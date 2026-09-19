# The send control is repaired, and it answers neither half

**Wave:** send-control - 2026-09-19
**File:** `tests/test_click_is_not_its_own_evidence.py`
**Test:** `test_a_click_that_does_commit_reaches_the_body_and_the_send`
**Red from:** 2026-09-05 19:16 (`9503723`) to 2026-09-19. Bisected, not inferred.

---

## 1. What was actually broken, and it was neither half

The red was reproduced before anything was edited:

```
E   AssertionError: {'proceeded': False,
                     'refused_condition': '3_needle_does_not_match', ...}
E   assert False is True
tests\test_click_is_not_its_own_evidence.py:372
```

`3_needle_does_not_match` is the gate's THIRD refusal branch. It is reached
only after `total == 1` - **a recipient WAS committed.** The chip existed and
the matcher declined its label. So the failure was never "the flow stopped
working", which is the one thing this control exists to detect.

The mechanism, end to end:

- the double's committing composer appends a chip whose `aria-label` is the
  remove word plus **the pressed row's text content**;
- the row is a name span beside a degree span with nothing between them, so
  that text runs the name onto the degree badge;
- `9503723` tightened `dom.SELECTED_RECIPIENT_JS` from `indexOf` to a
  word-bounded match, and its own commit message states the intent verbatim:
  *"a label running a name onto a connection degree must refuse rather than
  match"*;
- so the shipped matcher refused the double's chip, exactly as designed, and
  the positive control for the only tool in this package that reaches another
  person went red and shipped red.

**The commit that tightened the safety gate broke the gate's own positive
control, and the break was the tightening working.**

A second fact, previously unreconciled: this repository already holds **two
doubles of the same never-observed surface, in two files, with different
label shapes.** `tests/test_send_message_gate.py`'s static `_chip` draws the
name alone - bounded on both sides - and stayed green through `9503723`. Only
the click-produced chip in this file carries the run-on shape. The tightening
did not create the divergence; it made it load-bearing.

## 2. What I refused to decide

**I did not choose a separator to turn the test green.**

Whether LinkedIn draws the chip label with the degree run onto the name or
separated from it **has never been read.** `dom.RECIPIENT_CHIP_SELECTORS` has
never matched anything on any real page, on any branch, and both this file and
`tests/test_the_needle_is_matched_as_a_bare_substring.py` say so at length.
Drawing the label the way the matcher likes would have ruled on an unread
surface from inside a fixture, and smuggled that ruling in as a test fix - on
a gate whose docstring says refusing a legitimate recipient *"is the ruling
and not a regression"*.

Three further things this repair does not claim, deliberately:

1. that either shape is the live one;
2. that the word-boundary matcher is the RIGHT relation for the chip rail
   (the audit of 2026-09-03 measured every anchored matcher dead on the
   NEIGHBOURING surface, and that is a different surface);
3. that the accepted shape's green run is evidence about LinkedIn. It is
   evidence about `perform`.

## 3. The repair

The separator is made **the variable**, which is the same variable `_row`
already names further down the same file for the listbox. One builder,
`_committing(separator)`, produces both pages; the control runs **both** and
asserts the verdict is shape-determined.

| shape | chips committed | typeahead gate | recipient gate | body typed | send pressed |
|---|---|---|---|---|---|
| separated (`" "`) | 1 | proceeds, 1 press | **proceeds**, matches 1 | yes | yes |
| run-together (`""`) | 1 | proceeds, 1 press | refuses `3_needle_does_not_match`, matches 0 | no | no |

Three claims, and the third is the one that needed the pair:

1. **The pipeline is alive.** On the accepted shape the run reaches the body
   fill and the send press - the duty this control has always had. An
   unconditional refuser fails it.
2. **The refusal is a matcher verdict, not an absent chip.** `total` is 1 in
   both rows. This is the separation `9503723`'s own four-case table was built
   to make; without it a refusal proves only that the fixture stopped drawing.
3. **Nothing upstream moved.** Both runs clear the typeahead gate with exactly
   one press, so the difference is downstream of the click and attributable to
   the label's shape alone.

**The pair is proved to be a pair.** A module-level assertion collapses the
inserted separator out of the second page and requires it to equal the first
exactly - and if the anchor ever stops matching, `replace` becomes a no-op and
the two strings stay different, so it fails loudly instead of degrading into a
comparison of two pages that drifted apart.

## 4. The control shown failing - three ways

A check that cannot fail certifies nothing, and "two verdicts differ" is the
easiest kind of assertion to hold green by accident.

**(a) The shipped matcher against itself, minus one clause.** New test
`test_the_shape_determination_is_one_clause_and_here_it_is_removed` reads both
rails twice: once with `dom.SELECTED_RECIPIENT_JS`, once with that same source
mutated - the word-boundary clause removed, which is the matcher this gate
actually had until 2026-09-05. Not a rewrite: the source is imported and one
clause taken out, because a hand-written loose matcher would be a second
implementation, and the anchor is asserted so a moved target fails instead of
silently returning the original.

| shape | chips | shipped matches | loosened matches |
|---|---|---|---|
| separated | 1 | 1 | 1 |
| run-together | 1 | **0** | 1 |

The only zero in the table is produced by one clause, and removing it removes
the zero. That table is also the whole two-week regression in four numbers.

**(b) The repaired control against a dead flow.** `_recipient_gate`
monkeypatched to refuse unconditionally (scratch plugin, not committed):

```
>   assert accepted["recipient_gate"]["observed"]["total"] == 1
E   AssertionError: {'per_selector': {}, 'total': 0, 'matches': 0, ...}
E   assert 0 == 1
1 failed
```

**(c) Both controls against a reverted ruling.** The boundary clause
monkeypatched back out of the SHIPPED constant:

```
E   AssertionError: the word-boundary clause this control mutates is no longer
    spelled the way it was on 2026-09-05. Re-point the anchor; do not delete
    this control, because without it the discrimination asserted above has
    never been shown able to fail.
2 failed
```

## 5. Measurement conditions

Headless chromium, synthetic markup, `set_content` at a fixed viewport that is
re-asserted on every read. **No LinkedIn, no CDP, no profile, no session, no
write fired.** The shipped matcher and the shipped option selector are
IMPORTED and driven, never reimplemented. Every comparison runs inside the
page and only integers come back, so no accessible name entered the process.

## 6. Result

```
tests/test_click_is_not_its_own_evidence.py
30 passed, 1 xfailed in 41.28s
```

The xfail is the pre-existing strict marker on the 2026-09-03 known defect
(`test_a_run_that_pressed_no_send_should_report_not_performed`), untouched.

**Attribution: 0.** No `Co-Authored-By`, no `Claude-Session`, no "Generated
with". Verified against the commit and the index, not against a claim.

## 7. What is still open, and who can close it

Which shape LinkedIn draws on the chip rail. It cannot be closed from here -
it needs a chip observed. The refusal's own `per_selector` counts are the
instrument for reading it, and they come back from the first supervised live
run without any accessible name being read. Until then the suite asserts a
RELATION between two doubles and privileges neither, which is the most that
can be said honestly.
