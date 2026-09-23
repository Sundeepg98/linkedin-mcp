# Census slice: JOBS, END TO END

What LinkedIn's own Help Center documents a member can do with jobs, against what
`linkedin_server/` can actually do. Read-only work: no browser, no session, no page load,
no `mcp__linkedin__*` call, no tracked file edited, nothing committed.

Date 2026-09-03. Repo at ``, branch
`master`. Server surface measured at **35 registered tools** (`grep -c "^@mcp.tool()"`),
`writes.PERFORMABLE` at **12 actions**, `writes.SANCTIONED_WRITES` at 13 (the thirteenth,
`set_open_to_work`, has no tool).

---

## THE COUNTS

**REVISED 2026-09-03 after a second pass with a better instrument. The denominator grew by
18 and not one of the new rows is covered.** The first pass walked LinkedIn's Help TOPIC
tree; the second queried LinkedIn's own ARTICLE INDEX at
`linkedin.com/help/linkedin/search?q=` (see section 7). Before/after is in section 7.

The table below carries **151 numbered rows**. One of them (row 58, bulk-unsave) is a thing
LinkedIn itself does not offer, so it takes no state. **The denominator is 150 distinct job
capabilities**, imported from LinkedIn's own Help Center (not brainstormed). Every count
here was taken by grep against the finished table, not estimated:

| state | count | share of 150 | was (133-row pass) |
|---|---|---|---|
| COVERED-PROVEN | 21 | 14.0% | 21 |
| COVERED-UNFIRED | 7 | 4.7% | 7 |
| EXCLUDED-RULED | 23 | 15.3% | 23 |
| GAP | 99 | 66.0% | 81 |

**DELTA, 2026-09-19. The block above is UNCHANGED and still reads as it did when
this census was written**, so every document citing those numbers still resolves
against them. What moved is recorded here instead, because a count that silently
rewrites itself cannot be cited:

    COVERED-PROVEN    21  ->  19    rows 103 and 104 moved to COVERED-UNFIRED
    COVERED-UNFIRED    7  ->   9    same two rows

**Why, since it moves the number the wrong way for this slice.** Both rows were
banked on the word `PERFORMS` quoted out of a REFUSES/PERFORMS ledger, which is
a verdict about the gate and not a receipt for a fire; the cited document's own
receipts read `writes performed 0` and *"Nothing was fired."* This slice's own
section *"THE SECOND CORRECTION: what 'live-fire' means for the three writes"*
draws exactly that distinction and gave `unsave_job` **NO. NEVER FIRED.** on it.
The NETWORK census slice has held both actions at COVERED-UNFIRED all along in
its rows 46 and 48, so this removes a contradiction between two slices rather
than creating one.
**Nothing moved out of GAP and the GAP count is untouched.**

**CORRECTED BY:** `_audit/2026-09-19-unfired-but-built.md` -- rows 103 and 104 moved COVERED-PROVEN to COVERED-UNFIRED, on the four readings in its section 4.

**SECOND DELTA, 2026-09-19, and it moves the number the other way.** The block
above is still UNCHANGED; this records the movement:

    COVERED-PROVEN    19  ->  20    row 44, unsave a job, FIRED
    COVERED-UNFIRED    9  ->   8    same row

Net across both deltas on this slice today: **CP 21 -> 20, CU 7 -> 8.** Two rows
left COVERED-PROVEN on evidence that turned out to be a gate verdict, and one
entered it on a watched fire. **Both directions were measured the same way, and
the pass that moved the count down and the pass that moved it up applied the
identical standard:** a state is COVERED-PROVEN when the capability was
exercised and read back, on a surface other than the one acted on.

**NOT MOVED, and this is the larger half of the pass.** Rows **43** (save a job),
**45** (read the saved list) and **46** (read whether one posting is saved) were
ALREADY COVERED-PROVEN and do not move -- today's fires re-exercised all three,
and re-proving a proven row adds a reading, not a state. Rows **103** and **104**
(follow / unfollow a company) stay COVERED-UNFIRED: `follow_company` was
attempted today and **REFUSED, twice, identically**, because prior state came
back `unknown` from both available sources and the gate will not guess which way
it would move. **A refusal is not a fire**, and the refusal was measured on a
second independent target, so it is the gate's standing behaviour and not one
posting's quirk. Nothing about that changes their state. **Row 58 (bulk-unsave)
stays `n/a`** -- LinkedIn itself has no such control, and a fire on the
single-job path says nothing about a capability that does not exist.
**Nothing moved out of GAP and the GAP count is untouched.**

**THIRD DELTA, 2026-09-21, and it is the first on this slice that moves a row OUT
of GAP.** The block above is still UNCHANGED; this records the movement:

    GAP               99  ->  98    row 40, read per-job network proximity, BUILT
    COVERED-UNFIRED    8  ->   9    same row

Running totals on this slice after all three deltas: **CP 20, CU 9, XR 23, GAP 98.**

**CU AND NOT CP, and the distinction is the one the two deltas above were fought
over.** The reader was exercised and read back -- over four committed captures, in
a real headless browser, in both of LinkedIn's layouts -- but never against
LinkedIn. By this slice's own standard a fixture is not a fire, so it enters at
COVERED-UNFIRED and moves to COVERED-PROVEN on one live search. Booking it CP on
fixture evidence would repeat exactly the error that cost rows 103 and 104 their
state: banking a verdict taken off a document rather than a receipt for a run.

**WHY A GAP ROW MOVED AT ALL, since the re-walks kept finding "only a bigger
hole."** This row was never a capability nobody could reach; it was a field the
server LOADED ON EVERY SEARCH AND THREW AWAY. `_audit/2026-09-20-the-contingent-writeoffs.md`
measured its reason cell ("Not on any surface this server reads") against the
committed captures, found the field present, and re-priced the row at boundary
cost 0. The build cost one parser inside an existing one, and nothing was added
to the tool surface, the address allowlist or the write set. **The GAP count
falls because a parser was written, not because the denominator moved.**

**EVIDENCE:** `_audit/2026-09-21-the-proximity-field.md`.
**Row 57 did NOT move** -- its blocker ("BLOCKED behind row 40") is lifted and its
route is now measured, but nothing was built for it. See its cell.

**FOURTH DELTA, 2026-09-23 (lane L3), and it moves two rows out of GAP.**
The block above is still UNCHANGED; this records the movement, measured by
`census_completion.walk()` before and after:

    GAP               56  ->  54    rows 18 and 39, each BUILT
    COVERED-UNFIRED    5  ->   7    same two rows

`J 18` -- `linkedin_recent_job_searches`, off the jobs home the row was never
priced on. `J 39` -- `linkedin_premium_job_collection(2)`, the recommended
collection's posting ids. **Both were built OFFLINE and neither has been
fired**, so each enters at COVERED-UNFIRED and moves to COVERED-PROVEN on one
live call -- the bar the third delta set for row 40, applied unchanged.
**A THIRD, `J 57`, WAS BUILT AND WITHDRAWN BEFORE MERGE**: the join its own
cell names navigates to ids read off a page, which this repository forbids;
see its cell. **AND THE 54 THAT REMAIN NOW CARRY A DIRECTION**, outside this
file as section 8 of `_audit/2026-09-21-the-jobs-direction.md` argued it
should be: `_audit/_census/jobs-directions.tsv`, R 26, W 25, R+W 3, checked on
every run by `scripts/check_jobs_directions.py`.
**EVIDENCE:** `_audit/2026-09-23-lane-l3-jobs.md`.

**122 of 150 job capabilities cannot be reached through this server** -- 99 because nobody
considered them, 23 because somebody wrote down a reason. That is 81.3%, up from 78.8%. Of
the **28** a tool can reach, **21** have live-fire evidence and 7 have never run against
LinkedIn. **The covered set did not move at all: the re-walk found no hidden coverage, only
a bigger hole.**

**7 of those 81 GAPs are served by the `linkedin-jobs` SKILL** rather than by this server.
They are counted as server GAPs because the server does not hold them, flagged `SKILL` in
the table, and listed again in section 4 -- for the operator's real question ("can I do
it?"), those 7 (plus two card-level fields that are not separate rows) are available to
him today with no LinkedIn session at all.

Taxonomy source: 3 Help Center walks returning 353 sourced rows (122 search/alerts/saved,
92 applying, 139 preferences/company/Premium), deduped and consolidated to the 133 below.
Pages fetched successfully, per walk: **48 + 32 + 34**. Cross-walk overlap was not
measured, so the deduped total is between 48 and 114 and I am not quoting one. **9 distinct
help pages 404'd** (1 + 2 + 6); the load-bearing ones are named in section 3.

---

## THE CORRECTION TO THE BRIEF, and it cuts the other way

I was told the repo says *LinkedIn offers no withdraw at all, and that this is a fact
about LinkedIn rather than a missing tool*. **The repo says almost the opposite, and the
Help Center settles it against the repo.**

What the repo actually says, verbatim, `linkedin_server/server.py:3876`:

> **NOBODY HAS ESTABLISHED THAT LINKEDIN OFFERS A WITHDRAW AT ALL.** That is a stronger
> and worse statement than "this server cannot withdraw it", which would invite you to
> assume LinkedIn can. It might. It has not been measured

That is an **UNMEASURED** claim, not a fact about LinkedIn. And `server.py:5081` goes
further in the other direction, filing withdraw under `not_yet_measured` as:

> "WITHDRAWING an application. **A real LinkedIn feature**, and the one that would most
> change how safe applying is"

So the repo holds two positions at once: "nobody knows whether LinkedIn has one" and "it
is a real LinkedIn feature". `writes.py:680` names the blocking loop -- the measurement
needs an application to exist, and getting one means performing the irreversible act:

> "The measurement is: load /jobs-tracker/?stage=applied on an account that HAS an
> application and look for a withdraw control on a row. ... The loop resolves in one
> direction only: the first application made here is the one that settles the question,
> and if the answer is no, it will have been settled by an application nobody can take
> back."

**That loop is unnecessary. The Help Center answers it for free.** I fetched
`https://www.linkedin.com/help/linkedin/answer/a512388` ("Apply for jobs on LinkedIn")
myself, not through a subagent:

> "You cannot edit or withdraw an application once submitted through LinkedIn. To make
> changes, contact the job poster via InMail."

Corroborated by `a512329` (the Applied-tab page), which documents viewing applied jobs and
names no withdraw, remove or delete action anywhere on it.

**Verdict: withdraw is NOT-A-LINKEDIN-CAPABILITY for LinkedIn-hosted applications, and is
excluded from the 133-item denominator rather than counted as a GAP.** The repo's
`not_yet_measured` entry calling it "A real LinkedIn feature" is wrong and should be
retired; the `reversibility_procedure` prose should stop offering the "It might" reading.
The operational consequence stands and gets stronger, not weaker: `apply_job` is
irreversible because **LinkedIn** offers no undo, not merely because this server declines
to build one.

---

## THE SECOND CORRECTION: what "live-fire" means for the three writes

I was told `save_job`, `unsave_job` and `apply_job` all have live-fire evidence. Measured
against the audits, they are in **three different states**:

| action | live fire? | receipt |
|---|---|---|
| `save_job` | **YES, and it landed.** | `_audit/2026-08-30-linkedin-undo.md:433` -- "`writes.perform` gate-5 sweep, on the redeemed save \| `newly_observed_save_label: "Unsave the job"`". The ON label existed only because a real save produced it; `:1645` -- "on his first save, then three times by a read-only route that costs no write." |
| `unsave_job` | **SUPERSEDED 2026-09-19: FIRED AND VERIFIED** (saved-tab count 2 -> 1 on a different surface from the one clicked; `_audit/2026-09-19-tier1-fires.md`). This cell read **NO. NEVER FIRED.** from 2026-08-30 until that fire, and the six citations below are why -- they are kept because they were accurate when written. | `_audit/2026-08-30-linkedin-undo.md:1775` -- "`unsave_job` was **never fired**, including after it became capable." Same file records the same at `:639`, `:921`, `:1156`, `:1369`, `:1585`. |
| `apply_job` | **FIRED ONCE, AND IT DID NOT SUBMIT.** | `_audit/2026-08-31-linkedin-perform.md:790` -- "The operator authorised his first apply; the lead performed it. **IT DID NOT SUBMIT.** The gate held, on an irreversible action, on a real posting with a real employer at the other end." That firing found two defects. |

**Zero applications have ever been submitted through this server.** The same audit at
`:1039` still lists "withdrawing an application \| blocked on an EVENT rather than a
measurement -- **the Applied tab reads zero**". So `apply_job` is a tool that has executed
live and reported honestly; it is not a tool that has ever applied to anything. I have
classified it COVERED-PROVEN because the tool fired end to end, and flagged the effect
qualifier on its row and here. If the census wants a fifth state, this is the row that
needs it.

---

## 1. THE TABLE

`state` values: **CP** = COVERED-PROVEN, **CU** = COVERED-UNFIRED, **XR** = EXCLUDED-RULED,
**GAP** = no tool and no reason. `SKILL` marks a GAP the `linkedin-jobs` skill serves.
Sources are `linkedin.com/help/linkedin/answer/<id>`.

### A. Job search and the result surface (30)

**CORRECTED BY:** `_audit/2026-09-20-the-five-under-banked.md` -- rows 9, 11, 12, 13 and 14 below quote a drift floor of ZERO as though it described the surface. It is one session's reading: a second run of the same probe the same hour measured the stability control at 4 and the negative control at 2. Four of the five survive that stricter floor and are corroborated twice; row 11's "4 ids moved on a floor of 0" is refuted by it and the row now rests on its pass-three leg instead. No state moved.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 1 | Keyword / free-text job search (incl. LinkedIn's natural-language matching) | a511260, a6889044 | CP | `linkedin_search_jobs`; used as the standing live control in four audits -- 10 timed runs at `2026-08-30-jobs-view-reliability.md:123`, 7-row results at `2026-08-30-save-label.md:594` |
| 2 | Boolean operators in the query (AND / OR / NOT / "phrase" / parens) | a524335 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live through the shipped tool by `scripts/_probe_unfired_job_search_filters.py`, which measures DISCRIMINATION rather than response: every permitted value is fired against one fixed query and the returned JOB ID SETS are compared. That is the whole point -- **every value returned exactly 7 rows**, the measured per-page window, so a row COUNT discriminates nothing and a filter LinkedIn silently drops looks identical to one that works. DRIFT FLOOR measured in the SAME session by firing the baseline twice back to back: 2 of 7 ids. **5 distinct id sets across plain / OR / NOT / quoted phrase / parens+AND, widest disagreement 12** -- far above the drift floor, so the operators reach LinkedIn and change which postings come back. `keywords` is urlencoded verbatim by `server._search_url` with only `.strip()` applied, verified by reading the builder rather than by grep. |
| 3 | Filter: Location | a507441 | CP | `location=` param |
| 4 | Filter: Date posted (24h / week / month / any) | a507441 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live through the shipped tool by `scripts/_probe_unfired_job_search_filters.py`, which measures DISCRIMINATION rather than response: every permitted value is fired against one fixed query and the returned JOB ID SETS are compared. That is the whole point -- **every value returned exactly 7 rows**, the measured per-page window, so a row COUNT discriminates nothing and a filter LinkedIn silently drops looks identical to one that works. DRIFT FLOOR measured in the SAME session by firing the baseline twice back to back: 2 of 7 ids. **3 distinct id sets across the 4 `_DATE_POSTED` values, widest disagreement 12.** Param `f_TPR`. |
| 5 | Filter: Workplace type (remote / hybrid / on-site) | a508610, a512279 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live through the shipped tool by `scripts/_probe_unfired_job_search_filters.py`, which measures DISCRIMINATION rather than response: every permitted value is fired against one fixed query and the returned JOB ID SETS are compared. That is the whole point -- **every value returned exactly 7 rows**, the measured per-page window, so a row COUNT discriminates nothing and a filter LinkedIn silently drops looks identical to one that works. DRIFT FLOOR measured in the SAME session by firing the baseline twice back to back: 2 of 7 ids. **4 distinct id sets across the 4 `_WORKPLACE` values, widest disagreement 14.** Param `f_WT`. |
| 6 | Filter: Experience level (internship..executive, 6 values) | a507441 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live through the shipped tool by `scripts/_probe_unfired_job_search_filters.py`, which measures DISCRIMINATION rather than response: every permitted value is fired against one fixed query and the returned JOB ID SETS are compared. That is the whole point -- **every value returned exactly 7 rows**, the measured per-page window, so a row COUNT discriminates nothing and a filter LinkedIn silently drops looks identical to one that works. DRIFT FLOOR measured in the SAME session by firing the baseline twice back to back: 2 of 7 ids. **6 distinct id sets across the 6 `_EXPERIENCE` values, widest disagreement 14** -- one distinct set per value. Param `f_E`. |
| 7 | Sort by Most relevant / Most recent | a6889044 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live through the shipped tool by `scripts/_probe_unfired_job_search_filters.py`, which measures DISCRIMINATION rather than response: every permitted value is fired against one fixed query and the returned JOB ID SETS are compared. That is the whole point -- **every value returned exactly 7 rows**, the measured per-page window, so a row COUNT discriminates nothing and a filter LinkedIn silently drops looks identical to one that works. DRIFT FLOOR measured in the SAME session by firing the baseline twice back to back: 2 of 7 ids. **2 FULLY DISJOINT id sets, disagreement 14 of 14, against a drift floor of 0 measured on that same re-fire.** Param `sortBy=DD`. **THE PERMITTED VALUES ARE `relevance` AND `date`, NOT `recent`:** the first run passed LinkedIn's UI label `recent` straight through, the tool REFUSED it correctly, and the run reported THIN -- which read as LinkedIn serving nothing and was nearly written up as a server defect. The argument was wrong and the server was right; `_ids` now announces an argument refusal instead of returning it as an empty set. |
| 8 | Result paging by offset | a507441 | CP | `start=`; ~25/page, no auto-paging by design |
| 9 | Filter: Easy Apply only | a507441 | COVERED-PROVEN | `easy_apply` -> `f_AL`. **SHIPPED 2026-09-04 AND VERIFIED LIVE 2026-09-05; the row was never moved.** Re-verified independently 2026-09-19 by reading the tree, not the ledger: the parameter is exposed on `linkedin_search_jobs` and mapped in `server.py:3055 `_BOOLEAN_FILTERS``, and `tests/test_job_search_result_window.py` passes (6 tests). **Fired live against RESULT SETS, not merely against a pill** (`scripts/_probe_job_search_result_sets.py`, 13 loads, one session) with three controls deciding whether anything counted: POSITIVE another profession same city moved 7 of 7 shared 0; NEGATIVE a parameter LinkedIn never had moved 0; STABILITY the baseline retaken LAST moved 0, so the drift floor is ZERO. **14 ids moved on a floor of 0 -- the maximum available, seven in and seven out: it replaced the window entirely.** Owners by `git log`: `15c6693`, `af67cb8`, adopted `400e761`. Evidence `_audit/_scratch/_progress-job-search-params.md` s1, s5. **CORRECTED 2026-09-20 (five-under-banked wave) -- THE DRIFT FLOOR IS A SESSION READING, NOT A PROPERTY OF THE SURFACE.** A SECOND run of the same probe in the same hour -- 17 loads, all three passes, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` -- measured the stability control at **4** ids and the negative control at 2, where the 13-load run quoted above measured 0 and 0. Both are real readings of a surface that ranks; neither is the floor. Note also that the 13-load run's own raw output no longer exists: the probe writes to one fixed path, which was overwritten at 16:45 and again at 16:49, forty minutes before the progress document this cell cites was written at 17:29, so that run survives only in that document's prose. THIS ROW SURVIVES THE STRICTER FLOOR: the second run's own verdict line reads `EASY APPLY f_AL=true MOVED 14, above the 4-id drift floor`, so the conclusion is corroborated twice and only the phrase "the drift floor is ZERO" was overstated. Reading: `_audit/2026-09-20-the-five-under-banked.md`. |
| 10 | Filter: Company | a507441 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** The company filter was fired live by `scripts/_probe_unfired_job_search_filters.py`. The company id was not typed in: it was RESOLVED off a real posting by the shipped `linkedin_job_detail` (`company_id.state == 'resolved'`) and fed to `linkedin_search_jobs(company_id=...)`. Against the same query the unfiltered read returned 7 postings and the company-filtered read returned 7, **overlapping in only 1** -- a symmetric difference of 12 against a same-session drift floor of 2. So `f_C` reaches LinkedIn and narrows to the employer. The L1 live verification this row said had never been taken is now taken. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** `company_id` -> `f_C` via `linkedin_search_jobs(company_id=...)`. **BANKED 2026-09-19; THE BLOCKER WAS CLOSED BY A PRIOR WAVE AND THE ROW WAS NEVER MOVED.** `linkedin_server/jobfilter.py`'s own docstring says so in its first paragraph -- *both halves of that blocker are now built and the row is still GAP, because nothing joined them*. **Verified in the source rather than taken from the docstring:** `shape.company_id_from_insight_cards` (`shape.py:3195`) resolves the id, `server.py:3701` returns it as a VERDICT (state `resolved` only when exactly one card agrees), `linkedin_search_jobs(company_id=...)` (`server.py:3071`) consumes it via `jobfilter.company_filter_param`, and `COMPANY_FILTER_KEY` is `f_C`. **NO BOUNDARY COST: `/jobs/search/?f_C=<digits>` is ALREADY ADMITTED** -- measured True this wave against controls that behaved; it is one more query key on a root admitted since the first commit, so the ledger's cost-2 is really cost-0. **UNFIRED, NOT PROVEN, and I looked for the flattering answer:** no audit records the company filter returning a payload live, and `_audit/2026-09-05-company-about-card.md` states the L1 live verification was NOT taken and *remains the one reading everything in the previous wave's build rests on*. Siblings J 9 and J 11-14 were VERIFIED LIVE; this one was not. See `_audit/2026-09-19-read-tail.md` |
| 11 | Filter: Employment type / job type | a507441, a512746 | COVERED-PROVEN | `job_type` -> `f_JT`, seven values. **SHIPPED 2026-09-04 AND VERIFIED LIVE 2026-09-05; the row was never moved.** Re-verified independently 2026-09-19 by reading the tree, not the ledger: the parameter is exposed on `linkedin_search_jobs` and mapped in `server.py:2987 `_JOB_TYPE``, and `tests/test_job_search_result_window.py` passes (6 tests). **Fired live against RESULT SETS, not merely against a pill** (`scripts/_probe_job_search_result_sets.py`, 13 loads, one session) with three controls deciding whether anything counted: POSITIVE another profession same city moved 7 of 7 shared 0; NEGATIVE a parameter LinkedIn never had moved 0; STABILITY the baseline retaken LAST moved 0, so the drift floor is ZERO. **4 ids moved on a floor of 0.** Corroborated a second way, which is stronger than the pill: `f_JT=F` alone and `f_JT=C` alone share ZERO postings across three runs, while `f_JT=ZZ` draws nothing at all -- so the parameter is honoured rather than ignored. Owners by `git log`: `15c6693`, `af67cb8`, adopted `400e761`. Evidence `_audit/_scratch/_progress-job-search-params.md` s1, s5. **CORRECTED 2026-09-20 (five-under-banked wave) -- THE DRIFT FLOOR IS A SESSION READING, NOT A PROPERTY OF THE SURFACE.** A SECOND run of the same probe in the same hour -- 17 loads, all three passes, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` -- measured the stability control at **4** ids and the negative control at 2, where the 13-load run quoted above measured 0 and 0. Both are real readings of a surface that ranks; neither is the floor. Note also that the 13-load run's own raw output no longer exists: the probe writes to one fixed path, which was overwritten at 16:45 and again at 16:49, forty minutes before the progress document this cell cites was written at 17:29, so that run survives only in that document's prose. **AND ONE LEG OF THIS CELL IS REFUTED BY THAT RUN.** Against the 4-id floor the second run reported `JOB TYPE full-time f_JT=F moved 2 -- WITHIN DRIFT (4), not evidence`, so "4 ids moved on a floor of 0" is a reading from the friendlier of two sessions and does NOT carry this row. The row stands on its OTHER leg, reproduced in BOTH later runs: `f_JT=F` alone and `f_JT=C` alone share ZERO postings, and `f_JT=ZZ` draws nothing. The probe itself says the baseline comparison is the wrong measurement here -- the dropdown's default is ANY, so `f_JT=F` asks a corpus that is already mostly full-time to narrow to what it already is, and pass three is `f_JT`'s real measurement. STATE UNCHANGED, EVIDENCE CORRECTED. Reading: `_audit/2026-09-20-the-five-under-banked.md`. |
| 12 | Filter: Under 10 applicants | a507441 | COVERED-PROVEN | `under_ten_applicants` -> `f_EA`. **SHIPPED 2026-09-04 AND VERIFIED LIVE 2026-09-05; the row was never moved.** Re-verified independently 2026-09-19 by reading the tree, not the ledger: the parameter is exposed on `linkedin_search_jobs` and mapped in `server.py:3055 `_BOOLEAN_FILTERS``, and `tests/test_job_search_result_window.py` passes (6 tests). **Fired live against RESULT SETS, not merely against a pill** (`scripts/_probe_job_search_result_sets.py`, 13 loads, one session) with three controls deciding whether anything counted: POSITIVE another profession same city moved 7 of 7 shared 0; NEGATIVE a parameter LinkedIn never had moved 0; STABILITY the baseline retaken LAST moved 0, so the drift floor is ZERO. **14 ids moved on a floor of 0 -- the maximum available; it replaced the window entirely.** Owners by `git log`: `15c6693`, `af67cb8`, adopted `400e761`. Evidence `_audit/_scratch/_progress-job-search-params.md` s1, s5. **CORRECTED 2026-09-20 (five-under-banked wave) -- THE DRIFT FLOOR IS A SESSION READING, NOT A PROPERTY OF THE SURFACE.** A SECOND run of the same probe in the same hour -- 17 loads, all three passes, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` -- measured the stability control at **4** ids and the negative control at 2, where the 13-load run quoted above measured 0 and 0. Both are real readings of a surface that ranks; neither is the floor. Note also that the 13-load run's own raw output no longer exists: the probe writes to one fixed path, which was overwritten at 16:45 and again at 16:49, forty minutes before the progress document this cell cites was written at 17:29, so that run survives only in that document's prose. THIS ROW SURVIVES THE STRICTER FLOOR: the second run's own verdict line reads `UNDER TEN APPLICANTS f_EA=true MOVED 14, above the 4-id drift floor`, so the conclusion is corroborated twice and only the phrase "the drift floor is ZERO" was overstated. Reading: `_audit/2026-09-20-the-five-under-banked.md`. |
| 13 | Filter: In your network | a507441 | COVERED-PROVEN | `in_your_network` -> `f_JIYN`. **SHIPPED 2026-09-04 AND VERIFIED LIVE 2026-09-05; the row was never moved.** Re-verified independently 2026-09-19 by reading the tree, not the ledger: the parameter is exposed on `linkedin_search_jobs` and mapped in `server.py:3055 `_BOOLEAN_FILTERS``, and `tests/test_job_search_result_window.py` passes (6 tests). **Fired live against RESULT SETS, not merely against a pill** (`scripts/_probe_job_search_result_sets.py`, 13 loads, one session) with three controls deciding whether anything counted: POSITIVE another profession same city moved 7 of 7 shared 0; NEGATIVE a parameter LinkedIn never had moved 0; STABILITY the baseline retaken LAST moved 0, so the drift floor is ZERO. **12 ids moved on a floor of 0.** Owners by `git log`: `15c6693`, `af67cb8`, adopted `400e761`. Evidence `_audit/_scratch/_progress-job-search-params.md` s1, s5. **CORRECTED 2026-09-20 (five-under-banked wave) -- THE DRIFT FLOOR IS A SESSION READING, NOT A PROPERTY OF THE SURFACE.** A SECOND run of the same probe in the same hour -- 17 loads, all three passes, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` -- measured the stability control at **4** ids and the negative control at 2, where the 13-load run quoted above measured 0 and 0. Both are real readings of a surface that ranks; neither is the floor. Note also that the 13-load run's own raw output no longer exists: the probe writes to one fixed path, which was overwritten at 16:45 and again at 16:49, forty minutes before the progress document this cell cites was written at 17:29, so that run survives only in that document's prose. THIS ROW SURVIVES THE STRICTER FLOOR: the second run's own verdict line reads `IN YOUR NETWORK f_JIYN=true MOVED 12, above the 4-id drift floor`, so the conclusion is corroborated twice and only the phrase "the drift floor is ZERO" was overstated. Reading: `_audit/2026-09-20-the-five-under-banked.md`. |
| 14 | Filter: Fair chance employer | a415496 | COVERED-PROVEN | `fair_chance_employer` -> `f_FCE`. **SHIPPED 2026-09-04 AND VERIFIED LIVE 2026-09-05; the row was never moved.** Re-verified independently 2026-09-19 by reading the tree, not the ledger: the parameter is exposed on `linkedin_search_jobs` and mapped in `server.py:3055 `_BOOLEAN_FILTERS``, and `tests/test_job_search_result_window.py` passes (6 tests). **Fired live against RESULT SETS, not merely against a pill** (`scripts/_probe_job_search_result_sets.py`, 13 loads, one session) with three controls deciding whether anything counted: POSITIVE another profession same city moved 7 of 7 shared 0; NEGATIVE a parameter LinkedIn never had moved 0; STABILITY the baseline retaken LAST moved 0, so the drift floor is ZERO. **14 ids moved on a floor of 0 -- the maximum available; it replaced the window entirely.** Owners by `git log`: `15c6693`, `af67cb8`, adopted `400e761`. Evidence `_audit/_scratch/_progress-job-search-params.md` s1, s5. **CORRECTED 2026-09-20 (five-under-banked wave) -- THE DRIFT FLOOR IS A SESSION READING, NOT A PROPERTY OF THE SURFACE.** A SECOND run of the same probe in the same hour -- 17 loads, all three passes, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` -- measured the stability control at **4** ids and the negative control at 2, where the 13-load run quoted above measured 0 and 0. Both are real readings of a surface that ranks; neither is the floor. Note also that the 13-load run's own raw output no longer exists: the probe writes to one fixed path, which was overwritten at 16:45 and again at 16:49, forty minutes before the progress document this cell cites was written at 17:29, so that run survives only in that document's prose. THIS ROW SURVIVES THE STRICTER FLOOR: the second run's own verdict line reads `FAIR CHANCE f_FCE=true MOVED 14, above the 4-id drift floor`, so the conclusion is corroborated twice and only the phrase "the drift floor is ZERO" was overstated. Reading: `_audit/2026-09-20-the-five-under-banked.md`. |
| 15 | The "All filters" panel as a surface | a523136 | COVERED-PROVEN | **OPENED AND ENUMERATED LIVE 2026-09-19**, at an address already on the allowlist (`readonly.py:299` admits `/jobs/search/` with a query) -- zero boundary cost. `"All filters"` had **zero grep hits across the whole package** before this: nobody had ever opened it. Page control PASS (`Easy Apply` / `Date posted` / `Experience level` non-zero in the rail beside the trigger); exactly 1 control carries the name; pressed; Escape after. **17 filter groups**, labels through `shape.census_shape`, option COUNTS only and no option text (the Company group's options are employer names): Sort by (2 radios), Date posted (4 radios), Experience level (6), Company (13), Job type (7), Remote (3), Easy Apply (1), Has verifications (1), Location (10), Industry (11), Job function (13), Title (10), Under 10 applicants (1), In your network (1), Fair Chance Employer (1), Benefits (11), Commitments (5). Evidence `_audit/_scratch/_probe-small-measures-live.txt`; instrument `scripts/_probe_small_measures_live.py`, shown failing before admission |
| 16 | Suggested filters (adaptive, on AI search) | a6889044 | GAP | **NOT MEASURED 2026-09-19, and stated rather than left to look like a zero.** The All-filters wave opened `/jobs/search/` and enumerated the panel (see row 15), but performed a KEYWORD search, not an AI search, and carried no needle for an adaptive suggestion strip. A needle never fired is not a zero. **THE NEEDLE WAS THEN FIRED, SAME DAY:** `/jobs/search/` re-read under a NATURAL-LANGUAGE query, page control PASS, and `Suggested filter` / `Suggested filters` / `Try searching` / `Recommended filter` all read **0 in main text and 0 in html**; structure around the rail shows `[role="list"]` 0, `[role="radiogroup"]` 0, `button[aria-pressed]` 1, `fieldset` 4. What IS there: `Suggested` 8 in html but 0 in main text, `Refine` 2 in html. **STAYS GAP AND DOES NOT MOVE TO MEASURED-ABSENT, for one reason stated rather than hidden: I cannot confirm LinkedIn treated that query as an AI search.** There is no observable that says which search MODE served the page, so a zero here cannot be separated from a zero on the wrong mode -- the same class of error as reading a tabbed category without pressing its tab. NEXT ARTIFACT: an observable that identifies the search mode, before any needle count on this row is worth taking. Zero boundary cost -- same already-admitted address. Evidence `_audit/_scratch/_probe-small-measures-followup-v2.txt` |
| 17 | Search from device current location | a507703 | EXCLUDED-RULED | **RETIRED 2026-09-05, `DEVICE-GEOLOCATION` (3.7) -- and NOT on this row's own ground.** The impossibility half above is false and must not be inherited: this server drives Chrome over CDP, which can override geolocation. It retires because the capability is already served by naming the location as a parameter, and `a523131`, fetched this pass against every spelling, documents no distance, radius, within-X or near-me control. REOPENER: he wants a search whose location he cannot name AND `location` cannot express it -- both halves. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 18 | Recent searches: view and re-run | a523136 | COVERED-UNFIRED | **BUILT 2026-09-23 (lane L3), NEVER FIRED LIVE.** `linkedin_recent_job_searches` -> `job_home.read_recent_searches`. **THE ROW WAS PRICED ON THE WRONG ADDRESS.** `/jobs/search-history/` is refused and nothing shows it drawing this list; the list is drawn on the JOBS HOME, `/jobs/jam/`, which is where `/jobs/alerts/` lands (live-capture 12.1) and which has been admitted since 2026-09-20 with nothing behind it. Measured on the gitignored live capture of that landing: one `Recent job searches` list in `main`, six entries, each an anchor to the semantic-search route tagged `origin=SEMANTIC_SEARCH_HISTORY`, three carrying the `Alert On` badge, all six in the DOM without a press. VIEW: per entry `search_keywords` (off the href, by the shipped `shape.notification_handles`, the function that already publishes alert keywords off notifications), `location` (the one subtitle token that is not a badge; two candidates read `ambiguous` and publish nothing), `alert_on`, `in_your_network`, `workplace`, and the NAMES of the filters carried -- never a filter value (a salary band is his pay expectation), never a place id, never the href. RE-RUN: `linkedin_search_jobs(keywords=..., location=...)`, which builds its own address; this reader never follows an entry's href, and the route it points at stays refused. Fixture `tests/fixtures/synthetic/jobs_home_recent_searches.html`, built by `scripts/_build_jobs_home_fixture.py` from the capture with every query, place and value invented; checks `tests/test_job_home.py` (18), including a collapsed entry hidden two ways -- `visibility:hidden` is the mode under which `inner_text` reads it empty, and the reader uses `text_content`. **WHAT REMAINS FOR CP: one live call**, which is also the first check that `/jobs/jam/` serves this list when opened directly. |
| 19 | Recent searches: clear history | a523136 | GAP | -- |
| 20 | Result card fields: title, company, location, hiring status, posted-when, job id, url | a507441 | CP | `shape.parse_job_card` (`shape.py:768-779`) |
| 21 | Posting detail: title, company, location, salary, workplace type, employment type, applicant count, posted, description | a1395225, a1396429 | CP | `shape.parse_job_detail` + `_split_meta_line`; `linkedin_job_detail` |
| 22 | Posting: which apply route it uses (LinkedIn Apply vs off-site ATS, and the host) | a512388 | CP | `apply_path`; two routes measured, "Neither the label nor the href classifies alone; both must agree" (`writes.py:645`) |
| 23 | Hiring-status chip on a posting ("Actively reviewing applicants", "Be an early applicant") | a507990, a1661038 | CP | `shape._HIRING_STATUS` (`shape.py:1657`) |
| 24 | Hirer responsiveness: review-time estimate, "Responses managed off LinkedIn" | a1661038 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live by `scripts/_probe_unfired_job_detail_insights.py` through the shipped `linkedin_job_detail` over **11 real postings** harvested via the shipped search tool. **THE TEST IS DISCRIMINATION, NOT PRESENCE:** this field is a boolean, so a reader whose selector had rotted would return False for every posting on earth and be indistinguishable from a correct one over a flat sample. It is therefore tallied three ways and banked only on OBSERVED-BOTH. `responses_managed_off_linkedin`: **true on 5 postings, false on 6, absent on 0 -> OBSERVED-BOTH.** **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree, not from a docstring or another wave's report: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader emits **`responses_managed_off_linkedin`** in its returned dict (`dom.py:8309-8314`), and the function returns `out`. **So the field reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** the field is surfaced and no run has been recorded asserting a value on a live posting. Same chain, same commit, as `J 27` -- one reader, six fields, six rows that all sat GAP because nothing joined the code to the census. |
| 25 | "Why am I seeing this job?" | a7181681 | EXCLUDED-RULED | **RETIRED 2026-09-05, `PANEL-NOT-OBSERVED` (3.13), on the measurement already taken.** The needles read zero where the control -- Show match details / Show Premium Insights / How you match -- reproduces 1/1/0 on four committed captures, reads 0/0/0 on exactly the two the fixture table marks un-hydrated, and reproduced 1/1/0 LIVE twice across a browser restart. So the panel is not drawn for this account, rather than unread. REOPENER: the control at 1/1/0 AND a target needle non-zero; a zero without the control firing reopens nothing. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 26 | "Promoted by hirer" labelling on a result | a512429 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live by `scripts/_probe_unfired_job_detail_insights.py` through the shipped `linkedin_job_detail` over **11 real postings** harvested via the shipped search tool. **THE TEST IS DISCRIMINATION, NOT PRESENCE:** this field is a boolean, so a reader whose selector had rotted would return False for every posting on earth and be indistinguishable from a correct one over a flat sample. It is therefore tallied three ways and banked only on OBSERVED-BOTH. `promoted`: **true on 9 postings, false on 2, absent on 0 -> OBSERVED-BOTH.** At n=4 this field read 4/0 and would have banked as OBSERVED-TRUE; the larger sample is what produced a false and proved discrimination. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree, not from a docstring or another wave's report: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader emits **`promoted`** in its returned dict (`dom.py:8309-8314`), and the function returns `out`. **So the field reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** the field is surfaced and no run has been recorded asserting a value on a live posting. Same chain, same commit, as `J 27` -- one reader, six fields, six rows that all sat GAP because nothing joined the code to the census. |
| 27 | Verification badge on a posting | a1492056 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** Fired live by `scripts/_probe_unfired_job_detail_insights.py` through the shipped `linkedin_job_detail` over **11 real postings** harvested via the shipped search tool. **THE TEST IS DISCRIMINATION, NOT PRESENCE:** this field is a boolean, so a reader whose selector had rotted would return False for every posting on earth and be indistinguishable from a correct one over a flat sample. It is therefore tallied three ways and banked only on OBSERVED-BOTH. `verified_job`: **true on 5 postings, false on 6, absent on 0 -> OBSERVED-BOTH.** NOTE ON THE OLD EVIDENCE: this row's cited `_audit/_scratch/_for-small-measures-covered-vs-gap.tsv` is GITIGNORED and absent from a clone, so that half of the chain was checkable nowhere. The fired proof above replaces it and is re-derivable by re-running the probe. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-19. THE BUILD REACHED ITS TWIN IN ANOTHER SLICE AND NOT THIS ROW** -- a propagation failure, not a missing capability. Verified END TO END from the tree rather than from the twin's cell: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader returns `"verified_job": bool(markers.get("verified"))` at `dom.py:8313`, and the function returns `out`. **So the field reaches a caller today.** Its twin `profile.md K10` (*Verification badge as it appears on job posts*) was banked COVERED-UNFIRED earlier the same day on exactly this evidence while this row still read `--`: same capability, one build, two slices, one banked. **UNFIRED and not PROVEN, deliberately:** the field is surfaced but no run has been recorded asserting a value on a live posting, and matching the twin's honesty is worth more than an upgrade nobody measured. **FOUND BY A HANDED-OVER CANDIDATE LIST WHOSE PRECISION IS THE REAL HEADLINE:** 1 true pair of 61 (`_audit/_scratch/_for-small-measures-covered-vs-gap.tsv`, from `settings-tail`). See `_audit/2026-09-19-covered-vs-gap-pairs.md` |
| 28 | Report a job as closed | a515926 | GAP | -- |
| 29 | Skills Match insight ("x of y skills match your profile") | a793433 | EXCLUDED-RULED | **RETIRED 2026-09-05, `PANEL-NOT-OBSERVED` (3.13), on the measurement already taken.** The needles read zero where the control -- Show match details / Show Premium Insights / How you match -- reproduces 1/1/0 on four committed captures, reads 0/0/0 on exactly the two the fixture table marks un-hydrated, and reproduced 1/1/0 LIVE twice across a browser restart. So the panel is not drawn for this account, rather than unread. REOPENER: the control at 1/1/0 AND a target needle non-zero; a zero without the control firing reopens nothing. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 30 | Skills Match: add a missing skill from the insight | a793433 | EXCLUDED-RULED | **RETIRED 2026-09-05, `PANEL-NOT-OBSERVED` (3.13), on the measurement already taken.** The needles read zero where the control -- Show match details / Show Premium Insights / How you match -- reproduces 1/1/0 on four committed captures, reads 0/0/0 on exactly the two the fixture table marks un-hydrated, and reproduced 1/1/0 LIVE twice across a browser restart. So the panel is not drawn for this account, rather than unread. REOPENER: the control at 1/1/0 AND a target needle non-zero; a zero without the control firing reopens nothing. See `_audit/2026-09-05-decide-retire-rulings.md` |

### B. Job alerts (12)

Every alert WRITE is a GAP. Everything the alerts DELIVER is served by the skill.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 31 | Create a job alert from a search | a511279 | GAP | -- |
| 32 | Create a job alert from a company Page | a554166 | GAP | -- |
| 33 | Edit an existing job alert | a1420165 | GAP | -- |
| 34 | Delete / turn off a job alert | a1420165, a511279 | GAP | -- |
| 35 | Set alert frequency (daily / weekly) | a1420165 | GAP | -- |
| 36 | Set alert delivery channel (email / app / both) | a1420165 | GAP | -- |
| 37 | List and manage all alerts | a1420165 | GAP `SKILL` | server: none. Skill: each digest body carries `Your job alert for {QUERY} in {GEO}` and a stable `savedSearchId=`, so the live alert set is enumerable from mail; `alert-tuning.md` holds the current 5-alert inventory |
| 38 | Read the jobs an alert delivered | a511279 | GAP `SKILL` | server: none. Skill step 1-3: `jobalerts-noreply@linkedin.com`, ~6 cards/email, 5 emails/day |
| 39 | Read job recommendations ("Jobs you may be interested in") | a512279 | COVERED-UNFIRED | **BUILT 2026-09-23 (lane L3), NEVER FIRED LIVE AT THIS INDEX.** `linkedin_premium_job_collection(2)` -> `job_collections.read_job_collection`, which now carries `recommended` as its third, APPENDED collection: `/jobs/collections/recommended/`, admitted 2026-09-05, loaded by `linkedin_job_collections` since 2026-09-19, and the very page the reader's two-tier slot shape was measured on. It returns the recommended postings' NUMERIC IDS -- `linkedin_job_collections` returns their COUNT by design -- each consumable by `linkedin_job_detail`, the same shape `J 125` banked on for top-applicant. Run offline over the live capture itself (scripts stripped, every request aborted): 24 slots, 7 hydrated, 24 ids, 0 refused. Committed evidence: `tests/fixtures/synthetic/jobs_recommended_skeleton.html`, built by `scripts/_build_job_list_skeleton.py` from that capture keeping the tier pattern and nothing textual, and `tests/test_job_collections.py` section 8 (index 2 reads it as measured; the ids tool and the counts tool are pinned to one address). The `SKILL` tag is dropped because the legend scopes it to a GAP; the skill still serves the same need from mail. **WHAT REMAINS FOR CP: one live call at index 2.** Prior cell, kept: server: none. Skill: `jobs-noreply@linkedin.com`, `FACET_SUGGESTIONS_COMMS_EMAIL` |
| 40 | Read per-job network proximity ("2 connections", "1 company alum") | `tests/fixtures/jobs_search_hydrated.html` | CP | **FIRED LIVE 2026-09-21 (wave `what-is-reachable-now`) AND BANKED -- the bar was PRE-REGISTERED by the building wave and is quoted three lines down: *"it enters at COVERED-UNFIRED and moves to COVERED-PROVEN on one live search."* Four live searches were run through the shipped `linkedin_search_jobs` and `linkedin_job_detail`, on four runs, and every reading reproduced.** `scripts/_probe_proximity_live.py`, attach mode, provenance printed per run. **THE PER-JOB RATE IS 1 OF 14 DISTINCT POSTINGS, NOT 3 OF 21 CARDS, AND THE DIFFERENCE IS THIS PROBE'S OWN CORRECTED DEFECT:** one popular posting matched all three search terms and was rendered three times, so counting CARDS reports one fact three times -- the same "de-duplicate on the fact, not the match" hazard `find_proximity` closes INSIDE a card, reappearing in the instrument that measures it. **WHAT BANKED: the reader reaches the live field and SELECTS.** Within surface, 1 of 14 jobs drew `count_read`/`company_alum` and 13 omitted the key -- a dead selector omits it on all 14. Across surface, that same posting read `count_read` on the search card and `relation_only` on the detail page, which is the asymmetry this reader's design PREDICTED before any browser ran (detail draws the relation over a face pile and states no number). The leak gate never fired: every emitted value was `int` or `None` on every reading, and `shape.company_about` rode along at zero extra load. **WHAT DID NOT BANK, STATED SO NOBODY READS MORE INTO THIS:** the COUNT axis discriminates nothing -- every count read was `2`, n=1 distinct posting, so this fire proves the reader REACHES the field and does NOT prove the number is right. The `N 54` lesson (a clean, discriminating count that was wrong by one) is untouched by it. Gate control `scripts/_check_the_proximity_leak_gate_can_fail.py`, shown refusing a string in each of three slots without ever quoting it, refusing a bool, and calling an absent-everywhere tally the DEAD-READER signature. Prior state and its evidence: **BUILT 2026-09-21 (wave `proximity-field`), NEVER FIRED LIVE** -- `shape.find_proximity`, riding along in `parse_job_card` (so `linkedin_search_jobs` and every saved/applied row) and in `parse_job_detail` (`linkedin_job_detail`). No new tool, no new address, no edit to `server.py`: boundary cost 0, exactly as this row priced it. RETURNS `{state, relation, count}` -- **THREE INTEGERS OR NONE**, where `relation` and `state` are POSITIONS in closed alphabets this package ships; no string off a page can leave the reader on any path. MEASURED over the committed captures in a local headless Chromium, in BOTH layouts (LinkedIn's screen-reader rule present and stripped): `jobs_search_hydrated` -- 1 of 7 rows reads `count_read`/`company_alum`/**1**, the other 6 omit the key; `job_detail_following_hydrated` -- `relation_only`, because that page draws "Company alumni from `<ORG>`" with NO count and no name-free twin, so detail is a relation and never a number. **THE DISCRIMINATOR HELD THROUGH THE BUILD:** the un-hydrated twins read 0 of 7 rows and `None`. **THE SAFETY POINT:** the search card draws the insight TWICE and the ACCESSIBLE (`aria-hidden`) copy is the NAME-FREE one while the `.visually-hidden` copy carries the employer -- the reader never chooses between them, because `strip_screen_reader_copies` has already removed the name-carrying copy BY COUNT before `parse_job_card` builds `lines`. A fixture-wide census puts the field on **2 of 20** committed captures, both hydrated job surfaces. WHAT REMAINS FOR CP: one live fire. Evidence `_audit/2026-09-21-the-proximity-field.md`; checks `tests/test_proximity_reader.py` (27 functions, 73 cases) and `tests/test_proximity_is_on_a_read_surface.py` (3 functions, 6 cases, one INVERTED on landing) -- all 30 functions driven RED before being allowed to certify, two of them rewritten because a mutation proved they could not fail, and one late hardening edit convicted by them in a single run. The `linkedin-jobs` skill still serves the same need from mail, from a different and richer source -- that is not a reason to hold this row at GAP, and the `SKILL` tag is dropped because the legend scopes it to a GAP. |
| 41 | Subscribe / unsubscribe the job-collections weekly digest | a1652837 | GAP | -- |
| 42 | Job collections and their five groupings (Domains, Industries, Company Benefits, Editorial, Corporate Commitments) | a1652837 | COVERED-PROVEN | **READ LIVE 2026-09-19 -- the address SERVES, and a census-based reader CANNOT be built on it.** `/jobs/collections/recommended/` was admitted by `tests/test_school_and_collections_boundary.py` with nothing behind it (Amendment A10's shape), and nobody had opened it. Opened once, twice in the same session, via `scripts/_probe_job_collections_live.py`: relation **SERVED** both times (not a redirect), 93 controls, and the invitation badge read identical BEFORE and AFTER, so the load consumed nothing. **THE BLOCKING FINDING, and it was established by a CONTROL refuting my own instrument twice:** the page draws **ZERO `/jobs/view/` anchors** -- and so does `/jobs/search/`, a page that certainly lists jobs. A first marker keyed on `/jobs/view/` read 0 everywhere; a second keyed on `href` read `(no href)` on **147 of 147** controls. Both zeros measured the instrument, not the surface: `dom.read_surface_census` carries `has_href` and `href_shape` and **never hands out a raw href by construction**. Re-run against the real fields, the shaper is visibly holding (`<company>`, `<id>`) and the histogram contains no posting link at all. **SO THE REMAINING COST IS NOT `allowlist +1` -- that is already spent -- it is a PURPOSE-BUILT READER for anchors the shipped census cannot see.** One instability recorded rather than smoothed: the same address read 75 controls on one run and 93 about five minutes later, so any count from this surface is a reading with a timestamp. See `_audit/2026-09-19-read-tail.md` **READER BUILT 2026-09-19, `linkedin_server/collections_page.py`, AND THE FIVE GROUPINGS ARE NOT DRAWN.** The reader ships the vocabulary INTO the page and gets back a POSITION IN A TUPLE, so no page string crosses the boundary at all -- stricter than `groups.py` (takes hrefs somebody read) and `menus.py` (a pure function that IS handed a label). **ITS POSITIVE CONTROL FIRES:** the same in-page code run against a detached synthetic container matched **5 of 5** groupings plus **1 decoy unmatched**, so it matches AND discriminates, at no page-load cost. **With that control firing the live zero is a MEASUREMENT, not an artifact:** scanning headings, tabs and buttons -- 79 nodes -- the live page matched **NONE** of the five, identically across two reads, while the jobs-search control also matched none. So this row's capability AS STATED is not reproducible at this address for this account: the page serves and has content (53 cards under two headings), but the five groupings named in the help article are not labels on it. **STILL GAP, and the remaining step is TOOL WIRING, not a parser:** the reader has no `linkedin_*` entry point, and `server.py` is permanently contended, so wiring it is a deliberate act for a wave that can hold that file. Whoever does it inherits a reader whose control already fires. **AND THE ANCHOR READER SEES 9 JOB POSTINGS HERE, 2026-09-19.** `linkedin_server/anchors.py` classifies anchors by ROUTE SHAPE, shipping its table INTO the page and getting back integer indices, so no href crosses the boundary. Four live loads: **`job_posting` 9, `company_page` 6-9** -- against the ZERO the census-based probe measured on this same address, which was a fact about `read_surface_census` shaping hrefs by construction. **So the page is NOT empty and never was.** Two limits stated rather than smoothed: the anchor profile MOVES between loads (25 to 35 anchors across four reads, and one load drew 4 `member_profile` anchors where another drew 0), and **the five NAMED groupings are still not drawn** -- those are separate findings and neither cancels the other. Still GAP: the reader has no `linkedin_*` entry point. See `_audit/2026-09-19-anchor-reader.md` **WIRED AND FIRED 2026-09-19: `linkedin_job_collections`.** The tool opens this address once and runs both readers on the same load, returning COUNTS ONLY -- 9 job postings, 0 member-space anchors, 0 groupings matched, 52 headings seen, **every field an integer and no page string in the payload**. **THE CAVEAT IS DISCHARGED, 2026-09-19.** It was first banked on an IN-PROCESS call, with the transport named as unproven and the disagreement left visible. The lead then settled it by measurement rather than by ruling: the tool was called OVER THE MCP TRANSPORT against a restarted server -- 43 tools on the wire, call succeeded, **30 leaf values of which 4 are strings and all four are the staleness diagnostic, zero page content; `linkedin.com` and `/in/` absent from the payload entirely.** So the structural name-freedom holds ON THE WIRE and not only in unit tests. **The five named groupings remain NOT DRAWN** (matched 0 against a control that matches 5 of 5 on a synthetic fixture), and the surface MOVES between loads, so every count is a reading with a timestamp. See `_audit/2026-09-19-anchor-reader.md` |

### C. Saved jobs and the job tracker (16)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 43 | Save a job | a513247 | CP | `linkedin_save_job`. **The one write proven to land** -- see section above |
| 44 | Unsave a job | a513247 | **CP 2026-09-19** | `linkedin_unsave_job`. **FIRED AND VERIFIED.** Six separate places in `_audit/` recorded this as never fired, including after it became capable; that is now superseded. **The verification read a DIFFERENT surface from the one clicked** -- the saved tab (`?stage=saved`) count went 2 -> 1, and the posting's own label flipped Unsave -> Save. Prior state had been established TWO ways before the fire (the tab contained the posting, and the posting reported itself saved). Re-saved afterwards, 1 -> 2, so the membership round trip is closed in both directions. **ONE THING STAYS UNSETTLED AND THE GATE IS RIGHT ABOUT IT:** whether re-saving restores the original saved DATE, and therefore the list's ORDER -- reversible in membership is not reversible in ordering. The fire could not distinguish the two hypotheses (the posting had been saved sixty seconds earlier, so both put it at position 1), and the version that WOULD answer it risks a pre-existing save's place permanently. Evidence: `_audit/2026-09-19-tier1-fires.md` rungs 2 and 3 |
| 45 | Read the Saved list | a513247 | CP | `linkedin_saved_jobs`, `?stage=saved` |
| 46 | Read whether ONE posting is saved, from the posting | a513247 | CP | `job_detail.save_state`; three-valued, `shape.SAVE_LABELS` both states measured |
| 47 | Read the Applied list | a512329 | CP | `linkedin_my_applications`, `?stage=applied` |
| 48 | Read application status (applied / application viewed / resume downloaded / no longer accepting) | a508716 | CP | `linkedin_my_applications` row status; LinkedIn documents exactly two notification types and both are carried |
| 49 | Read the In Progress / Draft list | a8684146 | CP | `linkedin_draft_applications`, `?stage=draft`. Trap recorded: the tab is LABELLED "In Progress" and ADDRESSED `?stage=draft` |
| 50 | Read the Interview stage | a8684146 | XR | `readonly.py:198` enumerates `(saved\|applied\|draft)`; `readonly.py:195` -- "interview, archived and clicked_apply remain **deliberately absent** -- nothing builds them" |
| 51 | Read the Archive stage | a8684146, a513247 | XR | same allowlist and same sentence |
| 52 | Read the clicked_apply stage (off-site apply-clicks) | a8684146 | XR | same allowlist and same sentence |
| 53 | Archive a job | a513247 | XR | `readonly.py:992` -- `"archive"` is on the mutation-verb denylist; no tool |
| 54 | Change a job's tracker stage manually | a8684146, a513247 | GAP | -- |
| 55 | Add notes to a tracked job | a8684146 | GAP | -- |
| 56 | Filter the tracker by date posted | a8684146 | GAP | -- |
| 57 | View network connections reachable for a tracked job | a8684146 | GAP | **BUILT 2026-09-23 AND WITHDRAWN THE SAME DAY, BEFORE ANY MERGE: THE JOIN THIS CELL CALLS "THE BUILDABLE ROUTE" IS A DERIVED NAVIGATION, WHICH THIS REPOSITORY FORBIDS.** A server-side join reads job ids OFF THE TRACKER PAGE and navigates to each, so the page chooses the next url. `tests/test_navigation_is_never_derived.py` states the rule -- *"the process must be able to say what it is about to navigate to WITHOUT having asked the page, because a page that can choose the next url can choose a stranger's"* -- and its `KNOWN_DERIVED_NAVIGATIONS` has never held an entry. **ITS ENGINE WOULD NOT HAVE CAUGHT THIS ONE:** it taints only a `goto` return and a `.url`, and says itself that page content is left out as a limitation, not a permission; a self-review found it. **WHAT WORKS TODAY, WITH NO BUILD:** the CALLER composes it -- `linkedin_saved_jobs` (or its two siblings) returns the ids and `linkedin_job_detail(id)` returns each posting's proximity (`relation_only` on a posting, fired live for `J 40`), every target supplied by the caller, which is the shape the rule permits. Whether that composition closes the row is the question `_audit/2026-09-21-the-jobs-direction.md` section 6 item 1 leaves unruled, the same one `J 107` and `J 116` wait on. Evidence `_audit/2026-09-23-lane-l3-jobs.md`. PRIOR CELL, KEPT: THE SKILL DOES NOT SERVE THIS ROW, measured against its source: `referral_join.py` loads a DIFFERENT platform's applications database read-only, keys `warm_referrals` on COMPANY rather than on a job, and takes its proximity from a static extract dated 2026-08-20; nothing in the skill reads LinkedIn's own tracker. "A tracked job" here means a job in THAT tracker -- this row sits in section C among rows about LinkedIn's My Jobs stages. Both halves already exist in this repo: the tracker is read today by `linkedin_my_applications` and `linkedin_draft_applications` (rows 47-49, all CP), and the proximity field sits on the job surfaces per row 40. What is missing is the JOIN, and nobody owned it while the row was filed as served. BLOCKED behind row 40. The skill performs an ADJACENT and more valuable join -- applied-on-the-other-platform AND has-network-here -- which is not this capability and must not be deleted when this one is built. **UNBLOCKED 2026-09-21: row 40 is BUILT**, so the missing half is no longer the proximity read -- it is still the JOIN, and the route to it is now measured rather than assumed. A fixture-wide census of the proximity needle puts the field on 2 of 20 committed captures, both HYDRATED JOB SURFACES; **`jobs_tracker_row.html` carries ZERO**, so the tracker card does not render the insight and this join cannot be done from a tracker row alone. The buildable route is tracker -> job ids (`linkedin_my_applications` / `linkedin_draft_applications`, rows 47-49) -> `linkedin_job_detail` per job, one page load each, and what proximity yields THERE is `relation_only` -- a BOOLEAN, with no count, because the detail page states no number. **Row stays GAP:** nothing was built for it, nobody owns it, and it was not forced. |
| 58 | Bulk-unsave | a513247 | n/a | LinkedIn itself has none: "there is no way to unsave multiple jobs at once" |

### D. Applying (25)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 59 | Easy Apply, single-screen posting (submit) | a512388, a512348 | CP | `linkedin_apply_job`. **Fired live once; it did not submit; zero applications have ever landed.** See section above |
| 60 | Easy Apply, MULTI-STEP form (a posting that draws Next) | a512388 | XR | `server.py:3906` -- "**zero advance controls are present** ... filling in steps that have never been seen, to reach a submit that cannot be withdrawn, is **the one guess this server does not make**" |
| 61 | Answer screening questions | a526248, a507694 | XR | same gate; a screening screen is an advance control |
| 62 | Select a stored resume during Easy Apply | a512405 | XR | same gate |
| 63 | Attach a cover letter during Easy Apply | a7121956 | XR | same gate |
| 64 | Answer follow-up questions | a507694 | XR | same gate |
| 65 | Review screen before submit | a512388 | XR | same gate |
| 66 | Apply off-site (company site / ATS) | a512388 | XR | `server.py:3897` -- "**OFF-SITE POSTINGS ARE REPORTED, NOT DRIVEN.** ... Driving a form on somebody else's domain, under their terms, is not this server's to do **at any capture quality**" |
| 67 | "Apply with LinkedIn" on an external partner site | a507542 | XR | same reason: off-domain |
| 68 | Save an application as a draft / resume one | a8684146 | GAP | -- |
| 69 | Discard a draft application | a8684146 | XR | `server.py:988` names the control and declines it: a "Delete" control, "**never pressed from here**", behind a dialog "this server does not act on either" |
| 70 | Upload a NEW resume | a510363 | GAP | -- |
| 71 | List / delete stored resumes (max 4) | a510363, a512405 | EXCLUDED-RULED | -- **REFUSED BY THE SECOND GATE, WHICH IS THIS CENSUS'S OWN NAMED BAR FOR A RULING.** Stored resumes are managed under `/jobs/application-settings/`, and `/jobs/application` is an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS` -- checked before the allowlist, so no pattern edit could reach it. Measured: `is_read_url` returns REFUSE. The blocker this row already carries, `JOBS-APPLICATION-FORBIDDEN`, is that gate wearing its own name. THE ROW IS COMPOUND -- "list / delete" carries a write verb -- but the substring closes both halves identically, so the state does not depend on which half is read. |
| 72 | Download a stored resume | a8313636 | GAP | -- |
| 73 | See which resume was submitted for a given application | a506680 | EXCLUDED-RULED | -- As `J 71`, and on the same gate. The capability necessarily addresses an application, and `/jobs/application` is an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`, checked before the allowlist -- measured: `is_read_url` returns REFUSE. No tool reaches it and no allowlist edit could. |
| 74 | Toggle "Share resume data with recruiters" | a1327213 | XR | `readonly.py:521` -- `/mypreferences/d/categories/` is on the forbidden-substring list; `server.py:4400` -- "ONE SETTING IS WRITABLE" (dark mode) |
| 75 | Toggle "Share your full profile when you click Apply" (and the Undo banner) | a512339 | XR | same settings-family refusal |
| 76 | Opt out of saving job-application data | a507694 | XR | same settings-family refusal |
| 77 | View / delete stored third-party applicant accounts | a507642 | XR | same settings-family refusal |
| 78 | Cover Letter Assistance (Premium AI drafting) | a7121956 | GAP | -- |
| 79 | Mark a job "Top Choice" (Premium, 3/month) | a1462229 | GAP | -- |
| 80 | Attach an optional message to the poster with a Top Choice mark | a1462229 | GAP | -- |
| 81 | Verify account to raise the Easy Apply daily limit | a8068422 | GAP | -- |
| 82 | Observe the Easy Apply daily limit / rate-pause state | a8068422 | GAP | -- |
| 83 | Save voluntary self-identification answers for reuse | a507694 | GAP | -- |

### E. Dismissing and expressing interest (4)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 84 | Per-job "Not interested" / hide from recommendations | **undocumented** (see section 5) | XR | `readonly.py:992` -- `"dismiss"` is on the mutation-verb denylist. The control is visible in this repo's own fixtures (`test_shape.py:94`, `2026-08-30-save-label.md:52`) |
| 85 | Undo a dismissal | undocumented | GAP | -- |
| 86 | "I'm interested" -- privately signal interest in a company (max 50, expires 1 year) | a1380509, a1427386 | GAP | -- |
| 87 | Delete the "expressed interest" activity record | a1427386 | XR | settings-family refusal, as rows 74-77 |

### F. Job preferences and Open to Work (13)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 88 | READ the current Open to Work state and its audience | a507508 | CP | `linkedin_my_profile.open_to_work`; `writes.py:806` -- LinkedIn "prints the CURRENT AUDIENCE verbatim next to the label ... at BOTH hydration states" |
| 89 | Turn Open to Work on / off | a507508 | XR | `writes.py:786` -- "**NEVER LOADED.** ... the EDITOR is a modal opened from that card and no capture of it exists at any hydration state. So there is no url here, and `assert_write_url` refuses this action outright". `server.py:82` -- "has no tool registered for it at all" |
| 90 | Change the Open to Work audience (All members / Recruiters only / Only you) | a507508 | XR | same spec; `server.py:3652` -- "none of those anchors, and no other href on the page, reaches the Open To Work audience editor. It opens as a modal, and **the click that would first show it is also the first that could change it**" |
| 91 | Delete / disable the Open to Work preferences | a507508 | XR | same spec |
| 92 | Set preference: job titles | a507508 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I4` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 93 | Set preference: locations | a507508 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I5` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 94 | Set preference: workplace types | a507508, a512279 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I6` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 95 | Set preference: start date | a507508 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I8` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 96 | Set preference: employment types | a507508 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I7` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 97 | Set India-only preferences: notice period, expected annual salary | a507508 | EXCLUDED-RULED | propagated 2026-09-19: twin `P I9/I10` is EXCLUDED-RULED on the NEVER-LOADED ruling (`profile.md` block I), and **this slice's own collapsed-block note says 92-100 live behind the same modal as 89-91**, which are XR here. Counter-argument recorded in `_audit/2026-09-19-profile-modals-measured.md`: one operator-present capture would reopen the block |
| 98 | Set / edit / delete the Minimum Pay preference | a1644694 | GAP | -- |
| 99 | Control career-interests visibility to recruiters | a510407 | EXCLUDED-RULED | **EXCLUDED-RULED 2026-09-19 by CONTAINER INHERITANCE**, under the ruling in `_audit/2026-09-19-two-census-conventions-ruled.md` s2: a container's exclusion propagates to its contents when the exclusion is UNREACHABILITY. **Container: `P I12`** *Job preferences / career-interests page*, EXCLUDED-RULED on its own measurement -- *zero of 237 urls reach one*. This row is a control ON that page, and you cannot press a control on a page nothing can load. **The container's measurement is CITED, not re-derived.** REOPENER, and it is narrower than the container's: I12's measurement is URL-reachability. A CLICK route would not have been caught by it -- the Open-To-Work editor is the standing case of a surface with no url whose controls are reachable by a press -- so if a click route to this page is ever observed, reopen this row with `P I12`. |
| 100 | "Signal your interest to recruiters at companies you've created job alerts for" | a1380509 | GAP | -- |

### G. Company research reachable from a job (15)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 101 | Identify the employer and its Page url from a posting | a550270 | CP | `job_detail.company_url` |
| 102 | Read whether the employer is already followed, from the posting | a548013 | CP | `job_detail.company_follow_state`, three-valued, read off the same rendering |
| 103 | Follow a company | a548013 | CU | `linkedin_follow_company`. **CORRECTED CP -> CU 2026-09-19. The cited evidence is a PERFORMABILITY verdict, not a fire.** The row quoted `2026-08-31-linkedin-perform.md:1318` -- "**PERFORMS** \| verified by re-reading the followed list" -- but that table is `## 29. THE THIRTEEN-ROW LEDGER`, whose subject is *"`writes.SANCTIONED_WRITES` holds thirteen actions"* and whose closing line is *"Rows 7-12 are the six refusals a caller can reach through a tool"*; the same verdicts appear at `## 10` under columns headed `before \| after`. **`apply_job` reads `PERFORMS` in that same ledger while row 59 of THIS table records "zero applications have ever landed"**, so `PERFORMS` is demonstrably not a landing claim. And the receipts of the cited document itself, `:1058-1059`, `:1462`, `:1794`: `confirm_tokens used 0`, `writes performed 0`, **"Nothing was fired."** No live-fire receipt for this action exists anywhere in `_audit/`. **This slice already knew the distinction** -- its own section *"THE SECOND CORRECTION: what 'live-fire' means for the three writes"* draws it, and gave `unsave_job` **NO. NEVER FIRED.** on the same ground. The NETWORK census slice's row 46 has held COVERED-UNFIRED all along; the two slices now agree. Evidence: section 4 of the document named in the DELTA note under section 1's count block. **HELD BY `OPERATOR-NAMES-THE-TARGET`** (2026-09-23): a write, so a live proof only at a target the operator names. It was held by `NO-IRREVERSIBLE-WRITE-IS-FIRED` until the operator's ruling (b) at 18:15 on 2026-09-23 (`WRITE-CLASS-B`) lifted the read-only rule; the register records that ruling as amended, and this condition as its own standing ruling. This slice's per-row table has no R/W column, so the hold is cited here, where `scripts/census_completion.py` reads it **THE GATE READS THE RELABELLED CONTROL SINCE 2026-09-23 (lane L4).** From 2026-09-19 LinkedIn drew this control as `Follow <employer>`, and the exact-label union matched it on 0 of 5 live postings (the follow-control live measurement of that date), so the gate refused every live posting while this row read CU. `dom.read_follow_control` now also reads the About-the-company card's one control whose name opens `Follow ` and continues with the employer name the card itself draws, and `shape.posting_follow_state` answers `not_following` from it; the relabelled ON label is unmeasured and reads unknown. Shown failing, then passing: `tests/test_posting_follow_relabelled.py` (the lane-L4 record, section 10.3). It has still never fired, so the state does not move. |
| 104 | Unfollow a company | a548013 | CU | `linkedin_unfollow_company`; same table, same correction and same date -- it quoted "**PERFORMS** \| addressed by NUMERIC id; refuses when the Page is not among the rendered rows", which describes the gate's aiming and not a write that landed. The NETWORK census slice's row 48 has held COVERED-UNFIRED all along. Evidence: section 4 of the document named in the DELTA note under section 1's count block. **HELD BY `OPERATOR-NAMES-THE-TARGET`** (2026-09-23): a write, so a live proof only at a target the operator names. It was held by `NO-IRREVERSIBLE-WRITE-IS-FIRED` until the operator's ruling (b) at 18:15 on 2026-09-23 (`WRITE-CLASS-B`) lifted the read-only rule; the register records that ruling as amended, and this condition as its own standing ruling. This slice's per-row table has no R/W column, so the hold is cited here, where `scripts/census_completion.py` reads it |
| 105 | List followed companies | a548013 | CP | `linkedin_followed_companies` |
| 106 | Company Page About tab (size, industry, locations) | a550270 | GAP | -- |
| 107 | Company Page Jobs tab / "see all jobs at this company" | a550270, a567373 | GAP | -- |
| 108 | Company Page People tab (titles, study areas, skills, how you are connected) | a550270 | GAP | -- |
| 109 | Company Page Life tab | a550270 | GAP | -- |
| 110 | Company Page Home / Posts tabs | a550270 | GAP | -- |
| 111 | Company Page Products / Services tabs | a550270 | GAP | -- |
| 112 | School Page Alumni tab | a567083 | EXCLUDED-RULED | -- **BLOCKED ON A RULING, NOT ON A READER, 2026-09-19.** `linkedin_server/anchors.py` classifies `school_page` anchors correctly -- proven by its control fixture, and it is the exact case a containment matcher gets wrong (`/company/example-school-group/` must stay a company). **But no school page was opened and that is deliberate:** reaching `/school/<slug>/` requires a slug, **a slug is a NAME**, and obtaining one means reading a name off his profile in order to navigate by it. That is a ruling this wave did not have and did not take. The boundary is already open (`tests/test_school_and_collections_boundary.py` admits the address), so the `allowlist +1` is spent and what remains is the ruling plus a page load. See `_audit/2026-09-19-anchor-reader.md` section 6 **RULED 2026-09-19: REFUSED, AND NOT BY A NEW RULE.** The lead's ruling, given on this wave's report: reaching `/school/<slug>/` requires reading a slug off his profile IN ORDER TO NAVIGATE BY IT, and **that is navigation derived from page content, which this repository already forbids**. A slug is also a NAME -- `groups.py` refuses a non-numeric segment *because a slug is a name*, and this is that rule one level up. The shape is identical to `MENTION-COMPOSITION-RULING`: the caller supplies the target explicitly; the server never assembles a destination out of what it read. **WHAT IS BUILT AND STAYS BUILT:** `linkedin_server/anchors.py` classifies `school_page` anchors correctly and its control proves it -- it is the exact case a containment matcher gets wrong. So the surface is SERVED BY THE CLASSIFIER and UNREACHABLE BY THIS SERVER unless a caller hands it the identifier. **REOPENER:** a caller supplying the school identifier explicitly, which needs no new rule at all -- it is the same shape as every other caller-supplied target here. This is a refusal with a reason, not an omission. See `_audit/2026-09-19-anchor-reader.md` section 6 |
| 113 | Company Page Insights tab (Premium) | a550270 | GAP | -- |
| 114 | Premium Page Insights: headcount over time, distribution and growth by function, notable alumni, job openings by seniority | a565340 | GAP | -- |
| 115 | Meet the hiring team on a posting (connect with / message the team) | a767235 | XR | `server.py:1387` -- "LinkedIn draws **a hiring team** and a 'people also viewed' rail beside a job, and **neither is read here**" |

### H. "How you match" and Premium job features (12)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 116 | "How you match" panel: top-applicant flag | a1462281 | GAP | -- |
| 117 | "How you match": skills associated with the job | a1462281 | GAP | -- |
| 118 | "How you match": your matching profile skills | a1462281 | GAP | -- |
| 119 | "How you match": skills missing from your profile | a1462281 | GAP | -- |
| 120 | "How you match": additional skills among applicants | a1462281 | GAP | -- |
| 121 | Applicant insights: your ranking percentile vs other applicants | a563146 | COVERED-UNFIRED | **FIRED 2026-09-20 AND DELIBERATELY NOT BANKED.** `scripts/_probe_unfired_job_detail_insights.py` fired `linkedin_job_detail` over 11 real postings. `applicant_insights` ARRIVED on 11 of 11 -- and that is not evidence for THIS row. Measured over all 11 panels: **percentile 0, rank 0**; the `metrics` sub-part carries applicant COUNTS, not a percentile. **7 of 11 postings drew the gated control `Show Premium Insights`, which this reader does not open** -- that is where the percentile lives. A probe reporting only 'the panel arrived' would have banked this on evidence for nothing. The capability is NOT DELIVERED by this chain. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree, not from a docstring or another wave's report: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader emits **`applicant_insights`** in its returned dict (`dom.py:8309-8314`), and the function returns `out`. **So the field reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** the field is surfaced and no run has been recorded asserting a value on a live posting. Same chain, same commit, as `J 27` -- one reader, six fields, six rows that all sat GAP because nothing joined the code to the census. |
| 122 | Applicant insights: top skills among applicants, experience/education levels | a563146 | COVERED-UNFIRED | **FIRED 2026-09-20 AND DELIBERATELY NOT BANKED -- PARTIAL.** Same run as `J 121`. The **experience/education half ARRIVES**: `seniority` and `education` came back populated on 11 of 11 panels with percentage splits (27 and 42 entries across the sample). The **top-skills half does NOT**: the token `skill` appears in **0 of 11** panels and `applicant_insights` has no skills sub-key at all -- it holds only `heading`, `metrics`, `seniority`, `education`. Half a capability is not a banked row. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree, not from a docstring or another wave's report: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader emits **`applicant_insights`** in its returned dict (`dom.py:8309-8314`), and the function returns `out`. **So the field reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** the field is surfaced and no run has been recorded asserting a value on a live posting. Same chain, same commit, as `J 27` -- one reader, six fields, six rows that all sat GAP because nothing joined the code to the census. |
| 123 | Premium hiring-company insights (hiring trends, growth rate, average tenure, feeder companies/schools) | a563146 | COVERED-PROVEN |**BANKED 2026-09-19. BUILT AFTER THE CENSUS FROZE AND THE ROW WAS NEVER MOVED.** Verified END TO END from the tree, not from a docstring or another wave's report: `linkedin_job_detail` (`server.py:3410`) assigns `out["insights"] = await dom.read_job_insight_panels(page)` at `:3665`, that reader emits **`company_insights`** in its returned dict (`dom.py:8309-8314`), and the function returns `out`. **So the field reaches a caller today.** **COVERED-UNFIRED, not PROVEN:** the field is surfaced and no run has been recorded asserting a value on a live posting. Same chain, same commit, as `J 27` -- one reader, six fields, six rows that all sat GAP because nothing joined the code to the census.  **PROMOTED TO COVERED-PROVEN 2026-09-20 BY A LIVE RUN, wave `live-capture`.** `linkedin_job_detail` was called over SEVEN live postings from one `linkedin_search_jobs` pass. **Three of the seven returned `insights.company_insights` with a 45-char heading and 17, 21 and 21 lines;** four returned null and `insights_error` was absent on all seven. **THE FOUR NULLS ARE NOT A FAILURE** -- the reader's own docstring records the panel as absent on four of five committed captures and calls that the normal case, and seven live postings agree. A null is a fact about that employer, never about the capability, which is why several ids were budgeted. See `_audit/2026-09-20-the-live-capture.md` section 3b. |
| 124 | Premium AI company intelligence (headcount, openings, strategic priorities) | a563146 | GAP | -- |
| 125 | "Jobs where you're a top applicant" section | a548337, a1586951 | COVERED-PROVEN | **BANKED 2026-09-20 -- the page was opened for the first time and the tool shipped in the same commit.** `linkedin_premium_job_collection(0)` -> `/jobs/collections/top-applicant`. LIVE: **25 slots, 9 hydrated**, 7 containers, `list_container_seen` True, 25 posting ids all digits, 0 refused by shape, 0 empty-state needles, no refusal, no error. Landing: the PATH survived and the landed path kept its own route word; only a query was appended, so `redirected: True` here means a query and NOT a redirect. **THE COUNT ALONE COULD NOT HAVE BANKED THIS.** `/jobs/search/`, top-applicant and top-choice ALL read 25 -- the signature of one page served three times -- so the id SETS were compared: **disjoint from the control (0 of 25 shared) and 11 of 25 shared with top-choice**, which is three documents, not one. Instrument `scripts/_compare_collection_captures.py`. Two controls stood: the pinned synthetic fixture (8 of 8 fields, 3 of 3 ids) and `/jobs/search/` through the SAME reader (25 slots, 7 hydrated). Tool proof: 4 out-of-range inputs refused including `True` and a string; live payload 15 leaf values, exactly ONE string and it is a module literal, with `linkedin.com`, `/in/`, `http` and `@` all absent. **`hydrated` IS NOT THE ANSWER** -- quoting 9 instead of 25 under-reports this surface by 2.8x. Evidence `_audit/2026-09-20-the-first-firing.md`. |
| 126 | Premium AI job-fit tips | a7474394 | GAP | -- |
| 127 | Read the InMail credit balance | a7474394 | MEASURED-ABSENT `SKILL` | **RE-OPENED 2026-09-20 AND RE-CLOSED THE SAME DAY, BY MEASUREMENT RATHER THAN BY ARGUMENT.** The re-open was right about the instrument and wrong about the conclusion. It said `read_premium_surface` "never looked" -- true, it tallies 16 self-authored needles, none about a balance, a credit or a number, and returns an integer, a boolean, None or a needle name BY CONSTRUCTION. **But "the instrument could not have seen it" is a fact about the instrument, not evidence that the thing is there.** Three instruments have now looked. (1) `9a140a3` s13.3, whole-document RENDERED-TEXT census of `/premium/my-premium/`: `inmail` 0, `credit` 0, on a pass that named `premium` 9, `insight` 3, `applicant` 1, `interview` 1, `recruiter` 1 -- so it could speak. (2) s12.6, `/messaging/compose/`: `credit` 0, `premium` 0, `subject` 0 in text AND in the accessibility tree; `inmail` 4, which is the filter pill. (3) **A CORPUS-WIDE RAW-vs-RENDERED SWEEP OVER ALL 25 CAPTURES, 2026-09-20** -- `balance` 0 raw and 0 rendered EVERYWHERE; `credit` 17-31 RAW on 19 captures and **1 rendered on one capture** (word-bounded, no digit within 40 chars); `inmail` rendered ONLY on compose (4) and messaging (4); and **zero digits adjacent to a credit word on any of the 25**, with the rendered controls non-zero on every capture so no pass was blind. **THE RAW COUNTS ARE THE TRAP THIS ROW EXISTS TO SURVIVE**: `credit` at 30 raw / 0 rendered on the composer is the JS bundle, and a raw census would have argued a balance that is not drawn. MEASURED-ABSENT ON THE CAPTURED CORPUS, which is the honest scope. REOPENER, NAMED: a capture of a Premium surface not in the 25 -- the subscription/manage pages are the untested candidates -- drawing a digit beside an InMail or credit word. Blocker stands: PREMIUM-READER-NOT-BUILT. Agrees with `M M4` and `N 157`, which describe the same capability; see `_audit/2026-09-20-the-first-firing.md` s4 for why the three differ in STATE WORD and not in substance. |

**CORRECTED BY:** `_audit/2026-09-20-the-premium-block.md` -- row 127 above was banked MEASURED-ABSENT on a reading whose instrument carries no needle for a balance, a credit or a number, so it could not have reported one. Re-opened GAP.

**CORRECTED BY:** `_audit/2026-09-20-the-first-firing.md` -- the re-open above is kept because it is right about the instrument, and its CONCLUSION is superseded: three instruments have since looked, including a raw-versus-rendered sweep over all 25 captures with firing controls, and the balance is drawn nowhere. Row 127 returns to MEASURED-ABSENT with a named reopener. **Both corrections are left standing on purpose** -- a row that records only its latest state cannot be audited, and the first correction is the reason the second one had to be a measurement instead of an argument.


**CORRECTED BY:** `_audit/2026-09-05-jobs-tail.md` -- row 127 above cites a
**CORRECTED BY:** `_audit/2026-09-21-what-is-reachable-now.md` -- row `40` moves COVERED-UNFIRED to COVERED-PROVEN on its first live firing, against the bar the THIRD DELTA above pre-registered for it (*"moves to COVERED-PROVEN on one live search"*). Four runs through the shipped `linkedin_search_jobs` and `linkedin_job_detail`, every reading reproducing. The GAP count is UNCHANGED at 56 -- this row left GAP this morning when it was built -- and what moves is `CP 20 -> 21`, `CU 4 -> 3`. **What banked is that the reader REACHES the live field and SELECTS** (1 of 14 distinct postings drew, 13 omitted the key; the same posting read `count_read` on the search card and `relation_only` on the detail page, the asymmetry the reader's design predicted). **What did NOT bank is the COUNT**: every value read was 2, n=1 distinct posting, so the number itself is unproven and the cell says so.
2026-08-31 audit for "the boundary entry and reader are NOT built". Measured
2026-09-05: the boundary entry IS built and is one of the admitted patterns at
that tree; the reader is still not built. Half that sentence is current and half
is stale, which is the shape that survives a careless check -- a reader who
verifies either half concludes the whole is sound.

### I. Recruiter contact and interview prep (6)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 128 | Message the job poster (1st/2nd degree) | a519730 | CU | `linkedin_send_message` exists and gates on a name needle; it "ships expecting to refuse" and has never been fired. Whether it can reach a job poster specifically is unmeasured. **HELD BY `OPERATOR-NAMES-THE-TARGET`** (2026-09-23): a message is a write, so a live proof only at a target the operator names. Until the operator's ruling (b) at 18:15 on 2026-09-23 (`WRITE-CLASS-B`) it was held by both `NO-IRREVERSIBLE-WRITE-IS-FIRED` and `DO-NOT-OPEN-MESSAGING` (the rulings register lists `linkedin_send_message` among the latter's own names); that ruling lifted both for this server. This slice's per-row table has no R/W column, so the hold is cited here, where `scripts/census_completion.py` reads it |
| 129 | InMail the job poster after applying | a508716 | GAP | -- |
| 130 | Read recruiter messages / InMails in the inbox | a519730 | CP | `linkedin_open_messaging`, `linkedin_new_messages`. `server.py:5012` records the lifted refusal: "those people wrote to HIM" |
| 131 | Decide WHO to message and whether it costs a credit | -- | GAP `SKILL` | server: none. Skill `referral_join.py` + `inmail-targeting.md`: free 1st-degree DM vs paid InMail, ranked; "The tool **recommends only**. It never sends" |

### J. AI interview prep, Premium (7) -- RECOVERED 2026-09-03

Rows 132-138 replace a single row that read "Premium interview preparation (question bank,
sample answers, AI feedback)" and was sourced only to the Premium benefits page. The real
product is `a8336402`, "Learning FAQ: Practice with AI interview prep", which the topic
walk never reached. Every row is Premium-gated -- "You must be a Premium member to access
this feature" -- and the operator HAS Premium Career.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 132 | Generate role-specific practice questions from a real job description | a8336402 | EXCLUDED-RULED | "role-specific questions generated from real job descriptions" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` (3.1).** The practice interview is a real-time SPOKEN session that opens as a separate LinkedIn Learning product in its own tab and needs camera and microphone; a browser driver has no voice to supply it, and it is Premium-gated. `a8336402` and `a10133010` fetched directly. REOPENER: a text-only interview mode, or an address that renders the practice product without a session. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 133 | Practice out loud, by voice | a8336402 | EXCLUDED-RULED | "You can practice out loud" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` (3.1).** The practice interview is a real-time SPOKEN session that opens as a separate LinkedIn Learning product in its own tab and needs camera and microphone; a browser driver has no voice to supply it, and it is Premium-gated. `a8336402` and `a10133010` fetched directly. REOPENER: a text-only interview mode, or an address that renders the practice product without a session. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 134 | Practice by reading and typing responses instead | a8336402 | EXCLUDED-RULED | "read and type out your responses" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` (3.1).** The practice interview is a real-time SPOKEN session that opens as a separate LinkedIn Learning product in its own tab and needs camera and microphone; a browser driver has no voice to supply it, and it is Premium-gated. `a8336402` and `a10133010` fetched directly. REOPENER: a text-only interview mode, or an address that renders the practice product without a session. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 135 | Be interviewed by a real-time AI interviewer | a8336402 | EXCLUDED-RULED | "The AI interviewer listens, responds, and evaluates your answers in real time" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` (3.1).** The practice interview is a real-time SPOKEN session that opens as a separate LinkedIn Learning product in its own tab and needs camera and microphone; a browser driver has no voice to supply it, and it is Premium-gated. `a8336402` and `a10133010` fetched directly. REOPENER: a text-only interview mode, or an address that renders the practice product without a session. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 136 | Receive an interview readiness score (low / medium / high) | a8336402 | GAP | **THIS IS THE ONE REACHABLE SLICE OF A RETIRED PRODUCT, AND IT IS NOT REACHABLE YET.** Eleven of `AI-INTERVIEW-PRODUCT`'s fourteen rows retired 2026-09-05 -- the SESSION half, which is a live audio conversation this browser-driven server structurally cannot hold. These three are the READ half the census itself flagged as the realistic slice: *"a past session's readiness score, summary and transcript, IF they are addressed by a url."* **That IF is the whole row and nobody has tested it.** The product opens in LinkedIn Learning in a NEW TAB, on an address outside this server's allowlist, so the question is not whether a parser could read a score -- it is whether a past session's results have a stable address at all. **NEXT ARTIFACT, and it is a MEASURE not a ruling:** determine whether a completed session leaves a durable addressable result page. **PRECONDITION NOBODY CAN DISCHARGE CHEAPLY: it requires a completed session to exist**, and completing one means holding a live audio interview -- so this is unmeasurable on an account that has never run one, and running one is not a read. The blocker is filed DECIDE-RETIRE at cost 1; the honest reading is that these three are blocked on a precondition, not on a decision. "interview readiness score"  **THE STANDING REASON ABOVE IS REFUTED, MEASURED 2026-09-20 BY A LIVE PAGE LOAD, wave `live-capture`. THE ROW STAYS GAP AND ITS BLOCKER CHANGES.** The precondition filed here -- that answering needs a completed audio session, so only the operator can discharge it -- was a TECHNICAL UNKNOWN WEARING A PERMISSION COSTUME. It needed one page load and nothing from him. What the load found: (1) **the member-side product IS offered to this account** -- `/premium/my-premium/` draws exactly one role-play anchor, a 2-word 16-char label whose first word is `start`, sitting 5 sections deep in product content, not chrome; (2) **the address is `www.linkedin.com/learning/role-play/scenarios/new/` -- SAME ORIGIN and carrying NO member segment**, so this row's claim that it sits on an address outside reach is half wrong: it is refused today but it is an ordinary allowlist candidate, not a cross-domain impossibility; (3) **the one drawn route is a CREATE route**, the same autosave class as `/article/newsletter/new/` which this repo already refuses; (4) **across all six captured surfaces, learning/role-play route shapes drawn = 3, of which results/history/transcript-shaped = 0** -- LinkedIn offers a route to START a session and none to READ one back; (5) LinkedIn's own lix key **`learning-job-interview-prep-role-play-experiment` joins job-interview-prep and role-play as ONE product** and reads treatment `control` on this account, while 7 of the 8 interview flags on the page are `hiring-*` RECRUITER-side and are not this row. **NEXT ARTIFACT, and it needs no ruling and no operator:** read `/learning/role-play/scenarios/` -- the LISTING, without the `/new/` segment, a different address never opened. One allowlist hypothesis, one page load. See `_audit/2026-09-20-the-live-capture.md` section 4.  **AND THE LISTING WAS THEN ADMITTED AND OPENED, same day, same wave.** The refusal that had kept it shut was OURS, not LinkedIn's, so `^https://www\.linkedin\.com/learning/role-play/scenarios/?$` was added to `_ALLOWED_URL_PATTERNS` (35 -> 36, digest `6577a7bc8a32d7b8` -> `85e821d1af9060f3`) with the argument beside it, bounded and proved bounded over ten spellings **10 of 10 as intended -- the drawn `/new/` create route stays REFUSED because the pattern takes no sub-path.** **THE PAGE SERVES:** landed as requested, no redirect, no login wall, no error copy, with a known-served control read first in the same session. **AND IT DRAWS NOTHING:** 673538 bytes, 1135 chars of rendered text, 24 anchors, 26 buttons, 6 headings, and **`<main>` holds 17 characters -- two words, 1% of the page** -- byte-identical across three samples over 25 seconds, so not a hydration race; and **15 empty-state and error needles all silent**, so the page does not even report that there is nothing. **STILL GAP, and the blocker is now measured rather than assumed:** not the operator's knowledge, not the address, but that this account renders no session content on the surface. The leading explanation is the `control` treatment measured above -- **an INFERENCE, named as one**; a second possibility, that the product mounts only for a member who has a session, is not excluded. **NEXT ARTIFACT: re-run the one read when that flag's treatment changes** -- one command, address already admitted, nothing needed from him. See `_audit/2026-09-20-the-live-capture.md` section 11. |
| 137 | Receive a summary of strengths and areas to improve | a8336402 | GAP | **THIS IS THE ONE REACHABLE SLICE OF A RETIRED PRODUCT, AND IT IS NOT REACHABLE YET.** Eleven of `AI-INTERVIEW-PRODUCT`'s fourteen rows retired 2026-09-05 -- the SESSION half, which is a live audio conversation this browser-driven server structurally cannot hold. These three are the READ half the census itself flagged as the realistic slice: *"a past session's readiness score, summary and transcript, IF they are addressed by a url."* **That IF is the whole row and nobody has tested it.** The product opens in LinkedIn Learning in a NEW TAB, on an address outside this server's allowlist, so the question is not whether a parser could read a score -- it is whether a past session's results have a stable address at all. **NEXT ARTIFACT, and it is a MEASURE not a ruling:** determine whether a completed session leaves a durable addressable result page. **PRECONDITION NOBODY CAN DISCHARGE CHEAPLY: it requires a completed session to exist**, and completing one means holding a live audio interview -- so this is unmeasurable on an account that has never run one, and running one is not a read. The blocker is filed DECIDE-RETIRE at cost 1; the honest reading is that these three are blocked on a precondition, not on a decision. "a summary of your strengths and areas to improve"  **THE STANDING REASON ABOVE IS REFUTED, MEASURED 2026-09-20 BY A LIVE PAGE LOAD, wave `live-capture`. THE ROW STAYS GAP AND ITS BLOCKER CHANGES.** The precondition filed here -- that answering needs a completed audio session, so only the operator can discharge it -- was a TECHNICAL UNKNOWN WEARING A PERMISSION COSTUME. It needed one page load and nothing from him. What the load found: (1) **the member-side product IS offered to this account** -- `/premium/my-premium/` draws exactly one role-play anchor, a 2-word 16-char label whose first word is `start`, sitting 5 sections deep in product content, not chrome; (2) **the address is `www.linkedin.com/learning/role-play/scenarios/new/` -- SAME ORIGIN and carrying NO member segment**, so this row's claim that it sits on an address outside reach is half wrong: it is refused today but it is an ordinary allowlist candidate, not a cross-domain impossibility; (3) **the one drawn route is a CREATE route**, the same autosave class as `/article/newsletter/new/` which this repo already refuses; (4) **across all six captured surfaces, learning/role-play route shapes drawn = 3, of which results/history/transcript-shaped = 0** -- LinkedIn offers a route to START a session and none to READ one back; (5) LinkedIn's own lix key **`learning-job-interview-prep-role-play-experiment` joins job-interview-prep and role-play as ONE product** and reads treatment `control` on this account, while 7 of the 8 interview flags on the page are `hiring-*` RECRUITER-side and are not this row. **NEXT ARTIFACT, and it needs no ruling and no operator:** read `/learning/role-play/scenarios/` -- the LISTING, without the `/new/` segment, a different address never opened. One allowlist hypothesis, one page load. See `_audit/2026-09-20-the-live-capture.md` section 4.  **AND THE LISTING WAS THEN ADMITTED AND OPENED, same day, same wave.** The refusal that had kept it shut was OURS, not LinkedIn's, so `^https://www\.linkedin\.com/learning/role-play/scenarios/?$` was added to `_ALLOWED_URL_PATTERNS` (35 -> 36, digest `6577a7bc8a32d7b8` -> `85e821d1af9060f3`) with the argument beside it, bounded and proved bounded over ten spellings **10 of 10 as intended -- the drawn `/new/` create route stays REFUSED because the pattern takes no sub-path.** **THE PAGE SERVES:** landed as requested, no redirect, no login wall, no error copy, with a known-served control read first in the same session. **AND IT DRAWS NOTHING:** 673538 bytes, 1135 chars of rendered text, 24 anchors, 26 buttons, 6 headings, and **`<main>` holds 17 characters -- two words, 1% of the page** -- byte-identical across three samples over 25 seconds, so not a hydration race; and **15 empty-state and error needles all silent**, so the page does not even report that there is nothing. **STILL GAP, and the blocker is now measured rather than assumed:** not the operator's knowledge, not the address, but that this account renders no session content on the surface. The leading explanation is the `control` treatment measured above -- **an INFERENCE, named as one**; a second possibility, that the product mounts only for a member who has a session, is not excluded. **NEXT ARTIFACT: re-run the one read when that flag's treatment changes** -- one command, address already admitted, nothing needed from him. See `_audit/2026-09-20-the-live-capture.md` section 11. |
| 138 | Receive a transcript of your responses with worked improvements | a8336402 | GAP | **THIS IS THE ONE REACHABLE SLICE OF A RETIRED PRODUCT, AND IT IS NOT REACHABLE YET.** Eleven of `AI-INTERVIEW-PRODUCT`'s fourteen rows retired 2026-09-05 -- the SESSION half, which is a live audio conversation this browser-driven server structurally cannot hold. These three are the READ half the census itself flagged as the realistic slice: *"a past session's readiness score, summary and transcript, IF they are addressed by a url."* **That IF is the whole row and nobody has tested it.** The product opens in LinkedIn Learning in a NEW TAB, on an address outside this server's allowlist, so the question is not whether a parser could read a score -- it is whether a past session's results have a stable address at all. **NEXT ARTIFACT, and it is a MEASURE not a ruling:** determine whether a completed session leaves a durable addressable result page. **PRECONDITION NOBODY CAN DISCHARGE CHEAPLY: it requires a completed session to exist**, and completing one means holding a live audio interview -- so this is unmeasurable on an account that has never run one, and running one is not a read. The blocker is filed DECIDE-RETIRE at cost 1; the honest reading is that these three are blocked on a precondition, not on a decision. "a transcript of your responses with examples on how to improve"  **THE STANDING REASON ABOVE IS REFUTED, MEASURED 2026-09-20 BY A LIVE PAGE LOAD, wave `live-capture`. THE ROW STAYS GAP AND ITS BLOCKER CHANGES.** The precondition filed here -- that answering needs a completed audio session, so only the operator can discharge it -- was a TECHNICAL UNKNOWN WEARING A PERMISSION COSTUME. It needed one page load and nothing from him. What the load found: (1) **the member-side product IS offered to this account** -- `/premium/my-premium/` draws exactly one role-play anchor, a 2-word 16-char label whose first word is `start`, sitting 5 sections deep in product content, not chrome; (2) **the address is `www.linkedin.com/learning/role-play/scenarios/new/` -- SAME ORIGIN and carrying NO member segment**, so this row's claim that it sits on an address outside reach is half wrong: it is refused today but it is an ordinary allowlist candidate, not a cross-domain impossibility; (3) **the one drawn route is a CREATE route**, the same autosave class as `/article/newsletter/new/` which this repo already refuses; (4) **across all six captured surfaces, learning/role-play route shapes drawn = 3, of which results/history/transcript-shaped = 0** -- LinkedIn offers a route to START a session and none to READ one back; (5) LinkedIn's own lix key **`learning-job-interview-prep-role-play-experiment` joins job-interview-prep and role-play as ONE product** and reads treatment `control` on this account, while 7 of the 8 interview flags on the page are `hiring-*` RECRUITER-side and are not this row. **NEXT ARTIFACT, and it needs no ruling and no operator:** read `/learning/role-play/scenarios/` -- the LISTING, without the `/new/` segment, a different address never opened. One allowlist hypothesis, one page load. See `_audit/2026-09-20-the-live-capture.md` section 4.  **AND THE LISTING WAS THEN ADMITTED AND OPENED, same day, same wave.** The refusal that had kept it shut was OURS, not LinkedIn's, so `^https://www\.linkedin\.com/learning/role-play/scenarios/?$` was added to `_ALLOWED_URL_PATTERNS` (35 -> 36, digest `6577a7bc8a32d7b8` -> `85e821d1af9060f3`) with the argument beside it, bounded and proved bounded over ten spellings **10 of 10 as intended -- the drawn `/new/` create route stays REFUSED because the pattern takes no sub-path.** **THE PAGE SERVES:** landed as requested, no redirect, no login wall, no error copy, with a known-served control read first in the same session. **AND IT DRAWS NOTHING:** 673538 bytes, 1135 chars of rendered text, 24 anchors, 26 buttons, 6 headings, and **`<main>` holds 17 characters -- two words, 1% of the page** -- byte-identical across three samples over 25 seconds, so not a hydration race; and **15 empty-state and error needles all silent**, so the page does not even report that there is nothing. **STILL GAP, and the blocker is now measured rather than assumed:** not the operator's knowledge, not the address, but that this account renders no session content on the surface. The leading explanation is the `control` treatment measured above -- **an INFERENCE, named as one**; a second possibility, that the product mounts only for a member who has a session, is not excluded. **NEXT ARTIFACT: re-run the one read when that flag's treatment changes** -- one command, address already admitted, nothing needed from him. See `_audit/2026-09-20-the-live-capture.md` section 11. |

### K. AI interviews as a hiring stage, candidate side (7) -- RECOVERED 2026-09-03

An entire product surface the first census had **zero** rows for. `a10376002`, "AI
interviews on LinkedIn": a hirer invites an applicant to an audio or video interview
conducted by an AI. **Not Premium-gated.** This is a stage of applying, squarely in this
slice, and no walk of the jobs topic tree surfaced it.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 139 | Take a practice AI interview first, unlimited repeats | a10376002 | EXCLUDED-RULED | "You can take the practice interview as many times as you'd like" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` (3.1).** The practice interview is a real-time SPOKEN session that opens as a separate LinkedIn Learning product in its own tab and needs camera and microphone; a browser driver has no voice to supply it, and it is Premium-gated. `a8336402` and `a10133010` fetched directly. REOPENER: a text-only interview mode, or an address that renders the practice product without a session. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 140 | Complete a hirer's voice-based or video-based AI screening interview | a10376002 | EXCLUDED-RULED | "complete the hirer's voice-based or video-based AI screening interview" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` live application (3.1).** A hirer's live AI screening is a participation decision with a career consequence -- 140 submits irreversibly, and 142 is a decline LinkedIn documents as carrying no automatic disqualification -- so an automated choice would be making a career call, and no gate here can price it. REOPENER: nothing measurable; only the operator ruling that the decision is his to delegate. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 141 | End an interview in progress | a10376002 | EXCLUDED-RULED | "To end the interview, click End interview" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` live application (3.1).** A hirer's live AI screening is a participation decision with a career consequence -- 140 submits irreversibly, and 142 is a decline LinkedIn documents as carrying no automatic disqualification -- so an automated choice would be making a career call, and no gate here can price it. REOPENER: nothing measurable; only the operator ruling that the decision is his to delegate. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 142 | Decline to participate, without automatic disqualification | a10376002 | EXCLUDED-RULED | "If you decide not to participate, you will not be automatically disqualified" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` live application (3.1).** A hirer's live AI screening is a participation decision with a career consequence -- 140 submits irreversibly, and 142 is a decline LinkedIn documents as carrying no automatic disqualification -- so an automated choice would be making a career call, and no gate here can price it. REOPENER: nothing measurable; only the operator ruling that the decision is his to delegate. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 143 | Reply to the invitation with feedback on the interview experience | a10376002 | EXCLUDED-RULED | "contact the hirer with additional information or feedback on the interview experience by replying to the initial interview invitation" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` hirer messages (3.1).** The route is, in LinkedIn's own words, contacting the hirer, and the content is a personal statement about his own experience or his own needs -- the class the shipped `auto_accept_or_auto_reply` prohibition already names. REOPENER: nothing that keeps the shape. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 144 | Request your rating, summaries, transcript or recording | a10376002 | EXCLUDED-RULED | "You can request access to your rating and summaries, transcript, or recording by contacting the hirer" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` hirer messages (3.1).** `a10376002`, fetched this pass: access to your rating and summaries, transcript or recording is requested BY CONTACTING THE HIRER. The route is a message to a person, not a page, and that is what the retirement rests on -- the R/W column cannot distinguish this row either way. REOPENER: a capture showing a self-serve results page, and then it reopens with J 136-138. See `_audit/2026-09-05-decide-retire-rulings.md` |
| 145 | Request an accommodation | a10376002 | EXCLUDED-RULED | "contact the hirer directly to request an accommodation" **RETIRED 2026-09-05, `AI-INTERVIEW-PRODUCT` hirer messages (3.1).** The route is, in LinkedIn's own words, contacting the hirer, and the content is a personal statement about his own experience or his own needs -- the class the shipped `auto_accept_or_auto_reply` prohibition already names. REOPENER: nothing that keeps the shape. See `_audit/2026-09-05-decide-retire-rulings.md` |

### L. Resume tips and Writing Assistant, Premium (5) -- RECOVERED 2026-09-03

Rows 146-149 replace a single row that read "Premium AI resume builder / resume review"
and **misnamed the product**. `a6813101` documents resume TIPS, and states the limit
plainly: "Resume Tips is only able to provide feedback on an **existing uploaded resume**"
-- there is no builder. Desktop and English only.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 146 | Upload a resume for analysis against one specific job posting | a6813101 | GAP | reached from the Jobs tab, "Tailor my resume to this job" |
| 147 | Receive personalized insights on the job and how to enhance the resume | a6813101 | GAP | "personalized insights about the job" |
| 148 | Refine sections of the resume with suggested language | a6813101 | GAP | "refine sections of your resume with suggested language" |
| 149 | Export the result, or attach it to a LinkedIn application | a6813101 | GAP | "export it or attach it to a job application that you can submit through LinkedIn" |
| 150 | Send an enhanced message to a recruiter using Writing Assistant | a7146402 | GAP | Premium, "select LinkedIn Premium subscribers in the United States" |

### M. Late addition to job search (1)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 151 | Filter a job search by MULTIPLE simultaneous locations | a523131 | COVERED-PROVEN | **FIRED AND BANKED 2026-09-20.** The multi-location fan-out was fired live by `scripts/_probe_unfired_job_search_filters.py` with two cities. **2 searches reported, 12 rows returned, 12 DISTINCT job ids, all 12 carrying `found_in`, attributed to 2 distinct places.** So the second-load fan-out runs, merges and attributes, exactly as the build claimed. WHAT THIS STILL DOES NOT REACH, unchanged: LinkedIn's own CROSS-LOCATION RANKING. No request names two places, so this is per-city windows merged. NOTE ON THE OLD EVIDENCE: the cited `_audit/_scratch/_progress-job-search-params.md` is GITIGNORED and absent from a clone. **THE PRIOR SOURCE-TRACE, KEPT BECAUSE IT IS WHY THE ROW EXISTED:** **BANKED 2026-09-20. `locations` shipped on `linkedin_search_jobs` as a SECOND-LOAD capability, which is what the prior wave's own measurement said it had to be.** Semicolon-separated places, one `/jobs/search/` load each, merged round-robin and de-duplicated by `job_id`; every row carries `found_in` and `searches` reports what each place gave. Chain: `jobfilter.locations_plan` (the verdict), `jobfilter.merge_location_reads` (the merge), `linkedin_search_jobs(locations=...)` (the tool), `server._search_url` (the ONE place a location reaches a url). **NO BOUNDARY COST: no new address, no new injected script, no new evaluate call site, no new admission** -- every load is the single-location search already on the read allowlist, and the 1172-test boundary and inventory set passes untouched. **UNFIRED, NOT PROVEN, and I looked for the flattering answer:** no browser session was opened this wave, so nothing here has seen the fan-out return a live payload. The offline guards are `tests/test_job_search_multiple_locations.py` (27 tests), of which the load-bearing one is `test_a_fan_out_builds_one_url_per_place_and_never_joins_them` -- it asserts N navigations and that NO url spells two places into one request, and its control `test_the_url_guard_catches_both_spellings_measured_wrong` runs the same predicate over the two literal urls measured wrong on 2026-09-05 and requires it to catch both. **WHAT IT DOES NOT REACH, stated rather than glossed:** LinkedIn's own CROSS-LOCATION RANKING. No request names two places, so this is several per-city windows merged, and postings a genuine one-request multi-location search would have ranked between the cities were never in any page this read. That capability still needs LinkedIn's numeric place ids, which a posting does not carry. `jobfilter.MAX_LOCATIONS = 5` is a cost budget on this server and is declared as such, not a measured LinkedIn limit. **THE PRIOR WAVE'S FINDING, QUOTED BECAUSE IT IS THE REASON THIS IS LOADS AND NOT A PARAMETER -- it is a citation, not a live verdict; the row's state is the cell above, COVERED-UNFIRED.** That wave wrote *"stays GAP, but it is answered in the negative with evidence rather than unmeasured"* -- measured 2026-09-05, re-read 2026-09-19. Both plausible spellings are WRONG, not untried: with city A alone returning 7 ids and city B alone 7 ids sharing 2, `location=A%2C%20B` is KEPT by LinkedIn and returns 7 ids drawn from **0 of A-only and 0 of B-only** -- it geocodes somewhere else entirely -- while `location=A&location=B` is STRIPPED and serves the LAST city alone (0 of A-only, 5 of B-only). The tool's own docstring predicted exactly this: *"a guessed encoding does not fail loudly -- it silently searches somewhere else."* **RE-COSTED: this is NOT parameter work.** Reaching two cities honestly needs LinkedIn's numeric place ids, which a posting does not carry, so it is a SECOND-LOAD capability. The ledger prices `JOB-SEARCH-PARAMS` at cost 1 for all six rows; five of those are shipped and this one is not a parameter at all. Evidence `_audit/_scratch/_progress-job-search-params.md` s8. **That re-costing is what was built: the second load, and up to five of them per call.** See `_audit/2026-09-20-job-search-params-built.md` |

---

## 2. WHAT EACH GAP WOULD TAKE

Shapes, not designs. `R`/`W` is read or write. `REV` is whether the effect can be undone.

| rows | gap | shape | R/W | REV |
|---|---|---|---|---|
| 9-14 | six named search filters | pure parameter work on `linkedin_search_jobs`: six more `_WORKPLACE`-style dicts and six more `params.append`. `f_AL` (Easy Apply), `f_C` (company id), `f_JT` (job type), `f_EA`/under-10, `f_JIYN` (in network), `f_FCE`. The company filter needs a slug-to-numeric-id resolver, which the repo already names as an open problem for `follow_company` | R | REV (a search changes nothing but recent-search history) |
| 15-16 | All-filters panel, suggested filters | needs the panel rendered and its controls enumerated, or the query parameters read off a filtered url. A capture, then parameters | R | REV |
| 17 | search from current location | needs browser geolocation permission. Out of shape for this design | R | REV |
| 18-19 | recent searches read / clear | ~~a new read surface (`/jobs/search-history/` or equivalent) on the allowlist~~ **THAT HALF IS EXPIRED, measured 2026-09-23 (lane L3): the recent-searches list is drawn on the jobs home `/jobs/jam/`, admitted 2026-09-20, and row 18 is built on it (`linkedin_recent_job_searches`); `/jobs/search-history/` is still refused and nothing shows it drawing the list. The clear half is untouched, and its control is drawn on the same page.** the clear is a destructive verb and `"delete"`/`"remove"` are on the mutation-verb denylist | R + W | clear is NOT reversible |
| 24-30 | posting-side insight panels (responsiveness detail, why-seeing, promoted label, verification badge, Skills Match, report-closed) | all live on the posting `linkedin_job_detail` already loads. Each is a parser addition against a capture, at ZERO extra page load -- the cheapest block on this list. `report a job as closed` is the exception: a write behind a menu | R (28, 30 are W) | REV for reads; 28 not reversible |
| 31-36, 41 | all alert writes | a new write surface. ~~`/jobs/alerts` is not on the read allowlist~~ **THAT HALF IS EXPIRED, measured 2026-09-21: `^https://www\.linkedin\.com/jobs/alerts/?$` was admitted on 2026-09-05 by `61e3237` ("the job-alerts READ half"), sixteen days after this cell was written, and `readonly.is_read_url` returns True for it at HEAD. The READ half of this block is no longer boundary-blocked; the WRITE half below is untouched and no row moves.** Alert editing is a modal. Needs: a capture of the alerts manager, an allowlist entry, a `WriteSpec` per verb, and an aiming rule (which alert). `"create"`, `"delete"`, `"edit"`, `"subscribe"` are ALL on the mutation-verb denylist, so four denylist exemptions | W | create/edit REV; **delete NOT reversible** (the alert's history is gone) |
| 37-40 | alert results, proximity | **already served by the skill.** Building a server path would duplicate it and lose the proximity field, which no page carries | R | REV |
| 42 | job collections | a new read surface plus a parser | R | REV |
| 54-56 | tracker stage change, notes, date filter | the tracker is already read; these are row-level controls behind an overflow menu. Needs a capture of a POPULATED tracker row -- which the repo has never had, because the Applied tab reads zero. `"update"`, `"set"`, `"add"` are on the mutation-verb denylist | W | REV |
| 57 | connections for a tracked job | **served by the skill**, from a better source | R | REV |
| 68 | draft save / resume | the Easy Apply modal's own control; blocked behind the same multi-step gate as row 60 | W | REV (a draft can be discarded) |
| 70-73 | resume upload, list, delete, download, which-was-submitted | needs the Job Application Settings surface on the allowlist and a file-input driver, which this server has never had. `"upload"`, `"delete"` are on the mutation-verb denylist | R + W | upload/download REV; **delete NOT reversible** |
| 78-83 | Premium apply extras (cover-letter AI, Top Choice, limits, self-ID) | each is a distinct surface; Top Choice spends a non-refunding monthly credit | W | Top Choice **NOT reversible** (credit does not roll back) |
| 85-86 | undo a dismissal, "I'm interested" | posting-card and company-page controls; both need a capture | W | REV (both document an Undo) |
| 92-100 | every job-preference FIELD, Minimum Pay, recruiter visibility | all live behind the same modal as rows 89-91. **One capture of the Open To Work editor unlocks this entire block.** The repo already nominates the safe first click: `server.py:5058` -- "a `Show details` control whose action list holds one Navigate and no ServerRequest" | R + W | REV, EXCEPT the audience change: `writes.py` calls it "IRREVERSIBLE IN AUDIENCE" -- switching to All members draws a frame his current employer can see, and un-drawing it does not un-show it |
| 106-114 | company and school Page tabs, Premium insights | a company Page url is already returned by `job_detail`. ~~Needs `/company/<slug>/` and its tabs on the read allowlist~~ **HALF EXPIRED, measured 2026-09-21: the Page ROOT `^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_]{1,100}/?$` was admitted 2026-09-20 by `952af32`, and `is_read_url` returns True for it at HEAD. The pattern takes NO sub-path, so every TAB address (`/about/`, `/jobs/`, `/people/`, `/life/`, `/products/`, `/insights/`) is still REFUSED -- verified one by one. Row 110 is the one affected: the Home tab IS the root, so 110 alone is now boundary-clear and needs only a parser. The other eight stay address-blocked and no row moves.** Plus a parser per tab. Largest single block of pure-read GAPs on this census (9 rows) | R | REV |
| 116-126 | "How you match", applicant insights, Premium company insights, top-applicant, AI tips | ~~116-120 and 121-122 render **on the posting page `job_detail` already loads**, for a Premium account, which this operator has. Parser additions at zero extra page load.~~ **HALF EXPIRED, and the expired half was measured before this cell was last read: Amendment A13 of the 2026-09-03 gap-blockers ledger found 116-120's Show match details to be an anchor into the AI guide overlay `/preload/guideOverlay/` -- a generation, refused by the boundary -- and How you match reads 0 on the settled posting. 121-122 do render on the posting and are read there. Re-addressed row by row in `_audit/_census/jobs-directions.tsv` (lane L3, 2026-09-23).** 123-126 need other surfaces | R | REV |
| 127 | InMail balance | `/premium/my-premium/` is already ruled admitted as a census key; the boundary entry and the reader were deliberately not built. Smallest unbuilt read on this list | R | REV |
| 129 | InMail the job poster | needs both a compose surface for InMail (distinct from the message composer) and a verification. `send_message` cannot report "sent" today | W | **NOT reversible**, and it spends a credit |
| 132-138 | Premium AI interview prep | a whole separate product that opens in LinkedIn Learning in a new tab. Voice capture, a real-time conversational agent, and a scored transcript. **Structurally out of shape for this server**: it is not a page to read or a control to click, it is a live audio session. The realistic reachable slice is the READ side -- a past session's readiness score, summary and transcript, if they are addressed by a url | R (results) + W (the session) | REV (practice leaves no mark on any application) |
| 139-145 | AI interviews as a hiring stage | same shape and higher stakes: rows 140-142 are decisions on a live application. **Row 142 is the one to notice** -- declining is documented as safe ("you will not be automatically disqualified"), so an automated participation decision would be making a career call, not a mechanical one. Rows 143-145 are messages to a human hirer | R + W | 140 **NOT reversible** (a completed screening interview is submitted); 141-145 REV |
| 146-149 | Resume tips | reached from the Jobs tab by a sparkle control, desktop only. Needs the surface captured and a file input this server has never had (same blocker as row 70). Feedback only -- **it cannot generate a resume** | R + W | REV (it produces a file; nothing is sent) |
| 150 | Writing Assistant recruiter message | US-only Premium overlay on a compose surface. Blocked behind the same wall as `send_message`: nothing here can verify a send | W | **NOT reversible** |
| 151 | multi-location job search | **BUILT 2026-09-20 and the costing here was wrong.** "Parameter work" was true of the ARGUMENT and false of the URL: both spellings a second location might have taken were measured WRONG on 2026-09-05, so it shipped as `locations` -- one page load per place, merged. No new surface was right; no new BOUNDARY either | R | REV |

**The cheapest real wins, in order.** (a) Rows 9-14 and 4-7: search filters are parameter
work with no new surface, no capture and no permission -- six filters for the price of six
dicts. (b) Rows 116-122 and 24-30: everything that renders on a posting page
`linkedin_job_detail` **already loads**, at zero extra page loads and zero new permissions
-- 13 read capabilities behind parser work alone. (c) Row 127: one boundary entry and one
reader. (d) Rows 92-100: one modal capture unlocks nine preference fields.

**The one to weigh hardest.** Row 60 (multi-step Easy Apply) is the single capability whose
absence most limits the operator's actual job search, and it is the one whose gate should
NOT be relaxed casually: LinkedIn's own Help Center now confirms (a512388) that a submitted
application **cannot be withdrawn**. Building step-filling means building a machine that
performs an act with no undo, on screens nobody here has watched finish.

---

## 3. AREAS WALKED, AND THE HOLES IN THE DENOMINATOR

**Walked, with page-level citations:** job search and its documented filters; boolean
syntax; job alerts (create/edit/delete/frequency/channel/limits/company alerts/collections
digest); saved jobs and the 5-stage job tracker; Easy Apply end to end (steps, resumes,
screening questions, cover letter, limits); off-site apply and Apply-with-LinkedIn;
application status; withdrawing; archiving; job preferences and Open to Work; recruiter
visibility and career-interest privacy; company and school Page tabs; Premium Page Insights;
"How you match" and Skills Match; applicant insights; Top Applicant and Top Choice; Premium
Career benefits; job collections and recommendations.

**Reached only weakly, and these are holes rather than zeros:**

1. **Interview preparation. RESOLVED 2026-09-03, and it was the worst hole on the list.**
   The first pass had 2 rows resting on the Premium benefits page. LinkedIn documents two
   separate products the topic walk never surfaced: `a8336402` (Premium AI interview prep,
   7 capabilities) and `a10376002` (hirer-invited AI interviews, 7 capabilities, **not**
   Premium-gated). Plus `a6813101` turned "AI resume builder" into 4 resume-TIPS rows and
   showed the original phrasing was wrong -- there is no builder. **2 rows became 18.**
2. **Mobile-only job capabilities.** The walk was desktop-shaped. Several pages name mobile
   paths (alert defaults, Skills Match notifications); a mobile-only capability with no
   desktop equivalent would not have surfaced.
3. **The job-search-specific boolean page is dead.** `a507571` 404s under both URL forms.
   Row 2 rests on the GENERAL search boolean page (a524335); whether job search restricts
   operators to the description field is unconfirmed.
4. **Four filter chips. CHECKED AND CONFIRMED EMPTY 2026-09-03.** Title, Industry, Job
   function and Benefits are widely reported as job-search filters by third parties. Two
   article-index queries (`job search filter industry job function title`, `benefits filter
   job search`) returned `a507441` as the only candidate, and that page -- fetched four
   times now -- names none of them. **LinkedIn's own article index has no page documenting
   these as job-search filters.** They stay out of the denominator, and now with a reason
   rather than an absence. If they exist, LinkedIn does not document them.
   The same queries DID recover one real filter capability the topic walk missed:
   `a523131`, multiple simultaneous locations in one search -- now row 151. That page also
   **confirms the negative** on location radius: it documents adding locations by name and
   no distance control, which is the second page to agree.
5. **Per-job "Not interested". CHECKED AND CONFIRMED EMPTY 2026-09-03.** Two further
   article-index queries (`not interested job`, `hide job recommendation dismiss`) returned
   nothing about dismissing a job -- the `dismiss` query returns only PROFILE-recommendation
   articles (a542701 "Accept or dismiss recommendations" is about testimonials, not jobs).
   **LinkedIn does not document a per-job "Not interested" action anywhere in its own
   index.** Row 84 stays sourced to this repo's own fixtures, which show a `Dismiss` control
   on job cards -- product evidence with no documentation behind it, now confirmed twice.
6. **Sort is contested.** The page literally titled "Filter and sort job search results"
   (a507441) does not contain the word "sort" in its retrievable body across three fetches.
   Sort is sourced to a6889044, which frames "Most recent / Most relevant" as still being
   developed. The server implements `sortBy=DD` regardless, so row 7 is covered either way.
7. **Not walked at all:** the hirer/recruiter side of jobs (posting a job, LinkedIn
   Recruiter, Apply Connect), LinkedIn Learning course recommendations attached to jobs,
   and Services Marketplace. All are out of this slice's scope by design, not oversight.

---

## 4. THE CAPABILITIES THE SKILL SERVES AND THE SERVER DOES NOT

Seven numbered census rows, plus two per-card fields that are not separate capability rows.

For the operator's real question -- "can I do it?" -- these are available today, through
`linkedin-jobs` reading Gmail, with no LinkedIn session at all:

| row | capability |
|---|---|
| 37 | enumerate the live job alerts (query, geo, stable `savedSearchId`) |
| 38 | read every job an alert delivered, ~6 cards x 5 emails/day |
| 39 | read LinkedIn's job recommendations |
| 40 | **per-job network proximity** -- "2 connections", "1 company alum" |
| 57 | which connections to reach out to for a given company |
| 127 | the InMail credit ledger and its economics |
| 131 | who to message, and whether it is free or costs a credit |
| -- | Easy-Apply eligibility per card (`Apply with resume & profile` literal) |
| -- | hiring-velocity and growth badges (`This company is actively hiring`, `Fast growing`) |

Row 40 is the one that matters most and it is not a server GAP that could be closed: it is
an email-only field. `SKILL.md:13` -- "No scraper and no job-board API can produce that
field. Rank on it."

Two boundaries worth stating. The skill **reads** alerts and cannot **change** them:
`alert-tuning.md` specifies the exact settings to change and says "It is an operator action
at linkedin.com/jobs/alerts -- specify it, do not attempt it." And the skill **recommends**
outreach and never sends: "The tool recommends only. It never sends, drafts-and-sends, or
touches LinkedIn. He sends by hand in the browser. Do not add sending."

---

## 5. THREE THINGS THIS CENSUS FOUND THAT THE REPO SHOULD FIX

1. **Retire the "real LinkedIn feature" claim about withdraw** (`server.py:5081`) and stop
   offering the "It might" reading in `writes.py`'s `reversibility_procedure`. LinkedIn's
   own help page a512388 settles it: there is no withdraw, and it never needed an
   application to exist to find that out. The irreversibility argument gets STRONGER.
2. **`apply_job` has never submitted anything.** Any prose that reads as "apply works"
   should say what the audits say: it fired once, the gate held, and the Applied tab still
   reads zero. `server.py`'s docstring is honest about the gate; the risk is in summaries
   that flatten "PERFORMS" into "has applied".
3. **`unsave_job` WAS the only PERFORMABLE write with no live fire at all -- RESOLVED 2026-09-19, it fired and was verified** (`_audit/2026-09-19-tier1-fires.md`). The paragraph below is kept as written because its reasoning is what made the fire safe to choose, and it was accurate for twenty days. Six separate
   audit entries record it not being fired. It is one supervised call from being proven,
   and it is the cheapest and most reversible write on the whole surface -- `save_job`
   restores its own effect exactly.

---

## 6. THE SECOND PASS -- INSTRUMENT, DELTA, AND WHAT IT CONFIRMED

**The instrument.** `https://www.linkedin.com/help/linkedin/search?q=<terms>`. I verified it
myself before using it: `?q=interview%20preparation` returns a real 10-row article index.
It queries LinkedIn's OWN index, so unlike an external search engine it cannot miss an
article nobody crawled -- and unlike the topic tree, it cannot render `0 articles` for a
product that exists. **That difference is the entire finding**: the two products in sections
J and K are live, member-facing and documented, and a topic walk surfaced neither.

**Before / after.**

| | 133-row pass | 151-row pass | delta |
|---|---|---|---|
| numbered rows | 133 | 151 | **+18** |
| denominator | 132 | 150 | **+18** |
| COVERED-PROVEN | 21 | 21 | 0 |
| COVERED-UNFIRED | 7 | 7 | 0 |
| EXCLUDED-RULED | 23 | 23 | 0 |
| GAP | 81 | 99 | **+18** |
| unreachable share | 78.8% | 81.3% | +2.5pp |

**Every one of the 18 is a GAP. The covered set did not move by a single row.** The
recovery found no hidden coverage; it found the hole was bigger than a topic walk could
see -- the same result the sibling slice reported.

**Queries run (10), and what each settled.**

| query | result |
|---|---|
| `interview preparation` | **+6** -- a8336402, a10376002, a10133010 all new |
| `interview prep questions practice answers` | corroborated a8336402 and a10376002 |
| `not interested job` | **CONFIRMED EMPTY** -- nothing about dismissing a job |
| `hide job recommendation dismiss` | **CONFIRMED EMPTY** -- profile recommendations only |
| `job search filter industry job function title` | **CONFIRMED EMPTY** for the four chips; recovered a523131 |
| `benefits filter job search` | **CONFIRMED EMPTY** for the four chips |
| `job collections` | **CONFIRMED** -- a1652837 only, already held. No delta |
| `top applicant jobs` | **CONFIRMED** -- a548337 and a1462229 already held; a1517941 is the same Top Choice surface, no new member capability |
| `Premium job seeker features` | **CONFIRMED** -- a1462281, a548337, a1517941 all already held |
| `resume builder AI writing assistant` | **+4** -- a6813101 corrected and expanded rows; a7146402 new |

**One article deliberately excluded.** `a10133010`, "Allow camera and mic permissions for
AI interviews", is browser-settings troubleshooting for Chrome/Safari/Firefox/Edge. It
documents no LinkedIn capability of its own, so it is cited as evidence that sections J-K
exist and is not counted as a row.

**Not re-walked, as instructed:** everything the first pass already covered. The seventh
hole in section 3 (hirer side, LinkedIn Learning course recommendations, Services
Marketplace) remains unwalked and out of scope.

---

## 7. RECEIPTS

    numbered rows in the table        151   (was 133 before the 2026-09-03 re-walk)
    denominator (rows carrying state) 150   (row 58 is a LinkedIn non-capability)
    four-way split                    CP 21 / CU 7 / XR 23 / GAP 99   (sums to 150)
    delta from the second pass        +18 rows, all GAP; covered set unchanged
    counted by                        grep against the finished table, not by eye
    excluded as NOT-A-LINKEDIN-CAP    1 (withdraw, per a512388) -- never entered the table
    gaps the skill already serves     7 (counted inside the 99)
    help pages fetched OK             48 + 32 + 34 per topic walk; overlap unmeasured
                                      + 6 articles fetched in the 2026-09-03 pass
    article-index queries run         10, all against linkedin.com/help/linkedin/search?q=
    holes checked and found EMPTY     2 (the four filter chips; per-job "Not interested")
    areas confirmed with no delta     3 (job collections, top applicant, Premium job)
    help pages dead (404)             9 distinct; notably a507571, a520684, a507653
    external WebSearch calls          0 in the second pass (budget was exhausted; the
                                      article index made it unnecessary)
    server tools measured             35 (grep -c "^@mcp.tool()")
    writes.PERFORMABLE                12
    writes.SANCTIONED_WRITES          13 (set_open_to_work has no tool)
    jobs tools of the 35              9 read + 3 write = 12
    tracker stages readable           3 of 5 (saved, applied, draft)
    live LinkedIn page loads          0
    mcp__linkedin__* calls            0
    tracked files edited              0
    commits                           0

Walk products retained at:
`<a session scratch directory>`
`...\hc-apply.md`, `...\hc-prefs.md`.
