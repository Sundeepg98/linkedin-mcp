"""What do the three REACHABLE unmeasured surfaces actually draw?

THREE OF THE FIVE MEASURE BLOCKERS SIT ON PAGES THIS SERVER MAY ALREADY OPEN,
and nobody has looked at any of them. The other two (`GROUPS-SURFACE` 32 rows,
`EVENTS-SURFACE` 18 rows) are refused by the read boundary and are measured by
``scripts/_probe_unmeasured_surface_addresses.py``, which needs no browser.
This file measures the three that are reachable:

    /jobs/view/<id>   PANEL-NOT-OBSERVED (3 rows: J25, J29, J30)
                      Does the posting still draw "Why am I seeing this job"
                      and a Skills Match insight? Nobody knows -- the census
                      found them on NEITHER committed capture NOR the live
                      posting, and "not observed" is not "not drawn".

    /messaging/       CONVERSATION-OVERFLOW-MENU (10 rows)
                      NOT by pressing it. The question this asks instead is
                      cheaper and has never been put: IS THE MENU ALREADY IN
                      THE DOM? A dropdown whose items are rendered collapsed
                      needs no press to be read, and a dropdown built on
                      demand does. That answer decides whether these 10 rows
                      need a ruling at all.

    /feed/            HASHTAG-EXISTENCE (3 rows: N194, C11, C52)
                      The census's hashtag source article returns HTTP 404 and
                      two independent help-index queries return no
                      hashtag-following article at all. So the open question is
                      literally whether the product still has the surface. A
                      feed that draws hashtag anchors says it does.

## The settle verdict is not optional, and this file is built around that

A ZERO FROM AN UNRENDERED PAGE AND A ZERO FROM A PAGE WITH NO SUCH CONTROL ARE
THE SAME ZERO. `/feed/` has a measured baseline (277 controls) and gets the
shipped comparison. `/messaging/` and `/jobs/view/<id>` HAVE NONE -- neither is
in ``server.CENSUS_SETTLED_CONTROLS`` -- so a single reading of either would
report `unknown`, which is the ABSENCE of a check and not a check passing.

THIS RUNS IN STAGES SO EACH OF THOSE TWO IS READ TWICE. A surface earns a
baseline by being read more than once and agreeing with itself; that is how
every entry in the shipped table was earned, and it is the only thing that
converts `unknown` into a number.

## The posting carries its own CONTROL, and it is a strong one

`_audit/2026-09-03-linkedin-gap-blockers.md` section 6 measured three needles
on this exact surface, across two committed captures AND a live posting:

    "Show match details"      exactly 1
    "Show Premium Insights"   exactly 1
    "How you match"           exactly 0

Those three are run here as the CONTROL. If this probe reproduces 1/1/0, its
needle counting is calibrated on the page it is about to make a claim about.
If it does not, every other count it prints is suspect and it says so. A count
that cannot be checked against a known value is a number nobody can act on.

## What the cost is, stated before it is paid

`/messaging/` is the only surface here whose load may touch a third party:
LinkedIn's desktop inbox auto-selects a conversation and opening one can fire a
read receipt. THIS IS NOT A NEW COST CLASS -- ``linkedin_open_messaging``
performs exactly this one navigation and ships with the cost stated as accepted
(``dom.py`` MESSAGING_FILTERS note).

AND IT IS MEASURED HERE RATHER THAN ASSUMED, by the discipline the messaging
probe designed: the messaging nav badge is drawn on `/feed/`, which is a
surface this run loads anyway. Read the badge from the feed BEFORE the inbox
load and again AFTER, on a page being loaded regardless, for zero marginal
cost. A DROP is the auto-open consuming unread state. A badge that reads zero
both times cannot separate "consumed nothing" from "there was nothing to
consume", and this probe says so instead of reporting a clean run.

## Bounds

**IT NAVIGATES MODULE-LEVEL CONSTANTS AND NOTHING ELSE.** Three addresses,
three constants, none built from anything a page said.

**NOTHING IS PRESSED, TYPED, SCROLLED OR SUBMITTED.** No click, no fill, no
filter pill. ``page.locator(...).count()`` and ``page.inner_text("main")`` are
reads; no script is injected by this file.

**COUNTS AND SHAPES ONLY. NO IDENTITY.** No name, no url, no member path, no
message text, no heading text. Needles are LinkedIn's own furniture words and
are printed as literals BECAUSE THEY ARE THE QUESTION; what is printed beside
them is an integer. The census records that reach print are reduced to their
``shape``/``role``/``aria_expanded`` triples by ``dom.read_surface_census``,
which discards raw accessible names inside itself. Page HTML is read into a
local and counted; it is never printed and never written.

**NO OUTPUT PATH.** None, and no constant that could become one.

**RATE DISCIPLINE: two page loads per invocation, PAUSE_S apart.**

Run:  python scripts/_probe_unmeasured_surfaces_live.py a   feed, profile
      python scripts/_probe_unmeasured_surfaces_live.py b   posting, messaging
      python scripts/_probe_unmeasured_surfaces_live.py c   both again
Writes NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: THE THREE ADDRESSES, EVERY ONE A MODULE-LEVEL CONSTANT.
FEED_URL = f"{BASE_URL}/feed/"
MESSAGING_URL = f"{BASE_URL}/messaging/"
#: HIS OWN PROFILE. Allowlisted, baselined at 233 controls, and it is the
#: surface ``linkedin_my_profile`` already loads. IT IS HERE BECAUSE OF WHAT
#: THE INTERESTS SECTION LISTS: LinkedIn puts GROUPS, NEWSLETTERS and
#: companies he follows on his own profile. That makes this one read the
#: PRECONDITION QUESTION for two blockers he cannot otherwise reach --
#: `GROUPS-SURFACE` (32 rows) and `EVENTS-SURFACE` (18) -- because if he
#: belongs to no group, most of those rows are unreachable in principle for
#: this account and the blockers are not the size they are recorded as.
#: `/in/me/details/interests/` is NOT on the allowlist; `/in/me/` is.
PROFILE_URL = f"{BASE_URL}/in/me/"
#: HIS OWN INTERESTS PAGE, ADMITTED 2026-09-04 (readonly commit 90bfe21).
#: THE PRECONDITION SURFACE. `/in/me/` renders the Interests SECTION only
#: below the fold and this probe does not scroll, which is why the stage-a
#: reading of it failed its own control. This is the dedicated page, the
#: sibling of `/in/me/details/skills/` -- already proven to serve 20 cards
#: through the shipped harvest.
INTERESTS_URL = f"{BASE_URL}/in/me/details/interests/"
#: THE CONTROL FOR THE INTERESTS READ. `scripts/_probe_self_details_url.py`
#: established that this one IS served and that 20 skill cards come back
#: through the shipped harvest. If skills lands at its own depth and
#: interests redirects to the profile, the redirect is a fact about the
#: interests address rather than about `/details/` pages or about the
#: session. Without it, a redirect is uninterpretable.
SKILLS_URL = f"{BASE_URL}/in/me/details/skills/"
EDUCATION_URL = f"{BASE_URL}/in/me/details/education/"

#: THE POSTING. Copied from ``scripts/_probe_free_reads_shapes.py``, where it
#: was filled in on 2026-09-03 from ``linkedin_saved_jobs`` -- the one row in
#: his Saved tab. A POSTING id, not a person. All digits, at least six, which
#: is exactly what ``readonly._ALLOWED_URL_PATTERNS`` admits.
JOB_ID = "4423880462"
JOB_POSTING_URL = f"{BASE_URL}/jobs/view/{JOB_ID}"

#: Seconds between page loads. Rate discipline, and it is the reason this file
#: runs in stages rather than doing all six loads at once.
PAUSE_S = 3.0

#: WHAT A SETTLED `/feed/` DRAWS, and where the number comes from.
#: ``server.CENSUS_SETTLED_CONTROLS["feed"] == 277``, itself measured from
#: three readings (297, 277, 287). Copied as a literal rather than imported so
#: this script does not import the MCP server module to read one integer.
#: THE FLOOR IS ``server.CENSUS_SETTLE_FLOOR`` == 0.5, chosen against the two
#: observed failures, both of which came in at roughly a QUARTER.
SETTLED_CONTROLS: dict[str, int] = {"feed": 277, "profile": 233}
SETTLE_FLOOR = 0.5

#: THE CONTROL NEEDLES FOR THE POSTING, with the counts section 6 of
#: ``_audit/2026-09-03-linkedin-gap-blockers.md`` measured across two committed
#: captures AND a live posting. This probe reproduces them or admits it did
#: not. A control that cannot fire is not a control.
POSTING_CONTROL_NEEDLES: tuple[tuple[str, int], ...] = (
    ("Show match details", 1),
    ("Show Premium Insights", 1),
    ("How you match", 0),
)

#: THE TARGET NEEDLES FOR `PANEL-NOT-OBSERVED`. J25 is the "why am I seeing
#: this" panel; J29 is the Skills Match insight; J30 is the write hanging off
#: J29 and cannot exist unless J29 does.
POSTING_TARGET_NEEDLES: tuple[tuple[str, str], ...] = (
    ("Why am I seeing this job", "J25"),
    ("Why am I seeing this", "J25 looser"),
    ("Skills Match", "J29"),
    ("skills match your profile", "J29 looser"),
    ("Add skill", "J30"),
)

#: The control needles, relabelled so they print beside the value they must
#: reproduce. Built once at module level rather than inside the reporter, so
#: the expected numbers are visible in one place.
POSTING_CONTROL_NEEDLES_LABELLED: tuple[tuple[str, str], ...] = tuple(
    (needle, "CONTROL, must read %d" % expected)
    for needle, expected in POSTING_CONTROL_NEEDLES
)


#: HASHTAG NEEDLES. The first is the address shape a hashtag feed would use --
#: counted in HTML because an href never appears in visible text. The rest are
#: what a hashtag affordance says on screen.
HASHTAG_NEEDLES: tuple[str, ...] = (
    "/feed/hashtag/",
    "hashtag",
    "#hiring",
    "Followed hashtags",
)

#: INTERESTS-SECTION NEEDLES. LinkedIn writes its section furniture in
#: sentence case, so these are its own words and carry no identity. The
#: question each answers is "does this account HAVE any of this thing", and
#: a zero here is only readable beside the settle line above it.
PROFILE_NEEDLES: tuple[tuple[str, str], ...] = (
    ("Interests", "the section itself -- if this is 0 nothing below counts"),
    ("Groups", "GROUPS-SURFACE precondition, 32 rows"),
    ("Newsletters", "NEWSLETTER-SURFACE, 12 rows, adjacent"),
    ("Companies", "CONTROL -- followed_companies ships, so this MUST be non-zero"),
    ("Top Voices", "a sibling Interests tab"),
    ("Schools", "a sibling Interests tab"),
    ("Events", "EVENTS-SURFACE precondition, 18 rows"),
    ("/groups/", "an href shape -- html only, never visible text"),
    ("/events/", "an href shape"),
    ("/newsletters/", "an href shape"),
)

#: MESSAGING NEEDLES, AND THE FIRST SEVEN ARE THE CONTROL.
#:
#: `dom.MESSAGING_FILTERS` is a CLOSED SET OF SEVEN, and `dom.py` records the
#: measurement behind it: "all six pills are `<button>` with no href", read
#: off the live inbox. So a settled render of this surface DRAWS THIS PILL
#: ROW, and a reading that cannot find it is a reading of a page that had not
#: arrived. THIS SURFACE HAS NO CONTROL COUNT IN `CENSUS_SETTLED_CONTROLS`,
#: so without these seven a zero anywhere on it means nothing -- two agreeing
#: readings catch variance and cannot catch a stable wrong state, which is
#: exactly what this instrument was told twice.
MESSAGING_NEEDLES: tuple[tuple[str, str], ...] = (
    ("Focused", "CONTROL -- filter pill 1 of 7"),
    ("Other", "CONTROL -- pill 2"),
    ("Unread", "CONTROL -- pill 3"),
    ("Starred", "CONTROL -- pill 4"),
    ("Jobs", "CONTROL -- pill 5"),
    ("Connections", "CONTROL -- pill 6"),
    ("InMail", "CONTROL -- pill 7"),
    ("More options", "the overflow trigger label seen on the job card"),
    ("Overflow menu", "a second overflow label seen on the job card"),
    ("aria-haspopup", "html only -- a popup trigger of any kind"),
    ("role=\"menu\"", "html only -- a menu container of any kind"),
)

#: STRUCTURAL SELECTORS. Every one is a role or an ARIA attribute, so not one
#: of them can match on a person's name or a message's text.
#:
#: THE PAIR THAT ANSWERS THE OVERFLOW QUESTION is ``[aria-haspopup]`` against
#: ``[role="menuitem"]``. Triggers WITHOUT items means the menu is built on
#: demand and a capture needs a press. Triggers WITH items means it is already
#: in the DOM and the 10 rows behind `CONVERSATION-OVERFLOW-MENU` can be read
#: without pressing anything at all.
STRUCTURAL_SELECTORS: tuple[str, ...] = (
    "[aria-haspopup]",
    '[aria-expanded="false"]',
    '[aria-expanded="true"]',
    '[role="menu"]',
    '[role="menuitem"]',
    '[role="button"]',
    '[role="dialog"]',
    "[hidden]",
)

#: The six integer tallies ``dom.read_surface_census`` returns under ``counts``.
CENSUS_COUNT_KEYS = (
    "forms",
    "buttons",
    "links",
    "contenteditable",
    "file_inputs",
    "dialogs",
)

#: Which stage loads which two addresses. TWO PER INVOCATION, and the ordering
#: is load-bearing: stage ``a`` reads the badge from the feed BEFORE the inbox
#: load, stage ``b`` reads it again AFTER. Stage ``c`` is the second reading of
#: the two surfaces that have no baseline, which is what earns them one.
STAGES: dict[str, tuple[str, ...]] = {
    # STAGE a COSTS NOTHING AND ANSWERS THE MOST. Both surfaces are
    # allowlisted, both are baselined, and neither carries a third party.
    "a": ("feed", "profile"),
    # The only stage with a cost, and the badge read in ``a`` is its baseline.
    "b": ("posting", "messaging"),
    # The second reading of the two surfaces that have no baseline. Reading a
    # surface twice and comparing is the only thing that converts `unknown`
    # into a number.
    "c": ("posting", "messaging"),
    # ONE LOAD. Added after stages b and c returned 73 controls TWICE with zero
    # popup triggers -- agreement that could not be interpreted, because this
    # surface had no control. This stage runs the pill-row control on it.
    "d": ("messaging",),
    # ONE LOAD, the surface the widening was for.
    "e": ("interests",),
    # THE CONTROL PAIR for stage e. Two siblings on the same alternation,
    # one of them PROVEN served.
    "f": ("skills", "education"),
}

URL_OF: dict[str, str] = {
    "feed": FEED_URL,
    "profile": PROFILE_URL,
    "interests": INTERESTS_URL,
    "skills": SKILLS_URL,
    "education": EDUCATION_URL,
    "messaging": MESSAGING_URL,
    "posting": JOB_POSTING_URL,
}


def _shape_of(landed: str, requested: str) -> str:
    """WHAT HAPPENED TO AN ADDRESS, never the address it became.

    Copied from ``scripts/_probe_free_reads_shapes.py``. It exists because the
    first run of an ancestor of that file printed the operator's own slug.
    """
    want = urlsplit(str(requested or ""))
    got = urlsplit(str(landed or ""))
    if got.netloc != want.netloc:
        return "OFF-HOST"
    if got.path.rstrip("/") == want.path.rstrip("/"):
        return "same path" + (", query added" if got.query and not want.query else "")
    if "/login" in got.path or "/checkpoint" in got.path:
        return "REDIRECTED TO AN AUTH WALL"
    return "REDIRECTED, path changed, depth %d -> %d" % (
        len([p for p in want.path.split("/") if p]),
        len([p for p in got.path.split("/") if p]),
    )


def _settle_line(surface: str, controls_read: int) -> str:
    """The settle verdict for one reading, in the shipped instrument's terms."""
    expected = SETTLED_CONTROLS.get(surface)
    if expected is None:
        return (
            "    settle:  UNKNOWN -- no baseline exists for this surface, so "
            "this reading has\n             nothing to be compared against. "
            "That is the ABSENCE of a check,\n             not a check "
            "passing. Run the other stage and compare the two."
        )
    floor = int(expected * SETTLE_FLOOR)
    verdict = "consistent" if controls_read >= floor else "LOOKS_HALF_RENDERED"
    return (
        "    settle:  %s -- expected about %d, floor %d, read %d"
        % (verdict, expected, floor, controls_read)
    )


def _count_needle(haystack: str, needle: str) -> int:
    """Case-insensitive occurrence count. No text leaves this function."""
    return haystack.lower().count(needle.lower())


async def _report_census(page: object, surface: str) -> int:
    """Print the control census and the settle verdict. Returns controls_read."""
    census = await dom.read_surface_census(page)
    read = int(census.get("controls_read") or 0)
    counts = census.get("counts") or {}
    print("    census:  controls_read=%d truncated=%s"
          % (read, bool(census.get("truncated"))))
    print("             " + "  ".join(
        "%s=%d" % (key, int(counts.get(key) or 0)) for key in CENSUS_COUNT_KEYS
    ))
    print(_settle_line(surface, read))

    # THE aria-expanded TALLY, over the SHAPED records. A collapsed disclosure
    # is the shape both the overflow menu and the job panels wear, so this
    # number is the one that says how much of each page is behind a press.
    controls = census.get("controls") or []
    expanded: dict[str, int] = {}
    for row in controls:
        key = str(row.get("aria_expanded"))
        expanded[key] = expanded.get(key, 0) + 1
    print("    aria-expanded over the %d shaped controls: %s"
          % (len(controls), "  ".join(
              "%s=%d" % (k, v) for k, v in sorted(expanded.items()))))
    return read


async def _report_structure(page: object) -> None:
    """Structural counts. Roles and ARIA attributes only -- never a name."""
    print("    structure:")
    for selector in STRUCTURAL_SELECTORS:
        try:
            found = await page.locator(selector).count()
        except Exception as exc:  # noqa: BLE001
            print("      %-24s UNREADABLE %s" % (selector, type(exc).__name__))
            continue
        print("      %-24s %d" % (selector, found))


async def _report_needles(
    page: object,
    labelled: tuple[tuple[str, str], ...],
) -> None:
    """Count each needle in the VISIBLE text and in the RAW html, separately.

    THE PAIR IS THE POINT. A needle present in html and absent from main text
    is drawn into the DOM and not onto the screen -- collapsed, or carried in a
    payload. A needle in neither is not on this page at all. One number cannot
    tell those apart, and this probe exists because that distinction is the
    whole of what `PANEL-NOT-OBSERVED` is asking.
    """
    main_text = await dom.read_main_text(page)
    try:
        html = str(await page.content() or "")
    except Exception as exc:  # noqa: BLE001
        html = ""
        print("    html UNREADABLE: %s" % type(exc).__name__)
    print("    main text: %d chars      html: %d chars" % (len(main_text), len(html)))
    print("    needle                          in main   in html   note")
    for needle, note in labelled:
        print("      %-30s %7d  %8d   %s"
              % (needle, _count_needle(main_text, needle),
                 _count_needle(html, needle), note))


async def _report_href_kinds(page: object) -> None:
    """Tally the census's SHAPED hrefs by entity kind. Counts, never names.

    THIS IS THE PRECONDITION ANSWER. Every record's `href_shape` has been
    through `shape.census_shape`, which since 2026-09-04 reduces a group, a
    newsletter and a school to a placeholder exactly as it already did a
    member and a company. So a tally over those placeholders says HOW MANY of
    each kind this account carries without naming one of them.
    """
    census = await dom.read_surface_census(page)
    kinds = {
        "/in/<member>": 0,
        "/company/<company>": 0,
        "/groups/<group>": 0,
        "/newsletters/<newsletter>": 0,
        "/school/<school>": 0,
    }
    other = 0
    for row in census.get("controls") or []:
        hs = str(row.get("href_shape") or "")
        for marker in kinds:
            if marker in hs:
                kinds[marker] += 1
                break
        else:
            if hs:
                other += 1
    print("    entity kinds among %d shaped controls:" % len(census.get("controls") or []))
    for marker, n in kinds.items():
        print("      %-28s %d" % (marker, n))
    print("      %-28s %d" % ("(other hrefs)", other))


async def _report_badge(page: object, when: str) -> None:
    """The messaging nav badge, read off whatever page is already loaded."""
    try:
        html = str(await page.content() or "")
    except Exception as exc:  # noqa: BLE001
        print("    badge %s: UNREADABLE %s" % (when, type(exc).__name__))
        return
    verdict = shape.messaging_badge(html)
    # The verdict's own keys, printed as a shape. A badge label can carry a
    # name ("<person>, 2 new notifications"), so only the numeric and boolean
    # fields are printed and the label itself never is.
    printable = {
        key: value for key, value in sorted(verdict.items())
        if isinstance(value, (int, float, bool)) or value is None
    }
    print("    badge %s: %s" % (when, printable))


async def _read_surface(page: object, surface: str) -> None:
    """One address, fully reported. Wrapped by the caller."""
    url = URL_OF[surface]
    print("\n--- %s" % surface.upper())
    landed = await BROWSER.goto(page, url)
    print("    relation: %s" % _shape_of(landed, url))
    print("    nav settle: %s" % BROWSER.last_settle)
    if "/login" in str(landed) or "/checkpoint" in str(landed):
        print("    AUTH WALL on this address. Nothing else measured.")
        return
    await _report_census(page, surface)
    await _report_structure(page)
    # THE SIZE OF WHAT RENDERED, ON EVERY SURFACE WITHOUT EXCEPTION. A zero
    # needle count beside "main carried 17806 chars" and one beside "main was
    # empty" are different findings, and an instrument that prints only the
    # first is not worth the load it cost.
    print("    main text: %d chars" % len(await dom.read_main_text(page)))
    if surface == "posting":
        await _report_needles(
            page,
            POSTING_CONTROL_NEEDLES_LABELLED + POSTING_TARGET_NEEDLES,
        )
    elif surface == "feed":
        await _report_needles(
            page,
            tuple((needle, "hashtag") for needle in HASHTAG_NEEDLES),
        )
    elif surface == "profile":
        await _report_needles(page, PROFILE_NEEDLES)
    elif surface == "messaging":
        await _report_needles(page, MESSAGING_NEEDLES)
    elif surface == "interests":
        await _report_needles(page, PROFILE_NEEDLES)
        await _report_href_kinds(page)


async def main() -> None:
    stage = (sys.argv[1] if len(sys.argv) > 1 else "").strip().lower()
    if stage not in STAGES:
        print("usage: python scripts/_probe_unmeasured_surfaces_live.py a|b|c")
        print("  a  feed then profile   -- costs nothing, answers the most")
        print("  b  posting then messaging")
        print("  c  posting then messaging -- the second reading of each")
        print("  d  messaging alone      -- the pill-row control")
        return

    surfaces = STAGES[stage]
    print("=== STAGE %s: %s" % (stage, " then ".join(surfaces)))
    print("    two page loads, %.1fs apart, nothing pressed" % PAUSE_S)

    async with BROWSER.session() as page:
        for index, surface in enumerate(surfaces):
            if index:
                await asyncio.sleep(PAUSE_S)
            try:
                await _read_surface(page, surface)
                # The badge is read off the feed, and WHICH reading it is
                # depends on the stage: before the inbox load in ``a``, after
                # it in ``b``. A drop between them is the auto-open spending
                # unread state.
                if surface == "feed":
                    await _report_badge(page, "BEFORE any inbox load")
            except Exception as exc:  # noqa: BLE001
                print("    FAILED: %s: %s" % (type(exc).__name__, exc))

        print("\n=== READING")
        print("    A ZERO IS NOT A FINDING UNTIL THE SETTLE LINE IS READ FIRST.")
        print("    On the posting, the three CONTROL needles must read 1/1/0.")
        print("    If they do not, every target count below them is suspect.")
        print("    On messaging, [aria-haspopup] against [role=menuitem] is the")
        print("    answer: triggers with zero items means the menu is built on")
        print("    demand and a capture needs a press it has not been given.")

    await BROWSER.stop()


# GUARDED: importing a script must not DO anything.
if __name__ == "__main__":
    asyncio.run(main())
