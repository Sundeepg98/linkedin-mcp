"""Does a REAL Playwright error text reach ``$.message``, or is it stopped?

``_probe_what_playwright_quotes.py`` establishes WHAT Playwright writes. This
establishes WHERE IT GOES: it raises a genuine strict mode violation against a
planted local page, hands the resulting exception OBJECT to the shipped
``server._error``, and reads the envelope that comes out.

Nothing is simulated. The exception is not constructed by this file; it is
caught from the browser. That matters, because the whole question is what a
library nobody here controls put inside it.

THREE PATHS ARE COMPARED, because they are not the same path:

* **BARE** -- the Playwright exception reaches ``_error`` directly, which is
  what happens when a tool body's ``except Exception as exc: return
  _error(exc)`` catches a reader that did not wrap.
* **WRAPPED** -- the reader catches it and raises the package's own
  ``ExtractionFailedError(...) from exc``. ``_error`` then reads
  ``str(exc)`` of the PACKAGE's exception; the Playwright text survives only
  on ``__cause__``, which ``_error`` never reads.
* **SCRUB ALONE** -- ``config.scrub`` applied to the raw message, to show what
  the scrubber does and does not do to it. A name has no shape.

No network, no signed-in profile, no persistent user-data dir. An ephemeral
chromium this process launches and closes.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from linkedin_server import server as srv  # noqa: E402
from linkedin_server.config import scrub  # noqa: E402
from linkedin_server.errors import ExtractionFailedError  # noqa: E402

SENTINEL = "ZQTEXTZQ"

PLANTED = """<!doctype html><html><head><title>ZQTITLEZQ-doc</title></head>
<body>
 <div class="card" id="ZQIDZQ-1" data-probe="ZQATTRZQ-1">ZQTEXTZQ-alpha</div>
 <div class="card" id="ZQIDZQ-2" data-probe="ZQATTRZQ-2">ZQTEXTZQ-beta</div>
</body></html>
"""


def _ascii(text) -> str:
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


async def _catch_a_real_strict_violation():
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context()
        page = await ctx.new_page()
        try:
            await page.set_content(PLANTED)
            try:
                await page.locator(".card").text_content(timeout=900)
            except Exception as exc:  # noqa: BLE001 - the specimen
                return exc
            raise SystemExit(
                "NO SPECIMEN: the planted page did not produce a strict mode "
                "violation, so this probe measured nothing")
        finally:
            await ctx.close()
            await browser.close()


def main() -> int:
    exc = asyncio.run(_catch_a_real_strict_violation())
    raw = str(exc)

    print("=" * 72)
    print("THE SPECIMEN, caught from the browser")
    print("  type: " + type(exc).__module__ + "." + type(exc).__name__)
    print("  carries the page sentinel: " + str(SENTINEL in raw))
    print()

    findings = []

    # ---- BARE -------------------------------------------------------------
    bare = srv._error(exc)
    leaked = SENTINEL in str(bare.get("message", ""))
    findings.append(("BARE  Playwright exception -> server._error", leaked))
    print("=" * 72)
    print("PATH 1  BARE: the exception reaches _error unwrapped")
    print("  $.error   = " + repr(bare.get("error")))
    print("  $.message carries the page sentinel: " + str(leaked))
    print("  $.message, verbatim:")
    for line in _ascii(bare.get("message", "")).splitlines():
        print("    | " + line)
    print()

    # ---- WRAPPED ----------------------------------------------------------
    try:
        try:
            raise exc
        except Exception as inner:  # noqa: BLE001
            raise ExtractionFailedError(
                "the cards could not be read", url="") from inner
    except ExtractionFailedError as wrapped:
        env = srv._error(wrapped)
    leaked_wrapped = SENTINEL in str(env.get("message", ""))
    findings.append(("WRAPPED  ExtractionFailedError(...) from exc",
                     leaked_wrapped))
    print("=" * 72)
    print("PATH 2  WRAPPED: the reader raises the package's own error from it")
    print("  $.error   = " + repr(env.get("error")))
    print("  $.message = " + repr(_ascii(env.get("message", ""))))
    print("  $.message carries the page sentinel: " + str(leaked_wrapped))
    print("  (the Playwright text is on __cause__, which _error never reads)")
    print()

    # ---- SCRUB ALONE ------------------------------------------------------
    scrubbed = scrub(raw)
    unchanged = scrubbed == raw
    findings.append(("SCRUB  config.scrub over the raw message",
                     SENTINEL in str(scrubbed)))
    print("=" * 72)
    print("PATH 3  WHAT THE SCRUBBER DOES TO IT")
    print("  scrub(message) == message : " + str(unchanged))
    print("  sentinel survives scrub   : " + str(SENTINEL in str(scrubbed)))
    print("  characters removed        : %d" % (len(raw) - len(str(scrubbed))))
    print()

    print("=" * 72)
    for label, leaked_here in findings:
        print("  %-46s page value published: %s" % (label, leaked_here))
    print()

    # The probe asserts the shape it was written to establish, so that a
    # future Playwright or a future _error that changes it makes this RED
    # rather than quietly making the document wrong.
    problems = []
    if not bare_expected(findings):
        problems.append(
            "the three paths no longer behave as this probe documents")
    if problems:
        for line in problems:
            print("CHANGED: " + line)
        return 1
    print("the three paths behave as documented")
    return 0


def bare_expected(findings) -> bool:
    """BARE leaks, WRAPPED does not, SCRUB does not clean it."""
    as_map = {label.split()[0]: leaked for label, leaked in findings}
    return (as_map.get("BARE") is True
            and as_map.get("WRAPPED") is False
            and as_map.get("SCRUB") is True)


if __name__ == "__main__":
    sys.exit(main())
