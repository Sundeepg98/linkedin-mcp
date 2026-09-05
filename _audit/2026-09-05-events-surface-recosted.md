# EVENTS-SURFACE, re-costed row by row

**CORRECTS:** `_audit/2026-09-05-groups-events-precondition.md` -- the events root DOES draw a "Your events" region; it is present, structurally complete and EMPTY for this account, which is a different finding from the surface not existing and retires different rows

Wave: events-surface. Date: 2026-09-05. Every number here was taken by an
instrument carrying a control that fired, and the controls are listed at the
end with what each one caught.

---

## 1. WHAT THE LEDGER SAID, AND WHAT IT TURNS OUT TO BE

`_audit/2026-09-03-linkedin-gap-blockers.md` row 13: **`EVENTS-SURFACE`, 18
rows, 7R/11W, boundary "allowlist +1, WriteSpec", ruling YES, cost 9,
rows/cost 2.00, queue MEASURE.** It names no rows. Derived from
`_audit/_scratch/_route-gap-rows.tsv` and accepted only because the derivation
reproduces the ledger's own arithmetic exactly:

    READS  (7)   N 179 180 181 183 184 188 189
    WRITES (11)  N 182 185 186 187 190 191 192 193  +  M C57 C58 C92

**IT IS NOT AN EIGHTEEN-ROW BLOCKER. Eight rows are against this surface, and
one of those eight shipped today.** Three are filed against the wrong blocker,
four were already ruled out by a ruling this repository has made, and three
have no subject on this account. Section 5 is the row-by-row, and section 6 is
the arithmetic.

## 2. THE PREMISE I WAS HANDED, AND THE MEASUREMENT THAT REFINED IT

I was told, as settled and not to be re-derived: **no "events you are
registered for" surface exists on LinkedIn**, and instructed to retire the
rows presupposing one.

The first instrument I ran found an `h2` reading `Your events` in the same
capture that finding was taken from, between the page heading and the two
sections the precondition document reports.

**THAT IS A REFINEMENT AND NOT A CONTRADICTION, AND THE DIFFERENCE DECIDES HOW
ROWS RETIRE.** Bounded by ELEMENT rather than by offset -- which my own first
attempt got wrong, producing a plausible 98-character "empty state message"
that was markup -- the region is a card section with a header carrying the
heading, a body, and a footer:

    body   inner HTML 29 characters,  0 of text,  0 event anchors
    footer inner HTML 60 characters,  0 of text

Both hold a framework empty-binding comment.

**A RENDERED CONTAINER WHOSE LIST BINDING IS EMPTY IS NOT AN UNRENDERED
CONTAINER.** A section that had not hydrated would carry a skeleton or would
not be in the document. This one is structurally complete and holds a list of
length zero.

### 2a. THE OBJECTION TO THAT SENTENCE, AND THE MEASUREMENT THAT ANSWERS IT

**A CONTAINER ARRIVES BEFORE ITS CONTENTS.** A capture can hold a container
plus a shimmer bar and no text, and a container-only reader then publishes a
confident wrong answer. `unhydrated` is not `absent`. The objection was put to
this wave mid-flight and it is the right one to put, because the first version
of the corroborator did not close it: **full sibling cards prove the PAGE
hydrated, not that THIS card did.** Different cards hydrate from different
calls.

So the reader stopped inferring from the absence of rows and started reading
the card's BODY. One reading, live, one page, one instrument:

    card 0  'Your events'          body_found=True   text 0     elements 0
    card 1  a promoted section     body_found=False  --         --
    card 2  'Recommended for you'  body_found=True   text 1567  elements 432

**THE THIRD LINE IS THE CONTROL AND IT IS WHAT MAKES THE FIRST A READING.**
The same selector, on the same page, in the same pass, returns 1567 characters
and 432 elements for one card and nothing at all for another. A reader blind
to body content could not produce that contrast; a shimmer would have shown
elements; a rendered empty state would have shown text. Card 0 has neither.

The reader now REFUSES rather than answering zero in each of those cases --
`body_not_empty` when anything is in there, `body_unreadable` when the body
cannot be found. Reaching the one verdict that carries a zero takes four
independent facts, and `tests/test_events_home_reader.py` drives a shimmer and
a rendered empty state through it to show each refusing.

**AND THE READING WAS TAKEN TWICE PER LOAD, AT DIFFERENT MOMENTS OF IT.** Two
readings across two loads cannot separate "stable" from "always half-built";
one early reading and one after waiting for the network can. Four readings,
two loads, all four agreeing at 18 rows and the same verdict.

Card 1 reads `body_found=False` because the promoted card is built from a
different class family. It costs nothing here -- only the self-scoped card's
body is consulted -- but it is recorded rather than hidden, because a selector
that silently misses a third of the cards it is pointed at is worth knowing
about before somebody reuses it.

**HOW THE PREVIOUS PASS MISSED IT, because it was not carelessness.** That
pass assigned anchors to their nearest preceding heading. **A heading with
zero anchors under it is invisible to an anchor-assignment pass** -- it does
not appear in the output at all, at any count. The instrument was answering
"which section is each event in", and for that question it was right.

**WHY THE DISTINCTION IS WORTH A DOCUMENT.** "The platform has no such
surface" retires a row as impossible in principle, permanently, for anybody.
"The surface exists, on an address this server may already open, and is empty
for this account" leaves the row REACHABLE, makes its answer today a measured
zero, and makes the retirement REVERSIBLE the day he registers for something.
Those are different ledger entries.

## 3. WHAT THE ROOT DRAWS, MEASURED TWICE BY TWO INSTRUMENTS

`scripts/_probe_events_surface_shape.py` parses the gitignored capture with
regular expressions. `linkedin_server/events.py` walks the live DOM with
locators. They are different instruments and they agree:

    card 0   'Your events'          0 rows    0 event anchors
    card 1   a promoted section     3 rows    9 event anchors
    card 2   'Recommended for you' 15 rows   45 event anchors
                                   --------  ---------------
                                   18 rows   54 anchors

54 is the count `dom.read_surface_census` measured live on this page in a
different session, and 18 is the number of distinct addresses. The offline
probe REFUSES rather than reporting if it does not reproduce 54.

**ONE ADDRESS SHAPE, AND ONLY ONE.** All 54 hrefs are `/events/<id>/`. Zero
carry a query or a fragment. There is no link to `/events/<id>/comments/`, no
`/events/<id>/about/`, no `/search/results/events/`, no topics route, and no
route out to any self-scoped events surface: `my-items` 0, `registered` 0,
`attending` 0, `network-manager` 0 across 130 hrefs.

**NO RSVP CONTROL EXISTS ON THIS PAGE.** `Attend`, `Interested`, `Going` and
`Register` occur ZERO times in 1294108 characters.

## 4. THE ONE CONTROL AN EVENT ROW CARRIES, AND WHAT IS INSIDE IT

Each of the 18 rows carries exactly one `<button>`, and all 18 carry the same
class tokens: `artdeco-dropdown__trigger`, and
`events-components-shared-support-share__share-button`. It is a disclosure
widget -- `aria-expanded`, an svg for content -- and `role="menu"` occurs zero
times in the document, so **the menu is not in the DOM until pressed.**

`scripts/_probe_events_row_menu.py` pressed one, on a RECOMMENDATION row, and
pressed nothing inside it.

    aria-expanded          'false' -> 'true'
    [role="menu"]              0   ->  1
    [role="menuitem"]          0   ->  5

    Copy link          Repost to Feed     Send in a message
    Facebook           Twitter

**THIS IS THE ROUTE FOR `N 193` AND IT COMES WITH ITS OWN RISK CLASSIFICATION
ALREADY ATTACHED.** Two of the five items are acts this server already gates:
`Repost to Feed` is `publish_post` and `Send in a message` is `send_message`.
So a WriteSpec for `N 193` is not a new risk category to be argued from
scratch -- **it inherits, verbatim, the treatment of the two most tightly
gated writes in this package.** The third, `Copy link`, sends nothing and is
the only item on that menu a read could ever touch.

The press was taken where the groups wave declined its equivalent, and the
difference is stated in the probe rather than assumed: that press would have
been on a row for a group he BELONGS TO, to read a label it did not need; this
one is on an event he has no relationship with, opens a local menu, sends
nothing, and is the only route to a row otherwise costed blind.
`SANCTIONED_MUTATIONS`'s second entry already settles this class in this
repository's own words -- *counted by EFFECT rather than by verb, a view
filter is a read.*

## 5. THE EIGHTEEN ROWS, ADJUDICATED

| row | capability | verdict | why |
|---|---|---|---|
| `N 179` | search events by keyword, Events tab | **MISFILED** | the address is `/search/results/events/`. `readonly.py`'s own admission comment already assigns it to `SEARCH-RESULTS-SURFACE`, blocker 6, which is queued DECIDE with a consent ruling prepared. It is not blocked by the events surface |
| `N 180` | events recommended from interests, Pages followed, and what the network is attending | **REACHABLE NOW, part shipped** | this is what the root draws and what the admission comment names as its censused content. `events.read_events_home` counts it today: 18 rows across two sections. Per-event CONTENT needs a shaper ruling -- see below |
| `N 181` | events hosted by Pages you follow | **NEEDS RULING** | the organiser is on the page (each row's control block reads `<organiser> N attendees`). The join against `linkedin_followed_companies` can happen INSIDE the process, so the ruling is whether an organiser name may leave it or only the join's result may |
| `N 183` | receive event invitations only from 1st-degree connections | **MISFILED** | a SETTING, under preferences, not under `/events/`. `readonly.py`'s admission comment says so explicitly. Whether the setting exists is unmeasured and belongs to the settings family |
| `N 184` | reach an event through its URL | **NEEDS BOUNDARY** | needs `/events/<id>/`. Measured: that is the ONLY sub-route LinkedIn links from the root, 54 of 54 anchors, so the ledger's "allowlist +1" is exactly one pattern for this row |
| `N 188` | complete attendee list of an event | **EXCLUDED-RULED** | a member roster. Already ruled out in `readonly.py`'s admission comment, by the same ruling that put the group member list (`N 165`) out of scope |
| `N 189` | which 1st-degree connections have confirmed attendance | **EXCLUDED-RULED** | the same roster, filtered. Same ruling |
| `N 182` | accept or ignore an event invitation | **MISFILED** | no invitation control exists anywhere on `/events/`. The address is the invitation manager, which this server refuses on badge-cost grounds. Corroborated: the feed's pending-invitation badge carries NO count, so there are none to accept |
| `N 185` | attend an event you accepted | **NEEDS BOUNDARY, subject absent** | no RSVP control on the root, and the accepted invitation it presupposes does not exist. Its control, if any, lives on `/events/<id>/` |
| `N 186` | invite 1st-degree connections to an event you are attending | **MEASURED-ABSENT for this account** | presupposes an event he is attending. Measured zero, corroborated by full sibling cards on the same page |
| `N 187` | filter that invitee list by location, company, school, industry | **MEASURED-ABSENT** | one step deeper than `N 186` and unreachable for the same reason |
| `N 190` | hide your attendance from non-attending connections | **MEASURED-ABSENT** | presupposes attendance |
| `N 191` | message attendees who are already connections | **EXCLUDED-RULED** | needs the attendee roster, which is ruled out |
| `N 192` | reach non-connection attendees via InMail | **EXCLUDED-RULED** | the InMail half under R9 already; the attendee-targeting half needs the same ruled-out roster |
| `N 193` | share an event you are attending with your network | **MECHANISM MEASURED, subject absent** | the share menu is now enumerated: five items, of which two are `publish_post` and `send_message`. The row's subject -- an event he is attending -- is zero |
| `M C57` | create a LinkedIn Event | **NEEDS SURFACE** | no create control on the root. The `Create an event` control recorded in the census sits in the POST COMPOSER, a different surface with its own blocker, and the act is publish-class |
| `M C58` | attend or leave a LinkedIn Event | **NEEDS BOUNDARY, subject absent** | the same missing RSVP control as `N 185`. Attending puts him on a public attendee list, which the census row already flags |
| `M C92` | comment on an Event and reply to Event comments | **NEEDS A SECOND BOUNDARY PATTERN** | `/events/<id>/comments/`, which LinkedIn does NOT link from the root -- measured, 1 distinct path shape over 54 anchors. So this row needs a pattern nothing on an open page points at |

## 6. THE ARITHMETIC, AND WHAT THE "ALLOWLIST +1" ACTUALLY BUYS

    MISFILED, leave this blocker              3    N 179, N 183, N 182
    EXCLUDED-RULED already                    4    N 188, N 189, N 191, N 192
    MEASURED-ABSENT for this account          3    N 186, N 187, N 190
    ------------------------------------------------------------------
    genuinely against this surface            8    N 180 181 184 185 193
                                                   C57 C58 C92
    of which ALREADY DELIVERED                1    N 180's count half

**`EVENTS-SURFACE` IS AN EIGHT-ROW BLOCKER, NOT AN EIGHTEEN-ROW ONE.** At the
ledger's cost of 9 that is a rows/cost of 0.89, not 2.00 -- it drops from
thirteenth in the ledger's ranking to below its median. **That is the single
most consequential number in this document**, and it comes from adjudicating
rows rather than from measuring anything new about LinkedIn.

**THE BOUNDARY COST IS TWO PATTERNS, NOT ONE, AND THEY BUY DIFFERENT THINGS.**

    /events/<id>/            unblocks N 184, N 185, C58   -- 3 rows
    /events/<id>/comments/   unblocks C92                 -- 1 row

The admission comment for `/events/` predicted exactly this ("it is the row
that proves the ledger's *allowlist +1* for this blocker was short"), and the
prediction is now measured rather than asserted.

**NEITHER PATTERN IS TAKEN HERE.** An event page draws an organiser and, per
the census, an attendee list -- and the ruling that put `N 165` and `N 188`
out of scope is about exactly that kind of page. **The boundary decides what
may be OPENED; the shaper decides what may be SAID**, so the argument for
`/events/<id>/` has to be made about the page and not inherited from the
root's admission. I have not made it, and I have not opened one.

## 7. THE COST OF THE READ, AND WHY THE BOUND IS NARROWER THAN IT LOOKS

Read feed -> events -> feed, so both ends of the comparison came off the same
nav. The pending-invitation badge and the messaging badge were both READ at
both ends, and neither moved.

**THREE CAVEATS, ALL OF THEM MINE TO STATE:**

1. **Both counters stood at zero.** `shape.invitation_badge` already records
   why that is weak -- a badge at zero cannot distinguish "the page consumed
   nothing" from "there was nothing to consume".
2. **The events root renders the nav WITHOUT either count on it** (the
   invitation link draws with no badge, the messaging link with no label). So
   an after-reading taken on the page itself is a REFUSAL, not a number. The
   first version of this probe compared exactly that refusal against a
   readable feed reading and printed "unchanged". **Two refusals are not a
   pair**, and the probe now says so in its own output.
3. **The events root draws no counter of its own**: `aria-haspopup` 0,
   `role="menu"` 0 before any press, `role="dialog"` 0. So there is nothing
   events-specific to watch, and this is the whole of what "did the load cost
   anything" can mean at this address.

## 8. WHAT I DID NOT DO

* **I did not open `/events/<id>/`.** It is not on the allowlist and admitting
  it is a ruling about a third party's page, not a measurement.
* **I did not widen `readonly.py`.** The boundary digest chain is untouched by
  this wave; nothing here needs recomputing.
* **I did not press anything inside the share menu**, and no write, token or
  confirm was created anywhere in this wave.
* **I did not add a fixture.** The capture stays gitignored. The reader's
  tests use a stub carrying LinkedIn's structural class strings and this
  file's own invented headings -- no event title, organiser or identifier.
* **I did not build a per-event content reader for `N 180`.** Counts ship;
  titles, dates and organisers are third-party content and want the ruling in
  row `N 181` first.
* **I did not touch `dom.py`.** The reader was appended there and lifted back
  out byte for byte when another wave's 121 uncommitted lines turned up in it.

## 9. PROVENANCE

| instrument | control | outcome |
|---|---|---|
| `scripts/_probe_events_surface_shape.py` | anchors must total 54, the live census count; an impossible attribute must find 0 | both passed; the run REFUSES and voids every tally if the first fails |
| `scripts/_probe_events_home_live.py` | dark-mode census 20 at the START and the END; two readings must agree | 20 and 20; agreed on all four fields |
| `scripts/_probe_events_row_menu.py` | refuses unless exactly 18 share triggers; menu selectors tallied BEFORE and AFTER so the press is shown to have caused the change | 18 found; 0 -> 1 menu, 0 -> 5 items |
| `linkedin_server/events.py` | the zero requires four facts: card present, no rows, a body holding neither text nor elements, and a non-empty sibling | verdict `empty_beside_full_siblings`; the same body reader returns 1567 chars / 432 elements on a sibling card in the same pass |
| `tests/test_events_home_reader.py` | the stub is shown discriminating `~=` from `*=` before anything is asserted through it | 18 vs 54, so the regression test can fail |
| the settle re-read | one reading on landing, one after waiting on the network, SAME load | unchanged, on both loads -- four readings, all agreeing |

**THE ONE DEFECT FOUND IN MY OWN WORK, AND IT LOOKED CORROBORATED.** The row
selector first matched `[class*="discovery-card"]` and read **54 rows where
there are 18**, because each row holds a `__details` and a `__controls`
descendant whose class tokens begin with the row's own. The same run reported
`rows` and `event_links` as 9/9 and 45/45 -- **two selectors agreeing
exactly** -- because the page draws three anchors per row and the broken
selector counted three sections per row. Two instruments agreeing is evidence
only when their errors are independent. It is now a class-TOKEN match, pinned
by a test that drives the broken form through the same stub and asserts 54
comes back.
