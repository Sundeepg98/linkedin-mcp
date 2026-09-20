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
`./venv/Scripts/python.exe`, run
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

Delegated as a closed-form slice (`walker-divergence`), verified against SHA
`5c24b05` on a clean `tests/`, full file at
`scratchpad/walker-divergence.md`. **I re-ran its three load-bearing claims
myself before accepting them**; all three reproduced.

**It corrected my brief.** I was told a third guard "imports only a constant and a
file-lister" from the navigation engine. Measured:
`tests/test_probe_navigation_budget.py` imports **nothing** from it -- its only
imports are `__future__`, `ast` and `pathlib`. I verified that directly. It is not
even about the same rule: it classifies whether a `.goto` was allowlist-GUARDED, not
whether its argument is browser-derived. I relayed that claim without checking it; the
child declined to conform its write-up to the brief, which is the correct behaviour
and is why the error surfaced.

**The finding worth acting on: the page-text guard inherits a url-scoped safety claim
and applies it to page text.** The page-text walker imports `_is_sanitiser_call` from
the navigation guard, and that predicate answers over `_SANITISERS` -- whose entries
are proven **for urls only**. `_redact`'s own docstring in the navigation guard says
so in as many words, and adds that "a display name sitting beside a lowercase word
passes straight through it". Reproduced:

```
name = await item.inner_text()
print(_redact(name))

B._tainted_names      -> ['name']          (the value IS tracked as tainted)
B.text_violations     -> []                (and the print is NOT flagged)
control, no _redact   -> [(2, 'print')]    (so the flagger still flags)
```

So `print(_redact(<page text>))` is waved through by the rule built to stop exactly
that. **Live instances in the tree: ZERO** -- I swept all 175 files for an output sink
whose argument applies any of the three url sanitisers to a value the page-text walker
considers page text, and found none. Latent, not live, and named rather than left
implied.

Two further structural items, both reproduced by me:

- **A bare-name call is invisible to both taint-source checks.** Both engines match a
  taint source only in attribute-call form. `l = goto(X); print(l)` -> `[]`;
  `l = BROWSER.goto(X); print(l)` -> `[(2, 'print(l)')]`. Nothing in this codebase
  calls the browser API bare, so it is a shared latent gap -- shared **by
  construction**, not by any cross-check, and neither docstring mentions it.
- **The three call-classifying predicates are not shape-symmetric with each other.**
  `_is_sanitiser_call` matches both `f(x)` and `o.f(x)`; the counting carve-out matches
  a Name only, so `print(payload.len(landed))` is flagged. Inert today (nothing defines
  a `.len()` method) and worth knowing before someone adds one.

Items where the child checked and found the code FINE -- listed so coverage can be told
from silence: `_member_path`/`_path_of` absent from `_SANITISERS`; the page-text
inventory header's "111 sites, 25 files" (exact); `KNOWN_DERIVED_NAVIGATIONS == {}`;
the 4-pass convergence claim I wrote (independently re-derived as 4, same file);
`read_surface_census` absent from `TEXT_CALLS`; the budget guard's empty
`KNOWN_UNGUARDED`. Its own "what I did not check" list names the historical
measurements it declined to reproduce and the negative half of the binding
comparison, which it deferred to my pin rather than re-deriving.

---

## 4c. ESCALATION -- a demonstrated bypass of the page-text guard

**Not fixed. Not mine to rule. Reported here and to the coordinator.**

The question asked was narrow and empirical: does page text actually ESCAPE through
the url-sanitiser stop, or is the laundering merely inelegant? **It escapes.**

### The chain, measured end to end

```
STEP 1  B.text_violations("name = await item.inner_text()\nprint(_redact(name))\n")
        -> []                       the guard reports the site CLEAN

STEP 2  B.text_violations("name = await item.inner_text()\nprint(name)\n")
        -> [(2, 'print')]           the flagger still flags, so step 1 is not
                                    an empty result standing in for a pass

STEP 3  scripts/_probe_messaging.py::_redact("<two invented words> commented on this")
        -> "<two invented words> commented on this"        BYTE-IDENTICAL
```

Every string used is invented -- two ordinary words nobody is called, in the shapes
this package actually reads off LinkedIn.

### What survives, per input shape

`scripts/_probe_messaging.py::_redact` -- the implementation the navigation guard's
own `_SANITISERS` note describes:

| page-text shape | outcome |
|---|---|
| a card byline (`<Name> commented on this`) | **LEAKS**, byte-identical |
| plain prose (`Congratulate <Name> on the new role`) | **LEAKS**, byte-identical |
| a name beside a lowercase word (`by <name>, 2h ago`) | **LEAKS**, byte-identical |
| an aria-label (`<Name>'s profile photo`) | held -> `<NAME>'s profile photo` |
| a headline (`<Name> - Staff Engineer at <Company>`) | held |
| a message preview (`<Name>: thanks, ...`) | held |

**3 of 6.** And the control the trap-list demands: on the input it was actually
proven for -- a url carrying a vanity slug -- it **holds**, returning
`https://www.linkedin.com/in/<SLUG>/`. So the function is not broken. **It is
correctly scoped to urls, and the page-text guard is applying it outside that scope.**

### Why this is worse than an inelegance

- **Two safety mechanisms agree on a wrong answer.** An author who does the
  right-looking thing -- reach for a redactor before printing -- is waved through by
  the guard AND handed a redactor that does not redact prose. Nothing in either path
  says "out of scope".
- **The stop is matched BY NAME, globally, across every scanned module.** There are
  **16 definitions** of the three sanitiser names in this tree, including **two
  different `_redact`s with different properties**: the messaging one is a pattern
  list and leaks on prose; `scripts/_probe_search_render_timeline.py::_redact` is
  allowlist-based ("membership, not absence") and **held on all 6** page-text shapes.
  The guard treats them identically because it only sees the name.
- The navigation guard's own note already says `_redact` "is NOT a general-purpose
  name redactor... a display name sitting beside a lowercase word passes straight
  through it." That warning is true, it is written down, and the page-text guard
  inherits the recognition **without** inheriting the warning -- because it imports
  `_is_sanitiser_call`, not the paragraph above it.

### Is this a known trade or a gap nobody ruled? Measured: nobody ruled it

`tests/test_a_sanitiser_earns_its_entry.py` is the certifier that admits a function to
`_SANITISERS`. **Every fixture in its corpus is a url** -- I grepped its whole fixture
set and its `MUST_DISCRIMINATE` pairs and found `https://www.linkedin.com/...` and
nothing else. It contains no page text, no prose, no display-name case, and the words
"page text", "inner_text", "prose" and "display name" do not appear in it at all.

So the certification means "shapes a url safely" and was never asked to mean more. The
page-text guard then consumes that certification as if it were general. **Nobody
decided that; it fell out of an import.** That is the difference between a trade-off
and an invariant nobody ruled, and it is why this is escalated rather than filed.

### How live is it

**Zero live instances, in BOTH spellings, with both detectors shown working.**

My first sweep was wrong and I caught it before reporting it. It looked only for a
sanitiser call sitting INSIDE a sink argument -- `print(_redact(name))` -- and would
have missed the two-step form, which is at least as natural a thing to write:

```
shaped = _redact(name)      # the taint stops here, by design
print(shaped)               # and sweep 1 never looks at this line
```

A zero from a sweep that cannot see the commoner spelling is not a zero. Re-run over
all 175 files looking for both:

```
files parsed: 175
form 1  sanitiser call INSIDE a sink argument      : 0
form 2  name bound to a laundered value, then sunk : 0

CONTROL form 1 planted -> detector form1=1 form2=0  (SEEN)
CONTROL form 2 planted -> detector form1=0 form2=1  (SEEN)
```

Each detector convicts its own planted case and not the other's, so neither zero is an
empty result standing in for a pass.

So this is a demonstrated bypass that nothing exercises today -- which is the moment
to rule on it, not evidence that it is safe. "Nothing has leaked" is the argument that
produced the third slug leak, and this file says so at the top.

### What I did NOT do, deliberately

I did not add a `TEXT_SANITISERS`-side fix, did not scope `_is_sanitiser_call`, and
did not touch either `_redact`. Every available repair is a change to what a guard
will silence, and that is a boundary question. The options, for whoever rules it:

1. Stop ORing A's predicate into B -- B's own set is empty by design, so B would then
   have no sanitiser stop at all, which is arguably the honest state given its own
   finding that this package has no instrument that can decide whether a string is a
   person's name.
2. Keep the OR but scope it: a sanitiser entry declares WHAT it is proven for, and a
   guard consults only entries proven for its own kind of value.
3. Rule that the two `_redact`s must not share a name, since the stop is name-based.

Option 2 is the one that generalises, and it is the one that costs a schema change to
`_SANITISERS`. None of them is a line I should take alone.

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
| `global` / `nonlocal` rebinding | ~~BLIND~~ | **SEEN -- I HAD THIS WRONG** | see 7b |
| function parameters | BLIND | **STILL BLIND** | needs inter-procedural flow |

All the "STILL BLIND" rows are pinned **by name** in
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

### 7b. The exhaustive census -- and a correction to section 7

Delegated as a closed-form slice (`binding-census`), landed at
`scratchpad/binding-census.md`. **38 measured rows, every one with a positive AND a
negative control, and every control passed.** 4 rows UNMEASURED with reasons, 1
construct added beyond the brief. It handled HEAD moving under it correctly: diffed
the incoming commit, confirmed the delta was entirely inside a docstring with zero
executable lines, and said so rather than aborting or silently absorbing it.

**IT CONTRADICTED ME, AND IT WAS RIGHT.** Section 7's table said `global`/`nonlocal`
rebinding was STILL BLIND. It is SEEN. I verified the correction myself before
accepting it:

```
my original global case      -> blind
global rebind of a tainted v -> [(3, 'CACHE')]
same source, global DELETED  -> [(3, 'CACHE')]
```

`global LEAK; LEAK = landed` is two statements: an inert `ast.Global` plus an
**ordinary `ast.Assign`** the walker already handles. Taint is by name and per module,
so the rebinding propagates regardless of scope. Deleting the keyword changes nothing
-- that is the proof it contributes nothing either way.

**Why my probe said blind: I built the discriminating test badly.** My case passed the
value in through a function PARAMETER, and parameters are blind. So I measured the
parameter hole and filed it under the global row. This is the same failure as the
"already red for the wrong reason" case in section 2.1, running in the opposite
direction -- **blind for the wrong reason** -- and I caught the first one and shipped
the second. A control that comes back the colour you expected is the one you do not
re-examine.

The child's reconciliation is precise and I am adopting its scoping: the narrow claim
in `test_the_two_walkers_bind_the_same_forms` -- that `_bindings` never dispatches on
a bare `ast.Global` node -- **remains true and is not contradicted**. What was false
was generalising that to "the form is invisible to the rule". And the loophole is
specific: `except ... as`, `AugAssign` and parameters each bind ONLY through their own
node type, with no plain `Assign` hiding underneath, so their BLIND verdicts stand.

**The census's full result set**, beyond what section 7 covered:

| verdict | constructs |
|---|---|
| **SEEN** (23) | assignment, annotated, chained (`a = b = t`), tuple/list unpacking, starred unpacking, subscript target (and the KEY name too), attribute target, `for`, `async for`, nested-tuple `for`, list/set/dict/generator comprehension targets, nested comprehension, `with ... as`, `async with ... as`, second withitem in one `with`, `with ... as (tuple)`, walrus in `if` / in a comprehension `if` / in `while`, `global`, `nonlocal` |
| **BLIND** (15) | `AugAssign`, `except ... as`, `except*` groups, all five parameter forms (positional, keyword-only, default, `*args`, `**kwargs`), lambda parameters, `match` capture / `as` / star patterns, decorator-bound names, PEP 695 `type X = EXPR` |
| **N/A -- no value slot** (4) | `import x as y`, `from m import x as y`, bare `def`/`class` name binding, PEP 695 generic brackets `[T]` |

That last row is worth its own line: those four are **not gaps**. There is no
expression in the syntax for a tainted value to arrive through, and `alias.asname` is
a plain `str` rather than an `ast.Name`, so no walker could find it. "Unmeasured" was
the wrong word for them and the census supplied the right one.

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

**The drift detector, mutated from the SIBLING side** -- which is the direction it
actually exists for, since the historical failure was the page-text guard fixing this
and nobody noticing it had not come back:

| sibling-side mutation | detector | what it names |
|---|---|---|
| shipped state | agrees | -- |
| sibling gains `AugAssign` | **fires** | `only in sibling: [('AugAssign', 'r')]` |
| sibling loses the `For` binding | **fires** | `only in mine: [('AsyncFor','d'), ('For','c')]` |

It fires in both directions and says which side moved, so the failure is a routing
slip rather than a bare inequality.

Three readings I want on the record:

- **The drift detector earns its entry.** It independently catches five mutants from
  my side and both from the sibling's, where a single red case each would otherwise
  be the only guard. Shown failing, per the register's second law.
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

**What a child caught that I had shipped**

- I claimed `global`/`nonlocal` rebinding was blind, in a docstring AND in section 7.
  It is SEEN. My probe conflated it with the parameter hole -- I measured one thing and
  labelled it another. Corrected in both places, with the reason, rather than quietly
  edited. It is the second time in this wave that a case came back the expected colour
  for the wrong reason, and the first time I did not catch it myself.

**What I changed that I was not asked to**

- Corrected a fixed-point claim in a docstring I had just written and had guessed at
  (2 -> 4 passes, measured). Worth naming because it is the same defect class the file
  is about: prose asserting something nothing checks.

**What I found and did not fix**

- **A DEMONSTRATED BYPASS of the page-text guard (section 4c).** `print(_redact(<page
  text>))` is reported clean by the guard, and the redactor returns a plain name
  byte-identical in 3 of 6 realistic page-text shapes, while holding on the urls it
  was proven for. Zero live instances in 175 files. **Escalated, not patched** -- every
  available repair changes what a guard will silence.
- `AugAssign` binding, open on both walkers by choice.
- The navigation guard's bare-basename inventory key (latent; zero collisions today).
- **A sanitiser admission that three places record, that was attempted, REFUSED FOR A
  GOOD REASON, and reverted -- while the prose still narrates it as landed.** I first
  wrote this up as "an admission that never happened", which was wrong in the way that
  matters: it reads as an oversight, and it was a ruling. The divergence child found
  the half I was missing, one file away, and I verified it. Reported, not fixed:

  | claim | where | truth |
  |---|---|---|
  | "``_why_refused`` -- admitted to _SANITISERS 2026-09-19, WITH ITS CONTRACT" | comment at line 1188 | it is **not** in the set |
  | "THE FOURTH ENTRY EXISTS SO A PROBE CAN SAY WHY A LANDING WAS REFUSED..." | docstring at line 895 | there are three |
  | `_SANITISERS == frozenset({_shape_of, _redact, _relation})` | the pin, line 159 and its assertion | three, and the pin passes |

  The proof test `test_why_refused_returns_only_its_own_literals` **exists and runs**.
  The function is real. And parsed rather than grepped,
  `scripts/_probe_landed_address_sweep.py` contains **zero references** to
  `_why_refused` -- defined at line 185, never called.

  **Why the entry is absent is the point, and it is recorded in the wrong file.** The
  comment at `scripts/_probe_landed_address_sweep.py:244`, which a reader starting from
  the guard will never reach:

  > "The sanctioned route is an entry in `_SANITISERS`, and I took it and then GAVE IT
  > BACK: the enrolment table refused the entry. `_why_refused` fails
  > `MUST_DISCRIMINATE` on both pairs... That table certifies SHAPERS -- functions
  > mapping a url to a relation or a redaction -- and this is a VERDICT function, a kind
  > it has never been asked to certify. Reshaping the function to satisfy the table, or
  > widening the table to admit the function, would both have been getting a green
  > rather than earning one."

  **So the CODE is right and the PROSE is stale.** The entry was refused on a principled
  ruling; `_SANITISERS` holding three is correct; the pin asserting three is correct;
  the live behaviour is correct (`print(_why_refused(landed))` is flagged today, exactly
  as an unregistered function should be). What is wrong is two places in the guard
  narrating an admission that was given back, and a comment dated to the day it happened
  saying it landed.

  This is the repository's own `read_settings_surface` pattern, and one turn worse: a
  ruling whose reason lives only in the file that was refused, so every reader starting
  from the claim reaches the wrong document. Two outside registries
  (`test_a_sanitiser_earns_its_entry.py`, `test_a_verdict_earns_its_entry.py`) agree
  with the code; only this file's prose disagrees with its own set three lines below it.

  The correction is three lines of prose and it is still not mine: it touches the
  narration around a silencing set, and the wave that ruled it should be the wave that
  writes down what it ruled.
