# The flat gate: what the floor actually costs, and what it would take to remove it

Measured 2026-09-20 on this box. **Every absolute number here was taken on a
CONTENDED box** -- several agents were running pytest throughout -- so absolute
wall clocks run high and are not comparable with numbers taken on a quiet box.
The before/after pair below is the defensible comparison because its two arms
were INTERLEAVED in one session and reported as min-of-3: contention only ever
adds time, so the minimum is the least contaminated estimator, and interleaving
stops a noisy minute landing entirely on one arm.

---

## The headline

```
THE FLOOR, one instrument, arms interleaved, min of 3

  BEFORE   23,131 ms    1,841 tests    (samples 23131 / 24896 / 26749)
  AFTER    13,013 ms      947 tests    (samples 13013 / 14654 / 15243)
         +    959 ms    the three incremental scripts the gate now runs
         = 13,972 ms

  saved     9,159 ms     1.7x
```

**1.7x, not flat.** The rest of this document is why that number is 1.7 and not
20, what it would cost to move it further, and which of the thirteen guards can
never be moved at all.

---

## The finding that reframes the question, and it is not modularization

### 1. The floor's wall clock is a MAX, not a SUM

`scripts/impact_gate.py` runs the floor under `-n auto --dist loadfile`, and
that flag **pins each file to one worker** -- deliberately, because these files
carry module-level state and splitting one across workers would be an isolation
change. On an 8-core box with 13 files that means:

```
  sum of the 13 files run serially      75,479 ms
  the 13 run as the gate runs them      29,748 ms
  the single slowest file alone         17,996 ms
```

The wall is bounded below by the slowest single file. **So retiring a cheap
guard buys nothing at all.** Eleven of the thirteen could have gone to zero on
2026-09-20 morning and the floor would not have moved by one second. Only the
top of the list is load-bearing, and every repair moves the binding constraint
to the next file down -- which is exactly why the second pairing in this wave
bought 1.4s where the first bought 7.4s.

### 2. A pytest file has a floor of its own, about 2.9 seconds

```
  one trivial floor member, alone, under the gate's exact invocation   2,948 ms
  the cheapest floor member, alone, serial                               719 ms
  scripts/pre_commit_identity_gate.py, the proven incremental half       208 ms
```

The identity pair's 58x is **not only incrementality**. `pre_commit_identity_gate.py`
is a plain script: no pytest, no conftest, no xdist worker startup. An
incremental guard written AS A PYTEST TEST could not get below about a second,
and the floor as a whole could not get below about three.

**Therefore: zero latency is unreachable while the floor is a pytest
invocation at all.** The end state that answers the operator's question is a
floor made of plain scripts -- and that is a thirteen-guard job, not a
one-guard job.

### 3. Part of the cost was never about scope

Two of the three most expensive floor members were expensive because they
**redid the same corpus scan once per test**, not because they sweep the tree.
That is not an argument about denominators; it is a missing memo. Both were
repaired in place with no change to what is checked and no incremental
reasoning at all:

```
  tests/test_the_source_url_split_was_never_ruled.py    17,190 -> 1,540 ms   (20 tests, unchanged)
  tests/test_readers_outside_dom_are_a_pinned_inventory.py 8,720 -> 2,580 ms  ( 6 tests, unchanged)
```

The first parametrised one assertion over 13 declared sites and each case
re-parsed all of `linkedin_server/`; one `functools.lru_cache` fixed it. The
second ran `_called_names` -- a full `ast.walk` -- once per ORDERED PAIR of
modules, about 1,560 traversals for an answer that needs 40; inverting the loop
into a `callers` index fixed it. The rewritten condition is exactly equivalent,
and the file's three shown-failing detector controls still pass, which is what
says so.

**A guard can be slow for a reason that has nothing to do with the property it
checks.** Neither of these needed a sibling, a base case or a CI argument.

---

## The rule the pairings obey: an induction step needs a base case

An incremental guard is an **induction step**. "No committable file carries an
identifier shape", checked on staged content alone, is sound ONLY IF the
invariant held on the tree those files are landing on. Nothing local guarantees
that -- a `--no-verify` commit, a guard disarmed in a worktree, a merge from a
branch that never ran it.

**The base case is the whole-tree sweep, and it is not deleted and does not
move.** It stays in `tests/` and runs on every push, on three platforms, in
`.github/workflows/ci.yml`.

```
  base case        the whole-tree sweep, in CI, on every push
  induction step   the script, locally, on every commit
```

Neither is optional. A repository that deletes its whole-tree sweep because the
staged-content check is faster has traded a guarantee for a heuristic and will
not notice until it matters.

### The one place CI cannot be the base case

`committable_files()` is tracked **plus untracked-not-ignored**, widened
2026-09-01 after a file carrying a real activity id sat through a green suite
and became visible only in the commit that published it. **CI clones a commit,
so it never sees an untracked file and never will.** Untracked files therefore
stay inside the fast set rather than being deferred to a sweep that
structurally cannot see them, and `tests/test_staged_identity_shapes.py::test_an_untracked_file_is_in_the_change_set`
pins that.

### The unit of substitution is a SWEEP, not a FILE

Every floor member is MIXED: a sweep, plus its own shown-failing controls, plus
in some cases a genuinely set-shaped assertion. Substituting the FILE would
move the set-shaped half and all the controls to CI as collateral. So a pairing
names a **pytest node id**, the gate passes `--deselect`, and the file stays in
the plan. Concretely, for `tests/test_no_committed_identity.py`:

```
  whole file                                          17,996 ms   590 tests
  with the two paired sweeps deselected                3,170 ms    43 tests
```

Those 43 include `test_no_tracked_file_pairs_fixture_content_with_anything_else`,
which is genuinely set-shaped and still runs locally.

---

## What was built

| artifact | what it is |
|---|---|
| `scripts/staged_identity_shapes.py` | NEW. The shape half of the identity guard over the change set. 446 ms against 17,996 ms. Imports the property from the test module rather than restating it. |
| `scripts/staged_navigation_guard.py` | NEW. Both navigation rules over the change set. 451 ms against 8,420 ms. |
| `scripts/pre_commit_identity_gate.py` | ALREADY EXISTED at 208 ms, shipped as a git hook, never joined to the gate. This wave is the join. |
| `scripts/impact_gate.py` | The pairing register (`Pairing`, `_INCREMENTAL_SIBLINGS`, `pairings_for`, `run_siblings`), a third exit code that falls back to the slow path, and `--deselect` threaded into `run_plan`. |
| `tests/test_staged_identity_shapes.py` | 16 controls. |
| `tests/test_staged_navigation_guard.py` | 13 controls. |

### The scripts ship SHOWN FAILING, and the controls ship shown failing too

Three identifier shapes are assembled at runtime and staged in a throwaway git
repository; each is asserted visible to the SLOW half first, so a green fast
half can never be excused by "the property does not fire on that either". Both
navigation plants are the twin's own red exemplars, copied verbatim.

The trap the brief names -- an incremental guard is trivially green on an empty
stage -- is planted directly: a run that reads nothing must print
`examined 0 files` rather than a bare pass, on the same law as the gate's own
empty-impact-set alarm.

And the controls were themselves mutation-tested. Three deliberate defects,
each restored afterwards:

```
  reads the worktree instead of the index              RED: 1 failed, 15 passed
  stops declining when the property module is staged   RED: 1 failed, 15 passed
  drops untracked files from the change set            RED: 1 failed, 15 passed
```

One failure each, not a blanket red -- the controls are precise, not merely
loud.

### The set-shaped residue, computed from the diff rather than assumed away

Both properties are per-file EXCEPT for one thing: the declaration tables
(`DECLARED_PLANTS`, `KNOWN_DERIVED_NAVIGATIONS`, `KNOWN_TAINTED_OUTPUT`) and
the rule sets live in the test modules. A commit that edits one has changed
what the question MEANS for the files the fast run never reads. So both scripts
**exit 2 -- CANNOT ANSWER -- when the property module is in the change set**,
and the gate restores the whole-tree sweep to the plan.

Exit 2 is also why these scripts do NOT fail open. Every other gate in this
repository fails open because there is nowhere better to fail to; a paired
sweep has somewhere better, so it fails to the slow path. `pre_commit_identity_gate.py`
exits 0 and says `ALLOWING` when its gitignored wordlist is absent -- that is a
documented deliberate fail-open and it is **not an answer**, so the register
carries a `fails_open_token` and the gate restores that sweep too.

---

## The thirteen, enumerated

Derived by importing `scripts/impact_gate.py` and calling
`always_run_files(Corpus())` -- not read off a list. `min_ms` is a serial
single-file run on this box.

| # | guard | ms before | verdict |
|---|---|---|---|
| 1 | `test_no_committed_identity.py` | 17,996 | **SIBLING FOUND + SIBLING WRITTEN.** Two sweeps. The exact-value one already had `pre_commit_identity_gate.py` (208 ms) and nobody had joined them up; the shape one now has `staged_identity_shapes.py` (446 ms). Third assertion in the file is genuinely set-shaped and stays. |
| 2 | `test_the_source_url_split_was_never_ruled.py` | 17,190 | **NOT A SCOPE PROBLEM.** 13 parametrised cases each re-parsed all of `linkedin_server/`. Memoised; 1,540 ms. Whole-tree form untouched. |
| 3 | `test_navigation_is_never_derived.py` | 8,420 | **SIBLING WRITTEN.** Two per-file rules over 170 files, both verdicts a function of one file's AST plus a basename-keyed table. `staged_navigation_guard.py`, 451 ms. |
| 4 | `test_readers_outside_dom_are_a_pinned_inventory.py` | 8,720 | **GENUINELY SET-SHAPED, AND ALSO QUADRATIC.** Whether a staged file's `read_*` is wired depends on whether some OTHER, unstaged, file calls it -- a call-graph reachability question that staged bytes cannot answer. No sibling is possible. But the scan was O(n^2) in module count; fixed in place, 2,580 ms. |
| 5 | `test_a_sanitiser_earns_its_entry.py` | 4,855 | **PARTIAL.** The "unenrolled claimant" direction is per-file; `test_every_enrolled_file_is_tracked_by_git` is a property of the tracked SET. Not paired. |
| 6 | `test_ci_shard.py` | 3,308 | **MOSTLY SELF-CONTAINED, AND ALREADY CHEAP.** Pure packing/parsing tests plus two that need the current `tests/` listing. Below the 2.9 s pytest startup floor in practice; pairing it would buy nothing. |
| 7 | `test_page_text_is_never_printed.py` | 3,479 | **PARTIAL, leaning set-shaped.** `KNOWN_TEXT_SINKS` is per-file, so a new sink only appears in an edited file -- but the file also reconciles aggregate gained/lost sets across the corpus. Now the most expensive remaining member; see below. |
| 8 | `test_a_person_name_is_never_a_literal.py` | 3,036 | **PARTIAL.** `test_every_person_constant_holds_a_declared_invented_name` is per-file; `test_every_declared_name_is_actually_used` is a usage total over the corpus. |
| 9 | `test_no_committed_credential.py` | 2,962 | **PER-FILE, YES -- and already cheap.** `scan()` is a pure function of one file's text, 550 cases at ~5.6 ms each. A clean future pairing; buys nothing today because it is at the startup floor. |
| 10 | `test_probe_navigation_budget.py` | 2,944 | **PARTIAL.** Per-file unguarded-navigation status, plus three reconciliation tests over the current file set. |
| 11 | `test_a_correction_is_findable_from_the_claim.py` | 2,465 | **GENUINELY SET-SHAPED.** A corrector names what it corrects and the corrected document cannot name its corrector, so the back-pointer lives in a DIFFERENT file. Staging file A can break the invariant about the pair (A, B) where B was never staged. No sibling is possible. |
| 12 | `test_no_committed_document_defers_to_an_ignored_path.py` | 719 | **PER-FILE, YES.** Each document's offender status is a pure function of its own text. Also the cheapest member in the set; pairing it is free of value. |
| 13 | `test_every_ignore_entry_is_declared.py` | 868 | **PARTIAL.** The declaration checks are per-file over `.gitignore`; `test_every_derived_source_is_actually_swept` is a property of the tree. |

**Three are genuinely irreducible in whole or part**, and that is a result, not
a failure:

* **#11** -- a back-pointer between two documents. Staged bytes of one cannot
  see the other.
* **#4** -- call-graph reachability across the package. "Is this reader wired"
  is a question about every other module.
* **#5, #8, #13** -- each carries at least one assertion that is a TOTAL or an
  INVENTORY over the tracked set (is every enrolled file tracked, is every
  declared name used, is every derived source swept). A total is not
  decomposable into per-file facts.

For the rest, the barrier is not soundness. It is that **they are already at
the pytest startup floor**, so a sibling would save nothing while adding a
second instrument to keep in agreement with the first.

---

## Where the floor sits now, and what the next lever costs

After this wave the floor is **13,972 ms** and the distribution has no single
dominant term any more. Re-measured per guard, three interleaved round-robin
passes, minimum reported:

```
  SUM of the 13 minima, serial            39,865 ms   (was 75,479 ms)
  MAX of the 13 minima                     6,791 ms   (was 17,996 ms)
  bare pytest startup, -n auto              2,571 ms
  scripts/staged_identity_shapes.py           438 ms
  scripts/pre_commit_identity_gate.py         158 ms
```

**That table is itself noise-dominated and should be read as a shape, not as
values.** Its per-file samples spread by up to 3.5x on the same file in the
same session (`test_ci_shard.py`: 3385 / 2946 / 10188 ms), which is what a
shared box does to a measurement, and the navigation row in it was taken
WITHOUT its two new deselects because the pairing landed after that pass
started. The shape is what matters and the shape is unambiguous: eleven of the
thirteen now sit between 0.7 s and 3.6 s, which is the same order as the 2.6 s
pytest startup they each pay.

The most expensive individual assertions in a post-pairing floor run:

```
  4.49s  test_page_text_is_never_printed::test_no_file_prints_page_text_beyond_its_pinned_inventory
  4.48s  test_no_committed_identity::test_no_tracked_file_pairs_fixture_content_with_anything_else
  3.72s  test_a_sanitiser_earns_its_entry::test_each_enrolled_sanitiser_is_shown_holding_the_needle[...]
  2.65s  test_ci_shard::test_record_writes_what_verify_reads
  2.36s  test_navigation_is_never_derived::test_there_are_files_to_scan_and_gotos_among_them
```

**That is a long tail, not a term.** Each further pairing now buys single
seconds, and the sequence of wins this wave measured says so directly:

```
  pairing the two identity sweeps        23,131 -> 15,028 ms    -8,103 ms
  plus the two navigation sweeps         15,028 -> 13,972 ms    -1,056 ms
```

The honest projection, and the answer to *"what would the engineering cost be
to achieve zero latency"*:

* **Getting to roughly 8-10 s**: pair `test_page_text_is_never_printed` and
  memo-audit `test_a_sanitiser_earns_its_entry`. One more wave of the same
  shape as this one.
* **Getting below 3 s**: impossible while the floor is a pytest invocation.
  The xdist startup alone is 2,948 ms.
* **Getting to about 1 s**: the floor stops being pytest. Every one of the
  thirteen gets a plain-script half, the gate runs thirteen 200-450 ms scripts
  instead of one pytest plan, and the pytest forms live only in CI. That is
  ~9 more scripts plus ~9 more control files, and **three of the thirteen
  cannot make the trip** (#4, #11, and the total-shaped assertions in #5/#8/#13)
  -- those would have to stay behind as a small pytest residue, which puts the
  real asymptote back at the startup floor of whatever remains.

**So zero is not reachable, and the shape of the curve says where to stop.**
The cheap half of the work is done; the next wave is worth about 5 s and the
one after that is worth about 2 s.

---

## Two things found on the way that are not mine to fix

### A red at HEAD, introduced by the CI-sharding commit

```
tests/test_requirements_pins.py::test_the_two_files_declare_the_same_dependencies
  requirements.txt and pyproject.toml disagree about WHICH packages this
  server depends on. Only in requirements.txt: ['pytest-xdist'].
```

`970a276` added `pytest-xdist>=3.5` to `requirements.txt` and not to
`pyproject.toml`. It is red at HEAD, it is a one-line fix, and it is somebody
else's file -- so it is reported rather than touched. Any change wide enough to
widen the gate to the full suite hits it.

### The gate's own test is 10.8 s and is SELECTED, not floored

`tests/test_impact_gate_selects_data_dependencies.py` is **not** in the
always-run floor -- the derivation is right to exclude it, because its only
`ls-files` occurrence is inside prose and `code_text()` strips docstrings before
the corpus-wide patterns run. It costs 10,770 ms and its 13 tests each build a
fresh `Corpus()`. That fires on any change coupled to `scripts/impact_gate.py`,
which is this wave's diff and few others. It is a selected cost, not a floor
cost, and it is left alone: caching `Corpus` across those tests would trade the
isolation they were written to have.

---

## What was deliberately NOT done

**The floor derivation was not narrowed.** Seven of the thirteen are
FOLDER-BOUNDED -- they glob `scripts/*.py` and/or `linkedin_server/*.py` and
nothing else -- so a commit touching only `_audit/*.md` cannot change their
verdict, and gating them on "did the diff touch those folders" would be EXACT
rather than an induction step. It is the single largest remaining structural
lever for document-only commits.

It is not in this wave because it would fire
`test_impact_gate_selects_data_dependencies.py::test_the_floor_is_derived_and_still_finds_the_two_proven_guards`,
which pins `test_page_text_is_never_printed.py` and
`test_no_committed_identity.py` INSIDE the floor and exists because a sibling
wave shipped red to CI twice in one day for exactly that omission. Rewriting a
control that a live incident put there is a decision that deserves its own
reproduction, not a footnote in a latency wave. **Named here with its number so
it can be funded, not worked around.**
