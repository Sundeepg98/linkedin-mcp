"""Read the PEOPLE a people-search results page draws, as people records.

## WHAT DECIDED IT

``NAMES-AT-RUNTIME`` (the operator's, 2026-09-24 08:11): "The functionality is
to return people's names as the result. During runtime, if you want to be
careful, then follow the best procedure and practice to mitigate the risk."
``PEOPLE-DATA-MITIGATIONS`` (the orchestrator's) names six mitigations, and
this reader is held to all six (``tests/test_people_search_names.py``, one
section each, every one shown failing). It serves ``N 79`` (search for a
person), ``N 194`` (hiring managers found by a hashtag keyword) and ``N 172``
(a member's connections, by the ``connectionOf`` facet) -- the rows the WHO
rule held GAP until a reader returned names.

``linkedin_people_search_shape`` calls it only when its caller passes
``include_names=True``, the package's opt-in for a people payload
(``linkedin_open_messaging`` set it first); by default that tool still returns
the page's shape and nobody on it.

## WHY THIS IS NOT IN ``people_search.py``

That module composes the search address, and its proof that nothing a page
drew can reach an address is that it touches no page at all --
``tests/test_people_search_readers.py`` asserts it on the module's syntax
tree. A reader takes a page, so it lives here, and the proof stays whole.

## THE CAPTURE THIS IS BUILT OVER, AND NOTHING ELSE

One capture of a people-search results page exists: the live lane's session
1, 2026-09-23 (``_audit/2026-09-23-live-lane-session-1.md``, entry 5, item
9), kept in that lane's gitignored state and read OFFLINE, for structure
only, by lane S on 2026-09-27 -- tags, attribute names and text SHAPES, never
a text. What it draws, measured on every result and not on a sample:

* TEN RESULTS, each a child of one list, each holding a member link. No
  result is drawn without one.
* THE WHOLE CARD IS ONE LINK to the member, and inside it a second link to
  the SAME member is the name, in a paragraph that also draws the degree
  ("<bullet> 2nd" on all ten). An anchor inside an anchor: the page builds it
  with DOM calls, and HTML's parser would never produce it, which is why the
  tests load their fixture through an XML parser (the test file says how).
* THE NAME IS THE NAME LINK'S OWN TEXT: the link's other children are an
  empty span and a badge drawn as an image, neither carrying any text.
* THE TITLE PARAGRAPH IS THE FIRST OF THREE SIBLINGS on all ten, and the two
  after it each hold exactly one link-free line. The first line ran 28 to 181
  characters and carried a '|' or the word 'at' on all ten; the second was 27
  characters, three words and a comma on all ten. The first is the HEADLINE;
  the second is the LOCATION, which is not a declared field.
* ELSEWHERE IN THE CARD, a sentence names MUTUAL CONNECTIONS, each a link to
  ANOTHER member -- one or two per card. They are people LinkedIn shows, and
  they are not results.
* The class names are generated hashes. Nothing here reads a class.

## HOW IT READS: EVERY CARD PINNED BEFORE ANY TEXT IS READ

A search page re-renders while it lazy-loads and re-ranks, and a reader that
re-finds its elements for every read can take a NAME off one result and a
LINK off another -- the wrong person, reported confidently. So the cards are
resolved ONCE, to handles on their DOM nodes, before any text is read; every
read after that goes through a handle, which a re-render can detach but not
redirect; and both links are read AGAIN after the text, a card whose links
moved meanwhile being skipped and counted rather than returned. A person is
returned once, however many cards carry the same link. Handles act at once
and never wait: a node gone from the page answers "not visible", not a
timeout.

## WHAT IS READ, AND ALL THAT IS READ

    link      the card's own href, reduced by people_data.canonical_profile_link
    name      the NAME LINK's own text -- the first member link inside the card,
              required to point at the card's own member, to be visible, and to
              hold no nested element carrying text (the capture's name link has
              none, so nested text is a drawing nothing here can split)
    degree    the title paragraph's text beyond the name, reduced to the closed
              vocabulary by people_data.canonical_degree
    headline  the first of the two lines, READ ONLY IN THE CAPTURED SHAPE: the
              title paragraph first among exactly three siblings, each of the
              other two holding exactly one line and no link, and the line
              visible. Anything else leaves the headline ABSENT --
              people_data.ABSENT, null, never an empty string -- and
              counted

NEVER READ: the location line's text; the mutual-connections sentence and
every link in it; the hidden copy of the name that labels the photo; any
``aria-label``, ``alt`` or ``title``; the Connect control. The only attribute
read is ``href``: of the card, of its name link, and of the link enclosing
the title paragraph, which must be the card itself.

## THE SIX MITIGATIONS, WHERE EACH LIVES

1. DECLARED FIELDS ONLY -- a :class:`people_data.Person` envelope per result
   and nothing else about anybody.
2. SANITISED AND MARKED -- ``Person.from_page``: every string sanitised, the
   untrusted-third-party-text marker on every record.
3. NEVER STORED -- this module writes to nothing: no file, no log, no cache,
   no module-level container. A failure is counted by its exception's TYPE
   NAME, never its message, because a message can quote a page.
4. ONE PAGE -- it reads the page it is handed and loads none; the tool loads
   one. At most :data:`MAX_RESULTS_READ` results per call, above the ten the
   capture drew.
5. VISIBLE ONLY -- a card, a name link or a headline line the page does not
   show is not read. A result LinkedIn draws as "LinkedIn Member" comes back
   as exactly that, and nothing here looks anywhere else for who it was. A
   result drawn with NO member link is not read at all; no capture shows one.
6. NOT A TARGET BY ITSELF -- no write path in this package reaches this
   module, and a write takes a link or an id its caller names.

## WHAT IT DOES NOT CLAIM

That these are all the people the search matched (one page, as drawn, and a
search page lazy-loads); that a name is unique (two members can share one --
the link says which); or that the rules fit a page drawn differently from the
capture. Every rule above refuses rather than guesses, and each refusal is
counted in ``people_denominators`` -- with ONE LIMIT NO STRUCTURE CAN CLOSE:
the headline and the location are told apart by ORDER alone, as the capture
drew them, because nothing else in the markup distinguishes them (the classes
that differ are generated hashes). A page that drew the location first, in
the same shape, would return it as the headline.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import people_data

#: A MEMBER LINK, in the two spellings a LinkedIn page writes one: the
#: absolute form, which every one of the capture's 40 ``/in/`` hrefs used,
#: and the relative form other captured surfaces in this repository draw.
MEMBER_LINK = 'a[href^="https://www.linkedin.com/in/"], a[href^="/in/"]'

#: A RESULT CARD: a member link that HOLDS a member link. On the capture that
#: selects exactly the ten results -- a mutual connection's link holds no
#: link, and nothing else on the page wraps one.
RESULT_CARD = (
    ':is(a[href^="https://www.linkedin.com/in/"], a[href^="/in/"])'
    ':has(a[href^="https://www.linkedin.com/in/"], a[href^="/in/"])'
)

#: The same two spellings as an XPath test, for the axes CSS cannot walk.
_MEMBER_HREF = (
    "starts-with(@href, 'https://www.linkedin.com/in/') "
    "or starts-with(@href, '/in/')"
)

#: A member link ENCLOSING a card: a card nested in another result is not one.
ENCLOSING_RESULT = f"xpath=ancestor::a[{_MEMBER_HREF}]"

#: The paragraph that holds the name link: its nearest ``p`` ancestor.
TITLE_BLOCK = "xpath=ancestor::p[1]"

#: The link enclosing the title paragraph, which must be the card itself.
BLOCK_OWNER = "xpath=ancestor::a[1]"

#: The title paragraph's siblings: none before it, the two lines after it.
BEFORE_BLOCK = "xpath=preceding-sibling::*"
BESIDE_BLOCK = "xpath=following-sibling::*"

#: Inside one line's sibling: its paragraph, and any link at all.
LINE_PARAGRAPH = "xpath=.//p"
ANY_LINK = "xpath=.//a"

#: The name link's child elements.
NESTED = "xpath=./*"

#: How many line siblings the capture drew after the title, on all ten
#: results: the headline, then the location.
CAPTURED_LINES = 2

#: The most results one call reads. The capture drew ten; the ceiling is a
#: budget above that, not a measurement of anything LinkedIn does.
MAX_RESULTS_READ = 25

#: The closed reasons a card is not returned, in the order they are checked.
SKIP_REASONS: tuple[str, ...] = (
    "no_member_link",
    "inside_another_result",
    "not_visible",
    "title_is_another_member",
    "no_title_paragraph",
    "title_outside_its_result",
    "name_link_has_nested_text",
    "no_name",
    "changed_while_read",
    "already_returned",
)


def degree_beside(name_text: Any, block_text: Any) -> Optional[str]:
    """The degree the title paragraph draws beside the name, or ``None``.

    The name is removed first, once, so a name that itself carries "2nd" is
    not read as a degree. Both strings are sanitised before they are
    compared, so an invisible character cannot keep them apart. PURE.
    """
    cap = people_data.CAPS["headline"]
    name = people_data.sanitise(name_text, cap=cap)
    block = people_data.sanitise(block_text, cap=cap)
    rest = block.replace(name, "", 1) if name else block
    return people_data.canonical_degree(rest)


async def _href(handle: Any) -> Optional[str]:
    """A handle's href as a canonical profile link, or ``None``."""
    return people_data.canonical_profile_link(await handle.get_attribute("href"))


async def _headline(block: Any) -> Optional[str]:
    """The headline, read only in the captured shape; ``None`` otherwise.

    The second line -- the location -- is inspected for its SHAPE (a link?
    one paragraph?) and its text is never read.
    """
    if await block.query_selector(BEFORE_BLOCK) is not None:
        return None
    beside = list(await block.query_selector_all(BESIDE_BLOCK))
    if len(beside) != CAPTURED_LINES:
        return None
    lines = []
    for sibling in beside:
        if await sibling.query_selector(ANY_LINK) is not None:
            return None
        paragraphs = list(await sibling.query_selector_all(LINE_PARAGRAPH))
        if len(paragraphs) != 1:
            return None
        lines.append(paragraphs[0])
    if not await lines[0].is_visible():
        return None
    return await lines[0].inner_text()


async def _read_card(card: Any) -> Any:
    """One card: a :class:`people_data.Person` and whether its headline was
    read, or the SKIP_REASONS entry that stopped it."""
    link = await _href(card)
    if link is None:
        return "no_member_link"
    if await card.query_selector(ENCLOSING_RESULT) is not None:
        return "inside_another_result"
    if not await card.is_visible():
        return "not_visible"
    title = await card.query_selector(MEMBER_LINK)
    if title is None or await _href(title) != link:
        return "title_is_another_member"
    if not await title.is_visible():
        return "not_visible"
    block = await title.query_selector(TITLE_BLOCK)
    if block is None:
        return "no_title_paragraph"
    owner = await block.query_selector(BLOCK_OWNER)
    if owner is None or await _href(owner) != link:
        return "title_outside_its_result"
    for child in await title.query_selector_all(NESTED):
        if str(await child.text_content() or "").strip():
            return "name_link_has_nested_text"
    name = await title.inner_text()
    degree = degree_beside(name, await block.inner_text())
    headline = await _headline(block)
    # THE LINKS AGAIN, AFTER EVERY TEXT READ. A node the page reused for
    # another member meanwhile would pair one person's name with another's
    # link; a card whose links moved is skipped, never returned.
    if await _href(card) != link or await _href(title) != link:
        return "changed_while_read"
    person = people_data.Person.from_page(
        name=name, headline=headline, href=link, degree=degree
    )
    if person is None:
        return "no_name"
    return person, headline is not None


async def read_result_people(page: Any) -> dict[str, Any]:
    """The people the results page draws, as people-record envelopes.

    Returns ``{"people": [<envelope>, ...], "people_denominators": {...}}``.
    Every string in ``people`` sits inside a :class:`people_data.Person`
    envelope; ``people_denominators`` holds integers, closed literals and
    exception TYPE names only. ``result_cards_attempted`` counts the cards
    the call TRIED, at most :data:`MAX_RESULTS_READ`; each one tried is
    returned, skipped for a counted reason, or counted as failed. Reads the page it is handed; loads nothing,
    presses nothing, scrolls nothing, and never raises.
    """
    skipped = {reason: 0 for reason in SKIP_REASONS}
    failed: dict[str, int] = {}
    people: list[dict[str, Any]] = []
    returned: set[str] = set()
    headline_unread = 0

    try:
        cards = list(await page.locator(RESULT_CARD).element_handles())
    except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
        failed[type(exc).__name__] = 1
        cards = []
    to_read = min(len(cards), MAX_RESULTS_READ)

    for card in cards[:to_read]:
        try:
            verdict = await _read_card(card)
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            failed[kind] = failed.get(kind, 0) + 1
            continue
        if isinstance(verdict, str):
            skipped[verdict] += 1
            continue
        person, headline_read = verdict
        if person.link in returned:
            skipped["already_returned"] += 1
            continue
        returned.add(person.link)
        if not headline_read:
            headline_unread += 1
        people.append(person.envelope())

    return {
        "people": people,
        "people_denominators": {
            "result_cards_seen": len(cards),
            "result_cards_attempted": to_read,
            "people_returned": len(people),
            "skipped": skipped,
            "headline_unread": headline_unread,
            "failed": failed,
        },
    }
