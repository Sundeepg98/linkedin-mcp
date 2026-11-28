# Live session 14 -- the live lane's record, written as it runs

**2026-11-27. Lane `live-s13`, branch `live-s13`, built on the merge of master
`8fce32c` (integration 7 and masterfix7) into the branch, at `db70dc7`. PHASE
A, OFFLINE: zero LinkedIn page loads, no browser started or attached, port
9224 untouched, the live-session flag never raised.** PHASE B runs only on the
orchestrator's GO: a `_TEAM_LEAD_GO.md` at this worktree's root that names
exactly the pins of the latest READY. Session 14 is ATTENDED, so the GO comes
when the operator is at the console. Its record continues below READY, in this
file.

It runs under the lane standing rules (gitignored) and the orders of
2026-11-27 23:02 (`_TEAM_LEAD_S14.md`, deleted as the ack before the merge
commit). The hard limits:

- at most 40 loads a session, each at least 20 s apart, one live lane;
- at most 5 D1 searches a session, and at most 3 loads per tool call;
- one 40 per trailing 12 h on the account, shared with the pipeline, under
  BUDGET-ONE-ACCOUNT-40: one pinned ledger, and every load recorded before it
  is made.

Its method is session 13's (`_audit/2026-11-27-live-session-13.md`) and
session 12's (`_audit/2026-11-26-live-session-12.md`).

**Every person is named by ROLE. No name, slug, member id, urn, organisation,
keyword value, place value or absolute path is written here.** Evidence
classes: VERIFIED means measured by an instrument this lane ran; DERIVED means
computed from VERIFIED figures; UNVERIFIED means not measured.

---

## 0. What disk said that the orders did not

1. **J 9 is the Easy Apply key, not All filters.** The orders say "J 9 (All
   filters) gets its own line". On disk, J 9 is "Filter: Easy Apply only"
   (blocker map, JOB-SEARCH-PARAMS), and All filters is J 15. Session 13
   captured J 15's panel (in page, no navigation). It did not capture J 9,
   because the panel did not close before the toggle was reached. This lane
   reads TOGGLE-FIRST as it is plainly meant. The Easy Apply round trip
   (J 9) goes FIRST, on one search plus its two re-queries. The All filters
   press comes after it, as its own step, so a `did_not_close` there can no
   longer strand the toggle. That press reads the panel's close-control
   spelling, which is session 13's finding 2.
2. **The queue's `loads` column under-counts four lines.** It counts a press
   that may load a document as no load. Ruling Q2 and the 3-per-call ceiling
   count such a press. So this plan budgets each line's MOST loads:
   - rank 1: Drafts may navigate (+1);
   - rank 6: the receipt guard's two loads, and the search's Enter may
     navigate (+1);
   - rank 23: the switch and the switch back may each navigate (+2);
   - rank 31: its press rides E5's call (+1 on that call).
3. **E1 is not in the merged queue, and E5 decides the block.** Every self
   line's session cell reads "after SELF-LOADER (integration 7) and E5". E5
   lands through the shipped loader, `server._goto_self_profile_asserted`,
   which now waits for the client-side rewrite. So E5's own landing is the
   live proof. If it does not prove his root, every line that rests on it
   drops, with the reason. Session 12 ran the same block on E1.
4. **Rank 103 (`/in/me/edit/intro/`): its landing only.** The orders say
   "Record where `/in/me/edit/intro/` lands". The line's typing step
   (EDITOR-TYPEAHEAD-SANCTIONED) needs the editor to serve, and that is
   UNVERIFIED. So this session spends one load on the landing alone. If the
   editor serves, the typing is queued for a later session with its own
   checks.
5. **The pinned ledger at 23:32 IST: 7 loads in the trailing 12 h, 33
   free.** These are session 13's 7, the newest from 20:10. They leave the
   window from 08:02 to 08:10 IST tomorrow. After that, 40 are free (VERIFIED,
   `budget.usage` through the pin).
6. **The harness changed under the merge.** `scripts/_probe_live_lane_session_2.py`
   now waits on the self alias in `_in_me_more` (prof7's
   SELF-LOADER-WAITS-FOR-THE-REWRITE). So its pin is new for session 14.
   `scripts/people_gate.py` did not change.

## 1. The plan: the merged queue's session-14 lines, ordered by `rows_per_load`

The 27 lines integration 7's critic derived are ranks 1, 2, 23, 24, 26, 30,
31, 64, 67, 68, 69, 95, 102, 109, 111, 115, 144, 145, 147, 149, 150, 151,
154, 156, 157, 158 and 161. Each is carried here, plus the lines they rest on
or the orders name:

- rank 3, E5 his root, which every self line follows;
- rank 40, E23's skill form, which rank 102 reads;
- rank 71, the skill insights, off E5's index;
- rank 117, E18 and E19, per the orders;
- rank 132, C-SRCH-3a, under TOGGLE-FIRST;
- rank 6, the inbox, under UNREAD-IS-HIS;
- rank 103's landing, per the orders.

The order follows the queue's own `rows_per_load`. Within a tie, a line whose
press can stop its phase comes later. Three lines are put in 14b by design,
each for a named reason:

- rank 2 needs 3 searches, and C-SRCH-3a takes 3 of 14a's 5;
- rank 149's delete must be aimed at the Drafts list, which rank 1 captures
  first. A round trip needs its inverse proven first;
- rank 151 is the last by `rows_per_load` (0.33), and its unsave is an
  inverse to prove first.

Each phase has two load figures:

- **MOST loads** is the runner's own `PHASES` figure, the bound its preflight
  refuses on. It counts every goto (his root's shipped loader may load twice),
  every press that may navigate, and one unexpected document a press may load.
  Such a document is counted by hand, and it stops the phase.
- **EXPECTED loads** counts the gotos only, plus the presses meant to
  navigate. It is what the phase spends if nothing navigates unexpectedly and
  the loader proves his root at its first attempt.

**UNREAD-SKIPPED** (the orchestrator, `_TEAM_LEAD_UNREAD.md`, 2026-11-27
23:12): the operator left read-or-skip to the orchestrator, who ruled
`UNREAD_ANSWER=skip`.

- M M28 and M M54 DROP: "his unread message is not opened by automation".
- So does M M34: it rides the same `/messaging/` load, whose landing opens a
  conversation LinkedIn chooses.
- Phases 7 and 8 are not in the runner's table. Their code stays, for its
  checks.

The freed loads go to the next row by `rows_per_load` that needs no new
ruling, item or press: rank 34, his featured page (3.0: P G4, P G5, P S1).

| # | phase | rank | rows | most | expected | searches | cumulative most | items | attended |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `profile` (E5) with rank 31's press | 3, 31 | 19 + 4 | 3 | 1 | 0 | 3 | -- | yes (31) |
| 2 | `recommendations` | 23 | 13 | 3 | 1 | 0 | 6 | -- | -- |
| 3 | `otw_editor` | 24 | 13 | 3 | 1 | 0 | 9 | -- | yes |
| 4 | `c_srch_3a` (TOGGLE-FIRST) | 132 | J 9 (+ J 15's close control) | 3 | 1 | 3 | 12 | `job_kw` | -- |
| 5 | `newsletter_form` | 150 | 3 | 3 | 1 | 0 | 15 | -- | -- |
| 6 | `discovery` | 161 | 3 | 1 | 1 | 0 | 16 | -- | -- |
| 7 | `featured` (the freed loads) | 34 | 3 | 1 | 1 | 0 | 17 | -- | -- |
| 8 | `manage_syncing` | 158 | 2 | 1 | 1 | 0 | 18 | -- | -- |
| 9 | `skill_form` (E23) | 40, 102 | 2 (+ P S8's choice) | 1 | 1 | 0 | 19 | `skill` (named off E5) | -- |
| 10 | `intro_landing` | 103 | the landing | 1 | 1 | 0 | 20 | -- | -- |
| 11 | `contact_info` | 30 | 4 | 3 | 1 | 0 | 23 | -- | yes |
| 12 | `article_drafts` | 1 | 1 | 3 | 2 | 0 | 26 | -- | -- |
| 13 | `invitation_filter` | 26 | 1 | 2 | 1 | 0 | 28 | -- | -- |
| 14 | `permalink_menus` | 95 | 2 | 3 | 2 | 0 | 31 | `member_post`, `page_post` | -- |
| 15 | `key_skills` | 102 | 1 | 1 | 1 | 0 | 32 | -- | yes |
| 16 | `connections_pills` | 109 | 1 | 2 | 1 | 0 | 34 | -- | -- |
| 17 | `creator_hub` (+ P L8's re-aim) | 111 | 1 | 2 | 1 | 0 | 36 | -- | -- |
| 18 | `notifications_card` | 115 | 1 | 2 | 1 | 0 | 38 | -- | -- |
| 19 | `self_variant` (E18, E19) | 117 | 2 | 2 | 2 | 0 | 40 | -- | -- |
| 20 | `learning_goal` | 144 | 1 | 3 | 1 | 0 | 43 | -- | yes |
| 21 | `alert_row` | 145 | 1 | 3 | 1 | 0 | 46 | -- | yes |
| 22 | `learning_saved` | 147 | 1 | 1 | 1 | 0 | 47 | -- | -- |
| 23 | `post_analytics` | 154 | 1 | 1 | 1 | 0 | 48 | `own_post` (he names it) | yes |
| 24 | `search_history` | 156 | 1 | 1 | 1 | 0 | 49 | -- | -- |
| 25 | `download_data` | 157 | 1 | 1 | 1 | 0 | 50 | -- | -- |
| 26 | `skill_insights` | 71 | 1 | 1 | 1 | 0 | 51 | `skill_index` (named off E5) | -- |
| 27-30 | `self_press` x4 | 64, 67, 68, 69 | 1 each | 3 each | 1 each | 0 | 63 | rank 69: his profile id, in a gitignored items file deleted once read | yes |
| -- | `root_settle`, only while a compare of his root is deferred | -- | -- | 2 | 1 | 0 | -- | -- | -- |

The 30 phases total 63 most loads and 33 expected, with 3 searches.

**THE SPLIT.** 14a runs the phases in this order. Before each one, the
preflight reads the room again: the lesser of the session's 40 and what the
pinned ledger shows free. A phase whose MOST loads do not fit is deferred to
14b, and the next phase is tried. Because most-loads is the upper bound, how
far 14a reaches depends on what each phase actually spends. Both figures
below are DERIVED, by simulating the preflight's rule:

- **GO before 08:02 IST (33 free).**
  - At most-loads in every phase, 14a is phases 1-15 and 22, for 33 loads.
  - At the expected figures, 14a runs phases 1-28 for 31 loads, and defers
    29-30, which need 3 each with 2 left.
- **GO after 08:10 IST (40 free).**
  - At most-loads, 14a is phases 1-19, for 40 loads.
  - At the expected figures, all 30 phases run, for 33 loads.

Either way 14a's searches are C-SRCH-3a's 3.

**14b is a session of its own,** after the window, on its own GO:

- its own session directory (`live14b`), so 40 loads and 5 searches of its
  own;
- whatever 14a deferred, plus phases 32-34, which are NOT in this runner:
  - 32 `people_labels`, rank 2, 3 loads and 3 searches;
  - 33 `article_publish_settings`, rank 149, 2 loads;
  - 34 `saved_posts`, rank 151, 3 loads.

They are built after 14a: 149's delete is aimed at the Drafts list rank 1
captures, and their typing sites come with them. They get their own checks,
review and READY.

The searches question the cold review raised is settled by a ruling on
record. The inbox's typed search (M M34) is no D1 search under
INBOX-SEARCH-IS-NOT-A-D1-SEARCH, but it is a load if it navigates. So it
counts in phase 8's loads, not in its searches.

## 2. The rulings that bind the runner

- **TOGGLE-FIRST** (section 0, item 1): the Easy Apply round trip comes first
  (one search, two re-queries, each recorded BEFORE it is made), and All
  filters after it.
- **UNREAD-IS-HIS, answered: `UNREAD_ANSWER=skip`** (the orchestrator,
  23:12; section 1). The runner implements the ruling as written, and the
  checks show it: the guard drops the lines before any load on `skip`, and
  the inbox runs only on the guard's own count and on `read`. Under the answer
  given, phases 7 and 8 are not runnable at all. No message is opened or
  marked, and no conversation row is ever pressed.
- **E18 and E19 are waited on** before their landing is judged.
  - E18 (`/in/me/?isSelfProfile=true`, on the alias's root) calls the shipped
    `self_profile.await_rewrite`.
  - E19 (the overlay, beneath the root) calls it too. There, the shipped wait
    answers `not_needed`, so the runner's `_await_alias_left` watches
    `page.url` instead. It uses the same bound and poll constants, and it only
    reads.
- **Every self-root press goes through `volunteering_route.exact_link_verdict`**,
  imported, never re-implemented. Rank 69 goes through `match_verdict`,
  whose id comes from his arguments only. The landed member is the segment
  E5's loader proved.
- **Record where `/in/me/edit/intro/` lands** (phase 11).
- **P L8 is re-aimed from what phase 18 draws.** Its reader rests on
  `/dashboard/`, which moved. The hub's own navigation is read there, and the
  record maps P L8's surface to the drawn spelling. The page never supplies
  an address this session follows.

## 3. The stop lines

STOP-ALL ends the session (exit 4). The list is the final runner's
`STOP_ALL_KINDS`, all 22 kinds by name; `stop_lines_check_s14.py`, disposable,
beside the runner, reads them by AST and refuses a section 3 that misses one.
It fires on:

- any wall, checkpoint, challenge or password prompt
  (`auth_wall_or_challenge`);
- the flag not being this lane's, a second client on 9224, or a listener that
  is not the dedicated profile's browser (`flag_not_ours`,
  `second_client_on_9224`, `listener_not_the_dedicated_profile`);
- a count of the ledgers by hand that failed (`ledger_count_failed`);
- a failed restore: a switch, the toggle or the folder (`restore_failed`);
- a publishing or creating control as a press aim, or a commit or autosave
  sign (`publishing_control`, `commit_sign`, `autosave_sign`);
- a Save, Submit, Delete or Remove drawn as pressed (`save_drawn_pressed`),
  or a save request sent by the Open-to-Work editor's close
  (`save_request_on_close`);
- his root's structure changed after an editor (`profile_changed`);
- the Open-to-Work card changed (`otw_card_changed`);
- a conversation opened, or the guard's premise broken
  (`conversation_opened`, `guard_premise_broke`);
- a self-root or attended press that landed anywhere but its target
  (`press_landing_not_target`);
- an error after a press that may have changed something, which is never a
  plain abort (`press_outcome_unread`);
- the shipped loader proving a member other than the one this session's proof
  names (`self_member_changed`, the R3 ruling);
- an editor, overlay or attended menu that will not close
  (`editor_not_closed`, `post_editor_not_closed`, `otw_editor_not_closed`);
- a typing site asked for a text that is not one of its constants, or whose
  text reached a composer (`typing_not_closed`);
- a deletion that cannot be verified (phase 33, 14b; built for 14b's own
  READY, so not a kind of this runner).

A phase stops (exit 3) on:

- an error envelope or an exception;
- a menu or editor that does not close;
- a landing that is not its target;
- `people_gate.judge` raising;
- a ledger refusal.

The self block: if E5 does not prove his root, phases 1 (its presses), 3, 10,
12, 20, 27 and 28-31 drop, with the reason. Phases 2 and 16 read pages under
`/in/me/details/`, which served exact without the proof in session 12. They
press nothing on his root, so they still run, with skeletons only (people
gate v2 cannot learn him without the slug).

## 4. The runner

| file | where | role |
|---|---|---|
| `runner_s14.py` | the main checkout's gitignored `_state/live-runner/s14/` | session 14's runner: 31 phases plus `root_settle`, `flag_on`, `flag_off`, `provenance` |
| `runner_s13.py` | beside it | session 13's runner, byte-identical (`4f0adbed`): the red side of every check |
| `runner_s14_r1.py` .. `runner_s14_r4.py` | beside it | the snapshots the cold review read (round 1) and re-checked warm (rounds 2-4) |
| `s14_block_1.py` .. `s14_block_5.py`, `assemble_s14.py` | beside it | the session-14 code and the script that builds the runner from session 13's (each insertion asserts its anchor once) |
| `gate_checks_s14.py` | beside it | the red-first checks (section 5) |
| `scripts/people_gate.py` | tracked, unchanged by the merge | PEOPLE-GATE v2, IMPORTED from this worktree |
| `scripts/_probe_live_lane_session_2.py` | tracked, changed by the merge (prof7) | imported: the session ledger, the driver lock, the counter around `BROWSER.goto`, skeletons, health |
| `linkedin_server/volunteering_route.py`, `self_profile.py` | tracked (prof7, integration 7) | IMPORTED: the one matcher; the shipped self loader's wait |
| the job-pipeline skill's `jobpipe` | user scope, installed | the ONE account ledger, loaded by file location |

**WHAT CHANGED FROM SESSION 13'S RUNNER** (its header, S1-S9):

- S1: the import root is this worktree at the merge.
- S2: 40 loads a session and 40 on the account, with no reserve.
- S3: every load under `/in/me/` is waited on (section 2).
- S4: every self-root press goes through the one matcher, on the href as
  drawn, re-read after the pace. Where the press went is judged against the
  matched target, and anything else is STOP-ALL.
- S5: E5 decides the self block.
- S6: UNREAD-IS-HIS.
- S7: TOGGLE-FIRST.
- S8: ONE typing site, which SETS a fixed runner constant into one anchored
  input and re-reads the composer after.
- S9: the phases of section 1.

And, from the cold review's round 1 (section 6):

- THE ONE CLICK SITE dispatches without waiting on a navigation it starts.
  It counts every document it started in a `finally`. A press that opens a
  tab is counted, the tab closed, and the phase stopped.
- A `DocumentWatch` is held over EVERY phase. The metered goto marks its own
  navigation's first document, so a watch never counts a load twice.
- Escape and Enter are pressed only while a load fits the call.
- The attended presses refuse a toggle, an input or any pressed/checked
  state, whatever its label. Their region digest includes control states.

## 5. Shown offline, red first

`gate_checks_s14.py` drives the runner's REAL code on synthetic pages:

- a local headless Chromium, DNS mapped to NOTFOUND, every request aborted at
  the CONTEXT;
- `https://www.linkedin.com/` served from synthetic pages, every name, id and
  value synthetic;
- the ledgers, the store and the state redirected to a temp directory;
- every Save, Done, Delete, Hide and option counting its clicks.

GROUPS:

- **A**, the alias's wait.
- **B**, the self-root press through the one matcher: 16 lookalike spellings,
  two links, a re-point during the pace, a changed root, Escape and Dismiss,
  an editor that will not close, a press that loads a document and its
  deferred compare, rank 69's id.
- **C**, UNREAD-IS-HIS.
- **D**, TOGGLE-FIRST, and the panel's own close control.
- **E**, the typing site.
- **F**, the items and the tables.
- **G**, the phases end to end: ranks 23, 26, 109, 115, 150, 1, a password
  prompt, 103's landing, E18/E19, rank 30's two presses, M M34's search, and
  ranks 144 and 145 with an allowed and a refused label.
- **H**, E5 with rank 31's press.
- **R**, each round-1 finding.
- **S1**, the file's own structure.

RESULTS (each run serially, the flag down): see section 7's final pass.

## 6. The cold review

A general-purpose child, never an implementer, read the frozen snapshot cold:
`runner_s14_r1.py` (`39ddabfa`). Its report is a file:
`_state/lane-scratch/live-s13/review-s14/round-1.md` (gitignored, beside
this lane's scratch).

**The matcher re-check, where the runner imports it (the orders' item):
items 1-5 VERIFIED.** It ran 63 spellings on the about link (verify-prof7.md's
table, its fix notes, and further spellings of the same classes) and 16 on
the volunteering link:

- every href reached `exact_link_verdict` exactly as the DOM attribute held
  it;
- every lookalike refused, with 0 clicks;
- an href re-pointed during the pace was not pressed;
- the landed member was the loader's proven segment;
- rank 69's id appeared in 0 printed lines, state files, ledger rows or store
  events.

No BLOCKER.

FINDINGS, each fixed at the cause and shown red first (group R: all 16 fail
on `runner_s14_r1`, and pass after):

| finding | fix | check |
|---|---|---|
| MAJOR-1: the page could re-point the link inside the click, and the landing was never judged | `press_landing`: target, his root, or STOP-ALL `press_landing_not_target`; the before-reads moved above the pace | R1 |
| MAJOR-2: a click that started a slow navigation raised `_NotActionable` after dispatch, its document uncounted | `no_wait_after`; documents counted in a `finally`; the switch re-read after an error | R2 |
| MAJOR-3: six phases pressed with no `DocumentWatch` | a watch over every phase; the meter marks its own document | R3 |
| MAJOR-4: the label rule admitted a toggle with an allowed label | toggles, inputs and pressed/checked states refused; states in the digest | R4 |
| MINOR-1: a `target=_blank` link opened an uncounted tab | refused; `_click` counts and closes a popup, then stops | R5 |
| MINOR-2: an attended menu outside the region read as closed | popup evidence in `gone()` | R13 |
| MINOR-3: an in-page newsletter form read as closed | the form's own evidence; the autosave compare after the press and the close | G6 |
| MINOR-4: Done was both never-press and a close word | dropped, with an import-time assert | R6 |
| MINOR-5: focus could move to the composer mid-typing | the value SET on the anchored input; the composer re-read after, STOP-ALL | R7 |
| MINOR-6: Remove drawn as pressed went undetected | added | R8 |
| MINOR-7: a failed E5 left an earlier proof standing | self.json unlinked | R9 |
| MINOR-8: a deferred root compare could stay pending | `root_settle`; E18 settles one | R10 |
| MINOR-9: rank 69's id file stayed on disk | the file deleted once read; one outside gitignored state refused | R11 |
| MINOR-10: the Open-to-Work phase compared only the card | his whole root, under a watch | R14 |
| MINOR-11: Manage was never verified closed after Drafts | closed when Drafts did not navigate | R15 |
| NIT-6: Escape and Enter bypassed the call's room | `_key` | R16 |
| NIT-1, NIT-2, NIT-3, NIT-7 | the header; the clear through the one typing site; the unused table removed; the gate's routes per context | S1, the gate |

NOT FIXED HERE, by reason:

- NIT-4, E19's wait, is documented in section 2.
- NIT-8 is two notes on prof7's matcher itself, which cannot reach the
  runner. They are for the orchestrator.

The review's section 4 disagreements are corrected in sections 1-3 above.

**ROUND 2, the warm re-check** (the same reviewer, `review-s14/round-2.md`, on
`runner_s14_r2.py`, `4a55a9a3`). It re-ran its own probes warm.

- The matcher still held, 20/20. There was no BLOCKER.
- Of round 1's findings, ten were CLOSED and five CLOSED WITH A NEW ISSUE. NIT-6
  was PARTLY CLOSED, and NIT-4 and NIT-8 were not fixed here, by reason.
- It found two new MAJORS and three new MINORS. All are fixed in round 3, each
  red first (group Q: red on r2, green on r3):

| finding | fix | check |
|---|---|---|
| MAJOR-A (MAJOR-2's fix): `no_wait_after` left a navigation pending, so the next read raised, an ABORT that skipped the landing judge | `_click` waits for the navigation it counted (its `response()`, then the load state); any error after a self-root, attended or Create press is STOP-ALL `press_outcome_unread`; any error after the switch's press is STOP-ALL `restore_failed` | Q1 (3 s, 7 s), Q1b, Q2 |
| MAJOR-B (MAJOR-3's class): nine phases loaded BEFORE their watch, and the guard had none | the watch is entered before the load in every phase; the guard watches our own tab from outside the shipped tools' sessions | Q3 |
| MINOR-A: the first `--items` file was deleted, not the one holding the id | every file that holds it is deleted | Q4 |
| MINOR-B: a failed E5 made a pending compare unsettleable | the deferral keeps its slug; `root_settle` proves his root by its own loader call; `flag_off` refuses while a compare is pending, unless it is accepted by name | Q5 |
| MINOR-C: the region digest read values by length | the value itself, and a select's index | Q6 |
| NIT-A: a tracking key added on landing would have been a veto | the target's own parameters, each with its exact value | Q7 |
| NIT-C: E18's variant could make a spurious STOP-ALL | E18 settles nothing; `root_settle` does | R10 (amended) |
| NIT-D: `close_all`'s Escape bypassed the call's room | skipped while the room refuses | Q8 |
| NIT-E, NIT-F | the STOP-ALL line names the composer; the JS handles are disposed | -- |

NIT-B (an in-page opening is judged by URL only) is documented, not changed.

**ROUND 3, the warm close-out** (`review-s14/round-3.md`, on `runner_s14_r3.py`,
`c17487ed`).

- The matcher held, 20/20.
- Both of round 2's majors were CLOSED, and so were its minors. MINOR-B was
  CLOSED WITH A NEW ISSUE.
- No BLOCKER and no MAJOR remained. Two new MINORS were found, fixed in round 4,
  red first (red on r3, green on r4):

| finding | fix | check |
|---|---|---|
| MINOR-D (MAJOR-A's class): `DocumentWatch.reconcile` read a page whose navigation was pending, and the self press's close and compare sat outside the STOP-ALL wrapper | `reconcile` waits for a late document's navigation as `_click` does; the close and compare (and rank 30's two closes) run under the wrapper | Q9, Q10 |
| MINOR-E (MINOR-B's fix): `root_settle`'s proof rewrote E5's file, re-opening the self block | `his_root(prove=True, persist=False)`: proven by the loader's rule, nothing written | Q11 |
| NIT-G: dead switch code under `if False:` | removed | Q12 |
| NIT-H: an error after the Drafts press was a plain abort | the aftermath under the STOP-ALL wrapper | Q13 |

**ROUND 4, the final warm confirmation** (`review-s14/round-4.md`, on
`runner_s14_r4.py`, `1468b62b`, which also carries UNREAD-SKIPPED's change to
the table). Every round-3 finding is CLOSED:

- N1: `reconcile` waits for a 7 s late document, and it is counted once.
- X18: an Escape that navigates slowly is judged through.
- X19a/b: an error inside a close is STOP-ALL.
- N2 x2: `root_settle` writes no proof file.
- N4: `flag_off` refuses with a compare pending.

The UNREAD-SKIPPED delta is VERIFIED:

- the inbox's two phases refuse as unknown;
- `featured` makes 1 load and presses nothing;
- a client-side move after its load is counted.

Every earlier probe stays closed, and the matcher still holds (20/20).
**"Nothing above a NIT remains. This is the close-out."**

THE NITS THAT STAND:

- NIT-B (an in-page opening is judged by URL) and NIT-4 (E19's wait) are
  documented.
- NIT-8 is prof7's.
- T10b's residual: a hostile focus pull lands the fixed token in a composer
  before the STOP-ALL, and the STOP-ALL line tells him to clear it. The one
  typing site is unreachable in session 14: no runnable phase loads
  `/messaging/`.
- The `if True:` shims are style only.
- The one NIT new in round 4, the S6 header item, is fixed in r5
  (documentation only).

**THE ORCHESTRATOR'S RULING ON ROUND 3** (`_TEAM_LEAD_R3.md`, 2026-11-28 02:25,
deleted as the ack in the commit adding READY).

- It ordered all four items fixed, red first. They already were in r4, each
  with its check (section 6, round 3's table).
- It added one requirement to MINOR-E: "make a proof of any other member a
  STOP-ALL". That is r5's one behavioural change. If the shipped loader proves
  a member other than the one this session's proof names, `his_root` raises
  STOP-ALL `self_member_changed` before any file is touched. This covers a self
  line, E5's own re-run, and `root_settle`, which passes the deferred slug as
  `expected_member`.
- A loader that proves nothing is still "not proven".
- Check Q14 is red on r4 and green on r5.

**ROUND 5, the warm close-out on the FINAL sha** (`review-s14/round-5.md`, on
`runner_s14.py` = `runner_s14_r5.py`, `8094c4a0`):

- V1-V3: the new STOP-ALL, VERIFIED on a self line, on E5's re-run and in
  `root_settle`, each leaving `self.json` untouched.
- V5: a loader that proves nothing is never STOP-ALL.
- Every earlier probe gives the same result as on r4, and the matcher holds
  20/20. **"Nothing above a NIT remains on the final sha. This is the
  close-out."**
- One NIT is new, and accepted as it fails toward stopping. The member is
  compared case-sensitively, so E5's slug in another letter case would be
  STOP-ALL. LinkedIn's rewrite lands on one canonical spelling, and the
  matcher itself must stay case-exact.

## 7. The final pass, serially, on the FINAL runner

The final runner is `runner_s14.py` (`8094c4a0`, = `runner_s14_r5.py`), with
the check file `gate_checks_s14.py` (`6ea192d6`). The pass is
`final_pass_s14.sh`, in four chunks, 2026-11-28 05:15-06:28 IST, the flag
down at every step. The outputs are in `final/`, beside the runner.

| check set | runner | result |
|---|---|---|
| `provenance` | final | every gate module from where it must be (5 of 5 True) |
| `gate_checks_s14.py` | **final** | **82 of 82 passed** (78 red-class, 4 controls) |
| the same | `runner_s14_r4` | 1 red-class failed: Q14, the R3 ruling's STOP-ALL |
| the same | `runner_s14_r3` | 6 red-class failed: Q9-Q14 |
| the same | `runner_s14_r2` | 16 red-class failed: round 2's and later findings |
| the same | `runner_s14_r1` | 28 red-class failed: every round's findings, and S1 |
| the same | `runner_s13` | 54 of 54 red-class failed; its 2 controls passed |
| session 13's `gate_checks_s13.py`, on the shared code | final | 49 of 57 passed (below) |
| session 12's Open-to-Work checks (`otw_checks_s14_port.py`) | final | 8 of 8 |
| `entry_refusals_s14.py` | final | 14 of 14 refusals as named, before any browser contact; the pinned store unchanged; no flag, ledger, lock or self proof made |
| `prepare_items_s14.py` | -- | 3 items, every check passed (shapes, the identity-key veto, rank 95's veto, 21 of 21 addresses admitted, the AI route) |

Session 13's check set fails 8 checks on the final runner, each for a named
session-14 difference, not a defect:

- 3 are its 28-load caps (now 40);
- 3 are its inbox phase's vetoes (that phase is not runnable here);
- 1 is its "no typing site" control (session 14 has one);
- 1 is its runnable-phase set.

The other 49 checks of the shared code pass.

## READY (2026-11-28, 06:35 IST)

Session 14's Phase A is done. The runner, its checks and the cold review are
closed, and the final pass ran on the final sha. HOLD: PHASE B starts only on
a `_TEAM_LEAD_GO.md` that names these pins, with the operator at the
console.

**THE PINS** (full values in the session's gitignored `_state/live14/pins.json`,
written after the commit that adds this section):

| pin | sha256 (short) |
|---|---|
| `runner_s14.py` | `8094c4a0d9419b26` |
| `scripts/people_gate.py` | `6ff3afb732ed1546` (unchanged by the merge) |
| the harness, `scripts/_probe_live_lane_session_2.py` | `a5c10ae992f691b8` |
| `linkedin_server/volunteering_route.py` (the one matcher) | `5635e69f595bfa3c` |
| `linkedin_server/self_profile.py` (the shipped wait) | `b39b615b2c476b94` |
| the prepared items (gitignored) | `842bced39d3678bb` |
| `os_check.ps1` | `455cc21796054c94` |

The branch head is the commit that last amends READY. Two amendments follow
the first READY's commit: the AST-equality line below, then section 3's stop
lines, completed to all 22 of the runner's kinds. The head's sha is in the
amended READY message and in `pins.json`.

**THE AST-EQUALITY LINE** (`ast_delta_s14.py`, disposable, beside the runner;
run 06:36 IST; VERIFIED by instrument):

- **The measurement.** `runner_s14.py` (`8094c4a0`) against r4 (`1468b62b`),
  with every docstring stripped (comments are not in the AST): AST-equal
  outside exactly three top-level statements, `STOP_ALL_KINDS`, `his_root` and
  `phase_root_settle`. No statement is in one file only.
- **So the diff from r4 is NOT comment- and docstring-only.** Those three
  statements carry the R3 ruling's other-member STOP-ALL
  (`self_member_changed`), r5's one behavioural change (section 6). The
  orchestrator's round-4 message was written about r4, before r5 existed.
- **Nothing has to carry.** Round 5, the warm close-out, ran on `8094c4a0`
  itself (`cmp`-identical to `runner_s14_r5.py`, hashed at its start and its
  end). Its V1-V3 and V5 probe exactly those three statements. The final pass
  ran on the same sha (section 7).
- **The whole text diff, line by line:** 5 hunks, 6 lines removed and 21
  added.
  - 16 added and 4 removed lines are in the three statements.
  - 5 added and 2 removed lines are the module docstring's S6 item, which now
    says the inbox's two phases are not runnable under UNREAD-SKIPPED.
  - 0 comment-only lines, 0 formatting lines in an AST-equal statement, 0
    unclassified.
- **The controls:** each file against itself is AST-equal with 0 hunks, and
  one constant changed (`SESSION_CAP` 40 to 41) is caught.

**THE SPLIT** (section 1):

- **14a:**
  - with 33 free (before 08:02 IST): phases 1-15 and 22 at most-loads (33), or
    phases 1-28 at the expected spending (31);
  - with 40 free (after 08:10 IST): phases 1-19 at most-loads (40), or all 30
    at the expected spending (33);
  - its searches are 3, C-SRCH-3a's.
- **14b**, a session of its own after the window:
  - whatever 14a deferred, plus ranks 2 (3 loads, 3 searches), 149 (2 loads)
    and 151 (3 loads);
  - those three are built for 14b's own READY.

**THE BOX AND THE LEDGERS** (06:28 IST):

- `os_check`: 9224 down, 0 clients, no Chrome on the dedicated profile, no
  lock, no flag.
- The pinned ledger: 7 LinkedIn loads in the trailing 12 h, 33 free.
  Session 13's leave by 08:10 IST.

**THE ATTENDED ITEMS** (session 14 is attended):

- phase 1, rank 31: his add-a-position editor, opened and closed;
- phase 3: his Open-to-Work Edit (OPEN-TO-WORK-EDITOR-ATTENDED-ONLY);
- phase 11: his contact-info overlay and its form;
- phase 15: his key skills;
- phase 20: the Career goal control;
- phase 21: one alert row's control, pressed only on an allowed label that is
  no toggle;
- phases 27-30: his About, profile-language, services and volunteering
  presses.

What he names at the GO:

- a post of his, for phase 23;
- his profile id in a gitignored items file, for phase 30.

Without them, those phases drop with the reason. UNREAD is answered (`skip`).

**THE STOP LINES:** section 3. Every STOP-ALL ends the session, and nothing
loads LinkedIn after it until the orchestrator reconciles the ledgers.

**NOT IN THIS READY:**

- the INSTRUMENTS section 122, written at the close-out from what held live,
  as section 119 was;
- 14b's three lines.

## 8. The commands for PHASE B, on GO

Every runner call takes the same environment:
`LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 LINKEDIN_MIN_INTERVAL_S=20 LIVE_LANE_SESSION_DIR=live14`.
The runner and its tools are in the main checkout's `_state/live-runner/s14/`,
and each step runs in the foreground.

1. **Before the first load:**
   - `verify_pins_s14.py` must print ALL-MATCH against the GO's pins.
   - `os_check.ps1`: 9224 down, no flag, no lock.
   - The pinned ledger's free count is read; it sets 14a's room.
2. **Chrome and the flag:**
   - the dedicated Chrome is started with the main checkout's
     `scripts/start_chrome.ps1`, its two flags only;
   - `os_check.ps1` again;
   - `runner_s14.py flag_on`;
   - the harness's `attach_check`, 0 loads.
3. **The phases, in section 1's order.** The preflight refuses a phase
   whose most-loads do not fit the room, and the next one is then tried.
   - After `profile`, the caller names the items E5's reading drew
     (`name_items_s14.py skill`, then `name_items_s14.py skill_index`).
   - `c_srch_3a` and `permalink_menus` take
     `--items _state/live14/items_prepared.json`.
   - `post_analytics` takes the post he names.
   - `self_press_volunteering` takes his profile id, from a gitignored items
     file the runner deletes once read. Without one, phase 30 drops
     (section 9).
4. **The end:**
   - `root_settle`, if a compare of his root is pending;
   - `flag_off`, which refuses while a compare is pending;
   - the dedicated Chrome closed BY ITS PID, verified by its command line;
   - `os_check.ps1`: 9224 down, 0 clients, no Chrome on the profile, no
     lock, no flag.

## 9. What needs the orchestrator

1. **Rank 69's profile id has no source on disk.** The orders name "the
   gitignored identity key's operator class". That class holds 5 values, none
   of the member-id shape (VERIFIED, counts only). Under
   VOLUNTEERING-FALLBACK-BOUNDARY the page may never supply the id. So the GO
   must carry it in a gitignored items file, or phase 30 drops with that
   reason.
2. **Rank 154 needs a post of his, named by him at the GO.** Without one,
   phase 23 drops.
3. **UNREAD's optional round trip.** The two cells' definitions do not call
   for one. M M28 is the Archived view, and M M54 restores an archived row;
   neither is about a conversation's read state. And marking another
   conversation unread would not change what `/messaging/`'s landing opens.

   A route with no outward effect is on disk, though: the composer's own
   address. Session 13's load 7 of it drew the list with nothing opened, and
   its tracked skeleton (`tests/fixtures/live13/messaging_list.html`) draws
   the same folder pill and folder dropdown (VERIFIED by attribute). So the
   Archived capture could ride the composer's page, where no conversation is
   landed in. It is proposed for a ruling and not built.
4. **prof7's matcher, two notes, for its owner** (the cold review's NIT-8):
   - `_why_not` names a scheme-case difference `query`;
   - a dot-segment member passes the matcher's own member check.

   Neither can reach the runner, whose member always comes off a
   parser-normalised landing.

---

## 10. Live session 14a, the run (2026-11-28, attended)

**THE RULINGS ON SECTION 9** (the orchestrator, by message, after the amended
READY): no question asks the operator anything, and each takes its default.

- Phase 30 (rank 69) drops to 14b, "no operator-supplied profileId".
- Phase 23 (rank 154) drops to 14b, "no operator-named post".
- Either may come back only if he volunteers the item at the GO.
- UNREAD's composer-address route (item 3) is YES, for 14b. It is built after
  14a, offline and reviewed, with its own READY.

**THE GO** (`_TEAM_LEAD_GO.md`, written 08:31 IST; deleted as the ack at
08:35:11, before Chrome started; a copy is in the lane's gitignored scratch):

- The operator was at the console from 08:30.
- It named all 11 pins of `pins.json` (06:45:54).
- The budget: the pinned ledger is the authority. 14a runs in order, and
  stops when the next phase's most loads would pass what is free.
- UNREAD-SKIPPED: M M28, M M54 and M M34 are not run.
- Phases 23 and 30 are not supplied.
- TOGGLE-FIRST; E18 and E19 through `await_rewrite`; every self-root press
  through `exact_link_verdict`.
- Section 3's 22 kinds are the stop lines.
- A status message goes to the orchestrator before each attended phase. One
  was sent before phase 1 and one before phase 3.

**BEFORE THE FIRST LOAD** (08:34 IST, VERIFIED):

- `go_pins_check_s14.py` (disposable, the lane's scratch) read the GO's 11 pin
  lines. All 11 equal `pins.json`, and the three files the GO names beyond
  `verify_pins_s14.py`'s set hash to the GO's values: GO-MATCH True.
- `verify_pins_s14.py`: ALL-MATCH True (head `70ac75fa`, tracked tree clean).
- The pinned ledger: 0 LinkedIn page loads in the trailing 12 h, so 40 free;
  the live state down.
- `os_check`: 9224 down, 0 clients, no Chrome on the dedicated profile, no
  lock, no flag. No live runner process on the box.

**THE START** (0 loads):

- 08:35:16: the dedicated Chrome started by the main checkout's
  `scripts/start_chrome.ps1` (outcome `started`, Chrome 158, its two flags
  only).
- 08:35:24: `os_check`. 9224 was held by the profile's one browser process,
  with 0 clients and no lock.
- 08:35:33: the flag raised.
- `attach_check`: PASS `[0, 1, 0]`, restored, 0 loads.

### 10.1 The loads

| load | IST | phase | landing | what it read |
|---|---|---|---|---|
| 1 | 08:36:00 | 1 `profile` (E5) | served, same depth, another url: his root | E5 proved his root; the top card; the More menu; then the photo press stopped the phase |
| 2 | 08:37:55 | 2 `recommendations` | served exact | the Received and Given switch, round trip restored; the section's disclosure |
| 3 | 08:39:19 | 3 `otw_editor` (attended) | served, same depth, another url: his root | the same member proven; the card; Edit pressed; STOP-ALL `otw_editor_not_closed` |

Every load was recorded in the pinned ledger before it was made. No load drew
a wall, a checkpoint or a challenge (each: walled False, 0 challenge terms).
The closest two loads were 84 s apart.

### 10.2 What each phase showed

**Phase 1, `profile`: exit 3, a phase stop after 1 load.**

- **E5:** his root served through the shipped loader, and the self rule
  proved it at its first load. The proof was kept in the session's gitignored
  state, so the self block was open.
- People gate v2 withheld the raw, and the skeleton was kept.
- The top card drew More 1 (0 visible), Resources 1 (1), Open to 2 (1),
  Enhance profile 2 (1) and Add profile section 0.
- Editor routes on the first render: `edit/forms/summary/new/` 1,
  `edit/intro/` 1, `edit/secondary-language/` 1, and 1 other form.
- The top-card opener (Resources) drew a menu of 5 items, closed on the first
  Escape.
- The photo press was `did_not_close` at `in_me_photo`, so the phase stopped
  and closed its tab. Nothing was chosen or saved.
- Not reached:
  - the custom-button press;
  - the scroll pass and the Experience section;
  - rank 31's press;
  - E5's skill ids and insight indices.
- So phases 9 (`skill_form`) and 26 (`skill_insights`) have no item to name.
- Phase 1's readings are in its run log only. The stop raised before the
  phase recorded them.

**Phase 2, `recommendations`: exit 0, 1 load.**

- The self alias wait ended `not_within_bound` after 5008 ms, and the page
  still served exact. People gate v2 fired N1 1, R1 1 and R2 1 and withheld the raw;
  the skeleton was kept.
- The switch is two labelled checkboxes: Received checked, Given not. The
  first view: 0 entries and 0 member links.
- Given pressed once: Given checked, Received not. Its view: 0 entries and 1
  member link.
- Received pressed back: restored True.
- The section's disclosure drew 2 items and closed on its first Escape.

**Phase 3, `otw_editor`, attended: exit 4, STOP-ALL, 1 load.**

- The loader proved his root again, and the member was the one E5 proved
  (`the member E5 proved True`). The R3 ruling's check held, in its passing
  direction.
- The card before the press: drawn 1, audience "Recruiters only", Edit in the
  card 1 (visible), hydrated 2, the top-card photo not framed.
- Edit pressed. The editor opened as a modal: buttons 3, checkboxes 1 (1
  checked), inputs 1, switches 1, links 1, headings 1, editors 1. Nothing in
  it was drawn as pressed (save or confirm 0). Its words: Delete 3, Next 3,
  Dismiss 1, Locations 1, On 1.
- The close (3 Escapes, then the Dismiss step) left a modal visible beyond
  those before the press. That is STOP-ALL `otw_editor_not_closed`. The runner
  closed its tab, and the session ended.
- The window was `raised_unfocused` for this phase; it was `fronted` for
  phases 1 and 2.
- **No instrument read whether the close made a save request, or whether his
  card is unchanged.** The request summary and the card's after-read run only
  after a close succeeds. Nothing in the editor was pressed but the close
  attempts.
- **The answer is OPERATOR-OBSERVED** (08:43 IST, confirmed 08:44, relayed by
  the orchestrator's `_TEAM_LEAD_AFTER14.md`). His Open-to-Work card still
  reads "Recruiters only", with no green frame, and his photo is unchanged.
  OPERATOR-OBSERVED is its own class: he saw it, and no instrument of this
  lane measured it.

### 10.3 The close: no load after the STOP-ALL

- 08:40:57: the flag was lowered. No compare of his root was pending, so
  `root_settle` had nothing to settle, and it was not run: nothing loads after
  a STOP-ALL.
- The dedicated Chrome was closed BY ITS PID after its command line was
  checked (the debugging port and the dedicated profile). 0 processes were
  left on the profile and 0 listeners on 9224.
- 08:41:08: `os_check` showed 9224 down, 0 clients, no Chrome on the profile,
  no lock, no flag. His own Chrome was untouched.
- The session folder is preserved in the main checkout's gitignored
  `_state/preserved/live14-2026-11-28`: 24 files, each identical by sha256. No
  raw page was kept (`raw_kept` False in both readings that carry it).

### 10.4 The ledgers

- The session ledger: 3 loads, 0 searches.
- The pinned account ledger: 3 records for session 14
  (`live-s13/14/live_census`), so 3 in the trailing 12 h and 37 free. They
  leave the window at 20:39 IST.
- The two ledgers agree at 3.

### 10.5 The two close failures, measured offline

`skeleton_delta.py` (disposable, the lane's scratch) counts tags and close
words in the tracked skeletons. It prints no page text.

- **The Open-to-Work editor is a native `<dialog open>`** (VERIFIED).
  - The press added ONE `<dialog>` carrying `open`; the page's four other
    `<dialog>` elements stay closed. It also added 3 buttons, 1 input and 1
    label. Counted as an element's whole text or label, Dismiss, Delete and
    Next each appear once more.
  - After the 3 Escapes and the Dismiss step, the page's skeleton is
    byte-identical to the settled open one.
- **The room guard did not skip the Escapes** (DERIVED). Offline, against the
  same ledgers, `press_room()` returns None for a call with 1 load.
- **UNVERIFIED: why the dialog stayed.** Neither is it known whether the
  Dismiss control was found and pressed, because the close path records
  nothing when it raises. Two candidates, for 14b to measure offline first:
  - the Escapes reached an element outside the dialog (the window was
    `raised_unfocused`);
  - the dialog takes no Escape, and needs its own control pressed inside
    `dialog[open]`.
- **This was the editor's first live press.** Session 12 never pressed Edit:
  its record lists E37' as not loaded. So the close rule had never met the
  editor. The STOP-ALL did what session 12's check V3 built it for: it
  refused to call the editor closed.
- **The photo press added no dialog** (VERIFIED).
  - It added 152 `div`, 58 `span`, 47 `p`, 29 `a`, 14 `figure`, 14 `img`, 7
    `h2`, 7 `button`, 5 `section`, 5 `input` and 5 `label`.
  - No close word was added (Dismiss, Close, Edit and Next unchanged).
  - The 5 inputs are what 119.2's panel rule counts as a panel opened.
  - After 3 Escapes the skeleton is byte-identical.
- **A reading, not proven:** five sections, with headings, images and links,
  read like profile sections that rendered late, not a panel the press
  opened. If so, the stop was a false `did_not_close`. UNVERIFIED either way.

### 10.6 What 14a did not reach (all to 14b)

- **Not run because of the STOP-ALL:** phases 4-8, 10-22, 24, 25 and 27-29.
- **Not run for want of their items:** phases 9 and 26. E5's skill items were
  never read.
- **Not supplied (the GO):** phases 23 and 30, "no operator-named post" and
  "no operator-supplied profileId".
- **From phase 1:** rank 31's press, the scroll pass and the custom button.
- **From phase 3:** rank 24's close and the card's after-read.
- **14b's own lines:** ranks 2, 149 and 151, and the composer-address route
  for M M28 and M M54.

### 10.7 Rows moved: none

Every line was a capture, and a capture moves no row by itself.

- The capture queue's `captured_already` cells for ranks 23 and 24 now name
  the session-14 skeletons.
- `tests/fixtures/live14/` holds 11 tracked copies. Two of them are
  byte-identical "not closed" copies, kept as the stops' evidence.

### 10.8 What needs the orchestrator

1. **His Open-to-Work card after the STOP-ALL: answered, OPERATOR-OBSERVED**
   (10.2, phase 3). It still reads "Recruiters only", with no green frame, and
   his photo is unchanged. The next live session still reads the card before
   anything else on his root, so an instrument measures it too.
2. **14b's GO waits on the close failures** (10.5). Its runner needs, each red
   first and reviewed, with its own READY:
   - the close path recording which steps ran;
   - a phase stop recording what was read before it;
   - the Open-to-Work close aimed inside `dialog[open]`;
   - the panel rule kept apart from sections that render late.
3. **The account:** 37 free now. Session 14's 3 leave the window at 20:39 IST.

### 10.9 The orders after the STOP-ALL

These are `_TEAM_LEAD_AFTER14.md` (the orchestrator, 2026-11-28 09:00 IST). It
was deleted as the ack in the commit that adds this section. NO LIVE LOADS:
everything below is offline.

1. The close-out: the record, the skeleton export, the ledgers reconciled at
   3. Done in this record's section 10, with his check recorded as
   OPERATOR-OBSERVED.
2. The close-failure diagnosis, from the skeletons:
   - the native-`<dialog>` hypothesis tested RED FIRST against both
     skeletons;
   - the close sequence AND its check fixed, through the cold reviewer as in
     rounds 1-5.
3. 14b's runner, built on that fix, with its own READY and pins. It covers:
   - phases 4-29;
   - phase 1's unreached parts (rank 31's press and the skill ids);
   - phases 9 and 26;
   - ranks 2, 149 and 151;
   - phases 23 and 30, only if he volunteers their items;
   - the composer-address route for M M28 and M M54.
4. Merge master (9aa4c94 or later), then lane CI plus the full matrix, by
   sha. Then FINAL, then HOLD.

There is no GO for 14b until the close fix is reviewed. 14b's GO comes from
the orchestrator, with him at the console. Master 9aa4c94 is already merged
(the merge commit after section 10's close-out). Item 4 merges again if
master has moved by then.

## 11. Session 14b, PHASE A (offline): the close fix and the 14b table

Everything here is offline: zero loads, no browser started or attached, 9224
untouched, the flag never raised. The runner and its checks live in the main
checkout's gitignored `_state/live-runner/s14b/`.

### 11.1 The diagnosis, red first against both skeletons

`close_checks_s14b.py` drives the runner's REAL close path (`otw_capture`,
`press_open`, `otw_close`, `close_all`, `_click`, `press_read_close`) and the
panel rule's own scripts. It runs in a local headless Chromium with every
request aborted, on session 14's tracked skeletons. A skeleton holds no
script, so what LinkedIn's page does with a key or a click is MODELLED, one
hypothesis per model. Each model works on the captured editor's own
`<dialog>` and its own Dismiss:

| model | what it holds | session 14's runner | 14b r1 |
|---|---|---|---|
| `escape_inside` | the dialog hears Escape only when focus is inside it | STOP-ALL `otw_editor_not_closed`, the dialog open (the live outcome) | closed by `escape_1` |
| `covered` | a click cannot reach Dismiss; Enter on it works | STOP-ALL, the dialog open (the live outcome) | closed by `dismiss_enter` |
| `click` | Dismiss closes on a click | closed by `dismiss` | closed by `dismiss` |
| `none` | nothing closes it | STOP-ALL | STOP-ALL, with every step recorded |

- **Two models reproduce the live outcome on session 14's runner**
  (VERIFIED): Escape heard only inside the dialog, and a Dismiss the pointer
  cannot reach. The `click` model closes the dialog even on session 14's
  runner. So had LinkedIn's Dismiss worked on a dispatched click, the old
  runner would have closed it.
- **DERIVED, from timing only:** the phase ended at 08:40:02.8, about 20 s
  after the Edit press, which is the Dismiss press's pace. That fits a
  dispatched Dismiss click that changed nothing. It does not fit a click that
  timed out (5 s more), or no Dismiss press at all (about 10 s less).
- **UNVERIFIED: why the live dialog ignored both.** The window was
  `raised_unfocused` for that phase only.
- **The photo press, on the real pair** (VERIFIED, the runner's own
  `FORM_SIGS_JS` and `FORM_DELTA_JS` across the two skeletons):
  - session 14's runner counts 5 added checkboxes;
  - r1 counts 0, and 5 `in_main_sections`;
  - all three real panels still count, and identically on both runners:
    session 13's jobs All filters 29, session 12's content All filters 13,
    and session 12's people All filters 11.

### 11.2 The fix: r1 (`runner_s14b.py`, built from `8094c4a0` by `patch_s14b_r1.py`)

- **K1.** The close path records every step it takes (`close_steps`): each
  Escape, the Dismiss found or not, and its press `clicked`, `not_actionable`
  or `no_room`, with the modals visible after each. A failed close leaves
  the press's reading in the session state.
- **K2.** A native `<dialog open>` the press opened is closed inside itself:
  - focus moves onto its own Dismiss, with no press, before each Escape;
  - Dismiss is looked for inside that dialog;
  - a Dismiss the pointer cannot reach is pressed by Enter, only while it
    holds the focus, checked before and after the pace;
  - each close gets a 2.5 s grace.
- **K3.** A control added inside `main`'s sections is the page rendering on,
  never a panel the press opened. It is counted apart.
- **K4.** The Open-to-Work editor's request summary is made on every exit, a
  STOP-ALL's included.
- **K5.** Phase 1 records its readings before each of its presses.
- **K6.** A phase that presses an editor, an overlay or a self-root link (the
  self block and the attended set) runs only with the window in front. It is
  refused before any load otherwise. The evidence is thin: one failure while
  `raised_unfocused`, against the closes that held while `fronted`. It fails
  toward not pressing.
- **K7.** The session directory is `live15`, because the harness admits only
  `live` and one or two digits. 14b is a sitting of its own.

**Red first** (VERIFIED, `close_checks_s14b.py`):

- session 14's runner: 0 of 9 red-class checks pass, and 6 of 6 controls;
- r1: 9 of 9, and 6 of 6.
- Among the controls, a dialog nothing closes is still STOP-ALL on r1, and the
  three real panels still count as panels.

**Nothing regressed on r1** (VERIFIED):

- session 14's 82 gate checks, repointed to `live15`: 82 of 82;
- session 12's Open-to-Work checks: 8 of 8;
- the entry refusals: 14 of 14, each before any browser contact, the pinned
  store unchanged.

### 11.3 The 14b table: r2 (`patch_s14b_r2.py`, on r1 as reviewed)

- **K8.** `recommendations` (done in 14a) and `otw_editor` (not in the
  orchestrator's 14b list) are not runnable.
- **K9.** Rank 6's Archived round trip (M M28, M M54) rides the composer's
  page, under the ruling on section 9, item 3:
  - the shipped `linkedin_list_conversations` lands it, and must report that
    it opened nothing;
  - a landing on a thread is STOP-ALL; a landing anywhere else presses
    nothing;
  - then session 13's `_archived_round_trip` runs. From r2b on, its menus are
    closed here by their own trigger, never by Escape, and the watch is held
    from before the tool's load (round 2);
  - nothing is typed (M M34 is not in the ruling).
- **K10.** Rank 151, part 1: the admitted `/my-items/saved-posts/`, loaded
  once, read-only, skeleton only.
- **K11.** The flag and the pinned ledger's records carry session 15, so 14a's
  3 records and 14b's are told apart.
- **Red first** (VERIFIED, `table_checks_s14b.py`): r1 passes 0 of 9, the r2
  candidate 9 of 9, and both pass the control.

**What 14b cannot hold** (measured on disk; the orchestrator was told
2026-11-28 at about 09:50):

- **Rank 2 cannot share a session with C-SRCH-3a.** Each takes 3 searches,
  and the cap is 5.
- **Rank 149's deletion is aimed at the Drafts list** that rank 1 (phase 12)
  captures first, and 14a never reached it.
- **Rank 151's save and unsave ride a post he names.**

The default, until the orchestrator rules otherwise:

- all three go to 14c (only part 2 of rank 151);
- 14b keeps phase 4's searches.

### 11.4 The cold review

The reviewer of rounds 1-5 was resumed, cold to the fix. Each round's report
is in the lane's scratch under `review-s14b/`.

**ROUND 1, on r1 (`93d7fd3e`): no BLOCKER, one MAJOR, three MINOR.**

- **What 14a's own evidence says.** This is the review's section 0, from the
  preserved files' times and its own timing of `_click`.
  - The Dismiss click was dispatched 0.03 s into its run, so it was neither
    covered (that raises at 5.0 s) nor refused.
  - The dialog was byte-identical 1.5 s later.
  - So the shape 14a supports is a Dismiss that closed LATE, or a page that
    ignored the click. It is not the covered shape K2's Enter fallback was
    for.
  - K2's 2.5 s grace is the part of the fix that meets the evidence.
- **MAJOR-1: K2's Enter fallback could activate another control.**
  - The focus can move between the last focus check and the key. The
    `press_room` store guard sits in between.
  - Shown: Delete activated once on a synthetic dialog.
- **MINOR-1: K3 discounted every control inside any section of main**, so an
  inline panel in an existing section was left open, as "nothing opened".
- **MINOR-2: the close checks wrote nothing to the real ledgers, but nothing
  stopped them from doing so.** The session ledger and the pinned store were
  not redirected, and the CDP variables were set.
- **MINOR-3: the check set had no model for the late close, nor for the two
  findings.**
- **NITs:**
  - K6 held three readers;
  - it was checked after rank 69's file was read;
  - the grace reads a replaced dialog as closed. The Open-to-Work path's modal
    count still stops on that.

**r1b (`ba0aa6bb`, `patch_s14b_r1b.py`), each finding fixed red first:**

- **MAJOR-1:** the Enter fallback is REMOVED. A Dismiss the pointer cannot
  reach stays STOP-ALL, as in session 14.
- **MINOR-1:** K3 discounts only a control whose nearest section of main did
  NOT exist when the press's snapshot was taken.
- **Section 0:** at a native dialog's `did_not_close`:
  - OBSERVE-ONLY readings are recorded: the document's focus and visibility,
    the dialog's `:modal`, the focus inside it, and whether the Dismiss's
    centre is the Dismiss;
  - then its own evidence is watched 15 s more, pressing nothing;
  - a dialog that closes in that time is `closed_late`.
- **NIT:** K6 holds only phases that reach a press. The window is checked
  BEFORE any item is read.
- **MINOR-2:** the checks redirect both ledgers and the store, and drop the
  CDP variables.
- **MINOR-3:** the checks gained the late-close models (2.5 s and 6 s), the
  focus race, K3's inline panels (the reviewer's and the photo's own real
  checkboxes revealed in place), and K6 before the items.

**The close checks, three runners** (VERIFIED, `close_checks_s14b.py`):

| runner | red (11, red on session 14's runner) | red-r1 (8, round 1's findings) | controls (7) |
|---|---|---|---|
| `runner_s14` | 0 of 11 | 6 of 8 (its two K6 checks need K6) | 7 of 7 |
| `runner_s14b_r1` | 9 of 11 (the late close and the observe readings are r1b's) | 0 of 8 | 7 of 7 |
| r2 (`c6f6fe2e`, on r1b) | 11 of 11 | 8 of 8 | 7 of 7 |

The 14b table's checks: r1b passes 0 of 9, r2 passes 9 of 9.

**ROUND 2, on r2 (`c6f6fe2e`): a warm re-check and a cold review of K8-K11.
No BLOCKER, no MAJOR, three MINOR, one NIT.**

- **Round 1's findings:** every one CLOSED on r2, re-run with the reviewer's
  own probes. The focus race now activates nothing; the late closes read
  `dismiss` and `closed_late`; the inline panel counts.
- **The lane's add-on is agreed:** K6 had moved ahead of two entry refusals.
  The reviewer's refined order is: every refusal first, and the id's file
  deleted last of all, after the preflight and the driver lock.
- **MINOR-A:** a panel drawn inside a section the press REDRAWS was still
  discounted.
- **MINOR-B (K9):** K9 pressed Escape on the composer's page, where Escape was
  never measured.
  - On a pessimistic model, an Escape that leaves compose lands the
    conversation LinkedIn chooses: the unread top row.
  - The guard stops only after that.
- **MINOR-C (K9):** the document watch started after the shipped tool's load,
  so a document in that window was in no ledger.
- **NIT:** `NEEDS_FRONTED` still named the Open-to-Work editor.

**r2b (`patch_s14b_r2b.py`), each fixed red first:**

- **E1:** the entry runs `parse_items`, then judges the id's files without
  deleting, then the required items, then K6, the preflight and the driver
  lock. Only then is the id's file deleted.
- **MINOR-A:** a control is "late" only when main's sections also GREW over the
  press.
- **MINOR-B:** on the composer's page, the round trip closes its menus by
  their own trigger, NEVER by Escape. Ending off the composer's path is a phase
  stop.
- **MINOR-C:** the watch is held on our own tab from BEFORE the tool's load,
  outside its session.
- **NIT:** fixed.

`composer_checks_s14b.py` runs the round trip END TO END, on the reviewer's
synthetic composer (its menus toggle on their own trigger). It goes through
the shipped `linkedin_list_conversations`, with the call armed and both
ledgers and the store redirected (VERIFIED):

| mode | r2 | r2b |
|---|---|---|
| inert (control) | the round trip runs, the folder is restored | the same |
| an Escape that leaves compose | 3 Escapes, the unread top row opened 3 times, then STOP-ALL | 0 Escapes, nothing opened |
| a document 30 ms after the load | 2 served, 1 in each ledger | 2 served, 2 in each ledger |
| the address ends off the composer's path | recorded, exit 0 | a phase stop (`address_moved`) |

In no mode, on either runner, was a row pressed.

### 11.5 The 14b plan

The order is section 1's, by `rows_per_load`, with:

- 14a's done line and the Open-to-Work editor out;
- the composer's Archived round trip (K9) and rank 151's read (K10) OUT, both
  to 14c, by the orchestrator's 14b scope (11.6).

  Before that ruling, K9 had been moved to last but one. Its B2 rule makes any
  failure after Archived a STOP-ALL, and its close by its own trigger on the
  composer is unmeasured. Each captured row and folder trigger carries
  `aria-expanded` (VERIFIED, 4 skeletons), but no capture shows a re-press
  closing one.

The session directory is `live15`: 40 loads and 5 searches of its own, under
the account's 40 in the trailing 12 h.

| # | phase | rank | most | expected | searches | items | attended | needs the window in front |
|---|---|---|---|---|---|---|---|---|
| 1 | `profile` (E5, rank 31's press, the skill items) | 3, 31 | 3 | 1 | 0 | -- | yes (31) | yes |
| 2 | `c_srch_3a` (TOGGLE-FIRST) | 132 | 3 | 1 | 3 | `job_kw` | -- | -- |
| 3 | `newsletter_form` | 150 | 3 | 1 | 0 | -- | -- | -- |
| 4 | `discovery` | 161 | 1 | 1 | 0 | -- | -- | -- |
| 5 | `featured` | 34 | 1 | 1 | 0 | -- | -- | -- |
| 6 | `manage_syncing` | 158 | 1 | 1 | 0 | -- | -- | -- |
| 7 | `skill_form` | 40, 102 | 1 | 1 | 0 | `skill` (named off E5) | -- | -- |
| 8 | `intro_landing` | 103 | 1 | 1 | 0 | -- | -- | -- |
| 9 | `contact_info` | 30 | 3 | 1 | 0 | -- | yes | yes |
| 10 | `article_drafts` | 1 | 3 | 2 | 0 | -- | -- | -- |
| 11 | `invitation_filter` | 26 | 2 | 1 | 0 | -- | -- | -- |
| 12 | `permalink_menus` | 95 | 3 | 2 | 0 | `member_post`, `page_post` | -- | -- |
| 13 | `key_skills` | 102 | 1 | 1 | 0 | -- | yes | -- |
| 14 | `connections_pills` | 109 | 2 | 1 | 0 | -- | -- | -- |
| 15 | `creator_hub` | 111 | 2 | 1 | 0 | -- | -- | -- |
| 16 | `notifications_card` | 115 | 2 | 1 | 0 | -- | -- | -- |
| 17 | `self_variant` | 117 | 2 | 2 | 0 | -- | -- | -- |
| 18 | `learning_goal` | 144 | 3 | 1 | 0 | -- | yes | yes |
| 19 | `alert_row` | 145 | 3 | 1 | 0 | -- | yes | yes |
| 20 | `learning_saved` | 147 | 1 | 1 | 0 | -- | -- | -- |
| 21 | `post_analytics` | 154 | 1 | 1 | 0 | `own_post`, ONLY if he volunteers it | yes | -- |
| 22 | `search_history` | 156 | 1 | 1 | 0 | -- | -- | -- |
| 23 | `download_data` | 157 | 1 | 1 | 0 | -- | -- | -- |
| 24 | `skill_insights` | 71 | 1 | 1 | 0 | `skill_index` (named off E5) | -- | -- |
| 25-27 | `self_press` x3 (About, profile language, services) | 64, 67, 68 | 3 each | 1 each | 0 | -- | yes | yes |
| 28 | `self_press_volunteering` | 69 | 3 | 1 | 0 | his profile id, ONLY if he volunteers it | yes | yes |
| -- | `root_settle`, only while a compare of his root is deferred | -- | 2 | 1 | 0 | -- | -- | -- |

**The totals** (DERIVED from the table), without phases 21 and 28: 53 most
loads, 29 expected, 3 searches.

**How far 14b reaches** (DERIVED, by the GO's stop rule: stop when the next
phase's most loads would pass what is free):

- with 37 free (before 20:39 IST): phases 1-18 at most loads, or all of them
  at the expected spending;
- with 40 free (after 20:39 IST): phases 1-19 at most loads, or all of them
  at the expected spending.

**K6 asks one thing of him:** keep the dedicated Chrome in front while a "yes"
phase in the last column runs. A refusal costs no load; the phase is simply
run again.

**K6's reach, by the module's own call graph** (VERIFIED,
`which_phases_press.py` on r2b; on r3d, after K9 left, see 11.7):

- 17 runnable phases reach a press.
- K6 holds the 9 that press an editor, an overlay, a self-root link or the
  composer's menus. Each of the 9 reaches a press, and each is runnable.
- The other 8 press menus, pills, switches or disclosures, and are not held:
  `article_drafts`, `c_srch_3a`, `connections_pills`, `creator_hub`,
  `invitation_filter`, `newsletter_form`, `notifications_card` and
  `permalink_menus`. Their close failures stay as they were in session 14,
  each a phase stop or a STOP-ALL by its own rule.

### 11.6 Round 3, the orchestrator's 14b scope, and r3

**ROUND 3, on r2b (`1414e8d8`): a warm re-check, with no BLOCKER and no
MAJOR.**

- **Closed:** MINOR-A, MINOR-C, the NIT, E1, and MINOR-B's Escape and its end
  check. Each was re-run on r2b and on r2, red on r2 and green on r2b. E1 was
  run in process with seven cases.
- **Not closed: MINOR-B2.** A folder press on the composer could still route
  to a conversation and post a read receipt before the guard reads the
  address. On a pessimistic model it opened the unread top row. The fix of
  record is a write block for the length of the round trip.
- The reviewer's three ways to close MINOR-B2: land the write block, accept it
  by name, or run 14b without the composer.
- **NIT-1:** a close by trigger left no step, so a failed re-press could not
  say whether it was made.
- **NIT-2:** the lane's preflight keep case had not been shown red.

**THE ORCHESTRATOR'S 14b SCOPE** (`_TEAM_LEAD_14B_SCOPE.md`, 11:2x IST, deleted
as the ack before r3 was built; a copy is in the lane's scratch):

- **14b holds only built-and-reviewed phases, plus the close fix.**
- **OUT to 14c, each with its own review and READY:**
  - K9. MINOR-B2 is closed for 14b by the reviewer's third way. In 14c K9
    comes back behind a network write block: non-GET requests aborted and
    recorded, a block is STOP-ALL, the route removed on every exit, and the
    route shown in the path;
  - K10;
  - ranks 2, 149 and 151's part 2;
  - the Open-to-Work re-press.
- **Rank 2 against C-SRCH-3a is answered:** C-SRCH-3a stays in 14b. Review
  status outranks rows per load.
- **ADDED to 14b, Chrome's teardown and start:**
  - the operator saw a "Restore pages?" bubble after every session;
  - a graceful close first;
  - `--hide-crash-restore-bubble` with no session restore;
  - the tabs at the first attach.

**r3 (`947f8d73`) and r3b (`448f0f26`, `runner_s14b.py`):**

- **S-1:** K9 and K10 are out of `PHASES`, and their code stays for 14c.
- **S-2:** the observe-only readings and the 15 s watch run at ANY close stop,
  not only a native dialog's. They read the document's focus and visibility,
  whether a modal is open, the focused element's tag, and whether the trigger
  is the element at its own centre.
- **S-3: `tabs_check`.**
  - It reads the DevTools port's `/json/list` by HTTP, with no CDP client.
  - It keeps counts only.
  - It passes only exactly one page, none of it on LinkedIn. Anything else is
    a STOP before load 1, a dead port included.
- **NIT-1 (r3b):** the trigger re-press, Cancel and the declared re-press are
  close steps, each with what became of its press.

**THE CHROME ITEMS** (as round 4 reviewed them; each was hardened after it,
see 11.7):

- **The teardown, `close_chrome_s14b.py`:**
  - the PID is judged first: chrome.exe, this port, this profile;
  - then CDP `Browser.close`, with the process handle waited on up to 10 s;
  - only then the PID judged again and killed;
  - never by image.
- **`teardown_checks_s14b.py` (VERIFIED, 7 of 7)** runs throwaway Chromiums,
  never 9224 or his profile:
  - while running, a profile reads `exit_type` Crashed;
  - the graceful close leaves Normal;
  - a kill leaves Crashed. That is the red half: the state behind a "Restore
    pages?" bubble;
  - it refuses a PID that is not chrome.exe, and a chrome.exe on the right
    port with another profile.
- **`scripts/start_chrome.ps1` (TRACKED):**
  - it passes `--hide-crash-restore-bubble`. The installed Chrome
    158.0.8127.88's binary carries that switch: VERIFIED by reading
    `chrome.dll`, with no Chrome started;
  - ONLY while no Chrome has the profile open, it sets a profile left Crashed
    back to Normal. It changes that one literal value, writes UTF-8 without a
    BOM, and reports the value before and after.
- **Its test, `tests/test_start_chrome_restore_guard.py`:** 4 of 4 on the
  edited script, 4 failed on HEAD's.
- **UNVERIFIED: which exit made the bubble he saw.** The dedicated profile reads
  `exit_type` Normal now, after 14a's teardown by `taskkill /PID`.

### 11.7 Round 4, the orchestrator's final rulings, and r3c and r3d

**ROUND 4, on r3b (`448f0f26`): a warm close-out with 0 blockers, 0 majors,
0 minors and 3 NITs.**

- **Closed:** NIT-1, and NIT-2. The preflight keep case is red on r2 and
  green on r3b.
- **NIT-3:** `tabs_check` was a step in the run order, not a gate in code.
- **NIT-4:** the teardown's judge did not tie the port to the PID, and
  matched the profile by substring.
- **NIT-5:** the starter's guard replaced every occurrence and wrote in
  place, and the startup setting was not read.

**THE ORCHESTRATOR'S FINAL RULINGS** (`_TEAM_LEAD_14B_FINAL.md`, 11:5x IST,
deleted as the ack in this commit; a copy is in the lane's scratch):

1. **Phases are ruled by CONTENT:**
   - rank 31's add-a-position editor is IN;
   - rank 69's volunteering press runs only if he volunteers his profile id
     at the GO;
   - any other self-press that was not in 14a's phases 4-29 is OUT, to 14c;
   - READY states the final phase list by content.
2. **His profile is the main checkout's `_state/chrome-profile`.**
   - 14b starts Chrome with the MAIN checkout's `scripts/start_chrome.ps1`,
     after the orchestrator fast-forwards master to this lane's certified
     head.
   - READY names a head that carries the script fix, has passed lane CI and
     `--full` by sha, and descends from master `9aa4c94`.
3. **The three NITs are REQUIRED:**
   - **NIT-4:** the listener's owning PID equals the judged PID, and the
     profile path matches EXACTLY; if either check fails, no close, no kill,
     a report;
   - **NIT-3:** the tabs check is enforced in code before load 1;
   - **NIT-5:** the guard edits only the two keys, JSON-aware, through a temp
     file and an atomic replace, only while Chrome is down; the startup
     setting is read and recorded, never changed.

**r3c (`90327396`): NIT-3, in code.**

- The meter refuses load 1 of the session unless `tabs_check.json`:
  - reads answered, exactly one page, and none on LinkedIn;
  - is not older than the session's flag;
  - was taken on the browser LAUNCH the port names now.
- A launch is named by a 16-hex digest of the browser endpoint that
  `/json/version` names. That is one value per launch, and the endpoint
  itself is never kept or printed.
- `tabs_check` keeps the digest, and STOPs when the port names none.
- The launch condition goes past the ruling's words. It stops a reading
  taken before a Chrome restart from letting load 1 through.
- **Red first** (VERIFIED, `tabs_checks_s14b.py`; the runner's real meter
  over a fake navigation, an in-memory ledger and a stubbed account meter):

  | runner | its r3 class (T1-T5) | its r3c class (T6, G1-G4, G6, G8) | the control (G5) |
  |---|---|---|---|
  | r3c | 5 of 5 | 7 of 7 | 1 of 1 |
  | r3b | 5 of 5 | 0 of 7 | 1 of 1 |
  | r2b | 0 of 5 | 0 of 7 | 1 of 1 |

- The gate and composer harnesses stub the gate (a named difference). Its
  own checks are the ones above.

**r3d (`4258cf65`, `runner_s14b.py`): the phases by content.**

- Phase 1 is 14a's phase 1, which is not in 4-29. Besides rank 31's press it
  carried three self-presses: the top card's opener, his photo, and Add
  custom button.
- In 14b each of the three is found and counted, and never pressed
  (`PHASE1_OTHER_SELF_PRESSES = False`). Phase 1 presses rank 31's
  add-a-position link only. Its most loads stay 3, an upper bound.
- The rows those three presses serve go to 14c with them.
- **Red first** (VERIFIED, gate check H2: a top card that draws all three,
  each counting its clicks):
  - on r3c, the opener, the photo and Add custom button were each pressed
    once. FAIL, and the presses show the synthetic controls are found;
  - on r3d, none of them was pressed, and rank 31's link was pressed once.
    PASS;
  - the gate's other 82 checks still pass on r3d: 83 of 83, and 0 of the 78
    in the red class failed.
- **K6's reach on r3d** (VERIFIED, `which_phases_press.py`):
  - 16 runnable phases reach a press, and K6 holds 8 of them: `profile`,
    `contact_info`, `learning_goal`, `alert_row`, and the four `self_press`
    phases;
  - the other 8 are the same as on r2b.

**NIT-4: the teardown (`close_chrome_s14b.py`, `6102384c`).**

- The profile is matched by the whole `--user-data-dir` value, normalised
  and case-folded.
- The port's set of listeners must EQUAL the judged PID. If another process
  listens, or two do, or none does, nothing is closed and nothing is killed:
  a report, exit 2.
- **Red first** (VERIFIED, `teardown_checks_s14b.py`; throwaway headless
  Chromiums on ports 9334-9340, never 9224 or his profile; a quiet box):

  | tool | passed | red |
  |---|---|---|
  | `close_chrome_s14b.py` | 11 of 11 | -- |
  | its r1b (the fix before the no-listener ruling, which fell back to the kill) | 10 of 11 | T8 |
  | its r1 (round 4's object) | 7 of 11 | T5, T7, T6, T8 |

- On r1, T5's `Browser.close` went to the port and reached the OTHER
  browser. It closed it, and the judged browser was then killed. That is the
  hazard NIT-4 named, measured.
- **MEASURED:** one port number had two listeners because the second
  Chromium's DevTools server fell back to `::1` when `127.0.0.1` was taken.
  This held in 3 of 3 quiet runs. A note of mine had said that Windows lets
  two listen on one address. That was wrong, and the tool's docstrings are
  corrected.
- **MEASURED: the graceful close is fast to answer and slow to exit.** The
  reply comes in 0.02 to 0.04 s. The process then took from 3.37 s to past
  10 s to exit, across the runs of T1 and T4b on throwaway Chromiums.
  - One run went past 10 s twice, in T1 and T4b, and fell back to the kill.
  - An earlier series did the same on r1 and r1b, while a tree walk of mine
    loaded the disk.
  - The cause of the slow exits was not measured.
- **So the wait is 30 s, not the ruling's "about 10 s"** (r6). The graceful
  path is what keeps the profile clean, and the kill stays the fallback.
  This departs from the ruled number, on that measurement.

**NIT-5: the starter (`scripts/start_chrome.ps1`, tracked).**

- **JSON-aware:**
  - the file is parsed, and only `profile.exit_type` (Crashed to Normal) and
    `profile.exited_cleanly` (false to true) change;
  - each changes by its one literal, which must occur exactly once;
  - the result is parsed again and compared with the original, every other
    key included, before anything is written;
  - it is written beside the file without a BOM and swapped in by
    `File.Replace`;
  - all of this only while no Chrome has the profile.
- **The startup setting is read and reported, never changed:**
  `session.restore_on_startup` and the startup pages.
  - "Continue where you left off", a LinkedIn startup page, or a Preferences
    file that cannot be read are each a warning.
  - Under `-RefuseSessionRestore`, each is a refusal (exit 5).
  - The unreadable case goes past the ruling: what such a profile would
    reopen cannot be ruled out.
- **Red first** (VERIFIED, `guard_checks_s14b.py`: the guard cut out by its
  own markers and run alone on synthetic profiles). The counts on the final
  script, and on every earlier copy, are in r6 and the final pass, below.
- **Its tracked test** was rewritten to read the script's code with its
  comment lines stripped. Its counts are below too.
- This is the version round 5 reviewed (`307aa411`). Round 5 found that its
  startup read missed `Secure Preferences`.

**ROUND 5, on r3d (`4258cf65`), the teardown (`6102384c`) and the start
script (`307aa411`): a warm close-out with 0 blockers, 0 majors and
0 minors.**

- **Closed:** NIT-3 and NIT-4, as ruled. The reviewer's own probes covered
  the gate case by case, through the meter and end to end, and swept all 29
  phases with no reading: 28 stopped at the gate, and `root_settle` loaded
  nothing. The teardown's judge was run in process, 10 of 10.
- **Section 1:** r3d implements it, and no other path presses the three.
- **NIT-5, NOT closed in one clause.** The startup setting was read from
  `Preferences` only. On Windows Chrome keeps a tracked pref's value in
  `Secure Preferences`. The reviewer read his profile for names and counts
  only: all 12 tracked values that hold one hold it there. So the record
  would read "absent" exactly when the setting is set.
- **`found`** must be a STOP, read from the outcome field. Both outcomes
  exit 0.
- **NIT-6 (new):** a listener read that timed out escaped as a traceback,
  with no report.
- **NIT-7 (new):** nothing tied the port to the dedicated profile at the
  attach.
- **The close checks' crash in `final/`** was the lane's own doing. A chunk
  on r3c was stopped mid-run when r3d superseded it, and its process tree
  was killed by PID, so the harness's Chromium died under it. That run's
  output was the one on disk. On r3d the same checks ran to completion at
  13:11 (24 of 24, and 7 of 7), and no harness change was needed.

**THE ORCHESTRATOR'S RULING ON ROUND 5** (`_TEAM_LEAD_14B_R5.md`, 12:5x IST,
deleted as the ack in this commit; a copy is in the lane's scratch):

1. NIT-5 finished: read both files, red first on the reviewer's two cases,
   and measure on a THROWAWAY profile where Chrome 158 writes the setting.
2. NIT-7 in CODE: at the attach the tabs check confirms that the port's
   listener runs the dedicated profile, by NIT-4's exact match. A `found`
   whose Chrome fails it is a STOP before load 1. READY's procedure also
   reads the outcome field.
3. NIT-6: a report and a non-zero exit, never a traceback.
4. The final pass on the final sha, with the close checks completing.

**MEASURED, where Chrome 158 writes the setting** (VERIFIED,
`measure_restore_pref_s14b.py`):

- The setup: the installed Chrome 158.0.8127.88, headless, on a THROWAWAY
  profile and port 9346, every host mapped to NOTFOUND. Never his profile.
- The control: never set, the setting is in neither file. `Secure
  Preferences` already holds its MAC.
- Then it was set to 1 the way the settings page sets it
  (`chrome.settingsPrivate`, read back 1), and the browser closed gracefully.
  The value is in `Secure Preferences` ONLY: `Preferences` has no such key.
- So the reviewer's DERIVED is VERIFIED for this build. A read of
  `Preferences` alone misses it every time.

**r3e (`fd3bf239`, `runner_s14b.py`): NIT-7, in code.**

- `tabs_check` judges the port's listener with the teardown's own judge,
  loaded from `close_chrome_s14b.py` (pinned). It must be exactly one
  listening PID on every address, chrome.exe, this port, and the whole
  `--user-data-dir` equal to the main checkout's `_state/chrome-profile`.
- Otherwise it is a STOP before load 1, and the reading keeps
  `dedicated: false`. The meter's gate on load 1 requires `dedicated: true`.
  So a `found` start whose Chrome is not the dedicated one is a STOP in code.
- **Red first** (VERIFIED, `tabs_checks_s14b.py`; the judge's two OS reads
  are replaced, so nothing of the machine is read):

  | runner | r3 | r3c | r3e (N2-N6) | control |
  |---|---|---|---|---|
  | r3e | 5 of 5 | 7 of 7 | 5 of 5 | 1 of 1 |
  | r3d | 5 of 5 | 7 of 7 | 0 of 5 | 1 of 1 |
  | r3b | 5 of 5 | 0 of 7 | 0 of 5 | 1 of 1 |
  | r2b | 0 of 5 | 0 of 7 | 0 of 5 | 1 of 1 |

  N2-N6 are: another profile (his everyday Chrome, say), two listeners, a
  listener that is not chrome.exe, a read that fails, and a profile that
  only starts with the dedicated one. On r3d, load 1 was made in each.

**The Chrome items, r6:**

- **NIT-5's clause (`scripts/start_chrome.ps1`):** `session.restore_on_startup`
  and `session.startup_urls` are read from BOTH files, and a value in either
  counts. A `Secure Preferences` that does not parse is a refusal under the
  switch. Neither file is written by the read, and the report says which file
  the value came from.
  - Red first (VERIFIED, `guard_checks_s14b.py`): the script 15 of 15;
    `307aa411` 12 of 15, with G12, G13 and G14 red.
  - Its tracked test: 8 of 8 on the script, 5 of 8 on `307aa411`, 0 of 8 on
    HEAD's.
- **NIT-6 (`close_chrome_s14b.py`):** a process read, a listener read or a
  `taskkill` that fails is reported, never a traceback. A failed listener
  read is `refused_listener_read_failed`, exit 2, with nothing closed.
- **NIT-7, also in the preflight (`os_check.ps1`):** every phase's preflight
  runs it, and STOP-ALLs `listener_not_the_dedicated_profile` on False.
  - Its judge read the FIRST listener row and matched the profile by
    SUBSTRING. Those are the two gaps NIT-4 closed in the teardown.
  - It now asks for exactly one listening PID on every address, a browser
    process naming this port, and the whole `--user-data-dir` equal to the
    dedicated profile, normalised and case-folded.
  - This covers every phase, not only load 1, so a browser swapped after
    load 1 is caught at the next phase's preflight.
- **Red first** (VERIFIED, `teardown_checks_s14b.py`: T9 in process, O1-O4
  on throwaway Chromiums):
  - the tool with the new `os_check.ps1`: 16 of 16. O1 reads True; O2, O3
    and O4 read False;
  - round 5's tool with the old judge: T9 red (the timeout escaped), and O2
    red (a prefix profile judged True);
  - also O4 red. A foreign browser held `127.0.0.1` and the judged one `::1`.
    The old judge's first row was the judged browser, so it said True, while
    the attach, which uses `127.0.0.1`, would drive the foreign one.

**ROUND 6, on r3e (`fd3bf239`), the teardown (`83d17023`), `os_check.ps1`
(`0134d152`) and the start script (`fe00bd14`): 0 blockers, 0 majors,
0 minors, and 0 NITs open.**

- **NIT-5's clause, NIT-6 and NIT-7 are CLOSED as the orchestrator worded
  them** (VERIFIED by the reviewer's own probes):
  - 21 synthetic profiles, `Secure Preferences` byte-identical after each,
    and no false refusal on his profile's shape today;
  - every failed read, and a failed kill, reported with a non-zero exit;
  - the attach's judge right across ten cases, every one passing on r3d;
  - `os_check`'s judge 10 of 10 on synthetic tables, against the old one's
    6 of 10.
- **No regression on r3e:** NIT-3's sweep of all 29 phases, the gate cases,
  phase 1 by content, the entry order and the close steps.
- **The named departure:** the 30 s wait. The reviewer saw no safety cost,
  only time: "at most 20 s more at a teardown whose browser is slow to
  exit".

**THE FINAL PASS** (VERIFIED, `final_pass_s14b.sh` run from a frozen copy,
serially, chunk by chunk, 13:34 to 14:48 IST). It ran on
the final runner `fd3bf239` (r3e), the teardown `83d17023`, `os_check.ps1`
`0134d152` and the start script `fe00bd14`. The outputs are beside the
runner, in `final/`.

| run | on | result |
|---|---|---|
| provenance | r3e | the harness, the package, the people gate and the slot reader from the worktree; the job pipeline from the installed skill |
| the close checks | r3e | red class 24 of 24, controls 7 of 7: they ran to completion |
| the table checks | r3e / r2b | 3 of 3 and the control, and K9's 14c code 6 of 6 / 1 of 3 (K8 and K10 red) |
| the tabs checks | r3e | 18 of 18 |
| the tabs checks, red sides | r3d / r3b / r2b | the r3e class 0 of 5 / the r3c class 0 of 7 and r3e 0 of 5 / 1 of 18; the control 1 of 1 on each |
| the close checks, red sides | s14 / r1 / r2 / r2b / r3 | each snapshot's own class red: 0 of 11 / 0 of 8 / 0 of 2 / 0 of 1 / 0 of 2; the controls 7 of 7 on each |
| the teardown checks | the tool, with `os_check.ps1` | 16 of 16; the graceful exits 1.73 s (T1) and 2.37 s (T4b) |
| the teardown checks, red sides | r2 with the old judge / r1b / r1 | T9, O2 and O4 red / and T8 / and T5, T7, T6 and T8 |
| the gate checks | r3e / r3c | 83 of 83, the red class 0 of 78 failed / 82 of 83, H2 red |
| the Open-to-Work checks | r3e | 8 of 8 |
| the composer checks (14c's kept code) | r3e | 3 of 3, the controls 2 of 2 |
| the entry refusals | r3e / r2 | every refusal as named, before any browser contact / not (NIT-2's red) |
| the start script's tracked test | the script / `307aa411` / json1 / nit5 / round 4's / HEAD's | 8 of 8 / 5 / 5 / 3 / 1 / 0 of 8 |
| the restore guard | the script / `307aa411` / json1 / nit5 / round 4's | 15 of 15 / 12 / 11 / 9 / 6 of 15 |
| the items | `live15` | every check passed: `842bced3`, identical to 14a's |

T1 and T1b also failed on all three older tools, and that was not by
design. Each of those runs followed another run's teardown. Its first
graceful exit took longer than the old 10 s wait, so the tool fell back to
the kill. The tool, which ran first, closed its browsers in 1.7 s and 2.4 s.
Its 30 s wait is the margin.

**THE WAITS** (the orchestrator's `_TEAM_LEAD_WAITS.md` and
`_TEAM_LEAD_SPLIT.md`, 14:1x and 14:3x IST, deleted as the ack in this
commit).

- **The orchestrator's measurement.** The pass above took 74 minutes, and
  the box was 86% idle through it. The waits were idle time, not work.
- **The cause** (VERIFIED). The runner was written for live pages. It
  settles after every load and press with 55 literal real-time sleeps, gives
  a close 2.5 s in 0.25 s polls, watches a close stop for 15 s, and bounds
  its condition loops in real time. On the checks' synthetic pages nothing
  renders late unless a model says so, so almost all of that time was idle.
  - The gate checks did NOT wait on the 20 s page pace: their meter already
    runs on a fake clock.
- **CHECK MODE** (`fastclock_s14b.py`): each in-process harness gives the
  runner and the harness an `asyncio` whose `sleep` is scaled by 0.1.
  Playwright, the pages' own timers and the runner's condition loops keep
  real time. A loop that never meets its condition still runs its real
  bound.
- **The named real-time exceptions:**
  - the Open-to-Work "race" model, a focus stolen 50 ms after the focus
    move, against Playwright's real latency;
  - gate check Q3, a document 0.4 s after its load, during the capture's
    settle;
  - the teardown's T1 and T4b, which time the graceful exit itself;
  - the gate's slow-answer models (Q1, Q1b, Q2, Q9, Q10), where the
    harness's own 3 s and 7 s route delays ARE the test.
  - The "slow" and "slow6" close models keep their place differently: their
    timers scale with the clock, as factor x 2.5 s and factor x 6 s.
- **In parallel:**
  - the gate runs in four slices;
  - the teardown runs in three slices on its own ports;
  - the tabs checks each take their own fake port;
  - the entry refusals run their cases six at a time.
- **Each step is now under 2 minutes, and every result matches the
  real-clock pass, case for case** (VERIFIED, `final_pass2_s14b.sh`,
  15:31 to 15:46 IST, `final2/`).

| set | before: the real-clock pass, serially | after: check mode | the runner's own sleeps, as check mode's clock counted them |
|---|---|---|---|
| the close checks, r3e and 5 red sides | 400 s on r3e; 1824 s for the six | 106 s on r3e; 110 s for the six, together | 353 s requested on r3e, 64 s slept, 32 s of it the race on the real clock |
| the gate checks, r3e and r3c | 786 s and 792 s | 95, 66, 49 and 106 s per slice; 110 s per sha, its slices together | 1353 s requested on r3e |
| the teardown, the tool and 3 red sides | 92 to 121 s each; 422 s for the four | the close slice alone 53 s; the NIT and judge slices 71 to 105 s, together | none: real Chromium launches and exits |
| the Open-to-Work and composer checks | 91 s each | 25 s and 48 s | 85 s and 78 s requested |
| the entry refusals, r3e and r2 | 43 s each | 26 s and 21 s | none: a Python start per case |
| tabs, table, guard, starter, pytest, items, provenance | 1 to 23 s each | 1 to 36 s each | none to speak of |
| **the whole pass** | **74 min** | **about 9.5 min of steps, each under 2 min** | |

- The gate's "requested" overcounts its real-clock sleeping. Condition
  loops poll more often on a faster clock, and the real-clock gate took
  786 s in all.
- **The 5-minute target is NOT met.** Each step is as long as its slowest
  run, about 100 to 110 s: the close checks on r3e and r3, and the gate's
  main and r2 slices.
  - Under 5 minutes would need the close and gate steps together, about 17
    browsers at once. The real-clock cases would then run under that load,
    so it was not tried.
  - The rest of the floor is the named exceptions above.
- **Two runs hit the 115 s bound under load, and were run again** with less
  beside them:
  - the teardown's NIT slice on r1 took 105 s on its second run;
  - the entry refusals on r2 took 21 s once their cases ran six at a time.
- **What runs in the pass is confirmed.** Every green-side run names r3e
  (`runner_s14b`, `fd3bf239`). The r3c gate run at 14:33 was H2's RED
  side, by design, after its green run on r3e from 14:17 to 14:30.

**LIVE-RUNNER-CHECKS-ON-CI, a proposal (built nothing).** The check sets that
need no gitignored item could move into the tracked repo as pytest modules,
scrubbed of identity, so that free CI runs them in shards on every lane
push:

- The fully synthetic sets qualify as they stand: the tabs checks, the gate
  checks (synthetic pages and the tracked AI-route fixture), the composer
  checks, and the restore guard and start-script test.
- The fixture sets qualify too: the close, table and Open-to-Work checks
  read `tests/fixtures/live14`, which is tracked.
- The guard and teardown checks need CI's Windows cell: PowerShell 5.1,
  `Get-NetTCPConnection`, and a throwaway Chromium.
- The obstacle is that every set imports the runner, and the runner lives
  in the main checkout's gitignored `_state`. It carries absolute workspace
  paths and the installed skill's path. So the first build step is the
  runner's tracked, path-free form, with paths from configuration.
- `prepare_items` (session 12's preserved readings), provenance (this
  machine's paths) and the entry refusals' digest of the pinned store stay
  local, or take synthetic stand-ins.

### 11.8 READY for session 14b (2026-11-28, 14:5x IST)

Session 14b's Phase A is done:

- the close fix, the 14b table, and Chrome's start, tabs check and teardown
  are built, and each is shown red first;
- the review is closed on the final shas (round 6: 0 open at any severity);
- the final pass ran on those shas twice, with the same results:
  - on the real clock, 13:34 to 14:48 IST;
  - in check mode, 15:31 to 15:46 IST, in steps each under 2 minutes (11.7,
    "the waits").

**NAMED DEPARTURES from the rulings' words:**

- The teardown waits 30 s for a graceful exit, not about 10 s. Exits were
  measured past 10 s, and the reviewer saw a cost in time only.
- Two refusals go past the words:
  - the tabs gate also asks for the same browser launch;
  - the start script also refuses a preferences file it cannot read.

HOLD: PHASE B starts only on a `_TEAM_LEAD_GO.md` that names these pins,
with the operator at the console, after the orchestrator fast-forwards
master to this head.

**THE PINS** (full values in the session's gitignored `_state/live15/pins.json`,
written after the commit that adds this section):

| pin | sha256 (short) |
|---|---|
| `runner_s14b.py` (r3e) | `fd3bf239d6d514f9` |
| `scripts/people_gate.py` | `6ff3afb732ed1546` (unchanged) |
| the harness, `scripts/_probe_live_lane_session_2.py` | `a5c10ae992f691b8` (unchanged) |
| `linkedin_server/volunteering_route.py` (the one matcher) | `5635e69f595bfa3c` (unchanged) |
| `linkedin_server/self_profile.py` (the shipped wait) | `b39b615b2c476b94` (unchanged) |
| `scripts/start_chrome.ps1` (tracked; at the GO the main checkout's copy must match it) | `fe00bd14416e64e8` |
| `close_chrome_s14b.py` (the teardown, and the judge `tabs_check` loads) | `83d17023fc3a9da4` |
| `os_check.ps1` (every phase's preflight) | `0134d152b71bd613` |
| the prepared items (gitignored, `live15`) | `842bced39d3678bb` (identical to 14a's) |

**THE HEAD** is the commit that adds this section.

- It descends from master `9aa4c94` and carries the start script's fix.
- Lane CI and `--full` certify it by sha. Their run ids are in the READY
  message, and the head is in `pins.json`.

**THE PHASES, BY CONTENT** (the orchestrator's 14b rulings, section 1;
`PHASES` in r3e, unchanged since r3d, in 11.5's order):

| # | phase | rank | what it does, and what it presses |
|---|---|---|---|
| 1 | `profile` | 3, 31 | E5: his root through the shipped loader, the top card read, one scroll pass, and the skill ids and insight indices that phases 7 and 24 name, kept in gitignored state. Then rank 31, ATTENDED: the Experience section's add-a-position link, matched exactly, pressed once, its editor read and closed. NOT pressed: the top card's opener, his photo and Add custom button (OUT, to 14c) |
| 2 | `c_srch_3a` | 132 | TOGGLE-FIRST: one AI-route search. The Easy Apply toggle is pressed once and pressed back, each press a re-query recorded before it; then All filters is opened, read and closed. The session's 3 searches |
| 3 | `newsletter_form` | 150 | Manage's Create newsletter pressed and its form read by closed words. Nothing typed; its submit drawn, never pressed; closed without submitting |
| 4 | `discovery` | 161 | one load, read; the suggestion cards' controls never pressed |
| 5 | `featured` | 34 | read only |
| 6 | `manage_syncing` | 158 | read only |
| 7 | `skill_form` | 40, 102 | his skill's edit form, by the id E5 drew; nothing typed, chosen or saved |
| 8 | `intro_landing` | 103 | one load of the intro editor's address, and where it lands; nothing pressed |
| 9 | `contact_info` | 30 | ATTENDED: the top card's Contact info link, then the overlay's Edit contact info, each matched exactly; the form closed, then the overlay |
| 10 | `article_drafts` | 1 | Manage's Drafts pressed, the list read; nothing pressed in it |
| 11 | `invitation_filter` | 26 | the invitation manager; the first filter pill's disclosure opened and closed by Escape; nothing chosen |
| 12 | `permalink_menus` | 95 | one post of a member he follows and one of a Page (the prepared items), each post's control menu opened and closed; nothing in it pressed |
| 13 | `key_skills` | 102 | ATTENDED: his skills details page, read; nothing pressed |
| 14 | `connections_pills` | 109 | the Locations and Companies pills, each opened and closed by Escape; nothing chosen |
| 15 | `creator_hub` | 111 | `/dashboard/` and where it lands; the hub's navigation read; one overflow control, if exactly one is drawn, opened, read and closed |
| 16 | `notifications_card` | 115 | one card's More options opened, read and closed by Escape; nothing in it pressed |
| 17 | `self_variant` | 117 | E18 and E19: his root's self variant, then the contact-info overlay by its own address; labels only, nothing pressed |
| 18 | `learning_goal` | 144 | ATTENDED: the Career goal section's control pressed once; what opens read and closed; nothing typed or chosen |
| 19 | `alert_row` | 145 | ATTENDED: one alert row's control, pressed only on an allowed label that is no toggle; read and closed; no change |
| 20 | `learning_saved` | 147 | read only |
| 21 | `post_analytics` | 154 | a post of his, read; ONLY if he names one at the GO |
| 22 | `search_history` | 156 | read only |
| 23 | `download_data` | 157 | read only |
| 24 | `skill_insights` | 71 | one skill-insights page, by the index E5 drew; read |
| 25-27 | `self_press_summary`, `self_press_secondary_language`, `self_press_services` | 64, 67, 68 | ATTENDED: his root, then ONE self-root press each (his About, his profile language, his services) through the one matcher; what opens read and closed; his root compared before and after |
| 28 | `self_press_volunteering` | 69 | the same press, ONLY if he volunteers his profile id at the GO; otherwise it refuses before any browser contact |
| -- | `root_settle` | -- | only while a compare of his root is deferred |

**OUT of 14b, by name, to 14c:**

- K9, the composer's Archived round trip;
- K10, rank 151's read;
- ranks 2, 149 and 151's part 2;
- the Open-to-Work re-press;
- phase 1's opener, photo and Add custom button presses.

Rank 23, `recommendations`, ran in 14a.

**THE PLAN AND THE SPLIT:** section 11.5.

- The table holds 28 lines. Without phases 21 and 28 they come to 53 most
  loads, 29 expected and 3 searches.
- With 37 free (before 20:39 IST), 14b reaches phases 1-18 at most loads.
  With 40 free, it reaches phases 1-19.
- At the expected spending, it reaches every phase.

**WHAT HE IS ASKED** (K6): keep the dedicated Chrome in front while
`profile`, `contact_info`, `learning_goal`, `alert_row` or one of the four
`self_press` phases runs. A refusal costs no load, and the phase is run again.

**THE STOP LINES:**

- section 3's 22 kinds. The 14b runner's `STOP_ALL_KINDS` holds the same 22,
  read by AST on r3e;
- `tabs_check`'s STOP before load 1: not exactly one page, a LinkedIn tab, no
  browser endpoint, or a port whose one listener is not the dedicated
  profile's browser;
- the meter's refusal of load 1 without a passing tabs check taken on this
  launch;
- the start script's refusal (exit 5), and any `outcome` field but
  `started`;
- each phase's preflight STOP-ALL when the port's one listener is not the
  dedicated profile's browser (`os_check.ps1`, hardened in r6);
- the teardown's refusal: a report, with no close and no kill.

A STOP-ALL ends the session. UNREAD-SKIPPED holds.

**WHAT 14b MAY STILL HIT** (round 1's section 0): a live dialog may ignore a
dispatched Dismiss, or close later than its grace and the 15 s watch. Then
the session STOP-ALLs again. That fails closed, and every step and the
observe-only readings are recorded.

### 11.9 The commands for 14b's PHASE B, on GO

Every runner call takes the same environment:
`LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 LINKEDIN_MIN_INTERVAL_S=20 LIVE_LANE_SESSION_DIR=live15`.
The runner and its tools are in the main checkout's
`_state/live-runner/s14b/`, and each step runs in the foreground.

1. **Before Chrome:**
   - `verify_pins_s14b.py` must print ALL-MATCH against the GO's pins. It
     counts the MAIN checkout's `scripts/start_chrome.ps1` too, which matches
     only after the orchestrator's fast-forward.
   - `os_check.ps1`: 9224 down, no flag, no lock, no Chrome on the profile.
   - The pinned ledger's free count is read; it sets 14b's room.
2. **Chrome, the flag, the tabs:**
   - The dedicated Chrome is started with the MAIN checkout's
     `scripts/start_chrome.ps1 -RefuseSessionRestore`.
     - Its report's `outcome` field must read `started`. A `found` is a STOP:
       a browser was already up, and the guard and the startup read did not
       run. The exit code cannot tell them apart, since both exit 0. In code,
       `tabs_check` also STOPs on a `found` whose Chrome is not the dedicated
       one.
     - `exit_type_after` must read Normal or absent.
     - Its `pid` is the browser's, and it is kept for the close.
   - `os_check.ps1` again.
   - `runner_s14b.py flag_on`.
   - `runner_s14b.py tabs_check`: exactly one page, none on LinkedIn, and the
     port's one listener the dedicated profile's browser, or a STOP before
     load 1. The meter refuses load 1 without this reading.
   - The harness's `attach_check`, as `--only attach_check` (it takes its
     keys by `--only`, and refuses before any contact without it; 12, THE
     START), 0 loads.
3. **The phases, in 11.8's order.** The preflight refuses a phase whose most
   loads do not fit the room, and the next one is then tried.
   - After `profile`, the caller names the items E5's reading drew
     (`name_items_s14b.py skill`, then `name_items_s14b.py skill_index`).
   - `c_srch_3a` and `permalink_menus` take
     `--items _state/live15/items_prepared.json`.
   - `post_analytics` takes the post he names. `self_press_volunteering`
     takes his profile id, from a gitignored items file the runner deletes
     once read. Without them, both refuse before any browser contact.
4. **The end:**
   - `root_settle`, if a compare of his root is pending;
   - `close_chrome_s14b.py --port 9224 --pid <the browser's pid> --profile
     <the main checkout's _state/chrome-profile>`, while the flag still
     stands, so the box is quiet for it. It sends `Browser.close` first, and
     kills by PID only as the fallback. The path it took is recorded. A
     refusal closes and kills nothing, and is reported;
   - `flag_off`, which refuses while a compare is pending;
   - `os_check.ps1`: 9224 down, 0 clients, no Chrome on the profile, no
     lock, no flag.

## 12. Live session 14b, the run (2026-11-28, attended)

**Run by `live14b`, the successor lane.** live-s13 prepared and certified
14b (11.8). It could not be resumed after the machine restart, because its
history stalled, and it is STOPPED. live14b worked only from this record, its
pinned files and the GO, in 11.9's order exactly. It edited none of the
pinned files: `verify_pins_s14b.py` read ALL-MATCH before Chrome started and
again after the close.

**THE GO** (`_TEAM_LEAD_GO.md`, 16:2x IST, with `_TEAM_LEAD_CWD.md`). Both
were deleted as the ack at 16:53:58, after a copy of each was kept in the
lane's gitignored scratch.

- The head `9ec91965`, with 11.8's nine pins. The orchestrator measured
  master fast-forwarded to it, and lane CI, the full matrix and master's push
  CI green on that sha.
- The operator at the console ("resume with full throttle max", 16:19).
- At most 37 loads (the ledger read 3 at 16:20), at most 40 a session, 20 s
  apart, and at most 3 searches. UNREAD-SKIPPED. `post_analytics` and
  `self_press_volunteering` OFF. Any STOP ends the session.
- The CWD note: every git command takes `-C` and this worktree, and every
  write an absolute path.

**BEFORE CHROME** (16:53 to 16:54 IST, VERIFIED):

- `go_pins_check_s14b.py` (disposable, the lane's scratch) read the GO's nine
  pin lines and its head. All equal `pins.json`: GO-MATCH True.
- `verify_pins_s14b.py`, without `--before-fast-forward`: ALL-MATCH True.
  The main checkout's start script was counted and matched; the head
  `9ec91965`; the tracked tree clean.
- `os_check` (16:54:07): 9224 down, 0 clients, no Chrome on the dedicated
  profile, no lock, no flag.
- The pinned ledger (`ledger_state.py`, live-s13's read-only disposable): 3
  LinkedIn page loads in the trailing 12 h, so 37 free. Session 14's 3 leave
  the window at 20:39:17 IST.
- **Disk and the GO differ on one point.** `os_check`'s boot time reads
  2026-11-26 08:55, before and after the session, not a restart at about
  16:15. A power cycle under Windows fast startup keeps the last full boot's
  time (DERIVED; UNVERIFIED here). No step depends on it: the premises the run
  needs (9224 down, no Chrome on the profile) were measured.

**THE START** (0 loads, VERIFIED):

- 16:54:46: the main checkout's `scripts/start_chrome.ps1
  -RefuseSessionRestore`. Outcome `started`, Chrome 158, `exit_type` Normal
  before and after. The startup setting was absent from both files, with 0
  startup pages and 0 on LinkedIn. The browser's pid was kept for the close.
- 16:55:15: `os_check`. 9224 was held by one listener, the dedicated
  profile's one browser process (`listener_is_the_profile_browser` True), with
  0 clients and no lock.
- 16:55:42: the flag raised.
- 16:55:50: `tabs_check`. Answered: 1 page, 0 on LinkedIn, 1 blank; 1
  listener, and it is the dedicated one; the launch digest kept. Exit 0.
- `attach_check`. The first call, named as 11.9 names it, refused before any
  contact: the harness takes its keys by `--only`. With `--only
  attach_check`: PASS `[0, 1, 0]`, restored, 0 loads (16:56:18).
- A status message went to the orchestrator before phase 1. K6 asks him to
  keep the dedicated Chrome in front during the attended phases.

### 12.1 The loads

| load | IST | phase | landing | what it read |
|---|---|---|---|---|
| 1 | 16:57:26 | 1 `profile` (E5) | served, same depth, another url: his root | E5 proved his root at its first load; the top card; the scroll pass; no skill item |
| 2 | 16:58:22 | 2 `c_srch_3a` | served exact | the AI-route search; Easy Apply pressed on and back; STOP-ALL `restore_failed` |

Every load was recorded in the pinned ledger before it was made. Neither drew
a wall, a checkpoint or a challenge (each: walled False, 0 challenge terms).
The two were 56 s apart, and the window was `fronted` for both.

### 12.2 What each phase showed

**Phase 1, `profile`: exit 0, 1 load.**

- **E5:** his root served through the shipped loader, and the self rule
  proved it at its first load, by his edit controls (4 on the landed member,
  0 edit routes on another). The self block was open.
- People gate v2 withheld the raw (L1 10, N1 52, R1 11, R2 9), and the
  skeleton was kept.
- The top card drew More 1 (0 visible), Resources 1 (1), Open to 2 (1),
  Enhance profile 2 (1) and Add profile section 0, as in 14a. The editor
  routes were `edit/forms/summary/new/` 1, `edit/intro/` 1,
  `edit/secondary-language/` 1 and 1 other form, and the same after the
  scroll pass.
- **OUT by content, found and not pressed** (r3d): the top-card opener
  (Resources), the photo (1 image button) and Add custom button (0 drawn).
- **The scroll pass: 1 step.** After it, the section words Experience,
  Education, Skills, Services and Recommendations each read 0 in `main`.
  E23's input: 0 skill ids and 0 insight indices.
- **Rank 31: not pressed.** No Experience section was found, and the
  add-a-position link was drawn 0 times (`not_exactly_one_link`).
- **The scrolled skeleton is byte-identical to the first** (VERIFIED, by
  sha256).
- **DERIVED, from the code and the output:** the pass tests for the bottom
  before each scroll. So "1 step" means the document already read as at its
  bottom at the first test, and no scroll was made. A page that scrolls in an
  inner element, not the document, reads that way. Which element scrolls is
  UNVERIFIED. 14a's photo-press reading also saw sections render late (10.5).
- So `name_items_s14b.py skill` and `skill_index` each printed "drawn by
  E5's reading: 0" and NOTHING TO NAME (exit 2). Phases 7 and 24 have no item.

**Phase 2, `c_srch_3a`: exit 4, STOP-ALL `restore_failed`, 1 load, 3
searches.**

- Served exact. People gate v2 withheld the raw (R1 1, R2 1), and the
  skeleton was kept.
- **The first view:** the AI route; 25 cards, ids and rows, 0 unparsed; the
  total capped at 99 shown; the pager's 3 indicators and a visible next
  control. The Easy Apply toggle had 2 inputs (1 visible), 0 checked. The
  address keys: `currentJobId` and `keywords`.
- **ON** (search 2, recorded before the press at 16:58:44): it took effect.
  Checked 2 and 6 ids shared with the first view. The keys `f_AL` (true),
  `origin` and `referralSearchId` were added, and `currentJobId` changed. No
  document loaded.
- **OFF** (search 3, recorded before the press at 16:59:04): checked 0, and
  25 of 25 ids shared with the first view. The keys: `currentJobId`,
  `keywords`, `origin` and `referralSearchId`. No document loaded.
- **The judge read RESTORED False.** The toggle and the id set came back, and
  `f_AL` is gone. But `origin` and `referralSearchId`, which the ON press
  added, stayed, and the address is not the one before the press. Values are
  not kept, so whether `currentJobId` came back is not shown. STOP-ALL
  `restore_failed` at `c_srch_3a_easy_apply`; the runner closed its tab.
  **Corrected in 13.1:** the judge already ignored `origin`, so
  `referralSearchId` alone failed it.
- Not reached: All filters, opened, read and closed.

### 12.3 The close: no load after the STOP-ALL

- No compare of his root was deferred: phase 1 pressed nothing on his root,
  and `root_signatures.json` is absent. `root_settle` was not run, since
  nothing loads after a STOP-ALL.
- 16:59:50: `close_chrome_s14b.py --port 9224 --pid <the browser's> --profile
  <the dedicated profile>`, with the flag standing. It judged "the dedicated
  browser", 1 listener on the port, owned by the pid. `Browser.close` was
  sent and answered in 0.96 s, and the browser exited 1.56 s later. The path:
  `cdp_browser_close`. Nothing was killed. Exit 0.
- 17:00:07: the flag lowered; no compare was pending.
- 17:00:13: `os_check`. 9224 down, 0 listeners, 0 clients, no Chrome on the
  profile, no lock, no flag. His own Chrome was never named or signalled.
- **No restore prompt.** After the close, the profile's `Preferences` read
  `profile.exit_type` Normal (VERIFIED, a read only). Chrome offers a restore
  only on a Crashed mark (the start script's measurement, in its header), so
  the next start offers none (DERIVED).
- The session folder is preserved in the main checkout's gitignored
  `_state/preserved/live15-2026-11-28`: 16 files, each identical by sha256.
  No raw page was kept (`raw_kept` False in both readings).

### 12.4 The ledgers

- The session ledger: 2 loads, 3 searches.
- The pinned account ledger: 2 records for 14b (`live-s13/15/live_census`),
  so 5 in the trailing 12 h and 35 free. Session 14's 3 leave the window at
  20:39:17 IST, and 14b's 2 at 04:58:19 IST on 11-29.
- The two ledgers agree at 2.

### 12.5 The GO's accepted departures, recorded

The GO's ruling 1 ACCEPTED all three named in 11.8, each stricter than ruled:

- the teardown's 30 s exit wait. Here the browser exited 1.56 s after the
  reply;
- the tabs gate's same-launch condition. It held: the reading was taken on
  this launch;
- the start script's refusal of a preferences file it cannot read. It was not
  met: both files were read.

### 12.6 What 14b did not reach

- **Not run because of the STOP-ALL:** phases 3 to 20, 22, 23 and 25 to 27.
- **No item either:** phases 7 and 24, since E5's reading drew no skill item.
- **OFF by the GO:** phases 21 and 28.
- **From phase 1:** rank 31's press. **From phase 2:** All filters.

### 12.7 Rows moved: none

Each line was a capture, and a capture moves no row by itself (10.7). The two
skeletons are preserved, not exported to tracked fixtures: no order named an
export for this session.

### 12.8 What needs the orchestrator

1. **Rank 132's round trip cannot pass this judge on this route.** LinkedIn
   added `origin` and `referralSearchId` on the ON press and kept them after
   the OFF press. The view came back (the toggle unchecked, `f_AL` gone, 25 of
   25 ids), but the judge asks for every touched key back. It needs a ruling:
   either the two keys are judged volatile, as `ROOT_VOLATILE` is for his
   root, or the toggle's round trip is dropped from 14c. (Ruled VOLATILE,
   narrowly, in 13; and corrected in 13.1: `origin` was volatile already.)
2. **Phase 1's scroll pass made no scroll.** E23's skill items, rank 31's
   link, and phases 7 and 24 wait on a pass that scrolls the element that
   scrolls and waits for the late sections. That is offline work, red first
   on this session's skeleton, before 14c.
3. **The account:** 35 free now, 37 after 20:39 IST, and 40 after 04:58 IST
   on 11-29.
4. **Disk and the GO** differ on the boot time (BEFORE CHROME, above).

## 13. Session 14c, PHASE A (offline): the three fixes

Everything here is offline. There were zero loads, and 9224 was untouched;
the flag was never raised. The only browsers were the checks' own headless
Chromiums, with every request aborted.

**THE ORDER** (`_TEAM_LEAD_14C.md`, 17:1x IST). It was deleted as the ack at
17:12:35, and a copy is in the lane's gitignored scratch.

- **Ruling 1 (12.8.1), VOLATILE narrowly.** After a filter round trip,
  `origin` and `referralSearchId` are judged by NAME, their values ignored.
  - That holds ONLY when every `f_*` key, the first view's ids (all 25)
    and the 0-checked toggle restore exactly.
  - Any other added or missing key still STOPs.
  - Red first, with three fixtures.
- **Ruling 2:**
  - measure why phase 1 never scrolled, and fix it;
  - each step must prove that the position or the skeleton changed;
  - zero progress is a named STOP (`scroll_no_progress`) before any item
    is drawn;
  - red first, on a fake page where the old code reports done without
    moving.
- **Ruling 3:** 11.9's attach_check line gains `--only attach_check`. Done
  in 11.9 above.
- **The scope:** 14c is r3e plus these three fixes and nothing else. K9,
  K10, ranks 2, 149 and 151 and the Open-to-Work re-press move to 14d.

### 13.1 What failed 14b's restore, measured (a correction to 12.2, 12.8 and lesson 17)

- **r3e's judge (`view_restored`) already treats `origin` as volatile.** It
  is one of the ten `VOLATILE_KEYS` the warm re-check listed as LinkedIn's
  bookkeeping keys, so the judge never looked at it.
- **`referralSearchId` alone failed it** (VERIFIED, check L1 below):
  - the shipped judge, on 14b's live key names, reads False;
  - it reads True once `referralSearchId` alone is taken away;
  - the values are not kept, so synthetic ones stand in. The verdict
    depends only on which keys are present and equal (DERIVED from the
    judge's code).
- Section 12 named both keys as the cause. The reading was right that both
  stayed; the cause was one of them.

### 13.2 Why phase 1 never scrolled (the measurement the order's item 2 asked for)

- **Focus and visibility: ruled out.** The window was `fronted`, and the page
  `visible` (VERIFIED, the phase's own reading). The pass's
  `window.scrollBy` needs neither, and it was never called (below).
- **The method and the target: the cause.**
  - The pass tests the DOCUMENT's bottom (`innerHeight + scrollY >=
    documentElement.scrollHeight - 8`) before each scroll, and scrolls the
    WINDOW.
  - It printed 1 step, so the test read True before the first scroll, and
    no scroll was made (DERIVED from the code and the live output).
  - At that moment `main` held 15 sections, 14 headings and 2,576
    elements. VERIFIED: counted on the preserved skeleton by
    `scroll_structure_s14c.py` (disposable).
  - A page whose main holds 15 headed sections does not read as its own
    bottom in one window unless it scrolls INSIDE an element (DERIVED).
  - Which element is UNVERIFIED. The page's classes are hashed, and a
    skeleton keeps no style.
- **The late sections.** Two of main's sections were 27-element shells.
  - They sit where 14a's later skeleton, after the photo press, drew seven
    filled sections: 5 more sections and 7 more headings than its first
    render (VERIFIED, counts).
  - What fills them is UNVERIFIED. Being scrolled into view is the likely
    trigger.
- So C2 finds the element that scrolls by walking up from main. It does not
  name it.

### 13.3 The fixes

**THE FILES.** `runner_s14c.py` is built from r3e by `patch_s14c_r1.py`.
The runner, its tools and its checks are in the main checkout's gitignored
`_state/live-runner/s14c/`. The patch:

- refuses unless its source hashes to r3e's pin;
- replaces each anchor exactly once;
- writes LF bytes.

**C1, `restore_verdict`.** It returns `restored`, or the FIRST condition
that fails, by a closed word:

- `ids_not_exact`;
- `toggle_not_0`;
- `f_key_not_restored`;
- `key_added_or_missing`: any key name but the two;
- `touched_key_not_back`: r3e's own rule, with the two judged by name only.

The round trip records the word, and the volatile key NAMES present.

**C2, `scroll_pass_14c`.**

- **The target.** It takes the nearest of main and its ancestors that
  scrolls vertically: overflow-y auto, scroll or overlay, with more to
  scroll than it shows. Else it takes the document, when that scrolls. If
  neither does, it looks again, 16 times, 0.5 s apart.
- **Each step:** it scrolls that element by 85% of what it shows, waits
  1.2 s, and reads again.
- **Progress:** a step progressed when the position moved by 1 px or more,
  or main's structure changed. The structure is main's element count and a
  hash of its tag sequence, with no text, so a ticking counter is not
  progress.
- **Proved** only when every step progressed and at least one moved the
  position.
- **Otherwise** phase 1 records the pass's reading, then stops with
  `scroll_no_progress`. That comes before the skill items, the Experience
  reading and rank 31's press.

**`scroll_no_progress` is a PHASE stop (exit 3), not a STOP-ALL.**

- The order says "a named STOP". Section 3 uses that word for a phase stop.
- Nothing has been pressed at that point, so the session goes on to phase 2.
- If the orchestrator means STOP-ALL, it is one word added to
  `STOP_ALL_KINDS`.

**Mechanical, named:** the session folder is `live16`, and the session
number 16. 14b's `live15` holds its 2 loads and 3 searches.

**THE REACH, by AST** (`ast_delta_s14c.py`, disposable): 416 top-level
definitions become 423.

- Changed: the module docstring, `SESSION`, `easy_apply_round_trip`,
  `main_async` and `phase_profile_s14`.
- Added: `ROUND_TRIP_VOLATILE`, `_f_keys`, `restore_verdict`, `SCROLL_JS`,
  `SCROLL_MAX_STEPS`, `SCROLL_FIND_TRIES` and `scroll_pass_14c`.
- Removed: none.

### 13.4 Red first (VERIFIED, check mode, `gate_checks_s14c.py` slice c14)

The checks ran on three runners:

- 14c;
- r3e;
- `runner_s14c_loose.py`, a CHECK-ONLY mutant of r3e. It simply adds
  `referralSearchId` to `VOLATILE_KEYS`, which is the obvious fix the
  ruling's "any other added or missing key still STOPs" rules out. Its
  entry point refuses.

| check | what it asks | r3e | the mutant | 14c |
|---|---|---|---|---|
| R0 | control: the first view exactly back is restored | pass | pass | pass |
| R1 | fixture 1: only the two keys left over is restored | **red** | pass | pass |
| R2 | fixture 2: the two plus one unknown key is a STOP | pass | **red** | pass |
| R2b | the two, with another key missing, is a STOP | pass | **red** | pass |
| R3 | fixture 3: a missing `f_*` key is a STOP | pass | **red** | pass |
| R3b | a missing `f_*` key, neither volatile key present, is a STOP | **red** | **red** | pass |
| R4, R5 | controls: 24 of 25 ids back; the toggle left checked | pass | pass | pass |
| L1 | the live STOP's cause (13.1) | pass | -- | pass |
| E1 | end to end: a toggle that writes and keeps the two keys, as live: restored, All filters reached | **red** (STOP-ALL `restore_failed`) | pass | pass |
| E2 | the same, with one unknown key added at the press back: STOP-ALL | pass | **red** | pass |
| S1 | his root as 14b met it, scrolling inside an element whose lower sections render in view: scrolled, a skill id drawn, rank 31 pressed once | **red** (1 step, 0 skill ids, not pressed) | **red** | pass (5 steps, 5 moved) |
| S2 | nothing scrolls: a STOP before any item | **red** (done; rank 31 pressed) | **red** | pass |
| S3 | the document overflows, but every scroll is undone: a STOP after step 1 | **red** (24 steps, then done) | **red** | pass |
| S4 | control: the document scrolls, and the lower sections render | pass | pass | pass |

- **The totals:**
  - 14c: 15 of 15;
  - r3e: 9 of 15, with C1's R1, E1 and R3b and C2's S1 to S3 red;
  - the mutant: 6 of 14, with C1's strict class (R2, R2b, R3, E2) and R3b
    red.
- **R3b is a hole r3e already had.** An `f_*` key that a round trip lost
  without touching it read as restored.
- **S1 on r3e reproduces 14b's live signature:** 1 step, 0 skill ids, rank
  31 not pressed.

### 13.5 The check sets

**THE HARNESS EDITS** (`port_checks_s14c.py`, anchored, each from its set's
14b pin):

- runner_s14c and live16 by default;
- F2 and K11 expect session 16;
- H1 and H2's synthetic root gains a 2,400 px spacer, because 14c's pass
  STOPs where nothing scrolls;
- the AI route gains two modes, for E1 and E2;
- the gate gains slice c14.

**RE-RUN ON 14c** (check mode, each step under 2 minutes):

| set | 14c | r3e's last green (`final2/`, 15:31 to 15:46) |
|---|---|---|
| the gate, slices main / phase / r1 / r2 | 31 / 20 / 16 / 16, all passed | the same |
| the close set | 23 in a full run before the bound, then the other 8 alone (`close_k5k6_s14c.py --k1`): 31 of 31 | 31 of 31 |
| the table checks | red class 3 of 3, control 1 of 1 | the same |
| the tabs checks | 18 of 18 | 18 of 18 |
| the entry refusals | every refusal as named, before any browser contact | the same |

**NOT RE-RUN.** These reach no changed code, so their last green is
`final2/` on r3e:

- the Open-to-Work checks;
- the composer checks (14d's code);
- the teardown, the restore guard and the start script's test, whose files
  are unchanged; the tools here are byte-identical copies;
- the items: `live16`'s copy is byte-identical (842bced3);
- provenance, which runs again at READY.

**WHAT THE BOX DID** (VERIFIED, sampled):

- **Two gate runs crashed.** In each, the headless renderer died ("Page
  crashed", "Target crashed") at a different check: D2, then D1, and Q9.
  - Those were the four slices together, and then main and r2 as a pair.
  - The CPU read 57 to 97% in the second run, with other lanes' pytest
    runs on the box.
  - A third run of main and r2 passed, 31 of 31 and 16 of 16, with the CPU
    at 31 to 100%.
  - The crashes' cause is UNVERIFIED. They followed the load, not the code.
- **The full close set could not finish.** It ran in 106 s on r3e on a
  quiet box. Here it ran past the 115 s bound three times, with the CPU at
  96 to 100% before it started.
  - One of those runs failed K2g, a real-time check: a dialog that closes
    6 s after its Dismiss.
  - So the 8 checks the first run did not reach were run alone.

### 13.6 For the cold review: the delta only

- `delta_r3e_to_s14c_r1.diff`: r3e to r1, 186 changed lines;
- `runner_s14c_r1.py`, the same bytes as `runner_s14c.py` (sha256
  `372d4da91faee5fa`);
- `patch_s14c_r1.py`;
- `port_checks_s14c.py`, with slice c14;
- this section.

Candidates for INSTRUMENTS, each shown red above: slice c14's C1 and C2
checks. `scroll_structure_s14c.py`, `ast_delta_s14c.py` and
`close_k5k6_s14c.py` are disposable.

### 13.7 r2: the chained shell, LIVE-SESSIONS-RUN-WITHOUT-HIM, and the cold review

**THE ORDERS.** Each note was deleted as the ack, and a copy is in the lane's
gitignored scratch.

- **17:2x, by message:** `scroll_no_progress` stays a PHASE stop. A failed
  scroll in one phase must not stop the others.
- **17:4x, by message:** the chained-shell fix goes into r2 after the review.
  A bottom counts only when it still holds after one more 1.2 s read. Red
  first, on a chained-shell page.
- **`_TEAM_LEAD_UNATTENDED.md`** (18:2x, acked 18:31:36), LIVE-SESSIONS-RUN-WITHOUT-HIM:
  - nobody fronts, clicks or watches a window;
  - the lane keeps its own window usable over CDP before each K6 phase, with
    one retry, then a skip at no load cost;
  - launch flags only if a covered page is measured to stop rendering.
- **`_TEAM_LEAD_K6_RULING.md`** (18:50, acked 18:58:55):
  - the measurements below are accepted;
  - no step of the runner may ever take the OS foreground, so there is no
    restore step either;
  - `Page.bringToFront` stays;
  - whether the window was minimised is recorded, measured.
- **The cold review** (`review14c28`, 18:10 to 18:30): NO-GO, on one NATURAL
  finding (N1) and eight NITs.
- **`_TEAM_LEAD_MASTER_B7DB2F7A.md`** (18:57, acked 19:12:21): master was
  merged in before the certifying CI.

**THE MEASUREMENTS** (VERIFIED). They used the installed Chrome 158, with
throwaway profiles on ports 9351 and 9352 and every host mapped to NOTFOUND
(`occlusion_probe_s14c.py`, `occlusion_probe2_s14c.py`,
`occlusion_probe3_s14c.py`; disposable).

| window A | Playwright attached (every phase) | no client attached |
|---|---|---|
| covered by window B | 60 frames/s, visible, focused | hidden; 18 frames/s over 4 s, timers throttled |
| minimised (windowState minimized, IsIconic) | 60 frames/s, visible, focused | hidden; 0 frames/s, timers 1/s |

- **The runner's own kind of tab** (`ctx.new_page()`): attached while another
  window held the OS foreground, it read visible and focused, at 61 frames/s.
- **Focus emulation:** Playwright sends `Emulation.setFocusEmulationEnabled`
  for every page it attaches (VERIFIED in its bundled source). That is what
  keeps an attached page live (DERIVED).
- **The OS foreground:** `Page.bringToFront` did not take it.
  `Browser.setWindowBounds` "normal" on a minimised window did, twice.
- **What K6 checked:** the OS FOREGROUND. `front_chrome.ps1` required
  `GetForegroundWindow` to be the dedicated browser's window. It checked
  neither visibility nor focus.
- **So the launch flags' condition is not met.** A covered page does not stop
  rendering during a phase, and `scripts/start_chrome.ps1` is unchanged.
- **14b's empty scroll was not occlusion:** its window read fronted and
  visible (12.2).

**r2.** `runner_s14c.py`, the same bytes as `runner_s14c_r2.py` (sha256
`04b30b3d42002257`), is built from r1 by `patch_s14c_r2.py`, which refuses
unless its source is r1. It carries five changes.

- **R2-1, the chained shell.** A bottom counts only when it still holds after
  one more read 1.2 s later. Otherwise the pass steps on, inside the same 24
  steps.
- **R2-2, LIVE-SESSIONS-RUN-WITHOUT-HIM.**
  - K6 is no longer the OS foreground. `window_gate_14c` runs on the runner's
    own tab, after the preflight and the lock and before the id's file is
    deleted.
  - It turns focus emulation on (explicitly, besides Playwright's own),
    records the window's state (`minimised_at_gate`, measured, never changed)
    and calls `Page.bringToFront`. The page must then read visible and
    focused.
  - One retry; then the phase is SKIPPED (exit 2, no load), with its reason in
    `window_gate_<phase>.json`.
  - No step of the runner takes the OS foreground. No phase calls
    `front_window()`, neither as K6's refusal nor for the "### the window"
    line, and there is no restore.
- **N1, the review's NATURAL finding.** The walk for the element that scrolls
  starts INSIDE main, at the lowest element holding every section main holds
  (on 14b's root, main > div > div). Body counts when it scrolls on its own.
  The target's depth is now signed from main.
- **NIT-1.** A target lost or changed in a step, or at the bottom's re-read,
  is a stall, never a bottom.
- **NIT-7.** The round trip's docstring names `restore_verdict`, and its
  RESTORED line names the condition that failed. r1's patch script says
  `view_restored` is "called by" `restore_verdict`. It is not:
  `restore_verdict` re-implements the touched rule. r1's script stays as r1's
  build record.

**THE REACH, by AST:** 176 lines changed from r1
(`delta_r1_to_s14c_r2.diff`).

- Changed: the docstring, `SCROLL_JS`, `easy_apply_round_trip`, `main_async`
  and `scroll_pass_14c`.
- Added: `WINDOW_TRIES`, `_WINDOW_CDP`, `window_reading`, `window_gate_14c`
  and `_window_gate_cleanup`.

**RED FIRST** (VERIFIED, slice c14, check mode). S5 is a named real-time case,
because the test is the pass's own 1.2 s waits.

| check | what it asks | r1 | r2 |
|---|---|---|---|
| S5 | chained shells: the second exists only after the first renders, 1.8 s after the bottom; its skill id is drawn | **red** (proved, 0 skill ids) | pass |
| S6 | N1: 14b's own structure, main > div > div scrolling, with the aside inside it | **red** (target none: a phase STOP) | pass (depth -2) |
| S7 | N1: body scrolls on its own under html's overflow hidden | **red** (target none) | pass |
| S8 | control: html visible and body auto, so the document is the target | pass | pass |
| S9 | NIT-1: the scroller locks in step 2 while main gains a node: a STOP before any item | **red** (read as proved) | pass (a stall at step 2) |
| W1 | unattended, with the OS foreground refused: the gate keeps the tab usable, and the phase runs | **red** (refused) | pass |
| W2 | a first unusable reading is retried once, and the phase runs on the second | **red** | pass |
| W3 | still unusable after the retry: SKIPPED, no load, the reason named | **red** | pass |
| W4 | a minimised window is recorded and never restored, and the phase runs | **red** | pass |
| W5 | control: a window that keeps a phase from running leaves rank 69's id file | pass | pass |
| W6 | control: a phase that presses nothing never meets the gate | pass | pass |
| W7 | no phase asked Windows for the foreground (W1 to W6) | **red** (6 calls) | pass (0) |

- r2 passes 27 of 27.
- r1 passes 18 of 27. Its 9 reds are exactly S5, S6, S7, S9, W1 to W4 and W7,
  and every check of 13.4 still passes on both runners.

**THE CHECK SETS ON r2** (check mode):

| set | r2 |
|---|---|
| slice c14 | 27 of 27 |
| the gate, slices main and r2 | 31 of 31, and 16 of 16 (twice) |
| the close set's K1b, K1e, K1f, K5, K6, K6b, K6c and K7 | 8 of 8 |
| the table checks | red class 3 of 3, control 1 of 1 |
| the tabs checks | 18 of 18 |
| the entry refusals | every refusal as named, before any browser contact |
| provenance | the same as r3e's |

- **THE HARNESS EDITS** (`port_checks_s14c.py`, r2):
  - The close set's `window_refusal` stubs the gate UNUSABLE, so no offline
    check opens a tab or reaches for 9224. Its K6 words name both meanings.
  - The entry set's two K6 cases now expect the self block's veto, the first
    refusal before the gate. On r1 those two read NOT AS EXPECTED, as they
    must.
  - Slice c14 gains S5 to S9 and W1 to W7.
- **NOT RE-RUN, since they reach no changed code:**
  - the gate's phase and r1 slices (20 of 20 and 16 of 16 on r1, 18:2x);
  - the close set's other 23 checks;
  - the Open-to-Work, composer, teardown, guard, starter and items sets
    (`final2/`).
- **WHAT THE BOX DID:**
  - The r2 slice's two passing runs ended their work at 131 s (with five
    sets beside it) and at 112.9 s, each past my 115 s bound during the
    teardown.
  - A run alone, with the CPU at 100% from other lanes, failed Q1 only. Q1
    is a named real-time check (a 7 s slow answer) on code r2 does not reach.
  - Q5, the slice's one check on changed code (`flag_off` through
    `main_async`), passed in all three runs.

**THE REVIEW'S OTHER NITS, for the orchestrator** (not in r2):

- **NIT-2 (pre-existing in r3e).** A non-`f_*`, non-volatile key whose value
  only the OFF press changed is accepted. On 14b's route only `keywords` is
  such a key, and all 25 ids must still come back. The review's fix, if
  wanted: `_filters(back) == _filters(base)`, with the two keys removed.
- **NIT-3:** as ruled ("any other added or missing key still STOPs").
- **NIT-4 (pre-existing):** the path is not judged; `same_address_as_before`
  records it.
- **NIT-5, for the GO:** `scroll_no_progress` and a window SKIP are
  phase-level, so the GO's "any STOP ends the session" should not cover them.
- **NIT-6, for the GO:** All filters becomes reachable live. An unexpected
  re-query there would be search 4: under the runner's cap of 5, but past a
  GO's "at most 3".
- **NIT-8:** slice c14's module line counts kind `red` only; its C14 SUMMARY
  line and the exit code carry the result. S6 models the aside inside main,
  as on 14b.

**ANSWERED for the orchestrator.**

- `tabs_checks_s14b.py`'s 15:39:17 edit is live-s13's waits fix (its line
  57: "parallel runs each take their own fake port").
- Pass 2's tabs runs wrote their outputs from 15:39:34, after that edit, so
  `final2/`'s tabs results are on `8f5ffa6a`, the pinned sha.
- The summary's `967cf23c` is the sha before the edit (DERIVED from the
  mtimes).

**A RESIDUAL, UNVERIFIED:** the session's start (`scripts/start_chrome.ps1`)
opens the dedicated Chrome's window, which may take the OS foreground once,
at launch. It is not a runner step.

## Lessons (for the orchestrator to harvest)

1. **`Path.write_text` on Windows writes CRLF.** Three patch scripts turned
   an LF file CRLF this session, and one assembly refused on it. A patch
   writes bytes.
2. **An idempotent patch cannot test "the new text is present" when the new
   text CONTAINS the old.** The skip rule re-applied three edits whose
   replacement began with their anchor, and duplicated them. A recursive copy
   of one function was caught by a count. The skip has to test the old text's
   count outside the new.
3. **A watch entered before a load counts the load's own document again**,
   unless the meter marks it as the load's. The first fix of round 1's
   MAJOR-3 did exactly that, and check R3 caught it.
4. **`no_wait_after` trades a click timeout for a pending navigation.** The
   next page read blocks on the commit, then raises "execution context
   destroyed", so an error path skipped the landing judge. The click must
   wait for the navigation it counted. Measured by the warm re-check.
5. **A label rule judged by words admits a toggle.** A switch labelled with
   an allowed word was pressed, and its flip was invisible to a text digest.
   A control's role and state must refuse before its words are read.
6. **An order can name a source disk does not hold.** The identity key's
   operator class holds no member id, so the order's source for rank 69
   cannot be met as written.
7. **An equality proof carries a close-out only across prose.** The round-4
   message asked for docstring-only equality from r4, but the R3 ruling had
   added code after r4. The close-out had already run on the final sha, and
   the AST delta names the three code statements. So the claim the message
   asked for is replaced by a measured one.
8. **A stop-line list kept by hand drifts from the runner.** The first READY's
   section 3 named 4 of the runner's 22 STOP-ALL kinds. Three of them,
   `press_outcome_unread`, `save_request_on_close` and the R3 ruling's
   `self_member_changed`, were missing even from the prose. `stop_lines_check_s14.py` reads the kinds by
   AST and refuses a section 3 that misses one. It was red on the committed
   text and is green now, so it is a candidate for INSTRUMENTS 122.
9. **A close that leaves no trace cannot be judged afterwards.** Both stops
   left byte-identical skeletons and no record of which close steps ran, so
   the cause stays UNVERIFIED. A close path records each step it took before
   it raises.
10. **A stop must record what was read before it.** Phase 1's top card, menu
    and editor routes survive only in its run log.
11. **A close rule first meets its control live.** The Open-to-Work close was
    built before anyone had pressed Edit, and the editor is a native
    `<dialog open>`. The STOP-ALL is what made that first meeting safe.
12. **A ruling by content has to be read against the code, not the table.**
    The 14b table named phase 1 by rank 31's press. Its function carried
    three more self-presses, and the ruling's words put all three out. Only
    reading `phase_profile_s14` against those words found them.
13. **One port number can have two listeners on two addresses.** A second
    Chromium whose `127.0.0.1` bind failed listened on `::1`. A judge that
    reads only the first listener row, or connects to `127.0.0.1` alone,
    sees one browser where there are two. Read the whole listener set.
14. **Bash reads a running script from its byte offset, so an edit lands
    mid-run.** The final pass's script was edited while its chunk 2 ran.
    When chunk 2's last run returned, bash went on from its old offset into
    the new text, and ran chunk 5's last four steps. They were all
    read-only, and the one file they rewrote came out byte-identical, by
    sha. Copy a script before editing it while it runs, or wait for it to
    end.
15. **A protected setting's value is not where its key is documented.** On
    Windows, Chrome 158 wrote "continue where you left off" to `Secure
    Preferences` only, measured on a throwaway profile. A guard that read
    `Preferences` would have recorded "absent" exactly when the setting was
    set.
16. **A runner written for live pages makes its offline checks wait in real
    time.** The runner's settles, close polls and late watches sat idle on
    synthetic pages: 74 minutes of a pass, with the box 86% idle. A check
    harness needs its own clock from the first day. It should name the few
    checks that test a wait itself, and run its independent sets side by
    side.
17. **A restore judged on the whole address fails where the site adds keys
    and never takes them back.** On the AI route, the Easy Apply press added
    `origin` and `referralSearchId`, and the press back left them. The toggle
    and all 25 ids came back, and the judge still read RESTORED False (12.2).
    A round trip's judge has to know which keys the site owns, measured on a
    capture before the live press. (Corrected in 13.1: the judge already
    ignored `origin`; `referralSearchId` alone failed it. See lesson 20.)
18. **A scroll pass that tests for the bottom first can end before its first
    scroll.** "1 step" read like a pass, but the scrolled skeleton was
    byte-identical to the first, so the pass measured nothing (12.2). Count
    the scrolls made, not the loop's steps, and compare the skeletons before
    and after.
19. **A git hooks folder held in a shell variable reads as the consent hook's
    protected folder.** `$GD/hooks/` was denied by name (R2), and nothing ran.
    Read with the Read tool, or spelled as a literal path, it is judged by its
    path, as the denial itself says.
20. **Name a STOP's cause from the judge, not from the reading.** 14b's
    reading showed two keys left over, and section 12 named both. The judge
    already ignored one of them (13.1). Run the judge on the reading's names
    before naming its cause.
21. **A check set that runs near its bound on a quiet box fails on a shared
    one.** The close set took 106 s alone. With other lanes' tests holding
    the CPU at 96 to 100%, it could not finish in 115 s, and a real-time
    check failed (13.5). Keep each step well under the bound, and run the
    checks a delta reaches on their own.
22. **A page under a debugger is not the page a person sees.** With
    Playwright attached, a minimised window rendered at 60 frames/s and read
    visible and focused. Detached, the same window was hidden, at 0 frames/s
    (13.7). Measure a window's state with the client the run uses, and say
    which client that was.
23. **A walk up from a landmark cannot find what is below it.** C2 started at
    main and went up, and 14b's page scrolls two levels below main (13.7, N1).
    Start the search where the content is.

