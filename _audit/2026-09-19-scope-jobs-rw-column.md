# SCOPE ONLY — the price of giving `jobs.md` the R/W column it does not have

**This is a costing, not an edit. Nothing in `jobs.md` was changed.**

The defect: `jobs.md` records read-versus-write **nowhere** — 151 rows, 0 with a
value — while the other three slices record it for 199/202, 138/143 and 208/209.
So for a fifth of the census the question *"is this a read or a write"* is
unanswerable by anyone, and it fails **as "unknown" rather than as an error**.

---

## 1. WHERE A VALUE COULD COME FROM — and the figure you must not trust

| source | rows | share |
|---|---:|---:|
| **JUDGEMENT** — nothing in the row decides it | **66** | 44% |
| FREE — a cross-slice twin already records it | 47 | 31% |
| CHEAP — the capability text opens with an unambiguous verb | 35 | 23% |
| FREE — the row's own note names write machinery | 3 | 2% |

**THE 47 IS AN UPPER BOUND AND I DO NOT BELIEVE IT.** It is derived from the
same lexical pairing whose precision I published this morning as **~7 true of 15
at the head**, and which `small-measures` measured at **1 true of 61** in
another class. 182 candidate pairs have a `jobs.md` side; if the pairing is half
wrong, so is the 47.

> **Costing this row-by-row from twins would import a known-unreliable
> instrument into a structural edit.** The honest planning number is the
> JUDGEMENT column: **at least 66 rows need a human decision, and plausibly many
> more of the 47.**

The 35 "cheap" rows are cheap only in the sense that a verb suggests a
direction. `Filter: Location` reads as R and is R; but a filter that PERSISTS a
saved search is a write, and the text does not say which. **Verb-derived values
would be a guess wearing a column**, and this census already has a name for that
failure.

## 2. BLAST RADIUS OF THE EDIT ITSELF

    151 row lines  +  14 header lines  +  14 separator lines

**Every table row in the file lands in the diff**, in a slice four waves are
writing. `jobs.md` has taken commits from at least three different waves today.

A 179-line rewrite of a contended file is the shape that has already produced
three mis-attributed commits in this repo. `--only` does not help: it protects
at FILE granularity, and this edit touches the whole file, so any neighbour
editing `jobs.md` in the same minutes is in an unavoidable race.

**Cheapest safe window: a quiescent moment, done as one commit, by whoever owns
the slice.** It is not a background task and it cannot be interleaved.

## 3. WHAT BREAKS — measured, and the answer is encouraging

| guard | position-sensitive? |
|---|---|
| `scripts/count_census_states.py` | **no** — keys on the FIRST cell and scans `row_cells[1:]` for any recognised state |
| `scripts/build_blocker_map.py` | **no** — consumes the evidence TSV and row ids |
| `tests/test_blocker_map_is_derived.py` | **no** — its `parts[0..2]` indexing parses the TSV map, not the census markdown |
| ~30 other tests that mention `_census` | **no positional cell access found** |

**And the file is already not uniform**, which is the strongest evidence that a
width change is survivable:

    jobs.md    148 rows of 5 cells, 2 of 6, 1 of 7
    network    172 rows of 5 cells, 22 of 4
    messaging  143 rows of 7
    profile    202 rows of 5

Every parser that survives `network.md`'s 22 four-cell rows already tolerates a
varying width. **I found no guard that would go red on the column being added.**

**The caveat on that:** absence of a positional read is not proof no guard
breaks — a test could pin a row's rendered text or a line count. I checked for
positional cell access and found none; I did not run the full suite against a
mutated `jobs.md`, because that would mean making the edit this scope exists to
avoid.

## 4. THE RECOMMENDATION, stated so it can be refused

**Do not fill 151 cells.** The value is not in completeness; it is in the rows
where R/W is load-bearing — a blocker's published R/W split, a read-only queue,
a boundary cost that turns on direction.

**A bounded version buys most of it:** add the column, fill only the 3
note-derived and whatever subset of the 47 a human confirms **against the twin
rather than against the score**, and leave the rest EMPTY rather than guessed.
An empty cell is honest and an inferred one is not — and this census's whole
problem with `jobs.md` today is a value that was never recorded being
indistinguishable from one that is unknown.

**The sibling finding that makes this urgent rather than tidy:** a three-column
table elsewhere in this census could not have a ruling applied to it without a
structural edit first. That is this same defect one step further along — a
missing column stops being a reporting gap and starts blocking rulings.

## 5. WHAT I DID NOT DO

No cell was added, no header changed, no row in `jobs.md` touched by this
document. **The decision is the lead's and the edit is the slice owner's**; this
is the price tag.
