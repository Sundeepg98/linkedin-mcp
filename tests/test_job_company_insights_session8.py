"""Census row ``J 124`` -- Premium AI company intelligence on a posting -- read off session 8's posting.

WHAT THE ROW IS. "Premium AI company intelligence (headcount, openings,
strategic priorities)" (``_audit/_census/jobs.md`` row 124). Its cell said
the candidates disagreed and the class waited on a live look. Live session 8
(2026-10-10, load 17) kept one posting raw, and lane B4 MEASURED it: the
posting draws a block opening ``Insights about the company``, whose ``h2`` is
the shipped panel heading (``dom.JOB_COMPANY_PANEL_PREFIX`` + the employer),
then ``Powered by Bing``, then ``Company focus areas`` (a titled focus area
and its summary -- the strategic priorities), ``Hiring & headcount`` (a
summary -- the hiring), and the figures ``Total employees``, ``2 year
growth``, ``Company-wide`` and ``Median employee tenure:`` -- the headcount.

THE FIXTURE is ``tests/fixtures/live8/posting.html``, the tracked skeleton of
that capture (``scripts/_build_live8_posting_skeleton.py``): LinkedIn's words
kept, the AI prose replaced by invented sentences, every figure replaced in
format. So everything below is aimed at REAL captured markup.

WHAT THE SHIPPED READER DID ON THIS MARKUP, MEASURED by running it offline over
the RAW capture (counts and LinkedIn's words only were printed): 21 lines,
carrying ``Company focus areas``, ``Hiring & headcount``, ``Total employees``,
``Company-wide`` and ``2 year growth`` -- so the three payloads already came
back -- and two defects, shown red first here:

1. THE PANEL WAS CUT BEFORE ITS TENURE LINE. The panel shares the 24-line cap
   of the applicant panels, counted before the chart's screen-reader lines are
   dropped, and on this markup the run is longer: ``Median employee tenure``
   never came back.
2. NONE OF THE THIRD-PARTY-TEXT-AT-RUNTIME MITIGATIONS. The panel's lines are
   LinkedIn's AI-written prose about an organisation, returned at runtime:
   not marked untrusted, not sanitised, not bounded per line.

AND ONE THING THE FIXTURE HAD TO BE TAUGHT. ``tracked_copy`` makes every keyed
text one ``x``, so every keyed heading EQUALLED every keyed body line, and the
reader -- bounded by "the next heading" -- stopped at the first ``x`` line. The
builder now writes a heading's keyed text as ``Example heading``
(``SYNTHETIC_HEADING``), distinct from body lines as headings are live.

Nothing here reaches the network: a local headless Chromium over the tracked
fixture and over worlds derived from it by asserted edits.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, people_data

FIXTURE = Path(__file__).parent / "fixtures" / "live8" / "posting.html"
BASE = FIXTURE.read_text(encoding="ascii")

#: The builder's declared synthetic values, as they stand in the fixture.
FOCUS_TITLE = "Example focus area"
FOCUS_SUMMARY_START = "Example focus area summary: an invented sentence"
HIRING_SUMMARY = (
    "Example hiring summary: an invented sentence standing where the page "
    "drew its account of hiring and headcount, written for this fixture."
)
EMPLOYER = "Example Org"


def _derive(old: str, new: str, *, source: str = BASE) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op."""
    derived = source.replace(old, new, 1)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


@pytest.fixture
async def chromium_page():
    """A local headless Chromium whose page serves itself NOTHING from outside:
    the tracked skeleton keeps the capture's stylesheet and image addresses
    (reduced to ``https://x/...``), and every request they would start is
    aborted by the page's own route, before the network guard has to."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()

            async def _refuse(route):
                await route.abort()

            await page.route("**/*", _refuse)
            yield page
        finally:
            await browser.close()


async def _company(page, markup: str = BASE) -> dict:
    await page.set_content(markup, wait_until="domcontentloaded")
    panels = await dom.read_job_insight_panels(page)
    company = panels["company_insights"]
    assert company is not None, panels["observed"]
    return company


async def test_the_three_payloads_come_back_off_session_8s_markup(chromium_page):
    """Strategic priorities, hiring and headcount: all three, in the panel."""
    lines = (await _company(chromium_page))["lines"]

    assert "Company focus areas" in lines
    assert any(line.startswith(FOCUS_TITLE) and FOCUS_SUMMARY_START in line for line in lines)
    assert "Hiring & headcount" in lines
    assert any(line.startswith(HIRING_SUMMARY) for line in lines)
    # THE HEADCOUNT.
    assert "Total employees" in lines and "1,234" in lines
    assert "2 year growth" in lines
    # THE TENURE -- red on the shipped reader, whose shared 24-line cap cut
    # the panel before it on this markup (and on the raw capture).
    assert any(line.startswith("Median employee tenure") for line in lines)
    # The panel's boundaries, as the August test holds them.
    assert "Powered by Bing" not in lines
    assert "Show Premium Insights" not in lines
    assert "Chart" not in lines and "End of interactive chart." not in lines
    assert "About the company" not in lines


async def test_the_panel_is_marked_as_third_party_text(chromium_page):
    company = await _company(chromium_page)

    assert company[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    assert company["truncated"] is False


async def test_an_over_long_line_is_cut_and_says_so(chromium_page):
    long_summary = "Example long summary sentence. " * 200
    world = _derive(HIRING_SUMMARY, long_summary.strip())
    company = await _company(chromium_page, world)

    longest = max(len(line) for line in company["lines"])
    assert longest <= dom.JOB_COMPANY_LINE_CAP
    assert company["truncated"] is True


async def test_invisible_and_direction_characters_are_removed(chromium_page):
    planted = "Example" + "&#8203;" + " focus" + "&#8238;" + " area"
    world = _derive(FOCUS_TITLE + "\n</strong>", planted + "\n</strong>")
    lines = (await _company(chromium_page, world))["lines"]

    joined = "\n".join(lines)
    assert chr(0x200B) not in joined and chr(0x202E) not in joined
    assert any(line.startswith("Example focus area") for line in lines)


async def test_the_employer_never_rides_in_a_line(chromium_page):
    """The panel heading carries the employer; a line repeating it is shaped."""
    world = _derive(HIRING_SUMMARY, EMPLOYER + " grew its teams; " + HIRING_SUMMARY)
    company = await _company(chromium_page, world)

    assert company["heading"] == dom.JOB_COMPANY_PANEL_SHAPE
    assert not any(EMPLOYER in line for line in company["lines"])
    assert any(line.startswith("<company> grew its teams;") for line in company["lines"])


async def test_every_line_is_its_own_sanitised_form(chromium_page):
    """Idempotence, which is what lets a consumer check it: sanitising a
    returned line again changes nothing."""
    for line in (await _company(chromium_page))["lines"]:
        assert line == people_data.sanitise(line, cap=dom.JOB_COMPANY_LINE_CAP)
