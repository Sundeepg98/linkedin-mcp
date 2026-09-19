"""Enumerate the census rows behind `count_census_states.py`'s counts, BY ID.

WHY THIS EXISTS. `scripts/count_census_states.py` publishes how MANY rows carry
each state. It does not say WHICH. Every downstream artifact that divides those
rows -- above all `_audit/2026-09-03-linkedin-gap-blockers.md`, which split 409
GAP rows across 97 blockers -- has therefore been unauditable: the classifier
that produced that split was never committed, so a per-blocker count could not
be distinguished from a per-blocker guess. This script emits the ID SET so the
division can be checked against something.

IT IMPORTS THE SHIPPED COUNTER RATHER THAN REPARSING. `cells`, `state_of`,
`ROW`, `HEADERS`, `SLICES` and `CENSUS` all come from `count_census_states`.
Four waves reimplemented a shipped instrument on 2026-09-05 and three got a
broken one; the standing rule is IMPORT IT. The consequence is stated rather
than hidden: THIS SCRIPT INHERITS THAT PARSE'S BLIND SPOTS EXACTLY. A row whose
state cell is prose is invisible here for the same reason it is invisible there
(`N 132`), and `--unstated` in the shipped counter is still the only way to see
those. A shared parse is not a second opinion, and this file does not pretend
to be one.

ONE BEHAVIOUR IS REPLICATED, NOT IMPORTED, because it lives inside the shipped
counter's `main()` and has no seam: the network slice's admin-only table carries
no state column at all, and its section prose says all fifteen rows are GAP, so
`N A<digits>` is forced to GAP. The replication is guarded by --control, which
re-runs the shipped counter as a subprocess and fails if any per-slice count
disagrees. That check is a control on the replication and NOTHING MORE: it
cannot detect a defect the two share, because they share the parse by design.

    ./venv/Scripts/python.exe scripts/enumerate_gap_rows.py --control
    ./venv/Scripts/python.exe scripts/enumerate_gap_rows.py --ref 1c08e5f --state GAP

`--ref` reads the four slices out of a git object instead of the working tree,
which is how the frozen 15:53 row set behind the number 409 is recovered. That
matters because a per-blocker count that moved may have moved for two entirely
different reasons -- a row was re-costed, or a row left GAP -- and only the id
sets tell them apart.

IDS ARE EMITTED SLICE-QUALIFIED (`J 24`, `P B4`, `M M37`, `N 149`). The slices
reuse bare ids: `P C3` and `M C3` are different capabilities, as are `P M11`
and `M M11`. A bare id in this corpus is ambiguous and this script never emits
one.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs  # noqa: E402  (the shipped instrument)

#: Replicated from `count_census_states.main()`; see the module docstring. The
#: network slice's admin-only table has no state column and its section prose
#: covers all fifteen rows.
ADMIN_ONLY = re.compile(r"A\d+")


def slice_text(name: str, ref: str | None) -> str:
    """The slice's markdown, from the working tree or from a git object."""
    path = ccs.CENSUS / name
    if ref is None:
        return path.read_text(encoding="utf-8", errors="replace")
    rel = path.relative_to(pathlib.Path(__file__).resolve().parents[1])
    out = subprocess.run(
        ["git", "show", f"{ref}:{rel.as_posix()}"],
        cwd=str(pathlib.Path(__file__).resolve().parents[1]),
        capture_output=True, check=True,
    )
    return out.stdout.decode("utf-8", errors="replace")


def rows(ref: str | None = None):
    """Yield (letter, row_id, state, lineno, first_prose_cell) for every stated row."""
    for letter, name in ccs.SLICES.items():
        for lineno, line in enumerate(slice_text(name, ref).splitlines(), 1):
            if not line.startswith("|"):
                continue
            c = ccs.cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ccs.ROW.match(line) or c[0].lower() in ccs.HEADERS:
                continue
            st = ccs.state_of(c)
            if not st and letter == "N" and ADMIN_ONLY.fullmatch(c[0]):
                st = "GAP"
            if not st:
                continue
            yield letter, c[0], st, lineno, c[1]


def control(ref: str | None) -> int:
    """Re-run the shipped counter and fail on any per-slice disagreement."""
    if ref is not None:
        print("control: SKIPPED -- the shipped counter reads the working tree only")
        return 0
    root = pathlib.Path(__file__).resolve().parents[1]
    out = subprocess.run(
        [str(root / "venv" / "Scripts" / "python.exe"),
         str(root / "scripts" / "count_census_states.py")],
        cwd=str(root), capture_output=True, check=True,
    ).stdout.decode("utf-8", errors="replace")
    shipped = {}
    for line in out.splitlines():
        m = re.match(r"^(\S+\.md)\s+stated rows\s+(\d+)\s+GAP\s+(\d+)", line)
        if m:
            shipped[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    mine: dict[str, list[int]] = {n: [0, 0] for n in ccs.SLICES.values()}
    for letter, _rid, st, _ln, _t in rows(None):
        name = ccs.SLICES[letter]
        mine[name][0] += 1
        if st == "GAP":
            mine[name][1] += 1
    bad = 0
    for name in ccs.SLICES.values():
        got = tuple(mine[name])
        want = shipped.get(name)
        ok = got == want
        bad += 0 if ok else 1
        print(f"control {name:28s} enumerated rows/GAP {got}   shipped {want}   "
              f"{'MATCH' if ok else 'MISMATCH'}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=None, help="git ref to read the census from")
    ap.add_argument("--state", default="GAP", help="state to enumerate, or ALL")
    ap.add_argument("--control", action="store_true",
                    help="verify per-slice totals against the shipped counter")
    ap.add_argument("--count-only", action="store_true")
    args = ap.parse_args(argv)

    if args.control and control(args.ref):
        return 1

    n = 0
    per: dict[str, int] = {}
    for letter, rid, st, lineno, text in rows(args.ref):
        if args.state != "ALL" and st != args.state:
            continue
        n += 1
        per[letter] = per.get(letter, 0) + 1
        if not args.count_only:
            print(f"{letter} {rid}\t{st}\t{letter}\t{lineno}\t{text[:90]}")
    if args.count_only or args.control:
        for letter in ccs.SLICES:
            print(f"{letter} {args.state} {per.get(letter, 0)}")
        print(f"TOTAL {args.state} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
