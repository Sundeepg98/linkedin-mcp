# Messaging wave, 2026-09-05

**Owner: the `messaging` wave. Scope: 7 blockers, 24 rows (2R / 21W / 1RW).**
**Page loads taken: ZERO. Messages sent: ZERO. Commits: 1.**

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

### NOT FIXED, DELIBERATELY -- and this is the load-bearing judgment

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

    commit                3c3bfa3   1 file, 307 insertions, 0 deletions
    file                  tests/test_the_needle_is_matched_as_a_bare_substring.py
    tests                 5 passed, 7.15s
    identity guards       602 passed, 3 failed, 0 naming this file
    page loads            0
    writes fired          0
    boundary changes      0
    AI attribution        0 (grep over the commit body)

Names in the test file are imported from the invented set already committed in
`tests/test_send_message_gate.py`. No real person, no member id, no slug, no
urn, no thread id appears in anything this wave wrote. The needles are DERIVED
from the shipped selector constants rather than spelled, so a change to the
candidate tuple fails the file instead of silently aiming it at nothing, and
both needle premises are asserted in both directions.
