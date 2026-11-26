"""A post in ONE group he names: the group page's closed share box, opened, and his words.

Census row ``M C64``, built by lane build-msg2 on 2026-11-26, behind the
single-use grant (EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS: publishing his own
content is an outward class, built behind the grant and fired only at a target
he names), on the capture B5-GROUP-COMPOSER-OPENS-EMPTY permitted.

## WHAT IS MEASURED, AND WHERE

Live session 11, load 36, a group he is a member of, nothing typed. Two
tracked skeletons with LinkedIn's words put back by keyed shape:

* ``tests/fixtures/live11/group_member_words.html`` -- the group page: ONE
  closed share box (``.share-box-feed-entry__closed-share-box``) whose top bar
  holds ONE button named ``Start a public post``, and no share-box modal;
* ``tests/fixtures/live11/group_composer_open_words.html`` -- that button
  pressed: ONE share-box modal (``[role=dialog].share-box-v2__modal``), ONE
  editor (``Text editor for creating content``) reading blank, ONE ``Post``
  drawn DISABLED, and NO ``Schedule post``.

THE GROUP COMPOSER IS TOLD FROM THE FEED'S BY WHAT IT LACKS. readers-msg26
proposed the audience entry's "group image" class as the marker; it is not one
-- the feed's own composer (``sharebox.html``) draws the same class at the
same place. Measured instead: the feed's composer draws ``Schedule post`` and
the group's does not. So the opened gate requires NO schedule button, beside
the modal having been opened by the trigger on the group page the landing was
held to.

## WHAT IS NOT MEASURED, and the receipt says so

What ``Post`` leaves -- a post in the group's feed, or one held for a manager's
approval -- has never been drawn: only the first fire at his order can show it.
The act is therefore ``Unverifiable`` and its receipt reads what the page drew
after the press, counted, without claiming the post exists. Its undo would be
deleting his own post (``outward_classes``, NEEDS-CAPTURE): not built.

## NO PRESS IS MADE HERE

This module only READS: every press goes through ``writes.perform``'s one
click site and his words through its fill site, with the selectors below.
"""
from __future__ import annotations

import re
from typing import Any

from linkedin_server import coerce, dom

#: The page state the preview reads, by its ``state_from`` key.
STATE_FROM = "group_share_box"
#: The closed box, its trigger drawn and no modal open.
BOX_CLOSED = "box_closed"
#: Anything else -- no box, two boxes, a modal already open.
UNKNOWN = "unknown"

BOX = "main .share-box-feed-entry__closed-share-box"
TRIGGER_WORDS = "Start a public post"
TRIGGER = BOX + f' >> role=button[name="{TRIGGER_WORDS}"s] >> visible=true'
MODAL = '[role="dialog"].share-box-v2__modal'
EDITOR = MODAL + " " + dom.post_editor_selector()
BLANK_EDITOR = EDITOR + ".ql-blank"
POST_WORDS = dom.POST_SUBMIT_NAME
POST_BUTTON = MODAL + " button.share-actions__primary-action"
POST = MODAL + f' >> role=button[name="{POST_WORDS}"s] >> visible=true'
SCHEDULE = MODAL + " button.share-actions__scheduled-post-btn"

#: Bounds. A liveness bound decides nothing: the gate decides on the reading
#: taken after it.
POLLS: int = 15
POLL_MS: int = 200


def _normalise(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def read_box(page: Any) -> dict[str, Any]:
    """The group page's closed share box: boxes, triggers by their exact name,
    modals. COUNTS ONLY. Never raises; an error is an exception TYPE."""
    out: dict[str, Any] = {"boxes": 0, "triggers": 0, "modals": 0, "error": None}
    try:
        out["boxes"] = await _count(page, BOX)
        out["triggers"] = await _count(page, TRIGGER)
        out["modals"] = await _count(page, MODAL)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def box_state(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` for the preview and gate 5. PURE."""
    if reading.get("error"):
        return UNKNOWN, f"the group page could not be read ({reading['error']})"
    boxes, triggers, modals = (
        coerce.as_count(reading.get(key)) for key in ("boxes", "triggers", "modals")
    )
    if boxes == 1 and triggers == 1 and modals == 0:
        return BOX_CLOSED, (
            f"the group page draws one closed share box and its {TRIGGER_WORDS!r} "
            "button, with no composer open -- the measured shape"
        )
    return UNKNOWN, (
        f"the group page draws {boxes} closed share box(es), {triggers} "
        f"{TRIGGER_WORDS!r} button(s) and {modals} open composer(s), where one, one "
        "and none are the measured shape. A page with no share box is not a group "
        "he can post in, as far as this server can tell."
    )


async def read_composer(page: Any, *, text: str | None = None) -> dict[str, Any]:
    """The composer the trigger opened: modals, editors (blank or not), Post
    (count, enabled), Schedule post, and -- when ``text`` is given -- whether
    the one editor holds EXACTLY those words (a boolean; the editor's text never
    leaves). Never raises."""
    out: dict[str, Any] = {
        "modals": 0, "editors": 0, "editors_blank": 0, "post_buttons": 0,
        "post_enabled": None, "schedule_buttons": 0, "holds_exactly": None,
        "error": None,
    }
    try:
        out["modals"] = await _count(page, MODAL)
        out["editors"] = await _count(page, EDITOR)
        out["editors_blank"] = await _count(page, BLANK_EDITOR)
        posts = page.locator(POST_BUTTON).filter(has=page.get_by_text(POST_WORDS, exact=True))
        out["post_buttons"] = coerce.as_count(await posts.count())
        if out["post_buttons"] == 1:
            out["post_enabled"] = bool(await posts.first.is_enabled())
        out["schedule_buttons"] = await _count(page, SCHEDULE)
        if text is not None and out["editors"] == 1:
            held = _normalise(await page.locator(EDITOR).first.inner_text())
            out["holds_exactly"] = held == _normalise(text)
    except Exception as exc:  # noqa: BLE001
        out["error"] = type(exc).__name__
    return out


def opened_gate(reading: dict[str, Any]) -> dict[str, Any]:
    """After the trigger press and BEFORE a word is typed: may they go in?
    One modal, one editor and it blank, one Post drawn disabled, and NO
    Schedule post -- the feed composer's mark. PURE."""
    out: dict[str, Any] = {"proceed": False, "observed": reading, "refused_condition": None, "why": ""}
    if reading.get("error"):
        out["refused_condition"] = "0_unreadable"
        out["why"] = f"the composer could not be read ({reading['error']}); nothing is typed."
        return out
    checks = (
        ("1_not_one_composer", reading.get("modals") == 1,
         f"{reading.get('modals')} share-box composer(s) are open, where exactly one is"),
        ("2_editor_not_one_blank", reading.get("editors") == 1 and reading.get("editors_blank") == 1,
         "the composer does not draw exactly one editor, blank -- it may hold a draft"),
        ("3_post_not_one_disabled", reading.get("post_buttons") == 1 and reading.get("post_enabled") is False,
         "the composer does not draw exactly one Post, disabled, as measured on an empty composer"),
        ("4_feed_composer", coerce.as_count(reading.get("schedule_buttons")) == 0,
         "the composer draws Schedule post, which the FEED's composer draws and the group's does not"),
    )
    for condition, ok, why in checks:
        if not ok:
            out["refused_condition"] = condition
            out["why"] = why + "; nothing is typed."
            return out
    out["proceed"] = True
    out["why"] = "one empty group composer opened: his words may go in"
    return out


def post_gate(reading: dict[str, Any]) -> dict[str, Any]:
    """After the fill and BEFORE Post: one modal, one editor holding EXACTLY his
    words, one Post now ENABLED, still no Schedule post. PURE."""
    out: dict[str, Any] = {
        "proceed": False, "selector": POST, "observed": reading,
        "refused_condition": None, "why": "",
    }
    if reading.get("error"):
        out["refused_condition"] = "0_unreadable"
        out["why"] = f"the composer could not be read after the fill ({reading['error']})"
        return out
    checks = (
        ("1_not_one_composer", reading.get("modals") == 1 and reading.get("editors") == 1,
         "the composer is not the one modal with one editor it was"),
        ("2_words_not_exact", reading.get("holds_exactly") is True,
         "the editor does not hold exactly his confirmed words"),
        ("3_post_not_enabled", reading.get("post_buttons") == 1 and reading.get("post_enabled") is True,
         "Post did not turn on after the words went in"),
        ("4_feed_composer", coerce.as_count(reading.get("schedule_buttons")) == 0,
         "the composer now draws Schedule post"),
    )
    for condition, ok, why in checks:
        if not ok:
            out["refused_condition"] = condition
            out["why"] = (
                why + ". Post was NOT pressed; his words are left in the composer, "
                "unpublished -- whether LinkedIn keeps them as a draft is unmeasured."
            )
            return out
    out["proceed"] = True
    out["why"] = "the composer holds exactly his words and Post is on"
    return out


async def wait_for_composer(page: Any) -> dict[str, Any]:
    """A BOUNDED WAIT for the composer the trigger opens to be drawn -- a live
    modal opens after an animation. DECIDES NOTHING: ``opened_gate`` decides
    on the reading taken after it. Reads only."""
    polls = 0
    reading = await read_composer(page)
    for polls in range(1, POLLS + 1):
        if reading.get("modals") == 1 and reading.get("editors") == 1:
            break
        await page.wait_for_timeout(POLL_MS)
        reading = await read_composer(page)
    return {"polls": polls, "drawn": reading.get("modals") == 1 and reading.get("editors") == 1}


async def wait_for_post_enabled(page: Any) -> dict[str, Any]:
    """A BOUNDED WAIT for Post to turn on once his words are in -- the reply
    path measured that lag live (session 5). DECIDES NOTHING: ``post_gate``
    decides on the reading taken after it. Reads only."""
    polls = 0
    reading = await read_composer(page)
    for polls in range(1, POLLS + 1):
        if reading.get("post_enabled") is True:
            break
        await page.wait_for_timeout(POLL_MS)
        reading = await read_composer(page)
    return {"polls": polls, "enabled": reading.get("post_enabled") is True}


async def read_after_post(page: Any) -> dict[str, Any]:
    """What the Post press left, IN PLACE, counted: the composer still open or
    gone, and any dialog drawn. Nothing is pressed and nothing is claimed."""
    out: dict[str, Any] = {"modals": 0, "dialogs": 0, "editors": 0, "error": None}
    try:
        out["modals"] = await _count(page, MODAL)
        out["dialogs"] = await _count(page, '[role="dialog"], [role="alertdialog"]')
        out["editors"] = await _count(page, EDITOR)
    except Exception as exc:  # noqa: BLE001
        out["error"] = type(exc).__name__
    return out
