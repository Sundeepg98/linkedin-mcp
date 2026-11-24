"""``set_tracker_stage`` -- census row ``J 54`` -- built to REFUSE, and why.

WHAT THE ACTION IS. Move one job on his Saved tab to another stage of his job
tracker. SANCTIONED AND NOT PERFORMABLE (lane builds-26, 2026-11-24), the
shape ``set_open_to_work`` stands in: the control it would press -- an item
in the row's ``Overflow menu`` -- has never been captured, so no grant can
exist for it, and its preview is a warning that reads the Saved tab live and
names the capture that would lift the refusal.

WHAT IS MEASURED, so no test claims more. The one populated tracker capture,
``tests/fixtures/jobs_tracker_row.html``, draws the tab strip's five stage
words and, on each of its two row copies, one closed ``Overflow menu`` with an
empty item slot. The Saved-tab world the preview reads is
``tests.test_writes.SAVED_LIST_OF_ONE``: that capture with LinkedIn's own
Saved count edited 0 -> 1 (DERIVED, as that file says), so the one row it
draws reconciles as a saved job.

NOTHING HERE REACHES LINKEDIN. Pages are served into a local headless
Chromium by the navigator ``tests/test_writes.py`` owns.
"""
from __future__ import annotations

import asyncio

import pytest

from linkedin_server import server, tracker_stage, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import mint, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    JOB,
    SAVED_JOB,
    SAVED_LIST_OF_ONE,
    SAVED_LIST_PARTIAL,
    FixtureNavigator,
    browser_page,
    markup,
    writes_on,
)

ACTION = "set_tracker_stage"
SPEC = spec_for_action(ACTION)
CAPTURE = markup("jobs_tracker_row")


# ---------------------------------------------------------------------------
# 1. The vocabulary and the measured ground
# ---------------------------------------------------------------------------


def test_the_stage_words_are_the_tab_strip_s_own():
    """Every stage word is drawn by the capture, as a tab label, as written."""
    for word in tracker_stage.TRACKER_TAB_WORDS:
        assert f">{word}" in CAPTURE, word
    assert tracker_stage.TRACKER_STAGES == tuple(
        w.casefold() for w in tracker_stage.TRACKER_TAB_WORDS
    )


def test_the_capture_draws_a_closed_menu_and_no_item():
    """THE REFUSAL'S GROUND, pinned to the capture it was measured on. If a
    capture of an OPENED row menu ever replaces this file, this fails and the
    refusal has to be re-read rather than kept."""
    assert CAPTURE.count('aria-label="Overflow menu"') == 2
    assert CAPTURE.count('aria-label="Overflow menu" aria-expanded="false"') == 2
    for word in ("Move to", "Mark as", "Change stage"):
        assert word not in CAPTURE, word


@pytest.mark.parametrize("word", ["applied", "Applied", " interview ", "ARCHIVED", "draft"])
def test_a_drawn_stage_other_than_saved_is_admitted(word):
    stage, why = tracker_stage.checked_stage(word)
    assert stage == word.strip().casefold() and why == ""


@pytest.mark.parametrize("word", ["saved", "Saved", "promoted", "", "x" * 40, None])
def test_anything_else_is_refused_without_being_repeated(word):
    stage, why = tracker_stage.checked_stage(word)
    assert stage is None
    assert why
    if word and word.strip().casefold() not in ("saved", ""):
        assert str(word) not in why


# ---------------------------------------------------------------------------
# 2. Sanctioned, refusing, and saying why
# ---------------------------------------------------------------------------


def test_the_spec_is_sanctioned_and_cannot_hold_a_grant(writes_on):
    assert SPEC.tool_name == "linkedin_set_tracker_stage"
    assert ACTION not in writes.PERFORMABLE
    assert SPEC.url_template is None and SPEC.url_pattern is None
    assert writes.grant_is_possible(SPEC) is False
    with pytest.raises(WriteAttemptError) as caught:
        mint(ACTION, SAVED_JOB, receipt="anything")
    assert "no grant is minted for" in str(caught.value)


def test_the_refusal_is_its_own_and_names_the_capture_that_lifts_it():
    with pytest.raises(WriteAttemptError) as caught:
        writes._refuse_unperformable(SPEC)
    reason = str(caught.value)
    assert "WHAT WOULD LIFT IT" in reason
    assert "/jobs-tracker/?stage=saved" in reason
    assert "OPENED overflow menu" in reason
    assert "is not performable. The complete performable set is" not in reason


# ---------------------------------------------------------------------------
# 3. The preview reads the Saved tab, once, and mints nothing
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_saved_tab_and_issues_no_token(writes_on, browser_page):
    nav = FixtureNavigator({writes.SAVED_LIST_URL: SAVED_LIST_OF_ONE})
    block = await preview(SPEC, target=SAVED_JOB, navigator=nav, page=browser_page)
    assert nav.gotos == [writes.SAVED_LIST_URL]
    assert block["to_confirm"] is None
    assert block["performed"] is False
    assert "NO CONFIRM TOKEN IS ISSUED" in block["what_happens_next"]
    assert block["direction"]["currently"] == "saved"
    assert block["where"]["job_id"] == SAVED_JOB
    assert writes._GRANTS == {}


async def test_a_job_the_saved_tab_does_not_list_is_refused(writes_on, browser_page):
    nav = FixtureNavigator({writes.SAVED_LIST_URL: SAVED_LIST_OF_ONE})
    with pytest.raises(WriteAttemptError) as caught:
        await preview(SPEC, target=JOB, navigator=nav, page=browser_page)
    message = str(caught.value)
    assert "valid only from 'saved'" in message
    assert "refused rather than looked for elsewhere" in message


async def test_absence_from_a_partial_list_reads_unknown_not_absent(writes_on, browser_page):
    """The tab says 9 and draws 1: a job missing from what was drawn may be in
    the 8 that were not, so it reads ``unknown`` and the preview refuses --
    never a wrong-state 'not saved'. (A job PRESENT on a partial list is
    present, and reads saved: presence needs no count.)"""
    nav = FixtureNavigator({writes.SAVED_LIST_URL: SAVED_LIST_PARTIAL})
    with pytest.raises(WriteAttemptError) as caught:
        await preview(SPEC, target=JOB, navigator=nav, page=browser_page)
    assert "came back 'unknown'" in str(caught.value)


# ---------------------------------------------------------------------------
# 4. The tool: the destination is checked before anything loads
# ---------------------------------------------------------------------------


def test_the_tool_refuses_an_unknown_stage_before_any_page_loads(monkeypatch):
    def _never(*_args, **_kwargs):
        raise AssertionError("the write path was reached for a refused stage")

    monkeypatch.setattr(server, "_write_tool", _never)
    out = asyncio.run(server.linkedin_set_tracker_stage(job_id=SAVED_JOB, stage="promoted"))
    assert out["error"] == "unknown_stage"
    assert out["pages_loaded"] == 0 and out["performed"] is False
    assert "promoted" not in out["message"]


def test_the_tool_prints_the_destination_beside_the_warning(monkeypatch):
    seen = {}

    async def _fake(action, target, confirm_token):
        seen.update(action=action, target=target)
        return {"action": action, "to_confirm": None, "performed": False}

    monkeypatch.setattr(server, "_write_tool", _fake)
    out = asyncio.run(server.linkedin_set_tracker_stage(job_id=SAVED_JOB, stage="Applied"))
    assert seen == {"action": ACTION, "target": SAVED_JOB}
    assert out["requested_stage"] == "applied"
    assert out["to_confirm"] is None
