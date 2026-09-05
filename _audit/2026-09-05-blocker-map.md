# The row-to-blocker map, rebuilt from committed sources -- and 306 of 409 were never recoverable

**THE HEADLINE IS THE UNASSIGNED COUNT: 306.**

    409   GAP rows in the frozen census (1c08e5f), enumerated by the shipped instrument
    103   assigned to a blocker by a COMMITTED source
    306   UNASSIGNED -- no committed source names them against any blocker

     26   of 97 blockers have at least one recoverable row
     71   of 97 have NOT ONE

**`_audit/2026-09-03-linkedin-gap-blockers.md` assigned all 409 GAP rows to 97
blockers and published only the counts. The classifier that produced the
division was never committed** -- `git log -S` across all history finds it
nowhere, and the ledger's own provenance section says *"Nothing was committed.
No tracked file was edited."* So until now no per-blocker number in this
repository could be checked, and when later waves measured a blocker at 35
against a published 32, or 13 against 12, or 8 against 18, **nobody could tell a
re-cost from a miscount.**

This document does not restore the classifier. It measures how much of its
output survives in a form anybody can audit, and the answer is a quarter.

**306 is the number to quote.** It bounds how much of the ledger's division was
ever real, and it is the reason a per-blocker count in this repository should be
read as an author's assertion rather than as a measurement, unless it appears in
`_audit/_census/blocker-map.tsv`.

Wave `blocker-map`, 2026-09-05. Four files committed at `d5f6409`. Read-only
against the census: **no row's STATE was re-adjudicated, and none was edited.**

---

## 1. WHAT WAS BUILT

| file | what it is |
|---|---|
| `scripts/enumerate_gap_rows.py` | emits the row IDS behind the shipped counter's counts, at the working tree or at any git ref |
| `_audit/_census/blocker-assignments.tsv` | the evidence: one line per assignment, each with its committed source, locator and evidence class |
| `scripts/build_blocker_map.py` | joins the two, asserts on itself, and diffs the recount against the ledger's published counts |
| `_audit/_census/blocker-map.tsv` | the map: 409 lines, blocker or `UNASSIGNED`, evidence class, source, state at the freeze AND state today |

**The enumerator IMPORTS `count_census_states.py`; it does not reparse.** Four
waves reimplemented a shipped instrument yesterday and three got a broken one.
The consequence is stated in the file rather than hidden: **it inherits that
parse's blind spots exactly.** A row whose state cell is prose is invisible to
all three, which is not a hypothetical -- see section 6.

One behaviour had to be replicated rather than imported, because it lives inside
the shipped counter's `main()` and has no seam: the network slice's admin-only
table carries no state column, so `N A<digits>` is forced to GAP. `--control`
re-runs the shipped counter as a subprocess and fails on any per-slice
disagreement. **That control guards the replication and nothing more. It cannot
detect a defect the two share, because they share the parse by design** -- two
parsers agreeing on a wrong total is a failure this project has already had, and
a control that could not have caught it should not be sold as if it could.

    control jobs.md                   enumerated rows/GAP (150, 84)   shipped (150, 84)   MATCH
    control profile.md                enumerated rows/GAP (203, 73)   shipped (203, 73)   MATCH
    control messaging-and-content.md  enumerated rows/GAP (142, 99)   shipped (142, 99)   MATCH
    control network.md                enumerated rows/GAP (209, 114)  shipped (209, 114)  MATCH

---

## 2. THE SPINE IS THE FROZEN ROW SET, AND THAT IS A DECISION

The map enumerates the **409 GAP rows as of `1c08e5f`** -- the census commit,
stamped 2026-09-03 15:53:26 -- and not today's 370.

**Because 409 is the only set the ledger's counts can be checked against.** A
map built on today's rows would show `AI-INTERVIEW-PRODUCT` at 3 against a
published 14 and could not say whether eleven rows were misassigned or eleven
rows had been retired. Every line therefore carries BOTH states, so today's view
is a filter on one file rather than a second artifact that can drift from it.

**The frozen set reproduces exactly, and it reproduces four numbers rather than
one:**

    ledger section 1        jobs 99   profile 79   messaging 109   network 122   = 409
    enumerated at 1c08e5f   jobs 99   profile 79   messaging 109   network 122   = 409

That matters more than the total agreeing. **A classification that reproduces an
independent prior count is corroborated; one that merely sums to the total is
not** -- two errors of opposite sign cancel in a total and cannot cancel in four
per-slice figures at once.

---

## 3. THE EVIDENCE CLASSES, AND WHAT EACH IS WORTH

| class | rows | what it means |
|---|---:|---|
| `LEDGER-EXPLICIT` | 56 | the 2026-09-03 ledger's own body names these ids for this blocker. The nearest thing to the lost classifier that exists, because it is the classifier's author writing |
| `LEDGER-AMENDMENT` | 3 | an amendment appended to that ledger names them |
| `RECON-CENSUS-COMMITTED` | 34 | RECONSTRUCTED by a later wave, and commit `990bbd3` then acted on it |
| `RECON-DOC` | 10 | reconstructed in a tracked document; nothing acted on it |
| **`UNASSIGNED`** | **306** | **no committed source names the row against any blocker** |

**BE PRECISE ABOUT WHAT `RECON-CENSUS-COMMITTED` BUYS, BECAUSE IT LOOKS LIKE
MORE THAN IT IS.** `_audit/2026-09-05-decide-retire-rulings.md` section 1 says
its own row sets are a reconstruction and calls that *"the weakest thing here"*.
Commit `990bbd3` then moved exactly those rows GAP -> EXCLUDED-RULED. That
upgrades the assignment from prose to a commit a clone can reproduce, and **it
does not corroborate correctness, because the editor of `990bbd3` was acting on
that same reconstruction. Propagation is not confirmation.** An equal count is a
correlation, not an identity.

**No line in the evidence file is this wave's own inference.** There is no
`INFERRED` class because there are no inferred assignments: a row whose blocker
could not be read off a committed source is `UNASSIGNED`, which is the whole
point. A map that silently mixed derived and guessed assignments would
manufacture auditability, which is worse than the ledger's honest silence.

**Ids are slice-qualified throughout** (`J` jobs, `P` profile, `M`
messaging-and-content, `N` network) because the slices reuse bare ids -- `P C3`
and `M C3` are different capabilities. Where a source writes an unqualified
short form the qualification was settled **by measurement, never by guess**:
`_audit/2026-09-05-decide-retire-rulings.md` writes `M 24`, `M 38` and `M 42`,
and bare `M 24` / `M 38` / `M 42` are **absent from the census entirely** while
`M M24` / `M M38` / `M M42` are present and read as the source describes them.
The same test resolved A13's `C 11` and `C 52` to `M C11` ("Add a hashtag to a
post") and `M C52`.

---

## 4. THE PER-BLOCKER DIFF -- 24 COMPLETE, 2 PARTIAL, 71 ABSENT

The ledger's published counts are **parsed out of the ledger's own tables, never
retyped**, and the mapper refuses to run if those tables stop totalling 97
blockers and 409 rows. Independently re-derived here before any comparison: the
ranked table holds 88 blockers over 359 rows, the cost-0 table 9 over 50, and
88 + 9 = 97 with 359 + 50 = 409.

| blocker | published | recovered | verdict |
|---|---:|---:|---|
| `GROUPS-SURFACE` | 32 | 1 | **PARTIAL** -- 31 rows named nowhere |
| `FILE-UPLOAD-UNSANCTIONED` | 16 | 16 | COMPLETE |
| `AI-INTERVIEW-PRODUCT` | 14 | 14 | COMPLETE |
| `FORBIDDEN-CLASS-FIX-LANDED` | 8 | 8 | COMPLETE |
| `CLOSED-SINCE-CENSUS` | 7 | 7 | COMPLETE |
| `JOB-SEARCH-PARAMS` | 6 | 6 | COMPLETE |
| `CONTACT-IMPORT` | 5 | 5 | COMPLETE |
| `MATCH-DETAILS-COLLAPSED` | 5 | 5 | COMPLETE |
| `MESSAGING-SETTINGS` | 5 | 5 | COMPLETE |
| `ANALYTICS-CONTROLS-UNPRESSED` | 4 | 3 | **PARTIAL** -- the fourth row is named nowhere |
| `GROUP-CHAT-SURFACE` | 4 | 4 | COMPLETE |
| `OWNED-BY-A-SIBLING-SLICE` | 4 | 4 | COMPLETE |
| `HASHTAG-EXISTENCE` | 3 | 3 | COMPLETE |
| `HELP-CENTER-FORM` | 3 | 3 | COMPLETE |
| `OFF-PLATFORM-WIDGET` | 3 | 3 | COMPLETE |
| `PANEL-NOT-OBSERVED` | 3 | 3 | COMPLETE |
| `AI-ASSIST-MESSAGING` | 2 | 2 | COMPLETE |
| `LIVE-BROADCAST` | 2 | 2 | COMPLETE |
| `PARSER-ON-A-LOADED-PAGE` | 2 | 2 | COMPLETE |
| `COMPANY-ID-RESOLVER` | 1 | 1 | COMPLETE |
| `DEVICE-GEOLOCATION` | 1 | 1 | COMPLETE |
| `MOBILE-APP-ONLY` | 1 | 1 | COMPLETE |
| `PAID-BOOST` | 1 | 1 | COMPLETE |
| `REPORTING-FLOWS` | 1 | 1 | COMPLETE |
| `SIGNIN-INTERSTITIAL` | 1 | 1 | COMPLETE |
| `VOICE-CAPTURE` | 1 | 1 | COMPLETE |
| **the other 71 blockers** | **306** | **0** | **ABSENT** |

**WHERE EVIDENCE EXISTS, THE LEDGER'S ARITHMETIC WAS RIGHT.** Twenty-four
blockers recount to exactly their published figure. That is twenty-four
independent prior numbers reproduced -- not one total that happens to sum -- and
it is the strongest thing that can be said for the ledger on the evidence
available. **It says nothing whatever about the 306.**

**The two disagreements are both in the safe direction and neither is a
miscount.** The map recovers 1 of `GROUPS-SURFACE`'s 32 and 3 of
`ANALYTICS-CONTROLS-UNPRESSED`'s 4; the missing rows are named **nowhere**
rather than named differently. The mapper asserts on the dangerous direction and
would fail the run: **no blocker may recount HIGHER than its published count**,
because that would mean a committed source and the ledger disagree about which
rows are in a set, and that is a finding, not a merge.

**`GROUPS-SURFACE` is the worst case and the most consequential.** It is the
largest blocker in the census, and one row -- `N 165` -- is all that any
committed source names. `_audit/2026-09-05-groups-surface-measured.md`
independently derives **35** and records that *no subset reconciles to 32*. With
31 of 32 rows unrecoverable, **that disagreement cannot be adjudicated at all.**
There is no set to compare against; there are two counts and one row id.

---

## 5. WHY EVERY LINE CARRIES TWO STATES

**A per-blocker count that moved has two entirely different causes and they are
indistinguishable without the row ids.** Measured against the frozen set:

    409   GAP at 1c08e5f
    -40   rows that have LEFT GAP since (37 of them in one commit, 990bbd3)
     +1   row that has ENTERED GAP since  (P L2b, "Own follower LIST")
    ----
    370   which is exactly what the shipped counter reports today

The 40 that left, by destination:

| destination | rows |
|---|---:|
| `EXCLUDED-RULED` | 37 |
| `MEASURED-ABSENT` | 2 (`N 118`, `P L2`) |
| `COVERED-PROVEN` | 1 (`P G7`) |

**So the current total is now DERIVABLE from the frozen one, row by row, rather
than merely consistent with it.** That is the difference this artifact makes:
before it, 409 and 370 were two numbers from two passes; now they are one row
set with 41 named movements.

### What the diff settled that a document could not

`_audit/2026-09-05-decide-retire-rulings.md` flagged two substitution risks it
said it could not resolve. The tree has since resolved both -- **in the weak
sense, which is the only sense available:**

| risk | how the tree now stands |
|---|---|
| does `MESSAGING-SETTINGS` hold `M M42` or `M M24`? | `990bbd3` flipped `M M42`. `M M24` did NOT move and remains GAP |
| does `AI-ASSIST-MESSAGING` hold `J 150`? | it flipped `M M40` and `M M51`. `J 150` did NOT move |

**This does not prove what the original classifier meant.** It records that the
tree has committed to one reading, which makes it checkable and reversible
instead of merely uncertain. A wave refused to bank a twelve twice today for
exactly this reason, and the same caution applies here.

---

## 6. FINDINGS

### 6.1 THE FOUR CENSUS SLICES' OWN SUMMARY TABLES STILL PUBLISH 409

This is the most important finding in the document and it was not what I went
looking for.

The ledger's section 1 established its row set by a **two-way check**: derive
the expected total from each slice's own count table, then parse every table row
structurally, and require them to agree. They did, at 409, on both axes. That
agreement is why 409 was credible.

**Run that same method today and the two halves disagree by 39.**

| slice | its own summary table says | the table it summarises holds |
|---|---:|---:|
| `jobs.md` | GAP 99 | 84 |
| `profile.md` | GAP 79 | 73 |
| `messaging-and-content.md` | GAP 40 + 69 = 109 | 99 |
| `network.md` | GAP 107 + 15 admin = 122 | 114 |
| | **409** | **370** |

**Every one of the four is stale, and the staleness is exactly the movement:**
39 = 40 rows out less 1 row in. `990bbd3` edited the capability rows and left
every summary table untouched.

**THE CONSEQUENCE IS THE SHAPE OF THIS WHOLE PROJECT'S FAILURES.** The
cross-check that made 409 trustworthy is now a mirror: it reports the frozen
number back at anyone who runs it, and a reader following the ledger's own
documented method would get 409 from the summaries, 370 from the parse, and no
way to tell which half had rotted. **A corroboration that has stopped being
independent looks exactly like one that still is.**

Reported, not fixed. Editing four summary tables is the census's owners' call,
and the standing rule here is that a wave does not re-adjudicate a neighbour's
rows. But **nobody should quote a census summary table again without checking it
against `count_census_states.py` first.**

### 6.2 FOURTEEN ROWS WERE INVISIBLE TO THE COUNTER AT THE FREEZE

Measured across four refs, the row SET is not stable and the instrument's
coverage is part of the reason:

    rows PRESENT at 1c08e5f, ABSENT at 990bbd3^   N 132
    rows ABSENT at 990bbd3, PRESENT today          M M1  M M2  P G1  P L2b
                                                   N 119 120 121 122 123 124
                                                   125 126 127 128  N 132

`N 132` **round-tripped** -- countable at the freeze, invisible by `990bbd3^`
(its state cell had been replaced with a sentence, which the shipped counter's
own docstring records), countable again after `02e617d` restored it. **A
two-point diff cannot see a round trip**, and mine would have missed it had the
endpoints not happened to differ from the middle.

Of the 13 rows that were invisible at the freeze and are visible now, **12 are
EXCLUDED-RULED or COVERED today and one is GAP: `P L2b`.** So exactly one row
sits in today's numerator that no ledger has ever seen or classified. That is
small, and it is the measured floor rather than a reassurance: the ledger's own
section 7 says **761 is a floor**, and this is the mechanism by which it grows.

### 6.3 THE RANKED TABLE IS WHERE THE COUNTS LIVE AND IT CARRIES NO IDS AT ALL

Of the assignments recovered, **56 are `LEDGER-EXPLICIT` and they cluster hard**:
the ledger names rows freely for the blockers it argued about in prose (section
5's handful, section 6's thirteen-free-reads table, section 2's boundary
movements, Amendment A13) and names none at all for the 71 it merely ranked.
**The ranked table is where the counts live and it carries no ids anywhere.**

That is the structural cause of the 306, and it is worth stating as a rule
rather than as a complaint: **a table of counts with no key is not a
classification, it is a summary of one.** The classifier existed -- the ledger
describes it asserting on itself, raising on double-assignment, closing at
409/409/0/0 -- and it was thrown away at the moment it had produced the only
output anybody kept.

### 6.4 TWO REDS FOUND AND ROUTED, NEITHER OF THEM MINE

The six guards that scan `scripts/` and `_audit/` were run before committing --
`--tb=line`, per the standing rule that a mixed red queue must be sorted by what
each assertion is ABOUT before anything is touched. **317 passed, 2 failed, and
both failures are somebody else's. Neither is cleared here.**

| red | evidence | owner, by artifact |
|---|---|---|
| `test_every_person_constant_holds_a_declared_invented_name` | `tests/test_recommendation_tally.py:71` holds `NEEDLE = 'ZZQXNEEDLE7'`, not on `INVENTED_NAMES` | that file's only commit, `fc10b99` -- the name-free recommendations reader |
| `test_the_tab_leak_only_ever_shrinks` | 41 leaking scripts against a pinned 39 | `_probe_contact_info_panel.py` (`f08e62b`) and `_probe_premium_entitlement.py` (`ae469cc`) -- the only two leakers added since the pin `002a9dd` |

**Both are the UNDECLARED class, not the REAL class.** `ZZQXNEEDLE7` is
transparently invented and the remedy is one line in `INVENTED_NAMES` by its
author -- *"that edit is the check"*, in the test's own words. The tab ratchet
is doing exactly its job: it fired the moment two probes were added without a
`finally`, which is what a ratchet is for.

**Neither script committed by this wave appears in either failure's evidence.**
`enumerate_gap_rows.py` and `build_blocker_map.py` open no browser session and
declare no person-carrying constant. Verified by reading the failure lists, not
by assuming.

### 6.5 A COMMIT MESSAGE FILE IN THE SHARED SCRATCHPAD IS A RACE, AND IT NEARLY RAN

The standing rule here is that a commit message goes through a FILE PATH and
never through stdin or a shell string, because prose full of backticks and
dollar signs loses characters through a shell. That rule is right and it has a
gap nobody had written down.

**Measured during this wave: the message file at
`<scratchpad>/msg1.txt` was OVERWRITTEN by another wave's commit message
between this wave's two commits.** The scratchpad path carries this session's
own id and is not the shared tree, which is precisely why it read as private.

Nothing was lost -- verified rather than assumed: `git log -1 --format=%B` on
`d5f6409` contains zero lines of the neighbour's text, so the overwrite landed
after the commit consumed the file. **Had the order been reversed, this wave
would have committed a neighbour's commit message onto its own four files, and
`--only` would not have helped: the hazard is in the MESSAGE, not the paths.**

    RULE: name a message file for the WAVE, not for the step.
          <scratchpad>/msg-<wave>-<n>.txt, never msg1.txt.
          A generic name in a shared directory is a collision waiting for
          two waves to pick the same obvious word, and they will.

Same disease as everything else in this repository: a private-looking thing that
several writers share, and no instrument that can tell you it moved.

---

## 7. STATED LIMITS

1. **This map inherits the shipped parse's blind spots exactly**, by
   construction and by instruction. A row whose state cell is prose is invisible
   to it. `--unstated` on the shipped counter is the only way to see those, and
   6.2 is what it showed.
2. **`RECON-CENSUS-COMMITTED` is not corroboration of correctness.** It is one
   author's reconstruction that a second person acted on. Both may be wrong
   together, and 3 of those 34 rows are graded `DERIVED-WEAK` or flagged as
   substitution risks in the source itself.
3. **The 306 is a floor on what is unrecoverable, not a ceiling on what is
   wrong.** A row being `LEDGER-EXPLICIT` means the ledger's author named it,
   not that the assignment is right. The assignment rule -- *one blocker per
   row, the earliest binding constraint* -- is a judgment, and this document
   re-applied it to nothing.
4. **No row's STATE was re-adjudicated and none was edited.** Where a state
   looks wrong (6.1's four summary tables) it is reported.
5. **Nothing here re-costs any blocker.** `GROUPS-SURFACE` at 32 versus 35 and
   `NEWSLETTER-SURFACE` at 12 versus 13 are left exactly as their waves left
   them; what this document adds is that 31 of the 32 and all of the 12 are
   unrecoverable, so those disagreements cannot currently be settled by anyone.

---

## 8. PROVENANCE

* Rows enumerated by `scripts/enumerate_gap_rows.py`, which imports
  `scripts/count_census_states.py`; per-slice control passes at four of four.
* Frozen row set read out of git object `1c08e5f` -- the census commit, not a
  copy of it.
* The ledger's published counts parsed from `_audit/2026-09-03-linkedin-gap-blockers.md`'s
  own tables at run time; the mapper refuses to run if they stop totalling
  97 blockers / 409 rows.
* State movements measured across four refs: `1c08e5f`, `990bbd3^`, `990bbd3`,
  and the working tree.
* Ambiguous short-form ids resolved by testing both spellings against the census
  and keeping the one that exists.
* Identity sweep `scripts/sweep_tracked_for_identity.py` run **at the gate,
  after staging**: PASS, 0 hits across 374 swept files, 377 tracked.
* Commit `d5f6409`, four new files, 916 insertions, verified line-for-line
  against `git show HEAD --numstat` (143 + 410 + 205 + 158) and the map re-read
  out of `git show HEAD:_audit/_census/blocker-map.tsv` rather than off disk.
* Zero AI attribution.
