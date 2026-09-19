"""Which blockers are ALREADY EMPTY, and which cannot be known to be.

THE PROBLEM. `_audit/2026-09-03-linkedin-gap-blockers.md` section 3 publishes a
per-blocker row count, a cost and a queue for 97 blockers. **Those numbers are
dated 2026-09-03 and rows have moved since.** A wave briefed off that table
arrives at a closed door: measured 2026-09-19, two of seven blockers in one
assignment had left GAP entirely before the wave began, and nothing in the
table said so.

WHAT THIS DERIVES, per blocker:

    published      the ledger's own count, parsed from its own tables
    recovered      rows a COMMITTED source names against this blocker
    live GAP       of the recovered rows, how many are STILL GAP today
    verdict        EMPTY-CERTAIN / EMPTY-UNCERTIFIABLE / LIVE / UNLOCATABLE

**THE VERDICT IS GATED ON RECOVERY, AND THAT IS THE WHOLE POINT.** Only 134 of
409 frozen GAP rows are named against a blocker by any committed source. For a
blocker whose recovery is PARTIAL, "every row I can find has left GAP" is NOT
"the blocker is empty" -- the rows nobody can locate could be anywhere. Saying
so is the honest output and collapsing the two is the error this file refuses
to make.

    EMPTY-CERTAIN         recovered == published AND zero recovered rows are
                          still GAP. Every row the ledger claims is accounted
                          for and every one has left. Safe to close.
    EMPTY-UNCERTIFIABLE   zero recovered rows are still GAP, but recovered <
                          published. Suggestive, NOT closeable: the unlocated
                          remainder is unmeasured, not absent.
    LIVE                  at least one recovered row is still GAP.
    UNLOCATABLE           no committed source names any row against it. The
                          published count cannot be checked at all.

IT REPARSES NOTHING. `build_blocker_map` supplies the frozen row set, today's
per-row state and the assignments; it in turn imports `enumerate_gap_rows`,
which imports `count_census_states`, the shipped counter. Four waves
reimplemented a shipped instrument on 2026-09-05 and three got a broken one.
THE CONSEQUENCE IS INHERITED AND STATED: a row whose state cell is prose is
invisible to all four of us for the same reason.

=============================================================================
THE CONTROLS
=============================================================================

**1. CROSS-INSTRUMENT, and it is the one that matters.** Today's GAP total
derived here must equal the number the SHIPPED COUNTER prints when run as a
SUBPROCESS. Two instruments, one of them not imported by this file, reaching
the same integer. If they disagree, every per-blocker number below is void and
this file says so instead of printing a table.

**2. ARITHMETIC THAT MUST CLOSE.** recovered + unassigned == frozen GAP total;
blockers parsed == 97; published rows == 409. A partial parse otherwise reads
as a blocker published at zero, which looks like a data disagreement and is
not one.

**3. A MUST-BE-ABSENT BLOCKER.** A name no ledger table contains. A joiner
that finds it is matching its own structure.

Run::

    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py --control
    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py
    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py --tsv
"""
from __future__ import annotations

import collections
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_blocker_map as bbm  # noqa: E402

ROOT = HERE.parent
COUNTER = HERE / "count_census_states.py"

#: A blocker name no ledger table contains, in the ledger's own spelling shape.
ABSENT_BLOCKER = "ZQXJVBNM-NOT-A-BLOCKER"

#: The ledger publishes 97 blockers over 409 rows. Asserted, never assumed.
EXPECTED_BLOCKERS = 97
EXPECTED_ROWS = 409

RANKED_ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*`([A-Z0-9-]+)`\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|"
    r"\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|"
    r"\s*([^|]*?)\s*\|"
)
ZEROCOST_ROW = re.compile(
    r"^\|\s*`([A-Z0-9-]+)`\s*\|\s*(\d+)\s*\|\s*([^|]*?)\s*\|"
)


def ledger_detail() -> dict[str, dict]:
    """Full section-3 columns, read out of the ledger's own tables.

    Uses ``build_blocker_map``'s table locator rather than a second scan, so a
    change to the ledger's headings breaks both together instead of silently
    desynchronising them.
    """
    lines = bbm.LEDGER.read_text(encoding="utf-8", errors="replace").splitlines()
    out: dict[str, dict] = {}
    for line in bbm._table_after(lines, bbm.RANKED_HEADER):
        m = RANKED_ROW.match(line)
        if m:
            out[m.group(2)] = {
                "rank": int(m.group(1)),
                "published": int(m.group(3)),
                "rw": m.group(4),
                "boundary": m.group(5),
                "ruling": m.group(6),
                "cost": int(m.group(7)),
                "queue": m.group(9),
                "table": "ranked",
            }
    for line in bbm._table_after(lines, bbm.ZEROCOST_HEADER):
        m = ZEROCOST_ROW.match(line)
        if m and m.group(1) not in out:
            out[m.group(1)] = {
                "rank": None,
                "published": int(m.group(2)),
                "rw": "",
                "boundary": "",
                "ruling": "",
                "cost": 0,
                "queue": m.group(3),
                "table": "zero-cost",
            }
    return out


def shipped_counter_gap() -> int | None:
    """The GAP total from the SHIPPED counter, run as a SUBPROCESS.

    Deliberately not imported. An imported module shares this process's parse;
    a subprocess is a second opinion in the only sense that matters here.
    """
    exe = sys.executable
    try:
        proc = subprocess.run(
            [exe, str(COUNTER)], capture_output=True, text=True, timeout=600
        )
    except Exception as error:  # noqa: BLE001
        print(f"  counter subprocess failed: {type(error).__name__}")
        return None
    tail = proc.stdout.splitlines()
    seen_total = False
    for line in tail:
        if "TOTAL" in line:
            seen_total = True
        if seen_total:
            m = re.match(r"\s*GAP\s+(\d+)\s*$", line)
            if m:
                return int(m.group(1))
    return None


def analyse():
    gap, current, assign, problems = bbm.build()
    detail = ledger_detail()

    per: dict[str, dict] = {}
    for blocker, info in detail.items():
        rows = [r for r in gap if assign.get(r, (None,))[0] == blocker]
        states = collections.Counter(
            current.get(r, "ROW-GONE") for r in rows
        )
        live = states.get("GAP", 0)
        recovered = len(rows)
        published = info["published"]
        if recovered == 0:
            verdict = "UNLOCATABLE"
        elif live > 0:
            verdict = "LIVE"
        elif recovered == published:
            verdict = "EMPTY-CERTAIN"
        else:
            verdict = "EMPTY-UNCERTIFIABLE"
        per[blocker] = dict(
            info, recovered=recovered, live=live, states=states,
            verdict=verdict, rows=sorted(rows),
        )
    return gap, current, assign, problems, per


def run_controls(gap, current, assign, per) -> bool:
    print("=" * 74)
    print("CONTROLS -- run first, and their result gates every number below")
    print("=" * 74)
    ok = True

    derived_gap = sum(1 for v in current.values() if v == "GAP")
    shipped = shipped_counter_gap()
    agree = shipped is not None and shipped == derived_gap
    print(f"  1. CROSS-INSTRUMENT  derived here {derived_gap}  "
          f"shipped counter (subprocess) {shipped}  "
          f"{'PASS' if agree else 'FAIL'}")
    if not agree:
        ok = False

    n_blockers = len(per)
    published_rows = sum(v["published"] for v in per.values())
    recovered_total = sum(v["recovered"] for v in per.values())
    assigned_total = sum(1 for r in gap if r in assign)
    checks = (
        ("blockers parsed", n_blockers, EXPECTED_BLOCKERS),
        ("published rows", published_rows, EXPECTED_ROWS),
        ("recovered == assigned", recovered_total, assigned_total),
    )
    for label, got, want in checks:
        good = got == want
        if not good:
            ok = False
        print(f"  2. {label:24s} {got:5d}  expected {want:5d}  "
              f"{'PASS' if good else 'FAIL'}")

    absent_ok = ABSENT_BLOCKER not in per
    print(f"  3. MUST-BE-ABSENT blocker not present  "
          f"{'PASS' if absent_ok else 'FAIL'}")
    if not absent_ok:
        ok = False

    # 4. THE INVARIANT THAT GUARDS THE ONLY MISTAKE THAT MATTERS.
    # Controls 1-3 catch a miscount. NONE of them catches the failure that
    # would actually mislead a reader: calling a blocker EMPTY-CERTAIN when
    # rows of it cannot be located. That is not an arithmetic slip, it is the
    # two classes this file exists to separate collapsing into one -- and it
    # would print a clean table saying "safe to close" about a blocker nobody
    # can account for. So the classification is asserted against itself.
    liars = [
        n for n, v in per.items()
        if v["verdict"] == "EMPTY-CERTAIN"
        and (v["recovered"] != v["published"] or v["live"] != 0)
    ]
    ghosts = [
        n for n, v in per.items()
        if v["verdict"] == "EMPTY-UNCERTIFIABLE" and v["live"] != 0
    ]
    print(f"  4. EMPTY-CERTAIN implies full recovery AND zero live  "
          f"{len(liars)} violation(s)  {'PASS' if not liars else 'FAIL'}")
    print(f"  4. EMPTY-UNCERTIFIABLE implies zero live              "
          f"{len(ghosts)} violation(s)  {'PASS' if not ghosts else 'FAIL'}")
    if liars or ghosts:
        for n in (liars + ghosts)[:5]:
            v = per[n]
            print(f"      {n}: recovered {v['recovered']} of "
                  f"{v['published']}, live {v['live']}")
        ok = False

    if problems_global:
        print(f"  build reported {len(problems_global)} problem(s):")
        for p in problems_global[:5]:
            print(f"      {p}")
        ok = False

    print(f"\n  USABLE: {ok}")
    return ok


problems_global: list[str] = []


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    global problems_global
    gap, current, assign, problems, per = analyse()
    problems_global = problems

    if not run_controls(gap, current, assign, per):
        print("\nCONTROLS FAILED. No table is printed; nothing below would be "
              "a reading.")
        return 1
    if "--control" in argv:
        return 0

    order = {"EMPTY-CERTAIN": 0, "EMPTY-UNCERTIFIABLE": 1,
             "UNLOCATABLE": 2, "LIVE": 3}
    rows = sorted(
        per.items(),
        key=lambda kv: (order[kv[1]["verdict"]], -kv[1]["published"], kv[0]),
    )

    if "--tsv" in argv:
        print("blocker\tverdict\tpublished\trecovered\tlive_gap\tcost"
              "\tboundary\tqueue\trows")
        for name, v in rows:
            print(f"{name}\t{v['verdict']}\t{v['published']}\t{v['recovered']}"
                  f"\t{v['live']}\t{v['cost']}\t{v['boundary']}\t{v['queue']}"
                  f"\t{','.join(v['rows'])}")
        return 0

    tally = collections.Counter(v["verdict"] for _n, v in rows)
    print("\n" + "=" * 74)
    print("PER-BLOCKER, CURRENT. published = ledger 2026-09-03;"
          " live = still GAP today")
    print("=" * 74)
    print(f"  {'blocker':34s} {'pub':>4s} {'rec':>4s} {'live':>5s} "
          f"{'cost':>4s}  {'queue':14s} verdict")
    last = None
    for name, v in rows:
        if v["verdict"] != last:
            print(f"  --- {v['verdict']} ---")
            last = v["verdict"]
        print(f"  {name:34s} {v['published']:4d} {v['recovered']:4d} "
              f"{v['live']:5d} {v['cost']:4d}  {v['queue'][:14]:14s} "
              f"{v['verdict']}")

    print("\n" + "=" * 74)
    print("TALLY")
    print("=" * 74)
    for verdict in ("EMPTY-CERTAIN", "EMPTY-UNCERTIFIABLE", "UNLOCATABLE",
                    "LIVE"):
        blockers = [n for n, v in rows if v["verdict"] == verdict]
        pubrows = sum(per[n]["published"] for n in blockers)
        print(f"  {verdict:22s} {tally.get(verdict, 0):3d} blockers"
              f"   {pubrows:4d} published rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
