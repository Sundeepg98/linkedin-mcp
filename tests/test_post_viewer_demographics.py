"""Pins for ``linkedin_server.post_viewer_demographics`` -- the viewer-
demographics half of census row ``M C38`` -- over the TRACKED skeleton of the
per-post analytics page the live lane's session 1 captured,
``tests/fixtures/live1/post_summary.html`` (built by
``scripts/_build_live1_l1_fixtures.py``).

WHAT THE SKELETON DRAWS, measured (lane B3, 2026-10-10): one card titled
"Top demographics"; a nav of seven buttons, "All" marked ``aria-current`` and
the six category words; five rows, each a category word, a VALUE and a
percentage beside a ``role=progressbar`` whose ``aria-valuenow`` carried the
same number. In the tracked copy every value and every number is ``x``: they
are his post's audience, and other people's data however aggregated.

SO THE REAL SKELETON PROVES THE STRUCTURE AND NOTHING ELSE: card, categories,
selected tab and five rows found, and NO point read -- ``readable`` False with
``labels_seen`` 5, which is exactly the creator-analytics semantics for a page
whose shape held but whose numbers did not parse. The points are read on a
COPY with SYNTHETIC values planted in the five rows, and those values are
chosen to exercise the shaper: one of them is the reader-leak guard's own
name-shaped plant.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from linkedin_server import post_viewer_demographics as demographics
from tests.plantedpage import PLANT

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "live1" / "post_summary.html"

CATEGORIES = ["Job title", "Location", "Seniority", "Company", "Industry", "Company size"]

#: Synthetic rows, planted by category: (value, percentage). Declared here.
SYNTHETIC = {
    "Seniority": ("Entry", 34),
    "Industry": ("Example Industry Services", 21),
    "Job title": (PLANT, 12),
    "Company size": ("1,001-5,000 employees", 9),
    "Location": ("Exampletown, Exampleregion", 7),
}

#: What each synthetic value must leave as, pinned by hand rather than
#: recomputed through the shaper: a one-word value survives (the shaper's
#: documented residual gap), a run of two or more capitalised words is
#: redacted, digits and lower case pass.
SHAPED = {
    "Seniority": "Entry",
    "Industry": "<redacted>",
    "Job title": "<redacted>",
    "Company size": "1,001-5,000 employees",
    "Location": "Exampletown, <redacted>",
}

#: One row as the tracked copy writes it: the category word, the value, the
#: percentage, then the progressbar's attributes up to aria-valuenow.
_ROW = (
    r'(<p class="[^"]*">\n){category}(\n</p>\n<div class="[^"]*">\n<p class="[^"]*">\n)x'
    r'(\n</p>\n<p class="[^"]*">\n)x(\n</p>\n</div>\n<div class="[^"]*">\n<svg [^>]*?aria-valuenow=")x(")'
)


def _planted(html: str, rows: dict) -> str:
    for category, (value, percent) in rows.items():
        pattern = re.compile(_ROW.format(category=re.escape(category)))
        html, count = pattern.subn(
            lambda m, v=value, p=percent: (
                m.group(1) + category + m.group(2) + v + m.group(3) + str(p) + "%"
                + m.group(4) + str(p) + m.group(5)
            ),
            html,
        )
        assert count == 1, f"the skeleton no longer draws exactly one {category!r} row"
    return html


async def _refused(route) -> None:
    await route.abort()


async def _read(html: str):
    """Load ``html`` into a throwaway headless page and read it; the page's
    own route refuses every request the skeleton's shaped addresses make."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.route("**/*", _refused)
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await demographics.read_post_viewer_demographics(page)
        finally:
            await browser.close()


async def test_the_real_skeleton_draws_the_structure_and_no_point():
    reading = await _read(FIXTURE.read_text(encoding="utf-8"))
    assert reading["card_found"] is True
    assert reading["categories"] == CATEGORIES
    assert reading["selected"] == "All"
    assert reading["labels_seen"] == 5
    assert reading["points_found"] == 0
    assert reading["readable"] is False
    assert reading["rows"] == []
    assert reading["unparsed_rows"] == 5
    assert reading["unrecognised_categories"] == 0


async def test_synthetic_rows_on_a_copy_of_the_real_skeleton_are_read_and_shaped():
    reading = await _read(_planted(FIXTURE.read_text(encoding="utf-8"), SYNTHETIC))
    assert reading["readable"] is True
    assert reading["points_found"] == 5
    assert reading["labels_seen"] == 5
    assert reading["unparsed_rows"] == 0
    assert reading["percent_disagreements"] == 0
    # Page order, measured: Seniority, Industry, Job title, Company size, Location.
    assert reading["rows"] == [
        {"category": c, "value": SHAPED[c], "percent": SYNTHETIC[c][1]}
        for c in ("Seniority", "Industry", "Job title", "Company size", "Location")
    ]


async def test_the_name_shaped_plant_never_leaves_and_no_value_leaves_unshaped():
    reading = await _read(_planted(FIXTURE.read_text(encoding="utf-8"), SYNTHETIC))
    flat = repr(reading)
    for word in PLANT.split():
        assert word not in flat
    for category, (value, _) in SYNTHETIC.items():
        if SHAPED[category] != value:
            assert value not in flat, category


async def test_a_percentage_the_progressbar_contradicts_is_not_a_point():
    rows = dict(SYNTHETIC)
    html = _planted(FIXTURE.read_text(encoding="utf-8"), rows)
    # The Location row's text says 7%; make its progressbar say 70.
    html = html.replace('aria-valuenow="7"', 'aria-valuenow="70"', 1)
    reading = await _read(html)
    assert reading["points_found"] == 4
    assert reading["percent_disagreements"] == 1
    assert [row["category"] for row in reading["rows"]] == [
        "Seniority", "Industry", "Job title", "Company size",
    ]


async def test_a_page_without_the_card_title_is_not_found():
    html = FIXTURE.read_text(encoding="utf-8").replace("Top demographics", "x")
    reading = await _read(html)
    assert reading["card_found"] is False
    assert reading["readable"] is False
    assert reading["labels_seen"] == 0
    assert reading["rows"] == []


def test_percent_of_reads_only_the_measured_shape():
    assert demographics.percent_of("34%") == 34
    assert demographics.percent_of(" 7 % ") == 7
    assert demographics.percent_of("100%") == 100
    for refused in (None, "", "x", "34", "101%", "3.5%", "-4%", PLANT, chr(0x0663) + "4%", "1000%"):
        assert demographics.percent_of(refused) is None, refused


def test_shaped_value_is_census_shape_then_redact_rare_at_count_one():
    assert demographics.shaped_value("Entry") == "Entry"
    assert demographics.shaped_value(PLANT) == "<redacted>"
    assert demographics.shaped_value("x" * 61) == "<opaque>"
    assert demographics.shaped_value("10,001+ employees") == "<opaque>"
    assert demographics.shaped_value("") == ""
    assert demographics.shaped_value(None) == ""
