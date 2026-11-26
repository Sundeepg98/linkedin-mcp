"""Search LinkedIn POSTS by a keyword or a hashtag -- the content search vertical -- and read WHICH posts it found.

Census row ``M C93`` -- *search all of LinkedIn from the global search box,
the all-results page* -- served under D6 by this vertical, as the
orchestrator ruled.

## WHAT DECIDED IT

* ``CONTENT-VERTICAL-NOT-ALL-RESULTS`` (the orchestrator, 2026-10-10,
  ``_audit/2026-10-10-rulings-lane-a-questions.md`` section 5): "The hashtag
  row M C93 is served under D6 by the content vertical,
  /search/results/content/?keywords=<hashtag>, admitted by its own exact
  pattern under D1-SEARCH-AS-READS's three conditions with /all/ shown still
  refused; M C70 shares it, and post text returns under
  THIRD-PARTY-TEXT-AT-RUNTIME." The read boundary's own line for this address
  says the first tool that opens it lands with its reader in the same commit:
  this module is that reader, and :func:`compose` is the only code that
  builds the address.
* ``D1-SEARCH-AS-READS``'s three conditions: the keywords come from the tool's
  arguments only, never from a page; never an identifying value of the
  operator; at most five test searches a live session.
* ``NAMES-AT-RUNTIME`` and ``THIRD-PARTY-TEXT-AT-RUNTIME``: a read whose
  capability is WHICH items of other people's content returns them -- here a
  post's author as a person record and its words as untrusted text -- under
  the six ``PEOPLE-DATA-MITIGATIONS``, each enforced below.

## THE CAPTURE IT IS BUILT OVER, AND NOTHING ELSE

Live session 11 (2026-11-26, load 33): one content search for a generic
technology hashtag, served exact. Its tracked skeleton is
``tests/fixtures/live11/search_content.html``; the same skeleton with its
LinkedIn words measured against the session key and its people synthetic is
``tests/fixtures/live11/search_content_posts.html``
(``scripts/_build_content_search_skeleton.py``). MEASURED there:

* the page is LinkedIn's server-driven markup: every class is a generated
  hash, and nothing here reads one. The results sit inside ONE element whose
  ``data-sdui-screen`` names :data:`SCREEN_NAME`;
* THREE result cards, each an element with ``role="listitem"`` holding: one
  ``h2`` whose text is :data:`POST_HEADING`; three member links, all to ONE
  profile (the picture, the name block, a labelled link); the name block,
  which holds two paragraphs -- the author's name, then the degree line
  (``"• 3rd+"`` on all three); ONE words box,
  ``[data-testid="expandable-text-box"]``, holding the post's words and its
  hashtags (each a link to the mixed all-results page, which nothing here
  follows); ONE more control inside that box,
  ``[data-testid="expandable-text-button"]``, ``aria-hidden``, drawn as an
  ellipsis and ``more``; then the social bar (a reaction toggle, its menu,
  Comment, Repost, Send);
* NO PERMALINK: no card draws a ``/feed/update/`` link. The card's control
  menu -- labelled, by its keyed shape on all three cards, "Open control menu
  for post by" and the author's name -- is drawn closed and is never opened
  here. So a record's ``link`` is ``None``: this reader says WHICH posts by
  their author and their words, and cannot hand back an address for one;
* the filter bar draws Posts (checked), Sort by, Date posted, Content type,
  From member and All filters -- and no facet that restricts a search to a
  group (census ``M C70``, which this reader does NOT deliver).

## HOW IT READS

Every read is a locator scoped to one card, ``cards.nth(i)``, re-resolved at
each action, so a page that re-ranks while it is read could hand one card's
words to another card's author. The author's link is therefore read BEFORE
the words and AGAIN after them, and a card whose author moved meanwhile is
skipped and counted, never returned.

    the author   the ONE member link in the card, outside the words box,
                 that holds paragraphs: its first paragraph is the name, the
                 second the degree line, its href the profile -- and every
                 other member link in the card outside the box must name the
                 same profile, or the card is skipped
    the words    the words box's text, with the more control's own text cut
                 from its end; sanitised and cut at 3,000 characters by
                 ``people_data.Post``

NEVER READ: the headline, the time line, the Follow control and every
``aria-label`` (each names the author), any count in the social bar, any
picture's ``alt``. NOTHING IS PRESSED -- not the more control, not the
control menu, not a filter -- and no hashtag link is followed.

## AN EMPTY PAGE IS NOT AN EMPTY RESULT

No capture of an EMPTY content search exists, so this reader knows no empty
state. A page that draws the results screen and no card RAISES
``ExtractionFailedError`` instead of returning ``[]``, and so does a page that
does not draw the results screen at all: an uncorroborated zero is a broken
reading, never "no posts matched".

## THE SIX MITIGATIONS, WHERE EACH LIVES

1. DECLARED FIELDS ONLY -- a :class:`people_data.Post` envelope per result,
   its author a :class:`people_data.Person`; nothing else of a card crosses.
2. SANITISED AND MARKED -- ``Person.from_page`` and ``Post.from_page``.
3. NEVER STORED -- this module writes nothing and keeps no module-level
   container; a failure is counted by its exception's TYPE NAME, never its
   message, because a message can quote a page.
4. ONE PAGE -- it reads the page it is handed; the tool loads one. At most
   :data:`MAX_RESULTS_READ` cards per call, above the three the capture drew.
5. VISIBLE ONLY -- a card the page does not show is not read.
6. NOT A TARGET BY ITSELF -- no write path reaches this module, and a record
   carries no link a write could take.

## WHAT IT DOES NOT CLAIM

That these are all the posts the search matched (one page, as drawn, and the
page lazy-loads); that the words are whole where the more control is drawn
(whether the box holds the full text behind it is UNMEASURED, and
``more_controls_drawn`` counts the cards that draw one); or that the rules fit
a page drawn differently from the capture. A post by an organisation Page has
no record type with an organisation author yet (``people_data.Post`` needs a
member), so such a card is skipped and counted as ``no_member_author``.
"""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlencode, urlsplit

from linkedin_server import coerce, dom, jobfilter, people_data, people_search
from linkedin_server.errors import ExtractionFailedError

#: The one address this module composes, before its query. The read
#: boundary's exact line for the content vertical admits it with a query.
RESULTS_URL = "https://www.linkedin.com/search/results/content/"

#: The path a landing must keep to be the vertical this tool asked for.
RESULTS_PATH = "/search/results/content/"

#: MEASURED on the session-11 capture by keyed shape (see the module
#: docstring): the screen that holds the results, the heading every post
#: card draws, and the two test hooks inside a card.
SCREEN_NAME = "com.linkedin.sdui.flagshipnav.search.SearchResultsContent"
POST_HEADING = "Feed post"
SCREEN = f'[data-sdui-screen="{SCREEN_NAME}"]'
CARDS = SCREEN + ' [role="listitem"]'
HEADING = "h2"
WORDS_BOX = '[data-testid="expandable-text-box"]'
MORE_CONTROL = '[data-testid="expandable-text-button"]'
MEMBER_LINKS = 'a[href*="/in/"]'
PARAGRAPHS = "p"

#: The most cards one call reads: a budget above the three the capture drew.
MAX_RESULTS_READ = 25

#: Milliseconds any one read may wait: a card can vanish between its count
#: and its read, and Playwright would otherwise wait thirty seconds.
READ_TIMEOUT_MS = 2000

#: The closed reasons a card is not returned, in the order they are checked.
SKIP_REASONS: tuple[str, ...] = (
    "not_visible",
    "not_a_post",
    "not_one_words_box",
    "not_one_author_block",
    "more_than_one_profile",
    "no_member_author",
    "changed_while_read",
    "no_words",
)

#: Why a reading raised instead of returning, in this module's own words.
WHY_UNREADABLE: dict[str, str] = {
    "no_screen": (
        "The page did not draw the content search's results screen, so its "
        "cards cannot be told from anything else on the page. Nothing is "
        "reported as zero."
    ),
    "no_cards": (
        "The results screen drew no post card, and this reader knows no empty "
        "state for a content search (none has been captured), so the zero is "
        "not corroborated and is not reported as 'no posts matched'."
    ),
}


def compose(keywords: Any) -> dict[str, Any]:
    """The content search address for one keyword or hashtag, or a refusal.

    ``{"built": True, "url": <address>, "applied": {"keywords": 1}}`` or
    ``{"built": False, "argument": ..., "refused": ..., "saw": <shape>,
    "why": ...}``. The keyword goes through ``people_search.validated_keywords``
    -- the same budget and refusals every search vertical uses -- and is sent
    under the same key in the same encoding (a hashtag's ``#`` becomes
    ``%23``). No facet is taken: none of this vertical's facets is on record.

    PURE: arguments in, a dict out. It reads no page and never raises.
    """
    checked = people_search.validated_keywords(keywords)
    if not checked.get("ok"):
        return checked
    text = checked["text"]
    if not text:
        return {
            "built": False,
            "argument": "keywords",
            "refused": "keywords_required",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a content search is composed only WITH a keyword or a "
                "hashtag: the row it serves is a search, and the bare "
                "vertical is an address nobody has captured."
            ),
        }
    url = RESULTS_URL + "?" + urlencode([(people_search.KEYWORDS_KEY, text)])
    return {"built": True, "url": url, "applied": {"keywords": 1}}


def landed_on_the_vertical(landed: Any) -> bool:
    """Did the navigation stay on the content vertical? PURE."""
    path = urlsplit(str(landed or "")).path
    return path.rstrip("/") + "/" == RESULTS_PATH


async def _count(locator: Any) -> int:
    """A Playwright count, through the coercion gate every reader here uses."""
    return coerce.as_count(await locator.count())


async def _profile_of(link: Any) -> Optional[str]:
    return people_data.canonical_profile_link(
        await link.get_attribute("href", timeout=READ_TIMEOUT_MS)
    )


async def _member_links_outside_the_box(card: Any, box: Any) -> list[tuple[Any, Optional[str]]]:
    """``(link, profile)`` for each member link in the card, in document
    order, less as many as the words box holds for each profile -- a member
    MENTIONED in the words is not part of the author's block."""
    inside: list[Optional[str]] = []
    links = box.locator(MEMBER_LINKS)
    for index in range(await _count(links)):
        inside.append(await _profile_of(links.nth(index)))
    outside: list[tuple[Any, Optional[str]]] = []
    links = card.locator(MEMBER_LINKS)
    for index in range(await _count(links)):
        link = links.nth(index)
        profile = await _profile_of(link)
        if profile in inside:
            inside.remove(profile)
            continue
        outside.append((link, profile))
    return outside


async def _the_author_link(outside: list[tuple[Any, Optional[str]]]) -> Optional[tuple[Any, Optional[str]]]:
    """The ONE member link outside the box that holds paragraphs -- the name
    block -- or ``None`` when there is not exactly one."""
    blocks = [(link, profile) for link, profile in outside
              if await _count(link.locator(PARAGRAPHS)) >= 1]
    return blocks[0] if len(blocks) == 1 else None


def _cut_the_more_text(words: str, more: str) -> str:
    """The words with the more control's own text cut from their end."""
    if more and words.endswith(more):
        return words[: len(words) - len(more)].rstrip()
    return words


async def _read_card(card: Any) -> Any:
    """One card: a :class:`people_data.Post`, or the SKIP_REASONS entry that
    stopped it, and whether it draws a more control."""
    if not await card.is_visible():
        return "not_visible", False
    headings = card.locator(HEADING)
    if await _count(headings) != 1:
        return "not_a_post", False
    heading = people_data.sanitise(
        await headings.first.inner_text(timeout=READ_TIMEOUT_MS), cap=40
    )
    if heading != POST_HEADING:
        return "not_a_post", False
    boxes = card.locator(WORDS_BOX)
    if await _count(boxes) != 1:
        return "not_one_words_box", False
    box = boxes.first
    mores = box.locator(MORE_CONTROL)
    more_drawn = await _count(mores) == 1

    outside = await _member_links_outside_the_box(card, box)
    block = await _the_author_link(outside)
    if block is None:
        return "not_one_author_block", more_drawn
    author, profile = block
    if {named for _link, named in outside} != {profile}:
        return "more_than_one_profile", more_drawn
    paragraphs = author.locator(PARAGRAPHS)
    drawn = await _count(paragraphs)
    name = await paragraphs.first.inner_text(timeout=READ_TIMEOUT_MS)
    degree = (
        await paragraphs.nth(1).inner_text(timeout=READ_TIMEOUT_MS) if drawn >= 2 else None
    )
    person = people_data.Person.from_page(name=name, href=profile, degree=degree)
    if person is None or person.link is None:
        return "no_member_author", more_drawn

    words = people_data.sanitise(
        await box.inner_text(timeout=READ_TIMEOUT_MS), cap=4 * people_data.CAPS["text"]
    )
    if more_drawn:
        more = people_data.sanitise(
            await mores.first.inner_text(timeout=READ_TIMEOUT_MS), cap=40
        )
        words = _cut_the_more_text(words, more)

    # THE AUTHOR AGAIN, AFTER THE WORDS: a card the page reused meanwhile
    # would pair one post's words with another post's author.
    again = await _the_author_link(await _member_links_outside_the_box(card, box))
    if again is None or again[1] != profile:
        return "changed_while_read", more_drawn
    if not words:
        return "no_words", more_drawn
    post = people_data.Post.from_page(author=person, text=words)
    if post is None:
        return "no_member_author", more_drawn
    return post, more_drawn


async def read_content_results(page: Any) -> dict[str, Any]:
    """The posts a content search results page draws, as post records.

    Returns ``{"posts": [<envelope>, ...], "posts_denominators": {...}}``.
    Every string in ``posts`` sits inside a :class:`people_data.Post`
    envelope; ``posts_denominators`` holds integers, closed literals and
    exception TYPE names only. Reads the page it is handed; loads nothing,
    presses nothing, scrolls nothing.

    RAISES ``ExtractionFailedError`` -- never returns an empty list -- when
    the results screen is not drawn, or is drawn with no card at all: this
    reader knows no empty state, so such a zero is not corroborated.
    """
    # THE LANDING IS DESCRIBED, NEVER PUBLISHED: the ruling the dom readers
    # raise under (WITHHELD), and the same describer, in the hint.
    if await _count(page.locator(SCREEN)) != 1:
        raise ExtractionFailedError(WHY_UNREADABLE["no_screen"], hint=dom._landing_note(page))
    cards = page.locator(CARDS)
    seen = await _count(cards)
    if seen == 0:
        raise ExtractionFailedError(WHY_UNREADABLE["no_cards"], hint=dom._landing_note(page))
    skipped = {reason: 0 for reason in SKIP_REASONS}
    failed: dict[str, int] = {}
    posts: list[dict[str, Any]] = []
    more_controls = 0
    to_read = min(seen, MAX_RESULTS_READ)
    for index in range(to_read):
        try:
            verdict, more_drawn = await _read_card(cards.nth(index))
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            failed[kind] = failed.get(kind, 0) + 1
            continue
        if isinstance(verdict, str):
            skipped[verdict] += 1
            continue
        if more_drawn:
            more_controls += 1
        posts.append(verdict.envelope())
    return {
        "posts": posts,
        "posts_denominators": {
            "result_cards_seen": seen,
            "result_cards_attempted": to_read,
            "returned": len(posts),
            "skipped": skipped,
            "failed": failed,
            "more_controls_drawn": more_controls,
        },
    }
