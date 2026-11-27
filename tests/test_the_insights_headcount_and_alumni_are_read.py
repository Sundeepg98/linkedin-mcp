"""The Premium Insights tab's headcount over time and notable alumni (census row J 169; lane jobs7, 2026-11-27).

On the orchestrator's J169-BY-ITS-OWN-WORDS (14:05 IST): session 12's load 20
(``tests/fixtures/live12/c_rj26_1_functions-open.html``) draws both of the
row's facets, by keyed shape:

* HEADCOUNT OVER TIME -- the table LinkedIn summarises ``Total employee
  count``: one data row of four cells under the headers ``total employees``
  (LinkedIn's own lower case), ``6m growth``, ``1y growth`` and ``2y
  growth``, the data row drawn above the header row and outside any
  ``tbody``;
* NOTABLE ALUMNI -- the module headed ``Notable company alumni``: a carousel
  of member cards, four drawn, three with a name link, a degree line and a
  current-role line.

Every figure and every member's words are ``x`` in the words fixture, as in
the capture's tracked copy; each test PLANTS synthetic values at the places
the capture drew the real ones. Every name-shaped string here is synthetic.

RED FIRST: on the reader before this commit, ``headcount`` and
``notable_alumni`` did not exist.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import company_tabs as ct
from linkedin_server import people_data
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

ROOT = Path(__file__).resolve().parent.parent
LOAD_20 = ROOT / "tests" / "fixtures" / "live12" / "c_rj26_1_functions-open_words.html"
URL = "https://www.linkedin.com/company/example-org/insights/?insightType=HEADCOUNT"

SYNTHETIC = [
    ("Exampleperson Alphaone", "Synthetic Role at Example Org One", "2nd"),
    ("Exampleperson Betatwo", "Synthetic Role at Example Org Two", "3rd+"),
    ("Exampleperson Gammathree", "Synthetic Role at Example Org Three", "2nd"),
]


def plant_headcount(markup: str, total: str = "123,456", growth=("-3", "-5", "4")) -> str:
    start = markup.index('<table class="org-insights-module__summary-table" summary="Total employee count"')
    end = markup.index("</table>", start)
    table = markup[start:end]
    values = [total]
    for value in growth:
        word = "decrease" if value.startswith("-") else "increase"
        values += [value + "%", value + "% " + word]
    for value in values:
        assert "\nx\n" in table
        table = table.replace("\nx\n", "\n" + value + "\n", 1)
    return markup[:start] + table + markup[end:]


def run(markup: str) -> tuple[dict[str, Any], SkeletonPage]:
    page = SkeletonPage(PlantedPage(), parse(markup), url=URL)
    return asyncio.run(ct.read_insights_tab(page)), page


def plant_alumni(markup: str, people=SYNTHETIC) -> str:
    """Plant synthetic members into the alumni cards that draw a name link, in
    order: the name (both spans), the degree, the current role and its
    organisation; the link's slug made a synthetic one."""
    out = markup
    marker = '<div class="org-notable-alumni-card">'
    starts = [i for i in range(len(out)) if out.startswith(marker, i)]
    assert len(starts) == 4, len(starts)
    planted = 0
    pieces = []
    last = 0
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else out.index("</ul>", start)
        card = out[start:end]
        if "org-notable-alumni-card__alumni-name" in card and planted < len(people):
            name, role, degree = people[planted]
            slug = name.lower().replace(" ", "-")
            card = card.replace('href="https://www.linkedin.com/in/x"',
                                f'href="https://www.linkedin.com/in/{slug}/"')
            role_words, org = role.rsplit(" at ", 1)
            for value in (name, name, "· " + degree, role_words + " at", org):
                assert "\nx\n" in card, (index, value)
                card = card.replace("\nx\n", "\n" + value + "\n", 1)
            planted += 1
        pieces.append(out[last:start])
        pieces.append(card)
        last = end
    pieces.append(out[last:])
    return "".join(pieces)


def load_20() -> str:
    return plant_alumni(plant_headcount(LOAD_20.read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Headcount over time
# ---------------------------------------------------------------------------

def test_load_20_draws_the_three_modules_this_row_and_its_neighbours_read():
    result, page = run(load_20())
    assert page.unmodelled == [] and page.planted_answers == []
    assert result["modules"] == [
        "hiring_trends", "total_job_openings", "total_employee_count",
        "headcount_growth_by_function", "notable_company_alumni",
    ]


def test_the_headcount_summary_is_the_total_and_its_growth_over_three_spans():
    result, _ = run(load_20())
    assert result["headcount"] == {
        "employees": 123456, "growth_6_months_percent": -3,
        "growth_1_year_percent": -5, "growth_2_years_percent": 4,
    }
    assert result["headcount_unread"] is None


def test_a_growth_whose_sign_disagrees_with_its_word_is_withheld_not_flipped():
    markup = plant_alumni(plant_headcount(LOAD_20.read_text(encoding="utf-8"),
                                          growth=("-3", "-5", "4")))
    markup = markup.replace("\n4% increase\n", "\n-4% increase\n", 1)
    result, _ = run(markup)
    assert result["headcount"]["growth_2_years_percent"] is None
    assert result["headcount"]["employees"] == 123456


def test_session_11_draws_no_headcount_summary_and_says_why():
    from tests.live11_words import words
    result, _ = run(words("company_insights_headcount"))
    assert result["headcount"] is None
    assert result["headcount_unread"] == "no_table_with_this_summary"
    assert result["notable_alumni"] == []
    assert result["notable_alumni_unread"] == "module_heading_not_drawn"


# ---------------------------------------------------------------------------
# Notable alumni
# ---------------------------------------------------------------------------

def test_each_drawn_alumni_card_with_a_name_is_a_person_record():
    result, _ = run(load_20())
    names = [record["name"] for record in result["notable_alumni"]]
    assert names == [name for name, _role, _degree in SYNTHETIC]
    first = result["notable_alumni"][0]
    assert people_data.as_record(first) is not None
    assert first["link"] == "https://www.linkedin.com/in/exampleperson-alphaone/"
    assert first["degree"] == "2nd"
    assert first["headline"] == "Synthetic Role at Example Org One"
    assert result["alumni_withheld"] == 1          # the fourth card draws no name link
    assert result["notable_alumni_unread"] is None


def test_alumni_are_read_only_under_their_own_heading():
    markup = load_20().replace("\nNotable company alumni\n", "\nx\n")
    result, _ = run(markup)
    assert result["notable_alumni"] == []
    assert result["notable_alumni_unread"] == "module_heading_not_drawn"


def test_no_alumni_string_leaves_outside_a_person_record():
    result, _ = run(load_20())
    for record in result["notable_alumni"]:
        assert people_data.as_record(record) is not None
    outside = {k: v for k, v in result.items() if k != "notable_alumni"}
    flat = repr(outside)
    for name, role, _degree in SYNTHETIC:
        assert name not in flat and role not in flat
        assert "Example Org" not in flat
