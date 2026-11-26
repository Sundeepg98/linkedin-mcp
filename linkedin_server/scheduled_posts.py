"""His scheduled posts: the list behind the post composer's Schedule button, read and closed.

Census row ``M C14``, built by lane build-msg2 on 2026-11-26 on ruling
``SCHEDULED-LIST-AS-A-SHIPPED-READ`` (the orchestrator, 14:10, registered at
integration 4): "His scheduled posts list is a shipped read: the post composer
opened empty, Schedule post, then View all scheduled posts; the list read
(zero only on a drawn empty headline), closed with nothing typed or scheduled,
no draft verified, and a stop on any autosave sign."

## WHY THIS MODULE PRESSES WHERE ``press`` WILL NOT

``press._COMPOSER_MARKERS`` refuses every press on ``/preload/sharebox/``: a
composer may autosave, and readable is not pressable. The ruling above is the
named exception, for exactly this sequence, so it lives here with its own drain
point (:func:`_press`, one ``readonly.SANCTIONED_MUTATIONS`` entry) and the
general gate is not widened.

## WHAT IS MEASURED, AND WHERE

Live session 11, load 25: ``/preload/sharebox/``, served exact, nothing typed.
Three tracked skeletons with LinkedIn's words put back by keyed shape
(``tests/fixtures/live11/sharebox_words.html``,
``sharebox_schedule_open_words.html``,
``sharebox_scheduled_list_open_words.html``), measured by count:

    state       share-box modal  editor (blank)  Post (disabled)  Schedule post  View all  heading            empty headline  modal Dismiss
    composer          1              1 (1)          1 (yes)             1           0      --                       0              1
    schedule          1              0              0                   0           1      "Schedule post"          0              1
    list              1              0              0                   0           0      "Scheduled posts"        1              1

The list capture is EMPTY: its one ``h2.artdeco-empty-state__headline`` reads
"No scheduled posts yet". A populated list has never been captured, so this
module reports ZERO only on that drawn headline and ``unknown`` on anything
else -- never a count it cannot read.

## WHAT "NO DRAFT" MEANS HERE, stated because it is the ruling's hardest clause

No draft surface is reachable: 17 candidate draft addresses were run against
the read boundary on 2026-08-31 and all 17 were refused. So the check is
empirical and in three parts: (1) the composer opened EMPTY -- its editor
blank, Post drawn disabled -- before the first press, or nothing is pressed;
(2) the modal closed on its own Dismiss with no dialog left and no toast drawn
-- a dialog or a toast after it is an AUTOSAVE SIGN and stops everything; and
(3) the tool loads the composer a SECOND time and reads it empty again
(:func:`reopened_empty`), which is where a saved draft would show. Nothing is
typed at any step: no fill, no keyboard call exists in this module.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from linkedin_server import coerce, dom

#: THE RULING the presses rest on, by its register id.
RULING = "SCHEDULED-LIST-AS-A-SHIPPED-READ"

#: The composer's own address (admitted for reading by name in ``readonly``).
COMPOSER_URL = "https://www.linkedin.com" + dom.SHAREBOX_COMPOSER_HREF

#: The share box's modal, and everything below is scoped to it.
MODAL = '[role="dialog"].share-box-v2__modal'
EDITOR = MODAL + " " + dom.post_editor_selector()
BLANK_EDITOR = EDITOR + ".ql-blank"
POST = MODAL + " button.share-actions__primary-action"
SCHEDULE = MODAL + ' button.share-actions__scheduled-post-btn[aria-label="Schedule post"]'
DISMISS = MODAL + ' button.artdeco-modal__dismiss[data-test-modal-close-btn][aria-label="Dismiss"]'
HEADING = MODAL + " .artdeco-modal__header h2"
EMPTY_HEADLINE = MODAL + " .share-post-list-view__empty-state h2.artdeco-empty-state__headline"
VIEW_ALL_WORDS = "View all scheduled posts"
VIEW_ALL = MODAL + f' >> role=button[name="{VIEW_ALL_WORDS}"s] >> visible=true'
DIALOGS = '[role="dialog"], [role="alertdialog"]'
TOASTS = "section.artdeco-toasts .artdeco-toasts_toasts > *"

#: The words each state draws, compared IN THE PAGE (measured, exact).
SCHEDULE_HEADING_WORDS = "Schedule post"
LIST_HEADING_WORDS = "Scheduled posts"
EMPTY_WORDS = "No scheduled posts yet"
POST_WORDS = dom.POST_SUBMIT_NAME

#: Bounds. A liveness bound decides nothing: the reading at its end decides.
POLLS: int = 15
POLL_MS: int = 200
CLICK_TIMEOUT_MS: int = 5_000


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def _read_state(page: Any) -> dict[str, Any]:
    """Every count the sequence decides on. COUNTS AND BOOLEANS ONLY: each word
    is compared inside the page and comes back as a count. Never raises; an
    error is an exception TYPE."""
    out: dict[str, Any] = {
        "modals": 0, "editors": 0, "editors_blank": 0, "post_buttons": 0,
        "post_enabled": None, "schedule_buttons": 0, "schedule_heading": 0,
        "view_all": 0, "list_heading": 0, "empty_headline": 0, "dismiss": 0,
        "dialogs": 0, "toasts": 0, "error": None,
    }
    try:
        out["modals"] = await _count(page, MODAL)
        out["editors"] = await _count(page, EDITOR)
        out["editors_blank"] = await _count(page, BLANK_EDITOR)
        post = page.locator(POST).filter(
            has=page.get_by_text(POST_WORDS, exact=True)
        )
        out["post_buttons"] = coerce.as_count(await post.count())
        if out["post_buttons"] == 1:
            out["post_enabled"] = bool(await post.first.is_enabled())
        out["schedule_buttons"] = await _count(page, SCHEDULE)
        out["schedule_heading"] = await _count(page, f'{HEADING}:text-is("{SCHEDULE_HEADING_WORDS}")')
        out["list_heading"] = await _count(page, f'{HEADING}:text-is("{LIST_HEADING_WORDS}")')
        out["view_all"] = await _count(page, VIEW_ALL)
        out["empty_headline"] = await _count(page, f'{EMPTY_HEADLINE}:text-is("{EMPTY_WORDS}")')
        out["dismiss"] = await _count(page, DISMISS)
        out["dialogs"] = await _count(page, DIALOGS)
        out["toasts"] = await _count(page, TOASTS)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def composer_empty(state: dict[str, Any]) -> bool:
    """The composer as measured, EMPTY: one modal, one editor and it blank, one
    Post drawn disabled, one Schedule post, one modal Dismiss. PURE."""
    return (
        not state.get("error")
        and state.get("modals") == 1
        and state.get("editors") == 1
        and state.get("editors_blank") == 1
        and state.get("post_buttons") == 1
        and state.get("post_enabled") is False
        and state.get("schedule_buttons") == 1
        and state.get("dismiss") == 1
    )


def holds_text(state: dict[str, Any]) -> bool:
    """AN AUTOSAVE SIGN: an editor drawn and not blank, or Post drawn enabled --
    the composer holds words nobody typed this call. PURE."""
    return bool(
        (coerce.as_count(state.get("editors")) > coerce.as_count(state.get("editors_blank")))
        or state.get("post_enabled") is True
    )


def schedule_open(state: dict[str, Any]) -> bool:
    return (
        not state.get("error")
        and state.get("modals") == 1
        and state.get("schedule_heading") == 1
        and state.get("view_all") == 1
        and state.get("dismiss") == 1
    )


def list_open(state: dict[str, Any]) -> bool:
    return (
        not state.get("error")
        and state.get("modals") == 1
        and state.get("list_heading") == 1
        and state.get("dismiss") == 1
    )


def closed(state: dict[str, Any], toasts_before: int) -> bool:
    """No modal, no dialog of any kind, no toast that was not there before. PURE."""
    return (
        not state.get("error")
        and state.get("modals") == 0
        and state.get("dialogs") == 0
        and coerce.as_count(state.get("toasts")) <= toasts_before
    )


async def _press(page: Any, selector: str) -> None:
    """THE ONE PRESS IN THIS MODULE. Declared in ``readonly.SANCTIONED_MUTATIONS``;
    reached only from :func:`read_scheduled` and :func:`close_composer`, with
    a selector this module built from its own constants. Strict."""
    await page.click(selector, timeout=CLICK_TIMEOUT_MS, strict=True)


async def _wait(page: Any, done: Callable[[dict[str, Any]], bool]) -> tuple[dict[str, Any], int]:
    polls = 0
    state = await _read_state(page)
    for polls in range(1, POLLS + 1):
        if done(state):
            break
        await page.wait_for_timeout(POLL_MS)
        state = await _read_state(page)
    return state, polls


async def _close(page: Any, out: dict[str, Any], toasts_before: int) -> None:
    """Dismiss the modal -- only while exactly one modal and one modal Dismiss
    are drawn and no editor holds text -- then read that it closed clean."""
    now = await _read_state(page)
    if holds_text(now):
        out["autosave_sign"] = "the composer held text before the close"
        out["steps"].append({"step": "close", "pressed": False, "state": now})
        return
    if now.get("modals") != 1 or now.get("dismiss") != 1:
        out["steps"].append({"step": "close", "pressed": False, "state": now})
        out["closed"] = closed(now, toasts_before)
        return
    await _press(page, DISMISS)
    after, polls = await _wait(page, lambda s: closed(s, toasts_before))
    out["steps"].append({"step": "close", "pressed": True, "polls": polls, "state": after})
    out["closed"] = closed(after, toasts_before)
    if not out["closed"]:
        out["autosave_sign"] = (
            "a dialog or a toast was drawn after Dismiss" if after.get("modals") == 0
            else "the composer did not close on Dismiss"
        )


async def read_scheduled(page: Any) -> dict[str, Any]:
    """THE SEQUENCE THE RULING NAMES, on the composer page already open.

    Refuses before any press unless the composer reads EMPTY
    (:func:`composer_empty`); a composer holding text is an AUTOSAVE SIGN and
    nothing at all is pressed. Then: Schedule post, a bounded wait for the
    schedule dialog; View all scheduled posts, a bounded wait for the list;
    the list read; the modal's own Dismiss and a read that it closed with no
    dialog and no toast left. A state that does not arrive as measured
    skips straight to the close. Never raises; an error is an exception TYPE.
    """
    out: dict[str, Any] = {
        "ruling": RULING,
        "steps": [],
        "list_read": False,
        "empty_headline_drawn": None,
        "scheduled": None,
        "closed": None,
        "autosave_sign": None,
        "why": "",
        "error": None,
    }
    start = await _read_state(page)
    out["steps"].append({"step": "load", "pressed": False, "state": start})
    toasts_before = coerce.as_count(start.get("toasts"))
    if holds_text(start):
        out["autosave_sign"] = "the composer opened holding text"
        out["why"] = (
            "STOPPED ON AN AUTOSAVE SIGN: the composer opened with text in it or "
            "Post enabled -- likely a draft LinkedIn kept. Nothing was pressed. "
            "Open the post composer yourself and look."
        )
        return out
    if not composer_empty(start):
        out["closed"] = start.get("modals") == 0
        out["why"] = (
            "the composer did not draw the measured empty shape (one modal, a blank "
            "editor, Post disabled, one Schedule post, one Dismiss), so nothing was "
            "pressed."
        )
        return out
    try:
        await _press(page, SCHEDULE)
        opened, polls = await _wait(page, schedule_open)
        out["steps"].append({"step": "schedule", "pressed": True, "polls": polls, "state": opened})
        if schedule_open(opened):
            await _press(page, VIEW_ALL)
            listed, polls = await _wait(page, list_open)
            out["steps"].append({"step": "view_all", "pressed": True, "polls": polls, "state": listed})
            if list_open(listed):
                out["list_read"] = True
                out["empty_headline_drawn"] = listed.get("empty_headline") == 1
                out["scheduled"] = 0 if out["empty_headline_drawn"] else None
    except Exception as exc:  # noqa: BLE001 - reported; the close still runs
        out["error"] = type(exc).__name__
    finally:
        try:
            await _close(page, out, toasts_before)
        except Exception as exc:  # noqa: BLE001 - the close is not known done
            out["closed"] = False
            out["error"] = out["error"] or type(exc).__name__
    out["why"] = _why(out)
    return out


def _why(out: dict[str, Any]) -> str:
    if out.get("autosave_sign"):
        return (
            f"STOPPED ON AN AUTOSAVE SIGN ({out['autosave_sign']}); nothing more was "
            "pressed. Open the post composer yourself and check for a draft."
        )
    if out.get("closed") is not True:
        return (
            "THE COMPOSER WAS NOT SHOWN CLOSED after the sequence. Nothing was typed; "
            "open your feed and close the post composer yourself."
        )
    if not out.get("list_read"):
        return (
            "the schedule dialog or its list did not draw as measured, so no list was "
            "read; the composer was closed on its own Dismiss with nothing typed."
        )
    if out.get("scheduled") == 0:
        return (
            "the list drew its empty headline, 'No scheduled posts yet': zero "
            "scheduled posts. The composer was closed on its own Dismiss, nothing typed."
        )
    return (
        "the list opened without its empty headline, so it holds something this "
        "server has never seen drawn: the count is unknown, not zero. The composer "
        "was closed on its own Dismiss, nothing typed."
    )


async def reopened_empty(page: Any) -> dict[str, Any]:
    """THE THIRD PART OF "NO DRAFT": on the composer loaded a SECOND time, the
    editor reads blank and Post disabled -- where a kept draft would show.
    Reads only."""
    state = await _read_state(page)
    return {
        "state": state,
        "empty": composer_empty(state),
        "holds_text": holds_text(state),
    }


async def close_composer(page: Any) -> dict[str, Any]:
    """Close the composer the second load opened, the way the first was closed:
    the modal's own Dismiss, only while it reads empty."""
    out: dict[str, Any] = {"steps": [], "closed": None, "autosave_sign": None}
    start = await _read_state(page)
    await _close(page, out, coerce.as_count(start.get("toasts")))
    return out


def scheduled_result(
    reading: Any,
    reopened: Optional[dict[str, Any]],
    reclosed: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """What ``linkedin_scheduled_posts`` returns. PURE: counts, booleans and this
    module's own sentences."""
    reading = reading if isinstance(reading, dict) else {}
    reopened = reopened if isinstance(reopened, dict) else {}
    reclosed = reclosed if isinstance(reclosed, dict) else {}
    no_draft = bool(
        reading.get("closed") is True
        and not reading.get("autosave_sign")
        and reopened.get("empty") is True
    )
    presses = sum(
        1 for step in list(reading.get("steps") or []) + list(reclosed.get("steps") or [])
        if isinstance(step, dict) and step.get("pressed")
    )
    return {
        "ok": bool(reading.get("list_read")) and no_draft and reclosed.get("closed") is True,
        "scheduled_posts": reading.get("scheduled"),
        "count_state": (
            "zero" if reading.get("scheduled") == 0
            else "unknown" if reading.get("list_read") else "not_read"
        ),
        "empty_headline_drawn": reading.get("empty_headline_drawn"),
        "why": reading.get("why"),
        "closed": reading.get("closed"),
        "no_draft": no_draft,
        "reopened_empty": reopened.get("empty"),
        "reclosed": reclosed.get("closed"),
        "autosave_sign": reading.get("autosave_sign") or reclosed.get("autosave_sign")
        or ("the composer reopened holding text" if reopened.get("holds_text") else None),
        "presses": presses,
        "ruling": RULING,
        "error": reading.get("error"),
        "pages_loaded": 2 if reopened else 1,
        "not_claimed": [
            "a count of a populated list: no capture holds one, so anything but the "
            "drawn empty headline is unknown",
            "that no draft exists anywhere: no draft surface is reachable; the composer "
            "was read empty before the first press, closed clean, and read empty again "
            "on a second load",
        ],
    }
