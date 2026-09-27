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
* THE PARAGRAPH'S PARENT HOLDS EXACTLY THREE ELEMENTS on all ten: the title
  paragraph and two lines with no link. The first ran 28 to 181 characters and
  carried a '|' or the word 'at' on all ten; the second was 27 characters,
  three words and a comma on all ten. The first is the HEADLINE; the second is
  the LOCATION, which is not a declared field.
* ELSEWHERE IN THE CARD, a sentence names MUTUAL CONNECTIONS, each a link to
  ANOTHER member -- one or two per card. They are people LinkedIn shows, and
  they are not results.
* The class names are generated hashes. Nothing here reads a class.

## WHAT IS READ, AND ALL THAT IS READ

    link      the card's own href, reduced by people_data.canonical_profile_link
    name      the NAME LINK's own text -- the first member link inside the card,
              required to point at the card's own member
    degree    the title paragraph's text beyond the name, reduced to the closed
              vocabulary by people_data.canonical_degree
    headline  the FIRST of EXACTLY TWO link-free lines beside the title. Any
              other count leaves it ABSENT and counted: with one line, nothing
              here can know whether it is a headline or a location, and a
              location read as a headline is a wrong answer given confidently

NEVER READ: the location line (its text never enters this process); the
mutual-connections sentence and every link in it; the hidden copy of the name
that labels the photo; any ``aria-label``, ``alt`` or ``title``; the Connect
control. The only attribute read is ``href``, and only of the card and of its
name link.

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
5. VISIBLE ONLY -- the name is what the name link draws. A result LinkedIn
   draws as "LinkedIn Member" comes back as exactly that, and nothing here
   looks anywhere else for who it was. A result drawn with NO member link is
   not read at all; no capture shows one, so nothing here claims how it looks.
6. NOT A TARGET BY ITSELF -- no write path in this package reaches this
   module, and a write takes a link or an id its caller names.

## WHAT IT DOES NOT CLAIM

That these are all the people the search matched (one page, as drawn, and a
search page lazy-loads); that a name is unique (two members can share one --
the link says which); or that the selectors fit a page drawn differently from
the capture. A page drawn another way comes back as ZERO people with the
denominators saying what was seen, never as a guess.
"""

from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce, people_data

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

#: The paragraph that holds the name link: its nearest ``p`` ancestor.
TITLE_BLOCK = "xpath=ancestor::p[1]"

#: The title paragraph's parent: the column the headline sits in.
COLUMN = "xpath=.."

#: A line with no link. The mutual-connections sentence carries links, so it
#: can never be one -- and it is not in the column anyway.
PLAIN_LINE = "p:not(:has(a))"

#: How many link-free lines the capture's column drew beside the title, on
#: all ten results: the headline, then the location.
CAPTURED_LINES = 2

#: The most results one call reads. The capture drew ten; the ceiling is a
#: budget above that, not a measurement of anything LinkedIn does.
MAX_RESULTS_READ = 25

#: How long one read may wait for its element. Every read is preceded by a
#: count, so this bounds a page that changed underneath the call rather than
#: the ordinary path; Playwright's own default is thirty seconds.
READ_TIMEOUT_MS = 2000

#: The closed reasons a card is not returned.
SKIP_REASONS: tuple[str, ...] = (
    "no_member_link",
    "title_is_another_member",
    "no_title_paragraph",
    "no_name",
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


async def _count(locator: Any) -> Optional[int]:
    """How many elements ``locator`` matches, or ``None`` if the answer was
    not an integer. Never raises for a bad answer and never quotes one."""
    return coerce.as_int(await locator.count())


async def read_result_people(page: Any) -> dict[str, Any]:
    """The people the results page draws, as people-record envelopes.

    Returns ``{"people": [<envelope>, ...], "people_denominators": {...}}``.
    Every string in ``people`` sits inside a :class:`people_data.Person`
    envelope; ``people_denominators`` holds integers and closed literals
    only. Reads the page it is handed; loads nothing, presses nothing,
    scrolls nothing.
    """
    skipped = {reason: 0 for reason in SKIP_REASONS}
    failed: dict[str, int] = {}
    people: list[dict[str, Any]] = []
    headline_unread = 0

    cards = page.locator(RESULT_CARD)
    seen = await _count(cards)
    to_read = min(seen, MAX_RESULTS_READ) if seen is not None else 0

    for index in range(to_read):
        try:
            card = cards.nth(index)
            link = people_data.canonical_profile_link(
                await card.get_attribute("href", timeout=READ_TIMEOUT_MS)
            )
            if link is None:
                skipped["no_member_link"] += 1
                continue
            title = card.locator(MEMBER_LINK).first
            title_link = people_data.canonical_profile_link(
                await title.get_attribute("href", timeout=READ_TIMEOUT_MS)
            )
            if title_link != link:
                skipped["title_is_another_member"] += 1
                continue
            block = title.locator(TITLE_BLOCK)
            if await _count(block) != 1:
                skipped["no_title_paragraph"] += 1
                continue
            name = await title.inner_text(timeout=READ_TIMEOUT_MS)
            degree = degree_beside(name, await block.inner_text(timeout=READ_TIMEOUT_MS))
            lines = block.locator(COLUMN).locator(PLAIN_LINE)
            headline = None
            if await _count(lines) == CAPTURED_LINES:
                headline = await lines.nth(0).inner_text(timeout=READ_TIMEOUT_MS)
            else:
                headline_unread += 1
            person = people_data.Person.from_page(
                name=name, headline=headline, href=link, degree=degree
            )
            if person is None:
                skipped["no_name"] += 1
                continue
            people.append(person.envelope())
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            failed[kind] = failed.get(kind, 0) + 1

    return {
        "people": people,
        "people_denominators": {
            "result_cards_seen": seen,
            "result_cards_read": to_read,
            "people_returned": len(people),
            "skipped": skipped,
            "headline_unread": headline_unread,
            "failed": failed,
        },
    }
