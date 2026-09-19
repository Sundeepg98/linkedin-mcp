#!/usr/bin/env python
"""Does browser state survive the ATTACHING process dying and reconnecting?

THE CLAIM THIS EXISTS TO MEASURE. Moving this server to HTTP is only an
improvement if the server can be restarted freely, and the server can only be
restarted freely if restarting it does not cost the browser session. Under the
default LAUNCH mode it plainly does: the browser IS a child of the server, so
killing the server kills the browser. Under ATTACH the browser is a separate
process and the claim is that a second server generation reaches the same one.

That claim is cheap to assert and easy to get wrong, so it is measured here
instead, using exactly the mechanism the server uses -- ``cdp_bridge.attach``,
not a hand-rolled connection that might behave differently.

    python scripts/_probe_attach_continuity.py --set probe_marker=<value>
    python scripts/_probe_attach_continuity.py --get probe_marker

Run ``--set`` before killing the server and ``--get`` after the replacement is
up. Matching ``browser_guid`` and a surviving cookie together mean one browser,
one session, two attaching processes. A CHANGED guid means Chrome restarted
underneath and the cookie proves nothing -- which is why both are reported.

WHY A COOKIE. It is the same storage LinkedIn's session lives in, it is written
into the browser's own context (``contexts[0]``, the one carrying his real
cookies) rather than into an incognito side-context, and it needs no
navigation: nothing here loads a page, reaches LinkedIn, or touches the
network. The marker is scoped to ``127.0.0.1`` so it cannot be sent anywhere.

``--webdriver`` answers a different question that the cutover also raises: a
Chrome started by ``start_chrome.ps1`` gets no automation flag, so does it
announce itself as automated the way an unflagged Playwright launch does? It
opens one about:blank tab, reads ``navigator.webdriver``, and closes it.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

MARKER_DOMAIN = "127.0.0.1"
MARKER_PATH = "/"


def _browser_id() -> str:
    """A stable identity for the browser PROCESS, read straight off DevTools.

    ``/json/version`` carries ``webSocketDebuggerUrl``, whose path is a GUID
    Chrome mints once per browser process. It is therefore the one field that
    distinguishes "the same Chrome, reconnected" from "a different Chrome that
    happens to be on the same port" -- and the second of those is exactly the
    way this measurement could lie.

    Playwright's own connection guid was tried first and is NOT this: it is
    minted per CONNECTION, so it differs across attaches to one browser and
    proves nothing about continuity.
    """
    from urllib.request import urlopen

    from linkedin_server import cdp_bridge

    with urlopen(f"{cdp_bridge.endpoint()}/json/version", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8", "replace"))
    return str(payload.get("webSocketDebuggerUrl", "")).rsplit("/", 1)[-1]


async def _run(args) -> dict:
    from linkedin_server import cdp_bridge

    version = await cdp_bridge.probe()
    if not version.get("reachable"):
        return {"ok": False, "stage": "probe", "detail": version}

    pw, client, context = await cdp_bridge.attach()
    out: dict = {
        "ok": True,
        "endpoint": cdp_bridge.endpoint(),
        "browser": version.get("browser"),
        "browser_guid": _browser_id(),
        "contexts": len(client.contexts),
    }
    try:
        if args.set:
            name, _, value = args.set.partition("=")
            await context.add_cookies(
                [
                    {
                        "name": name,
                        "value": value,
                        "domain": MARKER_DOMAIN,
                        "path": MARKER_PATH,
                    }
                ]
            )
            out["action"] = "set"
            out["marker"] = {"name": name, "value": value}

        if args.get:
            cookies = await context.cookies()
            found = [c for c in cookies if c.get("name") == args.get]
            out["action"] = "get"
            out["marker_found"] = bool(found)
            out["marker_value"] = found[0]["value"] if found else None
            out["cookie_count"] = len(cookies)

        if args.webdriver:
            page = await context.new_page()
            try:
                out["navigator_webdriver"] = await page.evaluate(
                    "() => navigator.webdriver"
                )
                out["user_agent"] = await page.evaluate("() => navigator.userAgent")
            finally:
                await page.close()
    finally:
        # Close the CLIENT, never the context: the context is the browser's own
        # and closing it closes the operator's window. This is the same
        # asymmetry browser.py's teardown observes.
        await client.close()
        await pw.stop()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--set", default="", metavar="NAME=VALUE")
    parser.add_argument("--get", default="", metavar="NAME")
    parser.add_argument(
        "--webdriver",
        action="store_true",
        help="also read navigator.webdriver from a blank tab",
    )
    args = parser.parse_args()

    result = asyncio.run(_run(args))
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
