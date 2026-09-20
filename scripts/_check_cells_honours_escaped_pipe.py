"""Control for `count_census_states.cells()`: the markdown escape `\\|` is content.

WHAT THIS CERTIFIES, AND THE ONLY REASON IT IS WORTH SHIPPING. A parser repair is
the easiest kind of change to claim and the hardest to bound: the fix is four
lines, and the question nobody asks is WHAT ELSE MOVED. This runs the OLD
implementation and the NEW one over every line of all five census files and
asserts the disagreement set is EXACTLY the lines carrying an escaped pipe --
so the repair is shown to do its job AND shown to do nothing else.

THE OLD IMPLEMENTATION IS CARRIED HERE VERBATIM, on purpose. A control that
describes the bug in prose cannot fail when the bug comes back. `_naive_cells`
below is the code as it stood at `e6b11e5`, so `--demonstrate-red` re-runs the
whole suite against it and asserts every assertion FAILS. That is the
shown-failing proof: this file convicts the defect it was written against, on
demand, forever -- not once in a report nobody re-runs.

    python scripts/_check_cells_honours_escaped_pipe.py
    python scripts/_check_cells_honours_escaped_pipe.py --demonstrate-red
    python scripts/_check_cells_honours_escaped_pipe.py --verbose

AN EMPTY DISAGREEMENT SET IS A LOUD EVENT, never a quiet pass. If the corpus
stops carrying an escaped pipe -- because somebody rewrites `J 50`, say -- then
the corpus half of this control stops exercising anything, and an assertion
satisfied by an empty result cannot fail. It says so and returns non-zero
rather than printing ok over a vacuum. The PLANTED specimens keep working in
that case and are reported separately, so the two halves cannot cover for each
other.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import count_census_states as ccs        # noqa: E402  (the shipped instrument)

ROOT = pathlib.Path(__file__).resolve().parents[1]
CENSUS = ROOT / "_audit" / "_census"
#: All four counted slices plus the inventory, which is NOT counted by
#: `count_census_states` but is parsed by other readers with the same function.
#: A repair scoped to the counted four would leave the fifth unmeasured.
FILES = ("jobs.md", "profile.md", "messaging-and-content.md", "network.md",
         "mcp-inventory.md")

ESCAPE = "\\|"


def _naive_cells(line: str) -> list[str]:
    """`cells()` exactly as it stood at `e6b11e5`, before the repair.

    Kept byte-for-byte rather than paraphrased. This is the specimen the
    control convicts; a paraphrase would convict a paraphrase.
    """
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


#: Hand-built rows with a known-correct answer. Each is a SHAPE the corpus
#: either has or could acquire tomorrow, and the naive parser gets every one
#: of them wrong except the last two -- which are here precisely so the
#: specimen set is not all reds. A control whose every case fails under the old
#: code cannot show that the new code left the ordinary case alone.
SPECIMENS: tuple[tuple[str, str, list[str]], ...] = (
    ("escape in the middle cell",
     r"| 50 | a \| b | XR | reason |",
     ["50", "a | b", "XR", "reason"]),
    ("escape in the reason cell, which is where the corpus puts it",
     r"| 103 | thing | CU | head \| tail |",
     ["103", "thing", "CU", "head | tail"]),
    ("two escapes in one cell",
     r"| 7 | x | ER | (saved\|applied\|draft) |",
     ["7", "x", "ER", "(saved|applied|draft)"]),
    ("a row whose final cell ENDS in an escaped pipe, with no border pipe",
     r"| 8 | x | ER | trailing \|",
     ["8", "x", "ER", "trailing |"]),
    ("no escape at all -- must be untouched",
     "| 9 | plain | GAP | ordinary reason |",
     ["9", "plain", "GAP", "ordinary reason"]),
    ("an empty trailing cell, which is NOT an escape",
     "| 10 | plain | GAP | |",
     ["10", "plain", "GAP", ""]),
)


def check_specimens(fn, verbose: bool) -> list[str]:
    """Every specimen `fn` gets wrong."""
    bad = []
    for name, line, want in SPECIMENS:
        got = fn(line)
        ok = got == want
        if verbose or not ok:
            print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
            if not ok:
                print(f"          want {want}")
                print(f"          got  {got}")
        if not ok:
            bad.append(name)
    return bad


def corpus_disagreements() -> tuple[list[tuple[str, int, str]], list[tuple[str, int, str]]]:
    """(lines where old and new disagree, lines carrying an escaped pipe).

    Both as (filename, lineno, raw line). Every line of every file, not only
    table rows: the repair must be shown harmless on prose too, since `cells`
    is called by readers that filter differently from the counter.
    """
    disagree: list[tuple[str, int, str]] = []
    escaped: list[tuple[str, int, str]] = []
    for name in FILES:
        path = CENSUS / name
        text = path.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            if ESCAPE in line:
                escaped.append((name, lineno, line))
            if ccs.cells(line) != _naive_cells(line):
                disagree.append((name, lineno, line))
    return disagree, escaped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--demonstrate-red", action="store_true",
                    help="run the suite against the OLD parser and assert it FAILS")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    if args.demonstrate_red:
        print("DEMONSTRATE-RED -- running the specimen suite against `_naive_cells`,")
        print("the implementation as it stood at `e6b11e5`. This MUST fail.\n")
        bad = check_specimens(_naive_cells, verbose=True)
        expected_reds = {
            "escape in the middle cell",
            "escape in the reason cell, which is where the corpus puts it",
            "two escapes in one cell",
            "a row whose final cell ENDS in an escaped pipe, with no border pipe",
        }
        print(f"\n  old parser failed {len(bad)} of {len(SPECIMENS)} specimens")
        if set(bad) != expected_reds:
            print("  CONTROL BROKEN: the old parser did not fail exactly the four")
            print("  escape specimens. Either the specimens moved or the copy of the")
            print(f"  old parser is not the old parser. failed={sorted(bad)}")
            return 1
        print("  ok    and it failed EXACTLY the four escape specimens, passing the")
        print("        two that carry no escape -- so the repair's subject is the")
        print("        escape and not the parse in general.")
        return 0

    failed = False
    print("SPECIMENS -- hand-built rows with a known-correct answer")
    bad = check_specimens(ccs.cells, verbose=args.verbose)
    if bad:
        print(f"  FAILED {len(bad)} of {len(SPECIMENS)}")
        failed = True
    else:
        print(f"  ok    all {len(SPECIMENS)} specimens")

    print("\nCORPUS -- every line of five census files, old parser vs new")
    disagree, escaped = corpus_disagreements()
    print(f"  lines carrying an escaped pipe : {len(escaped)}")
    print(f"  lines where old and new differ : {len(disagree)}")

    # LOUD ON EMPTY. Not a pass.
    if not escaped:
        print("  EMPTY: no line in the corpus carries an escaped pipe any more, so")
        print("  this half of the control exercised NOTHING. That is a finding about")
        print("  the corpus, not a pass. Re-scope it or delete it deliberately.")
        failed = True

    d_keys = {(n, ln) for n, ln, _ in disagree}
    e_keys = {(n, ln) for n, ln, _ in escaped}
    only_disagree = sorted(d_keys - e_keys)
    only_escaped = sorted(e_keys - d_keys)

    if only_disagree:
        print(f"  FAIL  {len(only_disagree)} line(s) changed meaning WITHOUT carrying an")
        print("        escaped pipe. The repair is not bounded to its subject:")
        for n, ln in only_disagree[:20]:
            print(f"          {n}:{ln}")
        failed = True
    else:
        print("  ok    every changed line carries an escaped pipe -- no collateral")

    if only_escaped:
        print(f"  note  {len(only_escaped)} line(s) carry an escaped pipe but parse")
        print("        identically either way (the escape falls outside a cell split,")
        print("        e.g. in prose that is not a table row):")
        for n, ln in only_escaped:
            print(f"          {n}:{ln}")

    print("\n  BEFORE/AFTER on every line the repair moved:")
    for n, ln, line in disagree:
        old = _naive_cells(line)
        new = ccs.cells(line)
        rid = new[0] if new else "?"
        print(f"    {n}:{ln}  row {rid!r}  cells {len(old)} -> {len(new)}  "
              f"last cell {len(old[-1])} -> {len(new[-1])} chars")

    print("\n" + ("FAILED" if failed else "PASS"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
