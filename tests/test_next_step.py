"""The next-step ledger and the capture queue, held to the census.

`scripts/check_next_step.py` is the instrument; this file runs it on the
committed tables and re-runs its planted-defect controls, so the instrument is
seen failing on every run and not only on the day it was written
(`_audit/2026-09-28-lane-k-ledger.md`, section 9).
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _check_next_step_can_fail as controls  # noqa: E402
import check_next_step as cns  # noqa: E402


def test_the_committed_ledger_and_queue_are_green():
    rows, qrows, problems, _not_checked = cns.check()
    assert problems == [], "\n".join(problems[:20])
    assert len(rows) == len(cns.population())
    assert qrows, "the capture queue is empty"


def test_the_unplanted_copies_are_green():
    """The control: without it, a red below could be the copy's, not the plant's."""
    problems, _expected = controls.run(None)
    assert problems == [], "\n".join(problems[:20])


@pytest.mark.parametrize("kind", controls.DEMONSTRATIONS)
def test_each_planted_defect_is_caught_by_name(kind):
    problems, expected = controls.run(kind)
    assert any(expected in p for p in problems), (
        f"demonstration {kind}: the checker did not report {expected!r}; it reported "
        f"{problems[:5]}")


def test_every_kind_in_the_ledger_is_one_the_checker_knows():
    rows, _q, _p, _nc = cns.check()
    kinds = {r["next"].split(":", 1)[0] for r in rows}
    assert kinds <= set(cns.KINDS), kinds - set(cns.KINDS)
