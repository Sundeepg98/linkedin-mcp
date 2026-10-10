# Lane K: the next-step ledger and the capture queue

Lane K of the capability census, briefed by the orchestrator on 2026-09-28
22:55 IST, paused before any work landed, and relaunched on 2026-10-10 from
master 3c8edc2 (CI green). Offline throughout: no page was loaded, no port
was touched, and no live capture was taken. The live lane ran a session on
the same box until about 11:51 IST; while it ran, every test run here was
targeted and serial, and after it the orchestrator's gate policy of 11:35
held: the tests touched, their direct importers and the census instruments,
with the full suite left to CI.

THE QUESTION: for every GAP row, what is the NEXT step -- and which live
captures unblock the most rows per page load? Live page loads are the scarce
resource (the operator's ruling of 2026-09-23: 40 loads a session, 20 s or
more apart, at most 5 searches, one live lane).

This document is written as the lane goes; each section says what it rests on.

## 1. Method

The population is the shipped walk, never a re-parse: every row
`scripts/census_completion.py` reads as GAP (its `walk_cells()`, which
`scripts/enumerate_gap_rows.py` and the row pin cross-check). At the base it
was 587 rows -- 91 R + 7 R+W + 381 W outside `jobs.md`, and 108 `jobs.md`
rows whose direction lives in `_audit/_census/jobs-directions.tsv` (60 W,
40 R, 8 R+W). After section 2's two exclusions it is 585.

Each row is joined to the four side tables that already hold part of the
answer:
- `_audit/_census/blocker-map.tsv` -- 327 GAP rows by blocker at the base,
  260 in no map;
- `_audit/_census/write-classes.tsv` -- 381 write rows at the base: 253
  classify-only, 128 queued on a named blocker;
- `_audit/_census/read-addresses.tsv` -- the 98 read rows outside `jobs.md`,
  each address driven through `readonly.is_read_url`;
- `_audit/_census/jobs-directions.tsv` -- the 108 `jobs.md` rows.

A row's next step is the FIRST thing that must happen before anything else
can, in this order: a ruling nobody has made; a right or object he does not
hold; a target only he can name; an address the boundary refuses; a live
capture; a build on a capture that already exists. The rulings registered in
this lane's first commit are applied as written, and the rows other lanes own
are marked as theirs.

## 2. The purchase exclusions

The ruling PURCHASES-STAY-MANUAL (the orchestrator, 2026-09-28, registered in
this lane's first commit) reads: a purchase -- Premium, InMail credits, ads,
boosts, any paid upgrade -- is not built; its row is EXCLUDED-RULED with the
reopener "he names a purchase to automate". The brief allows this lane one
kind of row move: a purchase row whose own cell meets the bar.

Every GAP row was searched for the vocabulary of a spend (purchase, buy,
paid, payment, upgrade, subscription, credit, boost, sponsor, promote,
advertise, ad, billing, checkout, price). Thirty-one rows matched a word;
two are purchases:

    row     capability                      the cell's own words
    P S9    Change the Premium plan         "changing the plan is a purchase"
    M C71   Boost a post (paid promotion)   "the only capability in this slice
                                             that costs currency"

The rest are not purchases, each for a reason on its face: an InMail send
spends a credit his Premium already includes (`M M2`, `N 156`, `N 158`), the
advertising rows are settings about ads (`P P10` to `P P14`, `P P15`), `P N22`
is the read of his subscriptions, `J 159` searches the Ad Library, `N 200`
hides an ad, and the rest match a word in passing.

Both rows move GAP -> EXCLUDED-RULED. Each cell keeps its prior text, gains
the ruling, its document and the reopener, and says the named blocker no
longer decides the state. `_audit/_census/exclusion-basis.tsv` files both
under a new family, PURCHASES-STAY-MANUAL (made by the ORCHESTRATOR, op=NO),
registered in `scripts/check_exclusion_basis.py` with the ruling's two
anchors; the table is 40 of 40, no structural problem. Both lines leave
`_audit/_census/write-classes.tsv`, whose population is write-direction GAP
rows only, and the act `purchase` leaves the closed vocabulary with its one
line, as `outside-the-classes` did.

The pins, each MEASURED on this tree by the instrument that owns it:

    census_completion.PINNED   out_of_scope 38 -> 40, achievable 733 -> 731,
                               capabilities_achievable 747 -> 745,
                               adjudicated 184 -> 186, gap 587 -> 585,
                               gap_write 381 -> 379
    write-class split          (16, 37, 336) -> (16, 37, 334), 387 lines
    messaging triage headline  131 {R 16, W 111, R+W 4} -> 130 {R 16, W 110,
                               R+W 4}
    GAP rows on refused        78, unchanged: `P S9`'s address is refused by
      addresses                allowlist silence, which that check ignores
                               by design
    blocker map                one line: `M C71`'s state today

No other figure moved: the delivered lines, bucket 1, bucket 3 and the jobs
figures read as they did.

## 3. The ledger: every GAP row's next step

`_audit/_census/next-step.tsv` holds the 585 GAP rows, each exactly once, in
the shipped walk's population. Columns: `row`, `slice`, `dir` (the census
R/W cell; for `jobs.md`, the side table's), `class` (from the write-class
table, else `-`), `next`, `basis`, `source`. It is a JUDGED table, like the
write-class table, and `scripts/check_next_step.py` (section 9) checks it on
every run. The scratch generator that wrote it is disposable; the table is
the record.

`next` is one of eight kinds, each with a payload:

    kind          rows   payload
    SIBLING        160   lane-S 114, lane-U 23, another row 23
    ADMIT          144   the address lane A must admit
    TARGET          99   what he must name
    BUILD           56   the tracked fixture (or planned skeleton) to build on
    PRECONDITION    54   what he lacks
    RULING          30   a question id, section 7
    CAPTURE         25   a surface id in the capture queue, section 5
    PURPOSE         17   the doubt, section 8
    total          585   = still-GAP in `scripts/census_completion.py`

`basis` says what the step rests on: MEASURED 73 (an instrument read it on
this tree: an address driven through `readonly.is_read_url`, or a control
counted on a tracked fixture), NAMED 241 (a committed source names it: the
row's own cell, a queue name, a capture plan, a ruling), INFERRED 271 (this
lane's judgement). `source` resolves in one of three forms: a census row id
(`N 168`), a `path::phrase` whose phrase is in the file, or `RULING:<id>`
registered in `_audit/RULINGS.md`.

By slice and by direction:

    slice  ADMIT BUILD CAPTURE PRECOND PURPOSE RULING SIBLING TARGET
    J        30     7      0      12       4      6      29      20
    M         8    19     10       8       4     10      30      41
    N        41    11     14      17       3     10      32      31
    P        65    19      1      17       6      4      69       7

    dir    ADMIT BUILD CAPTURE PRECOND PURPOSE RULING SIBLING TARGET
    R        58    24     10       8       4     19       1       7
    W        79    31     15      45      12      9     157      91
    R+W       7     1      0       1       1      2       2       1

How the brief's assignments were applied:
- Lane U (uploads): the 16 rows on FILE-UPLOAD-UNSANCTIONED, and 7 more
  whose act is an upload (`P B2`, `P B3`, `P B5`, `P G3`, `P M1`, `J 63` a
  cover-letter file, `M M19` a voice attachment), INFERRED. The brief said
  15 rows; the blocker map holds 16 at 3c8edc2 (section 4).
- Lane S (settings of his own account): the P-R itemized rows that are
  writes (`P P4` to `P P23`, less the read `P P15`), the 8
  FORBIDDEN-CLASS-FIX-LANDED rows, the 5 MESSAGING-SETTINGS rows, the
  credential and verification settings (built, never live-proven unless he
  names them), and every other row whose act is a setting or a
  notification preference -- 114 in all.
- Lane A (read admissions): every read the boundary refuses on an act's
  substring or on allowlist silence takes `ADMIT:<its measured address>`.
  So does every WRITE whose page the boundary refuses, because nothing can
  be captured or built there until the page opens: the Open To Work editor,
  the profile section editors, his recommendations, the invitation manager,
  the application settings. The reads the boundary refuses on the read
  itself (a session surface, a sign-in challenge, a GET that may start an
  application) are not lane A's: they are RULING rows.
- The 19 UNASSIGNED rows each have a step: ADMIT 8 (`J 78`, `P D24`,
  `M C82`, `N 41`, `N 42`, `N 59`, `N 60`, `N 61`), lane S 5 (`J 83`,
  `J 99`, `J 100`, `N 96`, and `J 81` with the credential set), TARGET 1
  (`J 79`), SIBLING 1 (`J 80` on `J 79`), RULING 1 (`J 82`), PRECONDITION 1
  (`J 150`), and CAPTURE 2 (`N 51`, `N 95` on the feed load).
- SIBLING to another row (23): the jobs slice's Open To Work rows ride on
  the profile slice's (`J 89` to `J 98` on `P I2` to `P I13`); duplicates
  across slices (`N 149` to `N 151` on `M M38`, `N 160` on `M M6`); steps
  inside another row's act (`N 169`, `N 187`, `J 80`, `J 85`); and five that
  a shipped tool may already reach by D6-CAPABILITY-OVER-AFFORDANCE (`N 3` on
  `N 1`, `M C11` on `M C1`, `M C65` on `M C25`, `M C91` on `M C32`, `J 86` on
  `P I14`) -- a census call for the row's owner, not made here.

Where a write needs a menu or a dialog nobody has captured, and that menu is
drawn only inside the act at an item he names (his post, his comment, a
tracked job, a connection), the step is TARGET, not RULING: the capture
rides inside the granted act, as lane L8's capture plan has it, and the
package's write path, not the disclosing-press gate, governs that press. A
READ that can only be reached through a press the gate refuses is RULING
(section 7).

## 4. What disk said that the brief did not

- SESSION 7 HAS ALREADY RUN. The brief asked for a session-7 plan first.
  The live lane's `_state/live7/` ledger records a seventh session on
  2026-10-10 from 11:32 to 11:49: 17 loads and 2 searches (keys `signin`,
  `s1_name`, `connections`, `s2_geo`, `named`, `edit_read`, `follow_read`,
  an unfollow and refollow, `m10_resolve`, `notifications`, `j121`,
  `editor_capture`), and `_state/LIVE_SESSION_ON` was gone by 11:51. So the
  first plan here is SESSION 8. Its captures `named`, `editor` and
  `notifications` exist as skeletons in the live lane's state and are not
  yet tracked; the live lane's record will say what they served. Two rows
  here lean on them and say so: `P A9`, `P A14`, `P A15`, `P A22` (the
  editor's full read), and the `N 65` / `N 103` capture, which session 7's
  `named` key may already have taken.
- FILE-UPLOAD-UNSANCTIONED holds 16 rows at 3c8edc2, not 15: `J 70`,
  `J 146` to `J 149`, `M M14`, `M M15`, `M M18`, `M C3` to `M C7`, `M C27`,
  `M C45`, `M C86`.
- The census queue names for messaging captures C5, C8 and C9 still read
  "capture" while session 3 took all three and committed their open states
  (`tests/fixtures/live3/compose_c5-open.html`, `compose_c8-open.html`,
  `compose_c9-open.html`). Five rows build on them now (section 6).
- The profile section editors (`/in/me/edit/about/`, `/in/me/edit/forms/...`),
  the contact-info editor and the Open To Work editor are all refused by the
  read boundary today; only the intro editor is admitted. Their write rows
  wait on an admission, not on a capture.

## 5. The capture queue and the session plans

`_audit/_census/capture-queue.tsv`, one line per capture surface, 93 lines.
Columns: `rank`, `surface-id`, `session`, `needs`, `address`,
`address_verdict` (today's `readonly.is_read_url`; a refused address names
the admission it waits on, or the named-profile route), `presses` (each
control and the shipped press gate's verdict on it now, from
`press.check_address`, `check_shape` and `check_basis`), `save`, `loads`,
`searches`, `rows_unblocked`, `rows_per_load`, `rows`, `captured_already`,
`plan`.

    lines   gate                                         rows
        8   none: schedulable now                           25
       11   TARGET: he names the item                       99
       65   ADMIT: lane A admits the page first            144
        9   RULING: a question in section 7                 18

The press gate, measured per line: a press is PERMITTED before the press
only on `/feed/`, on a post's permalink and on `/analytics/profile-views/`
-- the three surfaces with a declared basis -- and there the counters still
decide at the press. Everywhere else it is refused: `no_sensitivity_basis`
(not yet) on messaging, notifications, groups, events, company pages, jobs
pages and searches; `control_not_judged` (not yet) for the `[aria-expanded]`
controls on his own profile, and `control_judged_an_action` for its
`[aria-haspopup]` links; `composer_or_editor` (never by this route) on the
composers and editors; `address_not_admitted` (never) on a third party's
profile, which only the named-profile route reaches.

### SESSION 8 -- the first 40 loads, in order

Ten loads need nothing from anyone; they come first. The order is by rows
unblocked per load, except that the thread read follows the guarded
messaging loads it depends on.

    #      surface                    loads search rows
    1      feed-menus                     1    0   9  N 37, N 43, N 51,
                                                      N 153, N 154, N 200,
                                                      M C36, M C37, N 95
    2      search-people-labels           1    1   4  N 80, N 88, N 89, N 93
    3      named-profile-addendum         1    0   2  N 65, N 103
    4      own-post-reactions             1    0   2  M C33, M C35
    5      in-me-profile                  1    0   1  P K8
    6-8    messaging-guarded              3    0   3  M M7, M M8, M M9
    9      search-people-first-degree     1    1   1  N 26b
    10     msg-thread-footer              1    0   3  M M20, M M40, M M51
           subtotal                      10    2  25

Load 1 is one feed load with two presses the feed basis prices: one item's
overflow menu (the curation acts: mute, hide, unfollow, save) and the global
search box (his recent searches). Load 3 is the member he already named for
session 6's addendum, through the named-profile route; check the live
lane's session-7 record first, since its `named` key may be this load. Loads
6 to 8 are the guarded pattern the live lane uses: the badge read off his
feed, the composer's list, then `/messaging/`. Load 10 opens a conversation
he named before, behind the badge at 0.

The other 30 loads go to TARGET lines, in rank order, each as he names its
target (each distinct thing he names costs a load):

    #      surface                    loads rows  he names
    11-12  t-non-connection               2    7  a non-connection; a member
                                                  to invite with a note
    13-16  t-named-connection             4   13  1st-degree connections to
                                                  endorse, recommend, ask,
                                                  follow
    17     t-named-school                 1    3  a school Page
    18-21  t-named-event                  4   11  an event; an event to create
    22     t-block-member                 1    2  a member to block
    23-32  t-named-job                   10   20  postings, an alert, a tracked
                                                  job, a draft
    33-35  t-named-page                   3    4  Pages to invite to, report,
                                                  follow
    36-40  t-named-group                  5    6  a group, a fellow member,
                                                  a pending request
           session 8 total               40 loads, 2 searches, 91 rows

### SESSION 9 -- the next 40

    #      surface                               loads rows  gate
    1-15   t-named-post                             15   21  TARGET: his
                                                             posts, comments,
                                                             a poll, reposts
    16     t-connection-row-menu                     1    1  TARGET
    17-30  t-named-thread                           14   11  TARGET: threads
                                                             he names (2 loads
                                                             each, guarded)
    31     admit-in-me-opportunities-job-opp...      1   13  after lane A
    32     admit-in-me-details-recommendations       1   12  after lane A
    33     admit-mynetwork-invitation-manager        1   10  after lane A
    34     admit-jobs-application-settings           1    9  after lane A
    35     admit-in-me-details-featured              1    6  after lane A
    36     admit-in-me-edit-forms-position-new       1    5  after lane A
    37     admit-mynetwork                           1    5  after lane A
    38     admit-preload-guideoverlay-...-details    1    5  after lane A
    39     admit-in-me-edit-contact-info             1    4  after lane A
    40     admit-newsletters-id                      1    4  after lane A
           session 9 total                          40  106

Sessions 10 and 11 take the remaining 55 admission-gated lines (40 loads,
then 15 loads and 2 searches), each one load for one to three rows. The
nine RULING-gated lines are scheduled by nobody until their question is
answered.

THE YIELD CURVE IS STEEP AND THEN FLAT. The first ten loads unblock 25 rows
(2.5 a load); a session of named targets unblocks 91; after the admissions,
most lines are one row a load. The cheapest rows in this ledger are not
captures at all: 56 build on captures already on disk (section 6), and 160
belong to sibling lanes.

## 6. The capture inventory

Taken by a child of this lane on 2026-10-10 at 11:53, read-only, over three
stores: the tracked fixtures, the main checkout's gitignored `_state/`
(with `_state/worktree-archive/` and its MANIFEST, every byte count
matching), and the live lane's `_state/`. No `chrome-profile` directory was
entered. Paths and shapes only; no capture text is copied here.

    store       raw  skeleton  derived  non-capture  total
    tracked       0        87        8            0     95
    state        35         0        5           48     88
    archive      22         0       17          146    185
    live-lane    30        48      151            7    236
    all          87       135      181          201    604

48 distinct surfaces carry a raw, skeleton or derived capture. The ones that
hold a GAP row's surface, and the rows that can be BUILT on them now:

    surface                              best capture                                rows BUILD now
    /messaging/compose/ C9 menu open     tests/fixtures/live3/compose_c9-open.html   M M26, M M27, M M29, M M31
    /messaging/compose/ C5 picker open   tests/fixtures/live3/compose_c5-open.html   M M16
    /groups/<group>/                     tests/fixtures/live2/group_home.html        M C61, M C64, M C69, N 63,
                                                                                     N 163, N 168
    /groups/<group>/members/             tests/fixtures/live2/group_members.html     N 165, N 177
    /company/<company>/people/           tests/fixtures/live2/company_people.html    J 108, N 102
    /search/results/companies/           tests/fixtures/live2/n104.html              N 104
    /search/results/groups/              tests/fixtures/live2/n161.html              N 161
    /search/results/events/              tests/fixtures/live3/n179.html              N 179
    /mynetwork/.../followers/            tests/fixtures/live2/followers.html         P L2b
    /feed/update/<urn>/ (his post)       tests/fixtures/live2/own_post.html          M C29
    his post's control menu              tests/fixtures/synthetic/own_post_menu.html M C18, M C23, M C90
    /jobs/search/                        tests/fixtures/live2/j107.html              J 31, J 84
    /jobs/view/<job>/                    tests/fixtures/live2/job_detail.html        J 115, J 124
    /jobs-tracker/                       tests/fixtures/jobs_tracker_row.html        J 56
    /jobs/alerts/ (the jobs home)        tests/fixtures/synthetic/jobs_home_recent_searches.html  J 19
    /mynetwork/.../newsletters/          tests/fixtures/synthetic/newsletter_subscriptions.html   N 56
    /analytics/profile-views/            tests/fixtures/synthetic/profile_views_pill_open.html    N 133
    /in/<member>/edit/intro/             tests/fixtures/live4/editor.html            P A11, P A13, P A17

Where the control a row needs was counted on the fixture, the row's basis
is MEASURED: "Who can (comment)", "Edit post" and "Delete post" on his
post's menu; "Most relevant" on his post; alert and dismiss controls on the
jobs search page; "Clear" on the jobs home; "unsubscribe" on the newsletter
list; "Join" and "invite" on the group page.

Raw captures with no tracked skeleton yet. Each line below is a PLANNED
skeleton: a builder writes it from the raw capture, and the rows build on
it. `scripts/check_next_step.py` reads this block, so a BUILD step naming a
fixture that is neither tracked nor planned here fails.

    PLANNED tests/fixtures/live1/contact_info.html <- live-lane _state/l1-contact.html (P A25)
    PLANNED tests/fixtures/live1/audience.html <- live-lane _state/l1-audience.html (P L1)
    PLANNED tests/fixtures/live1/overview.html <- live-lane _state/l1-overview.html (P L8)
    PLANNED tests/fixtures/live1/articles.html <- live-lane _state/l1-articles.html (M C48)
    PLANNED tests/fixtures/live1/post_summary.html <- live-lane _state/l1-post_summary.html (M C38)
    PLANNED tests/fixtures/synthetic/sharebox.html <- _state/cap-ct-sharebox.html (M C2, M C8, M C9, M C13, M C54)
    PLANNED tests/fixtures/synthetic/own_profile_sections.html <- _state/cap-rc-badges.html (P D25, P D26, P D27, P D28, P F1, P H11, P J4, P K1)
    PLANNED tests/fixtures/live7/editor.html <- live-lane _state/live7/editor.skeleton.html (P A9, P A14, P A15, P A22)

The first five are lane L1's five pages, which session 1 captured and whose
offline readers were never written (the session record, item 8). The sixth
is the share box as captured 2026-09-20, which draws Post, Schedule and the
add controls. The seventh is his own profile as captured 2026-09-20, raw,
which answers offline whether a section renders on a passive load. The
eighth is session 7's editor capture, named here by this lane; the live
lane's record names the real path.

Other raw captures on the box that a later step can use: nine jobs-tracker
stages, an events home, a groups list and a newsletters page, all raw under
the main checkout's gitignored `_audit/` (`_probe-*.html`) -- the only raw
captures of the tracker stages that `J 50` to `J 52` read once their
addresses are admitted; the events home and the groups list again under
`_state/` (`cap-rc-events.html`, `cap-rc-groups.html`); and three group
feeds in the archive.

Found while taking the inventory, for the owners:
- `_state/session.json` holds saved browser session cookies. Only its key
  names were read.
- The live lane's `_state/live2/` to `live7/` each hold a `shape.key`, the
  keyed-hash key behind the skeleton shapes; whoever holds one can re-link
  shapes to equal strings.
- Several gitignored JSON tool outputs hold unreduced people data (the
  who-viewed-me read, notification and profile-view readings). All are
  gitignored.

## 7. Questions for the orchestrator

Each question is a RULING step in the ledger; the rows it holds are listed,
and its ground is quoted from the record.

### Q-CAPTURE-PRESS -- a read capture needs a press or typing the gate refuses

Rows (10): `J 37`, `M C14`, `M C97`, `M M28`, `M M34`, `N 86`, `N 90`, `N 91`,
`N 92`, `N 178`. Each needs a control opened, or a box typed into, on a
surface where `linkedin_server/press.py` refuses it today: messaging's
folder item and search box, the people search's All-filters control, the
composer's scheduled-posts control, a notification's menu, the jobs home's
alert manager, the Interests tab on a named profile. The gate's words:
"A press NEVER extends reach", and on these surfaces "no basis is declared
for this surface, so condition 3 has no way to be satisfied here". THE
EVIDENCE THAT A SECOND ROUTE EXISTS: session 3 opened C8, C9 and C5 on the
composer -- a surface the gate refuses for pressing as `composer_or_editor`
-- under the probe rule, and committed the open states. The question: may
a read capture press, or type, under the probe rule (stopping before any
save, send or submit, closing with Escape), or must each surface first get
its own `SENSITIVITY_BASES` or `DECIDED_REVEALS` entry, or a view-switch
entry where the press selects?

### Q-IN-ME-PIN -- an index-pinned judgement of controls on his own profile

Rows (2): `N 76` (his Follow link), `P C8` (Save to PDF). Both sit behind
his profile's overflow control. The address table: "the Open-to control, an
[aria-expanded] button, is not judged (control_not_judged) -- it shares that
shape with the same links, so only a position-pinned judgement could admit
it". The question: admit the overflow control by an index-pinned judgement
in `press.SENSITIVITY_BASES`, or keep both rows waiting?

### Q-APPLY-FLOW -- opening the Easy Apply flow may be a GET that changes state

Row: `J 82` (the daily limit and its rate-pause message). The address
table: "Opening it is the first step of an application". The class rulings
of 2026-09-28, section 5, do not reach "a GET that changes state". The
question: is opening the apply flow such a GET (the read stays refused), or
may it be admitted read-only?

### Q-SESSIONS-LIST -- the active-sessions list

Row: `P N9`, refused on `/psettings/`. The class rulings, section 5: the
read-past ruling does not reach "a credential, recovery, session or
security surface". The question: is the sessions list readable at all, or
does the row leave scope?

### Q-SIGNIN-CHALLENGE -- a sign-in challenge

Row: `P N13` (the sign-in prompt, email code or CAPTCHA, at `/checkpoint/`).
The class rulings, section 5: not reached for "a sign-in challenge". The
question: rule the row out of scope with a reopener, or keep it GAP?

### Q-POST-TEXT -- a post's text

Row: `M C43`. The address table: "FEED-CONTENT-READ-RULING (lead,
2026-09-05, registered) reads feed content as counts and relations only".
The question: does NAMES-AT-RUNTIME, with the people-data mitigations, now
reach a post's own text, or does the counts-only ruling stand?

### Q-ORG-PROSE -- an organisation Page's own prose

Row: `J 110` (the Home and Posts tabs). The address table: the prose is
"MEASURED AND NOT PUBLISHED, because a person's name can sit inside it and
nothing here can clear it". The question: publish it under the people-data
mitigations, or keep the counts reader only?

### Q-SEARCH-LABEL -- telling a people filter from a jobs badge

Row: `N 82` (the Actively hiring filter). The address table: "nothing
available tells a people filter from a jobs badge without reading the
label, which this surface forbids". The question: may this one filter be
matched by its label?

### Q-CALLER-COMPOSES -- a caller composing shipped tools, under D6

Rows (3): `J 57`, `J 131`, `N 197`. For `J 57` the address table says
"Every piece ships and the CALLER can compose it today", while a server-side
join "would navigate to ids read off the tracker page, a derived
navigation"; for `N 197`, "Whether a link composed from the group id
discharges the row is an open question under the D6 capability-over-
affordance ruling". The question: does a caller composing shipped tools
(or a link composed from an id) discharge these rows under
D6-CAPABILITY-OVER-AFFORDANCE?

### Q-GEOLOCATION -- his browser's geolocation permission

Row: `J 17`. The address table: "Whether to grant that persistent
permission is the operator's call, not a boundary or reader question". It
is the operator's, so the orchestrator relays it or rules the row by D6
(the location parameter already reaches every documented result set).

### Q-CONTACT-IMPORT -- uploading his address book

Rows (2): `N 106`, `N 108`. The cell: "the import completes on Google's
OAuth consent screen, another domain", and "Importing uploads other people's
contact data to LinkedIn, an act his to fire". The question: is an
address-book import ever built, or do both rows leave scope?

### Q-ARTICLE-AUTOSAVE -- loading the article composer

Rows (6): `M C44`, `M C46`, `M C50`, `M C78`, `M C81`, `P L3`. The press
gate: "`/article/new/` is admitted for READING and opening it may autosave a
draft **no surface here can detect**". A capture of the composer is one
load and would unblock the six; this lane does not schedule it. The
question: accept that a capture load may leave an empty draft he cannot
see, or keep the composer unloaded?

## 8. Preconditions and purposes

PRECONDITION rows stay GAP; each waits on something he does not hold.

CHEAP AND PRIVATE -- he can make it himself, and nobody else sees it:
- an event he organises, made private or unlisted: `N A13`, `N A14`, `N A15`;
- a group he owns, made private: `N A10`, `N A11`, `N A12`.

CHEAP BUT PUBLIC -- his to make, but others can see it:
- a Service Page: `P H2` to `P H10` (9);
- an article: `M C49`, `M C77`;
- a newsletter: `M C51`, `M C83`, `P L4`; two of them: `M C84`.

NOT CHEAP, or not his to make:
- admin rights on a Company Page: `N A1` to `N A5`, `N A7` to `N A9` (8);
- a Top Voice badge: `P B8`, `P K9`;
- an endorsement received: `P E6`, `N 114`;
- a pending invitation to a group or an event: `N 164`, `N 182`;
- a collaborative post or article he is part of: `M C55`, `M C56`, `M C76`;
- a job change to share: `P I16`;
- a name-pronunciation recording, which only the mobile app records: `P A23b`;
- a LinkedIn Learning certificate: `P D29`;
- the AI role-play feature, an experiment LinkedIn controls: `J 132`,
  `J 134` to `J 139` (7);
- an AI interview invitation from an employer: `J 142` to `J 145`;
- US Premium (select US subscribers): `J 150`;
- a second account to watch the network from: `P O23`.

PURPOSE rows -- this lane doubts they serve a job-search and
professional-presence tool for his own account. Nothing moves; the
orchestrator rules.

    row(s)                        the doubt
    M C99                         daily games are entertainment
    M C95                         a live video stream, nothing to read
    M C98                         LinkedIn News is general news reading
    M C96                         an image's provenance label
    J 159                         a company's ads: market research
    J 162, J 163, J 164, N 198    feedback to LinkedIn about its own product
    N 50                          a Follow button on another website
    N 152                         a Help Center safety form
    P S10, P B7, P J1, P J2, P J3 hiring: posting a job, the #Hiring frame
    P L6                          hosting an audio event, existence uncertain
