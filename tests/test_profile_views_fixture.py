"""The profile-views surface, tested against the pages LinkedIn actually served.

Every other test in this suite runs on hand-written card text. That is the
right way to test the shapers, and it is exactly why this bug survived: the
defect was not in the shaping at all, it was in the DOM walk that decides
where a row STOPS, and hand-written text cannot exercise a walk. The tool
shipped four rows all named "Who's viewed your profile" -- the page heading,
wearing four different real people's profile links -- while every pure test
passed the whole time.

So this module does the one thing the others cannot: it runs the REAL
injected harvester over REAL frozen markup.

TWO fixtures, and the second is not a luxury. Both are the viewer-list
section of /analytics/profile-views/ captured on 2026-08-21, minutes apart,
from the same account:

* ``profile_views_analytics.html`` -- the PRE-HYDRATION render. No ``li``, no
  ``article``, and no ``data-view-name``. All three of the walk's original
  stops are missing, so it ran to ``maxHops`` and swallowed the heading.
* ``profile_views_analytics_hydrated.html`` -- the SAME page after LinkedIn's
  client attached ``data-view-name``. The walk stops early here, which puts
  each row's container at a different depth, which changes which node is a
  row's parent.

That difference is why both are pinned. A sibling harvest keyed on "the
linked rows share a parent" passes every assertion on the first fixture and
silently returns nothing extra on the second -- it was written that way, and
the first fixture alone called it green. The list is found as the nearest
common ancestor precisely so that it does not depend on how far the walk got.

Both fixtures have scripts, styles, images and all attributes removed
(``data-view-name`` deliberately kept in the second), and the viewers' names,
headlines, slugs and companies replaced with synthetic ones. The DOM SHAPE is
what is preserved, because the shape is the subject.

The counts below are what the real page held: 4 viewers who let their name
show, 6 who did not, and one recruiter roll-up card that is not a viewer.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"
#: name -> the render it froze. Every harvester test runs against both.
FIXTURES = {
    "pre_hydration": FIXTURE_DIR / "profile_views_analytics.html",
    "hydrated": FIXTURE_DIR / "profile_views_analytics_hydrated.html",
}
BOTH = sorted(FIXTURES)

#: The heading of the page. No row may ever be called this.
PAGE_HEADING = "Who's viewed your profile"
#: The date-range filter, which sits directly under the heading and became
#: every row's headline in the same failure.
PAGE_FILTER = "Past 90 days"

#: Viewers on the frozen page who let their name show.
NAMED_VIEWERS = 4
#: Viewers LinkedIn showed with a company, no name and no link.
ANONYMOUS_VIEWERS = 6
#: Not a viewer: the "2 recruiters viewed your profile" roll-up card.
ROLLUP_CARDS = 1

#: The bullet in front of a connection-degree badge, spelled this way so this
#: file stays pure ASCII -- the convention shape.py uses for the middle dot.
BULLET = chr(0x2022)

NAMES = ("Priya Sharma", "Arun Balakrishnan", "Meera Iyer", "Rohan Desai")

PRIYA_HEADLINE = (
    "Computer Science Student at Hillcrest Institute | Building things that ship"
)


# ---------------------------------------------------------------------------
# 1. The fixtures themselves
# ---------------------------------------------------------------------------
#
# These run with no browser. Their job is to stop the browser tests below
# from going vacuous: a fixture quietly emptied or regenerated wrong would
# make every assertion about "the rows" true of nothing at all.


@pytest.mark.parametrize("which", BOTH)
def test_the_fixture_exists_and_is_the_captured_page(which):
    path = FIXTURES[which]
    assert path.exists(), f"missing fixture: {path}"
    html = path.read_text(encoding="utf-8")
    assert PAGE_HEADING in html
    assert PAGE_FILTER in html
    for name in NAMES:
        assert name in html, name
    assert html.count("Viewed ") >= NAMED_VIEWERS + ANONYMOUS_VIEWERS


def test_the_two_fixtures_really_are_the_two_renders():
    """The one difference that makes the second fixture worth keeping."""
    pre = FIXTURES["pre_hydration"].read_text(encoding="utf-8")
    hydrated = FIXTURES["hydrated"].read_text(encoding="utf-8")
    assert "data-view-name" not in pre
    assert 'data-view-name="viewer-list-item"' in hydrated


@pytest.mark.parametrize("which", BOTH)
def test_no_fixture_has_a_stop_the_walk_can_lean_on(which):
    """Neither render offers ``li`` or ``article``; that is the whole problem."""
    html = FIXTURES[which].read_text(encoding="utf-8")
    assert "<li" not in html
    assert "<article" not in html


@pytest.mark.parametrize("which", BOTH)
def test_the_fixture_carries_no_session_material(which):
    html = FIXTURES[which].read_text(encoding="utf-8")
    for token in ("li_at", "JSESSIONID", "csrfToken", "urn:li:member", "Bearer "):
        assert token not in html, token


# ---------------------------------------------------------------------------
# 2. The shapers, on the exact row text the frozen pages produce
# ---------------------------------------------------------------------------
#
# Kept as literals rather than read through a browser so they run everywhere.

NAMED_ROW = (
    "Priya Sharma\n\n"
    + BULLET
    + " 3rd\n\nComputer Science Student at Hillcrest Institute | Building "
    "things that ship\n\nViewed 3d ago\n\nMessage"
)
NAMED_ROW_WITH_MUTUALS = (
    "Arun Balakrishnan\n\n"
    + BULLET
    + " 2nd\n\nHeavy Industry professional | Bulk Materials Handling\n\n"
    "Viewed 5d ago\n\n1 mutual connection\n\nConnect"
)
ANONYMOUS_ROW = "Someone at Inkwell Press\n\nViewed 1w ago\n\nSearch"
RECRUITER_ROW = "Recruiter at Larkspur Health\n\nViewed 4w ago\n\nSearch"
ROLLUP_ROW = (
    "2 recruiters viewed your profile\n\nFrom Grayling Partners, LLC and "
    "other companies\n\nView all recruiters"
)
#: What a row looked like when the walk overshot: the heading block, with a
#: real viewer's link attached to it.
OVERSHOT_ROW = (
    "Who's viewed your profile\n\nPast 90 days\nInteresting viewers\nCompany\n"
    "All filters\nReset\n\n27\n\nProfile viewers\n\nPriya Sharma\n\n"
    + BULLET
    + " 3rd\n\nViewed 3d ago"
)


def test_degree_badge_does_not_become_the_headline():
    card = shape.parse_person_card(
        {"href": "/in/priya-sharma-8a41b207/", "text": NAMED_ROW}
    )
    assert card is not None
    assert card["headline"] == PRIYA_HEADLINE


def test_compact_timestamp_is_read_and_spelled_out():
    card = shape.parse_person_card(
        {"href": "/in/priya-sharma-8a41b207/", "text": NAMED_ROW}
    )
    assert card is not None
    assert card["viewed"] == "3 days ago"


def test_mutual_connections_line_does_not_become_the_headline():
    card = shape.parse_person_card(
        {"href": "/in/arun-balakrishnan-4c19d833/", "text": NAMED_ROW_WITH_MUTUALS}
    )
    assert card is not None
    assert card["headline"].startswith("Heavy Industry professional")
    assert card["viewed"] == "5 days ago"


@pytest.mark.parametrize("text", [ANONYMOUS_ROW, RECRUITER_ROW])
def test_a_row_with_no_link_is_anonymous_and_stays_anonymous(text):
    card = shape.parse_person_card({"href": "", "text": text})
    assert card is not None
    assert card["anonymous"] is True
    assert "profile" not in card
    assert card["viewed"]
    # The company is the only thing LinkedIn showed, so it is the name. It is
    # not a headline and must not be dressed up as one.
    assert card["headline"] is None


def test_the_recruiter_rollup_card_is_not_a_viewer():
    assert shape.parse_person_card({"href": "", "text": ROLLUP_ROW}) is None


def test_the_page_heading_is_never_a_person_even_with_a_link_attached():
    assert (
        shape.parse_person_card(
            {"href": "/in/priya-sharma-8a41b207/", "text": OVERSHOT_ROW}
        )
        is None
    )


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Viewed 3d ago", "3 days ago"),
        ("Viewed 1w ago", "1 week ago"),
        ("Viewed 4w ago", "4 weeks ago"),
        ("Viewed 1mo ago", "1 month ago"),
        ("Viewed 2mo ago", "2 months ago"),
        ("Viewed 12h ago", "12 hours ago"),
        ("Viewed 1h ago", "1 hour ago"),
        ("Viewed 30m ago", "30 minutes ago"),
    ],
)
def test_compact_units_are_normalised(line, expected):
    assert shape.find_time_ago([line]) == expected


def test_month_is_not_read_as_minutes():
    """``mo`` before ``m``: the other order turns two months into two minutes."""
    assert shape.find_time_ago(["Viewed 2mo ago"]) == "2 months ago"
    assert shape.find_time_ago(["Viewed 2m ago"]) == "2 minutes ago"


def test_a_compact_unit_without_the_word_ago_is_not_a_time():
    """Guards the widened pattern: "3M" and "1 reaction" are not timestamps."""
    assert shape.find_time_ago(["3M Company"]) is None
    assert shape.find_time_ago(["1 reaction"]) is None
    assert shape.find_time_ago(["Head of 5d Printing"]) is None


# ---------------------------------------------------------------------------
# 3. The harvester, over the frozen markup, on BOTH renders
# ---------------------------------------------------------------------------


async def _harvest(which: str, sibling_rows: bool = True):
    """Run the REAL injected script over one of the frozen pages."""
    playwright = pytest.importorskip("playwright.async_api")
    html = FIXTURES[which].read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await dom.harvest_linked_cards(
                page,
                href_pattern=dom.PERSON_HREF,
                max_items=75,
                sibling_rows=sibling_rows,
            )
        finally:
            await browser.close()


async def _rows(which: str, sibling_rows: bool = True):
    records = await _harvest(which, sibling_rows)
    return dom.parse_all(records, shape.parse_person_card)


@pytest.mark.parametrize("which", BOTH)
async def test_every_row_is_a_different_person(which):
    """The bug, stated as the property it violated.

    Four rows came back with one identical name. "names are non-empty" was
    true throughout; distinctness is what was false.
    """
    rows, _ = await _rows(which)
    names = [row["name"] for row in rows]
    assert len(names) == len(set(names)), names


@pytest.mark.parametrize("which", BOTH)
async def test_no_row_is_named_after_the_page(which):
    rows, _ = await _rows(which)
    assert rows
    for row in rows:
        assert row["name"] != PAGE_HEADING, row
        assert PAGE_HEADING not in (row["name"] or "")
        assert row["headline"] != PAGE_FILTER, row


@pytest.mark.parametrize("which", BOTH)
async def test_the_named_viewers_come_back_whole(which):
    rows, _ = await _rows(which)
    by_name = {row["name"]: row for row in rows}

    assert "Priya Sharma" in by_name, sorted(by_name)
    priya = by_name["Priya Sharma"]
    assert priya["headline"] == PRIYA_HEADLINE
    assert priya["viewed"] == "3 days ago"
    assert priya["anonymous"] is False
    assert priya["profile"] == "https://www.linkedin.com/in/priya-sharma-8a41b207"

    assert by_name["Rohan Desai"]["viewed"] == "1 week ago"
    assert by_name["Meera Iyer"]["headline"] == (
        "Humans and AI for clinics | Co-Founder @ northgate.example"
    )


@pytest.mark.parametrize("which", BOTH)
async def test_the_anonymous_viewers_are_not_dropped(which):
    """Six of the ten viewers had no link. A link-anchored harvest saw none.

    Parameterised over both renders on purpose: the first implementation of
    the sibling harvest passed this on ``pre_hydration`` and returned four
    rows on ``hydrated``.
    """
    rows, dropped = await _rows(which)

    anonymous = [row for row in rows if row["anonymous"]]
    named = [row for row in rows if not row["anonymous"]]
    assert len(named) == NAMED_VIEWERS, named
    assert len(anonymous) == ANONYMOUS_VIEWERS, anonymous
    assert len(rows) == NAMED_VIEWERS + ANONYMOUS_VIEWERS
    assert dropped == ROLLUP_CARDS, "the recruiter roll-up should be the only drop"


@pytest.mark.parametrize("which", BOTH)
async def test_no_anonymous_viewer_carries_a_link_or_a_slug(which):
    """The privacy line, asserted rather than promised."""
    rows, _ = await _rows(which)
    seen_anonymous = False
    for row in rows:
        if not row["anonymous"]:
            continue
        seen_anonymous = True
        assert "profile" not in row, row
        assert not any("linkedin.com/in/" in str(v) for v in row.values()), row
    assert seen_anonymous, "no anonymous row to check -- the fixture regressed"


@pytest.mark.parametrize("which", BOTH)
async def test_the_rollup_card_never_becomes_a_viewer(which):
    rows, _ = await _rows(which)
    for row in rows:
        assert "viewed your profile" not in row["name"].lower(), row


@pytest.mark.parametrize("which", BOTH)
async def test_the_container_fix_holds_without_the_sibling_harvest(which):
    """The row boundary is right on its own, not only in sibling mode."""
    rows, _ = await _rows(which, sibling_rows=False)
    assert len(rows) == NAMED_VIEWERS
    names = [row["name"] for row in rows]
    assert len(names) == len(set(names)), names
    assert PAGE_HEADING not in names
    assert all(row["viewed"] for row in rows), rows
    assert all(row["headline"] for row in rows), rows


@pytest.mark.parametrize("which", BOTH)
async def test_each_harvested_record_holds_exactly_one_person(which):
    """The invariant the walk now enforces, checked on the records themselves."""
    records = await _harvest(which, sibling_rows=False)
    assert records
    for record in records:
        slugs = set(re.findall(dom.PERSON_HREF, record["text"]))
        assert len(slugs) <= 1, record
        present = {name for name in NAMES if name in record["text"]}
        assert len(present) == 1, (present, record["text"][:120])


@pytest.mark.parametrize("which", BOTH)
async def test_both_renders_produce_the_same_answer(which):
    """Hydration timing must not change what the operator is told."""
    rows, _ = await _rows(which)
    summary = [(row["name"], row["viewed"], row["anonymous"]) for row in rows]
    reference, _ = await _rows("pre_hydration")
    expected = [(row["name"], row["viewed"], row["anonymous"]) for row in reference]
    assert summary == expected
