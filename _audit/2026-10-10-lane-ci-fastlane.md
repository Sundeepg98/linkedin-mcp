# Lane CI fast lane (lci-fastlane-lead), 2026-10-10

Lane CI, branched from master 3c8edc2 (CI green, run 36460989178). The
operator's order was VELOCITY: lanes took 30-60 minutes because they could
not use GitHub Actions and ran full suites on the one shared 8-core box. This
lane fixes the CI half. It merges FIRST, ahead of five other lanes.

**Status at 12:24 (first version): built, tested locally, NOT yet proven on
GitHub.** The pre-push hook runs the MAIN checkout's copy of the gate
(section 5), so a `ci/` push from this worktree would have been refused by
that day's gate; the lane stopped before pushing. The orchestrator merged the
lane into master as 53908ea; lanes used it at once; section 10 records the
first defect that surfaced (no local `master` on a `ci/` checkout) and this
lane's own first `ci/` run.

The lane's commits, by SUBJECT (the short hashes beside them are the lane
branch's; the first seven reached master through 53908ea, the rest wait on
the next merge):

| subject | lane branch |
|---|---|
| push gate: admit a lone refs/heads/ci/<name> that descends from origin/master and sweeps clean | 5630ea4 |
| ci: a push to refs/heads/ci/* runs one ubuntu 3.13 cell in four shards | baa36f8 |
| lane_ci: push a lane to ci/<branch>, wait on its run by head sha, clean the ref | b508b8f |
| lane_ci tests: the ssh remote case is spelled without an address-shaped string | 2651bc4 |
| record: lane CI fast lane -- how a lane uses it, the red runs, and why the proof waits on the merge | 5dc7cb7 |
| ci: the fast-path comment says which comparison was a one-time check | 77039a7 |
| record: the lane's commit table names its last two commits | a0efbd8 |
| merge master 733c986 into lane CI: live session 7's records under the fast lane | fdbeb3d |
| identity blob sweep: one git cat-file --batch per sweep; lane_ci push leaves the sweep to the hook | 454f554 |
| merge origin/master 53908ea into lane CI: the fast lane's own merge, ahead of the local-master fix | 42b8513 |
| ci: every shard off master gets a local master ref before any test runs | 4bc1c84 |
| record: lane CI sections 9 and 10 -- the batched sweep's before/after, the local-master fix, and the lane's own ci/ run | 4edba7e |
| merge master 60587b0 into lane CI: the unfollow confirmation and badge-switch lanes, ahead of the UTF-8 sweep | b910eff |
| identity readers decode one way: UTF-8 when valid, else cp1252 -- a deliberate behaviour change | d8ef400 |
| merge master fe119de into lane CI: lane K's ledger and the merged CI fixes, ahead of the timings rebuild | 66c6241 |
| ci: shard timings rebuilt from master run 38034133514 | 54dd6c1 |
| record: lane CI sections 11 and 12 -- the one-way decoding as a ruled behaviour change, the rebuilt timings, and run 38038508157 | ac5cb0a |
| tests: the impact gate's real-tree tests share one reading of the tree -- 410s to 165s, no assertion touched | ef615b9 |
| merge origin/master 66eb699 into lane CI: the CI follow-ups' merge and live session 8, ahead of the certification push | 5ca58c1 |
| merge origin/master 1027bf8 into lane CI: lane G2's engine-run fixtures, ahead of the certification push | d7c6576 |
| record: lane CI section 13 -- the slowest test file shares one reading, and the fast lane at 4m46s | f93104c |
| rulings register regenerated: two headings naming a ruling, added by this lane's record | 7fee549 |
| merge origin/master 16ee59a into lane CI: master's own rulings-register fix, identical to this branch's | 950e7fe |
| ci: shard timings rebuilt from master run 38042601470, the first carrying the shared impact-gate reading | 94766d2 |
| this record's section 14 | (the commit that adds it) |

(Through 4bc1c84 the commits reached master in its merges 53908ea and
b10bde8, through ac5cb0a in f8c7392, and through f93104c by fast-forward;
7fee549 onward wait on the next merge.)

## 1. How a lane uses it -- two commands

From the lane's worktree root, with a clean tree whose branch descends from
`origin/master`:

    <main checkout>/venv/Scripts/python.exe scripts/lane_ci.py push
    <main checkout>/venv/Scripts/python.exe scripts/lane_ci.py wait <sha>

`push` prints the pushed sha as its LAST line (so `tail -1` captures it).
`wait` exits 0 green, 1 red (failing jobs and the first failing test lines
printed), 2 no verdict (no run appeared, 25-minute bound, gh kept failing, or
the run was cancelled by a newer push to the same ref). **2 is never green.**
When done: `lane_ci.py clean <branch>` deletes `ci/<branch>`.

A worktree has no venv, so the interpreter is the main checkout's. Until a
lane has merged this branch, it can run the MAIN checkout's copy of the
helper from its own worktree root -- the helper works on the cwd's repository.

EXPECTED WALL CLOCK, every figure labelled with what it is (CURRENT since
the 12:46 follow-up, section 9 -- the first version of this table quoted the
sweep at 72-217 s and twice per push):

| step | figure | class |
|---|---|---|
| `push`: the helper's checks (dirty tree, branch, hook gate, ancestry) | well under a second -- no sweep | DERIVED (git plumbing only) |
| `push`: the hook's full check, sweep included, ONCE | 9.8 s for 3 commits / 1002 blobs; 10.4 s for 8 commits. Whole `lane_ci.py push` once master carried section 9: 14.4 s (section 12), against 104.6 s before | MEASURED on this box, sections 9, 10 and 12 |
| CI run, one ubuntu 3.13 cell in four shards | 4m46s once the slowest test file shared its reading (run 38041688406, section 13.5); 5m39s on the timings rebuilt after that, in a runner hour 29 % slower (run 38043644363, section 14); 5m50s and 6m21s before (runs 38038508157, 38036281943). Expect ~4.5-6 min: free-pool runner speed moves it more than the plan does | MEASURED, sections 10, 12, 13 and 14 |
| total, push to verdict | ~5 minutes (18.1 s push, 4m46s run), against 30-60 locally | MEASURED, section 13.5 |

## 2. The gate -- `scripts/pre_push_ref_gate.py`

It still refuses every remote ref but `refs/heads/master`, deletes included,
with ONE exception: `refs/heads/ci/<name>`, admitted only when ALL hold:

1. `origin/master`, resolved once to a sha, is an ANCESTOR of the pushed
   commit. Everything below that sha is already public, so the push can only
   add `<master>..<sha>` -- the lane's own commits. `integrate-1821` and its
   kind are not descendants of master; that is the clause they fail.
2. The SHIPPED identity blob sweep reads PASS over `<master>..<sha>`. The gate
   imports `sweep_blobs_for_identity` and calls its `main`; the needles come
   from its own `load_wordlist` (through `sweep_tracked_for_identity.KEY_PATH`,
   which `tests/repo_paths.py` resolves to the main checkout's gitignored key
   from a worktree). Exit 1 (hits) refuses; exit 2 (cannot speak) refuses; a
   wordlist that does not load (`SystemExit` from `load_wordlist`) refuses.
   The sweep walks every blob of every commit in the range, so a value added
   in one commit and removed in the next is still caught.
3. The push goes to the remote named `origin` -- clause 1 says nothing about
   what another remote serves.
4. The `ci/` ref is the ONLY ref of its push, so `--all` and `--mirror` (which
   offer every branch at once) cannot carry one.
5. The name is plain: path components of `[A-Za-z0-9._-]`, none starting with
   a dot, no `..`, no `.lock` suffix.

A DELETE of a `ci/` ref, alone in its push, is allowed (it publishes nothing).
A `ci/` push of master's own commit is refused as "nothing above
origin/master to test". `ci-offload` is not under `ci/` and stays refused.
The master path is unchanged and still loads no wordlist, so it works on a
machine with no key. The override `LINKEDIN_MCP_ALLOW_ANY_REF=1` is untouched:
not used, not widened.

Two implementation choices worth stating:

* `verdicts()` takes the content check as a parameter, and with none wired a
  `ci/` update is REFUSED -- a caller that forgets to wire it gets the old
  gate's answer, never a silent allow.
* The sweep runs with `cwd` set to the checkout its file lives in (the MAIN
  checkout, under the hook). Objects are shared across worktrees, so that
  resolves today, but the gate pins `GIT_DIR` to the pushing repository's
  `git rev-parse --absolute-git-dir` for the duration of the sweep and
  restores it after, so the sweep measures the repository whose push this is.

### 2.1 Red first

`tests/test_pre_push_ci_refs.py` builds real repositories in tmp dirs, writes
git's own pre-push line format to stdin and calls the gate's `main` exactly as
the hook does; the wordlist is a synthetic one-value json the test writes.
Nothing touches this repository's remote.

| run | result |
|---|---|
| first 16 tests vs the 3c8edc2 gate (before the change) | 9 failed, 7 passed |
| all 18 tests vs the 3c8edc2 gate (re-run at 12:08) | 10 failed, 8 passed |
| all 18 + the 9 tests of `tests/test_pre_push_ref_gate.py` vs the new gate | 27 passed |

Every REFUSE test is pinned by the clause that must fire, not just exit 1 --
the old gate refused everything as "not master", so an exit-code-only test of
the ancestry clause would have passed on the old gate for the wrong reason.
Against the old gate, the two ALLOW tests failed on the exit code, and the
seven clause-refusal tests failed on the reason. The 8 that passed on the old
gate are the six non-`ci/` names (lane, ci-offload, cilane, a tag under ci/,
an empty ci/ name, a `..` name), the master push, and the unwired-check
refusal -- each a refusal the old gate also made, kept as a guard that the
new exception did not widen into them.

## 3. The fast lane -- `.github/workflows/ci.yml`

### 3.1 What changed

Only the plan job. Its step now reads `EVENT` and `REF` through `env` (never
spliced into `run:`), and after the unchanged `SHARDS=6` / `CELLS=...`
literals and every comment above them, a push to `refs/heads/ci/*` overrides
both: one cell `{"os":"ubuntu-latest","python-version":"3.13"}` in four
shards. Nothing downstream changed: the test matrix and the totals guard read
the plan's outputs, so the shard plan, the per-shard collected-vs-ran check,
the totals reconciliation, `fetch-depth: 0`, the jobcore sibling clone, the
chromium cache and every recorded comment are as they were.

Kept to the letter: the long comments' measured decisions (the
collected-vs-ran comparison, the browser-binary handling, the shallow-clone
fix, the master-exempt concurrency key). A `ci/` ref shares the branch
concurrency group, so a newer push to the same `ci/` ref supersedes the older
run -- which is why `lane_ci.py wait` reads a cancelled run as NO VERDICT
rather than red.

### 3.2 Why four shards, measured

On master's run 36460989178 (3c8edc2), the six ubuntu/3.13 shard jobs:

| shard | job total | Run this shard |
|---|---|---|
| 0 | 181 s | 98 s |
| 1 | 300 s | 222 s |
| 2 | 223 s | 147 s |
| 3 | 164 s | 99 s |
| 4 | 186 s | 118 s |
| 5 | 237 s | 161 s |

Fixed floor per job ~67 s (checkout, setup-python, pip, chromium from cache,
two collections); 845 s of shard time in all. Four balanced shards ->
~211 s + 67 s floor, so ~5 minutes per run with the plan and totals jobs;
three shards -> ~7 minutes. Four meets the 6-minute target; three does not.
PREDICTION from one run, not a measurement of this lane.

### 3.3 The job count -- a deviation from the brief, stated

The brief asked for "at most 5 jobs, so five lane runs fit inside the free
concurrency". A fast-lane run is SIX jobs (plan, four shards, totals), but
never more than FOUR at once: the plan job ends before the shards start, and
the totals job starts after they end. So five lanes' shard phases together
are 20 concurrent jobs, the Free ceiling (one full run alone is 18). The
PURPOSE clause holds; the literal count does not. Five jobs means three
shards, predicted ~7 minutes. I chose four; the question is in section 8.

### 3.4 Validation

actionlint is not installed on this box. Instead:

* `tests/test_ci_fast_lane.py` loads the YAML, takes the plan step's `run`
  text and EXECUTES it under bash (Git's bash on Windows; a `python3` shim to
  the running interpreter), once per event shape, with `GITHUB_OUTPUT` pointed
  at a temp file. Full shape for: push master, pull_request,
  workflow_dispatch on master AND on a `ci/` ref, push to `ci-offload`,
  `cilane`, a tag `refs/tags/ci/lane`, and a plain lane branch. Fast shape
  for `ci/lane` and `ci/lane/nested`. Plus: the matrix and the totals guard
  read the same plan outputs; the plan reads its inputs through env; the
  triggers and the three jobs are present.
* Against the 3c8edc2 workflow: 4 failed (both fast shapes, the concurrency
  arithmetic, the env read), 10 passed (every full shape and the structure).
  Against this one: 14 passed.
* BYTE-FOR-BYTE: a scratch run of the OLD and NEW plan scripts for push
  master, pull_request, workflow_dispatch on `ci/lane` and push to
  `ci-offload` produced identical `GITHUB_OUTPUT` files, 195 bytes each. The
  fast lane's output is `count=4`, `shards=[0, 1, 2, 3]`,
  `cells=[{"os": "ubuntu-latest", "python-version": "3.13"}]`.
* `tests/test_the_package_compiles_on_its_oldest_python.py` (reads the python
  versions out of ci.yml): passes; the lowest version CI runs is still 3.10.

## 4. The helper -- `scripts/lane_ci.py`

`push`, in order: refuses a dirty tree (tracked changes or untracked files --
an untracked `_TEAM_LEAD_*.md` refuses too: read it first); refuses a
detached HEAD; refuses unless the MAIN checkout's gate admits `ci/` refs
(the hook runs that copy); runs the gate's own ancestry clause
(`git_ci_check(sha, sweep=False)` since the 12:46 follow-up -- the identity
sweep is left to the hook, which runs it on the same push; section 9);
pushes the CHECKED sha (not `HEAD` again), forced (`+sha:ref` -- the ref
belongs to one lane), with `--no-follow-tags`; prints the sha.

`wait <sha>`: `gh run list --commit <sha> --event push`, keeping only runs on
a `ci/` ref (master's run of the same sha after the merge is never it),
preferring `ci/<current branch>`, newest first. Polls every 20 s, bounded at
25 minutes. Reads `gh run view --json status,conclusion,jobs,...`, never
`gh run watch`'s exit code (0 on a 403). A failing `gh` call is NO verdict
and is held until the bound. On red: failing job names, then the first 20
failing lines of `--log-failed` (gh's job/step/timestamp prefix cut,
duplicates collapsed, each cut at 220 chars).

`clean <branch>`: `git push --no-follow-tags origin :refs/heads/ci/<branch>`.

Tests, `tests/test_lane_ci.py`, 37 passed, none touching the network: ref
naming (and the six names the gate would refuse), slug parsing, run choice,
verdicts, failing jobs, log parsing, wall clock, the polling loop over canned
gh answers (green after polling; red with its lines; a 403 view and a run
that never appears both end in 2 at the bound; a superseded run is 2), and
the four refusals on synthetic repos, each against a pusher that FAILS THE
TEST if called, with the clean push as the positive control.

Shown failing by five mutants, each applied after collection by a scratch
pytest plugin, each turning its named test red:

| mutant | test that went red |
|---|---|
| M1 dirty check removed | `test_a_dirty_tree_is_refused_before_anything_else` ("pushed although a refusal was due") |
| M2 ancestry/sweep check returns nothing | `test_a_branch_not_descending_from_master_is_refused_before_the_push` |
| M3 run choice ignores branch and event | `test_masters_run_of_the_same_sha_is_never_the_run` |
| M4 cancelled read as failure | `test_a_superseded_run_is_no_verdict_rather_than_a_failure` (1 == 2) |
| M5 hook probe always true | `test_the_hook_probe_reads_the_gate_this_lane_ships` |

## 5. The end-to-end proof -- it waits on the merge

### 5.1 How the hook invokes the gate

`.git/hooks/pre-push` (written by `scripts/install_git_hooks.py`,
`PUSH_WANTED`) resolves `COMMON=$(git rev-parse --git-common-dir)`,
`ROOT=$(cd "$(dirname "$COMMON")" && pwd)`, and ends
`exec "$PY" "$ROOT/scripts/pre_push_ref_gate.py" "$@"`. From a linked
worktree `--git-common-dir` is the MAIN repository's `.git`, so ROOT is the
MAIN checkout: **the hook runs the main checkout's copy, not the pushing
worktree's.** The main checkout's file hashes to blob 80a9e38, the same blob
as `3c8edc2:scripts/pre_push_ref_gate.py` -- the old gate.

So, per the brief, this lane STOPPED BEFORE PUSHING.

### 5.2 What was proven without publishing anything

On this branch's real pre-push line (`refs/heads/<branch> <sha>
refs/heads/ci/<branch> 0000...`), run by hand, no push:

* the main checkout's gate (what the hook runs today): exit 1, "not master";
* this worktree's gate: exit 0 -- ancestry from origin/master 3c8edc2 holds,
  and the shipped sweep with the REAL wordlist read
  `PASS: 0 hits across 1002 blobs, 226 needles` over 3 commits, in 217 s
  (the box was running this lane's tests beside it);
* `lane_ci.py push`: exit 1, "the pre-push hook runs the MAIN checkout's
  scripts/pre_push_ref_gate.py, and that copy does not admit ci/ refs yet"
  -- refused before any network call; nothing was pushed.

### 5.3 The proof after the merge -- the recipe

1. Merge this branch into master IN THE MAIN CHECKOUT, so its working tree
   carries the new `scripts/pre_push_ref_gate.py` (the hook reads the file,
   not a ref).
2. From any lane worktree whose branch descends from `origin/master` and
   whose tree is clean: `lane_ci.py push`, then `lane_ci.py wait <sha>`.
3. Record: the run id, its job count (expect 6: plan, 4 shards, totals), its
   wall clock (`wait` prints it from the run's own timestamps; predicted
   ~5 minutes), its conclusion. Then `lane_ci.py clean <branch>`.

Note for every lane after the merge: when master moves (the orchestrator's
push updates `origin/master` for every worktree), clause 1 requires the lane
to `git merge origin/master` before its next `ci/` push. That is the clause
working, not a defect -- and it means the fast lane always tests the lane ON
TOP OF current master, which is what the merge will produce.

## 6. Local gates run

The box: `_state/LIVE_SESSION_ON` was present until ~11:52, so the first runs
were serial (`-p no:randomly`, no `-n`), targeted. Never the full suite.

| run | result |
|---|---|
| gate tests vs old gate (red) | 9 failed, 7 passed; full file later 10 failed, 8 passed |
| gate tests + old gate tests (green) | 27 passed |
| ci fast-lane test vs old workflow (red) | 4 failed, 10 passed |
| ci fast-lane test + oldest-python test (green) | 33 passed |
| lane_ci tests | 37 passed (5 mutants each shown killing its test) |
| local gate, after LIVE_SESSION_ON cleared, `-n 4 --dist loadfile`: the 5 test files I touched or that import/read what I changed, plus 5 corpus-wide guards that sweep `scripts/` and `tests/` (person-name literals, committed credentials, ignore entries, outage-as-absence, page text) | 1171 passed in 54.66 s |
| `tests/test_no_committed_identity.py` after each commit | 1044 passed; 1045 passed; 1 failed / 1046 passed after b508b8f (an scp-style ssh remote in a test read as an email shape); fixed in 2651bc4, then 1047 passed |

The five corpus-wide guards were a deliberate widening past "touched plus
direct importers", inside the 2-minute budget, because this lane merges first
and a new file under `scripts/` is exactly what those sweeps read. The other
25 corpus-wide guards and the remaining impact-selected files
(`scripts/impact_gate.py --against 3c8edc2 --plan-only`: 62 files) were NOT
run locally; the master merge's full matrix certifies them.

## 7. Costs, limits, what this does not do

* A `ci/` push PUBLISHES. GitHub retains pushed objects after `clean`; that is
  why the sweep is a clause and not advice.
* The gate measures against the LOCAL `refs/remotes/origin/master` and never
  fetches. Every worktree shares that ref.
* The fast lane covers ubuntu 3.13 only. The 3.10 floor and the Windows cell
  are certified by the full matrix on master after a merge; the fast lane is a
  lane's early signal, never a receipt.
* DONE in the 12:46 follow-up (section 9): the sweep reads its blobs through
  one `git cat-file --batch` process and runs once per push, in the hook.
  (This bullet first read "the sweep runs twice per push, ~72-217 s each";
  that was true until section 9 landed.)
* Not built: a real `git push` end-to-end test through a hook into a synthetic
  bare remote. The tests drive `main()` with git's exact line format instead;
  the hook's own environment is exercised only by the post-merge proof.

## 9. Follow-up, 12:46: the sweep through one process, run once per push

The orchestrator accepted the four decisions in section 8 (four shards stay;
a merge commit, not a squash; lanes merge `origin/master` before each `ci/`
push) and ordered this follow-up on the same branch, master merged in first.
Master had moved to 733c986 (live session 7's records); the only path both
sides touched was `_audit/INDEX.md`, a derived view, which git merged cleanly
and `build_audit_index.py --check` read ok.

### 9.1 One `git cat-file --batch` per sweep

`scripts/sweep_blobs_for_identity.py` read each blob with its own
`git cat-file -p` launch. It now reads them all through one
`git cat-file --batch` process (`_BlobReader`: started on the first read, so
the zero cases launch nothing; closed in a `finally`). The text each blob is
matched as is unchanged by construction: `_as_text` decodes the raw bytes
through the same `io.TextIOWrapper` that `subprocess.run(text=True,
errors="replace")` built -- the locale's encoding, replacement, universal
newlines. A blob git cannot produce raises `GitError` (exit 128, what
`cat-file -p` exited with) and the sweep refuses with exit 2, as before.

BEFORE AND AFTER, measured on this box back to back, old = the main
checkout's copy (blob 064bcd3, the 3c8edc2/733c986 version), new = this
branch's, same real wordlist (226 needles):

| range | old | new | stdout |
|---|---|---|---|
| 3c8edc2..b508b8f (3 commits, 1002 blobs) | 281.6 s | 9.8 s | byte-identical, 164 bytes |
| 733c986..fdbeb3d (this branch's 8 commits) | 190 s | 10.4 s | byte-identical, 164 bytes |

(The first version of this record quoted 72 s for one commit and 217 s for
the 3-commit range; the old figure moves with the box's load, the new one
stays near 10 s because it no longer pays a launch per blob.) Target was
under 15 s for a 3-commit range: met.

THE PLANTED-VALUE CONTROL STILL FAILS. In
`tests/test_sweep_blobs_reads_through_one_process.py` the whole `main()`
report over a synthetic repository carrying a planted synthetic value is
identical with the batch reader and with the old per-blob read swapped back
in, and it is `FAIL: 1 hit(s) in 1 distinct path(s).` naming the planted
line, value never printed. The gate's own planted-value tests
(`tests/test_pre_push_ci_refs.py`, a planted value, and one removed in a
later commit) still refuse through the new reader.

### 9.2 Once per push: the helper leaves the sweep to the hook

Chosen of the two options: `lane_ci.py push` skips its own sweep and asks
the gate for the ancestry clause only (`git_ci_check(sha, sweep=False)`); the
hook runs the full check, sweep included, on the same push. Simpler than a
sha-bound stamp because it REMOVES code and adds nothing the hook would have
to trust: a stamp is a new input that says "skip the sweep", and every such
input needs its own forgery and staleness story. The cost: a planted value
is now refused from inside the push (the hook's message, nothing
published) rather than before it.

### 9.3 Red first, and the local gate

| run | result |
|---|---|
| `tests/test_sweep_blobs_reads_through_one_process.py` vs the old sweep | 5 failed: "9 cat-file launch(es) for 9 blobs", and no batch reader for the other four |
| the same, new sweep | 5 passed |
| `tests/test_lane_ci.py::test_push_leaves_the_sweep_to_the_hook` vs the old helper | failed: "the helper ran the sweep itself over <base>..<sha>" |
| `tests/test_lane_ci.py`, new helper (incl. `test_the_hook_path_still_sweeps`) | 39 passed |
| local gate, `-n 4 --dist loadfile`: both sweep test files, both gate test files, the helper's, and `test_banked_evidence_is_reachable.py` (names the sweep) | 110 passed in 53.86 s |

`tests/test_sweep_blobs_refuses_a_vacuous_pass.py`'s zero-blobs test now
also forbids a batch read: its fake `_git` can no longer see blob reads, so
without the new line its stated proof ("no blob is read") would have gone
quietly vacuous.

### 9.4 A latent finding, NOT changed (the order was byte-for-byte)

The sweep decodes blob text with the interpreter's locale encoding, and on
this box that is cp1252 (no UTF-8 mode) -- before this change and after it.
9 of the 226 needles contain non-ASCII characters (counted, not printed). A
UTF-8 file carrying one of those values is matched as mojibake here, so
those 9 can never hit on this box; on a UTF-8 Linux runner they would.
Measured today: decoding the 3-commit range as UTF-8 instead also reads
`PASS: 0 hits across 1002 blobs`, so nothing is being missed NOW. Fixing it
changes verdicts by design; that is the orchestrator's call (section 8, Q4).

## 10. The 13:22 fix: a `ci/` checkout has no local `master`

THE DEFECT, measured by the orchestrator on lane runs 38035128406 and
38035353731: the same 20 tests failed on each, the cited-SHA family
(`tests/test_a_cited_sha_resolves.py` and its kin), all with "cannot resolve
`master` to a short sha (got '')". actions/checkout creates a local branch
only for the ref it checks out; with `fetch-depth: 0` everything else,
master included, arrives as `refs/remotes/origin/*`. Master's own runs check
master out, so they never saw it -- and section 3's validation ran the plan
step, which has no checkout, so it could not see it either. A pull_request
run checks out a detached merge commit and has the same gap.

THE FIX: in the test (shard) job, right after the checkout,
`git branch --force master origin/master`, guarded by
`if: github.ref != 'refs/heads/master'` -- a checked-out branch cannot be
force-updated, and master's runs skip the step so they do not move. The plan
job has no checkout; the totals job runs no tests; neither changed.

RED FIRST: the new tests in `tests/test_ci_fast_lane.py` failed 2 of 2 on the
workflow before the step (no step creates a local master; no guard), and 36
passed after, with the oldest-python test, including a reproduction that
builds a ci/-shaped clone with no local master, shows `master` failing to
resolve, runs the step's own script under bash, and shows it resolving to
origin/master.

THIS LANE'S OWN `ci/` RUN -- the end-to-end proof section 5 deferred.
Pushed with `lane_ci.py push` from this branch, head = the commit "ci: every
shard off master gets a local master ref before any test runs" (its short
hash in the table at the top resolves only on the lane branch until the
merge), with master 53908ea merged in first, as clause 1 requires:

| what | measured |
|---|---|
| `lane_ci.py push` | exit 0 in 104.6 s; the hook (the MAIN checkout's gate, merged) admitted the ref: ancestry held, and the main checkout's sweep -- still the per-blob one until this branch merges again -- read `PASS: 0 hits across 1011 blobs, 226 needles` over 4 commits |
| `lane_ci.py wait <sha>` | found run 38036281943 by head sha; exit 0 after 376.9 s of polling |
| run 38036281943 | push event on `ci/worktree-agent-a5475b349ebe80b87`; conclusion SUCCESS; 6 jobs (shard plan, 4 shards, every shard reported), all success; wall 6m21s from the run's own timestamps |
| the cited-SHA family | from the run's uploaded junit: `tests/test_a_cited_sha_resolves.py` 44 testcases, 0 failures, 0 errors, 0 skips; all four shards 12640 testcases, 0 failures, 0 errors, 9 skips |
| per shard (job total / Run this shard) | 255 s / 181 s; 362 s / 287 s; 230 s / 166 s; 243 s / 172 s; plan 3 s, totals 9 s |

AGAINST THE 6-MINUTE TARGET: 6m21s, over by 21 s, and the reason is
measured: shard 1 ran 287 s of tests where the other three ran 166-181 s.
The packer balances on `scripts/ci_shard_timings.json`, which the workflow's
own comment says goes stale as the suite grows. Balanced, the same 806 s of
shard time is ~200 s a shard, about 4.5 minutes a run. The fix is to
regenerate the table from the junit this run uploaded; not done here
(section 8, Q5).

CORRECTED 14:10, by section 12. Two claims in the paragraph above were
wrong, and are left in place so the correction can be found from them. (1)
This record first said the table "was priced at 3660 tests". It was not:
its own label names run 36338770074 (head 687b07c, 2026-09-27), two weeks
old; the 3660 was the workflow comment's suite size, misattributed. (2) "about
4.5 minutes" assumed balance was the whole story. It is not: one file,
`tests/test_impact_gate_selects_data_dependencies.py`, runs 189 s on ubuntu
by itself, so no packing of whole files gets its shard much below that.

## 11. The 13:43 ruling on Q4: one decoding rule for every reader of the wordlist -- A DELIBERATE BEHAVIOUR CHANGE

The orchestrator ruled YES on section 8's Q4: "a sweep that cannot match 9 of
the 226 needles on UTF-8 files is a latent hole in an identity gate on a
PUBLIC repo." This section is NOT a byte-for-byte change. It changes what
text the wordlist is matched against, on purpose, in four places.

### 11.1 The hole, reader by reader

| reader | decoded with, before | what it could not see |
|---|---|---|
| `scripts/sweep_blobs_for_identity.py` (the push gate's sweep) | the LOCALE's encoding (`text=True`, no encoding) -- cp1252 on this box | a non-ASCII needle in a UTF-8 file (mojibake) |
| `scripts/pre_commit_identity_gate.py` (the installed commit hook) | the locale's encoding, the same way | the same |
| `scripts/sweep_tracked_for_identity.py` | UTF-8 with replacement | a non-ASCII needle in a cp1252 file (U+FFFD) |
| `scripts/identity_gate.py` (the manual staged-blob gate) | UTF-8 with replacement | the same |

On a UTF-8 Linux runner the first two would have read UTF-8 correctly -- the
hole was the operator's box, which is where the commit and push hooks run.

### 11.2 The rule

`sweep_tracked_for_identity.decode_text(data)`: UTF-8 when the bytes are
valid UTF-8; otherwise cp1252, with replacement for its five undefined
bytes; universal newlines after. Never the locale. All four readers now call
it: the tracked sweep reads `path.read_bytes()` through it; the blob sweep's
`_as_text` returns it; the pre-commit gate reads the staged blob as bytes and
decodes it through the sweep module (loaded once); `identity_gate.py`'s
`_git` decodes stdout through it.

AND THE SHAPE PRINTED FOR A HIT. `redact` replaced `[A-Za-z0-9]` only. Once a
non-ASCII value can match, that rule would print its accented letters, and a
character outside cp1252 could crash the print on a cp1252 console. `redact`
now turns every letter and digit of ANY script into `x` and anything else
outside ASCII into `?`. The pre-commit gate's `_mask` and `identity_gate.py`'s
`redact` now call it instead of carrying their own copies. For an ASCII line
the shape is unchanged.

### 11.3 Red first, and the real tree

`tests/test_identity_text_is_decoded_one_way.py`, with a SYNTHETIC non-ASCII
needle written in both encodings, committed and staged in a tmp repository.
Against the old readers on this box: 6 failed --

| test | why it failed on the old code |
|---|---|
| the rule (UTF-8, cp1252, newlines, an undefined byte) | no `decode_text` |
| the shape | the old `redact` kept the accented letters |
| the blob sweep, both encodings | missed the UTF-8 copy (locale cp1252) |
| the tracked sweep, both encodings | missed the cp1252 copy (U+FFFD) |
| the pre-commit gate, both encodings | missed the UTF-8 copy (locale cp1252) |
| `identity_gate.py`, both encodings | missed the cp1252 copy (U+FFFD) |

6 passed after. Each detector test also asserts the printed report is ASCII
and does not carry the value. With the blob-sweep, identity-gate, ci-ref and
staged-shape tests: 64 passed in 26.7 s (before the live session began).

THE REAL TREE STILL READS PASS under the new decoder: the tracked sweep
`PASS: 0 hits across 1001 swept files`; the blob sweep
`PASS: 0 hits across 1041 blobs, 226 needles` over 3c8edc2..HEAD (20
commits, 8.4 s). `tests/test_no_committed_identity.py` after the commit: 1051
passed.

### 11.4 Readers left as they were, and why

* `scripts/completeness_harvest.py`'s `Veto` matches text its callers read
  as UTF-8 with replacement, from browser captures -- the UTF-8 half of the
  rule already holds there.
* `scripts/purge_denied_term.py` replaces UTF-8 byte literals with
  filter-repo. A cp1252 copy would survive a purge, but its own post-check
  runs both sweeps, which now see that copy and would block the push.
* The fixture builders and `scripts/_probe_live_lane_session_2.py` read the
  key itself, not files to sweep.

THE HOOKS RUN THE MAIN CHECKOUT'S COPIES (section 5.1), so the new decoding
guards commits and pushes from every worktree only once this branch is in
the main checkout's working tree.

## 12. The 13:43 ruling on Q5: the shard timings, rebuilt

### 12.1 What was done

`scripts/ci_shard_timings.json` rebuilt with the shipped recipe,
`ci_shard.py --write-timings` over all 18 junit reports of master's run
38034133514 (head 53908ea; ubuntu 3.10, ubuntu 3.13 and windows 3.13, 6
shards each), each file priced at its slowest cell: 292 files, 12628 tests,
3742.2 s. The previous table was run 36338770074's (head 687b07c,
2026-09-27).

ONE DEPARTURE FROM THE RECIPE, written into the table's own label: the
recipe collects with `pytest --collect-only -q` at the run's head. From
14:01 `_state/LIVE_SESSION_ON` was present, which forbids full-suite work on
the box, so the collection was read back from the run's own ubuntu 3.13
junit instead: every collected test ran (the per-shard and per-cell guards
refuse a run where that is not so), so the union of a cell's testcases IS
its collection at the run's head. All three cells read back to the same
12628 tests in 292 files. `tests/test_ci_shard.py`: 136 passed (serial).

### 12.2 What it buys, predicted, and the floor it cannot move

The shipped planner balances the four fast-lane shards exactly in table
seconds (935.6 each). In ubuntu 3.13 seconds -- the fast lane's -- predicted
by the shipped packer plus a replay of xdist 3.8's loadfile scheduling on 4
workers (units ordered by test count, the `--loadscope-reorder` default):

| table | ubuntu seconds per shard | slowest shard, 4 workers |
|---|---|---|
| before (run 36338770074) | 758 / 692 / 646 / 502 | 238 s |
| after (run 38034133514) | 638 / 656 / 707 / 598 | 211 s |

The same replay put the old table's worst shard at 238 s where this lane's
own run measured 287 s, so the model runs ~20 % fast; the ratio is what to
read. THE FLOOR: `tests/test_impact_gate_selects_data_dependencies.py` runs
189 s on ubuntu by itself, and its shard cannot finish sooner. The table is
priced at the SLOWEST cell (windows sets the full matrix's wall clock), so
ubuntu sums stay within about 9 % of their mean rather than equal. Section
8, Q6 asks for the file to be split or sped up.

### 12.3 The certification run

Pushed with `lane_ci.py push` once master fe119de was merged in (clause 1),
head = the commit "ci: shard timings rebuilt from master run 38034133514"
(the short hash in the table at the top; lane branch only until the merge).
It carries sections 11 and 12's code; this record follows it.

| what | measured |
|---|---|
| `lane_ci.py push` | exit 0 in 14.4 s, all of it: the hook (the main checkout's gate, now with the batched sweep) read `PASS: 0 hits across 1036 blobs, 226 needles` over 4 commits. The same command took 104.6 s before section 9 reached master |
| `lane_ci.py wait <sha>` | found run 38038508157 by head sha; exit 0 after 349.1 s |
| run 38038508157 | push on `ci/worktree-agent-a5475b349ebe80b87`; conclusion SUCCESS; 6 jobs, all success; wall 5m50s from the run's own timestamps |
| per shard, job total / Run this shard | 332 / 261 s; 271 / 203 s; 302 / 223 s; 303 / 223 s; plan 3 s; totals 8 s |
| ubuntu test seconds per shard, from its junit | 741 / 730 / 792 / 767 -- within 4 % of their mean. The previous run, on the old table: 653 / 801 / 532 / 631, within 21 % |
| the new tests and the cited-SHA family | `tests/test_identity_text_is_decoded_one_way.py` 6 cases, 0 failures; `tests/test_a_cited_sha_resolves.py` 44 cases, 0 failures; all shards 12698 cases, 0 failures, 0 errors, 9 skips |

AGAINST THE ~4.5-MINUTE TARGET: 5m50s, NOT met, and the reason is measured.
The shards are balanced now (within 4 %, from 21 %), and the run is 31 s
faster than the old table's. But the slowest shard, 261 s of tests, is the one
holding `tests/test_impact_gate_selects_data_dependencies.py` at 199 s, and
the suite grew under the run: 12698 tests and 3030 s of ubuntu test time,
against 2617 s in the run before. Balance is spent; what is left is that
one file (section 8, Q6).

## 13. The 14:21 ruling on Q6: the slowest file, made fast without touching an assertion

### 13.1 Where its time went

`tests/test_impact_gate_selects_data_dependencies.py`: 189 s on master's
ubuntu runner (run 38034133514), 199 s in this lane's previous run, and
410.2 s serial on the operator's box (42 passed; measured with
`--durations=0` while a live session was running). Every one of its
real-tree tests called `impact_set` or `G.Corpus()`, and each call built a
FRESH `Corpus` -- reading, tokenizing and parsing the tree. Profiled on the
box: one `impact_set` call is 12.8 s on a fresh reading and 3.5 s on a reading
already taken, the rest being per-call regex scans the assertions need. The
file already held a module-scoped reading for its last three tests; the other
twenty did not use it.

### 13.2 The change

Those twenty tests take the file's existing `shared_reading` fixture: a
SIGNATURE change, and nothing else in any test body -- no assertion line was
added, removed or edited. The fixture now hands every `G.Corpus()` call a
`_view`: a shallow copy sharing the per-file readings that derives its OWN
floor, because the floor is the one thing a `Corpus` memoises from module
state a test may change (`test_the_declared_floor_members_run_and_are_not_
derivable` clears `ALWAYS_RUN_DECLARED`). The planted-repository tests, which
point the analyser's roots at `tmp_path`, keep building their own readings.

### 13.3 Before and after, per test (`--durations=0`, serial, the operator's box)

| test | before | after |
|---|---|---|
| `test_the_observed_map_only_ever_adds_to_a_plan` | 61.37 s | 26.19 s |
| `test_reverting_the_composed_rule_loses_those_readers_again` | 36.03 s | 9.15 s |
| `test_turning_the_floor_off_removes_exactly_the_floor` | 31.81 s | 7.44 s |
| `test_the_lane_l5_record_no_longer_selects_through_a_package_sentence` | 26.85 s | 14.80 s |
| `test_a_composed_stem_reaches_the_file_that_composes_it` | 22.70 s | 6.99 s |
| `test_a_twice_composed_stem_reaches_it_too` | 20.55 s | 4.92 s |
| `test_a_scoped_plan_names_what_it_did_not_run` | 19.77 s | 3.17 s |
| `test_the_composed_rule_refuses_a_shape_the_reader_enumerates` | 17.43 s | 4.41 s |
| `test_a_script_loaded_by_path_carries_its_data_to_the_loader` | 17.12 s | 5.21 s |
| `test_a_runner_wide_change_refuses_to_scope` | 16.92 s | 5.01 s |
| `test_the_selection_travels_the_two_hop_chain_and_not_a_coincidence` | 16.32 s | 3.59 s |
| `test_the_census_evidence_table_selects_it_too` | 15.27 s | 5.08 s |
| `test_the_census_ledger_selects_the_test_that_caught_it` (now takes the first, cold reading) | 12.55 s | 11.14 s |
| `test_an_absent_read_map_is_reported_and_never_read_as_empty` | 12.03 s | 3.18 s |
| `test_reverting_the_import_walk_loses_the_path_loader` | 11.02 s | 3.08 s |
| `test_the_floor_does_not_mask_an_empty_selection` | 9.95 s | 2.94 s |
| the four `test_a_real_data_file_plan_is_identical_with_the_rule_on_and_off` cases (already shared) | 34.93 s | 39.56 s |
| `test_the_declared_floor_members_run_and_are_not_derivable` | 6.57 s | 1.75 s |
| `test_the_floor_runs_even_when_the_diff_couples_to_nothing` | 4.85 s | 1.25 s |
| `test_an_unreachable_path_widens_instead_of_passing_quietly` | 4.81 s | 1.60 s |
| `test_the_floor_is_derived_and_still_finds_the_two_proven_guards` | 3.94 s | 0.91 s |
| `test_reverting_the_data_rule_loses_the_test_again` | 3.59 s | 0.87 s |
| the file | 42 passed in 410.2 s | 42 passed in 165.3 s; 71.2 s with `-n 4` |

Two honest qualifiers. The BEFORE run had a live LinkedIn session on the box
and the AFTER run did not, so the box was busier for the first; the CI run in
13.5 is the like-for-like figure. And the four already-shared cases got
slower (34.9 s to 39.6 s): a view derives its floor per call where the shared
object reused one -- the price of no test's floor leaking into another's.

SAME COLLECTION, EVERY ASSERTION RUN: `--collect-only` reads 42 tests before
and 42 after; both runs passed all 42, none skipped.

### 13.4 Planted defects still fail

Applied after collection by a scratch pytest plugin:

| plant | result |
|---|---|
| C: the SHARED reading broken -- `Corpus.code` returns nothing for every file | 2 of 3 targeted tests red: the two-hop chain (hop 1 missing) and the floor derivation (the proven guards fall out) |
| B: the SHARE broken -- every `G.Corpus()` handed the one shared object | `test_the_declared_floor_members_run_and_are_not_derivable` red: the floor derived before the declaration was cleared answered after it |
| A: every file read as importing nothing | none of the three tests it was aimed at moved -- the constant rule and the observed map reach the same targets. A non-discriminating plant, recorded rather than dropped |

### 13.5 The certification run

Pushed with `lane_ci.py push` (18.1 s) once published master 1027bf8 was
merged in, head = the merge "merge origin/master 1027bf8 into lane CI: lane
G2's engine-run fixtures, ahead of the certification push"; found by
`lane_ci.py wait` by head sha after 280.2 s.

| what | measured |
|---|---|
| run 38041688406 | push on `ci/worktree-agent-a5475b349ebe80b87`; conclusion SUCCESS; 6 jobs, all success; wall 4m46s from the run's own timestamps |
| the file on the ubuntu runner, from its junit | 80 s for its 42 cases, 0 failures (189 s on master's run 38034133514, 199 s in this lane's previous run) |
| per shard, job total / Run this shard | 188 / 129 s; 267 / 188 s; 220 / 163 s; 241 / 171 s; plan 3 s; totals 10 s |
| all shards | 12922 cases, 0 failures, 0 errors, 9 skips; the cited-SHA family 44 cases, 0 failures |

THE FAST LANE AT 4m46s, against 5m50s on the rebuilt timings alone and
6m21s before them: the ~4.5-minute target, within 16 s. What is left is
measured too: the timings table still prices this file at its old 199 s, so
the packer gave its shard fewer other files (ubuntu sums 440 / 672 / 558 /
592 s), and the slowest shard is now the one WITHOUT it. Rebuilding the table
once master has run with this change rebalances them -- the recipe of
section 12 again, from that run's junit.

## 14. Q7, answered YES at 15:13: the timings rebuilt from master's own run, and what a table cannot do

MASTER'S RUN FIRST WENT RED, AND IT WAS THIS LANE'S COMMIT. Master's push run
38042601470 at f93104c failed one test in every cell,
`tests/test_the_rulings_register_is_derived.py::test_the_committed_register_is_what_the_corpus_derives`:
section 13's heading and INSTRUMENTS 87.8's heading each name a ruling, the
register counts such headings (280 became 282), and the record's commit had
regenerated the audit index but not the register. Master carries the
one-line re-render (16ee59a; this lane's identical fix was merged, not pushed
separately). THE PROCESS FIX, from the orchestrator: every record commit runs
all three derived-view checks -- `build_rulings_index.py`,
`build_audit_index.py` and `build_blocker_map.py`, each with `--check` --
not the audit index alone. This section's commit did. (The same record
commit also left this record with its section 8 heading written twice, an
edit-splice error; corrected here.)

THE REBUILD, the shipped recipe end to end: `pytest --collect-only -q` at
f93104c, the run's head (12922 tests; no live session this time), then
`ci_shard.py --write-timings` over all 18 junit reports of run 38042601470.
That run was red, but on a stale derived view only: every test ran and its
totals job passed, so no timing in it moved. 302 files, 3578.2 s; the
impact-gate test file priced 154 s (was 195 s).

THE 5 % TARGET IS NOT REACHABLE BY A TABLE, predicted and then measured:

| | ubuntu 3.13 test seconds per shard | 4-worker makespans |
|---|---|---|
| recipe table, predicted (xdist replay over run 38042601470's ubuntu 3.13 seconds) | 615 / 715 / 734 / 694 (19 % apart) | 160 / 181 / 194 / 190 (21 % apart) |
| probe: a table priced on ubuntu 3.13 alone, predicted | 690 / 690 / 690 / 690 (0 %) | 174 / 207 / 185 / 176 (19 % apart, and a slower worst) |
| recipe table, MEASURED in run 38043644363 | 594 / 708 / 783 / 833 (40 % apart) | "Run this shard" 168 / 193 / 231 / 232 s (38 % apart) |

Balanced SUMS do not make balanced WALLS: inside a shard, xdist places whole
files on 4 workers, most tests first, and that alone leaves the probe's
perfectly balanced shards 19 % apart. And the measured run adds a third
source the model cannot hold: the same 12922 tests took 2918 s of ubuntu test
time here against 2262 s in run 38041688406, an hour earlier -- 29 % slower,
file for file (the impact-gate file 108 s against 80 s). Per-runner speed on
GitHub's free pool varies by more than the 5 % the target asks for.

THE CERTIFICATION RUN: 38043644363, push on the lane's `ci/` ref, head = the
commit "ci: shard timings rebuilt from master run 38042601470, the first
carrying the shared impact-gate reading"; conclusion SUCCESS; 6 jobs; 12922
cases, 0 failures, 0 errors, 9 skips; WALL 5m39s (job totals 244 / 269 / 321
/ 314 s). Against 4m46s for the previous run on the old table -- a slower
runner hour, by the figures above, not a slower plan. `lane_ci.py push` 17.6 s;
`wait` 322.7 s.

WHAT WOULD MOVE IT, recorded and not done (the order was "then STOP"): the
remaining spread is inside shards, so the lever is the scheduler, not the
table -- e.g. a time-aware order in place of xdist's count order (the same
replay gives a slowest shard of 183 s against 194 s); or a fifth shard, which
the 20-job ceiling prices at five lanes x five shards.

## 8. Questions for the orchestrator

1. JOB COUNT. Ground: the brief's "at most 5 jobs, so five lane runs fit
   inside the free concurrency". The fast lane is 6 jobs, 4 at once (section
   3.3). Keep four shards (predicted ~5 min, peak 20 for five lanes), or drop
   to three (5 jobs, predicted ~7 min)? Recommendation: keep four.
2. MERGE INTO THE MAIN CHECKOUT. Ground: the hook execs
   `"$ROOT/scripts/pre_push_ref_gate.py"` with ROOT the main checkout. No lane
   can use the fast lane until the main checkout's WORKING TREE has this gate.
3. THE PROOF. Ground: brief step 4, "If it runs the main checkout's copy, stop
   before pushing." The first post-merge `lane_ci.py push` + `wait` is the
   proof and the first measurement of the 6-minute target; section 5.3 is the
   recipe.
4. (added 13:20) DECODE THE SWEEP'S BLOBS AS UTF-8? Ground: section 9.4 -- the
   blob sweep reads text in the locale's encoding (cp1252 here), and 9 of 226
   needles are non-ASCII, so on this box they cannot match a UTF-8 file.
   Nothing is missed today (UTF-8 decoding of the current tree also reads
   PASS). Recommendation: decode as UTF-8 with replacement in `_as_text`, as
   its own change with a planted non-ASCII control; it was not done here
   because the order was byte-for-byte identical results.

5. (added 13:40) REGENERATE THE SHARD TIMINGS? Ground: section 10 -- run
   38036281943 took 6m21s because one shard ran 287 s of tests against
   166-181 s for the others. (The ground first added "priced on a 3660-test
   suite"; wrong, see section 10's correction.) The run's junit is uploaded
   per shard for exactly this. Recommendation: a small follow-up that
   rebuilds the table from a full master run's junit.

Questions 1-3 were answered at 12:46: four shards stay; the branch merges as
a merge commit; lanes merge `origin/master` before each `ci/` push.
Questions 4 and 5 were answered at 13:43: YES to both -- section 11 (the
decoding rule, as a deliberate behaviour change) and section 12 (the
timings).

7. (added 15:10; answered YES at 15:13, done in section 14) REBUILD THE
   TIMINGS ONCE MORE? Ground: section 13.5 -- the
   table prices the impact-gate test file at its old 199 s where it now runs
   80 s, so the four shards are 440 / 672 / 558 / 592 s of ubuntu test time.
   Recommendation: rerun section 12's recipe on the first master run that
   carries section 13's change.

6. (added 14:15; answered YES at 14:21, done in section 13) SPLIT OR SPEED
   UP ONE TEST FILE? Ground: section 12 --
   `tests/test_impact_gate_selects_data_dependencies.py` runs 189 s on
   ubuntu, about 30 % of a balanced shard on its own, and it is the floor
   of the fast lane's slowest shard. Recommendation: whoever owns the impact
   gate measures where its 189 s go (if each test re-collects the suite, a
   module-scoped fixture would do it once) and splits or shares; the fast
   lane would then sit near 4.5 minutes.
