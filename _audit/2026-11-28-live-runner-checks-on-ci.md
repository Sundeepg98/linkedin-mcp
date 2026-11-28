# Live-runner checks on CI (lane ci-checks28, 2026-11-28)

**Task (LIVE-RUNNER-CHECKS-ON-CI).** live-s13's one-paragraph proposal (the session 14 record,
section 11.7, "LIVE-RUNNER-CHECKS-ON-CI, a proposal") asked that the live runner's check sets
which need no gitignored item move into the tracked repo, so that free CI runs them. The brief:
classify each set, make tracked equivalents for the ones that qualify, extract only identity-free
PURE functions from the gitignored runner when a check needs them, leave the live runner
untouched, red first, certify by lane CI and the full matrix, then hold.

Base: master `9ec91965`. Branch `ci-checks28`. Nothing under `_state/live-runner/` was modified,
moved or renamed: it was read, and nothing else.

## 1. The classification (written first)

The sets live in the gitignored `_state/live-runner/s14b/`. The brief named eight. A ninth, the
Open-to-Work checks (`otw_checks_s14b_port.py`), is on disk and in the proposal, so it is
classified too. The check counts are the final pass's own (the session 14 record, 11.7).

**Every set imports the runner.** The runner sits in gitignored state. At import it puts the live
lane's worktree on `sys.path`, loads the job pipeline from the installed skill, and names this
machine's paths. So no set runs on CI as it stands. What a set needs BESIDES the runner decides
its class, and then so does the runner code it drives:

- the brief admits only identity-free PURE functions out of the runner;
- most sets drive the runner's page code: its phases, its one click site, its close path, its
  meter. That code is neither pure nor small. Moving it is the proposal's own first step, "the
  runner's tracked, path-free form", which this brief did not order.

| set (file) | checks | what it needs besides the runner | class |
|---|---|---|---|
| guard (`guard_checks_s14b.py`) | 15 | the TRACKED `scripts/start_chrome.ps1`, synthetic profiles in a temp dir, Windows PowerShell | **CI-ABLE, whole.** It drives no runner code. It runs on the Windows cell; the ubuntu cells have no Windows PowerShell |
| tabs (`tabs_checks_s14b.py`) | 18 | synthetic targets on a fake DevTools port; the teardown's judge; the runner's meter | **CI-ABLE in part.** Each check's DECISION is pure and moves: the reading, its STOP, the listener judge and the gate on load 1. LOCAL: the port's HTTP read, the file writes, and the meter's wiring (that load 1 asks the gate, and a refusal reaches neither the navigation nor a ledger) |
| teardown (`teardown_checks_s14b.py`) | 16 | the gitignored tool `close_chrome_s14b.py`, the gitignored `os_check.ps1` (it carries the main checkout's absolute path), throwaway Chromiums, `Get-NetTCPConnection`, `taskkill` | **CI-ABLE in part.** The judge and the listener rule are pure, so T3, T4, T5, T6, T7, T8 and T9 move as decisions. LOCAL: T1, T1b, T2, T2b and T4b, a real graceful close and a real kill timed on real processes; and O1-O4, which run `os_check.ps1` against the OS's own tables |
| close (`close_checks_s14b.py`) | 31 | tracked skeletons (`tests/fixtures/live12`, `live13`, `live14`); the runner's `otw_capture`, `press_read_close`, `close_all`, `_click` and `main_async` | **CI-ABLE in part.** The panel rule's EVIDENCE is two read-only JS functions (`FORM_SIGS_JS`, `FORM_DELTA_JS`), so the 10 K3 checks move as evidence. LOCAL: every close outcome (`close_all`), K0-K2 and K4 (`otw_capture`), K5 (the runner's own source), K6 (`main_async`), K7 |
| gate (`gate_checks_s14b.py`) | 83 | synthetic pages and the tracked AI-route fixture; the runner's phases, `load`, `his_root`, `self_root_press`, `_click`, `close_all` | **CI-ABLE in part.** Q6 (the region digest), Q7 (`press_landing`, which the runner marks PURE) and R6 (the close and publish words) move whole. So does R4's digest half. LOCAL: the other 79, which drive phases |
| table (`table_checks_s14b.py`) | 10 | the tracked live13 skeleton; the runner's `PHASES`, `READ_LINES`, `SESSION` and its composer phase | **LOCAL-ONLY.** Its subject is the session's own plan and a page-driving phase |
| composer (`composer_checks_s14b.py`) | 5 | synthetic pages; the runner's `_archived_round_trip` (14c's code) | **LOCAL-ONLY.** The round trip is page-driving runner code |
| Open-to-Work (`otw_checks_s14b_port.py`) | 8 | the tracked live14 skeletons; the runner's `otw_capture` | **LOCAL-ONLY.** Page-driving runner code |
| entry refusals (`entry_refusals_s14b.py`) | 20 | the runner run as a subprocess in the live state folders, a digest of the pinned job-pipeline store by its absolute path, the live-session flag | **LOCAL-ONLY.** Real paths and the pinned store, by design |

Not check sets, and LOCAL by nature: the items (`prepare_items_s14b.py`, session 12's preserved
readings), the provenance step (this machine's paths), and the pins.

**The tally:** 5 of the 9 sets get a CI equivalent: the guard whole, and tabs, teardown, close and
gate in part. 54 of their 206 checks are covered:

- 18 move whole: the guard's 15, and Q6, Q7 and R6;
- 36 move as decisions or evidence: tabs 18, teardown 7, close 10, and R4's digest half.

## 2. What moved, and where (written as built)

**The layout is flat, and that is the disk's ruling, not a choice.** The brief's example,
`tests/live_runner/`, would turn the suite red.
`tests/test_impact_gate_selects_data_dependencies.py::test_no_python_hides_below_the_analysers_flat_glob`
refuses any `.py` below `tests/`, `scripts/` or `linkedin_server/`, because the impact gate's
`candidate_files()` globs one level.

| file | what it holds |
|---|---|
| `scripts/live_runner_rules.py` | The pure rules. VERBATIM from the pinned runner (r3e) and teardown: `FORM_SIGS_JS`, `FORM_DELTA_JS`, `SECTION_DIGEST_JS`, `PUBLISH_WORDS`, `PANEL_CLOSE_WORDS` and the assert that ties them, `press_landing`, `user_data_dir_of`, `BLANK_PAGES`. RE-CUT, the same decisions with their reads passed in: `judge_command_line` (the teardown's `judged`), `teardown_preclose` (its `main` up to the close), `dedicated_listener`, `browser_digest`, `tabs_reading`, `unanswered_reading`, `tabs_stop`, `tabs_gate`. ONE NAMED DIFFERENCE: `norm_profile_path` reads a path as a Windows path on every OS, which is what the teardown's `Path` is on the only OS it runs on |
| `tests/test_live_runner_chrome_judge.py` | 49 tests, pure: the teardown's T3-T9 and its control; the tabs check's T1-T6; N2-N6; G1-G8 and the control G5; and one property, that the gate accepts exactly what the tabs check passes |
| `tests/test_live_runner_page_rules.py` | 26 tests: the K3 evidence (K3a-K3e, counted apart, the re-render control); Q6 and R4's digest half; R6; Q7 and five more landings. One local headless Chromium per module, launched by a module-scoped fixture, on the TRACKED skeletons `tests/fixtures/live12`, `live13` and `live14`. Every request a skeleton makes is aborted by the test's own route |
| `tests/test_start_chrome_guard_behaviour.py` | 15 tests, G1-G15: the guard cut from the tracked `scripts/start_chrome.ps1` by its own markers, run in Windows PowerShell 5.1 on synthetic profiles, 8 at a time. The ubuntu cells skip them by name: 15 entries in `scripts/ci_expected_skips.json`, each with its reason. The skip condition is the platform alone, so on Windows a missing `powershell` FAILS the module rather than skipping |

Each case keeps the live check's own name and its own expectation. Where a live check judged a
CLOSE, the tracked test asserts the EVIDENCE that close rests on: `added` > 0 is a panel to close,
and `added` == 0 is `nothing_opened`. The close itself stays local (section 7).

**No waits.** None of the 90 tests sleeps, sets a timer or polls against a real-time bound:

- the live models' 50 ms timers are gone, and each mutation is made at once between the two
  readings;
- the live pass's named real-time exceptions are all in checks that stayed local: the race model,
  Q3, T1 and T4b, and the slow-answer models.

Measured on this box: the chrome judge takes about 1 s of test time. The page rules' one fixture
takes 5.8 s warm, or 17.7 s cold on the first Chromium start from the HDD. The guard's 15
PowerShell processes, 8 at a time, take 4.3 s.

## 3. Red first

**The mechanism.** A disposable pytest plugin in the lane's scratch (`plants.py`) rebinds one
tracked name, or the guard test's `SCRIPT`, before the tests run. The tracked tests are never
edited.

- The defect is the REAL PREVIOUS STATE wherever one is on disk. It is read as TEXT from the
  gitignored snapshots, and nothing of a runner is imported or run.
- Elsewhere, the decision was never a function of its own, so there is no text to restore. There
  the defect is a copy that mirrors the earlier tool's or runner's decision, line for line, and
  the plant cites those lines.
- The control, with no defect, passed 90 of 90.
- All 17 plants and the control ran in 71 s (`red_runs.sh`, 17:40 to 17:42).

| plant (the state it restores) | failed | the tests that convict it | the live checks' own red side on that state |
|---|---|---|---|
| teardown r1: the judge by substring, no listener rule | 9 of 49 | T5, T6, T7, T8, T9, the port-prefix case, a failed read, N6, and the control (r1 reported no listeners) | T5, T7, T6, T8 |
| teardown r1b: no listener falls through to the close | 2 | T8, T9 | T8 |
| teardown r2: the listener read can raise | 1 | T9, by name: "raised TypeError instead of a report" | T9 |
| `os_check_r0p.ps1`'s first-row judge | 1 | N3, two listeners | O3, O4 |
| runner r3b: no gate on load 1, no STOP for a port naming no endpoint | 20 | T6, G1, G2 (7 ways), G3, G4, G6, G8, a time that cannot be read, N2-N6's gate half, the property | the r3c class: T6, G1-G4, G6, G8 |
| runner r3d: the dedicated browser asked for nowhere | 8 | N2-N6, G2's two dedicated cases, the property | the r3e class: N2-N6 |
| session 14's panel rule (no K3) | 3 of 26 | K3a, K3c, counted apart | "red": K3a, K3c |
| r1's panel rule | 4 | K3x (and K3y), K3z, K3w (and K3v), counted apart | red-r1: K3x, K3y, K3z |
| r1b's panel rule, which is also r2's (late without "grew") | 2 | K3w (and K3v), and an existing section's controls counted apart | red-r2: K3w, K3v |
| session 14 r1's region digest | 2 | Q6, R4 | MAJOR-4, found on r1 |
| session 14 r2's region digest | 1 | Q6 | MINOR-C, found on r2 |
| session 14 r2's `press_landing` | 1 | Q7 | NIT-A, found on r2 |
| session 14 r1's close words | 1 | R6 | MINOR-4, found on r1 |
| start script `307aa411` | 3 of 15 | G12, G13, G14 | the same three |
| start script json1 | 4 | G11-G14 | the same four |
| start script nit5 | 6 | G8, G9, G11-G14 | the same six |
| start script, round 4's | 9 | G2, G4, G5, G8, G9, G11-G14 | the same nine |

The guard's tracked test reproduces the live checks' verdict CASE FOR CASE on all four earlier
copies of the script.

**No plant was convicted by an ERROR.** Every failure is an assertion, or a `pytest.fail` that names
the raise. Both of the following needed a correction, and both are in section 8:

- **A first cut of the K3 tests read `in_new_sections` by plain key.** Against session 14's and
  r1's rules, which return no such field (r1 returns `in_main_sections`), 7 tests failed. Most of
  them failed on a `KeyError`, the controls K3d and the re-render among them, which passed on
  those runners in the live checks. A missing field is a shape, not a conviction. Each test now
  asserts its live check's own claim on `added`, and "counted apart" is a test of its own.
- **A first cut of the teardown tests read `out["path"]` before the exit code.** So a defect that
  lets the close go ahead failed on a `KeyError`. Each now asserts exit 2 first, and the precheck
  and the judge run under a wrapper that turns a raise into a named failure.

## 4. The tracked copies against the pinned runner

`verbatim_check.py` (scratch) reads the tracked module, the pinned runner and the pinned teardown
as TEXT, by `ast`, never by import.

- **Against the session's own pins** (sha256 `fd3bf239`, r3e, and `83d17023`): 13 of 13 the same.
  That is 8 verbatim segments, the import-time assert, and 4 re-cut decisions that are AST-equal
  after the named substitutions: the judge after its read, `_norm` as `PureWindowsPath`, the
  three tab counts, and the digest.
- **Its failing control**, against r1 and the teardown's r1: 5 of 13. It differs on the panel rule
  and the judge, and finds missing every function r1 did not have yet.
- **Its first run said 12 of 13, for the checker's own reason.** It took `_browser_instance`'s
  `except` handler's `return None` for the digest, because `ast.walk` is breadth-first. It now
  takes the one conditional return.

**The honest limits:**

- The re-cut tabs and gate decisions equal the runner's by SPEC: the same 18 expectations the
  runner met in the final pass. They are AST-equal only in part (the three counts and the digest).
  No differential run went through the runner, because importing it loads the job pipeline from
  the installed skill.
- The 14b runner does not import the tracked module. Until a later session's runner does, these
  tests guard the tracked copy, not the code a sitting runs. Today the two are tied by the
  verbatim check, which is local because the runner is gitignored.

## 5. Gates run

All were local, each step under 2 minutes, and no live-session flag stood at any test run.

| step | result |
|---|---|
| the three new modules | 90 passed (49 + 26 + 15) |
| the sweeps that read `scripts/` and `tests/` (17 files, 6 workers) | 717 passed and 1 failed: the person-name guard on my first slug, `MEMBER` holding a value its table did not declare. The test now uses a value the table declares, `someone-example-1`; then 47 of 47 |
| the identity guard: my six files' cases, and the exact-value sweep, which RAN (54 s), with three named-profile sweeps | 10 passed |
| the navigation and group-members sweeps | 910 passed and 1 skipped (not one of mine), in 100.8 s. Sampled over that minute: CPU 0% idle and disk 80% idle, so the step was working, not waiting |
| the impact gate's flat-glob test | passed |
| the red runs (section 3) | 17 plants convicted, the control 90 of 90 |
| `scripts/check_cited_shas_resolve.py`, over the corpus | OK: every cited SHA resolves as an ancestor of master. The record's sha256 prefixes sit outside commit slots |
| the audit-index and rulings-register tests, the register's unique numbers, the ignored-path and model-id guards, the prose guard | 99 passed |
| the three derived views, before the record's commit | Staging the record changed two of them: the audit index gained the record's row, and the rulings register counted one more document scanned, with 216 rulings and none moved. Both were regenerated with `--write`, and then all three `--check` were clean |
| `scripts/census_completion.py` | "every headline figure matches its pin"; no census row or pin moves in this lane |

**Two first attempts at a sweep gate were cut off at 115 s.** `tests/test_impact_gate_selects_data_dependencies.py`
alone costs 198 s on CI (`scripts/ci_shard_timings.json`). Only its flat-glob test ran here, and CI
runs the rest.

## 6. Certification

**READY**, on the certified sha `3423d04a`. This is the integration branch, and it carries three
lanes:

- this lane, `5992d6a6`, green on lane CI 46154678640 and the full matrix 46155307618;
- master `acd9df5c`, the live lane's session 14c r3 READY;
- vendor-pin28, head `ddf45cae` (section 11.2).

Master is an ancestor of it, so it fast-forwards master.

| run | on | result |
|---|---|---|
| lane CI, 46160352024 | `3423d04a`, ubuntu py3.13, 4 shards | success, 6m38s |
| the full matrix, 46160990546 | `3423d04a`, 3 cells x 6 shards (`lane_ci.py wait <sha> --full`) | success, 9m40s, 18 of 18 shard jobs. The totals job printed "1 by-cell rule(s)" and no NOT CHECKED line, and no Windows shard declared a guard skip. So failure mode 7 held both halves: each ubuntu cell skipped the 15 by name, and the Windows cell ran them |

CI is the only workflow that ran on this sha. vendor-pin28's `vendored-current.yml` runs on a push to
master, on a schedule and on dispatch, never on a `ci/` ref. So its first run is master's push.

**The earlier heads**, in order:

| head | runs | result |
|---|---|---|
| `cab03baa` | lane 46144818568 | red on one test, the correction finder on a row of this record |
| `87f9ea95` | lane 46145540707, full 46146119772 | green; the first READY, before (c). The Windows cell ran the guard: its shard 0 holds the module, and its 2 declared skips are other files' |
| `355ddfa6` | lane 46147264245 | green, record only |
| `dddb46de` | lane 46150719805 | red on one test, the cited-sha guard on three slotted tokens in section 11 (section 8) |
| `3472fd46` | lane 46151713586, full 46152290793 | green, with (c) and master `b7db2f7a` merged in. Its READY was never pushed: master had moved to `d87d97ec` (section 11.1) |
| `5992d6a6` | lane 46154678640, full 46155307618 | green, with master `d87d97ec` merged in |

This section is a record-only commit on top of `3423d04a`. By the standing rules, it may be
fast-forwarded on that certification, and master's own run then covers the record.

**HOLD** for the orchestrator's merge.

## 7. What stayed local, and why

| set | stays local | why |
|---|---|---|
| gate | 79 of 83 | They drive the runner's phases, `load`, `his_root`, `self_root_press`, `_click` and `close_all`: page code in the gitignored runner |
| close | 21 of 31, and every K3 check's close half | K0-K2 and K4 drive `otw_capture`; K1's close steps and every close outcome are `close_all`'s; K5 reads the runner's own source; K6 drives `main_async`; K7 checks the redirected store |
| tabs | the half of all 18 that is I/O | The port's HTTP reads, the reading's file, and the meter's wiring: that load 1 is refused before the navigation and both ledgers |
| teardown | T1, T1b, T2, T2b, T4b; O1-O4 | A real graceful close and a real kill on real Chromiums, and the profile's `exit_type` after each; T1 and T4b time the exit itself. `os_check.ps1` carries the main checkout's absolute path and reads the OS's real listener table |
| table | all 10 | The session's own plan (`PHASES`, `READ_LINES`, `SESSION`) and a page-driving phase |
| composer | all 5 | 14c's round trip, page code |
| Open-to-Work | all 8 | `otw_capture`, page code |
| entry refusals | all 20 | The real entry point as a subprocess in the live state folders, and the pinned store's digest by its absolute path |

**What this retires locally, today: the guard set only.** Its subject is the tracked script, and
the full matrix's Windows cell now runs it on every master run. Nothing else retires for 14b,
because the pinned runner keeps its own copies, so its local pass still runs before a sitting. The
rest retires when a later runner imports `scripts/live_runner_rules.py`. Of the 152 checks with no
CI equivalent, the 132 that drive the runner's page code or plan (gate 79, close 21, table 10,
composer 5, Open-to-Work 8, teardown 9) could move only with the runner's tracked form. The 20
entry refusals are local by design.

## 8. Lessons

- **A test that reads a field a new version added convicts an old version by `KeyError`, and its
  controls go red with it.** Read the failure's reason before counting a red. Assert the claim
  (exit 2, `added`) before the field (the path, `in_new_sections`).
- **A raise inside the code under test is a finding, not an error.** Wrap the call and fail by
  name ("raised TypeError instead of a report"), so the red count holds only convictions.
- **A brief's example path can be refused by a standing guard.** `tests/live_runner/` meets the
  impact gate's flat glob. Trust disk.
- **Escapes are decoded on the way into a file.** The edit tool decodes `\u` in its strings, and
  sed's replacement reads `\u` as "uppercase the next character", which turned the escape into
  `Synth00e9tique`. A Python write that built the backslash with `chr(92)` put the six-character
  escape (a backslash, then `u00e9`) into the file, which is what keeps the test ASCII.
- **`ast.walk` is breadth-first**, so "the last `Return`" of a function can be its `except`
  handler's.
- **Price a gate's selection from `scripts/ci_shard_timings.json` before running it.** One file in
  my first sweep set was 198 s on CI alone, and it cost two 115 s cut-offs to find.
- **The person-name guard reads constants by NAME** (`MEMBER`, `OTHER`, ...). A value its table
  already declares invented can be reused, and nothing else has to move.
- **A row added to a record after its local audit run is an unchecked row.** I added the
  derived-views row to section 5 after the audit tests had passed, and pushed. Lane run
  46144818568 failed on it: `tests/test_a_correction_is_findable_from_the_claim.py` reads an
  audit file name within two lines of its vocabulary ("stale") as an undeclared correction. Re-run
  the audit-reading tests after the LAST edit to a record, not after the first.
- **A new rule read from the repository's own declaration file also reaches every test that feeds
  the script a synthetic suite.** Two existing tests went red on (c)'s first cut, because their
  ubuntu cell "failed" to skip tests it never had. Scope a rule to the runs it can speak for (here,
  runs in which some cell reported its tests), and close the remaining gap where the tests live.
- **The same miss again, one guard over.** Lane run 46150719805 failed
  `tests/test_a_cited_sha_resolves.py`. Section 11 had put three hex tokens in commit slots: the
  branch's own unmerged commit after "commit", and two sha256 prefixes after "at". The checker
  resolves a slotted token as an ancestor of master, so none of the three could. My last audit
  rerun had left out that test, because it is slow. The rule is now: after the last edit to a
  record, run `scripts/check_cited_shas_resolve.py` too, or apply its `SLOTS` to the record
  directly, which takes a second.

## 9. Questions for the orchestrator

1. **INSTRUMENTS.md.** The brief names no section, so this lane appended section 123, the next
   free one. Renumber it if it collides at the merge.
2. **The runner's tracked form.** The proposal's first step is "the runner's tracked, path-free
   form, with paths from configuration". It is what would move the 132 checks that drive the
   runner's page code or plan. Until it is ordered, those checks run locally before each sitting. Is it to be ordered
   for a later lane? Its first consumer would be 14c's runner, importing
   `scripts/live_runner_rules.py` instead of carrying copies.
3. **The 15 declared skips.** `scripts/ci_expected_skips.json` declares skips by NAME, not by cell,
   as its one earlier platform entry (the Windows junction test) does. A declared name would be
   tolerated even on the Windows cell. This module closes that gap itself: it skips on the platform
   alone, and fails on Windows when `powershell` is missing. Should the file instead learn a
   per-cell rule?

**All three are answered** (the orchestrator's hold note, 18:44 IST, deleted as the ack, with a copy
in the lane's scratch):

- (a) section 123 stands for now. hygiene28's instruments-order guard judges it at the integration.
- (b) YES, after session 14c, as part of 14d's prep. The live lane owns that runner edit, and it
  imports `scripts/live_runner_rules.py`. It is not built here, because 14c runs its runner exactly
  as pinned.
- (c) YES. It is built in section 10.

## 10. Question (c): a skip declared BY CELL

**The ruling.** The Windows cell must RUN all 15 guard tests, and a skip there is a failure. Each
ubuntu cell must skip them by name. A skip declared by name passes whether or not the Windows cell
ran the tests. Show it failing first, with a control in which the Windows cell skips one of them.

**What was built.** Failure mode 7, in `scripts/ci_shard_totals.py`, the cross-shard totals job:

- `scripts/ci_expected_skips.json` gains a `by_cell` list. Its one rule names the 15 guard tests,
  `skipped_on_os: ubuntu-latest` and `executed_on_os: windows-latest`. A rule only narrows a
  declaration: every test it names is still declared by name under `expected`.
- `record` writes each ruled test's outcome from the shard's junit into the report,
  as `ruled_outcomes`.
- `verify` holds each cell to its system's half of each rule:
  - each test must be skipped, by name, in exactly one shard, where the system must skip it;
  - it must be passed, failed or xfailed in exactly one shard, where the system must run it. An
    error does not count as a run;
  - a system the rule does not name is itself a finding.
- **A rule holds a run only when some cell reported one of its tests.** The suite's own tests feed
  `verify` synthetic suites, and the first cut turned two of them red:
  `tests/test_ci_shard.py::test_record_writes_what_verify_reads` and
  `tests/test_ci_runner_facts.py::test_the_totals_job_shows_every_shards_runner`. Their ubuntu cell
  could not skip 15 tests it never had. In every real run the ubuntu cells report all 15, so a
  Windows skip, or a test Windows never collected, stays strict.
- **Tests that vanish from every cell at once** (a conftest that ignores the module, or a rename) are
  caught where the rule's tests live. The new test file collects the guard module on every cell, and
  holds the rule's names to the module's 15 functions.
- **`verify` names what a run cannot check.** The lane fast path prints "NOT CHECKED in this run:
  the rule that 15 test(s) run on windows-latest", and the full matrix checks both halves.
- `scripts/ci_full_run_check.py`, the per-shard check, is untouched. Its docstring says it is
  byte-shared with ats-jobs.

**Red first, on the REAL full matrix (VERIFIED, `real_data_c.py` in scratch).** These are the 18 shard
reports of run 46146119772, the run that certified `87f9ea95`:

- each report's ruled outcomes come from its own junit, read by the new reader. That is exactly what
  the new `record` writes: 15 skipped on each ubuntu cell, and 15 passed on Windows;
- each plant keeps every count consistent, so only failure mode 7 can see it;
- the old gate is master's `ci_shard_totals.py` at `9ec91965`, reading the same declaration file.

| the reports | the old gate | the new gate |
|---|---|---|
| as CI wrote them | OK | OK |
| **the ruling's control:** the Windows cell skips one guard test (G13) | **OK**, which is the blindness | exit 1: G13 "must RUN on windows-latest, and this cell reported it skipped" |
| the Windows cell never collected G13 | OK | exit 1: "never collected or reported it" |
| ubuntu py3.10 ran G13 | OK | exit 1: "declared to SKIP on ubuntu-latest, by name, and this cell reported it passed" |

**The tracked test**, `tests/test_a_skip_declared_by_cell_holds_on_every_cell.py`, has 23 tests:

- the control;
- the blindness, kept on the record: the same reports judged by name alone find nothing;
- each way a cell can break its half;
- the outcome reader;
- the real declaration against the guard module and the workflow's two systems;
- the collection of the guard module on the cell that runs it;
- `verify` end to end, both the full matrix and the lane fast path's NOT CHECKED line.

**Its mutants (VERIFIED, `plants_c.py` in scratch).** Each is one edit to the shipped source. All 12
were convicted, with no ERROR, and the control passed 23 of 23:

| mutant | failed |
|---|---|
| the name-only tolerance (no per-cell check at all) | 9 of 23 |
| no rule active | 9 |
| the RUN half dropped | 5 |
| a missing test taken as fine | 3 |
| the SKIP half dropped | 2 |
| every rule active, even on another suite | 1 |
| an error counted as a run | 1 |
| an unnamed system allowed | 1 |
| no duplicate check | 1 |
| no check for a report without ruled outcomes | 1, by name: "raised KeyError instead of naming a problem" |
| the reader taking an error, or a skip, as passed | 1 each |

**Gates** (local, under 2 minutes, no live flag): the new file with `tests/test_ci_shard.py`,
`tests/test_ci_runner_facts.py`, `tests/test_lane_ci.py` and the import-safety sweep, 531 passed.
Then the audit tests and the identity cases, 104 passed, and the sweeps over `scripts/` and
`tests/`, 213 passed. (c) is one commit of its own on the branch, just before section 11's merge.

## 11. Integration with master `b7db2f7a` (hygiene28)

The orchestrator's second note (18:57 IST, deleted as the ack, with a copy in the lane's scratch)
said that master had moved to `b7db2f7a`, hygiene28's 6 commits. So the hold note's next step
applied: merge, re-check the pins, then certify the integrated head.

**The merge** is `195df7f1`. It is a merge, not a rebase, and master is an ancestor of it, so the
head fast-forwards master. hygiene28 and this lane met in three files, each appended at its end:

- **INSTRUMENTS, in conflict.** hygiene28's `scripts/resolve_instruments_order.py`, run in this
  worktree, cut the one hunk into sections and wrote them in number order, each with its
  subsections: 123 (this lane), then 124 (hygiene28). It refuses a number claimed twice, and none
  was. It exited 0 and left no conflict marker.
- **The audit index, in conflict.** It was regenerated by `scripts/build_audit_index.py --write`
  over 321 documents, and lists both lanes' records.
- **The rulings register merged without a conflict**, but its count of documents scanned was one
  side's. Regenerated, it reads 320 scanned, with 216 rulings and none moved.
- **All three derived views** then passed `--check`.

**The pins, re-checked at 19:04 IST** (VERIFIED):

- `_state/live15/pins.json`, written at 16:08. The runner and the teardown on disk match their pins
  in full (sha256 `fd3bf239` and `83d17023`), and the tracked module still matches them 13 of 13.
- `_state/live16/` holds no pins yet, only `items_prepared.json`.
- **Information only, not a pin:** 14c's runner, `runner_s14c_r2.py`, with the teardown copy beside
  it, also matches 13 of 13. The runner has the same bytes as `runner_s14c.py` (sha256 `04b30b3d`),
  and the teardown copy the same bytes as the pinned teardown (`83d17023`). So the runner 14c is to
  run still carries all 13 pieces unchanged.
- **Pass 2's 15:31 summary** lists `tabs_checks_s14b.py` with sha256 `967cf23c`. The pins, written
  at 16:08, list it with sha256 `8f5ffa6a`, the file on disk. So the pins agree with disk, and only that
  summary predates the 15:39 edit.

**Gates on the merged tree** (local, under 2 minutes, no live flag):

- the four new modules, with hygiene28's `tests/test_resolve_instruments_order.py`, the census-prose
  test it changed, and the totals tests: 311 passed;
- the correction finder, the audit index, the rulings register, the register's numbers, the
  ignored-path and prose guards, and the blocker map: 118 passed;
- `scripts/census_completion.py`: "every headline figure matches its pin";
- `scripts/check_cited_shas_resolve.py`: OK.

### 11.1 The second integration: master `d87d97ec` (session 14c READY)

**The READY push of 19:48 was refused by the pre-push gate, and nothing was pushed.** origin's
master had moved to `d87d97ec` while the full matrix ran. Those are the live lane's 5 commits, and
they touch only its session 14 record. The master note had foreseen this case: once the live lane's
r2 lands, integrate again.

**The merge** is `4565b4a4`. It merged cleanly, master is an ancestor of it, and all three derived
views passed `--check` against the merged corpus.

**The pins at 19:50 IST** (VERIFIED). No live session was on.

- `live15`: the runner and the teardown match their pins (sha256 `fd3bf239` and `83d17023`). The
  tracked module matches them 13 of 13.
- `live16`, written at 19:39, pins the 14c runner and the same teardown:
  - the teardown matches its pin (sha256 `83d17023`);
  - the runner's pin names `runner_s14c.py` with sha256 `04b30b3d`, which is r2;
  - **the file of that name now holds r3**: sha256 `459d339d`, written at 19:44:25, the same bytes
    as `runner_s14c_r3.py`. The live lane's gate checks on r3 were still running at 19:51;
  - r2's pinned bytes survive as `runner_s14c_r2.py` (sha256 `04b30b3d`).
  - The tracked module matches r2 13 of 13 (measured at 19:04) and r3 13 of 13 (measured at 19:50).
  - That pin is the live lane's to renew. This lane only read the files.

**Gates on the merged tree** (local, under 2 minutes, no live flag): the correction finder, the
audit index, the rulings register, the register's numbers, and the ignored-path and prose guards
passed 99. `scripts/check_cited_shas_resolve.py`: OK.

That head, `5992d6a6`, was green on lane CI (46154678640) and the full matrix (46155307618). At
20:17, r3's final runner (`runner_s14c.py`, sha256 `c0d61e0d`, pinned in live16 at 20:10:47)
matched the tracked module 13 of 13. Every runner name the module mirrors was byte-identical to
the 14b runner it was extracted from, 11 of 11, and none was among r3's changes:

- `capture`, `scroll_pass_14c` and `window_gate_14c` changed;
- `SCROLL_CENSUS_JS` was added.

The diff tool's control, run against r1, found 4 of 11 the same.

### 11.2 The integration: master `acd9df5c` and vendor-pin28, with this lane as integrator

The orchestrator made this lane the integrator at 20:5x IST. Session 14c had ended, and master was
`acd9df5c`, the live lane's r3 READY. One full matrix on this branch certifies all three lanes, and
master fast-forwards to its head.

- **Merge 1:** master `acd9df5c`. Its two commits touch only the live lane's session 14 record. It
  merged cleanly.
- **Merge 2:** vendor-pin28, head `ddf45cae`, jobcore-fast28's lane. It brings four files:
  `.github/workflows/vendored-current.yml`, `scripts/check_vendored_current.py`,
  `tests/test_check_vendored_current.py` and `tests/test_vendored_buildinfo.py`. It shares no file
  with this lane, and merged cleanly.
- **No conflict anywhere**, in or outside the derived views.
- **The derived views**, each regenerated with its own `--write`: the audit index (321 documents),
  the rulings register (216 rulings) and the blocker map (409 lines). Each came out byte-identical
  to the merged tree. The blocker map's only working-tree difference was its line ends, and staging
  it changed nothing.
- **`scripts/census_completion.py --check`:** "every headline figure matches its pin".
- **This lane's tests, serially:**
  - the four new modules passed 113;
  - `tests/test_ci_shard.py`, `tests/test_ci_runner_facts.py`,
    `tests/test_start_chrome_restore_guard.py` and the import-safety sweep passed 438.
- **The identity gate** examined each merge against 235 spellings, where it had 226 before.

Certification of the integrated head is in section 6.
