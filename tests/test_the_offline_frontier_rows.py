"""The offline frontier, 2026-09-28: each of the five rows says what it rests on.

THE ORDER (the orchestrator's, 2026-09-28 01:30): census_completion's bucket 3
named five still-GAP rows as BLOCKED ON NOTHING -- ``M M53``, ``N 195``,
``P K1``, ``P S5`` (read direction) and ``J 107`` (jobs). Each was built where
a capture on disk shows the field the row wants, and moved to COVERED-UNFIRED
in the same commit; where no capture shows it, nothing was built and the
capture spec went into the record (``_audit/2026-09-24-lane-s-people-search.md``,
"The offline frontier").

THIS FILE HOLDS THE CENSUS TO THAT: a moved row names the tool, the reader
and the test file it rests on, and has left its address table; the one row
not built names the missing capture, is re-gated MEASURE, and its spec is in
the record. When a row moves again -- a live fire, or a capture for P K1 --
this table moves with it in the same commit.
"""
from __future__ import annotations

import asyncio
import csv
import io
import re
from pathlib import Path

import pytest

from linkedin_server import dom, people_data, presence, recruiter_views
from linkedin_server import server as server_module

REPO = Path(__file__).resolve().parent.parent
CENSUS = REPO / "_audit" / "_census"
RECORD = REPO / "_audit" / "2026-09-24-lane-s-people-search.md"

OPENED = "**COVERED-UNFIRED 2026-09-28 (lane S, the offline frontier):"

#: (slice file, row) -> what the moved row's cell must name.
MOVED: dict[tuple[str, str], tuple[str, ...]] = {
    ("messaging-and-content.md", "M53"): (
        "`linkedin_messaging_presence`", "`presence.read_suggested_presence`",
        "`tests/test_messaging_presence.py`", "`PEOPLE-DATA-MITIGATIONS`"),
    ("network.md", "195"): (
        "`linkedin_recruiter_insights`", "`recruiter_views.read_recruiter_views`",
        "`tests/test_recruiter_insights.py`", "`PEOPLE-DATA-MITIGATIONS`"),
    ("profile.md", "S5"): (
        "`linkedin_search_appearances`", "`dom.read_search_appearances`",
        "`tests/test_profile_engagement_cards.py`", "`engagement`"),
    ("jobs.md", "107"): (
        "`linkedin_search_jobs`", "`tests/test_a_company_search_needs_no_keyword.py`"),
}

#: MOVED AGAIN, 2026-09-28: fired live and banked, each on its own cell's bar --
#: `N 195` and `P S5` in the live lane's session 2, `J 107` and `M M53` in its
#: session 3 (fired in session 2 too, without banking). The cell now OPENS on
#: the paragraph that banked it, and the move above follows it, kept as that
#: morning's record.
BANKED_AGAIN = {("network.md", "195"), ("profile.md", "S5"),
                ("jobs.md", "107"), ("messaging-and-content.md", "M53")}
BANKED_OPENING = ("**FIRED AND BANKED 2026-09-28 (the live lane's session 2).**",
                  "**FIRED AND BANKED 2026-09-28 (the live lane's session 3).**")

#: MOVED AGAIN, 2026-11-26: `J 107` returned to GAP at integration 6 by RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE
#: -- live session 12's load 3 showed the classic search no longer serves. Its
#: cell still opens on the banking paragraph and keeps the frontier's move; the
#: state is GAP, and its directions line is back, on the AI route.
RETURNED_TO_GAP = {("jobs.md", "107")}

#: The row not built, and why.
NOT_BUILT = ("profile.md", "K1")
NOT_BUILT_OPENED = "**NOT BLOCKED ON NOTHING, 2026-09-28 (lane S, the offline frontier):"

#: The address-table key each read row had.
ADDRESS_KEYS = {("messaging-and-content.md", "M53"): ("M", "M53"),
                ("network.md", "195"): ("N", "195"),
                ("profile.md", "S5"): ("P", "S5")}


def _row(slice_file: str, row: str) -> tuple[str, str]:
    """(state, notes) of one census row: the fourth cell and the last."""
    pattern = re.compile(r"^\| %s \|" % re.escape(row))
    hits = [line for line in (CENSUS / slice_file).read_text(encoding="utf-8").splitlines()
            if pattern.match(line)]
    assert len(hits) == 1, (slice_file, row, len(hits))
    cells = hits[0].split("|")
    return cells[4].strip().strip("*"), cells[-2].strip()


def _table(name: str) -> list[dict[str, str]]:
    text = (CENSUS / name).read_text(encoding="utf-8")
    body = "\n".join(line for line in text.splitlines() if line and not line.startswith("#"))
    return list(csv.DictReader(io.StringIO(body), delimiter="\t"))


@pytest.mark.parametrize("key", sorted(MOVED))
def test_a_moved_row_opens_on_its_move_and_names_what_it_rests_on(key):
    state, notes = _row(*key)
    if key in BANKED_AGAIN:
        assert state == ("GAP" if key in RETURNED_TO_GAP else "COVERED-PROVEN"), (key, state)
        assert notes.startswith(BANKED_OPENING), key
        assert notes.find(OPENED) > 0, (key, "the frontier's move no longer follows the banking")
    else:
        assert state == "COVERED-UNFIRED", (key, state)
        assert notes.startswith(OPENED), key
    for name in MOVED[key]:
        assert name in notes, (key, name)
    assert "Not PROVEN" in notes, key


@pytest.mark.parametrize("key", sorted(ADDRESS_KEYS))
def test_a_moved_read_row_has_left_the_address_table(key):
    keys = {(r["slice"], r["row"]) for r in _table("read-addresses.tsv")}
    assert ADDRESS_KEYS[key] not in keys, key


def test_the_jobs_row_is_back_in_the_directions_table_on_the_ai_route():
    """It left on 2026-09-28 and came back on 2026-11-26 (RETURNED_TO_GAP).

    Renamed from ``..._has_left_the_directions_table`` at integration 6: the row
    is GAP again, so the table must hold it, its read half on the AI route.
    """
    lines = [r for r in _table("jobs-directions.tsv") if (r["slice"], r["row"]) == ("J", "107")]
    assert len(lines) == 1, lines
    assert lines[0]["address"].startswith("https://www.linkedin.com/jobs/search-results/"), lines[0]["address"]


def test_THIS_CONTROL_CAN_FAIL_the_table_reader_finds_a_row_that_is_there():
    keys = {(r["slice"], r["row"]) for r in _table("read-addresses.tsv")}
    assert ("P", "K1") in keys


def test_the_row_not_built_says_why_and_is_gated_on_a_capture():
    state, notes = _row(*NOT_BUILT)
    assert state == "GAP"
    assert notes.startswith(NOT_BUILT_OPENED)
    assert "The offline frontier" in notes
    line = next(r for r in _table("read-addresses.tsv") if (r["slice"], r["row"]) == ("P", "K1"))
    assert line["gate"] == "MEASURE", line["gate"]
    assert line["note"].startswith("RE-GATED READER -> MEASURE 2026-09-28")


def test_the_record_carries_the_capture_spec_the_row_points_at():
    text = RECORD.read_text(encoding="utf-8")
    assert "\n## The offline frontier 2026-09-28\n" in text
    section = text[text.index("\n## The offline frontier 2026-09-28\n"):]
    assert "CAPTURE SPEC, `P K1`" in section


def test_every_artifact_a_moved_row_names_exists():
    tools = {tool.name for tool in asyncio.run(server_module.mcp.list_tools())}
    assert {"linkedin_messaging_presence", "linkedin_recruiter_insights",
            "linkedin_search_appearances", "linkedin_search_jobs"} <= tools
    assert callable(presence.read_suggested_presence)
    assert callable(recruiter_views.read_recruiter_views)
    assert callable(dom.read_search_appearances)
    for name in ("test_messaging_presence.py", "test_recruiter_insights.py",
                 "test_profile_engagement_cards.py",
                 "test_a_company_search_needs_no_keyword.py"):
        assert (REPO / "tests" / name).is_file(), name
    assert {"linkedin_messaging_presence", "linkedin_recruiter_insights"} <= people_data.PEOPLE_TOOLS
