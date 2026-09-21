"""Red proof: plant a wrong-row locator in the REAL file and show the guard red.

`tests/test_a_census_locator_names_its_row.py` plants its defects through the
library API. That proves the mechanism. It does not show a reader what the
guard SAYS when it convicts, and the pin in that module is EMPTY -- the whole
file is green on the live tree -- so a reader has never seen this guard fail.
A check nobody has seen fail is a check nobody can calibrate.

So this runs the REAL command-line entry point over a COPY of the real tree,
with one locator repointed at a real but different row, and prints exactly what
the terminal prints. Three plants, one per failing verdict that can be reached
from a hand-edited locator:

    NAMES-ANOTHER-ROW   `J 57` repointed at row 112 -- the 2026-09-21 defect
                        shape, a citation that resolves to the wrong thing
    LINE-NUMBER         `J 57` put back the way it was before the repair
    NO-SUCH-ROW         `J 57` pointed at a row label that does not exist

**NOTHING IS MUTATED IN THE TREE.** The four slices and the assignment file are
copied to a temp directory and the plant goes in the COPY, which is why this is
safe to run while other waves are writing `_audit/_census/`.

Run from the repository root::

    venv/Scripts/python.exe scripts/_check_census_locators_can_fail.py

Exit 0 means the unmutated control was GREEN and all three plants went RED with
the right verdict. Exit 1 names the plant that did not fire.
"""
from __future__ import annotations

import io
import contextlib
import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import check_census_locators_resolve as guard  # noqa: E402
import count_census_states as census  # noqa: E402

LIVE = HERE.parent
VICTIM = "J 57"


def _stage(work: pathlib.Path) -> pathlib.Path:
    (work / "_audit" / "_census").mkdir(parents=True, exist_ok=True)
    for name in census.SLICES.values():
        shutil.copy2(LIVE / "_audit" / "_census" / name,
                     work / "_audit" / "_census" / name)
    dest = work / guard.ASSIGNMENTS
    shutil.copy2(LIVE / guard.ASSIGNMENTS, dest)
    return dest


def _plant(path: pathlib.Path, locator: str) -> None:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split("\t")
        if len(fields) >= 5 and fields[1] == VICTIM:
            fields[4] = locator
            line = "\t".join(fields)
        out.append(line)
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def _run(work: pathlib.Path) -> tuple[int, str]:
    """The REAL `main()`, rooted on the copy. Its output is what a reader sees."""
    saved = guard.ROOT
    guard.ROOT = work
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = guard.main([])
    finally:
        guard.ROOT = saved
    return code, buf.getvalue()


PLANTS = (
    ("NAMES-ANOTHER-ROW", "112"),
    ("LINE-NUMBER", "L200"),
    ("NO-SUCH-ROW", "9999"),
)


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        tsv = _stage(work)

        code, text = _run(work)
        print("=" * 74)
        print("CONTROL -- nothing planted")
        print("=" * 74)
        print(text.rstrip())
        print("exit %d" % code)
        if code != 0:
            failures.append(
                "the UNMUTATED control is already red, so no plant below "
                "proves anything")

        for want, locator in PLANTS:
            _plant(tsv, locator)
            code, text = _run(work)
            print()
            print("=" * 74)
            print("PLANTED -- %s's locator rewritten to %r, expecting %s"
                  % (VICTIM, locator, want))
            print("=" * 74)
            print(text.rstrip())
            print("exit %d" % code)
            if code == 0 or want not in text:
                failures.append(
                    "planting %r on %s did not produce a %s finding. A check "
                    "that cannot fail certifies nothing."
                    % (locator, VICTIM, want))

    print()
    if failures:
        for f in failures:
            print("NOT PROVEN: %s" % f)
        return 1
    print("all three plants were convicted, and the control was green.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
