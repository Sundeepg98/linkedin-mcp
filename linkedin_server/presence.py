"""Messaging presence of the members the composer suggests -- census ``M M53``.

WHAT THE PAGE DRAWS. ``/messaging/compose/`` -- the composer with nobody in
it, which opens no conversation (measured three times: no redirect, zero
dialogs) -- draws a "Suggested" list of recipients, a listbox of option
cards. Captured 2026-09-20 (``_state/cap-ct-compose.html``, gitignored; its
structure is kept in ``tests/fixtures/synthetic/compose_suggestions.html``):
seventeen cards, sixteen of them a person and one a group conversation. A
person's card draws

    a photo            alt "Suggested: Photo of <name>"
    a presence line    "Status is reachable" | "Status is offline" |
                       "Status is online"     (visually hidden text)
    a name             the card's <dt>
    a headline         the card's <dd>

and a group's draws a facepile of several photos, a name and "Group Message
<middot> <n> participants", with no presence line.

WHAT THIS RETURNS. One row per person card, ``{"person", "presence"}``:
``person`` a PEOPLE RECORD (``people_data.Person``) -- name and headline, no
link (the card carries none), no degree -- under NAMES-AT-RUNTIME and
PEOPLE-DATA-MITIGATIONS; ``presence`` one of :data:`PRESENCE_WORDS`, THIS
module's own string, or null where the card drew no presence line. Presence
is not a field of the person record: it is what this row says about the
member at the moment of the read, the way ``linkedin_who_viewed_me``'s
``viewed`` sits beside its record.

WHAT IT DOES NOT RETURN: a group conversation (counted, never a person); a
card that is not visible or sits inside an ``aria-hidden="true"`` container
(counted); the photo's alt text; anything the list has not drawn -- nothing
is typed, so the list is the page's own suggestions, and a member it does not
draw is ABSENT here, which is not "offline".

HOW IT READS: Playwright's own read calls on each card, pinned as an element
handle before anything is read from it, so a card's name, headline and
presence come from the same card; no script, no press, no typing.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from linkedin_server import dom, people_data
from linkedin_server.errors import ExtractionFailedError

#: The option cards of the composer's recipient list.
SUGGESTED_CARD = '[data-view-name="messaging-type-ahead-card"]'

#: The presence words, as LinkedIn's hidden text spells them after
#: "Status is". CLOSED: all three were drawn on the capture.
PRESENCE_WORDS: tuple[str, ...] = ("reachable", "offline", "online")

#: The WORD only: anything a status line carries after it is never kept.
STATUS = re.compile(r"Status is (reachable|offline|online)\b")

#: LinkedIn's own line on a group conversation's card.
GROUP_LINE = re.compile(r"Group Message\b")

#: At most this many cards are read. The capture drew seventeen.
MAX_CARDS = 25

_HIDDEN_ANCESTOR = "xpath=ancestor-or-self::*[@aria-hidden='true']"


def _own_word(value: Optional[str]) -> Optional[str]:
    """The declared presence word equal to ``value``, as THIS module's string."""
    for word in PRESENCE_WORDS:
        if value == word:
            return word
    return None


async def _text(card: Any, selector: str) -> Optional[str]:
    element = await card.query_selector(selector)
    return None if element is None else str(await element.inner_text() or "")


async def _card(card: Any, people: list[dict[str, Any]], tally: dict[str, Any]) -> None:
    """One card: hidden, a group, a person, or unparsed -- counted as which."""
    # VISIBLE ONLY: counted, and nothing is read from it.
    if (not await card.is_visible()
            or await card.query_selector(_HIDDEN_ANCESTOR) is not None):
        tally["hidden"] += 1
        return
    name = await _text(card, "dt")
    headline = await _text(card, "dd")
    # A GROUP IS NOT A PERSON: a facepile of several photos, or LinkedIn's own
    # "Group Message" line. Counted, never read further.
    if (len(await card.query_selector_all("img")) > 1
            or GROUP_LINE.match(str(headline or "").strip())):
        tally["groups"] += 1
        return
    presence = None
    for span in await card.query_selector_all("span"):
        found = STATUS.match(str(await span.text_content() or "").strip())
        if found:
            presence = _own_word(found.group(1))
            break
    person = people_data.Person.from_page(name=name, headline=headline)
    if person is None:
        tally["unparsed"] += 1
        return
    people.append({"person": person.envelope(), "presence": presence})


async def read_suggested_presence(page: Any) -> dict[str, Any]:
    """The composer's suggested people, each with the presence it drew."""
    people: list[dict[str, Any]] = []
    tally: dict[str, Any] = {"groups": 0, "hidden": 0, "unparsed": 0, "failed": {}}
    try:
        cards = list(await page.query_selector_all(SUGGESTED_CARD))
    except Exception as exc:  # noqa: BLE001 -- raised by type alone
        # THE LANDING IS DESCRIBED, NEVER PUBLISHED: the same ruling the
        # twelve dom readers raise under (WITHHELD), and the same describer.
        raise ExtractionFailedError(
            f"could not read the composer's suggestions ({type(exc).__name__})",
            hint=dom._landing_note(page),
        ) from None
    # EVERY CARD DRAWN IS COUNTED, and at most MAX_CARDS are read, so a list
    # longer than the cap reads as longer rather than as exactly full. ONE CARD
    # THAT CANNOT BE READ IS COUNTED BY ITS EXCEPTION'S TYPE -- never its
    # message -- and the others are still read.
    read = 0
    for card in cards[:MAX_CARDS]:
        read += 1
        try:
            await _card(card, people, tally)
        except Exception as exc:  # noqa: BLE001 -- counted by type, never quoted
            name = type(exc).__name__
            tally["failed"][name] = tally["failed"].get(name, 0) + 1
    return {
        "suggested": people,
        "denominators": {
            "cards_seen": len(cards),
            "cards_read": read,
            "people_returned": len(people),
            "people_unparsed": tally["unparsed"],
            "groups_skipped": tally["groups"],
            "hidden_skipped": tally["hidden"],
            "cards_failed": tally["failed"],
        },
    }
