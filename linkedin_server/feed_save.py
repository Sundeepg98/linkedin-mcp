"""Saving ONE feed item he names to his Saved items, from that item's own control menu on its permalink (census ``M C36``; ``M C37`` rides it).

THE BUILD'S READING HALF -- selectors, locator COUNT readers and pure
verdicts -- the split ``feed_curation`` and ``group_leave`` set: ``writes.py``
holds the spec and the arms that call in here; this module presses nothing,
navigates nowhere and returns no page text.

## THE RULINGS IT IS BUILT UNDER

* ``SAVE-POST-UNDER-OWN-CURATION`` (the orchestrator, 2026-11-27 12:35 IST;
  registration owed at integration 7): "Build linkedin_save_post(item) behind
  the grant, in mark_not_interested's shape, under HIS-OWN-CURATION-NOT-OUTWARD."
  "The item is the caller's named target, never one supplied by the page."
* ``HIS-OWN-CURATION-NOT-OUTWARD``: saving an item is curation of his own items,
  not an outward act -- built behind the grant and proven with its inverse in
  the same session, read back.
* ``PAGE-MAY-VETO-NEVER-SUPPLY``: the item is the one whose urn HE names, and
  the only address loaded is that item's own permalink, composed from the urn.
  The page may only refuse, never supply.
* ``PEOPLE-DATA-MITIGATIONS``: the item's author is never read. The trigger's
  accessible name carries the author's name after LinkedIn's fixed prefix,
  and the selector names the PREFIX only.
* ``SAVE-RECEIPT-NEEDS-A-CHANGE`` (the orchestrator, 2026-11-27 17:20 IST, on
  the cold verification of 5beac57; registration owed at integration 7): "Read
  the live-region state BEFORE the press. After the press, require a NEW or
  CHANGED 'saved' region, or the item's own menu state flipping to Unsave,
  before reporting performed: true. Otherwise report the outcome in closed
  words (unverified or not_landed). Never claim performed."

## WHAT IS MEASURED, AND WHERE

The TRIGGER and the PORTAL the pressed trigger owns are ``feed_curation``'s,
IMPORTED, never re-written: measured on live session 11's permalink of a
member's post (load 29), pressed there live. ``Save`` is the FIRST of the open
menu's seven ``role=menuitem`` items on every permalink menu captured --
session 11's member post (``tests/fixtures/live11/permalink_member_post_menu_open.html``)
and session 12's member and Page posts (``tests/fixtures/live12/
permalink_member_post_menu-open.html``, ``permalink_page_post_menu-open.html``;
lane msg7's record, section 4) -- a ``div`` whose whole text is LinkedIn's word
``Save``, on the harness's closed word list, so verbatim in every tracked copy.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **Whether the item is already saved.** The closed permalink draws no save
  state; only the open menu could, and every captured menu was an unsaved
  item's. So the act refuses unless the menu the pressed trigger owns draws
  exactly one visible ``Save``: an already-saved item's menu -- expected to
  draw ``Unsave`` in its place (DERIVED, never captured) -- presses nothing
  beyond the trigger.
* **What pressing ``Save`` draws.** No capture holds it. DERIVED: a
  confirmation in a live region whose words include ``saved``
  (:data:`SAVED_WORD`), or the item's own menu drawing ``Unsave`` where it drew
  ``Save``; neither has been seen. The verification is IN PLACE, on the page
  the press was made on, and it reads a CHANGE, never a presence
  (SAVE-RECEIPT-NEEDS-A-CHANGE): the gate's reading, taken just before the
  ``Save`` press, is the baseline. Saved only when more visible live regions
  carry the word than the gate counted, or when the owned menu now draws
  ``Unsave`` where it drew ``Save``. A region already on the page before the
  press counts for nothing: until 2026-11-27 it read saved, and an unlanded
  save could report ``performed: true``. The owned menu still open with its
  ``Save`` and nothing changed is ``not_landed``; anything else is
  ``unverified`` -- never "not saved". The first supervised press records
  what was drawn, by counts.
* **The inverse** (``M C37``, unsaving): ``Unsave`` is drawn only after a save,
  in no capture, so it is not built. SAVE-POST-UNDER-OWN-CURATION names the
  capture: "save, read the drawn Unsave, unsave", riding this act's first live
  fire in session 14, on a post he names, attended.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from linkedin_server import coerce, feed_curation

ACTION = "save_post"
ACTIONS: tuple[str, ...] = (ACTION,)

#: The permalink: the urn HE names, composed into its own address --
#: ``feed_curation``'s, the same page that act presses on.
URL_TEMPLATE = feed_curation.URL_TEMPLATE

#: The item's own menu entry, LinkedIn's whole word, on the harness's closed
#: word list and verbatim on every captured permalink menu.
SAVE = "Save"

#: DERIVED, NEVER CAPTURED: the word a save's confirmation is expected to
#: carry. A reading, never an aim: nothing here presses it.
SAVED_WORD = re.compile(r"\bsaved\b", re.IGNORECASE)

#: DERIVED, NEVER CAPTURED: the word a saved item's own menu is expected to draw
#: in ``Save``'s place. A reading, never an aim: nothing here presses it.
UNSAVE = "Unsave"

#: THE CLOSED WORDS the verification's sentence opens with
#: (SAVE-RECEIPT-NEEDS-A-CHANGE). ``saved``: a change this press made.
#: ``not_landed``: the press was made and the menu still draws its ``Save``,
#: with nothing changed. ``not_pressed``: the gate refused, so nothing past the
#: trigger was pressed. ``unverified``: anything else.
SAVED_BY_THE_PRESS = "saved"
NOT_LANDED = "not_landed"
NOT_PRESSED = "not_pressed"
UNVERIFIED = "unverified"
OUTCOMES: tuple[str, ...] = (SAVED_BY_THE_PRESS, NOT_LANDED, NOT_PRESSED, UNVERIFIED)

#: The states this module knows. ``UNKNOWN`` is ``writes.UNKNOWN``'s spelling,
#: and ``SHOWN`` is ``feed_curation``'s: the closed item the act starts from.
SHOWN = feed_curation.SHOWN
SAVED = "item_saved"
UNKNOWN = feed_curation.UNKNOWN

#: THE TRIGGER, the first press, pressed strictly: ``feed_curation``'s.
TRIGGER = feed_curation.TRIGGER
TRIGGER_VISIBLE = feed_curation.TRIGGER_VISIBLE
OPEN_TRIGGERS = feed_curation.OPEN_TRIGGERS

#: The ``Save`` item IN THE MENU THE PRESSED TRIGGER OWNS: the click selector
#: for the second press, appended only by :func:`menu_item_gate`.
ITEM_IN_OWNED_MENU = (
    f"xpath={feed_curation._OWNED_PORTAL}//*[@role='menu']//*[@role='menuitem']"
    f"[normalize-space(.)='{SAVE}']"
)
ITEM_IN_OWNED_MENU_VISIBLE = ITEM_IN_OWNED_MENU + " >> visible=true"
#: ``Unsave`` IN THE SAME OWNED MENU: the flip a press could draw, read and
#: never pressed. Whole word, so ``Save`` and ``Unsave`` never count as each
#: other.
UNSAVE_IN_OWNED_MENU = (
    f"xpath={feed_curation._OWNED_PORTAL}//*[@role='menu']//*[@role='menuitem']"
    f"[normalize-space(.)='{UNSAVE}']"
)
UNSAVE_IN_OWNED_MENU_VISIBLE = UNSAVE_IN_OWNED_MENU + " >> visible=true"
#: The same item anywhere on the page, visible: the denominator.
ITEMS_VISIBLE = f'role=menuitem[name="{SAVE}"s] >> visible=true'
#: The live regions a confirmation could be drawn in.
LIVE_REGIONS = (
    ':is([role="alert"], [role="status"], [aria-live="polite"], '
    '[aria-live="assertive"]) >> visible=true'
)
DIALOGS = feed_curation.DIALOGS

#: The menu is POLLED briefly: a menu still opening reads as absent.
MENU_POLLS: int = 8
MENU_POLL_MS: int = 250

_KEYS = (
    "triggers", "triggers_visible", "triggers_expanded", "items_visible",
    "items_in_owned_menu", "unsave_in_owned_menu", "saved_regions", "dialogs",
)


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def read_item(page: Any) -> dict[str, Any]:
    """COUNTS ONLY, off the permalink already open. Never raises.

    ``error`` is an exception TYPE name, never its message.
    """
    out: dict[str, Any] = {key: 0 for key in _KEYS}
    out["error"] = None
    try:
        out["triggers"] = await _count(page, TRIGGER)
        out["triggers_visible"] = await _count(page, TRIGGER_VISIBLE)
        out["triggers_expanded"] = await _count(page, OPEN_TRIGGERS)
        out["items_visible"] = await _count(page, ITEMS_VISIBLE)
        out["items_in_owned_menu"] = await _count(page, ITEM_IN_OWNED_MENU_VISIBLE)
        out["unsave_in_owned_menu"] = await _count(page, UNSAVE_IN_OWNED_MENU_VISIBLE)
        out["saved_regions"] = coerce.as_count(
            await page.locator(LIVE_REGIONS).filter(has_text=SAVED_WORD).count()
        )
        out["dialogs"] = await _count(page, DIALOGS)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _error_kind(value: Any) -> str:
    return feed_curation._error_kind(value)


def _facts(reading: dict[str, Any]) -> dict[str, Any]:
    reading = reading if isinstance(reading, dict) else {}
    facts = {key: coerce.as_count(reading.get(key)) for key in _KEYS}
    facts["author_read"] = False
    return facts


def item_verdict(
    reading: dict[str, Any], *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading of the CLOSED item. PURE.

    ``item_shown``: exactly one control-menu trigger in the page's main,
    visible, none of it expanded -- ``feed_curation``'s reading, by the same
    keys. Whether the item is already saved is NOT readable closed: the gate
    after the trigger press decides that.
    """
    _their_facts, state, why = feed_curation.item_verdict(
        reading, landed_elsewhere=landed_elsewhere
    )
    return _facts(reading), state, why


async def read_state(page: Any, *, landed_elsewhere: bool = False) -> tuple[dict[str, Any], str, str]:
    return item_verdict(await read_item(page), landed_elsewhere=landed_elsewhere)


def menu_verdict(reading: dict[str, Any]) -> dict[str, Any]:
    """Whether the SECOND press -- ``Save`` -- may be queued. PURE.

    Exactly one trigger reads expanded, exactly one visible ``Save`` item is on
    the page, and it is inside the menu that trigger owns. Anything else -- an
    already-saved item's menu, say -- queues NOTHING; the trigger press stays
    the only press.
    """
    facts = _facts(reading)
    error = (_error_kind(reading.get("error"))
             if isinstance(reading, dict) and reading.get("error") else None)

    def refuse(condition: str, why: str) -> dict[str, Any]:
        return {"proceed": False, "selector": "", "refused_condition": condition,
                "why": why + " NOTHING further was pressed: the menu's trigger is the "
                "only press this call made.", "observed": facts}

    if error:
        return refuse("unreadable", f"the menu could not be read after the press ({error}).")
    if facts["triggers_expanded"] != 1:
        return refuse("menu_not_open",
                      f"{facts['triggers_expanded']} control-menu trigger(s) read open "
                      "after the press, where exactly one is required.")
    if facts["items_visible"] != 1:
        return refuse("item_not_unique",
                      f"{facts['items_visible']} visible {SAVE!r} item(s) are on the page, "
                      "where exactly one is required. An item already saved draws no "
                      f"{SAVE!r} in its menu, so this is also how that state refuses.")
    if facts["items_in_owned_menu"] != 1:
        return refuse("item_outside_the_owned_menu",
                      f"the one visible {SAVE!r} item is not inside the menu the pressed "
                      "trigger owns by id, so it is not provably this item's.")
    return {"proceed": True, "selector": ITEM_IN_OWNED_MENU, "refused_condition": None,
            "why": (f"exactly one visible {SAVE!r} item is on the page and it is inside "
                    "the menu the pressed trigger owns, by the portal id its anchor "
                    "names."),
            "observed": facts}


async def menu_item_gate(page: Any) -> dict[str, Any]:
    """Read the menu after the trigger press, briefly polled, and decide."""
    reading = await read_item(page)
    polls = 1
    while (
        polls < MENU_POLLS
        and not reading.get("error")
        and coerce.as_count(reading.get("items_in_owned_menu")) == 0
        and coerce.as_count(reading.get("items_visible")) <= 1
    ):
        await page.wait_for_timeout(MENU_POLL_MS)
        reading = await read_item(page)
        polls += 1
    verdict = menu_verdict(reading)
    verdict["polls"] = polls
    return verdict


def after_press_note(
    reading: dict[str, Any], *, before: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """What the ``Save`` press left, as the receipt prints it, beside the count
    the gate took just before the press (``before``), so a region that was
    already there is never read as one the press drew."""
    facts = _facts(reading)
    prior = (f"{_facts(before)['saved_regions']} just before the press"
             if isinstance(before, dict) else "none counted before the press")
    error = (_error_kind(reading.get("error"))
             if isinstance(reading, dict) and reading.get("error") else None)
    if error:
        sentence = (f"the page could not be read after the {SAVE!r} press ({error}), so "
                    "what it drew is not known.")
    elif facts["dialogs"]:
        sentence = (f"A FURTHER STEP OPENED AND WAS NOT TAKEN: {facts['dialogs']} visible "
                    f"dialog(s) after {SAVE!r} was pressed, and nothing in them was "
                    "pressed.")
    else:
        sentence = (f"no dialog was visible after {SAVE!r} was pressed; "
                    f"{facts['saved_regions']} visible live region(s) carried the DERIVED "
                    f"word 'saved' ({prior}), {facts['unsave_in_owned_menu']} visible "
                    f"{UNSAVE!r} item(s) are in the owned menu, and the trigger is drawn "
                    f"{facts['triggers']} time(s).")
    return {**facts, "error": error, "what_this_means": sentence}


def verification_verdict(
    reading: dict[str, Any],
    *,
    before: Optional[dict[str, Any]] = None,
    pressed: bool = True,
) -> tuple[dict[str, Any], str, str]:
    """IN PLACE, on the page the press was made on, read as a CHANGE. PURE.

    SAVE-RECEIPT-NEEDS-A-CHANGE. ``before`` is the reading the gate took just
    before the ``Save`` press. ``pressed`` says whether the gate let that press
    through at all. Every sentence opens with one of :data:`OUTCOMES`.

    * ``item_saved`` ONLY on a change this press can explain: more visible
      live regions carry the DERIVED word than ``before`` counted (a new region,
      or one whose words changed to carry it), or the item's own menu draws
      ``Unsave`` where, before the press, it drew ``Save``.
    * ``item_shown``, ``not_pressed``: the gate refused, so nothing was pressed
      past the trigger and this call saved nothing.
    * ``item_shown``, ``not_landed``: the owned menu is still open with its
      ``Save`` visible and nothing changed.
    * ``unknown``, ``unverified``: everything else, never "not saved". That
      includes a reading with no ``before``, which can show no change, and a
      new region while the menu still draws ``Save`` unpressed.
    """
    facts = _facts(reading)
    if not pressed:
        return (facts, SHOWN,
                f"{NOT_PRESSED}: the gate refused the {SAVE!r} item, so nothing past the "
                "item's menu trigger was pressed and this call saved nothing. It says "
                "nothing about whether the item was saved before this call.")
    if isinstance(reading, dict) and reading.get("error"):
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: the page could not be read after the press "
                f"({_error_kind(reading.get('error'))}).")
    still_open = facts["items_in_owned_menu"] == 1 and facts["triggers_expanded"] == 1
    if not isinstance(before, dict):
        if still_open:
            return (facts, SHOWN,
                    f"{NOT_LANDED}: the item's menu is still open with its {SAVE!r} item "
                    "visible, so the press did not land and this call saved nothing. No "
                    "reading was taken just before the press.")
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: no reading was taken just before the press, so nothing "
                "on the page can be shown to be a change this press made. Open your "
                "Saved items and look; do not retry.")
    prior = _facts(before)
    new_regions = facts["saved_regions"] - prior["saved_regions"]
    flipped = (
        prior["items_in_owned_menu"] == 1 and prior["unsave_in_owned_menu"] == 0
        and facts["unsave_in_owned_menu"] == 1 and facts["items_in_owned_menu"] == 0
    )
    counts = (f"{prior['saved_regions']} visible live region(s) carried the word 'saved' "
              f"just before the press and {facts['saved_regions']} after it")
    if still_open and new_regions <= 0:
        return (facts, SHOWN,
                f"{NOT_LANDED}: the item's menu is still open with its {SAVE!r} item "
                f"visible and nothing changed ({counts}), so the press did not land and "
                "this call saved nothing.")
    if still_open:
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: {counts}, but the item's menu still draws its {SAVE!r} "
                "unpressed. The two readings disagree, so neither is taken. Open your "
                "Saved items and look; do not retry.")
    if new_regions > 0:
        return (facts, SAVED,
                f"{SAVED_BY_THE_PRESS}: {counts}. The word is DERIVED, never captured: "
                "this is its first reading.")
    if flipped:
        return (facts, SAVED,
                f"{SAVED_BY_THE_PRESS}: the item's own menu draws {UNSAVE!r} where, just "
                f"before the press, it drew {SAVE!r}. That word is DERIVED, never "
                "captured: this is its first reading.")
    return (facts, UNKNOWN,
            f"{UNVERIFIED}: no live region carrying 'saved' was added ({counts}) and the "
            f"item's menu draws no {UNSAVE!r} in its {SAVE!r}'s place. The press may have "
            "landed with LinkedIn drawing something this server has never seen, or not "
            "at all. Open your Saved items and look; do not retry.")
