# The compound rows -- when one census row names two capabilities

**Wave:** `the-compound-rows`, 2026-09-21.
**Question:** when one census row describes TWO capabilities, should it be split?
**Answer:** **almost never, and the lead's proposed rule is refuted twice over by
evidence already on disk.** The corpus has answered this question EIGHT times
without ever naming a rule, and its answers are perfectly consistent. Seven of
the eight were not splits.

**VERDICT ON THE QUEUE: NOTHING IS SPLIT. `stated rows` stays 704.** Four
candidate rows get a cell correction instead, three get a written trigger
condition, and one sibling wave's claim is corrected.

---

## 0. THE HEADLINE, BEFORE THE ARGUMENT

The lead proposed:

> *Split a compound row only when its halves differ in DIRECTION (one R, one W).*

**Both of its boundaries fail against measurement.**

| the rule says | the corpus did | where |
|---|---|---|
| **split** when direction diverges | did **not** split, SEVEN times -- it widened the direction cell to a both-value instead | `P M6` `P M9` `P M11` `M M28` `M C47`, plus `J 71`'s own cell declining in writing, plus `_check_jobs_gap_directions.py` declining structurally |
| **do not split** when direction does not diverge | **split** `P L2` -> `L2` + `L2b`, the single precedent in the census's history -- and **both halves are `R`** | `_audit/_census/profile.md` section L |

The one split this census has ever made is a split the lead's rule forbids, and
the rule's own cited model is the counter-example to it.

**THE MECHANISM, MEASURED.** Direction and state are not symmetric, and the
asymmetry is a property of the shipped readers rather than a matter of taste:

    DIRECTION: the vocabulary HAS a both-value and the shipped reader
               normalises five spellings onto it.
      cell 'R+W'        -> direction_of = 'R+W'
      cell 'RW'         -> direction_of = 'R+W'
      cell 'R/W'        -> direction_of = 'R+W'
      cell 'W+R'        -> direction_of = 'R+W'

    STATE: the vocabulary has NO both-value, and every attempt to write one
           is answered SILENTLY and WRONGLY -- four different ways, none of
           them an error, none of them raising a dialect.
      cell 'MEASURED-ABSENT / GAP'  -> classify = ('MEASURED-ABSENT', [])   second state DISCARDED
      cell 'GAP / MEASURED-ABSENT'  -> classify = ('GAP', [])               TEXTUAL ORDER decides the census
      cell 'GAP+MEASURED-ABSENT'    -> classify = ('', [])                  row LEAVES numerator and denominator
      cell 'MEASURED-ABSENT, GAP'   -> classify = ('', [])                  same, silently

So a direction-divergent row can be told the truth IN THE CELL. A state-divergent
row cannot be, at all, by any spelling -- and the failure is silent in both
directions, which is the disease `count_census_states.py` was written against.

---

## THE RULING -- RULED: a compound row is split ONLY when its halves need different STATES

Canonical id **`COMPOUND-ROW-SPLITS-ONLY-ON-STATE`**. It repairs the lead's
proposed rule rather than adopting or discarding it: the lead correctly
identified that a compound row can hide a capability, and correctly identified
direction as where that was measured. What the measurement shows is that
direction is the one axis that does **not** need a split, because it is the one
axis whose vocabulary already has a both-value.

> **SPLIT a compound row if and only if its halves require DIFFERENT STATES.**
> A direction divergence is repaired IN THE CELL (`R+W`), never by a split,
> because the direction vocabulary has a both-value and the shipped reader
> speaks five spellings of it. A state divergence has no cell repair: the state
> vocabulary has no both-value, and the shipped counter answers a two-state cell
> by silently picking one by textual order or silently dropping the row out of
> the census. **Verbosity, two addresses, two surfaces and two verbs are not
> grounds** -- they live in the reason cell, which is prose and can carry two
> clauses without lying.
>
> **AND THE THIRD OPTION THE QUEUE NEVER CONSIDERED: a row whose halves share a
> state TODAY but will not once a pending ruling is applied is NOT SPLIT NOW.
> It carries a written TRIGGER naming the ruling and the state each half would
> take.** The split becomes owed at the moment somebody applies that ruling,
> and not one day earlier.

---

## 1. WHAT THE REGISTER RETURNED, VERBATIM

Queried before anything else, as instructed, with
`scripts/build_rulings_index.py --find`.

**`--find "should a census row that describes two capabilities be split"`** --
23 matches, best first. The relevant one is third, and it governs the OPPOSITE
operation:

```
  3. DUPLICATE-ROW-IS-MARKED-NEVER-DELETED   [2026-09-20]
     RULED  : When two census rows describe one capability the duplicate STAYS in the file, marked as a duplicate and naming the row it duplicates. It is not removed and its id is never reused.
     BINDS  : census state -- every cross-slice re-file and de-duplication
     WHERE  : _audit/2026-09-20-the-deduplication-ruling.md
     SECTION: The ruling
     ALIASES: the deduplication ruling, OWNED-BY-A-SIBLING-SLICE
```

**`--find "L2b"`** -- the register refuses, and its refusal names what it did
not read, which is the behaviour `refusals-must-name-what-they-saw` asks for:

```
NOTHING REGISTERED MATCHES 'L2b'.

THAT IS NOT A FINDING THAT NOTHING WAS RULED. The register
holds 34 rulings and its discovery scan reads `RULED:`
only -- section 4 of _audit/RULINGS.md lists the signals it
does not read. Search the corpus before concluding.
```

**`--find "split a row into two"` and `--find "one row two capabilities"`**
return the same families -- container/content, dedup, canonical ids. Nothing
about splitting.

**Corroborated outside the register**, because its scan is admittedly narrow.
`grep "RULED:" _audit/**/*.md | grep -i split` returns exactly one hit and it is
a different sense of the word: `PUBLISHED-SPLIT-REPORT-NOW-GATE-LATER`, about
when a reporting check becomes a blocking gate.

**CONFIRMED: NO SPLIT RULING EXISTS.** The `what-was-ruled` wave and the lead
were both right. I did not find one they missed.

**BUT THE PREMISE BEHIND THE QUESTION IS WRONG, AND THAT IS THE FINDING.** The
absence of a *written* ruling was read as the absence of a *decision*. The
corpus has decided this eight times in practice, consistently, in cells and in
instrument source. Those decisions were unfindable for the ordinary reason:
none of them is phrased as a ruling, so no register scan and no `RULED:` grep
reaches them. This is `invariants-nobody-ruled` with eight sites.

---

## 2. HOW I ENUMERATED THE CANDIDATES, AND WHAT THE METHOD MISSES

`scripts/_census_compound_rows.py` (new; see section 6). Two nets over the same
population, and **row admission is delegated to the shipped counter's own
predicates** -- the same `ROW` regex, the same `HEADERS` set, the same `cells()`
-- so the net cannot disagree with `count_census_states.py` about what a row is.

**THE BROAD NET** flags any capability cell carrying `slash / or / and / comma /
then / plus`. **229 of 785 rows.** Almost all are noise of one shape: a
parenthetical enumerating an act's VALUES, as in *"Filter: Date posted (24h /
week / month / any)"* -- one act, four values, three markers tripped.

**THE SHARP NET** (`--verb-pairs`) requires a joiner with a VERB on the left and
a verb as the FIRST word on the right. **55 of 785 rows.** The asymmetry is
deliberate: *"Vote in a poll / view poll results"* puts its left verb five words
back, so a positional left test misses it; but *"...post or comment"* would be
admitted by a loose right test, because `post` is a verb elsewhere in this
corpus. Parenthesised text is stripped first. The comma is excluded from the
sharp net entirely -- measured, every comma in a census capability cell
separates FACETS of one act, never two acts.

**FOUR THINGS THE METHOD MISSES, stated so the 55 is not read as complete:**

1. **AN IMPLICIT PAIR -- and this is the one that matters most.** A row naming
   one act whose surface serves two carries no conjunction and does not appear
   in either net. **`P L2`, the only row this census has ever split, is exactly
   this shape**: *"Own follower count"* covered COUNT and LIST with no joiner
   between them. **So my net misses the precedent's own case, and any rule
   validated only against the net's output is validated against a population
   that excludes the one positive example.** I found `L2b` by grep, not by the
   net, and no enumerator over capability TEXT can find its like.
2. **A PAIR SPLIT ACROSS CELLS.** Only cell[1] is read. A row whose capability
   names one act while its REASON cell discusses a second is invisible.
3. **A CONJUNCTION OR A VERB THE LEXICON DOES NOT SPELL.** Both lists are
   printed on every run for exactly this reason. The verb lexicon is 85 entries,
   hand-authored from the measured leading-word distribution of all 785 cells
   and deliberately not auto-derived -- "leading word" also yields `company`,
   `premium`, `profile`, `own`, `real`, `how` and `which`, which are not acts.
4. **`jobs.md` HAS NO PER-ROW DIRECTION COLUMN AT ALL** -- its tables run
   `# | capability | source | state | reason`. So for all 186 jobs rows the
   direction prints `-`, and **any rule phrased as a test on a row's direction
   cell is unevaluable on 24% of the census.** That is a fact about the corpus,
   not a limit of the script, and it is an independent problem with the lead's
   rule, separate from the two refutations above.

**AGAINST THE HANDED-DOWN LIST.** `what-was-ruled` reported four (`P D27`,
`P L3`, `M C67`, `M C85`) "and arguably ten with the sweep's six compound rows";
`write-ceiling` named `N 169` and `N 187` as the same shape. My net finds **55**,
confirms all four of the queue, and **refutes the `N 169` / `N 187` claim**:
neither is a compound row. Each names ONE act (`Filter`) over four facets, and
neither appears in the sharp net. What they actually carry is a single-capability
row whose direction cell says `W` while its own reason cell says
*"A filtered read over his own connections"* -- a direction dispute, which is
section 4's business, not a split question. Reported to the lead as found; not
ruled on here.

---

## 3. THE EIGHT DECISIONS THE CORPUS ALREADY MADE

Every one of these was on disk before this wave started. None is phrased as a
ruling. Together they are unanimous.

### 3.1 SEVEN TIMES: direction diverged, and the cell was widened rather than the row split

Measured over all four slices by direction-cell value:

| slice | row | direction cell | capability |
|---|---|---|---|
| P | `M6` | `R/W` | Saved screening-question answers |
| P | `M9` | `R/W` | Stored job applicant accounts |
| P | `M11` | `R/W` | Resume Builder |
| M | `M28` | `R+W` | View and restore archived conversations |
| M | `C47` | `R+W` | Manage, share or duplicate article drafts |
| N | `125` | `W (also R5)` | Delete a recommendation you have sent |
| J | `71` | (no column) | List / delete stored resumes -- **declined in writing, see 3.2** |

**`M M28` IS THE DECISIVE ONE.** It is the SAME SHAPE as `M C85`, in the SAME
FILE, in the SAME COLUMN: a read verb and a write verb joined, state GAP. `M28`
reads `R+W`. `C85` reads `W`.

So the write-ceiling wave's finding -- that `C85`'s read half is *"invisible to
every direction sweep including the one that built your backlog"* -- is **true,
and its cause is not what the wave concluded**. Run the shipped triage:

    scripts/triage_messaging_gap_rows.py
      GAP rows             77
      BY DIRECTION, as the census's own R/W column states it
        R           10
        R+W          1        <- this is M28. It is NOT invisible.
        W           66        <- this is where C85 sits
      reads 10   writes 66   read-and-write 1   unreadable-cell 0

**A compound row is not invisible to the direction sweeps. A MISSTATED CELL is.**
`C85` is invisible because its direction cell is wrong, and `M28` -- identically
compound -- is visible because its cell is right. The remedy is a cell edit, and
it costs nothing: no new id, no denominator move, no row outside a frozen set.

`scripts/reader_closable_blockers.direction_of` is the reader, it is value-based
rather than positional, it ships with a negative control, and its `DIRECTIONS`
table already normalises `R+W`, `RW`, `R/W` and `W+R` onto one verdict. **The
both-value is not something this wave is proposing. It is shipped, and five
spellings of it are already understood.**

### 3.2 `J 71` DECLINED THE SPLIT IN WRITING, AND STATED MY RULE BEFORE I DID

`_audit/_census/jobs.md`, row 71, in its own reason cell:

> *"THE ROW IS COMPOUND -- 'list / delete' carries a write verb -- but the
> substring closes both halves identically, **so the state does not depend on
> which half is read**."*

A direction-divergent row (`list` is a read, `delete` is a write), examined,
and **not split, on precisely the ground I arrived at independently: the
published cell value is the same either way.** The lead's rule would require
this row to be split. The census already refused, and wrote down why.

### 3.3 THE SWEEPS THEMSELVES DECLINED IT, STRUCTURALLY

`scripts/_check_jobs_gap_directions.py`, module docstring:

> *"a block direction can be WRONG FOR A ROW INSIDE IT, and this file found
> three: `J 56` ... and `J 37` ('List AND MANAGE all alerts') sits in a range
> filed `R` while its own text names a write. So this file classifies PER ROW
> off the row's own capability text, and prints the three disagreements rather
> than hiding them."*

A shipped instrument met the compound-row problem head-on and its remedy was to
**make the sweep read the capability text**. Not to split the rows. `J 37` is
one of my 55 and it already has a published disagreement recorded against it.

### 3.4 ONCE: the states diverged, and the row WAS split

`P L2` -> `L2` + `L2b`, 2026-09-04, by team-lead ruling. `L2b`'s own cell:

> *"L2 was compound -- count AND list -- and one half is measured absent while
> the other was never searched for. Neither state is honest about both:
> MEASURED-ABSENT would claim evidence this half does not have, and GAP would
> throw away evidence the COUNT half does have. **Merging the two deletes the
> vocabulary needed to say what is actually known.**"*

**Both halves are `R`.** The divergence was entirely in the STATE. `L2` is
`MEASURED-ABSENT`; `L2b` is `GAP`. And section 0 measured what the shipped
counter does with a cell that tries to say both: it discards one silently, or
drops the row out of the census silently, and never raises a dialect. **There
was no cell repair available. The split was the only honest move, and it remains
the only one this census has ever needed.**

---

## 4. EACH CANDIDATE, WITH ITS VERDICT

`stated rows` is unchanged by every verdict below.

### THE QUEUE OF FOUR

| row | halves | dir cell | state | VERDICT |
|---|---|---|---|---|
| `M C85` | vote (W) / view poll results (R) | `W` | GAP | **DO NOT SPLIT. CORRECT THE DIRECTION CELL TO `R+W`.** |
| `P D27` | create (W) / delete (W) | `W` | GAP | **DO NOT SPLIT. WRITE THE TRIGGER.** |
| `P L3` | create (W) / edit (W) / delete (W) | `W` | GAP | **DO NOT SPLIT. WRITE THE TRIGGER.** |
| `M C67` | edit (W) / delete (W) | `W` | GAP | **DO NOT SPLIT. WRITE THE TRIGGER.** |

**`M C85` -- do not split; the cell is wrong, not the row.** The halves differ in
direction and NOT in state: both are GAP, and nobody disputes that either half
is unbuilt. Under the rule, direction divergence is a cell repair. `R+W` puts
the read half into the `R+W` bucket of every direction sweep -- the bucket
`M M28` already occupies in the same file -- at zero cost to the denominator,
zero new ids, and zero rows outside a frozen set. **The split would have bought
exactly the visibility the cell edit buys, and paid the `L2b` price for it.**

The row's own cell already argues for its read half being admissible (*"poll
results are COUNTS"*, under `FEED-CONTENT-READ-RULING`). That argument is
untouched and gets stronger once the row is classed `R+W`, because it then
appears in the read-side population where it can be triaged.

**`P D27`, `P L3`, `M C67` -- do not split; write the trigger.** All halves are
writes; all halves are GAP. **No published cell is false today**, so there is
nothing to repair and nothing to split. The write-partition wave framed this as
*"RULING NEEDED: split, or leave whole"* -- a binary that hides the right answer.
What makes these rows feel unsettled is not their present state, it is that
`R5` reaches the `delete` half and nothing reaches the `create`/`edit` half, so
**applying `R5` would make the state cell false of one half** -- and section 0
proves that is the case with no cell repair.

So the split is not owed now. It is owed **at the instant `R5` is applied**, and
that is a condition that can be written down:

> TRIGGER: if `R5` (or any ruling) is applied to the DELETE half alone, this row
> MUST be split first, because the state cell would then be false of the
> other half and the state vocabulary has no both-value. Until then the row
> stays whole and both halves are GAP.

This converts three rows from *unruled and re-escalating* to *ruled, with the
condition for revisiting them written in the row*. It costs no denominator move,
and it means the next wave to touch `R5` cannot apply it without seeing the
consequence.

### THE TWO NAMED BY `write-ceiling` AS THE SAME SHAPE

| row | VERDICT |
|---|---|
| `N 169` | **NOT A COMPOUND ROW. Claim refuted.** |
| `N 187` | **NOT A COMPOUND ROW. Claim refuted.** |

*"Filter the connections you invite by location, company, school and industry"*
is ONE act over four facets. Neither row appears in the sharp net; both appear
in the broad net only via `comma` and `and`, which is the parenthetical-value
noise class. They carry a real defect, but it is a different one: the direction
cell says `W` while the row's own reason cell says *"A filtered read over his own
connections"*. **That is a direction dispute on a single-capability row.** Out of
scope for a split ruling; handed to the lead, unruled by me.

### THE REST OF THE 55 -- the classes, with the population each covers

Every one of the 55 falls into one of these. None is a split.

| class | n | direction | verdict |
|---|---|---|---|
| **Same-direction verb family** (`add / edit / delete`, `hide / unhide`, `block / unblock`, `mute / unmute`, `follow / unfollow`, `subscribe / unsubscribe`) | 38 | all `W` | **NO SPLIT.** One state, one direction, both true of every half. `P B2` `P D5` `P D11` `P G4` `P N7` and the rest. The verb family IS the capability. |
| **Direction-divergent, direction cell already correct** | 2 | `R+W` | **NO ACTION.** `M M28`, `M C47`. Already right. |
| **Direction-divergent, direction cell wrong or absent** | 8 | `W` or `-` | **CORRECT THE CELL where there is one.** `M C85` (**done, this wave**), plus 7 jobs rows (`J 18` `J 34` `J 37` `J 68` `J 71` `J 77` `J 149`) where **there is no per-row cell to correct**, so the remedy is the one `_check_jobs_gap_directions.py` already ships: classify per row off the capability text. `J 37` is already on that script's published disagreement list. |
| **Flagged by the net, REFUTED by the row's own cell** | 1 | `W` | **NO CHANGE -- and I was wrong in draft.** `N 160` *"Send, receive and manage message requests"* trips the net on `receive`, and I had it down for an `R+W` correction. Its own reason cell refutes me: it names its three twins -- `M M6` send, `M M7` accept, `M M8` decline -- and **all three are `W`**. `receive` here is the passive arrival of a request, not an act this census tracks. `W` is correct. This is the sharp net over-reporting exactly as designed, and being adjudicated by the corpus rather than by me. |
| **Same-direction, both reads** | 3 | `R` | **NO SPLIT.** `M M43`, `N 95`, `N 179`. (`N 95` *"View and re-run"* is arguably `R+W`; flagged, not ruled -- it is the direction question again.) |
| **Pending-ruling divergence** | 3 | `W` | **TRIGGER, per above.** `P D27`, `P L3`, `M C67`. |

**`P L2b` itself**: nothing to do. It exists, it is correct, and its cost is real
-- see section 5.

---

## 5. THE COST OF A SPLIT, PRICED -- AND WHY IT DID NOT DECIDE THIS

The lead's strongest argument against splitting was the `L2b` blocker-map hole:
**`P L2b` is the only GAP row of 275 absent from the blocker map entirely**,
because the map derives from a set frozen 2026-09-03 and `L2b` was created the
day after. `scripts/_check_open_slots.py` takes its universe from that map and
cannot see the row. `blocker-assignments.tsv` states the consequence twice, in
two different blockers' evidence cells, both times as a dated boundary:

> *"P L2b, 'Own follower LIST', which is GAP today and is NOT IN THE FROZEN SET.
> ... If the ledger's 4R counted the compound L2, the missing fourth is an
> artifact of a split that happened after the count was published, and no map
> edit can fix that."*

**That cost is real and I confirm it.** But it did not decide this wave, and it
should not decide the next one, because **it is a cost of CREATING A ROW, not a
cost of splitting.** Any new row added after 2026-09-03 lands outside the same
frozen set. The honest statement of the cost is therefore:

> A split is the most expensive way to make a capability visible, because it
> creates a row outside every set frozen before it AND moves the denominator.
> Use it only where no cheaper instrument can say the truth.

Which is the rule, arrived at from the other end. **And it is why `C85` gets a
cell edit: the cheaper instrument exists, ships, and is already in use on the
identical row three files away.**

---

## 6. THE INSTRUMENT

`scripts/_census_compound_rows.py` -- enumerates rows whose capability cell names
more than one act. Two nets (broad, and `--verb-pairs`), both printing their own
vocabulary on every run so what they cannot see is legible without reading the
source. Row admission delegated to `count_census_states.py`; direction read by
`reader_closable_blockers.direction_of`.

**IT IS A TRIAGE NET, NOT A CHECK, AND IT IS NOT REGISTERED AS AN INSTRUMENT.**
It cannot fail, it asserts nothing, and this repo's second law is that an
instrument enters the register only if it has been shown failing. It ships as a
reproducible enumerator so that a later reader can confirm every member of the
55 got a verdict, rather than the ones somebody remembered.

**ITS FIRST VERSION WAS WRONG AND THE CORPUS CAUGHT IT.** It matched
`^(R|W|R/W|W/R|RW)$` against a cell found by COLUMN INDEX, and reported `M M28`
-- whose cell reads `R+W` -- as `?`. Two defects in four lines: a spelling the
corpus uses that the regex did not, and an index-based finder that breaks on the
messaging layout. Both were already solved by
`reader_closable_blockers.direction_of`, which is value-based, normalises five
spellings, and ships with a negative control. Replaced by the import. This is
`import-the-shipped-instrument` firing on schedule, and it matters beyond
hygiene: **had the bug survived, `M M28` would have read `?` instead of `R+W`,
and the single measurement that refutes the lead's rule would have been
invisible to this wave.**

---

## 7. `stated rows` -- BEFORE AND AFTER

    BEFORE   ./venv/Scripts/python.exe scripts/count_census_states.py
             jobs.md                      stated rows  150   GAP   56
             profile.md                   stated rows  203   GAP   55
             messaging-and-content.md     stated rows  142   GAP   77
             network.md                   stated rows  209   GAP   87
             TOTAL stated rows            704          GAP  275

    AFTER    identical, all five figures.

**704 BEFORE, 704 AFTER. NOTHING MOVED, AND NOTHING NEEDED TO.** No assertion of
the denominator anywhere in the corpus or in the shipped tests goes stale, which
is the strongest practical argument for the rule: the cheapest correct answer to
seven of the eight cases costs the denominator nothing.
