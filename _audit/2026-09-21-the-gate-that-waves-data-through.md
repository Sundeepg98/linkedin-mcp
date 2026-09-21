# The gate that waves data through

Subject: `scripts/impact_gate.py` -- the impact analyser that selects which
tests a change can break. Measured 2026-09-21 in a linked worktree at
`f729a2a`, windows, the main checkout's `venv/Scripts/python.exe`, 208 test
files on disk, 266 tracked non-python files.

Written in the order the work happened, because the first measurement
overturned the brief and everything after it is a consequence.

---

## 1. THE BRIEF'S FRAMING IS WRONG, AND THE MEASUREMENT SAYS SO IN ONE LINE

The wave was commissioned on this statement:

> `scripts/impact_gate.py` selects which tests to run from a diff. Its coupling
> is **NAME-BASED**: it reasons from source-file names to test-file names. [...]
> A change to one of those files has no name-mate, so the analyser returns an
> empty impact set and the gate passes having run nothing relevant.

**That describes `scripts/pre_commit_boundary_gate.py`, which is a different
instrument.** It does not describe `impact_gate.py` on any commit in this
history. The impact gate was built on 2026-09-20 (`467b52f`, `9951c01`,
`e672ed7`) with a data-path coupling as its LEAD design decision; its own
docstring opens on the census-ledger defect the brief quotes as the receipt,
and `_audit/2026-09-20-the-impact-gate.md` is that wave's write-up of the same
reproduction.

So the two claims were put to the tree before anything was built.

### 1.1 The receipt file, re-run today

    python scripts/impact_gate.py --paths _audit/2026-09-03-linkedin-gap-blockers.md --plan-only

selects **11** test files, and `tests/test_blocker_map_is_derived.py` -- the
guard whose parser the `CORRECTED BY` marker broke -- is among them. The
reproduction the brief calls "not hypothetical" is fixed and stays fixed.

### 1.2 Every tracked non-python file, not a sample

The analyser was run over all 266 of them, with the corpus-wide floor excluded
so that only the SELECTION is counted (2127s, because each call builds its own
corpus -- see RESIDUAL):

| class | n | empty selection | min | median | max |
|---|---|---|---|---|---|
| audit doc (`_audit/*.md`) | 213 | 0 | 10 | 10 | 11 |
| census (`_audit/_census/*`) | 9 | 0 | 10 | 13 | 18 |
| fixture (`tests/fixtures/**`) | 25 | 0 | 14 | 16 | 22 |
| tests data (`tests/*.json`) | 3 | 0 | 11 | 11 | 11 |
| scripts data (`scripts/*`) | 9 | 0 | 21 | 21 | 91 |
| ci config (`.github/workflows/ci.yml`) | 1 | 0 | 1 | 1 | 1 |
| root config | 6 | 1 | 0 | 3 | 65 |

**One file in 266 returns an empty selection, and it is `LICENSE`.** The
brief's "returns an empty impact set" is false for every census `.md`, every
baseline `.json` and every `.tsv` in the tree.

The second half of that sentence -- "the gate passes having run nothing
relevant" -- could not happen even if the first half were true. An empty
`selected` is the gate's LOUDEST branch: it widens to the full suite and prints
why, and `tests/test_impact_gate_selects_data_dependencies.py` already pinned
that with a control.

**VERDICT: the defect as stated does not exist on this tree.** A fix built on
that framing would have been a fix to a fixed thing.

---

## 2. WHAT IS ACTUALLY WRONG, WHICH IS NARROWER AND MORE DANGEROUS

### 2.1 An audit-doc selection is very nearly a CONSTANT

For 213 audit documents the analyser returns TEN test files, and they are the
SAME ten for every one of them:

    tests/test_a_cited_sha_resolves.py
    tests/test_a_correction_is_findable_from_the_claim.py
    tests/test_an_asserted_name_resolves.py
    tests/test_blocker_map_is_derived.py
    tests/test_impact_gate_selects_data_dependencies.py
    tests/test_state_cell_dialects_refuse_loudly.py
    tests/test_the_audit_index_is_derived.py
    tests/test_the_blocker_reason_locator_states_its_recall.py
    tests/test_the_rulings_register_is_derived.py
    tests/test_the_unassigned_reason_is_not_a_default.py

Across all 213 documents only FOUR file-specific selections ever appear on top
of that ten. Those ten really do read every document, so this is not wrong --
but it means the discrimination for that whole class lives in the basename
match alone, and 2.2 is where the basename match breaks.

### 2.2 A STEM COMPOSED AT RUNTIME IS NOT TEXT, AND THE ANALYSER IS TEXT

`data_tokens()` matches the last path segment, bounded, and the docstring's
argument for picking that token is correct: the basename is what survives
`ROOT / "_audit" / "<name>"`.

**It does not survive a composed STEM.** Counted by AST -- every `Path`
division whose right operand is an f-string or a string concatenation --
there are **38 such sites in 24 files**:

| where | shape |
|---|---|
| `tests/test_free_read_panels.py` (3 sites) | `(FIXTURES / f"{fixture}.html")`, with `HYDRATED = "job_detail_hydrated"` three lines above |
| `tests/test_job_description_readiness.py:99` | `(FIXTURE_DIR / f"{which}.html")` |
| `tests/test_job_detail_wiring.py:77` | `(FIXTURES / f"{fixture}.html")` |
| `tests/test_save_candidates_fixture.py` (2) | `(FIXTURE_DIR / f"{name}.html")` |
| `tests/test_tracker_harvest_census.py:58` | `(FIXTURE_DIR / f"{which}.html")` |
| `tests/test_tracker_readiness.py:81` | `(FIXTURE_DIR / f"{which}.html")`, and at line 170 `markup(f"jobs_tracker_{which}")` -- the stem composed a SECOND time before the extension is added |
| `tests/test_unfired_probe_verdicts.py:45` | `SCRIPTS / (name + ".py")` |
| `tests/test_vendored_buildinfo.py` (6) | composed names under the vendored tree |
| `tests/test_ci_shard.py` (4), `tests/test_auth_lifecycle.py`, `tests/test_every_orphan_module_is_ruled.py`, `tests/test_profile_version_gate.py`, `tests/test_writes.py:87` | the same shape |
| 13 sites in `scripts/` | capture and probe outputs |

**A GREP FOR THE SAME THING FOUND 11.** The AST pass found 38. The difference
is not a detail: it is the reason this wave was told to parse the structure,
and the undercount ran in the direction that makes the problem look smaller.
The same gap appears twice more below -- `spec_from_file_location` is in
**35** files where a grep of `tests/` showed 25, and **37** files import from
another `tests.test_*` module where a narrower grep showed 28.

**Measured consequence, before any change.**
`tests/test_free_read_panels.py` reads `tests/fixtures/job_detail_hydrated.html`
at eleven call sites through the constant `HYDRATED`. The analyser's selection
for that fixture was **22 test files and that reader was not one of them.**

That is worse than the defect the brief described. An empty set widens to the
full suite and says so; twenty-two somethings without the one that matters is a
PASS.

---

## 3. THE INSTRUMENT: STOP INFERRING WHO READS A FILE, AND WATCH

`scripts/build_read_map.py` (new) runs the suite with `builtins.open`,
`io.open`, `subprocess.run` and `subprocess.Popen` instrumented, attributes
every read to the OUTERMOST `tests/test_*.py` frame on the live stack, and
writes `scripts/impact_gate_read_map.json`.

Outermost, not innermost, is the whole point: when `tests/repo_paths.py` or a
`markup()` helper composes the path and opens it, the test file that ASKED is
still on the stack above.

**One full recording, 2865s (47m42s), `-n auto`: 8661 raw edges over 143 test
files, 192 unattributed reads.** Pruned for shipping to non-python targets
that are FILES (a walk opens its directory, so the first pruning kept rows
for `.` and `_audit`): 2294 edges over 86 test files, 117 KB.

Two defects in the instrument, both found by running it rather than by reading
it, and both are the kind this repository catalogues:

* **`builtins.open` and `io.open` are the same function object and DIFFERENT
  NAMES.** `pathlib` holds `import io` and calls `io.open`, so a
  `builtins`-only wrapper recorded nothing from `Path.read_text`. The first
  smoke run recorded four census documents, every one of them from a `git show`
  ARGV, and not one of the `Path` reads those same tests perform. Patching both
  names took one test file from 5 recorded edges to 220.
* **An argv is not a path.** `Path("git").resolve()` is `<repo>/git`:
  repo-relative, plausible, and not a file. The first run recorded `git` and
  `show` as read targets. Existence is now the filter.

And the repository's own guard caught a third, in my code, on the first full
run: `tests/test_an_outage_is_never_filed_as_an_absence.py` refused
`build_read_map.py:293` for returning `""` out of an `except OSError`. It was
right -- that empty string would have been written into the map's `head` field
as a blank, indistinguishable from a repository that legitimately reports
nothing, and a map that cannot say which commit it describes is a map nobody
can age.

### 3.1 The number the brief asked for

Over the 266 tracked data files, the recording holds **2271 true (data file ->
test file) edges.**

| analyser | true edges MISSED | over how many files | mean plan |
|---|---|---|---|
| **as it stood at `f729a2a`** | **37 (1.6%)** | 12 of 266 | 23.7 |
| + the composed-name rule | 15 (0.7%) | 7 of 266 | 24.0 |
| + the path-load hop | 13 (0.6%) | 5 of 266 | 25.0 |
| + the recording unioned in | 0 | 0 | 25.1 -- CIRCULAR, see R7 |

**A NOTE ON THE FIRST ROW, because two of these numbers were taken an hour
apart and they disagreed.** A later pass read the "before" figure as 35 over 10
files rather than 37 over 12. That is not drift and it is not noise: the
path-load hop of section 4.2 has NO SWITCH -- it is part of the import walk --
so a run that disarms `composed_coupling` and `observed_coupling` still has it,
and it recovers two edges on its own. The 37 is the honest pristine number,
measured before that hop existed. The mixed reading is recorded here rather
than quietly dropped, because a "before" column that silently contains half the
change is the commonest way a cost table flatters itself.

The 37 fall into exactly three shapes, none of which any widening of a name
rule could reach:

1. **A fixture borrowed across test modules by pytest INJECTION.**
   `from tests.test_writes import (...)  # fixtures are used by injection`.
   The fixture does the reading; the importer is the file that must run. 37
   files in this suite do it.
2. **A script loaded by PATH**, `importlib.util.spec_from_file_location`, which
   no import parser can see. 35 files.
3. **A composed stem** (section 2.2). 38 sites.

---

## 4. THE COUPLING BUILT, AND WHAT DEFEATS IT

Three additions, each with its own switch so a control can disarm it, because
a selector whose rules cannot be disarmed individually cannot be shown failing
at all.

### 4.1 `composed_coupling` -- read the f-string as the pattern it is

`composed_name_patterns()` walks the AST for `JoinedStr` and string-`Add`
nodes and turns each into a regex with the holes CAPTURED:
`f"{fixture}.html"` becomes `([^/\\]*)\.html`, `f"jobs_tracker_{which}"`
becomes `jobs_tracker_([^/\\]*)`. Each is tested by `fullmatch` against three
strings -- the changed file's BASENAME, its STEM, and its whole repo-relative
path.

Two independent guards keep it from becoming a floor:

* **An ancestor-directory requirement at the call site.** The pattern only
  fires for a file that also names one of the changed path's ancestor
  directories as a quoted segment -- the same discipline the existing
  directory rule already applies with its sweep-verb requirement.
* **A three-tier verdict** (`composed_verdict`):
  * `EXACT` -- the pattern matches and every hole is filled by a string
    literal the file itself contains. `HYDRATED = "job_detail_hydrated"` is
    that literal, three lines above the read.
  * `SHAPE` -- the pattern matches, no literal fills the hole, and the file
    enumerates NO name of that shape. That is "I cannot tell", so it couples.
  * `None` -- the pattern matches and the file DOES enumerate names of that
    shape, and this is not one of them. The only narrowing in the function,
    and it is bounded: a file that sweeps its directory was coupled by an
    earlier branch, so by the time control reaches here the file does not
    glob -- its names are the ones it names.

**WHAT DEFEATS IT.** A composed name whose literal anchor is shorter than
three characters is discarded (`f"{a}-{b}"` fullmatches half the tree and means
nothing). A reader that borrows its directory constant from another module and
so names no ancestor directory itself is not reached. And a stem that comes
from a list built elsewhere -- imported, or read from a file -- lands in the
`SHAPE` tier, which couples generously rather than precisely.

### 4.2 `loads it by path` -- the narrowest form of the text edge

At hops 1..N, in addition to the import walk, a file that contains another
file's FULL repo-relative path as a literal is coupled to it. Scoped to
`scripts/` sources, and the scope was measured rather than assumed: run over
package modules as well, `linkedin_server/shape.py` went from 123 selected to
**159 of 208** and the analyser from 7s to 18s, for zero recovered edges.
`scripts/` is not a package, so a test that wants a script reaches for the
file; `linkedin_server/` is imported normally.

This is a different instrument from the basename text edge the module's
docstring rules out. A bare stem (`shape`) matches prose across the tree; a
path with its directory and its extension is an ADDRESS.

### 4.3 `observed_coupling` -- the recording, unioned in

`impact_gate.py` reads `impact_gate_read_map.json` and adds every test file
recorded reading a changed path. **ADDITIVE ONLY, and that is a law**: a test
written since the recording is absent from it, so absence proves nothing and
may never trim a plan. The report prints the recording's date and commit beside
the verdict, how many files it added that no static rule found, and -- when
the recording was NOT taken at this commit -- says so in a line of its own
rather than leaving the reader to compare two short shas. When there is no map
on disk at all it says that every edge above is inferred.

**WHAT DEFEATS IT.** Staleness, structurally: a test added after the recording
contributes nothing, which is why the static rules are not replaced by it. A
module-level read in a shared helper is attributed only to whichever test file
imported it FIRST, because the second importer never triggers the read; the
static import rule covers that hop. A child process's own reads are invisible
and only its argv is recorded.

### 4.4 ONE THING TRIED AND REJECTED, because it is the most tempting repair

The obvious fix for the fixture-injection class is to expand the walk THROUGH
test modules: make a test file a node and not just a sink. It was built and
measured, and it collapsed the selector:

| change | before | with test-module expansion |
|---|---|---|
| `_audit/_census/jobs.md` | 16 selected | **71** |
| `tests/fixtures/job_detail_hydrated.html` | 27 selected | **158 of 208 (76%)** |
| `linkedin_server/shape.py` | 123 | 164 |
| analyser wall clock | ~5s | 18-28s |

That is the 158-of-170 failure the module's own docstring records, reproduced
by a different route: once test modules are nodes with unlimited depth and
every edge kind, the import graph closes over the suite. Bounding it to one
import-only hop still took that fixture from 27 selected to 45. The recording
supplies the same edges at a mean cost of **+0.1 test files**, so the structural
approximation was dropped in favour of the measurement. The reverted design is
recorded here rather than in the code, so the next person to think of it finds
the number instead of the idea.

---

## 5. COST: THE IMPACT-SET SIZE BEFORE AND AFTER

Sizes are SELECTED test files; `plan` is what pytest is actually handed (the
selection unioned with the 15-file corpus-wide floor). 208 test files on disk.
**BEFORE here means `composed_coupling` and `observed_coupling` disarmed**, so
it carries the path-load hop of 4.2 -- see the note in 3.1. The true delta from
`f729a2a` is therefore a little larger than these columns show.

| class | change | selected BEFORE | selected AFTER | plan BEFORE | plan AFTER |
|---|---|---|---|---|---|
| source | `linkedin_server/shape.py` | 125 | 126 | 131 | 132 |
| script | `scripts/build_blocker_map.py` | 22 | 23 | 27 | 28 |
| test | `tests/test_shape.py` | 57 | 57 | 62 | 62 |
| census md | `_audit/_census/jobs.md` | 17 | 20 | 29 | 29 |
| census tsv | `_audit/_census/blocker-map.tsv` | 14 | 16 | 26 | 26 |
| audit doc | `_audit/2026-09-03-linkedin-gap-blockers.md` | 12 | 15 | 25 | 25 |
| baseline json | `tests/tool_envelope_baseline.json` | 13 | 13 | 20 | 20 |
| fixture | `tests/fixtures/job_detail_hydrated.html` | 24 | 29 | 31 | 36 |
| fixture | `tests/fixtures/jobs_tracker_row.html` | 17 | 24 | 24 | 31 |
| fixture | `tests/fixtures/synthetic/drawn_routes.txt` | 17 | 17 | 24 | 24 |
| ci config | `.github/workflows/ci.yml` | 1 | 3 | 16 | 16 |

Three of those rows have a larger SELECTION and an unchanged PLAN -- the census
`.md`, the `.tsv` and the audit doc. The files the new rules found were already
in the corpus-wide floor, so the gate runs exactly what it ran before and now
knows WHY it is running it. That is worth having on its own: a plan whose
provenance is a floor cannot be audited, and a floor that happens to cover a
real reader is luck, not coupling.

**Over all 266 observed-read data files: the mean plan went from 23.7 test
files at `f729a2a` to 25.0 with the static rules and 25.1 with the recording
unioned in, out of 208, and the maximum did not move.**
No plan shrank -- verified by comparing every file's set before and against
after, with **zero** edges removed, which is the property that matters for a
gate: every change here widens or does nothing.

The widening is concentrated in ONE class, fixtures, and it is bounded: at
most +7 selected files, from a base of 17-24. Nothing crosses the 45% line at which
the gate abandons scoping, and the number of data files that would widen to the
full suite is unchanged at 1 (`pyproject.toml`, which is a declared global
trigger anyway).

Analyser wall clock is unchanged within noise: 4-8s per call on a loaded box,
against 4-9s before. The composed-name parse is LAZY -- it runs only on files
that already passed the directory prefilter -- and memoised per corpus.

---

## 6. THE CONTROL: A DATA CHANGE THE OLD GATE PASSES AND THE NEW GATE CATCHES

### 6.1 The specimen, chosen from the recording rather than guessed

`tests/fixtures/jobs_tracker_row.html` has **10 observed readers**. The
analyser at `f729a2a` missed FIVE of them --
`test_apply_modal_fixture`, `test_click_is_not_its_own_evidence`,
`test_tracker_harvest_census`, `test_tracker_readiness`, `test_writes`. After
this wave it misses none.

### 6.2 The change

`tests/test_tracker_readiness.py` builds a DERIVED page by
`derive(markup("jobs_tracker_row"), "<main>", '<nav>...</nav><main>')`, and
`derive()` asserts the edit landed. So the mutation is one character:

    <main>   ->   <main >

**Semantically a no-op to every HTML parser, textually fatal to a real guard**,
and a realistic edit -- it is what a reformat of a captured fixture looks like.
It was staged with `git add`, put to both gates, and then reverted.

### 6.3 The old gate: EXIT 0, PASS

The gate as it stands at `f729a2a` (its own file restored from `HEAD`, and this
wave's two new files removed from `scripts/` so the tree is faithful):

```
impact-gate: 1 changed path(s) -> 15 SELECTED + 15 corpus-wide = 23 test file(s).
    tests/test_a_person_name_is_never_a_literal.py     (sweeps the directory)
    tests/test_a_sanitiser_earns_its_entry.py          (sweeps the directory)
    tests/test_ci_shard.py                             (sweeps the directory)
    tests/test_every_ignore_entry_is_declared.py       (sweeps the directory)
    tests/test_impact_gate_selects_data_dependencies.py  (imports impact_gate)
    tests/test_no_committed_credential.py              (sweeps the directory)
    tests/test_no_committed_identity.py                (sweeps the directory)
    tests/test_proximity_is_on_a_read_surface.py       (sweeps the directory)
    tests/test_readers_outside_dom_are_a_pinned_inventory.py (sweeps the directory)
    tests/test_scripts_are_import_safe.py              (sweeps the directory)
    tests/test_sdui_surfaces_fixture.py                (names the path)
    tests/test_surface_census.py                       (names the path)
    tests/test_the_audit_index_is_derived.py           (imports build_audit_index)
    tests/test_the_rulings_register_is_derived.py      (imports build_rulings_index)
    tests/test_the_sanitisation_key_is_unignorable_under_any_name.py (names the path)
  + 15 CORPUS-WIDE guard(s), run unconditionally ...
  4 corpus-wide SWEEP(s) inside them answered on the CHANGE rather than the tree, in 2492 ms:
      [...]

  PASS over the 23 file(s) above (1784 tests) -- AND OVER NOTHING ELSE.

  NOT CHECKED: 185 of 208 test files (88.9% of the suite by file).
  The corpus-wide guards DID run, so the identity, credential and page-text
  sweeps cover the whole tree. Everything else above is unexamined.
  That is roughly 4310 of 6094 tests unrun (70.7%), against a suite count taken 2026-09-20 at 970a276.
  Wall clock: 216.9s.
  THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
  certifier; a green gate here is not a reason to shrink that matrix.
```

`EXIT=0`. Twenty-three files, 1784 tests, green -- on a tree with three red
tests in it.

Fifteen names, and the file that reads this fixture eleven times is not one of
them. Nine of the fifteen are there only because they SWEEP `tests/fixtures/`
looking for identifiers -- they would be selected by any fixture at all.


### 6.4 The new gate: EXIT 1, REFUSED

Same staged index, same box, this wave's gate:

```
impact-gate: 1 changed path(s) -> 24 SELECTED + 15 corpus-wide = 31 test file(s).
    [...]
    tests/test_tracker_harvest_census.py
        via tests/fixtures/jobs_tracker_row.html -> ... (composes this exact name (/([^/\\]*)\.html/))
        via tests/fixtures/jobs_tracker_row.html -> ... (OBSERVED reading it in the recorded suite run)
    tests/test_tracker_readiness.py
        via tests/fixtures/jobs_tracker_row.html -> ... (composes this exact name (/jobs_tracker_([^/\\]*)/))
        via tests/fixtures/jobs_tracker_row.html -> ... (OBSERVED reading it in the recorded suite run)
    tests/test_writes.py
        via tests/fixtures/jobs_tracker_row.html -> ... (composes this exact name (/([^/\\]*)\.html/))
        via tests/fixtures/jobs_tracker_row.html -> ... (OBSERVED reading it in the recorded suite run)
  observed read map: 87 test files recorded 2026-09-21 at f729a2a; it added 2 file(s) here that no static rule found.
    A test written since that recording is ABSENT from it, so it can only ever ADD to this plan, never trim it.
  + 15 CORPUS-WIDE guard(s), run unconditionally ...

REFUSED: a test this change can reach is RED.
    FAILED tests/test_tracker_harvest_census.py::test_a_hidden_row_still_harvests
    FAILED tests/test_tracker_harvest_census.py::test_a_visibility_hidden_row_is_what_ACTUALLY_breaks_the_harvest
    FAILED tests/test_tracker_readiness.py::test_the_walk_is_scoped_to_main - Ass...
    FAILED tests/test_impact_gate_selects_data_dependencies.py::test_reverting_the_data_rule_loses_the_test_again
    4 failed, 2106 passed, 1 xfailed in 298.97s (0:04:58)

  changed:
    tests/fixtures/jobs_tracker_row.html

  NOT CHECKED: 177 of 208 test files (85.1% of the suite by file).
  [... the same scope report, printed on failure as loudly as on success ...]
  Wall clock: 300.4s.
  Bypass, if you truly mean to: git commit --no-verify
```

`EXIT=1`. The cost of catching it was **eight more test files and 84 more
seconds**.

### 6.5 The fourth failure in that run is the best thing in this document

`tests/test_impact_gate_selects_data_dependencies.py::test_reverting_the_data_rule_loses_the_test_again`
went red -- the repository's OWN control on the gate, refusing MY change. It
asserts that with `data_coupling=False` the census ledger reaches nothing, and
two new rules now reached it by another route. **A control that names one
switch while the code has three has quietly stopped controlling the thing it
claims to.** It was repaired by disarming all three, not by loosening the
assertion.

### 6.6 The new rules, shown failing

Four controls were added to that file (21 tests now pass in 74s), and two were
put to a mutation to prove they can fail:

| mutation | result |
|---|---|
| `composed_verdict`'s narrowing clause forced to `True` (couple on the shape alone) | `test_the_composed_rule_refuses_a_shape_the_reader_enumerates` FAILED -- `tests/test_free_read_panels.py` was dragged into a tracker-capture edit |
| `read_map()` returns `{"edges": {}}` instead of `None` when the file is absent | `test_an_absent_read_map_is_reported_and_never_read_as_empty` FAILED -- "a missing read map must read as None, never as an empty recording" |

The positive arms (`test_a_composed_stem_reaches_the_file_that_composes_it`,
`test_a_twice_composed_stem_reaches_it_too`,
`test_a_script_loaded_by_path_carries_its_data_to_the_loader`) each have a
negative twin that disarms the rule and asserts the same target goes dark, so
neither a selector that returns everything nor one that returns nothing passes
both arms.

---

## 7. RESIDUAL

**R1. The recording is a cache and it will go stale.** A test written after
2026-09-21 at `f729a2a` contributes nothing to it. The union with the static
rules means staleness can only cost precision, never safety, and the stamp is
printed on every run -- but nothing yet FORCES a rebuild. A `--recount`-style
staleness threshold (refuse to use a map more than N commits old, or rebuild in
CI on a schedule) is the obvious next step and is not built. Rebuild cost is
2865s.

**R2. Thirteen true edges remain unreachable by any static rule here, and
every one of them is the fixture-injection class.** They are
`test_apply_modal_fixture`, `test_verification_that_could_not_read`,
`test_save_candidates_fixture` and `test_click_is_not_its_own_evidence`, over
five fixtures -- each borrowing a pytest fixture from another test module by
import. The recording covers them; nothing static does, and section 4.4 is why
the structural repair was not taken. If the recording is ever dropped, those
five fixtures go back to being edited with their readers unrun.

**R2b. The `SHAPE` tier still over-selects on fixtures.** A file that composes
`f"{x}.html"` and enumerates no html literal is coupled to EVERY html change.
Four test files are in that position, which is where most of the +5 to +7 on
fixture plans comes from. Resolving it needs the hole's possible VALUES, which
means following a `parametrize` list or an imported constant -- real work, and
the current cost does not justify it.

**R3. The analyser is O(corpus) per invocation, not O(change).** Each
`impact_set()` call builds its own `Corpus` and re-reads ~600 files: 4-8s on a
loaded box, and 2127s to sweep 266 files one at a time. That is fine for the
gate, which calls it once, and it is why every census in this document took
half an hour. A module-level corpus cache keyed on mtime would fix it. Not
built; it changes no verdict.

**R4. `candidate_files()` globs three directories FLAT.** There is no `.py`
under `tests/`, `scripts/` or `linkedin_server/` in a subdirectory today, so
the flat glob is correct today. The day somebody adds `tests/unit/`, every file
in it becomes invisible to the analyser and nothing will say so. A guard that
asserts the flat glob still covers what pytest collects would close it.

**R5. `.github/workflows/ci.yml` selects exactly ONE test file.** The
recording agrees -- only `tests/test_the_package_compiles_on_its_oldest_python.py`
reads it. That is a true reading and also a thin one: CI is the certifier, and a
change to the matrix is the change least checkable from here. Out of scope for
an impact analyser; named so nobody reads the 1 as coverage.

**R6. Five tests were already red on this tree during the recording**
(`test_click_is_not_its_own_evidence`, `test_a_cited_sha_resolves`'s cheapness
guard, `test_typeahead_gate`, `test_sweep_blobs_refuses_a_vacuous_pass`, and my
own `build_read_map.py` outage defect, since fixed). Seven other waves were
writing at the time. The recording captures READS, not verdicts, so a red test
still contributes its edges -- but a test that died before opening its fixtures
would be under-recorded, and I have not separated those cases.

**R7. The recall numbers in 3.1 are measured against the recording, so the
line "with the observed map unioned, 0 missed" would be CIRCULAR and is not
claimed.** The honest figures are the static ones: 37 -> 13 true edges missed
by rules that never saw the recording. The map's contribution is stated as what
it is -- a union of measured edges -- not as a recall improvement.

**R8. This wave merges LAST and the tree will have moved.** Every count here
is at `f729a2a` with 208 test files; the gate that ships runs against whatever the
merge produces. The controls are written against named artifacts and FAIL
loudly (never skip) if one is renamed, and every derived number the gate prints
is computed at run time, not baked in. The one baked artifact is the read map,
and it is additive by construction.

---

## INSTRUMENTS

| file | what it is |
|---|---|
| `scripts/build_read_map.py` | NEW. Records which test file reads which data file, by instrumenting `builtins.open`, `io.open` and `subprocess`. Re-runnable: `python scripts/build_read_map.py`. |
| `scripts/impact_gate_read_map.json` | NEW. The recording, stamped with its date and commit; the gate prints that stamp, and says so when it was not taken at this commit. |
| `scripts/impact_gate.py` | `composed_name_patterns`, `composed_verdict`, `composed_targets`, `read_map`, `observed_readers`, and the `loads it by path` hop. |
| `tests/test_impact_gate_selects_data_dependencies.py` | Four new controls plus the repaired one. Two shown failing by mutation. |
