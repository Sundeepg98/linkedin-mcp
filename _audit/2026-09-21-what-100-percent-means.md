# What 100 percent means here, and the two numbers that both deserve the word "done"

**CORRECTS:** `_audit/2026-09-21-the-open-queue.md` -- its section 2 lists `J 40`, its highest-value uncommissioned build, as *"named, measured and NOT yet commissioned"*; measured at `f729a2a` that row is `COVERED-UNFIRED`, banked by the `proximity-field` wave, so a reader arriving there would commission a build that has already landed. Its own header declares it a dated snapshot and says to re-derive, which is correct behaviour, but that warning names no row. `N 134` and `P O3` from the same section were re-measured and are unaffected.

**Wave `what-100-percent-means`, 2026-09-21, measured at `f729a2a`.** Every
figure below is recomputable: `python scripts/census_completion.py`. Nothing
here is quoted from a document without being re-derived first, and where a
document and the tree disagree the disagreement is printed rather than settled
silently.

---

## THE HEADLINE, IN TEN SECONDS

    DENOMINATOR      704 stated rows, four census slices        (762 capabilities)
    of which         315 are out of scope    EXCLUDED-RULED 308 + MEASURED-ABSENT 7
    ACHIEVABLE       389 rows

    ADJUDICATED      429 / 704   60.9%   every state except GAP
    DELIVERED broad   95 / 704   13.5%   COVERED-PROVEN + COVERED-UNFIRED
    DELIVERED strict  72 / 704   10.2%   COVERED-PROVEN only

    against the ACHIEVABLE surface, which is the number to plan on:
    DELIVERED broad   95 / 389   24.4%
    DELIVERED strict  72 / 389   18.5%

**If one number has to be said aloud, it is 24.4 percent of the achievable
surface, or 13.5 percent of everything enumerated.** Not 61. The 60.9 percent
is real and it is not a completion figure: it counts every row somebody reached
a verdict on, and 334 of those verdicts are "we are not doing this", "LinkedIn
does not have it", or "a tool fired and cannot do it".

**The honest answer to "how long" is that it is not derivable from anything in
this repository, and no estimate appears in this document.** What is derivable
is what remains and what would unblock it:

    NOT DELIVERED                317 rows   (GAP 275 + UNFIRED 23 + CANNOT-DELIVER 19)
      needs a live browser session  25   DERIVED 23 UNFIRED + ENUMERATED 2
      needs an operator ruling     151   CEILING, the standing write ruling
                                   + 5   ENUMERATED, one undecided question
      blocked on nothing at all     61   UPPER BOUND, and see the residual
      unplaceable by any instrument 56   jobs.md has no direction column
      a tool fired and cannot do it 19   COVERED-CANNOT-DELIVER

    IT SUMS, AND HERE IS THE CHECK, because the buckets are drawn from two
    different populations and a reader is entitled to be suspicious:
      23 UNFIRED + 19 CANNOT-DELIVER + 275 GAP                      = 317
      and inside the 275:  151 write + 68 read + 56 unplaceable     = 275
      and inside the 68:     2 press +  5 ruling + 61 blocked-on-nothing = 68

---

## 1. IS 704 THE WHOLE SURFACE? YES, AND THE CENSUS SAYS THAT IS NOT THE SAME AS COMPLETE

The brief asked whether 704 is the whole surface or a slice of it, because this
project has reported completion against a fraction before. Three things were
measured.

**The tool surface is 49, triangulated three ways.** A `@mcp.tool` grep returns
51 and two of those are comments narrating past incidents; an AST walk resolving
every decorator to a dotted name returns 49; `mcp.list_tools()` on the live
registry returns 49. The repository's own pin agrees and its control
demonstration passes. **The tool count is not a denominator for this question** --
49 tools serve capabilities across all four slices and one tool can serve
several rows.

**`mcp-inventory.md` is a fifth file in `_audit/_census/` and is a DIFFERENT
POPULATION, by its own declaration.** It enumerates 35 tools of this server
(23 read/session + 12 write) under its own state vocabulary. The shipped counter
excludes it by name. Its own preamble says what it is:

> **You can grep a codebase for what it refuses. You cannot grep it for what
> nobody considered.** ... the gap between what LinkedIn offers and what this
> server delivers is made of two parts: the refusals, which are enumerable, and
> the never-considered, which are not enumerable from inside the repo at all.

It calls the four slices *"the four sibling agents on this census"* -- siblings,
not the same table. **Adding 35 to 704 would sum two different things.**

**So 704 is the whole of the OUTWARD census, and it is not a subset of some
larger table in this repository.** But the census's own words above are the
caveat that matters more than any arithmetic here: **100 percent of 704 is 100
percent of what somebody enumerated, and the census states that its enumeration
cannot be complete.** Every percentage in this document is scoped by that
sentence. It is not a hedge -- it is the census refusing to claim a completeness
it has no instrument for.

### 1.1 ROWS ARE NOT CAPABILITIES, AND THREE CAPABILITY TOTALS CIRCULATE

`profile.md` collapses two blocks. Both were re-verified against the file at
HEAD rather than inherited:

| block | stands for | how verified | state |
|---|---|---|---|
| `P O6-O20` | 15 capabilities in 1 row | id range O6..O20 is 15, AND the capability cell lists 15 items -- two independent counts agreeing | EXCLUDED-RULED |
| the `P-R` section | 45 capabilities, 1 row (`P1`) | its own header declares `(45)`, its own closing note reads *"`P1` is counted in the 45; the settings-family share of this block is 44"* | EXCLUDED-RULED |

    704 stated rows + 58 collapsed = 762 capabilities, computed at HEAD
    761   published, and quoted under every coverage ratio in this campaign
    760   the shipped counter's docstring

**`_audit/2026-09-19-cross-slice-rulings.md` reported that the published 761
does not reconcile with its own stated terms, and it was right:** `705 + 59 - 2`
is 762. That wave also reported `THE P-R BLOCK DOES NOT EXIST` and named three
futures it could not separate.

**One of those three is now closed.** That wave was looking for a ROW named
`P-R` and correctly did not find one. **The block is a SECTION** -- `### P-R.
Data privacy, advertising data, notification settings (45)` -- whose 44
settings-family items are **prose bullets carrying no row ids at all**. So the
`+44` cannot be double-counting rows that were expanded: those capabilities have
no rows to double-count. **The unexplained term is the `- 2 stateless`, and it
is the entire difference.** The two stateless rows are `J 58` and `M C53`, and
neither is inside the 704 -- they carry no state, so the counter never counted
them; subtracting them removes them a second time.

**Reported, not corrected.** This denominator's owner is the counter's, and
moving it quietly is how 761 became unreproducible in the first place.

**AND IT BARELY MATTERS, WHICH IS WORTH PRINTING BECAUSE IT IS THE FIRST
OBJECTION ANYBODY RAISES.** Every one of the 58 collapsed capabilities is
EXCLUDED-RULED -- asserted at runtime by the instrument, not assumed -- so they
leave the achievable surface the moment they enter it:

    delivered / published surface    rows 13.5%   capabilities 12.5%
    delivered / achievable surface   rows 24.4%   capabilities 24.4%

---

## 2. ADJUDICATED IS NOT DELIVERED -- THE DISTINCTION IS ADOPTED, NOT INVENTED

`_audit/2026-09-19-the-read-rows.md` section 4 is the commit the brief pointed
at (`8dd3c5c`, *"the read rows convert to capability at 11 percent, not 61"*).
Its finding, in its own sentence:

> The 61% headline survives only because **`COVERED-CANNOT-DELIVER` is a
> `COVERED-*` state and is not a capability.** Counting it as one answers a
> different question from the one a planner is asking.

Its table drew the line at PROVEN or UNFIRED, headed *"an actual capability"*.
**That line is adopted here as DELIVERED-broad, and a stricter one is printed
beside it** -- COVERED-PROVEN alone -- because UNFIRED means the code exists and
has never returned a payload from live LinkedIn. Both are printed with the
state-set that defines them. Choosing silently between them is how a headline
becomes a quotation.

| state | rows | is it a capability a user can exercise? |
|---|---|---|
| COVERED-PROVEN | 72 | yes, and it has been fired live |
| COVERED-UNFIRED | 23 | the code exists; nothing has seen it return live |
| COVERED-CANNOT-DELIVER | 19 | **no.** A tool fired and cannot do the thing |
| EXCLUDED-RULED | 308 | **no.** Decided against, on written grounds |
| MEASURED-ABSENT | 7 | **no.** LinkedIn does not offer it |
| GAP | 275 | not yet adjudicated |

**The arithmetic that makes the point: 429 rows carry a verdict, 95 of them are
a capability anybody can use, and the difference is 334.** Those 334 are real
work -- the exclusions are argued, cited and in several cases hard-won -- and
not one unit of it is something the server can do.

### 2.1 A COINCIDENCE, NAMED SO NOBODY BUILDS ON IT

The whole-census adjudicated figure is **60.9%** and the strict delivered figure
is **10.2%**, which is very nearly the 61/11 shape of the read-rows document.
**It is a different population and a different construction** -- that document
measured read-shaped rows against a frozen 409-row GAP set, and could not
reproduce its own brief's 61 either. The resemblance is arithmetic. It is
recorded here only so that a future reader who notices it does not conclude the
two are the same measurement.

---

## 3. THE GUARD: `stated rows` IS LOAD-BEARING AND NOTHING WAS HOLDING IT

**Verified rather than inherited from the brief.** As a standalone number, `704`
appears in **15** tracked `_audit` documents before this one (16 including it)
and in two module docstrings. In Python it appears four times: twice in
`count_census_states.py`'s docstring, once in `blocker_table_refresh.py`'s
docstring, and once in a `#:` comment in
`tests/test_writeoff_kinds_are_derivable.py`. **No assertion anywhere.**

*An earlier draft of this document, and the commit message that landed it, said
**21**. That came from `git grep -l "704"`, a SUBSTRING match, which also counts
six documents where the digits sit inside a longer number. The figure was caught
by building the guard's own computed version and watching it disagree --
`(?<!\d)704(?!\d)` returns 16. A number taken from a loose grep and published
without a second reading is the exact failure this wave exists to guard against,
arriving in the wave's own prose, and it is recorded rather than quietly fixed.*

### 3.1 WHY THE EXISTING GUARDS COULD NOT DO IT

Measured, not assumed. `tests/test_census_rows_carry_a_state.py` inspects **706**
rows against the counter's **704** -- the two extra are its own
`DECLARED_STATELESS` pair, `J 58` and `M C53`. **Every counted row is already
being inspected.** So this is not a coverage gap. Neither that guard nor
`test_state_cell_dialects_refuse_loudly.py` **counts**, and looking at one row
at a time is a different question from asking how many there are.

*An earlier draft of this wave's control claimed `network.md`'s admin-only table
had no `state` column and was therefore uninspected. That was measured and it is
false -- the header is `| # | capability | R/W | state | note |`. The claim is
recorded rather than deleted, because `count_census_states.main()` still carries
the same stale belief in a comment, and the GAP-forcing it justifies is now
largely inert.*

### 3.2 WHAT SHIPS

| file | what it does |
|---|---|
| `tests/test_the_census_row_total_is_pinned.py` | 7 assertions: the pin is non-empty and agrees with hand-written literals; the population matches; each slice matches; the state VOCABULARY has not widened |
| `tests/census_row_pin.json` | the pinned ID SET with multiplicity, 704 rows |
| `scripts/pin_census_rows.py` | takes, checks and re-writes the pin; refuses to write while any dialect is open |
| `scripts/_check_the_census_row_pin_can_fail.py` | the three failing demonstrations below |

**It pins the POPULATION, never the ADJUDICATION.** A row moving GAP ->
COVERED-PROVEN does not fire it, and must not: several waves move census rows
daily and a guard firing on each would be switched off within the week.

**It pins an ID SET, not a scalar, and multiplicity is carried.** A scalar can
say `704 -> 705` and nothing else, after which somebody diffs 592 KB of markdown
to find which row. `DUPLICATE-ROW-IS-MARKED-NEVER-DELETED` makes a plain set
wrong the first time that ruling is exercised, so a `Counter` is used.

**The third leg has no neighbour.** Widening `count_census_states.STATES` makes
invisible rows countable, so the denominator moves while every census file stays
byte for byte identical. That has happened twice -- `XR` (+23) and
`CANNOT-DELIVER` (+2) -- both times correctly, and both times the counter's own
docstring demanded a receipt nothing enforced.

### 3.3 SHOWN FAILING, THREE WAYS

Run on a scratch copy; the live tree is never mutated. **Each demonstration also
runs the cell-shaped neighbour and asserts what it does**, so the claim is not
merely "mine can fail" but "mine fires while the neighbour stays green".

    isolation asserted: census=<scratch>/_audit/_census
    --- CONTROL, unmutated ---
    exit code 0 (want 0)
    PASS  the guard is green on an unmutated copy
    precondition asserted: 'BLOCKED' is neither a state nor a dialect, so a row
                           wearing it leaves the denominator in silence

    --- A  A ROW IS ADDED (a sixteenth row on network.md's admin table) ---
    exit code 1 (want non-zero)
    E  AssertionError: THE CENSUS POPULATION MOVED: 1 added, 0 removed (total 704 -> 705).
    E    This is the DENOMINATOR under every completion figure in this repository --
    E    16 documents under `_audit/` print 704. Each of them now divides by a
    E    number that is no longer true.
    E      ADDED    N A16 -- a capability row entered the census. Every published
    E                        percentage divides by a different number than it did.
    neighbour test_census_rows_carry_a_state.py: exit 0 -- STAYED GREEN, expected to stay green
    PASS  A  A ROW IS ADDED

    --- B  A ROW IS DELETED (jobs.md J 1) ---
    exit code 1 (want non-zero)
    E  AssertionError: THE CENSUS POPULATION MOVED: 0 added, 1 removed (total 704 -> 703).
    E      DELETED  J 1 -- the row is gone from its slice. `DUPLICATE-ROW-IS-MARKED-
    E                      NEVER-DELETED` says a census row is marked, never removed;
    E                      if this deletion is intended, say so in the commit.
    neighbour test_census_rows_carry_a_state.py: exit 0 -- STAYED GREEN, expected to stay green
    PASS  B  A ROW IS DELETED

    --- C  A STATE IS CHANGED TO ONE OUTSIDE THE VOCABULARY (jobs.md J 1) ---
    exit code 1 (want non-zero)
    E  AssertionError: THE CENSUS POPULATION MOVED: 0 added, 1 removed (total 704 -> 703).
    E      UNREADABLE J 1 -- THE ROW IS STILL IN THE FILE but its state cell is no
    E                        longer a state the shipped vocabulary can read. It has
    E                        left the numerator AND the denominator with no diff that
    E                        looks like a state change.
    neighbour test_census_rows_carry_a_state.py: exit 1 -- FIRED, expected to fire
    PASS  C  A STATE IS CHANGED TO ONE OUTSIDE THE VOCABULARY

    --- CONTROL, restored ---
    exit code 0 (want 0)
    PASS  the copy is byte-restored and the guard is green again
    ALL THREE DEMONSTRATIONS PASS

**C is the leg that earns the guard, and its value is the DISCRIMINATION.** A
and B are visible in a census diff. C is not: the row renders exactly as it
always did and the only thing that moved is a number in 21 other documents.
`BLOCKED` is used rather than a dialect deliberately, and the control ASSERTS
that choice against the shipped `dialect_of` -- a dialect is built only from the
vocabulary's own atoms and the counter already refuses on one loudly, so a
dialect would prove nothing new. The neighbour does fire on C, on a different
ground (the cell is now prose); what it cannot say is that the DENOMINATOR moved
or that the row is still present.

---

## 4. THE COMPLETION INSTRUMENT, AND THE DEFECT ITS OWN CONTROL FOUND IN IT

`scripts/census_completion.py` prints everything above so it can be recomputed
rather than remembered, and `--check` pins every headline figure so it can
disagree with the tree.

**Its first version was wrong, and demonstration C of its own control convicted
it.** With one row's state rewritten to a word outside the vocabulary, it
printed a complete and entirely plausible set of percentages over 703 rows. The
row had left numerator and denominator together, so nothing looked odd. Its
control compared the walk against `enumerate_gap_rows.rows()` -- and **the two
share the parse by design**, which that module's own docstring states about
itself. The check was structurally incapable of catching it.

**The repair is the coupling, and it is why the guard in section 3 is
load-bearing rather than decorative:** the instrument now consults
`tests/census_row_pin.json`, the only record of the population not produced by
that parse, and **refuses entirely** rather than publishing a figure over a
denominator nobody agreed to. A warning printed above the numbers would have
been the worst option available -- the numbers get quoted and the warning does
not.

    --- C  A STATE BECOMES UNREADABLE (network.md, GAP -> BLOCKED) ---
    exit code 1 (want non-zero)
    REFUSING TO REPORT -- a control failed, so no figure below would mean anything:
      THE POPULATION HAS DRIFTED OFF ITS PIN: 0 added, 1 removed (pinned 704, live 703).
      Every percentage this file would print divides by a denominator nobody has agreed to.
      UNREADABLE N 4 -- THE ROW IS STILL IN THE FILE but its state cell is no longer
                        a state the shipped vocabulary can read.
    PASS  C  A STATE BECOMES UNREADABLE

---

## 5. THE BLOCKER DECOMPOSITION

**No blocker was classified by its name.** `scripts/classify_surface_blockers.py`
records what that costs: a five-way split of 97 blockers was once published from
a classifier that was never committed, and its own limits section admits the
class *"is a guess about names, not a measurement of reasons"* --
186,629,988,917,605 distinct subsets fit its three published integers. Every
division below is either **DERIVED** by a shipped instrument or is an
**ENUMERATED** list of row ids taken from a named document.

### 5.1 BUCKET 1 -- BLOCKED ON A LIVE BROWSER SESSION: 25

| what | rows | basis |
|---|---|---|
| `COVERED-UNFIRED` | 23 | **DERIVED from the state itself.** The code exists and has never returned a payload from live LinkedIn. A session is the entire remaining cost, by the state's own definition -- no ruling, no design, no build |
| `N 134`, `P O3` | 2 | **ENUMERATED.** Both need a disclosing press. `DISCLOSING-PRESS-PERMITTED` ruled it allowed and `press.disclose` is built -- and has **zero callers among the shipped tools**. A sanctioned, built mechanism nothing invokes |

**This is the cheapest bucket in the whole decomposition and it is the one a
single session clears.** 23 rows move from "code exists" to "proven" with no
decision from anybody.

### 5.2 BUCKET 2 -- BLOCKED ON AN OPERATOR RULING: 5 named, 151 ceiling

| what | rows | basis |
|---|---|---|
| D3 -- `N 99`, `N 172`, `N 177`, `N 178`, `M C83` | 5 | **ENUMERATED.** One undecided question: does a reasoned allowlist refusal count as "written" for `COVERED-CANNOT-DELIVER`? `_audit/2026-09-19-the-read-rows.md` calls it *"the single highest-yield decision left in this row set"*. All five verified still GAP at HEAD |
| write-direction still-GAP rows | 151 | **DERIVED** from the census R/W cell by the shipped direction finder. A **CEILING**, not a claim each row is otherwise ready |

The 151 are governed by the standing ruling `NO-IRREVERSIBLE-WRITE-IS-FIRED`: a
write may be designed, gated, tested against fixtures and left ready, and may
**not** be fired at a real target without him. So the last step of every one is
a decision, whatever gets built first.

### 5.3 BUCKET 3 -- BLOCKED ON NOTHING AT ALL: 61, AND IT IS AN UPPER BOUND

**This is the only bucket whose size is a statement about work, and it is the
number the question was really asking for.**

    read-direction still-GAP rows      68   DERIVED  (R 65 + R+W 3)
      minus those known to need a session  -2
      minus those known to need a ruling   -5
      ----------------------------------------
      blocked on nothing at all          61   UPPER BOUND

It is an upper bound and nothing stronger: it is the set a reader could close
**in principle**. It has not been shown that each one's address is admitted by
the shipped read boundary, and that is exactly the measurement missing (see
RESIDUAL).

### 5.4 UNPLACEABLE: 56

    direction unknown    56     ALL of them jobs.md
    direction ambiguous   0

`jobs.md` has no per-row R/W column at all, so its entire still-GAP population
is unplaceable by this method. That is a fact about the census's shape, not a
blocker, and `_audit/2026-09-21-the-jobs-direction.md` section 8 argues the
column should **not** be added. Until that is ruled these rows are honestly
unplaceable, and they are **not** folded into a neighbouring bucket to make the
arithmetic tidy.

    CHECK: 65 + 3 + 151 + 56 + 0 = 275 = still-GAP

---

## 6. THREE STALE READINGS FOUND WHILE DERIVING, EACH RE-DERIVED

The brief said to check staleness rather than trust a classification. Three
were found. **None is anybody's error; all three are the cost of a corpus that
moves faster than its documents.**

**6.1 `blocker-map.tsv`'s `state_today` column is a DATED SNAPSHOT wearing the
word "today", and no check can see it.** The coordinator asked precisely the
right question -- whether the disagreeing GAP counts are competing claims about
one instant or one current figure beside dated ones -- so it was tested rather
than assumed. Compared row by row against the live census, over the same 409
rows the map holds:

    map data rows compared     409
    column AGREES with live    375
    column DISAGREES            34
    on the GAP question: column says 301, live says 274 -- stale by 27

    GAP             -> EXCLUDED-RULED           20
    COVERED-UNFIRED -> COVERED-PROVEN            6
    GAP             -> COVERED-CANNOT-DELIVER    3
    GAP             -> COVERED-PROVEN            2
    GAP             -> COVERED-UNFIRED           1
    GAP             -> MEASURED-ABSENT           1
    COVERED-UNFIRED -> COVERED-CANNOT-DELIVER    1

**ANSWER: a dated snapshot, not a competing claim.** Every one of the 34 moves
in the same direction -- a row advancing. Not one goes backwards. The column is
simply the value at the last `--write`.

**Two things make it worse than an ordinary stale number, and both are
structural.** First, the column is NAMED `state_today` and carries no date, so
unlike `profile.md`'s COUNTS block -- which declares its own frozenness in prose
and is therefore honest -- it reads as current. Second, **`build_blocker_map.py
--check` cannot detect this**: the committed file is read on neither path, and
`state_today` is only computed on `--write`. `--check` exits 0 while printing
`today's GAP total, derived 275` directly beneath a committed column that says
301. `tests/test_blocker_map_is_derived.py` passes for the same reason -- it
re-derives the row-to-blocker ASSIGNMENT, which is what it was built for and
what it says it does.

**Nothing in this wave takes a state from that column.** The shipped
`reader_closable_blockers.py` enumerates live GAP rows and joins to the map for
the blocker NAME only, which is the correct coupling; this wave does the same.
Recorded so the next reader does not take `301` from a column that says today.

**NOT REPAIRED HERE, deliberately.** The repair is one `--write` plus a
`--check` that reads the committed column, and `blocker-map.tsv` is a derived
view that concurrent waves are moving; regenerating it from this worktree would
land a 409-row diff on top of theirs for a column this wave does not consume.
The measurement is the contribution; the rebuild belongs to whoever next owns
that map, with the `--check` gap closed in the same commit so it cannot recur
silently.

**6.2 The open queue is stale on its own highest-value item.**
`_audit/2026-09-21-the-open-queue.md` section 2 lists `J 40` (the
network-proximity extractor) as *"named, measured and NOT yet commissioned"*.
Measured at HEAD: **`J 40` is `CU` -- COVERED-UNFIRED.** It was banked by the
`proximity-field` wave, which is in this tree's history. The queue is dated at
master `9dbaad2` and says of itself *"a dated snapshot, not a claim about the
present"*, which is the document behaving correctly. `N 134` and `P O3` from the
same section **are** still GAP and are carried into bucket 1 above.

**6.3 The write ceiling's 152 reads 151 at HEAD.**
`_audit/2026-09-21-the-write-ceiling.md` headlines *"5 of 157 moved. 152 stay"*,
scoped to `profile.md`, `network.md` and `messaging-and-content.md`. Measured at
HEAD those three carry **W 151 and R+W 3**, and `jobs.md` contributes no
direction at all. The compound-rows wave repaired `M C85` from `W` to `R+W`
in place, which is a `-1` on W. **Stated as consistent with the difference
rather than as proof of it** -- that document's population was not re-derived
row by row, and saying "this explains it" without doing so is the inference this
corpus keeps removing from rows.

---

## 7. RESIDUAL -- WHAT COULD NOT BE MEASURED, AND EXACTLY WHAT WOULD SETTLE IT

**7.1 Whether bucket 3 is really blocked on nothing.** 61 is an upper bound.
THE INSTRUMENT THAT WOULD SETTLE IT: a per-row ADDRESS for each read-direction
GAP row, run through the shipped `readonly.is_read_url`. A row whose address is
already admitted and that no tool reads is blocked on code alone;
`_audit/2026-09-19-the-read-rows.md` calls this the bought-and-unread shape and
did it **by hand for 39 rows**. It cannot be automated today because **the census
records addresses in prose, not in a column** -- so the precondition is a schema
decision, not a script. At the read-rows wave's demonstrated rate this is a
bounded, unglamorous job.

**7.2 The `- 2 stateless` term in the published capability denominator.** 762 is
what the tree computes; 761 is published; 760 is in the counter's docstring.
Section 1.1 closes one of the three futures 2026-09-19 could not separate and
localises the remaining difference to that one term. **It is not corrected here:
the denominator's owner is the counter's, and an uncoordinated edit is how 761
became unreproducible.** WHAT WOULD SETTLE IT: one line from whoever owns
`count_census_states.py` saying whether `J 58` and `M C53` are meant to be
subtracted from a total they are already outside of.

**7.3 Whether 275 GAP rows are the real remainder.** Every figure here is over
the census as written. `mcp-inventory.md` states that the never-considered is
*"not enumerable from inside the repo at all"*. WHAT WOULD SETTLE IT: nothing in
this repository. It is an outward walk of LinkedIn's surface, which is what
produced the four slices in the first place, and no instrument can find what
nobody enumerated.

**7.4 Whether the 151 write rows would move if the standing ruling changed.**
Not measured here. `_audit/2026-09-20-the-write-partition.md` reports that
turning writes on would move none of it and that R2's headline claim is false at
HEAD; that claim was **not** re-derived by this wave and is cited, not adopted.

**7.5 How long any of it takes.** Not derivable. No duration appears in this
document, and a reader who needs one should be given the bucket sizes and asked
which bucket they want cleared.

---

## 8. PROCESS NOTES

**Delegation.** Two `implementer` children produced closed-form inventories --
the tool/capability surface and the blocker inventory -- each writing to a file
and returning its path. **Both were reviewed before anything entered this
document, and one relayed figure was overturned by doing so:** a child correctly
reported that `count_census_states.py`'s docstring paraphrases
`mcp-inventory.md`'s vocabulary as three states when the file's own table gives
six. A second child's claim that the P-R block's 44 items carry no row ids was
re-read directly against `profile.md` before section 1.1 was written, because it
closes a question another wave left open.

**Both children escalated an unexplained writer in this worktree** -- four
untracked files appearing between two `git status` calls four minutes apart, on
tasks that touched nothing in the repository. **The writer was me**, building
this wave's guard while they measured. They were right to refuse to guess and
right to report it: from inside a brief that maps no neighbours, a parent's
edits and an intruder's are indistinguishable. A coordinator ruling at this
worktree's root independently closed the same false alarm.

**The coordinator's ruling was verified against disk before being acted on, and
it held**: its stamped reading (`master @ f729a2a`, `GAP 275, stated rows 704`)
matches this wave's measurement exactly. Its one open question -- whether the
disagreeing GAP counts are competing claims or dated snapshots -- is answered in
section 6.1, by measurement rather than by hypothesis, which is how it was
asked.

**The impact gate, and what it says it did NOT run.** First run REFUSED with 4
red -- `test_the_audit_index_is_derived` (x2), `test_the_rulings_register_is_derived`
and `test_a_correction_is_findable_from_the_claim::test_every_candidate_pair_is_declared_or_triaged`.
All four are the designed consequence of adding an audit document: two derived
views needed `--write`, and the correction register found 5 candidate pairs. One
of those five is a real correction and is DECLARED with its back-pointer (the
`J 40` staleness above); the other four are triaged in the register with a
written reason each. **The gate's own disclosure, quoted rather than
paraphrased:**

    NOT CHECKED: 179 of 209 test files (85.6% of the suite by file).
    The corpus-wide guards DID run, so the identity, credential and page-text
    sweeps cover the whole tree. Everything else above is unexamined.
    That is roughly 4337 of 6094 tests unrun (71.2%).
    THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
    certifier; a green gate here is not a reason to shrink that matrix.

That is the correct reading of this wave's risk: the 15 corpus-wide guards --
identity, credentials, page text -- swept the whole tree, and this wave's own
files are pure ASCII and carry no identifier, verified separately. What is
unexamined is 71 percent of the suite, and CI is the certifier.

**Read-only throughout.** No browser was launched, no network call made, no
write fired. No file under `_audit/_census/` was edited -- this wave measures and
guards, it does not reclassify. Every mutation in every demonstration was planted
in a scratch copy whose isolation was ASSERTED, not eyeballed, and restored byte
for byte with a clean control run at the end.
