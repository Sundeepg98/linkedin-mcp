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
    ADMIT          151   the address lane A must admit
    SIBLING        149   lane-S 105, lane-U 20, another row 24
    TARGET          99   what he must name
    PRECONDITION    57   what he lacks
    BUILD           45   the tracked fixture (or planned skeleton) to build on
    RULING          42   a question id, section 7
    CAPTURE         28   a surface id in the capture queue, section 5
    PURPOSE         14   the doubt, section 8
    total          585   = still-GAP in `scripts/census_completion.py`

`basis` says what the step rests on: MEASURED 79 (an instrument read it on
this tree: an address driven through `readonly.is_read_url`, or a control
counted on a tracked fixture), NAMED 275 (a committed source names it: the
row's own cell, a queue name, a capture plan, a ruling), INFERRED 231 (this
lane's judgement). `source` resolves in one of three forms: a census row id
(`N 168`), a `path::phrase` whose phrase is in the file, or `RULING:<id>`
registered in `_audit/RULINGS.md`.

By slice and by direction:

    slice  ADMIT BUILD CAPTURE PRECOND PURPOSE RULING SIBLING TARGET
    J        32     8      3      12       2      6      29      16
    M        11    15      8       8       4     13      29      42
    N        42    12     12      17       1     12      29      34
    P        66    10      5      20       7     11      62       7

    dir    ADMIT BUILD CAPTURE PRECOND PURPOSE RULING SIBLING TARGET
    R        60    17     12      10       4     20       1       7
    W        84    28     15      46       9     20     146      91
    R+W       7     0      1       1       1      2       2       1

How the brief's assignments were applied:
- Lane U (uploads): the 16 rows on FILE-UPLOAD-UNSANCTIONED, and 4 more
  whose act is a file upload (`P B2`, `P B5`, `P G3`, and `M M19` a voice
  attachment), INFERRED. The brief said 15 rows; the blocker map holds 16 at
  3c8edc2 (section 4).
- Lane S (settings of his own account): the P-R itemized rows that are
  writes (`P P4` to `P P23`, less the read `P P15`), the 8
  FORBIDDEN-CLASS-FIX-LANDED rows, the 5 MESSAGING-SETTINGS rows, the
  credential and verification settings (built, never live-proven unless he
  names them), and every other row whose act is a setting or a
  notification preference -- 105 in all. Lane S owns them even where their
  page needs an admission first (the application settings, for `P M7`,
  `P M8`, `P M10`, `J 74` to `J 76`): the brief assigns settings writes to
  lane S by name. For lane S, from the cold review: `P N12`'s control sits
  on the sign-in form at `/uas/login`, reachable only when signed out.
- Lane A (read admissions): every read the boundary refuses on an act's
  substring or on allowlist silence takes `ADMIT:<its measured address>`.
  So does every WRITE whose page the boundary refuses and that is not a
  setting, because nothing can be captured or built there until the page
  opens: the Open To Work editor, the profile section editors, his
  recommendations, the invitation manager, his saved posts. The reads the
  boundary refuses on the read itself (a session surface, a sign-in
  challenge, a GET that may start an application) are not lane A's: they
  are RULING rows.
- The 19 UNASSIGNED rows each have a step: ADMIT 9 (`J 78`, `P D24`,
  `M C82`, `N 41`, `N 42`, `N 59`, `N 60`, `N 61`, `N 96`), lane S 3
  (`J 83`, `J 100`, and `J 81` with the credential set), SIBLING 2 (`J 80`
  on `J 79`, `J 99` on its container `P I12`), TARGET 1 (`J 79`), RULING 1
  (`J 82`), PRECONDITION 1 (`J 150`), and CAPTURE 2 (`N 51`, `N 95` on the
  feed load).
- SIBLING to another row (24): the jobs slice's Open To Work rows ride on
  the profile slice's (`J 89` to `J 98` on `P I2` to `P I13`, `J 99` on
  `P I12`); duplicates across slices (`N 149` on `M M38`, `N 160` on
  `M M6`); steps inside another row's act (`N 169`, `N 187`, `J 80`, `J 85`,
  and `M C2`, which its own cell ties to `M C12`); and six a shipped tool may
  already reach by D6-CAPABILITY-OVER-AFFORDANCE (`N 3` on `N 1`, `M C11` on
  `M C1`, `M C65` on `M C25`, `M C91` on `M C32`, `J 86` on `P I14`, `N 50` on
  `N 47`) -- a census call for the row's owner, not made here.

Where a write needs a menu or a dialog nobody has captured, and that menu is
drawn only inside the act at an item he names (his post, his comment, a
tracked job, a connection), the step is TARGET, not RULING: the capture
rides inside the granted act, as lane L8's capture plan has it, and the
package's write path, not the disclosing-press gate, governs that press. A
READ that can only be reached through a press the gate refuses is RULING
(section 7).

### 3.1 The cold review

A child that did not write the table read every row's step against the row's
own cell, the rulings and the brief's rules, and wrote 61 findings, each
quoting its evidence. This lane checked each against the tree before
adopting it: the addresses it named were driven through `readonly.is_read_url`
(eleven refused, two admitted), and the controls it counted were counted
again on the fixtures. 55 were adopted, some in a different form than
proposed; 6 were not:

    adopted                                                 rows
    a lane-S row that is a relation act, a deletion of his  N 142, J 87, N 96, P K7, P N14,
      own item, a credential step or an outward reply       P A24, P K5, M M39, M C52,
                                                            P N21, P N10, J 99
    a setting the cell names, moved INTO lane S             P D7, J 35, J 36
    an address the row's own cell names                     P I12, P I13, P S2, P H1, P D2,
                                                            P E2, P D27, M C36, M C37, P K1,
                                                            J 159, P M1
    a control a tracked fixture already holds               M C97, J 53, J 55, J 161
    a fresh load where a skeleton cannot answer             P D25, P D26, P F1, P S8, J 115,
                                                            J 124, J 163
    a precondition the cell states                          P D28, P H11
    a target inside the act, not a build on the share box   M C2, M C8, M C9, M C13, M C54,
                                                            N 150, N 151, J 63
    a question, not a build or a capture                    P A9, P D29, P B3, P S4, M C15,
                                                            M C16, M C17, N 152
    a purpose doubt the cell answers                        N 50 (D6 on N 47), J 159, J 163;
                                                            P J4 joins the hiring family

    not adopted                      why
    P M7                             a setting: the brief assigns settings writes to lane S
    J 32, N 49                       the Page's address still has to come from him
    N 99, J 112                      the school's address has to come from him; the
                                     session record plans "a school id he names"
    P N12                            a FORBIDDEN-CLASS-FIX-LANDED row, which the brief
                                     assigns to lane S; its point is passed to lane S above

The review moved 55 of 585 rows; four more followed their neighbours
(`P D26` and `P F1` onto the fresh profile load, `P E3` with `P E2`, `M C54`
with `M C8`), and the INFERRED share fell from 271 to 231. Live session 7's
record, merged from master, moved three more (section 4).

## 4. What disk said that the brief did not

- SESSION 7 HAS ALREADY RUN. The brief asked for a session-7 plan first.
  The live lane's `_state/live7/` ledger records a seventh session on
  2026-10-10 from 11:38 to 11:49: 17 loads and 2 searches, and
  `_state/LIVE_SESSION_ON` was gone by 11:51. Its record reached master
  (`1170c98`) and this branch at the merge of `53908ea`. So the first plan
  here is SESSION 8. What session 7 settled for GAP rows: C-P7 was taken on
  the member he named and drew no Interests section on the first render, so
  `N 65` and `N 178` wait on "a ruling for a scroll or the sub-page"
  (Q-PROFILE-SCROLL); `N 103` builds on that capture; its editor capture was
  taken for `P B9`, so whether it draws `P A14`, `P A15` and `P A22`'s
  unread controls is an offline read on it.
- FILE-UPLOAD-UNSANCTIONED holds 16 rows at 3c8edc2, not 15: `J 70`,
  `J 146` to `J 149`, `M M14`, `M M15`, `M M18`, `M C3` to `M C7`, `M C27`,
  `M C45`, `M C86`.
- The census queue names for messaging captures C5, C8 and C9 still read
  "capture" while session 3 took all three and committed their open states
  (`tests/fixtures/live3/compose_c5-open.html`, `compose_c8-open.html`,
  `compose_c9-open.html`). Five rows build on them now (section 6).
- The profile section editors (`/in/me/edit/forms/...`, the skills editor,
  `/in/me/edit/secondary-language/`), the contact-info editor and the Open
  To Work editor are all refused by the read boundary today; only the intro
  editor is admitted. Their write rows wait on an admission, not on a
  capture.

**CORRECTED BY:** `_audit/2026-11-25-admit26.md` -- five of those editors are
admitted since 2026-11-25 (the position, About, contact-info and
secondary-language forms and one skill's form, each in the spelling LinkedIn
draws, two of them re-addressed), and every other ADMIT step in the ledger has
moved to a capture or to a question in section 7; the Open To Work editor has
no address at all, so its rows wait on Q-OPEN-TO-WORK-EDITOR.

## 5. The capture queue and the session plans

`_audit/_census/capture-queue.tsv`, one line per capture surface, 103 lines.
Columns: `rank`, `surface-id`, `session`, `needs`, `address`,
`address_verdict` (today's `readonly.is_read_url`; a refused address names
the admission it waits on, or the named-profile route), `presses` (each
control and the shipped press gate's verdict on it now, from
`press.check_address`, `check_shape` and `check_basis`), `save`, `loads`,
`searches`, `rows_unblocked`, `rows_per_load`, `rows`, `captured_already`,
`plan`.

    lines   gate                                         rows
       10   none: schedulable now                           28
       11   TARGET: he names the item                       99
       72   ADMIT: lane A admits the page first            151
       10   RULING: a question in section 7                 23

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

Twelve loads need nothing from anyone; they come first, by rows unblocked
per load, except that the thread read follows the guarded messaging loads it
depends on.

    #      surface                    loads search rows
    1      feed-menus                     1    0   7  N 37, N 43, N 51, N 95,
                                                      N 153, N 154, N 200
    2      in-me-profile                  1    0   4  P D25, P D26, P F1, P K8
    3      search-people-labels           1    1   4  N 80, N 88, N 89, N 93
    4      job-posting-panels             1    0   2  J 115, J 124
    5      own-post-reactions             1    0   2  M C33, M C35
    6      jobs-recommended-feedback      1    0   1  J 163
    7-9    messaging-guarded              3    0   3  M M7, M M8, M M9
    10     premium-key-skills             1    0   1  P S8
    11     search-people-first-degree     1    1   1  N 26b
    12     msg-thread-footer              1    0   3  M M20, M M40, M M51
           subtotal                      12    2  28

Load 1 is one feed load with two presses the feed basis prices: one item's
overflow menu (the curation acts: mute, hide, unfollow) and the global search
box (his recent searches). Load 2 is his own profile, fresh: it records the
Add-section anchors' addresses, which the live probe deliberately never
recorded, and answers whether the strength meter and the recommendations
section render on a passive load. Load 4 is one posting from his own saved
jobs, as session 7's `j121` load took one, kept raw because a skeleton cannot
answer `J 124`. Loads 7 to 9 are the guarded pattern the live lane uses: the
badge read off his feed, the composer's list, then `/messaging/`. Load 12
opens a conversation he named before, behind the badge at 0.

The other 26 loads go to TARGET lines, in rank order, each as he names its
target (each distinct thing he names costs a load):

    #      surface                    loads rows  he names
    13-14  t-non-connection               2    7  a non-connection; a member
                                                  to invite with a note
    15-18  t-named-connection             4   13  1st-degree connections to
                                                  endorse, recommend, ask,
                                                  follow
    19     t-named-school                 1    3  a school Page
    20-23  t-named-event                  4   11  an event; an event to create
    24-32  t-named-job                    9   16  postings, an alert, a tracked
                                                  job, a draft, a multi-step
                                                  Easy Apply
    33-34  t-block-member                 2    3  a member to block; one to
                                                  unblock
    35-37  t-named-page                   3    4  Pages to invite to, report,
                                                  follow
    38     t-connection-row-menu          1    1  a connection to remove
           session 8 total               38 loads, 2 searches, 86 rows

### SESSION 9 -- the next 40

    #      surface                               loads rows  gate
    1-18   t-named-post                             18   22  TARGET: his
                                                             posts, comments,
                                                             a poll, reposts,
                                                             composer modes
    19-23  t-named-group                             5    6  TARGET
    24     admit-in-me-details-recommendations       1   12  after lane A
    25     admit-in-me-opportunities-job-opp...      1   11  after lane A
    26     admit-jobs-application-settings           1   10  after lane A
    27     admit-mynetwork-invitation-manager        1   10  after lane A
    28-40  thirteen more admission lines            13   47  after lane A
           session 9 total                          40  118

Sessions 10 and 11 take the named threads (18 loads: two each, guarded, 13
rows) and the remaining 55 admission-gated lines, each one load for one to
three rows. The ten RULING-gated lines are scheduled by nobody until their
question is answered.

These plans cover the captures GAP rows need. The live lane's own
carry-over -- the live proofs of rows already built (bucket 1) -- draws on the
same 40 loads, and the orchestrator splits the budget between the two.

THE YIELD CURVE IS STEEP AND THEN FLAT. The first twelve loads unblock 28
rows (2.3 a load); a session of named targets unblocks 86; after the
admissions, most lines are one row a load. The cheapest rows in this ledger
are not captures at all: 45 build on captures already on disk (section 6),
and 125 belong to sibling lanes.

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

The per-file table is `_audit/_census/capture-inventory.tsv`: the 403 files
that are captures (store, path, date, kind, surface, url evidence, shape),
the 201 non-capture files left out. It is a SNAPSHOT of 2026-10-10 11:53,
dated here and checked by no instrument; the live lane was writing
`_state/live7/` while it was taken.

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
    /jobs/view/<job>/                    tests/fixtures/job_detail_hydrated.html     J 161
    /jobs-tracker/                       tests/fixtures/jobs_tracker_row.html        J 53, J 55, J 56
    /jobs/alerts/ (the jobs home)        tests/fixtures/synthetic/jobs_home_recent_searches.html  J 19
    /mynetwork/.../newsletters/          tests/fixtures/synthetic/newsletter_subscriptions.html   N 56
    /notifications/                      tests/fixtures/notifications.html           M C97
    /analytics/profile-views/            tests/fixtures/synthetic/profile_views_pill_open.html    N 133
    /in/<member>/edit/intro/             tests/fixtures/live4/editor.html            P A11, P A13, P A17

Where the control a row needs was counted on the fixture, the row's basis
is MEASURED: "Who can (comment)", "Edit post" and "Delete post" on his
post's menu; "Most relevant" on his post; alert and dismiss controls on the
jobs search page; "Set alert for similar jobs" on the posting; "Archive" and
"Add note" on the tracker row; "Delete notification" on the notifications
list; "Clear" on the jobs home; "unsubscribe" on the newsletter list; "Join"
and "invite" on the group page.

Raw captures with no tracked skeleton yet. Each line below is a PLANNED
skeleton: a builder writes it from the raw capture, and the rows build on
it. `scripts/check_next_step.py` reads this block, so a BUILD step naming a
fixture that is neither tracked nor planned here fails.

    PLANNED tests/fixtures/live1/contact_info.html <- live-lane _state/l1-contact.html (P A25)
    PLANNED tests/fixtures/live1/audience.html <- live-lane _state/l1-audience.html (P L1)
    PLANNED tests/fixtures/live1/overview.html <- live-lane _state/l1-overview.html (P L8)
    PLANNED tests/fixtures/live1/articles.html <- live-lane _state/l1-articles.html (M C48)
    PLANNED tests/fixtures/live1/post_summary.html <- live-lane _state/l1-post_summary.html (M C38)
    PLANNED tests/fixtures/live7/editor.html <- live-lane _state/live7/editor.skeleton.html (P A14, P A15, P A22)
    PLANNED tests/fixtures/live7/named.html <- live-lane _state/live7/named.skeleton.html (N 103)

The first five are lane L1's five pages, which session 1 captured and whose
offline readers were never written (the session record, item 8). The last
two are session 7's captures, named here by this lane; the live lane's
record names the real paths. Two raw captures on this box were considered
and set aside: the share box as captured 2026-09-20 draws the composer's
labels but none of the forms behind them, so its rows take a target inside
the act; and his own profile as captured 2026-09-20 is three weeks old where
a fresh load is already in session 8.

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

Rows (11): `J 37`, `M C14`, `M C15`, `M C16`, `M C17`, `M M28`, `M M34`,
`N 86`, `N 90`, `N 91`, `N 92`. Each needs a control opened, or a box typed
into, on a surface where `linkedin_server/press.py` refuses it today:
messaging's folder item and search box, the people search's All-filters
control, the composer's scheduled-posts control (the scheduled list has no
address, so no scheduled post can be named first), the jobs home's alert
manager. The gate's words: "A press NEVER extends reach", and on these
surfaces "no basis is declared for this surface, so condition 3 has no way
to be satisfied here". THE EVIDENCE THAT A SECOND ROUTE EXISTS: session 3
opened C8, C9 and C5 on the composer -- a surface the gate refuses for
pressing as `composer_or_editor` -- under the probe rule, and committed the
open states. The question: may a read capture press, or type, under the
probe rule (stopping before any save, send or submit, closing with Escape),
or must each surface first get its own `SENSITIVITY_BASES` or
`DECIDED_REVEALS` entry, or a view-switch entry where the press selects?

### Q-ARTICLE-AUTOSAVE -- loading the article composer

Rows (6): `M C44`, `M C46`, `M C50`, `M C78`, `M C81`, `P L3`. The press
gate: "`/article/new/` is admitted for READING and opening it may autosave a
draft **no surface here can detect**". A capture of the composer is one
load and would unblock the six; this lane does not schedule it. The
question: accept that a capture load may leave an empty draft he cannot
see, or keep the composer unloaded?

### Q-IN-ME-PIN -- judging controls on his own profile

Rows (4): `N 76` (his Follow link), `P C8` (Save to PDF), `P B3` (the photo
editor), `P S4` (the custom-button editor). Each sits behind a control on his
own profile the gate has not judged. The address table: "the Open-to
control, an [aria-expanded] button, is not judged (control_not_judged) -- it
shares that shape with the same links, so only a position-pinned judgement
could admit it". The question: admit these controls by index-pinned
judgements in `press.SENSITIVITY_BASES`, or keep the rows waiting?

### Q-CALLER-COMPOSES -- a caller composing shipped tools, under D6

Rows (3): `J 57`, `J 131`, `N 197`. For `J 57` the address table says
"Every piece ships and the CALLER can compose it today", while a server-side
join "would navigate to ids read off the tracker page, a derived
navigation"; for `N 197`, "Whether a link composed from the group id
discharges the row is an open question under the D6 capability-over-
affordance ruling". The question: does a caller composing shipped tools
(or a link composed from an id) discharge these rows under
D6-CAPABILITY-OVER-AFFORDANCE?

### Q-CONTACT-IMPORT -- uploading other people's contact data

Rows (3): `N 106`, `N 108`, `P N21` (contact sync). The cell: "the import
completes on Google's OAuth consent screen, another domain", and "Importing
uploads other people's contact data to LinkedIn, an act his to fire". The
question: is an address-book import or sync ever built, or do the rows
leave scope?

### Q-PROFILE-SCROLL -- a scroll, or the sub-page, on a profile he names

Rows (2): `N 65`, `N 178`. Session 7 took C-P7 on the member he named; the
cell: "The section is not on the first render, so this row waits on a
ruling for a scroll or the sub-page (C-P7 step 5)". Infinite scroll is not
sanctioned (SCROLL-NOT-SANCTIONED), and the named-profile ruling reads
"never for a measurement". The question: allow one bounded scroll, or a
load of the profile's details sub-page, inside the named read he orders?

### Q-SESSIONS-LIST -- the active-sessions page

Rows (2): `P N9` (the list), `P N10` (signing out of sessions, on the same
page). The class rulings, section 5: the read-past ruling does not reach
"a credential, recovery, session or security surface". The question: is the
sessions page readable or writable at all, or do the rows leave scope?

### Q-SIGNIN-CHALLENGE -- sign-in and account-recovery surfaces

Rows (2): `P N13` (the sign-in prompt, email code or CAPTCHA, at
`/checkpoint/`), `P N14` (identity verification for account recovery, whose
cell reads "CREDENTIAL, BLOCKED -- AND NO BUILD IS APPROPRIATE"). The class
rulings, section 5: not reached for "a sign-in challenge". The question:
rule both out of scope with a reopener, or keep them GAP?

### Q-APPLY-FLOW -- opening the Easy Apply flow may be a GET that changes state

Row: `J 82` (the daily limit and its rate-pause message). The address
table: "Opening it is the first step of an application". The class rulings
of 2026-09-28, section 5, do not reach "a GET that changes state". The
question: is opening the apply flow such a GET (the read stays refused), or
may it be admitted read-only?

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

### Q-GEOLOCATION -- his browser's geolocation permission

Row: `J 17`. The address table: "Whether to grant that persistent
permission is the operator's call, not a boundary or reader question". It
is the operator's, so the orchestrator relays it or rules the row by D6
(the location parameter already reaches every documented result set).

### Q-AWAY-MESSAGE -- a reply in his name, composed in advance

Row: `M M39` (an away message, Premium). The cell quotes the refusal it
rests on -- "a reply in his name that he did not read is a message from a
stranger wearing his face" -- and names its reopener: "the operator ruling
that a message composed and approved IN ADVANCE is not a reply he did not
read". The question is the operator's; the orchestrator relays it.

### Q-UNAIMABLE-CONTROL -- a control no route can aim

Row: `P A9` (the additional name's visibility). The cell: "its only
candidates are two unnamed switches ... so the control is unidentifiable by
every non-press route", and "The A2 and A4 precedent would file it
COVERED-CANNOT-DELIVER". The question: file it so, on that precedent?

### Q-BROADCAST-EDIT -- a profile entry that broadcasts by nature

Row: `P D29` (a LinkedIn Learning certificate on his profile). The cell: "A
new section entry ... excluded from live proof by that ruling", and "No
build." The question: build it behind the grant and leave it unproven, or
rule it out with a reopener?

### Q-SAFETY-REPORT -- a safety report through a Help Center form

Row: `N 152`. The cell: "A harassment or safety report is an accusation",
with the reopener "an in-product STRUCTURED report". The question: keep it
GAP on that reopener, or rule it out of scope?

### Q-ORG-IDENTITY -- which organisations a companies search found

Added 2026-10-10 by lane B2 (`_audit/2026-10-10-lane-b2-network-build.md`,
section 5). Row: `N 104`. The cell's bar: an id reader delivers it if the
results page draws a numeric organisation id per result, and "If the result
cards carry slugs only, it does not deliver: a slug is a name". Session 2's
capture draws slugs only: 10 result Pages, 0 numeric. The question: does
`NAMES-AT-RUNTIME`, with `THIRD-PARTY-TEXT-AT-RUNTIME` (an organisation Page's
prose returned at runtime), let a search return each organisation it found as
its name and its Page link, held to the ruling `PEOPLE-DATA-MITIGATIONS` --
or does the row wait on a page that draws numeric ids?

### Q-EDITOR-TYPEAHEAD -- typing into his own editor's autocomplete field, saving nothing

Added 2026-11-25 by lane build-p26 (`_audit/2026-11-25-build-p26.md`, section
4). Rows (3): `P A11`, `P A13`, `P A17`. Each is an intro-editor field drawn as
an input carrying `aria-autocomplete="list"` and no list relation; LinkedIn
draws the entry list only after typing, and the editor captures of sessions 1,
4 and 7 hold 0 `role=listbox` and 0 `role=option`. The one measurement is lane
B1's capture C-B1a (its section F.1; queue line `C-B1a`): type three
characters into one field, keep a skeleton of the list, then Escape and the
dialog's Dismiss, never Save, and re-read the stored value. Ruling 1 reaches
"a SEARCH box, never a composer or an editor", and the press gate refuses
typing on that page as `composer_or_editor`. The question: may a capture type
into his own editor's autocomplete field when nothing is saved?

### Q-ABSENT-ON-HIS-ACCOUNT -- three things no live reading of his account draws

Added 2026-11-25 by lane build-p26 (`_audit/2026-11-25-build-p26.md`, section
4). Rows (3): `P A14` (postal code), `P A15` (location display choice), `P K8`
(Top Voice badge). Each was read on a live capture of his own account and read
zero: session 7's intro editor holds eleven controls, every one named, none a
postal code or a location display choice; session 8's first render of his
profile, whose top card is where a badge is drawn, holds 0 "Top Voice" in its
text, its labels, its attributes and its scripts. The grounds: `P A14`'s cell,
"if C1 finds none, this row's candidate state is MEASURED-ABSENT for this
account"; `P K8`'s cell, "the next holder of the signed-in profile can settle
it in one re-read"; the state's definition, "no tool, and a LIVE READING of
the surface says LinkedIn does not draw the thing". A build lane moves rows
only to COVERED-UNFIRED. The question, lane B1's first of 2026-10-10: is each
of the three MEASURED-ABSENT for this account?

### Q-OWN-PROFILE-SCROLL -- one bounded scroll of his own profile

Added 2026-11-25 by lane build-p26 (`_audit/2026-11-25-build-p26.md`, section
4). Row: `P D26` (the profile-strength meter). Session 8's first render of
`/in/me/` holds 0 "Profile strength", "All-Star", "Intermediate" and
"Suggested for you" anywhere in the document, and draws no section heading
below Activity. No sub-page of his profile draws a meter, so the details-page
route of `NAMED-PROFILE-DETAIL-PAGES` reaches nothing here. The scroll ruling's
reopener 3: "A surface exists that has no `start` equivalent at all. Then
scroll is not an efficiency but the only route, and this ruling does not cover
it." The question: one bounded scroll of his own `/in/me/` inside a capture
that commits nothing -- or is the first render enough to put `P D26` on
Q-ABSENT-ON-HIS-ACCOUNT beside `P K8`?

### Q-NOTIFICATION-KEY -- which notification card a delete is aimed at

Added 2026-11-25 by lane build-jmn26 (`_audit/2026-11-25-build-jmn26.md`,
section 4). Row: `M C97`. Every notification card draws its own
`Delete notification` item -- 9 of 9 cards on live session 5's capture and 10
of 10 on session 10's, by keyed shape -- but no card carries a key a caller
could pass back: the card and its menu nodes hold `id`, `class`, `type`, a
position (`data-nt-card-index`) and a view name, and `linkedin_notifications`
returns a card's text, its relative time and its link, a link shared by every
card of one kind. A target chosen by position is the page supplying it
(`PAGE-MAY-VETO-NEVER-SUPPLY`), and one matched on a card's words is a write
aimed by text. The question: may a caller name one notification by what
`linkedin_notifications` returned for it, the page vetoing unless exactly one
card matches -- or does the row wait on a key LinkedIn draws?

### Q-ONE-SHOT-FEEDBACK -- a press with no inverse that tunes his recommendations

Added 2026-11-25 by lane build-jmn26 (`_audit/2026-11-25-build-jmn26.md`,
section 5.2). Row: `J 163`. The control is drawn on real markup: live session
8's recommended jobs draws, in `div[data-view-name="jobs-search-list-feedback"]`,
the sentence `Your feedback helps us improve job recommendations.` and two
buttons whose texts are `Are you finding what you<U+2019>re looking for? No`
and `... Yes`, by keyed shape. OUTSIDE-THE-PRODUCT-PURPOSE keeps the row
because it tunes his recommendations. But the press is ONE-SHOT: no inverse
exists to build, what it leaves is unmeasured, and so nothing on the page can
verify it. HIS-OWN-CURATION-NOT-OUTWARD builds curation with its inverse and
proves it in one session, which this act cannot meet, and
OUTWARD-ACTS-NEED-THE-OPERATOR sends an irreversible act to him. The
question: is it built as his own curation whose first press, at his order,
captures what LinkedIn leaves (an undo, if one is drawn, becoming its
inverse) -- or as a one-shot write fired only on his order and verified by
nothing but its receipt -- or held until he asks for it?

### Q-RECOMMENDATIONS-DETAIL-PAGE -- his own recommendations detail page, on a named spelling

Added 2026-11-25 by lane admit26 (`_audit/2026-11-25-admit26.md`, section 5).
Rows: `N 121`, `N 122`, `N 123`, `N 125`, `N 126`, `N 127`, `N 128` and
`P F5` to `P F9`, twelve writes on his recommendations. Lane B1 asked this
first (`_audit/2026-10-10-lane-b1-profile-build.md`, section K, question 3:
"`F1`: admit `/in/me/details/recommendations/` (the `/in/me/` form only)? The
first render never draws the section (A.2)"), and no answer is on disk. The
spelling is NAMED, never drawn: session 8's raw first render of `/in/me/`
holds 0 "Recommendations" as text or label, no capture draws the detail page,
and the ruling `SCROLL-NOT-SANCTIONED` closes the route that would render the
section. The family is measured (`/in/me/details/` for skills, experience,
education and interests), and the interests page is this repository's
precedent for a NAMED detail page admitted and then measured to redirect, its
line kept because it widens nothing. The question: admit
`/in/me/details/recommendations/` by its own anchored `/in/me/` line on the
second clause of `READ-PAST-AN-ACT-SUBSTRING`, on that NAMED spelling, the
capture recording the landing -- or do the rows wait on a capture that draws
it, which no sanctioned route can take?

### Q-OPEN-TO-WORK-EDITOR -- an editor whose only entry is a press named save

Added 2026-11-25 by lane admit26 (record, section 5). Rows: `P B6` and `P I2`
to `P I11`, eleven writes on the Open To Work card. The editor has NO ADDRESS:
`_audit/_slice-otw-census.md`, C3, finds its entry is a button
(`aria-label="Edit"`, no href) whose action is two `SetState`s and a
`ServerRequest` named `saveAndFetchNextStepRequest`, `isEditFlow = true` --
"There is no url anywhere in that action." The ledger's
`/in/me/opportunities/job-opportunities/edit/` is an inference, refused on
`/edit/`, and admitting it would buy nothing. The ruling
`CAPTURE-PRESS-UNDER-PROBE-RULE` lets a capture press a disclosure, "never a
composer or an editor", and the census owes "one capture of the modal taken
with him watching" (`_audit/2026-09-05-profile-modals.md`, section 7). The
question: may a capture press that Edit button -- whose request's name says
save -- with him watching, the modal read and closed and nothing chosen; or
do the eleven rows stay GAP on an editor no route can open?

### Q-VOLUNTEERING-PROFILE-ID -- a page drawn only with his own member id

Added 2026-11-25 by lane admit26 (record, section 5). Row: `P D24`. LinkedIn
draws his "Open to volunteering" page only as
`/in/<me>/opportunities/volunteering/education/?profileId=<his own profile
id>` (both tracked top-card fixtures, the id replaced, and the raw capture);
the services page beside it is drawn bare and was admitted (record, section
3.2). The bare volunteering spelling is unmeasured, and a line for the drawn
one would carry his own member id, which no tracked file may hold, or a
pattern admitting any id. `PAGE-MAY-VETO-NEVER-SUPPLY` says an id comes from a
tool's arguments; `OTHER-MEMBER-IDS-AS-READS` reaches another member's id in a
search facet, not his own in an address. The question: admit the drawn shape
with `profileId` as an id-shaped value from the tool's arguments (his own id,
never stored), or the bare spelling nothing draws with the capture recording
the landing -- or neither?

### Q-VERIFICATIONS-PAGE -- a page the credential words refuse by name

Added 2026-11-25 by lane admit26 (record, section 5). Rows: `P K1`, `P K7`.
`/mypreferences/d/verifications` is refused on "verification", one of the six
words the 2026-09-03 block added beside "password" and "two-factor";
`tests/test_the_second_gate_covers_the_class.py` lists this exact address as
that word's class member, beside `/mypreferences/d/two-step-verification`. So
the substring's recorded ground is a credential-and-security class, not an
act, and `READ-PAST-AN-ACT-SUBSTRING` does not reach "a credential, recovery,
session or security surface". The page lists his identity and workplace
verifications (`P K1`'s cell). The question: is his Verifications settings
page a security surface that stays refused, or a page of his own account to
admit by name, one exemption excusing "verification" for that address alone?

### Q-NAME-BEARING-ADDRESS-REDACTION -- which load records the redaction reaches

Added 2026-11-25 by lane admit26 (record, section 5). Rows: `M C80`, `M C82`,
`M C101`, `N 55`, `N 56` (a newsletter's own page) and `M C79`, `N 41`, `N 42`
(a member's article page). The ruling `NAMED-ADDRESS-NEEDS-LOG-REDACTION`
admits a page whose address carries a person's or a publication's name only
after every log line that records a page load writes that route as a shape.
Lane A measured that the server's own navigation logs no address -- no logger
call in `browser.py` takes the url -- and that the load records which do carry
addresses are the probe and capture scripts' own, the live lane's harness
among them; it left "which of those lines the ruling reaches" to the
orchestrator (its record, section 8, item 4), and no answer is on disk. The
newsletter address is drawn as a slug (`/newsletters/<slug>/` in the
drawn-route corpus); the article address is drawn on no capture, so whether
its slug carries the author's name is unmeasured. The question: does the
redaction reach the probe and capture scripts' load records, or only the
server's own, which already log no address? If only the server's, the
newsletter page can be admitted on its drawn shape now, and the article page
after a capture spells it.

### Q-AI-GENERATING-LOADS -- a load that starts a generation in LinkedIn's AI

Added 2026-11-25 by lane admit26 (record, section 5). Rows: `J 116` to
`J 120`, `J 126` and `J 78` (a posting's guide overlay: Show match details,
Help me stand out, Create cover letter) and `P S2` (the Enhance profile
overlay). The guide overlay's anchors are drawn on the tracked job-detail
fixtures, and the side table records that "Its query is a prompt and its href
carries a conversation id, so opening it starts a generation rather than a
read" (`_audit/_census/jobs-directions.tsv`, `J 116`) -- a GET that changes
state, which `READ-PAST-AN-ACT-SUBSTRING` does not reach, named so by lane A
(its record, 2.6). `/in/<me>/overlay/enhance/` is drawn too (the drawn-route
corpus), carries no prompt and no conversation id, and has never been opened:
whether its first render starts a generation is unmeasured. `J 116`'s flag half
is already derivable from `linkedin_premium_job_collection(0)`. The question:
is a load that starts a generation in LinkedIn's AI products, on his own
account and toward no person, a GET that changes state (refused), or a passive
cost of a read (admitted, the generation recorded on the row)? And does the
answer reach the enhance overlay on its unmeasured first render?

### Q-AI-COACH-QUESTION -- a typed question to an AI product

Added 2026-11-25 by lane admit26 (record, section 5). Row: `J 155` (ask
LinkedIn Learning's AI coach and read its answers). `/learning/chatbot/` is
drawn in the Learning nav (the completeness table); lane A left it out because
"the read half exists only after a typed question, a write" (its record, 2.6).
A question typed to an AI product reaches no person, so it is no outward act
in `OUTWARD-ACTS-NEED-THE-OPERATOR`'s sense, and no build-class ruling names
it. The question: is asking the coach a question a write this server builds
behind the grant -- the page then admitted for its capture -- or does the row
stay GAP, or leave by the ruling `OUTSIDE-THE-PRODUCT-PURPOSE`?

### Q-COURSE-VIDEO-PROGRESS -- a hold that was answered and never registered

Added 2026-11-25 by lane admit26 (record, section 5). Row: `J 153` (watch a
LinkedIn Learning course video). The shape `/learning/<digits>/<digits>/` is
drawn (the drawn-route corpus). Lane A did not admit it, on its own inference
that "playing a course records progress in his own Learning history, a state
change" (its record, 2.6), and the orchestrator's answer of 2026-10-10 kept it
"as lane A left them: refused on its stated inference"
(`_audit/2026-10-10-rulings-lane-a-questions.md`, Q4), registering no ruling.
`D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING` leaves such a row GAP until a
decision is registered. The question: register the hold -- a course video
stays refused as a GET that changes state, the row EXCLUDED-RULED with a
reopener -- or rule that progress recorded in his own history is a passive
cost by `D5-PASSIVE-COST-IS-NOT-A-ROW`, admitting the drawn shape by its own
line?

### Q-AD-LIBRARY-PURPOSE -- a purpose doubt that was answered and never registered

Added 2026-11-25 by lane admit26 (record, section 5). Row: `J 159` (search
LinkedIn's Ad Library for the ads a company runs). `/ad-library/search/` is
drawn on a company Page as 'View ad library' (the completeness table). Lane A
did not admit it, class (e), "purpose doubtful", reopening "on the
orchestrator's word that it serves the product" (its record, 2.6), and the
orchestrator's answer of 2026-10-10 (Q4) kept it as lane A left it,
registering no ruling. The row's own cell reads "Company research reachable
from a job, beside rows 106-114". The question: does company research from a
job serve his search -- then `/ad-library/search/?companyIds=<digits>` is
admitted by its own exact line -- or is the row EXCLUDED-RULED by
`OUTSIDE-THE-PRODUCT-PURPOSE`, reopened when he asks?

### Q-RESUME-BUILDER -- a builder that may autosave, at an address nothing draws

Added 2026-11-25 by lane admit26 (record, section 5). Row: `P M11` (LinkedIn's
Resume Builder, read and write). Lane A left `/resume-builder/` refused on two
grounds (its record, 2.6): the address is INFERRED -- nothing draws it; it comes
from a script's table -- and "a builder is a composer-class surface that may
autosave" (lane L1's ground, argued, not measured). The ruling
`ARTICLE-COMPOSER-CAPTURE` answered that question for the article composer
alone: one load, nothing typed, an empty draft his, private and deletable,
recorded if it appears. The question: does its reasoning extend to the resume
builder, so that once a capture finds where LinkedIn draws it (the
application-settings page, admitted, is the likeliest), one load of it may be
taken -- or does it stay refused as a surface that may autosave?

### Q-SELF-PROFILE-QUERY-VARIANT -- whether his own profile's self-profile spelling is a read address

Owed to the orchestrator since integration 3 (2026-11-26), by its ruling LINKS-ARE-NOT-DISCLOSURES of
2026-11-25: the `in-me-profile` capture's link presses for `P D25` ('Add section', a top-card link to his own
profile carrying `?isSelfProfile=true`) and `P A25` ('Contact info', the top card's link to his contact-info
overlay) are vetoed, because a link is not a disclosure and a page may veto a target, never supply one. The
question both rows wait on: is the self-profile query variant of his own profile address admissible as a READ
address in its own right? Rows: `P D25`, `P A25`.

### Q-REINVITE-COMPOSITION -- a re-invitation composed from two shipped tools

Added 2026-11-26 by lane readers-net26 (`_audit/2026-11-26-readers-net26.md`,
section 5). Row: `N 6`. Its cell's prerequisite -- the Sent manager admitted --
is met, and the manager is read: `linkedin_sent_invitations` (row `N 9`) lists
each pending invitation he sent, so one that expired is no longer listed; and
sending anew is `linkedin_connect_from_profile` (rows `N 2`, `N 4`,
COVERED-UNFIRED), which presses Connect only where the member's profile draws
it. The question: is `N 6` discharged by CALLER-COMPOSITION-UNDER-D6 on those
two tools, its state the weaker of them, COVERED-UNFIRED -- or does a
re-invitation need an expiry LinkedIn itself draws, which no capture shows?

ANSWERED 2026-11-26 by the orchestrator, applied in lane readers-net26's round
2: YES -- discharged by CALLER-COMPOSITION-UNDER-D6 on those two tools, at the
weaker state, COVERED-UNFIRED; LinkedIn's own re-invite cooldown is honoured,
because `linkedin_connect_from_profile` presses only a Connect the profile
draws, and Connect stays outward, fired only at a target he names. `N 6` left
the ledger with it. Registered at integration 4.

### Q-REFOLLOW-AIM -- a Follow button on a row that carries no member

Added 2026-11-26 by lane readers-net26 (section 5 of its record). Rows:
`N 40`, and `M C52` beside it. Each of the 44 rows of his unfollowed page
(`/mypreferences/d/unfollowed`, session 11, load 9) draws one `Follow`
button, and no row carries a member link or id -- measured on the kept raw
page: 0 profile addresses and 0 member urns, the picture link without an
href. So the only things that tell one row from another are the member's
name and the row's position, and PEOPLE-DATA-MITIGATIONS item 6 forbids
aiming a write by a name, NO-INDEX-PINNED-JUDGEMENTS by a position. The
question: is the re-follow built from the member's own profile, which he
names by link (THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET; row `N 34`'s route,
unbuilt), the unfollowed list read only as a veto -- or held?

ANSWERED 2026-11-26 by the orchestrator, applied in lane readers-net26's round
2: build the re-follow from the member's OWN profile, which he names by link
(THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET, `N 34`'s route); the unfollowed list is
a read and a veto only, never a source of the target. `N 40` and `M C52` now read
SIBLING `N 34`. Registered at integration 4.

### Q-AD-HIDE-TARGET -- hiding an ad LinkedIn chose

Added 2026-11-26 by lane readers-net26 (section 5 of its record). Row:
`N 200`. Session 11 opened a promoted item's own control on the feed (load
28): its menu draws `Hide this ad`, `Report ad` and `Why am I seeing this
ad?` (keyed shape), the hide an action link. Lane B2's blocker (3) stands:
the ad is LinkedIn's choice, and the only handle on it on the page is the urn
its own `Embed this post` entry carries -- the page would supply the target
(PAGE-MAY-VETO-NEVER-SUPPLY). The question: may a hide be aimed at an ad he
names by that urn, read off his own feed by a reader and handed back by him,
with its undo captured on the first supervised fire (HIS-OWN-CURATION-NOT-
OUTWARD) -- or does an ad stay out of the curation class? The report half is
an outward class either way, fired only at a real item he names.

ANSWERED 2026-11-26 by the orchestrator, applied in lane readers-net26's round
2: YES under HIS-OWN-CURATION-NOT-OUTWARD -- the ad is one he names, an urn a
reader returned to him and he hands back; the tool never picks an ad itself;
the hide's undo is captured on the first supervised fire; `Report ad` stays
outward, fired only at a real item he names. `N 200` now reads BUILD behind the
grant. Registered at integration 4.

### Q-MESSAGE-SEARCH-TYPING -- a search box in his own inbox, reachable only by typing

Added 2026-11-26 by lane readers-msg26 (`_audit/2026-11-26-readers-msg26.md`,
section 4). Row: `M M34`. Live session 11 typed one benign keyword into the
message search at the head of his own inbox and LinkedIn drew a results view
in place of the conversation list; no address of the search's own was
recorded. A shipped read may not type -- the press module refuses typing in
both its rules -- and `D1-SEARCH-AS-READS` permits search keywords as reads
for an address composed from a tool's arguments, which this search has not
been seen to have. The question: may a shipped read type a caller's keyword
into his inbox's search box, read the rows the view draws as the list reader
does, and clear the box -- or does the row wait on a capture that shows the
search landing on an address of its own?

**Answered 2026-11-26 by the orchestrator** (relayed to lane readers-msg26;
registration owed at integration 4). CAPTURE FIRST: one capture load that
types a benign keyword into the inbox search and records whether the search
lands on an address of its own. If it does, the read composes that address
under `D1-SEARCH-AS-READS` and types nothing. Only if it does not, a shipped
read may type the caller's keyword into the inbox SEARCH input, under a new
sanctioned shape SEARCH-BOX-TYPING: the input identified by role search or
searchbox and its own label, never a contenteditable composer; Enter pressed
only within that input; the rows read as the list reader reads them; the box
then cleared and the conversation list verified restored; a refusal if focus
is ever in a composer or any send control becomes enabled -- built red first,
with a control that shows composer typing refused. Row `M M34`: next step
`CAPTURE:messaging-guarded`, the search box riding that line's load.

### Q-SCHEDULED-LIST-PRESS -- a list of his own reached only through the post composer

Added 2026-11-26 by lane readers-msg26 (`_audit/2026-11-26-readers-msg26.md`,
section 5). Row: `M C14`. Live session 11 pressed the post composer's
`Schedule post`, then `View all scheduled posts`, and LinkedIn drew a dialog
headed `Scheduled posts` holding an empty state (`No scheduled posts yet`, a
`Schedule` button) -- a list of his own, drawn and corroborated empty. No link
reaches it and no address is drawn for it: both presses sit inside the
composer, which the press module refuses for any shipped read, whatever the
surface's admission (the autosave argument). The question: may a shipped
read press those two controls, read the list -- an empty state counted as
zero only when its headline is drawn -- and close it with nothing typed or
scheduled, or does the row stay unreachable as a composer surface?

**Answered 2026-11-26 by the orchestrator** (relayed to lane readers-msg26;
registration owed at integration 4). YES, as a shipped read: open the post
composer EMPTY, press `Schedule post`, then `View all scheduled posts`, read
the list -- an empty state counted as zero only when its headline is drawn --
and close everything with nothing typed or scheduled, VERIFYING that no draft
appeared; STOP on any autosave or draft sign. Row `M C14`: next step `BUILD`
on `tests/fixtures/live11/sharebox_scheduled_list_open.html`.

### Q-ARTICLE-COMPOSER-DISCLOSURES -- the article editor's own closed controls, nothing typed

Added 2026-11-26 by lane readers-msg26 (`_audit/2026-11-26-readers-msg26.md`,
section 6). Rows: `M C44`, `M C46`, `M C50`, `M C78`, `M C81`, `P L3`. Live
session 11's one load of `/article/new/` (ARTICLE-COMPOSER-CAPTURE: nothing
typed, nothing published, no draft redirect) drew every entry point these rows
need CLOSED: the author toggle (subtitle `Individual article`, where a
newsletter is chosen), `Manage`, the embed control, and `Next`, the publish
flow's first step, enabled on the empty article -- behind an onboarding dialog
(`Get started`, `Dismiss`). Each is a disclosure or a dialog that commits
nothing, and each sits inside an editor, which CAPTURE-PRESS-UNDER-PROBE-RULE
excludes. The question: may one capture load of the article composer, nothing
typed, dismiss the onboarding dialog and press the author toggle, `Manage`,
the embed control and `Next` -- each read and closed with nothing chosen and
nothing published, a draft's appearance recorded -- as
B5-GROUP-COMPOSER-OPENS-EMPTY allowed a group composer to be opened?

**Answered 2026-11-26 by the orchestrator** (relayed to lane readers-msg26;
registration owed at integration 4). YES, as ONE CAPTURE, nothing typed:
dismiss the onboarding dialog, then press the author toggle, `Manage`, the
embed control and `Next`, each read and closed with Escape or Cancel; never
Publish and never Schedule; record whether a draft appeared, and if one did
its next step is deleting that draft (his own, reversible); STOP-ALL if any
control would publish. Rows `M C44`, `M C46`, `M C50`, `M C78`, `M C81`,
`P L3`: next step `CAPTURE:C-MSG26-4`, one queue line.

### Q-CONVERSATION-MENU-STATE -- a menu whose items exist only while it is open

Added 2026-11-26 by lane readers-msg26 (`_audit/2026-11-26-readers-msg26.md`,
section 7). Rows: `M M26`, `M M27`, `M M29`, `M M31`. Live session 11 opened,
on the conversation he named, by its recorded id and behind the receipt guard,
the ACTIVE row's options menu: eight items -- Move to Other, one unmatched,
Mark as unread, Star, Mute, Archive, Delete conversation, Manage settings --
bound to that conversation by the active marker on the thread's own page,
which lane B3 found no earlier capture could do. The items exist only while
the menu is open, so a write's preview, which presses nothing, cannot read
whether the conversation is already muted, archived or unread. The question:
may each such write's preview open that one menu as a disclosure and close it
on Escape, to read its item's word before a token is minted -- a new
sanctioned preview press, as the similar-jobs toggle's trial press was -- or
must each act read its word only inside the confirmed press, refusing without
pressing when the menu draws the inverse word? And `Delete conversation`,
whose next state is not on disk and which has no inverse: built refusing at
any dialog it has not seen, as `J-19-BUILT-BEHIND-THE-GRANT` built `J 19`?

**Answered 2026-11-26 by the orchestrator** (relayed to lane readers-msg26;
registration owed at integration 4). YES, a sanctioned PREVIEW press, on the
similar-jobs trial-press precedent: the preview opens that ONE options menu as
a disclosure, bound to the named conversation by the active marker, reads the
item's word (Mute or Unmute, Archive or Unarchive, and so on), presses nothing
inside it, closes it on Escape and verifies it closed; the confirmed press
RE-READS the word and refuses on the inverse. `Delete conversation` has no
inverse, so it is RECEIPT-ONLY behind the grant (the `J 163` class), fired only
on his explicit order for a conversation he names, and refusing otherwise.
Rows `M M26`, `M M27`, `M M29`, `M M31`: next step `BUILD` on
`tests/fixtures/live11/c_b3_1_menu_open.html`.

### Q-J37-SPLITS -- a compound row whose list half is built and whose manage half is not

Added 2026-11-26 by lane build-jobs2 (`_audit/2026-11-26-build-jobs2.md`,
section 6). Row: `J 37`, "List and manage all alerts". The list half is
built on session 11's capture of the alert manager --
`linkedin_job_alerts`, each alert's keywords and the names of its filters --
and the manage half is not: the row button's label and what it opens have
never been measured, and editing or deleting an alert is the `J 33` and
`J 34` capability, each waiting on an alert he names. The halves now need
different STATES (COVERED-UNFIRED and GAP), which is
COMPOUND-ROW-SPLITS-ONLY-ON-STATE's ground, and `J-114-SPLITS` split the same
shape. The question: split `J 37` -- the list half COVERED-UNFIRED on the new
read, the manage half the next free numeric id, GAP, resting on `J 33` and
`J 34` -- or hold it whole and GAP until the manage half is built?

ANSWERED 2026-11-26 by the orchestrator, `J-37-SPLITS` (integration 6
registers it): SPLIT under COMPOUND-ROW-SPLITS-ONLY-ON-STATE, the `J 114` /
`J 169` precedent. Applied by lane build-jobs2's round 2: `J 37` keeps the
list half, COVERED-UNFIRED on `linkedin_job_alerts`; the manage half is
`J 170`, GAP, next step BUILD (the alert edits).

### Q-SEARCH-BOX-PRESS-SHAPE -- a press shape the search box does not wear

Added 2026-11-26 by lane build-net2 (`_audit/2026-11-26-build-net2.md`,
section 4). Row: `N 95`. Its step, from lane readers-net26, is "the search
box's sanctioned press first, then a reader of that listbox over the capture".
The global search box's input carries neither sanctioned press shape -- no
`aria-expanded`, no `aria-haspopup`, no role -- on session 11's three feed
captures. `press.py` makes a third shape a RULING REQUEST with a measured
blast radius. Measured over the 176 tracked HTML fixtures, counts only: an
input carrying `aria-autocomplete` inside `role=search` is 63 elements, one on
each of 63 pages; the same input outside `role=search` is 78 elements in 57
files, the typeaheads of forms and filters. The question: may a press of
`[role=search] input[aria-autocomplete]` -- one element a page -- open the
recent-searches listbox so a read can take it over the capture, re-running a
search staying the caller passing its keywords to a search tool (D6)? (The
nearest ruling, MESSAGE-SEARCH-CAPTURE-FIRST, contemplates a SEARCH-BOX-TYPING
shape for his inbox search only after a capture; this row types nothing.) Or
does `N 95` stay GAP?

**Answered 2026-11-26 by the orchestrator** (relayed to lane build-net2;
registration owed at integration 6): YES, as SEARCH-BOX-TYPEAHEAD-DISCLOSURE,
on the lane's measured anchors. A module of its own, one closed table, one
`readonly.SANCTIONED_MUTATIONS` entry -- one sanctioned SHAPE, not one
triple, the orchestrator clarified the same day on the lane's question: one
drain function with exactly two call sites, the click that opens (as load
28 measured it) and the Escape that closes, so the list holds TWO lines,
16 -> 18; every other key and every fill refused; no Shift-key or focus
open, since nothing measured one. The target is
`[role=search] input[aria-autocomplete]` on an admitted page, refused at
runtime if the match count is 0 or 2 or more, naming the count. NOTHING is
typed: a typing attempt is refused. Only the listbox's recent-searches group
is read, located by its own structure, under HIS-OWN-TEXT-AT-RUNTIME; the
people options are never read or returned. Closed by Escape, and the listbox
verified gone. Condition 3, the structural argument that a typeahead opening
sends nothing outward, is accepted. Red first, with three controls: an
`aria-autocomplete` input outside `role=search` refused; a second matching
input refusing; an attempt to read the people options failing the test. Row
`N 95`: built and COVERED-UNFIRED on `linkedin_recent_searches` (the lane's
record, section 4).

### Q-AD-HIDE-AIM -- an ad he names, when no reader returns one

Added 2026-11-26 by lane build-net2 (`_audit/2026-11-26-build-net2.md`,
section 5). Row: `N 200`. `Q-AD-HIDE-TARGET`'s answer, AD-HIDE-AT-HIS-NAMED-AD,
builds the hide at an ad he names: "an urn a reader returned to him and he
hands back". No shipped reader returns an ad's urn. The readers of item keys are
`linkedin_my_activity_items` (his own posts) and `linkedin_read_named_profile`'s
`activity_items` (a named member's posts); `linkedin_search_content` returns no
link, and `linkedin_surface_census` substitutes urns out. On session 11's
capture the ad's urn is drawn only inside its own menu (the Embed entry), after
a press, on `/feed/`. An ad's own permalink -- `N 154`'s route, where the urn is
the address -- has never been loaded, so whether it draws `Hide this ad` is
unseen. The question: does `N 200` wait until a reader returns ad urns to him
(a feed reader under FEED-CONTENT-READ-RULING) and an ad's permalink is
captured with its menu open, then built in `mark_not_interested`'s shape? Or
is it built now on the permalink route, aimed at an urn he names, though
nothing he can read today hands him one? The lane's default, with no answer on
disk: it waits. `Report ad` stays outward either way.

**Answered 2026-11-26 by the orchestrator** (relayed to lane build-net2;
registration owed at integration 6): AD-HIDE-AIM-HELD, option (a). `N 200`
stays GAP with the lane's measurement recorded. Reopener: a sanctioned
disclosure shape for the ad control-menu trigger, measured, so that a reader
can return an ad's urn to him WITHOUT pressing ads he did not name. Option
(b) is declined: it presses the menus of ads he did not name, for a low-value
row. Row `N 200`: next step this question, held, until the reopener is met.

### Q-MEDIA-POST-AUDIENCE -- a photo or a video on the composer whose audience is unread

Added 2026-11-26 at integration 6, from lane build-msg2's question 2
(`_audit/2026-11-26-build-msg2.md`, section 6). Rows: `M C3` and `M C4` (`M C6`
and `M C7` ride `M C5` and `M C3`). The media control is drawn on the feed's
composer, `/preload/sharebox/`, the composer `linkedin_publish_post` types into
-- and that tool refuses before minting anything (`audience_unread`): the
composer's audience control is unread, so nothing here can say who a post
would reach. The lane asked: "DOES THE FEED POST'S AUDIENCE REFUSAL BIND A
MEDIA POST?" -- and, if it were built, whether `perform` may hand a file over
after a press that only opens a dialog, against the drain's stated "before
any click" order.

**Answered 2026-11-26 by the orchestrator** (22:33, registered at integration
6): MEDIA-POST-SAME-REFUSAL. The audience is unread, and there is no upload
after a press; `M C3`, `M C4`, `M C6` and `M C7` stay GAP and cite the
ruling. Reopener: an audience the server can read. Rows `M C3` and `M C4`:
next step this question, held, until the reopener is met.

### Q-SELF-ROOT-FORM-LINKS -- a form his own profile root reaches only by a link

Added 2026-11-27 by lane prof7 (`_audit/2026-11-27-prof7.md`, section 3).
Rows: `P A26` to `P A29`, `P D2`, `P D5`, `P D6`, `P D8`, `P D9`, `P D27`,
`P H1` (queue lines 30, 31, 64, 67, 68). Live session 12 found every
`/in/me/edit/` and `/in/me/opportunities/` address landing on his profile root
with no form (6 of 6). On the nine keyed skeletons of his root (sessions 11
and 12, matched offline in LinkedIn's own words) every drawn entry to those
forms is a LINK -- `Edit about`, `Edit profile language`, the services card,
the top card's `Contact info` -- and LINKS-ARE-NOT-DISCLOSURES vetoes link
presses on his profile. The question: may a capture press such a link when
its target, his proven member read as `me`, is exactly the address the
boundary already admits for that line?

**Answered 2026-11-27 by the orchestrator** (13:00, amended 13:10; on disk
to lane prof7; registration owed at integration 7):
SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH, attended only. A link drawn on his root
is pressed only when its href is EXACTLY the admitted address for that line,
the landed member, proven his by the self-profile loader, read as `me`: a
match, never a follow, and any difference vetoes. The match includes any
query the admission itself carries (rank 31's entry-point query), and nothing
the page adds. The contact-info line takes the rule twice (the overlay link,
then the form's own link inside it). A press that navigates is a load. In the
editor, labels and states only, nothing typed or saved, no Save, Submit,
Delete or Remove in the closed list; closed by Escape or its exact Dismiss
and verified gone; his root read before and after, its structure unchanged.
No row moves on the ruling; the rows' next steps are those queue lines'
session-14 captures.

**Amended 2026-11-27 17:20 by the orchestrator** (on disk to lane prof7,
after the cold verification; registration owed at integration 7):
EXACT-MATCH-REFUSES-ANY-WHITESPACE. The match never normalises the target:
any whitespace, control, character outside printable ASCII or
percent-escaped whitespace or control refuses, and the raw string is compared
with the admitted address character for character, its only equivalences the
admission's own query and `me` for the proven member. One matcher serves
every line: `volunteering_route.exact_link_verdict`.

### Q-VOLUNTEERING-ID-FROM-HIS-ARGUMENTS -- a page every drawn route reaches with his own id

Added 2026-11-27 by lane prof7 (`_audit/2026-11-27-prof7.md`, section 3).
Row: `P D24` (queue line 69). VOLUNTEERING-BARE-SPELLING-FIRST's reopener is
met: the bare spelling landed on his profile root (live session 12, load
22). Every drawn route to the page carries `?profileId=` -- his root's card
link on all nine keyed skeletons, and the `Open to` menu's volunteering item
(`_audit/_slice-otw-census.md`) -- an id the page supplies, which
SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH vetoes. The question: does the ruling's
fallback, profileId from tool arguments at runtime (his own id, never
stored), now get its boundary line -- or does `P D24` hold?

**Answered 2026-11-27 by the orchestrator** (13:10; on disk to lane prof7;
registration owed at integration 7): VOLUNTEERING-FALLBACK-BOUNDARY, yes. The
boundary line is built in lane prof7, red first: the drawn spelling with one
member-id-shaped `profileId`, the id ONLY from the caller's arguments at
runtime (for the live runner, the gitignored identity key's operator class),
validated by shape, never stored, logged, committed or kept in a raw; a
missing or ill-shaped id refuses; the page never supplies it, so his root's
card link -- or the `Open to` menu's item, by the same match -- is pressed
only when its target equals the address formed from his argument. Row
`P D24` moves no state; its next step is the session-14 capture under that
match, attended.

### Q-J169-SENIORITY -- a facet whose one measured control offers another

Added 2026-11-27 by lane jobs7 (`_audit/2026-11-27-jobs7.md`, sections 4 and 7). Row: `J 169`
("Premium Page Insights: headcount over time, notable alumni, job openings by seniority", split
from `J 114` by J-114-SPLITS). Its step was `CAPTURE:C-RJ26-1`: the job-openings card's
`Functions` dropdown opened as a disclosure, "the seniority view, if one is offered, then read
offline". Session 12's load 20 opened it: by keyed shape the dropdown's items are JOB FUNCTIONS
(the open page draws 14 of the 26 function words), and 0 of 10 seniority words and 0 of 5
experience-level words match anywhere on the page. So no seniority view is offered behind the one
control the row's step named; "notable alumni" is not drawn on this view; and the open page draws a
table summarised `Total employee count`, the candidate for "headcount over time", its cells reduced.
The lane asks: IS "JOB OPENINGS BY SENIORITY" A FACET LINKEDIN STILL DRAWS ANYWHERE -- so the row's
next step is a capture of another Insights view -- OR DOES THE ROW SPLIT, its seniority facet closed
by this measurement? The cell names no absence as its bar, so this lane moves nothing.

**Answered 2026-11-27, 13:45 IST, by the orchestrator** (integration 7 registers it): J169-SPLITS-SENIORITY-REAIMED-UNDER-D6 -- split, the FUNCTION half keeping `J 169` and building on load 20, the SENIORITY half a new GAP row whose next step is a capture of the AI job search's experience-level facet for that company (not MEASURED-ABSENT on one dropdown). HELD by the lane: `J 169`'s capability names no function facet on disk (distribution by function is `J 114`), so the split cannot be applied as written without re-scoping the row (the lane's record, section 11.4); its step stays here, and the counts the ruling asked for are in its cell.

**Answered again 2026-11-27, 14:05 IST, by the orchestrator** (integration 7 registers them): J169-BY-ITS-OWN-WORDS, plus JOB-OPENINGS-BY-FUNCTION-ADDED, replacing the 13:45 answer. The split is applied to the row's own words: load 20 draws headcount over time and notable alumni, so `J 169` keeps those two (step BUILD on `tests/fixtures/live12/c_rj26_1_functions-open.html`), and the seniority facet is `J 173`, GAP, step CAPTURE `C-J173-1` under D6. "Job openings by function" is a new row, `J 174`, drawn on load 20 with no selection (step BUILD on the same fixture); `J 114` is a different capability and is not merged. The counts stay in the cells. The lane's record, section 11.5.

### Q-J170-ROW-CONTROL -- an alert's own control that may open an editor

Added 2026-11-27 by lane jobs7 (`_audit/2026-11-27-jobs7.md`, section 7). Row: `J 170` ("Manage
all alerts", split from `J 37` by J-37-SPLITS). Its step was BUILD on session 11's alert-manager
capture (`tests/fixtures/live11/jobs_alerts_manager.html`), but that capture never drew what an
alert row's control opens: the control's label matched none of 23 candidates by keyed shape (an
edit, a delete, a frequency, a menu word), and nothing was pressed. A build aimed at an unmeasured
dialog would be built on synthetic markup and move nothing. Pressing the control to read it is not
plainly a CAPTURE-PRESS-UNDER-PROBE-RULE disclosure: it may open an EDITOR, which that rule forbids
pressing. The lane asks: MAY A CAPTURE PRESS ONE ALERT ROW'S CONTROL, read what it opens by keyed
shape, and close it on Escape with nothing chosen -- as a disclosure if it opens a menu, and stop
unpressed if it opens an editor? Until ruled, `J 170` stays GAP on this question.

**Answered 2026-11-27, 13:45 IST, by the orchestrator** (on disk to the lane; integration 7 registers it): JOB-ALERT-ROW-CONTROL-ATTENDED -- accepted as a SESSION-14 capture, ATTENDED: one alert row's control pressed; a menu read and closed on Escape; an editor or dialog read for labels and states only, nothing typed or chosen, closed by Escape or its exact Dismiss and verified gone; the alert manager read before and after, no change; no Save, Delete or Remove press in the closed list. `J 170` stays GAP, its step now CAPTURE `C-J170-1` (the lane's record, section 11.3); wave 8 builds on that capture.

### Q-LEARNING-SPLITS -- three Learning rows, each captured on one half

Added 2026-11-27 by lane jobs7 (`_audit/2026-11-27-jobs7.md`, section 7). Rows: `J 152`, `J 154`,
`J 156`, each captured by session 12 on ONE half of a compound capability. `J 152` ("Browse
LinkedIn Learning: its home, the catalogue, certifications, topic pages and showcase collections"):
the home is captured (load 23: 16 course cards, each a type label and a duration by keyed shape);
the catalogue and certifications pages are admitted and uncaptured; topic and showcase pages are
refused. `J 154` ("View your LinkedIn Learning library: saved courses and the ones in progress"):
load 25 landed one level deeper, on the IN-PROGRESS tab (its link marked `aria-current="page"`),
drawing one course with `Unsave` beside it; the saved list is uncaptured, and the read boundary
refuses its address (NO-PATTERN). (This sentence first named the other tab; the lane's record,
section 11.2, holds the reading that settled it.) `J 156` ("See and set career goals", R+W): load 24 draws a section
labelled `Career goal`; the setting half is an editor, unmeasured. Each row's payload is WHICH items
of other people's content (course titles; NAMES-AT-RUNTIME) or his own text (his goal;
HIS-OWN-TEXT-AT-RUNTIME). The lane asks: DOES EACH SPLIT UNDER COMPOUND-ROW-SPLITS-ONLY-ON-STATE, as
J-114-SPLITS and J-37-SPLITS split theirs -- the captured half building on its capture, the rest a
new GAP row with its own next step? Until ruled, the three stay GAP on this question.

**Answered 2026-11-27, 13:45 IST, by the orchestrator** (integration 7 registers it): LEARNING-ROWS-SPLIT -- all three split under COMPOUND-ROW-SPLITS-ONLY-ON-STATE, each captured half keeping its id. APPLIED to `J 152` (its other half `J 171`, step CAPTURE `C-LRN-1`) and `J 156` (its write half `J 172`, step CAPTURE `C-LRN-2`, session 14, attended). `J 154` is HELD: the ruling named in-progress as its other half, and disk says the captured tab is in-progress (the lane's record, section 11.2); its step stays here until the orchestrator rules again.

**Answered again 2026-11-27, 14:05 IST, by the orchestrator** (integration 7 registers it): LEARNING-ROWS-SPLIT, re-ruled on the lane's measurement -- the IN-PROGRESS half keeps `J 154` and builds on load 25's capture (step BUILD on `tests/fixtures/live12/learning_library.html`); the SAVED half is `J 175`, GAP, its address ADMITTED by one anchored line, red first, its step CAPTURE `C-LRN-3` (session 14, the ADMIT-NOW-LANDING-IN-SESSION-14 shape). "Your corrected three sentences stand." The lane's record, section 11.5.

### Q-FEED-UNFOLLOW-AIM -- an Unfollow drawn only on /feed/, where an item's urn is drawn only inside its open menu

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 4). Row:
`N 37`. Session 12 opened a followed author's item menu on `/feed/` (load 16)
and that same post's own permalink menu (load 17). The feed menu draws
`Unfollow <the author>` (the runner's in-page count, 1). The permalink, where
the urn he names IS the address, draws no entry beginning `Unfollow ` (0), and
neither does a Page post's permalink (load 39). On `/feed/` an item's urn is
drawn only inside its open menu: one `/feed/update/` address across the seven
menu-bearing items closed, and one `targetUrn` link once a menu opens. So the
only drawn route presses the menus of items he did not name until the one
whose urn he named appears -- the option AD-HIDE-AIM-HELD declined for ads
(`N 200`). The question: is `N 37` held the same way, until a sanctioned
disclosure shape returns item urns without pressing items he did not name? Or
is it discharged under D6 by another route that unfollows a person he names --
his following list (`linkedin_my_following_list`'s page, where each followed
member's card draws one `Following` button)?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): FEED-UNFOLLOW-ROUTES-UNDER-D6. `N 37` is HELD on the feed, on
AD-HIDE-AIM-HELD's ground: no press on the menu of an item he did not name.
Under D6-CAPABILITY-OVER-AFFORDANCE its next step goes to a surface that draws
the named target directly: a SIBLING to an existing route that unfollows a
member he names, if the tool surface has one, else a CAPTURE on his following
list, network's surface, for wave 8; the lane builds neither. Checked by the
lane: no shipped tool unfollows a member (`linkedin_follow_company`,
`linkedin_follow_company_page` and `linkedin_unfollow_company` act on a
company). Row `N 37`: next step `CAPTURE:following-list-unfollow`.

### Q-ARTICLE-MANAGE-DRAFTS -- a drafts list reached only by a button inside the article editor

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 2). Row:
`M C47`. Session 12 opened `Manage` on the article composer (load 7): eight
`role=button` items and no address -- `Settings` | `Drafts`, `Scheduled`,
`Published` | `New draft`, `Create newsletter`, `Help`, `Give feedback`, each by
keyed shape. The drafts list this row needs is reached by pressing `Drafts`; no
spelling of its address is drawn, and the three NAMED ones are drawn nowhere.
Q-ARTICLE-COMPOSER-DISCLOSURES' answer named the controls one capture may press
inside the editor (the author toggle, `Manage`, the embed control, `Next`);
`Drafts` is one press deeper, and it navigates. The question: may one capture
load of the article composer press `Manage` and then `Drafts`, record where it
lands (by path words) and what the list draws (by closed words, each draft's
own controls drawn closed), and return, with nothing else pressed and nothing
typed?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): ARTICLE-EDITOR-PRESSES, part (a): the `Drafts` press in `Manage` is
a read of his own lists, ACCEPTED as a session-14 capture spec in the queue's
own form. Row `M C47`: next step `CAPTURE:article-composer`.

### Q-NEWSLETTER-CREATE-FORM -- a newsletter form behind Manage's Create newsletter

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 2). Rows:
`M C50`, `M C81`, `P L3`. Session 12 opened the article composer's author
toggle (load 7): a form whose `Publish as` lists only him and whose `Publish to`
lists `Individual article` and an empty newsletter list. It draws no create
control, so the DERIVED premise those three cells carried (the newsletter
"chosen behind the author toggle") is wrong. `Create newsletter` is drawn in
`Manage` instead, by keyed shape. What it opens -- expected to be the
newsletter's creation form -- is not on disk, and it sits inside the editor.
The question: may one capture load press `Manage` and then `Create newsletter`,
read the form it opens by closed words (its fields; any choice of publisher
between him and a Page, for `M C81`; its submit control drawn and never
pressed), and close it with Cancel or Escape, with nothing typed and STOP-ALL if
any control would create or publish?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): ARTICLE-EDITOR-PRESSES, part (b): press `Create newsletter`, read its
form with NOTHING typed, and close it without submitting -- ACCEPTED as a
session-14 capture spec. Rows `M C50`, `M C81`, `P L3`: next step
`CAPTURE:C-MSG7-2`.

### Q-ARTICLE-NEXT-NEEDS-A-TITLE -- the publish settings, reachable only after a title is typed

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 2). Rows:
`M C44`, `M C78`. Session 12 pressed `Next` on the empty article (load 7): an
error toast, and the title box focused; no dialog and no publish settings.
ARTICLE-COMPOSER-CAPTURE admits one load "with nothing typed", and
CAPTURE-PRESS-UNDER-PROBE-RULE excludes typing into a composer or an editor, so
no capture today may reach the settings `M C44`'s publish and `M C78`'s
visibility need. The question: may one capture load of the article composer
type a placeholder title (nothing in the body), press `Next`, read the publish
settings by closed words, and close them with Cancel or Escape -- never Publish
and never Schedule -- then delete the draft that typing makes (his own, private,
reversible), with STOP-ALL if any control would publish?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): ARTICLE-EDITOR-PRESSES, part (c): ACCEPTED, ATTENDED ONLY. A fixed
placeholder title with no personal content is typed; `Next` is pressed and the
publish settings read; they are closed without Publish; the draft is deleted
and verified absent with part (a)'s `Drafts` read. No Publish press is ever in
the runner's closed press list, and a deletion that cannot be verified is
STOP-ALL and a report. `M C46` rides `M C44`. Rows `M C44`, `M C78`: next step
`CAPTURE:C-MSG7-1`.

### Q-COMMENT-ANALYTICS-METRIC -- a content analytics page whose metric type offers no comments

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 6). Row:
`M C39`. Session 12 opened the metric selector on his content analytics (load
36): a popover titled `Metric type` with two options, `Impressions` and
`Engagements`, and `Show results` -- no comments metric. The only `metricType`
link on the page spells `IMPRESSIONS`. The row's premise, in its address line
("the comments metric needs ?metricType="), is not what the page draws. The
question: under MEASURED-ABSENT-OR-PRECONDITION, is `M C39` MEASURED-ABSENT, or
does it wait on another surface where a per-comment figure might be drawn?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): (question 6, no id given) `M C39` is NOT MEASURED-ABSENT: one
dropdown on one surface does not measure a capability. Under
D6-CAPABILITY-OVER-AFFORDANCE it is re-aimed to a post's own analytics, a
CAPTURE, and kept at GAP. Row `M C39`: next step
`CAPTURE:post-analytics-comments`.

### Q-GROUP-CONTENT-SEARCH-ABSENT -- a search inside groups that neither surface draws

Added 2026-11-27 by lane msg7 (`_audit/2026-11-27-msg7.md`, section 5). Row:
`M C70`. Its plan named two places: a group facet in the content search's All
filters panel, and failing that a group page's own search control (spec F.4 of
`_audit/2026-09-24-lane-s-people-search.md`). Session 12 (load 13): All filters
draws ten facets, none a group (`In group` and `Posted in group` counted 0).
Session 11's member-group page (`tests/fixtures/live11/group_member.html`): one
input, the global search combobox in the page header; no form; no
`role=search`; and no group-scoped search label among its 63 buttons, by keyed
shape. The question: under MEASURED-ABSENT-OR-PRECONDITION, is `M C70`
MEASURED-ABSENT, with the reopener "a capture drawing a group facet or a
group-scoped search control"?

**Answered 2026-11-27 by the orchestrator** (on disk at 12:35 IST as `_TEAM_LEAD_RULINGS1.md`, deleted by lane msg7 as its ack; registration owed at integration 7): GROUP-SEARCH-MEASURED-ABSENT: `M C70` is MEASURED-ABSENT, on the two
surfaces measured -- the content search's All filters (session 12, load 13), no
group facet; session 11's member-group page, no group-scoped search control.
Reopener: a capture that draws a group facet or a group-scoped search control.
Row `M C70`: MEASURED-ABSENT, so it leaves the next-step table.

## 8. Preconditions and purposes

PRECONDITION rows stay GAP; each waits on something he does not hold.

CHEAP AND PRIVATE -- he can make it himself, and nobody else sees it:
- an event he organises, made private or unlisted: `N A13`, `N A14`, `N A15`;
- a group he owns, made private: `N A10`, `N A11`, `N A12`.

CHEAP BUT PUBLIC -- his to make, but others can see it:
- a Service Page: `P H2` to `P H11` (10);
- an article: `M C49`, `M C77`;
- a newsletter: `M C51`, `M C83`, `P L4`; two of them: `M C84`;
- a secondary-language profile: `P D28` (`P D27` makes one).

NOT CHEAP, or not his to make:
- admin rights on a Company Page: `N A1` to `N A5`, `N A7` to `N A9` (8);
- a Top Voice badge: `P B8`, `P K9`;
- an endorsement received: `P E6`, `N 114`;
- a pending invitation to a group or an event: `N 164`, `N 182`;
- a Page-follow invitation he has sent, pending -- his Sent tab draws only its
  people category (session 11): `N 11`, `N 12` (lane readers-net26, 2026-11-26);
- a received invitation carrying a personal note: `N 19` (the same lane);
- a collaborative post or article he is part of: `M C55`, `M C56`, `M C76`;
- a job change to share: `P I16`;
- a name-pronunciation recording, which only the mobile app records: `P A23b`;
- a completed identity verification (a verified name to show): `P A24`;
- a company LinkedIn Learning licence: `P K5`;
- the AI role-play feature, an experiment LinkedIn controls: `J 132`,
  `J 134` to `J 139` (7);
- an AI interview invitation from an employer: `J 142` to `J 145`;
- US Premium (select US subscribers): `J 150`;
- a second account to watch the network from: `P O23`.

PURPOSE rows -- this lane doubts they serve a job-search and
professional-presence tool for his own account. Nothing moves; the
orchestrator rules.

    row(s)                              the doubt
    M C99                               daily games are entertainment
    M C95                               a live video stream, nothing to read
    M C98                               LinkedIn News is general news reading
    M C96                               an image's provenance label
    J 162, J 164, N 198                 feedback to LinkedIn about its own product
    P S10, P B7, P J1, P J2, P J3, P J4 hiring: posting a job, the #Hiring frame
                                        and state
    P L6                                hosting an audio event, existence uncertain

## 9. The instrument: `scripts/check_next_step.py`

It holds both tables to the census on every run, and says what it did not
check:

- every GAP row exactly once, by the shipped walk, and no other row;
- the count equal to the walk's still-GAP figure and to
  `census_completion`'s pinned `gap`;
- each line's slice, direction (the jobs side table for `jobs.md`) and class
  (the write-class table) agreeing with their sources;
- every source resolving: a census id against the census, a tracked fixture
  path against git, and every other form through
  `check_write_classes.source_problems`, the shipped resolver, imported;
- every payload resolving: a CAPTURE id on a queue line that lists the row; a
  BUILD path tracked, or PLANNED in section 6 of this record; a RULING id with
  a `### Q-...` heading in section 7; a SIBLING a lane or a census row; an
  ADMIT address the read boundary refuses TODAY, so a step goes red the day
  its admission lands;
- the queue: every listed row a census row, every row's step matching its
  line's gate, every CAPTURE, TARGET and ADMIT row on some line, and every
  address verdict re-driven through `readonly.is_read_url`.

NOT CHECKED, printed every run: the press-verdict text in the queue (the
generator re-drove it through `press.py`; the checker does not), and the
session cut (the queue's own arithmetic).

SHOWN FAILING BEFORE IT WAS TRUSTED. `scripts/_check_next_step_can_fail.py`
copies the two tables, runs a control over the unplanted copies (GREEN), then
plants one defect per run. Measured 2026-10-10, 11 s:

    A  CAUGHT  N 37: a GAP row today with NO line -- nobody gave it a next step
    B  CAUGHT  P S1: 2 lines, want exactly one
    C  CAUGHT  J 82: phrase does not resolve
    D  CAUGHT  N 169: source N 9999 is not a census row
    E  CAUGHT  P K8: CAPTURE:a-surface-planted-by-the-control has no line in
               the capture queue
    F  CAUGHT  queue in-me-profile: N 9999 is not a census row
    G  CAUGHT  N 104: BUILD:tests/fixtures/planted/no-such-capture.html is
               neither a tracked fixture nor PLANNED

The first run over the real tables was RED, on the instrument's own blind spot: the
shipped resolver reads `.py`, `.md`, `.tsv` and `.json` paths only, so all 27
lines citing a tracked `.html` fixture failed as unparseable. The checker now
resolves a bare `tests/fixtures/...` path itself -- tracked, or it fails --
and passes every other form to the shipped resolver unchanged.
`tests/test_next_step.py` runs the committed check, the control and each of
the seven plants: 10 tests, 19 s. Registered in `_audit/INSTRUMENTS.md`,
section 82.

## 10. Gates run, and what was not run

While `_state/LIVE_SESSION_ON` existed (until about 11:51), every run was
targeted and serial (`-p no:randomly`, no `-n`), the flag checked before each.
After it, the orchestrator's policy of 11:35 held: the tests touched, their
direct importers and the census instruments, longer runs in the background,
the full suite on CI.

    commit    what ran                                          result
    4b78e5f   15 files: the register, the index, the map, the   564 passed, 3 failed: the new
              holds, the corpus guards                          document's three guards,
                                                                repaired before the commit
              the three again, after the repairs                48 passed
              the committed-blob identity test                  1044 passed
    a191fc3   census_completion --check, check_write_classes,   every pin matches; GREEN 387
              check_exclusion_basis, the refused-address        lines; 40 of 40; PASS at 78;
              check, the three derived-view checks              all match
              15 files: the importers of the scripts changed,   392 passed
              the pins edited, the corpus guards
              the committed-blob identity test                  1045 passed
    b6d6bd5   check_next_step                                   GREEN
              tests/test_next_step.py                           10 passed
              the identity test, eight corpus and               1175 passed, 2 failed: a
              derived-view files                                placeholder urn, a drifted map;
                                                                both repaired in dba0bd9
    dba0bd9   the identity test, the derived views, the         1320 passed, 1 failed: the map
              register's numbers and probe controls, the        again, drifted by a table
              corpus guards, the ledger test                    regenerated after the commit
    76ae696   the merge of master 53908ea: census_completion    every pin matches; GREEN 585;
              --check, check_next_step, check_write_classes,    GREEN 387; 40 of 40
              check_exclusion_basis, on the merged tree
              CI run 38035568464 (ci/ ref, 6 jobs, 6m03s)       failure: shard 1, 14 failed --
                                                                the cited-SHA family, which
                                                                cannot resolve old SHAs on a
                                                                ci/ checkout (the orchestrator
                                                                named it at 13:23: not lane
                                                                code); shard 3, 1 failed --
                                                                ours, below; 2975 and 3056
                                                                passed on those two shards
    4d66e1c   the ledger test, the probe budget, the corpus     1188 passed
              guards, the derived views, the committed-blob
              identity test
              the cited-SHA test, locally, with full history    44 passed
              CI run 38036495914 (ci/ ref, 6 jobs, 5m51s)       failure: shard 1 only, 14 failed,
                                                                all in test_a_cited_sha_resolves
                                                                (the ci/-checkout family; 44 of
                                                                44 pass locally); the other
                                                                five jobs green

CI FOUND ONE RED THE LOCAL GATES MISSED: `tests/test_probe_interaction_budget.py`
read `cns.check(table, queue)` in `scripts/_check_next_step_can_fail.py` as
Playwright's checkbox verb `Locator.check`. A false positive -- the scanner
matches the verb, not the receiver -- declared as one in that file's DECLARED
table, with its reason, in the commit after the merge; 8 passed locally.

THE MAP DRIFTED TWICE FOR ONE REASON: the blocker map's reason locator reads
the census side tables as well as the documents, so any table regenerated
after the map makes the committed map stale. It is regenerated LAST before
every commit here.

NOT RUN LOCALLY, and why: the full suite (the 11:35 policy puts it on CI,
where it ran as above); the impact gate's widened run --
`impact_gate.py --against 3c8edc2 --plan-only` selects 77 test files (72 by
impact, 30 corpus-wide, overlapping); this lane ran the ones named above, and
CI ran the rest. Nothing here touched a live page.

## 11. Commits

    4b78e5f  rulings: register the five class rulings of 2026-09-28
    a191fc3  census: P S9 and M C71 EXCLUDED-RULED on PURCHASES-STAY-MANUAL;
             pins re-derived
    b6d6bd5  census: the next-step ledger for all 585 GAP rows, the capture
             queue, and their checker
    dba0bd9  census: register check_next_step (INSTRUMENTS 82), commit the
             capture inventory, two repairs
    b55b1eb  record: lane K's gates and commits; the queue names the
             captures already on disk
    76ae696  merge master 53908ea into lane K: the CI fast lane and live
             session 7's record
    4d66e1c  census: the next-step ledger after a cold review and live
             session 7
    4f28cd3  record: lane K's last gates
    fe119de  merge master b10bde8 (the CI lane's fixes); merged to master
             by the orchestrator, CI run 38037275277 success
    865e57f  rulings: register the orchestrator's rulings on lane K's
             ledger questions
    then     census: the rulings applied (section 12)

## 12. The orchestrator's rulings of 2026-10-10, applied

The orchestrator answered section 7's questions and section 8's purpose list
in `_audit/2026-10-10-rulings-ledger-questions.md`, copied byte-identical
and registered in `865e57f`: fifteen rulings, one route already answered by
lane NP, and one question relayed to the operator. This section applies them.
Sections 3 to 8 describe the ledger as it stood at `4d66e1c`; the tables now
read as below.

### 12.1 The rows moved

    row                                   from  ->  to                       ruling
    N 106, N 108, P N21                   GAP   ->  EXCLUDED-RULED           CONTACT-IMPORT-STAYS-MANUAL
    P N10                                 GAP   ->  EXCLUDED-RULED           SESSION-SURFACE
    P N13, P N14                          GAP   ->  EXCLUDED-RULED           SIGN-IN-CHALLENGES-ARE-HIS
    N 152                                 GAP   ->  EXCLUDED-RULED           SAFETY-REPORTS-STAY-MANUAL
    M C95, M C96, M C98, M C99, J 162,    GAP   ->  EXCLUDED-RULED           OUTSIDE-THE-PRODUCT-PURPOSE
      J 164, N 198, P S10, P B7, P J1,
      P J2, P J3, P J4, P L6
    P A9                                  GAP   ->  COVERED-CANNOT-DELIVER   P-A9-CANNOT-DELIVER
    J 17                                  GAP   ->  COVERED-PROVEN           GEOLOCATION-BY-D6
    J 57                                  GAP   ->  COVERED-PROVEN           CALLER-COMPOSITION-UNDER-D6

Twenty-four rows. Each excluded cell keeps its text and gains the ruling, its
document and the reopener; `_audit/_census/exclusion-basis.tsv` files the 21
under five new families made by the ORCHESTRATOR, op=NO, registered in
`scripts/check_exclusion_basis.py` on each ruling's two anchors: 61 of 61.

THE PURPOSE EXCEPTION, read before moving. Ruling 17 keeps a row whose own
cell shows it tunes his job recommendations or his search. All fourteen cells
were read in full; none shows it. The closest is `N 198`, a verdict to
LinkedIn on people-search results: its cell names the same kind of verdict as
row 163, but where row 163's cell quotes "Your feedback helps us improve job
recommendations", `N 198`'s names no tuning of what he is shown. Row 163 stays
GAP, on the capture of its pair.

### 12.2 The D6 rows, each on its own bar

The order allows a D6 move only where the bar is met today; otherwise the
row's next step becomes the proof.

- `J 17` -- MET. Its one part is the shipped location parameter,
  `linkedin_search_jobs(location=...)`, row 3, COVERED-PROVEN; its cell
  already records that the parameter reaches every documented result set.
  COVERED-PROVEN.
- `J 57` -- MET. The cell's own composition (the tracker's ids into
  `linkedin_job_detail`'s proximity) yields a BOOLEAN, which is whether, not
  who. The composition that delivers WHO uses only proven parts, every target
  supplied by the caller: the tracker tools return the job ids (rows 45-49);
  `linkedin_job_detail` returns the posting's `company_id` (resolved live,
  row 10); `linkedin_people_search_shape(network="F",
  current_company_ids=[...], include_names=True)` returns his 1st-degree
  connections there as people records (`N 84`, `N 81`, `N 25`). The weakest
  part is proven. COVERED-PROVEN; the cell names the composition.
- `J 131` -- NOT MET. WHO is composable, but whether a message costs a credit
  is not readable today: the balance is MEASURED-ABSENT (row 127), and a
  non-connection's Open Profile status is read by no tool. Its next step is
  the proof: the C-P5 capture on a non-connection he names, which records
  whether the composer names a credit. It rides that TARGET line.
- `N 197` -- NOT MET. `linkedin_group_memberships` returns numeric ids and
  `linkedin_group_page(group_id)` verifies that `/groups/<id>/` lands on that
  group (fired on three groups 2026-09-21) -- but the tool deliberately
  publishes no address ("The LANDING is not published"), so no shipped tool
  delivers the row's payload, a link. Its next step is a BUILD (the tool
  returns the address it verified, the caller's own id in the package's own
  template), and then one fire is the proof.

### 12.3 The next steps the rulings set

- Rulings 1 to 3 turn every capture question into a capture: `J 37`,
  `M C14` to `M C17`, `M M28`, `M M34`, `N 86`, `N 90` to `N 92` under
  CAPTURE-PRESS-UNDER-PROBE-RULE; the six article rows under
  ARTICLE-COMPOSER-CAPTURE; `N 76`, `P C8`, `P B3` and `P S4` under
  NO-INDEX-PINNED-JUDGEMENTS. Each joins a capture line in the queue.
- Ruling 6: `N 65` and `N 178` go to lane NP (`SIBLING:lane-NP`), whose
  details-page route needs no scroll.
- Ruling 7: `P N9` takes a capture of the settings index, which shows the
  sessions page's current address before that page's one named admission.
- Ruling 9: `J 82` is a PRECONDITION row: the daily limit, observable only
  when it is reached.
- Ruling 10: `M C43` builds on his post's permalink capture, and `J 110` on
  the Page root's, each returning the text at runtime under the mitigations.
- Ruling 11: `N 82` joins the people-search capture, whose skeleton keeps the
  fixed product label the match needs; no tracked fixture keeps it today.
- Ruling 13: `M M39` stays a question -- the operator's, relayed. It is the
  ledger's one RULING row.
- Ruling 15: `P D29` waits on the certifications editor's admission, with
  `P D13`.

### 12.4 The ledger and the queue now

`_audit/_census/next-step.tsv` holds 561 rows, the counter's gap, after the
rulings and after live session 8 (12.7):

    kind          rows   payload
    ADMIT          152   the address lane A must admit
    SIBLING        151   lane-S 105, lane-U 20, lane-NP 2, another row 24
    TARGET         100   what he must name
    PRECONDITION    58   what he lacks
    BUILD           66   the tracked fixture (or planned skeleton) to build on
    CAPTURE         33   a surface id in the capture queue
    RULING           1   Q-AWAY-MESSAGE, the operator's
    PURPOSE          0   ruled
    total          561

    basis: NAMED 275, INFERRED 208, MEASURED 78

`_audit/_census/capture-queue.tsv`: 94 lines -- 11 that need nothing (13
loads, 2 searches, 33 rows), 11 on a target he names (100 rows), 72 on lane
A's admission (152 rows), and none gated on a question.

SESSION 9 (session 8 has run), the first 40 loads: the eleven open lines first,
by rows per load -- the article composer (6 rows), the people search's
All-filters panel and its fixed labels (5), his own profile's three controls
opened by name and role (4), the composer's scheduled-posts list (4), his
post's reactions control found by name (2), the guarded messaging loads with
the folder and the search box (3 loads, 5 rows), the feed's search box, the
jobs home's alert manager, the first-degree search's Industry and School
pills, and the settings index for the sessions page (1 row each), and a
named thread that reads READ, for its footer (3 rows) -- 13 loads, 2
searches, 33 rows. Then the target lines as he names each target: his named
connections (4 loads, 13 rows), a school (1, 3), an event (4, 11), a
non-connection (3, 8), jobs and alerts (9, 16), a member to block or unblock
(2, 3), Pages (3, 4), a connection to remove (1, 1). Session 9: 40 loads, 2
searches, 92 rows.

SESSION 10: his posts and comments (18 loads, 22 rows) and a group (5, 6),
then seventeen admission lines in rank order (17 loads, 90 rows). Session 10:
40 loads, 118 rows. Sessions 11 and 12 take the named threads and the
remaining admissions.

### 12.5 The pins, each measured on this tree

    census_completion.PINNED   out_of_scope 40 -> 61, achievable 731 -> 710,
                               capabilities_achievable 745 -> 724,
                               adjudicated 186 -> 210, gap 585 -> 561,
                               gap_read 98 -> 92, gap_write 379 -> 365,
                               gap_unknown 108 -> 104, cannot_deliver
                               16 -> 17, delivered_broad 130 -> 132,
                               delivered_strict 105 -> 107, b3_admitted
                               43 -> 41, b3_refused 38 -> 34, jobs_gap
                               108 -> 104, jobs_dir_r 40 -> 38, jobs_dir_w
                               60 -> 58, jobs_admitted 12 -> 10
    write-class split          (16, 37, 334) -> (16, 37, 320), 373 lines
    messaging triage headline  130 {R 16, W 110, R+W 4} -> 126 {R 13,
                               W 110, R+W 3}
    the pointer graph          re-pinned: `P J2` and `P J3` point at `P J1`
                               ("same"), whose verdict moved with its
                               exclusion; both were excluded in the same
                               edit with their own ruling text. 64 pointers,
                               unchanged.
    refused-address GAP rows   78, unchanged (measured)
    side tables                jobs-directions 108 -> 104, read-addresses
                               98 -> 92, write-classes 387 -> 373 lines

### 12.6 Gates

Instruments, on the final tree: `census_completion --check` matches every
pin; `check_next_step` GREEN, 561 = the counter's gap;
`check_exclusion_basis` 61 of 61; `check_write_classes` GREEN, 373 lines;
`check_jobs_directions` GREEN, 104; `check_read_addresses` GREEN, 92;
`measure_pointer_graph --check` passes after the re-pin; the refused-address
check PASS at 78; `build_blocker_map --check`, the register and the index
regenerated and matching.

Tests, serial: the census tables and pins (10 files) 227 passed, in 4m22s --
over the orchestrator's 2-minute local budget; the live session's flag stood
when it started and was gone when it ended; the census-reading guards (4
files) 48 passed in 6 s; the document guards (4 files) 56 passed in 31 s; the
derived views (2 files) 52 passed in 44 s. The register's commit (`865e57f`)
ran the same document and derived-view guards: 99 passed and 1 red, the
asserted-name site pinned there, then 12 passed. The full suite runs on CI.

Master moved to `f8c7392` (lane NP, the CI lane's follow-ups) before the
certification, and was merged: `profile.md` kept master's `P A8` and this
branch's `P A9`; the register kept this branch's fifteen entries and lane NP's
NAMED-PROFILE-DETAIL-PAGES (89 rulings); the derived views were regenerated.
Every pin matched on the merged tree, measured; the guards and the ledger
test, 110 passed; the committed-blob identity test, 1073 passed.

CI run 38040288947 on that merge found two reds of this lane's, in files the
local selection had left out:
- `tests/test_triage_read_gap_rows.py`: its TRIAGE table still listed `P J4`
  and `P N13`, two read rows that left GAP. Their lines are removed, each with
  a comment naming its ruling.
- `tests/test_banked_evidence_is_reachable.py`: `J 57`, banked now, keeps a
  prior reading that cites the linkedin-jobs skill's script by file name, a
  file no clone holds. The citation is reworded in that kept text to say the
  script lives in the skill, outside this repository, and cannot be re-checked
  from a clone -- the repair `P O3` took. The promotion's own evidence (rows
  45-49, 10, `N 84`, `N 81`, `N 25`) is all in the census.
Both files then passed locally: 42 passed. The other four jobs were green.

Master moved again, to `66eb699` (live session 8), and was merged: both sides
had re-pinned `delivered_strict` from 105, and the merged tree MEASURES 111
(session 8's four rows and this lane's two), pinned so; every other pin
matched as merged. CI run 38041159605 on that merge (`824d6b4`): success, 6
jobs, 5m53s. The ledger was then brought up to session 8's captures (12.7):
`check_next_step` GREEN at 561; the ledger test, the prose guards, the index
and the map, 97 passed in 1m45s.

At 15:32 the live lane re-read its session-8 thread capture and found the
composer page (12.7). After a merge of master `16ee59a` (the register at its
fixed point), `M M20`, `M M40` and `M M51` went back to CAPTURE on the thread
footer, and the queue gained that line again. No census state moved, so no
pin did: `census_completion --check` matches every pin, and
`check_next_step` is GREEN at 561.

### 12.7 Live session 8 took the twelve open loads

The live lane's session 8 (re-issued 2026-10-10, merged to master `66eb699`)
ran this ledger's first twelve open loads, as the plan at `4d66e1c` drew them,
and recorded each in its section "3: lane K's block". A capture moves no row;
it changes the next step:

    surface                      session 8 found                      rows -> next
    feed-menus                   an item's menu pressed and kept;     N 37, N 43, N 51, N 153, N 154,
                                 the search box not pressed           N 200 -> BUILD; N 95 stays
    in-me-profile                his profile, raw and skeleton        P D25, P D26, P F1, P K8 -> BUILD;
                                                                      N 76, P C8, P B3, P S4 stay
    search-people-labels         the label reading fired              N 80, N 88, N 89, N 93 -> BUILD;
                                                                      N 82, N 86, N 90-92 stay
    job-posting-panels           one posting, raw and skeleton        J 115, J 124 -> BUILD
    jobs-recommended-feedback    kept                                 J 163 -> BUILD (if the pair is drawn)
    premium-key-skills           kept                                 P S8 -> BUILD (if the chooser is drawn)
    msg-thread-footer            not taken: the receipt guard         M M20, M M40, M M51 stay; the
                                 refused (one conversation read       capture opens a named thread
                                 unread); its lk_thread capture is    that reads READ
                                 the new-message composer page
    own-post-reactions           not pressed: no [aria-expanded]      M C33, M C35 stay, the control now
                                 control named for the menu           found by name (rulings 1 and 3)
    messaging-guarded            the receipt guard refused on the     M M7, M M8, M M9 stay, with
                                 composer's list; /messaging/ not     M M28, M M34
                                 opened
    search-people-first-degree   no Industry or School term drawn     N 26b stays, the pills opened
                                                                      under ruling 1

Nineteen rows move to BUILD on six skeletons in the live lane's
gitignored `_state/live8/`. Each is a PLANNED tracked skeleton; the live lane
names the real paths when it commits them:

    PLANNED tests/fixtures/live8/feed_item_menu_open.html <- live-lane _state/live8/lk_feed-item-menu-open.skeleton.html (N 37, N 43, N 51, N 153, N 154, N 200)
    PLANNED tests/fixtures/live8/in_me.html <- live-lane _state/live8/lk_inme.skeleton.html (P D25, P D26, P F1, P K8; P D25 reads the raw page's anchors)
    PLANNED tests/fixtures/live8/search_labels.html <- live-lane _state/live8/lk_search_labels.skeleton.html (N 80, N 88, N 89, N 93)
    PLANNED tests/fixtures/live8/posting.html <- live-lane _state/live8/lk_posting.skeleton.html (J 115; J 124 reads the raw page)
    PLANNED tests/fixtures/live8/recommended.html <- live-lane _state/live8/lk_recommended.skeleton.html (J 163)
    PLANNED tests/fixtures/live8/keyskills.html <- live-lane _state/live8/lk_keyskills.skeleton.html (P S8)

The eleven lines session 8 did not finish stay CAPTURE, now with the presses
rulings 1 and 3 permit a capture to make, and the queue is renumbered to start
at session 9.

**CORRECTED BY:** `_audit/2026-10-10-lane-b2-network-build.md` -- read against the two skeletons, the feed menu cannot be aimed at an item he names and the search page's first render draws no School, Industry or Keywords control, so `N 37`, `N 43`, `N 51`, `N 153`, `N 154`, `N 200`, `N 88`, `N 89` and `N 93` return to CAPTURE and `N 80` is discharged under D6; and section 5's "unsubscribe" on the newsletter list was counted inside the fixture's header comment, so `N 56` goes to ADMIT.

**CORRECTED BY:** `_audit/2026-11-25-build-p26.md` -- read against their captures, the eleven profile rows this ledger put on BUILD (`P A11`, `P A13`, `P A17` on `live4/editor.html`, `P A14`, `P A15` on `live7/editor.html`, `P A25` on the planned `live1/contact_info.html`, `P D25`, `P D26`, `P F1`, `P K8` and `P S8` on session 8's skeletons) have nothing to build on; they go to three questions (`Q-EDITOR-TYPEAHEAD`, `Q-ABSENT-ON-HIS-ACCOUNT`, `Q-OWN-PROFILE-SCROLL`), one admission and two captures, and `P L2b` moves to COVERED-UNFIRED on the reader built for it.

THE THREAD FOOTER, as the live lane re-read it at 15:32. Its session-8
capture `lk_thread` is the NEW-MESSAGE COMPOSER page, not a named thread's
footer: the receipt guard refused to open the thread, because one
conversation read unread -- its row carries LinkedIn's unread markers, the
first capture of that markup. So the composer's footer controls it recorded
(attach image, attach file, the GIF and emoji keyboards) are the composer's,
and say nothing of a thread's footer. `M M20`, `M M40` and `M M51` stay
CAPTURE on the thread footer, behind the receipt guard at 0 unread, on a
named thread that reads READ.
