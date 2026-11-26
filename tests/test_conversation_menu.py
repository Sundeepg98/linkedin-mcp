"""One conversation's own options menu -- census rows ``M M26``, ``M M27``, ``M M29``, ``M M31``.

WHAT IS BUILT (lane build-msg2, 2026-11-26), on ruling
``CONVERSATION-MENU-PREVIEW-PRESS``: five writes behind the single-use grant
-- mute, unmute, mark unread, archive, and a RECEIPT-ONLY delete -- each
previewed by the sanctioned preview press (the one menu in the row wearing the
active marker, opened, its words counted, nothing pressed inside it, closed on
Escape and read closed) and confirmed by a press that re-reads the word in the
menu it opened and refuses on the inverse.

WHAT IS MEASURED AND WHAT IS NOT, so no test here claims more. The MARKUP of
every world is live session 11's own (load 40): the closed thread page, with
the open menu's items cut out of the open capture and put back on a press --
``tests/conversation_menu_worlds.py``. What any ITEM press does is NOT
measured, and every world below that presses one names the behaviour it
chooses (``after``); ``Unmute`` and ``Mark as read`` are DERIVED words, drawn
by name only in worlds that say so.

NOTHING HERE REACHES LINKEDIN. Every page is set into a local headless
Chromium by the navigator below, which records every address asked for and
the page's own press counters before each load replaces it.
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from linkedin_server import conversation_menu as cm
from linkedin_server import readonly, server, threads, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, perform, preview, spec_for_action
from tests import conversation_menu_worlds as w
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

#: An invented thread id of the shape the read boundary admits.
THREAD = "2-SYNTHETICTHREADidAA=="
THREAD_URL = f"https://www.linkedin.com/messaging/thread/{THREAD}/"
LIST = (w.LIVE11 / "messaging_list.html").read_text(encoding="utf-8")
LIST_UNREAD = (w.LIVE11 / "messaging_list_unread.html").read_text(encoding="utf-8")


class _Navigator:
    """Serves frozen worlds per address, in order (the last one repeats), and
    RECORDS every ask -- with the page's OWN press counters read off the
    document each load replaces, so "nothing was pressed" is the page's
    witness and not the actor's."""

    def __init__(self, *, thread: list[str], listing: str = LIST, landed: Any = None):
        self.worlds = {threads.COMPOSE_URL: [listing], THREAD_URL: list(thread)}
        self.gotos: list[str] = []
        self.pressed: list[dict[str, Any]] = []
        self.landed = landed

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url not in self.worlds:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        self.pressed.append(
            await page.evaluate("() => window.__presses || null")
        )
        queue = self.worlds[url]
        html = queue.pop(0) if len(queue) > 1 else queue[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        if self.landed is not None and url == THREAD_URL:
            return self.landed
        return url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


@pytest.fixture(autouse=True)
def _fast_polls(monkeypatch):
    """The polls' INTERVAL pushed down for documents that change only when the
    test presses; the COUNT -- the property -- is kept."""
    monkeypatch.setattr(cm, "MENU_POLL_MS", 5)


@pytest.fixture
async def page(browser_page):
    """The shared local browser's page, with EVERY request refused: the
    skeletons keep LinkedIn's own resource links as ``https://x/...``, and a
    test never lets the browser fetch one (``tests/network_guard.py``)."""

    async def _refuse(route) -> None:
        await route.abort()

    await browser_page.route("**/*", _refuse)
    yield browser_page


async def _witness(page) -> dict[str, Any]:
    return await page.evaluate("() => window.__presses")


async def _granted(page, action: str, nav: _Navigator):
    spec = spec_for_action(action)
    block = await preview(spec, target=THREAD, navigator=nav, page=page)
    return consume(block["to_confirm"], action=action, target=THREAD), block


# ---------------------------------------------------------------------------
# 1. The vocabulary is the capture's
# ---------------------------------------------------------------------------


def test_the_measured_words_are_the_open_captures_own():
    """Every word the open capture draws -- parsed out of it, not typed -- is in
    the module's measured vocabulary, except the one the skeleton reduced."""
    drawn = [word for word in w.CAPTURED_WORDS if word != "x"]
    assert w.CAPTURED_WORDS.count("x") == 1
    assert set(drawn) == set(cm.MEASURED_WORDS) | set(cm.LINK_WORDS)
    assert not set(cm.DERIVED_WORDS) & set(drawn), "a derived word is drawn on the capture"
    for act in cm.ACTS.values():
        assert act.word in cm.MEASURED_WORDS + cm.DERIVED_WORDS
        assert act.word in dict(act.family)


def test_an_item_selector_is_built_only_from_the_vocabulary():
    assert cm.item_selector("Mute").startswith(cm.ACTIVE_CONTENT + " >> role=button")
    for bad in ("Manage settings", "Report", 'Mute"] , *', ""):
        with pytest.raises(ValueError):
            cm.item_selector(bad)


# ---------------------------------------------------------------------------
# 2. The preview press: one menu, read, nothing pressed inside, closed
# ---------------------------------------------------------------------------


async def test_the_preview_press_reads_the_captured_menu_and_presses_nothing_inside(page):
    await page.set_content(w.world(), wait_until="domcontentloaded")
    reading = await cm.preview_press(page)
    assert reading["ready"] and reading["pressed"] and reading["opened"] and reading["closed"]
    assert reading["words"]["Mute"] == 1 and reading["words"]["Unmute"] == 0
    assert reading["links"] == {"Manage settings": 1}
    assert reading["other_items"] == 1, "the reduced item is counted, never read"
    presses = await _witness(page)
    assert presses == {"trigger": 1, "escape": 1, "items": {}, "dialog": 0}
    states = {action: cm.menu_verdict(reading, action)[1] for action in cm.ACTIONS}
    assert states == {
        cm.MUTE: cm.NOT_MUTED, cm.UNMUTE: cm.NOT_MUTED, cm.MARK_UNREAD: cm.READ,
        cm.ARCHIVE: cm.IN_INBOX, cm.DELETE: cm.DELETE_OFFERED,
    }


async def test_the_preview_press_refuses_before_pressing_off_the_measured_shape(page):
    """No active row: refused with ZERO presses -- the page's own witness."""
    await page.set_content(w.no_active_row_world(), wait_until="domcontentloaded")
    reading = await cm.preview_press(page)
    assert reading["ready"] is False and reading["pressed"] is False
    assert "active marker" in reading["why_not_pressed"]
    assert await _witness(page) == {"trigger": 0, "escape": 0, "items": {}, "dialog": 0}
    for action in cm.ACTIONS:
        assert cm.menu_verdict(reading, action)[1] == cm.UNKNOWN


async def test_a_menu_left_open_is_unknown_and_one_that_draws_nothing_is_unknown(page):
    await page.set_content(w.world(escapeStaysOpen=True), wait_until="domcontentloaded")
    reading = await cm.preview_press(page)
    assert reading["closed"] is False
    _f, state, why = cm.menu_verdict(reading, cm.MUTE)
    assert state == cm.UNKNOWN and "did NOT read closed" in why

    await page.set_content(w.world(openDrawsNothing=True), wait_until="domcontentloaded")
    reading = await cm.preview_press(page)
    assert reading["opened"] is False
    assert cm.menu_verdict(reading, cm.MUTE)[1] == cm.UNKNOWN


async def test_the_derived_words_name_the_other_state_and_two_words_name_none(page):
    await page.set_content(w.muted_world(), wait_until="domcontentloaded")
    assert (await cm.read_state(page, cm.UNMUTE))[1] == cm.MUTED
    await page.set_content(w.unread_world(), wait_until="domcontentloaded")
    assert (await cm.read_state(page, cm.MARK_UNREAD))[1] == cm.UNREAD
    # BOTH words of a pair drawn: not a reading.
    await page.set_content(
        w.world(swap={"Star": "Unmute"}), wait_until="domcontentloaded"
    )
    _f, state, why = await cm.read_state(page, cm.MUTE)
    assert state == cm.UNKNOWN and "exactly one of these words" in why
    # THE WORD DROPPED: archive and delete read unknown, never a state.
    await page.set_content(
        w.world(drop=["Archive", "Delete conversation"]), wait_until="domcontentloaded"
    )
    assert (await cm.read_state(page, cm.ARCHIVE))[1] == cm.UNKNOWN
    assert (await cm.read_state(page, cm.DELETE))[1] == cm.UNKNOWN


# ---------------------------------------------------------------------------
# 3. The confirmed press re-reads the word and refuses on the inverse
# ---------------------------------------------------------------------------


async def test_the_item_gate_refuses_on_the_inverse_and_closes_what_it_opened(page):
    await page.set_content(w.muted_world(), wait_until="domcontentloaded")
    await page.click(cm.ACTIVE_TRIGGER, strict=True)
    gate = await cm.menu_item_gate(page, cm.MUTE)
    assert gate["proceed"] is False and gate["refused_condition"] == "1_inverse_drawn"
    assert gate["close_selector"] == cm.ACTIVE_TRIGGER and gate["selector"] == ""

    await page.set_content(w.world(), wait_until="domcontentloaded")
    await page.click(cm.ACTIVE_TRIGGER, strict=True)
    gate = await cm.menu_item_gate(page, cm.MUTE)
    assert gate["proceed"] is True and gate["selector"] == cm.item_selector("Mute")
    assert await page.locator(gate["selector"]).count() == 1


async def test_the_inverse_refusal_is_shown_failing(page, monkeypatch):
    """SHOWN FAILING. Take the inverse word away from the act and the gate
    proceeds on a menu that says the conversation is ALREADY muted -- it would
    press whatever the item is, which for a toggle is the opposite act."""
    # THE INVERSE AND THE WORD BOTH DRAWN, in that order of swaps: the
    # captured "Mute" becomes "Unmute", then the captured "Star" becomes "Mute".
    await page.set_content(
        w.world(swap={"Mute": "Unmute", "Star": "Mute"}), wait_until="domcontentloaded"
    )
    await page.click(cm.ACTIVE_TRIGGER, strict=True)
    assert (await cm.menu_item_gate(page, cm.MUTE))["proceed"] is False
    blind = cm.MenuAct(cm.MUTE, "Mute", "", cm.NOT_MUTED, cm.MUTED, cm.ACTS[cm.MUTE].family, True)
    monkeypatch.setitem(cm.ACTS, cm.MUTE, blind)
    assert (await cm.menu_item_gate(page, cm.MUTE))["proceed"] is True


# ---------------------------------------------------------------------------
# 4. The write, end to end over frozen worlds
# ---------------------------------------------------------------------------


async def test_the_preview_reads_behind_the_guard_and_mints_one_token(writes_on, page):
    nav = _Navigator(thread=[w.world()])
    block = await preview(spec_for_action(cm.MUTE), target=THREAD, navigator=nav, page=page)
    assert nav.gotos == [threads.COMPOSE_URL, THREAD_URL]
    assert block["direction"]["currently"] == cm.NOT_MUTED and block["direction"]["after"] == cm.MUTED
    shown = block["where"]["what_the_page_showed"]
    assert shown["menu"]["nothing_inside_the_menu_was_pressed"] is True
    assert shown["menu"]["menu_closed_again"] is True
    assert shown["receipt_guard"]["unread_positions"] == []
    assert isinstance(block["to_confirm"], str) and block["to_confirm"]
    assert await _witness(page) == {"trigger": 1, "escape": 1, "items": {}, "dialog": 0}
    # WHOSE CONVERSATION, named the way a reply's preview names it
    # (PREVIEW-NAMES-THE-RESOLVED-TARGET): the header's one title, as a record --
    # here the skeleton's reduced title -- in the block he reads, never on the grant.
    assert "whose_conversation" in block and "whose_conversation_check" in block
    assert "who_this_would_reach" not in block
    assert "whose_conversation" not in json.dumps(writes._GRANTS[block["to_confirm"]].preview)


async def test_the_preview_refuses_an_unread_list_a_wrong_landing_and_a_wrong_state(
    writes_on, page
):
    nav = _Navigator(thread=[w.world()], listing=LIST_UNREAD)
    with pytest.raises(WriteAttemptError, match="receipt guard refused"):
        await preview(spec_for_action(cm.MUTE), target=THREAD, navigator=nav, page=page)
    assert nav.gotos == [threads.COMPOSE_URL], "a refused guard opened the conversation"

    nav = _Navigator(thread=[w.world()], landed="https://www.linkedin.com/messaging/thread/2-OTHER/")
    with pytest.raises(WriteAttemptError, match="did not land on the conversation"):
        await preview(spec_for_action(cm.MUTE), target=THREAD, navigator=nav, page=page)

    nav = _Navigator(thread=[w.muted_world()])
    with pytest.raises(WriteAttemptError, match="valid only from"):
        await preview(spec_for_action(cm.MUTE), target=THREAD, navigator=nav, page=page)
    assert not writes._GRANTS, "a refused preview minted a grant"

    with pytest.raises(WriteAttemptError, match="thread id"):
        await preview(spec_for_action(cm.MUTE), target="not a thread", navigator=nav, page=page)


async def test_mute_presses_the_trigger_then_the_item_and_a_fresh_render_reads_it_muted(
    writes_on, page
):
    nav = _Navigator(thread=[w.world(), w.world(), w.muted_world()])
    grant, _block = await _granted(page, cm.MUTE, nav)
    receipt = await perform(nav, page, grant)
    assert nav.gotos == [threads.COMPOSE_URL, THREAD_URL, THREAD_URL, THREAD_URL]
    # THE PAGE'S OWN WITNESS of the act's page, read when the fresh render replaced it.
    assert nav.pressed[-1] == {"trigger": 1, "escape": 0, "items": {"Mute": 1}, "dialog": 0}
    assert receipt["clicked"]["clicks_made"] == 2 and receipt["clicked"]["opener_clicks"] == 1
    assert receipt["menu_gate"]["proceeded"] is True
    assert receipt["verification"]["observed_state"] == cm.MUTED
    assert receipt["performed"] is True


async def test_a_menu_already_muted_at_click_time_is_closed_and_nothing_is_pressed(
    writes_on, page
):
    nav = _Navigator(thread=[w.world(), w.muted_world()])
    grant, _block = await _granted(page, cm.MUTE, nav)
    receipt = await perform(nav, page, grant)
    assert receipt["menu_gate"]["refused_condition"] == "1_inverse_drawn"
    assert receipt["clicked"]["closer_clicks"] == 1
    assert await _witness(page) == {"trigger": 2, "escape": 0, "items": {}, "dialog": 0}
    assert receipt["verification"]["observed_state"] == cm.NOT_CHANGED
    assert receipt["verification"]["read_from"] == ""
    assert receipt["performed"] is False
    assert nav.gotos[-1] == THREAD_URL and len(nav.gotos) == 3, "a refused item still loaded again"


async def test_the_unread_mark_is_read_back_in_place_without_a_new_load(writes_on, page):
    after = {"Mark as unread": {"swap": {"Mark as unread": "Mark as read"}}}
    nav = _Navigator(thread=[w.world(), w.world(after=after)])
    grant, _block = await _granted(page, cm.MARK_UNREAD, nav)
    receipt = await perform(nav, page, grant)
    assert nav.gotos == [threads.COMPOSE_URL, THREAD_URL, THREAD_URL], "the verification loaded again"
    presses = await _witness(page)
    assert presses["items"] == {"Mark as unread": 1}
    assert receipt["verification"]["observed_state"] == cm.UNREAD
    assert receipt["performed"] is True


async def test_archive_reads_a_fresh_render_and_its_positive_is_the_derived_one(
    writes_on, page
):
    nav = _Navigator(thread=[w.world(), w.world(), w.no_active_row_world()])
    grant, _block = await _granted(page, cm.ARCHIVE, nav)
    receipt = await perform(nav, page, grant)
    assert receipt["verification"]["observed_state"] == cm.ARCHIVED
    assert "DERIVED" in receipt["verification"]["why"]
    assert receipt["performed"] is True

    nav = _Navigator(thread=[w.world(), w.world(), w.world()])
    grant, _block = await _granted(page, cm.ARCHIVE, nav)
    receipt = await perform(nav, page, grant)
    assert receipt["verification"]["observed_state"] == cm.NOT_CHANGED
    assert receipt["performed"] is False


async def test_delete_presses_the_item_counts_the_dialog_and_answers_nothing(writes_on, page):
    dialog = (
        "<h2>x</h2><button type='button'>Delete</button>"
        "<button type='button'>Cancel</button>"
    )
    after = {"Delete conversation": {"dialog": dialog}}
    nav = _Navigator(thread=[w.world(), w.world(after=after)])
    grant, block = await _granted(page, cm.DELETE, nav)
    assert block["verification"]["outcome_is_verifiable"] == "NO"
    assert block["irreversible"] is True
    receipt = await perform(nav, page, grant)
    after_press = receipt["menu_gate"]["after_the_item_press"]
    assert after_press["dialogs"] == 1 and after_press["further_step_opened"] is True
    assert after_press["dialog_words"]["Delete"] == 1 and after_press["dialog_words"]["Cancel"] == 1
    presses = await _witness(page)
    assert presses["items"] == {"Delete conversation": 1} and presses["dialog"] == 0
    assert receipt["performed"] == "unknown"
    assert receipt["verification"]["outcome_is_verifiable"] == "NO"
    assert nav.gotos == [threads.COMPOSE_URL, THREAD_URL, THREAD_URL], "a receipt-only act loaded again"


async def test_a_wrong_landing_at_the_act_presses_nothing(writes_on, page):
    nav = _Navigator(thread=[w.world()])
    grant, _block = await _granted(page, cm.MUTE, nav)
    nav.landed = "https://www.linkedin.com/messaging/thread/2-OTHER/"
    with pytest.raises(WriteAttemptError, match="landed somewhere that is not that"):
        await perform(nav, page, grant)
    assert nav.pressed[-1] == {"trigger": 1, "escape": 1, "items": {}, "dialog": 0}


# ---------------------------------------------------------------------------
# 5. The surface: off by default, the id checked first, the sanctions declared
# ---------------------------------------------------------------------------


async def test_writes_off_refuses_before_any_load_and_a_bad_id_too(monkeypatch):
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    for name in (
        "linkedin_set_conversation_muted", "linkedin_unset_conversation_muted",
        "linkedin_mark_conversation_unread", "linkedin_set_conversation_archived",
        "linkedin_set_conversation_deleted",
    ):
        tool = getattr(server, name)
        assert (await tool(THREAD))["error"] == "writes_disabled"
        refused = await tool("not a thread id")
        assert refused["error"] == "bad_argument" and "not a thread id" not in json.dumps(refused)


def test_the_preview_press_is_declared_and_nothing_else_in_the_module_mutates():
    path = "linkedin_server/conversation_menu.py"
    text = (w.LIVE11.parent.parent.parent / path).read_text(encoding="utf-8")
    sanctioned, unsanctioned = readonly.partition_mutation_hits(path, text)
    assert unsanctioned == []
    assert sorted((kind for _line, kind, _src in sanctioned)) == ["click", "press"]
    assert (path, "_open", "click") in readonly.SANCTIONED_MUTATIONS
    assert (path, "_close", "press") in readonly.SANCTIONED_MUTATIONS


def test_the_five_specs_are_performable_on_the_thread_address_and_delete_is_receipt_only():
    for action in cm.ACTIONS:
        spec = spec_for_action(action)
        assert action in writes.PERFORMABLE and action in writes.STRICT_PRESS_ACTIONS
        assert spec.state_from == cm.STATE_FROM and spec.target_kind == "thread_id"
        assert spec.click_from_state == cm.MENU_CLOSED != spec.from_state
        assert spec.not_performed_state == cm.NOT_CHANGED
        assert writes.anchor_label_for(spec) == cm.act_for(action).word
        assert writes.url_target_of(spec, THREAD) == THREAD
        assert spec.url_template.format(target=THREAD) == THREAD_URL
        assert readonly.name_implies_write(spec.tool_name)
    assert spec_for_action(cm.DELETE).unverifiable is not None
    assert spec_for_action(cm.DELETE).irreversible is True
    assert all(spec_for_action(a).unverifiable is None for a in cm.ACTIONS if a != cm.DELETE)
