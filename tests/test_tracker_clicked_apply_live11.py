"""His job tracker's clicked_apply stage, read over the stage's REAL capture (census J 52).

Lane readers-jobs26, 2026-11-26. ``linkedin_tracker_stage(stage="clicked_apply")``
was built by lane A on 2026-10-10 over captures of the tracker that drew NO
clicked_apply tab, so whether that stage renders anything the tracker's reader
can read was unmeasured, and ``J 52`` stayed GAP on exactly that. Session 11
loaded ``/jobs-tracker/?stage=clicked_apply`` (load 12) and its skeleton is
tracked as ``tests/fixtures/live11/tracker_clicked_apply.html``;
``tracker_clicked_apply_words.html`` is the same skeleton with eight of
LinkedIn's words written where their keyed shapes matched
(``scripts/_build_live11_word_skeletons.py``).

WHAT THE CAPTURE DRAWS, MEASURED: the tab strip, twice, reading
``Saved <dot> 0``, ``Clicked apply <dot> 0`` (its pill checked), ``Applied
<dot> 0``, ``Interview <dot> 0`` and ``Archived``; one ``h2`` reading ``No
matches``; no job row. So the stage IS drawn with a count, and the tracker's
own zero rule -- believed only when LinkedIn's count says zero AND the page
draws its empty state -- is met on the real page: a corroborated empty list.

The tests run the SHIPPED reader end to end (``server._read_tracker`` through
the tool) in a local headless Chromium over that markup, and show the words are
the anchor: the same capture with its words reduced is a failed read, and a
count planted above zero with no row is a failed read too.

Every string planted here is synthetic.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, shape
from linkedin_server import server as server_module
from linkedin_server.server import linkedin_tracker_stage
from tests.live11_words import body_lines, chromium_page, plain, plant, words  # noqa: F401

STEM = "tracker_clicked_apply"
URL = "https://www.linkedin.com/jobs-tracker/?stage=clicked_apply"
DOT = chr(0xB7)

#: The eight words the builder declares for this fixture, as the markup holds them.
DECLARED = (
    "Job tracker", "0 selected", "Saved &#183; 0", "Clicked apply &#183; 0",
    "Applied &#183; 0", "Interview &#183; 0", "Date posted", "No matches",
)


def _drive(monkeypatch, page, markup: str) -> list[str]:
    """Hand the tool a real page already holding ``markup``; record each goto."""
    navigations: list[str] = []

    @asynccontextmanager
    async def fake_session():
        yield page

    async def fake_goto(target_page, url, **kwargs):
        navigations.append(url)
        await target_page.set_content(markup, wait_until="domcontentloaded")
        return url

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    return navigations


# ---------------------------------------------------------------------------
# 1. The fixture is the capture, with its measured words and nothing else
# ---------------------------------------------------------------------------


def test_the_words_fixture_differs_from_the_capture_only_by_its_declared_words():
    fixture = body_lines(words(STEM))
    capture = plain(STEM).split("\n")[1:]
    assert len(fixture) == len(capture)
    differing = [(a, b) for a, b in zip(fixture, capture) if a != b]
    assert len(differing) == 13
    for written, reduced in differing:
        undone = written
        for word in DECLARED:
            undone = undone.replace(">" + word + "<", ">x<").replace(word, "x")
        assert undone == reduced


# ---------------------------------------------------------------------------
# 2. What the stage's page says, read by the shipped helpers
# ---------------------------------------------------------------------------


async def test_the_stage_draws_its_own_tab_with_a_count_and_its_empty_state(chromium_page):
    await chromium_page.set_content(words(STEM), wait_until="domcontentloaded")
    text = await dom.read_main_text(chromium_page)
    assert shape.parse_tracker_tabs(text) == {
        "saved": 0, "clicked_apply": 0, "applied": 0, "interview": 0,
    }
    assert shape.tracker_empty_state(text) == "No matches"
    wait = await dom.wait_for_tracker_list(chromium_page)
    assert wait["attached"] is True, wait
    records = await dom.harvest_linked_cards(chromium_page, href_pattern=dom.JOB_HREF, max_items=75)
    assert records == []


async def test_with_its_words_reduced_the_same_capture_reads_no_tab(chromium_page):
    """THE CONTROL: the words are the anchor. The committed copy draws the same
    markup with every word ``x``, and the strip reads nothing."""
    await chromium_page.set_content(plain(STEM), wait_until="domcontentloaded")
    text = await dom.read_main_text(chromium_page)
    assert shape.parse_tracker_tabs(text) == {}
    assert shape.tracker_empty_state(text) is None


# ---------------------------------------------------------------------------
# 3. The tool, end to end, over the real markup
# ---------------------------------------------------------------------------


async def test_the_tool_reads_a_corroborated_empty_clicked_apply_list(monkeypatch, chromium_page):
    navigations = _drive(monkeypatch, chromium_page, words(STEM))

    result = await linkedin_tracker_stage("clicked_apply", limit=25)

    assert "error" not in result, result
    assert navigations == [URL]
    assert result["count"] == 0
    assert result["empty"] is True
    assert result["linkedin_count"] == 0
    assert result["empty_state"] == "No matches"
    assert result["tab"] == server_module.TRACKER_STAGES_LANE_A["clicked_apply"]
    assert result["tab_counts"]["clicked_apply"] == 0


async def test_the_same_capture_with_its_words_reduced_is_a_failed_read(monkeypatch, chromium_page):
    """Nothing corroborates the zero, so it is reported as a failure, never as none."""
    _drive(monkeypatch, chromium_page, plain(STEM))

    result = await linkedin_tracker_stage("clicked_apply", limit=25)

    assert result.get("error") == "extraction_failed", result
    assert result.get("empty") is None


async def test_a_count_above_zero_with_no_row_is_a_failed_read(monkeypatch, chromium_page):
    """LinkedIn's count says three and no row was read: not an empty list."""
    markup = plant(words(STEM), "Clicked apply &#183; 0", "Clicked apply &#183; 3", 2)
    _drive(monkeypatch, chromium_page, markup)

    result = await linkedin_tracker_stage("clicked_apply", limit=25)

    assert result.get("error") == "extraction_failed", result


async def test_an_empty_state_with_no_count_for_the_stage_is_a_failed_read(monkeypatch, chromium_page):
    """The empty state alone does not corroborate a zero: the strip must count it."""
    markup = plant(words(STEM), "Clicked apply &#183; 0", "x", 2)
    _drive(monkeypatch, chromium_page, markup)

    result = await linkedin_tracker_stage("clicked_apply", limit=25)

    assert result.get("error") == "extraction_failed", result
