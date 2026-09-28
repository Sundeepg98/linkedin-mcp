"""The Premium recruiter-insights page -- census ``N 195``.

WHAT THE PAGE DRAWS. ``/analytics/recruiter-views/`` (admitted by the
premium-four entry, 2026-09-20; captured live on 2026-09-23 by the live lane,
``_state/live1/cap_recruiter_views.html`` in that lane's worktree, gitignored;
its structure is kept in ``tests/fixtures/synthetic/recruiter_views.html``) is
one section headed "Recruiter insights":

    <n> / Profile views / Past 90 days       a metric card, a link to the
                                             profile-views page, and its chart
    <n> / Recruiter views / Past 90 days     the recruiter metric, and its chart
    Line chart with 13 data points.          each chart's own description
    x, <epoch ms>, <n>. Views over time.     each chart POINT, as the label of
                                             one svg path
    Recruiter at <employer>                  one row per recruiter viewer, each
    <industry>                               a link to the employer's insights
    Viewed <when> ago                        page -- and NO member link

WHAT THIS RETURNS.

* ``counts`` -- the two metrics, each an integer, keyed by a word this module
  declares (:data:`METRIC_KEYS`), never by the label the page drew;
* ``time_range_days`` -- the filter's "Past <n> days", as the integer;
* ``trends`` -- per metric, the chart's own point count and its POINTS, each
  ``{"date", "views"}``: the UTC date of the point's epoch and the integer
  count. MEASURED, not assumed: the capture's 26 points all sit at UTC
  midnight (each a Thursday), so the UTC date is the date the chart means;
* ``viewers`` -- each recruiter viewer as a row shaped like
  ``linkedin_who_viewed_me``'s: ``{"person", "viewed", "anonymous"}``, the
  person a PEOPLE RECORD (``people_data.Person``) whose name is the employer
  line LinkedIn gives the viewer ("Recruiter at <employer>") and whose
  headline is the industry, ``anonymous`` true and no link -- exactly as
  LinkedIn draws the viewer, and no more, the way that tool returns a viewer
  drawn as "Recruiter at Acme". That is the page naming nobody:
  WHO-WHICH-COUNTS-ARE-NOT-DELIVERY does not hold this row (lane Y2,
  2026-09-24), and the viewer rows go out under PEOPLE-DATA-MITIGATIONS;
* ``denominators`` -- what was SEEN beside what was returned, so a row or a
  chart drawn in a shape this reader does not know reads as seen-and-unread
  rather than as absent: chart regions seen and read, insights links seen,
  viewer rows seen, returned, unparsed and hidden, and the regions and links
  that could not be read at all, counted by exception TYPE -- one element that
  fails is counted and the rest are still read.

WHAT IT NEVER RETURNS: a label the page drew (every word in the output is this
module's own or a record's field), an employer's Page link or id, anything of
a hidden viewer row, or anything past what had drawn -- no scroll, no "show
more", no press of any kind.

HOW IT READS: Playwright's own read calls -- find elements, read their text
and attributes, ask whether they are visible -- and no script. Every page
string is matched against a pattern this module declares before anything is
kept: a count leaves only as the digits a pattern captured, a label only as
the key it matched, a time only in this package's own spelling with ASCII
digits, and a viewer's lines only inside a people record.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import dom, people_data, shape
from linkedin_server.errors import ExtractionFailedError

RECRUITER_VIEWS_URL = "https://www.linkedin.com/analytics/recruiter-views/"

#: The metric labels this page draws, and the key each is returned under.
#: Pairs, not a dict: nothing at module level here can be written to.
METRIC_KEYS: tuple[tuple[str, str], ...] = (
    ("Profile views", "profile_views"),
    ("Recruiter views", "recruiter_views"),
)
_KEYS: tuple[str, ...] = tuple(key for _label, key in METRIC_KEYS)

NUMBER = re.compile(r"[0-9][0-9,]{0,12}")
RANGE = re.compile(r"Past ([0-9]{1,4}) days")
POINT = re.compile(r"x, ([0-9]{10,13}), ([0-9]{1,7})\. Views over time\.")
DESCRIBED = re.compile(r"Line chart with ([0-9]{1,4}) data points\.?")
#: A viewer row's link: an employer's insights page, matched on the PATH, so a
#: query or a fragment LinkedIn adds does not drop the row.
VIEWER_PATH = re.compile(r"/company/[^/]+/insights/?")
VIEWER_HOSTS = frozenset({"", "www.linkedin.com", "linkedin.com"})
#: The viewer row's time line, in either notation LinkedIn uses -- "Viewed 2w
#: ago" and "Viewed 2 weeks ago" (``shape.find_time_ago`` reads both).
VIEWED = re.compile(r"Viewed .{1,24} ago")
#: What a normalised time may look like when it leaves: this package's own
#: spelling, ASCII digits only.
NORMALISED_TIME = re.compile(r"[0-9]{1,4} [a-z]+ ago")

#: Bounds: the capture drew two viewer rows and two charts of thirteen points.
MAX_VIEWERS = 25
MAX_POINTS = 60
MAX_CHARTS = 4
MAX_REGIONS = 40
MAX_PARAGRAPHS = 400
MAX_COUNT = 10_000_000

#: A chart point's epoch, in milliseconds, must fall between these to be a
#: date this page could draw (2003, LinkedIn's founding, to 2100).
_EPOCH_MS_FLOOR = 1_041_379_200_000
_EPOCH_MS_CEILING = 4_102_444_800_000

#: Where a viewer row sits inside a container hidden from assistive technology.
_HIDDEN_ANCESTOR = "xpath=ancestor-or-self::*[@aria-hidden='true']"

#: THE QUERIES, named, so the page is asked exactly these and a drive of this
#: reader (``tests/shipped_drives.py``) can answer exactly these.
PARAGRAPHS = "p"
LABELS = "label"
CHART_REGIONS = '[role="region"]'
CHART_POINTS = "path[aria-label]"
CHART_CARD = "xpath=.."
COMPANY_LINKS = 'a[href*="/company/"]'


def _key_for(label: Any) -> Optional[str]:
    """The declared key a page label names, as THIS module's string."""
    text = str(label or "").strip()
    for declared, key in METRIC_KEYS:
        if text == declared:
            return key
    return None


def _count(text: Any) -> Optional[int]:
    found = NUMBER.fullmatch(str(text or "").strip())
    if not found:
        return None
    value = int(found.group(0).replace(",", ""))
    return value if value <= MAX_COUNT else None


def _point(label: Any) -> Optional[dict[str, Any]]:
    found = POINT.fullmatch(str(label or "").strip())
    if not found:
        return None
    epoch = int(found.group(1))
    if not _EPOCH_MS_FLOOR <= epoch <= _EPOCH_MS_CEILING:
        return None
    day = datetime.fromtimestamp(epoch / 1000, tz=timezone.utc).date().isoformat()
    return {"date": day, "views": int(found.group(2))}


def _lines(text: Any) -> list[str]:
    return [line.strip() for line in str(text or "").split("\n") if line.strip()]


def _is_viewer_link(href: Any) -> bool:
    parts = urlsplit(str(href or ""))
    return parts.netloc.lower() in VIEWER_HOSTS and bool(VIEWER_PATH.fullmatch(parts.path))


def _when(line: str) -> Optional[str]:
    """The row's time in this package's spelling, or None: a page-drawn digit
    that is not ASCII, or a run too long to be a time, never leaves."""
    found = shape.find_time_ago([line])
    return found if found and NORMALISED_TIME.fullmatch(found) else None


#: THE STEPS TAKE THE ELEMENTS, NEVER THE PAGE. The page is queried once, in
#: :func:`read_recruiter_views`, and each step reads the handles it is given:
#: one page entry point, which is the one the reader-leak guard drives.


async def _counts(paragraphs: list[Any]) -> dict[str, Optional[int]]:
    """A paragraph that is only a number, followed by one that is a declared
    label: the count under that label's key. First reading of each key wins."""
    counts: dict[str, Optional[int]] = {key: None for key in _KEYS}
    texts = [await p.inner_text() for p in paragraphs[:MAX_PARAGRAPHS]]
    for value, label in zip(texts, texts[1:]):
        key, count = _key_for(label), _count(value)
        if key is not None and count is not None and counts[key] is None:
            counts[key] = count
    return counts


async def _range_days(labels: list[Any]) -> Optional[int]:
    for label in labels:
        found = RANGE.fullmatch(str(await label.inner_text() or "").strip())
        if found:
            return int(found.group(1))
    return None


def _failed(tally: dict[str, int], exc: BaseException) -> None:
    """One element that could not be read, counted by its exception's TYPE --
    never its message -- so the others are still read."""
    name = type(exc).__name__
    tally[name] = tally.get(name, 0) + 1


async def _chart(region: Any, trends: dict[str, Any]) -> bool:
    """One region: False if it holds no labelled point (not a chart), else
    True, and its trend added when its card names a declared metric."""
    paths = await region.query_selector_all(CHART_POINTS)
    if not paths:
        return False
    if len(trends) >= MAX_CHARTS:
        return True
    card = await region.query_selector(CHART_CARD)
    key = None
    for p in await card.query_selector_all(PARAGRAPHS) if card is not None else []:
        key = _key_for(await p.inner_text())
        if key is not None:
            break
    if key is None or key in trends:
        return True
    described = None
    for line in _lines(await region.inner_text()):
        found = DESCRIBED.fullmatch(line)
        if found:
            described = int(found.group(1))
            break
    points = []
    for path in paths[:MAX_POINTS]:
        point = _point(await path.get_attribute("aria-label"))
        if point is not None:
            points.append(point)
    trends[key] = {"data_points": described, "points": points}
    return True


async def _trends(regions: list[Any]) -> tuple[dict[str, Any], int, dict[str, int]]:
    """Each chart: a region holding labelled points, the metric its own card
    names, its description's point count, and its points. Returns the trends,
    how many chart regions were SEEN -- so a chart whose card names no
    declared metric is counted rather than silently dropped -- and the regions
    that could not be read, by type."""
    trends: dict[str, Any] = {}
    seen = 0
    failed: dict[str, int] = {}
    for region in regions[:MAX_REGIONS]:
        try:
            if await _chart(region, trends):
                seen += 1
        except Exception as exc:  # noqa: BLE001 -- counted by type, never quoted
            _failed(failed, exc)
    return trends, seen, failed


async def _viewers(anchors: list[Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Each recruiter viewer row: a link to an employer's insights page that
    draws a "Viewed ... ago" line. Its twin, "View insights", draws none and is
    not a viewer. A hidden row is counted and nothing of it is returned: its
    text is read only to decide whether it is a viewer row."""
    viewers: list[dict[str, Any]] = []
    tally: dict[str, Any] = {"links": 0, "seen": 0, "hidden": 0, "unparsed": 0, "failed": {}}
    for anchor in anchors:
        try:
            await _viewer(anchor, viewers, tally)
        except Exception as exc:  # noqa: BLE001 -- counted by type, never quoted
            _failed(tally["failed"], exc)
    return viewers, tally


async def _viewer(anchor: Any, viewers: list[dict[str, Any]], tally: dict[str, Any]) -> None:
    """One company link: a viewer row, a hidden viewer row, or neither."""
    if not _is_viewer_link(await anchor.get_attribute("href")):
        return
    tally["links"] += 1
    if (not await anchor.is_visible()
            or await anchor.query_selector(_HIDDEN_ANCESTOR) is not None):
        if VIEWED.search(str(await anchor.text_content() or "")):
            tally["seen"] += 1
            tally["hidden"] += 1
        return
    lines = _lines(await anchor.inner_text())
    viewed = next((line for line in lines if VIEWED.fullmatch(line)), None)
    if viewed is None:
        return
    tally["seen"] += 1
    if len(viewers) >= MAX_VIEWERS:
        return
    others = lines[:lines.index(viewed)] + lines[lines.index(viewed) + 1:]
    # THE RECORD IS THE ONLY CHANNEL. No link and no degree: the row's link is
    # an employer's page, and a record's link is a member's or nothing.
    person = people_data.Person.from_page(
        name=others[0] if others else None,
        headline=others[1] if len(others) > 1 else None,
    )
    if person is None:
        tally["unparsed"] += 1
        return
    viewers.append({
        "person": person.envelope(),
        "viewed": _when(viewed),
        "anonymous": True,
    })


async def read_recruiter_views(page: Any) -> dict[str, Any]:
    """Everything the recruiter-insights section draws, as declared above."""
    try:
        counts = await _counts(list(await page.query_selector_all(PARAGRAPHS)))
        days = await _range_days(list(await page.query_selector_all(LABELS)))
        trends, charts_seen, charts_failed = await _trends(
            list(await page.query_selector_all(CHART_REGIONS)))
        viewers, tally = await _viewers(
            list(await page.query_selector_all(COMPANY_LINKS)))
    except Exception as exc:  # noqa: BLE001 -- raised by type alone
        # THE LANDING IS DESCRIBED, NEVER PUBLISHED: the same ruling the
        # twelve dom readers raise under (WITHHELD), and the same describer.
        raise ExtractionFailedError(
            f"could not read the recruiter-insights page ({type(exc).__name__})",
            hint=dom._landing_note(page),
        ) from None
    return {
        "counts": counts,
        "time_range_days": days,
        "trends": trends,
        "viewers": viewers,
        "denominators": {
            "charts_seen": charts_seen,
            "charts_read": len(trends),
            "charts_failed": charts_failed,
            "insight_links_seen": tally["links"],
            "viewer_rows_seen": tally["seen"],
            "viewers_returned": len(viewers),
            "viewers_unparsed": tally["unparsed"],
            "viewers_hidden": tally["hidden"],
            "links_failed": tally["failed"],
        },
    }
