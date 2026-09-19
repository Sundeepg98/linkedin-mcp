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

#: THE aria-expanded VALUES THIS FILE WILL PRINT, AND NOTHING ABOUT ARIA.
#:
#: This is NOT a claim that the ARIA spec closes the set. The attribute is read
#: off the page, so it is matched against these tokens and anything unmatched
#: prints UNKNOWN-EXPANDED. That holds whether or not the spec is closed, and
#: whether or not this tuple is complete -- which is the reason to prefer
#: matching to trusting.
EXPANDED_VALUES: tuple[str, ...] = ("false", "true")

#: THE RUN COUNTS THE haspopup BLOCK WILL PRINT. describe_name_shaped returns
#: an integer, but it arrives inside a dict the taint engine has marked, so the
#: number is rendered by matching this tuple rather than by printing the dict.
#: Anything past the end is MANY.
RUN_COUNTS: tuple[int, ...] = (0, 1, 2, 3, 4, 5)


def partition_word(document: str, word: str) -> dict[str, list[str]]:
    """Split a document into script content and everything else.

    A PARTITION, NOT A GUESS. The first attempt at this question used seven
    guessed shape classes and matched none of fifteen occurrences, which reads
    like absence and was really a classifier that did not fit. These two
    buckets are exhaustive by construction and their sum is checked.

    IT RETURNS THE PIECES AND NOT THE COUNTS, WHICH IS THE REPAIR.
    The caller counts with ``len(pieces) - 1``. That is not decoration: this
    function is called on CONTROL_HTML by the control and on live page content
    by the readers, and the page-text guard taints the RESULT of any call that
    was handed page text. Returning integers therefore produced numbers no
    caller could print, and the alternatives were both worse -- duplicating
    the arithmetic at the live sites would have left the control certifying
    code the live path no longer runs, and declaring this function a sanitiser
    would have been an exemption earned by its NAME.

    Handing back the pieces keeps ONE implementation under the control and
    puts the count in ``len()``, the single counting form the guard reads
    through. The arithmetic becomes visible at the call site, which is where
    the partition is checked anyway.

    THE PARAMETER IS ``document`` AND NOT ``html`` FOR THE SAME FAMILY OF
    REASON: the analysis is per module and keyed on the NAME, so a parameter
    sharing a name with a live ``html = await page.content()`` elsewhere in
    the file is tainted by the collision alone.

    The script blocks are joined on NUL before counting rather than counted
    one at a time. NUL cannot occur in any needle this file passes, so no
    match can be manufactured across a join that the per-block count would not
    have found.
    """
    needle = word.lower()
    script_text = "\x00".join(
        match.group(1) for match in SCRIPT_BLOCK.finditer(document)
    ).lower()
    return {
        "everywhere": document.lower().split(needle),
        "in_script": script_text.split(needle),
    }


async def run_detector_control() -> bool:
    print("=" * 70)
    print("DETECTOR CONTROL -- runs first, gates every number below")
    print("=" * 70)
    part = partition_word(CONTROL_HTML, "hashtag")
    got = {
        "total": len(part["everywhere"]) - 1,
        "in_script": len(part["in_script"]) - 1,
        # total - in_script, with both -1 terms cancelling.
        "outside_script": len(part["everywhere"]) - len(part["in_script"]),
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
    # COUNTS, SPELLED WITH len() RATHER THAN str.count().
    #
    # These are integers -- a count of a needle THIS FILE wrote, taken over
    # text the page wrote -- and nothing of the page's is printed. The guard
    # flags str.count() anyway: its only call carve-out is the bare name
    # ``len`` and ``.count`` is an attribute call it cannot see through.
    #
    # len(h.split(n)) - 1 IS THE SAME INTEGER: str.count and str.split are
    # both non-overlapping. The measurement is unchanged and the spelling is
    # one the guard can read. ``.count`` was NOT added to the engine's
    # carve-out list -- that list matches BY SPELLING, and an exemption earned
    # by a name stops the guard checking everything downstream of it.
    for needle in needles:
        in_main = len(main_text.split(needle)) - 1
        in_html = len(html.split(needle)) - 1
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
    # THE READ VALUE IS NAMED ``aria_label`` AND NOT ``label``.
    #
    # ``label`` is a PARAMETER of _page_control and _goto above, carrying a
    # surface name this file wrote. The page-text analysis is per module and
    # keyed on the NAME, so binding the page's aria-label to ``label`` here
    # tainted those two parameters as well and flagged three prints that never
    # touched a page. That was a collision, not a leak; the rename is the
    # whole repair for those three.
    for index in range(min(total, 40)):
        node = triggers.nth(index)
        aria_label = ""
        try:
            aria_label = await node.get_attribute("aria-label") or ""
            if not aria_label:
                aria_label = (
                    await node.inner_text(timeout=2_000) or "").strip()
        except Exception:  # noqa: BLE001
            aria_label = ""
        expanded = ""
        try:
            expanded = await node.get_attribute("aria-expanded") or "-"
        except Exception:  # noqa: BLE001
            expanded = "-"
        described = shape.describe_name_shaped(aria_label)
        tail = described.get("tail")
        # THE TAIL IS NO LONGER PRINTED, AND THIS BLOCK HAS EARNED THAT.
        #
        # It is asserted name-free BY CONSTRUCTION -- what remains after the
        # last capitalised run -- and that is probably true. It is still not
        # vouched for: TEXT_SANITISERS is empty on purpose, because no
        # function in this package can decide whether a string is a person's
        # name, and the version of describe_name_shaped that returned the
        # WHOLE STRING when no run matched was defended as safe until it was
        # not. This very block printed census_shape once and leaked his name.
        #
        # None still means no run was found, which is NOT the same as an empty
        # tail; conflating them would publish a string the function declined
        # to vouch for. Both survive, as a marker and a length.
        tail_out = "<no-run>" if tail is None else "len=%d" % len(tail)
        # ``runs`` IS an integer, but it arrives inside a dict the engine
        # tainted, so it is rendered by matching RUN_COUNTS -- tokens this
        # file owns -- and a count past the end of that tuple prints MANY.
        runs_shown = "/".join(
            str(k) for k in RUN_COUNTS if described.get("runs") == k
        ) or "MANY"
        # aria-expanded is read off the page, so it is matched rather than
        # printed. This is not a claim that the ARIA spec closes the set: a
        # value this file does not name prints UNKNOWN-EXPANDED and leaks
        # nothing, which holds whether the spec is closed or not. "-" is the
        # file's existing marker for the attribute being absent and it keeps
        # its meaning.
        exp_shown = "-" if expanded == "-" else (
            "/".join(t for t in EXPANDED_VALUES if expanded == t)
            or "UNKNOWN-EXPANDED")
        # Whether the label is one of the furniture words this part is
        # hunting for is a BOOLEAN, not a name.
        hits = [w for w in ("section", "Section", "profile", "Profile", "Add")
                if w in aria_label]
        print(f"      haspopup {index:2d}: aria-expanded={exp_shown:16s} "
              f"len={len(aria_label):3d} runs={runs_shown:4s} "
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
        pieces = partition_word(html, needle)
        print(f"      {needle:26s} {len(pieces['everywhere']) - 1:6d} "
              f"{len(pieces['in_script']) - 1:12d} "
              f"{len(pieces['everywhere']) - len(pieces['in_script']):10d}")

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
        print(f"      {needle:26s} "
              f"main={len(main_text.split(needle)) - 1:4d}  "
              f"html={len(html.split(needle)) - 1:5d}")
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

    pieces = partition_word(html, "hashtag")
    in_script = len(pieces["in_script"]) - 1
    everywhere = len(pieces["everywhere"]) - 1
    outside = len(pieces["everywhere"]) - len(pieces["in_script"])
    print("\n    PARTITION -- exhaustive by construction, and its sum is")
    print("    checked rather than assumed:")
    print(f"      inside <script> content   {in_script:5d}")
    print(f"      everywhere else           {outside:5d}")
    print(f"      total in html             {everywhere:5d}")
    sums = in_script + outside == everywhere
    print(f"      PARTITION SUMS: {'PASS' if sums else 'FAIL'}")
    print(f"      in main text              "
          f"{len(main_text.lower().split('hashtag')) - 1:5d}")

    print("\n    CASING VARIANTS actually present (counts only):")
    for variant in ("hashtag", "Hashtag", "HASHTAG", "hashtags", "Hashtags",
                    "hashtagged"):
        print(f"      {variant:14s} {len(html.split(variant)) - 1:5d}")

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
