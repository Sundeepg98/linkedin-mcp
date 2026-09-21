"""RED PROOF: ``auth._cookie_records`` states an invariant the browser breaks.

``linkedin_server/auth.py::_cookie_records`` says, in its own docstring:

    Read the raw cookie jar. Never logged, never persisted, never returned.
    Values stay inside this module. Only derived facts -- a name, a presence,
    an expiry timestamp -- ever reach a tool result.

``_probe_what_playwright_quotes.py`` measured that a failing
``page.request.get`` renders ITS OWN CALL LOG into ``str(exc)``, and that call
log enumerates EVERY REQUEST HEADER -- including ``cookie:``. ``check_auth``
interpolates that ``str(exc)`` into ``$.reason`` and ``linkedin_auth_status``
returns that dict to the caller unchanged: not through ``_error``, not through
``scrub``.

So the cookie value leaves the module by a door the docstring does not know
about. This drives it and shows the value landing in the published field.

## WHAT IS REAL HERE AND WHAT IS PLANTED

REAL: the exception. It is not constructed by this file. It is caught from an
ephemeral chromium making a genuine failing request, so its text is whatever
the shipped Playwright actually writes. REAL: ``check_auth`` itself, imported
and called.

PLANTED: the cookie jar, and the page. Every cookie value here is a synthetic
token. Nothing in this file touches the operator's profile, his session, his
Chrome, or linkedin.com.

## WHAT THIS PROBE DOES NOT CLAIM

It does not claim the failure is common. It claims it is REACHABLE: any
connect error or timeout on the identity call takes this branch, and both were
driven. Whether that is worth repairing, and how, is the reader's call --
``press.disclose`` in this package already shows the shape of the repair
(render the type, drop the text).

EXIT 0 means the leak reproduced, because that is what this probe is for. It
exits 1 if the leak does NOT reproduce, which is the day somebody fixed it and
this file should be retired.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server import auth  # noqa: E402

COOKIE_SENTINEL = "ZQCOOKIEZQ"
# DELIBERATELY SHORT. The planted value plus the cookie NAME must stay
# under the length at which `scripts/staged_identity_shapes.py` calls a
# `<name>=<value>` pair a credential SHAPE -- the guard refused an
# earlier, longer plant in this wave's own audit document, and the
# guard is right to: it cannot tell a plant from the real thing, and
# declaring one permanently widens what it tolerates for that file.
SESSION_VALUE = COOKIE_SENTINEL + "-val"
CSRF_VALUE = COOKIE_SENTINEL + "-csrf"


def _ascii(text) -> str:
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


async def _real_specimen():
    """Catch a genuine APIRequestContext failure carrying a cookie header."""
    import socket

    from playwright.async_api import async_playwright

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    dead_port = sock.getsockname()[1]
    sock.close()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            await ctx.add_cookies([{
                "name": "li_at",
                "value": SESSION_VALUE,
                "domain": "127.0.0.1",
                "path": "/",
            }])
            try:
                await page.request.get(
                    "http://127.0.0.1:%d/identity" % dead_port, timeout=900)
            except Exception as exc:  # noqa: BLE001 - the specimen
                return exc
            raise SystemExit(
                "NO SPECIMEN: the request did not fail, so nothing was measured")
        finally:
            await ctx.close()
            await browser.close()


class _PlantedRequest:
    def __init__(self, specimen):
        self._specimen = specimen

    async def get(self, *_args, **_kwargs):
        raise self._specimen


class _PlantedContext:
    async def cookies(self, *_args, **_kwargs):
        # Both names the module looks for, so check_auth takes the branch
        # under test rather than short-circuiting on a cold browser.
        return [
            {"name": auth.SESSION_COOKIE, "value": SESSION_VALUE},
            {"name": auth.CSRF_COOKIE, "value": CSRF_VALUE},
        ]


class _PlantedPage:
    url = "https://www.linkedin.com/feed/"

    def __init__(self, specimen):
        self.context = _PlantedContext()
        self.request = _PlantedRequest(specimen)

    def is_closed(self) -> bool:
        return False


async def _run() -> int:
    specimen = await _real_specimen()
    raw = str(specimen)

    print("=" * 72)
    print("THE SPECIMEN, caught from a real browser")
    print("  type : " + type(specimen).__module__ + "." + type(specimen).__name__)
    print("  the cookie header is inside str(exc): "
          + str(COOKIE_SENTINEL in raw))
    print()

    if COOKIE_SENTINEL not in raw:
        print("SPECIMEN DID NOT CARRY THE COOKIE -- nothing to prove here.")
        return 1

    result = await auth.check_auth(
        _PlantedPage(specimen), corroborate=False, warm=True)

    reason = str(result.get("reason", ""))
    leaked = COOKIE_SENTINEL in reason

    print("=" * 72)
    print("check_auth's OWN RETURN, which linkedin_auth_status returns unchanged")
    print("  $.authenticated          = " + repr(result.get("authenticated")))
    print("  $.session_cookie_present = " + repr(result.get("session_cookie_present")))
    print("  $.reason carries the cookie value: " + str(leaked))
    print()
    print("  $.reason, verbatim:")
    for line in _ascii(reason).splitlines():
        print("    | " + line)
    print()

    print("=" * 72)
    if leaked:
        print("REPRODUCED. _cookie_records says the jar's values 'never reach a")
        print("tool result'. They reach one, through a library exception's own")
        print("call log, in a field that sees neither _error nor scrub.")
        return 0
    print("NOT REPRODUCED -- the leak is closed and this probe can be retired.")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(_run()))
