"""The Premium Insights tab's two function tables, each read under its OWN SUMMARY (lane jobs7, 2026-11-27).

Census rows ``J 114`` (distribution and headcount growth by function) and
``J 174`` (job openings by function), on the orchestrator's
J114-READS-ITS-OWN-TABLE (14:30 IST). Record: ``_audit/2026-11-27-jobs7.md``
sections 11.5 and 11.6.

THE DEFECT, VERIFIED BY KEYED SHAPE. LinkedIn heads BOTH screen-reader
function tables with the same words -- ``Function``, ``Number of employees``,
``Percentage of total headcount`` -- and only the table's ``summary`` says
what it counts: ``Headcount growth by function`` or ``Total job openings``.
The shipped reader chose a table by its header words, so:

* on session 11's capture (``tests/fixtures/live11/company_insights_headcount.html``,
  load 19), which draws ONLY the openings table, it returned job openings as
  ``employees`` and ``share_of_headcount_percent``;
* on session 12's load 20 (``tests/fixtures/live12/c_rj26_1_functions-open.html``),
  which draws BOTH, it found two tables and read no row at all.

RED FIRST: every test below but the composition control failed on the shipped
reader (the record gives the counts). The fixtures are the words skeletons --
LinkedIn's words written where their keyed shapes matched; every figure is
``x`` there, as in the tracked copies, and each test PLANTS synthetic figures
at the cells the capture drew.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from linkedin_server import company_tabs as ct
from linkedin_server.errors import ExtractionFailedError
from tests.live11_words import words
from tests.plantedpage import PlantedPage
from tests.skeleton_page import SkeletonPage, parse

ROOT = Path(__file__).resolve().parent.parent
LOAD_20 = ROOT / "tests" / "fixtures" / "live12" / "c_rj26_1_functions-open_words.html"
URL = "https://www.linkedin.com/company/example-org/insights/?insightType=HEADCOUNT"

HEADCOUNT = "Headcount growth by function"
OPENINGS = "Total job openings"

#: The functions each table drew on load 20, in its order (LinkedIn's own
#: list; MEASURED by keyed shape, the headcount table's "Education" kept as a
#: plain word by the capture itself).
HEADCOUNT_FUNCTIONS_20 = [
    "Engineering", "Information Technology", "Sales", "Program and Project Management",
    "Business Development", "Operations", "Product Management", "Support", "Research",
    "Education", "Arts and Design", "Administrative", "Marketing", "Human Resources",
]
OPENINGS_FUNCTIONS = [
    "Engineering", "Information Technology", "Sales", "Program and Project Management",
    "Operations", "Product Management", "Business Development", "Arts and Design",
    "Marketing", "Finance", "Support",
]


def _growth_texts(value: str) -> tuple[str, str]:
    word = "decrease" if value.startswith("-") else "increase"
    return value + "%", value + "% " + word


def plant(markup: str, summary: str, figures) -> str:
    """Plant synthetic figures into the table carrying ``summary``, row by row:
    a count, a share, then each growth cell's two spans."""
    start = markup.index(f'<table summary="{summary}"')
    end = markup.index("</table>", start)
    rows = markup[start:end].split("<tr>")
    out = [rows[0], rows[1]]
    for index, row in enumerate(rows[2:]):
        count, share, first, second = figures(index)
        for value in (count, share, *_growth_texts(first), *_growth_texts(second)):
            assert "\nx\n" in row, (summary, index)
            row = row.replace("\nx\n", "\n" + value + "\n", 1)
        out.append(row)
    return markup[:start] + "<tr>".join(out) + markup[end:]


def headcount_figures(index: int):
    return str(20000 - 1000 * index), str(30 - index), "4", "-2"


def openings_figures(index: int):
    return str(500 - 40 * index), str(25 - 2 * index), "12", "-8"


def run(markup: str) -> dict[str, Any]:
    page = SkeletonPage(PlantedPage(), parse(markup), url=URL)
    result = asyncio.run(ct.read_insights_tab(page))
    assert page.unmodelled == [] and page.planted_answers == []
    return result


def load_20() -> str:
    markup = LOAD_20.read_text(encoding="utf-8")
    markup = plant(markup, HEADCOUNT, headcount_figures)
    return plant(markup, OPENINGS, openings_figures)


def session_11() -> str:
    return plant(words("company_insights_headcount"), OPENINGS, openings_figures)


# ---------------------------------------------------------------------------
# Load 20: both tables drawn
# ---------------------------------------------------------------------------

def test_on_load_20_the_headcount_rows_are_j_114s_functions():
    result = run(load_20())
    assert [row["function"] for row in result["functions"]] == HEADCOUNT_FUNCTIONS_20
    assert result["functions"][0] == {
        "function": "Engineering", "employees": 20000, "share_of_headcount_percent": 30,
        "growth_6_months_percent": 4, "growth_1_year_percent": -2,
    }
    assert result["functions_unread"] is None


def test_on_load_20_the_openings_rows_are_j_174s_openings_by_function():
    result = run(load_20())
    assert [row["function"] for row in result["openings_by_function"]] == OPENINGS_FUNCTIONS
    assert result["openings_by_function"][0] == {
        "function": "Engineering", "openings": 500, "share_of_openings_percent": 25,
        "growth_3_months_percent": 12, "growth_6_months_percent": -8,
    }
    assert result["openings_by_function_unread"] is None
    assert result["rows_withheld"] == 0 and result["headers_unread"] == 0


def test_no_openings_figure_is_returned_as_a_headcount_figure():
    """The two tables' figures were planted apart: no headcount row carries an
    openings count, and no openings row carries an employee count."""
    result = run(load_20())
    employees = {row["employees"] for row in result["functions"]}
    openings = {row["openings"] for row in result["openings_by_function"]}
    assert employees.isdisjoint(openings)
    assert all("openings" not in row for row in result["functions"])
    assert all("employees" not in row for row in result["openings_by_function"])


# ---------------------------------------------------------------------------
# Session 11: the openings table only
# ---------------------------------------------------------------------------

def test_on_session_11_the_headcount_field_is_empty_and_says_why():
    result = run(session_11())
    assert result["functions"] == []
    assert result["functions_unread"] == "no_table_with_this_summary"


def test_on_session_11_the_openings_are_j_174s_and_never_employee_counts():
    result = run(session_11())
    assert [row["function"] for row in result["openings_by_function"]] == OPENINGS_FUNCTIONS
    assert result["openings_by_function"][0]["openings"] == 500
    assert result["openings_by_function_unread"] is None


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

def test_a_page_with_neither_summary_returns_both_empty_with_their_reasons():
    """THE CONTROL: the header words alone choose no table."""
    markup = session_11().replace(f'<table summary="{OPENINGS}"', '<table summary="x"', 1)
    assert 'summary="Total job openings"' not in markup
    assert 'summary="Headcount growth by function"' not in markup
    result = run(markup)
    assert result["functions"] == [] and result["openings_by_function"] == []
    assert result["functions_unread"] == "no_table_with_this_summary"
    assert result["openings_by_function_unread"] == "no_table_with_this_summary"
    # The modules are still read, so the answer is a reading, not a failure.
    assert result["modules"] == ["hiring_trends", "total_job_openings"]


def test_a_summary_drawn_twice_is_read_from_neither_copy():
    markup = session_11()
    start = markup.index(f'<table summary="{OPENINGS}"')
    end = markup.index("</table>", start) + len("</table>")
    doubled = markup[:end] + markup[start:end] + markup[end:]
    result = run(doubled)
    assert result["openings_by_function"] == []
    assert result["openings_by_function_unread"] == "more_than_one_table_with_this_summary"


def test_a_page_with_no_module_and_no_row_is_a_failed_read():
    markup = session_11().replace(f'<table summary="{OPENINGS}"', '<table summary="x"', 1)
    for heading in ("Hiring trends", "Total job openings"):
        markup = markup.replace("\n" + heading + "\n", "\nx\n")
    with pytest.raises(ExtractionFailedError):
        run(markup)


def test_each_summary_names_its_own_field_and_header_map():
    assert set(ct.FUNCTION_TABLES) == {HEADCOUNT, OPENINGS}
    assert ct.FUNCTION_TABLES[HEADCOUNT][0] == "functions"
    assert ct.FUNCTION_TABLES[OPENINGS][0] == "openings_by_function"
    for _summary, (_field, headers) in ct.FUNCTION_TABLES.items():
        assert all(word in headers for word in ct._REQUIRED_HEADERS)
