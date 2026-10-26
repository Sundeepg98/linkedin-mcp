"""The People tab's insight cards, read over REAL captured markup (census J 108).

Every reading here runs ``company_people_insights.read_people_insights`` over
``tests/fixtures/live2/company_people_insights.html`` -- the live lane's
session-2 capture of one organisation's People tab, its carousel's LinkedIn
words measured against the session key and its rows' labels and counts
synthetic (``scripts/_build_company_people_insights_skeleton.py``) -- through
``tests/skeleton_page.py``, which answers Playwright's locators from the
parsed document with no browser. Plants are made by editing that document's
text before it is parsed, so each one sits in the markup LinkedIn drew.

Every name-shaped string in this file is synthetic.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import company_people_insights as cpi
from linkedin_server import people_data
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "live2"
INSIGHTS = FIXTURES / "company_people_insights.html"
BASE_CAPTURE = FIXTURES / "company_people.html"
URL = "https://www.linkedin.com/company/5417062/people/"

#: A marker no fixture draws: where it is planted, it must come back only
#: inside a record, or not at all.
MARKER = "Exampleperson Markersurname"

#: The cards, in the order the capture draws them.
ORDER = [key for key, _heading, _facet in cpi.CARDS]


def _markup(text: str = "") -> str:
    return text or INSIGHTS.read_text(encoding="ascii")


def read(markup: str = "", page_class: type = SkeletonPage) -> tuple[dict[str, Any], Any]:
    page = page_class(PlantedPage(), parse(_markup(markup)), url=URL)
    result = asyncio.run(cpi.read_people_insights(page))
    return result, page


def by_facet(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {card["facet"]: card for card in result["cards"]}


def strings_in(value: Any, path: tuple = ()):
    """Every string in ``value`` with the path that holds it, keys included."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield path + ("<key>",), str(key)
            yield from strings_in(item, path + (key,))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            yield from strings_in(item, path + (index,))


def _replace_once(markup: str, old: str, new: str) -> str:
    assert markup.count(old) >= 1, "the fixture no longer draws what this plant edits"
    return markup.replace(old, new, 1)


# ---------------------------------------------------------------------------
# 1. The measured cards come back, with synthetic labels and integer counts
# ---------------------------------------------------------------------------


def test_the_six_measured_cards_come_back_in_page_order():
    result, page = read()
    assert page.unmodelled == [] and page.planted_answers == []
    assert [card["facet"] for card in result["cards"]] == ORDER
    assert [card["heading"] for card in result["cards"]] == [h for _k, h, _f in cpi.CARDS]
    assert result["cards_returned"] == 6
    assert result["headings_unrecognised"] == result["parts_seen"] - 27 - 6
    assert result["rows_in_unreturned_cards"] == 0
    assert result["rows_before_any_heading"] == 0
    assert result["reads_failed"] == 0
    assert result["truncated"] is False


def test_each_category_row_is_a_record_and_an_integer():
    cards = by_facet(read()[0])
    stems = {
        "where_they_live": "Example place",
        "where_they_studied": "Example school",
        "what_they_do": "Example title",
        "what_they_are_skilled_at": "Example skill",
        "what_they_studied": "Example field",
    }
    for key, stem in stems.items():
        card = cards[key]
        assert card["rows_seen"] == 5 and len(card["rows"]) == 5, key
        assert all(n == 0 for n in card["rows_withheld"].values()), key
        for index, row in enumerate(card["rows"]):
            assert set(row) == {"label", "label_truncated", "count"}
            assert row["label"] == {
                "label": f"{stem} {index + 1}",
                people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
            }
            assert type(people_data.as_record(row["label"])) is people_data.Category
            assert row["label_truncated"] is False
            assert isinstance(row["count"], int) and not isinstance(row["count"], bool)
    # The synthetic counts keep the measured digits: grouped from four up.
    assert [row["count"] for row in cards["where_they_live"]["rows"]] == [9000, 8000, 900, 800, 700]
    assert [row["count"] for row in cards["where_they_studied"]["rows"]] == [90, 80, 70, 60, 50]


def test_the_connection_card_is_degree_counts_and_no_record():
    card = by_facet(read()[0])[cpi.CONNECTION_CARD]
    assert card["heading"] == "How you are connected"
    assert card["rows"] == [{"degree": "3rd+", "count": 9000}, {"degree": "2nd", "count": 900}]
    assert card["rows_withheld"]["not_a_degree"] == 0


def test_the_base_capture_with_its_headings_reduced_returns_no_card():
    """THE SAME MARKUP WITH EVERY HEADING REDUCED TO x: every card is counted
    as unrecognised and nothing of it is returned or read."""
    result, _page = read(BASE_CAPTURE.read_text(encoding="ascii"))
    assert result["cards"] == []
    assert result["rows_in_unreturned_cards"] == 27
    assert result["headings_unrecognised"] == result["parts_seen"] - 27


# ---------------------------------------------------------------------------
# 2. The plants
# ---------------------------------------------------------------------------


def test_an_unknown_heading_is_counted_and_never_returned():
    markup = _replace_once(_markup(), "\nWhere they live\n", "\nWhere they work\n")
    result, _page = read(markup)
    assert "where_they_live" not in by_facet(result)
    assert [card["facet"] for card in result["cards"]] == ORDER[1:]
    assert result["rows_in_unreturned_cards"] == 5
    baseline, _ = read()
    assert result["headings_unrecognised"] == baseline["headings_unrecognised"] + 1
    assert not any("Where they work" in text for _p, text in strings_in(result))


def test_a_repeated_heading_is_counted_and_its_rows_are_not_read():
    markup = _replace_once(_markup(), "\nWhere they studied\n", "\nWhere they live\n")
    result, _page = read(markup)
    assert [card["facet"] for card in result["cards"]] == [ORDER[0]] + ORDER[2:]
    assert result["headings_repeated"] == 1
    assert result["rows_in_unreturned_cards"] == 5


@pytest.mark.parametrize("drawn, shape", [
    ("9.5K", "abbreviated_refused"),
    ("9.5", "decimal_refused"),
    ("95%", "percent_refused"),
    ("12345678901", "too_long_refused"),
    (MARKER, "not_a_count"),
])
def test_a_count_that_is_not_digits_withholds_its_row(drawn, shape):
    markup = _replace_once(_markup(), "\n9,000\n", "\n" + drawn + "\n")
    result, _page = read(markup)
    card = by_facet(result)["where_they_live"]
    assert len(card["rows"]) == 4 and card["rows_seen"] == 5
    assert card["rows_withheld"]["count_refused"] == 1
    assert card["counts_refused_by_shape"][shape] == 1
    assert [row["label"]["label"] for row in card["rows"]][0] == "Example place 2"
    assert not any(drawn in text for _p, text in strings_in(result))


def test_more_rows_than_the_bound_are_counted_and_not_read():
    markup = _markup()
    start = markup.index('<a role="checkbox"', markup.index("facetGeoRegion") - 400)
    end = markup.index("</a>", start) + len("</a>")
    row = markup[start:end]
    extra = cpi.ROWS_PER_CARD + 3 - 5
    result, _page = read(markup[:end] + ("\n" + row) * extra + markup[end:])
    card = by_facet(result)["where_they_live"]
    assert card["rows_seen"] == cpi.ROWS_PER_CARD + 3
    assert len(card["rows"]) == cpi.ROWS_PER_CARD
    assert card["rows_beyond_bound"] == 3
    assert card["truncated"] is True and result["truncated"] is True


def test_markup_and_control_characters_in_a_label_leave_inert_and_marked():
    planted = ("Example &lt;b&gt;place&lt;/b&gt;" + chr(0x202E) + chr(0x07)
               + chr(0x200B) + " &lt;script&gt;x&lt;/script&gt; 1")
    markup = _replace_once(_markup(), "\nExample place 1\n", "\n" + planted + "\n")
    row = by_facet(read(markup)[0])["where_they_live"]["rows"][0]
    assert row["label"]["label"] == "Example <b>place</b> <script>x</script> 1"
    assert people_data.UNTRUSTED_KEY in row["label"]
    assert not any(ord(ch) < 32 or ch in (chr(0x202E), chr(0x200B)) for ch in row["label"]["label"])


def test_an_over_long_label_is_capped_and_flagged():
    long_label = "Example " + "x" * (people_data.CAPS["label"] * 2)
    markup = _replace_once(_markup(), "\nExample place 1\n", "\n" + long_label + "\n")
    row = by_facet(read(markup)[0])["where_they_live"]["rows"][0]
    assert len(row["label"]["label"]) == people_data.CAPS["label"]
    assert row["label_truncated"] is True


def test_a_connection_row_that_is_not_a_degree_is_withheld_and_counted():
    """THE WHO CAVEAT, PLANTED: if LinkedIn drew a person in this card, the
    row is withheld, no record is built for it, and the name goes nowhere."""
    markup = _replace_once(_markup(), "\n3rd+\n", "\n" + MARKER + "\n")
    result, _page = read(markup)
    card = by_facet(result)[cpi.CONNECTION_CARD]
    assert card["rows"] == [{"degree": "2nd", "count": 900}]
    assert card["rows_withheld"]["not_a_degree"] == 1
    assert not any(MARKER in text for _p, text in strings_in(result))


def test_a_row_carrying_another_cards_facet_is_withheld():
    markup = _replace_once(_markup(), "?facetGeoRegion=x", "?facetSchool=x")
    card = by_facet(read(markup)[0])["where_they_live"]
    assert card["rows_withheld"]["facet_parameter_disagrees"] == 1
    assert len(card["rows"]) == 4


# ---------------------------------------------------------------------------
# 3. Nothing of a label reaches a log or an exception
# ---------------------------------------------------------------------------


def test_a_planted_label_leaves_only_inside_a_record_and_never_in_a_log(caplog):
    caplog.set_level(logging.DEBUG)
    markup = _replace_once(_markup(), "\nExample skill 3\n", "\n" + MARKER + "\n")
    result, _page = read(markup)
    holders = [path for path, text in strings_in(result) if MARKER in text]
    assert holders and all(path[-2:] == ("label", "label") for path in holders), holders
    assert MARKER not in caplog.text


class _RaisingTextPage(SkeletonPage):
    """Every ``inner_text`` raises an error QUOTING the marker, as a
    Playwright error can quote the element it failed on."""

    def locator(self, selector, **kwargs):
        return _Raising(super().locator(selector, **kwargs))


class _Raising:
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def locator(self, selector, **kwargs):
        return _Raising(self._wrapped.locator(selector, **kwargs))

    def nth(self, index):
        return _Raising(self._wrapped.nth(index))

    async def count(self):
        return await self._wrapped.count()

    async def get_attribute(self, name, **kwargs):
        return await self._wrapped.get_attribute(name, **kwargs)

    async def inner_text(self, **kwargs):
        raise RuntimeError("element <p>" + MARKER + "</p> detached")


def test_a_read_that_raises_quoting_the_page_is_counted_and_dropped(caplog):
    caplog.set_level(logging.DEBUG)
    result, _page = read(page_class=_RaisingTextPage)
    assert result["cards"] == [] and result["reads_failed"] > 0
    assert not any(MARKER in text for _p, text in strings_in(result))
    assert MARKER not in caplog.text


def test_count_of_never_raises_and_never_quotes():
    for text in (MARKER, "", None, 12, "1,23", "1,234,567,890", " 1,234 ", "0012"):
        shape, value = cpi.count_of(text)
        assert shape in cpi.COUNT_SHAPES
        assert value is None or isinstance(value, int)
    assert cpi.count_of(" 1,234 ") == ("grouped_digits", 1234)
    assert cpi.count_of("1,23") == ("not_a_count", None)


# ---------------------------------------------------------------------------
# 4. The tool: one load, a landing veto, and a refusal before any load
# ---------------------------------------------------------------------------


def _drive_tool(organisation_id: str, *, landed: str = "", markup: str = "") -> tuple[dict, list]:
    from linkedin_server import browser as browser_module
    from linkedin_server import server

    gotos: list[str] = []
    page = SkeletonPage(PlantedPage(), parse(_markup(markup)), url=URL)

    @asynccontextmanager
    async def fake_session(*args, **kwargs):
        yield page

    async def fake_goto(target, url, **kwargs):
        gotos.append(url)
        return landed or url

    original = browser_module.BROWSER.session, browser_module.BROWSER.goto
    browser_module.BROWSER.session = fake_session
    browser_module.BROWSER.goto = fake_goto
    try:
        result = asyncio.run(server.linkedin_company_people_insights(organisation_id))
    finally:
        browser_module.BROWSER.session, browser_module.BROWSER.goto = original
    return result, gotos


def test_the_tool_loads_one_composed_page_and_returns_the_cards():
    result, gotos = _drive_tool("5417062")
    assert gotos == ["https://www.linkedin.com/company/5417062/people/"]
    assert result["ok"] is True and result["pages_loaded"] == 1
    assert [card["facet"] for card in result["cards"]] == ORDER


def test_the_tool_reports_a_redirect_to_the_slug_form_as_a_boolean_only():
    landed = "https://www.linkedin.com/company/example-org/people/"
    result, _gotos = _drive_tool("5417062", landed=landed)
    assert result["ok"] is True and result["redirected"] is True
    assert not any("example-org" in text for _p, text in strings_in(result))


@pytest.mark.parametrize("landed", [
    "https://www.linkedin.com/company/5417062/",
    "https://www.linkedin.com/company/unavailable/",
    "https://www.linkedin.com/feed/",
])
def test_a_landing_off_a_people_tab_is_vetoed_before_any_read(landed):
    result, gotos = _drive_tool("5417062", landed=landed)
    assert len(gotos) == 1
    assert result["ok"] is False and result["refused"] == "landed_off_the_people_tab"
    assert "cards" not in result
    assert not any(landed in text for _p, text in strings_in(result))


@pytest.mark.parametrize("organisation_id", ["example-org", "5417062/people/?x=1", "", "1" * 25])
def test_a_non_numeric_id_is_refused_before_any_load(organisation_id):
    result, gotos = _drive_tool(organisation_id)
    assert gotos == []
    assert result["ok"] is False and result["built"] is False
    if organisation_id:
        assert not any(organisation_id in text for _p, text in strings_in(result))
