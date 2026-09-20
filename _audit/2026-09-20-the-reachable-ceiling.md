# The census is not one schema, and 171 of the answerable GAP rows are writes

**2026-09-20, integrator. Measured through the shipped parser
(`scripts/count_census_states.py`), over the four census slices at master
`fd81f4e`.**

**CORRECTED BY:** `_audit/2026-09-21-the-jobs-direction.md` -- the `no direction column` cell for the jobs slice is right about its per-row tables and wrong about the file, because section 2 of that slice IS a direction table keyed by ROW-RANGE rather than by row id; its 57 GAP rows are now classified per row as **R 29 / W 25 / R/W 2 / AMBIGUOUS 1**, the `300 GAP rows` denominator above measures 285 at HEAD so the 242-row answerable population must be RE-TAKEN before anything adds the jobs split to it, and jobs measures read-heavy at 29 of 57 (50.9%) against the non-jobs 70 of 242 (28.9%).

## THE RE-TAKE THE CORRECTION ABOVE ASKS FOR, done 2026-09-21 at master `5e9802d`

That marker says the 242-row answerable population must be re-taken before
anything adds the jobs split to it. **It has been.** The table further down is
left exactly as written, because a number in a record is evidence of what was
true when it was written; this section is the current reading beside it, not a
replacement for it.

Re-derived through the same shipped parser over the three slices that carry a
per-row direction cell, then combined with the per-row jobs classification from
`_audit/2026-09-21-the-jobs-direction.md`:

| direction | profile + messaging + network | jobs | total |
|---|---:|---:|---:|
| **W** | 157 | 25 | **182** |
| **R** | 69 | 29 | **98** |
| R/W | 1 | 2 | 3 |
| unclassified | 1 | 1 | 2 |
| | | | **285** |

**The sum is 285, which is the census total at HEAD, and that agreement is the
only reason this combination is trusted at all.** It joins two measurements
taken hours apart; the day before, a coincidence of cardinality between two
sets of 22 was read as set identity and cost an hour, so a combined figure that
did not reconcile exactly would have been discarded rather than explained.

**So roughly 64% of the remaining GAP is write-direction**, and the ceiling
argument survives the correction intact — what changed is that jobs is
read-heavy (29 of 57) against the non-jobs slices (69 of 228), which localises
where the readable remainder lives rather than enlarging it.

**TWO HONESTY NOTES ON THIS TABLE.** The single unclassified messaging row is an
artifact of the integrator's own crude extractor, which matches an exact cell
value; the wave that owns that slice classified all of its rows and found no
unreadable cell. And the jobs `AMBIGUOUS` row is `J 148`, left undecided on
purpose: its section argues nothing is sent, and nobody has measured whether a
refinement persists to the copy LinkedIn stores.

## The reading

Of **300 GAP rows**, direction splits as follows — stated over the population
that can answer, not over all 300:

| slice | R | W | R/W | no direction column |
|---|---:|---:|---:|---:|
| `profile.md` | 17 | 45 | 1 | 0 |
| `messaging-and-content.md` | 11 | 71 | 0 | 1 |
| `network.md` | 42 | 55 | 0 | 0 |
| `jobs.md` | — | — | — | **57** |
| **total** | **70** | **171** | **1** | **58** |

**Of the 242 GAP rows that carry a direction, 171 — just over 70% — are
writes.**

## WHY THAT MATTERS: it is a ceiling, not a backlog

This server is read-only by design. `writes_enabled()` is `False`, apply,
connect and InMail were deliberately cut, and the first write round was scoped
to reversible actions behind an off-by-default flag. **A write-direction GAP row
is not work waiting to be done; it is a capability this product has ruled
itself out of.**

So "GAP 300" reads as an enormous backlog and is not one. The reachable
population under the current posture is **70 reads and one R/W**, plus whatever
the 57 unclassified jobs rows turn out to be. That is a different campaign from
the one the headline number describes, and the difference is the kind of thing
that should steer which waves get launched.

**This does not say the 171 are correctly GAP rather than EXCLUDED-RULED.** It
says nobody has ruled them, which is its own finding: a row that is
unreachable-by-design and still filed GAP inflates the denominator every time
anyone quotes it. Whether they should be ruled, and under what wording, is a
census decision and is not taken here.

## THE 58 ARE A SCHEMA FACT, NOT A PARSER FAILURE

`jobs.md` **has no direction column**. Its tables are:

```
| # | capability | source | state | tool, or the repo's own reason |
```

Five columns, no `R/W`. The other three slices carry one. So the 57 jobs GAP
rows are not missing data and not a parse error — **they were never asked the
question**, and any instrument that assumes a uniform schema will report them
as unknown or, worse, silently skip them.

**This is the second schema divergence found in the census today.** A sibling
measurement found **21 rows in `network.md` with no reason cell at all**, in two
contiguous blocks under a **four**-column header (`| # | capability | R/W |
state |`) where the reason is embedded inside the state cell as
`EXCLUDED-RULED (R11)`.

So the corpus contains **at least three distinct table shapes**:

| shape | columns | seen in |
|---|---|---|
| A | `# / capability / source / state / reason` | `jobs.md` |
| B | `# / capability / R/W / state / reason` | profile, messaging, network |
| C | `# / capability / R/W / state` | two blocks of `network.md` |

**AN INSTRUMENT THAT ASSUMES ONE SHAPE FAILS QUIET ON THE OTHERS** — returning
`?`, or an empty string, or the wrong cell. The existing parser survives this
only because it searches for a recognised *state word* by content rather than
reading a fixed column index, which is the right design and is why the state
counts are trustworthy while a direction count is not.

That generalises past this repo: **a heterogeneous corpus silently punishes
positional parsing and rewards content-addressed parsing.** Every census figure
should say which shapes it could read.

## What is claimed, and what is not

- **CLAIMED:** the direction counts above, over the 242 rows that carry a
  direction column, re-derivable by running the shipped parser over the four
  slices at `fd81f4e`.
- **NOT CLAIMED:** anything about the 57 jobs GAP rows' direction. They are
  unmeasured on this axis, not zero and not reads.
- **NOT CLAIMED:** that the 171 are correctly filed. Only that they are filed
  GAP and are write-direction.
- **NO INSTRUMENT IS ADMITTED.** This was a reading, not a check, and nothing
  here has been shown failing.
