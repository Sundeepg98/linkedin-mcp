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

**That is the finding under all the findings below**, and s6 turns it into a
number: **a contingent write-off carrying a reopener is 15% still GAP; one
carrying none is 91% still GAP**, and every contingent write-off yet found
wrong sits in the second group. The failure is not that somebody reasoned
badly about the Gmail skill. It is that a queue was created whose entries are
exempt from the reopener rule the sibling queue obeys, and the exemption is
measurable.

---

## 1. `SERVED-BY-GMAIL-SKILL` -- 6 rows, checked against the skill's SOURCE

**The claim under test**, `_audit/2026-09-03-linkedin-gap-blockers.md` s3:

> | `SERVED-BY-GMAIL-SKILL` | 6 | NOT-OURS | Available to him today through
> `linkedin-jobs`, with no LinkedIn session at all |

The six rows, from `_audit/_census/blocker-map.tsv`, all GAP at freeze and GAP
today: `J 37`, `J 38`, `J 39`, `J 40`, `J 57`, `J 131`.

### 1.1 The instruments, run rather than described

The skill lives outside this repo, at `<job-hunting>/.claude/skills/linkedin-jobs/`
(path written repo-relative on purpose -- the absolute one carries a real name).
All three of its executables were run offline, against their own committed fixtures:

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

### 3.1 By the subject the BLOCKER NAME asserts

Derived from `_audit/_census/blocker-map.tsv` at HEAD -- 409 rows, 301 still
GAP today. **This is a candidate list, not a set of verdicts.** It classifies
each of the 97 blockers by what its NAME asserts, which is cheap and
reproducible; whether the assertion is still true is the per-blocker work in
s1, s2 and s3.3.

| subject the name asserts | blockers | rows | still GAP |
|---|---:|---:|---:|
| **OPERATOR** -- what he owns, holds or administers | 1 | 15 | 14 |
| **ACCOUNT** -- what LinkedIn renders for his account | 7 | 19 | 14 |
| **WORLD** -- another codebase, slice, product or platform | 18 | 45 | 18 |
| **SURFACE?** -- a surface whose existence FOR HIM is contingent | 22 | 139 | 108 |
| CODE -- this repo: no tool, no parser, no pattern, a ruling | 47 | 191 | 147 |
| | **95** | **409** | **301** |

**Two things about that bottom row, so it is not quoted wrong.** The blocker
column holds **95 distinct values over 409 rows**, and one of them is
`UNASSIGNED` carrying **19 rows** -- so **94 named blockers** appear in the map
against the ledger's published 97, and the 19 unassigned rows sit inside the
CODE line above without being a code fact or anything else. They are
unclassified, and a sibling is on them.

**OPERATOR, ACCOUNT and WORLD together: 26 blockers, 79 rows, 46 still GAP.**
Those are the ones whose name alone says the reason is contingent.

    OPERATOR  ADMIN-RIGHTS-NOT-HELD           15 rows, 14 GAP   <- instance 1, sibling owns

    ACCOUNT   MATCH-DETAILS-COLLAPSED          5 rows,  5 GAP
              ANALYTICS-CONTROLS-UNPRESSED     4 rows,  3 GAP
              PANEL-NOT-OBSERVED               3 rows,  0 GAP   <- SOUND, see below
              PREMIUM-JOBS-SURFACES            3 rows,  3 GAP   <- instance 2, siblings own
              ACCOUNT-VERIFICATION             2 rows,  2 GAP
              OPEN-PROFILE-SETTING             1 row,   0 GAP
              PREMIUM-READER-NOT-BUILT         1 row,   1 GAP   <- instance 3 (J 127)

    WORLD     AI-INTERVIEW-PRODUCT            14 rows,  3 GAP
              SERVED-BY-GMAIL-SKILL            6 rows,  6 GAP   <- s1, 2 overturned
              OWNED-BY-A-SIBLING-SLICE         4 rows,  4 GAP   <- s2, 2 orphaned
              HELP-CENTER-FORM                 3 rows,  0 GAP
              OFF-PLATFORM-WIDGET              3 rows,  2 GAP
              AI-ASSIST-MESSAGING              2 rows,  0 GAP
              LIVE-BROADCAST                   2 rows,  0 GAP
              AUDIO-EVENTS-EXISTENCE           1 row,   1 GAP
              DEVICE-GEOLOCATION               1 row,   0 GAP
              HASHTAG-EXISTENCE                1 row,   0 GAP
              LEARNING-CERTIFICATE             1 row,   1 GAP
              MOBILE-APP-ONLY                  1 row,   0 GAP
              NO-URL-AT-ALL                    1 row,   0 GAP
              PAID-BOOST                       1 row,   0 GAP
              SIGNIN-INTERSTITIAL              1 row,   0 GAP
              THIRD-PARTY-PROFILE-FORBIDDEN    1 row,   0 GAP
              VIDEO-MEETING-INTEGRATION        1 row,   1 GAP
              VOICE-CAPTURE                    1 row,   0 GAP

**Read the "still GAP" column, because it is the load-bearing one.** Twelve of
the eighteen WORLD blockers have already gone to zero GAP -- they were ruled,
retired or built, and almost all of them under `decide-retire-rulings`, WITH a
reopener. **The two that are entirely still GAP are the two this document
overturns.** That is not a coincidence: a write-off that was never given a
reopener is a write-off nobody revisited.

`PANEL-NOT-OBSERVED` is the ACCOUNT-class write-off done RIGHT, and is
confirmed here rather than criticised. Its reason is an account fact -- *the
panel is not drawn for this account* -- and it ships with a control that
reproduces 1/1/0 on four committed captures, reads 0/0/0 on exactly the two
the fixture table marks un-hydrated, reproduced live twice across a browser
restart, and a reopener stated as an instrument: *the control at 1/1/0 AND a
target needle non-zero; a zero without the control firing reopens nothing.*
**That is what an account-contingent write-off is supposed to look like.**

### 3.2 The SURFACE? class is the biggest unexamined block, and I am not claiming it

139 rows, 108 still GAP, across 22 blockers whose names read like code facts
(`SERVICES-PAGE-SURFACE`, `CREATOR-HUB-SURFACE`, `NEWSLETTER-SURFACE`,
`BADGES-SURFACE`, `SCHOOL-PAGE-SURFACE`, `MULTILANG-PROFILE`, ...) while the
underlying claim is often an account fact: does that surface EXIST for him.

**I am flagging this class, not adjudicating it.** Several already have live
siblings (`build-company-page`, `build-newsletter`), several have already been
re-costed twice, and a name-level guess is not a measurement. The one worked
example below is offered as the SHAPE of the check rather than as a verdict on
the class.

### 3.3 One worked example from the SURFACE? class -- `P H11`, and the answer is "nobody looked"

`SERVICES-PAGE-SURFACE` has been re-costed carefully already:
`_audit/2026-09-05-network-tail.md` s3 corrects its own `allowlist +1` in the
same session, on the right ground -- row `P H11` is *the "Providing services"
section AS RENDERED ON THE PROFILE*, which is `/in/me/`, ALLOWED, so no pattern
is owed. **The address reasoning is right.**

What nobody joined is whether the section is drawn at all -- and the census
already holds the answer, in a different row of the same slice.

    profile.md H1   Create a Service Page / add services   GAP
                    "one of the three items the `Open to` menu resolves to
                     on his account; NEVER ACTIONED"

    profile.md s7.8  "A census of all five profile captures measured the
                      `Open to` button's menu resolving to exactly three
                      items -- Hiring, Providing services, Finding volunteer"

    profile.md H11  "Providing services" section as rendered on the profile
                    GAP   "no tool, no reason"

So, measured across five captures: **the entry point to create a Service Page
is rendered on his profile, and he has never used it.** `H11` is the section
that appears once a Service Page EXISTS. It does not exist.

**VERDICT for `P H11` and the nine write rows above it: TRUE BUT CHANGEABLE,
at the cost of one operator action** -- exactly the `ADMIN-RIGHTS-NOT-HELD`
shape, and spelled nowhere. Note also that `H11`'s own cell claims nothing at
all (*"no tool, no reason"*); the claim that the section renders was introduced
downstream, in the cost correction, and never had a source.

**And a costing consequence, flagged for whoever owns that blocker rather than
ruled here.** `H6` edit, `H7` unpublish, `H8` link to a Company Page, `H9`
request reviews and `H10` manage reviews all presuppose `H1`. They are costed
as independent writes against a page that does not exist. That is a cost
question, not a write-off question, and it is out of this pass's scope.

*(My own first attempt at this row was weaker and is recorded so the method is
visible: I read `providing services` as 0 in both committed captures of
`/in/me/` and nearly reported the section absent. Those captures also read
`Experience` 0, `Licenses` 0, `Recommendations` 0 and `Activity` 0 -- they are
TOPCARD-SCOPED and never reach the region. A needle that never reached the
region is not a zero, per `jobs.md` row 16. The answer came from the census's
own `H1` cell, not from my needle.)*

### 3.4 The row cells are markedly more honest than the blocker table

A row-level sweep of the four capability slices -- `jobs.md`, `network.md`,
`profile.md`, `messaging-and-content.md` -- pulled every reason cell carrying
an operator, account or world signal: **179 rows** (42 / 42 / 49 / 46).
(`mcp-inventory.md` was excluded on measurement: it is a tool and
evidence-class inventory with none of the census vocabulary, so it has no
capability rows to sweep.)

Of those, **144 sit in a write-off state** (EXCLUDED-RULED, XR, GAP,
MEASURED-ABSENT). Applying s6's predictor at row level:

| | rows | carry a REOPENER in the cell |
|---|---:|---:|
| EXCLUDED-RULED / XR -- rows actually CLOSED with a reason | 86 | **36 (42%)** |
| GAP -- not closed, so none is owed | 55 | 1 |

**42% at row level against 15%-with / 91%-without at blocker level.** The
cells are the better artifact, and the ones that are good are very good --
`jobs.md` 25/29/30 carry the `PANEL-NOT-OBSERVED` control and its reopener
verbatim; `network.md` 136 is MEASURED-ABSENT with two independent sources
named; `network.md` 174 refuses to close on a zero in its own words
(*"A ZERO CANNOT SETTLE THIS ROW"*); `profile.md` L2b says **"NOBODY HAS
LOOKED"** rather than picking a state.

**The contingent problem is concentrated one level up, in the blocker table,
where a single reason cell speaks for 6 or 15 or 30 rows and no row can
contradict it.** `J 40` is the clean case: the census ROW says the field is
the skill's exclusive one, and the BLOCKER reason turned that into "not on any
surface this server reads", which is the sentence this repo's own fixtures
refute.

*(Instrument note, because the sweep's own count moved: the first pass matched
`"has no"` inside `"has none"` and `"not a"` inside `"not at all"`, and the
settings-family boilerplate `"a setting is admitted by name or not at all"`
alone contributed ~33 rows of pure artifact. Word-boundary regexes removed 33
and added 0. The 179 above is the corrected figure.)*

### 3.5 Why the reopener predictor works: 34 blockers' reasons are UNREACHABLE from the blocker table

A second sweep took every one of the 95 blockers in `blocker-map.tsv` and
harvested its reason prose from the seven documents a reader starting at the
blocker table would reach:

    2026-09-03-linkedin-gap-blockers.md    2026-09-05-blocker-map.md
    2026-09-05-decide-retire-rulings.md    2026-09-19-blocker-table-refresh.md
    2026-09-19-blocker-conflicts.md        2026-09-19-the-four-absent-blockers.md
    2026-09-05-routes-already-admitted.md

**It found no reason for 34 of them -- 100 rows, 86 of them still GAP.**

**That result is a claim about the CORPUS, not about the blockers, and I
measured the difference rather than reporting the headline.** Re-run over every
`.md` under `_audit/` INCLUDING the slice-specific audit documents:

    named SOMEWHERE outside the seven : 34
    named NOWHERE at all              :  0

**Not one is orphaned.** Every reason exists. `SERVICES-PAGE-SURFACE` is the
clean example: NO-REASON-FOUND in the seven, and two careful rulings about it
in `2026-09-05-lead-rulings-round-two.md` s4 and `2026-09-05-network-tail.md`
s3 -- the second of which corrects its own cost in the same session. I had read
both by hand before this sweep ran, which is how the over-report was caught.

**So the corrected finding, and it is the mechanism under s6.** For 34 of 95
blockers, carrying **100 rows and 86 of the census's 301 remaining GAPs**, the
reason is real, careful, sometimes self-correcting -- and **it cannot be found
from the artifact people actually read.** The blocker table names no corrector;
the corrector names the blocker. A reader who starts at the blocker and stops
at the seven sees a name, a row count, a cost, and no argument.

**That is why a reopener predicts revisiting and a good reason does not.** A
reopener lives IN the blocker's own row. A reason two documents away does not
get re-read, however good it is.

**The cheapest fix is not to rewrite 34 reasons.** It is one column in
`blocker-map.tsv`: `reason_doc`, the document that argues this blocker. The
assignments file already carries `source` and `locator` for the row-to-blocker
mapping; the blocker-to-reason mapping has no such column, which is the entire
gap.

### 3.6 Four blockers carry TWO reasons on different subjects, and the NAME keeps the wrong one

The ledger sweep found four blockers whose reason prose gives two different
subjects. In three of them a CODE reason was later corrected to an ACCOUNT or
WORLD one -- **and the blocker NAME was never changed, so the superseded
reason is the one a reader meets first.**

**`ENDORSE-SUBSTRING-OVERREACH` -- 3 rows, 2 still GAP.** Named for a forbidden
substring, i.e. a fact about our boundary. Corrected in
`routes-already-admitted.md`: the substring appears *"at exactly one site in
`linkedin_server/` -- its own entry in the tuple"*, and

> *"what stops these rows is that LinkedIn draws no endorsement line for this
> account to read, which is a measurement, where the substring was an
> inference. The rows stay blocked and the reason changes"*

The correction is exemplary and its consequence was not followed through:
**"no endorsement line for this account" is CONTINGENT.** One endorsement
received and the line is drawn. That is TRUE-BUT-CHANGEABLE at a cost nobody
here controls but nobody here has named either, and the blocker is still
called `ENDORSE-SUBSTRING-OVERREACH`.

**`OPEN-TO-HIRING-MODAL` -- 5 rows, 5 still GAP.** Two reasons: a CODE one
(*"50 rows sit behind a control on a page this server already loads and already
parses ... none has ever been opened"*) and an ACCOUNT one, *"`P J4` IS
UNVERIFIABLE ON THIS ACCOUNT, AND THAT IS THE POINT OF LISTING IT."* The
account reason is the binding one and it is contingent: the #Hiring state
becomes verifiable the moment he turns #Hiring on. Same shape as
`ADMIN-RIGHTS-NOT-HELD`, and unspelled.

**`PARSER-ON-A-LOADED-PAGE` -- 2 rows, 0 still GAP.** Ranked as *"the cheapest
BUILD in the document: zero extra page loads, zero boundary change, zero
ruling"*, then corrected 900 lines later: *"`N 118` is not a missing parser. It
is a line LinkedIn does not draw."* Resolved, and worth keeping as the pattern:
**a cheap-BUILD costing is the most likely place for a contingent fact to hide,
because nobody audits a cheap row.**

**`CONTACT-IMPORT` -- 5 rows, 0 still GAP.** Two reasons, both correct and both
retired: a WORLD one (mobile address-book flow, no address book to offer) and a
CODE one (a shipped ruling about driving a form on another party's domain).
Sound; listed for completeness.

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

## 6. THE PREDICTOR: A REOPENER IS WHAT MAKES A WRITE-OFF GET REVISITED

The lead's pattern has been an anecdote -- three instances, found one at a
time, by somebody happening to look. This makes it a measurement with a named
remaining queue.

**THE QUESTION.** Of the 26 blockers whose NAME asserts an operator, account or
world fact (s3.1), which ones have a REOPENER recorded anywhere in the
committed audit -- a stated condition under which the write-off comes back?

**THE INSTRUMENT, and its error bars, because it has them.** Search every
committed `.md` under `_audit/` for each blocker name and look for a
`REOPEN*` marker. Resolution decides the answer, so it was run at two:

* **STRICT** -- the marker must be on the SAME LINE as the blocker name. This
  is the resolution of the artifact that actually carries reopeners: the table
  in `decide-retire-rulings.md` s6 puts blocker and reopener in one table row.
* **LOOSE** -- within 6 lines. This OVER-reports, and the receipt is
  `MATCH-DETAILS-COLLAPSED`: it read YES off a `REOPENER: nothing that keeps
  the shape` sentence five lines above that belongs to `PAID-BOOST`.

|  | blockers | rows | still GAP | share |
|---|---:|---:|---:|---:|
| **STRICT** -- with a reopener | 13 | 34 | 5 | **15%** |
| **STRICT** -- without | 13 | 45 | 41 | **91%** |
| LOOSE -- with a reopener | 16 | 43 | 14 | 33% |
| LOOSE -- without | 10 | 36 | 32 | 89% |

**The conclusion survives the instrument's own error in both directions.** The
loose pass credits reopeners that are not there, which biases AGAINST the
finding, and the gap is still 89% versus 33%.

**AND THE CONVICTION RATE IS 5 OF 5.** Every contingent write-off yet found
wrong sits in the STRICT no-reopener set:

| instance | blocker | found by |
|---|---|---|
| 1 | `ADMIN-RIGHTS-NOT-HELD` | the lead, 2 days ago |
| 2 | `PREMIUM-JOBS-SURFACES` | the lead (Premium held since 2026-08-30) |
| 3 | `PREMIUM-READER-NOT-BUILT` (`J 127`) | re-opened this morning |
| 4 | `SERVED-BY-GMAIL-SKILL` | s1 of this document |
| 5 | `OWNED-BY-A-SIBLING-SLICE` | s2 of this document |

Not one was in the set that carries reopeners. **A reopener is not paperwork.
It is the only thing that has ever caused one of these to be looked at again.**

**THE REMAINING QUEUE, and it is small enough to finish.** Eight blockers in
the no-reopener set have not been tested by anybody -- **16 rows, 13 still
GAP**:

| blocker | rows | still GAP | the contingent claim to test |
|---|---:|---:|---|
| `MATCH-DETAILS-COLLAPSED` | 5 | 5 | is the panel collapsed, or not drawn for this account? |
| `ANALYTICS-CONTROLS-UNPRESSED` | 4 | 3 | unpressed by us, or absent for him? |
| `ACCOUNT-VERIFICATION` | 2 | 2 | already self-flagged: *"the address is ASSUMED and this is NOT machine-verified"* |
| `AUDIO-EVENTS-EXISTENCE` | 1 | 1 | does the product exist, or was it never looked for? |
| `LEARNING-CERTIFICATE` | 1 | 1 | contingent on a course he has or has not taken |
| `VIDEO-MEETING-INTEGRATION` | 1 | 1 | contingent on a third-party account being linked |
| `OPEN-PROFILE-SETTING` | 1 | 0 | closed; reopener still owed |
| `THIRD-PARTY-PROFILE-FORBIDDEN` | 1 | 0 | closed by OUR ruling; permanent, but say so |

**AND TWO MORE THAT THE NAME-LEVEL SWEEP COULD NOT SEE**, found by the
reason-level sweep instead (s3.6) -- which is why both were run:

| blocker | rows | still GAP | the contingent claim, and where it is hidden |
|---|---:|---:|---|
| `OPEN-TO-HIRING-MODAL` | 5 | 5 | *"UNVERIFIABLE ON THIS ACCOUNT"* -- becomes verifiable when he turns #Hiring on. Name says CODE |
| `ENDORSE-SUBSTRING-OVERREACH` | 3 | 2 | *"LinkedIn draws no endorsement line for this account"* -- one endorsement received and it is drawn. Name says CODE |

**A blocker named for a code fact can hold an account fact, and the name is
what everybody reads.** That is 8 more rows, 7 still GAP, on top of the queue
above -- and it means the name-level classification in s3.1 is a FLOOR, not a
census.

**RECOMMENDED STANDING RULE, one line, and it is the cheapest thing in this
document.** *A write-off whose reason asserts a fact about the operator, his
account or the world may not be filed without a REOPENER and the name of who
can establish it.* The census already enforces it on one queue. Extending it
costs nothing and is the only measure above that prevents instance 6.

---

## 7. WHAT THIS PASS DID NOT DO

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
6. **s3.1's name-level classification is a FLOOR.** s3.6 found two contingent
   blockers wearing code-fact names, so the 26 is an undercount by at least
   two and the SURFACE? class of 22 is a guess about names, not a measurement
   of reasons.
7. **The reopener scan is a text search and can be fooled both ways.** Its
   over-reporting receipt is in s6 (`MATCH-DETAILS-COLLAPSED` at a 6-line
   window). It can also under-report: a reopener written as a condition
   without the word would read as absent. Both bounds are published.

---

## 8. PROVENANCE, AND THE ARTIFACTS

Everything here is re-runnable offline. Nothing needs a session or a mailbox.

| artifact | what it is |
|---|---|
| `tests/test_proximity_is_on_a_read_surface.py` | the only thing that ships; 6 tests, shown failing 4 of 4 |
| `_audit/_scratch/_contingent-census-sweep.tsv` | 179 row-level reason cells + 1 exclusion marker, over four slices |
| `_audit/_scratch/_contingent-ledger-sweep.tsv` | 99 blocker-level reasons over 95 blockers, classified by subject |
| `_audit/_scratch/_cw-writeoffs.tsv` | the 144 of those 179 in a write-off state |

The scratch TSVs are gitignored by design and are inputs, not conclusions --
every number quoted above was re-derived from them in this document and each
one is reproducible from the committed census.

**One hygiene note, corrected before it was reported as a finding.** This
document first quoted the skill's location as an ABSOLUTE path, which carries a
real name, and the commit passed. My first inference was the known worktree
scar -- a gate disarmed because its key is gitignored. **Measured instead of
reported:** `sweep_tracked_for_identity.py` resolves `KEY_PATH` against the
MAIN repo, not the worktree, so the key is present and the gate runs ARMED here
(`PASS: 0 hits across 544 swept files`, 218 spellings, 16 classes). The token
is on the key's own `_ignore_values` list, deliberately, because it is
unavoidable in the absolute Windows path that `ci.yml`, `pyproject.toml` and
two tests already carry. **So the gate behaved correctly and the scar does not
reproduce here.** The path is now written repo-relative anyway, because the
instruction is about tracked files rather than about what a gate catches.

**What was run, and what was deliberately not.** Read: `blocker-map.tsv`,
`blocker-assignments.tsv`, the four census slices, the ledger documents, the
skill's own source and fixtures, `linkedin_server/readonly.py`,
`shape.py`, `dom.py`, and 20 committed HTML captures. Executed: the skill's
three selftests, `parse_digest --json` and `referral_join --json` over their
own fixtures, `readonly.is_read_url` over nine addresses by import, and the
guard's own mutation harness. **Not executed: any browser, any LinkedIn page
load, any mailbox read, any write, `build_blocker_map.py --write`.** No census
row was moved and `readonly.py` was not edited.
