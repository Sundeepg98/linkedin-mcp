"""Read the GROUPS and the EVENTS a groups or events search results page draws, as records.

## WHAT DECIDED IT

``D2-SEARCH-VERTICALS-WIDENED`` (2026-09-24) admitted the groups and events
search verticals, composed by ``search_verticals.compose`` from a tool's
arguments only, and said of each: "Each then needs a reader."
``NAMES-AT-RUNTIME`` (the operator's, 2026-09-24 08:11) lets a read whose
capability IS the items it finds return them -- a group or an event as its
title and its link -- and ``PEOPLE-DATA-MITIGATIONS`` (the orchestrator's)
holds every such reader to six mitigations, each enforced below by code and
held by ``tests/test_search_vertical_results.py``. These readers serve census
rows ``N 161`` (search for groups by name or keyword) and ``N 179`` (search
for events by keyword, on the Events tab -- which IS the vertical).

## THE CAPTURES THIS IS BUILT OVER, AND NOTHING ELSE

One results page of each vertical exists: the live lane's session 2 (groups)
and session 3 (events), 2026-09-28, kept as gitignored keyed skeletons and as
the tracked copies ``tests/fixtures/live2/n161.html`` and
``tests/fixtures/live3/n179.html``; measured OFFLINE, by shape only, on
2026-10-10 (tags, attribute names, text shapes -- never a text). The readers'
fixtures are ``tests/fixtures/synthetic/search_groups_live.html`` and
``search_events_live.html``, built from the same skeletons by
``scripts/_build_search_vertical_fixtures.py`` and tied to the tracked copies
by a structure digest. What they draw, measured on every result:

GROUPS -- NINE RESULTS, each a group link ``/groups/<digits>/`` (relative,
5 to 8 digits) that WRAPS one ``[role="listitem"]``; each group linked ONCE.
Inside the list item: a picture, then a column whose FIRST paragraph is the
TITLE (one text node, no child element, on all nine), then a second short
line, a member count and a description with the keyword in ``strong``; then a
Join button whose label repeats the title. No other link in any card.

EVENTS -- THIRTEEN RESULTS, each a ``[role="listitem"]`` holding an event link
``/events/<19 digits>/`` (relative) that HOLDS A SECOND LINK TO THE SAME EVENT:
the TITLE, the inner link's own text (one text node, no child element, on all
thirteen). After it a date line, a second line, sometimes a description, and
an attendee count. No button and no other link in any card. An anchor inside
an anchor: the page builds it with DOM calls, and HTML's parser would never
produce it, which is why the tests load the fixture through an XML parser.

The class names are generated hashes. Nothing here reads a class.

## HOW IT READS: EVERY CARD PINNED BEFORE ANY TEXT IS READ

A search page re-renders while it lazy-loads and re-ranks, and a reader that
re-finds its elements for every read can take a TITLE off one result and a
LINK off another. So the cards are resolved ONCE, to handles, before any text
is read; every read goes through a handle; and the links are read AGAIN after
the text, a card whose link moved meanwhile being skipped and counted rather
than returned. A group or an event is returned once, however many cards carry
its link. Handles act at once and never wait.

## WHAT IS READ, AND ALL THAT IS READ

    link   the card's own href, reduced by people_data.canonical_group_link or
           canonical_event_link (an event's title run into its address is
           dropped; the query is dropped)
    title  GROUPS: the text of the first paragraph inside the card's list
           item. EVENTS: the text of the first event link inside the card,
           required to point at the card's own event. Either way required to
           be visible and to hold no nested element carrying text (the
           captures' title nodes hold none, so nested text is a drawing
           nothing here can split)

NEVER READ: the second line, the member count, the description and its
highlighted keyword, the date, the attendee count; any ``aria-label`` -- the
Join control's names the group -- ``alt`` or ``title``; any control, which is
never pressed either. The only attribute read is ``href``: of the card, and of
an event's title link.

## THE SIX MITIGATIONS, WHERE EACH LIVES

1. DECLARED FIELDS ONLY -- a :class:`people_data.Group` or
   :class:`people_data.Event` envelope per result, and nothing else.
2. SANITISED AND MARKED -- ``Group.from_page`` and ``Event.from_page``: every
   string sanitised, the untrusted-third-party-text marker on every record.
3. NEVER STORED -- this module writes to nothing: no file, no log, no cache,
   no module-level container. A failure is counted by its exception's TYPE
   NAME, never its message, because a message can quote a page.
4. ONE PAGE -- it reads the page it is handed and loads none; the tool loads
   one. At most :data:`MAX_RESULTS_READ` results per call, above the nine and
   thirteen the captures drew.
5. VISIBLE ONLY -- a card or a title the page does not show is not read.
6. NOT A TARGET BY ITSELF -- no write path in this package reaches this
   module, and a write takes a link or an id its caller names.

## WHAT IT DOES NOT CLAIM

That these are all the groups or events the search matched (one page, as
drawn, and a search page lazy-loads); that a title is unique (the link says
which); or that the rules fit a page drawn differently from the captures.
Every rule above refuses rather than guesses, and each refusal is counted in
the denominators. ONE LIMIT NO STRUCTURE CLOSES: a group link holding a list
item is a result wherever the page draws it -- on the capture that selects
exactly the nine results, and a page that drew recommended groups the same
way would have them read as results.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable

from linkedin_server import people_data

_GROUP_HREFS = 'a[href^="/groups/"], a[href^="https://www.linkedin.com/groups/"]'
_EVENT_HREFS = 'a[href^="/events/"], a[href^="https://www.linkedin.com/events/"]'

#: A GROUP RESULT: a group link that HOLDS a list item. On the capture that
#: selects exactly the nine results -- the aside's "More" link goes to the
#: search, not to a group, and nothing else on the page is a group link.
GROUP_RESULT_CARD = (
    ':is(a[href^="/groups/"], a[href^="https://www.linkedin.com/groups/"])'
    ':has([role="listitem"])'
)

#: AN EVENT RESULT: an event link that HOLDS an event link. On the capture
#: that selects exactly the thirteen card links -- a title link holds none.
EVENT_RESULT_CARD = (
    ':is(a[href^="/events/"], a[href^="https://www.linkedin.com/events/"])'
    ':has(a[href^="/events/"], a[href^="https://www.linkedin.com/events/"])'
)

#: An event's TITLE LINK: the first event link inside the card.
EVENT_TITLE_LINK = _EVENT_HREFS

#: A group's TITLE PARAGRAPH: the first paragraph inside the card's list item,
#: in document order.
GROUP_TITLE_PARAGRAPH = '[role="listitem"] p'

#: A result link ENCLOSING a card: a card nested in another result is not one.
GROUP_ENCLOSING_RESULT = (
    "xpath=ancestor::a[starts-with(@href, '/groups/') "
    "or starts-with(@href, 'https://www.linkedin.com/groups/')]"
)
EVENT_ENCLOSING_RESULT = (
    "xpath=ancestor::a[starts-with(@href, '/events/') "
    "or starts-with(@href, 'https://www.linkedin.com/events/')]"
)

#: The title node's child elements.
NESTED = "xpath=./*"

#: The most results one call reads. The captures drew nine groups and
#: thirteen events; the ceiling is a budget above that, not a measurement of
#: anything LinkedIn does.
MAX_RESULTS_READ = 25

#: The closed reasons a group card is not returned, in the order they are
#: checked.
GROUP_SKIP_REASONS: tuple[str, ...] = (
    "no_group_link",
    "inside_another_result",
    "not_visible",
    "no_title_paragraph",
    "title_has_nested_text",
    "changed_while_read",
    "no_title",
    "already_returned",
)

#: The closed reasons an event card is not returned, in the order they are
#: checked.
EVENT_SKIP_REASONS: tuple[str, ...] = (
    "no_event_link",
    "inside_another_result",
    "not_visible",
    "title_is_another_event",
    "title_has_nested_text",
    "changed_while_read",
    "no_title",
    "already_returned",
)


async def _nested_text(title: Any) -> bool:
    """Does any child element of the title node carry text?"""
    for child in await title.query_selector_all(NESTED):
        if str(await child.text_content() or "").strip():
            return True
    return False


async def _read_group_card(card: Any) -> Any:
    """One group card: a :class:`people_data.Group`, or the
    GROUP_SKIP_REASONS entry that stopped it."""
    link = people_data.canonical_group_link(await card.get_attribute("href"))
    if link is None:
        return "no_group_link"
    if await card.query_selector(GROUP_ENCLOSING_RESULT) is not None:
        return "inside_another_result"
    if not await card.is_visible():
        return "not_visible"
    title = await card.query_selector(GROUP_TITLE_PARAGRAPH)
    if title is None:
        return "no_title_paragraph"
    if not await title.is_visible():
        return "not_visible"
    if await _nested_text(title):
        return "title_has_nested_text"
    text = await title.inner_text()
    # THE LINK AGAIN, AFTER THE TEXT READ. A node the page reused for another
    # group meanwhile would pair one group's title with another's link.
    if people_data.canonical_group_link(await card.get_attribute("href")) != link:
        return "changed_while_read"
    group = people_data.Group.from_page(title=text, href=link)
    if group is None:
        return "no_title"
    return group


async def _read_event_card(card: Any) -> Any:
    """One event card: a :class:`people_data.Event`, or the
    EVENT_SKIP_REASONS entry that stopped it."""
    link = people_data.canonical_event_link(await card.get_attribute("href"))
    if link is None:
        return "no_event_link"
    if await card.query_selector(EVENT_ENCLOSING_RESULT) is not None:
        return "inside_another_result"
    if not await card.is_visible():
        return "not_visible"
    title = await card.query_selector(EVENT_TITLE_LINK)
    if title is None or people_data.canonical_event_link(await title.get_attribute("href")) != link:
        return "title_is_another_event"
    if not await title.is_visible():
        return "not_visible"
    if await _nested_text(title):
        return "title_has_nested_text"
    text = await title.inner_text()
    # BOTH LINKS AGAIN, AFTER THE TEXT READ.
    if (
        people_data.canonical_event_link(await card.get_attribute("href")) != link
        or people_data.canonical_event_link(await title.get_attribute("href")) != link
    ):
        return "changed_while_read"
    event = people_data.Event.from_page(title=text, href=link)
    if event is None:
        return "no_title"
    return event


async def _read_cards(
    cards: list[Any],
    failed: dict[str, int],
    read_card: Callable[[Any], Awaitable[Any]],
    reasons: tuple[str, ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The records the cards hold, and the counts of what was not read.

    Takes the cards ALREADY RESOLVED to handles, and the failures met
    resolving them. Never raises: each card's failure is counted by its
    exception's TYPE NAME."""
    skipped = {reason: 0 for reason in reasons}
    records: list[dict[str, Any]] = []
    returned: set[str] = set()
    to_read = min(len(cards), MAX_RESULTS_READ)
    for card in cards[:to_read]:
        try:
            verdict = await read_card(card)
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            failed[kind] = failed.get(kind, 0) + 1
            continue
        if isinstance(verdict, str):
            skipped[verdict] += 1
            continue
        if verdict.link in returned:
            skipped["already_returned"] += 1
            continue
        returned.add(verdict.link)
        records.append(verdict.envelope())
    denominators = {
        "result_cards_seen": len(cards),
        "result_cards_attempted": to_read,
        "returned": len(records),
        "skipped": skipped,
        "failed": failed,
    }
    return records, denominators


async def read_group_results(page: Any) -> dict[str, Any]:
    """The groups a groups-search results page draws, as group records.

    Returns ``{"groups": [<envelope>, ...], "groups_denominators": {...}}``.
    Every string in ``groups`` sits inside a :class:`people_data.Group`
    envelope; ``groups_denominators`` holds integers, closed literals and
    exception TYPE names only. ``result_cards_attempted`` counts the cards the
    call TRIED, at most :data:`MAX_RESULTS_READ`; each one tried is returned,
    skipped for a counted reason, or counted as failed. Reads the page it is
    handed; loads nothing, presses nothing, scrolls nothing, and never raises.
    """
    failed: dict[str, int] = {}
    try:
        cards = list(await page.locator(GROUP_RESULT_CARD).element_handles())
    except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
        failed[type(exc).__name__] = 1
        cards = []
    groups, denominators = await _read_cards(
        cards, failed, _read_group_card, GROUP_SKIP_REASONS
    )
    return {"groups": groups, "groups_denominators": denominators}


async def read_event_results(page: Any) -> dict[str, Any]:
    """The events an events-search results page draws, as event records.

    Returns ``{"events": [<envelope>, ...], "events_denominators": {...}}``,
    on the same terms as :func:`read_group_results`.
    """
    failed: dict[str, int] = {}
    try:
        cards = list(await page.locator(EVENT_RESULT_CARD).element_handles())
    except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
        failed[type(exc).__name__] = 1
        cards = []
    events, denominators = await _read_cards(
        cards, failed, _read_event_card, EVENT_SKIP_REASONS
    )
    return {"events": events, "events_denominators": denominators}
