# Slice: the census could not read a `<label>`

2026-08-31. `CENSUS_JS` resolved an accessible name through `aria-label`,
`aria-labelledby` and `title` and then fell back to the element's own text. It
never followed `<label for="...">` and never checked an ancestor `<label>`, so
every form field on every surface it had ever read came back
`name_source: "none"` with an empty shape. Fixed, with the two routes reported
separately as `label-for` and `label-ancestor`.

Two files changed, both owned by this slice, and the diff is almost pure
addition:

    linkedin_server/dom.py         76 added   0 removed
    tests/test_surface_census.py  461 added   1 removed

The one removed line is the file docstring's `Nothing here launches Chromium or
reaches LinkedIn.` -- replaced, not deleted, because section 8 now does launch a
local headless Chromium over invented markup. **No existing test body was
edited.** That is checkable rather than asserted: `git diff -U0` on the test
file reports exactly one deleted line and it is that docstring line.

---

## 1. THE RED, verbatim

Eleven tests were written first and run against unmodified `dom.py`.

```
$ venv\Scripts\python.exe -m pytest -q tests/test_surface_census.py \
      -k "label or nothing_is_still_reported or redaction_check or beats or movement"

____________ test_a_sibling_label_for_names_the_input_it_points_at ____________

    async def test_a_sibling_label_for_names_the_input_it_points_at(census_over):
        row = (await _label_form_rows(census_over))[ROW_LABEL_FOR]
>       assert row["name_source"] == "label-for"
E       AssertionError: assert 'none' == 'label-for'
E
E         - label-for
E         + none

___________________ test_a_label_wrapping_an_input_names_it ___________________

    async def test_a_label_wrapping_an_input_names_it(census_over):
        row = (await _label_form_rows(census_over))[ROW_LABEL_ANCESTOR]
>       assert row["name_source"] == "label-ancestor"
E       AssertionError: assert 'none' == 'label-ancestor'
E
E         - label-ancestor
E         + none

______________ test_the_two_label_routes_are_reported_separately ______________

        rows = await _label_form_rows(census_over)
>       assert (
            rows[ROW_LABEL_FOR]["name_source"]
            != rows[ROW_LABEL_ANCESTOR]["name_source"]
        )
E       AssertionError: assert 'none' != 'none'

____ test_that_redaction_check_would_notice_a_reader_that_stopped_shaping _____

        raw = await census_over(LABEL_FORM_HTML, work)
        name = raw["controls"][ROW_LABEL_CARRYING_A_NAME]["name"]
>       assert "Jane Doe" in name
E       AssertionError: assert 'Jane Doe' in ''

7 failed, 4 passed, 72 deselected in 8.55s
```

Both halves of the brief's red criterion are in that output: `name_source` came
back `'none'` for (a) the sibling-labelled input and (b) the label-wrapped
input, and the raw name came back `''` -- the last block is the empty string
shown directly, since it asserts a substring is present in the raw name and the
raw name is empty.

The four that PASSED against unmodified `dom.py` were the two precedence tests
(`aria-label` and `title` already won, because there was nothing to beat), the
"named by nothing stays nothing" residue test, and one unrelated parametrised
case whose id contains the string `aria-label`. Two more failed on the derived-
script anchor, which did not exist yet.

## 2. The resolution chain as it now stands

In order, first non-empty wins:

| # | source | how it is read |
|---|--------|----------------|
| 1 | `aria-label`   | attribute |
| 2 | `aria-labelledby` | ids resolved through `getElementById`, texts joined |
| 3 | `title`        | attribute |
| 4 | **`label-for`**      | **NEW** -- a `<label>` in `el.labels` whose `for` equals the element's `id` |
| 5 | **`label-ancestor`** | **NEW** -- `el.closest('label')`, gated on `el.labels` |
| 6 | `text`         | the element's own `innerText` |
| 7 | `none`         | nothing found; name is `""` |

The two new routes report separately. They are not collapsed into one `label`
source: the whole value of `name_source` is that it says WHERE the string came
from, and a reader costing a capability can act on "labelled by a sibling" but
cannot act on "something labelled it".

**`el.labels`, not `document.querySelector` on an escaped id.** The brief left
this open and asked which and why. `.labels` was chosen for blast radius, not
for escaping:

* `.labels` exists only on the elements HTML lets a `<label>` name -- `input`,
  `button`, `select`, `textarea`, and the meter/output/progress family. An
  anchor or a `div[role="button"]` that happens to sit inside a label therefore
  **cannot** be renamed by one. A `querySelector` would have had to be told that
  rule; this way the browser holds it.
* It settles `<label for="other">` wrapping an unrelated input for free: HTML
  drops the implicit association when the wrapper points elsewhere, so `.labels`
  is empty and no name is invented.
* `CSS.escape` never enters the script.

The `for=` comparison is only used to CLASSIFY which of the two routes named a
control; association itself is the browser's answer, not a selector's.

**Placement is deliberately narrower than the accessible-name spec.** The spec
ranks a native `<label>` ABOVE `title`. Here `title` still wins. The constraint
is not correctness in the abstract -- it is that captures taken with the
three-route chain are already in the audit record, and a route that outranked an
existing one would rename controls inside them with nothing in the diff saying
so. Pinned by a test, so the deviation is reviewable rather than discovered.

## 3. Precedence evidence

`aria-label` still beats `<label for>`, and `title` still beats it too. Both are
asserted on fixture rows carrying BOTH attributes:

```
ROW_ARIA_BEATS_LABEL   <label for="c-pronouns">Pronouns</label>
                       <input id="c-pronouns" aria-label="Pronouns, choose one">
                       -> name_source "aria-label",  shape "Pronouns, choose one"

ROW_TITLE_BEATS_LABEL  <label for="c-industry">Industry</label>
                       <input id="c-industry" title="Industry, start typing">
                       -> name_source "title",       shape "Industry, start typing"
```

Shown failing under mutation -- see section 5.

## 4. Redaction evidence

The privacy rule did not move: a label-derived name goes through the same
`shape.census_shape` call in `read_surface_census` as an `aria-label`-derived
one, with no branch of its own. Driven with a person's name in a label, with
the curly apostrophe LinkedIn actually serves:

```
<label for="c-note">Reply to Jane Doe<U+2019>s message</label><input id="c-note">

raw   (page.evaluate on CENSUS_JS)   name = "Reply to Jane Doe<U+2019>s message"
tool  (dom.read_surface_census)      shape = "Reply to <member>'s message"
                                     "Jane Doe" not in json.dumps(row)
```

Both halves are asserted, and the raw read is the CONTROL: without it the
redaction assertion would pass equally against a script that returned nothing at
all.

Two further receipts that the shaping path really is shared. In the fixture
sweep below, twelve tracker filter labels shape to `<opaque>` -- the character
gate and the length limit firing on label text exactly as they fire on
`aria-label` text. And the footer language `<select>`'s old `text` name (36
languages in a dozen scripts) shaped to `<opaque>` before this edit and shapes
to `Select language` after it.

## 5. Mutation evidence

Each mutation was applied to `dom.py`, measured, and reverted from a byte copy
taken before the first one. `dom.py` is byte-identical to its pre-mutation state
afterwards, and the full four-file run at the end proves it.

**(a) Remove the fall-through.** Deleting the two-line call site:

```
8 failed, 76 passed in 9.99s
  test_a_sibling_label_for_names_the_input_it_points_at
  test_a_label_wrapping_an_input_names_it
  test_the_two_label_routes_are_reported_separately
  test_a_name_in_a_label_is_shaped_like_a_name_in_an_aria_label
  test_that_redaction_check_would_notice_a_reader_that_stopped_shaping
  test_no_committed_fixture_loses_a_readable_name_to_the_label_routes
  test_the_movement_the_label_routes_cause_is_pinned_file_by_file
  test_that_sweep_can_detect_movement
```

**(b) Make `label-for` win over `aria-label`.** Moving the same call site to the
top of `nameOf`:

```
_________________ test_aria_label_still_beats_a_label_element _________________
>       assert row["name_source"] == "aria-label"
E       AssertionError: assert 'label-for' == 'aria-label'
E         - aria-label
E         + label-for

___________________ test_title_still_beats_a_label_element ____________________
>       assert row["name_source"] == "title"
E       AssertionError: assert 'label-for' == 'title'
E         - title
E         + label-for

2 failed, 82 deselected in 3.81s
```

The precedence tests are the only guard on this. The committed-fixture sweep did
NOT go red under (b), because no committed fixture carries both an `aria-label`
and a `<label>` on one control -- worth knowing, and the reason the precedence
contract needs its own dedicated fixture row rather than leaning on the sweep.

## 6. DID ANY PREVIOUSLY-MEASURED CONTROL CHANGE ITS NAME OR name_source?

**Yes -- 28 of them, and this is the part of the slice that needs the lead's
eye.** It is not the class of change the brief said to stop on, but it is not
zero either, so here is the whole measurement rather than a verdict.

Both scripts -- the real one, and one with the label call site deleted -- were
run over **all 19 committed fixtures, 537 controls**. Twenty-eight controls
move:

| fixture | n | tag | before | after |
|---|---|---|---|---|
| `apply_modal_derived.html`   | 2  | `input`  | `none` | `label-for` |
| `jobs_tracker_empty.html`    | 12 | `input`  | `none` | `label-for` |
| `jobs_tracker_row.html`      | 12 | `input`  | `none` | `label-for` |
| `job_detail_following.html`  | 1  | `select` | `text` | `label-for` |
| `job_detail_shell.html`      | 1  | `select` | `text` | `label-for` |

The other 14 fixtures: zero movement.

**NOT ONE control whose published shape was a READABLE NAME changed.** Every
mover was previously either nameless or unreadable:

* The 26 `input` rows had published shape `""`. They ARE the blind spot. Two of
  them are the Easy Apply modal's `<label for="resume">Resume</label>` and
  `<label for="phone">Phone</label>` pairs -- which means the gap was already
  sitting in committed captures of the Easy Apply modal and the job tracker, not
  only on the profile editor that found it. That is an independent second
  confirmation of the defect and it was not in the brief.
* The 2 `select` rows are the same footer language picker. Its `text` name was
  the entire option list, 36 languages in a dozen scripts, which the shaper
  refused as `<opaque>`. Through the label route it reads `Select language`,
  which is what a screen reader says. `<opaque>` -> a real name.

So no census already written down is contradicted: a non-answer became an
answer. That is why this was completed rather than stopped. **The one judgement
call the lead may want to overturn** is the placement relative to the existing
`text` route, which the brief did not mention (the brief described the chain as
`aria-label` -> `aria-labelledby` -> `title`; there is a fourth fallback,
`text`, and the label routes had to go on one side of it):

* **As shipped** -- label routes ABOVE `text`. Reads the spec's answer for the
  language `<select>` (`Select language`), and costs the two `<opaque>` -> real
  name transitions above.
* **The alternative** -- label routes BELOW `text`. Provably renames nothing at
  all (an `<input>` has no `innerText`, so the 26 blind-spot rows still get
  named), at the price of leaving the two `<select>` rows reporting an option
  list the shaper throws away as `<opaque>`.

Flipping to the alternative is a two-line move of the call site and the pinned
sweep map in `tests/test_surface_census.py` would need its two `select` rows
dropped. Say the word and it is a five-minute change.

Both sweeps are now permanent instruments in the test file rather than notes
here:

* `test_no_committed_fixture_loses_a_readable_name_to_the_label_routes` -- the
  invariant that decides whether old captures are still true: no mover's BEFORE
  shape may be a readable name (only `""` or `<opaque>`).
* `test_the_movement_the_label_routes_cause_is_pinned_file_by_file` -- the
  receipt: the exact per-file movement map, the count 28, and the denominator
  537, so the routes cannot stop firing in one place and start in another while
  a total stays flat.
* `test_that_sweep_can_detect_movement` -- the control, so neither of the above
  is a check that could not fail.

The three live census surfaces measured before today (`feed`, `profile`,
`settings`) contain no committed fixture, so the only statement available about
them is the structural one: the fall-through is gated on `el.labels`, which does
not exist on anchors or on `div[role="button"]`, and those two are what those
surfaces are made of. The live re-run is the lead's.

## 7. Two other things worth a line

**The census test file now launches Chromium, and its docstring says so.** There
was no way to make a fixture answer this question: name resolution is not
Python, it is the injected script, and a `FakePage` returning a hand-typed
payload certifies the payload. The harness is copied from
`test_apply_modal_fixture.py` -- one browser per test, one ISOLATED CONTEXT per
reading, `window.innerWidth` asserted on every measurement. Nothing reaches
LinkedIn, no account, no persistent profile.

**The sweep reads fixtures as utf-8, not ascii.** `tests/fixtures/
profile_views_analytics*.html` carry raw non-ASCII bytes and
`read_text(encoding="ascii")` raises on them. That is a property of those
captures, not of this edit; the derived fixtures elsewhere in the suite are
still read as ascii by their own tests, and every string this slice ADDED to the
repo is ASCII.

## 8. Verification

```
$ venv\Scripts\python.exe -m pytest -q tests/test_surface_census.py \
      tests/test_readonly.py tests/test_no_committed_identity.py tests/test_tools.py
513 passed in 24.69s
```

With `tests/test_path_hygiene.py` added (not required, run because this slice
writes new fixture text): **532 passed**. `tests/test_surface_census.py` alone is
**84 passed**, 73 of which are the pre-existing tests, unedited. The full suite
was NOT run, per the brief.

`tests/test_readonly.py` passes with `CENSUS_JS` unchanged in its
`INJECTED_SCRIPTS` declaration -- no new script was added, and no token this
slice introduced (`el.labels`, `.closest(`, `getAttribute`) is on
`readonly.JS_MUTATION_TOKENS`. The scanner was not worked around.

Not done, per the brief: no commit, no `git add`, no `_state/` access, no
`mcp__linkedin__*` call, no Chrome profile launch.
