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

## 3b. AND THEN THE SAME SURFACE ANSWERED, BY A THIRD ROUTE

**Section 3 above is true and one inference from being wrong, so it gets a
successor rather than an edit.** It says a count cannot aim and a name cannot
aim. Both hold. What it silently assumed is that those are the only two ways
to address a control, because they are the only two THIS PACKAGE uses.

A file input declares what it is for. Read live on the same address, through
the locator API rather than a new injected script:

    [0] accept='image/*'                          multiple=None
    [1] accept='image/*,.ai,.psd,.pdf,.doc,.docx,.ppt,.pptx,.pps,.ppsx,
                .xls,.xlsx,.txt,.eml,.mov,.mp4'   multiple=None

    aimable by declaration: YES -- 2 distinct declarations over 2 inputs

**Two inputs, two different declarations, authored by LinkedIn rather than by
this server.** That is a property to match on where a name and a count both
fail, and it is the distinction the three blocked rows need: one input takes
images only, the other also takes `.mov`, `.mp4` and the document extensions.

**IT DOES NOT SAY WHICH ONE IS "THE PHOTO ONE".** Mapping an accept list onto
a capability is a judgement, not a reading, and it belongs to whoever wires
the composer. The probe's verdict function compares and refuses to interpret:
NO when nothing is declared, NO when the declarations are IDENTICAL (two
inputs saying the same thing are as unaimable as two with no names, and
choosing between them would be aiming by document order), YES only when the
page distinguishes them itself.

**AND ONE THING THE READING TOOK AWAY.** `multiple` is absent on BOTH inputs,
so the row reading "attach files, max 5, 20 MB total" has no DOM expression of
its own limit here. A wiring cannot learn that cap from the control.

**THE PROBE NO LONGER PRINTS THOSE LISTS, AND THE LISTS ABOVE ARE STILL THE
EVIDENCE.** A sibling wave extended the consent guard from urls to
text-extraction sinks, and this probe's `print` of a value read off the page
is one of the two new sites it caught. That guard is not in this tree yet --
measured: the file's last commit here is `196394d`, it carries no text-sink
rule, and both parametrized cases for this probe pass at HEAD -- but the line
is the shape it names, so it was reduced rather than declared. A declaration
keys on the whole sink expression and would tolerate that line forever
whatever the expression later holds. The probe now emits a closed vocabulary:

    [0] tokens=1  image=True video=False documents=False multiple=absent
    [1] tokens=16 image=True video=True  documents=True  multiple=absent

Same verdict, and it reads better than the value did. The exact list belongs
to whoever wires the composer, re-read live at the moment they aim.

**What this changes about the ledger:** `M M14 M15 M18` move from *no aiming
strategy exists* to *the aim is available and the rest of the wiring is not
built* -- a `_live_control` arm returning `UPLOAD_CONTROL_KIND`, a target
shape, a tool and its consent text. That is a wave, and it is now a wave with
a measured control to aim at instead of a plan for one.

---

## 3c. `undercounted` IS A CORRECT GATE ON AIMING AND AN OVER-STRONG ONE ON COUNTING

Read off the shipped code rather than its reputation:

    "undercounted": bool(census.get("truncated")) or described != counted

Two conditions, one flag, and they are not the same claim. `counted` comes
from `counts.file_inputs`, a **document-wide `querySelectorAll`** that a
control-list cap cannot touch. `described` comes from the censused controls,
which stop at `CENSUS_MAX_CONTROLS`. So a truncated census makes the
DESCRIPTIONS incomplete while leaving the COUNT exact.

The reader's own docstring is right: *"a caller must not aim on a truncated
reading."* Aiming needs a described control. **Counting does not.**

**WHERE IT MATTERS, and it is a reading in the survey this wave already
corrects once.** The feed came back `count=0 described=0 undercounted=True`
and was recorded as *"UNKNOWN -- the census was truncated; no count may be
read off this."* The truncation is real (177 buttons, 192 links, past the
cap). But `count=0` is a document-wide zero, and with nothing to describe
`described == counted`; the ONLY thing making that reading UNKNOWN is the
`census.truncated` disjunct.

**The honest statement about the feed is stronger than the one recorded:** it
draws ZERO file inputs document-wide, and nothing can be AIMED there because
its control list was cut short. Two facts, and the flag collapses them into
the weaker one.

**NOT FILED AS A DEFECT AND NOT CHANGED.** `read_file_inputs` is another
wave's artifact, its conservative disjunct is defensible for the decision it
was built to gate, and a caller wanting the count already has `count` sitting
beside the flag. What is wrong is a READING that treats the flag as a verdict
on the count -- and that is this document's business, because the same flag
governs every surface in section 5's table.

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
| `M M14 M15 M18` | message attachments | **SUPERSEDED BY SECTION 3b.** Two inputs and no names (section 3), but they carry DIFFERENT `accept` declarations, so the aim exists. What is missing is now the wiring -- an arm returning `UPLOAD_CONTROL_KIND`, a target shape, a tool, consent text -- and not a way to address the control. |
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

**AND THE AIMING ANSWER GOT BETTER AFTER THAT SENTENCE WAS WRITTEN** -- see
section 3b. Three of the sixteen (`M14 M15 M18`) now have a control a wiring
can address, by a property LinkedIn states about it. Still not reachable, and
saying so is the point: an aim is one of four things those rows need. But the
blocker under them changed from *nothing can address this* to *nobody has
built the rest*, and those are different queues.

---

## 5b. THE "DEAD CITATION" UNDER `M 18` IS NOT DEAD. IT IS A TOPIC.

**CORRECTS:** `_audit/2026-09-05-decide-retire-rulings.md` -- its section 10.5 records `a148003` as returning HTTP 404 and routes the row to this blocker's owner to re-source; the id is a TOPIC id and resolves in the `/topic/` form, so the row's numbers are unsourced for a different reason than the one recorded

That section was routed to me by name -- *"whoever holds that blocker should
re-source them rather than quote them"* -- and it was right to route it. The
finding underneath it needs one correction and then goes further.

**MEASURED, four url forms:**

    /help/linkedin/topics/a148003      404
    /help/linkedin/answer/a148003      404
    /help/linkedin/answer/en/a148003   400
    /help/linkedin/topic/a148003       SERVES -- "Messaging | LinkedIn Help",
                                       a hub of 28 articles

**`a148003` IS A TOPIC ID, NOT AN ARTICLE ID.** The earlier reading tried two
ANSWER forms; an article route was never going to resolve a topic, so the 404s
are facts about the form and not about the id. Both readings are accurate
about what they saw -- the missing fact was the id's KIND.

**AND THE CENSUS ALREADY HELD IT.** `_audit/_census/messaging-and-content.md`
line 79 lists the Messaging topic as `/help/linkedin/topic/a148003`, 28
articles, in its own topic table -- twenty-seven lines above the row table that
cites the bare id. The correct form was in the same file the whole time. This
is not a research failure; it is the same shape as everything else here, a
fact present in one place and not carried to the place that needed it.

### The row's numbers still cannot be sourced, and now for a reason that holds

Asked for every article on that topic page concerning attaching or sending
files, photos, videos or media, the served hub returns **none** -- its 28
articles cover InMail, conversation management, group chats, editing and
notification settings.

**STATED AT ITS REAL STRENGTH.** That is a reading of the topic hub as served
and rendered today, by one reader. It is NOT "LinkedIn documents no
attachment limit" -- a hub can paginate, and a limit can live in an article
the hub does not surface. What it does establish is that **"max 5, 20 MB
total" cannot be re-derived from the citation the census gives for it**, which
is what a ruling would need.

### A second, independent line pointing the same way

Section 3b read the compose surface's own controls: **`multiple` is absent on
BOTH file inputs.** So the cap is not expressed by the control either. Two
routes -- the cited documentation and the live DOM -- and neither corroborates
the number.

**THE CONSEQUENCE FOR THE ROW, precisely.** `M 18` stays a real capability row:
the control exists, it accepts documents and video, and section 3b makes it
aimable. What must not travel is the PARENTHESIS. "Attach files" is measured;
"(max 5, 20 MB total)" is currently unsourced, and any ruling that leans on
those two numbers is leaning on nothing this repository can show.

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
