# THE JOBS DIRECTION: the fifth of the GAP that was never asked the question

**Wave** `jobs-direction`. **Date** 2026-09-21. Read-only against LinkedIn: no browser,
no session, no page load, no `mcp__linkedin__*` call. Source, census and boundary only.

**CORRECTS:** `_audit/2026-09-20-the-reachable-ceiling.md` -- it records the jobs slice's GAP rows as carrying **no direction column at all** and therefore leaves them unmeasured; the first half is true of the per-row tables and the second is now discharged, and its own non-jobs numbers need re-taking before anything combines them with these (section 7).

**CORRECTED BY:** `_audit/2026-09-23-lane-l3-jobs.md` -- five of its address readings, re-taken through the shipped boundary: `J 16`'s suggestions belong to the semantic search at `/jobs/search-results/` (refused), not the classic `/jobs/search/` priced here; `J 18`'s list is drawn on the admitted jobs home `/jobs/jam/`, not on `/jobs/search-history/`; `J 56`'s date filter is a label-toggled checkbox on the admitted tracker tab, a press rather than a refused query; `J 116`-`J 120` sit behind the AI guide overlay that Amendment A13 of the 2026-09-03 gap-blockers ledger measured, a refused address, not on the admitted posting; and `J 110`'s Home tab is admitted but its content is organisation prose `shape.company_about_card` rules unpublished. `J 148` is resolved from AMBIGUOUS to R+W. `J 18`, `J 39` and `J 57` were then built and left GAP; the per-row directions of the rest live in `_audit/_census/jobs-directions.tsv`.

---

## 1. THE ANSWER, FIRST

| direction | rows |
|---|---|
| **R** | **29** |
| **W** | **25** |
| **R/W** | **2** |
| **AMBIGUOUS** | **1** |
| **total** | **57** |

**And the useful one.** Of the **31** rows that read (29 `R` plus the read half of the 2
`R/W`), **16 sit on an address `readonly.is_read_url` admits at HEAD**, 10 sit on an
address it refuses, and 5 name no readable address at all.

**The jobs slice answers DIFFERENTLY from messaging, and this is the finding.** The
messaging wave reported *"not one is blocked on a reader somebody could sit down and
write."* Jobs is not zero. **One row is buildable today on committed evidence alone**
(`J 40`), and **six more have an admitted address and a parser as their only remaining
cost**. Graded by evidence class in section 5, because "buildable" and "would close" are
two claims and only the first is verified for most of them.

---

## 2. THE COUNT WAS RE-DERIVED, NOT INHERITED

The brief said 57 and said not to trust it. Re-derived by importing
`scripts/count_census_states.py` and running its shipped `cells()` / `classify()` over
`_audit/_census/jobs.md` at HEAD:

    jobs.md    stated rows 150    GAP 57

**57 confirmed.** `cells()` was imported rather than re-implemented deliberately: it
honours the markdown escape for a literal pipe, and lines 156, 161, 243, 316 and 317 of
this file carry one. A hand-rolled `split("|")` returns the TAIL of those reasons and
looks like it worked -- register section 41. None of the five is a GAP row and none is in
section 2, so no edit in this wave goes near them.

**A number worth stating because the file's own prose disagrees with it.** `jobs.md`'s
frozen header block still reads `GAP 99`, deliberately -- it is pinned so that documents
citing it still resolve. 42 rows have left GAP since 2026-09-03 through other waves'
rulings. The 57 is today's tables; the 99 is the frozen headline. Both are correct and
they are not the same measurement.

---

## 3. THE STRUCTURAL FINDING: the direction data existed and was keyed by range

`jobs.md`'s per-row tables run `| # | capability | source | state | reason |` -- five
columns, no `R/W`, exactly as the ceiling document says. **But section 2, "WHAT EACH GAP
WOULD TAKE", is a table `| rows | gap | shape | R/W | REV |` whose first cell is a
ROW-RANGE and whose fourth cell is a direction.** `scripts/_check_jobs_range_directions.py`
already reads it, for a different purpose.

Expanded against today's 57:

| section 2 says | rows |
|---|---|
| a single direction (`R` or `W`) | 42 |
| a COMPOUND cell (`R + W`, `R (results) + W (the session)`) | 14 |
| named by no range at all (`J 131`) | 1 |

**A range direction is a claim about a BLOCK, and three of them are wrong about a row
inside them.** This is why the classification was done per row off the row's own
capability text rather than by expanding the ranges:

| row | capability text | range says | the row is | why |
|---|---|---|---|---|
| **J 37** | "List **and manage** all alerts" | `R` (range 37-40) | **R/W** | the row's own text names a write; its write half duplicates rows 33-34 |
| **J 56** | "**Filter** the tracker by date posted" | `W` (range 54-56) | **R** | filtering changes nothing; section 2 files an ordinary search as `R` |
| **J 82** | "**Observe** the Easy Apply daily limit / rate-pause state" | `W` (range 78-83) | **R** | the row's own verb is `Observe` |

Had the ranges simply been expanded, the split would have read `R 27 / W 27 / R/W 1 /
AMBIGUOUS 1` with 14 rows resolved only at block level. The per-row read moves three rows
and resolves all 57.

**A denominator note so two instruments are not read as disagreeing.**
`_check_jobs_range_directions.py` reports `99` frozen GAP rows in the jobs slice, because
it works off `build_blocker_map`'s FROZEN set. This wave works off the census at HEAD,
which is 57. Different denominators, both correct, neither one a drift in the other.

---

## 4. THE ONE THAT IS HONESTLY AMBIGUOUS

**`J 148` -- "Refine sections of the resume with suggested language."** Counted separately
rather than forced.

Section 2's own `REV` cell for this block says *"it produces a file; nothing is sent"*,
which argues `R`. Against that: LinkedIn **stores** resumes -- rows 70-73 are entirely
about stored resumes -- and whether a refinement persists to the stored copy is
**unmeasured**. Nobody has captured the surface. The direction is not decidable from the
file, so it is reported as `AMBIGUOUS 1` and not split.

Two neighbours were decidable and are recorded as such: `J 147` ("Receive personalized
insights") is `R`, gated behind `J 146`'s upload; `J 149` ("Export the result, **or**
attach it to a LinkedIn application") names both acts in its own text and is `R/W`.

---

## 5. THE BUILDABILITY ANSWER, GRADED

Every address below was probed against **`readonly.is_read_url` at HEAD**, never against
what a census cell claims. The instrument is
`scripts/_check_jobs_gap_directions.py`; its `--control-stub-admits` run proves the
reachability column follows the shipped boundary rather than the table in the file.

### 5a. VERIFIED-BY-INSTRUMENT -- the address is admitted at HEAD (16 rows)

`J 16, 37, 38, 39, 40, 57, 110, 116, 117, 118, 119, 120, 131, 136, 137, 138`

### 5b. Of those, what a reader would actually do

**BUILDABLE AND WOULD CLOSE -- committed evidence, boundary 0, no ruling, nothing needed
from the operator:**

- **`J 40` -- read per-job network proximity. This is the strongest row on the slice.**
  The row's own reason already states it: the field is **present and unparsed in two
  committed captures** (`tests/fixtures/jobs_search_hydrated.html` reads "1 company alum
  works here"; `job_detail_following_hydrated.html` reads "Company alumni from ..."), on
  pages `linkedin_search_jobs` and `linkedin_job_detail` load on an ordinary call, at
  addresses admitted since the first commit. The UN-hydrated twins read zero on every
  needle, so the hit is a property of the page and not a loose regex. No extractor exists
  anywhere in `linkedin_server/`. **"COST one parser, boundary 0. REOPENER a parser over
  either capture. WHO this repo."** Nothing is waiting on anybody.

**BUILDABLE AT BOUNDARY 0, BUT THE PAGE CONTENT IS UNMEASURED -- `J 110, 116, 117, 118,
119, 120` (6 rows).** The address is admitted and the only remaining cost is a parser --
but no capture of the target panel exists, so that a reader would FIND anything is a
hypothesis, named as one. **Three further rows sit in this section and are NOT in that
six**: `J 37` and `J 38` are refuted below, and `J 57` is dependent rather than
independent.

- **`J 116, 117, 118, 119, 120`** -- the "How you match" fields. Section 2 asserts
  116-120 *"render on the posting page `job_detail` already loads, for a Premium account,
  which this operator has. Parser additions at ZERO extra page load."* `/jobs/view/<id>/`
  is admitted (pattern 10). **That the panel renders for this account is UNVERIFIED** --
  it is section 2's claim, not a measurement.
- **`J 110`** -- Company Page Home tab. The Home tab **is** the Page root, and the root
  was admitted 2026-09-20 (`952af32`). A reader needs no boundary change. No capture
  exists.
- **`J 37` (read half) and `J 38` -- ADMITTED IS NOT SERVED, and this pair is the
  specimen.** `/jobs/alerts/` is admitted (2026-09-05, `61e3237`) and I first filed both
  as parser-only on that basis. **That was wrong and the boundary file says so two lines
  above the pattern:** measured by the `live-capture` wave, *"requested `/jobs/alerts/`
  landed `/jobs/jam` query: none"* -- LinkedIn **redirects away from the admitted
  address**. It does not 404, so a load scored pass/fail looks like success. The redirect
  target `/jobs/jam/` is separately admitted (pattern 40), so the navigation is legal end
  to end -- but a reader written against the alerts-manager shape would be parsing a
  different page than the one it asked for. **Neither row is parser-only; both need the
  landing surface captured first.** `readonly.py` names this class outright:
  *"ALLOWED-AND-STILL-WRONG IS A REAL CATEGORY AND THIS IS ITS SPECIMEN."*
- **`J 57`** -- the join. Both inputs already ship: the tracker is read by
  `linkedin_my_applications` / `linkedin_draft_applications` (rows 47-49, all CP), and
  the proximity field is `J 40`. **Blocked behind `J 40`, which is itself buildable.**
  Caveat recorded rather than hidden: the Applied tab reads zero, so the join would be
  vacuous on today's account.

**ADMITTED, READ, AND MEASURED NOT TO CLOSE (4 rows):**

- **`J 136, 137, 138`** -- `/learning/role-play/scenarios/` was admitted AND opened by the
  `live-capture` wave on 2026-09-20. The page serves, and `<main>` holds **17 characters**,
  byte-identical across three samples. **No shipped tool navigates there** -- that load was
  an ad-hoc probe, not a registered reader, and no extractor, fixture or `role_play`
  identifier exists anywhere in the package. So the reader is unwritten AND the surface is
  empty on this account: writing one today would parse 17 characters. Blocked on an
  account/flag state, not on an address and not on a ruling.
- **`J 16`** -- `/jobs/search/` is admitted and the needle was fired: every "suggested
  filter" spelling read 0. The row cannot move to MEASURED-ABSENT because **no observable
  identifies which search MODE served the page**. Reader runs; row does not resolve.

**ADMITTED BUT BLOCKED ON A RULING, NOT A BUILD (2 rows)** -- these are listed for you in
section 6 and stay GAP:

- **`J 39`** -- read job recommendations. `/jobs/collections/recommended/` is admitted AND
  a **shipped, live-fired tool already loads it**: `linkedin_job_collections`
  (`server.py:2046`). It returns **counts only, deliberately** -- *"No job title, no
  company name, no posting id, no member name"* -- under the package's name-freedom
  discipline. The row does not close without changing that posture, which is a ruling.
- **`J 131`** -- decide who to message. Both inputs sit on admitted addresses
  (`/premium/my-premium/`, `/mynetwork/invite-connect/connections/`), and the
  `linkedin-jobs` SKILL already serves the capability. Building a server path duplicates
  the skill.

### 5c. REFUSED at HEAD (10 rows) -- blocked on an address nobody has opened

`J 18` (`/jobs/search-history/`), `J 56` (the tracker pattern is exact: `?stage=` and
nothing else, so a date-filtered query is refused), `J 72`
(`/jobs/application-settings/`), and **`J 106, 107, 108, 109, 111, 113, 114`** -- every
Company Page TAB. The root pattern takes **no sub-path**, verified tab by tab.

### 5d. No readable address at all (5 rows)

`J 82` (behind the Easy Apply modal, which needs a press), `J 124`, `J 126` (section 2
says 123-126 need other surfaces and names none), `J 147`, `J 149` (both behind `J 146`'s
upload).

---

## 6. WHAT STAYS GAP PENDING A DECISION THAT IS YOURS, NOT MINE

No row's state was changed by this wave. These need a ruling:

1. **`J 116` -- does a derivation close a row, or must the named surface be parsed?**
   The capability "am I a top applicant for this posting" is **answerable today by two
   shipped tools with no new address and no new parser**: `linkedin_premium_job_collection(0)`
   reads `/jobs/collections/top-applicant/` and returns **numeric posting ids** (fired and
   proven live 2026-09-20), and `linkedin_job_detail` consumes such an id. Set membership
   gives the flag. But the census row names the *"How you match" panel*, a different
   surface, which is still unparsed. Moving the row would be ruling that the member
   capability, not the documented surface, is what the census counts. **I did not rule it.**

   **A THIRD EXPIRED PREMISE, FOUND WHILE CHECKING THAT EVIDENCE, AND IT IS IN SOURCE
   RATHER THAN IN A CENSUS.** `linkedin_server/job_collections.py`'s module docstring
   still carries a shouted heading -- *"NOBODY HAS EVER OPENED EITHER PAGE, AND THIS
   MODULE SAYS SO IN ITS OUTPUT"* -- and calls its own reading *"a HYPOTHESIS about the
   target, not a measurement of it."* **Both pages were opened later the same day.** The
   tool docstring in `server.py` records the firing with numbers only real loads produce
   (two id sets "disjoint from the control and overlapping each other 11 of 25"), the
   probe `scripts/_probe_premium_collections_live.py` and the audit
   `_audit/2026-09-20-the-first-firing.md` both exist, and `git merge-base --is-ancestor`
   confirms the module's commit `fce0843` precedes the firing's `71d1f3c`. **A reader who
   starts at the module -- the natural place to start -- is told the surface is unmeasured
   and stops.** I have NOT edited it: it belongs to the wave that owns that surface, and
   this is a measuring wave. Flagged for you to route.
2. **`J 39` -- should the collections reader return titles?** It deliberately returns
   counts only. Closing the row means relaxing a privacy posture the package argues for at
   length. That is your call, not a build.
3. **`J 131` -- should the server duplicate a capability the skill already serves?**
   Section 2 already answers this for rows 37-40 with *"Building a server path would
   duplicate it and lose the proximity field"*. The same argument plausibly covers 131.

4. **`J 40` -- commission the proximity reader?** Section 10 answers the question that
   gates it: the field **is** name-free extractable, in exactly one shape, and only on the
   search card. It is the one row on this slice that needs no address, no ruling and
   nothing from the operator, and the field it would return is the one a sibling channel
   ranks highest of anything in the workflow. **Not built here** -- a shaper on a page
   dense with other people needs its own scope and its own blast radius. This is a
   commission decision, not a build I should have taken unasked.

**And one thing I deliberately did not touch.** The ban on `set_input_files` rests on
*"the operator has never been asked about it"* and no answer is recorded anywhere
(`_audit/2026-09-20-the-sanctioned-seventh.md`). `J 70` and `J 146` are filed `W` and stay
GAP. **Nothing in this wave treats that question as settled in either direction.**

---

## 7. THE CEILING ARITHMETIC, AND WHY I AM NOT PUBLISHING A COMBINED TOTAL

The ceiling document reports `W 171 / R 70 / R/W 1` over 242 GAP rows carrying a direction
column. **Adding this wave's 57 to that 242 would be wrong**, and the reason is measurable:

    this wave, off the census at HEAD:   jobs 57 + profile 55 + messaging 82 + network 91 = 285
    the ceiling document:                242 non-jobs rows + 57 jobs = 299

285 against 299. **14 rows have left GAP in the other three slices since that measurement
was taken.** A number one agent hands another is a reading with a timestamp the receiver
cannot see. The jobs split in section 1 is exact and current; **the other slices' splits
need re-taking before any document adds them together.** That re-take is one run of the
existing instruments and needs nothing from you.

What can be said safely: **jobs contributes 25 W and 29 R**, and **the ceiling's shape
does NOT survive on this slice.** Everywhere else writes dominate; here reads do, 29
against 25. The read share is **29 of 57 (50.9%)** against the ceiling's non-jobs `70 of
242` (28.9%) -- **the brief's hypothesis that jobs is read-heavy is CONFIRMED, by a factor
of about 1.8.**

**That does not weaken the ceiling argument; it localises it.** "A write-direction GAP row
is not a backlog item" still holds for all 25 W rows here. What changes is where the
remaining reachable work lives: if the campaign has a readable remainder, **this is the
slice it is in**, which is exactly what the brief suspected and is now measured rather
than suspected.

---

## 8. IN-PLACE CORRECTIONS MADE, AND THEIR EVIDENCE

Two statements in `jobs.md` section 2 were **false at HEAD** and are corrected in place.
Neither is a schema change, neither moves a row, and both are struck-through-with-reason
rather than deleted, so a reader arriving at the old claim can see what replaced it.

| where | the expired premise | the evidence |
|---|---|---|
| range `31-36, 41` | *"`/jobs/alerts` is not on the read allowlist"* | admitted 2026-09-05 by `61e3237`, **sixteen days after the cell was written**; `is_read_url` returns True at HEAD |
| range `106-114` | *"Needs `/company/<slug>/` and its tabs on the read allowlist"* | the ROOT was admitted 2026-09-20 by `952af32`. The pattern takes **no sub-path**, so every tab is still refused -- verified one by one. Only `J 110` is affected |

**No `R/W` column was added to any census table**, and no per-row table was restructured.
The classification lives in `scripts/_check_jobs_gap_directions.py` as data, emittable as
TSV with `--emit-tsv`.

**Should the column exist?** My reasoning, for you to rule on: **no, not as a sixth
column.** Section 2 already carries direction and carries it with the COST and the
REVERSIBILITY beside it, which is where a direction is actually useful. A per-row column
would duplicate it and immediately drift from it -- the three disagreements in section 3
are what that drift looks like when there is only one copy. What was genuinely missing was
not a column but a READER that resolves the ranges per row and flags where a block
direction is wrong about a row inside it. That is now the instrument, and its drift
control fails loudly when the GAP set moves.

---

## 9. THE INSTRUMENT

`scripts/_check_jobs_gap_directions.py`. Registered as section **47**.

**Shown failing before admission, three ways:**

- `--control-stub-admits` replaces `is_read_url` with a stub admitting everything. The
  REFUSED set goes **10 -> 0**, proving the reachability column reads the shipped boundary
  and not the table in the file.
- `--control-drift` drops `J 110` from the table; the reconciliation **names it**.
- A planted row (`DIRECTIONS[999]`, a row the census does not hold) makes the default run
  exit **1** -- so the reconciliation is a gate, not decoration. This matters because the
  census moved eight times yesterday; a stale split here would otherwise be silent.

It is a REPORT for reachability and a GATE for drift, deliberately: an address the
boundary refuses is a fact to read, not a failure, but a classification that no longer
matches the census is always a defect.

**WHAT IT CANNOT TELL YOU, STATED SO NOBODY READS MORE INTO ITS COLUMN THAN IS THERE.**
`ADMITTED` means *our gate permits this navigation*. It does **not** mean LinkedIn serves
that address, and on `J 37` / `J 38` it demonstrably does not -- the gate admits
`/jobs/alerts/` and LinkedIn lands `/jobs/jam`. I filed both rows as parser-only on the
strength of this instrument's own column before a child refuted it from
`readonly.py`'s comment. The column is not wrong; the question it answers is narrower
than the question a reader wants answered. **Closing that gap needs a page load, which is
outside a text-only wave** -- so the instrument states the limit rather than implying a
reach it does not have, and the two affected rows carry `ADMITTED-BUT-REDIRECTED` in their
`why` field so the TSV cannot mislead a downstream consumer either.

---

## 10. THE PROXIMITY FIELD: can it be read name-free? MEASURED, AND THE ANSWER IS NOT THE OBVIOUS ONE

Asked because a sibling channel ranks this field highest of anything in the
job-search workflow. Four questions, each answered by measurement here rather
than taken on report.

**Q1. Is there a census row for it?** **YES -- `J 40`**, "Read per-job network
proximity (`2 connections`, `1 company alum`)", state `GAP` `SKILL`. **The census
is not missing the field**; it is the row this wave already named the strongest
buildable row on the slice.

**Q2. Is the page admitted, and does a shipped tool load it?** **YES to both, and
twice over.** `/jobs/search/` (pattern 9) is loaded by `linkedin_search_jobs`,
which parses cards through `shape.parse_job_card`; `/jobs/view/<digits>/`
(pattern 10) is loaded by `linkedin_job_detail` through `dom.read_job_posting`.
Both admitted since the first commit.

**Q4, taken before Q3 because it is decisive. Is the stripping a RULING?**
**NO. Nobody ruled it out, and nothing strips it.**

The only two mentions of the field in the whole package are comments --
`dom.py:93` and `shape.py:699` -- and **both describe a DEFENCE, not a
deletion.** They list "an alumni line" alongside "Promoted", "Viewed",
"Actively reviewing applicants" and a salary chip as lines LinkedIn inserts
that can displace a positional field, and the architecture's answer was to
ANCHOR each field on something that identifies it (`link_text` for the title,
`logo_name` for the company, `meta_line` for the location) so that an inserted
line cannot shift them.

**The alumni line is not deleted by that design. It is simply never collected**,
because it falls outside all three anchors. And it is not caught by either
subtraction: `_JOB_STATUS_LINE` (`shape.py:521`) and `JOB_STATUS_PHRASES`
(`shape.py:1844`) were both read in full and **neither names `alum`, `alumni`,
`connection` or `proximity`**. A package-wide grep returns **zero** occurrences
of `proximity` and exactly the two comments for `alum`.

> **NOBODY DECIDED NOT TO HAVE THIS FIELD. IT IS AN INVARIANT NOBODY RULED --
> collateral damage from protecting three adjacent fields, not a judgement
> about this one.**

**Q3. Could an extractor be name-free? THIS IS THE CRUX, AND THE ANSWER IS
"YES, BUT THE SAFE ANCHOR IS THE COUNTERINTUITIVE ONE."**

Measured on the committed captures. Organisation names are written `<ORG>` here
and are **not** reproduced.

On the search card the field renders **TWICE, and the two copies do not say the
same thing**:

    <div class="job-card-container__job-insight-text" dir="ltr">
      <span aria-hidden="true">1 company alum works here</span>
      <span class="visually-hidden">1 <ORG> company alum works here</span>
    </div>

**The VISIBLE copy is name-free. The SCREEN-READER copy carries the employer
name.** That inverts the instinct: `aria-hidden="true"` normally marks
decoration to ignore, and the `visually-hidden` span is the copy an
accessibility-minded engineer reaches for first. **Here it is the dangerous
one.** A reader that took the container's whole text would concatenate both and
get the name.

Two things in that window are reassuring and were checked rather than assumed:
**0 member-space (`/in/`) hrefs** within 1200 bytes, and the adjacent `<img>`
carries an **empty `alt`**. So the search-card insight names no PERSON at all --
the only identifier in reach is an employer.

**The job-detail surface is worse and has no safe copy.** Under a heading
"People you can reach out to" there is a single `<p>` reading
`Company alumni from <ORG>` -- **no count, no name-free twin, nothing to anchor
on that is not the sentence itself.** `/in/` hrefs within 1500 bytes: **0**; the
neighbouring anchor is a `/jobs/view/<digits>/` link, which this package already
treats as safe.

**So a name-free extractor is achievable, and only in one shape:**

    {count: int, relation: <index into a closed tuple>}

taking the integer through `coerce.as_int` / `as_count` (so a refusal cannot
quote what it refused -- register 44, `an exception is not a return value`) and
returning the relation as a POSITION IN A TUPLE rather than matched text, which
is the discipline `linkedin_job_collections` already ships. **Never the line.**
On the detail surface even that is not available: the honest ceiling there is a
boolean or a block count.

**A COUNTING CAVEAT THAT APPLIES TO EVERY NUMBER ABOVE.** A raw grep reports
`company alum` twice in the search capture. That is **two renderings of ONE
fact**, and `alum` / `company alum` / `alumni` are one occurrence of one word on
the detail page. **A count over a rendered page counts renderings, not facts.**
The distinct-fact counts are: search capture **1**, detail capture **1**,
un-hydrated twins **0 and 0** -- and the twins reading zero is what makes the
hit a property of the page rather than of a loose regex.

**NOT BUILT IN THIS WAVE, DELIBERATELY.** A shaper on a page dense with other
people needs its own scope and its own blast radius. What this section
establishes is that the field is **a genuine gap nobody ruled**, that it is
**name-free extractable on the search card in one specific shape**, and that
**the detail-page spelling has no name-free rendering at all** -- which is the
fact a future builder would most easily get wrong, because the search card
would teach them the opposite.
