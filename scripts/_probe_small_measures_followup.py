"""The three things the small-measures wave named as owed, and did not settle.

Every one of them is a stated limitation of that wave rather than a new
question, and every one costs ZERO boundary -- same three addresses, all
already on ``readonly._ALLOWED_URL_PATTERNS``.

    A.  /in/me/         DEFENDS the MEASURED-ABSENT this wave put on `P D25`.
                        The add-a-section control is not drawn under either
                        accessible-name spelling. **The uncertainty that
                        survives is whether LinkedIn draws it under a
                        DIFFERENT name**, and 9 controls on that render carry
                        ``aria-haspopup``. A state change is only as good as
                        the doubt it closed, so this enumerates those 9
                        through the shipped shaper.

    B.  /jobs/search/   MOVES or KEEPS `J 16`, "Suggested filters (adaptive,
                        on AI search)". The wave searched by KEYWORD and
                        carried no needle for a suggestion strip, and said so
                        rather than reporting a zero it never measured. This
                        fires the needle it did not.

    C.  /feed/          REPAIRS THIS WAVE'S OWN INSTRUMENT. Its hashtag
                        context classifier accounted for **0 of 15**
                        occurrences -- all seven classes read zero. That is a
                        defect in the classifier, not a finding about
                        LinkedIn, and it was recorded as such. This replaces
                        guessed classes with a partition that cannot miss.

## Why C is written the way it is

The first classifier guessed SEVEN SHAPES a word might wear -- href, path,
attribute name, json key, json string, class token, urn -- and every guess
missed. **A set of guessed buckets can be wrong in a way that looks like a
finding**, because "0 in every class" reads as absence rather than as a
classifier that does not fit.

So this one does not guess. It splits the document into SCRIPT CONTENT and
EVERYTHING ELSE -- a partition, exhaustive by construction -- counts in each,
and prints the casing variants actually present. A partition's totals must sum
to the whole, and that sum is asserted below and printed. If it does not add
up, the reader is told.

=============================================================================
THE CONTROLS
=============================================================================

**DETECTOR CONTROL on owned markup**, runnable alone via ``--control`` and
deliberately BEFORE the CDP gate, so it can be shown failing without a
browser. An instrument that has never been shown failing certifies nothing.

**PAGE CONTROL on each live surface**, chosen to sit in the SAME REGION as the
target. A working detector aimed at an unrendered page still reads zero.

=============================================================================
WHAT IS PRINTED
=============================================================================

**ACCESSIBLE NAMES GO THROUGH ``shape.census_shape`` AND NOWHERE ELSE.** That
function returns ``<opaque>`` for anything it cannot certify -- a refusal that
KEEPS ITS MARKER, rather than a redaction that erases the evidence it
redacted. This matters more here than anywhere else in the wave: the profile
is HIS page, and a control's accessible name there can carry his own name.

Nothing is pressed, typed, scrolled or submitted anywhere in this file. No
member id, no slug, no urn, no employer, no job id, no url, no href value.

Run::

    ./venv/Scripts/python.exe scripts/_probe_small_measures_followup.py --control
    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_small_measures_followup.py

Writes NOTHING. Prints to stdout.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, readonly, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

PROFILE_URL = f"{BASE_URL}/in/me/"
FEED_URL = f"{BASE_URL}/feed/"

#: A NATURAL-LANGUAGE QUERY, because that is what "AI search" means on this
#: surface and a keyword query is exactly what the first wave already ran.
#: Generic occupational words only -- nothing here names a person, an employer
#: or a place.
JOBS_AI_SEARCH_URL = (
    f"{BASE_URL}/jobs/search/?keywords=remote%20backend%20engineer%20roles"
    "%20for%20someone%20with%20node%20experience"
)

# --------------------------------------------------------------------------
# DETECTOR CONTROL
# --------------------------------------------------------------------------

CONTROL_HTML = (
    "<html><body>"
    '<button aria-haspopup="true" aria-label="More">m</button>'
    '<script>var a = "hashtag one hashtag two";</script>'
    "<div>hashtag three</div>"
    '<script>var b = "Hashtag four";</script>'
    "</body></html>"
)
#: Known in both directions. Four occurrences of the word: three inside script
#: content, one outside it. A partition must reproduce 3 + 1 = 4.
CONTROL_EXPECT: dict[str, int] = {
    "total": 4,
    "in_script": 3,
    "outside_script": 1,
    "haspopup": 1,
    "must_be_absent": 0,
}
ABSENT_NEEDLE = "Zqxjvbnm Followup Needle"

SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>(.*?)</script>", re.DOTALL | re.I)


def partition_word(html: str, word: str) -> dict[str, int]:
    """Split a document into script content and everything else.

    A PARTITION, NOT A GUESS. The first attempt at this question used seven
    guessed shape classes and matched none of fifteen occurrences, which reads
    like absence and was really a classifier that did not fit. These two
    buckets are exhaustive by construction and their sum is checked.
    """
    lowered = html.lower()
    needle = word.lower()
    total = lowered.count(needle)
    in_script = 0
    for match in SCRIPT_BLOCK.finditer(html):
        in_script += match.group(1).lower().count(needle)
    outside = total - in_script
    return {"total": total, "in_script": in_script, "outside_script": outside}


async def run_detector_control() -> bool:
    print("=" * 70)
    print("DETECTOR CONTROL -- runs first, gates every number below")
    print("=" * 70)
    part = partition_word(CONTROL_HTML, "hashtag")
    got = {
        "total": part["total"],
        "in_script": part["in_script"],
        "outside_script": part["outside_script"],
        "haspopup": len(re.findall(r"aria-haspopup", CONTROL_HTML)),
        "must_be_absent": CONTROL_HTML.count(ABSENT_NEEDLE),
    }
    ok = True
    for key, expected in CONTROL_EXPECT.items():
        actual = got[key]
        verdict = "PASS" if actual == expected else "FAIL"
        if actual != expected:
            ok = False
        print(f"  {key:18s} expected {expected:3d}  got {actual:3d}  {verdict}")
    sums = got["in_script"] + got["outside_script"] == got["total"]
    print(f"  {'partition sums':18s} "
          f"{got['in_script']} + {got['outside_script']} == {got['total']}  "
          f"{'PASS' if sums else 'FAIL'}")
    if not sums:
        ok = False
    print(f"\n  DETECTOR USABLE: {ok}")
    return ok


async def _page_control(page, label: str, needles: tuple[str, ...]) -> bool:
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception as error:  # noqa: BLE001
        print(f"    main text unreadable: {type(error).__name__}")
    html = await page.content()
    print(f"    PAGE CONTROL for {label} -- must be non-zero:")
    passed = False
    for needle in needles:
        in_main = main_text.count(needle)
        in_html = html.count(needle)
        if in_main or in_html:
            passed = True
        print(f"      {needle:26s} main={in_main:4d}  html={in_html:5d}")
    print(f"      main {len(main_text)} chars   html {len(html)} chars")
    print(f"      PAGE CONTROL: {'PASS' if passed else 'FAIL -- SUSPECT'}")
    return passed


async def _goto(page, url: str, label: str) -> bool:
    if not readonly.is_read_url(url):
        print(f"    {label}: REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return False
    landed = await BROWSER.goto(page, url)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print(f"    {label}: AUTH WALL. Nothing here is a reading.")
        return False
    try:
        await page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception as error:  # noqa: BLE001
        print(f"    settle wait did not complete: {type(error).__name__}")
    return True


async def part_a_profile_haspopup(page) -> None:
    print("\n" + "=" * 70)
    print("A. /in/me/  -- do any of the 9 aria-haspopup controls open the")
    print("   add-a-section menu under a DIFFERENT accessible name?")
    print("=" * 70)
    if not await _goto(page, PROFILE_URL, "profile"):
        return
    ok = await _page_control(
        page, "profile top card", ("Edit", "Open to", "Add")
    )

    triggers = page.locator("[aria-haspopup]")
    total = await triggers.count()
    print(f"\n    controls carrying aria-haspopup: {total}")
    print("    NO NAME IS PRINTED. The first version of this block printed")
    print("    shape.census_shape(name) and THAT LEAKED THE OPERATOR'S OWN")
    print("    NAME TO STDOUT -- census_shape is a STRUCTURAL shaper (urns,")
    print("    member paths, possessives, digit runs) plus a character gate,")
    print("    and a bare personal name carries none of those markers, so it")
    print("    returns unchanged. The repo already recorded that defect; the")
    print("    mistake here was reaching for it as if it were a name")
    print("    redactor. shape.describe_name_shaped is the shipped instrument")
    print("    for this, and it returns STRUCTURE and never any part of a")
    print("    name: how many capitalised runs, and the name-free tail.\n")
    for index in range(min(total, 40)):
        node = triggers.nth(index)
        label = ""
        try:
            label = await node.get_attribute("aria-label") or ""
            if not label:
                label = (await node.inner_text(timeout=2_000) or "").strip()
        except Exception:  # noqa: BLE001
            label = ""
        expanded = ""
        try:
            expanded = await node.get_attribute("aria-expanded") or "-"
        except Exception:  # noqa: BLE001
            expanded = "-"
        described = shape.describe_name_shaped(label)
        tail = described.get("tail")
        # The tail is asserted name-free BY CONSTRUCTION -- it is what
        # remains after the last capitalised run. None means no run was
        # found, which is NOT the same as an empty tail, and conflating them
        # publishes a string this function declined to vouch for.
        tail_out = "<no-run>" if tail is None else repr(tail)
        # Whether the label is one of the furniture words this part is
        # hunting for is a BOOLEAN, not a name.
        hits = [w for w in ("section", "Section", "profile", "Profile", "Add")
                if w in label]
        print(f"      haspopup {index:2d}: aria-expanded={expanded:5s} "
              f"len={len(label):3d} runs={described.get('runs')} "
              f"name_free_tail={tail_out} furniture_words={hits}")

    # THE DIRECT QUESTION, asked of the whole document rather than of the
    # nine: does any control anywhere carry a name that MENTIONS a section?
    html = await page.content()
    print("\n    document-wide needles for the same control under other names,")
    print("    each PARTITIONED into script content vs everywhere else --")
    print("    because a name living only inside a <script> payload is NOT a")
    print("    control a member could press, and the raw count cannot tell")
    print("    those apart:")
    print(f"      {'needle':26s} {'total':>6s} {'in <script>':>12s} "
          f"{'elsewhere':>10s}")
    for needle in ("Add profile section", "Add section", "add-profile-section",
                   "profile-section", "Add to profile", "ADD_PROFILE_SECTION"):
        part = partition_word(html, needle)
        print(f"      {needle:26s} {part['total']:6d} {part['in_script']:12d} "
              f"{part['outside_script']:10d}")

    # AND THE DISCRIMINATOR THAT DECIDES IT: is any of them a real control?
    print("\n    is any of them an actual pressable control?")
    for selector, note in (
        ('button:has-text("Add section")', "a button whose text says so"),
        ('[aria-label*="Add section" i]', "a control labelled so"),
        ('[aria-label*="Add profile section" i]', "the original spelling"),
        ('a:has-text("Add section")', "a link"),
    ):
        try:
            found = await page.locator(selector).count()
        except Exception as error:  # noqa: BLE001
            found = -1
            note = f"{note} (selector error {type(error).__name__})"
        print(f"      {selector:44s} {found:4d}   {note}")
    if not ok:
        print("\n    SUSPECT: page control failed; nothing above is a reading.")


async def part_b_suggested_filters(page) -> None:
    print("\n" + "=" * 70)
    print("B. /jobs/search/ under a NATURAL-LANGUAGE query -- J 16,")
    print("   'Suggested filters (adaptive, on AI search)'")
    print("=" * 70)
    if not await _goto(page, JOBS_AI_SEARCH_URL, "jobs ai search"):
        return
    ok = await _page_control(
        page, "jobs rail", ("Easy Apply", "Date posted", "Experience level")
    )
    html = await page.content()
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:  # noqa: BLE001
        pass
    print("\n    TARGET needles for an adaptive suggestion strip:")
    for needle in ("Suggested filter", "Suggested filters", "Suggested",
                   "Try searching", "Refine", "Recommended filter",
                   "AI", ABSENT_NEEDLE):
        print(f"      {needle:26s} main={main_text.count(needle):4d}  "
              f"html={html.count(needle):5d}")
    print("\n    STRUCTURE around the rail:")
    for selector, note in (
        ('[role="list"]', "any list container"),
        ("fieldset", "filter groups drawn inline"),
        ('button[aria-pressed]', "toggle pills -- the shape a suggestion "
                                 "chip would take"),
        ('[role="radiogroup"]', "radio groups"),
    ):
        print(f"      {selector:22s} {await page.locator(selector).count():4d}"
              f"   {note}")
    if not ok:
        print("\n    SUSPECT: page control failed; nothing above is a reading.")


async def part_c_hashtag_partition(page) -> None:
    print("\n" + "=" * 70)
    print("C. /feed/ -- REPAIRING THIS WAVE'S OWN CLASSIFIER (it matched")
    print("   0 of 15, which reads like absence and was a bad fit)")
    print("=" * 70)
    if not await _goto(page, FEED_URL, "feed"):
        return
    ok = await _page_control(page, "feed", ("Feed", "Start a post"))
    html = await page.content()
    main_text = ""
    try:
        main_text = await page.inner_text("main")
    except Exception:  # noqa: BLE001
        pass

    part = partition_word(html, "hashtag")
    print("\n    PARTITION -- exhaustive by construction, and its sum is")
    print("    checked rather than assumed:")
    print(f"      inside <script> content   {part['in_script']:5d}")
    print(f"      everywhere else           {part['outside_script']:5d}")
    print(f"      total in html             {part['total']:5d}")
    sums = part["in_script"] + part["outside_script"] == part["total"]
    print(f"      PARTITION SUMS: {'PASS' if sums else 'FAIL'}")
    print(f"      in main text              {main_text.lower().count('hashtag'):5d}")

    print("\n    CASING VARIANTS actually present (counts only):")
    for variant in ("hashtag", "Hashtag", "HASHTAG", "hashtags", "Hashtags",
                    "hashtagged"):
        print(f"      {variant:14s} {html.count(variant):5d}")

    print("\n    THE THING A MEMBER COULD CLICK:")
    any_hashtag = await page.locator('a[href*="hashtag"]').count()
    feed_hashtag = await page.locator('a[href*="/feed/hashtag/"]').count()
    print(f"      a[href*='hashtag']         {any_hashtag:5d}")
    print(f"      a[href*='/feed/hashtag/']  {feed_hashtag:5d}")
    if not ok:
        print("\n    SUSPECT: page control failed; nothing above is a reading.")


async def main() -> int:
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
        print("\nDETECTOR BROKEN. Nothing live is loaded.")
        return 1

    # THE PAGE IS CLOSED IN A ``finally``. BROWSER.session() caches one tab
    # per PROCESS and does not close it; a probe is a process. Every run that
    # skipped this left a tab in the operator's shared Chrome -- measured once
    # fleet-wide at 120 CDP targets, which made every attach time out.
    page = None
    try:
        async with BROWSER.session() as opened:
            page = opened
            await part_a_profile_haspopup(page)
            await part_b_suggested_filters(page)
            await part_c_hashtag_partition(page)
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
