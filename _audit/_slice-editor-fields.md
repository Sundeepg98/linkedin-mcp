# Slice: `linkedin_profile_editor_fields` -- names, from inside one measured container

**Status:** built and tested. Left UNCOMMITTED by this slice as instructed --
**then committed by another writer in this tree while the final suite run was still
in flight.** See section 0b; nothing was lost and nothing here did the committing.
**Branch:** `master`. Written on top of `08e846a`; landed as `3940f72`, whose parent is
`826efe7` -- a docs commit from a sibling that arrived under this work. Nothing pushed,
no `mcp__linkedin__*` tool called, `_state/` untouched,
`readonly._ALLOWED_URL_PATTERNS` and `_FORBIDDEN_URL_SUBSTRINGS` untouched.

---

## 0. ONE DISCREPANCY WITH THE BRIEF, AND IT IS THE FIRST THING TO READ

**The brief says the suite baseline is 2156. Measured at `08e846a`, it is 2158.**

Measured rather than argued: `git archive HEAD` into a scratch directory, `git init`
plus one commit there so the two modules that shell out to `git ls-files` can collect,
then `pytest --collect-only -q` in that untouched copy.

```
2158 tests collected in 2.11s
```

Nothing is failing and nothing about the slice depends on which number is right, so
this was not escalated mid-flight. It is flagged here because a stale baseline is the
kind of premise that turns into a "you broke two tests" bounce three waves later.

**Final numbers, and the arithmetic between them:**

| | count |
|---|---|
| `08e846a`, measured | **2158** |
| this tree, `venv\Scripts\python.exe -m pytest -q` | **2205 passed in 764.45s** |
| delta | **+47** |

That 764.45s run is the LAST one, taken after the prose-count corrections in section 1.
An earlier identical-content run of the code alone gave 2205 passed in 746.18s; both
are recorded so nobody has to wonder which edit a number predates.

The +47 decomposes exactly, with no residue:

* **+46** -- `tests/test_editor_fields.py`, the new file.
* **+1** -- `test_every_script_this_package_executes_cannot_mutate` is parametrised
  over `EXECUTED_SCRIPTS`, which went from seven scripts to eight.

Derived by collecting three ways with the two git-dependent modules excluded from all
three: HEAD 1834, this tree 1881, this tree with `--ignore=tests/test_editor_fields.py`
1835.

## 0b. A SECOND WRITER MOVED THIS TREE MID-RUN, and the number above needs its timestamp

The 2205 was measured on a tree that no longer exists, and the reason is not a mistake
in it -- it is that **this repository had two writers during this slice.** Recorded here
because a suite number without the tree it was taken on is exactly the kind of claim
this repo keeps having to correct.

| when | what |
|---|---|
| 15:10:03 | this slice's final `pytest -q` starts and COLLECTS -- 2205 tests |
| 15:11:36 | a sibling commits `826efe7`, adding one tracked file, `_audit/2026-08-31-linkedin-lift.md` |
| 15:17:39 | a sibling commits `3940f72` -- **this slice's eight files, committed by somebody other than this slice** |
| 15:22:48 | the run ends: **2205 passed in 764.45s**, on the file set it collected at 15:10 |

**Nothing was lost and nothing here did the committing.** The brief said leave the tree
uncommitted for review, and this slice did; the commit was made by another actor with
the operator's git identity, six minutes after the run began.

**The count is now 2211, and the +6 decomposes exactly.** Three files became TRACKED
across those two commits -- `_audit/2026-08-31-linkedin-lift.md` from the sibling, and
`tests/test_editor_fields.py` plus `_audit/_slice-editor-fields.md` from this slice's
own commit. Two checks are parametrised per tracked file, measured off the collection
rather than assumed:

```
3 tests/test_no_committed_identity.py::test_no_tracked_file_carries_a_real_identifier
3 tests/test_no_committed_credential.py::test_no_tracked_file_carries_a_session_credential
```

Three files times two sweeps is six, with no residue. **Both sweeps PASS on this
slice's two newly tracked files** -- run explicitly, since being committed is what first
subjected this file and the test module to the identity scan, and both carry invented
slugs and a urn:

```
tests/test_no_committed_identity.py tests/test_no_committed_credential.py tests/test_path_hygiene.py
349 passed in 7.45s
```

`_audit/2026-08-31-linkedin-lift.md` was still being edited by its own writer while
this was measured, so the tree was not quiescent and no number taken here should be
read as one taken on a still repository.

### The sibling is BUILDING ON this slice, not colliding with it -- measured

By the time this was written the working tree carried another 857 uncommitted lines
across `dom.py`, `server.py`, `test_readonly.py` and `test_server_surface.py`: a
sibling's next slice (`read_own_activity_items`, `ACTIVITY_REFUSALS`,
`ACTIVITY_PERMALINK_MARKER`). Sampled rather than assumed, because uncommitted
interleaved edits are the one unrecoverable state:

* **This slice's symbols are all still present** -- `EDITOR_FIELDS_JS`,
  `read_self_owned_editor_fields`, `EDITOR_ANCHOR_NAME`,
  `linkedin_profile_editor_fields`, `SELF_PROFILE_EDIT_INTRO_URL`,
  `_self_assertion_on`.
* **The sibling's diff is additive.** Across all four files it removes FIVE lines, and
  they are exactly the five counts this slice had just moved, being moved again for
  their tool: `waived_in.get("dom.py", 0) <= 8`, `len(EXECUTED_SCRIPTS) == 8`,
  `test_the_surface_is_exactly_the_thirtytwo_tools`, `len(tools) == 32`, and the
  non-write `== 20`. Nothing of this slice's was overwritten.
* Their new prose CITES this slice -- `shape.census_substitute`, `EDITOR_FIELDS_JS`,
  `read_self_owned_editor_fields` -- so the coupling is deliberate.

### Three suite runs, and which one is this slice's number

| tree | result |
|---|---|
| **this slice, in the real repo, before either commit** | **2205 passed in 764.45s** -- the number for this slice |
| commit `3940f72` alone, in an isolated `git archive` copy | 2 failed, 2203 passed, 6 skipped in 1026.51s |
| working tree = `3940f72` + the sibling's in-flight edits | 1 failed, 2210 passed in 880.87s |

**Neither failure is this slice's, and both are shown so rather than asserted.**

The isolated copy's two failures are
`test_path_hygiene.py::test_a_cookie_jar_failure_never_returns_an_absolute_path`, on
both its parameters. THE CONTROL: the same two tests were run in the OTHER scratch copy
-- the one archived from `08e846a`, containing none of this work -- and they fail there
identically (`2 failed, 17 passed in 8.02s`). They are artefacts of running from a
directory that is not the repo root, which is what a path-scrubbing test would be
expected to notice. The 6 skips are the same class: `test_vendored_buildinfo.py`
skipping because the `jobcore` checkout is not beside a scratch copy. 2203 + 2 + 6 =
2211, with no residue.

The working tree's one failure is
`test_writes.py::test_a_second_click_inside_perform_is_still_caught` -- a file this
slice does not touch, on a tree carrying the sibling's half-finished edits. It passed
in this slice's own run and did not fail in the isolated copy of `3940f72`, which is
the pair of readings that places it.

---

## 1. What was built

| file | change |
|---|---|
| `linkedin_server/shape.py` | `census_substitute` factored OUT of `census_shape`; `census_shape` is now that call plus its gate |
| `linkedin_server/dom.py` | new `EDITOR_FIELDS_JS`, `EDITOR_ANCHOR_NAME`, `EDITOR_CONTAINER_SELECTOR`, `EDITOR_MAX_CONTROLS`, `read_self_owned_editor_fields` |
| `linkedin_server/server.py` | new tool `linkedin_profile_editor_fields`, plus `SELF_PROFILE_URL`, `SELF_PROFILE_EDIT_INTRO_URL`, `_MEMBER_SEGMENT`, `_landed_path`, `_member_segment_of`, `_self_assertion_on`, `_path_without_member`, `_ownership_block` |
| `tests/test_readonly.py` | `EDITOR_FIELDS_JS` declared in `INJECTED_SCRIPTS`; executed-script count 7 -> 8; dom.py evaluate-waiver budget 7 -> 8 |
| `tests/test_server_surface.py` | tool added to `EXPECTED_TOOLS`; count 31 -> 32; non-write count 19 -> 20; test renamed `..._twentythree_tools` -> `..._thirtytwo_tools` |
| `tests/test_editor_fields.py` | NEW, 46 tests |
| `linkedin_server/server.py` (module docstring) | count corrections, below |
| `README.md` | count corrections and one table row, below |

### The counts my change made false, corrected in the same edit

Four prose claims were stale the moment the tool registered, and all four were
COUNTS -- the thing this repo's own module docstring says "keeps rotting", right above
the sentence admitting it had already been wrong four times. Nothing tests them; they
were found by grep after the code was green, not by a failure.

| where | was | now |
|---|---|---|
| `server.py` line 1 | "thirty-one tools" / "NINETEEN read" / "Nineteen plus seven plus five is thirty-one" | thirty-two / TWENTY / "Twenty plus seven plus five is thirty-two" |
| `README.md` headline | "Thirty-one tools ship. Nineteen read." | "Thirty-two tools ship. Twenty read." |
| `README.md` derivation note | "thirty-one and nineteen are pinned in" | "thirty-two and twenty are pinned in" |
| `README.md` file map | "server.py the thirty-one tools" | "the thirty-two tools" |
| `README.md` reads table | "All nineteen reads are here" over a table with no row for this tool | "All twenty", plus the row |

Each correction records what the line used to say, in the register the surrounding
prose already uses. **One extra thing was changed while in there:** the module
docstring cited three pin sites BY LINE NUMBER -- "line 356 ... line 1252 ... line
413" -- and all three were already wrong, because the assertions had moved when the
comments above them grew. Those citations are now TEST NAMES, which grep finds and an
edit does not silently move. That is a citation-rot fix rather than a count fix and is
called out separately so a reviewer can reject it on its own.

**One stale count was left alone, deliberately:** `README.md`'s file map says
`tests/ 1393 tests`. It is off by roughly eight hundred, it was stale before this slice
touched anything, and correcting it is not this slice's to make.

**`linkedin_surface_census` and `shape.census_shape` are unmodified in behaviour.**
`census_shape`'s body changed shape (its two early-return branches folded into
`census_substitute`) and its outputs did not -- R11 pins that against outputs captured
from the pre-move code.

### The three things the ruling asked for, and where each lives

1. **Self-ownership established per call** -- `server.linkedin_profile_editor_fields`.
   Load 1 `/in/me/`, require `isSelfProfile=true` on the landed url AND a
   `/in/<segment>/` path; load 2 `/in/me/edit/intro/`, require the same segment. Two
   loads exactly, at the `max_page_loads_per_call: 2` ceiling.
2. **Container identified structurally** -- `dom.EDITOR_FIELDS_JS`. The nearest
   `dialog, [role="dialog"]` ancestor of the one control whose accessible name is
   `Save`. No index anywhere in the script.
3. **The gate relaxed, the substitutions kept** -- `read_self_owned_editor_fields`
   calls `shape.census_substitute`, not `shape.census_shape`. One word, and it is the
   whole capability.

### Two design calls worth reviewing rather than skimming

**The ambiguity count is DOCUMENT-WIDE.** Two controls named `Save` anywhere on the
page is `ambiguous_anchor`, even if only one is inside a dialog. The brief's wording
allows either reading; this is the strict one, because "the one in the dialog" is
itself a rule about position and position is what this reader exists to refuse.

**`required` is a tri-state, not a boolean.** `True`/`False` for input/select/textarea,
`None` for anything else unless it wears `aria-required`. A `False` on a button would
have meant "measured, and optional", which nobody measured -- the same conflation
`checked` already carries a comment about. No extra `required_source` key was added;
the field count stayed at the ten the brief named.

---

## 2. R1-R11: every check, shown failing

Each mutation was applied to the real source, the single test run, the file restored
from a byte-for-byte backup in a `finally`. The harness is
`<scratchpad>/mutate.py`; it is DISPOSABLE and is not harvested -- it encodes this
slice's specific edits and nothing reusable. Tree confirmed restored afterwards
(`scan_js_for_mutations == []`, no `.value`, no `raw_value`, 46 passed).

### R1 -- a label the census refuses comes back NAMED here

Test: `test_a_label_the_census_refuses_comes_back_named_here`.
Both halves asserted in one test, so the relaxation is measured against the thing it
relaxes rather than against nothing. Two failure routes covered: over the 60-character
limit, and outside the ASCII character class.

MUTATION: `dom.py`, `shape.census_substitute(...)` -> `shape.census_shape(...)`.

```
E       AssertionError: ['<opaque>', '<opaque>', 'Note on <urn> for /in/<member>/', 'Learn more', 'Save']
E       assert 'Additional name, and every other spelling this member has gone by' in ['<opaque>', '<opaque>', 'Note on <urn> for /in/<member>/', 'Learn more', 'Save']
```

Note what the mutation shows about the CENSUS: exactly two of the five names collapse
to `<opaque>`, and they are the two the gate is built to refuse. That is the live
`<opaque>` finding from section 2g of `2026-08-31-linkedin-finish.md`, reproduced on
invented markup.

### R2 -- controls outside the container are not returned

Test: `test_controls_outside_the_container_are_not_returned`.
Fixture `TWO_DIALOG_HTML`: a dialog with `Submit` and two fields, a dialog with `Save`
and three fields, plus two loose controls. The in-container set is asserted EXACTLY --
a check that only looked for what must be absent would pass against a reader returning
nothing.

MUTATION: `container.querySelectorAll(...)` -> `document.querySelectorAll(...)`.

```
E       AssertionError: ['Comments', 'Posts', 'Submit', 'Report this ad', 'I have seen the same ad too often', 'Additional name', ...]
E       assert ['Comments', ...al name', ...] == ['Additional ...onth', 'Save']
E
E         At index 0 diff: 'Comments' != 'Additional name'
E         Left contains 5 more items, first extra item: 'I have seen the same ad too often'
```

Control: `test_the_ad_dialog_and_the_loose_controls_are_really_in_that_document`.

### R3 -- the container is found via `Save`, not via an index

Test: `test_the_container_is_found_by_the_anchor_not_by_position`.
**The editor dialog is SECOND in document order in the fixture**, and the test asserts
that ordering before it does anything else -- without it, this check cannot fail.

MUTATION: `anchors[0].closest(cfg.containerSelector)` ->
`document.querySelector(cfg.containerSelector)`.

```
E       AssertionError: ['Submit', 'Report this ad', 'I have seen the same ad too often']
E       assert 'Report this ad' not in ['Submit', 'Report this ad', 'I have seen the same ad too often']
```

### R4 -- two `Save` controls refuse as ambiguous, with no field key

Test: `test_two_anchors_refuse_as_ambiguous_and_carry_no_fields`.
Asserts `"fields" not in result` and `"container" not in result`, never `== []`.

MUTATION, two parts, because the rule is enforced in two places and removing either
alone still refuses: JS `if (anchors.length !== 1)` -> `if (anchors.length < 1)`, AND
Python `if anchors > 1:` -> `if anchors > 2:`.

```
E       AssertionError: {'self_ownership': {'established': True, 'how': "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the same...name': 'I have seen the same ad too often', 'name_source': 'label-for', 'tag': 'input', 'type': 'checkbox', ...}], ...}
E       assert None == 'ambiguous_anchor'
E        +  where None = <built-in method get of dict object at 0x0000018F41CF5F80>('refused')
```

The result repr is the finding: with the rule removed the tool returns the AD DIALOG's
fields (`I have seen the same ad too often`), because `anchors[0]` is the first `Save`
in document order. That is precisely the choose-by-position defect.

### R5 -- zero `Save` controls refuse, with no field key

Test: `test_no_anchor_refuses_and_carries_no_fields`.

MUTATION, three parts, so the failure is a fallback rather than a relabelled refusal:
JS `!== 1` -> `> 1`; JS `container = anchors[0].closest(...)` ->
`container = anchors.length ? anchors[0].closest(...) : document.querySelector(...)`;
Python `if anchors == 0:` -> `if anchors < 0:`.

```
E       AssertionError: {'self_ownership': {'established': True, 'how': "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the same...name': 'I have seen the same ad too often', 'name_source': 'label-for', 'tag': 'input', 'type': 'checkbox', ...}], ...}
E       assert None == 'no_anchor'
```

A third refusal is covered too and is not in the brief's list:
`test_an_anchor_outside_every_dialog_refuses` -- exactly one anchor, no dialog ancestor,
with a dialog full of fields sitting beside it.

### R6 -- no `isSelfProfile=true`: refuse, and the second page is never loaded

Test: `test_a_missing_self_assertion_refuses_before_the_second_load`.
Asserts `navigations == [SELF_PROFILE_URL]` and `pages_loaded == 1`.

MUTATION: `self_assertion = _self_assertion_on(landed_profile)` -> `self_assertion = True`,
which models a tool that trusts what `/in/me/` ought to mean instead of what LinkedIn
said.

```
E       AssertionError: {'self_ownership': {'established': True, 'how': "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the same...'tag': 'select', 'type': None, ...}, {'name': 'Save', 'name_source': 'text', 'tag': 'button', 'type': None, ...}], ...}
E       assert None == 'no_self_assertion'
```

### R7 -- landed urls naming different members refuse

Test: `test_two_landed_urls_naming_different_members_refuse`.

MUTATION: `if editor_segment != profile_segment:` -> `if editor_segment is None:`.

```
E       AssertionError: {'self_ownership': {'established': True, 'how': "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the same...'tag': 'select', 'type': None, ...}, {'name': 'Save', 'name_source': 'text', 'tag': 'button', 'type': None, ...}], ...}
E       assert None == 'different_member'
```

### R8 -- the member segment appears NOWHERE in the returned structure

Test: `test_the_member_segment_appears_nowhere_in_the_answer`. The whole result is
serialised to JSON and searched as one string, because a key-by-key check only covers
the keys somebody thought of.

MUTATION: `_path_without_member` returns `_landed_path(landed_url)` raw.

```
E       AssertionError: {"self_ownership": {"established": true, "how": "LinkedIn's own isSelfProfile=true assertion on /in/me/, plus the same member segment on both landed urls", "self_assertion_present": true, "same_member": true}, "landed_paths": {"profile": "/in/alex-r-12ab34/", "editor": "/in/a
E       assert 'alex-r-12ab34' not in '{"self_owne... not zero."}'
E
E         'alex-r-12ab34' is contained here:
E         ?     -------------------                    ^^^^
E           le": "/in/alex-r-12ab34/", "editor": "/in/alex-r-12ab34/edit/intro"}, ...
```

Two companions: `test_the_segment_sweep_is_looking_at_a_slug_that_was_really_there`
(the control), and `test_a_refusal_does_not_leak_the_segment_either`, which sweeps the
different-member refusal -- the one path that holds BOTH slugs at the moment it writes
its reason.

### R9 -- no control VALUE is returned

Test: `test_no_control_value_is_returned`. **Three edits were tried and the middle one
found a barrier nobody put there on purpose.**

MUTATION A -- `raw_value: String(el.value || '')` in the script:

```
E       AssertionError: assert '.value' not in '\n(cfg) => ...rn out;\n}\n'
E
E         '.value' is contained here:
E            String(el.value || ''),
E         ?           ++++++
```

MUTATION B -- `raw_value: attrOf(el, 'value')` in the script, which reaches the value
without the token. **The test PASSED (`1 passed in 2.12s`).** The reason is
`read_self_owned_editor_fields`'s field dict, which NAMES its ten keys: a field the
script emits and that dict does not name is dropped before anything is returned. The
same enumerate-the-keys discipline that once lost `container` in silence is here a
privacy backstop. Recorded in the test's own docstring, not just here.

MUTATION C -- B plus `"raw_value": control.get("raw_value")` in that dict, which is the
edit somebody would really write, because a value is no use to them until it is
returned:

```
E           AssertionError: VALUE-ALPHA-NOT-A-LABEL
E           assert 'VALUE-ALPHA-NOT-A-LABEL' not in '{"self_owne... not zero."}'
E
E             'VALUE-ALPHA-NOT-A-LABEL' is contained here:
E               _value": "VALUE-ALPHA-NOT-A-LABEL", "has_href": false}, ...
```

So the scan guards the script, the enumeration guards the crossing, the sweep guards
the answer -- three layers, and only the sweep sees an edit that made it all the way
out. `test_no_href_is_returned_either` covers the other field that could carry an
identity out: `has_href` is a boolean and `/help/` appears nowhere in the answer.

### R10 -- the substitutions still run with the gate off

Test: `test_the_substitutions_still_run_with_the_gate_switched_off`. The fixture label
carries a urn AND a member path.

MUTATION: `shape.census_substitute(...)` -> `str(control.get("name") or "")`.

```
E       AssertionError: ['Additional name, and every other spelling this member has gone by', '\u091c\u0928\u0924\u093e City', 'Note on urn:li:fsd_profile:7400000000000000001 for /in/alex-r-12ab34/', 'Learn more', 'Save']
E       assert 'Note on <urn> for /in/<member>/' in [...]
```

Control: `test_that_label_really_carries_both_identities`.

### R11 -- the refactor is behaviour-preserving

Test: `test_the_refactor_left_census_shape_byte_identical`, parametrised over 19 rows.

**The inputs are IMPORTED, not copied.** The first eight rows are
`tests/test_surface_census.py`'s own `LEAKS` table, reused directly, and
`test_the_leaks_table_is_the_one_the_census_file_uses` asserts they still are. Eleven
more rows cover what `LEAKS` deliberately does not: empty, whitespace, `None`, both
sides of the 60-character limit, an em dash, whitespace collapsing. The EXPECTED values
are literals captured by running the PRE-MOVE `census_shape` over these exact strings
before `shape.py` was touched.

MUTATION: delete `shaped = _CENSUS_LONG_DIGITS.sub("<id>", shaped)` from
`census_substitute`.

```
E       AssertionError: digit run
E       assert '/feed/update...000000000001/' == '/feed/update/<id>/'
E
E         - /feed/update/<id>/
E         + /feed/update/7400000000000000001/
```

A second test, `test_the_two_halves_recompose_into_the_whole`, applies the gate by hand
to `census_substitute` and asserts it reproduces `census_shape` on every row -- the
property the pinned table cannot see, since a from-scratch reimplementation could agree
on nineteen strings by luck.

---

## 3. The four structural guards beyond R1-R11

**The two JS name chains are held to agreeing.** `EDITOR_FIELDS_JS` carries its own copy
of `CENSUS_JS`'s resolution chain. The duplication is forced, not chosen: `CENSUS_JS` is
document-wide and would bring every stranger's name on the profile render into this
process, and a script assembled from a shared fragment cannot be certified by
`test_readonly.py`'s call-site resolver -- which is why it is a copy and why
`test_the_editor_chain_resolves_the_same_names_as_the_census` runs both scripts over one
document and compares `(name, name_source)` pairs.

MUTATION: delete the `labelRoutes` call from the editor script's `nameOf`.

```
E           AssertionError: (('', 'none'), [('Additional name', 'label-for'), ('City', 'label-for'), ('Comments', 'text'), ('I have seen the same ad too often', 'label-for'), ('Month', 'label-for'), ('Posts', 'text'), ...])
E           assert ('', 'none') in {('Additional name', 'label-for'), ...}
```

**The ten fields are pinned by name and by count** --
`test_the_ten_fields_are_present_on_every_returned_control` asserts `len(expected) == 10`
and set-equality per record, so the "TEN FIELDS" in the dom.py comment is checkable
rather than trusted. `test_the_tristates_are_not_collapsed_to_booleans` shows `None`,
`True` and `False` all arriving from one document.

**The two addresses are pinned equal to the census's** --
`test_the_two_addresses_are_the_census_surfaces_they_claim_to_be`, plus
`readonly.is_read_url` returning True for both, which is what says the read boundary did
not need to move.

**The census has no path into this reader** --
`test_the_census_has_no_path_into_this_reader` reads `server.py`'s source, asserts
`read_self_owned_editor_fields` is named exactly once in the file, asserts the census
tool's own body does not name it, and asserts `CENSUS_SURFACES` is still five keys. A
caller cannot reach the relaxed behaviour through the instrument it relaxes.

---

## 4. Residues, stated rather than left to be found

1. **An authwall landing could carry a slug through `assert_not_authwall`.** That helper
   raises with the landed url in its message, and `_error` renders it. This is unchanged
   pre-existing behaviour shared with the census -- which also returns `source_url` with
   his slug in it -- and no marker in `AUTHWALL_MARKERS` has been observed on a url
   carrying an `/in/<member>/` path. Not touched, because touching it is a change to a
   shared auth helper and this slice was scoped to one entry point.
2. **A `<select>` whose options are his data would publish them through `text`.** The
   name chain falls through to `innerText`, and for a select that is its option list.
   Inherent to the chain and pre-existing in the census (the footer language picker is
   the known case, where the gate turned it into `<opaque>`); here the gate is off, so a
   select in the editor container would publish its options. In the fixture the select
   is named through `label-for` and never reaches the fall-through. Named, not fixed.
3. **`/in/me/` landing WITHOUT a trailing slash would refuse.** `_MEMBER_SEGMENT`
   requires the slash, per the brief. All four measured profile landings carry it (with
   `?isSelfProfile=true` behind it) and the editor's lack of a trailing slash is handled
   because its segment is still followed by `/edit/intro`. If LinkedIn ever lands
   `/in/<member>` bare, this tool refuses rather than reads -- the conservative
   direction, and a live-usability risk worth knowing about.
4. **The container measurement is from ONE surface.** `Save` is the intro editor's
   commit control on the render captured twice on 2026-08-31. Nothing here establishes
   that it is the anchor for any other editor, and the tool reaches no other page.

## 5. What was NOT done

* No commit, no push, no branch. Tree dirty as instructed.
* No `mcp__linkedin__*` call. Nothing in this slice touched LinkedIn or the account;
  every reading is local headless Chromium over `page.set_content`.
* `readonly._ALLOWED_URL_PATTERNS` and `_FORBIDDEN_URL_SUBSTRINGS` unchanged -- both
  addresses were already admitted, and `is_read_url` is asserted True for both.
* `_state/` untouched.
* The mutation harness is declared **DISPOSABLE**: it encodes this slice's exact edit
  sites and nothing about it generalises, so it is not proposed for an instrument
  register.
