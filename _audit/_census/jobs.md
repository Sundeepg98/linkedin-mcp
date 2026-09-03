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
| `unsave_job` | **NO. NEVER FIRED.** | `_audit/2026-08-30-linkedin-undo.md:1775` -- "`unsave_job` was **never fired**, including after it became capable." Same file records the same at `:639`, `:921`, `:1156`, `:1369`, `:1585`. |
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

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 1 | Keyword / free-text job search (incl. LinkedIn's natural-language matching) | a511260, a6889044 | CP | `linkedin_search_jobs`; used as the standing live control in four audits -- 10 timed runs at `2026-08-30-jobs-view-reliability.md:123`, 7-row results at `2026-08-30-save-label.md:594` |
| 2 | Boolean operators in the query (AND / OR / NOT / "phrase" / parens) | a524335 | CU | `keywords` is `urlencode`d verbatim into `/jobs/search/`, so operators reach LinkedIn unmodified; no audit records a boolean query |
| 3 | Filter: Location | a507441 | CP | `location=` param |
| 4 | Filter: Date posted (24h / week / month / any) | a507441 | CU | `f_TPR`, `_DATE_POSTED` 4 values (`server.py:1189`) |
| 5 | Filter: Workplace type (remote / hybrid / on-site) | a508610, a512279 | CU | `f_WT`, `_WORKPLACE` 4 values |
| 6 | Filter: Experience level (internship..executive, 6 values) | a507441 | CU | `f_E`, `_EXPERIENCE` 6 values |
| 7 | Sort by Most relevant / Most recent | a6889044 | CU | `sortBy=DD` |
| 8 | Result paging by offset | a507441 | CP | `start=`; ~25/page, no auto-paging by design |
| 9 | Filter: Easy Apply only | a507441 | GAP | -- |
| 10 | Filter: Company | a507441 | GAP | -- |
| 11 | Filter: Employment type / job type | a507441, a512746 | GAP | -- |
| 12 | Filter: Under 10 applicants | a507441 | GAP | -- |
| 13 | Filter: In your network | a507441 | GAP | -- |
| 14 | Filter: Fair chance employer | a415496 | GAP | -- |
| 15 | The "All filters" panel as a surface | a523136 | GAP | -- |
| 16 | Suggested filters (adaptive, on AI search) | a6889044 | GAP | -- |
| 17 | Search from device current location | a507703 | GAP | -- |
| 18 | Recent searches: view and re-run | a523136 | GAP | -- |
| 19 | Recent searches: clear history | a523136 | GAP | -- |
| 20 | Result card fields: title, company, location, hiring status, posted-when, job id, url | a507441 | CP | `shape.parse_job_card` (`shape.py:768-779`) |
| 21 | Posting detail: title, company, location, salary, workplace type, employment type, applicant count, posted, description | a1395225, a1396429 | CP | `shape.parse_job_detail` + `_split_meta_line`; `linkedin_job_detail` |
| 22 | Posting: which apply route it uses (LinkedIn Apply vs off-site ATS, and the host) | a512388 | CP | `apply_path`; two routes measured, "Neither the label nor the href classifies alone; both must agree" (`writes.py:645`) |
| 23 | Hiring-status chip on a posting ("Actively reviewing applicants", "Be an early applicant") | a507990, a1661038 | CP | `shape._HIRING_STATUS` (`shape.py:1657`) |
| 24 | Hirer responsiveness: review-time estimate, "Responses managed off LinkedIn" | a1661038 | GAP | -- |
| 25 | "Why am I seeing this job?" | a7181681 | GAP | -- |
| 26 | "Promoted by hirer" labelling on a result | a512429 | GAP | -- |
| 27 | Verification badge on a posting | a1492056 | GAP | -- |
| 28 | Report a job as closed | a515926 | GAP | -- |
| 29 | Skills Match insight ("x of y skills match your profile") | a793433 | GAP | -- |
| 30 | Skills Match: add a missing skill from the insight | a793433 | GAP | -- |

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
| 39 | Read job recommendations ("Jobs you may be interested in") | a512279 | GAP `SKILL` | server: none. Skill: `jobs-noreply@linkedin.com`, `FACET_SUGGESTIONS_COMMS_EMAIL` |
| 40 | Read per-job network proximity ("2 connections", "1 company alum") | -- (email-only field) | GAP `SKILL` | **The skill's exclusive field.** SKILL.md:13 -- "No scraper and no job-board API can produce that field." Not on any surface this server reads |
| 41 | Subscribe / unsubscribe the job-collections weekly digest | a1652837 | GAP | -- |
| 42 | Job collections and their five groupings (Domains, Industries, Company Benefits, Editorial, Corporate Commitments) | a1652837 | GAP | -- |

### C. Saved jobs and the job tracker (16)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 43 | Save a job | a513247 | CP | `linkedin_save_job`. **The one write proven to land** -- see section above |
| 44 | Unsave a job | a513247 | CU | `linkedin_unsave_job`. Built, gated, **never fired**, including after it became capable |
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
| 57 | View network connections reachable for a tracked job | a8684146 | GAP `SKILL` | server: none. Skill `referral_join.py`: joins digest proximity + career-insights people against the Naukri applications DB -- "That pairing does not appear in any UI he uses" |
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
| 71 | List / delete stored resumes (max 4) | a510363, a512405 | GAP | -- |
| 72 | Download a stored resume | a8313636 | GAP | -- |
| 73 | See which resume was submitted for a given application | a506680 | GAP | -- |
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
| 92 | Set preference: job titles | a507508 | GAP | -- |
| 93 | Set preference: locations | a507508 | GAP | -- |
| 94 | Set preference: workplace types | a507508, a512279 | GAP | -- |
| 95 | Set preference: start date | a507508 | GAP | -- |
| 96 | Set preference: employment types | a507508 | GAP | -- |
| 97 | Set India-only preferences: notice period, expected annual salary | a507508 | GAP | -- |
| 98 | Set / edit / delete the Minimum Pay preference | a1644694 | GAP | -- |
| 99 | Control career-interests visibility to recruiters | a510407 | GAP | -- |
| 100 | "Signal your interest to recruiters at companies you've created job alerts for" | a1380509 | GAP | -- |

### G. Company research reachable from a job (15)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 101 | Identify the employer and its Page url from a posting | a550270 | CP | `job_detail.company_url` |
| 102 | Read whether the employer is already followed, from the posting | a548013 | CP | `job_detail.company_follow_state`, three-valued, read off the same rendering |
| 103 | Follow a company | a548013 | CP | `linkedin_follow_company`; `2026-08-31-linkedin-perform.md:1318` -- "**PERFORMS** \| verified by re-reading the followed list" |
| 104 | Unfollow a company | a548013 | CP | `linkedin_unfollow_company`; same table -- "**PERFORMS** \| addressed by NUMERIC id; refuses when the Page is not among the rendered rows" |
| 105 | List followed companies | a548013 | CP | `linkedin_followed_companies` |
| 106 | Company Page About tab (size, industry, locations) | a550270 | GAP | -- |
| 107 | Company Page Jobs tab / "see all jobs at this company" | a550270, a567373 | GAP | -- |
| 108 | Company Page People tab (titles, study areas, skills, how you are connected) | a550270 | GAP | -- |
| 109 | Company Page Life tab | a550270 | GAP | -- |
| 110 | Company Page Home / Posts tabs | a550270 | GAP | -- |
| 111 | Company Page Products / Services tabs | a550270 | GAP | -- |
| 112 | School Page Alumni tab | a567083 | GAP | -- |
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
| 121 | Applicant insights: your ranking percentile vs other applicants | a563146 | GAP | -- |
| 122 | Applicant insights: top skills among applicants, experience/education levels | a563146 | GAP | -- |
| 123 | Premium hiring-company insights (hiring trends, growth rate, average tenure, feeder companies/schools) | a563146 | GAP | -- |
| 124 | Premium AI company intelligence (headcount, openings, strategic priorities) | a563146 | GAP | -- |
| 125 | "Jobs where you're a top applicant" section | a548337, a1586951 | GAP | -- |
| 126 | Premium AI job-fit tips | a7474394 | GAP | -- |
| 127 | Read the InMail credit balance | a7474394 | GAP `SKILL` | server: `/premium/my-premium/` is a census key but `2026-08-31-linkedin-perform.md:1035` -- "the boundary entry and reader are **NOT built**". Skill `inmail-targeting.md` holds the ledger: 5/month, 15 cap, 90-day expiry, refunded on any reply |

### I. Recruiter contact and interview prep (6)

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 128 | Message the job poster (1st/2nd degree) | a519730 | CU | `linkedin_send_message` exists and gates on a name needle; it "ships expecting to refuse" and has never been fired. Whether it can reach a job poster specifically is unmeasured |
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
| 132 | Generate role-specific practice questions from a real job description | a8336402 | GAP | "role-specific questions generated from real job descriptions" |
| 133 | Practice out loud, by voice | a8336402 | GAP | "You can practice out loud" |
| 134 | Practice by reading and typing responses instead | a8336402 | GAP | "read and type out your responses" |
| 135 | Be interviewed by a real-time AI interviewer | a8336402 | GAP | "The AI interviewer listens, responds, and evaluates your answers in real time" |
| 136 | Receive an interview readiness score (low / medium / high) | a8336402 | GAP | "interview readiness score" |
| 137 | Receive a summary of strengths and areas to improve | a8336402 | GAP | "a summary of your strengths and areas to improve" |
| 138 | Receive a transcript of your responses with worked improvements | a8336402 | GAP | "a transcript of your responses with examples on how to improve" |

### K. AI interviews as a hiring stage, candidate side (7) -- RECOVERED 2026-09-03

An entire product surface the first census had **zero** rows for. `a10376002`, "AI
interviews on LinkedIn": a hirer invites an applicant to an audio or video interview
conducted by an AI. **Not Premium-gated.** This is a stage of applying, squarely in this
slice, and no walk of the jobs topic tree surfaced it.

| # | capability | source | state | tool, or the repo's own reason |
|---|---|---|---|---|
| 139 | Take a practice AI interview first, unlimited repeats | a10376002 | GAP | "You can take the practice interview as many times as you'd like" |
| 140 | Complete a hirer's voice-based or video-based AI screening interview | a10376002 | GAP | "complete the hirer's voice-based or video-based AI screening interview" |
| 141 | End an interview in progress | a10376002 | GAP | "To end the interview, click End interview" |
| 142 | Decline to participate, without automatic disqualification | a10376002 | GAP | "If you decide not to participate, you will not be automatically disqualified" |
| 143 | Reply to the invitation with feedback on the interview experience | a10376002 | GAP | "contact the hirer with additional information or feedback on the interview experience by replying to the initial interview invitation" |
| 144 | Request your rating, summaries, transcript or recording | a10376002 | GAP | "You can request access to your rating and summaries, transcript, or recording by contacting the hirer" |
| 145 | Request an accommodation | a10376002 | GAP | "contact the hirer directly to request an accommodation" |

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
| 151 | Filter a job search by MULTIPLE simultaneous locations | a523131 | GAP | "You can add multiple locations in the same search." Row 3 covers ONE location; `linkedin_search_jobs` takes a single `location` string |

---

## 2. WHAT EACH GAP WOULD TAKE

Shapes, not designs. `R`/`W` is read or write. `REV` is whether the effect can be undone.

| rows | gap | shape | R/W | REV |
|---|---|---|---|---|
| 9-14 | six named search filters | pure parameter work on `linkedin_search_jobs`: six more `_WORKPLACE`-style dicts and six more `params.append`. `f_AL` (Easy Apply), `f_C` (company id), `f_JT` (job type), `f_EA`/under-10, `f_JIYN` (in network), `f_FCE`. The company filter needs a slug-to-numeric-id resolver, which the repo already names as an open problem for `follow_company` | R | REV (a search changes nothing but recent-search history) |
| 15-16 | All-filters panel, suggested filters | needs the panel rendered and its controls enumerated, or the query parameters read off a filtered url. A capture, then parameters | R | REV |
| 17 | search from current location | needs browser geolocation permission. Out of shape for this design | R | REV |
| 18-19 | recent searches read / clear | a new read surface (`/jobs/search-history/` or equivalent) on the allowlist; the clear is a destructive verb and `"delete"`/`"remove"` are on the mutation-verb denylist | R + W | clear is NOT reversible |
| 24-30 | posting-side insight panels (responsiveness detail, why-seeing, promoted label, verification badge, Skills Match, report-closed) | all live on the posting `linkedin_job_detail` already loads. Each is a parser addition against a capture, at ZERO extra page load -- the cheapest block on this list. `report a job as closed` is the exception: a write behind a menu | R (28, 30 are W) | REV for reads; 28 not reversible |
| 31-36, 41 | all alert writes | a new write surface. `/jobs/alerts` is not on the read allowlist and alert editing is a modal. Needs: a capture of the alerts manager, an allowlist entry, a `WriteSpec` per verb, and an aiming rule (which alert). `"create"`, `"delete"`, `"edit"`, `"subscribe"` are ALL on the mutation-verb denylist, so four denylist exemptions | W | create/edit REV; **delete NOT reversible** (the alert's history is gone) |
| 37-40 | alert results, proximity | **already served by the skill.** Building a server path would duplicate it and lose the proximity field, which no page carries | R | REV |
| 42 | job collections | a new read surface plus a parser | R | REV |
| 54-56 | tracker stage change, notes, date filter | the tracker is already read; these are row-level controls behind an overflow menu. Needs a capture of a POPULATED tracker row -- which the repo has never had, because the Applied tab reads zero. `"update"`, `"set"`, `"add"` are on the mutation-verb denylist | W | REV |
| 57 | connections for a tracked job | **served by the skill**, from a better source | R | REV |
| 68 | draft save / resume | the Easy Apply modal's own control; blocked behind the same multi-step gate as row 60 | W | REV (a draft can be discarded) |
| 70-73 | resume upload, list, delete, download, which-was-submitted | needs the Job Application Settings surface on the allowlist and a file-input driver, which this server has never had. `"upload"`, `"delete"` are on the mutation-verb denylist | R + W | upload/download REV; **delete NOT reversible** |
| 78-83 | Premium apply extras (cover-letter AI, Top Choice, limits, self-ID) | each is a distinct surface; Top Choice spends a non-refunding monthly credit | W | Top Choice **NOT reversible** (credit does not roll back) |
| 85-86 | undo a dismissal, "I'm interested" | posting-card and company-page controls; both need a capture | W | REV (both document an Undo) |
| 92-100 | every job-preference FIELD, Minimum Pay, recruiter visibility | all live behind the same modal as rows 89-91. **One capture of the Open To Work editor unlocks this entire block.** The repo already nominates the safe first click: `server.py:5058` -- "a `Show details` control whose action list holds one Navigate and no ServerRequest" | R + W | REV, EXCEPT the audience change: `writes.py` calls it "IRREVERSIBLE IN AUDIENCE" -- switching to All members draws a frame his current employer can see, and un-drawing it does not un-show it |
| 106-114 | company and school Page tabs, Premium insights | a company Page url is already returned by `job_detail`. Needs `/company/<slug>/` and its tabs on the read allowlist, plus a parser per tab. Largest single block of pure-read GAPs on this census (9 rows) | R | REV |
| 116-126 | "How you match", applicant insights, Premium company insights, top-applicant, AI tips | 116-120 and 121-122 render **on the posting page `job_detail` already loads**, for a Premium account, which this operator has. Parser additions at zero extra page load. 123-126 need other surfaces | R | REV |
| 127 | InMail balance | `/premium/my-premium/` is already ruled admitted as a census key; the boundary entry and the reader were deliberately not built. Smallest unbuilt read on this list | R | REV |
| 129 | InMail the job poster | needs both a compose surface for InMail (distinct from the message composer) and a verification. `send_message` cannot report "sent" today | W | **NOT reversible**, and it spends a credit |
| 132-138 | Premium AI interview prep | a whole separate product that opens in LinkedIn Learning in a new tab. Voice capture, a real-time conversational agent, and a scored transcript. **Structurally out of shape for this server**: it is not a page to read or a control to click, it is a live audio session. The realistic reachable slice is the READ side -- a past session's readiness score, summary and transcript, if they are addressed by a url | R (results) + W (the session) | REV (practice leaves no mark on any application) |
| 139-145 | AI interviews as a hiring stage | same shape and higher stakes: rows 140-142 are decisions on a live application. **Row 142 is the one to notice** -- declining is documented as safe ("you will not be automatically disqualified"), so an automated participation decision would be making a career call, not a mechanical one. Rows 143-145 are messages to a human hirer | R + W | 140 **NOT reversible** (a completed screening interview is submitted); 141-145 REV |
| 146-149 | Resume tips | reached from the Jobs tab by a sparkle control, desktop only. Needs the surface captured and a file input this server has never had (same blocker as row 70). Feedback only -- **it cannot generate a resume** | R + W | REV (it produces a file; nothing is sent) |
| 150 | Writing Assistant recruiter message | US-only Premium overlay on a compose surface. Blocked behind the same wall as `send_message`: nothing here can verify a send | W | **NOT reversible** |
| 151 | multi-location job search | the smallest item on this list: `linkedin_search_jobs` takes one `location` string and LinkedIn accepts several. Parameter work, no new surface | R | REV |

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
3. **`unsave_job` is the only PERFORMABLE write with no live fire at all.** Six separate
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
