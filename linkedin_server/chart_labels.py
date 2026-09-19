"""THE ANALYTICS NUMBERS ARE IN THE ACCESSIBLE NAMES, NOT IN THE TEXT.

Measured 2026-09-19 on `/analytics/creator/content/`, an address the read
boundary already admits. The whole document carries **1,869 characters of
text** -- `main` holds 1,690 of them -- with **zero** `h3`, `h4`, `table` or
`canvas`, and 56 `svg` nodes. A text reader gets nothing from it, and four
still-GAP rows depend on it::

    M C38  View post analytics (impressions, viewer demographics)
    M C39  View analytics for your comments
    M C40  View your creator analytics
    P G6   Per-post analytics

The values are on the chart nodes as ``aria-label``, which is how LinkedIn
renders those charts to a screen reader::

    "Sunday, Sep 13, 2026, 0. Impressions."
    "Tuesday, Sep 15, 2026, 2. Impressions."

**That is a date, a value and a metric, already separated.** This module is
the pure half: strings in, a series out. It does no IO and opens no page.

## THE DISCRIMINATION PROBLEM, WHICH IS THE WHOLE DIFFICULTY

The same page carries 34 ``aria-label`` nodes and **most of them are the nav**::

    "Home, 1 new notification"
    "Notifications, 6 new notifications"

Both families are "a phrase with a digit in it". A reader that takes every
labelled node with a number in it reports the notification badge as an
analytics datapoint. **So a label is admitted only when it carries a DATE and
a metric**, which the nav labels never do -- selection is by STRUCTURE, not by
position and not by "has a digit".

## A ZERO HERE IS THE SELF-CONTROLLING KIND, SO IT CARRIES ITS DENOMINATOR

The measured account reads **0 impressions on most days**. That is the true
answer, and it is also exactly what a broken reader returns. The two are
indistinguishable from the value alone, so :func:`series` reports
``points_found`` beside the values and :func:`is_readable` exists for a caller
to ask BEFORE believing a zero:

    points_found 0   ->  the reader reached nothing. NOT "zero impressions".
    points_found 7, values all 0  ->  genuinely zero, on seven days.

**This repository has paid for the collapsed version of this twice today**, so
the distinction is a function rather than a comment.

## IT CANNOT EMIT A NAME, BY CONSTRUCTION

The parser returns a date string, an integer and a metric drawn from a CLOSED
vocabulary. **Anything it cannot parse into that shape is discarded**, so a
label containing a person's name cannot reach the output even if LinkedIn
starts putting one there -- the output has nowhere to put it.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Optional

#: Metrics this module will name. CLOSED, for the same reason the press gate's
#: shapes are: an open vocabulary is a place for arbitrary page text to land.
#:
#: **ONLY ONE OF THESE HAS BEEN SEEN, AND THE LIST IS NOT A COVERAGE CLAIM.**
#: `impressions` is the only metric measured live (7 points, 2026-09-19). The
#: rest are spellings this parser would ACCEPT if LinkedIn drew them -- which
#: is not the same as metrics it can reach, and the difference is a boundary
#: fact rather than a parsing one:
#:
#:     readonly admits `/analytics/creator/content/` ANCHORED, with NO query
#:     group, and LinkedIn's analytics pages select a metric with
#:     `?metricType=`.
#:
#: So **the admitted address serves the DEFAULT view and nothing else**, and
#: reaching another metric is an allowlist decision, not a reader improvement.
#: Listing seven here and letting a reader infer seven are reachable would be
#: the same overstatement as naming a readable counter "priced_by" -- a
#: vocabulary is a claim about what can be PARSED, never about what can be
#: REACHED.
KNOWN_METRICS = (
    "impressions",      # MEASURED LIVE 2026-09-19
    "engagements",      # accepted if drawn; NOT reachable at the admitted url
    "members reached",  # ditto
    "reactions",        # ditto
    "comments",         # ditto
    "reposts",          # ditto
    "followers",        # ditto
)

#: The subset actually observed. A caller reporting coverage should read THIS,
#: not the vocabulary above.
MEASURED_METRICS = ("impressions",)

#: "Sunday, Sep 13, 2026, 0. Impressions."
#: Deliberately anchored at BOTH ends. An unanchored search would match the
#: same shape embedded in a longer sentence, and a longer sentence is exactly
#: where prose (and a name) would be.
_POINT = re.compile(
    r"^\s*(?P<weekday>[A-Za-z]{3,9}),\s*"
    r"(?P<date>[A-Za-z]{3,9}\s+\d{1,2},\s*\d{4}),\s*"
    r"(?P<value>\d[\d,]*)\s*\.\s*"
    r"(?P<metric>[A-Za-z][A-Za-z ]{0,30}?)\s*\.?\s*$"
)

#: The nav family, recorded so the exclusion is explicit rather than implied by
#: the point pattern failing to match. A reader that only says what it KEPT
#: cannot be audited for what it dropped.
_NAV = re.compile(
    r"^\s*[A-Za-z][A-Za-z ]{0,30},\s*\d+\s+new\s+notifications?\s*\.?\s*$",
    re.IGNORECASE,
)


def _as_int(digits: str) -> Optional[int]:
    try:
        return int(digits.replace(",", ""))
    except (TypeError, ValueError):
        return None


def classify(label: Optional[str]) -> str:
    """What FAMILY is this label? ``point`` / ``nav`` / ``other``.

    Exported because the counts of all three are the denominator that makes a
    zero readable, and a caller that cannot see ``other`` cannot tell a page
    that changed shape from a page with no data.
    """
    if not isinstance(label, str) or not label.strip():
        return "other"
    if _NAV.match(label):
        return "nav"
    m = _POINT.match(label)
    if not m:
        return "other"
    if m.group("metric").strip().lower() not in KNOWN_METRICS:
        return "other"
    return "point"


def parse_point(label: Optional[str]) -> Optional[dict[str, Any]]:
    """One datapoint, or None. NEVER a partial one."""
    if classify(label) != "point":
        return None
    m = _POINT.match(label)  # type: ignore[arg-type]
    assert m is not None
    value = _as_int(m.group("value"))
    if value is None:
        return None
    return {
        "date": m.group("date").strip(),
        "value": value,
        "metric": m.group("metric").strip().lower(),
    }


def series(labels: Iterable[Optional[str]]) -> dict[str, Any]:
    """A metric series with the denominator it was taken over.

    **The counts are not diagnostics.** ``points_found`` is what makes a run
    of zeros a reading rather than a silence, and ``other`` is what shows the
    page still has the shape this parser was written against.
    """
    seen = list(labels or [])
    points, nav, other = [], 0, 0
    for label in seen:
        kind = classify(label)
        if kind == "nav":
            nav += 1
        elif kind == "point":
            parsed = parse_point(label)
            if parsed is None:
                other += 1
            else:
                points.append(parsed)
        else:
            other += 1

    by_metric: dict[str, list[dict[str, Any]]] = {}
    for point in points:
        by_metric.setdefault(point["metric"], []).append(point)

    return {
        "points_found": len(points),
        "labels_seen": len(seen),
        "nav_labels_excluded": nav,
        "unrecognised_labels": other,
        "metrics": sorted(by_metric),
        "by_metric": {
            metric: {
                "points": len(rows),
                "total": sum(r["value"] for r in rows),
                "dates": [r["date"] for r in rows],
                "values": [r["value"] for r in rows],
            }
            for metric, rows in sorted(by_metric.items())
        },
        # THE BOUND TRAVELS WITH THE READING. A caller that reads `total` 0
        # without this is reading a claim about the account when the
        # measurement may be about the reader.
        "scope": (
            "chart accessible-names on one analytics page. A zero total is "
            "only a reading about the account when points_found > 0; with "
            "points_found 0 the reader reached nothing and the account is "
            "UNMEASURED."
        ),
    }


def is_readable(reading: Optional[dict[str, Any]]) -> bool:
    """Would any number in this reading be worth acting on? ASK BEFORE BELIEVING.

    A series over no points answers nothing, and every total in it would read
    0 -- which is the self-controlling zero this repository keeps paying for.
    """
    if not isinstance(reading, dict):
        return False
    return int(reading.get("points_found") or 0) > 0
