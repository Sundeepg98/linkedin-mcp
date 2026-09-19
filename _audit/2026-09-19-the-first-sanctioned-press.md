# The first sanctioned press -- PERMITTED, safe, and it discloses nothing yet

> **THE RECORD EVERY LATER PRESS IS MEASURED AGAINST.** Full evidence, not a
> summary. Taken 2026-09-19 ~11:32 by the box, on `/analytics/profile-views/`,
> under the ruling at `c48ec60`, using `press.disclose` from `5be109a`.
>
> **THE HEADLINE IS TWO SENTENCES AND THEY MUST TRAVEL TOGETHER. The press was
> permitted, priced by two counters, and left the page exactly as found. It
> does NOT establish that anything was disclosed, and `N 133` / `N 134` are
> therefore NOT banked.**

## 1. THE AUTHORISATION, HELD AS GIVEN

The authorisation was for the MECHANISM to be used as designed, **not for a
press**. This wave did not decide to press. It supplied an address, a shape key
and a counter reader, and `press.disclose` decided. Had it refused -- including
on `no_counter_prices_this_press`, which this wave had flagged as an open
question for this page -- the refusal would have been the deliverable.

Nothing was pressed that the gate did not evaluate. Nothing adjacent was
pressed "to check". There was no retry.

## 2. THE FOUR CONDITIONS, BY NAME

### Condition 1 -- address already admitted. CHECKED BEFORE ANY LOAD.

    readonly.is_read_url("https://www.linkedin.com/analytics/profile-views/")
        -> True
    press.check_address(...)
        -> {'pressed': False, 'admitted': True}

### Condition 2 -- enumerated attribute shape, by key. CHECKED BEFORE ANY LOAD.

    press.SANCTIONED_SHAPES -> ('[aria-expanded]', '[aria-haspopup]')
    press.check_shape('[aria-expanded]')
        -> {'pressed': False, 'shape_ok': True}

The shape is a KEY from a closed tuple. No selector and no label was supplied
at any point.

### Condition 3 -- shown not to move an outward counter

**The one judgement this wave made was WHICH counters**, and it is stated
rather than buried: `dom.read_invitation_badge` and
`notify_cost.read_notifications_badge`. Both are this repository's established
cost instruments, both render on the nav of any signed-in page, and **both are
built to refuse rather than report a false zero** -- which is exactly what
`check_counters` needs, since it refuses on an unreadable counter.

Reading taken on the page already open, before handing over:

    invitations            0
    notifications_unread   6

**Both READ. Neither is None.** The gate then took its own before/after pair
across the press and did not refuse, so both were equal at both ends:

    priced_by: ['invitations', 'notifications_unread']

Had either moved, `check_counters` would have returned `counter_moved`, which
is TERMINAL -- *"a press that moves an outward counter is a WRITE, whatever it
looked like."*

### Condition 4 -- closed, and the closure verified

    check_closure requires expanded_before and expanded_after to be
    NON-NONE and EQUAL. The verdict permitted, so both read and matched.

Page state, measured independently of the gate:

    BEFORE   url_relation=target  expanded_true=0  expanded_false=9
             dialogs=0  shape_total=9
    AFTER    url_relation=target  expanded_true=0  expanded_false=9
             dialogs=0  shape_total=9

**Identical on every field.** The page was left as found.

## 3. THE VERDICT, VERBATIM

    {"permitted": true, "pressed": true,
     "priced_by": ["invitations", "notifications_unread"],
     "shape": "[aria-expanded]"}

CDP pages: **10 before, 10 after.** No tab leaked; the page was closed in a
`finally`.

## 4. WHAT THIS DOES NOT ESTABLISH, AND WHY THE ROWS ARE NOT BANKED

**`aria-expanded` read the same value at both ends, and the page carried
`expanded_true=0` both before and after.** Two readings fit that evidence
equally:

    (a) the press opened the panel and Escape closed it, returning to false
    (b) the press did nothing at all, so the state never left false

**NOTHING IN THIS RUN DISTINGUISHES THEM.** Condition 4 verifies that the page
was left as it was found; it does not verify that anything happened in
between. A gate built to prove SAFETY is not thereby proving DISCLOSURE, and
reading the permit as though it were would be the same error as a control that
cannot fail.

So:

* **The mechanism is proven safe on this page.** Four conditions, two
  counters, a verified closure and an unchanged page.
* **`N 133` and `N 134` stay GAP.** The capability is reading the filtered
  viewer data and the notable-viewers panel. **No content was read.** A press
  that is permitted is not a capability that is covered.

## 5. THE NEXT ARTIFACT, NAMED PRECISELY

**A reader, not another press.** What is missing is a run that presses and
READS THE DISCLOSED CONTENT IN THE SAME BREATH -- and that needs two things
this run did not have:

1. **A DISCLOSURE WITNESS.** Something that fails if the panel did not open:
   a count of a region that exists only while expanded, or an
   `aria-expanded="true"` observed WHILE the control is held open, before
   Escape. Without it, (a) and (b) above stay indistinguishable forever and
   every future permit will carry the same silence.
2. **A NAME-FREE SHAPER for whatever the panel draws.** The notable-viewers
   panel is made of other people, and `linkedin_who_viewed_me` already states
   the resolution for that page: *"numbers, filter labels, the chart's own
   sentence and COUNTS of page regions, and nothing else."*

**The witness is the harder half and it is the one worth building first**,
because without it a permitted press cannot be told from a press that missed.

---

# 6. CORRECTION, SAME DAY ~11:50 -- I UNDERSTATED THIS, AND IN THE DIRECTION THAT MATTERS

Section 4 above filed the ambiguity as a limit of THIS RUN. **It is a limit of
the GATE**, and the two are not close: a limit of a run is fixed by running
again, and this one cannot be. **Every press through `press.disclose`, past and
future, carries the same silence.**

The evidence is four lines of `press.disclose`, in this order:

    expanded_before = await locator.get_attribute("aria-expanded")
    await locator.click(...)
    await page.keyboard.press("Escape")          # <-- DISMISSED FIRST
    expanded_after = await locator.get_attribute("aria-expanded")

**`expanded_after` is read AFTER the dismissal.** Nothing reads the control
while it is open. `check_closure` requires `before == after`, and a successful
Escape guarantees that equality whether or not anything ever opened. The gate
takes exactly **two readings, and both are outside the open state. Two readings
cannot describe three states.**

Why the original wording was wrong in the dangerous direction: "this run could
not distinguish them" invites a later wave to run it again and expect an
answer. **It would get the same verdict, and would have spent a press on his
live account to learn nothing.**

## SHOWN, NOT ARGUED

`tests/test_the_press_gate_cannot_witness_disclosure.py` builds three pages
that differ IN THE WORLD and shows `disclose` returning **one identical
verdict** for all three:

    opens    the control really opens      aria-expanded false -> true
    misses   the press lands on nothing    nothing changes
    dialog   it really opens AS A DIALOG, and the control's own
             aria-expanded never moves

Its control is a fourth case -- a moved counter -- **shown SEPARATING** through
the same comparison, because a test asserting that things are
indistinguishable passes trivially if it is comparing the wrong thing.

## THE FIX IS ONE READING, AND IT IS VERIFIED RATHER THAN PROPOSED

A local copy of `disclose` with a single observation taken between the click
and the dismissal was measured: the three verdicts separate, `disclosed` is
True only where something opened, **the four safety conditions are unchanged
field for field, exactly one control is clicked, and a refused press carries no
witness at all.**

Two design points, both decided by measurement rather than taste:

1. **THE OBSERVATION IS AN ENUMERATED CLOSED SET, NEVER A CALLER'S CALLABLE.**
   A seam that accepts arbitrary code at the open moment is a press seam
   wearing an observer's clothes -- it would reintroduce precisely what
   `SANCTIONED_SHAPES` exists to prevent, at the most privileged instant.
2. **IT READS THE PAGE, NOT ONLY THE CONTROL, AND IT IS A PAIR.** The `dialog`
   case decides this: a witness reading only the pressed control's own
   `aria-expanded` sees `false` while a dialog is open on the page, and
   **reports a real disclosure as a miss.** That false negative is worse than
   no witness, because it manufactures a confident wrong answer where there was
   an honest silence. A page-wide count also needs its baseline -- this page
   already carried nine `[aria-expanded]` nodes before any press -- so the
   witness is the SAME readings taken at both moments, never a single one.

**And the witness is not a fifth condition.** Permission stays decided on
safety alone. Folding disclosure into permission would turn a READING into a
GATE and refuse a perfectly safe press for the sin of being uninformative.

## WHAT IS OWED, AND TO WHOM

`linkedin_server/press.py` is owned by `messaging-measure`. **This wave did not
edit it.** What is handed over is a red-when-fixed test, a verified design, and
the one case that picks it. `N 133` / `N 134` remain GAP either way -- **no
content has been read** -- and the second half, a name-free shaper for what the
panel draws, is still unbuilt.

---

# 7. THE SAME SHAPE IN CONDITION 3, AND THIS ONE BOUNDS MY OWN EVIDENCE

Having found one check that passes whether or not the thing it describes
occurred, the honest next question is whether any other condition has that
shape. **Condition 3 does**, and since this record's headline is *"priced by
two counters"*, the bound belongs here rather than in a note about someone
else's file.

`check_counters` refuses `no_counter_prices_this_press` when
`set(before) & set(after)` is empty -- **that is a test for whether a counter
was READ at both ends, not for whether it COULD HAVE MOVED.** So `priced_by`
names counters that were *readable*, never counters that were *sensitive to
this press*. The ruling's language is the stronger one -- *"where no counter
can price a press, unmeasurable resolves AGAINST the press"* -- and **the
implementation's reading of "can price" is the weaker of the two.**

**What that does and does not do to the press recorded above.** It does not
make it unsafe: a counter that did not move is still a counter that did not
move, and nothing here weakens conditions 1, 2 or 4. It does mean the natural
strong reading of *"priced by two counters"* -- that a write would have been
caught -- **is not established by this run.** Pending invitations and unread
notifications are nav badges on his own account; there is no derived reason
either would respond to expanding a filter panel on an analytics page.

**And the boundary is the interesting part: sensitivity cannot be established
here without doing the thing the gate exists to prevent.** A counter is shown
sensitive to a class of press only by a press of that class moving it -- which,
for an outward counter, is the write. `messaging-measure` derived it for a feed
press against `off_state` because that surface offered a safe one. **This page
offers none, so condition 3 on `/analytics/profile-views/` can be shown
passing and cannot be shown capable of failing.**

That is a real limit, not a defect to fix by trying harder, and the useful form
of it is a question for the owner rather than a patch from this wave:

> **Should `priced_by` distinguish a counter shown SENSITIVE to a press class
> from one merely shown READABLE?** If it should, the sensitive set is empty
> for this page and the ruling's own words resolve that against the press --
> which would have made this first press a REFUSAL.

**This wave is not ruling on that**, and deliberately: it is the owner's
boundary, and a wave arguing its own permitted press should have been refused
is exactly the argument that should be made by someone else. It is recorded
because **the record every later press is measured against should carry the
limits of its own strongest claim.**
