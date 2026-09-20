"""For each blocker, WHICH DOCUMENT ARGUES IT -- derived, not listed.

WHY THIS EXISTS. A wave measured, 2026-09-20, that **34 of 95 blockers -- 100
rows, 86 of them still GAP -- have no reason in any of the seven documents a
reader starting at the blocker table would reach.** Then it measured the
over-report, which is the half that matters: swept across every audit document,
**34 of 34 are named somewhere and none is orphaned.**

**Every reason exists, and is often excellent. None of it is findable from the
artifact people actually open.** That is the same defect this repository already
records about corrections -- a corrector names what it corrects, and the
corrected document cannot name its corrector, so a reader starting at the claim
never arrives.

AND IT PREDICTS WRONG VERDICTS, WHICH IS WHY IT IS WORTH A SCRIPT. The same wave
measured that a contingent write-off carrying a REOPENER is 15% still GAP, while
one carrying NONE is 91% -- and that all five wrongly-closed blockers found this
week sit in the no-reopener set. A blocker nobody can find the argument for is a
blocker nobody re-examines.

    ./venv/Scripts/python.exe scripts/find_blocker_reason.py
    ./venv/Scripts/python.exe scripts/find_blocker_reason.py --unreachable

THE SCORE IS NOT A VERDICT. This ranks candidate documents by how much they
argue a blocker; it does not decide which is right. A blocker whose best
candidate scores low is a blocker to READ, not one to re-file -- the ranking
points at prose, and a human still has to read the prose.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIT = ROOT / "_audit"

#: Documents a reader starting at the blocker table actually reaches: the
#: ledger, the census slices, and the map itself. Anything OUTSIDE this set is
#: where a reason can exist and still be unfindable.
REACHABLE = {
    "2026-09-03-linkedin-gap-blockers.md",
    "blocker-map.tsv",
    "blocker-assignments.tsv",
    "jobs.md",
    "network.md",
    "profile.md",
    "messaging-and-content.md",
}

#: Words that mark a sentence ARGUING a blocker rather than merely naming it.
#: Deliberately broad -- a false positive costs a document in a ranked list; a
#: false negative hides the only argument there is.
ARGUES = re.compile(
    r"\b(because|therefore|refus|admit|rule[ds]?|ruling|measur|evidence|blocked|"
    r"cannot|never|proves?|shows?|the reason|which is why|so that|hence)\b",
    re.I,
)


def _bbm():
    spec = importlib.util.spec_from_file_location(
        "bbm", str(ROOT / "scripts" / "build_blocker_map.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["bbm"] = mod
    spec.loader.exec_module(mod)
    return mod


def candidates(blocker: str) -> list[tuple[int, str]]:
    """Documents that NAME the blocker, ranked by how much they ARGUE it.

    The score is the count of argument-marked lines mentioning it, not the count
    of mentions: a table listing every blocker once scores zero, which is
    exactly right -- it names them and argues nothing.
    """
    needle = re.compile(re.escape(blocker), re.I)
    out: list[tuple[int, str]] = []
    for path in sorted(AUDIT.rglob("*.md")) + sorted(AUDIT.rglob("*.tsv")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:                      # unreadable is UNKNOWN,
            print(f"  ! unreadable {path}: {error}",  # never silently absent
                  file=sys.stderr)
            continue
        score = sum(
            1 for line in text.splitlines()
            if needle.search(line) and ARGUES.search(line)
        )
        if score:
            out.append((score, str(path.relative_to(ROOT)).replace("\\", "/")))
    out.sort(reverse=True)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--unreachable", action="store_true",
                    help="only blockers whose best argument is OUTSIDE the "
                         "documents a reader starting at the table reaches")
    args = ap.parse_args(argv)

    mod = _bbm()
    blockers = sorted(mod.ledger_counts())
    unreachable, orphaned = [], []
    for b in blockers:
        c = candidates(b)
        if not c:
            orphaned.append(b)
            continue
        best_doc = c[0][1]
        if pathlib.Path(best_doc).name not in REACHABLE:
            unreachable.append((b, c[0][0], best_doc))

    if args.unreachable:
        print(f"  {'blocker':34s} {'score':>5s}  best argument lives in")
        for b, s, d in sorted(unreachable, key=lambda x: (-x[1], x[0])):
            print(f"  {b:34s} {s:5d}  {d}")
    print(f"\n  blockers                                   {len(blockers)}")
    print(f"  best argument NOT in a reachable document  {len(unreachable)}")
    print(f"  ORPHANED -- argued nowhere at all          {len(orphaned)}")
    for b in orphaned:
        print(f"    {b}")
    print("\n  A blocker whose argument is unreachable is one nobody re-examines.")
    print("  Measured 2026-09-20: reopener present -> 15% still GAP; absent -> 91%.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
