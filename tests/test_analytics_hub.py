"""Pins for ``linkedin_server.analytics_hub``, the reader of his analytics hub
(``/dashboard/``, census row ``P L8``), over the TRACKED skeleton
``tests/fixtures/live1/overview.html``.

The fixture is the live lane's session-1 capture of the page reduced by
``scripts/_build_dashboard_fixture.py``: the capture's structure, LinkedIn's
own label, period, path and icon words restored by keyed hash, and every value,
delta and date DECLARED SYNTHETIC (the builder's ``SYNTHETIC_*`` constants:
41 / 512 / 63 / 27, deltas 12% / 3% / 50% / 0%). So every number asserted
below is one the builder invented, and every word is one LinkedIn drew.

THE PLANTS, each shown changing the verdict against the unplanted reading:

* a card whose LABEL is outside the vocabulary -> counted unrecognised, and
  the card is not returned;
* a card whose LINK points outside ``/analytics/`` -> not a card at all;
* a NAME planted in the ``aside`` (his profile card's place) -> never in the
  output, and the reading does not move;
* a VALUE node holding words -> value ``None``, the rest of the card kept;
* a delta drawn with NO direction icon and not zero -> delta ``None``;
* a label naming ANOTHER metric than its link -> unrecognised (both closed
  vocabularies must agree; neither is trusted alone).
"""

from __future__ import annotations

import asyncio
import json
import pathlib

import pytest

from linkedin_server import analytics_hub

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "live1" / "overview.html"

#: Name-shaped and synthetic: the shape guard's own vocabulary admits it.
PLANTED_NAME = "Exampleperson Markersurname"

EXPECTED_METRICS = {
    "followers": {
        "value": 512, "delta": 3, "direction": "increase",
        "window": "total", "period": "vs_prior_7_days",
    },
    "post_impressions": {
        "value": 41, "delta": -12, "direction": "decrease",
        "window": "7_days", "period": "vs_prior_7_days",
    },
    "profile_viewers": {
        "value": 63, "delta": 50, "direction": "increase",
        "window": "90_days", "period": "vs_prior_7_days",
    },
    "search_appearances": {
        "value": 27, "delta": 0, "direction": "unchanged",
        "window": "dated_range", "period": "vs_prior_dated_range",
    },
}


def _fixture() -> str:
    return FIXTURE.read_text(encoding="ascii")


async def _read_all(variants: dict[str, str]) -> dict[str, dict]:
    """Every variant's reading, from ONE throwaway headless chromium.

    Never the signed-in profile. ONE launch for all variants because a launch
    measured 13.75 s on this box on 2026-10-10 while a load on a running
    browser costs well under one; nothing crosses between variants, since each
    load replaces the whole document. The skeleton keeps its stylesheet and
    image addresses' path words, so every request is refused in the page's
    own route before it can leave (the network guard's rule)."""
    playwright = pytest.importorskip("playwright.async_api")
    out: dict[str, dict] = {}
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})

            async def _refuse(route) -> None:  # noqa: ANN001 - playwright route
                await route.abort()

            await page.route("**/*", _refuse)
            for name, html in variants.items():
                await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
                out[name] = await analytics_hub.read_analytics_hub(page)
        finally:
            await browser.close()
    return out


def _planted(html: str, old: str, new: str, count: int = 1) -> str:
    """``html`` with ``old`` replaced -- asserting the fixture draws it exactly
    ``count`` times first, so a plant that misses is a red, not a no-op."""
    assert html.count(old) == count, f"the fixture no longer draws {old!r} {count} time(s)"
    return html.replace(old, new)


# ---------------------------------------------------------------------------
# a. the pure half: strings in, closed words out
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "href, metric",
    [
        ("https://www.linkedin.com/analytics/creator/content/", "post_impressions"),
        ("https://www.linkedin.com/analytics/creator/audience/", "followers"),
        ("https://www.linkedin.com/analytics/profile-views/", "profile_viewers"),
        ("https://www.linkedin.com/analytics/search-appearances/", "search_appearances"),
        ("/analytics/profile-views/", "profile_viewers"),
    ],
)
def test_a_card_address_names_its_metric(href, metric):
    assert analytics_hub.classify_href(href) == ("card", metric)


@pytest.mark.parametrize(
    "href, kind",
    [
        ("https://www.linkedin.com/feed/", "not_a_card"),
        ("https://www.linkedin.com/dashboard/share/", "not_a_card"),
        ("https://www.linkedin.com/analytics/creator/top-posts/", "card"),
        ("https://www.example.com/analytics/profile-views/", "not_a_card"),
        (PLANTED_NAME, "not_a_card"),
        (None, "not_a_card"),
    ],
)
def test_an_address_outside_the_four_names_no_metric(href, kind):
    assert analytics_hub.classify_href(href) == (kind, None)


def test_the_dated_label_and_period_are_closed_grammars():
    dash = chr(0x2013)
    assert analytics_hub.classify_label("Search appearances Jan 12" + dash + "18") == (
        "search_appearances", "dated_range")
    assert analytics_hub.classify_period("vs. Jan 5" + dash + "11") == "vs_prior_dated_range"
    assert analytics_hub.classify_label("Search appearances " + PLANTED_NAME) is None
    assert analytics_hub.classify_period("vs. " + PLANTED_NAME) is None
    assert analytics_hub.classify_label("Search appearances Jan 12-18") is None  # hyphen, not en dash


def test_a_card_is_judged_by_the_shape_of_its_texts_not_their_order():
    texts = ["vs. prior 7 days", "12%", "41", "Post impressions in 7 days"]
    card = analytics_hub.read_card("post_impressions", texts, ["caret-small"])
    assert card == EXPECTED_METRICS["post_impressions"]


@pytest.mark.parametrize(
    "drawn, value",
    [("41", 41), ("1234", 1234), ("1,234", 1234), ("12,345,678", 12345678),
     ("1.2K", None), ("12,34", None), ("forty-one", None), ("1234567890", None)],
)
def test_a_value_is_ascii_digits_plain_or_grouped_and_nothing_else(drawn, value):
    texts = [drawn, "Post impressions in 7 days", "12%", "vs. prior 7 days"]
    assert analytics_hub.read_card("post_impressions", texts, ["caret-small"])["value"] == value


def test_two_values_in_one_card_are_ambiguous_and_read_none():
    texts = ["41", "42", "Post impressions in 7 days", "12%", "vs. prior 7 days"]
    assert analytics_hub.read_card("post_impressions", texts, ["caret-small"])["value"] is None


def test_an_unknown_icon_signs_nothing():
    texts = ["41", "Post impressions in 7 days", "12%", "vs. prior 7 days"]
    card = analytics_hub.read_card("post_impressions", texts, ["arrow-sideways-small"])
    assert card["delta"] is None and card["direction"] is None


def test_a_metric_drawn_twice_is_returned_by_neither_card():
    card = (
        "https://www.linkedin.com/analytics/creator/audience/",
        ["512", "Total followers", "3%", "vs. prior 7 days"],
        ["caret-up-small"],
    )
    reading = analytics_hub.tally([card, card], links_seen=2)
    assert reading["metrics"] == {}
    assert reading["metrics_drawn_twice"] == 1


# ---------------------------------------------------------------------------
# b. the reader over the tracked skeleton, and the plants
# ---------------------------------------------------------------------------


def _variants() -> dict[str, str]:
    html = _fixture()
    return {
        "baseline": html,
        "label_outside_vocabulary": _planted(html, "\nTotal followers\n", "\nTotal connections\n"),
        "link_outside_analytics": _planted(
            html,
            'href="https://www.linkedin.com/analytics/profile-views/"',
            'href="https://www.linkedin.com/feed/"',
        ),
        "name_in_aside": _planted(
            html, "<aside", '<aside data-plant="1"><p>' + PLANTED_NAME + "</p></aside><aside", count=2
        ),
        "name_in_label": _planted(html, "\nProfile viewers in 90 days\n", "\n" + PLANTED_NAME + "\n"),
        "value_holds_words": _planted(html, "\n512\n", "\nfive hundred\n"),
        "delta_without_icon": _planted(html, "\n0%\n", "\n7%\n"),
        "label_names_another_metric": _planted(
            html, "\nPost impressions in 7 days\n", "\nProfile viewers in 90 days\n"
        ),
        "no_card": '<html><body><main><section aria-label="x"><p>x</p></section></main></body></html>',
    }


@pytest.fixture(scope="module")
def readings() -> dict[str, dict]:
    return asyncio.run(_read_all(_variants()))


def test_the_reader_produces_the_exact_reading_on_the_tracked_skeleton(readings):
    reading = readings["baseline"]
    assert reading["metrics"] == EXPECTED_METRICS
    assert reading["cards_seen"] == 4
    assert reading["cards_parsed"] == 4
    assert reading["labels_unrecognised"] == 0
    assert reading["paths_unrecognised"] == 0
    assert reading["links_seen"] == 6  # four cards and two "Weekly progress" links
    assert reading["links_not_cards"] == 2
    assert reading["readable"] is True


def test_every_string_in_every_reading_is_the_modules_own(readings):
    strings = set()

    def walk(value):
        if isinstance(value, str):
            strings.add(value)
        elif isinstance(value, dict):
            for key, item in value.items():
                strings.add(key)
                walk(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item)

    for reading in readings.values():
        walk(reading)
    assert strings <= analytics_hub.emitted_alphabet()


def test_a_label_outside_the_vocabulary_is_unrecognised_and_not_returned(readings):
    reading = readings["label_outside_vocabulary"]
    assert "followers" not in reading["metrics"]
    assert reading["labels_unrecognised"] == 1
    assert reading["cards_seen"] == 4
    assert reading["cards_parsed"] == 3


def test_a_card_linking_outside_analytics_is_not_a_card(readings):
    reading = readings["link_outside_analytics"]
    assert "profile_viewers" not in reading["metrics"]
    assert reading["cards_seen"] == 3
    assert reading["links_not_cards"] == 3
    assert reading["labels_unrecognised"] == 0


def test_a_name_in_the_aside_never_reaches_the_output(readings):
    reading = readings["name_in_aside"]
    assert PLANTED_NAME not in json.dumps(reading)
    assert reading == readings["baseline"]


def test_a_name_in_a_card_label_never_reaches_the_output(readings):
    reading = readings["name_in_label"]
    assert PLANTED_NAME not in json.dumps(reading)
    assert "profile_viewers" not in reading["metrics"]
    assert reading["labels_unrecognised"] == 1


def test_a_value_node_holding_words_reads_none(readings):
    reading = readings["value_holds_words"]
    followers = reading["metrics"]["followers"]
    assert followers["value"] is None
    assert followers["delta"] == 3
    assert "five hundred" not in json.dumps(reading)


def test_a_nonzero_delta_with_no_direction_icon_reads_none(readings):
    card = readings["delta_without_icon"]["metrics"]["search_appearances"]
    assert card["delta"] is None
    assert card["direction"] is None
    assert card["value"] == 27


def test_a_label_naming_another_metric_than_its_link_is_unrecognised(readings):
    reading = readings["label_names_another_metric"]
    assert "post_impressions" not in reading["metrics"]
    assert reading["metrics"]["profile_viewers"] == EXPECTED_METRICS["profile_viewers"]
    assert reading["labels_unrecognised"] == 1


def test_a_page_that_draws_no_card_is_unreadable_not_zero(readings):
    reading = readings["no_card"]
    assert reading["cards_seen"] == 0
    assert reading["metrics"] == {}
    assert reading["readable"] is False
