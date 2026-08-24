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
