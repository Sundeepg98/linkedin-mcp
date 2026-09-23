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

from . import chart_labels, item_addresses, post_summary_counts
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

    ## THE SECOND READING, ADDED 2026-09-20, AND IT COSTS NOTHING EXTRA

    ``item_addresses`` is read off the SAME already-open page, so this adds no
    navigation, no click and no page load -- the expensive thing was opening
    the address, and it is already open. The field is ADDITIVE: every key this
    function returned before is unchanged, which matters because ``C40`` is
    banked on a live run that quoted ``points_found``, ``values`` and
    ``readable``, and a banked reading should not be invalidated by a wave
    that added a field beside it.

    **WHY IT IS HERE AND NOT IN A SECOND TOOL.** This page draws LinkedIn's
    own item permalinks and per-post analytics addresses in its hrefs, and
    ``scripts/_probe_creator_content_analytics.py`` -- the probe that captured
    it -- deliberately emitted **no href at all**, on the correct ground that
    LinkedIn urls carry member and entity identifiers. So the addresses were
    captured and never read: the instrument's own disclosure rule hid them.
    The answer is a classifier that keeps the identifiers inside and publishes
    a closed alphabet, which is what ``item_addresses`` is.

    It defaults to ``include_identifiers=False``, so this function's payload
    gains counts and no identifiers. A caller that has decided to hold real
    post identifiers asks ``item_addresses.read_item_addresses`` directly.
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
    reading["item_addresses"] = await item_addresses.read_item_addresses(page)
    # THE THIRD READING, ADDED 2026-09-23 BY LANE L1, AND IT IS ADDITIVE IN
    # THE SAME SENSE AS THE SECOND: same open page, no navigation, no press,
    # and every key above is unchanged -- ``C40`` stays banked on the keys it
    # quoted. The post-summary links this page draws carry each featured
    # item's impressions and engagements IN THEIR OWN TEXT, measured on a
    # capture of this page, so census row ``P G6`` needs no second page for
    # its headline numbers. Integers only; see ``post_summary_counts``.
    reading["per_post"] = await post_summary_counts.read_post_summary_counts(page)
    return reading
