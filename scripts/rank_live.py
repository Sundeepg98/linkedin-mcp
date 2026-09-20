"""Rank blockers by rows STILL GAP TODAY, not by what the ledger froze.

WHY THIS EXISTS, and it cost a fleet of three waves to learn. On 2026-09-20 an
orchestrator aimed three waves off the ledger's ranking tables at
`_audit/2026-09-03-linkedin-gap-blockers.md` L171-188 and L365-375, briefing
"45 rows sit behind these five blockers". A wave measured the live census and
found **23** did. Twenty-two had left GAP fifteen days earlier, on 2026-09-05,
and the ranking tables still published the freeze figures.

**A RANKING IS A DECISION INPUT, SO A STALE ONE IS A MIS-AIMED FLEET.** The
prose in that document has been amended repeatedly -- its L354 and L544 already
carry corrections -- but nobody amends a table, because a table looks like data
rather than like a claim.

So this derives the ranking instead of reading it. The ledger still supplies the
COST and the boundary charge, which are properties of the work and do not go
stale; the ROW COUNT comes from the live census every run.

    ./venv/Scripts/python.exe scripts/rank_live.py            # live ranking
    ./venv/Scripts/python.exe scripts/rank_live.py --drift    # live vs frozen

**DRIFT IS THE INTERESTING OUTPUT.** A blocker whose published count and live
count disagree is either work somebody did and never wrote back, or a ledger
over-count. Both have been found this week and neither is visible from the
frozen table.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _bbm():
    spec = importlib.util.spec_from_file_location(
        "bbm", str(ROOT / "scripts" / "build_blocker_map.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def live_rows(mod) -> tuple[dict[str, int], dict[str, int]]:
    """Rows a blocker holds that are STILL GAP today, and rows it HOLDS at all.

    Returns ``(still_gap, held)``.

    **BOTH NUMBERS ARE NEEDED AND THE FIRST ALONE LIES.** A blocker with no
    assigned rows scores zero on "assigned and still GAP" -- not because its
    work is done but because nobody has attributed anything to it. Measured the
    hour this file was written: PREMIUM-APPLY-SURFACES publishes 5 and holds 0,
    and reporting it as 0-still-GAP would rank the census's largest unreached
    block as finished. That is the same class of error this file exists to stop,
    reproduced inside the fix for it.

    So a caller must be able to tell "nothing left" from "nothing known", and
    the printer below says UNHELD rather than 0.
    """
    _gap, current, assign, _p = mod.build()
    still: dict[str, int] = {}
    held: dict[str, int] = {}
    for row, (blocker, *_rest) in assign.items():
        held[blocker] = held.get(blocker, 0) + 1
        if current.get(row) == "GAP" or current.get(row) is None:
            still[blocker] = still.get(blocker, 0) + 1
    return still, held


def published_or_empty(mod):
    """Every blocker the ledger publishes, so UNHELD ones stay visible."""
    return list(mod.ledger_counts())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--drift", action="store_true",
                    help="show published vs live, biggest disagreement first")
    args = ap.parse_args(argv)

    mod = _bbm()
    published = mod.ledger_counts()
    live, held = live_rows(mod)

    if args.drift:
        rows = []
        for b, pub in published.items():
            p = pub[0] if isinstance(pub, tuple) else pub
            rows.append((abs(p - live.get(b, 0)), b, p, live.get(b, 0),
                         held.get(b, 0)))
        rows.sort(reverse=True)
        print(f"  {'blocker':34s} {'pub':>5s} {'held':>5s} {'stillGAP':>9s} {'drift':>6s}")
        for d, b, p, lv, h in rows:
            if d == 0:
                continue
            mark = "  UNHELD -- nothing attributed, not nothing left" if h == 0 else ""
            print(f"  {b:34s} {p:5d} {h:5d} {lv:9d} {lv - p:+6d}{mark}")
        stale = sum(1 for d, *_ in rows if d)
        print(f"\n  blockers whose published count is not their live count: {stale}")
        print("  Each is either work done and never written back, or an over-count.")
        return 0

    print(f"  {'blocker':34s} {'stillGAP':>9s} {'held':>5s}")
    for b, n in sorted(live.items(), key=lambda kv: (-kv[1], kv[0])):
        if n:
            print(f"  {b:34s} {n:9d} {held.get(b, 0):5d}")
    unheld = sorted(b for b in published_or_empty(mod) if held.get(b, 0) == 0)
    if unheld:
        print("")
        print("  UNHELD blockers -- they publish rows and hold none, so no "
              "live count exists for them, and a 0 here would read as done: "
              + str(len(unheld)))
        for b in unheld:
            print(f"    {b}")
    print(f"\n  blockers with at least one row still GAP: "
          f"{sum(1 for n in live.values() if n)}")
    print(f"  rows still GAP and assigned: {sum(live.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
