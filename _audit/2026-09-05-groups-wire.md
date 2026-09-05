# Wiring `groups.py`: a tool does not have to certify its cost from the page it loads

**CORRECTS:** `_audit/2026-09-05-wire-readers.md` -- its section 2 gives three reasons not to wire `groups.py`. The first two were sound and are now measured obsolete; the third, *"a groups tool cannot certify its own cost from the page it loads"*, is a true measurement carrying a false conclusion, and this document supplies the counter-example from the same wave's own work.

**CORRECTS:** `_audit/2026-09-05-groups-surface-measured.md` -- its section 7A specifies the missing reader as needing a DOM walk in `dom.py`; the walk was re-expressed with locators and needs no `dom.py` change at all. Its section 3 says a groups tool "returns to a page carrying the instrument for the AFTER reading, or it declares the cost uncertified" -- correct, and it names one counter where the feed carries two, which is the difference between a degenerate bracket and an informative one.

Wave: `groups-wire`. 2026-09-05, 22:04-23:0x IST, times taken with `date`.
All paths are repo-relative; commands run from the repo root.

---

## 1. THE RULING, AND WHAT IT REVERSED

A wave declined to wire `groups.py`, giving three reasons. The third was the
design one:

> A groups tool cannot certify its own cost from the page it loads.

**That measurement is right and the inference from it is wrong**, and the
counter-example was wired by the same wave in the same commit.
`linkedin_notify_cost_precondition` reads a badge on `/feed/` to say something
about `/notifications/` -- **precisely because the page under test cannot
answer for itself.** Bracketing a load with a reading taken elsewhere is this
package's established pattern, not a workaround.

So the ruling this wave executed: **wire it, and bracket the load with nav
readings taken on a page that carries a counter.**

## 2. WHAT WAS BUILT

| artifact | what it is |
|---|---|
| `linkedin_server/groups_page.py` | the page reader `groups.py` never had, plus `cost_certification` |
| `linkedin_server/server.py` | `linkedin_group_memberships`, one import, one docstring paragraph |
| `scripts/_probe_groups_locator_walk.py` | the walk, run live, REFUSING to publish anything but five |
| `scripts/_probe_group_memberships_tool_live.py` | the tool called through the registry, live |
| `tests/test_the_groups_tool_keeps_its_properties.py` | 22 tests over four claimed properties |

## 3. BOTH NAMED HAZARDS WERE AVOIDED, AND NEITHER BY BEING CAREFUL

### 3.1 The `page.evaluate` waiver was not needed at all

The brief's hazard: the section-aware collector lives in a probe and uses
`page.evaluate`, which this package confines to `dom.py` behind a waiver --
the most contended file, and the one `server.py:_composer_audience_is_readable`
feature-detects on, so an unlucky name there re-arms an irreversible broadcast.

**The walk was re-expressed with Playwright's `xpath=..` parent step.** Same
rule, no script evaluated in the page:

    for each button[aria-expanded]:
        climb parents; the first ancestor holding >= 1 group anchor is the
        stopping ancestor; the control QUALIFIES only if it holds EXACTLY ONE

**FIRST LIVE RUN, 22:08, no iteration:**

    ANCHORS 11, CONTROLS 22
    row-scoped 5   |   not row-scoped 17   |   climbs exhausted 0
    stopping-ancestor widths  {11: 15, 1: 5, 5: 2}
    MEMBERSHIPS   rows 5, groups 5, DISTINCT 5, refused none
    EVERYTHING ELSE  rows 6, groups 5, DISTINCT 5, refused {root: 1}
    in common 0, DISJOINT True
    control census 20 -> 20 at both ends

**FIVE, not ten.** So `dom.py` was not touched. **Not one line** -- verified
structurally, not promised: `test_the_groups_reader_does_not_live_in_dom`
asserts the two new function names are absent from `dom.py`'s syntax tree, and
`test_the_feature_detected_name_is_still_undefined_on_dom` asserts
`server._composer_audience_is_readable() is False` at the tree as it stands.

**THE PROPERTY IS SHOWN FAILING RATHER THAN ASSERTED.** An `evaluate` call was
planted INTO the real reader -- not into a plant string -- and exactly one test
went red; the file was restored and verified byte-identical in the same run.

### 3.2 The ten-versus-five trap did not fire, and the probe would have refused it

`scripts/_probe_groups_locator_walk.py` **returns non-zero and publishes
nothing** unless it resolves five memberships with zero identifiers in common.
That is not decoration: the flat-sweep reader answers ten in the flattering
direction, and a probe that reports ten as a result is the same defect
arriving with a fresh face.

`CORROBORATED_MEMBERSHIPS = 5` and `agrees_with_corroborated` travel in the
tool's own payload, so a caller sees the agreement rather than taking it on
trust.

### 3.3 One number DID move between the two instruments, and it is not the answer

    the evaluate-based probe, earlier today   10 controls -- widths {5: 2, 11: 3}
    the locator walk, 22:08 and 22:17         22 controls -- widths {5: 2, 11: 15}

Twelve more PAGE-SCOPED disclosures were drawn. **The row-scoped count is 5 in
both, and the block-scoped count is 2 in both.** The discriminating half of the
histogram is stable and the non-discriminating half is not, which is the
direction you want: the rule is insensitive to how many page-level controls
LinkedIn happens to render.

## 4. THE COST -- MEASURED, AND SHARPER THAN EITHER BRANCH I WAS OFFERED

The brief allowed two outcomes: bracket it, or ship reporting UNMEASURABLE
with the measurement. **The measurement gives a third answer that is better
than both.**

### 4.1 What each page carries, measured

    /feed/          invitations   READABLE      notifications   READABLE
    /groups/        invitations   UNREADABLE    notifications   UNREADABLE

**The groups page carries NEITHER counter.** That is why the tool navigates
back to the feed -- a third page load, which is the entire price of the
ruling. It is asserted in the control flow by
`test_the_tool_returns_to_the_feed_to_take_the_after_reading`, so removing it
as an "optimisation" turns a test red rather than silently deleting the
bracket. The tool also REPORTS the two on-page states
(`counter_states_on_the_groups_page`), so the day LinkedIn draws a badge there
the third navigation becomes removable ON EVIDENCE.

### 4.2 I PREDICTED DEGENERATE. THE LIVE RUN REFUTED ME.

I wrote -- in a docstring, in a commit message, and in this wave's plan -- that
the cost would come back **UNMEASURABLE**, because the invitation badge is
known to sit at zero on this account. Measured 22:17:

    invitations     0 -> 0    unmoved_at_zero        DEGENERATE
    notifications   1 -> 1    unmoved_above_zero     INFORMATIVE
    verdict         unmoved,  measured = True

**One counter was degenerate and the other was not.** The prediction is left
in the source rather than edited away, because the reason it was wrong is the
useful part:

> **THE CHEAPEST REPAIR FOR A DEGENERATE INSTRUMENT IS A SECOND INSTRUMENT,
> NOT A BETTER ARGUMENT ABOUT THE FIRST.**

A bracket built on the invitation badge alone could only ever have returned
UNMEASURABLE -- it would have been an instrument reporting its own shape, which
is the exact defect `linkedin_notify_cost_precondition` refused to build into
`linkedin_notifications`. The second counter costs nothing (both render on the
same nav of the same already-loaded page) and it is what made the pair carry
information on the day.

### 4.3 AND `unmoved` STILL DOES NOT MEAN THE LOAD IS FREE

This is the limit no future non-zero badge repairs, and it is in the payload
under `cost.certifies` rather than left for a caller to derive:

> Every counter this package can read is a nav badge for a **different
> surface** -- pending invitations, unread notifications. **Nothing measured
> anywhere establishes that a `/groups/` load touches either.** So `unmoved`
> certifies that THOSE COUNTERS did not move and says nothing about a
> groups-specific cost.

**This server holds no instrument known to respond to the event being
bracketed.** That is the honest form of the answer the brief asked for, and it
is stronger than "UNMEASURABLE" because it names WHICH question is
unanswerable and WHY, while still returning the real reading that was taken.

### 4.4 There is no branch that returns a cost of zero

`cost_certification` has four verdicts -- `uncertified`, `moved`, `degenerate`,
`unmoved` -- and **none of them is a number**. All four are reachable from
inputs where each is the only answer, parametrised in the test file.

**THE ASSERTION THAT NO SUMMARY FIELD IS A NUMERIC ZERO CAUGHT A PYTHON TRAP IN
ITS OWN FIRST DRAFT.** Written as `assert 0 not in [...]` it went RED -- on
`measured: False`, because `False == 0`. A "no zero here" check that fires on a
boolean is a check somebody would weaken to make it pass, and weakening it is
how the real guard gets lost. It now excludes `bool` **by type**, with the
failure recorded beside it.

## 5. THE TOOL COUNT, BY MEASUREMENT

    before   41    mcp.list_tools()
    after    42    mcp.list_tools()
    split    30 read + 12 write + 0 write-shaped-and-unable = 42

**The write side is byte-identical across this change**, which is the half that
matters here more than usual: the surface this tool opens DRAWS A WRITE
AFFORDANCE. Every membership row's overflow menu offers `Leave this group`,
measured on all five earlier today. This tool presses nothing, follows no
per-row control, and returns counts. (The per-row `Update your settings`
control is an `<a>` whose href meets two forbidden substrings and is refused
before the allowlist is consulted -- so it is not merely unpressed, it is
unreachable.)

Sites that moved:

| site | what moved |
|---|---|
| `tests/test_every_tool_is_on_the_surface.py` | `assert len(_tool_names()) == 42` |
| `tests/test_server_surface.py` | `EXPECTED_TOOLS`, `== 42`, the read split `== 30`, and the test's own NAME (`..._fortyone_...` -> `..._fortytwo_...`) |
| `linkedin_server/server.py` docstring | headline and the three-way split, both regex-read by a test |
| `README.md` | the registry sentence, the no-row list, and a history line |

**No line was deleted from `tests/test_readers_outside_dom_are_a_pinned_inventory.py`, and that is itself the finding.** `groups.py` was never on that
list -- the detector selects functions named `read_*` and `groups.py` has none
-- so **a module went from unreachable to wired without moving any number in
the file built to track exactly that.** The new reader IS in that file's scope
and is absent from the pin only because `server.py` calls it, which is the
detector working. A successor note saying so was APPENDED rather than edited
into the paragraph it succeeds.

**No allowlist pattern was added and no boundary digest was re-frozen.**
`/groups/` was already admitted, anchored, and `/feed/` needs no argument. The
boundary-freeze chain has one head and this wave never touched it.

## 6. THE COUNT PIN IS A CONTROL AND IT WAS SHOWN STILL FAILING

`scripts/_check_tool_count_pin_control.py`, run after the bump:

    live registry: 42 tools
    broken reading: ['_attach_recipient_ids', 'linkedin_my_profile']

    A. the two rules, over the registry measured while the defect was live
    PASS   rule 1 (a shipped read tool is missing) rejects the broken reading
    PASS   rule 2 (a private helper is on the surface) rejects the broken reading

    B. with the live registry REPLACED by that broken reading, the guard goes red
    PASS   test_every_read_tool_this_package_ships_is_registered goes RED
    PASS   test_no_private_helper_is_a_tool goes RED
    PASS   the CONTROL itself goes RED

    C. live registry INTACT, pinned number WRONG -- only the count may move
    PASS   the pin assertion is present and readable
    PASS   the pin agrees with the live registry (42)
    PASS   the mutation actually changed the source
    PASS   the control goes RED on a WRONG pin
    PASS   rule 1 stays GREEN under the wrong pin
    PASS   rule 2 stays GREEN under the wrong pin

    all demonstrations behaved as stated

Part C is the claim written beside the bump: with the registry intact and only
the pin wrong, the two rules stay green and the count assertion alone moves.
**Its predecessor promoted this from disposable to tracked exactly so that a
bump would not become a number edit. It did not.**

## 7. THE SUCCESS PATH IS EXERCISED -- THE THING THREE PREDECESSORS COULD NOT DO

`_audit/2026-09-05-wire-readers.md` section 7 records live verification
ATTEMPTED and BLOCKED: Chrome on 9224 was down. **It is up.** So this wave's
tool was called **through the registry**, not through its undecorated body --
`mcp.call_tool("linkedin_group_memberships", {})`, which is what a client
calls. Three defects in this repository's history lived in the wiring rather
than the reader.

    REGISTRY: 42 tools; linkedin_group_memberships present: True
    ok=True  pages_loaded=3  redirected=False
    anchors 11, controls 22, row-scoped 5, not row-scoped 17, exhausted 0
    MEMBERSHIPS  rows 5, groups 5, DISTINCT 5, refused {}
    OTHERS       rows 6, groups 5, DISTINCT 5, refused {root: 1}
    in common 0, DISJOINT True
    agrees with the four corroborating instruments: True
    COST: unmoved, measured=True
    counter states ON the groups page: both UNREADABLE
    IDENTIFIERS RETURNED: 10 -- non-numeric among them: 0

**Ten identifiers, zero non-numeric.** A non-numeric segment is a slug and a
slug is a name; `groups.group_identifier` refuses one, and the probe checks the
payload rather than trusting the chain. **No identifier was printed** -- the
module publishes them because a caller computing overlap needs them, and a
transcript is not that caller.

**PAGE LOADS SPENT BY THIS WAVE: 8, counted per run rather than remembered.**

    _probe_groups_locator_walk.py            1 run  x 5 loads    5
    _probe_group_memberships_tool_live.py    1 run  x 3 loads    3
    the aborted tool run (AttributeError)    navigated nowhere   0
                                                              ----
                                                                 8

**THIS PARAGRAPH SAID 16 IN ITS FIRST DRAFT**, from my own sense of what I had
run rather than from the runs. Corrected before the commit and left visible,
because a cost section that is merely wrong and a cost section that is out of
date are indistinguishable to a reader -- which is the finding
`2026-09-05-groups-surface-measured.md` section 6 records about its own.

Every run closed its PAGE in a `finally` and never the CONTEXT. The dark-mode
control census read 20 at both ends of the locator run.

## 8. WHAT I GOT WRONG, LISTED

1. **The degenerate prediction.** Section 4.2. Refuted by the run, corrected in
   place with the prediction kept visible.
2. **`assert 0 not in [...]`.** Section 4.4. `False == 0`; caught by my own
   test going red, not by review.
3. **`mcp._tool_manager` does not exist on FastMCP 3.4.7.** The live probe's
   first attempt raised `AttributeError`; the public `mcp.call_tool` is the
   route. Cost: one aborted run that navigated nowhere and is not counted in
   the sixteen.

## 9. WHAT IS STILL OWED

* **`recommendations.py` is untouched and still has no consumer.** Its two
  blockers are unchanged: no admitted address, and no page behind it has been
  opened by anybody. **This wave deliberately kept its stronger property in
  view when choosing this tool's shape** -- that module goes further than
  `groups.py` (no public function returns any string derived from its input,
  because a recommendation author's href IS a slug). The groups tool takes
  **no parameter at all**, which is the same idea from the other end: there is
  no input to derive anything from.
* **`shape.membership_row` still has its declared hole and still has no
  consumer.** Untouched by this wave, deliberately -- it is `groups-events`'
  artifact and its limit is asserted by its own tests. The name-free reader is
  the ruling's answer; the two are allowed to coexist and now one of them is
  reachable.
* **`notify_cost.cost_delta` remains unwired.** Unchanged. This wave read the
  notifications badge but never opened `/notifications/`.
* **The `Leave this group` WriteSpec.** Measured present on all five rows, on
  an already-admitted address, and NOT built. Its reversibility is not obvious:
  rejoining a private group needs a manager's approval, and nothing on the root
  says which of the five those are.
* **A groups-specific cost instrument does not exist**, and section 4.3 is the
  statement of that gap rather than a workaround for it.
* **Nothing pushed.** The push freeze is the operator's and is untouched. Zero
  AI attribution across this wave's commits, verified.

## 10. PROVENANCE

| instrument | control | outcome |
|---|---|---|
| `scripts/_probe_groups_locator_walk.py` | dark-mode census 20 at both ends; REFUSES any split that is not 5 with 0 in common | GREEN, 1 run |
| `scripts/_probe_group_memberships_tool_live.py` | refuses a payload disagreeing with the four corroborating instruments; refuses a non-numeric identifier; refuses a degenerate cost marked measured | GREEN, 1 run |
| `tests/test_the_groups_tool_keeps_its_properties.py` | the `evaluate` detector planted INTO the shipped reader -- exactly one test red, file restored byte-identical | 22 passed |
| `scripts/_check_tool_count_pin_control.py` | the pin mutated wrong with the registry intact | all demonstrations behaved as stated |
| `scripts/sweep_tracked_for_identity.py` | run AFTER staging the new files, per the standing rule | PASS: 0 hits across 361 swept files |
