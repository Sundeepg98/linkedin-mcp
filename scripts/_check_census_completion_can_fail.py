"""Show `census_completion.py --check` failing, and show it REFUSING.

A completion figure is the easiest thing in this repository to publish and the
hardest to keep true: it is quoted, it goes stale silently, and the tree that
would refute it is 592 KB of markdown nobody re-reads. So the instrument that
prints it only earns its entry if it can disagree with the tree. Three
demonstrations, and the third is a different KIND of failure from the first two:

  A  A ROW CHANGES STATE.   Move one row GAP -> COVERED-PROVEN. `--check` must
                            go red and must NAME every figure that moved --
                            not just the one, because a single state change
                            moves five of them at once and a reader who is told
                            about one will re-quote the other four.
  B  A ROW CHANGES DIRECTION. Move one still-GAP row W -> R. `--check` must go
                            red on the bucket split ALONE, with every headline
                            figure unmoved. This is the leg that proves the
                            decomposition is measured rather than decorative:
                            a report that only notices state changes would pass
                            here while its three buckets were wrong.
  C  A STATE BECOMES UNREADABLE. The instrument must REFUSE ENTIRELY rather
                            than print a smaller, tidier, wrong set of numbers.
                            A row with an unreadable state leaves numerator and
                            denominator together, so every percentage would
                            still look plausible -- which is exactly why
                            printing them would be the worst available
                            behaviour.

**C IS THE ONE WORTH THE FILE.** A and B prove the pins are connected to the
tree. C proves the instrument would rather say nothing than publish a figure
it cannot stand behind, and that is the property this repository keeps finding
it did not have.

IT NEVER TOUCHES THE LIVE TREE -- copy, ASSERT the copy is what resolves, plant
ONE mutation, run, restore, finish on a clean control run. See the preamble of
`_audit/INSTRUMENTS.md` for why "confirm" is not good enough here.

    python scripts/_check_census_completion_can_fail.py
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]


def _copy_tree() -> pathlib.Path:
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="census-completion-control-"))
    shutil.copytree(REPO / "scripts", scratch / "scripts",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (scratch / "_audit").mkdir()
    shutil.copytree(REPO / "_audit" / "_census", scratch / "_audit" / "_census")
    # The PIN is the instrument's only witness independent of the census parse,
    # so a copy without it would have the instrument refusing for the wrong
    # reason in every demonstration.
    (scratch / "tests").mkdir()
    shutil.copy2(REPO / "tests" / "census_row_pin.json",
                 scratch / "tests" / "census_row_pin.json")
    return scratch


def _assert_isolated(scratch: pathlib.Path) -> None:
    probe = (
        "import sys, pathlib;"
        "sys.path.insert(0, str(pathlib.Path(sys.argv[1]) / 'scripts'));"
        "import count_census_states as C;"
        "print(C.CENSUS)"
    )
    out = subprocess.run([sys.executable, "-c", probe, str(scratch)],
                         capture_output=True, text=True, check=True)
    census = pathlib.Path(out.stdout.strip())
    assert census.is_relative_to(scratch), (
        f"ISOLATION FAILED: census resolves to {census}, not under {scratch}. "
        f"Refusing to plant a mutation.")
    assert not census.is_relative_to(REPO), (
        f"ISOLATION FAILED: census {census} sits under the live repo {REPO}.")
    print(f"isolation asserted: census={census}")


def _run(scratch: pathlib.Path):
    proc = subprocess.run(
        [sys.executable, "scripts/census_completion.py", "--check"],
        cwd=str(scratch), capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def _slice(scratch: pathlib.Path, name: str) -> pathlib.Path:
    return scratch / "_audit" / "_census" / name


def _retarget(frm: str, to: str, also: str | None = None):
    """Rewrite the FIRST row carrying a `frm` cell -- target chosen at runtime.

    THE TARGET IS FOUND, NOT NAMED, AND THAT IS DELIBERATE. The first draft of
    this control hardcoded `N 33` and died on its first run with *"no 'GAP'
    cell on '33'"* -- a sibling wave had banked that row to COVERED-UNFIRED
    hours earlier. A control naming a row by id rots every time the census
    moves, which is continuously, and rots into a FALSE ALARM that the next
    reader has to diagnose.

    `also` narrows the search to rows that ALSO carry that cell value, which is
    how demonstration B finds a row that is both still-GAP and write-direction
    without naming one.

    It ASSERTS that a target was found and PRINTS which row it chose, so the
    demonstration stays legible and a census with no such row left fails loudly
    instead of passing vacuously.
    """
    def mutate(text: str) -> str:
        out, chosen = [], None
        for line in text.splitlines():
            if chosen is None and line.startswith("|"):
                cells = line.split("|")
                bare = [c.replace("`", "").replace("*", "").strip()
                        for c in cells]
                hit = next((i for i, b in enumerate(bare)
                            if b.split(" ")[0] == frm), None)
                ok_also = also is None or any(b == also for b in bare[1:])
                if hit is not None and ok_also and len(cells) > 3:
                    cells[hit] = f" {to} "
                    chosen = bare[1] if len(bare) > 1 else "?"
                    line = "|".join(cells)
            out.append(line)
        assert chosen is not None, (
            f"control is broken, or the census no longer has such a row: "
            f"found no row carrying {frm!r}"
            + (f" together with {also!r}" if also else ""))
        print(f"    target chosen at runtime: row {chosen!r} "
              f"({frm} -> {to}{', also ' + also if also else ''})")
        return "\n".join(out) + "\n"
    return mutate


def _demo(label: str, path: pathlib.Path, scratch: pathlib.Path, mutate,
          want: list[str], forbid: list[str], want_exit_nonzero: bool = True):
    original = path.read_bytes()
    try:
        path.write_text(mutate(original.decode("utf-8")), encoding="utf-8")
        code, out = _run(scratch)
        missing = [w for w in want if w not in out]
        present = [f for f in forbid if f in out]
        ok = ((code != 0) == want_exit_nonzero) and not missing and not present
        print(f"\n--- {label} ---")
        print(f"exit code {code} (want {'non-zero' if want_exit_nonzero else '0'})")
        if missing:
            print(f"MISSING from the output: {missing}")
        if present:
            print(f"WRONGLY PRESENT: {present}")
        keep = False
        for line in out.splitlines():
            if "MOVED" in line or "REFUSING" in line:
                keep = True
            if keep and line.strip():
                print(f"    {line.rstrip()[:160]}")
        print(f"{'PASS' if ok else 'FAIL'}  {label}")
        return ok
    finally:
        path.write_bytes(original)


def main() -> int:
    scratch = _copy_tree()
    print(f"scratch {scratch}")
    _assert_isolated(scratch)

    code, out = _run(scratch)
    print(f"\n--- CONTROL, unmutated ---\nexit code {code} (want 0)")
    if code != 0:
        print(out[-1500:])
        print("FAIL  the instrument does not agree with its own pins on an "
              "unmutated copy; nothing below would mean anything")
        return 1
    print("PASS  every pinned figure matches on an unmutated copy")

    results = [
        _demo("A  A ROW CHANGES STATE (network.md, GAP -> COVERED-PROVEN)",
              _slice(scratch, "network.md"), scratch,
              _retarget("GAP", "COVERED-PROVEN"),
              # ONE state change moves FIVE pinned figures at once. Naming
              # only the first would leave four stale numbers looking healthy,
              # so all four of the headline ones are demanded by name.
              # `gap_read` is deliberately NOT demanded: whether the direction
              # counter that moves is the read one or the write one depends on
              # the row the search lands on, and an expectation that depends on
              # that is a coin-flip dressed as an assertion. The FIRST draft of
              # this control demanded `gap_read` and failed on a W row.
              want=["PINNED FIGURE(S) MOVED", "adjudicated", "delivered_broad",
                    "delivered_strict", "gap "],
              forbid=["stated_rows ", "REFUSING TO REPORT"]),
        _demo("B  A ROW CHANGES DIRECTION (network.md, a still-GAP W row -> R)",
              _slice(scratch, "network.md"), scratch,
              _retarget("W", "R", also="GAP"),
              # The bucket split moves and NOTHING else does. If `adjudicated`
              # appeared here the instrument would be reporting a state change
              # that did not happen.
              want=["PINNED FIGURE(S) MOVED", "gap_read", "gap_write"],
              forbid=["adjudicated", "delivered_broad", "stated_rows"]),
        _demo("C  A STATE BECOMES UNREADABLE (network.md, GAP -> BLOCKED)",
              _slice(scratch, "network.md"), scratch,
              _retarget("GAP", "BLOCKED"),
              # It must REFUSE, not publish 703 tidy-looking rows.
              want=["REFUSING TO REPORT"],
              forbid=["ADJUDICATED", "DELIVERED, broad"]),
    ]

    final_code, _ = _run(scratch)
    print(f"\n--- CONTROL, restored ---\nexit code {final_code} (want 0)")
    clean = final_code == 0
    print(f"{'PASS' if clean else 'FAIL'}  byte-restored and green again")

    shutil.rmtree(scratch, ignore_errors=True)
    ok = all(results) and clean
    print(f"\n{'ALL THREE DEMONSTRATIONS PASS' if ok else 'SOMETHING DID NOT BEHAVE AS STATED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
