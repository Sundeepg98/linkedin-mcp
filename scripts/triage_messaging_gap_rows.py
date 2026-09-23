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
   tally over 80 of 83 rows looks identical to one over 83. **One class of row
   is exempt, and it is derived, never listed:** the map enumerates the GAP
   rows of the FROZEN census (``build_blocker_map.FROZEN_REF``), so a row that
   entered GAP after that commit has no map line by construction. Those rows
   are found by reading the census AT the freeze from git -- never from the
   map, which would turn every hole in it into an exemption -- and printed by
   id in a bucket of their own. A row that was GAP at the freeze is never
   exempt. (Added 2026-09-24, when lane Y2 admitted the slice's first rows
   since the freeze; ``_audit/2026-09-24-lane-y2-admission.md``.)
3. **The negative control.** ``direction_of`` is shown REFUSING on a row with
   no direction cell and on one with two, using
   ``reader_closable_blockers.control_negative``. Without it, a run where every
   direction came back ``unknown`` would print a clean-looking table of zeros.

Any control that fails REFUSES THE WHOLE REPORT. A triage that cannot be
trusted to have read every row should not print a tally at all.

USAGE:

    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py
    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py --slice M
    ./venv/Scripts/python.exe scripts/triage_messaging_gap_rows.py --ids
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import subprocess
import sys

_HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

import build_blocker_map as bbm  # noqa: E402  (the map's own freeze ref)
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


def entered_since_freeze(letter: str, rows) -> list[str]:
    """Ids among ``rows`` that were NOT GAP when the blocker map was frozen.

    The map enumerates the GAP rows of the census at
    ``build_blocker_map.FROZEN_REF`` -- the set the ledger divided -- so a row
    that entered GAP later (admitted from what LinkedIn draws, or returned to
    GAP) has no map line and never will. Reporting it as UNJOINED would make
    CONTROL 2 red on every admission; dropping it would shrink the tally in
    silence. So it is exempt from the join and named, by id, in its own bucket.

    THE FROZEN SET IS READ FROM GIT, NEVER FROM THE MAP. The map is the thing
    being joined against; deriving "entered" from it would turn every hole in
    it into an exemption and leave CONTROL 2 unable to fail. An EMPTY frozen
    set would do the same from the other side -- every row today would read as
    entered -- so that REFUSES rather than answering.
    """
    dialects: list[str] = []
    frozen = {
        row_id
        for slice_letter, row_id, state, _lineno, _prose in egr.rows(
            bbm.FROZEN_REF, dialects
        )
        if slice_letter == letter and state == "GAP"
    }
    if not frozen:
        raise SystemExit(
            "REFUSING: the census at the blocker map's freeze (%s) holds no "
            "GAP row for slice %s, so every row today would read as entered "
            "since the freeze and the join control could not fail."
            % (bbm.FROZEN_REF, letter)
        )
    return sorted(row_id for row_id, _ in rows if row_id not in frozen)


def unjoined_rows(letter, rows, blockers, entered=()) -> list[str]:
    """Row ids with no blocker assignment. CONTROL 2, as a callable.

    Extracted from :func:`main` so it can be SHOWN FAILING against a blocker
    map with a hole in it. A check that only ever runs over the real, complete
    map has never been observed to fail, and this repository counts that as
    uncertified.

    ``entered`` is :func:`entered_since_freeze`'s answer -- rows the map
    cannot hold. They are exempt here and named by :func:`main`. A row that
    was GAP at the freeze is never in it, so a hole in the map is still named.
    """
    exempt = set(entered)
    return sorted(
        row_id
        for row_id, _ in rows
        if ("%s %s" % (letter, row_id)) not in blockers
        and row_id not in exempt
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

    # ---- CONTROL 2: every row joins, save those the map cannot hold ------
    entered = entered_since_freeze(letter, rows)
    unjoined = unjoined_rows(letter, rows, blockers, entered)
    if unjoined:
        print(
            "REFUSING: %d of %d GAP rows carry no blocker assignment: %s"
            % (len(unjoined), len(rows), " ".join(sorted(unjoined)))
        )
        return 1

    by_direction: dict[str, list[str]] = collections.defaultdict(list)
    by_blocker: dict[str, list[str]] = collections.defaultdict(list)
    cross: dict[tuple[str, str], int] = collections.Counter()

    # Not a blocker name: the bucket for rows the frozen map cannot hold. Each
    # of them names its blocker in its own census line.
    entered_bucket = "(entered GAP after %s)" % bbm.FROZEN_REF
    exempt = set(entered)
    for row_id, _lineno in rows:
        direction = rcb.direction_of(cells[row_id])
        if row_id in exempt:
            blocker = entered_bucket
        else:
            blocker = blockers["%s %s" % (letter, row_id)]
        by_direction[direction].append(row_id)
        by_blocker[blocker].append(row_id)
        cross[(blocker, direction)] += 1

    print("slice                %s (%s)" % (letter, ccs.SLICES[letter]))
    print("GAP rows             %d" % len(rows))
    print("controls             counter agrees, every row GAP at the map's "
          "freeze joined, direction reader shown refusing")
    print("entered since %s  %d -- GAP rows the frozen map cannot hold, "
          "named here rather than joined:" % (bbm.FROZEN_REF, len(entered)))
    print("      %s" % (" ".join(entered) or "(none)"))
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
    print("BY BLOCKER (from the committed blocker map, not assigned here; the "
          "rows it cannot hold are one bucket, each naming its blocker in its "
          "own census line)")
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
