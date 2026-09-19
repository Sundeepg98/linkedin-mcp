"""The chart-label parser, SHOWN REFUSING before it is trusted to accept.

Every string in `LIVE_*` below was read off `/analytics/creator/content/` on
2026-09-19 by `scripts/_probe_creator_content_analytics.py`. They are the
reason this parser exists and they are the corpus it is pinned to: a parser
tested only on strings its author invented is tested against its own
assumptions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import chart_labels  # noqa: E402

#: MEASURED LIVE. Chart datapoints.
LIVE_POINTS = [
    "Sunday, Sep 13, 2026, 0. Impressions.",
    "Monday, Sep 14, 2026, 0. Impressions.",
    "Tuesday, Sep 15, 2026, 2. Impressions.",
]

#: MEASURED LIVE, on the SAME page. The nav, which any "has a digit" reader
#: would have swallowed as analytics data.
LIVE_NAV = [
    "Home, 1 new notification",
    "My Network, 0 new notifications",
    "Jobs, 0 new notifications",
    "Messaging, 0 new notifications",
    "Notifications, 6 new notifications",
    "Learning, 0 new notifications",
]


# ---------------------------------------------------------------------------
# SHOWN REFUSING FIRST
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", LIVE_NAV)
def test_the_nav_is_excluded_and_named_as_nav(label):
    """THE CASE THAT MOTIVATES THE PARSER.

    These carry digits and sit on the same page. A reader selecting labelled
    nodes with numbers in them reports the notification badge as impressions.
    """
    assert chart_labels.classify(label) == "nav"
    assert chart_labels.parse_point(label) is None


@pytest.mark.parametrize("label", [
    "",
    None,
    "<opaque>",
    "Sunday, Sep 13, 2026, 0. Impressions. Posted by a person named here",
    "Jane Doe, Sep 13, 2026, 4. Impressions.",
    "Sunday, Sep 13, 2026, 5. Fascinations.",
    "Sunday, Sep 13, 2026. Impressions.",
    "0. Impressions.",
    12,
])
def test_anything_that_is_not_the_measured_shape_is_refused(label):
    """A NAME CANNOT REACH THE OUTPUT, and neither can a novel metric.

    The fourth case is the important one: the datapoint shape with prose
    appended. An unanchored pattern would match the prefix and emit a point
    from a sentence -- which is where a name would be.
    """
    assert chart_labels.parse_point(label) is None
    assert chart_labels.classify(label) in ("other", "nav")


# ---------------------------------------------------------------------------
# THEN ACCEPTING
# ---------------------------------------------------------------------------


def test_a_measured_datapoint_parses_to_date_value_metric():
    assert chart_labels.parse_point(LIVE_POINTS[2]) == {
        "date": "Sep 15, 2026",
        "value": 2,
        "metric": "impressions",
    }


def test_a_thousands_separator_is_a_number_not_a_refusal():
    got = chart_labels.parse_point("Friday, Sep 11, 2026, 12,431. Impressions.")
    assert got is not None and got["value"] == 12431


# ---------------------------------------------------------------------------
# THE SELF-CONTROLLING ZERO -- the reason this module has is_readable
# ---------------------------------------------------------------------------


def test_a_run_of_real_zeros_is_readable_and_totals_zero():
    """THE TRUE ANSWER FOR THIS ACCOUNT, and it must not look like failure."""
    reading = chart_labels.series(LIVE_POINTS + LIVE_NAV)

    assert reading["points_found"] == 3
    assert reading["nav_labels_excluded"] == 6
    assert reading["by_metric"]["impressions"]["total"] == 2
    assert reading["by_metric"]["impressions"]["values"] == [0, 0, 2]
    assert chart_labels.is_readable(reading) is True


def test_zero_points_is_unmeasured_and_is_not_zero_impressions():
    """THE DISTINCTION THIS REPOSITORY HAS PAID FOR TWICE TODAY."""
    empty = chart_labels.series([])
    nav_only = chart_labels.series(LIVE_NAV)

    for reading in (empty, nav_only):
        assert reading["points_found"] == 0
        assert reading["by_metric"] == {}
        assert chart_labels.is_readable(reading) is False

    # And the two are distinguishable from each other, which is the point of
    # reporting the denominator rather than only the verdict.
    assert empty["labels_seen"] == 0
    assert nav_only["labels_seen"] == 6
    assert nav_only["nav_labels_excluded"] == 6


def test_the_scope_bound_always_travels():
    reading = chart_labels.series(LIVE_POINTS)
    assert "UNMEASURED" in reading["scope"]
    assert "points_found" in reading["scope"]


def test_unrecognised_labels_are_counted_not_dropped_silently():
    """If LinkedIn changes the shape, the reading must SAY so.

    A parser that reports only what it kept goes quiet on a page that changed
    under it, and a quiet parser reads as an account with no data.
    """
    reading = chart_labels.series(LIVE_POINTS + ["Something Else Entirely"])
    assert reading["points_found"] == 3
    assert reading["unrecognised_labels"] == 1


def test_the_output_has_nowhere_to_put_a_name():
    """Structural, not a filter: the shape itself excludes free text."""
    reading = chart_labels.series(LIVE_POINTS)
    point_keys = set()
    for rows in reading["by_metric"].values():
        point_keys |= set(rows)
    assert point_keys == {"points", "total", "dates", "values"}
    assert set(chart_labels.parse_point(LIVE_POINTS[0])) == {
        "date", "value", "metric"
    }
    for metric in reading["metrics"]:
        assert metric in chart_labels.KNOWN_METRICS


def test_the_vocabulary_is_not_a_coverage_claim():
    """PARSEABLE IS NOT REACHABLE, and the module must not let them blur.

    Seven metrics are accepted; ONE has been seen. The admitted address is
    anchored with no query group and LinkedIn selects a metric with
    ``?metricType=``, so the other six are an allowlist decision away, not a
    reader improvement. A caller reporting coverage reads MEASURED_METRICS.
    """
    assert chart_labels.MEASURED_METRICS == ("impressions",)
    assert set(chart_labels.MEASURED_METRICS) < set(chart_labels.KNOWN_METRICS)
    assert len(chart_labels.KNOWN_METRICS) > len(chart_labels.MEASURED_METRICS)
