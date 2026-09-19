# EVENTS-SURFACE, 16 GAP rows -- why, and what actually moves them

Wave: `events-reader`. All timestamps are box time, 2026-09-19.
Written as the wave ran, not reconstructed at the end.

---

## THE ASSIGNMENT ASKED WHICH OF FOUR CAUSES IT WAS. IT IS NONE OF THEM.

The brief named four candidate causes and said three of them were cheap. The
measurement says the cause is a fifth one, and it is cheaper than three of the
four because **no shaper and no boundary change is missing.**

    1  shaper exists, not wired to a registered tool     RULED OUT, measured
    2  rows never banked, capability works                RULED OUT, measured
    3  reader covers part of the surface                  TRUE BUT NOT THE CAUSE
    4  rows need deeper addresses, individually refused   TRUE BUT NOT THE CAUSE
    5  THE ADJUDICATION EXISTS AND IS COMMITTED, BUT AS   <-- THE CAUSE
       PROSE, AND THIS CENSUS REFUSES TO RETIRE A ROW
       ON PROSE

**The rows are not unexamined. They were adjudicated row by row two weeks ago,
the adjudication is committed, and the census deliberately declined to apply
it** -- with the reason written down at the time.

## THE BAR, VERBATIM, AND IT IS COMMITTED

`_audit/_census/blocker-assignments.tsv`, the `N 181` line, committed `c1991ac`
today at 12:41. Working tree clean against it at 13:31, so this is HEAD and not
somebody's draft:

> **WHAT THIS ASSIGNMENT DOES NOT DO: it does not retire anything.** Fourteen
> of these seventeen carry a verdict here (MISFILED, EXCLUDED-RULED,
> MEASURED-ABSENT) that would move them out of GAP, and **NONE of those
> verdicts is enforced by a shipped rule** -- the four EXCLUDED-RULED rest on
> `readonly.py`'s admission COMMENT, which is **prose in a source file and not
> a refusal anything can be shown failing against.** Under the standing bar
> (**a row moves only when a shipped, shown-failing rule refuses the
> capability**) they stay GAP.

That is the whole answer. The census is not behind; it is holding a line.

**AND THE LINE IS THE SAME ONE THIS CAMPAIGN APPLIES TO ITS OWN INSTRUMENTS**
-- a check that cannot fail certifies nothing. A comment in a source file
cannot fail. Neither can a table in an audit document. Both were written by
people who had measured the thing; neither survives an edit by somebody who
has not.

## WHY CAUSES 1 AND 2 ARE RULED OUT, WITH THE MEASUREMENT

**Cause 1 -- unwired shaper. FALSE.** `linkedin_server/events.py` defines one
public shaper, `read_events_home`. It is called at `linkedin_server/server.py`
line 1553, inside `linkedin_events_home`, which carries `@mcp.tool()` at line
1495. Wired at `76514cf`, "the thirty-eighth tool, a READ".

**Cause 2 -- never banked. FALSE, and this is the one worth stating loudly.**
`N 180` is banked, and banked HONESTLY: it is the census's only
`COVERED-CANNOT-DELIVER` row, noted "PARTIAL -- one of a published 18". A wave
that wanted a bigger number had the chance to call that COVERED and did not.
The other seventeen rows are banked too -- in
`_audit/_census/blocker-assignments.tsv`, lines 289-304, one line each, each
naming its verdict and each explicitly declining to apply it.

## CAUSES 3 AND 4 ARE BOTH TRUE AND NEITHER IS THE BLOCKER

They are true, they are the same fact, and that fact is already recorded.

**The admission is exactly one address.** Measured 13:28 with `is_read_url`,
both controls firing:

    ADMIT    https://www.linkedin.com/events/
    ADMIT    https://www.linkedin.com/events
    REFUSE   /events/<id>/            /about/  /comments/  /attendees/
    REFUSE   /events/invited/   /events/past/   /events/discovery/
    REFUSE   /my-items/saved-events/  /event-creation/new
    REFUSE   CONTROL  /mypreferences/d/close-account
    ADMIT    CONTROL  /feed/

Every id above is a repdigit. No real event was addressed, and none was needed
-- `is_read_url` is a pure string predicate.

**The refusal of the deep addresses is DELIBERATE, not an absence.**
`readonly.py` line 642 is anchored `^https://www\.linkedin\.com/events/?$`, and
the comment above it lists what it declines to admit **by census row id** --
`N 184`, `C 92`, and "THE ATTENDEE LIST -- census rows N 188 and N 189 ... out
of scope by the same ruling that put `N 165` out of scope."

That matters because `N 165` IS `EXCLUDED-RULED` in the census today. **The
ruling those rows need already exists and has already been applied to their
twin.** What is missing is not the ruling. It is a rule.

---

## THE SIXTEEN, DECOMPOSED BY WHAT EACH ACTUALLY NEEDS

Every verdict below is the committed one from
`_audit/2026-09-05-events-surface-recosted.md` section 5, whose section 6
arithmetic closes on 18. I did not re-adjudicate a single row; I checked that
its verdict was still the document's and asked what would ENFORCE it.

    BANKED HERE (2)
      N 188  complete attendee list          EXCLUDED-RULED  a roster
      N 189  which connections confirmed     EXCLUDED-RULED  the same roster

    RULED BUT NOT BANKED, AND DELIBERATELY (2)
      N 191  message attendees                needs the roster AND a message
      N 192  reach attendees via InMail       needs the roster AND an InMail

    MISFILED -- a blocker change, not a state change (2)
      N 182  accept or ignore an invitation   the address is the invitation
                                              manager, refused on badge cost
      N 183  invitations from 1st-degree only a SETTING under preferences;
                                              readonly.py says so explicitly

    MEASURED-ABSENT for this account (3)
      N 186 N 187 N 190                       all presuppose an event he is
                                              attending. Measured zero

    GENUINELY AGAINST THIS SURFACE, BEHIND A DECISION NOBODY HAS MADE (7)
      N 181 N 184 N 185 N 193  M C57 M C58 M C92

## WHY N 191 AND N 192 ARE NOT BANKED, THOUGH THE DOCUMENT RULES THEM

Their refusal has TWO halves and this guard ships ONE. The roster half is now
enforced. The messaging and InMail half is `MESSAGING`'s surface, and
`messaging-measure` is live on it today.

**Banking a row on half its refusal is the inflation this census exists to
prevent.** `COVERED-UNFIRED` and `EXCLUDED-RULED` are separate states for the
same reason. They become bankable the moment a shipped guard refuses the
messaging half too, and whoever ships that should take them.

## THE SEVEN THAT REMAIN ARE ONE DECISION, NOT SEVEN PROBLEMS

Five of the seven sit behind two boundary patterns:

    /events/<id>/            N 181, N 184, N 185, M C58
    /events/<id>/comments/   M C92

**That decision is not this wave's to take and I did not take it.** The
recosting document declined it in the same words and for the same reason:

> An event page draws an organiser and, per the census, an attendee list --
> and the ruling that put `N 165` and `N 188` out of scope is about exactly
> that kind of page. **The boundary decides what may be OPENED; the shaper
> decides what may be SAID**, so the argument for `/events/<id>/` has to be
> made about the page and not inherited from the root's admission. I have not
> made it, and I have not opened one.

An events admission is a harder case than the search admission that got the
full blast-radius treatment today, because an event page carries an attendee
roster by construction -- and this repository has already ruled that
enumerating people is refused whatever url serves it.

**N 181 is the trap in that set and it is worth naming.** It reads like the
cheap one -- the organiser is visible on the root as text. It is not: measured
over all 18 rows, `/company/` hrefs per row is **0**, and `/company/` appears
in none of the page's 130 hrefs. The join would have to be done by MATCHING
NAMES, which is the construction this repository has already measured as
unsound on a different surface, where a uniqueness test over a set LinkedIn
had already filtered by the needle could not fail.

## WHAT I SHIPPED

`tests/test_the_events_boundary_is_root_only.py` -- 16 assertions, 0.11s.

* pins `/events/` and `/events` ADMITTED. **This is the vacuity control, not a
  courtesy:** a file of all-refused assertions passes perfectly against a
  boundary that refuses everything, a typo'd predicate, or an emptied
  allowlist.
* pins 13 deeper addresses REFUSED, each naming its census row.
* **SHOWN FAILING.** Installing an `/events/.*` family pattern in memory turns
  10 red including the vacuity control. Nothing was written to disk to prove
  it.
* **NAMES WHICH GATE HOLDS WHICH.** Only 9 of the 13 are held by the
  anchoring. Three are not under `/events/`. The fourth, `/events/invited/`,
  is held by the `/invite` SUBSTRING gate -- so that entry is annotated. A
  guard that cannot say which rule refuses an address gets read later as
  evidence for the wrong one, which is this session's most repeated defect.

## A NOTE ON THE SHARED TREE, MEASURED RATHER THAN REPORTED

`_audit/_census/network.md` had a SECOND live writer while I was in it:
`groups-reader`'s `N 162` at line 493, against my rows at 534-535. The derived
map is rebuilt from the whole census, so a plain rebuild-and-commit would have
carried their row under my message.

**Staged with `git apply --cached` on my hunks only.** Their working tree was
never touched and their row is not in my commit. Two foreign files were also
sitting STAGED in the shared index (`content-tail`'s taint fix and
`small-measures`' `REGIONS` declaration); both were unstaged before my commit
and **restored to the index byte-identical afterwards**, verified by blob
hash. Neither is mine to commit and neither was harmed.

## WHAT I DID NOT DO

* **No page was opened and no browser was started.** Every measurement here is
  either a pure string predicate or a read of a committed file.
* **No boundary was widened.** The guard pins the boundary where it already
  stood.
* **No RSVP, no registration, no comment, no invitation.** Ten of these
  sixteen rows are WRITES against other people; none was exercised.
* **No event id in this document or the guard is real.** They are repdigits,
  and the one slug form carries a sanctioned synthetic token.
* **I did not re-adjudicate the rows.** The verdicts are the committed ones.
  This wave supplied enforcement, not judgement.
