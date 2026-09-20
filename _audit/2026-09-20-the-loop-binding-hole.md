# The loop-binding hole in the navigation taint walker

2026-09-20. Wave: `agent-a5ab0e661aa3fea66`, branch `worktree-agent-a5ab0e661aa3fea66`.
Written as the work ran, in order.

**One sentence.** `tests/test_navigation_is_never_derived.py` -- the AST taint walker
that backs this server's read-only boundary -- bound `Assign` and `AnnAssign` and
nothing else, so a derived url reaching `goto` (or a `print`) through a `for` target,
a comprehension target, an `async for`, a `with ... as` or a walrus was invisible to
it. The sibling page-text walker had already fixed exactly this and never carried it
back. The treatment is ported, seven reds were watched failing first, and the live
tree measures **zero** instances at either sink.

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

Measured, not reasoned, with `scratchpad/probe_cases.py`:

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
      await BROWSER.goto(page, u)
  -A FOR TARGET IS A BINDING...]
FAILED ...::test_it_goes_red_on_a_derived_navigation[
  ...
  seen = [await BROWSER.goto(page, u) for u in queue]
  -A COMPREHENSION TARGET IS A BINDING TOO...]
FAILED ...::test_it_goes_red_on_a_derived_navigation[
  ...
  async for u in following(landed):
      await BROWSER.goto(page, u)
  -AsyncFor binds exactly as For does...]
FAILED ...::test_it_goes_red_on_a_derived_navigation[
  ...
  with holding(landed) as u:
      await BROWSER.goto(page, u)
  -`with ... as` binds...]
FAILED ...::test_it_goes_red_on_a_derived_navigation[
  ...
  if (u := landed):
      await BROWSER.goto(page, u)
  -THE WALRUS BINDS...]
FAILED ...::test_output_goes_red_on_a_navigation_derived_value[
  landed = await BROWSER.goto(page, X)
  for u in [landed]:
      print(u)
  -THE SAME HOLE AT THE OTHER SINK...]
FAILED ...::test_output_goes_red_on_a_navigation_derived_value[
  landed = await BROWSER.goto(page, X)
  queue = [landed]
  [logger.info(u) for u in queue]
  -A COMPREHENSION TARGET AT THIS SINK...]
```

The `assert []` in each failure is the point: `violations()` and `output_violations()`
returned an **empty list** for a navigation aimed at a url the browser chose.

Six GREEN pairs were added in the same commit and passed both before and after the
fix, because a walker that binds every loop target is a walker that flags every loop:
a `for`/`async for`/`with`/walrus over urls this repository authored, and
`for i in range(len(landed))` -- where the counting carve-out must survive the wider
bindings or the rule starts forbidding its own remedy.

---

## 3. (filled in below as the work ran)
