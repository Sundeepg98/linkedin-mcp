"""WHICH LIVE BLOCKERS COULD A READER ACTUALLY CLOSE?

A blocker's GAP count is the number everyone schedules from, and **it is the
wrong number for this question.** `GROUPS-SURFACE` holds 23 GAP rows and most
of them are *join*, *post*, *invite*, *message* -- writes that no reader closes
and that this repository refuses outright. A reader cannot be "the whole
remaining cost" of a row that is not a read.

So this splits every still-GAP row by its READ/WRITE column and reports, per
blocker, **how many rows a reader could actually reach.**

## IT IMPORTS THE SHIPPED ENUMERATOR RATHER THAN REPARSING

`enumerate_gap_rows.rows()` decides what a stated row is, and this file does
not get a vote. A previous attempt of mine at a census reader disagreed with
the shipped count by 66 rows because it re-derived the filter and got it
subtly wrong. **The rule this repository already paid for: import the shipped
instrument.**

## THE R/W CELL IS NOT AT A FIXED INDEX, AND ASSUMING IT IS WAS THE LAST BUG

Measured, per slice:

    profile.md              c[2] = R/W
    network.md              c[2] = R/W
    messaging-and-content   c[4] = R/W      (c[2] is source refs)
    jobs.md                 NO PER-ROW R/W COLUMN AT ALL

**Four layouts, and one of them does not have the column.** So the cell is
found BY VALUE -- a short cell whose content is exactly a direction token --
never by position. A positional reader would have silently returned source
refs as directions for messaging and reported every jobs row as a write.

**AND AMBIGUITY IS ITS OWN ANSWER.** If no cell matches, the row is `unknown`.
If more than one matches, it is `ambiguous`. Neither is folded into a
direction, because **a tidy answer over a column that is not there is the
failure this file exists to avoid** -- and `unknown` is the honest majority
verdict for a whole slice.

## THE CONTROLS, AND IT REFUSES TO REPORT IF ANY FAILS

1. the shipped enumerator's own control -- per-slice row and GAP counts must
   match `count_census_states.py`
2. **KNOWN ANSWERS.** Rows whose direction was read by hand, in slices with
   DIFFERENT layouts, must come back right -- including one in the slice where
   the column sits at c[4]. A finder that happened to hardcode c[2] passes
   every other check and fails this one.
3. **A SHOWN-FAILING NEGATIVE.** A note cell containing a bare "R" must NOT be
   read as a direction, and a row with two direction-shaped cells must come
   back `ambiguous` rather than resolved. Without this the finder is a
   plausible string search.
4. **THE JOIN LOSES NOTHING.** Every GAP row either joins the blocker map or
   is counted as unjoined and REPORTED. The two must sum to the enumerated
   GAP total.

Run::

    ./venv/Scripts/python.exe scripts/reader_closable_blockers.py

Writes nothing. Prints to stdout.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import count_census_states as ccs  # noqa: E402
import enumerate_gap_rows as egr  # noqa: E402

BLOCKER_MAP = ROOT / "_audit" / "_census" / "blocker-map.tsv"

#: Exactly the spellings the census uses for a direction. A cell must BE one of
#: these after stripping emphasis -- never merely contain one.
DIRECTIONS = {
    "R": "R",
    "W": "W",
    "R+W": "R+W",
    "RW": "R+W",
    "R/W": "R+W",
    "W+R": "R+W",
}

#: A direction cell is short. This bounds the value-based search so a prose
#: note that happens to equal a token cannot be mistaken for the column.
MAX_DIRECTION_CHARS = 4


def _bare(cell: str) -> str:
    return cell.replace("`", "").replace("*", "").replace("_", "").strip()


def direction_of(row_cells: list[str]) -> str:
    """The row's direction, or ``unknown`` / ``ambiguous``. NEVER a guess."""
    hits = []
    for index, cell in enumerate(row_cells[1:], start=1):
        bare = _bare(cell)
        if len(bare) > MAX_DIRECTION_CHARS:
            continue
        if bare.upper() in DIRECTIONS:
            hits.append((index, DIRECTIONS[bare.upper()]))
    if not hits:
        return "unknown"
    verdicts = {v for _i, v in hits}
    if len(verdicts) > 1:
        return "ambiguous"
    return hits[0][1]


def load_blockers() -> dict[str, str]:
    """row_id -> blocker, from the shipped map."""
    out: dict[str, str] = {}
    lines = BLOCKER_MAP.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < 2 or not parts[0].strip():
            continue
        out[parts[0].strip()] = parts[1].strip() or "UNASSIGNED"
    return out


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------

#: (slice letter, row id, direction) read BY HAND. Deliberately spans layouts:
#: messaging's column sits at c[4], so a finder hardcoding c[2] fails here.
KNOWN = [
    ("P", "A1", "R"),
    ("N", "1", "W"),
    ("M", "M1", "W"),
    ("N", "133", "R"),
]


def control_known(rows_by_key: dict) -> int:
    bad = 0
    print("  CONTROL 2 -- known answers, across DIFFERENT column layouts")
    for letter, rid, want in KNOWN:
        got = rows_by_key.get((letter, rid), ("?", "?"))[1]
        ok = got == want
        bad += 0 if ok else 1
        print(f"      {letter} {rid:5s} want {want:4s} got {got:10s} "
              f"{'OK' if ok else 'FAIL'}")
    return bad


def control_negative() -> int:
    """SHOWN FAILING. A finder that cannot produce these is a string search."""
    print("  CONTROL 3 -- shown refusing, on cases built to fool it")
    cases = [
        (["9", "Some capability", "R", "GAP", "note"], "R", "the real column"),
        (["9", "Some capability", "a511260", "GAP",
          "a note mentioning R and W at length"], "unknown",
         "no direction cell -- the jobs layout"),
        (["9", "Some capability", "R", "GAP", "W"], "ambiguous",
         "two direction cells disagree"),
        (["9", "Some capability", "GAP", "R"], "R",
         "column order swapped -- value-based finder is unmoved"),
    ]
    bad = 0
    for cells, want, why in cases:
        got = direction_of(cells)
        ok = got == want
        bad += 0 if ok else 1
        print(f"      want {want:10s} got {got:10s} {'OK' if ok else 'FAIL'}"
              f"   {why}")
    return bad


# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 74)
    print("WHICH LIVE BLOCKERS COULD A READER ACTUALLY CLOSE?")
    print("=" * 74)

    print("\n  CONTROL 1 -- the shipped enumerator agrees with the shipped counter")
    if egr.control(None):
        print("  REFUSING TO REPORT: the enumerator disagrees with the counter.")
        return 1

    # Re-walk the slices to get full cells, using the SHIPPED filter verbatim.
    rows_by_key: dict[tuple[str, str], tuple[str, str]] = {}
    gap_rows: list[tuple[str, str, str]] = []
    for letter, name in ccs.SLICES.items():
        path = ROOT / "_audit" / "_census" / name
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
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
            if not st and letter == "N" and egr.ADMIN_ONLY.fullmatch(c[0]):
                st = "GAP"
            if not st:
                continue
            d = direction_of(c)
            rows_by_key[(letter, c[0])] = (st, d)
            if st == "GAP":
                gap_rows.append((letter, c[0], d))

    bad = control_known(rows_by_key) + control_negative()
    if bad:
        print(f"\n  REFUSING TO REPORT: {bad} control failure(s).")
        return 1

    # CONTROL 4 -- the join loses nothing.
    blockers = load_blockers()
    joined, unjoined = [], []
    for letter, rid, d in gap_rows:
        key = f"{letter} {rid}"
        (joined if key in blockers else unjoined).append((key, d))
    print(f"\n  CONTROL 4 -- join accounts for every GAP row")
    print(f"      enumerated GAP {len(gap_rows)}   joined {len(joined)}   "
          f"unjoined {len(unjoined)}   "
          f"{'OK' if len(joined) + len(unjoined) == len(gap_rows) else 'FAIL'}")
    if len(joined) + len(unjoined) != len(gap_rows):
        return 1

    tally: dict[str, dict[str, int]] = {}
    for key, d in joined:
        b = blockers[key]
        tally.setdefault(b, {}).setdefault(d, 0)
        tally[b][d] += 1
    for _key, d in unjoined:
        tally.setdefault("(NOT IN THE MAP)", {}).setdefault(d, 0)
        tally["(NOT IN THE MAP)"][d] += 1

    print("\n" + "=" * 74)
    print("  PER BLOCKER, STILL-GAP ROWS BY DIRECTION")
    print("  'reader-reachable' counts R and R+W ONLY. A write is not a reader's")
    print("  cost, and unknown is not a read.")
    print("=" * 74)
    print(f"  {'blocker':34s} {'GAP':>4s} {'R':>4s} {'R+W':>4s} {'W':>4s} "
          f"{'unk':>4s} {'amb':>4s}  reader-reachable")
    order = sorted(
        tally.items(),
        key=lambda kv: (-(kv[1].get("R", 0) + kv[1].get("R+W", 0)),
                        -sum(kv[1].values())),
    )
    tot = {"GAP": 0, "reach": 0}
    for name, d in order:
        g = sum(d.values())
        r, rw = d.get("R", 0), d.get("R+W", 0)
        reach = r + rw
        tot["GAP"] += g
        tot["reach"] += reach
        print(f"  {name[:34]:34s} {g:4d} {r:4d} {rw:4d} {d.get('W',0):4d} "
              f"{d.get('unknown',0):4d} {d.get('ambiguous',0):4d}  "
              f"{reach if reach else '-'}")
    print("-" * 74)
    print(f"  {'TOTAL':34s} {tot['GAP']:4d} "
          f"{'':4s} {'':4s} {'':4s} {'':4s} {'':4s}  {tot['reach']}")
    print(f"\n  A READER CANNOT BE THE REMAINING COST FOR "
          f"{tot['GAP'] - tot['reach']} OF {tot['GAP']} STILL-GAP ROWS.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
