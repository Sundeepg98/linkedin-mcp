# The loop-binding hole in the navigation taint walker

2026-09-20. Wave: `agent-a5ab0e661aa3fea66`, branch `worktree-agent-a5ab0e661aa3fea66`.
Fix commit `5c24b05`. Written as the work ran, in order.

**One sentence.** `tests/test_navigation_is_never_derived.py` -- the AST taint walker
that backs this server's read-only boundary -- bound `Assign` and `AnnAssign` and
nothing else, so a derived url reaching `goto` (or a `print`) through a `for` target,
a comprehension target, an `async for`, a `with ... as` or a walrus was invisible to
it. The sibling page-text walker had already fixed exactly this and never carried it
back. The treatment is ported, seven reds were watched failing first, and the live
tree measures **zero** instances at the navigation sink and **one** new one at the
output sink which is a name collision rather than a leak.

---

## 1. The baseline, before anything was touched

```
$ venv/Scripts/python.exe -m pytest tests/test_navigation_is_never_derived.py -q
381 passed in 27.98s
```

Note for anyone reproducing: `venv/` is gitignored, so it does **not** exist inside a
worktree. The interpreter used throughout is the main checkout's
`D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\venv\Scripts\python.exe`, run
with the worktree as cwd. That is the standing worktree trap, hit again here.

---

## 2. The red, first, and what it cost to make it honest

### 2.1 The first attempt at a comprehension red was already red, for the wrong reason

The obvious output-sink comprehension case is

```python
landed = await BROWSER.goto(page, X)
print(next(u for u in [landed]))
```

It **passed on the unfixed walker.** Not because the walker understood the generator
target -- because the iterable `[landed]` sits inside the same expression as the sink,
so `_is_tainted_expr`'s subtree walk reaches `landed` without ever needing the binding.
A red case that fires for a reason other than the one it names proves nothing about
the defect, and would have shipped as a check that could not fail in the way its
comment claimed.

Measured, not reasoned (`scratchpad/probe_cases.py`):

| candidate output-sink shape | unfixed walker |
|---|---|
| `print(next(u for u in [landed]))` -- sink OUTSIDE the comprehension | ALREADY RED |
| `print("\|".join(u for u in queue))` -- sink OUTSIDE | ALREADY RED |
| `[logger.info(u) for u in queue]` -- sink INSIDE | **BLIND** |
| `any(print(u) for u in queue)` -- sink INSIDE | **BLIND** |
| `d = {i: print(u) for i, u in enumerate(queue)}` -- sink INSIDE | **BLIND** |

The rule that falls out: **for a comprehension, the target is the sole route to the
sink only when the sink is inside the comprehension.** Anywhere else the enclosing
expression carries the taint and the binding is never consulted. The shipped case is
the INSIDE one, and its docstring says why the other was rejected.

### 2.2 The seven reds, failing on the unfixed walker

```
$ venv/Scripts/python.exe -m pytest tests/test_navigation_is_never_derived.py -q \
      -k "goes_red or stays_green"
7 failed, 29 passed, 358 deselected in 0.67s

FAILED ...::test_it_goes_red_on_a_derived_navigation[
  landed = await BROWSER.goto(page, SELF_PROFILE_URL)
  queue = [landed]
  for u in queue:
      await BROWSER.goto(page, u)                       -A FOR TARGET IS A BINDING...]
FAILED ...  seen = [await BROWSER.goto(page, u) for u in queue]
                                          -A COMPREHENSION TARGET IS A BINDING TOO...]
FAILED ...  async for u in following(landed): ...       -AsyncFor binds as For does...]
FAILED ...  with holding(landed) as u: ...              -`with ... as` binds...]
FAILED ...  if (u := landed): ...                       -THE WALRUS BINDS...]
FAILED ...::test_output_goes_red_on_a_navigation_derived_value[
  for u in [landed]:
      print(u)                             -THE SAME HOLE AT THE OTHER SINK...]
FAILED ...  [logger.info(u) for u in queue]  -A COMPREHENSION TARGET AT THIS SINK...]
```

The `assert []` inside each failure is the point: `violations()` and
`output_violations()` returned an **empty list** for a navigation aimed at a url the
browser chose.

Six GREEN pairs were added in the same commit and pass both before and after the fix,
because a walker that binds every loop target is a walker that flags every loop: a
`for` / `async for` / `with` / walrus over urls this repository authored, and
`for i in range(len(landed))` -- where the counting carve-out must survive the wider
bindings or the rule starts forbidding its own remedy.

---

## 3. The fix, and what "port the treatment, not the code" came to

`_bindings(node)` now sits in the navigation guard, structurally identical to the
sibling's, and `_tainted_names` iterates it instead of testing `isinstance(node,
(ast.Assign, ast.AnnAssign))` inline. Ten node classes bind: `Assign`, `AnnAssign`,
`For`, `AsyncFor`, `ListComp`, `SetComp`, `GeneratorExp`, `DictComp`, `withitem`,
`NamedExpr`.

Two things were deliberately NOT done:

- **The two walkers were not merged.** They are not one engine and must not become
  one -- see section 4. What was shared is the part that carries no knowledge of
  taint at all.
- **No binding form was added beyond sibling parity.** `AugAssign` in particular is a
  one-line addition and is genuinely missing from both. Adding it here alone would
  re-open, in the other direction, the exact divergence this commit exists to close.
  It is named in section 7 as open rather than quietly fixed on one side.

The fixed-point cap moved 4 -> 6, matching the sibling. **A claim I wrote there was
wrong and is corrected in the same commit**: the docstring first said the deepest
module converges in 2 passes, which I had not measured. Measured across all 175 files
it is **4** -- the old cap exactly. The walker was one binding form away from silently
truncating its own taint set, and a cap that under-approximates does not raise; it
returns a smaller set and the rule goes quiet.

---

## 4. What else diverged between the two walkers

Measured, not read off the similarity of the code. A child agent
(`walker-divergence`) was given this as a closed-form slice and its findings are in
section 4b; what follows is what I established directly.

| | navigation guard | page-text guard |
|---|---|---|
| taint SOURCES | `_TAINTED_ATTRS={url}` (a bare attribute read) **and** `_TAINTED_CALLS={goto}` | `TEXT_CALLS` -- 16 reader methods, **calls only**, no bare-attribute taint |
| sanitisers | `_SANITISERS`, 3 entries | `TEXT_SANITISERS`, **deliberately empty** -- and it applies BOTH predicates |
| bindings | was 2 forms | was 10 forms -- **now equal and pinned** |
| fixed-point cap | was 4 | 6 -- **now equal** |
| reads files as | `encoding="utf-8"` | `encoding="utf-8", errors="replace"` |
| inventory KEY | bare basename, `"_probe_x.py"` | folder-qualified, `"scripts/_probe_x.py"` |
| inventory VALUE | list of expression strings | an integer count per file |
| sink detection | `_sink_calls` -- **imported by the sibling, so sinks cannot drift** | same function |
| `_python_files` | defined | defined again, byte-for-byte equivalent, not imported |

Two observations worth someone's attention, neither fixed here:

- **The navigation guard's inventories key on `path.name` alone**, so a file of the
  same basename in both scanned folders would share one declaration. Measured today:
  135 files in `scripts/`, 40 in `linkedin_server/`, **zero basename collisions**. It
  is latent, not live. The sibling's folder-qualified key does not have the hazard.
- The two inventory VALUE types have different rot-resistance. A list of expressions
  fails when a site's *text* changes; a count fails only when the *number* changes.
  Neither is wrong; they are different instruments and the difference is not written
  down anywhere.

### 4b. The divergence child's findings

(Pending at the time of the freeze -- see section 10.)

---

## 5. The sweep: the measured count

Corpus frozen and stated: HEAD `cf16bc9` at sweep time, `git status --short scripts
linkedin_server` **empty**. 175 files across `scripts/` and `linkedin_server/`.
Read RAW -- ignoring `KNOWN_DERIVED_NAVIGATIONS` and `KNOWN_TAINTED_OUTPUT` -- because
a sweep read through the declarations reports the declarations.

```
NAVIGATION SINK  pre-fix 0  post-fix 0   -> NEW: 0
OUTPUT SINK      pre-fix 8  post-fix 9   -> NEW: 1
deepest fixed point across all scanned modules: 4 passes (cap is 6)
```

**The navigation sink measures ZERO, and it is a zero this instrument can move off.**
That last clause is the whole value of the number. An assertion satisfied by an empty
result cannot fail, so the same sweep was re-run over the same 175 files with a
deliberately over-tainting walker (`scratchpad/zero_control.py`):

```
files swept            : 175
goto call sites in them: 152   (the sweep has something to look at)

SHIPPED walker          NAV sites 0     OUT sites 9
OVER-TAINTING control   NAV sites 86    OUT sites 1232
```

86 of the 152 navigation sites are reachable by a permissive taint set and the shipped
walker convicts none of them. The zero is a measurement, not a silence.

---

## 6. The one new output site, and why it is declared rather than fixed

`scripts/_probe_job_search_filter_params.py` line 1295, `print(text)`.

**It is a name collision, not a leak.** The chain:

- line 945 `kept_reading = _key_kept(parameter, landed_url)` -- tainted *before* this
  wave, because `landed_url` is tainted and `_key_kept` is not a sanitiser;
- line 964 `for text in _key_kept_lines(parameter, kept_reading):` -- the new For
  binding taints the name `text`;
- taint here is **by name and per module**, a deliberate over-approximation argued in
  `_tainted_names` (a function-scoped analysis would be blind to the closure shape the
  rule was written for), so that one `text` taints **every** `text` in the module --
  including the parameter of a nested `emit` helper 330 lines away.

What the site actually emits was **measured, not assumed**: `_key_kept_lines` returns
the parameter literal this file asked for, two integers (both `len`), two booleans
rendered as YES/NO and IS/IS NOT, and an occurrence count. `_key_kept` builds
`raw_values` and `decoded` off the landed query and returns neither. No landed value
leaves it.

So why declare it instead of calling it clean? Because the clean route is
`_SANITISERS`, and that list has a bar: **a function must ship with the test that
proves its contract.** `_redact` was admitted on the strength of its name and turned
out to have no slug rule at all. My reading of `_key_kept_lines` is a reading, and a
reading is exactly what `_redact` had. The declaration states what is true today: a
rule sees this site, its emission has been read and looks clean, and nothing yet
proves it.

**The follow-up, for whoever takes it:** admit `_key_kept_lines` to `_SANITISERS` with
its own both-directions proof, the way `_relation` and `_why_refused` were argued. That
is a silencing change, so it goes through `test_a_sanitiser_entry_is_a_claim_about_a_contract`,
which will go red and force the review. **The one repair that is not allowed** is
renaming the loop variable at line 964 to clear the red: that tunes the instrument's
input until it agrees with whoever is holding it, and the class returns the next time
two scopes pick the same word.

*Escalation note:* the brief said to stop and report before fixing any real instance
reaching a **navigation** sink. There were none. This one is at the output sink and is
not a leak, so it was declared under the file's own existing mechanism rather than
escalated -- but the `_SANITISERS` promotion above **is** a boundary judgement and is
left open rather than taken.

---

## 7. Binding-form coverage

Measured against the shipped walker. `scratchpad/probe_cases.py` for the pre-fix
column, the drift test's fixture for the node-class pin. A second, exhaustive census
was delegated (`binding-census`) and is section 7b.

| binding form | before | after | note |
|---|---|---|---|
| `Assign` (incl. tuple unpacking) | HANDLED | HANDLED | over-approximates: every Name in the target is tainted |
| `AnnAssign` | HANDLED | HANDLED | |
| `for` target | **BLIND** | HANDLED | the defect |
| `async for` target | **BLIND** | HANDLED | every probe here is async |
| list/set/dict/generator comprehension target | **BLIND** | HANDLED | only reachable when the sink is inside |
| `with ... as` | **BLIND** | HANDLED | parity with the sibling; no measured site |
| walrus (`:=`) | **BLIND** | HANDLED | |
| `except ... as` | BLIND | **STILL BLIND** | see below |
| augmented assignment (`x += t`) | BLIND | **STILL BLIND** | one line; deliberately not taken alone |
| `global` / `nonlocal` rebinding | BLIND | **STILL BLIND** | needs cross-function flow |
| function parameters | BLIND | **STILL BLIND** | needs inter-procedural flow |

All four "STILL BLIND" rows are pinned **by name** in
`test_the_two_walkers_bind_the_same_forms`, with a control asserting the fixture
actually contains each form first -- otherwise those four are four assertions that
cannot fail.

`except ... as` deserves its reason rather than a shrug: `ast.ExceptHandler.name` is a
plain string and `.type` is the exception **class**, not the value bound. There is no
value expression to taint from, so a binding there would be an invention. The leak
shape that matters -- an exception whose message interpolates a url -- is
inter-procedural and this engine is not. **That is a real, named gap, not a covered
one.**

**Forms I did not check at all:** `match` capture / `as` / star patterns, `except*`
groups, `import ... as`, `def` / `class` name binding, decorator-bound names, lambda
parameters, comprehension `if`-clause walrus, and PEP 695 type parameters. Named here
rather than implied by omission; the delegated census covers them and its answer is
section 7b.

### 7b. The exhaustive census

(Pending at the time of the freeze -- see section 10.)

---

## 8. Mutation ledger -- which of my own tests notice

Mutation is how this repository's traps were found; reading is how they survived. Run
by exec from source in the scratchpad, touching no file in the shared worktree
(`scratchpad/mutate.py`, `scratchpad/mutate2.py`).

**Towards blindness:**

| mutant | caught by |
|---|---|
| baseline (no mutation) | nothing -- correct |
| drop `For`/`AsyncFor` | 6: two nav reds, one out red, two drift assertions, the live output sweep |
| drop comprehensions | 4: one nav red, one out red, two drift assertions |
| drop `withitem` | 3: the `with` red, two drift assertions |
| drop `NamedExpr` | 3: the walrus red, two drift assertions |
| drop `AsyncFor` only (keep `For`) | 3: the async-for red, two drift assertions |
| `_bindings` yields NOTHING | 11 |
| fixed point capped at 1 pass | 1: the live output sweep only |

**Towards over-taint** -- added because round one broke **no green case at all**, which
meant the six green pairs were unproven. A "this is not wrongly flagged" assertion no
mutation can break is exactly the trap measured in this repo today.

| mutant | caught by |
|---|---|
| bind targets without checking the value | 191, including **all six greens** |
| drop the counting carve-out | 3, including the `range(len(landed))` green |
| drop the comparison carve-out | 25 live-sweep failures, **no green** -- see below |
| `For` binds every name in the loop body | 2: drift, and the live **navigation** sweep |
| `_bindings` also binds `AugAssign` | 3: drift by name -- the intended review moment |

Three readings I want on the record:

- **The drift detector earns its entry.** It independently catches five mutants that
  would otherwise be caught only by a single red case each. Shown failing, per the
  register's second law.
- **The "capped at 1 pass" mutant is caught by exactly one check** -- the live output
  sweep on one file. If that file is ever fixed, nothing else in this file notices a
  truncating cap. That is thin and I am saying so rather than leaving it.
- **The comparison carve-out has no green of mine guarding it.** Its greens are the
  file's pre-existing ones (`print("/login" in landed)`), which are outside the corpus
  my mutation harness drives. Not a defect introduced here, but my harness's coverage
  stops short of it and the table would otherwise imply otherwise.

One mutant, "`_bindings` binds EVERYTHING", was **malformed** and died with an
`AttributeError` rather than running. It is superseded by "`For` binds every name in
the loop body", which is the same direction done correctly. Reported as malformed
rather than counted as a pass.

---

## 9. Gates

| gate | result |
|---|---|
| both guards, py3.13 (box interpreter) | **409 passed** |
| both guards, py3.10 via `uv run --python 3.10` | **409 passed** |
| py3.10 parse of both guard files + every `ast` class `_bindings` names | present, parses |
| `scripts/impact_gate.py --against HEAD~1` | **PASS over 18 files / 1037 tests in 85.5s** |

The impact gate's own disclosure, kept because a gate that claims more than it ran is
the failure mode it exists to avoid: **157 of 175 test files not checked (89.7% by
file, roughly 5057 of 6094 tests, 83.0%)**. The 13 corpus-wide guards did run, so the
identity, credential and page-text sweeps covered the whole tree.

3.10 was reproduced locally rather than discovered in CI, at ~45s against an ~8-minute
CI cell. That route exists because a PEP 701 f-string once parsed on this 3.13 box and
not on the 3.10 floor; nothing in this change is near that class, but the check is
cheap and the floor is real.

### 9b. CI: NOT PUSHED, and the reason is a measurement

**CI certification of `5c24b05` is UNKNOWN.** Nothing was pushed. That is a decision,
not an omission, and here is what it was made on:

- The branch is not on the remote: `git ls-remote --heads origin
  worktree-agent-a5ab0e661aa3fea66` returns empty.
- The shared free pool is already backed up by a sibling wave. At the time of the
  call, `gh run list` showed **three runs QUEUED** on branch
  `worktree-agent-a17fef46fe411787f` and none running. A fourth 20-job matrix would
  have deepened that queue for everyone and returned a queued id, not a signal.
- The platform risk this change carries is the Python-version class, and the floor
  cell (**py3.10**) was reproduced locally: 409 passed in 44s. The two remaining cells
  are py3.13 on ubuntu and on windows; the box ran py3.13 on windows, and `_bindings`
  is pure `ast` with no path, encoding or filesystem behaviour, so the ubuntu-3.13
  delta is the smallest of the three. That is an argument, not a measurement, and it
  is labelled as one.
- This is a worktree branch, not the integration target. The merge window is the
  serialisation point and whoever runs it pushes a batched tip.

If CI on this commit is wanted before the merge, it is one `git push -u origin
worktree-agent-a5ab0e661aa3fea66` away, and the run must be read as an artifact --
`gh run view <id> --json status,conclusion,headSha` with `headSha` checked against the
branch tip, because `gh run watch --exit-status` exits 0 when it never learned the
conclusion.

---

## 10. Honest ledger

**What is verified by instrument**

- The seven reds failed on the unfixed walker and pass on the fixed one; the output is
  pasted in section 2.2 rather than summarised.
- The six green pairs pass in both states, and five of the six are shown **failing**
  under the over-taint mutants -- so they are checks that can fail.
- Navigation sink: **0** instances in 175 files, with a control proving the same sweep
  reports 86 under a permissive walker.
- Output sink: 8 -> 9. The ninth's emission was read line by line; the chain that
  makes it visible was traced to a specific name collision at lines 945/964/1295.
- Deepest fixed point across the corpus: 4 passes. Cap set to 6.
- Both guard files pass on 3.13 and 3.10.

**What is derived, not verified**

- That `_key_kept_lines` cannot emit a landed value. I read its body and its callee's
  return dict; I did not write the proof test that `_SANITISERS` demands. That is
  precisely the distinction that made `_redact`'s entry wrong, so it is stated as a
  reading and the site is declared rather than exempted.

**What is unverified**

- CI. Nothing was pushed (section 11). Three-platform certification of this commit is
  **UNKNOWN**, and that is the honest word rather than a pass.
- The `with ... as` case is parity with the sibling and has no measured site behind it.
  Said in its own docstring too.

**What I changed that I was not asked to**

- Corrected a fixed-point claim in a docstring I had just written and had guessed at
  (2 -> 4 passes, measured). Worth naming because it is the same defect class the file
  is about: prose asserting something nothing checks.

**What I found and did not fix**

- `AugAssign` binding, open on both walkers by choice.
- The navigation guard's bare-basename inventory key (latent; zero collisions today).
- **A sanitiser admission that three places record and the code never made.** Measured
  while the walker was open, and reported rather than fixed, because changing
  `_SANITISERS` is a silencing change and is not this wave's to rule:

  | claim | where | truth |
  |---|---|---|
  | "``_why_refused`` -- admitted to _SANITISERS 2026-09-19, WITH ITS CONTRACT" | comment at line 1188 | it is **not** in the set |
  | "THE FOURTH ENTRY EXISTS SO A PROBE CAN SAY WHY A LANDING WAS REFUSED..." | docstring at line 895 | there are three |
  | `_SANITISERS == frozenset({_shape_of, _redact, _relation})` | the pin, line 159 and its assertion | three, and the pin passes |

  The proof test `test_why_refused_returns_only_its_own_literals` **exists and runs** --
  so the contract was proved and the entry was never added. And the whole thing is
  currently inert for a third reason: parsed rather than grepped,
  `scripts/_probe_landed_address_sweep.py` contains **zero references** to
  `_why_refused` -- it is defined at line 185 and never called. A name-based sanitiser
  stop silences nothing when nothing calls it.

  Three layers of dormancy stacked so that no check could fire: an entry that was not
  added, about a function that is not called, guarded by a pin that passes because it
  agrees with the code rather than with the prose. This is the file's own
  `read_settings_surface` pattern -- its standing example of what a stale "known hole"
  note becomes -- reproduced inside the file that cites it.
