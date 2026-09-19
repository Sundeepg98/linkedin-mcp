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
| `tests/test_the_groups_tool_keeps_its_properties.py` | 30 tests over five claimed properties |

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

**PAGE LOADS SPENT BY THIS WAVE: 16, COMPUTED AT FREEZE.**

    _probe_groups_locator_walk.py            2 runs x 5 loads   10
    _probe_group_memberships_tool_live.py    2 runs x 3 loads    6
    the aborted tool run (AttributeError)    navigated nowhere   0
                                                              ----
                                                                16

**THIS PARAGRAPH HAS NOW BEEN WRONG THREE TIMES: 16 from memory, then 8, then
11.** Each intermediate value was correct when written and stopped being
correct within minutes, because the wave kept running. The two corrections are
left visible and the lesson is not "count more carefully":

> **A COST SECTION WRITTEN BEFORE THE WORK ENDS IS WRONG BY CONSTRUCTION.**
> The only version worth trusting is the one computed at freeze, and the fix
> is the TIMING, not the arithmetic.

The first draft's 16 was a guess that happens to equal the final measured
figure, which is worth naming rather than quietly enjoying: **a guess that
lands on the right answer is still a guess**, and it was wrong at every moment
between being written and now. The sibling audit records the identical shape
one surface over -- a cost section that "was true when written and had stopped
being the whole story two probes later".

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

## 8A. A ZERO HAD TO BE MADE INTERPRETABLE, AND ONE BRANCH IS HONESTLY AMBIGUOUS

The reader answers five today. **It had no way to say what a ZERO would
mean**, which is the newsletter tool's `heading_seen` gap arriving on a
surface that needs it more. `groups_page.interpret_zero` closes it with three
states, and only two of them are answers:

    not_zero      memberships were found. Nothing to interpret.
    instrument    no group anchor, or no disclosure control, or the climb
                  exhausted its bound. The reader COULD NOT SEE, so the zero
                  is a fact about the reader.
    ambiguous     the walk ran cleanly over real anchors and real controls
                  and resolved no row-scoped control.

**`ambiguous` IS NOT A HEDGE AND IT IS THE INTERESTING ONE.** LinkedIn draws
suggestion rows with NO per-row control -- so a page of suggestions alone,
which is exactly what a group-less account draws, produces the identical
reading to a restyle that moved the control. **Nobody here can separate them,
because there is no known-empty groups account to test the reader against.**
That is the freeze ruling's own shape, one surface over: *a reading no
instrument can fail is not a reading.* So the tool never says he belongs to no
group, and `test_no_branch_ever_says_he_belongs_to_no_group` asserts that over
every reachable branch.

**THAT TEST CAUGHT MY OWN PROSE AND MY FIRST FIX WAS THE WRONG ONE.** The
`instrument` branch ended *"...and none of them says he belongs to no group"*
-- the forbidden phrase, negated. My first response was to strip that exact
sentence before checking, i.e. to park a negation in an exemption. **This
repository already has the rule**: a negated write verb still reads as a
write, and the exemption list carries a control asserting each entry really
does make the claim. The prose was reworded instead, the exemption was
deleted, and the test now needs none.

## 8B. AN INDEPENDENT COUNT-SITE CENSUS FOUND TWO SITES I MISSED

A child was dispatched to census every tracked site carrying `41` or `29` as a
tool-count claim, pinned to the parent commit, with no permission to edit. Its
deliverable is `_audit/_scratch/_groups-wire-count-sites.md`. **It confirmed
the four sites I changed and found two more, both invisible to the obvious
search:**

1. **`server.py` cited the test I RENAMED, twice** --
   ``test_the_surface_is_exactly_the_fortyone_tools`` at two sites, after I
   had renamed it to `..._fortytwo_...`. **A Python identifier cannot carry a
   hyphen**, so the glued spelling matches neither `forty-one` nor
   `forty one`; only a pattern with an OPTIONAL separator finds it. I caused
   these two dangling citations with my own rename and did not see them.
2. **`README.md`'s opening headline was stale by NINE TOOLS** -- *"Thirty-three
   tools ship. Twenty-one read. Five write. The other seven are write-shaped,
   gated, and cannot act at all"* against a measured 42 / 30 / 12 / 0. **All
   four numbers wrong, and the seventh category has been empty for some time.**
   It predates this wave by several bumps.

**THE SECOND ONE IS THE FINDING AND IT IS NOT ABOUT ARITHMETIC.**
`server.py`'s module docstring carries the same three numbers and IS pinned --
`test_this_modules_docstring_numbers_are_derived` reads those words and fails
if they disagree with the registry. **The README headline, which is the first
sentence any reader of this repository sees, is pinned by nothing.** So the
highest-traffic claim on the surface is the unguarded one. Corrected, with
the stale text kept and the asymmetry named in the file itself.

Two smaller notes from the same census, neither actioned: `README.md`'s "27"
still does not reconcile (30 rows over 28 distinct names, no reading gives
27), which its own paragraph already parks; and the child confirmed
independently that the pinned-inventory paragraph about `groups.py` does not
go false, because its structural claim -- no `read_`-prefixed function in
`groups.py` itself -- survives the wiring.

**AND IT CAUGHT THE TREE MOVING UNDER IT**, which is why its numbers are
trustworthy: two scans of `server.py` seconds apart disagreed on a line number
for identical text, so it pinned the whole census to an immutable SHA and
verified every prediction against `git diff` afterwards. That is the
suite-reading-is-dated-by-the-tree law applied by an agent to its own work,
unprompted.

## 8C. THIS TOOL DOES NOT REFUSE ON A MOVED COUNTER, AND ITS SIBLING DOES

`linkedin_newsletter_subscriptions` WITHHOLDS its answer when the invitation
badge moves. This tool REPORTS the move and keeps the reading. **That is a
ruling and not an inconsistency**, and it is written where it is made rather
than only here, because a reader comparing the two will otherwise assume one
of them is sloppy.

    the newsletter address sits UNDER /mynetwork/  -> a moved invitation badge
                                                     is a live hypothesis that
                                                     the load consumed one
    NEITHER of this tool's counters belongs to /groups/, and this tool takes
    THREE navigations over tens of seconds on a signed-in account -- during
    which a notification arriving on its own is the ORDINARY case

Refusing there would manufacture a false alarm out of a background event and
teach a caller to ignore the field. **A refusal is not automatically the
stricter choice**: two tools can share a mechanism without sharing a remedy,
because a remedy is judged against what the payload is for. That law came out
of two waves disagreeing earlier today and is applied here rather than
re-derived.

Pinned by `test_the_tool_has_no_refusal_branch_and_that_is_deliberate`
(the tool body branches on nothing and calls no refusal helper) **with a
control beside it** -- `test_the_sibling_that_DOES_refuse_still_does` --
because otherwise the first test would pass equally well if `_badge_refusal`
had been deleted or if nothing in the package refused any more. The contrast
is what is being asserted, so both halves are.

## 8D. THE PACKAGE'S FRONT-DOOR DOCSTRING UNDERSTATED THE WRITE SURFACE BY NINE TOOLS

Found by widening the count hunt past the census's `.py`/`.md` digit search to
number WORDS in a non-count phrasing. `linkedin_server/__init__.py` -- the
first docstring anyone importing this package reads -- said:

> Three write tools ship: save, unsave and unfollow. [...] exactly ONE
> mutating call exists in the package

Measured off the live registry and off `readonly.SANCTIONED_MUTATIONS`:

    write tools            12   (the docstring said 3)
    sanctioned mutations    5   (the docstring said 1)

**STALE IN THE DIRECTION THAT MATTERS**: understating the write surface by
nine tools, five of them irreversible.

**AND THE FILE HAD ALREADY DIAGNOSED ITS OWN FAILURE MODE, CORRECTLY, IN THE
PARAGRAPH DIRECTLY ABOVE THE STALE SENTENCE.** It reads: *"The package
docstring is the first thing a reader trusts and was the last thing
updated."* It was written after that docstring claimed the package was
read-only for a day past being true. **Then the file did it again, in the
same direction** -- because the remedy chosen was to write a better sentence
rather than to build something that would notice.

**THE SHAPE, and it is the same one as 8B:**

    server.py's module docstring   same counts   PINNED (a test reads the words)
    __init__.py's docstring        same counts   pinned by NOTHING
    README.md's opening headline   same counts   pinned by NOTHING

**The two highest-traffic count claims in the repository are the two unguarded
ones**, and both were found stale within the same hour, by a census
commissioned for something else and by a grep run while waiting for a test
suite. Neither was found by a test, because no test looks there.

Both corrected, both keeping their stale text, and `__init__.py` now points a
reader at `server.py`'s docstring for counts **on the stated ground that that
one is checked and this one is not**. Extending the docstring-number pin to
these two files is the mechanism-level fix and is left as an owed item rather
than done at 22:45 in a tree eight waves are writing.

## 8E. THE FULL SUITE, AND THE ONE RED THAT WAS BRIEFLY MINE

**`4827 passed, 9 failed, 4 skipped, 1 xfailed` in 16m27s**, over `tests/` in
the WORKING TREE. **Dated by the tree and not by a SHA** -- five neighbour
commits landed during the run, so this is a reading about a tree that was
moving, which is exactly what this repository's own law says to state rather
than to hide behind a commit hash.

Triage, by what the assertion is about rather than by count:

| red | whose |
|---|---|
| `test_stale_process_is_announced.py` x3 | the running MCP server holds older code. Named as a known class in the freeze ruling |
| `test_server_surface.py::test_both_login_names_...` | the same stale-server class, also named there |
| `test_a_named_cost_names_a_tool_that_can_incur_it.py` | a messaging wave's own new guard, landed this hour |
| `test_click_is_not_its_own_evidence.py` | writes/messaging |
| `test_a_person_name_is_never_a_literal.py` | not this wave's; no person constant was added here |
| `test_publish_post_names_its_audience.py` | the audience reader; a sibling skip says it "does not exist yet" |
| `test_a_probe_closes_its_own_tab.py` | **BRIEFLY MINE. See below.** |

### The tab guard listed my probe, and my probe closes its tab

It prints `tab closed: True` on every run and closes in a `finally`. **The
detector could not see it**: `CLOSES_PAGE` matches a receiver named `page`,
`tab` or `_own_page`, and mine was named `page_ref`. Renamed to `tab`, which
the guard recognises, and the leaker set drops from 42 to 41 with my script
off it.

**AND THAT EXPOSED A REAL DEFECT IN THE PIN, WHICH IS NOT MINE TO FIX.**
`scripts/_probe_membership_tally_live.py` closes its tab correctly -- read in
the file, not relayed -- **using the same `page_ref` name, and it is counted
as a leaker.** So the pinned 39 over-counts by at least one, and the guard's
own docstring records that an earlier crude version was tightened after
matching `.close(` on files and captures. The tightening went one notch too
far: naming three receivers is an allowlist, and an allowlist of variable
names cannot keep up with the code it scans.

**I did not widen that pattern.** It is a shared guard, widening an
accept-pattern to clear a red is the move this repository names as the way a
real guard dies, and it would not clear this one anyway -- the count would go
to 40 against a pin of 39.

**The residual +2 are named rather than guessed.** Computing the leaker set at
the commit that set the pin (`002a9dd`) and at this tree:

    at the pin commit   39
    now                 41
    ADDED since         _probe_contact_info_panel.py, _probe_premium_entitlement.py
    REMOVED since       none

**Neither is this wave's.** My two scripts are
`_probe_groups_locator_walk.py` and
`_probe_group_memberships_tool_live.py`; the second opens no session of its
own, and the first is now off the list. Owners route by
`git log --oneline -3 -- scripts/<name>`, not by this table.

## 8F. THE OWED MECHANISM WAS BUILT, AND BUILDING IT FOUND TWO MORE

Section 8D named the mechanism-level fix -- extend the docstring-number pin to
the two unguarded files -- and parked it. **It needed no ruling from anybody
and 20 minutes remained, so it was built rather than left owed:**
`tests/test_the_other_two_count_claims_are_pinned_too.py`, 18 assertions over
`README.md`'s headline, its module listing, and
`linkedin_server/__init__.py`'s write and mutation counts, each expected
sentence CONSTRUCTED from the live registry so a failure hands over the exact
replacement text.

**BUILDING IT IMMEDIATELY FOUND TWO THINGS NO ASSERTION EXISTED FOR.**

**1. `server.py`'s citation of its own guard was DANGLING IN BOTH HALVES.**
Its docstring said the split is *"pinned in the same file by
`test_this_modules_docstring_numbers_are_derived`"*. **No test of that name
exists anywhere**, and the real guard --
`tests/test_prose_that_makes_a_claim.py::test_the_server_docstring_numbers_are_derived`
-- is in a different file. The guard was passing the whole time; **the POINTER
was broken, so a reader who followed it found nothing and would conclude the
numbers were unchecked.** I concluded exactly that for about ninety seconds.

**AND I HAD REPEATED THE BROKEN CITATION AS FACT.** Sections 8B and 8D above
said server.py's docstring "IS pinned -- a test reads those words" and named
that test. I took the name from the docstring rather than from the test suite.
The CLAIM was true and the CITATION was false, and I could not have known
which until I looked -- **which is the whole argument for pinning a claim
rather than restating it, arriving inside this document about pinning
claims.**

**2. `tests/test_server_surface.py`'s OWN module docstring was stale by
nineteen tools** -- *"The tool surface: twenty-three tools, nineteen of which
do not write"* -- **three lines above assertions updated at every bump, in the
file that pins the tool count.** That is the fourth stale count claim found in
one hour and the third found by something other than a test.

Both corrected. The dangling citation is corrected with its history kept,
because a citation is a claim like any other and this one had been wrong long
enough to mislead its own author.

## 9. WHAT IS STILL OWED

* **`recommendations.py` is untouched and still has no consumer.** Its two
  blockers are unchanged: no admitted address, and no page behind it has been
  opened by anybody. **This wave kept its stronger property in view when
  choosing this tool's shape, and READ THE FILE rather than the description of
  it** -- a relayed property is a reading with a timestamp. Measured over its
  syntax tree: the three public functions are `author_present(href)`,
  `recommendation_tally(hrefs, relation)` and `relation_split(received,
  given)`, and every key any of them returns is a count, a boolean, or the
  module's own `href_shape` literal.

  The one string parameter, `relation`, is the interesting case, and it is
  handled the way `groups.py` handles a digit run: **a membership test against
  a closed vocabulary**, returning `"relation": None` rather than echoing an
  unrecognised value. So the property stated precisely is *no public function
  returns a string derived from PAGE DATA* -- stronger than `groups.py`'s,
  which publishes numeric identifiers, and right for a surface where a
  recommendation author's href IS a person's slug.

  The groups tool reaches the same place from the other end: it takes **no
  parameter at all**, so there is no input to derive anything from.
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
* **The docstring-number pin covers `server.py` and nothing else.** `README.md`'s
  headline and `linkedin_server/__init__.py`'s docstring carry the same counts
  and are checked by no test -- see 8D. Both are corrected; neither is
  guarded. **That is the mechanism this wave found the need for and did not
  build**, and it is the highest-value thing left on this list.
* **Nothing pushed.** The push freeze is the operator's and is untouched. Zero
  AI attribution across this wave's commits, verified.

## 10. PROVENANCE

| instrument | control | outcome |
|---|---|---|
| `scripts/_probe_groups_locator_walk.py` | dark-mode census 20 at both ends; REFUSES any split that is not 5 with 0 in common | GREEN, 2 runs -- the second AFTER the rename, so the edit is verified live rather than compiled |
| `scripts/_probe_group_memberships_tool_live.py` | refuses a payload disagreeing with the four corroborating instruments; refuses a non-numeric identifier; refuses a degenerate cost marked measured | GREEN, 2 runs |
| `tests/test_the_groups_tool_keeps_its_properties.py` | the `evaluate` detector planted INTO the shipped reader -- exactly one test red, file restored byte-identical | 30 passed |
| `scripts/_check_tool_count_pin_control.py` | the pin mutated wrong with the registry intact | all demonstrations behaved as stated |
| `scripts/sweep_tracked_for_identity.py` | run AFTER staging the new files, per the standing rule | PASS: 0 hits across 361 swept files |

## 11. THE WAVE, BY COMMIT

    5131271  wire the membership reader -- 41 -> 42
    8d9ad77  the cost prediction refuted by the run; the audit; the property tests
    343b192  a zero is interpretable now, and one branch is honestly ambiguous
    e1a81e9  two dangling citations my own rename created; the stale README headline
    564ed73  why this tool reports a moved counter where its sibling refuses
    6531223  the close: freeze numbers, and how to falsify each claim
    be1a6cd  the package front-door docstring understated the writes by nine tools
    5023667  the tab guard could not see my close; the pin it enforces over-counts
    7568f1c  page loads computed at freeze; the rename verified live

    97398e9  this list said five and there were nine
    <this one> the count is self-referential; the range is not

**THE WAVE IS THE RANGE `5131271..HEAD` AT FREEZE, AND STATING IT AS A COUNT
WAS THE MISTAKE.** This list said FIVE for half an hour, then NINE for one
commit -- and it could not have said anything else, because **writing the
number is itself a commit, so a self-counting list is wrong the instant it is
saved.** It is the cost paragraph of section 7 one level up, and the remedy is
not to recount: a RANGE is stable under its own recording and a COUNT is not.

That is worth more than the bookkeeping. This repository keeps finding claims
that were true when written -- a `--stat` read seconds before a commit, a port
that was listening 38 minutes ago, an agent's own clock. **This one is the
degenerate case: a claim that cannot be true when written, no matter how
carefully.** The fix is never care; it is choosing a form that survives its
own recording.

**Zero AI attribution across every commit in the range, verified by grep over
the message bodies.**
Nothing pushed; the push freeze is the operator's.

Neighbours committed five times INTO THIS RANGE while this wave ran
(`697b609`, `a373547`, `d1b1a62`, `38ea9dc`, `e4a7947` -- a messaging wave).
**None of their files is in any of the five commits above**, checked per
commit with `git show --stat` rather than by trusting `--only`, which protects
at FILE granularity and cannot protect a path two waves both legitimately own.

## 12. THE NUMBERS, RECOMPUTED AT FREEZE

    tools 42   read 30   write 12       off mcp.list_tools() at the freeze tree
    boundary   allowlist UNCHANGED, no digest re-frozen, no pattern added
    page loads 16, computed at freeze (see 7)
    identity   sweep AT THE GATE before every commit -- 0 hits, last run 368 files
    ports      8322 LISTENING pid 29216   9224 LISTENING pid 27940 (Chrome)

**The running MCP server holds older code and cannot see this tool.** It was
NOT restarted: a dozen waves share it, and restarting it to demonstrate one
wave's work is not a trade made at the end of a session. That is why the live
verification went through the package's own registry instead.

## 13. WHAT WOULD FALSIFY THIS WAVE'S CENTRAL CLAIMS

Stated so the next reader can attack them cheaply rather than re-derive them:

* **the split** -- run `scripts/_probe_groups_locator_walk.py`. It refuses to
  publish anything but five disjoint memberships. A reading of TEN means the
  walk collapsed into a flat sweep; a reading of ZERO with
  `climbs_exhausted: 0` means LinkedIn moved the per-row control, and
  `interpret_zero` will say `ambiguous` rather than guess.
* **the waiver claim** -- plant an `evaluate` call anywhere in
  `groups_page.py`; exactly one test must go red. Done once already, with the
  file restored byte-identical in the same run.
* **the cost claim** -- if a counter is ever found that responds to a
  `/groups/` load, `cost.certifies` is wrong and section 4.3 is the paragraph
  to delete. Until then the tool is bracketing with instruments that belong to
  other surfaces and says so in the payload.
* **the name claim** -- add any parameter to `linkedin_group_memberships` or a
  name-shaped one to any `groups.py` function; two tests must go red.

