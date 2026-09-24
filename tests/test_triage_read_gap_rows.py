"""`scripts/triage_read_gap_rows.py` must be able to go RED, and until this
file existed nothing ran it: it sat red at HEAD on its own CONTROL 4, naming
five verdicts for rows that had left GAP, and nobody was told
(`_audit/2026-09-23-bucket3-addresses.md` 7.4).

**GREEN ON ITS OWN IS AMBIGUOUS.** It passes when the hand-authored ``TRIAGE``
table truly matches today's read-GAP population in ``profile.md`` and
``network.md`` AND when CONTROL 4's key-set diff has been broken into
something that finds no drift at all -- an empty ``missing``/``extra`` looks
identical either way. So this file plants both directions the table can rot:
a verdict for a row that has LEFT the read-GAP set (a STALE row -- the defect
that sat unnoticed at HEAD), and a row with NO verdict at all (a MISSING
row), and asserts each is NAMED in the output, never just that the exit code
moved. It also drives every ``--plant`` this module ships, and it checks
CONTROL 7 (the ``MEASURED_PAST_BY_BUCKET3`` annotation table) against the
real tree: every key it names must still carry a live verdict, and the
population CONTROL 4 compares against must not be empty -- a control over an
empty set passes vacuously and proves nothing. CONTROL 8 (the
``DECIDED_SINCE_TRIAGE`` table, added when the rulings registered on
2026-09-23 decided four RULING verdicts) is held the same way: every key must
carry RULING, and a plant that annotates a row of any other verdict is named.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import census_completion as cc  # noqa: E402
import triage_read_gap_rows as triage  # noqa: E402

# NO MODULE-LEVEL CONSTANT BEYOND THE CONVENTIONAL ``ROOT``, deliberately --
# the impact gate couples every test file that NAMES an upper-case constant
# this file defines, as a whole word, and a common word widens a one-file
# change into the full suite (`tests/test_read_addresses.py` carries the same
# note about its own first draft's ``REAL``).


def _run(capsys, argv: list[str] | None = None) -> tuple[int, str]:
    code = triage.main(argv or [])
    return code, capsys.readouterr().out


# ----------------------------------------------------------------- green


def test_green_on_the_real_tree(capsys) -> None:
    code, out = _run(capsys)
    assert code == 0, out
    assert "identical -- OK" in out
    assert "annotations, every key carries a verdict -- OK" in out
    assert "decided since the triage, each a RULING verdict -- OK" in out
    assert "THE READ-GAP TRIAGE, BY REMAINING COST" in out


# ------------------------------------------------- the two ways it rots


def test_a_stale_row_turns_it_red(monkeypatch, capsys) -> None:
    """A verdict for a row that has LEFT the read-GAP set -- CONTROL 4's 'extra'.

    Found AT RUNTIME off ``census_completion.walk()`` rather than a hardcoded
    row id, so this control does not rot into a false alarm the day the row
    it once named gets banked or re-adjudicated.
    """
    victim = None
    for letter, row_id, state, direction in cc.walk():
        if letter in ("P", "N") and direction == "R" and state != "GAP":
            victim = f"{letter} {row_id}"
            break
    assert victim is not None, (
        "no read-direction P/N row outside GAP was found to plant a stale "
        "verdict on -- the census may have changed shape")

    patched = dict(triage.TRIAGE)
    patched[victim] = ("BUILDABLE", "", "planted: a stale verdict")
    monkeypatch.setattr(triage, "TRIAGE", patched)

    code, out = _run(capsys)
    assert code == 1, out
    assert f"VERDICT for {victim}, which is NOT a read GAP row today" in out


def test_a_missing_verdict_turns_it_red(monkeypatch, capsys) -> None:
    """A read-GAP row with NO verdict at all -- CONTROL 4's 'missing'."""
    real = dict(triage.TRIAGE)
    victim = sorted(real)[0]
    patched = dict(real)
    del patched[victim]
    monkeypatch.setattr(triage, "TRIAGE", patched)

    code, out = _run(capsys)
    assert code == 1, out
    assert f"NO VERDICT for {victim}" in out


# ------------------------------------------------------- every shipped plant


@pytest.mark.parametrize("plant, named", [
    ("drop-a-row", "NO VERDICT for "),
    ("bad-verdict", "which is not one of "),
    ("stale-census", "which is NOT a read GAP row today"),
    ("stale-annotation", "N 99999 carries an annotation but NO VERDICT"),
    ("undecided-annotation", "is annotated as decided, and carries "),
    ("unmarked-returned", "carries RETURNED and its cell has no returned-row marker"),
])
def test_every_built_in_plant_refuses(plant, named, capsys) -> None:
    """Each plant is refused BY THE CONTROL BUILT FOR IT, not merely refused.

    A bare "REFUSING TO REPORT" would pass if the wrong control fired -- the
    stale-annotation plant caught by CONTROL 4, say -- and CONTROL 7 could then
    be dead with this test green.
    """
    code, out = _run(capsys, ["--plant", plant])
    assert code == 1, out
    assert "REFUSING TO REPORT" in out
    assert named in out, out


# ------------------------------------------------- CONTROL 7's own coverage


def test_the_annotation_control_reads_the_real_dict() -> None:
    """Every MEASURED_PAST_BY_BUCKET3 key is a live TRIAGE key, and it is non-empty."""
    assert triage.MEASURED_PAST_BY_BUCKET3
    assert set(triage.MEASURED_PAST_BY_BUCKET3) <= set(triage.TRIAGE)


def test_the_decided_control_reads_the_real_dict() -> None:
    """Every DECIDED_SINCE_TRIAGE key is a live TRIAGE key carrying RULING, and it is non-empty."""
    assert triage.DECIDED_SINCE_TRIAGE
    for key in triage.DECIDED_SINCE_TRIAGE:
        assert triage.TRIAGE[key][0] == "RULING", key


def test_the_control_4_population_is_not_empty_and_equals_the_key_set() -> None:
    """A control over an empty set passes vacuously and proves nothing."""
    reads = {k for k, d in triage.read_rows().items() if d == "R"}
    assert reads
    assert set(triage.TRIAGE) == reads
