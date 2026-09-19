# GROUPS-SURFACE: why 22 rows were still GAP, and the one that was already served

Wave: `groups-reader`. 2026-09-19, 13:25-13:45 IST, every time taken with
`date` on the box. All paths repo-relative; commands run from the repo root.

**THE SHORT ANSWER.** The brief named four candidate causes. Measured, the
block is not one cause: **cause 1 and cause 3 are refuted outright, cause 2 is
true for EXACTLY ONE ROW, and cause 4 is the bulk.** One row is banked. The
other 21 are stated below with what each actually needs, and most of them need
a ruling rather than a build.

---

## 1. THE BLOCK, AND THE RECONCILIATION NOBODY HAD DONE

`GROUPS-SURFACE` held **30 rows at HEAD**: 2 COVERED-PROVEN, 6 EXCLUDED-RULED,
**22 GAP**. Measured 13:25 off `_audit/_census/blocker-map.tsv`.

The group family's own measurement pass walked **35** rows and recorded that no
subset of them reconciles to the ledger's published 32. It does reconcile, and
the census already contains the arithmetic:

    35 rows walked by the groups pass
    -3   the three admin-only A-rows        -> ADMIN-RIGHTS-NOT-HELD
    -2   search-inside-groups, two rows     -> SEARCH-RESULTS-SURFACE
    ----
    30   = the census's GROUPS-SURFACE, exactly

Verified row by row against the map at 13:27, not by subtraction alone: each of
the five sits under the blocker named above, and no row is double-assigned.

---

## 2. THE FOUR CAUSES, EACH WITH ITS MEASUREMENT

### Cause 1 -- "the shapers exist but are not wired". REFUTED.

`linkedin_group_memberships` is registered and reachable. Measured at HEAD,
2026-09-19 13:33, by resolving the tool out of the live registry:

    TOOLS AT HEAD: 44
    groups tool present: True

It wires `groups_page.read_group_memberships` over `groups.membership_tally`,
and is pinned by `tests/test_every_tool_is_on_the_surface.py` plus the property
battery in `tests/test_the_groups_tool_keeps_its_properties.py`.

**A NUMBER THAT MOVED WHILE NOBODY WAS LOOKING, recorded because this wave was
told to stamp its figures.** The wiring pass recorded `REGISTRY: 42 tools`. The
registry answers **44** today. Nothing is wrong with that line -- it was right
when taken -- but any document quoting it as a current count is quoting a
reading with a timestamp it does not print.

### Cause 3 -- "the reader covers part of the surface". REFUTED.

The reader covers the whole admitted root and splits it STRUCTURALLY, returning
`memberships`, `others` and an `overlap` disjointness proof. There is no
uncovered part of `/groups/`. What is uncovered is everything BELOW it, which
is cause 4 and a different repair.

### Cause 2 -- "the rows were never banked". TRUE FOR EXACTLY ONE ROW.

That row is **N 162**, and section 3 is entirely about it.

### Cause 4 -- "addresses deeper than `/groups/`, individually refused". THE BULK.

Eleven rows need an allowlist entry for `/groups/<id>/` or `/groups/discover/`;
three more are refused twice over, by an anchored pattern AND by a forbidden
substring, so each needs two boundary changes rather than one. Section 4.

---

## 3. THE ONE ROW THAT WAS ALREADY SERVED

**`N 162` -- "Browse groups recommended from attributes you share with their
members".**

The shipped tool was fired live through the registry on 2026-09-05 at 22:08,
and its payload carries this row's answer beside the one everybody banked:

    MEMBERSHIPS  rows 5, groups 5, DISTINCT 5, refused {}
    OTHERS       rows 6, groups 5, DISTINCT 5, refused {root: 1}
    in common 0, DISJOINT True

The `MEMBERSHIPS` line closed `M C60` and `N 173`. The `OTHERS` line answers
`N 162`, from the same load, in the same payload, on the same run. Nobody moved
the row.

### It is NOT `COVERED-PROVEN`, and that is the whole value of the number

The tool reads no heading by design, so it cannot certify WHICH section the
others came from; the section identity is a separate instrument's reading, the
heading-boundary probe, which resolved the suggestions disjoint from the
memberships at 5.

And more decisively: **what this row asks to BROWSE is exactly what the shaper
refuses to say.** `groups.membership_tally` takes no name as a parameter of any
function it calls, and refuses a non-numeric path segment because a slug is a
name. The tool can report HOW MANY groups are recommended. It can never report
WHICH.

So the row is banked **`COVERED-CANNOT-DELIVER`** -- not GAP, because nothing
needs building; not COVERED-PROVEN, because the thing the row asks to see is
withheld on purpose. **The boundary decided the page may be OPENED; the shaper
decided what may be SAID.**

### The ruling is not this wave's. It is the twin's, already made.

Row `N 180`, "See events recommended from your interests", is the same shape
one surface along: an admitted root, a recommendation section made of other
people's things, published as a count. It was moved to `COVERED-CANNOT-DELIVER`
on 2026-09-19 on exactly that reasoning. This wave cited that ruling rather
than re-deriving it, per the standing requirement that a ruling has one
canonical id and every citation resolves to it.

### The mechanism of the miss, which is the part worth keeping

The pass that banked `N 180` found it by cross-referencing the registered tools
against GAP rows BY HAND, after an automated sweep of the same question failed
four times. That hand pass reached the events recommendation row and **did not
reach the groups recommendation row eighteen lines above it in the same table**.

> **A hand cross-reference has a reading order, and a row's twin is not
> adjacent to it in that order.** The automated sweep would have had no such
> blind spot and could not be built; the hand pass could be built and had one.
> Neither is a substitute for the other, and the gap between them is where this
> row sat.

---

## 4. THE REMAINING 21, STATED SO A READER CAN CHECK THEM

Against the boundary as it stands: `/groups/` root only, anchored, no query and
no sub-path.

| what they need | rows | count |
|---|---|---:|
| an allowlist entry for `/groups/<id>/` or `/groups/discover/` | join and request-to-join x3; the group FEED x5 (post, comment, edit-or-delete, approval, react); a private group by direct link | 9 |
| **two** boundary changes -- an anchored pattern AND a forbidden substring | two invite-from-inside-a-group rows, one invite-filter row, one join-notification setting | 4 |
| a ruling that already exists elsewhere, applied | a message request to a stranger; finding people through shared membership; which groups a member belongs to | 3 |
| a WriteSpec, a sanction entry and a reversibility ruling | leave a group, counted twice by two slices | 2 |
| re-costing or retirement -- they describe LinkedIn's behaviour, not an act | expose-your-profile-on-joining; a member's connections after connecting | 2 |
| an invitations surface nobody has looked for | join by responding to an invitation | 1 |
| nothing measurable on this account | the groups you have requested to join | 1 |

**NOT ONE of the 21 is closable by writing a shaper.** Nine need a boundary
decision, four need two, six need a ruling, and two need re-costing. That is
the honest shape of what is left, and it is why the block did not shrink by
building.

### Two that are cheaper than their placement suggests

**The two "describes LinkedIn's behaviour" rows.** One is a consequence of
joining rather than an action; the other is a LinkedIn rule about when a
member's connections become visible. Neither is a capability this server could
implement at any boundary. The groups pass wrote that they should be re-costed
or retired -- and wrote it as a RECOMMENDATION, which this wave has not
executed as though it were a ruling. **They need one sentence from the lead and
they close.** That is the cheapest thing in the block.

**The duplicate pairs.** A cross-slice pass measured that join-a-group and
leave-a-group each appear twice, once per census slice, and reported rather
than executed the subtraction because it changes a published denominator. Two
of the 21 are the same two capabilities counted again. Executing that is the
slice owners' call, not this wave's.

---

## 5. WHAT THIS WAVE VERIFIED, AND WHAT IT DID NOT

**VERIFIED BY INSTRUMENT.** The registry count and tool presence at HEAD
(13:33). The 30-row reconciliation, row by row (13:27). The one-row map
movement, by diffing the derived map against HEAD (13:42). The failure
baseline, by running the census, prose, identity and groups-tool cluster
against pristine HEAD content in a throwaway worktree and then against the same
content plus this change:

    pristine HEAD    4 failed, 567 passed, 1 skipped
    with this change 4 failed, 567 passed, 1 skipped

Identical. **This change adds no failure.** The four are foreign, standing at
HEAD, and two of them were already named in the lead's own downlink.

**NOT VERIFIED, AND SAID PLAINLY.** This wave ran no full suite. It ran a
five-file cluster and a targeted battery, and the number above is that
cluster's, never the tree's. Two other waves were mid-run on a contended tree
and a long run there measures an interval, not a state.

**NOT MEASURED LIVE.** No browser was opened and no page was loaded by this
wave. The `OTHERS` payload quoted in section 3 is the wiring pass's live run,
re-read from its own record rather than re-taken -- which is a reading with a
2026-09-05 timestamp, and is cited that way in the census cell.

---

## 6. A GUARD THIS WAVE DECIDED NOT TO BUILD, AND WHY

The obvious durable fix is a check that no row can sit GAP while its twin
carries a ruling. It was scoped and declined.

Twinship is not machine-derivable here. A sibling pass tried similarity
scoring at a 0.62 bar over sixteen rows: nine twins returned, three real, with
"Create a LinkedIn Event" matching "Leave a LinkedIn group" at 0.67. Its own
conclusion is the reason this guard was not attempted -- **the score generates
candidates and must never settle one.**

The decidable seam that remains is census row ids named in shipped package
source. Measured at HEAD: **eight references across four modules.** A guard
over eight references exercises almost nothing, and a check that barely fires
certifies almost nothing.

**RECOMMENDATION, offered as one and not as an instruction.** The events tool
names its census row in its own docstring, and that is why its row is
checkable. The groups tool names none. Making that convention general would
grow the seam from eight to something a guard could stand on. It is a
`server.py` edit, that file is contended, and a wave declined to take it for
this same reason on 2026-09-05 -- so it belongs to whoever can hold the file,
not to this wave.

---

## 7. THE LEDGER

    GROUPS-SURFACE GAP      22 -> 21
    census GAP, derived    313 -> 311   (two of those three are the events
                                         wave's, landed while this wave ran)
    rows banked by this wave  1, COVERED-CANNOT-DELIVER
    rows inflated             0
    page loads spent          0
    writes fired              0
    AI attribution            0
