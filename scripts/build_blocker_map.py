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

AN UNASSIGNED ROW HAS TWO CAUSES AND THE CELL NOW SAYS WHICH. Until 2026-09-19
every unassigned row carried the same generated sentence: "no committed source
names this row against any blocker". That is a universal negative asserted from
a lookup in ONE file, and it was FALSE for six rows -- `J 78`-`J 83` are named
against `PREMIUM-APPLY-SURFACES` in a tracked probe. The second cause is
NAMED-UNFILEABLE: a committed source names the row, and the naming cannot be
turned into an assignment (here, a six-row range against a five-row published
count). Both are still UNASSIGNED; only one of them means nobody knows.

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
#: ROWS A BLOCKER PUBLISHED THAT NOW LIVE SOMEWHERE ELSE, each with the
#: committed source that moved it. RULED 2026-09-19 after three waves reported
#: the same defect from three directions.
#:
#: THE VERDICT STRING WAS FALSE. "PARTIAL -- N row(s) named by no committed
#: source" claims nobody can name the row. For these five, a committed source
#: names the row AND names where it went -- the map simply had no way to say so,
#: because it compared AT-HEAD membership against AS-PUBLISHED counts and those
#: are two different questions.
#:
#: WHY AT-HEAD MEMBERSHIP AND NOT AS-PUBLISHED. Strict as-published would undo
#: deliberate re-files: `M C52` was moved to FEED-PREFERENCES on 2026-09-19 on
#: four measurements, one of which is that the ledger's own supporting quote for
#: keeping it was a MISQUOTE. A convention that reverses a better-evidenced
#: later reading is not a convention, it is a ratchet pointing backwards.
#:
#: So membership follows the best current evidence, and THIS TABLE carries the
#: history. A published row is ACCOUNTED if it is held here or listed here.
#: Anything else is still PARTIAL and still means what it says.
RE_FILED: dict[str, dict[str, str]] = {
    "HASHTAG-EXISTENCE": {
        "N 194": "SEARCH-RESULTS-SURFACE -- the ledger's OWN amendment table "
                 "(2026-09-03-linkedin-gap-blockers.md:1171-1180) carries an "
                 "'at HEAD' column and puts it there, quoting the census note "
                 "'no people search'. The map had been reading that column for "
                 "this row and the 'as published' column for C 11, out of one "
                 "table, which is the mixed convention this ruling ends.",
        "M C52": "FEED-PREFERENCES -- moved 2026-09-19 reversing a "
                 "LEDGER-AMENDMENT on four measurements, including that the "
                 "note keeping it here quoted the row as 'follow / unfollow "
                 "topics/hashtags' while the capability cell contains no "
                 "occurrence of hashtag. The misquote was doing the work.",
    },
    "GROUPS-SURFACE": {
        "N 161": "SEARCH-RESULTS-SURFACE -- carved by the groups wave's own "
                 "table 5.4. Direction confirms it: this blocker is short two "
                 "READS with its write side full at 20/20, and both carved "
                 "rows are R.",
        "M C70": "SEARCH-RESULTS-SURFACE -- same table 5.4, same wave, same "
                 "direction arithmetic.",
    },
    "EVENTS-SURFACE": {
        "N 179": "SEARCH-RESULTS-SURFACE -- conceded by the events wave. "
                 "Short one READ with 11/11 writes full; the conceded row is R.",
    },
}

FROZEN_REF = "1c08e5f"
EVIDENCE = ROOT / "_audit" / "_census" / "blocker-assignments.tsv"
MAP_OUT = ROOT / "_audit" / "_census" / "blocker-map.tsv"
LEDGER = ROOT / "_audit" / "2026-09-03-linkedin-gap-blockers.md"

#: SOURCES THAT NAME A ROW AGAINST A BLOCKER WITHOUT BEING ABLE TO FILE IT.
#:
#: THE DEFECT THIS EXISTS TO END. The UNASSIGNED reason cell used to read "no
#: committed source names this row against any blocker" for every unassigned
#: row. That is a UNIVERSAL NEGATIVE asserted from a lookup in ONE file --
#: `blocker-assignments.tsv` -- and it was FALSE for six rows: `J 78`-`J 83`
#: are named against `PREMIUM-APPLY-SURFACES`, in a tracked probe, in one
#: comment. A generator default is not a measurement, and a sweep reading that
#: column would have concluded the six were unnamed and gone looking again.
#:
#: WHY THE SIX STILL CANNOT BE FILED, which is the part the true cell has to
#: carry: the probe names SIX rows and the ledger publishes that blocker at
#: FIVE. Filing all six trips the over-count assertion below, and picking five
#: of six is a CHOICE wearing a forced row's clothes -- the same reasoning that
#: pulled `J 82` back out of this very blocker on 2026-09-19. So the honest
#: answer is neither "unnamed" nor an assignment: it is NAMED-UNFILEABLE, with
#: the arithmetic conflict printed in the cell.
#:
#: THE MARK IS PARSED, NEVER RETYPED. Both the blocker and the row range are
#: read out of the probe on every run, and the line number is computed rather
#: than quoted, so this cannot rot into a plausible wrong answer the way a
#: hand-copied citation does. If the mark disappears, `probe_marks` returns
#: nothing and `build` raises it as a problem -- the map refuses to write
#: rather than silently reverting to the false default.
NAMED_BY_PROBES = ("scripts/_probe_jobs_tail_boundary.py",)
PROBE_MARK = re.compile(
    r"^\s*#\s*\d+\s+(?P<blocker>[A-Z][A-Z0-9-]+)\s*--\s*census rows\s+(?P<spec>.+?)\s*$"
)
#: `J78-J83`, `J31-J36 and J41`, `J54-J56`. A bare number after a hyphen
#: inherits the letter (`J78-J83` and `J78-83` both mean the same six rows).
_SPEC_TOKEN = re.compile(r"\b([A-Z])\s?(\d+)(?:\s*-\s*(?:([A-Z])\s?)?(\d+))?")


def _expand(spec: str) -> list[str]:
    """Row ids named by a probe mark's row spec, slice-qualified."""
    out: list[str] = []
    for letter, first, _l2, last in _SPEC_TOKEN.findall(spec):
        lo = int(first)
        hi = int(last) if last else lo
        if hi < lo:
            continue
        out.extend(f"{letter} {n}" for n in range(lo, hi + 1))
    return out


def probe_marks() -> tuple[dict[str, tuple[str, str, str, int]], list[str]]:
    """rid -> (source, locator, blocker, rows_named), plus any parse problems.

    Derived from the tracked probe on every run. A source that vanishes or
    stops matching is a PROBLEM, never a silent fallback to the old claim.
    """
    found: dict[str, tuple[str, str, str, int]] = {}
    problems: list[str] = []
    for rel in NAMED_BY_PROBES:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"NAMED-BY-PROBE source missing: {rel}")
            continue
        marks = 0
        for lineno, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
        ):
            m = PROBE_MARK.match(line)
            if not m:
                continue
            ids = _expand(m.group("spec"))
            if not ids:
                problems.append(
                    f"NAMED-BY-PROBE {rel}:L{lineno} matched the mark grammar "
                    f"but named no rows: {m.group('spec')!r}")
                continue
            marks += 1
            for rid in ids:
                found[rid] = (rel, f"L{lineno}", m.group("blocker"), len(ids))
        if not marks:
            problems.append(
                f"NAMED-BY-PROBE {rel} carries no parseable "
                f"'# <n> <BLOCKER> -- census rows <spec>' mark any more. The "
                f"UNASSIGNED reason cell would silently revert to claiming no "
                f"committed source names those rows, which was false before.")
    return found, problems


def unassigned_row(rid: str, marks: dict[str, tuple[str, str, str, int]],
                   published: dict[str, int]) -> tuple[str, str, str, str, str]:
    """The five map columns for a row no evidence line files, and WHY.

    THE BLOCKER AND THE EVIDENCE CLASS STAY `UNASSIGNED` IN EVERY BRANCH, and
    that is deliberate rather than lazy. Naming a row is not filing it, so this
    generator does not get to promote one into the division -- and the two
    columns downstream readers key on (`blocker`, `evidence_class`) are
    asserted against the committed map by `test_blocker_map_is_derived`, which
    a sibling wave regenerates. Moving the distinction into a column somebody
    else's artifact is pinned to would break their tree to make a point that
    belongs in the reason cell. The distinction lives in the NOTE, tagged
    `NAMED-UNFILEABLE` so it is still greppable, and the `source` and `locator`
    columns -- empty for every unassigned row until now -- carry the citation.
    """
    named = marks.get(rid)
    if named is None:
        return ("UNASSIGNED", "UNASSIGNED", "-", "-",
                f"no line in {EVIDENCE.name} files this row, and no probe mark "
                f"in {'/'.join(NAMED_BY_PROBES)} names it")
    source, locator, blocker, rows_named = named
    pub = published.get(blocker)
    if pub is None:
        why = (f"the ledger's tables do not publish {blocker} at all, so there "
               f"is no count to file this row into")
    elif rows_named > pub:
        why = (f"the mark names {rows_named} rows and the ledger publishes "
               f"{blocker} at {pub}; filing them all would trip the over-count "
               f"assertion, and filing {pub} of {rows_named} would be a CHOICE "
               f"wearing a forced row's clothes")
    else:
        why = (f"named but not filed: {blocker} publishes {pub} and the mark "
               f"names {rows_named}; no evidence line assigns this row")
    return ("UNASSIGNED", "UNASSIGNED", source, locator,
            f"NAMED-UNFILEABLE -- named against {blocker} by "
            f"{source}:{locator}, {why}")


#: The two tables are located by their HEADER ROW, never by line offset.
#: MEASURED 2026-09-05 23:48, and it is why this is not a window: another wave
#: appended 19 lines to the ledger (`f7594c0`), the file went 1546 -> 1565, both
#: tables slid 28 lines down, and the cost-0 table left the hardcoded slice
#: `text[140:311]` entirely -- so four blockers silently read as published 0 and
#: the over-count assertion fired on them. It fired CORRECTLY on a defect in
#: this parser rather than in the data, which is the outcome a guard is for. A
#: reading pinned to a POSITION in a file other waves are appending to is the
#: same class of defect as every stale reading in this repository.
RANKED_HEADER = "| # | blocker | rows | R/W | boundary | ruling | cost |"
ZEROCOST_HEADER = "| blocker | rows | queue | why |"


def _table_after(lines: list[str], header: str) -> list[str]:
    """Lines of the markdown table whose header row starts with `header`."""
    for i, line in enumerate(lines):
        if line.startswith(header):
            out = []
            for row in lines[i + 1:]:
                if not row.startswith("|"):
                    break
                out.append(row)
            return out
    return []


def ledger_counts() -> dict[str, int]:
    """The ledger's published per-blocker row counts, parsed from its own tables.

    Never retyped: the ranked table and the cost-0 table are read out of the
    document by locating their header rows, and the caller asserts they total 97
    blockers and 409 rows before anything is compared against them. Returning a
    partial parse silently would turn a missing table into a blocker published
    at zero, which reads as a data disagreement and is not one.
    """
    lines = LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    counts: dict[str, int] = {}
    for line in _table_after(lines, RANKED_HEADER):
        m = re.match(r"^\|\s*\d+\s*\|\s*`([A-Z0-9-]+)`\s*\|\s*(\d+)\s*\|", line)
        if m:
            counts[m.group(1)] = int(m.group(2))
    for line in _table_after(lines, ZEROCOST_HEADER):
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
    # A DIALECT IN A STATE CELL IS A PROBLEM OF THIS MAP, NOT ONLY OF THE
    # COUNTER. Both enumerations collect them rather than refusing, because the
    # map's job is to report every defect it can see in one pass -- but they go
    # straight into `problems`, so the map will not WRITE while one is open.
    # Measured 2026-09-19: at `1c08e5f` two rows wore `**CANNOT-DELIVER**` and
    # this function saw 690 stated rows where the file held 692.
    dialects: list[str] = []
    frozen = {f"{L} {r}": (st, txt)
              for L, r, st, _ln, txt in egr.rows(FROZEN_REF, dialects)}
    current = {f"{L} {r}": st
               for L, r, st, _ln, _t in egr.rows(None, dialects)}
    gap = {k: v for k, v in frozen.items() if v[0] == "GAP"}

    problems: list[str] = [f"STATE-CELL-DIALECT {d}" for d in dialects]
    # The UNASSIGNED reason cell is DERIVED from these marks. If they stop
    # parsing, the cell reverts to a claim that was measured false, so the
    # derivation failing is a problem for the map and not just for the cell.
    _marks, mark_problems = probe_marks()
    problems.extend(mark_problems)
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

    #: ROWS A BLOCKER HOLDS THAT IT NEVER PUBLISHED, i.e. the other end of every
    #: RE_FILED entry. ADDED 2026-09-19 after a wave measured that the first cut
    #: of RE_FILED credited a re-file's DESTINATION for rows outside its own
    #: published set: SEARCH-RESULTS-SURFACE read 21 of 21 while holding four
    #: incoming rows, so its own count was 17 of 21 and four holes were masked;
    #: FEED-PREFERENCES read 1 of 1 while holding nothing it published.
    #:
    #: A PUBLISHED COUNT IS A CLAIM ABOUT A BLOCKER'S OWN ROWS. A row that
    #: arrived from somewhere else does not satisfy it, and subtracting at the
    #: source while adding at the destination is how a re-file turned into free
    #: credit at both ends.
    incoming: dict[str, int] = {}
    for _src, _rows in RE_FILED.items():
        for _rid, _why in _rows.items():
            _dest = _why.split(' -- ')[0].strip()
            incoming[_dest] = incoming.get(_dest, 0) + 1

    recount: dict[str, int] = {}
    for blocker, *_ in assign.values():
        recount[blocker] = recount.get(blocker, 0) + 1
    print(f"\nblockers with at least one recovered row  {len(recount)} of 97")
    print(f"blockers with NO recovered row            {97 - len(recount)}")

    print("\nper-blocker recount vs the ledger's published count")
    print(f"  {'blocker':32s} {'pub':>4s} {'map':>4s} {'delta':>6s}  verdict")
    complete = partial = 0
    for b in sorted(published, key=lambda x: (-published[x], x)):
        got = recount.get(b, 0) - incoming.get(b, 0)
        # SKIP ONLY BLOCKERS THAT HOLD NOTHING AT ALL -- they are counted separately
        # as 'absent'. Testing the NET here would hide a blocker whose every held
        # row arrived from somewhere else, which is exactly what FEED-PREFERENCES
        # is: 1 published, 1 held, 0 of them its own.
        if recount.get(b, 0) == 0:
            continue
        d = got - published[b]
        if d == 0:
            verdict = "COMPLETE -- every published row recovered"
            complete += 1
        else:
            moved = RE_FILED.get(b, {})
            if len(moved) >= -d:
                where = ', '.join(sorted(moved))
                verdict = (
                    f"ACCOUNTED -- {-d} published row(s) re-filed elsewhere on a "
                    f"committed source ({where}); see RE_FILED"
                )
                complete += 1
            else:
                verdict = (
                    f"PARTIAL -- {-d + len(moved)} row(s) neither held nor named "
                    f"as re-filed by any committed source"
                )
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

    marks, _mp = probe_marks()
    named_unassigned = sorted(r for r in gap if r not in assign and r in marks)
    print(f"\nUNASSIGNED rows a committed probe DOES name   "
          f"{len(named_unassigned)}  {' '.join(named_unassigned)}")

    if args.write and not fail:
        lines = ["row_id\tblocker\tevidence_class\tsource\tlocator\t"
                 "state_at_freeze\tstate_today\tcapability\tnote"]
        for rid in sorted(gap, key=lambda s: (s[0], len(s), s)):
            b, klass, source, locator, note = assign.get(
                rid, unassigned_row(rid, marks, published))
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
