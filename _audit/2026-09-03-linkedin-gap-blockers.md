# The 409 gaps are 97 blockers

**THE NUMBER: 97.** Every one of the census's 409 GAP rows was walked and
assigned exactly one BLOCKER ID -- the earliest thing that stops it -- and the
distinct blockers count 97. Not 409 decisions. Not 20 either.

The count alone still under-serves the question, because the distribution is
the finding:

| rows a blocker gates | how many blockers | rows |
|---:|---:|---:|
| 1 | 32 | 32 |
| 2 | 16 | 32 |
| 3 | 12 | 36 |
| 4 | 10 | 40 |
| 5 | 9 | 45 |
| 6-8 | 7 | 46 |
| 10-16 | 7 | 89 |
| 18-32 | 4 | 89 |
| | **97** | **409** |

**The 15 biggest blockers gate 206 rows -- half the census. The smallest 32
gate one row each.** So the honest answer to "is this 409 decisions or 20" is:
it is about a dozen decisions that matter and eighty-five that do not, and the
dozen are named below.

Read-only work. No browser, no LinkedIn session, no page load, no
`mcp__linkedin__*` call. One file created, nothing tracked was edited, nothing
committed.

---

## 1. HOW THE ROW SET WAS ESTABLISHED, BEFORE ANY CLASSIFYING

A scan compared against nothing publishes its own blind spots as absence, so
the expected total was derived first, from each slice's own section-1 count
table, summed by hand:

    jobs.md                     GAP  99  (of 150)
    profile.md                  GAP  79  (of 260)
    messaging-and-content.md    GAP 109  (of 142)
    network.md                  GAP 107 in-scope + 15 admin-only = 122 (of 209)
    ---------------------------------------------------------------------
    EXPECTED                        409  (of 761)

Then every markdown table row in the four slices was parsed structurally and
its state column read. Result, per file:

    jobs.md      151 table rows -> GAP  99   MATCH
    profile.md   202 table rows -> GAP  79   MATCH
    messaging    143 table rows -> GAP 109   MATCH
    network.md   209 table rows -> GAP 122   MATCH
    ----------------------------------------------
                 705 table rows -> GAP 409   MATCH

705 table lines rather than 761 capabilities because `profile.md` collapses two
blocks: `O6-O20` is ONE line standing for 15 capabilities and the `P-R` block is
ONE line (`P1`) standing for 45. Both collapsed blocks are argued
EXCLUDED-RULED in their own prose, so no GAP hides inside either.
705 + 14 + 44 = 763, less two stateless rows (jobs 58 bulk-unsave, which
LinkedIn does not offer, and one messaging row) = 761. The arithmetic closes on
both axes.

The classifier consumes the same parse and asserts on itself: **409 GAP rows
in, 409 assigned, 0 unassigned, 0 assigned-but-not-a-GAP, and the assignment
function raises on any double-assignment.**

**ROW IDS IN THIS DOCUMENT CARRY A SLICE LETTER** -- `J` jobs, `P` profile,
`M` messaging-and-content, `N` network -- because the slices reuse ids.
`P C3` (per-section public visibility) and `M C3` (post a photo) are different
capabilities; so are `P M11` (Resume Builder) and `M M11` (edit a sent
message).

---

## 2. THE BOUNDARY MOVED AFTER THE CENSUS FROZE, AND 29 ROWS ARE NOT WHAT IT SAYS

The census file was written at 15:53 today. Commit `1c08e5f` is stamped
`2026-09-03 15:53:26`. Measured at that commit by AST, and again at HEAD by
importing the module under `venv/Scripts/python.exe`:

| list | at 1c08e5f | at HEAD |
|---|---:|---:|
| `readonly._ALLOWED_URL_PATTERNS` | 22 | **23** |
| `readonly._FORBIDDEN_URL_SUBSTRINGS` | 23 | **33** |
| `readonly.SANCTIONED_MUTATIONS` | 4 | 4 |
| `writes.PERFORMABLE` | 12 | 12 |
| `writes.PERMANENTLY_FORBIDDEN` | 9 | 9 |

**The census's numbers were right when written. The boundary moved after it
froze.** Diffed, the additions are:

    ALLOWLIST +1
      /messaging/compose/?profileUrn=urn%3Ali%3Afsd_profile%3A<id>&recipient=<id>

    FORBIDDEN +10
      /create   /mwlite/   /uas/   cookies   job-application
      password  settings   two-factor   verification   visibility

Those ten are exactly the class the census named in its defect #4. **The class
fix landed.** And `set_input_files` is still absent from `SANCTIONED_MUTATIONS`
-- confirmed at HEAD, not inferred.

Three consequences, each counted:

**(a) 8 rows now meet a written refusal that did not exist this morning.**
Machine-checked with `readonly.assert_read_url` at HEAD, against addresses
quoted VERBATIM in the census rows, with four controls (three must-allow, one
must-refuse; 0 control failures):

| address | newly-biting substring | rows |
|---|---|---|
| `/public-profile/settings` | `settings` | `P B4 C2 C3 C4 C5 C6` |
| `/uas/login` | `/uas/` | `P N12` |
| `/badges/profile/create` | `/create` | `P O5` |

Whether that makes them EXCLUDED-RULED is a judgment the census's own rule
leaves open -- it says a general mechanism that merely happens to block
something is "a GAP with a NAMED BLOCKER, not laundered into a decision", and
these ten substrings were written for the class rather than for the capability.
I have not re-stated the census total on my own authority. I have filed the
8 rows under `FORBIDDEN-CLASS-FIX-LANDED` with cost 0, and the ruling is the
lead's.

**(b) 7 rows were BUILT after the census froze,** read off tool docstrings at
HEAD rather than off any agent's report: `linkedin_job_detail.insights` now
carries `J 24` (responses managed off LinkedIn), `J 26` (promoted),
`J 27` (verification badge), `J 121` and `J 122` (applicant insights), plus
`J 123` (company insights) as a bonus; `linkedin_who_viewed_me.insights` now
carries `N 135` (the trend chart, as LinkedIn's own description of it).

**(c) 14 rows depend on measurements the census reports differently.** See
section 6.

**So 409 was true at 15:53 and is not true now.** Every number in this document
is against the census's own frozen row set, because that is the only set anybody
can audit; the delta above is stated separately rather than folded in.

---

## 3. THE RANKED TABLE

**COST MODEL, stated so it can be argued with rather than believed.**

    cost = A + C + P + D + T + 3*W + R

      A  new allowlist patterns
      C  new surface captures (a page or menu nobody here has opened)
      P  new parsers
      D  boundary LISTS needing an exemption or edit -- one per list, not per entry
      T  tools written or edited
      W  a new WriteSpec + gate + consent text, costed 3, once per blocker
      R  an operator ruling
      cost 0  nothing to build: already closed, already refused by a written
              rule, already served elsewhere, or belongs to another slice

The unit is a NAMED ARTIFACT this repo has produced before, so the numbers are
commensurable with its own history. They are not hours.

**MERGE RULE, because it decides the count of 97:** two blockers merge only
when THE SAME SINGLE ACTION closes both. Different surfaces stay different
blockers. That is why the tail is long, and it is deliberate -- a single
"no allowlist pattern" blocker gating 189 rows would predict no effort at all.

**ASSIGNMENT RULE:** one blocker per row, the EARLIEST binding constraint. A
row that looks blocked by a missing write but has no way to find its target is
filed against the missing surface, not the missing write.

| # | blocker | rows | R/W | boundary | ruling | cost | rows/cost | queue |
|---|---|---:|---|---|---|---:|---:|---|
| 1 | `FILE-UPLOAD-UNSANCTIONED` | 16 | 1R/15W | none | YES | 1 | 16.00 | DECIDE |
| 2 | `AI-INTERVIEW-PRODUCT` | 14 | 4R/10W | none | YES | 1 | 14.00 | DECIDE-RETIRE |
| 3 | `JOB-SEARCH-PARAMS` | 6 | 6R | none | no | 1 | 6.00 | BUILD |
| 4 | `MESSAGING-SETTINGS` | 5 | 5W | none | YES | 1 | 5.00 | DECIDE-RETIRE |
| 5 | `CONTACT-IMPORT` | 5 | 5W | none | YES | 1 | 5.00 | DECIDE-RETIRE |
| 6 | `SEARCH-RESULTS-SURFACE` | 21 | 19R/2W | allowlist +1 | YES | 5 | 4.20 | DECIDE |
| 7 | `GROUPS-SURFACE` | 32 | 12R/20W | allowlist +2, WriteSpec | YES | 10 | 3.20 | MEASURE |
| 8 | `PANEL-NOT-OBSERVED` | 3 | 2R/1W | none | no | 1 | 3.00 | MEASURE |
| 9 | `HELP-CENTER-FORM` | 3 | 3W | none | YES | 1 | 3.00 | DECIDE-RETIRE |
| 10 | `OFF-PLATFORM-WIDGET` | 3 | 2R/1W | none | YES | 1 | 3.00 | DECIDE-RETIRE |
| 11 | `HASHTAG-EXISTENCE` | 3 | 1R/2W | none | no | 1 | 3.00 | MEASURE |
| 12 | `COMPANY-PAGE-SURFACE` | 18 | 13R/5W | allowlist +1, WriteSpec | no | 9 | 2.00 | BUILD |
| 13 | `EVENTS-SURFACE` | 18 | 7R/11W | allowlist +1, WriteSpec | YES | 9 | 2.00 | MEASURE |
| 14 | `LIVE-BROADCAST` | 2 | 2W | none | YES | 1 | 2.00 | DECIDE-RETIRE |
| 15 | `AI-ASSIST-MESSAGING` | 2 | 2W | none | YES | 1 | 2.00 | DECIDE-RETIRE |
| 16 | `MENTION-COMPOSITION-RULING` | 2 | 2W | none | YES | 1 | 2.00 | DECIDE |
| 17 | `CONVERSATION-OVERFLOW-MENU` | 10 | 1R/8W/1RW | WriteSpec | no | 6 | 1.67 | MEASURE |
| 18 | `MATCH-DETAILS-COLLAPSED` | 5 | 5R | none | YES | 3 | 1.67 | DECIDE |
| 19 | `NEWSLETTER-SURFACE` | 12 | 1R/11W | allowlist +2, WriteSpec | no | 8 | 1.50 | BUILD |
| 20 | `OPEN-TO-WORK-MODAL` | 11 | 11W | denylist x1, WriteSpec | YES | 8 | 1.38 | MEASURE |
| 21 | `SERVICES-PAGE-SURFACE` | 11 | 1R/10W | allowlist +1, WriteSpec | YES | 8 | 1.38 | DECIDE |
| 22 | `INTRO-EDITOR-UNREAD-CONTROLS` | 4 | 4W | none | no | 3 | 1.33 | MEASURE |
| 23 | `ANALYTICS-CONTROLS-UNPRESSED` | 4 | 4R | none | YES | 3 | 1.33 | DECIDE |
| 24 | `CONTENT-ANALYTICS-SURFACE` | 5 | 5R | allowlist +1 | no | 4 | 1.25 | BUILD |
| 25 | `CREATOR-HUB-SURFACE` | 4 | 4R | allowlist +1 | no | 4 | 1.00 | BUILD |
| 26 | `PARSER-ON-A-LOADED-PAGE` | 2 | 2R | none | no | 2 | 1.00 | BUILD |
| 27 | `DEVICE-GEOLOCATION` | 1 | 1R | none | YES | 1 | 1.00 | DECIDE-RETIRE |
| 28 | `MOBILE-APP-ONLY` | 1 | 1W | none | YES | 1 | 1.00 | DECIDE-RETIRE |
| 29 | `AUDIO-EVENTS-EXISTENCE` | 1 | 1W | none | no | 1 | 1.00 | MEASURE |
| 30 | `SIGNIN-INTERSTITIAL` | 1 | 1R | none | YES | 1 | 1.00 | DECIDE-RETIRE |
| 31 | `NO-URL-AT-ALL` | 1 | 1W | none | no | 1 | 1.00 | MEASURE |
| 32 | `NOTIFY-COST-UNMEASURED` | 1 | 1R | none | no | 1 | 1.00 | MEASURE |
| 33 | `VOICE-CAPTURE` | 1 | 1W | none | YES | 1 | 1.00 | DECIDE-RETIRE |
| 34 | `MISSING-PARAM-MESSAGING` | 1 | 1R | none | no | 1 | 1.00 | BUILD |
| 35 | `PAID-BOOST` | 1 | 1W | none | YES | 1 | 1.00 | DECIDE-RETIRE |
| 36 | `JOB-ALERTS-SURFACE` | 7 | 7W | allowlist +1, denylist x1, WriteSpec | no | 8 | 0.88 | BUILD |
| 37 | `ARTICLE-SURFACE` | 6 | 1R/5W | allowlist +1, WriteSpec | no | 7 | 0.86 | BUILD |
| 38 | `CONTACT-INFO-PANEL` | 5 | 1R/4W | WriteSpec | no | 6 | 0.83 | MEASURE |
| 39 | `RECOMMENDATIONS-SURFACE` | 6 | 1R/5W | allowlist +1, WriteSpec | YES | 8 | 0.75 | DECIDE |
| 40 | `SCHOOL-PAGE-SURFACE` | 3 | 3R | allowlist +1 | no | 4 | 0.75 | BUILD |
| 41 | `PREMIUM-JOBS-SURFACES` | 3 | 3R | allowlist +1 | no | 4 | 0.75 | BUILD |
| 42 | `OPEN-TO-HIRING-MODAL` | 5 | 1R/4W | WriteSpec | YES | 7 | 0.71 | MEASURE |
| 43 | `BADGES-SURFACE` | 5 | 2R/3W | allowlist +1, WriteSpec | no | 7 | 0.71 | BUILD |
| 44 | `FEED-ITEM-OVERFLOW-MENU` | 5 | 5W | WriteSpec | YES | 7 | 0.71 | MEASURE |
| 45 | `GROUP-CHAT-SURFACE` | 4 | 4W | WriteSpec | no | 6 | 0.67 | BLOCKED |
| 46 | `POST-COMMENT-CONTROLS` | 4 | 1R/3W | WriteSpec | no | 6 | 0.67 | MEASURE |
| 47 | `COMMENT-IDENTIFIER` | 4 | 4W | WriteSpec | no | 6 | 0.67 | BLOCKED |
| 48 | `ALL-FILTERS-PANEL` | 2 | 2R | none | no | 3 | 0.67 | MEASURE |
| 49 | `FEED-CONTENT-READ-RULING` | 2 | 2R | none | YES | 3 | 0.67 | DECIDE |
| 50 | `MESSAGE-REQUESTS-SURFACE` | 4 | 1R/3W | allowlist +1, WriteSpec | no | 7 | 0.57 | BUILD |
| 51 | `COLLABORATIVE-CONTENT` | 4 | 4W | allowlist +1, WriteSpec | no | 7 | 0.57 | BUILD |
| 52 | `PEOPLE-FOLLOW-LISTS` | 4 | 3R/1W | allowlist +2, denylist x1, WriteSpec | no | 8 | 0.50 | BUILD |
| 53 | `SEARCH-APPEARANCES-SURFACE` | 2 | 2R | allowlist +1 | no | 4 | 0.50 | BUILD |
| 54 | `RESUME-TOOLS-SURFACE` | 2 | 1R/1RW | allowlist +1 | no | 4 | 0.50 | BLOCKED |
| 55 | `COMPANY-ID-RESOLVER` | 1 | 1R | none | no | 2 | 0.50 | BUILD |
| 56 | `PREMIUM-READER-NOT-BUILT` | 1 | 1R | none | no | 2 | 0.50 | BUILD |
| 57 | `MESSAGE-ADDRESSING` | 1 | 1W | none | no | 2 | 0.50 | MEASURE |
| 58 | `PROFILE-PDF-DOWNLOAD` | 1 | 1R | none | YES | 2 | 0.50 | DECIDE |
| 59 | `PUBLISH-POST-AUDIENCE-PARAM` | 1 | 1W | none | no | 2 | 0.50 | BUILD |
| 60 | `INVITE-NOTE-PARAM` | 1 | 1W | none | YES | 2 | 0.50 | DECIDE |
| 61 | `PREMIUM-APPLY-SURFACES` | 5 | 1R/4W | allowlist +2, WriteSpec | YES | 11 | 0.45 | BUILD |
| 62 | `TRACKER-ROW-MENU` | 3 | 3W | denylist x1, WriteSpec | no | 7 | 0.43 | BLOCKED |
| 63 | `ENDORSE-SUBSTRING-OVERREACH` | 3 | 1R/2W | denylist x1, WriteSpec | YES | 7 | 0.43 | DECIDE |
| 64 | `MENTION-TAG-CONTROLS` | 3 | 3W | allowlist +1, WriteSpec | no | 7 | 0.43 | BUILD |
| 65 | `JOBCARD-OVERFLOW-MENU` | 2 | 2W | WriteSpec | no | 6 | 0.33 | MEASURE |
| 66 | `THREAD-REPLY-BOX` | 2 | 2W | WriteSpec | no | 6 | 0.33 | MEASURE |
| 67 | `PER-MESSAGE-OVERFLOW-MENU` | 2 | 2W | WriteSpec | no | 6 | 0.33 | MEASURE |
| 68 | `PICKER-SURFACES` | 2 | 2W | WriteSpec | no | 6 | 0.33 | MEASURE |
| 69 | `POLL-SURFACE` | 2 | 2W | WriteSpec | no | 6 | 0.33 | MEASURE |
| 70 | `EASY-APPLY-MULTISTEP` | 1 | 1W | none | YES | 3 | 0.33 | DECIDE |
| 71 | `ADD-SECTION-MENU` | 1 | 1R | none | no | 3 | 0.33 | MEASURE |
| 72 | `MULTILANG-PROFILE` | 2 | 1R/1W | allowlist +1, WriteSpec | no | 7 | 0.29 | BUILD |
| 73 | `SAVED-POSTS-SURFACE` | 2 | 2W | allowlist +1, WriteSpec | no | 7 | 0.29 | BUILD |
| 74 | `SEARCH-HISTORY-SURFACE` | 2 | 1R/1W | allowlist +1, denylist x1, WriteSpec | no | 8 | 0.25 | BUILD |
| 75 | `JOB-COLLECTIONS-SURFACE` | 1 | 1R | allowlist +1 | no | 4 | 0.25 | BUILD |
| 76 | `MESSAGE-REACTION` | 1 | 1W | WriteSpec | no | 6 | 0.17 | MEASURE |
| 77 | `CELEBRATION-COMPOSER` | 1 | 1W | WriteSpec | no | 6 | 0.17 | MEASURE |
| 78 | `OPEN-PROFILE-SETTING` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 79 | `LEARNING-CERTIFICATE` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 80 | `ACTIVITY-VIEW-SETTING` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 81 | `FOUND-A-JOB-FLOW` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 82 | `VIDEO-MEETING-INTEGRATION` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 83 | `REPORTING-FLOWS` | 1 | 1W | WriteSpec | YES | 7 | 0.14 | MEASURE |
| 84 | `POST-DRAFT-SURFACE` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 85 | `FEED-PREFERENCES` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 86 | `EMBED-SETTING` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 87 | `SKILL-PAGE-SURFACE` | 1 | 1W | allowlist +1, WriteSpec | no | 7 | 0.14 | BUILD |
| 88 | `INMAIL-COMPOSE-SURFACE` | 1 | 1W | allowlist +1, WriteSpec | YES | 8 | 0.12 | BLOCKED |

**The nine with cost 0 -- nothing to build:**

| blocker | rows | queue | why |
|---|---:|---|---|
| `ADMIN-RIGHTS-NOT-HELD` | 15 | NOT-OURS | He administers no Page, owns no group, organises no event. Not a capability he holds either |
| `FORBIDDEN-CLASS-FIX-LANDED` | 8 | RE-FILE | Machine-verified refused at HEAD by substrings added after the census froze |
| `CLOSED-SINCE-CENSUS` | 7 | RE-FILE | Built and committed after 15:53 today |
| `SERVED-BY-GMAIL-SKILL` | 6 | NOT-OURS | Available to him today through `linkedin-jobs`, with no LinkedIn session at all |
| `OWNED-BY-A-SIBLING-SLICE` | 4 | RE-FILE | `N 149 150 151 160` -- network records these as owned by the messaging slice, and messaging counts them too |
| `JOBS-APPLICATION-FORBIDDEN` | 3 | RE-FILE | `/jobs/application` is the FIRST entry on the forbidden tuple, and the same slice cites it as EXCLUDED-RULED for rows 74-77 |
| `ACCOUNT-VERIFICATION` | 3 | RE-FILE | The new `verification` substring probably bites -- but no row names a url, so the address is ASSUMED and this is NOT machine-verified |
| `INVITATION-SUBSTRING-BLOCKED` | 3 | RE-FILE | `/invite` and `invitation` are forbidden substrings and the network slice's R2 is written for exactly these |
| `THIRD-PARTY-PROFILE-FORBIDDEN` | 1 | RE-FILE | `PERMANENTLY_FORBIDDEN[load_a_third_partys_profile_to_measure_a_control]` reaches it; the row records the collision itself |

---

## 4. THE THREE QUEUES, WHICH ARE NOT ONE ROADMAP

Conflating a decision with a build is how a roadmap becomes a wish. Each
blocker's queue is the FIRST thing that must happen, not the whole path.

| queue | blockers | rows | what it means |
|---|---:|---:|---|
| **MEASURE** | 25 | 120 | A capture is missing. No design is possible until a menu, modal or panel has been rendered and read once |
| **BUILD** | 34 | 113 | Engineering only. No ruling needed, the shape is known |
| **DECIDE** | 12 | 73 | Needs his answer. Engineering is blocked behind it, or would be wasted without it |
| **DECIDE-RETIRE** | 12 | 39 | Needs his answer, and the answer is almost certainly "no" -- the ruling RETIRES the rows to EXCLUDED-RULED rather than delivering them |
| **RE-FILE** | 7 | 29 | Nothing to do but correct the census |
| **NOT-OURS** | 2 | 21 | Not this server's to hold |
| **BLOCKED** | 5 | 14 | Waiting on another blocker |
| | **97** | **409** | |

**DECIDE-RETIRE is the cheapest work in this document and the least
satisfying.** Twelve rulings costing one answer each convert 39 rows from
"nobody considered it" to "somebody wrote down why not". That does not move the
proven count by one. It moves 39 rows out of the number that has been read all
day as an indictment -- and it is honest, because the reasons are real: a live
audio session in a separate product, a mobile-only OAuth import, a third-party
streaming tool, a Help Center form, a capability that costs currency.

**CORRECTED BY:** `_audit/2026-09-05-decide-retire-rulings.md` -- the queue was ruled and it converts 37 rows rather than 39, and the answer was not no for all twelve: three rows of AI-INTERVIEW-PRODUCT (the READ side, a past session's readiness score, summary and transcript) and two of OFF-PLATFORM-WIDGET (both reads drawn on a LinkedIn page) meet no reason that retires them and are handed back as gaps under two new blocker names, while five of the 37 are a RE-FILE against a ruling that already existed rather than a new decision.

---

## 5. WHAT TO DO NEXT

**Ranked by rows that could become REACHABLE per unit cost** -- retire-rulings,
re-files and not-ours removed, because they do not add coverage:

| | blocker | rows | cum | cost | ratio | queue |
|---|---|---:|---:|---:|---:|---|
| 1 | `FILE-UPLOAD-UNSANCTIONED` | 16 | 16 | 1 | 16.00 | DECIDE |
| 2 | `JOB-SEARCH-PARAMS` | 6 | 22 | 1 | 6.00 | BUILD |
| 3 | `SEARCH-RESULTS-SURFACE` | 21 | 43 | 5 | 4.20 | DECIDE |
| 4 | `GROUPS-SURFACE` | 32 | 75 | 10 | 3.20 | MEASURE |
| 5 | `PANEL-NOT-OBSERVED` | 3 | 78 | 1 | 3.00 | MEASURE |
| 6 | `HASHTAG-EXISTENCE` | 3 | 81 | 1 | 3.00 | MEASURE |
| 7 | `COMPANY-PAGE-SURFACE` | 18 | 99 | 9 | 2.00 | BUILD |
| 8 | `EVENTS-SURFACE` | 18 | 117 | 9 | 2.00 | MEASURE |
| 9 | `MENTION-COMPOSITION-RULING` | 2 | 119 | 1 | 2.00 | DECIDE |
| 10 | `CONVERSATION-OVERFLOW-MENU` | 10 | 129 | 6 | 1.67 | MEASURE |
| 11 | `MATCH-DETAILS-COLLAPSED` | 5 | 134 | 3 | 1.67 | DECIDE |
| 12 | `NEWSLETTER-SURFACE` | 12 | 146 | 8 | 1.50 | BUILD |

**Twelve blockers reach 146 of the 409.** The remaining 59 costed blockers
share 160 rows between them at ratios from 1.38 down to 0.12.

### The handful, with what each actually buys

**1. `FILE-UPLOAD-UNSANCTIONED` -- 16 rows, ONE ANSWER, and be precise about
what the answer buys.** `set_input_files` is on the mutation-pattern list and
in no sanction. `tests/test_readonly.py:310-341` carries the full argument,
scans every module, plants a mutation to prove the pattern still bites, and
asserts the kind absent from `SANCTIONED_MUTATIONS` BY NAME. Nothing needs
measuring. **But a yes does not ship 16 capabilities -- it unblocks them.**
Each still needs its composer surface afterwards, and 8 of the 16 sit on the
post and message composers this repo has already captured, which is why the
answer is worth having early rather than late. The rows:
`J 70 146 147 148 149`, `M C3 C4 C5 C6 C7 C27 C45 C86 M14 M15 M18`.

**2. `JOB-SEARCH-PARAMS` -- 6 rows, one tool, no new surface, no capture, no
permission.** Six `_WORKPLACE`-style dicts and six `params.append` in
`linkedin_search_jobs`: `f_AL` Easy Apply, `f_JT` job type, `f_EA` under ten
applicants, `f_JIYN` in-network, `f_FCE` fair chance, plus multiple
simultaneous locations. **The highest-certainty item in the census, and the
only one that improves his actual job search this week.** Rows
`J 9 11 12 13 14 151`. The company filter `J 10` sits one blocker along
(`COMPANY-ID-RESOLVER`) because `f_C` needs a numeric id and a posting only
gives a slug.

**3. `SEARCH-RESULTS-SURFACE` -- 21 rows and the biggest structural hole.**
Job search is the only search: `/search/results/` has no address on the
allowlist in any vertical. Nineteen of the 21 are pure reads, and
`shape.parse_person_card` ALREADY EXISTS and `who_viewed_me` uses it live, so
the parser half is done. **It is queued DECIDE, not BUILD**, because a results
page renders people who did not choose to be seen by him -- the same question
`who_viewed_me`'s emission ruling and
`PERMANENTLY_FORBIDDEN[load_a_third_partys_profile_to_measure_a_control]`
already answered for two other surfaces, and it should be answered once for
this one rather than inherited by accident.

**CORRECTED BY:** `_audit/2026-09-05-search-results-consent.md` -- the parser-half claim above is an assumption about a page nobody here has captured, so this item's cost is one piece larger than 5; the ruling itself is prepared there, over 19 reads rather than 21 rows

**4. `GROUPS-SURFACE` -- 32 rows, the single largest blocker in the census.**
`/groups/` is on neither list and returns zero grep hits across the whole
package. Twelve of the 32 are reads, including the only member directory this
server could plausibly reach without loading a third party's profile
(`N 165`, a group's member list). It is queued MEASURE, and it carries a real
ruling inside it: **posting in a group is a second broadcast route with a
different audience, and it should be treated as `publish_post`'s equal in risk,
not a lesser case.**

**CORRECTED BY:** `_audit/2026-09-05-groups-events-precondition.md` -- the zero-groups possibility is closed by measurement; he belongs to five and these 32 rows stand.

This entry, and the costed proposal that grew out of it, treat "he belongs to
zero groups" as live -- an answer that would make 29 of these 32 rows
unreachable in principle and leave a three-row blocker. Measured 2026-09-05 and
it is not the case: five distinct groups on his own Groups page, disjoint from
the five that page calls suggestions, each carrying a per-row management
control the suggestion rows lack. **The 32 rows stand.** The same document
files a MEASURED-ABSENT finding against the Events half, where the assumption
did NOT survive: there is no "events you are registered for" surface at all.

**5. `COMPANY-PAGE-SURFACE` -- 18 rows, and it pays a debt.** `job_detail`
already returns a company Page url and cannot follow it. Thirteen of the 18 are
reads. **It also closes the slug-versus-numeric-id gap behind
`follow_company`'s aiming failure** -- a posting gives a slug, unfollow
addresses a numeric id, nothing resolves one to the other, and a company page
carries both. No ruling needed.

### Two items that outrank their ratio, and should not wait for it

**`PUBLISH-POST-AUDIENCE-PARAM` (rank 59, one row).** Ratio is the wrong
instrument here. `linkedin_publish_post(text, confirm_token)` has no audience
argument and its docstring contains none of the words *audience*, *visibility*,
*Anyone*, *connections only*, *who sees* or *public*. The control was CAPTURED
-- `_audit/2026-08-31-linkedin-perform.md:166`, 31 controls read on an
address already on the allowlist. **The gate tells him how many people may see
a post and never who may.** That is a consent defect on a shipped irreversible
write, and it is a precondition of firing `publish_post`, not a backlog item.
One read, one parameter.

**`PARSER-ON-A-LOADED-PAGE` (rank 26, two rows) is the cheapest BUILD in the
document**: zero extra page loads, zero boundary change, zero ruling. `N 118`
reads endorsement counts off `/in/me/details/skills/`, which
`linkedin_my_profile(include_skills=True)` already loads; `P L2` reads his own
follower count off a page whose value is already quoted inside
`publish_post.residue` ("275 followers") by no tool at all.

---

## 6. WHERE THE THIRTEEN FREE JOB READS WENT, AND WHY THE LATER NUMBER WINS

The census says "13 job read capabilities render on a page
`linkedin_job_detail` ALREADY LOADS". A later measurement says six. **Prefer
the later one**, and the reason is a property of the instrument rather than a
matter of taste: the earlier claim came from reading the census table and
counting rows whose surface is the posting page; the later one came from
grepping two committed captures AND a live posting for each panel by name, and
it found that `Show match details` and `Show Premium Insights` each occur
exactly ONCE in all three renders while the string "How you match" occurs ZERO
times. **The panel is not missing from the page. It is collapsed behind a
control.** A count taken from a table cannot see that; a count taken from the
render can. Resolution, row by row:

| rows | verdict |
|---|---|
| `J 24 26 27 121 122` (+123 as a bonus) | render unpressed. **SHIPPED** -- `CLOSED-SINCE-CENSUS` |
| `J 116 117 118 119 120` | present, COLLAPSED behind `Show match details`. `MATCH-DETAILS-COLLAPSED`, and it needs a ruling: pressing a disclosure control is a different permission from reading a render |
| `J 25 29` | NOT OBSERVED on either capture or on the live posting. `PANEL-NOT-OBSERVED` -- nobody knows whether LinkedIn still draws them, and `J 30` depends on `J 29` |
| `J 28 30` | writes behind a menu, never in the thirteen |

The same correction runs through `who_viewed_me`: the census names "top
companies and top locations"; the live page carries a **Company FILTER** and no
such panel. `N 136` is therefore filed with `N 133 134` under
`ANALYTICS-CONTROLS-UNPRESSED` -- reachable by pressing `Show more analytics`
or a filter pill, on a page the server already opens -- and not as a missing
parser.

---

## 7. WHAT I COULD NOT CLASSIFY, AND WHERE MY INFERENCE CARRIES THE WEIGHT

**Every one of the 409 got a blocker. That is not the same as every one being
evidenced, and the difference is countable.**

**183 of 409 rows carry NO blocker sentence in the census row itself.** For
those, the blocker is MY inference from the capability text plus the boundary
measured at HEAD -- not something read off the page:

| slice | row states a blocker | row is bare |
|---|---:|---:|
| `jobs.md` | 27 | **72** |
| `network.md` | 50 | **72** |
| `messaging-and-content.md` | 76 | 33 |
| `profile.md` | 73 | 6 |
| | 226 | **183** |

`jobs.md` is the least alarming of the two big numbers: its table cell is bare
by format, but its **section 2 states a shape and an R/W for every gap
row-range**, and that prose is what I classified against.

`network.md`'s 72 bare rows, counted by section:

    H. People search and discovery      19   family blocker stated once, on row 79 and in s5
    S. Admin-only                       15   that table has NO note column at all;
                                             the section prose covers all fifteen
    P. LinkedIn Groups                  10
    Q. LinkedIn Events                   8
    F. Following orgs / newsletters      6
    E, I, L, A, M, G (six sections)     14
    ----------------------------------------
                                        72

So 34 of the 72 sit under a family-level blocker sentence even though the row
is bare, and **18 -- the Groups and Events rows recovered on the second pass --
are the softest set in the document**: the slice itself says those families
have "zero prior art in the package" and gives no per-row blocker, so for those
18 my blocker is a surface name and nothing more.

**Four further things I could not settle, each of which would change a count:**

1. **Whether the ten new forbidden substrings convert 8 GAP rows to
   EXCLUDED-RULED.** The refusal is machine-verified; the classification is a
   ruling the census's own rule does not decide (section 2a).
2. **Whether `ACCOUNT-VERIFICATION`'s 3 rows are refused.** The `verification`
   substring almost certainly reaches them, but no census row names a url, and
   I will not invent an address to make a check pass.
3. **Whether `MESSAGING-SETTINGS`' 5 rows were already ruled.** `/psettings/`
   is a forbidden substring and the settings-family ruling is explicitly
   capability-level, which would reach them -- but the messaging slice filed
   them GAP and nothing written names messaging settings.

   **CORRECTED BY:** `_audit/2026-09-05-decide-retire-rulings.md` -- they were already ruled: the settings ruling is quoted in the live linkedin_update_setting docstring at HEAD, a setting is admitted by name or not at all, and the profile slice applied that same ruling to 93 rows as EXCLUDED-RULED while this slice filed five as GAP; the ruling says a setting, not a profile setting, so the five are a RE-FILE and not a decision anybody still owes.
4. **Whether `RECOMMENDATIONS-SURFACE` collides with the network slice's R3.**
   The same capability family is EXCLUDED-RULED under `endorse_or_recommend` in
   `network.md` and GAP in `profile.md`. One of the two slices is wrong and I
   cannot tell which from the text.

**`OWNED-BY-A-SIBLING-SLICE` is a measured double-count**, not a maybe:
`N 149 150 151 160` are recorded BY THE NETWORK SLICE as belonging to messaging,
and messaging counts them again under its own ids. **So 409 is at least 4
over-counted**, and that is the only direction of error I found in the total.

**CORRECTED BY:** `_audit/2026-09-05-decide-retire-rulings.md` -- it is at least 6 and it is not the only direction: the newsletter wave measured two further duplicate pairs that no slice had flagged (M C80 against N 55 plus N 56, and P L4 against M C83, both verified on disk), while A1 subtracted P N12 on an address nothing in this package builds, which is an error in the OTHER direction; its section 9 recomputes the ledger with every movement named and its TAKEN-or-FLAGGED status stated, and applies the duplicates to the 761 denominator, which nobody had done.

**AND 761 IS STILL A FLOOR.** Three passes grew it 661 -> 721 -> 761 and the
covered count never moved once. This document classifies the 409 that exist; it
makes no claim about the ones no pass has found. A blocker gating N rows today
gates more tomorrow, and `GROUPS-SURFACE` and `EVENTS-SURFACE` -- 50 rows
between them, both recovered only on the second pass, both from products whose
Help topic page renders `0 articles` -- are exactly where the next growth will
land.

---

## 8. THE SHAPE UNDER THE 97

Rolled up by kind, the 409 rows are not evenly caused:

| kind | blockers | rows |
|---|---:|---:|
| **NO-ADDRESS** -- the surface exists, nothing admits it | **33** | **189** |
| OUT-OF-SHAPE -- unreachable by a page-reading browser driver | 10 | 32 |
| UNOPENED-MENU / MODAL / PANEL -- loaded page, collapsed control | 12 | 50 |
| RE-FILE -- already refused, closed, or double-counted | 6 | 22 |
| UNSANCTIONED-MUTATION-KIND -- `set_input_files` | 1 | 16 |
| NOT-HELD -- admin rights he does not have | 1 | 15 |
| MISSING-PARAMETER / MISSING-PARSER | 6 | 12 |
| UNPRESSED-CONTROL -- measured present, behind a click | 2 | 9 |
| everything else (14 kinds) | 26 | 64 |

**46% of the census is one sentence in the code: the read allowlist is closed
by default and 33 surfaces are not on it.** But that sentence is not one
decision. It is 33, and they range from `SEARCH-RESULTS-SURFACE` at 21 rows to
`SKILL-PAGE-SURFACE` at one. **A blocker taxonomy that stopped at "the
allowlist is 23 patterns" would gate 189 rows behind a single line and predict
nothing about the work.** That is why the merge rule is one-action-one-blocker.

The second-largest cause is not a rule at all: **50 rows sit behind a control
on a page this server already loads and already parses.** The conversation
overflow menu, the post overflow menu, the contact-info panel, the Open-To-Work
and Open-To-Hiring modals, the All-filters panel, the Add-section menu, the
per-message and job-card menus -- none has ever been opened. Ten of them are
one capture each. **Nobody has been refused these; nobody has looked.**

Of the 409: **263 writes, 143 reads, 2 both, 1 unstated.** The reads are where
the cheap work is -- 43 of the 88 costed blockers need no new WriteSpec at all,
and they carry 141 rows between them.

---

## 9. PROVENANCE

* Row set parsed from `_audit/_census/{jobs,profile,messaging-and-content,network}.md`.
* Boundary measured by importing `linkedin_server.readonly` and
  `linkedin_server.writes` under `venv/Scripts/python.exe` at HEAD, and by AST
  over `git show 1c08e5f:linkedin_server/readonly.py` for the 15:53 baseline.
* URL refusals machine-checked with `readonly.assert_read_url`, four controls,
  0 control failures. **An earlier run of that check failed its controls
  (`/feed/` and `/jobs/search/` reported REFUSED) and was discarded whole
  rather than read; none of its numbers appear above.**
* Shipped-since-census verified by reading tool docstrings in
  `linkedin_server/server.py` at HEAD, not by trusting any agent's report.
* `jobs.md` has no R/W column; its 99 rows were filled from ITS OWN section 2,
  which states R/W per row-range. One row (`J 131`) falls in no range and is
  left unfilled rather than guessed.
* Working log, including the discarded run: `_audit/_scratch/_progress-blockers.md`.
* Nothing was committed. No tracked file was edited.

---

# AMENDMENT A -- 2026-09-03, after team-lead review

**Appended, not merged.** Sections 1-9 above are as published and nothing in
them has been rewritten. The reason to append is the one this repo learned
today: a claim pinned to a moving tip goes false without anybody touching it,
and a document that silently rewrites itself cannot be cited. Every figure
above is true at the commit it names; every figure here is true at `23f04f1`
and says so.

## A1. THE ARITHMETIC: 409 AT THE FREEZE, 390 AT HEAD

    409   GAP rows at 1c08e5f, 2026-09-03 15:53:26
     -8   now meet a written refusal that did not exist at the freeze
     -7   built and committed after the freeze
     -4   double-counted: network carries them, messaging counts them too
    ----
    390   at 23f04f1

Each subtraction, named and machine-checked:

**-8, RULED EXCLUDED-RULED** (team-lead ruling, this review). They meet the
census's own definition -- an entry on `readonly._FORBIDDEN_URL_SUBSTRINGS`
that bears on the capability -- and the class fix that produced them is exactly
the defect the census itself named as its #4. They are not gaps; they are the
census working. Verified with `readonly.assert_read_url` at `23f04f1`, four
controls, 0 control failures:

| address | substring, added post-freeze | rows |
|---|---|---|
| `/public-profile/settings` | `settings` | `P B4 C2 C3 C4 C5 C6` |
| `/uas/login` | `/uas/` | `P N12` |
| `/badges/profile/create` | `/create` | `P O5` |

**CORRECTED BY:** `_audit/2026-09-05-routes-already-admitted.md` -- the `P N12` line above subtracts the row on `/uas/login`, which nothing in this package builds; the sign-in form this server does open is `config.LOGIN_URL` = `https://www.linkedin.com/login`, machine-verified ALLOWED at HEAD, so the boundary is not what holds that row out.

**-7, BUILT** -- `J 24 26 27 121 122 123` (`linkedin_job_detail.insights`) and
`N 135` (`linkedin_who_viewed_me.insights`).

**-4, DOUBLE-COUNTED** -- `N 149 150 151 160`, which `network.md` itself records
as owned by the messaging slice.

**390 is a floor, and it does not include the `ACCOUNT-VERIFICATION` rows (3),**
which the new `verification` substring probably reaches -- but no census row
names a url, so the address would have to be invented to make the check pass,
and it was not.

## A2. THE BOUNDARY: THREE NUMBERS, ALL TRUE, NONE A CORRECTION

The team lead measured 24 allowlist patterns; section 2 above published 23.
Both readings are right, and the disagreement is the point of this amendment:

| commit | when | allowlist | forbidden |
|---|---|---:|---:|
| `1c08e5f` | 15:53:26, census freeze | 22 | 23 |
| `ceb89c8` | when section 2 was measured | 23 | 33 |
| `23f04f1` | HEAD now | **24** | 33 |

The 24th pattern arrived in `5e33aa9`, after section 2 was written:

    ^https://www\.linkedin\.com/mynetwork/invite-connect/connections/?$

**Nothing was restated. A number acquired a third timestamp.**

## A3. `PUBLISH-POST-AUDIENCE-PARAM` IS NOT CLOSED, AND THE DIFFERENCE MATTERS

The review reports that `publish_post` shipped in `f9d382e` and asks for the row
to move to a closed-since-freeze list. Measured at HEAD, half of that is right,
and the half that is not changes where the row belongs.

`f9d382e` is dated **16:36:49** -- 43 minutes after the census froze, and 39
commits before HEAD. **It was already in the tree when section 3 was written,
and the ranking missed it.** That is a real miss, and its cause was worse than
the miss itself: the "closed since census" scan was ad hoc, built from one
progress file that happened to be open. It has been replaced by an enumeration
of all **51** commits in `1c08e5f..HEAD`, with every `feat(` commit checked
against the tool surface rather than against its message.

**What `f9d382e` actually did:**

    linkedin_publish_post(text: str, confirm_token: str = "")

Signature UNCHANGED. No visibility argument. The docstring now opens
*"Publish a post to your LinkedIn feed. REFUSES: the audience is unread"* and
states verbatim: *"This tool has NO VISIBILITY PARAMETER and never had one."*

**So the consent defect is closed and the capability is not.** He can no longer
be handed a confirm token for a broadcast at an audience nobody read -- which
is what section 5 said outranked its ratio, and it was fixed before that
sentence was written. But census row `M C2` is *"Choose the post's audience /
visibility"*, and at HEAD he still cannot. **The row stays a GAP and does not
subtract from 409.** Had it subtracted, A1 would read 389.

**Its blocker changed, and got sharper.** Section 3 filed it
`MISSING-PARAMETER`, cost 2, on the premise that the control had been seen and
never read. At HEAD the control is *located* -- 32 controls on a
settle-consistent reading, the only aria-label-named button in the dialog with
`aria-expanded="false"` -- and **the census that can see it REDACTS its name,
under the rule that keeps other members out of this process.** That is not an
unbuilt reader. It is a collision between two of this repository's own rules,
and it needs a ruling before it needs code. Re-filed:

| | as published | at HEAD |
|---|---|---|
| kind | MISSING-PARAMETER | RULING-FORK |
| blocker | the control was never read | the reader that can see it must redact it |
| queue | BUILD | DECIDE |
| cost | 2 | 2 (1 ruling + 1 tool) |

**The ranking was correct and the item was overtaken.** Recorded here rather
than deleted, so the record shows both.

## A4. TWO POST-FREEZE COMMITS THAT MOVED BLOCKERS WITHOUT CLOSING ROWS

**`5e33aa9` -- the biggest event in the window, and it closes nothing yet.**
It admits `/mynetwork/invite-connect/connections/`: his own 1st-degree
connections list. Machine-checked ALLOWED at HEAD, and `grep` finds **zero**
readers of that address in `server.py` and `dom.py`. Boundary open, no reader
-- the same shape as `PREMIUM-READER-NOT-BUILT`.

It does not touch the 409, because the rows it un-refuses (`N 23-28`) were
EXCLUDED-RULED under R2, where that address tripped BOTH `/invite` and
`/connect`. **It is still the most consequential change since the freeze**, and
`network.md` says why in its own words: that block is *"the single most
consequential block in the census for the operator's actual job hunt"*, because
the warm-referral workflow he already runs needs exactly one thing from LinkedIn
-- who he knows and where they work. It also unblocks the upstream of two GAP
rows this document ranked, `N 169` and `N 187`, both described by the census as
*"a filtered read over his own connections -- the capability rows 23-28 are
ruled out of"*. They are no longer ruled out of it.

**`81c5c9b` -- the reply surface got a reader, not a send.** It added
`read_thread_reply_surface` to `dom.py` and one field to an existing tool; the
tool count is still **35**, and the reader returns counts and booleans only,
because *"a conversation is a third party's words, in full, sent to him
privately"*. `M10` and `M47` stay GAP. What changed is the cost:
`THREAD-REPLY-BOX`'s capture is paid, so it drops from 6 to 5 -- and `M47`,
responding to an inbound Recruiter InMail, which the census calls the single
most job-hunt-relevant messaging action, is now the nearest write in the package
that needs no address at all.

## A5. THE THREE THINGS THAT MADE THE NUMBER WORTH HAVING

Recorded here at the team lead's direction, because a method that lives only in
a working log cannot be reused.

**1. The expected total was derived independently BEFORE any classifying, and
matched 409 per file.** Section 1. A classification that begins by counting what
it finds cannot discover that it missed something -- it publishes its own blind
spots as absence. The derivation came from the four slices' own count tables;
the measurement came from parsing every table row; they agreed four times out of
four. Had they disagreed, the disagreement would have been the finding.

**2. The cost model is an EQUATION in units this repo has produced before,
explicitly not hours.** Section 3. `A + C + P + D + T + 3W + R`, where every
term is a countable artifact -- an allowlist pattern, a capture, a parser, a
boundary-list edit, a tool, a WriteSpec family, a ruling. A cost stated in hours
can only be believed or disbelieved. A cost stated in artifacts can be argued
with term by term, and every ranking here can be recomputed by anyone who
disagrees with one coefficient.

**3. The tempting merge was refused.** A single `NO-ADDRESS` blocker would have
gated **189 of the 409 rows** behind one line of code and predicted no effort at
all. The merge rule -- two blockers merge only when the same single action
closes both -- is what turns "the allowlist is closed by default" into 33
separate decisions ranging from 21 rows down to one. **The long tail is the
honest part of the count**, not an artifact of over-splitting: 32 blockers gate
exactly one row each because 32 capabilities really do each need their own
surface.

## A6. THE STATED LIMIT, IN THIS DOCUMENT'S OWN WORDS

**An inferred blocker is not the same artefact as a cited one, and 183 of the
409 are inferred.** Section 7 carries the per-slice split. Restated here so it
is not read as a footnote:

For 183 rows -- **45% of the census** -- no sentence anywhere in the census
names what blocks them. Their blocker is my inference from the capability text
plus the boundary measured at HEAD. That inference is disciplined -- it is
checked against the code's own refusal machinery, and where a row named an
address the refusal was machine-verified -- but it is inference, and a reader
should be able to tell the two apart without having to ask.

**The softest set is 18: the LinkedIn Groups and Events rows recovered on the
census's second pass.** For those the slice itself says the families have "zero
prior art in the package" and offers no per-row blocker, so **my blocker is a
surface name and nothing more.** They sit inside `GROUPS-SURFACE` and
`EVENTS-SURFACE` -- ranked 4th and 8th on the reachable ranking, 50 rows between
them. **The two blockers carrying the most rows are also the two resting on the
least evidence**, and that pairing is the single thing in this document most
likely to be wrong.

## A7. WHAT DID NOT CHANGE

`PARSER-ON-A-LOADED-PAGE` stands exactly as published: 2 rows, cost 2, zero
extra page loads, zero boundary change, zero ruling -- the cheapest build in the
document. `N 118` reads endorsement counts off a page
`linkedin_my_profile(include_skills=True)` already loads; `P L2` reads his own
follower count off a page whose value is already quoted inside
`publish_post.residue` by no tool at all.

The queue table, the 97 blockers and the ranked table are unchanged. Three
blockers move on the evidence above -- `PUBLISH-POST-AUDIENCE-PARAM` (BUILD to
DECIDE), `THREAD-REPLY-BOX` (cost 6 to 5), and `MESSAGE-ADDRESSING` (its
allowlist half landed in `25d3440`; a committed recipient has still never been
observed) -- and they are recorded here rather than edited into section 3, for
the reason this amendment exists.

## A8. A LIVE WRITER IS IN THIS TREE, AND IT DOES NOT AFFECT THE NUMBERS ABOVE

Stated because anyone re-running these checks will see it, and because a shared
tree with an active writer is not a tree to sweep.

At 23:03:58 `git status` showed uncommitted work that is **not mine** -- this
task edited no tracked file:

    M  linkedin_server/server.py                  mtime 23:03:49
    M  linkedin_server/writes.py                  mtime 22:56:34
    ?? tests/test_stale_process_is_announced.py   mtime 23:02:27

`server.py` was written **nine seconds** before that reading, so this is an
ACTIVE writer, not stale WIP. It was left untouched.

**The counts in this document survive it, and that was checked rather than
assumed.** The boundary figures came from importing the working copy, so the
question is fair:

* `linkedin_server/readonly.py` is **CLEAN** -- not in `git diff --name-only`.
  The allowlist 24 and the forbidden 33 are therefore the committed values at
  `23f04f1`, not working-copy values.
* The uncommitted diff touches **none** of `PERFORMABLE`,
  `SANCTIONED_MUTATIONS`, `SANCTIONED_WRITES`, `PERMANENTLY_FORBIDDEN`,
  `_ALLOWED_URL_PATTERNS` or `_FORBIDDEN_URL_SUBSTRINGS` -- grepped over
  `git diff -U0`, zero hits. `SANCTIONED_WRITES` 13 and `PERMANENTLY_FORBIDDEN`
  9 re-read straight off `23f04f1` by AST agree with what is published above.
* The `writes.py` change is a docstring rewrite about `unsave_job`'s preview
  route, and the `server.py` change is 391 lines this task did not read.

So the numbers are pinned to `23f04f1` and the live WIP sits on top of them.
**Anything that lands from that writer moves 390 again**, in the same direction
everything else moved today.

## A9. THE REDACTION FORK IS RULED: A CLOSED VOCABULARY

**Team-lead ruling, this review. Recorded, not implemented** -- this was a
read-only pass. It is written here so whoever builds it inherits the argument
instead of re-deriving it.

**THE FORK, restated.** `publish_post` refuses because the audience is unread.
The control is located. The census that can see it REDACTS its name, under the
rule that keeps other members out of this process. Two of this repo's rules
collide, and the reader cannot be built by widening either one.

**WHY THE REDACTION IS OVER-BROAD HERE, and it is a reason the rule cannot see
from inside itself: the audience control's label is FURNITURE, not a person.**
No property of a string separates `"Anyone"` from a person's name -- which is
exactly why the caps rule exists, and exactly why it is wrong on this control.
A rule that cannot tell furniture from a person must refuse both, and that is
correct behaviour producing a wrong outcome.

**THE RESOLUTION: admit a CLOSED VOCABULARY, which this package already runs.**
LinkedIn's post-audience options are a closed set. A closed vocabulary is
matched BY NAME before any selector exists, so it **cannot pass an arbitrary
string, therefore cannot carry a member's name, and the redaction has nothing
to refuse.** No widening of the caps rule; no new permission class.

**THE PRECEDENT, verified at HEAD rather than recalled.**
`dom.MESSAGING_FILTERS` (`linkedin_server/dom.py:2458`) is a closed tuple --
`focused, other, unread, jobs, connections, inmail, starred` -- and
`dom.py:2502` refuses anything outside it *before a locator is built*:

> `"The permitted set is [...] and it is closed: a control outside it is`
> `refused rather than clicked, because the permission granted here is to`
> `filter a view, not to press things on a page."`

Its click is one of the four entries in `readonly.SANCTIONED_MUTATIONS`, and
the sanction argues itself in exactly the shape the audience control needs
(`readonly.py:1058-1078`):

> *"dom.MESSAGING_FILTERS is a CLOSED SET matched before any selector is
> built, so an arbitrary string can never become a click target. The
> permission is not 'may click on that page', it is 'may activate one of these
> seven pills'."*

Transposed: the permission sought is not *"may read that dialog"*, it is
*"may recognise which of these N audience values is selected"*. Same shape,
same enforcement point, same reviewer-legible list.

**THE ONE THING THAT MUST HAPPEN FIRST, and it is not code.** *The audience
option set has never been written down in this repository.* Grepped at HEAD:
`"Anyone"` appears in `linkedin_server/` only inside prose describing its own
absence (`server.py:4798`, `:4862`, `:4954`), plus one synthetic fixture in
`tests/test_publish_post_names_its_audience.py:127`. The Help Center walks
name the option set for RECOMMENDATION visibility (`a542730`: *All LinkedIn
members / 1st-degree connections only / Only you*) and for ADDITIONAL-NAME
visibility (`a545784`) -- **neither is the post composer.** A closed vocabulary
is admitted by name or not at all, so **the set has to be established before it
can be written**, and taking it from a sibling control's options would be
inventing it. That measurement is the first task, and it is one read on an
address already on the allowlist.

**ONE DISCREPANCY IN THE PRECEDENT, flagged because I am citing it.** The
sanction comment says *"seven named filter pills"* twice and *"all six pills
are `<button>` with no href"* once; the tuple holds seven. Six-versus-seven is
unresolved and was not this pass's to resolve -- but a builder inheriting this
argument should know the count is not self-consistent in the passage they are
inheriting.

`PUBLISH-POST-AUDIENCE-PARAM` therefore stays `RULING-FORK` / DECIDE in A3 --
**and the fork is now decided.** What remains is a measurement and a build, in
that order.

## A10. A BOUNDARY OPENED WITH NOTHING BEHIND IT

Carried forward at the team lead's direction, because it is the sentence that
generalises past this one row.

`5e33aa9` admits `/mynetwork/invite-connect/connections/` -- his own 1st-degree
connections list, the block `network.md` calls *"the single most consequential
block in the census for the operator's actual job hunt"*, because the
warm-referral workflow he already runs needs exactly one thing from LinkedIn:
who he knows and where they work. Machine-checked ALLOWED at HEAD. **Zero tools
read it** -- `grep` over `server.py` and `dom.py`, no hits.

**A boundary opened with nothing behind it is a capability that exists on
paper.** The refusal is gone and the answer is still unavailable, and nothing
in the tool surface would tell you which of those two states you are in. This
document already carries the same shape twice under different names:
`PREMIUM-READER-NOT-BUILT` (`/premium/my-premium/` admitted as a census key,
reader deliberately not built, the smallest unbuilt read in the census) and now
the connections list.

**It is worth a standing check rather than a note.** The count that would catch
it is: allowlist patterns with no reader. At HEAD that is at least two of
twenty-four, and neither is visible from the tool surface, from
`writes.PERFORMABLE`, or from any number in the census -- which counts
capabilities, not the gap between a permission and its use.

## A11. HEAD MOVED WHILE THIS AMENDMENT WAS BEING WRITTEN

Recorded because it is this document's own thesis happening to this document.

Amendment A pins every figure to `23f04f1`. By the time it was finished, HEAD
was `bb107a1` -- one further commit, `docs(writes): the module docstring
outlived the blocker it describes`, from the writer named in A8.

**The figures survive it, checked rather than assumed.** `readonly.py` is still
clean, and the boundary re-reads **allowlist 24, forbidden 33** at `bb107a1` --
identical to `23f04f1`. The new commit changes a docstring, not a capability.

So the pin is now historical, and that is what a pin is for. A number in this
document does not go stale silently; it goes stale visibly, against a commit
anybody can check out. **That is the whole difference between appending an
amendment and editing the census.**

## A12. RECOMMENDATION -- THE UNREAD-BOUNDARY CHECK

**Named recommendation, team-lead directed. NOT BUILT** -- this was a read-only
pass. Recorded so it can be built deliberately rather than rediscovered.

**THE CHECK:** *for every pattern in `readonly._ALLOWED_URL_PATTERNS`, does any
code in this package actually navigate to an address that pattern admits?*
Every pattern with no such navigation is a **boundary opened with nothing behind
it.**

**WHY IT IS A CLASS AND NOT AN ANECDOTE -- two confirmed instances, both
measured today:**

| pattern | admitted | reader | how it got here |
|---|---|---|---|
| `/premium/my-premium/` | as a census key | **none** | deliberately not built; `2026-08-31-linkedin-perform.md:1035` -- "the boundary entry and reader are NOT built". The smallest unbuilt read in the census (`J 127`) |
| `/mynetwork/invite-connect/connections/` | `5e33aa9`, today | **none** | `grep` over `server.py` and `dom.py`, zero hits. The block `network.md` calls the most consequential in the census for his actual job hunt |

**WHY IT IS INVISIBLE TO EVERY COUNT THIS PROJECT ALREADY RUNS.** The tool
surface says 35 either way. `writes.PERFORMABLE` says 12 either way. The census
counts CAPABILITIES, so an admitted-but-unread address is not a row in it --
it is a permission with no consumer, and permissions are not what the census
enumerates. **A boundary opened with nothing behind it looks identical to a
boundary that was never opened**, from every number anybody currently takes.
That is the gap this check closes.

**THE DESIGN NOTE THAT DECIDES WHETHER IT WORKS: it must PARSE, not GREP.**
Addresses are named three different ways in this package --

    writes.py:2314    SAVED_LIST_URL = "https://www.linkedin.com/jobs-tracker/?stage=saved"
    config.py:129     FEED_URL = f"{BASE_URL}/feed/"
    writes.py:442     url_template="https://www.linkedin.com/jobs/view/{target}/"

-- so a literal scan misses two of the three forms and under-reports readers.
**And it fails the other way too, which is worse.** `dom.py:860` builds

    out["company_url"] = f"https://www.linkedin.com/company/{slug.group(1)}/"

`/company/` is **not on the allowlist**; that string is an output FIELD handed
back by `job_detail`, not a navigation target. A grep for the surface finds a
hit and scores `COMPANY-PAGE-SURFACE` as *having a reader* -- a false green on
the third-largest blocker in this document. **The check must match NAVIGATION
CALLS against the allowlist, not mentions of a url anywhere in the source.**

**THE COUNT IS NOT STATED HERE, DELIBERATELY.** "At least 2 of 24" is a range,
and this document's own first rule is that a range is what you publish when
counting was possible and was not done. Counting it properly means building the
parse above, and building it was out of scope. **Two instances are confirmed;
the true figure is unknown and is not 2 by any argument made here.** Whoever
builds it should expect it to be higher, because both known instances arrived
the same way -- a boundary argued and admitted on its own merits, with the
reader left for later, and later not yet arrived.

**AND IT HAS A SECOND USE.** Run in reverse it is the freeze check this
document needed and did not have: an allowlist entry that gains a reader
silently closes census rows, which is how `J 24 26 27 121 122 123` and `N 135`
moved without anything in `_audit/` saying so until section 2 went looking.

## A13. FOUR BLOCKERS MOVE: MEASURE ENDS AT 23 BLOCKERS / 105 ROWS, NOT THE STATED 22

Four blockers move on evidence from a live wave -- measured verdicts, not
proposals, recorded here rather than edited into section 3, for the reason A7
already gives.

**1. `PANEL-NOT-OBSERVED` (rank 8, 3 rows, 2R/1W) -- MEASURE to
DECIDE-RETIRE.** Rows `J 25 29 30` -- `J 25` ("Why am I seeing this job?"),
`J 29` (Skills Match insight), `J 30` (add a missing skill from the insight;
depends on `J 29`) -- the same three rows section 6 already named and left
open ("nobody knows whether LinkedIn still draws them").

Measured with a known-value CONTROL taken from this document's own section 6
-- the needles `Show match details` / `Show Premium Insights` / `How you
match` must read 1/1/0 on a settled posting:

* The control reproduced **1/1/0 on FOUR committed captures** (all confirmed
  present on disk this pass): `tests/fixtures/job_detail.html`,
  `job_detail_hydrated.html`, `job_detail_following_hydrated.html`, and the
  unsanitised `_audit/_probe-job-followed-company-hyd.html`.
* It reads **0/0/0 on exactly the two captures the fixture table already
  marks un-hydrated** (`job_detail_following.html`, `job_detail_shell.html`)
  -- so the control also discriminates settled from half-rendered.
* It reproduced **1/1/0 LIVE, twice**, on `/jobs/view/<id>` across a full
  browser stop and restart.

On all four settled captures AND both live reads, every target needle reads
**0 in visible text and 0 in html**: `Why am I seeing this job`,
`Why am I seeing this`, `why am i`, `seeing this`, `Skills Match`,
`skills match your profile`, `of 10 skills match`, `Add skill`. The loosest
probe, the bare token `skill`, reads **1**, and that one occurrence sits
inside `<strong>` with `<br>` siblings -- job-description prose, not a panel.

The page carries `aria-expanded="false"` x10 and `aria-expanded="true"` x0,
and **no aria-label on it mentions matching or skills**. So the panels are
ABSENT, not collapsed.

Also record: `/jobs/view/<id>` has **EARNED a settled-control baseline of
193** -- two readings, 193 both times, identical on every structural count,
across a browser restart. It belongs in `server.CENSUS_SETTLED_CONTROLS`
(the name is real -- present in `server.py`, `tests/test_surface_census.py`
and `scripts/_probe_unmeasured_surfaces_live.py`, checked this pass) under a
`job_posting` key; that edit is not yet made.

**A table cell this pass did not touch:** every DECIDE-RETIRE row in section
3 carries `ruling: YES` -- all twelve, zero exceptions, checked by reading
the column down. `PANEL-NOT-OBSERVED` currently carries `ruling: no`. The
queue move argued above implies that column moves with it; section 3 stays
unedited, so the table and this amendment disagree on that one cell until
someone edits it.

**2. `CONVERSATION-OVERFLOW-MENU` (rank 17, 10 rows, 1R/8W/1RW) -- ANSWERED,
and the cost doubles.** Boundary change needed: **NONE**. `/messaging/` is
already on the allowlist (machine-verified at HEAD) and
`linkedin_open_messaging` already performs exactly this one navigation.

THREE readings of `/messaging/`, the third carrying a control:

| | reading 1 | reading 2 | reading 3 |
|---|---:|---:|---:|
| controls_read | 73 | 73 | 64 |
| buttons / links | 42 / 18 | 42 / 18 | 37 / 18 |
| `[aria-expanded="false"]` | 22 | 22 | 18 |
| `[aria-haspopup]` | 0 | 0 | 0 |
| `[role="menu"]` | 0 | 0 | 0 |
| `[role="menuitem"]` | 0 | 0 | 0 |

THE CONTROL: `dom.MESSAGING_FILTERS` is a closed set of seven pills that
`dom.py` records as MEASURED to be `<button>`s on the live inbox -- the same
tuple, and the same six-versus-seven wording split, A9 already flagged. On
reading 3 all seven appear in VISIBLE main text (Focused 1, Other 2, Unread
1, Starred 1, Jobs 1, Connections 1, InMail 4). So the render is settled and
the zeros are readable. Two agreeing readings alone would NOT have been
enough here -- repeated readings catch variance between readings, and cannot
by themselves catch a stable wrong state; only a control with a known value
can, which is why reading 3 carries one.

THE FINDING: on a settled inbox of **1280994 characters of HTML** -- the
largest DOM of any surface measured that day -- there is not one popup
trigger and not one menu item in the document. `More options` occurs ONCE in
1.28 MB of html and ZERO times in visible text; `Overflow menu` zero in both.

THE COMPARISON THAT MAKES IT A FINDING RATHER THAN AN ABSENCE:

| surface | settle evidence | `[aria-haspopup]` | `[role="menu"]` | `[role="menuitem"]` |
|---|---|---:|---:|---:|
| `/feed/` | CONSISTENT, 307 read vs 277 baseline | 16 | 6 | 3 |
| `/jobs/view/<id>` | control fires 1/1/0, twice | 2 | 0 | 0 |
| `/messaging/` | 7 of 7 filter pills drawn | 0 | 0 | 0 |

**The feed proves this build DOES pre-render menus into the DOM with nothing
pressed.** So messaging's zero is a fact about messaging, not about the
instrument.

CONSEQUENCE: the cost is **TWO interactions, not one**. The menu is not
merely closed -- its TRIGGER is absent from the DOM, so the control must
first be made to exist (the conversation row reveals it on hover) and only
then opened. This document costs the unopened-menu class at "one capture
each"; this member of the class needs a HOVER ruling as well as a press
ruling, and hovering has never been argued anywhere in the package. Proposed
queue move: MEASURE -> DECIDE, with the note that the ruling in front of it
is about hovering, not about the click.

Also: `/messaging/` redirected 1 -> 3 path segments on all three loads --
LinkedIn auto-opens a conversation, which the August messaging probe
hypothesised and nobody had watched. The nav badge read
`new_since_last_visit: 0` before any inbox load, so by this project's own
rule that a zero cannot separate "consumed nothing" from "there was nothing
to consume", **no cost is claimed in either direction.**

**A second table cell this pass did not touch:** every DECIDE row in section
3 also carries `ruling: YES` -- all twelve, zero exceptions.
`CONVERSATION-OVERFLOW-MENU` currently carries `ruling: no`. Same unedited-
cell disagreement as item 1, same reason.

**3. `HASHTAG-EXISTENCE` (rank 11, 3 rows, 1R/2W) -- RE-FILE 3 rows to 1.**
Three independent instruments agree the hashtag-follow surface is not
present:

1. LinkedIn's own help index (recorded in this document already): source
   article `a528144` returns HTTP 404, and two independent index queries
   return no hashtag-following article.
2. The read boundary at HEAD, machine-verified: `/feed/hashtag/hiring/`,
   `/feed/hashtag/?keywords=hiring` and
   `/search/results/content/?keywords=%23hiring` are all REFUSED-NO-PATTERN;
   `/feed/follows/` is REFUSED-FORBIDDEN on the substring `/follow`.
3. A live settled `/feed/` -- 307 controls, settle CONSISTENT against the
   277 baseline, 405872 characters of html -- draws `/feed/hashtag/` 0,
   `hashtag` 0, `#hiring` 0, `Followed hashtags` 0, in visible text AND in
   html.

The three rows do not share a blocker:

| row | as published | at HEAD |
|---|---|---|
| `N 194` | `HASHTAG-EXISTENCE` | `SEARCH-RESULTS-SURFACE` -- the census's own note names its blocker: "no people search" |
| `C 11` | `HASHTAG-EXISTENCE` | EXCLUDED-RULED, not GAP -- see below |
| `C 52` | `HASHTAG-EXISTENCE` | `HASHTAG-EXISTENCE`, unchanged -- the one row the three instruments above actually speak to |

**`C 11` needs precision, because the obvious citation is wrong.** The row
reads "add a hashtag to a post", and a shipped, AST-asserted invariant
already forbids the server composing anything into his text -- but **the
word `hashtag` does NOT appear in `tests/test_typed_bytes.py`** (checked this
pass, zero hits, case-insensitive). It appears in `linkedin_server/server.py`
and `linkedin_server/writes.py`, in `publish_post`'s rationale comments -- at
this pass's re-check, at lines 5486 and 4652 respectively, not the
5434/4538 first cited. Both files are uncommitted-dirty in this tree right
now, more so than A8's two-file reading (this tree is running well past
a dozen touched files across the span of this append), so neither line
number is a stable HEAD pin and both should be expected to drift again
before anyone reads this. **What the test enforces is stronger than a
hashtag rule** -- the typed text is a slice of the GRANT's canonical target,
so the server never composes what it types; the AST-node form exists because
the substring form let an appended-hashtag mutation through. The hashtag is
the WORKED EXAMPLE of the defect, not the subject of the assertion. Reads
EXCLUDED-RULED rather than GAP.

So `HASHTAG-EXISTENCE` becomes a ONE-ROW blocker. Nothing in the evidence
above argues its queue changes -- unlike items 1 and 2, no move off MEASURE
is made for `C 52` here, so it is carried forward MEASURE, at 1 row, unless
a future pass rules otherwise.

**4. `MATCH-DETAILS-COLLAPSED` (rank 18, 5 rows, 5R, `J 116 117 118 119 120`)
-- RE-FILE, do not delete.** Section 6 files these as present, COLLAPSED
behind `Show match details`, queued DECIDE on the ground that "pressing a
disclosure control is a different permission from reading a render". That
premise is now measured false.

**Measured on the UNSANITISED capture
`_audit/_probe-job-followed-company-hyd.html` (its `URN-REMOVED` count is 0,
so these are LinkedIn's own bytes and not the sanitiser's): `Show match
details` is NOT a disclosure control.** It is an `<a href>` inside an `<li>`.
Three such anchors exist on the page, all with the same path and the same
ten parameter names:

    path:   /preload/guideOverlay/
    params: interop, query, originalThreadMailbox, conversationUrn,
            contextUrns, intent, originalIntent, trackingId, customContext,
            pageContextJobPostingUrns

Their `query` parameter is LinkedIn's own control label -- plain words, no
identity -- and reads:

    'Show match details'
    'Create cover letter'
    'Help me stand out'

**VERIFIED-BY-INSTRUMENT:** the three anchors, the ten parameters, the three
labels, the tag being `<a>` and not `<button>`.

**DERIVED (strong, not measured):** pressing it invokes a GENERATION product
rather than expanding a region already on the page. The sibling labels
settle the family -- "Create cover letter" and "Help me stand out" are
unambiguously generative -- and `intent` / `originalIntent` / `customContext`
read as a prompt payload.

CONSEQUENCE: `J 116 117 118 119 120` are not "a render behind a click", so
the blocker's NAME is wrong and the DECIDE in front of it is a different
question -- closer to `AI-INTERVIEW-PRODUCT` (14 rows, DECIDE-RETIRE) than to
the unopened-menu class. Proposed rename: `AI-ASSISTANT-OVERLAY` -- a
proposal, not a ruling. **The five rows are not deleted** -- they are
re-filed, and the capability they describe may genuinely not exist as a
readable panel at all.

Corroborating, from the same wave: `How you match` reads **0 in html on a
settled live posting, twice**. There is no collapsed panel holding that
text, which is consistent with the text not existing until something
generates it.

Also note: `/preload/guideOverlay/` is a sibling of `/preload/sharebox/`,
already on the allowlist -- so the boundary cost would be one line. The
boundary is the cheap part; the destination is not.

**THE ARITHMETIC, closed rather than asserted.** Independently re-summed
before applying any move: section 3's own 25 MEASURE-queue rows
(`GROUPS-SURFACE` 32, `PANEL-NOT-OBSERVED` 3, `HASHTAG-EXISTENCE` 3,
`EVENTS-SURFACE` 18, `CONVERSATION-OVERFLOW-MENU` 10, `OPEN-TO-WORK-MODAL`
11, `INTRO-EDITOR-UNREAD-CONTROLS` 4, `AUDIO-EVENTS-EXISTENCE` 1,
`NO-URL-AT-ALL` 1, `NOTIFY-COST-UNMEASURED` 1, `CONTACT-INFO-PANEL` 5,
`OPEN-TO-HIRING-MODAL` 5, `FEED-ITEM-OVERFLOW-MENU` 5,
`POST-COMMENT-CONTROLS` 4, `ALL-FILTERS-PANEL` 2, `MESSAGE-ADDRESSING` 1,
`JOBCARD-OVERFLOW-MENU` 2, `THREAD-REPLY-BOX` 2, `PER-MESSAGE-OVERFLOW-MENU`
2, `PICKER-SURFACES` 2, `POLL-SURFACE` 2, `ADD-SECTION-MENU` 1,
`MESSAGE-REACTION` 1, `CELEBRATION-COMPOSER` 1, `REPORTING-FLOWS` 1) sum to
**120**, matching section 4 exactly -- so the base this ledger moves from is
confirmed, not assumed.

    120   rows in MEASURE at the ranking (25 blockers)
     -3   PANEL-NOT-OBSERVED, whole blocker, to DECIDE-RETIRE
    -10   CONVERSATION-OVERFLOW-MENU, whole blocker, to DECIDE (proposed)
     -2   HASHTAG-EXISTENCE re-filed: N 194 out to SEARCH-RESULTS-SURFACE,
          C 11 out to EXCLUDED-RULED -- 1 row (C 52) stays in MEASURE
    ----
    105   rows in MEASURE

     25   blockers in MEASURE at the ranking
     -1   PANEL-NOT-OBSERVED leaves entirely
     -1   CONVERSATION-OVERFLOW-MENU leaves entirely
      0   HASHTAG-EXISTENCE -- SHRINKS to one row, does not leave
    ----
     23   blockers in MEASURE

**Two corrections against the brief this amendment was built from, both
recomputed rather than trusted:**

* **"16 rows move" should read 15.** 13 (`PANEL-NOT-OBSERVED` 3 +
  `CONVERSATION-OVERFLOW-MENU` 10) plus 2 (the two `HASHTAG-EXISTENCE` rows
  that leave) is 15, not 16. 105 is unaffected, because the subtraction that
  actually produces it is 120 - 3 - 10 - 2 = 105 either way -- `C 52` never
  moves, so there is no sixteenth row to subtract.
* **"22 blockers" should read 23.** The brief's own parenthetical already
  contradicts itself: it names three blockers as leaving the queue "entirely"
  and then describes the third, `HASHTAG-EXISTENCE`, as "remains but
  shrinks" -- which is not entirely. Two blockers leave
  (`PANEL-NOT-OBSERVED`, `CONVERSATION-OVERFLOW-MENU`); one shrinks in place
  (`HASHTAG-EXISTENCE`, 3 rows to 1) and is still a MEASURE blocker on this
  amendment. 25 - 2 = 23.

`SEARCH-RESULTS-SURFACE` goes 21 -> 22 rows (21 + `N 194` = 22). `N 194` was
a MEASURE row and `SEARCH-RESULTS-SURFACE` is a DECIDE blocker, so this same
row leaving MEASURE is already inside the -2 line above; it is not a second
subtraction.

`MATCH-DETAILS-COLLAPSED` keeps its 5 rows and its DECIDE queue; only its
name and the question in front of it change, so it does not enter this
ledger at all.

**One subtraction this pass did not make, flagged rather than taken:** `C 11`
reading EXCLUDED-RULED is the same class of row A1 already subtracted eight
of, out of the master GAP total (409 at the freeze, 390 at HEAD per A1,
still 390 as of A11's re-check). If folded into that ledger the same way,
HEAD would read 389. **DERIVED, not verified this pass** -- re-confirming
the current pinned GAP total against a live HEAD running well past a dozen
touched files was out of scope for this append, and A11 already shows how
fast that number goes stale under exactly this kind of tree.

**THE STATED LIMIT.** Every number above traces to a named instrument (a
grep count, a settle-control triple, a redirect count, a badge read) or to
this file's own prior sections (6, A1, A7-A9). Nothing here re-opens
`PUBLISH-POST-AUDIENCE-PARAM` (A3/A9) or the boundary-with-no-reader class
(A10/A12) -- both stand as last amended. The `AI-ASSISTANT-OVERLAY` rename is
a proposal, not a ruling. Section 3's `ruling` column for `PANEL-NOT-OBSERVED`
and `CONVERSATION-OVERFLOW-MENU` is unedited and now disagrees with the
argument above until someone edits it -- the same kind of gap A7 already
leaves standing for its own three moves. And the line numbers cited for `C
11` are a snapshot of a tree that was still moving while this sentence was
written.


---

# AMENDMENT B -- 2026-09-04. A CORRECT MEASUREMENT WAS PUBLISHED AND THEN WALKED PAST TWICE

**Appended, not merged, on this document's own rule.** Sections 1-9 stand
as published, and so does amendment A, A1-A13 included -- nothing above
has been rewritten. This amendment is not about a number being
wrong. It is about a number that was RIGHT, written down IN THIS REPOSITORY,
and then contradicted by two later documents that never consulted it -- which
is a documentation-integrity defect, and it is worth more than the row it
happened to.

## B1. THE THREE DOCUMENTS, IN ORDER

**1. `_audit/2026-08-22-parity-linkedin.md:18` -- THE CLAIM.**

> **Skill endorsement counts** -- the `/details/skills/` page is *already
> loaded* by `linkedin_my_profile(include_skills=True)`; counts are dropped
> today. **0 extra page loads.** Smallest real win left.

Reasonable when written. Nobody had looked at the page.

**2. `_audit/2026-08-23-build-linkedin.md:229-231` -- THE CORRECTION, TAKEN
THE NEXT DAY, IN WRITING, IN THIS REPOSITORY.**

> `_audit/2026-08-22-parity-linkedin.md` ranked "skill endorsement counts" as
> the smallest real win at **0 extra page loads**. **That is mis-specified,
> measured:** `tests/fixtures/profile_skills.html` carries **zero** endorsement
> counts -- no `N endorsements` text anywhere in the capture. The "already
> loaded" half is right; the *capture* does not exist, so the build needs a
> fresh live page load and a re-freeze, not zero.

That agent did the right thing in the right place: measured, named the earlier
document, quoted the number, and said what it would actually cost.

**3. `_audit/_census/network.md:365` and this file, section 5 and A7 -- THE
CLAIM RESTATED, TWICE, AS THOUGH THE CORRECTION HAD NOT HAPPENED.**

`network.md` row `N 118` cites the parity audit VERBATIM -- *"Costed at zero
extra page loads and never built"* -- and cites `2026-08-22-parity-linkedin.md`
by path while not citing the file that corrected it. This document then ranked
`PARSER-ON-A-LOADED-PAGE` as **the cheapest build in the document** on that
basis, and **A7 re-affirmed it unchanged** under the heading `WHAT DID NOT
CHANGE`.

**So a correct measurement sat in `_audit/` for twelve days and was walked past
by two subsequent readers, one of them a pass whose entire purpose was to
establish what blocks each row.**

## B2. WHAT THE LIVE PAGE SAYS, 2026-09-04

Two allowlisted self-reads, one session, three seconds apart, nothing pressed:

| | measured |
|---|---|
| `/in/me/details/skills/` | 20 skill cards, 2,359 characters of `main` |
| occurrences of `endors` anywhere on it | **0**, cards and body alike |
| `/in/me/` topcard, relationship-count lines | **1**, and it reads CONNECTIONS |
| followers lines on the topcard | **0** |

**The page DREW.** So "the fixture is stale" is ruled out: the committed
fixture agrees with live LinkedIn, which is what the 2026-08-23 correction
already implied and nobody tested. `N 118` is not a missing parser. It is a
line LinkedIn does not draw. And `P L2`'s follower count is not on the topcard
at all -- wherever the *"275 followers"* in `writes.publish_post.residue` came
from, it was not that page.

**Both rows of the cheapest build in this document are refuted.** The cost was
never 2; it was unbounded, because the thing being costed does not exist.

## B3. WHY THIS IS THE FINDING AND THE ROWS ARE NOT

The rows are two. The defect is general, and this document is a witness to it
twice over: **the reason drifts away from the fact, and then the fact stops
being consulted.**

Every step was individually defensible. The parity audit was reasoning from a
page nobody had opened. `network.md` was citing its source faithfully -- it
quoted the parity audit exactly. This document's section 5 was ranking on the
census's own numbers, which is what a ranking pass is for. A7 re-affirmed a row
nothing had visibly moved. **No one of those is a mistake, and the outcome is a
wave dispatched to build something that is not there.**

The structural fault is that **a correction lived in a different file from the
claim, and nothing joined them.** `2026-08-23-build-linkedin.md` names
`2026-08-22-parity-linkedin.md`; the parity audit does not, and cannot, name
its own corrector. Every later reader who started from the claim -- which is
what a census row cites -- reached the wrong document first and had no signal
that a second one existed.

## B4. WHAT WOULD HAVE CAUGHT IT, STATED AS A CHECK RATHER THAN A RESOLUTION

**A claim in `_audit/` that a later `_audit/` document contradicts should be
findable from the claim.** The cheapest form is a backlink written INTO the
corrected document at correction time -- one line at
`2026-08-22-parity-linkedin.md:18` saying "CORRECTED 2026-08-23, see
`2026-08-23-build-linkedin.md:229`" -- because it costs the corrector one edit
and it reaches every future reader who starts where the census points.

The mechanical version, which this repository is better at: **a check that
greps `_audit/` for a document quoted by a later document that contains the
words "mis-specified", "corrected", "measured" or "that is wrong" beside the
citation, and asserts the cited document carries a pointer back.** Not built
here; named so it can be built deliberately rather than rediscovered.

**AND THE ROW-LEVEL FIX IS ALREADY IN THE CODE, which is the part that does not
rot.** `N 118` is now answered by a LIVE reading in
`dom.read_profile_detail_entries`, re-taken on every call, carrying the
denominator it was taken over -- cards searched, card lines searched,
characters of `main`, and whether the body mentions an endorsement at all. A
constant would have frozen today's answer into next year's; a reading that
ships with its denominator cannot be quoted onward as a property, which is
exactly the failure this amendment is about. See `_audit/INSTRUMENTS.md`
section 2.3.

## B5. WHAT THIS AMENDMENT DOES NOT CLAIM

It does not restate the GAP total. `N 118` and `P L2` do not become
EXCLUDED-RULED on my authority -- they are refuted as SPECIFIED, and whether
"LinkedIn does not draw it" retires a row or re-files it is the lead's ruling,
the same fork A1 recorded for the eight forbidden-substring rows.

It does not touch `PARSER-ON-A-LOADED-PAGE`'s cost model, its ranking method,
or any other row. The instrument that produced the refutation is
`scripts/_probe_endorse_and_follow_lines.py`, tracked, read-only, module-level
literals only, and it prints no skill name, no employer and no member path --
so these numbers can be re-taken by anyone who doubts them rather than
re-derived.

## A14. A BOUNDARY BREADTH NOBODY RULED, MEASURED AND LEFT FOR THE OPERATOR

**RECORDED, NOT ACTED ON.** This section changes no code and moves no row. It
exists because the measurement behind the ruling is cheap to take now and
expensive to re-derive later.

### The two rulings that disagree, three lines apart

`linkedin_server/readonly.py` admits the self-profile detail pages with this
member segment:

    /in/[A-Za-z0-9\-_%]+/details/(skills|experience|education)/

**That is not `me`. It admits ANY member's details pages.** Sixteen lines
below it, the intro editor is deliberately restricted to the `/in/me/` form,
and its comment gives a MEASURED reason rather than a preference:
`linkedin_who_viewed_me` establishes that loading a member's profile leaves
them a durable record in their own viewer list, so **"a pattern that can
address anybody but him is refused on that ground alone, whatever the page
underneath is for."**

Both sentences are in one file, three lines apart, and they answer the same
question differently. Nothing anywhere records a decision to treat the details
pages as the exception.

### It was nearly inherited today, and that is why this section exists

The Interests page was first admitted by adding a fourth word to that
alternation. **For one commit the boundary therefore admitted
`/in/<a-third-party>/details/interests/`, measured ALLOWED rather than
inferred** -- on the worst surface in the package for it, because that tab
enumerates the PEOPLE somebody follows. It would have read a third party's
follow graph while announcing to that third party that he had looked.

Caught in review, and re-landed as its own anchored `/in/me/` pattern,
NARROWER than its three siblings. Twelve controls, zero mismatches. The
siblings were left exactly as they were, because narrowing them is a
different decision with a different owner.

### THE MEASUREMENT, so the cost of narrowing is a number and not a guess

`scripts/_probe_details_url_breadth.py`. **Parsed, not grepped** -- and that
is not fastidiousness: the allowlist entry is a two-line implicit string
concatenation, and a grep over it during this very review returned only the
first line and appeared to contradict a correct reading. A text-shaped read of
a structure sees whichever line it caught.

CONTROL FIRST, so a zero is legible rather than ambiguous:

| what the instrument saw | count |
|---|---:|
| files parsed | 55 |
| string literals examined | 10854 |
| literals mentioning `/in/` | 122 |
| literals mentioning `/details/` | 42 |
| f-strings mentioning `/details/` | 12 |
| `.format()` on a `/details/` string | 0 |

RESULT:

| classification | count |
|---|---:|
| `literal-me` | 21 |
| f-string `literal-me` | 10 |
| `regex` (the allowlist patterns themselves) | 4 |
| `no-member-segment` | 8 |
| `self-reference` (the probe's own prose) | 9 |
| **f-string `interpolated`** | **2** |

**BOTH interpolated sites were traced by hand, and NEITHER is a third party:**

* `linkedin_server/server.py:2885` builds
  `/in/{slug}/details/<section>/` for Experience, Education and Skills. `slug`
  is `shape.profile_slug_from(final_url)`, and `final_url` is the LANDING of
  `/in/me/` -- **his own vanity slug**. It emits these urls in
  `linkedin_my_profile`'s answer; it does not navigate to them.
* `scripts/_probe_interests.py:33` interpolates the module constant
  `ME = "me"`.

### THE ANSWER, and the limit on it

**Nothing in this package builds a `/in/<not-me>/details/` url.** So the
breadth in the allowlist is reach NOBODY USES, and narrowing the three
siblings to the `me` form would break no caller here.

**THAT IS A STATEMENT ABOUT THIS PACKAGE, NOT ABOUT THE BOUNDARY.** The
allowlist still admits those urls to anything that asks -- a future tool, a
future probe, or an agent handed a slug. The whole point of the intro editor's
ruling is that the boundary should not depend on nobody happening to ask.

**IT IS THE OPERATOR'S RULING AND IT IS NOT TAKEN HERE.** What this section
provides is the cost: one pattern edit, one re-freeze, zero callers broken.

### A SMALLER FINDING FROM THE SAME TRACE, reported and not fixed

`linkedin_server/server.py:1095-1097`, immediately above `PROFILE_DETAIL_URLS`,
states:

> "The vanity slug is never used to build one of these, even though the
> allowlist would accept it: an address built from a landed url is an address
> the page chose."

`server.py:2885` builds three details urls from exactly that vanity slug. The
sentence is defensible if "one of these" means the NAVIGATION table it sits on
and 2885's urls are only EMITTED -- but the distinction is not in the words,
and it is load-bearing prose about the boundary. Not edited here: `server.py`
had another wave writing in it throughout this review, and the correction is a
sentence somebody who owns that file should choose.
