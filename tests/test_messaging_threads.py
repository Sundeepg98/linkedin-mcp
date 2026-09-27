"""The receipt-safe inbox: a list that opens nothing, a guard that refuses to
open a conversation while anything reads unread, and a thread reader that
returns counts. Census rows ``M M43``, ``M M49`` and ``M M33``'s route.

WHAT IS MEASURED AND WHAT IS NOT, so no test here claims more. The two
synthetic fixtures carry STRUCTURE measured off two gitignored captures of
2026-09-20 (the composer and a conversation LinkedIn chose to open), with
invented content; each file's header says which parts are measured and which
are derived. Every UNREAD world, every world with a message HE sent, and the
drawn seen receipt are DERIVED here by asserted edits, and labelled.

NOTHING HERE REACHES LINKEDIN. Every page is a fixture served into a local
headless Chromium.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from linkedin_server import server, threads
from tests.test_apply_modal_fixture import over  # noqa: F401 -- fixture
from tests.test_writes import browser_page  # noqa: F401 -- fixture

_SYNTHETIC = Path(__file__).parent / "fixtures" / "synthetic"
COMPOSE_LIST = (_SYNTHETIC / "messaging_compose_list.html").read_text(encoding="ascii")
THREAD = (_SYNTHETIC / "messaging_thread.html").read_text(encoding="ascii")

#: Invented, shape-valid thread ids -- a digit first, the id alphabet after.
THREAD_ID = "2-SYNTHETICTHREADAAAA=="
OTHER_THREAD_ID = "2-SYNTHETICTHREADBBBB=="

#: What the fixtures' OTHER side wrote, and their names. Nothing any function
#: in ``threads`` returns may carry one of these (the preview's title aside,
#: which is ``test_send_reply.py``'s subject).
THEIR_WORDS = (
    "Would Thursday work for a short call?",
    "Hello, is the example role still open?",
    "Thanks for the note about the fixture schedule.",
)
THEIR_NAMES = ("Kai Example", "Juno Fixture", "Ivo Placeholder", "Lea Sample")


def _derive(source: str, old: str, new: str, count: int = 1) -> str:
    """An ASSERTED edit: a replace whose anchor drifted is a silent no-op, and
    a test run against the unedited page would pass for the wrong reason."""
    derived = source.replace(old, new, count)
    assert derived != source, f"the derivation anchored on {old!r} changed nothing"
    return derived


def _clean(value) -> None:
    text = json.dumps(value)
    for needle in THEIR_WORDS + THEIR_NAMES + (THREAD_ID, OTHER_THREAD_ID):
        assert needle not in text, f"{needle!r} leaked into: {text[:400]}"


# DERIVED unread worlds -- one signal each, on row 2 of the composer's list.
_ROW_TWO_CARD = 'aria-label="Select conversation with Juno Fixture"></label>'
UNREAD_BY_CLASS = _derive(
    COMPOSE_LIST,
    '<h3 class="msg-conversation-listitem__participant-names msg-conversation-card__participant-names t-16 t-black t-normal"><div><span>Juno Fixture',
    '<h3 class="msg-conversation-listitem__participant-names msg-conversation-card__participant-names t-16 t-black t-bold msg-conversation-card__convo-item-container--unread"><div><span>Juno Fixture',
)
UNREAD_BY_WORD = _derive(
    COMPOSE_LIST, _ROW_TWO_CARD, _ROW_TWO_CARD + '<span class="visually-hidden">Unread</span>'
)
UNREAD_BY_BADGE = _derive(
    COMPOSE_LIST, _ROW_TWO_CARD, _ROW_TWO_CARD + '<span class="notification-badge notification-badge--show">1</span>'
)
UNREAD_BY_ARIA = _derive(
    COMPOSE_LIST, _ROW_TWO_CARD, _ROW_TWO_CARD + '<span aria-label="1 Unread message" role="img"></span>'
)


# ---------------------------------------------------------------------------
# 1. The addresses: a thread id is a tool argument, compared, never extracted
# ---------------------------------------------------------------------------


def test_a_thread_url_is_built_from_the_constant_and_a_valid_id_only():
    assert threads.thread_url(THREAD_ID) == (
        "https://www.linkedin.com/messaging/thread/" + THREAD_ID + "/"
    )
    for bad in ("", "new", "abc", "2-x/../compose", "2-x?recipient=1", "2 x", None, 7, "9" * 201):
        with pytest.raises(Exception) as excinfo:
            threads.thread_url(bad)
        assert "Nothing was opened" in str(excinfo.value)


def test_the_thread_shape_is_the_read_allowlists_own():
    """Every url this module can build passes the unrelaxed read door."""
    from linkedin_server import readonly

    assert readonly.is_read_url(threads.thread_url(THREAD_ID))
    assert readonly.is_read_url(threads.COMPOSE_URL)
    assert not readonly.is_read_url(
        "https://www.linkedin.com/messaging/thread/new/?recipient=1"
    )


@pytest.mark.parametrize(
    "landed, expected",
    [
        ("https://www.linkedin.com/messaging/thread/" + THREAD_ID + "/", True),
        ("https://www.linkedin.com/messaging/thread/" + THREAD_ID, True),
        ("https://www.linkedin.com/messaging/thread/" + THREAD_ID + "/?filter=unread", True),
        ("https://www.linkedin.com/messaging/thread/" + OTHER_THREAD_ID + "/", False),
        ("https://www.linkedin.com/messaging/", False),
        ("https://www.linkedin.com/messaging/compose/", False),
        ("http://www.linkedin.com/messaging/thread/" + THREAD_ID + "/", False),
        ("https://example.invalid/messaging/thread/" + THREAD_ID + "/", False),
        ("", False),
        (None, False),
    ],
)
def test_the_landing_comparison_is_exact_on_the_path(landed, expected):
    assert threads.landed_on_thread(landed, THREAD_ID) is expected


# ---------------------------------------------------------------------------
# 2. The list: opens nothing, and unread is paired to the row
# ---------------------------------------------------------------------------


async def test_the_composer_list_reads_rows_placeholders_and_no_open_conversation(over):
    reading = await over(COMPOSE_LIST, threads.read_conversation_list)
    assert reading["error"] is None
    assert reading["rows_total"] == 5
    assert reading["rows_rendered"] == 3
    assert reading["rows_placeholder"] == 2
    assert [r["unread"] for r in reading["rows"]] == [False, False, False, None, None]
    assert [r["group"] for r in reading["rows"][:3]] == [False, False, True]
    assert reading["message_events"] == 0 and reading["active_rows"] == 0
    assert {p["name"] for p in reading["pills"]} == {
        "jobs", "unread", "connections", "inmail", "starred"
    }
    assert all(p["pressed"] is False for p in reading["pills"])
    _clean(reading)


async def test_names_cross_only_when_asked_for(over):
    async def named(page):
        return await threads.read_conversation_list(page, include_names=True)

    reading = await over(COMPOSE_LIST, named)
    assert [r.get("name") for r in reading["rows"]] == [
        "Kai Example", "Juno Fixture", "Ivo Placeholder, Lea Sample", None, None
    ]
    unnamed = threads.list_result(
        await over(COMPOSE_LIST, threads.read_conversation_list),
        threads.COMPOSE_URL,
        include_names=False,
    )
    assert {r.get("name") for r in unnamed["rows"] if r["rendered"]} == {"<NAME>"}
    _clean(unnamed)


@pytest.mark.parametrize(
    "world, signal",
    [
        (UNREAD_BY_CLASS, "class"),
        (UNREAD_BY_WORD, "word"),
        (UNREAD_BY_BADGE, "badge"),
        (UNREAD_BY_ARIA, "word"),
    ],
    ids=["class-token", "hidden-word", "badge", "accessible-name"],
)
async def test_each_unread_signal_marks_its_own_row_and_no_other(over, world, signal):
    """DERIVED worlds: no capture holds an unread row in the current markup."""
    reading = await over(world, threads.read_conversation_list)
    assert [r["unread"] for r in reading["rows"]][:3] == [False, True, False]
    assert signal in reading["rows"][1]["signals"]


def test_the_list_result_names_its_evidence_that_nothing_opened():
    reading = {
        "rows_total": 1, "rows_rendered": 1, "rows_placeholder": 0,
        "rows": [{"position": 1, "rendered": True, "unread": False, "signals": [], "group": False}],
        "message_events": 0, "active_rows": 0, "pills": [], "error": None,
    }
    result = threads.list_result(reading, threads.COMPOSE_URL, include_names=False)
    assert result["opened_a_conversation"]["opened"] is False
    assert result["opened_a_conversation"]["landed_on_the_composer"] is True
    assert "NONE" in result["thread_ids"]
    # The same reading, on a page that drew a conversation: opened.
    opened = threads.list_result(
        {**reading, "message_events": 1}, threads.COMPOSE_URL, include_names=False
    )
    assert opened["opened_a_conversation"]["opened"] is True
    moved = threads.list_result(reading, "https://www.linkedin.com/messaging/thread/" + THREAD_ID + "/", include_names=False)
    assert moved["opened_a_conversation"]["opened"] is True


# ---------------------------------------------------------------------------
# 3. The receipt guard
# ---------------------------------------------------------------------------


async def test_the_guard_passes_a_list_with_nothing_unread_and_states_its_residue(over):
    guard = threads.receipt_guard(
        await over(COMPOSE_LIST, threads.read_conversation_list),
        allow_unread=False,
        landed=threads.COMPOSE_URL,
    )
    assert guard["proceed"] is True
    assert guard["unread_positions"] == []
    assert "WHAT THIS DOES NOT COVER" in guard["why"]


async def test_the_guard_refuses_any_unread_row_because_a_row_has_no_thread_id(over):
    guard = threads.receipt_guard(
        await over(UNREAD_BY_CLASS, threads.read_conversation_list),
        allow_unread=False,
        landed=threads.COMPOSE_URL,
    )
    assert guard["proceed"] is False
    assert guard["unread_positions"] == [2]
    assert "carries no thread id" in guard["why"]
    _clean(guard)


async def test_allow_unread_is_the_only_way_past_an_unread_row(over):
    reading = await over(UNREAD_BY_WORD, threads.read_conversation_list)
    assert threads.receipt_guard(reading, allow_unread=True, landed=threads.COMPOSE_URL)["proceed"] is True
    assert threads.receipt_guard(reading, allow_unread=False, landed=threads.COMPOSE_URL)["proceed"] is False


async def test_a_list_page_that_opened_a_conversation_refuses_even_with_the_opt_in(over):
    """The thread fixture has a conversation open and a row marked active: it
    is NOT the composer's shape, and no opt-in makes it one."""
    reading = await over(THREAD, threads.read_conversation_list)
    assert reading["message_events"] == 3 and reading["active_rows"] == 1
    for allow in (False, True):
        guard = threads.receipt_guard(reading, allow_unread=allow, landed=threads.COMPOSE_URL)
        assert guard["proceed"] is False
        assert guard["list_page"]["opened"] is True


#: DERIVED -- the composer's list with an overlay conversation bubble open
#: OUTSIDE <main>. No capture holds one (the overlay is minimised on every
#: capture); LinkedIn can restore an open bubble from one page to the next.
COMPOSE_WITH_A_BUBBLE = _derive(
    COMPOSE_LIST,
    '<aside class="msg-overlay-container">',
    '<aside class="msg-overlay-container"><div class="msg-overlay-conversation-bubble">'
    '<ul><li class="msg-s-message-list__event"><div class="msg-s-event-listitem '
    'msg-s-event-listitem--other"><p class="msg-s-event-listitem__body">Words in a '
    "bubble.</p></div></li></ul></div>",
)


async def test_a_conversation_the_overlay_draws_counts_against_nothing_was_opened(over):
    """RECEIPT EVIDENCE IS PAGE-WIDE; AIM IS <main>. The bubble is not this
    page's conversation -- the thread reader ignores it (the next section) --
    but a list page that draws one HAS displayed a conversation, so the guard
    refuses, and the opt-in does not reach it."""
    reading = await over(COMPOSE_WITH_A_BUBBLE, threads.read_conversation_list)
    assert reading["message_events"] == 1 and reading["rows_rendered"] == 3
    for allow in (False, True):
        guard = threads.receipt_guard(reading, allow_unread=allow, landed=threads.COMPOSE_URL)
        assert guard["proceed"] is False
        assert guard["list_page"]["opened"] is True


def test_no_rendered_row_and_an_unreadable_list_both_refuse_by_default():
    empty = {"rows": [], "rows_placeholder": 3, "message_events": 0, "active_rows": 0, "error": None}
    assert threads.receipt_guard(empty, allow_unread=False)["proceed"] is False
    broken = {**empty, "error": "TimeoutError"}
    guard = threads.receipt_guard(broken, allow_unread=False)
    assert guard["proceed"] is False and "TimeoutError" in guard["why"]
    assert threads.receipt_guard(broken, allow_unread=True)["proceed"] is True


def test_a_landing_off_the_composer_refuses():
    reading = {
        "rows": [{"position": 1, "rendered": True, "unread": False}],
        "rows_placeholder": 0, "message_events": 0, "active_rows": 0, "error": None,
    }
    guard = threads.receipt_guard(
        reading, allow_unread=True, landed="https://www.linkedin.com/messaging/"
    )
    assert guard["proceed"] is False


# ---------------------------------------------------------------------------
# 4. The thread reader: counts, the reply box, the read indicator
# ---------------------------------------------------------------------------


async def test_the_thread_fixture_reads_as_measured(over):
    reading = await over(THREAD, threads.read_thread)
    assert reading["error"] is None and reading["rendered"] is True
    assert reading["events"] == 3
    assert reading["items_from_the_other_side"] == 2
    assert reading["last_from"] == "other"
    assert reading["last_event_marked_last"] is True
    assert reading["seen_without_marker"] == 1 and reading["seen_with_marker"] == 0
    assert reading["editors"] == 1 and reading["editor_label_matches"] is True
    assert reading["editor_empty"] is True
    assert reading["send_controls"] == 1 and reading["send_disabled"] is True
    assert reading["recipient_boxes"] == 0
    assert reading["file_inputs"] == 2
    assert reading["file_input_accepts"] == ["images", "images_and_documents"]
    assert reading["footer_actions"] == [
        "attach_image", "attach_file", "gif_keyboard", "emoji_keyboard"
    ]
    assert reading["titles"] == 1 and reading["sponsored"] is False
    assert threads.reply_state(reading)[0] == "reply_box_empty"
    assert threads.seen_state(reading)["state"] == "not_applicable"
    _clean(reading)
    _clean(threads.thread_facts(reading))


#: DERIVED -- a message HE sent as the last message: an item with NO --other
#: modifier, the last-msg marker moved onto it.
HIS_LAST = _derive(
    _derive(
        THREAD,
        '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">',
        '<li class="msg-s-message-list__event clearfix">',
    ),
    '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
    '<li class="msg-s-message-list__event clearfix msg-s-message-list__last-msg-">'
    '<div class="msg-s-event-listitem msg-s-event-listitem--last-in-group">'
    '<p class="msg-s-event-listitem__body t-14">Thursday works, speak then.</p></div></li>'
    '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
)
#: DERIVED -- the counterpart modifier, NEVER CAPTURED.
HIS_LAST_SEEN = _derive(
    HIS_LAST,
    # THE ELEMENT, not the class name alone: the fixture's own header comment
    # names the class first, and a count-of-one replace on the bare name
    # edited the comment and left the page unchanged -- which this test's
    # first run caught.
    '<li class="msg-s-message-list__typing-indicator-container--without-seen-receipt" id="typing"></li>',
    '<li class="msg-s-message-list__typing-indicator-container--with-seen-receipt" id="typing"></li>',
)


async def test_the_read_indicator_on_his_last_message_says_how_it_knows(over):
    not_seen = threads.seen_state(await over(HIS_LAST, threads.read_thread))
    assert (not_seen["state"], not_seen["evidence"]) == ("not_drawn", "measured")
    assert not_seen["last_from"] == "him" and "derived" in not_seen["last_from_evidence"]
    seen = threads.seen_state(await over(HIS_LAST_SEEN, threads.read_thread))
    assert (seen["state"], seen["evidence"]) == ("drawn", "derived")
    assert "NEVER CAPTURED" in seen["why"]


async def test_the_text_is_compared_inside_the_page_exactly(over):
    async def with_text(words):
        async def work(page):
            return await threads.read_thread(page, text=words)
        return await over(HIS_LAST, work)

    exact = await with_text("Thursday works, speak then.")
    assert exact["events_with_text"] == 1 and exact["last_has_text"] is True
    spaced = await with_text("  Thursday   works,  speak then.  ")
    assert spaced["events_with_text"] == 1, "whitespace is normalised"
    partial = await with_text("Thursday works")
    assert partial["events_with_text"] == 0 and partial["last_has_text"] is False
    cased = await with_text("thursday works, speak then.")
    assert cased["events_with_text"] == 0, "the match is exact, case included"
    theirs = await with_text("Hello, is the example role still open?")
    assert theirs["events_with_text"] == 1 and theirs["last_has_text"] is False
    _clean({k: v for k, v in exact.items()})


SPONSORED = _derive(
    _derive(THREAD, '<div class="msg-thread msg-thread--pillar">',
            '<div class="msg-thread msg-thread--pillar msg-sponsored-conversation-thread">'),
    THREAD[THREAD.index('<form class="msg-form'):THREAD.index("</form>") + len("</form>")],
    '<div class="msg-s-sponsored-message-actions">'
    '<button type="button">I want to know more!</button>'
    '<button type="button">Not interested</button>'
    '<button type="button">Kai Example says hello</button></div>',
)
DRAFT = _derive(
    _derive(THREAD, 'id="reply-editor"></div>', 'id="reply-editor">an old draft</div>'),
    'id="reply-send" disabled>', 'id="reply-send">',
)
#: DERIVED -- the composer's own recipient box, in its measured shape, drawn
#: inside a conversation. The global search combobox the fixture already
#: carries is NOT this, and the next test shows the difference.
WITH_A_RECIPIENT_BOX = _derive(
    THREAD,
    '<form class="msg-form',
    '<div class="msg-connections-typeahead"><input class="msg-connections-typeahead__search-field" '
    'role="combobox" type="text"></div><form class="msg-form',
)
#: DERIVED -- an overlay conversation bubble open OUTSIDE <main>, with a form
#: and a message of its own. No capture holds one; the overlay's place outside
#: <main> is measured on both captures.
OVERLAY_BUBBLE = _derive(
    THREAD,
    "<script>",
    '<aside class="msg-overlay-container"><div class="msg-overlay-conversation-bubble">'
    '<ul><li class="msg-s-message-list__event"><div class="msg-s-event-listitem msg-s-event-listitem--other">'
    '<p class="msg-s-event-listitem__body">Words in another bubble.</p></div></li></ul>'
    '<form class="msg-form"><div class="msg-form__contenteditable" contenteditable="true" role="textbox" '
    'aria-label="Write a message&#8230;">a draft in the bubble</div>'
    '<button type="submit" class="msg-form__send-button">Send</button></form></div></aside>'
    "<script>",
)


@pytest.mark.parametrize(
    "world, fragment",
    [
        (SPONSORED, "SPONSORED conversation"),
        (DRAFT, "NOT EMPTY"),
        (WITH_A_RECIPIENT_BOX, "recipient box"),
        ("<html><body><p>nothing</p></body></html>", "had not arrived"),
    ],
    ids=["sponsored", "draft-present", "recipient-box", "unrendered"],
)
async def test_every_other_reply_box_state_is_unknown_and_says_why(over, world, fragment):
    reading = await over(world, threads.read_thread)
    state, why = threads.reply_state(reading)
    assert state == "unknown" and fragment in why
    _clean(why)


async def test_the_global_search_box_is_a_combobox_and_not_a_recipient_box(over):
    """THE DEFECT THE FIRST VERSION SHIPPED WITH, as a control. LinkedIn's
    global search input is a ``role=combobox`` on every page -- measured on
    both captures -- and the first recipient-box selector was that role alone,
    so every real conversation would have read as "not a conversation"."""

    async def counts(page):
        return (
            await page.locator('[role="combobox"]').count(),
            await page.locator(threads.RECIPIENT_BOX_SELECTOR).count(),
        )

    assert await over(THREAD, counts) == (1, 0)
    assert await over(WITH_A_RECIPIENT_BOX, counts) == (2, 1)


async def test_the_composer_is_not_a_conversation_and_its_recipient_box_says_so(over):
    """The count that CAN fail, failing where it should: the composer draws
    its own typeahead, and nothing may be typed there as a reply."""
    reading = await over(COMPOSE_LIST, threads.read_thread)
    assert reading["recipient_boxes"] == 1
    state, why = threads.reply_state(reading)
    assert state == "unknown" and "recipient box" in why


async def test_an_open_overlay_bubble_is_not_this_conversation(over):
    """Everything is scoped to <main>; the bubble's form, draft and message
    are outside it and none of them is counted."""
    reading = await over(OVERLAY_BUBBLE, threads.read_thread)
    assert reading["editors"] == 1 and reading["editor_empty"] is True
    assert reading["events"] == 3 and reading["send_controls"] == 1
    assert threads.reply_state(reading)[0] == "reply_box_empty"


async def test_response_buttons_are_a_closed_vocabulary(over):
    reading = await over(SPONSORED, threads.read_thread)
    assert reading["response_controls"] == ["want_to_know_more", "not_interested", "unrecognised"]
    _clean(reading)


# ---------------------------------------------------------------------------
# 5. The tools, driven over the fixtures with no LinkedIn behind them
# ---------------------------------------------------------------------------


class _FixtureBrowser:
    """Stands where ``server.BROWSER`` stands: serves frozen worlds into ONE
    real local page, lands where the map says, and RECORDS every ask."""

    def __init__(self, page, pages: dict[str, tuple[str, str]]):
        self.page = page
        self.pages = dict(pages)
        self.gotos: list[str] = []

    def session(self):
        browser = self

        class _Session:
            async def __aenter__(self):
                return browser.page

            async def __aexit__(self, *exc):
                return False

        return _Session()

    async def goto(self, page, url: str) -> str:
        from linkedin_server import readonly

        readonly.assert_read_url(url)
        self.gotos.append(url)
        if url not in self.pages:
            raise AssertionError(f"the tool asked for {url!r}, which this test did not freeze")
        html, landed = self.pages[url]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


async def test_the_list_tool_opens_nothing_and_returns_no_name_by_default(monkeypatch, browser_page):
    fake = _FixtureBrowser(browser_page, {threads.COMPOSE_URL: (COMPOSE_LIST, threads.COMPOSE_URL)})
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_list_conversations()
    assert fake.gotos == [threads.COMPOSE_URL]
    assert result["opened_a_conversation"]["opened"] is False
    assert result["rows_rendered"] == 3 and result["unread_rendered"] == 0
    assert result["pages_loaded"] == 1
    _clean(result)


async def test_the_open_thread_tool_refuses_before_loading_the_thread_while_a_row_is_unread(
    monkeypatch, browser_page
):
    url = threads.thread_url(THREAD_ID)
    fake = _FixtureBrowser(
        browser_page,
        {threads.COMPOSE_URL: (UNREAD_BY_BADGE, threads.COMPOSE_URL), url: (THREAD, url)},
    )
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_thread(THREAD_ID)
    assert result["refused"] is True and result["opened_a_conversation"] is False
    assert fake.gotos == [threads.COMPOSE_URL], "the conversation was loaded after a refusal"
    _clean(result)


async def test_the_open_thread_tool_reads_counts_when_nothing_is_unread(monkeypatch, browser_page):
    url = threads.thread_url(THREAD_ID)
    fake = _FixtureBrowser(
        browser_page,
        {threads.COMPOSE_URL: (COMPOSE_LIST, threads.COMPOSE_URL), url: (HIS_LAST, url)},
    )
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_thread(THREAD_ID)
    assert fake.gotos == [threads.COMPOSE_URL, url]
    assert result["refused"] is False and result["landed_on_the_named_thread"] is True
    assert result["read_indicator"]["state"] == "not_drawn"
    assert result["reply_box"]["state"] == "reply_box_empty"
    assert result["pages_loaded"] == 2
    _clean(result)


async def test_the_open_thread_tool_does_not_read_a_conversation_it_was_redirected_into(
    monkeypatch, browser_page
):
    url = threads.thread_url(THREAD_ID)
    elsewhere = threads.thread_url(OTHER_THREAD_ID)
    fake = _FixtureBrowser(
        browser_page,
        {threads.COMPOSE_URL: (COMPOSE_LIST, threads.COMPOSE_URL), url: (THREAD, elsewhere)},
    )
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_thread(THREAD_ID)
    assert result["refused"] is True and result["landed_on_the_named_thread"] is False
    assert "conversation" not in result
    _clean(result)


async def test_a_malformed_thread_id_is_refused_before_any_load(monkeypatch, browser_page):
    fake = _FixtureBrowser(browser_page, {})
    monkeypatch.setattr(server, "BROWSER", fake)
    result = await server.linkedin_open_thread("new")
    assert "error" in result and fake.gotos == []


async def test_open_messaging_is_guarded_before_it_asks_for_the_inbox(monkeypatch, browser_page):
    """``M M33`` / ``M M43``'s tool: an unread row refuses and /messaging/ is
    never asked for; nothing unread lets it through, two loads."""
    from linkedin_server.config import MESSAGING_URL

    landed_thread = threads.thread_url(THREAD_ID)
    refused = _FixtureBrowser(
        browser_page,
        {threads.COMPOSE_URL: (UNREAD_BY_CLASS, threads.COMPOSE_URL),
         MESSAGING_URL: (THREAD, landed_thread)},
    )
    monkeypatch.setattr(server, "BROWSER", refused)
    result = await server.linkedin_open_messaging()
    assert result["refused"] is True and refused.gotos == [threads.COMPOSE_URL]

    allowed = _FixtureBrowser(
        browser_page,
        {threads.COMPOSE_URL: (COMPOSE_LIST, threads.COMPOSE_URL),
         MESSAGING_URL: (THREAD, landed_thread)},
    )
    monkeypatch.setattr(server, "BROWSER", allowed)
    result = await server.linkedin_open_messaging()
    assert allowed.gotos == [threads.COMPOSE_URL, MESSAGING_URL]
    assert result["pages_loaded"] == 2
    assert result["receipt_guard"]["proceed"] is True
    assert result["landed_conversation"]["read_indicator"]["state"] == "not_applicable"
    assert THREAD_ID not in json.dumps(result)
