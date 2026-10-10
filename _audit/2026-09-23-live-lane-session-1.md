# THE LIVE LANE, SESSION 1

**2026-09-23. Wave `live-lane-session-1`, base `c8fa6ea`. WRITTEN AS THE WAVE
RUNS, not at its end.** This lane is the only agent that drives the browser.
The brief is the orchestrator's re-brief of 22:00 IST: build four readers or
presses offline, then fire a priority queue live, under the 2026-09-23
rulings registered in `scripts/build_rulings_index.py`.

Live rules this session runs under: the attached Chrome on `127.0.0.1:9224`
only, its own tab only, never started, restarted or closed; at most 40
LinkedIn page loads, serial, at least 20 seconds apart
(`LIVE-BUDGET-40-LOADS`); stop at the first login page, checkpoint, captcha
or challenge; no outward write (`OPERATOR-NAMES-THE-TARGET` holds all nine);
raw captures only under this worktree's gitignored `_state/`.

---

## 0. THE PLAN, WRITTEN BEFORE ANY BUILD OR LOAD

### 0.1 Three calls the brief carries, recorded as it asked

- **DECIDED (orchestrator-delegated, 2026-09-23):** "Show more analytics"
  (a plain button) is permitted as a DISCLOSURE, provided a before/after
  reading shows it only reveals content and changes no state.
- **DECIDED (orchestrator-delegated, 2026-09-23):** `M C72`'s copy-link is
  proven on the operator's OWN posts only (`M C41`'s activity ids), so no
  other author's share figures are touched.
- **DECIDED (orchestrator-delegated, 2026-09-23):** `M C85`'s poll address
  comes from tool arguments only. If one of his OWN posts carries a poll, use
  it; otherwise record NEEDS-TARGET and move on.

### 0.2 The rows, as their cells stand at `c8fa6ea`

    queue  row              state            tool or mechanism named in the cell
    1      P G6             COVERED-UNFIRED  linkedin_creator_analytics -> per_post (lane L1)
    2      M M43            COVERED-UNFIRED  linkedin_open_messaging
    2      M M33            COVERED-UNFIRED  linkedin_open_messaging(message_filter=...)
    3      N 20             COVERED-UNFIRED  linkedin_notifications -- proves only if an
                                             invitation-kind item is in his list today
    3      N 45             COVERED-UNFIRED  linkedin_notifications -- only if a follow-kind item is
    4      M M49            GAP              none: "blocked on a reader plus the cost of opening
                                             somebody's thread"
    5      N 134, P O3      GAP (gate PRESS) none: the view-switch and the insights press
    6      M C72            GAP (gate PRESS) none: the copy-link press
    --     M C85            GAP (gate RULING) none: a poll address, now DECIDED (0.1)
    7      P A8 A11 A13     COVERED-UNFIRED  linkedin_update_profile_field (a WRITE, two-step
           P A17 A19 A21                     token), linkedin_profile_editor_values (its restore read)
    8      P A25 P L1 P L8  GAP, NEEDS-      scripts/_probe_l1_admitted_reads_live.py keys contact,
           M C48 M C38      CAPTURE          audience, overview, articles, post_summary

### 0.3 What reading the shipped code found BEFORE anything was built or loaded

1. **`/messaging/` never stays on a list.** `linkedin_open_messaging`'s own
   docstring: it "redirects into ONE SPECIFIC CONVERSATION, and LinkedIn
   chooses which". So a fire cannot PREFER an already-read thread, which is
   what `OWN-INBOX-READS-COVERED-BY-B` asks of the live lane; LinkedIn picks
   the landing. What CAN be read first, at zero messaging cost, is
   `linkedin_new_messages`: the messaging badge off `/feed/`, which counts
   NEW-SINCE-LAST-VISIT. **The lane's rule, written before any load:** open
   `/messaging/` only when that badge reads exactly 0. A number above 0 means
   something has landed that he has not looked at, and the landing would
   most likely open it -- spending both his unread marker and a possible read
   receipt on a message he has not seen. `null` (badge not drawn) is not 0
   and does not pass. A 0 is not proof the landing thread is read (the tool
   says so itself); the residue is (b)'s, and is reported rather than smoothed.
2. **`M M33`'s pill press is a closed set of seven.** `unread`, `inmail`,
   `jobs` and `other` are the pills likeliest to put an unread thread first.
   The pill this lane presses is `starred`: a conversation he starred is one
   he has read. An empty starred list is a weaker proof and will be reported
   as such.
3. **`linkedin_notifications` clears his unread badge on load**, permitted by
   `NOTIFICATIONS-UNREAD-SPEND`. One load serves `N 20` and `N 45`; each
   proves only if its kind of item is in his list today.
4. **ITEM 7 CANNOT SAVE, and the reason is in the shipped write path, not in
   a guess.** The ruling's first condition is "notify network is confirmed
   off in the edit dialog BEFORE saving". `linkedin_update_profile_field`'s
   own spec (`writes.py`, its `residue`) says: "LinkedIn notifies a network
   about some profile changes, which is a broadcast this server has not
   measured and would not control." Nothing in `writes.py` reads or sets a
   notify toggle (searched: `notify`, `share with network`, `broadcast`). So
   the perform step cannot confirm the condition at save time, and making it
   do so is an edit to `writes.py`, which lane L4 holds. **Planned outcome
   for all six: NOT SAVED, condition 1 unprovable through the shipped write
   path.** What this lane can do at zero writes is read the intro editor's
   controls (`linkedin_profile_editor_fields`) and report whether a notify
   toggle is drawn there at all -- the measurement lane L4 would need.
5. **The package already spaces navigations.** `BROWSER.goto` waits
   `LINKEDIN_MIN_INTERVAL_S` (default 3.0) between loads in one process,
   tool-internal retries included. This session runs with it at `20`, and
   the session harness enforces the same gap ACROSS processes from a ledger
   on disk.
6. **Activity ids.** `linkedin_my_activity_items` returns real item keys for
   his own posts (authorship established three ways on every call). If those
   keys are not ACTIVITY urns, lane L1 names the fallback: the post-summary
   links on `/analytics/creator/content/`. Every id goes to `_state/` only,
   and reaches a tool as a caller-supplied argument, never as a navigation
   the package derives.

### 0.4 ORDER OF WORK, AND THE ONE DEPARTURE FROM THE BRIEF'S PHASING

The brief says build first, then fire. **Queue items 1-3 and the activity-id
read need no build**, and the build for item 4 (`M M49`) is a reader for a
page no capture in this repository has ever drawn -- a reader written before
that page is seen is a guess about LinkedIn's DOM. The item-2 fire loads that
page anyway. So:

    1. fire items 1-3 (tools already shipped); capture on the same loads
       (the /feed/ of the badge read and /notifications/ are lane Y items 1
       and 3; the messaging landing is item 4's missing capture)
    2. build (a) view switch, (b) insights disclosure, (d) copy-link offline,
       and (c) against the capture from step 1
    3. fire items 4, 5, 6
    4. item 7 at zero writes (0.3 point 4), then items 8, 9 as budget allows

Items 1-3 lead the priority order anyway, so this departs from the
phasing only, not from the order. Nothing downstream is fired before its
build.

### 0.5 The load budget, allotted before any load

    item   what                                                  loads (planned)
    1      linkedin_creator_analytics (P G6)                        1
    2      linkedin_new_messages (badge, + /feed/ capture)          1
    2      linkedin_open_messaging (M M43, + landing capture)       1   only if badge == 0
    2      linkedin_open_messaging(starred) (M M33)                 1   only if badge == 0
    3      linkedin_notifications (N 20, N 45, + capture)           1
    ids    linkedin_my_activity_items (for C72, C38, C85)           1-2
    4      M M49 fire                                               1   only if badge == 0
    5      N 134 / P O3: open-form capture, fire, verify reload     3
    6      M C72 on his own post                                    1
    7      intro editor fields, zero writes                         1-2
    8      L1 harness: 5 keys + 2 control                           7
           ------------------------------------------------------------
           planned                                               19-21 of 40
    9      lane Y's list, remainder                               <= 19

### 0.6 Stop rules

A login page, checkpoint, captcha or challenge phrase ends the session with
no further load. An error envelope, or an exception from a tool, stops the
queue until it is diagnosed offline; a refusal is an answer, not an anomaly.
The ledger refuses a navigation that would be the 41st.

### 0.7 FORCED PREDICTION, logged before the first load

Of the nine rows a fire can prove this session (`P G6`, `M M43`, `M M33`,
`N 20`, `N 45`, `M M49`, `N 134`, `P O3`, `M C72`): **4 prove.** `M C85`:
NEEDS-TARGET (no poll among his posts). The six profile edits: 0 saved
(0.3 point 4). The likeliest misses are the messaging three, on the badge
rule.

---

## LOG

### Entry 1 -- 21:50-22:10, step 0 and the session harness, zero loads

**Step 0.** The disk agreed with the orchestrator's sample: `master` at
`c8fa6ea`, this branch's `d4d5d62` an ancestor of it, tree clean.
`git merge --ff-only master` fast-forwarded. The 9224 Chrome answered
`/json/version` (Chrome 153) with ONE page target, a new tab -- nothing else
was driving it.

**The harness:** `scripts/_probe_live_lane_session_1.py`. A closed key table
of SHIPPED tools, the badge-before-messaging rule in code, and a LEDGER: it
wraps `BROWSER.goto` (the only `page.goto` in the package -- measured, no
tool navigates around it) so every navigation a tool makes is counted
against 40, a 41st is refused BEFORE it navigates, and 20 seconds since the
ledger's last load are waited out across separate runs. It prints
integers, booleans, field names and this package's own closed words; every
other string by length.

**Shown failing, in a scratch copy of the tree** (the register's rule --
never the live tree; the copy was confirmed to be what imported). Six
plants, one at a time, each restored before the next, against
`tests/test_live_lane_session_harness.py`:

    BASELINE                                              18 passed
    H1 the ceiling checked AFTER the navigation           1 failed  (the ceiling test)
    H2 a refused address counted as a load                1 failed  (the refused-address test)
    H3 the messaging rule dropped from selection          2 failed  (m43, m33)
    H4 strings printed whole                              2 failed  (both shape tests)
    H5 the gap owed but not waited                        1 failed  (the gap test)
    H6 the budget off by one                              1 failed  (the budget test)
    RESTORED                                              18 passed

**One test of mine was wrong before it ran, and the run said so.** I used
`/messaging/compose/` as the address the boundary refuses. It is ADMITTED
(the blank-composer read); the refused composer is `/messaging/thread/new/`.
The test now uses `/my-items/`, which the boundary refuses and lane Y
measured as refused. **And one assertion of mine could not fail** -- it ended
`or True` -- and was deleted before the first run, not after.

### Entry 2 -- 22:14:11-22:15:45, the first live run: 4 loads, 0 presses

`scripts/_probe_live_lane_session_1.py --only per_post,badge,m43,m33,notifications,activity`,
attach mode, `LINKEDIN_MIN_INTERVAL_S=20`. Every page: walled False,
challenge terms 0. Ledger 0 -> 4.

    key            load  result
    per_post        1    RETURNED  per_post readable True, items_read 2
    badge           2    RETURNED  new_since_last_visit 1; notifications badge 20 (state read)
    m43             -    HELD      the badge read 1, not 0 -- /messaging/ NOT opened
    m33             -    HELD      the same
    notifications   3    RETURNED  10 rows, unread_when_read 10; invitation-kind 0, follow-kind 0
    activity        4    RETURNED  authorship established; 8 items, all activity urns;
                                   poll-shaped nodes in main 0

**`P G6` -- PROVEN.** The field's claim, from its cell: impressions and
engagements, integers, one per distinct item, no identifier. What came back:
`readable` True, `items_read` 2, `impressions` a list of 2 integers,
`engagements` a list of 2 integers, `engagements_drawn_for` 2. **The fields
whose meaning was checked:** `total_impressions` equals the sum of
`impressions`, and `total_engagements` the sum of `engagements`; both lists
have one entry per item read; `unparsed` 0, `not_activity_links` 0,
`duplicate_links` 0, `unreadable_links` 0. Nothing in `per_post` is a string
except its `scope` sentence, which is this package's. Lane L1's own bank rule
for this row: "PROVEN if per_post.readable".

**`M M43`, `M M33` -- NOT FIRED, held by the rule written in 0.3 point 1.**
`linkedin_new_messages` read `new_since_last_visit` 1: one message had
landed since his last look at Messaging. `/messaging/` lands in a
conversation LinkedIn chooses, most likely the newest, so opening it would
have spent his unread marker on a message he has not seen and possibly shown
its sender a read receipt. The ruling asks the lane to PREFER already-read
threads; this was the one reading that could honour that, and it said no.
**What moves them: the badge reading 0**, which it does once he opens
Messaging himself. Nothing about these rows needs a ruling.

**`N 20`, `N 45` -- FIRED, NOT PROVEN.** `linkedin_notifications` returned
the documented shape (10 rows, each with `text`, `when`, `unread`, `link`;
`side_effect` present; `unread_when_read` 10). None of the 10 is an
invitation-kind or a follow-kind notification -- by the closed phrase lists in
the harness, and cross-checked offline with broader stems (counts only): 0 rows
mention an invitation, a follow or an acceptance; the one row mentioning a
connection is a hiring notice. Each row proves only on a day his list holds
its kind, as the bucket-1 wave priced. The page drew 10 rows; the badge had
counted 20.

**THE COST, MEASURED IN BAND FOR THE FIRST TIME.** The notifications badge
read 20 on `/feed/` before the call. The notifications page draws no badge,
so the harness's own after-reading was `unreadable` and `cost_delta` refused
-- correctly. The `/in/me/` page loaded next draws it, and its capture read
offline (a local headless Chromium, every request aborted, LinkedIn's script
and policy tags removed) gives 0. **Control:** the same offline method on the
`/feed/` capture gives 20, matching the live reading. The shipped
`notify_cost.cost_delta` on the live before and the offline after: state
`measured`, **delta 20**. His 20 unread notifications were spent, as
`NOTIFICATIONS-UNREAD-SPEND` permits; the 10 rows returned carry their
`unread` flags as they stood.

**`M C85` -- NEEDS-TARGET.** Of the 8 items his profile's activity rail drew,
none is a poll: 0 poll-shaped nodes in `main` live, and offline 0 nodes with a
poll class and 0 "N votes" phrases in the capture. Scope stated rather than
widened: the 8 the rail draws on first render, not every post he has made. By
the DECIDED call (0.1) the lane records NEEDS-TARGET and moves on; no reader
was built.

**Ids in hand for `M C72` and `M C38`:** 8 activity urns of his own, in
`_state/live1/activity.json` only.

**TWO LEAKS OF MY OWN, AND WHERE THEY WENT.**
1. **The harness printed eight item urns.** `anchors_per_item` is keyed BY
   urn, and the first `shape_of` printed every dict key on the belief that
   keys are field names this package wrote. They went to the run's scratch
   output (outside the repository, scrubbed within minutes: 8 found, 0 left)
   and to this session's context; not to any tracked file. **Fixed:**
   `is_field_name` -- a key prints only if shaped like an identifier (ASCII
   letters, digits, underscore; no six-digit run); the rest are counted and
   withheld, at every depth. Three tests pin it, and the leak itself was
   planted back in the scratch copy as H7: **3 tests red; baseline and
   restored 21 passed.** The six earlier plants re-ran red as before.
2. **An ad-hoc count of mine printed one profile slug** while tallying link
   kinds (my mask covered digit runs only). Session output only. Link paths
   are printed by first segment only from here.

**THE CENSUS, AFTER ENTRY 2.** `profile.md` `G6` -> COVERED-PROVEN with the
evidence above, lane L1's paragraph kept beneath it. `network.md` `20`, `45`,
`messaging-and-content.md` `M33`, `M43`, `C85`: a dated paragraph each, state
unchanged. `read-addresses.tsv` `M C85`: note rewritten (the source is
DECIDED; NEEDS-TARGET), gate left RULING -- the table's alphabet has no
"needs a target", and READER would count the row as blocked on nothing
while no target exists. The correction guard's two proximity candidates
from these edits (`G6` beside `G7`'s "false", `M33` two rows above `M35`'s
"corrected") are triaged on `NOT_A_CORRECTION`, each after reading the line.

**PIN MOVES SO FAR, NOT RE-PINNED** (`census_completion.py --check`):
`delivered_strict` 75 -> 76, `unfired` 22 -> 21, `b1_no_ruling` 7 -> 6, and
`PINNED_B1_ROWS` -- `P G6` leaves its hold (it is no longer COVERED-UNFIRED).
`check_read_addresses.py`: GREEN, 66 of 66, blocked on nothing 1 (`M M49`).

**THE GATE ON THOSE EDITS** (`scripts/impact_gate.py --against c8fa6ea` at
`1d470d2`, 22:26:38-22:31:45, not widened: 58 of 229 test files, 171 NOT
CHECKED): **REFUSED, 2 failed, 2542 passed.** Both reds are `P G6`'s
promotion, and they are two different kinds of pin:

1. `test_a_covered_row_names_the_artifact_that_covers_it.py`, the `G6` entry,
   pinned at COVERED-UNFIRED by lane L1 with the instruction *"A fire that
   promotes or demotes it must move this pin in the same commit."* That is a
   per-row pin only this lane touches, so it is MOVED -- to COVERED-PROVEN,
   with a comment pointing at the evidence -- in the next commit. 15 passed.
2. `tests/test_ruling_holds.py::test_bucket_one_is_derived_and_sits_on_its_pins`:
   `PINNED_B1_ROWS` in `scripts/census_completion.py`, an AGGREGATE pin.
   **Left red by design**, per the brief ("Do NOT re-pin"): the orchestrator
   re-pins it at merge, with the three figures listed above.

### Entry 3 -- 22:28:38-22:29:31, the profile-views page with each pill open: 1 load, 3 presses

`--only pv_capture`, ledger 4 -> 5. Walled False, challenge terms 0. The page
is loaded once and each filter pill is opened through the SHIPPED gate --
`press.disclose`, main-scoped, priced by the server's own
`_profile_views_press_counters` -- and the page is snapshotted inside the
counter reader's second call, the gate's open moment, after a 1.5-second
settle (the popover is built after the click). Counters readable before any
press: `headline_viewers`, `invitations`, `notifications_unread`.

    pill  permitted  refused       disclosed  appeared       new_lines
    0     True       -             True       show_results   32
    1     True       -             True       show_results   22
    2     False      not_restored  True       show_results   37

**PILL 2 WAS REFUSED AFTER ITS PRESS, AND THE GATE WAS RIGHT.** Condition 4:
its `aria-expanded` read `'false'` before and `'true'` after the gate's
Escape -- the popover stayed open. At 19:10 today the same three pills were
all permitted and closed. The difference is this probe's settle: pill 2 is
the Company filter, whose popover holds a text input, and after 1.5 seconds
focus is plausibly inside it, where Escape does not close the popover
(DERIVED from the structure below, not measured by a second press). So **the
settle was not neutral** -- a lesson for the build, not a gate defect: a
view-switch press must close its popover by the popover's own controls, never
by Escape. Nothing was applied (no "Show results" was pressed) and the
popover lived only in this lane's own tab, which the run closed. The harness
stopped on the refusal, as the rule says.

**WHAT THE THREE OPEN POPOVERS DRAW** (read offline from the captures, in a
local headless Chromium with every request aborted; labels printed only as
closed-vocabulary TERMS or lengths):

    pill 0  time range       4 div[role=radio] {aria-label, aria-checked}, each with a hidden
                             input[type=radio] + label[for]; ONE checked; then
                             button[type=button] "reset" (enabled), "show results"
    pill 1  interesting      2 div[role=checkbox] {aria-label, aria-checked}, none checked --
            viewers          LinkedIn's categories "works at a company you follow" and
                             "verified"; "reset" DISABLED, "show results"
    pill 2  company          a typeahead input (aria-autocomplete), 5 div[role=checkbox]
                             options (other people's employers: lengths only, never read),
                             "reset" disabled, "show results"
    all     container        a div with only hashed class names; no role, no aria

    closed page, main:  "all filters", "reset", "show more analytics" -- each a plain
                        button[type=button] with attributes {class, componentkey, type}
                        only: no aria-expanded, no aria-haspopup, no aria-controls, not in
                        a dialog; the same six div ancestors up to a section

So the time-range pill's option names ARE in the shipped vocabulary; the
interesting-viewers pill's two categories are NOT (added for the build), and
the popover's own "reset" and "show results" are the controls a view switch
presses.

### Entry 4 -- 22:37:44-22:38:27, his own post with its control menu open: 1 load, 1 press

`--only post_capture`, ledger 5 -> 6. The newest activity id in the
`activity` raw (authorship established) -- read by the harness, never printed
or passed on a command line. Walled False, challenge terms 0. 4
`[aria-expanded]` in `main`; exactly 1 whose name starts "open control menu".
Opened through `press.disclose`, priced by `off_state`: **permitted**, closure
verified. Captured closed (lane Y's item 5, a post permalink) and open.
**(Entry 11 corrects this price: `off_state` reads 0 on this page whatever
happens, so it priced nothing.)**

**The open menu, read offline:** eight `div[role=button]` items, each inside
an `li` of one `ul`, no `role=menu` or `menuitem` anywhere -- "feature on top
of profile", "save", **"copy link to post"**, "embed this post", "edit post",
"delete post", "who can comment on this post", "who can see this post". **Five
of the eight are writes, one of them irreversible.** So the copy-link press
aims by EXACT equality, and "delete post" being drawn is the ownership proof
(only a post's author is offered it). This is what the child building (d)
was briefed on.

### Entry 5 -- 22:45:15-22:51:37, items 7, 8 and 9: 13 loads, 0 presses, 0 writes

`--only editor_fields,l1_*,people_search,cap_*`, ledger 6 -> 19. Every page:
walled False, challenge terms 0. Every key RETURNED.

**ITEM 7 -- NOTHING SAVED, AND THE REASON IS NOW MEASURED.** The shipped
`linkedin_profile_editor_fields` (2 loads, self-ownership established) read
17 controls in the intro editor. **None is a notify-network control.** The
only two switches (`input[type=checkbox][role=switch]`, no accessible name,
both checked) were identified offline from the capture by the text of their
section: "Open Profile" (let anyone message him free) and "Profile Premium
Badge". The ruling's first condition -- notify network CONFIRMED OFF IN THE
EDIT DIALOG -- cannot be confirmed in a dialog that draws no such control, and
the brief's own rule applies: **if any condition cannot be proven, do not
save.** `P A8`, `A11`, `A13`, `A17`, `A19`, `A21`: NOT SAVED, zero writes.
**What would make it provable:** a reading of the ACCOUNT-level setting that
decides whether profile edits are shared ("share profile updates with your
network", under the settings index captured below), plus a ruling that the
account-level setting satisfies condition 1 -- and the write path asserting
it at save time, which is an edit to `writes.py` (lane L4's).

**ITEM 8 -- lane L1's five NEEDS-CAPTURE pages, captured** (L1's readers,
L1's file names `_state/l1-<key>.html`, no control bracket):

    row     key            relation                       reading (integers)
    P A25   contact        REDIRECTED, path depth 4 -> 2  anchors 58 (30 member), 1 dialog
    P L1    audience       SERVED, exact                  39 chart labels, 0 in the metric vocabulary
    P L8    overview       SERVED, exact                  19 chart labels, 0 in the vocabulary
    M C48   articles       SERVED, exact                  anchors 22, /pulse/ links 0
    M C38   post_summary   SERVED, exact                  38 chart labels, 0 in the vocabulary

Findings the next offline build needs: `chart_labels.KNOWN_METRICS`
recognises NONE of the labels on the audience, overview and post-summary
pages (33, 13 and 32 unrecognised); the contact overlay lands on his profile
as a dialog; and the articles page is SERVED (not redirected) and draws no
article link.

**ITEM 9 -- lane Y's live-capture list: all eight of its page items are now
captured**, three of them on loads spent for other rows: `/feed/` (the
badge read), `/notifications/` (N 20/45), a post permalink (post_capture), plus
`/mypreferences/d/` (REDIRECTED, depth 2 -> 4), the people search through the
shipped `linkedin_people_search_shape` (one of D1's five test searches: 17
person results, 3 filters offered, landed where sent), `/analytics/recruiter-views/`
(SERVED at a different url of the same depth, 1 dialog),
`/mynetwork/invite-connect/connections/` (SERVED exact) and two company roots
of the kinds lane Y asked for, a large organisation and a services firm
(SERVED exact, 268 and 342 anchors). Y's items 9 and 10 are presses and were
not taken.

**The people-search tool flagged its own process as stale** (loaded code
older than disk): I was editing `press.py` and `readonly.py` while the run
was in flight. Its detector was right; the reading is unaffected because
nothing it calls was edited.

### Entry 6 -- 22:40-23:06, builds (a) and (b), offline, zero loads

**THE SHAPE OF THE PERMISSION CHANGED, AND IT IS THE MOST IMPORTANT THING IN
THIS ENTRY.** `readonly.SANCTIONED_MUTATIONS` is the complete, pinned list of
where this package presses, and its count test admits ONE call per entry --
"the list admits ONE call and not a licence". It held 7 entries. It now holds
**9**:

    8  ("linkedin_server/reveal.py", "reveal", "click")
       the DECIDED reveal -- "Show more analytics", a plain button, admitted
       BY NAME per control, on the orchestrator-delegated call of 0.1
    9  ("linkedin_server/view_switch.py", "_activate", "click")
       the view switch, on VIEW-SWITCH-PRESS-RESTORED; one drain-point click
       every step goes through, and a test pins apply_and_restore as its only
       caller

Each carries its argument beside it in `readonly.py`, citing the call it
rests on. `press.py` -- the attribute gate -- is UNCHANGED except its
docstring, which said every package press goes through `disclose` and no
longer can; the new presses live in their own modules and reuse its pure
checks (`check_address`, `check_basis`, `check_counters`, the witness and
the open-moment reading) rather than a second copy. **(b) was first written
into `press.py` and moved out** when its refusal inventory showed it could
not be driven through `disclose`.

**(b) `linkedin_server/reveal.py` -- `DECIDED_REVEALS` and `reveal()`.** The
control is the ONE visible button in `main` carrying no `aria-expanded`,
`aria-haspopup` or `aria-controls` whose label EQUALS "show more analytics"
after normalisation (the measured shape: two other plain buttons of the same
shape sit beside it). Refused BEFORE the click: an undecided key, another
surface, an unadmitted address, no basis, a reading not sanctioned there, no
counter reader, an unreadable counter, not exactly one match. After it:
`url_unchanged`, `counters` (the gate's own check), the witness, `main`'s
element count before and after, the reading. `permitted` only if the url and
every counter held. **No closure step**: the call requires none, and a second
press to collapse would be a second press nobody decided.

**(a) `linkedin_server/view_switch.py` -- `VIEW_SWITCHES` and
`apply_and_restore()`**, built to the captured popover: open the pill (found by
caption among main's `[aria-expanded]` role=button pills), select the option
(`[role=checkbox|radio]` by `aria-label`, checked state by `aria-checked`),
press the popover's own "show results" (which applies AND closes), read the
view, then reopen, deselect, apply again, read again. **Escape is never used**
(Entry 3's measured failure). `restored` requires the view read after the
restore to EQUAL the view read before, the pill closed, the path unmoved;
`permitted` adds no counter moved. A switch it cannot take off is its loudest
refusal (`switch_left_applied`), and it closes a popover left open before
saying so. Two entries: the "Interesting viewers" pill's "verified" and "works
at a company you follow".

**Wired into `linkedin_who_viewed_me`**: `view_switch=<key>` and
`show_more_analytics=True`, both on the page the tool already loaded, switch
first so it reads and restores the page as found, each failure caught
separately so neither can cost the viewer list. The view is read with the
tool's own harvest and row parser plus the headline count. Tool-surface pin
67 -> 69 parameters, re-pinned in the same commit with the statement that no
row moves in it; README row updated. `tests/reader_leak_baseline.json`: 8
readers added, all `clean`, none removed or changed (regenerated with the
file's own writer, in a copy without the child's unfinished module).

**SHOWN FAILING, in a scratch copy of the tree** (child-free, the copy
confirmed to be what imported), one plant at a time:

    BASELINE   test_reveal.py 29 passed, test_view_switch.py 35 passed
    R1 a control carrying disclosure state counted     1 red
    R2 an invisible match counted                      1 red
    R3 an unreadable counter pressed anyway            2 red
    R4 the url never compared                          2 red
    R5 the counters never compared                     2 red
    R6 the surface never checked                       2 red
    V1 the restore never compares the view             2 red
    V2 the restore never deselects                     5 red
    V3 an already-applied option pressed anyway        2 red
    V4 an absent option leaves the pill open           1 red
    V5 the apply pattern loosened to any "show"        1 red
    V6 the counters never compared                     2 red
    V7 a failed restore leaves the popover open        1 red
    RESTORED   29 passed, 35 passed

**Two defects of mine caught before any fire.** The apply pattern first
allowed `[0-9,]+` for a count, but the normaliser turns "1,234" into "1 234"
-- the pattern test went red on its own first run. And a view-switch test
ended `or True` and could not fail; it was rewritten to assert on the syntax
tree before it ran.

**`tests/test_readonly.py` also carries a hand-edited constant** in a chained
comparison (`total == len(...) == N`), with a paragraph warning that it goes
stale on every widening; it went red on the first new entry and was bumped
with each, as that paragraph predicts.

### Entry 7 -- 23:08:46-23:09:25, the view switch and the reveal, fired: 2 loads, 7 presses

`--only pv_switch,pv_verify`, ledger 19 -> 21, both pages walled False with
0 challenge terms. `pv_switch` is the shipped
`linkedin_who_viewed_me(limit=10, view_switch="interesting_viewers_verified",
show_more_analytics=True)`; `pv_verify` is the same tool plainly, a fresh
load, straight after.

    view_switch   permitted True   restored True   left_applied False
                  applied_view_differs True   closed after apply True, after restore True
                  path_unchanged True   counters held: headline_viewers, invitations,
                  notifications_unread (read at both ends; structural basis)
                  viewers_when_applied 6 rows (the same fields as the unfiltered rows)
                  headline_when_applied 6
    reveal        permitted True   url_unchanged True   counters held (the same three)
                  main elements 822 -> 912; reading: 49 new lines, 82 new elements,
                  "show more analytics" GONE, nothing else appeared or went
                  witness: nothing it counts moved (an inline expansion, not a
                  dialog or menu -- a MISS for that set, by its own wording)
    pv_verify     rows 10 and the headline: THE SAME as the switch run's own load

**`N 134` -- PROVEN.** The row asks to see notable or interesting viewers.
The tool applied the "Interesting viewers" pill's "verified" option, returned
the 6 viewers it left, and took the filter off. **The fields whose meaning
was checked:** the headline under the filter (6) equals the number of rows it
left (6); the filter changed the view; the view read after the restore EQUALS
the view read before (the module's `restored`, which also requires the pill
closed and the path unmoved); no counter moved; and a fresh load straight
after agreed with the load before the switch, so the restore held on
LinkedIn's side as well as in the tab. Presses: open, select, apply, reopen,
deselect, apply -- 6.

**`P O3` -- HALF PROVEN, STATE UNCHANGED, AND NOW A READER AWAY.** The
filters half is shown by the same switch. The insights half: the decided
"Show more analytics" press was PERMITTED -- url and three counters
unchanged -- and it drew two new sections, "Highlights" (7 lines, no numbers,
1 chart) and "Details" (7 lines, 5 of them percentages, 2 charts), read
offline from the capture by headings and line counts only. **Nothing in the
package turns those two sections into data yet**, so the row is not banked on
them. Its gate in `read-addresses.tsv` moves PRESS -> READER: a reader is all
that is left, built offline from `_state/live1/pv_switch.html`, owing a shape
and a redaction rule for rare values (the sections describe other people in
aggregate). Presses: the reveal, 1 (plus the switch's 6 shared with `N 134`).

**A FINDING FOR ANOTHER ROW, NOT ACTED ON.** `N 136` ("See top locations,
industries and companies of your viewers (Premium)") is MEASURED-ABSENT on
the finding that no such panel is drawn. The "Details" section behind "Show
more analytics" -- percentages about his viewers -- may be exactly that panel,
unseen because nothing could press the button until today. `N 136` is not in
this lane's queue and its cell is left alone; it is flagged for the
orchestrator.

**THE CENSUS:** `network.md` `134` GAP -> COVERED-PROVEN with the evidence
above; `profile.md` `O3` a dated paragraph, state GAP; `read-addresses.tsv`
`N 134`'s line REMOVED (a proven row is no longer bucket 3, and the checker
flags a line for a non-bucket-3 row), `P O3` gate PRESS -> READER.
`check_read_addresses.py`: GREEN, 65 of 65; blocked on nothing 2 (`M M49`,
`P O3`). The proximity scan's new pair from the network census, and `O3`
joining the profile census's pair, are triaged after reading each line in the
window.

**PIN MOVES SO FAR, NOT RE-PINNED** (`census_completion.py --check`, now):

    adjudicated            431 -> 432   (+1)
    delivered_broad         97 -> 98    (+1)
    delivered_strict        75 -> 77    (+2: P G6, N 134)
    gap                    273 -> 272   (-1: N 134)
    gap_read                66 -> 65    (-1)
    unfired                 22 -> 21    (-1: P G6)
    b1_no_ruling             7 -> 6     (-1)
    b3_admitted             40 -> 39    (-1)
    b3_blocked_on_nothing    1 -> 2     (+1: P O3 is now READER)
    PINNED_B1_ROWS           P G6 leaves its hold

### Entry 8 -- 23:14-23:24, the reader P O3 was waiting on, built and fired: 2 loads

**Built:** `linkedin_server/profile_views_more.py`, reading what "Show more
analytics" draws -- "Highlights" (value/label pairs: top location, top
industry, top company) and "Details" (a "companies" breakdown, each entry
"<name> (<n>%)"). Locators and `inner_text` only; no injected script (the
`# readonly-ok` waiver budget stands at 22 of 22 and is untouched). **Fitted
before it was wired:** run offline against the live capture, it read both
sections, all three highlight values, 5 entries and 0 unparsed lines; on the
closed page it found nothing, not an empty reading. **No name is redacted**,
and its docstring says why and when that stops holding: the tool it is wired
into already returns every viewer by name and headline, so an aggregate over
the same people discloses nothing new -- the redaction is owed the day it is
wired to a surface whose rows are not returned. Wired as
`more_analytics.revealed_insights`, no new parameter. 10 tests; five plants in
a scratch copy all red (M1 value paired with the NEXT line: 3 red; M2 entries
without parentheses: 4; M3 unparsed not counted: 1; M4 headings read
page-wide: 3; M5 the section climb stopping at the heading: 1); baseline and
restored 10 passed. `reader_leak_baseline`: 1 reader added, clean.

**Fired** (`--only pv_switch,pv_verify`, 23:21:53-23:22:39, ledger 21 -> 23,
walled False, 0 challenge terms): the switch permitted and restored (6 rows
under the filter, headline 6), the reveal permitted (url and counters held),
`revealed_insights`: both sections, the three highlights, 5 company entries,
0 unparsed; the fresh load agreed with the switch's own load again.

**`P O3` -- PROVEN.** Filters by the switch, insights by the reveal and its
reader, in one fire. **The fields whose meaning was checked:** the top
company in "Highlights" EQUALS the largest entry in the "Details" breakdown,
and that entry is unique -- two sections parsed independently, agreeing (a
string comparison in memory; only the boolean left the process); the shares
are percentages the reader's pattern admits; url and counters held across
the press. Census: `profile.md` `O3` GAP -> COVERED-PROVEN, the half-proven
paragraph kept beneath; its `read-addresses.tsv` line removed.
`check_read_addresses.py`: GREEN, 64 of 64; blocked on nothing 1 (`M M49`).

**A DEFECT IN MY OWN COMMIT `85df223` (a lane commit; it does not resolve on
`master` until the lane merges), fixed in the next.** Entry 7 named the
two census files in backticks beside the word "correction", and the
correction guard reads that as this document correcting them -- two
untriaged pairs, so that commit's tree fails that guard. Reworded, not
triaged: a triage entry would have muted the pair for good.

**PIN MOVES NOW, NOT RE-PINNED:**

    adjudicated            431 -> 433   (+2)
    delivered_broad         97 -> 99    (+2)
    delivered_strict        75 -> 78    (+3: P G6, N 134, P O3)
    gap                    273 -> 271   (-2: N 134, P O3)
    gap_read                66 -> 64    (-2)
    unfired                 22 -> 21    (-1: P G6)
    b1_no_ruling             7 -> 6     (-1)
    b3_admitted             40 -> 38    (-2)
    b3_blocked_on_nothing    1 -> 1     (P O3 in and out; M M49 remains)
    PINNED_B1_ROWS           P G6 leaves its hold

### Entry 9 -- 23:26:17-23:26:30, the messaging badge read again: 1 load, messaging still held

`--only badge,m43,m33`, ledger 23 -> 24, walled False, 0 challenge terms.
`linkedin_new_messages` read `new_since_last_visit` **1**, as at 22:14, so
the harness opened no `/messaging/` page (m43, m33: HELD-BY-BADGE). The
notifications badge on the same page read 2 -- two notifications have
arrived since the 22:15 spend.

**So `M M43`, `M M33` and `M M49` keep their states this session, on a
reading taken twice, 72 minutes apart.** For `M M49` that also means build
(c) was NOT written: the one page it reads -- the conversation `/messaging/`
lands in -- has never been captured, and a reader for a thread DOM nobody
has seen would be a guess. **What moves all three is one event outside this
lane's reach: the badge reading 0**, which happens when he opens Messaging
himself. The next live session's first key should be `badge,m43,m33`: on a
0 it fires `M M43`, captures the landing (the capture build (c) needs), and
fires `M M33` with the `starred` pill -- three loads.

### Entry 10 -- 23:30-00:10, build (d): the copy link of his own post, offline, 0 loads

**Built by a child, bounced once, then changed again in the lead's review.**
`linkedin_server/share_link.py`, `tests/test_share_link.py` (61 tests),
`tests/fixtures/synthetic/own_post_menu.html` (synthetic; the post id is
four digits). Served by a new tool, `linkedin_own_item_link(activity_id,
include_link=False)`: it loads his post's permalink (the admitted
`/feed/update/urn:li:activity:<digits>/`), prices the presses by `off_state`
on that page (**vacuous there -- Entry 11, and the fix beside it**), runs
`share_link.copy_own_post_link`, and returns the link's
SHAPE -- https, LinkedIn host, path kind, whether it carries this id. The
link itself only with `include_link=True`, since it can carry his vanity
name; the session harness never asks for it.

**What it presses, in order, and what stops it.** The control-menu trigger,
found by aria-label prefix among `main [aria-expanded]` (exactly one required;
Entry 4 measured 1 of 4). Press's own four pre-press checks, called BY NAME
(address, shape, scope, basis) as `reveal` and `view_switch` call them.
Counters read before any click. **The owner check is read off the SAME menu,
before the copy item is pressed:** "edit post" or "delete post" must be drawn,
and LinkedIn draws them for a post's author alone. The copy item is matched by
EXACT normalised equality, among eight items of which five are writes. The
capture is installed just before the copy press. Escape only if the menu is
still open. Counters and closure verified at the end.

**Three sanctioned lines, one per kind** (`readonly.SANCTIONED_MUTATIONS`
entries 10-12): click `_activate`, evaluate `_clipboard`, press
`copy_own_post_link`. The package scanner reports exactly those three and 0
unsanctioned -- read by the lead from disk, not taken from the child's report.

**THE FIRST BOUNCE.** The child had imported `press.evaluate` under an alias:
a pure function whose name collides with the scanner's `evaluate` pattern,
renamed so the scanner could not see the call. Rejected as scanner evasion,
whatever the call's own safety; the four component checks are now called by
their own names. Its two clicks and two evaluates became two drain points and
one script with two modes.

**WHAT THE LEAD'S REVIEW CHANGED, and why each mattered for a one-shot live
fire:**

1. **The clipboard claim was stated six times and is false of one route.**
   "His system clipboard is never touched" -- in the tool docstring, the
   server headline, the README twice, a test comment and the mutation
   entry's argument. A reference to the async clipboard API that the page
   took BEFORE the capture was installed bypasses the replacement, and that
   API fires no copy event, so no listener sees it either. Every one of the
   six now names the gap, and a fixture variant pins the answer: `copied`
   False, no link, no shape -- never a fabricated link, and no claim about
   his clipboard either way.
2. **The copy listener's comment overclaimed too.** It said the listener stops
   code holding earlier references. It cannot for the async API, and in
   Chromium a cancelled copy event writes whatever the page's own copy
   handlers put into `clipboardData`. Reworded: it narrows that route and does
   not close it.
3. **The read now waits for the first text** -- woken by the write itself,
   bounded at 3000 ms. A page that copies after an `await` of its own, and any
   `ClipboardItem` write (async by nature), would otherwise have been read as
   NOT copied: the fire would have spent its load and reported a miss that
   was not one.
4. **`write` keeps the `text/plain` part of each item.** The child kept a
   placeholder ("[items]"), which the shape reader would have reported as a
   non-link. An item carrying no text is kept as an empty string: counted in
   `captures`, never promoted to `copied` or a link.
5. **A refusal after the menu opened now carries `closure`** -- the menu was
   opened, so the refusal says whether it was left as found.
6. **The fixture never calls an unpatched clipboard function.** It decides
   "unpatched" by identity and then counts and stops. Before, a planted
   defect that skipped the hook made the fixture call the real `writeText` in
   the test browser.

**Red-proofs, each plant alone in a scratch copy, restored byte-for-byte.**
The child's eight, re-anchored after the rework: owner check skipped (1 red),
exact match loosened to `startswith` (1), hook not installed (4), Escape
skipped (7), counters not compared (1), `\d` for `[0-9]` (2), a second
caller of `_activate` (1), the mode not validated (2). The lead's eight:

    plant                                               red  caught by
    P9  the read does not wait for a late copy           2   the late copy; the ClipboardItem copy
    P10 write keeps a placeholder, not the item's text   1   the ClipboardItem copy
    P11 an empty kept text promoted to a link            1   the write with no text part
    P12 a refusal after the menu opened drops closure    2   the non-owner refusal, twice
    P13 Escape pressed whether or not the menu is open   1   the menu that closes itself
    P14 empty captures dropped before they are counted   1   the write with no text part
    P15 an empty box falls back to the page's own url    2   the captured reference; no text part
    P16 the script's wait drifts from READ_WAIT_MS       3   the pin, and both shortened waits

Baseline 61 passed; restored 61 passed.

**Two guards were red on this branch from `c523769` to `f100efa`, and this
build found them.** `c523769` moved `readonly.SANCTIONED_MUTATIONS` from 7 to
9 without the read-only boundary's re-freeze and without the package
docstring's count, so `test_the_read_only_boundary_is_where_it_was_re_frozen`
and `test_the_package_docstring_agrees_about_writes_and_mutations` failed on
that commit and on the five after it. Measured, not inferred: the committed
tree at `f100efa` -- this lane's commit, which does not resolve on `master`
until the lane merges; its subject is "live lane session 1: messaging read
again and still held; M M49 not built, with the reason" -- exported with
`git archive` and run, fails both. The
per-commit runs were chosen by hand and did not select them. Both are
repaired in `1d4ef86` (the re-freeze attributed in the file's own form: the
tree minus exactly the five new entries hashes to the frozen value). The
lesson is the repository's own, paid again: a gate chosen by name misses a
guard that reads the file as a whole. The full impact gate is run at the end
of this session for that reason.

**The tool body, driven end to end offline (`21d718c`).** A stand-in
`BROWSER` navigates the local fixture by its fulfilled route, so the
navigation, the landed-url check, the real counter reader and the envelope
all run; 5 plants in the tool body red (the counter reader ignoring the page,
the link withheld only when asked, the load not reported, a derived address,
a bad id reporting a load).

### Entry 11 -- 00:15:39-00:15:56, M C72 fired: 1 load, 2 presses -- the link obtained, and its price found vacuous

`--only own_link`, ledger 24 -> 25, walled False, challenge terms 0. The id
is the newest of his own activity ids, read in-process from the activity raw
(authorship established) and never printed. **Returned:** `permitted` True,
`copied` True, `captures` 1, `owner_item_present` True, the link withheld
(`link_withheld` True), `pages_loaded` 1; `shape`: https, LinkedIn host, path
kind `posts` (the shareable form), carries the id as a whole number, has a
query, length 213; closure closed; `counters_ok`, priced by `off_state`.

**THE PRICE WAS A ZERO THAT COULD NOT MOVE, found in the capture and not in
the verdict.** The `/feed/` basis names `off_state`, the count of toggles
labelled "Reaction button state: no reaction". The session's `/feed/`
capture draws three. His post's permalink draws NONE: its one toggle reads
"Unreact Like" (the post is liked) in all three captures of that page, 22:38
closed, 22:38 open and 00:15. So `off_state` read 0 before and after the
press whatever happened; the gate compared two zeros and reported them as a
price. **(Overclaimed, and corrected in Part 2 (a) below: had an unreaction
drawn the toggle OFF in the state family, `off_state` would have moved; what
the zero could not do is tell unmoved from unmovable.)** It cannot tell "did not move" from "could not move", and the `/feed/`
basis reaches `/feed/update/` by path prefix while its counter exists only
on `/feed/`. **The same zero priced Entry 4's press** on the same page, which
Entry 4 records as "priced by `off_state`: permitted" without the value.
That price was vacuous too, and this entry is its correction.

**What the presses did NOT do, read another way.** Across the three captures
the post's reaction state is identical -- the toggle "Unreact Like" 1, the
count label "1 reaction", one reacted-with entry -- so neither press (22:38's
menu; 00:15's menu and copy) added or removed a reaction. The like predates
both: the 22:38:20 capture was taken on the session's first load of that
page, before any press on it. That is an after-the-fact reading of captures,
not the gate's price, and the gate is what failed.

**THE FIX, offline, before the fire is repeated.**
`share_link.read_item_price` counts the item's toggle in both measured
dialects -- `off_state` (the basis's own), plus the permalink's "Unreact "
(on) and "React " (off; inferred from the on form, not yet seen; **Part 2
(a) below: the permalink's OFF label had been MEASURED on 2026-08-31, in the
state family, so "dialects" was the wrong model**). The tool
asks `price_can_move` BEFORE the first press and refuses `price_cannot_move`,
with nothing pressed, when every counter reads 0; every reading comes back
as integers in `price_readings`. 84 tests. Seven plants, all red: the zero
accepted (2), the permalink dialect ignored (5), the off form misspelled (2),
an unread toggle turned into 0 (4), a bool read as a count (1), the tool
pressing without the check (2), the readings not returned (2). **One plant
survived its first run:** an unread toggle turning into 0 moved no test,
because nothing had driven the reader's exception path. It is driven now.

### Entry 12 -- 00:37:03-00:37:23, M C72 re-fired on the fixed price: 1 load, 2 presses -- PROVEN

`--only own_link` on `2775d02`, ledger 25 -> 26, walled False, challenge
terms 0, the same post. **Returned:** `permitted` True, `copied` True,
`captures` 1, `owner_item_present` True, `link_withheld` True, `pages_loaded`
1; `shape` identical to Entry 11's (https, LinkedIn host, path kind `posts`,
carries the id as a whole number, has a query, length 213); closure closed.
**`price_readings`, three:** `off_state` 0, `toggle_on` 1, `toggle_off` 0 at
each -- the check before any press, and the gate's two. The gate compared
all three counters at both ends (`read_at_both_ends` lists them) and none
moved; the toggle that was drawn is one an outward reaction would move.
**The gate's own `priced_by` still names only `off_state`**, the basis's
counter, which is 0 here: the field reports the basis, not the counter that
could move. That is press's reporting and is left alone; the readings beside
it are the evidence. The capture agrees with the three before it: the toggle
"Unreact Like" 1, "1 reaction", one reacted-with entry.

**`M C72` -- PROVEN.** **The fields whose meaning was checked:** ownership
read off the menu before the copy press (an author-only entry drawn); the
text the page copied was captured, and it is the post's shareable link --
the `posts` path on a LinkedIn https host carrying this post's id as a whole
number; the price could move and did not; the menu closed. **NOT CLAIMED:**
the link itself (withheld; nobody read it); the embed half of the row ("Embed
this post" is a different item, not pressed); whether his system clipboard
was untouched (not observable from the page -- the capture held the text, so
the page copied through a route the capture covers); a reaction changing KIND
(Like to another keeps a toggle on, so these counts cannot see it); n=1 on a
price that could move -- the first fire's capability reading agrees, its
price is disowned. Census: `messaging-and-content.md` `C72` GAP ->
COVERED-PROVEN, its prior readings kept beneath; its `read-addresses.tsv`
line removed.

### Entry 13 -- 00:43:12-00:43:50, the held rows read once more: 2 loads, 0 presses

`--only badge,m43,m33`, ledger 26 -> 27: `new_since_last_visit` **1**, the
third reading of 1 (22:14, 23:26, 00:43), so no `/messaging/` page was
opened; `M M43`, `M M33` and `M M49` stay held on the badge rule. The
notifications badge on the same page read 2, as at 23:26.

`--only notifications`, ledger 27 -> 28, on `NOTIFICATIONS-UNREAD-SPEND`:
10 rows (4 unread when read), **0 invitation-kind and 0 follow-kind** --
the same answer as 22:15 over a list with two newer items. `N 20` and `N 45`
stay FIRED, NOT SHOWN: a row this tool serves is proven by an item of its
kind being in his list, and there was none either time. The cost delta was
not measured this time (no badge reading before the load in this key).

---

## THE ROWS, ONE LINE EACH

    queue  row      outcome           the reason, or the evidence (entry)
    1      P G6     PROVEN            per_post readable, 2 items; totals = sums of lists (2)
    2      M M43    NOT FIRED         messaging badge read 1 at 22:14, 23:26, 00:43 (2, 9, 13)
    2      M M33    NOT FIRED         the same readings (2, 9, 13)
    3      N 20     FIRED, NOT SHOWN  10 notifications twice, none invitation-kind (2, 13)
    3      N 45     FIRED, NOT SHOWN  10 notifications twice, none follow-kind (2, 13)
    4      M M49    NOT BUILT         the thread page it reads was never landed on (9)
    5      N 134    PROVEN            6 viewers under the filter; restored, twice (7)
    5      P O3     PROVEN            filters by the switch; insights revealed and read (8)
    6      M C72    PROVEN            the link's shape checked; priced by a toggle that could move (12)
    --     M C85    NEEDS-TARGET      no poll among the 8 items his rail draws (2)
    7      P A8 A11 A13 A17 A19 A21
                    NOT SAVED         the dialog draws no notify control (5); zero writes
    8      P A25 P L1 P L8 M C48 M C38
                    CAPTURED          state unchanged; the captures await readers (5)
    9      lane Y   CAPTURED          all 8 page items of its list (2, 4, 5)

## LOADS, PRESSES AND WRITES

    loads      28 of 40, serial, every one through the ledger; the smallest
               gap between two loads 22.5 s, none under the 20 s floor
    clicks     22 -- Entry 3: 3 (the pills, through press.disclose);
               Entry 4: 1 (the post menu, press.disclose); Entry 7: 7 (the
               switch's 6 and the reveal's 1); Entry 8: 7 (the same, fired
               again); Entries 11 and 12: 2 each (the menu, the copy entry)
    keys       4 Escapes recorded (press.disclose sends one after each of its
               4 clicks) and 0 to 2 NOT recorded: the two C72 fires ran
               before share_link reported escape_pressed, and the menu may
               have closed itself on the copy press. The field exists now,
               because of this line (the last commit below).
    writes     0. No save, send, reaction, follow or profile field; the nine
               outward writes stay held by OPERATOR-NAMES-THE-TARGET.

**ENTRY 7'S HEADING SAID 8 PRESSES; IT WAS 7.** Counted from the source, not
recalled: the switch's success path is six clicks (open, select, apply,
reopen, deselect, reapply) and the reveal is one. The heading is corrected
in place and this line says so.

The forced prediction (0.7) said 4 rows would prove and named the messaging
three as the likeliest misses. **4 proved** (P G6, N 134, P O3, M C72); the
misses were the messaging three, as predicted, and N 20 / N 45, which the
prediction's count absorbed without naming.

## EXPECTED PIN MOVES, NOT RE-PINNED

Every one below is a consequence of this lane's four promotions (`P G6`,
`N 134`, `P O3`, `M C72`), and each names the exact edit a re-pin makes.

`scripts/census_completion.py --check`, at the end of the session:

    adjudicated            431 -> 434   (+3: N 134, P O3, M C72)
    delivered_broad         97 -> 100   (+3)
    delivered_strict        75 -> 79    (+4: P G6, N 134, P O3, M C72)
    gap                    273 -> 270   (-3: N 134, P O3, M C72)
    gap_read                66 -> 63    (-3)
    unfired                 22 -> 21    (-1: P G6)
    b1_no_ruling             7 -> 6     (-1: P G6)
    b3_admitted             40 -> 37    (-3)
    b3_blocked_on_nothing    1 -> 1     (P O3 in and out; M M49 remains)
    PINNED_B1_ROWS           P G6 leaves its hold

And the tests that pin a census-derived set, red on the full gate for
exactly these reasons:

    tests/test_ruling_holds.py
        test_bucket_one_is_derived_and_sits_on_its_pins
            PINNED_B1_ROWS: P G6 leaves its hold
    tests/test_banked_evidence_is_reachable.py
        test_the_seven_under_banked_rows_are_exactly_these
            PINNED gains (messaging-and-content.md, C72) and (network.md, 134)
        test_every_unreachable_artifact_is_named_and_classified
            15 -> 18 artifacts
            BOTH ROWS' UNREACHABLE CITATIONS ARE IN THEIR KEPT PRIOR READINGS,
            written by earlier waves (gitignored _audit/_scratch/ files:
            one under C72, two under 134). The evidence for the promotion
            itself is tracked. Promotion is what made the guard read the
            whole cell: it examines banked rows only. P O3 cited a gitignored
            capture in this lane's own words and was reworded instead.
    tests/test_triage_read_gap_rows.py
        test_green_on_the_real_tree
        test_the_control_4_population_is_not_empty_and_equals_the_key_set
            scripts/triage_read_gap_rows.py's verdict table still carries
            "N 134" and "P O3", which are no longer read GAP rows: 53
            verdicts over 51 rows. Drop the two entries.
    tests/test_triage_instrument.py
        test_the_headline_split_is_the_one_the_report_quotes
            EXPECTED_NOW (77, {R: 10, W: 65, R+W: 2}) -> (76, {R: 9, ...}),
            M C72, and the report that quotes it
    tests/test_pointer_graph_guard.py
        test_the_committed_census_still_matches_its_pin
        test_every_failure_class_is_convicted_and_the_calibration_is_not
            N 135's cell opens with a bare "Same", a pointer that resolved to
            N 133 and now resolves to N 134, because N 134's state moved.
            N 135's own evidence follows the fragment and did not change.
            pointer-graph.tsv 69 -> 68 (network 4 -> 3). The honest repair is
            to replace the vestigial "Same" in the commit that re-pins; N 133
            is in the cleanup lane's ten, so this lane left both alone.

The per-row pin for `P G6` in
`tests/test_a_covered_row_names_the_artifact_that_covers_it.py` WAS moved,
in Entry 2's commit: its own instruction said a fire must move it.
`check_read_addresses.py`: GREEN, 63 of 63.

## GATES RUN, AND NOT RUN

RUN, and what each covered:

- **The full impact gate**, `scripts/impact_gate.py --against c8fa6ea`, on
  the tree of the last commit below: it widened to the full suite (215 of
  233 test files reachable). **9 failed, 8958 passed, 8 skipped, 1 xfailed,
  in 20 min 45 s.** Eight of the nine are the pin moves listed above. The
  ninth was a defect in this document -- `f100efa` cited in a commit slot
  without its subject or a disclosure -- and is repaired
  (`scripts/check_cited_shas_resolve.py` exits 0). After the repairs the
  eight pin reds were re-run by name and are exactly the eight.
- **Per commit, scoped by hand** -- the files each change touched plus the
  identity, person-name and correction guards on the staged index. **This is
  the gate that missed two guards for six commits** (Entry 10): a selection
  by name did not include the two files that read `readonly.py` and the
  package docstring as wholes. The full gate above is what that miss is
  answered by.
- **The generated files**: `build_audit_index.py`, `build_rulings_index.py`
  and `build_blocker_map.py`, `--write` twice (the second sweep changed
  nothing) and `--check` exit 0 on all three, in the C72 commit and again
  in the last. **An earlier "fixed point" claimed in the build (d) commit
  was void**: the three were run without `--write`, so they only reported.
  Nothing was stale -- the proper sweep changed INDEX and RULINGS not at
  all, and the blocker map only for `C72` -- but that check verified
  nothing and is not counted.
- **Red-proofs, each plant alone in a scratch copy**: share_link 8 (the
  child's) + 8 (P9-P16) + 2 (P17-P18); the price 7 (Q1-Q6, Q4b); the tool
  body 5 (T1-T5); the replacement-script guards 3 plus one measurement
  (RA-RD); reveal R1-R6, view_switch V1-V7, profile_views_more M1-M5 and the
  harness H1-H7 (earlier entries). Every plant red.

NOT RUN:

- **CI.** Nothing was pushed (the brief). The 3.10 cell is CI's; every
  number here is 3.13 on this box.
- **A live fire after `escape_pressed` existed.** Offline proof only.
- **The observed read map** the impact gate consults was recorded on
  2026-09-22 (`5c910e4`), not on this branch; the gate says so itself, and
  it only ever ADDS to a plan.

## COMMITS

On the lane branch, oldest first. **None resolves on `master` until the lane
merges**; each subject is the key that survives a rewrite.

    1ef494c  live lane session 1: the plan, and a harness that counts every load
    1d470d2  live lane session 1: P G6 proven; messaging held on the badge; N 20/45 not shown
    0cf9720  live lane session 1: the filter popovers captured open; G6's banked pin moved
    e2fa2d5  live lane harness: a post_capture key; two urn-shaped test literals built at runtime
    d9b4c26  live lane harness: the editor-fields read, lane L1's captures and lane Y's pages as keys
    2e7cb2f  live lane session 1: the post menu captured; nothing saved; L1 and lane Y captured
    c523769  view switch and decided reveal: two presses, each on a recorded call
    4279dc3  live lane harness: pv_switch fires the view switch and the reveal; pv_verify reloads to check the restore held
    85df223  live lane session 1: N 134 proven by the view switch; P O3 half proven, now a reader away
    5ed7d14  profile views: read what Show more analytics reveals
    70d3472  live lane session 1: P O3 proven -- filters by the view switch, insights by the reveal and its reader
    f100efa  live lane session 1: messaging read again and still held; M M49 not built, with the reason
    1d4ef86  copy link of his own post: share_link and linkedin_own_item_link; the late re-freeze
    21d718c  linkedin_own_item_link driven end to end on the fixture: real counter reader, 5 plants red
    2775d02  own item link: price the presses by the post's own reaction toggle; refuse a price that cannot move
    2d4bb44  live lane session 1: M C72 proven -- the link of his own post, on a price that could move
    8cd8e98  share_link reports whether it pressed the Escape; the held rows read once more

and the commit that adds this section.

## FINDINGS AND DECISIONS FOR THE ORCHESTRATOR

1. **The `/feed/` basis prices nothing on a post permalink.** It reaches
   `/feed/update/` by path prefix, but its counter, `off_state`, counts the
   feed's toggle label ("Reaction button state: no reaction"), and the
   permalink draws its toggle as "Unreact Like" -- measured in all three
   captures of his post's page, with zero in the feed's label, while the
   feed draws three. So `press.check_counters` compares two zeros and calls
   it a price. `linkedin_own_item_link` now prices by the toggle itself and
   refuses before any press when nothing can move; **`press.disclose` on a
   permalink is still priced by the zero** (the harness's `post_capture`
   was, Entry 4). Two ways to close it, both in `press.py`, which is not
   this lane's: a basis of its own for `/feed/update/`, or a refusal when the
   basis-named counter reads 0 at both ends and nothing else priced the
   press. The gate's `priced_by` field also names the basis counter rather
   than whatever counter could move (Entry 12). **Built in Part 2 (a), and
   narrowed there: "prices nothing" overclaimed -- the zero cannot tell
   unmoved from unmovable.**
2. **The react write aims by the feed's label** (`dom.REACTION_OFF_LABEL`,
   `reaction_control_selector`, used on item permalinks). On his own post's
   permalink the measured toggle is "Unreact Like" (the post liked; the OFF
   form "React Like" is inferred). n=1, one liked post, but it suggests the
   write would find no control there. For lane L4. **Corrected in Part 2
   (a): the permalink's OFF label was measured on 2026-08-31 in the state
   family, and an ON label on 2026-09-04 ("Reaction button state: Like");
   the write's real defect is reading the "Unreact" ON label -- Part 2 (b).**
3. **`JS_MUTATION_TOKENS` cannot see API replacement -- now VERIFIED BY
   INSTRUMENT.** With `CLIPBOARD_JS` undeclared (RC) or declared as an
   ordinary injected script (RD),
   `test_every_script_this_package_executes_cannot_mutate` PASSES it -- a
   script that replaces three page functions and adds a listener. It is held
   by `SCRIPTS_THAT_REPLACE_PAGE_BEHAVIOUR` and its two guards instead.
4. **A scanner that matches by attribute name** flagged nothing wrong in
   `press.evaluate` -- a pure function -- and invited a child to import it
   under an alias to keep the scanner quiet. Rejected as evasion; the four
   component checks are called by their own names, as `reveal` and
   `view_switch` already did.
5. **`N 136` may be the "Details" panel** behind "Show more analytics" (Entry
   7). Not this lane's row; its cell is untouched.
6. **The six profile edits** need an account-level reading of the
   "share profile updates" setting, a ruling that it satisfies condition 1,
   and `writes.py` asserting it at save time (lane L4). Entry 5.
7. **`M C85`** needs `/in/me/recent-activity/all/` admitted to look past the
   rail's 8 items for a poll of his own -- a boundary decision.
8. **Messaging moves only when his badge reads 0.** Read 1 at 22:14, 23:26
   and 00:43. The next session's first key: `badge,m43,m33`; on a 0 it fires
   `M M43`, captures the landing (the page `M M49`'s reader needs) and fires
   `M M33` -- three loads.
9. **`check_banked_evidence_is_reachable.py` lists 28 banked rows as
   describing a live run with no tracked script**, including long-standing
   `profile.md` rows (`A5`, `A7`, `G7` among them) and this lane's `G6` and
   `O3`, whose cells do name `scripts/_probe_live_lane_session_1.py`; `C41`,
   `N 134` and `C72`, written in the same form, are not listed. Report-only,
   asserted by no test, and not chased here.
10. **A long-running `find` process** on the box (PID 19532, about 4.7
    CPU-hours when sampled at 00:4x) is not this lane's and was left alone;
    whoever owns it should know.

## INSTRUMENTS -- register candidates, and what is disposable

Not appended to `_audit/INSTRUMENTS.md` on this branch: it is append-ordered
and shared, and several lanes are writing it; an append here is a merge
conflict. Each candidate names what killed it, as the register requires; the
orchestrator appends them at merge or declines them.

    candidate                                    shown failing by
    scripts/_probe_live_lane_session_1.py        H1-H7 in a scratch copy (Entries 1, 2): the ceiling
      the session ledger around BROWSER.goto     checked after the navigation, a refused address
      (40-load ceiling refused BEFORE a load,    counted, the messaging rule dropped, strings printed,
      20 s across processes), the badge-before-  the gap not waited, the budget off by one, and the
      messaging rule, the shape printer          first run's own leak (urn keys printed) restored
    linkedin_server/reveal.py                    R1-R6 (Entry 6)
    linkedin_server/view_switch.py               V1-V7 (Entry 6), including a restore that never
                                                 compares the view
    linkedin_server/profile_views_more.py        M1-M5 (Entry 8)
    linkedin_server/share_link.py                the child's 8 and P9-P18 (Entry 10, 13): the owner
      copy_own_post_link, CLIPBOARD_JS           check skipped, a startswith match, the hook not
                                                 installed, the Escape skipped or unreported, a read
                                                 that does not wait, a placeholder for the item's
                                                 text, an empty text promoted, a refusal dropping
                                                 its closure, a url fallback for an empty box
      share_link.read_item_price,                Q1-Q6 and Q4b (Entry 11): a zero accepted as a
      price_can_move                             price, the permalink dialect ignored, the off form
                                                 misspelled, an unread toggle turned into 0 (the one
                                                 that survived its first run), a bool read as a
                                                 count, the tool pressing without the check, the
                                                 readings not returned
    linkedin_own_item_link, end to end           T1-T5 (Entry 10): the counter reader ignoring the
      on the fixture through a stand-in BROWSER  page, the link withheld only when asked, the load
                                                 unreported, a derived address, a bad id reporting
                                                 a load
    tests/test_readonly.py                       RA-RC (a reader declared as a replacement script;
      SCRIPTS_THAT_REPLACE_PAGE_BEHAVIOUR and    the script run from a second, unsanctioned
      its two guards                             function; the script left undeclared), and RD, the
                                                 measurement that the token scan passes it

**A METHOD, for the register's method list rather than its instruments:**
**a counter that reads 0 at both ends of a press priced nothing unless it
could have moved.** Before trusting a price, count the counter's own label
in a capture of the page the press happens on. The `/feed/` basis's
`off_state` passed every gate check on a page that does not draw its label
at all (Entry 11); the gate compares readings and cannot know what a
reading is able to do.

**ALSO DISPOSABLE, from build (d) and the price fix, in the session
scratchpad:** `mutate_share.py`,
`mutate_escape.py`, `mutate_price.py`, `mutate_tool.py`,
`mutate_readonly.py` (the plant runners -- each copies the tree, plants one
defect, restores byte-for-byte, and handles CRLF anchors after two of them
reported "anchor found 0 times" instead of planting), `refreeze_attr.py`
(the re-freeze attribution, in the test file's own form), `c72_census.py`,
`verify_share_hits.py`, `doc_claims.py` (the tool docstring's write-verb
scan, run before the surface test).

**DISPOSABLE, in the session scratchpad, never tracked:** the planted-defect
runners, the child-free tree copier, the offline readers of captures
(badges, popovers, options, switches, the post menu, the revealed sections),
the census-paragraph inserter and the address-table row editor, and the
correction-pair lister. The one method worth keeping from them is written
in the entries: **read a capture offline in a local headless Chromium with
every request aborted and LinkedIn's script and policy tags removed**, and
check it against a live reading first (Entry 2's control: 20 live, 20
offline) before trusting what it says about anything else.

---

## Integration 2026-09-24

**The order** (orchestrator, 01:58): merge master into this branch, re-derive
every pin on the merged state, fix the eight red test pins, gate, commit --
PART 1, before any follow-up. **Disk at 01:55, before anything was done:**
this branch clean at its last commit, `3b4a69f` (this lane's close, which
does not resolve on `master` until the lane merges); master at `001f70b`, 24
commits past this branch's base; no `_TEAM_LEAD_*.md`. It matched the order,
so the order was followed as written.

**THE COMMITS:** `28eeccc` (the merge, with every conflict resolved and the
derived files regenerated), `5f11f1e` (the pins), and the commit that adds
this section.

### The merged surface, re-derived rather than summed

    tools          52   the base's 49 + this lane's linkedin_own_item_link
                        + master's linkedin_recent_job_searches (L3) and
                        linkedin_follow_company_page (L4)
    reads          39   writes 13 (L4's follow is the thirteenth)
    parameters     73   67 at the base + this lane's 4 + L4's 2
    sanctioned     12   mutating calls: 7 + this lane's 5; L4's follow
                        reuses perform's existing click

Each is measured off the merged registry by the surface tests, not trusted
from the sum. The surface test is renamed `..._fifty_two_tools`, with its
record.

### Conflicts: 13 files, and how each was resolved

- **The count sites** -- `server.py` (two hunks), `README.md` (two),
  `linkedin_server/__init__.py`, `tests/test_server_surface.py` (three),
  `tests/test_every_tool_is_on_the_surface.py`, the tool-surface pin: every
  paragraph from both sides kept, the numbers above written in.
- **The census, per row, against the merge base** (a comparison of the three
  git stages of each file, row by row):

      file                  one side only        both sides
      profile.md            5 (ours)             6: P A8 A11 A13 A17 A19 A21
      network.md            15 (ours 3, theirs 12)   0
      read-addresses.tsv    17 (ours 4, theirs 13)   0
      messaging-and-content.md   merged by git: no overlapping hunk

  A row changed on one side takes that side. **The six own-profile-edit rows
  changed on both:** this lane's side only INSERTED its dated "NOT SAVED"
  paragraph, and master's cleanup lane rewrote the rest of each cell (the
  RELEASED BY citation), so both are kept: the lane's paragraph, then
  master's cell. That is the case the order allows; nothing was guessed.
  `network.md` also carries a paragraph outside the table that only master
  changed (lane L4's delta for `N 47`); it is master's.
- **The derived files** (`_audit/INDEX.md`, `_audit/RULINGS.md`,
  `blocker-map.tsv`): master's taken, every resolved path staged, then
  regenerated with `--write` twice -- the second sweep changed nothing --
  and `--check` exits 0 on all three. Against master's copy, the blocker map
  differs in exactly four state cells (`P G6`, `N 134`, `P O3`, `M C72`) and
  in 126 reason-rank recounts (its ninth column alone).
  `completeness-candidates.tsv` changed on neither side and was NOT
  regenerated: it harvests local captures under `_state/`, not tracked files,
  so regenerating it would be a new harvest rather than a merge step.

**A CORRECTION TO THE MERGE COMMIT'S OWN MESSAGE.** It says "26 rows changed
on one side only take that side". The count is **37**: 20 census rows in the
two table files plus 17 address-table lines. The message was written from an
estimate and not from the comparison's output; this line is the record.

### The pins, re-derived on the merged tree

`scripts/census_completion.py --check`, measured after the merge (the lane's
forecast deltas were against its base and were NOT applied):

    adjudicated         434 -> 437      delivered_broad    100 -> 103
    delivered_strict     75 -> 79       gap                270 -> 267
    unfired              25 -> 24       gap_read            66 -> 63
    b3_admitted          40 -> 37       b1_no_ruling        15 -> 14
    PINNED_B1_ROWS       P G6 leaves its hold

Every move is this lane's four live promotions; master's own figures had
moved from the lane's base, which is why the numbers on the left are not
the ones this document forecast in its closing section.

**The census-derived test pins**, each for the same rows:

- `test_banked_evidence_is_reachable`: `M C72` and `N 134` pinned (their
  gitignored citations sit in PRIOR readings that earlier waves wrote), and
  the unreachable count 15 -> 18;
- `scripts/triage_read_gap_rows.py`: `N 134` and `P O3` dropped from its
  verdict table (51 read-GAP rows, 51 verdicts);
- `tests/test_triage_instrument.py`: `EXPECTED_NOW` re-derived to 76 GAP
  rows, R 9 (`M C72` left); a new dated constant keeps the old value;
- the pointer graph: `N 135`'s vestigial positional "Same" is written out as
  the reference it stood for (`N 133`'s page), so it no longer re-points
  when a row above it changes; `pointer-graph.tsv` re-pinned 69 -> 67 (the
  two moves, both intended: `N 134` has evidence of its own, `N 135` is no
  longer positional), and the selftest's calibration literal moved with it.

### Gates, run and NOT run

**RUN**, all on the merged tree:

- **The navigation-derivation and page-string guards on the merged
  `server.py`**, where lane L4's tools and this lane's meet:
  `test_navigation_is_never_derived`, `test_readers_emit_no_page_string`,
  `test_tool_envelopes_emit_no_page_string` -- 765 passed.
- **The census instruments**, by exit code: `census_completion.py --check`
  0, `check_read_addresses.py` 0, `check_write_classes.py` 0,
  `ruling_holds.py` 0, `pin_census_rows.py --check` 0,
  `measure_pointer_graph.py --check` 0, `check_jobs_directions.py` 0.
- **The corpus guards**: `check_cited_shas_resolve.py` 0,
  `check_contingent_writeoffs_carry_a_reopener.py` 0, the three derived-file
  `--check`s 0; `check_asserted_names_resolve.py` exits 1 on eight findings,
  every one in another wave's document and every one pinned by
  `tests/test_an_asserted_name_resolves.py`, which passes -- none is in this
  lane's document.
- **`scripts/impact_gate.py --against 001f70b`, planned and NOT run**: the
  plan widens to the full suite (224 of 239 test files reachable), and the
  order says not to run a full suite locally while six lanes share the box --
  measured at the time: six pytest processes, CPU 100% in three samples.
- **In its place, a selection of 62 files** at two workers: the gate's 17
  corpus-wide guards, the order's named corpus guards (correction, cited
  sha, reopener, identity, audit index, rulings register), the tests of the
  code files changed on both sides (the three surface tests, the prose-count
  and package-docstring pins, `test_tools`, the two page-string guards), the
  read-only boundary tests, this lane's module tests, lane L4's and L3's new
  tests, and the census tests. **4581 passed, 1 failed, in 30 min 41 s.** The failure was
  real and was the merge's: `test_ci_shard.py::test_the_timings_table_still_
  prices_most_of_the_suite` -- the timings table prices 157 files, master
  has 234 test files (0.671, over the two-thirds line) and the merge 239
  (0.657, under it), because this lane's five new test files carry no
  timings. **Repaired by measurement, not by moving the line:** the five
  files were run alone into a junit report and added through the shipped
  `ci_shard.seconds_per_file`, with their provenance appended to the
  table's own (a loaded box, so their seconds are high). 162 of 239; the
  shard tests pass (131).

**NOT RUN:** the full suite (CI runs it after the orchestrator's merge);
CI itself (nothing pushed); the 3.10 cell; any live fire.

### Master moved three more times while this lane integrated it

The order says to integrate a newer master the same way. Master moved past
`001f70b` three times during Part 1, and each was merged in turn:

    at     master      lane                                   merge commit
    03:42  d65759f     R: 245 exclusions returned to GAP       7bd064f
    04:05  209a831     G: three guards hardened               2b118e6
    04:33  ff98a7f     S: people search takes a keyword
                          and four facets                     a77d194

**Lane R (`7bd064f`).** The census, per row against the merge base: no row
changed on both sides -- lane R's rows take lane R's cells (234 across the
three table files), this lane's take this lane's (P A8 A11 A13 A17 A19 A21
A25 G6 L1 L8 O3; N 20 45 134 135; M C38 C48 C72 C85 M33 M43 M49), and every
line outside the tables was changed on lane R's side only. The triage
headline split: lane R's 117 kept as a dated constant, `EXPECTED_NOW` 116
(R 12, `M C72`). A selection of 43 files -- the 17 corpus-wide guards, the
named corpus guards, the census tests, lane R's four new tests --
**3283 passed, 0 failed**.

**Lane G (`2b118e6`).** A clean merge, after which two hardened guards saw
this lane's files for the first time:

- **The navigation guard now treats a reader's RETURN as a derived
  navigation** and found two sites in this lane's session-1 harness: the L1
  post-summary capture and the post-menu capture, each opening an address
  built from the newest activity id of his own rail. Lane G found the same
  class in `server.py` and two probes and DECLARED them -- not fixed, not
  waived -- pending a ruling on whether a walk of his own rail is a derived
  navigation. This lane's two are declared beside them, with the same
  argument plus the orchestrator's recorded call for `M C72`. **A finding
  about session 1, stated rather than smoothed:** both navigations ran live
  before the rule could see them.
- **The cited-sha guard now case-folds its slot keywords** and found one of
  this lane's commits cited in a capitalised "COMMIT" slot; the citation now
  says it does not resolve on `master` until the lane merges.

A selection of 32 files -- the corpus-wide guards, lane G's changed tests,
and the tests of every module whose readers or error fields lane G touched
and this lane calls (`test_share_link`, `test_view_switch`, `test_reveal`,
`test_profile_views_more`, `test_press`, `test_readonly`, `test_writes`,
`test_tools`, `test_server_surface`) -- **4063 passed, 0 failed**.

**Lane S (`a77d194`).** The tool-surface pin: both branch pins kept, the
merged pin re-derived at **52 tools and 78 parameters** (master's 69, this
lane's 4, lane S's 5), measured off the merged registry. The surface and
boundary tests: 282 passed. A selection of 32 files -- the corpus-wide
guards, lane S's reader tests, the census tests, the page-string guards,
`test_tools`, `test_readonly` -- **3730 passed, 0 failed**.

**THE PINS AS THEY STAND AFTER THE LAST MERGE**, re-derived on that tree
(each merge re-derived them on its own tree; only the last set is live):

    adjudicated        197      delivered_broad    108
    delivered_strict    79      gap                507
    unfired             29      gap_read            91
    b3_admitted         37      b1_no_ruling        19
    PINNED_B1_ROWS      P G6 out; lane R's N 23 and lane S's four filter
                        rows in

After every merge: the derived files regenerated with `--write` twice (the
second sweep changed nothing) and `--check` 0 on all three, and every census
instrument exited 0 (`check_asserted_names_resolve.py` aside: the same
eight findings in other waves' documents, pinned by its test, which passes).
**NOT RUN after any of the three:** the full suite (six lanes share the box;
the order says not to), CI, the 3.10 cell. **If master moves again before
the orchestrator merges this branch, that merge is the orchestrator's;** the
chase is stopped here so Part 2 can start.

---

## Part 2 -- offline follow-ups, 2026-09-24

The order's six follow-ups, one commit each, after Part 1. Nothing is fired.

### (a) PRICE: the gate refuses a price that cannot move, and the permalink gets its own basis

**FIRST, A CORRECTION TO SESSION 1, FOUND WHILE BUILDING THIS.** Before
writing the basis I read what this repository had already measured about the
reaction toggle, and it contradicts part of Entry 11:

    "Reaction button state: no reaction"  OFF  the feed, his rail, AND an item
                                               permalink, 2026-08-30/31
    "Reaction button state: Like"         ON   his profile rail, 2026-09-04
    "Unreact Like"                        ON   his own liked post's permalink,
                                               2026-09-23/24 (session 1)

So there are two label FAMILIES, not a feed dialect and a permalink dialect:
the permalink drew the state family's OFF label on 2026-08-31, and the
"Unreact" family on 2026-09-23. Whether LinkedIn changed the permalink's
labels in between, or draws a different component there, is not known.
Three session-1 statements follow from that and are corrected in place, each
with a pointer here: Entry 11's "`off_state` read 0 whatever happened"
(overclaimed -- an unreaction drawn in the state family would have moved
it; what a zero cannot do is tell unmoved from unmovable); Entry 11's
inferred OFF form "React Like" (unmeasured, and the measured permalink OFF
label is the state family's); and finding 2 of the closing section (the
react write's real defect is reading the "Unreact" ON label, which (b)
takes). **The first fire's price is still unverifiable, and the fix still
stands**: 0 of a counter that counts one label cannot distinguish a toggle
drawn ON, a toggle drawn in the other family, and no toggle at all.

**BUILT (offline):**

- `dom`: the "Unreact" family's two prefixes as constants, dated and
  sourced; `read_reaction_surface` counts both (None, never 0, when a count
  did not read); a pure `reaction_toggle_counts` turns one reading into
  `toggles_off` and `toggles_on` across both families -- a reaction or an
  unreaction moves both, one up and one down, whichever family is drawn.
- `press`: a sensitivity basis of its own for `/feed/update/`, ordered before
  `/feed/` (the table matches by containment, first entry wins), naming the
  two toggle counts; a pure `check_price_can_move` -- a sensitive basis whose
  named counters all read an integer and sum to 0 is refused
  `price_cannot_move`; `disclose` asks it after its first reading and BEFORE
  the click, and `check_counters` refuses the same zero after a press for a
  caller that skipped it. Classified `after_a_read` in the refusal inventory
  and reached by a real input, like every other refusal.
- `share_link`: `read_item_price` is now a thin reader over `dom`, and the
  zero rule is `press`'s -- the lane's own copy of both is deleted; the
  module also refuses an unreadable price before its trigger. The tool drops
  its pre-check (the module refuses first) and returns two readings, not
  three.

**SHOWN FAILING ON THE SHAPE OF THE VACUOUS FIRST FIRE.** The new test feeds
`press.evaluate` exactly load 25's reading -- a permalink, `off_state` 0
before and after, the menu closed -- and asserts no permit. Run against the
committed `press.py` it FAILS with `permitted: True`; on the new code it is
refused (`sensitive_counter_not_read`: the permalink's basis names the toggle
counts). Plus eight plants, each alone in a scratch copy, all red:

    plant                                                        red
    A1 the permalink basis removed                                28
    A2 the post-press zero rule removed                            2
    A3 disclose's pre-click check removed                          1
    A4 check_price_can_move never refuses a zero                   3
    A5 toggles_on ignoring the "Unreact" family                    3
    A6 an unread family count made a zero                          2
    A7 share_link's pre-trigger zero check removed                 1
    A8 share_link's pre-trigger unread check removed               1

Baseline and restored: 167 passed (`test_press` and `test_share_link`).

**CORRECTED 2026-09-24, found by (c)'s gate: THIS BUILD GREW THE PAGE-TEXT
INVENTORY.** `read_reaction_surface`'s new family loop handed its loop name
`key` to a debug line, and `key` is a name `dom.py` binds from page data
elsewhere; `tests/test_page_text_is_never_printed.py` tracks a tainted name
module-wide, so the pinned count for `linkedin_server/dom.py` read 10 against
9 from this commit on. Nothing the page wrote reached a log -- the value was
always one of two literals -- but the rule is on the binding, and it was
right to go red. Nothing in this build's gate ran that guard; the next
build's selection is where it showed. Repaired by renaming the loop's names
(the commit after `cdf1c42`), and the inventory reads 9 again.

### (b) REACT: the react write reads the other label family; nothing fired

**THE DEFECT, stated from (a)'s correction rather than from the order's
wording.** The order said the react write should "also aim at the permalink
label ('Unreact Like')". It should not AIM there -- a reaction is made from
the OFF state, and the OFF label the write aims at is the one measured on
permalinks on 2026-08-31. What it could not do was READ the ON state in the
other family: its three reading sites -- the preview's direction
(`_read_item_permalink`), the click-time re-read (`_live_control`) and the
verification after the click (`_verify_after`) -- counted only the state
family's prefix, so his own reacted post, whose toggle reads "Unreact Like",
counted ZERO controls: UNKNOWN at preview (a refusal for the wrong reason:
"a page that had not arrived"), and a reaction that LANDED in that family
would have been verified UNKNOWN. That item is very likely the one this
write last reacted to (the spec records a reaction left on one of his items
on 2026-09-03, and the post reads "1 reaction").

**BUILT (offline, against frozen worlds; nothing fired, no grant issued):**
one pure reader in `dom`, `reaction_toggle_state`, shared by all three sites
so the preview and the click cannot read one page two ways: `reacted` when
the one toggle wears an ON label in either family, `no_reaction` only on the
state family's MEASURED OFF label (the only label a click is aimed at),
`unmeasured_off` -- refused, never aimed -- on the "React" family's inferred
OFF label, and `unknown` for anything but exactly one toggle. The
verification treats either OFF family as not reacted. `read_reaction_surface`
reports the other family's names in `labels` too, so the receipt's
`newly_observed_reaction_labels` carries "Unreact Like" after such a
reaction. The spec's residue and two comments that still said the ON label
had never been observed are corrected.

**A SIBLING LANE'S TEST, re-aimed rather than deleted.** Lane L4's
`test_a_string_count_no_longer_carries_itself_out_of_live_control` proved
its repair by planting a bare `int()` in `coerce.as_count` and expecting the
page's string to escape in a ValueError. The react arm no longer calls
`coerce.as_count`: its counts are type-checked inside
`dom.reaction_toggle_counts` (a string count makes the state `unknown`). The
property the test asserts first -- the string does not escape -- still
holds; its control now plants the naive `int()` counter where the
protection lives. Nothing was loosened: the control still goes red.

**RED-PROOFS, each plant alone in a scratch copy of the package:**

    plant                                                           red
    B1 the preview reads the state family only                       3
    B2 the click reads the state family only                         1
    B3 the verification reads the state family only                  1
    B4 an unmeasured OFF label treated as the measured one           3
    B5 the other family's names left out of the labels               1

Baseline and restored: 14 passed (`test_react_direction_is_read_where_it_
acts`, six of them new). The write suites, the follow-page tests, the
page-string guards and the corpus guards: 2185 passed with the one sibling
test red before its re-aim, then 54 passed on the two files it touches.

**CORRECTED 2026-09-24: "the corpus guards" OVERCLAIMED.** One of them,
`tests/test_page_text_is_never_printed.py`, was red on this tree from (a)'s
commit on (see (a)'s correction above), so the run that read 2185 passed with
only the sibling test red cannot have included it. Run afterwards on an
archive of this commit (`cdf1c42`), it fails: 1 failed, 19 passed. The other
numbers stand as they were read.

### (c) N 76: his own profile judged control by control, and the gate taught to see it

**WHAT THE ORDER ASKED, AND TWO FACTS THE BUILD TURNED UP.** The order: the
gate's blanket `no_sensitivity_basis` for `/in/me/` becomes per-control
evidence, per `IN-ME-NO-BLANKET-BAR`. That is built. Building it turned up
two measured facts that decide what `N 76` can do next, and neither was on
the record:

1. **THE GATE COULD NOT SEE HIS PROFILE AT ALL.** `press.disclose` reads
   `page.url`, the LANDED url, and `/in/me/` lands on his vanity form with
   `?isSelfProfile=true` behind it. Measured in-process on an invented
   vanity before this build: `check_address` refused it
   `address_not_admitted`, `reachable_by_this_route` False -- NEVER, for the
   one profile the allowlist exists to admit -- and `evaluate` never reached
   condition 3. Every live press on `/in/me/` would have been refused there
   whatever any basis said. Reads accept the redirect (`browser.goto` asserts
   the requested url) and writes accept it (`writes._assert_landed`); the
   press gate was the one reader that did not.
2. **THE SHAPE THIS ROW WAS PLANNED ON NOW MATCHES LINKS.** Read offline from
   the 2026-09-23 capture of his profile (session 1, load 4, in `_state/`;
   zero loads), structure only:

        on his profile as captured                       2026-09-19   2026-09-23
        [aria-haspopup], page-wide                                1            9
          of which <a href> to a member profile root              -            9
          all 9 to one member (the one 60 of the page's
            70 member links point to: a proxy for the owner)      -          yes
        [role=menu] / [role=menuitem] / [role=dialog]         0 / 0 / -    0 / 0 / 0
        [aria-expanded], page-wide                                -           43
          in main (38) + main's footer (1)                        -           39
          of which the 9 links above                              -            9
        the overflow control: button, type=button, aria-expanded,
          no aria-haspopup, no href; main-scope [aria-expanded] index        5

   Every `[aria-haspopup]` there is an anchor carrying
   `aria-haspopup="dialog"`, and activating an anchor follows it: a
   navigation. None of the nine is the overflow trigger the 2026-09-19 plan
   meant, which carries `aria-expanded` and no `aria-haspopup`. The 2026-09-19
   count is a reading with its own date, not a wrong one. Nor can
   `[aria-expanded]` be judged as a shape: on this page it also matches the
   same nine links, and top-card and rail toggles whose function nobody has
   identified. The `componentkey` attribute every control carries is a
   per-render UUID, so no component name pins the overflow either: only its
   position does.

**BUILT, in `linkedin_server/press.py` (nothing pressed, nothing loaded):**

* **`/in/me/` IS JUDGED PER CONTROL.** A `SENSITIVITY_BASES` entry of kind
  `per_control`, matched EXACTLY (a judgement on the profile root says
  nothing about `/in/me/recent-activity/all/` or `/in/me/edit/...`), naming
  its ruling. A control is admitted by a recorded DISCLOSURE judgement -- which
  is a basis like any other, so route (b)'s whole-argument rule and the price
  rules apply to it -- refused by an ACTION judgement (`control_judged_an_action`,
  NEVER while its evidence stands), or refused NOT-YET because nobody has
  judged it (`control_not_judged`, which names the remedy). Both refusals are
  pure functions of the url and the shape key, so both are taken before any
  contact. An entry with no evidence, no verdict, or a basis kind condition 3
  does not know is not a judgement and is treated as none.
* **THE TWO MOMENTS AGREE.** `sensitivity_basis(url, shape)` answers a mapping
  for every control on a per-control surface, judged or not, so the pre-press
  `check_basis` and the post-press `check_counters` reach the same refusal
  through the one `_basis_refusal` -- were it None, the post-press moment
  would say `no_sensitivity_basis` about a surface that has an entry. `shape`
  is optional throughout, and every caller that omits it gets what it got.
* **COMMITTED JUDGEMENTS:** `[aria-haspopup]` on `/in/me/` is JUDGED AN
  ACTION, with the evidence above written into the entry. `[aria-expanded]`
  is NOT judged, for the reason above.
* **HIS PROFILE AS LANDED IS ADMITTED AS `/in/me/`, ON LINKEDIN'S OWN
  ASSERTION** (`press.self_landing`, `press.admitted_address`): a profile ROOT
  on `https://www.linkedin.com` whose `isSelfProfile` values all say `true` --
  the anchor the operator-ruled names reader already stands on, and stricter
  than it (every value, not any). The verdict says `self_landing: True`; the
  composer and third-party checks, the basis lookup and a reading's surface
  list all read the admitted form. Absent, `false`, contradictory, a page
  beneath the root, another host or scheme: refused exactly as before. The
  parameter name and the self-profile address are pinned equal to
  `server`'s.

**WHAT `N 76` WAITS ON NOW, specified for session 2.** The row stays PRESS.
The overflow control can be aimed only by position, and a position-pinned
judgement is a table shape the gate does not have: `controls` is keyed by
shape. So the next step is a decision before it is a build:

    step  what                                                   loads presses
    1     load his profile through the self-profile loader        1-2      0
          (isSelfProfile retried once on ABSENT); capture the
          page to _state/
    2     offline: the main-scope [aria-expanded] list by           0      0
          structure (tag, type, href, aria-haspopup, an svg
          inside), and the overflow's index read BY NAME from
          the capture by the lead -- never by the gate
    3     DECISION FOR THE ORCHESTRATOR: is an index-pinned         0      0
          disclosure judgement admissible -- one control at one
          scope and index, with a pre-click check that the
          control there still carries the judged signature
          (button, type=button, no href, no aria-haspopup)? If
          yes, that is a table extension to build and red-prove
          offline before any press
    4     one press through press.disclose, scope main, that        0      1
          index, with a reading key whose needles are the
          2026-09-19 set: copy link, follow link, share
          profile, personal link

`P J4` and `P D28`, the two other `/in/me/` rows the cleanup moved to
MEASURE under the same ruling, meet the same table: `[aria-haspopup]` is
refused there, `[aria-expanded]` is not judged, and `P J4`'s "Open to"
dropdown is another position in the same top card.

**RED-PROOFS, each plant alone in a scratch copy of the package; the new
tests are also run against the `press.py` before this build:**

    plant                                                              red
    on the press.py before (c) (the new and re-aimed tests)            41
    C1  the blanket bar restored                                       19
    C2  the /in/me/ entry matched by containment, not exactly           1
    C3  a landing with NO assertion admitted                            6
    C4  a page BENEATH the profile root admitted as the landing         3
    C5  an action judgement reported as NOT-YET                         2
    C6  a disclosure entry with no basis kind taken as a judgement      2
    C7  an entry with no evidence taken as a judgement                  1
    C8  the landing's member segment checked as landed                  4
    C9  a reading's surface compared on the raw landed path             1
    C10 the pre-click price read off the surface, not the control       1
    C11 the post-press basis read off the surface, not the control      1
    C12 the pre-press basis read off the surface, not the control       8
    C13 an unjudged control resolving to None (the moments drift)      14

Baseline and restored: 128 passed (`test_press`). C3 also turns a
STRANGER's unasserted profile into a per-control verdict instead of
`address_not_admitted` -- the ordering test's third-party row goes red --
which is the failure the root-and-assertion rule exists to prevent.

**GATES.** The impact plan for `press.py` widened to the full suite (161 of
240 test files, since `server.py` imports it), so by order the full suite was
NOT run locally. Run instead: the 15 test files that use the press gate, the
editor-field, orphan-module and blast-radius tests, and the 18 corpus-wide
guards -- 36 files, 3643 passed and 1 red, `test_page_text_is_never_printed`,
which had been red since (a)'s commit and is repaired in its own commit
(`45c46c8`; see (a)'s correction). Then, on the committed tree, that
selection widened by everything the changed DOCUMENTS reach (the shipped
`impact_gate.impact_set` over the session document, the network census
table, the rulings register and the blocker map: 94 files, under the widening line on
their own): 97 files, 5893 passed, 1 skipped, 3 red. Two were
`test_stale_process_is_announced`, an artifact of committing `404da96` while
the run was loading `2b75d01`, green on the stable tree. The third was real:
`test_prose_that_makes_a_claim` found a sentence in `self_landing`'s
docstring that put a member-path placeholder beside the words "the read
allowlist admits" -- a sentence saying the allowlist admits ONLY `/in/me/`,
but the guard reads the sentence, not the intent, and the repository has
paid for exactly that shape before. Reworded in the next commit; the three
files re-run: 164 passed. The census instruments: all exit 0 but
`check_asserted_names_resolve`, whose eight findings sit in other waves'
documents and are pinned by its test; the derived files are at a fixed
point.

### (d) M C85: his all-activity list admitted, so a poll post of his can be found

**THE ORDER'S WORDS:** "Admit `/in/me/recent-activity/all/` (his own
activity, a closed segment) so his own poll posts can be found. If he has
none, NEEDS-TARGET stands." Session 1 found no poll among the 8 items his
profile's activity rail draws (Entry 2); the rail's "Show all posts" anchor
opens this list, which draws the rest.

**BUILT (nothing loaded, nothing pressed):**

* `readonly._ALLOWED_URL_PATTERNS` gains ONE anchored line,
  `^https://www\.linkedin\.com/in/me/recent-activity/all/?$` -- the `/in/me/`
  form only, no class, no wildcard, no query, no sub-path -- with its
  argument on the line. It REVERSES A STATED SCOPE and says so: lane L1's
  articles line listed `/recent-activity/all/` among what it did not admit;
  that comment now carries a dated pointer, and L1's test moves the address
  out of its refused neighbours with the same pointer.
* `tests/test_own_activity_all_admission.py`, in L1's shape: both spellings
  admitted through the shipped gate; fourteen neighbours refused (another
  member's list, the activity root, the comments and reactions lists, five
  other activity tabs, a query, a sub-path, a longer word, two traversals);
  the articles list shown admitted by its OWN line, so neither line stands
  in for the other; a control removing this line, which refuses the target
  and moves no neighbour (the revert path, proven); the blast radius with
  `blast_radius.newly_admitted` -- exactly its own two spellings, nothing
  newly refused -- and the instrument's own control, a family pattern over
  the activity tree, admitting the comments list and a traversal onto a
  third party.
* The boundary re-freeze: `_ALLOWED_URL_PATTERNS` `c37e98f84ee443f2 ->
  b99f3c765fcb8043`, 49 -> 50 patterns; the tree minus exactly this line
  hashes to the value replaced; dropping the pre-existing articles line
  instead lands on `fcd2612ef29ac056`; seven of eight digests
  byte-identical, `<functions>` unmoved.
* The address table: `M C85` gains the list as an also-driven address
  (admitted), and its gate moves RULING -> MEASURE -- the next thing past the
  boundary is a look at an admitted page, not a decision. No pin moves
  (`census_completion --check` green: MEASURE is not blocked-on-nothing).
  The census cell carries a dated note.

**EXPECTED, NOT MEASURED: WHETHER THE LIST KEEPS THE `/in/me/` FORM.** Its
sibling `/in/me/recent-activity/articles/` SERVED EXACTLY on its first load
(session 1, load 12: relation "SERVED, exact"), so this one probably does
too. A redirect would widen nothing: `browser.goto` asserts the requested
url.

**RED-PROOFS, each plant alone in a scratch copy (the new file, L1's
admission tests and the boundary invariant):**

    plant                                                        red
    on the readonly.py before (d)                                  6
    D1 the line widened to every activity tab                     19
    D2 the line accepting any member's activity                    4
    D3 the line accepting a query                                  4
    D4 the line admitting a sub-path                               8
    D5 the line removed (the admission not made)                   6

Baseline and restored: 104 passed.

**THE CAPTURE SPEC FOR SESSION 2 (one load, zero presses, zero writes):**

    step  what
    1     load /in/me/recent-activity/all/ once; record the landing as a
          RELATION (served exact, or redirected by depth), never the url;
          read the health line (walled, challenge terms)
    2     in main, by structure: item urns by type, the rail reader's
          authorship check on each item, poll-shaped nodes
          (`main [class*="poll"]`), and -- offline in the capture -- the
          count of "N votes" phrases. State the scope: what the first render
          draws; scrolling for more is not sanctioned
    3     capture the page to the gitignored state directory; if a poll post
          OF HIS is found, its urn stays there, never in a tracked file
    4     offline, not in the session: if a poll of his exists, build the
          results reader from the captured markup -- counts only, under the
          feed-content ruling -- and fire it in a later key; if none exists,
          NEEDS-TARGET stands and the address table's gate returns to RULING

**AND THE LATER KEY TAKES ITS ADDRESS FROM ITS ARGUMENTS** -- registered
since this spec was drafted, `PAGE-MAY-VETO-NEVER-SUPPLY` (on master, and
merged into this branch after Part 2 -- the last section below): the poll
post's id is the tool's argument, supplied by
the caller, and the package may only VERIFY it against his own list and
refuse it when it is not his; the list never supplies the address. That is
the DECIDED source this row already carried ("from tool arguments only"),
now a registered rule.

**GATES:** the admission, L1-admission, boundary-invariant, blast-radius,
search-blast-radius and prose tests, 142 passed; the address table's checker
91 of 91 green with the new also-driven verdict; the census instruments as
before. Then, on the committed tree (`7b38ffd`), every test file that drives
the read boundary (68), the 18 corpus-wide guards and the census and
document guards -- 93 files: 5918 passed, 4 skipped, 1 red, and the red was
real: `test_the_census_prose_matches_the_boundary` reads the allowlist COUNT
out of a census correction row, which still said 49. The row now says 50
and names this line as the latest admission (the next commit). The full
suite was not run locally: `readonly.py` is imported by nearly every test
file, so the plan widens, and by order that run is CI's.

### (e) N 136: the panel is probably the one behind "Show more analytics" -- a note, the state left as it stands

**THE ORDER:** "A census note that it may be the 'Details' panel behind
'Show more analytics'." Written into row `136` of the network census. What
the note rests on is this document's own record, not a guess: the press row
`136` names as its REOPENER was taken live in session 1 for `P O3`
(Entries 7 and 8), permitted by the reveal gate with the url and the
counters held, and `profile_views_more` read what it drew -- a
"Highlights" section of three value/label pairs (top location, top
industry, top company) and a "Details" section, a companies breakdown of 5
entries, each a share in percent, whose largest entry equals the top
company. So a breakdown IS drawn on that page, behind the press.

**NOT MEASURED, and the note says so:** whether "Details" also breaks down
locations and industries (the reader found one breakdown, of companies), and
whether the row's "top locations, industries and companies" means the three
top values or three breakdowns. **The state stays MEASURED-ABSENT, as the
order asked for a note;** the row's own reopener condition -- "a breakdown
panel drawn under any name on that page" -- is met, so its state is for the
census owner to re-rule, with `P O3`'s proving fire as the evidence and
`linkedin_who_viewed_me(show_more_analytics=True)` as the tool that returns
it (`more_analytics.revealed_insights`). Zero loads.

### (f) The six own-profile edits: the account-level setting, found by name, not yet by address

**THE ORDER:** where the dialog draws no notify control, his account-level
"Share profile updates with your network" setting, read OFF before the edit,
satisfies condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD (the orchestrator's
amendment, registered since as `SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED`
on master, and merged into this branch after Part 2); if neither can be
established the row is NEEDS-OPERATOR. "Find that setting's page and build
its reader. If a capture exists, do it offline; otherwise write a capture
spec for session 2. Read only; never toggle it."

**FOUND BY NAME, offline, in the settings index captured in session 1**
(`/mypreferences/d/`, load 15, zero presses), read from the page's own data
and re-checked for this section:

    setting key      notifyNetworkForUpdates
    display name     "Sharing profile edits"    (the key's display-name map)
    identifier       notify_network_for_updates (the key's identifier map)

LinkedIn's current label for the setting the amendment names is "Sharing
profile edits"; the words "Share profile updates" occur 0 times in the
capture.

**NOT FOUND BY ADDRESS. No capture of the setting's own page exists** (every
`_state/` of every checkout searched for the label and the identifier's
spellings: the only hits are the settings index itself and the cached script
bundle read below), so no reader is built: a reader over imagined markup
would be a claim. The index draws a link to the setting's CATEGORY,
`/mypreferences/d/categories/profile-visibility`, and every category page is
refused by the boundary's `/mypreferences/d/categories/` substring. The
index's own slug-to-address pattern, measured on the settings it does link
(`darkMode` -> `/mypreferences/d/dark-mode`; `showProfilePhotos` ->
`/mypreferences/d/settings/show-profile-photos` -- the `/settings/` family
holds 5 of the index's links, all display preferences), gives two
candidates and no way to choose offline:

    /mypreferences/d/notify-network-for-updates
    /mypreferences/d/settings/notify-network-for-updates

Both, the category page and the old `/psettings/` address below are refused
by the shipped boundary today (driven through `readonly.is_read_url`,
2026-09-24); `/mypreferences/d/dark-mode` is admitted, the control.

**ONE MORE READING, AND IT ORDERS THE TWO.** LinkedIn's own settings bundle,
cached in the package's browser-profile backup in the gitignored state
directory (2026-08-30), carries a list pairing its OLD settings slugs with
the new ones. In that list `activity-broadcast` pairs with
`notify-network-for-updates` -- the old `/psettings/activity-broadcast`
page, a family the boundary refuses outright, named here so a ruling does
not rediscover it -- and, in the same list, `profile-photo-visibility`
pairs with `show-profile-photos` and `videos` with `autoplay-videos`, the
two whose new addresses the index draws, both under
`/mypreferences/d/settings/`. So the `/settings/` candidate goes FIRST:
DERIVED from two of two known pairs, not measured.

**THE CAPTURE SPEC FOR SESSION 2, each step a separate decision:**

    step  what                                                  loads presses
    1     a ruling admitting ONE candidate, exact and anchored --   0      0
          /mypreferences/d/settings/notify-network-for-updates
          first -- on the ONE-NAMED-SETTINGS-PAGE-AT-A-TIME
          precedent that admitted dark-mode
    2     one load, captured closed; the capture answers: SERVED    1      0
          or REDIRECTED (as a relation, never the url); the
          switch's accessible name; its aria-checked / checked;
          whether the page draws exactly one switch
    3     if it redirects, the same for the second candidate --    0-1     0
          or, if the redirect lands on the category page, a
          separate ruling for that one load

**THE READER, specified and not built:** one switch; its state read off the
browser's own `checked` property (the verification `update_setting` already
trusts), its name matched by exact equality to the display name above;
returns one of lane L7's `profile_editor.ACCOUNT_READINGS` -- `off`, `on`,
`unknown` -- and nothing else. It is taken BEFORE the change is entered and
handed to the seam lane L7 built for exactly this (master, merged here):
the `account_share_updates` keyword of `profile_editor.read_save_gate`,
which `writes.perform` calls without it today, so the save gate refuses
wherever the dialog draws no named notify control. **READ ONLY: this lane
never presses the switch.** Condition 1 asks for OFF to be READ, never made
so -- and turning it off would itself be a settings write this order does
not grant.

**IT IS NOW THE LAST OFFLINE PIECE THE SIX ROWS WAIT ON.** Lane L7's save
gate also refuses while the dialog draws a switch it cannot NAME
(`6_unnamed_switch_unresolved`), which the registered amendment requires,
and the intro editor draws two. Session 1's capture identified them ('Open
Profile' and 'Profile Premium Badge', Entry 5) by the text of their section,
read offline -- the switches carry no accessible name, which was the one
thing the gate classified on. **This paragraph first said the six rows
needed that recognition built as well; lane L7 built it the same day** (its
follow-up 1, "recognised by structure -- code 6 lifted there only", merged
into this branch at the second master merge below), and its session-2 queue
for `P A8`, `A11`, `A13`, `A17`, `A19` and `A21` now waits on exactly two
things: this reader wired at the seam, and his setting reading OFF at fire
time. So the critical path is the capture spec above -- a ruling admitting
one address, one load, the reader built offline from that capture -- and
until it is walked the six rows stay where session 1 left them.

### Master merged once more, after Part 2 (`b230287`)

Master moved to `1902fcb` while Part 2 was built -- lanes L7 (writes to his
own profile) and Y2 (43 capabilities admitted as rows), and two rulings
batches, among them the amended notify condition (f) was written for and
`PAGE-MAY-VETO-NEVER-SUPPLY`. Integrated so the branch hands over
merge-ready; the order's rules, applied as in Part 1:

    file                                   resolution
    _audit/_census/messaging-and-content   C72 changed on both sides: ours the
                                           (a) correction mid-cell, theirs
                                           only APPENDED lane Y2's DRAWN note
                                           -> both kept; every other row one
                                           side only -> that side
    _audit/_census/read-addresses.tsv      no row on both sides: ours C85,
                                           N 76, P D28, P J4; theirs sixteen,
                                           including Y2's new rows
    _audit/RULINGS.md, blocker-map.tsv     derived: theirs, every resolved
                                           path staged, all three generators
                                           --write twice, then --check

Code merged without conflict (`server.py`, `writes.py`, the correction
guard). The census instruments are green on the merged tree,
`census_completion --check` included -- no pin moves -- and the
asserted-name checker's findings are the pinned eight. **Gate, on the
committed merge, scoped to where the two sides meet** (the write tests where
(b) meets lane L7's `writes.py`; the tool-surface, envelope and reader
guards where (a) meets `server.py`; the press and boundary files by their
own tests; the census and document guards where the Part 2 notes meet lane
Y2's rows; the 18 corpus-wide guards): 57 files, **4396 passed**. The full
suite was not run locally, by order.

Two Part 2 sections now cite what the merge brought: (d)'s later key takes
its address from its arguments (`PAGE-MAY-VETO-NEVER-SUPPLY`), and (f)'s
reader returns lane L7's `ACCOUNT_READINGS` into the seam L7 built for it.

**MASTER MOVED ONCE MORE, TO `7d89b8d`, AND MERGED WITHOUT CONFLICT** --
lane L7's three follow-ups: the intro editor's two unnamed switches
recognised by structure, `P B9` and `P I14`/`I15` recorded, and its
session-2 queue for the six intro rows. That follow-up is why (f)'s last
paragraph now names this lane's reader as the last offline piece. The
blocker map regenerated to a fixed point (derived candidate columns only);
the census instruments green, no pin moves.

## Session-2 preparation, 2026-09-27 -- OFFLINE ONLY

The orchestrator's order of 2026-09-27 16:45 IST: prepare live session 2 with
no browser, no attach and no page loads; session 2 itself runs only on its
separate go. Four items -- (a) the setting's address, (b) its reader wired at
the save gate's seam, (c) a session-2 harness written under
PAGE-MAY-VETO-NEVER-SUPPLY, (d) the plan,
`_audit/2026-09-27-live-session-2-plan.md` -- each its own commit, on a branch
fast-forwarded to master `2eb90ad` first (the order's sample said the tree was
clean at `aa559de`, an ancestor of master; disk agreed at 16:34).

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key and the orchestrator's own
memory; every step that needs one names it by role.

### (a) The setting's address: admitted for reading, on an application of ONE-NAMED-SETTINGS-PAGE-AT-A-TIME

**THE CALL IS THE ORCHESTRATOR'S, AND IT APPLIES AN EXISTING DECISION.**
Step 1 of the capture spec in (f) above: admit
`/mypreferences/d/settings/notify-network-for-updates`, exact and anchored,
for reading, and that path alone -- the operator's settings ruling of
2026-08-31 (ONE-NAMED-SETTINGS-PAGE-AT-A-TIME) applied to a second named
page, as it was once to dark mode. No register entry is written.

**BUILT, as lane L1's follower-list carve-out was built -- two gates, each
naming the one address:**

* one anchored line in `readonly._ALLOWED_URL_PATTERNS`, beside the dark-mode
  entry, with its argument on the line: what the page is for (condition 1 as
  amended), where its identity comes from (the settings index captured in
  session 1), that the address is DERIVED and never drawn on a capture, that
  the other candidate is not admitted, and that it is READ ONLY;
* one entry in `readonly._FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS` excusing
  exactly `/settings/` and `settings` -- the two forbidden substrings the
  address trips, measured -- for exactly that anchored address. The forbidden
  tuple is unchanged at 33, so both words keep their full reach everywhere
  else: nothing is NARROWED, which is the trade the dark-mode entry declined
  for `language` and `autoplay-videos`.

**THE CONTROLS THE ORDER NAMED, and more** (`tests/test_notify_setting_admission.py`):
both spellings admitted through the shipped gate; refused, each on the gate
that names it -- the sibling `/mypreferences/d/settings/show-profile-photos`,
the two siblings the dark-mode entry declined by name, this address with a
sub-path (`/anything`), a query, a traversal onto a sibling and onto the
account-ending address, the same path in another case, the OTHER candidate
(`/mypreferences/d/notify-network-for-updates`, allowlist), the category page
(`/mypreferences/d/categories/`), the old `/psettings/activity-broadcast`
(`/psettings/`) and the settings family root. EITHER gate alone admits
nothing; the pair's blast radius over the shipped corpus plus these spellings
is exactly its own two spellings, nothing newly refused; and no write spec
names the address or exempts either word, so it is no write surface.

**THE RE-FREEZE, in the comment chain's attribution form:**

    _ALLOWED_URL_PATTERNS                     6240409ec52c4ab2 -> 18e5958586c2c367   54 -> 55
    _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS   76d7b10899530d69 -> 14f567fd160048a8    3 -> 4

The tree minus exactly the two entries hashes to the two values replaced;
the line alone is 18e5958586c2c367 / 76d7b10899530d69 and the exemption alone
6240409ec52c4ab2 / 14f567fd160048a8; dropping the pre-existing dark-mode line
instead lands on ec6311ecf485ba6a; six of eight digests byte-identical,
`<functions>` unmoved. Two other pins moved with it and say why:
`tests/test_job_alerts_read_boundary.py`'s count of pattern exemptions
(3 -> 4, a dated note) and the census allowlist-count claim in
`_audit/_census/messaging-and-content.md` (54 -> 55, naming this admission as
the latest). `P O6-O20` in `_audit/_census/profile.md` -- the fifteen
visibility toggles, one of which this setting is -- carries a dated note: its
page is named for reading; its toggles stay GAP.

**RED-PROOFS, each plant alone in a scratch copy (the new file and the
boundary invariant):**

    plant                                                        red
    on the readonly.py before (a)                                  8
    R1 the admission not made                                      8
    R2 the exemption widened to the settings family                5
    R3 the allowlist line widened to the settings family           4
    R4 the exemption excusing '/settings/' only                    6
    R5 the exemption left open at the end (sub-paths excused)      6
    R6 the allowlist line left open at the end                     2

Baseline and restored: 35 passed. **If session 2's capture shows this
address redirects, the second candidate gets its own admission then** -- not
now.

### (b) The reader for "Sharing profile edits", wired at the save gate's seam

**THE CHOICE THE ORDER LEFT OPEN, TAKEN: BUILD IT NOW, against synthetic
pages, because session 2's plan validates it on the real capture, offline
and inside the session, BEFORE any of the six edits fires** (the plan's step
for it, and the harness's offline check). The other option -- capture in
session 2, fire the edits in a session 3 -- stays the fallback the plan names
if that validation does not agree.

**THE READER, `profile_editor.read_account_share_updates`, exactly the spec
from (f):** one control of role switch or checkbox whose accessible name is
EXACTLY "Sharing profile edits" (Playwright's own role-and-name engine, the
comparison made inside the page -- lane L7's P B9 discipline, so a count comes
back and never text); its state from the browser's `checked` PROPERTY when it
is an `input[type=checkbox]`, cross-checked against `aria-checked` when both
are drawn, and from `aria-checked` alone otherwise; the answer one of lane
L7's `ACCOUNT_READINGS`. Every doubt is 'unknown', and 'unknown' is never
'off': no control of that name, two of them, a name that only contains it, a
disagreement, a control with no state, a button of that name, a failure (its
exception TYPE only). **READ ONLY: it presses nothing** -- asserted on its
body's calls. The address and the name are constants beside it
(`ACCOUNT_SETTING_URL`, `ACCOUNT_SETTING_NAME`), and
`served_at_account_setting` says whether the page kept its own path: a
redirect -- to the other candidate, to the category page that lists this
setting among others -- reads 'unknown', because an admitted address is not a
served one.

**THE WIRING, in `writes.perform`, for EDITOR_SAVE_ACTIONS only:** one load of
the setting's page through `_load` -- the read door, unrelaxed -- BEFORE the
editor is opened, so before the change is entered (the amendment's word; the
setting lives on another page); the answer handed to all four
`profile_editor.read_save_gate` calls the action can make (select, fill, the
Premium badge's switch gate and its Save gate); the receipt gains
`account_setting` (the reading, whether the page was served, the counts,
constants-only reasons). A page that cannot be loaded gives None, never 'off',
and does not stop the write: a dialog drawing its own notify control can still
establish condition 1, so the gate decides -- and it refuses None wherever the
dialog draws no control of its own. No rule in `profile_editor` moved; lane
L7's seam received its input, and three stale sentences that said nothing
supplied it were corrected in place.

**THE ORDER'S FOUR TESTS, through the real preview, `consume` and `perform`
over lane L7's editor world with his settings page added**
(`tests/test_account_share_updates.py`): OFF passes (Save pressed, value
stored, `condition_1: account_setting_off`); ON refuses (two shapes of switch);
unknown refuses (no switch, an unnamed one, two named, a redirect); a missing
reading refuses (the page cannot load: `reading: null`, the error's type).
Beside them: the reading is taken before the editor is opened, once per write;
a dialog control still governs whatever the account reads, both ways; an
unrecognised unnamed switch still refuses with the account OFF (code 6); every
save-gate call in `perform` passes the reading (structural); and the reader
on twelve synthetic pages.

**ONE GUARD CAUGHT THE FIRST DRAFT, and was right.** The navigation guard
tracks a tainted name across the whole module, and `landed` is one in
`writes.py`: binding the new function's booleans from it spread the taint
through `value` and `reading` to every `goto(page, url)` in the file. The
locals are now named for the function, as the probes' own docstrings say to.
`tests/reader_leak_baseline.json` gains the two new readers, both measured
`clean` by the guard's own `measure()`; no other verdict moved, so only those
two lines were added.

**RED-PROOFS, each plant alone in a scratch copy (the new file and lane L7's
editor-commit tests):**

    plant                                                          red
    on writes.py and profile_editor.py before (b)   the new file does not
                                                    import: collection errors
    B1 the fill path's save gate loses the reading                   9
    B2 the reading taken AFTER the editor is opened                 10
    B3 a reading that could not be taken made 'off'                  3
    B4 a redirected page's reading counted                           1
    B5 a named control with no state read as off                     1
    B6 the checked pseudo-class asked of any control                 3
    B7 the name matched loosely                                      1
    B8 two controls of that name accepted                            1
    B9 an input whose aria-checked disagrees trusted                 1

Baseline and restored: 75 passed. B8 SURVIVED THE FIRST RUN: the later
exactly-one counts refused the same world for another reason, so the test
now asserts the count the reading reports and the reason it gives, and B8
goes red.

**WHAT THE SYNTHETIC PAGES CANNOT SAY:** whether LinkedIn draws this setting
as any of these shapes. The live page may name its switch through a title
paragraph with no accessible name -- the intro editor's shape -- and then this
reader answers 'unknown' and nothing fires. That is the case the in-session
validation exists for.

### (c) The session-2 harness, written under PAGE-MAY-VETO-NEVER-SUPPLY -- and session 1's harness converted to it

**`scripts/_probe_live_lane_session_2.py`: 34 closed keys**, one for every
step of the plan (d) that is not an outward act. **The rule is three
mechanisms, each enforced:**

* **every address is a module constant, or one of the package's own
  composers** -- `search_verticals.compose`, `member_rosters.compose`, the
  digit templates lane L1 and session 1 already use -- **filled from the
  caller's `--item`**, each item validated as a closed shape before anything
  loads (1-20 ASCII digits; a thread id by `threads.valid_thread_id`). A
  refusal never echoes what was typed;
* **a reading may only say no:** a group must be among the MEMBERSHIPS his
  Groups page returned this session (not its suggestions), a post among the
  ids his rail returned with authorship established, an attendees list only
  after this session's `event` read that event and saw it link its own list.
  A mismatch stops the key with nothing loaded;
* **the caller may read a result and name an item from it; the file never
  does.** `job_detail` writes the organisation it resolved; `n84` takes an
  organisation only as `--item`.

**THE NAVIGATION GUARD FINDS NOTHING IN IT, AND IS SHOWN ABLE TO:** its own
engine over this file reports zero derived sites, and over a copy with one
line changed -- an item taken from a reading on disk, a navigation to where
the last one landed -- it reports the site (both in the new test file). No
entry was added to `KNOWN_DERIVED_NAVIGATIONS`.

**The ledger** (`_state/live2/ledger.json`, gitignored) is session 1's --
every load counted through a wrapper around `BROWSER.goto`, the 41st refused
before it navigates, the spacing waited out across processes -- plus two
things session 1 did not have: **D1's five searches**, a sixth `/search/`
load refused before it navigates, and **one driver at a time**, a lock that
refuses a second harness process.

**What it writes.** His settings page raw -- it draws no other person -- and
every other page as a SKELETON reduced in the process before anything is
written: tags, attribute names, classes, roles and closed ARIA states kept;
every other text node and attribute value replaced by its shape (letters,
digits, length) and an 8-hex HMAC under a key made once per session and kept
in the gitignored state directory, so two captures compare and a list of
names cannot reverse a hash; an id and every attribute naming it shaped with
one key, so a label still finds its control; addresses keep LinkedIn's own
path words and query parameter names; a closed set of LinkedIn's own UI words
survives verbatim. Tool envelopes are raw where the tool is name-free by its
own contract, and reduced where it can carry a person (notifications,
connections, a job posting, an opened thread): integers, booleans, the
package's literal fields and organisation, group and posting ids kept, every
other string shaped. **The (b) reader still reads a skeleton**: shown on a
synthetic page, it finds "Sharing profile edits" through a label and an id
both shaped with one key, and reads the state.

**Presses: ONE click site in the file**, `press_and_read` (asserted on the
syntax tree), on a trigger found as exactly one match: a click -- an open
verb by the probe rule -- a reading of the opened menu BY ATTRIBUTE and by
our own words compared inside the page (only our words and integers come
back), a skeleton of the open state, then Escape. Two anomalies stop the
session: a menu whose own words do not go away again, and any message event
on `/messaging/`, which is a conversation opened. Words are counted only
where VISIBLE, because a menu LinkedIn keeps in the DOM while closed must not
read as opened.

**The setting's offline check** (`setting_offline`): the (b) reader over the
setting's own capture in a local headless Chromium whose context is offline
and runs no script (both flags asserted on the syntax tree), against the live
reading, as one of seven verdicts. **The case a capture cannot answer is
reproduced, not argued:** a switch whose ON is held only in the `checked`
PROPERTY reads ON live, and its capture -- no `checked` attribute -- replays
OFF. The live step therefore records the property and the attribute side by
side, and that case reads `STATE-NOT-IN-MARKUP`, never `DISAGREES` or
`AGREES`.

**Lane D's LQ-4** (`attach_check`): the attach runs in a child process with
the driver's protocol log on; the parent keeps only the
`Browser.setDownloadBehavior` sends and the answers matched to them by id,
each reduced to closed words, as the lines arrive -- a decoy line naming a
tab never survives (tested). Its filter is proven on synthetic lines only;
the plan says what a mismatch with the real log's form reads as.

**Read offline before it was written, counts only, from session 1's own
captures (no load):** his profile draws exactly ONE
`button[aria-label="More"][aria-expanded="false"]`, page-wide and in main --
so lane D's LQ-1 and the overflow `N 76` waits on are one control, which the
inventory had as DERIVED; the header's Me trigger is one button named exactly
"Me" on two captures; his newest post draws an empty comments list while his
profile's rail draws four "N comments" phrases; all eight rail items are
activity urns with authorship established. What each changed is in the plan.

**SESSION 1 CONVERTED, AND ITS DECLARED ENTRY DELETED.** Judged cheap, and
it was: `post_capture`, `l1_post_summary` and `own_link` take the post from
the caller's `--activity` (1-20 ASCII digits, never echoed) and
`activity_veto` refuses one that is not among his authorship-established rail
ids; `newest_own_activity_digits` is gone. The navigation guard now finds
nothing in `_probe_live_lane_session_1.py`, so its entry in
`KNOWN_DERIVED_NAVIGATIONS` is deleted and the comment beside it records why.
Its tests: the two that pinned the old choice are replaced by five that pin
the veto, the digits rule and the selection.

**Every corpus instrument over both files, run on them directly:**
navigation 0, output 0, page text 0, import-time effects 0, gated
interactions 0, context closers 0, tab leaks 0, never-branched controls 0,
unguarded navigations 0. The tests: `tests/test_live_lane_session_2_harness.py`,
106; `tests/test_live_lane_session_harness.py`, 33.

**RED-PROOFS, each plant alone in a scratch copy (the two harness test files
and the navigation guard):**

    plant                                                            red
    on the session-1 harness before the conversion      2, and 4 errors
    C1  an address taken from a reading on disk                        3
    C2  the search cap removed                                         1
    C3  the ceiling not checked before the navigation                  1
    C4  a suggested group accepted as a membership                     1
    C5  authorship not required (session 1's rail ids)                 3
    C6  a text node kept verbatim in a skeleton                        2
    C7  classes shaped in a skeleton                                   2
    C8  the shape's hash not keyed                                     4
    C9  every envelope string kept                                     1
    C10 hidden words counted as drawn                                  1
    C11 a conversation opened by a press not an anomaly                1
    C12 every menu taken as closed again                               2
    C13 no STATE-NOT-IN-MARKUP verdict                                 2
    C14 every protocol answer kept, not only the sends' own            5
    C15 the artifacts folder not checked                               2
    C16 a rider allowed without its page                               1
    C17 an item's digits read by isdigit, not as ASCII                 1
    C18 a second click site                                            1
    C19 session 1 takes his post off the rail again                    1
    C20 the replay runs the capture's scripts                          2
    C21 the replay reaches the network                                 1
    C22 a second driver let in                                         1

Baseline and restored: 783 passed. None survived. C21 is caught only by the
structural test, which is why that test exists: no synthetic document can
witness a network the replay never needed.

**ONE DEFECT CAUGHT BY THE STRICT-ASCII CHECK BEFORE THE COMMIT:** the
ellipsis in one of LinkedIn's labels, written as a `\u` escape, reached the
file as the character itself -- the tool channel decoded it. It is now built
with `chr()`, and the check reads the file's bytes, not the intent.

**WHAT IT DOES NOT DO.** The outward block is not in it; its loads are added
to the ledger by hand. Its vocabulary of LinkedIn's words is a list written
from the captures and lanes' records, not measured complete: a menu label
outside it survives only as its shape and count (the plan's D-2). Its
triggers were measured on captures of 2026-09-20 and 2026-09-23, and a
trigger that is not exactly one match refuses without pressing.

### (d) The session-2 plan

**`_audit/2026-09-27-live-session-2-plan.md`**, from an inventory of every
open capture spec and every built-unfired row on master, taken by a
read-only child of this lane over this branch at `2eb90ad` and kept in the
lane's scratch (its counts were re-derived four ways and agreed: 36 rows by
the header parse, the repository's own counter, `PINNED_B1_ROWS` and
`census_completion --check`). The plan orders it: the attach first (no
load), captures that need nothing from a fire, then the no-target fires,
then the captures that need a fire's result, then the outward block, which
fires only after he has seen each resolved identity once and names every
target by role. **At most 38 of the 40 loads and 5 of the 5 searches, two in
reserve.** Every step names its loads, the ruling it rests on, and whether it
needs him; the credential and session controls are excluded by name, `P N10`
among the seven.

**What the plan found that the inventory had not, all offline:**

* **the More control on his profile is ONE control** -- one match on
  session 1's capture, page-wide -- so lane D's LQ-1 and the overflow `N 76`
  waits on meet in one press; the plan asks the orchestrator to govern it
  once (D-1);
* **`linkedin_group_memberships` costs three loads, not one**: the tool
  brackets the Groups page with the feed at both ends, which moved the
  group steps' price;
* **`M C29` and `M C42` need a DIFFERENT post of his** than session 1
  captured: that post draws no comment, while his profile page, where the
  rail is, draws four comment counts -- so the plan's `own_post` takes one of
  those posts, named by the lead and vetoed against the rail;
* **a skeleton cannot learn a label nobody has measured** -- the ON form of
  "I'm interested" (`P I15`), a menu item outside the harness's words -- so
  the raw-capture question (D-2) is priced in the plan, not left abstract.

**The count, against the inventory:** of its 46 open capture specs, 27 are
captured in session 2, 6 (and one part) wait on items only he can supply,
3 go to session 3, 4 need an admission first, and 6 are optional,
superseded, conditional or unspecified. Of the 36 built-unfired rows, 15 are
fired -- every one of the 11 that need no target, `N 84` and `N 87`, and
`M M10` and `M M17` in the outward block -- 8 go to session 3 (the six
intro edits, `P B9`, `N 85`), 11 are outward rows whose target he has not
named (three of them blocked), and 2 are blocked reads.

**The decisions it puts to the orchestrator, D-1 to D-8,** and one to him,
D-9 -- the ids only he can supply. None is taken here.

### Integration, gates, and what did not run

**Commits on this branch, none pushed, none attributed**, each through the
pre-commit identity gate with 0 hits: `93d90c2` (a), `2761e35` (b), `4453124`
(c), `56f129a` (d), `826ad09` (a's census note, below), `3233ebd` (the merge
of master), and this section's commit.

**ITEM (a)'S CENSUS NOTE, MENDED AT THE GATE OF (c) AND (d).** Its note on
the profile census row O6-O20 wrote the two substrings its exemption excuses
in backticks. The refused-address check reads every backticked path in a GAP
row's cell as an address the row rests on, so it checked the substring
itself, found it refused, and counted the row: 74 against its pin of 73. (a)'s
gate never ran that check -- its selection named the read boundary's tests,
and this one reads the census through a script -- and the gate of (c) and
(d), built from every test that reads `scripts/`, did. The note now quotes
them, as the cell's own text does, and the check reads 73.

**THE ONE INTEGRATION**, at master's tip when the preparation was done:
`52b55b6`, 68 commits and 137 files past `2eb90ad` -- lane L8's outward
classes, the census applications of their rulings, and lane G's people-data
foundation. Six conflicts, each resolved against the merge base:

    file                                     resolution
    the profile census                       O6-O20 changed here only, O21 on
                                             master only, on neighbouring lines:
                                             each side's row kept
    tests/test_navigation_is_never_derived   master had emptied the table of
                                             three entries and kept session 1's
                                             harness as debt pending its
                                             conversion; (c) converted it, so
                                             the table is EMPTY and its note
                                             records the debt as paid
    tests/test_readonly_boundary_invariant   only the ledger notes: both kept,
                                             master's first, one more for the
                                             merge. The merged readonly.py equals
                                             master on eleven digests and this
                                             branch on its two, and the pin dict
                                             matches all thirteen, no hand edit
    the audit index, the rulings register,   master's, regenerated to a fixed
    the blocker map                          point over the merged corpus

`writes.py` and the reader baseline merged without conflict: (b)'s wiring --
the reading before the editor, the four save-gate calls, the receipt's key --
and its two readers are present beside lanes L8's and G's changes, and the
merged gate below runs both sides' tests over them.

**AND ONE THING THE MERGE BROUGHT INTO THE PLAN:** since lane G, the reply
preview's `who_this_would_reach` is a people record, as the ruling
`PREVIEW-NAMES-THE-RESOLVED-TARGET` has it -- the name and headline the page draws
for the conversation he named, sanitised, marked untrusted, returned at
runtime and never written. That is the identity the plan's outward block
shows him once; the plan's D-6 and its step 4.1 now cite it.

**GATES, each on a committed tree:**

    item     tree       files   result
    (a)      93d90c2       94   6100 passed, 4 skipped
    (b)      2761e35       75   4993 passed, 3 skipped, 1 xfailed
    (c)(d)   56f129a       97   5813 passed, 4 skipped, 1 xfailed, 1 FAILED:
                                the refused-address pin, mended in 826ad09;
                                that file and two boundary-reading census
                                files re-run, 28 passed
    merge    3233ebd      185   8822 passed, 8 skipped, 1 xfailed: (b)'s and
                                (c)(d)'s selections, every test file master
                                changed since the base, and the census and
                                boundary files (a) reaches

plus: the census instruments on the merged tree, all exit 0 but the
asserted-name checker, whose eight findings are the pinned eight in other
waves' documents; the three generators at a fixed point; red-proofs, (a) 6
plants, (b) 9, (c) 22, none surviving; strict ASCII over every file touched;
the changed Python compiled under Python 3.10.19.

**NOT RUN, named:**

* **the full suite locally**, by order: 82 of the merged tree's 267 test
  files were outside its gate, and CI's cells run them at the merge;
* **anything live**, by order: no attach, no load, no press. So every
  harness key, `attach_check` against the real driver's protocol log, and the
  offline replay of a REAL capture are proven only on synthetic pages, fakes
  and synthetic log lines;
* **the impact gate**: the selections above were built by hand and are
  named, each with its reason;
* **session 2 itself**, which runs on the orchestrator's separate go.

## Live session 2, 2026-09-28

The orchestrator's order of 08:04 IST, RUN LIVE SESSION 2 NOW, superseding
its own refresh order of 08:05 ("keep what you have already done, and skip
the rest of the refresh"). He was present and gave his permission. The
session ran from 08:20 to 08:49 on the Chrome he had started on port 9224,
which this lane never started, restarted or closed. **35 of the 40 loads, 5
of the 5 searches, 0 writes.** Chrome ended after the last run's teardown
(below). Four offline fixes the orchestrator ordered at 08:52 follow this
section, each shown failing first.

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key; every step below names them by
role, and a key POSITION, where one is given, is 0-based, as the
orchestrator counts.

### The go, and the three harness commits it needed

**The refresh's merge became a fast-forward.** Master had merged this branch
(`5189ea7`) as `b6993e5` and stood at `c94c39e`; the branch was
fast-forwarded to it, and the rest of the refresh was skipped by order.

* **`2f24ec4`, the go's deltas.** The three people searches (`N 94`, `N 84`,
  `N 87`) pass `include_names=True`, and `N 94`'s keyword search fires `N 79`
  off the same load. `P K1` is read off the `/in/me/` load: every control in
  main whose label mentions a verification, by structure, the label compared
  inside the page. `M M53` (`linkedin_messaging_presence`), `N 195`
  (`linkedin_recruiter_insights`) and `J 107` (`linkedin_search_jobs` with a
  company id and no keyword) are one-load keys, and `P S5` rides `N 132`'s
  load. 1083 passed, 1 skipped: the harness's tests with the seven corpus
  guards that read `scripts/`.
* **`d27090e`.** `job_detail` writes the organisation it resolved, by name
  and id, to gitignored state, so D-4's name could reach the orchestrator
  before any fire on it. 1056 passed, 1 skipped.
* **`41fea96`, mid-session.** The ledger counts the named-person door (the
  outward block, below). 813 passed, 1 skipped.

The skip in each run is the navigation guard's whole-tree complement, which
runs where CI is set. The navigation guard found no derived site after any
of the three.

### The session, load by load

    n   time      key                        surface        what it read
    1   08:20:30  setting                    mypreferences  SERVED, exact; 0 controls of the (b) name
    2   08:21:37  in_me                      in             self-assertion true on the first load;
                                                            7 [aria-expanded] in main; P K1;
                                                            in_me_more TimeoutError, nothing pressed
    3   08:23:31  n132                       analytics      N 132, P S5, P G7
    4   08:24:03  notifications              notifications  N 20, N 45
    5   08:24:40  j18                        jobs           J 18, J 37
    6   08:25:10  j39                        jobs           J 39
    7   08:25:40  j158                       jobs           J 158
    8   08:26:48  job_detail                 jobs           the organisation for D-4; the posting
    9   08:27:32  in_me                      in             the window in front: 44 [aria-expanded];
                                                            in_me_more TimeoutError again
    10  08:28:44  in_me_probe (scratch)      in             1 trigger; its scroll into view timed out
    11  08:29:15  m43                        messaging      M M43; C1; C8 opened, did not close
    12  08:29:56  outward_resolve (scratch)  messaging      read before the list drew: 0 rows
    13  08:30:31  outward_resolve (scratch)  messaging      10 rows, 0 matches
    14  08:31:14  n23                        feed           the badge, before
    15  08:31:42  n23                        mynetwork      N 23
    16  08:32:12  n94                        search         search 1 of 5: N 94, N 79
    17  08:33:31  outward_resolve (scratch)  messaging      both spellings: 10 rows, 0 matches
    18  08:34:08  n84                        search         search 2 of 5
    19  08:34:36  n87                        search         search 3 of 5
    20  08:35:00  company_people             company        N 102, J 108
    21  08:35:30  j107                       jobs           J 107
    22  08:40:51  M M1's preview (tool call) in             the named-person door; refused
    23  08:42:06  recruiter                  analytics      N 195
    24  08:42:35  presence                   messaging      M M53
    25  08:43:30  the brother's profile      in             the named-person door; a skeleton
    26  08:44:05  activity_all               in             M C85; the Me menu rode it
    27  08:44:34  followers                  mynetwork      P L2b
    28  08:45:03  own_post                   feed           M C29, M C42
    29  08:45:31  n104                       search         search 4 of 5
    30  08:46:00  n161                       search         search 5 of 5
    31  08:46:34  memberships                feed           the tool's bracket, before
    32  08:47:03  memberships                groups         5 memberships
    33  08:47:26  memberships                feed           the tool's bracket, after
    34  08:48:05  group_home                 groups         M C70
    35  08:48:44  group_members              groups         N 165, N 177

By surface: in 6, jobs 5, messaging 5, search 5, feed 4, groups 3,
analytics 2, mynetwork 2, mypreferences 1, notifications 1, company 1. The
closest two loads stood 22.7 s apart. Load 22 was recorded in the ledger by
hand after the run (the outward block says why). Every "scratch" row is a
disposable runner in the lane's scratch folder that took the harness's
ledger, counter and driver lock by import, so its loads were counted like
any key's.

### What the rows read

**FIRED AND PROVEN, each against its row's own bank condition** (the census
moves are recorded below):

* `M M43`: 5 conversations listed, 5 rendered, 0 placeholders; none opened
  (0 message events, and the page stayed the composer).
* `N 132` with `P S5`, and `P G7`'s tool-level fire: the headline and the
  delta drawn and not withheld, 2 metrics; 2 of 2 engagement cards read, 0
  unreadable.
* `N 195`: 44 profile views and 1 recruiter view over 90 days; 2 charts of
  13 points each, both read; 1 viewer returned as an anonymous record, and 1
  more drawn hidden.
* `J 18` with `J 37`: 6 recent searches read, 3 with the alert on.
* `J 39`: 24 job ids in 24 slots, 0 refused. `J 158`: 25 ids in 25 slots, 0
  refused.
* `J 107`: 7 postings at the organisation cleared under D-4, with an empty
  keyword, not capped.
* `N 23`: 10 rows, all parsed, each with a recipient id; the badge read 0
  before and 0 after, which says nothing about cost, and the row does not
  claim it.
* `N 94` with `N 79`: the keyword kept and both location ids applied; 10
  people records from 10 of 10 cards, 0 skipped, 0 headlines unread.
* `N 84` and `N 87`: the one organisation cleared under D-4, as the current-
  and as the past-company facet, each applied and kept; 10 people records
  each; 7 and 6 person results by the classifier.

**FIRED, NOT BANKED:**

* `N 20` and `N 45`: 10 notifications read, 0 of the invitation kind and 0 of
  the follow kind. Neither row's item was drawn, so neither is proven or
  refuted: a third reading, NOT SHOWN.
* `M M53`: the composer drew 0 suggestion cards (0 seen, 0 read). A thin
  reading, not a proof: the row stays where it is, with the empty composer
  on record.
* `P K1`: 6 controls in main labelled with a verification, all 6 linking to
  neither refused address (link kind "other"), none in a heading.

**CAPTURED, as skeletons (D-2):** his profile (loads 2 and 9; the file on
disk is load 9's, the second write replacing the first), the all-activity
list (`M C85`: 0 activity permalinks, 0 poll-shaped nodes and 0 vote phrases
by the old selectors, which the new markup no longer carries), the Me menu
open (lane Y's item 9: 8 of our words added, closed again), his followers
(`P L2b`: 20 member links of 33 anchors), his commented post (`M C29`,
`M C42`: 28 comment items), the composer with its unread row (lane L5's C1)
and with the folder menu open (C8), the two vertical searches (`N 104`: 44
anchors; `N 161`: 21, served at the same depth under a different address),
his Groups page (5 memberships and 5 others), one group's page (`M C70`:
reach AMBIGUOUS -- 122 anchors and not one post permalink, which a
membership gate, an empty group and a restyle all produce) and its member
list (`N 165`, `N 177`: 20 member links), the organisation's People tab
(`N 102`, `J 108`: 227 member links of 349 anchors), the posting (`J 124`,
`J 115`, `P M12`), the three people searches, the recruiter page, the
composer again (`M M53`), the jobs pages, the notifications, the
connections, the search-appearances page, and the brother's profile. His
own settings page is the one RAW capture, as the plan says.

### D-1: the More on his profile never became actionable

Three tries, nothing pressed. At 08:21 the window was maximized but not in
the foreground, and the press timed out on Playwright's actionability wait
(5 s). The orchestrator fronted the window with his own script, and it was
run before every press block after that. At 08:27, with the window in front,
the same press timed out again; at 08:28 a scratch probe found exactly one
trigger by the harness's handle and timed out scrolling it into view, before
any click. So the handle -- `main button[aria-label="More"][aria-expanded="false"]`,
exactly one match -- names a control that is not drawn (DERIVED from the two
timeouts with the window in front). Fix 3 below finds why.

### C8: the folder menu opened and did not close on Escape

The folder pill, found as exactly one match, pressed once: 4 items and 6 of
our words added, 0 message events. After Escape the harness read it as NOT
closed, so the key stopped as an anomaly, and C9 and C5 never ran. Nothing
inside the menu was pressed. The open state is a skeleton; the after-Escape
state is not (the anomaly stops before the next write), so which of the two
conditions failed -- a word still drawn, or the trigger still expanded -- is
not on record. Fix 4 below reads the open state.

### An occluded window draws less of the page

His profile, loaded twice: 7 `[aria-expanded]` controls in main at 08:21
with the window behind others, 44 at 08:27 with it in front. The page
hydrates lazily, and a covered Chrome window stops drawing frames (DERIVED
from the pair, one load each). A reading taken with the window covered
UNDER-counts, and nothing in the reading says so; everything after 08:25 ran
with the window fronted first.

### The setting: served, and its label is not the one the reader asks for

His settings page was served at its own address (`SERVED, exact`), and the
(b) reader found 0 controls named "Sharing profile edits". The live page's
switch is labelled "Share key profile updates" -- an `input` checkbox with
role switch, named through `aria-labelledby` -- under the page heading
"Share profile updates". So the setting was not read this session, and the
offline check says `LIVE-UNKNOWN`. The six intro edits stay in session 3.
Fix 2 below.

### The outward block

**THE RESOLUTION OF THE BROTHER'S THREAD, not resolved, twice.** The
receipt-safe conversation list with names (`include_names=True`), matched
whole-word and casefolded against the brother's spellings in the key:

* 08:29-08:30, key position 2: the first load was read before the list drew
  (0 rows -- the settle race), so the runner re-reads on the same page after
  rows draw, and the second load drew 10 rows: 0 carry the spelling, so 0
  one-to-one and 0 with the family name. Nothing was opened.
* 08:33, key positions 2 and 3, on the orchestrator's order of 08:32: 10
  rows, 0 carry either spelling.

The connections (`N 23`, 08:31) drew 10 people and 0 carry any of the six
words the key held then (positions 0 to 5: the father's two, the brother's
two, and the two others'). The page draws 10 connections on its first render,
so no route in this session reached him or the father without a scroll or a
search, and neither was ruled. The orchestrator ruled a people search for
the brother at 08:35 and cancelled it within the minute: the operator had
supplied the brother's exact profile link, in gitignored state, and the key's
class grew to 8 (position 6, a third spelling; position 7, the link's slug).

**M M1, THROUGH THAT LINK: REFUSED BY THE TOOL.** Its supplied target checked
on disk first -- gitignored, a profile link of the exact shape, its segment
equal to key position 7. The preview (`linkedin_message_from_profile`,
`LINKEDIN_ENABLE_WRITES=1` in the process) loaded that profile once through
the named-person door and refused before minting a token:
`write_attempt_blocked`, raised in `writes._direction` because the
observation's state came back 'unknown'. Replayed against a fake browser with
no network, it stops on the same line. On the live page the named-profile
reader, built on the old markup, could not establish its conditions on
today's profile, which draws hashed class names. Nothing was pressed, typed
or sent, and no token was minted. So `M M17` had no thread to reply in and
did not fire, and `M M10` has no older thread. All three go to session 3,
after lane L5 rebuilds its reader over a capture of the new markup.

**THE BROTHER'S PROFILE, AS A SKELETON (08:43, the orchestrator's order of
08:43):** one load through the named-person door, counted, nothing pressed,
no raw capture. Its controls in main, by LinkedIn's own words ("exact": the
word alone; "with a name": the word and then a name):

    Message    exact 2, with a name 4, visible 5
    More       exact 2, visible 1
    Follow     with a name 4, visible 4
    Connect 0, Pending 0, Following 0

So the page does not draw exactly one Message control in main, and it draws
two More buttons, one hidden -- the shape that failed D-1 on his own profile.
A page-wide count cannot aim either; lane L5's rebuilt reader must scope the
top card and take the visible control. The skeleton is routed to L5.

**The father and the two others:** counts only, as ordered: 0 in every list
drawn.

**THE LOAD THE LEDGER DID NOT COUNT, AND ITS FIX.** The wrapper around
`BROWSER.goto` counted only addresses the read door admits, and passed every
other navigation through uncounted -- but `goto(..., named_profile=True)` is
a second admitted door, and M M1's preview went through it. That one load
was entered in the ledger by hand after the run (load 22, marked so), and
`41fea96` makes the wrapper count the second door, with a test. Only that
navigation was affected: every other load went through the read door, and
the brother's skeleton at 08:43 was counted by the fixed wrapper.

### D-4, as the order asks it recorded

The organisation `job_detail` resolved on the first posting of `J 39`'s
collection was **cleared by the orchestrator against his resume's current
and past employers**, and used for `N 84` (current company), `N 87` (past
company), `company_people` and `J 107`. Its name and id live in gitignored
state only.

### Chrome's end

The last run's teardown ran at 08:48:45: close our own tab, then disconnect
CDP. At 08:49:16 the next attach failed with `BrowserUnavailableError`
before any load: nothing listened on 9224, and no process held the profile.
If our tab was the window's last, closing it ended the browser -- plausible,
not proven. The optional last read (his setting's switch by its live label,
one load) did not happen, and nothing else was lost. He will start Chrome
again for session 3. Fix 1 below.

### To session 3

* D-1 on his profile, with fix 3's handle and fix 3's finding;
* C8 with fix 4's close step, then C9 and C5;
* `M M1`, then `M M17` in the thread it makes, after lane L5's reader is
  rebuilt over the brother's skeleton; `M M10` needs an older thread;
* `M M33` and `M M49`: a rendered row reads UNREAD, so their receipt guards
  would refuse -- each would spend a load and bank nothing until he reads it;
* the setting, read by its live label (fix 2), then the six intro edits and
  `P B9` if it reads OFF;
* `N 179`, `N 85`, `N 194`, `N 172`, `N 93`; `M M53` again; the event, school
  and thread items he supplies (D-9); the father and the two others.

### Scratch, declared disposable

In the lane's scratch folder, none of it tracked: the outward runner
(resolve, fire, the brother's skeleton), the item setter, the runner that
passes items to the harness, the ledger's hand entry, the setting and More
inspectors and probes, the key-position checks, and the orchestrator's
window-fronting script. Each took the harness's ledger, counter and driver
lock by import, so nothing in it loaded uncounted except the one load above.

## After session 2, offline: the skeletons, the four fixes, the census

The orchestrator's order of 08:52: after the record, four offline fixes, each
shown failing first against today's skeletons; then the census moves for the
proven rows, the pins re-derived, the gates, and a commit with no
attribution. **The laptop restarted at about 09:57** with this lane's turn cut
off inside the census step; the orchestrator's resume order of 10:02 found
the branch at `d81511d` (fix 1's commit, "no page is closed as the browser's
last tab", which does not resolve on `master` until the lane merges) with the
four census files modified and nothing else dirty, and disk agreed at 10:03. **The four files were whole**: every changed
line a complete table row, its cell count unchanged, every cell but the state
unchanged, and the old reason cell intact after the new paragraph -- checked
line by line against `HEAD`. The step continued from there.

### The skeletons, committed as tracked copies (`5f70af8`)

**28 files under `tests/fixtures/live2/`, 3.3 MB**: the session's 27
skeletons and his settings page reduced to one. The harness writes a
skeleton with a keyed hash of every text it shapes, which compares two
captures and cannot be reversed without the key -- and the key sits beside
it in gitignored state. A tracked copy (`--export-fixtures`, `tracked_copy`)
carries no hash of anybody's words: **every keyed shape becomes one `x`**
(an empty value stays empty), an id reference keeps its hash as `k` and 8 hex
so a label still finds its control, and anything outside ASCII becomes a
character reference. Rendering each shape's LENGTH in `x` was tried first and
rejected on size: 14 MB, because one shape stands for a value of any length.

**WHY THE COPY, SHOWN:** `tests/test_fixtures_hold_only_synthetic_people.py`
reads the value in every person slot of a tracked fixture, and a keyed shape
in a member link is an undeclared candidate -- a planted page's keyed
skeleton fails it once, its tracked copy passes (a harness test). **THE GUARD
NARROWED, AS ITS OWN REMEDY SAYS:** 19 sites in the copies held a LinkedIn
word as a member link's first visible text -- "Send" 11, "Show all" 4,
"Premium" 4 -- so those three words are SKIPPED, not taken, and the link's
next text is read as its person; a name after a skipped word is still
convicted (shown), and a value that only contains one is a candidate like any
other. The identity gate and the shape guard passed all 28.

**A COPY LOADED IN A TEST NEEDS THE PAGE'S OWN ROUTE TO REFUSE EVERY
REQUEST.** The copies keep their stylesheet and image addresses' path words,
so a browser fetches them; `tests/network_guard.py` caught the first test
that loaded one without the route.

### Fix 1: never the browser's last tab (`d81511d`)

**THE RULE, ONE FUNCTION:** `linkedin_server/browser.close_tab_keeping_the_window`.
Our tab closes only while another open page remains in its context; when it
is the last, a KEEPER tab (a blank page) opens first and ours closes only once
the keeper counts as open; when no keeper can be opened, or the pages cannot
be counted, ours is LEFT OPEN and the caller only disconnects. The attach
teardown closes through it; a probe calls `BROWSER.close_tab(page)`. **What it
counts is the context's pages** -- his browser's default context, every
window of it -- so it never closes the tab whose closing would end the
browser; a window holding nothing but our tab, beside other windows of his,
closes with it, and the function's docstring says so rather than implying a
per-window rule Playwright cannot place a keeper for.

**MADE IMPOSSIBLE, WITH A TEST:** all 47 scripts that closed a page directly
were converted -- 46 by one mechanical line each, the attach-continuity probe
by hand because it attaches without `BROWSER` -- and a third check in
`tests/test_a_probe_closes_its_own_tab.py` fails on any `.close()` of a
receiver named for a page or a tab, in `scripts/` or the package, outside that
one function. The page matcher counts the rule's spelling as a close, so the
leak ratchet did not move (38).

**RED FIRST:** the old teardown, run end to end over a fake context with ours
as its only tab, left it **0 open pages** -- the state that ends a real
Chrome; the third check over the tree at `HEAD` before the fix found **48**
direct closes (47 scripts and the teardown); after it, 0.
`tests/test_the_last_tab_is_never_closed.py` holds the behaviour (8 tests).
**NOT PROVEN:** which window Chrome puts a keeper in, which no fake can say;
session 3's first teardown is the first live use.

### Fix 2: the setting reader asks for the switch's own label (`619870e`)

`profile_editor.ACCOUNT_SETTING_NAME` was "Sharing profile edits", the
settings INDEX's display name; the page draws no control of that name. It is
now "Share key profile updates", the label the page's switch is named by
through `aria-labelledby`. **RED FIRST ON TODAY'S CAPTURE:** the raw capture
replayed offline (headless, the context offline, no script) read 0 named and
'unknown'; after the fix, 1 named, an input, reading OFF -- the markup holds
no `checked` attribute, and the page's own toggle text reads Off. The tracked
copy reads the same, and the tests run on it: one named input read OFF, and
neither the index's name nor the page heading names a control there.
**WHAT IT DOES NOT SETTLE:** whether the live `checked` PROPERTY agrees. The
first live read of session 3 answers it, and the offline check's
`STATE-NOT-IN-MARKUP` verdict exists for the case where it cannot.

### Fix 3: D-1's More, inside the top card and only when one is visible (`f1f34a4`)

**WHAT TODAY'S SKELETONS SAY.** His profile draws no `h1`: the name is the top
card's one `h2`, and its section holds the card's actions TWICE, in two bars
of which the page shows one at a time -- [Open to, Enhance profile,
Resources] and [Open to, More, Enhance profile]. The old handle's one match is
the labelled More in the second bar, which his window width did not show
(DERIVED from the two timeouts with the window in front). The brother's
profile has the same two bars, each holding a More -- one by its text, one by
its label -- and the live count was 2 drawn, 1 visible.

**THE HANDLE:** `topcard_of`, the nearest section around the first `h2` in
main, with no class named (the classes are hashed); `topcard_control(page,
name)`, the button of exactly that name inside it, taken only when exactly
one is VISIBLE. **RED FIRST, END TO END:** the key on his profile at his
width -- the other bar hidden by one stylesheet rule standing in for
LinkedIn's, which no skeleton carries -- timed out on the old handle's click
(`ElementHandle.click: Timeout 5000ms exceeded`), as it did live, and now
refuses with nothing pressed (1 drawn, 0 visible). Five of the six new tests
were red on the old harness; the sixth records the old handle's defect and
passes on both. `in_me` now counts the top card's words, drawn and visible,
on every load.

**THE FINDING SESSION 3 NEEDS A RULING ON:** at his width the top card draws
no visible More at all. The bar it shows holds Resources where the other
holds More, and nobody has seen Resources' menu. D-1 can fire only on a
ruling to press Resources, or at a width that shows the More.

### Fix 4: C8's close step (`209d65a`)

**WHAT THE OPEN-MENU SKELETON SAYS:** an artdeco dropdown; its trigger, the
folder pill, reads `aria-expanded="true"` while open; its content is a sibling
holding four items -- Focused, Other, Archived, Spam -- each a folder CHOICE,
and no close control of its own. A click outside was the other way the order
named, and on `/messaging/` the skeleton certifies no neutral outside: the
list beside the pill is conversations. **THE STEP:** when Escape leaves the
trigger reading expanded -- and only if it read closed before the press, so
the click can only close what the first opened -- the same trigger is pressed
once more; never a third time; `closed_by` records which step closed it.

**RED FIRST ON TODAY'S SKELETON**, with the menu's behaviour installed: Escape
inert, as it was live, and the trigger toggling, as an artdeco trigger does
(ASSUMED from the component, never pressed live). The old code stopped with
`the_menu_did_not_close`, the session's own outcome; now it closes by its
trigger, reads 4 items and 0 message events, in 2 clicks. The controls: a menu
Escape closes takes 1 click; one nothing closes is still the anomaly after 2;
a trigger that reads closed with the words still drawn is not pressed again.
The click-site test holds two clicks, both on the trigger in
`press_and_read`, the second inside the one `if` that reads it expanded.

### The gates of the export and the four fixes, each on its committed tree

    commit    files   result
    5f70af8      10   2958 passed, 1 skipped (identity, credential, path,
                      and the seven script guards); 190 passed (the harness
                      and the fixture people guard)
    619870e       3   195 passed (the reader, the harness, the editor commits)
    f1f34a4       8   1095 passed, 1 skipped (the harness, the seven script
                      guards)
    209d65a       8   1099 passed, 1 skipped (the same)
    d81511d       3   48 passed (the last tab, attach, browser); 15 (the tab
                      guard and the last tab)

The skip in each is the navigation guard's whole-tree complement, which runs
where CI is set. The impact gate on the final tree is below.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/jobs.md` -- rows `18`, `39` and `158` read COVERED-UNFIRED, never fired; each fired live in session 2 on its own cell's bar and moves to COVERED-PROVEN. Row `107` fired and does not bank; row `37` is measured and stays.

**CORRECTS:** `_audit/_census/network.md` -- rows `23`, `79`, `84`, `87`, `94`, `132` and `195` read COVERED-UNFIRED, never fired; each fired live in session 2 on its own cell's bar -- lane S's whole bank rule for the three facets -- and moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/profile.md` -- row `S5` read COVERED-UNFIRED, never fired; it fired live on `N 132`'s load in session 2 and moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `M43` read COVERED-UNFIRED, never opened; it fired live in session 2, opening no conversation, and moves to COVERED-PROVEN.

**TWELVE ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar its cell set                          what session 2 read
    J 18    list label seen, an entry with keywords       6 of 6 with keywords; not redirected
    J 39    list container seen, ids non-empty            24 ids
    J 158   list container seen, slots above 0            25 slots, 25 ids
    M M43   rows rendered, no conversation opened         5 rendered, 0 message events
    N 23    one call that returns rows                    10 rows, each with a recipient id
    N 79    the name-returning reader, fired              10 people records, 10 of 10 cards
    N 84    ok, landed, kept verbatim or same values,     verbatim; 7 person results
    N 87      person results >= 1, panel settled,         verbatim; 6
    N 94      0 values refused (lane S's bank rule)       verbatim, both ids; 8
    N 132   one end-to-end call of the tool               headline and delta; 2 metrics
    N 195   fired live                                    44 and 1 over 90 days; 2 charts
    P S5    fired live                                    2 of 2 cards read

**NOT BANKED, EACH CELL SAYING WHY:** `N 20` and `N 45` (a third reading, NOT
SHOWN, again); `M M53` (the composer drew no card); `M M1` (refused by the tool
before a token). **AND A CORRECTION TO THIS LANE'S OWN END-OF-SESSION REPORT:**
it listed `J 107` as fired and passing. Its cell's bar also names the
default-location question -- whether LinkedIn narrows a keyword-less employer
search to his location -- and the fire does not settle it: the envelope
records no location applied, and no address the capture draws carries one. So
`J 107` does not move. **MEASURED, NO STATE:** `J 37`, by lane L3's own test at
no extra load -- `J 18`'s 3 alerts against the 5 in the mail inventory its cell
cites: unequal, so the jobs home does not carry every alert.

**HELD, A DATED NOTE IN EACH CELL:** `P C8` and `N 76` (D-1, fix 3's finding);
`M M7`, `M M8`, `M M9`, `M M28` (C8) and `M M22`, `M M27`, `M M29`, `M M31`,
`M M16` (C9 and C5, never reached); `M M10` and `M M17`; `M M33` and `M M49`
(the unread row); the six intro edits and `P B9` (fix 2). **CAPTURED, A NOTE
POINTING AT ITS TRACKED COPY:** `P L2b`, `M C85`, `M C29`, `M C42`, `N 104`,
`N 161`, `N 102`, `J 108`, `N 165`, `N 177`, `M C70`, `P K1`, `J 124`, `J 115`,
`P M12`, `P J4`, `P D28`, `P F1`, `P H11`, `P K8`, `P D26` -- no state moves on
a capture. `J 124`'s own question is not readable from its capture: the
posting's company-insights block drew 21 lines, and a skeleton shapes their
words (the cost D-2 stated).

**THE COUNTS**, file-wide by `scripts/count_census_states.py`, each slice's
delta written into its own count section:

    slice         COVERED-PROVEN   COVERED-UNFIRED
    jobs             19 -> 22          6 -> 3
    network           8 -> 15         20 -> 13
    profile          24 -> 25          9 -> 8
    messaging         7 -> 8          11 -> 10
    all four         58 -> 70         46 -> 34      GAP 584, unmoved

**THE PINS, MEASURED ON THE FINAL TREE AND RE-PINNED, NEVER SUMMED:**
`scripts/census_completion.py --check` named three figures and twelve
bucket-1 rows off their pins, and nothing else:

    delivered_strict    79 -> 91
    unfired             49 -> 37
    b1_no_ruling        30 -> 18
    PINNED_B1_ROWS      NO_RULING loses the twelve rows above

`delivered_broad`, `adjudicated`, `gap` and every other headline figure did
not move: a row changing class inside the covered states. The derived views
were regenerated with `--write` twice and `--check`: the audit index gains the
four correction edges, each with both markers; the blocker map moves the
twelve state cells; the rulings register does not change.

**THE AST DUPLICATE-KEY CHECK** (a scratch walker, shown firing on a planted
duplicate first): 591 tracked Python files, 4417 dict displays, **0 duplicate
keys**. It also reports one SET literal with a repeated member --
`_FETCH_NAMES` in `tests/test_api_call_sites.py`, `"urlretrieve"` twice since
`fbedfca` -- harmless in a set, its intended third member unknown; left for
its owner and not changed here.

### Gates on the final tree, run and NOT run

**THE IMPACT GATE**, `scripts/impact_gate.py --against c94c39e`, background,
offline, sharded by the gate itself (`-n auto --dist loadfile`). The diff
reaches 198, then 228, of 280 test files, so both runs widened to the full
suite at the gate's 45% line:

    tree       result
    1847a82    15 failed, 12055 passed, 9 skipped, 1 xfailed, in 17 min 33 s
    f4c82cf    PASS over the full suite, 12080 tests, in 18 min 31 s

**THE FIFTEEN, EACH REPAIRED AT ITS CAUSE, in `f4c82cf`:**

* **3, the reader-leak guard.** The last-tab rule takes a `page`, so the guard
  discovered it as a page reader with no recorded verdict. Its own
  `measure()` gives `not_driven:returned without reading the page`, and no
  other reader's verdict moved: one baseline line, and a `WHAT_WOULD_DRIVE_IT`
  entry declaring it NOT A PAGE READER, with why.
* **4 in `tests/test_people_search_readers.py` and 2 in
  `tests/test_a_covered_row_names_the_artifact_that_covers_it.py`:** pins
  naming `N 79`, `N 84`, `N 87`, `N 94`, `J 18` and `J 39` COVERED-UNFIRED.
  Both files say a fire that moves a row moves the pin in the same commit;
  they now pin COVERED-PROVEN, and the people-search pin checks that each
  banked cell opens on its banking with the earlier record after it.
* **4, `tests/test_the_offline_frontier_rows.py`.** Two of its rows moved
  again (`N 195`, `P S5`) and now open on their banking, the frontier's move
  kept after it. Two did not (`J 107`, `M M53`) -- and this lane had put its
  session-2 note FIRST in their cells, so neither opened on its move any
  more. Those two notes now close their cells instead.
* **1, the correction guard.** Row `18` cites this record on a line that keeps
  lane L3's "THE ROW WAS PRICED ON THE WRONG ADDRESS", about the row's own
  pricing: triaged NOT_A_CORRECTION, with what would make the entry wrong.
* **1, the cited-SHA guard.** `d81511d`, a commit of this branch, cited in an
  "at" slot: disclosed in place with its subject.

**THE CENSUS INSTRUMENTS AND THE THREE `--check`s**, on `f4c82cf`, by exit
code: `census_completion.py --check`, `check_read_addresses.py`,
`check_write_classes.py`, `ruling_holds.py`, `pin_census_rows.py --check`,
`measure_pointer_graph.py --check`, `check_jobs_directions.py`,
`check_gap_rows_on_refused_addresses.py`, `check_cited_shas_resolve.py`,
`check_contingent_writeoffs_carry_a_reopener.py`,
`check_census_locators_resolve.py` and the three generators' `--check` all
exit 0. `check_asserted_names_resolve.py` exits 1 on the eight findings
pinned in other waves' documents, none in this one.

**THE NAVIGATION GUARD'S WHOLE-TREE COMPLEMENT**, the one skip in every local
run above, run with `CI=1`: 11 passed.

**THE IDENTITY GATE:** the pre-commit exact-value gate on every commit of
this branch, 0 hits each (226 spellings); the shape guard,
`tests/test_no_committed_identity.py`, inside both full-suite runs, and again
on this section's commit.

**NOT RUN, named:**

* **CI**: nothing pushed, by order. Every number here is this box's Python
  3.13; the 3.10 cell is CI's.
* **Anything live**: Chrome on 9224 was not running and was not needed. So
  fix 1's keeper -- which window Chrome puts it in -- fix 2's reading of the
  live `checked` property, fix 3's handle at his width, and fix 4's trigger
  toggle are all proven offline only; each one's first live use is session
  3's.

## Live session 3, 2026-09-28

The orchestrator's GO of 12:42 IST, RUN LIVE SESSION 3, under the operator's
standing instruction ("do the needful": establish everything yourself, and ask
him nothing). The session ran from 12:52 to 13:09 on the Chrome the
orchestrator had started on port 9224 at 12:40, which this lane never started,
restarted or closed. **16 of the 40 loads, 2 of the 5 searches, 0 writes.
Three rows banked -- `J 107`, `N 194` and `M M53` -- and Chrome was still up at
the end.**

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key; every step below names them by
role, and a key POSITION, where one is given, is 0-based, as the orchestrator
counts.

### The go, and the harness change it needed

The branch fast-forwarded to master `5564c15`: this lane's session-2 wrap-up
with lane L5's named-profile read on top. The harness tests, the navigation
guard and L5's two named-profile test files: 863 passed, 1 skipped.

* **`ed858fe`.** Each session gets its own state directory
  (`LIVE_LANE_SESSION_DIR`, a closed shape: `live` and one or two digits), so
  session 3's ledger, key and captures sit in `_state/live3/` and its forty
  loads are its own. D-1 presses the ONE opener the top card draws, More or
  Resources, on the orchestrator's ruling, once. A menu drawn as a
  `role=menu` apart from its trigger is read. With the seven script guards:
  1109 passed, 1 skipped.

The skip in each run is the navigation guard's whole-tree complement, which
runs where CI is set.

**THE ATTACH CHECK, 12:52, 0 loads: PASS**, by lane D's LQ-4 rule. The
download behaviour was set with a path and then reset to the default with
none, both answered without error, in that order; the library's artifact
folders in the temp directory counted 2455, 2456 and 2455 before, during and
after; the reset reads restored, and the child exited 0.

### The session, load by load

    n   time      key (the ledger's)    surface        what it read
    1   12:52:54  read_named_confirm    in             2a: the named read, its first live proof
    2   12:53:30  m1_preview            in             M M1: resolved; the runner stopped (below)
    3   12:54:26  m1_preview            in             M M1: resolved, 1st degree, one Message
    4   12:54:48  m1_confirm            in             REFUSED at condition 5: no composer in 3 s
    5   12:57:17  m1_preview            in             the approved retry: resolved again
    6   12:57:45  m1_confirm            in             REFUSED at condition 6
    7   12:59:23  in_me                 in             D-1 (Resources, once); the Me menu; P K1
    8   13:01:37  m1_capture_profile    in             the composer captured; nothing typed
    9   13:02:59  m43                   messaging      M M43; C8, C9 and C5; C1's unread row
    10  13:04:05  setting               mypreferences  the switch by its live label: OFF
    11  13:05:21  presence              messaging      M M53: 17 cards, 16 people
    12  13:05:43  n179                  search         search 1 of 5: N 179
    13  13:06:14  notifications         notifications  N 20, N 45: neither kind drawn
    14  13:07:28  j107_worldwide        jobs           J 107 with 'Worldwide': 7 postings
    15  13:08:35  j107_default          jobs           J 107 with no location: 7 postings
    16  13:09:26  n194                  search         search 2 of 5: N 194

By surface: in 8, messaging 2, search 2, jobs 2, mypreferences 1,
notifications 1. The closest two loads stood 21.7 s apart (3 and 4). Loads 1
to 6, 8 and 14 to 16 were made by the lane's outward runner, a disposable
script in its scratch folder that took the harness's ledger, counter and
driver lock by import; the others by the harness. Every load is in the ledger.

### 2a: the named read, PROVEN live

`linkedin_read_named_profile` on the operator's supplied link and nothing
else. The preview loaded nothing and minted a token; the confirm made one load
through the named-person door. It landed on the named profile, the identity
was confirmed (1 top card, 1 heading, matching the page's title), and it
returned one people record, marked untrusted, with a headline drawn. The
returned name carries the spelling at key position 6 as a whole word, and its
last word is the family initial -- checked in the process, and only positions
and booleans left it. **This is the first live proof of the read he ruled YES
on**: lane L5's tool, over the reader it rebuilt on this lane's tracked
skeleton of the same page.

From the SAME load, with no scroll and no press, a skeleton and these counts:
0 group links, and 0 "Groups" and 0 "Interests" drawn (`N 178`, C-P7: this
first render shows no groups; whether a scroll draws them is not measured); 0
"People also viewed" and 1 "People you may know" (`N 103`); 1
mutual-connections phrase (`N 31`); 41 member links. The controls in main,
page-wide, as session 2 counted them, are unchanged: Message 2 exactly the
word, 4 with a name, 5 visible; More 2, 1 visible; Follow 4 with a name; 0
Connect, Pending or Following. The tool's own top-card reading: one visible
Message control, the owner's, and none foreign.

### 2b: M M1, refused twice by its gate; nothing typed

* **12:53, load 2.** The preview resolved the named person, but the lane's
  runner read the person from `who_this_would_reach`, where this route
  returns it as `whom_this_resolves_to`. The runner found none and stopped
  before confirming: fail-closed, one load spent for nothing. The runner now
  reads either field.
* **12:54, loads 3 and 4.** The preview resolved him -- key position 6, the
  family initial, 1st degree, exactly one visible Message control in the top
  card and it is his, none foreign; the control is a link whose address is of
  the compose kind. The confirm reloaded the profile, pressed that control
  once, and waited the tool's 3 s for a composer. None was drawn (0 bubbles,
  0 editors), still on the profile: **REFUSED at condition 5**
  (`5_not_one_conversation`). Nothing typed: `text_was_entered` and
  `left_in_the_composer` both read no, and `performed` no.
* **12:57, loads 5 and 6: the one retry the orchestrator approved at 12:57.**
  The composer wait -- which the code calls a liveness bound, not a safety
  one -- was raised to 12 s in the runner's process, never in the package. The
  composer was drawn in 1.5 s, still on the profile: ONE bubble holding ONE
  empty editor, ONE disabled Send and ONE RECIPIENT BOX, with 0 conversation
  titles. **REFUSED at condition 6** (`6_not_their_conversation`); condition
  7, a recipient box, refuses the same shape next. Nothing typed.

So for a first contact -- no conversation with him was found: session 2's two
reads of the list drew none, and the press opened none (DERIVED) -- LinkedIn's
Message press opens a NEW-MESSAGE composer, and the gate, built for a
conversation headed by his name, refuses it by design. A skeleton of the page
after that press did not contain the composer: the overlay the gate counted
through Playwright's locators is invisible to `document.querySelectorAll` and
to `page.content()`, as a shadow root is (the link carries an interop
parameter; DERIVED, not inspected).

**THE COMPOSER, CAPTURED: 13:01, load 8, on the orchestrator's approval of
12:59.** One reload through the named-person door, and the tool's own gates
first -- identity confirmed, exactly one visible Message control that is the
owner's, none foreign, no composer already open -- then one press. The
composer was drawn in 2.0 s. Its bubble was read through a SHADOW-PIERCING
locator and written as a skeleton to gitignored state, with no raw copy
anywhere. The four answers, taken in the process as booleans and positions:

    (a) a recipient box is drawn, and a committed pill sits in it    yes
    (b) the pill's text carries the spelling at key position 6,
        with the family initial last                                 yes
    (c) the pill carries an id or urn                                no: nothing to compare.
        The profile's own member id was found, in the pressed link's address.
    (d) pills                                                        1, in the box

The pill is a dismissable pill button whose label has the shape of a
remove-this-recipient label carrying the name. The bubble also draws attach
image and attach file ("for your draft conversation", in LinkedIn's words),
GIF and emoji, a disabled Send and a send-mode toggle. **NOTHING WAS TYPED.**
The close did not confirm. The bubble has no control labelled Close by
attribute (its header's two controls carry their labels as text, which a
skeleton shapes), so Escape was pressed, and after it 1 bubble, 1 editor and
1 dialog were still drawn. Closing our tab at the end of the run removed the
page and the bubble with it. **Whether an empty new-message composer leaves a
draft is NOT MEASURED:** the next messaging load (13:02:59) lists
conversations with no draft field, and a skeleton shapes a draft row's label.
Nothing had been typed into it.

The capture went to lane L5 through the orchestrator (its addendum of 13:03),
as the ground for a FIRST-CONTACT path in which every link of the chain
refuses on doubt: the caller-supplied link and a confirmed top card; the
pressed control's member id equal to the profile's; exactly one bubble and one
committed pill, whose text equals the top-card name, whole-word; only then
type and send; afterwards a conversation headed by that name, as the receipt;
and the header's close control, found by its visible text. The tracked copy:
`tests/fixtures/live3/m1_composer_bubble.html`.

**2c, `M M17`: NOT FIRED.** It replies in the thread `M M1` would make. `M M1`
and `M M17` go to session 4 on L5's first-contact path.

### D-1: Resources, pressed once

His profile at 12:59, the window fronted first: 44 `[aria-expanded]` controls
in main (session 2's fronted load: 44). The top card drew More 1, visible 0,
and Resources 1, visible 1 -- fix 3's finding, live. On the orchestrator's
ruling, Resources was pressed ONCE. Its menu held 5 items, read by attribute:
exactly 1 is Save to PDF, found by comparison inside the page, and its
attribute handle was found; 0 items match any of `N 76`'s four needles (copy
link, follow link, share profile, personal link). Of our words the menu added
Activity, Save to PDF and Send profile in a message. Nothing inside was
pressed, and it closed on Escape. `P C8` does not move: the item's own press
starts a download, which is neither sanctioned nor built.

The Me menu rode the same load: 8 of our words added, closed on Escape. `P K1`:
7 controls in main labelled with a verification (6 in session 2), none
linking to either refused address.

### C8, C9 and C5: each opened and closed on Escape

On `M M43`'s load at 13:02:59, which read 20 conversations listed (10
rendered, 10 placeholders), 0 opened, 0 message events and 1 unread row:

* **C8, the folder menu:** 4 items (Focused, Other, Archived, Spam), all
  buttons; 0 message events; **closed on Escape**. Session 2's failure to
  close did not recur, so fix 4's trigger step was not needed, and it stays
  proven offline only.
* **C9, one READ row's options menu:** 9 items, 8 of role button and 1 of role
  link with no address -- Move to Other, one item not among our words, Mark as
  unread, Star, Mute, Archive, Report / Block, Delete conversation, Manage
  settings. 0 message events; closed on Escape; nothing inside was pressed.
* **C5, the GIF picker:** opened; no menu container and none of our words
  drawn; closed on Escape.

Each open state is a tracked copy (`compose_c8-open.html`,
`compose_c9-open.html`, `compose_c5-open.html`). The rows they feed -- `M M7`,
`M M8`, `M M9` and `M M28`; `M M22`, `M M27`, `M M29` and `M M31`; `M M16` --
carry a dated capture note. No state moves on a capture.

### The setting: read by its live label, OFF (fix 2, live)

13:04, one load. Served at its own address (`SERVED, exact`); exactly one
control named "Share key profile updates", an input, reading OFF -- the live
`checked` PROPERTY 0 and the attribute 0 -- and the offline replay of the raw
capture AGREES. Read only, never pressed. So condition 1 of the six intro
edits and `P B9` reads OFF. The orchestrator ruled at 13:06 that those edits
are its call, not his, and go in the session-4 plan: read the current value,
set a harmless test value, verify that it saved, RESTORE the original, and
verify the restore -- one field at a time, the setting re-read OFF just
before each. Not this session. The raw capture stays in gitignored state; its
tracked copy is `tests/fixtures/live3/setting.html`.

### The rows the budget allowed

* **`M M53`, BANKED.** `linkedin_messaging_presence`, one load: 17 suggestion
  cards seen and 17 read; 16 people returned as records with their presence
  (reachable 10, offline 4, online 2); 1 group conversation skipped; 0
  unparsed. Session 2's load drew no card.
* **`N 179`, CAPTURED.** The events vertical, search 1 of 5: served exactly,
  38 anchors, all classified, 0 member links.
* **`N 20` and `N 45`, FIRED A THIRD TIME, NOT SHOWN.** 10 notifications, 6
  unread when read, 0 of the invitation kind and 0 of the follow kind.
* **`M M33` and `M M49`, HELD AGAIN.** The composer's list drew the one unread
  row again.

### J 107: the default location narrows (D-4)

On the orchestrator's D-4 yes of 13:06, two keyword-less searches at the
organisation cleared under D-4, a minute apart:

    13:07  location 'Worldwide'  7 postings; the query carried 'Worldwide'
    13:08  no location           7 postings; the page's one location box held
                                 another value, neither empty nor 'Worldwide'
                                 (read in the process, never printed)

The two sets share **0** ids, and the no-location set shares **all 7** with
session 2's no-location search of 08:35. So LinkedIn applies a default
location to a keyword-less employer search, and the location moved the set,
not the hour (DERIVED from the three sets; the two no-location searches, five
hours apart, are the control). Every posting at one employer is
`linkedin_search_jobs(keywords="", company_id=<id>, location="Worldwide")`,
which the tool accepts today; its docstring should say so (for its owner,
lane S). Each page drew 7 postings, one page's hydration and not the
employer's total. The row banks on its own bar.

**D1'S CAP, AND THE JOBS SEARCHES.** The ruling
(`_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`, section "D1:
search keywords and facets") reads: *"A live session makes at most 5 test
searches, because people searches count against the account's monthly
limit."* The harness counts a load against the five by its address, a
`/search/` load (surface "search"). The two J 107 searches loaded
`/jobs/search/` (surface "jobs") and were not counted, as session 2's four
jobs loads were not: the rule's stated reason, read as its scope, since a jobs
search is not a people search. Read strictly instead -- every search a test
search -- the session made 4 (`N 179`, `N 194` and the two J 107 searches),
inside the five either way.

### N 194: the #hiring people search, banked

`linkedin_people_search_shape(keywords="#hiring", include_names=True)`, search
2 of 5. `ok`; it landed on the people search, where it was sent; the keyword
kept `verbatim`; 11 person results; the filter panel settled (3 polls, 93
controls first and last); 0 values refused; 10 people records from 10 of 10
cards, 0 skipped and 0 headlines unread. Every term of lane S's bank rule
held. Which of them manage hiring stays the caller's judgement from the
headlines.

### D-4, as the order asks it recorded

The organisation used for `J 107` is the one `job_detail` resolved in session
2, **cleared by the orchestrator against his resume's current and past
employers**. Its name and id live in gitignored state only.

### Chrome's end: still up; fix 1 proven live on its normal path

At 13:09, after the last run, port 9224 was listening, owned by the process
the orchestrator had started at 12:40, and Chrome held exactly 1 page -- a
blank tab -- and no LinkedIn tab. Twelve runs made loads, 8 through the
outward runner, each reporting `closed` (another page was open, so ours
closed normally), and 4 through the harness, whose teardown does not print its
word; the attach check made none. Chrome survived every one. **Fix 1's normal
path is proven live. Its keeper path -- ours the last tab -- did not arise,
and stays proven offline only.**

### The census moves, and the pins

**CORRECTS:** `_audit/_census/jobs.md` -- row `107` read COVERED-UNFIRED, its default-location question open after session 2; it fired live in session 3 on its own cell's bar, the question settled, and moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/network.md` -- row `194` read COVERED-UNFIRED, never fired; it fired live in session 3 on lane S's whole bank rule and moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `M53` read COVERED-UNFIRED, its session-2 fire drawing no card; it fired live in session 3, the composer drawing 17 cards, and moves to COVERED-PROVEN.

**THREE ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar its cell set                        what session 3 read
    J 107   whether the default location narrows a      a default in the box; 0 ids shared
              keyword-less employer search              with 'Worldwide', 7 of 7 with session 2
    N 194   ok, landed, kept verbatim, person results   verbatim; 11; settled; 0 refused;
              >= 1, panel settled, 0 values refused     10 records
    M M53   the composer draws its suggestion cards     17 cards read, 16 people with presence

**NOT BANKED, EACH CELL SAYING WHY:** `M M1` (refused twice by its gate),
`M M17` (no thread), `N 20` and `N 45` (not shown, a third time), `M M33` and
`M M49` (held). **A DATED NOTE, NO STATE:** `N 76` and `P C8` (D-1), `P K1`,
`N 31`, `N 103`, and the six intro edits and `P B9` (the setting).
**CAPTURED, A NOTE POINTING AT ITS TRACKED COPY:** `N 178`, `N 179`, and the
C8, C9 and C5 rows above.

**THE COUNTS**, file-wide by `scripts/count_census_states.py`, each slice's
delta written into its own count section:

    slice         COVERED-PROVEN   COVERED-UNFIRED
    jobs             22 -> 23          3 -> 2
    network          15 -> 16         13 -> 12
    messaging         8 -> 9          10 -> 9
    profile          25 -> 25          8 -> 8
    all four         70 -> 73         34 -> 31      GAP unmoved

**THE PINS, MEASURED ON THE FINAL TREE AND RE-PINNED, NEVER SUMMED:**
`scripts/census_completion.py --check` named three figures and three bucket-1
rows off their pins, and nothing else:

    delivered_strict    91 -> 94
    unfired             37 -> 34
    b1_no_ruling        18 -> 15
    PINNED_B1_ROWS      NO_RULING loses J 107, M M53 and N 194

Two test pins moved with their rows: `tests/test_the_offline_frontier_rows.py`
(`J 107` and `M M53` now open on their session-3 banking, the frontier's move
after it) and `tests/test_people_search_readers.py` (`N 194` COVERED-PROVEN,
opening on its banking). The derived views were regenerated with `--write`
twice and `--check`.

### The tracked copies, and a ledger label (`23a9124`)

14 files under `tests/fixtures/live3/`, 2.0 MB: the session's 13 skeletons and
his settings page, each written by `--export-fixtures` (every keyed shape one
`x`, ids as `k` and 8 hex, strict ASCII). The fixture tests now count each
session's directory, and a directory nobody counted fails. The same change
fixes a label: a new ledger was headed "live-lane-session-2" whatever its
directory, a constant the per-session directory of `ed858fe` never reached,
so session 3's ledger carries the old name (nothing reads it). A new ledger
now names its directory, with a test shown red first. The identity gate
examined its 16 files, 0 hits; the shape guard and the fixture people guard on
the result: 1097 passed.

### To session 4

* `M M1`, then `M M17` in the thread it makes, on lane L5's first-contact
  path; `M M10` still needs an older thread.
* The six intro edits and `P B9`, by the orchestrator's pattern above.
* `M M33` and `M M49` while the unread row stands: each would spend a load
  and bank nothing.
* `N 20` and `N 45`, when the notifications draw either kind.
* `J 121` and `J 122`: not on this session's list, and no ruling holds them.
  Session 2's posting load already returned `applicant_insights` -- a
  heading, 2 metrics, 4 seniority entries and 4 education entries -- to
  gitignored state. Whether that meets either row's bar is not judged here:
  `J 122`'s levels are drawn and its top skills are not, and `J 121`'s
  percentile would be one of the two metrics, whose labels a reduced envelope
  shapes. One posting load, read against each bar.
* `N 85` and `N 172`: each takes a member he names as its argument, and none
  was ruled for this session.
* Fix 1's keeper path and fix 4's trigger step, the first time either arises
  live; and the harness's teardown should print `close_tab`'s word, as the
  outward runner does, so the keeper path can be seen when it does.
* The event, school and thread items he supplies (D-9); the father and the
  two others.

### Scratch, declared disposable

In the lane's scratch folder, none of it tracked: the session-3 outward runner
and its self-check, the census, delta and pin editors, the JSON printers that
print only numbers and closed words, the condition matcher, and the
window-fronting scripts. The outward runner took the harness's ledger, counter
and driver lock by import, so nothing loaded uncounted.

### Gates on the final tree, run and NOT run

**THE IMPACT GATE**, `scripts/impact_gate.py --against 5564c15`, in the
background, offline, sharded by the gate itself (`-n auto --dist loadfile`),
started once lane L5's full suite on the same box had ended. The diff reaches
144 of 283 test files, so it widened to the full suite at the gate's 45% line:

    tree       result
    2a47949    PASS over the full suite, 12246 tests, in 18 min 33 s

**THE CENSUS INSTRUMENTS AND THE THREE `--check`s**, on the same tree, by exit
code: `census_completion.py --check`, `check_read_addresses.py`,
`check_write_classes.py`, `ruling_holds.py`, `pin_census_rows.py --check`,
`measure_pointer_graph.py --check`, `check_jobs_directions.py`,
`check_gap_rows_on_refused_addresses.py`, `check_cited_shas_resolve.py`,
`check_contingent_writeoffs_carry_a_reopener.py`,
`check_census_locators_resolve.py` and the three generators' `--check` all
exit 0. `check_asserted_names_resolve.py` exits 1 on the same eight findings
as session 2's, all pinned in other waves' documents and none in this one.

**THE NAVIGATION GUARD WITH CI SET**, whose whole-tree complement is the one
skip in every local run: `tests/test_navigation_is_never_derived.py`, 683
passed, none skipped.

**THE IDENTITY GATE:** the pre-commit exact-value gate on both commits of this
wrap-up, 0 hits each against 226 spellings (16 files, then 10); the shape
guard, `tests/test_no_committed_identity.py`, inside the full-suite run, and
again on this section's commit.

**NOT RUN, named:**

* **CI**: nothing pushed, by order. Every number here is this box's Python
  3.13; the 3.10 cell is CI's.
* **Anything live after 13:09.** Fix 1's keeper path, fix 4's trigger step,
  `M M1` and `M M17` wait for session 4, as listed above.
* **The observed read map** the impact gate consults was recorded at
  `5c910e4`, not at this tree; the gate widened to the full suite, so nothing
  here rested on it.

## Live session 4, 2026-09-28

The orchestrator's GO of 17:05 IST, LIVE SESSION 4, under the operator's
standing instruction ("establish everything yourself, and ask him nothing").
The session ran from 17:33 to 17:44 on the Chrome the orchestrator had started
on port 9224 at 12:40 -- the same instance as session 3 -- which this lane
never started, restarted or closed. **10 of the 40 loads, 0 of the 5 searches.
NOTHING WAS SENT AND NOTHING CHANGED ON HIS PROFILE: two write attempts, and
neither landed. Three rows moved to GAP on the orchestrator's ruling, and
Chrome was still up at the end.**

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key; every step below names them by
role, and a key POSITION, where one is given, is 0-based, as the orchestrator
counts.

### The go

**CI FIRST.** The order held the session until CI on master `0e1040b` (lane
L5's first-contact path) was green, checked by the full sha: run 36416346909,
all 20 jobs passed, at 17:13. The branch then fast-forwarded to it. The
gitignored skeleton of the first-degree profile in `_state/live2/` was renamed
to the neutral name master's tracked copy now carries, so that a re-export
cannot write the old name back; its re-export is byte-equal to master's
`tests/fixtures/live2/first_degree_profile.html` (174925 bytes). The harness
tests, the navigation guard, `tests/test_first_contact_message.py` and
`tests/test_named_profile_live_skeleton.py`: 883 passed, 1 skipped (the
navigation guard's whole-tree complement, which runs where CI is set).

**THE ATTACH CHECK: CONFOUNDED ONCE, THEN PASS.** At 17:19 it read FAIL-FOLDER,
0 loads: the library's artifact folders in the OS temp directory counted
2456, 2461 and 2459 before, during and after, where a pass needs the last to
equal the first. Lane S's impact gate was running a full suite on the same box
from 17:15, 8 workers, and at 17:20 six Playwright drivers that were not this
lane's were alive and two new artifact folders appeared: the count takes every
process's folders, so the reading proves nothing either way (DERIVED). On a
quiet box at 17:33 it read PASS: 2455, 2456 and 2455, the download behaviour set
and reset in order, both answered, the reset reading restored. Making the count
HERMETIC -- the attach run's own temp directory -- is the orchestrator's
offline item after this section.

### The session, load by load

    n   time      key (the ledger's)    surface        what it read
    1   17:33:36  m1_preview            in             M M1: the brother resolved, 1st degree
    2   17:34:04  m1_confirm            in             M M1: typed, NOT SENT (below)
    3   17:35:43  edit_read             in             his intro editor, read; the plan
    4   17:36:44  B9_test_preview       in             P B9's test write: the preview
    5   17:37:08  B9_test_confirm       mypreferences  his sharing setting, read by the tool
    6   17:37:30  B9_test_confirm       in             the editor: REFUSED before any press
    7   17:41:52  notifications         notifications  N 20, N 45: neither kind drawn
    8   17:42:46  c8                    messaging      C8 pressed once; closed on Escape
    9   17:43:10  editor_capture        in             the editor's dialog timed; a skeleton
    10  17:43:39  j121                  jobs           J 121, J 122: re-measured

By surface: in 6, and mypreferences, notifications, messaging and jobs 1 each.
The closest two loads stood 22.3 s apart. Loads 1 to 6 and 8 to 10 were made by
the lane's outward runner, which took the harness's ledger, counter and driver
lock by import, and load 7 by the harness. The ledger heads itself "live4" --
the label fix of `23a9124`, the first ledger to carry it.

### 2a: M M1 on the first-contact path -- typed, NOT SENT

The preview resolved the brother from the link he supplied: key position 6,
the family initial, 1st degree. The confirm pressed the owner's one visible
Message control once, and the composer was drawn in 1.3 s. **LANE L5'S
FIRST-CONTACT GATE PASSED EVERY LINK OF ITS CHAIN:** one bubble, titled as a
new message; one recipient box, holding one committed recipient whose name is
the profile's, compared in the page; the search field empty; the recipient card
linking his profile; the pressed link naming his member; Send inside the
bubble. **His words were then TYPED -- 65 of 65 characters, exact -- and the
send gate REFUSED at `4_fill_not_landed`:** Send read DISABLED the moment after
the fill. **Send was never pressed**: the receipt counts one click, the Message
press, and `submit_was_pressed` false. Nothing reached him. The tool's own
verdict is `unknown`, because its words were left in the composer; its runner
then closed its own tab, which takes the bubble off the page.

**THE CAUSE, FOR LANE L5 (DERIVED from two captures):** a skeleton of the bubble
taken through the piercing locator about a second after the refusal, with no
load and no press, draws Send with NO disabled attribute, where session 3's
capture of the same empty composer draws it disabled. LinkedIn enabled Send a
moment after the fill, and the gate read it first: a race. Lane L5's post-fill
wait for Send is the fix, in flight. The bubble's header also draws exactly one
control whose text starts "Close", which is what L5's close step aims at.
**NOT MEASURED:** whether LinkedIn keeps the unsent words as a draft; if it
does, the next Message press reopens the composer holding them and the gate
refuses at `8_not_empty`.

**NO THIRD ATTEMPT**, by the order and by the tool's own word on `unknown`.
**2b, `M M17`: NOT FIRED** -- no thread exists. The census keeps `M M1`
COVERED-UNFIRED with the fire in its cell (the orchestrator's ruling of 17:48);
it re-fires in session 5. The bubble's tracked copy:
`tests/fixtures/live4/m1_refused_bubble_0.html`.

### 3: the edits -- read, planned, refused once before any press, then stopped

**THE EDITOR, READ ONCE (load 3)**, into gitignored state only, with a benign
test value chosen per row -- benign even if a restore failed -- or the row
skipped with its reason, as the orchestrator ratified at 17:22:

    row    field             live reading                     plan
    P B9   the Premium badge on                               test off, restore on
    P A21  Education         ONE entry of his, and the        test: the unset option
                             unset option                     (no school in the intro)
    P A19  Pronouns          SET                              test: unset them
    P A8   Additional name   empty                            skipped: any value would be
                                                              a statement he has not made
    P A11  Country / Region  an input with aria-autocomplete  skipped: see below
    P A13  City              an input with aria-autocomplete  skipped
    P A17  Industry          an input with aria-autocomplete  skipped

Each option the two selects would use is one whose text is exactly what the
tool's `select_option(label=...)` matches, so each original could be put back
exactly. The three autocomplete fields store the ENTRY picked from LinkedIn's
list; the one tool, `linkedin_update_profile_field`, types text only, so neither
a benign test value nor an exact restore can be made through it (measured live
on the attribute; what LinkedIn would store from typed text is not measured).

**P B9's TEST WRITE WAS REFUSED BEFORE ANY PRESS.** The preview (load 4), then
the confirm read his sharing setting (load 5) and loaded the editor (load 6),
and returned `write_attempt_blocked`. Its message is shaped in the receipt, so
each refusal `writes.perform` can build on that path was built the same way and
its keyed shape compared: exactly one matches -- "the Premium badge switch was
not aimed because the intro editor's dialog -- the one holding the one Save
control -- was not found exactly once. Nothing was pressed." (`0_editor_not_found`).
No verification load followed, as a refusal before the press predicts. The
lane's runner stopped the edits on that error by its own rule, and the
orchestrator ruled at 17:43: stop for the session.

**THE RACE:** the tool reads the dialog the moment the editor's address loads.
The read of load 3 waited 3 s and found the badge aimable; load 9, read only,
found the dialog ALREADY drawn when the navigation returned. So the race is
intermittent, and the refusal cannot say whether it saw 0 dialogs or 2. **WHY
NO RUNNER-SIDE WAIT:** the orchestrator chose (b) over a wait added in this
lane's runner, because the edits are writes to his public profile: proven
through a patch the package lacks, they would be fired again once the package
carried its own wait -- two rounds of writes for one proof. The package gets the
bounded wait (the next section's item), and session 5 fires `P B9`, `P A21`
and `P A19` once, through the package as shipped.

**AND A RULING CORRECTED ITSELF:** at 17:22 the orchestrator ruled the skipped
rows filed GAP; at 17:48, on the census's own definition (GAP is "no tool and no
such passage"), it corrected that for `P A8`, which has a working tool and lacks
only a benign value: `A8` stays COVERED-UNFIRED with the reason in its cell. The
three autocomplete rows go to GAP -- the one tool cannot make their change.

### Step 5: the notifications and C8

* **`N 20` and `N 45`, A FOURTH READING, NOT SHOWN:** 9 notifications, 5 unread
  when read, 0 of the invitation kind and 0 of the follow kind.
* **C8, ALONE, FOR FIX 4'S TRIGGER STEP:** the folder pill found as exactly one
  match and pressed once by the harness's own `press_and_read`: 4 items, 0
  message events, and it CLOSED ON ESCAPE again, so the trigger step was not
  needed and stays proven offline only. C9 and C5 were not pressed. The open
  menu: `tests/fixtures/live4/compose_c8-open.html`.

### J 121 and J 122: re-measured, and a correction to this record

**A CORRECTION TO THIS RECORD'S OWN "To session 4" LIST** (the session-3
section): it put `J 121` and `J 122` there as "one posting load, read against
each bar", and said `J 121`'s percentile "would be one of the two metrics".
Both cells already recorded a fire on 2026-09-20 over 11 postings, DELIBERATELY
NOT BANKED: the metrics are applicant counts, `J 121`'s percentile lives behind
the gated Show Premium Insights control, which the reader does not open, and
`J 122`'s top-skills half has no key in the reader. The list should have said
so. With the budget comfortable, the orchestrator allowed the one
load anyway, as a re-measurement: the same posting session 2 read, at the
organisation cleared under D-4. `applicant_insights` holds heading, metrics (2),
seniority (4) and education (4); 0 percentile, rank, skill or "top" words; the
gated control is drawn. Unchanged, and neither row banks.

### Chrome's end

At 17:44, after the last run, port 9224 was listening, owned by the process the
orchestrator started at 12:40, and Chrome's DevTools target list -- read over
HTTP, nothing attached -- held exactly 1 page, a blank tab, and 0 LinkedIn tabs.
The outward runner's six runs each reported its tab `closed` -- another page
being open -- and the harness's one loading run closes through the same rule
without printing its word. Fix 1's keeper path still did not arise.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/profile.md` -- rows `A11`, `A13` and `A17` read COVERED-UNFIRED, a tool that would not refuse; session 4 measured each field an input carrying `aria-autocomplete`, which the one tool can only type into, and each moves to GAP on the orchestrator's ruling.

**THREE ROWS MOVED, COVERED-UNFIRED TO GAP**, each with its paragraph first in its
cell and a line in `_audit/_census/write-classes.tsv` (R3, queued on a way to
pick an entry from the list). **A DATED NOTE, NO STATE:** `M M1`, `M M17`,
`P B9`, `P A21`, `P A19`, `P A8`, `N 20`, `N 45`, `J 121`, `J 122`, and the C8
rows `M M7`, `M M8`, `M M9`, `M M28`.

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice      COVERED-UNFIRED   GAP
    profile       8 -> 5         186 -> 189
    all four     31 -> 28        588 -> 591

**THE PINS, MEASURED ON THE FINAL TREE AND RE-PINNED, NEVER SUMMED:**
`scripts/census_completion.py --check` named seven figures and three bucket-1
rows off their pins, and nothing else:

    adjudicated        182 -> 179
    delivered_broad    128 -> 125
    gap                588 -> 591
    gap_write          378 -> 381
    unfired             34 -> 31
    b1_no_ruling        15 -> 12
    b1_released          7 -> 4
    PINNED_B1_ROWS     NO_RULING loses P A11, P A13 and P A17

`check_write_classes.py` named the three new write-direction GAP rows as
unclassed until their lines were added, then read GREEN. The derived views were
regenerated with `--write` twice and `--check`.

### The tracked copies

4 files under `tests/fixtures/live4/`, written by `--export-fixtures`: the refused
bubble, the open C8 menu, the notifications, and his intro editor -- the source
the offline wait's builder is ordered to build from. No settings page was read
raw this session. The fixture tests count the new directory.

### To session 5

* `P B9`, `P A21` and `P A19`, once, by the ratified pattern, after the editor
  path's own wait lands; `P A8` while it is empty, never.
* `M M1`, then `M M17`, after lane L5's post-fill Send wait; the gate refuses at
  `8_not_empty` if LinkedIn kept a draft. `M M10` still needs an older thread.
* `M M33` and `M M49` while the unread row stands; `N 20` and `N 45` when the
  notifications draw either kind; fix 4's trigger step and fix 1's keeper path
  the first time either arises.

### Scratch, declared disposable

In the lane's scratch folder, none of it tracked: the session-4 outward runner
and its offline self-check, the refusal matcher (keyed-shape comparison), the
page-target counter, the census, delta, pin and write-class editors, and the
CI waiter. The runner took the harness's ledger, counter and driver lock by
import, so nothing loaded uncounted.

## After session 4, offline: the editor's wait, the autocomplete refusal, the hermetic attach check

The orchestrator's two offline items, ordered at 17:22 (the attach check) and
17:43 (the editor), the second widened at 17:48 by the autocomplete refusal.
The edit rows themselves fire in session 5, once, through the package as it now
ships.

### The editor waits for its dialog (`be665f8`)

**THE DEFECT, AS MEASURED LIVE** (section "Live session 4", above): P B9's test
write read the intro editor's dialog the moment the address loaded and refused
`0_editor_not_found`, and a later load found the dialog drawn at the landing.
The fresh-render verification reads the same way, so a clean save could come
back `unknown`.

**THE WAIT:** `profile_editor.wait_for_editor_dialog`. It polls 50 times, 200 ms
apart -- 10 s -- until exactly one dialog holding the one Save control is drawn,
and returns what it saw: drawn, the polls taken, the last count; a reading that
fails is `None`, never "not drawn". **IT DECIDES NOTHING.** `writes.perform`
takes it for an editor write after the landing and before the gate reads the
control, and the fresh-render verification takes it after its load and before
it reads the value; a dialog never drawn, or drawn twice, still refuses exactly
as it did. The receipt carries it as `editor_dialog_wait`.

**THE AUTOCOMPLETE REFUSAL:** the gate refuses, before anything is typed, a field
whose control carries `aria-autocomplete` (other than `none`), a combobox role
or a `list` attribute -- counted in the page on the one control its id names.
His Country/Region, City and Industry carry the first (measured live); what
LinkedIn stores for them is the entry picked from its list, and this write types
text. The tool's docstring says both.

**RED FIRST:** `tests/test_the_editor_waits_for_its_dialog.py`, 15 tests. On the
unrepaired module 12 failed, each for the live reason: the badge write refused
"the intro editor's dialog ... was not found exactly once", the field write found
no Save anchor, the late verification read `unknown` over a value that WAS
stored, and all four autocomplete marks were TYPED AND SAVED. The three that
passed were the builder's own checks and the `aria-autocomplete="none"` control.
All 15 pass now; the controls -- a dialog never drawn, two editors -- still
refuse, with nothing pressed and nothing saved.

**THE WORLD:** `tests/fixtures/synthetic/intro_editor_late.html`, built by
`scripts/_build_intro_editor_late_fixture.py`, its digest pinned. The builder
holds the editor's one dialog in a template and has the page's own script draw
it `data-late-ms` after the load. Its structure is the synthetic switch fixture
(session 1's capture), because today's tracked copy reduced the labels and test
ids the readers aim by; today's capture is its PRECONDITION -- the builder
refuses unless `tests/fixtures/live4/editor.html` draws exactly one dialog
holding Save. It does: 5 dialogs, 1 holding Save. His profile without the editor
open (`tests/fixtures/live3/in_me.html`) draws 4 and 0, which the precondition
refuses. The reader-leak baseline gained exactly one line, the new reader clean.

**AND A DEFECT IN THE TEST, CAUGHT BEFORE CI (`5427f24`):** the digest was taken
over the file's bytes, and a Windows checkout with `core.autocrlf` writes CRLF,
so CI's Windows cells would have failed it. It is taken over the text now; a
CRLF copy of the fixture reads the same digest, where its bytes would not.

### The attach check is hermetic (`3656648`)

Built by a child of this lane in a worktree of its own, reviewed here, and
cherry-picked: the child's commit `40b1453` is nowhere on `master` and never
will be, its change landing as `3656648`. The attach child now runs with
TMP, TEMP and TMPDIR naming a fresh, empty directory under the session's
gitignored state (`attach_tmp`), and both of the parent's counts are taken
there: the only artifacts folder it can hold is its own child's driver's. The
child counts only when its own temp directory IS that directory, and reports no
count otherwise, which the unchanged rule reads as FAIL-FOLDER. Emptying the
directory refuses anything not strictly under the session's state, once both
are resolved -- a `..` or a junction leading out included -- before anything is
deleted. `attach_verdict` is unchanged.

**RED FIRST**, with a stand-in child and no browser: on the old code a foreign
folder planted in the (moved) system temp while the stand-in ran read
FAIL-FOLDER `[0, 2, 1]` -- the shape of the live `[2456, 2461, 2459]` -- and on
the new code PASS `[0, 1, 0]`; the control, a child that leaves its own folder
behind, reads FAIL-FOLDER `[0, 1, 1]`. Each guard was removed in turn and shown
to be what its tests catch; removing the handover turned the control into a
FALSE PASS, which is why the child-side rule exists. Gates in its worktree: the
harness file 143 passed; the seven script guards 987 passed, 1 skipped, and that
one passed with `CI=1`. **NOT RUN LIVE:** that the driver makes its folder there
is read off the driver's source; session 5's first attach check is the first
live use, and it should read `[0, 1, 0]`.

**A HAZARD, FOUND BY THAT CHILD:** the first child, cut from a master that did
not contain this branch's base, stopped as its brief said and returned clean;
its worktree was then removed, and when it was resumed with a reset order it
came back INSIDE this lane's worktree -- and refused the order, which would have
reset this lane's tree. A worktree child that returned clean is spawned fresh,
never resumed with a git order.

### The census

`P B9`, `P A21` and `P A19` carry a dated note that the wait landed, and `P A11`,
`P A13` and `P A17` that the refusal did; their write-class lines say so too. No
state moved.

### Gates, run and NOT run

    commits              gate                                   result
    be665f8 + 5427f24    the impact gate against ef58580,       PASS over the full suite,
                         widened to the full suite              12373 tests, 31 min 39 s
                         (219 of 286 files)                     (a shared box)
    40b1453 (as 3656648) the harness file; the seven script     143 passed; 987 passed,
                         guards; the CI-only one with CI=1      1 skipped; 1 passed

The pre-commit identity gate read 0 hits on each commit. **NOT RUN:** CI
(nothing pushed); anything live. The integration of master and its gate
follow.

### Scratch, declared disposable

The child's red-run and mutant scripts and their outputs, the builder's staged
drafts, and the census and record editors, in the lane's scratch folder.

### The integration of master `c2825a4` (`bf7a903`)

Master had moved to `c2825a4`: lane S's people-search items (the network facet,
`N 81`, `N 25` and `N 26`) and lane L5's answer to session 4's refusal (the wait
for Send after the fill, and the draft rule). CI on it was green, checked by the
full sha, before the merge. **Two conflicts, each resolved at its cause:**

* **`M M1`'s cell** in `_audit/_census/messaging-and-content.md`: this branch had
  appended session 4's fire and lane L5 its answer to it. Both notes are kept, in
  time order -- the fire, then L5's note.
* **The pins** in `scripts/census_completion.py`: master's side was taken and
  measured again on the merged tree. `--check` named seven figures and three
  bucket-1 rows, all of them this branch's three GAP rows and nothing else:

      adjudicated        187 -> 184
      delivered_broad    133 -> 130
      gap                584 -> 587
      gap_write          378 -> 381
      unfired             39 -> 36
      b1_no_ruling        20 -> 17
      b1_released          7 -> 4
      PINNED_B1_ROWS     NO_RULING loses P A11, P A13 and P A17

`writes.py` -- this branch's editor path and L5's send path -- merged without a
conflict. The derived views were regenerated to a fixed point. **THE GATE:** the
impact gate against `c2825a4` widened to the full suite (226 of 287 files) and
PASSED, 12475 tests in 31 min 44 s, on a box a second full suite shared. The
census instruments exit 0 but the asserted-names check, on the same eight
findings in other waves' documents.

## Live session 5, 2026-09-28

The orchestrator's GO of 21:00 IST, LIVE SESSION 5, under the operator's
standing instruction. The session ran from 21:03 to 21:15 on the Chrome the
orchestrator had started on port 9224 at 12:40 -- the instance of sessions 3
and 4 -- which this lane never started, restarted or closed. **23 of the 40
loads, 0 of the 5 searches. `M M1` SENT AND VERIFIED -- the first outward act
of this server proven live -- and `P B9` PROVEN BOTH WAYS, after ONE RESTORE
FAILED and the ordered recovery restored it. `M M17` was typed and not sent.
Chrome was still up at the end.**

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key; every step below names them by
role, and a key POSITION, where one is given, is 0-based.

### The go

The branch was master: `1db8992`, pushed by the orchestrator, CI green (run
36442529675, checked by its sha before the first load). Chrome's port was owned
by the session's process, and no other test suite ran on the box. The harness
tests, `tests/test_first_contact_message.py` and
`tests/test_the_editor_waits_for_its_dialog.py`: 217 passed. **THE ATTACH
CHECK: PASS `[0, 1, 0]`** -- the hermetic count's first live use, the triple
the fix predicted: one artifacts folder, the child's own, appeared in its own
directory during the attach and was gone after.

### The session, load by load

    n   time      key (the ledger's)    surface        what it read
    1   21:03:47  m1_preview            in             M M1: the brother resolved, 1st degree
    2   21:04:15  m1_confirm            in             M M1: SENT, verified
    3   21:04:52  m17_resolve           messaging      the list: 1 row carries a spelling
    4   21:05:13  m17_open_by_click     messaging      the thread, opened by its row
    5   21:05:41  m17_preview           messaging      M M17: the brother resolved
    6   21:06:10  m17_confirm           messaging      M M17: typed, NOT SENT
    7   21:06:39  m17_confirm           messaging      the reply's fresh-load verification
    8   21:07:22  edit_read             in             his intro editor, read; the plan
    9   21:07:50  B9_test_preview       in             P B9 on -> off: the preview
    10  21:08:12  B9_test_confirm       mypreferences  his sharing setting: OFF
    11  21:08:34  B9_test_confirm       in             the editor: one press, Save
    12  21:09:03  B9_test_confirm       in             the fresh render: off. SAVED
    13  21:09:33  B9_restore_preview    in             P B9 off -> on: the preview
    14  21:09:55  B9_restore_confirm    mypreferences  his sharing setting: OFF
    15  21:10:24  B9_restore_confirm    in             one press; the switch did not move
    16  21:10:58  B9_restore_confirm    in             the fresh render: off. NOT RESTORED
    17  21:11:28  reread_B9             in             the re-read ordered: off
    18  21:12:02  notifications         notifications  N 20, N 45: neither kind drawn
    19  21:12:55  B9_recovery_preview   in             the ordered recovery: the preview
    20  21:13:22  B9_recovery_confirm   mypreferences  his sharing setting: OFF
    21  21:13:54  B9_recovery_confirm   in             one press; the switch moved; Save
    22  21:14:23  B9_recovery_confirm   in             the fresh render: on. RESTORED
    23  21:14:52  reread_B9             in             confirmed: on, Open Profile on

By surface: in 14, messaging 5, mypreferences 3, notifications 1. The closest
two loads stood 20.2 s apart. Loads 1 to 17 and 19 to 23 were made by the lane's
outward runner, which took the harness's ledger, counter and driver lock by
import, and load 18 by the harness.

### 2a: M M1 -- SENT, verified

The preview resolved the brother from the link he supplied: key position 6, the
family initial, 1st degree. The confirm pressed the owner's one visible Message
control; the new-message composer was drawn in 1.4 s, and **every link of lane
L5's first-contact chain held**: one bubble titled as a new message, one
recipient box holding one committed recipient whose name is the profile's
(compared in the page), the search field empty, the recipient card linking his
profile, the pressed link naming his member, Send inside the bubble. **The
composer opened EMPTY** -- session 4's unsent words were not kept as a draft,
which settles that section's open question -- so the draft rule did not apply
and his words were typed: 65 of 65 characters, exact. **Send turned on in
228 ms** (L5's wait, `send_enabled_wait`), the last-moment check held, and Send
was pressed. His words were drawn as the new conversation's message in 1.4 s,
the close gate found the bubble's one "Close" header control and pressed it
(three clicks in all: Message, Send, Close), and **the verification read
`message_sent`.**

### 2b: M M17 -- typed, NOT SENT

The thread was resolved as ordered: the receipt-safe list drew 10 rows, 0
unread, and exactly one carries a spelling -- at the top, one-to-one, read: the
conversation `M M1` had just made. It was opened by its row (a navigation
counted by hand) and its header carries the spelling. The reply preview
resolved the brother. The confirm typed his words and U+1F44D -- 67 of 67
characters, exact -- and **the reply's send gate refused at
`4_fill_not_landed`**: Send read disabled straight after the fill. **Send was
never pressed** (0 clicks). It is session 4's `M M1` race on the REPLY path:
`threads.reply_send_gate` reads Send the moment the fill lands, and lane L5's
wait was built for the first-contact path only. The tool's verdict is `unknown`,
its words having been left in the reply box; its fresh reload of the thread
found no reply sent. **NOT MEASURED:** whether LinkedIn keeps those words as a
draft of that conversation's reply. No retry, by the order; lane L5 is building
the reply path's wait, and `M M17` re-fires in session 6.

### 3: the edits -- P B9 proven both ways, one restore failing first

**THE READ (load 8)** gave the plan of session 4: `P B9` on, `P A21` the unset
option then its one entry, `P A19` unset then its pronouns; the pronouns'
visibility control read All LinkedIn members, recorded to be compared after
`A19`. Each write read his sharing setting OFF first, and the editor's dialog
was drawn at the first poll of the package's new wait every time.

**P B9, on -> off (loads 9-12): SAVED.** One press; straight after it the badge
read off and Open Profile on -- the badge alone moved -- so Save was pressed, the
editor closed, and the fresh render read the badge off, Open Profile on.

**P B9, off -> on (loads 13-16): THE RESTORE FAILED.** One press, no click
error, and straight after it the badge STILL read off (`the_badge_did_not_move`),
so the tool -- as designed -- did not press Save, and the fresh render read
`value_unchanged`: off. **His Premium badge was left HIDDEN**, the value ruled
benign should a restore fail. The runner's STOP-ALL marker refused every later
edit; the re-read the order requires (load 17) read the badge off, shape
`{L3D0n3:7bc10cea}`, the original on, `{L2D0n2:cb21795d}`, and Open Profile on;
the orchestrator was told at once.

**THE RECOVERY, on the orchestrator's order of 21:13 (loads 19-22): RESTORED.**
One restore through the tool as shipped: the same press, about two minutes after
the one that failed, flipped the switch -- badge on, Open Profile on, straight
after it -- Save was pressed, the editor closed, and the fresh render read on.
**One read-only load (23) confirmed it: the badge on, Open Profile on.** The
order's step (b), a wait built in-session, was not needed live.

**WHAT THE FAILURE MEASURED:** the same off -> on press, minutes apart, first did
not flip the switch in the in-dialog read taken straight after it, and then did.
The press-then-read is intermittent -- the class of today's Send race -- and a
bounded wait after the press, for the control to reach the requested state, is
the orchestrator's offline item (below).

**P A21 AND P A19: HELD** by the orchestrator at 21:16 for session 6 -- the select
path's press-then-read is the same class of race, and a failed restore there
would leave a visible change (his school hidden, his pronouns unset). The
STOP-ALL marker holds them until the wait lands.

### 4: the rows the budget allowed, and what did not arise

* **`N 20` and `N 45`, A FIFTH READING, NOT SHOWN:** 9 notifications, 1 unread when
  read, 0 of either kind.
* **`M M33` and `M M49`:** the list read 0 unread rows for the first time, but
  neither was fired -- the orchestrator's order put them after the edits, and the
  session ended on the recovery. Session 6 may fire them.
* **Fix 1's keeper path and fix 4's trigger step** did not arise (C8 was not
  pressed).

### Chrome's end

At 21:15 port 9224 was listening, owned by the process the orchestrator started
at 12:40, and Chrome's DevTools target list -- read over HTTP, nothing attached
-- held exactly 1 page, a blank tab, and 0 LinkedIn tabs.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `M1` read COVERED-UNFIRED, refused or not sent at every earlier fire; it was sent on the first-contact path in session 5 and verified, and moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/profile.md` -- row `B9` read COVERED-UNFIRED, its session-4 test refused before any press; in session 5 both directions were measured -- one restore failing before the recovery held -- and it moves to COVERED-PROVEN.

**TWO ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar                                   what session 5 read
    M M1    the message sent to the person he named   message_sent, on the first-contact
                                                      chain, every link held
    P B9    the badge shown and hidden, verified      on -> off saved; off -> on saved
              on a fresh render, only it moving         at the second attempt; confirmed

**A DATED NOTE, NO STATE:** `M M17`, `N 20`, `N 45`, `P A21`, `P A19`.

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice         COVERED-PROVEN   COVERED-UNFIRED
    messaging        9 -> 10          9 -> 8
    profile         25 -> 26          5 -> 4

**THE PINS, MEASURED AND RE-PINNED, NEVER SUMMED:** `--check` named five figures
and two bucket-1 rows, and nothing else:

    delivered_strict    94 -> 96
    unfired             36 -> 34
    b1_standing         19 -> 18
    b1_no_ruling        17 -> 16
    b1_released          4 -> 3
    PINNED_B1_ROWS      OPERATOR-NAMES-THE-TARGET loses M M1; NO_RULING loses P B9

One tracked copy, `tests/fixtures/live5/notifications.html`; the fixture tests
count the new directory.

### To session 6

* `M M17`, after lane L5's reply-path Send wait; `M M10` still needs an older
  thread.
* `P A21` and `P A19`, once each, after the bounded wait after the press lands;
  `A19`'s pronoun visibility compared before and after.
* `M M33` and `M M49`, the unread row having gone; `N 20` and `N 45`.
* Fix 1's keeper path and fix 4's trigger step, the first time either arises.

### Scratch, declared disposable

The session-5 runner and its self-check, the census, delta and pin editors, in
the lane's scratch folder. Nothing loaded uncounted.

## After session 5, offline: the wait after the press

The orchestrator's item of 21:16: a bounded liveness wait after the press, for
the SWITCH path and the SELECT path, for the control to reach the requested
state, deciding nothing, with Save still conditional on exactly that field
having moved; red first on a late switch and a late select; fixtures from
today's captures, digests pinned. `P A21` and `P A19` fire in session 6 on it.

### The wait, and the rule on the select path (`c3b2393`)

**THE WAIT:** `profile_editor.wait_for_state` calls the reader it is handed, 25
times at most, 200 ms apart -- 5 s -- until the reading reaches the requested
state, and returns the last reading with whether it did and the polls taken. It
decides nothing: each path asks its own question of the last reading.

* **The switch path** waits for the badge to read the requested state, then asks
  `badge_moved_alone` exactly as before -- the badge, and only the badge, moved --
  and presses Save only on its yes. The receipt carries the wait as
  `switch_press.waited_for_the_requested_state`.
* **The select path** reads EVERY field's value before the choice, waits for the
  chosen field to read the requested option, and asks for Save only if
  `profile_editor.only_the_field_moved` holds: exactly one control named for the
  field reads the requested value, and every other value-bearing control reads,
  as a multiset, what it read before. Until now the select path pressed Save
  straight after the choice and asked nothing of the field. The receipt carries
  both as `field_press`.

**RED FIRST:** `tests/test_an_editor_press_is_waited_for.py`, 12 tests. On the
unrepaired module 9 failed: a switch flipping 1.2 s late read
`the_badge_did_not_move` in both directions -- off -> on is today's live failure
exactly -- and stored nothing; a select applying its choice late was saved over
the OLD option; a choice that also rewrote the City field was SAVED, the second
field stored beside the one asked for; and the new functions did not exist. All 12
pass now. **THE CONTROLS:** a switch that never flips and a select that never
updates still store nothing, and a select that applies at once is saved at the
first poll. The fixture's own self-test failed once under a concurrent suite
with its first 800 ms delay -- the read "straight after the press" landed after
it -- and the committed delays are 2500 ms.

**THE WORLD:** `tests/fixtures/synthetic/intro_editor_late_press.html`, built by
`scripts/_build_intro_editor_late_press_fixture.py`, its digest pinned over its
text. The switch row is the synthetic switch fixture's (session 1's capture),
with the badge's title on its block as the badge tests place it; the two selects
are shaped as TODAY's capture draws them -- the builder refuses unless
`tests/fixtures/live4/editor.html` draws a 5-option and a 2-option select, each
opening on one unset option, and two switch inputs (it does). The lateness is one
appended script: a switch press flips `switch_ms` later, and a select's change is
undone at once and applied `select_ms` later. The write tests make the badge and
editor worlds of the existing suites late with the builder's own function.

**THE LEAK GUARD:** the select path's reading, `writes._editor_values_or_refusal`,
is the values reader returned whole, so it is driven over the same editor and
ADMITTED as that reader is; the wait itself is recorded not driven (called with
the page alone it has no reader), as fifteen other functions that raise are.

**THE FILL PATH IS NOT CHANGED:** a typed field (`P A8` alone, and it is not
tested) presses Save after its fill as before; the order named the switch and
select paths.

### The census

`P A21` and `P A19` carry a dated note that the wait landed, `P B9` that its path
waits too. No state moved.

### Gates, run and NOT run

The editor and write-path suites on `c3b2393`: 581 passed; the reader-leak guard:
653 passed. The pre-commit identity gate read 0 hits on each commit. The
integration of master and the full gate follow.

### Scratch, declared disposable

The late-press debugging script, the census and record editors, in the lane's
scratch folder.

## Live session 6, 2026-09-28

The orchestrator's GO of 22:36 IST, LIVE SESSION 6, under the operator's
standing instruction; its addendum of about 22:50; and its SPEND BRAKE of
22:57, on the operator's words at 22:55 ("I don't want any new lanes at the
moment"). The session ran from 22:43 to 22:58 on the Chrome of sessions 3 to 5,
which this lane never started, restarted or closed. **29 of the 40 loads, 0 of
the 5 searches. `M M17` SENT AND VERIFIED; `P A21` and `P A19` each TESTED AND
RESTORED EXACTLY; `M M33` and `M M49` fired behind the badge reading 0. Five
rows banked. Chrome was still up at the end.**

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
They live only in the gitignored identity key; every step below names them by
role, and a key POSITION, where one is given, is 0-based.

### The go

The fill-path follow-up (`76817ca`) was committed and gated before the GO landed
(the full suite, 12517 tests). Master `675c7a0` -- the orchestrator's merge of
this lane's session-5 wrap-up onto lane L5's reply-path Send wait and reply draft
rule -- was CI-green by its sha, and was merged into the branch without a
conflict (`d621582`): the tree was master plus the one gated commit. The harness
tests, `tests/test_reply_send_wait_and_draft.py`,
`tests/test_an_editor_press_is_waited_for.py` and the first-contact tests: 237
passed. **THE ATTACH CHECK: PASS `[0, 1, 0]`.**

### The session, load by load

    n   time      key (the ledger's)    surface        what it read
    1   22:43:40  m17_resolve           messaging      the list: 1 row carries a spelling
    2   22:44:00  m17_open_by_click     messaging      the thread, opened by its row
    3   22:44:28  m17_preview           messaging      M M17: the brother resolved
    4   22:44:56  m17_confirm           messaging      typed; Send on in 221 ms; pressed
    5   22:45:25  m17_confirm           messaging      the fresh load: reply_sent
    6   22:46:02  edit_read             in             his intro editor, read; the plan
    7-10          A21_test_*            in, mypref.    Education -> unset: SAVED
    11-14         A21_restore_*         in, mypref.    Education -> the original: SAVED
    15-18         A19_test_*            in, mypref.    Pronouns -> unset: SAVED
    19-22         A19_restore_*         in, mypref.    Pronouns -> the original: SAVED
    23  22:53:46  reread_A19            in             the pronouns and their visibility
    24  22:54:09  m33_badge             feed           the badge: 0
    25  22:54:39  m33                   messaging      the composer's list: 0 unread
    26  22:55:08  m33                   messaging      /messaging/, the starred pill
    27  22:55:52  m49_badge             feed           the badge: 0
    28  22:56:21  m49                   messaging      the composer's list: 0 unread
    29  22:56:50  m49                   messaging      /messaging/, the read indicator

(Each edit's four loads: the tool's preview of his profile, his sharing page,
the editor, and the verification's fresh render of it.) By surface: in 14,
messaging 9, mypreferences 4, feed 2. The closest two loads stood 20.2 s apart.
Every load was made by the lane's outward runner, which took the harness's
ledger, counter and driver lock by import.

### M M17 -- SENT, verified; and what LinkedIn keeps

The thread was resolved as ordered: the receipt-safe list drew 10 rows, 0
unread, and exactly one carries a spelling -- at the top, one-to-one, read. It
was opened by its row and its header carries the spelling; the reply preview
resolved the brother. **The reply box opened EMPTY** (`reply_box_empty`): LinkedIn
did NOT keep session 5's unsent reply as a draft, which settles that section's
open question, as session 5's empty composer settled session 4's -- two
measurements, both "not kept". So the draft rule did not apply and his words
and U+1F44D were typed, 67 of 67 characters, exact. **Send turned on in 221 ms** -- lane L5's
reply-path wait, the race session 5 lost -- the send gate held, Send was pressed,
nothing was left in the box, and **a fresh load of the thread read
`reply_sent`**: the words, the emoji among them, read back exactly as text.

### P A21 and P A19 -- each tested and restored exactly

Through the package as shipped, with the dialog's wait (`be665f8`) and the wait
after the press (`c3b2393`); his sharing setting read OFF before each of the
four writes, and the dialog was drawn at the first poll every time.

* **P A21 (Education):** the unset option SAVED -- the choice read back at the
  first poll of the press wait, no other field moved, Save pressed, the editor
  closed, the fresh render `field_changed` -- then his one entry, the exact
  original, SAVED the same way. Each write's prior value equalled the planned
  one exactly.
* **P A19 (Pronouns):** unset SAVED, then the exact original SAVED, the same
  readings. **A separate read-only load (23)** read the pronouns back as the
  original and their visibility control as it read before the edits: All
  LinkedIn members. The unset-and-restore did not reset it.

With `P B9` in session 5, the three edits ordered for session 5 are proven both
ways, each field reading its original again on a fresh render.

### M M33 and M M49 -- behind the badge reading 0

Each fire read the badge off his feed first (0 both times) and went through the
tool's own receipt guard (the composer's list, 0 unread rows both times); no
unread row was opened.

* **M M33:** `linkedin_open_messaging(message_filter="starred")` opened
  /messaging/ and ACTIVATED the starred pill -- the view moved to its filter
  state. The filtered list drew 0 conversations: none starred, or none rendered.
* **M M49:** `linkedin_open_messaging()` drew 10 conversations, 0 unread; the
  conversation LinkedIn opened drew 2 messages, and the read indicator on the
  last words he wrote read `not_drawn`, on the measured without-seen-receipt
  marker (1 such marker, 0 with one).

### Left unstarted, the operator's spend brake 22:55

On the orchestrator's brake of 22:57, these were **left unstarted -- not failed**:
the addendum's people-search proofs (`N 25`, `N 26`, `N 81`, `N 30`, `N 85`,
`N 172`, `N 31`) and its `N 178` / `N 65` capture on the brother's profile;
`N 20` / `N 45` on the notifications; C8 for fix 4's trigger step. **One fact
read for the addendum before the brake, for whoever takes it up:**
`connections_of` takes ONE member's opaque token -- the `recipient_id` that
`linkedin_connections` returns -- and refuses a profile slug; the link the
operator supplied for the brother is a profile-slug link. So the brother's
token would come from his row in `linkedin_connections`, if his row is among
the ones it draws.

**TWO CANDIDATES, NOT MOVED** (the addendum's census checks, held by the
brake): `M M10` -- `M M17` fired its tool live and it sent, but in a conversation
session 5 had made, not the older thread the row asks for; `N 155` -- `M M1` sent
to a first-degree connection through the tool that now reaches the row, and by
`D6-CAPABILITY-OVER-AFFORDANCE` it may bank on that. Each cell carries a dated
note saying so.

### Chrome's end

At 22:58 port 9224 was listening, owned by the process the orchestrator started
at 12:40, and Chrome's DevTools target list -- read over HTTP, nothing attached
-- held exactly 1 page, a blank tab, and 0 LinkedIn tabs. Every run closed its
own tab normally; fix 1's keeper path did not arise.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- rows `M17`, `M33` and `M49` read COVERED-UNFIRED, never fired or not sent; in session 6 the reply with its emoji was sent and verified, the starred pill applied and the read indicator read, and each moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/profile.md` -- rows `A21` and `A19` read COVERED-UNFIRED, held in session 5; in session 6 each was tested and restored exactly, verified on a fresh render, and moves to COVERED-PROVEN.

**FIVE ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar                                    what session 6 read
    M M17   an emoji in a message, by send_reply,      reply_sent; the emoji read back
              read back exactly                          exactly as text
    M M33   a filter pill applied, the badge at 0      the starred pill activated
    M M49   the read indicator, on the conversation    not_drawn, on the measured
              /messaging/ opens                          marker
    P A21   the choice saved and restored, verified    both saved, fresh render each
    P A19   the choice saved and restored, verified    both saved; visibility unchanged

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice         COVERED-PROVEN   COVERED-UNFIRED
    messaging       10 -> 13          8 -> 5
    profile         26 -> 28          4 -> 2

**THE PINS, MEASURED AND RE-PINNED, NEVER SUMMED:** `--check` named five figures
and five bucket-1 rows, and nothing else:

    delivered_strict     96 -> 101
    unfired              34 -> 29
    b1_standing          18 -> 17
    b1_no_ruling         16 -> 12
    b1_released           3 -> 1
    PINNED_B1_ROWS       OPERATOR-NAMES-THE-TARGET loses M M17; NO_RULING loses
                         M M33, M M49, P A21 and P A19

No skeleton was taken, so there is no tracked copy.

### Scratch, declared disposable

The session-6 runner, the census, delta and pin editors, in the lane's scratch
folder. Nothing loaded uncounted.

## Live session 7, 2026-10-10

The orchestrator's GO of 11:17 IST, LIVE SESSION 7, on the operator's words of
10:56 ("keep going on and on... Try to finish the existing pending items,
everything... go aggressively"), which the orchestrator took as YES to the two
questions of 2026-09-28 23:48: (a) unfollow, then re-follow, a company Page he
already follows; (b) react to one of the brother's posts, then remove the
reaction. It replaced the spend brake of 2026-09-28. The session ran from 11:38
to 11:49. **17 of the 40 loads, 2 of the 5 searches. `N 25`, `N 81` and `N 26`
FIRED AND BANKED; `N 155` moved on the orchestrator's call of the day. The
unfollow did NOT land and the Page stayed followed; the father's thread was not
in the list; the react's route is the blocker; `P A8` was not fired. Chrome was
still up at the end.**

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS appear nowhere in this repository.**
Every step below names them by role. No company, Page or member is named, and
a key POSITION, where one is given, is 0-based.

### The go, measured before obeying it

Between 11:18 and 11:36 every fact of the order was re-read and held: port 9224
was listened on by one process, Chrome 155, started 11:15:16, the old process of
sessions 3 to 6 gone, and the machine booted at 10:51:30; master and this
worktree were both `3c8edc2` and the tree clean, CI-green by its sha; the
repository was public; the main checkout's live-session flag stood.

**THE LANE'S SCRATCH FOLDER HAD BEEN EMPTIED** by the operating system's temp
cleanup in the twelve days: every runner and helper was gone. The runner was
rebuilt by replaying the lane's own recorded tool calls in order -- the Write of
session 4's runner, twelve Edits across the three runners, two copies, four
transforms and one helper script -- with every call that had failed at the time
skipped, and lines 560-899
were checked against a read of the file recorded on 2026-09-28: 340 of 340
equal. The window-front script and the page-target counter were recovered
verbatim from the same record. A copy of the rebuilt runner is kept in the
gitignored `_state/live7/`, on the D drive. **THE ATTACH CHECK: PASS
`[0, 1, 0]`** (11:38).

### The session, load by load

    n   time      key (the ledger's)    surface        what it read
    1   11:38:34  signin                feed           signed in; no wall; badge 0
    2   11:39:00  s1_name               search         search 1: degree F and a name
    3   11:39:22  connections           feed           the invitation badge, before: 0
    4   11:39:44  connections           mynetwork      his connections list: 9 rows
    5   11:40:06  s2_geo                search         search 2: degree F and a place
    6   11:41:15  named                 in             the named read; the C-P7 capture
    7   11:41:53  edit_read             in             his intro editor: A8 empty
    8   11:42:29  follow_read           mynetwork      Manage Pages: the first Page
    9   11:43:27  unfollow_preview      mynetwork      the unfollow's preview
    10  11:43:55  unfollow_confirm      mynetwork      the confirm: one click
    11  11:44:25  unfollow_confirm      mynetwork      the reload: still following
    12  11:45:56  refollow_preview      company        the Page root: refused, no press
    13  11:46:41  follow_check          mynetwork      the end state: following
    14  11:47:33  m10_resolve           messaging      the list: no row is his
    15  11:48:07  notifications         notifications  N 20, N 45: neither kind
    16  11:48:48  j121                  jobs           one posting: the gated control
    17  11:49:31  editor_capture        in             his editor's skeleton, for B9

By surface: mynetwork 6, in 3, feed 2, search 2, company 1, messaging 1,
notifications 1, jobs 1. The closest two loads stood 21.6 s apart. Every load
was made by the lane's outward runner or the harness, each taking the ledger,
counter and driver lock by import; the Chrome window was brought to the front
before each block that could press.

### 0: signed in

`linkedin_new_messages` off his feed raised no wall, and the harness's health
check on the page it left read no wall and 0 challenge terms. The messaging
badge read 0.

### 1: the people searches -- three rows banked; the token not found

* **Search 1 (load 2):** `linkedin_people_search_shape(network="F",
  keywords=<the spelling LinkedIn draws for the brother, key position 6>,
  include_names=True)`. `ok`, on the people search, `query_kept` `verbatim` for
  the keyword and for `network`; 5 person results and 4 people records, all 4 at
  1st degree and all 4 carrying the spelling, and **exactly one at the link the
  operator supplied, at 1st degree**; the panel settled, 0 values refused.
  **`N 25` BANKED** -- a 1st-degree connection found by name -- **and `N 81`
  BANKED**: the facet kept verbatim and every result at 1st degree, the question
  that cell left to the first fire.
* **Search 2 (load 5):** `network="F"` beside one country-level geo id, the
  first of lane S's `N 94` pair (neither his city nor his country). `query_kept`
  `verbatim` for both; 12 person results, 10 people records, all at 1st degree;
  the panel settled, 0 values refused. **`N 26` BANKED, its location half**;
  `N 81` held on this fire too (10 of 10 at 1st degree).
* **The brother's token (loads 3-4):** `connections_of` takes the
  `recipient_id` `linkedin_connections` returns, and that list drew 9 rows -- his
  newest connections, every one with a recipient id -- none at the operator's
  link, as on 2026-09-28. **No token, so `N 30`, `N 85`, `N 172` and `N 31` did
  not fire** and 2 searches were saved. The orchestrator's message of 11:41
  (after these loads) said the member id was recorded in session 5's state;
  disk disagreed -- no member token, raw or shaped, in `_state/live2` to
  `_state/live6`, and no member, recipient or urn field in session 5's receipts
  -- and the named read returns no member id. **No member id was taken from a
  page.**

### 2: the named read and the C-P7 capture -- no section drawn

`linkedin_read_named_profile` on the operator's link, under his YES of
2026-09-28 08:01: the preview loaded nothing; the confirm (load 6) landed,
confirmed the identity (a person carrying the spelling at key position 6 and
the family initial), returned `groups` ABSENT and `group_links_drawn` 0. Off the
same page, no scroll and no press, after a 3 s settle, a skeleton (gitignored)
and these counts: 0 "Interests" and 0 "Groups" words, 0 group links, 0
details/interests links, 0 tabs. **The Interests section is not on the first
render, so `N 178` and `N 65` stay GAP** (C-P7 step 5: the next step is a ruling
for a scroll or the sub-page), and the reader build the order set for after the
wrap-up does not trigger. The same render drew an Activity section with **5
links to activity items** and 1 recent-activity link -- item 5's evidence below.

### 3: `P A8` -- not fired; an empty original cannot be restored

His intro editor (load 7) read the Additional name EMPTY, as in sessions 4 to 6,
and the plan skipped it: any test value is drawn beside his name, and **the fill
path cannot write the empty original back** -- `writes._clean_target_part`
refuses an empty `value` before a token exists. The orchestrator accepted this
at 11:41 and put "a fill path that can restore an EMPTY field" on his build
list. **ONE MORE READING FROM THE SAME LOAD: `P B9`'s switch no longer reads** --
the planner answered `3_not_the_recorded_row`, `aimable` false; load 17 read it
again the same way and kept the editor's skeleton (gitignored) for the offline
diagnosis. `P B9` was proven both ways in session 5; its state does not move
here.

### 4: the follow round trip -- the unfollow did not land

* **Load 8, Manage Pages:** 20 rows drawn, `complete` false, LinkedIn's own
  total unreadable (null, as on 2026-09-03). The FIRST Page by the list's own
  order -- the target fixed by rule -- carries an 8-digit id, written to the
  gitignored state.
* **Loads 9-11, `linkedin_unfollow_company` on that id:** the preview read
  `following` on the same page and minted a token; the confirm made one click (0
  opener, 0 closer clicks) and a fresh reload read the row **still
  `following`**: `performed` false, `verified` false. Why the click did not land
  is unmeasured -- a confirmation dialog, or a press on a control not yet
  hydrated, are the candidates -- and it was not retried blind.
* **Load 12, the cross-check on a second surface:**
  `linkedin_follow_company_page`'s preview on the Page's root REFUSED before any
  press: its own control did not read as not-following, consistent with the
  follow standing. Nothing pressed, nothing written.
* **Load 13, Manage Pages again:** the target row drawn at position 1,
  `following` -- **the end state equals the start.** No STOP-ALL arose: the
  re-follow was never reached.

`N 48` / `J 104` fired, not performed; `N 47` / `J 103` not attempted; `N 46`
left, the round trip never having started. The orchestrator accepted it at
11:50 and set the fix as an offline item: wait for a confirmation dialog, press
its own confirm control by role and label, and read back, red first on a
synthetic fixture, with session 8's measurement written beside it.

### 5: the react -- the route is the blocker

The order was a reaction and its removal on one of the brother's posts, through
`M C32`'s tool, the post's id from tool arguments. **No shipped tool returns
another member's item id:** `linkedin_my_activity_items` reads his own, and the
named read returns a name and a headline; the brother's activity page is a load
no ruling covers. Nothing was improvised and nothing fired. The named read's own
load drew 5 activity-item links on its first render, so **an extension of
`linkedin_read_named_profile` returning them as declared fields is the missing
route.**

### 6: `M M10` -- not fired; no thread found

The receipt-safe list (load 14) drew 10 rows, and **0 carried either of the
father's spellings** (key positions 0 and 1); 1 row read unread and was not
opened. The item stopped there, by the order: no conversation opened, none
begun. Whether a thread with him exists beyond the 10 rows the list draws is
not measured.

### 7: `N 20` and `N 45` -- fired a sixth time, not shown

`linkedin_notifications` (load 15): 10 rows, 4 unread when read, 0 of the
invitation kind and 0 of the follow kind.

### 8: `J 121` and `J 122` -- the press gate refuses the surface

One posting (load 16), session 2's: the applicant insights again hold
education (4), seniority (4) and metrics (2), with 0 percentile, rank or skill
words, and `Show Premium Insights` drawn (2 gated controls). **The shipped
press gate, evaluated before any press (`press.evaluate`, pure), refuses the
posting surface for both sanctioned shapes -- `[aria-expanded]` and
`[aria-haspopup]` -- with `no_sensitivity_basis`**, so the control was not
pressed. Neither row moves.

### Chrome's end

At 11:49 port 9224 was listened on by the same one process, and its DevTools
target list -- read over HTTP, nothing attached -- held 2 pages: 1 blank tab,
and 1 other page that was already there at 11:36 and is not the lane's; 0
LinkedIn tabs. Every run closed its own tab. The orchestrator was told at 11:50
that the session had closed.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/network.md` -- rows `25`, `81`, `26` and `155` read COVERED-UNFIRED, never fired or held for a target; in session 7 the name search, the degree facet and the place filter each fired and banked, and `155` moved on the orchestrator's call of 2026-10-10 by D6 on `M M1`'s session-5 send, and each moves to COVERED-PROVEN.

**FOUR ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar                                    what session 7 read
    N 25    his 1st degree searched for a name,        exactly one record at the
              the match returned                         operator's link, 1st degree
    N 81    the facet kept, applied to the results     verbatim; 4 of 4, 10 of 10
                                                         at 1st degree
    N 26    his 1st degree filtered by place or        verbatim for both facets;
              employer                                   10 of 10 at 1st degree
    N 155   a message to a 1st-degree connection       M M1, session 5, sent and
                                                         verified (the call of
                                                         2026-10-10, D6)

Every other row the session touched carries a dated note and keeps its state:
`N 30`, `N 85`, `N 172`, `N 31` (no token), `N 178`, `N 65` (C-P7, no section),
`N 48`, `J 104` (fired, not performed), `N 47`, `J 103` (not attempted), `N 20`,
`N 45` (a sixth fire), `J 121`, `J 122` (the press gate), `M M10` (no thread),
`M C32` (the route), `P A8` (an empty original) and `P B9` (the switch no longer
reads).

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice         COVERED-PROVEN   COVERED-UNFIRED
    network         16 -> 20         17 -> 13

**THE PINS, MEASURED AND RE-PINNED, NEVER SUMMED:** `--check` named four
figures and four bucket-1 rows, and nothing else:

    delivered_strict    101 -> 105
    unfired              29 -> 25
    b1_standing          17 -> 16
    b1_no_ruling         12 -> 9
    PINNED_B1_ROWS       OPERATOR-NAMES-THE-TARGET loses N 155; NO_RULING loses
                         N 25, N 81 and N 26

No skeleton of this session is exported, so there is no tracked copy.

### Scratch, declared disposable

The session-7 runner (rebuilt, then extended), the replay and verification
scripts, the census, delta and pin editors, in the lane's scratch folder; the
rebuilt runner's copy in the gitignored state. Nothing loaded uncounted.

## After session 7, offline: the badge's second shape, and the unfollow's confirmation

The orchestrator's order of 2026-10-10 11:50: two offline items, red first, local gates
under two minutes in the background, and session 8's measurement written for each. No
page was loaded for either.

### 1: `P B9` -- the switch moved onto its input (`83aaab6`)

**THE DIAGNOSIS, BY STRUCTURE.** Session 7's editor skeleton (load 17, gitignored) against
session 4's: in session 4 each setting block's switch sat in a wrapper `div` carrying
`role=switch`, `aria-checked`, `aria-label` and `tabindex`, around an unnamed checkbox
`input[role=switch]`. On 2026-10-10 the wrapper carries none of those four, and the
checkbox input carries an `aria-label` itself -- one label of 21 characters (18 letters,
measured as a keyed shape and never read), the SAME on both switches, so it names
neither. The empty `label` before the input, the row's leading paragraph and its two
blocks are unchanged; the dialog's column drew one row more. Against the recorded wrapper
shape the reader matched no row: `3_not_the_recorded_row`, on both loads.

**THE FIX.** `profile_editor.SWITCH_SHAPES` names the two recorded shapes, `wrapper` and
`named_input`, told apart by attribute PRESENCE only. The badge's block is still found by
its title, compared in the page; the row must be in exactly ONE shape, both blocks alike
and nothing of the other shape in it, or it is refused; the press is aimed at the switch's
own control in that shape -- the named input, by its role -- inside the titled block. The
reading reports `switch_shape`, and `badge_moved_alone` refuses a row that changed shape
between its two readings. `only_the_field_moved`'s rule for the badge (`badge_moved_alone`)
and the wait after the press are unchanged. Seven tests in `tests/test_premium_badge.py`
were written first and run red (`3_not_the_recorded_row`), and are green: the reader on the
second shape, the first shape still named, the write moving only the badge, the restore, a
press that also moves Open Profile, a mixed row refused, a nameless input refused.

**SESSION 8's RE-PROOF, TWO LOADS, READ-ONLY, BEFORE ANY PRESS:**

1. His intro editor: `read_premium_badge` must answer aimable, `switch_shape`
   `named_input`, both states read; the badge input's box non-empty and the element at its
   centre the input or its empty label (a press can reach it); and the save gate's reading
   taken without Save (`read_save_gate(require_save=False)`), which must count 0 unnamed
   switches and read `notify_network` `not_drawn` -- the one thing a skeleton cannot say is
   whether the shared label is a notify phrase.
2. A fresh load: the same three readings, equal.

Only if both hold: the badge's test and restore by the (b) pattern (8 loads), STOP-ALL on a
failed restore.

### 2: the unfollow -- read what the press drew (`028daef`)

**THE FIX.** `writes._unfollow_confirm_gate`, read after the unfollow press and before
anything navigates: a bounded poll (a liveness bound that decides nothing) for a
confirmation dialog, or for the row's inverse-action control gone. It presses on only when
exactly one dialog is drawn and exactly one button in it is named, exactly, `Unfollow` --
a closed vocabulary of one word; the press goes through the same click call site, with no
second one. Every other button is reported by its shape, never quoted, and a press that
drew nothing at all is said so (`no_dialog_drawn`, the row's control still wearing its
prefix), for the reload to decide. The receipt carries `unfollow_confirm_gate`.
`tests/test_unfollow_confirmation.py` was written first and run red against the unfixed
path -- its confirmation world read `performed` false with one press made, the live
failure -- and its six tests are green.

**SESSION 8's MEASUREMENT, ABOUT NINE LOADS:**

1. Manage Pages (1 load): the first Page by the list's own order must still be the id
   session 7 fixed by rule; if it is not, stop and report -- no other Page is chosen.
2. The window fronted. ONE unfollow through the fixed path (preview 1, confirm 2): the
   receipt's `unfollow_confirm_gate` is the measurement of what LinkedIn draws, and the
   runner wraps the gate in its scratch copy to keep a skeleton of the page at that moment,
   before any confirm press and before the reload. Verified by the tool's reload; with
   LinkedIn's total unreadable, by the Page root's own control in the re-follow's preview.
3. `linkedin_follow_company_page` on the same id (preview 1, confirm 2), verified on
   Manage Pages. STOP-ALL and report at once if the re-follow fails.
4. Manage Pages (1 load): the row drawn, `following` -- the end state equal to the start.

### Gates

Local, targeted, in the background, none widened: `tests/test_premium_badge.py` 24
passed; the reader-leak guard with the badge drive's double updated, 665 passed, then 699
with the unfollow tests and the unfollow fixture's; the editor tests (switches, commit,
the press wait, the dialog wait) green; `tests/test_writes.py`'s unfollow tests 4 passed;
the receipt and readonly guards green. The new gate's verdict is one line of
`tests/reader_leak_baseline.json`, its success path triaged in `WHAT_WOULD_DRIVE_IT`
until session 8 captures LinkedIn's own confirmation.

## Live session 8, 2026-10-10 -- stopped before its first load

The orchestrator's GO of 13:54 IST, a short session 8: the attach and signed-in checks, then
`P B9`'s re-proof by the plan in "After session 7, offline", then the follow round trip
through the new confirmation gate. About 14:00 the orchestrator's SAFETY STOP arrived: the
operator's usage limit was reached, and no new item or press block was to start. **Session 8
made NO page load, NO search and NO press: 0 of 40.** Nothing was in flight, so there was
nothing to restore.

Measured before the stop, as the GO's facts: port 9224 was held by the same one Chrome
process, started 11:15:16; master was `b10bde8`, CI-green by its sha, and this branch was
fast-forwarded to it; the main checkout's live-session flag stood. The session-8 runner was
prepared in the lane's scratch folder, and its badge readings were run offline over the
synthetic second-shape world in a local headless Chromium -- the reader aimable in
`named_input`, the save gate read without Save naming 0 unnamed switches, and a trial click
on the badge's switch actionable -- nothing of which reached LinkedIn.

**HIS ACCOUNT IS EXACTLY AS SESSION 7 LEFT IT**: the first Page in Manage Pages still
followed (read at row 1 at 11:46), the Premium badge switch untouched since session 5's
restore, and no message sent in session 7 or 8. Session 8's items -- the badge's two
read-only loads and its test and restore, and the follow round trip -- wait for a new GO,
unchanged. The note of this is `_state/live8/session_note.json` (gitignored).

## Live session 8, re-issued, 2026-10-10

The orchestrator's GO of 14:02 IST re-issued session 8 after the safety stop was lifted.
The session ran from 14:02 to 14:20. **25 of the 40 loads, 2 of the 5 people searches
(and 1 jobs search, the recovery's). `N 48`, `J 104`, `N 46` and `J 103` FIRED AND
BANKED. The unfollow LANDED through LinkedIn's confirmation, the Page-root re-follow was
refused, a STOP-ALL was raised, and the RECOVERY ORDER of 14:10 restored the follow through
a posting: his account ended at its start state, verified at 14:11.** `P B9`'s re-proof read
the switch but found it unreachable by a click, so nothing was pressed; lane K's
twelve-load block ran as reads and gated disclosures.

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS, his Pages and his employers appear nowhere in
this repository.** Every step below names them by role.

### The go, measured before obeying it

Port 9224 was held by the same one Chrome process (started 11:15:16); master was
`fe119de` (`b10bde8` plus lane K's ledger), merged into this branch (`d519869`); the main
checkout's live-session flag stood. **THE ATTACH CHECK: PASS `[0, 1, 0]`** (14:02), and he
was signed in (load 1: no wall, 0 challenge terms, the messaging badge 0).

### The session, load by load

    n   time      key (the ledger's)        surface     what it read
    1   14:02:53  signin                    feed        signed in; the badge 0
    2   14:03:16  badge_check               in          P B9 read; a click cannot reach it
    3   14:04:16  badge_check               in          the same; where a press could land
    4   14:05:05  follow_read               mynetwork   the first Page: session 7's
    5   14:05:38  unfollow_preview          mynetwork   following; a token
    6   14:06:10  unfollow_confirm          mynetwork   the press drew a confirmation
    7   14:06:41  unfollow_confirm          mynetwork   the reload: the row gone
    8   14:07:07  refollow_preview          company     the Page root: refused, no press
    9   14:07:47  follow_check              mynetwork   the row not drawn: STOP-ALL
    10  14:10:18  recover_search            jobs        1 posting, of that Page
    11  14:10:46  recover_follow_preview    jobs        the posting: not following
    12  14:11:14  recover_follow_confirm    jobs        one press
    13  14:11:44  follow_check              mynetwork   row 1, following: RESTORED
    14  14:15:14  lk_feed                   feed        a post's control menu, gated
    15  14:15:40  lk_inme                   in          his profile, kept
    16  14:16:05  lk_search_labels          search      the label-shape reading
    17  14:16:27  lk_posting                jobs        one posting, kept
    18  14:17:08  lk_own_post               feed        his own post, kept; no press
    19  14:17:49  lk_recommended            jobs        recommendations, kept
    20  14:18:12  lk_messaging_badge        feed        the badge: 0
    21  14:18:42  lk_messaging              messaging   the receipt guard refused
    22  14:19:11  lk_keyskills              premium     the key-skills page, kept
    23  14:19:33  lk_search_first           search      his first degree, kept
    24  14:19:56  lk_thread_badge           feed        the badge: 0
    25  14:20:25  lk_thread                 messaging   the named thread's footer

By surface: mynetwork 6, feed 5, jobs 5, in 3, search 2, messaging 2, company 1, premium 1.
The closest two loads stood 21.7 s apart. The window was brought to the front before every
block that could press.

### 1: `P B9` -- the switch is read, and a click cannot reach it

Two read-only loads of his intro editor (2, 3), the plan of "After session 7, offline":

* **The fixed reader aims it:** aimable, `switch_shape` `named_input`, the badge at
  position 2, both switches on -- the same on both loads.
* **The shared label is no notify control:** the save gate read without Save counts 0
  unnamed switches and reads `notify_network` `not_drawn`.
* **A CLICK CANNOT REACH THE SWITCH:** the named input draws no box, is not visible, and a
  trial click (Playwright's actionability checks only, nothing dispatched) timed out. Load
  3 listed where a press could land, by tag, attribute names and box only: the old wrapper
  `div` (76 x 32, the role it carried in the first shape gone), a toggle container (52 x 32)
  holding the empty label, the input and a knob (28 x 28) -- each visible one
  trial-actionable.

So the (b) pattern was NOT run and nothing was pressed. The orchestrator ruled at 14:10:
the aim at the visible toggle is an offline fix after this session.

### 2: the follow round trip -- the unfollow landed, the re-follow was refused, and the recovery

* **Load 4:** the first Page by the list's own order is the one session 7 fixed by rule.
* **Loads 5-7, `linkedin_unfollow_company` through `028daef`:** the press DREW A
  CONFIRMATION -- one `alertdialog` (`data-test-modal`) drawing a Dismiss, a Cancel and
  exactly one Unfollow (the two others shaped W7 and W6 by the gate). The gate pressed the
  Unfollow through the same click call site; the reload read the row gone (`performed`
  `unknown`, LinkedIn's total unreadable). A skeleton of the page inside the gate, before
  the confirm press, is in the gitignored state. **Session 7's diagnosis is confirmed
  live: the press that did not land had drawn a confirmation nothing pressed.**
* **Load 8, `linkedin_follow_company_page` on the same id:** its preview REFUSED before any
  press -- as it had in session 7 with the Page followed, so the refusal is the gate's
  reading of this Page, not its state.
* **Load 9, Manage Pages:** the target's row not drawn among the 20 (row 1 before). **The
  end state did not equal the start: STOP-ALL**, the marker written, the orchestrator told
  at once.
* **THE RECOVERY ORDER OF 14:10, route (a), N 46's shipped route under the marker:** a
  keyword-less, Worldwide jobs search for that Page's id drew 1 posting, its employer
  matched to the Page in the process by a keyed shape of the name (load 10); the posting's
  own control read `not_following` -- a second surface showing the unfollow had landed --
  and `linkedin_follow_company` pressed it once (loads 11-12; its in-place verdict
  `unknown`, the followed-state label being unmeasured). **Load 13, Manage Pages: the
  Page's row at position 1, `following` -- the start state.** No write was made after it.

### 3: lane K's block -- reads, and disclosures where the gate permits

Every load below was a read; presses went only through `press.disclose`, where the
shipped gate permits them now. A capture moves no row: it unblocks rows for building.

    surface                      load   what was kept / pressed            rows it unblocks
    feed-menus                   14     a post's control menu PRESSED:     N 37, N 43, N 51,
                                        permitted, priced by off_state,    N 153, N 154, N 200
                                        the witness saw it disclose; the
                                        feed and the open moment kept.
                                        The search box NOT pressed: the    (N 95 waits)
                                        veto admitted 0, and the positions
                                        did not line up (40 vs 39)
    in-me-profile                15     his profile, skeleton and raw      P D25, P D26, P F1,
                                                                           P K8
    search-people-labels         16     the label-shape reading fired:     N 80, N 88, N 89,
                                        keyword verbatim, 92 controls      N 93
                                        settled, by_term read
    job-posting-panels           17     one posting, raw and skeleton      J 115, J 124
    own-post-reactions           18     his newest own post kept; NOT      none: M C33, M C35
                                        pressed -- no [aria-expanded]      wait
                                        control in main is named for the
                                        reactions menu (0 of 4)
    jobs-recommended-feedback    19     kept (a variant of the address)    J 163, if the pair
                                                                           is drawn (offline)
    messaging-guarded            20-21  the badge 0; the receipt guard     none: M M7, M M8,
                                        REFUSED on the composer's list     M M9 wait
                                        (0 rows read), so /messaging/ was
                                        not opened; the folder pill not
                                        pressed (the gate refuses)
    premium-key-skills           22     kept (a variant of the address)    P S8, if the chooser
                                                                           is drawn (offline)
    search-people-first-degree   23     network verbatim; the first        none: N 26b waits
                                        render's filter bar draws no
                                        Industry or School term
    msg-thread-footer            24-25  the named thread, behind the       M M20, M M40, M M51
                                        badge at 0: attach_image,
                                        attach_file, gif_keyboard,
                                        emoji_keyboard -- no video-meeting
                                        control in the footer

**CORRECTED** by "After session 9, offline", section 2, below: `messaging-guarded`'s "0 rows
read" was the runner's count of a field a refusal never carries, not the guard's reading -- one
conversation read unread -- and `msg-thread-footer` did not open the named thread: the footer
it read is the composer's, and `M M20`, `M M40` and `M M51` were not unblocked.

Every skeleton and raw page is in the gitignored `_state/live8/`.

### Chrome's end

At 14:20 port 9224 was held by the same process, and its DevTools target list held 1 page,
a blank tab, and 0 LinkedIn tabs. Every run closed its own tab.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/network.md` -- rows `48` and `46` read COVERED-UNFIRED, never performed; in session 8 the unfollow landed through LinkedIn's confirmation and the follow from a posting restored it, each verified, and each moves to COVERED-PROVEN.

**CORRECTS:** `_audit/_census/jobs.md` -- rows `103` and `104` read CU, never performed; in session 8 each fired its own tool live and was verified, and each moves to CP.

**FOUR ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar                                  what session 8 read
    N 48    an unfollow that landed                  the confirmation's Unfollow pressed;
                                                     the row gone; a posting not-following
    J 104   linkedin_unfollow_company performed      the same fire
    N 46    a follow from a posting                  not_following, one press; Manage
                                                     Pages: row 1, following
    J 103   linkedin_follow_company performed        the same fire

`N 47` and `P B9` carry dated notes and keep their states.

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice         proven                    unfired
    network       COVERED-PROVEN 20 -> 22   COVERED-UNFIRED 13 -> 11
    jobs          CP             21 -> 23   CU               3 -> 1

**THE PINS, MEASURED AND RE-PINNED:** `--check` named three figures and four bucket-1 rows:

    delivered_strict    105 -> 109
    unfired              25 -> 21
    b1_standing          16 -> 12
    PINNED_B1_ROWS       OPERATOR-NAMES-THE-TARGET loses J 103, J 104, N 46 and N 48

### Scratch, declared disposable

The session-8 runner (session 7's, plus the badge check, the gate capture, the recovery and
lane K's captures), the census and pin editors, in the lane's scratch folder.

## Live session 9, 2026-10-10

The orchestrator's GO of 14:42 IST: a short session, READ-ONLY -- no write and no edit, at
most 10 loads and 3 searches, at least 20 s apart. The session ran from 14:41:54 to
14:45:31. **6 of the 10 loads, 2 of the 3 searches, no write and no press. `N 30`, `N 85`,
`N 172` and `N 31` FIRED AND BANKED, read-only, at the member he named, on the member token
his named read of that member returned.** The interests details page was captured for
`N 178` and `N 65`, and `N 47`'s refusal was read; each carries a dated note and keeps its
state.

**THE OPERATOR'S NAMED LIVE-PROOF TARGETS, his Pages and his employers appear nowhere in
this repository.** Every step below names them by role.

### The go, measured before obeying it

At 14:40 port 9224 was held by the same one Chrome process (started 11:15:16); master was
`f8c7392`, already merged into this branch (`66eb699`), which holds lane NP's two handles
and its detail-page route; the main checkout's live-session flag stood. **THE ATTACH CHECK:
PASS `[0, 1, 0]`** (14:42), and he was signed in (load 1: no wall, 0 challenge terms, the
messaging badge 0).

### The session, load by load

    n   time      key (the ledger's)          surface   what it read
    1   14:42:17  signin                      feed      signed in; the badge 0
    2   14:42:40  named9                      in        the member he named; the token
    3   14:43:03  s3_of                       search    that member's connections
    4   14:43:25  s4_shared                   search    the connections the two share
    5   (below)   details9_counted_by_hand    in        the interests details page
    6   14:45:15  n47diag                     company   the Page root, read only

By surface: in 2, search 2, feed 1, company 1. The closest two stamped loads stood 22.1 s
apart. **Load 5's time is bounded, not stamped:** its run started at 14:43:46, 20.8 s after
load 4, and its receipt was written at 14:43:55; the ledger's entry for it carries the time
it was appended by hand (14:44:38). See "The harness's ledger missed a door" below. No
block could press, so none was fronted.

### 1: the named read -- the member token came back

Load 2, `linkedin_read_named_profile` on the profile link the operator supplied, through
lane NP's route: landed, identity confirmed. **The member token came back** -- 39
characters, of the closed shape the read checks -- and is kept only in the gitignored
state, never printed. `activity_items` held 2, both authored by the profile's owner: the
item keys `M C32`'s react would take, which this session did not fire.

### 2: the two searches with that token -- four rows banked

* **Load 3, `linkedin_people_search_shape(connections_of=<token>, include_names=True)`:**
  ok, landed on the people search, `query_kept` `verbatim` for `connections_of`; 10 person
  results, the panel settled (6 polls), 0 values refused; 10 people records from 10 of 10
  result cards, all 10 at 2nd degree. **`N 30`, `N 85` and `N 172` BANKED**: a member's
  connections, the Connections-of filter, and those connections as people.
* **Load 4, the same with `network="F"`:** `query_kept` `verbatim` for `connections_of`
  and for `network`; 13 person results, the panel settled (5 polls), 0 values refused; 10
  people records from 10 of 10 result cards, all 10 at 1st degree. **`N 31` BANKED**: the
  connections he and that member share.

Neither search drew a record at the named member's own link.

### 3: the interests details page -- served, and no group on its first render

Load 5, `linkedin_read_named_profile(section="interests")` (ruling
NAMED-PROFILE-DETAIL-PAGES), the same member: landed on the details page, its path
`/details/interests/` when read; `entries` absent, no reader being built yet. Its first
render drew 4 headings, 8 list items and 16 member links, and 0 group, 0 company, 0
newsletter and 0 school links, and no `role="tab"` element. **The default view is not
every tab, and no group is on it:** `N 178` and `N 65` keep GAP, with a dated note each.
The skeleton is in the gitignored state, for the reader built offline.

### 4: `N 47` -- why the gate refuses, read

Load 6, the first-by-rule Page's root, the Page followed, read through the shipped reader
and verdict of `linkedin_follow_company_page` in the runner's process; nothing pressed:

* the identity link holds: 1 link, naming exactly the id;
* the Page's own control is named, shaped, `W10 click to unfollow W9`, so it does not open
  `Follow `;
* the one control in the main column that does (10 on the page in all) is shaped
  `Follow W5 W5 W5` -- another name than the Page's -- and binds to none of the column's
  headings;
* so the verdict refuses at its binding condition, `unknown`, before any press.

**THE SIMPLE CAUSE, DERIVED:** unfollowed, as at session 8's load 8, the Page's own control
opens `Follow ` too, so the column holds two and the verdict refuses them as several --
pressing one would be picking by position. The fix is offline: among several, aim at the
one control bound to the Page's own heading.

### Chrome's end

At 14:45 port 9224 was held by the same process, and its DevTools target list held 1 page,
a blank tab, and 0 LinkedIn tabs. Every run closed its own tab.

### The harness's ledger missed a door

The harness counts a load by wrapping `BROWSER.goto`, and it counts two doors: the read
door and the named-profile door (`named_profile=True`). Lane NP's detail page enters
through a third, `named_profile_details_of=`, so load 5 passed the wrapper uncounted and
unspaced. It was counted by hand the moment its run ended, before load 6; its spacing held
only because its run started 20.8 s after load 4. The wrapper is to be fixed offline, red
first, before the next session that loads a detail page.

### The census moves, and the pins

**CORRECTS:** `_audit/_census/network.md` -- rows `30`, `85`, `172` and `31` read COVERED-UNFIRED, never fired; in session 9 each fired read-only at the member he named, on the member token his named read returned, and each moves to COVERED-PROVEN.

**FOUR ROWS MOVED, EACH ON ITS OWN CELL'S BAR:**

    row     the bar                                  what session 9 read
    N 30    a member's connections, at a member      load 3: verbatim; 10 person results;
            he names                                 settled; 0 refused; 10 records
    N 85    the Connections-of filter, on lane S's   the same fire
            whole bank rule
    N 172   those connections AS PEOPLE, under the   the same fire: 10 people records
            six mitigations
    N 31    the connections the two share            load 4: both verbatim; 13 person
                                                     results; 10 records, all 1st degree

`N 178`, `N 65` and `N 47` carry dated notes and keep their states.

**THE COUNTS**, file-wide by `scripts/count_census_states.py`:

    slice         proven                    unfired
    network       COVERED-PROVEN 22 -> 26   COVERED-UNFIRED 11 -> 7

**THE PINS, MEASURED AND RE-PINNED:** `--check` named three figures and four bucket-1 rows:

    delivered_strict    109 -> 113
    unfired              21 -> 17
    b1_no_ruling          9 -> 5
    PINNED_B1_ROWS       NO RULING loses N 30, N 31, N 85 and N 172

The tests that pin those rows moved with them, in the same commit:
`tests/test_people_search_readers.py` (`N 85`, `N 172`) and
`tests/test_shared_connections_search.py` (`N 30`, `N 31`).

### Scratch, declared disposable

The session-9 runner (session 8's, with session 9's four read phases and a read-only
gate), the census, pin and test editors, in the lane's scratch folder.

## After session 9, offline: the badge's toggle, N 47's binding, the guard re-read, the third door, and session 8's six skeletons

The orchestrator's order of 14:42 set three offline items after session 9's wrap-up,
each red first; its order of 15:43 added the harness's third door and session 8's six
skeletons as tracked fixtures. Nothing below loaded a page: every page is a fixture or a
kept skeleton in a local headless Chromium.

### 1: `P B9` -- the press lands on the drawn toggle that holds the named input (`20fc073`)

Session 8 measured why the badge could not be pressed: the named input draws no box and
is not visible, and a trial click on it timed out; its parent -- one div holding the empty
label, the input and the knob, 52 x 32 -- is drawn and trial-actionable.

* **The aim:** the reader aims the second shape's press at that toggle
  (`profile_editor._NAMED_SWITCH_TOGGLE_PATH`), found from the same block by the same named
  input. The second shape now requires exactly one toggle.
* **The box:** the reader asks whether the press target draws a box (`is_visible()`, its
  one question that is not a count), and refuses with `8_press_target_not_drawn` when it
  does not -- before any press, where session 8's aim would have spent a token on a click
  that could not land.
* **Kept, as ordered:** the press wait (`wait_for_state`) and the only-the-badge-moved
  check (`badge_moved_alone`) are unchanged; the select and fill paths'
  `only_the_field_moved` is untouched.
* **Red first:** the badge world's second shape redrawn as measured -- the input hidden,
  the toggle drawn and pressable -- turned the three named-input writes red against the
  press aimed at the input, beside three new tests (the aim at a drawn toggle holding the
  badge's input; a toggle drawing no box refused; an input no toggle holds refused):
  6 failed, 37 passed. Then 43 passed.

### 2: the receipt guard did not read 0 rows -- a correction to session 8

**CORRECTION, to this record's "Live session 8, re-issued", section 3:** its
`messaging-guarded` line says the guard refused "(0 rows read)", and its
`msg-thread-footer` line says the named thread was opened and its footer read. Both are
wrong, by the same mechanism:

* **The 0 was the runner's.** Its view counted the tool result's top-level `rows`, which
  `threads.refused_result` never carries, so every refusal printed 0. The guard's own
  reading (`receipt_guard.rows_rendered`, `unread_positions`) was neither printed nor
  kept.
* **The skeleton kept a moment later** draws 20 conversation rows, 10 rendered and 10
  placeholders, in the measured places (`main li.msg-conversation-listitem`). **Row 1
  carries LinkedIn's unread markers** -- the class tokens
  `msg-conversation-card__message-snippet--unread` and
  `msg-conversation-card__unread-count`, and a shown notification badge
  (`notification-badge--show`, `artdeco-notification-badge--new`); rows 2-10 carry none.
  It is the first capture of the unread form in LinkedIn's current markup, which
  `threads.read_conversation_list` says no capture held.
* **The shipped reader and guard over that skeleton:** 10 rendered, unread at position 1,
  refused. DERIVED: the live guard refused for the same reason -- one conversation unread
  -- which is the guard working as designed, beside a messaging badge of 0 (it counts
  new-since-last-visit).
* **The thread footer was never read.** `linkedin_open_thread` reads the composer's list
  first; the same guard refused, so the ledger counted one messaging load, not two, and
  the page left open was the composer. Its kept skeleton draws 0 conversation messages and
  0 active rows. The footer actions recorded -- attach image, attach file, the GIF and
  emoji keyboards -- are the COMPOSER's, exactly the four `threads` measured on it.
  `M M20`, `M M40` and `M M51` were not unblocked; lane K's ledger reverted them to
  CAPTURE the same hour.

Nothing in the guard changes: it refused rightly. The session runner's view of a messaging
answer now prints the guard's own counts beside the result's, and the session-8 section
carries a pointer to this correction.

### 3: `N 47` -- among several controls, the one bound to the Page's own heading (`b46736d`)

Session 9 read why the gate refuses (its section 4). The Page root is also redesigned: no
h1, the Page's name in an h2, class names generated.

* **The gate:** several `Follow `-prefixed controls in the main column are admitted only
  through the binding -- exactly one whose name is `Follow ` and a heading the Page prints,
  as the reader compares them (whitespace folded) AND as the page's own XPath engine does,
  exactly (`dom.COMPANY_PAGE_BOUND_FOLLOW_CONTROL`, a constant: nothing the page wrote is
  spliced into it). That selector is the press, still strict. If the two comparisons
  disagree, the gate refuses.
* **The prose it made stale,** corrected: the tool's docstring and the spec's direction
  source (one control in the main column), and the followed label, which session 9 read
  once as a shape and which nothing here reads.
* **Red first:** 6 failed, 39 passed -- the world with another entity's control in the
  main column refused, a padded heading pressed, the aim among several missing, and the
  end-to-end follow beside another control refused at preview. Then 45 passed; the
  end-to-end test records, through the world's own handlers, that the press landed on the
  Page's own control.

### 4: the harness's third door (`65f22e0`)

Session 9's load 5 entered through lane NP's detail-page door, `named_profile_details_of=`,
which the ledger's counted wrapper did not recognise. The wrapper now counts every door
`BROWSER.goto` has. Red first: the new test failed on the spacing; then 145 passed.

### 5: session 8's six skeletons, tracked (`ca0d0d0`)

The six skeletons lane K's ledger (section 12.7) planned, written by the harness's own
`tracked_copy` -- every keyed shape one `x`, an id reference `k` and its hash, strict
ASCII -- at the paths that plan gave them:

    tests/fixtures/live8/feed_item_menu_open.html   N 37, N 43, N 51, N 153, N 154, N 200
    tests/fixtures/live8/in_me.html                 P D25, P D26, P F1, P K8
    tests/fixtures/live8/search_labels.html         N 80, N 88, N 89, N 93
    tests/fixtures/live8/posting.html               J 115, J 124
    tests/fixtures/live8/recommended.html           J 163
    tests/fixtures/live8/keyskills.html             P S8

The identity gate over the index: 7 files, 226 spellings, 0 hits; the identity tests on the
committed tree, 2191 passed.

### Gates

Each item committed first, then its targeted tests in the background: the badge's guards,
1202 passed; N 47's, 1203 passed; the harness's, 145 passed; identity, 2191 passed. The
box was loaded by other lanes, so two of these ran past two minutes; none widened to the
suite. CI certifies the merged tree.

### Scratch, declared disposable

The red and fix editors for each item, the offline diagnoses over the kept skeletons
(`diag_messaging.py`, `diag_unread_tokens.py`, `diag_n47.py`) and the fixture copier, in
the lane's scratch folder.
