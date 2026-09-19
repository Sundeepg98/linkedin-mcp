"""The map's UNASSIGNED reason cell must be a measurement, not a default.

THE DEFECT. `_audit/_census/blocker-map.tsv` carried one generated sentence
against every unassigned row: "no committed source names this row against any
blocker". That is a UNIVERSAL NEGATIVE, and the generator had checked exactly
one file before asserting it -- `blocker-assignments.tsv`. It was FALSE for six
rows: `scripts/_probe_jobs_tail_boundary.py` names `J 78`-`J 83` against
`PREMIUM-APPLY-SURFACES`, in a tracked file, in one comment. A sweep reading
that column would have concluded the six were unnamed and gone looking for a
source that was already there.

THE SECOND HALF, WHICH IS WHY THE FIX IS NOT AN ASSIGNMENT. The probe names SIX
rows; the ledger publishes that blocker at FIVE. Filing all six trips the
over-count assertion, and filing five of six is a CHOICE wearing a forced row's
clothes -- the exact reasoning that pulled `J 82` back out of this blocker on
2026-09-19. So the rows stay UNASSIGNED and the CELL changes: named, not
fileable, with the arithmetic printed.

THE CELL IS DERIVED, NEVER RETYPED, which is the only version of this fix that
cannot rot. The blocker name, the row range and the line number are all parsed
out of the probe on every run, and the published count comes from the ledger's
own tables. If the mark disappears the derivation raises a PROBLEM rather than
falling back to the sentence that was measured false.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import build_blocker_map as B  # noqa: E402

#: The six rows a committed probe names and the map could not say so about.
NAMED_ROWS = [f"J {n}" for n in range(78, 84)]
BLOCKER = "PREMIUM-APPLY-SURFACES"
#: The claim that was false. Kept verbatim so this test fails if it returns.
THE_FALSE_DEFAULT = "no committed source names this row against any blocker"


@pytest.fixture(scope="module")
def marks():
    found, problems = B.probe_marks()
    assert problems == [], problems
    return found


@pytest.fixture(scope="module")
def published():
    return B.ledger_counts()


def test_the_probe_really_does_name_the_six_rows(marks):
    """The premise, measured before anything is asserted about the cell.

    If the probe stops naming them the whole fix is pointless and the rest of
    this file would be asserting a story rather than a fact.
    """
    for rid in NAMED_ROWS:
        assert rid in marks, (
            f"{rid} is no longer named by any probe mark. Either the mark was "
            f"edited or the spec grammar broke; the reason cell will have "
            f"reverted to a claim that was measured false."
        )
        source, locator, blocker, rows_named = marks[rid]
        assert blocker == BLOCKER, (rid, blocker)
        assert rows_named == 6, (rid, rows_named)
        # The locator is COMPUTED, so prove it points at the real line rather
        # than at a number somebody typed once and nobody re-read.
        lineno = int(locator.lstrip("L"))
        line = (_ROOT / source).read_text(
            encoding="utf-8", errors="replace").splitlines()[lineno - 1]
        assert BLOCKER in line and "census rows" in line, (locator, line)


def test_the_six_rows_no_longer_claim_that_nobody_names_them(marks, published):
    for rid in NAMED_ROWS:
        _b, _k, source, locator, note = B.unassigned_row(rid, marks, published)
        assert THE_FALSE_DEFAULT not in note, (
            f"{rid} still carries the false default. A committed source names "
            f"it and the cell says nobody does."
        )
        assert note.startswith("NAMED-UNFILEABLE"), note
        assert BLOCKER in note, note
        assert source.endswith("_probe_jobs_tail_boundary.py"), source
        assert locator.startswith("L"), locator
        # The arithmetic conflict is the REASON it cannot be filed, and it must
        # be in the cell -- otherwise the next reader files six into five.
        assert "6 rows" in note and f"at {published[BLOCKER]}" in note, note


def test_the_blocker_and_the_row_ids_stay_unassigned(marks, published):
    """Naming a row is not filing it, and this generator does not promote.

    Also pins the two columns downstream readers and
    `test_blocker_map_is_derived` key on: moving the distinction into
    `evidence_class` would have broken a sibling's committed artifact to make a
    point that belongs in the reason cell.
    """
    for rid in NAMED_ROWS:
        blocker, klass, *_rest = B.unassigned_row(rid, marks, published)
        assert (blocker, klass) == ("UNASSIGNED", "UNASSIGNED"), (rid, blocker, klass)


def test_a_row_nothing_names_says_what_was_actually_searched(marks, published):
    """The honest default names its own scope instead of asserting a universal.

    `J 18` is unassigned and no probe mark names it. The cell may say so -- but
    it has to say WHERE it looked, because "no committed source" is a claim
    about every file in the repository and the generator reads two.
    """
    assert "J 18" not in marks
    _b, _k, source, locator, note = B.unassigned_row("J 18", marks, published)
    assert THE_FALSE_DEFAULT not in note, note
    assert "blocker-assignments.tsv" in note, note
    assert "_probe_jobs_tail_boundary.py" in note, note
    assert (source, locator) == ("-", "-")


# --------------------------------------------------- the grammar, and the red

@pytest.mark.parametrize("spec,expected", [
    ("J78-J83.", [f"J {n}" for n in range(78, 84)]),
    ("J54-J56.", ["J 54", "J 55", "J 56"]),
    ("J31-J36 and J41, all writes.",
     [f"J {n}" for n in range(31, 37)] + ["J 41"]),
    ("J78-83.", [f"J {n}" for n in range(78, 84)]),
    ("N 5.", ["N 5"]),
    ("nothing numeric here", []),
])
def test_the_row_spec_grammar(spec, expected):
    assert B._expand(spec) == expected


def test_a_probe_that_stops_carrying_a_mark_is_a_problem_not_a_silent_revert(
        tmp_path, monkeypatch, published):
    """The failure mode, which is the whole reason this is derived.

    A hand-written table would go stale in silence. The derivation cannot: if
    the source stops parsing, `probe_marks` reports it, `build` puts it in
    `problems`, and the map refuses to write.
    """
    fake = tmp_path / "probe.py"
    fake.write_text("# a probe with no census-row mark at all\n", encoding="ascii")
    monkeypatch.setattr(B, "ROOT", tmp_path)
    monkeypatch.setattr(B, "NAMED_BY_PROBES", ("probe.py",))
    found, problems = B.probe_marks()
    assert found == {}
    assert len(problems) == 1 and "no parseable" in problems[0], problems
    # And with no marks the six rows fall back to the SCOPED default, never to
    # the universal negative.
    _b, _k, _s, _l, note = B.unassigned_row("J 78", found, published)
    assert THE_FALSE_DEFAULT not in note, note


def test_a_missing_probe_file_is_a_problem(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "ROOT", tmp_path)
    monkeypatch.setattr(B, "NAMED_BY_PROBES", ("gone.py",))
    found, problems = B.probe_marks()
    assert found == {}
    assert problems and "missing" in problems[0], problems


def test_the_reason_follows_the_ledger_rather_than_a_hardcoded_number(marks):
    """Change the published count and the cell's argument must change with it.

    This is what separates a derivation from a sentence somebody typed that
    happens to be true today.
    """
    over = B.unassigned_row("J 78", marks, {BLOCKER: 5})[4]
    assert "over-count" in over and "at 5" in over, over
    fits = B.unassigned_row("J 78", marks, {BLOCKER: 9})[4]
    assert "over-count" not in fits and "publishes 9" in fits, fits
    absent = B.unassigned_row("J 78", marks, {})[4]
    assert "do not publish" in absent, absent
