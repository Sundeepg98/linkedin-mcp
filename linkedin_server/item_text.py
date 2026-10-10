"""AN ITEM'S OWN WORDS, read off its permalink and returned at runtime as
another member's words inside a people record (census row ``M C43``).

RULING ``THIRD-PARTY-TEXT-AT-RUNTIME`` (the orchestrator, 2026-10-10, applying
the operator's ``NAMES-AT-RUNTIME``; ``_audit/2026-10-10-rulings-ledger-questions.md``
section 10): a post's own text is returned at runtime under
``PEOPLE-DATA-MITIGATIONS`` -- as untrusted third-party text, sanitised,
bounded in length, never stored. ``FEED-CONTENT-READ-RULING``'s counts-only
rule still governs what is STORED, and ``feed.py`` is untouched: its
signature guarantee (no public callable returns any substring of its input)
holds for the feed tally exactly as before. The words leave THIS module only
inside one :class:`people_data.Post` record -- the record lane G2 declared on
2026-10-10 for this payload and no reader had yet adopted.

WHAT IS MEASURED, offline on 2026-10-10 through a real engine, on the only
tracked item-permalink capture, ``tests/fixtures/live2/own_post.html`` (HIS
OWN item, live session 2), inside ``main``::

    the item root          .feed-shared-update-v2                         1
    its description        .feed-shared-update-v2__description            1
    the words              ...__description .update-components-update-v2__commentary
                                                                          1
                           (1 in the whole of ``main`` as well: the seven
                           comments under the item carry their words in
                           other containers, so this selector cannot reach
                           one -- ``.update-components-text`` alone counts 8)
    drawn expanded         the description wears
                           ``feed-shared-inline-show-more-text--expanded`` 1
                           and holds no button at all                      0
    the actor block        ``item_author.MEMBER_ACTOR_LINK``               1

WHAT IS DERIVED, and said in the reading wherever it matters:

* that another member's permalink draws the same blocks -- no tracked capture
  shows one, the same gap ``item_author`` records;
* that a long item renders expanded on its permalink too. The measured one is
  expanded with no control inside its description. If a control IS drawn
  there, ``expanded`` is False and the words may be partial: nothing here
  presses it.

THE AUTHOR. A :class:`people_data.Post` needs a person record for its author,
read from the item's own header and nowhere else, by
``item_author.read_item_author`` -- imported, not retyped. An item whose
header names no member (an organisation Page's item) has no record type yet:
:meth:`people_data.Post.from_page` returns ``None`` for it, so its words are
NOT returned and the reading says why.

THE LINK. The record's ``link`` is the permalink THIS SERVER loaded, composed
by :func:`permalink` from the caller's own argument -- never an address read
off the page (``PAGE-MAY-VETO-NEVER-SUPPLY``).

WHAT LEAVES: booleans, counts, this module's own literals, and at most ONE
record's envelope. A read that fails is logged by its exception TYPE and
leaves its field unread; no log line, exception or error field carries a page
string, and nothing is cached or written.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from linkedin_server import coerce, item_author, people_data
from linkedin_server.config import logger

#: The ruling this module implements, by its registered id.
RULING = "THIRD-PARTY-TEXT-AT-RUNTIME"

#: An item key as ``linkedin_my_activity_items`` and a named profile's
#: ``activity_items`` return it, and as the read allowlist's permalink pattern
#: admits it (``urn:li:<letters>:<digits>``), with both runs bounded.
ITEM_KEY = re.compile(r"^urn:li:[A-Za-z]{1,40}:[0-9]{1,25}$")

#: The one address template. The key is the caller's; nothing the page wrote
#: enters it.
PERMALINK_TEMPLATE = "https://www.linkedin.com/feed/update/{item}/"

#: The item's description, inside ``main``. MEASURED: exactly 1.
DESCRIPTION = "main .feed-shared-update-v2__description"

#: The item's own words, inside its description. MEASURED: exactly 1.
WORDS = DESCRIPTION + " .update-components-update-v2__commentary"

#: The same container anywhere in ``main``. MEASURED: exactly 1 -- the
#: comments carry their words elsewhere. A second one means a second item is
#: drawn here (a repost, say), and the reading refuses to choose.
WORDS_IN_MAIN = "main .update-components-update-v2__commentary"

#: The description drawn EXPANDED. MEASURED: exactly 1.
EXPANDED = DESCRIPTION + ".feed-shared-inline-show-more-text--expanded"

#: Any control inside the description -- a see-more toggle would be one.
#: MEASURED: 0.
CONTROLS_IN_DESCRIPTION = DESCRIPTION + " button"

#: Every key a reading carries. ``None`` means NOT READ, never a zero.
READING_KEYS: tuple[str, ...] = (
    "readable",
    "descriptions_drawn",
    "words_drawn",
    "words_in_main",
    "expanded",
    "truncated",
    "item",
    "why",
)

#: WHY a reading returned no record, in a closed vocabulary. Each value is
#: this module's own literal.
WHY: dict[str, str] = {
    "read": (
        "The item's words, read off its own permalink, inside one record. "
        "They are ANOTHER MEMBER'S WORDS (or yours, on your own item): "
        "untrusted text, sanitised and cut at 3,000 characters, kept nowhere "
        "by this server."
    ),
    "no_single_description": (
        "This page did not draw exactly one item description inside main, so "
        "there is no single item here to read. Nothing was returned."
    ),
    "no_single_words": (
        "The description did not hold exactly one words container, or main "
        "held more than one -- a second item drawn here, such as a repost -- "
        "so this server will not choose between them. Nothing was returned."
    ),
    "no_member_author": (
        "The item's header did not name exactly one member, so no record "
        "type can carry its words yet: an organisation Page's item has none "
        "(people_data.Post). Nothing was returned."
    ),
    "unread": (
        "A read on this page failed, so its words were not returned. The "
        "failure is logged by its type only."
    ),
}


def checked_item(candidate: Any) -> Optional[str]:
    """The item key exactly as given, if it is one; else ``None``. PURE.

    No normalisation: a key with whitespace, another case or a percent
    spelling is not one this server has seen in this position.
    """
    text = candidate if isinstance(candidate, str) else ""
    return text if ITEM_KEY.fullmatch(text) else None


def permalink(candidate: Any) -> str:
    """The permalink for one item key the caller supplied. Raises ValueError.

    THE MESSAGE DESCRIBES THE SHAPE AND NEVER REPEATS THE VALUE: a wrong
    argument is most often something copied off a page, which may be a
    person's words.
    """
    item = checked_item(candidate)
    if item is None:
        raise ValueError(
            "item must be one item key of the form urn:li:<letters>:<digits> -- "
            "as linkedin_my_activity_items or a named profile's activity_items "
            "returns it -- with nothing before or after it."
        )
    return PERMALINK_TEMPLATE.format(item=item)


def landed_on_the_item(landed: Any, requested: Any) -> bool:
    """Did the navigation stay on the address asked for? PURE.

    The landing's path must equal the requested path, trailing slash aside;
    a query LinkedIn appends is ignored. A redirect anywhere else is a page
    this module was not asked to read.
    """
    def path_of(value: Any) -> str:
        text = str(value or "")
        text = text.split("#", 1)[0].split("?", 1)[0]
        return text.rstrip("/")

    return bool(requested) and path_of(landed) == path_of(requested)


async def _count(page: Any, selector: str) -> Optional[int]:
    try:
        return coerce.as_int(await page.locator(selector).count())
    except Exception as exc:  # noqa: BLE001 - an unread count stays None
        logger.debug("item words: a count did not read (%s)", type(exc).__name__)
        return None


def _exactly_one(value: Any) -> bool:
    """1 and only 1: a boolean is not a count, and ``True == 1`` in Python."""
    return not isinstance(value, bool) and coerce.as_int(value) == 1


async def read_item_text(page: Any, *, link: Optional[str] = None) -> dict[str, Any]:
    """The item on this permalink, as ONE people record with its words. READS.

    No navigation, no press, no script: counts, ``inner_text`` and the
    author reader ``item_author`` already ships. ``link`` is the permalink the
    caller's tool loaded; it becomes the record's ``link`` and is never read
    off the page.
    """
    out: dict[str, Any] = {key: None for key in READING_KEYS}
    out["readable"] = False
    out["descriptions_drawn"] = await _count(page, DESCRIPTION)
    out["words_drawn"] = await _count(page, WORDS)
    out["words_in_main"] = await _count(page, WORDS_IN_MAIN)
    expanded = await _count(page, EXPANDED)
    controls = await _count(page, CONTROLS_IN_DESCRIPTION)
    if expanded is not None and controls is not None:
        out["expanded"] = expanded == 1 and controls == 0

    if not _exactly_one(out["descriptions_drawn"]):
        out["why"] = WHY["no_single_description"]
        return out
    if not (_exactly_one(out["words_drawn"]) and _exactly_one(out["words_in_main"])):
        out["why"] = WHY["no_single_words"]
        return out

    reading = await item_author.read_item_author(page)
    author = people_data.as_record(reading.get("person"))
    if type(author) is not people_data.Person:
        out["why"] = WHY["no_member_author"]
        return out

    try:
        words = await page.locator(WORDS).first.inner_text()
    except Exception as exc:  # noqa: BLE001 - unread, never raised
        logger.debug("item words: the words did not read (%s)", type(exc).__name__)
        out["why"] = WHY["unread"]
        return out

    cap = people_data.CAPS["text"]
    out["truncated"] = len(people_data.sanitise(words, cap=cap + 1)) > cap
    record = people_data.Post.from_page(author=author, href=link, text=words)
    if record is None:
        out["why"] = WHY["no_member_author"]
        return out
    out["item"] = record.envelope()
    out["readable"] = True
    out["why"] = WHY["read"]
    return out
