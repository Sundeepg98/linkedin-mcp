"""Build the row -> blocker map from committed sources, and diff it against the
ledger's published per-blocker counts.

THE PROBLEM THIS ANSWERS. `_audit/2026-09-03-linkedin-gap-blockers.md` divided
409 census GAP rows across 97 named blockers and published ONLY THE COUNTS. The
classifier that produced the division was never committed; `git log -S` across
all history finds it nowhere. So every per-blocker number in this repository has
been unauditable, and when a later wave measured a blocker at 35 rather than 32,
or 13 rather than 12, nobody could tell a RE-COST from a MISCOUNT.

WHAT THIS PRODUCES. `_audit/_census/blocker-map.tsv`: one line per GAP row of
the frozen census, carrying the blocker it is assigned to, the CLASS of evidence
behind that assignment, and the committed source. Rows no committed source names
are emitted as `UNASSIGNED`, which is the honest majority and the headline
number -- it bounds how much of the ledger's division was ever recoverable.

THE SPINE IS THE FROZEN ROW SET, NOT TODAY'S. The map enumerates the 409 GAP
rows as of `1c08e5f` (the census commit, 2026-09-03 15:53), because that is the
set the ledger divided and the only set its counts can be checked against. Every
row also carries its CURRENT state, so today's 370 view is a filter on the same
file rather than a second artifact that could drift from it. Without both, a
per-blocker disagreement has two indistinguishable causes: a row was re-costed,
or a row left GAP entirely.

ROW ENUMERATION IS NOT DONE HERE. It is imported from `enumerate_gap_rows`,
which imports `count_census_states`, the shipped counter. This file adds no
parse of its own and inherits that parse's blind spots exactly -- a row whose
state cell is prose is invisible to all three.

ASSERTIONS, because a map that cannot fail certifies nothing:
  * every evidence id must resolve to a real census row       -> else FAIL
  * every evidence id must have been GAP at the frozen commit -> else FAIL
  * no row may carry two blockers (the ledger's own rule is
    one blocker per row, the earliest binding constraint)     -> else FAIL
  * assigned + unassigned must equal the frozen GAP total     -> else FAIL

    ./venv/Scripts/python.exe scripts/build_blocker_map.py --write
    ./venv/Scripts/python.exe scripts/build_blocker_map.py --check
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import enumerate_gap_rows as egr  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN_REF = "1c08e5f"
EVIDENCE = ROOT / "_audit" / "_census" / "blocker-assignments.tsv"
MAP_OUT = ROOT / "_audit" / "_census" / "blocker-map.tsv"
LEDGER = ROOT / "_audit" / "2026-09-03-linkedin-gap-blockers.md"


def ledger_counts() -> dict[str, int]:
    """The ledger's published per-blocker row counts, parsed from its own tables.

    Never retyped: the 88-row ranked table and the 9-row cost-0 table are read
    out of the document, and the caller asserts they total 97 blockers and 409
    rows before anything is compared against them.
    """
    text = LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    counts: dict[str, int] = {}
    for line in text[140:311]:
        m = re.match(r"^\|\s*\d+\s*\|\s*`([A-Z0-9-]+)`\s*\|\s*(\d+)\s*\|", line)
        if m:
            counts[m.group(1)] = int(m.group(2))
            continue
        m = re.match(r"^\|\s*`([A-Z0-9-]+)`\s*\|\s*(\d+)\s*\|", line)
        if m:
            counts[m.group(1)] = int(m.group(2))
    return counts


def evidence() -> list[tuple[str, str, str, str, str, str]]:
    out = []
    for raw in EVIDENCE.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw.strip() or raw.startswith(">"):
            continue
        parts = raw.split("\t")
        if parts[0] == "blocker":
            continue
        parts += [""] * (6 - len(parts))
        out.append(tuple(p.strip() for p in parts[:6]))  # type: ignore[arg-type]
    return out


def build():
    frozen = {f"{L} {r}": (st, txt) for L, r, st, _ln, txt in egr.rows(FROZEN_REF)}
    current = {f"{L} {r}": st for L, r, st, _ln, _t in egr.rows(None)}
    gap = {k: v for k, v in frozen.items() if v[0] == "GAP"}

    problems: list[str] = []
    assign: dict[str, tuple[str, str, str, str, str]] = {}
    for blocker, rid, klass, source, locator, note in evidence():
        if rid not in frozen:
            problems.append(f"UNRESOLVED id {rid!r} for {blocker} ({source} {locator})")
            continue
        if rid not in gap:
            problems.append(f"NOT-GAP-AT-FREEZE {rid} is {frozen[rid][0]} for {blocker}")
            continue
        if rid in assign and assign[rid][0] != blocker:
            problems.append(f"DOUBLE-ASSIGNED {rid}: {assign[rid][0]} and {blocker}")
            continue
        assign[rid] = (blocker, klass, source, locator, note)
    return gap, current, assign, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="write the map file")
    ap.add_argument("--check", action="store_true", help="assert only, write nothing")
    args = ap.parse_args(argv)

    gap, current, assign, problems = build()
    published = ledger_counts()

    fail = 0
    print(f"frozen GAP rows at {FROZEN_REF}     {len(gap)}")
    print(f"ledger blockers parsed              {len(published)}  "
          f"rows {sum(published.values())}")
    if len(published) != 97 or sum(published.values()) != 409:
        print("  FAIL: the ledger's own tables no longer total 97 blockers / 409 rows")
        fail = 1
    if len(gap) != 409:
        print("  FAIL: the frozen census no longer enumerates 409 GAP rows")
        fail = 1
    for p in problems:
        print(f"  FAIL: {p}")
        fail = 1

    assigned = len(assign)
    unassigned = len(gap) - assigned
    print(f"assigned from committed sources     {assigned}")
    print(f"UNASSIGNED                          {unassigned}")
    if assigned + unassigned != len(gap):
        print("  FAIL: assigned + unassigned does not close on the frozen total")
        fail = 1

    by_class: dict[str, int] = {}
    for _b, klass, *_ in assign.values():
        by_class[klass] = by_class.get(klass, 0) + 1
    print("\nassignments by evidence class")
    for k in sorted(by_class):
        print(f"  {k:26s} {by_class[k]:4d}")

    recount: dict[str, int] = {}
    for blocker, *_ in assign.values():
        recount[blocker] = recount.get(blocker, 0) + 1
    print(f"\nblockers with at least one recovered row  {len(recount)} of 97")
    print(f"blockers with NO recovered row            {97 - len(recount)}")

    print("\nper-blocker recount vs the ledger's published count")
    print(f"  {'blocker':32s} {'pub':>4s} {'map':>4s} {'delta':>6s}  verdict")
    complete = partial = 0
    for b in sorted(published, key=lambda x: (-published[x], x)):
        got = recount.get(b, 0)
        if got == 0:
            continue
        d = got - published[b]
        if d == 0:
            verdict = "COMPLETE -- every published row recovered"
            complete += 1
        else:
            verdict = f"PARTIAL -- {-d} row(s) named by no committed source"
            partial += 1
        print(f"  {b:32s} {published[b]:4d} {got:4d} {d:+6d}  {verdict}")
        if d > 0:
            print("     FAIL: the map assigns MORE rows than the ledger published")
            fail = 1
    print(f"\n  complete {complete}   partial {partial}   "
          f"absent {97 - len(recount)}")

    left = sum(1 for k in gap if current.get(k, "ROW-GONE") != "GAP")
    print(f"\nrows that have LEFT GAP since the freeze   {left}")
    print(f"rows still GAP today                       {len(gap) - left}")
    entered = [k for k, v in current.items() if v == "GAP" and k not in gap]
    print(f"rows that ENTERED GAP since the freeze     {len(entered)}"
          f"  {' '.join(sorted(entered))}")
    print(f"today's GAP total, derived                 "
          f"{len(gap) - left + len(entered)}")

    if args.write and not fail:
        lines = ["row_id\tblocker\tevidence_class\tsource\tlocator\t"
                 "state_at_freeze\tstate_today\tcapability\tnote"]
        for rid in sorted(gap, key=lambda s: (s[0], len(s), s)):
            b, klass, source, locator, note = assign.get(
                rid, ("UNASSIGNED", "UNASSIGNED", "-", "-",
                      "no committed source names this row against any blocker"))
            txt = gap[rid][1].replace("\t", " ").replace("|", "/")[:110]
            lines.append(f"{rid}\t{b}\t{klass}\t{source}\t{locator}\t"
                         f"GAP\t{current.get(rid, 'ROW-GONE')}\t{txt}\t{note}")
        MAP_OUT.write_text("\n".join(lines) + "\n", encoding="ascii", errors="replace")
        print(f"\nwrote {MAP_OUT.relative_to(ROOT).as_posix()}  "
              f"{len(lines) - 1} data lines")
    elif args.write:
        print("\nNOT WRITTEN -- assertions failed above")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
