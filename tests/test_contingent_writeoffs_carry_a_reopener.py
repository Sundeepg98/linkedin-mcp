"""The contingent-reopener guard must RUN, and must still be able to FAIL.

WHY THIS FILE EXISTS AND THE SCRIPT ALONE IS NOT ENOUGH. `scripts/
check_contingent_writeoffs_carry_a_reopener.py` was shown failing the day it
was written -- but a guard that only runs when somebody remembers to run it is
a guard that has already stopped working and nobody has noticed yet. The same
law the register applies to instruments applies to their wiring: a check nobody
executes certifies nothing. This is the house pattern, copied from
`tests/test_pointer_graph_guard.py`, which wraps `measure_pointer_graph.py
--check` for exactly this reason.

TWO TESTS, AND THE SECOND IS THE ONE THAT WILL SAVE SOMEBODY. The first asserts
the property: every contingent write-off in the enforced row-set names a
condition that would reopen it. The second re-runs the guard's own
`--demonstrate-red`, which plants a contingent write-off with no trigger into a
COPY of the census and asserts the guard convicts it.

**A GREEN FIRST TEST IS AMBIGUOUS ON ITS OWN.** It passes when the census is
clean AND when the guard has been broken into something that cannot speak --
an import that quietly returns nothing, a walk that stops finding rows, a
predicate inverted. Those look identical from outside. The second test is what
separates them, and it is why breaking the guard fails CI instead of silently
widening the census.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_contingent_writeoffs_carry_a_reopener.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(ROOT), capture_output=True, text=True,
    )


def test_the_guard_script_is_present():
    """A wiring test whose subject has been renamed is a test of nothing."""
    assert SCRIPT.is_file(), (
        f"{SCRIPT} is missing. If the guard was renamed, repoint this file; if "
        f"it was deleted, the census lost its only standing check that a "
        f"contingent write-off names what would reopen it, and that needs a "
        f"ruling rather than a deletion."
    )


def test_every_contingent_writeoff_in_scope_names_a_reopener():
    """The property itself."""
    p = _run()
    assert p.returncode == 0, (
        "a write-off resting on a fact about the account or the world names no "
        "condition that would falsify it, so nothing would ever say it had "
        "changed:\n" + p.stdout + p.stderr
    )
    # An assertion satisfied by an empty result cannot fail. The guard prints
    # its own scope; a run that checked nothing must not read as a pass here.
    assert "contingent write-offs in scope carry a reopener" in p.stdout, (
        "the guard passed without reporting the scope it passed over:\n"
        + p.stdout + p.stderr
    )


def test_the_guard_can_still_convict():
    """The control. A guard that cannot fail certifies nothing.

    This runs the guard's OWN red demonstration, which plants a contingent
    write-off carrying no reopener into a copy of the four census files,
    repoints the walker at the copy and runs the shipped pipeline end to end.
    Asserting on the printed markers rather than only the exit code, because a
    red demonstration that silently skipped its expensive half would still
    exit 0.
    """
    p = _run("--demonstrate-red")
    assert p.returncode == 0, (
        "the guard could not convict a planted contingent write-off:\n"
        + p.stdout + p.stderr
    )
    assert "ALL THREE REDS FIRED" in p.stdout, (
        "the red demonstration did not report all three reds firing:\n"
        + p.stdout + p.stderr
    )
    for marker in (
        "the planted row is convicted",
        "the same row WITH a reopener is cleared",
        "the walk found the planted row",
        "the guard FAILED on the planted corpus",
        "it named the planted row",
        "a cell may not satisfy a reopener",
    ):
        assert marker in p.stdout, (
            f"the red demonstration never reported {marker!r}, so one half of "
            f"the control did not run:\n" + p.stdout
        )
