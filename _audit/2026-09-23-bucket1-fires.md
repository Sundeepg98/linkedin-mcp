claude-opus-5-5[1m]

# BUCKET 1: the read-direction COVERED-UNFIRED rows, fired once each through attach

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `C41` read COVERED-UNFIRED with *"It has never returned an item"*; it returned eight on its first fire here, with authorship established on all three conditions, and moves to COVERED-PROVEN.

**2026-09-23. Wave `bucket1-live-reads`, base `79c5f8e`. WRITTEN AS THE WAVE
RUNS, not at its end.** One browser slot, ATTACHED to the Chrome already
serving on `127.0.0.1:9224` (started by the orchestrator on the persistent
profile). No Chrome was started, none was killed, no window of the operator's
was closed or navigated. `writes_enabled()` false throughout.

---

## 0. THE PLAN, WRITTEN BEFORE ANY FIRE

### 0.1 The population, taken with the shipped walk and not quoted

`scripts/census_completion.py`'s own `walk()` (which imports `cells`,
`state_of` and `direction_of` from the shipped counter and direction finder)
yields **22 COVERED-UNFIRED rows**, matching its pin `unfired: 22`.

The shipped `direction_of` places them:

    R        5   M M33, M M43, M C41, N 20, N 45
    W       13   P A8, A11, A13, A17, A19, A21; M C1, C25, C32; N 1, 46, 48
    unknown  5   J 103, J 104, J 121, J 122, J 128

**THE FIVE `unknown` ARE ALL `jobs.md`, AND THAT IS A TABLE SHAPE, NOT A
DIRECTION.** `jobs.md`'s per-row table carries no R/W column, so the shipped
finder returns `unknown` for every jobs row (recorded already in
`_audit/2026-09-21-what-is-reachable-now.md` section 0). The slice keeps its
directions in section 2's ROW-RANGE table, which reads **`116-126 ... | R`** --
so `J 121` and `J 122` are reads by the slice's own record. `J 103` (follow a
company), `J 104` (unfollow a company) and `J 128` (message the job poster) are
writes by their own capability text, and their twins in the network slice
(`N 46`, `N 48`) carry `W` in the shipped cell.

**IN SCOPE: 7 read rows** -- `J 121`, `J 122`, `M M33`, `M M43`, `M C41`,
`N 20`, `N 45`. The 15 write rows stay UNFIRED and are not touched. `N 134` and
`P O3` (bucket 1's two still-GAP press rows) are a sibling wave's and are not
touched.

### 0.2 Each in-scope row, priced BEFORE firing

| row | reader | prior fire | what stands in the way | plan |
|---|---|---|---|---|
| `J 121` | `linkedin_job_detail` -> `dom.read_job_insight_panels` | 2026-09-20, 11 postings, NOT BANKED: percentile 0 of 11, behind `Show Premium Insights` (a press) | the value lives behind a control this wave may not press | re-fire through the SHIPPED harness `scripts/_probe_unfired_job_detail_insights.py` (planned unmodified; 0.3 records why it was repaired before it ran) |
| `J 122` | the same | same run, PARTIAL: seniority/education arrive, skills 0 of 11 | half the capability was never drawn | the same run |
| `M C41` | `linkedin_my_activity_items` | 2026-09-20, REFUSED `self_assertion_unreadable` | a refusal is not a bank | re-fire through the SHIPPED harness `scripts/_probe_unfired_self_reads.py` (checked first: it also fires the already-PROVEN `M M45`) |
| `M M33` | `linkedin_open_messaging(message_filter=...)` | never | **standing ruling `DO-NOT-OPEN-MESSAGING`** (`_audit/RULINGS.md`, address family, binds `/messaging/`) | NOT FIRED. A ruling, not a judgement of this wave |
| `M M43` | `linkedin_open_messaging` | never | the same ruling | NOT FIRED |
| `N 20` | `linkedin_notifications` | never | loading `/notifications/` CLEARS THE UNREAD BADGE, measured 1 -> 0 on 2026-08-21, irreversible (the tool's own docstring). Not a pure read | NOT FIRED without the operator. Price the ruling instead (section 2) |
| `N 45` | `linkedin_notifications` | never | the same | NOT FIRED |

**FORCED PREDICTION, logged before the first fire:** 0 of 7 move to
COVERED-PROVEN. `J 121` fails on the press, `J 122` on the missing skills half,
`M C41` repeats a refusal unless its code changed since 2026-09-20, and four
rows are not fired at all.

---

### 0.3 Two harness defects fixed BEFORE any fire, committed first (`599a0cb`)

**TWO OF THE SHAS IN THIS DOCUMENT ARE BRANCH-ONLY TODAY.** `599a0cb` and
`abd5d75` are this wave's commits on its worktree branch and do not resolve
on `master` until that branch merges. Their subjects, which survive a rewrite:
*"probes(unfired): stop at the first anomaly, and fire one self-read alone"*
and *"probes(unfired): an anomaly keeps its envelope, so it can be read at
zero loads"*.

Reading the two harnesses before running them found that **neither stopped at
an anomaly**. `_probe_unfired_job_detail_insights.py` counted an error
envelope under "errors by type" and went on to the next posting, so a login
wall or a throttled page met mid-run would have been answered with more page
loads into the same session -- the opposite of this wave's stop rule. And
`_probe_unfired_self_reads.py` fires `M M45` and `M C41` together, while only
`M C41` is in scope (`M M45` is COVERED-PROVEN), so re-measuring `M C41` would
have loaded the composer again for nothing.

Both repaired in the harnesses themselves rather than by writing a new one:

* `_anomaly(out)` -- ANY error envelope stops the run with no further page
  load, not even the closing control. Deliberately not only
  `not_authenticated`: a 999 or a throttled page draws nothing and arrives as
  `extraction_failed`, and no HTTP status travels in the envelope to tell it
  from a flake. A refusal is a result and does not stop the run. The
  self-reads harness imports it from its sibling rather than copying it.
* `--only C41` / `--only M45` on the self-reads harness, decided before the
  browser is touched; a bad value refuses rather than falling back to both.

Six tests in `tests/test_unfired_probe_verdicts.py`, **shown failing** under
four planted defects, each restored by sha256 before the next:

    BASELINE                                              24 passed
    A  _anomaly never reports a kind                      3 failed, 21 passed
    B  _anomaly returns the MESSAGE, not the kind         1 failed, 23 passed
    C  a bad --only value falls back to BOTH rows         1 failed, 23 passed
    D  a refusal is treated as an anomaly                 2 failed, 22 passed
    RESTORED                                              24 passed

The script-scanning guards over the edited files (decorative controls, the
tab-leak ratchet, page text never printed, import safety, navigation and
interaction budgets, redaction, filter channels): **314 passed**.

### 0.4 STEP 0 -- the session, measured before any fire

One read through the attach path at **16:27:09**: the harness's own CONTROL
(`_control_serves`, the jobs search), with the shipped authwall detector and a
closed list of challenge phrases read off the same page at zero further
loads. `linkedin_cdp_status` first, which touches nothing on LinkedIn.
Instrument: a scratch preflight, declared disposable -- it fires no
capability and banks nothing.

    provenance         worktree HEAD 599a0cb; linkedin_server imported from
                       this worktree; CDP_ATTACH True, 127.0.0.1:9224;
                       writes_enabled() False
    sha256[:16]        server.py 1015d0ff3d009fda  dom.py 75af40c9fecaa62c
                       notify_cost.py 1e2ba3575406d0c1
    cdp_status         reachable True, Chrome/153.0.8010.53, mode attach
    control serves     True; landed path still /jobs/search; 7 job cards
    authwall marker    None      (config.AUTHWALL_MARKERS: /login, /authwall,
                                  /uas/login, /checkpoint/)
    challenge phrases  none of 9 present (unusual activity, security
                       verification, captcha, restricted, too many requests...)
    VERDICT            signed in, clear to fire

**TWO BADGES READ UNREADABLE ON THAT PAGE, AND NEITHER IS A ZERO.** The
invitation badge: `badge_links` 0, so the harness's before/after consumption
control will report UNKNOWN at that end, as it did on 2026-09-20. The
notifications badge (`notify_cost.read_notifications_badge`, the shipped
reader): `links` 1, `badge_links` 0, so `measurability` says **unreadable**
-- the nav drew the notifications link with no count tail. Either nothing is
unread or the nav had not drawn a count; the module refuses to read that as
zero and so does this wave. **So the price of the `N 20` / `N 45` ruling
(section 2) could not be taken today from this page.** No extra page load was
spent to try: the nav is the same nav on every page.

---

## 1. THE FIRES

### FIRE 1 -- `M C41`, View your own activity feed. Direction R. **PROVEN.**

    fired      16:28:24-16:28:58, scripts/_probe_unfired_self_reads.py --only C41
               at 599a0cb, attach 127.0.0.1:9224
    reader     server.linkedin_my_activity_items -> /in/me/, clicks nothing
    loads      control 1 + /in/me/ 1 (pages_loaded 1) + closing control 1
    outcome    RETURNED -- the first time this tool has returned items on any
               recorded run (every earlier one refused, three ways:
               no_page_owner_heading, no_self_assertion,
               self_assertion_unreadable -- the last on 2026-09-20)

**THE SHAPE is exactly the documented success shape** -- the docstring's
"an authorship block, counts, item_root_source and pages_loaded ... plus items
and anchors_per_item only when authorship was established": seven top-level
keys, those six plus `note`, and no `refused`.

**THE FIELDS WHOSE MEANING WAS CHECKED**, from the raw capture
`_state/unfired-self-reads-raw.json` (gitignored, in this wave's worktree),
read by a scratch reader that prints booleans, integers and this package's
own tokens and never an item:

    authorship.established         True -- and it is a CONJUNCTION, not a
                                   default; each of its three conditions is
                                   reported and each was read:
      self_assertion_present       True   LinkedIn's own isSelfProfile rode on
                                          the FIRST load (pages_loaded 1)
      authors_found / unanimous    1 / True   across 8 overflow controls
      matches_page_owner           True   named by owner_source
                                          'document-title' (owner_headings 0)
    items                          8, all 8 anchored urn:li:activity:<digits>,
                                   8 distinct
    the reader's own counters      distinct_urns 8 = len(items) = overflow_controls 8
                                   unrecognised 0, unpaired 0
                                   per-item anchors [4,4,2,2,2,2,2,2] sum 20
                                     = counts.permalink_anchors 20
                                     = item_root_source climb 20
                                   anchors_per_item keys = items, as a set

**`owner_headings 0` WITH `owner_source` 'document-title' IS THE SHAPE THE
CODE PREDICTED FOR A LIVE PROFILE**, in `server._authorship_block`'s own
comment: *"None here beside a non-null owner_source is the live profile's
exact shape -- no heading names anybody, the title does."* A prediction made
before this fire, met by it. The recorded `no_page_owner_heading` refusal is
the h1 route finding nothing, from before the title route existed; the title
route (`7e7c728`, 2026-08-31, *"the live profile names its owner in the title,
and in nothing else"*) is what named the owner here.

**WHAT DISCRIMINATES.** A dead or blind reader of this surface does not return
an empty list -- it REFUSES, carrying no `items` key at all, which is what
every earlier run did. This run returned eight distinct, anchored, paired keys
whose three independent counters (anchors, overflow controls, climbed roots)
reconcile with the published list.

**THE CAVEATS, which go into the cell with the bank:**
* **n = 1 fire.** The brief is one fire per row. `isSelfProfile` is measured
  TRANSIENT (2026-09-02: absent then true seconds apart), so a later run may
  refuse again; that would be a reliability fact, not a retraction of this
  one -- COVERED-PROVEN means *recorded working live*, and this is that record.
* **FIRST RENDER ONLY, KEYS ONLY, HIS OWN AUTHORED ITEMS ONLY** -- all three by
  design and in the tool's own `note`. Post text is out of scope by
  `FEED-CONTENT-READ-RULING` (row `C43`, EXCLUDED-RULED on it). An item absent
  here is unknown, not unwritten.
* **"HIS" RESTS ON THE TOOL'S OWN IN-PAGE COMPARISON.** I read the three
  reported facts; I did not re-derive the author comparison independently,
  because doing so means reading a name.

**CONSUMPTION CONTROL:** invitation badge BEFORE UNREADABLE (`badge_links` 0
on the jobs page), AFTER READABLE, so the harness reports UNKNOWN -- the same
shape as 2026-09-20. The tool clicks nothing by construction; that is the
stronger guarantee and the only one this run has.

**A CONSEQUENCE, RECORDED NOT ACTED ON.** This tool is, in its own docstring,
*"THE AIMING READER"* for `linkedin_comment_on_item` and
`linkedin_react_to_item`, which were *"UNAIMABLE: no other tool here returns an
item key"*. It now demonstrably returns them, for his own posts. Row `M C42`
(EXCLUDED-RULED) still reads *"no tool in this server returns one"*; that
premise is now false for his own items. Both writes stay unfired under
`NO-IRREVERSIBLE-WRITE-IS-FIRED`; the stale premise is for the owner of `C42`.

### FIRE 2 -- `J 121` and `J 122`. Direction R. **VOID: THE STOP RULE FIRED.**

    fired      16:31:35-16:32:47, scripts/_probe_unfired_job_detail_insights.py 10
               at 599a0cb, attach 127.0.0.1:9224
    loads      control 1, harvest searches (10 ids), job_detail x2
    outcome    posting 1: insights dict arrived, 7 keys
               posting 2: ANOMALY extraction_failed -> EVERY FURTHER FIRE
               STOPPED, no closing control, exit 1

**THE RULE ADDED AT `599a0cb` DID EXACTLY WHAT IT WAS ADDED FOR, ON ITS FIRST
LIVE RUN.** Before that commit this probe would have counted the failure under
"errors by type" and loaded eight more postings into whatever the session had
become. `extraction_failed` from `linkedin_job_detail` is raised when the page
LOADED -- the authwall check had already passed, so it was not a login or
checkpoint landing -- but no posting could be read from it: a render race
(the description not yet drawn, measured 13 of 13 on the early-settle branch
on 2026-08-30), a closed or removed posting, or a throttled page that drew
nothing. **Nothing in the envelope's kind separates those three.**

**AND MY OWN EDIT HAD A HOLE, FOUND BY THIS RUN.** The anomaly path wrote
nothing to `_state/`, so the envelope that DOES separate them --
`shape.job_detail_failure_note` puts `main_chars` and the settle branch into
its message -- was thrown away with the run. The only way left to classify the
anomaly was another page load, which is precisely what a stop is for
preventing. Fixed at `abd5d75`: the envelope and the postings read before it
are now written to the gitignored `_state/`, printing nothing more; shown
failing under two further planted defects (the record dropping the envelope;
the exception text carrying it), all six mutations red, restored green.

**NO ROW MOVES ON THIS RUN.** One panel is not a sample, and a run that
stopped is VOID by its own rule.

**THE ANOMALY WAS CLASSIFIED BEFORE ANYTHING ELSE FIRED.** After a 4.5-minute
pause, ONE health read -- the same Step-0 preflight, at `abd5d75`, 16:37:19:

    control serves True; landed path still /jobs/search; 7 job cards
    authwall marker None; challenge phrases none of 9
    VERDICT  signed in, clear to fire

So it was not a login, checkpoint or challenge landing, and the session was
serving normally minutes later. **Posting-level, not session-level** -- which
still does not say WHICH of the three posting-level causes it was; the envelope
that would have said so is the one `abd5d75` now keeps. One bounded re-fire
follows, and it is the last for these two rows whatever it shows.

### FIRE 3 -- `J 121` and `J 122`, the bounded re-fire. **VOID AGAIN, SAME POSITION. NOT PROVEN.**

    fired      16:37:54-16:39:00, the same harness at abd5d75, sample 10
    loads      control 1, harvest searches, job_detail x2
    outcome    posting 1: insights dict arrived, 7 keys
               posting 2: ANOMALY extraction_failed -> stopped, envelope KEPT

**THIS TIME THE ANOMALY WAS CLASSIFIED FROM DISK, AT ZERO PAGE LOADS**, from
`_state/unfired-job-detail-insights-raw.json` (gitignored, in this wave's
worktree), by a scratch reader that parses only integers and
closed-vocabulary tokens out of the package's own failure note
(`shape.job_detail_failure_note`):

    missing required fields   description        (title present)
    main_chars                8785    -- the package's own DRAWN range is
                                         5600-18400; UNDRAWN is ~1100-1400
    settle                    networkidle_timed_out, 7012 ms (the full branch)
    description wait          "WAITED FOR AND NEVER ARRIVED (10016ms, the
                              full bound)"

The note itself names the discriminating next step: *"Call linkedin_job_detail
on a second posting: if that fails the same way, it is the selector."* **That
test had already run, twice, one posting earlier:** posting 1 read in full in
the same session seconds before, on both runs. So this is not a renamed
component, not an early read, and not the session (the control served at
16:37:19). **It is a posting whose page draws and whose description this
reader never finds.** That FIRE 2 stopped on the SAME posting is INFERRED,
not measured: both runs harvest with the same terms and both stopped at
position 2, but FIRE 2 kept no envelope, and this repository has measured the
search drifting 2 of 7 ids between identical requests -- so it may have been a
second posting of the same kind.

**WHAT THAT COSTS, STATED AGAINST MY OWN CLAIM.** The `_anomaly` docstring I
wrote at `599a0cb` said *"The cost of stopping on a harmless flake is one
re-run."* Measured here, that is not so: a posting-level miss that is not a
flake stops the harness wherever the harvest puts it, and on both runs today
that was position 2, so no sample past posting 1 was reachable. The sentence
is replaced in the docstring itself, in the commit after this document's
first, rather than left in shipped source. The rule is still the right default -- the alternative is loading pages into a
session nobody has classified -- and the repair is not to loosen it but to
let the harness CLASSIFY before it decides: on `extraction_failed`, read the
control once (exactly the health read taken by hand above) and continue only
if it serves with no authwall marker. **Proposed, not built:** it is a change
to the stop semantics, and a control flow that has never run live should not
be shipped by the wave that would also be its first user.

**THE ONE PANEL THAT WAS READ, reported by tally only and too thin to judge
anything alone** -- it agrees in STRUCTURE with the 11-posting reading of
2026-09-20 and adds nothing that could move either row:

    applicant_insights sub-keys   heading, metrics, seniority, education
                                  (no skills sub-key -- a property of the
                                   READER, identical to 2026-09-20)
    tokens                        percentile 0, rank 0, skill 0, % 1
    'Show Premium Insights'       not drawn on this one posting

**VERDICTS, per row:**
* **`J 121` NOT PROVEN.** The run is VOID by its own rule. The standing reason
  is unchanged from 2026-09-20: the percentile lives behind a gated control
  this reader does not open, and pressing is out of this wave's scope.
* **`J 122` NOT PROVEN.** Same. The skills half cannot arrive through this
  reader at all -- `applicant_insights` has no skills sub-key, so a live
  sample of any size could only show the token inside `heading` or `metrics`
  text. That is a reader change, not a session.

**THE CENSUS CELLS OF `J 121` AND `J 122` ARE LEFT AS THEY ARE.** Their 2026-09-20
text is still accurate, and one panel is not new evidence.

---

## 2. THE FOUR IN-SCOPE ROWS THIS WAVE DID NOT FIRE, AND WHY EACH IS NOT MINE TO FIRE

All four are READ-ONLY by the write gate's classification. **None of them is a
pure read**, and the brief this wave ran under says never to take an action
whose effect is not one. Each is priced below so the decision that would move
it can be taken once.

### `M M33` (apply an inbox filter pill) and `M M43` (open the inbox and list conversations)

Reader: `linkedin_open_messaging`. **Blocked by a standing ruling, not by this
wave's judgement:** `DO-NOT-OPEN-MESSAGING` (`_audit/RULINGS.md`, address
family, binds `/messaging/`, 2026-08-31): *"Opening it opens a conversation
LinkedIn chooses and can mark a real person's InMail read -- a cost paid on
somebody else."* `/messaging/` does not stay on a list; it redirects into one
conversation of LinkedIn's choosing (measured twice, stated on the tool). No
row-level evidence can be gathered without spending a stranger's read state.
**What would move them:** the operator lifting or narrowing that ruling. Not a
browser slot.

### `N 20` (notified when a member invites you) and `N 45` (notified when a non-connection follows you)

Reader: `linkedin_notifications`. **Blocked by a measured, irreversible cost
on HIS account:** loading `/notifications/` clears the unread badge -- 1 -> 0
on 2026-08-21, "it does not come back" (the tool's own docstring, which calls
it *"the only server-side change any READ in this package causes WITHOUT BEING
ASKED FOR IT"*). `_audit/2026-09-20-the-unfired-twentyseven.md` section 8
declined these two rows on the same ground; this is the SECOND wave to reach
them, so the blocker is priced rather than re-reported:

* **THE COST** is his unread notifications, whatever they number at the moment
  of the load. **It could not be read today:** the shipped
  `notify_cost.read_notifications_badge`, run on the control page at 16:27,
  saw the notifications link (`links` 1) carrying no count (`badge_links` 0),
  and `notify_cost.measurability` reports that as `unreadable`, never as zero.
* **THE YIELD IS NOT GUARANTEED.** A fire proves `N 20` only if the list it
  returns holds an invitation-kind row, and `N 45` only if it holds a
  follow-kind row. Which kinds are in his list today is unknown until the page
  is loaded -- which is the spend.
* **WHAT WOULD MOVE THEM:** one ruling from him -- *may one
  `linkedin_notifications` call spend the unread state, on a day he picks?* --
  after which the fire is one page load, and `notify_cost.cost_delta` (which
  has no caller yet, by design) can take the before/after pair in band for
  free.

**THE CENSUS CELLS OF ALL FOUR ARE LEFT AS THEY ARE.** The two messaging rows
already cite the decline; the two network rows name only the tool, and the
reason is recorded here and in `_audit/2026-09-20-the-unfired-twentyseven.md`
rather than written into a cell whose state is not moving.

---

## 3. BUCKET 1'S PREMISE, MEASURED ROW BY ROW -- AND IT HOLDS FOR NONE OF THE 21 LEFT

`scripts/census_completion.py` describes bucket 1 as *"BLOCKED ON A LIVE
BROWSER SESSION ... A session is the entire remaining cost, by definition of
the state -- no ruling, no design, no build."* Classified by what actually
stands in front of each of the 22 COVERED-UNFIRED rows this wave began with:

    moved to COVERED-PROVEN by a session                     1   M C41
    WRITE -- NO-IRREVERSIBLE-WRITE-IS-FIRED (a ruling)       15   J 103, 104, 128; P A8, A11,
                                                                  A13, A17, A19, A21; M C1,
                                                                  C25, C32; N 1, 46, 48
    READ -- DO-NOT-OPEN-MESSAGING (a ruling)                  2   M M33, M M43
    READ -- spends HIS unread state (his decision)            2   N 20, N 45
    READ -- a press, or a reader change (a build)             2   J 121 (percentile behind a
                                                                  gated control), J 122 (the
                                                                  reader has no skills key)
                                                            --
                                                            22

**So a session was the whole remaining cost for exactly one row, and it has
now been paid.** For every one of the 21 that remain, the next cost is a
ruling or a build. The state word is right about each row -- the tool ships
and has not returned its payload live -- but *"a session is the entire
remaining cost"* is a claim the state cannot carry. Reported, not edited:
`census_completion.py` belongs to a sibling wave, and the correction is its
owner's to word.

---

## 4. THE LEDGER

    in-scope read rows                                  7   J 121, J 122, M M33, M M43,
                                                            M C41, N 20, N 45
    rows moved to COVERED-PROVEN                        1   M C41
    rows fired and NOT proven                           2   J 121, J 122 -- two runs, both
                                                            VOID at posting 2 by the stop rule
    in-scope rows not fired                             4   M M33, M M43 (ruling);
                                                            N 20, N 45 (his unread state)
    write rows touched                                  0   of 15
    N 134 / P O3 touched                                0
    rows inflated                                       0
    LinkedIn page loads, all serial                    15   step 0: 1; FIRE 1: 3; FIRE 2: 5;
                                                            health read: 1; FIRE 3: 5
                                                            (5 = control + 2 harvest
                                                            searches + 2 postings; the 2 is
                                                            DERIVED from the 7-card window
                                                            against 10 ids wanted)
    presses, clicks, fills, keys                        0
    tabs leaked                                         0   cdp_targets: 1 page before and
                                                            after, not one of this wave's
    raw captures committed                              0   all under the gitignored _state/
    harness defects found and fixed before/while firing 3   no stop on anomaly; the composer
                                                            re-fired needlessly; the anomaly
                                                            envelope discarded
    forced prediction                                   0 of 7   ACTUAL 1 of 7

**THE PREDICTION MISSED ON `M C41` AND THE MISS IS INFORMATIVE.** I predicted a
repeated refusal because no line of the tool's code had changed since
2026-09-20. The code did not need to: `isSelfProfile` is measured TRANSIENT
(absent then true seconds apart, 2026-09-02), it rode on the first load today,
and the `document-title` route -- added 2026-08-31 -- named the owner that the
h1 route never could. **"The code is unchanged" was evidence about the tool
and none about the page.**

### 4.1 THE NEW FIGURES, re-derived, not quoted

`scripts/census_completion.py` (all four slices, 704 stated rows):

                              before (79c5f8e)     after (this wave)
    DELIVERED, strict         74 / 704  10.5%      75 / 704  10.7%
                              74 / 389  19.0%      75 / 389  19.3%
    DELIVERED, broad          96 / 704  13.6%      96 / 704  13.6%   (unchanged:
                              96 / 389  24.7%      96 / 389  24.7%    UNFIRED -> PROVEN
                                                                      stays inside broad)
    COVERED-UNFIRED           22                   21
    bucket 1, named           24                   23
    ADJUDICATED               430 / 704            430 / 704
    GAP                       274                  274

**`--check` IS RED ON EXACTLY TWO PINS, AS THE BRIEF SAID IT WOULD BE:**

    delivered_strict       pinned    74   now    75   (+1)
    unfired                pinned    22   now    21   (-1)

**NOT RE-PINNED** -- that file belongs to a sibling wave and the re-pin is the
orchestrator's at the serial merge. `scripts/count_census_states.py --expect
J=56,P=55,M=77,N=86` MATCHES on every slice and on the GAP control (274); the
messaging slice moves COVERED-PROVEN 5 -> 6 and COVERED-UNFIRED 6 -> 5, stated
rows 142 -> 142.

---

## 5. WHAT NEEDS THE OPERATOR

1. **`N 20` / `N 45`: may one `linkedin_notifications` call spend his unread
   notification state?** The cost is irreversible and could not be priced
   today (the badge read `unreadable`, not zero). The yield is conditional on
   the kinds in his list. A yes makes these a one-page-load fire; a no is a
   ruling that should then be written down, so a third wave does not reach
   them again.
2. **`M M33` / `M M43`: nothing to decide unless he wants to revisit
   `DO-NOT-OPEN-MESSAGING`.** Listed so the rows stop reading as "needs a
   session".
3. **Nothing live is owed for `J 121` / `J 122`** -- they need a sanctioned
   press (the percentile) and a reader change (the skills half), not a
   ruling from him and not another session.

## 6. WHAT THIS WAVE DID NOT DO

* Fired nothing that writes, pressed nothing, opened no messaging surface,
  loaded no notifications page.
* Did not edit `scripts/census_completion.py`, did not re-pin, did not touch
  `N 134` / `P O3`, did not push.
* Did not build the control-on-anomaly step proposed in FIRE 3.
* Did not fire `M M45`: it is COVERED-PROVEN, and `--only C41` exists so that
  re-measuring its neighbour no longer loads the composer.
* Chrome on 9224 was attached to and left serving; it was never started,
  navigated in any tab but this wave's own, or stopped.

## 7. THE GATE

Committed first, then `scripts/impact_gate.py --against 79c5f8e`, the scoped
gate over the wave's three commits, verbatim where it matters:

    impact-gate: 9 changed path(s) -> 51 SELECTED + 17 corpus-wide = 51 test file(s).
    REFUSED: a test this change can reach is RED.
        FAILED tests/test_the_rulings_register_is_derived.py::test_the_committed_register_is_what_the_corpus_derives
        FAILED tests/test_a_cited_sha_resolves.py::test_no_new_unresolvable_citation_appears
        2 failed, 2334 passed in 253.11s (0:04:13)
      NOT CHECKED: 163 of 214 test files (76.2% of the suite by file).
      That is roughly 3758 of 6094 tests unrun (61.7%), against a suite count
      taken 2026-09-20 at 970a276.

**BOTH REDS WERE MINE AND BOTH WERE RIGHT.**

1. **The rulings register.** I edited this document in the working copy after
   the commit (the END STATE section), and its wording moved two of the
   register's scan counts; the committed `RULINGS.md` had been derived before
   that edit. Regenerated with `scripts/build_rulings_index.py --write`, never
   hand-merged, and swept twice until nothing moved.
2. **The cited SHAs.** `599a0cb` and `abd5d75` sit on this wave's branch only,
   and the guard's predicate is ancestry of `master`, not existence. Its own
   remedy, taken: disclose it and record the subjects (section 0.3) -- and do
   not delete the hash.

**What the gate did NOT run is stated by the gate:** 163 of 214 test files.
Its 17 corpus-wide guards ran unconditionally, but four of their sweeps (the
identity shape and exact-value sweeps, and two navigation sweeps) answered on
the CHANGE rather than the whole tree, by the gate's own design -- an
induction step whose base case is the whole-tree run in CI, which this
branch has not had: it is not pushed, by the brief. **The re-run over the
corrected range is reported in the wave's final message rather than here** --
a document cannot quote the gate that checks the document's own last edit,
and this is where that recursion stops.

## 8. END STATE

**MOVED TO COVERED-PROVEN: 1** -- `M C41`.

**NEW CENSUS FIGURES** (`scripts/census_completion.py`, 704 stated rows,
achievable surface 389):

    DELIVERED, strict    75 / 704  10.7%     75 / 389  19.3%     (was 74)
    DELIVERED, broad     96 / 704  13.6%     96 / 389  24.7%     (unchanged)
    COVERED-UNFIRED      21                                      (was 22)

**ROWS NOT PROVEN, AND WHY -- 6 of the 7 in scope:**

    J 121   fired twice, both VOID at posting 2 by the stop rule; the
            percentile sits behind a gated control (a press, out of scope)
    J 122   the same runs; the reader carries no skills sub-key (a build)
    M M33   not fired -- DO-NOT-OPEN-MESSAGING (a standing ruling)
    M M43   not fired -- DO-NOT-OPEN-MESSAGING (a standing ruling)
    N 20    not fired -- loading notifications clears HIS unread badge,
            irreversibly (his decision); yield also conditional on the kinds
            in his list
    N 45    not fired -- the same

**NEEDS AN OPERATOR RULING: one** -- may a single `linkedin_notifications`
call spend his unread notification state (`N 20`, `N 45`)? Everything else
left in bucket 1 needs a build, a sanctioned press, or a ruling that already
exists; none of it needs another session.
