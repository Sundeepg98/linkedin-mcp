"""Three unmeasured surfaces nobody in this repository has ever opened.

Serves three MEASURE blockers whose boundary cost is ZERO -- every address
below already matches ``readonly._ALLOWED_URL_PATTERNS``, so nothing here asks
for a widening:

    /jobs/search/   ALL-FILTERS-PANEL (2 rows: J15, J16)
                    The census row reads "The 'All filters' panel as a
                    surface". **The string "All filters" has ZERO grep hits
                    across the entire package** -- not in a probe, not in a
                    test, not in a fixture, not in a docstring. Nobody has
                    opened it. The question is what controls it carries.

    /events/        AUDIO-EVENTS-EXISTENCE (1 row: profile L6)
                    The row reads "Audio events -- no tool, no reason; the
                    Help article itself 404s". So LinkedIn's own
                    documentation cannot say whether the product still
                    exists. A live events root either draws the affordance
                    or does not.

    /feed/          HASHTAG-EXISTENCE (context only, not the verdict)
                    ``_probe_unmeasured_surfaces_live.py`` stage a measured
                    the feed at 263 controls with every hashtag needle at 0
                    in main text -- AND ``hashtag`` at 20 in raw HTML. Twenty
                    occurrences with zero rendered anchors is the shape of a
                    word living in a script payload, but THAT IS A GUESS
                    UNTIL IT IS COUNTED. This file counts it.

## Why the third surface is here at all

**A REFUSAL THAT REPORTS ONLY WHAT IT DID NOT MATCH IS HALF A MEASUREMENT.**
This repository lost three rounds to "zero matched" before the fix was to
print what WAS there. "Zero hashtag anchors, and by the way there are twenty
of the word in the HTML" is exactly that half-measurement, and leaving the
twenty uncharacterised would hand the next reader a number they cannot use.

=============================================================================
THE CONTROLS, AND THERE ARE TWO KINDS BECAUSE THEY ANSWER DIFFERENT DOUBTS
=============================================================================

**1. A DETECTOR CONTROL, on markup this file owns.** Every target needle here
is expected to read ZERO or near it, and a zero from a working reader and a
zero from a broken one are the same character. So the same counting routine is
aimed first at a fragment whose answers are known IN BOTH DIRECTIONS -- a
needle that must count 2 and a needle that must count 0. If the must-find
needle reports 0 the reader is broken and every live number below is void.

**2. A PAGE CONTROL, on each live surface.** A working detector aimed at an
unrendered page still reads zero. This repository has the scar twice over: a
tabbed category read zero because nobody pressed its tab, and a profile read
zero for its own Interests section because the probe did not scroll. So each
surface carries needles that MUST be non-zero if LinkedIn drew the page at
all, chosen to sit in the SAME REGION as the target rather than anywhere on
the document -- a control on the far side of a page proves the page loaded,
not that the target's neighbourhood rendered.

If a page control fails, this file prints SUSPECT against that surface and
does not offer its target counts as a reading.

=============================================================================
WHAT IS PRESSED, AND WHAT IS NEVER PRESSED
=============================================================================

**ONE CONTROL IS PRESSED: the jobs search "All filters" trigger.** Opening a
panel to enumerate it is a read. Pressing anything INSIDE it is not, and
nothing inside it is touched -- no checkbox, no radio, no Show-results, no
Reset. Escape is pressed afterwards.

**NOTHING ELSE ANYWHERE IS PRESSED, TYPED, SCROLLED OR SUBMITTED.** The events
root and the feed are read exactly as served.

=============================================================================
WHAT IS PRINTED -- COUNTS AND SHAPES, NEVER VALUES
=============================================================================

**NO OPTION TEXT IS EVER PRINTED.** The All-filters panel contains a Company
filter, and its options are employer names. Group LABELS are LinkedIn's own
furniture words ("Date posted", "Experience level") and are printed through
the SHIPPED shaper ``shape.census_shape``, which returns ``<opaque>`` for
anything it cannot certify -- a refusal that KEEPS ITS MARKER rather than a
redaction that erases the evidence it redacted. Option COUNTS per group are
printed; option text never is.

No member id, no slug, no urn, no employer name, no job id, no url, no href
value. Every address is a module-level constant built from nothing a page
said.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_small_measures_live.py

Writes NOTHING. Prints to stdout.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

# --------------------------------------------------------------------------
# THE THREE ADDRESSES. Module-level constants, every one already allowlisted.
# --------------------------------------------------------------------------

#: The jobs search results page. ``readonly`` admits this address WITH a query
#: group. The keyword is a generic occupational word carried as a constant so
#: that a results page renders at all -- a bare /jobs/search/ can serve an
#: empty state whose filter rail is not drawn, which would be a zero about the
#: page rather than about the panel.
JOBS_SEARCH_URL = f"{BASE_URL}/jobs/search/?keywords=developer"
EVENTS_URL = f"{BASE_URL}/events/"
FEED_URL = f"{BASE_URL}/feed/"

# --------------------------------------------------------------------------
# THE DETECTOR CONTROL FRAGMENT. This file owns this markup; the expected
# integers are written here beside it, so the detector is not its own
# assertion.
# --------------------------------------------------------------------------

CONTROL_FRAGMENT = (
    "<div>"
    '<button aria-label="All filters">a</button>'
    '<button aria-label="Show all filters">b</button>'
    '<div role="dialog"><fieldset><legend>Date posted</legend>'
    '<input type="checkbox"><input type="checkbox"></fieldset>'
    '<fieldset><legend>Experience level</legend>'
    '<input type="radio"></fieldset></div>'
    "</div>"
)
CONTROL_EXPECT: dict[str, int] = {
    "all filters": 2,
    "dialogs": 1,
    "fieldsets": 2,
    "legends": 2,
    "checkboxes": 2,
    "radios": 1,
    "must_be_absent": 0,
}

#: A string that must never match anything, on the fragment or on any live
#: page. A detector that finds this is matching its own selectors.
ABSENT_NEEDLE = "Zqxjvbnm Filter Panel"

# --------------------------------------------------------------------------
# PAGE CONTROLS -- needles that MUST be non-zero if LinkedIn drew the page.
# Chosen to sit in the SAME REGION as the target, not anywhere on the page.
# --------------------------------------------------------------------------

#: The filter rail sits immediately beside the All-filters trigger, so these
#: prove the trigger's own neighbourhood rendered and not merely that some
#: bytes arrived.
JOBS_PAGE_CONTROLS: tuple[str, ...] = (
    "Easy Apply",
    "Date posted",
    "Experience level",
)
JOBS_TARGET_NEEDLES: tuple[str, ...] = (
    "All filters",
    "Show all filters",
    "Reset",
)

#: The events root's own furniture. The groups/events precondition work has
#: already read this surface live, so a zero here is a regression signal
#: rather than a novelty.
EVENTS_PAGE_CONTROLS: tuple[str, ...] = (
    "Events",
)
EVENTS_TARGET_NEEDLES: tuple[str, ...] = (
    "Audio event",
    "Audio Event",
    "audio",
    "Audio",
    "Create an event",
    "Event type",
)

FEED_PAGE_CONTROLS: tuple[str, ...] = (
    "Feed",
    "Start a post",
)


def _count(haystack: str, needle: str) -> int:
    return haystack.count(needle)


async def run_detector_control() -> bool:
    """Aim the counting routine at markup whose answers are known."""
    frag = CONTROL_FRAGMENT
    got = {
        "all filters": len(re.findall(r'aria-label="[^"]*[Aa]ll filters"', frag)),
        "dialogs": len(re.findall(r'role="dialog"', frag)),
        "fieldsets": len(re.findall(r"<fieldset", frag)),
        "legends": len(re.findall(r"<legend", frag)),
        "checkboxes": len(re.findall(r'type="checkbox"', frag)),
        "radios": len(re.findall(r'type="radio"', frag)),
        "must_be_absent": _count(frag, ABSENT_NEEDLE),
    }
    print("=" * 70)
    print("DETECTOR CONTROL -- runs first, and gates every number below")
    print("=" * 70)
    ok = True
    for key, expected in CONTROL_EXPECT.items():
        actual = got[key]
        verdict = "PASS" if actual == expected else "FAIL"
        if actual != expected:
            ok = False
        print(f"  {key:20s} expected {expected:3d}  got {actual:3d}  {verdict}")
    print(f"\n  DETECTOR USABLE: {ok}")
    return ok


async def _page_control(page, label: str, needles: tuple[str, ...]) -> bool:
    """A page control. Reports what it SAW, never only that it missed."""
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception as error:  # noqa: BLE001
        print(f"    main text unreadable: {type(error).__name__}")
    html = await page.content()
    print(f"    PAGE CONTROL for {label} -- must be non-zero:")
    passed = False
    for needle in needles:
        in_main = _count(main_text, needle)
        in_html = _count(html, needle)
        if in_main > 0 or in_html > 0:
            passed = True
        print(f"      {needle:24s} main={in_main:4d}  html={in_html:5d}")
    print(f"      main text: {len(main_text)} chars   html: {len(html)} chars")
    print(f"      PAGE CONTROL: {'PASS' if passed else 'FAIL -- SUSPECT'}")
    return passed


async def _needles(page, needles: tuple[str, ...], note: str) -> None:
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:  # noqa: BLE001
        pass
    html = await page.content()
    print(f"    TARGET needles ({note}):")
    for needle in needles:
        print(f"      {needle:24s} main={_count(main_text, needle):4d}  "
              f"html={_count(html, needle):5d}")


async def read_jobs_search(page) -> None:
    print("\n" + "=" * 70)
    print("SURFACE: /jobs/search/   ALL-FILTERS-PANEL (J15, J16)")
    print("=" * 70)
    if not readonly.is_read_url(JOBS_SEARCH_URL):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return
    landed = await BROWSER.goto(page, JOBS_SEARCH_URL)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL. Nothing here is a reading.")
        return
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception as error:  # noqa: BLE001
        print(f"    settle wait did not complete: {type(error).__name__}")

    control_ok = await _page_control(page, "jobs search rail", JOBS_PAGE_CONTROLS)
    await _needles(page, JOBS_TARGET_NEEDLES + (ABSENT_NEEDLE,), "the trigger")

    census = await dom.read_surface_census(page)
    print(f"    census controls_read={census.get('controls_read')}")

    # ABSOLUTE COUNTS BEFORE AND AFTER, never a difference. Three waves in
    # this repo measured CHANGE at a question about whether things EXIST.
    async def structure(when: str) -> dict:
        counts = {
            "dialogs": await page.locator('[role="dialog"]').count(),
            "fieldsets": await page.locator("fieldset").count(),
            "legends": await page.locator("legend").count(),
            "checkboxes": await page.locator('input[type="checkbox"]').count(),
            "radios": await page.locator('input[type="radio"]').count(),
            "selects": await page.locator("select").count(),
            "haspopup": await page.locator("[aria-haspopup]").count(),
        }
        print(f"    {when:7s} " + "  ".join(
            f"{k}={v}" for k, v in counts.items()))
        return counts

    print("\n    STRUCTURE, absolute counts on both sides of the press:")
    await structure("BEFORE")

    pressed = False
    try:
        trigger = page.locator(
            'button[aria-label*="All filters" i], '
            'button:has-text("All filters"), '
            '[role="button"][aria-label*="All filters" i]'
        ).first
        found = await trigger.count()
        print(f"\n    trigger controls carrying that name: {found}")
        if found > 0:
            await trigger.click(timeout=8_000)
            await page.wait_for_timeout(1_500)
            pressed = True
            print("    PRESSED the All-filters trigger. Nothing inside it is "
                  "touched.")
        else:
            print("    NOT PRESSED: no control carries that accessible name "
                  "on this render. That is a reading about the page, and this "
                  "probe reports it rather than widening its aim until "
                  "something matches.")
    except Exception as error:  # noqa: BLE001
        print(f"    PRESS FAILED: {type(error).__name__}")

    after = await structure("AFTER")

    if pressed and after["dialogs"] > 0:
        print("\n    THE PANEL'S OWN GROUPS -- labels through the shipped")
        print("    shaper, option COUNTS only. No option text is printed.")
        dialog = page.locator('[role="dialog"]').first
        legends = dialog.locator("fieldset")
        total = await legends.count()
        print(f"    fieldsets inside the panel: {total}")
        for index in range(min(total, 40)):
            group = legends.nth(index)
            try:
                raw = await group.locator("legend").first.inner_text(
                    timeout=2_000)
            except Exception:  # noqa: BLE001
                raw = ""
            boxes = await group.locator('input[type="checkbox"]').count()
            radios = await group.locator('input[type="radio"]').count()
            print(f"      group {index:2d}: {shape.census_shape(raw)!r:36s} "
                  f"checkboxes={boxes:3d} radios={radios:3d}")
        try:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(600)
            print("    Escape pressed.")
        except Exception as error:  # noqa: BLE001
            print(f"    Escape failed: {type(error).__name__}")
    elif pressed:
        print("\n    PRESSED BUT NO DIALOG APPEARED. The panel may not be a "
              "dialog-roled region; the absolute counts above are the "
              "reading.")

    if not control_ok:
        print("\n    SUSPECT: the page control failed, so nothing above is "
              "offered as a reading about the panel.")


async def read_events(page) -> None:
    print("\n" + "=" * 70)
    print("SURFACE: /events/   AUDIO-EVENTS-EXISTENCE (profile L6)")
    print("=" * 70)
    if not readonly.is_read_url(EVENTS_URL):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return
    landed = await BROWSER.goto(page, EVENTS_URL)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL. Nothing here is a reading.")
        return
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception as error:  # noqa: BLE001
        print(f"    settle wait did not complete: {type(error).__name__}")
    await _page_control(page, "events root", EVENTS_PAGE_CONTROLS)
    await _needles(page, EVENTS_TARGET_NEEDLES + (ABSENT_NEEDLE,), "audio")
    census = await dom.read_surface_census(page)
    print(f"    census controls_read={census.get('controls_read')}")


async def read_feed_hashtag_context(page) -> None:
    print("\n" + "=" * 70)
    print("SURFACE: /feed/   HASHTAG-EXISTENCE -- characterising the twenty")
    print("=" * 70)
    if not readonly.is_read_url(FEED_URL):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL. Nothing here is a reading.")
        return
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception as error:  # noqa: BLE001
        print(f"    settle wait did not complete: {type(error).__name__}")
    await _page_control(page, "feed", FEED_PAGE_CONTROLS)
    html = await page.content()
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:  # noqa: BLE001
        pass

    total = _count(html.lower(), "hashtag")
    print(f"\n    'hashtag' occurrences in html (case-insensitive): {total}")
    print(f"    'hashtag' occurrences in main text: "
          f"{_count(main_text.lower(), 'hashtag')}")
    print("\n    WHERE THEY LIVE -- context classes, counts only:")
    classes = {
        "inside an href value": len(re.findall(
            r'href="[^"]*hashtag', html, re.IGNORECASE)),
        "as a /feed/hashtag/ path": len(re.findall(
            r"/feed/hashtag/", html, re.IGNORECASE)),
        "as an attribute name": len(re.findall(
            r'[a-z-]*hashtag[a-z-]*\s*=', html, re.IGNORECASE)),
        "as a json key": len(re.findall(
            r'"[^"]*hashtag[^"]*"\s*:', html, re.IGNORECASE)),
        "as a json string value": len(re.findall(
            r':\s*"[^"]*hashtag[^"]*"', html, re.IGNORECASE)),
        "inside a class token": len(re.findall(
            r'class="[^"]*hashtag', html, re.IGNORECASE)),
        "inside a urn": len(re.findall(
            r"urn:li:[a-zA-Z]*hashtag", html, re.IGNORECASE)),
    }
    for label, count in classes.items():
        print(f"      {label:28s} {count:5d}")
    accounted = sum(classes.values())
    print(f"\n      accounted for by the classes above: {accounted} of {total}")
    print("      (classes overlap by construction -- a json key inside a "
          "script is counted twice. This is a CHARACTERISATION, not a "
          "partition, and it is stated rather than implied.)")

    print("\n    RENDERED ANCHORS -- the thing a member could actually click:")
    anchors = await page.locator('a[href*="hashtag"]').count()
    feed_hashtag = await page.locator('a[href*="/feed/hashtag/"]').count()
    print(f"      a[href*='hashtag']          {anchors}")
    print(f"      a[href*='/feed/hashtag/']   {feed_hashtag}")


async def main() -> int:
    # THE CONTROL IS RUNNABLE ALONE, AND DELIBERATELY BEFORE THE CDP GATE.
    # An instrument admitted without having been SHOWN FAILING certifies
    # nothing, and a control reachable only through a live browser cannot be
    # exercised against a deliberate break.
    if "--control" in sys.argv:
        return 0 if await run_detector_control() else 1

    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print("    Chrome runs externally on the operator's own profile and "
              "this script attaches to it. A launch-mode session would open "
              "a SECOND Chrome on that profile, one major version behind it.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2

    if not await run_detector_control():
        print("\nDETECTOR BROKEN. Nothing live is loaded and no number below "
              "would be a reading.")
        return 1

    # THE PAGE IS CLOSED IN A ``finally``. ``BROWSER.session()`` does not
    # close its page: in attach mode it caches one tab per PROCESS and reuses
    # it, and a probe is a process. Every probe run that skipped this left a
    # tab open in the operator's shared Chrome -- measured fleet-wide once at
    # 120 CDP targets, which made every attach time out.
    # THE PAGE, NEVER THE CONTEXT. The context is his own browser session.
    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            await read_jobs_search(page)
            await read_events(page)
            await read_feed_hashtag_context(page)
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
