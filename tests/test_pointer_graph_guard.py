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

import os
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


def test_two_concurrent_selftests_do_not_collide(tmp_path):
    """Two lanes running `--selftest` at once must not delete each other's sandbox.

    WHAT IT GUARDS. `--selftest` used to build at ONE fixed path,
    `<temp>/pointer-graph-selftest`, and `make_sandbox` starts with an `rmtree` -- so
    two worktrees gating at the same moment deleted each other's tree mid-check, and
    the test above failed intermittently in every lane. Each run now makes its own
    directory and removes it when it ends.

    WHY THE SENTINEL, and it is what makes this a test rather than a lottery. Two runs
    that merely overlap collide only when their controls happen to interleave, so a
    race test built on timing alone passes by luck whenever they do not. The SENTINEL
    sits at the OLD fixed path and stands for another run's live sandbox: code that
    still builds there deletes it on its first control, every time, so the old defect
    fails this test DETERMINISTICALLY, not by luck of timing. The two concurrent runs
    are the realistic load on top of that, and the leftover check proves each run
    cleaned up after itself rather than trading a collision for a leak.
    """
    root = tmp_path / "tmp"
    sentinel = root / "pointer-graph-selftest" / "SENTINEL"
    sentinel.parent.mkdir(parents=True)
    sentinel.write_text("another run's live sandbox\n", encoding="ascii")
    # All three: `tempfile.gettempdir()` takes the first of TMPDIR, TEMP and TMP that
    # names a usable directory, so setting one would leave the child free to pick
    # another -- and to run against the real, shared temp directory.
    env = dict(os.environ, TMPDIR=str(root), TEMP=str(root), TMP=str(root))
    runs = [subprocess.Popen([sys.executable, str(SCRIPT), "--selftest"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, cwd=str(ROOT), env=env)
            for _ in range(2)]
    try:
        outs = [(p.communicate(timeout=900)[0], p.returncode) for p in runs]
    finally:
        for p in runs:          # a hung run must not outlive the test that started it
            if p.poll() is None:
                p.kill()
                p.wait()
    both = "\n----- the other run -----\n".join(out for out, _rc in outs)

    # The two DETERMINISTIC checks go first, so a failure names its cause the same way
    # every time; whether the runs also crashed each other depends on timing.
    assert sentinel.exists(), (
        "a selftest deleted <temp>/pointer-graph-selftest: it still builds at the old "
        "fixed path, so two lanes gating at once delete each other's sandbox.\n" + both)
    left = sorted(d.name for d in root.glob("pointer-graph-selftest-*"))
    assert left == [], (
        f"a selftest left its per-run directory behind: {left}. A run that does not "
        f"remove its own sandbox fills the temp directory one gate at a time.\n" + both)
    for out, rc in outs:
        assert rc == 0, both
        assert "all 5 controls behaved as specified" in out, both
