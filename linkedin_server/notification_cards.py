"""Notification cards on LinkedIn's SERVER-DRIVEN ``/notifications/`` page, read for ``linkedin_notifications`` (census ``M C75``, ``N 20``, ``N 45``).

THE PAGE CHANGED UNDER THE SHIPPED READER. Sessions 2 to 5 drew the page as
9 or 10 ``article.nt-card`` cards, which ``dom.NOTIFICATION_SELECTORS`` reads.
Live session 12 (load 38, ``tests/fixtures/live12/notifications.html``) drew it
as ONE server-driven screen (``[data-sdui-screen]``, generated classes,
``componentkey`` attributes) with no ``article`` at all. Run offline through
the shipped path, the old selectors harvest 0 records there: four match
nothing, and ``main ul li`` matches 12 avatar figures that carry no text (lane
msg7, ``_audit/2026-11-27-msg7.md`` section 7). The orchestrator's ruling
CAPTURE-SHOWS-READER-BLIND-DEMOTES (2026-11-27, registration owed at
integration 7) made this read this lane's, red first on that capture, with
session 5's 9 of 9 kept as a control that must stay green.

WHAT A CARD IS, MEASURED on session 12's keyed skeleton (structure only, no
class): every card ends, after an ``hr``, in ONE full-card link -- an ``a``
whose ``aria-labelledby`` names an element INSIDE that same link, which holds
the card's sentence. 10 of 10 cards draw one. Beside the card's time sits its
menu trigger, the card's ONE ``button`` declaring ``aria-expanded`` (its
accessible name LinkedIn's fixed ``More options`` by keyed shape, equal on all
ten, and never read); the time is the first paragraph in that trigger's own
parent.

WHAT THIS READS, and the shape it returns: ``dom.harvest_block_cards``'
records, ``{href, text, hidden, time, unread, selector}``, so
``shape.parse_notification`` shapes them unchanged and publishes the link
exactly as before (``shape.absolute_url`` deletes the query).

* ``text`` is the full-card link's own label -- ONE copy of the sentence. The
  card's body repeats it in a paragraph, and the label is the copy the page
  names as the card's.
* ``unread`` is ``None``, never ``False``: no unread marking on this design has
  been measured, so the state is not reported rather than reported as read.
* NOTHING IS PRESSED and nothing navigates. The menu trigger is read for its
  position only; its menu is drawn only when pressed, and is not.

WHICH DESIGN IS READ is decided by the page, never assumed: :func:`harvest`
reads this design only where the screen is drawn and falls back to the old
selectors otherwise, so a page in the old design reads exactly as it did.
"""
from __future__ import annotations

import re
from typing import Any

from linkedin_server import coerce, dom

#: The server-driven screen the cards are drawn in.
SCREEN = "main [data-sdui-screen]"

#: Each card's one full-card link. The label check below decides whether a
#: match IS a card's: its ``aria-labelledby`` must name an element inside it.
CARD_LINK = SCREEN + " a[aria-labelledby][href]"

#: Each card's menu trigger, found by STRUCTURE: the card's one button that
#: declares ``aria-expanded`` (10 of 10 cards draw exactly one). Its
#: accessible name is LinkedIn's ``More options`` by keyed shape, and it is not
#: read: the tracked copy reduces it, and a label is a locale's.
MENU_TRIGGER = "xpath=../descendant::button[@aria-expanded]"

#: The ``selector`` every record from this design carries.
SELECTOR_NAME = "sdui: a full-card link labelled from inside itself"

#: The two designs :func:`harvest` can report.
SDUI = "server-driven"
CLASSIC = "classic"

#: An element id the reader will put into a selector. LinkedIn's ids are
#: generated tokens; anything outside this class is skipped, never escaped.
_ID = re.compile(r"^[A-Za-z0-9_:\-]{1,120}$")


async def is_sdui(page: Any) -> bool:
    """Whether the page draws the server-driven screen. Never raises."""
    try:
        return coerce.as_count(await page.locator(SCREEN).count()) >= 1
    except Exception:  # noqa: BLE001 - an unreadable page is not this design
        return False


async def _read_cards(page: Any, *, max_items: int, max_chars: int = 800) -> list[dict[str, Any]]:
    """The server-driven cards as ``harvest_block_cards`` records.

    A link whose label is not inside it, whose id is outside :data:`_ID`, or
    whose label reads empty is not a card and is skipped. A failure reading one
    card skips that card only.
    """
    links = page.locator(CARD_LINK)
    total = coerce.as_count(await links.count())
    out: list[dict[str, Any]] = []
    for index in range(total):
        if len(out) >= max_items:
            break
        link = links.nth(index)
        try:
            label_id = str(await link.get_attribute("aria-labelledby") or "")
            if not _ID.match(label_id):
                continue
            label = link.locator(f'[id="{label_id}"]')
            if coerce.as_count(await label.count()) != 1:
                continue
            text = " ".join(str(await label.inner_text() or "").split())
            if not text:
                continue
            href = str(await link.get_attribute("href") or "")
            when = ""
            trigger = link.locator(MENU_TRIGGER)
            if coerce.as_count(await trigger.count()) == 1:
                stamp = trigger.locator("xpath=../descendant::p[1]")
                if coerce.as_count(await stamp.count()) == 1:
                    when = " ".join(str(await stamp.inner_text() or "").split())
        except Exception:  # noqa: BLE001 - one card unreadable skips that card
            continue
        out.append({
            "href": href,
            "text": text[:max_chars],
            "hidden": [],
            "time": when[:40],
            "unread": None,
            "selector": SELECTOR_NAME,
        })
    return out


async def harvest(page: Any, *, max_items: int) -> tuple[list[dict[str, Any]], str]:
    """``(records, design)``: this design where the page draws it, else the old.

    The server-driven read runs only where the screen is drawn. Where it is
    not, or where it finds no card, the shipped ``dom.NOTIFICATION_SELECTORS``
    harvest runs exactly as before -- the control is session 5's page, which
    reads 9 of 9 through it.
    """
    if await is_sdui(page):
        records = await _read_cards(page, max_items=max_items)
        if records:
            return records, SDUI
    records = await dom.harvest_block_cards(
        page,
        selectors=dom.NOTIFICATION_SELECTORS,
        max_items=max_items,
        hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
        time_selector=dom.NOTIFICATION_TIME_SELECTOR,
        unread_class=dom.NOTIFICATION_UNREAD_CLASS,
    )
    return records, CLASSIC
