"""Marking ONE feed item he names "Not interested", from that item's own control menu on its permalink (census ``N 154``; ``N 153`` rides it).

THE BUILD'S READING HALF -- selectors, locator COUNT readers and pure
verdicts -- the split ``group_leave`` set: ``writes.py`` holds the spec and the
arms that call in here; this module presses nothing, navigates nowhere and
returns no page text.

## THE RULINGS IT IS BUILT UNDER

* ``HIS-OWN-CURATION-NOT-OUTWARD``: hiding an item from his own feed is
  curation of his own feed, not an outward act -- built behind the grant and
  proven with its inverse in the same session, read back; and "an undo drawn
  only once proves the act only through that undo".
* ``PAGE-MAY-VETO-NEVER-SUPPLY``: the item is the one whose urn HE names, and
  the only address loaded is that item's own permalink, composed from the urn
  -- the aim lane B2 found missing on ``/feed/``, where no item carries its
  urn until its menu opens. The page may only refuse (no one control menu, no
  one ``Not interested`` item in the menu that control owns), never supply.
* ``PEOPLE-DATA-MITIGATIONS``: the item's author is never read. The control's
  accessible name carries the author's name after LinkedIn's fixed prefix, and
  the selector names the PREFIX only; nothing here returns a label.
* ``FEED-CURATION-RECEIPT-NEEDS-A-CHANGE`` (the orchestrator, 2026-11-27 17:50
  IST, on lane msg7's finding beside its SAVE-RECEIPT-NEEDS-A-CHANGE): "Read
  the relevant state just before the press: the Undo count, and the item's own
  drawn state. After the press, report item_hidden ONLY on a change the press
  made: a NEW Undo beside THAT item, or the item replaced by its hidden-state
  card. Otherwise report not_landed or unverified, in closed words."

## WHAT IS MEASURED, AND WHERE

Live session 11, load 29 -- a member's post's permalink, opened by the urn the
feed item's own menu carried, its control menu pressed and read, nothing in
it pressed (``tests/fixtures/live11/permalink_member_post.html`` closed,
``permalink_member_post_menu_open.html`` open; the menu's words put back by
keyed shape in ``tests/fixtures/synthetic/live11_permalink_menu_words.html``,
``scripts/_build_live11_net2_word_skeletons.py``):

* THE TRIGGER: the live runner pressed ``main button[aria-label^="Open
  control menu"]`` on that page, found as the ONE visible match, and the menu
  opened. Closed, the button declares no ``aria-expanded``; pressed, it reads
  ``aria-expanded="true"`` and a sibling ``[data-menu-portal-anchor]`` holds an
  element whose ``aria-owns`` is the id of the PORTAL the menu draws in, at the
  end of the document. Its label's keyed shape is 36 letters in 43 characters,
  consistent with LinkedIn's "Open control menu for post by " and a name.
* THE MENU: one ``role=menu`` in that portal, seven ``role=menuitem`` items --
  ``Save``, ``Copy link to post``, ``Embed this post``, one of 23 letters,
  ``Not interested`` (a ``div``), one of 15 letters, ``Report post``.

WHERE THE MENU IS OWNED BY THE PRESSED CONTROL, BY ID: the item is pressed only
inside the portal whose id the pressed trigger's own anchor names -- the
relation the page draws, not a position.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **What pressing ``Not interested`` draws.** No capture holds it. The undo
  LinkedIn is expected to draw in the item's place -- the only proof the ruling
  accepts -- is DERIVED here as a control whose whole word is ``Undo``
  (:data:`UNDO_WORDS`), never seen. The verification is IN PLACE, on the page
  the press was made on, because the undo is drawn once, and it reads a
  CHANGE, never a presence (FEED-CURATION-RECEIPT-NEEDS-A-CHANGE): the gate's
  reading, taken just before the ``Not interested`` press, is the baseline.
  Hidden only when the page's main -- where the permalink draws its one item --
  draws more undo controls than the gate counted there: a new undo beside that
  item. The hidden-state card the item may be replaced by is known only by
  that undo, so the item's trigger vanishing is never read as hidden on its
  own: a navigation or an error page removes it too. An undo already on the
  page before the press counts for nothing; until 2026-11-27 any visible undo
  read hidden, and an unlanded mark could report ``performed: true``. The menu
  still open with its item and nothing changed is ``not_landed``; anything else
  is ``unverified`` -- never "not done". The first supervised press records
  what was drawn, by counts.
* **The inverse.** Pressing that undo is the round trip; it is not built,
  because no capture draws it. Until then, the undo is his, by hand, while it is
  drawn.
* **Another kind of item** (``N 153``, a network update): whether its menu
  draws the same entry is read at its first fire; anything else refuses.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce

ACTION = "mark_not_interested"
ACTIONS: tuple[str, ...] = (ACTION,)

#: The permalink: the urn HE names, composed into its own address.
URL_TEMPLATE = "https://www.linkedin.com/feed/update/{target}/"

#: LinkedIn's fixed prefix on an item's control-menu trigger, the aim the live
#: runner pressed on session 11's permalink. The rest of the label is a name
#: and is never read.
TRIGGER_PREFIX = "Open control menu"

#: The item's own menu entry, LinkedIn's whole word, verified by keyed shape.
NOT_INTERESTED = "Not interested"

#: DERIVED, NEVER CAPTURED: the word of the undo LinkedIn draws in an item's
#: place after it is hidden. A reading, never an aim: nothing here presses it.
UNDO_WORDS: tuple[str, ...] = ("Undo",)

#: The states this module knows. ``UNKNOWN`` is ``writes.UNKNOWN``'s spelling.
SHOWN = "item_shown"
HIDDEN = "item_hidden"
UNKNOWN = "unknown"

#: THE CLOSED WORDS the verification's sentence opens with
#: (FEED-CURATION-RECEIPT-NEEDS-A-CHANGE), the four ``feed_save.OUTCOMES``
#: has. ``hidden``: a change this press made. ``not_landed``: the press was
#: made and the menu still draws its ``Not interested``, with nothing changed.
#: ``not_pressed``: the gate refused, so nothing past the trigger was pressed.
#: ``unverified``: anything else.
HIDDEN_BY_THE_PRESS = "hidden"
NOT_LANDED = "not_landed"
NOT_PRESSED = "not_pressed"
UNVERIFIED = "unverified"
OUTCOMES: tuple[str, ...] = (HIDDEN_BY_THE_PRESS, NOT_LANDED, NOT_PRESSED, UNVERIFIED)

#: THE TRIGGER, as a CSS selector: the click selector for the first press, which
#: the verdict requires to match exactly one element (pressed strictly).
TRIGGER = f'main button[aria-label^="{TRIGGER_PREFIX}"]'
TRIGGER_VISIBLE = TRIGGER + " >> visible=true"

_OPEN_TRIGGER = (
    f"//main//button[starts-with(@aria-label, '{TRIGGER_PREFIX}')][@aria-expanded='true']"
)
#: The portal the PRESSED trigger owns: the element whose id the trigger's own
#: sibling anchor names in ``aria-owns``. XPath 1.0 compares the id with each
#: ``aria-owns`` value, so a portal no pressed trigger owns is never matched.
_OWNED_PORTAL = (
    "//*[@data-floating-ui-portal]"
    f"[@id = {_OPEN_TRIGGER}/following-sibling::*[@data-menu-portal-anchor]//@aria-owns]"
)
#: The ``Not interested`` item IN THE MENU THE PRESSED TRIGGER OWNS: the click
#: selector for the second press, appended only by :func:`menu_item_gate`.
ITEM_IN_OWNED_MENU = (
    f"xpath={_OWNED_PORTAL}//*[@role='menu']//*[@role='menuitem']"
    f"[normalize-space(.)='{NOT_INTERESTED}']"
)
ITEM_IN_OWNED_MENU_VISIBLE = ITEM_IN_OWNED_MENU + " >> visible=true"
#: The same item anywhere on the page, visible: the denominator.
ITEMS_VISIBLE = f'role=menuitem[name="{NOT_INTERESTED}"s] >> visible=true'
OPEN_TRIGGERS = "xpath=" + _OPEN_TRIGGER
DIALOGS = ":is([role=dialog], [role=alertdialog]) >> visible=true"


def _undo_selector(word: str) -> str:
    return f':is(button, a, [role=button]):text-is("{word}") >> visible=true'


def _undo_in_main_selector(word: str) -> str:
    """The same undo, inside the page's main: on the permalink that is where
    the one item is drawn, and where its undo is DERIVED to be drawn -- beside
    THAT item, not in a toast or another region of the page."""
    return f'main :is(button, a, [role=button]):text-is("{word}") >> visible=true'


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def read_item(page: Any) -> dict[str, Any]:
    """COUNTS ONLY, off the permalink already open. Never raises.

    ``error`` is an exception TYPE name, never its message.
    """
    out: dict[str, Any] = {
        "triggers": 0,
        "triggers_visible": 0,
        "triggers_expanded": 0,
        "items_visible": 0,
        "items_in_owned_menu": 0,
        "undo_controls": 0,
        "undo_in_main": 0,
        "dialogs": 0,
        "error": None,
    }
    try:
        out["triggers"] = await _count(page, TRIGGER)
        out["triggers_visible"] = await _count(page, TRIGGER_VISIBLE)
        out["triggers_expanded"] = await _count(page, OPEN_TRIGGERS)
        out["items_visible"] = await _count(page, ITEMS_VISIBLE)
        out["items_in_owned_menu"] = await _count(page, ITEM_IN_OWNED_MENU_VISIBLE)
        undo = undo_in_main = 0
        for word in UNDO_WORDS:
            undo += await _count(page, _undo_selector(word))
            undo_in_main += await _count(page, _undo_in_main_selector(word))
        out["undo_controls"] = undo
        out["undo_in_main"] = undo_in_main
        out["dialogs"] = await _count(page, DIALOGS)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _error_kind(value: Any) -> str:
    text = str(value or "")
    if text and len(text) <= 64 and (text[0].isalpha() or text[0] == "_") and all(
        character.isascii() and (character.isalnum() or character == "_")
        for character in text
    ):
        return text
    return "an exception"


def _facts(reading: dict[str, Any]) -> dict[str, Any]:
    reading = reading if isinstance(reading, dict) else {}
    facts = {
        key: coerce.as_count(reading.get(key))
        for key in (
            "triggers", "triggers_visible", "triggers_expanded", "items_visible",
            "items_in_owned_menu", "undo_controls", "undo_in_main", "dialogs",
        )
    }
    facts["author_read"] = False
    return facts


def item_verdict(
    reading: dict[str, Any], *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading of the CLOSED item. PURE.

    ``item_shown``: exactly one control-menu trigger in the page's main, visible,
    none of it expanded. Anything else is ``unknown`` and the why says which,
    in counts -- never the author.
    """
    reading = reading if isinstance(reading, dict) else {}
    facts = _facts(reading)
    if landed_elsewhere:
        return (facts, UNKNOWN,
                "the browser did not land on the permalink of the item you named, "
                "so its control is not that item's. THE LANDING IS WITHHELD rather "
                "than named.")
    if reading.get("error"):
        return (facts, UNKNOWN,
                f"the permalink could not be read ({_error_kind(reading.get('error'))} "
                "was raised inside the reader; its message is not repeated here).")
    triggers, visible = facts["triggers"], facts["triggers_visible"]
    if triggers != 1 or visible != 1:
        return (facts, UNKNOWN,
                f"the permalink draws {triggers} control-menu trigger(s) in its main "
                f"({visible} visible), where exactly one is required: more than one "
                "would be choosing by position, and none is an item not drawn.")
    if facts["triggers_expanded"]:
        return (facts, UNKNOWN,
                "the item's control menu already reads open, so its state before "
                "any press is not the closed one this act starts from.")
    return (facts, SHOWN,
            "the permalink of the item you named draws exactly one control-menu "
            "trigger, visible and closed -- the item's own menu, found by "
            "LinkedIn's fixed prefix; the author it names is not read.")


async def read_state(page: Any, *, landed_elsewhere: bool = False) -> tuple[dict[str, Any], str, str]:
    return item_verdict(await read_item(page), landed_elsewhere=landed_elsewhere)


#: The menu is POLLED briefly: a menu still opening reads as absent.
MENU_POLLS: int = 8
MENU_POLL_MS: int = 250


def menu_verdict(reading: dict[str, Any]) -> dict[str, Any]:
    """Whether the SECOND press -- ``Not interested`` -- may be queued. PURE.

    Exactly one trigger reads expanded, exactly one visible ``Not interested``
    item is on the page, and it is inside the menu that trigger owns. Anything
    else queues NOTHING; the trigger press stays the only press.
    """
    facts = _facts(reading)
    error = _error_kind(reading.get("error")) if isinstance(reading, dict) and reading.get("error") else None

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
                      f"{facts['items_visible']} visible {NOT_INTERESTED!r} item(s) are on "
                      "the page, where exactly one is required.")
    if facts["items_in_owned_menu"] != 1:
        return refuse("item_outside_the_owned_menu",
                      f"the one visible {NOT_INTERESTED!r} item is not inside the menu the "
                      "pressed trigger owns by id, so it is not provably this item's.")
    return {"proceed": True, "selector": ITEM_IN_OWNED_MENU, "refused_condition": None,
            "why": (f"exactly one visible {NOT_INTERESTED!r} item is on the page and it is "
                    "inside the menu the pressed trigger owns, by the portal id its anchor "
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
    """What the ``Not interested`` press left, as the receipt prints it, beside
    the counts the gate took just before the press (``before``), so an undo
    that was already there is never read as one the press drew."""
    facts = _facts(reading)
    prior = (f"{_facts(before)['undo_in_main']} in the page's main just before the press"
             if isinstance(before, dict) else "none counted before the press")
    error = _error_kind(reading.get("error")) if isinstance(reading, dict) and reading.get("error") else None
    if error:
        sentence = (f"the page could not be read after the {NOT_INTERESTED!r} press "
                    f"({error}), so what it drew is not known.")
    elif facts["dialogs"]:
        sentence = (f"A FURTHER STEP OPENED AND WAS NOT TAKEN: {facts['dialogs']} visible "
                    f"dialog(s) after {NOT_INTERESTED!r} was pressed, and nothing in them was "
                    "pressed.")
    else:
        sentence = (f"no dialog was visible after {NOT_INTERESTED!r} was pressed; "
                    f"{facts['undo_controls']} control(s) whose whole word is on the DERIVED "
                    f"undo list are on the page, {facts['undo_in_main']} of them in the "
                    f"page's main beside the item ({prior}), and the trigger is drawn "
                    f"{facts['triggers']} time(s).")
    return {**facts, "error": error, "what_this_means": sentence}


def verification_verdict(
    reading: dict[str, Any],
    *,
    before: Optional[dict[str, Any]] = None,
    pressed: bool = True,
) -> tuple[dict[str, Any], str, str]:
    """IN PLACE, on the page the press was made on, read as a CHANGE. PURE.

    FEED-CURATION-RECEIPT-NEEDS-A-CHANGE, ``feed_save.verification_verdict``'s
    shape. ``before`` is the reading the gate took just before the
    ``Not interested`` press; ``pressed`` says whether the gate let that press
    through at all. Every sentence opens with one of :data:`OUTCOMES`.

    * ``item_hidden`` ONLY on a change this press can explain: the page's main,
      where the permalink draws its one item, draws more undo controls than
      ``before`` counted there -- a new undo beside THAT item, whether the
      item's trigger is still drawn or the item was replaced by its
      hidden-state card. An undo elsewhere on the page is not beside the item.
    * ``item_shown``, ``not_pressed``: the gate refused, so nothing was pressed
      past the trigger and this call marked nothing.
    * ``item_shown``, ``not_landed``: the owned menu is still open with its
      ``Not interested`` visible and no new undo beside the item.
    * ``unknown``, ``unverified``: everything else, never "not done". That
      includes a reading with no ``before``, which can show no change; a new
      undo while the menu still draws its item unpressed; a new undo outside
      the page's main; and the item's trigger gone with no new undo.
    """
    facts = _facts(reading)
    if not pressed:
        return (facts, SHOWN,
                f"{NOT_PRESSED}: the gate refused the {NOT_INTERESTED!r} item, so nothing "
                "past the item's menu trigger was pressed and this call marked nothing. It "
                "says nothing about whether the item was marked before this call.")
    if isinstance(reading, dict) and reading.get("error"):
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: the page could not be read after the press "
                f"({_error_kind(reading.get('error'))}).")
    still_open = facts["items_in_owned_menu"] == 1 and facts["triggers_expanded"] == 1
    if not isinstance(before, dict):
        if still_open:
            return (facts, SHOWN,
                    f"{NOT_LANDED}: the item's menu is still open with its {NOT_INTERESTED!r} "
                    "item visible, so the press did not land and this call marked nothing. "
                    "No reading was taken just before the press.")
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: no reading was taken just before the press, so nothing on "
                "the page can be shown to be a change this press made. Open your feed and "
                "look; do not retry.")
    prior = _facts(before)
    new_beside = facts["undo_in_main"] - prior["undo_in_main"]
    new_elsewhere = (
        (facts["undo_controls"] - facts["undo_in_main"])
        - (prior["undo_controls"] - prior["undo_in_main"])
    )
    counts = (f"{prior['undo_in_main']} control(s) whose whole word is 'Undo' were drawn "
              "in the page's main, beside the item, just before the press and "
              f"{facts['undo_in_main']} after it")
    if still_open and new_beside <= 0:
        return (facts, SHOWN,
                f"{NOT_LANDED}: the item's menu is still open with its {NOT_INTERESTED!r} "
                f"item visible and nothing changed beside it ({counts}), so the press did "
                "not land and this call marked nothing.")
    if still_open:
        return (facts, UNKNOWN,
                f"{UNVERIFIED}: {counts}, but the item's menu still draws its "
                f"{NOT_INTERESTED!r} unpressed. The two readings disagree, so neither is "
                "taken. Open your feed and look; do not retry.")
    if new_beside > 0:
        return (facts, HIDDEN,
                f"{HIDDEN_BY_THE_PRESS}: {counts} -- a new undo where the item is, the undo "
                "LinkedIn draws in a hidden item's place. That word is DERIVED, never "
                "captured: this is its first reading.")
    elsewhere = (f" {new_elsewhere} new undo control(s) were drawn elsewhere on the page, "
                 "outside its main, which is not beside the item."
                 if new_elsewhere > 0 else "")
    return (facts, UNKNOWN,
            f"{UNVERIFIED}: no new undo was drawn beside the item ({counts}), and the "
            f"menu is not open with its item unpressed.{elsewhere} The press may have "
            "landed with LinkedIn drawing something this server has never seen, or not "
            "at all. Open your feed and look; do not retry.")
