"""Enumerate census rows whose CAPABILITY cell names more than one act.

WHY THIS EXISTS. A row that names two capabilities publishes ONE direction
cell, ONE state cell and ONE reason cell for both of them, so whichever half
loses the coin toss is invisible to every sweep that reads those cells. This
was measured on `M C85` -- *"Vote in a poll / view poll results"* -- which
publishes `W` for a pair whose second half is a READ, and was therefore absent
from the write-direction sweep that built the backlog AND from every read
sweep, because the census says it is a write.

WHAT IT IS AND IS NOT. It is a TRIAGE NET, not a classifier. It reports every
row whose capability text carries a conjunction, because "two capabilities" is
a semantic property and no regex decides it. Its output is a candidate list a
human adjudicates; its value is that the list is CLOSED and reproducible, so a
later reader can check that a verdict was given to every member rather than to
the ones somebody remembered.

THE THREE THINGS IT CANNOT SEE, stated so the list is not read as complete:

  1. AN IMPLICIT PAIR. A row naming one act whose surface also serves another
     -- `P L2` was *"Own follower count"*-shaped prose covering count AND list
     -- carries no conjunction and does not appear here. This is the class the
     one existing split came from, so the net misses the precedent's own case.
  2. A PAIR SPLIT ACROSS CELLS. A row whose capability names one act while its
     REASON cell discusses a second is invisible: only cell[1] is read.
  3. A CONJUNCTION THIS NET DOES NOT SPELL. The markers are enumerated in
     `MARKERS` and printed on every run for exactly that reason.

AND IT OVER-REPORTS BY DESIGN. *"Filter by location, company, school and
industry"* is ONE act over four facets and trips three markers. Over-reporting
is the correct failure direction for a net whose output is adjudicated.

    ./venv/Scripts/python.exe scripts/_census_compound_rows.py
    ./venv/Scripts/python.exe scripts/_census_compound_rows.py --markers-only

THE DIRECTION COLUMN IS NOT UNIVERSAL AND THIS PRINTS THAT. `profile.md`,
`network.md` and `messaging-and-content.md` publish a per-row R/W cell;
`jobs.md` publishes NONE -- its columns are `# | capability | source | state |
reason`. So for every jobs row the direction is reported as `-`, and any rule
phrased as a test on direction divergence cannot be evaluated on that slice at
all. That is a fact about the corpus, not a limit of this script.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import reader_closable_blockers as rcb  # noqa: E402
from count_census_states import (  # noqa: E402
    CENSUS,
    HEADERS,
    ROW,
    SLICES,
    cells,
    classify,
)

#: Which slices publish a per-row direction at all. `jobs.md`'s capability
#: tables run `# | capability | source | state | reason` and carry NONE; its
#: direction lives in a separate section-2 table keyed by ROW RANGE, which
#: `scripts/_check_jobs_range_directions.py` reads and which resolves only part
#: of the slice. So a rule phrased as a test on a row's direction cell cannot
#: be evaluated on 186 of the 785 rows here -- a fact about the corpus, not a
#: limit of this script.
HAS_DIRECTION = {"J": False, "P": True, "M": True, "N": True}

#: Every conjunction this net spells. Printed on every run so a reader can see
#: what it does NOT spell without reading the source.
MARKERS = (
    ("slash", re.compile(r"\S\s*/\s*\S")),
    ("or", re.compile(r"\bor\b", re.I)),
    ("and", re.compile(r"\band\b", re.I)),
    ("comma", re.compile(r",")),
    ("then", re.compile(r"\bthen\b", re.I)),
    ("plus", re.compile(r"\+")),
)

#: THE DIRECTION IS READ BY THE SHIPPED READER, NOT BY A REGEX WRITTEN HERE.
#: The first version of this file matched `^(R|W|R/W|W/R|RW)$` against a cell
#: found by COLUMN INDEX and reported `M M28` -- whose cell reads `R+W` -- as
#: `?`. Two defects in four lines: a spelling the corpus uses that the regex
#: did not, and an index-based finder that breaks on the messaging layout.
#: `reader_closable_blockers.direction_of` already solves both, is value-based
#: rather than positional, normalises five spellings of "both" onto `R+W`, and
#: ships with a negative control. Importing it also means this net cannot
#: disagree with the triage instruments about what a row's direction IS.

#: THE VERB LEXICON, hand-authored FROM the measured leading-word distribution
#: of all 785 capability cells and printed on every run so it can be argued
#: with rather than trusted. Every entry below leads at least one census row.
#: It is deliberately NOT derived automatically: "leading word" also yields
#: `company`, `premium`, `profile`, `own`, `real`, `how` and `which`, which are
#: not acts, and a net that silently swallowed those would report the noun
#: phrases as capability pairs.
VERBS = frozenset("""
accept add apply attach block cancel change choose copy create decline delete
deselect disconnect dismiss download edit endorse enter export filter find
follow forward generate hide ignore import invite leave list manage mark
mention message mute open opt pin post print react read receive recommend
remove rename reorder reply report request re-run rerun restore resume retract
save schedule search see select send set share sort start stop subscribe
switch tag toggle turn unblock unfollow unhide unmute unsave unsend
unsubscribe update upload view vote withdraw write
""".split())

#: A conjunction that can join two VERB PHRASES. `,` is excluded on purpose:
#: measured, every comma in a census capability cell separates FACETS of one
#: act (*"by location, company, school and industry"*), never two acts, so
#: admitting it would have added 100+ rows of pure noise to the candidate set.
_JOINER = re.compile(r"\s*(?:/|\bor\b|\band\b|\bthen\b)\s*", re.I)

#: Parenthesised text is STRIPPED before the verb-pair test. The measured
#: reason: *"Filter: Date posted (24h / week / month / any)"* is ONE act whose
#: parenthetical enumerates the FILTER'S VALUES, and this shape is the single
#: largest source of false candidates in the corpus.
_PARENS = re.compile(r"\([^)]*\)")


def _verb(word: str) -> bool:
    return word.strip("`*\"'.,:;").lower() in VERBS


def verb_pairs(text: str) -> list[str]:
    """The joiners in `text` that have a VERB on the left and a VERB immediately
    on the right -- i.e. the *"create / delete a thing"* shape.

    THE RIGHT-HAND TEST IS POSITIONAL AND THE LEFT-HAND TEST IS NOT, and the
    asymmetry is deliberate. *"Vote in a poll / view poll results"* puts its
    left verb five words back, so a positional left test would miss it; but
    *"...post or comment"* would be admitted by a loose right test, because
    `post` is a verb elsewhere in this corpus. Requiring the right-hand verb to
    be the FIRST word after the joiner is what discriminates the two.
    """
    bare = _PARENS.sub(" ", text)
    found = []
    for m in _JOINER.finditer(bare):
        left = bare[:m.start()].split()
        right = bare[m.end():].split()
        if not left or not right:
            continue
        if any(_verb(w) for w in left) and _verb(right[0]):
            found.append(m.group(0).strip() or "/")
    return found


def direction_of(letter: str, row_cells: list[str]) -> str:
    """The row's published direction, or '-' when the slice publishes none.

    `unknown` and `ambiguous` come straight from the shipped reader and are
    printed as it spells them -- a row whose direction cell the corpus's own
    instruments cannot read is exactly the thing worth seeing.
    """
    if not HAS_DIRECTION[letter]:
        return "-"
    return rcb.direction_of(row_cells)


def capability_rows() -> list[tuple[str, str, str, str, str, str]]:
    """Every census capability row, as (slice, id, capability, dir, state, reason).

    Row admission is DELEGATED to the shipped counter's own predicates -- the
    same `ROW` regex, the same `HEADERS` set, the same `cells()` -- so this
    enumerator cannot disagree with `count_census_states.py` about what a row
    is. A net built on its own idea of a row would report on a population no
    published count describes.
    """
    out = []
    for letter, name in SLICES.items():
        path = CENSUS / name
        for line in path.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
            if not line.startswith("|"):
                continue
            c = cells(line)
            if len(c) < 3:
                continue
            if c[0] and set(c[0]) <= set("-: "):
                continue
            if not ROW.match(line) or c[0].lower() in HEADERS:
                continue
            state, _ = classify(c)
            if not state and letter == "N" and re.fullmatch(r"A\d+", c[0]):
                state = "GAP"
            out.append((letter, c[0], c[1], direction_of(letter, c),
                        state, c[-1]))
    return out


def markers_on(text: str) -> list[str]:
    return [nm for nm, rx in MARKERS if rx.search(text)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--markers-only", action="store_true",
                    help="print the marker list and exit")
    ap.add_argument("--marker", default="",
                    help="report only rows tripping this marker")
    ap.add_argument("--verb-pairs", action="store_true",
                    help="the SHARP net: a joiner with a verb on both sides")
    args = ap.parse_args(argv)

    print("MARKERS THIS NET SPELLS: " + ", ".join(nm for nm, _ in MARKERS))
    print("A conjunction absent from that list is INVISIBLE here.")
    if args.verb_pairs:
        print("VERB LEXICON (" + str(len(VERBS)) + "): "
              + " ".join(sorted(VERBS)))
        print("A verb absent from that list is INVISIBLE to the sharp net.")
    if args.markers_only:
        return 0

    rows = capability_rows()
    if args.verb_pairs:
        hits = [(r, verb_pairs(r[2])) for r in rows]
    else:
        hits = [(r, markers_on(r[2])) for r in rows]
    hits = [(r, m) for r, m in hits if m]
    if args.marker:
        hits = [(r, m) for r, m in hits if args.marker in m]

    per_slice: dict[str, int] = {}
    for (letter, *_), _m in hits:
        per_slice[letter] = per_slice.get(letter, 0) + 1

    print(f"\n{len(rows)} capability rows read; {len(hits)} carry a marker.")
    for letter in SLICES:
        total = sum(1 for r in rows if r[0] == letter)
        print(f"  {letter}  {per_slice.get(letter, 0):3d} of {total:3d}")

    print("\nslice  id      dir  state                   capability")
    for (letter, rid, cap, drn, state, _reason), marks in hits:
        print(f"  {letter}  {rid:<7s} {drn:<4s} {state or '(none)':<22s} "
              f"{cap[:90]}   [{','.join(marks)}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
