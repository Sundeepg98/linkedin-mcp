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
  a date this module computed from the point's epoch and the integer count;
* ``viewers`` -- each recruiter viewer as a row shaped like
  ``linkedin_who_viewed_me``'s: ``{"person", "viewed", "anonymous"}``, the
  person a PEOPLE RECORD (``people_data.Person``) whose name is the employer
  line LinkedIn gives the viewer ("Recruiter at <employer>") and whose
  headline is the industry, ``anonymous`` true and no link -- exactly as
  LinkedIn draws the viewer, and no more, the way that tool returns a viewer
  drawn as "Recruiter at Acme". That is the page naming nobody:
  WHO-WHICH-COUNTS-ARE-NOT-DELIVERY does not hold this row (lane Y2,
  2026-09-24), and the viewer rows go out under PEOPLE-DATA-MITIGATIONS.

WHAT IT NEVER RETURNS: a label the page drew (every word in the output is this
module's own or a record's field), an employer's Page link or id, a hidden
viewer, or anything past what had drawn -- no scroll, no "show more", no
press of any kind.

HOW IT READS: Playwright's own read calls -- find elements, read their text
and attributes, ask whether they are visible -- and no script. Every page
string is matched against a pattern this module declares before anything is
kept: a count leaves only as the digits a pattern captured, a label only as
the key it matched, and a viewer's lines only inside a people record.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional

from linkedin_server import people_data, shape

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
VIEWER_HREF = re.compile(r"(?:https://www\.linkedin\.com)?/company/[^/?#]+/insights/?")
VIEWED = re.compile(r"Viewed \S+ ago")

#: Bounds: the capture drew two viewer rows and two charts of thirteen points.
MAX_VIEWERS = 25
MAX_POINTS = 60
MAX_CHARTS = 4
MAX_PARAGRAPHS = 400
MAX_COUNT = 10_000_000

#: A chart point's epoch, in milliseconds, must fall between these to be a
#: date this page could draw (2003, LinkedIn's founding, to 2100).
_EPOCH_MS_FLOOR = 1_041_379_200_000
_EPOCH_MS_CEILING = 4_102_444_800_000

#: Where a viewer row sits inside a container hidden from assistive technology.
_HIDDEN_ANCESTOR = "xpath=ancestor-or-self::*[@aria-hidden='true']"


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


async def _counts(page: Any) -> dict[str, Optional[int]]:
    """A paragraph that is only a number, followed by one that is a declared
    label: the count under that label's key. First reading of each key wins."""
    counts: dict[str, Optional[int]] = {key: None for key in _KEYS}
    texts = [await p.inner_text() for p in (await page.query_selector_all("p"))[:MAX_PARAGRAPHS]]
    for value, label in zip(texts, texts[1:]):
        key, count = _key_for(label), _count(value)
        if key is not None and count is not None and counts[key] is None:
            counts[key] = count
    return counts


async def _range_days(page: Any) -> Optional[int]:
    for label in await page.query_selector_all("label"):
        found = RANGE.fullmatch(str(await label.inner_text() or "").strip())
        if found:
            return int(found.group(1))
    return None


async def _trends(page: Any) -> dict[str, Any]:
    """Each chart region: the metric its own card names, its description's
    point count, and its points."""
    trends: dict[str, Any] = {}
    for region in (await page.query_selector_all('[role="region"]'))[:MAX_CHARTS]:
        card = await region.query_selector("xpath=..")
        key = None
        for p in await card.query_selector_all("p") if card is not None else []:
            key = _key_for(await p.inner_text())
            if key is not None:
                break
        if key is None or key in trends:
            continue
        described = None
        for line in _lines(await region.inner_text()):
            found = DESCRIBED.fullmatch(line)
            if found:
                described = int(found.group(1))
                break
        points = []
        for path in (await region.query_selector_all("path[aria-label]"))[:MAX_POINTS]:
            point = _point(await path.get_attribute("aria-label"))
            if point is not None:
                points.append(point)
        trends[key] = {"data_points": described, "points": points}
    return trends


async def _viewers(page: Any) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Each recruiter viewer row: a link to an employer's insights page that
    draws a "Viewed ... ago" line. Its twin, "View insights", draws none and is
    not a viewer. A hidden row is counted before anything is read from it."""
    viewers: list[dict[str, Any]] = []
    seen = hidden = unparsed = 0
    for anchor in await page.query_selector_all('a[href*="/company/"]'):
        if not VIEWER_HREF.fullmatch(str(await anchor.get_attribute("href") or "")):
            continue
        if (not await anchor.is_visible()
                or await anchor.query_selector(_HIDDEN_ANCESTOR) is not None):
            if VIEWED.search(str(await anchor.text_content() or "")):
                seen += 1
                hidden += 1
            continue
        lines = _lines(await anchor.inner_text())
        viewed = next((line for line in lines if VIEWED.fullmatch(line)), None)
        if viewed is None:
            continue
        seen += 1
        if len(viewers) >= MAX_VIEWERS:
            continue
        others = lines[:lines.index(viewed)] + lines[lines.index(viewed) + 1:]
        # THE RECORD IS THE ONLY CHANNEL. No link and no degree: the row's
        # link is an employer's page, and a record's link is a member's or
        # nothing.
        person = people_data.Person.from_page(
            name=others[0] if others else None,
            headline=others[1] if len(others) > 1 else None,
        )
        if person is None:
            unparsed += 1
            continue
        viewers.append({
            "person": person.envelope(),
            "viewed": shape.find_time_ago([viewed]),
            "anonymous": True,
        })
    return viewers, {"seen": seen, "hidden": hidden, "unparsed": unparsed}


async def read_recruiter_views(page: Any) -> dict[str, Any]:
    """Everything the recruiter-insights section draws, as declared above."""
    try:
        counts = await _counts(page)
        days = await _range_days(page)
        trends = await _trends(page)
        viewers, tally = await _viewers(page)
    except Exception as exc:  # noqa: BLE001 -- raised by type alone
        raise RuntimeError(
            f"could not read the recruiter-insights page ({type(exc).__name__})"
        ) from None
    return {
        "counts": counts,
        "time_range_days": days,
        "trends": trends,
        "viewers": viewers,
        "denominators": {
            "viewer_links_seen": tally["seen"],
            "viewers_returned": len(viewers),
            "viewers_unparsed": tally["unparsed"],
            "viewers_hidden": tally["hidden"],
        },
    }
