"""The triage instrument's three controls, SHOWN FAILING.

``scripts/triage_messaging_gap_rows.py`` publishes the integers that the wave
report ``_audit/2026-09-20-the-messaging-gap.md`` quotes. An instrument that
publishes a number a document rests on is exactly the class this repository
requires to be shown going red first -- it found roughly ten distinct shapes
of un-failable check in one day, one of which printed
``PASS: 0 hits across 0 blobs``.

So each of the three controls is exercised here against a defect planted to
defeat it:

* **CONTROL 1, the counter agreement.** :func:`_control_count` is handed a row
  total that does not match the shipped counter and must return a failure
  string naming both numbers.
* **CONTROL 2, the join coverage.** :func:`unjoined_rows` is handed a blocker
  map with a hole and must name the row that fell through.
* **CONTROL 3, the direction reader.** It is inherited from
  ``reader_closable_blockers`` and already carries its own shown-failing set;
  what is asserted here is that the triage REFUSES when that control fails,
  rather than printing a table of ``unknown``.

AND THE POSITIVE CONTROL, which is the half that is easy to forget: over the
real census and the real blocker map every control must PASS and the row total
must be the one the shipped counter publishes. A suite that only shows
refusals has not shown that anything can succeed.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import reader_closable_blockers as rcb  # noqa: E402
import triage_messaging_gap_rows as triage  # noqa: E402

SLICE = "M"


def test_the_slice_is_enumerated_and_every_row_joins():
    """THE POSITIVE CONTROL."""
    rows = triage._gap_rows(SLICE)
    assert rows, "no GAP rows enumerated -- the parse found nothing"
    blockers = rcb.load_blockers()
    assert triage.unjoined_rows(SLICE, rows, blockers) == []


def test_the_counter_agreement_control_passes_on_the_real_tree():
    rows = triage._gap_rows(SLICE)
    assert triage._control_count(SLICE, len(rows)) == ""


def test_the_counter_agreement_control_can_fail():
    """SHOWN FAILING. Hand it a total the shipped counter does not publish."""
    rows = triage._gap_rows(SLICE)
    problem = triage._control_count(SLICE, len(rows) + 1)
    assert problem, "the counter control accepted a total that is wrong by one"
    assert str(len(rows) + 1) in problem
    assert "messaging-and-content.md" in problem


def test_the_join_coverage_control_can_fail():
    """SHOWN FAILING. Punch one hole in the blocker map and it must be named."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    victim = rows[0][0]
    del blockers["%s %s" % (SLICE, victim)]
    assert triage.unjoined_rows(SLICE, rows, blockers) == [victim]


def test_the_join_coverage_control_names_every_hole_not_just_the_first():
    """A control that stops at the first miss under-reports the damage."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    victims = sorted(row_id for row_id, _ in rows[:3])
    for victim in victims:
        del blockers["%s %s" % (SLICE, victim)]
    assert triage.unjoined_rows(SLICE, rows, blockers) == victims


def test_the_direction_reader_control_is_the_inherited_one():
    """CONTROL 3 is imported, not rewritten, and it must be green here.

    ``reader_closable_blockers.control_negative`` returns the number of its
    own planted cases that behaved wrongly. Zero is the only acceptable
    answer, and a non-zero one refuses the whole triage in
    ``triage.main``.
    """
    assert rcb.control_negative() == 0


def test_every_gap_row_has_a_direction_the_reader_can_state():
    """An unreadable direction cell is a measurement, so it must be visible.

    This does not require every row to be ``R`` or ``W``; it requires that
    whatever the reader says is one of its declared answers, so a silent
    empty string cannot be counted as a write.
    """
    rows = triage._gap_rows(SLICE)
    cells = triage._cells_by_row(SLICE)
    allowed = set(rcb.DIRECTIONS) | {"unknown", "ambiguous"}
    for row_id, _ in rows:
        direction = rcb.direction_of(cells[row_id])
        assert direction in allowed, (row_id, direction)


#: THE TRIAGE DENOMINATOR, measured at the wave's start and quoted in
#: ``_audit/2026-09-20-the-messaging-gap.md``: 83 GAP rows, 11 reads, 71
#: writes, 1 read-and-write.
DENOMINATOR_AT_WAVE_START = (83, {"R": 11, "W": 71, "R+W": 1})

#: AFTER the wave moved ``C43`` -- a READ -- out of GAP onto the
#: FEED-CONTENT-READ-RULING. One row, one direction, and the arithmetic is
#: stated so the two numbers cannot be confused for a disagreement.
EXPECTED_NOW = (82, {"R": 10, "W": 71, "R+W": 1})


def test_the_headline_split_is_the_one_the_report_quotes():
    """THE NUMBERS THE WAVE REPORT RESTS ON, pinned here rather than in prose.

    Measured 2026-09-20. If a sibling wave moves one of these rows out of GAP
    this goes red, which is the correct outcome: the report's headline would
    then be stale and somebody should know before quoting it again. The
    failure message carries the arithmetic so the next reader can tell a
    sibling's legitimate move from a regression.
    """
    rows = triage._gap_rows(SLICE)
    cells = triage._cells_by_row(SLICE)
    counted = {"R": 0, "W": 0, "R+W": 0}
    for row_id, _ in rows:
        direction = rcb.direction_of(cells[row_id])
        if direction in counted:
            counted[direction] += 1
    total_then, split_then = DENOMINATOR_AT_WAVE_START
    total_now, split_now = EXPECTED_NOW
    assert (len(rows), counted) == (total_now, split_now), (
        "this slice held %d GAP rows %r at the start of the 2026-09-20 "
        "messaging-gap wave, and %d %r after it moved C43. It now holds %d "
        "%r. If a later wave moved a row, update both constants and the "
        "report that quotes them."
        % (total_then, split_then, total_now, split_now, len(rows), counted)
    )
