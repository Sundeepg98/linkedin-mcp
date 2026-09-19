# GROUPS DEEP PATHS: the admission is BUILT AND GATE-REFUSED, and it banks ZERO rows

Wave: `groups-admit`. 2026-09-19, 13:50-14:10 IST. Every time below was taken
with `date` on the box and is stamped where it was taken. All paths are
repo-relative; commands ran from the repo root.

**THE SHORT ANSWER, AND IT IS NOT THE ONE THE ASSIGNMENT EXPECTED.**

The admission is correct, narrow, and finished with its control. **It is NOT
COMMITTED** -- the pre-commit gate refused it on six reds measured foreign to
it, and the amendment at the end of this document is that measurement. **It
also closes no census row at all** -- not the 13 the brief hoped for, not the 9 the surface
document costed, not one. Eight of the nine rows it was bought for are WRITES,
and the ninth has no reader. That is stated first because it is the number this
campaign is actually keeping, and a widening reported by what it *unblocks*
rather than by what it *banks* is how a denominator gets inflated.

Two defects in the ruling's own literal text were found by measurement before
the pattern landed. Both narrowed it.

---

## 1. WHAT WAS BUILT

Two patterns in `linkedin_server/readonly.py`, immediately below the
`/groups/` root admitted on 2026-09-05 -- present in the working tree and in
`_RECOVER_groups_admission.patch`, not in any commit:

    ^https://www\.linkedin\.com/groups/[0-9]{1,20}/?$
    ^https://www\.linkedin\.com/groups/discover/?$

plus `tests/test_the_groups_id_segment_is_closed.py`, the control condition 2
requires, and the re-freeze of the two boundary digests.

**THE RULING SAID `\d+` AND THIS IS NOT THAT.** Both departures are narrowings,
both were measured rather than argued, and each is recorded at its line.

---

## 2. THE FIRST DEFECT: `\d` IS NOT TEN CHARACTERS

**Measured 13:54:36.** Python's `\d` on a `str` pattern matches any Unicode
decimal digit, so the ruling as literally written admits four further spellings
of a group id:

    case                    \d+      [0-9]+    groups.py shaper
    ascii digits            True     True      identified
    arabic-indic            True     False     identifier_is_not_numeric
    ext arabic-indic        True     False     identifier_is_not_numeric
    devanagari              True     False     identifier_is_not_numeric
    fullwidth               True     False     identifier_is_not_numeric

The ruling's safety argument is *a digits-only segment cannot carry a slug, a
vanity name or a urn*, and it BORROWS the word "numeric" from `groups.py`. That
module does not use `str.isdigit()`, and says why in its own comment: a
fresh-eyes re-read before a freeze found `isdigit()` true of three other
scripts, so the promise of ten characters was an overclaim. **`\d` is the same
overclaim in the other module.**

The concrete cost is not that a name can be written in Devanagari digits. It is
a **BOUNDARY THAT DISAGREES WITH ITS OWN SHAPER**: the allowlist would open an
address `group_identifier` then refuses to name. An inconsistency bought for
nothing, in the one place the admission's justification is load-bearing.

## 3. THE SECOND DEFECT: THE CONTROL CAUGHT ME ON ITS FIRST RUN

The pattern first shipped as `[0-9]+`, unbounded. `test_the_two_gates_agree`
went red at **14:00:56** on a 21-digit segment: the boundary admitted it, the
shaper refused it, because `groups.py` caps an identifier at
`_MAX_IDENTIFIER_DIGITS` = 20 -- *an unbounded repetition on attacker-shaped
input is a cost nobody chose.*

Same class of divergence as the `\d` one, found by the instrument rather than
by a re-read, on the run it was written. The bound is now `{1,20}` and is taken
FROM that module rather than restated, so if it moves the coupling test says so.

> **This is the whole argument for writing the control before believing the
> pattern.** I had already read the twenty-digit comment, quoted it in the
> entry, and still shipped an unbounded pattern.

---

## 4. THE BLAST RADIUS -- CONDITION 3

**Measured 13:54:48**, with `scripts/blast_radius.py` IMPORTED and not
rewritten. Its `newly_admitted(candidate, urls=...)` takes an explicit corpus,
which is the designed extension point, so the group-family spellings were ADDED
to its own corpus rather than replacing it.

    CORPUS  98 addresses  =  67 from the shipped instrument
                            +31 added here (group family, traversals,
                                non-ASCII digit forms, slug forms, urn)

    candidate                              newly admitted   newly refused
    ^.../groups/\d+/?$      (the ruling)        6                0
    ^.../groups/[0-9]+/?$   (shipped)           2                0
    ^.../groups/discover/?$ (shipped)           2                0

The two each admit exactly their own target with and without the trailing
slash. **The `\d` form admits three times as much as the form that shipped**,
and the four extra are the digit scripts above.

### The refusals were verified POSITIVELY, not inferred from absence

A blast-radius report lists what was gained; it does not assert what stayed
refused. **Re-measured at 13:55:18 with both candidates installed**, 15 probes:

    2 MUST-ADMIT    admitted
    13 MUST-REFUSE  refused
    0 mismatches

covering the roster, the requests queue, `/invite/` (refused twice, `/invite`
firing first), three slug spellings, a urn, a query string on the id, five
traversals -- including the two that normalise onto account-ending addresses
and one that normalises onto a member profile -- and a non-ASCII digit run.

---

## 5. THE CONTROL, SHOWN FAILING -- CONDITION 2

`tests/test_the_groups_id_segment_is_closed.py`. 27 addresses that must stay
refused, 4 admitted targets, 53 tests, green at **14:01:38**.

It is not a list of `is_read_url(...) is False` assertions. Those pass equally
well when the predicate has stopped admitting anything, so the file carries
three further things:

**THE COUPLING.** `test_the_two_gates_agree` drives 15 segments through BOTH
`readonly.is_read_url` and `groups.group_identifier` and asserts they answer
the same. A widening of EITHER module, in EITHER direction, is red. This is the
assertion that caught the twenty-digit bound, and it is the durable half --
because the admission's justification is a sentence borrowed from the other
module, and nothing else in the repository makes the two agree.

**THE CAN-IT-FAIL CONTROL, on every run.** Three wider spellings are installed
onto the real tuple and the breach is measured. **Taken 14:02:14:**

    anchored-wildcard   ^.../groups/.*$        BREACHES 19 of 27
        including the member ROSTER, a traversal onto an account-ending
        address, a traversal onto a member profile, and all five slugs
    any-segment         ^.../groups/[^/]+/?$   BREACHES 10 of 27
        all five slugs, the urn, and the four digit scripts
    unicode-digits      ^.../groups/\d+/?$     BREACHES 4 of 27
        the four digit scripts, and nothing else

**Condition 1 is therefore measured on THIS surface and not inherited.** The
lead's amendment recorded an anchored `.*` admitting a traversal onto an
account-ending address on the search surface; the same shape does the same
thing here, and the closed segment is what refuses it.

**AND THE SLUG CLASS SPECIFICALLY.** The ruling's words are *"goes red if the
segment class ever widens to admit letters"*, so
`test_the_letter_admitting_widenings_reach_a_slug` asserts the two
letter-admitting widenings reach a SLUG rather than merely breaching something.
The Unicode-digit widening is deliberately excluded from that test -- it admits
no slug, which is exactly why it is the plausible mistake, and it is the
coupling test's to catch.

### The revert path, measured at the same time

    patterns at HEAD 34 -> reverted 32
    all 4 targets refused after revert
    the /groups/ root STILL admitted   (the revert is surgical)
    0 guard breaches after revert

---

## 6. THE BANKING: ZERO ROWS, AND THE EVIDENCE

`GROUPS-SURFACE` held **21 GAP rows** before this wave and holds 21 after.

Nine of them were costed as blocked on this address
(`_audit/2026-09-05-groups-surface-measured.md`, table 5.4, minus the two it
carves out to `SEARCH-RESULTS-SURFACE`). **Read the census's own read/write
column for those nine, taken 14:05:**

    row     R/W   capability
    N 175    R    reach a private unlisted group by direct link
    N 63     W    join a LinkedIn group
    N 163    W    request to join a group
    M C61    W    join a group
    M C64    W    post content in a group feed
    M C65    W    add a comment to a group conversation
    M C67    W    edit or delete a group post or comment
    M C68    W    submit a group post for admin approval
    M C91    W    react in a group conversation

**EIGHT OF THE NINE ARE WRITES.**

### The eight writes: the census already ruled this, TODAY, against itself

This is not my inference. `_audit/_census/network.md` at row `N 163` was
re-costed earlier today and says it outright:

> **RE-COSTED 2026-09-19: this is DECIDE, not MEASURE, and no measurement
> moves it.** ... **AND A BOUNDARY CHANGE ALONE WOULD NOT BUY IT.** ... *"NO
> WRITE IS BOUGHT BY THIS. Joining, leaving, posting and inviting all need
> their own url, their own sanction and their own ruling."* So the real price
> is THREE things -- an address, a write sanction, and a ruling.

**This wave delivered one of the three.** Condition 4 of the ruling forbids the
other two being exercised, and rightly: a group is made of other people. The
eight stay GAP, and they were never a boundary change away from anything.

### The ninth row has no reader

`N 175` is the only READ, and the address is now admitted. It still does not
bank, because nothing can open it. **Measured 13:58 by parsing `server.py`:**

    tools defined                                    46
    tools taking a url, href or link parameter        0
    group tools                                       1   (takes no parameter)

`linkedin_group_memberships()` reads the root and nothing else. There is no
generic navigator. So the capability is not delivered by the server, and
`COVERED-UNFIRED` does not apply either: that state is for built-and-unfired,
and nothing is built.

### Why nothing was banked as COVERED-UNFIRED to show progress

Because it would be false, and the brief named the exact failure mode. The
honest ledger line for this wave is **rows banked 0, rows inflated 0**.

> **A WIDENING'S HONEST UNIT IS WHAT IT BANKS, NOT WHAT IT UNBLOCKS.** This one
> bought a PRECONDITION for nine rows and a CAPABILITY for none. Reported the
> other way it would read as the biggest movement of the day.

### And the tension that should be recorded rather than resolved here

The lead's own amended condition-2 document says: *"A surface admitted and
unusable is not a partial win; it is a blast radius paid for nothing."* That
sentence is about this wave's output as much as the search one, and the two
cases are not identical -- the search surface was unusable because the denylist
refuses 8 of 11 ordinary keywords, which is a defeat in the mechanism, whereas
this address is simply unread. Nothing structurally defeats it; a reader would
work.

**So the question is whether to pay a blast radius now or when a reader
exists.** It was ruled APPROVED IN PRINCIPLE and it landed. The blast radius is
2 addresses per pattern with 0 undefended surprises, which is about as cheap as
a widening gets. **But it is a real question and the answer here is "ruled",
not "argued" -- recorded so the next surface does not inherit a precedent
nobody meant to set.**

---

## 7. THE RE-FREEZE, ATTRIBUTED

Two digests move on any boundary edit and both were re-pinned in
`tests/test_readonly_boundary_invariant.py`. **Measured 14:03:33:**

    _ALLOWED_URL_PATTERNS   34f364971cf9e81c -> 5b5d34b6e3cc8059
    the other SEVEN digests byte-identical

In the attribution form this dict adopted from the newsletter wave:

    the tree MINUS exactly my two lines  ->  34f364971cf9e81c
                                             the value being replaced

so nothing else rides inside the re-pin. Both of the analytics wave's controls
behave: dropping a DIFFERENT allowlist line lands on a third value entirely
(`9ebcf0a8dec42642`), and a needle no line carries drops zero lines and moves
nothing.

The three denylists, both exemption tables, `SANCTIONED_MUTATIONS` and
`<functions>` are byte-identical -- which is the whole of what the second dict
is for, and it means the write touched nothing.

---

## 8. WHAT WAS REWRITTEN RATHER THAN DELETED

`tests/test_readonly.py` pinned `/groups/<id>/` and `/groups/discover/` as
BLOCKED. Per the lead's revert-path ruling, **rewrite-inverted, never delete**:
both moved to `ALLOWED` with a comment naming what flipped, and two SLUG
spellings were added to `BLOCKED` in their place, so the list is not quietly
narrower than it was.

`test_the_two_membership_roots_are_admitted_and_their_families_are_not` now
asserts an **ASYMMETRY** rather than a pair: the groups family is one segment
wider and the events family is exactly where it was. An event page is census
row `N 184` and stays refused. The two roots were never bought on the same
basis, and the test now says so.

### A prose claim this admission would have quietly falsified

`test_the_member_roster_is_refused_by_ONE_gate_and_the_count_is_the_point`
carries a sentence that was true when written: *the only thing standing between
this server and the roster is the fact that the pattern two lines away is
anchored to the root.* **The anchor moved.** The test is unchanged and still
green -- a closed numeric segment refuses `/members/` exactly as the root
anchor did -- but the sentence now describes a pattern that no longer exists,
so it is annotated at its site and re-measured against the current pattern in
the new control file rather than left to be read as current truth.

---

## 9. A COUNT CORRECTION IN A DOCUMENT FROM EARLIER TODAY

`_audit/2026-09-19-groups-surface.md` section 4 states the remaining 21 and
then tables them in seven buckets that sum to **22**. The slip is the
double-refused bucket, given as 4.

Measured against the blocker map at 13:57: of the seven rows
`2026-09-05-groups-surface-measured.md` table 5.5 lists as double-refused, four
(`N 170`, `N 168`, `M C69`, `M C62`) are now `EXCLUDED-RULED` and out of the
GAP set. **Three remain: `N 166`, `N 169`, `N 176`.** With 3 the table sums to
21 exactly.

Recorded rather than edited into that file -- it is another wave's document and
the push is frozen. **It changes no banking**: those rows need two boundary
changes and this wave made neither.

---

## 10. WHAT THE NEXT WAVE ON THIS SURFACE NEEDS

**For `N 175`, the only read:** a reader for `/groups/<id>/`. The address is
now open. **That page draws a group FEED -- other members' posts in full**, so
the reader owes it a shaper as strict as the one the search-results admission
is being held for. That obligation belongs to the reader, which is why this
line could land without one, and it is written into the entry so it cannot be
discovered later.

**For the eight writes:** an address (now held), a write sanction, and a
ruling. Two of three are outstanding on each and neither is a boundary
question. `M C67` additionally bundles a delete, which meets
`delete_or_withdraw_anything`.

**Not this wave's, and named so they are not re-derived:** the
`MUST_STAY_REFUSED` entries for `groups` and `events` inside
`tests/test_search_admission_blast_radius.py` are `/search/results/groups/` --
`SEARCH-RESULTS-SURFACE`'s rows `N 161` and `M C70`, not this family's. The
lead's amendment rules they must come out of `17733f1`. **Untouched here.**

---

## 11. THE LEDGER

    GROUPS-SURFACE GAP          21 -> 21
    rows banked                  0
    rows inflated                0
    addresses admitted           2   (+2 slashless spellings of the same two)
    addresses newly admitted
      outside the two targets    0
    page loads spent             0
    browsers opened              0
    writes fired                 0
    AI attribution               0

## 12. WHAT WAS MEASURED AND WHAT WAS NOT

**VERIFIED BY INSTRUMENT.** Every figure above carries the time it was taken.
The boundary cluster ran green at **14:04:57, 493 passed** -- baseline 436 at
13:55:57 plus this file's 53 plus 4 added parametrisations, which reconciles
exactly.

**NOT THE TREE, AND SAID PLAINLY.** No full suite was run. Two waves were live
and the lead's standing measurement is that a 24-minute run on a contended tree
is an INTERVAL, not a state. What ran is the boundary cluster and a 16-file
package-scope guard battery.

**THE SIX REDS IN THAT BATTERY ARE FOREIGN, AND THAT IS MEASURED RATHER THAN
ASSUMED.** At 14:05 the battery returned `6 failed, 900 passed`. The same three
files were run against **pristine HEAD in a detached throwaway worktree** at
14:07:38 and returned the **identical six**:

    test_a_correction_is_findable_from_the_claim  2
    test_every_tool_is_on_the_surface             1
    test_server_surface                           3

Four of the six are the stale pins the lead's downlink already names. **I did
not attribute them by reading that downlink** -- the lead's own recorded error
today was attributing a red by inference, twice, and the worktree run costs
fourteen seconds.

**NOT MEASURED LIVE.** No browser was opened, no page was loaded, and no group
was addressed. Every url in this wave is an invented numeric id or a synthetic
slug built from the sanctioned token list.

**ONE THING I WAS TOLD AND DID NOT VERIFY INDEPENDENTLY:** that
`linkedin_group_memberships` is registered in the live registry. I measured the
package's tool definitions by AST (46) and did not resolve the live registry,
so the count differs from the 44 another wave measured at 13:33 off
`tools/list`. Those are two different instruments answering two different
questions and **neither figure is load-bearing here** -- what this wave needed
was the zero, and the zero is a property of the signatures.

---

# AMENDMENT, 14:22 -- THE COMMIT IS REFUSED BY THE GATE, ON SIX REDS THAT ARE NOT MINE

**The work above is finished, verified and NOT COMMITTED.** The pre-commit
boundary gate refused it at 14:19 after a 464-second run:

    pre-commit[boundary]: 1 package file staged -> the read-only boundary
    pre-commit[boundary]: 3 test files staged -> themselves + 47 COUPLED
    COMMIT REFUSED: a guard over what this commit touches is RED.
    6 failed, 2871 passed in 464.49s

**I DID NOT `--no-verify`, AND WILL NOT.** One wave tried once today, was
blocked, stopped, and offered the bypass upward; the lead refused it and ruled
that a hook its author bypasses on install day has no authority, and less if
the lead does it. That refusal binds this wave the same way.

## THE SIX ARE FOREIGN, MEASURED IN A DETACHED WORKTREE RATHER THAN ASSUMED

The same files were run against **pristine HEAD with none of my changes
present**, twice as the tree moved under me:

    14:07:38  worktree at 744a1f4   test_server_surface 3, correction 2,
                                    every_tool_is_on_the_surface 1  -> IDENTICAL
    14:19:34  worktree at 7668b40   test_a_person_name 1,
                                    test_messaging_overview 2       -> IDENTICAL

**Every red the gate refused on is present at HEAD without me.** The lead's own
recorded error today was attributing a red by inference -- twice in ten minutes
-- and a detached worktree costs fourteen seconds, so ownership here is
measured and not read off a report.

    test_a_person_name_is_never_a_literal  an UNDECLARED synthetic needle in
                                           test_recommendation_tally.py, whose
                                           own commit a5a988a says it was
                                           deliberately left: "THE OTHER IS NOT
                                           MINE AND IS DELIBERATELY LEFT RED".
                                           Red since 2026-09-05 19:15 -- fourteen
                                           days.
    test_messaging_overview x2             SANCTIONED_MUTATIONS is 7 and both
                                           pins say 5.
    test_server_surface x3                 the stale count pins the lead's
                                           downlink already names.

### The messaging pair is stale against a freeze that ALREADY ratified seven

Worth one line because it looks like an open permission question and is not.
`READONLY_AST_AT_LAST_REFREEZE["SANCTIONED_MUTATIONS"]` is `3676d309ead50c61`,
and the live tuple hashes to exactly that -- **measured 14:03:33 in this wave's
own re-freeze run.** The boundary freeze records seven. Two assertions in a
messaging test still say five. That is a reconciliation somebody owes, not a
sanction anybody needs to grant.

## AND THE BOTTLENECK HAS A SHAPE, WHICH IS THE NEW THING HERE

The gate's coupling is COMPUTED, so it can be computed without running it.
**Measured 14:21:42 by importing the gate's own `coupled_test_files`** -- which
file I stage drags in which red:

    tests/test_readonly.py                     18 coupled  -> test_a_person_name
    tests/test_readonly_boundary_invariant.py  30 coupled  -> test_messaging_overview
                                                              test_server_surface
    tests/test_the_groups_id_segment_is_closed.py
                                               11 coupled  -> NONE

**The only clean file is the new one, and it is the only one that cannot land
alone** -- it asserts the two addresses ARE admitted, which is false until
`readonly.py` moves. And the two that drag in reds are both REQUIRED: without
`test_readonly.py`'s update the boundary is red at HEAD, which is the exact
defect this gate was built to stop, and without the invariant's re-pin the
frozen digest is stale.

> **So there is no honest subset.** Every split either leaves the tree red at
> HEAD or lands a guard that fails on the tree it is guarding. The commit is
> whole or it is nothing, and what holds it is six reds in four files owned by
> at least four other waves.

## WHAT I DID INSTEAD OF CLEARING THEM, AND WHY THAT IS THE DISCIPLINE

Clearing all six means editing four foreign files -- adopting another wave's
identity disclosure, re-pinning two count claims, and re-costing a tool surface
-- on a tree where neighbours landed **four commits in the eleven minutes this
wave was measuring** (`744a1f4`, `f484af4`, `7668b40`, and the one before).

The lead's own caution on the adjacent question is the reason:

> *the fact that settling it quickly would now be CONVENIENT is the exact
> pressure this campaign has twice recorded as the mechanism of its own worst
> calls.*

**It would be extremely convenient for me to declare six foreign reds green.**
That is the pressure, named, and it is why this wave did not take it. The
standing rule the orphaned needle's own commit states -- *admit one line at a
time, with its reason, by whoever owns the thing it fired on* -- points the
same way, and declaring somebody else's needle is adopting their disclosure
rather than helping them.

## THE WORK IS PRESERVED SO THE WORKING TREE IS NOT THE ONLY COPY

    _RECOVER_groups_admission.patch     676 lines, all FOUR files, including
                                        the new control file as a create diff

Untracked at the tree root so it surfaces in `git status`, in the form the lead
adopted for the three stranded commits. `git apply --check --reverse` verifies
it matches the working tree exactly, so a `git reset` or checkout no longer
destroys this wave.

**THIS DOCUMENT IS COMMITTED ON ITS OWN**, which the gate permits: it stages no
package file and no test file, so no coupled run is owed. The code lands the
moment the six clear -- apply the patch and commit it under this wave's
reasoning.

## LEDGER CORRECTION FOR THIS AMENDMENT

    rows banked                  0   (unchanged -- and now also uncommitted)
    commits landed by this wave  1   this document only
    code commits landed          0   REFUSED by the gate, on foreign reds
    --no-verify used             0
