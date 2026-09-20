# `PREMIUM-APPLY-SURFACES` -- the five slots measured, and the reason they stay empty is arithmetic, not evidence

> **SHA NOTE, added 2026-09-20.** The short hash `1349fe6` cited
> below was committed on a `worktree-agent-*` branch that never merged, so
> it is reachable only from that branch and never from `master`. **The work
> itself landed.** Mapped to its `master` twin -- identical subject, identical
> author date, identical `git patch-id` -- under **"Dead hashes, recovered"**
> at the foot of this file; it is kept in place here because a short hash
> is the key a reader arrives with.

Wave `premium-apply`, 2026-09-19, from master `201b757`. Scope: the largest
single unreached block in the census -- one blocker publishing 5 rows, with
zero ever recovered, declined by four previous waves.

## RESULT

    filed                     0 of 5
    verdict                   DECLINED -- and the reason is now a measurement
    blockers with NO row      3 (unchanged)
    UNASSIGNED                21 (unchanged)
    census source             blocker-assignments.tsv, 0 lines appended
    map                       NOT regenerated; blocker-map.tsv untouched
    instrument added          scripts/_check_open_slots.py, control shown failing
    writes fired              0     browser opened     0     attribution     0

**THE PREVIOUS DECLINE SAID "unfillable by searching; needs a ruling". THAT WAS
THE WRONG SHAPE OF ANSWER AND THIS DOCUMENT REPLACES IT.** The question is not
*which of six rows is not this blocker's*. It is measured here that the row
excluded by that question -- whichever it is -- **has no destination anywhere in
the ledger's 97 blockers.** There are 12 fillable slots in the entire census
against 21 unassigned rows, so 9 rows can never be filed by anybody, and this
family contributes exactly one of them. A ruling naming the sixth row would not
home it. It would only decide which row gets to be homeless.

| | |
|---|---|
| referent set | exactly `J 78` - `J 83`, six rows, measured closed (section 1) |
| discriminators tested | 5, of which 3 are new to this wave; all 5 fail, each for a stated reason (section 2) |
| slots available elsewhere for the surplus row | **1** (`ACCOUNT-VERIFICATION`), and it is ruled shut (section 3) |
| displacement available | **0** -- every semantically adjacent blocker is COMPLETE on a committed row-id enumeration, four of them `LEDGER-EXPLICIT` (section 3.3) |
| what would close it | a COUNT correction, not a membership ruling (section 5) |

---

## 0. VERIFIED BEFORE STARTING, and the brief reproduced exactly

`scripts/build_blocker_map.py` at `201b757`:

    frozen GAP rows at 1c08e5f     409
    ledger blockers parsed          97  rows 409
    assigned from committed sources 388
    UNASSIGNED                       21
    complete 86   partial 8   absent 3

Disk and brief agree on every figure. The 21 unassigned rows carry the literal
token `UNASSIGNED` in column 2, as the brief states; an emptiness filter returns
nothing. Every extraction below used the literal.

**THE NUMBER-SPACE TRAP, checked rather than avoided.** Ledger amendment C
(`_audit/2026-09-03-linkedin-gap-blockers.md:1571`) reads *"Blockers 72, 78, 79,
80, 85, 86 and 87 are each charged `allowlist +1, WriteSpec`"*. Those seven are
RANKS in the ranked table -- `MULTILANG-PROFILE`, `OPEN-PROFILE-SETTING`,
`LEARNING-CERTIFICATE`, `ACTIVITY-VIEW-SETTING`, `FEED-PREFERENCES`,
`EMBED-SETTING`, `SKILL-PAGE-SURFACE` -- a settings cluster with no jobs row in
it. Read the table row, not the integer. The same check was applied to the
CORRECTED-BY note at ledger `L283` (*"across rows 83, 31, 29, 48, 68 and 54"* --
also ranks) and to the probe comment `# 61 PREMIUM-APPLY-SURFACES` (`61` is the
rank; the blocker sits at ranked-table line 231). Three collisions, none of them
load-bearing here.

**AND THE COUNTS-DO-NOT-CLOSE WARNING IS NOT ONLY TRUE, IT IS THE FINDING.**
Section 3 turns it into a number.

---

## 1. THE REFERENT SET IS EXACTLY SIX, AND THAT IS MEASURED

### 1.1 One committed source names rows for this blocker, and it names six

`scripts/_probe_jobs_tail_boundary.py:63`

    # 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83.

**Read in context rather than as a one-line quote, that comment is one of six
blocker headers in the probe's `_CANDIDATES` tuple, and three of them enumerate
rows.** The other two are checkable against the ledger:

| probe comment | rows it names | ledger publishes | |
|---|---:|---:|---|
| `# 36 JOB-ALERTS-SURFACE -- census rows J31-J36 and J41` | 7 | 7 | AGREES |
| `# 62 TRACKER-ROW-MENU -- census rows J54-J56` | 3 | 3 | AGREES |
| `# 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83` | 6 | 5 | **OFF BY ONE** |

The author is transcribing the census's own section-2 group ranges onto ledger
blockers -- the comment says "census rows" and the non-contiguous `J31-J36 and
J41` reproduces `jobs.md`'s group line `| 31-36, 41 | all alert writes |`
exactly. **Both checkable transcriptions land on the published count. The third
is the one that misses.** That is a control on the author's accuracy, and it is
recorded here because no prior document quoted more than the single line.

### 1.2 The census's own group label enumerates the six and nothing else

Frozen `_audit/_census/jobs.md:437`:

    | 78-83 | Premium apply extras (cover-letter AI, Top Choice, limits,
      self-ID) | each is a distinct surface; Top Choice spends a
      non-refunding monthly credit | W | Top Choice NOT reversible |

Four named features, six rows, and the map is onto and one-to-one with nothing
left over:

    cover-letter AI  ->  J 78
    Top Choice       ->  J 79, J 80
    limits           ->  J 81, J 82
    self-ID          ->  J 83

**The family is CLOSED at six.** The label names nothing that is not one of the
six, and no row of the six is unnamed by the label. This matters twice below:
it is why `J 81` cannot be carved out on a subject test (section 2.2), and it is
why no seventh candidate exists.

### 1.3 Nothing outside those six can be this blocker's row

Three independent passes, all returning empty:

* **The 21 unassigned rows read end to end.** Outside `J 78`-`J 83` the only
  other premium-shaped row is `J 150` (Writing Assistant recruiter message).
  The census gives `J 150` its **own** section-2 line and its own section
  (`### L. Resume tips and Writing Assistant, Premium (5)`), separate from
  section D where all six of `J 78`-`J 83` sit; no committed source has ever
  named it for this blocker; the blocker it does resemble,
  `AI-ASSIST-MESSAGING`, was checked by the routing pass
  (`_audit/2026-09-19-routing-the-unassigned.md:121`) and is COMPLETE at 2 of 2
  with no room. **`J 150` is not a candidate here and the brief's inclusion of
  it on its title is refuted.**
* **The 388 assigned rows.** Every one is held on a committed source; none is a
  premium-apply row that a member of this family should displace (section 3.3
  takes this seriously rather than asserting it).
* **The whole-corpus blocker-evidence scan.**
  `_audit/2026-09-06-corpus-sweep-blocker-evidence.md` lists neither any of
  `J 78`-`J 83` in its assignable set (section 2) nor in its
  disagreed-with-itself set (section 5). **A dedicated corpus-wide scan produced
  ZERO blocker claims for any of the six**, which is independent corroboration
  that the probe comment is the only source there is.

---

## 2. FIVE DISCRIMINATORS TESTED. ALL FIVE FAIL, EACH FOR A DIFFERENT REASON

Three of these are new to this wave. They are recorded whole -- including the
two that looked strongest -- because a sixth wave will otherwise re-derive them.

### 2.1 The published `1R` -- RETIRED, not available

`{J 78, J 79, J 80, J 82, J 83}` is exactly `1R/4W` if `J 82` is the read. That
filing was made at `1349fe6` (branch-only; on `master` at `81c8534`) and
retracted at `0aca3d0`. Request 4
(`_audit/2026-09-19-the-three-ruling-requests-ruled.md:220`) ruled the ledger's
`1R` an ERROR against the census and closed the door explicitly: *"That `1R` may
no longer be cited as evidence in any filing."* **Not re-litigated.**

### 2.2 The subject test on `J 81` -- RULED AGAINST, and the source's own label nails it in

Request 2a ruled that *"the subject is the account rather than an application"*
is the reader's test, while the census's sectioning is the source's, and it
places `J 81` in section D, Applying. `_audit/2026-09-19-the-row-walk.md:263`
contests that ruling on the ledger's ASSIGNMENT RULE (earliest binding
constraint) and files it as ruling request B, unruled at this tree.

**I add one measurement that was not in either document, and it runs against the
request rather than for it:** section 2's group label does not merely place
`J 81` in the same section, it names its feature. *"Premium apply extras
(cover-letter AI, Top Choice, **limits**, self-ID)"* -- `J 81` and `J 82` are the
**limits** pair, named by the source as a member of this family, in the same
cell that the probe maps onto this blocker. `J 81` is not adjacent to the
family. It is one quarter of the source's enumeration of it.

**The section-D objection in `the-row-walk` is answered by this and its own
counter stands too:** "the section test proves too much" is correct about
SECTIONS and irrelevant to the GROUP LABEL, which discriminates at feature
level and includes `J 81` by name.

### 2.3 NEW -- the blocker's own NAME as the discriminator. REFUTED BY THE SOURCE

Request 1 forced eight rows by restating a blocker's name as a test (*"the
blocker is NAMED for a menu that acts on ONE conversation"*). The same move here
asks: which of the six is PREMIUM?

    J 78  "Cover Letter Assistance (PREMIUM AI drafting)"   census says Premium
    J 79  "Mark a job Top Choice (PREMIUM, 3/month)"        census says Premium
    J 80  optional message with a Top Choice mark           inherits, not stated
    J 81  Verify account to raise the Easy Apply limit      not stated
    J 82  Observe the Easy Apply limit / rate-pause state   not stated
    J 83  Save voluntary self-identification answers        not stated

Under the Request 1 shape this would FORCE `J 78`, `J 79` and `J 80` in (six
candidates, five slots, the excluded one must come from the three that fail, so
the three that pass are in regardless).

**IT FAILS, and the refutation is the source's.** `jobs.md:437` labels the whole
range *"Premium apply extras"*. The census has already classified all six as
Premium; asking "does the row's own cell repeat the word" is a reader's test
applied on top of a source classification that answers it. Request 2a's standard
-- *"When a reader's test and the source's classification disagree, the source
wins"* -- kills it. **A discriminator that the source has pre-empted is not a
discriminator.**

### 2.4 NEW -- the `/preload/guideOverlay/` measurement on `J 78`. DECLINED

This is the strongest unexplored route in the corpus and it reaches
`LEDGER-AMENDMENT` grade evidence, so it is set out in full.

Ledger amendment A13 item 4 measured, on the unsanitised committed capture
`_audit/_probe-job-followed-company-hyd.html`, that the posting page carries
three `<a href>` anchors on `/preload/guideOverlay/` whose `query` parameter is
LinkedIn's own control label:

    'Show match details'
    'Create cover letter'
    'Help me stand out'

graded **VERIFIED-BY-INSTRUMENT** in that amendment. So the cover-letter control
is measured PRESENT, on a page `linkedin_job_detail` already loads, as a sibling
of a control belonging to a different blocker. Combined with the ledger's
`allowlist +2` charge on this blocker -- a charge for NEW addresses -- that
reads as: `J 78` needs no new address, so it is not behind the boundary cost
that defines `PREMIUM-APPLY-SURFACES`, and it is the one out. Five remain.

**DECLINED, on four grounds, in descending order of how much they matter.**

1. **A13 names neither the row nor the blocker.** Its subject is
   `MATCH-DETAILS-COLLAPSED` and rows `J 116`-`J 120`. Binding
   `'Create cover letter'` to `J 78` and `J 78` to blocker 61 is the READER's
   work in both steps. This is the exact standard that retracted the previous
   filing in this same blocker.
2. **It does not home the row.** Excluding `J 78` from blocker 61 sends it
   nowhere: `MATCH-DETAILS-COLLAPSED` is COMPLETE at 5 of 5 on `LEDGER-EXPLICIT`
   evidence, and A13 explicitly declines to move anything (*"The
   `AI-ASSISTANT-OVERLAY` rename is a proposal, not a ruling"*). Section 3 is
   the general form of this objection.
3. **The surface argument does not survive the ledger's assignment rule.**
   Generating a cover letter is a WRITE; this blocker carries the WriteSpec; an
   already-loaded surface makes the row CHEAPER, not differently blocked. The
   earliest binding constraint is unchanged.
4. **A13's own grading forbids the step the route needs.** That the anchor
   invokes a generation product is labelled **DERIVED (strong, not measured)**
   in the amendment itself. The route needs it to be measured.

### 2.5 NEW -- `cheap-reads` routes cover-letter and Top Choice to `PREMIUM-JOBS-SURFACES`. REFUTED

Two committed documents describe a DIFFERENT blocker's rows in terms that name
two of this family:

> `_audit/2026-09-05-cheap-reads.md:294` and
> `_audit/2026-09-05-cheap-reads-build.md:180`: *"Row 41's rows are different
> features -- cover-letter assistance, marking a job Top Choice, AI job-fit
> tips"*

Rank 41 is `PREMIUM-JOBS-SURFACES`, 3 rows, `3R`. Taken at face value this homes
`J 78` and `J 79` elsewhere and leaves four -- a different, worse answer.

**Measured against the census, that sentence is a paraphrase and it is wrong on
two of its three items.** `PREMIUM-JOBS-SURFACES` is COMPLETE at 3 of 3 holding
`J 124`, `J 125`, `J 126`, filed `RECON-DOC` on `jobs.md` section H, which reads:

    | 124 | Premium AI company intelligence (headcount, openings, ...)  |
    | 125 | "Jobs where you're a top applicant" section                 |
    | 126 | Premium AI job-fit tips                                     |

*AI job-fit tips* is exact. *Marking a job Top Choice* is `J 125`'s **top
applicant** garbled -- the census itself puts the two phrases in one breath at
`jobs.md:473` (*"Top Applicant and Top Choice"*), which is where the slip comes
from. *Cover-letter assistance* corresponds to nothing in the blocker's section
at all. **And the direction refutes it independently:** rank 41 publishes `3R`,
while `J 78` and `J 79` are writes under the census's group column. A paraphrase
that misses two of three and contradicts the split does not outrank a structural
section enumeration.

---

## 3. THE MEASUREMENT: THE EXCLUDED ROW HAS NOWHERE TO GO

Every discriminator above asks *which of the six is out*. **Nobody asked where
the out-one would go.** It has no answer, and that changes what kind of problem
this is.

### 3.1 The instrument

`scripts/_check_open_slots.py`, added by this wave. It reuses
`build_blocker_map.ledger_counts()` and `build()` so no number is retyped, and
carries a control that must fire before it prints: the ledger's published total,
the map's data lines and the frozen GAP set are three independently produced
numbers that must all read 409, because the ledger claims a PARTITION of that
set. `--selftest` perturbs one published count by +1 and the control refuses:

    SELFTEST: ACCOUNT-VERIFICATION published count perturbed +1.
    CONTROL FAILED -- the ledger's published total (410), the map's data
    lines (409) and the frozen GAP set (409) must all agree.  exit=1

### 3.2 The open-slot inventory, and it does not pair with the unassigned rows

    ACCOUNT-VERIFICATION         pub  3  held  2  open 1   1 fillable
    ARTICLE-SURFACE              pub  6  held  5  open 1   1 fillable
    COMPANY-PAGE-SURFACE         pub 18  held 16  open 2   2 fillable
    CONTENT-ANALYTICS-SURFACE    pub  5  held  4  open 1   1 fillable
    CREATOR-HUB-SURFACE          pub  4  held  3  open 1   1 RULED PHANTOM
    EVENTS-SURFACE               pub 18  held 17  open 1   1 RE_FILED elsewhere
    FOUND-A-JOB-FLOW             pub  1  held  0  open 1   1 RULED PHANTOM
    GROUPS-SURFACE               pub 32  held 30  open 2   2 RE_FILED elsewhere
    HASHTAG-EXISTENCE            pub  3  held  1  open 2   2 RE_FILED elsewhere
    MESSAGE-ADDRESSING           pub  1  held  0  open 1   1 RULED PHANTOM
    OPEN-TO-HIRING-MODAL         pub  5  held  4  open 1   1 fillable
    PER-MESSAGE-OVERFLOW-MENU    pub  2  held  1  open 1   1 fillable
    POST-COMMENT-CONTROLS        pub  4  held  3  open 1   1 RULED PHANTOM
    PREMIUM-APPLY-SURFACES       pub  5  held  0  open 5   5 fillable

    open slots, total                    21
    ... whose row is filed elsewhere      5   (RE_FILED -- the row exists)
    ... RULED to have no referent         4
    FILLABLE SLOTS                       12
    UNASSIGNED ROWS                      21

    ROWS THAT CAN NEVER BE FILED          9

The four ruled phantoms are `CREATOR-HUB-SURFACE` and `POST-COMMENT-CONTROLS`
(**ruled by the box**, `_audit/2026-09-19-the-five-requests-ruled.md` section E)
and `FOUND-A-JOB-FLOW` and `MESSAGE-ADDRESSING` (**wave verdicts**,
`_audit/2026-09-19-the-four-absent-blockers.md` sections 3 and 4). The
distinction is kept in the instrument's table: on the two box-ruled ones alone
the fillable count is 14 and **at least 7** rows are unhomeable. Either way the
sign does not change.

**SO THE CENSUS IS NOT 21 ROWS LOOKING FOR 21 SLOTS. IT IS 21 ROWS FOR 12
SLOTS.** That is stated nowhere else in this corpus and it is the number a
successor needs before it computes any "N candidates for M slots" argument.

### 3.3 Of the seven fillable slots outside this blocker, exactly one is reachable, and it is shut

Read against the 21 unassigned rows by capability text:

| slot | reachable by a `J 78`-`J 83` row? |
|---|---|
| `ACCOUNT-VERIFICATION` 1 | **YES -- `J 81`, and it is the ONLY verification-shaped row among all 21.** Ruled shut at Request 2a |
| `ARTICLE-SURFACE` 1 | no -- the article-shaped unassigned rows are `N 41` / `N 42`; whose slot this is was not adjudicated here |
| `COMPANY-PAGE-SURFACE` 2 | no |
| `CONTENT-ANALYTICS-SURFACE` 1 | no |
| `OPEN-TO-HIRING-MODAL` 1 | no |
| `PER-MESSAGE-OVERFLOW-MENU` 1 | no -- `M M13` is named its only candidate by `_audit/2026-09-19-partial-blockers-closed.md` |

**And displacement is closed too.** The surplus row could in principle displace a
filed row in a COMPLETE blocker. Every semantically adjacent jobs blocker was
checked against its evidence class:

    FILE-UPLOAD-UNSANCTIONED   16/16   LEDGER-EXPLICIT (section 5 item 1 lists
                                       all sixteen rows verbatim)
    MATCH-DETAILS-COLLAPSED     5/5    LEDGER-EXPLICIT (L472, L1183)
    CLOSED-SINCE-CENSUS         7/7    LEDGER-EXPLICIT on its jobs rows
    JOB-SEARCH-PARAMS           6/6    LEDGER-EXPLICIT
    JOBS-APPLICATION-FORBIDDEN  3/3    RECON-DOC, census group 70-73
    EASY-APPLY-MULTISTEP        1/1    RECON-DOC, census group 68
    PREMIUM-JOBS-SURFACES       3/3    RECON-DOC, census section H (see 2.5)
    PREMIUM-READER-NOT-BUILT    1/1    RECON-DOC, J 127
    JOBCARD-OVERFLOW-MENU       2/2    RECON-DOC

**Not one has room, and four are held by the ledger's own verbatim
enumerations.** There is no displacement to make.

### 3.4 What that does to the question

The ledger's 409 published slots are a PARTITION claim -- `build_blocker_map.py`
asserts the total and it holds exactly. In a partition of a fixed set, **every
slot with no referent must be matched by a row with no slot.** Four phantom
slots are already on record; nine rows are already unhomeable. **So the ledger
under-counts somewhere by construction, and this blocker is the one place in the
jobs slice where a committed enumeration names MORE rows than the ledger
publishes.**

That is not a proof that blocker 61 is the under-count. **It is a measurement
that "the source over-names by one" -- Request 2a's reading -- is not the only
reading available, and that the arithmetic which would settle it has already
failed in the opposite direction four times.** The direction of the error is
undetermined and the document that reads it one way did not have these numbers.

**A SECOND OVER-NAMING EXISTS AND IT IS NAMED HERE RATHER THAN LEFT OUT:**
`_audit/2026-09-06-corpus-sweep-blocker-evidence.md` section 6 records two rows
that would have pushed `ANALYTICS-CONTROLS-UNPRESSED` to 5 against a published
4. So blocker 61 is not unique in the census, only in the jobs slice. Its
candidate list is in a gitignored scratch file and could not be read from a
worktree (section 7, defect 2).

---

## 4. PER-PUBLISHED-SLOT VERDICT

The five slots are not individually named by any source, so a per-slot table is
five copies of one verdict. The honest form is per-candidate. Both are given.

| published slot | verdict |
|---|---|
| 1 of 5 | DECLINED -- no forced row; see per-candidate table |
| 2 of 5 | DECLINED -- as above |
| 3 of 5 | DECLINED -- as above |
| 4 of 5 | DECLINED -- as above |
| 5 of 5 | DECLINED -- as above |

| candidate | what was searched | what is missing |
|---|---|---|
| `J 78` Cover Letter Assistance | probe file whole; ledger A13's guideOverlay measurement (2.4); `cheap-reads` / `cheap-reads-build` routing to rank 41 (2.5); help id `a7121956` across the corpus (also carried by `J 63`, XR); the Premium name test (2.3) | a source that names the ROW and the BLOCKER. A13 names neither; `cheap-reads` is refuted on its own census section |
| `J 79` Mark a job Top Choice | as above, plus help id `a1462229` (shared with `J 80`; `jobs.md:602` lists it beside `J 125`'s `a548337` under one search term, which is where 2.5's confusion originates) | the same. Nothing separates it from `J 80`, which shares its help id |
| `J 80` optional message with a Top Choice mark | as above | the same. It is the only row whose Premium status is inherited rather than stated, which is the closest thing to a discriminator in the set, and 2.3 shows why that cannot be used |
| `J 81` Verify account to raise the limit | `ACCOUNT-VERIFICATION`'s open slot; Request 2a; ruling request B in `the-row-walk`; all 21 unassigned rows for a rival verification row | nothing is missing -- the source's group label names it a member of this family (2.2). It is the only one of the six with a reachable slot elsewhere and that slot is ruled shut |
| `J 82` Observe the limit / rate-pause state | the retired `1R`; `_audit/2026-09-19-the-read-rows.md:197` (address could not be established; `easyapply`, `easy-apply`, `/jobs/application` all forbidden) | the discriminator that once admitted it has been retired by ruling and may not be cited |
| `J 83` Save self-identification answers | help id `a507694` (shared with `J 61`, `J 64`, `J 76`, all XR under the settings-family refusal); `profile.md` section 8, which sets the same capability aside as NOT-ENTITLED, US-only | a blocker. The profile slice's set-aside is not a blocker and does not remove it from the 409; no NOT-ENTITLED blocker exists among the 97 |

---

## 5. WHAT WOULD ACTUALLY CLOSE THIS, AS TWO DECIDABLE QUESTIONS

Neither is "which of the six is out". That question has been asked four times
and section 3 shows it has no useful answer, because its answer homes nothing.

**Q1 -- THE COUNT.** Is blocker 61's published `5` correct, or is it `6`? This is
decidable on evidence already on disk: the ledger's cell makes two claims from
one reading of one census group, `rows 5` and `1R/4W`; **the box has already
ruled the second one an error.** The first has never been examined. If it is
also wrong, all six file and the blocker closes at 6 of 6.

**Q2 -- THE ASSERTION.** `build_blocker_map.py` fails on `map > published`
(*"the map assigns MORE rows than the ledger published"*). That guard is correct
and has caught a real parser defect before. But it means **the map physically
cannot record a ledger under-count**, while `RE_FILED` lets it record the
opposite. If Q1 goes the other way, the fix is a declared-exception table of the
same shape as `RE_FILED` and `RULED_PHANTOM` -- which
`_audit/2026-09-19-the-five-requests-ruled.md` section D already prescribes for
the split check, in those words.

**I did not make either change.** Q1 is a ruling on a first-party count, and Q2
would rewrite a gate every concurrent wave is running.

---

## 6. FOUR THINGS FOUND IN PASSING

1. **`ACCOUNT-VERIFICATION` is now permanently PARTIAL at 2 of 3.** `J 81` is
   the only verification-shaped row among all 21 unassigned, and Request 2a shut
   it out. Measured here rather than suspected: the other 20 were read end to
   end. Its cost cell's own hedge is the corroboration -- *"no row names a url,
   so the address is ASSUMED"*.

2. **A cited enumeration is still unreadable.** `_audit/_scratch/` is gitignored,
   so `_would-exceed-published.tsv` (the other over-naming's candidate rows,
   section 3.4) and `_progress-unlocatable-recovery.md` section 47 cannot be
   opened from a worktree. `_audit/2026-09-19-the-four-absent-blockers.md`
   reported the same class this evening. **This is the second wave in one night
   blocked by the same gitignored directory**, and worktree isolation is the
   reason both hit it: a worktree carries no gitignored file.

3. **The map's UNASSIGNED reason string is still false for these six.**
   `blocker-map.tsv` says *"no committed source names this row against any
   blocker"* against `J 78`-`J 83`, and `scripts/_probe_jobs_tail_boundary.py:63`
   does name them. Reported by the previous wave and unfixed; I did not fix it
   either, for the same reason (it rewrites all 21 UNASSIGNED lines while
   siblings regenerate the file). **It is now load-bearing:** section 1 of this
   document rests on a source that column denies exists.

4. **`scripts/_check_published_split.py` skips 19 blockers** because the jobs
   slice's row table has no per-row direction column -- direction for a jobs row
   exists ONLY in the range-keyed section-2 table. That is the mechanical reason
   Request 4 had to rule on a group-level `W`, and it means no split-based
   discriminator will ever be available for any jobs blocker.

---

## 7. PROVENANCE, AND WHAT I DO NOT VOUCH FOR

* No write fired. No browser opened. `blocker-assignments.tsv` unchanged, 0
  lines appended. `blocker-map.tsv` untouched; `build_blocker_map.py --write`
  never run. `build_blocker_map.py` (read-only) reproduces the briefed state at
  `201b757` before and after this wave.
* One file added: `scripts/_check_open_slots.py`, read-only, with its control
  shown failing under `--selftest`. Its `RULED_PHANTOM` table is hand-maintained
  by design and says so; an empty slot is never inferred to be a phantom.
* **Sections 1.1, 2.3, 2.4, 2.5, 3.2 and 3.3 are new to this wave.** Sections
  2.1 and 2.2 restate standing rulings and are not re-litigated.
* **NOT VOUCHED FOR:** the `RE_FILED` entries, the `J 124`/`J 125`/`J 126`
  filings to `PREMIUM-JOBS-SURFACES`, and the `FOUND-A-JOB-FLOW` /
  `MESSAGE-ADDRESSING` over-count verdicts are other waves' work. Section 3.2
  depends on the last pair only for the size of the number, not its sign:
  dropping both leaves 14 fillable slots against 21 rows and every conclusion
  stands.
* **THE REOPENER.** Any committed source that names FIVE of `J 78`-`J 83`, or
  that homes any one of the six anywhere, retracts section 3 and this decline
  with it. Any ruling on Q1 closes the blocker outright.
* Relations and counts only. No identifier value is emitted anywhere above.

## Dead hashes, recovered

Added 2026-09-20. The hash mapped here was made on a `worktree-agent-*` branch
that never merged, so the citation was never checkable from a clone -- NOT
because history was rewritten, but because the branch carrying the commit was
never published. **The underlying work did reach `master`**, re-applied under a
new hash.

Method, measured per pair rather than inferred from ordering: the live hash is
an ancestor of `master` and the dead hash is not; both commits carry a
byte-identical SUBJECT and a byte-identical author identity and date;
`git patch-id --stable` returns the SAME id for both, so the CONTENT is
identical and not merely the message; that subject occurs EXACTLY ONCE on
`master`, so the key is unambiguous; and the dead hash prefixes exactly one
object, so a reader typing it gets one answer. The four controls that show those
checks can fail, and the whole 22-row table, are in
`_audit/2026-09-20-the-evidence-that-resolves.md`.

| dead hash | subject (the durable reference) | live hash | confidence |
|---|---|---|---|
| `1349fe6` | census(blockers): file the three rulings -- fill what is forced, leave what is chosen | `81c8534` | CONFIRMED |
