"""The messaging-and-content GAP rows, split by DIRECTION and by BLOCKER.

WHY THIS EXISTS. A wave asked to triage 83 GAP rows can write its integers into
an audit document, and then nobody can check them: a count in prose beside a
table it cannot read goes stale in silence, and ``readonly.py`` says so in its
own words. **This script is the triage.** The document quotes it.

IT IMPORTS THREE SHIPPED INSTRUMENTS AND REIMPLEMENTS NONE OF THEM:

* ``count_census_states`` -- the parse. Every cell, header and state spelling
  comes from there, so this script inherits its blind spots exactly rather than
  inventing new ones.
* ``enumerate_gap_rows`` -- which rows carry which state, slice-qualified.
* ``reader_closable_blockers.direction_of`` -- the R/W column reader, which is
  value-based because a positional one read a Help Center reference as a
  direction and reported every jobs row as a write.

Four waves on 2026-09-05 wrote a second copy of a shipped instrument and three
of the copies had a bug. The standing rule is to import.

THE BLOCKER COLUMN COMES FROM ``_audit/_census/blocker-map.tsv``, which is a
COMMITTED, DERIVED artefact with its own guard
(``tests/test_blocker_map_is_derived.py``). This script does not assign a
blocker to anything; it joins.

## WHAT THE THREE CONTROLS DO, AND WHY A CLEAN RUN WITHOUT THEM MEANS NOTHING

1. **The count control.** The shipped counter is re-run as a SUBPROCESS and its
   per-slice GAP total must equal the number of rows this script enumerated. A
   join that silently dropped rows would otherwise read as a tidy answer.
2. **The coverage control.** Every enumerated GAP row must appear in the
   blocker map. An unjoined row is reported by id, never skipped -- a blocker
   tally over 80 of 83 rows looks identical to one over 83.
3. **The negative control.** ``direction_of`` is shown REFUSING on a row with
   no direction cell and on one with two, using
   ``reader_closable_blockers.control_negative``. Without it, a run where every
   direction came back ``unknown`` would print a clean-looking table of zeros.

Any control that fails REFUSES THE WHOLE REPORT. A triage that cannot be
trusted to have read every row should not print a tally at all.

## A ROW RETURNED FROM AN EXCLUSION IS ITS OWN CLASS, NOT A HOLE IN THE MAP

The blocker map's spine is the 409 rows that were GAP at the 2026-09-03 freeze,
and it is not grown (the orchestrator's call, delegated, 2026-09-24). A row lane
R returned from EXCLUDED-RULED on 2026-09-23 that was NOT one of those 409 has
no map line, and never will. Such a row is not unjoined: its blocker is NAMED IN
ITS OWN CELL, after the marker ``RETURNED TO GAP ... BY LANE R ... BLOCKER,
NAMED:`` (``_audit/2026-09-23-exclusion-returns.md``). It is tallied under
:data:`RETURNED_CLASS`. **The coverage control still refuses** a row that is
absent from the map AND carries no such marker, so the class cannot absorb a
genuinely missing row.

USAGE:

    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py
    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py --slice M
    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py --ids
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import subprocess
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

import count_census_states as ccs  # noqa: E402
import enumerate_gap_rows as egr  # noqa: E402
import reader_closable_blockers as rcb  # noqa: E402

#: The slice this wave owns. A letter, as ``count_census_states.SLICES`` keys
#: them -- ``M`` is ``messaging-and-content.md``.
DEFAULT_SLICE = "M"

#: Direction tokens grouped for the headline. ``R+W`` is its own bucket
#: because a row with a read half and a write half is neither, and folding it
#: into either is how a triage over-states what a reader could close.
_READ = ("R",)
_WRITE = ("W",)
_BOTH = ("R+W",)

#: The census's convention for a row lane R returned from an exclusion: its
#: cell opens a note with this marker and names its blocker after it.
RETURNED_MARKER = re.compile(
    r"\*\*RETURNED TO GAP\b[^*]*\bBY LANE R\b.*?BLOCKER, NAMED:", re.S)

#: The class such a row is tallied under when the frozen blocker map has no
#: line for it. Not a blocker name: the blocker is in the row's own cell.
RETURNED_CLASS = "RETURNED-OUTSIDE-LEDGER"


def _gap_rows(letter: str):
    """Every GAP row of one slice, with its cells. Refuses on a dialect."""
    dialects: list[str] = []
    out = []
    for slice_letter, row_id, state, lineno, _prose in egr.rows(
        dialects=dialects
    ):
        if slice_letter != letter or state != "GAP":
            continue
        out.append((row_id, lineno))
    if dialects:
        raise SystemExit(
            "REFUSING: the census spells a state in a dialect the shipped "
            "vocabulary does not hold, so rows dropped out of this "
            "enumeration:\n  " + "\n  ".join(dialects)
        )
    return out


def _cells_by_row(letter: str) -> dict[str, list[str]]:
    """Row id -> its cells, for the direction read. Parsed by the shipped parser."""
    name = ccs.SLICES[letter]
    found: dict[str, list[str]] = {}
    for line in egr.slice_text(name, None).splitlines():
        if not line.startswith("|"):
            continue
        cells = ccs.cells(line)
        if len(cells) < 3 or not ccs.ROW.match(line):
            continue
        if cells[0].lower() in ccs.HEADERS:
            continue
        if cells[0] and set(cells[0]) <= set("-: "):
            continue
        found[cells[0]] = cells
    return found


def _control_count(letter: str, enumerated: int) -> str:
    """Re-run the shipped counter and compare. Returns '' or a failure line."""
    proc = subprocess.run(
        [sys.executable, str(_HERE / "count_census_states.py")],
        capture_output=True,
        text=True,
        cwd=str(_HERE.parent),
    )
    if proc.returncode != 0:
        return "the shipped counter exited %d" % proc.returncode
    name = ccs.SLICES[letter]
    for line in proc.stdout.splitlines():
        if line.startswith(name) and "GAP" in line:
            token = line.split("GAP")[1].strip().split()[0]
            if int(token) != enumerated:
                return (
                    "the shipped counter says GAP %s for %s; this script "
                    "enumerated %d" % (token, name, enumerated)
                )
            return ""
    return "the shipped counter printed no GAP line for %s" % name


def returned_outside_ledger(letter, rows, blockers, cells) -> set[str]:
    """Row ids absent from the blocker map whose own cell carries the
    returned-row marker, and so names its blocker. See the module docstring."""
    return {
        row_id
        for row_id, _ in rows
        if ("%s %s" % (letter, row_id)) not in blockers
        and RETURNED_MARKER.search(" | ".join(cells.get(row_id, [])))
    }


def unjoined_rows(letter, rows, blockers, returned=frozenset()) -> list[str]:
    """Row ids with no blocker assignment. CONTROL 2, as a callable.

    Extracted from :func:`main` so it can be SHOWN FAILING against a blocker
    map with a hole in it. A check that only ever runs over the real, complete
    map has never been observed to fail, and this repository counts that as
    uncertified. ``returned`` is :func:`returned_outside_ledger`'s set: those
    rows are classed, not missing.
    """
    return sorted(
        row_id
        for row_id, _ in rows
        if ("%s %s" % (letter, row_id)) not in blockers
        and row_id not in returned
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--slice", default=DEFAULT_SLICE)
    parser.add_argument(
        "--ids", action="store_true", help="print the row ids in each bucket"
    )
    args = parser.parse_args(argv)
    letter = args.slice

    rows = _gap_rows(letter)
    cells = _cells_by_row(letter)
    blockers = rcb.load_blockers()

    # ---- CONTROL 3: the direction reader must be shown refusing ----------
    negative = rcb.control_negative()
    if negative:
        print("REFUSING: the direction reader's negative control failed.")
        return 1

    # ---- CONTROL 1: the shipped counter agrees ---------------------------
    problem = _control_count(letter, len(rows))
    if problem:
        print("REFUSING: %s" % problem)
        return 1

    # ---- CONTROL 2: every row joins, or names its blocker in its cell -----
    returned = returned_outside_ledger(letter, rows, blockers, cells)
    unjoined = unjoined_rows(letter, rows, blockers, returned)
    if unjoined:
        print(
            "REFUSING: %d of %d GAP rows carry no blocker assignment: %s"
            % (len(unjoined), len(rows), " ".join(sorted(unjoined)))
        )
        return 1

    by_direction: dict[str, list[str]] = collections.defaultdict(list)
    by_blocker: dict[str, list[str]] = collections.defaultdict(list)
    cross: dict[tuple[str, str], int] = collections.Counter()

    for row_id, _lineno in rows:
        direction = rcb.direction_of(cells[row_id])
        blocker = (RETURNED_CLASS if row_id in returned
                   else blockers["%s %s" % (letter, row_id)])
        by_direction[direction].append(row_id)
        by_blocker[blocker].append(row_id)
        cross[(blocker, direction)] += 1

    print("slice                %s (%s)" % (letter, ccs.SLICES[letter]))
    print("GAP rows             %d" % len(rows))
    print("controls             counter agrees, all rows joined or "
          "classed, direction reader shown refusing")
    print("returned, off ledger %d   (%s: the blocker is named in the "
          "row's own cell)" % (len(returned), RETURNED_CLASS))
    print()
    print("BY DIRECTION, as the census's own R/W column states it")
    total = 0
    for direction in sorted(by_direction):
        ids = sorted(by_direction[direction])
        total += len(ids)
        print("  %-10s %3d" % (direction, len(ids)))
        if args.ids:
            print("      %s" % " ".join(ids))
    print("  %-10s %3d" % ("TOTAL", total))
    reads = sum(len(by_direction[d]) for d in _READ)
    writes = sum(len(by_direction[d]) for d in _WRITE)
    both = sum(len(by_direction[d]) for d in _BOTH)
    other = total - reads - writes - both
    print()
    print("  reads %d   writes %d   read-and-write %d   unreadable-cell %d"
          % (reads, writes, both, other))
    print()
    print("BY BLOCKER (from the committed blocker map, not assigned here)")
    for blocker in sorted(by_blocker, key=lambda b: (-len(by_blocker[b]), b)):
        ids = sorted(by_blocker[blocker])
        shape = " ".join(
            "%s%d" % (d, cross[(blocker, d)])
            for d in ("R", "W", "R+W")
            if cross[(blocker, d)]
        )
        print("  %-30s %3d  %s" % (blocker, len(ids), shape))
        if args.ids:
            print("      %s" % " ".join(ids))
    print()
    print(
        "DIRECTION IS THE CENSUS'S OWN COLUMN, NOT THIS SCRIPT'S JUDGEMENT. "
        "A write row is not buildable on a read-only server; a read row may "
        "still be blocked on an address, a ruling or a press. The blocker "
        "column says which."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
