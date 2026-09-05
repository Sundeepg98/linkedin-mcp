"""Count the state of every capability row in `_audit/_census/`, from the files.

WHY THIS IS TRACKED. The count that produced 409 -- and every re-count since --
was taken by a script living in `_audit/_scratch/`, which `.gitignore` excludes
by design. So the headline number of this repository's capability census could
not be reproduced from a clone by anybody, and a measurement nobody else can
take is a measurement on its way to becoming a quotation. That is the disease
`_audit/2026-09-05-decide-retire-rulings.md` section 9.4 names one level up.

WHAT IT COUNTS, AND WHAT IT DELIBERATELY DOES NOT. It counts TABLE ROWS carrying
a state cell. Rows are not capabilities: `profile.md` collapses two blocks
(`O6-O20` stands for 15, the `P-R` block stands for 45), so the published
capability DENOMINATOR is 705 rows + 59 collapsed - 2 stateless = 761, while the
GAP numerator is a plain row count. Correcting a capability total from a row
count is the error the ledger's own section 1 warns about, so this script prints
rows and states and computes no denominator.

    ./venv/Scripts/python.exe scripts/count_census_states.py

CONTROL. `--expect J=99,P=79,M=109,N=122` fails the run if the GAP counts do not
match, so a silent drift is loud. Without it the script reports and returns 0.
A ROW WHOSE STATE CELL IS PROSE IS INVISIBLE HERE AND THAT IS NOT A BUG IN THE
CENSUS -- it is why `--unstated` exists: it lists rows in a capability table
that carry NO recognised state at all, which is the only way a row silently
leaves the numerator without anybody ruling it. Measured 2026-09-05: `N 132` is
GAP in its own prose and uncountable here, because its state cell was replaced
with a sentence.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

CENSUS = pathlib.Path(__file__).resolve().parents[1] / "_audit" / "_census"
SLICES = {
    "J": "jobs.md",
    "P": "profile.md",
    "M": "messaging-and-content.md",
    "N": "network.md",
}
#: Every state spelling the four slices use, long and short form alike.
STATES = {
    "GAP", "CP", "CU", "CCD", "ER", "XR",
    "EXCLUDED-RULED", "COVERED-PROVEN", "COVERED-UNFIRED",
    "COVERED-CANNOT-DELIVER", "MEASURED-ABSENT",
}
#: `XR` was added 2026-09-05 and is the single biggest thing this counter could
#: not see. It is `jobs.md`'s own short spelling of EXCLUDED-RULED, used 23
#: times and NOWHERE ELSE in the four slices -- and `jobs.md`'s own frozen
#: table reads `EXCLUDED-RULED 23`. So 23 rows carrying a correctly-written
#: verdict were in neither the numerator nor the denominator, and the cause was
#: a DIALECT THIS INSTRUMENT DID NOT SPEAK, not prose in a state cell. It is
#: reported under its own key rather than folded into EXCLUDED-RULED, which is
#: how `CP`/`CU`/`CCD` are already handled: a counter that silently merges two
#: spellings cannot show you that a slice uses two.
ROW = re.compile(r"^\|\s*([A-Za-z0-9][A-Za-z0-9 .\-]*?)\s*\|")
HEADERS = {"#", "id", "row", "rows", "state", "blocker", "capability"}


def cells(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def state_of(row_cells: list[str]) -> str:
    for cell in row_cells[1:]:
        bare = cell.replace("`", "").replace("*", "").strip()
        head = bare.split(" ")[0]
        if head in STATES:
            return head
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--expect", default="",
                    help="GAP control, e.g. J=99,P=79,M=109,N=122")
    ap.add_argument("--unstated", action="store_true",
                    help="list capability-table rows carrying no state cell")
    args = ap.parse_args(argv)

    expect = {}
    for part in filter(None, args.expect.split(",")):
        k, _, v = part.partition("=")
        expect[k.strip()] = int(v)

    totals: dict[str, int] = {}
    failed = False
    for letter, name in SLICES.items():
        path = CENSUS / name
        counts: dict[str, int] = {}
        unstated: list[str] = []
        rows = 0
        for lineno, line in enumerate(path.read_text(encoding="utf-8",
                                                     errors="replace").splitlines(), 1):
            if not line.startswith("|"):
                continue
            c = cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ROW.match(line) or c[0].lower() in HEADERS:
                continue
            st = state_of(c)
            # The network slice's admin-only table carries no state column at
            # all; its own prose says all fifteen are GAP.
            if not st and letter == "N" and re.fullmatch(r"A\d+", c[0]):
                st = "GAP"
            if not st:
                # Only a row sitting in a table that HAS states is interesting.
                unstated.append(f"{letter} {c[0]} (line {lineno}) {c[1][:60]}")
                continue
            rows += 1
            counts[st] = counts.get(st, 0) + 1
        for st, n in counts.items():
            totals[st] = totals.get(st, 0) + n
        gap = counts.get("GAP", 0)
        note = ""
        if letter in expect:
            ok = gap == expect[letter]
            note = f"   expected {expect[letter]:4d}  {'MATCH' if ok else 'MISMATCH'}"
            failed = failed or not ok
        print(f"{name:28s} stated rows {rows:4d}   GAP {gap:4d}{note}")
        for st in sorted(counts):
            if st != "GAP":
                print(f"{'':28s}   {st:24s} {counts[st]:4d}")
        if args.unstated and unstated:
            print(f"{'':28s}   rows with NO state cell: {len(unstated)}")
            for u in unstated:
                print(f"{'':30s} {u}")

    print("\nTOTAL, all four slices")
    for st in sorted(totals):
        print(f"  {st:26s} {totals[st]:4d}")
    print(f"  {'stated rows':26s} {sum(totals.values()):4d}")
    if expect:
        want = sum(expect.values())
        got = totals.get("GAP", 0)
        print(f"\nGAP control: expected {want}, measured {got} -- "
              f"{'MATCH' if want == got else 'MISMATCH'}")
        failed = failed or want != got
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
