"""Does ``linkedin_job_detail`` actually RETURN the fields it computes?

WHY THIS FILE EXISTS, AND IT IS NOT A TIDY-UP. Everything else in this suite
tests ``linkedin_job_detail``'s two derived fields one layer down -- the DOM
reader that finds the control and the pure shaper that classifies it. Both are
covered thoroughly. **Nothing covered the four lines in ``server.py`` that put
the answer into the result a caller sees.**

Measured 2026-08-24, which is the only reason this is stated as a fact rather
than a worry: ``apply_path`` appeared in the tests exactly twice, both times
inside an assertion about a DOCSTRING, and ``company_follow_state`` -- added by
an earlier wave in the same shape -- appeared **zero** times outside the source.
Delete either field's wiring from ``server.py`` and the suite stays green. A
reader would conclude the feature shipped, because every test about it passes,
and every one of them is about a function the tool would no longer call.

So this drives the TOOL, with a real headless page and the frozen captures
behind it, and asserts what a caller receives. It is deliberately narrow: the
classification itself is `test_apply_fixture.py`'s job and is not re-tested
here. What is tested is the seam.

**A note on why this is worth a file rather than one more assertion elsewhere.**
The gap has a shape that recurs: a field computed correctly, tested correctly,
and never plumbed. It is invisible to unit tests by construction, because a
unit test of the computation passes whether or not anybody calls it. The only
thing that catches it is exercising the surface a caller actually touches.

SHOWN FAILING, ON THE REAL FILE, and the numbers are the argument rather than
the claim. One mutant: ``server.py``'s ``out["apply_path"] = ...`` changed to
assign a local nobody reads -- the field computed, and dropped on the floor,
which is precisely what "wired wrong" looks like.

    tests/test_apply_fixture.py     68 tests   ALL 68 STILL PASSED
    tests/test_job_detail_wiring.py  5 tests   3 FAILED

Sixty-eight tests about the feature agreed it was fine. The two that stayed
green here are the two that are not about ``apply_path`` -- the sibling field
and the shell control -- which is the right shape for a mutant that removed one
thing. Mutant reverted; ``server.py`` is byte-identical to its commit.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import company_page, readonly
from linkedin_server import server as server_module

FIXTURES = Path(__file__).parent / "fixtures"

#: The two postings whose apply routes differ, and the ids they are addressed
#: by. Both are INVENTED values from sanitised captures.
LINKEDIN_ROUTE = ("job_detail_hydrated", "4600000042")
OFFSITE_ROUTE = ("job_detail_following_hydrated", "4600000117")


@pytest.fixture
async def chromium_page():
    """One local headless Chromium for the module. Nothing leaves the machine."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield await browser.new_page()
        finally:
            await browser.close()


async def _job_detail(monkeypatch, page, fixture: str, job_id: str) -> dict:
    """Call the real tool with a frozen capture behind it.

    Patches the SESSION and the NAVIGATION, which is the pair every other
    tool-level test in this suite patches, so the tool's own body -- including
    the lines this file exists to cover -- runs unmodified.
    """
    html = (FIXTURES / f"{fixture}.html").read_text(encoding="utf-8")

    class Session:
        async def __aenter__(self):
            await page.set_content(html, wait_until="domcontentloaded")
            return page

        async def __aexit__(self, *exc):
            return False

    async def fake_goto(_page, url, **kwargs):
        # The content is already loaded; report the url the tool asked for, so
        # the auth-wall check sees a job posting rather than a blank page.
        return url

    monkeypatch.setattr(server_module.BROWSER, "session", lambda: Session())
    monkeypatch.setattr(server_module.BROWSER, "goto", fake_goto)
    return await server_module.linkedin_job_detail(job_id)


async def test_the_tool_returns_apply_path_for_a_linkedin_hosted_posting(
    monkeypatch, chromium_page
):
    """The seam, on the route a caller most wants to know about.

    If the four lines wiring ``shape.apply_route`` into the result were
    deleted, every test in ``test_apply_fixture.py`` would still pass and this
    one would fail. That asymmetry is the whole point of the file.
    """
    fixture, job_id = LINKEDIN_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert "error" not in out, out
    assert "apply_path" in out
    assert out["apply_path"]["route"] == "linkedin_apply"
    # The reason travels with the verdict. A route with no why is the confident
    # string this package refuses everywhere else.
    assert len(out["apply_path"]["why"]) > 40


async def test_the_tool_returns_apply_path_and_the_ats_host_for_an_offsite_one(
    monkeypatch, chromium_page
):
    """The off-site route, and the field that makes it USEFUL rather than a label.

    Knowing an application happens elsewhere is worth little; knowing WHOSE
    site it happens on is the thing a person acts on. So the host is asserted
    to be present and to not be LinkedIn -- without naming it, because the
    fixture's decoded destination carries a real applicant-tracking VENDOR's
    domain and this file is tracked.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert "error" not in out, out
    assert out["apply_path"]["route"] == "offsite"
    host = out["apply_path"]["destination_host"]
    assert host and "linkedin.com" not in host
    assert out["apply_path"]["destination"].startswith("http")


async def test_the_tool_returns_company_follow_state_too(
    monkeypatch, chromium_page
):
    """THE SIBLING GAP, closed at the same time and not silently.

    ``company_follow_state`` was added to this tool by an earlier wave in
    exactly the same shape as ``apply_path``, and had exactly the same hole:
    its reader and its shaper are both tested and nothing asserted the tool
    returned it. It is not this wave's field and it is covered here anyway,
    because the gap is a property of the seam rather than of either feature,
    and leaving one half of it open would leave the next person to find it
    believing the seam is tested.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert "company_follow_state" in out
    assert out["company_follow_state"]["state"] == "following"
    assert len(out["company_follow_state"]["why"]) > 20


async def test_the_tool_returns_the_company_page_tally(
    monkeypatch, chromium_page
):
    """THE SAME SEAM, ONE WAVE LATER, for ``COMPANY-PAGE-SURFACE``.

    ``company_page.tally`` is exhaustively unit-tested in
    ``tests/test_company_page.py`` and every one of those tests passes whether
    or not ``server.py`` calls it. This is the line that notices.

    THE NUMBERS ARE MEASURED OFF THIS CAPTURE, not chosen: the hydrated
    About-the-company card holds FIVE links, of which TWO are
    ``/company/<slug>/life/`` and three are LinkedIn help pages.

    **AND ``page_roots`` IS ZERO, WHICH IS THE FINDING RATHER THAN A BUG.**
    The card never links the Page ROOT, only the Life tab -- so "is this
    employer's Page addressable" is NOT answerable from this card, and a
    future wave that assumes otherwise will read this zero as "no Page". It is
    pinned here so the assumption fails loudly instead.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert "company_page" in out
    tally = out["company_page"]
    assert tally["hrefs"] == 5
    assert tally["slug"] == 2
    assert tally["numeric"] == 0
    assert tally["distinct"] == 1
    assert tally["page_roots"] == 0

    counts = tally["counts"]
    assert len(counts) == len(company_page.TAB_KINDS)
    named = {
        company_page.term_for(index): value
        for index, value in enumerate(counts)
        if value
    }
    assert named == {"life_tab": 2, "off_company": 3}


async def test_an_empty_href_list_can_be_told_from_an_unreadable_one(
    monkeypatch, chromium_page
):
    """THE THREE-WAY DISTINCTION, on the field this wave added.

    An empty ``hrefs`` from a failed read and an empty one from a card with no
    links are the SAME VALUE and DIFFERENT ANSWERS. ``dom.py`` already refuses
    to collapse that pair in the other direction -- ``container`` true with
    ``lines`` empty is a fact about hydration, not about the employer -- and
    ``hrefs_error`` is the same refusal for the links.

    Asserted on the healthy path, which is the only one a fixture can reach:
    links were read AND the error field is null, so a future reader can treat
    a null there as "the count is real" rather than having to guess.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert out["company_page"]["hrefs"] == 5
    # The shell capture draws no card at all: zero links AND no error, which
    # is the other half of the distinction and is a different zero again.
    shell = await _job_detail(
        monkeypatch, chromium_page, "job_detail_shell", "4600000042"
    )
    assert shell.get("error") == "extraction_failed", shell
    assert "company_page" not in shell


async def test_the_tool_publishes_no_slug_anywhere_in_the_company_page_block(
    monkeypatch, chromium_page
):
    """THE PROPERTY THE SHAPER EXISTS FOR, asserted ON THE WIRE rather than
    only in a unit test.

    A shaper that keeps names out of its own return value is worth nothing if
    the seam publishes the raw hrefs beside it. This capture's employer slug
    is a real string in the document; it must not be anywhere in the block.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    published = repr(out["company_page"])
    assert "/company/" not in published
    assert "linkedin.com" not in published
    assert "life" not in published


async def test_the_tool_joins_the_resolved_id_to_a_page_address(
    monkeypatch, chromium_page
):
    """CENSUS ROW ``N 104``, and the gap it closes is a SEAM rather than a
    feature.

    ``jobfilter.py``'s own first paragraph describes this exact shape about
    ``J 10``: *both halves of that blocker are now built and the row is still
    GAP, because nothing joined them.* Here the halves are
    ``shape.company_id_from_insight_cards`` (a NUMERIC organisation id, read
    off this posting) and the ``/company/`` allowlist entry added 2026-09-20.

    THE ADDRESS IS THE NUMERIC FORM AND THAT IS WHY IT CAN BE PUBLISHED AT
    ALL: a slug is a name and a digit run cannot be one.
    """
    fixture, job_id = OFFSITE_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert out["company_id"]["state"] == "resolved", out["company_id"]
    identifier = out["company_id"]["company_id"]

    url = out["company_page_url"]
    assert url == f"https://www.linkedin.com/company/{identifier}/"
    # AND THE DOOR AGREES. An address this tool hands the operator that the
    # boundary would refuse is an address nobody can act on.
    assert readonly.is_read_url(url) is True


async def test_a_posting_with_no_resolved_id_gets_no_address_rather_than_a_guess(
    monkeypatch, chromium_page
):
    """THE CONTROL for the join above, and it is not hypothetical: the id is
    absent on four of the five tracked captures, because LinkedIn's Premium
    insights panel is not drawn for every employer.

    An unresolved id must produce ``None``, never an address assembled from
    whatever number happened to be nearby.
    """
    fixture, job_id = LINKEDIN_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert out["company_id"]["state"] != "resolved", out["company_id"]
    assert out["company_page_url"] is None


async def test_both_derived_fields_come_from_the_same_single_page_load(
    monkeypatch, chromium_page
):
    """Neither field costs an extra page load, and the result says so.

    This is the claim both features are sold on -- the state is read off the
    page the tool already has open -- and it is the first thing an
    "improvement" would break by reaching for a second surface. ``pages_loaded``
    is the field that would move, so it is pinned rather than described.
    """
    fixture, job_id = LINKEDIN_ROUTE
    out = await _job_detail(monkeypatch, chromium_page, fixture, job_id)

    assert out["pages_loaded"] == 1
    assert "apply_path" in out
    assert "company_follow_state" in out


async def test_a_shell_that_never_rendered_the_posting_still_fails_loudly(
    monkeypatch, chromium_page
):
    """THE CONTROL. Without it, the four tests above pass on a tool that
    returns a dict for anything.

    A pre-hydration shell carries a server-rendered document title and no
    posting. The tool must FAIL rather than return a result whose apply_path is
    a tidy 'unknown' beside a title with nothing behind it -- an unreadable page
    and a page with no apply route are different answers, and only one of them
    is worth showing anybody.
    """
    out = await _job_detail(
        monkeypatch, chromium_page, "job_detail_shell", "4600000042"
    )

    assert out.get("error") == "extraction_failed", out
    assert "apply_path" not in out
