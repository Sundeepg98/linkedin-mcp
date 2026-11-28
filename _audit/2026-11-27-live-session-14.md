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
- the composer's Archived round trip LAST BUT ONE, not in the inbox's old slot,
  for two reasons:
  - its B2 rule makes any failure after Archived a STOP-ALL;
  - on the composer, its menus' close by their own trigger is unmeasured. Each
    captured row and folder trigger carries `aria-expanded` (VERIFIED, 4
    skeletons), but no capture shows a re-press closing one.
  - A stop there costs the fewest lines;
- rank 151's read last.

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
| 29 | `messaging_archived_composer` | 6 | 3 | 1 | 0 | -- | -- | yes |
| 30 | `saved_posts` (part 1) | 151 | 1 | 1 | 0 | -- | -- | -- |
| -- | `root_settle`, only while a compare of his root is deferred | -- | 2 | 1 | 0 | -- | -- | -- |

**The totals** (DERIVED from the table), without phases 21 and 28: 57 most
loads, 31 expected, 3 searches.

**How far 14b reaches** (DERIVED, by the GO's stop rule: stop when the next
phase's most loads would pass what is free):

- with 37 free (before 20:39 IST): phases 1-18 at most loads, or all of them
  at the expected spending;
- with 40 free (after 20:39 IST): phases 1-19 at most loads, or all of them
  at the expected spending.

**K6 asks one thing of him:** keep the dedicated Chrome in front while a "yes"
phase in the last column runs. A refusal costs no load; the phase is simply
run again.

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

