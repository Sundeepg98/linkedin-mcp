# `_SANITISERS` holds two kinds of claim and has one certifier

Filed 2026-09-19 12:45 by the box. **A design brief, not an implementation.**
It is filed rather than built because the gap bit twice in ten minutes and a
safety mechanism written against a closing deadline is how the defects in this
file got here.

---

## THE EVENT

`tests/test_a_sanitiser_earns_its_entry.py` **refused** `_why_refused`, an entry
its author ran the adversarial table against **before** adding the row, per that
file's documented order. It passed the needle half -- no input survives any
branch -- and failed `MUST_DISCRIMINATE`, because the urls tested were all
ADMITTED and the function correctly returned one verdict for all of them.

**The author gave the entry back** rather than reshape the function or widen the
table, on the grounds that *"both would be getting a green rather than earning
one."* **That refusal is correct and stands.**

Ten minutes later the same gap appeared on a different function found by a
different instrument: `_landing_class` in
`scripts/_probe_creator_content_analytics.py` returns a closed enumerated
alphabet -- `AUTH-WALL`, `target`, `REDIRECTED-WITHIN-ANALYTICS`, every return a
string constant -- and its value reaching a `print` is an undeclared taint site
with **no honest route to declaration.**

**Two functions, two instruments, ten minutes. That is a kind, not a case.**

---

## THE DIAGNOSIS

`_SANITISERS` holds two different kinds of function, and the certifier
understands one of them.

```
SHAPERS            _shape_of, _redact, _relation
                   input -> a SHAPED OUTPUT derived from it
                   SAFE IFF no input survives AND IT DISCRIMINATES

VERDICT FUNCTIONS  _why_refused, _landing_class
                   input -> ONE OF A CLOSED, ENUMERATED SET
                   SAFE IFF no input survives AND THE ALPHABET IS CLOSED
```

### AND THE TEST IS NOT MERELY WRONG FOR THE SECOND KIND -- IT IS INVERTED

> **Apply `MUST_DISCRIMINATE` to a verdict function and satisfying it would make
> the function WORSE.**

The more a verdict varies with its input, the more it tells you about that
input. **For a verdict function, returning one value for many inputs is the
property you want**, and the shaper test scores that property as a defect. A
verdict function that discriminated per-input would be leaking, and the table
would pass it.

**So widening the table is not a loosening. It is a certifier that rewards the
hazard.** That is why the refusal must stand and why nobody may "just add an
arm".

---

## WHAT TO BUILD

**Two lists, two certifiers.** Not one list with a kind flag -- the guard
matches `func.id in _SANITISERS`, so a single list means a single trust
decision, and the whole lesson of the three namesake recurrences is that a name
in that list is trusted corpus-wide on spelling alone.

### `_SHAPERS` -- unchanged

Keeps the present table verbatim, including `MUST_DISCRIMINATE`. **No entry
moves and no contract changes.** Whatever is built must leave every existing
entry certified by the test that certified it.

### `_VERDICTS` -- new, and its certifier is a different proof

A verdict function earns its entry by showing, **off the AST rather than by
reading**:

1. **Every `return` in the function is a string constant.** No f-string, no
   concatenation, no `%`, no `.format`, no name. This is the needle half and it
   is stronger than the shaper's, not weaker -- a shaper may derive; a verdict
   may not.
2. **The set of those constants is the declared alphabet**, enumerated in the
   entry, and the entry goes RED if the function gains or loses one.
3. **The function is shown returning at least two DIFFERENT members** over the
   corpus -- the control proving it can speak, without which the whole thing is
   satisfied by `return "x"`.

**Note what is deliberately absent: no discrimination requirement.** Many inputs
mapping to one verdict is the point.

### AND AN ENROLMENT ROW EITHER WAY

Both lists share `ENROLLED`'s discipline: `(filename, function name) -> arity`,
**a claim made by the function's author and by nobody else.** That rule has now
caught the same event four times (`_shape_of` -> `_redact` -> `_relation` ->
`_why_refused`) and must not be relaxed for the new list.

---

## THE TWO RULES ALREADY EARNED, TO BE CARRIED INTO IT

**WHEN A NAMESAKE IS NOT A COPY, THE REPAIR IS A RENAME.** Enrolment ASSERTS a
contract is safe; a rename WITHDRAWS the claim to be trusted. The second
requires knowing nothing about the contract, which is exactly why it is
available to someone who did not write it -- and why an absent owner must never
leave a false trust claim standing.

**A GUARD SILENCED BY A NAME STOPS CHECKING EVERYTHING DOWNSTREAM OF IT.**
Measured: renaming the namesake turned a *different* test red, exposing a
navigation-derived value reaching a `print` that had been invisible for as long
as the name held. **Enrolling it would have made the red go away while leaving
the print unexamined.** That is the argument for rename-over-enrolment, measured
rather than reasoned.

---

## THE INTERIM STATE, WHICH IS HONEST AND SHOULD NOT BE TIDIED

Until this exists there is **no route to admit a verdict-shaped sanitiser.** The
correct interim posture, already taken for `_why_refused`:

* no entry in either list,
* no print of the verdict at the call site,
* the classification left in the docstring **where it was measured**.

**Do not re-add a name to turn a red green.** That is the enrolment argument
wearing a rename's clothes, and its cost is now measured: it conceals whatever
sits downstream.

---

## AMENDMENT, SAME DAY: A THIRD INSTANCE, AND IT IS THE CLEAREST OF THE THREE

Measured 12:43 by the box, on the orphaned red two waves had each reported as
*"not mine"*: `scripts/_probe_add_section_menu.py` carries **two** undeclared
taint sites. Owner `edd24f8`, a commit rather than a live agent.

```
287  print(f"  anchor {index}: rel={rel:20s} haspopup={haspopup} ...
                role={role} EVIDENCED-DISCLOSURE={pressable}")
310  print(f"    boundary: is_read_url={admitted}  path_depth={depth}
                forbidden_tokens_present={trips}")
```

### LINE 310 ALREADY COMPLIES WITH THE GUARD'S OWN REMEDY

The failure message says: *"If you ADDED one, emit a RELATION or a count
instead."* **Line 310 emits nothing else.** `admitted` is the boolean returned
by `is_read_url`; `depth` is an integer; `trips` is a presence flag. There is no
browser-chosen string anywhere in it.

> **The guard flags a line that already satisfies the remedy the guard
> prescribes.**

It is not wrong to flag it -- it **tracks the NAME**, and it cannot know that
`is_read_url` returns a boolean. That is the identical mechanism as
`_why_refused` and `_landing_class`: **a function whose output alphabet is
closed, with no way to say so.**

### SO THE COUNT IS THREE, AND THEY ARRIVED BY THREE DIFFERENT ROUTES

    _why_refused      refused by the adversarial table when its author enrolled it
    _landing_class    exposed by a rename withdrawing a false trust claim
    is_read_url       standing in an orphaned red two waves declined to own

**Three functions, three instruments, one missing certifier.** The third is the
most persuasive because **nobody was looking for it** -- it was sitting in a red
that had been triaged twice as somebody else's problem, and it turns out to be
the same problem as the other two.

### WHAT THIS CHANGES ABOUT PRIORITY, AND WHAT IT DOES NOT

**It changes the priority:** this is not a tidiness gap. Three real sites are
currently unrepresentable, and the only way to green two of them today would be
to declare safe code as a known violation or to re-add a name -- **both of which
record something false.**

**It does not change the decision to file rather than build.** Line 287 is the
mixed case and needs judgement: `index` is a count and `controls` is already
reduced to `yes`/`no`, but `role` is an ARIA attribute read off the page, and
*"ARIA roles are a closed set in the spec"* is a claim about the spec, not about
what a page may put there. **That distinction is the whole subject of this
brief, and settling it in the last quarter-hour of a session is how the defects
above got written.**

**FIRST WORK FOR WHOEVER PICKS THIS UP:** build `_VERDICTS` and its certifier as
specified, then re-run these three. Two should resolve without an exemption
entry. **The third, line 287's `role`, is a genuine open question and should be
ruled rather than assumed** -- it is the one place in this brief where the
closed-alphabet argument may not hold.

**CORRECTED BY:** `_audit/2026-09-19-verdict-certifier.md` -- built and re-run the same day: two of three do resolve, but they are `_landing_class` and `is_read_url`, because `_why_refused` is refused a second time by the new proof over its `%`-interpolated return; and `_landing_class` returns five verdicts, not the three counted above.
