# Slice: a `checked` reading on the surface census

Date 2026-08-31. Branch `master`, base HEAD `4f45781`, tree clean at start.
Offline only -- no `mcp__linkedin__*` tool was called, no browser reached
LinkedIn, `_state/` untouched. **Nothing committed, nothing staged.**

Files changed (three, exactly the three the brief named, plus nothing else):

    linkedin_server/dom.py         +80 / -26 lines net    CENSUS_JS + read_surface_census
    linkedin_server/shape.py       +34                    census_aggregate
    tests/test_surface_census.py   +989                   sections 8f / 8g / 8h / 8i

Suite: **2156 passed** in 722s (baseline 2132; +24 tests, zero failures).
`tests/test_surface_census.py` alone: 103 -> 127 passed.

---

## 0. READ THIS FIRST -- one measured contradiction with the brief

**The brief's fixture rows 4 and 5 specified a `div[role="checkbox"]`. That
element is not censused at all**, so as written those two rows would have
produced ZERO census records and T3 and T5 would have had nothing to assert
on.

`CENSUS_CONTROL_SELECTOR` is:

    button, a[href], input, textarea, select,
    [role="button"], [role="link"], [role="textbox"], [role="combobox"],
    [contenteditable]:not([contenteditable="false"])

There is no `[role="checkbox"]` and no `[role="radio"]` arm. Measured, not
read off the string -- six elements on one page, four rows returned:

    div[role=checkbox]  aria-checked=true    -> NO ROW
    div[role=radio]     aria-checked=true    -> NO ROW
    button[role=checkbox] aria-checked=true  -> checked true    source aria-checked
    div[role=button]    aria-checked=mixed   -> checked "mixed"  source aria-checked
    button[role=switch] aria-checked=true    -> checked true    source aria-checked
    input[type=radio] checked                -> checked true    source native

**What I did instead of stopping:** the ARIA route is exercised on two
elements the selector DOES admit -- `button[role="switch"] aria-checked="true"`
and `button[role="checkbox"] aria-checked="mixed"`. Both are well-formed ARIA
and both reach the same `checkedOf` branch, so every assertion the brief asked
for is made. I did **not** widen the selector: that would change the control
population of every fixture and every census already written into `_audit/`,
which is not my slice.

**What I added instead of only reporting it:** the invisible
`div[role="checkbox"]` is IN the fixture, last in document order so it cannot
move a `ROW_` index, and
`test_a_div_built_as_a_checkbox_is_not_censused_at_all` pins the limit -- the
fixture has eleven elements and the census returns ten rows.

**Why this may matter to you rather than only to me.** The live dark-mode
radios are safe: `_audit/2026-08-31-linkedin-finish.md` lines 189-191 record
them as `tag input`, so they take the NATIVE branch and this slice reads them.
But any future surface whose controls are `div[role="radio"]` or
`div[role="checkbox"]` is invisible to the census entirely -- not "reports no
checked state", but **produces no row at all**. That is a selector decision,
not a `checked` decision, and it is yours to rule on.

---

## 1. What was built

### 1.1 `CENSUS_JS` -- `checkedOf`, beside `containerOf`

Verbatim as briefed, native branch first, with the ordering reason written
into the comment beside it (that it is deliberately the OPPOSITE of `nameOf`,
so a later reader finds a decision rather than an inconsistency to "fix").
Two record fields appended LAST, after `container`; nothing existing was
renamed, removed or reordered.

`readonly.JS_MUTATION_TOKENS` scan: clean. `el.checked` and
`getAttribute('aria-checked')` are reads.
`test_the_census_script_carries_no_mutating_token`,
`test_that_scan_can_fail_on_this_script`, `test_the_script_never_scrolls` and
the whole of `tests/test_readonly.py` -- 147 passed.

### 1.2 `read_surface_census` -- both fields into the enumerating literal

    "checked": control.get("checked"),
    "checked_source": str(control.get("checked_source") or "none"),

`checked` passes through UNSHAPED and UNCOERCED; `checked_source` takes the
same `str(... or "none")` default `container` uses.

### 1.3 `census_aggregate` -- both fields into the merge key, 8 -> 10

Appended after `disabled`, emitted on each output row beside `disabled`. The
docstring now enumerates the ten fields by name rather than counting them, and
carries the justification: `checked` is a control STATE, the same axis as
`disabled` and `aria_expanded` which were already in the key, where
`container` is a PLACE.

`census_aggregate`'s rows go straight into the tool result
(`server.py:1924`), so the key change IS the plumbing to tool output. That is
pinned by `test_the_result_has_the_shape_a_caller_is_promised`, which **went
red on this edit** and now asserts the twelve-key row set.

---

## 2. T1-T7, each SHOWN FAILING. Exact assertion text, mutation reverted.

Every mutation below was applied to the real source file, run, and reverted in
a `finally`; the revert was verified byte-for-byte. `git status` at the end of
this document confirms only the three intended files are modified.

### T1 -- the checked radio reads true, the other two read false

Mutation: delete the checked call site from `CENSUS_JS`
(`dom.py`), so no record carries a `checked` key.

    rows = await _checked_form_rows(census_over)
    group = [rows[index] for index in ROW_THEME_GROUP]
>   assert [row["checked"] for row in group] == [False, True, False]
E   assert [None, None, None] == [False, True, False]
E
E     At index 0 diff: None != False
E     Use -v to get more diff

    tests\test_surface_census.py:2408: AssertionError

### T2 -- the text input reads `None`, NOT `False` (the type gate)

Mutation: drop the `type === 'radio' || type === 'checkbox'` gate, so
`el.checked` is read on every input.

    rows = await _checked_form_rows(census_over)
    text = rows[ROW_TEXT_INPUT]
    assert text["tag"] == "input"
    assert text["shape"] == "Headline", (...)
>   assert text["checked"] is None
E   assert False is None

    tests\test_surface_census.py:2447: AssertionError

**`assert False is None` is the whole argument for the gate**: the `Headline`
text field, reported as a checkable control that is switched off. Across the
19 committed fixtures the ungated read does this to **8 controls** (37 non-null
readings instead of 29), every one of them an `input` that cannot be checked.

### T3 -- `checked_source` reports the three routes distinctly

Mutation: collapse both routes to a single source string `'checked'`.

    rows = await _checked_form_rows(census_over)
>   assert rows[ROW_RADIO_ON]["checked_source"] == "native"
E   AssertionError: assert 'checked' == 'native'
E
E     - native
E     + checked

    tests\test_surface_census.py:2461: AssertionError

### T4 -- the conflict row reads true, with source native

Mutation: try ARIA first -- the native branch stands down wherever an
`aria-checked` exists (`if (tag === 'input' && !attrOf(el, 'aria-checked').trim())`).

    rows = await _checked_form_rows(census_over)
    row = rows[ROW_NATIVE_BEATS_ARIA]
>   assert row["checked"] is True
E   assert False is True

    tests\test_surface_census.py:2479: AssertionError

A natively checked radio, read as OFF off a stale attribute. That is the
reading the native-first order exists to prevent.

### T5 -- `mixed` survives as the string and is not coerced

Mutation: `bool()` the value in `read_surface_census`.

    rows = await _checked_form_rows(census_over)
    row = rows[ROW_ARIA_MIXED]
>   assert row["checked"] == "mixed"
E   AssertionError: assert True == 'mixed'

    tests\test_surface_census.py:2501: AssertionError

A tri-state control reported as fully on.

### T6 -- three same-shaped radios do not merge into one row

Mutation: `checked` no longer discriminates in the merge key (the slot made
constant, so the tuple stays ten long and the row emit still indexes).

    rows = await _merge_fixture_rows(census_over)
    merged, _hrefs = shape.census_aggregate(rows)
>   assert len(merged) == 2, merged
E   AssertionError: [{'shape': 'Theme choice', 'count': 3, 'tag': 'input', 'role': None, ...}]
E   assert 1 == 2
E    +  where 1 = len([{'shape': 'Theme choice', 'count': 3, 'tag': 'input', 'role': None, ...}])

    tests\test_surface_census.py:2812: AssertionError

**One row of count 3** -- three radios of which exactly one is on, reported as
"three identical radios". That is the dark-mode page, and it is what the key
change prevents.

> First attempt at this mutation deleted the key line outright, which made the
> tuple nine long and failed with an `IndexError` inside the row emit -- red,
> but red for the wrong reason. Re-run with the constant-slot mutation, which
> isolates the merge behaviour. Recorded because the first failure text would
> have been misleading evidence.

### T7 -- `read_surface_census` passes `checked` through untouched

Shown failing TWICE, because the claim has two ways of being false.

Mutation A: drop the `checked` key from the reader's enumerating dict literal.

    raw, shaped = await census_over(CHECKED_FORM_HTML, work)
    before = [row["checked"] for row in raw["controls"]]
>   after = [row["checked"] for row in shaped["controls"]]
             ^^^^^^^^^^^^^^
E   KeyError: 'checked'

    tests\test_surface_census.py:2557: KeyError

Mutation B: `bool()` it in the reader -- the value-level failure.

    before = [row["checked"] for row in raw["controls"]]
    after = [row["checked"] for row in shaped["controls"]]
>   assert before == after
E   assert [False, True,...se, None, ...] == [False, True,...e, False, ...]
E
E     At index 5 diff: None != False
E     Use -v to get more diff

    tests\test_surface_census.py:2558: AssertionError

Index 5 is the text input: `None` becoming `False` is the conflation, caught
at the level a caller actually receives.

---

## 3. THE FIXTURE SWEEP -- measured over all 19 committed fixtures

Run with the real script and with one whose checked call site is deleted,
isolated browser context per fixture, `window.innerWidth` asserted == 1280 on
every measurement.

| measurement | value |
|---|---|
| fixtures read | 19 |
| **total controls read** | **537** (unchanged -- `FIXTURE_CONTROLS`) |
| controls with non-null `checked` | **29** |
| `checked_source` tally | `native` 29, `none` 508, `aria-checked` 0 |
| **pre-existing fields that moved** | **ZERO**, on every control of every fixture (counts block compared too) |
| aggregate rows that change | **2 fixtures, +1 row each** |
| **readable shapes lost to `<redacted>`** | **NONE -- in any fixture** |

### 3.1 Where the 29 readings are (document order, pinned as `FIXTURE_CHECKED`)

    job_detail.html                     1   (input, False, native)
    job_detail_following_hydrated.html  1   (input, False, native)
    job_detail_hydrated.html            1   (input, False, native)
    jobs_tracker_empty.html            12   ON,OFF*5,ON,OFF*5
    jobs_tracker_row.html              14   ON,ON,OFF*4,ON,ON,OFF*6

### 3.2 The two aggregate rows that change -- shape, count, and what happened

    jobs_tracker_empty.html   10 rows -> 11
      before: <opaque>  count 8   (input, label-for)
      after:  <opaque>  count 6  checked False  native
              <opaque>  count 2  checked True   native

    jobs_tracker_row.html     14 rows -> 15
      before: <opaque>  count 8   (input, label-for)
      after:  <opaque>  count 4  checked True   native
              <opaque>  count 4  checked False  native

**This is the capability, on a real committed capture.** Before the key
change, one row said the job tracker carries eight indistinguishable filter
checkboxes. After it, two rows say how many of them are on. No other row in
any fixture changes shape or count.

### 3.3 The redaction hazard -- checked, and absent

The hazard that kept `container` out of the key is that a split drops a row to
`count == 1`, where `census_redact_rare` blanks capitalised runs. Checked per
fixture as `readable(before) - readable(after)`, over all 19: **empty
everywhere.** The shape that splits in both tracker files is `<opaque>`, which
carries no name to lose, and the two count-1 rows produced elsewhere carry
sentence-case labels the cap does not match.

**No escalation was needed on this point.** Had any readable shape gone
`<redacted>` I would have stopped and asked you to rule.

### 3.4 The sweep is pinned, with a companion that can detect movement

`test_no_committed_fixture_moves_a_pre_existing_field_under_checked`,
`test_what_the_checked_field_reads_across_the_repo_is_pinned` and
`test_the_key_split_is_pinned_and_costs_no_readable_shape` pin the numbers.
`test_that_checked_sweep_can_detect_movement` is the control and it makes
three separate claims falsifiable, on a COMMITTED fixture:

1. the comparator is silent for the checked derivation and reports **12** rows
   for the label derivation on `jobs_tracker_empty.html`;
2. the count of 29 is a measurement OF THE TYPE GATE -- the ungated derivation
   reads **37** across the same directory, a gap of exactly 8;
3. the split detector can see a split -- it reports
   `{("Theme choice", 3): {True: 1, False: 2}}` on the merge fixture.

---

## 4. Tests added (24), and the two fixtures

Invented markup lives in the module, not `tests/fixtures/`, following the
`LABEL_FORM_HTML` precedent and its reason. No slug, no urn, no id shape, no
phone-shaped digit run; ASCII throughout;
`tests/test_no_committed_identity.py` passes.

**`CHECKED_FORM_HTML`** -- ten censused controls plus one deliberately
invisible element:

    0,1,2  radio group of three, exactly one checked, each with <label for>
    3      checkbox, checked
    4      checkbox, unchecked
    5      text input                      <- the type gate
    6      button[role=switch] aria-checked=true      <- ARIA route
    7      button[role=checkbox] aria-checked=mixed
    8      radio checked + aria-checked="false"       <- the conflict
    9      button, no checked anything
    --     div[role=checkbox] aria-checked=true       <- NOT CENSUSED (0 rows)

The three radio labels echo the strings measured live on the dark-mode page so
the fixture's purpose is legible; the comment says plainly that nothing else
in it was served by LinkedIn.

**`CHECKED_MERGE_HTML`** -- three radios sharing one accessible name, differing
only in state. Two rows out with the state in the key, one row of count 3
without.

Sections added: **8f** (the readings, all taken through
`read_surface_census`), **8g** (three derivations, each shown getting a
different reading wrong -- call site, type gate, ARIA-first), **8h** (the merge
key), **8i** (the 19-fixture sweep).

---

## 5. THE COUNT ROT -- every stale number corrected

`grep -rn "eight" linkedin_server/ tests/` found five sites referring to this
key or this literal. All five corrected:

| site | was | now |
|---|---|---|
| `dom.py` CENSUS_JS comment | "ENUMERATES eight keys" / "eight-field tuple" | "NAMES TEN KEYS" / "TEN-FIELD tuple" |
| `dom.py` reader comment | "eight named keys carry eight fields and silently drop a ninth" | the keys are NAMED; ten are named now |
| `test_surface_census.py` 8c header | "ENUMERATES eight keys, so a ninth ... never reaches a caller" | past tense; gap closed; ten keys |
| `test_surface_census.py` 8d header | "one of the eight already there" | "eight of them when this was measured, ten as of the `checked` edit" |
| `test_surface_census.py:2041` | present tense "shapes ... eight named keys" | past tense "WAS shaping ... eight named keys" |

Plus one that is the same defect wearing different words:
`test_controls_differing_only_in_state_stay_separate_rows` still opened with
**"The merge key is the whole record, not the name."** -- the exact sentence
`shape.py` was corrected for on 2026-08-31. Rewritten to say it is a NAMED SET
OF FIELDS and that the old claim is what let two added fields be dropped in
silence.

### 5.1 A DECISION YOU SHOULD REVIEW -- I rewrote a paragraph, not just a number

The `dom.py` CENSUS_JS block's paragraph was headed **"WHAT IT DOES NOT YET
REACH"** and said the descriptor "stops at this script's own return value and
no tool output carries it yet". That was already FALSE before I touched
anything -- `container` reaches the reader and the tool today. Bumping only
the number inside it would have left a paragraph whose thesis contradicts the
code, which is the defect this section exists to kill.

So I rewrote it as **"WHERE A NEW FIELD GOES"**: it quotes what it used to say,
records that the mechanism it describes is permanent even though the gap it
described is closed, states the two counts as ten and ten, and names the two
counts as the thing to re-check when the next field is added. The same
treatment was applied to the 8c header, which additionally pointed at
`test_the_shaped_reader_still_drops_the_container_descriptor` -- a test that no
longer exists.

This is more than "correct every count you change". Flagging it because it is
prose I rewrote on my own judgement rather than a number you asked me to move.

---

## 6. Completeness claims made checkable

Per the constraint that no completeness claim ships without a test or as its
own enumeration:

* "THE KEY IS THESE TEN" -- written out by name in the `census_aggregate`
  docstring, and every one of the ten comes back on the row, pinned by
  `test_the_result_has_the_shape_a_caller_is_promised`.
* "THREE values" for `checked_source` -- `CHECKED_SOURCES` is the enumeration
  itself; `test_the_source_says_where_each_reading_came_from` asserts the
  fixture produces exactly that set, and the sweep asserts every source in all
  19 fixtures is a member of it.
* "NOT ONE readable shape lost" -- computed per fixture and asserted, not
  described.
* "ZERO pre-existing fields move" -- asserted with a comparator shown catching
  12 movers on the same file.

---

## 7. State at hand-off

    $ git status --porcelain
     M linkedin_server/dom.py
     M linkedin_server/shape.py
     M tests/test_surface_census.py

Nothing staged, nothing committed, nothing pushed, `_state/` untouched, no
`mcp__linkedin__*` call made. Line endings verified unchanged (LF on disk
before and after, matching files I never wrote). All three files ASCII.

    $ venv\Scripts\python.exe -m pytest -q
    2156 passed in 722.05s (0:12:02)
