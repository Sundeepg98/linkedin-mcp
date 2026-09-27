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

from linkedin_server import people_data

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


async def read_suggested_presence(page: Any) -> dict[str, Any]:
    """The composer's suggested people, each with the presence it drew."""
    people: list[dict[str, Any]] = []
    seen = groups = hidden = unparsed = 0
    try:
        cards = list(await page.query_selector_all(SUGGESTED_CARD))
        for card in cards[:MAX_CARDS]:
            seen += 1
            # VISIBLE ONLY: counted, and nothing is read from it.
            if (not await card.is_visible()
                    or await card.query_selector(_HIDDEN_ANCESTOR) is not None):
                hidden += 1
                continue
            name = await _text(card, "dt")
            headline = await _text(card, "dd")
            # A GROUP IS NOT A PERSON: a facepile of several photos, or
            # LinkedIn's own "Group Message" line. Counted, never read further.
            if (len(await card.query_selector_all("img")) > 1
                    or GROUP_LINE.match(str(headline or "").strip())):
                groups += 1
                continue
            presence = None
            for span in await card.query_selector_all("span"):
                found = STATUS.match(str(await span.text_content() or "").strip())
                if found:
                    presence = _own_word(found.group(1))
                    break
            person = people_data.Person.from_page(name=name, headline=headline)
            if person is None:
                unparsed += 1
                continue
            people.append({"person": person.envelope(), "presence": presence})
    except Exception as exc:  # noqa: BLE001 -- raised by type alone
        raise RuntimeError(
            f"could not read the composer's suggestions ({type(exc).__name__})"
        ) from None
    return {
        "suggested": people,
        "denominators": {
            "cards_seen": seen,
            "people_returned": len(people),
            "people_unparsed": unparsed,
            "groups_skipped": groups,
            "hidden_skipped": hidden,
        },
    }
