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

STOP-ALL ends the session (exit 4). It fires on:

- any wall, checkpoint, challenge or password prompt;
- the flag not being this lane's, a second client on 9224, or a listener that
  is not the dedicated profile's browser;
- `ledger_count_failed`;
- a failed restore: a switch, the toggle or the folder;
- a publishing or creating control as a press aim, or a commit or autosave
  sign;
- a Save, Submit, Delete or Remove drawn as pressed;
- his root's structure changed after an editor;
- the Open-to-Work card changed;
- a conversation opened, or the guard's premise broken;
- a self-root or attended press that landed anywhere but its target
  (`press_landing_not_target`);
- an editor, overlay or attended menu that will not close
  (`editor_not_closed`);
- a typing site asked for a text that is not one of its constants, or whose
  text reached a composer (`typing_not_closed`);
- a deletion that cannot be verified (phase 33, 14b).

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

The branch head is the commit that amends this section with the AST-equality
line below; the first READY's commit is its parent. Its sha is in the amended
READY message and in `pins.json`.

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

