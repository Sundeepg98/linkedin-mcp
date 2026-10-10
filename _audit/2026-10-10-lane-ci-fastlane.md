# Lane CI fast lane (lci-fastlane-lead), 2026-10-10

Lane CI, branched from master 3c8edc2 (CI green, run 36460989178). The
operator's order was VELOCITY: lanes took 30-60 minutes because they could
not use GitHub Actions and ran full suites on the one shared 8-core box. This
lane fixes the CI half. It merges FIRST, ahead of five other lanes.

**Status: built, tested locally, NOT yet proven on GitHub.** The pre-push hook
runs the MAIN checkout's copy of the gate (section 5), so a `ci/` push from
this worktree would be refused by today's gate. Per the brief, the lane
stopped before pushing; the end-to-end proof follows the merge, and the
recipe for it is in section 5.3.

The lane's commits, by SUBJECT (the short hashes beside them are the lane
branch's and are nowhere on `master` until the merge):

| subject | lane branch |
|---|---|
| push gate: admit a lone refs/heads/ci/<name> that descends from origin/master and sweeps clean | 5630ea4 |
| ci: a push to refs/heads/ci/* runs one ubuntu 3.13 cell in four shards | baa36f8 |
| lane_ci: push a lane to ci/<branch>, wait on its run by head sha, clean the ref | b508b8f |
| lane_ci tests: the ssh remote case is spelled without an address-shaped string | 2651bc4 |
| this record, INSTRUMENTS section 87 and the regenerated index | (the commit that adds this file) |

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

EXPECTED WALL CLOCK, every figure labelled with what it is:

| step | figure | class |
|---|---|---|
| `push`: the gate's checks in the helper | ~72 s (one commit, 997 blobs, box quiet-ish); 217 s for 3 commits / 1002 blobs while this lane ran its own tests beside it | MEASURED on this box |
| `push`: the same checks again in the hook | same as above -- the hook re-runs them authoritatively | DERIVED (same code) |
| CI run, one ubuntu 3.13 cell in four shards | ~5 minutes | PREDICTED from run 36460989178, section 3.2 |
| total, push to verdict | ~7-10 minutes, against 30-60 locally | DERIVED |

The sweep is the expensive local step: `sweep_blobs_for_identity.py` spawns
one `git cat-file` per blob. A `--batch` reader inside that instrument would
cut it to seconds; that is a change to a shipped instrument with its own test
file and is left as a proposal (section 7).

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
(the hook runs that copy); runs the gate's own `git_ci_check` (ancestry, then
the shipped sweep over `origin/master..HEAD`); pushes the CHECKED sha (not
`HEAD` again), forced (`+sha:ref` -- the ref belongs to one lane), with
`--no-follow-tags`; prints the sha.

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
* The sweep runs twice per push (helper, then hook), ~72-217 s each on this
  box. PROPOSAL: a `git cat-file --batch` reader inside
  `sweep_blobs_for_identity.py`.
* Not built: a real `git push` end-to-end test through a hook into a synthetic
  bare remote. The tests drive `main()` with git's exact line format instead;
  the hook's own environment is exercised only by the post-merge proof.

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
