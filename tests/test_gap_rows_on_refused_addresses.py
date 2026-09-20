"""The refused-address check must RUN, and must still be able to FAIL.

WHY THE SCRIPT ALONE IS NOT ENOUGH. `scripts/check_gap_rows_on_refused_addresses.py`
was shown failing on the real pre-edit census -- it convicts the eight rows the
write-partition wave moved -- but a check that runs only when somebody
remembers to run it is a check that has already stopped working and nobody has
noticed yet. This is the house pattern, copied from
`tests/test_contingent_writeoffs_carry_a_reopener.py`.

THREE TESTS, AND THE LAST TWO ARE THE ONES THAT WILL SAVE SOMEBODY. The first
asserts the pinned property. The second re-runs the script's own
`--demonstrate-red`, which plants a GAP row on a REFUSED address into a copy of
the real census and asserts the check convicts it. The third is the half a red
usually forgets: it plants a GAP row on an ADMITTED address and asserts the
check CLEARS it, because a rule that convicts everything is not discriminating,
it is failing.

**A GREEN FIRST TEST IS AMBIGUOUS ON ITS OWN.** It passes when the census is
clean AND when the walk has been broken into something that finds nothing, or
the shipped gate has been mutated into a no-op. Those look identical from
outside, which is why the script prints per-slice and per-gate liveness and why
this file asserts on those lines rather than only on the exit code.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_gap_rows_on_refused_addresses.py"

#: The pin. A move in EITHER direction is meant to fail: see the script's own
#: docstring for why a silent fix is as loud as a new offender. The unit is a
#: ROW, never a (row, address) pair.
EXPECTED_GAP_ROWS = 5


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT), capture_output=True, text=True,
    )


def test_the_check_script_is_present():
    """A wiring test whose subject has been renamed is a test of nothing."""
    assert SCRIPT.is_file(), (
        f"{SCRIPT} is missing. If it was renamed, repoint this file; if it was "
        f"deleted, the census lost its only standing check that a GAP row is "
        f"not sitting on an address the shipped read gate already refuses, "
        f"which is this census's own named bar for EXCLUDED-RULED."
    )


def test_gap_rows_on_refused_addresses_is_pinned():
    """The property, plus the two liveness lines that make a green meaningful."""
    p = _run("--expect-gap", str(EXPECTED_GAP_ROWS))
    assert p.returncode == 0, (
        "the number of GAP rows sitting on an address the shipped read gate "
        "refuses on a forbidden substring has moved. MORE means a row was "
        "filed GAP against this census's own bar for EXCLUDED-RULED; FEWER "
        "means one was resolved and this pin was not updated:\n"
        + p.stdout + p.stderr
    )
    # An assertion satisfied by an empty result cannot fail. The script prints
    # what it walked and what the gate did; a run that walked nothing, or a
    # gate that refused nothing, must not read as a pass here.
    assert "stated rows read" in p.stdout, (
        "the check passed without reporting that it read any census rows:\n"
        + p.stdout + p.stderr
    )
    assert "REFUSED-SUBSTRING" in p.stdout, (
        "the check passed without the shipped gate refusing anything on a "
        "forbidden substring, which is what a no-op gate looks like:\n"
        + p.stdout + p.stderr
    )


def test_the_check_can_convict_and_can_clear():
    """The control. A check that cannot fail certifies nothing.

    Asserting on the printed markers rather than only the exit code, because a
    red demonstration that silently skipped a half would still exit 0.
    """
    p = _run("--demonstrate-red")
    assert p.returncode == 0, (
        "the check could not convict a planted GAP row on a refused address, "
        "or convicted one on an admitted address:\n" + p.stdout + p.stderr
    )
    assert "ALL THREE REDS FIRED" in p.stdout, (
        "the red demonstration did not report all three reds firing:\n"
        + p.stdout + p.stderr
    )
    for marker in (
        "the walk found the planted row and the gate refused it",
        "it FAILED and it NAMED the planted row",
        "the row carrying an admitted address is cleared",
    ):
        assert marker in p.stdout, (
            f"the red demonstration never reported {marker!r}, so one part of "
            f"the control did not run:\n" + p.stdout
        )
