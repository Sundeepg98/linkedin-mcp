"""Read the creator content-analytics chart, via accessible names.

The impure half of :mod:`linkedin_server.chart_labels`. It opens one admitted
page, collects ``aria-label`` off every labelled node, and hands the strings
to the pure parser. **It makes no decision about what a label MEANS** -- that
is the parser's job and it is tested without a browser.

## WHY aria-label AND NOT THE TEXT

Measured 2026-09-19 (`scripts/_probe_creator_content_analytics.py`): the whole
document carries **1,869 characters of text**, `main` holds 1,690 of them, and
there are **zero** ``h3``, ``h4``, ``table`` or ``canvas`` nodes against 56
``svg``. The values are drawn, not written. LinkedIn renders them to a screen
reader as ``aria-label`` on the chart nodes, and that is the only text route
into the numbers.

**The headings are the trap.** They are FEED-shaped on this page -- `Feed
post`, `Ad Options` -- and identical in shape to the feed's own, because
``h2``/``main`` reads shared chrome here. A reader built on headings measures
the chrome and reports nothing about analytics. That route is named so a
later attempt does not repeat it.

## WHAT IT COSTS TO OPEN, AND WHY THIS TOOL DOES NOT RE-BRACKET

`readonly.py` admits this address with the cost already measured:
``dom.read_invitation_badge`` read before and after, twice, and the badge did
not move. **A three-navigation bracket on every call would spend two extra
page loads on his account to re-derive a settled answer**, so this reader
takes ONE navigation and cites that measurement instead. If a badge is ever
observed responding to this surface, that decision is the one to revisit.
"""
from __future__ import annotations

from typing import Any, Optional

from . import chart_labels
from .config import BASE_URL

CONTENT_ANALYTICS_URL = f"{BASE_URL}/analytics/creator/content/"

#: Every labelled node. The SELECTION is deliberately wide and the JUDGEMENT
#: is deliberately narrow: this reader must not decide which labels are
#: analytics, because deciding that from a selector is how the notification
#: badge became a datapoint in the first draft.
LABEL_SELECTOR = "[aria-label]"

#: A label longer than this is prose, not a chart annotation. Bounded so a
#: page that starts putting paragraphs in accessible names cannot stream them
#: into this process.
MAX_LABEL_CHARS = 200


async def collect_labels(page: Any) -> list[Optional[str]]:
    """Every ``aria-label`` on the page, unparsed and unfiltered.

    Returned as-is so the caller's reading carries the true denominator. A
    reader that filters here and counts there reports a denominator it did not
    measure.
    """
    out: list[Optional[str]] = []
    locator = page.locator(LABEL_SELECTOR)
    try:
        total = int(await locator.count())
    except Exception:  # noqa: BLE001
        return out
    for index in range(total):
        try:
            value = await locator.nth(index).get_attribute("aria-label")
        except Exception:  # noqa: BLE001
            value = None
        if isinstance(value, str) and len(value) > MAX_LABEL_CHARS:
            value = None
        out.append(value)
    return out


async def read_content_analytics(page: Any) -> dict[str, Any]:
    """The chart series on the already-open content-analytics page.

    The page must already be at :data:`CONTENT_ANALYTICS_URL`; navigation is
    the caller's, so this stays testable and does no IO of its own beyond
    reading attributes.
    """
    labels = await collect_labels(page)
    reading = chart_labels.series(labels)
    reading["readable"] = chart_labels.is_readable(reading)
    # THE ROUTE TRAVELS WITH THE READING. A caller seeing points_found 0 can
    # otherwise not tell "the chart drew nothing" from "the page changed shape
    # and this route is dead", and those need different next actions.
    reading["route"] = (
        "aria-label on chart nodes. The document carries under 2,000 chars of "
        "TEXT and no table; the numbers are drawn, not written. If "
        "points_found is 0 while labels_seen is large, the page still renders "
        "but this route no longer finds datapoints."
    )
    return reading
