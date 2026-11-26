"""His messaging folders: the Archived view, read through ONE folder switch and put back.

Census row ``M M28`` (view and restore archived conversations), its VIEW half,
built by lane build-msg2 on 2026-11-26: the folder press the row needs, the
shipped read ``linkedin_archived_conversations``, and its one entry in
``readonly.SANCTIONED_MUTATIONS`` -- the order integration 4 queued for the
first build lane after it (its record's section 9), on the ruling
``VIEW-SWITCH-PRESS-RESTORED``: "a press that changes which rows a view shows
is permitted if the view is RESTORED afterwards and a before/after reading
proves it."

## WHAT IS MEASURED, AND WHERE

Live session 11, load 39 (``/messaging/``, behind the receipt guard), three
tracked skeletons:

* ``tests/fixtures/live11/messaging_guarded.html``: ONE folder pill,
  ``button[data-test-messaging-inbox-filters__folder-pill]``
  (``aria-expanded`` false), its own text the folder shown -- ``Focused`` --
  inside ONE dropdown root ``div[data-test-messaging-inbox-filters__folder-dropdown]``
  whose content node is empty while closed;
* ``messaging_folder_open.html``: the pill pressed -- ``aria-expanded`` true,
  the content drawing FOUR ``div[role=button]`` choices: ``Focused``,
  ``Other``, ``Archived``, ``Spam``;
* ``messaging_archived.html``: ``Archived`` chosen -- the pill reads
  ``Archived`` and is closed, the list draws 20 rows (10 rendered), no row
  wears the active marker, and the filter pills are gone. The capture then
  chose the folder it had read and verified it.

The composer's list (``tests/fixtures/live11/messaging_list.html``,
``/messaging/compose/``, which opens no conversation) draws the same pill and
the same dropdown root, closed. THAT THE SWITCH BEHAVES THERE AS IT DID ON
``/messaging/`` IS DERIVED -- the press is the same component's -- so the pill,
the list and the address are read after every step, and a page that does not
switch reads as not switched rather than as an empty folder.

## WHAT THIS DOES NOT DO

It restores no conversation to the inbox: the RESTORE half of ``M M28`` is a
write whose control -- an archived row's own menu item -- has never been
captured. It opens no conversation and reads no message text: an archived row
is listed exactly as ``threads.read_conversation_list`` lists any row, unread
paired to the row, names only on the caller's opt-in and only as people
records (``threads.list_result``).

## THE ONE MUTATION

:func:`_activate` is the only call site that presses, declared in
``readonly.SANCTIONED_MUTATIONS``; every press of the sequence -- the pill, the
choice, the pill again, the choice it read before, and a close of a menu that
drew the wrong choices -- goes through it, always on a selector this module
built from its own constants, and :func:`read_archived` is the only function
that reaches it (through :func:`_switch_to` and :func:`_close_if_open`).
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from linkedin_server import coerce, threads

#: THE RULING the press rests on, by its register id.
RULING = "VIEW-SWITCH-PRESS-RESTORED"

#: The folder pill and its dropdown, scoped to ``<main>`` (measured: one each
#: on every session-11 messaging capture, the composer's list included).
PILL = "main button[data-test-messaging-inbox-filters__folder-pill]"
ROOT = "main div.artdeco-dropdown[data-test-messaging-inbox-filters__folder-dropdown]"
CONTENT = ROOT + " .artdeco-dropdown__content"

#: The four folders the open dropdown draws, by their exact words (measured).
FOLDERS: tuple[str, ...] = ("Focused", "Other", "Archived", "Spam")
ARCHIVED: str = "Archived"

#: Bounds. A liveness bound decides nothing: the reading at its end decides.
POLLS: int = 15
POLL_MS: int = 200
CLICK_TIMEOUT_MS: int = 5_000

#: The parts of a list reading the restore proof compares, before and after:
#: counts, the unread positions and the receipt evidence -- never a name.
_VIEW_KEYS: tuple[str, ...] = (
    "rows_total",
    "rows_rendered",
    "rows_placeholder",
    "message_events",
    "active_rows",
)


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def _read_pill(page: Any) -> dict[str, Any]:
    """The pill: how many, whether expanded (a closed token), which folder word
    it wears (matched in the page against :data:`FOLDERS`; one of them or
    ``None``), and how many choices its dropdown draws. COUNTS AND CLOSED
    WORDS. Never raises; an error is an exception TYPE."""
    out: dict[str, Any] = {
        "pills": 0,
        "expanded": None,
        "folder": None,
        "choices_drawn": 0,
        "error": None,
    }
    try:
        out["pills"] = await _count(page, PILL)
        if out["pills"] == 1:
            value = await page.locator(PILL).first.get_attribute("aria-expanded")
            out["expanded"] = (
                None if value is None
                else "true" if value == "true"
                else "false" if value == "false"
                else "other"
            )
            worn = [word for word in FOLDERS if await _count(page, f'{PILL}:text-is("{word}")') == 1]
            out["folder"] = worn[0] if len(worn) == 1 else None
            out["choices_drawn"] = coerce.as_count(
                await page.locator(CONTENT).get_by_role("button").count()
            )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _is_closed_on(pill: dict[str, Any], word: Optional[str]) -> bool:
    """The pill wears ``word``, reads collapsed, and draws no choice. PURE."""
    return (
        pill.get("pills") == 1
        and pill.get("folder") == word
        and pill.get("expanded") == "false"
        and not pill.get("choices_drawn")
        and not pill.get("error")
    )


def choice_selector(word: str) -> str:
    """The one choice of the open dropdown named ``word``, by its exact name,
    visible only. Raises for a word outside the four: nothing a page chose can
    become a selector here."""
    if word not in FOLDERS:
        raise ValueError("refusing to build a folder selector for a word outside the four")
    return f'{CONTENT} >> role=button[name="{word}"s] >> visible=true'


async def _activate(page: Any, selector: str) -> None:
    """THE ONE PRESS IN THIS MODULE. Declared in ``readonly.SANCTIONED_MUTATIONS``;
    reached only from :func:`read_archived`'s sequence, with a selector this
    module built from its own constants. Strict: a selector matching more than
    one control raises instead of choosing."""
    await page.click(selector, timeout=CLICK_TIMEOUT_MS, strict=True)


async def _wait(page: Any, done: Callable[[dict[str, Any]], bool]) -> int:
    polls = 0
    for polls in range(1, POLLS + 1):
        if done(await _read_pill(page)):
            break
        await page.wait_for_timeout(POLL_MS)
    return polls


async def _close_if_open(page: Any, steps: list[dict[str, Any]]) -> None:
    """A dropdown left open is closed by the pill that opened it -- only while
    it reads open."""
    pill = await _read_pill(page)
    if pill.get("pills") == 1 and pill.get("expanded") == "true":
        await _activate(page, PILL)
        await _wait(page, lambda r: r.get("expanded") == "false")
        steps.append({"step": "close", "pressed": True, "pill": await _read_pill(page)})


async def _switch_to(page: Any, word: str, steps: list[dict[str, Any]]) -> bool:
    """Open the pill, choose ``word``, wait for the pill to wear it. Records
    each step's reading; returns whether the pill wears ``word``, closed, at
    the end. Presses nothing unless the pill reads exactly the measured closed
    shape first."""
    pill = await _read_pill(page)
    if pill.get("pills") != 1 or pill.get("expanded") != "false" or pill.get("choices_drawn"):
        steps.append({"step": "open", "pressed": False, "pill": pill})
        return False
    await _activate(page, PILL)
    polls = await _wait(page, lambda r: bool(r.get("choices_drawn")))
    opened = await _read_pill(page)
    drawn = coerce.as_count(
        await page.locator(CONTENT).get_by_role("button", name=word, exact=True).count()
    )
    steps.append(
        {"step": "open", "pressed": True, "polls": polls, "pill": opened, "choice_drawn": drawn}
    )
    if drawn != 1:
        # NOT THE MEASURED MENU: nothing in it is chosen, and the pill that
        # opened it closes it again.
        await _close_if_open(page, steps)
        return False
    await _activate(page, choice_selector(word))
    polls = await _wait(page, lambda r: _is_closed_on(r, word))
    after = await _read_pill(page)
    steps.append({"step": "choose", "pressed": True, "polls": polls, "pill": after})
    return _is_closed_on(after, word)


def view_of(reading: Any) -> dict[str, Any]:
    """The comparable shape of one list reading: counts, unread positions and
    the reading's error type -- never a name. PURE."""
    reading = reading if isinstance(reading, dict) else {}
    out: dict[str, Any] = {key: coerce.as_count(reading.get(key)) for key in _VIEW_KEYS}
    out["unread_positions"] = [
        coerce.as_count(row.get("position"))
        for row in reading.get("rows") or []
        if isinstance(row, dict) and row.get("rendered") and row.get("unread") is True
    ]
    out["error"] = reading.get("error")
    return out


def _on_the_composer(page: Any) -> bool:
    """Is the page still the composer's list? A COMPARISON's boolean, so no
    address is ever bound to a name here."""
    return threads.is_the_compose_address(getattr(page, "url", None)) is True


async def read_archived(page: Any, *, include_names: bool = False) -> dict[str, Any]:
    """THE FOLDER SWITCH, APPLIED AND PUT BACK, with the Archived list read between.

    On the composer's list page already open. The pill and the list are read
    BEFORE anything is pressed; then the pill is opened, ``Archived`` chosen,
    and the pill waited for until it wears ``Archived``, closed; the list is
    read; then the pill is opened again and the folder it wore BEFORE chosen,
    and the list read again.

    ``restored`` is True only when the pill wears that folder again, closed,
    the page is still the composer's list, and the list read after EQUALS the
    list read before (:func:`view_of`) -- the before/after reading the ruling
    requires. A switch left applied is the loudest answer this returns. Never
    raises; an error is an exception TYPE.
    """
    out: dict[str, Any] = {
        "ruling": RULING,
        "before": {},
        "steps": [],
        "switched": False,
        "archived": None,
        "restore_steps": [],
        "after": {},
        "folder_restored": None,
        "view_matches": None,
        "restored": None,
        "why": "",
        "error": None,
    }
    before_pill = await _read_pill(page)
    before_view = view_of(await threads.read_conversation_list(page))
    on_composer_before = _on_the_composer(page)
    out["before"] = {"pill": before_pill, "view": before_view, "on_the_composer": on_composer_before}
    original: Optional[str] = before_pill.get("folder")
    if not _is_closed_on(before_pill, original) or original is None or not on_composer_before:
        out["why"] = (
            f"the page draws {coerce.as_count(before_pill.get('pills'))} folder pill(s), "
            f"wearing {original!r}, expanded {before_pill.get('expanded')!r}, on the "
            f"composer's list: {on_composer_before}. Exactly one closed pill wearing one of "
            f"{list(FOLDERS)}, on the composer's list, is the measured shape; nothing was "
            "pressed."
        )
        out["folder_restored"] = out["view_matches"] = out["restored"] = True
        return out
    if original == ARCHIVED:
        out["switched"] = True
        out["archived"] = await threads.read_conversation_list(page, include_names=include_names)
        out["folder_restored"] = out["view_matches"] = out["restored"] = True
        out["why"] = "the pill already wore Archived; nothing was pressed."
        return out
    try:
        out["switched"] = await _switch_to(page, ARCHIVED, out["steps"])
        if out["switched"]:
            out["archived"] = await threads.read_conversation_list(
                page, include_names=include_names
            )
            out["archived_on_the_composer"] = _on_the_composer(page)
    except Exception as exc:  # noqa: BLE001 - reported; the restore still runs
        out["error"] = type(exc).__name__
    finally:
        try:
            await _close_if_open(page, out["restore_steps"])
            now = await _read_pill(page)
            if now.get("folder") != original:
                await _switch_to(page, original, out["restore_steps"])
            after_pill = await _read_pill(page)
            after_view = view_of(await threads.read_conversation_list(page))
            on_composer_after = _on_the_composer(page)
            out["after"] = {"pill": after_pill, "view": after_view, "on_the_composer": on_composer_after}
            out["folder_restored"] = _is_closed_on(after_pill, original) and on_composer_after
            out["view_matches"] = after_view == before_view
            out["restored"] = bool(out["folder_restored"] and out["view_matches"])
        except Exception as exc:  # noqa: BLE001 - the restore is not known done
            out["folder_restored"] = out["view_matches"] = None
            out["restored"] = False
            out["error"] = out["error"] or type(exc).__name__
    worn_after = (out["after"].get("pill") or {}).get("folder")
    if out["restored"] is not True:
        if out["folder_restored"] is True:
            out["why"] = (
                f"the pill wears {original!r} again, closed, but the list read after "
                "the switch back does NOT equal the list read before it (its counts or "
                "its unread positions differ), so the restore is not proven. Open your "
                "messages and look at the list yourself."
            )
        else:
            out["why"] = (
                f"THE FOLDER WAS NOT PUT BACK: the pill wears {worn_after!r} where "
                f"{original!r} was read before, or the page left the composer's list. "
                f"Open your messages and choose {original!r} in the folder menu yourself."
            )
    elif not out["switched"]:
        out["why"] = (
            "the folder menu did not switch to Archived as measured, so no archived "
            "row was read; the view was read again and is as it was."
        )
    else:
        out["why"] = (
            f"the pill was switched to Archived, the list read, and switched back to "
            f"{original!r}: the pill wears it again, closed, and the list reads exactly "
            "as it did before."
        )
    return out


def archived_result(reading: Any, landed: Any, *, include_names: bool) -> dict[str, Any]:
    """What ``linkedin_archived_conversations`` returns. PURE; every field
    testable without a server. The rows are ``threads.list_result``'s, so an
    archived row is described exactly as an inbox row is -- unread paired to
    the row, names only as people records on the caller's opt-in."""
    reading = reading if isinstance(reading, dict) else {}
    archived = reading.get("archived")
    listed = (
        threads.list_result(archived, landed, include_names=include_names)
        if isinstance(archived, dict)
        else None
    )
    restored = reading.get("restored") is True
    steps = list(reading.get("steps") or []) + list(reading.get("restore_steps") or [])
    return {
        "ok": bool(reading.get("switched")) and restored and listed is not None,
        "folder": ARCHIVED,
        "archived": listed,
        "switched_to_archived": bool(reading.get("switched")),
        "restored": restored,
        "folder_restored": reading.get("folder_restored"),
        "view_matches_before": reading.get("view_matches"),
        "why": reading.get("why"),
        "folder_before": ((reading.get("before") or {}).get("pill") or {}).get("folder"),
        "folder_after": ((reading.get("after") or {}).get("pill") or {}).get("folder"),
        "presses": sum(1 for step in steps if isinstance(step, dict) and step.get("pressed")),
        "ruling": RULING,
        "error": reading.get("error"),
        "pages_loaded": 1,
        "not_claimed": [
            "that every archived conversation was listed: one view of the folder, as drawn",
            "that the switch behaves on the composer's list as it did on /messaging/, where "
            "it was captured: DERIVED, and the pill, the list and the address are read "
            "after every step",
            "a restore of any conversation to the inbox: that control has never been "
            "captured",
        ],
    }
