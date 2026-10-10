"""Show `scripts/check_next_step.py` FAILING on planted defects, before trusting it.

Each demonstration copies the committed ledger and queue into a temporary
directory, plants ONE defect in the copy, runs the checker over the copy, and
requires the problem it reports to name the defect. A control run over the
unplanted copies must come back GREEN first, so every red below is the planted
defect's and nothing else's.

    python scripts/_check_next_step_can_fail.py

The demonstrations, and the message each must produce:

    A  a GAP row's line deleted        "with NO line -- nobody gave it a next step"
    B  a line doubled                  "2 lines, want exactly one"
    C  a source phrase that is in no   "phrase does not resolve"
       file (a dangling source)
    D  a census-row source that is     "is not a census row"
       no row
    E  a CAPTURE id with no queue line "has no line in the capture queue"
    F  a queue line listing a row the  "is not a census row"
       census does not hold
    G  a BUILD path neither tracked    "neither a tracked fixture nor PLANNED"
       nor planned

Nothing here reaches LinkedIn, an account, or a browser.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_next_step as cns  # noqa: E402


def _lines(path: pathlib.Path) -> list[str]:
    return path.read_text(encoding="ascii").splitlines()


def _write(path: pathlib.Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def _first(lines: list[str], test) -> int:
    return next(i for i, ln in enumerate(lines) if i and test(ln.split("\t")))


def plant(kind: str, table: pathlib.Path, queue: pathlib.Path) -> str:
    """Plant defect `kind` in the copies; return the substring that must appear."""
    t, q = _lines(table), _lines(queue)
    if kind == "A":
        i = _first(t, lambda c: c[0] == "N 37")
        del t[i]
        _write(table, t)
        return "N 37: a GAP row today with NO line -- nobody gave it a next step"
    if kind == "B":
        i = _first(t, lambda c: c[0] == "P S1")
        t.insert(i, t[i])
        _write(table, t)
        return "P S1: 2 lines, want exactly one"
    if kind == "C":
        i = _first(t, lambda c: c[0] == "J 82")
        cells = t[i].split("\t")
        cells[6] = "_audit/_census/jobs-directions.tsv::a phrase planted by the control and in no file"
        t[i] = "\t".join(cells)
        _write(table, t)
        return "J 82: phrase does not resolve"
    if kind == "D":
        i = _first(t, lambda c: c[0] == "N 169")
        cells = t[i].split("\t")
        cells[6] = "N 9999"
        t[i] = "\t".join(cells)
        _write(table, t)
        return "N 169: source N 9999 is not a census row"
    if kind == "E":
        i = _first(t, lambda c: c[0] == "P K8")
        cells = t[i].split("\t")
        cells[4] = "CAPTURE:a-surface-planted-by-the-control"
        t[i] = "\t".join(cells)
        _write(table, t)
        return "P K8: CAPTURE:a-surface-planted-by-the-control has no line in the capture queue"
    if kind == "F":
        i = _first(q, lambda c: c[1] == "in-me-profile")
        cells = q[i].split("\t")
        cells[12] = cells[12] + ", N 9999"
        cells[10] = str(int(cells[10]) + 1)
        q[i] = "\t".join(cells)
        _write(queue, q)
        return "queue in-me-profile: N 9999 is not a census row"
    if kind == "G":
        i = _first(t, lambda c: c[0] == "N 104")
        cells = t[i].split("\t")
        cells[4] = "BUILD:tests/fixtures/planted/no-such-capture.html"
        t[i] = "\t".join(cells)
        _write(table, t)
        return "N 104: BUILD:tests/fixtures/planted/no-such-capture.html is neither a tracked fixture nor PLANNED"
    raise ValueError(kind)


DEMONSTRATIONS = ("A", "B", "C", "D", "E", "F", "G")


def run(kind: str | None) -> tuple[list[str], str]:
    """(problems, expected substring or '') for one demonstration, or the control."""
    with tempfile.TemporaryDirectory() as tmp:
        table = pathlib.Path(tmp) / "next-step.tsv"
        queue = pathlib.Path(tmp) / "capture-queue.tsv"
        shutil.copyfile(cns.TABLE, table)
        shutil.copyfile(cns.QUEUE, queue)
        expected = plant(kind, table, queue) if kind else ""
        _rows, _q, problems, _nc = cns.check(table, queue)
    return problems, expected


def main() -> int:
    problems, _ = run(None)
    if problems:
        print("CONTROL IS RED -- no demonstration below would be attributable:")
        for p in problems:
            print("  " + p)
        return 1
    print("control: the unplanted copies are GREEN")
    failed = 0
    for kind in DEMONSTRATIONS:
        problems, expected = run(kind)
        hit = [p for p in problems if expected in p]
        verdict = "CAUGHT" if hit else "MISSED"
        failed += not hit
        print(f"{kind}  {verdict}  {expected}")
        for p in problems:
            print(f"     reported: {p}")
    if failed:
        print(f"\n{failed} planted defect(s) MISSED")
        return 1
    print("\nevery planted defect was caught by name")
    return 0


if __name__ == "__main__":
    sys.exit(main())
