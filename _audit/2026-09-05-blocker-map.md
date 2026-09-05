# The row-to-blocker map, rebuilt from committed sources -- and 284 of 409 are named nowhere

**THE HEADLINE IS THE UNASSIGNED COUNT: 284.**

    409   GAP rows in the frozen census (1c08e5f), enumerated by the shipped instrument
    125   assigned to a blocker by a COMMITTED source
    284   UNASSIGNED -- no committed source names them against any blocker

     39   of 97 blockers have at least one recoverable row
     58   of 97 have NOT ONE

**The first pass of this document published 306 and 26/71.** A second harvest
found two further committed blocker-to-row tables (section 9) and moved 19 rows;
a recall check on that scan (section 12) moved 3 more. That direction is the
point of the artifact and the guard is built to allow it: `UNASSIGNED` is a
CEILING that may only fall. **284 is the number to quote.**

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

**284 bounds how much of the ledger's division was ever real,** and it is the reason a per-blocker count in this repository should be
read as an author's assertion rather than as a measurement, unless it appears in
`_audit/_census/blocker-map.tsv`.

Wave `blocker-map`, 2026-09-05. Commits `d5f6409`, `78729da`, `b343795` and the
commit carrying this revision. Read-only against the census: **no row's STATE was
re-adjudicated, and none was edited.**

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
| `RECON-DOC` | 32 | reconstructed in a tracked document; nothing acted on it |
| **`UNASSIGNED`** | **284** | **no committed source names the row against any blocker** |

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

## 4. THE PER-BLOCKER DIFF -- 32 COMPLETE, 7 PARTIAL, 58 ABSENT

The ledger's published counts are **parsed out of the ledger's own tables, never
retyped**, and the mapper refuses to run if those tables stop totalling 97
blockers and 409 rows. Independently re-derived here before any comparison: the
ranked table holds 88 blockers over 359 rows, the cost-0 table 9 over 50, and
88 + 9 = 97 with 359 + 50 = 409.

| blocker | published | recovered | verdict |
|---|---:|---:|---|
| `GROUPS-SURFACE` | 32 | 4 | **PARTIAL** -- 28 named nowhere |
| `COMPANY-PAGE-SURFACE` | 18 | 1 | **PARTIAL** -- 17 named nowhere |
| `EVENTS-SURFACE` | 18 | 1 | **PARTIAL** -- 17 named nowhere |
| `FILE-UPLOAD-UNSANCTIONED` | 16 | 16 | COMPLETE |
| `AI-INTERVIEW-PRODUCT` | 14 | 14 | COMPLETE |
| `FORBIDDEN-CLASS-FIX-LANDED` | 8 | 8 | COMPLETE |
| `CLOSED-SINCE-CENSUS` | 7 | 7 | COMPLETE |
| `JOB-SEARCH-PARAMS` | 6 | 6 | COMPLETE |
| `SERVED-BY-GMAIL-SKILL` | 6 | 2 | **PARTIAL** -- 4 named nowhere |
| `CONTACT-IMPORT` | 5 | 5 | COMPLETE |
| `MATCH-DETAILS-COLLAPSED` | 5 | 5 | COMPLETE |
| `MESSAGING-SETTINGS` | 5 | 5 | COMPLETE |
| `OPEN-TO-HIRING-MODAL` | 5 | 1 | **PARTIAL** -- 4 named nowhere |
| `ANALYTICS-CONTROLS-UNPRESSED` | 4 | 3 | **PARTIAL** -- 1 named nowhere |
| `GROUP-CHAT-SURFACE` | 4 | 4 | COMPLETE |
| `OWNED-BY-A-SIBLING-SLICE` | 4 | 4 | COMPLETE |
| `PEOPLE-FOLLOW-LISTS` | 4 | 3 | **PARTIAL** -- 1 named nowhere |
| `ENDORSE-SUBSTRING-OVERREACH` | 3 | 3 | COMPLETE |
| `HASHTAG-EXISTENCE` | 3 | 3 | COMPLETE |
| `HELP-CENTER-FORM` | 3 | 3 | COMPLETE |
| `OFF-PLATFORM-WIDGET` | 3 | 3 | COMPLETE |
| `PANEL-NOT-OBSERVED` | 3 | 3 | COMPLETE |
| `AI-ASSIST-MESSAGING` | 2 | 2 | COMPLETE |
| `LIVE-BROADCAST` | 2 | 2 | COMPLETE |
| `PARSER-ON-A-LOADED-PAGE` | 2 | 2 | COMPLETE |
| `SEARCH-HISTORY-SURFACE` | 2 | 2 | COMPLETE |
| `ACTIVITY-VIEW-SETTING` | 1 | 1 | COMPLETE |
| `COMPANY-ID-RESOLVER` | 1 | 1 | COMPLETE |
| `DEVICE-GEOLOCATION` | 1 | 1 | COMPLETE |
| `EMBED-SETTING` | 1 | 1 | COMPLETE |
| `LEARNING-CERTIFICATE` | 1 | 1 | COMPLETE |
| `MISSING-PARAM-MESSAGING` | 1 | 1 | COMPLETE |
| `MOBILE-APP-ONLY` | 1 | 1 | COMPLETE |
| `PAID-BOOST` | 1 | 1 | COMPLETE |
| `REPORTING-FLOWS` | 1 | 1 | COMPLETE |
| `SIGNIN-INTERSTITIAL` | 1 | 1 | COMPLETE |
| `SKILL-PAGE-SURFACE` | 1 | 1 | COMPLETE |
| `VIDEO-MEETING-INTEGRATION` | 1 | 1 | COMPLETE |
| `VOICE-CAPTURE` | 1 | 1 | COMPLETE |
| **the other 58 blockers** | **284** | **0** | **ABSENT** |

**WHERE EVIDENCE EXISTS, THE LEDGER'S ARITHMETIC WAS RIGHT.** Thirty-two
blockers recount to exactly their published figure. That is thirty-two
independent prior numbers reproduced -- not one total that happens to sum -- and
it is the strongest thing that can be said for the ledger on the evidence
available. **It says nothing whatever about the 284.**

**All six disagreements are in the safe direction and none is a miscount.** The
map recovers 4 of `GROUPS-SURFACE`'s 32, 1 of `COMPANY-PAGE-SURFACE`'s 18, 1 of
`EVENTS-SURFACE`'s 18, 2 of `SERVED-BY-GMAIL-SKILL`'s 6, 1 of
`OPEN-TO-HIRING-MODAL`'s 5 and 3 of `ANALYTICS-CONTROLS-UNPRESSED`'s 4; the
missing rows are named **nowhere** rather than named differently. The mapper asserts on the dangerous direction and
would fail the run: **no blocker may recount HIGHER than its published count**,
because that would mean a committed source and the ledger disagree about which
rows are in a set, and that is a finding, not a merge.

**`GROUPS-SURFACE` is the worst case and the most consequential.** It is the
largest blocker in the census and four of its 32 rows are all that any committed
source names. `_audit/2026-09-05-groups-surface-measured.md` independently
derives **35** and records that *no subset reconciles to 32*. With 28 of 32 rows
unrecoverable, **that disagreement still cannot be adjudicated** -- see section
9.3, which measures where the 32 cannot be coming from.

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

Of the assignments recovered, **56 are `LEDGER-EXPLICIT` and they cluster hard**
(that figure did not move in the second harvest -- everything the second pass
found came from LATER waves, not from the ledger):
the ledger names rows freely for the blockers it argued about in prose (section
5's handful, section 6's thirteen-free-reads table, section 2's boundary
movements, Amendment A13) and names none at all for the 71 it merely ranked.
**The ranked table is where the counts live and it carries no ids anywhere.**

That is the structural cause of the 284, and it is worth stating as a rule
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
3. **The 284 is a floor on what is unrecoverable, not a ceiling on what is
   wrong.** A row being `LEDGER-EXPLICIT` means the ledger's author named it,
   not that the assignment is right. The assignment rule -- *one blocker per
   row, the earliest binding constraint* -- is a judgment, and this document
   re-applied it to nothing.
4. **No row's STATE was re-adjudicated and none was edited.** Where a state
   looks wrong (6.1's four summary tables) it is reported.
5. **Nothing here re-costs any blocker.** `GROUPS-SURFACE` at 32 versus 35 and
   `NEWSLETTER-SURFACE` at 12 versus 13 are left exactly as their waves left
   them; what this document adds is that 28 of the 32 and all of the 12 are
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

---

## 9. THE SECOND HARVEST -- 306 TO 287, AND THREE THINGS IT TURNED UP

*(a third pass took it to 284; see section 12.)*

A mechanical scan of the whole tracked corpus was run for every one of the 97
blocker names alongside census row ids. **Its output is a haystack and was
treated as one:** 900 passages, and for `FILE-UPLOAD-UNSANCTIONED` -- a 16-row
blocker -- it captured 111 distinct ids, because a context window catches
neighbouring ids as readily as the blocker's own. **Folding that into the map
would have been the exact failure this artifact exists to fix**, so none of it
was folded in as scanned.

What it was used for is a filter: passages whose id count EQUALS the blocker's
published row count, over blockers the map had not already recovered. Seventeen
candidates, each then read in its source and adjudicated by hand.

### 9.1 Two real blocker-to-row tables, and five false positives

| source | what it is | rows taken |
|---|---|---:|
| `_audit/2026-09-05-settings-tail.md` section 2.3 | an explicit blocker / row-id / R-W table over the settings family | 7 |
| `_audit/2026-09-05-routes-already-admitted.md` | a route table naming the blocker per row beside a dated gate reading | 12 |

Both state their own method, which is why they are admitted as `RECON-DOC` and
not higher: settings-tail says its row lookup was delegated and verified against
the ranked table's counts and R/W splits -- the same method, and the same
weakness, as the retirement wave's reconstruction.

**Five of the seventeen were rejected, and the rejections are the more useful
half.** Four were parser artifacts (`P 1`, `N 1` -- ids scraped out of a table of
ledger RANK numbers) and one was worse:

> `INVITE-NOTE-PARAM` matched at 1 id, `P H9`, on a sentence reading *"It is the
> same act as `INVITE-NOTE-PARAM` at twenty times the scale"*.

**That is an ANALOGY, and an exact-count filter cannot tell an analogy from an
assignment.** Taken, it would have filed a service-review row under an
invitation-note blocker on the strength of a simile. The filter is a way of
finding candidates; it is not a way of accepting them.

Two of the twelve route-table rows -- `J 10` and `P N12` -- were ALREADY in the
map from the ledger itself, and both agree. Small, but it is the only place in
this exercise where two independent sources name the same row for the same
blocker.

### 9.2 A ROW CLAIMED BY TWO BLOCKERS, AND BOTH SOURCES ARE COMMITTED

    M C52   "Manage your LinkedIn feed preferences (follow / unfollow topics/hashtags)"

    ledger Amendment A13          keeps it as HASHTAG-EXISTENCE's one remaining row
    2026-09-05-settings-tail.md   assigns it to FEED-PREFERENCES

**Under the ledger's own rule -- one blocker per row, the earliest binding
constraint -- exactly one of these is right, and the row's own text supports
both readings.** Following/unfollowing hashtags is a hashtag capability and a
feed-preferences capability in the same sentence.

The map keeps it under `HASHTAG-EXISTENCE` because `LEDGER-AMENDMENT` outranks
`RECON-DOC`, **and the row's `note` field records the dispute rather than
hiding it.** `FEED-PREFERENCES` therefore recovers zero rows, and if the
settings reading is right then `HASHTAG-EXISTENCE` is a two-row blocker, not
three.

**This was found by the double-assignment assertion, not by reading.** The guard
earned its place within an hour of being written, which is the only argument for
a guard that counts.

### 9.3 WHERE `GROUPS-SURFACE`'s 32 CANNOT BE COMING FROM

The largest blocker in the census, published at 32 rows, re-derived at 35 by
`_audit/2026-09-05-groups-surface-measured.md`, which records that *no subset of
the 35 reconciles to 32*. Four rows are now recovered. A measurement that
narrows the space:

    network.md section P, "LinkedIn Groups as a people surface"
      at 1c08e5f:  18 rows, N 161-178, EVERY ONE GAP
    network.md section Q, "LinkedIn Events as a people surface"
      at 1c08e5f:  15 rows, N 179-193, EVERY ONE GAP

**So `GROUPS-SURFACE`'s 32 draws at least 14 rows from OUTSIDE the network
slice's groups section, and `EVENTS-SURFACE`'s 18 draws at least 3 from outside
its own.** The re-derivation says where from -- `N 63 64`, `M C60-C70`, `M C91`,
`N A10 A11 A12` -- but it walked a GITIGNORED route table to get there, so that
half does not survive a clone.

This does not settle 32 against 35. It says the disagreement is not a
counting slip inside one section: **two documents are drawing a family boundary
across four slices in two different places, and the boundary is what neither
publishes.**

### 9.4 THE STRONGEST UNASSIGNED CANDIDATE IN THE MAP, DELIBERATELY LEFT UNASSIGNED

`ANALYTICS-CONTROLS-UNPRESSED` is published at 4 rows and the ledger names three
(`N 133 134 136`). The profile-viewer analytics family at the freeze is exactly
five GAP rows -- `N 132 133 134 135 136` -- and `N 135` is filed by name under
`CLOSED-SINCE-CENSUS` in the same document. **Four remain, and the fourth is
`N 132`, "Switch between Search appearances and Who viewed your profile" -- a
control on a page this server already opens, which is precisely what the blocker
name describes.**

**It is still `UNASSIGNED` in the map, and that is the discipline rather than an
oversight.** The elimination is mine, no committed source states it, and a
headline number that means *"recoverable from a committed source"* stops meaning
anything the moment one good inference is allowed in. It is recorded here so
whoever owns that row can promote it in one line.

### 9.5 WHAT THE SECOND HARVEST DID NOT CHANGE

`LEDGER-EXPLICIT` stayed at 56. **Every row the second pass recovered came from
a LATER wave, never from the ledger** -- which is section 6.3's finding arriving
from a second direction: the ranked table where the counts live has no ids in
it, and no amount of scanning can find what was never written down.

---

## 10. THE GUARD FIRED WITHIN THE HOUR, ON A DEFECT IN MY OWN INSTRUMENT

Written at `b343795`. Fired at 23:48, before this wave closed.

    FAILED test_the_ledger_tables_still_total_97_blockers_and_409_rows
    FAILED test_no_blocker_recounts_higher_than_the_ledger_published
       these blockers hold MORE rows in the map than the ledger published:
       CLOSED-SINCE-CENSUS, FORBIDDEN-CLASS-FIX-LANDED,
       OWNED-BY-A-SIBLING-SLICE, SERVED-BY-GMAIL-SKILL

**Nothing was wrong with the data. `ledger_counts()` read the ledger's two
tables out of a HARDCODED LINE WINDOW, `text[140:311]`.** Another wave appended
19 lines (`0d66ebe`), the file went 1546 -> 1565, both tables slid 28 lines down,
and the cost-0 table left the window entirely. Its nine blockers then parsed as
absent, `published.get(b, 0)` turned absent into **zero**, and four blockers the
map holds legitimately read as over-counted.

**A READING PINNED TO A POSITION IN A FILE OTHER WAVES ARE APPENDING TO.** That
is this repository's own disease in a new place, and I wrote it into the
instrument built to cure it. Both tables are now located by their HEADER ROW.

### The second defect was in the MESSAGE, and it is the worse one

The assertion said *"a committed source and the ledger disagree about which rows
are in a set"*. That was false. It had SEEN four blockers missing from its
lookup and REPORTED them as published at zero -- **a refusal naming a cause it
had not observed**, which is this project's `refusals-must-name-what-they-saw`
scar with my name on it. Anyone reading that message would have gone hunting a
data disagreement that did not exist.

Split into two assertions that cannot be confused, and the new one is **shown
failing** by breaking the header anchor deliberately:

    the map holds blockers the ledger parse does not know at all: [...].
    Before treating this as a disagreement, check that BOTH ledger tables
    still parse -- a renamed or reformatted header returns a partial parse
    rather than an error.

### And the reassuring measurement, taken because the alarm demanded it

Re-parsed at `b343795` and at HEAD with the fixed reader:

    b343795   97 blockers   409 rows
    HEAD      97 blockers   409 rows
    per-blocker count changes:  NONE

`0d66ebe`'s *"four cells corrected"* touched cells other than the row counts, so
**every comparison in sections 4 and 9 stands unchanged.** That is worth stating
explicitly, because the honest reading of a fired guard is not "it was a false
alarm" -- it is "the alarm was right about something, and here is what."

**The receipt this leaves is the only argument for a guard that counts:** it
caught a real drift within an hour, in the safest possible direction, on the
author who wrote it.

---

## 11. THE TAB LEAK RE-MEASURED AT FREEZE -- 39 PINNED, 41, THEN 42

Section 6.4 read the tab ratchet at **41** against a pinned 39, at 23:34. Read
again at 23:55, immediately before this wave closed, it is **42**.

    23:34   41 leaking scripts   +2 since the pin: _probe_contact_info_panel.py (f08e62b)
                                                   _probe_premium_entitlement.py (ae469cc)
    23:55   42 leaking scripts   +1 more:          _probe_job_alerts_live.py     (NO COMMIT)

**THE THIRD LEAKER IS IN THE INDEX AND IN NO COMMIT ANYWHERE**, and I nearly
published a wrong owner for it. I attributed it to `6b90622` because that commit
carries the job-alerts boundary work and the name matched. Then I ran the check
this repository already requires -- `git log --oneline -1 -- <path>` -- and it
returned NOTHING. `git log --all` returns nothing either, while
`git ls-files --error-unmatch` succeeds. The file is staged and unwritten to
history.

**A name that sounds right is not a measurement**, and that rule caught me one
command before the commit. The owner of that probe cannot be named by `git log`
at all and is not named here.

**AND THE STATE ITSELF IS THE FINDING.** A tracked-file guard reads the INDEX, so
a staged-but-uncommitted file is already inside every such guard's corpus while
being invisible to every history query. That is the ~16:57 scar -- files entering
the index between two readings -- seen from the other side: not a sweep going
stale, but a file with no author a reader can reach.

**A number in a durable record is a MEASUREMENT and it expires.** 6.4's 41 was
true when taken and is stated with its time; this is the same reading retaken at
the gate, which is the discipline this repository already applies to the identity
sweep and which applies identically to a ratchet in a tree with a dozen writers.

**The third leaker is not mine either.** 445 passed across the five suites that
enumerate `scripts/`, one failed, and neither `enumerate_gap_rows.py` nor
`build_blocker_map.py` appears in the leak list at either reading -- they open no
browser session at all.

**Nothing here is a criticism of three good probes.** The ratchet is doing
exactly what a ratchet does: naming the moment a class grew, cheaply, so it is a
line in a diff and not an incident. Each remedy is one `finally` closing the
PAGE, and each belongs to the wave that opened it.

---

## 12. A RECALL CHECK ON MY OWN FILTER -- 287 TO 284, AND 23 OF 24 CONFIRMED JUNK

Section 9's filter accepted a passage only when its id count EQUALLED the
blocker's published count. **That is a precision filter, and precision filters
have recall costs nobody measures.** So before banking the number, I asked the
opposite question of the same scan: of the blockers still ABSENT from the map,
how many carry ANY id evidence at all, and does any of it look like a real row
list the equality test skipped?

    absent blockers carrying at least one captured id   24 of 58

Every one of the 24 was read in its source. **Twenty-three are junk, and the
junk falls into three named shapes:**

| shape | example | what it really is |
|---|---|---|
| rank-table scrape | `EASY-APPLY-MULTISTEP` -> `P 0`, `MESSAGE-REACTION` -> `N 1` | ids manufactured out of a table of ledger RANK numbers and zero-costs |
| sentence bleed | `THREAD-REPLY-BOX` and `MESSAGE-ADDRESSING` both -> `P L2` | one sentence names three blockers and one row; the row belongs to a fourth |
| a POINTER cited as a set | `PREMIUM-JOBS-SURFACES` -> `J 25 J 29 J 30` | those are `PANEL-NOT-OBSERVED`'s rows, cited under a heading that says in terms *"A POINTER FOR ROW 41, NOT A RULING ON IT"* |

One more deserves its own line because it is the funniest failure mode
available: `CONTENT-ANALYTICS-SURFACE` matched `N 05 N 09 N 2026` -- **fragments
of a date in a source comment**, wearing the exact shape of a network row id.

### The one real miss, and why the filter missed it

    PEOPLE-FOLLOW-LISTS   published 4   recovered 3   N 38, N 39, N 40

`_audit/2026-09-05-routes-already-admitted.md` prints them in a refusal block and
names the blocker in the next sentence -- *"Neither is a new finding:
`PEOPLE-FOLLOW-LISTS` already costs a denylist edit alongside its two allowlist
patterns, so the ledger has this right."* **An explicit, committed assignment,
skipped purely because 3 is not 4.**

**THE LESSON IS ABOUT THE FILTER, NOT THE ROW.** An equality test between a
passage's id count and a published count is a proxy for *"is this a complete row
list"*, and it silently discards every PARTIAL list -- which, given that the
whole finding of this document is that lists are partial, was the wrong proxy to
lean on unexamined. One recall check cost ten minutes and found one row set in
twenty-four.

**And it does not change the shape of the answer.** 284 rather than 287, 39
blockers rather than 38, 58 absent rather than 59. The headline moved by 1% and
the 23-of-24 junk rate is the more useful number: **it says the scan is a
haystack and the map is right not to have absorbed it.**
