"""The REPLY path's Send wait, its draft rule, and its never-pressed verdict --
the orchestrator's order of 2026-09-28 21:08 (lane L5).

WHAT WAS MEASURED LIVE (the live lane's session 5, M M17; no names here). The
conversation resolved exactly, the preview resolved the person, and his words
went into the reply box, 67 of 67 characters with an emoji among them. Then
``threads.reply_send_gate`` read Send DISABLED straight after the fill and
refused at ``4_fill_not_landed``: no press, the words left in the box, and a
fresh reload showed no reply. The race the first contact met in session 4 --
there Send was drawn enabled about a second later, and 228 ms later once
waited for in session 5.

SO, AS ON THE FIRST CONTACT: after the fill the reply waits, bounded, for its
Send to be drawn without ``disabled``, then runs the whole last-moment check
as before, pressing only if every condition holds. A reply box that ALREADY
holds exactly his words, whole and nothing else, is a state the reply may act
from (``reply_box_holds_the_words``): nothing is typed, and the same wait and
check run. Any other text still refuses. And a Send the check never let
through reads NOT SENT, never "unknown": nothing can have left, the fresh load
says whether LinkedIn kept his words, and a retry is safe.

THE PAGE is the reply fixture every reply test uses
(``tests/fixtures/synthetic/messaging_thread.html``); each world below is one
asserted edit of it, and its reply form's structure is pinned by digest.
NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from linkedin_server import threads, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview
from tests.test_messaging_threads import THREAD, THREAD_ID, _derive
from tests.test_send_reply import (
    _SPEC, AFTER, AFTER_DIFFERENT_WORDS, DISPATCHING, DRAFT, TEXT, TARGET, URL,
    _nav, _no_third_party,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = Path(__file__).resolve().parent.parent

#: THE REPLY FORM'S STRUCTURE, tags and nesting, as the first-contact builder's
#: digest prints it over the fixture's one ``form.msg-form``. A structural
#: edit of the form changes it; every world below is the same form.
REPLY_FORM_DIGEST = "plmmidecdkbbmdma"

#: M M17's words had an emoji in them: his words, and the thumbs-up sign.
TEXT_EMOJI = TEXT + " \U0001F44D"
TARGET_EMOJI = {"thread": THREAD_ID, "text": TEXT_EMOJI}

_LISTENER = "    send.disabled = (editor.textContent.trim().length === 0);"


def _late(world: str, delay_ms: int) -> str:
    """SESSION 5's TIMING, as an asserted edit of the fixture's own listener:
    Send stays disabled as his words land and turns on ``delay_ms`` later."""
    return _derive(
        world,
        _LISTENER,
        "    var filled = editor.textContent.trim().length > 0;\n"
        "    send.disabled = true;\n"
        "    if (filled) { setTimeout(function () {"
        " if (editor.textContent.trim().length) { send.disabled = false; } }, "
        + str(delay_ms) + "); }",
    )


def _holding(world: str, words: str, *, send_enabled: bool = True) -> str:
    """A reply box that already holds ``words`` -- a draft LinkedIn kept."""
    held = _derive(world, 'id="reply-editor"></div>', 'id="reply-editor">' + words + "</div>")
    if send_enabled:
        held = _derive(held, 'id="reply-send" disabled>', 'id="reply-send">')
    return held


LATE = _late(DISPATCHING, 1_000)
NEVER = _late(DISPATCHING, 600_000)


async def _grant(page, world: str = THREAD, target: dict = TARGET):
    block = await preview(_SPEC, target=target, navigator=_nav(world), page=page)
    return block, consume(block["to_confirm"], action=_SPEC.action, target=target)


# ---------------------------------------------------------------------------
# 1. The reply form the worlds are built on
# ---------------------------------------------------------------------------


def _reply_form_digest(html: str) -> str:
    sys.path.insert(0, str(REPO / "scripts"))
    import _build_first_contact_bubble as builder
    from _build_named_profile_skeleton import Text, Tree

    tree = Tree()
    tree.feed(html)
    tree.close()
    forms = []

    def walk(node) -> None:
        if isinstance(node, Text):
            return
        if getattr(node, "tag", None) == "form" and "msg-form" in (node.get("class") or "").split():
            forms.append(node)
        for child in getattr(node, "children", []):
            walk(child)

    walk(tree.root)
    assert len(forms) == 1, len(forms)
    return builder.fragment_digest(forms)


def test_the_reply_form_is_the_pinned_structure():
    assert _reply_form_digest(THREAD) == REPLY_FORM_DIGEST


def test_THIS_CONTROL_CAN_FAIL_a_structural_edit_of_the_form_changes_its_digest():
    edited = _derive(THREAD, '<button type="button" class="msg-form__send-toggle artdeco-button">'
                     "Open send options</button>", "")
    assert _reply_form_digest(edited) != REPLY_FORM_DIGEST


def test_the_worlds_edit_the_listener_or_the_box_and_nothing_else():
    """The timing worlds edit only the page's listener, outside the form: the
    form's digest is the pinned one. A draft world differs by exactly one
    thing, the words in the editor -- the text node the digest counts, as the
    live filled bubble differed from the empty one -- and without them it is
    the pinned form again."""
    for world in (LATE, NEVER):
        assert _reply_form_digest(world) == REPLY_FORM_DIGEST
    for send_enabled in (True, False):
        held = _holding(THREAD, TEXT, send_enabled=send_enabled)
        assert _reply_form_digest(held) != REPLY_FORM_DIGEST
        emptied = _derive(held, 'id="reply-editor">' + TEXT + "</div>", 'id="reply-editor"></div>')
        assert _reply_form_digest(emptied) == REPLY_FORM_DIGEST


def test_the_reply_wait_is_bounded_at_five_seconds():
    assert threads.REPLY_SEND_ENABLED_WAIT_MS == 5_000


# ---------------------------------------------------------------------------
# 2. Session 5: Send turns on after the words land
# ---------------------------------------------------------------------------


async def test_a_reply_whose_send_turns_on_after_the_words_land_is_waited_for_and_sent(
    writes_on, browser_page
):
    """M M17, REPRODUCED OFFLINE: the words land and Send turns on a second
    later. The reply now waits for it, bounded, re-reads everything, and the
    reply goes; a fresh load confirms it."""
    _block, grant = await _grant(browser_page)
    receipt = await writes.perform(_nav(LATE, AFTER), browser_page, grant)
    send = receipt["send_gate"]
    assert send["proceeded"] is True, send
    wait = receipt["send_enabled_wait"]
    assert wait["enabled"] is True and wait["waited_ms"] >= 500, wait
    assert receipt["typed_text"]["submit_was_pressed"] is True
    assert receipt["verification"]["observed_state"] == threads.REPLY_SENT
    assert receipt["performed"] is True and receipt["verified"] is True
    assert receipt["typed_text"]["words_left_in_the_box"] is False
    _no_third_party(receipt)


@pytest.mark.parametrize(
    "fresh, kept",
    [(THREAD, False), (_holding(THREAD, TEXT, send_enabled=False), True)],
    ids=["the-fresh-load-drops-them", "linkedin-keeps-them"],
)
async def test_a_reply_whose_send_never_turns_on_is_refused_and_reads_not_sent(
    writes_on, browser_page, monkeypatch, fresh, kept
):
    """The wait decides nothing: Send still disabled at its end refuses at 4,
    as before, with nothing pressed -- and that is NOT SENT, never "unknown"
    (the calls of 19:48 and 21:08): the fresh load says whether LinkedIn kept
    his words, and a retry is safe."""
    monkeypatch.setattr(threads, "REPLY_SEND_ENABLED_WAIT_MS", 1_500)
    _block, grant = await _grant(browser_page)
    receipt = await writes.perform(_nav(NEVER, fresh), browser_page, grant)
    send = receipt["send_gate"]
    assert send["proceeded"] is False and send["refused_condition"] == "4_fill_not_landed", send
    wait = receipt["send_enabled_wait"]
    assert wait["enabled"] is False and wait["waited_ms"] >= 1_400, wait
    assert receipt["clicked"]["clicks_made"] == 0
    typed = receipt["typed_text"]
    assert typed["text_was_entered"] is True and typed["submit_was_pressed"] is False
    verification = receipt["verification"]
    assert verification["observed_state"] == threads.REPLY_HELD, verification
    assert receipt["performed"] is False
    assert "SEND WAS NEVER PRESSED" in verification["why"]
    assert "A RETRY IS SAFE" in verification["why"] and "Do NOT retry" not in verification["why"]
    assert typed["words_left_in_the_box"] is kept
    assert ("LinkedIn kept them" in verification["why"]) is kept
    _no_third_party(receipt)


# ---------------------------------------------------------------------------
# 3. The draft rule: his words already in the box
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "words, target", [(TEXT, TARGET), (TEXT_EMOJI, TARGET_EMOJI)], ids=["his-words", "with-the-emoji"]
)
async def test_a_reply_box_already_holding_exactly_his_words_is_sent_without_typing(
    writes_on, browser_page, words, target
):
    """DERIVED WORLD: the retry of M M17 may reopen the box with the same words
    in it. The preview reads the state his words make, the act types nothing,
    waits for Send, re-checks everything, presses, and a fresh load confirms."""
    held = _holding(THREAD, words)
    block, grant = await _grant(browser_page, held, target)
    assert block["direction"]["currently"] == threads.REPLY_WORDS_IN_PLACE, block["direction"]
    dispatching = _holding(DISPATCHING, words)
    after = _derive(AFTER, f">{TEXT}</p>", f">{words}</p>") if words != TEXT else AFTER
    receipt = await writes.perform(_nav(dispatching, after), browser_page, grant)
    typed = receipt["typed_text"]
    assert typed["text_was_entered"] is False and typed["words_were_already_in_the_box"] is True
    assert typed["submit_was_pressed"] is True
    assert receipt["send_gate"]["proceeded"] is True
    assert receipt["send_enabled_wait"]["enabled"] is True
    assert receipt["verification"]["observed_state"] == threads.REPLY_SENT
    assert receipt["performed"] is True
    _no_third_party(receipt)


@pytest.mark.parametrize(
    "words",
    [TEXT + " PS", TEXT[:10], "an old draft"],
    ids=["his-words-and-more", "part-of-his-words", "other-words"],
)
async def test_any_other_text_in_the_reply_box_still_refuses(writes_on, browser_page, words):
    with pytest.raises(WriteAttemptError, match="NOT EMPTY"):
        await preview(_SPEC, target=TARGET, navigator=_nav(_holding(THREAD, words)), page=browser_page)


async def test_the_existing_draft_world_refuses_as_it_always_did(writes_on, browser_page):
    with pytest.raises(WriteAttemptError, match="NOT EMPTY"):
        await preview(_SPEC, target=TARGET, navigator=_nav(DRAFT), page=browser_page)


async def test_a_draft_whose_send_never_turns_on_reads_not_sent_and_keeps_the_words(
    writes_on, browser_page, monkeypatch
):
    monkeypatch.setattr(threads, "REPLY_SEND_ENABLED_WAIT_MS", 1_500)
    held = _holding(THREAD, TEXT, send_enabled=False)
    _block, grant = await _grant(browser_page, held)
    receipt = await writes.perform(_nav(held, held), browser_page, grant)
    assert receipt["send_gate"]["refused_condition"] == "4_fill_not_landed"
    typed = receipt["typed_text"]
    assert typed["text_was_entered"] is False and typed["words_were_already_in_the_box"] is True
    assert typed["submit_was_pressed"] is False and typed["words_left_in_the_box"] is True
    assert receipt["verification"]["observed_state"] == threads.REPLY_HELD
    assert "sends them without typing them again" in receipt["verification"]["why"]
    _no_third_party(receipt)


# ---------------------------------------------------------------------------
# 4. "unknown" is kept for a Send that was pressed
# ---------------------------------------------------------------------------


async def test_a_reply_pressed_but_unconfirmed_stays_unknown_and_says_do_not_retry(
    writes_on, browser_page
):
    _block, grant = await _grant(browser_page)
    receipt = await writes.perform(_nav(DISPATCHING, AFTER_DIFFERENT_WORDS), browser_page, grant)
    assert receipt["typed_text"]["submit_was_pressed"] is True
    verification = receipt["verification"]
    assert verification["observed_state"] == writes.UNKNOWN, verification
    assert "Do NOT retry" in verification["why"] and "A RETRY IS SAFE" not in verification["why"]
    assert receipt["typed_text"]["words_left_in_the_box"] is False
    _no_third_party(receipt)


def test_the_preview_prints_whether_the_box_holds_his_words():
    assert "editor_holds_the_words" in threads.thread_facts({})

