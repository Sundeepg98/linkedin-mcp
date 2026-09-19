"""Does the blocker map agree with the ledger's published R/W SPLIT?

WHY THIS EXISTS, AND WHY IT IS A REPORT RATHER THAN A GATE.
`build_blocker_map.py` asserts on per-blocker COUNTS and on nothing else. That
leaves a whole class of disagreement unwatched: the ledger publishes an R/W
split for 88 of its 97 blockers, and a blocker can be UNDER on its total while
OVER on one direction -- in which case the count assertion is silent by
construction.

THE CLASS IS NOT THEORETICAL AND THE REASON IS STRUCTURAL. A row RE-FILED from
one blocker to another is COUNT-NEUTRAL across the pair, so no count assertion
anywhere can see it; but it MOVES THE SPLIT of both. `SEARCH-RESULTS-SURFACE`'s
own assignment note says so in writing -- *"the split is not claimed for the
post-freeze set ... That is what a re-file does"*. So the split is the only
signal that distinguishes the two things a PARTIAL blocker can mean:

    a published row was LOST, nobody can say which        -> a real hole
    a published row was RE-FILED OUT and this map HAS it  -> not a hole at all

Measured 2026-09-19 on `424fe66`, this reports 2 blockers over-published on a
direction, both COMPLETE on their counts and therefore invisible to the shipped
builder. A third (`COMPANY-PAGE-SURFACE`, 14R held against 13R published) is
NOT reported here and the limitation is stated rather than hidden: `jobs.md`
keys direction by RANGE (`106-114`) and not by row id, so this script cannot
read the direction of a `J` row and SKIPS any blocker holding one. It reports
how many it skipped for that reason.

IT IS DELIBERATELY NOT AN ASSERTION. Two of the three known over-runs are
documented and were ruled deliberate, so a red gate here would fail CI on work
somebody decided. The rule this supports is narrower: a NEW over-run must be
argued. Promote to an assertion only once the known three are adjudicated.

CONTROL, because a check that cannot fail certifies nothing: `--control`
injects a synthetic over-run into the tally and requires the report to name it.

    ./venv/Scripts/python.exe scripts/_check_published_split.py
    ./venv/Scripts/python.exe scripts/_check_published_split.py --control
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
CENSUS = ROOT / "_audit" / "_census"

#: 0-based index of the R/W cell in each slice's row table. `jobs.md` has none
#: -- see the module docstring.
SLICE_DIR_COL = {
    "M": ("messaging-and-content.md", 4),
    "N": ("network.md", 2),
    "P": ("profile.md", 2),
}
ROW_ID = re.compile(r"[A-Z]{0,2}\d{1,3}")
DIR_CELLS = {"R", "W", "R+W", "RW", "R/W"}
RANKED_HEADER = "| # | blocker | rows | R/W | boundary | ruling | cost |"


def _norm(d: str) -> str:
    return "RW" if d in ("R+W", "RW", "R/W") else d


def row_directions() -> dict[str, str]:
    """{slice-qualified row id: 'R' | 'W' | 'RW'} read off the census tables."""
    out: dict[str, str] = {}
    for letter, (name, col) in SLICE_DIR_COL.items():
        text = (CENSUS / name).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) <= col:
                continue
            rid = cells[0].strip("`* ")
            if not ROW_ID.fullmatch(rid):
                continue
            d = cells[col].strip("`* ")
            if d in DIR_CELLS:
                out.setdefault(letter + " " + rid, _norm(d))
    return out


def published_splits() -> dict[str, dict[str, int]]:
    """The ledger's per-blocker R/W split, parsed from its ranked table.

    Located by HEADER ROW for the same reason `build_blocker_map` does it that
    way: another wave appending to the ledger slides every table down, and a
    reading pinned to a line offset is the defect that already fired once.
    """
    lines = bbm.LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    out: dict[str, dict[str, int]] = {}
    for row in bbm._table_after(lines, RANKED_HEADER):
        m = re.match(r"^\|\s*\d+\s*\|\s*`([A-Z0-9-]+)`\s*\|\s*\d+\s*\|([^|]*)\|", row)
        if not m:
            continue
        spec = {"R": 0, "W": 0, "RW": 0}
        for n, kind in re.findall(r"(\d*)\s*(RW|R\+W|R|W)", m.group(2)):
            spec[_norm(kind)] += int(n) if n else 1
        if any(spec.values()):
            out[m.group(1)] = spec
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control", action="store_true",
                    help="inject a synthetic over-run and require it be named")
    args = ap.parse_args(argv)

    dirs = row_directions()
    _gap, _cur, assign, _problems = bbm.build()
    published = published_splits()

    held: dict[str, dict[str, int]] = {}
    for rid, (blocker, *_rest) in assign.items():
        k = dirs.get(rid, "?")
        held.setdefault(blocker, {"R": 0, "W": 0, "RW": 0, "?": 0})
        held[blocker][k] = held[blocker].get(k, 0) + 1

    if args.control:
        victim = sorted(published)[0]
        held.setdefault(victim, {"R": 0, "W": 0, "RW": 0, "?": 0})
        held[victim]["R"] = published[victim]["R"] + 99
        held[victim]["?"] = 0

    print(f"blockers with a published split   {len(published)}")
    over: list[str] = []
    skipped = 0
    for b in sorted(published):
        h = held.get(b)
        if not h:
            continue
        if h["?"]:
            skipped += 1
            continue
        bad = [k for k in ("R", "W", "RW") if h[k] > published[b][k]]
        if not bad:
            continue
        over.append(b)
        print(f"  OVER on {','.join(bad):<3s}  {b:30s} "
              f"published R{published[b]['R']} W{published[b]['W']} "
              f"RW{published[b]['RW']}   "
              f"held R{h['R']} W{h['W']} RW{h['RW']}")
    print(f"blockers OVER on some direction   {len(over)}")
    print(f"blockers SKIPPED (a held row's direction is unreadable -- the "
          f"jobs-slice limitation in the docstring)   {skipped}")

    if args.control:
        victim = sorted(published)[0]
        ok = victim in over
        print(f"\ncontrol: injected over-run on {victim} -- "
              f"{'NAMED, the report can fail' if ok else 'NOT NAMED -- BROKEN'}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
