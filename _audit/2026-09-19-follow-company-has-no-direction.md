# follow_company: the About card is not a second source. It is the same button.

**Diagnosis only. No write was fired, no confirm token was minted, nothing was
edited in `writes.py`, `dom.py` or `shape.py`.** The proposed repair is
**REFUSED**, and the reason is a measurement rather than a ruling I found
written down.

## THE PROPOSAL, AND WHY ITS PREMISE IS FALSE

The finding at 17:52 reads:

    company_follow_state.state   unknown     <- the gate reads this, and refuses
    company_about.follow_state   "Follow"    <- POPULATED, on BOTH postings

and infers that the payload carries **a source the gate never consults**.

**It does not. Both fields describe the SAME BUTTON.**

Measured offline over the tracked, sanitised captures, counting
`button[aria-label="Follow"]` or `"Following"` -- which is `dom.FOLLOW_CONTROL`
verbatim:

    job_detail.html                      1   'Follow'
    job_detail_hydrated.html             1   'Follow'
    job_detail_following_hydrated.html   1   'Following'
    job_detail_following.html            0   (the pre-hydration skeleton)

**Exactly one on every hydrated page.** And its position says whose it is --
the 300 characters preceding it on the followed-employer capture close the
About-the-company card's own follower line and open the button immediately
after it:

    ...<span>NNN,NNN followers</span></p></div></div></div>
    <button class="..." type="button" aria-label="Following">

So the page's only follow control **sits inside the About-the-company card**.
`shape.company_about_card` reads it via `_ABOUT_FOLLOW_STATE` off the card's
rendered TEXT LINES; `dom.read_follow_control` reads the same element's
`aria-label`. **Two routes to one control, not two controls.**

> A field the gate "never consults" would have to name something the gate
> cannot see. This one names the thing the gate is already pointed at.

## THE LABEL IS NOT STATIC -- THAT HALF OF THE WORRY IS CLOSED

The brief asked whether `"Follow"` might be a fixed caption, which would make
the whole repair a fabrication. **It is not.** `_ABOUT_FOLLOW_STATE` is
`^(Follow|Following)$` and both states are pinned on real captures:

    test_a_whole_card_reads_all_four_fields                   -> "Follow"
    test_the_followed_employers_card_reads_its_follow_state   -> "Following"

the second off `job_detail_following_hydrated.html`, a capture of a posting
whose employer the account already follows. **The card's field is
state-bearing and has been seen moving.** That is worth recording on its own,
because it was the stated risk and it is now answered.

## WHAT THE REFUSAL ACTUALLY MEANS, AND IT IS A NEW FACT

`shape.follow_state` returns `unknown` on three distinct causes and says which:
`count == 0` (not rendered), `count > 1` (ambiguous -- "choosing the first
would be choosing by position"), or a label outside `FOLLOW_LABELS`.

On the two live postings the card's TEXT route succeeded while the ARIA route
returned `unknown`. **The element was therefore on the page** -- the card read
its line off it. So what went missing on live LinkedIn is the `aria-label`, or
its value, **not the control.**

**That divergence appears on no tracked capture.** All three hydrated captures
carry the attribute and count exactly 1. The live pages are doing something
this repo has never photographed.

## WHY WIRING THE CARD IN WOULD BE WORSE THAN THE REFUSAL

The gate does not only need a direction. **It needs a control the click can
address**, and the click is built by `dom.follow_control_selector(label)` --
`button[aria-label="<label>"]`. Its own docstring already rules on the
adjacent shortcut:

> *"It never returns the two-state `FOLLOW_CONTROL` union. That constant
> exists to READ a state and matches the control in either one; a click built
> from it would press whichever of the two happened to be on the page, which
> on a toggle is how an action performs its opposite."*

If the `aria-label` is precisely what the live page is not drawing, then
sourcing the direction from the card's text hands the gate a confident
`not_following` **for a control the click path cannot select**. The tool would
stop refusing and start failing one step later -- or select something else.

> **The repair does not buy a capability. It buys the removal of the refusal
> that is currently the only thing reporting the defect.**

An `unknown` that blocks is a capability that does not work **and says so**.
A wired-in card state is a capability that does not work **and does not**.

## THE STATED REASON I WAS SENT TO FIND -- HONESTLY, WHAT I FOUND

**No prose anywhere names the About card and rejects it as a direction
source.** I will not claim otherwise. What `writes.py`'s `direction_source`
does state is that the posting control was chosen **against a named
alternative**, and that alternative is the standalone followed-companies
surface, rejected as "the weaker source: LinkedIn renders 20 rows under a
heading saying 58." The About card is not weighed there, because at the time
that was written it was not a separate thing to weigh.

**So the repair does not overturn a written ruling. It rests on a premise the
markup refutes**, which is the stronger objection of the two.

## WHAT THE NEXT WAVE SHOULD DO, AND WHAT IT MUST NOT

**MUST NOT:** change `shape.follow_state`, widen `FOLLOW_LABELS`, add a
fallback from `company_about.follow_state`, or relax `read_follow_control`'s
`count != 1` return. Every one of those converts a reported defect into a
silent one.

**SHOULD:** take ONE live posting and read, on the same render, the count of
`button[aria-label=...]` follow controls, the count of elements whose TEXT is
exactly `Follow`/`Following` inside `ABOUT_COMPANY_CONTAINER`, and the full
`company_follow_state.why`. Three numbers. They separate "LinkedIn dropped the
attribute" from "LinkedIn now draws two" from "LinkedIn relabelled it", and
those have three different repairs. **I did not have the session time to take
that read, and I am recording the gap rather than characterising what I did
not see.**

## ONE UNRELATED STALENESS, NOTED NOT FIXED

`shape.py` at `_ABOUT_FOLLOW_STATE` says *"``dom.read_follow_line`` is what
interrogates the control itself."* **There is no `read_follow_line` in
`dom.py`**; the function is `read_follow_control`. A dangling name in a
comment that points a reader at the right idea by the wrong handle. Left
alone -- it is not this wave's file, and a one-word edit to a comment is still
an edit to a tree with live writers.
