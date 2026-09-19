"""Does the off-platform SHARE / FOLLOW-LINK control render at all?

`OFF-PLATFORM-WIDGET`, rows `M C72` (share a post off LinkedIn) and `N 76`
(copy your personal Follow link for use off LinkedIn). Both are READS, and
both are reachable in principle: the LINK is obtained ON LinkedIn, on pages
this server already opens.

**THE WRITE HALF OF THIS BLOCKER WAS RETIRED AND THE READ HALF WAS SPARED.**
`N 50` retired 2026-09-05 because the ACT is pressing a button embedded on a
third party's website, which `server.py:5706-5711` rules out. That ruling
explicitly did not touch the read.

=============================================================================
WHAT THIS CAN AND CANNOT ANSWER, DECIDED BEFORE THE FIRST LOAD
=============================================================================

**A "Copy link" item almost certainly lives INSIDE an overflow menu, and this
file does not press one.** So a zero on the ITEM would be uninformative --
exactly the trap this repository has paid for repeatedly: a control that is
not in the document until its menu is opened reads identically to a control
that does not exist.

So the question is split, and only the answerable half is asked:

    ANSWERABLE    does the TRIGGER render? (a share control on a feed item,
                  an overflow control on his own profile)
    NOT ASKED     what the menu contains -- that needs a press, and a press
                  on a post's share control sits next to `publish_post`

**A trigger that renders is positive evidence the surface exists.** A trigger
that does not is evidence about this render, reported as such. Neither
outcome requires pressing anything.

CONTROLS. A detector control on owned markup, runnable via ``--control``
before the CDP gate. A page control on each surface, in the same region as
the target, because a working detector aimed at an unrendered page still
reads zero.

WHAT IS PRINTED: counts and LinkedIn's own furniture words. No href value, no
accessible name, no post id, no member path. Nothing is pressed, typed,
scrolled or submitted.

Run::

    ./venv/Scripts/python.exe scripts/_probe_off_platform_controls.py --control
    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_off_platform_controls.py

Writes NOTHING.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

FEED_URL = f"{BASE_URL}/feed/"
PROFILE_URL = f"{BASE_URL}/in/me/"

#: C 72 -- the share affordance on a feed item, and the off-platform words
#: that would sit inside it.
FEED_TRIGGERS = ("Share", "Send", "Repost", "Copy link", "Share via",
                 "Embed this post")
#: N 76 -- the profile's own overflow, where a personal link would live.
PROFILE_TRIGGERS = ("More", "Copy link", "Follow link", "Contact info",
                    "Share profile", "Personal link")

FEED_PAGE_CONTROLS = ("Feed", "Start a post")
PROFILE_PAGE_CONTROLS = ("Open to", "Add", "Edit")

ABSENT_NEEDLE = "Zqxjvbnm Off Platform Needle"

CONTROL_HTML = (
    "<html><body>"
    '<button aria-label="Share">s</button>'
    '<button aria-haspopup="true" aria-label="More">m</button>'
    "<div>Copy link</div>"
    "</body></html>"
)
CONTROL_EXPECT = {"Share": 1, "More": 1, "Copy link": 1,
                  "haspopup": 1, ABSENT_NEEDLE: 0}


async def run_detector_control() -> bool:
    print("=" * 70)
    print("DETECTOR CONTROL -- gates every number below")
    print("=" * 70)
    ok = True
    for needle, expected in CONTROL_EXPECT.items():
        if needle == "haspopup":
            got = len(re.findall(r"aria-haspopup", CONTROL_HTML))
        else:
            got = CONTROL_HTML.count(needle)
        good = got == expected
        if not good:
            ok = False
        print(f"  {needle:26s} expected {expected:3d}  got {got:3d}  "
              f"{'PASS' if good else 'FAIL'}")
    print(f"\n  DETECTOR USABLE: {ok}")
    return ok


async def read_surface(page, url: str, label: str,
                       page_controls: tuple[str, ...],
                       triggers: tuple[str, ...]) -> None:
    print("\n" + "=" * 70)
    print(f"SURFACE: {label}")
    print("=" * 70)
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return
    landed = await BROWSER.goto(page, url)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL. Nothing here is a reading.")
        return
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception as error:  # noqa: BLE001
        print(f"    settle wait did not complete: {type(error).__name__}")

    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:  # noqa: BLE001
        pass
    html = await page.content()

    print("    PAGE CONTROL -- must be non-zero:")
    passed = False
    for needle in page_controls:
        count = main_text.count(needle)
        if count:
            passed = True
        print(f"      {needle:22s} main={count:4d}  html={html.count(needle):5d}")
    print(f"      PAGE CONTROL: {'PASS' if passed else 'FAIL -- SUSPECT'}")

    print("\n    TRIGGERS -- rendered without pressing anything:")
    for needle in triggers + (ABSENT_NEEDLE,):
        print(f"      {needle:22s} main={main_text.count(needle):4d}  "
              f"html={html.count(needle):5d}")

    print("\n    MENU MACHINERY (a trigger with no items means built on demand):")
    for selector in ('[aria-haspopup]', '[role="menu"]', '[role="menuitem"]',
                     '[aria-expanded="false"]'):
        print(f"      {selector:24s} {await page.locator(selector).count():5d}")
    if not passed:
        print("\n    SUSPECT: page control failed; nothing above is a reading.")


async def main() -> int:
    if "--control" in sys.argv:
        return 0 if await run_detector_control() else 1
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2
    if not await run_detector_control():
        print("\nDETECTOR BROKEN. Nothing live is loaded.")
        return 1

    # Page closed in a finally: attach mode caches one tab per PROCESS and
    # never closes it, and a probe is a process.
    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            await read_surface(page, FEED_URL, "/feed/  -- M C72",
                               FEED_PAGE_CONTROLS, FEED_TRIGGERS)
            await read_surface(page, PROFILE_URL, "/in/me/  -- N 76",
                               PROFILE_PAGE_CONTROLS, PROFILE_TRIGGERS)
    finally:
        if page is not None:
            try:
                await page.close()
                print("\n    page closed.")
            except Exception as error:  # noqa: BLE001
                print(f"\n    page close failed: {type(error).__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
