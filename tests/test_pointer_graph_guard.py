"""`scripts/measure_pointer_graph.py --check` must be able to go RED.

WHAT IT GUARDS. 66 census reason cells (69 until the live lane's merge,
2026-09-24, which banked `N 134` and wrote out `N 135`'s vestigial pointer;
67 until lane L7's merge the same day, which named `P G3`'s ruling in place of
its positional 'same ruling') say
`same` and resolve BY POSITION to the
nearest substantive row above them in the same table. Nothing marks a row as
load-bearing for the rows beneath it, so a row inserted mid-table re-points every
dependent below it and changes its classification -- with no edit to those rows, no
error and no warning. Measured on this corpus: 71 insertion slots, 48 of which move a
published verdict, and 45 distinct write-off rows whose argument can be changed by an
edit that never touches them. `scripts/measure_pointer_graph.py --plant-sweep`
reproduces that measurement; this file guards against it happening unnoticed.

WHY IT IS A THIN WRAPPER AND THAT IS DELIBERATE. The mutations live in the instrument
itself (`--selftest`) because they need its sandbox, its pin and its plant. Copying
them here would give two implementations of one control that can disagree, which is
the defect this repository spent a day measuring in the census. One source of truth,
asserted from outside.

THE CALIBRATION IS PART OF THE CONTROL, NOT A COURTESY. `--selftest` includes a
mutation that must NOT fire. A harness where every mutation goes red is not
discriminating, it is broken, and there is no way to tell that from the red alone.

WHAT THIS DOES NOT PROVE, said here so a green is not read as wider than it is:
`--selftest` overlays the WORKING TREE's scripts and census into its sandbox, so it
proves the guard convicts as the tree stands. It does not prove anything about HEAD.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "measure_pointer_graph.py"
PIN = ROOT / "_audit" / "_census" / "pointer-graph.tsv"

#: Every control `--selftest` runs, by the prefix it prints. Named here so a control
#: that is silently DELETED from the instrument fails this file, rather than shrinking
#: the suite to nothing and passing. A test that asserts only "exit 0" cannot tell a
#: complete run from an empty one.
CONTROLS = ("G1 re-point", "G2 donor rewrite", "G3 jobs.md loses every pointer",
            "G4 pin holds a header and no rows", "G5 CALIBRATION")


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=str(ROOT))


def test_the_pin_exists_and_is_not_empty():
    """A guard with no baseline is not a guard that passes; it is one that never ran."""
    assert PIN.exists(), f"no pin at {PIN}; run --pin"
    lines = PIN.read_text(encoding="ascii", errors="replace").splitlines()
    assert len(lines) > 1, "the pin holds a header and no rows"
    slices = {line.split("\t")[5] for line in lines[1:]}
    # PER SLICE, never over the union: if one slice lost every pointer, a union count
    # would still look plausible and nothing would say a source had gone dark.
    assert slices == {"jobs.md", "profile.md", "messaging-and-content.md",
                      "network.md"}, f"the pin is missing a slice: {sorted(slices)}"


def test_the_committed_census_still_matches_its_pin():
    p = _run("--check")
    assert p.returncode == 0, (
        "a pinned pointer's argument moved without that pointer being edited:\n"
        + p.stdout + p.stderr)
    assert "PASS -- all" in p.stdout


def test_every_failure_class_is_convicted_and_the_calibration_is_not():
    p = _run("--selftest")
    out = p.stdout + p.stderr
    for control in CONTROLS:
        assert control in out, (
            f"control {control!r} did not run. A suite that quietly loses a control "
            f"reports the same green as one that passed it.\n" + out)
    assert p.returncode == 0, out
    assert "all 5 controls behaved as specified" in out, out
