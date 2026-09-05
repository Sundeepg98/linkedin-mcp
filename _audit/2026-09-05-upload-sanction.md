# The upload sanction was already granted. What was missing was an aim, and a guard.

Wave `upload-sanction`, 2026-09-05. Sent to land blocker
`FILE-UPLOAD-UNSANCTIONED` -- 16 rows, the highest ratio in
`_audit/2026-09-03-linkedin-gap-blockers.md`. Nothing here was pushed; the
freeze holds.

---

## 1. THE ORDER WAS STALE, AND DISK IS THE THING THAT SAYS SO

The brief read: *"`set_input_files` joins `readonly.SANCTIONED_MUTATIONS`
(currently 5 entries)"*, and *"`tests/test_readonly.py:310-341` asserts the
kind ABSENT by name -- that assertion now inverts."*

Measured at HEAD and in the working tree, which were byte-identical for every
file this wave owns:

    ("linkedin_server/writes.py", "perform", "click")
    ("linkedin_server/dom.py",    "activate_messaging_filter", "click")
    ("linkedin_server/writes.py", "perform", "fill")
    ("linkedin_server/writes.py", "perform", "select_option")
    ("linkedin_server/writes.py", "perform", "set_input_files")   <-- present

Five entries INCLUDING the one I was asked to add, landed 2026-09-04 in
`615a5c4`. The test had already inverted and been renamed
`test_exactly_one_place_in_this_package_can_reach_a_file_input`; its docstring
opens *"THE QUESTION THIS TEST CARRIED FOR THREE DAYS HAS BEEN ANSWERED."*

**Re-landing it would have been worse than a no-op.** Three sites assert the
length is exactly five (`tests/test_readonly.py`, and two in
`tests/test_messaging_overview.py`); a duplicate entry fails the COUNT check
that exists precisely so a second grant cannot hide inside a set comparison.
The suite would have gone red in a way that reads like a real regression.

Verify-before-obey. The sanction cost this wave zero.

---

## 2. THE DEFECT THAT WAS ACTUALLY THERE

`writes.UPLOAD_ACTIONS` is empty, and its own comment says why: each composer
"still needs its own file input measured before it can join". The same comment
says wiring the first one "is a one-line diff a reviewer can see". Both
sentences are true and together they were the hole -- **a one-line diff
satisfies no comment.**

`perform` loads four queues. `select_plan` is loaded on
`control_kind == "select_option"`, a classification `_live_control` DERIVES
from the tag of the control it actually read. `upload_plan` was loaded on
action membership alone, so it inherited whatever selector that action's arm
had built for its own purpose.

Measured 2026-09-04 by the wave that built the queue, and reproduced here in
the mutation run below: with `publish_post` forced into the set, the selector
arriving at the drain point resolves to the POST EDITOR --

    locator resolved to <div role="textbox" contenteditable="true"
                              aria-label="Text editor for creating content">

-- and the only thing that refused was Chromium. **That is somebody else's
check.** It fires on a div, and it would NOT fire on a file input that is
simply the wrong one.

`writes.UPLOAD_CONTROL_KIND` makes the stated requirement executable. The
check sits immediately above the call it protects, so a reader sees the check
and the handover in one breath and no later edit slips between them.

**It is not a new bar and not a stricter one.** It is the bar the sanction
already described in prose, and the derivation still belongs in the arm beside
the reading -- never at the call site from a selector string. The refusal
names the classification it found and deliberately does NOT carry the
selector: `_live_control` builds selectors out of dom ids, and a dom id on
this site can carry an entity identifier.

### SHOWN FAILING, on a copy of the tree, never on the shared one

    CONTROL -- unmutated copy                                    3 passed
    M1  the guard removed                                        2 FAILED
        test_the_upload_REFUSES_a_control_..._file_input
        test_an_unchanged_file_gets_PAST_the_digest_gate
    M2  the guard made unconditional (refuses everything)        1 FAILED
        test_the_sanctioned_call_site_EXECUTES_when_the_control_IS_a_file_input
    RESTORED                                                     3 passed

M2 is the half that matters: a check that refused every upload would pass M1's
tests and look identical in the report.

**And M1 shows the positive control still PASSING**, which says it is not
circular -- it tests the handover, not the guard.

`writes.py` was NOT mutated in the live tree. Six-plus waves are writing it
today and a mutation harness on a shared file is a two-writer hazard that has
already been disclosed once in this repository. The copy was asserted to be
the thing under test before the first write -- `writes.__file__` resolving
under the copy AND not under the checkout -- and **the negative half fired on
the first run**, because the scratch directory's own name is derived from the
checkout's, so a word-shaped needle matched the copy. The needle is now the
checkout root itself.

### The positive control is the first time the drain point has landed

Every upload test before it ended in a refusal -- by digest, or by Chromium
rejecting a div. `test_the_sanctioned_call_site_EXECUTES_when_the_control_IS_a_file_input`
drives the other branch against a real file input in headless Chromium, and
reads the result **off the browser's own node** (`el.files.length` and the name
the DOM reports) rather than off our own `uploads_made` counter. Counting our
own bookkeeping and calling it evidence is asking the code whether it did the
thing it says it did.

---

## 3. THE MESSAGE COMPOSER HAS NO NEEDLE, AND THAT WAS THE PLAN

**CORRECTS:** `_audit/2026-09-04-file-input-survey.md` -- its section 3 costs the message composer as "a `_live_control` arm + a name needle", and there is no needle to be had

The survey recorded TWO file inputs from a 2026-09-01 census whose two
accessible names lived only as prose in a docstring and an audit file,
"reproducible by no instrument here". One page load settles it, on an address
already on the read allowlist, through the attached browser:

    count=2  described=2  ambiguous=True  undercounted=False
    - shape='' container=form#0 disabled=False name_source=none
    - shape='' container=form#0 disabled=False name_source=none

**Both come back with an EMPTY shaped name.** The census's whole
name-resolution chain -- aria-label, aria-labelledby, title, the label routes
-- finds nothing for either. So a count cannot aim, because there are two; and
a name cannot aim either, because there is nothing to match on. The survey's
costing assumed the second half was available. It is not.

ABSENT IS NOT ZERO, so the composer's own controls were read in the same pass:
`recipients_selected=0`, `dispatch_modes_count=2`, body present and editable.
A real composer with nobody in it -- which is also the precondition that
licenses reading it at all.

Nothing was clicked, typed, selected or uploaded, and
`scan_source_for_mutations` over the probe's own source reports 0 hits,
printed by the run itself.

---

## 4. A GAP IN A SHIPPED CONSENT GUARD, REPORTED AND NOT FIXED

`tests/test_navigation_is_never_derived.py` refuses a navigation-derived url
reaching a print, because the operator's own slug reached a transcript three
times. The probe as first written printed the landed url and **the guard
passed it.**

Measured against a copy carrying two variants of the same file, same value,
same line:

    printed through the bare name `landed`         ->  RED
    printed through `out['landed']` (a dict)       ->  PASSES

**A dict subscript launders navigation taint.** The fixed point follows name
bindings, so storing a tainted value in a container and reading it back out
one line later is invisible to it. This is one level down from the finding the
`groups-events` wave filed -- *assigning to a variable does not launder taint*
-- and it is the case that does.

It is REPORTED here rather than fixed: the guard is not this wave's artifact,
and the choice of remedy (taint containers, taint any subscript of a tainted
name, or something narrower) is a decision for whoever owns it. The probe
takes the sanctioned route instead of riding through the gap, emitting
`_relation(...)` copied byte-identically from `_probe_groups_events_live.py`
because `test_every_relation_definition_is_byte_identical` requires exactly
that.

---

## 5. WHAT THE SANCTION ACTUALLY BUYS THE 16 ROWS, ROW BY ROW

The ledger's own words -- a yes "does not ship 16 capabilities, it UNBLOCKS
them". Here is what each still waits on, resolved against
`_audit/_scratch/_route-gap-rows.tsv` rather than from memory.

| rows | surface | still blocked on |
|---|---|---|
| `M C3 C4 C5 C7` | post composer media | **a CLICK.** The composer was read live 2026-09-04, drew ZERO file inputs, and draws an `Add media` button that builds the input on demand. The capture exists and supports nothing. A click there is a new sanction with its own argument. |
| `M C6` | title on an uploaded document | depends on `C5` |
| `M M14 M15 M18` | message attachments | **two inputs, no names.** Section 3. Not a missing capture any more -- a missing property of the page. |
| `M C27` | media in a comment | a picker surface nobody has captured |
| `M C45` | rich media in an article | depends on `C44`, the article composer |
| `M C86` | tag people in a photo | **not an upload.** A coordinate-anchored tag on an image that must already exist. |
| `J 70` | upload a NEW resume | a resume-manager address, not on the read allowlist |
| `J 146` | upload a resume against one posting | LinkedIn's resume-tailoring surface; never opened |
| `J 147 148 149` | insights / refine / export | all downstream of `J 146` |

**Eight of the sixteen sit on the two composers and the two are in different
states.** The post composer HAS been captured and the capture says there is
nothing to aim at without a click. The message composer HAD never been
captured; now it has, and the answer is that neither of the two aiming
strategies this package uses -- count-of-one, or exactly-one-name-match --
can address it.

**The honest total: this wave moves ZERO of the 16 rows into reachable.** What
it moves is the floor under all of them: an action can no longer be wired by
editing one set, the drain point has been proven to work end to end for the
first time, and the aiming question for the largest sub-group has a measured
answer instead of a plan.

---

## 6. WHAT THIS WAVE DID NOT DO

* **It did not wire any action into `UPLOAD_ACTIONS`.** None of the four
  candidates is aimable today and three of them are irreversible and
  outward-facing.
* **It did not widen anything.** No address entered the allowlist, no click
  was sanctioned, `SANCTIONED_MUTATIONS` is unchanged at five, no new
  `# readonly-ok` waiver, no boundary digest moved.
* **It did not fix the taint-guard gap in section 4**, nor edit `dom.py`,
  `readonly.py`, `server.py` or `shape.py` -- all four were dirty with other
  waves' uncommitted work while this ran.
* **It did not run the sharded CI**, which needs a push, and the freeze holds.
* **It did not re-verify the 2026-09-04 post-composer reading.** Section 5
  carries it forward on that wave's measurement, not on one taken here.
