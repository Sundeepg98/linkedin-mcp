# Three of the seven cheapest rows are not what the ledger says they cost

**Wave `cheap-reads`, 2026-09-05.** Seven blocker rows were handed to this wave
as "the cheapest coverage left on the board, all reads, each needing at most one
allowlist pattern and no ruling". Three of them were re-measured against the
tree rather than read off the ledger, and **all three came back different**.

The ledger is dated 2026-09-03. This tree has moved every hour since.

---

## 1. THE MEASUREMENT

One import, seven addresses, `linkedin_server.readonly.is_read_url` under
`venv/Scripts/python.exe`. The shipped predicate, not a reimplementation of it
-- the standing rule after a lead wrote its own exact-value check twice and got
it wrong twice.

    ALLOWLIST AT THE TIME OF READING: 29 patterns

| address | `is_read_url` | the row filed against it | ledger said |
|---|---|---|---|
| `/premium/my-premium/` | **True** | 56 `PREMIUM-READER-NOT-BUILT` | none |
| `/jobs/search/?f_C=<numeric id>` | **True** | 55 `COMPANY-ID-RESOLVER` | none |
| `/analytics/search-appearances/` | **True** | 53 `SEARCH-APPEARANCES-SURFACE` | **allowlist +1** |
| `/messaging/` | True | -- | -- |
| `/messaging/?searchTerm=<q>` | **False** | 34 `MISSING-PARAM-MESSAGING` | **none** |
| `/school/<slug>/` | False | 40 `SCHOOL-PAGE-SURFACE` | allowlist +1 |
| `/jobs/collections/recommended/` | False | 75 `JOB-COLLECTIONS-SURFACE` | allowlist +1 |

**Two rows are cheaper than filed and one is dearer.** The errors run in both
directions, which is the reason to re-measure rather than to spot-check the
ones that look suspicious.

---

## 2. ROW 53 IS ALREADY PAID FOR, AND NOT BY THIS WAVE

`/analytics/search-appearances/` reads ALLOWED at 29 patterns. The ledger costs
it `allowlist +1`. That pattern is on the boundary because the `search-appearances`
wave put it there today -- it owns `dom.SEARCH_APPEARANCES_*`,
`server.linkedin_search_appearances` and `tests/test_search_appearances.py` per
the roster, and `mcp__linkedin__linkedin_search_appearances` is in the tool
list.

This wave adds nothing to that row and claims nothing for it. It is recorded
here only because **a reader of the ledger cannot see it** -- the same defect
route-audit named for four rows that `6b5dad5` had already unblocked. A ledger
row and a boundary are two documents and only one of them moves.

---

## 3. ROW 34 IS FILED "BOUNDARY: NONE" AND THE BOUNDARY REFUSES IT

    /messaging/                        ALLOWED
    /messaging/?searchTerm=recruiter   REFUSED

Pattern 1 is anchored and admits no query string at all. So `M M34`, search
messages by keyword, costs an allowlist edit -- or it costs a fill into the
inbox's own search box, which is a mutation-shaped argument on a read surface
and is a different discussion again. **It does not cost 1 with boundary
"none".**

**THIS IS A SECOND, INDEPENDENT READING.** `_audit/2026-09-05-routes-already-admitted.md`
section 6 reached the same verdict earlier today by the same route. Two waves
agreeing here is weak evidence by this repository's own law -- corroboration
between instruments that share a defect is not corroboration, and both readings
called the same predicate. What makes it safe to rely on is that the predicate
is the SHIPPED gate: if it is wrong, the server is wrong, and the row is the
least of the problem.

Recorded rather than fixed. Widening pattern 1 to admit a query string is a
boundary change on the messaging root, and this wave was given no ruling and
did not seek one at 18:50 on a freeze day.

---

## 4. ROW 55 IS THE ONE WORTH LOOKING AT, BECAUSE ITS TWO HALVES BOTH EXIST

`J 10`, filter a job search by company, is filed against `COMPANY-ID-RESOLVER`
-- the reasoning being that `f_C` needs a numeric Page id and a posting only
yields a slug. That reasoning was correct when it was written. It is now stale
in both halves:

* **the address is admitted.** `/jobs/search/?f_C=<id>` reads ALLOWED, and has
  since the first commit -- `f_C` is just another query key on a root this
  server has always been able to open.
* **the resolver exists.** `shape.company_id_from_insight_cards` is in the tree
  with `tests/test_company_id_resolver.py` beside it, and `linkedin_job_detail`
  already returns a `company_id` verdict -- state `resolved` only when exactly
  one card agrees, and `absent` on four of five captures, which is a verdict and
  not a bare value. That is the `company-page` wave's artifact, built today.

**So the blocker named on this row is discharged and the row is still GAP.**
What remains between the two is one query parameter in `linkedin_search_jobs`:
the six-filter machinery `job-search-params` shipped already has the
`params.append` shape, and `f_C` is the same shape as `f_E` and `f_JT`.

**The gap is not a missing capability. It is that nobody joined two finished
halves** -- the same shape as `A boundary opened with nothing behind it`, one
level up: here BOTH sides are built and the wire between them is absent.

---

## 5. WHAT THIS WAVE DID NOT DO, STATED PLAINLY

* **No live page was opened.** Not one. The browser was available and this wave
  used none of it, so nothing here is a claim about what any LinkedIn page
  currently draws.
* **Rows 40 and 75 were not touched** beyond confirming both addresses are
  refused today, which is what the ledger already said. Their cost of
  `allowlist +1` is the one figure in the seven that this pass corroborates
  rather than corrects.
* **Row 56 was not built.** `/premium/my-premium/` is admitted and no reader
  exists -- confirmed here by measurement, having been named by the ledger's
  own amendment A10. Building one needs a capture, and an invented DOM fails
  closed as "he has no premium features", which is the exact answer the surface
  exists to produce. The newsletter wave declined a reader on that reasoning
  and this wave declines on the same reasoning.
* **Row 53 was not worked on and is not this wave's** -- see section 2.
* **The row-by-row census edit is still not applied**, here as everywhere. The
  census files read GAP for every row named above and a re-count taken today
  returns the old figure and would be right to.

  > **CORRECTED BY: this document, section 7, about forty minutes later.** That
  > sentence was true when it was committed at `6456701` and false by `990bbd3`,
  > which is four commits later on the same afternoon. The marker is here, beside
  > the claim, rather than at the foot of the file: a reader who opens this
  > document to learn whether the census is current stops at this line satisfied,
  > and a pointer they never scroll to cannot reach them.

## 6. PROVENANCE

Boundary readings taken by importing the shipped module at the working tree, not
at a SHA -- a suite or a predicate reading is dated by the TREE. Allowlist count
29 at the moment of reading; it was 27 when route-audit measured earlier today
and 28 after the newsletter re-freeze, so **that number expires in hours and the
verdicts above should be re-taken rather than quoted.**

No identifier of any kind appears in this document; every address above is
written with a placeholder where a value would go.

**One disclosure note, because the honest version is shorter than the argument
for it.** The probe needed a numeric id to exercise `f_C`, and the value it used
was lifted from a company id already printed in another tracked audit document
in this repository. This wave did not establish that value as synthetic and does
not claim it is. It is not reproduced here, the probe itself lives under the
gitignored `_audit/_scratch/` and enters no commit, and the numeric shape is all
the reading depended on -- any seven digits would have returned the same verdict.
Recorded rather than left implicit: **a value inherited from a tracked file is
still a value somebody vouched for, and it was not me.**

---

## 7. J 10 IS BUILT, AND THIS DOCUMENT WENT STALE WHILE IT WAS BEING BUILT

`67da282` wires the company filter: `linkedin_search_jobs` now takes a
`company_id`, and `linkedin_server/jobfilter.py` turns it into the `f_C` pair or
refuses it. No new address, no allowlist pattern, no capture, no page load, no
ruling -- section 4 predicted the row needed only the wire, and that is all it
needed.

**The refusal describes a shape and never quotes its input**, which is why the
verdict is a module rather than four inline lines. This package's standing rule
is that a refusal names what it SAW. Followed literally, the refusal for `f_C`
publishes a company SLUG -- a third-party organisation's name, and the likeliest
wrong value by a wide margin, since a slug is exactly what a posting hands you.
**Two standing rules collide on this one function and the identity rule wins.**
Length and character classes are reported instead; a digits-only value is echoed,
because once known to be all digits it cannot be a name.

Shown failing twice before admission: quoting the input turned 2 tests red (the
leak test caught the slug verbatim inside its own failure message), and
neutralising the digit guard turned 7 red. Restored, 11 pass. Gate: 246 passed
across four suites.

### The stale sentence, and it is this document's own thesis arriving on time

Section 5 says the row-by-row census edit is not applied. **It was true at
`6456701` and false by `990bbd3`**, four commits and roughly forty minutes later,
when another wave landed 37 rows from GAP to EXCLUDED-RULED. This document opened
by saying a ledger dated two days ago had gone stale under a tree that moves
every hour. It then went stale itself, in under an hour, in the same tree.

Two further readings in that commit bear directly on the table in section 1 and
are recorded here rather than folded silently into it, because they are another
wave's measurements and not this one's:

* **`P G7` moved to COVERED-PROVEN today by the `search-appearances` wave** --
  which corroborates section 2 from a second direction: that surface is not just
  admitted, it is proven.
* **the true GAP figure before that edit was 407, not 409**, and the counter saw
  406, because one row's state cell had been overwritten with prose and is
  invisible to the instrument that counts it.

### What is still owed on J 10, and by whom

**The census row is NOT edited and this wave did not edit it.** `f_C` does not
have a row of its own: it sits inside a grouped row covering *six named search
filters*, whose text still reads that the company filter *"needs a slug-to-numeric-id
resolver, which the repo already names as an open problem"*. That premise is now
false in the code and true in the census.

It is left alone deliberately. Those files were edited by another wave twenty
minutes before this was written, and a grouped row cannot be flipped for one of
its six members without a judgement about the other five. **Naming the owner by
artifact rather than by guess:** whoever holds `_audit/_census/jobs.md` and the
applier behind `990bbd3` -- not the wave that happens to have built the filter.

**And the standing-instruction hazard applies to that census line specifically.**
An audit document is a dated record and rots fairly harmlessly; a census row is
read as current truth by whoever plans from it next. The sentence naming the
resolver as an open problem is the class most able to propagate a stale premise,
and it is the one class the correction machinery cannot bind.

---

## 8. THE GATE SWEEP IS RED ON A COMMITTED FILE, AND IT IS NOT THIS WAVE'S

Recorded here because a commit is the only receipt that survives a session, and
because this one gates the push rather than any single row.

    scripts/sweep_tracked_for_identity.py
    HIT  _audit/2026-09-05-jobs-tail.md:403  [operator_own_denied_terms]
    FAIL: 1 hit across 332 tracked files

**It is COMMITTED, not working-tree.** `git diff --numstat` on that path is
empty, so the string is in history and a clean working copy proves nothing about
it. Route by artifact, not by guess: `git log -- _audit/2026-09-05-jobs-tail.md`
names `f8e706c` and `b312d98`, both from the jobs-tail measurement work. **That
wave owns the remedy.** This wave does not fix it -- a neighbour's lines are not
swept, and for this class the author is the only person who can say what the
string is.

### What is NOT being claimed, because the rule cuts the other way here

**A red guard means UNDECLARED, not real.** The lead escalated that reading
twice today and was wrong twice. So this section reports a HIT and a CLASS and
nothing more; it does not say an identifier is in history.

**And the likeliest explanation is already written down.** The same guard fired
this afternoon on a repair that explained a fix by NAMING the offending word in
its new prose -- the guard cannot tell a quotation from a claim, and one that
tried to would be a worse guard. The obfuscated hit is prose carrying markdown
emphasis, which is the same shape. If that is what it is, the remedy is the one
already found: describe the term without spelling it, and say so in the file, so
the next reader does not reintroduce it while documenting it.

### The ordering is the finding, and it is the third instance today

    sweep before staging this wave's second commit   PASS, 0 hits / 316 files
    sweep before staging this wave's third commit    FAIL, 1 hit  / 332 files

Sixteen tracked files entered between those two readings and one of them carried
this. **A sweep from earlier in a session is not evidence about the tree you
push** -- the rule was written at ~16:57 today off exactly this ordering, and it
has now paid for itself twice in one afternoon. The count of files swept moving
316 to 332 is the part worth reading: the corpus grew under both readings.

**Whoever runs the gate must run the sweep AGAIN at the gate.** Not this
reading, and not the 0-hit one above it.

### One race, recorded because it will happen to the next wave too

This wave's third commit failed outright with an `index.lock` error while a
neighbour was committing, and HEAD moved by three commits between the attempt
and the retry. Nothing was lost -- the failure was loud, `--only` re-took exactly
the two intended paths, and the diff was re-read before the retry. Worth knowing
that in a tree this busy a commit is not certain to land, and **the honest check
after any commit is `git log --oneline -1`, not the absence of an error.**

---

## 9. A POINTER FOR ROW 41, NOT A RULING ON IT

`PREMIUM-JOBS-SURFACES` (3 rows, `allowlist +1`) was not worked on. One thing
found while reading the census is worth handing to whoever takes it, because it
could collapse the row count before any address is opened -- and because it is
the shape the newsletter wave named: *a zero on the right page turns a
twelve-row blocker into a one-row blocker.*

Census rows `J 25`, `J 29` and `J 30` were retired today under
`PANEL-NOT-OBSERVED` on an unusually strong measurement, quoted from the census
rather than re-derived: the control -- *Show match details / Show Premium
Insights / How you match* -- reproduces 1/1/0 on four committed captures, reads
0/0/0 on exactly the two the fixture table marks un-hydrated, and reproduced
1/1/0 LIVE twice across a browser restart. The conclusion recorded there is that
**the panel is not drawn for this account, rather than unread.**

### Why that is a pointer and not an answer

**It does not transfer to row 41 by itself, and saying so is the point.** The
retired rows are the match-insight panel on a posting. Row 41's rows are
different features -- cover-letter assistance, marking a job Top Choice, AI
job-fit tips -- and a panel not rendering says nothing directly about a separate
product surface.

**There is also a tension worth someone resolving rather than inheriting.** This
account is understood to carry a Premium subscription, and a Premium-gated panel
reading absent is exactly the observation that should not be waved through in
either direction: it is equally consistent with *not entitled*, *entitled and
not rendered on these postings*, and *rendered somewhere this reader has not
looked*. **Three states, one reading, and the reading cannot separate them.**

So the cheap move for row 41 is the one this wave did not have the hours for:
establish the ENTITLEMENT first, on `/premium/my-premium/` -- **already on the
allowlist, no boundary change, one page load** -- before costing three feature
rows. If the entitlement is absent the rows retire for a reason that will still
be true tomorrow; if it is present, the reader that row 56 wants and the answer
row 41 needs are the same page load.

**That is the strongest argument this wave found for building the premium
reader, and it arrived too late in the session to act on.** It is recorded here
so the next wave does not have to find it again: rows 41 and 56 are cheaper
together than separately, and neither needs the boundary moved.

---

## 10. SECTION 8 IS CLOSED, WITHIN MINUTES, AND THE LOOP IS THE RESULT

> **CORRECTED BY: this section.** Section 8 reports the gate sweep RED. It was
> red when taken and is green now. Do not act on section 8's reading; re-run the
> sweep, which is what section 8 itself tells you to do.

    sweep at the time of section 8    FAIL, 1 hit  / 332 tracked files
    sweep roughly ten minutes later   PASS, 0 hits / 329 tracked files

The change is not drift and was not guessed at: `git log` on that path names
`1eae6ff`, *"a real denied term reached a tracked audit doc, redacted at the
tree"*, and the same wave had already committed `7da74fd`, *"my last commit
reported a sweep PASS that had already failed, and a push is blocked."*

**Three things are worth separating, because they are three different results.**

1. **The finding was real.** Section 8 declined to say whether the hit was a
   genuine identifier or a term quoted while being documented, on the standing
   rule that a red guard proves UNDECLARED and never REAL. That hedge was the
   right posture and the answer came back on the other side: the fix commit
   calls it *a real denied term.* **Hedging correctly is not the same as being
   wrong to hedge** -- the evidence available at the time supported no stronger
   claim, and a stronger claim would have been the error the lead made twice
   today.
2. **The owning wave found it independently and first.** `7da74fd` predates this
   wave's section 8. Two waves converged on the same push blocker from different
   directions within minutes, which is the fleet working rather than duplication
   to be trimmed -- and the one that owned the string is the one that fixed it,
   which is the routing rule paying out.
3. **This document has now gone stale three times in one session** -- section 5
   on the census edit, section 8 on the sweep, and its own provenance note
   warning that the allowlist count expires in hours. It opened by saying a
   two-day-old ledger had gone stale under a fast tree. **Every correction in it
   is that same sentence, aimed at itself, at a shorter interval each time.**

The practical instruction, which has not changed and is now demonstrated twice
rather than argued: **the sweep that matters is the one run at the gate.**
Neither of the readings in this document is that reading, and by the time anyone
reads this, neither is the reading above.

---

## 11. FREEZE. THE NUMBERS BELOW WERE RECOMPUTED, NOT RE-READ

Every figure here was derived from `git` at freeze time rather than copied from
an earlier sentence in this document, because proofreading cannot reach a number
that is wrong and the numbers most worth recomputing are the ones that flatter
the author.

    5 commits    656 insertions    0 deletions    4 distinct files

| commit | files | + | - | what |
|---|---:|---:|---:|---|
| `6456701` | 1 | 144 | 0 | the seven-address measurement |
| `67da282` | 3 | 290 | 0 | `jobfilter.py`, its tests, the `server.py` wire |
| `825543d` | 2 | 79 | 0 | the `company_id` docstring, section 7 |
| `780a5c2` | 1 | 56 | 0 | the gate sweep red |
| `88bd02c` | 1 | 87 | 0 | its close |

**ZERO DELETIONS ACROSS ALL FIVE, and that is the load-bearing number rather
than the insertions.** It says no neighbour's line was swept into any commit
here -- five separate incidents of exactly that happened in this tree today. It
is a measurement (`git show --numstat`), not a recollection of having been
careful.

**AI attribution: 0 lines in each of the five, checked per commit rather than
across the range.**

    GATE  878 passed, 0 failed, 225.54s   test_company_job_filter, test_tools,
                                          test_server_surface,
                                          test_every_tool_is_on_the_surface,
                                          test_job_search_fixture,
                                          test_job_search_result_window,
                                          test_no_committed_identity,
                                          test_navigation_is_never_derived

**That is a TARGETED run and it clears SHAPE violations only.** An enumeration
guard fires on *somebody added a caller* and is invisible to any run scoped to a
file list, so this says nothing about that class. The full clone gate is still
owed and is not this wave's to run.

### The boundary was not touched, and here is the check rather than the claim

`linkedin_server/readonly.py` appears in none of the five commits --
`git show --name-only` over all five returns four paths and that is not one of
them. The allowlist stood at **29** when this wave measured it and this wave
added nothing to it. **A wave that changes no boundary still has to prove it**,
and the proof is the file list, not the intention.

### Cost, in this document's own currency

Rows moved: **one built** (`J 10`), **three re-costed on measurement** (34
dearer, 53 already paid, 55 discharged), **three left alone with reasons** (40,
41, 75), **one declined with a reason** (56).

    page loads          0
    allowlist patterns  0
    captures            0
    rulings sought      0
    new modules         1
    new test files      1

**No live page was opened by this wave at any point.** The browser was available
the whole session and none of it was used, so nothing in this document is a
claim about what any LinkedIn page currently draws. Every verdict here is a
verdict about this repository's own code.

### What a successor should pick up first

**Rows 41 and 56 are cheaper together than separately** -- section 9. One load of
`/premium/my-premium/`, already admitted, settles the entitlement question that
sits under both. That is the single highest-value page load left on this wave's
board and it needs no boundary change and no ruling.
