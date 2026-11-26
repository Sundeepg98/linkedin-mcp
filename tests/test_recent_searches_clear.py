"""Clearing his recent job searches -- census row ``J 19``, built behind the grant and REFUSING.

Lane build-jobs2, 2026-11-26, applying J-19-BUILT-BEHIND-THE-GRANT (the
orchestrator, 2026-11-25): "BUILD behind the grant, REFUSING until its confirm
dialog is captured; it fires only on his order".

THE PAGE is the live lane's session-2 capture of his jobs home, with LinkedIn's
words written by keyed shape (``tests/fixtures/live2/j18_words.html``,
``scripts/_build_jobs2_word_skeletons.py``): one card headed
``Recent job searches``, one button in it reading ``Clear``, and a list of six
searches. What the press opens is not in any capture, and that is the refusal.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
and every request a page would make is refused first.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from linkedin_server import recent_searches_clear as rsc, server, writes
from linkedin_server.errors import WriteAttemptError
from tests.test_writes import FixtureNavigator, browser_page, writes_on  # noqa: F401 -- fixtures

_LIVE2 = Path(__file__).parent / "fixtures" / "live2"
_WORDS = (_LIVE2 / "j18_words.html").read_text(encoding="ascii")
_REDUCED = (_LIVE2 / "j18.html").read_text(encoding="ascii")
_ACTION = "set_recent_job_searches_cleared"

#: The Clear button's text span, exactly as the words fixture draws it.
_CLEAR = '<span class="artdeco-button__text">\nClear\n</span>'


def _swap(markup: str, old: str, new: str, count: int = 1) -> str:
    assert markup.count(old) == count, (old, markup.count(old))
    return markup.replace(old, new)


async def _refused(route) -> None:
    await route.abort()


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


async def _read(page, markup: str) -> dict:
    await page.set_content(markup, wait_until="domcontentloaded")
    return await rsc.read_clear_control(page)


# ---------------------------------------------------------------------------
# 1. The reader: the card by its heading, the button by its own words
# ---------------------------------------------------------------------------


async def test_the_card_its_clear_button_and_its_searches_are_read_off_the_capture(browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    reading = await _read(page, _WORDS)
    assert reading == {
        "cards": 1, "clear_buttons": 1, "lists": 1, "searches_listed": 6,
        "confirm_dialog_read": False, "error": None,
    }, reading
    assert rsc.state_of(reading)[0] == rsc.SEARCHES_LISTED


async def test_THIS_CONTROL_CAN_FAIL_each_doubt_reads_unknown(browser_page):
    """The words are the anchor, and every count must be exactly what the
    capture drew: the reduced copy names no card; a second Clear button, a
    second card and an empty list each read ``unknown``."""
    page = browser_page
    await page.route("**/*", _refused)
    reduced = await _read(page, _REDUCED)
    assert reduced["cards"] == 0 and rsc.state_of(reduced)[0] == rsc.UNKNOWN
    two_buttons = _swap(_WORDS, _CLEAR, _CLEAR + "</button><button>" + _CLEAR)
    reading = await _read(page, two_buttons)
    assert reading["clear_buttons"] == 2 and rsc.state_of(reading)[0] == rsc.UNKNOWN
    assert _WORDS.count("<main ") == 1
    two_cards = _WORDS.replace(
        "<main ", "<main><section><h2>Recent job searches</h2></section></main><main ", 1)
    reading = await _read(page, two_cards)
    assert reading["cards"] == 2 and rsc.state_of(reading)[0] == rsc.UNKNOWN
    start = _WORDS.index('aria-label="Recent job searches">')
    end = _WORDS.index("</ul>", start)
    empty = _WORDS[:start] + 'aria-label="Recent job searches">\n' + _WORDS[end:]
    reading = await _read(page, empty)
    assert reading["searches_listed"] == 0
    state, why = rsc.state_of(reading)
    assert state == rsc.UNKNOWN and "never been captured" in why


# ---------------------------------------------------------------------------
# 2. The write: sanctioned, refusing, minting nothing
# ---------------------------------------------------------------------------


def test_the_action_is_sanctioned_not_performable_and_names_what_lifts_it():
    spec = writes.spec_for_action(_ACTION)
    assert spec.tool_name == "linkedin_set_recent_job_searches_cleared"
    assert _ACTION not in writes.PERFORMABLE
    assert spec.url_template is None and spec.url_pattern is None
    assert spec.target_kind == "self"
    assert spec.irreversible is True
    assert spec.reversibility_class == "STILL-UNKNOWN" and spec.reversibility_measured is False
    refusal = writes._NINE_REFUSALS[_ACTION]
    assert "AT HIS ORDER" in refusal and "J-19-BUILT-BEHIND-THE-GRANT" in refusal
    assert not writes.grant_is_possible(spec)
    assert writes._SURFACE_READS[spec.state_from][0] == rsc.HOME_URL
    tool = getattr(server, spec.tool_name)
    assert list(inspect.signature(getattr(tool, "fn", tool)).parameters) == ["confirm_token"]


async def test_the_preview_reads_the_jobs_home_once_and_issues_no_token(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    nav = FixtureNavigator({rsc.HOME_URL: _WORDS})
    block = await writes.preview(writes.spec_for_action(_ACTION), target="self",
                                 navigator=nav, page=page)
    assert nav.gotos == [rsc.HOME_URL]
    assert block["to_confirm"] is None, block
    assert block["where"]["whose"].startswith("your own jobs home")
    shown = block["where"]["what_the_page_showed"]
    assert (shown["cards"], shown["clear_buttons"], shown["searches_listed"]) == (1, 1, 6)
    assert shown["confirm_dialog_read"] is False
    assert block["direction"]["currently"] == rsc.SEARCHES_LISTED
    # The block never names his profile: this act does not touch it.
    assert "your own LinkedIn profile" not in json.dumps(block)
    assert writes._GRANTS == {}
    with pytest.raises(WriteAttemptError):
        writes.mint(_ACTION, "self", receipt="any")


async def test_a_page_that_draws_no_card_is_refused_at_the_preview(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    nav = FixtureNavigator({rsc.HOME_URL: _REDUCED})
    with pytest.raises(WriteAttemptError) as caught:
        await writes.preview(writes.spec_for_action(_ACTION), target="self",
                             navigator=nav, page=page)
    assert "unknown" in str(caught.value)
    assert writes._GRANTS == {}


async def test_with_writes_off_the_tool_loads_nothing(monkeypatch):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    tool = server.linkedin_set_recent_job_searches_cleared
    out = await getattr(tool, "fn", tool)()
    assert out.get("performed") is not True
    assert "writes" in json.dumps(out).lower()
