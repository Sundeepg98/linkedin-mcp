"""Show the census row-population guard failing all THREE ways it claims to fail.

`tests/test_the_census_row_total_is_pinned.py` pins the denominator every
completion figure in this repository divides by. A pin is the cheapest thing in
this codebase to make green -- run `--write` and the guard agrees with whatever
the tree now says -- so the guard is only worth its place if it can be SHOWN
dying, on real census rows, in each of the three ways it advertises:

  A  A ROW IS ADDED.      The delta must name it as ADDED.
  B  A ROW IS DELETED.    The delta must name it as DELETED -- not merely
                          missing, but gone from the slice file.
  C  A ROW'S STATE IS CHANGED TO ONE OUTSIDE THE VOCABULARY. The row is still
                          in the file, and has still left the denominator. The
                          delta must say UNREADABLE and NOT say DELETED,
                          because those two need opposite fixes and this
                          repository has twice paid for reporting them alike.

**C IS THE ONE THAT EARNS THE FILE.** A and B are visible in a diff of the
census. C is not: the row renders exactly as it always did, the markdown table
is unchanged in shape, and the only thing that moved is a number in four other
documents. `XR` survived a fortnight that way and `CANNOT-DELIVER` survived the
freeze the number 409 is taken from.

**EACH DEMONSTRATION ALSO RUNS THE NEIGHBOUR GUARD AND REPORTS WHETHER IT
FIRED.** A guard shown failing proves it can fail; it does not prove anything
was missing. `tests/test_census_rows_carry_a_state.py` inspects every row the
counter counts -- measured at HEAD, 706 against 704 -- so the interesting claim
is not "mine goes red" but "mine goes red WHILE THE NEIGHBOUR STAYS GREEN". For
A and B the neighbour is expected to stay green, and that expectation is
ASSERTED rather than described. For C it is expected to fire too, on a
different ground (the cell is now prose), and that is recorded rather than
hidden -- C's contribution is the DISCRIMINATION between a deleted row and an
unreadable one, which nothing else in the suite makes.

**AN EARLIER DRAFT OF THIS FILE CLAIMED `network.md`'s admin-only table HAD NO
`state` COLUMN** and that demonstration A therefore ran in a zone nothing
inspects. That was measured and it is false -- the table's header is
`| # | capability | R/W | state | note |`. The claim is recorded here rather
than quietly deleted, because the counter's own `main()` still carries the
same stale belief in a comment, and the row-forcing it justifies is now
largely inert.

## IT NEVER TOUCHES THE LIVE TREE

Several agents write this repository at once and mutating a shared file even
briefly can be picked up or clobbered -- `_audit/INSTRUMENTS.md` records a wave
that did it and measured its own five-second window. So: copy
`_audit/_census`, `scripts`, `tests` and `pytest.ini` to a scratch directory,
**ASSERT** that both the census path and the pin path resolve under the copy
(assert, not print -- a human confirming an eyeballed path is not a control),
plant ONE mutation, run ONLY the selector that should die, restore that one
file byte for byte, repeat, and finish on a clean control run.

    python scripts/_check_the_census_row_pin_can_fail.py

Prints a PASS/FAIL line per demonstration and exits non-zero if any of them
does not behave exactly as stated above. **Paste the output beside any re-pin.**
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = "tests/test_the_census_row_total_is_pinned.py"

#: The three selectors, one per demonstration. Named rather than run as a whole
#: file so a demonstration cannot pass because some OTHER assertion went red.
POPULATION = f"{GUARD}::test_no_census_row_appeared_or_vanished_without_a_decision"

#: The cell-shaped neighbour. Run under every mutation so each demonstration
#: can state what the suite WITHOUT this guard would have said. It is not run
#: alongside `test_state_cell_dialects_refuse_loudly.py`, which resolves a
#: frozen baseline out of git objects by literal SHA and cannot work in a
#: scratch copy with no `.git` -- it would fail for a reason that has nothing
#: to do with the mutation, which is worse than not running it. Its relevance
#: to demonstration C is settled by a cheaper and more direct means instead:
#: `_assert_alien_is_not_a_dialect` below.
NEIGHBOUR = "tests/test_census_rows_carry_a_state.py"


def _copy_tree() -> pathlib.Path:
    """A scratch copy of everything the guard reads."""
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="census-row-pin-control-"))
    for rel in ("scripts", "tests"):
        shutil.copytree(REPO / rel, scratch / rel,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # THE WHOLE `_audit` TREE, not just `_census`. The guard's failure message
    # COMPUTES how many documents print the pinned total, and a copy holding
    # only the census would make every demonstration report `0 documents` --
    # a figure that is false about the repository and that would be pasted
    # into an audit document as evidence. A demonstration whose output cannot
    # be quoted is half a demonstration.
    shutil.copytree(REPO / "_audit", scratch / "_audit",
                    ignore=shutil.ignore_patterns("_scratch"))
    shutil.copy2(REPO / "pytest.ini", scratch / "pytest.ini")
    # The guard imports nothing from the package, but pytest.ini's rootdir
    # collection and conftest do; an absent package turns every demonstration
    # into a collection error, which would "fail" for the wrong reason.
    shutil.copytree(REPO / "linkedin_server", scratch / "linkedin_server",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return scratch


def _assert_isolated(scratch: pathlib.Path) -> None:
    """ASSERT the copy is what will be read. Confirming is what a human does.

    Both paths matter and they are computed independently: the counter derives
    the census directory from its own `__file__`, and the pin module derives
    the pin from its own. Either one resolving back to the live tree would mean
    this script is mutating the repository other agents are writing.
    """
    probe = (
        "import sys, pathlib;"
        "sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / 'scripts'));"
        "import count_census_states as C, pin_census_rows as P;"
        "print(C.CENSUS);print(P.PIN);print(C.__file__)"
    )
    out = subprocess.run([sys.executable, "-c", probe, str(scratch)],
                         capture_output=True, text=True, check=True)
    census, pin, module = [pathlib.Path(x) for x in out.stdout.split("\n")[:3]]
    for name, path in (("census", census), ("pin", pin), ("module", module)):
        assert scratch in path.parents or path.is_relative_to(scratch), (
            f"ISOLATION FAILED: the {name} path resolves to {path}, which is "
            f"NOT under the scratch copy {scratch}. Refusing to plant a "
            f"mutation -- this would edit the live tree."
        )
        assert REPO not in path.parents, (
            f"ISOLATION FAILED: the {name} path {path} sits under the live "
            f"repository {REPO}."
        )
    print(f"isolation asserted: census={census}")


def _run_guard(scratch: pathlib.Path, selector: str):
    """Run one selector inside the copy. Returns (exit_code, stdout+stderr)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", selector, "-q", "--no-header",
         "-p", "no:cacheprovider"],
        cwd=str(scratch), capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def _slice(scratch: pathlib.Path, name: str) -> pathlib.Path:
    return scratch / "_audit" / "_census" / name


def _demo(label: str, scratch: pathlib.Path, path: pathlib.Path,
          mutate, want: list[str], forbid: list[str],
          neighbour_fires: bool) -> bool:
    """Plant one mutation, run the population selector, restore, judge.

    `want`            -- substrings that MUST appear in the failure output
    `forbid`          -- substrings that must NOT, which is how C proves it is
                         not merely reporting B in different words
    `neighbour_fires` -- what the cell-shaped guard is expected to do. Asserted,
                         so "nothing else catches this" stops being a claim
                         about the suite and becomes a measurement of it.
    """
    original = path.read_bytes()
    try:
        path.write_text(mutate(original.decode("utf-8")), encoding="utf-8")
        code, out = _run_guard(scratch, POPULATION)
        n_code, _n_out = _run_guard(scratch, NEIGHBOUR)
        ok = code != 0
        missing = [w for w in want if w not in out]
        present = [f for f in forbid if f in out]
        neighbour_ok = (n_code != 0) == neighbour_fires
        ok = ok and not missing and not present and neighbour_ok
        print(f"\n--- {label} ---")
        print(f"exit code {code} (want non-zero)")
        if missing:
            print(f"MISSING from the failure text: {missing}")
        if present:
            print(f"WRONGLY PRESENT in the failure text: {present}")
        for line in out.splitlines():
            if ("ADDED" in line or "DELETED" in line or "UNREADABLE" in line
                    or "POPULATION MOVED" in line or line.startswith("E  ")):
                print(f"    {line.strip()[:200]}")
        print(f"neighbour {NEIGHBOUR.split('/')[-1]}: "
              f"exit {n_code} -- {'FIRED' if n_code else 'STAYED GREEN'}, "
              f"expected {'to fire' if neighbour_fires else 'to stay green'}"
              f"{'' if neighbour_ok else '   <-- EXPECTATION WRONG'}")
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        return ok
    finally:
        path.write_bytes(original)


def _assert_alien_is_not_a_dialect(scratch: pathlib.Path, alien: str) -> None:
    """Demonstration C is only interesting if `alien` is NOT a dialect.

    A DIALECT is a verdict built only from the vocabulary's own atoms, and the
    shipped counter REFUSES on one loudly -- so a dialect would be caught
    already and C would prove nothing new. Asserting this against the shipped
    `dialect_of` is cheaper and more exact than running the dialect test, and
    it is the claim that actually matters.
    """
    probe = (
        "import sys, pathlib;"
        "sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / 'scripts'));"
        "import count_census_states as C;"
        "print(repr(C.dialect_of(sys.argv[2])));"
        "print(sys.argv[2] in C.STATES)"
    )
    out = subprocess.run([sys.executable, "-c", probe, str(scratch), alien],
                         capture_output=True, text=True, check=True)
    dialect, in_states = out.stdout.split("\n")[:2]
    assert dialect == "''", (
        f"demonstration C is not testing what it claims: dialect_of({alien!r}) "
        f"returns {dialect}, so this is a DIALECT and the shipped counter "
        f"already refuses on it loudly. Pick a word sharing no atom with the "
        f"vocabulary."
    )
    assert in_states.strip() == "False", (
        f"demonstration C is not testing what it claims: {alien!r} is IN the "
        f"shipped vocabulary, so the row would still be counted."
    )
    print(f"precondition asserted: {alien!r} is neither a state nor a dialect, "
          f"so a row wearing it leaves the denominator in silence")


def _add_admin_row(text: str) -> str:
    """Append a sixteenth row to `network.md`'s admin-only table.

    The zone no other guard inspects: the table declares no `state` column, so
    the shipped counter forces `N A<n>` to GAP from the section prose while
    `test_census_rows_carry_a_state.py` skips the table entirely.
    """
    lines = text.splitlines()
    last = max(i for i, ln in enumerate(lines)
               if re.match(r"^\|\s*A15\b", ln))
    template = lines[last]
    cells = template.split("|")
    cells[1] = " A16 "
    if len(cells) > 2:
        cells[2] = " a row this control planted "
    lines.insert(last + 1, "|".join(cells))
    return "\n".join(lines) + "\n"


def _delete_a_row(row_id: str):
    def mutate(text: str) -> str:
        out, dropped = [], False
        for line in text.splitlines():
            if not dropped and re.match(rf"^\|\s*{re.escape(row_id)}\s*\|", line):
                dropped = True
                continue
            out.append(line)
        assert dropped, f"control is broken: no row {row_id!r} to delete"
        return "\n".join(out) + "\n"
    return mutate


def _make_state_unreadable(row_id: str, alien: str = "BLOCKED"):
    """Replace one row's state with a word the vocabulary does not hold.

    `BLOCKED` is chosen deliberately: it is NOT a dialect. A dialect is built
    only from the vocabulary's own atoms (`CANNOT-DELIVER` is), and the shipped
    counter REFUSES on one loudly. `BLOCKED` shares no atom, so `classify`
    returns no state and no dialect -- the row leaves the denominator in total
    silence, which is the class this leg exists to catch.
    """
    def mutate(text: str) -> str:
        out, done = [], False
        for line in text.splitlines():
            if not done and re.match(rf"^\|\s*{re.escape(row_id)}\s*\|", line):
                cells = line.split("|")
                for i, cell in enumerate(cells):
                    bare = cell.replace("`", "").replace("*", "").strip()
                    if bare.split(" ")[0] in (
                            "GAP", "CP", "CU", "CCD", "ER", "XR",
                            "EXCLUDED-RULED", "COVERED-PROVEN",
                            "COVERED-UNFIRED", "COVERED-CANNOT-DELIVER",
                            "MEASURED-ABSENT", "CANNOT-DELIVER"):
                        cells[i] = f" {alien} "
                        done = True
                        break
                line = "|".join(cells)
            out.append(line)
        assert done, f"control is broken: no state cell found on {row_id!r}"
        return "\n".join(out) + "\n"
    return mutate


def main() -> int:
    scratch = _copy_tree()
    print(f"scratch {scratch}")
    _assert_isolated(scratch)

    baseline_code, baseline_out = _run_guard(scratch, POPULATION)
    print(f"\n--- CONTROL, unmutated ---\nexit code {baseline_code} (want 0)")
    if baseline_code != 0:
        print(baseline_out[-2000:])
        print("FAIL  the guard is not green on an unmutated copy; nothing "
              "below would mean anything")
        return 1
    print("PASS  the guard is green on an unmutated copy")

    _assert_alien_is_not_a_dialect(scratch, "BLOCKED")

    results = [
        _demo("A  A ROW IS ADDED (a sixteenth row on network.md's admin table)",
              scratch, _slice(scratch, "network.md"), _add_admin_row,
              want=["ADDED    N A16", "POPULATION MOVED"],
              forbid=["DELETED  N A16"],
              # The planted row copies A15's cells, so it carries a perfectly
              # well-formed state. The cell-shaped guard has nothing to object
              # to, which is exactly why a row can enter the census unnoticed.
              neighbour_fires=False),
        _demo("B  A ROW IS DELETED (jobs.md J 1)",
              scratch, _slice(scratch, "jobs.md"), _delete_a_row("1"),
              want=["DELETED  J 1", "POPULATION MOVED"],
              forbid=["UNREADABLE J 1"],
              # A row that is gone offends no cell-shaped rule: there is no
              # cell left to inspect.
              neighbour_fires=False),
        _demo("C  A STATE IS CHANGED TO ONE OUTSIDE THE VOCABULARY (jobs.md J 1)",
              scratch, _slice(scratch, "jobs.md"),
              _make_state_unreadable("1"),
              # Case-exact on purpose. The first run of this control asked for
              # "still in the file" and the guard says "STILL IN THE FILE", so
              # demonstration C reported FAIL while the guard was behaving
              # perfectly. A control whose expectation is a paraphrase of the
              # message convicts the wrong file, which is worth one comment.
              want=["UNREADABLE J 1", "POPULATION MOVED",
                    "THE ROW IS STILL IN THE FILE"],
              forbid=["DELETED  J 1"],
              # THIS ONE THE NEIGHBOUR DOES CATCH, on a different ground: the
              # cell is now prose. Recorded rather than hidden. What it cannot
              # say is that the DENOMINATOR moved, nor that the row is still
              # present -- and telling "deleted" from "unreadable" is the only
              # thing this leg claims for itself.
              neighbour_fires=True),
    ]

    final_code, _ = _run_guard(scratch, POPULATION)
    print(f"\n--- CONTROL, restored ---\nexit code {final_code} (want 0)")
    clean = final_code == 0
    print(f"{'PASS' if clean else 'FAIL'}  the copy is byte-restored and the "
          f"guard is green again")

    shutil.rmtree(scratch, ignore_errors=True)
    ok = all(results) and clean
    print(f"\n{'ALL THREE DEMONSTRATIONS PASS' if ok else 'SOMETHING DID NOT BEHAVE AS STATED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
