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
