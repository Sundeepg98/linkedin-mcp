"""The reader for what "Show more analytics" reveals, against fixtures shaped like
the live capture (``_audit/2026-09-23-live-lane-session-1.md`` Entry 7).

The live capture itself is gitignored and holds other people's data, so the
fixture below is SYNTHETIC: the same structure -- a heading, value/label
pairs, "<name> (<n>%)" entries -- with invented tokens. Offline, the reader
was also run against the real capture and read it exactly (2 sections, 3
highlight values, 5 entries, 0 unparsed), which is recorded in that entry and
not re-proven here.
"""
from __future__ import annotations

import asyncio

import pytest

from linkedin_server import profile_views_more as pvm

HIGHLIGHTS = ["Highlights", "Alpha Region Omega", "Top location",
              "Beta Sector", "Top industry", "Gamma Works", "Top company"]
DETAILS = ["Details", "Companies", "Gamma Works (13.3%)", "Delta Group (6.7%)",
           "Epsilon Labs (6.7%)"]


def test_highlights_pair_each_value_with_the_label_after_it():
    values, unparsed = pvm.parse_highlights(HIGHLIGHTS)
    assert values == {"top_location": "Alpha Region Omega", "top_industry": "Beta Sector",
                      "top_company": "Gamma Works"}
    assert unparsed == 0


def test_a_missing_label_is_none_and_a_stray_line_is_counted():
    values, unparsed = pvm.parse_highlights(["Highlights", "Beta Sector", "Top industry", "a stray line"])
    assert values["top_industry"] == "Beta Sector"
    assert values["top_location"] is None and values["top_company"] is None
    assert unparsed == 1


def test_details_read_the_heading_and_every_entry():
    parsed, unparsed = pvm.parse_details(DETAILS)
    assert parsed["heading"] == "companies"
    assert parsed["entries"] == [
        {"name": "Gamma Works", "percent": 13.3},
        {"name": "Delta Group", "percent": 6.7},
        {"name": "Epsilon Labs", "percent": 6.7},
    ]
    assert unparsed == 0


@pytest.mark.parametrize("line", ["Gamma Works 13.3%", "Gamma Works (13.3)", "(13.3%)", "Gamma Works (1234%)"])
def test_a_line_that_is_not_an_entry_is_counted_never_guessed(line):
    parsed, unparsed = pvm.parse_details(["Details", "Companies", line])
    assert parsed["entries"] == [] and unparsed == 1


def _fixture(sections: str) -> str:
    return (
        "<html><body><header><h2>Highlights</h2><div>not in main</div></header>"
        "<main><section><h1>Who viewed your profile</h1></section>" + sections + "</main></body></html>"
    )


def _section(title: str, lines: list[str]) -> str:
    inner = "".join("<div><span>" + line + "</span></div>" for line in lines[1:])
    return "<section><div><h2>" + title + "</h2></div><div>" + inner + "</div></section>"


def _read(html: str) -> dict:
    from playwright.async_api import async_playwright

    async def go():
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.route("**/*", lambda route: route.abort())
                await page.set_content(html, wait_until="domcontentloaded")
                return await pvm.read_profile_views_more_insights(page)
            finally:
                await browser.close()

    return asyncio.run(go())


def test_the_revealed_page_is_read_whole():
    out = _read(_fixture(_section("Highlights", HIGHLIGHTS) + _section("Details", DETAILS)))
    assert out["sections_found"] == ["highlights", "details"]
    assert out["highlights"]["top_company"] == "Gamma Works"
    assert [e["percent"] for e in out["details"]["entries"]] == [13.3, 6.7, 6.7]
    assert out["unparsed_lines"] == 0


def test_the_unrevealed_page_reports_nothing_found_not_an_empty_reading():
    out = _read(_fixture(""))
    assert out == {"sections_found": [], "highlights": None, "details": None, "unparsed_lines": 0}


def test_a_heading_outside_main_is_not_read():
    out = _read(_fixture(_section("Details", DETAILS)))
    assert out["sections_found"] == ["details"], "the header's Highlights was read"
