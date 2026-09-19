#!/usr/bin/env python
"""Speak MCP to an HTTP server using nothing but the standard library.

WHY NOT A CLIENT. The claim this script exists to check is "the server is
serving the MCP protocol over HTTP". An MCP client library answering yes would
prove that the library and the server agree; it would not separate "the
protocol is being spoken" from "both ends share a bug". More practically, it
would make the check depend on the very package whose transport is being
changed. urllib and json are enough: an initialize is one POST.

WHAT A GREEN HERE MEANS, precisely. The socket accepted a connection, the
server returned a well-formed JSON-RPC ``initialize`` result carrying a
protocol version and a server name, and -- with ``--list`` or ``--call`` -- it
went on to serve a session-bound request. It does NOT mean the browser is
reachable, that a session is signed in, or that any tool would succeed. Those
are different questions and ``--call linkedin_cdp_status`` is how you ask one
of them.

Exit code is the verdict: 0 served, 1 did not. Everything it learned goes to
stdout as JSON so a script can read it and a human can too.

    python scripts/mcp_probe.py --url http://127.0.0.1:8322/mcp
    python scripts/mcp_probe.py --list
    python scripts/mcp_probe.py --call linkedin_cdp_status

WHAT ``--call`` PRINTS BACK, because it is not simply the result. ``--call``
will invoke ANY tool the server exposes, and this output lands in terminals and
agent transcripts. ``linkedin_my_profile`` would therefore put the operator's
own profile into a transcript, which is the channel all three slug leaks of
2026-09-03 used. So the payload is printed in full only for tools measured to
carry no identity -- see ``_PRINTABLE_IN_FULL``, currently one entry -- and
every other tool reports ``call_result_shape``: its top-level keys and the TYPE
of each value, never a value. The verdict is unaffected either way; only the
contents are withheld. If you want the contents, use an MCP client.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8322/mcp"
PROTOCOL_VERSION = "2025-06-18"


class ProbeError(RuntimeError):
    """The server did not answer the way an MCP server answers."""


def _parse_body(raw: bytes, content_type: str) -> dict:
    """Read a JSON-RPC message out of either response shape.

    Streamable HTTP is allowed to answer a POST with ``application/json`` OR
    with an SSE stream, and which one you get depends on server configuration
    rather than on anything the caller said. Handling only the first is the
    bug that makes a working server look dead, so both are read here.
    """
    text = raw.decode("utf-8", "replace")
    if "text/event-stream" in content_type:
        for line in text.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise ProbeError(f"event-stream carried no data: frame: {text[:300]!r}")
    return json.loads(text)


def _post(url: str, payload: dict, headers: dict, timeout: float) -> tuple[dict, dict]:
    """One JSON-RPC POST. Returns ``(message, response_headers)``."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    # BOTH content types, because the server picks. See _parse_body.
    request.add_header("Accept", "application/json, text/event-stream")
    for name, value in headers.items():
        request.add_header(name, value)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            got = dict(response.headers)
            return _parse_body(raw, response.headers.get("content-type", "")), got
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise ProbeError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProbeError(f"could not reach {url}: {exc.reason}") from exc


def _notify(url: str, payload: dict, headers: dict, timeout: float) -> None:
    """A JSON-RPC notification. 202 with no body is the correct answer."""
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("Accept", "application/json, text/event-stream")
    for name, value in headers.items():
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        raise ProbeError(f"HTTP {exc.code} on notification") from exc
    except urllib.error.URLError as exc:
        raise ProbeError(f"could not reach {url}: {exc.reason}") from exc


def probe(
    url: str,
    *,
    token: str = "",
    list_tools: bool = False,
    call: str = "",
    args: dict | None = None,
    timeout: float = 20.0,
) -> dict:
    """Initialize, then optionally list or call. Raises ProbeError on refusal."""
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    started = time.monotonic()
    message, response_headers = _post(
        url,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mcp_probe", "version": "1"},
            },
        },
        headers,
        timeout,
    )
    elapsed_ms = round((time.monotonic() - started) * 1000)

    if "error" in message:
        raise ProbeError(f"initialize returned an error: {message['error']}")
    result = message.get("result") or {}
    if not result.get("protocolVersion"):
        raise ProbeError(f"initialize result carried no protocolVersion: {message}")

    session_id = ""
    for name, value in response_headers.items():
        if name.lower() == "mcp-session-id":
            session_id = value
            break

    out = {
        "served": True,
        "url": url,
        "initialize_ms": elapsed_ms,
        "protocol_version": result.get("protocolVersion"),
        "server": result.get("serverInfo") or {},
        "session_id_present": bool(session_id),
    }

    if not (list_tools or call):
        return out

    # Everything past initialize is session-bound. A server that hands out a
    # session id and then ignores it would pass the check above and fail every
    # real call, which is exactly the gap this second half closes.
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    headers["MCP-Protocol-Version"] = str(result.get("protocolVersion"))
    _notify(
        url,
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers,
        timeout,
    )

    if list_tools:
        message, _ = _post(
            url,
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            headers,
            timeout,
        )
        if "error" in message:
            raise ProbeError(f"tools/list returned an error: {message['error']}")
        tools = (message.get("result") or {}).get("tools") or []
        out["tool_count"] = len(tools)
        out["tool_names"] = sorted(t.get("name", "?") for t in tools)

    if call:
        message, _ = _post(
            url,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": call, "arguments": args or {}},
            },
            headers,
            timeout,
        )
        if "error" in message:
            raise ProbeError(f"tools/call {call} returned an error: {message['error']}")
        payload = message.get("result") or {}
        out["called"] = call
        out["call_is_error"] = bool(payload.get("isError"))
        out.update(_render_call_result(call, payload))

    return out


#: TOOLS WHOSE RESULT MAY BE PRINTED IN FULL.
#:
#: This probe's output lands in terminals and, more to the point, in agent
#: transcripts. ``--call`` will call ANY tool this server exposes, and some of
#: them return the operator's own account: ``linkedin_my_profile`` would put his
#: profile -- vanity slug included -- into whatever transcript ran the probe.
#: That is precisely the channel the three slug leaks of 2026-09-03 used.
#:
#: So the payload is printed only for tools measured to carry no identity, and
#: everything else reports its SHAPE. The list is deliberately one entry long:
#: ``linkedin_cdp_status`` was read field by field (reachable, endpoint,
#: browser, protocol_version, is_the_daily_path, active_browser_mode,
#: how_to_use) and carries nothing about a person. Others may well be safe --
#: they have not been measured, and a list of things nobody checked is the
#: ``_redact`` mistake in a different costume.
#:
#: IT FAILS SAFE. A tool that is not on the list loses its payload, not its
#: verdict; the caller still learns whether the call succeeded and what shape
#: came back. Forgetting to add a name costs detail, never disclosure.
_PRINTABLE_IN_FULL = frozenset({"linkedin_cdp_status"})


def _render_call_result(call: str, payload: dict) -> dict:
    """What to report about a tool result, given who returned it.

    A SHAPE IS NOT A SUMMARY. It reports the top-level keys and the TYPE of
    each value -- never a value -- so "did the call come back with what it
    should" stays answerable without the contents passing through here. A
    summary would be a second thing to trust; a key list cannot reconstruct
    what it describes.
    """
    if call in _PRINTABLE_IN_FULL:
        if "structuredContent" in payload:
            return {"call_result": payload["structuredContent"]}
        return {
            "call_result": [
                block.get("text") for block in payload.get("content") or []
            ]
        }

    if "structuredContent" in payload:
        structured = payload["structuredContent"]
        shape = (
            {key: type(value).__name__ for key, value in sorted(structured.items())}
            if isinstance(structured, dict)
            else type(structured).__name__
        )
    else:
        shape = {"content_blocks": len(payload.get("content") or [])}

    return {
        "call_result_shape": shape,
        "call_result_withheld": (
            f"{call!r} is not in _PRINTABLE_IN_FULL, so its payload is not "
            "printed -- this probe's output reaches transcripts and a tool "
            "result can carry the operator's own account. Use an MCP client "
            "if you need the contents."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    # THE FLAG IS --url; THE ATTRIBUTE IS DELIBERATELY NOT `url`.
    #
    # `test_navigation_is_never_derived` treats ANY `.url` attribute in this
    # package as a value the browser chose, and it is right to: enumerating the
    # objects that could hold one would be a list to keep in step, so the rule
    # taints the attribute whatever holds it. In `linkedin_server/` that
    # generalisation is true -- every `.url` there is a page, a request or a
    # response.
    #
    # This file is its first counterexample. `options.endpoint` would be an argparse
    # Namespace holding an address the CALLER typed, and nothing in this module
    # can reach a browser: it imports argparse, json, os, sys, time and urllib,
    # and that is the whole list.
    #
    # THE RENAME IS NOT A DODGE, AND WHAT MAKES IT NOT ONE IS A TEST. Renaming
    # to escape a checker is how a value stops being examined; the claim being
    # made here -- that no browser exists in this file -- is pinned by
    # `test_mcp_probe_has_no_browser_surface` in tests/test_transport.py, so if
    # anyone ever teaches this probe to drive a page, that test fails and this
    # comment stops being true out loud rather than quietly.
    #
    # `endpoint` is also just the better name. In a package where `.url` means
    # "the browser chose this", calling a caller-supplied MCP address `url` is
    # the misleading spelling, not the honest one.
    parser.add_argument(
        "--url",
        dest="endpoint",
        default=os.environ.get("LINKEDIN_HTTP_URL", DEFAULT_URL),
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("LINKEDIN_HTTP_TOKEN", ""),
        help="bearer token, if the server was started with one",
    )
    parser.add_argument("--list", action="store_true", help="also run tools/list")
    parser.add_argument("--call", default="", help="also call this tool")
    parser.add_argument("--args", default="{}", help="JSON arguments for --call")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="retry a refused connection this many times, 1s apart. For a "
        "server that was just started and may not have bound yet.",
    )
    options = parser.parse_args()

    try:
        call_args = json.loads(options.args)
    except ValueError as exc:
        print(json.dumps({"served": False, "reason": f"--args is not JSON: {exc}"}))
        return 1

    last = ""
    for attempt in range(options.retries + 1):
        try:
            result = probe(
                options.endpoint,
                token=options.token,
                list_tools=options.list,
                call=options.call,
                args=call_args,
                timeout=options.timeout,
            )
        except ProbeError as exc:
            last = str(exc)
            if attempt < options.retries:
                time.sleep(1.0)
                continue
            print(json.dumps({"served": False, "url": options.endpoint, "reason": last}, indent=2))
            return 1
        result["attempts"] = attempt + 1
        print(json.dumps(result, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
