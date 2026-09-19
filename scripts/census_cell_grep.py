"""CORPUS-WIDE CENSUS CELL MATCHER -- ask which rows say a thing, and where they already live.

WHY THIS EXISTS. Four matchers built during the 2026-09-19 blocker-map recovery
reached a fixed point and stopped, and every one of them read the CAPABILITY
column. The census also names blockers in the REASON cell and enumerates whole
families in section 2's grouping lines, and once someone looked there, eleven
more rows routed. This tool reads the WHOLE ROW, including the reason cell.

    ./venv/Scripts/python.exe scripts/census_cell_grep.py "per-post comment control"
    ./venv/Scripts/python.exe scripts/census_cell_grep.py --col reason "picker"
    ./venv/Scripts/python.exe scripts/census_cell_grep.py --selftest

WHAT IT IS DELIBERATELY NOT. It is not a scorer and it does not rank. It prints
EVERY hit, including rows already filed to some other blocker, because the
question that actually decides an assignment is usually "why can this row NOT go
to the obvious place" -- and you cannot see that if the tool only shows you free
rows. Three assignments this round turned on a hit whose blocker was COMPLETE:

    "on your post"      -> 3 rows; the third is in COMMENT-IDENTIFIER, 4W, FULL
    "no tool returns"   -> 3 rows; the third is in SEARCH-APPEARANCES, FULL
    "a picker surface"  -> 2 rows, and FILE-UPLOAD-UNSANCTIONED at 16/16 is why
                           they could not go to the blocker their article shares

HOW TO READ THE COUNT. A phrase that returns ONE unassigned row against a
blocker published at one row is the PICKER-SURFACES standard and is bankable. A
phrase that returns six is a candidate list and needs a different discriminator
-- direction, or a committed row-id enumeration, or a ruling. The count is the
finding; the tool does not decide.

THE CONTROLS, AND THIS TOOL DOES NOT ENTER THE REGISTER WITHOUT THEM.
`--selftest` runs both and is expected to be kept green:
  * POSITIVE -- "a picker surface" must return exactly 2 rows, M M16 and M M17.
    That is the known-answer case the PICKER-SURFACES filing was made on, so a
    change that breaks the parse shows up as a wrong count rather than silence.
  * NEGATIVE -- a nonsense phrase must return exactly 0. A matcher that cannot
    return zero certifies nothing; this one was run on "zzz-no-such-reason"
    before it was trusted on anything.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
CENSUS = ROOT / "_audit" / "_census"
MAP = CENSUS / "blocker-map.tsv"

SLICES = {"J": "jobs.md",
          "M": "messaging-and-content.md",
          "N": "network.md",
          "P": "profile.md"}

#: Cells that are exactly a direction token. The census writes R+W several ways.
_DIRECTIONS = {"R", "W", "R+W", "RW", "R + W"}


def _load_map() -> tuple[dict, dict]:
    """row_id -> blocker, row_id -> state_today, off the generated map."""
    blocker, state = {}, {}
    if not MAP.exists():
        return blocker, state
    with MAP.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith(">"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7 or parts[0] == "row_id":
                continue
            blocker[parts[0]] = parts[1]
            state[parts[0]] = parts[6]
    return blocker, state


def scan(phrase: str, reason_only: bool = False) -> list[dict]:
    phrase = phrase.lower()
    blocker, state = _load_map()

    # A MISSING CORPUS MUST NOT LOOK LIKE AN ABSENCE OF EVIDENCE. Found by
    # mutation-testing this file's own selftest: a copy run from outside the
    # repo resolved ROOT elsewhere, read no census at all, returned [] -- and
    # THE NEGATIVE CONTROL STILL PASSED, because "nonsense phrase -> 0 hits"
    # is indistinguishable from "no corpus -> 0 hits". Only the positive
    # control caught it. A probe with no guard here reports an outage as a
    # finding about the data, which is the failure this repository has been
    # bitten by before. Fail loudly instead.
    missing = [n for n in SLICES.values() if not (CENSUS / n).exists()]
    if missing:
        raise SystemExit("census slice file(s) not found under %s: %s -- refusing to "
                         "report 0 hits, because that would read as an absence of "
                         "evidence rather than a missing corpus"
                         % (CENSUS, ", ".join(sorted(missing))))

    hits = []
    for slice_letter, name in SLICES.items():
        path = CENSUS / name
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 3:
                continue
            row_id = cells[0].strip("`*").strip()
            # Skip separator rows and header rows; keep everything else, because
            # section 2's GROUPING rows are not census rows and are exactly what
            # the row-id enumerations live in.
            if not row_id or row_id.lower() in ("row", "id", "#") or set(row_id) <= set("-: "):
                continue
            haystack = (cells[-1] if reason_only else " | ".join(cells[1:])).lower()
            if phrase not in haystack:
                continue
            key = "%s %s" % (slice_letter, row_id)
            direction = ""
            for cell in cells[1:]:
                if cell.strip("*` ") in _DIRECTIONS:
                    direction = cell.strip("*` ")
                    break
            hits.append({"row": key,
                         "dir": direction or "?",
                         "blocker": blocker.get(key, "(NOT IN FROZEN 409)"),
                         "state": state.get(key, "-"),
                         "capability": cells[1] if len(cells) > 1 else "",
                         "file": name,
                         "line": lineno})
    return hits


def _print(hits: list[dict], phrase: str, reason_only: bool) -> None:
    where = "reason cell only" if reason_only else "whole row"
    print("PHRASE %r   %s   HITS %d" % (phrase, where, len(hits)))
    print("%-10s %-4s %-15s %-30s %s" % ("row", "dir", "state", "blocker now", "capability"))
    for h in hits:
        mark = "  <== UNASSIGNED" if h["blocker"] == "UNASSIGNED" else ""
        print("%-10s %-4s %-15s %-30s %s%s"
              % (h["row"], h["dir"], h["state"], h["blocker"], h["capability"][:58], mark))
    unassigned = sum(1 for h in hits if h["blocker"] == "UNASSIGNED")
    filled = sum(1 for h in hits if h["blocker"] not in ("UNASSIGNED", "(NOT IN FROZEN 409)"))
    outside = sum(1 for h in hits if h["blocker"] == "(NOT IN FROZEN 409)")
    print("\n  total %d   unassigned %d   already-filed %d   outside-frozen %d"
          % (len(hits), unassigned, filled, outside))


def selftest() -> int:
    ok = True

    positive = scan("a picker surface")
    rows = sorted(h["row"] for h in positive)
    if rows != ["M M16", "M M17"]:
        print("FAIL positive control: expected ['M M16', 'M M17'], got %r" % (rows,))
        ok = False
    else:
        print("pass  positive control: 'a picker surface' -> M M16, M M17")

    negative = scan("zzz-no-such-reason-anywhere")
    if negative:
        print("FAIL negative control: a nonsense phrase returned %d hits" % len(negative))
        ok = False
    else:
        print("pass  negative control: nonsense phrase -> 0 hits")

    print("SELFTEST", "GREEN" if ok else "RED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("phrase", nargs="*", help="substring to look for, case-insensitive")
    ap.add_argument("--col", choices=("reason", "row"), default="row",
                    help="'reason' restricts the search to the last cell")
    ap.add_argument("--selftest", action="store_true", help="run the two controls and exit")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.phrase:
        ap.error("give a phrase, or --selftest")

    phrase = " ".join(args.phrase)
    reason_only = args.col == "reason"
    _print(scan(phrase, reason_only), phrase, reason_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
