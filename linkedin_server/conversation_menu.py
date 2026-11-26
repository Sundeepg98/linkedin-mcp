"""One conversation's own options menu: read by a sanctioned preview press, acted on through it.

Census rows ``M M26`` (delete a conversation), ``M M27`` (archive one), ``M M29``
(mute or unmute one) and ``M M31`` (mark one unread), built by lane build-msg2
on 2026-11-26 under ruling ``CONVERSATION-MENU-PREVIEW-PRESS`` (the
orchestrator, 14:10, registered at integration 4):

    "a sanctioned PREVIEW press (the similar-jobs trial-press precedent): open
    that one options menu bound to the named conversation, read the item's
    word, press nothing inside, close on Escape, verify closed; the confirmed
    press re-reads and refuses on the inverse. DELETE CONVERSATION (no
    inverse): RECEIPT-ONLY behind the grant (the J 163 class), only on his
    explicit order for a named conversation."

The selectors, the readings and the verdicts live here; ``writes`` holds the
specs and delegates to these functions, as it does to ``group_leave`` and
``job_alert_switch``.

## WHAT IS MEASURED, AND WHERE

Live session 11, load 40 (the conversation he named, by its recorded id,
opened behind the receipt guard at 0 unread rows): the tracked skeleton of the
thread page with the menu CLOSED, ``tests/fixtures/live11/msg_thread.html``,
and the same page with the ACTIVE row's menu OPEN,
``tests/fixtures/live11/c_b3_1_menu_open.html``. Counted on both by this lane
(a probe that prints counts and closed-vocabulary matches only):

* 20 list rows, ONE wearing the active marker
  (``msg-conversations-container__convo-item-link--active``), holding ONE
  options trigger (``button.msg-thread-actions__control``, ``aria-expanded``);
  11 triggers on the page, 10 in rows and the conversation header's own;
* CLOSED: the active row's menu content
  (``.msg-thread-actions__dropdown-options--inbox-shortcuts``) present,
  ``aria-hidden="true"`` and EMPTY -- 0 items in the document;
* OPEN: that trigger ``aria-expanded="true"``, its content
  ``aria-hidden="false"``, EIGHT items (``.msg-thread-actions__dropdown-option``),
  seven ``role=button`` and one ``role=link``. By exact accessible name, inside
  the active row: ``Move to Other``, ``Mark as unread``, ``Star``, ``Mute``,
  ``Archive``, ``Delete conversation`` (buttons), ``Manage settings`` (the
  link) -- and one button whose word the skeleton reduced, never matched.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* THE INVERSE WORDS. ``Unmute`` and ``Mark as read`` are DERIVED: no capture
  holds a muted or an unread conversation's menu. A menu drawing neither word
  of a pair reads ``unknown``, never a state.
* WHAT ARCHIVE LEAVES. The inverse lives in the Archived folder, whose rows'
  menus have never been opened (census ``M M28``). The verification reads a
  FRESH render of the conversation's own address: its menu still drawing
  ``Archive`` is a strong NOT-archived; the row no longer drawn in the list,
  on a list that drew rows, is the DERIVED positive and says so.
* WHAT DELETE DRAWS. A confirmation or the deletion itself -- not on disk. The
  act is RECEIPT-ONLY: the item is pressed, what the page drew is counted
  (:func:`read_after_press`), and NOTHING further is pressed -- a confirmation
  is reported and never answered. Its first fire, at his order, is that
  measurement.
* WHETHER OPENING A CONVERSATION MARKS IT READ. Believed (LinkedIn marks a
  conversation read when it is opened) and never measured here. It is why no
  "mark as read" act is built on this page: the preview's own load of the
  conversation would be the act. The read half of ``M M31`` is
  ``linkedin_open_thread`` with ``allow_unread=True`` -- his opt-in -- and it
  is why ``mark_conversation_unread`` verifies IN PLACE, without a fresh load.

## THE PREVIEW PRESS, AND THE TWO MUTATIONS IT IS ALLOWED

:func:`preview_press` is the sanctioned preview press. It refuses before any
press unless the page draws EXACTLY ONE active row holding EXACTLY ONE
collapsed trigger and no visible item; then it presses that trigger
(:func:`_open`, one ``click``), waits -- bounded, deciding nothing -- for the
items, counts them by exact word INSIDE THE PAGE, presses Escape
(:func:`_close`, one ``press``) and verifies the menu closed. Nothing inside
the menu is ever pressed by it. Those two calls are the module's only
mutating call sites, each declared in ``readonly.SANCTIONED_MUTATIONS``; the
confirmed press -- the trigger, then the item -- goes through
``writes.perform``'s one click site, like every write.

## WHAT NEVER LEAVES THIS MODULE

Counts, booleans and words from the closed vocabulary below. No item's text
is read into Python -- every word is compared inside the page by Playwright's
role engine -- and no message, name or thread id is read at all.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from linkedin_server import coerce, threads

#: THE RULING THIS MODULE IS BUILT UNDER, by its register id.
RULING = "CONVERSATION-MENU-PREVIEW-PRESS"

#: The ``state_from`` every spec acting through this menu declares.
STATE_FROM = "conversation_menu"

#: The list row, the active marker, and the row that wears it. MEASURED: one
#: active row on the thread page, none on the composer's list.
ROW = threads.ROW_SELECTOR
ACTIVE_LINK = ".msg-conversations-container__convo-item-link--active"
ACTIVE_ROW = f"{ROW}:has({ACTIVE_LINK})"
#: A RENDERED row: not a virtualised placeholder, and drawing its own link.
RENDERED_ROW = f"{ROW}:not(.{threads.OCCLUDED_CLASS}):has({threads.ROW_LINK_SELECTOR})"

#: The options trigger, and the one in the active row -- the press target of
#: the preview press and of a write's first click.
TRIGGER = "button.msg-thread-actions__control[aria-expanded]"
ACTIVE_TRIGGER = f"{ACTIVE_ROW} {TRIGGER}"

#: The menu's content node and its items, inside the active row.
CONTENT = ".msg-thread-actions__dropdown-options--inbox-shortcuts"
ACTIVE_CONTENT = f"{ACTIVE_ROW} {CONTENT}"
ITEM = ".msg-thread-actions__dropdown-option"
#: Every item drawn in the active row's content, visible or not -- a fact.
ACTIVE_ITEMS = f"{ACTIVE_CONTENT} {ITEM}"

#: THE CLOSED VOCABULARY. Measured as buttons on the open menu (session 11):
MEASURED_WORDS: tuple[str, ...] = (
    "Move to Other",
    "Mark as unread",
    "Star",
    "Mute",
    "Archive",
    "Delete conversation",
)
#: The one link item measured. A link is a navigation and is never pressed.
LINK_WORDS: tuple[str, ...] = ("Manage settings",)
#: DERIVED: the words a menu would draw in the other state of each pair. No
#: capture holds them; each is counted when drawn and decides nothing alone.
DERIVED_WORDS: tuple[str, ...] = ("Unmute", "Mark as read", "Unstar", "Move to Focused")

#: The states. MEASURED: ``not_muted``, ``read``, ``in_inbox``,
#: ``delete_offered`` (each read off the captured menu's word). DERIVED:
#: ``muted``, ``unread``, ``archived``.
NOT_MUTED: str = "not_muted"
MUTED: str = "muted"
READ: str = "read"
UNREAD: str = "unread"
IN_INBOX: str = "in_inbox"
ARCHIVED: str = "archived"
DELETE_OFFERED: str = "delete_offered"
DELETE_PRESSED: str = "delete_pressed"
UNKNOWN: str = "unknown"
#: THE CLICK-TIME STATE: the trigger, collapsed, in the one active row. The
#: word is not readable until the menu is open, so the confirmed press opens
#: it and re-reads the word there (:func:`menu_item_gate`).
MENU_CLOSED: str = "menu_closed"
#: THE ONE "IT DID NOT HAPPEN" ANSWER: this call changed nothing -- the item
#: was not pressed, or was pressed and the menu still reads the word it acted
#: from. Distinct from the states above, so a conversation that was ALREADY
#: muted is never reported as muted BY THIS CALL.
NOT_CHANGED: str = "not_changed_by_this_call"

MUTE: str = "set_conversation_muted"
UNMUTE: str = "unset_conversation_muted"
MARK_UNREAD: str = "mark_conversation_unread"
ARCHIVE: str = "set_conversation_archived"
DELETE: str = "set_conversation_deleted"


@dataclass(frozen=True)
class MenuAct:
    """One act through the menu: the item's word, and what it reads before and after."""

    action: str
    word: str
    #: The word a menu draws once the act's destination already holds -- the
    #: word the confirmed press REFUSES on. Empty where it is not measured or
    #: derivable (archive, delete): the act then refuses on anything but its
    #: own word drawn exactly once, which subsumes it.
    inverse: str
    from_state: str
    to_state: str
    #: The words that, between them, say this act's state: exactly one drawn,
    #: exactly once, names the state; anything else is unknown.
    family: tuple[tuple[str, str], ...]
    #: Whether the verification may load the conversation again. ``False`` for
    #: the read mark: a load is believed to mark it read (DERIVED), which would
    #: undo the act it is verifying, so that act is read back IN PLACE.
    fresh_load: bool


ACTS: dict[str, MenuAct] = {
    MUTE: MenuAct(
        MUTE, "Mute", "Unmute", NOT_MUTED, MUTED,
        (("Mute", NOT_MUTED), ("Unmute", MUTED)), True,
    ),
    UNMUTE: MenuAct(
        UNMUTE, "Unmute", "Mute", MUTED, NOT_MUTED,
        (("Mute", NOT_MUTED), ("Unmute", MUTED)), True,
    ),
    MARK_UNREAD: MenuAct(
        MARK_UNREAD, "Mark as unread", "Mark as read", READ, UNREAD,
        (("Mark as unread", READ), ("Mark as read", UNREAD)), False,
    ),
    ARCHIVE: MenuAct(
        ARCHIVE, "Archive", "", IN_INBOX, ARCHIVED,
        (("Archive", IN_INBOX),), True,
    ),
    DELETE: MenuAct(
        DELETE, "Delete conversation", "", DELETE_OFFERED, DELETE_PRESSED,
        (("Delete conversation", DELETE_OFFERED),), False,
    ),
}

#: Every action this module serves, in a fixed order.
ACTIONS: tuple[str, ...] = (MUTE, UNMUTE, MARK_UNREAD, ARCHIVE, DELETE)

#: Bounds. A LIVENESS BOUND decides nothing: the reading at its end decides.
MENU_POLLS: int = 15
MENU_POLL_MS: int = 200
CLICK_TIMEOUT_MS: int = 5_000

#: What a press of an item may draw: dialogs, by role, and the closed words a
#: confirmation's buttons are counted against. NOTHING in a dialog is pressed.
DIALOGS: str = "role=dialog"
ALERTDIALOGS: str = "role=alertdialog"
DIALOG_WORDS: tuple[str, ...] = ("Delete", "Cancel", "Archive", "Dismiss", "Close")


def act_for(action: Any) -> MenuAct:
    """The act for one of this module's actions. Raises ``KeyError`` otherwise."""
    return ACTS[str(action)]


def item_selector(word: str) -> str:
    """The pressable item named EXACTLY ``word``, inside the active row's menu.

    Through the role engine, which skips an ``aria-hidden`` subtree, then
    required visible: a closed menu's content is never pressable. ``word`` is
    one of this module's own constants -- never page text, never a caller's.
    """
    if word not in MEASURED_WORDS + DERIVED_WORDS:
        raise ValueError("refusing to build an item selector for a word outside the vocabulary")
    return f'{ACTIVE_CONTENT} >> role=button[name="{word}"s] >> visible=true'


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def _expanded(page: Any) -> Optional[str]:
    """The active trigger's ``aria-expanded`` as a CLOSED token -- ``"true"``,
    ``"false"`` or ``"other"`` -- when exactly one is drawn; else ``None``.

    The page's own attribute value never leaves: it is compared with the two
    words this module knows and one of this module's constants is returned.
    """
    triggers = page.locator(ACTIVE_TRIGGER)
    if coerce.as_count(await triggers.count()) != 1:
        return None
    value = await triggers.first.get_attribute("aria-expanded")
    if value is None:
        return None
    if value == "true":
        return "true"
    if value == "false":
        return "false"
    return "other"


async def _visible_items(page: Any) -> int:
    """Items the active row's menu draws as pressable or followable controls."""
    content = page.locator(ACTIVE_CONTENT)
    buttons = coerce.as_count(await content.get_by_role("button").count())
    links = coerce.as_count(await content.get_by_role("link").count())
    return buttons + links


async def read_structure(page: Any) -> dict[str, Any]:
    """COUNTS ONLY, off the conversation page already open. Never raises."""
    out: dict[str, Any] = {
        "rows": 0,
        "rows_rendered": 0,
        "active_rows": 0,
        "triggers_in_the_active_row": 0,
        "triggers_on_the_page": 0,
        "expanded": None,
        "items_in_the_dom": 0,
        "items_visible": 0,
        "error": None,
    }
    try:
        out["rows"] = await _count(page, ROW)
        out["rows_rendered"] = await _count(page, RENDERED_ROW)
        out["active_rows"] = await _count(page, ACTIVE_ROW)
        out["triggers_in_the_active_row"] = await _count(page, ACTIVE_TRIGGER)
        out["triggers_on_the_page"] = await _count(page, TRIGGER)
        out["expanded"] = await _expanded(page)
        out["items_in_the_dom"] = await _count(page, ACTIVE_ITEMS)
        if out["active_rows"] == 1:
            out["items_visible"] = await _visible_items(page)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _ready_to_open(structure: dict[str, Any]) -> tuple[bool, str]:
    """Is the page the measured shape for a press? Never presses."""
    if structure.get("error"):
        return False, (
            f"the conversation page could not be read ({structure['error']}); "
            "nothing was pressed."
        )
    active = coerce.as_count(structure.get("active_rows"))
    if active != 1:
        return False, (
            f"the page draws {active} list row(s) wearing the active marker, where "
            "exactly one binds the menu to the conversation you named; nothing "
            "was pressed. A conversation older than the rows the list renders is "
            "not drawn as a row at all."
        )
    triggers = coerce.as_count(structure.get("triggers_in_the_active_row"))
    if triggers != 1:
        return False, (
            f"the active row holds {triggers} options trigger(s), where exactly one "
            "is the measured shape; nothing was pressed."
        )
    if structure.get("expanded") != "false":
        return False, (
            "the active row's options trigger does not read collapsed "
            f"(aria-expanded {structure.get('expanded')!r}), so the menu is not in "
            "the state this press starts from; nothing was pressed."
        )
    if coerce.as_count(structure.get("items_visible")):
        return False, (
            "the active row's menu already draws items while its trigger reads "
            "collapsed -- not the measured shape; nothing was pressed."
        )
    return True, ""


async def _read_words(page: Any) -> dict[str, Any]:
    """The open menu's items by EXACT word, counted inside the page. Never raises.

    ``words`` holds a count for every word of the closed vocabulary; ``links``
    for each link word; ``other_items`` is the visible items no word of the
    vocabulary names -- counted, never read.
    """
    out: dict[str, Any] = {"words": {}, "links": {}, "items_visible": 0, "other_items": 0, "error": None}
    try:
        content = page.locator(ACTIVE_CONTENT)
        named = 0
        for word in MEASURED_WORDS + DERIVED_WORDS:
            count = coerce.as_count(
                await content.get_by_role("button", name=word, exact=True).count()
            )
            out["words"][word] = count
            named += count
        for word in LINK_WORDS:
            count = coerce.as_count(
                await content.get_by_role("link", name=word, exact=True).count()
            )
            out["links"][word] = count
            named += count
        out["items_visible"] = await _visible_items(page)
        out["other_items"] = max(0, out["items_visible"] - named)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


async def _open(page: Any) -> None:
    """THE PREVIEW PRESS'S ONE CLICK: the active row's trigger, strictly.

    Declared in ``readonly.SANCTIONED_MUTATIONS``. Reached only from
    :func:`preview_press`, after :func:`_ready_to_open` passed on the page.
    """
    await page.click(ACTIVE_TRIGGER, timeout=CLICK_TIMEOUT_MS, strict=True)


async def _close(page: Any) -> None:
    """THE PREVIEW PRESS'S ONE ESCAPE, which closes the menu it opened.

    Declared in ``readonly.SANCTIONED_MUTATIONS``. Reached only from
    :func:`preview_press`, and only while the menu reads open.
    """
    await page.keyboard.press("Escape")


async def _wait_for_items(page: Any) -> int:
    """Polls, bounded, until the open menu draws an item. Decides nothing."""
    polls = 0
    for polls in range(1, MENU_POLLS + 1):
        if await _visible_items(page):
            break
        await page.wait_for_timeout(MENU_POLL_MS)
    return polls


async def _wait_for_closed(page: Any) -> int:
    """Polls, bounded, until the menu reads closed. Decides nothing."""
    polls = 0
    for polls in range(1, MENU_POLLS + 1):
        if await _expanded(page) == "false" and not await _visible_items(page):
            break
        await page.wait_for_timeout(MENU_POLL_MS)
    return polls


async def preview_press(page: Any) -> dict[str, Any]:
    """THE SANCTIONED PREVIEW PRESS: open the one menu, read its words, close it.

    ``CONVERSATION-MENU-PREVIEW-PRESS``. Refuses before any press unless the
    page is the measured shape (:func:`_ready_to_open`). Then: the trigger
    pressed; a bounded wait for the items; the words counted; Escape pressed;
    a bounded wait for the menu to close, and the closure read. NOTHING INSIDE
    THE MENU IS PRESSED. Never raises; an error is an exception TYPE.

        pressed   whether the trigger was pressed
        opened    whether the menu drew at least one item after the press
        words     a count per vocabulary word (see :func:`_read_words`)
        closed    True only when, after Escape, the trigger reads collapsed and
                  the menu draws no item. A menu left open is the loudest
                  answer this returns: every verdict on it is ``unknown``.
    """
    out: dict[str, Any] = {
        "structure": {},
        "ready": False,
        "why_not_pressed": "",
        "pressed": False,
        "opened": False,
        "open_polls": 0,
        "expanded_when_open": None,
        "words": {},
        "links": {},
        "items_visible": 0,
        "other_items": 0,
        "escape_pressed": False,
        "close_polls": 0,
        "closed": None,
        "error": None,
    }
    structure = await read_structure(page)
    out["structure"] = structure
    ready, why = _ready_to_open(structure)
    out["ready"] = ready
    if not ready:
        out["why_not_pressed"] = why
        return out
    try:
        await _open(page)
        out["pressed"] = True
        out["open_polls"] = await _wait_for_items(page)
        out["expanded_when_open"] = await _expanded(page)
        words = await _read_words(page)
        out["words"] = words["words"]
        out["links"] = words["links"]
        out["items_visible"] = words["items_visible"]
        out["other_items"] = words["other_items"]
        out["opened"] = coerce.as_count(words["items_visible"]) > 0
        if words.get("error"):
            out["error"] = words["error"]
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    finally:
        if out["pressed"]:
            try:
                if await _expanded(page) != "false" or await _visible_items(page):
                    await _close(page)
                    out["escape_pressed"] = True
                out["close_polls"] = await _wait_for_closed(page)
                out["closed"] = (
                    await _expanded(page) == "false" and not await _visible_items(page)
                )
            except Exception as exc:  # noqa: BLE001 - reported, the menu is not known closed
                out["closed"] = False
                out["error"] = out["error"] or type(exc).__name__
    return out


def _family_state(act: MenuAct, words: dict[str, Any]) -> tuple[str, str]:
    """The state the menu's words name for ``act``, or ``unknown``. PURE."""
    drawn = {word: coerce.as_count(words.get(word)) for word, _state in act.family}
    named = [(word, state) for word, state in act.family if drawn[word] == 1]
    extra = [word for word, count in drawn.items() if count > 1]
    if extra or len(named) != 1 or sum(drawn.values()) != 1:
        counts = ", ".join(f"{word!r} {count}" for word, count in drawn.items())
        return UNKNOWN, (
            f"the menu drew {counts}, where exactly one of these words, exactly "
            "once, says the state; anything else is not a reading."
        )
    word, state = named[0]
    return state, f"the menu draws {word!r} exactly once."


def menu_verdict(reading: dict[str, Any], action: Any) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for one act, off ONE preview-press reading. PURE.

    Shared by the preview and the verification, so the two ends of a write
    cannot disagree about what a menu says. Every ``why`` is built from counts
    and this module's own words.
    """
    act = act_for(action)
    reading = reading if isinstance(reading, dict) else {}
    structure = dict(reading.get("structure") or {})
    facts: dict[str, Any] = {
        "active_rows": coerce.as_count(structure.get("active_rows")),
        "triggers_in_the_active_row": coerce.as_count(structure.get("triggers_in_the_active_row")),
        "rows_rendered": coerce.as_count(structure.get("rows_rendered")),
        "menu_pressed_open": bool(reading.get("pressed")),
        "menu_opened": bool(reading.get("opened")),
        "words": dict(reading.get("words") or {}),
        "links": dict(reading.get("links") or {}),
        "other_items": coerce.as_count(reading.get("other_items")),
        "menu_closed_again": reading.get("closed"),
        "nothing_inside_the_menu_was_pressed": True,
        "error": reading.get("error"),
    }
    if not reading.get("ready"):
        return facts, UNKNOWN, str(reading.get("why_not_pressed") or "the page was not read.")
    if reading.get("error"):
        return facts, UNKNOWN, (
            f"the menu could not be read ({reading['error']} was raised; its "
            "message is not repeated here)."
        )
    if reading.get("closed") is not True:
        return facts, UNKNOWN, (
            "the menu did NOT read closed after Escape, so the page is not as it "
            "was found -- nothing more is pressed, and in a live session this is "
            "a stop."
        )
    if not reading.get("opened"):
        return facts, UNKNOWN, (
            "the trigger was pressed and the menu drew no item inside the bound; "
            "it was closed again, and nothing was read."
        )
    state, why = _family_state(act, facts["words"])
    return facts, state, (
        why + " Read by the sanctioned preview press: the one menu in the row "
        "wearing the active marker on the conversation you named was opened, "
        "its words counted, nothing inside it pressed, and it was closed on "
        "Escape and read closed."
    )


async def read_state(page: Any, action: Any) -> tuple[dict[str, Any], str, str]:
    """The preview's reading: the preview press, then the verdict for ``action``."""
    return menu_verdict(await preview_press(page), action)


def closed_menu_state(structure: dict[str, Any]) -> tuple[str, str]:
    """GATE 5's reading at click time, off the trigger alone. PURE.

    The word cannot be read without opening the menu, and the confirmed press
    opens it -- then :func:`menu_item_gate` re-reads the word. So the click-time
    state is the trigger's: :data:`MENU_CLOSED` when the page is the measured
    shape for a press, ``unknown`` otherwise.
    """
    ready, why = _ready_to_open(structure)
    if not ready:
        return UNKNOWN, why
    return MENU_CLOSED, (
        "exactly one row wears the active marker, holding exactly one options "
        "trigger, collapsed, with no item drawn: the press opens that menu and "
        "the word is re-read inside it before anything else is pressed."
    )


async def menu_item_gate(page: Any, action: Any) -> dict[str, Any]:
    """After the confirmed press opened the menu: may the item be pressed?

    THE CONFIRMED PRESS RE-READS THE WORD AND REFUSES ON THE INVERSE. A
    bounded wait for the items (deciding nothing), then the words counted in
    the page. ``proceed`` only when the act's own word is drawn EXACTLY ONCE
    and its inverse NOT AT ALL; ``selector`` is then that item, strict and
    visible-only. On a refusal, ``close_selector`` is the trigger when it still
    reads expanded -- the menu is closed by the same click that opened it,
    through ``writes.perform``'s one click site, and nothing inside it is
    pressed. Never raises.
    """
    act = act_for(action)
    out: dict[str, Any] = {
        "proceed": False,
        "selector": "",
        "close_selector": "",
        "refused_condition": None,
        "why": "",
        "observed": {},
        "polls": 0,
    }
    try:
        out["polls"] = await _wait_for_items(page)
        words = await _read_words(page)
        expanded = await _expanded(page)
        forward = coerce.as_count(words["words"].get(act.word))
        inverse = coerce.as_count(words["words"].get(act.inverse)) if act.inverse else 0
        out["observed"] = {
            "expanded": expanded,
            "word": act.word,
            "word_drawn": forward,
            "inverse": act.inverse or None,
            "inverse_drawn": inverse,
            "items_visible": words["items_visible"],
            "other_items": words["other_items"],
            "error": words.get("error"),
        }
        if words.get("error"):
            out["refused_condition"] = "0_unreadable"
            out["why"] = f"the open menu could not be read ({words['error']}); nothing in it is pressed."
        elif inverse:
            out["refused_condition"] = "1_inverse_drawn"
            out["why"] = (
                f"the menu draws {act.inverse!r}: the conversation is already where "
                f"this act would take it, and pressing {act.word!r} is not "
                "possible -- pressing the item it draws instead would do the "
                "OPPOSITE. Refused; nothing in the menu is pressed."
            )
        elif forward != 1:
            out["refused_condition"] = "2_word_not_exactly_one"
            out["why"] = (
                f"the menu draws {act.word!r} {forward} time(s), where exactly once "
                "is required; nothing in it is pressed."
            )
        else:
            out["proceed"] = True
            out["selector"] = item_selector(act.word)
            out["why"] = (
                f"the menu the press opened draws {act.word!r} exactly once"
                + (f" and {act.inverse!r} not at all" if act.inverse else "")
                + ": that item is pressed, strictly, and nothing else."
            )
        if not out["proceed"] and expanded == "true":
            out["close_selector"] = ACTIVE_TRIGGER
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["proceed"] = False
        out["selector"] = ""
        out["refused_condition"] = "0_unreadable"
        out["why"] = f"the open menu could not be read ({type(exc).__name__}); nothing in it is pressed."
    return out


async def read_after_press(page: Any) -> dict[str, Any]:
    """What the item press left on the page, BEFORE anything else happens.

    Counts and closed words only, and it presses nothing: a dialog here is a
    further step that opened and is NOT taken. ``dialog_words`` counts each
    word of :data:`DIALOG_WORDS` among the dialogs' buttons; the rest are
    counted, never read. Never raises.
    """
    out: dict[str, Any] = {
        "dialogs": 0,
        "alertdialogs": 0,
        "dialog_buttons": 0,
        "dialog_words": {},
        "other_dialog_buttons": 0,
        "active_rows": 0,
        "expanded": None,
        "items_visible": 0,
        "message_events": 0,
        "error": None,
    }
    try:
        out["dialogs"] = await _count(page, DIALOGS)
        out["alertdialogs"] = await _count(page, ALERTDIALOGS)
        named = 0
        for root in (DIALOGS, ALERTDIALOGS):
            dialogs = page.locator(root)
            out["dialog_buttons"] += coerce.as_count(await dialogs.get_by_role("button").count())
            for word in DIALOG_WORDS:
                count = coerce.as_count(
                    await dialogs.get_by_role("button", name=word, exact=True).count()
                )
                out["dialog_words"][word] = out["dialog_words"].get(word, 0) + count
                named += count
        out["other_dialog_buttons"] = max(0, out["dialog_buttons"] - named)
        out["active_rows"] = await _count(page, ACTIVE_ROW)
        out["expanded"] = await _expanded(page)
        if out["active_rows"] == 1:
            out["items_visible"] = await _visible_items(page)
        out["message_events"] = await _count(page, threads.EVENT_SELECTOR)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def after_press_note(reading: dict[str, Any]) -> dict[str, Any]:
    """The receipt's account of what the item press drew. PURE."""
    reading = reading if isinstance(reading, dict) else {}
    dialogs = coerce.as_count(reading.get("dialogs")) + coerce.as_count(reading.get("alertdialogs"))
    return {
        **{key: reading.get(key) for key in (
            "dialogs", "alertdialogs", "dialog_buttons", "dialog_words",
            "other_dialog_buttons", "active_rows", "expanded", "items_visible",
            "message_events", "error",
        )},
        "further_step_opened": dialogs > 0,
        "what_was_done_with_it": (
            "NOTHING: a dialog the item press drew is reported here by its counts "
            "and closed words, and nothing in it was pressed. It is the "
            "measurement this press's first fire exists to take."
            if dialogs
            else "no dialog was drawn after the item press."
        ),
    }


def verification_verdict(
    reading: dict[str, Any], action: Any, *, item_pressed: bool
) -> tuple[str, str]:
    """``(state, why)`` after the act, off a preview-press reading. PURE.

    :data:`NOT_CHANGED` when the item was not pressed, or was pressed and the
    menu still reads the word the act starts from -- this call changed nothing;
    the act's destination when the menu reads it after the press; ``unknown``
    otherwise. FOR ARCHIVE, the DERIVED positive: the conversation's row no
    longer drawn on a list that drew rows, on a fresh render of its own
    address. The caller says whether the reading is in place or fresh.
    """
    act = act_for(action)
    if not item_pressed:
        return NOT_CHANGED, (
            f"the item {act.word!r} was not pressed -- the confirmed press refused "
            "on the word it re-read -- so this call changed nothing in the "
            "conversation."
        )
    reading = reading if isinstance(reading, dict) else {}
    structure = dict(reading.get("structure") or {})
    if (
        act.action == ARCHIVE
        and not structure.get("error")
        and coerce.as_count(structure.get("active_rows")) == 0
        and coerce.as_count(structure.get("rows_rendered")) > 0
    ):
        return ARCHIVED, (
            "after the press, the conversation's own address draws a list of "
            f"{coerce.as_count(structure.get('rows_rendered'))} rendered row(s) and "
            "NO row wearing the active marker: the conversation left the list "
            "it was drawn in. DERIVED, not measured -- no capture holds an "
            "archived conversation's page -- and stated as such."
        )
    _facts, state, why = menu_verdict(reading, action)
    if state == act.to_state:
        return state, f"after the press the menu reads {state}: " + why
    if state == act.from_state:
        return NOT_CHANGED, (
            f"the item was pressed and the menu still reads {state} -- the act "
            "did not land: " + why
        )
    return UNKNOWN, why
