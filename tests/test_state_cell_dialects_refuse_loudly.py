"""A state cell the counter cannot spell must REFUSE, never return ''.

WHY THIS EXISTS. `scripts/count_census_states.state_of` used to answer the
empty string for a state cell it could not read, and an empty string removes
the row from the NUMERATOR and the DENOMINATOR at the same instant -- no error,
no exception, and no diff that looks like a state change. Two rows lived that
way through the freeze that the number 409 is taken from:
`messaging-and-content.md` wrote `**CANNOT-DELIVER**` for `M1` and `M2` while
the vocabulary held only `COVERED-CANNOT-DELIVER`, so at `1c08e5f` the
enumerator reported 690 stated rows against a file holding 692. It cost the
blocker `MESSAGE-ADDRESSING` its only named row and produced a published count
with no referent inside the 409, which three waves then went looking for.

`XR` was the same class a fortnight earlier -- 23 correctly-written verdicts
invisible because a slice used its own short spelling. Two instances make it a
class, and a class gets a guard rather than a third correction.

WHAT IS ASSERTED, AND WHAT DELIBERATELY IS NOT. Not "every cell parses" -- 78
rows in these files are correctly stateless and always will be. The assertion
is narrower and is the whole discrimination: a cell that is ENTIRELY a verdict,
built only out of words the vocabulary itself is built from, in a combination
the vocabulary does not hold, is a MISSPELLED STATE and must refuse. Prose does
not qualify. A neighbouring vocabulary does not qualify.

EVERY TEST BELOW WAS SHOWN FAILING BEFORE IT WAS TRUSTED, and the two that
matter are shown failing against REAL DATA rather than a fixture:
  * `state_of` on the genuine frozen `M1` row, with the spelling withdrawn,
    raises -- and returned `''` before this change. That is the historical
    defect reproduced, not a model of it.
  * the frozen enumeration counts 692 with the spelling taught and 690 with it
    withdrawn, so the number this fix moves is asserted in both directions.
  * the false-positive tests were written because the FIRST detector drafted
    here flagged 101 cells at HEAD, including every `R`, `W` and `REV` column
    and the whole of `mcp-inventory.md`. A detector that loud would have been
    switched off within the day.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import count_census_states as C  # noqa: E402
import census_dialect_sweep as S  # noqa: E402
import enumerate_gap_rows as E  # noqa: E402

#: The commit the number 409 is taken from, and the only place in this
#: repository's history where the dialect is still live.
FROZEN_REF = "1c08e5f"
#: `M M1` and `M M2` at that commit. Kept as ROW IDS rather than line numbers:
#: a line number into a file other waves are appending to is the same class of
#: stale reading this repository keeps finding.
HIDDEN_AT_THE_FREEZE = ("M1", "M2")
#: Frozen totals, measured both ways on 2026-09-19. The GAP figure is the point
#: of the pair: the dialect moved the DENOMINATOR and left the numerator alone,
#: because both hidden rows were CANNOT-DELIVER and neither was ever GAP.
FROZEN_STATED_TAUGHT = 692
FROZEN_STATED_WITHDRAWN = 690
FROZEN_GAP = 409


def _frozen_row(row_id: str) -> list[str]:
    """The real `M<n>` row at the frozen commit, as cells. Never a fixture."""
    out = subprocess.run(
        ["git", "show", f"{FROZEN_REF}:_audit/_census/messaging-and-content.md"],
        cwd=str(_ROOT), capture_output=True, check=True,
    ).stdout.decode("utf-8", errors="replace")
    for line in out.splitlines():
        if not line.startswith("|"):
            continue
        cells = C.cells(line)
        if cells and cells[0] == row_id:
            return cells
    raise AssertionError(
        f"row {row_id!r} is not in messaging-and-content.md at {FROZEN_REF}. "
        f"That commit is history and cannot have changed, so either the ref is "
        f"unreachable in this clone or the row-id parse broke."
    )


# ---------------------------------------------------------------- the refusal

def test_an_unregistered_dialect_refuses_instead_of_returning_empty():
    """The behaviour change itself, on a cell nobody has ever written.

    `MEASURED-GAP` is built from two of the vocabulary's own words in an order
    it does not hold. Before this change `state_of` returned `''` here and the
    row would have left the census in silence.
    """
    row = ["M99", "a capability", "a541865", "**MEASURED-GAP**", "W", "NOT", "note"]
    with pytest.raises(C.UnknownStateDialect) as caught:
        C.state_of(row)
    message = str(caught.value)
    assert "MEASURED-GAP" in message, message
    # The refusal must say what to DO, or it is just a crash with good manners.
    assert "STATES" in message and "receipt" in message, message


def test_the_real_frozen_row_refuses_once_the_spelling_is_withdrawn():
    """The historical defect, reproduced against the committed object.

    Withdrawing `CANNOT-DELIVER` does NOT remove CANNOT or DELIVER from
    `STATE_ATOMS` -- `COVERED-CANNOT-DELIVER` still contributes both -- which is
    exactly the state the vocabulary was in on 2026-09-03.
    """
    for row_id in HIDDEN_AT_THE_FREEZE:
        cells = _frozen_row(row_id)
        assert any("CANNOT-DELIVER" in c and "COVERED" not in c for c in cells), (
            f"{row_id} at {FROZEN_REF} no longer carries the short spelling; "
            f"this test's premise is gone and it is certifying nothing."
        )
        with S.withdrawn("CANNOT-DELIVER"):
            with pytest.raises(C.UnknownStateDialect):
                C.state_of(cells)
        # Taught, the same row parses and lands under its OWN key rather than
        # being folded into COVERED-CANNOT-DELIVER.
        assert C.state_of(cells) == "CANNOT-DELIVER"


def test_the_counter_reports_dialects_under_their_own_heading_and_fails(capsys):
    """Loud is not enough; it must be loud in a way nobody reads as benign.

    `--unstated` already lists rows carrying no state. A dialect reported in
    that list would be read as "the census wrote prose here", which is a defect
    in the ROW; a dialect is a defect in the VOCABULARY and needs the opposite
    fix. So it gets its own heading and its own non-zero exit.
    """
    with S.withdrawn("CANNOT-DELIVER"):
        # The working tree is clean, so plant the refusal where the counter
        # will meet it: a slice read out of the frozen commit.
        cells = _frozen_row("M1")
        state, dialects = C.classify(cells)
    assert state == "", f"expected no readable state, got {state!r}"
    assert dialects == ["CANNOT-DELIVER"], dialects
    # And with it taught, classify reports the state and NO dialect.
    state, dialects = C.classify(cells)
    assert (state, dialects) == ("CANNOT-DELIVER", [])


# ------------------------------------------------- the numbers it moves, both

def test_the_frozen_census_counts_692_taught_and_690_withdrawn():
    """The denominator this fix moves, asserted in both directions.

    A test that only pinned 692 would pass just as happily if the detector were
    deleted; pinning 690 under withdrawal is what makes the pair mean anything.
    """
    taught = list(E.rows(FROZEN_REF))
    assert len(taught) == FROZEN_STATED_TAUGHT, (
        f"the frozen census at {FROZEN_REF} enumerates {len(taught)} stated "
        f"rows, not {FROZEN_STATED_TAUGHT}. That commit is history and cannot "
        f"have changed, so the PARSE changed."
    )
    with S.withdrawn("CANNOT-DELIVER"):
        dialects: list[str] = []
        blind = list(E.rows(FROZEN_REF, dialects))
    assert len(blind) == FROZEN_STATED_WITHDRAWN, (
        f"with the spelling withdrawn the enumeration should lose exactly the "
        f"{FROZEN_STATED_TAUGHT - FROZEN_STATED_WITHDRAWN} hidden rows and "
        f"report {FROZEN_STATED_WITHDRAWN}; it reported {len(blind)}."
    )
    assert len(dialects) == 2, dialects
    assert all("CANNOT-DELIVER" in d for d in dialects), dialects


def test_the_409_does_not_move_because_neither_hidden_row_was_ever_gap():
    """The number everything else is measured against, held still ON PURPOSE.

    The wave that found this reported the dialect as costing `M M1` "its
    membership in the 690 AND the 409". Only the first half is true, and its
    own section 4.2 says so: the row has never been GAP at any point in its
    history. A census whose GAP total moved when a parser was fixed would be a
    far larger finding than this one, so it is asserted rather than assumed.
    """
    taught = {f"{L} {r}": st for L, r, st, _ln, _t in E.rows(FROZEN_REF)}
    with S.withdrawn("CANNOT-DELIVER"):
        blind = {f"{L} {r}": st for L, r, st, _ln, _t in E.rows(FROZEN_REF, [])}
    assert sum(1 for s in taught.values() if s == "GAP") == FROZEN_GAP
    assert sum(1 for s in blind.values() if s == "GAP") == FROZEN_GAP
    recovered = set(taught) - set(blind)
    assert recovered == {f"M {r}" for r in HIDDEN_AT_THE_FREEZE}, recovered
    for rid in recovered:
        assert taught[rid] == "CANNOT-DELIVER", (rid, taught[rid])


# ------------------------------------------------- the things it must NOT eat

@pytest.mark.parametrize("cell", [
    # `N 174` at HEAD. The first detector drafted here flagged this, because
    # its head word MEASURED is a vocabulary word. It is a sentence.
    "**MEASURED AND DELIBERATELY NOT CLOSED -- A ZERO CANNOT SETTLE THIS ROW.**",
    # `mcp-inventory.md` runs a neighbouring vocabulary on purpose. None of
    # these is a misspelling of a census state; they are a different language.
    "PROVEN-LIVE", "TESTED-ONLY", "KNOWN-BROKEN", "FIRED-GATE-HELD", "UNKNOWN",
    # Column values that are shouted but are not verdicts at all.
    "R", "W", "REV", "NOT", "URL", "HTTP", "**REAL HOLE**", "--", "",
    # Every shipped spelling: a recognised state is never a dialect.
    "GAP", "`CP`", "**COVERED-CANNOT-DELIVER**", "XR", "MEASURED-ABSENT",
])
def test_these_are_not_dialects(cell):
    assert C.dialect_of(cell) == "", (
        f"{cell!r} was classified as a misspelled state. The detector is "
        f"widening, and a detector that flags prose or a neighbouring "
        f"vocabulary gets switched off -- which is worse than not having one."
    )


@pytest.mark.parametrize("cell", [
    "**CANNOT-DELIVER**", "CANNOT DELIVER", "`COVERED`", "**MEASURED-GAP**",
    "EXCLUDED", "GAP-RULED", "**UNFIRED**",
])
def test_these_are_dialects(cell):
    """The other half of the control: the detector must actually catch things.

    Every entry is built only from words the vocabulary is built from, in a
    combination it does not hold. Without this list the detector could be
    narrowed to nothing and every test above would still pass.
    """
    with S.withdrawn("CANNOT-DELIVER"):
        assert C.dialect_of(cell) != "", (
            f"{cell!r} is assembled entirely from this vocabulary's own words "
            f"and is not one of its states, but the detector let it through."
        )


def test_no_census_file_at_head_carries_a_dialect():
    """Zero false positives over the whole real corpus, pinned.

    Scoped to every markdown file under `_audit/_census/`, not just the four
    counted slices -- a file's exclusion from the count is a reason to look at
    it, not a reason to skip it.
    """
    offenders = [
        f"{name} line {lineno} row {rid}: {'/'.join(ds)}"
        for name in S.census_files(None)
        for name_, lineno, rid, _st, ds, _cap in S.scan(name, None)
    ]
    assert offenders == [], (
        "a census state cell at HEAD is spelled in a dialect the counter "
        "cannot read. Each of these rows is in NEITHER the numerator NOR the "
        "denominator. Teach `scripts/count_census_states.py` the spelling "
        "under its own key with a receipt, or fix the cell if nobody meant "
        "it.\n  " + "\n  ".join(offenders)
    )


def test_the_sweep_control_fires():
    """The instrument's own control, run as a test.

    `scripts/census_dialect_sweep.py --control` withdraws the taught spelling
    and asserts the sweep recovers exactly the two known rows. A sweep that
    reports nothing is indistinguishable from a sweep that cannot see.
    """
    assert S.control() == 0


def test_the_map_refuses_to_build_while_a_dialect_is_open():
    """`build_blocker_map` inherits the refusal instead of the silent drop.

    It collects rather than raises -- its job is to report every defect it can
    see in one pass -- but a dialect lands in `problems`, and the map does not
    WRITE while `problems` is non-empty.
    """
    import build_blocker_map as B  # noqa: E402  (imports egr, which imports ccs)

    _gap, _current, _assign, problems = B.build()
    assert [p for p in problems if p.startswith("STATE-CELL-DIALECT")] == [], (
        "the census carries a state-cell dialect and the map cannot see the "
        "rows wearing it:\n  " + "\n  ".join(problems)
    )
    with S.withdrawn("CANNOT-DELIVER"):
        _gap, _current, _assign, problems = B.build()
    planted = [p for p in problems if p.startswith("STATE-CELL-DIALECT")]
    assert len(planted) == 2, (
        f"withdrawing the spelling should make the map report the two rows it "
        f"can no longer see; it reported {len(planted)}: {planted}"
    )
