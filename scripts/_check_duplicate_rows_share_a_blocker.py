"""DO TWO ROWS OF ONE CAPABILITY EVER SHARE A BLOCKER? MEASURED, NOT ASSUMED.

WHY. `blocker-assignments.tsv` admits `P B7` to `BADGES-SURFACE` on an
arithmetic whose own note says the name argues against it -- *"The count admits
it; I would not have on the name."* That arithmetic has one load-bearing
premise: that `B8` and `K9` *"collapse to one slot"*, i.e. that one blocker
cannot hold two frozen-GAP rows of the same capability. Nobody measured it. This
measures it.

TWO ARMS, because one shape of duplicate is invisible to the other.

  PAIRWISE (Jaccard over capability tokens). Finds `B8`/`K9`, `M C83`/`P L4`,
  `M C50`/`M C81`. This is the arm that answers the premise above.

  CONTAINMENT. Finds a COMPOUND row split across a slice boundary into halves,
  which pairwise Jaccard structurally cannot see: `M C79` *"Follow or unfollow
  member articles"* scores only 0.50 against each of `N 41` and `N 42`,
  under any useful threshold -- but its token set is wholly CONTAINED in their
  union. A wave that ran only the pairwise arm would report those two as
  unrelated to a row sitting in the blocker they were candidates for.
  `_audit/2026-09-19-partial-blockers-closed.md` found that pair by reading;
  this is the reading made mechanical.

WHAT THE ANSWER IS FOR, AND WHAT IT IS NOT FOR. A duplicate pair sharing a
blocker is EVIDENCE ABOUT THE LEDGER'S HABITS, never a licence to file a row.
Filing still needs a committed source naming the row.

CONTROL, because a check that cannot fail certifies nothing: the pairwise arm
must find the `M C83`/`P L4` pair that `_audit/2026-09-19-the-five-requests-
ruled.md` names by hand, and the containment arm must find `M C79` inside
`N 41` + `N 42` which `_audit/2026-09-19-partial-blockers-closed.md` names by
hand. If either misses its known pair, its silence means nothing.

    ./venv/Scripts/python.exe scripts/_check_duplicate_rows_share_a_blocker.py
    ./venv/Scripts/python.exe scripts/_check_duplicate_rows_share_a_blocker.py --control
"""
from __future__ import annotations

import argparse
import itertools
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import build_blocker_map as bbm  # noqa: E402
import _check_published_split as sp  # noqa: E402

#: Words that carry no capability meaning. Kept short on purpose: a long stop
#: list is a tuning knob, and a detector tuned until it agrees with the reader
#: is the reader wearing an instrument's clothes.
STOP = {"a", "an", "the", "your", "you", "of", "to", "on", "in", "from", "for",
        "or", "and", "with", "at", "is", "it", "this", "that", "own"}

THRESHOLD = 0.55


def toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", s.lower()) if w not in STOP}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--control", action="store_true",
                    help="require each arm to find the pair a committed audit names by hand")
    args = ap.parse_args(argv)

    gap, _cur, assign, _p = bbm.build()
    dirs = sp.row_directions()
    rows = sorted(gap, key=lambda s: (s[0], len(s), s))
    tok = {r: toks(gap[r][1]) for r in rows}

    def blocker(r: str) -> str:
        return assign.get(r, ("UNASSIGNED",))[0]

    pairs = []
    for a, b in itertools.combinations(rows, 2):
        if not tok[a] or not tok[b]:
            continue
        j = len(tok[a] & tok[b]) / len(tok[a] | tok[b])
        if j >= THRESHOLD:
            pairs.append((round(j, 2), a, b))
    pairs.sort(reverse=True)

    same = split = 0
    print(f"PAIRWISE ARM -- Jaccard >= {THRESHOLD}: {len(pairs)} pairs\n")
    for j, a, b in pairs:
        ba, bb = blocker(a), blocker(b)
        if ba == bb and ba != "UNASSIGNED":
            tag, _ = "SAME-BLOCKER", same
            same += 1
        elif "UNASSIGNED" in (ba, bb):
            tag = "one-unassigned"
        else:
            tag = "SPLIT-ACROSS"
            split += 1
        print(f"  {j:4.2f} {tag:15s} {'INTRA' if a[0] == b[0] else 'cross':5s} "
              f"{a:7s}[{dirs.get(a,'?'):2s}] {ba:26s} | "
              f"{b:7s}[{dirs.get(b,'?'):2s}] {bb:26s}")

    intra_same = sum(1 for j, a, b in pairs
                     if a[0] == b[0] and blocker(a) == blocker(b) != "UNASSIGNED")
    print(f"\n  both rows in ONE blocker   {same}   (of which INTRA-slice {intra_same})")
    print(f"  split across two blockers  {split}")
    print("  -> a blocker holding both rows of a near-duplicate pair is ORDINARY,")
    print("     intra-slice included. Nothing forces such a pair into one slot.")

    print("\nCONTAINMENT ARM -- a COMPOUND row split into halves in another slice")
    # BARE CONTAINMENT IS A COINCIDENCE GENERATOR AND WAS MEASURED AS ONE: the
    # first draft required only `tok[c] <= tok[a] | tok[b]` and returned 1217
    # hits, nearly all of them a row plus an unrelated bystander that happened
    # to carry the one missing word. Three STRUCTURAL constraints cut it, and
    # each describes the shape being looked for rather than tuning the output:
    #
    #   * THE TWO HALVES LIVE IN ONE SLICE AND THE COMPOUND IN ANOTHER. That is
    #     what "split across a slice boundary" means; a pair drawn from two
    #     different slices is not a split of anything.
    #   * NEITHER HALF IS A BYSTANDER. Each must cover at least half of the
    #     compound's tokens on its own, so a row contributing one stray word
    #     cannot complete a containment.
    #   * NEITHER HALF ALREADY CONTAINS THE WHOLE, which would be a pairwise
    #     duplicate and belongs to the arm above.
    HALF_COVER = 0.5
    found: list[tuple[str, str, str]] = []
    for c in rows:
        if len(tok[c]) < 3:
            continue
        for a, b in itertools.combinations([r for r in rows if r[0] != c[0]], 2):
            if a[0] != b[0] or not tok[a] or not tok[b]:
                continue
            if tok[c] <= tok[a] or tok[c] <= tok[b]:
                continue
            if not tok[c] <= (tok[a] | tok[b]):
                continue
            if (len(tok[c] & tok[a]) / len(tok[c]) < HALF_COVER
                    or len(tok[c] & tok[b]) / len(tok[c]) < HALF_COVER):
                continue
            found.append((c, a, b))
    for c, a, b in found:
        print(f"  {c:7s} {blocker(c):26s} <= {a:7s} {blocker(a):24s} + "
              f"{b:7s} {blocker(b)}")
        print(f"     {gap[c][1][:70]}")
    print(f"  compound rows split across a pair: {len(found)}")

    if args.control:
        arm1 = any({a, b} == {"M C83", "P L4"} for _j, a, b in pairs)
        arm2 = any(c == "M C79" and {a, b} == {"N 41", "N 42"} for c, a, b in found)
        print(f"\ncontrol pairwise    (M C83 / P L4)            "
              f"{'FOUND' if arm1 else 'MISSED -- ARM IS BLIND'}")
        print(f"control containment (M C79 <= N 41 + N 42)    "
              f"{'FOUND' if arm2 else 'MISSED -- ARM IS BLIND'}")
        return 0 if (arm1 and arm2) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
