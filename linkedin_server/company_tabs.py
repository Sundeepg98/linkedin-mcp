"""Read ONE tab of an organisation's Page -- its About tab or its Events tab.

Census rows ``J 106`` (*Company Page About tab (size, industry, locations)*)
and ``J 165`` (*Company Page Events tab: the events a company hosts*). Lane
readers-jobs26, 2026-11-26, over the live lane's session-11 captures of both
tabs (loads 20 and 21), tracked as ``tests/fixtures/live11/company_about.html``
and ``company_events.html`` and, with LinkedIn's words measured by keyed shape,
as ``company_about_words.html`` and ``company_events_words.html``
(``scripts/_build_live11_word_skeletons.py``).

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

## THE ZERO RULE

A tab that yields nothing is a finding only when the page corroborates it:
the Upcoming card's own sentence corroborates NO upcoming event, and nothing
corroborates an empty Past card or an About card with no recognised term.
An uncorroborated zero raises ``ExtractionFailedError`` -- in this module's
own words, never the page's -- so a broken read can never pass for "this
organisation has none".

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

from linkedin_server import company_page, people_data
from linkedin_server.errors import ExtractionFailedError

#: The tabs this module reads, each with the path it is addressed by under
#: ``/company/<id>/``: its segment, and for the Insights tab the one query the
#: read boundary admits with it (exactly ``insightType=HEADCOUNT``, the value
#: LinkedIn drew). Closed: anything else is refused before any load.
TAB_SEGMENTS: dict[str, str] = {
    "about": "about",
    "events": "events",
    "insights": "insights",
}
TAB_QUERIES: dict[str, str] = {"insights": "?insightType=HEADCOUNT"}
TAB_PATHS: dict[str, str] = {
    tab: segment + "/" + TAB_QUERIES.get(tab, "") for tab, segment in TAB_SEGMENTS.items()
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
    segment = re.escape(TAB_SEGMENTS[tab])
    return bool(re.fullmatch(r"/company/[^/?#]{1,200}/%s/?" % segment, path)) and not path.startswith(
        "/company/unavailable/"
    )


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
    """The last path segment of the ONE Page tab the page marks current, from
    a closed vocabulary; ``no_current_tab`` or ``tabs_disagree`` otherwise."""
    marked = page.locator('main nav a[aria-current="page"]')
    total = await _count(marked, failed)
    if total == 0:
        return "no_current_tab"
    if total > 1:
        return "tabs_disagree"
    href = await _attribute(marked.nth(0), "href", failed)
    try:
        segments = [s for s in urlsplit(href or "").path.split("/") if s]
    except ValueError:
        segments = []
    last = segments[-1] if len(segments) >= 3 and segments[0] == "company" else ""
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
            f"(view read {view!r}, {out['overview_headings']} Overview heading(s))."
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
            f"{len(out['cards'])} recognised card(s))."
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
}

#: The screen-reader data table LinkedIn draws beside the function chart:
#: its header cells, MEASURED, each with the field its column is returned as.
#: A table is read only when it carries the first two; a header not here
#: leaves its column unread.
FUNCTION_TABLE_HEADERS: dict[str, str] = {
    "Function": "function",
    "Number of employees": "employees",
    "Percentage of total headcount": "share_of_headcount_percent",
    "3 month growth": "growth_3_months_percent",
    "6 month growth": "growth_6_months_percent",
}
_REQUIRED_HEADERS = ("Function", "Number of employees")

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
    if key in ("growth_3_months_percent", "growth_6_months_percent"):
        return _growth(text)
    if _PLAIN_INT.fullmatch(line):
        value = _grouped_int(line)
        if key == "share_of_headcount_percent" and value > 100:
            return None
        return value
    return None


async def read_insights_tab(page: Any) -> dict[str, Any]:
    """The Insights tab ``page`` already shows: the modules it drew, and the
    function table's rows -- each a function from LinkedIn's taxonomy with
    its employee count, its share of headcount and its growth.

    Raises ``ExtractionFailedError`` when neither a known module nor a
    function row was read.
    """
    failed = [0]
    out: dict[str, Any] = {
        "tab": "insights",
        "view": await current_tab(page, failed),
        "modules": [],
        "modules_unrecognised": 0,
        "functions": [],
        "function_tables": 0,
        "rows_withheld": 0,
        "headers_unread": 0,
    }
    for text in await _texts(page.locator("main h2"), failed, MAX_PARTS):
        key = INSIGHT_MODULES.get(collapsed(text))
        if key is not None and key not in out["modules"]:
            out["modules"].append(key)
    tables = page.locator("main table")
    chosen = []
    for index in range(min(await _count(tables, failed), 20)):
        heads = tables.nth(index).locator("th")
        headers = [collapsed(t) for t in await _texts(heads, failed, 12)]
        if all(h in headers for h in _REQUIRED_HEADERS):
            chosen.append((tables.nth(index), heads, headers))
    out["function_tables"] = len(chosen)
    if len(chosen) == 1:
        table, heads, headers = chosen[0]
        # A CELL BELONGS TO THE HEADER ITS OWN ``headers`` ATTRIBUTE NAMES --
        # the table's own accessibility wiring, measured on every cell of the
        # capture -- never to the header at the same position.
        column: dict[str, str] = {}
        for index, word in enumerate(headers):
            key = FUNCTION_TABLE_HEADERS.get(word)
            ident = await _attribute(heads.nth(index), "id", failed)
            if key is None or not ident:
                out["headers_unread"] += 1
                continue
            column[ident] = key
        rows = table.locator("tbody tr")
        for index in range(min(await _count(rows, failed), FUNCTION_ROWS)):
            cells = rows.nth(index).locator("td")
            row: dict[str, Any] = {}
            for cell_index in range(min(await _count(cells, failed), 12)):
                cell = cells.nth(cell_index)
                key = column.get(await _attribute(cell, "headers", failed) or "")
                if key is not None and key not in row:
                    row[key] = _cell_value(key, await _text(cell, failed))
            if row.get("function") is None or row.get("employees") is None:
                out["rows_withheld"] += 1
                continue
            out["functions"].append(row)
    out["reads_failed"] = failed[0]
    if not out["functions"] and not out["modules"]:
        raise ExtractionFailedError(
            "the Insights tab yielded no known module and no function row; an "
            "empty answer here would be indistinguishable from a broken read "
            f"({out['function_tables']} function table(s) found)."
        )
    return out


#: The reader for each tab, by its token. The tool calls each one BY NAME
#: (``server.linkedin_company_page_tab``), so the guards that follow calls by
#: name -- the reachability inventory and the people-reader derivation -- find
#: every reader wired and the record each one builds.
READERS = {"about": read_about_tab, "events": read_events_tab, "insights": read_insights_tab}
