# Slice: repoint the tests that pinned "apply registers no tool"

Date: 2026-08-25. Scope: `tests/` only. No file under `linkedin_server/` was
touched. Nothing committed; all changes are in the working tree.

## Headline

    collected BEFORE: 1462      collected AFTER: 1462      (no test deleted)
    suite BEFORE:     16 failed, 1446 passed
    suite AFTER:       2 failed, 1460 passed

The 2 remaining failures are EXACTLY the two reserved for you and untouched by
me:

    tests/test_writes.py::test_apply_is_sanctioned_and_refuses_for_the_flow_it_has_never_seen
    tests/test_writes.py::test_a_second_click_inside_perform_is_still_caught

**Excluding those two: 1460 passed, 0 failed.** All 14 tests you listed are
green. Nothing was deleted, skipped, xfailed or weakened.

Files edited (both verified 0 bytes > 127):

    tests/test_server_surface.py    50288 bytes, 0 bytes > 127
    tests/test_writes.py           141966 bytes, 0 bytes > 127

## ONE RENAME -- read this before you grep

    test_the_surface_is_exactly_the_seventeen_tools
      -> test_the_surface_is_exactly_the_eighteen_tools

Renamed, not deleted; collected count is unchanged at 1462. I renamed it
because this specific test has been renamed for this reason before -- it
shipped as `test_the_surface_is_exactly_the_nine_reads` in `1a94cf9` -- and a
test named "seventeen" over a body asserting eighteen is the exact species of
stale claim this file exists to catch. The rename is recorded in the test's own
docstring. Revert it if you would rather keep the name stable.

I did NOT rename `test_the_exemption_covers_only_those_two` or
`test_the_two_exempted_names_do_in_fact_trip_the_name_check`; both already said
"two" while covering three before this change, so that drift is pre-existing
and I left it rather than widen the diff.

## Two PRODUCT defects found, NOT fixed (rule 3), NOT test-visible

Neither of these makes the suite red -- no test pins either string -- so they
did not block green. Both are stale claims in prose the caller actually reads,
which is the failure class this repo's tests exist to catch, and both were
reversed by the same change that reversed the tests.

### 1. `linkedin_server/server.py` ~line 1637 -- `server_info()["irreversible"]["note"]`

The note is a hardcoded string, still reading:

    "Every action this process could actually perform is REVERSIBLE, and its
    inverse is named in the preview block. The irreversible one is sanctioned
    and is NOT performable -- see writes_sanctioned_but_not_performed. Read
    the two lists together: the first being empty means something only because
    the second is not."

Every clause is now false:

- apply_job IS performable and carries `irreversible=True`;
- its inverse is NOT named in the preview block -- `reversible_by` says NOBODY;
- it is NOT in `writes_sanctioned_but_not_performed` (that field is now
  `{follow_company, set_open_to_work}`, which my repointed test asserts);
- the first list is no longer empty -- it is `["apply_job"]`.

The comment block directly above it (server.py ~1620-1624) carries the same
reversed rationale. This is the most dangerous residue of the change: the two
LISTS beside the note are correct and derived, so a caller reading the note
gets a confident false reassurance printed next to accurate data.

Once you fix the note, this assertion pins it and will fail on the current
string. I did not add it, because it would leave the suite red:

```python
    note = block["note"]
    assert "Every action this process could actually perform is REVERSIBLE" \
        not in note
    for action in block["performable_and_irreversible"]:
        assert action in note, action
```

### 2. `linkedin_server/writes.py` lines 517-530 -- apply's `reversibility_procedure`

This text is RENDERED into `block["reversibility"]`, i.e. into the confirm
block a human reads before submitting an application. It still says:

    "THE FLOW ITSELF IS THE LARGER GAP: no capture in this repo shows the
    LinkedIn apply form at all, so before any apply could be attempted there
    would have to be a capture containing the form, its fields, its resume
    selection, any screening questions, and the control that submits it. THAT
    CAPTURE NOW HAS A PROCEDURE ... scripts/_probe_apply_flow.py ... It has
    not been run."

The comment 60 lines above it in the same file says the flow WAS captured on
2026-08-24 (2 forms, 1 file input, 1 dialog, 43 buttons, one enabled "Submit
application"). So the block tells the operator, at the moment of confirming,
that the thing about to happen has never been observed and cannot be attempted
until a script is run. The first half of the same field (the UNMEASURED
withdraw verdict and "What would settle it") is still accurate and is pinned by
`test_an_unmeasured_verdict_prints_as_unmeasured_and_names_its_fix`; only this
trailing paragraph is stale.

### Minor, pre-existing, offered as a note to the next repointer

`linkedin_server_info` wraps its body in `_error(exc)`, so any exception inside
it returns `{'error': 'unexpected', 'message': ...}` rather than raising. While
probing falsifiability I removed `apply_job` from `writes.PERFORMABLE` and got
`KeyError: 'apply_job'` (server.py looks up `_WHY_NOT_PERFORMED[action]` for
every sanctioned-but-not-performable action, and apply's entry was deliberately
removed) -- surfacing to the test as a bare `KeyError: 'irreversible'` on the
returned dict. Not a regression, and not caused by this change; just an
unhelpful failure mode if `PERFORMABLE` and `_WHY_NOT_PERFORMED` ever drift.

## Tests I could NOT repoint honestly

**None.** Every one of the 14 kept a falsifiable check. The two that came
closest to being un-repointable are documented below (items 14 and 18): in both
cases the property the test pinned was genuinely INVERTED by the change, and in
both cases the check survives as its own inverse rather than being dropped.

I verified that with a throwaway probe (created, run, deleted -- not left in
the tree) that mutated the world and confirmed the repointed assertions go RED:

- flipping apply's spec to `irreversible=False` -> the irreversibility test's
  `expected` and `expected_performable == ["apply_job"]` anchors both fail;
- stripping apply's `url_template` -> the writes-side `surfaceless` and
  `url_template is not None` anchors both fail;
- restoring the old instructions wording -> all five new instruction pins fail
  and the `"does not submit applications" not in text` inversion fails;
- removing apply from `EXPECTED_TOOLS` -> the 18-count and membership fail.

## What changed, test by test

### tests/test_server_surface.py

Module-level constants (not tests, but they are what most of the file derives
from):

1. **Module docstring** -- rewrote the "AND NOTE WHAT IS NOT ON THE SURFACE"
   paragraph, which claimed apply "registers NO TOOL and stays on
   FORBIDDEN_TOOLS"; quoted the old claim, named the capture that falsified it,
   and handed the paragraph's subject to `set_open_to_work`.
2. **`SANCTIONED_WRITE_TOOLS`** -- added `linkedin_apply_job`, with a note that
   the intersection with `SANCTIONED_WRITES` is doing its job (apply was
   already sanctioned on 2026-08-24; what changed is `PERFORMABLE` plus
   registration, not this line).
3. **`EXPECTED_TOOLS`** -- added `linkedin_apply_job`. Quoted the old comment
   verbatim ("apply is sanctioned and specced and registers NO TOOL ...") and
   recorded which clause became false and which one still holds and is why the
   name was allowed to move.
4. **`FORBIDDEN_TOOLS`** -- removed `linkedin_apply_job`, which is the ONLY
   sanctioned way off that set (it is in `SANCTIONED_WRITES`, so the
   conservation law in test_writes.py still accounts for it). Recorded the move
   in the header comment and stated explicitly that `linkedin_apply` and
   `linkedin_easy_apply` STAY -- nothing is sanctioned under either spelling.

Tests:

5. **test_the_surface_is_exactly_the_eighteen_tools** (renamed, see above) --
   17 -> 18; apply added to the asserted write split; the read count stays a
   literal 14 and is now evidence across two write-adding waves.
6. **test_no_write_tool_exists_under_any_of_its_obvious_names** -- NO body
   edit. Green because apply left `FORBIDDEN_TOOLS` above.
7. **test_no_tool_name_implies_a_write** -- docstring only. Its example ("a
   seventeenth tool called linkedin_apply_job still lands in offenders") became
   false; quoted it and pointed at where the live probe now runs.
8. **test_the_exemption_covers_only_those_two** -- probe swapped from
   `linkedin_apply_job` to `linkedin_set_open_to_work`, which inherits the
   identical condition (sanctioned, full spec, no url_template, no registered
   tool). Added `assert probe in SANCTIONED_WRITES` so the probe cannot decay
   into "made-up names are not exempt", which would prove nothing. Exemption
   set assertion 3 -> 4 names.
9. **test_no_docstring_claims_a_write** -- NO edit. Green via the exemption set.
10. **test_the_docstring_exemption_does_not_cover_the_reads** -- NO edit. Green
    via the exemption set; the planted-victim control still isolates
    `linkedin_saved_jobs`.
11. **test_server_info_stops_claiming_read_only_once_writes_are_on** --
    `writes_available` gains `apply_job`. Kept as a hand-typed literal on
    purpose (deriving it from `PERFORMABLE` would make the test agree with any
    change); said so in a comment.
12. **test_the_capability_is_reported_even_with_the_flag_off** --
    `writes_sanctioned` gains `apply_job`; `writes_sanctioned_but_not_performed`
    drops it (now `{follow_company, set_open_to_work}`). The deleted line
    `assert not_performed["apply_job"]["can_hold_a_grant"] is False` is replaced
    by a TWO-SIDED departure check -- absent from the refusal list AND present
    as a capability -- because absence alone is also satisfied by apply having
    been dropped from the report entirely.
13. **test_the_server_instructions_name_every_write_that_ships** -- the
    `"does not submit applications" in text or "not submit" in text` assertion
    is INVERTED to `"does not submit applications" not in text`, so the
    retracted claim cannot come back. Added five positive pins against the new
    paragraph: the capability (`can now submit an application`), its one
    irreducible warning (`cannot be taken back`), and both refusals that still
    stand (`reported and not driven`, `applicant-tracking system`,
    `multi-step one is refused`). The derived `four write` + tool-name loop and
    the `out of scope` / `read-only window` negatives needed no change.
14. **test_server_info_reports_irreversibility_before_a_caller_commits** --
    THE ONE WHOSE INVARIANT GENUINELY INVERTED. It asserted
    `performable_and_irreversible == []` and then walked `PERFORMABLE`
    asserting every spec `irreversible is False`. That property is now false by
    design: this server can now perform something it cannot undo. Repointed to
    assert AGREEMENT ACROSS FIELDS instead of a value -- both lists derived
    from the specs, a hand-typed `== ["apply_job"]` anchor so the two derived
    views cannot be wrong together, `performable <= sanctioned`, and a loop
    that splits by side of the boundary: a reachable irreversible action must
    appear in `writes_sanctioned` and in `performable_and_irreversible` and NOT
    in `writes_sanctioned_but_not_performed`; an unreachable one must appear in
    that field with `irreversible is True`. Neither arm was dropped. The
    docstring quotes the old empty-list argument and states its new form.
    (This is the test whose `note` sibling is product defect 1 above.)

### tests/test_writes.py

15. **test_nothing_is_both_forbidden_and_sanctioned_by_accident** -- overlap
    `{set_open_to_work, apply_job}` -> `{set_open_to_work}`. Quoted the whole
    2026-08-24 paragraph that argued apply should STAY on the forbidden list,
    named the capture that removed its single premise, and noted which clause
    survived and licensed the move. Added a control: "apply is not in the
    overlap" is equally satisfied by apply being deleted from either list, so
    it is now asserted to be in exactly one of them, the sanctioned one, with a
    url_template.
16. **test_what_ships_is_narrower_than_what_is_sanctioned** -- the outer set
    stays six (apply entered it on 2026-08-24, not now); `PERFORMABLE` 3 -> 4;
    the gap 3 -> 2; `surfaceless` 2 -> 1. Added two assertions that apply is on
    the other side of the surface line (`url_template` equals the posting-page
    template, `url_pattern is not None`) so the shrunken `surfaceless` set is
    not just an absence.
17. **test_exactly_the_performable_writes_are_registered** -- the derived
    assertion needed no edit, which is the test working as designed;
    `assert "linkedin_apply_job" not in names` is INVERTED to `in names` rather
    than deleted, because "reachable" is the claim that now needs pinning.
    Noted that `names & FORBIDDEN_TOOLS == set()` went green by apply moving
    off that list in the open, not by the assertion being loosened.
18. **test_an_unmeasured_verdict_prints_as_unmeasured_and_names_its_fix** --
    the UNMEASURED half is untouched and still exercises the branch this test
    exists for (apply is still `reversibility_measured=False`,
    class STILL-UNKNOWN, `irreversible=True`, `reversible_by` says NOBODY). The
    tail inverted: apply now has a surface, so `to_confirm is None` and
    `"NO CONFIRM TOKEN IS ISSUED"` are replaced by the stronger situation --
    a token IS issued (checked against `writes._GRANTS`, not just truthiness),
    `performed is False`, and `"NO CONFIRM TOKEN IS ISSUED" not in nxt` so a
    silent fall-back to the refusal branch is caught. The old
    `("apply_job", "set_open_to_work")` both-surface-less loop is replaced by
    the split that is now true.
    NOTE: the surface-less branch did not lose coverage. Every string this test
    used to pin is still pinned by
    `test_open_to_work_has_no_measured_surface_and_issues_no_token`
    (test_writes.py ~line 2443), which is green and untouched.

## Verification commands run

    python -m pytest -q --collect-only    # 1462 before, 1462 after
    python -m pytest -q                   # 16 failed/1446 passed -> 2 failed/1460 passed
    python -m pytest tests/test_server_surface.py -q     # 44 passed
    python -m pytest tests/test_writes.py -q             # 2 failed (yours), 141 passed

No browser script, no Playwright script, nothing under `scripts/` was run. The
`browser_page` fixture inside test_writes.py launches headless Chromium as part
of the normal suite; that is the suite's own behaviour, not an added step.
