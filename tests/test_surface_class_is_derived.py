"""The SURFACE class must stay DERIVED, and its headline zero must stay a READING.

WHY THIS TEST EXISTS. `_audit/2026-09-20-the-contingent-writeoffs.md` s3.1
published a five-way classification of 97 blockers and gave one class the name
`SURFACE?` at 22 blockers / 139 rows / 108 GAP. **The classifier was never
committed and its three inputs are gitignored and no longer on disk**, so the
membership survives only as those integers -- and 186,629,988,917,605 distinct
22-blocker subsets of the residual pool fit them exactly. That is the same
defect `test_blocker_map_is_derived` exists to punish, one level up: a division
published as counts with no classifier behind it.

`scripts/classify_surface_blockers.py` is the remedy -- a membership rule that
RUNS. This file is what stops it decaying into another table nobody can re-derive.

THE HEADLINE IS A ZERO, WHICH IS THE DANGEROUS SHAPE. The wave's finding is
that **none** of the selected blockers is blocked by a surface fact; every one
names an artifact of this repo (an allowlist entry, a denylist exemption, a
WriteSpec). A zero emitted by a branch that cannot fire certifies nothing, and
this repository has shipped five checks that could not fail and found each one
later at cost. So `test_the_surface_fact_branch_can_fire` plants a boundary
cell that IS a surface fact and requires the classifier to name it.

SHOWN FAILING in five directions, four planted plus the live-branch mutation:

    ranked table header broken        every boundary cell would read as absent
    cost-0 table header broken        its blockers read as missing entirely
    one ranked row deleted            97/409 stops closing
    SURFACE blocker absent from both  a map/ledger disagreement about membership
    boundary cell made a surface fact SURFACE-FACT count must move 0 -> 1

Cases 1 and 2 are not hypothetical. On 2026-09-05 a neighbouring wave appended
19 lines to the ledger, both tables slid 28 rows down, and a hardcoded line
window lost one of them -- four blockers silently read as published 0. Both
tables here are found by HEADER ROW and a missing header is loud.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import classify_surface_blockers as csb  # noqa: E402

LEDGER_TEXT = csb.LEDGER.read_text(encoding="utf-8", errors="replace")
MAP_TEXT = csb.MAP.read_text(encoding="ascii", errors="replace")


@pytest.fixture
def repoint(tmp_path, monkeypatch):
    """Run the classifier against doctored copies. Nothing tracked is touched."""

    def _go(ledger_text=None, map_text=None):
        led = tmp_path / "ledger.md"
        mp = tmp_path / "map.tsv"
        led.write_text(LEDGER_TEXT if ledger_text is None else ledger_text,
                       encoding="utf-8")
        mp.write_text(MAP_TEXT if map_text is None else map_text,
                      encoding="ascii", errors="replace")
        monkeypatch.setattr(csb, "LEDGER", led)
        monkeypatch.setattr(csb, "MAP", mp)
        return csb.main([])

    return _go


def test_control_the_committed_tree_classifies(repoint, capsys):
    """If this is red, every planted red below is meaningless."""
    assert repoint() == 0
    out = capsys.readouterr().out
    assert "MEMBERSHIP RULE" in out
    assert "FAIL" not in out


def test_the_rule_selects_a_nonempty_class(capsys):
    csb.main([])
    out = capsys.readouterr().out
    assert "selected         26 blockers" in out, (
        "the name rule stopped selecting the 26 SURFACE-named blockers; either "
        "a blocker was renamed or the map changed shape")


def test_reason_class_is_total_over_every_ledger_boundary_cell():
    """No blocker may fall through the classifier into an unnamed state.

    A partial classifier is how a class becomes unauditable in the first place.
    """
    ledger, problems = csb.ledger_rows()
    assert not problems, problems
    known = {"ADDRESSABILITY-OURS", "WRITER-OURS", "SURFACE-FACT", "NONE-STATED"}
    for blocker, cells in ledger.items():
        assert csb.reason_class(cells["boundary"]) in known, blocker


def test_no_selected_blocker_is_blocked_by_a_surface_fact(capsys):
    """THE WAVE'S HEADLINE, pinned so a later edit reports itself.

    This is a MEASUREMENT, not a law of nature. If a future wave establishes
    that LinkedIn genuinely does not draw one of these surfaces and writes that
    into the boundary cell, this test goes red -- and that is the correct
    outcome: the finding in `_audit/2026-09-20-the-surface-class.md` s3.1 would
    then be stale, and somebody has to update it rather than discover the drift
    by accident.
    """
    csb.main([])
    out = capsys.readouterr().out
    assert "asserts a SURFACE fact: 0" in out, (
        "a SURFACE-named blocker now carries a boundary cell that asserts a "
        "fact about LinkedIn rather than about this repo. That is a real "
        "finding: re-read _audit/2026-09-20-the-surface-class.md s3 and "
        "update it.")


def test_the_surface_fact_branch_can_fire(repoint, capsys):
    """THE ONE THAT MATTERS: prove the zero above is a reading, not a default."""
    planted = LEDGER_TEXT.replace(
        "| 6 | `SEARCH-RESULTS-SURFACE` | 21 | 19R/2W | allowlist +1 |",
        "| 6 | `SEARCH-RESULTS-SURFACE` | 21 | 19R/2W | LinkedIn draws no such page |",
        1)
    assert planted != LEDGER_TEXT, (
        "the mutation did not apply -- the ledger row this test plants into "
        "has moved, so the test was about to pass without testing anything")
    assert repoint(ledger_text=planted) == 0
    out = capsys.readouterr().out
    assert "asserts a SURFACE fact: 1" in out
    assert "SEARCH-RESULTS-SURFACE" in out


def test_every_selected_blocker_has_a_candidate_address():
    """No blocker may fall out of the live-boundary check silently.

    The check prints `NOT CHECKED -- no candidate address stated for N`. That
    line is the honest fallback, but if the class grows and nobody adds the
    address, the "16 of 26" headline quietly becomes "16 of a smaller
    denominator" -- a number shrinking its own denominator is this project's
    2.3 law, and this is where it would happen.
    """
    csb.main([])
    ledger, _ = csb.ledger_rows()
    tot, _gap, _rows = csb.map_counts()
    selected = sorted(b for b in tot if csb.NAME_RULE.search(b))
    missing = [b for b in selected if b not in csb.SURFACE_ADDRESSES]
    assert not missing, (
        f"these selected blockers have no candidate address, so the live-"
        f"boundary section silently skips them: {missing}")


def test_the_live_boundary_section_actually_measured_something(capsys):
    """A blank section must not read as a clean one.

    If `linkedin_server.readonly` stops importing, the section prints UNKNOWN
    and measures nothing. That is the correct behaviour and it is also
    indistinguishable from "nothing was overtaken" unless somebody asserts on
    it -- which is this repo's A-BLIND-CHANNEL-MUST-NOT-REPORT-A-CLEAN-ABSENCE.
    """
    csb.main([])
    out = capsys.readouterr().out
    assert "THE LEDGER'S BOUNDARY CLAIM vs THE LIVE ALLOWLIST" in out
    assert "UNKNOWN -- linkedin_server.readonly did not import" not in out, (
        "the live-boundary section could not run; its findings in "
        "_audit/2026-09-20-the-surface-class.md s3.4 are unverified in this tree")
    assert "live allowlist patterns:" in out
    assert "base address ALREADY ALLOWED" in out


def test_a_broken_ranked_header_is_loud(repoint, capsys):
    broken = LEDGER_TEXT.replace(csb.RANKED_HEADER,
                                 csb.RANKED_HEADER.replace("boundary", "BOUNDARY"), 1)
    assert broken != LEDGER_TEXT
    assert repoint(ledger_text=broken) == 1
    assert "ranked table header is no longer present" in capsys.readouterr().out


def test_a_broken_costzero_header_is_loud(repoint, capsys):
    broken = LEDGER_TEXT.replace(csb.ZEROCOST_HEADER,
                                 csb.ZEROCOST_HEADER.replace("why", "WHY"), 1)
    assert broken != LEDGER_TEXT
    assert repoint(ledger_text=broken) == 1
    assert "cost-0 table header is no longer present" in capsys.readouterr().out


def test_totals_that_stop_closing_are_loud(repoint, capsys):
    lines = LEDGER_TEXT.splitlines()
    drop = next(i for i, l in enumerate(lines) if l.startswith("| 1 | `FILE-UPLOAD"))
    assert repoint(ledger_text="\n".join(lines[:drop] + lines[drop + 1:])) == 1
    assert "no longer total 97 blockers / 409 rows" in capsys.readouterr().out


def test_a_surface_blocker_in_neither_ledger_table_is_loud(repoint, capsys):
    planted = MAP_TEXT + ("Z 999\tPHANTOM-SURFACE\tUNASSIGNED\t-\t-\tGAP\tGAP\t"
                          "planted by a test\tplanted by a test\n")
    assert repoint(map_text=planted) == 1
    assert "PHANTOM-SURFACE is in the map but in NEITHER ledger table" in \
        capsys.readouterr().out
