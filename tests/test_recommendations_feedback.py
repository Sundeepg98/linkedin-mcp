"""The feedback pair under his recommended jobs -- census row ``J 163``, a RECEIPT-ONLY write.

Lane build-jobs2, 2026-11-26, applying J-163-RECEIPT-ONLY-WRITE (the
orchestrator, 2026-11-25): "a RECEIPT-ONLY WRITE behind the grant, fired only
on his order (no inverse exists, so the round-trip rule cannot apply); proven
by that press".

THE PAGE is live session 8's recommended jobs with LinkedIn's words written by
keyed shape (``tests/fixtures/live8/recommended_words.html``,
``scripts/_build_jobs2_word_skeletons.py``): one block LinkedIn names
``jobs-search-list-feedback``, its heading ``Are these results helpful?``, its
sentence, and two buttons -- ``Are you finding what you're looking for? No``,
then ``... Yes`` (LinkedIn's curly apostrophe). What an answer leaves is in no
capture, so the outcome is declared unverifiable and the receipt records what
the page draws after the press.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
and every request a page would make is refused first.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from linkedin_server import job_feedback as jf, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_LIVE8 = Path(__file__).parent / "fixtures" / "live8"
_WORDS = (_LIVE8 / "recommended_words.html").read_text(encoding="ascii")
_REDUCED = (_LIVE8 / "recommended.html").read_text(encoding="ascii")
_ACTION = "send_recommendations_feedback"

#: A witness standing in for nothing LinkedIn does: it records the words of
#: the button a click landed on, so a test can say WHICH answer was pressed.
_WITNESS = (
    "<script>window.__pressed = [];"
    "document.addEventListener('click', function (e) {"
    " var b = e.target.closest('button'); if (!b) return;"
    " window.__pressed.push((b.textContent || '').replace(/\\s+/g, ' ').trim());"
    "}, true);</script>"
)


def _witnessed(markup: str) -> str:
    assert markup.count("</head>") == 1
    return markup.replace("</head>", _WITNESS + "</head>")


async def _refused(route) -> None:
    await route.abort()


class _Navigator:
    """Serves frozen worlds for the ONE address, in order; the last repeats."""

    def __init__(self, *worlds: str, landed: str = ""):
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.landed = landed

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url != jf.PAGE_URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed or url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


async def _read(page, markup: str) -> dict:
    await page.set_content(markup, wait_until="domcontentloaded")
    return await jf.read_block(page)


# ---------------------------------------------------------------------------
# 1. The reader and the aim
# ---------------------------------------------------------------------------


async def test_the_block_and_its_two_buttons_are_read_off_the_capture(browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    reading = await _read(page, _WORDS)
    assert reading == {
        "blocks": 1, "heading": 1, "sentence": 1, "buttons": 2,
        "answers": {"no": 1, "yes": 1}, "error": None,
    }, reading
    assert jf.state_of(reading)[0] == jf.ASKED
    # THE AIM: each answer's selector resolves to exactly one button, and it
    # is the button whose own words are that answer's.
    for answer, words in jf.ANSWERS.items():
        target = page.locator(jf.press_selector(answer))
        assert await target.count() == 1, answer
        assert " ".join((await target.text_content()).split()) == words, answer


async def test_THIS_CONTROL_CAN_FAIL_each_doubt_reads_unknown(browser_page):
    """The words are the anchor and every count must be the capture's: the
    reduced copy, a third button, a second block, and a block whose heading
    reads otherwise each read ``unknown``."""
    page = browser_page
    await page.route("**/*", _refused)
    reduced = await _read(page, _REDUCED)
    assert reduced["heading"] == 0 and jf.state_of(reduced)[0] == jf.UNKNOWN
    opening = '<div data-view-name="jobs-search-list-feedback">'
    assert _WORDS.count(opening) == 1
    # A THIRD BUTTON INSIDE THE BLOCK: planted beside the pair, in the block.
    pair = _WORDS.index('<div class="flex-shrink-zero">', _WORDS.index(opening))
    third = _WORDS[:pair] + "<button>x</button>" + _WORDS[pair:]
    reading = await _read(page, third)
    assert reading["buttons"] == 3 and jf.state_of(reading)[0] == jf.UNKNOWN
    second = _WORDS.replace(opening, opening + "</div>" + opening, 1)
    reading = await _read(page, second)
    assert reading["blocks"] == 2 and jf.state_of(reading)[0] == jf.UNKNOWN
    renamed = _WORDS.replace("\nAre these results helpful?\n", "\nAre these jobs helpful?\n", 1)
    assert renamed != _WORDS
    reading = await _read(page, renamed)
    assert reading["heading"] == 0 and jf.state_of(reading)[0] == jf.UNKNOWN


def test_an_answer_is_yes_or_no_and_a_refusal_never_repeats_it():
    assert jf.canonical_answer(" Yes ") == ("yes", "")
    assert jf.canonical_answer("NO") == ("no", "")
    for bad in ("maybe", "", None, "yes please", "Example Person"):
        answer, why = jf.canonical_answer(bad)
        assert answer is None and why
        assert "Example Person" not in why


# ---------------------------------------------------------------------------
# 2. The write: performable, strict, receipt-only
# ---------------------------------------------------------------------------


def test_the_spec_is_performable_strict_irreversible_and_declared_unverifiable():
    spec = spec_for_action(_ACTION)
    assert (jf.ACTION, jf.TOOL_NAME) == (_ACTION, spec.tool_name) == (
        _ACTION, "linkedin_send_recommendations_feedback")
    assert _ACTION in writes.PERFORMABLE and _ACTION in writes.STRICT_PRESS_ACTIONS
    assert spec.irreversible is True and spec.unverifiable is not None
    assert spec.reversibility_class == "STILL-UNKNOWN" and spec.reversibility_measured is False
    assert spec.url_pattern.match(jf.PAGE_URL)
    for other in (jf.PAGE_URL + "?x=1", jf.PAGE_URL + "x/", "https://www.linkedin.com/jobs/collections/"):
        assert not spec.url_pattern.match(other), other
    assert spec.target_kind == "recommendations_feedback"
    tool = getattr(server, spec.tool_name)
    assert list(inspect.signature(getattr(tool, "fn", tool)).parameters) == ["answer", "confirm_token"]
    assert writes.anchor_label_for(spec, "yes") == jf.ANSWERS["yes"]


async def test_the_preview_reads_the_block_once_and_binds_the_answer(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    nav = _Navigator(_WORDS)
    block = await preview(spec_for_action(_ACTION), target="no", navigator=nav, page=page)
    assert nav.gotos == [jf.PAGE_URL]
    assert block["to_confirm"], block
    assert block["where"]["answer"] == "no" and block["where"]["press"] == jf.ANSWERS["no"]
    assert block["direction"]["currently"] == jf.ASKED
    assert block["verification"]["outcome_is_verifiable"] == "NO"
    # THE TOKEN BINDS THE ANSWER: one shown for "no" does not confirm "yes".
    with pytest.raises(WriteAttemptError):
        consume(block["to_confirm"], action=_ACTION, target="yes")


async def test_the_press_lands_on_his_answer_and_the_receipt_records_what_the_page_drew(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    world = _witnessed(_WORDS)
    block = await preview(spec_for_action(_ACTION), target="yes",
                          navigator=_Navigator(world), page=page)
    grant = consume(block["to_confirm"], action=_ACTION, target="yes")
    act = _Navigator(world)
    receipt = await writes.perform(act, page, grant)
    assert act.gotos == [jf.PAGE_URL]
    assert await page.evaluate("() => window.__pressed") == [jf.ANSWERS["yes"]]
    # DECLARED UNVERIFIABLE: nothing compared, "unknown", the declaration printed.
    assert receipt["performed"] == "unknown", receipt
    assert receipt["verification"]["outcome_is_verifiable"] == "NO"
    after = receipt["after_press"]
    assert after["blocks"] == 1 and after["question_still_drawn"] is True, after
    assert "Example Person" not in json.dumps(receipt)


async def test_a_landing_elsewhere_and_a_redrawn_block_are_refused_before_any_press(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    world = _witnessed(_WORDS)
    block = await preview(spec_for_action(_ACTION), target="no", navigator=_Navigator(world), page=page)
    grant = consume(block["to_confirm"], action=_ACTION, target="no")
    elsewhere = _Navigator(world, landed="https://www.linkedin.com/jobs/collections/top-applicant/")
    with pytest.raises(WriteAttemptError) as caught:
        await writes.perform(elsewhere, page, grant)
    assert "top-applicant" not in str(caught.value)
    assert await page.evaluate("() => window.__pressed") == []
    writes.discard_all()
    block = await preview(spec_for_action(_ACTION), target="no", navigator=_Navigator(world), page=page)
    grant = consume(block["to_confirm"], action=_ACTION, target="no")
    with pytest.raises(WriteAttemptError):
        await writes.perform(_Navigator(_witnessed(_REDUCED)), page, grant)
    assert await page.evaluate("() => window.__pressed") == []


async def test_with_writes_off_the_tool_loads_nothing(monkeypatch):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    tool = server.linkedin_send_recommendations_feedback
    out = await getattr(tool, "fn", tool)("yes")
    assert out.get("performed") is not True
    assert "writes" in json.dumps(out).lower()


async def test_an_answer_that_is_not_yes_or_no_loads_nothing(writes_on, browser_page):
    nav = _Navigator(_WORDS)
    with pytest.raises(WriteAttemptError):
        await preview(spec_for_action(_ACTION), target="maybe", navigator=nav, page=browser_page)
    assert nav.gotos == []
