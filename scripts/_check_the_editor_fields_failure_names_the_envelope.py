#!/usr/bin/env python3
"""Force a REAL ``Page.set_content`` timeout and print what the suite says about it.

WHY THIS EXISTS. On 2026-09-21 CI run 35592629243, job
``pytest (windows-latest, py3.13, shard 3)``, the build reported

    E   KeyError: 'fields'
    tests\\test_editor_fields.py:323: KeyError

while what the tool had actually returned was

    {'error': 'unexpected', 'message': 'TimeoutError: Page.set_content:
     Timeout 60000ms exceeded. ... waiting until "domcontentloaded"'}

``tests/test_editor_fields.py`` now routes every read of ``"fields"`` through
``fields_of``, so the headline names the envelope instead of a missing key. THAT
CLAIM IS ONLY WORTH THE DEMONSTRATION. A check that cannot fail certifies
nothing, and "the message would be better" is an assertion, not a measurement.
So this script MAKES THE TIMEOUT HAPPEN -- against a real headless Chromium, on
the real tool, through the real monkeypatch the fixture uses -- and prints the
old rendering beside the new one.

HOW THE TIMEOUT IS FORCED, AND WHY IT IS THE SAME EVENT AS CI'S. The editor
markup opens with a synchronous script that spins the parser past the deadline.
``domcontentloaded`` cannot fire while a synchronous script is executing, so
``set_content(..., wait_until="domcontentloaded")`` genuinely times out: same
Playwright call, same wait condition, same exception class, same envelope. The
spin is BOUNDED (it ends by itself) so nothing is left running, and the timeout
is set to a few seconds rather than sixty because the only difference that makes
is the integer printed inside the message. Nothing here simulates the error --
no exception is constructed by hand and no result dict is written by hand.

THIS SCRIPT LAUNCHES A LOCAL HEADLESS CHROMIUM OVER INVENTED MARKUP. It never
reaches LinkedIn, never opens the persistent profile, and needs no session --
``browser.BROWSER.session`` and ``.goto`` are replaced before the tool runs, so
the tool's only view of the world is the page this script made.

USAGE
    python scripts/_check_the_editor_fields_failure_names_the_envelope.py
Exit 0 when the new rendering names the envelope and the old one does not.
"""

from __future__ import annotations

import asyncio
import sys
import time
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# The same two lines scripts/_check_the_tool_envelope_guard_can_fail.py uses:
# pytest.ini's ``pythonpath = .`` only binds under pytest, and a script run
# directly gets its OWN directory on sys.path rather than the repo root.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

TIMEOUT_MS = 3_000
SPIN_MS = TIMEOUT_MS * 3

#: A document whose parser is blocked past the deadline. Everything after the
#: script is irrelevant -- it is never reached -- but it is written out anyway so
#: the fixture reads as a page rather than as a trick.
BLOCKING_HTML = (
    "<!doctype html><html><head><script>"
    f"var t=Date.now(); while(Date.now()-t < {SPIN_MS}) {{}}"
    "</script></head><body><dialog open><button>Save</button></dialog>"
    "</body></html>"
)

PLAIN_HTML = "<!doctype html><html><body><h1>Profile</h1></body></html>"


def names_of_OLD(result: dict[str, Any]) -> list[str]:
    """The implementation that shipped, kept here only to be shown failing."""
    return [field["name"] for field in result["fields"]]


def render_failure(label: str, call) -> str:
    """Run something that must fail, and return what a reader would see."""
    try:
        call()
    except BaseException:
        text = traceback.format_exc().strip()
        headline = text.splitlines()[-1]
        print("--- %s" % label)
        print(text)
        print("    HEADLINE: %s" % headline)
        print()
        return headline
    print("--- %s" % label)
    print("    DID NOT FAIL -- that is itself the finding")
    print()
    return ""


async def drive() -> dict[str, Any]:
    from playwright.async_api import async_playwright

    from linkedin_server import browser as browser_module
    from linkedin_server.server import (
        SELF_PROFILE_URL,
        linkedin_profile_editor_fields,
    )

    slug = "a-slug-this-script-invented"
    landed_profile = f"https://www.linkedin.com/in/{slug}/?isSelfProfile=true"
    landed_editor = f"https://www.linkedin.com/in/{slug}/edit/intro"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            page = await context.new_page()

            # THE SHIPPED HELPERS, NOT A COPY OF THEM. This render is the
            # fixture's render with one number changed (the timeout, so the
            # control finishes in seconds); the diagnosis and the control
            # reading are imported from the module under test, so what is
            # printed below is what CI would print and not a re-implementation
            # that happens to agree.
            from tests.test_editor_fields import (
                _render_diagnosis,
                _trivial_render_seconds,
            )

            async def render(markup: str) -> None:
                started = time.monotonic()
                try:
                    await page.set_content(
                        markup, wait_until="domcontentloaded", timeout=TIMEOUT_MS
                    )
                except Exception as exc:
                    waited = time.monotonic() - started
                    control = await _trivial_render_seconds(browser)
                    raise AssertionError(
                        _render_diagnosis(
                            type(exc).__name__, waited, len(markup), control
                        )
                    ) from exc

            @asynccontextmanager
            async def fake_session():
                yield page

            async def fake_goto(_page, url, **_kwargs):
                if url == SELF_PROFILE_URL:
                    await render(PLAIN_HTML)
                    return landed_profile
                await render(BLOCKING_HTML)
                return landed_editor

            saved = (browser_module.BROWSER.session, browser_module.BROWSER.goto)
            browser_module.BROWSER.session = fake_session
            browser_module.BROWSER.goto = fake_goto
            try:
                return await linkedin_profile_editor_fields()
            finally:
                browser_module.BROWSER.session, browser_module.BROWSER.goto = saved
        finally:
            await browser.close()


def main() -> int:
    print("Forcing a real Page.set_content timeout (wait_until=domcontentloaded,")
    print("timeout=%dms, parser blocked for %dms) against a local headless Chromium."
          % (TIMEOUT_MS, SPIN_MS))
    print()

    result = asyncio.run(drive())

    print("THE TOOL RETURNED:")
    print("    %r" % (result,))
    print()
    if "fields" in result:
        print("UNEXPECTED: the tool published 'fields' -- the timeout did not happen,")
        print("so this control proved nothing. Do not read the comparison below.")
        return 1

    from tests.test_editor_fields import names_of as names_of_NEW

    old = render_failure("BEFORE (the implementation that shipped)",
                         lambda: names_of_OLD(result))
    new = render_failure("AFTER (fields_of)", lambda: names_of_NEW(result))

    old_ok = old.startswith("KeyError")
    new_ok = "set_content did not finish" in new
    named_kind = "TimeoutError" in new
    # The reading that separates a starved box from a hanging document. Its
    # PRESENCE is what is checked, never its value -- asserting a number here
    # would make this control fail on a slow machine, which is the one machine
    # it most needs to keep working on.
    took_control_reading = "immediately afterwards took:" in new
    worker_named = "xdist worker:" in new

    # AND THE DISCRIMINATOR MUST ACTUALLY DISCRIMINATE. This script's fixture is
    # a HANGING DOCUMENT, not a starved machine: the box is fine, one page's
    # parser is wedged. So the correct reading is the prompt one. If this
    # reports "ALSO FAILED" the diagnosis is indicting the machine for what the
    # markup did -- which is exactly what the first version of
    # _trivial_render_seconds did by reusing the wedged page, and exactly how
    # that defect was found.
    discriminated = "in a fresh context" in new and "ALSO FAILED" not in new

    print("VERDICT")
    print("  old headline names only the absent key   : %s" % ("yes" if old_ok else "NO"))
    print("  new headline quotes the real envelope    : %s" % ("yes" if new_ok else "NO"))
    print("  new message names the exception kind     : %s" % ("yes" if named_kind else "NO"))
    print("  new message carries the CONTROL reading  : %s" % ("yes" if took_control_reading else "NO"))
    print("  new message names the xdist worker       : %s" % ("yes" if worker_named else "NO"))
    print("  CONTROL READING BLAMES THE MARKUP, NOT")
    print("  THE MACHINE (this fixture hangs a page,")
    print("  it does not starve the box)              : %s"
          % ("yes" if discriminated else "NO"))
    ok = (old_ok and new_ok and named_kind and took_control_reading
          and worker_named and discriminated)
    print()
    print("CONTROL: %s" % (
        "PASS -- the failure now names what the tool returned" if ok
        else "FAIL -- the comparison did not come out as claimed"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
