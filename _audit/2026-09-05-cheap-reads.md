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
