"""Job search, tested against the result pages LinkedIn actually served.

THE DEFECT. On a row for a VERIFIED employer LinkedIn adds a screen-reader
line reading "<title> with verification". Read positionally -- line 1 title,
line 2 company, line 3 location -- that line became the ``company`` and pushed
the real company down into ``location``. Measured live on 2026-08-22 over two
searches: 5 of 14 rows, e.g.

    title    'Senior Backend Developer (Node.js / NestJS)'
    company  'Senior Backend Developer (Node.js / NestJS) with verification'
    location 'Harborline Finance'

THE POINT IS THE CLASS, NOT THE STRING. "with verification" is one of many
things LinkedIn inserts into a row, and any of them shifts every field after
it. The same two pages carried "Promoted" (14 rows), "Apply" (8), "Actively
reviewing applicants" (5), "Viewed" (2), a salary chip (3) and an alumni line
("1 <company> alum works here"). So the fix anchors each field on what
IDENTIFIES it -- the title on the link that makes the row a job row, the
company on the accessible name of the employer's logo, the location on the
metadata list inside the entity lockup -- and section 4 injects a decoration
LinkedIn has never shipped to show that a NEW one would not shift anything
either.

THREE FIXTURES, and the pair is not a luxury:

* ``jobs_search.html`` -- the PRE-HYDRATION render of a Node.js search.
* ``jobs_search_hydrated.html`` -- the SAME seven jobs after the client
  finished. It carries the decorations the early render had not drawn yet,
  and 18 further list items that are placeholders with no link at all.
* ``jobs_search_salary.html`` -- a second, remote search. Its subject is the
  salary chip, which sits INSIDE the entity lockup in a list of its own,
  directly after the one holding the location.

Each is the results list and nothing else, with scripts, image sources and
tracking parameters removed, and with employers, places and job ids replaced
by invented ones.

ONE THING IS DELIBERATELY KEPT that the earlier fixtures strip: LinkedIn's
``.visually-hidden`` rule. Taking it away CHANGES THE DEFECT rather than
preserving it -- the hidden copy is absolutely positioned on the live page, so
``innerText`` gives it a line of its own, and that line is what shifted the
fields. With no stylesheet the same text arrives welded onto the title
instead, a different wrong answer. Section 3 therefore runs every row through
BOTH layouts, because the parse is claimed to be independent of which one it
gets, and that claim should be executable.
"""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

SEARCH_PRE = FIXTURE_DIR / "jobs_search.html"
SEARCH_HYDRATED = FIXTURE_DIR / "jobs_search_hydrated.html"
SEARCH_SALARY = FIXTURE_DIR / "jobs_search_salary.html"

#: The pre-hydration and hydrated renders of the SAME search, in the order a
#: browser produced them. Every harvester assertion runs against both.
FIXTURES = {
    "pre_hydration": SEARCH_PRE,
    "hydrated": SEARCH_HYDRATED,
    "salary": SEARCH_SALARY,
}
#: The two renders of one search. "Both renders agree" is only a question for
#: these; the salary fixture is a different search with different jobs.
SAME_SEARCH = ["pre_hydration", "hydrated"]
ALL_RENDERS = ["pre_hydration", "hydrated", "salary"]

#: job id -> (title, company, location), as the page displayed them.
#:
#: Written out rather than derived. "company is non-empty" was true of every
#: broken row -- the value was simply a location, or the title with four words
#: added -- so an assertion that does not name the answer cannot see this bug.
EXPECTED = {
    "pre_hydration": {
        "4600000001": (
            "Senior Software Engineer",
            "Northwind Labs",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
        "4600000015": (
            "Senior Backend Developer (Node.js / NestJS)",
            "Harborline Finance",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
        "4600000017": (
            "Senior Software Engineer - Backend",
            "Tallow Analytics",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
        "4600000008": (
            "Software Engineer",
            "Sablefort Security",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
        "4600000006": (
            "Back End Developer",
            "Brightpath Wellness",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
        "4600000013": (
            "Senior Backend Engineer (MERN)",
            "Kestrel Software",
            "Greater Fairhaven Area (Hybrid)",
        ),
        "4600000014": (
            "Software Engineer",
            "Grandview Networks",
            "Fairhaven, Riverton, Westland (On-site)",
        ),
    },
    "salary": {
        "4600001010": (
            "Full-Stack Engineer - Backend & Technical Delivery",
            "Perrin Digital",
            "Westland (Remote)",
        ),
        "4600001003": (
            "Backend Engineer | Remote",
            "Ridgeway Talent",
            "Westland (Remote)",
        ),
        "4600001001": (
            "Software Engineer - Backend",
            "Aldergate Insurance",
            "Westland (Remote)",
        ),
        "4600001023": (
            "Backend Software Developer (Remote)",
            "Fenwick Staffing",
            "Westland (Remote)",
        ),
        "4600001022": (
            "Software Engineer - Backend (Remote)",
            "Calderwood AI",
            "Westland (Remote)",
        ),
        "4600001009": (
            "Lead DevOps Engineer",
            "Thornbury Cyber - Enterprise Defence Partner",
            "Westland (Remote)",
        ),
        "4600001008": (
            "Full Stack Engineer",
            "Lumen Scribe",
            "Westland (Remote)",
        ),
    },
}
#: The hydrated render is the same seven jobs, decorated.
EXPECTED["hydrated"] = EXPECTED["pre_hydration"]

#: The rows LinkedIn drew with a verification badge, per render. These are the
#: rows that were broken; the others were right by luck of layout.
VERIFIED = {
    "pre_hydration": {"4600000015", "4600000008", "4600000006", "4600000014"},
    "hydrated": {"4600000015", "4600000008", "4600000006", "4600000014"},
    "salary": {"4600001009"},
}

#: The decoration itself, spelled once.
VERIFICATION_SUFFIX = "with verification"

#: List items the hydrated render carries with no job link at all. A harvest
#: anchored on links must return the seven jobs and none of these.
PLACEHOLDER_ROWS = 18

#: A decoration LinkedIn has not shipped. Section 4 injects it.
UNKNOWN_DECORATION = "Recommended by someone in your network"


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


_STYLE_BLOCK = re.compile(r"<style>.*?</style>", re.S)


def markup(which: str, *, styled: bool = True) -> str:
    """The fixture, optionally with LinkedIn's screen-reader rule removed.

    Removing it is not vandalism, it is the second layout: without the rule
    the hidden copy is inline and ``innerText`` welds it onto the title
    instead of giving it a line. Both are real -- which one arrives depends on
    whether the stylesheet had loaded -- and the parse must answer the same
    either way.
    """
    html = FIXTURES[which].read_text(encoding="utf-8")
    return html if styled else _STYLE_BLOCK.sub("", html)


async def _records(which: str, *, styled: bool = True):
    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=60
        )

    return await _with_html(markup(which, styled=styled), work)


async def _rows(which: str, *, styled: bool = True):
    records = await _records(which, styled=styled)
    return dom.parse_all(records, shape.parse_job_card)


# ---------------------------------------------------------------------------
# 1. The fixtures themselves
# ---------------------------------------------------------------------------
#
# No browser. Their job is to stop everything below from going vacuous: a
# fixture quietly emptied or regenerated wrong would make every assertion
# about "the rows" true of nothing at all. The privacy guards live in
# ``test_sdui_surfaces_fixture.py`` and these three files are on its list.


@pytest.mark.parametrize("which", ALL_RENDERS)
def test_the_fixture_exists_and_is_pure_ascii(which):
    path = FIXTURES[which]
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw, f"empty fixture: {path}"
    raw.decode("ascii")


@pytest.mark.parametrize("which", ALL_RENDERS)
def test_the_fixture_holds_the_jobs_it_is_supposed_to(which):
    # Unescaped so an expected value can be written the way the page RENDERS
    # it: one title carries an ampersand, which the markup spells "&amp;".
    html = unescape(FIXTURES[which].read_text(encoding="utf-8"))
    for job_id, (title, company, location) in EXPECTED[which].items():
        assert f"/jobs/view/{job_id}/" in html, job_id
        assert title in html, title
        assert f'alt="{company} logo"' in html, company
        assert location in html, location


@pytest.mark.parametrize("which", ALL_RENDERS)
def test_the_fixture_carries_the_decoration_under_test(which):
    """No verification line in the file means the bug cannot be reproduced."""
    html = FIXTURES[which].read_text(encoding="utf-8")
    for job_id in VERIFIED[which]:
        title = EXPECTED[which][job_id][0]
        assert f"{title} {VERIFICATION_SUFFIX}" in html, job_id


@pytest.mark.parametrize("which", ALL_RENDERS)
def test_the_fixture_keeps_the_screen_reader_rule(which):
    """Without it the hidden copy welds to the title and the defect changes."""
    html = FIXTURES[which].read_text(encoding="utf-8")
    assert "<style>" in html
    assert ".visually-hidden" in html
    assert "position: absolute" in html


def test_the_hydrated_fixture_carries_the_other_decorations():
    """Verification is one of several. The rest are on this page too."""
    html = SEARCH_HYDRATED.read_text(encoding="utf-8")
    for decoration in (
        "Promoted",
        "Apply",
        "Viewed",
        "Actively reviewing applicants",
        "company alum works here",
    ):
        assert decoration in html, decoration


def test_the_salary_fixture_carries_a_pay_chip():
    """The chip sits inside the lockup, in its own list after the location."""
    html = SEARCH_SALARY.read_text(encoding="utf-8")
    assert re.search(r"\$\d+/hr - \$\d+/hr", html), "no salary chip in the fixture"


def test_the_two_renders_really_are_two_renders():
    """Otherwise the pair pins one render twice and proves nothing."""
    pre = SEARCH_PRE.read_text(encoding="utf-8")
    hydrated = SEARCH_HYDRATED.read_text(encoding="utf-8")
    assert pre != hydrated
    pre_items = pre.count("data-occludable-job-id")
    hydrated_items = hydrated.count("data-occludable-job-id")
    assert pre_items == len(EXPECTED["pre_hydration"])
    assert hydrated_items == pre_items + PLACEHOLDER_ROWS
    # The decorations are what the client added afterwards.
    assert "Actively reviewing applicants" not in pre
    assert "Actively reviewing applicants" in hydrated


# ---------------------------------------------------------------------------
# 2. The shapers, on card records written here
# ---------------------------------------------------------------------------
#
# No browser, so these run everywhere. The record below is the exact shape the
# harvester returns for a verified row, and the exact text the live page gave.

VERIFIED_TITLE = "Senior Backend Developer (Node.js / NestJS)"
VERIFIED_COMPANY = "Harborline Finance"
VERIFIED_LOCATION = "Fairhaven, Riverton, Westland (On-site)"


def verified_record(**overrides) -> dict:
    record = {
        "href": "/jobs/view/4600000015/",
        "text": (
            f"{VERIFIED_TITLE}\n"
            f"{VERIFIED_TITLE} {VERIFICATION_SUFFIX}\n"
            f"{VERIFIED_COMPANY}\n"
            f"{VERIFIED_LOCATION}\n"
            "Actively reviewing applicants\n"
            "Promoted\n"
            "Apply"
        ),
        "hidden": [f"{VERIFIED_TITLE} {VERIFICATION_SUFFIX}"],
        "link_text": f"{VERIFIED_TITLE}\n{VERIFIED_TITLE} {VERIFICATION_SUFFIX}",
        "link_hidden": [f"{VERIFIED_TITLE} {VERIFICATION_SUFFIX}"],
        "logo_name": VERIFIED_COMPANY,
        "meta_line": VERIFIED_LOCATION,
    }
    record.update(overrides)
    return record


def test_the_verification_line_is_not_the_company():
    """The bug, stated as the three values it got wrong."""
    row = shape.parse_job_card(verified_record())
    assert row is not None
    assert row["title"] == VERIFIED_TITLE
    assert row["company"] == VERIFIED_COMPANY
    assert row["location"] == VERIFIED_LOCATION
    assert row["company"] != row["location"]
    assert VERIFICATION_SUFFIX not in row["company"]
    assert VERIFICATION_SUFFIX not in row["title"]


def test_the_welded_render_reads_the_same():
    """No stylesheet: the hidden copy arrives glued to the title, not below it."""
    welded = verified_record(
        text=(
            f"{VERIFIED_TITLE}  {VERIFIED_TITLE} {VERIFICATION_SUFFIX}\n"
            f"{VERIFIED_COMPANY}\n"
            f"{VERIFIED_LOCATION}"
        ),
        link_text=f"{VERIFIED_TITLE}  {VERIFIED_TITLE} {VERIFICATION_SUFFIX}",
    )
    row = shape.parse_job_card(welded)
    assert row is not None
    assert (row["title"], row["company"], row["location"]) == (
        VERIFIED_TITLE,
        VERIFIED_COMPANY,
        VERIFIED_LOCATION,
    )


def test_the_hidden_subtraction_alone_fixes_the_field_shift():
    """With every anchor gone, the page's own hidden list still saves it.

    Worth pinning separately: the anchors are the durable fix, but the
    subtraction is what keeps a surface that offers no logo and no metadata
    list -- the job tracker is one -- from inheriting the same shift.
    """
    bare = verified_record()
    for key in ("link_text", "link_hidden", "logo_name", "meta_line"):
        bare.pop(key)
    row = shape.parse_job_card(bare)
    assert row is not None
    assert (row["company"], row["location"]) == (VERIFIED_COMPANY, VERIFIED_LOCATION)


def test_a_plain_row_keeps_its_title_when_the_hidden_copy_is_identical():
    """LinkedIn repeats the title verbatim on an unverified row. One survives."""
    title = "Senior Software Engineer"
    row = shape.parse_job_card(
        {
            "href": "/jobs/view/4600000001/",
            "text": f"{title}\n{title}\nNorthwind Labs\nRiverton (On-site)",
            "hidden": [title],
            "link_text": f"{title}\n{title}",
            "link_hidden": [title],
            "logo_name": "Northwind Labs",
            "meta_line": "Riverton (On-site)",
        }
    )
    assert row is not None
    assert row["title"] == title
    assert row["company"] == "Northwind Labs"


def test_the_anchored_title_needs_the_link_to_name_one_thing():
    """A link wrapping a whole card is not a title, and says so by returning None.

    The job tracker draws exactly that: one anchor around the title, the
    company and the location. Reading its text as the title would put three
    facts in one field, so the anchor declines and the line walk takes over.
    """
    assert shape.anchored_title({}) is None
    assert (
        shape.anchored_title({"link_text": "Platform Integration Engineer"})
        == "Platform Integration Engineer"
    )
    assert (
        shape.anchored_title(
            {"link_text": "Platform Integration Engineer\nAshgrove Systems"}
        )
        is None
    )


def test_a_title_long_enough_to_be_trimmed_still_locates_the_next_field():
    """Trimming is for the OUTPUT. Matching runs on the full value.

    A title past the 120-character cap comes back with an ellipsis, and a
    truncated title no longer equals the line it came from -- so if the
    matching used the trimmed value, every field after it would quietly go
    positional again on exactly the rows least able to spare it.
    """
    long_title = "Senior Staff Engineer, " + ("Distributed Platform " * 8).strip()
    assert len(long_title) > 120
    # The decoration sits BEFORE the title, which is the only arrangement in
    # which the two behaviours differ: when the title is the first line,
    # ``lines_after`` falling back to "everything after line one" happens to
    # give the same answer, and the bug hides.
    row = shape.parse_job_card(
        {
            "href": "/jobs/view/4600000099/",
            "text": (
                f"{UNKNOWN_DECORATION}\n{long_title}\n"
                "Northwind Labs\nRiverton (Remote)"
            ),
            "link_text": long_title,
        }
    )
    assert row is not None
    assert row["title"].endswith("...")
    assert row["title"].startswith("Senior Staff Engineer,")
    assert row["company"] == "Northwind Labs"
    assert row["location"] == "Riverton (Remote)"


def test_lines_after_finds_a_field_by_its_text_not_its_index():
    lines = ["Title", "Decoration", "Company", "Location"]
    assert shape.lines_after(lines, "Company") == ["Location"]
    # Not present: everything after the first line, the old behaviour.
    assert shape.lines_after(lines, "Absent") == ["Decoration", "Company", "Location"]
    assert shape.lines_after(lines, None) == ["Decoration", "Company", "Location"]
    assert shape.lines_after([], "Company") == []


def test_a_metadata_line_that_repeats_a_field_is_refused():
    """The lockup's list moved. Reporting the company twice is not an answer."""
    row = shape.parse_job_card(
        verified_record(meta_line=VERIFIED_COMPANY),
    )
    assert row is not None
    assert row["location"] == VERIFIED_LOCATION


def test_the_tracker_row_still_splits_on_the_middle_dot():
    """The other surface through this parser must not regress."""
    dot = shape.MIDDLE_DOT
    row = shape.parse_job_card(
        {
            "href": "https://www.linkedin.com/jobs/view/4011223344/",
            "text": (
                "Platform Integration Engineer\n"
                f"Ashgrove Systems {dot} Fairhaven (Remote)\n"
                "Applied 3 days ago"
            ),
        }
    )
    assert row is not None
    assert row["title"] == "Platform Integration Engineer"
    assert row["company"] == "Ashgrove Systems"
    assert row["location"] == "Fairhaven (Remote)"
    assert row["status"] == "applied"
    assert row["when"] == "3 days ago"


# ---------------------------------------------------------------------------
# 3. The harvester, over the frozen pages, on every render
# ---------------------------------------------------------------------------

LAYOUTS = [True, False]
LAYOUT_IDS = {True: "styled", False: "welded"}


@pytest.mark.parametrize("styled", LAYOUTS, ids=lambda s: LAYOUT_IDS[s])
@pytest.mark.parametrize("which", ALL_RENDERS)
async def test_every_row_comes_back_exactly_as_the_page_showed_it(which, styled):
    rows, dropped = await _rows(which, styled=styled)
    assert dropped == 0, rows
    by_id = {row["job_id"]: row for row in rows}
    assert sorted(by_id) == sorted(EXPECTED[which]), sorted(by_id)
    for job_id, (title, company, location) in EXPECTED[which].items():
        row = by_id[job_id]
        assert row["title"] == title, row
        assert row["company"] == company, row
        assert row["location"] == location, row


@pytest.mark.parametrize("styled", LAYOUTS, ids=lambda s: LAYOUT_IDS[s])
@pytest.mark.parametrize("which", ALL_RENDERS)
async def test_no_company_is_a_title_a_location_or_a_decoration(which, styled):
    """The signature of the bug, checked without naming any expected value."""
    rows, _ = await _rows(which, styled=styled)
    assert rows
    locations = {row["location"] for row in rows}
    for row in rows:
        assert row["company"], row
        assert row["company"] != row["location"], row
        assert row["company"] != row["title"], row
        assert row["company"] not in locations, row
        assert VERIFICATION_SUFFIX not in row["company"], row
        assert VERIFICATION_SUFFIX not in row["title"], row
        assert VERIFICATION_SUFFIX not in (row["location"] or ""), row


@pytest.mark.parametrize("which", ALL_RENDERS)
async def test_the_verified_rows_are_the_ones_that_used_to_break(which):
    """Anti-vacuity: if no row on the page is verified, this module is idle."""
    records = await _records(which)
    decorated = {
        shape.job_id_from(record["href"])
        for record in records
        if VERIFICATION_SUFFIX in record["text"]
    }
    assert decorated == VERIFIED[which], decorated


@pytest.mark.parametrize("styled", LAYOUTS, ids=lambda s: LAYOUT_IDS[s])
async def test_both_renders_of_one_search_produce_the_same_answer(styled):
    """Hydration timing must not change what the operator is told."""
    answers = []
    for which in SAME_SEARCH:
        rows, _ = await _rows(which, styled=styled)
        answers.append(
            sorted(
                (row["job_id"], row["title"], row["company"], row["location"])
                for row in rows
            )
        )
    assert answers[0] == answers[1]


async def test_the_link_less_placeholders_are_not_returned_as_jobs():
    """The hydrated list holds 25 items. Eighteen of them are not jobs."""
    html = SEARCH_HYDRATED.read_text(encoding="utf-8")
    assert html.count("data-occludable-job-id") == 7 + PLACEHOLDER_ROWS
    rows, dropped = await _rows("hydrated")
    assert len(rows) == 7
    assert dropped == 0


@pytest.mark.parametrize("which", ALL_RENDERS)
async def test_the_harvest_reports_the_anchors_it_claims_to(which):
    """The observations the parse leans on, checked on the records themselves."""
    records = await _records(which)
    assert records
    for record in records:
        job_id = shape.job_id_from(record["href"])
        title, company, location = EXPECTED[which][job_id]
        assert record["logo_name"] == company, record
        assert record["meta_line"] == location, record
        assert shape.anchored_title(record) == title, record


# ---------------------------------------------------------------------------
# 3b. A shape written by hand, because no capture contains it
# ---------------------------------------------------------------------------
#
# Every card on both captured pages has a logo, so on those pages the climb
# from the link finds the lockup before it ever reaches the row -- and the
# clause that stops it AT the row could be deleted with all of section 3
# green. It is not decoration: without it a card LinkedIn draws with no logo
# sends the climb out of its own row and into the list, where the NEXT card's
# logo is waiting. That is a company name on the wrong job, which is the exact
# class of failure this module exists for, so the shape is written here.


def _card(
    job_id: str,
    title: str,
    company: str,
    location: str,
    *,
    logo: bool,
    extra_metadata: tuple[str, ...] = (),
) -> str:
    image = f'<div><img alt="{company} logo"></div>' if logo else "<div></div>"
    items = "".join(
        f"<li><span>{value}</span></li>" for value in (location,) + extra_metadata
    )
    return (
        f'<li data-occludable-job-id="{job_id}"><div class="lockup">{image}'
        f"<div><div>"
        f'<a href="/jobs/view/{job_id}/">'
        f'<span aria-hidden="true">{title}</span>'
        f'<span class="visually-hidden">{title} {VERIFICATION_SUFFIX}</span>'
        f"</a></div>"
        f"<div><span>{company}</span></div>"
        f"<div><ul>{items}</ul></div>"
        f"</div></div></li>"
    )


TWO_CARDS = (
    "<style>.visually-hidden { position: absolute; clip: rect(0 0 0 0); "
    "height: 1px; width: 1px; overflow: hidden; }</style>"
    "<ul>"
    + _card("4600009001", "Alpha Engineer", "Northwind Labs", "Riverton", logo=True)
    + _card("4600009002", "Beta Engineer", "Kestrel Software", "Fairhaven", logo=False)
    + "</ul>"
)


async def test_a_card_with_no_logo_does_not_borrow_its_neighbours():
    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=10
        )

    records = await _with_html(TWO_CARDS, work)
    rows, dropped = dom.parse_all(records, shape.parse_job_card)
    assert dropped == 0
    by_id = {row["job_id"]: row for row in rows}
    assert sorted(by_id) == ["4600009001", "4600009002"], sorted(by_id)

    assert by_id["4600009001"]["company"] == "Northwind Labs"
    assert by_id["4600009001"]["location"] == "Riverton"
    # The card with no logo has no company anchor, so it reads lines -- and
    # the line it reads must be its OWN.
    assert by_id["4600009002"]["company"] == "Kestrel Software"
    assert by_id["4600009002"]["location"] == "Fairhaven"


CROWDED_METADATA = (
    "<ul>"
    + _card(
        "4600009003",
        "Gamma Engineer",
        "Harborline Finance",
        "Riverton (Hybrid)",
        logo=True,
        extra_metadata=("$90/hr - $140/hr", "Health insurance"),
    )
    + "</ul>"
)


async def test_the_location_is_the_first_metadata_entry_not_the_last():
    """Also written by hand: every captured row's metadata list holds ONE item.

    On the live pages the salary sits in a list of its OWN, directly after the
    one holding the location, so first and last coincide and the choice
    between them could be flipped with everything above still green. Put two
    entries in one list -- which is how LinkedIn draws this elsewhere -- and
    the location is the first, in the order a reader sees them.
    """

    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=10
        )

    records = await _with_html(CROWDED_METADATA, work)
    assert len(records) == 1
    assert records[0]["meta_line"] == "Riverton (Hybrid)"
    rows, _ = dom.parse_all(records, shape.parse_job_card)
    assert rows[0]["location"] == "Riverton (Hybrid)"
    assert rows[0]["company"] == "Harborline Finance"


# ---------------------------------------------------------------------------
# 4. The guard: a decoration LinkedIn has not shipped yet
# ---------------------------------------------------------------------------
#
# "with verification" is the one that happened to appear in a five-row sample.
# The failure it caused belongs to a CLASS -- any line inserted anywhere in a
# card shifts every field read positionally after it -- so the guard injects a
# line that is not on any list anywhere, at every position in every row, and
# requires the answer not to move.


def _spliced(record: dict, position: int) -> dict:
    """The same record with one unknown line inserted at ``position``."""
    lines = record["text"].split("\n")
    lines.insert(position, UNKNOWN_DECORATION)
    spliced = dict(record)
    spliced["text"] = "\n".join(lines)
    return spliced


@pytest.mark.parametrize("which", ALL_RENDERS)
async def test_an_unknown_decoration_anywhere_in_a_row_shifts_nothing(which):
    records = await _records(which)
    assert records
    for record in records:
        job_id = shape.job_id_from(record["href"])
        title, company, location = EXPECTED[which][job_id]
        line_count = len(record["text"].split("\n"))
        for position in range(line_count + 1):
            row = shape.parse_job_card(_spliced(record, position))
            assert row is not None, (job_id, position)
            assert (row["title"], row["company"], row["location"]) == (
                title,
                company,
                location,
            ), (job_id, position, row)


async def test_the_unknown_decoration_guard_can_actually_fail():
    """The control. Without the anchors the same injection moves the fields.

    A guard that passes because nothing it does reaches the code under test
    certifies nothing, so this strips the anchors off the very same records
    and requires the injection to break at least one row -- which is what the
    positional read did, and what it would do again.
    """
    records = await _records("hydrated")
    assert records
    broken = 0
    for record in records:
        job_id = shape.job_id_from(record["href"])
        _, company, location = EXPECTED["hydrated"][job_id]
        bare = {
            key: value
            for key, value in record.items()
            if key not in ("link_text", "link_hidden", "logo_name", "meta_line")
        }
        for position in range(1, 4):
            row = shape.parse_job_card(_spliced(bare, position))
            if row is None or (row["company"], row["location"]) != (
                company,
                location,
            ):
                broken += 1
    assert broken, (
        "the injection changed nothing even with the anchors removed -- the "
        "guard above is not measuring the anchoring"
    )
