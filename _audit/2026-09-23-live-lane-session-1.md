claude-opus-5-5[1m]

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

**A DEFECT IN MY OWN COMMIT `85df223`, fixed in the next.** Entry 7 named the
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
price. It cannot tell "did not move" from "could not move", and the `/feed/`
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
(on) and "React " (off; inferred from the on form, not yet seen). The tool
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
   than whatever counter could move (Entry 12).
2. **The react write aims by the feed's label** (`dom.REACTION_OFF_LABEL`,
   `reaction_control_selector`, used on item permalinks). On his own post's
   permalink the measured toggle is "Unreact Like" (the post liked; the OFF
   form "React Like" is inferred). n=1, one liked post, but it suggests the
   write would find no control there. For lane L4.
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
