# Slice: which container each control sits in

Date 2026-08-31. Branch `master`, base `fc9aeb6`, tree otherwise clean.
Files changed: `linkedin_server/dom.py` (the `CENSUS_JS` string and its
comment block only) and `tests/test_surface_census.py`. Nothing committed,
nothing staged, `_state/` untouched, no browser profile launched and no
`mcp__linkedin__*` tool called.

Verification command as briefed:

    venv\Scripts\python.exe -m pytest -q tests/test_surface_census.py \
      tests/test_readonly.py tests/test_no_committed_identity.py \
      tests/test_shape.py tests/test_tools.py
    607 passed in 47.05s

`tests/test_surface_census.py` alone: 100 passed (was 86). No token tripped the
JS mutation scanner -- `readonly.scan_js_for_mutations(dom.CENSUS_JS)` returns
`[]`, and `test_readonly.py` passes untouched. `closest()`, `querySelectorAll`,
`Array.from` and `indexOf` are all reads. Both files decode as pure ASCII.

---

## ESCALATION -- READ FIRST. The brief's two halves cannot both hold.

The brief scopes me to `CENSUS_JS` + its comments in `dom.py`, plus the test
file, and says "touch nothing else". It ALSO says the aggregation is the point
and tells me to put the descriptor in the merge key or carry a set of
containers on the merged row.

**Those are different files.** Measured, not inferred:

* `linkedin_server/dom.py:2587` (post-edit numbering) -- `read_surface_census`
  shapes each control by building a dict literal that ENUMERATES eight keys.
  A ninth field emitted by the script dies there, ~40 lines below the string I
  own.
* `linkedin_server/shape.py:3681` -- `census_aggregate` builds its merge key as
  an explicit eight-field tuple.

So the container descriptor is real, measured and tested, and **it does not
reach any tool output**. I did not touch either site. I did not silently let
this pass either: it is pinned in the suite by
`test_the_shaped_reader_still_drops_the_container_descriptor`, which fails the
moment somebody wires it through, and documented in the `CENSUS_JS` comment.

**The root cause of the brief's assumption is a false docstring, and it is
worth fixing on its own.** `census_aggregate`'s docstring says:

> The merge key is the WHOLE record, not just the name

It is not. It is eight named fields. Anybody reading that docstring -- which
is how this brief was written -- would reasonably expect an additive field to
join the key automatically. It does not, and nothing errors.

Two edits close the gap. Both are outside my ownership and neither is made:

1. `dom.py` shaped dict: add `"container": control.get("container") or "none"`.
2. `shape.py` `census_aggregate`: see the merge-key decision below.

---

## RED FIRST

Tests written before `dom.py` was touched, run against unmodified `CENSUS_JS`.
Line numbers are from that moment; the file has since grown.

    FFFFF.FF                                                                 [100%]
    ================================== FAILURES ===================================
    ________ test_the_same_name_in_two_containers_is_two_different_answers ________
                "accessible name, so distinguishing them proves nothing."
            )
    >       assert rows[ROW_NO_CONTAINER]["container"] == "none"
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    E       KeyError: 'container'

    tests\test_surface_census.py:1655: KeyError

    ________ test_a_control_in_no_container_says_none_rather_than_nothing _________
            rows = await _container_rows(census_over)
    >       assert all("container" in row for row in rows)
    E       assert False
    E        +  where False = all(<generator object ... at 0x000001FB050F8C70>)

    tests\test_surface_census.py:1687: AssertionError

    =========================== short test summary info ===========================
    FAILED tests/test_surface_census.py::test_the_same_name_in_two_containers_is_two_different_answers
    FAILED tests/test_surface_census.py::test_two_controls_in_one_container_share_a_descriptor
    FAILED tests/test_surface_census.py::test_the_nearest_container_wins_when_containers_nest
    FAILED tests/test_surface_census.py::test_a_control_in_no_container_says_none_rather_than_nothing
    FAILED tests/test_surface_census.py::test_the_container_descriptor_carries_no_text_from_the_container
    FAILED tests/test_surface_census.py::test_the_role_arm_of_the_container_selector_fires
    FAILED tests/test_surface_census.py::test_the_descriptor_population_is_not_the_counts_block
    7 failed, 1 passed, 84 deselected in 7.53s

The one pass is `test_that_privacy_check_is_reading_markup_that_carries_the_name`,
the non-vacuity control: it asserts the planted name really is in the fixture's
heading, id, class and aria-label, which is true with or without the walk.

## THE DESCRIPTOR FORMAT

One new key per control row, appended LAST, always present, always a string:

    "container": "form#0" | "dialog#3" | "none"

* **Kind** is the container's ROLE if that role is `dialog` or `form`,
  otherwise its TAG. So `<div role="dialog">` is `dialog`, `<section
  role="form">` is `form`, and `<dialog role="alertdialog">` falls back to its
  tag and is `dialog`. Nothing else can appear.
* **Index** is ONE document-order sequence over the UNION of containers,
  assigned once per run from `document.querySelectorAll('form, dialog,
  [role="dialog"], [role="form"]')` -- not one counter per kind. A descriptor
  is therefore unique in the document, so `form#3` and `dialog#3` cannot be
  two names for different containers, and two controls in one container get a
  string a reader can GROUP BY.
* **Nearest ancestor**, via `el.closest(containerSelector)`.
* **`none`** for a control with no such ancestor. A string, never null, never
  a missing key.
* **No text ever.** No heading, no aria-label, no id, no class. The kind is a
  tag or one of two role words; the index is an integer.

## MERGE-KEY DECISION: option B -- the merged row carries the SET of containers

**Not the merge key.** Justified by measurement, not preference.

`census_redact_rare(shape, count)` fires **only when `count == 1`** and blanks
any run of two capitalised words, and its own docstring says it over-redacts by
construction. The count is a function of the merge key. So adding a field to
the merge key is not additive at all -- **it is a redaction change.**

Measured on `shape.census_aggregate` directly, two identical `Easy Apply`
buttons in two different dialogs:

    TODAY (key without container):
      [{'shape': 'Easy Apply', 'count': 2, ...}]
    OPTION A (container in the key) -- equivalent to two separate merges:
      [{'shape': '<redacted>', 'count': 1, ...}] [{'shape': '<redacted>', 'count': 1, ...}]

Option A splits a readable furniture shape into two singletons and the
singleton cap then blanks both. That is the same class of harm the label-routes
edit went out of its way to avoid ("NOT ONE control whose published shape was a
readable name changed") and it would hit every capture at once, because every
count in every census would move. A field added to answer a question must not
silently destroy the answers already published.

Option B leaves the key alone: every shape, every count and every redaction
decision in every existing capture stays identical, and the row gains where it
was seen.

**Recommended form, and it is strictly better than a bare set** -- a COUNTED
MAP, not a list:

    {"shape": "Submit", "count": 2, ..., "containers": {"dialog#1": 1, "dialog#2": 1}}

A bare set loses the split as soon as the count exceeds the set size ("5
controls across 2 containers" tells you nothing). The map buys back exactly
what option A would have bought, with no effect on the merge key and therefore
none on redaction: the redactor reads the MERGED count, which is unchanged, so
a per-container 1 in the map cannot switch it on. (The option A harm above is
measured. The counted-map variant is reasoned, not run -- it is in a file I do
not own.)

**Implementation note for whoever lands it.** `census_aggregate` re-merges
AFTER redaction (`merged[redacted] = merged.get(redacted, 0) + count`). The
container map has to be UNIONED in that second pass as well, or two redacted
singletons from two containers will merge into one row of count 2 carrying only
one of the two containers -- a stale field that looks measured.

## NOTHING ELSE MOVED

Two independent sweeps, both over all 19 committed fixtures, both pinned in the
suite. The comparator reports differing FIELD NAMES only, never values, so no
accessible name can reach a CI log.

1. **Script level** -- `CENSUS_JS` versus the same script with the container
   call site deleted, 537 controls: **zero** pre-existing fields differ. Name,
   name_source, tag, role, href, has_href, aria_expanded, disabled, and the
   whole counts block, identical on every control.
   (`test_no_committed_fixture_moves_a_pre_existing_field`)
2. **Reader level, which is what captures were written from** --
   `read_surface_census` pointed at the pre-edit script, whole return value
   compared including `shape` and `href_shape`, which the script-level sweep
   cannot see: identical on all 19 fixtures.
   (`test_the_shaped_reader_returns_what_it_returned_before`)

Both have a can-fail control run over the same committed file
(`jobs_tracker_empty.html`): the label-routes derivation makes the SAME
comparator report 12 moved rows at both levels, so "zero" is a reading rather
than a comparison that could not fail.
(`test_that_sweep_can_detect_a_moved_field`,
`test_that_reader_comparison_can_detect_a_changed_row`)

Nothing in `_audit/` is contradicted: no capture's shapes, counts or ordering
change, and the new field does not reach the tool at all (see the escalation).

## MUTATION EVIDENCE

Done twice: as permanent in-suite derivations, and live against `dom.py`
itself with a sha256 backup/restore (`restored: True 9e06384056d91e2b`).

**A. Walk removed** (`,\n      container: containerOf(el)` deleted) --
11 failed, 1 passed. Every section 8c reading, the repo-wide format check, both
mutation tests and the boundary pin go red. Only the non-vacuity control
survives, correctly.

**B. Nearest replaced by outermost** (`el.closest(containerSelector)` ->
`containerNodes.filter(...)[0]`) -- 4 failed, 8 passed, and the nested test is
one of them:

    FAILED tests/test_surface_census.py::test_the_nearest_container_wins_when_containers_nest
    FAILED tests/test_surface_census.py::test_the_descriptor_population_is_not_the_counts_block
    FAILED tests/test_surface_census.py::test_every_descriptor_in_every_committed_fixture_is_a_shape
    FAILED tests/test_surface_census.py::test_walking_to_the_outermost_container_breaks_the_nesting

The third of those is the interesting one. Under the outermost rule, across all
19 committed fixtures, **not one `form#` descriptor survives** -- the assertion
that fails is `any(d.startswith("form#"))`. Measured over the corpus:

    controls            : 537
    moved by outermost  : 2
    kinds nearest       : {'dialog': 1, 'form': 2, 'none': 534}
    kinds outermost     : {'dialog': 3, 'none': 534}
    apply_modal_derived.html: 2/45

Every form in the captures is inside a dialog. Nearest-versus-outermost is
exactly the difference between naming the editor and naming the modal around
it, on LinkedIn's own markup.

## THE REAL-CAPTURE FINDING (unasked for, and the best evidence in the slice)

`apply_modal_derived.html` is the only committed fixture with containers in it,
and what it holds is the intro editor's question already answered on a real
capture -- ONE dialog holding TWO SEPARATE FORMS:

    form#1   input   label-for     'Resume'
    form#2   input   label-for     'Phone'
    dialog#0 button  aria-label    'Submit application'

A flat list says the modal has a submit button and two inputs. This says the
submit belongs to the modal itself and the two inputs belong to two DIFFERENT
forms inside it -- which no amount of reading adjacency would have produced,
and which the outermost walk would have destroyed. Pinned as
`FIXTURE_CONTAINMENT`.

## THE PRIVACY TEST

`test_the_container_descriptor_carries_no_text_from_the_container`. Container
`#4` of the invented fixture carries a person's name FOUR ways at once --
heading, id, class and aria-label:

    <section role="dialog" id="jane-doe-intro" class="jane-doe-intro-panel"
             aria-label="Jane Doe"><h2>Jane Doe</h2><button>Message</button></section>

The descriptor is `dialog#4`, and the test asserts none of `Jane`, `Doe` or
`jane-doe` appears in it, case-insensitively. Its non-vacuity control
(`test_that_privacy_check_is_reading_markup_that_carries_the_name`) asserts all
four plants are actually in the markup -- that control passed even before the
walk existed, which is what makes it a control.

Repo-wide, `test_every_descriptor_in_every_committed_fixture_is_a_shape`
whitelists the two legal forms (`^(?:none|(?:form|dialog)#[0-9]+)$`) over all
537 controls. It is a whitelist rather than a name search, for the same reason
the shaper is.

The name is invented (`Jane Doe` is already the literal content of the label
fixture beside it) and the fixture carries no slug, urn, email, phone or id
shape. `test_no_committed_identity.py` passes; no `DECLARED_PLANTS` entry was
added.

## LIMITS OF THIS APPROACH

1. **It does not reach a caller.** See the escalation. This is the limit that
   matters; everything below is smaller.
2. **The corpus barely exercises it.** 534 of 537 committed controls are in no
   container at all. The format check covers the repo; the VALUES are certified
   on three real controls in one fixture plus the invented markup. The live
   re-run on the intro editor is where this gets its real workout.
3. **The descriptor's population is NOT the counts block.** `counts.forms` is
   `form` and `counts.dialogs` is `[role="dialog"], dialog`; the container
   selector is their union PLUS `[role="form"]`, which neither counts. A reader
   who adds the two counts and expects that many containers will be wrong.
   Pinned in `test_the_descriptor_population_is_not_the_counts_block`.
4. **The index is per-RUN, not stable across runs.** It is document order in
   the DOM as rendered at that moment. Two censuses of the same url can
   legitimately disagree about which dialog is `#3` if the page rendered a
   different number of dialogs. The descriptor groups controls WITHIN one
   census; it is not a cross-census identifier and must not be used as one.
5. **`closest()` starts at the element itself.** A control that also matched
   the container selector would name itself. No member of
   `CENSUS_CONTROL_SELECTOR` can do that without a role no real page writes; it
   has never been observed, and it is documented in `dom.py` rather than
   guarded -- a guard would be code with no failing case behind it.
6. **Shadow DOM and iframes are invisible to `closest()`.** A control inside a
   shadow root reports the containment of its own tree, and one inside an
   iframe is not in this document at all. Neither has been observed on a
   censused surface; neither is handled.
7. **Nothing here was measured against live LinkedIn.** All readings are from
   committed fixtures and invented markup in headless Chromium at 1280x720,
   isolated context per reading, `window.innerWidth` asserted on every
   measurement. The 256-control intro-editor capture quoted in the brief is the
   wave lead's, not mine.
