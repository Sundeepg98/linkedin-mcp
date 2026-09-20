# The reason kinds

Every census cell that writes off a capability rests on a reason. This pass sorts all
**309** of them by the KIND of fact the reason asserts, because the corpus spells three
very different things the same way and only one of them is stable.

Read-only. No browser, no LinkedIn session, no page load, no mailbox, no write fired.
Everything below is measured against the committed tree and is re-runnable offline.

Repo at `cd08e05` when the measurements were taken; the instrument lands at `b839c85`.

**0 census rows were moved.** That is the expected result and it is stated first so
nothing below reads as a re-adjudication. Where a reason looks false, it is reported as a
candidate with its evidence and the row is left exactly where it is.

**Prior art this builds on rather than repeats.**
`_audit/2026-09-20-the-contingent-writeoffs.md` named this class, proved it costs real
rows, and measured the predictor (a contingent write-off carrying a reopener is 15% still
GAP; one carrying none is 91%). `_audit/2026-09-20-the-live-capture.md` s13 classified the
13 Premium exclusions and contributed the taxonomy refinement this document adopts.

---

## 1. THE TAXONOMY, AND THE ONE SPLIT THAT DOES THE WORK

| kind | what it asserts | what re-checking it costs |
|---|---|---|
| **US-RULING** | somebody here DECIDED this | nothing -- read the ruling |
| **US-BOUNDARY** | a line somebody TYPED in our allowlist / denylist / forbidden substrings | nothing -- read one file |
| **WORLD-FACT** | what LinkedIn draws, offers or retired; geography; policy; another codebase | a page load, or a help fetch |
| **ACCOUNT-FACT** | what THIS account holds, is rendered, or would spend | a page load on his session, or his answer |
| **PROCESS-FACT** | a refusal read off a RUNNING server rather than off the file | restart and re-ask |

**US-BOUNDARY is split out of US-RULING and the split is not a preference.** Both are
ours, but a ruling is a decision somebody defended and a boundary entry is a line somebody
typed. `the-live-capture.md` s12.1 is this session's proof that the second can be flatly
wrong while looking settled: `/jobs/alerts/` was ALLOWED by our own gate and redirected
away to an address sixteen enumerated guesses had missed, wrong for fifteen days. Billing
that as "decided" is false, and the four-way split says so where a three-way one cannot.

**The split that actually does the work is two-way.** US-RULING and US-BOUNDARY are OURS:
re-checkable by reading this tree, and stale only when we act. The other three are
**CONTINGENT** -- they depend on something outside the codebase, and **nothing in the cell
says so.**

---

## 2. THE HEADLINE MEASUREMENT

    slice                      write-offs  US-RULING  US-BOUNDARY  WORLD  ACCOUNT  PROCESS  CONTINGENT  UNCLEAR
    jobs.md                            48         39           12      5       11        0          12        1
    profile.md                        112         88           50     10       11        0          18       11
    messaging-and-content.md           48         41           14      2        8        0          10        2
    network.md                        101         61           46      9       19        0          24        4
    ----------------------------------------------------------------------------------------------------------
    TOTAL (kinds overlap)             309        229          122     26       49        0          64       18

Kinds overlap because a reason may assert more than one; the exact single-count verdicts:

    US-RULING                                       115
    US-BOUNDARY+US-RULING                            67
    US-BOUNDARY                                      40
    UNCLEAR                                          33
    ACCOUNT-FACT+US-RULING                           20
    US-RULING+WORLD-FACT                              8
    ACCOUNT-FACT+WORLD-FACT                           7
    ACCOUNT-FACT                                      6
    US-BOUNDARY+US-RULING+WORLD-FACT                  4
    WORLD-FACT                                        3
    ACCOUNT-FACT+US-RULING+WORLD-FACT                 3
    ACCOUNT-FACT+US-BOUNDARY+US-RULING                2
    ACCOUNT-FACT+US-BOUNDARY+US-RULING+WORLD-FACT     1

**64 of 309 write-offs are CONTINGENT, and 40 of those carry no reopener.** Those 40 are
section 6, and they are the point of the document.

**THE PREDICTION THIS DOCUMENT MADE AND THEN TESTED.** An earlier draft reported 54
contingent and said: *10 UNCLEAR rows are known to rest on a ruling that is itself part
ACCOUNT-FACT, and resolving that alone would put contingency at 64.* Implementing the
section-heading resolution (3.2) landed it on **exactly 64**, and took UNCLEAR from 33 to
24. Three further spelling fixes took it to **18**. The figure is reported this way
because a number that was predicted and then hit is worth more than one that was merely
measured.

**64 IS STILL A FLOOR.** 18 rows remain UNCLEAR; section 7 says which of those are the
census's silence and which are my instrument's vocabulary.

---

## 3. THE FINDING UNDER THE CLASSIFICATION: THE CORPUS IS A POINTER GRAPH, NOT PROSE

This is the part worth reading even if the taxonomy is uninteresting.

**127 of the 309 write-off reason cells -- 41% -- are not reasons. They are references.**
`network.md`'s median write-off reason cell is **fourteen characters**. Six dialects:

| dialect | cells | resolves to | how fragile |
|---|---:|---|---|
| **BACKREFERENCE** `same`, `same gate`, `same measurement` | 46 | the nearest preceding substantive row **in the same table** | **BY POSITION.** Transitive: `P D17` -> `D16` -> `D15` -> `D14` |
| **RULING CODE** `R4. NOT-REV`, `R1 + R2` | 72 | a `### R<n>` section in `network.md` | stable, but the body is where the argument is |
| **SECTION HEADING** | 9 | the table's own `###` heading | **invisible to every row-level reader** |
| **RETIREMENT** `RETIRED 2026-09-05, X (3.13)` | 38 | argument inline + `decide-retire-rulings.md` | the only queue carrying reopeners |
| **FAMILY RULING** `/edit/ family ruling` | ~14 | a named ruling | fine |
| **NAMED KEY** `delete_or_withdraw_anything` | ~20 | a `PERMANENTLY_FORBIDDEN` entry in `writes.py` | fine |

**Three of these were not in my design; they were found by measuring the failures of the
previous draft.** That is recorded because it is the standing law here: every fresh
instrument built in one session had a bug on its first attempt.

### 3.1 The backreference is the most fragile construct in the census

46 cells resolve **by position** to the row physically above them. Nothing marks a cell as
load-bearing for the rows beneath it, so **a row inserted into the middle of a table
silently re-points every `same` below it**, with no error and no warning. The chains are
real and they are long: `P D15`, `D16`, `D17` all reach their argument only at `D14`, and
the `P I5`-`I10` block is six rows deep on one donor.

This is measured, not asserted -- see the mutation harness, section 8, M7.

### 3.2 Ten rows whose entire reason lives in a heading

`network.md` section K is titled

    ### K. Recommendations (10) -- all EXCLUDED-RULED under R3

and **not one of `N 119`-`N 128` carries that attribution in any cell.** Those rows ship
four columns (`# | capability | R/W | state`) with no note column at all, so there is
nowhere to put it. A reader who lands on `N 126` from the blocker map sees a capability, a
state, and no argument whatsoever.

**Confirmed from two independent directions, which is why it is stated as a measurement
rather than an impression.** R3's own body declares `Rows: 111, 112, 113, 119-128` -- 13
rows. A parse that looks for a standalone `R<n>` token in **every cell of every stated
row** finds **4**. The set difference is exactly the ten:

    R3   declared (the ruling's own Rows: block)  13
         found citing it anywhere in a cell        4
         in DECLARED, not FOUND                   N 119 ... N 128   <- all ten

For contrast, five of the nine codes that declare a row set match element for element
(R1 14/14, R4 14/14, R5 6/6, R6 1/1, R8 1/1), so this is not a slack parse -- it is one
block of the census attributing ten rows in a place no row can see.

This is the same disease `the-contingent-writeoffs.md` s3.5 measured one level up -- a
reason that is real, careful, and **unreachable from the artifact people actually read**.
There it was a blocker whose argument lived two documents away; here it is a heading one
line above the table.

### 3.3 21 write-off rows carry no reason cell at all

`N 67`-`N 78` and `N 119`-`N 128`. Eleven of them recover their reason from an R-code
written **inside the state cell** (`EXCLUDED-RULED (R11)`); the other ten are section 3.2.
A parse that takes "the last non-empty cell" as the reason -- which my first draft did --
silently returns the string `EXCLUDED-RULED` as the reason for all 21.

---

## 4. THE PREMIUM ROWS, RECONCILED RATHER THAN RE-DERIVED

The 13 Premium exclusions were classified by a live wave and pushed as `9a140a3` before
this brief went out; that work is adopted, not repeated. **What this pass adds is a
reconciliation, because "the 13 Premium rows" denotes different sets depending on who is
asking, and two of the three reasons quoted to me belong to rows that are not written off
at all.**

### 4.1 Two defensible definitions, and they share only three rows

| definition | count | states |
|---|---:|---|
| `9a140a3` s13.2 -- Premium ENTITLEMENT rows, chosen semantically | 13 | all EXCLUDED-RULED |
| `premium` appearing anywhere in the row's raw line | 34 | 18 GAP, 11 EXCLUDED-RULED, 4 COVERED-PROVEN, 1 MEASURED-ABSENT |

The write-off subsets are 13 and 12. **Their overlap is three rows** -- `M 4`, `M 39`,
`N 157`. Neither is wrong; they are answers to different questions, and the phrase "the 13
Premium rows" should not be used without saying which.

### 4.2 Two of the three spot-checked reasons are not write-off reasons

The brief cited three reasons as examples of Premium exclusions. Resolved against the
tree:

| quoted reason | row(s) | actual state |
|---|---|---|
| "a whole separate product that opens in LinkedIn Learning in a new tab" | `J 132`-`138` | **`J 132`-`135` EXCLUDED-RULED; `J 136`-`138` GAP** |
| "US-only Premium overlay" | `J 150` | **GAP** |
| "spends a non-refunding monthly credit" | `J 78`-`83` | **all six GAP, reason cell literally `--`** |

All three are quoted from `jobs.md` section 2, whose heading is **"WHAT EACH GAP WOULD
TAKE"**. It is a COSTING table: by construction every row in it is a GAP row, it has no
state column, and the shipped counter correctly drops all 12 of its Premium lines as
unstated. **They are cost notes, read as write-off reasons.**

### 4.3 Which makes the answer to the operator's question better than "ruled out"

Of the 24 rows in the three `jobs.md` sections whose heading names Premium:

    GAP              17
    EXCLUDED-RULED    4      (J 132-135, the spoken AI interview)
    COVERED-UNFIRED   2
    COVERED-PROVEN    1

**Seventeen of twenty-four are open GAP rows nobody has built, six of which carry an empty
reason cell.** Combined with `9a140a3` s13.4 -- 18 Premium GAP rows, none blocked on the
subscription, and not one of the 13 exclusions resting on the entitlement either -- the
answer stands: **the subscription is the blocker exactly zero times.** The coverage gap is
unbuilt work, not adjudicated refusal, and that is a cheaper problem.

### 4.4 One Premium row is its own reopener

`J 134` -- *"Practice by reading and typing responses instead"* -- is EXCLUDED-RULED on the
boilerplate shared by its four siblings: the practice interview is a real-time SPOKEN
session needing camera and microphone, **REOPENER: a text-only interview mode.**

The cell opens by quoting LinkedIn's own help text: **"read and type out your responses"**.
So the evidence the row cites documents the very mode whose absence writes it off, and the
stated reopener condition is the row's own capability text. Nothing here measured whether
LinkedIn draws a text mode; the row inherited a reason written about its voice siblings.

Adjudicated WORLD-FACT, pinned. **The row is not moved** -- settling it needs a load, which
this pass does not do.

---

## 5. WHAT I SHIPPED, AND WHY IT IS DERIVED RATHER THAN WRITTEN DOWN

`scripts/classify_writeoff_reasons.py`, plus `_audit/_census/reason-kind-adjudications.tsv`.

Three designs were available and the brief asked me to argue the choice.

**(a) A hand-written table of 309 classifications.** Rejected. It is stale the day after it
is written, and this corpus is already full of that failure: s4.1 of
`the-contingent-writeoffs.md` found four of six hand-written locators dead, one landing on
a DIFFERENT row that read COVERED-PROVEN, so a reader checking a GAP found a covered row
and stopped.

**(b) The tag written INTO each cell, so it travels with the row.** Rejected, and the
mechanical objection is the weaker of the two. Mechanically: it means editing 309 rows
across four files that sibling waves are writing right now -- a guaranteed conflict that
corrupts attribution for work that is not mine. **The real objection is that an in-cell tag
is still hand-maintained.** It is written once, against the reason that was there that day.
When somebody rewrites the reason -- which happens constantly here; `M C52` carries the
words *"CORRECTED 2026-09-19 BY THE WAVE THAT GOT IT WRONG, SECOND TIME TODAY"* -- the tag
does not follow. A wrong tag that travels with the row is worse than no tag, because it
looks maintained. That is this wave's own subject matter applied to its own deliverable.

**(c) Derived, with a pinned hand overlay. Chosen.** The rule re-runs over whatever the
cells say today, so the mass tracks the text for free. Where the unit of reasoning is not
the cell, a committed adjudication supplies the kind **by row id, never by line number**,
and **each adjudication pins a verbatim quote from the thing it rules on.**

**The quote is the entire mechanism.** `--check` fails when a pinned quote stops being
present. So when somebody rewrites a reason out from under a hand judgement, the judgement
goes **red and loud** instead of silently mislabelling the row. That is the one property
(a) and (b) cannot have: **a hand judgement that invalidates itself when its evidence
moves.** All 12 adjudications currently pin clean.

### 5.1 The eleven rulings are the adjudication unit, not the row

72 rows point at eleven `### R<n>` sections. The first draft keyword-matched each row
against the whole body it pointed at -- so a row whose entire cell is `R2` was classified
against R2's 926 characters and came out `ACCOUNT-FACT+US-BOUNDARY+US-RULING`, a three-kind
verdict carrying no information. **87 of 309 rows had zero signals in their own cell.**

Eleven hand judgements now cover 72 rows, which is the leverage a derived approach is
supposed to buy. Two of them are worth quoting:

- **`R2` = US-BOUNDARY.** Four substrings -- `invitation`, `/invite`, `/connect`,
  `/withdraw` -- checked BEFORE the allowlist. The ruling's own text admits the collateral:
  the connections list is unreachable **only because its address contains `/invite` and
  `/connect`**, *"two substrings put on the list to stop invitations, catching a read that
  has nothing to do with inviting anyone."* 20 rows rest on it and not one says it is a
  line rather than a decision.
- **`R9` = ACCOUNT-FACT+US-RULING+WORLD-FACT**, the most contingent ruling in the slice,
  and its name says none of it. One of its four grounds is arithmetic over an allowance --
  *"He has 5 InMail credits a month... That is roughly one send per week. Automating five
  actions a month is not engineering, it is ceremony"* -- plus *"he now also has a paid
  subscription that a restriction would strand."* Both are account facts. The argument
  weakens the moment the allowance changes, and nothing would say so.

### 5.2 Four defects in my own drafts, every one found by measurement

Recorded so the method is visible, and because two were found by a child's independent
extraction rather than by re-reading my own code.

1. **Heading scanning was not fence-aware.** `network.md` quotes other documents' markdown
   headings inside ``` fences. A scanner that does not track fences ends R1's body at line
   644 and R9's at 776 -- **truncating each ruling at exactly the quote it rests on.**
2. **"The last non-empty cell" returned the STATE cell on 21 rows** whose tables have no
   note column (section 3.3), making the reason of `N 120` the string `EXCLUDED-RULED`.
3. **`third-party` was tagged WORLD-FACT.** It fired 50 times, 41 of them inside R4's body
   -- and R4 is *"loading a third party's profile is permanently forbidden"*, which is OUR
   prohibition. Retagged US-RULING.

4. **Backreference inheritance silently never ran** -- the donor key was recovered by
   re-parsing a label with `(\S+)`, and every row key in this corpus contains a space.
   46 rows were affected; UNCLEAR was inflated by 17 and contingency understated by 5.
   Found by the mutation harness, not by re-reading the code. Section 8.3.

And a fifth, a dead needle: `separate product` never fired because the corpus writes *"a
separate LinkedIn Learning product"*, with two words in between. **A needle that never
fires and a fact that is never true look identical in a count**, which is why section 8.2
tests every zero-firing signal against a synthetic positive.

---

## 6. THE RE-EXAMINATION LIST

**40 write-offs rest on a fact about him or the world, and carry nothing that would ever
say it had changed.** Ordered by what it would cost to settle, cheapest first. The full
machine-generated list is `classify_writeoff_reasons.py --contingent`; this is its
structure, which is what makes it actionable.

### TIER 1 -- settles by reading one file in this repo. Cost: zero page loads.

| rows | capability | why it is contingent |
|---|---|---|
| `M C52`, `N 10`, `P N20` | feed preferences, withdraw an invitation, calendar sync | each carries a US-BOUNDARY **and** a WORLD-FACT, so the cell cannot tell you which one is binding. If the boundary is the binding half, it is a one-line change |

**These are the cheapest possible re-checks and the `/jobs/alerts/` scar is what makes them
worth doing:** a boundary entry can be wrong for fifteen days while looking settled. Confirm
the substring still does what the cell says, then decide which half binds.

### TIER 2 -- one instrument this repo already ships. Cost: one page load.

| rows | capability | the mechanical trigger |
|---|---|---|
| `N 111`, `N 112`, `N 113`, `N 118`, `P E4`, `P E5`, `P F2`, `P F6`-`F9`, `P O2` | the whole endorsement / recommendation family -- **11 rows**, and 10 more sit behind the same ruling in `N 119`-`N 128` | `R3`'s refusal rests on a MEASUREMENT taken on his own profile: *zero endorse controls among the 222 controls read live 2026-08-30.* **One endorsement received and the line is drawn.** The trigger is that count going non-zero, and the probe exists: `scripts/_probe_endorse_and_follow_lines.py` |

**This is the largest contingent cluster in the census and it was already suspected:**
`the-contingent-writeoffs.md` s3.6 flagged `ENDORSE-SUBSTRING-OVERREACH` as an account fact
wearing a code-fact name. This pass reaches the same conclusion from the opposite
direction -- row cells rather than blocker names -- which is independent agreement, and it
adds the row count and the instrument.

### TIER 3 -- the InMail family, where the measurement has already been taken twice.

| rows | capability |
|---|---|
| `M M2`, `M M4`, `N 156`, `N 157`, `N 158` | InMail send, balance, Open Profile message |

See section 6.1: for two of these the re-check is not a measurement at all, it is a
cross-reference.

### TIER 4 -- needs his answer or a live read.

`M M39` (away message), `M C20` / `M C21` (repost), `N 57` (newsletters subscribed),
`N 131` (anonymous viewer identity), and the `P D13`-`D17` block (licenses, courses,
projects, publications, patents) -- which is a single backreference chain, so it is **one**
judgement wearing five row ids, not five independent ones.

### 6.1 THE SHARPEST SINGLE ITEM: one capability, three rows, two states, and the correction reached one of them

| row | capability | state |
|---|---|---|
| `J 127` | Read the InMail credit balance | **GAP** |
| `M M4` | View available InMail credit balance | **EXCLUDED-RULED** |
| `N 157` | View your available InMail credits | **EXCLUDED-RULED** |

`J 127`'s cell reads:

> **RE-OPENED 2026-09-20.** The MEASURED-ABSENT verdict rested on a reading that could not
> have produced it: the only instrument that has ever opened `/premium/my-premium/` tallies
> 16 self-authored needles, 8 entitlement and 8 upsell [...]

`M M4`'s cell rests on exactly that finding, about exactly that page:

> `readonly.py:411-433` admits `/premium/my-premium/` for exactly this and **it carries no
> balance**

**The correction that reopened `J 127` this morning did not propagate to its twin.**

**And the honest other half, which cuts against the finding:** `9a140a3` s13.3 re-measured
`M 4` today with a **stronger** instrument -- a whole-document rendered-text census reading
`inmail` 0 and `credit` 0 on that page -- and it holds. So `M M4`'s CONCLUSION is now
supported. What is wrong is the cell, which still cites the weak instrument, and the state
disagreement between three rows describing one capability.

**Cost to settle: zero new measurements.** Cite s13.3 in `M M4` and `N 157`, and mark the
three as duplicates under the rule master landed at `9f50087` -- *a duplicate row is
MARKED, never DELETED*.

### 6.2 PROCESS-FACT: measured zero, and the needle was proved alive

Zero write-off reasons rest on a refusal read off a running server. **This is a real zero,
not a dead needle** -- section 8, P1, feeds the pattern a synthetic positive and confirms it
matches. Worth stating because the category was live: master carries `0a7836f`, *"the server
that answered section 3 was 58 commits stale."* The hazard is real; it has simply not
reached a census reason cell.

---

## 7. WHY THE 50 UNCLEAR ROWS ARE UNCLEAR, AND WHICH ARE MY FAULT

UNCLEAR is the honest answer only when nobody could tell from what is written. It is **not**
honest when my rule simply does not know a spelling, so the 50 are split:

UNCLEAR fell **50 -> 33 -> 24 -> 18** across three corrections: backreference inheritance
(8.3), section-heading resolution (3.2), and three spellings the rule did not know. Every
one was found by reading the UNCLEAR bucket rather than by design, which is the argument
for printing it at all.

The **spellings** were worth fixing because they were not ambiguity, they were vocabulary:
`P M1`/`M2`/`M4`-`M7` and `P N29` say *"the FIRST entry on the forbidden TUPLE"* where the
rule knew only "forbidden substring"; `P I4`-`I10` say *"editor never loaded"*, the
NEVER-LOADED ruling by its lowercase name. Fourteen rows, all plainly US-BOUNDARY or
US-RULING, sitting in UNCLEAR because of a word.

**The remaining 18, and who is at fault for each:**

| cause | rows | whose fault |
|---|---:|---|
| a `same` chain whose donor is itself undecidable | ~5 | the chain |
| the reason is a retirement whose argument is a shape, not a subject (`N 107`, `N 108` -- *"a step INSIDE an import, so it has no life if the import cannot run"*) | 2 | nobody's |
| genuinely undecidable from what is written -- `P I12` *"measured: zero of 237 urls reach one"*, `N 101` which flags its OWN blocker as stale | ~11 | nobody's -- UNCLEAR is the right answer |

**UNCLEAR is now mostly the census's silence rather than my instrument's vocabulary**,
which is the state it should be in before anybody quotes it. It is not zero and should not
be: a classifier that can always decide is not measuring anything.

---

## 8. THE GUARD, SHOWN FAILING

`tests/test_writeoff_kinds_are_derivable.py` -- **69 tests, 8.6s**, driven over **mutated
sandbox copies** of the census. No committed file is written at any point.

The first version was mine and had 11 tests. It was replaced by a colder, independent one
that runs each mutation against EVERY slice rather than only the one the design document
names, asserts byte-identical output on the calibration rather than equal verdicts, and
writes through with `newline=""` because **the slices are CRLF and my version was
silently rewriting their line endings**. Its findings are in 8.3; two of the three are
defects in my instrument that I did not find by re-reading my own code.

| mutation | what it does | verdict |
|---|---|---|
| **M1 per-file** | empties `network.md` of all 101 write-offs, leaves J/P/M at 48/112/48 | **RED** -- `--check` exit 1, *"network.md contributed ZERO write-off rows"* |
| **M2 pinned quote** | rewords R2's pinned evidence by two words | **RED** -- *"ADJUDICATION for RULING R2 pins the quote ... which is NO LONGER PRESENT"* |
| **M3 moot adjudication** | moves `J 134` from EXCLUDED-RULED to GAP | **RED** -- the row-level judgement reports itself moot |
| **M4 missing ruling** | deletes the whole `### R5` section | **RED** -- 6 rows citing R5 report it has no ruling section |
| **M5 empty corpus** | empties all four slices | **RED** -- *"An empty result is a loud event here, never a silent pass"* |
| **M7 backref fragility** | plants one row between `P D14` and `P D15` | **RED** -- see below |
| **M8 calibration** | one space in a CAPABILITY cell, reason untouched | **GREEN** -- verdicts identical |

**M1 is the one that matters most and it nearly did not get tested.** In that state the
other three slices still hold 208 write-off rows, so **a union assertion over 309 would
pass** -- which is precisely why it is asserted per file.

**M8 is the calibration, and it is not decorative.** A harness where every mutation goes
red is not discriminating; it is broken.

### 8.1 M7, the measurement of the census rather than of the script

    row      donor BEFORE   donor AFTER   kind BEFORE            kind AFTER
    P D15    P D14          P D14b        US-RULING+WORLD-FACT   WORLD-FACT
    P D16    P D14          P D14b        US-RULING+WORLD-FACT   WORLD-FACT
    P D17    P D14          P D14b        US-RULING+WORLD-FACT   WORLD-FACT
    donors re-pointed silently: 3 of 3      problems raised: 0

One planted row re-points all three dependents, **changes their classification**, and
raises nothing. That is not a defect in the classifier -- it is what `same` means.

### 8.2 Ten signals fire zero times, and all ten needles are alive

A needle that never fires and a fact that is never true look identical in a count, so every
zero-firing pattern is fed a synthetic positive. **All ten match; there are no dead
needles.** That is what makes section 6.2's PROCESS-FACT zero a measurement:

    live-process   PROCESS-FACT   matches "measured off the live server, which is 58 commits stale"

### 8.3 FOUR DEFECTS THE HARNESSES FOUND -- THREE IN MY INSTRUMENT, ONE IN A HARNESS

**In the instrument, and it was silently wrong across 46 rows.** Backreference inheritance
read its donor by re-parsing the label `backref<-P D14` with `(\S+)` -- and **every row key
in this corpus contains a space**, so the capture stopped at `P`, the lookup missed, and
**inheritance never ran at all.** No error, no warning: every `same` row simply came out
UNCLEAR, which looks exactly like a census that never wrote a reason. Fixed by recording
the donor on the row instead of encoding it in a string. **UNCLEAR fell 50 -> 33 and
contingency rose 49 -> 54**, so the bug was materially distorting the headline.

**In the harness itself, and it is the same disease one level down.** M1's first version
rewrote state cells with one regex and left 12 of network.md's 101 write-offs standing --
because the corpus also writes `EXCLUDED-RULED (R11)` and `**COVERED-CANNOT-DELIVER**`. The
per-file control then passed CORRECTLY, and I was one step from recording it as *a control
that cannot fail*. **Asserting that a mutation changed bytes is not asserting that it
achieved its intent.** Every mutation now asserts its postcondition first. A second
instance of the same shape: M1 was checking `build()`'s problems list, while the per-file
control lives in `main(--check)` -- so it was asserting against the wrong surface entirely.

**A CONTROL OF MINE THAT COULD NOT FAIL, and it took a second reader to see it.** The
per-file control's second half read

    unkinded = [r for r in sub if not r.kind]

and `finalise` sets `r.kind = "UNCLEAR"` whenever the kind set is empty. **`r.kind` is
therefore never falsy and that branch was unreachable.** It printed *"all 112 write-off
rows carry a kind"* over four slices and could never have said anything else -- a control
computed, printed and structurally unable to fire, which is the exact defect this repo
built `scripts/detect_unbranched_probe_controls.py` to find in 129 other places. **That is
the second time this shape has turned up in my own work in one wave, so it is counted
rather than reported again.**

It is replaced with the invariant that actually broke: **a row resolved through a pointer
must end up carrying at least what it points at.** With inheritance disabled, that control
convicts 102 rows across all four slices (13 / 11 / 6 / 72) and names them:

    N 10 resolved through ruling<-R2+ruling<-R5 but is missing ['US-BOUNDARY', 'US-RULING']
    P A6 resolved through backref<-P A4 but is missing ['US-RULING']

The tautology it replaced would have stayed green through every one of those.

**AND MY DOCSTRING MADE A CLAIM MY CODE DID NOT HONOUR.** `forbidden_keys()` says every
fallback path returns the nine known names *"AND SAYS SO in the run header"*. `FKEYS_SOURCE`
was assigned once and **read nowhere**, so a reader of a FALLBACK run could not tell it was
one. That is precisely the half-truth this wave is auditing the census for -- an artifact
claiming more than it ran -- reproduced in the instrument doing the auditing. Now printed
on every run.

---

## 9. WHAT THIS PASS DID NOT DO

1. **It moved no census row.** 0 banked, as expected.
2. **It did not re-derive the 13 Premium exclusions.** `9a140a3` owns them; section 4
   reconciles rather than repeats.
3. **It opened no page and no mailbox.** Every contingent row in section 6 is reported with
   what would settle it, not settled.
4. **It did not fix the reason cells it found thin.** `N 119`-`N 128` still carry no reason;
   that is a census edit and siblings are in those files.
5. **The contingent count of 49 is a FLOOR.** Section 2 says why, and section 7 says which
   fixes would move it.
6. **The classification is only as good as the eleven ruling adjudications**, which are
   mine and are hand judgements. They are pinned to verbatim quotes so they fail loudly if
   the rulings change, but **a pin detects movement, not misreading**. Anyone who disagrees
   can run `--explain <row>` and convict the rule at the pattern rather than argue with the
   verdict.
7. **The re-check triggers are derived per KIND, not written per row.** That is deliberate
   -- a per-row table of 309 triggers is the hand-maintained artifact this whole design
   rejects -- but it means the trigger is the right SHAPE for a row rather than tailored to
   it. `--contingent` prints them tiered; section 6 is that output with the clusters named.
8. **One delegated slice failed and then did not.** The mutation child produced nothing on
   disk for 35 minutes, against a live process check and repeated `ls`. I wrote the harness
   myself rather than stay blocked on a hard requirement. It then delivered -- a better
   file than mine, which replaced it, and which found two defects in my instrument that my
   own harness had not. Recorded because "no output on disk" was indistinguishable from
   death for more than half an hour, and the recovery that mattered was doing the work
   anyway rather than waiting or re-spawning.
