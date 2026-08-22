"""SECONDARY PATH -- attach to a Chrome the operator started himself.

This module is NOT the daily path and is not how this server is meant to run.
The primary answer to "how does it stay signed in" is the persistent profile
in ``browser.py``: sign in once, the profile keeps the session, done. This
file exists for one situation -- the profile's session has died and a fresh
automated sign-in is being refused -- so that the operator can sign in by hand
in a browser he launched, and let this server read through it.

WHAT IT REQUIRES, stated plainly because every one of these has bitten:

1. **Chrome must already be running**, started BY HIM, and started WITH
   ``--remote-debugging-port``. Nothing here launches a browser. This is not
   "your normal browser" -- a Chrome started from the taskbar has no DevTools
   port and cannot be attached to, no matter how signed in it is.

2. **Chrome's singleton will silently defeat you.** If any Chrome is already
   running on a profile, starting a second ``chrome.exe --remote-debugging-
   port=...`` against that SAME profile hands the arguments to the running
   instance and exits. No port opens. No error is printed, and the exit code
   is zero. Measured on this machine: the launcher process was gone inside
   five seconds, nothing listened on the port, and the only new processes
   were renderers belonging to the already-running browser. So one of:

   * **Quit Chrome completely first** (every window AND the tray/background
     instance), then start it once with the port. This is the option that
     keeps his real profile, and therefore his real LinkedIn session::

         "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9224

   * **Or give it a profile of its own**, which works with Chrome already
     running but is a DIFFERENT profile -- it is signed into nothing, so he
     has to sign in to LinkedIn inside that window once::

         "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9224 --user-data-dir="%LOCALAPPDATA%\\linkedin-cdp"

   Confirm either one worked before bothering with this server: open
   ``http://127.0.0.1:9224/json/version`` in any tab. JSON means the port is
   live; "cannot reach" means Chrome swallowed the flag.

3. **The address is ``127.0.0.1``, never ``localhost``.** Chrome binds the
   port on IPv4 only, so ``localhost`` tries IPv6 first and eats the timeout
   before falling back -- measured at 2085 ms against 35 ms.

WHAT IT WILL NOT DO. It takes no profile lock, because it owns no profile.
It never drives one of his existing tabs -- it opens its own and closes only
that one. And it never closes his browser: Playwright's ``close()`` on a CDP
connection disconnects the client and leaves Chrome serving, which was
measured here rather than assumed (the endpoint still answered afterwards).

The read-only boundary is unchanged in this mode. Every navigation still goes
through ``readonly.assert_read_url``; nothing in this module clicks, types,
submits or issues a non-GET request.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

from linkedin_server.config import CDP_HOST, CDP_PORT, logger
from linkedin_server.errors import BrowserUnavailableError

#: How long to wait for the CDP handshake before giving up.
ATTACH_TIMEOUT_MS = 15_000
#: How long to wait on the plain HTTP probe of ``/json/version``.
PROBE_TIMEOUT_S = 5.0

#: The command to start Chrome with the port open, quoted for a Windows shell.
#: Reported verbatim in errors and in ``linkedin_session_info`` so the operator
#: never has to come and read this file.
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
START_COMMAND = f'"{CHROME_PATH}" --remote-debugging-port={CDP_PORT}'
START_COMMAND_SEPARATE_PROFILE = (
    f'{START_COMMAND} --user-data-dir="%LOCALAPPDATA%\\linkedin-cdp"'
)

#: The one-paragraph version of the module docstring, for error messages.
ATTACH_REQUIREMENTS = (
    "ATTACH mode needs a Chrome that is ALREADY RUNNING and was started with "
    f"--remote-debugging-port={CDP_PORT}. A Chrome opened normally has no "
    "DevTools port and cannot be attached to. If Chrome is already running, "
    "quit it COMPLETELY first (windows and the background instance) and then "
    f"run:  {START_COMMAND}  -- otherwise the flag is silently handed to the "
    "running instance and no port opens. To leave his existing Chrome alone, "
    f"use a separate profile instead:  {START_COMMAND_SEPARATE_PROFILE}  -- "
    "but that profile is signed into nothing, so LinkedIn has to be signed "
    f"into once inside it. Verify with http://{CDP_HOST}:{CDP_PORT}/json/version"
)


def endpoint() -> str:
    """The CDP base url. Literal IPv4 -- see the module docstring."""
    return f"http://{CDP_HOST}:{CDP_PORT}"


def _read_version() -> str:
    """Blocking GET of ``/json/version``. Runs in a worker thread."""
    from urllib.request import urlopen

    with urlopen(f"{endpoint()}/json/version", timeout=PROBE_TIMEOUT_S) as response:
        return response.read().decode("utf-8", "replace")


async def probe() -> dict[str, Any]:
    """Is there an attachable browser on the port? A read, and never raises.

    Returns ``reachable`` plus, when it is, whatever ``/json/version`` said
    about the browser. When it is not, the reason and the command that fixes
    it. This is diagnostics: it opens no page and reads nothing on LinkedIn.
    """
    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(_read_version), timeout=PROBE_TIMEOUT_S + 1.0
        )
    except Exception as exc:
        return {
            "reachable": False,
            "endpoint": endpoint(),
            "reason": (
                f"nothing answered at {endpoint()}/json/version "
                f"({type(exc).__name__}: {exc})."
            ),
            "how_to_fix": ATTACH_REQUIREMENTS,
        }

    try:
        payload = json.loads(raw)
    except ValueError:
        payload = {}

    return {
        "reachable": True,
        "endpoint": endpoint(),
        "browser": payload.get("Browser"),
        "protocol_version": payload.get("Protocol-Version"),
    }


async def attach() -> tuple[Any, Any, Any]:
    """Connect to the running browser. Returns ``(playwright, client, context)``.

    The caller owns teardown and must close the CLIENT, never the context:
    the context is the operator's own browser session and closing it closes
    his window. ``browser.py`` does exactly that.

    Raises:
        BrowserUnavailableError: Playwright is missing, or no attachable
            browser is listening -- with the command that fixes it.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:  # pragma: no cover - environment
        raise BrowserUnavailableError(
            "Playwright is not installed. Run: pip install playwright && "
            "playwright install chromium"
        ) from exc

    pw = await async_playwright().start()
    client: Optional[Any] = None
    try:
        client = await pw.chromium.connect_over_cdp(
            endpoint(), timeout=ATTACH_TIMEOUT_MS
        )
        contexts = list(client.contexts)
        if not contexts:  # pragma: no cover - a live Chrome always has one
            raise BrowserUnavailableError(
                f"attached to {endpoint()} but it exposed no browser context. "
                "This is not a browser this server can read through."
            )
        # contexts[0] is the browser's OWN context, cookies and all. Making a
        # new one would produce an incognito-ish context signed into nothing,
        # which is the opposite of why anyone attaches.
        logger.info("cdp attach: %d context(s) at %s", len(contexts), endpoint())
        return pw, client, contexts[0]
    except BrowserUnavailableError:
        await _abandon(pw, client)
        raise
    except Exception as exc:
        await _abandon(pw, client)
        raise BrowserUnavailableError(
            f"could not attach to a browser at {endpoint()} "
            f"({type(exc).__name__}: {exc}). {ATTACH_REQUIREMENTS}"
        ) from exc


async def _abandon(pw: Any, client: Any) -> None:
    """Drop a half-made attachment without touching the operator's browser."""
    if client is not None:
        try:
            await client.close()
        except Exception as exc:  # pragma: no cover - shutdown noise
            logger.debug("cdp disconnect raised %s: %s", type(exc).__name__, exc)
    try:
        await pw.stop()
    except Exception as exc:  # pragma: no cover - shutdown noise
        logger.debug("stopping playwright raised %s: %s", type(exc).__name__, exc)
