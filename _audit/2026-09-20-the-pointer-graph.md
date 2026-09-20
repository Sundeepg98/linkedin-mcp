# The pointer graph

`_audit/2026-09-20-the-reason-kinds.md` found that 127 of 309 write-off reason cells are
not reasons but POINTERS, in six dialects, and that the worst of them -- the literal word
`same` -- resolves BY POSITION. This pass measures that dialect end to end, plants a row
at every insertion point it exposes, prices the obvious repair, and rules on it.

Read-only against LinkedIn. No browser, no session, no page load, no mailbox, no write
fired. Every measurement below is re-runnable offline from the committed tree.

**0 census rows were banked and no census number moved.** That is the expected result for
a notation and safety change and it is stated first, with its proof in section 5, so
nothing below reads as a re-adjudication.

---

## 0. LEAD WITH THIS

**45 write-off rows in this census can have their argument changed by an edit that never
touches them, and no instrument in this repository says a word about it.**

Measured, not argued. 71 insertion slots exist between a pointer and the row it reads its
argument from. A row planted at each in turn:

    slots planted                                        71
    slots that changed another row's published verdict   48
    (slot, row) verdict changes                         108
    DISTINCT rows whose verdict moved with no edit        45

And the other half of the receipt, which is the half that matters: on the single plant
above `P D15`, `count_census_states.py` reported the planted row honestly -- `stated rows
704 -> 705`, `EXCLUDED-RULED 267 -> 268` -- and **zero lines mentioning `P D15`, `P D16`
or `P D17`**, whose verdicts had just changed. `build_blocker_map.py --check` was
**byte-identical**. The census is loud about the row that was added and silent about the
three rows that were re-argued.

**AND THE REPAIR THE BRIEF PROPOSED WAS MEASURED AND REJECTED.** Rewriting `same` to
`same as P D14` moves three published verdicts, one of them from `US-RULING` to `UNCLEAR`
-- and buys nothing, because the resolver still resolves by position, so the cell ends up
carrying a written target that disagrees with the argument actually used. Section 4 has
the numbers. The detector shipped instead.

---

## 1. WHAT THE POSITIONAL DIALECT ACTUALLY IS

A cell is a positional pointer when its reason leads with the word `same`. It inherits the
reason of **the nearest preceding row in the same table whose own cell is substantive and
is not itself a pointer**. Nothing in the file marks a row as load-bearing for the rows
beneath it, and nothing marks a pointer as depending on one.

    POSITIONAL POINTER CELLS                                      69
      ... resolving to a donor                                    69
      ... pointing at nothing                                      0

    slice                          stated  pointers  write-off  other state
    jobs.md                           150        13         13            0
    profile.md                        203        33         25            8
    messaging-and-content.md          142        19          8           11
    network.md                        209         4          0            4
    TOTAL                             704        69         46           23

**69, not 46.** The reason-kinds pass counted 46 because it classifies write-offs. `same`
points at the row above it whatever state that row is in, so the DIALECT is 69 cells wide
and 23 of them sit at GAP or COVERED-PROVEN. Those 23 are re-pointed by exactly the same
mechanism and produce no diff in any published artifact, because no artifact states their
verdict at all. **Every count in section 0 is therefore a floor.**

**TWO INDEPENDENT METHODS, SAME NUMBER.** The measurement above imports the shipped parse
(`classify_writeoff_reasons` -> `enumerate_gap_rows` -> `count_census_states`). A child
was briefed to write its own parser from scratch, forbidden to import any of the three,
reading the slices out of the git object at `0882d35`. It returned **69**, the same
13/33/19/4 per-slice split, and the same state split (EXCLUDED-RULED 30, GAP 21, XR 13,
COVERED-CANNOT-DELIVER 3, COVERED-PROVEN 2). A shared parse is not a second opinion; this
one was, and section 7 is what it found that the shipped one could not.

### 1.1 The dialect has 36 spellings, and printing them is the point

A cell whose entire content is `same` and a cell of 4,236 characters beginning `Same.` are
the same construct to the resolver and nothing alike to a reader.

      19  'same'
       4  'same gate'
       4  'same address'
       3  'same settings-family refusal'
       2  'same allowlist and same sentence'
       2  'same measurement'          2  'same panel'          2  'same ruling'
       2  'same page'                 2  'same, plus `delete_or_withdraw_anything`'
       1  each of 26 more, including 'same key, same caveat', 'same mutation class as
          M14', 'same shape as D4: ...', and four cells over 200 characters whose
          leading `Same` is followed by the row's entire independent argument

Two of those 36 already carry the target -- `same shape as D4`, `same mutation class as
M14`. The grammar the brief proposed therefore exists in this corpus already, twice, with
BARE ids. That is the strongest argument FOR the rewrite, and section 4 is why it still
loses.

### 1.2 Fan-out: 36 rows carry the argument for 69

    donors with 1 dependent   20        heaviest donors
    donors with 2 dependents   9          P I4   carries 7  (P I5 .. P I11)
    donors with 3 dependents   3          P M1   carries 6  (P M2 .. P M7)
    donors with 4 dependents   1          J 60   carries 5  (J 61 .. J 65)
    donors with 5 dependents   1          M C13  carries 4  (M C14 .. M C17)
    donors with 6 dependents   1
    donors with 7 dependents   1

### 1.3 Read distance: how far a human walks before the argument appears

The resolver jumps straight past intervening `same` rows to the first substantive one, so
its depth is always 1 and measures nothing about the corpus. A reader's depth is not.

    1 row up  34      4 rows up   4       LONGEST: P I11 -> P I4, seven rows
    2 rows up 18      5 rows up   3         P I4   'editor never loaded'   <- the argument
    3 rows up  7      6 rows up   2         P I5   'same'
                      7 rows up   1         P I6   'same'   ... through P I10 ...
                                            P I11  'same, plus `delete_or_withdraw_anything`'

**`P I4`'s entire argument is three words.** Seven rows rest on it, and a reader who lands
on `P I11` from the blocker map walks six cells that say `same` to reach them.

### 1.4 The fragility, stated as a number

For a dependent at table position `p` whose donor sits at `d`, any substantive non-pointer
row inserted anywhere in `(d, p]` becomes the new donor. That is `p - d` insertion points
per dependent.

    distinct exposed slots                      71
    (slot, dependent) incidences               141
    worst single slot                            7 dependents re-pointed at once
                                                 (before `P I5`, profile.md line 382)

---

## 2. THE PLANTED-ROW RECEIPT

`scripts/measure_pointer_graph.py --plant "P D15"` and `--plant-sweep`. Both copy the tree
into a sandbox under the system temp directory, mutate the copy, and run the real scripts
there as subprocesses. **Nothing in the repository is written, and `linkedin_server/` is
not touched even briefly** -- several agents write that package concurrently and
`_audit/INSTRUMENTS.md` already records a wave that mutated it live and had to be ruled
against.

### 2.1 One plant, and what each instrument said about it

Planted directly above `P D15`: one row, shaped like its neighbours, carrying the reason
`PLANTED CONTROL -- mobile only, and the surface is 404` (two WORLD-FACT signals and
nothing else, so an inherited verdict changes visibly rather than possibly).

    P D15   kind US-RULING+WORLD-FACT -> WORLD-FACT   donor P D14 -> P PLANT1
    P D16   kind US-RULING+WORLD-FACT -> WORLD-FACT   donor P D14 -> P PLANT1
    P D17   kind US-RULING+WORLD-FACT -> WORLD-FACT   donor P D14 -> P PLANT1

    count_census_states.py   4 output lines changed, ALL of them the planted row:
                               stated rows 704 -> 705, EXCLUDED-RULED 267 -> 268
                             lines mentioning P D15 / P D16 / P D17:  0
    build_blocker_map.py     output BYTE-IDENTICAL
                             lines mentioning P D15 / P D16 / P D17:  0

That pair of facts is the finding. **Not that a verdict changed -- that nothing said so.**

### 2.2 The sweep, because one example proves a mechanism and a sweep measures a corpus

    slots planted                                       71
    slots that changed another row's KIND               48
    (slot, row) verdict changes                        108
    distinct rows movable without being edited          45
    write-off pointer rows that survived EVERY slot      1   -- P N31

**`P N31` is the exception that argues for the fix.** Its cell begins `same article,
different form slug ...` and then carries 456 characters of its own argument. It inherits
a donor and does not depend on one. That is the shape the other 45 do not have.

The 23 slots that re-pointed a row without moving a published verdict are not 23 safe
slots: most of them re-point a GAP or COVERED-PROVEN row, for which the classifier
publishes nothing to move. **48 of 71 is what the artifacts can see, not what happened.**

### 2.3 The instrument is shown failing

`--plant-sweep --plant-reason same` plants a cell that cannot become a donor. Every verdict
stays identical and the sweep **REFUSES, exit 1**, naming what it planted:

    REFUSED after planting 'same' at every slot: every planted row left every verdict
    identical. Either the positional dialect is gone from this census -- in which case
    this instrument is obsolete and should be deleted -- or this harness is not planting
    what it thinks it is. It is NOT reported as a pass.

An assertion satisfied by an empty result cannot fail, and a sweep that finds nothing must
not look like a sweep that found nothing wrong.

---

## 3. THE SIX DIALECTS, WITH COUNTS

Measured at `0882d35`, before this wave's edit. The `cells` column is the number of
write-off rows whose resolution goes through that dialect.

| dialect | cells | resolves to | fragile how |
|---|---:|---|---|
| **RULING CODE** `R4. NOT-REV`, `R1 + R2` | 72 | a `### R<n>` section in `network.md` | stable; the argument is in the body, not the cell |
| **BACKREFERENCE** `same`, `same gate` | 46 | the nearest preceding substantive row IN THE SAME TABLE | **BY POSITION.** 69 cells corpus-wide; sections 1 and 2 |
| **RETIREMENT** `RETIRED 2026-09-05, X (3.13)` | 38 | argument inline + `decide-retire-rulings.md` | the only queue carrying reopeners |
| **NAMED KEY** `delete_or_withdraw_anything` | ~20 | a `PERMANENTLY_FORBIDDEN` entry in `writes.py` | fine -- the key is read from the package |
| **FAMILY RULING** `/edit/ family ruling` | ~14 | a named ruling | fine |
| **SECTION HEADING** | 9 | the table's own `###` heading | **invisible to every row-level reader.** CLOSED by this wave; section 6 |

**THE `9` IN THE LAST ROW IS AN ARTEFACT OF HOW IT WAS COUNTED, AND IT IS WORTH SAYING
BECAUSE A READER WILL TRIP ON IT.** Ten rows carried their reason in that heading. The
counter buckets each row by the FIRST component of its resolution string, and `N 125`
resolves `ruling<-R5+heading<-R3` because its R/W cell already cited R5 -- so it lands in
the `ruling` bucket and the heading bucket reads 9. Measured both ways: `heading<-`
appears anywhere in **10** resolutions and first in **9**. The ten rows are named in
section 6.

---

## 4. THE DECISION ON THE POSITIONAL DIALECT

**RULED: ship the detector. Do not rewrite the 69 cells.** The brief authorised this
outcome and the argument below is measurement, not preference -- the rewrite was built,
run against the whole corpus in a sandbox, and priced on four axes before it was refused.

### 4.1 The repair as proposed, and what it costs

Insert ` as <slice> <id>` immediately after the leading `same` token of all 69 cells.

**(1) IT IS NOT CLASSIFICATION-NEUTRAL. Three published verdicts move.**

    P G3   kind  US-RULING -> UNCLEAR          signals  UR:ruling -> (none)
    P B5   kind  US-BOUNDARY+US-RULING -> US-BOUNDARY
    P B3   source rule -> inherit-backref      signals  UR:ruling -> (none)

The mechanism is exact and it is worth pausing on. `P G3`'s entire reason cell is the two
words `same ruling`. The classifier's US-RULING signal is
`\b(?:family|shipped|same|own|settings)\s+(?:ruling|refusal)\b` -- it fires on the
ADJACENCY. Rewriting the cell to `same as P G1 ruling` puts three tokens between `same`
and `ruling`, the signal stops firing, and the row falls to UNCLEAR. **A notation edit
that looked purely cosmetic moved a census verdict, and the only thing that caught it was
running the instrument before and after.**

**(2) THE TWO INSTRUMENTS THE BRIEF NAMED WOULD HAVE PASSED IT.** Both produced
byte-identical output across the rewrite -- same exit code, same sha256, same bytes.
Neither reads a reason cell. **Byte-identity on those two is necessary and not
sufficient**, and this wave found that out by building the edit rather than by reasoning
about it. Any future census notation change needs the classifier in its proof too.

**(3) IT IS REVERSIBLE.** Forward then reverse gives back the original bytes on 4 of 4
files. This is the one axis the proposal passes cleanly.

**(4) IT BUYS NO SAFETY AT ALL.** This is what settles it. Rewrite all 69 cells, then
plant the same row above `P D15`:

    P D15   the CELL now says : 'same as P D14. One official fact only: the Pro...'
            the RESOLVER used : backref<-P PLANT1
            verdict           : US-RULING+WORLD-FACT -> WORLD-FACT
    classifier exit code                              : 0
    lines of output naming P D15 / P D16 / P D17      : 0

The cell now makes a claim about where its argument comes from, the resolver uses a
different row, **and nothing compares the two.** That is strictly worse than `same`: a
wrong label that looks maintained. It is the same objection the reason-kinds wave raised
against an in-cell kind tag, and it applies to this proposal with full force.

**(5) THE COUPLING IS THE REAL DISQUALIFIER.** To buy safety, the notation needs a resolver
that prefers the written id and RAISES when it disagrees with the positional one. So the
change is not notation at all -- it is 69 cells across four files that sibling waves are
writing right now, PLUS a semantics change to an instrument shipped hours ago with 71
tests behind it, PLUS the classifier proof from (2). Three coupled changes. The brief's
test is "mechanical and reversible"; this fails on the coupling, not on any one piece.

**(6) AND IT DOES NOT READ.** 39 of the 69 cells are left ungrammatical by the single
mechanical insertion point -- `same gate` becomes `same as J 60 gate`. There is no one
insertion rule that reads correctly across 36 spellings, and choosing per-cell is a hand
edit of 69 cells, not a mechanical one.

### 4.2 What shipped instead

`scripts/measure_pointer_graph.py --pin` derives the whole graph and commits it to
`_audit/_census/pointer-graph.tsv`; `--check` re-derives it and **fails when a pinned
pointer's argument moved without that pointer being edited.**

It is DERIVED, so it tracks the cells for free and cannot rot the way a hand-written tag
rots. It covers all 69 pointers including the 23 the classifier publishes nothing for. It
touches no census cell, so it cannot conflict with a sibling wave. And it catches the
second failure mode as well as the first.

**WHY THE PIN CARRIES THE DONOR'S KIND AND NOT ITS TEXT.** There are two ways a pointer's
argument changes with no edit to the pointer: the donor is RE-POINTED, or the donor's own
reason is REWRITTEN. Pinning the donor's prose would catch the second -- and would also go
red every time a wave appends a correction to a cell, which happens here several times a
day. A guard that cries wolf gets switched off, and a switched-off guard is worse than
none. So the pin carries the CONSEQUENCE rather than the evidence.

**THE COST OF THAT CHOICE, STATED RATHER THAN HIDDEN:** a donor rewrite that changes the
ARGUMENT without changing its KIND passes this guard, and nothing here would see it. The
`--check` output says so on every green run.

### 4.3 The guard, shown failing

`scripts/measure_pointer_graph.py --selftest`, wrapped by
`tests/test_pointer_graph_guard.py` (3 tests, 26s).

| control | mutation | verdict |
|---|---|---|
| **G1 re-point** | plant one substantive row above `P D15` | **RED** -- *"P D15 was reading its argument off P D14 and now reads it off P PLANT1"* |
| **G2 donor rewrite** | replace `P D14`'s own reason, same position | **RED** -- *"P D14's verdict moved US-RULING+WORLD-FACT -> WORLD-FACT, so P D15 now rests on a different argument than when it was pinned"* |
| **G3 source goes dark** | blank all 13 of `jobs.md`'s pointers; 56 remain elsewhere | **RED** -- *"jobs.md contributed ZERO positional pointers, against 13 pinned"* |
| **G4 empty pin** | pin reduced to its header | **RED** -- *"AN ASSERTION SATISFIED BY AN EMPTY RESULT CANNOT FAIL"* |
| **G5 CALIBRATION** | whitespace into `P D15`'s capability cell | **GREEN** -- verdicts identical |

**G3 is asserted PER SLICE and that is the whole design.** With `jobs.md` dark, 56 pointers
remain in the other three -- a union assertion would pass. A union assertion over a
redundant corpus cannot detect a lost source.

**G5 is not a courtesy.** A harness where every mutation goes red is not discriminating,
it is broken, and there is no way to tell that from the red alone.

### 4.4 Three defects in my own work, every one found by running it

1. **THE SELFTEST WENT RED ON ALL FIVE CONTROLS, CALIBRATION INCLUDED.** Its sandbox is
   built with `git archive HEAD`, chosen so an uncommitted edit cannot leak into a
   measurement -- and the instrument on trial was itself uncommitted, so the sandbox did
   not contain it. Every control failed for a reason with nothing to do with the census.
   **The calibration is what convicted it**: a harness in which the control that must pass
   also fails is announcing that it is broken, and without G5 I would have read five reds
   as five successes.
2. **G3'S REFUSAL WAS COMPUTED AND NEVER PRINTED.** The per-slice check built the sentence
   *"jobs.md contributed ZERO positional pointers"*, appended it to the failure tally, and
   put it nowhere a reader could see. The run went red with a count and no cause. A
   refusal that names only what it did not match is half a measurement; this was less than
   half.
3. **A CONTROL OF MINE CLAIMED MORE THAN IT RAN.** The single-plant path printed *"WRITE-OFF
   pointer rows that survived EVERY plant unchanged: 43"* after planting exactly one row.
   43 of those rows had nothing planted near them. It now refuses to make that claim unless
   `--plant-sweep` earned it -- the same half-truth this wave is auditing the census for,
   reproduced in the instrument doing the auditing.

---

## 5. THE BEFORE/AFTER PROOF

The only census edit in this wave is section 6's ten cells. Both instruments were run on
the working tree BEFORE any edit and again after. The comparison was made on the full
sha256 of each captured stdout AND by `diff` over the bytes; the digests are abbreviated
here to their leading 20 hex characters, which is all a reader needs to re-run and match.

    scripts/count_census_states.py
      before  5697f90d9f17b48ea5f0...      after  5697f90d9f17b48ea5f0...     IDENTICAL
    scripts/build_blocker_map.py --check
      before  b7b04eb6a0cf33c17172...      after  b7b04eb6a0cf33c17172...     IDENTICAL
    byte diff on both captures: empty
    git diff --stat    1 file changed, 10 insertions(+), 10 deletions(-)

Verified twice, independently: once by the child that made the edit and once by me against
a baseline I captured before the child was briefed. `build_blocker_map.py --write` was
never run. It regenerates a tracked artifact and this wave had no business regenerating
one; `--check` only.

**AND THE CLASSIFIER, WHICH SECTION 4.1 IS WHY.** All 309 write-off rows compared field by
field against the pre-edit tree:

    row / state / kind / contingent / has_reopener / has_reason_cell   IDENTICAL, 309 of 309
    source        N 119 .. N 128   inherit-heading -> inherit-ruling   (10 rows)
    resolution    N 119 .. N 128   heading<-R3     -> ruling<-R3+heading<-R3
                  N 125            ruling<-R5+heading<-R3 -> ruling<-R3+ruling<-R5+heading<-R3

Nothing else in the file moved. **That delta IS the deliverable of section 6**: the
citation moved from a place no row can see into a place every row-level reader reaches.

---

## 6. THE SECTION-HEADING DIALECT: NAMED, AND CLOSED

**The brief said report-don't-fix, on the premise that moving a reason out of a heading is
an adjudication. A child refuted the premise and the campaign lead reversed the ruling
mid-wave.** The grammar was not invented here; it was found, already in use at scale, in
the same file.

`network.md` line 394: `### K. Recommendations (10) -- all EXCLUDED-RULED under R3`. The
table beneath it ships four columns -- `| # | capability | R/W | state |` -- with no note
column, so there was nowhere to put the attribution. All ten rows carried a capability, a
state, and no argument whatsoever.

**The ten rows, all verbatim EXCLUDED-RULED with no citation before this wave:**

    N 119  Request a recommendation from a 1st-degree connection
    N 120  Write and send a recommendation for a 1st-degree connection
    N 121  Accept a received recommendation onto your profile
    N 122  Dismiss a recommendation you received
    N 123  Ask for a revision of a recommendation you received
    N 124  Revise a recommendation you have given
    N 125  Delete a recommendation you have sent            (R/W cell reads `W (also R5)`)
    N 126  Hide or unhide a recommendation you received
    N 127  Set the visibility of a recommendation you have given
    N 128  Decline a recommendation request someone sent you

**WHAT EACH ONE NEEDED, and why the cheaper of the two options was taken.** Two mechanical
options existed and both are proven in use in this same file:

- **Option A -- inline in the existing state cell.** Section G's table is the IDENTICAL
  four-column shape with no note column, and writes `EXCLUDED-RULED (R11)` on 11 rows and
  `EXCLUDED-RULED (R11 + R2)` on three. Touches ten cells and nothing else.
- **Option B -- add a fifth `note` column**, mirroring section J. Touches the header, the
  separator and all ten rows.

**Option A was taken.** Fewer moving parts in a file where a marker in the wrong place
once made `build_blocker_map.py` read zero rows and every blocker come back unknown.

**THE FACT THAT MAKES IT SAFE, VERIFIED ON DISK BEFORE THE EDIT RATHER THAN ASSUMED.** The
shipped parser reads all three of these as the identical state:

    'EXCLUDED-RULED'              -> 'EXCLUDED-RULED'
    'EXCLUDED-RULED (R3)'         -> 'EXCLUDED-RULED'
    'EXCLUDED-RULED (R11 + R2)'   -> 'EXCLUDED-RULED'

and `dialect_of` never sees the cell, because `classify` takes the first token and moves
on. So the edit is census-neutral by construction, which is what section 5's byte-identity
then confirms rather than discovers.

**THE TWO TRAPS A NAIVE EDIT WOULD HAVE SPRUNG, both honoured:**

1. **`N 114` cites R3 IN ORDER TO DISCLAIM IT.** Its state is GAP, not EXCLUDED-RULED, and
   its note reads *"R3 governs endorsing others, not managing what he received. Nothing
   written covers the receiving side."* A string match on the token `R3` files it as an R3
   row when the file says the reverse. **Rows were selected by section membership -- the
   consecutive block 119-128 under the section-K heading -- never by token.** `N 114` is
   untouched; `git diff` carries zero lines for it.
2. **`N 125` already carried `W (also R5)` in its R/W cell.** After the edit it reads
   `W (also R5)` in one column and `EXCLUDED-RULED (R3)` in another. **That is correct and
   is not a contradiction** -- section J's `N 113` already carries the dual form `R3 + R5`
   for the equivalent case. Recorded here so the next reader does not "fix" it.

**THIS CLOSES THE CLASS RATHER THAN ONE CASE.** A census of all 43 headings in
`network.md` found exactly 11 that mention an R-code, and ten of those are the rulings'
own headings. Section K's was **the only heading in the file that cites an R-code without
being that ruling's own heading.** After this edit:

    rows resolving via a heading, before   9 first / 10 anywhere
    rows resolving via a heading, after    0 first /  0 anywhere
    the `ruling` bucket                   72 -> 81        total write-offs  309 -> 309

**What the ten still do not have is a reason cell.** Their tables have four columns and
the edit did not add a fifth, so `has_reason_cell` is still 0 for all ten and they remain
in the 21 rows that `classify_writeoff_reasons.py` reports as carrying no reason cell at
all. **That is deliberate.** What they were missing was a reachable ARGUMENT, and R3 is
now cited in a cell on every one of them. Giving them prose of their own is an
adjudication, and it is still not this wave's to make.

---

## 7. A DEFECT IN THE SHIPPED PARSE, FOUND BY THE CROSS-CHECK AND NOT FIXED HERE

The child written to disagree with the shipped parser disagreed with it, in a place
nobody had looked. **`count_census_states.cells()` splits on `|` without honouring the
markdown escape `\|`**, so a cell containing one is fractured and everything after the
escape becomes a separate cell.

Four lines in the corpus carry an escaped pipe, all in `jobs.md`, three of them census
rows. On every one of them the STATE is read correctly -- which is exactly why no
instrument has ever noticed -- and the REASON is read as a truncated tail:

    row     shipped parse sees          the cell actually holds
    J 50      123 chars                   170 chars
    J 103     795 chars                  1322 chars   -- loses 527, including the row's
                                                         opening `linkedin_follow_company`
    J 104     302 chars                   403 chars   -- loses the leading tool name

**No census number is affected and no pointer count is affected** -- I checked both, and
that is why this is reported rather than repaired here. It is a defect in a shipped
instrument that four waves have now built on, the fix belongs with that instrument's owner
alongside its 71 tests, and a fifth wave editing it today is how this corpus got the
defects it has. Named, measured, and handed over.

---

## 8. THE LEDGER

**0 census rows banked. 0 census numbers moved.** Proven in section 5 by sha256 and byte
diff on both named instruments, and field by field on all 309 classifier verdicts.

What landed:

| artifact | what it is |
|---|---|
| `scripts/measure_pointer_graph.py` | the measurement, the planted-row control, the pin and the guard, with `--selftest` |
| `_audit/_census/pointer-graph.tsv` | the pinned graph: 69 pointers, their donors, read distances and donor kinds |
| `tests/test_pointer_graph_guard.py` | 3 tests, 26s; asserts every control ran, not only that the run was green |
| `_audit/_census/network.md` | ten state cells, `EXCLUDED-RULED` -> `EXCLUDED-RULED (R3)` |

What this pass did NOT do:

1. **It did not rewrite the 69 positional pointers.** Section 4 is the measured argument.
   The dialect is still positional and 45 rows are still silently movable -- what changed
   is that moving one is now loud.
2. **It did not repair `cells()`.** Section 7.
3. **It did not give `N 119`-`N 128` reason cells.** Section 6's last paragraph.
4. **It opened no page and fired no write.**
5. **It did not prove anything about HEAD.** `--selftest` overlays the working tree into
   its sandbox, deliberately, because the instrument on trial is uncommitted. A green
   proves the guard convicts as the tree stands.
