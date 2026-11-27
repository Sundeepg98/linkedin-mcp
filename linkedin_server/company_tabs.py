"""Read ONE tab of an organisation's Page -- its About, Events, Insights or Life tab, or its posts.

Census rows ``J 106`` (*Company Page About tab (size, industry, locations)*)
and ``J 165`` (*Company Page Events tab: the events a company hosts*). Lane
readers-jobs26, 2026-11-26, over the live lane's session-11 captures of both
tabs (loads 20 and 21), tracked as ``tests/fixtures/live11/company_about.html``
and ``company_events.html`` and, with LinkedIn's words measured by keyed shape,
as ``company_about_words.html`` and ``company_events_words.html``
(``scripts/_build_live11_word_skeletons.py``). The Insights tab (``J 113``)
and the posts (``J 168``) joined on the same lane; the LIFE tab (``J 109``)
on lane build-jobs2, the same day, over session 11's capture of it (load 22),
``tests/fixtures/live11/company_life.html`` and ``company_life_words.html``
(``scripts/_build_jobs2_word_skeletons.py``).

## THE RULINGS IT READS UNDER

* THIRD-PARTY-TEXT-AT-RUNTIME (the orchestrator, 2026-10-10): an organisation
  Page's prose is returned at runtime as untrusted third-party text --
  sanitised, bounded, never stored -- under PEOPLE-DATA-MITIGATIONS. Every
  string of the Page's own that leaves here leaves inside a
  ``people_data.OrganisationProse`` record whose ``read_from`` names the fact
  it was read as (:data:`ABOUT_SOURCES`).
* NAMES-AT-RUNTIME (the operator, 2026-09-24): a read whose capability is
  WHICH items of other people's content returns them -- "the titles of groups
  and events". So each event leaves as a ``people_data.Event`` record, its
  title and its canonical link, and nothing else of the card: the
  attendee-count line, which can name a member ("<a member> and 12,345 others
  interested"), is never read.

## WHAT WAS MEASURED (session 11, by keyed shape)

THE ABOUT TAB. The Page's tab navigation marks ``About`` current
(``aria-current="page"``, its href's last segment ``about``). One ``h2``
reading ``Overview`` opens the Page's details card; the card holds ONE
paragraph (the description) and ONE definition list whose terms are each an
``h3`` inside a ``dt`` -- ``Website``, ``Verified page``, ``Industry``,
``Company size``, ``Headquarters``, ``Specialties`` -- each followed by its
``dd`` values (``Company size`` by two: the size band, then a link reading
``<n> associated members``). One ``h3`` elsewhere reads ``Locations (<n>)``.

THE EVENTS TAB. A sub-page with its own ``h2`` reading ``Events`` and no tab
navigation. Two cards, each opened by an ``h4``: ``Upcoming events`` -- on the
capture, with no event and the sentence ``<the Page's name> has no upcoming
events planned`` -- and ``Past events``, six event anchors to
``/events/<title>-<id>/``, each holding exactly two spans: the start
(``Tue, Nov 11, 2025, 3:30 PM`` in form) and the title. A button reading
``Show more events`` is drawn under the list; it is never pressed.

THE LIFE TAB. The Page navigation marks ``Life`` current. Each module carries
a ``data-view-name`` of LinkedIn's own (:data:`LIFE_MODULES`). The trending
module's ``h3`` reads ``Trending employee content`` over a carousel: ONE
wrapper article holding TWO item articles and eight empty slots. Each item
draws two links to its author's profile outside its words -- the picture,
and the name block, whose one ``aria-hidden`` span inside a ``dir`` span is
the name -- and ONE link to its permalink that holds its words (and, on one
item, a see-more control). An ``h3`` reading ``Company spotlights`` opens the section holding
three spotlights, each an ``h4`` title with ONE paragraph beside it (a second
paragraph sits inside the spotlight's video player). The photo module's
``h3`` reads ``Company photos`` over two drawn photos. The interest card
draws one button reading ``I<U+2019>m interested`` -- never pressed.

THE LIFE TAB'S PEOPLE are read under NAMES-AT-RUNTIME exactly as the content
search reads its cards (``content_search``): each trending item leaves as a
``people_data.Post`` whose author is a ``people_data.Person`` -- the name and
the profile link, read off the item's own header, re-read after the words so
a reused item cannot pair one post's words with another's author -- and its
canonical permalink and words. NEVER READ: the headline, the time line, the
degree line (not measured on this capture), any ``aria-label`` (each names
the author), the social counts, the featured members' cards (drawn empty).

## THE ZERO RULE

A tab that yields nothing is a finding only when the page corroborates it:
the Upcoming card's own sentence corroborates NO upcoming event, and nothing
corroborates an empty Past card or an About card with no recognised term.
An uncorroborated zero raises ``ExtractionFailedError`` -- in this module's
own words, never the page's -- so a broken read can never pass for "this
organisation has none". On the Life tab a page drawing none of its modules
raises; a trending carousel that has drawn no item yet answers ``posts``
``None`` -- unread -- never an empty list.

## THE PAGE MAY VETO, NEVER SUPPLY

Nothing read here becomes an address, an argument or a target. The one load
is composed by :func:`tab_url` from the caller's numeric organisation id and
a constant of this module, and :func:`landed_on_tab` only answers whether the
landing kept the tab. Every read is a locator read in the skeleton grammar --
tags, attributes, the descendant combinator, the parent step -- never a class
name and never a position: a heading is found by its words, a value by the
heading before it, a date span by its own form.

Nothing read off the page is logged, stored, or put into an exception: each
read is wrapped, a failure is COUNTED under ``reads_failed`` and its message
dropped (a Playwright error can quote the element it failed on).
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import company_page, dom, people_data
from linkedin_server.errors import ExtractionFailedError

#: The tabs this module reads, each with the path it is addressed by under
#: ``/company/<id>/``: its segment, and for the Insights tab the one query the
#: read boundary admits with it (exactly ``insightType=HEADCOUNT``, the value
#: LinkedIn drew). Closed: anything else is refused before any load.
#:
#: ``posts`` HAS NO SEGMENT OF ITS OWN (census ``J 168``, 2026-11-26): the read
#: boundary refuses ``/company/<x>/posts/``, and the admitted ROOT drew the
#: Posts view on 2026-10-10 (session 9), so the posts are read off the root.
TAB_SEGMENTS: dict[str, str] = {
    "about": "about",
    "events": "events",
    "insights": "insights",
    "life": "life",
    "posts": "",
    # Census J 111 (lane jobs7, 2026-11-27): the Products tab, admitted by
    # lane A on 2026-10-10 and captured by session 12's load 21.
    "products": "products",
}
TAB_QUERIES: dict[str, str] = {"insights": "?insightType=HEADCOUNT"}
TAB_PATHS: dict[str, str] = {
    tab: (segment + "/" if segment else "") + TAB_QUERIES.get(tab, "")
    for tab, segment in TAB_SEGMENTS.items()
}

#: Milliseconds any one read may wait; a node can vanish between a count and
#: its read, and Playwright would otherwise wait 30 s for it.
READ_TIMEOUT_MS = 2000

#: The most characters of one value carried into a record's builder: twice the
#: prose cap, so the record can tell a cut text from one that merely ended.
MAX_CHARS_CARRIED = 2 * people_data.PROSE_CAP

# ---------------------------------------------------------------------------
# The About tab's vocabulary, MEASURED on session 11's capture
# ---------------------------------------------------------------------------

#: The heading over the details card.
OVERVIEW_HEADING = "Overview"

#: The definition-list terms measured, each with the fact it is returned as.
#: A term not here is COUNTED and its values are never read.
ABOUT_TERMS: dict[str, str] = {
    "Website": "website",
    "Verified page": "verified_page",
    "Industry": "industry",
    "Company size": "company_size",
    "Headquarters": "headquarters",
    "Specialties": "specialties",
}

#: Facts returned as the Page's own text, in a record whose ``read_from``
#: says which. Each is one of ``people_data.PROSE_SOURCES``.
ABOUT_SOURCES: dict[str, str] = {
    "description": "about_overview",
    "website": "about_website",
    "industry": "about_industry",
    "headquarters": "about_headquarters",
    "specialties": "about_specialties",
}

#: LinkedIn's company-size bands, as the About tab writes them. A value that
#: is not one of these is withheld and counted, never quoted. MEASURED:
#: ``10,001+ employees``; the rest are the same field's fixed choices.
COMPANY_SIZE_BANDS: tuple[str, ...] = (
    "0-1 employees", "2-10 employees", "11-50 employees", "51-200 employees",
    "201-500 employees", "501-1,000 employees", "1,001-5,000 employees",
    "5,001-10,000 employees", "10,001+ employees",
)

_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December")
_LONG_DATE = re.compile(r"(%s) ([0-9]{1,2}), ([0-9]{4})" % "|".join(_MONTHS))
_ASSOCIATED = re.compile(r"([0-9]{1,3}(?:,[0-9]{3}){0,3}|[0-9]{1,12}) associated members?")
_LOCATIONS = re.compile(r"Locations \(([0-9]{1,3}(?:,[0-9]{3}){0,2}|[0-9]{1,9})\)")

# ---------------------------------------------------------------------------
# The Events tab's vocabulary, MEASURED
# ---------------------------------------------------------------------------

EVENTS_HEADING = "Events"
UPCOMING = "Upcoming events"
PAST = "Past events"
CARD_HEADINGS: dict[str, str] = {UPCOMING: "upcoming", PAST: "past"}
SHOW_MORE = "Show more events"

#: The Upcoming card's sentence when it holds no event. The Page's name opens
#: it; only the tail -- LinkedIn's words -- is compared, and nothing of it is
#: returned.
NO_UPCOMING_TAIL = " has no upcoming events planned"

_SHORT_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec")
_START = re.compile(
    r"(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), (%s) ([0-9]{1,2}), ([0-9]{4}), "
    r"([0-9]{1,2}):([0-9]{2}) (AM|PM)" % "|".join(_SHORT_MONTHS)
)

#: THE BOUNDS. Events kept per card; parts read at most on one page.
EVENTS_PER_CARD = 25
MAX_PARTS = 200


def collapsed(text: Any) -> str:
    """White space collapsed and the ends trimmed; ``""`` for a non-string."""
    return " ".join(text.split()) if isinstance(text, str) else ""


# ---------------------------------------------------------------------------
# The address, and the landing's veto
# ---------------------------------------------------------------------------


def tab_url(organisation_id: Any, tab: Any) -> dict[str, Any]:
    """The ONE tab address this module will load, or a refusal.

    Composed from ``company_page.company_page_url`` -- ten ASCII digits and
    nothing else, refused before any load otherwise -- and a constant of
    :data:`TAB_PATHS`. The refusal for an unknown tab names the tabs this
    reads and never repeats the value it was given.
    """
    if not isinstance(tab, str) or tab not in TAB_PATHS:
        return {
            "built": False,
            "refused": "unknown_tab",
            "why": "tab must be one of %s; the value given is not repeated." % sorted(TAB_PATHS),
        }
    root = company_page.company_page_url(organisation_id)
    if not root.get("built"):
        return root
    return {
        "built": True,
        "url": root["url"] + TAB_PATHS[tab],
        "identifier": root["identifier"],
        "tab": tab,
    }


_LINKEDIN_HOSTS = ("www.linkedin.com", "linkedin.com")


def landed_on_tab(landed: Any, tab: str) -> bool:
    """Whether a navigation LANDED on that tab of an organisation's Page.

    LinkedIn serves the numeric address by redirecting to the slug, so
    ``/company/<anything>/<tab>/`` is the tab; the unavailable-organisation
    page, the Page root and any other address are not, and the page is then
    not read. A yes or a no: nothing read here is returned.
    """
    if tab not in TAB_PATHS or not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc.lower() not in _LINKEDIN_HOSTS:
        return False
    path = parts.path or ""
    if path.startswith("/company/unavailable/"):
        return False
    if tab == "posts":
        # The root, or the Posts tab LinkedIn may redirect the root to.
        return bool(re.fullmatch(r"/company/[^/?#]{1,200}/(?:posts/?)?", path))
    segment = re.escape(TAB_SEGMENTS[tab])
    return bool(re.fullmatch(r"/company/[^/?#]{1,200}/%s/?" % segment, path))


# ---------------------------------------------------------------------------
# Reads, each wrapped: a failure is counted and its message dropped
# ---------------------------------------------------------------------------


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _text(locator: Any, failed: list[int]) -> Optional[str]:
    try:
        value = await locator.inner_text(timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def _attribute(locator: Any, name: str, failed: list[int]) -> Optional[str]:
    try:
        value = await locator.get_attribute(name, timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def _texts(locator: Any, failed: list[int], cap: int) -> list[Optional[str]]:
    total = min(await _count(locator, failed), cap)
    return [await _text(locator.nth(i), failed) for i in range(total)]


async def current_tab(page: Any, failed: list[int]) -> str:
    """The last path segment of the Page tab the page marks current, from a
    closed vocabulary; ``no_current_tab`` or ``tabs_disagree`` otherwise.

    MEASURED IN TWO FORMS: the Ember tabs mark one anchor
    ``aria-current="page"`` (session 11's About and Insights tabs); the SDUI
    Posts view marks ``aria-current="true"`` on TWO anchors to the same tab
    (session 9's root). Marked anchors that agree are one tab; anchors that
    name different tabs disagree, and nothing is chosen between them."""
    marked = page.locator('main nav a[aria-current="page"], main nav a[aria-current="true"]')
    total = await _count(marked, failed)
    if total == 0:
        return "no_current_tab"
    seen: set[str] = set()
    for index in range(min(total, 8)):
        href = await _attribute(marked.nth(index), "href", failed)
        try:
            segments = [s for s in urlsplit(href or "").path.split("/") if s]
        except ValueError:
            segments = []
        seen.add(segments[-1] if len(segments) >= 3 and segments[0] == "company" else "")
    if len(seen) != 1:
        return "tabs_disagree"
    last = seen.pop()
    return last if last in _TAB_WORDS else "unrecognised_tab"


#: The tab segments a Page's navigation draws, MEASURED on session 11's
#: captures of four tabs (``insights`` among them), plus the ones this
#: census names. A position here, never a page string, is what leaves.
_TAB_WORDS: tuple[str, ...] = (
    "about", "posts", "jobs", "life", "people", "insights", "events",
    "products", "services", "home", "videos",
)


def _prose_record(text: Optional[str], source: str) -> Optional[dict[str, Any]]:
    """One value of the Page's own, as a record's envelope, or ``None``."""
    if not isinstance(text, str):
        return None
    record = people_data.OrganisationProse.from_page(
        text=text[:MAX_CHARS_CARRIED],
        read_from=source,
        cut_before=len(text) > MAX_CHARS_CARRIED,
    )
    return None if record is None else record.envelope()


def _iso_long_date(text: Optional[str]) -> Optional[str]:
    found = _LONG_DATE.fullmatch(collapsed(text))
    if not found:
        return None
    month = _MONTHS.index(found.group(1)) + 1
    day, year = int(found.group(2)), int(found.group(3))
    if not 1 <= day <= 31:
        return None
    return "%04d-%02d-%02d" % (year, month, day)


def _grouped_int(text: str) -> int:
    return int(text.replace(",", ""))


# ---------------------------------------------------------------------------
# The About tab
# ---------------------------------------------------------------------------


async def read_about_tab(page: Any) -> dict[str, Any]:
    """The About tab ``page`` already shows: its description, its definition
    list's measured facts, and its locations count.

    Raises ``ExtractionFailedError`` when the tab drew no Overview card and no
    recognised fact -- a zero nothing on the page corroborates.
    """
    failed = [0]
    view = await current_tab(page, failed)
    out: dict[str, Any] = {
        "tab": "about",
        "view": view,
        "description": None,
        "facts": {},
        "company_size": None,
        "associated_members": None,
        "verified_on": None,
        "locations": None,
        "terms_unrecognised": 0,
        "values_withheld": 0,
        "overview_headings": 0,
        "paragraphs_in_card": 0,
    }
    headings = page.locator("main h2")
    texts = await _texts(headings, failed, MAX_PARTS)
    overview = [i for i, t in enumerate(texts) if collapsed(t) == OVERVIEW_HEADING]
    out["overview_headings"] = len(overview)
    if len(overview) == 1:
        card = headings.nth(overview[0]).locator("xpath=..")
        await _read_about_card(card, out, failed)
    for text in await _texts(page.locator("main h3"), failed, MAX_PARTS):
        found = _LOCATIONS.fullmatch(collapsed(text))
        if found:
            out["locations"] = (
                _grouped_int(found.group(1)) if out["locations"] is None else out["locations"]
            )
    out["reads_failed"] = failed[0]
    if out["description"] is None and not out["facts"] and out["company_size"] is None:
        raise ExtractionFailedError(
            "the About tab yielded no Overview card and no recognised fact, and "
            "nothing on the page says the organisation has none; reporting an "
            "empty About tab here would be indistinguishable from a broken read "
            f"(view read {view!r}, {out['overview_headings']} Overview heading(s)).",
            hint=dom._landing_note(page),
        )
    return out


async def _read_about_card(card: Any, out: dict[str, Any], failed: list[int]) -> None:
    # THE CARD NESTS ANOTHER CARD. Measured: inside the details card sits the
    # Page's "interested in working here" section, a ``section`` of its own
    # with its own paragraph. So the description is the ONE paragraph of the
    # card that no nested section holds -- found by subtracting what the
    # nested sections hold, compared as text, never by its position.
    every = await _texts(card.locator("p"), failed, MAX_PARTS)
    nested = await _texts(card.locator("section p"), failed, MAX_PARTS)
    remaining = list(every)
    for text in nested:
        if text in remaining:
            remaining.remove(text)
    own = [t for t in remaining if collapsed(t)]
    out["paragraphs_in_card"] = len(own)
    if len(own) == 1:
        out["description"] = _prose_record(own[0], ABOUT_SOURCES["description"])
    parts = card.locator("dl dt, dl dd")
    total = min(await _count(parts, failed), MAX_PARTS)
    term: Optional[str] = None
    values: dict[str, list[Any]] = {}
    for index in range(total):
        part = parts.nth(index)
        if await _count(part.locator("h3"), failed):
            word = collapsed(await _text(part.locator("h3").nth(0), failed))
            term = ABOUT_TERMS.get(word)
            if term is None:
                out["terms_unrecognised"] += 1
            continue
        if term is None:
            continue
        values.setdefault(term, []).append(part)
    for term, cells in values.items():
        await _read_about_fact(term, cells, out, failed)


async def _read_about_fact(term: str, cells: list[Any], out: dict[str, Any], failed: list[int]) -> None:
    first = await _text(cells[0], failed)
    if term == "company_size":
        band = collapsed(first)
        if band in COMPANY_SIZE_BANDS:
            out["company_size"] = band
        else:
            out["values_withheld"] += 1
        # The second value is a link beside a tooltip of LinkedIn's own words,
        # so the LINK's text is read, never the cell's.
        for cell in cells[1:]:
            links = cell.locator("a")
            if await _count(links, failed) != 1:
                continue
            found = _ASSOCIATED.fullmatch(collapsed(await _text(links.nth(0), failed)))
            if found:
                out["associated_members"] = _grouped_int(found.group(1))
        return
    if term == "verified_page":
        out["verified_on"] = _iso_long_date(first)
        if out["verified_on"] is None:
            out["values_withheld"] += 1
        return
    record = _prose_record(first, ABOUT_SOURCES[term])
    if record is None:
        out["values_withheld"] += 1
        return
    out["facts"][term] = record


# ---------------------------------------------------------------------------
# The Events tab
# ---------------------------------------------------------------------------


def _iso_start(text: Optional[str]) -> Optional[str]:
    found = _START.fullmatch(collapsed(text))
    if not found:
        return None
    month = _SHORT_MONTHS.index(found.group(1)) + 1
    day, year = int(found.group(2)), int(found.group(3))
    hour, minute = int(found.group(4)), int(found.group(5))
    if not (1 <= day <= 31 and 1 <= hour <= 12 and 0 <= minute <= 59):
        return None
    hour = hour % 12 + (12 if found.group(6) == "PM" else 0)
    return "%04d-%02d-%02dT%02d:%02d" % (year, month, day, hour, minute)


async def read_events_tab(page: Any) -> dict[str, Any]:
    """The Events tab ``page`` already shows: each card's events, as records.

    Raises ``ExtractionFailedError`` when no event was read and the page does
    not say the organisation has none.
    """
    failed = [0]
    headings = await _texts(page.locator("main h2"), failed, MAX_PARTS)
    out: dict[str, Any] = {
        "tab": "events",
        "events_headings": sum(1 for t in headings if collapsed(t) == EVENTS_HEADING),
        "cards": {},
        "cards_unrecognised": 0,
        "events_withheld": 0,
        "more_offered": False,
    }
    card_headings = page.locator("main h4")
    for index, text in enumerate(await _texts(card_headings, failed, MAX_PARTS)):
        key = CARD_HEADINGS.get(collapsed(text))
        if key is None:
            out["cards_unrecognised"] += 1
            continue
        if key in out["cards"]:
            out["cards_unrecognised"] += 1
            continue
        card = card_headings.nth(index).locator("xpath=..")
        out["cards"][key] = await _read_company_event_card(card, key, out, failed)
    buttons = await _texts(page.locator("main button"), failed, MAX_PARTS)
    out["more_offered"] = any(collapsed(t) == SHOW_MORE for t in buttons)
    out["reads_failed"] = failed[0]
    read = sum(len(card["events"]) for card in out["cards"].values())
    corroborated = any(card.get("none_planned") for card in out["cards"].values())
    if read == 0 and not corroborated:
        raise ExtractionFailedError(
            "the Events tab yielded no event and no card that says the "
            "organisation has none; an empty answer here would be "
            "indistinguishable from a broken read "
            f"({out['events_headings']} Events heading(s), "
            f"{len(out['cards'])} recognised card(s)).",
            hint=dom._landing_note(page),
        )
    return out


async def _read_company_event_card(card: Any, key: str, out: dict[str, Any], failed: list[int]) -> dict[str, Any]:
    anchors = card.locator('a[href*="/events/"]')
    total = await _count(anchors, failed)
    events: list[dict[str, Any]] = []
    for index in range(min(total, EVENTS_PER_CARD)):
        anchor = anchors.nth(index)
        link = people_data.canonical_event_link(await _attribute(anchor, "href", failed))
        spans = await _texts(anchor.locator("span"), failed, 8)
        starts = [_iso_start(t) for t in spans]
        dated = [i for i, s in enumerate(starts) if s is not None]
        others = [t for i, t in enumerate(spans) if i not in dated and collapsed(t)]
        if link is None or len(dated) != 1 or len(others) != 1:
            out["events_withheld"] += 1
            continue
        record = people_data.Event.from_page(title=others[0], href=link)
        if record is None:
            out["events_withheld"] += 1
            continue
        events.append({"event": record.envelope(), "starts": starts[dated[0]]})
    none_planned = False
    if key == "upcoming" and total == 0:
        for text in await _texts(card.locator("p"), failed, 20):
            line = collapsed(text)
            if line.endswith(NO_UPCOMING_TAIL) and len(line) > len(NO_UPCOMING_TAIL):
                none_planned = True
    return {
        "events": events,
        "anchors_seen": total,
        "beyond_bound": max(0, total - EVENTS_PER_CARD),
        "none_planned": none_planned,
    }


# ---------------------------------------------------------------------------
# The Insights tab (Premium), at insightType=HEADCOUNT
# ---------------------------------------------------------------------------

#: The modules the tab drew, by the heading LinkedIn writes over each,
#: MEASURED on session 11's capture (load 19). A heading not here is counted.
INSIGHT_MODULES: dict[str, str] = {
    "Hiring trends": "hiring_trends",
    "Total job openings": "total_job_openings",
    # Session 12's load 20 (lane jobs7, 2026-11-27): the page scrolled to its
    # foot draws three more Premium modules, each under its own h2.
    "Total employee count": "total_employee_count",
    "Employee distribution and headcount growth by function": "headcount_growth_by_function",
    "Notable company alumni": "notable_company_alumni",
}

#: THE SCREEN-READER DATA TABLES LinkedIn draws beside the Insights charts,
#: CHOSEN BY THE SUMMARY EACH CARRIES -- NEVER BY ITS HEADER WORDS. Each
#: summary names the field its rows are returned under, and the field each
#: header word is read as THERE. A table is read only when it carries the
#: two required headers; a header not in its map leaves its column unread.
#:
#: WHY THE SUMMARY AND NOT THE HEADERS (J114-READS-ITS-OWN-TABLE, the
#: orchestrator, 2026-11-27, on lane jobs7's finding). LinkedIn heads BOTH
#: function tables ``Function``, ``Number of employees`` and ``Percentage of
#: total headcount``. MEASURED by keyed shape:
#:
#: * session 11's load 19 (``tests/fixtures/live11/company_insights_headcount.html``)
#:   draws ONE such table, summarised ``Total job openings`` under that
#:   module heading;
#: * session 12's load 20 (``tests/fixtures/live12/c_rj26_1_functions-open.html``)
#:   draws it AND one summarised ``Headcount growth by function``, under the
#:   heading ``Employee distribution and headcount growth by function``.
#:   For each of the 10 functions in both, the openings count has one or two
#:   fewer digits than the headcount.
#:
#: A table chosen by its headers returned job openings as employee counts on
#: the first page, and read neither table on the second. Under the openings
#: summary, the same header words mean the function's openings and its
#: share of them.
FUNCTION_TABLES: dict[str, tuple[str, dict[str, str]]] = {
    # Census row J 114: distribution and headcount growth by function.
    "Headcount growth by function": ("functions", {
        "Function": "function",
        "Number of employees": "employees",
        "Percentage of total headcount": "share_of_headcount_percent",
        "3 month growth": "growth_3_months_percent",
        "6 month growth": "growth_6_months_percent",
        "1 year growth": "growth_1_year_percent",
    }),
    # Census row J 174: job openings by function.
    "Total job openings": ("openings_by_function", {
        "Function": "function",
        "Number of employees": "openings",
        "Percentage of total headcount": "share_of_openings_percent",
        "3 month growth": "growth_3_months_percent",
        "6 month growth": "growth_6_months_percent",
        "1 year growth": "growth_1_year_percent",
    }),
}
_REQUIRED_HEADERS = ("Function", "Number of employees")

#: Why a function field came back empty, in closed words:
#:
#: * no table carries its summary;
#: * more than one does, so neither copy is read;
#: * its table draws no ``Function`` or no ``Number of employees`` header;
#: * every row was withheld.
FUNCTION_TABLE_UNREAD: tuple[str, ...] = (
    "no_table_with_this_summary",
    "more_than_one_table_with_this_summary",
    "required_headers_not_drawn",
    "every_row_withheld",
)

#: HEADCOUNT OVER TIME (census row J 169), as the page draws it in text: the
#: table LinkedIn summarises ``Total employee count``, under that module
#: heading. MEASURED by keyed shape on session 12's load 20:
#:
#: * ONE data row of four cells, each naming its header through its
#:   ``headers`` attribute;
#: * the headers ``total employees`` (LinkedIn's own lower case), ``6m
#:   growth``, ``1y growth`` and ``2y growth``;
#: * the data row drawn ABOVE the header row, and neither inside a ``tbody``.
#:
#: The module's monthly chart is not drawn as text, so the total and its
#: growth over three spans is what is read.
HEADCOUNT_SUMMARY = "Total employee count"
HEADCOUNT_SUMMARY_HEADERS: dict[str, str] = {
    "total employees": "employees",
    "6m growth": "growth_6_months_percent",
    "1y growth": "growth_1_year_percent",
    "2y growth": "growth_2_years_percent",
}

#: NOTABLE ALUMNI (census row J 169): the module LinkedIn heads ``Notable
#: company alumni``, a carousel of member cards. MEASURED on load 20: four
#: cards are drawn, three of them with a name link, a degree line and a
#: current-role line.
#:
#: * It is read ONLY when the module's own heading is drawn.
#: * Each card becomes a ``people_data.Person`` under NAMES-AT-RUNTIME:
#:   declared fields only, sanitised, bounded, never stored.
#: * A card with no single name is withheld and counted.
#: * The carousel's Next button is never pressed: only the cards the page
#:   drew are read.
ALUMNI_CARD = 'div[class="org-notable-alumni-card"]'
ALUMNI_NAME_LINK = 'a[class*="org-notable-alumni-card__alumni-name"]'
ALUMNI_NAME = ALUMNI_NAME_LINK + ' span[aria-hidden="true"]'
ALUMNI_DEGREE = 'p[class*="org-notable-alumni-card__degree"]'
ALUMNI_CURRENT_ROLE = (
    'div[class="org-notable-alumni-card__current-alumni-detail"] '
    'p[class*="org-notable-alumni-card__alumni-title"]'
)
ALUMNI_BOUND = 12

#: Why the alumni came back empty, in closed words: the module's heading is
#: not drawn; it is drawn with no card; every card drawn was withheld.
ALUMNI_UNREAD: tuple[str, ...] = (
    "module_heading_not_drawn",
    "no_alumni_card_drawn",
    "every_card_withheld",
)

#: LinkedIn's job-function taxonomy -- a fixed list of LinkedIn's own words,
#: not a Page's. Eleven were drawn on the capture; the rest are the same
#: field's fixed choices. A row whose function is not one of these is
#: withheld and counted, so no text the page chose can leave as a function.
JOB_FUNCTIONS: tuple[str, ...] = (
    "Accounting", "Administrative", "Arts and Design", "Business Development",
    "Community and Social Services", "Consulting", "Customer Success and Support",
    "Education", "Engineering", "Entrepreneurship", "Finance", "Healthcare Services",
    "Human Resources", "Information Technology", "Legal", "Marketing",
    "Media and Communication", "Military and Protective Services", "Operations",
    "Product Management", "Program and Project Management", "Purchasing",
    "Quality Assurance", "Real Estate", "Research", "Sales", "Support",
)

#: A growth cell's screen-reader words, MEASURED: ``75% increase`` and
#: ``-35% decrease``. The sign must agree with the word or the cell is withheld.
_GROWTH = re.compile(r"(-?[0-9]{1,4})% (increase|decrease)")
_PLAIN_INT = re.compile(r"[0-9]{1,3}(?:,[0-9]{3}){0,3}|[0-9]{1,12}")
FUNCTION_ROWS = 40


def _growth(text: Optional[str]) -> Optional[int]:
    found = _GROWTH.search(collapsed(text))
    if not found:
        return None
    value = int(found.group(1))
    if (found.group(2) == "decrease") != (value < 0):
        return None
    return value


def _cell_value(key: str, text: Optional[str]) -> Any:
    line = collapsed(text)
    if key == "function":
        return line if line in JOB_FUNCTIONS else None
    if key.startswith("growth_"):
        return _growth(text)
    if _PLAIN_INT.fullmatch(line):
        value = _grouped_int(line)
        if key.startswith("share_") and value > 100:
            return None
        return value
    return None


async def _read_function_table(
    page: Any, summary: str, headers_map: dict[str, str], out: dict[str, Any], failed: list,
) -> tuple[list[dict[str, Any]], Optional[str]]:
    """The rows of the ONE table carrying ``summary``, and why there are
    none (a word of :data:`FUNCTION_TABLE_UNREAD`) when there are none."""
    tables = page.locator(f'main table[summary="{summary}"]')
    drawn = await _count(tables, failed)
    if drawn == 0:
        return [], "no_table_with_this_summary"
    if drawn > 1:
        return [], "more_than_one_table_with_this_summary"
    table = tables.nth(0)
    heads = table.locator("th")
    headers = [collapsed(t) for t in await _texts(heads, failed, 12)]
    if not all(h in headers for h in _REQUIRED_HEADERS):
        return [], "required_headers_not_drawn"
    count_key = headers_map["Number of employees"]
    # A CELL BELONGS TO THE HEADER ITS OWN ``headers`` ATTRIBUTE NAMES -- the
    # table's own accessibility wiring, measured on every cell of both
    # captures -- never to the header at the same position.
    column: dict[str, str] = {}
    for index, word in enumerate(headers):
        key = headers_map.get(word)
        ident = await _attribute(heads.nth(index), "id", failed)
        if key is None or not ident:
            out["headers_unread"] += 1
            continue
        column[ident] = key
    found: list[dict[str, Any]] = []
    rows = table.locator("tbody tr")
    for index in range(min(await _count(rows, failed), FUNCTION_ROWS)):
        cells = rows.nth(index).locator("td")
        row: dict[str, Any] = {}
        for cell_index in range(min(await _count(cells, failed), 12)):
            cell = cells.nth(cell_index)
            key = column.get(await _attribute(cell, "headers", failed) or "")
            if key is not None and key not in row:
                row[key] = _cell_value(key, await _text(cell, failed))
        if row.get("function") is None or row.get(count_key) is None:
            out["rows_withheld"] += 1
            continue
        found.append(row)
    return found, (None if found else "every_row_withheld")


async def _read_headcount_summary(
    page: Any, failed: list,
) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    """The headcount summary's one reading, and why there is none when there
    is none (a word of :data:`FUNCTION_TABLE_UNREAD`)."""
    tables = page.locator(f'main table[summary="{HEADCOUNT_SUMMARY}"]')
    drawn = await _count(tables, failed)
    if drawn == 0:
        return None, "no_table_with_this_summary"
    if drawn > 1:
        return None, "more_than_one_table_with_this_summary"
    table = tables.nth(0)
    heads = table.locator("th")
    column: dict[str, str] = {}
    for index in range(min(await _count(heads, failed), 8)):
        key = HEADCOUNT_SUMMARY_HEADERS.get(collapsed(await _text(heads.nth(index), failed)))
        ident = await _attribute(heads.nth(index), "id", failed)
        if key is not None and ident:
            column[ident] = key
    if "employees" not in column.values():
        return None, "required_headers_not_drawn"
    reading: dict[str, Any] = {key: None for key in HEADCOUNT_SUMMARY_HEADERS.values()}
    seen: set[str] = set()
    # A CELL BELONGS TO THE HEADER ITS OWN ``headers`` ATTRIBUTE NAMES, as in
    # the function tables; here the data row is drawn above the header row.
    cells = table.locator("td[headers]")
    for index in range(min(await _count(cells, failed), 8)):
        cell = cells.nth(index)
        key = column.get(await _attribute(cell, "headers", failed) or "")
        if key is not None and key not in seen:
            seen.add(key)
            reading[key] = _cell_value(key, await _text(cell, failed))
    if reading["employees"] is None:
        return None, "every_row_withheld"
    return reading, None


async def _read_alumni(page: Any, failed: list) -> dict[str, Any]:
    """Each notable alumni card the page drew, as a person record: the
    records, the cards withheld, the cards past the bound, and why there is
    no record when there is none (:data:`ALUMNI_UNREAD`). The caller reads
    the cards only under the module's own heading."""
    reading: dict[str, Any] = {"records": [], "withheld": 0, "beyond_bound": 0, "unread": None}
    cards = page.locator(f"main {ALUMNI_CARD}")
    total = await _count(cards, failed)
    if total == 0:
        reading["unread"] = "no_alumni_card_drawn"
        return reading
    for index in range(min(total, ALUMNI_BOUND)):
        card = cards.nth(index)
        names = card.locator(ALUMNI_NAME)
        links = card.locator(ALUMNI_NAME_LINK)
        if await _count(names, failed) != 1 or await _count(links, failed) != 1:
            reading["withheld"] += 1
            continue
        degrees = card.locator(ALUMNI_DEGREE)
        roles = card.locator(ALUMNI_CURRENT_ROLE)
        person = people_data.Person.from_page(
            name=await _text(names.nth(0), failed),
            headline=(await _text(roles.nth(0), failed)
                      if await _count(roles, failed) == 1 else None),
            href=await _attribute(links.nth(0), "href", failed),
            degree=(await _text(degrees.nth(0), failed)
                    if await _count(degrees, failed) == 1 else None),
        )
        if person is None:
            reading["withheld"] += 1
            continue
        reading["records"].append(person.envelope())
    reading["beyond_bound"] = max(0, total - ALUMNI_BOUND)
    if not reading["records"]:
        reading["unread"] = "every_card_withheld"
    return reading


async def read_insights_tab(page: Any) -> dict[str, Any]:
    """The Insights tab ``page`` already shows: the modules it drew, and the
    rows of its two function tables, EACH CHOSEN BY ITS SUMMARY
    (:data:`FUNCTION_TABLES`). ``functions`` comes from the table summarised
    ``Headcount growth by function``: each function of LinkedIn's taxonomy,
    its employee count, its share of headcount and its growth.
    ``openings_by_function`` comes from the table summarised ``Total job
    openings``: each function, its job openings, its share of them and their
    growth. A field with no row says why in ``<field>_unread``
    (:data:`FUNCTION_TABLE_UNREAD`); both are None when rows were read.

    ``headcount`` comes from the table summarised ``Total employee count``:
    the total and its growth over 6 months, 1 year and 2 years
    (:data:`HEADCOUNT_SUMMARY_HEADERS`). When there is no reading it is None,
    and ``headcount_unread`` says why. ``notable_alumni`` is each member card
    under the module heading ``Notable company alumni``, as a person record
    (NAMES-AT-RUNTIME). ``alumni_withheld`` counts the cards not returned,
    and ``notable_alumni_unread`` says why when none is (:data:`ALUMNI_UNREAD`).

    Raises ``ExtractionFailedError`` when it reads no known module, no row of
    either table, no headcount and no alumni card.
    """
    failed = [0]
    out: dict[str, Any] = {
        "tab": "insights",
        "view": await current_tab(page, failed),
        "modules": [],
        "modules_unrecognised": 0,
        "functions": [],
        "functions_unread": None,
        "openings_by_function": [],
        "openings_by_function_unread": None,
        "rows_withheld": 0,
        "headers_unread": 0,
        "headcount": None,
        "headcount_unread": None,
        "notable_alumni": [],
        "notable_alumni_unread": None,
        "alumni_withheld": 0,
        "alumni_beyond_bound": 0,
    }
    for text in await _texts(page.locator("main h2"), failed, MAX_PARTS):
        key = INSIGHT_MODULES.get(collapsed(text))
        if key is not None and key not in out["modules"]:
            out["modules"].append(key)
    for summary, (field, headers_map) in FUNCTION_TABLES.items():
        rows, unread = await _read_function_table(page, summary, headers_map, out, failed)
        out[field] = rows
        out[field + "_unread"] = unread
    out["headcount"], out["headcount_unread"] = await _read_headcount_summary(page, failed)
    # THE ALUMNI ARE READ ONLY UNDER THEIR OWN HEADING: a card class alone is
    # not the module.
    if "notable_company_alumni" in out["modules"]:
        alumni = await _read_alumni(page, failed)
        out["notable_alumni"] = alumni["records"]
        out["alumni_withheld"] = alumni["withheld"]
        out["alumni_beyond_bound"] = alumni["beyond_bound"]
        out["notable_alumni_unread"] = alumni["unread"]
    else:
        out["notable_alumni_unread"] = "module_heading_not_drawn"
    out["reads_failed"] = failed[0]
    if (not out["functions"] and not out["openings_by_function"] and not out["modules"]
            and out["headcount"] is None and not out["notable_alumni"]):
        raise ExtractionFailedError(
            "the Insights tab yielded no known module and no row of either "
            "function table; an empty answer here would be indistinguishable "
            "from a broken read (the headcount table: "
            f"{out['functions_unread']}; the openings table: "
            f"{out['openings_by_function_unread']}).",
            hint=dom._landing_note(page),
        )
    return out


# ---------------------------------------------------------------------------
# The Page's posts (J 168), read off the Page ROOT
# ---------------------------------------------------------------------------

#: The accessible heading LinkedIn draws over every feed item, MEASURED by
#: lane B4 (``company_home.FEED_ITEM_HEADING``): thirteen on session 9's Posts
#: view, one on the 2026-09-23 Home view.
FEED_ITEM_HEADING = "Feed post"

#: The text box's hook on a feed item, MEASURED on session 9's Posts view:
#: thirteen items, eleven holding one box, one holding none, one two.
TEXT_BOX = '[data-testid="expandable-text-box"]'

#: Feed items read at most on one page: the thirteen drawn, with room.
POSTS_PER_PAGE = 40


async def read_posts_tab(page: Any) -> dict[str, Any]:
    """The Page's own posts, off the Page root ``page`` already shows.

    THE ROOT, NOT THE TAB: the read boundary refuses ``/company/<x>/posts/``,
    and on 2026-10-10 the admitted root address drew the Posts view itself
    (lane B4's capture, session 9). So the tool loads the root, and this says
    which view it read before anything else.

    Each feed item -- a ``role="listitem"`` holding exactly one ``h2``
    reading ``Feed post`` -- comes back as its words in a
    ``people_data.OrganisationProse`` record (``read_from`` ``page_post``)
    when it holds exactly ONE text box. An item with no box is a post without
    words and is counted; an item with two -- a reshare, whose second box is
    the reshared post's own words, possibly a member's -- is counted and NOT
    read. No item's link is returned: the Posts view draws no permalink on
    an item. Raises ``ExtractionFailedError`` when no feed item is read.
    """
    failed = [0]
    out: dict[str, Any] = {
        "tab": "posts",
        "view": await current_tab(page, failed),
        "posts": [],
        "items_seen": 0,
        "posts_without_text": 0,
        "posts_with_several_text_boxes": 0,
        "items_beyond_bound": 0,
    }
    items = page.locator('main div[role="listitem"]')
    total = await _count(items, failed)
    for index in range(min(total, MAX_PARTS)):
        item = items.nth(index)
        heads = [collapsed(t) for t in await _texts(item.locator("h2"), failed, 6)]
        if heads.count(FEED_ITEM_HEADING) != 1:
            continue
        out["items_seen"] += 1
        if len(out["posts"]) >= POSTS_PER_PAGE:
            out["items_beyond_bound"] += 1
            continue
        boxes = item.locator(TEXT_BOX)
        found = await _count(boxes, failed)
        if found == 0:
            out["posts_without_text"] += 1
            continue
        if found > 1:
            out["posts_with_several_text_boxes"] += 1
            continue
        record = _prose_record(await _text(boxes.nth(0), failed), "page_post")
        if record is None:
            out["posts_without_text"] += 1
            continue
        out["posts"].append(record)
    out["reads_failed"] = failed[0]
    if out["items_seen"] == 0:
        raise ExtractionFailedError(
            "the Page root drew no feed item this reader knows; an empty list "
            "here would be indistinguishable from a broken read "
            f"(view read {out['view']!r}).",
            hint=dom._landing_note(page),
        )
    return out


# ---------------------------------------------------------------------------
# The Life tab (J 109)
# ---------------------------------------------------------------------------

#: The modules a Life tab draws, each by the ``data-view-name`` LinkedIn gives
#: it, MEASURED on session 11's capture (load 22): one hero video, one
#: featured-members module (its three cards drawn empty), one trending
#: carousel, one interest card, three spotlights and one photo carousel. Each
#: is COUNTED by its key; only the trending items, the spotlights, the photo
#: count and the interest button are read.
LIFE_MODULES: dict[str, str] = {
    "hero_media": "org-member-life-hero-image",
    "featured_members": "org-member-life-page-featured-members",
    "trending_employee_content": "org-member-life-trending-employee-content",
    "interest_pipeline": "org-member-life-interest-pipeline",
    "company_spotlight": "org-member-life-company-spotlight",
    "company_photos": "org-member-life-company-photos",
}

#: The headings each read section is corroborated by, MEASURED by keyed shape:
#: the trending carousel's own ``h3``, the ``h3`` that opens the section the
#: spotlights sit in, and the photo carousel's own ``h3``. A section whose
#: heading does not read exactly so is NOT READ, whatever its module name.
TRENDING_HEADING = "Trending employee content"
SPOTLIGHTS_HEADING = "Company spotlights"
PHOTOS_HEADING = "Company photos"

#: The interest button, by its module name and its text, MEASURED (LinkedIn's
#: curly apostrophe, built with ``chr`` so this file stays ASCII). Reported
#: drawn, NEVER PRESSED: it tells the Page's recruiters he is interested.
INTERESTED_CTA = "org-member-life-interest-pipeline-interested-cta"
INTERESTED = "I" + chr(0x2019) + "m interested"

#: One photo of the carousel, by its module name: counted, never opened.
OPEN_PHOTO = "org-member-life-company-photos-open-photo"

#: Inside the trending module, MEASURED: THREE ``role="article"`` elements --
#: one wrapper holding the carousel, and two items (eight more slots drawn
#: empty: the carousel loads them as it moves). An ITEM is an article that
#: holds no other article. Each item draws two member links to its author
#: outside its words -- the picture, and the name block, which holds three
#: ``aria-hidden`` spans and exactly ONE of them inside a ``dir`` span: the
#: name (the other two, the supplementary line and the headline, sit in
#: none) -- and ONE link to its own permalink
#: (``/feed/update/urn:li:activity:<id>/``) that holds the words, and on one
#: item a see-more control after them.
LIFE_ITEM = '[role="article"]'
LIFE_MEMBER_LINKS = 'a[href*="/in/"]'
LIFE_PERMALINKS = 'a[href*="/feed/update/"]'
LIFE_NAME = 'span[dir="ltr"] span[aria-hidden="true"]'

#: THE BOUNDS: articles attempted, posts kept, spotlights read.
LIFE_ARTICLES_READ = 40
TRENDING_POSTS = 25
SPOTLIGHTS_READ = 12

#: The closed reasons an article is not returned, in the order checked.
TRENDING_SKIP_REASONS: tuple[str, ...] = (
    "not_visible",
    "holds_other_items",
    "not_one_permalink",
    "not_one_author_block",
    "more_than_one_profile",
    "no_member_author",
    "changed_while_read",
    "no_words",
)


def _life_view(name: str) -> str:
    return f'main [data-view-name="{name}"]'


async def _profiles_outside(item: Any, box: Any, failed: list[int]) -> list[tuple[Any, Optional[str]]]:
    """``(link, profile)`` for each member link in the item, less as many as
    the words hold for each profile -- a member MENTIONED in the words is not
    part of the author's block. ``content_search``'s rule, on Ember markup."""
    inside: list[Optional[str]] = []
    links = box.locator(LIFE_MEMBER_LINKS)
    for index in range(min(await _count(links, failed), MAX_PARTS)):
        inside.append(people_data.canonical_profile_link(
            await _attribute(links.nth(index), "href", failed)))
    outside: list[tuple[Any, Optional[str]]] = []
    links = item.locator(LIFE_MEMBER_LINKS)
    for index in range(min(await _count(links, failed), MAX_PARTS)):
        link = links.nth(index)
        profile = people_data.canonical_profile_link(await _attribute(link, "href", failed))
        if profile in inside:
            inside.remove(profile)
            continue
        outside.append((link, profile))
    return outside


async def _name_block(outside: list[tuple[Any, Optional[str]]], failed: list[int]) -> Optional[tuple[Any, Optional[str]]]:
    """The ONE member link outside the words holding exactly one name span
    (:data:`LIFE_NAME`) -- the name block -- or ``None`` when there is not
    exactly one such link."""
    blocks = [(link, profile) for link, profile in outside
              if await _count(link.locator(LIFE_NAME), failed) == 1]
    return blocks[0] if len(blocks) == 1 else None


def _without_the_more_text(words: str, more: str) -> str:
    words = words.rstrip()
    if more and words.endswith(more):
        return words[: len(words) - len(more)].rstrip()
    return words


async def _read_trending_item(item: Any, failed: list[int]) -> tuple[Any, bool]:
    """One article: a :class:`people_data.Post`, or the
    :data:`TRENDING_SKIP_REASONS` entry that stopped it; and whether it draws
    a see-more control."""
    try:
        visible = await item.is_visible()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        visible = False
    if not visible:
        return "not_visible", False
    if await _count(item.locator(LIFE_ITEM), failed):
        return "holds_other_items", False
    permalinks = item.locator(LIFE_PERMALINKS)
    if await _count(permalinks, failed) != 1:
        return "not_one_permalink", False
    box = permalinks.nth(0)
    mores = box.locator("button")
    more_drawn = await _count(mores, failed) == 1
    outside = await _profiles_outside(item, box, failed)
    block = await _name_block(outside, failed)
    if block is None:
        return "not_one_author_block", more_drawn
    author, profile = block
    if {named for _link, named in outside} != {profile}:
        return "more_than_one_profile", more_drawn
    person = people_data.Person.from_page(
        name=await _text(author.locator(LIFE_NAME), failed), href=profile)
    if person is None or person.link is None:
        return "no_member_author", more_drawn
    words = (await _text(box, failed) or "")[: 4 * people_data.CAPS["text"]]
    if more_drawn:
        words = _without_the_more_text(words, collapsed(await _text(mores.nth(0), failed)))
    # THE AUTHOR AGAIN, AFTER THE WORDS: an item the carousel reused
    # meanwhile would pair one post's words with another post's author.
    again = await _name_block(await _profiles_outside(item, box, failed), failed)
    if again is None or again[1] != profile:
        return "changed_while_read", more_drawn
    if not collapsed(words):
        return "no_words", more_drawn
    post = people_data.Post.from_page(
        author=person, href=await _attribute(box, "href", failed), text=words)
    if post is None:
        return "no_member_author", more_drawn
    return post, more_drawn


async def _read_trending(module: Any, failed: list[int]) -> dict[str, Any]:
    heads = [collapsed(t) for t in await _texts(module.locator("h3"), failed, 8)]
    out: dict[str, Any] = {
        "heading_matched": heads.count(TRENDING_HEADING) == 1,
        "posts": None,
        "articles_seen": 0,
        "skipped": {reason: 0 for reason in TRENDING_SKIP_REASONS},
        "more_controls_drawn": 0,
        "posts_beyond_bound": 0,
    }
    if not out["heading_matched"]:
        return out
    items = module.locator(LIFE_ITEM)
    out["articles_seen"] = await _count(items, failed)
    posts: list[dict[str, Any]] = []
    for index in range(min(out["articles_seen"], LIFE_ARTICLES_READ)):
        verdict, more_drawn = await _read_trending_item(items.nth(index), failed)
        if isinstance(verdict, str):
            out["skipped"][verdict] += 1
            continue
        out["more_controls_drawn"] += 1 if more_drawn else 0
        if len(posts) >= TRENDING_POSTS:
            out["posts_beyond_bound"] += 1
            continue
        posts.append(verdict.envelope())
    # A CAROUSEL THAT DREW NO ITEM YET IS UNREAD, never "no trending content":
    # the list is returned only when an item was drawn to read or to skip.
    drawn = len(posts) + out["posts_beyond_bound"] + sum(
        n for reason, n in out["skipped"].items() if reason != "holds_other_items")
    out["posts"] = posts if drawn else None
    return out


async def _read_spotlights(headings: Any, failed: list[int]) -> Optional[dict[str, Any]]:
    """The spotlights under the ONE ``h3`` of ``headings`` reading
    :data:`SPOTLIGHTS_HEADING`; ``None`` when no heading reads so."""
    texts = await _texts(headings, failed, MAX_PARTS)
    matched = [i for i, t in enumerate(texts) if collapsed(t) == SPOTLIGHTS_HEADING]
    if not matched:
        return None
    out: dict[str, Any] = {
        "heading_matched": len(matched) == 1,
        "spotlights": [],
        "withheld": 0,
        "beyond_bound": 0,
    }
    if len(matched) != 1:
        return out
    # THE SECTION IS THE HEADING'S PARENT, as the About card is the Overview
    # heading's; each spotlight inside it is found by its module name.
    section = headings.nth(matched[0]).locator("xpath=..")
    rows = section.locator('[data-view-name="%s"]' % LIFE_MODULES["company_spotlight"])
    total = await _count(rows, failed)
    out["beyond_bound"] = max(0, total - SPOTLIGHTS_READ)
    for index in range(min(total, SPOTLIGHTS_READ)):
        titles = rows.nth(index).locator("h4")
        if await _count(titles, failed) != 1:
            out["withheld"] += 1
            continue
        # MEASURED: a spotlight holds TWO paragraphs, one inside its video
        # player's dialog -- so its words are the ONE paragraph under the
        # title's own parent, never "the paragraph" of the spotlight.
        bodies = await _texts(titles.nth(0).locator("xpath=..").locator("p"), failed, 4)
        title = _prose_record(await _text(titles.nth(0), failed), "life_spotlight_title")
        body = _prose_record(bodies[0], "life_spotlight_body") if len(bodies) == 1 else None
        if title is None and body is None:
            out["withheld"] += 1
            continue
        out["spotlights"].append({"title": title, "body": body})
    return out


async def read_life_tab(page: Any) -> dict[str, Any]:
    """The Life tab ``page`` already shows: which modules it drew, its
    trending items as post records, its spotlights as the Page's prose, how
    many photos it drew, and whether it offers the interest button.

    Raises ``ExtractionFailedError`` when the page drew none of the modules
    this reader knows -- a zero nothing on the page corroborates.
    """
    failed = [0]
    out: dict[str, Any] = {
        "tab": "life",
        "view": await current_tab(page, failed),
        "modules": {},
        "trending": None,
        "spotlights": None,
        "photos": None,
        "interest_offered": False,
    }
    for key, name in LIFE_MODULES.items():
        out["modules"][key] = await _count(page.locator(_life_view(name)), failed)
    if out["modules"]["trending_employee_content"] == 1:
        out["trending"] = await _read_trending(
            page.locator(_life_view(LIFE_MODULES["trending_employee_content"])), failed)
    out["spotlights"] = await _read_spotlights(page.locator("main h3"), failed)
    if out["modules"]["company_photos"] == 1:
        module = page.locator(_life_view(LIFE_MODULES["company_photos"]))
        heads = [collapsed(t) for t in await _texts(module.locator("h3"), failed, 8)]
        out["photos"] = {
            "heading_matched": heads.count(PHOTOS_HEADING) == 1,
            "drawn": await _count(module.locator('[data-view-name="%s"]' % OPEN_PHOTO), failed),
        }
    buttons = page.locator(_life_view(INTERESTED_CTA))
    if await _count(buttons, failed) == 1:
        out["interest_offered"] = collapsed(await _text(buttons.nth(0), failed)) == INTERESTED
    out["reads_failed"] = failed[0]
    if not any(out["modules"].values()):
        raise ExtractionFailedError(
            "the Life tab drew none of the modules this reader knows, and "
            "nothing on the page says the organisation's Life tab is empty; "
            "reporting an empty tab here would be indistinguishable from a "
            f"broken read (view read {out['view']!r}).",
            hint=dom._landing_note(page),
        )
    return out


# ---------------------------------------------------------------------------
# The Products tab (census J 111, lane jobs7, 2026-11-27)
# ---------------------------------------------------------------------------

#: The Products tab's own words, MEASURED by keyed shape on session 12's
#: capture of an organisation's Products tab (load 21;
#: ``tests/fixtures/live12/c_rj26_2_products_words.html``): the Page
#: navigation's tab word, and the label of the button LinkedIn draws to show
#: the rest of the list (never pressed).
PRODUCTS_TAB_WORD = "Products"
SHOW_ALL_PRODUCTS = "Show all products"

#: The most products one read returns. The capture drew two; the rest sit
#: behind LinkedIn's own button, which is never pressed.
PRODUCTS_BOUND = 25

#: A product's own page, ``/products/<slug>/``, relative or absolute. The slug
#: is the product's name in another spelling, so it is matched and never
#: returned.
_PRODUCT_HREF = re.compile(r"^(?:https://www\.linkedin\.com)?/products/[^/?#]{1,200}/?$")

#: The fewest navigation links a Page must draw for "no Products tab among
#: them" to be a reading rather than a navigation that failed to render.
#: MEASURED: the capture's navigation draws eight.
_NAV_LINKS_MIN = 3

#: Where a product's NAME sits: the ``h2`` inside the ``aria-label``-carrying
#: link to its own page. Its CATEGORY is the one paragraph inside the link to
#: LinkedIn's product-category search, in the same lockup -- two levels above
#: the name link. Both MEASURED on the capture's two cards.
PRODUCT_NAMES = 'main a[aria-label][href*="/products/"] h2'
PRODUCT_CATEGORY = 'a[href*="/search/results/products/"] p'


async def read_products_tab(page: Any) -> dict[str, Any]:
    """The Products tab ``page`` already shows: each product's name and
    category, as records.

    A product's NAME and its CATEGORY each leave as a
    ``people_data.OrganisationProse`` record (``read_from`` ``product_name``
    / ``product_category``): the Page's own words under
    THIRD-PARTY-TEXT-AT-RUNTIME, untrusted, sanitised, bounded, never
    stored. NEVER READ: the product's link (its slug is its name), the face
    pile under each card (the members who use it), the card's own button,
    any ``aria-label``. ``show_all_offered`` says LinkedIn draws its button
    for the rest of the list; it is never pressed.

    THE ZERO RULE. A Page whose navigation is drawn and draws NO Products
    tab answers ``products: None`` with ``products_tab_drawn: False``: the
    organisation has no Products tab, and the navigation itself says so
    (session 11's load 23 was such a Page). A Products tab marked current
    that yields no product raises ``ExtractionFailedError``, as does a page
    that marks no Products tab and draws too little navigation to say why:
    an empty answer would be indistinguishable from a broken read.
    """
    failed = [0]
    tab = await current_tab(page, failed)
    nav = [collapsed(t) for t in await _texts(page.locator("main nav a"), failed, 20)]
    out: dict[str, Any] = {
        "tab": "products",
        "view": tab,
        "products_tab_drawn": PRODUCTS_TAB_WORD in nav,
        "products": [],
        "products_withheld": 0,
        "products_beyond_bound": 0,
        "show_all_offered": (
            await _count(page.locator(f'button[aria-label="{SHOW_ALL_PRODUCTS}"]'), failed)
        ) > 0,
    }
    if tab != "products":
        out["reads_failed"] = failed[0]
        if len(nav) >= _NAV_LINKS_MIN and not out["products_tab_drawn"]:
            out["products"] = None
            return out
        raise ExtractionFailedError(
            "the Products tab is not the tab this Page marks current, and its "
            "navigation does not show that it has none "
            f"({len(nav)} navigation link(s) read, the current tab {tab}).",
            hint=dom._landing_note(page),
        )
    names = page.locator(PRODUCT_NAMES)
    total = await _count(names, failed)
    for index in range(min(total, PRODUCTS_BOUND)):
        heading = names.nth(index)
        link = heading.locator("xpath=..")
        href = await _attribute(link, "href", failed)
        name = _prose_record(await _text(heading, failed), "product_name")
        if not _PRODUCT_HREF.match(href or "") or name is None:
            out["products_withheld"] += 1
            continue
        lockup = link.locator("xpath=..").locator("xpath=..")
        categories = lockup.locator(PRODUCT_CATEGORY)
        category = None
        if await _count(categories, failed) == 1:
            category = _prose_record(await _text(categories.nth(0), failed), "product_category")
        out["products"].append({"name": name, "category": category})
    out["products_beyond_bound"] = max(0, total - PRODUCTS_BOUND)
    out["reads_failed"] = failed[0]
    if not out["products"]:
        raise ExtractionFailedError(
            "the Products tab yielded no product; an empty answer here would be "
            f"indistinguishable from a broken read ({total} product heading(s) "
            f"drawn, {out['products_withheld']} withheld).",
            hint=dom._landing_note(page),
        )
    return out


#: The reader for each tab, by its token. The tool calls each one BY NAME
#: (``server.linkedin_company_page_tab``), so the guards that follow calls by
#: name -- the reachability inventory and the people-reader derivation -- find
#: every reader wired and the record each one builds.
READERS = {
    "about": read_about_tab,
    "events": read_events_tab,
    "insights": read_insights_tab,
    "life": read_life_tab,
    "posts": read_posts_tab,
    "products": read_products_tab,
}
