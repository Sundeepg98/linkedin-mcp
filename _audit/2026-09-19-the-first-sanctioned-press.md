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
