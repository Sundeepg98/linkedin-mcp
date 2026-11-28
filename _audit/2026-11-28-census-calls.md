# Lane census-calls28 (lane A): the census calls, no code

Lane A of the census wave plan of 2026-11-28 (`census-plan28`, section 3), branched
from master `9ec91965`. Census only: no file under `linkedin_server/` is touched, nor
`capture-queue.tsv`, `INSTRUMENTS.md` or the rulings register by hand. Nothing loaded
LinkedIn; no browser, port or session was touched.

Evidence classes: VERIFIED means read on disk in this lane, MEASURED means an
instrument counted it on a tracked file in this lane, DERIVED means computed from
what was read, UNVERIFIED means not checked. People by role only.

STATUS: IN PROGRESS, AND HOLDING FOR THE MERGE ORDER. J 86's move at `118d4008` (on
this lane's branch, `census-calls28`, and nowhere on `master` until the orchestrator's
merge; its subject is "census: J 86 COVERED-UNFIRED by D6 on P I14's tool -- the lane-K
ledger's call, made") was certified by lane CI run 46145558412 and full-matrix run
46146396940, both success, read by sha. After hygiene28 reached master (`b7db2f7a`) the
branch merged it, and N 3's move, M C11's step and the M C65 and M C91 notes were
applied (section 1). The orchestrator's merge order puts this lane after the live
lane's r2, with master merged in before the certifying run, so the final certification
waits on that. N 61, N 50, rank 23's rows and the new capture steps wait on Q2 to Q5.

## 1. The order, and what holds what

| item | rows | outcome | where |
|---|---|---|---|
| 1. J 86, the D6 call on P I14 | J 86 | GAP -> COVERED-UNFIRED, committed | section 2 |
| 2. the code reads | M C65, M C91 | both stay GAP: neither tool reaches a group post | section 3 |
| 3. D6 calls | N 3 | GAP -> COVERED-UNFIRED, applied after hygiene28's merge | section 4.1 |
| 3. D6 calls | N 50 | split (Q2, answered): N 50 GAP -> COVERED-PROVEN by D6; N 50b enters at GAP | section 4.2 |
| 4. the orchestrator's ruling | N 61 | GAP -> MEASURED-ABSENT, applied with queue rank 83's line (Q3, answered) | section 5 |
| 5. the re-judges | M C11 | step re-pointed and cell noted, applied | section 6.1 |
| 2. the code reads | M C65, M C91 | the cell notes, applied | section 3 |
| 5. the re-judges | rank 23's 13 rows | all stepped PRECONDITION, with queue rank 23's line (Q4, answered); no state moves | section 6.2 |
| 5. the re-judges | J 3, J 17, J 151 | stepped to a new place capture, `C-SRCH-2b` (Q5, answered) | section 6.3 |
| 5. the re-judges | M C65, M C91 | stepped to a group-feed capture, `C-GROUP-POST-1` (Q5, answered) | section 6.4 |

WHAT "HELD" MEANS HERE. The held edits exist as a tested ready patch in the lane's
scratch directory (gitignored, so this record states what each edit is, and section 5.2
and 6 give the exact lines): an apply script anchored on each line's own text, run in
steps `n3`, `n61`, `msg` and `delta`, refusing on any anchor it cannot find exactly
once. A queue step exists only for the queue's owner, and is never run by default.

THE BASE HOLD. The brief puts `network.md` and `messaging-and-content.md` after
hygiene28's merge, because that lane edits both. Master was `9ec91965` at every check
until 18:34 IST, without hygiene28, so every edit to those two slices was written as a
ready patch under the lane's scratch directory and held, with "the rest" the brief
held beside them. At 18:57 IST the orchestrator's note said master was `b7db2f7a`,
hygiene28's head, and that those two slices could go ahead. The branch merged master
then (a merge, not a rebase), and the patch's steps `n3` and `msg` applied on the
merged tree with every anchor found once.

## 2. J 86: COVERED-UNFIRED by D6 on P I14's tool

The lane-K ledger (`_audit/2026-09-28-lane-k-ledger.md`, section 3) lists six rows "a
shipped tool may already reach by D6-CAPABILITY-OVER-AFFORDANCE", among them "`J 86` on
`P I14`", as "a census call for the row's owner, not made here". This lane makes it.

The bar (D6, `_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`): the
package delivers the same capability payload by its own sanctioned routes, the row names
them, and it rests on their proofs: PROVEN if live-proven, else UNFIRED.

VERIFIED on this tree, each read in the source:

- `linkedin_mark_company_interest(job_id, confirm_token)` is spec `mark_company_interest`
  in `writes.SANCTIONED_WRITES` and `writes.PERFORMABLE` (36 performable actions,
  imported), behind `writes_enabled()` and the single-use grant. `P I14` rests on it,
  COVERED-UNFIRED since lane L7 (2026-09-24), never fired.
- It presses the control J 86's own Help article documents. The gate requires one
  'I'm interested' button in a posting's About-the-company card, found beside the link
  to `a1380509` (`company_interest.HELP_ARTICLE_FRAGMENT` is `/answer/a1380509`); the
  spec's `direction_source` says this was MEASURED on three tracked posting captures.
  J 86 cites `a1380509` and `a1427386`.
- The spec cites J 86 by id twice: `reversibility_evidence` ("a1380509, cited by census
  row J 86") and `spends` ("census row J 86 quotes its Help article as 'max 50, expires
  1 year'. Not measured here").
- The payload: the tool's docstring says the signal goes to that employer's recruiters,
  is not a post, and his network is not told -- J 86's "privately signal interest".

So D6 holds, and more strongly than it needs to: the route is not a substitute for
J 86's affordance, it is that affordance, on a posting. The route is a posting by that
employer, named by its job id; whether a company Page draws the same control is not
measured here, and no shipped tool presses it there, so the cell names the one route
that delivers. The two rows are one capability counted in two slices, as J 72 and P M4
are (the plan, section 5).

THE STATE IS COVERED-UNFIRED, because the route never fired. THE HOLD IS
OPERATOR-NAMES-THE-TARGET: the act is for one employer's recruiters, so its proof fires
only at a posting he names, after `P I14`'s two prerequisites (a company he names, and
`P I15`'s ON-state control captured so that the undo exists before the act). The jobs
slice's per-row table has no R/W column, so `reader_closable_blockers.direction_of`
reads J 86 as `unknown` and `ruling_holds.hold_of` adds no write hold by itself; the
cell cites `HELD BY` `OPERATOR-NAMES-THE-TARGET` in the marker form, as J 128 and
J 163 do.

What moved with it, each MEASURED:

- `jobs.md`: the cell, and a DELTA paragraph from `scripts/count_census_states.py`
  (COVERED-UNFIRED 27 -> 28, GAP 104 -> 103, stated rows 175).
- `next-step.tsv` and `jobs-directions.tsv`: J 86's line leaves each, because both hold
  still-GAP rows only.
- `write-classes.tsv`: no J 86 line existed (its class read `-`), so nothing changes.
- `blocker-assignments.tsv` is the committed evidence the map is derived from and is
  unchanged, as at the N 93 precedent; `blocker-map.tsv` is regenerated.
- The pins, section 7.

## 3. The code reads: M C65 and M C91 stay GAP

The question (brief, item 2): do `linkedin_comment_on_item` and `linkedin_react_to_item`
reach a GROUP post by their own route? The answer is NO for both, so the two D6 calls
the ledger named ("`M C65` on `M C25`", "`M C91` on `M C32`") fail and both rows stay
GAP.

VERIFIED in the source on this tree:

1. BOTH TOOLS ACT ONLY ON ONE ADDRESS SHAPE. Each spec's `url_pattern` is
   `^https://www\.linkedin\.com/feed/update/urn:li:[A-Za-z]+:[0-9]+/$`
   (`writes.py`, `linkedin_comment_on_item` and `linkedin_react_to_item`), enforced at
   the write door by `assert_write_url`. The read boundary admits the same permalink and
   nothing wider (`readonly.py`, the ONE ITEM PERMALINK entry), and the readers that
   emit an item key require the same shape (`dom.py`, `urnShape` in
   `ACTIVITY_ITEMS_JS` and in the named profile's activity read, and `NAMED_ITEM_KEY`).
2. NO SHIPPED TOOL HANDS OUT A GROUP POST'S KEY.
   - `linkedin_group_page` returns "A verdict and counts, never a post" (its docstring).
   - `linkedin_publish_group_post` is receipt-only: what Post leaves in a group is not
     captured, and no key comes back.
   - `linkedin_my_activity_items` reads his own activity page and
     `linkedin_read_named_profile` the Activity section of a profile he names; no
     capture on disk shows a group post on either.
   - `linkedin_group_memberships`, `linkedin_group_members` and
     `linkedin_search_groups` return groups or members, not posts.
3. THE GROUP FEED DOES NOT DRAW THAT ADDRESS AT ALL. `N 175`'s cell records a live
   fire of 2026-09-21 on three groups this account belongs to: a route census of those
   pages, 86, 35 and 47 anchors, found `/feed/update/` zero times -- "A group feed's
   post permalinks do not wear that route" (`linkedin_server/group_page.py` says the
   same, with its receipt `scripts/_probe_group_feed_permalinks.py`). Session 11's
   group skeletons on disk blank every entity path and `data-urn`, so they can neither
   confirm nor contradict that.

So the address these two tools are confined to is not the one a group post wears on its
own surface, and no route in the package supplies a group post's key: the payload is
not delivered by the package's own sanctioned routes, and D6 does not discharge either
row. Whether a group post also has a `/feed/update/` permalink somewhere else is
UNVERIFIED; no capture shows one.

WHAT EACH ROW NEEDS FIRST: the route a group post's permalink wears, and its comment and
reaction controls, captured on the feed of a group he belongs to. That is also `N 175`'s
reopener ("`anchors.ROUTE_TABLE` gaining the route a group post permalink actually
wears"). The cell text and the re-pointed step are held (sections 1 and 6.4): the cells
are in `messaging-and-content.md`, and a step to a capture needs a capture-queue line,
which this lane does not write.

## 4. N 3 and N 50 (held)

### 4.1 N 3: COVERED-UNFIRED by D6, applied after hygiene28's merge

The ledger's call "`N 3` on `N 1`". N 3 is "Send an invitation from People You May
Know"; its blocker is the `/mynetwork/` surface's unmeasured badge cost. The payload is
an invitation to a person LinkedIn suggests, and the package sends one by two
sanctioned routes, neither from `/mynetwork/`:

1. `linkedin_send_invitation(profile, confirm_token)`, `N 1`'s tool (COVERED-UNFIRED,
   never fired). It presses the one invitation control in his own profile's rail
   whose card links to the profile he names (`dom.rail_invite_control_selector`).
   MEASURED in this lane, on the two tracked skeletons of his profile
   (`tests/fixtures/live11/in_me_profile.html`,
   `tests/fixtures/live14/in_me_profile.html`): 5 of the 6 buttons whose text reads
   `Connect` sit in the section whose `h2` reads 'People you may know', and the sixth
   under a heading the skeleton blanks. So that rail IS LinkedIn's People You May Know
   list, drawn on his profile. The skeletons blank every name-bearing label to `x`
   (125 of 176 labels), so they cannot show the invitation label's own shape; `N 1`'s
   cell holds that measurement, on keyed captures.
2. `linkedin_connect_from_profile(profile, confirm_token)`, `N 4`'s route by D6
   (COVERED-UNFIRED, never fired), for a suggestion the rail does not draw.

Both are UNFIRED, so N 3 is COVERED-UNFIRED. It is a W row, so `ruling_holds` holds it
by OPERATOR-NAMES-THE-TARGET with no marker: it fires only at a person he names. Its
write-class line keeps its R2 class and becomes `built:send_invitation`
(`send_invitation` is in `writes.PERFORMABLE`), on the `N 4` precedent, so the class
split `test_write_classes.py` pins (16, 33, 316) does not move.

The probe that counted the buttons is DISPOSABLE (lane scratch, never shown failing).
It walked each tracked page with Python's `html.parser` and counted, per nearest
enclosing `section`'s first `h2`, the buttons whose text is exactly `Connect`.

A FINDING FOR `N 4`'s OWNER, not acted on. `N 4`'s write-class line says its undo is
"NOT through this server ... withdrawing is destruction, in PERMANENTLY_FORBIDDEN, and
the Sent manager is a forbidden address". On this tree `linkedin_withdraw_invitation`
withdraws one pending invitation he sent, from the Sent tab (census row `N 10`,
COVERED-UNFIRED), and `linkedin_sent_invitations` reads that tab. N 3's held line
states that undo; `N 4`'s line is not this lane's to edit.

### 4.2 N 50: STOPPED, because disk disagrees with the plan's premise

N 50 is "Follow a company or school via an off-site Follow button". The plan expected
COVERED-UNFIRED, "D6 on `N 47`". Two facts on this tree say otherwise.

- THE SCHOOL HALF IS DELIVERED BY NOTHING. `linkedin_follow_company` acts on
  `/jobs/view/<id>/` (a posting's employer), and `linkedin_follow_company_page` acts on
  `/company/<numeric id>/` (`writes.py` url patterns). No write spec acts on
  `/school/`; the boundary admits `/school/<slug>/` for reading only (`readonly.py`),
  and `J 112`'s cell says a school's slug is a name. Whether `/company/<id>/` reaches
  a school by its numeric id is UNVERIFIED.
- THE COMPANY HALF RESTS ON A LIVE-PROVEN ROUTE. `linkedin_follow_company` was fired
  and banked in the live lane's session 8 (`N 46` and `J 103` are COVERED-PROVEN on
  that fire). D6 says a row rests on its routes' proofs, "COVERED-PROVEN if they are
  live-proven"; `N 80`, `N 133` and `N 155` were banked PROVEN that way.

So the two halves need different states, and COMPOUND-ROW-SPLITS-ONLY-ON-STATE splits
such a row. Every recent split was the orchestrator's own per-row call (`N 26` to
`N 26b` on the call of 17:46, 2026-09-28; `J-110-SPLITS-HOME-AND-POSTS`;
`J-114-SPLITS`), so the lane asked (Q2, section 9).

APPLIED on the orchestrator's answer (19:04 IST), which accepted the recommendation, in
the `N 26` -> `N 26b` shape:

- `N 50`, renamed to its company half, "Follow a company via an off-site Follow
  button": GAP -> COVERED-PROVEN by D6, resting on `linkedin_follow_company`'s
  session-8 fire. Its write-class line stays R1 as `built:follow_company`, and its
  next-step line leaves.
- `N 50b`, "Follow a school via an off-site Follow button", enters at GAP. BLOCKER
  SCHOOL-PAGE-SURFACE, as `J 112`, `N 99` and `N 100` carry. Its write-class line is
  R1, `queued:SCHOOL-PAGE-SURFACE`. Its step is `TARGET:a school Page he names`, on
  queue rank 13, `t-named-school`, whose rows went from 3 to 4 (rows per load 3.0 ->
  4.0, its one load unchanged). That is the queue edit `check_next_step.py` needs in
  the split's own commit. Whether that line's address, the school's `people/` tab,
  draws the school's own Follow control is UNVERIFIED; the school root
  `/school/<slug>/` is admitted too.
- MEASURED: network.md stated rows 216 -> 217 and COVERED-PROVEN 29 -> 30, GAP 127
  unchanged (`count_census_states.py`). The census row pin moved 784 -> 785, one row
  added and none removed (`scripts/pin_census_rows.py --write`, and the two literals
  in `test_the_census_row_total_is_pinned.py` and
  `test_a_census_locator_names_its_row.py`). The write-class split moved to (17, 33,
  316) on 366 lines, read from the table (`test_write_classes.py`'s literal).
- THE DENOMINATORS: stated rows 784 -> 785, capabilities 797 -> 798, and the
  achievable surface 709 -> 710 (section 7).

## 5. N 61 (held)

### 5.1 NO FOLLOWED-HASHTAGS VIEW IS DRAWN

The orchestrator's ruling on the plan's section 2b, made 2026-11-28 at 17:1x IST (as
the lane's brief gives the time), for the integrator to copy into the rulings register:

- id: N61-FOLLOWED-HASHTAGS-MEASURED-ABSENT
- claim: N 61, viewing his followed hashtags, is MEASURED-ABSENT on two independent
  observations: the network manager's own nav draws no hashtags entry and no
  hashtag-feed link, and a hashtag's results draw no follow control and no hashtag
  feed.
- binds: census row N 61
- under: MEASURED-ABSENT-OR-PRECONDITION, on the precedents
  GROUP-SEARCH-MEASURED-ABSENT and KEYWORD-FIELDS-MEASURED-ABSENT
- reopener: if rank 152's `/feed/hashtag/` load (for N 59 and N 60, under
  HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS) ever draws a follow control or a
  followed-hashtags list, N 61 reopens.
- citations, both VERIFIED in this lane:
  1. `_audit/2026-11-27-live-session-13.md`, load 3 (`tests/fixtures/live13/following.html`):
     "the network manager's own nav draws `people-follow` (2) and no hashtags entry;
     0 hashtag-feed links (N 61)", and its finding 5, "The network manager no longer
     lists followed hashtags in its own nav".
  2. `_audit/2026-11-27-msg7.md`, section 5.1 (live session 12, load 13): "A HASHTAG'S
     RESULTS DRAW NO FOLLOW CONTROL AND NO HASHTAG FEED" -- 0 of 92 links reach
     `/feed/hashtag/`, and 0 buttons are named exactly `Follow`.

APPLIED after the orchestrator's answer to Q3 (19:04 IST): the queue rule is amended
for this lane, for exactly what `check_next_step.py` needs in the same commit as the
row's move, so rank 83's line leaves with N 61. Measured on the move: network.md
MEASURED-ABSENT 5 -> 6 and GAP 128 -> 127 (its DELTA paragraph); the pointer guard 63
of 63 after `--pin`; `check_next_step.py` GREEN at 503; `check_exclusion_basis.py` 75
of 75.

### 5.2 What the move touches, and the one piece this lane could not do alone

Written as the held patch's `n61` step (section 1), each piece on its precedent (net7's
N 93 and N 27, msg7's M C70):

- `network.md`: the state, and the reason cell. Its positional "Same uncertainty" is
  struck for evidence of its own, as `M C63`'s 'same' was, so N 61 leaves the pointer
  graph. No row below it reads its argument through it (`pointer-graph.tsv`).
- `exclusion-basis.tsv`: an `M+` line whose source is this section's heading.
- `next-step.tsv` and `read-addresses.tsv`: N 61's lines leave (it was NEEDS-SESSION
  in bucket 3).
- `scripts/triage_read_gap_rows.py`: both N 61 entries leave, the TRIAGE one and the
  `MEASURED_PAST_BY_BUCKET3` one (its test holds that table's keys inside TRIAGE), with
  a LEFT THE READ-GAP SET note.
- `scripts/measure_pointer_graph.py`: its calibration literal "PASS -- all 64 pinned
  pointers" becomes 63, with a history line, as at `M C63`'s and `M M2`'s write-outs;
  then `--pin` re-pins `pointer-graph.tsv`. The 63 is to be MEASURED by `--check`, not
  assumed.
- THE CAPTURE QUEUE, WHICH THIS LANE DOES NOT WRITE. Rank 83,
  `admit-mynetwork-network-manager-people-follow-following`, lists N 61 alone with
  needs `-`, and `scripts/check_next_step.py` requires every member of such a line to
  carry the step `CAPTURE:<that line>`. Once N 61 leaves GAP it has no step, so the
  checker goes RED on rank 83 until that line leaves the queue: N 61 cannot move
  without one queue edit. Question Q3.

## 6. The re-judges (no row moves)

### 6.1 M C11 RIDES INSIDE M C1'S FIRST NAMED FIRE

The ledger's D6 call "`M C11` on `M C1`" fails on M C11's own sentence, "whether
LinkedIn turns a typed hashtag into an entity is unmeasured": `linkedin_publish_post`
types his words verbatim, a '#' he types is his own text, and what LinkedIn makes of it
has never been read. The kind stays `SIBLING:M C1`, as a step inside another row's
act (the ledger's own sub-kind); its source moves off D6 to that sentence and to this
section. The step: `M C1`'s first named fire, a post whose words he supplies with a
hashtag in them, its published render read for whether the hashtag became a link.
Applied (the patch's step `msg`): the cell note, and the `next-step.tsv` line

    M C11  M  W  R3  SIBLING:M C1  INFERRED
           _audit/_census/messaging-and-content.md::whether LinkedIn turns a typed
           hashtag into an entity is unmeasured ; _audit/2026-11-28-census-calls.md::
           M C11 RIDES INSIDE M C1'S FIRST NAMED FIRE ; M C1

### 6.2 Rank 23's 13 rows: every one waits on a precondition, not a capture

Live session 14, phase 2 (`_audit/2026-11-27-live-session-14.md`), read his
recommendations page served exact: the first view (Received) drew "0 entries and 0
member links", and the Given view "0 entries and 1 member link". The plan sent the
given side to "one capture of an entry's menu"; with no given entry there is no menu to
open, so disk disagrees with that half of the plan. Re-judged from each row's own cell:

| rows | the act | proposed step |
|---|---|---|
| N 121, N 122, P F6 | accept or dismiss a received recommendation | `PRECONDITION:a recommendation he has received` |
| N 123, P F7 | ask for a revision of one received | `PRECONDITION:a recommendation he has received` |
| N 126, P F9 | hide or unhide one received | `PRECONDITION:a recommendation he has received` |
| N 128, P F8 | decline a recommendation request | `PRECONDITION:a recommendation request someone has sent him` |
| N 125, P F5 | delete a recommendation he sent | `PRECONDITION:a recommendation he has given` |
| N 127 | set the visibility of one he gave | `PRECONDITION:a recommendation he has given` |
| P F1 | read the recommendations he received | `PRECONDITION:a recommendation he has received` -- an empty list is not a believable zero until one entry's shape is captured |

Each with basis MEASURED and the source
`_audit/2026-11-27-live-session-14.md::Its view: 0 entries and 1 member link` (the
Given rows) or `::first view: 0 entries and 0 member links` (the rest), plus
`tests/fixtures/live14/recommendations.html`. THIS IS COUPLED TO THE QUEUE: rank 23,
`admit-in-me-details-recommendations`, lists all 13 with needs `-`, and
`check_next_step.py` requires each to step `CAPTURE:admit-in-me-details-recommendations`.
The capture it names is done (session 14). So the 13 lines and the rank 23 line move
together, and the queue was not this lane's. Question Q4.

APPLIED on the orchestrator's answer (19:04 IST: "YOUR commit"), in one commit: each of
the 13 cells gains a note citing session 14's reading by record and section
(`_audit/2026-11-27-live-session-14.md`, section 10.2, phase 2), the 13 `next-step.tsv`
lines become the PRECONDITION steps above (basis MEASURED), and rank 23's line leaves
the queue. No row's STATE moves: PRECONDITION is a next-step kind, not a census state,
so "the 13 rows to PRECONDITION" is read as their steps, and every pin held
(`census_completion.py --check`).

### 6.3 J 3, J 17 and J 151: the step is a new place capture

Live session 13 (`_audit/2026-11-27-live-session-13.md`, loads 1 and 2) captured
`C-SRCH-2`, queue rank 133: "the AI route DROPS a text `location` (no `geoId` written
in its place)", and its 25 cards are the 25 the search without a location returns.
Finding 1 there: "The AI job search ignores a text `location`." So rank 133's own
address, `...&location=placeholder-place`, cannot discriminate any of the three rows
again. Each reopener needs an AI-route fire whose results move with the place.

The step named here: a new queue line, `C-SRCH-2b`, the AI route's own place, 2 loads
and 2 searches as `C-SRCH-2` was (with and without the place, the id sets compared).
The place goes in by the AI route's own means, either a `geoId` or the place written
into the AI search's own words; the boundary admits both spellings today
(`readonly.is_read_url` True on
`https://www.linkedin.com/jobs/search-results/?keywords=placeholder&geoId=1234567` and
on `...?keywords=placeholder-in-placeholder-place`, read in this lane). Which one is the
queue owner's design. The proposed `next-step.tsv` line for each of the three:

    J 3   J  R  -  CAPTURE:C-SRCH-2b  MEASURED
          _audit/2026-11-27-live-session-13.md::The AI job search ignores a text ;
          RULING:RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE

The plan had the queue line written after 14b's close-out; the orchestrator's answer
to Q5 gave it to this lane, and it is applied with the three `next-step.tsv` lines, in
one commit (section 6.4).

### 6.4 M C65 AND M C91 NEED THE GROUP FEED'S OWN ROUTE

Both stay GAP (section 3), and their ledger step, `SIBLING:M C25` / `SIBLING:M C32` on
D6, is now answered. The next step is a capture on the feed of a group he belongs to,
`https://www.linkedin.com/groups/1234567/` (admitted): the route a group post's
permalink wears, and that post's comment and reaction controls, read with nothing
pressed. That needs a queue line (Q5).

APPLIED on the orchestrator's answer to Q5 (19:04 IST: "YOU write them"), in one
commit with the steps that cite them. Two lines were appended at the queue's end, at
the next free ranks, and nothing was renumbered:

- `C-SRCH-2b` for J 3, J 17 and J 151: 2 loads and 2 searches, derived as C-SRCH-2's
  were (a load with the place, and the same session's control without it). The place
  goes into the AI search's own words, and a `geoId` spelling is the fallback. The line
  says it spends 2 of D1's 5 searches a session.
- `C-GROUP-POST-1` for M C65 and M C91: 1 load and 0 searches of a group he belongs to,
  nothing pressed. It reads the leading path segment of each post's own permalink
  anchor, and each post's Comment and reaction controls, by counts. The same reading
  answers `N 175`'s reopener.
- Their five `next-step.tsv` lines step to those lines, basis MEASURED.
- Rank 133, `C-SRCH-2`, leaves the queue in the same commit. Its three rows all moved to
  `C-SRCH-2b`, its own capture is done (session 13, loads 1 and 2), and
  `check_next_step.py` requires every member of a needs `-` line to step to that line.
  That is the one queue edit beyond the two appends, and it is exactly what the checker
  needs in this commit.

## 7. Pins re-derived

`scripts/census_completion.py --check` after J 86's move, MEASURED, never summed: eight
pinned figures moved, and `PINNED` was re-pinned from those values with one history line
each.

    adjudicated        278 -> 279
    b1_standing         28 ->  29
    delivered_broad    187 -> 188
    gap                506 -> 505
    gap_unknown        104 -> 103
    jobs_dir_w          54 ->  53
    jobs_gap           104 -> 103
    unfired             92 ->  93

`PINNED_B1_ROWS`: J 86 entered COVERED-UNFIRED held by OPERATOR-NAMES-THE-TARGET, as
`--check` reported it, and joins that tuple. After the re-pin `--check` ends "every
headline figure matches its pin".

After N 3's move, on the tree that merged master `b7db2f7a`, `--check` MEASURED six
moves, re-pinned the same way:

    adjudicated        279 -> 280
    b1_standing         29 ->  30
    delivered_broad    188 -> 189
    gap                505 -> 504
    gap_write          346 -> 345
    unfired             93 ->  94

`PINNED_B1_ROWS`: N 3 entered COVERED-UNFIRED held by OPERATOR-NAMES-THE-TARGET (a W
row, held with no marker). The class split `test_write_classes.py` pins is unchanged,
because N 3 keeps its R2 line as a `built:` line.

After N 61's move, `--check` MEASURED seven moves, re-pinned the same way, with no
bucket-1 change:

    achievable                710 -> 709
    adjudicated               280 -> 281
    b3_needs_session            5 ->   4
    capabilities_achievable   723 -> 722
    gap                       504 -> 503
    gap_read                   56 ->  55
    out_of_scope               74 ->  75

After N 50's split, `--check` MEASURED seven moves, re-pinned the same way, with no
bucket-1 change (N 50 is PROVEN, N 50b is GAP):

    achievable                709 -> 710
    adjudicated               281 -> 282
    capabilities              797 -> 798
    capabilities_achievable   722 -> 723
    delivered_broad           189 -> 190
    delivered_strict           95 ->  96
    stated_rows               784 -> 785

## 8. Gates

### 8.1 J 86's commit

No live session was on (`_state/LIVE_SESSION_ON` absent at each check).

- `scripts/census_completion.py --check`: "every headline figure matches its pin",
  rc 0, after the re-pin (rc 1 before it, naming the eight figures and J 86).
- `scripts/check_next_step.py` GREEN (505 = census_completion's gap);
  `check_jobs_directions.py` GREEN (103 of 103); `check_write_classes.py` GREEN (365
  lines); `check_read_addresses.py` GREEN (56 of 56); `ruling_holds.py` GREEN.
- The three derived views, `--check` rc 0 after `--write`: `build_audit_index.py`,
  `build_rulings_index.py` (only its "documents scanned" count moved, for this
  record) and `build_blocker_map.py`. The map moved 92 lines: J 86's `state_today`,
  and the reason locator's candidate count on rows whose top candidate is unchanged
  (`CANDIDATE-1-OF-17` -> `1-OF-18` on J 9). Without this record staged it moved 12, so
  80 of the 92 are the new document entering the locator's corpus, not a row moving.
- pytest, the 35 test files that read a changed file (the impact gate's read map,
  `scripts/impact_gate_read_map.json`, used as a list of direct readers and not
  widened), with `-n 4 --dist loadfile -p no:randomly --durations=15`: 2352 passed in
  285 s. That is over the 2-minute local cap. Sampled while it ran: CPU 100% busy and
  disk 91.2% idle, with two other lanes' pytest runs on the box. The five slowest were
  corpus-wide guards (58 s, 57 s, 56 s, 29 s, 27 s). Later gates in this lane run the
  census instruments for the changed tables only; the corpus-wide guards run on CI.
- After the commit: the pre-commit identity gate was armed ("226 spellings; 0 hits"),
  and `tests/test_no_committed_identity.py` passed, 1481 tests, on the committed blobs.

### 8.1a CI on J 86's head, read by sha

- `scripts/lane_ci.py push` put `118d4008` on `ci/census-calls28`; the pre-push gate
  swept it clean and confirmed it descends from master.
- `lane_ci.py wait 118d4008...`: run 46145558412, success, 7 jobs, 6m52s.
- `lane_ci.py wait 118d4008... --full`: run 46146396940, success, 21 jobs, 17m10s;
  ubuntu py3.10, ubuntu py3.13 and windows py3.13 each 6 of 6 shards.

### 8.1b The merge of master `b7db2f7a`, and N 3's commit

- The merge conflicted only in the derived `_audit/INDEX.md` and `blocker-map.tsv`.
  Both were regenerated with `--write` on the merged corpus, as was the rulings
  register's count. Then `census_completion.py --check` matched every pin, and
  `check_next_step.py`, `check_jobs_directions.py`, `check_write_classes.py`,
  `check_read_addresses.py`, `ruling_holds.py` and `measure_pointer_graph.py --check`
  were green.
- N 3 and the messaging notes applied with every anchor found once. Then
  `census_completion.py --check` measured the six moves of section 7, re-pinned, and
  ended "every headline figure matches its pin".
- GREEN after the move: `check_next_step.py` (504 = census_completion's gap; M C11's
  new source resolves), `check_jobs_directions.py` (103 of 103),
  `check_write_classes.py` (365 lines), `check_read_addresses.py` (56 of 56),
  `ruling_holds.py`, `check_exclusion_basis.py` (74 of 74) and
  `triage_read_gap_rows.py`. `measure_pointer_graph.py --check` read 64 pinned and 64
  measured, so M C65's note kept its pointer and re-pointed nothing.
- pytest, the census instruments for the changed tables (19 files, `-n 4`): 442
  passed in 199 s, over the 2-minute cap. Sampled while it ran: CPU 54.2% busy and
  disk 95.4% idle, with two other repositories' pytest runs on the box. So the box
  was not saturated; the wall time is a few long single tests. The repository-wide
  literal sweep took 58 s, the pointer guard's two selftests 40 s and 37 s, and the
  Playwright teardowns 7 to 10 s each. The corpus-wide guards are left to lane CI.

### 8.2 The held patch, tried on this tree and reverted

The held patch was applied to this worktree at `118d4008` in steps `before`,
`n3,n61,msg` and `delta`, measured, and then every file it touched was restored from
HEAD; `git status` showed only this record afterwards. On that trial tree:

- The DELTA it measured on `network.md`: COVERED-UNFIRED 28 -> 29, MEASURED-ABSENT 5 ->
  6, GAP 129 -> 127, stated rows 216.
- `census_completion.py --check` moved 11 pins: achievable 710 -> 709, adjudicated
  279 -> 281, b1_standing 29 -> 30, b3_needs_session 5 -> 4, capabilities_achievable
  723 -> 722, delivered_broad 188 -> 189, gap 505 -> 503, gap_read 56 -> 55, gap_write
  346 -> 345, out_of_scope 74 -> 75, unfired 93 -> 94. N 3 entered bucket 1 held by
  OPERATOR-NAMES-THE-TARGET. These are the trial's readings; the real commit
  re-measures on the merged tree and re-pins from that.
- `measure_pointer_graph.py --check`: POINTER GONE 1 (N 61); RE-POINTED 0 and DONOR
  VERDICT MOVED 0, so `M C66` still reads `M C64` through M C65's kept 'same'. After
  `--pin`, 63 pinned and 63 measured: the calibration literal's 63 is that reading.
- `check_next_step.py` RED with exactly one problem: "queue
  admit-mynetwork-network-manager-people-follow-following: N 61's step is '', not
  CAPTURE:admit-mynetwork-network-manager-people-follow-following". With the queue
  owner's step applied in the trial (rank 83's line removed), GREEN (503 =
  census_completion's gap). The queue file was restored at once.
- GREEN: `check_jobs_directions.py` (103 of 103), `check_write_classes.py` (365
  lines, so N 3's built line kept the count), `check_read_addresses.py` (55 of 55),
  `ruling_holds.py`, `check_exclusion_basis.py` (population 75, table 75, 0 untraced)
  and `triage_read_gap_rows.py`.
- pytest, the tests that hold the patch's own pieces
  (`test_pointer_graph_guard.py` with its selftest, `test_triage_read_gap_rows.py`,
  `test_exclusion_basis.py`, `test_write_classes.py`, `test_read_addresses.py`,
  `test_ruling_holds.py`): 175 passed in 74 s, `-n 4`.
- `build_blocker_map.py --check`: 8 lines, N 61's `state_today` and seven
  reason-locator re-ranks (J 112, N 99, N 100, N 133, N 134, N 136, P O3), all derived.

## 9. Questions for the orchestrator

- **Q1, THE BASE -- ANSWERED.** hygiene28 reached master (`b7db2f7a`, the
  orchestrator's note of 18:57 IST), the branch merged it, and N 3 and the messaging
  notes were applied. What remains of Q1 is the merge order the same note gives: this
  lane merges after the live lane's r2, with master merged in again before the
  certifying run.
- **Q2, N 50 SPLITS? -- ANSWERED: SPLIT, AS RECOMMENDED (19:04 IST); APPLIED.** Ground, section 4.2: the company half is delivered by D6 on a
  live-proven route (`linkedin_follow_company`, `N 46` and `J 103` banked PROVEN on
  its session-8 fire), and the school half by nothing (no write acts on `/school/`).
  The halves need different states, and COMPOUND-ROW-SPLITS-ONLY-ON-STATE splits such
  a row. The recommendation: split on the `N 26` -> `N 26b` precedent; the company half
  stays N 50 at COVERED-PROVEN by D6 on that fire, with `linkedin_follow_company_page`
  (`N 47`, UNFIRED) as its by-id route, and the school half enters as `N 50b` at GAP,
  its step the school's address from him (as `J 112`). If the by-id route should be
  the row's proof instead, the company half is COVERED-UNFIRED, as the plan had it.
- **Q3, N 61 NEEDS ONE QUEUE EDIT -- ANSWERED YES (19:04 IST).** Ground, section 5.2:
  queue rank 83 lists N 61 alone with needs `-`, its capture is done (session 13, load
  3), and `check_next_step.py` goes RED on that line the moment N 61 leaves GAP. The
  orchestrator amended the queue rule for this lane, for exactly that, and the line
  left in N 61's commit.
- **Q4, RANK 23 LEAVES THE QUEUE? -- ANSWERED: THIS LANE'S COMMIT (19:04 IST); APPLIED.** Ground, section 6.2: all 13 rows re-judged
  PRECONDITION, because session 14 read both views empty. The 13 `next-step.tsv` lines
  and the rank 23 line must move in one commit. Whose commit?
- **Q5, TWO NEW QUEUE LINES -- ANSWERED: THIS LANE WRITES THEM (19:04 IST); APPLIED.** Ground, sections 6.3 and 6.4: `C-SRCH-2b` for J 3, J 17
  and J 151, after 14b's close-out as the plan says, and a group-feed capture for M C65
  and M C91. Each `next-step.tsv` line follows its queue line, so the queue's owner
  writes both, or this lane writes the step lines after the queue lines land.

## 10. Lessons

- On this box, `grep -c $'\r'` in Git Bash counted every line of a file as
  CR-bearing, before and after `sed -i` had rewritten that file to LF-only (Python
  read 0 CRLF in 506 lines). The commit was unaffected, because the index stores LF,
  but the check could not fail. Count line endings on bytes, and edit CRLF tables
  with a bytes-aware script, not `sed -i`.
- A census move can be coupled to a table the lane does not own. `check_next_step.py`
  ties every member of a capture-queue line with needs `-` to the step
  `CAPTURE:<that line>`, so a row leaving GAP, or re-stepped to any other kind, turns
  that line RED until the queue changes with it. Read the queue membership of every row
  before planning a lane's files; here it decided N 61, rank 23's 13 rows, and the
  C-SRCH-2 follow-up.
- Writing out a positional 'same' re-points every 'same' below it. M C66 reads M C64
  THROUGH M C65, so M C65's note had to follow its 'same', not replace it.
  `scripts/measure_pointer_graph.py --check` proved it: RE-POINTED 0.
- A new `_audit` record moves derived views far from the rows it discusses. This
  record re-ranked the reason locator's candidates on 80 blocker-map lines it never
  names, each top candidate unchanged. Read a derived diff by column before
  accepting it.
- A record that cites its own lane's sha is red on the lane's own CI until the merge:
  `tests/test_a_cited_sha_resolves.py` asks whether `master` has the sha as an
  ancestor, not whether the store holds it. Write the subject and the branch-only
  fact beside the first citation. The J 86 gate missed this only because the record
  did not yet cite that sha; the record head's lane CI caught it.
- A plan's "a shipped tool may already reach it" needs the tool's address read, not
  its name. Both group rows failed on one `url_pattern` and one live count
  (`N 175`'s zero `/feed/update/` links), and N 50 on two `url_pattern`s that never
  name `/school/`.
