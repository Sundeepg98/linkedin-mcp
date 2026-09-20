# The contingent write-offs

A write-off is CONTINGENT when its reason cell asserts a fact about the
OPERATOR, his ACCOUNT, or the WORLD rather than about the capability or the
code. Three had already cost this census before this pass began --
`ADMIN-RIGHTS-NOT-HELD` (a fact about a Tuesday), Premium (a fact recorded
true in August and still filed as a blocker in September), and `J 127` (banked
MEASURED-ABSENT by an instrument carrying no needle for a balance).

This pass tests the rest. Read-only: no browser, no LinkedIn session, no page
load, no mailbox opened, no write fired. Everything below is measured against
committed evidence or against the skill's own source, run offline.

Repo at `bf275cf` when the measurements were taken; this document's own guard
lands at `5e2727e`.

---

## 0. THE THREE VERDICTS, AND WHY THE CENSUS SPELLS THEM THE SAME

The census has one word, `NOT-OURS`, for three different situations:

| verdict | what it means | what it costs to change |
|---|---|---|
| **FALSE NOW** | the asserted fact is not true, and committed evidence in this repo says so | nothing -- correct the cell |
| **TRUE BUT CHANGEABLE** | the fact holds today and an act changes it | the named act |
| **TRUE AND PERMANENT** | the fact cannot be changed by him or by us | nothing, and the row is genuinely closed |

The census already knows how to do this properly, and does it in exactly one
place. `_audit/2026-09-05-decide-retire-rulings.md` s6 gives **every** one of
its twelve retirements a concrete REOPENER and names **who can establish it**
-- "a capture", "the operator", "LinkedIn", or a named instrument. Not one of
the `NOT-OURS` write-offs carries either field. The discipline exists in this
repository; it was applied to the DECIDE-RETIRE queue and to no other.

**That is the finding under all the findings below.** The failure is not that
somebody reasoned badly about the Gmail skill. It is that a queue was created
whose entries are exempt from the reopener rule the sibling queue obeys.

---

## 1. `SERVED-BY-GMAIL-SKILL` -- 6 rows, checked against the skill's SOURCE

**The claim under test**, `_audit/2026-09-03-linkedin-gap-blockers.md` s3:

> | `SERVED-BY-GMAIL-SKILL` | 6 | NOT-OURS | Available to him today through
> `linkedin-jobs`, with no LinkedIn session at all |

The six rows, from `_audit/_census/blocker-map.tsv`, all GAP at freeze and GAP
today: `J 37`, `J 38`, `J 39`, `J 40`, `J 57`, `J 131`.

### 1.1 The instruments, run rather than described

The skill lives outside this repo at
`D:\Sundeep\projects\job-hunting\.claude\skills\linkedin-jobs\`. All three of
its executables were run offline, against their own committed fixtures:

    parse_digest.py    --selftest   SELFTEST PASS -- 7 msgs, 38 cards, 37 unique, 5 proximity, 1 dupe
    career_insights.py --selftest   SELFTEST PASS -- 4 msgs, 36 entries, 29 unique people, 30 slug / 6 post
    referral_join.py   --selftest   SELFTEST PASS -- 9 matcher cases

**The skill works.** Nothing below is an argument that it is broken. Two of the
six rows it serves outright, and this document confirms them rather than
inheriting them.

`parse_digest.py --json fixtures/*.txt`, structure only:

    unique jobs        37      source_kind   job_alert 31 / recommendation 6
    with proximity      5      warnings key  present, 0 warnings
    rows w/ source_alert + source_geo   31      distinct alerts   4
    rows w/ alert_id                     0      <- see 1.2

`referral_join.py --json`, structure only, run 2026-09-20:

    applications 156 | proximity_cards 43 | people 29
    referrals 6 | free_actions 10 | inmail_candidates 5
    credits: available 10, granted 10, committed 0, recorded_sends 0

### 1.2 Row by row

---

#### `J 37` -- "List and manage all alerts" -- **SPLIT. The write-off is half true and the other half is FALSE NOW.**

Reason cell: *"server: none. Skill: each digest body carries `Your job alert
for {QUERY} in {GEO}` and a stable `savedSearchId=`, so the live alert set is
enumerable from mail; `alert-tuning.md` holds the current 5-alert inventory."*

**The MANAGE half is not served by the skill, and the skill says so.**
`SKILL.md` s"If the user asks how to get more out of this": *"It is an operator
action at linkedin.com/jobs/alerts -- specify it, do not attempt it."* The
skill creates, edits, deletes, pauses and re-frequencies nothing.

**The LIST half is served, with two limits the cell does not carry:**

1. It enumerates alerts that MAILED in the window, not the alert set. An alert
   whose delivery channel is app-only -- census row `J 36` is precisely
   *set alert delivery channel (email / app / both)* -- sends no mail and is
   invisible to this method BY CONSTRUCTION. So is an alert with no new jobs.
2. **The stable id the cell leans on never reaches a caller.** `SSID_RE` is
   matched and assigned to `meta['alert_id']` in `parse_body`, and the card
   dict built at the end of that same function copies `alert_query`,
   `alert_geo`, `id` and `date` and **not** `alert_id`. Measured: 0 of 37 rows
   carry it, and `--json` emits `messages` as an integer, so the meta dict is
   never published either. Identity is therefore by QUERY STRING, which is not
   stable across the edit that census row `J 33` describes.
3. `alert-tuning.md` describes itself as *"Written 2026-08-20 against the
   alerts that were live that day"* and RECOMMENDS repointing two of the five.
   It is a dated snapshot carrying pending changes, not a live inventory.

**And the reason is FALSE NOW on its own terms, because "server: none" is
wrong.** `linkedin_server/readonly.py` admits the alerts page on
`_ALLOWED_URL_PATTERNS`, and the gate was measured at HEAD by importing the
module -- no browser:

    READ  the alerts page                      ALLOWED  /jobs/alerts/
    READ  the alerts page, no slash            ALLOWED  /jobs/alerts
    WRITE create an alert                      REFUSED  /jobs/alerts/create
    WRITE delete an alert                      REFUSED  /jobs/alerts/delete
    WRITE alert settings/frequency             REFUSED  /jobs/alerts/settings/
    WRITE pause an alert                       REFUSED  /jobs/alerts/pause
    READ  an alert detail page                 REFUSED  /jobs/alerts/12345
    (allowlist 35 patterns, forbidden 33 substrings)

The comment above that pattern states the position in the repo's own words:
*"THE ADDRESS IS A HYPOTHESIS AND THIS COMMENT WILL NOT PRETEND OTHERWISE.
Nobody has opened this page."* It then cites the skill's inventory as its
ground truth -- *"the skill's own inventory says he has five"* -- which is the
2026-08-20 snapshot above. The circle closes: the server defers to the skill,
the skill defers to a month-old hand-written table, and the census reads the
pair as coverage.

**REPLACEMENT.** Split the row.
* `J 37a` LIST the alert set -- **GAP**, blocker `ALERTS-PAGE-UNREAD`.
  Address ADMITTED, page never opened, no reader. This is Amendment A10's
  bought-and-unread shape and the cost is one load plus a parser, not zero and
  not somebody else's.
* `J 37b` MANAGE the alert set -- **GAP**, blocker `JOB-ALERTS-SURFACE`, where
  its six siblings `J 31`-`J 36` already sit. Blocked by this repo's own
  `_FORBIDDEN_URL_SUBSTRINGS`, measured above -- a CODE fact, not a world fact.

---

#### `J 38` -- "Read the jobs an alert delivered" -- **SOUND. Confirmed on evidence.**

Reason cell: *"server: none. Skill step 1-3: `jobalerts-noreply@linkedin.com`,
~6 cards/email, 5 emails/day."*

Served, and uniquely. 31 of 37 unique rows in the fixture run carry
`source_kind: job_alert`, over fixtures pinned to real mail, with 0 warnings.

**I went looking for the flattering counter-argument and it fails.**
`_audit/2026-09-05-routes-already-admitted.md:98` files `J 38` as **REACHABLE
NOW** by the server at `/jobs/search/?keywords=<the alert's own query>`,
ALLOWED since `b7e210b`. That route is not this capability: re-running the
query returns TODAY's results, and *the jobs an alert delivered* is a
historical fact only the email records. The route table's verdict is the
over-claim here, not the skill's.

**No replacement.** The row stays written off. Add the reopener the cell lacks:
*reopens if the server ever stores a delivered result set, which nothing today
does.*

---

#### `J 39` -- "Read job recommendations" -- **SOUND, but the reason is spelled wrong.**

Reason cell: *"server: none. Skill: `jobs-noreply@linkedin.com`,
`FACET_SUGGESTIONS_COMMS_EMAIL`."*

Served: 6 of 37 rows carry `source_kind: recommendation`, from the
facet-layout fixture.

**But "server: none" is again not the reason.** `/jobs/collections/recommended/`
is ALLOWED (measured above), and census row `J 42` records that
`linkedin_job_collections` was WIRED AND FIRED on 2026-09-19 and sees **9 job
postings** there. What it cannot do is name them: the tool returns COUNTS ONLY,
by the structural name-freedom constraint that row documents in detail.

So the server reaches the surface and is FORBIDDEN BY ITS OWN DESIGN from
emitting the rows. That is a RULING of this repo, not an absence, and the
difference decides who may reopen it.

**REPLACEMENT.** Keep the row closed against the skill, and re-spell the reason:
*"Served by the skill. The server reaches this surface -- `linkedin_job_collections`
counts 9 postings there -- and this repo's name-freedom ruling forbids it
emitting the rows. REOPENER: a ruling that named job rows may cross the
boundary. WHO: the operator."*

---

#### `J 40` -- "Read per-job network proximity" -- **FALSE NOW. Overturn.**

Reason cell: *"**The skill's exclusive field.** SKILL.md:13 -- 'No scraper and
no job-board API can produce that field.' **Not on any surface this server
reads**."*

**The last clause is refuted by this repo's own committed captures.**

    tests/fixtures/jobs_search_hydrated.html
        <span aria-hidden="true"><!---->1 company alum works here<!----></span>
    tests/fixtures/job_detail_following_hydrated.html
        <p class="...">Company alumni from ... </p>

Both are captures of pages `linkedin_search_jobs` and `linkedin_job_detail`
load on an ordinary call, at addresses on the allowlist since the first commit.

**Scanned all 20 committed HTML fixtures: 2 carry the field, 18 do not** -- and
the 18 include the UN-HYDRATED TWINS of those same two pages, which read zero
on every spelling of the needle. That is the discriminator: the result is a
property of the page, not of a loose regex.

**Nothing extracts it.** `grep -niE "alum" linkedin_server/ --include=*.py`
returns exactly two hits, one `#:` comment in `dom.py` and one docstring
sentence in `shape.py`, and both are about the field as a HAZARD -- a line that
can shift `company` into `location` -- rather than as a field to read.

The skill's own sentence is about scrapers and job-board APIs. This server is
neither: it drives his own signed-in browser, which is precisely the thing that
CAN see a field LinkedIn computes against his graph and renders to him. The
census generalised a true sentence about third parties onto a first-party
reader.

**Present and discarded is not the same verdict as not present**, and the price
is different: a parser at an already-admitted address, versus somebody else's
job.

**REPLACEMENT.** `J 40` -- **GAP**, blocker `PROXIMITY-NOT-PARSED`, queue
BUILD, boundary cost 0 (address already admitted), cost = 1 parser. The skill
keeps serving it in the meantime; the row is no longer NOT-OURS.

**Guard shipped:** `tests/test_proximity_is_on_a_read_surface.py`, s5 below.

---

#### `J 57` -- "View network connections reachable for a tracked job" -- **FALSE NOW. Overturn.**

Reason cell: *"server: none. Skill `referral_join.py`: joins digest proximity +
career-insights people against the Naukri applications DB -- 'That pairing does
not appear in any UI he uses'."*

**Read the quoted sentence again: it is the skill saying it does something
ELSE.** The row sits in section C of the jobs census, *Saved jobs and the job
tracker*, source `a8684146`, among rows about LinkedIn's own My Jobs stages.
"A tracked job" means a job in THAT tracker.

`referral_join.py` reads, from its source:

* `load_applications` -> `mcp-servers/naukri/naukri.db`, `mode=ro`. A different
  platform's applications. Nothing in the skill reads LinkedIn's tracker.
* `warm_referrals` keys on **company**: `match(p['company'], a['company'])`.
  It is a per-COMPANY join, not a per-JOB one.
* `load_proximity` reads a STATIC file,
  `mcp-servers/_audit/linkedin-7day-extract.json`, 72,371 bytes, dated
  **2026-08-20**.

So for a job in the LinkedIn tracker, `referral_join.py` has no input at all.

**And the two halves both exist in this repo already.** The server reads the
tracker today -- census rows 47-49 are COVERED-PROVEN, `linkedin_saved_jobs`,
`linkedin_applied_jobs`, `linkedin_draft_applications` -- and the proximity
field sits on the job surfaces, per `J 40` above. What is missing is the join,
and nobody owns it because the row was filed as served.

**REPLACEMENT.** `J 57` -- **GAP**, blocker `PROXIMITY-NOT-PARSED` (BLOCKED
behind `J 40`), queue BLOCKED. Note on the row: *the skill performs an adjacent
and more valuable join -- applied-on-the-other-platform AND has-network-here --
which is not this capability and should not be deleted when this one is built.*

---

#### `J 131` -- "Decide WHO to message and whether it costs a credit" -- **SOUND, with two limits the cell does not carry.**

Reason cell: *"server: none. Skill `referral_join.py` + `inmail-targeting.md`:
free 1st-degree DM vs paid InMail, ranked; 'The tool recommends only. It never
sends'."*

The row asks the CLASS question -- free or paid -- and `plan()` answers it
structurally, not by guess: every career-insights entry is first-degree
(LinkedIn's own hero link in that mail carries `network=["F"]`), so those are
free direct messages; a warm-referral company with no named contact is out of
network and costs a credit. Measured live offline: 10 free actions all labelled
`free direct message (1st-degree)`, 5 candidates all labelled `one InMail
credit (target is out of network)`. **Confirmed.**

**Two limits, stated rather than left to be discovered:**

1. **The people input is fixture-bound.** `main()` builds the people set from a
   HARDCODED glob, `fixtures/career-insights/*.txt` -- four files dated
   2026-07-23 to 2026-08-15. `--db`, `--extract` and `--ledger` are all CLI
   flags; there is **no `--insights` flag**. `career_insights.py` itself takes
   paths and `-` for stdin, so the live path exists one level up -- but
   `referral_join.py` as shipped cannot be pointed at fresh mail without
   editing it.
2. **The credit number is computed and never consumed.** `plan(referrals,
   people, credit_state)` takes `credit_state` and does not read it anywhere in
   its body. The balance is printed on its own line and does not affect the
   ranking.

**No replacement for the row.** Add the two limits to the cell, and the
reopener: *reopens if the free/paid split ever needs a live balance, which is
`J 127`, not this row.*

### 1.3 `J 127` is not one of the six, and the skill does not close it either

`J 127` *Read the InMail credit balance* is flagged `SKILL` in `jobs.md` but
filed under `PREMIUM-READER-NOT-BUILT`, and was re-opened this morning. Stated
here so nobody closes it on the skill by association:

`credits()` **models** a balance from a hand-maintained local ledger at
`mcp-servers/_audit/inmail_ledger.json`. **That file does not exist.** The
function therefore runs on its own hardcoded fallback -- a `premium_started`
date, 5 a month, a 15 cap, 90-day expiry -- and returned
`available 10, granted 10, committed 0, recorded_sends 0` today. Every one of
those integers is arithmetic over an assumption. Nothing has ever read a
balance from LinkedIn. **The skill does not serve `J 127`.**

### 1.4 Verdict on the write-off as a whole

| row | verdict | what replaces it |
|---|---|---|
| `J 37` | **SPLIT**: manage half false-now, list half true-but-limited | two rows: `ALERTS-PAGE-UNREAD` + `JOB-ALERTS-SURFACE` |
| `J 38` | **SOUND** -- confirmed, not inherited | keep; add reopener |
| `J 39` | **SOUND**, reason mis-spelled | keep; reason becomes a RULING, not an absence |
| `J 40` | **FALSE NOW** | `PROXIMITY-NOT-PARSED`, BUILD, boundary cost 0 |
| `J 57` | **FALSE NOW** | `PROXIMITY-NOT-PARSED`, BLOCKED behind `J 40` |
| `J 131` | **SOUND**, two limits unstated | keep; add both limits |

**Three of six sound, two false now, one split.** The blocker survives with 2
rows (`J 38`, `J 39`) plus one half-row (`J 37a` is not its, `J 37`'s list half
is). It should not survive with 6.

---

## 2. `OWNED-BY-A-SIBLING-SLICE` -- 4 rows, and 2 of them are orphans

The structural twin of s1: a write-off that asserts a fact about ANOTHER
DOCUMENT without checking that document.

Reason, `_audit/2026-09-03-linkedin-gap-blockers.md` s3: *"`N 149 150 151 160`
-- network records these as owned by the messaging slice, and messaging counts
them too."* Queue RE-FILE, *"nothing to do but correct the census."*

Checked. `_audit/_census/network.md` files them exactly as described. The
messaging slice was then searched for each twin:

| network row | capability | twin in `messaging-and-content.md` |
|---|---|---|
| `N 149` | Report a message | **`M38`** Report a message as spam. REAL |
| `N 160` | Send, receive and manage message requests | **`M6` `M7` `M8`** send / accept / decline. REAL |
| `N 150` | Report a whole conversation thread | **NONE** |
| `N 151` | Mark a system-flagged message as safe instead of reporting it | **NONE** |

The zero is a measurement, not a glance. Eleven needle spellings over the
messaging slice:

    report a message          1   <- M38, the J149 twin
    report a conversation     0
    report a thread           0
    report the conversation   0
    report this conversation  0
    mark as safe              0
    system-flagged            0
    flagged message           0
    message request           5   <- M6/M7/M8, the N160 twins
    safe                      2   <- both unrelated prose, read and checked
    spam                      2

**Why this one matters more than its row count.** The blocker's queue is
RE-FILE, and the re-file it prescribes is *"these belong to messaging."* Execute
it on `N 150` and `N 151` and those two capabilities leave the census entirely,
because the slice that is supposed to inherit them never counted them.

**A write-off that is merely wrong costs a wrong number. This one, if
executed, DELETES two capabilities.**

And the reconciliation discipline exists here too, in one direction only.
`messaging-and-content.md` s10 is a model of the work -- it hand-matched its
sixteen flagged rows, fired its own conditional once somebody checked its
trigger, subtracted exactly four, and recorded that a 0.62-similarity pass
returned nine twins of which only three were real. Nobody ran it from the
network side.

**REPLACEMENT.**
* `N 149`, `N 160` -- blocker stands, `OWNED-BY-A-SIBLING-SLICE`, twin named in
  the cell (`M38`; `M6 M7 M8`) so the claim is checkable from the row.
* `N 150`, `N 151` -- **UNASSIGNED**, and must NOT be re-filed out of
  `network.md`. They are the network slice's until some slice claims them.

(Flagged for the lead: a sibling on cross-slice duplicates may be in this same
ground. This measurement is 4 rows deep and stops there.)

---

## 3. THE SWEPT LIST

(pending -- filled in below from the two extraction passes)

---

## 4. TWO SECONDARY FINDINGS

### 4.1 Four of the six assignment locators are dead, and one is worse than dead

`_audit/_census/blocker-assignments.tsv` cites a file and a LINE for each of
the six. Resolved against the files at HEAD:

| row | cited locator | what is actually there |
|---|---|---|
| `J 37` | `routes-already-admitted.md` L97 | **correct** -- the `J 37` route row |
| `J 38` | `routes-already-admitted.md` L98 | **correct** -- the `J 38` route row |
| `J 39` | `jobs.md` L177 | a BLANK LINE |
| `J 40` | `jobs.md` L178 | the TABLE HEADER |
| `J 57` | `jobs.md` L200 | **row 21**, a COVERED-PROVEN posting-detail row |
| `J 131` | `jobs.md` L311 | a table SEPARATOR |

The live rows are at `jobs.md` 225, 226, 248 and 362 -- every citation has
drifted by 48 to 51 lines. `J 57`'s is the dangerous one: it does not dangle,
it lands on a DIFFERENT row that reads COVERED-PROVEN, so a reader checking the
provenance of a GAP finds a covered row and stops.

The assignment evidence itself is sound -- all six are recoverable from the
`SKILL` marker in the census's own state column, which is a stronger shape than
a line number. **The locators should be the row ids they already have, not
line numbers.**

### 4.2 `alert_id` and `claimed_new` are parsed and thrown away

Two fields in `parse_digest.parse_body` are matched into `meta` and then not
copied into the card dict, and `--json` publishes `messages` as an integer, so
neither reaches any caller: `alert_id` (the `savedSearchId`, 0 of 37 rows) and
`claimed_new` (the "N new jobs" telemetry). The first is load-bearing for
`J 37` -- it is the stable identity the census cell cites. This is a defect in
a file outside this repo and is recorded here, not fixed here.

---

## 5. THE GUARD, SHOWN FAILING

`tests/test_proximity_is_on_a_read_surface.py`, six tests, committed at
`5e2727e`. It pins the EVIDENCE for s1's `J 40` overturn, not the conclusion:
two positives on the hydrated job captures, three controls on pages that do not
draw the field (two of them the un-hydrated twins of the positives), and one
check that the package names the field only in prose.

Driven over MUTATED SANDBOX COPIES -- no committed file written at any point --
baseline green, then:

    M1  delete the proximity line from the hydrated search page   RED
    M2  plant the field into the UN-HYDRATED twin                 RED
    M3  plant a CODE line naming the field into shape.py          RED
    M4  erase both prose mentions (calibration)                   RED
    mutations that turned the guard RED: 4 of 4

**The guard's first version was wrong and the guard caught it.** The
prose/code split originally skipped only lines beginning with `#`, and so
called the `shape.py` DOCSTRING sentence a reader; it went red on the real tree
immediately. It now uses `tokenize` for comments and `ast` for docstring
ranges. Recorded because it is the standing law here: every fresh instrument
built in one session had a bug on its first attempt.

M2 also failed to fire on its first run -- the mutation inserted before
`</body>`, and `jobs_search.html` is a FRAGMENT with no `</body>`. The
mutation was a no-op and the harness reported GREEN. The harness now asserts
the mutated text differs from the original before running. **A control that
did not land looks exactly like a control that did not fire.**

---

## 6. WHAT THIS PASS DID NOT DO

1. **It did not move a census row.** Siblings are building capability in other
   worktrees; s1.4, s2 and s3 state exact replacements for the lead to
   integrate.
2. **It did not re-litigate Premium or `ADMIN-RIGHTS-NOT-HELD`.** Both are
   named in the brief as already-found instances and both have live siblings.
3. **It did not open the mailbox.** The skill's live path runs on the
   `claude_ai_Gmail` MCP, which is available in this session and was
   deliberately not used: every claim above about what the skill serves rests
   on its own committed fixtures and its own selftests, which is evidence a
   future session can re-run.
4. **It did not fix the skill.** s4.2 is a defect in another codebase,
   reported.
5. **The `J 39` and `J 131` confirmations are narrower than they look.** Both
   say the skill DOES serve the row. Neither says the row could not ALSO be
   served here -- `J 39` explicitly could, and is held shut by a ruling.
