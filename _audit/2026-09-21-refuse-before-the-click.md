# REFUSE BEFORE THE CLICK -- the press gate now consults the basis table before it touches a page

**CORRECTS:** `_audit/_census/network.md` -- row `76`, which states that `/in/me/` + `[aria-haspopup]` **is PERMITTED**, quoting `permitted_to_attempt: true` and `permitted: true, priced_by: [...]`. Re-measured 2026-09-21 through the shipped gate: it is `no_sensitivity_basis` at BOTH ends, and has been since `61e3e01` at 11:56 on 2026-09-19 -- sixty-three minutes after the claim landed at `1f5985d` 10:53. The cell is corrected in place and the row is re-filed from BLOCKED ON EXECUTION to BLOCKED ON A RULING. **NO STATE MOVED:** the row is GAP before and after.

**WAVE:** `refuse-first`. **DATE:** 2026-09-21. **SUBJECT:** `linkedin_server/press.py`,
`tests/test_press.py`, census row `network.md` 76.

**STATUS AT THE TOP, because the rest is evidence.** `press.disclose` took a real
click and a real `Escape` on any surface that passed conditions 1 and 2 and
declared no sensitivity basis, then refused with `no_sensitivity_basis` -- a
refusal derivable from the URL alone. It now refuses BEFORE the page is touched.
Two admitted surfaces were affected: `/search/results/people/`, which lists other
people, and `/in/me/`.

**NOTHING IN THIS WAVE TOUCHED A LIVE PAGE.** Every number here is from the
repository's own `FakePage` and from pure functions. No browser was opened, no
port attached, nothing on 9224 was used or closed, `writes_enabled()` untouched.

**THE WAVE ALSO FOUND THREE THINGS IT WAS NOT SENT FOR**, all in `press.py` and
all the same family, listed in section 7 and fixed with their own controls:
a counter reader returning `None` made a POST-press call look like a PRE-press
one, so the gate clicked and then returned `permitted_to_attempt: true` with no
refusal at all; `structural_argument_incomplete` was a second URL-derivable
refusal taken after the click; and the witness text asserted *"the press was
permitted and safe"* on refusals.

---

## 0. WHAT WAS RUNNING WHEN THIS STARTED

    worktree HEAD    4c8d0f1  merge the-press: All filters is refused at condition 2,
                              and the gate presses before it refuses
    interpreter      venv/Scripts/python.exe   (3.13)
    baseline         tests/test_press.py + tests/test_the_press_gate_cannot_witness_disclosure.py
                     59 passed in 0.78s
    after            88 passed in 1.54s
                     test_press.py: 33 -> 40 test functions, 39 -> 74 cases
                     (the difference is parametrisation)
    wider            + test_readonly, test_readonly_boundary_invariant,
                       test_probe_interaction_budget -> 398 passed in 19.76s
    census gates     test_the_census_prose_matches_the_boundary, test_surface_census,
                     test_prose_that_makes_a_claim,
                     test_a_correction_is_findable_from_the_claim,
                     test_a_settled_count_is_named_once -> 222 passed in 121.91s

Section 3 of `_audit/2026-09-21-the-all-filters-press.md` is the handover this
wave started from. Its reproduction was not rebuilt.

---

## 1. EVERY READER OF `permitted_to_attempt`, AND THE SHAPE CHOSEN

### 1.1 The whole reader set, enumerated before anything was decided

`permitted_to_attempt` is produced in exactly one place and read in exactly
three, two of which are the same test file. Counted, not estimated:

| where | line | what it does with the field |
|---|---|---|
| `linkedin_server/press.py` | the pre-press branch of `evaluate` | PRODUCER -- the only site that sets it |
| `linkedin_server/press.py` | `disclose` | READER -- `pre.get("refused")`; it acts on the ABSENCE of a refusal, which is the defect |
| `tests/test_press.py` | `test_his_own_profile_is_permitted_and_a_third_party_is_not` | asserted `is True` for `/in/me/` |
| `tests/test_press.py` | `test_a_surface_with_no_declared_basis_is_pressed_before_it_is_refused` | asserted `is True` as the characterisation of the defect |
| `_audit/_census/network.md` | row **76** | quotes the pre-press verdict as evidence the row is PERMITTED |
| `_audit/2026-09-21-the-all-filters-press.md` | 3 mentions | prose, the handover |

**AND NOTHING ELSE.** `scripts/_probe_first_sanctioned_press.py` and
`scripts/_probe_all_filters_disclosure_shape.py` are the only two files in the
repository that import `press`, and neither reads the field: the first calls
`check_address`, `check_shape` and then hands to `disclose`; the second never
presses at all. `tests/test_the_press_gate_cannot_witness_disclosure.py` drives
`disclose` but only against `/feed/`, which declares a basis, so it never met
the branch.

**SO THE CONTRACT CHANGE HAS A FOUR-SITE BLAST RADIUS**, not a package-wide one.
That is why the shape below could be decided on the merits rather than on how
much would break.

### 1.2 The shape chosen: (b), with the pre-press permit made more informative

**CHOSEN: (b) -- `permitted_to_attempt` is False whenever no basis exists.**
The pre-press verdict now returns the refusal itself, `no_sensitivity_basis`,
with `reachable_by_this_route: true`.

**(a) WAS PREFERRED BY THE BRIEF AND IS UNAVAILABLE ON THE EVIDENCE, which is
the finding rather than a preference.** Giving `/in/me/` its own basis entry
needs one of two routes and neither can be written honestly today:

* **Route (a), a sensitive counter.** None is known for a profile overflow
  press. The feed's `off_state` is a reaction counter; it prices a reaction,
  not a profile menu.
* **Route (b), a structural argument.** It must claim NO OUTWARD EFFECT is
  possible. The analytics entry -- the only structural argument on the record --
  lists among its own REFUTERS *"the expanded region containing any control that
  addresses a person (message, invite, follow, endorse)"*. On a profile that
  refuter is live and unchecked, and **census row 76's own measurement says why
  it cannot be checked**: `/in/me/` draws exactly one `[aria-haspopup]` and zero
  `[role=menu]` / `[role=menuitem]`, so whatever it opens is built on demand and
  **cannot be read unpressed**.

**The argument would therefore have to assert the absence of exactly the thing
only the press it authorises can look at.** That is circular, and
`press.py` says in terms what such an entry would be: *"a basis a caller can
assert is a basis a caller can invent, and 'no outward effect is possible here'
is exactly the claim somebody in a hurry would assert about a surface they had
not read."* **This wave declined to write one and says so instead.** Route (a)
remains correct as a general policy and is the right answer for
`/search/results/people/` too, once somebody can argue it; what is measured here
is that neither surface can have one written today.

**(c) AND (d) WERE CONSIDERED AND REJECTED.**

* **(c) keep the permit, add a `basis_declared: false` field beside it.**
  Rejected: a permit that requires the caller to read a second field to learn it
  is not a permit is a report with extra steps -- and the only in-package caller,
  `disclose`, acts on the absence of `refused`. This is the "exemption that makes
  the verdict true by declaration" the brief forbids, wearing a new field.
* **(d) check the basis only inside `disclose`, leaving `evaluate` alone.**
  Rejected: `evaluate` is the pure, browser-free gate, and it is what the census
  quotes and what a future caller will read. Splitting the truth between the
  pure function and its async wrapper is how this shipped in the first place --
  `disclose`'s docstring already claimed the ordering property that `evaluate`
  did not implement.

**WHAT (b) COSTS, stated plainly.** `/in/me/` presses are unavailable until a
basis is written for it. That is a real loss and it is the right one: the gate
was already going to refuse that press, and refusing it before the click is
strictly better than refusing it after. Census row 76 is re-filed accordingly in
section 6.

**WHAT (b) DOES NOT DO.** It only ever makes the gate refuse EARLIER. No press
that was permitted is now refused and no press that was refused is now
permitted; `/analytics/profile-views/` still presses, which is the positive
control in section 3.2.

### 1.3 The permit got more honest as well, which is not a free addition

A surviving pre-press permit now carries the basis kind and what still has to be
shown, derived rather than constant:

    /feed/                       {"basis": "sensitive",   "requires_counters": ["off_state"],
                                  "still_to_show": ["sensitive_counter_read",
                                                    "counters_unmoved", "closure_verified"]}
    /analytics/profile-views/    {"basis": "structural",  "requires_counters": [],
                                  "still_to_show": ["counters_unmoved", "closure_verified"]}

`still_to_show` was the same two-item constant for every surface. For a route (a)
surface it was incomplete: `sensitive_counter_not_read` is still reachable after
the press, and the permit now names the counter the caller's `read_counters` has
to return rather than letting it find out by pressing. **Nothing about this
relaxes a condition** -- it publishes a requirement the gate already enforced.

---

## 2. THE ZERO-CLICKS CONTROL, QUOTED FAILING AND THEN PASSING

`tests/test_press.py::test_a_surface_with_no_declared_basis_is_refused_before_it_is_pressed`.
It is the 2026-09-21 characterisation test INVERTED, exactly as that test's own
docstring instructed (*"WHEN THE ORDERING IS FIXED, INVERT THIS TEST -- DO NOT
DELETE IT"*), not a new file beside it. The load-bearing assertion is asserted
FIRST on purpose: everything else in the test is a statement about a verdict,
and this is the statement about the PAGE.

**RED, against `press.py` at `4c8d0f1`, verbatim:**

    >           assert page.clicks == [], (
    E           AssertionError: the gate clicked 'people' and refused afterwards:
    E           clicks=['[aria-expanded]']. The refusal is a pure function of the url
    E           and was available before any contact.
    E           assert ['[aria-expanded]'] == []
    E             Left contains one more item: '[aria-expanded]'
    tests\test_press.py:830: AssertionError

The same run took the two new condition-3 rows of the ordering test down with it,
one per affected surface:

    >       assert page.clicks == [], (condition, url, shape, page.clicks)
    E       AssertionError: ('condition 3', 'https://www.linkedin.com/search/results/people/',
    E                        '[aria-expanded]', ['[aria-expanded]'])
    >       assert page.clicks == [], (condition, url, shape, page.clicks)
    E       AssertionError: ('condition 3', 'https://www.linkedin.com/in/me/',
    E                        '[aria-haspopup]', ['[aria-haspopup]'])
    tests\test_press.py:518: AssertionError

    3 failed, 6 passed in 1.87s

**The full red, before any change to `press.py` -- eight failures, sixty-three
passes**, which is the other half of the control: the new tests fail, and they do
not fail by breaking everything. (This capture is of `tests/test_press.py` at the
moment the tests existed and `press.py` did not yet consult the basis table;
three further tests were added afterwards and are shown failing by mutation in
section 3.3, so the final file collects 74 cases rather than 71.)

    FAILED test_his_own_profile_is_admitted_and_a_third_party_is_not
    FAILED test_a_refused_press_never_touches_the_page[condition 3-no_sensitivity_basis0]
    FAILED test_a_refused_press_never_touches_the_page[condition 3-no_sensitivity_basis1]
    FAILED test_a_malformed_structural_basis_is_also_caught_before_the_press
    FAILED test_a_surface_with_no_declared_basis_is_refused_before_it_is_pressed
    FAILED test_every_refusal_is_classified_by_when_it_is_knowable[no_counter_reading]
    FAILED test_every_refusal_is_classified_by_when_it_is_knowable[no_sensitivity_basis]
    FAILED test_a_counter_reader_returning_none_cannot_pass_for_a_pre_press_permit
    8 failed, 63 passed in 1.42s

**GREEN, after the change:**

    tests/test_press.py tests/test_the_press_gate_cannot_witness_disclosure.py
    85 passed in 0.95s

And the gate re-measured on the four surfaces, same probe before and after:

    SURFACE                              BASIS        PRE-PRESS BEFORE    PRE-PRESS AFTER
    /in/me/                    [haspopup]  none        permitted           no_sensitivity_basis
    /search/results/people/    [expanded]  none        permitted           no_sensitivity_basis
    /feed/                     [expanded]  sensitive   permitted           permitted (+ requires_counters)
    /analytics/profile-views/  [expanded]  structural  permitted           permitted

---

## 3. WHAT `test_a_refused_press_never_touches_the_page` COVERED, BEFORE AND AFTER

### 3.1 Before: four addresses, two conditions

    (/article/new/,  [aria-expanded])  -> composer_or_editor     condition 1
    (/pulse/drafts/, [aria-expanded])  -> address_not_admitted   condition 1
    (/feed/, button:has-text("All filters")) -> shape_not_sanctioned  condition 2
    (/feed/, button)                   -> shape_not_sanctioned   condition 2

Four cases, **two conditions**, and both of those are evaluated before anything
is touched. The test asserted the right property over a row set that could not
fail on the branch that was broken.

### 3.2 After: eight parametrized rows, three conditions, plus two tests behind them

The row set is now `_REFUSED_BEFORE_ANY_CONTACT`, one row per condition rather
than one per address, with the condition written into the row so a gap is visible
on the page:

    condition 1   /pulse/drafts/        [aria-expanded]  address_not_admitted
    condition 1   /article/new/         [aria-expanded]  composer_or_editor
    condition 1   /in/another-person/   [aria-expanded]  address_not_admitted | third_party_surface
    condition 1   (url None)            [aria-expanded]  no_address
    condition 2   /feed/                button:has-text  shape_not_sanctioned
    condition 2   /feed/                button           shape_not_sanctioned
    condition 3   /search/results/people/ [aria-expanded] no_sensitivity_basis      <- NEW
    condition 3   /in/me/               [aria-haspopup]  no_sensitivity_basis       <- NEW

**CONDITION 4 IS ABSENT ON PURPOSE AND THAT IS A FINDING, NOT A GAP.** It has no
pre-press-derivable refusal by construction: `closure_verified` is a statement
about the state AFTER the press. A row set that "covers every condition" with
zero contact is therefore impossible, and saying so is worth more than faking it.

Two tests stand behind the row set:

* **`test_a_malformed_structural_basis_is_also_caught_before_the_press`** --
  condition 3's SECOND url-derivable refusal, `structural_argument_incomplete`,
  which was also taken after the click. The malformed entry is PLANTED with
  `mock.patch.object`, on `/notifications/` because it is admitted and declares
  no basis, so the plant is the only thing that changed. The committed table has
  no such row and `test_every_declared_structural_basis_carries_the_full_shape`
  exists to keep it that way, so manufacturing the fixture is the only honest
  route to the branch.
* **`test_every_refusal_is_classified_by_when_it_is_knowable`** -- and this is
  the actual repair to the blind spot.

### 3.3 The repair to the blind spot is the inventory, not the two new rows

The ordering test could only ever cover inputs somebody thought to write down.
`no_sensitivity_basis` shipped because nobody did. So `WHEN_KNOWABLE` now
classifies **every refusal `press.py` can emit** into a closed three-value
vocabulary, and `_refusal_reasons_in_source()` extracts the reasons **by AST**
from the `_refuse()` call sites and asserts the dict is EXACTLY complete in both
directions -- an unclassified reason fails, and a stale entry for a reason the
module no longer emits fails just as loudly.

    before_any_contact  (8)  no_address, address_not_admitted, composer_or_editor,
                             third_party_surface, shape_not_sanctioned,
                             no_sensitivity_basis, structural_argument_incomplete,
                             no_counter_reader_supplied
    after_a_read        (1)  shape_absent_on_this_page
    after_the_press     (8)  no_counter_reading, counter_unreadable,
                             no_counter_prices_this_press, counter_moved,
                             sensitive_counter_not_read, closure_unverifiable,
                             not_restored, press_failed

**THE MIDDLE VALUE IS NOT PADDING.** A gate may READ a page without pressing it,
and reading is not what the ordering rule forbids; what it forbids is ACTING on a
refusal that was already derivable. `shape_absent_on_this_page` asks the page for
a count and clicks nothing.

**AND THE LOAD-BEARING ASSERTION IS THE ONE ON `after_the_press`.** Each such row
is driven to its refusal, and then the PRE-PRESS verdict on the same input must
be a permit -- the mechanical form of *"this one genuinely could not have been
taken earlier"*. Reclassify `no_sensitivity_basis` back to `after_the_press` and
that assertion is what fails. The classification cannot be satisfied by relabelling.

**SIXTEEN OF THE SEVENTEEN ARE REACHED BY A REAL INPUT** in `_REACHES`,
including `press_failed` (a `RaisingPage` whose click raises) and the counter
family (five readers returning moving, unreadable, disjoint, incomplete and
`None` readings). The seventeenth,
`structural_argument_incomplete`, needs a PLANT rather than an input and is
driven by its own test. `test_every_classified_refusal_is_actually_exercised_somewhere`
asserts that `_REACHES` plus that one named plant is EXACTLY `WHEN_KNOWABLE`,
in both directions -- because a classification nobody drives is a claim, not a
check.

**ALL THREE NEW INSTRUMENTS SHOWN FAILING BY MUTATION**, restored between each,
because a check that cannot fail certifies nothing:

    THE INVENTORY (AST vs WHEN_KNOWABLE)
      BASELINE                                                  GREEN
      drop no_sensitivity_basis from WHEN_KNOWABLE              RED  "unclassified refusals: ['no_sensitivity_basis']"
      RESTORED                                                  GREEN
      add an entry for a reason the module cannot emit          RED  "stale entries for refusals the module no longer emits"
      RESTORED                                                  GREEN

    THE CLASSIFICATION, on the row that matters
      BASELINE [no_sensitivity_basis]                           GREEN
      reclassify no_sensitivity_basis -> after_the_press        RED  "classified after_the_press and no press happened --
                                                                     it is derivable earlier and must be taken earlier."
      RESTORED                                                  GREEN

    THE COVERAGE (_REACHES + the plant vs WHEN_KNOWABLE)
      BASELINE                                                  GREEN
      drop counter_moved from _REACHES                          RED  "classified but never driven: ['counter_moved']"
      RESTORED                                                  GREEN
      add a driven reason nobody classified                     RED  "driven but not classified: ['invented_refusal']"
      RESTORED                                                  GREEN

The middle block is the one to read. **The classification cannot be satisfied by
relabelling**: moving `no_sensitivity_basis` back to `after_the_press` -- which
is what the shipped code did -- makes the test fail with the sentence that names
the rule.

### 3.4 And the two moments are held to the same answer

`check_basis` (pre-press) and `check_counters` (post-press) both decide the two
url-derivable refusals. Two copies of one refusal drift, so the reasoning lives
in `press._basis_refusal` and
`test_the_two_moments_give_the_same_reason_for_the_same_surface` asserts the
callers still agree: same REASON and same terminality on three basis-less
surfaces, and the `why` texts DELIBERATELY different -- the post-press form also
reports what was read at both ends, which is evidence the pre-press form does not
have. A difference of evidence, not of rule; if the two texts were identical that
evidence had been dropped, and the test says so.

### 3.5 A branch that had never been shown failing, found while building the inventory

`third_party_surface` is **unreachable through any real url**. Measured:

    /in/another-person/                       is_read_url=False -> address_not_admitted
    /in/another-person/detail/                is_read_url=False -> address_not_admitted
    /in/another-person/recent-activity/all/   is_read_url=False -> address_not_admitted

The read allowlist refuses every third-party profile spelling first, so
`check_address` never reaches its own third-party branch. That is real defence in
depth -- and it also means the branch had never been shown capable of failing.
`test_the_third_party_refusal_fires_on_its_own_merits` did not catch this: it
asserted `refused in {address_not_admitted, third_party_surface}`, a SET satisfied
by the first of the two, and then asserted a CONSTANT (`"me" in _SELF_SEGMENTS`)
rather than the branch. Its docstring's own words -- *"the third-party branch is
never the thing standing"* -- were true of itself.

**REPAIRED:** the allowlist is now STIPULATED with `mock.patch.object`, which is
what "on its own merits" was always supposed to mean, and both halves are
asserted -- a third party refuses, and HIS OWN profile still passes, so the branch
is shown discriminating on WHO THE MEMBER IS rather than on the `/in/` segment.

---

## 4. WHAT CHANGED IN `press.py`

| change | why |
|---|---|
| `_basis_refusal(basis, *, read_at_both_ends=None)` | condition 3's url-derivable half, in ONE place. It is consulted from two moments, and a refusal whose reasoning is written twice is a refusal whose copies drift apart. `read_at_both_ends` is the only difference between them and it is a difference of EVIDENCE, not of rule. |
| `check_basis(url)`, public and pure | the pre-press form. Returns the basis kind and, for route (a), the counters the surface declares sensitive. |
| `check_counters` delegates to `_basis_refusal` | identical behaviour; the two refusal texts are no longer duplicated. **Post-press ordering deliberately unchanged**: `counter_moved` is TERMINAL and is a measurement of a real write, so once readings exist it still outranks a missing basis. The strongest true thing to say about a press that moved an outward counter is that it was a write, not that the surface lacked paperwork. |
| `evaluate(..., already_pressed=False)` | the moment is SAID, not inferred. See section 7.1. |
| `evaluate`'s pre-press branch runs `check_basis` | the ruling, implemented. |
| `disclose` passes `already_pressed=True` | ditto. |
| the witness MISS text | section 7.3. |
| module docstring: a new section | the ordering rule, what it does NOT do, the `/in/me/` consequence, and the second instance. |

**`SANCTIONED_SHAPES`, `SENSITIVITY_BASES`, `_COMPOSER_MARKERS`, `_SELF_SEGMENTS`,
`WITNESS_SELECTORS` and `_STRUCTURAL_REQUIRED` are byte-identical.** No allowlist
grew, no refusal was removed, and no condition was relaxed. The diff adds
refusals earlier and nothing else.

---

## 5. THE IMPACT GATE

Run on the staged index. **IT REFUSED, AND EVERY RED WAS REAL.** Quoted with its
own scope lines verbatim, because a gate that claims more than it ran destroys
the trust that made it useful.

**THE CONTROL FIRST -- an empty index is a LOUD event here, not a silent pass:**

    impact-gate: NOTHING WAS STAGED, SO NOTHING WAS CHECKED. This is not a
    pass. Stage the change first, or pass --against <ref> to measure a range
    instead of the index.

**THE RUN.** There is no `NOT CHECKED` line on this one, and the reason is the
finding: the change was too broad to scope, so the gate widened and ran
everything, which means **nothing went unchecked**.

    impact-gate: 5 changed path(s) -> 133 SELECTED + 15 corpus-wide = 133 test file(s).
    ...
      + 15 CORPUS-WIDE guard(s), run unconditionally -- they sweep the tracked set and take no input from the diff,
        so no impact analysis can ever select them. Omitting them is how a fast gate ships a real name.

      WIDENING TO THE FULL SUITE, because the impact set is 133 of 204 test files (65%), at or above the 45% line where running everything costs about the same and answers more.

    REFUSED: a test this change can reach is RED.
        FAILED tests/test_the_audit_index_is_derived.py::test_the_committed_index_is_what_the_corpus_derives
        FAILED tests/test_the_audit_index_is_derived.py::test_there_is_a_corpus_and_the_index_covers_all_of_it
        FAILED tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged
        FAILED tests/test_gap_rows_on_refused_addresses.py::test_gap_rows_on_refused_addresses_is_pinned
        FAILED tests/test_gap_rows_on_refused_addresses.py::test_the_check_can_convict_and_can_clear
        FAILED tests/test_probe_controls_are_never_decorative.py::test_probe_corpus_baseline_is_an_exact_mapping
        6 failed, 7800 passed, 8 skipped, 1 xfailed in 1096.81s (0:18:16)

**SO THE `NOT CHECKED` LINE THIS BRIEF ASKED FOR DOES NOT EXIST FOR THIS RUN,
and saying that is more useful than quoting the line from a different one.** The
gate prints `NOT CHECKED: N of 204 test files` only when it runs a SCOPED plan.
At 65% of the suite it took its own documented branch and ran all 204. For
contrast, the wave immediately before this one was scoped and printed:

    NOT CHECKED: 177 of 204 test files (86.8% of the suite by file).
    ...roughly 4398 of 6094 tests unrun (72.2%)

**AND THAT 86.8% IS WHERE TWO OF MY SIX REDS CAME FROM** -- see 5B. Both were
red at HEAD, and the scoped gates that ran before mine never reached them.

**WHAT HAPPENED TO EACH RED.** Four fixed, one fixed on its behalf, one
declined and reported:

| red | mine? | disposition |
|---|---|---|
| `test_the_audit_index_is_derived` x2 | YES | `_audit/INDEX.md` is DERIVED and my new report made it stale. Regenerated with `scripts/build_audit_index.py --write` (209 tracked documents), never hand-merged. |
| `test_a_correction_is_findable_from_the_claim` | YES | a new candidate pair from my own section 10. Triaged -- see 5A. |
| `test_gap_rows_on_refused_addresses::...is_pinned` | NO | pin stale since `c500cf9`. Re-pinned 5 -> 4 with the row named. See 5B. |
| `test_gap_rows_on_refused_addresses::...can_convict_and_can_clear` | NO | the control held a SECOND COPY of the pin. Derived instead. See 5B. |
| `test_probe_controls_are_never_decorative` | NO | another wave's probe. **Diagnosed and deliberately NOT fixed** -- see 5B. |

**AFTER THE FIXES**, each re-run individually:

    tests/test_a_correction_is_findable_from_the_claim.py
    tests/test_the_audit_index_is_derived.py            46 passed in 19.05s
    tests/test_gap_rows_on_refused_addresses.py          3 passed in 0.82s
    scripts/check_gap_rows_on_refused_addresses.py --demonstrate-red
                                                         ALL THREE REDS FIRED

**THE GATE WAS THEN RUN AGAIN ON THE CORRECTED TREE**, full suite once more, and
the count came down to exactly the one I declined plus one new candidate pair
this report's own section 5 had just created:

    impact-gate: 8 changed path(s) -> 138 SELECTED + 15 corpus-wide = 138 test file(s).
      WIDENING TO THE FULL SUITE, because the impact set is 138 of 204 test files (68%), ...

    REFUSED: a test this change can reach is RED.
        FAILED tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged
        FAILED tests/test_probe_controls_are_never_decorative.py::test_probe_corpus_baseline_is_an_exact_mapping
        2 failed, 7804 passed, 8 skipped, 1 xfailed in 813.70s (0:13:33)

**6 -> 2, and 7804 passing.** The four census and index reds are gone at
full-suite scope, not merely in isolation.

**THE REMAINING CORRECTION PAIR WAS THIS SECTION.** Writing "a derived artifact
went out of date and was rebuilt" puts that vocabulary two lines from a citation,
so the scan produced a pair. It is triaged with a shape this dict had not carried
before -- **a derived artifact cannot be corrected, only regenerated** -- and the
entry states what would make it wrong. After that entry:

    tests/test_a_correction_is_findable_from_the_claim.py
    tests/test_gap_rows_on_refused_addresses.py
    tests/test_the_audit_index_is_derived.py
    tests/test_press.py                                    123 passed in 57.15s

**LEAVING EXACTLY ONE RED, 5B.3, DECLINED ON PURPOSE.**

**THIS SECTION'S OWN TEXT WAS WRITTEN AFTER THOSE RUNS**, which is unavoidable
for any report that quotes its own gate -- the recursion has to stop somewhere
and this is where. The tree that was committed differs from the one gate 4
measured by exactly two things: the triage entry above and this paragraph. Both
were re-verified by the four guards named above rather than assumed, and the
gate was run once more after the commit for the record.

---

## 5B. TWO REDS THAT WERE NOT MINE, AND THE ONE I DECLINED TO FIX

Both were red at HEAD. Neither is caused by anything this wave changed, and both
were invisible to the scoped gates that ran before mine.

### 5B.1 `test_gap_rows_on_refused_addresses` -- FIXED, because the remedy is what the check itself prescribes

**PROOF IT IS NOT MINE, BEFORE ANYTHING ELSE.** The check reads the four census
slices plus `readonly.py`. I edited exactly one of those, `network.md`. Running
the check's own row walk -- shipped `ADDR` regex, shipped gate -- over HEAD's
`network.md` and mine:

    network.md REFUSED-SUBSTRING findings   HEAD=18   MINE=18
    lost by my edit: []
    gained by my edit: []
    GAP-only  HEAD=2  MINE=2

**Zero difference.** My census edit is a no-op for this check, so the red
predates me.

**WHICH ROW LEFT, AND WHETHER IT WAS RESOLVED OR HID.** The pin `5` was set at
`16941f0` (2026-09-20 19:40); the check now measures 4. Walking both census
snapshots names the row:

    AT THE PIN (16941f0): 5 distinct GAP rows
       M C88   Choose whether members can mention, tag or collaborate with you
       M M11 / N A3 / N A5 / P D25
    AT HEAD             : 4 distinct GAP rows
       M M11 / N A3 / N A5 / P D25
    LEFT THE SET : ['M C88']    JOINED : []

**THE DISTINCTION THAT DECIDES THE REMEDY, and it is the one a bare count
cannot make.** A row can leave this set two ways: its STATE moves out of GAP
(resolved -- re-pin), or its backticked ADDRESS is edited away while it is still
GAP (the check went BLIND -- re-pinning would hide a real offender). Measured on
both snapshots:

    AT THE PIN: STATE='GAP'             addresses seen: ['/mypreferences/d/categories/',
                                                         '/mypreferences/d/categories/visibility']
    AT HEAD   : STATE='EXCLUDED-RULED'  addresses seen: ['/mypreferences/d/categories/',
                                                         '/mypreferences/d/categories/visibility']

**RESOLVED, not blind** -- the same two addresses are visible at both ends, and
the state moved. Closed by `c500cf9` (the write-ceiling wave, 2026-09-21 11:15,
*"5 of 157 write-direction GAP rows close"*), which did not re-pin here.

**FIXED:** `EXPECTED_GAP_ROWS` 5 -> 4, with the row, the commit and the
resolved-not-blind evidence written into the constant's own docstring, because a
re-pin without a named row is just fitting the number to today.

### 5B.2 The same red's second half -- ONE NUMBER LIVING IN TWO PLACES

`test_the_check_can_convict_and_can_clear` was failing for a different reason,
and it is worth its own paragraph because the failure mode is instructive:

    RED 2 -- THE CHECK MUST FAIL ON THE PLANTED CORPUS
      CONTROL BROKEN: it PASSED a corpus containing a planted
      offender, so it cannot fail and certifies nothing.

The control plants one offending row into a copy of the census and requires the
check to fail. It called `run(expect_gap=5)` -- **a hardcoded second copy of the
pin.** When the real count went 5 -> 4, the literal `5` came to match the
PLANTED corpus exactly, so the control passed its own planted offender and
reported ITSELF broken.

**A CONTROL WHOSE EXPECTATION IS A COPY OF THE THING IT CONTROLS FAILS IN THE
DIRECTION THAT LOOKS LIKE ITS OWN FAULT**, and the obvious repair -- change the 5
to a 4 -- reinstates the duplication and schedules the next one.

**FIXED BY DERIVATION**, one line: `run(expect_gap=len(keys) - 1)`. That is
exactly the count without the plant, and it is not an assumption -- RED 1
immediately above asserts the planted refused row IS in `keys` and RED 3
immediately below asserts the planted ADMITTED row is NOT, so precisely one
planted row joins the set. The two assertions that bracket the line are what
make it derivable.

**AND THE DERIVATION WAS SHOWN NOT TO WEAKEN THE CONTROL**, by mutating the
shipped `run` underneath it:

    BASELINE, unmutated                     ok    it FAILED and it NAMED the planted row
    MUTATION 1 -- run() never fails         CONTROL BROKEN: it PASSED a corpus containing a planted offender
    RESTORED                                ok    it FAILED and it NAMED the planted row
    MUTATION 2 -- fails but names nothing   CONTROL BROKEN: it failed but never named J 9801
    RESTORED                                ok    it FAILED and it NAMED the planted row

### 5B.3 `test_probe_controls_are_never_decorative` -- DIAGNOSED, DELIBERATELY NOT FIXED

    GAINED (a NEW never-branched control -- do NOT add it here to clear the red;
    branch on its result, or if it is a genuinely decorative reading that was
    reviewed and accepted, add it to the baseline with a one-line reason):
      _probe_all_filters_disclosure_shape.py:544 _print_shape() -> 'shape'
      _probe_all_filters_disclosure_shape.py:559 _print_shape() -> 'index'
      _probe_all_filters_disclosure_shape.py:594 _print_payload() -> 'index'
      _probe_all_filters_disclosure_shape.py:716 main() -> 'wait'
    LOST: (none)

**NOT MINE:** neither `scripts/_probe_all_filters_disclosure_shape.py` nor
`scripts/probe_controls_known_decorative_baseline.json` appears in my diff, so
the drift is between two files I did not touch. It arrived with the-press wave
at `4c8d0f1`, whose gate was scoped and printed `NOT CHECKED: 177 of 204 test
files` -- this guard was among the 177.

**READ, SO THE NEXT WAVE DOES NOT RE-DO IT.** All four sites are
report-formatting: `_print_shape` and `_print_payload` are `say(...)` loops
rendering an already-gated record, and line 716 is `wait = one["panel"]
["panel_wait"] or {}` immediately printed -- the branch that matters, `_gate(one,
...)`, runs three lines earlier at 713. The detector's `control` marker is
firing on the literal row label `"-control-"` in those format strings.

**WHY I STOPPED THERE.** The two remedies are opposite in kind. Re-pinning
5B.1 RESTORES a control to working order; adding to this baseline SUPPRESSES a
detector's finding, and the baseline's own contract is that each entry records a
REVIEWED acceptance by somebody who owns the probe. I did not write that probe,
and I am forbidden the browser it runs against, so I can say the four readings
are decorative from the source but I cannot certify the acceptance. **Suppressing
a finding on another wave's behalf is the one edit a passing gate is not worth.**

---

## 5A. ONE FILE WAS TOUCHED OUTSIDE THE BRIEF'S LIST, AND WHY

The brief's list was `linkedin_server/press.py`, `tests/test_press.py`, this
report, and `_audit/_census/*.md` only on a genuine state change. **Four more
files were edited, and none of them is a tidy-up:**

| file | why it was unavoidable |
|---|---|
| `tests/test_a_correction_is_findable_from_the_claim.py` | the census edit turns it RED until the correction is DECLARED or TRIAGED. Below. |
| `_audit/INDEX.md` | DERIVED. A new audit document makes it stale, and the brief says to regenerate it with `scripts/build_audit_index.py --write` and never hand-merge. Done. |
| `tests/test_gap_rows_on_refused_addresses.py` | a red at HEAD that blocks every wave's gate. 5B.1. |
| `scripts/check_gap_rows_on_refused_addresses.py` | the same red's second half, one derived line. 5B.2. |

The last two are outside this wave's subject entirely and are flagged here
rather than folded in quietly. The correction-test edit:

    FAILED test_every_candidate_pair_is_declared_or_triaged
    2 candidate correction(s) nobody has triaged.

Both pairs are resolved the way that file's own precedents resolve them:

* **`refuse-before-the-click.md` -> `network.md` is DECLARED**, with a
  `**CORRECTS:**` marker at the top of this report and the matching
  `**CORRECTED BY:**` line in `network.md`'s header block, beside the five
  already there. **That is the substantive half**: a reader who arrives at
  row 76's old claim can now find the document that refutes it, which is the
  defect that file exists to prevent.
* **`network.md` -> `refuse-before-the-click.md` is TRIAGED** onto
  `NOT_A_CORRECTION` as the SHADOW of the declared arrow -- row 76 cites this
  report as the SOURCE of its own in-place correction and withdraws nothing from
  it. The entry states what would make it wrong, as its neighbours do. The
  reverse pair cannot be declared: a census row is one line of a markdown table
  and a marker must OPEN its line.

Green after: `tests/test_a_correction_is_findable_from_the_claim.py 13 passed`.

---

## 6. THE CENSUS ROW THAT CHANGED, AND TWO THAT DID NOT

**EDITED: `_audit/_census/network.md` row `76`** -- "Copy your personal Follow
link for use off LinkedIn". **THAT IS THE ONLY ROW ID THIS WAVE TOUCHED.**

**AND ITS STATE DID NOT MOVE: GAP BEFORE, GAP AFTER.** The brief said to touch a
census row only on a genuine state change, so the reason for editing anyway is
stated rather than assumed: the row carried a claim that is FALSE at HEAD, and
its BLOCKER -- the field that decides whether a future wave can move it -- was
wrong in the direction that costs a wave. That is the same standard the
write-ceiling and all-filters waves used on this file hours earlier, both of
which corrected evidence cells in place and wrote NO STATE MOVED. If the rule is
read strictly as "state column only", this edit is outside it and is flagged
here rather than buried.

It is the ONLY census row in the repository that quotes `permitted_to_attempt`,
and its claim was false on disk before this wave touched anything:

    CENSUS CLAIM   /in/me/ + [aria-haspopup] is PERMITTED; pre-press
                   permitted_to_attempt: true; with a counter unmoved at both
                   ends it returns permitted: true, priced_by: [...]
    RE-MEASURED    no_sensitivity_basis, at BOTH ends

**DATED RATHER THAN BLAMED, because the row was true when written.** `git log -S`
on both sides:

    1f5985d  2026-09-19 10:53  census(press): four rows re-filed on what the
                               shipped gate actually returns, not on one label
    61e3e01  2026-09-19 11:56  press: readability no longer prices a press, and
                               the verdict says which way it did

**Sixty-three minutes.** The claim landed at 10:53 and was falsified at 11:56 by
the ruling that made readability stop pricing a press. Nobody re-ran the row.
That is not a wrong reading -- it is a reading with a timestamp, quoted after its
subject moved, which is this repository's own `relayed-measurements-go-stale`.

The row is also **re-filed from BLOCKED ON EXECUTION to BLOCKED ON A RULING**,
with the circularity from section 1.2 written into it, because the difference
decides whether a future wave can move it: no counter reader will ever move this
row, and a wave dispatched to "just run it with a counter reader" would burn
itself finding that out.

**NOT EDITED, and each says why.**

* **`messaging-and-content.md` row `C72`** -- claims `/feed/` + `[aria-haspopup]`
  refuses at condition 3 with `no_counter_prices_this_press`. **RE-RUN AND STILL
  EXACT**, same refusal, same wording. No change.
* **`network.md` rows `133` and `134`** -- both quote a verdict verbatim:
  `{"permitted": true, "pressed": true, "priced_by": ["invitations",
  "notifications_unread"], "shape": "[aria-expanded]"}`. **`permitted` and
  `pressed` still hold. `priced_by` does not**: `/analytics/profile-views/` is a
  STRUCTURAL basis today, so the verdict now carries `basis: "structural"` and
  `priced_by: []`. **Same sixty-three-minute window** -- the press was taken at
  ~11:32 and the basis table landed at 11:56, twenty-four minutes later. **NOT
  EDITED BY THIS WAVE**: the rows' disposition (GAP) is unchanged, my change does
  not touch that surface, two waves are live, and the correction belongs to
  whoever owns the basis-table ruling. **The replacement value is stated here so
  the edit is one line when somebody takes it.**

---

## 7. THREE THINGS THIS WAVE WAS NOT SENT FOR, ALL IN `press.py`

### 7.1 A counter reader returning `None` disarmed conditions 3 AND 4, and reported a permit

**THE WORST OF THE THREE, and the same root cause: a moment inferred from its
inputs.** `evaluate` decided it was being called BEFORE a press from the absence
of counter readings -- `before is None and after is None`. A `read_counters` that
returns `None` reproduces exactly that shape AFTER a real click. Measured at
`4c8d0f1` against the repo's own fake:

    verdict : {"permitted_to_attempt": true, "pressed": false,
               "still_to_show": ["counters_unmoved", "closure_verified"],
               "witness": {"disclosed": false, ...}}
    clicks  : ['[aria-expanded]']
    keys    : ['Escape']

**This is worse than refusing late.** The reported defect at least refuses; this
one does not refuse at all. A caller testing `verdict.get("refused")` sees `None`
and banks a press that was never priced and never checked for closure -- on a
verdict whose own attached witness says the press happened.

**REACHABILITY, stated honestly:** the one live probe that calls `disclose`,
`scripts/_probe_first_sanctioned_press.py`, builds its reader to always return a
dict, so this could not have fired there. It is a hole in the CONTRACT, not a
past incident: `read_counters` is documented as returning "a mapping of counter
name to int-or-None", and a caller writing `async def read(): pass` silently
disarms two conditions.

**FIXED** by `already_pressed`, a keyword that SAYS which moment it is instead of
inferring it, and pinned by
`test_a_counter_reader_returning_none_cannot_pass_for_a_pre_press_permit`, which
was red before the change and asserts both halves: the verdict is now
`no_counter_reading`, and the click IS still recorded -- because the defect was
never that the click occurred, it was that the verdict denied it had.

### 7.2 `structural_argument_incomplete` was the second url-derivable refusal

The brief named one. Enumerating `check_counters`' branches found two: a
structural basis missing any of `why` / `bound` / `refuters` is decided from the
closed table keyed by surface, so it is as much a pure function of the url as
`no_sensitivity_basis` is, and it was taken after the click for the same reason.
Fixed by the same `check_basis` call; covered by
`test_a_malformed_structural_basis_is_also_caught_before_the_press` (section 3.2).

### 7.3 The witness asserted permission it cannot see

`witness_verdict` is handed two counts and, at most, the control's own
`aria-expanded`. It never sees the verdict. Its MISS text nevertheless read:

    "That is a MISS rather than a failure: the press was permitted and safe,
     and it disclosed nothing this set can see."

and the module docstring is emphatic that **the witness is attached to REFUSALS
TOO** -- so that sentence shipped on refusals, saying the opposite of the verdict
it rode beside. Measured on the section 7.1 refusal, where a press refused for
`no_counter_reading` came back carrying "the press was permitted and safe".

**A surface may not print a claim it cannot derive.** The text now says *"whatever
the verdict decided, this press disclosed nothing the witness set can see"*, and
`test_the_witness_never_asserts_permission` asserts the property about the
FUNCTION rather than one call site: no reading it can return may contain a
permission word. Shown failing against `4c8d0f1`:

    E   AssertionError: the witness claimed 'permitted' in {'disclosed': False,
    E   'moved': [], 'witnessed_by': ['menus'], 'why': 'nothing this witness
    E   counts changed between the press and the dismissal. That is a MISS rather
    E   than a failure: the press was permitted and safe, and it disclosed
    E   nothing this set can see.'}

and passing after. The only thing the pre-existing
`test_a_miss_is_reported_as_a_miss_and_not_as_a_failure` pinned about that string
was that it contains "miss", so nothing was weakened.

---

## 8. OTHER GATES IN THIS PACKAGE THAT DECIDE AFTER THEY ACT

**REPORTED, NOT FIXED**, per the brief. The scan is mechanical and stated so it
can be re-run: inside one function body, a PAGE-MUTATING verb (`click`, `fill`,
`type`, `goto`, `select_option`, `check`, `set_input_files`, `keyboard.press`,
...) at a line BEFORE a REFUSING construct (a `raise`, or a call whose name
contains `refuse`/`assert_`/`check_`/`guard`/`require`/`verify`/`permitted`/
`is_read_url`/`writes_enabled`/`evaluate`). Over `linkedin_server/*.py`:

    32 functions match the shape.

Triaged by reading each one:

| class | n | verdict |
|---|---|---|
| `goto` -> `assert_not_authwall` / `require_rows` / `raise` in `server.py` | 21 | **INHERENT.** An auth wall is not knowable without navigating, and the `goto` IS the read. Measurements, not late gates. |
| the same shape in `writes.py::_load` and `auth.py::login_via_browser` | 2 | **INHERENT**, same argument. |
| `browser.py::start`, `::_page`, `::goto` -- a launch or navigation then a `raise` | 3 | **INFRASTRUCTURE.** The raise reports that the launch or navigation failed. Nothing is being permitted or refused. |
| `press.disclose` | 1 | **THE DEFECT.** Fixed by this wave. |
| `writes.perform` | 1 | **CLEAN.** `writes_enabled()` fires at line 8320, **358 lines and one guard block before** the first mutation at 8678. `_verify_after` at 8818 is a post-act verification by design. |
| false positives | 4 | `preflight.assert_ready`, `profile_version.assert_no_downgrade`, `job_collections.collection_url` (Playwright's checkbox verb `check` collides with this package's `check()` functions) and `dom.read_invitation_surface` (Playwright's `page.evaluate` collides with `press.evaluate`). No page is mutated in any of the four. |

**THE ONE WORTH A SEPARATE PARAGRAPH, and it is a different shape:**
`dom.activate_messaging_filter`, the package's only other click on a read path.
It does NOT appear in the scan, correctly -- `assert_permitted_filter` raises
before any locator exists and the `count != 1` check returns before the click, so
it decides first. But its own docstring writes a consequence nobody implemented:

> *"If activating a pill turns out to move the page, that is a finding rather
> than a detail: it would mean the control does more than filter, and **the read
> classification that permits this click would no longer hold**."*

It detects exactly that, returning `navigated: page.url != before` -- **and
nothing anywhere acts on it.** Grepped across `linkedin_server/`, `tests/` and
`scripts/`: the only consumer is `test_a_thread_id_never_leaves_the_module.py`,
asserting `navigated is False` for a same-url case. **A condition the code names
as permission-invalidating is measured, returned, and never enforced.** That is
not the act-then-decide shape; it is a gate that was described and never built.
Not this wave's file, so: reported.

**THE SCANNER IS DECLARED DISPOSABLE, and its rule is written out above rather
than filed, deliberately.** It is a one-shot triage aid with a 4-in-32 false
positive rate that a human has to read anyway -- `check` and `evaluate` are both
Playwright verbs AND this package's own function-name conventions, and no
tightening fixes that without losing real hits. **Registering a check whose
output always needs a human is how a register stops meaning anything.** What is
worth keeping is the QUESTION, and the durable form of it now lives in
`tests/test_press.py::WHEN_KNOWABLE`, which asks it of one module mechanically
and cannot be satisfied by relabelling.

---

## 9. WHERE DISK DISAGREED WITH THE BRIEF

The brief invited this and it was right to. Five items, all verified on disk.

1. **"THE NAIVE CHANGE BREAKS `test_his_own_profile_is_permitted_and_a_third_party_is_not`,
   WHICH PINS `permitted_to_attempt is True` FOR `/in/me/`."** True, and the test
   is now RENAMED to `..._is_admitted_and_a_third_party_is_not` because the old
   name asserted something that was never a fact about the self/third-party
   split. That split lives entirely in `check_address`; the permit read True only
   because the gate did not consult the basis table. The test now asserts
   `check_address(...).get("admitted") is True` AND that the refusal standing is
   `no_sensitivity_basis`, NOT-YET, naming its own remedy. **Narrower, not
   weaker** -- it pins three facts where it pinned one.

2. **"(a) IS LIKELY THE RIGHT ANSWER."** Right as policy, unavailable as an
   action: writing a basis for `/in/me/` requires claiming the absence of exactly
   what only the authorised press can read (section 1.2). Recorded as a RULING
   REQUEST with its obstacle stated, rather than answered by writing the
   argument anyway.

3. **THE BRIEF NAMED ONE URL-DERIVABLE REFUSAL. THERE ARE TWO.**
   `structural_argument_incomplete` is the second (section 7.2).

4. **THE DEFECT HAS A WORSE SIBLING THE BRIEF DID NOT KNOW ABOUT** (section 7.1):
   a `None`-returning counter reader makes the gate click, skip conditions 3 and
   4 entirely, and return a permit with no refusal at all.

5. **THE CENSUS ROW THE BRIEF POINTED AT WAS ALREADY FALSE, AND NOT BECAUSE OF
   THIS DEFECT** (section 6). `/in/me/` + `[aria-haspopup]` had not been
   `permitted` since 11:56 on 2026-09-19, sixty-three minutes after the row was
   written.

**AND ONE THING THE BRIEF ASKED FOR THAT CANNOT EXIST.** "Widen
`test_a_refused_press_never_touches_the_page` so it covers a refusal at EVERY
condition." Condition 4 has no pre-press-derivable refusal by construction
(section 3.2), so no zero-contact row can exist for it. The request is answered
by `WHEN_KNOWABLE` instead, which covers all seventeen refusals across all four
conditions and requires each `after_the_press` one to prove it could not have
been hoisted.

---

## 10. WHAT THIS WAVE DID NOT DO

* **Nothing live.** No browser, no port 9224, no navigation, no click, no key on
  any real page. Every measurement is `FakePage` or a pure function.
* **No basis was written** for `/in/me/` or `/search/results/people/`. Writing one
  is a RULING with a measured blast radius, and section 1.2 says why neither can
  be argued today.
* **No allowlist grew.** `SANCTIONED_SHAPES`, `SENSITIVITY_BASES` and
  `_COMPOSER_MARKERS` are byte-identical.
* **Census rows 133 and 134 were not edited**, with the replacement value stated
  in section 6 for whoever owns them.
* **`dom.activate_messaging_filter`'s unenforced `navigated` finding was not
  fixed** (section 8).
* **`_audit/2026-09-21-the-all-filters-press.md` was not rewritten.** It is a
  dated record and it was accurate; this file implements its handover rather than
  correcting it. No `CORRECTS:` marker names it, for the same reason.
* **No instrument was filed.** The act-then-decide scanner is declared disposable
  with its rule written out (section 8); the durable instrument this wave adds is
  `WHEN_KNOWABLE` in `tests/test_press.py`, and it is shown failing three ways.
* **Nothing was pushed.**

---

## 11. WHAT WOULD MOVE THE TWO BLOCKED SURFACES

Both are now blocked on the SAME thing and it is a ruling, not a run.

| surface | what it needs | the obstacle, measured |
|---|---|---|
| `/in/me/` | a `SENSITIVITY_BASES` entry | route (a): no counter is known sensitive to a profile overflow press. route (b): the argument must deny an outward control in a region that **cannot be read unpressed** (census row 76: 1 `[aria-haspopup]`, zero `[role=menu]`/`[role=menuitem]`, built on demand). Circular. |
| `/search/results/people/` | a `SENSITIVITY_BASES` entry | condition 2 refuses the `All filters` control TERMINALLY anyway (`_audit/2026-09-21-the-all-filters-press.md`), so a basis would not by itself enable that press. The surface draws 8 `[aria-expanded]` and 0 dialogs/menus/menuitems/listboxes shut, so what any of them opens is also unread. |

**A RULING REQUEST WITH A STATED OBSTACLE, not a queued task.** Anyone taking it
should notice that both obstacles have the same shape: the structural argument
needs a fact about the expanded region, and only the press it would authorise can
produce that fact. The analytics entry escaped it because its surface *addresses
no one* -- an argument about the PAGE rather than about what the control opens.
Neither of these two surfaces can make that argument: one is a profile, the other
lists people.
