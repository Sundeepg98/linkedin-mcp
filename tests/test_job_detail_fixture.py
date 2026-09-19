"""The job posting, read from the page LinkedIn actually served.

WHY THIS SURFACE EXISTS AT ALL. Every list tool here returns CARDS: title,
company, location, id, link. That is enough to recognise a job and not nearly
enough to decide on one. The posting itself carries the three facts that
actually settle it -- what it pays, how many people have already applied, and
what the work is -- and none of the three is on any card. Measured on
2026-08-22: a six-result search returned six rows and zero descriptions, zero
salaries and zero applicant counts.

WHAT EACH FIXTURE PINS. All three are the same real posting, captured on
2026-08-22, with the employer, its slug and the job id replaced by invented
ones, and with scripts, styles, svg, images, media urls, urns and tracking
tokens removed.

* ``job_detail_hydrated.html`` -- the settled page as LinkedIn served it,
  carrying its ``data-view-name`` instrumentation.
* ``job_detail.html`` -- the SAME render with that instrumentation stripped.
  It is here because of a defect this repo has already shipped once: a reader
  anchored on hydration-only attributes passes every test on one render and
  returns nothing on the other. Agreeing across the pair is the property, and
  it is asserted field by field rather than as a summary.
* ``job_detail_shell.html`` -- the document BEFORE its content renders, which
  is what a slow network hands you. It carries the document ``<title>``,
  because LinkedIn sets that server-side, and NOTHING else. Its whole job is
  to prove that a title on its own does not become an answer: this must read
  as a FAILURE, never as a posting with most of its fields missing.

THE ANCHORING RULE, restated because this surface is where it matters most.
Nothing below is read by line number. The employer comes from the
``/company/`` link, the title from the document title with the employer taken
off the end (the title itself contains a ``|``, so splitting on the separator
is wrong), and every fact on the metadata line is claimed by WHAT IT IS -- an
applicant count, a time-ago, a currency range -- never by where it sits. The
job-card parser on this repo was broken for exactly the other reason.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

DETAIL_PRE = FIXTURE_DIR / "job_detail.html"
DETAIL_HYDRATED = FIXTURE_DIR / "job_detail_hydrated.html"
DETAIL_SHELL = FIXTURE_DIR / "job_detail_shell.html"

FIXTURES = {
    "pre_hydration": DETAIL_PRE,
    "hydrated": DETAIL_HYDRATED,
    "shell": DETAIL_SHELL,
}

#: The two renders that must agree. The shell is deliberately not among them.
BOTH_RENDERS = ["pre_hydration", "hydrated"]

JOB_ID = "4600000042"
COMPANY = "Ashgrove Systems"
COMPANY_SLUG = "ashgrove-systems"
TITLE = "Backend Engineer | Remote"

#: chr(0xB7) is the middle dot LinkedIn separates metadata with, and chr(0x20B9)
#: the rupee sign. Spelled this way so this file stays pure ASCII, as shape.py
#: does.
DOT = chr(0xB7)
RUPEE = chr(0x20B9)


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


def markup(which: str) -> str:
    return FIXTURES[which].read_text(encoding="ascii")


async def _identity(which: str):
    async def work(page):
        return await dom.read_job_identity(page)

    return await _with_html(markup(which), work)


async def _main_text(which: str) -> str:
    async def work(page):
        return await dom.read_main_text(page)

    return await _with_html(markup(which), work)


async def _detail(which: str):
    """The whole read, exactly as the tool assembles it."""

    async def work(page):
        identity = await dom.read_job_identity(page)
        text = await dom.read_main_text(page)
        return shape.parse_job_detail(
            text,
            company=identity.get("company"),
            document_title=identity.get("document_title"),
        )

    return await _with_html(markup(which), work)


def _parse(body: str, *, company=COMPANY, title=TITLE):
    """Shape a posting from text alone, the way the fixtures deliver it."""
    document_title = f"{title} | {company} | LinkedIn" if company else ""
    return shape.parse_job_detail(
        body, company=company, document_title=document_title
    )


# ---------------------------------------------------------------------------
# 1. The fixtures themselves
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", list(FIXTURES))
def test_the_fixture_exists_and_is_pure_ascii(which):
    path = FIXTURES[which]
    assert path.exists(), f"missing fixture: {path}"
    raw = path.read_bytes()
    assert raw, f"empty fixture: {path}"
    raw.decode("ascii")


@pytest.mark.parametrize("which", BOTH_RENDERS)
def test_the_fixture_holds_the_posting_it_is_supposed_to(which):
    html = markup(which)
    assert TITLE in html
    assert COMPANY in html
    assert f"/company/{COMPANY_SLUG}/" in html
    assert "Over 100 applicants" in html
    assert "$120/hr - $230/hr" in html
    assert "About the job" in html


def test_the_two_renders_differ_only_in_instrumentation():
    """Otherwise the pair proves nothing -- one file twice is not two renders."""
    pre = markup("pre_hydration")
    hydrated = markup("hydrated")
    assert pre != hydrated
    assert "data-view-name" not in pre
    assert 'data-view-name="job-detail-page"' in hydrated
    assert re.sub(r' data-view-name="[^"]*"', "", hydrated) == pre


def test_the_shell_carries_the_title_and_none_of_the_body():
    """The exact shape of the trap: a real title with nothing behind it."""
    shell = markup("shell")
    assert f"<title>{TITLE} | {COMPANY} | LinkedIn</title>" in shell
    assert "About the job" not in shell
    assert "Over 100 applicants" not in shell


# ---------------------------------------------------------------------------
# 2. Reading the page
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", BOTH_RENDERS)
@pytest.mark.asyncio
async def test_the_employer_comes_from_the_company_link(which):
    identity = await _identity(which)
    assert identity["company"] == COMPANY
    assert identity["company_url"].endswith(f"/company/{COMPANY_SLUG}/")


@pytest.mark.parametrize("which", BOTH_RENDERS)
@pytest.mark.asyncio
async def test_every_field_is_read_from_the_posting(which):
    got = await _detail(which)
    assert got["title"] == TITLE
    assert got["company"] == COMPANY
    assert got["location"] == "India"
    assert got["posted"] == "Reposted 3 days ago"
    assert got["applicants"] == "Over 100 applicants"
    assert got["salary"] == "$120/hr - $230/hr"
    assert got["workplace_type"] == "Remote"
    assert got["employment_type"] == "Contract"
    assert got["status"] == "Actively reviewing applicants"


@pytest.mark.asyncio
async def test_the_two_renders_agree_field_for_field():
    """The property the pair exists to claim, asserted rather than assumed."""
    pre = await _detail("pre_hydration")
    hydrated = await _detail("hydrated")
    assert pre == hydrated


@pytest.mark.parametrize("which", BOTH_RENDERS)
@pytest.mark.asyncio
async def test_the_description_is_the_job_and_stops_being_it(which):
    got = await _detail(which)
    body = got["description"]
    assert body
    # It starts at the posting, not at the heading or the AI panel above it.
    assert "About the job" not in body
    assert "Tailor my resume" not in body
    assert body.startswith("Position: Software Engineer")
    assert "Role Responsibilities" in body
    # And it stops before the page's own trailing furniture.
    assert "About the company" not in body
    assert "Set alert for similar jobs" not in body


# ---------------------------------------------------------------------------
# 3. A title that contains the separator
# ---------------------------------------------------------------------------


def test_the_title_survives_containing_a_pipe():
    """The captured posting is really called "Backend Engineer | Remote".

    Splitting the document title on "|" yields "Backend Engineer" and loses
    the rest, which is why the employer is taken off the END instead.
    """
    got = shape.job_title_from_document_title(
        f"{TITLE} | {COMPANY} | LinkedIn", COMPANY
    )
    assert got == TITLE


def test_the_title_is_not_guessed_when_the_employer_is_unknown():
    """No employer to subtract means no defensible answer, so none is given."""
    document_title = f"{TITLE} | {COMPANY} | LinkedIn"
    assert shape.job_title_from_document_title(document_title, None) is None
    assert shape.job_title_from_document_title("", COMPANY) is None


def test_a_title_that_does_not_carry_the_employer_is_refused():
    """A document title from some other page must not become this job's title."""
    assert shape.job_title_from_document_title("LinkedIn", COMPANY) is None
    assert (
        shape.job_title_from_document_title("Notifications | LinkedIn", COMPANY)
        is None
    )


# ---------------------------------------------------------------------------
# 4. Anchoring: a field is claimed by what it is, never by where it sits
# ---------------------------------------------------------------------------


def _meta(line: str) -> dict:
    return _parse(f"{COMPANY}\n{TITLE}\n{line}\nAbout the job\nwork here\n")


def test_the_metadata_line_is_read_by_identity_not_by_order():
    """The same three facts in a different order must still land correctly."""
    forward = _meta(f"India {DOT} Reposted 3 days ago {DOT} Over 100 applicants")
    shuffled = _meta(f"Over 100 applicants {DOT} India {DOT} Reposted 3 days ago")
    for got in (forward, shuffled):
        assert got["location"] == "India"
        assert got["posted"] == "Reposted 3 days ago"
        assert got["applicants"] == "Over 100 applicants"


def test_a_posting_with_no_applicant_count_does_not_borrow_the_location():
    """A missing fact reads as missing. It never promotes the next one."""
    got = _meta(f"Riverton, Fairhaven, United States {DOT} 2 weeks ago")
    assert got["location"] == "Riverton, Fairhaven, United States"
    assert got["posted"] == "2 weeks ago"
    assert got["applicants"] is None


def test_an_exact_applicant_count_is_read_as_well_as_an_over_count():
    got = _meta(f"India {DOT} 1 day ago {DOT} 47 applicants")
    assert got["applicants"] == "47 applicants"


def test_a_decoration_above_the_metadata_cannot_shift_a_field():
    """The failure class that broke the card parser, run against this one."""
    plain = _parse(
        f"{COMPANY}\n{TITLE}\nIndia {DOT} 3 days ago {DOT} 12 applicants\n"
        "About the job\nwork here\n"
    )
    decorated = _parse(
        f"{COMPANY}\n{COMPANY} with verification\n{TITLE}\nPromoted by hirer\n"
        f"India {DOT} 3 days ago {DOT} 12 applicants\n"
        "About the job\nwork here\n"
    )
    for field in ("title", "company", "location", "posted", "applicants"):
        assert plain[field] == decorated[field], field


def test_the_chips_are_recognised_by_vocabulary_not_by_position():
    got = _parse(
        f"{COMPANY}\n{TITLE}\nIndia {DOT} 3 days ago\n"
        f"Hybrid\nFull-time\n{RUPEE}25,00,000/yr - {RUPEE}35,00,000/yr\n"
        "Apply\nSave\nAbout the job\nwork here\n"
    )
    assert got["workplace_type"] == "Hybrid"
    assert got["employment_type"] == "Full-time"
    assert got["salary"].startswith(RUPEE)


def test_apply_and_save_are_never_mistaken_for_content():
    """Two buttons sit in the middle of the facts. Neither is a fact."""
    got = _parse(
        f"{COMPANY}\n{TITLE}\nIndia {DOT} 3 days ago\nRemote\nContract\n"
        "Apply\nSave\nAbout the job\nwork here\n"
    )
    assert got["employment_type"] == "Contract"
    assert got["description"] == "work here"


# ---------------------------------------------------------------------------
# 5. A page that did not render is a FAILURE, not a sparse posting
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_unrendered_shell_yields_no_posting():
    """The title is right there. It still must not become an answer."""
    identity = await _identity("shell")
    assert identity["company"] is None
    text = await _main_text("shell")
    got = shape.parse_job_detail(
        text,
        company=identity.get("company"),
        document_title=identity.get("document_title"),
    )
    assert got["title"] is None
    assert got["company"] is None
    assert got["description"] is None


def test_an_empty_page_is_not_a_posting():
    got = shape.parse_job_detail("", company=None, document_title=None)
    assert got["title"] is None
    assert got["description"] is None


def test_a_posting_is_only_believable_with_a_title_and_a_body():
    assert not shape.job_detail_is_believable({"title": None, "description": "x"})
    assert not shape.job_detail_is_believable({"title": "x", "description": None})
    assert shape.job_detail_is_believable({"title": "x", "description": "y"})


# ---------------------------------------------------------------------------
# 6. The privacy line
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", BOTH_RENDERS)
@pytest.mark.asyncio
async def test_no_third_party_person_is_read_off_the_posting(which):
    """A posting names recruiters. This reader takes the JOB, not the people.

    LinkedIn renders a hiring-team block and "people also viewed" rows on this
    page. Both are other members. Nothing here extracts either, and this test
    is what stops a later field quietly adding one.
    """
    got = await _detail(which)
    assert set(got) == {
        "title",
        "company",
        "location",
        "posted",
        "applicants",
        "salary",
        "workplace_type",
        "employment_type",
        "status",
        "description",
    }
    for value in got.values():
        assert "/in/" not in str(value)
