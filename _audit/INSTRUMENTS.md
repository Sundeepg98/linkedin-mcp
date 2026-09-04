# The instrument register

**An instrument enters this file only if it has been SHOWN FAILING.** A check
that cannot fail certifies nothing, and a register of such checks is worse than
no register: it manufactures confidence at scale. Every entry below names the
mutation that killed the guard and where the guard lives, so a reader can
re-plant it rather than trust this file.

This register was created on 2026-09-04 because a session found THREE checks
that could not fire, in one wave, and filing them in a scratch progress file
would have taught nobody anything durable. The three are section 1. The
method that found them is section 2.

**How a red-proof is run here.** Never in the live tree -- several agents write
`linkedin_server/` concurrently and mutating a shared file even briefly can be
picked up or clobbered. Copy `linkedin_server`, `tests`, `scripts` and
`pytest.ini` to a scratch directory, **print `linkedin_server.__file__` and
confirm it resolves under the copy before touching anything**, plant ONE
mutation, run ONLY the selector that should die, restore by re-copying that one
file, repeat. Finish on a clean control run.

---

## 1. THE THREE GUARDS THAT COULD NOT FIRE

### 1.1 `NEVER-EXECUTED-BUT-REPORTED-GREEN`

**The most expensive shape in this codebase, and it was found in the work
written to avoid it.**

`tests/test_tools.py::test_a_checkbox_filter_emits_its_parameter_only_when_it_is_on`
was written, run, and reported green. It had never executed: the `-k` selector
used to "verify" it (`search or boolean or job_type or location`) matched none
of its name or its parametrize ids. Run for real it failed 4 of 4.

**The defect underneath.** The `drive` fixture (`tests/test_tools.py:216`)
closes over ONE list. Calling `drive()` a second time returns that same
accumulating list, not a fresh one -- so a test that installed twice read the
FIRST call's url as the second call's, and the ON url was compared against
itself. The test asserted its own tautology.

    THE FIX      one install, two calls, `assert len(navigations) == 2`
                 first, then `on_url, off_url = navigations`
    THE CONTROL  `if True:` in the emit loop  -> dies on the OFF assertion
                 `if False:` in the emit loop -> dies on the ON assertion
                 Both must die. One direction alone leaves the word ONLY
                 in the test's name untested.

**THE STANDING RULE THIS PRODUCES: a `-k` run is not evidence a test ran.**
Confirm with `--collect-only` and count the ids, or run the file. A selector
that matches nothing exits 0 and prints "deselected", which reads like success.

### 1.2 `STRUCTURALLY-BLIND-GUARD` -- the fixture cannot reach the branch

`tests/test_sdui_surfaces_fixture.py::test_reading_the_count_did_not_cost_the_headline`
is named for the `_COUNT_LINE` exclusion in `shape.parse_profile_topcard`.
Deleting that exclusion left it PASSING on both committed renders.

**Why, measured by differential run rather than reasoned about.** On both
fixtures the count line sits BELOW `Contact info`. `parse_profile_topcard`
takes headline and location from the lines ABOVE that link and returns; the
count is never a candidate, so adding it to `eligible` changes nothing. Three
shapes were run against a mutated module and a pristine one:

    count below "Contact info"   identical output   clause DEAD
    count above "Contact info"   identical output   clause DEAD
    NO "Contact info" line       differs            clause LOAD-BEARING

    THE FIX      `test_the_count_exclusion_is_load_bearing_without_a_contact_line`
                 -- line input, not a fixture, because the shape is defined by
                 what it LACKS and a capture cannot be trusted to go on lacking
                 something
    THE CONTROL  delete `and not _COUNT_LINE.match(line)` from the `eligible`
                 comprehension -> the new test fails, `location` comes back as
                 "268 connections"

**THE STANDING RULE: a guard named after a branch must be shown to REACH that
branch.** The old test still passes and is still worth having; its docstring
now says in its own words that it cannot fail from the mutation its name
implies.

### 1.3 `GUARDS-ITS-OWN-COPY` -- the test re-implements the code it names

**NAMED DEFECT, not a note.** The name claims coverage the test does not have,
and the next reader will believe the name.

`tests/test_sdui_surfaces_fixture.py::test_a_skill_keeps_only_its_name_not_its_evidence_lines`
reads as the guard on skill-evidence separation. It cannot catch a defect in
`dom.read_profile_detail_entries` AT ALL. Its helper `_skills()` calls
`dom.harvest_linked_cards` directly and re-implements the name-selection loop
INSIDE the test file, so it exercises the test's own copy of the logic.

    THE CONTROL  add `entries.extend(rest)` to `read_profile_detail_entries`
                 -- the reader now returns evidence lines as skills, which is
                 exactly the defect this test is named for.
                 test_a_skill_keeps_only_its_name...   PASSES
                 test_the_evidence_lines_never_rejoin_the_skills_list  FAILS

The reader is covered by the second test. The first is left alone
deliberately -- it is another wave's, and it is not WRONG, only narrower than
its name. What is corrected is the claim, not the coverage.

**THE STANDING RULE: a test that re-implements production logic tests the
copy.** If a helper in a test file duplicates a function under test, the
guard's subject is the duplicate. Call the real function or rename the test.

---

## 2. THE MEASUREMENT PATTERNS WORTH REUSING

### 2.1 `A-NEGATIVE-CONTROL-MAKES-A-ZERO-MEAN-SOMETHING`

Established while measuring LinkedIn's job-search filter parameters
(`scripts/_probe_job_search_filter_params.py`).

The question was whether `f_AL`, `f_EA`, `f_JIYN`, `f_FCE` and `f_JT` are
honoured. A pill reading "checked" proves nothing on its own. The instrument
is the control: a parameter LinkedIn has never had, `f_ZZQQX=true`, loaded
under identical conditions.

    f_ZZQQX=true   0 pills moved, count identical, and the parameter was
                   STRIPPED from the landed url

**That is what makes "behaves like baseline" MEAN ignored** -- and no candidate
read that way. Without the control the same numbers are a screenshot.

**Its second law, learned the same day: a control at the KEY level does not
settle the VALUE.** `f_JT=ZZ` survived into the landed url verbatim while being
demonstrably inert. So url survival measures whether LinkedIn recognises the
KEY and says nothing about whether the VALUE was applied. A value-level control
(`f_JT=ZZ` against `f_JT=F`) is a different instrument and had to be built
separately.

### 2.2 `A-BLIND-CHANNEL-MUST-NOT-REPORT-A-CLEAN-ABSENCE`

Same probe, and the same disease as section 1.

Pass one filtered controls to those carrying `aria-pressed`, `aria-checked` or
`aria-expanded`, then reported which differed. It reported `(none)` for
`f_JT=F`. The control that proves `f_JT` applies is `Reset selected Job type`,
and it carries **no aria state at all** -- so the gate had structurally excluded
the one thing that could answer, and printed a zero.

**A zero from a gate that cannot see the thing is not a negative reading.** The
repair is not a wider gate; it is that a channel which dropped candidates may
not print a bare absence. It must carry its denominator:

    (none on the aria channel; N controls carry no aria state and are
     invisible to it)

### 2.3 `A-NUMBER-SHIPS-WITH-THE-DENOMINATOR-IT-WAS-TAKEN-OVER`

**The pattern this session most wants reused.** A number that ships with its
denominator cannot be quoted onward as a property.

`dom.read_profile_detail_entries` answers census row `N 118` -- endorsement
counts on the operator's own skills -- and the answer is "LinkedIn draws none".
It does not ship that as a constant. It ships a READING, re-taken on every
call, carrying what it looked at: cards searched, card lines searched,
characters of main text, and whether the body mentions one at all.

Two reasons, and the second is the general one:

* **Two worlds fit the evidence and nothing on his own account separates
  them** -- LinkedIn draws the line only for a skill someone endorsed, or
  LinkedIn stopped drawing it. A hardcoded answer would go on denying the count
  on the day one appears.
* **A "no" with no denominator is indistinguishable from a page that never
  loaded.** That confusion has cost this repository more than one round.

    THE CONTROL, and it is the entry condition for the whole reading:
    `test_the_endorsement_reader_can_say_yes` hands the same reader a card that
    DOES carry the line. Hardcoding `"drawn": False` kills that test and
    nothing else -- every other endorsement assertion is a negative taken on a
    page that draws none, so all of them would survive it.

### 2.4 `TWO-INSTRUMENTS-DISAGREEING-MAY-BE-TWO-MOMENTS`

Three instances in one day, all initially read as somebody's error:

* a `server_module` NameError reported against line numbers exactly one higher
  than any commit's -- the checker read the file in the seconds between a test
  being appended and its import being added
* a report that `tests/test_a_sanitiser_earns_its_entry.py` did not exist,
  accurate when taken; the docstring naming it was written ahead of the file
* a phone number reported in `scripts/_probe_interests_entity_shaping.py`
  against a scan finding zero -- the number existed in a PRE-COMMIT draft, was
  refused by `test_no_committed_identity`, and was replaced before the first
  commit

**Before treating a disagreement as an error, ask whether the two readings
share a moment.** A reading carries a timestamp its reader cannot see.
