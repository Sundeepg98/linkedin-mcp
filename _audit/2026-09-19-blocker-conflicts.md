# The four row-to-blocker contradictions, adjudicated

`_audit/2026-09-06-corpus-sweep-blocker-evidence.md` section 3 left four
disagreements between committed sources "for a person", declining on purpose
to resolve them: *"resolving them means editing
`_audit/_census/blocker-assignments.tsv` by hand ... which is a ruling this
document declines to make on someone else's behalf."*

This is that ruling. **Two resolve and are applied. Two do not, and are
recorded as unresolved rather than forced** -- a queue cleared by manufacturing
a verdict is worse than a queue left honest, because the next reader cannot
tell which entries were decided and which were tidied.

**CORRECTS:** `_audit/2026-09-06-corpus-sweep-blocker-evidence.md` -- its finding C offers a dichotomy, that one of the two sources is wrong or the ledger's bare id was never the messaging row at all, and neither disjunct holds: exactly one census slice carries a C 52, so the bare id is unambiguous, and neither source is mistaken, because the row's capability was rewritten out from under the ledger's grouping between the two readings.

(A marker's reason may contain NO backticks. The checker takes everything after
the LAST backtick on the line, so a quoted id inside the reason silently eats
it and the marker reads as having no reason at all. Measured here, twice.)

Applied at `c4d2be2`. Ratchet, counts and tests at the foot.

---

## A. `N 194` -- RESOLVED. `HASHTAG-EXISTENCE` -> `SEARCH-RESULTS-SURFACE`

**The evidence line contradicted itself.** `_audit/_census/blocker-assignments.tsv`
carried, on one line, a blocker column reading `HASHTAG-EXISTENCE` and a note
reading:

    A13 re-files N 194 out of this blocker into SEARCH-RESULTS-SURFACE

The finding had been recorded and never applied. Nothing anywhere argues for
keeping it, so this is STALE rather than debatable -- and it was tested rather
than inherited, because the sweep's own confidence about it is not evidence.

Three committed sources agree, and one of them is arithmetic that closes:

| source | says |
|---|---|
| `2026-09-03-linkedin-gap-blockers.md:1270` | `-2 HASHTAG-EXISTENCE re-filed: N 194 out to SEARCH-RESULTS-SURFACE` |
| the same file, `:1298` | `SEARCH-RESULTS-SURFACE goes 21 -> 22 rows (21 + N 194 = 22)` |
| `2026-09-05-decide-retire-rulings.md:973` | `N 194` from MEASURE into `SEARCH-RESULTS-SURFACE` |

A13's own three-row table renders it explicitly as a row whose blocker
CHANGED: *"`N 194` | `HASHTAG-EXISTENCE` | `SEARCH-RESULTS-SURFACE` -- the
census's own note names its blocker: 'no people search'"*.

**And the census row corroborates without being asked.** `network.md` row 194
reads *"Find hiring managers through the #Hiring hashtag in search"*, note
*"Blocker: no people search."* The blocker is written in the row itself. That
is a second, independent signal of a different kind from the ledger's
arithmetic, which is what this repository asks for before a ruling.

---

## B. `J 116`-`J 120` -- NOT RESOLVED. Nothing to apply, and the choice is THREE-way

Committed as `MATCH-DETAILS-COLLAPSED` (ledger publishes 5 rows, 5R; the map
holds 5; COMPLETE).

A13 measures the blocker's founding premise FALSE, and the measurement is
sound: `Show match details` is not a disclosure control but an `<a href>` to
`/preload/guideOverlay/`, one of three anchors sharing a path and ten
parameter names, whose sibling labels are `Create cover letter` and
`Help me stand out`. Its own confidence grading is exemplary -- the anchors,
parameters and labels VERIFIED-BY-INSTRUMENT, the generative reading DERIVED.

It then says, in its own words:

    Proposed rename: `AI-ASSISTANT-OVERLAY` -- A PROPOSAL, NOT A RULING.

**There is nothing here to apply to the map.** The dispute is about the
blocker's NAME, not about which rows belong to it; no row moves under any of
the three candidates, so `blocker-assignments.tsv` is unaffected either way.

**Filed so the next reader is not stranded, because the choice reads as two
and is three:**

| candidate | standing |
|---|---|
| `MATCH-DETAILS-COLLAPSED` | the committed name, and the one the 97-blocker ledger knows |
| `AI-INTERVIEW-PRODUCT` | an EXISTING blocker (14 rows, DECIDE-RETIRE) that A13 says these rows are "closer to" -- a merge, not a rename |
| `AI-ASSISTANT-OVERLAY` | A13's proposal. **Not one of the 97, and never ruled on** |

Whoever rules is choosing among three, and two of the options carry costs the
passage does not price: a MERGE into `AI-INTERVIEW-PRODUCT` moves five rows
into a DECIDE-RETIRE queue and changes two published counts, while a RENAME to
a name outside the 97 breaks the comparison
`test_the_ledger_tables_still_total_97_blockers_and_409_rows` rests on.
Neither is a documentation edit.

---

## C. `M C52` -- RESOLVED. `HASHTAG-EXISTENCE` -> `FEED-PREFERENCES`

This is the one the sweep expected to be hardest, and it resolves on four
measurements, none of which required an instrument the sweep lacked -- only
reading the row.

### C.1 The sweep's dichotomy is false on BOTH sides

It offered: *"One of them is wrong, or the ledger's bare `C 52` was never
`M C52` at all."*

**The second disjunct is measurably false.** The census warns that the profile
and messaging slices both have a `C` section, so a bare `C 52` could in
principle be either. Counted across all four slices (named without their
extensions on purpose, so this table does not read as a citation):

    slice                  C11   C52
    profile                 0     0
    network                 0     0
    jobs                    0     0
    messaging-and-content   1     1

Only one slice has either id. The bare `C 52` can only be `M C52`, and the
qualification needs no judgement. The sibling id in the same A13 table
corroborates it: `C 11` resolves to `M C11` the same way, and `a402c35`
independently moved `M C11` to EXCLUDED-RULED exactly as A13 predicted.

**The first disjunct is also false**, which is the finding underneath: neither
source is mistaken. They read the row at different times, and it changed in
between.

### C.2 A13 does not RULE on this row -- it says so itself

`2026-09-03-linkedin-gap-blockers.md:1197`:

    So `HASHTAG-EXISTENCE` becomes a ONE-ROW blocker. Nothing in the evidence
    above argues its queue changes -- unlike items 1 and 2, no move off MEASURE
    is made for `C 52` here, so it is carried forward MEASURE, at 1 row,
    UNLESS A FUTURE PASS RULES OTHERWISE.

That is a DEFAULT-CARRY, labelled provisional by its own author, with an
explicit invitation to a later pass. The evidence file's tie-breaker --
*"LEDGER-AMENDMENT outranks RECON-DOC"* -- ranks a document class above
another, but the ledger document does not make the claim being ranked.

`_audit/2026-09-05-settings-tail.md:224` is that later pass, and it spells the
id fully qualified, no guess required:

    | `FEED-PREFERENCES` | `M C52` | 1W | no -- a Help Center article id only |

### C.3 The note that kept the assignment MISQUOTES the row

The evidence file justified the carry with: *"the row reads 'follow / unfollow
topics/hashtags' and supports both readings."*

It does not read that. Capability cell, verbatim:

    Manage your LinkedIn feed preferences (follow / unfollow topics and sources)

**"topics and sources", not "topics/hashtags".** The word `hashtag` does not
occur in the capability cell at all -- it appears only in the notes cell, in
the correction history and in today's live measurement. Quoted correctly the
capability supports ONE reading, and the "supports both readings" conclusion
was produced entirely by the misquote.

### C.4 A13's justification cites the OTHER row's article

A13 calls `C 52` *"the one row the three instruments above actually speak to"*,
and its instrument 1 is *"source article `a528144` returns HTTP 404"*.

**`C52`'s source article is `a528074`.** `a528144` is `C11`'s -- the row above
it in the same blocker, whose capability is "Add a hashtag to a post". The
instrument offered as speaking to C52 is about a different row.

### C.5 The row was corrected BEFORE A13, and A13 never quotes it

| commit | box time | the row read |
|---|---|---|
| `61d3816` | 2026-09-03 15:24 | "Follow a hashtag / topic", article `a528144` |
| `1c08e5f` | 2026-09-03 15:53 | **corrected** to feed preferences, article `a528074` (the frozen census commit) |
| `7bfe420` | 2026-09-04 09:03 | A13 written -- **seventeen hours later** |

The row records its own correction and why: *"It previously read 'Follow a
hashtag / topic' sourced to `a528144`, which returns HTTP 404, and two
independent help-index queries return no hashtag-following article at all."*

A13 had the corrected text on disk. It quotes `C 11`'s capability and reasons
about it at length; for `C 52` it makes no argument at all beyond declining to
move it. **The ledger's grouping is sound for the row as it read when the
grouping was made, and was never re-derived once the capability changed.**

### C.6 The argument on the other side, stated rather than buried

`HASHTAG-EXISTENCE` publishes **3 rows, 1R/2W**, and that split is satisfied
exactly by `N 194` (R) + `C 11` (W) + `C 52` (W) -- all three R/W cells
verified at the frozen commit. So the original grouping did include C52, and
after A and C the blocker holds ONE mapped row against a published 3.

That is an UNDER-count, which the map permits and the over-count assertion does
not touch. It is also the honest shape: two of the three rows were re-filed out
by A13 itself, and the third stopped being a hashtag capability on 2026-09-03.

### C.7 Today's live reading -- which was RETRACTED while I was writing this

`a402c35` moved `M C52` GAP -> MEASURED-ABSENT on a live feed read:
`a[href*='hashtag']` **0** and `a[href*='/feed/hashtag/']` **0**, two loads on
two instruments 13 minutes apart.

**Measured 09:30 by the box, the state is no longer MEASURED-ABSENT.** The wave
that made that move has withdrawn it in the working tree -- the row now reads
EXCLUDED-RULED -- on the ground that the FEED was the wrong surface for a row
whose capability is feed preferences, and that the real address
`/mypreferences/d/unfollowed` is refused at the FORBIDDEN-SUBSTRING gate by
`/unfollow`. That retraction was UNCOMMITTED when I read it; it is recorded as
a reading with a timestamp, not as a settled state.

**Neither state decides the blocker, and this document never rested on one.**
Both are facts about whether the capability is reachable; the adjudication
above is built from the row's TEXT, the ledger's arithmetic and the two
sources' timestamps.

The hashtag reading itself stands as evidence about a different question, with
its stated limitation respected -- a context classifier accounted for 0 of 15
raw-HTML occurrences, later repaired into a partition. Nothing further is
concluded from it, and this document **does not rule on `network.md` rows
59-61**, which that cell explicitly declined to touch.

### C.7b TWO WAVES REACHED THIS VERDICT FROM DIFFERENT DIRECTIONS

This wave adjudicated C from documents: the row's text, the misquote, the
article id, and the seventeen-hour gap between the correction and A13.

Independently, and inside the same hour, the wave that owns the settings
addresses reached `FEED-PREFERENCES` from a MEASUREMENT -- it found the row's
real address and the gate that refuses it. Its note says so directly: *"THIS
ALSO SETTLES CONFLICT C ... `M C52` is `FEED-PREFERENCES`, not
`HASHTAG-EXISTENCE`."*

**Neither wave's argument is the other's.** One is a reading of what the
documents say and when they said it; the other is a reading of where the
capability actually lives. They converge, and convergence from two unrelated
instruments is worth more than either argument alone -- which is this
repository's own standing preference for a second SIGNAL over a better
argument.

Order, so the convergence is not mistaken for an echo: this wave's verdict was
committed at `c4d2be2` (09:26 by the box). The sibling's note was read at 09:29,
after. Neither adopted the other's reasoning.

### C.8 A trap worth recording, because it would have dissolved C for free

`M C52` is MEASURED-ABSENT today, which invites the conclusion that it has left
the blocker map and the conflict with it. **It has not.**
`scripts/build_blocker_map.py`: *"THE SPINE IS THE FROZEN ROW SET, NOT TODAY'S
... the 409 GAP rows as of `1c08e5f`."* C52 was GAP at the freeze and stays in
the map with its current state carried alongside. A conflict that appears to
dissolve because a row changed state is a fact about which set you are looking
at.

---

## D. `M 24` / `M 42` -- NOT RESOLVED. Already encoded both ways; no edit

    blocker-assignments.tsv   MESSAGING-SETTINGS   M M42   RECON-CENSUS-COMMITTED
    blocker-assignments.tsv   GROUP-CHAT-SURFACE   M M24   RECON-DOC

Both rows are assigned, to different blockers, and **both blockers are COMPLETE
against their published counts** -- `MESSAGING-SETTINGS` 5 of 5,
`GROUP-CHAT-SURFACE` 4 of 4.

**The arithmetic cannot discriminate.** Swapping the two assignments leaves
both blockers at exactly their published counts, so no count, R/W split or
completeness figure distinguishes the two readings. That is the same thing
`_audit/2026-09-05-decide-retire-rulings.md:114` says about itself -- it states
the substitution as a RISK (*"`M M24`, if the classifier put `M 42` rather than
`M 24` in `GROUP-CHAT-SURFACE`"*), and the classifier that would settle it was
never committed; `git log -S` across all history finds it nowhere.

**Recording that is the result.** The two rows are not interchangeable in
principle -- one of the two assignments is wrong -- but nothing committed can
say which, and a coin-flip dressed as a ruling would be indistinguishable in
the file from an adjudicated one. Left exactly as unresolved as its source
leaves it.

---

## What was applied, and what the numbers did

Applied at `c4d2be2`, by editing `blocker-assignments.tsv` and re-running
`scripts/build_blocker_map.py --write`. The map is a DERIVED artifact and was
not hand-edited.

    UNASSIGNED                275 -> 275   ceiling 278
    complete / partial / absent   34/9/54 -> 34/10/53
    HASHTAG-EXISTENCE         3 mapped -> 1   (published 3; under-count, allowed)
    SEARCH-RESULTS-SURFACE    2 mapped -> 3   (published 21)
    FEED-PREFERENCES          0 mapped -> 1   (published 1; COMPLETE)

**UNASSIGNED does not move, and that is correct rather than disappointing.**
Both verdicts MOVE a row between blockers; neither RECOVERS a row that no
source named. The ratchet measures recovery, and this wave did not do any --
it corrected two attributions. A wave that reported progress on the ratchet
here would be reporting the wrong number.

    tests/test_blocker_map_is_derived.py                7 passed
    tests/test_a_correction_is_findable_from_the_claim.py   9 passed

Census, both ends, my own readings:

    09:17:39   GAP 363
    (closing reading at the foot of the progress file)

## One instrument gap found on the way, and NOT fixed here

**The committed map's `state_today` column is asserted by nothing.**

* `test_the_committed_map_still_matches_what_the_evidence_derives` reads the
  committed file but compares columns 1 and 2 only -- blocker and
  evidence_class.
* `test_the_state_today_column_reproduces_the_shipped_gap_total` computes BOTH
  of its sides from the live census and never opens the committed file.

So a row can flip state in a census slice while the committed map keeps the old
value indefinitely, with the suite green. **Demonstrated rather than argued:**
at HEAD in a clean clone, the profile slice reads `D25` as `GAP`, the committed
map reads `MEASURED-ABSENT`, and all 7 tests pass. Rebuilding for this wave
moved that one value back onto the census as a side effect, which is named in
`c4d2be2` rather than left for a reader to find.

**Not fixed here, and the reason is a real trade rather than a shrug:** an
assertion on that column would couple every census state edit to a map rebuild,
and four waves are editing census slices concurrently. Whether that coupling is
wanted is a decision for whoever owns the map. It is written down here because
the gap is invisible from either test's name.

### It reproduced within nine minutes, on a different row, unprompted

The paragraph above rested on one instance (`D25`), which is an anecdote. It is
now a measurement.

At 09:26 this wave rebuilt the map, which pulled `D25` back into agreement with
the census. At 09:35, measured:

    the census slice says   M C52   EXCLUDED-RULED
    the committed map says  M C52   MEASURED-ABSENT
    both governing guards               16 passed

A sibling wave had withdrawn its own state change for that row in the interval.
**The map went stale again immediately, on a row this wave had just touched,
with every test green** -- and nothing in the suite will say so until somebody
happens to run `--write` for an unrelated reason, as this wave did.

That is the difference between a control and a repetition: the first showed the
column CAN go unchecked, the second shows it does, in ordinary operation, at
the rate the census actually changes. **The gap is not a corner case; it is the
normal state of the file between rebuilds.**
