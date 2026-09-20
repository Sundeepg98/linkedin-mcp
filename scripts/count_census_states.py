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
capability DENOMINATOR is 704 rows + 59 collapsed - 2 stateless = 761 -- the 705
was a typo, the expression evaluated to 762 and did not match its own stated
total. RE-DERIVED 2026-09-19 against the file: rows 704, collapse +58 (`O6-O20`
15-in-1 = +14, the `P-R` SECTION 45-in-1 = +44), so today's tree gives 760. The
one-capability gap is drift and 761 is deliberately NOT changed here. While the
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

TWO CAUSES WEARING ONE COSTUME, AND ONLY ONE OF THEM IS THE CENSUS'S FAULT.
`--unstated` collapses PROSE (the census wrote a sentence where a state goes --
a defect in the row) with DIALECT (the census wrote a state this counter does
not speak -- a defect in THIS FILE). They need opposite fixes and they were
reported identically, which is how `XR` survived a fortnight and how
`CANNOT-DELIVER` survived the freeze. So a dialect is now a REFUSAL rather than
an empty string: `state_of` RAISES `UnknownStateDialect`, `--unstated` keeps
only the prose class, and a dialect fails the run under its own heading.

WHAT A DIALECT IS, STATED SO IT CAN BE ARGUED WITH. A cell is a dialect when it
is ENTIRELY a verdict -- one to three shouted words, nothing else in the cell --
and every word it is built from is a word the shipped vocabulary is built from,
yet the combination is not in the vocabulary. `**CANNOT-DELIVER**` qualifies:
CANNOT and DELIVER are both `COVERED-CANNOT-DELIVER`'s own words. A prose cell
does not qualify (`**MEASURED AND DELIBERATELY NOT CLOSED ...**` on `N 174` is
four words and AND is not a vocabulary word), and neither does a NEIGHBOURING
vocabulary -- `mcp-inventory.md` runs `PROVEN-LIVE` / `TESTED-ONLY` /
`KNOWN-BROKEN`, which share no complete word set with this one and are not
counted here at all. MEASURED over all 61 commits that ever touched the four
counted slices: the rule fires on exactly two rows in the whole history of this
census, `M M1` and `M M2`, and on nothing at HEAD.

THE BLIND SPOT IS NAMED RATHER THAN HIDDEN: the dialect scan reads the SAME
cells `state_of` reads, `row_cells[1:]`. A dialect written into a row's FIRST
cell is invisible to both, because that is where the summary tables put the
state as a ROW LABEL (`| GAP | 99 | 66.0% |`) and firing there would flag every
slice's own roll-up.
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
    "CANNOT-DELIVER",
}
#: `CANNOT-DELIVER` is the SECOND dialect this counter was taught, admitted
#: 2026-09-19 on the same principle as `XR` and for a worse reason. It is
#: `messaging-and-content.md`'s own first spelling of COVERED-CANNOT-DELIVER,
#: and it cost TWO rows -- `M M1` "Send a message to a 1st-degree connection"
#: and `M M2` "Send an InMail to a non-connection" -- their membership of the
#: census for the whole window 2026-09-03..2026-09-05 (11 commits), including
#: the freeze at `1c08e5f` that the number 409 is taken from. MEASURED, not
#: inferred: the frozen census enumerates 692 stated rows with this spelling
#: admitted and 690 without, and the GAP count is 409 either way -- the two rows
#: were CANNOT-DELIVER, never GAP, so the 409 does not move and is not touched.
#: `02e617d` (2026-09-05) rewrote both cells to the long spelling, which is why
#: HEAD reads 0 dialects and why this entry only ever matters to a reader of
#: history -- and a census whose own frozen denominator cannot be recomputed is
#: exactly the disease this script was written against.
#:
#: IT IS REPORTED UNDER ITS OWN KEY, never folded into COVERED-CANNOT-DELIVER,
#: for the reason `XR` is: a counter that silently merges two spellings cannot
#: show you that a slice used two.

#: Every word the shipped vocabulary is built from. A cell assembled only out of
#: these, in a combination the vocabulary does not hold, is a MISSPELLED STATE
#: rather than a different kind of cell -- which is the whole discrimination.
STATE_ATOMS = frozenset(atom for state in STATES for atom in state.split("-"))
#: A verdict is SHOUTED and has no lowercase in it. Anything with a lowercase
#: letter, a comma, a full stop or a backtick-wrapped identifier is prose.
_SHOUTED_WORD = re.compile(r"^[A-Z][A-Z0-9-]*$")


class UnknownStateDialect(Exception):
    """A state cell is spelled in a dialect this counter does not speak.

    RAISED RATHER THAN SWALLOWED because the alternative was measured: an empty
    string from `state_of` removes the row from the NUMERATOR and the
    DENOMINATOR at the same instant, with no error, no diff that looks like a
    state change, and no way for any downstream artifact to notice. Every
    caller that wants to report several at once calls `classify` instead and
    says so; a caller that does nothing special gets the refusal.
    """

    def __init__(self, spelling: str, cell: str) -> None:
        super().__init__(
            f"census state cell {cell!r} spells a state as {spelling!r}, which "
            f"is not in the shipped vocabulary {sorted(STATES)}. This row is in "
            f"NEITHER the numerator NOR the denominator until it is resolved. "
            f"THE FIX IS USUALLY THIS FILE, NOT THE ROW: if the spelling is a "
            f"real state, add it to STATES under its own key with the receipt, "
            f"as `XR` and `CANNOT-DELIVER` are. Rewrite the census row only if "
            f"the spelling is a mistake nobody meant."
        )
        self.spelling = spelling
        self.cell = cell


def dialect_of(cell: str) -> str:
    """The misspelled state in `cell`, or '' if the cell is not one.

    Returns '' for every cell that carries a RECOGNISED state, so this answers
    only "is this a state spelled wrong", never "is this a state".
    """
    bare = cell.replace("`", "").replace("*", "").strip()
    words = bare.split()
    if not words or len(words) > 3:
        return ""
    if not all(_SHOUTED_WORD.match(w) for w in words):
        return ""
    joined = "-".join(words)
    if joined in STATES:
        return ""
    if all(atom in STATE_ATOMS for atom in joined.split("-")):
        return joined
    return ""
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


#: The markdown escape for a literal pipe INSIDE a table cell. GFM says a
#: backslash-pipe is content, not a column break, and this corpus uses it:
#: `readonly.py:198` enumerates `(saved|applied|draft)` on `J 50` is written
#: that way because the alternation would otherwise split the row.
_ESCAPED_PIPE = "\\|"


def cells(line: str) -> list[str]:
    """The row's cells, honouring the markdown escape for a literal pipe.

    THE DEFECT THIS REPLACED, AND WHY NO INSTRUMENT CAUGHT IT FOR A FORTNIGHT.
    The first version was `s.strip('|').split('|')`, which treats an escaped
    pipe as a column break. Four lines in the whole census carry one, all in
    `jobs.md` -- and on every one of them THE STATE CELL IS STILL READ
    CORRECTLY, because the escape always falls in the REASON, which is the last
    cell. So every count this file publishes was right, every control passed,
    and the only thing that was wrong was invisible to all of them: the reason
    came back as the TAIL AFTER the escape. `J 103` held 1322 characters and
    handed back 795. A downstream reader classifying that reason is reading
    60% of an argument and cannot tell.

    WHY THIS MATTERS MORE THAN A TRUNCATION USUALLY WOULD. The tail is not
    merely short, it is SYNTACTICALLY VALID -- it looks like a whole reason
    cell, so nothing downstream can discriminate it from one. Registered in
    `_audit/INSTRUMENTS.md` section 35 as "not an instrument" and fixed here
    with section 41's control, `scripts/_check_cells_honours_escaped_pipe.py`,
    which shows the old behaviour failing and asserts the new one changes
    NOTHING on the 4461 lines that carry no escape.

    NO REGEX, DELIBERATELY. A lookbehind for "backslash not preceded by a
    backslash" is the standard one-liner and it is wrong at a doubled
    backslash; a left-to-right scan has no such case to get wrong.
    """
    s = line.strip()
    out: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        if s.startswith(_ESCAPED_PIPE, i):
            buf.append("|")
            i += 2
            continue
        if s[i] == "|":
            out.append("".join(buf))
            buf = []
            i += 1
            continue
        buf.append(s[i])
        i += 1
    out.append("".join(buf))
    # Drop the BORDER pipes -- and only real ones. An empty first element means
    # the line opened with an unescaped `|`; an empty last element means it
    # closed with one. A line ending in an ESCAPED pipe leaves a non-empty last
    # element and keeps it, which is the whole repair.
    if len(out) > 1 and out[0] == "":
        out = out[1:]
    if len(out) > 1 and out[-1] == "":
        out = out[:-1]
    return [c.strip() for c in out]


def classify(row_cells: list[str]) -> tuple[str, list[str]]:
    """(the row's state or '', every misspelled state found in the same cells).

    The non-raising half of `state_of`, for the callers that must report EVERY
    offending row rather than die on the first. A row can return both: a state
    AND a dialect means `state_of` picked a different cell from the one the
    author wrote the verdict in, which is the masking case and the worse one.
    """
    state = ""
    dialects: list[str] = []
    for cell in row_cells[1:]:
        bare = cell.replace("`", "").replace("*", "").strip()
        head = bare.split(" ")[0]
        if head in STATES:
            if not state:
                state = head
            continue
        spelling = dialect_of(cell)
        if spelling:
            dialects.append(spelling)
    return state, dialects


def state_of(row_cells: list[str]) -> str:
    """The row's state, REFUSING on a cell whose state it cannot spell.

    Returning '' for an unreadable state cell is the defect this raise exists
    to end; '' now means one thing only -- the row carries no state cell at all,
    which is a fact about the CENSUS and is reported by `--unstated`.
    """
    state, dialects = classify(row_cells)
    if dialects:
        raise UnknownStateDialect(dialects[0], " | ".join(row_cells))
    return state


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
    refused: list[str] = []
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
            st, dialects = classify(c)
            for spelling in dialects:
                refused.append(
                    f"{letter} {c[0]} ({name} line {lineno}) spells a state "
                    f"{spelling!r}; state_of reads {st or 'NOTHING'} -- "
                    f"{c[1][:60]}")
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

    # LOUD, AND UNDER ITS OWN HEADING. A dialect is not an unstated row and
    # must never be read as one: an unstated row is a fact about the census, a
    # dialect is a fact about THIS FILE's vocabulary. Reported last so it is
    # the final thing on the terminal, and it fails the run on its own.
    if refused:
        print(f"\nREFUSED -- {len(refused)} state cell(s) spelled in a dialect "
              f"this counter does not speak. Each of these rows is in NEITHER "
              f"the numerator NOR the denominator:")
        for r in refused:
            print(f"  {r}")
        print("  Teach STATES the spelling under its own key with a receipt "
              "(as `XR` and `CANNOT-DELIVER` are), or fix the cell if nobody "
              "meant it. Do not widen the counter to guess.")
        failed = True
    if expect:
        want = sum(expect.values())
        got = totals.get("GAP", 0)
        print(f"\nGAP control: expected {want}, measured {got} -- "
              f"{'MATCH' if want == got else 'MISMATCH'}")
        failed = failed or want != got
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
