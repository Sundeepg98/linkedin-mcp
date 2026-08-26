# Slice: the apply-modal reader gets a DERIVED fixture and real execution

Worktree: `D:\Sundeep\projects\job-hunting\mcp-servers\linkedin\.claude\worktrees\agent-ad23e7e8fd9f722a8`
Base: `66f3a1d` on `master`. Python 3.13.14, no `venv/` in this worktree.
Date: 2026-08-26.

## Headline

`dom.read_apply_modal` now executes, over a real parsed DOM, in 20 new tests.
Tests 1-6 of the brief are delivered in full.

**Tests 7 and 8 are NOT deliverable as specified, and the reason is a
production defect, not a test problem.** `writes.perform` cannot execute
`apply_job` at all -- it refuses at the anchor gate, several steps before the
click loop. The two-click loop, `TWO_CLICK_ACTIONS`, `_apply_submit_gate` and
`dom.read_apply_modal` are ALL unreachable from `perform` today. That is
escalated below rather than worked around; I changed no production code.

Two further findings came out of writing the fixtures. Both are pinned as
passing tests, neither is fixed.

## Files

| file | status |
|---|---|
| `tests/fixtures/apply_modal_derived.html` | ADDED. 5113 bytes, verified pure ASCII (0 bytes > 127). |
| `tests/test_apply_modal_fixture.py` | ADDED. 33k, verified pure ASCII. 20 tests. |

**No production file was modified.** `git status` shows exactly two untracked
additions and nothing else. `linkedin_server/dom.py` and
`linkedin_server/writes.py` were verified byte-identical after the mutation
battery below.

### Harness decision, as asked

I **copied** the launch/`set_content` pattern from `tests/test_apply_fixture.py`'s
`_with_html` rather than importing it. Reason: `_with_html` launches AND closes
a Chromium on every call, and this module takes ~24 readings. `test_writes.py`'s
own `browser_page` docstring already records the measurement -- a cold
launch-and-close is 1.35s while five `set_content` loads on a live browser cost
0.89s between them -- so the launch is essentially the whole price. My `over`
fixture launches ONE browser per test and opens a fresh isolated
`browser.new_context()` per reading, and **asserts `window.innerWidth == 1280`
on every measurement**, because the reader calls `is_visible()` and a
visibility answer taken at an unrecorded width is not a measurement.

### The DERIVED discipline

One base fixture, every variant derived from it by an asserted `.replace()` --
the same shape as `SAVED_LIST_CONTAINING`. The `derive()` helper **asserts the
edit changed something**, which is the repo's own lesson from
`test_a_second_click_inside_perform_is_still_caught`: a derivation that cannot
prove it landed is a copy with a different name.

The fixture header separates MEASURED from INVENTED explicitly, says it is
derived from the six 2026-08-24 counts, and says in terms that **it does not
prove a live LinkedIn apply modal has this shape**. The caveat is repeated in
the test module header and in individual docstrings.

`test_the_single_observation_caveat_is_still_stated_in_full` pins the
`_apply_submit_gate` sentence **byte for byte against the production source
file**, with an assertion message that names the exact temptation ("if that was
done because 'there are tests now', put it back"). I pinned the SOURCE, not
`__doc__`: Python 3.13 strips common leading indentation from docstrings at
compile time, so an `__doc__` pin would assert a property of the interpreter
rather than of writes.py. I did not touch that docstring or any other.

## Verification

### 1. Whole suite -- `python -m pytest tests/ -q`

| | collected | passed | failed |
|---|---|---|---|
| baseline `66f3a1d`, clean tree | 1598 | **1596** | 2 |
| with this slice | 1620 | **1618** | 2 (the same 2) |

**THE BRIEF'S BASELINE OF 1598 PASSED IS NOT REPRODUCIBLE IN A FRESH
WORKTREE, and this is environmental, not a regression.** Two tests fail at a
clean `66f3a1d` before I touched anything:

```
tests/test_path_hygiene.py::test_a_cookie_jar_failure_never_returns_an_absolute_path
  [jar locked by a live Chrome]
  [jar vanished mid-read]
```

Cause, diagnosed: both monkeypatch a `cookie_jar` internal to raise, then call
`read_jar(CHROME_PROFILE, ...)`. In this worktree the call raises EARLIER than
the monkeypatched point -- "chrome profile directory does not exist: D:\...\
_state\chrome-profile" -- and that earlier message is not relativised, so the
drive-letter regex fires. **`_state/chrome-profile/` exists in the main tree
and is gitignored, so it does not come with a worktree.** The 1598 in the base
commit's own message was measured in a tree that had it. Nothing to do with
this slice; I did not create `_state/` to make it green.

Delta accounting for the +22: **20 are mine.** The other **2** are existing
repo-wide fixture sweeps picking up the new fixture file, and both pass:

```
test_sdui_surfaces_fixture.py::test_the_fixture_carries_no_session_material[apply_modal_derived.html]
test_sdui_surfaces_fixture.py::test_no_fixture_carries_a_real_opaque_linkedin_id[apply_modal_derived.html]
```

### 2. `tests/test_readonly.py` -- **99 passed**

Unchanged. `readonly.SANCTIONED_MUTATIONS` still holds exactly the 2 sanctioned
entries and no new hits:

```
('linkedin_server/writes.py', 'perform', 'click')
('linkedin_server/dom.py', 'activate_messaging_filter', 'click')
```

This was never at risk: the scanner globs `linkedin_server/*.py` only, so test
files are outside its scope by construction.

### 3. `tests/test_readonly_boundary_invariant.py` -- **9 passed**, untouched.

### 4. Can-it-fail: 10 mutations, 10 red

Every mutation was applied to the real production file, the specific test run,
and the file restored from an in-memory copy in a `finally`. Both files
verified byte-identical afterwards.

| # | mutation | file | test | result |
|---|---|---|---|---|
| M1 | `if count != 1:` -> `if count < 1:` | dom.py | two-hooked | **RED** |
| M2 | `if count != 1:` -> `if False:` | dom.py | two-hooked | **RED** |
| M3 | advance-word match -> `if False:` | dom.py | advance words (3 cases) | **RED** (3 failed) |
| M4 | `f"{APPLY_MODAL_SELECTOR} button"` -> `"button"` | dom.py | outside-the-dialog | **RED** |
| M5 | `aria-disabled != "true"` -> `True` | dom.py | `[aria-disabled=true]` | **RED** |
| M6 | `disabled is None` -> `True` | dom.py | `[disabled attribute]` | **RED** |
| M7 | `range(min(total, 40))` -> `range(total)` | dom.py | the 40-cap finding | **RED** |
| M8 | `modal_present` -> hardcoded `True` | dom.py | the two-failures finding | **RED** |
| M9 | gate `if modal.get("advance_names"):` -> `if False:` | writes.py | gate refuses multi-step | **RED** |
| M10 | gate `if not modal.get("submit_enabled"):` -> `if False:` | writes.py | gate refuses disabled | **RED** |

**Test 2 specifically -- the dead `count != 1` branch.** Both M1 and M2 turn it
red. M1 is the more interesting of the two because it is a mutation a human
would plausibly WRITE: `count < 1` still refuses zero, still reads like a
sanity check, and quietly accepts two. With it in place the reader reports
`submit_present: True` on a modal carrying two hooked controls, at which point
Playwright's strict mode makes every attribute read raise, all of them are
swallowed by the reader's own `except`, and the gate is handed
`submit_name: None`. The test goes red on `submit_present`. So yes -- test 2
genuinely exercises that branch and genuinely fails without it.

**A methodology note that cost me a false green.** My first battery selected
tests with `-k "disabled attribute"` and `-k "aria-disabled"`. pytest parses
`-k` as a keyword EXPRESSION, so a space becomes `and` and a hyphen becomes
subtraction; both produced a pytest USAGE ERROR with a non-zero exit, which my
harness scored as RED. M6 printing "(no summary)" is what exposed it. I re-ran
M5 and M6 addressed by exact nodeid, plus an unmutated control:

```
M5 aria-disabled ignored          exit 1   1 failed
M6 disabled attribute ignored     exit 1   1 failed
CONTROL unmutated                 exit 0   1 passed
```

A can-it-fail harness that cannot tell a usage error from a failure is the
thing it exists to prevent. Both are real reds.

## What test 4 revealed about `disabled` vs `aria-disabled`

**BOTH ARE HONOURED. There is no gap, and this is a measurement rather than an
assumption.**

```
submit + disabled              -> submit_present True, submit_enabled False
submit + aria-disabled="true"  -> submit_present True, submit_enabled False
submit + aria-disabled="false" -> submit_present True, submit_enabled True
```

The two are read differently and the reader gets both right:

- `disabled` is a valueless HTML attribute. `get_attribute("disabled")` returns
  the **empty string**, not the element name and not `True`. The reader
  compares `is None`, which is the correct test; a reader comparing truthiness
  would call every disabled control enabled, because `""` is falsy.
- `aria-disabled` is a STRING compared `!= "true"`. The reader tests the VALUE,
  not presence -- so `aria-disabled="false"` correctly reads as enabled.

I added `test_aria_disabled_false_is_not_read_as_disabled` as the control on
that second point, because a presence-based reader would pass both of the
required cases while being wrong about every explicitly-enabled control. That
failure is invisible from the disabled side and had to be checked from the
other one.

Also confirmed while I was in there: the private `_disabled` / `_aria_disabled`
scratch keys never leak into the result. They are popped inside a
short-circuiting boolean expression, so on `visible=False` the in-expression
pops never run and only the trailing cleanup removes them -- a real edge. Test
1 pins the complete key set rather than spot-checking fields.

## ESCALATION 1 -- `perform` cannot reach the apply gate (BLOCKS tests 7 and 8)

Measured 2026-08-26 by driving the real path -- `preview` -> `consume` ->
`perform` -- with a real redeemed grant carrying a real observation:

```
GRANT OK: apply_job 4600000042 True
PERFORM RAISED: WriteAttemptError
MESSAGE: 'apply_job' has no measured anchor and will not be performed. It is
valid from 'linkedin_apply', and the accessible name the save control wears in
that state has NEVER BEEN OBSERVED -- ...
```

**Mechanism.** `writes.perform` line ~2409:

```python
anchor = anchor_label_for(spec)
if anchor is None:
    raise WriteAttemptError(...)
```

`anchor_label_for` special-cases `unfollow_company` and otherwise answers from
`shape.SAVE_LABELS`, which is `{"Save the job": "not_saved"}` -- a table of SAVE
states. `apply_job` is valid from `linkedin_apply`, which is not a save state
and is not in that table, so the lookup falls through to `None` and apply takes
the branch written for `unsave_job`. Verified directly:

```
from_state : 'linkedin_apply'
state_from : 'apply_control'
anchor     : None
```

**Consequences, all of which follow from that one line:**

1. The click loop is never reached, so `TWO_CLICK_ACTIONS` is never consulted
   for the only action in it.
2. `_apply_submit_gate` is called from exactly one place -- inside that loop --
   so the gate is dead in production.
3. `dom.read_apply_modal` is called from exactly one place -- the gate -- so
   the reader this whole slice tests is dead in production too.
4. Even past the anchor gate, `_live_control` has **no `apply_control` branch**;
   it would fall through to `dom.read_save_control` and read the SAVE button on
   the posting, returning `not_saved` against a required `linkedin_apply`. So
   there is a SECOND blocker behind the first. (The preview path at writes.py
   ~1458 does have its `apply_control` branch. The perform path does not.)

**I did not fix this.** Whether apply should get an anchor, or be exempted from
the anchor gate the way it is already exempted from the save family everywhere
else, is a production decision and yours. What I did instead:

- `test_perform_cannot_reach_the_apply_gate_at_all` -- pins the blocker by
  EXECUTION on the real path, with a docstring that says it is expected to go
  red the day the decision is taken, and that it should then be REPLACED by the
  real end-to-end apply rather than relaxed.
- `test_a_save_never_consults_the_apply_gate` -- delivers the **achievable half
  of test 8 by execution, not by a text pin**: drives a real `save_job` all the
  way through `perform` with `_apply_submit_gate` monkeypatched to a recorder,
  and asserts the recorder stayed empty. The apply half (assert the gate IS
  called) cannot be written until the blocker is decided.
- The gate is instead driven over a REAL DOM through the REAL reader, directly,
  in four tests -- proceed, multi-step, disabled, hook/name disagreement. That
  is the reader-plus-gate coverage that never existed, and it is what test 7 was
  really after; it just cannot come in through `perform`.

Note on scope for the gate-over-real-DOM tests: only shapes where the modal AND
the submit are both present are driven through the gate, because the gate polls
15 times with a real 1s `wait_for_timeout` between attempts and a shape that
never satisfies the break condition costs 15 seconds per case. Those shapes are
covered at the reader level.

## ESCALATION 2 -- the advance scan has a ceiling of 40, and the one modal ever observed had 43 buttons

`dom.read_apply_modal`:

```python
buttons = page.locator(f"{APPLY_MODAL_SELECTOR} button")
total = int(await buttons.count())
for i in range(min(total, 40)):
```

**A visible advance control past the 40th button in the modal is reported as
absent**, and the gate reads absent as "single-screen flow" and allows the
submit. `advance_names` is the field condition 5 of the gate rests on -- the one
that catches a multi-step posting nobody has measured. It has a silent ceiling.

Measured, one edit apart, same page, same button count:

```
Next after 41 fillers (index 41)  -> advance_names: []        MISSED
Next first, then 41 fillers       -> advance_names: ['next']  SEEN
```

**The number matters.** The single 2026-08-24 observation was recorded as
**43 buttons**. Whether all 43 sat inside the dialog was never written down --
that count is page-level -- so this is NOT a claim that the live flow trips the
cap. It is the observation that the only button count anybody recorded is
ABOVE the ceiling, which puts the margin somewhere between three buttons and
unknown.

Pinned by `test_an_advance_control_past_the_fortieth_button_is_not_seen`, which
asserts BOTH halves so it cannot be satisfied by a reader that sees nothing.
Not fixed -- raising or removing the bound is a production change. What would
settle it cheaply: a recount of the live modal that records how many buttons
are INSIDE the dialog rather than on the page.

## ESCALATION 3 -- two different failures produce one byte-identical message

Your test 3 asked that "a rendered dialog with zero hooked buttons" be
distinguishable from "the modal never rendered", and that the two must not
produce one message. Measured:

```
dialog present, hook renamed:
  modal_present=True,  why="expected exactly one ... and found 0. ..."
no dialog, hook renamed:
  modal_present=False, why="expected exactly one ... and found 0. ..."
```

**The `why` sentences are byte-identical.** The reader writes `why` from the
count alone, and the count really is 0 in both. The distinction exists, but it
lives ONLY in `modal_present`.

It is survivable today only because `_apply_submit_gate` tests `modal_present`
FIRST and writes its own "the apply modal never rendered" message before it
ever consults the reader's `why`. So the SYSTEM separates them and the READER
does not. Anything else that ever reads `why` alone will not be able to tell a
non-hydrated page from a renamed hook -- which are different problems wanting
different responses from a human.

`test_a_dialog_with_no_hooked_control_and_no_dialog_at_all_read_differently`
asserts the distinction in the field that carries it AND asserts the sentences
are equal, so that making them differ is a deliberate act with a visible test
to delete, not a surprise.

## Other things that surprised me (reported, not acted on)

1. **`PERFORMABLE`'s docstring contradicts `PERFORMABLE`.** The comment block
   above it (writes.py ~1917) still says "``apply_job`` is not here and is the
   one whose absence needs saying plainly", and then lists reasons -- while the
   set on the next line is
   `{"save_job", "unsave_job", "unfollow_company", "apply_job"}`. Stale since
   apply shipped on 2026-08-25.
2. **Dead refusal block.** `_refuse_unperformable` returns early on
   `spec.action in PERFORMABLE`, so the entire `if spec.action == "apply_job":`
   refusal at writes.py ~2015 -- about 25 lines explaining that apply is not
   performed and pointing at `scripts/_probe_apply_flow.py` -- is unreachable.
   It is also the second place that now says something the code no longer does.
3. **The advance scan does not exclude the submit control itself.** It walks
   every button in the dialog including the hooked one, so a submit named
   "Review and submit" would be collected as its own advance control and refuse
   itself. That fails SAFE, so I have not treated it as a defect -- but it means
   the accessible name of the submit is load-bearing in a second, undocumented
   way.
4. The fixture picked up two existing repo-wide hygiene sweeps automatically
   (session material, opaque LinkedIn ids) and passes both.

## What this slice does and does not establish

DOES: `dom.read_apply_modal` is executed, over a real parsed DOM, across the
measured shape and eight derived departures from it; every branch reachable
without a production change has been reached, including the previously dead
`count != 1`; and 10 mutations of the production code each turn a specific test
red.

DOES NOT: say anything whatever about what a live LinkedIn apply modal looks
like. The input is DERIVED from six remembered numbers from one posting on one
day, and the capture no longer exists. It also does not show that apply works
end to end -- it shows the opposite, that `perform` cannot get there.
