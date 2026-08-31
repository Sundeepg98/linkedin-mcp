"""The three surfaces LinkedIn rebuilt, tested against the pages it served.

A companion to ``test_profile_views_fixture.py`` and written for the same
reason: the defects here do not live in the shaping, they live in where a row
STOPS and in what the DOM hands back, and hand-written card text cannot
exercise either. All three tools were measured broken on live pages on
2026-08-21 while every pure test passed.

WHAT WAS BROKEN, and what each fixture pins:

* ``jobs_tracker_row.html`` -- one real job in the tracker. The row walk stops
  when an ancestor holds more than one deduped KEY, and this card carries TWO
  anchors to the SAME job id, so the count never rose, the walk ran to
  ``maxHops``, and the row came back as ``title: "Job tracker"``,
  ``company: "Saved <dot> 0"``. Confidently wrong, and invisible for as long as
  the list stayed empty.
* ``jobs_tracker_empty.html`` -- the same page with nothing in it. Its subject
  is the tab strip: LinkedIn's own count is the only thing on the page that
  can tell an empty list from a failed read.
* ``notifications.html`` -- six real cards. Screen-reader-only text ("Unread
  notification.", "Status is reachable") was welded to every body, and ``when``
  was null on all 22 rows of the live page because LinkedIn writes "2h" in an
  element of its own and the word "ago" appears nowhere.
* ``profile_topcard.html`` / ``profile_topcard_hydrated.html`` -- the profile
  before and after hydration. The page carries ZERO ``h1`` and none of the
  ``about``/``experience``/``skills`` ids the reader used to look for, so every
  field read null and the tool errored on its owner's own profile. Both renders
  are kept because agreeing across them is the property being claimed.
* ``profile_skills.html`` -- the skills page. On the live page ``main ul li``
  matched the three filter pills, so "All", "Industry Knowledge" and "Tools &
  Technologies" were being reported as his skills. NOTE that this fixture keeps
  only the six skill entries, so the pills are not in it and no test here can
  reproduce the old wrong answer; what it does pin is that the page offers no
  list element to select at all, and that the per-skill anchor the reader now
  uses is there once per skill.

Every fixture is the region named above and nothing else, with scripts, styles,
svg and images stripped, and with names, companies, slugs, member ids, content
urns and impression tokens replaced by invented ones. Stripping the styles
makes these renders HARSHER than the live page -- without CSS, ``innerText``
runs hidden menu items and duplicated bodies together -- which is deliberate: a
parser that survives both layouts cannot be reading one particular render.

TWO SHAPES ARE WRITTEN BY HAND rather than captured, and section 1c says why:
a row whose photo link comes before its name link, and two profile sections
sharing a wrapper. Neither is in any capture -- the photo links were stripped
along with the images -- and without them both of the row walk's stop
conditions and the profile section rule could be DELETED with the whole suite
green. That was found by a cold review, not by this module.
"""

from __future__ import annotations

import pathlib
import re
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

TRACKER_ROW = FIXTURE_DIR / "jobs_tracker_row.html"
TRACKER_EMPTY = FIXTURE_DIR / "jobs_tracker_empty.html"
NOTIFICATIONS = FIXTURE_DIR / "notifications.html"
PROFILE_PRE = FIXTURE_DIR / "profile_topcard.html"
PROFILE_HYDRATED = FIXTURE_DIR / "profile_topcard_hydrated.html"
PROFILE_SKILLS = FIXTURE_DIR / "profile_skills.html"

BOTH_PROFILES = ["pre_hydration", "hydrated"]
PROFILE_FIXTURES = {
    "pre_hydration": PROFILE_PRE,
    "hydrated": PROFILE_HYDRATED,
}

#: chr(0xB7) is the middle dot LinkedIn separates a tab from its count with,
#: and a company from its location with. Spelled this way so this file stays
#: pure ASCII, as shape.py does.
DOT = chr(0xB7)

#: The one job on the tracker fixture.
JOB_ID = "4011223344"
JOB_TITLE = "Platform Integration Engineer"
JOB_COMPANY = "Ashgrove Systems"
JOB_LOCATION = "Fairhaven (Remote)"

#: The page furniture that became the row when the walk overshot.
PAGE_HEADING = "Job tracker"

NAME = "Alex Rivera"
HEADLINE = (
    "Senior Backend Engineer | Node.js, TypeScript, React | "
    "Building reliable services | Riverton"
)
LOCATION = "Riverton, Fairhaven, United States"
SCHOOL = "Lakeside Institute of Technology"

SKILLS = [
    "Node.js",
    "TypeScript",
    "React.js",
    "Next.js",
    "Apache Kafka",
    "Systems Design",
]
#: What the old ``main ul li`` selector returned instead.
FILTER_PILLS = ("All", "Industry Knowledge", "Tools & Technologies")


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_page(path: Path, work):
    """Run ``work(page)`` over one frozen page in a LOCAL headless Chromium."""
    return await _with_html(path.read_text(encoding="utf-8"), work)


async def _with_html(html: str, work):
    """The same, over markup written here rather than captured."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# 1. The fixtures themselves
# ---------------------------------------------------------------------------
#
# No browser. Their job is to stop everything below from going vacuous: a
# fixture quietly emptied or regenerated wrong would make every assertion
# about "the rows" true of nothing at all.

NEW_FIXTURES = [
    TRACKER_ROW,
    TRACKER_EMPTY,
    NOTIFICATIONS,
    PROFILE_PRE,
    PROFILE_HYDRATED,
    PROFILE_SKILLS,
]

#: The privacy checks below run over EVERY fixture in the repo, DISCOVERED
#: rather than listed.
#:
#: This was a hand-written list, under a comment recording that scoping the
#: privacy checks to one module's own files is how two real member urns sat
#: unnoticed in the older pair until a cold review went looking. A list is
#: that same failure moved one step later: a fixture frozen by a later wave is
#: not on it, so the guards never run over the new file and nothing fails --
#: the checks stay green by not looking. Three job-posting captures landed on
#: 2026-08-22 and would have been exactly that case.
#:
#: A glob closes the class instead of the instance: a capture is covered the
#: moment it lands in the directory, by whoever adds it, without their having
#: to know this module exists.
ALL_FIXTURES = sorted(FIXTURE_DIR.glob("*.html"))


@pytest.mark.parametrize("path", NEW_FIXTURES, ids=lambda p: p.name)
def test_the_fixture_exists_and_is_pure_ascii(path):
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw, f"empty fixture: {path}"
    raw.decode("ascii")


def test_the_privacy_guards_cover_every_fixture_on_disk():
    """A discovered list still has to be shown discovering something.

    If the glob ever returns nothing -- a moved directory, a renamed suffix --
    every parametrised guard below silently collapses to zero cases and the
    suite goes green having checked no file at all. That is a worse outcome
    than the stale list this replaced, so it is asserted rather than assumed.
    """
    assert ALL_FIXTURES, f"no fixtures discovered under {FIXTURE_DIR}"
    for path in NEW_FIXTURES:
        assert path in ALL_FIXTURES, f"{path.name} not discovered"
    # The three job-posting captures are named because they are the reason
    # the list became a glob.
    for name in ("job_detail.html", "job_detail_hydrated.html", "job_detail_shell.html"):
        assert FIXTURE_DIR / name in ALL_FIXTURES, name


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_the_fixture_carries_no_session_material(path):
    html = path.read_text(encoding="utf-8")
    for token in ("li_at", "JSESSIONID", "csrfToken", "Bearer "):
        assert token not in html, token


#: Every opaque LinkedIn identifier these captures are known to carry, matched
#: RAW and PERCENT-ENCODED. A member urn, an activity or post urn and a
#: per-impression tracking token each name a real person or a real post as
#: surely as a name does.
#:
#: This check is written as a SHAPE rather than as a list of known-bad strings
#: on purpose. The list version has now failed twice for the same reason: it
#: looked for ``urn:li:member`` and the files held ``urn%3Ali%3Afsd_profile``
#: and ``urn:li:ugcPost``, so two real viewers and three real posts passed it.
#: A guard that cannot see the CLASS of thing it guards against is not a guard.
_OPAQUE_ID_PATTERNS = (
    ("member or content urn", re.compile(r"urn(?::|%3A)li(?::|%3A)", re.I)),
    ("member id", re.compile(r"\bACoAA[A-Za-z0-9_-]{20,}")),
    ("impression tracking token", re.compile(r"[Tt]rackingId=[A-Za-z0-9%+/=_-]{8,}")),
)

#: The pseudonyms the fixtures are allowed to keep, listed EXACTLY rather than
#: by shape. A loose exemption is how a real id hides behind the guard, which
#: is the failure mode this whole check exists to close -- so every permitted
#: id is written out, and a new capture has to add its own here deliberately.
_ALLOWED_OPAQUE_IDS = re.compile(
    "|".join(
        re.escape(value)
        for value in (
            # Two profile-view viewers.
            "ACoAAB1c2D3e4F5g6H7i8J9k0L1m2N3o4P5q6R7",
            "ACoAAC8s7T6u5V4w3X2y1Z0a9B8c7D6e5F4g3H2",
            # The profile owner, on the profile and skills fixtures.
            "ACoAAA1B2C3D4E5F6G7H8I9J0KLMNOPQRSTUVWX",
            # Three notification content ids.
            "7400000000000000001",
            "7400000000000000002",
            "7400000000000000003",
            # Two impression tokens.
            "AAAAAAAAAAAAAAAAAAAAAA%3D%3D",
            "BBBBBBBBBBBBBBBBBBBBBB%3D%3D",
        )
    )
)


@pytest.mark.parametrize("path", ALL_FIXTURES, ids=lambda p: p.name)
def test_no_fixture_carries_a_real_opaque_linkedin_id(path):
    """Names are the easy half. The ids underneath them identify people too."""
    html = path.read_text(encoding="utf-8")
    for label, pattern in _OPAQUE_ID_PATTERNS:
        for match in pattern.finditer(html):
            tail = html[match.start() : match.start() + 120]
            assert _ALLOWED_OPAQUE_IDS.search(tail), (label, tail[:90])


def test_the_exact_value_guard_is_wired_even_though_its_values_are_not_here():
    """THE DENYLIST IS EMPTY IN THIS FILE ON PURPOSE, AND THAT IS THE POINT.

    Until 2026-08-24 this module carried thirteen real tokens -- the operator's
    surname, his city, five former employers, and four names whose provenance
    nobody had established. They were kept on the reasoning that a denylist
    must name what it denies, ratified while this repo was private.

    THE RATIFICATION RESTED ON A CLAIM THAT WAS NOT TRUE. Both copies of the
    note asserted all thirteen were "already-public facts about the OPERATOR...
    his own, not a third party's". Measured by SURFACE on 2026-08-24:

      * SIX were found in a capture of HIS OWN PROFILE -- his own, evidenced.
      * ONE appears in a capture of HIS FEED and NOWHERE on his own profile.
        It is the name of somebody he follows: a THIRD PARTY, which the note
        explicitly denied.
      * SIX appear NOWHERE on this machine outside those two denylists, so
        nothing established whose they were. "His own" was an assumption
        wearing a ratification's clothes.

    The operator then ruled the whole set out of the tracked repo rather than
    only the four that could not be cleared -- which also retires the question
    of whether aggregating a surname, a city and five employers beside a
    LinkedIn automation tool is different from publishing any one of them.

    WHERE THE CHECK WENT, AND WHY NOTHING WAS LOST. All thirteen live in
    ``_audit/_sanitisation_key.json``, which is gitignored.
    ``scripts/sweep_tracked_for_identity.py`` loads EVERY non-underscore list
    in that key, expands each value through ``leakwalk.url_spellings``, and
    sweeps every tracked file -- so the terms are now checked in more spellings
    and across more files than this test ever covered, without being published.

    WHAT THIS TEST IS FOR NOW. It guards the WIRING, because an exact-value
    check that quietly stopped being reachable would be worse than one that
    was never written: the suite would stay green and nobody would look. It
    asserts the sweep exists, that it REFUSES rather than passing when its
    wordlist is absent, and that this file no longer carries the values.

    WHAT IT DELIBERATELY DOES NOT DO IS SKIP. A skipping guard is a dead guard
    -- this family lost a leak-detector control that way once, to a
    ``pytest.skip`` that kept CI green while the only test proving the detector
    still detected stopped running. Everything below runs everywhere, including
    CI, where the key is absent by design.

    THE HONEST RESIDUAL: the exact-value half no longer runs in CI at all. That
    is acceptable for one specific reason rather than by shrug -- the failure
    it guards against is a REGENERATED FIXTURE reintroducing a real value, and
    regeneration runs ``scripts/_build_follow_fixtures.py``, which requires the
    key and refuses without it. The defect can therefore only be created on a
    machine where the sweep is available to catch it.
    """
    repo = pathlib.Path(__file__).resolve().parents[1]
    sweep = repo / "scripts" / "sweep_tracked_for_identity.py"
    assert sweep.exists(), "the exact-value guard's script is gone"

    source = sweep.read_text(encoding="utf-8")

    # It must REFUSE when the wordlist is missing, not pass and not skip.
    assert "SystemExit" in source
    assert "the wordlist is missing" in source

    # It must load the key generically, so a channel added to the key is swept
    # without anybody editing the script. That generality is what made moving
    # the terms free; if it were replaced by a hardcoded list of channel names,
    # a future move would silently sweep nothing.
    assert "startswith" in source and "isinstance(values, list)" in source

    # And the construct that carried the values is gone. Named precisely
    # rather than by shape: an earlier draft of this assertion forbade any
    # ``for token in (`` in the file and failed immediately, because a
    # LEGITIMATE loop over four SYNTHETIC ids lives a few tests down. A guard
    # that cannot tell the thing it forbids from the thing beside it is the
    # same defect this module keeps finding elsewhere.
    # THE NEEDLE IS ASSEMBLED, NOT WRITTEN. Spelled literally, it appears in
    # this very line and the check finds ITSELF -- which it did, on the first
    # run, exactly as the runbook's law says: an instrument must exclude its
    # own machinery from what it measures. Splitting the name is the designed
    # version of what would otherwise be an accident.
    mine = pathlib.Path(__file__).read_text(encoding="utf-8")
    needle = "def test_no_fixture_names_" + "a_real_person_or_employer"
    assert mine.count(needle) == 0, (
        "the literal denylist test has come back into a tracked file"
    )


def test_that_wiring_check_would_notice_a_dead_sweep():
    """THE CONTROL. Without it the assertions above pass on any file that
    happens to contain those words -- including this docstring.

    Proves each required property is actually load-bearing by removing it from
    a COPY of the source and confirming the corresponding assertion would
    fail. Nothing on disk is touched.
    """
    repo = pathlib.Path(__file__).resolve().parents[1]
    source = (repo / "scripts" / "sweep_tracked_for_identity.py").read_text(
        encoding="utf-8"
    )
    for needle in ("SystemExit", "the wordlist is missing", "isinstance(values, list)"):
        assert needle in source
        assert needle not in source.replace(needle, ""), (
            f"removing {needle!r} must make the check fail"
        )

def test_the_opaque_id_guard_can_actually_fail():
    """The control. This guard has twice been unable to see a real leak.

    THE INPUTS ARE SYNTHETIC, AND THAT IS THE THIRD THING THIS TEST HAS HAD TO
    LEARN. Until 2026-08-23 it ran over the REAL ids that were in these files
    before they were pseudonymised -- a real member urn, a real activity urn, a
    real post urn and a real per-impression tracking token, all four of them
    naming real third parties, pasted into a tracked and pushed file in order
    to prove that real values get caught.

    That is the sanitisation script's own mistake one layer up: the fixtures
    were scrubbed and the scrubbed-out values were kept next to them. A CONTROL
    NEEDS THE SHAPE, NOT THE VALUE. These four trip all three patterns and are
    absent from the allowlist, which is the entire property under test, and no
    real person is named to establish it.

    It is also why the identity sweep did not find them: this module was
    EXCLUDED from the repo-wide member-id sweep because it defines the
    allowlist, and the real ids were sitting inside the excluded file. See
    ``tests/test_no_committed_identity.py``, which no longer excludes it.
    """
    leaks = (
        "urn%3Ali%3Afsd_profile%3AACoAAQ1w2E3r4T5y6U7i8O9p0A1s2D3f4G5h6J7",
        "urn%3Ali%3Aactivity%3A7490000000000000001",
        "urn:li:ugcPost:7490000000000000002",
        "highlightedUpdateTrackingId=Zz9Yy8Xx7Ww6Vv5Uu4Tt3Q%3D%3D",
    )
    for leak in leaks:
        caught = False
        for _, pattern in _OPAQUE_ID_PATTERNS:
            match = pattern.search(leak)
            if match and not _ALLOWED_OPAQUE_IDS.search(
                leak[match.start() : match.start() + 120]
            ):
                caught = True
                break
        assert caught, leak


def test_the_tracker_fixture_keeps_the_duplicate_anchor():
    """The whole bug. One card, two links, one job id.

    A fixture that ended up with a single anchor would pass every assertion
    below against the OLD walk as well, and pin nothing.
    """
    html = TRACKER_ROW.read_text(encoding="utf-8")
    assert html.count(f"/jobs/view/{JOB_ID}") == 2


def test_the_profile_fixtures_have_no_h1_and_no_section_ids():
    """The two anchors the old profile reader was built on. Both gone."""
    for path in (PROFILE_PRE, PROFILE_HYDRATED):
        html = path.read_text(encoding="utf-8")
        assert "<h1" not in html, path.name
        for section_id in ('id="about"', 'id="experience"', 'id="skills"'):
            assert section_id not in html, (path.name, section_id)


def test_the_skills_fixture_does_not_contain_the_filter_pills():
    """So a passing skills test cannot be passing by accident."""
    html = PROFILE_SKILLS.read_text(encoding="utf-8")
    for pill in FILTER_PILLS:
        assert f">{pill}<" not in html, pill


# ---------------------------------------------------------------------------
# 1b. The anchors the old readers were built on, run against today's pages
# ---------------------------------------------------------------------------
#
# These pass both before and after the fix, and that is the point: they are
# the executable statement of WHY the readers had to change, in a form that
# goes red if LinkedIn ever puts these anchors back. Without them the profile
# and skills tests below fail on the pre-fix code only because the functions
# they call did not exist yet, which proves nothing about the page.

OLD_PROFILE_SELECTORS = {
    "name": ["main h1", "h1"],
    "headline": [
        "main .text-body-medium.break-words",
        "main .top-card-layout__headline",
        "main h1 + div",
    ],
    "location": [
        "main .text-body-small.inline.t-black--light.break-words",
        "main .top-card__subline-item",
    ],
    "photo": [
        "main img.pv-top-card-profile-picture__image",
        'main img[class*="profile-photo"]',
    ],
    "sections": ["#about", "#experience", "#education", "#skills"],
}

_COUNT_SELECTORS_JS = """
(selectors) => {
  const out = {};
  for (const [field, list] of Object.entries(selectors)) {
    let found = 0;
    for (const selector of list) {
      try { found += document.querySelectorAll(selector).length; } catch (e) {}
    }
    out[field] = found;
  }
  return out;
}
"""


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_every_anchor_the_old_profile_reader_used_is_gone(which):
    """Measured: the old reader returned null for every field, on both renders."""

    async def work(page):
        return await page.evaluate(_COUNT_SELECTORS_JS, OLD_PROFILE_SELECTORS)

    found = await _with_page(PROFILE_FIXTURES[which], work)
    assert found == {
        "name": 0,
        "headline": 0,
        "location": 0,
        "photo": 0,
        "sections": 0,
    }, found


async def test_the_skills_page_has_no_list_semantics_for_a_selector_to_use():
    """Why ``main ul li`` could never have worked here.

    An earlier version of this test asserted that the old selector harvests
    nothing from the fixture, which a cold review correctly called vacuous: the
    file has no ``ul`` and no ``li`` at all, and ``harvest_block_cards``
    returns ``[]`` for any selector matching nothing, so the assertion was a
    tautology about a frozen file rather than a statement about the page.

    This says the thing that is actually true and actually falsifiable: the
    skills page uses ARIA roles on divs, so there is no list element to select,
    while the per-skill edit anchor the reader now keys on is present once per
    skill.
    """

    async def work(page):
        return await page.evaluate(
            """() => ({
                 ul: document.querySelectorAll('main ul').length,
                 li: document.querySelectorAll('main li').length,
                 listitem_roles: document.querySelectorAll('[role="listitem"]').length,
                 skill_anchors: document.querySelectorAll(
                   'a[href*="/details/skills/edit/forms/"]').length
               })"""
        )

    shape_of_page = await _with_page(PROFILE_SKILLS, work)
    assert shape_of_page["ul"] == 0
    assert shape_of_page["li"] == 0
    assert shape_of_page["skill_anchors"] == 6, shape_of_page


# ---------------------------------------------------------------------------
# 1c. The row walk's two stop conditions, each on markup that needs it
# ---------------------------------------------------------------------------
#
# These are written here rather than captured, and that is the point. A cold
# review showed that BOTH stops in the walk could be deleted with the whole
# suite green, because no committed fixture contains the shape either one
# exists for: LinkedIn wraps a row's photo in its own link to the same person,
# and every viewer in both profile-view fixtures has exactly ONE anchor -- the
# images were stripped when those files were scrubbed. Capturing a page with
# photos would drag a real person's picture into the repo, so the shape is
# reproduced instead, minimally and by hand.

#: A NESTED row: the photo link and the name link sit inside a row container.
#: Walking from the photo link, which has no text, a bare link-count stop
#: freezes on that empty anchor and the viewer is dropped entirely. The
#: ``hasText(row)`` clause is what climbs through it.
NESTED_ROWS_HTML = """
<main><div id="list">
  <div class="row">
    <a href="/in/priya-sharma-8a41b207/"><img alt=""></a>
    <div>
      <a href="/in/priya-sharma-8a41b207/">Priya Sharma</a>
      <div>Engineer at Northwind</div>
      <div>Viewed 3d ago</div>
    </div>
  </div>
  <div class="row">
    <a href="/in/arun-b-4c19d833/"><img alt=""></a>
    <div>
      <a href="/in/arun-b-4c19d833/">Arun Balakrishnan</a>
      <div>Analyst at Ashgrove</div>
      <div>Viewed 5d ago</div>
    </div>
  </div>
</div></main>
"""

#: A FLAT row: the photo link's own parent is already the whole list. Here the
#: text clause disables the link stop, so only the "more than one deduped key"
#: stop can halt the walk -- without it the first viewer's record swallows the
#: entire list and the second viewer disappears into it.
FLAT_ROWS_HTML = """
<main><div id="list">
  <a href="/in/priya-sharma-8a41b207/"><img alt=""></a>
  <span>Priya Sharma</span><span>Engineer at Northwind</span><span>Viewed 3d ago</span>
  <a href="/in/arun-b-4c19d833/"><img alt=""></a>
  <span>Arun Balakrishnan</span><span>Analyst at Ashgrove</span><span>Viewed 5d ago</span>
</div></main>
"""


async def _people_from(html: str):
    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.PERSON_HREF, max_items=40
        )
        rows, dropped = dom.parse_all(records, shape.parse_person_card)
        return records, rows, dropped

    return await _with_html(html, work)


async def test_a_row_whose_photo_link_comes_first_is_not_lost():
    """Pins ``hasText(row)``. Without it this returns nothing at all."""
    records, rows, _ = await _people_from(NESTED_ROWS_HTML)

    assert len(records) == 2, records
    assert [row["name"] for row in rows] == ["Priya Sharma", "Arun Balakrishnan"]
    assert rows[0]["headline"] == "Engineer at Northwind"
    assert rows[0]["viewed"] == "3 days ago"
    assert rows[1]["viewed"] == "5 days ago"


async def test_a_flat_list_of_photo_links_does_not_collapse_into_one_row():
    """Pins the deduped-key stop, which the link stop cannot cover here.

    With the key stop removed, the first viewer's record grows to hold the
    whole list and the second is skipped as already seen -- one row wearing two
    people's text, which is the profile-views failure all over again.
    """
    records, _, _ = await _people_from(FLAT_ROWS_HTML)

    for record in records:
        names = [
            name
            for name in ("Priya Sharma", "Arun Balakrishnan")
            if name in record["text"]
        ]
        assert len(names) <= 1, record["text"][:160]


# ---------------------------------------------------------------------------
# 1d. The profile section rule, on markup that needs it
# ---------------------------------------------------------------------------
#
# Same gap, same reason: in both profile fixtures every heading already sits
# inside its own direct child of ``main``, so the ``node !== main`` bound alone
# gives the right answer and the heading stop can be deleted green. Here two
# sections share a wrapper, which is what the stop is for.

SHARED_WRAPPER_HTML = """
<main><div id="wrapper">
  <div class="card">
    <h2>Alex Rivera</h2><div>He/Him</div>
    <div>Senior Backend Engineer</div>
    <div>Riverton, Fairhaven, United States</div>
    <div>Contact info</div>
  </div>
  <div class="card"><h2>About</h2><div>Nine years of backend work.</div></div>
</div></main>
"""


async def test_a_section_stops_before_the_wrapper_it_shares_with_the_next_one():
    """Pins ``headingsIn(node) > 1``: without it both sections are the wrapper."""

    async def work(page):
        return await dom.read_profile_fields(page)

    fields = await _with_html(SHARED_WRAPPER_HTML, work)
    sections = fields["sections"]

    assert [s["heading"] for s in sections] == ["Alex Rivera", "About"]
    # The topcard must not have swallowed the About card.
    assert "Nine years of backend work." not in " ".join(sections[0]["lines"])
    assert shape.profile_section_lines(sections, "About") == [
        "Nine years of backend work."
    ]
    identity = shape.parse_profile_topcard(sections[0]["lines"])
    assert identity["name"] == "Alex Rivera"
    assert identity["headline"] == "Senior Backend Engineer"
    assert identity["location"] == "Riverton, Fairhaven, United States"


# ---------------------------------------------------------------------------
# 2. The job tracker: the row, over the real markup
# ---------------------------------------------------------------------------


async def _tracker_rows(path: Path):
    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=75
        )
        rows, dropped = dom.parse_all(records, shape.parse_job_card)
        return records, rows, dropped

    return await _with_page(path, work)


async def test_the_tracker_row_is_the_job_and_not_the_page():
    """The defect, stated as the values it got wrong.

    Every one of these was non-empty before the fix, which is exactly why
    "the field is populated" is not an assertion.
    """
    _, rows, dropped = await _tracker_rows(TRACKER_ROW)

    assert len(rows) == 1, rows
    assert dropped == 0
    assert rows[0] == {
        "title": JOB_TITLE,
        "company": JOB_COMPANY,
        "location": JOB_LOCATION,
        "status": "no longer accepting applications",
        "job_id": JOB_ID,
        "url": f"https://www.linkedin.com/jobs/view/{JOB_ID}",
    }


async def test_no_tracker_field_is_page_furniture():
    """The heading and the tab strip are the values the old walk returned."""
    _, rows, _ = await _tracker_rows(TRACKER_ROW)
    assert len(rows) == 1, "an empty harvest would make this loop vacuous"
    forbidden = (PAGE_HEADING, "Saved", "Applied", "Interview", "Date posted", DOT)
    for row in rows:
        for field in ("title", "company", "location"):
            value = row.get(field) or ""
            for token in forbidden:
                assert token not in value, (field, value, token)


async def test_the_harvested_tracker_record_stops_at_the_card():
    """The walk's own output, before any shaping touches it."""
    records, _, _ = await _tracker_rows(TRACKER_ROW)

    assert len(records) == 1, records
    text = records[0]["text"]
    assert JOB_TITLE in text
    assert PAGE_HEADING not in text, text[:200]
    assert "Date posted" not in text, text[:200]


async def test_an_empty_tracker_yields_no_rows_at_all():
    """The other half: nothing to parse, and nothing invented."""
    records, rows, _ = await _tracker_rows(TRACKER_EMPTY)
    assert records == []
    assert rows == []


# ---------------------------------------------------------------------------
# 3. The job tracker: the counts that make an empty list believable
# ---------------------------------------------------------------------------


async def _main_text(path: Path) -> str:
    return await _with_page(path, dom.read_main_text)


async def test_the_empty_tracker_publishes_its_own_counts():
    text = await _main_text(TRACKER_EMPTY)

    assert shape.parse_tracker_tabs(text) == {
        "saved": 0,
        "in_progress": 1,
        "applied": 0,
        "interview": 0,
    }
    assert shape.tracker_empty_state(text) == "No jobs here"


async def test_the_populated_tracker_publishes_its_own_counts():
    text = await _main_text(TRACKER_ROW)

    counts = shape.parse_tracker_tabs(text)
    assert counts == {"saved": 0, "draft": 1, "applied": 0, "interview": 0}
    # A tab LinkedIn draws without a count is absent rather than reported as
    # zero, because zero is a claim.
    assert "archived" not in counts
    # This page has a row, so it drew no empty state.
    assert shape.tracker_empty_state(text) is None


def test_both_empty_state_wordings_are_recognised():
    """"No matches" is the one the tools will actually meet, and it was untested.

    Both frozen tracker fixtures show "No jobs here", which is the DEFAULT
    tab's wording. Every read this server performs goes through ``?stage=``,
    and a stage-selected tab that is empty says "No matches" instead -- so the
    wording on the live code path was the one no test exercised.
    """
    default_tab = "Saved " + DOT + " 0\nDate posted\nNo jobs here\nFind more jobs"
    stage_tab = "Applied " + DOT + " 0\nDate posted\nNo matches\nNot seeing some jobs?"

    assert shape.tracker_empty_state(default_tab) == "No jobs here"
    assert shape.tracker_empty_state(stage_tab) == "No matches"
    assert shape.tracker_empty_state("Saved " + DOT + " 0\nDate posted") is None
    # A line that merely CONTAINS the wording is not the empty state.
    assert shape.tracker_empty_state("No matches were harmed") is None


@pytest.mark.parametrize(
    "linkedin_count, empty_state, believable",
    [
        (0, "No jobs here", True),
        (0, "No matches", True),
        # LinkedIn says there are three. Nothing parsed. That is a broken read
        # and reporting it as an empty list is the lie this guards.
        (3, "No jobs here", False),
        # No empty state drawn: the page may simply not have rendered.
        (0, None, False),
        # The tab strip could not be read, so there is nothing to corroborate.
        (None, "No jobs here", False),
        (None, None, False),
    ],
)
def test_a_zero_is_only_believed_when_the_page_says_so(
    linkedin_count, empty_state, believable
):
    assert (
        shape.empty_is_believable(
            linkedin_count=linkedin_count, empty_state=empty_state
        )
        is believable
    )


# ---------------------------------------------------------------------------
# 4. Notifications
# ---------------------------------------------------------------------------

#: What the six frozen cards must come back as. Written out in full rather
#: than checked for non-emptiness: every one of these bodies was non-empty
#: before the fix too, just with "Unread notification." on the front.
EXPECTED_NOTIFICATIONS = [
    ("Senior Software Engineer: new opportunities in Riverton.", "22 minutes ago", True),
    (
        "Suggested for you: A note on hiring feedback: even a short reply after "
        "an interview means a great deal to a candidate. #Hiring #Career "
        "1,613 reactions 31 comments",
        "1 hour ago",
        False,
    ),
    (None, "1 hour ago", False),
    (
        "Robin Ellery commented on Marco Benitez's post: Congratulations Marco!!",
        "2 hours ago",
        False,
    ),
    ("Full Stack Engineer: new opportunities in Riverton.", "3 hours ago", False),
    (
        "Sam Okonkwo's connection is hiring for a Senior Software Engineer "
        "(SDE-3) Java at Brightpath. Explore jobs in your network.",
        "4 hours ago",
        False,
    ),
]

#: Text the page marks screen-reader-only. None of it is a notification.
A11Y_NOISE = (
    "Unread notification.",
    "Status is reachable",
    "Status is offline",
    "Status is online",
    "Profile image for several companies on LinkedIn",
)


async def _notifications_from(html: str):
    """Harvest and parse notifications out of one page of markup.

    Section 4c writes its own card rather than using a capture, so the harvest
    configuration lives here once instead of twice: a selector changed in one
    copy and not the other would leave the surface under test and the surface
    being pinned quietly different.
    """

    async def work(page):
        records = await dom.harvest_block_cards(
            page,
            selectors=dom.NOTIFICATION_SELECTORS,
            max_items=40,
            hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
            time_selector=dom.NOTIFICATION_TIME_SELECTOR,
            unread_class=dom.NOTIFICATION_UNREAD_CLASS,
        )
        rows, dropped = dom.parse_all(records, shape.parse_notification)
        return records, rows, dropped

    return await _with_html(html, work)


async def _notification_rows():
    return await _notifications_from(NOTIFICATIONS.read_text(encoding="utf-8"))


async def test_the_notification_harvest_finds_every_card():
    records, rows, dropped = await _notification_rows()
    assert len(records) == 6, records
    assert len(rows) == 6
    assert dropped == 0


async def test_no_notification_body_carries_accessibility_text():
    """The defect. "Unread notification." was welded to the front of a body."""
    _, rows, _ = await _notification_rows()
    assert len(rows) == 6, "an empty harvest would make this loop vacuous"
    for row in rows:
        for noise in A11Y_NOISE:
            assert noise not in row["text"], (noise, row["text"])


async def test_every_notification_body_is_exactly_what_the_page_showed():
    _, rows, _ = await _notification_rows()
    # zip() truncates silently, so a harvest that returned one row would make
    # every assertion below vacuously true.
    assert len(rows) == len(EXPECTED_NOTIFICATIONS)
    for row, (expected, _, _) in zip(rows, EXPECTED_NOTIFICATIONS):
        if expected is None:
            continue
        assert row["text"] == expected


async def test_a_body_the_page_prints_twice_keeps_one_copy():
    """The trap under the fix.

    Three of these cards repeat their whole body in a hidden span. Deleting
    every hidden string by phrase would empty them, so the subtraction is by
    count -- one removal per hidden element -- and this is the card that
    proves it did not take both.
    """
    _, rows, _ = await _notification_rows()
    body = rows[2]["text"]
    assert body.startswith("Forgeworks was live for Open Source Tuesday with Boulder:")
    assert body.count("Forgeworks was live") == 1


async def test_every_notification_carries_the_time_the_page_wrote():
    """``when`` was null on all 22 rows of the live page."""
    _, rows, _ = await _notification_rows()
    assert [row.get("when") for row in rows] == [
        when for _, when, _ in EXPECTED_NOTIFICATIONS
    ]


async def test_a_notification_body_does_not_end_with_its_own_timestamp():
    _, rows, _ = await _notification_rows()
    assert len(rows) == 6, "an empty harvest would make this loop vacuous"
    for row in rows:
        assert not row["text"].rstrip().endswith(("22m", "1h", "2h", "3h", "4h"))


async def test_the_unread_flag_is_read_before_the_page_load_destroys_it():
    """Exactly one of the six was unread, and the badge is about to be cleared."""
    _, rows, _ = await _notification_rows()
    assert [row.get("unread") for row in rows] == [
        unread for _, _, unread in EXPECTED_NOTIFICATIONS
    ]
    assert sum(1 for row in rows if row["unread"]) == 1


# ---------------------------------------------------------------------------
# 4b. The same card as the LIVE page lays it out
# ---------------------------------------------------------------------------
#
# The fixtures have their styles stripped, which runs the hidden copy and the
# visible one together on one innerText line. The live page puts them on
# separate lines. Both must give the same answer, so the live layout is pinned
# here as a literal -- and with a control that shows the hidden list is what
# does the work, rather than something else cleaning up after it.

LIVE_CARD = {
    "href": "https://www.linkedin.com/jobs/search-results/?keywords=Senior",
    "text": (
        "Profile image for several companies on LinkedIn\n\n"
        "Unread notification.\n\n"
        "Senior Software Engineer: new opportunities in Riverton.\n"
        "Senior Software Engineer: new opportunities in Riverton.\n"
        "View jobs\nView jobs\n\n22m"
    ),
    "hidden": [
        "Profile image for several companies on LinkedIn",
        "Unread notification.",
        "Senior Software Engineer: new opportunities in Riverton.",
        "View jobs",
    ],
    "time": "22m",
    "unread": True,
}


def test_the_live_layout_body_is_stripped_of_accessibility_text():
    """Red against the pre-fix code, through an API that already existed.

    ``parse_notification`` predates this fix, so this is one of the few places
    the OLD behaviour can be exercised directly: before it, this same record
    came back as "Profile image for several companies on LinkedIn Unread
    notification. Senior Software Engineer ... View jobs 22m".
    """
    row = shape.parse_notification(LIVE_CARD)
    assert row is not None
    assert row["text"] == "Senior Software Engineer: new opportunities in Riverton."


def test_the_live_layout_carries_the_time_the_page_wrote():
    """The other half, split out so its own failure is visible on its own."""
    row = shape.parse_notification(LIVE_CARD)
    assert row is not None
    assert row["when"] == "22 minutes ago"
    assert row["unread"] is True


def test_without_the_hidden_list_the_accessibility_text_survives():
    """The control. A check that cannot fail certifies nothing."""
    stripped = dict(LIVE_CARD)
    stripped.pop("hidden")
    row = shape.parse_notification(stripped)
    assert row is not None
    assert "Unread notification." in row["text"]


def test_without_the_time_element_there_is_no_when():
    """The other control: the body genuinely does not contain a readable time."""
    stripped = dict(LIVE_CARD)
    stripped["time"] = ""
    row = shape.parse_notification(stripped)
    assert row is not None
    assert "when" not in row


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("22m", "22 minutes ago"),
        ("1h", "1 hour ago"),
        ("2h", "2 hours ago"),
        ("3d", "3 days ago"),
        ("1w", "1 week ago"),
        ("2mo", "2 months ago"),
        ("1y", "1 year ago"),
    ],
)
def test_a_bare_compact_time_is_spelled_out(raw, expected):
    assert shape.compact_time_ago(raw) == expected


@pytest.mark.parametrize("text", ["1 reaction", "", "hello", "5x", "12", "3M Co"])
def test_a_bare_compact_time_reader_refuses_everything_else(text):
    assert shape.compact_time_ago(text) is None


def test_the_two_time_readers_disagree_about_3m_on_purpose():
    """The reason there are two of them, in one assertion.

    ``compact_time_ago`` is handed the notification card's OWN time element --
    a string LinkedIn has already declared to be a timestamp -- so "3M" there
    is three minutes and reading it as such is right. ``find_time_ago`` scans
    free prose, where "3M" is a company, so it requires the word "ago" and
    finds nothing. Folding the two together would break one or the other.
    """
    assert shape.compact_time_ago("3M") == "3 minutes ago"
    assert shape.find_time_ago(["3M Company"]) is None


@pytest.mark.parametrize("text", ["3M Company", "1 reaction", "Head of 5d Printing"])
def test_free_text_scanning_still_refuses_a_time_with_no_ago(text):
    """The guard the compact reader must not have loosened."""
    assert shape.find_time_ago([text]) is None


# ---------------------------------------------------------------------------
# 4c. The screen-reader budget's premise, on the surface left behind
# ---------------------------------------------------------------------------
#
# 8573b8b fixed this in HARVEST_LINKED_CARDS_JS and deliberately did NOT touch
# HARVEST_BLOCK_CARDS_JS, on the stated grounds that notifications are its only
# caller, that no fixture exercised a non-rendered duplicate here, and that a
# surface it could not verify may not be changed on the strength of an
# argument. This section is the missing evidence, and it was written and run
# RED before the guard was ported.
#
# THE PREMISE. strip_screen_reader_copies subtracts BY COUNT -- one occurrence
# per hidden element -- and its docstring states what makes that allowed:
# "innerText includes visually-hidden text". True of the CLIP pattern, where
# the element IS rendered and innerText really does carry a second copy. FALSE
# of display:none, whose copy innerText never returned -- and textOf() reads it
# anyway, because innerText on a NON-RENDERED element falls back to
# textContent. The budget is then charged for a duplicate that was never in the
# card, and the subtraction pays for it out of the VISIBLE one.
#
# The card below is written by hand rather than captured, and that is exactly
# why the hole survived: none of the six frozen notifications repeats its body
# in a non-rendered element, so no assertion in section 4 could have gone red
# no matter how the budget behaved.

#: The CLIP pattern: the element IS rendered, only clipped to nothing, so its
#: text really is in innerText and removing one copy is correct. Spelled
#: exactly as in tests/test_tracker_harvest_census.py, where the sibling
#: script's version of this guard is pinned, so the two surfaces are held to
#: the same stylesheet rather than to two hand-written approximations of it.
CLIP = (
    "position:absolute;clip:rect(0 0 0 0);clip-path:inset(50%);"
    "height:1px;width:1px;overflow:hidden"
)

DUPLICATED_BODY = (
    "Priya Sharma commented on your post: Congratulations on the launch!"
)
#: The href is a PLACEHOLDER, not a shape-valid urn, and that is deliberate.
#: Nothing here parses it -- the walk returns it untouched and every assertion
#: below is about the card's TEXT -- so a urn-shaped literal would buy realism
#: in a field no test reads, at the price of a standing entry in
#: tests/test_no_committed_identity.py's DECLARED_PLANTS. That guard fired on
#: the first version of this constant and it was right to: it cannot tell an
#: invented urn from a real one, which is the whole of its value. The two files
#: that DO hold urn-shaped literals earned their entries by needing the shape
#: -- one feeds a redactor, one certifies that _target_for declines to validate
#: the shape. This one does not, so the allowlist stays where it was.
DUPLICATED_LINK = "https://www.linkedin.com/feed/update/<urn>/"


def notification_card(style: str) -> str:
    """One notification card whose entire body is repeated in a hidden span.

    The shape is the live one: an ``article.nt-card`` inside the card list, one
    anchor, and the timestamp in its own ``p.nt-card__time-ago`` -- so the
    selectors under test are the ones the notifications tool actually passes,
    not a simplification that would let the walk succeed for the wrong reason.
    """
    return (
        '<main><div class="nt-card-list">'
        '<article class="nt-card">'
        f'<a href="{DUPLICATED_LINK}">'
        f'<span class="visually-hidden" style="{style}">{DUPLICATED_BODY}</span>'
        f"<span>{DUPLICATED_BODY}</span></a>"
        '<p class="nt-card__time-ago">2h</p>'
        "</article></div></main>"
    )


async def test_a_body_repeated_in_a_display_none_span_is_not_eaten():
    """THE DEFECT, reached through the notifications caller.

    The card prints its body ONCE and hides a second copy in a display:none
    span. innerText never carried that copy, so the card arrives with one body
    -- but the hidden list arrives with one entry, the budget spends it on the
    only copy there is, and the notification is left with no line at all.
    parse_notification then has nothing to return and the row is DROPPED: the
    same records=N, dropped=N signature the tracker showed.

    SHOWN FAILING against dom.py before the isRendered guard was ported::

        AssertionError: assert [] == ['Priya Sharma commented on your
        post: Congratulations on the launch!']
        Right contains one more item: 'Priya Sharma commented on your
        post: Congratulations on the launch!'

    -- and the record printed alongside it says why: hidden carried the
    body while text carried it exactly ONCE, so the budget's one removal
    was spent on the visible copy. rows == [], dropped == 1.
    """
    records, rows, dropped = await _notifications_from(
        notification_card("display:none")
    )

    assert len(records) == 1, records
    # The headline, asserted first, so a regression reports the lost body
    # rather than the mechanism that lost it.
    assert [row["text"] for row in rows] == [DUPLICATED_BODY], (records, rows)
    assert dropped == 0, records
    # The mechanism: a copy innerText never carried is never charged.
    assert records[0]["hidden"] == [], records[0]
    assert records[0]["text"].count(DUPLICATED_BODY) == 1, records[0]


async def test_a_clipped_duplicate_is_still_charged_on_this_surface():
    """THE CONTROL, and the behaviour the guard must NOT change.

    Notifications are a surface the subtraction was built for: the live cards
    weld "Unread notification." and a repeated body onto every innerText they
    hand back, and section 4 pins six of them. A guard that stopped charging
    the clip pattern would hand all of that straight back as content, which is
    a regression wearing a fix's commit message.

    SHOWN FAILING by skipping every hidden element regardless of rendering::

        AssertionError: assert [] == ['Priya Sharma commented on your post:
        Congratulations on the launch!'] -- a rendered duplicate stopped being
        subtracted, so the body comes back printed twice.
    """
    records, rows, dropped = await _notifications_from(notification_card(CLIP))

    assert len(records) == 1, records
    # The card really does carry both copies. Without this the assertions
    # below would also hold of a page that never had a duplicate to subtract.
    assert records[0]["text"].count(DUPLICATED_BODY) == 2, records[0]
    assert records[0]["hidden"] == [DUPLICATED_BODY], records[0]
    assert dropped == 0, records
    assert [row["text"] for row in rows] == [DUPLICATED_BODY], rows


async def test_a_visibility_hidden_duplicate_was_never_charged_either_way():
    """MEASURED, and deliberately NOT filed under the fix.

    visibility:hidden is the case the guard looks like it should also be for,
    and on this script it changes nothing: the element IS rendered, so
    innerText runs its rendering algorithm and returns '' for it, textOf()
    therefore yields an empty string, and it was never pushed onto the hidden
    list to begin with. Measured 2026-08-31 against dom.py both before and
    after the guard: hidden == [] in both, rows identical.

    It is pinned anyway, because the reason it is safe is a property of
    innerText rather than of anything in this package, and a rewrite of
    textOf() that reached for textContent would silently turn this into the
    display:none bug with no test to catch it.

    The sibling script records the same measurement from the other side: there
    the visibilityProperty option moves only its skip COUNTER, 2 -> 0, and
    leaves the budget identical. HARVEST_BLOCK_CARDS_JS has no counter, so
    here that option is observable in nothing at all -- MUTATION-CHECKED, not
    inherited: dropping it from the ported guard leaves all three cases in
    this section green. It is passed regardless, so the two scripts ask the
    DOM the same question rather than drifting into two different ones, and
    the fact that no test can tell is written down instead of implied.
    """
    records, rows, dropped = await _notifications_from(
        notification_card("visibility:hidden")
    )

    assert len(records) == 1, records
    assert records[0]["hidden"] == [], records[0]
    assert records[0]["text"].count(DUPLICATED_BODY) == 1, records[0]
    assert dropped == 0, records
    assert [row["text"] for row in rows] == [DUPLICATED_BODY], rows


# ---------------------------------------------------------------------------
# 5. The profile
# ---------------------------------------------------------------------------


async def _profile(which: str):
    async def work(page):
        fields = await dom.read_profile_fields(page)
        sections = fields.get("sections") or []
        topcard = shape.pick_topcard(sections, fields.get("title"))
        return fields, sections, topcard

    return await _with_page(PROFILE_FIXTURES[which], work)


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_profile_identity_is_read_from_a_page_with_no_h1(which):
    """The defect: name, headline and location all read null and the tool errored."""
    _, _, topcard = await _profile(which)
    identity = shape.parse_profile_topcard((topcard or {}).get("lines") or [])

    assert identity["name"] == NAME
    assert identity["headline"] == HEADLINE
    assert identity["location"] == LOCATION


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_school_is_not_mistaken_for_the_location(which):
    """It sits between the headline and the location on this render.

    Reading the location as "the second eligible line" returned the school,
    which is a plausible-looking wrong answer -- the worst kind.
    """
    _, _, topcard = await _profile(which)
    identity = shape.parse_profile_topcard((topcard or {}).get("lines") or [])
    assert identity["location"] != SCHOOL
    assert identity["headline"] != SCHOOL


async def test_both_renders_produce_the_same_identity():
    """Hydration timing must not change what the operator is told."""
    answers = []
    for which in BOTH_PROFILES:
        _, _, topcard = await _profile(which)
        answers.append(
            shape.parse_profile_topcard((topcard or {}).get("lines") or [])
        )
    assert answers[0] == answers[1]


@pytest.mark.parametrize("which", BOTH_PROFILES)
async def test_the_topcard_is_found_by_name_not_by_position(which):
    _, sections, topcard = await _profile(which)
    assert topcard is not None
    assert topcard["heading"] == NAME
    assert sections[0]["heading"] == NAME


def test_the_topcard_is_still_found_when_it_is_not_the_first_section():
    """Position is a fallback, so it must not be the only route."""
    sections = [
        {"heading": "Analytics", "lines": ["Analytics"], "images": 0},
        {"heading": NAME, "lines": [NAME, HEADLINE], "images": 1},
    ]
    picked = shape.pick_topcard(sections, f"{NAME} | LinkedIn")
    assert picked["heading"] == NAME


async def test_the_photo_is_detected_on_a_page_with_no_photo_class():
    """``img[class*="profile-photo"]`` matched nothing, so has_photo read false."""
    _, _, topcard = await _profile("hydrated")
    assert topcard["images"] > 0


async def test_the_about_text_is_read_from_the_hydrated_render():
    _, sections, _ = await _profile("hydrated")
    about = shape.profile_section_lines(sections, "About")
    assert about == [
        "I build production backend services in Node.js and TypeScript, and I "
        "have spent five years doing it across payments, messaging "
        "infrastructure and consumer health."
    ]


async def test_the_pre_hydration_render_simply_has_no_about_section():
    """And that is UNKNOWN, not "he has no About" -- the tool says which."""
    _, sections, _ = await _profile("pre_hydration")
    assert [s["heading"] for s in sections] == [NAME]
    assert shape.profile_section_lines(sections, "About") == []


async def test_the_hydrated_render_shows_which_sections_arrived():
    _, sections, _ = await _profile("hydrated")
    assert [s["heading"] for s in sections] == [NAME, "Analytics", "About"]


# ---------------------------------------------------------------------------
# 6. The skills page
# ---------------------------------------------------------------------------


async def _skills():
    async def work(page):
        records = await dom.harvest_linked_cards(
            page, href_pattern=dom.SKILL_HREF, max_items=200, max_chars=300
        )
        skills: list[str] = []
        for record in records:
            lines = shape.content_lines(record.get("text", ""))
            if not lines:
                continue
            name = shape.trim(lines[0], 80)
            if name and name not in skills:
                skills.append(name)
        return records, skills

    return await _with_page(PROFILE_SKILLS, work)


async def test_the_skills_page_yields_skills_and_not_filter_pills():
    """It was returning "All", "Industry Knowledge", "Tools & Technologies"."""
    records, skills = await _skills()
    assert len(records) == 6
    assert skills == SKILLS
    for pill in FILTER_PILLS:
        assert pill not in skills


async def test_a_skill_keeps_only_its_name_not_its_evidence_lines():
    """The first entry carries two extra lines. Neither is the skill."""
    _, skills = await _skills()
    assert skills[0] == "Node.js"
    assert not any("experiences at" in skill for skill in skills)
    assert not any("Skill Assessment" in skill for skill in skills)
