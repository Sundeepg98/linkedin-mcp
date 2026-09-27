"""Messaging threads: a receipt-safe inbox, a reply gate, and a send that can
confirm itself.

WHY THIS MODULE EXISTS
----------------------
Two blocks, each measured twice.

1. **The inbox reads were held.** Asking LinkedIn for ``/messaging/`` does not
   stay on a list: it redirects into ONE conversation of LinkedIn's choosing,
   and opening an unread conversation can show its sender a "seen" receipt --
   an effect on another person. The live lane held three census rows on that
   cost at 22:14 and again at 23:26 on 2026-09-23.
2. **A send could not confirm itself.** ``linkedin_send_message``'s docstring
   said it can report NOT SENT and can never report SENT, because the only
   surface that could confirm a send is the thread -- then forbidden. Ruling
   ``WRITE-CLASS-B`` (2026-09-23 18:15) lifted that: the thread may be read.

WHAT THE CAPTURES SAID, and the design follows from it rather than from the
brief's first guess (``_audit/2026-09-24-lane-l5-messaging.md`` section 1):

* ``/messaging/compose/`` -- an address this server already loads by exact-url
  exemption -- draws the WHOLE conversation list and opens NO conversation:
  zero ``li.msg-s-message-list__event``, zero rows wearing the active marker,
  against one of each on ``/messaging/`` captured the same minute. **That is
  the receipt-free list.**
* A list row carries NO thread identifier -- no urn, no thread path, no
  ``2-`` token on any attribute of any row or descendant, and no conversation
  entity in any data payload. So a listing CANNOT say whether a particular,
  caller-supplied thread id is unread. The receipt guard below therefore
  refuses on ANY unread rendered row rather than on "the" row, because it
  cannot tell which row a thread id is.
* The minimised messaging overlay on every other admitted page draws no rows
  at all, so it is not a list.

THE PRIVACY SHAPE
-----------------
Every reader here is a LOCATOR CHAIN, not an injected script, and it spends
no ``evaluate`` waiver: ``tests/test_readonly.py`` holds that budget to
``dom.py`` and forces the question "could this be a locator chain?" -- here it
could. Comparisons happen INSIDE THE PAGE through Playwright's own text engine
(``get_by_text(..., exact=True)`` inside ``filter(has=...)``), so what crosses
into this process is a count. **No message body, no correspondent's name and
no thread identifier is returned by any function in this module**, with two
deliberate, named exceptions: the conversation list's names when the caller
passes ``include_names`` (his own inbox, opt-in, as ``linkedin_open_messaging``
already offers), and the reply preview's ``who_this_would_reach``, printed in
the confirm block only -- see :func:`name_the_reply_recipient`.

A THREAD ID IS ONLY EVER A TOOL ARGUMENT. It is validated against the same
shape the read allowlist admits, formatted into one constant template, and
compared against a landing -- never read off a page and never returned.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import coerce, landing, shape
from linkedin_server.errors import WriteAttemptError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 1. Addresses
# ---------------------------------------------------------------------------

#: The composer. On the read allowlist by an EXACT-url exemption since
#: 2026-08-31, and the one messaging address measured to open no conversation.
COMPOSE_URL = "https://www.linkedin.com/messaging/compose/"

#: One conversation, by the id HE supplies. Formatted from this constant and
#: nothing else, so the only variable part of the address is a tool argument.
THREAD_URL_TEMPLATE = "https://www.linkedin.com/messaging/thread/{thread_id}/"

#: THE SHAPE THE READ ALLOWLIST ADMITS, and no looser: a digit first (the
#: 2026-09-03 tightening -- ``new`` is a word, every recorded thread id starts
#: with a digit), then the id alphabet including base64 padding and percent
#: escapes. The length cap is this module's, so a pasted paragraph is refused
#: here with a sentence rather than at the read door with a pattern.
_THREAD_ID_SHAPE = re.compile(r"^[0-9][A-Za-z0-9%\-_=]{0,199}$")
_THREAD_PATH_PREFIX = "/messaging/thread/"


def valid_thread_id(thread_id: Any) -> bool:
    """Is this a thread id this module would put into an address?"""
    return isinstance(thread_id, str) and bool(_THREAD_ID_SHAPE.match(thread_id.strip()))


def thread_url(thread_id: Any) -> str:
    """The address of ONE conversation, from a caller-supplied id. Or raise.

    The refusal names the SHAPE and not the value: the value is his argument
    and he already holds it, and a refusal is text that reaches transcripts.
    """
    if not valid_thread_id(thread_id):
        raise WriteAttemptError(
            "that is not a LinkedIn thread id this server will open. A thread "
            "id is the part of a conversation's address after "
            "'/messaging/thread/' -- it starts with a digit and holds only "
            "letters, digits, '-', '_', '=' and '%'. Copy it from the address "
            "bar of the conversation in your own browser. Nothing was opened."
        )
    return THREAD_URL_TEMPLATE.format(thread_id=str(thread_id).strip())


def landed_on_thread(landed: Any, thread_id: Any) -> bool:
    """Did the browser land on the conversation that was asked for?

    A COMPARISON AND NOTHING ELSE: the landing is LinkedIn's string, the id is
    his, and only a boolean leaves. Scheme, host and path must match exactly
    (a trailing slash aside); a query is LinkedIn's own view state and cannot
    re-address a conversation, so it is not compared.

    WHY THIS MATTERS MORE HERE THAN ANYWHERE: an id LinkedIn does not
    recognise can be redirected to ``/messaging/``, which lands in a DIFFERENT
    conversation of LinkedIn's choosing. A reply aimed by a mistyped id would
    then be typed into somebody else's thread. Every step that acts or reads
    on a thread checks this first.
    """
    if not valid_thread_id(thread_id):
        return False
    parts = urlsplit(str(landed or ""))
    return (
        parts.scheme == "https"
        and parts.netloc == "www.linkedin.com"
        and parts.path.rstrip("/") == _THREAD_PATH_PREFIX + str(thread_id).strip()
    )


def is_a_thread_address(url: Any) -> bool:
    """Is ``url`` SOME conversation's address? The id is never extracted."""
    parts = urlsplit(str(url or ""))
    return (
        parts.scheme == "https"
        and parts.netloc == "www.linkedin.com"
        and parts.path.startswith(_THREAD_PATH_PREFIX)
        and len(parts.path.rstrip("/")) > len(_THREAD_PATH_PREFIX)
    )


def is_the_compose_address(url: Any) -> bool:
    parts = urlsplit(str(url or ""))
    return (
        parts.scheme == "https"
        and parts.netloc == "www.linkedin.com"
        and parts.path.rstrip("/") == "/messaging/compose"
    )


# ---------------------------------------------------------------------------
# 2. Selectors, each one measured on a named capture unless it says DERIVED
# ---------------------------------------------------------------------------
#
# Measured 2026-09-20 on the composer and the inbox captures (gitignored, in
# the main checkout's _state/). Shapes and counts only were taken; the lane
# record section 1 carries the numbers.

#: EVERY PAGE-LEVEL SELECTOR BELOW IS SCOPED TO <main>, and that is
#: measured, not tidy: on both captures one <main>
#: (``main#main.scaffold-layout__list-detail.msg__list-detail``) holds the
#: list, the open conversation, the composer's form and the header, while
#: the messaging overlay and LinkedIn's global search sit OUTSIDE it. The
#: overlay can hold conversation bubbles with forms of their own, and the
#: search is a combobox; neither may be counted as this page's. The row- and
#: message-relative selectors are read inside a row or a message, so they
#: inherit the scope. Counted old spelling against scoped on both captures:
#: nothing moved but the recipient box (lane record, section 3.3). The ONE
#: page-wide exception is receipt evidence -- see EVIDENCE_EVENT_SELECTOR.
ROW_SELECTOR = "main li.msg-conversation-listitem"
#: 10 of the 20 rows on both captures -- virtualised placeholders, no content.
OCCLUDED_CLASS = "msg-conversation-card--occluded"
#: The row's clickable element: a div with tabindex=0 and NO href.
ROW_LINK_SELECTOR = ".msg-conversation-listitem__link"
PARTICIPANT_NAMES_SELECTOR = ".msg-conversation-card__participant-names"
GROUP_FACEPILE_SELECTOR = ".msg-facepile-grid__img--multiple-participants"
#: The row whose conversation is open. 0 on the composer, 1 on the inbox.
ACTIVE_ROW_SELECTOR = "main .msg-conversations-container__convo-item-link--active"
#: The filter pills: buttons, no href, a data-test hook naming each.
PILL_SELECTOR = "main button[data-test-messaging-inbox-filters__filter-pill]"
PILL_HOOK = "data-test-messaging-inbox-filters__filter-pill"

#: One message of an open conversation. 0 on the composer, 1 on the inbox.
EVENT_SELECTOR = "main li.msg-s-message-list__event"
ITEM_SELECTOR = ".msg-s-event-listitem"
#: RECEIPT EVIDENCE IS READ PAGE-WIDE, ON PURPOSE -- the one exception to
#: the <main> scoping above. "Did loading this page display anybody's
#: conversation?" is not a question about <main>: the overlay sits outside
#: it and can hold an open conversation bubble, and a list page that draws
#: one HAS displayed a conversation, whoever opened it. So the list's
#: evidence counts messages and active markers ANYWHERE on the page, while
#: every reader that AIMS -- what this conversation holds, what a reply
#: would type into -- counts inside <main> only. On both captures the two
#: spellings count the same (lane record, section 3.3).
EVIDENCE_EVENT_SELECTOR = "li.msg-s-message-list__event"
EVIDENCE_ACTIVE_ROW_SELECTOR = ".msg-conversations-container__convo-item-link--active"
#: MEASURED on the other party's message. His own carries no such modifier --
#: DERIVED: no capture holds a message he sent.
OTHER_ITEM_SELECTOR = ".msg-s-event-listitem--other"
#: Worn by the LAST event (measured on the one event the inbox capture drew).
LAST_MSG_CLASS = "msg-s-message-list__last-msg"
#: The container after the last event. The WITHOUT form is measured; the WITH
#: form is DERIVED as the BEM counterpart and has never been captured.
SEEN_WITHOUT_SELECTOR = (
    "main .msg-s-message-list__typing-indicator-container--without-seen-receipt"
)
SEEN_WITH_SELECTOR = (
    "main .msg-s-message-list__typing-indicator-container--with-seen-receipt"
)
SEEN_ANY_SELECTOR = "main [class*='seen-receipt']"

#: The reply form. Measured on the COMPOSER, whose form wears
#: ``msg-form--thread-footer-feature`` -- the thread footer's own component.
#: That a thread draws the same form is DERIVED; the first live preview of a
#: reply measures it (every count below is in the preview's facts).
REPLY_FORM_SELECTOR = "main form.msg-form"
REPLY_EDITOR_SELECTOR = 'main form.msg-form div.msg-form__contenteditable[role="textbox"]'
REPLY_SEND_SELECTOR = 'main form.msg-form button.msg-form__send-button[type="submit"]'
#: The editor's accessible name, measured: 'Write a message' + U+2026.
REPLY_EDITOR_LABEL = "Write a message\u2026"
FILE_INPUT_SELECTOR = 'main form.msg-form input[type="file"]'
#: A thread has nobody to choose, so a MESSAGING recipient box here means it
#: is not a thread. NOT ``[role=combobox]`` alone, and that was this module's
#: first version: LinkedIn's global search input is a combobox on EVERY page
#: (measured on both captures), so a bare role count read every real
#: conversation as "not a conversation" and no reply could ever have been
#: typed. The recipient box is the composer's own typeahead, measured as
#: ``input.msg-connections-typeahead__search-field`` inside
#: ``div.msg-connections-typeahead``.
RECIPIENT_BOX_SELECTOR = (
    'main .msg-connections-typeahead [role="combobox"], '
    "main input.msg-connections-typeahead__search-field"
)
TEXTBOX_SELECTOR = 'main [role="textbox"]'

#: The correspondent's name in the conversation header -- exactly one.
TITLE_SELECTOR = "main .msg-entity-lockup__entity-title"
#: The conversation the inbox capture opened was SPONSORED: no reply form,
#: response buttons instead.
SPONSORED_SELECTOR = "main .msg-sponsored-conversation-thread"
RESPONSE_BUTTON_SELECTOR = "main .msg-s-sponsored-message-actions button"

#: Below this many elements a LinkedIn page has not rendered. The same floor
#: ``dom.read_thread_reply_surface`` uses, for the same reason: on a page that
#: has not arrived every count reads zero, and a zero would be read as a fact.
RENDERED_FLOOR = 50

#: The reply form's footer controls, MEASURED on the composer's form (four:
#: attach an image, attach a file, the GIF keyboard, the emoji keyboard) --
#: reported by a CLOSED vocabulary so a conversation's own footer is measured
#: on the first live read without any label crossing. A video-meeting control
#: was NOT among the four; ``video_meeting`` is listed so its presence would
#: be counted if a conversation draws one (census ``M M20``).
FOOTER_ACTION_SELECTOR = "main form.msg-form button.msg-form__footer-action"
_FOOTER_VOCABULARY: dict[str, str] = {
    "attach an image for your draft conversation": "attach_image",
    "attach a file for your draft conversation": "attach_file",
    "open gif keyboard": "gif_keyboard",
    "open emoji keyboard": "emoji_keyboard",
}
_VIDEO_MEETING_WORDS = ("video meeting", "meeting")

#: Response controls, as a CLOSED vocabulary. A label outside it is reported
#: as ``unrecognised`` -- never returned raw, because a response button's text
#: is written by the sender of a sponsored message.
_RESPONSE_VOCABULARY: dict[str, str] = {
    "not interested": "not_interested",
    "interested": "interested",
    "i want to know more!": "want_to_know_more",
    "yes, interested": "yes_interested",
    "no thanks": "no_thanks",
    "maybe later": "maybe_later",
}

#: The pill names this module reports, from dom's closed set. Imported rather
#: than restated so the two cannot drift.
def _pill_names() -> tuple[str, ...]:
    from linkedin_server import dom

    return tuple(dom.MESSAGING_FILTERS)


_WORD_UNREAD = re.compile(r"\bunread\b", re.IGNORECASE)


def _normalise(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


async def _count(locator: Any) -> int:
    """A Playwright count, through the coercion gate every reader here uses."""
    return coerce.as_count(await locator.count())


# ---------------------------------------------------------------------------
# 3. The receipt-free list
# ---------------------------------------------------------------------------


async def read_conversation_list(page: Any, *, include_names: bool = False) -> dict[str, Any]:
    """The conversation list on the page already open, with unread PAIRED to rows.

    Run on ``/messaging/compose/``, which is measured to open no conversation.
    Every field is a count, a boolean or a closed token, except each row's
    ``name`` when ``include_names`` is passed.

    UNREAD IS THREE-VALUED. ``True`` when any of three signals is present on a
    rendered row -- a class token containing ``unread``, the whole word
    ``unread`` in the row's text or an accessible name, or a notification badge
    inside the row. ``False`` on a rendered row carrying none. ``None`` on a
    placeholder row, whose content is not in the DOM. **The READ form is
    measured** (ten rendered rows, none carrying any signal); **the UNREAD
    form is not in any capture** -- the signals are the union of the markers
    measured 2026-08-26 (a class token and the word) and a badge. A row that
    is unread in some fourth way would read ``False``; capture spec C1 is the
    capture that settles it.
    """
    out: dict[str, Any] = {
        "rows_total": 0,
        "rows_rendered": 0,
        "rows_placeholder": 0,
        "rows": [],
        "message_events": 0,
        "active_rows": 0,
        "editors": 0,
        "pills": [],
        "error": None,
    }
    try:
        rows = page.locator(ROW_SELECTOR)
        total = await _count(rows)
        out["rows_total"] = total
        for index in range(total):
            row = rows.nth(index)
            classes = str(await row.get_attribute("class") or "")
            placeholder = OCCLUDED_CLASS in classes.split()
            record: dict[str, Any] = {
                "position": index + 1,
                "rendered": False,
                "unread": None,
                "signals": [],
                "group": None,
            }
            if placeholder or await _count(row.locator(ROW_LINK_SELECTOR)) != 1:
                out["rows_placeholder"] += 1
                if include_names:
                    record["name"] = None
                out["rows"].append(record)
                continue
            out["rows_rendered"] += 1
            record["rendered"] = True
            signals: list[str] = []
            if "unread" in classes.lower() or await _count(row.locator("[class*='unread']")):
                signals.append("class")
            if await _count(row.get_by_text(_WORD_UNREAD)) or await _count(
                row.locator("[aria-label*='unread' i]")
            ):
                signals.append("word")
            if await _count(
                row.locator("[class*='notification-badge'], [class*='unread-count']")
            ):
                signals.append("badge")
            record["signals"] = signals
            record["unread"] = bool(signals)
            record["group"] = bool(await _count(row.locator(GROUP_FACEPILE_SELECTOR)))
            if include_names:
                names = row.locator(PARTICIPANT_NAMES_SELECTOR)
                record["name"] = (
                    _normalise(await names.first.inner_text())
                    if await _count(names) == 1
                    else None
                )
            out["rows"].append(record)
        # PAGE-WIDE: receipt evidence, not aim (EVIDENCE_EVENT_SELECTOR).
        out["message_events"] = await _count(page.locator(EVIDENCE_EVENT_SELECTOR))
        out["active_rows"] = await _count(page.locator(EVIDENCE_ACTIVE_ROW_SELECTOR))
        out["editors"] = await _count(page.locator(REPLY_EDITOR_SELECTOR))
        out["pills"] = await _read_pills(page)
    except Exception as exc:  # noqa: BLE001 - reported as a type, never raised
        out["error"] = type(exc).__name__
        logger.debug("conversation list unreadable: %s", type(exc).__name__)
    return out


async def _read_pills(page: Any) -> list[dict[str, Any]]:
    """The filter pills, by the hook LinkedIn writes on each -- a closed set."""
    known = set(_pill_names())
    pills = page.locator(PILL_SELECTOR)
    found: list[dict[str, Any]] = []
    for index in range(await _count(pills)):
        pill = pills.nth(index)
        hook = _normalise(await pill.get_attribute(PILL_HOOK)).lower()
        text = _normalise(await pill.inner_text()).lower()
        name = hook if hook in known else (text if text in known else "unrecognised")
        pressed = await pill.get_attribute("aria-pressed")
        found.append(
            {
                "name": name,
                "pressed": None if pressed is None else pressed == "true",
            }
        )
    return found


def list_opened_a_conversation(reading: dict[str, Any], landed: Any) -> dict[str, Any]:
    """Did loading the list open anybody's conversation? The evidence, as counts."""
    events = coerce.as_count(reading.get("message_events"))
    active = coerce.as_count(reading.get("active_rows"))
    on_compose = is_the_compose_address(landed)
    opened = bool(events or active or not on_compose)
    return {
        "opened": opened,
        "message_events_on_the_page": events,
        "rows_marked_active": active,
        "landed_on_the_composer": on_compose,
        "why": (
            "the page drew no conversation's messages and marked no row "
            "active, on the composer's own address -- the measured shape of a "
            "list with nothing open"
            if not opened
            else "the page did not have the shape of a list with nothing open: "
            "it drew a conversation's messages, marked a row active, or was "
            "not the composer's address. Treat a conversation as opened."
        ),
    }


def receipt_guard(
    reading: dict[str, Any], *, allow_unread: bool, landed: Any = None
) -> dict[str, Any]:
    """May a conversation be opened without showing anybody a new "seen"?

    THE RULE, and why it is coarser than the brief asked for. The brief asked
    to refuse opening a thread THE LISTING MARKED UNREAD. A listing row carries
    no thread id (measured), so no listing can say which row a thread id is --
    and the guard cannot refuse "that" row. It refuses on ANY unread rendered
    row instead, because it cannot rule out that the conversation about to be
    opened is it. When no rendered row is unread, an unread conversation would
    have to be older than every rendered row, or in a folder the default view
    does not draw: a new incoming message moves its conversation to the top of
    the list, which is why the rendered rows are the ones that matter. That
    residue is stated in every answer rather than rounded away.

    ``allow_unread`` is the explicit opt-in. It is his to pass.
    """
    rows = list(reading.get("rows") or [])
    rendered = [r for r in rows if r.get("rendered")]
    unread = [r["position"] for r in rendered if r.get("unread") is True]
    residue = (
        "WHAT THIS DOES NOT COVER: the list's placeholder rows (their content "
        "is not drawn -- older conversations), conversations beyond them, and "
        "any folder the default view does not draw (InMail and 'Other' "
        "conversations may not appear in it). An unread conversation in any "
        "of those would not stop this. And the unread markers themselves are "
        "matched as a union of signals because no capture holds an unread row "
        "in LinkedIn's current markup."
    )
    list_page = list_opened_a_conversation(
        reading, landed if landed is not None else COMPOSE_URL
    )
    base = {
        "rows_rendered": len(rendered),
        "rows_placeholder": coerce.as_count(reading.get("rows_placeholder")),
        "unread_positions": unread,
        "allow_unread": bool(allow_unread),
        "list_page": list_page,
        "residue": residue,
    }
    if list_page["opened"]:
        # FIRST, AND allow_unread DOES NOT REACH IT. That opt-in accepts a
        # receipt on an unread ROW; this is a list page that did not have the
        # measured shape at all -- it drew a conversation, marked a row
        # active, or was not the composer's address -- and nothing a caller
        # passes makes an unmeasured page the one this guard was built on.
        return {
            **base,
            "proceed": False,
            "why": (
                "the list page did not have the measured shape of a list with "
                "nothing open, so nothing further is opened: the receipt this "
                "guard exists to prevent may already have been spent by that "
                "page, and a second one is not added to it. "
                + list_page["why"]
            ),
        }
    if reading.get("error"):
        return {
            **base,
            "proceed": bool(allow_unread),
            "why": (
                f"the conversation list could not be read ({reading['error']}), "
                "so nothing is known about what is unread."
                + (
                    " You passed allow_unread, so this proceeds anyway."
                    if allow_unread
                    else " Refused: an unknown is not a read conversation."
                )
            ),
        }
    if allow_unread:
        return {
            **base,
            "proceed": True,
            "why": (
                "you passed allow_unread, so a conversation may be opened even "
                f"though {len(unread)} of {len(rendered)} rendered rows read "
                "unread. If the one you open is unread, its sender may be shown "
                "that you have seen it."
            ),
        }
    if not rendered:
        return {
            **base,
            "proceed": False,
            "why": (
                "no conversation row rendered, so whether anything is unread is "
                "unknown -- and an unknown is not a read conversation. Refused. "
                "Pass allow_unread to accept the receipt."
            ),
        }
    if unread:
        return {
            **base,
            "proceed": False,
            "why": (
                f"{len(unread)} of the {len(rendered)} rendered conversation rows "
                f"read UNREAD (positions {unread}). A row carries no thread id, "
                "so this server cannot tell whether the conversation it would "
                "open is one of them -- opening it could show its sender a "
                "'seen'. Refused. Read that conversation yourself first, or pass "
                "allow_unread to accept the receipt."
            ),
        }
    return {
        **base,
        "proceed": True,
        "why": (
            f"none of the {len(rendered)} rendered conversation rows reads "
            "unread, so opening one of them shows nobody a new 'seen'. "
            + residue
        ),
    }


def list_result(
    reading: dict[str, Any], landed: Any, *, include_names: bool
) -> dict[str, Any]:
    """What ``linkedin_list_conversations`` returns. Built here so the tool
    body is navigation only and every field is testable without a server."""
    rows = []
    for row in reading.get("rows") or []:
        entry = {
            key: row.get(key)
            for key in ("position", "rendered", "unread", "signals", "group")
        }
        if row.get("rendered"):
            entry["name"] = row.get("name") if include_names else shape.NAME_PLACEHOLDER
        rows.append(entry)
    return {
        "conversations_listed": coerce.as_count(reading.get("rows_total")),
        "rows_rendered": coerce.as_count(reading.get("rows_rendered")),
        "rows_placeholder": coerce.as_count(reading.get("rows_placeholder")),
        "unread_rendered": sum(1 for r in rows if r.get("unread") is True),
        "rows": rows,
        "filters": reading.get("pills"),
        "opened_a_conversation": list_opened_a_conversation(reading, landed),
        "names_included": bool(include_names),
        "thread_ids": (
            "NONE, and none can be: a list row carries no thread identifier "
            "on any attribute (measured). To open one conversation, copy its "
            "id from your own browser and pass it to linkedin_open_thread."
        ),
        "error": reading.get("error"),
        "pages_loaded": 1,
    }


def refused_result(guard: dict[str, Any]) -> dict[str, Any]:
    """The guard refused; nothing past the list page was loaded."""
    return {
        "refused": True,
        # From the list page's own evidence, not assumed: the composer is
        # measured to open nothing, and this says whether it did this time.
        "opened_a_conversation": bool((guard.get("list_page") or {}).get("opened")),
        "receipt_guard": guard,
        "pages_loaded": 1,
    }


def off_thread_result(guard: dict[str, Any], landed: Any) -> dict[str, Any]:
    """The named conversation was asked for and the browser went elsewhere."""
    return {
        "refused": True,
        # LinkedIn put the browser SOMEWHERE, and on this surface that is
        # most likely a conversation of its own choosing -- so this says a
        # conversation may have been opened rather than claiming none was.
        "opened_a_conversation": "unknown",
        "landed_on_the_named_thread": False,
        "why": (
            "the browser did not land on the conversation you named, so that "
            "page was NOT read. What is safe to say about where it went -- "
            f"{landing.withheld(landed)}."
        ),
        "receipt_guard": guard,
        "pages_loaded": 2,
    }


def open_thread_result(guard: dict[str, Any], reading: dict[str, Any]) -> dict[str, Any]:
    """The named conversation, read: counts, the read indicator, the reply box."""
    state, why = reply_state(reading)
    return {
        "refused": False,
        "opened_a_conversation": True,
        "landed_on_the_named_thread": True,
        "conversation": thread_facts(reading),
        "read_indicator": seen_state(reading),
        "reply_box": {"state": state, "why": why},
        "receipt_guard": guard,
        "pages_loaded": 2,
    }


# ---------------------------------------------------------------------------
# 4. One open conversation
# ---------------------------------------------------------------------------


async def read_thread(page: Any, *, text: Optional[str] = None) -> dict[str, Any]:
    """What the open conversation draws, as counts, booleans and closed tokens.

    ``text``, when given, is HIS words -- a reply he is sending or has sent.
    It is compared against each message INSIDE THE PAGE by Playwright's text
    engine (exact, whitespace-normalised), and only counts come back. No
    message body is read into this process by this function.
    """
    out: dict[str, Any] = {
        "elements": 0,
        "rendered": False,
        "events": 0,
        "items": 0,
        "items_from_the_other_side": 0,
        "last_event_marked_last": None,
        "last_from": "unknown",
        "events_with_text": None,
        "last_has_text": None,
        "seen_without_marker": 0,
        "seen_with_marker": 0,
        "seen_other_markers": 0,
        "forms": 0,
        "editors": 0,
        "editor_label_matches": None,
        "editor_empty": None,
        "send_controls": 0,
        "send_disabled": None,
        "textboxes": 0,
        "recipient_boxes": 0,
        "file_inputs": 0,
        "file_input_accepts": [],
        "footer_actions": [],
        "titles": 0,
        "sponsored": False,
        "response_controls": [],
        "active_rows": 0,
        "error": None,
    }
    try:
        out["elements"] = await _count(page.locator("*"))
        out["rendered"] = out["elements"] >= RENDERED_FLOOR
        events = page.locator(EVENT_SELECTOR)
        count = await _count(events)
        out["events"] = count
        out["items"] = await _count(page.locator(f"{EVENT_SELECTOR} {ITEM_SELECTOR}"))
        out["items_from_the_other_side"] = await _count(
            page.locator(f"{EVENT_SELECTOR} {OTHER_ITEM_SELECTOR}")
        )
        if count:
            last = events.nth(count - 1)
            classes = str(await last.get_attribute("class") or "")
            out["last_event_marked_last"] = any(
                token.startswith(LAST_MSG_CLASS) for token in classes.split()
            )
            items = await _count(last.locator(ITEM_SELECTOR))
            others = await _count(last.locator(OTHER_ITEM_SELECTOR))
            if items == 1 and others == 1:
                out["last_from"] = "other"
            elif items == 1 and others == 0:
                out["last_from"] = "him"
            if text is not None:
                matcher = page.get_by_text(_normalise(text), exact=True)
                out["events_with_text"] = await _count(events.filter(has=matcher))
                out["last_has_text"] = await _count(last.filter(has=matcher)) == 1
        elif text is not None:
            out["events_with_text"] = 0
            out["last_has_text"] = False
        out["seen_without_marker"] = await _count(page.locator(SEEN_WITHOUT_SELECTOR))
        out["seen_with_marker"] = await _count(page.locator(SEEN_WITH_SELECTOR))
        out["seen_other_markers"] = max(
            0,
            await _count(page.locator(SEEN_ANY_SELECTOR))
            - out["seen_without_marker"]
            - out["seen_with_marker"],
        )
        out["forms"] = await _count(page.locator(REPLY_FORM_SELECTOR))
        editors = page.locator(REPLY_EDITOR_SELECTOR)
        out["editors"] = await _count(editors)
        if out["editors"] == 1:
            out["editor_label_matches"] = (
                await editors.first.get_attribute("aria-label")
            ) == REPLY_EDITOR_LABEL
            # HIS OWN BOX. Only the emptiness crosses, as a boolean; whatever
            # is in it is his draft and it is not kept.
            out["editor_empty"] = _normalise(await editors.first.inner_text()) == ""
        sends = page.locator(REPLY_SEND_SELECTOR)
        out["send_controls"] = await _count(sends)
        if out["send_controls"] == 1:
            out["send_disabled"] = bool(await sends.first.is_disabled())
        out["textboxes"] = await _count(page.locator(TEXTBOX_SELECTOR))
        out["recipient_boxes"] = await _count(page.locator(RECIPIENT_BOX_SELECTOR))
        inputs = page.locator(FILE_INPUT_SELECTOR)
        out["file_inputs"] = await _count(inputs)
        accepts = []
        for index in range(out["file_inputs"]):
            accepts.append(_accept_shape(await inputs.nth(index).get_attribute("accept")))
        out["file_input_accepts"] = accepts
        footer = page.locator(FOOTER_ACTION_SELECTOR)
        actions = []
        for index in range(await _count(footer)):
            control = footer.nth(index)
            label = _normalise(
                await control.get_attribute("aria-label") or await control.inner_text()
            ).lower()
            if label in _FOOTER_VOCABULARY:
                actions.append(_FOOTER_VOCABULARY[label])
            elif any(word in label for word in _VIDEO_MEETING_WORDS):
                actions.append("video_meeting")
            else:
                actions.append("unrecognised")
        out["footer_actions"] = actions
        out["titles"] = await _count(page.locator(TITLE_SELECTOR))
        out["sponsored"] = bool(await _count(page.locator(SPONSORED_SELECTOR)))
        responses = page.locator(RESPONSE_BUTTON_SELECTOR)
        labels = []
        for index in range(await _count(responses)):
            raw = _normalise(await responses.nth(index).inner_text()).lower()
            labels.append(_RESPONSE_VOCABULARY.get(raw, "unrecognised"))
        out["response_controls"] = labels
        out["active_rows"] = await _count(page.locator(ACTIVE_ROW_SELECTOR))
    except Exception as exc:  # noqa: BLE001 - reported as a type, never raised
        out["error"] = type(exc).__name__
        logger.debug("thread unreadable: %s", type(exc).__name__)
    return out


def _accept_shape(value: Any) -> str:
    """An ``accept`` declaration as a CLOSED token; its text never crosses.

    Measured on the composer's form: one input declares ``image/*``, the
    other a list of extensions beginning ``image/*,`` that includes
    ``.pdf``. The first version returned the declaration itself, lowercased
    and cut to an alphabet -- still a page string, and one the page-string
    guard's needle cannot see once it is lowercased. So it is compared here
    and only the token leaves.
    """
    declared = re.sub(r"\s+", "", str(value or "")).lower()
    if not declared:
        return "any_file"
    if declared == "image/*":
        return "images"
    parts = declared.split(",")
    if parts[0] == "image/*" and ".pdf" in parts:
        return "images_and_documents"
    return "unrecognised"


def reply_state(reading: dict[str, Any]) -> tuple[str, str]:
    """Is this conversation's reply box EMPTY and ready? ``(state, why)``.

    ``reply_box_empty`` is the one state a reply acts from. Everything else is
    ``unknown`` with the measured reason, and every reason is built from
    counts: a refusal here reaches a transcript.
    """
    if reading.get("error"):
        return "unknown", f"the conversation could not be read ({reading['error']})."
    if not reading.get("rendered"):
        return "unknown", (
            f"{coerce.as_count(reading.get('elements'))} elements -- under the "
            f"{RENDERED_FLOOR} floor, so the page had not arrived and every count "
            "on it is uninterpretable rather than zero."
        )
    if reading.get("sponsored") and not coerce.as_count(reading.get("forms")):
        return "unknown", (
            "this is a SPONSORED conversation: it draws response buttons "
            f"({len(reading.get('response_controls') or [])}) and no reply box, "
            "which is the measured shape of the one such conversation captured. "
            "There is nothing to type into."
        )
    if coerce.as_count(reading.get("recipient_boxes")):
        return "unknown", (
            f"{coerce.as_count(reading.get('recipient_boxes'))} recipient "
            "box(es) are drawn. A conversation has nobody to choose, so this "
            "is not a conversation's reply surface."
        )
    editors = coerce.as_count(reading.get("editors"))
    if editors != 1:
        return "unknown", (
            f"{editors} reply editor(s) matched, where exactly one is the shape "
            "measured on the composer's form. At any other number a fill would "
            "be aiming by document order."
        )
    sends = coerce.as_count(reading.get("send_controls"))
    if sends != 1:
        return "unknown", (
            f"{sends} Send control(s) in the reply form, where exactly one is "
            "the measured shape."
        )
    if reading.get("send_disabled") is not True or reading.get("editor_empty") is not True:
        return "unknown", (
            "the reply box is NOT EMPTY -- Send is already enabled, or the box "
            "holds text. Something is in it, most likely a draft LinkedIn "
            "restored, and a fill REPLACES: this will not type over words it "
            "cannot read back. Clear it yourself."
        )
    return "reply_box_empty", (
        "exactly one reply editor, empty, and exactly one Send control drawn "
        "DISABLED -- which is what an empty reply box looks like on the "
        "measured form. No recipient box is drawn: a conversation fixes who "
        "receives the words."
    )


def seen_state(reading: dict[str, Any]) -> dict[str, Any]:
    """The sender-side read indicator on HIS last message (census ``M M49``).

    Three answers and each says how it knows. ``not_drawn`` rests on the
    MEASURED ``--without-seen-receipt`` modifier. ``drawn`` rests on its BEM
    counterpart, DERIVED and never captured. ``not_applicable`` when the last
    message is the other side's: a seen receipt marks HIS words.
    """
    last_from = reading.get("last_from")
    without = coerce.as_count(reading.get("seen_without_marker"))
    with_ = coerce.as_count(reading.get("seen_with_marker"))
    other = coerce.as_count(reading.get("seen_other_markers"))
    out: dict[str, Any] = {
        "last_from": last_from,
        "last_from_evidence": (
            "measured modifier --other"
            if last_from == "other"
            else "derived: no --other modifier on the last message"
            if last_from == "him"
            else None
        ),
        "without_marker": without,
        "with_marker": with_,
        "other_seen_receipt_markers": other,
    }
    if last_from == "other":
        out.update(
            state="not_applicable",
            evidence=None,
            why="the last message is the other side's; a seen receipt marks yours.",
        )
    elif last_from != "him":
        out.update(
            state="unknown",
            evidence=None,
            why="the last message's author could not be told from this page.",
        )
    elif with_ and not without:
        out.update(
            state="drawn",
            evidence="derived",
            why=(
                "the container after your last message wears the "
                "--with-seen-receipt modifier: the counterpart of the measured "
                "--without form, NEVER CAPTURED. Treat as likely, not certain."
            ),
        )
    elif without and not with_:
        out.update(
            state="not_drawn",
            evidence="measured",
            why=(
                "the container after your last message wears the measured "
                "--without-seen-receipt modifier: no seen receipt is drawn."
            ),
        )
    else:
        out.update(
            state="unknown",
            evidence=None,
            why=(
                f"neither marker alone: without={without}, with={with_}. "
                f"{other} other element(s) carry 'seen-receipt' in a class -- "
                "that count is the measurement a capture of a seen message "
                "would settle."
            ),
        )
    return out


def thread_facts(reading: dict[str, Any]) -> dict[str, Any]:
    """The reading as the preview prints it: counts, booleans, closed tokens."""
    keep = (
        "elements", "events", "items", "items_from_the_other_side",
        "last_from", "events_with_text", "forms", "editors",
        "editor_label_matches", "editor_empty", "send_controls",
        "send_disabled", "textboxes", "recipient_boxes", "file_inputs",
        "file_input_accepts", "footer_actions", "titles", "sponsored",
        "response_controls", "error",
    )
    return {key: reading.get(key) for key in keep}


# ---------------------------------------------------------------------------
# 5. The gate between the fill and the Send click
# ---------------------------------------------------------------------------


async def reply_send_gate(page: Any, *, text: str) -> dict[str, Any]:
    """May Send be pressed? Read AFTER his words are in the box.

    The transition ``publish_post`` and ``send_message`` gate on: Send is
    measured DISABLED on an empty form, so a fill that landed is something
    this server can SEE -- Send enabled, the box no longer empty. Every
    condition is re-read here, on the page, after the fill.

    AND THE WORDS MUST BE HIS, EXACTLY. ``text`` is the grant's own words
    and it is REQUIRED: a caller that forgets it gets a TypeError, never a
    gate that quietly skipped the check. A box can turn Send on while
    holding something else -- an autocorrect, an emoji substitution, a
    mention picked up as he typed -- and a message cannot be taken back,
    so words he did not confirm are not sent. The comparison is the one
    :func:`composer_holds` makes, whitespace-normalised; only a boolean
    and two lengths are kept.
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": REPLY_SEND_SELECTOR,
        "observed": {},
        "why": "",
        "refused_condition": None,
    }
    try:
        editors = page.locator(REPLY_EDITOR_SELECTOR)
        sends = page.locator(REPLY_SEND_SELECTOR)
        observed = {
            "editors": await _count(editors),
            "send_controls": await _count(sends),
            "recipient_boxes": await _count(page.locator(RECIPIENT_BOX_SELECTOR)),
            "send_enabled": None,
            "editor_empty": None,
            "words_exact": None,
            "held_characters": None,
            "grant_characters": len(_normalise(text)),
        }
        if observed["send_controls"] == 1:
            observed["send_enabled"] = bool(await sends.first.is_enabled())
        if observed["editors"] == 1:
            # HIS OWN WORDS, compared here and dropped: a boolean and a
            # length leave, the text does not.
            held = _normalise(await editors.first.inner_text())
            observed["editor_empty"] = held == ""
            observed["words_exact"] = held == _normalise(text)
            observed["held_characters"] = len(held)
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the reply form could not be read after the fill "
            f"({type(exc).__name__}), so nothing is known about whether it is "
            "ready. Send was not pressed."
        )
        return out
    out["observed"] = observed
    if observed["recipient_boxes"]:
        out["refused_condition"] = "1_not_a_conversation"
        out["why"] = (
            f"{observed['recipient_boxes']} recipient box(es) are drawn after "
            "the fill. A conversation has nobody to choose. Send was not pressed."
        )
        return out
    if observed["editors"] != 1:
        out["refused_condition"] = "2_editor_count"
        out["why"] = (
            f"{observed['editors']} reply editor(s) after the fill, where "
            "exactly one is the shape. Send was not pressed."
        )
        return out
    if observed["send_controls"] != 1:
        out["refused_condition"] = "3_send_count"
        out["why"] = (
            f"{observed['send_controls']} Send control(s) in the reply form, "
            "where exactly one is required. Send was not pressed."
        )
        return out
    if observed["send_enabled"] is not True or observed["editor_empty"] is not False:
        out["refused_condition"] = "4_fill_not_landed"
        out["why"] = (
            "Send is not enabled, or the box reads empty, after the fill. On "
            "this form Send is measured disabled while empty, so the words did "
            "not land -- and a disabled control is not pressed to find out."
        )
        return out
    if observed["words_exact"] is not True:
        out["refused_condition"] = "5_words_not_exact"
        out["why"] = (
            "Send turned on, but the reply box does not hold exactly the "
            f"words the grant carries ({observed['held_characters']} "
            f"characters in the box, {observed['grant_characters']} "
            "confirmed): they were changed as they were typed, or something "
            "else is in the box. A message cannot be taken back, so words "
            "you did not confirm are not sent. Send was not pressed."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "the reply box holds exactly the words you confirmed and Send went "
        "from the disabled state an empty form draws to enabled -- the "
        "observable transition a fill produces. No recipient box is drawn."
    )
    return out


# ---------------------------------------------------------------------------
# 6. SENT, read back
# ---------------------------------------------------------------------------

#: The states a reply's verification can return. ``REPLY_SENT`` is the
#: spec's ``to_state``; ``REPLY_HELD`` its ``not_performed_state``.
REPLY_SENT = "reply_sent"
REPLY_HELD = "reply_box_holds_text"
UNKNOWN = "unknown"


async def composer_holds(page: Any, text: str) -> Optional[bool]:
    """In place, BEFORE any reload: does the reply box still hold his words?

    ``True`` when exactly one editor holds exactly ``text`` and Send is still
    enabled -- the shape of words that were never dispatched. ``False`` when
    the box is empty. ``None`` when it cannot be told. Only a boolean leaves;
    the box is his.
    """
    try:
        editors = page.locator(REPLY_EDITOR_SELECTOR)
        if await _count(editors) != 1:
            return None
        held = _normalise(await editors.first.inner_text())
        sends = page.locator(REPLY_SEND_SELECTOR)
        enabled = (
            bool(await sends.first.is_enabled()) if await _count(sends) == 1 else None
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("reply box unreadable: %s", type(exc).__name__)
        return None
    if held == "":
        return False
    if held == _normalise(text) and enabled is True:
        return True
    return None


def reply_verdict(
    before: dict[str, Any], after: dict[str, Any], *, held_in_place: Optional[bool]
) -> tuple[str, str]:
    """Did the reply land? Read off a FRESH LOAD of the conversation he named.

    ``reply_sent`` needs ALL THREE, and each refuses something the others let
    through:

    1. the LAST message is his (no ``--other`` modifier -- DERIVED, see the
       selector note) ;
    2. that last message's text is EXACTLY the text sent (compared in the page,
       whitespace-normalised);
    3. the number of messages carrying that exact text rose by EXACTLY ONE
       against the preview's reading of the same conversation -- so an
       identical earlier message cannot stand in for this one, and two sends
       cannot be read as one.

    ``reply_box_holds_text`` is the NOT-SENT answer: the box still held his
    words with Send enabled before the reload, and the reload shows no new
    message carrying them. Anything else is ``unknown``, with the counts.
    """
    if after.get("error") or not after.get("rendered"):
        return UNKNOWN, (
            "the conversation did not render on the re-read "
            f"(elements {coerce.as_count(after.get('elements'))}, error "
            f"{after.get('error')!r}), so it says nothing about whether the "
            "reply landed. Open the conversation and look before retrying."
        )
    was = before.get("events_with_text")
    now = after.get("events_with_text")
    if not isinstance(was, int) or not isinstance(now, int):
        return UNKNOWN, (
            "a before- or after-count of messages carrying your exact words is "
            "missing, so no delta can be computed. Open the conversation and "
            "look before retrying."
        )
    if (
        after.get("last_from") == "him"
        and after.get("last_has_text") is True
        and now == was + 1
    ):
        return REPLY_SENT, (
            "a FRESH LOAD of the conversation you named shows your words as its "
            "last message, and the number of messages carrying exactly those "
            f"words went from {was} to {now}. The last message carries no "
            "'--other' modifier, which is how this page marks the other side's "
            "messages (measured) -- that it marks yours by its absence is "
            "derived, and this is the first reading that can confirm it."
        )
    if now == was and held_in_place is True:
        return REPLY_HELD, (
            "the reply box still held your words with Send enabled, and a fresh "
            "load shows no new message carrying them "
            f"({was} before, {now} after). NOTHING WAS DISPATCHED."
        )
    return UNKNOWN, (
        f"messages carrying your exact words: {was} before, {now} after; last "
        f"message from: {after.get('last_from')}; last carries your words: "
        f"{after.get('last_has_text')}; box held them in place: "
        f"{held_in_place}. That combination proves neither outcome -- LinkedIn "
        "may have rendered the text differently (a link, an emoji as an "
        "image). Open the conversation and look. Do NOT retry: a retry on a "
        "reply that landed sends it twice."
    )


def sent_in_place(reading: dict[str, Any]) -> tuple[str, str]:
    """For a send from the COMPOSER: read the conversation the send left open.

    WEAKER THAN :func:`reply_verdict`, and it says so. After a compose send
    LinkedIn shows the conversation on the same page; this reads it IN PLACE,
    because that conversation's id is on the page and a page-derived id is
    never navigated to. There is no before-count -- the composer drew no
    conversation -- so an identical earlier last message of his cannot be
    told from this one.
    """
    if reading.get("error") or not reading.get("rendered") or not reading.get("events"):
        return UNKNOWN, "no conversation is drawn on the page the send left open."
    if reading.get("last_from") == "him" and reading.get("last_has_text") is True:
        return "message_sent", (
            "the conversation now drawn on the page the send left open shows "
            "your exact words as its last message, and that message carries no "
            "'--other' modifier. Read IN PLACE and with no before-count, so an "
            "identical earlier last message of yours in the same conversation "
            "would read the same -- that is this reading's limit."
        )
    return UNKNOWN, (
        f"a conversation is drawn but its last message is from "
        f"{reading.get('last_from')!r} and carries your words: "
        f"{reading.get('last_has_text')!r}. Open your messages and look."
    )


# ---------------------------------------------------------------------------
# 7. Who a reply would reach -- in the confirm block and nowhere else
# ---------------------------------------------------------------------------


async def name_the_reply_recipient(
    page: Any, spec: Any, observation: Any, block: dict[str, Any]
) -> dict[str, Any]:
    """Print the conversation's title in the confirm block, and only there.

    THE SAME ARGUMENT THE INVITATION RULING MADE (2026-08-31), applied to a
    conversation he named by id. A gate firing an irreversible act to a person
    while unable to say WHO is a confirm prompt with the important word
    missing. The title is read off HIS OWN conversation page, already open
    from the preview's load, and nobody is notified by reading it. It is
    added to a NEW dict: not to ``grant.preview`` (assigned before this runs),
    not to the grant's target, not to the observation, and not to a log.

    IT IS READ ONLY OFF THE CONVERSATION THE OBSERVATION READ, and that is
    checked on the PAGE rather than on its url -- the invitation ruling's own
    choice, for its own reason: a page can be re-rendered at the same address,
    and what matters is that the title is read off the conversation whose
    reply box was just measured. So the observation must have landed on the
    named thread, and a re-read here must find the same number of messages
    it recorded and exactly one title. No second page load.
    """
    if getattr(spec, "action", None) != "send_reply":
        return block
    facts = dict(getattr(observation, "facts", None) or {})
    if facts.get("landed_on_the_named_thread") is not True:
        return block
    try:
        same_conversation = await _count(page.locator(EVENT_SELECTOR)) == coerce.as_count(
            facts.get("events")
        )
        titles = page.locator(TITLE_SELECTOR)
        if not same_conversation or await _count(titles) != 1:
            title = None
        else:
            title = _normalise(await titles.first.inner_text()) or None
    except Exception as exc:  # noqa: BLE001
        logger.debug("title unreadable: %s", type(exc).__name__)
        title = None
    out = dict(block)
    out["who_this_would_reach"] = (
        "The conversation you named is titled "
        f"{title!r}. Read off that conversation's own header, already open on "
        "your screen; nobody is notified, and this server keeps no copy -- it "
        "is in no grant, no log and no file. CHECK IT: a thread id that "
        "uniquely names the WRONG conversation is the one failure this gate "
        "cannot catch for you."
        if title
        else "The conversation's header did not draw exactly one title, so "
        "this server cannot tell you who it would reach. Open the "
        "conversation yourself and check it before confirming."
    )
    return out
