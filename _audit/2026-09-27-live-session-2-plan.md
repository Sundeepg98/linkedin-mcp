# Live session 2 -- the plan, written offline

The live lane, 2026-09-27. **OFFLINE PLAN: nothing here has loaded a page,
attached to a browser or pressed anything.** Session 2 runs only on the
orchestrator's separate go, and its outward block only after he has seen each
resolved identity once.

What it covers, as the order of 2026-09-27 16:45 set it: every NEEDS-CAPTURE
spec on master (lanes S, D, L5's merged part, L7, Y2's re-harvest, and the
setting admitted as item (a) of the live lane's session-2 preparation), plus
the fires of BUILT-UNFIRED rows that need no target. Captures first, inside
the budget. Every step names its loads, the ruling it rests on, and whether it
needs the operator.

**THE HARNESS IS `scripts/_probe_live_lane_session_2.py`**, built as item (c)
of the same preparation and held by `tests/test_live_lane_session_2_harness.py`.
Every step below is one of its keys, except the outward block, which runs as
tool calls. The record of how the plan was built -- the inventory, the offline
readings it rests on -- is the session-2 preparation section of
`_audit/2026-09-23-live-lane-session-1.md`.

## 0. What every step runs under

| rule | what it does to this session |
|---|---|
| `LIVE-BUDGET-40-LOADS` | 40 LinkedIn page loads, serial, 20 s or more apart, one driver. The harness's ledger (`_state/live2/ledger.json`, gitignored) counts every load any key makes -- a shipped tool's own included -- refuses the 41st BEFORE it navigates, and waits out the spacing across processes; a driver lock refuses a second harness process. The outward block's tool calls are counted by hand into the same total (section 2, block 4). |
| `D1-SEARCH-AS-READS` | five test searches in the session. The harness refuses a sixth `/search/` load before it navigates. Six are wanted (lane S, J.6); section 1, D-3, trades one. |
| `PAGE-MAY-VETO-NEVER-SUPPLY` | every address is a constant or a package composer filled from the caller's `--item`; a reading may only refuse (the group, post and attendee vetoes). `tests/test_navigation_is_never_derived.py` holds no entry for the harness. |
| `PEOPLE-DATA-MITIGATIONS` | mitigation 3, as lane S read it for its own specs (J.6): every page is reduced to a SKELETON before anything is written, except his own settings page, which draws no other person and is captured raw. Section 1, D-2. |
| `OUTWARD-ACTS-NEED-THE-OPERATOR`, `OPERATOR-NAMES-THE-TARGET` | nothing outward runs from the harness. The outward block fires only at targets he named, each shown to him once. Targets are named here by ROLE only; their names live in the gitignored identity key and nowhere in this repository. |
| `CREDENTIAL-SETTINGS-NEED-THE-OPERATOR` | never live-proven: section 3. |

The environment: `LINKEDIN_CDP_ATTACH=1`, `LINKEDIN_CDP_PORT=9224`,
`LINKEDIN_MIN_INTERVAL_S=20`; the harness refuses to run without the first and
the third. A run killed before its end leaves the driver lock
(`_state/live2/driver.lock`, gitignored) behind; it is deleted by hand, and
only after checking that no harness process is alive. This lane never starts, restarts or closes the Chrome on 9224. L1's
control-page bracket (two loads a run, and a jobs search into his history) is
not used, as in session 1: the harness reads the auth wall and the challenge
phrases on every page it opens, and either stops the session.

## 1. Decisions before the go

Each is the orchestrator's unless it says his. A recommendation is mine.

* **D-1. The More press on his profile (`in_me_more`).** Lane D's LQ-1
  governs it by the probe rule; the live lane's Part 2 (c) routed the same
  top-card overflow, for `N 76`, through an index-pinned judgement that has
  not been decided. **They are one control, measured offline today:** the
  session-1 capture of his profile draws exactly ONE
  `button[aria-label="More"][aria-expanded="false"]`, page-wide and in main.
  Recommendation: fire LQ-1 as specified -- two openings, attributes only,
  Save to PDF found by comparison inside the page, nothing inside the menu
  pressed. The same openings count the items matching `N 76`'s four needles,
  which is the evidence the undecided judgement lacked.
* **D-2. Raw captures of pages of people.** Whether a gitignored raw capture
  is a store under mitigation 3 is decided nowhere. The harness writes
  skeletons for every page but his settings page. Cost of that choice,
  stated: a skeleton keeps tags, classes, roles, closed ARIA states,
  LinkedIn's own path words and its own UI words, so every reader's
  selectors still run on it; it drops every other label, so the completeness
  harvester's control-label axis (lane Y2, section 9) sees only LinkedIn's
  own words on these captures, and a label nobody has measured yet -- a menu
  item outside the harness's vocabulary, the ON form of "I'm interested"
  (`P I15`) -- is kept as its shape and count, never its words. Recommendation:
  keep skeletons, and rule an exception by name where a lane needs one
  unknown label.
* **D-3. The search trade.** Six searches wanted, five allowed. Fired:
  `N 104`, `N 161` (captures), `N 94`, `N 84`, `N 87` (the shipped people
  search). Deferred: `N 179` to session 3; `N 85` to session 3 regardless,
  since it needs a member he names.
* **D-4. The organisation ids.** `N 84` and `company_people` take the
  organisation `linkedin_job_detail` resolves on a posting that `J 39` or
  `J 158` returned (one load). `N 87` needs a different one: the numeric id of
  either organisation page session 1 captured, read offline (no load), or a
  second `job_detail` (one load). Either way the orchestrator confirms, before
  the fire, that neither organisation is his current or past employer -- D1
  forbids a value that identifies him.
* **D-5. The outward words -- HIS.** `M M10`: "Testing a LinkedIn tool I'm
  building. Please ignore this message." unless he changes it. `M M17`: the
  same words with one emoji he names (default U+1F44D). Typed exactly as
  granted; the send gate refuses a changed word before Send.
* **D-6. The identity shown once.** For the reply target, the preview's
  `who_this_would_reach` is what he confirms: since lane G, a people record,
  as the ruling `PREVIEW-NAMES-THE-RESOLVED-TARGET` has it -- the name and headline the page
  draws for the conversation he named, sanitised, marked untrusted, returned
  at runtime and never written; the receipt keeps only the thread id he
  supplied. The confirm must follow the preview within 120 s, so if his
  answer comes later the preview is taken again: one load, budgeted.
* **D-7. The Me menu (`me_menu`, lane Y's item 9).** A press on his own view,
  the discovery curve's item; riding on his profile's page, no load.
  Recommendation: fire.
* **D-8. LQ-4's optional synthetic download.** It writes a file into his
  Downloads folder; not built. Recommendation: skip -- the attach check's
  order, acknowledgement and folder readings stand without it.
* **D-9, HIS. Items only he can supply**, asked before the session: a thread
  whose last message is his (`M M49`'s fallback), a Recruiter InMail he has
  read (`M M47`), a conversation in which he sent an attachment (`M M14`,
  `M M15`, `M M18`), a conversation he has starred (`M M30`), a school that is
  not his campus (`N 99`), an event he can open (`N 184`). Whatever arrives
  runs in the reserve (block 5); the rest goes to session 3.

## 2. The steps, in order

Loads are the most a step may spend; the running total is the ceiling's
arithmetic. A rider presses on the page the step before it left open and
loads nothing.

### Block 0 -- the attach, zero loads

| step | key | rows | loads (total) | rests on | needs him |
|---|---|---|---|---|---|
| 0.1 | `attach_check` | `P C8`, enabling (lane D, LQ-4) | 0 (0) | `LIVE-BUDGET-40-LOADS` (spends none) | no |

The attach runs in a child process with the driver's protocol log on; only
the download-behaviour lines are kept, as they arrive -- every other line
names his tabs. Pass: `allowAndName` with a path, then `default` with none,
both answered, the library's temporary folder there during the attach and
gone after, and the reset record restored. The orchestrator's order of
2026-09-27 says the session is no longer gated on this; it is still the
first thing observed, and a FAIL is reported, not a stop. The filter was
proven on synthetic protocol lines only: if the driver writes its log in
another form, the check reads zero events and says `FAIL-ORDER`, which
means LQ-4 was not observed -- not that the hazard is back.

### Block 1 -- captures that need nothing from a fire

| step | key | rows | loads (total) | rests on | needs him |
|---|---|---|---|---|---|
| 1.1 | `setting` | `P A8`, `A11`, `A13`, `A17`, `A19`, `A21`, `P B9` (condition 1) | 1 (1) | `ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`, applied; `SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED` | no |
| 1.2 | `setting_offline` | the reader's validation | 0 (1) | the same | no |
| 1.3 | `in_me` | `N 76`, `P J4`, `P D28`; `P F1`, `P H11`, `P K8`, `P D26` off the capture | 2 (3) | `IN-ME-NO-BLANKET-BAR` | no |
| 1.4 | `in_me_more` (rider) | `P C8` (LQ-1); `N 76`'s needles | 0 (3) | the probe rule; D-1 | no |
| 1.5 | `me_menu` (rider) | lane Y item 9 | 0 (3) | D-7 | no |
| 1.6 | `activity_all` | `M C85` | 1 (4) | `SHARE-AND-POLL-PROOFS-OWN-POSTS`; `FEED-CONTENT-READ-RULING` (counts only) | no |
| 1.7 | `followers` | `P L2b` | 1 (5) | lane L1's follower-list admission | no |
| 1.8 | `own_post` | `M C29`, `M C42` | 1 (6) | `FEED-CONTENT-READ-RULING`; `VIEW-SWITCH-PRESS-RESTORED` for the later sort press | no |
| 1.9 | `m43` | `M M43`; lane L5's C1 rides | 1 (7) | `OWN-INBOX-READS-COVERED-BY-B` | no |
| 1.10 | `compose_presses` (rides on 1.9's page) | lane L5's C8, C9, C5: `M M7`, `M M8`, `M M9`, `M M28`; `M M22`, `M M27`, `M M29`, `M M31`; `M M16` | 0, or 1 if the page moved (8) | `OWN-INBOX-READS-COVERED-BY-B`; the probe rule | no |
| 1.11 | `n104` | `N 104` | 1 (9); search 1 of 5 | `D1-SEARCH-AS-READS`, `D2-SEARCH-VERTICALS-WIDENED` | no |
| 1.12 | `n161` | `N 161` | 1 (10); search 2 of 5 | the same | no |

What each reads, beyond its capture:

* **1.1-1.2, the setting.** The (b) reader live: the reading, the one named
  control, and whether its state sits in the markup or only in the checked
  property -- a capture cannot hold the second. Then the same reader over its
  own capture, in a local headless Chromium with the network off and no
  script run: `AGREES` is the validation the order asked for before any of
  the six edits fires. `STATE-NOT-IN-MARKUP` means the capture cannot answer
  and the live reading stands alone -- the orchestrator's call. Anything else
  stops the six. A redirect stops the run: the other candidate gets its own
  admission then, not now.
* **1.3, his profile,** through the package's self-profile loader
  (`isSelfProfile` retried once on absent, never on false): the main-scope
  `[aria-expanded]` controls by structure, and the section words `P F1`,
  `P H11`, `P K8` and `P D26` ask about, counted in main.
* **1.4,** two openings of the top card's More: per item, its tag, role,
  ARIA attribute names, `data-view-name`, whether a `componentkey` is set,
  href or button; the Save-to-PDF item found by exact comparison inside the
  page, and whether its attribute handle is the same across both openings.
  Escape; the menu must close.
* **1.8, one of his posts WITH comments.** Offline today: session 1's
  capture of his newest post draws an empty comments list (no comment item,
  no "N comments" phrase), while his profile's rail capture draws four
  "N comments" phrases. So the lead names one of those posts with
  `--item activity=` from the rail capture, and the harness vetoes any id
  that is not among the rail's authorship-established items.
* **1.9-1.10, the composer,** which draws the conversation list and opens
  none: `M M43` banks on `opened_a_conversation.opened` false with rows
  rendered; C1 is the capture of any unread row it draws. Then, on the same
  page, the folder menu (C8), ONE READ row's options menu (C9) and the GIF
  picker (C5) -- each exactly one trigger, a click, the menu read by
  attribute and by LinkedIn's own words, Escape, and the count of message
  events re-read after each: any message event is a conversation opened, and
  stops the session. The presses ride on 1.9's page only inside the same
  invocation (`--only m43,compose_presses`); every run closes its own tab at
  the end, so a later run loads the composer once.
* **1.11-1.12,** lane S's words, "robotics" and "open source": the result
  cards, and whether each links a numeric id or a slug, by shape.

### Block 2 -- fires of built-unfired rows that need no target

| step | key | rows | loads (total) | rests on | needs him |
|---|---|---|---|---|---|
| 2.1 | `m33` | `M M33` | 2 (12) | `OWN-INBOX-READS-COVERED-BY-B` | no; if a rendered row reads unread the tool refuses, spending 1: he reads it himself first |
| 2.2 | `m49` | `M M49` | 2 (14) | the same | no (its fallback needs him: D-9) |
| 2.3 | `j18` | `J 18`; `J 37` rides | 1 (15) | none cited: a read of his own account | no |
| 2.4 | `j39` | `J 39` | 1 (16) | none cited: a read of his own account | no |
| 2.5 | `j158` | `J 158` | 1 (17) | the orchestrator's delegated call on its state | no |
| 2.6 | `n132` | `N 132`; `P G7`'s tool-level fire | 1 (18) | `D6-CAPABILITY-OVER-AFFORDANCE` | no |
| 2.7 | `notifications` | `N 20`, `N 45` | 1 (19) | `NOTIFICATIONS-UNREAD-SPEND` (the load clears his unread badge) | no |
| 2.8 | `n23` | `N 23` | 2 (21) | none cited: a read of his own account | no |
| 2.9 | `n94` | `N 94` | 1 (22); search 3 of 5 | `D1-SEARCH-AS-READS` | no |
| 2.10 | `job_detail` | an organisation for 2.11 and 3.3; `J 124`, `J 115`, `P M12` off its capture | 1 (23) | none cited: any posting | no |
| 2.11 | `n84` | `N 84` | 1 (24); search 4 of 5 | `D1-SEARCH-AS-READS`; D-4 | no |
| 2.12 | `n87` | `N 87` | 1 (25); search 5 of 5 | the same | no |
| 2.13 | `memberships` | the ids block 3 is vetoed against | 3 (28) | none cited: a read of his own account | no |

`job_detail` takes a posting the lead names from 2.4's or 2.5's result, and
writes the organisation it resolves; `n84` and `n87` take organisations only
as `--item`. The choosing is the caller's -- which is what
`PAGE-MAY-VETO-NEVER-SUPPLY` draws for every tool. `memberships` costs three
loads, not one: the tool brackets the Groups page with the feed at both ends.

### Block 3 -- captures that need a fire's result

| step | key | rows | loads (total) | rests on | needs him |
|---|---|---|---|---|---|
| 3.1 | `group_home` | `M C70` | 1 (29) | none cited; vetoed unless 2.13 returned the group as a membership | no |
| 3.2 | `group_members` | `N 165`, `N 177` | 1 (30) | `MEMBER-ROSTERS-AS-BOUNDED-READS`; the same veto | no |
| 3.3 | `company_people` | `N 102`, `J 108` | 1 (31) | `MEMBER-ROSTERS-AS-BOUNDED-READS`; D-4 | no |

### Block 4 -- OUTWARD, firing only after he has seen each resolved identity once

Not harness keys: tool calls with `LINKEDIN_ENABLE_WRITES=1`, which the
preview needs as well as the confirm. Their loads are added to the ledger's
total by hand.

| step | call | target, by role | rows | loads (total) | rests on | needs him |
|---|---|---|---|---|---|---|
| 4.1 | `linkedin_send_reply` preview | the brother's existing thread, its id supplied by him | `M M10`; lane L5's C3 (a) and C7 ride on the preview | 1 (32), +1 if the preview is re-taken (33) | `OPERATOR-NAMES-THE-TARGET`; `WRITE-CLASS-B`; `PREVIEW-NAMES-THE-RESOLVED-TARGET` (D-6) | YES: the thread, the words, and the identity once |
| 4.2 | the same call with its `confirm_token`, within 120 s | the same | `M M10` | 2 (35) | the same | YES |
| 4.3 | `linkedin_send_reply`, preview then confirm, with the emoji | the same thread | `M M17` | 3 (38) | `D6-CAPABILITY-OVER-AFFORDANCE`; `OPERATOR-NAMES-THE-TARGET` | YES; a changed emoji refuses before Send, and is not retried |

Budget after block 4: at most 38 of 40, five searches of five. Two loads
stay in reserve for the next block or an anomaly's re-read.

The other named targets, by role, and why none of them fires in session 2:

* **a 1st-degree connection he named:** `N 85` takes the member token
  `linkedin_connections` returns for that connection -- a sixth search, and a
  member named, so session 3; the endorse and recommend classes wait on lane
  L8, which is not on master.
* **the two others he named:** a connection invitation or a message through
  a profile (`N 1`, `M M1`, `M M6`) waits on lane L5's named-person route,
  which is on its branch and not on master.

Each will be resolved to one exact profile link and shown to him once --
name, headline, link -- before it fires, as the standing plan says.

### Block 5 -- items only he can supply (D-9), in the reserve or session 3

| key | rows | loads | rests on |
|---|---|---|---|
| `thread` | `M M47` (C2), `M M14`, `M M15`, `M M18` (C3 b), `M M30` (C10), `M M49`'s fallback | 2 each | `OWN-INBOX-READS-COVERED-BY-B`; the tool refuses while any rendered row reads unread |
| `school_people` | `N 99`, `N 100`, `J 112` | 1 | `MEMBER-ROSTERS-AS-BOUNDED-READS` |
| `event`, then `event_attendees` | `N 184`; `N 188`, `N 189` | 1, then 0-1 | the same; the second vetoed unless the first drew the event's own attendees link |
| `job_detail`, on a posting at an employer he has already signalled interest in | `P I15` (lane L7's C6), the prerequisite of `P I14` | 1 | the orchestrator's call that the undo exists before the act; D-2, since a skeleton cannot learn a label nobody has measured |

## 3. Never, or not this session

**`CREDENTIAL-SETTINGS-NEED-THE-OPERATOR` -- never live-proven unless he
names them:** the seven credential and recovery controls, `P N4`, `P N5`,
`P N6`, `P N7`, `P N8`, `P N10` and `P N11` -- `P N10`, signing out of
sessions, is one of the seven and would end this server's own session.
`P A24` and `P N14` cite the same ruling. No harness key loads a settings
page but item (a)'s, and that one only to read; no key writes a setting.

**Blocked -- no session can bank them today:** `J 121` (the percentile is
behind a press not built), `J 122` (a reader change), `J 128` (the recipient
gate refuses before any send), `M C1` (the tool refuses: the audience is
unread), `P I14` (lane L7's C6 capture and a `P I15` build with a tested
restore come first).

**Need an admission before any load:** lane L7's C3 (`P D24`, `P H1`), C4
(`P G2`), C5 (`P I13`) and C2's second stage (`P A26`-`A29`). Lane Y2's
re-harvest rows that name an address -- `M C98`, `M C99`, `N 199` -- are
refused with no pattern: admissions, not loads. Its four unnamed
connection-notification toggles wait on "the first capture of the
notifications page" (its section F.1) -- read here as the notification
SETTINGS the toggles sit on, a settings category page the boundary refuses;
if the words mean the notifications list itself, session 1 captured it and
the question is offline.

**Conditional or unspecified:** `J 136`-`J 138` (only after the role-play
flag leaves control), the jobs All-filters press (not established as
sanctioned), `N A3` (no method), lane L5's C4 (optional), `N 133` (partly
superseded; its per-option counts need a reader nobody has built), `N 178`
(not in session 2 by its own text).

## 4. Session 3, named and not scheduled here

* **The six intro edits and `P B9`**, about 8 to 12 loads each by lane L7's
  estimates -- beyond what session 2 leaves. They fire only after block 1's
  `setting_offline` reads `AGREES` (or the orchestrator accepts
  `STATE-NOT-IN-MARKUP`), with his setting reading OFF when each edit reads
  it again before the change, and for `P A8`-`A21` with values he picks.
* `N 179` and `N 85` (D-3); `N 93`, whose spec does not say whether it
  spends one of the five searches.
* Lane L5's C6 -- the menu on one of his own messages, under an hour old: the
  reply of 4.2 makes one, but the hover-revealed press is not built.
* `N 76`'s press (after D-1), `P C8`'s download (lane D's LQ-2, after its
  press is sanctioned and built), `M C85`'s poll reader (if 1.6 finds a poll
  of his), `J 107`'s fire (its build first).
* Lane L8's outward classes and lane L5's named-person route, once each is
  on master.
* The outward rows whose target he has not named: `J 103` and `N 46`,
  `J 104` and `N 48`, `N 47` (an organisation he names), `M C25` and `M C32`
  (an item he names), `N 1` (a member on his own profile's rail he names).

## 5. Zero-load items

* **`M C29`, `M C42`, answered in part offline today** (1.8 above): his newest
  post draws no comment; his profile page, where the rail is, draws four
  comment counts.
* **The More control is one control** (D-1): measured on session 1's
  capture, no load.
* Lane L7's C2 first stage may be answerable from session 1's contact
  capture and lane Y2's drawn note (DERIVED by the inventory, not checked
  here), by the owners.
* Five address-table lines still gate MEASURE on pages session 1 captured
  (`P A25`, `P L1`, `P L8`, `M C38`, `M C48`): offline readers, the owners'
  work.
* After the session: the setting's capture becomes the reader's committed
  fixture, sanitised, in place of the synthetic worlds.

## 6. Found while planning, for the owners -- nothing moved here

* `M C32`'s cell says never fired on a real target, while the react spec in
  `linkedin_server/writes.py` records a reaction left on one of his items on
  2026-09-03.
* `J 128` is COVERED-UNFIRED on the tool and gate that hold `M M1` and
  `M M2` at COVERED-CANNOT-DELIVER.
* `P B9`'s aim rests on the orchestrator's 09:15 ruling of 2026-09-24,
  which is not in the register.
* Lane D's LQ-2 says it moves `P C8` from COVERED-UNFIRED; the cell reads
  GAP, and its own text puts the press build first.
* `P I15`'s cell still says C6 is lifted by the first supervised `P I14`
  press, which lane L7's integration reversed.
* `P G7` is COVERED-PROVEN while lane D's LQ-3 says `N 132`'s call gives it
  the tool-level fire it has stood without.

## 7. The count

    block   steps                                   loads, at most   searches
    0       the attach                                     0             0
    1       captures needing nothing (12 steps)           10             2
    2       no-target fires (13 steps)                    18             3
    3       captures needing a fire (3 steps)              3             0
    4       outward, after the identity (3 steps)          7             0
    -----                                                 --             -
            planned                                       38             5 of 5
            reserve                                        2   (D-4's second posting would spend one)
    5       items only he supplies                  in the reserve, else session 3

**Against the inventory's 46 open capture specs** (its entries A01-A46,
counted, each once):

    captured in blocks 0-4                27   A01, A03 (its part a), A05, A07,
                                               A08, A09, A16, A19, A20, A22, A23,
                                               A25, A26, A28, A31-A40, A42, A43,
                                               A45
    his items, block 5                     6   A02, A10, A15, A17, A27, A29
                                               (and A03's part b)
    session 3                              3   A06 (not built), A24 (the sixth
                                               search), A41 (its search cost
                                               is unstated)
    an admission first                     4   A11 (stage 2), A12, A13, A14
    optional, superseded, conditional      6   A04, A18, A21, A30, A44, A46
    or unspecified
                                          --
                                          46

A03's part a and A07 ride on block 4's preview: if he declines the outward
block, they move with it.

**Against the 36 built-unfired rows** (census state COVERED-UNFIRED):

    fired in session 2                    15   the 11 that need no target
                                               (J 18, J 39, J 158, M M33, M M43,
                                               M M49, N 20, N 23, N 45, N 94,
                                               N 132), N 84 and N 87, and
                                               M M10 and M M17 in block 4
    session 3                              8   the six intro edits and P B9
                                               (section 4), N 85
    outward, target not named             11   J 103, J 104, M C25, M C32, N 1,
                                               N 46, N 47, N 48; and J 128,
                                               M C1, P I14, blocked (section 3)
    blocked reads                          2   J 121, J 122 (section 3)
                                          --
                                          36
