# The impact gate: a check whose cost is a function of the change, not of the tree

`scripts/impact_gate.py`, `tests/test_impact_gate_selects_data_dependencies.py`,
`scripts/impact_gate_suite_size.json`. Measured 2026-09-20 in a worktree at
`970a276`, windows, `venv/Scripts/python.exe`, pytest `-n auto --dist loadfile`.

The brief was not "make the gate faster". It was that a full-suite gate is
**O(suite)** -- it gets worse with every feature, forever -- and an
impact-scoped gate is **O(change)**, which stays flat. This builds the second
one. The exponent is visible in this very change: adding ONE script and ONE
test file moved the suite from 6076 tests to 6094, because nine parametrised
meta-tests sweep `scripts/*.py` and grew simply because a file appeared. Under
a full-suite gate every future commit pays for those nine, including every
commit that cannot possibly touch them.

---

## 1. LEAD WITH THIS: the census-data defect, which is the whole difference between a gate and a rubber stamp

An impact gate is only as honest as its selector, and the obvious selector for
this repository is already on disk: `coupled_test_files()` in
`scripts/pre_commit_boundary_gate.py`. Its rule is **name-based over python** --
file B is coupled to staged file A when B names a module-level CONSTANT that A
defines. It is a good rule for the class it was built for.

**It is blind to the class that broke this repository the same morning.**

### The reproduction, measured, not argued

Commit `5d0efb5` fixed a one-line defect: a `**CORRECTED BY:**` marker had been
inserted between a table header and its first data row in
`_audit/2026-09-03-linkedin-gap-blockers.md`. `scripts/build_blocker_map.py`
reads that table with `_table_after()`, which takes rows until the first
non-pipe line -- so it took zero, and every blocker came back unknown to the
ledger parse.

I reversed that commit in a worktree, staged it, and put it to both:

| | result |
|---|---|
| `git diff --cached --name-only` | `_audit/2026-09-03-linkedin-gap-blockers.md` |
| **`pre_commit_boundary_gate.py`** | **exit 0, ZERO bytes of output, ZERO tests run** |
| `staged_paths()` | `[]` -- it keeps only `*.py`, so a `.md` never reaches the rule |
| `coupled_test_files([...])` | `[]` |
| **the truth** | `tests/test_blocker_map_is_derived.py` -- **2 failed, 5 passed in 1.16s** (3.07s wall) |

An impact gate keyed on that rule would have returned zero tests and waved the
breakage through: faster than the full suite, and wrong in the only direction
that matters. A gate that is silent on a red tree is worse than no gate,
because its presence implies a check nobody is running.

### Why the obvious extension does not work either

The instinct is "also grep for the file path". That fails too, and the reason
generalises:

> **A document that is also a DATA SOURCE is read by a PATH, and a path is not
> a name.**

`build_blocker_map.py` opens the ledger as
`ROOT / "_audit" / "2026-09-03-linkedin-gap-blockers.md"` -- composed from
segments at runtime, so the repo-relative string appears nowhere in any source
file. And the failing test never mentions the ledger at all; it does
`import build_blocker_map`. The coupling is **two hops over two different kinds
of edge**:

```
_audit/2026-09-03-linkedin-gap-blockers.md
    --named by-->     scripts/build_blocker_map.py
    --imported by-->  tests/test_blocker_map_is_derived.py
```

So the gate uses **three readers for three couplings**, and the match between
instrument and edge is the design, not an implementation detail:

| coupling | instrument | why not the others |
|---|---|---|
| python dependency | **AST import parse** | `linkedin_server/shape.py` has stem `shape`; a text scan for that word hits docstring prose in most of the suite |
| data dependency | **path scan, basename-anchored** | the path is composed at runtime -- there is no import to parse and no constant to match; the basename is the only token that survives assembly |
| shared constant | **the shipped `coupled_test_files`, imported not copied** | catches a structure pinned by a LITERAL COPY in another file, with no import between them |

### The measurement that forced a fourth mechanism: prose is not dependency

The first working version scanned raw source for the path. It selected **158 of
170 test files in 14.7s**, then **93 of 170** after the text edge was made
non-transitive. A selector returning 93% of the tree is not selecting; it is
laundering a full run through a narrowing story, which is worse than an honest
full run because it claims to have reasoned.

The cause was specific and checkable: `linkedin_server/readonly.py:2045`
mentions that ledger in a `#` comment and `linkedin_server/server.py:185`
quotes it in a module docstring. **Neither opens it.** In a repository whose
house style puts long argued docstrings on nearly every file, raw text is mostly
essay -- and an essay names everything it reasons about.

So the data scan runs over source with **comments and docstrings stripped**
(`code_text()`, via `tokenize` + AST). 93 files -> 9. Two further precision
fixes followed, both found by checking rather than reasoning:

- a directory token fires only for a file that also shows a **sweep verb** --
  `tests/repo_paths.py` holds `Path("_audit") / "_sanitisation_key.json"`,
  which names the folder to reach ONE file inside it and can never be affected
  by a different document there. 9 -> 5.
- `walk` was removed from the sweep-verb list because a bare `\bwalk\b` matched
  **`ast.walk`** in `test_a_covered_row_names_the_artifact_that_covers_it.py`,
  which traverses a syntax tree and no directory at all. It is spelled
  `os.walk` now. 5 -> 4.

Final: **`_audit/2026-09-03-linkedin-gap-blockers.md` -> 4 selected test files**,
including `tests/test_blocker_map_is_derived.py` via exactly the two-hop chain
above. The old rule's answer was 0.

It reads as **5** everywhere below, and the extra one is the control file added
by this same change: `tests/test_impact_gate_selects_data_dependencies.py`
spells that ledger path as a literal, so the gate selects it. That is the rule
working on its own author's file, not drift.

### The same defect, through the finished gate

```
impact-gate: 1 changed path(s) -> 5 SELECTED + 13 corpus-wide = 17 test file(s).
    tests/test_blocker_map_is_derived.py
        via scripts/build_blocker_map.py -> tests/test_blocker_map_is_derived.py (imports it)
REFUSED: a test this change can reach is RED.
    FAILED tests/test_the_unassigned_reason_is_not_a_default.py::test_the_six_rows_no_longer_claim_that_nobody_names_them
    FAILED tests/test_blocker_map_is_derived.py::test_the_ledger_tables_still_total_97_blockers_and_409_rows
    FAILED tests/test_blocker_map_is_derived.py::test_no_blocker_recounts_higher_than_the_ledger_published
    3 failed, 1862 passed in 23.86s
```

**Exit 1 in 25.7s wall.** It also found a third failure that `5d0efb5`'s own
commit message never mentions -- the impact set was wider than the known
defect, and correctly so.

---

## 2. The third category, which no coupling rule can ever reach

Mid-build, a sibling wave reported shipping red to CI **twice in one day**, one
cause both times, in its own words: *"a local selection that ran the files I
touched and their neighbours and missed guards whose names connect to nothing I
was working on"* -- `test_page_text_is_never_printed.py` and
`test_no_committed_identity.py`.

I verified the diagnosis on disk before acting on it, and it is not a coupling
bug. `test_no_committed_identity.py` sweeps **every tracked file, including
`.md` and `.tsv`**, so a census edit can trip it -- while it names no document
and imports nothing from any diff. It is coupled to *everything* and therefore
to nothing in particular. **The relationship is real and maximal; it is the
ANALYSIS that has no handle on it.** No widening of the rules in section 1 could
ever select it.

So the plan has three parts:

```
selected     coupled to the diff -- name, import, constant, data path
+ floor      every corpus-wide sweep, run UNCONDITIONALLY
= plan
```

The floor is **derived, not listed** (`always_run_files()`): a test qualifies if
its file enumeration takes no input from the diff -- it calls `git ls-files`,
walks the repo root, or sweeps two or more top-level folders. That yields **13
files / 1797 tests / 25.6s**, and both proven members are found. Derived rather
than hand-written for the reason the boundary gate already gives about its own
rule: a hand-written pair is correct for the instance that produced it and blind
to the next one. A control pins the two proven members so the derivation is
**checked rather than believed**.

### The trap this created, and why the fields are kept apart

The floor is never empty. Had the plan been a single merged list, the
"empty impact set" alarm in section 4 **could never have fired again** --
permanently satisfied by a guarantee that says nothing whatever about whether
the analyser worked. That is a check that cannot fail, introduced by the very
change meant to make the gate safer, and invisible because everything would
still look green.

`Impact.selected` and `Impact.always_run` are therefore separate fields, the
alarm tests `selected`, and
`test_the_floor_does_not_mask_an_empty_selection` asserts it so the trap cannot
be reintroduced.

---

## 3. Measured latency, five change shapes

Analysis time is the selector alone; wall clock is the complete gate including
pytest. All plans include the 13-file corpus-wide floor.

| shape | staged path | selected | + floor | analysis | tests run | **wall** |
|---|---|---:|---:|---:|---:|---:|
| **source file** | `linkedin_server/jobfilter.py` | 47 | 54 | 2.2s | 3343 | **190.9s** |
| **boundary file** | `linkedin_server/readonly.py` | 96 | 103 (61%) | 3.2s | -- | **widens to full suite** |
| **census data** | `_audit/2026-09-03-linkedin-gap-blockers.md` | 5 | 17 | 1.3s | 1862 | **25.7s** |
| census data | `_audit/_census/blocker-assignments.tsv` | 5 | 17 | 1.3s | -- | -- |
| runner config | `tests/conftest.py` | 17 | 24 | 1.4s | -- | **widens to full suite** |

Reference points, all from this box:

| | |
|---|---|
| full suite, collect-only | **36.2s cold / 7.0s warm** -- before a single test runs |
| full suite, 6-way xdist | **6189 passed in 10m41s (641s)** *(relayed from a sibling wave, not re-measured here)* |
| full suite, repo's own record 2026-09-19 | 913s serial / 601s `-n auto` |
| CI, three platforms | 1042s (17 min); windows shards 409-460s |
| **old gate on the census defect** | **0s, exit 0, zero tests -- and wrong** |

**Read this honestly rather than favourably.** The census-data case is a 25x
win (25.7s against ~641s). The source-file case is only **3.4x** (190.9s against
~641s), because `jobfilter.py` is imported by `server.py` and most of the suite
imports `server` -- that is genuine transitive coupling, not selector noise, and
190s is the true cost of touching a module the server depends on. The gate's
value is therefore not uniform: it is large exactly where the repository does
most of its editing (census documents, audit tables, leaf scripts) and small
where a change genuinely reaches the core.

I did **not** re-measure the full suite locally. The box is running roughly
thirty sibling agents, and a `-n auto` full-suite run would both produce a
contended number and degrade their gates. The 641s figure is a relayed reading
with a timestamp, labelled as such.

---

## 4. The fallback rule

Three conditions widen to the full suite. Each prints its reason; none of them
may narrow silently.

| condition | trigger | rationale |
|---|---|---|
| **empty** | `impact.selected` is empty | an empty selection is indistinguishable from a broken selector from outside, so it is never a pass |
| **too wide** | plan >= **45%** of the 168 test files | past this the scoped run is no longer fast, so the scoped claim buys nothing and the complete claim costs the same order of time |
| **unclassified** | a staged path in `_GLOBAL_TRIGGERS` | `tests/conftest.py`, `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`, `requirements*.txt` |

`tests/conftest.py` is the sharp member of the third row: its fixtures are
**autouse**, so it is loaded by every test in the suite and named by almost
none of them -- exactly the coupling a name-based analyser cannot see.

**The 45% line is a PRODUCT decision, not a cost one, and the numbers argue
both ways.** On pure cost it is too aggressive: a 103-file plan is roughly 61%
of the files and would still save perhaps 40% of the wall clock. But the gate's
product is a signal fast enough that nobody reaches for `--no-verify`, and at
100 files that signal is already minutes long -- a slow partial answer, which is
the worst of both. With the sibling wave's 10m41s upper bound for the full
suite, **falling back is a ten-minute case, not a disaster**, so it is right to
fall back often rather than strain to classify every edge. The constant is one
line and cheap to re-rule.

Two further widening behaviours, same principle, different inputs:

- **unreadable or unparseable is UNKNOWN, never ABSENT.** `code_text()`,
  `_imports_of()` and `Corpus.raw()` return `None` on failure, and every call
  site couples defensively on `None`. `changed_paths()` returns `None` when git
  cannot answer, and the gate says *"the impact set is UNKNOWN -- not empty"*
  instead of reading an outage as an all-clear.
- **deletions are tokenised, never dropped.** A vanished file is the one case
  where name-based rules are at their most useful and content-based ones are
  useless: nothing can be read out of a file that is gone, but everything that
  NAMES it is about to break.

---

## 5. The control: the selector shown FAILING

`tests/test_impact_gate_selects_data_dependencies.py`, **13 tests**.

A selector is unusually exposed to the disease this repository has hit three
times in two days -- a check that cannot fail -- because a selector that returns
EVERYTHING and one that returns NOTHING both look calm from outside: one never
refuses, the other never fires. So every rule is disarmable by keyword
(`data_coupling=`, `import_coupling=`, `constant_coupling=`, `always_run=`), and
the control asserts both arms.

**Shown failing, by reverting the coupling rule in the source and re-running:**

```
$ sed -i 's/data_coupling: bool = True/data_coupling: bool = False/' scripts/impact_gate.py
FFF..........
FAILED ...::test_the_census_ledger_selects_the_test_that_caught_it
FAILED ...::test_the_census_evidence_table_selects_it_too
FAILED ...::test_the_selection_travels_the_two_hop_chain_and_not_a_coincidence
3 failed, 10 passed in 4.37s
```

Restored byte-identical (`diff -q` clean); **13 passed in 10.9s**.

The negative arm runs on every CI cycle rather than living in a comment:
`test_reverting_the_data_rule_loses_the_test_again` asserts that with the rule
off the census ledger reaches **nothing at all**. There is no version of a
broken selector that passes both arms -- return everything and the negative arm
reddens, return nothing and the positive arm does.

Also pinned:

- `test_the_shipped_constant_rule_is_still_blind_to_this` asserts
  `coupled_test_files([LEDGER]) == []`, so a later simplification back onto the
  boundary gate's rule fails loudly instead of quietly restoring the hole.
- `test_a_docstring_that_cites_the_ledger_is_not_coupled_to_it` asserts on
  **both** sides -- the raw source must still contain the citation, or the test
  is measuring nothing, and the stripped code must not.
- `test_the_floor_is_derived_and_still_finds_the_two_proven_guards` fails and
  names them if the detector ever narrows past the two guards that cost CI
  cycles.
- `test_a_scoped_plan_names_what_it_did_not_run` fails if the unrun count is
  ever demoted from the verdict to a footnote.

### An accident worth recording

The first draft of the empty-set test spelled its sentinel path as one literal
and **failed**: the gate selected the control file itself, because that file's
own source named the path. That is precisely what the data rule is supposed to
do. A sentinel meant to be unreachable cannot be spelled in the corpus it is
unreachable from; it is assembled from fragments now, and the accident stands as
the rule demonstrating itself against a file written to have no dependencies.

### And the gate caught a real defect in its own author

The first dogfood run -- the gate applied to its own staged change -- came back
**RED**:

```
FAILED tests/test_an_outage_is_never_filed_as_an_absence.py::test_no_probe_returns_a_falsy_datum_from_an_exception_handler
    impact_gate.py:225
```

`code_text()` returned `""` from an `except OSError`. An empty string means
"this file mentions nothing"; a file that cannot be read means "unknown" -- and
the two were the same value to every caller, so an I/O error would have silently
**removed a candidate from the plan**. That is the exact failure this gate
exists to prevent, reproduced inside the gate, found by the suite rather than by
me. Repaired by taking the remedy the guard itself named (`None`, and widen at
the call site) rather than the one that would have cleared the red.

---

## 6. What this does NOT replace

**CI stays. Do not shrink the matrix.** `.github/workflows/ci.yml` runs this
suite across three platforms; this box is windows-only, and windows-vs-linux
defects -- path separators, encodings, line endings, filesystem-dependent guards
-- are exactly what CI has been catching. This is the fast local signal that
tells you before you push; **CI is the certifier**. The claim is written into
the module docstring and printed in the gate's own output on every scoped run,
so nobody can read a 25-second pass as grounds for deleting a platform cell.

The gate also prints, every time, on success as loudly as on failure:

```
  NOT CHECKED: 151 of 168 test files (89.9% of the suite by file).
  The corpus-wide guards DID run, so the identity, credential and page-text
  sweeps cover the whole tree. Everything else above is unexamined.
  That is roughly 4229 of 6094 tests unrun (69.4%), against a suite count taken 2026-09-20 at 970a276.
```

Where it cannot derive a number it says so rather than estimating. The
denominator is cached in `scripts/impact_gate_suite_size.json` **with the commit
it was taken at**, so its staleness is visible; a missing cache downgrades the
report to file counts, which are exact and free.

---

## 7. Known imprecision, stated rather than hidden

The selector over-couples in one identified way, and over-coupling is the safe
direction (it runs more, never less):

- a file that names a directory **and** shows a sweep verb is coupled to
  everything in that directory, even when it actually reaches one named child.
  Sampled 4 of the `jobfilter.py` hits: 3 were genuine directory sweeps, 1
  (`SERVER = REPO / "linkedin_server" / "server.py"`) was not. A refinement that
  tried to distinguish these would be fragile heuristics on top of a rule that
  is currently sound in the direction that matters.

Two things the gate still cannot see, and neither is claimed:

- a coupling carried entirely by a runtime-constructed string with no literal
  segment anywhere in the source;
- a behavioural coupling with no textual trace at all -- shared global state,
  import-order effects. The corpus-wide floor is the partial answer; CI is the
  complete one.

## 8. Open decisions, not taken here

1. **Wiring.** `.git/hooks/pre-commit` currently runs the identity gate only
   (~0.2s), by deliberate ruling. I did **not** change it. Whether the impact
   gate belongs in the hook, in a pre-push hook, or stays a hand-run command is
   a latency decision the hook's own history has strong opinions about -- a slow
   hook earns `--no-verify`, and the bypass habit is the real loss.
2. **The 45% line** (section 4), which is one constant and a product judgement.
3. **The floor's 25.6s**, which is now paid on every invocation. It is the price
   of not shipping a real name into served history, and that trade should be
   made knowingly rather than inherited.
