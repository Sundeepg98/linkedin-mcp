"""HTTP transport for this server, and the one gate that makes it safe.

WHY THIS FILE EXISTS, stated as the problem it removes.

Under **stdio** the MCP client owns this process. Changed code on disk is not
changed code in the session: the only way to load it is the operator typing
``/mcp`` himself, which puts a human in the loop at every verification point.
Under **HTTP** the client owns nothing -- it holds a URL. Claude Code
reconnects a dropped HTTP/SSE server on its own (exponential backoff, five
attempts), so the server can be stopped and started from a shell and the
client re-attaches without him. That is the whole reason for this file.

THE SECOND HALF, without which HTTP is a REGRESSION. A long-lived HTTP server
in the default LAUNCH mode would hold the persistent Chrome profile lock for
as long as it runs -- strictly worse than stdio, where the server at least
dies with the session and releases it. So HTTP is meant to be run with
``LINKEDIN_CDP_ATTACH=1``, against a Chrome the operator (or
``scripts/start_chrome.ps1``) started separately. In that mode this server
owns no profile, takes no lock, and can be restarted freely. Nothing here
enforces the pairing -- ``serve_http`` REPORTS the mode it is starting in, and
a launch-mode HTTP server is a legitimate thing to run deliberately -- but the
runbook pairs them and the log line says which one you got.

WHAT CHANGES ABOUT SAFETY, named here rather than discovered later:

* **A grant is process memory.** ``writes.mint`` issues single-use grants held
  in this process. Under stdio each Claude session had its OWN process, so a
  grant could only ever be redeemed inside the session that previewed it.
  One HTTP server serves every session, so that isolation is gone. The token
  is still opaque, still single-use, still short-lived, and is returned only
  to the caller that minted it -- but "a different session cannot possibly
  hold it" stops being true by construction and becomes true only because the
  string was never shown to it.

* **A loopback port is a surface stdio did not have.** stdio could be driven
  by exactly one thing: the parent that spawned it. An HTTP server on
  127.0.0.1 can be driven by anything running as this user. With
  ``LINKEDIN_ENABLE_WRITES=1`` that means anything on this machine could post,
  message or invite as him. :func:`bearer_gate` is the answer: set
  ``LINKEDIN_HTTP_TOKEN`` and every request must carry it. It is OPTIONAL
  because the sibling Naukri server has run unauthenticated on this box for
  months and the parity is deliberate -- but LinkedIn's writes are
  outward-facing in a way Naukri's are not, so the recommendation in the
  runbook is to set it.

Binding is loopback-only and this module offers no way to change that. There
is no ``MCP_REMOTE`` equivalent here on purpose: a server that drives his
signed-in LinkedIn session has no business listening on a LAN.
"""

from __future__ import annotations

import os
import socket
from typing import Any, Optional

from linkedin_server.config import CDP_ATTACH, logger

#: Default loopback port. Deliberately adjacent to the sibling Naukri server's
#: 8321 so the two read as a pair in ``.mcp.json``. Every port in use on this
#: machine was enumerated before this number was picked.
DEFAULT_HTTP_PORT = 8322

#: The MCP endpoint path. Matches Naukri's ``http://127.0.0.1:8321/mcp`` so one
#: spelling covers both entries.
HTTP_PATH = "/mcp"

#: Loopback, always. Not overridable -- see the module docstring.
HTTP_HOST = "127.0.0.1"

_PORT_ENV = "LINKEDIN_HTTP_PORT"
_TOKEN_ENV = "LINKEDIN_HTTP_TOKEN"


def http_port() -> int:
    """The port to serve on. ``LINKEDIN_HTTP_PORT`` overrides the default."""
    raw = os.environ.get(_PORT_ENV, "").strip()
    if not raw:
        return DEFAULT_HTTP_PORT
    try:
        port = int(raw)
    except ValueError:
        raise SystemExit(
            f"{_PORT_ENV}={raw!r} is not a number. Unset it to use "
            f"{DEFAULT_HTTP_PORT}."
        )
    if not (1 <= port <= 65535):
        raise SystemExit(f"{_PORT_ENV}={port} is not a port number.")
    return port


def http_url(port: Optional[int] = None) -> str:
    """The url to put in ``.mcp.json``. One place, so it cannot drift."""
    return f"http://{HTTP_HOST}:{port or http_port()}{HTTP_PATH}"


def _port_is_free(port: int) -> bool:
    """Can we bind it? A real bind, not a connect -- they answer differently.

    A ``connect`` to a dead port fails and a ``connect`` to a live one
    succeeds, which tells you whether something is SERVING. That is not the
    question here. The question is whether uvicorn will be able to take the
    port, and the only honest way to ask it is to take it briefly ourselves.
    """
    probe = socket.socket()
    try:
        probe.bind((HTTP_HOST, port))
    except OSError:
        return False
    finally:
        probe.close()
    return True


def bearer_gate(app: Any, token: str) -> Any:
    """Wrap an ASGI app so every HTTP request must carry ``token``.

    Pure ASGI rather than Starlette middleware so it holds whatever the
    framework underneath happens to be, and so the refusal is a plain 401 with
    no body worth parsing.

    THE COMPARISON IS CONSTANT-TIME. A token checked with ``==`` leaks its
    length and its prefix to anything that can time a loopback request, and
    "it is only loopback" is exactly the reasoning that makes a local
    privilege boundary decorative. ``hmac.compare_digest`` costs nothing here.

    Only ``http`` scope is gated. A ``lifespan`` message is the server's own
    startup and carries no headers to check; refusing it would stop the app
    booting rather than stop an intruder.
    """
    import hmac

    expected = token.encode("utf-8")

    async def gated(scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") != "http":
            await app(scope, receive, send)
            return

        presented = b""
        for name, value in scope.get("headers") or ():
            if name.lower() == b"authorization":
                presented = value
                break
        prefix = b"Bearer "
        if presented.startswith(prefix):
            presented = presented[len(prefix):]

        if not hmac.compare_digest(presented, expected):
            await send(
                {
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        (b"content-type", b"text/plain; charset=utf-8"),
                        (b"www-authenticate", b"Bearer"),
                    ],
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": b"unauthorized: this server requires the bearer "
                    b"token in LINKEDIN_HTTP_TOKEN.\n",
                }
            )
            return

        await app(scope, receive, send)

    return gated


def serve_http(mcp: Any, *, port: Optional[int] = None) -> None:
    """Serve MCP over streamable HTTP on loopback. Blocks until stopped.

    Mirrors the sibling Naukri server's ``run_http_only``: build the ASGI app,
    drive it with uvicorn explicitly rather than through the framework's own
    ``run``, and do it inside an event loop we opened ourselves.

    THE LOOP IS THE POINT, and it is why this does not simply call
    ``FastMCP.run``. ``uvicorn.Server.run()`` installs its own event-loop
    policy; ``uvicorn.Server.serve()`` awaited inside an existing loop does
    not. On Windows that difference decides whether Playwright can start a
    browser subprocess at all, so the browser this server exists to drive
    depends on which of the two is called. Naukri has run this shape for
    months.
    """
    import anyio
    import uvicorn

    chosen = port or http_port()

    if not _port_is_free(chosen):
        raise SystemExit(
            f"port {chosen} is already in use on {HTTP_HOST}. Something is "
            f"already serving there -- stop it first (scripts/stop_server.ps1) "
            f"or set {_PORT_ENV} to a free port."
        )

    app = mcp.http_app(path=HTTP_PATH)

    token = os.environ.get(_TOKEN_ENV, "").strip()
    if token:
        app = bearer_gate(app, token)

    async def _serve() -> None:
        config = uvicorn.Config(
            app,
            host=HTTP_HOST,
            port=chosen,
            log_level="warning",
            # Access logs would print every MCP request path to stderr for a
            # server that runs all day. Nothing reads them and they are not
            # free.
            access_log=False,
        )
        server = uvicorn.Server(config)
        logger.info(
            "linkedin http: serving %s | browser mode=%s | auth=%s",
            http_url(chosen),
            "attach" if CDP_ATTACH else "LAUNCH (holds the profile lock)",
            "bearer" if token else "none",
        )
        if not CDP_ATTACH:
            # Not a refusal -- running HTTP in launch mode is a deliberate
            # thing to do. But it is the configuration the whole design warns
            # about, so it says so once, loudly, rather than being discovered
            # later as a profile nobody can open.
            logger.warning(
                "linkedin http: LINKEDIN_CDP_ATTACH is not set, so this "
                "long-lived server will hold the persistent Chrome profile "
                "lock for as long as it runs. Set LINKEDIN_CDP_ATTACH=1 and "
                "start Chrome separately (scripts/start_chrome.ps1)."
            )
        await server.serve()

    anyio.run(_serve)
