"""READ THE DIRECTION OF A `J` ROW, SO THE SPLIT CHECK STOPS SKIPPING 19 BLOCKERS.

WHY THIS EXISTS. `scripts/_check_published_split.py` compares each blocker's
held R/W split against the ledger's published split, and it SKIPS any blocker
holding a `J` row. Its own docstring says why: *"`jobs.md` keys direction by
RANGE (`106-114`) and not by row id, so this script cannot read the direction of
a `J` row and SKIPS any blocker holding one."* Measured at `201b757` that is 19
of 88 blockers -- more than a fifth of the published splits are unwatched, and
`COMPANY-PAGE-SURFACE`, the largest PARTIAL in the map, is one of them.

THE RANGES ARE MACHINE-READABLE. `jobs.md` section 2 is a table
`| rows | gap | shape | R/W | REV |` whose first cell is a row-range spec
(`9-14`, `31-36, 41`, `85-86`) and whose fourth cell is the direction. This
reads that table and expands each range.

WHAT IT REFUSES TO DO, WHICH IS THE POINT. A range carrying a COMPOUND
direction -- `R + W`, `R (results) + W (the session)` -- says the BLOCK contains
both, never which row is which. Those rows are reported UNRESOLVED and are not
guessed, because a direction invented here would feed straight into a split
comparison and manufacture a disagreement or hide one. The count of unresolved
rows is printed, so a caller can see what the reading does not cover.

IT IS A REPORT, NOT A GATE, for the same reason the split check is: two
over-runs are ruled deliberate and a gate that fires on a ruled state teaches
people to bypass it.

CONTROLS, because a check that cannot fail certifies nothing:
  * `--control-blind` deletes the direction cell of one range and requires the
    report to move those rows into UNRESOLVED rather than keep a stale reading.
  * `--control-overrun` flips one held row's direction and requires the split
    comparison to name the blocker that then goes over.

    ./venv/Scripts/python.exe scripts/_check_jobs_range_directions.py
    ./venv/Scripts/python.exe scripts/_check_jobs_range_directions.py --control-blind
    ./venv/Scripts/python.exe scripts/_check_jobs_range_directions.py --control-overrun
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402
import _check_published_split as sp  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
JOBS = ROOT / "_audit" / "_census" / "jobs.md"

#: The section-2 table, located by its HEADER ROW and never by line offset --
#: the same rule `build_blocker_map` and the split check both follow, and for
#: the same measured reason: waves append to these files and every line-pinned
#: reading in this repository has gone stale at least once.
SECTION2_HEADER = "| rows | gap | shape | R/W | REV |"

#: A direction cell resolves a range only if it names exactly one direction.
#: Anything else is a statement about the BLOCK, not about a row.
#:
#: `RW` IS DELIBERATELY NOT ACCEPTED HERE, AND THE FIRST DRAFT OF THIS FILE
#: ACCEPTED IT. In the per-row census tables an `R/W` cell means THAT ROW both
#: reads and writes. In THIS table the cell describes a RANGE, so `R + W` means
#: the block contains reads and writes without saying which row is which --
#: `70-73` is "resume upload, list, delete, download" and its `R + W` is four
#: rows of mixed direction, not four rows that each do both. Mapping it to `RW`
#: put 5 phantom `RW` rows into `FILE-UPLOAD-UNSANCTIONED` and 7 into
#: `OPEN-TO-WORK-MODAL`, and both then reported OVER on a direction no row
#: carries. A direction invented here feeds straight into a split comparison,
#: so the compound cells resolve nothing and say so.
_SINGLE = {"R": "R", "W": "W"}


def _expand(spec: str) -> list[int]:
    """`31-36, 41` -> [31..36, 41]. Anything unparseable contributes nothing."""
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip().strip("`* ")
        m = re.fullmatch(r"(\d{1,3})\s*-\s*(\d{1,3})", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a <= b:
                out.extend(range(a, b + 1))
            continue
        if re.fullmatch(r"\d{1,3}", part):
            out.append(int(part))
    return out


def _direction(cell: str) -> str | None:
    """The one direction this cell names, or None when it names none or many."""
    c = cell.strip().strip("`* ")
    key = c.replace(" ", "").upper()
    if key in _SINGLE:
        return _SINGLE[key]
    return None


def jobs_directions(blind_range: str | None = None) -> tuple[dict[str, str], dict[str, str]]:
    """({`J n`: direction}, {`J n`: why-unresolved}) off jobs.md section 2."""
    lines = JOBS.read_text(encoding="utf-8", errors="replace").splitlines()
    resolved: dict[str, str] = {}
    unresolved: dict[str, str] = {}
    for row in bbm._table_after(lines, SECTION2_HEADER):
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        spec, dircell = cells[0], cells[3]
        if blind_range is not None and spec.strip() == blind_range:
            dircell = ""
        d = _direction(dircell)
        for n in _expand(spec):
            rid = f"J {n}"
            if d is None:
                unresolved.setdefault(rid, f"range {spec!r} direction cell {dircell!r}")
            else:
                resolved.setdefault(rid, d)
    for rid in list(resolved):
        unresolved.pop(rid, None)
    return resolved, unresolved


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control-blind", action="store_true",
                    help="blind one range's direction cell; its rows must become UNRESOLVED")
    ap.add_argument("--control-overrun", action="store_true",
                    help="flip one held row's direction; the report must name the over-run")
    args = ap.parse_args(argv)

    blind = "106-114" if args.control_blind else None
    jdirs, junres = jobs_directions(blind)

    gap, _cur, assign, _problems = bbm.build()
    published = sp.published_splits()
    dirs = dict(sp.row_directions())
    dirs.update(jdirs)

    frozen_j = [r for r in gap if r.startswith("J ")]
    print(f"frozen GAP rows in the jobs slice        {len(frozen_j)}")
    print(f"  direction READ off a section-2 range   "
          f"{sum(1 for r in frozen_j if r in jdirs)}")
    print(f"  UNRESOLVED (compound or absent cell)   "
          f"{sum(1 for r in frozen_j if r in junres)}")
    orphan = sorted((r for r in frozen_j if r not in jdirs and r not in junres),
                    key=lambda s: int(s.split()[1]))
    print(f"  named by no section-2 range at all     {len(orphan)}"
          f"{'  ' + ' '.join(orphan) if orphan else ''}")

    if args.control_blind:
        hit = [r for r in frozen_j if r in junres and junres[r].startswith("range '106-114'")]
        ok = len(hit) >= 8
        print(f"\ncontrol-blind: blinded range '106-114' -> "
              f"{len(hit)} of its frozen rows now UNRESOLVED -- "
              f"{'READING FOLLOWS THE CELL' if ok else 'STALE, BROKEN'}")
        return 0 if ok else 1

    held: dict[str, dict[str, int]] = {}
    for rid, (blocker, *_rest) in assign.items():
        k = dirs.get(rid, "?")
        held.setdefault(blocker, {"R": 0, "W": 0, "RW": 0, "?": 0})
        held[blocker][k] = held[blocker].get(k, 0) + 1

    #: Arrivals are read against the WIDENED direction map, not the narrow one,
    #: so a re-filed `J` row counts under its real direction here even though
    #: the sibling report can only score it `?`.
    incoming = sp._incoming(dirs)

    victim = None
    if args.control_overrun:
        # DELIBERATELY a blocker this report calls "within split" on the real
        # data. Injecting into one it ALREADY names (COMPANY-PAGE-SURFACE is
        # over on R) would pass whether or not the injection did anything --
        # the control would be measuring the baseline, not the instrument.
        victim = "SCHOOL-PAGE-SURFACE"
        held[victim]["W"] = published[victim]["W"] + 99

    print("\nblockers the shipped split check SKIPS, now readable")
    shown = still = 0
    over: list[str] = []
    causes: dict[str, str] = {}
    for b in sorted(published):
        h = held.get(b)
        if not h or not any(r.startswith("J ") for r, v in assign.items() if v[0] == b):
            continue
        shown += 1
        if h["?"]:
            still += 1
            print(f"  STILL BLIND  {b:30s} {h['?']} row(s) of unreadable direction")
            continue
        bad = [k for k in ("R", "W", "RW") if h[k] > published[b][k]]
        short = [k for k in ("R", "W", "RW") if h[k] < published[b][k]]
        if bad:
            over.append(b)
        tag = ("OVER on " + ",".join(bad)) if bad else "within split"
        print(f"  {tag:16s} {b:30s} "
              f"published R{published[b]['R']} W{published[b]['W']} RW{published[b]['RW']}"
              f"   held R{h['R']} W{h['W']} RW{h['RW']}"
              + (f"   short on {','.join(short)}" if short else ""))
        # THE CAUSE, IMPORTED FROM `_check_published_split` RATHER THAN
        # RE-DERIVED. ADDED 2026-09-20. This file exists to widen that report
        # to the blockers it skips, and it was widening the COVERAGE while
        # dropping the READING: `COMPANY-PAGE-SURFACE` is the third known
        # over-run and the only report that can see it printed the same
        # undifferentiated `OVER on R` the sibling had just stopped printing.
        # A discriminator that lives one import away from the report that
        # needs it is the defect register 24.1 is about, and leaving it here
        # while fixing it there would have been that defect twice.
        if bad:
            inc = incoming.get(b, {"R": 0, "W": 0, "RW": 0, "?": 0})
            own = {k: h[k] - inc.get(k, 0) for k in ("R", "W", "RW")}
            cause, why = sp.classify_overrun(published[b], h, own)
            causes[b] = cause
            print(f"      incoming R{inc['R']} W{inc['W']} RW{inc['RW']}   "
                  f"own R{own['R']} W{own['W']} RW{own['RW']}")
            print(f"      CAUSE {cause} -- {why}")
    print(f"\nblockers holding a J row      {shown}")
    print(f"  still blind after this read {still}")

    if args.control_overrun:
        # The assertion is on the REPORT, never on the injection. Checking that
        # the injected number is large would be a tautology and would certify
        # nothing -- the question is whether the printed table NAMES it.
        ok = victim in over
        print(f"\ncontrol-overrun: inflated {victim}'s held W -- "
              f"{'NAMED in the table above, the report can fail' if ok else 'NOT NAMED -- BROKEN'}")
        # AND WHETHER IT IS CLASSIFIED, ADDED 2026-09-20 WITH THE CAUSE LINE.
        # A cause printed beside every over-run and asserted by nothing is
        # decoration, and decoration in a report is read as a measurement. The
        # injection adds 99 held writes without touching the published count,
        # so the blocker now holds far more rows than it published and
        # OVER-COUNT is the only honest verdict. Stub the classifier, or lose
        # the incoming subtraction, and this line is what says so.
        got = causes.get(victim, "NOT CLASSIFIED")
        cok = got == "OVER-COUNT"
        print(f"control-overrun: cause for {victim} -- expected OVER-COUNT, "
              f"got {got} -- {'OK' if cok else 'WRONG'}")
        return 0 if (ok and cok) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
