"""His own ARTICLES list, off ``/in/me/recent-activity/articles/``. Census row ``M C48``.

The impure half is :func:`read_own_articles`: locator reads on the page the
caller already opened -- ``count``, ``get_attribute`` and ``inner_text`` -- so
no script is injected and no evaluate waiver is spent. It navigates nowhere
and takes no address; :data:`ARTICLES_URL` is a constant the tool loads, and
nothing on the page can change which page that is.

## WHAT THE PAGE DRAWS, MEASURED (lane B3, 2026-10-10)

On the live lane's session-1 capture (2026-09-23; the tracked skeleton is
``tests/fixtures/live1/articles.html``), LinkedIn SERVES the address and draws
the ALL-ACTIVITY shell, not an articles-specific view:

    main > section (one)          its heading is LinkedIn's "All activity"
      nav                         ONE filter pill, "Posts", to /recent-activity/all/
      [data-sdui-screen] (one)    the screen slot -- its screen name names
                                  articles and recent activity -- holding ONE
                                  container with no children at all

22 anchors on the page, 0 of them ``/pulse/``, no list, no list item and no
empty-state words anywhere in the section. So this reader keys on the
section's heading (a fixed LinkedIn word, :data:`ACTIVITY_HEADING`) and on the
screen slot (an attribute NAME, structure), never on a position.

## THE FIELDS

    readable   the page's own structure was found: exactly one section under
               the "All activity" heading, its filter nav, and exactly one
               screen slot in it
    articles   [{title, link}] -- each a ``/pulse/<one segment>/`` link drawn
               inside the slot. ``title`` is HIS OWN article's title, the
               link's text through ``people_data.sanitise`` (form only:
               invisible and direction characters out, whitespace collapsed)
               and cut at :data:`MAX_TITLE_CHARS`; ``link`` is the path only --
               host, query and fragment dropped, anything else refused
    count      len(articles)
    empty      True ONLY when the page's own screen slot is found and draws
               NOTHING an entry could be (:data:`CONTENT_SELECTOR`) -- the
               measured page. NEVER inferred from ``count == 0``: a slot that
               draws links which are not articles is not empty, and an
               unreadable page is never empty
    truncated  more ``/pulse/`` links than :data:`MAX_ARTICLES` were drawn

## WHAT IS DERIVED, AND WHAT IT CANNOT TELL YOU

**THE ENTRY SHAPE IS DERIVED. No capture shows an article**: he has published
none that any capture draws. An article is read as a ``/pulse/`` anchor inside
the screen slot because that is LinkedIn's article address and the slot is
where this page draws its entries; the positive path is tested on a copy of
the real skeleton with one synthetic anchor planted there. The first live
load of a page with an article is what turns this into a measurement.

**AN EMPTY SLOT IS WHAT THE PAGE DREW, AND A SLOT STILL STREAMING WOULD LOOK
THE SAME.** The capture was taken after the page settled; on the same
session's per-post analytics page the same kind of slot held 653 elements, so
an empty one here is the page's own drawing, read as such -- and stated as
the limit it is.
"""

from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from . import people_data
from .config import BASE_URL

#: The one address this reader is written for. ``/in/me/`` only: the
#: allowlist admits no other member's form.
ARTICLES_URL = f"{BASE_URL}/in/me/recent-activity/articles/"

#: LinkedIn's heading over the section, measured on the capture. A fixed
#: product word, kept verbatim in the tracked skeleton by its builder.
ACTIVITY_HEADING = "All activity"

#: The section, by its heading's accessible name.
SECTION_SELECTOR = "main section"

#: The filter nav's links into the activity family.
FILTER_SELECTOR = 'nav a[href*="/recent-activity/"]'

#: The page's SDUI screen slot: where the section draws its entries.
SLOT_SELECTOR = "[data-sdui-screen]"

#: Every link the slot draws, and the ones that may be articles.
LINK_SELECTOR = "a[href]"
ARTICLE_SELECTOR = 'a[href*="/pulse/"]'

#: Anything an entry could be. A slot holding none of these drew nothing.
CONTENT_SELECTOR = (
    "a, li, article, [role=list], [role=listitem], h1, h2, h3, h4, p, span, img, svg, button"
)

#: Bounds, so a page that draws something unexpected cannot stream it in.
MAX_ARTICLES = 50
MAX_TITLE_CHARS = people_data.CAPS["title"]
MAX_HREF_CHARS = 400

#: ``/pulse/<one segment>/``: LinkedIn's article address, one closed segment.
_PULSE_PATH = re.compile(r"^/pulse/([A-Za-z0-9._~%-]{1,200})/?$")

ROUTE = (
    "/pulse/ links inside the screen slot of the 'All activity' section of "
    "/in/me/recent-activity/articles/. The entry shape is derived: no capture "
    "has shown an article yet."
)


def link_of(href: Optional[str]) -> Optional[str]:
    """An article's ``/pulse/<segment>/`` path, or None. PURE; never raises.

    Relative, or absolute on ``https://www.linkedin.com`` only. Query and
    fragment dropped; one segment, closed alphabet, bounded.
    """
    if not isinstance(href, str) or not href or len(href) > MAX_HREF_CHARS:
        return None
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        if parts.scheme != "https" or parts.netloc != "www.linkedin.com":
            return None
    found = _PULSE_PATH.match(parts.path)
    if found is None:
        return None
    return "/pulse/" + found.group(1) + "/"


def title_of(text: Optional[str]) -> Optional[str]:
    """His article's title, sanitised in form and bounded, or None. PURE."""
    if not isinstance(text, str):
        return None
    cleaned = people_data.sanitise(text, cap=MAX_TITLE_CHARS)
    return cleaned or None


async def _count(locator: Any) -> int:
    try:
        return max(0, int(await locator.count()))
    except Exception:  # noqa: BLE001 -- a failed count is zero, never raised
        return 0


async def read_own_articles(page: Any) -> dict[str, Any]:
    """The reading, off the already-open articles page. Navigates nowhere.

    A locator call that fails is counted, never raised: an exception here
    could carry page text into an envelope.
    """
    reading: dict[str, Any] = {
        "readable": False,
        "articles": [],
        "count": 0,
        "empty": False,
        "truncated": False,
        "sections_matched": 0,
        "filter_links": 0,
        "slots_found": 0,
        "links_seen": 0,
        "not_article_links": 0,
        "unreadable_links": 0,
        "route": ROUTE,
    }
    section = page.locator(SECTION_SELECTOR).filter(
        has=page.get_by_role("heading", name=ACTIVITY_HEADING, exact=True)
    )
    reading["sections_matched"] = await _count(section)
    if reading["sections_matched"] != 1:
        return reading
    reading["filter_links"] = await _count(section.locator(FILTER_SELECTOR))
    slot = section.locator(SLOT_SELECTOR)
    reading["slots_found"] = await _count(slot)
    if reading["filter_links"] < 1 or reading["slots_found"] != 1:
        return reading
    reading["readable"] = True

    links = slot.locator(LINK_SELECTOR)
    reading["links_seen"] = await _count(links)
    candidates = slot.locator(ARTICLE_SELECTOR)
    drawn = await _count(candidates)
    articles: list[dict[str, str]] = []
    refused = 0
    for index in range(min(drawn, MAX_ARTICLES)):
        node = candidates.nth(index)
        try:
            href = await node.get_attribute("href")
            text = await node.inner_text()
        except Exception:  # noqa: BLE001
            reading["unreadable_links"] += 1
            continue
        link = link_of(href)
        title = title_of(text)
        if link is None or title is None:
            refused += 1
            continue
        articles.append({"title": title, "link": link})
    reading["articles"] = articles
    reading["count"] = len(articles)
    reading["truncated"] = drawn > MAX_ARTICLES
    # Links the slot drew that are not articles: every link outside the
    # /pulse/ selector, plus every /pulse/ candidate the closed shape refused.
    reading["not_article_links"] = max(0, reading["links_seen"] - drawn) + refused
    reading["empty"] = await _count(slot.locator(CONTENT_SELECTOR)) == 0
    return reading
