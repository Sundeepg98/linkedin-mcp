"""WHICH FROZEN-GAP ROWS MATCH A WORD, AND WHERE IS EACH ONE FILED?

WHY THIS EXISTS. A blocker left PARTIAL has two possible causes and they need
different answers: a row the search missed, or a count the corpus never
supported. Telling them apart means answering one question -- *does any
UNASSIGNED row belong to this family?* -- and the honest form of a NO is a
refusal that names what it DID see, not one that reports zero matches.

Every "family exhausted" verdict in this repository has rested on somebody
running this sweep by hand and reporting the conclusion. The sweep itself was
never committed, so the next wave re-ran it from memory and the one after that
took the conclusion on trust. This is the sweep.

WHAT IT IS NOT. A name match is NOT EVIDENCE for an assignment -- the repo has
said so repeatedly and this file does not change it. It is evidence for the
NEGATIVE: if a word that names a blocker's family returns rows and every one of
them is already filed, the family is closed and a missing row is not hiding in
the pool. Used the other way round it manufactures exactly the filings the
blocker-map evidence rules exist to prevent.

    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py analytics comment
    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py --unassigned
    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py --control
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402
import _check_published_split as sp  # noqa: E402

#: `--control` needs BOTH arms. A sweep that only ever confirms a hit cannot be
#: shown to discriminate, and a sweep that only ever confirms a miss cannot be
#: shown to see. HIT is a word the frozen set certainly contains; MISS is one
#: it certainly does not.
CONTROL_HIT = "newsletter"
CONTROL_MISS = "zzzznotacapability"


def sweep(word: str):
    gap, cur, assign, _p = bbm.build()
    dirs = sp.row_directions()
    try:
        import _check_jobs_range_directions as jrd
        jdirs, _un = jrd.jobs_directions()
        dirs = {**dirs, **jdirs}
    except Exception:
        pass  # the J-range reader is optional; its absence costs direction only
    hits = [r for r in sorted(gap, key=lambda s: (s[0], len(s), s))
            if word.lower() in gap[r][1].lower()]
    return gap, cur, assign, dirs, hits


def report(word: str) -> tuple[int, int]:
    gap, cur, assign, dirs, hits = sweep(word)
    un = [r for r in hits if r not in assign]
    print(f"\n=== {word!r} -- {len(hits)} of {len(gap)} frozen GAP rows, "
          f"{len(un)} UNASSIGNED ===")
    for r in hits:
        b = assign.get(r, ("UNASSIGNED",))[0]
        mark = "  <<<" if b == "UNASSIGNED" else ""
        print(f"  {r:8s} [{dirs.get(r,'?'):3s}] {b:30s} {gap[r][1][:78]}{mark}")
    if hits and not un:
        print(f"  -> every row naming {word!r} is filed; the pool holds none")
    return len(hits), len(un)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("words", nargs="*", help="substrings to sweep for")
    ap.add_argument("--unassigned", action="store_true",
                    help="list the whole unassigned pool instead")
    ap.add_argument("--control", action="store_true",
                    help="run both control arms and assert on them")
    args = ap.parse_args(argv)

    if args.control:
        hit_n, _ = report(CONTROL_HIT)
        miss_n, _ = report(CONTROL_MISS)
        ok = hit_n > 0 and miss_n == 0
        print(f"\ncontrol: {CONTROL_HIT!r} -> {hit_n} hits (must be > 0); "
              f"{CONTROL_MISS!r} -> {miss_n} hits (must be 0) -- "
              f"{'the sweep both SEES and DISCRIMINATES' if ok else 'BROKEN'}")
        return 0 if ok else 1

    if args.unassigned or not args.words:
        gap, cur, assign, dirs, _h = sweep("")
        pool = [r for r in sorted(gap, key=lambda s: (s[0], len(s), s))
                if r not in assign]
        print(f"UNASSIGNED pool -- {len(pool)} of {len(gap)} frozen GAP rows")
        for r in pool:
            print(f"  {r:8s} [{dirs.get(r,'?'):3s}] "
                  f"today={cur.get(r,'ROW-GONE'):16s} {gap[r][1][:80]}")
        return 0

    for w in args.words:
        report(w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
