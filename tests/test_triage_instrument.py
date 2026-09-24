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


def _returned(rows, blockers):
    return triage.returned_outside_ledger(SLICE, rows, blockers,
                                          triage._cells_by_row(SLICE))


def _joined_unmarked(rows, blockers):
    """Rows the map holds and whose cell carries no returned-row marker -- the
    only rows a planted hole can leave unjoined, since a marked row would be
    classed instead. Chosen from the tree, so the plant cannot miss."""
    cells = triage._cells_by_row(SLICE)
    return [row_id for row_id, _ in rows
            if "%s %s" % (SLICE, row_id) in blockers
            and not triage.RETURNED_MARKER.search(" | ".join(cells[row_id]))]


def _accounted(rows, blockers):
    """What ``main`` exempts from the join: the returned class together with the
    rows that entered GAP after the map's freeze (lane Y2's integration)."""
    return _returned(rows, blockers) | set(triage.entered_since_freeze(SLICE, rows))


def test_the_slice_is_enumerated_and_every_row_joins():
    """THE POSITIVE CONTROL: every GAP row joins the map, or is a returned row
    that names its blocker in its own cell (lane R, 2026-09-23), or entered GAP
    after the map's freeze (lane Y2, 2026-09-24)."""
    rows = triage._gap_rows(SLICE)
    assert rows, "no GAP rows enumerated -- the parse found nothing"
    blockers = rcb.load_blockers()
    assert triage.unjoined_rows(SLICE, rows, blockers, _accounted(rows, blockers)) == []
    entered = triage.entered_since_freeze(SLICE, rows)
    assert triage.misfiled_returns(_returned(rows, blockers), entered) == []


def test_every_returned_row_entered_gap_after_the_freeze():
    """The two rules agree on this tree: each returned row is off the map
    because it was not GAP at the freeze, never because the map lost it."""
    rows = triage._gap_rows(SLICE)
    blockers = rcb.load_blockers()
    returned = _returned(rows, blockers)
    assert returned, "no returned row found -- the marker reader reads nothing"
    assert returned <= set(triage.entered_since_freeze(SLICE, rows))


def test_a_marked_row_missing_from_the_map_is_refused_not_classed(monkeypatch, capsys):
    """SHOWN FAILING, CONTROL 2b. A row that WAS GAP at the freeze, lost from
    the map, whose cell carries the returned-row marker: the returned class
    alone would absorb it. The fixture is BUILT -- a joined, unmarked row given
    the marker and removed from the map -- so the control cannot pass because
    the tree happens to hold no such row."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    cells = dict(triage._cells_by_row(SLICE))
    victim = _joined_unmarked(rows, blockers)[0]
    del blockers["%s %s" % (SLICE, victim)]
    cells[victim] = list(cells[victim]) + [
        "**RETURNED TO GAP 2026-09-23 BY LANE R (planted).** BLOCKER, NAMED: planted"]
    returned = triage.returned_outside_ledger(SLICE, rows, blockers, cells)
    assert victim in returned, "the planted marker was not read"
    entered = triage.entered_since_freeze(SLICE, rows)
    assert triage.misfiled_returns(returned, entered) == [victim]

    monkeypatch.setattr(triage.rcb, "load_blockers", lambda: blockers)
    monkeypatch.setattr(triage, "_cells_by_row", lambda letter: cells)
    assert triage.main([]) == 1
    out = capsys.readouterr().out
    assert "were GAP at the map's freeze" in out and victim in out, out


def test_every_entered_row_names_its_blocker_in_its_own_cell():
    """CONTROL 2c on the real tree: no row off the map is exempted in silence."""
    rows = triage._gap_rows(SLICE)
    blockers = rcb.load_blockers()
    entered = triage.entered_since_freeze(SLICE, rows)
    others = set(entered) - _returned(rows, blockers)
    assert others, "no entered row outside the returned class -- nothing to read"
    assert triage.unnamed_entered(entered, _returned(rows, blockers),
                                  triage._cells_by_row(SLICE)) == []


def test_an_entered_row_that_names_no_blocker_is_refused(monkeypatch, capsys):
    """SHOWN FAILING, CONTROL 2c. The fixture is BUILT: an entered row outside
    the returned class has its cell replaced by one that names nothing, and
    the refusal must name that row, through ``main`` as well."""
    rows = triage._gap_rows(SLICE)
    blockers = rcb.load_blockers()
    cells = dict(triage._cells_by_row(SLICE))
    entered = triage.entered_since_freeze(SLICE, rows)
    returned = _returned(rows, blockers)
    victim = sorted(set(entered) - returned)[0]
    cells[victim] = [victim, "planted: a capability", "GAP", "R",
                     "planted: this cell says nothing about what holds it"]
    assert triage.unnamed_entered(entered, returned, cells) == [victim]

    monkeypatch.setattr(triage, "_cells_by_row", lambda letter: cells)
    assert triage.main([]) == 1
    out = capsys.readouterr().out
    assert "name no blocker in their own cell" in out and victim in out, out


def test_the_exemption_is_exactly_the_rows_the_map_cannot_hold():
    """Rows that entered GAP after the map's freeze, and nothing else.

    Without the exemption the join names EXACTLY the entered rows -- so the
    exemption hides no other hole -- and no entered row has a map line, which
    is what makes it an exemption rather than a skipped join. If the map ever
    starts holding post-freeze rows, the second assertion goes red and the
    exemption should go with it.
    """
    rows = triage._gap_rows(SLICE)
    blockers = rcb.load_blockers()
    entered = triage.entered_since_freeze(SLICE, rows)
    assert triage.unjoined_rows(SLICE, rows, blockers) == entered
    assert [r for r in entered if "%s %s" % (SLICE, r) in blockers] == []


def test_an_empty_frozen_census_refuses_rather_than_exempting_every_row(
        monkeypatch):
    """SHOWN FAILING. A freeze read that came back empty would exempt the slice."""
    rows = triage._gap_rows(SLICE)
    monkeypatch.setattr(triage.egr, "rows",
                        lambda ref=None, dialects=None: iter(()))
    with pytest.raises(SystemExit) as refused:
        triage.entered_since_freeze(SLICE, rows)
    assert triage.bbm.FROZEN_REF in str(refused.value)
    assert "could not fail" in str(refused.value)


def test_a_dialect_at_the_freeze_refuses_rather_than_exempting_its_row(
        monkeypatch):
    """SHOWN FAILING. The enumerator drops a row whose frozen state cell is a
    dialect, and a row that was GAP at the freeze would then read as entered."""
    rows = triage._gap_rows(SLICE)
    real = triage.egr.rows

    def planted(ref=None, dialects=None):
        yield from real(ref, dialects)
        if ref is not None and dialects is not None:
            dialects.append("M PLANTED spells its state in a planted dialect")

    monkeypatch.setattr(triage.egr, "rows", planted)
    with pytest.raises(SystemExit) as refused:
        triage.entered_since_freeze(SLICE, rows)
    assert "M PLANTED" in str(refused.value)
    assert triage.bbm.FROZEN_REF in str(refused.value)


def test_the_returned_class_holds_only_marked_rows_outside_the_map():
    """The own class is DERIVED from the cell, never typed: every member is off
    the map and carries the marker, and it is not empty on this tree."""
    rows = triage._gap_rows(SLICE)
    blockers = rcb.load_blockers()
    cells = triage._cells_by_row(SLICE)
    returned = _returned(rows, blockers)
    assert returned, "no returned row found -- the marker reader reads nothing"
    for row_id in returned:
        assert "%s %s" % (SLICE, row_id) not in blockers, row_id
        assert triage.RETURNED_MARKER.search(" | ".join(cells[row_id])), row_id


def test_an_unmarked_row_off_the_map_is_still_refused():
    """SHOWN FAILING: the class cannot absorb a genuinely missing row. A row
    removed from the map that carries no marker must come back unjoined -- and
    since it was GAP at the freeze, the entered exemption cannot absorb it
    either (what ``main`` passes is both)."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    victim = _joined_unmarked(rows, blockers)[0]
    del blockers["%s %s" % (SLICE, victim)]
    assert victim not in _returned(rows, blockers)
    assert triage.unjoined_rows(SLICE, rows, blockers, _accounted(rows, blockers)) == [victim]


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
    """SHOWN FAILING. Punch one hole in the blocker map and it must be named.

    The victim is a JOINED row (it was `rows[0]` until lane R's returns put
    rows off the map at the head of the slice, where a delete raises), so it
    WAS GAP at the freeze; both exemptions are passed in, as ``main`` passes
    them, and neither may swallow a real hole."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    joined = _joined_unmarked(rows, blockers)
    assert joined, "no row joins the map unmarked, so there is no hole to punch"
    victim = joined[0]
    del blockers["%s %s" % (SLICE, victim)]
    assert triage.unjoined_rows(SLICE, rows, blockers, _accounted(rows, blockers)) == [victim]


def test_the_join_coverage_control_names_every_hole_not_just_the_first():
    """A control that stops at the first miss under-reports the damage."""
    rows = triage._gap_rows(SLICE)
    blockers = dict(rcb.load_blockers())
    joined = _joined_unmarked(rows, blockers)
    assert len(joined) >= 3, (
        "fewer than three rows join the map unmarked -- punching holes in "
        "nothing would pass this control without testing it")
    victims = sorted(joined[:3])
    for victim in victims:
        del blockers["%s %s" % (SLICE, victim)]
    assert triage.unjoined_rows(SLICE, rows, blockers, _accounted(rows, blockers)) == victims


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
AFTER_THE_MESSAGING_GAP_WAVE = (82, {"R": 10, "W": 71, "R+W": 1})

#: AFTER ``_audit/2026-09-21-the-write-ceiling.md``, which adjudicated this
#: slice's 71 WRITE-direction GAP rows and moved FIVE of them --
#: ``M35``, ``M36``, ``C73``, ``C88``, ``C89`` -- to EXCLUDED-RULED under the
#: settings-family ruling (``_audit/2026-09-05-decide-retire-rulings.md``
#: section 3.10, which states that ruling is capability-level rather than
#: path-level). **THE ARITHMETIC IS STATED RATHER THAN THE NUMBER REPLACED:**
#: 82 - 5 = 77, and the writes 71 - 5 = 66. The read and read-and-write counts
#: are UNTOUCHED, which is the check that this wave stayed inside its scope --
#: it was a write-direction pass, so any movement in ``R`` would have been a
#: row it had no business moving.
AFTER_THE_WRITE_CEILING_WAVE = (77, {"R": 10, "W": 66, "R+W": 1})

#: AFTER ``_audit/2026-09-21-the-compound-rows.md``, which ruled
#: ``COMPOUND-ROW-SPLITS-ONLY-ON-STATE`` and corrected ONE direction cell:
#: ``C85`` ("Vote in a poll / view poll results") carried ``W`` for a pair
#: whose second half is a READ, and now carries ``R+W``.
#:
#: **THE TOTAL DOES NOT MOVE AND THAT IS THE WHOLE POINT OF THIS ENTRY.**
#: 77 before, 77 after: no row left GAP, no row was created, no denominator
#: moved. The arithmetic is entirely inside the split -- writes 66 - 1 = 65,
#: read-and-writes 1 + 1 = 2, reads UNTOUCHED at 10 because the read HALF of a
#: compound row is counted in ``R+W`` and never in ``R``.
#:
#: WHY A CELL EDIT RATHER THAN A SPLIT, since a split was the queued option:
#: the row's halves differ in DIRECTION and agree on STATE (both GAP), and the
#: direction vocabulary has a both-value that ``rcb.DIRECTIONS`` already
#: normalises from four spellings, while the STATE vocabulary has none --
#: ``classify`` answers a two-state cell by silently taking the first by
#: textual order, or by silently dropping the row out of the census. So a
#: direction divergence can be told the truth in the cell and a state
#: divergence cannot, which is the whole of the ruling. ``M28`` in the same
#: file is the identical shape and has carried ``R+W`` since it was written.
AFTER_THE_COMPOUND_ROWS_WAVE = (77, {"R": 10, "W": 65, "R+W": 2})

#: AFTER LANE R, 2026-09-23 (`_audit/2026-09-23-exclusion-returns.md`), which
#: returned 40 of this slice's exclusions to GAP with each blocker named in
#: its cell: 77 + 40 = 117. Reads 10 + 3 (`C14`, `C42`, `C43`), read-and-writes
#: 2 + 1 (`C47`), writes 65 + 36. Fourteen of the forty were not GAP at the
#: blocker map's freeze and are tallied RETURNED-OUTSIDE-LEDGER; the map is not
#: grown (the orchestrator's call, delegated, 2026-09-24).
AFTER_LANE_R = (117, {"R": 13, "W": 101, "R+W": 3})

#: AFTER THE LIVE LANE'S MERGE, 2026-09-24, re-derived on the tree merged over
#: lane R: ``C72`` ("Share a post off LinkedIn") -- a READ -- was proven live
#: on his own post and moved GAP -> COVERED-PROVEN
#: (``_audit/2026-09-23-live-lane-session-1.md`` Entries 10-12). 117 - 1 =
#: 116, reads 13 - 1 = 12; writes and read-and-writes UNTOUCHED, because the
#: lane moved no write. ``_audit/2026-09-20-the-messaging-gap.md`` quotes the
#: wave-start 83, which stays true of that moment and is not edited.
AFTER_THE_LIVE_LANE = (116, {"R": 12, "W": 101, "R+W": 3})

#: AFTER ``_audit/2026-09-24-lane-y2-admission.md``, which ADMITTED eleven rows
#: of this slice at GAP -- ``M52``, ``M53`` and ``C93``-``C101``, capabilities
#: LinkedIn draws that no row carried -- measured on the tree that merged it
#: with lane R and then the live lane. **THE ARITHMETIC:** 116 + 11 = 127;
#: reads 12 + 6 = 18 (``M53``, ``C93``, ``C95``, ``C96``, ``C98``, ``C101``),
#: writes 101 + 4 = 105 (``M52``, ``C94``, ``C97``, ``C100``), read-and-writes
#: 3 + 1 = 4 (``C99``). No row LEFT GAP. None of the eleven was GAP at the
#: blocker map's freeze and none carries lane R's marker, so they are the
#: entered-since-freeze bucket, beside lane R's fourteen RETURNED-OUTSIDE-LEDGER
#: rows.
AFTER_THE_LANE_Y2_ADMISSION = (127, {"R": 18, "W": 105, "R+W": 4})

#: AFTER LANE L5, 2026-09-24 (`_audit/2026-09-24-lane-l5-messaging.md`),
#: re-derived with `scripts/triage_messaging_gap_rows.py` on the tree merged
#: with master 9b9a4d0: three rows built out of GAP -- `M10` and `M17`
#: (writes, `linkedin_send_reply`) and `M49` (a read, the read indicator on
#: his own last message). 116 - 3 = 113: reads 12 - 1, writes 101 - 2,
#: read-and-writes untouched at 3. RETURNED-OUTSIDE-LEDGER stays 14: none of
#: the three was a lane-R return.
AFTER_LANE_L5 = (113, {"R": 11, "W": 99, "R+W": 3})

#: BOTH, AT LANE L5'S MERGE OF MASTER 530227e (lane Y2's), 2026-09-24,
#: re-derived with the merged tree's `scripts/triage_messaging_gap_rows.py`
#: -- not summed: lane Y2's eleven admitted rows are GAP and this lane's
#: three built rows are not. 127 - 3 = 124: reads 18 - 1, writes 105 - 2,
#: read-and-writes 4, untouched. RETURNED-OUTSIDE-LEDGER stays 14, and the
#: eleven admitted rows stay in the entered-since-freeze bucket.
AFTER_LANE_L5_OVER_Y2 = (124, {"R": 17, "W": 103, "R+W": 4})

EXPECTED_NOW = AFTER_LANE_L5_OVER_Y2


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
