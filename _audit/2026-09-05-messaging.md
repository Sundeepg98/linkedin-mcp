# Messaging wave, 2026-09-05

**Owner: the `messaging` wave. Scope: 7 blockers, 24 rows (2R / 21W / 1RW).**
**Page loads taken: ZERO. Messages sent: ZERO. Rows retired: ZERO.**
**Commits: 7. Tests added: 8, in one new file. Boundary changes: 0.**

**HEADLINE: a defect in `writes._recipient_gate` -- the last thing between a
tool call and a message reaching a real person -- was found, measured, ruled
on and FIXED today. Two ways a stranger reached `proceed: True` now refuse.
Sections 1, 1a and 7. Section 7 carries the ruling and supersedes my own
recommendation not to fix it.**

Rows, recomputed at freeze rather than re-read from the brief:

    17  CONVERSATION-OVERFLOW-MENU   10   1R/8W/1RW   WriteSpec        MEASURE
    50  MESSAGE-REQUESTS-SURFACE      4   1R/3W       allowlist +1     BUILD
    66  THREAD-REPLY-BOX              2   2W          WriteSpec        MEASURE
    67  PER-MESSAGE-OVERFLOW-MENU     2   2W          WriteSpec        MEASURE
    76  MESSAGE-REACTION              1   1W          WriteSpec        MEASURE
    57  MESSAGE-ADDRESSING            1   1W          none             MEASURE
    45  GROUP-CHAT-SURFACE            4   4W          WriteSpec        BLOCKED
                                     --
                                     24    = 2R + 21W + 1RW

---

## 1. THE FINDING: the recipient gate's name match is a bare substring, and its
## own selector supplies half the haystack

**VERIFIED-BY-INSTRUMENT.** Commit `3c3bfa3`,
`tests/test_the_needle_is_matched_as_a_bare_substring.py`, 5 tests, 7.15s,
run through the shipped gate and the shipped injected script in a real
browser.

`writes._recipient_gate` is the only thing standing between a tool call and a
message arriving in a named human being's inbox. It is the gate on
`send_message`, one of the five irreversible writes, on a server currently
running `writes_enabled: true` with `auth: "none"`. Its docstring states the
safety property in capitals:

> **WHAT MAKES THIS SAFE IS THE NAME MATCH, NOT THE COUNT.**

That sentence is correct about the COUNT, and the count half is well tested.
This wave measured the other half. The name match is `indexOf`, over

    (aria-label or "") + " " + (textContent or "")

lowercased. That is the loosest relation available between two strings.

### The three readings

Identical page, identical chip, identical gate. **Only the needle differs.**

| case | needle | total | matches | verdict |
|---|---|---:|---:|---|
| control | absent from everything | 1 | 0 | REFUSED `3_needle_does_not_match` |
| furniture | a substring of the remove control's own label word | 1 | 1 | **`proceed: True`** |
| containment | a proper substring of the stranger's name | 1 | 1 | **`proceed: True`** |

In both proceed rows the composer holds **one committed recipient and it is a
stranger** -- byte-for-byte the state
`test_the_gate_refuses_one_wrong_recipient` refuses. The gate returns
`proceed: True`, and `proceed: True` is what causes his words to be typed
next.

### Why the furniture case is the structural one

Every candidate in `dom.RECIPIENT_CHIP_SELECTORS` constrains `aria-label` to
carry a remove-control's own label word. The matcher then searches that same
attribute. **The string being searched was selected BECAUSE it contains the
thing being searched for.**

That is `uniqueness-over-a-filtered-set-measures-the-filter`, one layer below
where this repo first found it. The typeahead case was LinkedIn's filter; this
one is ours. A needle that is a common short given name and also a substring
of the control's wording matches on a chip naming somebody he never named.

### Why the control matters more than either defect row

The control is **the detector factored out of the assertion**. A guessed
selector's guaranteed failure mode is a fixture that quietly stops drawing a
chip, at which point every case becomes the empty case and passes for the
wrong reason. The control refuses on the same page with the same chip, so both
`proceed` results are attributable to the MATCHER and not to a dead fixture.

### NOT FIXED BY ME -- AND THEN RULED AND FIXED. SEE SECTION 7.

> **SUPERSEDED THE SAME EVENING.** The paragraphs below argue for recording
> the defect rather than repairing it. The coordinator ruled the other way,
> with an argument I had not made and should have: **the two error directions
> are not symmetric.** Section 7 carries the ruling, the fix and its cost.
> Read it before acting on anything in this subsection.

### The reasoning I used to decline, kept because the ruling turns on it

The obvious repair is a stricter matcher. **Every stricter matcher was
MEASURED DEAD on the neighbouring surface**:
`_audit/2026-09-03-typeahead-name-matching-is-dead.md` reports `prefix`,
`prefix_then_nonletter`, `prefix_boundary`, `prefix_then_space_or_end` and
`whole` at **zero** across three live sessions, and shows a word boundary
cannot even separate a name from a connection degree run onto it.

That measurement is about the SUGGESTION rows. This is the CHIP rail, which is
a different surface -- **and nobody has ever observed a chip.**
`RECIPIENT_CHIP_SELECTORS` has never matched anything on any real page; `dom`,
`tests/test_send_message_gate.py` and `scripts/_probe_typeahead_commit.py` all
say so, and one of them pins the sentence so it cannot quietly go stale.

So choosing a matcher here would be choosing it against an imagined DOM, which
is verbatim the error the typeahead audit records: *"correct on the shape the
fixtures had, and dead on the shape the page has."* A tighter matcher aimed at
an unobserved rail either refuses everybody -- safe -- or keeps proceeding for
a reason nobody measured, which is not. **Hand the peer the measurement, not
the fix.**

The two defect tests therefore assert TODAY's behaviour and go RED the day it
is fixed. Green on that file means *the defect is still present and recorded*,
never *the defect is absent*.

### What the fix probably is, for whoever takes it

Not a matcher. The typeahead audit's section 5 already names the route --
address the recipient by IDENTIFIER through LinkedIn's own compose url --
and states the residue plainly: *addressing by identifier removes the CHOOSING
problem; it does not remove the OBSERVING one.* A route that commits a
recipient this server cannot read back is a route whose precondition it cannot
verify, and `_recipient_gate` would refuse it for exactly the reason it
refuses today.

One narrowing IS available without observing anything, and it is not a guess:
**do not search the attribute the selector selected on.** The furniture is
guaranteed present by construction. That kills collision 1 and leaves
collision 2 untouched. I did not apply it -- it edits `dom.py`, which was
contended all afternoon, and it is a change to the most irreversible write in
the package that deserves its own wave and its own red/green pair rather than
twenty minutes at the end of one.

> **AMENDED BY SECTION 1a, BELOW, TWENTY MINUTES AFTER THIS PARAGRAPH WAS
> WRITTEN.** The narrowing is real but it is SMALLER than the sentence above
> implies, and I measured that rather than leaving it to be read charitably.
> Read 1a before acting on this paragraph.

## 1a. THE NARROWING IS SMALLER THAN I SAID, AND HERE IS ITS REACH

**VERIFIED-BY-INSTRUMENT.** Commit `809fde1`, same file, 2 further tests,
7 passed total.

A claim about a repair is worth what a measurement of its reach is worth. On
the chip this suite draws, counts only, comparison inside the page:

    found                    1
    name in aria-label       1
    name in textContent      0
    furniture in aria-label  1

**The name lives ONLY in the field carrying the contaminant.** So "stop
searching the attribute you selected on", read as *drop `aria-label` from the
haystack*, leaves the matcher searching a string with no name in it at all.
The gate would then refuse every recipient including the right one -- safe,
and useless.

The available repair is therefore narrower than the paragraph above: **strip
the pinned furniture from the front, then search the remainder.** And that is
defined for exactly one candidate of four:

    aria-label^=    1   position known, remainder well defined
    aria-label*=    1   occurs somewhere, no defined cut point
    no aria-label   2   no constraint on the haystack at all

Stripping the first occurrence on the `*=` candidate would eat a name that
happens to contain those letters, which is the collision being repaired. The
two candidates with no `aria-label` constraint are not "fine" either -- what
those chips carry is simply unknown, which is a different problem and no strip
addresses it. They are counted separately for that reason.

**The reader used here is shown both firing and not firing in a single call**
-- same function, same needle, same node, one field answers 1 and another
answers 0 -- so `in_text == 0` cannot be the reading of a reader stuck at
zero. The detector is factored out of the assertion rather than assumed
beside it.

Same caveat as everywhere in this family: **this is the GUESSED chip.**
Whether LinkedIn puts a name in `aria-label`, in `textContent`, in both or in
neither is unobserved. What is measured is the shape this repo has been
reasoning against, which is the shape any repair written today would be
written against.

---

## 2. WHAT I DID NOT DO

Stated plainly, because a wave's omissions are the part a successor cannot
recover.

* **I took ZERO page loads.** I did not open `/messaging/`. The brief records
  its measured cost -- clearing the messaging badge and opening a conversation
  LinkedIn chooses -- and nothing I needed required paying it. **The badge cost
  is therefore zero BY CONSTRUCTION, not by measurement**, and that is a
  stronger claim than a before/after pair: my commit contains no navigation
  call at all. I did not read the badge, because there was no load to bracket.
* **I did not measure any of the seven surfaces live.** Rows 17, 50, 66, 67,
  76 and 45 are all exactly where the ledger left them. No row is retired by
  this wave.
* **I did not verify the prior wave's `CONVERSATION-OVERFLOW-MENU` result.**
  `_audit/_scratch/_progress-measure-surfaces.md` records it ANSWERED -- three
  readings, a firing control, 0 triggers and 0 menu items in 1.28 MB of DOM,
  costing two interactions rather than one -- and section A13 of the blockers
  ledger proposes moving all 10 rows to DECIDE. **I am relaying that, not
  confirming it.** Route the artifact: the scratch file and A13, not this
  sentence.
* **I did not touch the boundary.** No allowlist entry, no denylist entry, no
  digest recomputed. Row 50's `allowlist +1` is untouched and the chain head is
  wherever the newsletter wave left it.
* **I wrote no WriteSpec**, for any of the six blockers that need one.
* **I did not fire a single write**, gated or otherwise, at anyone.
* **I did not run the full suite.** I ran my own module (5 passed) and the
  three identity guards (602 passed, 3 failed).

---

## 3. THE THREE REDS I FOUND ARE NOT MINE, AND I CHECKED RATHER THAN ASSUMED

Re-run AFTER staging, per the rule that a guard run before staging cannot see a
new file:

    tests/test_no_committed_identity.py
    tests/test_page_text_is_never_printed.py
    tests/test_navigation_is_never_derived.py
    -> 602 passed, 3 failed

    test_no_file_prints_page_text_beyond_its_pinned_inventory
    test_no_navigation_derived_value_reaches_an_output_sink[_probe_profile_modal_presence.py]
    test_every_relation_definition_is_byte_identical

Named by those failures: `scripts/_probe_comment_identifier.py`,
`scripts/_probe_contact_info_panel.py`, `scripts/_probe_profile_modal_presence.py`.

**My file occurs 0 times in either guard's full output** -- measured with a
grep over `--tb=long`, not inferred from the fact that a test file has no
prints in it. My tree was clean at wave start; these landed inside the wave's
own window, which makes them somebody's live work and not mine to sweep.

The third one, `test_every_relation_definition_is_byte_identical`, is the
ENUMERATION class the freeze doc warns about: it fires because a caller was
added, so it is invisible to any run scoped to the file that defines it. It now
lists **6** claimant probes against a pin of 1.

---

## 4. A COST-MODEL OBSERVATION, offered as DERIVED and not as a measurement

Six of my seven blockers carry `WriteSpec` in the boundary column, costed at 3
each -- **18 of my total cost, gating 23 of my 24 rows.**

The ledger's own ASSIGNMENT RULE is *"one blocker per row, the EARLIEST binding
constraint."* For these rows I do not believe the WriteSpec is the earliest
binding constraint, and section 1 is why: `send_message` HAS a WriteSpec, has a
consent flow, has a gate, has 5 irreversible writes' worth of machinery around
it -- and the gate's own name match still cannot distinguish the person he
named from a stranger whose label merely contains those letters, because
**nobody has observed the control it reads.**

A WriteSpec written against an unobserved control is a specification of an
imagined DOM. The precondition all 23 rows share is an OBSERVATION, and the
ledger does not have a column for it.

I am not proposing a re-cost. I have measured one gate, not six surfaces, and
`CONVERSATION-OVERFLOW-MENU`'s own measurement -- 0 triggers in 1.28 MB --
points the same way without my having reproduced it. Whoever re-costs this
family should reproduce that reading first.

---

## 5. PROVENANCE

Recomputed at freeze, not re-read from the sections above.

    commits               3c3bfa3  the gate's substring match, 307 insertions
                          9a9dbad  this document, 225 insertions
                          809fde1  the narrowing's reach, 123 insertions
                          + the commit carrying section 1a
    file                  tests/test_the_needle_is_matched_as_a_bare_substring.py
                          430 lines, 7 tests
    tests                 8 passed after the fix (7 before it)
                          26 passed with tests/test_send_message_gate.py at
                          the tree as it stood at close, 90.69s -- re-run
                          because other waves committed to the modules this
                          file imports while it was being written
    identity guards       602 passed, 3 failed, 0 naming this file
    exact-value sweep     TWO readings, and the ORDERING is the point:
                            first   PASS, 0 hits across 326 swept files
                            at close PASS, 0 hits across 330 swept files
                          The corpus grew by 4 files between them. The second
                          is the one that says anything about the tree this
                          wave closed on; the first would have been a reading
                          about a tree that no longer existed. My two files
                          appear in 0 hits in both.
    page loads            0
    writes fired          0
    boundary changes      0
    rows retired          0
    AI attribution        0 (grep over every commit body)

Names in the test file are imported from the invented set already committed in
`tests/test_send_message_gate.py`. No real person, no member id, no slug, no
urn, no thread id appears in anything this wave wrote. The needles are DERIVED
from the shipped selector constants rather than spelled, so a change to the
candidate tuple fails the file instead of silently aiming it at nothing, and
both needle premises are asserted in both directions.

---

## 6. ROW 57 `MESSAGE-ADDRESSING`: THE ADDRESS IS ADMITTED, AND THE BINDING
## CONSTRAINT HAS MOVED TO THE ONE THIS WAVE MEASURED

**VERIFIED-BY-INSTRUMENT**, by importing the module and counting rather than
reading a comment:

    _ALLOWED_URL_PATTERNS      29
    _FORBIDDEN_URL_SUBSTRINGS  33

    admitted: ^https://www\.linkedin\.com/messaging/compose/\?profileUrn=
              urn%3Ali%3Afsd_profile%3A[A-Za-z0-9_-]{1,64}
              &recipient=[A-Za-z0-9_-]{1,64}$

The compose-by-identifier route is **admitted today**, anchored end to end,
with both identifier components bounded.

This matters because it changes which constraint binds first. When
`_audit/2026-09-03-typeahead-name-matching-is-dead.md` was written its section
5 recorded that route as refused by the read boundary; **the boundary has
moved since, and this is a statement about the tree as it now stands rather
than a claim about that document's accuracy on the day it was written.** Three
sibling spellings named there are still refused, which is the tightening it
anticipated.

**THE RESIDUE THAT DOCUMENT NAMED IS THE ONE THAT STILL BINDS, and this wave
made it worse rather than better:**

> addressing by identifier removes the CHOOSING problem; it does not remove
> the OBSERVING one.

Section 1 measured the observing half and found that even when a chip IS read,
the matcher over it cannot distinguish the person he named from a stranger
whose label merely contains those letters. So row 57's earliest binding
constraint is no longer an address and no longer name-matching -- both are
settled -- it is that **the chip rail has never been observed and the relation
read off it does not discriminate.**

Cost consequence, offered as DERIVED: the ledger costs row 57 at 2 with
`boundary: none`. The `none` is now right for a different reason than when it
was written -- not "no boundary work is needed to reach the surface" by
oversight, but because the pattern is already in. What it does not carry is
the observation, which no column in that table represents.

**I did not take that observation.** It needs a live composer, and a live
composer is `/messaging/`, whose measured cost is a cleared badge and a
conversation LinkedIn chooses. That is a load with a real obligation attached
and it belongs to a wave that can pay it deliberately, bracket it with a badge
reading before and after, and act on what it sees -- not to twenty minutes at
the end of this one.


---

## 7. THE RULING WENT THE OTHER WAY, AND THE ARGUMENT IS BETTER THAN MINE

**VERIFIED-BY-INSTRUMENT.** Commit `773a409`. 27 passed across this wave's
file and `tests/test_send_message_gate.py`, including all 19 pre-existing gate
tests.

I declined to fix the gate on the grounds that choosing a matcher against an
unobserved DOM is guessing. **That framing is what made it look blocked, and
it is wrong** -- not because the DOM became known, but because the choice never
depended on knowing it:

    a matcher too STRICT   refuses a legitimate send. He retries, or sends by
                           hand. Recoverable, visible, annoying.
    a matcher too LOOSE    commits a STRANGER to an irreversible message under
                           his name. Not recoverable, and not visible until
                           the stranger replies.

**When the error directions differ that much you do not need the DOM. You need
only which way to fail, and that was already settled.** A gate that refuses
everything on an unobserved surface is correct FOR an unobserved surface. My
section 1 had the asymmetry in it as an aside -- *"either refuses everybody --
safe -- or keeps proceeding for a reason nobody measured, which is not"* -- and
I wrote it as a reason the choice was hard instead of reading it as the choice
itself.

### What landed

`dom.SELECTED_RECIPIENT_JS` requires a WORD-BOUNDED match. A letter or digit
on either side of the hit means the needle is a fragment of a longer word, and
a fragment is not a name. Digits are word characters deliberately, so a label
running a name onto a connection degree refuses rather than matches.

    control    needle absent          total 1  matches 0  REFUSED
    furniture  needle in the button   total 1  matches 0  REFUSED  (was PROCEED)
    contained  needle inside a name   total 1  matches 0  REFUSED  (was PROCEED)
    exact      the full name          total 1  matches 1  PROCEEDS

**`total` stays 1 in every refusal**, which is what separates *the matcher got
stricter* from *the fixture stopped drawing a chip*. And the fourth case is not
decoration: **a gate that can only refuse certifies nothing**, so the strict
matcher is shown capable of saying yes.

**A CORRECTION TO MY OWN SECTION 1a.** I reported the available repair as a
prefix strip "defined for exactly one candidate of four". That was the reach of
*one* repair -- stripping the furniture -- and I presented it as the reach of
the fix in general. **An unanchored word-boundary rule needs no strip at all**,
applies to every candidate, and kills both collisions while still admitting an
exact name. My number was right about the thing I measured and wrong about the
question it was asked to answer.

### The docstring was corrected in the SAME commit as the code

`_recipient_gate` opened with *"WHAT MAKES THIS SAFE IS THE NAME MATCH, NOT THE
COUNT"* while the name match was the loosest relation between two strings. A
docstring is read as current truth by whoever opens the file next and is the
one class the correction machinery cannot bind, so it could not wait.

### What this still does not claim

**It may refuse a legitimate recipient on a real chip, and that is the accepted
cost rather than a regression.** No chip has ever been observed. A boundary
rule is not claimed to be the RIGHT relation for this rail, only a safer one
than a substring: **a stranger whose name contains the needle as a WHOLE WORD
still matches.** The answer to that residue is the identifier route, which
section 6 shows is now admitted at the boundary -- not a cleverer string
comparison.

**Relaxing this needs a chip observed, which needs `/messaging/` and its badge.
That spend was explicitly NOT authorised for this fix and did not need to be:
the fix does not depend on it.**

### A HAZARD FOUND BY LOSING WORK TO IT, 19:18

**A FAILED `git commit --only` ROLLED THE WORKING TREE BACK AND DISCARDED AN
UNCOMMITTED APPEND TO THE FILE IT WAS GIVEN.** The commit failed because
`-F /dev/stdin` could not be read (`fatal: could not read log file
'/proc/self/fd/0'`), and a partial commit restores the tree it had staged
around. Section 7 was written, verified present, and gone one command later.

I found it because the commit that did land reported **8 insertions** where
roughly ninety were expected, and I checked `git show HEAD:<path>` rather than
trusting the success line. **The count in a success message is the cheapest
available check on what a commit actually carried, and it is the one nobody
reads.**

    RULE: pass a commit message as a FILE PATH, never via /dev/stdin or a
          process substitution. And after any commit that reports a size you
          did not expect, verify with `git show HEAD:<path>` -- a partial
          commit can fail in a way that edits your working tree.

### 7a. THE COST IS NOT HYPOTHETICAL: ONE RED, AND IT IS MINE

**Found at 19:21, after the fix commit. I caused it and I am not clearing it
by relaxing the matcher.**

    tests/test_click_is_not_its_own_evidence.py
      test_a_click_that_does_commit_reaches_the_body_and_the_send
      -> recipient_gate refuses 3_needle_does_not_match, expected proceed

    66 passed, 1 failed, 1 xfailed

**THE CAUSE, traced rather than guessed.** That module's listbox is
`_option(NAMED_RECIPIENT, "1st")`, and its commit script sets the chip's
label to `'Remove ' + node.textContent`. So the label runs the connection
degree straight onto the name. The needle is the full name, the next character
is a digit, and this fix counts digits as word characters -- so it refuses.

**THAT IS THE MEASURED LIVE SHAPE, NOT AN ODD FIXTURE.** The typeahead audit
records exactly this as why a word boundary could not work on the suggestion
rows: *the last letter of a name and the `1` of `1st` are both word
characters*. The fixture models what was measured.

**SO THE "IT MAY REFUSE EVERYBODY" CLAUSE HAS ARRIVED CONCRETELY.** If real
chips carry the degree run onto the name the way suggestions do, this gate
refuses every legitimate recipient. Per the ruling that is the accepted
direction to fail -- but it should be read as a live prediction rather than a
formality, and it is strong evidence FOR the identifier route in section 6
rather than for any further tuning of a string comparison.

**WHY I DID NOT MAKE IT GREEN.** Two ways were available and both are wrong
tonight:

* **Relax the digit rule.** Defensible on its face -- names carry no digits,
  so a digit adjacent to the needle is arguably a separator. But that is
  reversing a safety decision, at the end of a wave, under a deadline, to turn
  a test green. This repo already has the rule for that: a red queue is sorted
  by WHAT THE ASSERTION IS ABOUT before anything is cleared, and a guard that
  fired is not a count that moved.
* **Edit that test.** It belongs to the typeahead wave, not to me, and tonight's
  standing rule is that you do not sweep a neighbour's lines.

**THE HAND-OFF.** Whoever owns `test_click_is_not_its_own_evidence.py` decides
one question, and it is a ruling rather than a test edit: **is a digit adjacent
to a name a word character or a separator?** Answering "separator" makes that
test green and admits `<name>1st`; answering "word character" keeps this
refusal and the positive test must be re-expressed as the accepted cost. I have
deliberately not answered it for them.
