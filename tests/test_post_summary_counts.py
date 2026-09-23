"""Pins for ``linkedin_server.post_summary_counts`` and its additive use
inside ``creator_analytics.read_content_analytics``.

The fixture (``tests/fixtures/synthetic/post_summary_counts.html``) is
entirely synthetic -- see its own header comment for what it reproduces, the
two anchor shapes it carries, and why every urn digit run is exactly five
ASCII digits. This file pins:

  a. ``parse_line`` over the accepted and refused shapes, including the
     length guard as a DIFFERENT failure reason than a shape mismatch.
  b. ``first_line``, including that it stops at the first non-blank line.
  c. ``tally`` over hand-built ``(href, text)`` pairs -- order, duplicates,
     the share-urn refusal, an unparsable line, and the two-zero-vs-none
     distinction between an empty engagements list and a drawn one.
  d. ``read_post_summary_counts`` against the fixture in a real headless
     chromium -- the exact reading, decoy by decoy.
  e. the published alphabet is closed, and no fixture text survives into a
     reading.
  f. the three failure paths (dead locator, one unreadable link, anchors
     beyond MAX_ANCHORS), against a small hand-written fake page.
  g. ``creator_analytics.read_content_analytics`` carries ``per_post``
     additively, even when every sub-reading is at its own zero.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from linkedin_server import creator_analytics, post_summary_counts

FIXTURE = (
    pathlib.Path(__file__).parent
    / "fixtures"
    / "synthetic"
    / "post_summary_counts.html"
)

#: chr(0xB7) is the middle dot LinkedIn draws between impressions and
#: engagements. Computing it at runtime keeps this file's source strictly
#: ASCII -- the same technique tests/test_follow_state_fixture.py,
#: tests/test_job_detail_fixture.py, tests/test_sdui_surfaces_fixture.py and
#: tests/test_tools.py already use for this exact character.
DOT = chr(0xB7)

#: An Arabic-Indic digit -- not an ASCII digit, so parse_line must refuse a
#: line built from it. Same technique tests/test_company_page.py uses for
#: its own Arabic-Indic construction.
ARABIC_INDIC_ONE = chr(0x0661)


async def _open(html, factory):
    """Load markup into a real headless page and run ``factory`` over it.

    Copied from ``tests/test_job_collections.py``'s ``_open`` helper, same
    pattern and same reason: never the signed-in profile at
    ``_state/chrome-profile``, always a throwaway chromium context.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await factory(page)
        finally:
            await browser.close()


async def _read_fixture():
    html = FIXTURE.read_text(encoding="utf-8")

    async def factory(page):
        return await post_summary_counts.read_post_summary_counts(page)

    return await _open(html, factory)


# ---------------------------------------------------------------------------
# a. parse_line
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line, expected",
    [
        ("7 impressions " + DOT + " 0 engagements", {"impressions": 7, "engagements": 0}),
        ("352 impressions", {"impressions": 352, "engagements": None}),
        ("1,234 impressions", {"impressions": 1234, "engagements": None}),
        ("12 Impressions", {"impressions": 12, "engagements": None}),
    ],
)
def test_parse_line_accepts_the_measured_shapes(line, expected):
    assert post_summary_counts.parse_line(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "View analytics",
        "Show stats",
        "",
        None,
        "7 engagements",
        "7 impressions and a name",
        "7 impressions " + DOT + " x engagements",
        ARABIC_INDIC_ONE + " impressions",  # not an ASCII digit
        (" " * 60) + "5 impressions" + (" " * 60),  # otherwise matches, too long
    ],
)
def test_parse_line_refuses_everything_else(line):
    assert post_summary_counts.parse_line(line) is None


def test_parse_line_refuses_on_length_not_shape():
    """THE LENGTH GUARD, ISOLATED FROM THE SHAPE CHECK. The padded string
    above is refused; this proves it is refused BECAUSE of its length and
    not because its shape was ever wrong -- its stripped form parses fine."""
    padded = (" " * 60) + "5 impressions" + (" " * 60)
    assert len(padded) > post_summary_counts.MAX_LINE_CHARS
    assert post_summary_counts.parse_line(padded) is None
    assert post_summary_counts.parse_line(padded.strip()) == {
        "impressions": 5,
        "engagements": None,
    }


# ---------------------------------------------------------------------------
# b. first_line
# ---------------------------------------------------------------------------


def test_first_line_returns_the_first_non_blank_line():
    text = "\n  \n7 impressions\nView analytics"
    assert post_summary_counts.first_line(text) == "7 impressions"


def test_first_line_is_none_for_none():
    assert post_summary_counts.first_line(None) is None


def test_first_line_is_none_when_the_first_line_is_too_long():
    """Stops AT the first non-blank line and refuses there -- it does not
    skip ahead to a later, shorter one."""
    long_first = "x" * (post_summary_counts.MAX_LINE_CHARS + 1)
    text = long_first + "\n7 impressions"
    assert post_summary_counts.first_line(text) is None


# ---------------------------------------------------------------------------
# c. tally, over hand-built (href, text) pairs -- no page involved
# ---------------------------------------------------------------------------


def test_tally_over_hand_built_pairs():
    pairs = [
        (
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:30001/",
            "5 impressions " + DOT + " 1 engagements",
        ),
        (
            # A share urn behind the post-summary marker -- not_activity_links.
            "https://www.linkedin.com/analytics/post-summary/urn:li:share:30002/",
            "9 impressions",
        ),
        (
            # An activity urn with an unparsable line -- unparsed.
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:30003/",
            "Show stats",
        ),
        (
            # A clean read with no engagements drawn.
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:30004/",
            "10 impressions",
        ),
        (
            # A second link to the first urn -- duplicate_links.
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:30001/",
            "5 impressions " + DOT + " 1 engagements",
        ),
    ]
    reading = post_summary_counts.tally(pairs)
    assert reading["anchors_seen"] == 5
    assert reading["items_read"] == 2
    assert reading["impressions"] == [5, 10]  # ORDER PRESERVED
    assert reading["engagements"] == [1, None]
    assert reading["total_impressions"] == 15
    assert reading["total_engagements"] == 1
    assert reading["engagements_drawn_for"] == 1
    assert reading["not_activity_links"] == 1
    assert reading["duplicate_links"] == 1
    assert reading["unparsed"] == 1
    assert reading["readable"] is True


def test_tally_total_engagements_is_none_when_none_drawn():
    """THE ZERO-VS-NONE DISTINCTION. An engagements list of all-None must not
    collapse to a total of 0 -- 0 would claim a measurement that was never
    taken."""
    pairs = [
        (
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:30005/",
            "3 impressions",
        ),
    ]
    reading = post_summary_counts.tally(pairs)
    assert reading["engagements"] == [None]
    assert reading["total_engagements"] is None
    assert reading["engagements_drawn_for"] == 0


def test_tally_is_unreadable_on_empty_input():
    reading = post_summary_counts.tally([])
    assert reading["readable"] is False
    assert reading["items_read"] == 0
    assert reading["anchors_seen"] == 0


# ---------------------------------------------------------------------------
# d. read_post_summary_counts, against the real fixture in a real browser
# ---------------------------------------------------------------------------


async def test_the_reader_produces_the_exact_reading_on_the_fixture():
    """THE EXACT READING, decoy by decoy.

    items_read is 5 (2 shape-A + 3 shape-B); D1 (outside main) never reaches
    the selector; D2 (a feed permalink) never matches the selector; D3 (a
    share urn behind the post-summary marker) lands in not_activity_links;
    D4 (a second link to B3's urn) lands in duplicate_links; D5 ("Show
    stats") lands in unparsed.
    """
    reading = await _read_fixture()
    assert reading["items_read"] == 5
    assert reading["impressions"] == [7, 1234, 352, 901, 42]
    assert reading["engagements"] == [0, 88, None, None, None]
    assert reading["total_impressions"] == 2536
    assert reading["total_engagements"] == 88
    assert reading["engagements_drawn_for"] == 2
    assert reading["not_activity_links"] == 1
    assert reading["duplicate_links"] == 1
    assert reading["unparsed"] == 1
    assert reading["readable"] is True
    assert reading["unreadable_links"] == 0
    assert reading["links_beyond_bound"] == 0
    # anchors_seen = 2 shape-A + D3 + D5 + 3 shape-B + D4 = 8. D1 sits
    # outside <main> and is never matched by SELECTOR at all -- it does not
    # even reach anchors_seen, unlike the three decoys counted above.
    assert reading["anchors_seen"] == 8


async def test_anchors_seen_equals_the_in_main_post_summary_links():
    """MEASURED OFF THE FIXTURE BY AN INDEPENDENT PARSE, never transcribed
    twice: every in-main href containing the post-summary marker, regardless
    of which urn family it names -- which is exactly what SELECTOR matches.

    The header comment is stripped first: it names "/analytics/post-summary/"
    several times in prose, and a bare substring count over the whole file
    would measure the comment's own explanation rather than the markup --
    the same discipline ``test_job_collections.py``'s ``_markup()`` applies
    for the same reason.
    """
    markup = FIXTURE.read_text(encoding="utf-8")
    stripped = re.sub(r"<!--.*?-->", "", markup, flags=re.S)
    main_only = stripped.split("<main>", 1)[-1].split("</main>", 1)[0]
    count = main_only.count("/analytics/post-summary/")

    reading = await _read_fixture()
    assert reading["anchors_seen"] == count


# ---------------------------------------------------------------------------
# e. the published alphabet is closed, and no fixture text leaks
# ---------------------------------------------------------------------------


def _strings_in(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings_in(item)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            yield from _strings_in(item)


async def test_every_emitted_string_is_in_the_declared_alphabet():
    reading = await _read_fixture()
    allowed = post_summary_counts.emitted_alphabet()
    for value in _strings_in(reading):
        assert value in allowed, value


async def test_no_fixture_text_survives_into_the_reading():
    reading = await _read_fixture()
    blob = json.dumps(reading)
    for leaked in (
        "A post title",
        "View analytics",
        "Show stats",
        "Feed post",
        "Analytics chart",
    ):
        assert leaked not in blob


# ---------------------------------------------------------------------------
# f. failure paths, with a small hand-written fake page -- no browser
# ---------------------------------------------------------------------------


class _FakeAnchor:
    """The smallest object that behaves like the locator handle we read."""

    def __init__(self, href, text, raises=False):
        self._href = href
        self._text = text
        self._raises = raises

    async def get_attribute(self, name):
        assert name == "href", name
        if self._raises:
            raise RuntimeError("element detached")
        return self._href

    async def inner_text(self):
        if self._raises:
            raise RuntimeError("element detached")
        return self._text


class _FakeLocator:
    def __init__(self, anchors, count_raises=False, count_override=None):
        self._anchors = anchors
        self._count_raises = count_raises
        self._count_override = count_override

    async def count(self):
        if self._count_raises:
            raise RuntimeError("locator died")
        if self._count_override is not None:
            return self._count_override
        return len(self._anchors)

    def nth(self, index):
        if index < len(self._anchors):
            return self._anchors[index]
        # count_override can promise more anchors than this fake actually
        # holds -- the reader must still be able to call .nth() for every
        # index up to MAX_ANCHORS without this fake raising, or the
        # boundedness test below would be failing on the fake, not proving
        # the bound.
        return self._anchors[-1]


class _FakePage:
    def __init__(self, anchors, count_raises=False, count_override=None):
        self._locator = _FakeLocator(
            anchors, count_raises=count_raises, count_override=count_override
        )

    def locator(self, selector):
        assert selector == post_summary_counts.SELECTOR, selector
        return self._locator


async def test_a_dead_count_locator_reports_zero_not_an_exception():
    page = _FakePage([], count_raises=True)
    reading = await post_summary_counts.read_post_summary_counts(page)
    assert reading["anchors_seen"] == 0
    assert reading["readable"] is False


async def test_one_unreadable_link_is_counted_and_the_rest_still_read():
    anchors = [
        _FakeAnchor(
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:40001/",
            "1 impressions",
        ),
        _FakeAnchor(None, None, raises=True),
        _FakeAnchor(
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:40002/",
            "2 impressions",
        ),
    ]
    page = _FakePage(anchors)
    reading = await post_summary_counts.read_post_summary_counts(page)
    assert reading["unreadable_links"] == 1
    assert reading["items_read"] == 2
    assert reading["impressions"] == [1, 2]


async def test_anchors_beyond_the_bound_are_counted_not_read():
    anchors = [
        _FakeAnchor(
            "https://www.linkedin.com/analytics/post-summary/urn:li:activity:40003/",
            "1 impressions",
        )
    ]
    page = _FakePage(anchors, count_override=post_summary_counts.MAX_ANCHORS + 3)
    reading = await post_summary_counts.read_post_summary_counts(page)
    assert reading["links_beyond_bound"] == 3
    assert reading["anchors_seen"] <= post_summary_counts.MAX_ANCHORS


# ---------------------------------------------------------------------------
# g. creator_analytics.read_content_analytics carries per_post, additively
# ---------------------------------------------------------------------------


class _EmptyLocator:
    async def count(self):
        return 0

    def nth(self, index):  # pragma: no cover -- count is always 0
        raise AssertionError("nth() called on a locator that reported zero")


class _EmptyPage:
    """No labels and no anchors of any kind -- proves the additive claim
    holds even when every sub-reading is at its own zero. One fake serves
    all three locator calls (aria-label nodes, a[href], and the post-summary
    SELECTOR) because none of them ever reach .nth() at count 0."""

    def locator(self, selector):
        return _EmptyLocator()


async def test_read_content_analytics_carries_per_post_additively():
    reading = await creator_analytics.read_content_analytics(_EmptyPage())
    expected_keys = {
        "points_found",
        "labels_seen",
        "nav_labels_excluded",
        "unrecognised_labels",
        "metrics",
        "by_metric",
        "scope",
        "readable",
        "route",
        "item_addresses",
        "per_post",
    }
    assert expected_keys <= set(reading)
    assert reading["per_post"]["readable"] is False
