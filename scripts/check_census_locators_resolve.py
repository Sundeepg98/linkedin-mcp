"""Every locator into a census slice must NAME the row it is evidence for.

THE DEFECT CLASS, AND IT IS THE SIBLING GUARD'S OWN DECLARED BLIND SPOT.
`scripts/check_asserted_names_resolve.py` ends every run by printing what it
does not check. Two of the items on that list were:

    "whether a RESOLVING citation points at the right thing, and locator
     line numbers."

All the damage was inside those two. Measured 2026-09-21 over
`_audit/_census/blocker-assignments.tsv`: of the 137 `L<number>` tokens whose
source is one of the four census slices, **ZERO resolved to the row they were
evidence for**. 80 landed on a REAL BUT DIFFERENT row, 43 on a line that is not
a row, 14 blank -- and 80 + 43 + 14 is 137, which is the check that caught an
earlier draft of this paragraph quoting the compound-locator subtotal beside the
whole-population denominator. The guard was not broken. It said where it does
not look, and nobody went and looked.

WHY A LINE NUMBER CANNOT BE FIXED, ONLY REPLACED. Git says these citations were
RIGHT when they were written: blaming each TSV line to the commit that wrote it
and reading the source file AS OF THAT COMMIT, **32 of the 35 bare `L<number>`
locators landed exactly on their own row**. Nobody was careless. The census
files simply grew above the cited lines -- a near-constant per-file offset
(network.md +114, messaging-and-content.md +63, profile.md +56, jobs.md +79)
that is just the sum of every insertion made higher up since. A line number is a
pointer into a file that every edit invalidates, and it invalidates it SILENTLY,
into a plausible wrong answer.

THE REPLACEMENT WAS ALREADY IN THE FILE. `blocker-assignments.tsv` has always
carried two locator dialects. 18 of its 94 census-sourced rows cite a ROW LABEL
(`C36`, `N25`, `M6-M9 rows`); the rest cited line numbers. The row-label dialect
resolves at 18 of 18 once ranges are expanded; the line-number dialect resolves
at 0 of 137. The difference is not care. A row label is a KEY and a line number
is a POSITION, and this census has 704 rows whose labels are unique within their
slice -- measured, not assumed, by `test_a_row_label_is_a_unique_key`.

============================================================================
WHAT THIS GUARD ASKS
============================================================================

For every data row of `_audit/_census/blocker-assignments.tsv` whose `source`
is one of the four census slices: does its `locator` NAME the row the
assignment is about?

    RESOLVES          every label token names a real row in that slice, and
                      the rows they name include this assignment's own row.
    NAMES-ANOTHER-ROW every token names a real row, and NONE of them is this
                      assignment's row. This is the expensive verdict -- it is
                      a citation that resolves to the wrong thing, which stops
                      a reader instead of sending them looking.
    NO-SUCH-ROW       a token names a label that is nowhere in that slice.
    LINE-NUMBER       the locator carries a token shaped `L<number>` that names
                      no row in that slice. REFUSED rather than resolved, and
                      this verdict OUTRANKS the others: see below.
    UNREADABLE        no token could be extracted at all.

THE LINE-NUMBER REFUSAL OUTRANKS EVERY OTHER VERDICT. A locator mixing a good
row label with a stale line number is not half-right; it is a citation that will
send the next reader to the wrong place with the other half vouching for it.

WHY `LINE-NUMBER` IS A REFUSAL AND NOT A RESOLUTION. This guard could resolve a
line number -- read line N, see which row is there. The first draft did. It was
removed, because a guard that resolves line numbers makes writing new ones
FEEL safe: the citation is green today and rots on the next edit anybody makes
to the file above it, with no event to notice. The measurement above is what
that feels like at scale. So the token is refused and the message says what to
write instead -- after the label lookup has missed, never on the spelling alone,
because `profile.md` numbers eight of its own rows `L1` .. `L8`. Four locators
in this file cite those rows by label today -- `P L1`, `P L6`, `P L7`, `P L8` --
and a shape-only rule would convict all four. A guard's job here is to make the
rotting construct unwritable, not to chase it.

============================================================================
THE INDEX IS BUILT FROM THE CENSUS, NEVER FROM THE TSV
============================================================================

`row_labels()` reads the four slice files and nothing else. It deliberately
does NOT read `blocker-assignments.tsv`, `blocker-map.tsv` or any `_audit/`
prose, for the reason the sibling guard learned the hard way inside its first
hour: it shipped with a registry that read `scripts/` and `tests/`, then
absorbed the example names out of its own docstring and reported the corpus
clean. Writing ABOUT a row is not the row existing. The census slices ARE the
census; everything else is a citation of it.

`test_the_index_cannot_absorb_a_label_from_its_own_instruments` asserts that.

============================================================================
THE LOCATOR GRAMMAR, read off the file rather than invented
============================================================================

A locator is a comma-separated list of TOKENS. Trailing prose and parenthetical
annotations are the author's own words and are ignored for resolution but kept
in the report, because they are the half of the citation that does not rot --
and twice in this corpus they were the only surviving record of what a stale
line number had meant.

A token is one of:

    `57`        a bare numeric row label            (jobs.md, network.md)
    `C12`       a lettered row label                (profile, messaging)
    `18-19`     a LITERAL compound label -- a real row in a cost table whose
                own first cell reads `18-19`
    `106-115`   a RANGE over labels, expanded against the slice's own label
                order, keeping only members that really exist
    `Company pages`
                a GROUPING row, whose first cell is bold text. Matched on the
                bold text with any trailing parenthetical dropped, because
                those cells run to 40 words.

LITERAL BEFORE RANGE, AND THE ORDER IS LOAD-BEARING. `18-19` and `85-86` are
both real single rows in `jobs.md`'s cost tables AND valid ranges over its
capability rows. A token is looked up as a literal label first; the range
expansion is added, not substituted. Reversing that order silently reinterprets
a citation of one cost row as a citation of two capability rows.

    venv/Scripts/python.exe scripts/check_census_locators_resolve.py
    venv/Scripts/python.exe scripts/check_census_locators_resolve.py --all
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from typing import NamedTuple

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import count_census_states as census  # noqa: E402

#: The assignment evidence file. One file, named once.
ASSIGNMENTS = "_audit/_census/blocker-assignments.tsv"

#: repo-relative source path -> slice letter. Built from the counter's own
#: SLICES map so the two instruments cannot disagree about what a slice is.
CENSUS_SOURCES = {
    "_audit/_census/%s" % name: letter
    for letter, name in census.SLICES.items()
}

#: The shape of a line-number token, single or range: `L177`, `L406-L418`.
#:
#: SHAPE ALONE CANNOT DECIDE THIS, AND THE COLLISION IS REAL RATHER THAN
#: HYPOTHETICAL. `profile.md` section L numbers its rows `L1` .. `L8`, so the
#: token `L6` is a perfectly good ROW LABEL in that slice and a line number in
#: every other. A guard that reads the shape and stops would refuse the four
#: correct profile.md citations that use those labels and call them rot.
#:
#: So KIND IS DECIDED FROM THE DATA, NOT THE SPELLING: a token is looked up in
#: the slice's own label index FIRST, and only a token that names nothing there
#: is judged by shape. `L6` resolves in profile.md and is refused in jobs.md,
#: which is exactly right, because jobs.md has no L-prefixed rows.
#:
#: THE RESIDUAL THIS LEAVES, STATED RATHER THAN HIDDEN: a genuinely stale line
#: number in the range L1-L8 pointed at `profile.md` would be read as a row
#: label and pass. That is eight lines of one file, all of them inside its
#: front matter, and no citation in the corpus points there. It is on the
#: `NOT checked:` line.
_LINE_SHAPE = re.compile(r"^L\d+(?:-L?\d+)?$")

#: A label splits into (prefix, number) for range expansion. `C12` -> (C, 12).
#: THERE IS DELIBERATELY NO "IS THIS A LABEL" PATTERN. An earlier draft had one
#: and it was dead code within an hour: a label is whatever the slice's own
#: index holds, so a pattern describing label SHAPE can only ever disagree with
#: the data, and a guard that carries two answers to one question will
#: eventually use the wrong one.
_SPLIT = re.compile(r"^([A-Za-z]{0,2})(\d+)$")


class Index(NamedTuple):
    """One census slice's row labels, and which of them carry a state."""

    letter: str
    #: every table-row label -> the lines it appears on
    labels: dict[str, list[int]]
    #: the STATED capability rows only -- label -> line. Unique by measurement.
    stated: dict[str, int]


class Finding(NamedTuple):
    """One assignment row, with the verdict its locator earned."""

    row_id: str
    blocker: str
    source: str
    locator: str
    verdict: str
    named: tuple[str, ...]      # the row labels the locator resolved to
    detail: str

    def __str__(self) -> str:
        return "%-9s %-28s %-44s [%s]" % (
            self.row_id, self.blocker, self.locator[:44], self.verdict)


def _bold_label(cell: str) -> str:
    """The stable part of a grouping row's first cell.

    `**Conversation management** (archive, restore, mute, ...)` runs to eleven
    words of parenthetical. The bold text is the part an author would cite and
    the part that does not move, so it is what this matches on.
    """
    bare = cell.replace("**", "").strip()
    cut = bare.find("(")
    if cut > 0:
        bare = bare[:cut]
    return bare.strip()


def row_labels(repo: pathlib.Path) -> dict[str, Index]:
    """The label index for all four slices, read from the slices themselves."""
    out: dict[str, Index] = {}
    for letter, name in census.SLICES.items():
        text = (repo / "_audit" / "_census" / name).read_text(
            encoding="utf-8", errors="replace")
        out[letter] = build_index(text, letter)
    return out


def build_index(text: str, letter: str) -> Index:
    """Index one slice's markdown. A PURE FUNCTION, deliberately.

    The control in `tests/test_a_census_locator_names_its_row.py` builds a
    MANUFACTURED census -- thirteen hand-written lines carrying six labelled
    rows, with their true line numbers written beside them -- and pushes it
    through this exact function. A control that finds its fixture in ambient
    repo state passes on the box it was written on and fails in every clone;
    this one carries its fixture with it.
    """
    labels: dict[str, list[int]] = {}
    stated: dict[str, int] = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = census.cells(line)
        if len(cells) < 3:
            continue
        if cells[0] and set(cells[0]) <= set("-: "):
            continue
        label = _bold_label(cells[0])
        if not label or label.lower() in census.HEADERS:
            continue
        labels.setdefault(label, []).append(lineno)
        state, _dialects = census.classify(cells)
        if not state and letter == "N" and re.fullmatch(r"A\d+", cells[0]):
            # network.md's admin-only table carries no state column; its own
            # prose says all fifteen are GAP. Mirrors count_census_states.
            state = "GAP"
        if state:
            stated.setdefault(label, lineno)
    return Index(letter, labels, stated)


def expand(token: str, index: Index) -> list[str]:
    """Every row label `token` names in `index`. LITERAL FIRST, then range.

    Returns [] when it names nothing, which is how NO-SUCH-ROW is reached.
    """
    found: list[str] = []
    if token in index.labels:
        found.append(token)
    if "-" in token:
        lo, _, hi = token.partition("-")
        a, b = _SPLIT.match(lo), _SPLIT.match(hi)
        if a and b and a.group(1).upper() == b.group(1).upper():
            prefix = a.group(1)
            first, last = int(a.group(2)), int(b.group(2))
            if first <= last and last - first < 200:
                for n in range(first, last + 1):
                    member = "%s%d" % (prefix, n)
                    if member in index.labels and member not in found:
                        found.append(member)
    return found


def tokens(locator: str) -> list[str]:
    """The label tokens in a locator, with annotations stripped.

    A comma inside a parenthetical is not a token separator, so the
    parentheticals go first. `L498 (group of 11), L366 (M35 row)` would
    otherwise split into four.
    """
    stripped = re.sub(r"\([^)]*\)", " ", locator)
    out: list[str] = []
    for piece in stripped.split(","):
        piece = piece.strip()
        # trailing prose the corpus writes after a token: `M6-M9 rows`
        piece = re.sub(r"\s+rows?$", "", piece.strip())
        if piece:
            out.append(piece)
    return out


def assignments(repo: pathlib.Path) -> list[tuple[str, ...]]:
    """The TSV's data rows. Commentary (`>`) and the header are not data."""
    text = (repo / ASSIGNMENTS).read_text(encoding="utf-8", errors="replace")
    rows: list[tuple[str, ...]] = []
    header_seen = False
    for line in text.splitlines():
        if line.startswith(">") or not line.strip():
            continue
        fields = tuple(line.split("\t"))
        if not header_seen and fields[0] == "blocker":
            header_seen = True
            continue
        rows.append(fields)
    if not header_seen:
        raise RuntimeError(
            "%s has no `blocker<TAB>row_id<TAB>...` header line. Refusing to "
            "run: without it the first data row is silently eaten, and this "
            "guard would report one fewer finding than there are."
            % ASSIGNMENTS)
    return rows


def resolve(row_id: str, locator: str, index: Index) -> tuple[str, tuple[str, ...], str]:
    """(verdict, the labels named, detail) for one locator."""
    bare = row_id.split(" ", 1)[1] if " " in row_id else row_id
    toks = tokens(locator)
    if not toks:
        return ("UNREADABLE", (), "no token could be extracted")
    named: list[str] = []
    unknown: list[str] = []
    lines: list[str] = []
    for tok in toks:
        hits = expand(tok, index)
        if hits:
            named.extend(h for h in hits if h not in named)
        elif _LINE_SHAPE.match(tok):
            lines.append(tok)
        else:
            unknown.append(tok)
    # THE LINE-NUMBER REFUSAL OUTRANKS EVERY OTHER VERDICT, deliberately. A
    # locator that mixes a good row label with a stale line number is not
    # half-right; it is a citation that will send the next reader to the wrong
    # place with the other half vouching for it.
    if lines:
        return ("LINE-NUMBER", tuple(named), (
            "carries %s, a line number into this slice. A line number is a "
            "POSITION: every edit above it moves the row without moving the "
            "number, and it rots into a REAL BUT DIFFERENT row rather than "
            "into an error. Cite the row label instead -- `%s`."
            % (", ".join(lines), bare)))
    if unknown:
        return ("NO-SUCH-ROW", tuple(named),
                "names %s, which is no row in this slice" % ", ".join(
                    repr(u) for u in unknown))
    if bare in named:
        return ("RESOLVES", tuple(named), "")
    return ("NAMES-ANOTHER-ROW", tuple(named),
            "resolves to %s, none of which is %s" % (", ".join(named), bare))


def run(repo: pathlib.Path) -> tuple[list[Finding], list[Finding]]:
    """(every in-subject finding, the ones that are not RESOLVES)."""
    index = row_labels(repo)
    out: list[Finding] = []
    for fields in assignments(repo):
        if len(fields) < 5:
            continue
        blocker, row_id, _ev, source, locator = fields[:5]
        letter = CENSUS_SOURCES.get(source)
        if letter is None:
            continue
        verdict, named, detail = resolve(row_id, locator, index[letter])
        out.append(Finding(row_id, blocker, source, locator, verdict, named,
                           detail))
    bad = [f for f in out if f.verdict != "RESOLVES"]
    return out, bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true",
                    help="print every in-subject row, not only the findings")
    args = ap.parse_args(argv)

    every = assignments(ROOT)
    found, bad = run(ROOT)

    if args.all:
        for f in sorted(found, key=lambda x: (x.source, x.row_id)):
            print(f)
            if f.named:
                print("        names: %s" % ", ".join(f.named))
        print()

    out_of_subject = len(every) - len(found)
    print("assignment rows in the file : %d" % len(every))
    print("in subject (census source)  : %d" % len(found))
    print("locator NAMES its own row   : %d" % (len(found) - len(bad)))
    print("does not                    : %d" % len(bad))
    # A guard must say what it did NOT check, every time, or its PASS is a
    # half-truth. These two lines are that statement, and the count is printed
    # rather than described so that a change in scope is visible as a number.
    print("NOT checked: the %d assignment rows whose source is NOT a census "
          "slice (a ledger, a probe script, a server module) -- this guard "
          "holds no row index for those files; whether a RESOLVING locator's "
          "row actually SUPPORTS the assignment; a stale line number in the "
          "range L1-L8 aimed at profile.md, which collides with that slice's "
          "own row labels; and the `note` column's own prose citations."
          % out_of_subject)
    if not bad:
        print("\nevery census locator names the row it is evidence for.")
        return 0
    print()
    for f in bad:
        print(f)
        print("        %s" % f.detail)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
