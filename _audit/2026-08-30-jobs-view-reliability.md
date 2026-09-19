# Why /jobs/view/<id> draws sometimes and not others

**Wave:** jobs-view reliability. **Baseline in:** `d0d3e3b`, 1764 passed, tree clean.
**Server process under test:** pid 25376, started 14:36:47 IST, `build.code.commit
d0d3e3b65d52`, `dirty: false` -- so the running process holds HEAD and every reading
below is a reading of the shipped build.

**Verdict, stated at the precision the evidence supports:**

- **Throttling is REFUTED.** Not "unlikely" -- refuted, by a measurement anyone can
  re-run in forty seconds. The surface is not rate limited and pacing is not the fix.
- **The variable is inside our own process, not on LinkedIn's side.** `browser.goto`'s
  settle has exactly two outcomes, ~1 s and ~7 s after DOMContentLoaded, chosen by a
  race. Every failing read landed on the ~1 s branch; the read that drew landed on the
  ~7 s branch. The call durations in the client's own log are a direct readout of which
  branch ran, and they match the code's arithmetic exactly rather than approximately.
- **One alternative survives and I say so** (section 5): that LinkedIn intermittently
  sends a description-less page, which would be quiet, which would produce the same
  correlation. Four independent reasons make it the weaker account, none is a proof, and
  the probe that kills it is the fix itself (section 8). I could not run that probe
  against the shipped build and did not pretend otherwise.

So: **not throttling, not the postings, not the session, not the reader** -- and the
remaining question is narrow, named, and answered by shipping 7.2.

---

## 1. The instrument nobody had used

The MCP client writes a JSONL log per session at

    %LOCALAPPDATA%\claude-cli-nodejs\Cache\D--Sundeep-projects-job-hunting-mcp-servers\mcp-logs-linkedin\

and every entry carries a UTC timestamp plus, on completion, **the wall-clock duration of
the tool call**:

    {"debug":"Calling MCP tool: linkedin_job_detail","timestamp":"2026-08-30T09:20:24Z",...}
    {"debug":"Tool 'linkedin_job_detail' completed successfully in 1s","timestamp":...}

It also captures the server's stderr, so FastMCP's startup banner marks every server
restart. This is a complete, retrospective, zero-cost time series of every LinkedIn call
this machine has made -- including the ones taken before this wave existed. All times
below are IST (UTC+5:30).

## 2. The probe log

Every row is one live MCP call. `dur` is the client log's own measurement, not mine.
`main` is the character count of `<main>` reported by the refusal. No `confirm_token` was
passed at any point; every call below is a read.

| # | time IST | tool | job id | dur | outcome | main |
|---|---|---|---|---|---|---|
| 1 | 14:50:26 | job_detail | 4448301715 Fivetran | **1s** | FAIL `missing: description` | 1348 |
| 2 | 14:50:48 | job_detail | 4448301715 Fivetran | **8s** | **DREW FULLY** -- description, `apply_path` offsite to `www.fivetran.com`, `company_follow_state not_following` | -- |
| 3 | 14:52:03 | job_detail | 4448301715 Fivetran | **1s** | FAIL `missing: description` | 1348 |
| 4 | 14:54:30 | search_jobs | (control) | 9s | 7 results on page, full rows | -- |
| 5 | 14:54:42 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |
| 6 | 14:54:50 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |
| 7 | 14:54:59 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |
| 8 | 14:56:49 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |

**Rows 1, 2 and 3 are the whole finding.** The same posting, the same session, the same
build, no code change and no intervention: it failed, then drew completely 22 seconds
later, then failed again 75 seconds after that. Whatever the variable is, it is not the
posting, not the account, not the session and not the hour.

Two details worth keeping:

- **The failures are byte-stable per posting.** Fivetran fails at exactly 1348 chars
  twice; Gunpowder at exactly 1315 chars four times. A read landing at a random point in
  a progressive render would scatter. This lands on a fixed point -- the server-rendered
  document, before hydration.
- **`missing` is `description` ALONE, never `title`.** The title and the employer are
  present on every failure, so `read_job_identity`'s company block had drawn. This is not
  the bare shell (`job_detail_shell`, 1092 chars, missing title AND description). It is
  the shape the concurrent wave captured as `job_detail_following`: 1358 chars, missing
  the description only.

## 3. The mechanism, and the arithmetic that identifies it

`browser.goto` (`linkedin_server/browser.py`) settles like this:

```python
await page.goto(url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
...
try:
    await page.wait_for_load_state("networkidle", timeout=settle_ms)
except Exception:
    # networkidle rarely settles on LinkedIn (long-poll connections).
    # Falling through with a flat wait is expected, not an error.
    await page.wait_for_timeout(settle_ms)
```

with `SETTLE_MS = 3500`. That code has exactly **two** possible settle durations and
nothing in between:

| branch | what happened | settle | + nav | observed call |
|---|---|---|---|---|
| networkidle **RESOLVED** | the page had <= 2 connections in flight for 500 ms | ~0.0-0.5 s | ~1 s | **1-2 s** |
| networkidle **TIMED OUT** | still busy at 3.5 s, so the flat 3.5 s runs too | **7.0 s** | ~1 s | **7-8 s** |

The measured call durations are 1s and 8s. They are not near those numbers, they ARE
those numbers. **The duration is not a symptom of the outcome; it is a readout of which
branch ran**, and the branch decides how long after DOMContentLoaded the read is taken:
about one second, or about seven.

So the answer to the lead's question is:

> The page draws when the call happens to take the `networkidle`-timed-out branch and the
> read lands ~7 s after DOMContentLoaded. It does not draw when `networkidle` happens to
> resolve, the flat wait is skipped, and the read lands ~1 s after DOMContentLoaded --
> before LinkedIn's own client has fetched the description into the DOM.

**The `except` fallback is doing all the useful work, and it only runs when the `try`
FAILS.** The comment above it says networkidle "rarely settles on LinkedIn". Measured
across every logged call on this machine, that is true of the search page and **false of
the job page**: `/jobs/view/<id>` settles early on 28 of 37 loads.

### Why `linkedin_search_jobs` never fails -- the same fact, not a second one

| tool | n | durations observed |
|---|---|---|
| `linkedin_search_jobs` | 10 | 8s x2, 9s x5, 10s, 12s, 14s -- **never once below 8 s** |
| `linkedin_job_detail` | 37 | 1s, 2s and 3s x28, then 6s, 7s, 8s x7, 28s -- **fast on 28 of 37**, and NOTHING between 3s and 6s |

The search page keeps its network busy past 3.5 s on every load ever recorded here, so it
**always** takes the timed-out branch and **always** gets the full 7-second settle. It
never fails because it is never read early. One mechanism explains both halves of the
puzzle; a throttle would need a separate per-endpoint assumption to explain why the
control surface is exempt.

| 9 | 14:58:03 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |

## 4. What the evidence rules OUT

### Throttling of this surface -- REFUTED

This was the lead's leading hypothesis and it does not survive row 2.

- **The same url drew fully 22 seconds after it was refused, and failed again 75 seconds
  after that.** A throttle that lifts for exactly one call in the middle of a burst and
  re-arms immediately is not a throttle.
- **The call that succeeded is the one that spent MORE on LinkedIn, not less** -- 7
  seconds of settle against 1, and by construction more of the page's own requests
  observed. Throttling predicts the opposite direction.
- **The branches interleave call by call, not in blocks.** In the 13:40-13:43 burst the
  client log shows `1s, 8s, 1s, 1s, 1s, 2s, 7s`. A rate limit produces a window of
  failures with an edge, not an alternation at 20-second spacing.
- **There is no throttle artefact anywhere in the payload.** `final_url` comes back as
  exactly `https://www.linkedin.com/jobs/view/<id>`, `assert_not_authwall` passes, no
  interstitial, no redirect, no error status -- and the document title and the employer
  are read successfully off the page on **every single failure**.

### The posting being expired or gone -- REFUTED

Already ruled out by the lead's 37-minute-old Rockerbox posting. Independently confirmed
here: Fivetran `4448301715` drew in full at 14:50:48 carrying `Reposted 4 days ago`, and
then failed again at 14:52:03.

### A broken session, cookie jar or browser -- REFUTED

`linkedin_search_jobs` returned 7 full rows at 14:54:30, twelve seconds before three
consecutive job-page failures on the same browser and the same tab.

### A difference between the two readers -- ALREADY DEAD

Killed by the concurrent wave in `_audit/2026-08-30-save-label.md` Part 3. Not
re-litigated here.

### A bot-detection interstitial, or an A/B rollout of a client-rendered job page

Both are refuted by the same observation: the failing page is not a *different* page. It
is byte-stably the *same* document that the successful call read, minus the one field the
client fetches. `missing` is `description` alone; the title and employer are always there.

## 5. The alternative I could not execute a probe against, and why I do not believe it

Honest statement of the one surviving competitor, because it predicts the identical
duration/outcome correlation:

> LinkedIn intermittently serves a job page that never fetches its description. That page
> is therefore quiet, so `networkidle` resolves, so the call is fast. The 1 s call is a
> CONSEQUENCE of the empty page rather than its cause, and waiting longer would not help.

Four reasons it is the weaker account, none of which is a proof:

1. **It requires LinkedIn to withhold the description on ~69% of signed-in job-page
   loads.** That is a notorious, user-visible outage on their flagship surface, and it is
   not happening. The settle race needs only that a heavy SPA sometimes has a 500 ms
   network lull between DOMContentLoaded and its hydration fetches, which is ordinary and
   is invisible to a human, who waits.
2. **It needs a second assumption to exempt the search page.** The settle race explains
   `search_jobs` never failing and `job_detail` failing 69% of the time with one
   mechanism and no extra parts.
3. **An independent instrument already measured the un-hydrated signature live.** The
   concurrent wave drove the save gate over a LIVE failing posting -- `4456021840`, the
   same Gunpowder id, at 12:26 -- and recorded **0 buttons of any kind under `<main>`**,
   with 2 anchors present. Their capture table makes that decisive: the un-hydrated shell
   has 0 buttons and every drawn capture has at least 2, while anchors attach earlier. A
   page that had hydrated and merely lacked its description would still carry its
   buttons. That page had not run its hydration at all -- which is what "read one second
   too early" looks like and is not what "the server sent a page without a description"
   looks like.
4. **The failure is byte-stable and equals the server-rendered document.** 1348 chars
   twice for Fivetran, 1315 four times for Gunpowder, missing exactly the one field that
   arrives by client fetch.

**What would settle it outright:** read the same page twice inside one navigation, once
at ~1 s and once at ~7 s, and report both. If the second read carries the description the
race is proven and withholding is dead. That probe cannot be run against the shipped
build; it is specified in section 8.

## 6. Pacing: it IS enforced, and it is not the problem

The lead asked whether `min_seconds_between_page_loads: 3` and
`max_page_loads_per_call: 2` are actually enforced for this surface. **Both are.**

- `browser.goto` calls `await self.wait_for_rate_slot()` unconditionally, after the
  read-boundary assertion and before `page.goto`. There is no path to a navigation that
  skips it. `_last_navigation_at` is stamped in a `finally`, so a navigation that
  *failed* still consumes its slot.
- Pinned by three tests, one of which is the control:
  `test_consecutive_navigations_are_spaced_by_the_configured_floor`,
  `test_the_rate_gate_is_shown_actually_waiting` (floor at zero -- shows the gate can
  fail), and `test_a_failed_navigation_still_consumes_its_rate_slot`.
- `linkedin_job_detail` performs exactly one `BROWSER.goto` and reports
  `pages_loaded: 1`. Confirmed in the live payload of probe 2.
- Corroborated in the client log: the three `job_detail` calls timed at **3s** are the
  floor engaging -- up to 3 s of rate sleep in front of a ~1 s fast-branch read.

**I am not changing the interval, and the lead's own rule is the reason.** "Derive the
number from measurement, never pick a round one because it sounds safe" cuts against a
change here. Across roughly forty `/jobs/view/` loads today there is **no rate response
from LinkedIn anywhere in the record**: no 429, no interstitial, no authwall redirect, no
degradation across a burst. The one success arrived in the middle of the densest burst of
the day. There is nothing to pace against, and slowing the server down would have bought
a placebo and hidden the real defect behind a longer wall-clock.

**One real gap, recorded rather than fixed.** The floor is **per process**:
`_last_navigation_at` is instance state on the module singleton, so two MCP client
processes keep two independent clocks, and the profile lock only stops them running at
the same instant, not from alternating. The lead's "another session at 14:00" is exactly
that shape. It is not today's bug, and a cross-process rate file is a design with its own
failure modes, so it is written down here rather than built.

| 10 | 15:01:51 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |

**On Gunpowder, and stated as a limit rather than a finding:** it has now failed six times
for me and roughly five for the lead, and **every one of my six took the fast branch.**
That posting has never once been read on the slow branch. So nothing whatever is known
about whether it draws, and "some postings never render" is NOT supported by this run --
it is untested. See section 8.

## 7. The fix

### 7.1 What I changed, in the file I own (`browser.py`)

**An instrument, and no behaviour change.** `goto` now records how the settle went and
exposes it as `BROWSER.last_settle`:

```python
{"branch": "networkidle_resolved" | "networkidle_timed_out" | "settle_failed",
 "settled_ms": 4,
 "settle_ms_configured": 3500}
```

This is the answer to the lead's ask for "an instrument that tells a caller which state it
is in", and it is **cheaper than cheap: it costs no page load at all**, because it is
measured during a wait that was already happening. It is what lets a refusal distinguish

- *"I looked 4 ms after DOMContentLoaded"* -- re-read, this says nothing about LinkedIn;

from

- *"I waited the full 7 s and the description still was not there"* -- now that IS a
  finding about the posting or about LinkedIn.

Today the refusal cannot tell those apart, which is why the lead's table of per-posting
outcomes could be assembled at all.

I also **replaced the comment that hid this for a day.** It read "networkidle rarely
settles on LinkedIn (long-poll connections)"; it is true of `/jobs/search` (0 early
resolutions in 10 recorded loads) and false of `/jobs/view/<id>` (28 of 37). The new
comment carries the measurement and points here.

**What I deliberately did NOT do: change `SETTLE_MS`, or add a flat floor.** The settle is
binary *by construction* -- either ~0 s or exactly 2 x `SETTLE_MS` -- so no measurement
taken through the shipped build can ever distinguish "2 s would be enough" from "6 s would
be enough". Every candidate number sits inside an unmeasured bracket of (1 s, 7 s]. Picking
one would be exactly the round-number-that-sounds-safe the brief forbids, and it would tax
every surface for one surface's missing readiness check. If the lead wants a stopgap before
7.2 lands, the one honest form is "always take the branch measured to work" -- i.e. run the
flat wait unconditionally as well, making every navigation settle a uniform 7.0 s. That is
a one-word order and I have not taken it on my own.

### 7.2 SPECIFIED for the owner of `dom.py` / `server.py` -- do not let me edit these

The durable fix is a readiness wait on the description, modelled exactly on
`dom.wait_for_save_control`, which the same wave already built, bounded, and measured at
**27 ms on a ready page**.

**The anchor, MEASURED across all five job captures in this repo (do not substitute):**

```python
#: The description section, as LinkedIn's SDUI layer marks it FILLED.
#: Measured 2026-08-30 over tests/fixtures/job_detail*.html:
#:
#:   capture                         this anchor   id="JobDetails_AboutTheJob_<id>"
#:   job_detail_shell                     0                  0
#:   job_detail_following                 0                  1   <-- description ABSENT
#:   job_detail                           1                  1
#:   job_detail_hydrated                  1                  1
#:   job_detail_following_hydrated        1                  1
#:
#: THE OBVIOUS ANCHOR IS THE WRONG ONE, AND WRONG IN THE DANGEROUS DIRECTION.
#: id="JobDetails_AboutTheJob_<id>" is the SLOT and is drawn before its content;
#: it is PRESENT on job_detail_following, the capture whose description is
#: missing, so a wait anchored on it reports READY in precisely the state this
#: wait exists to detect. The data-sdui-component attribute marks the slot
#: FILLED. Measured, not preferred.
JOB_DESCRIPTION_SLOT = (
    'main [data-sdui-component='
    '"com.linkedin.sdui.generated.jobseeker.dsl.impl.aboutTheJob"]'
)
JOB_DESCRIPTION_TIMEOUT_MS = 10_000
```

**`dom.wait_for_job_description(page) -> dict`** -- one wait on that selector attaching,
bounded by `JOB_DESCRIPTION_TIMEOUT_MS`, **one verdict, no retry loop**. It must
**return** its verdict rather than raise, so the caller decides:

| outcome | return |
|---|---|
| attached | `{"attached": True,  "waited_ms": n, "why": "..."}` |
| TimeoutError | `{"attached": False, "waited_ms": n, "why": "..."}` |
| any other exception | `{"attached": None,  "waited_ms": n, "why": "the readiness check itself failed"}` |

The three-valued return is not decoration: a locator that *raised* is evidence for
neither, and collapsing it into `False` would report a broken instrument as a finding
about LinkedIn. That exact mutation came back green on first pass in the save wave.

**`dom.read_job_posting`** calls it **FIRST**, before `read_job_identity` -- after the text
has been read the wait is worthless -- and returns the verdict alongside the existing
`main_present` / `main_chars` as `description_wait`.

**`server.linkedin_job_detail`** passes it into `shape.job_detail_failure_note(...)`, and
**`writes._read_posting_facts` inherits the fix for free**, which matters: the apply and
save confirm gates read the same page through the same reader.

**What the refusal must then be able to say**, which it cannot today:

- `attached False` + `main_chars` low + `BROWSER.last_settle.branch == "networkidle_resolved"`
  -> the read was taken ~0 ms after DOMContentLoaded AND a full 10 s wait still found
  nothing. Only now is "LinkedIn did not render this posting" a claim worth printing.
- `attached False` + the anchor never seen on any live posting -> suspect a RENAME of the
  SDUI component, not a LinkedIn outage. The refusal should say so, because a wrong anchor
  fails identically to a dead page and the two want opposite responses.

**Cost of the change:** ~0 on a page that has drawn; up to the bound instead of a
guaranteed failure on one that has not. **Benefit, measured:** `linkedin_job_detail`
currently takes the read-too-early branch on 28 of 37 recorded loads.

### 7.3 Specified tests -- I did not create these; `tests/` is not mine

Each is written with the mutation it must go RED at, since a check that cannot fail
certifies nothing.

| test | RED at |
|---|---|
| `test_the_description_anchor_separates_drawn_from_not_drawn` -- drive the selector over all five captures, assert `[0,0,1,1,1]` | anchor swapped to `[id^="JobDetails_AboutTheJob_"]`: `assert [0,1,1,1,1] == [0,0,1,1,1]` |
| `test_a_page_that_never_draws_the_description_is_reported_not_attached` | the wait re-raising TimeoutError instead of returning `attached False` |
| `test_a_locator_failure_is_not_a_timeout` | a bare `except Exception: attached=False` -- reports a broken instrument as a LinkedIn finding |
| `test_the_wait_runs_before_the_text_is_read` (order) | the wait moved after `read_main_text`, where it changes nothing |
| `test_a_ready_page_is_not_delayed` | an unconditional `wait_for_timeout` floor substituted for the element wait |
| `test_the_refusal_names_the_settle_branch_and_the_wait` | `description_wait` or `last_settle` dropped from the note |

## 8. What is still open, and what settles it

**The fix in 7.2 and the decisive experiment are the same change.** That is worth saying
plainly, because it means the one surviving alternative in section 5 gets killed or
confirmed as a side effect of shipping, at no extra page load:

> On a call whose `BROWSER.last_settle.branch` is `networkidle_resolved` -- i.e. the read
> would have been taken ~1 s after DOMContentLoaded and would have failed today -- does
> `wait_for_job_description` report `attached: True`?
>
> **YES** -> the description arrives after the settle returns. The race is proven, the
> "LinkedIn withholds it" alternative is dead, and the tool is fixed by the same commit.
> **NO, repeatedly, on postings that other calls have drawn** -> the race account is
> incomplete and section 5's alternative comes back. Say so; do not patch around it.

Two smaller things left open, both recorded rather than guessed:

1. **Gunpowder `4456021840` is untested, not unrenderable.** Ten-odd failures, every one
   of mine on the fast branch, zero slow-branch reads ever taken of it. After 7.2 lands
   it should be re-read; if it still refuses with `attached: False` and a full 10 s wait,
   *that* is the first real evidence for a per-posting effect and it will be the first.
2. **The rate floor is per process** (section 6). Not today's bug.

## 9. Method notes, including where I nearly went wrong

- **Every measurement is repeated and every job read is paired with a `search_jobs`
  control**, as instructed. The control at 14:54:30 sits twelve seconds before three
  consecutive failures.
- **The lead's cheapest test was run first and it answered immediately**: the Fivetran
  posting known to have drawn was re-read after ~70 minutes, failed, and then drew on the
  very next call 22 seconds later. That one pair is what turned "wait and see if the
  throttle lifts" into "the variable is inside our own process".
- **I built a fourth theory and then had to check it did not fit everything equally.** The
  duration/outcome correlation is predicted just as well by "LinkedIn served a page with
  no description", and I nearly filed the correlation as proof. It is not proof; section 5
  is the honest version, and section 8 is the probe that would settle it.
- **The instrument that broke this open cost nothing and was already on disk.** The MCP
  client had been recording the duration of every LinkedIn call all day. Three theories
  died for want of a time series that existed the whole time.

---

## Appendix A -- probe log, continued

| # | time IST | tool | job id | dur | outcome | main |
|---|---|---|---|---|---|---|
| 11 | 15:05:30 | job_detail | 4456021840 Gunpowder | **1s** | FAIL `missing: description` | 1315 |
| 12 | 15:05:57 | job_detail | 4448301715 Fivetran | **1s** | FAIL `missing: description` | 1348 |
| 13 | 15:06:05 | job_detail | 4454627766 MeridianSquare | **2s** | FAIL `missing: description` | 1323 |

Probe 13 is a posting **never read before by anyone** -- taken off the 14:54 search
control -- and it fails in exactly the same shape at 1323 chars, missing the description
alone. So the failure is not a property of the two postings the lead happened to pick.

**A run worth recording honestly:** probes 3 and 5-13 are eleven consecutive fast-branch
calls. At the day's base rate (24 fast of 32) a run of eleven is about a 4% event, so it
is probably not chance. I floated a cache explanation here and then tested it.
**IT FAILED TO REPLICATE -- see Appendix E, and read that before believing this
paragraph.** What decides the branch remains unknown. The run itself is real and is worth
recording; the explanation I reached for is not.

## Appendix B -- "can a cheap probe tell throttled from not-drawn-yet BEFORE burning a read?"

Answering the ask directly, because the finding changes the question.

**There is no throttled state to detect.** Across roughly forty `/jobs/view/` loads today
LinkedIn returned no 429, no interstitial, no authwall redirect and no degradation across
a burst, and the same posting drew in the middle of the densest burst of the day. A probe
built to detect throttling would be an instrument for a condition that has not been
observed -- and by the register's second law, a check that has never been shown failing
certifies nothing.

**The state that DOES need distinguishing is "this read landed early", and it is now
free.** `BROWSER.last_settle` answers it, and it answers it better than a pre-flight probe
could:

- a pre-flight probe would cost **an extra page load** on the very surface we are trying
  not to hammer, and it would measure a *different* load than the one about to be read;
- `last_settle` costs **nothing** -- it is recorded during a wait that already happens --
  and it describes **the actual read**, not a correlated one.

The right shape here was never "check first, then read". It is "read, and be able to say
what you were looking at". With `last_settle` plus `main_chars` plus the specified
`description_wait`, a refusal carries all three and the caller can tell the three cases
apart without another request.

## Appendix C -- a blind retrodiction the lead can check against his own notes

The client log recorded the lead's calls hours before this wave existed, and it records
durations without recording job ids. So the correlation can be tested against data I had
no hand in generating.

The 13:39-13:51 burst, in full, `job_detail` only:

| time | dur | branch this implies |
|---|---|---|
| 13:40:24 | 1s | early read |
| **13:40:53** | **8s** | **full settle** |
| 13:41:17 | 1s | early read |
| 13:41:33 | 1s | early read |
| 13:41:48 | 1s | early read |
| 13:42:26 | 2s | early read |
| **13:42:49** | **7s** | **full settle** |
| 13:47:54 | 1s | early read |
| 13:48:04 | 1s | early read |
| 13:49:11 | 1s | early read |
| 13:50:15 | 1s | early read |

**There are exactly two full-settle calls in that window, and the lead reports exactly two
successes in it -- Fivetran `4448301715`, "drew fully, twice", around that time.**

So the prediction is: **the two postings that drew were the 13:40:53 and 13:42:49 calls,
and every other call in that burst was a refusal.** If the lead's own record says one of
the successes was a 1-second call, or that a 7-8 second call was refused, then the account
in this document is wrong and should be reopened. I could not check that myself; the log
does not carry arguments.

Note also what this window rules out on its own: the two full-settle calls are separated
by 116 seconds with four refusals sitting between them. No throttle turns off, on, off and
on again at that cadence.

---

## Appendix D -- the capstone: Gunpowder drew, and per-posting eligibility is dead

Probe 14 was taken as a **pre-registered test**: the reasoning in Appendix A said a warm
HTTP cache should make the page find its 500 ms lull more easily, so the FIRST call after
a genuine 300 s idle-close -- a fresh Chromium with a cold cache -- should be much more
likely to take the timed-out branch. I waited the idle-close out with a clock rather than
by estimating, precisely because I had misjudged elapsed time three times already.

| # | time IST | tool | job id | dur | outcome |
|---|---|---|---|---|---|
| 14 | 15:11:42 | job_detail | 4456021840 Gunpowder | **8s** | **DREW FULLY** -- `Lead Software Engineer`, `Gunpowder Innovations`, `Over 100 applicants`, `Actively reviewing applicants`, full description |

**That is the posting that had failed roughly twelve times across two sessions, seven of
them mine within the last twenty minutes.** It drew on the first call that waited.

### The final correlation

| settle branch (from call duration) | n | drew | refused |
|---|---|---|---|
| **slow, 7-8 s** (`networkidle` timed out, flat wait ran) | 2 | **2** | 0 |
| **fast, 1-2 s** (`networkidle` resolved, flat wait skipped) | 12 | 0 | **12** |

Fourteen reads, four postings (Fivetran, Gunpowder, MeridianSquare, plus the lead's),
**perfect separation**. No posting has ever failed a slow-branch read. No posting has ever
survived a fast-branch one.

So, to the three "always fails" postings in the lead's table: they were never postings
that would not render. **They were postings that happened never to be read on the branch
that waits.**

### One nuance the success itself handed over -- carry this into 7.2

The Gunpowder payload drew its description in full while reporting:

```
"company_follow_state": {"state": "unknown", "why": "no follow control rendered. ...
                          the page had not hydrated yet ..."}
"apply_path":           {"route": "unknown", "why": "no apply control rendered ..."}
```

**The description had arrived and the control layer still had not.** That is the
concurrent wave's "the control layer and the text layer render on independent schedules",
confirmed live from the other direction -- they had a page with controls and no
description; this is a page with a description and no controls.

**Consequence for the specified fix:** `wait_for_job_description` fixes the DESCRIPTION and
must not be read as a proxy for hydration. `apply_path` and `company_follow_state` can
still come back `unknown` after it, and on an irreversible path that matters. If those two
fields are wanted reliably they need their own waits on their own anchors, measured the
same way. Do not let one wait be quietly promoted into a readiness check for the page.

---

## 10. Receipts

### Suite

`venv\Scripts\python.exe -m pytest -q` -> **1772 passed, 2 failed in 460.23s**.

**Neither failure is mine, and the arithmetic closes exactly.** Baseline in was 1764 on a
clean tree. The concurrent agent has `tests/test_job_search_fixture.py` **uncommitted**
in this tree (+155 lines, 5 new test functions, one of them parametrized). 1764 + 10 new
cases = 1774 total = 1772 passed + 2 failed. Nothing is unaccounted for.

Both failing names --
`test_a_lone_line_after_the_title_is_the_location_not_the_company` and
`test_a_positional_company_that_repeats_the_metadata_line_is_refused` --
appear as **`+` lines in `git diff tests/test_job_search_fixture.py`**, i.e. they are tests
that agent is writing right now, red against their own in-progress work. They assert on
job-search CARD PARSING; that module does not import `browser` and never constructs one,
and my change adds a dict field to `goto` and a read-only property. My audit file was
untracked when the suite ran, so it contributed no parametrized cases.

**I did not touch their file, and I have not committed it.**

### Boundary compliance

- **Files changed by me: `linkedin_server/browser.py` and my own audit file. Nothing
  else.** `dom.py`, `shape.py`, `server.py`, `writes.py`, `readonly.py` and all of
  `tests/` are untouched -- the fix that belongs in them is SPECIFIED in 7.2/7.3, not
  applied. Committed with explicit paths; no `git add -A`, no `git commit -a`.
- **Reads only. No `confirm_token` was passed to anything, at any point.** Every live call
  was `linkedin_job_detail`, `linkedin_search_jobs` or `linkedin_server_info`.
- **The Chrome profile was never launched from a script.** Every reading came through
  `mcp__linkedin__*` against the already-running server (pid 25376). The only local
  browser used was the test suite's own headless Chromium over frozen HTML.
- **`_state/` untouched.** `_state/session.json` is byte-identical at wave end:
  `sha256 f0892e35688868fa...`, 7813 bytes, mtime Aug 26 00:41. (Prefix only, not the full
  digest: `test_no_committed_identity` rejected a full digest in a sibling audit because
  further into it sits a ten-digit decimal run of mobile shape. Re-derive with
  `sha256sum _state/session.json`.)
- **ASCII-clean**, both files verified by byte scan (0 bytes > 127).
- No `Co-Authored-By`. Committed on `master`. **Not pushed.**

### The running server is STALE with respect to this commit

`linkedin_server_info` reports `build.code.commit d0d3e3b65d52`, process started 14:36:47.
`browser.py` is now ahead of it. **`BROWSER.last_settle` does not exist in the running
process and will not until the MCP client restarts the server** (`/mcp` reconnect). Every
measurement in this document was taken against `d0d3e3b` -- the build the lead handed me
-- so no reading here is contaminated by my own change.

---

## Appendix E -- a prediction of mine that did NOT replicate

| # | time IST | tool | job id | dur | outcome | main |
|---|---|---|---|---|---|---|
| 15 | 15:17:57 | job_detail | 4454627766 MeridianSquare | **3s** | FAIL `missing: description` | 1323 |

Probe 15 was the replication of probe 14: a second genuinely cold browser (no call from
anyone for 375 s, idle-close fired at 15:16:42), on a posting that had never drawn.

**It took the fast branch and refused.** So the cold-cache story I floated in Appendix A --
"a warm HTTP cache makes the page find its 500 ms lull more easily, so cold loads should
take the timed-out branch" -- is **one for two, which is no evidence at all**. I am
striking it. It was a plausible mechanism offered for a single observation, and a single
observation is exactly what this whole investigation kept dying of. **What decides the
branch is still unknown**, and nothing in this document needs it to be known.

**What does NOT weaken, and why the 3 s reading is still unambiguous.** A slow-branch call
cannot finish in under 7 s -- the flat wait alone is 2 x 3500 ms and it runs to completion
-- so **any call under 7 s is proof of the early branch no matter how much cold-start
overhead is folded into it.** Probe 15 is therefore an early read, and it refused, exactly
like the other twelve.

### The correlation after fifteen probes

| settle branch | n | drew | refused |
|---|---|---|---|
| slow (>= 6 s) | 2 | **2** | 0 |
| fast (< 6 s) | 13 | 0 | **13** |

Fifteen reads, four postings, still perfect separation and still no counterexample. The
finding stands; my explanation of *which* branch gets chosen does not, and I have not
substituted another one.

---

## Appendix F -- the consolidated time series

Every live call this wave made, in one place. `gap` is seconds since the previous call to
this server from any agent. Every url is `https://www.linkedin.com/jobs/view/<id>` except
the control. `branch` is inferred from duration and the inference is sound in one
direction absolutely: **a timed-out settle cannot finish in under 7 s**, because the flat
wait alone is 2 x 3500 ms and runs to completion.

| # | time IST | gap | tool | job id | dur | branch | outcome | main |
|---|---|---|---|---|---|---|---|---|
| 1 | 14:50:26 | 17 | job_detail | 4448301715 Fivetran | 1s | early | FAIL `description` | 1348 |
| 2 | 14:50:48 | 22 | job_detail | 4448301715 Fivetran | 8s | **timed out** | **DREW** | -- |
| 3 | 14:52:03 | 75 | job_detail | 4448301715 Fivetran | 1s | early | FAIL `description` | 1348 |
| 4 | 14:54:30 | 147 | **search_jobs** | (control) | 9s | timed out | 7 rows, full | -- |
| 5 | 14:54:42 | 12 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 6 | 14:54:50 | 8 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 7 | 14:54:59 | 9 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 8 | 14:56:49 | 110 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 9 | 14:58:03 | 74 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 10 | 15:01:50 | 227 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 11 | 15:05:30 | 220 | job_detail | 4456021840 Gunpowder | 1s | early | FAIL `description` | 1315 |
| 12 | 15:05:57 | 27 | job_detail | 4448301715 Fivetran | 1s | early | FAIL `description` | 1348 |
| 13 | 15:06:05 | 8 | job_detail | 4454627766 MeridianSquare | 2s | early | FAIL `description` | 1323 |
| 14 | 15:11:42 | 337 | job_detail | 4456021840 Gunpowder | 8s | **timed out** | **DREW** | -- |
| 15 | 15:17:57 | 375 | job_detail | 4454627766 MeridianSquare | 3s | early | FAIL `description` | 1323 |

**Spacing:** minimum gap 8 s, well above the enforced 3 s floor; median 74 s; two gaps
over 300 s taken deliberately to force a browser idle-close. Fifteen job-page loads over
27 minutes. Nothing was hammered, and the two long gaps are experiments, not politeness.

**Every failure is `missing required field(s): description`** -- never `title`, on any of
the fifteen. **Every `main` count is byte-stable per posting** across up to seven repeats.

Commit: `90e1936` on `master`, not pushed, `linkedin_server/browser.py` and this file only.
