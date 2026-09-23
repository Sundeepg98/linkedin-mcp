"""``send_reply`` -- census row ``M M10`` -- built to ready-to-fire, the three
controls that keep a built write from being a fired one, and the read-back
that lets a send say SENT.

WHAT THIS ACTION IS. One reply, typed into the reply box of ONE existing
conversation he names by thread id, and confirmed by loading that
conversation FRESH: his exact words as its last message, and the count of
messages carrying them up by exactly one against the preview's reading.

WHAT IS MEASURED AND WHAT IS NOT. The conversation's structure and the reply
form are measured (see ``tests/fixtures/synthetic/messaging_thread.html``);
that a conversation draws the composer's form, and that his own message is an
item WITHOUT the ``--other`` modifier, are DERIVED, and every world below that
needs either is built by an asserted edit and says so.

NOTHING HERE REACHES LINKEDIN. Every page is a fixture served into a local
headless Chromium; the fixture's own script stands in for LinkedIn's redraw.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import server, threads, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_messaging_threads import (
    OTHER_THREAD_ID,
    THEIR_NAMES,
    THEIR_WORDS,
    THREAD,
    THREAD_ID,
    _derive,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_ACTION = "send_reply"
_SPEC = spec_for_action(_ACTION)
TEXT = "Thursday works, speak then."
TARGET = {"thread": THREAD_ID, "text": TEXT}
URL = threads.thread_url(THREAD_ID)
OTHER_URL = threads.thread_url(OTHER_THREAD_ID)

_FORM = '<form class="msg-form msg-form--thread-footer-feature" id="reply-form">'
#: The conversation whose Send DISPATCHES -- the fixture's script draws the
#: words as the new last message and empties the box, as LinkedIn redraws.
DISPATCHING = _derive(THREAD, _FORM, _FORM.replace('id="reply-form"', 'id="reply-form" data-dispatches="yes"'))
#: DERIVED -- the conversation as a FRESH LOAD draws it after the reply
#: landed: his words, as an item with no --other modifier, marked last.
AFTER = _derive(
    _derive(
        THREAD,
        '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">',
        '<li class="msg-s-message-list__event clearfix">',
    ),
    '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
    '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">'
    '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group">'
    f'<p class="msg-s-event-listitem__body t-14">{TEXT}</p></div></li>'
    '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
)
#: DERIVED -- a fresh load where the last message is his but its words are
#: not the ones sent (LinkedIn rendered them differently, say).
AFTER_DIFFERENT_WORDS = _derive(AFTER, f">{TEXT}</p>", ">Thursday works (edited)</p>")
DRAFT = _derive(
    _derive(THREAD, 'id="reply-editor"></div>', 'id="reply-editor">an old draft</div>'),
    'id="reply-send" disabled>',
    'id="reply-send">',
)


class _Navigator:
    """Serves frozen worlds, LANDS where the map says, and RECORDS the asks.

    A url maps to a list of ``(html, landed)`` served one per visit in order,
    the last repeating -- a reply's conversation is visited by the preview, by
    the click, and by the verification, and those are different worlds.
    """

    def __init__(self, pages: dict[str, list[tuple[str, str]]]):
        self.pages = {url: list(entries) for url, entries in pages.items()}
        self.gotos: list[str] = []
        self._visits: dict[str, int] = {}

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url not in self.pages:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        visit = self._visits.get(url, 0)
        self._visits[url] = visit + 1
        entries = self.pages[url]
        html, landed = entries[min(visit, len(entries) - 1)]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


def _nav(*worlds: str, landed: str = URL) -> _Navigator:
    return _Navigator({URL: [(world, landed) for world in worlds]})


def _no_third_party(value) -> None:
    """The rule: nothing the OTHER side wrote, and no thread id but the one he
    supplied, in a block or a receipt. The title is allowed ONLY in the
    preview's ``who_this_would_reach`` -- asserted separately."""
    text = json.dumps(value)
    for needle in THEIR_WORDS + (OTHER_THREAD_ID,):
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


async def _preview(page, world: str = THREAD):
    nav = _nav(world)
    block = await preview(_SPEC, target=TARGET, navigator=nav, page=page)
    return block, nav


# ---------------------------------------------------------------------------
# 1. The target: a thread id and his words, bound together
# ---------------------------------------------------------------------------


def test_the_target_is_the_thread_and_the_words_and_only_the_thread_reaches_a_url():
    canonical = writes._target_for(_SPEC, TARGET)
    assert canonical == THREAD_ID + writes.TARGET_JOIN + TEXT
    assert writes.url_target_of(_SPEC, canonical) == THREAD_ID
    assert writes._text_component_of(_SPEC, canonical) == TEXT
    grant = writes.WriteGrant(action=_ACTION, target=canonical, token="t", minted_at=0.0)
    assert writes.assert_write_url(URL, grant) == URL
    with pytest.raises(WriteAttemptError):
        writes._target_for(_SPEC, {"thread": THREAD_ID, "text": "two\nlines"})
    with pytest.raises(WriteAttemptError):
        writes._target_for(_SPEC, {"thread": "", "text": TEXT})


@pytest.mark.parametrize("bad", ["new", "abc", "2-x/../compose", "2-x?recipient=1"])
def test_a_target_that_is_not_a_thread_id_cannot_rebuild_an_address_the_write_door_passes(bad):
    grant = writes.WriteGrant(
        action=_ACTION, target=bad + writes.TARGET_JOIN + TEXT, token="t", minted_at=0.0
    )
    rebuilt = _SPEC.url_template.format(target=writes.url_target_of(_SPEC, grant.target))
    with pytest.raises(WriteAttemptError):
        writes.assert_write_url(rebuilt, grant)


def test_the_tables_name_this_action():
    assert _ACTION in writes.PERFORMABLE
    assert _ACTION in writes.TYPING_ACTIONS and _ACTION in writes.REPLY_ACTIONS
    assert _ACTION not in writes.ADDRESSED_TYPING_ACTIONS
    assert _ACTION not in writes._TOGGLE_ACTIONS
    assert _ACTION not in writes.UPLOAD_ACTIONS
    assert writes.anchor_label_for(_SPEC) == threads.REPLY_EDITOR_LABEL
    assert writes._WRITE_SURFACE_FOR_ACTION[_ACTION] == "messaging thread"
    assert "conversation" in writes._WHERE_TO_LOOK[_ACTION]
    assert "DELTA" in writes._VERIFIED_FROM[_ACTION]
    assert _SPEC.unverifiable is None, "this action HAS a verification"
    assert _SPEC.irreversible is True
    assert writes.grant_is_possible(_SPEC)


# ---------------------------------------------------------------------------
# 2. The preview: the named conversation, read; one token; the title printed
#    to him and kept nowhere
# ---------------------------------------------------------------------------


async def test_the_preview_reads_the_named_conversation_and_mints_one_token(writes_on, browser_page):
    block, nav = await _preview(browser_page)
    assert nav.gotos == [URL]
    assert block["to_confirm"]
    assert block["where"]["thread"] == THREAD_ID and block["where"]["text"] == TEXT
    assert block["where"]["url"] == URL
    assert block["direction"]["currently"] == "reply_box_empty"
    facts = block["where"]["what_the_page_showed"]
    assert facts["landed_on_the_named_thread"] is True
    assert facts["events_with_text"] == 0 and facts["recipient_boxes"] == 0
    assert "Kai Example" in block["who_this_would_reach"]
    grant = writes._GRANTS[block["to_confirm"]]
    assert "who_this_would_reach" not in grant.preview, "the title reached the grant"
    assert "Kai Example" not in json.dumps(grant.preview)
    assert "Kai Example" not in grant.target
    _no_third_party(block)


async def test_a_preview_that_lands_in_another_conversation_reads_nothing_and_mints_nothing(
    writes_on, browser_page
):
    nav = _nav(THREAD, landed=OTHER_URL)
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target=TARGET, navigator=nav, page=browser_page)
    assert "did not land on the conversation you named" in str(excinfo.value)
    assert OTHER_THREAD_ID not in str(excinfo.value)
    assert writes._GRANTS == {}, "a token exists for a conversation nobody named"


async def test_a_preview_over_a_draft_mints_nothing(writes_on, browser_page):
    with pytest.raises(WriteAttemptError) as excinfo:
        await _preview(browser_page, DRAFT)
    assert "NOT EMPTY" in str(excinfo.value)
    assert writes._GRANTS == {}


# ---------------------------------------------------------------------------
# 3. THE THREE CONTROLS -- no grant, another target, a second use
# ---------------------------------------------------------------------------


async def test_control_1_it_refuses_without_a_grant(monkeypatch, browser_page):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    nav = _nav(THREAD)
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(_SPEC, target=TARGET, navigator=nav, page=browser_page)
    with pytest.raises(WriteAttemptError, match="disabled"):
        consume("anything", action=_ACTION, target=TARGET)
    off = await server.linkedin_send_reply(THREAD_ID, TEXT)
    assert off["error"] == "writes_disabled" and off["performed"] is False

    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    for bogus in ("", None, True, "not-a-real-token"):
        with pytest.raises(WriteAttemptError):
            consume(bogus, action=_ACTION, target=TARGET)
    unredeemed = writes.WriteGrant(
        action=_ACTION, target=writes._target_for(_SPEC, TARGET), token="t", minted_at=0.0
    )
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(nav, browser_page, unredeemed)
    with pytest.raises(WriteAttemptError, match="WriteGrant"):
        await writes.perform(nav, browser_page, {"action": _ACTION})
    assert nav.gotos == [], "a refused write navigated"


async def test_control_2_it_refuses_a_grant_for_a_different_target(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    token = block["to_confirm"]
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(token, action=_ACTION, target={"thread": OTHER_THREAD_ID, "text": TEXT})
    block, _nav_used = await _preview(browser_page)
    with pytest.raises(WriteAttemptError, match="minted for target"):
        consume(block["to_confirm"], action=_ACTION, target={"thread": THREAD_ID, "text": TEXT + "!"})
    block, _nav_used = await _preview(browser_page)
    with pytest.raises(WriteAttemptError, match="minted for 'send_reply'"):
        consume(block["to_confirm"], action="send_message", target={"member": "x", "text": TEXT})


async def test_control_3_it_refuses_a_second_use_of_the_same_grant(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    with pytest.raises(WriteAttemptError, match="unknown or already-discarded"):
        consume(block["to_confirm"], action=_ACTION, target=TARGET)
    first = _nav(DISPATCHING, AFTER)
    receipt = await writes.perform(first, browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    second = _nav(DISPATCHING, AFTER)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(second, browser_page, grant)
    assert second.gotos == [], "the second use navigated before it refused"


async def test_the_second_use_guard_is_shown_failing_without_its_flag(writes_on, browser_page):
    """SHOWN FAILING, for THIS action: clear the flag and the same grant
    object walks back to the conversation, types, and presses Send again --
    on the one action where a replay is a second message to a person."""
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    await writes.perform(_nav(DISPATCHING, AFTER), browser_page, grant)
    assert grant.performed is True
    grant.performed = False  # the mutation: the guard's input, removed
    replay = _nav(DISPATCHING, AFTER)
    receipt = await writes.perform(replay, browser_page, grant)
    assert replay.gotos[0] == URL
    assert receipt["clicked"]["clicks_made"] == 1, "without the flag the replay sends again"


# ---------------------------------------------------------------------------
# 4. End to end: SENT, NOT SENT, and the honest unknown
# ---------------------------------------------------------------------------


async def test_a_reply_that_lands_reports_sent_from_a_fresh_load(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    act = _nav(DISPATCHING, AFTER)
    receipt = await writes.perform(act, browser_page, grant)
    assert act.gotos == [URL, URL], "one load to act, one FRESH load to verify"
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["typed_text"]["submit_was_pressed"] is True
    assert receipt["clicked"]["clicks_made"] == 1 and receipt["clicked"]["error"] is None
    assert receipt["verification"]["observed_state"] == threads.REPLY_SENT
    assert receipt["performed"] is True and receipt["verified"] is True
    assert "from 0 to 1" in receipt["verification"]["why"]
    _no_third_party(receipt)
    assert "Kai Example" not in json.dumps(receipt)


async def test_a_reply_that_never_left_the_box_reports_not_sent(writes_on, browser_page):
    """The form does not dispatch: Send is pressed, the words stay in the box
    with Send enabled, and a fresh load shows nothing new. False, not unknown."""
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(THREAD, THREAD), browser_page, grant)
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["verification"]["observed_state"] == threads.REPLY_HELD
    assert receipt["performed"] is False
    assert "NOTHING WAS DISPATCHED" in receipt["verification"]["why"]


@pytest.mark.parametrize(
    "after, why_fragment",
    [(THREAD, "0 before, 0 after"), (AFTER_DIFFERENT_WORDS, "last carries your words: False")],
    ids=["box-emptied-but-nothing-drawn", "his-last-message-in-other-words"],
)
async def test_what_proves_neither_is_unknown_and_says_do_not_retry(
    writes_on, browser_page, after, why_fragment
):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(DISPATCHING, after), browser_page, grant)
    assert receipt["performed"] == writes.UNKNOWN
    assert why_fragment in receipt["verification"]["why"]
    assert "Do NOT retry" in receipt["verification"]["why"]


#: DERIVED -- the fresh load shows his exact words as the last message, count
#: up by one, but WEARING THE --other MODIFIER: the other side sent them.
AFTER_FROM_THEM = _derive(
    AFTER,
    '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group">'
    f'<p class="msg-s-event-listitem__body t-14">{TEXT}</p>',
    '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group msg-s-event-listitem--other">'
    f'<p class="msg-s-event-listitem__body t-14">{TEXT}</p>',
)


async def test_the_same_words_from_the_other_side_are_not_his_send(writes_on, browser_page):
    """Authorship is the third condition, and it is the one a delta and a text
    match cannot supply: the other side can write the same words."""
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(DISPATCHING, AFTER_FROM_THEM), browser_page, grant)
    assert receipt["performed"] != True  # noqa: E712 -- never SENT
    assert "last message from: other" in receipt["verification"]["why"]


async def test_an_identical_earlier_message_cannot_stand_in_for_this_one(writes_on, browser_page):
    """The words are ALREADY the conversation's last message before the reply
    (DERIVED): the preview counts one, so a fresh load still showing one is
    not a send -- the delta must be exactly one."""
    block = await preview(_SPEC, target=TARGET, navigator=_nav(AFTER), page=browser_page)
    assert block["where"]["what_the_page_showed"]["events_with_text"] == 1
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(DISPATCHING, AFTER), browser_page, grant)
    assert receipt["performed"] != True  # noqa: E712 -- "unknown" or False, never True


#: DERIVED -- a reply box whose Send never follows the box: the fixture's
#: script is removed, so a fill lands and Send stays drawn DISABLED. The
#: transition the gate requires never happens.
_SCRIPT = THREAD[THREAD.index("<script>"):THREAD.index("</script>") + len("</script>")]
NO_TRANSITION = _derive(THREAD, _SCRIPT, "")


async def test_send_is_not_pressed_when_the_words_did_not_turn_it_on(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    receipt = await writes.perform(_nav(NO_TRANSITION, NO_TRANSITION), browser_page, grant)
    assert receipt["send_gate"]["proceeded"] is False
    assert receipt["send_gate"]["refused_condition"] == "4_fill_not_landed"
    assert receipt["clicked"]["clicks_made"] == 0
    assert receipt["typed_text"]["left_in_the_composer"] is True
    assert receipt["performed"] is not True


async def test_the_click_refuses_before_typing_when_the_landing_is_another_conversation(
    writes_on, browser_page
):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    elsewhere = _nav(DISPATCHING, landed=OTHER_URL)
    with pytest.raises(WriteAttemptError, match="refusing to type") as excinfo:
        await writes.perform(elsewhere, browser_page, grant)
    assert "WITHHELD" in str(excinfo.value)
    assert OTHER_THREAD_ID not in str(excinfo.value)
    assert await browser_page.locator(threads.REPLY_EDITOR_SELECTOR).inner_text() == ""


async def test_the_click_refuses_over_a_draft_that_appeared_after_the_preview(writes_on, browser_page):
    block, _nav_used = await _preview(browser_page)
    grant = consume(block["to_confirm"], action=_ACTION, target=TARGET)
    with pytest.raises(WriteAttemptError, match="refusing to click"):
        await writes.perform(_nav(DRAFT), browser_page, grant)
    assert "an old draft" in await browser_page.locator(threads.REPLY_EDITOR_SELECTOR).inner_text()


# ---------------------------------------------------------------------------
# 5. The tool
# ---------------------------------------------------------------------------


async def test_the_tool_refuses_a_malformed_thread_id_before_anything(writes_on, monkeypatch):
    class _NoBrowser:
        def session(self):
            raise AssertionError("the tool opened a browser for a malformed id")

    monkeypatch.setattr(server, "BROWSER", _NoBrowser())
    result = await server.linkedin_send_reply("new", TEXT)
    assert "error" in result


def test_the_tool_is_registered_as_a_sanctioned_write():
    assert writes.SANCTIONED_WRITES["linkedin_send_reply"].action == _ACTION
    assert callable(getattr(server, "linkedin_send_reply", None))
    from linkedin_server import readonly

    assert readonly.name_implies_write("linkedin_send_reply")
