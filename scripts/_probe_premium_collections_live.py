"""FIRE ``job_collections.read_job_collection`` at the two Premium collections.

``/jobs/collections/top-applicant`` and ``/jobs/collections/top-choice`` were
admitted to the read allowlist on 2026-09-20 and their shaper landed in the
same commit, on this repository's rule that an address and its name-free reader
land together or neither lands. **Nobody had ever opened either page**, so the
shaper was a HYPOTHESIS built off two captured SIBLING job lists, and
``tests/test_every_orphan_module_is_ruled.DELIBERATELY_UNWIRED`` rules it
unwired until somebody spends the one page load that turns it into a reading.

THIS SCRIPT IS THAT PAGE LOAD. It runs the exact call
``_audit/2026-09-20-the-premium-four.md`` section 9 names, and it exists
because that section also states what each outcome banks -- so the run cannot
end in an argument about what the number meant.

## THE CONTROL IS RUN TWICE, ON TWO DIFFERENT KINDS OF INPUT

A zero here has THREE causes and the reading must separate all of them: the
collection is empty, the target does not draw the sibling shape, or the
session/network is down. One control cannot separate three things.

    CONTROL 1   the synthetic fixture, via set_content, NO page load.
                Proves the reader CAN count at all in this process. Its
                expected reading is pinned in tests/test_job_collections.py
                and repeated here, so a drift fails loudly rather than
                quietly producing a control that always passes.

    CONTROL 2   a LIVE LinkedIn job list -- /jobs/search/ -- through THE SAME
                READER. Proves the selectors this module measured off the
                captures still match what LinkedIn draws TODAY, on this
                account, in this session. A synthetic fixture cannot say that,
                because this repository wrote both sides of it.

**CONTROL 2 IS THE ONE THAT MATTERS AND IT IS THE ONE THAT DID NOT EXIST.**
The premium-four wave proved the reader against markup the premium-four wave
authored. That is a test, not a measurement.

## THE TWO TIERS ARE BOTH REPORTED, ALWAYS

The module's first version counted hydrated cards and would have under-reported
by 3.4x -- 7 where the collection held 24. So every line below prints ``slots``
(tier 1, the answer) BESIDE ``hydrated`` (tier 2, the render state), and the
verdict keys on slots. A single number from this surface is a wrong answer
waiting for somebody to quote it.

## WHAT LEAVES THIS PROCESS

Integers, booleans, literals of this file or of ``job_collections``, and the
RELATION between a landed url and the asked one. **No posting id is printed**
-- the reader is allowed to return them and a transcript is not the place for
them, so they are COUNTED here and the raw reading is written to gitignored
``_state/`` for whoever needs one.

Filter captions on the analytics surface are handled the same way and harder:
they are page text, the page-text rule has a DELIBERATELY EMPTY sanitiser list,
and this package has no instrument that can decide whether a string is a
person's name. So a caption is printed ONLY when it matches
:data:`CAPTION_CANDIDATES`, a vocabulary THIS FILE authors; anything else is
reported as a length and a word skeleton. That is ``EMPTY_STATE_NEEDLES``'
pattern, reused with its reason.

## THE BADGE IS READ BEFORE AND AFTER

The invitation counter is a control that must NOT move. Nothing here is
believed to touch it, which is exactly why it is worth reading: a control that
must not move, and does not, is the only evidence the instrument can tell the
difference between a read and a press.

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000 \\
        ./venv/Scripts/python.exe scripts/_probe_premium_collections_live.py
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from linkedin_server import dom, job_collections, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: Where a raw reading goes. GITIGNORED, and it is the only place a posting id
#: or a caption is written.
STATE = pathlib.Path(__file__).resolve().parent.parent / "_state"

#: THE LIVE CONTROL SURFACE. A job list this account is known to be served,
#: read through the SAME reader as the targets. Chosen over
#: ``/jobs/collections/recommended/`` because it is one of the two surfaces
#: ``job_collections`` measured its selectors off, so a divergence here is a
#: fact about LinkedIn having changed since 2026-09-20 rather than about the
#: sibling being a different template.
CONTROL_URL = "https://www.linkedin.com/jobs/search/"

#: The analytics surface, for the two undocumented filter captions. One load.
ANALYTICS_URL = "https://www.linkedin.com/analytics/profile-views/"

#: THE PINNED CONTROL READING, copied from
#: ``tests/test_job_collections.test_the_control_fixture_produces_its_known_reading``.
#: Repeated rather than imported: a control that reads its expectation from the
#: thing under test is not a control.
FIXTURE_EXPECTED = {
    "collection": "top-choice",
    "slots": 4,
    "slots_outside_main": 1,
    "hydrated": 2,
    "hydrated_outside_main": 1,
    "ids_refused": 1,
    "list_container_seen": True,
    "refusal": None,
}
FIXTURE_EXPECTED_IDS = 3

#: **A VOCABULARY THIS FILE AUTHORS, AND THE ONLY WAY A CAPTION IS EVER
#: PRINTED.** Three of these are the captions ``dom.py`` already documents; the
#: rest are hypotheses about the two it does not, drawn from LinkedIn's own
#: published analytics vocabulary. A match prints the literal from THIS tuple,
#: never the page's string -- so the output alphabet stays closed even if
#: LinkedIn's caption differs by a space or a case.
CAPTION_CANDIDATES: tuple[str, ...] = (
    # the three dom.py documents
    "past 90 days",
    "interesting viewers",
    "company",
    # hypotheses for the two it does not
    "all profile viewers",
    "all viewers",
    "job title",
    "all job titles",
    "location",
    "all locations",
    "industry",
    "all industries",
    "seniority",
    "date range",
    "past 7 days",
    "past 28 days",
    "past 30 days",
    "past 12 months",
    "viewers by company",
    "viewers by job title",
    "viewers by location",
    "show more analytics",
    "discover more insights with premium",
    "people who viewed your profile",
    "who viewed your profile",
    "your profile viewers",
    "filter by company",
    "filter by job title",
    "filter by location",
)


def _relation(landed: str, asked: str) -> str:
    """Did the address serve, or did LinkedIn send us somewhere else?

    THE INTERESTS LESSON, applied. ``/in/me/details/interests/`` is on the
    allowlist and REDIRECTS to the profile, so an admitted address is not a
    served one -- and a probe that does not compare the landed url to the
    requested one cannot tell those apart.

    RETURNS A RELATION AND NEVER A URL. Every branch below yields a literal or
    an integer depth; no part of either input survives into the result. The
    depths are taken with ``len`` rather than a helper, because counting a
    thing is the discipline this package uses INSTEAD of printing it, and
    ``tests/test_navigation_is_never_derived.py`` recognises that form.

    ITS LOCALS ARE NAMED FOR THIS FUNCTION, and that is not cosmetic. The
    consent guard tracks tainted names ACROSS A WHOLE MODULE, not per scope,
    so a local called ``before`` here made every ``before`` in this file read
    as navigation-derived -- including three in the cost report, which are
    tallies of shaped control names and touch no url at all. Three of that
    guard's four findings against this file were that collision.
    """
    if str(landed) == str(asked):
        return "SERVED, exact"
    asked_depth = len([seg for seg in urlsplit(str(asked)).path.split("/") if seg])
    landed_depth = len([seg for seg in urlsplit(str(landed)).path.split("/") if seg])
    if asked_depth != landed_depth:
        return f"REDIRECTED, path depth {asked_depth} -> {landed_depth}"
    return "SERVED, same depth, different url"


def _skeleton(text: str) -> str:
    """A caption reduced to WORD LENGTHS. Carries no letter and no digit.

    ``"Past 90 days"`` becomes ``"4-2-4"``. This is what gets printed for a
    caption that matches no authored candidate: enough structure to recognise
    the same caption again, or to aim a better hypothesis at it next session,
    and provably not enough to reconstruct a name. Every character of the
    output is a digit or a hyphen, which
    ``test_the_skeleton_cannot_carry_a_letter`` asserts over adversarial input.
    """
    return "-".join(str(len(word)) for word in str(text).split() if word)


def _caption_verdict(caption: str) -> dict[str, object]:
    """One caption -> a literal of this file, or a shape. Never the page's text."""
    folded = " ".join(str(caption).split()).strip().lower()
    for candidate in CAPTION_CANDIDATES:
        if folded == candidate:
            return {"named": candidate, "chars": len(caption),
                    "words": len(folded.split()), "skeleton": _skeleton(caption)}
    return {"named": None, "chars": len(caption),
            "words": len(folded.split()), "skeleton": _skeleton(caption)}


async def _badge(page, label: str) -> None:
    """The counter that must NOT move. Printed as its own integers only."""
    try:
        read = await dom.read_invitation_badge(page)
    except Exception as error:  # noqa: BLE001
        print(f"    badge {label}: UNREADABLE ({type(error).__name__})")
        return
    # INTEGERS AND A PRESENCE FLAG. The badge's ``label`` is a raw page string
    # -- measured 2026-09-19, it came back as a nav element's accessible name --
    # so it is counted, never shown.
    shown = {
        key: value for key, value in sorted(read.items())
        if key != "raw" and isinstance(value, (int, bool)) and not isinstance(value, str)
    }
    has_label = bool(read.get("label"))
    print(f"    badge {label}: " + "  ".join(
        f"{key}={value!r}" for key, value in shown.items()
    ) + f"  label_present={has_label}  error={read.get('error') is not None}")


def _print_reading(out: dict) -> None:
    """BOTH TIERS, ALWAYS, and the control a zero is only readable beside."""
    print(f"    collection        : {out['collection']!r}")
    print(f"    slots      TIER 1 : {out['slots']}   (outside main: "
          f"{out['slots_outside_main']})   <-- THE POSTING COUNT")
    print(f"    hydrated   TIER 2 : {out['hydrated']}   (outside main: "
          f"{out['hydrated_outside_main']})   <-- render state, NOT the answer")
    print(f"    containers        : {out['containers']}   (outside main: "
          f"{out['containers_outside_main']})")
    print(f"    list_container_seen: {out['list_container_seen']}   <-- THE CONTROL")
    print(f"    job_ids returned  : {len(out['job_ids'])}   refused by shape: "
          f"{out['ids_refused']}   (ids are COUNTED here, never printed)")
    print(f"    empty_state_needles: {out['empty_state_needles']}")
    print(f"    refusal           : {out['refusal']!r}   error: {out['error']!r}")


def _banks(out: dict) -> str:
    """SECTION 9'S RULE, ENCODED. The verdict is not decided at reporting time.

    Written as a function so the three outcomes are enumerable by reading it,
    rather than being an argument somebody has after seeing the number.
    """
    if out["error"] is not None:
        return ("BANKS NOTHING -- the read itself failed. This is an OUTAGE, "
                "not an absence, and it is not a fact about the account.")
    if not out["list_container_seen"]:
        return ("BANKS NOTHING -- list_container_seen is False, so the target "
                "does NOT draw the sibling shape. FIX THE READER. Do NOT "
                "report that he has no postings here.")
    if out["slots"] > 0:
        return "BANKS THE ROW -- a drawn list with %d slots. GAP -> BUILT." % out["slots"]
    return ("BANKS THE ROW as MEASURED-EMPTY -- the list container drew and "
            "held zero slots. That is a fact about HIS ACCOUNT, not about the "
            "reader.")


async def _capture(page, name: str) -> int:
    """Write the raw document to gitignored ``_state/``. Returns its length.

    RAW TO ``_state``, DERIVED TO THE AUDIT. A capture of a LinkedIn page
    carries his name, his connections' names and his account ids, and the only
    number about it that may be printed is how big it was.
    """
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        markup = await page.content()  # readonly-ok
        path = STATE / name
        path.write_text(markup, encoding="utf-8")
        return len(markup)
    except Exception as error:  # noqa: BLE001
        print(f"    capture {name}: FAILED ({type(error).__name__})")
        return 0


async def _fire(page, label: str, url: str, expect: int | None,
                capture_as: str) -> dict:
    """assert_read_url -> navigate -> read. The exact section 9 call."""
    print(f"\n--- {label}")

    # THE BOUNDARY IS ASKED FIRST, BY NAME. BROWSER.goto asks it again
    # internally; this call is here so a lost allowlist entry refuses at a
    # readable place rather than from inside a navigation.
    if not readonly.is_read_url(url):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True, "banks": "BANKS NOTHING -- boundary refused."}

    landed = await BROWSER.goto(page, url)
    relation = _relation(landed, url)
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    LANDING           : {relation}")

    # **THE PATH, SEPARATED FROM THE QUERY.** ``_relation`` compares the WHOLE
    # url, so LinkedIn appending a tracking query reads as "different url" --
    # indistinguishable, in its output, from a redirect to another page. That
    # ambiguity is the thing a collection reading cannot survive: three
    # addresses all reporting 25 slots is either three collections or one page
    # served three times, and the first run could not tell them apart.
    #
    # BOTH FACTS BELOW ARE COMPARISONS, WHICH IS WHY THEY MAY BE PRINTED. A
    # comparison yields a boolean whatever it compared, so no part of the
    # landed url survives into the output -- the same carve-out every
    # auth-wall check in this package relies on, and the reason neither line
    # needs a sanitiser.
    path_survived = (
        urlsplit(str(landed)).path.rstrip("/") == urlsplit(str(url)).path.rstrip("/")
    )
    query_added = urlsplit(str(landed)).query != urlsplit(str(url)).query
    route_word = job_collections.COLLECTIONS[expect] if expect is not None else None
    route_word_kept = (
        route_word is not None and route_word in urlsplit(str(landed)).path
    )
    print(f"    path survived     : {path_survived}   query added: {query_added}"
          f"   route word kept: {route_word_kept}")
    if walled:
        print("    AUTH WALL. Nothing else measured, and this is an OUTAGE.")
        return {"authwall": True,
                "banks": "BANKS NOTHING -- auth wall. An outage, not an absence."}

    out = await job_collections.read_job_collection(page, expect=expect)
    _print_reading(out)
    chars = await _capture(page, capture_as)
    print(f"    capture           : {capture_as}  ({chars} chars, gitignored)")
    verdict = _banks(out)
    print(f"    VERDICT           : {verdict}")
    return {"relation": relation, "reading": out, "banks": verdict,
            "capture_chars": chars, "path_survived": path_survived,
            "route_word_kept": route_word_kept}


async def _analytics(page) -> dict:
    """The five filter captions. One load, and no caption is printed raw."""
    print("\n--- ANALYTICS  profile-views  (the two undocumented captions)")
    if not readonly.is_read_url(ANALYTICS_URL):
        print("    REFUSED BY THE READ BOUNDARY. Nothing loaded.")
        return {"refused": True}

    landed = await BROWSER.goto(page, ANALYTICS_URL)
    relation = _relation(landed, ANALYTICS_URL)
    walled = "/login" in str(landed) or "/checkpoint" in str(landed)
    print(f"    LANDING           : {relation}")
    if walled:
        print("    AUTH WALL. Nothing measured.")
        return {"authwall": True}

    try:
        insights = await dom.read_profile_views_insights(page)
    except Exception as error:  # noqa: BLE001
        print(f"    READER FAILED: {type(error).__name__} -- an OUTAGE, not an absence.")
        return {"error": type(error).__name__}

    captions = [str(item) for item in (insights.get("filters") or [])]
    verdicts = [_caption_verdict(item) for item in captions]
    observed = dict(insights.get("observed") or {})
    print(f"    filters drawn     : {len(captions)}")
    print(f"    main_present={observed.get('main_present')}  "
          f"main_chars={observed.get('main_chars')}  "
          f"viewer_rows={observed.get('viewer_rows')}")
    for index, verdict in enumerate(verdicts):
        named = verdict["named"]
        shown = repr(named) if named else "UNIDENTIFIED (no authored candidate matched)"
        print(f"      caption {index}: chars={verdict['chars']:>3}  "
              f"words={verdict['words']}  skeleton={verdict['skeleton']:<12}  {shown}")

    chars = await _capture(page, "cap-profile-views-captions.html")
    print(f"    capture           : cap-profile-views-captions.html "
          f"({chars} chars, gitignored)")
    try:
        STATE.mkdir(parents=True, exist_ok=True)
        (STATE / "profile-views-captions-raw.json").write_text(
            json.dumps(captions, ensure_ascii=False, indent=2), encoding="utf-8")
        print("    raw captions      : _state/profile-views-captions-raw.json "
              "(gitignored -- the only place they are written)")
    except Exception as error:  # noqa: BLE001
        print(f"    raw captions NOT written: {type(error).__name__}")
    return {"relation": relation, "count": len(captions), "verdicts": verdicts}


async def main() -> int:
    if os.environ.get("LINKEDIN_CDP_ATTACH") != "1":
        print("REFUSED: run with LINKEDIN_CDP_ATTACH=1. Launch mode would open "
              "a SECOND Chrome on the signed-in profile, which is the "
              "2026-08-25 failure that cost the session.")
        return 2

    print("=== THE PREMIUM TWO, FIRED. Integers, relations and verdicts only.")
    print("    Nothing here clicks, fills, submits or presses.")

    _own_page = None
    try:
        async with BROWSER.session() as page:
            _own_page = page

            print("\n### CONTROL 1: the synthetic fixture. NO page load.")
            print("    A reader that cannot count a known DOM makes every zero")
            print("    below meaningless.")
            await page.set_content(  # readonly-ok -- local markup, no navigation
                job_collections.control_fixture(),
                wait_until="domcontentloaded", timeout=60_000)
            fixture = await job_collections.read_job_collection(page, expect=1)
            drift = {key: (value, fixture.get(key))
                     for key, value in FIXTURE_EXPECTED.items()
                     if fixture.get(key) != value}
            ids_ok = len(fixture["job_ids"]) == FIXTURE_EXPECTED_IDS
            print(f"    pinned fields matching : {len(FIXTURE_EXPECTED) - len(drift)}"
                  f" of {len(FIXTURE_EXPECTED)}")
            print(f"    job_ids returned       : {len(fixture['job_ids'])} "
                  f"(MUST be {FIXTURE_EXPECTED_IDS})")
            if drift or not ids_ok:
                print(f"    THE READER DRIFTED: {drift}")
                print("    EVERY ZERO BELOW WOULD BE MEANINGLESS. Aborting.")
                return 1
            print("    CONTROL 1 PASSED -- the reader can count.")

            print("\n### CONTROL 2: a LIVE job list, through the SAME reader.")
            print("    This is the control the premium-four wave could not run.")
            control = await _fire(page, "CONTROL  jobs search", CONTROL_URL,
                                  None, "cap-control-jobs-search.html")

            # **THE BADGE IS READ HERE AND NOT EARLIER, AND THE FIRST RUN OF
            # THIS SCRIPT GOT IT WRONG.** It read "before" while the page still
            # held CONTROL 1's synthetic markup -- a document with no LinkedIn
            # nav in it -- so the reading was 0 by construction and the "after"
            # reading of 1 looked like a counter that had MOVED. It had not;
            # the instrument had been pointed at the wrong document. A control
            # that must not move is worthless if its baseline is taken
            # somewhere the thing being controlled does not exist.
            await _badge(page, "before")

            print("\n### THE TARGETS. Nobody has ever opened either address.")
            top_applicant = await _fire(
                page, "TARGET 1  top-applicant",
                job_collections.collection_url(0), 0,
                "cap-collection-top-applicant.html")
            top_choice = await _fire(
                page, "TARGET 2  top-choice",
                job_collections.collection_url(1), 1,
                "cap-collection-top-choice.html")

            analytics = await _analytics(page)

            await _badge(page, "after")
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print(f"\nRUN ABORTED: {name}")
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. This is "
                  "the cross-process guard working, not a defect.")
        elif "BrowserUnavailable" in name:
            print("    DO NOT QUIT CHROME. That remedy is wrong and "
                  "destructive. Re-run with "
                  "LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000.")
        else:
            print(f"    {error}")
        return 1
    finally:
        # CLOSE THE TAB THIS RUN OPENED. In ATTACH mode ``BROWSER._page()``
        # caches the page and ``session()``'s finally only touches an idle
        # timer, so the tab OUTLIVES THE PROCESS. THE PAGE, NEVER THE CONTEXT.
        if _own_page is not None:
            try:
                await _own_page.close()
                print("\n    tab closed")
            except Exception as error:  # noqa: BLE001
                print(f"\n    tab NOT closed: {type(error).__name__}")

    print("\n=== VERDICT")
    control_reading = control.get("reading") or {}
    control_ok = bool(control_reading.get("list_container_seen"))
    print(f"    CONTROL 2 saw a live job list : {control_ok}")
    if not control_ok:
        print("    THE LIVE CONTROL DID NOT FIRE. Every zero above is a fact")
        print("    about this session or about LinkedIn's markup having moved,")
        print("    NOT about the two collections. NOTHING BANKS.")
        return 1
    print(f"    control  slots/hydrated       : {control_reading.get('slots')}"
          f" / {control_reading.get('hydrated')}")
    for label, result in (("top-applicant", top_applicant), ("top-choice", top_choice)):
        reading = result.get("reading") or {}
        print(f"    {label:<14} slots/hydrated : {reading.get('slots')}"
              f" / {reading.get('hydrated')}   seen="
              f"{reading.get('list_container_seen')}")
        print(f"                   {result.get('banks')}")

    # **THE ANALYTICS READING IS BRANCHED ON, NOT PRINTED.** The first version
    # of this block printed `analytics.get('count')` and nothing else, so a
    # refusal, an auth wall or a reader exception would all have rendered as
    # `None` beside the word "drawn" -- a control taken and never acted on,
    # which is the decorative-control defect this repository has a guard for.
    # It caught this on CI, on a test the local impact gate did not select.
    # A count that was never taken and a count of zero are different findings
    # and they do not share a line.
    if analytics.get("refused"):
        print("    analytics captions drawn      : NOT READ -- the read "
              "boundary refused the address. Nothing loaded.")
    elif analytics.get("authwall"):
        print("    analytics captions drawn      : NOT READ -- auth wall. "
              "An OUTAGE, not an absence.")
    elif analytics.get("error"):
        print(f"    analytics captions drawn      : NOT READ -- the reader "
              f"raised {analytics['error']}. An OUTAGE, not an absence.")
    else:
        drawn = int(analytics.get("count") or 0)
        named = sum(1 for v in analytics.get("verdicts") or [] if v.get("named"))
        print(f"    analytics captions drawn      : {drawn}  "
              f"({named} matched an authored candidate, "
              f"{drawn - named} unidentified)")
        if not drawn:
            print("    THE CAPTION READER RETURNED NOTHING. That is a reading "
                  "about the reader until a control says otherwise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
