# The reopener triggers

A write-off that rests on a fact about the world is excluded WHILE THAT FACT
HOLDS. With nothing stating what would falsify it, the row reads exactly like a
permanent exclusion -- and the census shrinks its own denominator by an amount
nobody ruled and nobody can measure.

`_audit/2026-09-20-the-contingent-writeoffs.md` named that class and measured
its cost: **a contingent write-off carrying a reopener is 15% still GAP, one
carrying none is 91% still GAP**, and every contingent write-off yet found
wrong sat in the second group, 5 of 5. This pass closes the second group for
the `EXCLUDED-RULED` / `XR` row-set, and ships the guard that keeps it closed.

Read-only with respect to LinkedIn: no browser, no session, no page load, no
`mcp__linkedin__*` call. Everything below was measured by running the shipped
instruments over the committed tree.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `M M4` moved EXCLUDED-RULED to MEASURED-ABSENT; its cell reports a measurement, and an exclusion is a decision.

**CORRECTS:** `_audit/_census/network.md` -- row `N 157` moved EXCLUDED-RULED to MEASURED-ABSENT on the same ground, and it was filed under a ruling about sending while being a read.

**CORRECTS:** `_audit/_census/profile.md` -- rows B2 and M1 and finding 7.11 called the upload ban package-wide and the verb unsanctioned; one call site has been sanctioned since 2026-09-04, and no state moved.

---

## 1. THE POPULATION, RE-DERIVED RATHER THAN INHERITED

The brief handed me "roughly 40 contingent write-offs with no reopener." **That
figure is right about the corpus and wrong about this row-set**, and the
difference is worth stating precisely rather than confirming.

| measured at `e6b11e5` | all write-off states | `EXCLUDED-RULED` + `XR` only |
|---|---:|---:|
| write-off rows | 310 | **290** |
| of which CONTINGENT | 65 | **59** |
| ... carrying a REOPENER | 25 | **22** |
| ... carrying NONE | **40** | **37** |

**The real number for this row-set is 37, not 40.** The other three are
`M M2` and `N 57` (`COVERED-CANNOT-DELIVER`) and `N 118` (`MEASURED-ABSENT`) --
different state classes, outside the row-set I was scoped to. The 40 is a
correct count of a wider population.

Census totals at `e6b11e5`, for the record: 704 stated rows, `EXCLUDED-RULED`
267, `XR` 23, `GAP` 300, `COVERED-PROVEN` 39, `COVERED-UNFIRED` 27,
`COVERED-CANNOT-DELIVER` 15, `MEASURED-ABSENT` 5, plus the `CP`/`CU` short
spellings at 20 and 8.

### 1.1 The instrument's blind spot, measured rather than assumed

`contingent` is a DERIVED verdict, and 14 rows in this row-set come back
`UNCLEAR` -- the rule could not read them, so they are neither convicted nor
cleared. An undercount hiding there would make 37 a floor rather than a count,
so all 14 were adjudicated by hand against their cells and against each slice's
own section 6.

**Three are contingent in substance and the rule missed them:** `J 144`,
`N 107`, `N 108`, all `AI-INTERVIEW-PRODUCT` / `CONTACT-IMPORT` retirements
resting on what LinkedIn offers. **All three already carry a reopener**, so the
derived contingent count of 59 is an undercount by 3 and **the no-trigger
count of 37 is exact and unaffected.** That is the result that mattered.

**Eleven are genuinely not contingent**, and the reason is worth recording
because the cells do not show it. `P I4`-`I10` read *"editor never loaded"* and
`P I12` reads *"measured: zero of 237 urls reach one"* -- which look like
non-measurements masquerading as rulings. They are not: `profile.md`'s own
section 6 attributes `I2`-`I12` and `B6` to the **`set_open_to_work` spec**, a
ruling of ours. The cells are terse shorthand over that ruling and are
unreadable without section 6. `P B6`, `P N29` and `M M3` likewise resolve to a
spec residue clause, a forbidden-tuple entry and a lead ruling. **No row was
moved on this finding**; it is recorded so the next reader does not re-open it.

---

## 2. WHERE A TRIGGER BELONGS, AND WHY NOT ON EVERY ROW

The 37 are not 37 arguments. They cluster into 14 families, and **16 of them
resolve through a pointer into a shared ruling** -- `R3`, `R6`, `R9` in
`network.md` -- while five more inherit by backreference from a donor row.

Two facts settled the design:

1. **Ten of the 37 have NO REASON CELL AT ALL.** `N 119`-`N 128` sit in a
   four-column table with no note column. There is physically nowhere on those
   rows to put a clause. The only place their reopener can live is the ruling
   they point at.
2. **A tag copied onto 37 cells is hand-maintained by definition.**
   `classify_writeoff_reasons.py`'s own design section rejected the in-cell tag
   on exactly this ground: when a sibling rewrites a reason -- which happens
   constantly in this corpus -- the tag does not follow, and a WRONG tag that
   travels with a row is worse than none, because it looks maintained.

So **the trigger goes where the contingent fact is asserted**: the ruling body
for a ruling-resolved family, the donor cell for a backreference, the row's own
cell otherwise. That is also how the 22 rows that already had one are written.

**THE COST IS NAMED RATHER THAN HIDDEN.** A backreference resolves BY POSITION,
so a row inserted above a donor silently re-points it and a reopener can
evaporate with no edit to the row relying on it. That is a real fragility and
it is why this ships as a GUARD rather than as a one-time repair -- the
evaporation becomes a red run instead of a silent loss.

### 2.1 What changed

| where | covers | the contingent fact it names |
|---|---|---|
| `network.md` **R3** body | `N 111`-`113`, `N 119`-`128` (13) | zero endorse controls over 13 fixtures / the account's own skills surface / 222 live controls |
| `network.md` **R6** body | `N 131` (1) | what LinkedIn renders this account; *six of ten* is a dated reading |
| `network.md` **R9** body | `N 156`, `N 158` (2) | a five-a-month allowance, and a paid subscription a restriction would strand |
| `N 10` cell | itself | -- and the world-fact in it reopens NOTHING; see 2.2 |
| `P D13` cell | itself | the 404 is colour; the `/edit/` ruling is the reason |
| `P D14` cell | `P D15`-`D17` by backreference (4) | as `D13` |
| `P E4` cell | `P E5` by backreference (2) | the same measurement as `R3` |
| `P F2`, `F6`-`F9` cells | themselves (5) | recommendation rows written off on an ENDORSE count |
| `P N20` cell | itself | `mobile app only` is the contingent half and not the load-bearing one |
| `P O2` cell | itself | as `R6` |
| `M M39` cell | itself | the refusal turns on *did not read* |
| `M C20` cell | `M C21` by backreference (2) | a ruling AND an admitted unopened menu |
| `M C52` cell | itself | mechanical: `is_read_url` on the real address |
| `M M4`, `N 157` cells | themselves (2) | state corrected; see section 3 |

Two more were given triggers although they sit outside the row-set, because
leaving them would have made the class I had just tidied internally
inconsistent:

- **`N 118`** (`MEASURED-ABSENT`) -- **and its reopener was already built.**
  `dom.read_profile_detail_entries` has re-taken that reading on every call
  since 2026-09-04. What it lacked was the word `REOPENER`, so no instrument
  sweeping the census for re-check triggers could see it, and the row read as a
  permanent closure. Zero new code, one clause. **A trigger that exists in code
  and is not named in the cell is invisible to every reader who starts from the
  census**, which is this document's defect in its cheapest form.

### 2.2 THE 21 ROWS THAT HAVE NO REASON CELL -- TREATMENT, BY COUNT

`network.md` ships two four-column tables (`| # | capability | R/W | state |`)
with no note column at all, so 21 write-off rows have physically nowhere to
write a clause: `N 67`-`75`, `77`, `78` and `N 119`-`128`. The reason is
embedded in the STATE cell as `EXCLUDED-RULED (R3)` / `(R11)`. Three treatments
were available -- widen the table, write the trigger inline beside the code, or
declare them an exception with the count stated. **Silently skipping them was
not among them.** The split, measured rather than assumed:

| rows | count | contingent? | treatment |
|---|---:|---|---|
| `N 119`-`128` | **10** | YES (`ACCOUNT-FACT+US-RULING`) | **trigger written ONCE in `R3`'s body**, inherited by all ten through the code they cite |
| `N 67`-`75`, `77`, `78` | **11** | **NO** (`US-BOUNDARY`, resolving to `R11`) | **none needed.** A boundary entry is ours; re-typing it is a visible act, so it is its own trigger |

**No table was widened and no clause was written 21 times.** The per-CODE route
is available precisely because these rows cite `R3` and `R11`, and it is both
cheaper and more auditable than 21 hand-written triggers that would each go
stale independently -- the in-cell-tag failure mode the classifier's own design
section rejected.

The eleven are worth one more sentence, because "no reopener" and "needs no
reopener" look identical in a count and are opposite findings. `R11` is *the
settings family is admitted by name or not at all* -- a line somebody typed in
our own denylist. It can be flatly wrong while looking settled, which is why
`US-BOUNDARY` is split out of `US-RULING` at all; but it is OURS, and reading
one file re-checks it. That is a different class from a fact about LinkedIn
that nobody will ever be told has changed.

### 2.3 Two triggers that say a fact reopens NOTHING, and why that is the point

A reopener naming a fact that cannot actually move the row is decorative, and
decorative is the failure mode this repository has been finding all day. Three
cells were written the other way round deliberately.

`N 10` asserts *"LinkedIn DOES offer this -- verified against the Help
Center"*. That is the live-LOOKING half and it reopens nothing: it is already
TRUE and the row is excluded anyway. What holds `N 10` is `R5`
(`delete_or_withdraw_anything`) -- ours, settled-looking, and the half that can
actually move. **A reader taking the Help Center line for the trigger has it
exactly backwards**, so the cell now says so.

`P D13`/`D14` are the same shape: a Help article resolving would supply field
names the row records as UNVERIFIED and would not move the row an inch, because
the `/edit/` family ruling excludes it either way. `P N20` likewise -- a
calendar-sync control on the desktop settings surface falsifies *mobile app
only* and leaves the row where it is.

**A world-fact sitting beside a ruling is colour, not the load-bearing reason.**
Five of the 37 are that shape, and writing a reopener on the colour would have
produced five triggers that can never fire -- a check that cannot fail, at row
scale.

---

## 3. `M M4` AND `N 157` -- RESOLVED, AND THE PRIOR WAVE ASKED FOR THIS

Both read `EXCLUDED-RULED` while their reasons are measurements. Both are now
`MEASURED-ABSENT`.

**This is not a fresh opinion.** `_audit/2026-09-20-the-first-firing.md` s4d
named the defect in terms this pass has nothing to add to:

> **THEY STILL DIFFER IN STATE WORD, AND THAT IS A REAL DEFECT I AM NAMING
> RATHER THAN QUIETLY FIXING.** `M M4` and `N 157` read EXCLUDED-RULED, which
> means *somebody decided not to build this*. Their reasons are not decisions
> -- they are measurements [...] I am not re-stating two rows another wave
> committed four hours ago on a vocabulary question that is bigger than this
> wave. **The owner of the state vocabulary can rule it in one line.**

That wave declined on TIMING, not on substance, and left the ruling open. This
is that one line.

**The ground is a contradiction inside the census, not a preference.** `J 127`,
`M M4` and `N 157` assert ONE fact about ONE object -- the InMail credit
balance is not rendered -- and `J 127` already read `MEASURED-ABSENT` while the
other two read `EXCLUDED-RULED`. Three rows, one fact, two state words.

Three independent supports, none of them mine:

1. **`9a140a3` settles it from our own side.** The commit whose entire purpose
   was the kind distinction files `M 4` as **WORLD-FACT**, not `US-RULING`, in
   the table built to draw exactly that line.
2. **`network.md` section 2's definition fits without stretching:** *no tool,
   and a LIVE READING of the surface says LinkedIn does not draw the thing.*
3. **`readonly.py` ADMITS the address.** `/premium/my-premium/` is on the
   allowlist for exactly this purpose. **A row whose page we are allowed to
   open, and did open, cannot be written off as a refusal.**

And `R9` never covered `N 157` anyway: `R9` is outreach AUTOMATION and `N 157`
is a READ. `R9`'s row list is now 156 and 158.

Both rows keep their prior text verbatim under a `PRIOR TEXT, KEPT:` heading --
a row that records only its latest state cannot be audited -- and both carry
**the same reopener `J 127` already carries**, so the three now agree on trigger
as well as on substance.

**Count effect, and it touches no coverage number.** `EXCLUDED-RULED` 267 ->
265; `MEASURED-ABSENT` 5 -> 7; **`GAP` 300, unchanged; 704 stated rows,
unchanged; no capability added or removed.** Both slices carry a delta block in
the house style, with the frozen blocks left byte-identical so every document
citing them still resolves.

---

## 4. THE `\|` PARSE DEFECT -- FIXED, AND BOUNDED

`INSTRUMENTS.md` section 35 registered this as NOT AN INSTRUMENT:
`count_census_states.cells()` split on `|` without honouring the markdown
escape `\|`. The state was read correctly on every affected line -- which is
why no instrument ever caught it -- and the REASON came back as the TAIL AFTER
the escape.

The tail is not merely short, it is **syntactically valid**: it looks like a
whole reason cell, so nothing downstream can discriminate it from one.

Fixed with a left-to-right character scan (no regex -- the standard lookbehind
one-liner is wrong at a doubled backslash), and **bounded by its own control**,
`scripts/_check_cells_honours_escaped_pipe.py`, which carries the pre-fix
implementation verbatim and runs both over every line of five census files:

    lines carrying an escaped pipe : 5
    lines where old and new differ : 5
    ok    every changed line carries an escaped pipe -- no collateral

    jobs.md:156  row '`save_job`'  last cell 197 -> 296 chars
    jobs.md:161  (prose, not a table row)  33 -> 83
    jobs.md:243  row '50'   123 ->  168 chars
    jobs.md:316  row '103'  795 -> 1320 chars
    jobs.md:317  row '104'  302 ->  402 chars

**`J 103` held 1320 characters and handed back 795.**

**TWO RECONCILIATIONS, because a correct count of the wrong population reported
as a drift is the exact failure that cost this repo an hour the same afternoon.**

1. **Five lines, four rows, and both numbers are right.** `INSTRUMENTS.md`
   section 35 says four; the control above says five. Section 35 counts TABLE
   ROWS carrying an escaped pipe -- `jobs.md` 156, 243, 316, 317. The control
   counts LINES, and adds 161, which does not start with a pipe and is prose
   quoting another document. **Whenever either figure is cited, the population
   goes with it.**

2. **`J 50` is the sharper demonstration than `J 103`, and it is a row in this
   row-set.** `J 50` is `XR` -- a kept write-off -- and the naive split
   mis-splits inside `` `(saved\|applied\|draft)` ``, after which the
   "last non-empty cell after the state" rule grabs a fragment:

       J 50 reason cell   naive 124 raw / 123 stripped
                          escape-aware 170 raw / 168 stripped

   An independent extraction that did not strip the cell reported the raw pair,
   this repaired parser reports the stripped pair, and the two-character
   difference is surrounding whitespace. The same offset explains the brief's
   1322 for `J 103` against this parser's 1320: **both readings are confirmed,
   neither is contradicted.** `J 103` is `CU` and outside this row-set, so
   `J 50` is the one that actually cost a write-off row 45 characters of its
   argument.

`--demonstrate-red` runs the specimen suite against the old implementation and
asserts it fails **exactly four of six** -- the two carrying no escape must
still pass, or the repair's subject would be the parse in general rather than
the escape.

**NOTHING MOVED BUT THE TEXT.** Census counts before and after are identical,
and `classify_writeoff_reasons.py --tsv` is byte-identical across the fix on
all six verdict columns for all 310 rows (row, state, kind, contingent,
has_reopener, has_reason_cell). Section 35's standing requirement -- that any
notation change over these files carries the classifier in its proof -- is met.

---

## 5. THE GUARD

`scripts/check_contingent_writeoffs_carry_a_reopener.py`. It imports the
shipped classifier rather than reparsing, and fails the run if a write-off row
is contingent and names no reopener in its RESOLVED text.

**Resolved, not raw, and the choice is load-bearing**: 127 of the corpus's
write-off reason cells are pointers, and 21 rows carry no reason cell at all.
Reading the raw cell would demand the impossible of a fifth of the corpus.

### 5.1 Shown failing, twice, because one red was not enough

A verdict that fires on an injected row proves nothing about whether the walk
would ever hand it one. So `--demonstrate-red` runs both halves:

    RED 1 -- VERDICT LOGIC, on a synthetic row that never touches disk
      ok    the planted row is convicted: contingent, no reopener
      ok    and the same row WITH a reopener is cleared, so the rule
            discriminates rather than merely refusing

    RED 2 -- END TO END, on a COPY of the real census with one row planted
      ok    the walk found the planted row: J 9901 state=EXCLUDED-RULED
            kind=ACCOUNT-FACT+WORLD-FACT
      ok    the guard FAILED on the planted corpus
      ok    and it named the planted row rather than failing vaguely

Red 2 copies the four census files to a temp directory, plants one row inside a
live table, repoints the walker, and runs **the shipped `build()` pipeline end
to end** -- walk, pointer resolution, classification, pinned adjudications.
Reassembling a subset would have meant the red exercised a different instrument
from the green.

The planted reason is built from signals already in the shipped table
(`he-holds`, `entitlement`) rather than from a word invented for the test, so
the red proves the REAL rule fires rather than a rule written to be fired. And
Red 1's second half is the discrimination control: **a rule that convicts a row
carrying a reopener is not working, it is just failing.**

### 5.2 Four ways it could have been decorative, each closed and named

1. **An empty result would pass.** Asserted **per slice** -- a file yielding
   zero contingent write-offs is a LOUD failure naming the file. Per slice and
   never over the union: if `network.md` stopped being read, the other three
   would still satisfy a union assertion.
2. **An exemption list would grow into a rubber stamp.** The two pins
   (`M M2`, `N 57`) are **self-retiring**: the guard FAILS if a pinned row no
   longer needs its exemption. It convicts itself the moment somebody fixes a
   row on it.
3. **It would claim more than it ran.** Every run prints what it did NOT check,
   by state and count -- including the 18 `UNCLEAR` rows, which are neither
   convicted nor cleared.
4. **The logic could be right while the walk finds nothing.** Red 2 exists
   solely for this.

### 5.3 Green

    write-off rows            : 310
      of which CONTINGENT     : 65
      contingent, no reopener : 2

    ENFORCED SCOPE -- states ['EXCLUDED-RULED', 'XR']
      ok    all 57 contingent write-offs in scope carry a reopener

---

## 6. THE GATE CONVICTED THIS WAVE, AND IT WAS RIGHT ABOUT A REAL DEFECT

The impact gate REFUSED the census commit on **three red tests across two
guards** -- two from `test_pointer_graph_guard.py`, one from
`test_a_correction_is_findable_from_the_claim.py`. All three are recorded,
because a wave that reports only the green is reporting half a run.

**`test_the_committed_census_still_matches_its_pin` -- AND IT CAUGHT A REAL
MISCLASSIFICATION I HAD JUST WRITTEN.** Adding a reopener to `P D14` moved its
verdict `US-RULING+WORLD-FACT` -> `ACCOUNT-FACT+US-RULING+WORLD-FACT`, and
because `D15`-`D17` resolve to `D14` by backreference, three pinned pointers
now rested on a different argument than when they were pinned.

The cause was four words. I had written *"three addresses have ever left these
families, each on his own ruling"*, and `his own` matches the shipped
`AF:his-thing` signal. **`P D14` is an `/edit/` family row; nothing about it is
a fact about the account.** The guard offers `--pin` as the remedy, and taking
it would have baked a false `ACCOUNT-FACT` into the corpus and into three
inherited rows. **Re-pinning would have made the guard agree with a mistake.**
Reworded to *"each on an operator ruling"*; `D14` returned to
`US-RULING+WORLD-FACT` and the pins hold untouched.

**THE LESSON IS ABOUT WRITING IN A CLASSIFIED CORPUS, and it generalises past
this wave.** These cells are INPUT to a running classifier. Prose added to one
is not commentary -- it is data, and an idiom can move a published verdict and
every row inheriting it. Every kind change this pass caused was therefore
diffed rather than assumed:

    M M4   US-RULING+WORLD-FACT -> ACCOUNT-FACT+US-RULING+WORLD-FACT   KEPT
    N 10   US-BOUNDARY+US-RULING+WORLD-FACT -> +ACCOUNT-FACT           KEPT
    P D14  spurious ACCOUNT-FACT                                       REWORDED

The two kept ones are the rule's considered verdict, not an accident. `N 10`
fires on *"the operator moving `delete_or_withdraw_anything`"*, which the
shipped table classes `ACCOUNT-FACT` under `operator-must-act` -- and the
`CONTACT-IMPORT` reopener uses that exact phrasing. `M M4` fires on the word
`credit`, and `M M4` **is** an account-fact row in substance: the change makes
it agree with `J 127`, its twin, which was already `ACCOUNT-FACT`. Neither
broke a pin.

**`test_every_candidate_pair_is_declared_or_triaged` -- four candidates, and
the fourth is the heuristic's own cost.** Three are rows this pass wrote. The
fourth is `M M5`, **which no wave touched today**: it sits one line below
`M M4`, and `M M4` now opens `STATE CORRECTED`, so the vocabulary tripping the
scan belongs to a different row. **In a markdown table every row is one line,
so a `+-2` window means the two adjacent capabilities.** That is a real
property of this heuristic on this corpus and it is recorded in the triage
entry rather than argued away -- it is the price of not missing a correction,
and it is cheap.

The genuine correction is now declared both ways: `CORRECTS:` in this document
naming each census file, `CORRECTED BY:` in each census file naming this one,
so a reader landing on `M M4` can find what moved it.

---

## 7. FIVE ROWS WHOSE REASON HAD ALREADY GONE FALSE

Handed to this wave as a measurement by the integrator, re-measured here by
importing the modules rather than by grep. **It is the same defect one step
further along: not a write-off missing a trigger, but a write-off whose stated
reason has ALREADY been falsified and nobody noticed.**

    readonly.SANCTIONED_MUTATIONS    7 entries
      entry 7  ('linkedin_server/writes.py', 'perform', 'set_input_files')
    writes.PERFORMABLE               12 actions -- the upload verb is NOT one
    writes.writes_enabled()          False
    readonly._ALLOWED_URL_PATTERNS   41

All four figures reproduce exactly. `profile.md` said, in three places, that the
ban on `set_input_files` was **package-wide** and the verb **unsanctioned**.
Both have been false since 2026-09-04.

**THE ROWS DO NOT MOVE AND THAT IS WHY IT IS WORTH THE TIME.** Upload is absent
from `PERFORMABLE`, so no caller can name it, and writes are off. Nothing became
reachable. **Right answer, wrong reason is indistinguishable to a later reader
from wrong answer, wrong reason** -- which is the same indistinguishability this
whole document is about, one level down.

Repaired, with reopeners that are checkable by import rather than by reading
prose -- *the upload verb entering `writes.PERFORMABLE`, or
`writes.writes_enabled()` returning True*:

| site | what was false |
|---|---|
| `B2` | *"a test-enforced **package-wide** ban"* |
| `M1` | *"`set_input_files` is **unsanctioned** on top of that"* |
| finding 7.11 | *"asserts the kind **absent** from `SANCTIONED_MUTATIONS`"* -- the test asserts the exact inverse, and says so in its own docstring |
| finding 7.11 | the citation `tests/test_readonly.py:306-341` now lands inside `test_the_partition_conserves_every_hit`, a different test |
| section 6 roll-up | the four-row attribution, annotated (below) |

**A STALE LINE RANGE DOES NOT DANGLE -- IT HANDS BACK A PLAUSIBLE WRONG ANSWER**
and stops the reader looking. Re-cited by SYMBOL,
`test_exactly_one_place_in_this_package_can_reach_a_file_input`, which cannot
drift.

**WHAT I DID NOT RULE, because it is not a wave's to rule.** The ban's stated
ground is *"the operator has never been asked about it"*. **No operator answer
is recorded anywhere in the corpus.** The 2026-09-04 sanction is a dated fact
about the code and is NOT an answer to that question; every repaired cell says
so explicitly, and the honest phrasing used throughout is that **the verb is
permitted at exactly one switched-off call site while the capability stays
closed.**

**AND A MEMBERSHIP CLAIM THAT DOES NOT SURVIVE ITS OWN POINTER GRAPH.** The
roll-up attributes four rows to this ban -- `B2, B3, B5, G3`. Resolved, only
`B3` inherits `B2`: **`B5` backreferences `B4` and `G3` backreferences `G1`**,
so two of the four rest on a different cell than the roll-up says. Annotated in
place and deliberately NOT re-pointed -- moving a backreference changes what a
row MEANS, and it is a different decision from fixing a false sentence.

---

## 8. WHAT I DID NOT RESOLVE

**`M M2` and `N 57`** -- contingent, no reopener, `COVERED-CANNOT-DELIVER`.
Outside the row-set this wave was scoped to, so they are PINNED in the guard
with a reason rather than fixed, and the pin self-retires. Drafted triggers, so
whoever owns that state class pays nothing to land them:

- `M M2` (*Send an InMail to a non-connection*): its contingent fact is the
  monthly allowance, the same one `R9` now carries a reopener for. **REOPENER:
  a monthly InMail allowance materially above five, read off a Premium
  surface.** WHO: a capture.
- `N 57` (*View the newsletters you subscribe to*): **REOPENER: the account
  subscribing to any newsletter**, which is what the measured emptiness rests
  on. WHO: the operator, or a re-read of the subscriptions surface.

**The `UNCLEAR` bucket is not closed, only bounded.** 18 write-off rows carry a
kind the rule cannot read; 14 are in this row-set and all 14 were adjudicated
here, but the rule itself was not widened. Widening it is a change to a
published classifier with 12 pinned adjudications hanging off it, and it needs
its own control.

**The terse-cell class is named and not fixed.** `P I4`-`I10` are excluded by
the `set_open_to_work` spec and their cells say *"editor never loaded"*. The
attribution is real and lives in section 6 of that slice -- but a reader
landing on `P I7` from the blocker map sees a capability, a state, and a
sentence that sounds like an admission of not having looked. That is the
SECTION HEADING dialect problem one level down, and it is a census-hygiene
wave, not this one.
