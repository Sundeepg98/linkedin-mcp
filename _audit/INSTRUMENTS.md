# The instrument register

**An instrument enters this file only if it has been SHOWN FAILING.** A check
that cannot fail certifies nothing, and a register of such checks is worse than
no register: it manufactures confidence at scale. Every entry below names the
mutation that killed the guard and where the guard lives, so a reader can
re-plant it rather than trust this file.

This register was created on 2026-09-04 because a session found THREE checks
that could not fire, in one wave, and filing them in a scratch progress file
would have taught nobody anything durable. The three are section 1. The
method that found them is section 2.

**THIS FILE IS APPEND-ORDERED. FIND ENTRIES BY NAME, NEVER BY SCROLLING TO A
SECTION.** A number records which SECTION an entry belongs to; it says nothing
about where the entry SITS. Several waves wrote this file at once and every one
of them appended, which is the correct behaviour under contention -- an
in-place insert into a contended file loses somebody's work. So 2.5, 2.6, 2.7
and 2.7a sit physically after section 4, and later additions will do the same.

This is stated rather than fixed on purpose. Renumbering would break the
citations already written against these names in `linkedin_server/readonly.py`
and `linkedin_server/shape.py`, and it would have to be redone after the next
append. **A reader who cannot find an entry treats it as absent -- and an
absent entry in a register of failing-proofs is exactly the confidence-at-scale
this file exists to prevent**, so knowing how to look is load-bearing rather
than cosmetic. Grep for the entry NAME.

**How a red-proof is run here.** Never in the live tree -- several agents write
`linkedin_server/` concurrently and mutating a shared file even briefly can be
picked up or clobbered. Copy `linkedin_server`, `tests`, `scripts` and
`pytest.ini` to a scratch directory, **print `linkedin_server.__file__` and
confirm it resolves under the copy before touching anything**, plant ONE
mutation, run ONLY the selector that should die, restore by re-copying that one
file, repeat. Finish on a clean control run.

> **THIS RULE WAS ALREADY HERE ON 2026-09-04 AND WAS VIOLATED THE SAME DAY,
> BY THE WAVE THAT WROTE MOST OF SECTIONS 2 AND 3 BELOW.** The upload wave
> proved its three digest gates by mutating the REAL `linkedin_server/writes.py`
> three times -- the file another agent was holding uncommitted work in at that
> moment. Each mutation opened a window of roughly five seconds in which a
> byte-exact restore would have silently reverted anything they wrote. Nothing
> was lost, and that is LUCK RATHER THAN DESIGN: a restore verified by sha256
> against the pre-mutation bytes cannot tell a clobbered edit from a clean one,
> because both produce the hash it is checking for. **The verification I ran
> was incapable of detecting the failure I was risking**, which is the same
> shape as every entry in section 1.
>
> It was disclosed unprompted with the window measured rather than found in
> review, which is the only reason it is a receipt and not an incident. The
> rule needed no strengthening; it needed reading. **Read this preamble before
> planting a mutation, not after.**

**THE PROOF STEP, tightened 2026-09-04 in the same wave as the receipt above,
and BE PRECISE ABOUT WHAT CHANGED because most of it was already written.**
The rule already said to print `linkedin_server.__file__` and CONFIRM it
resolves under the copy. Two narrow things were missing, and both are the
difference between an instruction and a control:

* **ASSERT, do not confirm.** "Confirm" is a thing a person does with their
  eyes, between the copy and the mutation, at the exact moment they are keen
  to get on with it -- and it is skippable in silence. An `assert` that halts
  BEFORE the first write is not. The check that catches you must be the one
  that runs whether or not you remember it.
* **ASSERT THE NEGATIVE TOO.** "Resolves under the copy" is a substring test
  and passes on a path that contains BOTH roots; the repo path must also be
  asserted ABSENT. One of those two checks alone is a check that can be
  satisfied by the wrong tree.

The shape, run before anything is mutated:

    resolved = <subprocess: import linkedin_server.dom; print(dom.__file__)>
    assert str(COPY) in resolved   # it IS the copy
    assert str(REPO) not in resolved   # and it is NOT the live tree

**"Run against a copy" is an intention. That is a measurement.** Everything
after it -- the mutation, the selector, the restore -- is only as good as the
answer to "which tree am I actually importing", and that question has a
cheap, checkable answer that no amount of care substitutes for.

---

## 1. THE THREE GUARDS THAT COULD NOT FIRE

### 1.1 `NEVER-EXECUTED-BUT-REPORTED-GREEN`

**The most expensive shape in this codebase, and it was found in the work
written to avoid it.**

`tests/test_tools.py::test_a_checkbox_filter_emits_its_parameter_only_when_it_is_on`
was written, run, and reported green. It had never executed: the `-k` selector
used to "verify" it (`search or boolean or job_type or location`) matched none
of its name or its parametrize ids. Run for real it failed 4 of 4.

**The defect underneath.** The `drive` fixture (`tests/test_tools.py:216`)
closes over ONE list. Calling `drive()` a second time returns that same
accumulating list, not a fresh one -- so a test that installed twice read the
FIRST call's url as the second call's, and the ON url was compared against
itself. The test asserted its own tautology.

    THE FIX      one install, two calls, `assert len(navigations) == 2`
                 first, then `on_url, off_url = navigations`
    THE CONTROL  `if True:` in the emit loop  -> dies on the OFF assertion
                 `if False:` in the emit loop -> dies on the ON assertion
                 Both must die. One direction alone leaves the word ONLY
                 in the test's name untested.

**THE STANDING RULE THIS PRODUCES: a `-k` run is not evidence a test ran.**
Confirm with `--collect-only` and count the ids, or run the file. A selector
that matches nothing exits 0 and prints "deselected", which reads like success.

### 1.2 `STRUCTURALLY-BLIND-GUARD` -- the fixture cannot reach the branch

`tests/test_sdui_surfaces_fixture.py::test_reading_the_count_did_not_cost_the_headline`
is named for the `_COUNT_LINE` exclusion in `shape.parse_profile_topcard`.
Deleting that exclusion left it PASSING on both committed renders.

**Why, measured by differential run rather than reasoned about.** On both
fixtures the count line sits BELOW `Contact info`. `parse_profile_topcard`
takes headline and location from the lines ABOVE that link and returns; the
count is never a candidate, so adding it to `eligible` changes nothing. Three
shapes were run against a mutated module and a pristine one:

    count below "Contact info"   identical output   clause DEAD
    count above "Contact info"   identical output   clause DEAD
    NO "Contact info" line       differs            clause LOAD-BEARING

    THE FIX      `test_the_count_exclusion_is_load_bearing_without_a_contact_line`
                 -- line input, not a fixture, because the shape is defined by
                 what it LACKS and a capture cannot be trusted to go on lacking
                 something
    THE CONTROL  delete `and not _COUNT_LINE.match(line)` from the `eligible`
                 comprehension -> the new test fails, `location` comes back as
                 "268 connections"

**THE STANDING RULE: a guard named after a branch must be shown to REACH that
branch.** The old test still passes and is still worth having; its docstring
now says in its own words that it cannot fail from the mutation its name
implies.

### 1.3 `GUARDS-ITS-OWN-COPY` -- the test re-implements the code it names

**NAMED DEFECT, not a note.** The name claims coverage the test does not have,
and the next reader will believe the name.

`tests/test_sdui_surfaces_fixture.py::test_a_skill_keeps_only_its_name_not_its_evidence_lines`
reads as the guard on skill-evidence separation. It cannot catch a defect in
`dom.read_profile_detail_entries` AT ALL. Its helper `_skills()` calls
`dom.harvest_linked_cards` directly and re-implements the name-selection loop
INSIDE the test file, so it exercises the test's own copy of the logic.

    THE CONTROL  add `entries.extend(rest)` to `read_profile_detail_entries`
                 -- the reader now returns evidence lines as skills, which is
                 exactly the defect this test is named for.
                 test_a_skill_keeps_only_its_name...   PASSES
                 test_the_evidence_lines_never_rejoin_the_skills_list  FAILS

The reader is covered by the second test. The first is left alone
deliberately -- it is another wave's, and it is not WRONG, only narrower than
its name. What is corrected is the claim, not the coverage.

**THE STANDING RULE: a test that re-implements production logic tests the
copy.** If a helper in a test file duplicates a function under test, the
guard's subject is the duplicate. Call the real function or rename the test.

### 1.4 `MOCKS-THE-READER-IT-DEPENDS-ON` -- and the refusal that agreed with the docstring

**The worst-placed blind check found in two days, because its false result was
the one the documentation told you to expect.**

`dom.read_comment_surface` harvested control names with
`census.get("control_shapes", [])`. `read_surface_census` has never returned
that key -- its keys are `counts`, `controls`, `controls_read`, `truncated` --
so the loop iterated an empty list on every page. A second bug sat in the same
line: the shaped records carry no `count` field, so `row.get("count") or 0`
would have summed zeros even with the key corrected.

`writes._comment_submit_gate` builds its before/after maps from that reader.
With `names` permanently `{}`, `arrived` was permanently empty, so the gate
refused `2_nothing_arrived` **on every page, forever, for a reason with
nothing to do with LinkedIn** -- and `controls_read` uses a key that DOES
exist, so the refusal reported a plausible non-zero count beside the empty
map and looked alive.

**WHY IT SHIPPED:** `tests/test_comment_delta_gate.py` monkeypatches
`dom.read_comment_surface` with a stand-in returning a fixed census. The gate
is thoroughly tested, against a fake reader, so the real one's dead key was
invisible to its own suite. That is 1.3 one level up: 1.3 re-implements the
logic, this MOCKS it, and both leave the named subject unexercised.

**WHY IT WAS EXPENSIVE:** `comment_on_item`'s docstring instructs the reader
that it is "EXPECTED TO REFUSE ON FIRST USE, and that is the design rather
than a defect". A fire would have typed his words into the box, refused,
left a draft this package has no surface to find or remove, and handed back
a refusal indistinguishable from the designed one -- and it would have been
written up as a measurement. **A false result that agrees with the
documentation's own prediction is the most expensive shape available.** It
did not land only because a harness classifier refused the call.

    THE CONTROL  swap the reader's census key back: in
                 `dom.read_comment_surface`, iterate
                 `census.get("control_shapes", [])` instead of
                 `census.get("controls", [])`.
                 tests/test_comment_delta_gate.py
                   test_the_real_reader_harvests_names_off_a_census_payload
                     FAILS -- {} where three names are expected
                 Offline, no browser: the test feeds a page fake whose
                 `evaluate` returns three named controls and reads `names`.
                 Every test added with this entry drives the REAL reader --
                 a stand-in is what hid the defect, so a stand-in cannot be
                 what certifies the repair.

    THE CONTROLS test_an_unnamed_control_is_counted_rather_than_dropped_silently
                 -- an arrival with no accessible name must be REPORTED, or a
                 nameless control arriving reads as nothing arriving.
                 test_the_gate_still_reports_the_ordinary_absence_with_no_menu_open
                 -- `2b_menu_items_present` must NOT fire when no menu is
                 open. Without this, a branch that always fired would look
                 like a branch that works.

**THE SECOND HALF, and it is the same disease in the other direction.**
`dom.CENSUS_CONTROL_SELECTOR` carries no menu role, so a delta pointed at a
menu reports a clean absence. Measured 2026-09-04: a comment's own overflow
menu draws three `[role="menuitem"]` nodes (`Copy link to comment`, `Edit`,
`Delete`). The repair is 2.2's law -- a blind channel may not print a bare
absence -- and it is a COUNT (`menus`, `menu_items`, appended last to the
`counts` block beside `dialogs`) rather than a widened selector: widening
shifts `controls_read` and the shaped-name distribution across all 19
fixtures the boundary freeze hashes, and menu items on a comment menu sit
beside people's names, so enumerating them would add a name-bearing class to
a structure many consumers read.

**AND THE COUNT IS CONSUMED.** `_comment_submit_gate` refuses
`2b_menu_items_present`, distinct from `2_nothing_arrived`, when arrival is
empty and menu items are present. *Adding an unread count while fixing an
unread `labels` field would have been absurd* -- the same wave had just found
`writes.py` discarding `read_reaction_surface`'s `labels`, the string its own
fire was supposed to measure, from the dict it had already built.

---

## 2. THE MEASUREMENT PATTERNS WORTH REUSING

### 2.1 `A-NEGATIVE-CONTROL-MAKES-A-ZERO-MEAN-SOMETHING`

Established while measuring LinkedIn's job-search filter parameters
(`scripts/_probe_job_search_filter_params.py`).

The question was whether `f_AL`, `f_EA`, `f_JIYN`, `f_FCE` and `f_JT` are
honoured. A pill reading "checked" proves nothing on its own. The instrument
is the control: a parameter LinkedIn has never had, `f_ZZQQX=true`, loaded
under identical conditions.

    f_ZZQQX=true   0 pills moved, count identical, and the parameter was
                   STRIPPED from the landed url

**That is what makes "behaves like baseline" MEAN ignored** -- and no candidate
read that way. Without the control the same numbers are a screenshot.

**Its second law, learned the same day: a control at the KEY level does not
settle the VALUE.** `f_JT=ZZ` survived into the landed url verbatim while being
demonstrably inert. So url survival measures whether LinkedIn recognises the
KEY and says nothing about whether the VALUE was applied. A value-level control
(`f_JT=ZZ` against `f_JT=F`) is a different instrument and had to be built
separately.

### 2.2 `A-BLIND-CHANNEL-MUST-NOT-REPORT-A-CLEAN-ABSENCE`

Same probe, and the same disease as section 1.

Pass one filtered controls to those carrying `aria-pressed`, `aria-checked` or
`aria-expanded`, then reported which differed. It reported `(none)` for
`f_JT=F`. The control that proves `f_JT` applies is `Reset selected Job type`,
and it carries **no aria state at all** -- so the gate had structurally excluded
the one thing that could answer, and printed a zero.

**A zero from a gate that cannot see the thing is not a negative reading.** The
repair is not a wider gate; it is that a channel which dropped candidates may
not print a bare absence. It must carry its denominator:

    (none on the aria channel; N controls carry no aria state and are
     invisible to it)

### 2.3 `A-NUMBER-SHIPS-WITH-THE-DENOMINATOR-IT-WAS-TAKEN-OVER`

**The pattern this session most wants reused.** A number that ships with its
denominator cannot be quoted onward as a property.

`dom.read_profile_detail_entries` answers census row `N 118` -- endorsement
counts on the operator's own skills -- and the answer is "LinkedIn draws none".
It does not ship that as a constant. It ships a READING, re-taken on every
call, carrying what it looked at: cards searched, card lines searched,
characters of main text, and whether the body mentions one at all.

Two reasons, and the second is the general one:

* **Two worlds fit the evidence and nothing on his own account separates
  them** -- LinkedIn draws the line only for a skill someone endorsed, or
  LinkedIn stopped drawing it. A hardcoded answer would go on denying the count
  on the day one appears.
* **A "no" with no denominator is indistinguishable from a page that never
  loaded.** That confusion has cost this repository more than one round.

    THE CONTROL, and it is the entry condition for the whole reading:
    `test_the_endorsement_reader_can_say_yes` hands the same reader a card that
    DOES carry the line. Hardcoding `"drawn": False` kills that test and
    nothing else -- every other endorsement assertion is a negative taken on a
    page that draws none, so all of them would survive it.

### 2.4 `TWO-INSTRUMENTS-DISAGREEING-MAY-BE-TWO-MOMENTS`

Three instances in one day, all initially read as somebody's error:

* a `server_module` NameError reported against line numbers exactly one higher
  than any commit's -- the checker read the file in the seconds between a test
  being appended and its import being added
* a report that `tests/test_a_sanitiser_earns_its_entry.py` did not exist,
  accurate when taken; the docstring naming it was written ahead of the file
* a phone number reported in `scripts/_probe_interests_entity_shaping.py`
  against a scan finding zero -- the number existed in a PRE-COMMIT draft, was
  refused by `test_no_committed_identity`, and was replaced before the first
  commit

**Before treating a disagreement as an error, ask whether the two readings
share a moment.** A reading carries a timestamp its reader cannot see.

---

### 2.5 `TRIAGE-THE-CANDIDATES-INSTEAD-OF-CLASSIFYING-THEM`

**The move to reach for whenever the task is "detect X in prose" and X cannot
be detected.** Named at the team lead's direction because it generalises past
the check that produced it.

**THE SITUATION.** A defect was found in `_audit/`: a correction can name what
it corrects, and a corrected document cannot name its corrector, so the arrow
points one way and every reader who starts at the claim reaches the wrong
document first. The obvious fix is a check that FINDS corrections and demands
a back-pointer for each.

**THE OBVIOUS FIX CANNOT BE BUILT, and that was measured before anything was
written rather than discovered afterwards:**

    94 documents under _audit/
    27 candidate (corrector, target) pairs under a loose vocabulary
    26 of the 27 are MENTIONS, not corrections
     1 is a genuine document-corrects-document pair

The 26 are not near-misses. They are structurally different things that no
vocabulary separates: a markdown table row whose NEIGHBOUR carries a verdict
(tables have no blank lines, so proximity is meaningless); a correction of a
HYPOTHESIS rather than of the cited document; a later document QUOTING the
original correction; a self-correction about the author's own arithmetic; an
open question explicitly DECLINING to rule. A tighter vocabulary at a one-line
window reproduces 6, of which the same 1 is genuine.

**So a classifier would either miss corrections or cry wolf, and a check that
cries wolf gets an allowlist bolted on until it is a silencer.**

**THE MOVE: STOP CLASSIFYING. MAKE THE NOISE DO THE WORK.**

    1. ASSERT the contract only where it is DECLARED. A corrector writes a
       `CORRECTS:` marker; the named target must carry `CORRECTED BY:`. Zero
       false positives, because the assertion is over markers and not prose.

    2. ASSERT that every CANDIDATE the loose scan finds is either declared
       under (1) or listed on a `NOT_A_CORRECTION` dict with a written reason.

Step 2 is what makes step 1 more than an honour system. A new correction
written into `_audit/` turns the suite RED until somebody either declares it or
says why it is not one. **The precision problem, which is unsolvable, becomes a
bookkeeping obligation, which is bounded** -- 27 entries, and a wave writing a
genuine correction pays one line.

**THE ENTRIES ARE THEMSELVES CHECKED.** A `NOT_A_CORRECTION` entry for a pair
the scan no longer produces FAILS as loudly as a missing one -- the discipline
`test_reader_reachability.UNREACHABLE_BY_DESIGN` and
`test_selectors_resolve.NOT_RESOLVED_HERE` already keep. Without that, the dict
is a silencer with extra steps.

**WHEN TO REACH FOR IT.** Any check whose subject is a JUDGEMENT a regex cannot
make -- is this a correction, is this a real TODO, is this comment stale, does
this docstring describe this function. Do not tune the detector. Let it
over-report, then require every report to be resolved. The detector's job stops
being "be right" and becomes "miss nothing", which a loose pattern is actually
good at.

**AND IT MUST BE ABLE TO GO RED ON ITS AUTHOR.** It did, within the hour:
retiring census row `N 118` quoted both documents in the correction chain, and
the check stopped the suite until both were triaged. **A check whose first
real-world firing is against the person who wrote it is the cheapest available
proof that it is not a silencer** -- cheaper than any mutation, because nobody
arranged it.

    THE INSTRUMENT  tests/test_a_correction_is_findable_from_the_claim.py
    THE CONTROLS    delete the back-pointer   -> 1 test fails
                    delete the marker         -> 2 fail (orphaned pointer AND
                                                 untriaged candidate)
                    plant a stale triage entry-> 1 fails
                    All three shown failing in a scratch copy before the
                    check was trusted.

**ONE DEPLOYMENT DETAIL THAT DECIDES WHETHER IT IS ADOPTABLE.** The corrected
claim is NOT rewritten. `2026-08-22-parity-linkedin.md` line 18 is
byte-identical to what it always said -- verified by diff, so every existing
`:18` citation still resolves -- and the back-pointer is a NEW line beneath it.
The record still shows what was believed; it just cannot be read without
meeting its refutation. A check that required editing the claim would have been
refused by everyone holding a citation to it.

---

## 3. GUARDS THAT MEASURED A NAME INSTEAD OF A CONTRACT

Section added 2026-09-04 by a cold verifier. APPENDED rather than merged,
because this file had been written two minutes earlier and a full rewrite would
have clobbered whatever was in flight -- 2.4 is the same lesson from the other
side.

### 3.1 `A-GUARD-THAT-MATCHES-A-NAME-CERTIFIES-A-NAME`

`tests/test_navigation_is_never_derived.py` stops its taint walk at a call to
any function whose NAME is in `_SANITISERS`. The whole test is
`func.id in _SANITISERS`. Nothing checked the contract behind the name.

**SHOWN FAILING BY MUTATION** -- seven versions of the real source of
`scripts/_probe_job_search_filter_params.py`, through the guard's own
`output_violations`:

    1  real source, unmodified                             GREEN
    2  the sanitiser's body gutted to return its input      GREEN   <-- defect
    3  the sanitiser renamed, body intact                   GREEN
    4  a synthetic module with its own no-op `_redact`      GREEN
    5  a synthetic module with no sanitiser at all          RED
    6  the sanitiser call DELETED, value emitted anyway     GREEN
    7  arm 6 with that one `emit(...)` made `print(...)`    RED

Arm 2 against arm 5: a body returning its input verbatim passes the check that
the same code without the name fails. Arm 4: any module may define the name and
inherit the trust. **Arms 6 and 7 differ by ONE IDENTIFIER** -- `emit` against
`print` -- and that was the entire difference between green and red, because
the probe routes its output through a closure the sink list does not know.

    THE INSTRUMENT   tests/test_a_sanitiser_earns_its_entry.py
                     ENROLMENT: every function in the scanned tree whose name
                     is in _SANITISERS must be declared, which is what makes
                     the name non-transferable. DEMONSTRATION: each is run
                     against four needled urls and must change all four, and
                     must still DISCRIMINATE, so a constant-returner fails too.
    THE CONTROL      the same two tables through an identity function and
                     through a constant function; both must be caught. In the
                     file as test_the_table_would_catch_a_do_nothing_sanitiser
                     and ..._a_constant_returning_sanitiser.
    THE MUTATION     _audit/_scratch/_control_guard_is_name_only.py replants
                     all seven arms against the live source.

**IT CAUGHT A SEVENTH CLAIMANT ON ITS FIRST RUN.** The enrolment list was
written with six entries; twenty minutes later, before the test was committed,
another agent added `scripts/_probe_search_render_timeline.py` carrying its own
`_redact`, which inherited the guard's trust the moment it was typed. It holds
all four needles and was enrolled. The drift this guards against happened
during the writing of the guard.

**AND THE DRIFT WAS ALREADY THERE.** `test_a_sanitiser_entry_is_a_claim_about_a_contract`
justifies its `_redact` entry with "`_redact` has its own both-directions test
file". Six functions claimed a guarded name; exactly one had that file. True of
one, false of five.

### 3.2 `THE-SINK-IS-THE-PROCESS-BOUNDARY-NOT-THE-PRINT`

`_SINK_NAMES = frozenset({"print"})` models ONE way out. Counted over all 52
scanned files, with the sanitiser set both honoured and emptied:

    P       print + logging (the shipped model)            8 / 17
    +W      a local closure wrapping print (an `emit`)      1 /  2
    +R      return <tainted>, any function                 58 / 58
    +Rtool  return <tainted> from an @mcp.tool()           18 / 18
    +F      file write                                      0 /  0
    +X      raise Error(<tainted>)                         10 / 10

**COUNT BEFORE WIDENING.** 58 was never the right number: a `return` inside an
internal helper hands a value to more of the same process, where a return from
an `@mcp.tool()` hands it OUT to a caller this package does not control. THE
RULED BOUNDARY IS THE TOOL -- +Rtool (18) plus +X (10), because a refusal
message crosses the same boundary a return does, and this package's refusal
doctrine (a refusal must name what it saw) is exactly what puts urls into
exception text.

    THE INSTRUMENT   _audit/_scratch/_control_sink_model_blast_radius.py
    THE COLUMN       the SECOND column is the number that matters: 10 sites
    THAT MATTERS     across 5 files are held green ONLY by a sanitiser trusted
                     by name. Fixing the sink model RAISES the stakes on 3.1
                     rather than lowering them.

**A RAW COUNT IS NOT A DEFECT COUNT.** Of the 18, triage gave 7 REACHES, 10
SANITISED, 1 FALSE POSITIVE -- the checker taints by NAME across a subtree, so
a dict called `out` that once touched a url stays tainted forever.

### 3.3 `DECLARE-THE-ANSWER-NOT-THE-CURRENT-STATE`

`source_url` was shaped in six places, raw in seven, relayed verbatim in one.
Nothing decided which; a new site inherited whichever neighbour it sat beside.

**THE FIX WAS NOT TO WRAP THE SEVEN.** Wrapping a deliberate publication is as
much a defect as leaking an accidental one: it breaks a tool's contract
silently, and afterwards nobody can tell a reasoned shaper from a reflexive
one. `linkedin_my_profile` is the worked example and its own source comment
already said so -- shaping `source_url` there "DOES NOT MAKE THIS PAYLOAD
SLUG-FREE AND MUST NOT BE READ THAT WAY", because three fields above it publish
his identity on purpose.

    THE INSTRUMENT   tests/test_the_source_url_split_was_never_ruled.py
                     Per site: PUBLISHES, SHAPED, UNMEASURED or PASSTHROUGH,
                     each with its reason and its count.
    BOTH DIRECTIONS  a shaper REMOVED from a SHAPED site fails; a shaper ADDED
                     to an UNMEASURED one fails too. The second is the half
                     nobody guards, and it is what stops the reflexive wrap.
    THE CONTROL      four, on synthetic source: removal caught, addition
                     caught, all three spellings of the field read (keyword
                     argument, dict literal, subscript assignment), and
                     `shape.envelope` asserted NOT to be a shaper.

**MOST RAW SITES ARE `UNMEASURED`, NOT "FINE".** The tempting argument is that
they land on resource paths and so carry no identity. That is the argument that
produced the third slug leak: "paths are safe" was never the rule, "these paths
are safe" was. A constant start is not a measured finish. **Close a row by
MEASURING the surface, never by reasoning about what the path ought to be.**

**`shape.envelope` IS NEUTRAL** -- it writes `source_url` into its result
verbatim, so it neither shapes nor leaks and the verdict belongs entirely to
its caller. Treating it as a shaper would mark four call sites safe on the
strength of the function they call. Declared PASSTHROUGH and pinned, because a
shaper added INSIDE it would silently double-shape all four
`linkedin_connections` sites from one edit nobody would think of as touching
those tools.

### 3.4 `A-DENOMINATOR-IS-SITES-OR-OCCURRENCES-AND-THEY-DIFFER`

Two readers counted `source_url` and got 13 and 19. Neither was wrong: 19 is
every line the string appears on, six of which are comments ABOUT the field,
and 13 is the places it is WRITTEN. Nothing was contradicted -- a denominator
had gone unstated. **Say which you counted.**

An earlier grep here also used `grep -v "^.*#"` intending to drop comment
lines. It drops any line containing a `#` ANYWHERE. A filter that silently
shrinks a count is worse than no filter. Parse, do not line-filter.

### 3.5 `A-LINE-NUMBER-IS-NOT-AN-ANCHOR-IN-A-LIVE-TREE`

One citation in this session was given as `server.py:4232`, re-checked by a
second reader as `4201`, then by a third as `4322` -- three numbers, one site,
inside an hour, because other agents were writing the file between reads. The
function name `linkedin_compose_fields` was correct at every reading.

**CITE BY ANCHOR: the enclosing function name plus the quoted source line.** In
a tree with concurrent writers a line number is a reading carrying a timestamp
its reader cannot see, and it is the one part of a citation guaranteed to rot.

### 2.5 `A-REDACTION-THAT-ERASES-ITS-OWN-MARKER`

**A redaction that erases its own marker is more dangerous than no redaction,
because it buys the reader's trust.**

`shape._CENSUS_ENTITY_HREFS` had TWO members -- `/in/<member>` and
`/company/<company>` -- while the profile Interests tab enumerates FIVE entity
kinds. Groups, newsletters and schools shipped their names VERBATIM at
`count == 2`, and a newsletter shipped its slug -- routinely its author's name
-- in the `href_shape` field of every record at ANY count. On surfaces the
census ALREADY reads. `census_redact_rare` could not see it: it returns the
shape unchanged for `count != 1`, in its first line, deliberately.

**THE NEAR-MISS IS THE ENTRY, NOT THE LEAK.** The first fix added the path
substitutions and the markers and NOT the placeholders. `_CENSUS_SAFE_CHARS`
admits no angle brackets, so every new shape failed the gate and became
`<opaque>`. That reads as a redaction and is strictly worse than the leak it
replaced: `<opaque>` carries no marker, so `census_href_identifies_entity`
returns False and the NAME BESIDE IT SHIPS. Nothing raises, no count moves, and
the output looks more careful than before.

    THE INSTRUMENT  scripts/_probe_interests_entity_shaping.py -- one
                    adversarial table, five entity kinds, run at count 1 AND
                    count 2, over BOTH leak paths (`shape` and `href_shape`)
    THE RED         run against the PRE-FIX shaper: 3 name leaks, 1 href leak
    THE GREEN       run against the repository's own shaper: 0 and 0
    THE CONTROLS    both must behave in BOTH runs --
                      MUST-REDACT   a person behind /in/<slug>. If this
                                    survives the guard is broken and every
                                    other row is uninterpretable.
                      MUST-SURVIVE  the furniture label `Show more`, with no
                                    href. If this is redacted the shaper is
                                    blanking its own vocabulary, and a table
                                    of redactions proves nothing.
    HOW IT RUNS     it takes a CANDIDATE PACKAGE ROOT as argv[1], so the pair
                    is taken against the same table with only the shaper
                    differing, without editing a file another wave holds. It
                    REFUSES a root with no `linkedin_server/shape.py` rather
                    than falling back to the repository's own and reporting a
                    pass for a file it never loaded -- caught when a typo'd
                    path produced a confident GREEN.

**THE STANDING RULE: a GREEN alone would have passed the broken fix.** Every
needle was gone from the field being checked. Only running the same table
against the pre-fix code, and requiring the leak count to MOVE with both
controls behaving in both runs, distinguishes "the hole is closed" from "the
hole moved to the field I stopped looking at".

### 2.6 `BOTH-BRANCHES-OF-A-TWO-BRANCH-MESSAGE`

**A message that can only ever say one of two things is printing a constant,
not reporting a fact.**

`readonly.assert_read_url` checks forbidden substrings BEFORE the allowlist and
raises on the first hit, so its refusal named a substring and stopped. Readers
took the substring for the wall. It is usually not the wall -- the allowlist is
closed by default, and every address measured on 2026-09-04 that tripped a
forbidden substring ALSO had no pattern admitting it.

**IT MISLED THREE READERS**, which is what promoted it from a wording nit to a
defect: the blockers ledger's section 2 filed `/invite` and `/follow` as the
blocker for rows they do not gate; a measurement wave reported the same two the
next morning as "the defect"; and the team lead relayed that upward as an
instruction to narrow the guards. All three read a refusal telling them half of
what it knew.

    THE FIX        the refusal now also says whether any allowlist pattern
                   would have matched. No refusal is removed; the raise is
                   unconditional either way and only the sentence differs.
    THE INSTRUMENT tests/test_refusal_names_both_gates.py
    THE CONTROL    BOTH branches are exercised. The second needs an address a
                   pattern ADMITS and a substring still REFUSES -- which the
                   shipped boundary deliberately has none of, since the
                   exemption tables exist to remove them -- so it is
                   CONSTRUCTED by emptying those tables for one test, the
                   technique tests/test_readonly.py already uses to reach its
                   own hard branch.
    AND THE FACT   each branch asserts its claim INDEPENDENTLY against
                   `_ALLOWED_URL_PATTERNS`, so the test pins a measurement
                   rather than a string.

**A WORDING CONSTRAINT PINNED BESIDE THE CODE THAT COULD BREAK IT.** Two tests
in `tests/test_readonly.py` tell the two gates apart BY THE MESSAGE -- the
forbidden sentence must contain "not a read surface" and must NOT contain the
allowlist's own sentence. A later edit phrasing the new clause with the
allowlist's words would pass its own test and silently break theirs from
another file, so the prohibition is asserted in the new file too.

### 3.6 `A-REWRITE-THAT-REPLACES-A-FUNCTION-LEAVES-ITS-PROSE-BEHIND`

`_redact` was replaced by `_shape_of` in one commit. Two blocks of prose about
`_redact` survived it -- a module docstring paragraph and a constant's comment
-- and between them made three claims that were no longer true:

    ":func:`_redact` below carries that name"    no such function
    "a pair prints its value verbatim if ..."    no value prints at all
    "NOTHING OUTSIDE THIS FILE VERIFIES IT"      something now does

**THE THIRD IS THE ONE WORTH THE ENTRY.** That sentence was an HONEST
DISCLOSURE when it was written. The hour it stopped being true it became a
false claim that UNDERSTATED the file's safety and POINTED AWAY FROM THE
INSTRUMENT THAT FIXED IT. An auditor reading top-down meets "nothing verifies
this" and stops -- so the fix existed and was unreachable from where the reader
stood. That is the corrector and the corrected drifting apart inside a single
file, and a stale honest disclosure is more dangerous than a stale boast
because nobody re-reads a sentence that flatters nothing.

**THIS IS THE SHAPE OF THE EDIT, NOT CARELESSNESS.** Replacing a function
changes code the compiler checks and prose nothing checks. Expect the residue
by default and schedule a pass for it; a glance will not find it, because the
stale paragraph reads as fluent and self-consistent -- it was true once.

    THE SWEEP        after any function replacement, grep the file's prose for
                     the vocabulary of the OLD design -- here: raw, verbatim,
                     printed, survived, allowlist, redact -- and check each
                     hit against what the code now does.
    THE CHEAP CHECK  resolve every `:func:` cross-reference against a `def`
                     that exists. Four in that file, all resolved after the
                     pass; one had been dangling.
    THE DISTINCTION  a HISTORICAL mention of the old name in double backticks
                     is correct and worth keeping -- it says what was replaced
                     and why. A `:func:` CROSS-REFERENCE to it is a broken
                     pointer. Same string, different claim.

**AND A DANGLING REFERENCE IS SOMETIMES A COLLISION, NOT A TYPO.** The first
dangling `:func:` in that file pointed at `_key_kept`, a channel another agent
was writing when a third-party edit landed on top of it. It was left standing
deliberately rather than deleted, because deleting it would have hidden the
collision from the person who held the body. **Do not tidy away a broken
reference until you know whether it is residue or a receipt.**


---

## 4. THE UPLOAD WAVE, 2026-09-04

Four entries. The first three are patterns; the fourth is a defect class the
grant model could not see.

### 4.1 `A-SKIP-IS-NOT-A-RED`

**A suite green because three tests never ran certifies nothing, and the report
looks identical either way.**

`tests/test_uploads.py` guards a path against symbolic links -- a symlink is a
path that names one file and reads another, which is the one shape every other
check in that module is blind to: the name sits inside the declared root and
the bytes do not. Three tests plant a real symlink and assert the refusal.

MEASURED on the development box: Windows refuses symlink creation without
Developer Mode or elevation, `WinError 1314: A required privilege is not held
by the client`. All three SKIPPED. The link guard -- the most important one in
the file -- sat entirely unexercised while the run reported green, and would
have gone on doing so on every developer box with the same privileges.

    THE FIX      drive the branch DIRECTLY as well: monkeypatch
                 `Path.is_symlink` to answer True for exactly ONE component of
                 an otherwise ordinary file, and assert the refusal. Done for
                 the leaf, for a parent, and shown NOT firing above the root.
    THE CONTROL  each of those tests lifts the patch and re-runs the identical
                 call, which must resolve. Without that half, a guard that
                 refused everything would pass all three.

**THE STANDING RULE: a platform-conditional skip is a HOLE in the suite until
the property is also reached by a route that cannot skip.** Skipping loudly is
correct -- swallowing the OSError would be worse -- but a loud skip is a
request for a second route, not a discharge of the obligation. Count the skips
in any run you are about to call green, and ask what each one was carrying.

### 4.2 `TWO-GUARDS-ARE-NOT-REDUNDANT-UNTIL-ONE-IS-SHOWN-BLIND`

**A docstring claiming "belt and braces" is a claim about two mechanisms that
nobody has separated. Separate them, or delete one.**

`linkedin_server/uploads.py` refuses a path two ways: a per-component symlink
scan over the whole chain, and a containment check comparing the REAL path
against the REAL root. The docstring asserted the second was not redundant
because a Windows directory junction is not reported as a link. That was an
argument, not a measurement.

MEASURED 2026-09-04 on this box, and every clause of it matters:

    mklink /J <inside-root> <outside>   succeeds with NO elevation
    Path.is_symlink() on the junction   False
    os.path.realpath follows it         straight out of the root

So a junction planted inside the declared root passes a per-component link scan
cleanly and serves bytes from anywhere on the disk. The link check provably
cannot see it; containment provably catches it. Neither is redundant, and that
is now `test_a_windows_junction_out_of_the_root_is_caught_by_containment`.

    THE CONTROL  the test ASSERTS ITS OWN PREMISE first --
                 `assert junction.is_symlink() is False` -- so that if a future
                 Python starts reporting junctions as links, the test goes red
                 instead of quietly passing while testing the OTHER guard and
                 leaving the gap it documents unmeasured.

**THE STANDING RULE: when two checks are said to cover each other, find the
input that exactly one of them catches and pin it.** If no such input exists,
one of the checks is decoration. If it does, the test that pins it must assert
the premise that makes it that input.

### 4.3 `A-SHARED-PAGE-CARRIES-THE-LAST-SUBJECTS-POLICY`

**A survey reused one browser page across thirty captures and reported nine of
them as unrenderable. All thirty render.**

The file-input survey rendered every committed capture and measured it. Nine
came back `RENDER FAILED`, all of them late in alphabetical order -- which is
the tell, because a property of a CAPTURE does not correlate with its position
in a list. Rendered individually every one of the nine succeeded.

The discarded exception said it exactly:

    Page.set_content: TypeError: Failed to execute 'write' on 'Document':
    This document requires 'TrustedHTML' assignment.

One earlier capture carries a Trusted Types Content-Security-Policy. Once
loaded, that policy governs the PAGE, so every later `set_content` on the same
page throws -- and the failures are attributed to the innocent captures that
happened to come after it.

    THE FIX      a fresh `browser.new_page()` per subject, closed after.
    THE MISTAKE  the handler recorded `type(exc).__name__` and DROPPED the
                 message. "Error" is what a nine-capture hole looked like for
                 two runs; the message named the cause on the first.

**TWO STANDING RULES.** A subject may leave state on the harness -- a CSP, a
service worker, an init script, a cookie -- so **reuse the harness only where
you can show the subject cannot alter it**, and prefer a fresh one. And **an
exception handler in a measurement instrument records the MESSAGE**: a survey
that reports its own failures as a bare class name cannot distinguish a broken
subject from a broken harness, which is the distinction the survey exists to
make.

### 4.4 `A-TOKEN-BINDS-A-PATH-AND-A-PATH-IS-NOT-A-FILE`

**The two-call grant model proves the caller confirmed the same TARGET. Where
the target names something outside the process, that is strictly weaker than it
reads, and the gap is invisible.**

`writes.consume` refuses any token whose canonical target does not match the
one it was minted for. For every write this package had before 2026-09-04 that
was the whole story: the target WAS the content -- a post's words, a setting's
value -- so binding the string bound the act.

An upload's target is a PATH. The path is stable and the token matches and the
preview showed him a file, and in between -- `GRANT_TTL_SECONDS`, long enough
for a person to read a block and decide -- whatever sits at that path can be
replaced, edited, or finish being written. Every check in the chain passes and
different bytes leave the machine.

    THE FIX      `uploads.digest_of` -- a sha256 prefix read when the preview
                 is rendered, PRINTED in the block beside the size and the
                 extension, and re-read immediately before the browser is
                 handed the file. A mismatch is a refusal, naming both
                 readings so the person reading it can check.
    THE CONTROLS three mutations, each shown RED against a driven
                 `preview -> consume -> perform` on headless Chromium:
                 the comparison removed, the missing-digest check removed
                 (it must fail CLOSED), and the queue never populated.
                 Plus the positive control: an untouched file gets PAST the
                 gate and fails elsewhere, which is what proves the gate was
                 passed rather than skipped.

**THE STANDING RULE, and it generalises well past uploads: when a consent token
binds a NAME for something the process does not own, bind its CONTENT too.** A
path, a url, a row id, a file handle -- each is a reference whose referent can
change under a live grant. Ask of any new target kind: is the thing he approved
the thing the string names, or only where it lives? If the latter, the token is
one indirection short and something has to close it.

### 4.5 `BUILT-BUT-INERT` -- and this repo already had the guard

**`tests/test_reader_reachability.py::test_every_reader_is_reachable_from_the_tool_surface`.
Cite it. It is the check, and it is older than the argument.**

A reader added to `dom.py` that nothing calls -- directly or transitively from
`server.py` -- fails immediately, with:

    read_file_inputs is defined in dom.py and NOTHING calls it, directly or
    transitively, from outside dom.py. It cannot be exercised by any tool, so
    its tests certify a thing no caller can reach.

**IT FIRED ON `read_file_inputs` THE MOMENT THE FUNCTION EXISTED, before any
of its tests were written.** The wave that added it had just spent two
messages arguing the same objection in prose -- that a capability built and
left unreachable is not built -- and had not known a test already enforced it.
The fix was not to weaken the check: the reader was wired into
`linkedin_surface_census`, which is where it belonged and where it now makes
the file-input measurement one call wide.

**THE STANDING RULE: a reader is not finished when it works, but when a tool
can reach it.** Prose arguing that built-but-inert is a defect is weaker than
the check that says so on the same day. Before writing tests for a new reader,
run this file -- it costs a second and it fires before the tests it would
otherwise certify.

**AND THE GENERAL FORM, which is what earns this an entry rather than a note:
when you are about to argue a standard in review, look for the test first.**
It is faster, it does not depend on the reviewer being present, and where it
exists it has already decided.

### 4.6 `A-REDACTION-APPLIED-AT-ONE-SITE-AND-NOT-AT-ITS-TWIN`

**One tool payload blanked a member's name in one block and printed it in the
block beside it, because the two blocks took different paths to the same
records.**

`linkedin_surface_census` reports `control_shapes` (aggregated) and, from
2026-09-04, `file_inputs` (per-control). Both start from
`dom.read_surface_census`. Only the first went through
`shape.census_aggregate`, and the singleton redaction lives inside it:

    control_shapes   'Message Ada Lovelace'  ->  <redacted>
    file_inputs      'Message Ada Lovelace'  ->  'Message Ada Lovelace'

**THE TRAP IS THE NAME OF THE FUNCTION THAT LOOKS LIKE IT COVERS THIS.**
`census_shape` sounds like the redactor and is not -- it is a character and
length gate that returns anything short and plain VERBATIM, correctly, because
opaquing `Send` would cost the census its use. What catches a member name is
`census_href_identifies_entity` (any control linking to a person) and
`census_redact_rare` (a capitalised run in a shape seen exactly once). The new
block inherited the gate and missed both.

    THE FIX      call `shape.census_redact_rare(shape, 1)` on each emitted
                 record -- CALL it, never re-derive the rule, or the copy
                 drifts (see 1.3)
    THE CONTROL  two halves, and the second is the one that matters:
                 'Message Ada Lovelace' must become <redacted>, AND
                 'Attach a file for your draft conversation' must SURVIVE.
                 A fix that redacted every file-input name would pass the
                 first assertion and destroy the reader's only purpose.
    RED-PROOF    the redaction line replaced with `pass`, run AGAINST A COPY
                 with `dom.__file__` confirmed resolving under the copy first:
                 control PASS, mutant RED, restored PASS, live tree untouched.

**THE STANDING RULE: when you add a second way out of a data structure, list
every transform the FIRST way applies and show your path applying each one.**
Not "it goes through the shaper too" -- name them and check them off. A new
emission path inherits the transforms it happens to call and silently drops
every one it routes around, and the payload will contain both answers side by
side for anyone who looks.

**AND THE DOCUMENTATION HALF, because the code fix alone leaves the trap
armed for the next caller.** The fact now sits where a payload reader meets
it: `dom.read_surface_census`'s docstring names the two functions and says in
so many words that a caller emitting its records WITHOUT aggregating them must
apply `census_redact_rare` itself, and `linkedin_surface_census`'s docstring
says the same to a tool consumer. The sentence that had to go was
"the raw strings are discarded inside it" -- true of the unshaped value,
and read by everyone as redaction.

### 2.7 `A-CENSUS-ANSWERS-WHAT-BUILDS-A-URL-NOT-WHAT-OPENS-ONE`

**A construction site and a navigation site are different questions, and only
one of them is the boundary's.**

A read allowlist governs what the process may OPEN. So "does anything build
this url?" is the wrong question by one step -- it is answerable, it is
cheaper, and it is not the one the decision rests on. A url can be built and
never opened (an output field handed to a human), and a url can be opened
without being built anywhere visible (picked from a table, or a landed
redirect).

**BOTH TIMES THIS WAS ASKED ON 2026-09-04, THE TWO QUESTIONS GAVE DIFFERENT
ANSWERS, AND THE SECOND IS THE ONE THAT MATTERED:**

| narrowing | the census said | the navigation site said |
|---|---|---|
| `/in/<not-me>/details/` | 2 interpolated sites BUILD such urls | `linkedin_my_profile` navigates from `PROFILE_DETAIL_URLS`, a table of `/in/me/` literals -- **zero open it** |
| `/in/<not-me>/` | 5 interpolated sites BUILD such urls | every `goto` carrying `/in/` is `/in/me/` -- **zero open it** |

In both cases a ruling taken on the census alone would have been RIGHT BY
ACCIDENT: the builders were all output fields, and the navigation had already
been moved onto literal tables by an earlier wave. The reason was not
sufficient for the conclusion, and nobody would have known.

    THE INSTRUMENT   scripts/_probe_details_url_breadth.py, parsed not
                     grepped -- the allowlist entry it is about is a two-line
                     implicit string concatenation, and a grep over it
                     returned only the first line and misled a reviewer the
                     same day
    THE SECOND PASS  read the NAVIGATION site by hand: which table does the
                     tool pick from, and does `goto` re-check the landed url?
                     (It does not -- it asserts the REQUESTED url before
                     navigating, which is what lets `/in/me/` survive a
                     narrowing that removes the slug form it redirects to.)
    THE CONTROL      the census reports the total literals examined and how
                     many mention the marker, so a zero is legible: "0 hits
                     across 10854 literals in 55 files" is a finding, "0 hits"
                     alone is a broken parse

**AND A THIRD QUESTION HIDES BEHIND THE SECOND: what does the process assert,
the requested url or the landed one?** A narrowing is safe for a redirecting
address only if the answer is "the requested one". That was checked at both
assert sites (`browser.goto`, `writes._load`) rather than assumed, and it is
the difference between removing a dead pattern and breaking every self-profile
read in the package.

**THE STANDING RULE: before narrowing a boundary, ask all three -- what BUILDS
it, what OPENS it, and WHICH url the door is shown.** The first is a grep-like
question, the second needs a reader, and the third is a property of the door.

#### 2.7a The door's blindness is a LIABILITY in one place and LOAD-BEARING in another

`assert_read_url` sees the REQUESTED url and never the landed one. That single
property has opposite signs in two places in the same file, and a reader who
"fixes" it in one will break the other.

**LOAD-BEARING, here.** `/in/me/` redirects to his vanity slug -- the exact
shape the removed pattern was the only thing admitting. The narrowing is safe
ONLY because the door never sees where the navigation ended up.

**A LIABILITY, on `/messaging/`.** LinkedIn redirects `/messaging/` into one
conversation thread of its own choosing, measured twice. `readonly.py` records
what that forced, in its own words:

> leaving "/messaging/thread" forbidden while permitting "/messaging/" would
> have produced **a guard that forbids a destination it knowingly delivers you
> to -- a fiction, and a worse one than an honest permission, because the next
> reader would trust it.**

So BOTH forms had to go on the list. The blindness is why an honest boundary
there costs two entries instead of one.

**AND THE FILE ALREADY NAMES THE TRAP,** which is the part worth carrying: the
messaging entry says listing only the root would mean the server "routinely
sitting on a url its own allowlist does not cover -- **true today because the
landed url is not re-checked, and a trap the moment anybody adds that
check.**"

**THE STANDING RULE: adding a landed-url check is not a hardening, it is a
THIRD decision.** It would make `/messaging/` honest and would simultaneously
break every self-profile read, because `/in/me/` no longer has a pattern for
what it lands on. Anyone proposing it must re-answer the boundary for every
redirecting address at once -- and this register entry exists so they find that
out before writing the check rather than after.

### 4.7 `AIM-BY-THE-PROPERTY-NOT-BY-THE-LABEL`

**"The only file input in this dialog" is a PROPERTY. "The input labelled
`Resume`" is a GUESS. They look equally concrete in a report and only one of
them survives contact with the page.**

A survey of every committed capture found exactly one file input, in
`tests/fixtures/apply_modal_derived.html`, and read its accessible name as
`'Resume'`. Handing that string upward would have looked like a measurement.
It is not one: the fixture is DERIVED, its own header separates what was
measured from what was invented, and the name came from a
`<label for="resume">Resume</label>` the fixture author wrote so the file would
"answer to the recorded counts".

What IS measured about that modal is the COUNT -- 1 file input, page-level,
2026-08-24. So the two halves of the same record have different standing:

    the count       MEASURED   -> "the only file input in this dialog" holds
    the label       INVENTED   -> "the input named Resume" asserts a shape
                                  nobody has seen

**AND THE PROPERTY IS THE CHEAPER AIM ANYWAY**, which is what makes this a
pattern rather than a caution. A count of exactly one addresses the control
with no string at all, so it cannot be wrong about a name, cannot rot when
LinkedIn relabels the control, and needs no in-page comparison. The measured
half was the more useful half.

**THE CONTRAST CASE, from the same wave, so the rule does not read as "never
trust a name".** The post composer, read live on 2026-09-04, draws an
`Add media` button whose name came off LinkedIn itself and survives the census
shaping intact. That name is evidence. The difference is not the string; it is
where it was read.

**THE STANDING RULE: before aiming at a value, ask which half of the record
was measured.** A capture, a fixture and a docstring all present measured and
invented fields in the same typeface, and a derived fixture is BUILT to be
consistent with the counts -- so it will hand you a plausible value for
anything you ask it. Prefer the relation ("exactly one", "the only one named
as asked", "the one whose href matches") over the literal, and where you must
use a literal, cite where it was read.

**IT IS THE SAME MOVE AS EMITTING THE RELATION RATHER THAN THE VALUE**, which
this package already does for disclosure -- `_typeahead_gate` compares a needle
INSIDE the page and returns integers, and `census_aggregate` reports shapes and
counts instead of names. 4.7 is that discipline applied to AIMING instead of to
what is emitted, and the two reinforce: a server that will not emit a name is
a server that had better not need one to find a control.

---

### 4.8 `A-CARD-THAT-NAMES-TWO-PARTIES-NEEDS-A-POSITION-NOT-A-MENTION`

**Where:** `linkedin_server/shape.py`
`company_id_from_insight_cards`; `tests/test_company_id_resolver.py`.

**The guard:** the employer's numeric Page id is read off the canned
people-search link in a posting's Premium insights panel, and it is accepted
only if the card carrying it NAMES the employer the posting already
identified.

**Shown failing, on real markup, on the first run.** The name check was
written first as a MENTION -- "is the employer's name in this card's text".
LinkedIn's own sentence is

    <Employer> hired 6 people from <Other>. See all

and its href carries BOTH organisations, `currentCompany=<employer>` and
`pastCompany=<other>`. So "does this card mention X" is TRUE FOR BOTH, and the
resolver asked about `<Other>` returned `<Employer>`'s id -- with a `why`
string stating, correctly by its own lights, that the card named the company
asked about. Against the tracked fixture, not a constructed case.

**The mutation that kills it:** revert `startswith` to `in`:

    -    if not _WS.sub(" ", text).strip().casefold().startswith(wanted.casefold()):
    +    if wanted.casefold() not in _WS.sub(" ", text).casefold():

`test_the_other_company_named_on_the_same_card_resolves_to_nothing` reds.
Three further mutations were planted and all four were killed by their named
test, zero survivors, run in an isolated copy with
`linkedin_server.__file__` printed and asserted under it:
`_audit/_scratch/_mutate_company_id_resolver.py`, output beside it.

**THE LESSON, WHICH IS NOT ABOUT COMPANIES.** When one string names two
parties, a MENTION cannot attribute and a POSITION can. The fix is not a
cleverer matcher; it is noticing that the SOURCE already encodes the
attribution -- LinkedIn made the employer the subject of its sentence -- and
anchoring on that rather than on containment. Ask of any name check: *could
this text name somebody else too?* If yes, containment is measuring the wrong
thing, and it will be confidently wrong rather than silent.

**Its companion, and the reason both are here.** A related failure has the
same shape one level up: `dom.harvest_linked_cards` defaults to EIGHT
ancestor hops, and at eight this card's text becomes the whole insights panel
-- every organisation named anywhere on it. A containment check over that text
would pass for almost any name on the page. Measured at five depths and pinned
at three (`shape.COMPANY_ID_CARD_HOPS`), with the reading written on the
constant. This is `a-budget-is-not-a-containment-rule` again: a cap on how far
a walk climbs is not a rule about what it is allowed to absorb.

### 4.9 `A-GUARD-THAT-NEEDS-ADJACENCY-IS-DEFEATED-BY-INTERPOLATION`

**Where:** `tests/test_no_committed_identity.py`, `COMPANY_ID_SHAPE` --
`(?:/company/|currentCompany=|companyId=)(\d{3,})`.

**Shown failing.** A new test module was written with its urls built the
obvious way::

    HREF = f"...?currentCompany={EMPLOYER_ID}&pastCompany=26105338"

The identity guard swept the file -- it sweeps tracked PLUS
untracked-not-ignored, so the file was genuinely in scope -- and passed. It
passed because it found NOTHING TO CHECK: its pattern needs the parameter name
and the digits ADJACENT IN THE SOURCE TEXT, and the f-string had put an
expression between them. **A green that means "no match" is indistinguishable
from a green that means "declared and verified", and this file's whole job is
to tell those apart.**

**The control that proves it now speaks.** Append a comment carrying the
parameter name and six digits with nothing between them -- the literal is NOT
written out here, for a reason two paragraphs down -- and re-run: the guard
reds on
`test_no_tracked_file_carries_a_real_identifier[tests/test_company_id_resolver.py]`
with `assert 1 <= 0`. Before the url was spelled out as a literal, planting a
bare `31415926` and a bare `9876543210` in the same file changed NOTHING --
which is the measurement that found this, and it is worth repeating that the
plant that finds a blind spot is the one that looks like the real thing rather
than the one that looks alarming.

**AND THIS ENTRY WENT RED ON ITSELF, WHICH IS THE BEST EVIDENCE IN IT.** The
first draft quoted the control verbatim. `_audit/INSTRUMENTS.md` is a tracked
file, the guard sweeps it like any other, and the quoted control is a real
match with an undeclared value -- so the paragraph explaining the check FAILED
the check, inside the same test run that was meant to certify it. Nothing was
wrong with the guard; the documentation was a live instance of what it hunts.
Declaring the throwaway in `SYNTHETIC_IDS` would have "fixed" it by making the
register a place where identifiers get waved through, so the literal is
described instead. **A register of failing-proofs has to be sweepable on the
same terms as the code it describes.**

**The fix is in the TEST, not the guard, and deliberately.** The url is now a
literal and the id is parsed back out of it (`EMPLOYER_ID = parse_qs(...)`),
with `test_the_pinned_href_is_the_fixtures_own` holding the literal to the
tracked capture so it cannot go stale. Widening `COMPANY_ID_SHAPE` to chase
interpolations would make it match `currentCompany={` and start reporting
variable names as identifiers.

**WHAT WAS NOT DONE, stated so nobody reads this entry as closed.** A census of
the same shape found EIGHT tracked sites putting a value next to `/company/`
through a variable. Six interpolate a SLUG, which this digits-only pattern
would never match anyway and which are therefore not instances. **Two are
numeric ids and are real instances:**

    tests/test_unfollow_fixture.py:250   f"/company/{ANCHOR_ID}/"    ANCHOR_ID = "902611"
    tests/test_writes.py:4157            "/company/" + FOLLOWED_COMPANY + "/"

Neither is a live red -- both values are declared in `SYNTHETIC_IDS` and both
appear adjacent to `/company/` inside a tracked fixture, so the guard checks
them THERE. But it does not check them at these sites, and it cannot tell you
which of the two situations you are in.

**One value in the same neighbourhood is invented and undeclared and nothing
can see it:** `tests/test_writes.py:83` `UNFOLLOWED_COMPANY = "7777777"`. Seven
sevens is self-evidently constructed, so this is not an incident -- it is a
demonstration that the guard's coverage is decided by ADJACENCY rather than by
what a file contains.

The general check that would catch the class: **for each declared synthetic id,
assert the guard actually MATCHES it somewhere.** A declaration nothing matches
is either a stale entry or a blind spot, and both are worth knowing. Its
mirror, harder and more valuable: **for each id-shaped literal in a tracked
file, assert some pattern binds it.**

---

## 6. The search-appearances reader, and the two rules that are not one rule

Added 2026-09-05 by the search-appearances wave. **APPENDED, not inserted** --
see this file's preamble; find these by NAME.

The instrument is `dom.read_search_appearances` plus its pure helper
`dom._search_appearance_labels`, both in `linkedin_server/dom.py`, over
`tests/fixtures/search_appearances_synthetic.html`. The selectors live in
`tests/test_search_appearances.py`.

**THE HONEST LIMIT GOES FIRST, because it changes what these entries certify.**
The fixture is SYNTHETIC. Nobody in this repository has opened a
search-appearances page. These eight proofs establish that the reader REFUSES
what is put in front of it; they establish NOTHING about whether it reads the
real surface. A refusal proven over an invented page is in the same family as
an instrument that returns zero because it cannot see the thing -- if it is
ever quoted as evidence about the live page, that is the defect, and this
paragraph is where a reader is told so.

Eight mutations were planted, one at a time, in a scratch copy of
`linkedin_server`, `tests` and `pytest.ini`, with a guard asserting
`linkedin_server.__file__` resolved under the copy before every pytest run --
ten runs, zero WRONG TREE. Each was restored by re-copying that one file from
the live tree, and the live `dom.py` and `readonly.py` were diffed
byte-identical against the restored copies at the end. Baseline and final
control both 24 passed.

The run's own `RESULTS.md` was written to a session scratch directory outside
this repository and **is not durable** -- its path is deliberately not quoted
here, because `test_no_committed_identity` refuses a user path in a tracked
file and it is right to: an absolute path under a home directory carries the
account name. The table below is the record. If it disagrees with anything,
re-plant the mutations rather than hunting for that file.

| # | mutation | selector that died | what came back |
|---|---|---|---|
| M1 | `SEARCH_APPEARANCES_LABELLED_PAIRS = 2` -> `40` | `test_no_third_party_string_reaches_the_output` | RED -- leaked `Rivermouth` |
| M2 | the entity gate -> `if False:` | `test_an_entity_linked_label_is_refused_whatever_it_says` | RED -- got `['Hillcrest']` |
| M3 | `census_redact_rare(value, counts[value])` -> `value` | `test_a_singleton_two_capital_word_label_is_redacted` | RED -- got `['Northgate Analytics']` |
| M4 | `!= "no"` -> `== "yes"` | `test_an_unwalked_row_is_treated_as_linked_and_not_as_unlinked` | RED -- got `['Hillcrest']` |
| M5 | `const PERSON = /\/in\//` -> `/\/nobodyhere\//` | `test_the_person_anchor_count_is_non_zero_on_a_page_with_a_member` | RED -- `0 >= 1` |
| M6 | `SEARCH_APPEARANCES_LABELLED_PAIRS = 2` -> `0` | `test_the_headline_and_delta_are_readable` | RED -- headline went blank |
| M7 | delete the allowlist pattern | `test_the_address_this_reader_names_is_the_one_the_boundary_admits` | RED -- `is_read_url` False |
| M8 | that pattern -> `/analytics/[a-z-]+/?$` | `test_the_neighbours_of_that_address_are_still_refused` | RED -- 1 of 7, on `/analytics/creator/` |

### 6.1 What M1 and M3 prove that neither proves alone

`Rivermouth` is why the fixture has a keyword panel at all. It is ONE
capitalised word, seen ONCE, in a row carrying no anchor -- so
`census_redact_rare` cannot touch it (its own docstring puts the run length at
two) and `census_href_identifies_entity`'s sibling rule has no link to key on.
**Neither redaction rule can reach it.** Only the in-page withholding does.

Before that row existed, every breakdown row in the fixture was inside a
company link, so killing ONE guard still left the other holding and the
mutation came back green. **A fixture on which two guards overlap on every row
cannot show either of them failing** -- it certifies the pair and says nothing
about the members, which is the confidence-at-scale this register exists to
prevent. The row was added for that reason and is documented in the fixture's
own header.

### 6.2 M4 and the extra check: two states of one field, kept apart

M4 was run with a SECOND selector,
`test_an_entity_linked_label_is_refused_whatever_it_says`, which **stayed
GREEN**. That is the point of the pair. `entity_linked` has three values, and
`unwalked` means the ancestor walk ran out of hops rather than reaching the
page root having found nothing.

* M2 (`if False:`) breaks the `yes` case; the `unwalked` selector also dies.
* M4 (`== "yes"`) leaves `yes` correct and breaks `unwalked` alone.

Two mutations, two different deaths, one green cross-check. Without it, two
tests that both go red under every mutation are one test with two names. **A
budget on how far a search goes is not a rule about where it may stop**, and
this is the check that keeps the difference real rather than commented.

### 6.3 M6 is the control-for-the-control, and it is the one worth copying

Every other entry here proves a guard can REFUSE. M6 proves the suite notices
when the reader goes BLANK: the labelled-pair budget is set to zero, the
reader emits no labels at all, and every redaction test in the module still
passes -- because a reader that says nothing leaks nothing.

`test_the_headline_and_delta_are_readable` is the only thing standing between
that state and a green suite, and under M6 it went RED. **A privacy test suite
with no positive-reading control is satisfied by an instrument that has
stopped working**, which is this project's most expensive recurring defect
wearing its most flattering costume. Any future reader shaped by subtraction
needs one of these.

### 6.4 M8, and why the near-miss list is parametrised

`/analytics/[a-z-]+/?$` is the widening a future reader is most likely to
write -- it looks like tidying and it admits `/analytics/creator/` and every
other page in that tree. It failed exactly ONE of seven parametrised
neighbours while the other six still refused, which is what tells a real
narrowing from a test that would have gone red at anything.

The seventh case is `/search/results/people/?keywords=x`, and it is in that
list on purpose rather than for symmetry: this whole reading exists to inform
a ruling on people search, and the gate in
`_audit/2026-08-30-linkedin-nine.md` forbids one load of the page under
consideration being the evidence that authorises it. The test asserts the
surface stayed shut.

### 6.5 The attribution probe, which is an instrument and shipped with a control

`_audit/_scratch/_probe_which_refreeze_carries_my_line.py` answers "does this
frozen digest cover this line" by removing the line from the source text IN
MEMORY -- `readonly.py` is never written, so a concurrent writer cannot be
clobbered -- and recomputing. It found that the 2026-09-05 re-freeze
`9d21c894b13316f7 -> 6f82ef147356ce5d` covers THREE allowlist additions while
its written entry names two.

**Its control is the entry condition:** removing a substring that appears
nowhere drops zero lines and moves no digest. Without that line, "the digest
changed" would be a fact about the removal machinery rather than about the
line, and three matching moves would prove nothing. Declared DISPOSABLE as a
one-off; the method -- *delete-and-recompute to ask what a digest covers, with
an absent-needle control* -- is the part worth keeping.

## 7. The groups/events wave, 2026-09-05

Added by the groups-events wave. **APPENDED, not inserted** -- see this file's
preamble; find these by NAME.

Two instruments, both shown failing before they were believed. The transcripts
are `_audit/_scratch/_redproof-corpus-sweep.txt` and
`_audit/_scratch/_redproof-membership-row.txt`. Both runs asserted
`linkedin_server.__file__` under the scratch copy AND the repo path absent
before any mutation was planted, and both finished on a clean control run.

### 7.1 `scripts/_probe_membership_signal_in_corpus.py` -- a NEGATIVE reading with two controls

Sweeps every HTML document this repository holds for six group and event route
needles. Its answer -- ZERO across 30 documents and 2522736 characters -- is
what established that no offline route to the groups/events precondition
exists, and it is worth having only because of the controls.

**THE MUST-FIRE CONTROL IS `/company/`, and it is not decoration.** It has to
be non-zero somewhere, because `linkedin_followed_companies` ships and reads
exactly that data and `manage_pages_following.html` is a tracked capture of the
surface it reads. A sweep reporting zero groups AND zero companies has measured
its own blindness. The second control runs the other way: a needle nobody has
ever written must find nothing, or the matcher is wrong rather than the corpus
rich.

| # | mutation | what came back |
|---|---|---|
| M1 | the must-fire control's regex -> a string that cannot match | RED -- MUST FIRE 0, FAIL, exit 1, and the verdict says the target counts are not a reading about memberships |
| M2 | `CORPUS_DIRS` -> a directory that does not exist | RED -- "NO DOCUMENTS FOUND", exit 1 |
| M3 | the must-stay-silent control's regex -> `a` | RED -- 30583 hits, FAIL, exit 1 |
| M4 | ONE synthetic file added to the corpus carrying a group href | GREEN AND DIFFERENT -- groups-href 1, groups-path 1, both controls still PASS, verdict switches to the "an offline route MAY exist" branch |
| -- | final clean control run | groups/events 0, company-href non-zero, needle 0, both controls PASS |

**M4 IS THE ONE THAT MAKES THE ZERO READABLE.** M1 to M3 prove the instrument
can DIE. Only M4 proves it can SEE -- that a real group signal in the corpus
would change the answer. A sweep proven only to fail is still consistent with
one that never finds anything, and "zero from an instrument that cannot see the
thing" is the class this register exists to keep out.

**A CORROBORATION THAT WAS NOT PLANNED.** The proof ran in a copy of
`linkedin_server`, `tests`, `scripts` and `pytest.ini` -- and NOT `_audit`. Its
control read 82 where the live tree reads 90. The difference is exactly the 8
company anchors in the one raw `_audit` capture that survives on disk, so two
independently-derived numbers reconcile to the document. The gap was a fact
about the copy's scope, and it is recorded because a number that differs
between two runs is normally the first sign of a stale reading.

### 7.2 `shape.membership_row` -- and the mutation that UNDER-KILLED

The per-record emission gate for a groups reader, over
`tests/test_membership_row.py`. It exists because a per-record path inherits
NEITHER census protection: `census_shape` is a length-and-charset gate, and
`census_redact_rare` needs a COUNT so it lives inside aggregation.

| # | mutation | what came back |
|---|---|---|
| M1 | delete the `if foreign:` branch | RED -- 5 failed |
| M2 | delete the name substitution check | RED -- 5 failed |
| M3 | gate on `census_href_identifies_entity` instead of on which entity kind | RED -- 14 failed |
| M4 | hard-code the foreign set to 2 of the 4 markers | RED -- 3 failed, exactly the newsletter and school rows plus the derivation test |
| -- | final clean control run | 24 passed |

**M1 UNDER-KILLED ONE NAMED TEST, AND THAT IS THE ENTRY WORTH READING.**
`test_a_refusal_returns_no_fragment_of_what_it_refused` was expected to die
with the branch and did not. Diagnosis, taken by reading the test rather than
by adjusting the mutation: its input was a plain `/in/` href, which with the
foreign branch deleted STILL refuses -- it falls through to the group-marker
check. **So the test passed against a guard with its first branch removed. It
was asserting the refusal SHAPE and nothing at all about the branch it appeared
to protect.**

The remedy is the input, not the assertion. It now uses a url where the foreign
branch is the ONLY thing refusing -- a group url carrying a member path in its
query -- with the old input kept as a second case, because the two prove
different refusal paths. Verified sensitive afterwards: with the branch
neutralised, that input publishes a name verbatim.

**THE GENERAL FORM, which is the part to carry away.** A mutation that fails to
kill a test is not a weaker result than one that kills it -- it is a DIFFERENT
result, and it is about the TEST. The instinct is to conclude the mutation was
too small. Here the mutation was exactly right and the test's INPUT was chosen
from its author's model of the risk rather than from the branch structure. That
is the third time this project has caught a probe set that agreed with its
author.

### 7.3 M3 is a control for a failure mode, not just a mutation

`census_href_identifies_entity` returns True for a group href -- the marker was
added to that tuple on 2026-09-04 -- so a reader gated on the shared predicate
refuses EVERY membership row and returns an empty list. **That empty list is
indistinguishable from "he belongs to no groups"**, which is the exact question
the whole wave exists to answer.

M3 is therefore not testing a typo. It is testing that the suite can tell a
correct empty answer from a blind one, and its blast radius says it can: 14 of
24 tests died, including two of the suite's own mutation-proofs, because they
depend on a group row publishing as their precondition. A suite where that
mutation killed only one or two tests would be a suite that could ship the
blind zero.

### 7.4 A design decision a test forced, recorded because the test is the reason

`membership_row` first published `census_substitute(href)` as its `href_shape`.
`test_the_consumers_of_this_predicate_are_the_ones_that_were_considered` went
red on the new caller, and the entry it already carries is fatal to that
design: **a bare member token in a query survives those substitutions**, since
`/in/` is the only member shape they know. So
`/groups/<id>/?invitedBy=<token>` would have shaped to
`/groups/<group>/?invitedBy=<that same token>` and published it.

The fix is the closed-vocabulary conclusion `linkedin_connections` reached
after two filters that each looked right: the href DECIDES and is never
EMITTED; what is published is a module literal. An arbitrary string that never
crosses cannot carry an identifier.

**THE INSTRUMENT HERE IS THE ENUMERATION TEST, and this is its fifth catch.**
It is not a boundary and it publishes nothing; its whole function is to make a
new caller be CONSIDERED rather than inherited. On this occasion the
consideration changed the code. `tests/test_membership_row.py` now rebuilds the
leaky first version from the shared predicate and asserts it still leaks, so if
that predicate ever learns the bare-token shape the decision is revisited
deliberately instead of outliving its reason.

## 8. The groups/events precondition wave, 2026-09-05 (second entry)

**APPENDED, not inserted.** Three instruments from the run that answered the
precondition. Section 7 above holds the two written before the browser freed;
these are the three the live read produced, and each is here for a different
reason.

### 8.1 A FAILED CHEAP ROUTE, KEPT RATHER THAN DELETED

`read_surface_census` returns a CONTAINER per control. If a member's own groups
and LinkedIn's suggestions sat in different containers, the split would fall out
with no name ever crossing -- the cheapest possible answer, and the first thing
to try.

**MEASURED: it does not.** 10 of 10 group-marked controls and 54 of 54
event-marked controls report `container: none`, one distinct container each.

**THIS IS AN INSTRUMENT AND NOT A NOTE.** It is in
`scripts/_probe_groups_events_capture.py`, it runs on every invocation, and it
prints the container tally whether or not it separates anything. A negative that
saves the next person the same hour is worth its lines, and a negative kept only
in prose is one somebody re-derives.

Its control is the dark-mode surface at 20 controls, read in the same session.
A container tally from a page that had not arrived would be a fact about the
run.

**AND IT REFUSES TO RUN IN LAUNCH MODE.** `LINKEDIN_CDP_ATTACH=1` is asserted
before any session is opened, because a launch-mode session would open a second
Chrome on the operator's real profile. The refusal was SHOWN FIRING before the
real run rather than assumed to work.

### 8.2 THE RELATIVE-HREF DEFECT, AND WHY IT IS THE THIRD OF ITS KIND THIS WEEK

`scripts/_probe_membership_sections.py` first matched anchors with an ABSOLUTE
pattern -- `linkedin\.com/groups/...`. On the real captures that found **5 of
the 10 group links and ZERO of the 54 event links**, because both pages write
RELATIVE hrefs.

**THAT EXACT HAZARD IS DOCUMENTED IN THIS PACKAGE, AT ITS OWN SITE.**
`census_href_identifies_entity` explains in its body why it uses CONTAINMENT
rather than `startswith`, and names the measurement behind it: LinkedIn writes
member links both ways on one page, so an anchored check caught the relative
form and let the absolute one through.

**Reading that comment did not prevent the same mistake on two more surfaces.**
What caught it was the control. This is the third instance this week of
documentation losing to a control -- the others being the `<opaque>`
half-applied-fix note, which failed to prevent the same error on two consecutive
days, and the `--stat` warning in the push-freeze file.

**THE ENTRY IS THEREFORE NOT "USE CONTAINMENT".** It is: a hazard that has
already been measured once and written down at its own site will still arrive in
the next instrument, so the next instrument needs a CONTROL rather than a
reader who has read the comment.

### 8.3 THE CROSS-INSTRUMENT CONTROL, WHICH IS THE PATTERN TO COPY

`_probe_membership_sections.py` parses HTML with regex. `read_surface_census`
walks the live DOM. **Two different instruments over one page**, so their
anchor totals must agree:

    groups   parsed 10, census measured 10   AGREE
    events   parsed 54, census measured 54   AGREE

On the first run they did not agree -- 5 against 10, and 0 against 54 -- and the
probe printed **THE TALLIES ABOVE ARE VOID** and returned 1, rather than
printing a plausible section split that happened to be built from half the data.

**THAT IS THE PART WORTH COPYING.** A 5-of-10 result is not obviously wrong: it
would have produced a clean-looking table with two sections and a sensible
story. The only thing standing between that table and this register was a number
taken by a different instrument in the same session.

**THE SECOND CONTROL RUNS THE OTHER WAY** -- an `<h9>` heading pattern that
cannot match anything must find nothing, or the matcher is over-broad rather
than the page rich. Both directions, both on every run.

**AND ITS REDACTIONS ARE FED A REAL COUNT.** Headings and control labels pass
`census_shape` and then `census_redact_rare` with the number of times that
string occurs in the document -- not a guess, not 1. That is the shipped rule
applied where it is correct, on a path that emits per record, which is the gap
`shape.membership_row` exists to close elsewhere. It is visible working in the
output: one events heading came back `<redacted>` and every group name in the
control labels did.

### 8.4 WHAT THE THREE OF THEM ANSWERED

Two independent signals agreeing: five distinct group identifiers under a
non-suggestion heading, disjoint from five under a suggestion heading, each
carrying a per-row management control the suggestion rows lack -- measured at
two window sizes with the same split.

Recorded in full, with what is MEASURED separated from what is READ, in
`_audit/2026-09-05-groups-events-precondition.md`.

## 9. The newsletter-surface wave, 2026-09-05

Added by the newsletter-surface wave. **APPENDED, not inserted** -- see this
file's preamble; find these by NAME.

Three instruments. The RED/GREEN transcript for the two guards is
`_audit/_scratch/_redproof-newsletter-guards.txt`: four guards, each shown
GREEN and then shown RED under a planted mutation, in memory, with nothing on
disk written.

### 9.1 `scripts/_probe_newsletter_routes.py` -- the route table for a blocker whose surfaces are all dead

Twelve candidate addresses through `readonly.assert_read_url`, with three
must-allow and four must-refuse controls, one of the four refused by a
SUBSTRING rather than by a missing pattern. **The substring control is the one
that earns its place**: without it a gate that refuses everything and a gate
that refuses this family in particular produce the same clean table.

**WHAT IT FOUND THAT THE CENSUS COULD NOT.** Two of the thirteen newsletter
rows resolve to the SAME address as two others, which is how `M C80` was found
to duplicate `N 55` + `N 56` and `P L4` to duplicate `M C83`. Neither slice
flags either pair. **A route table is a duplicate detector; a capability census
is not, because two rows written from two help articles look different until
you ask where each one goes.**

**AND IT FOUND A ROW COSTED AGAINST AN ADDRESS IT MAY NOT USE.**
`/article/new/` is ALLOWED at HEAD and `/article/new/?isNewsletter=true` is
refused FOR THE QUERY STRING ALONE. So `M C50` "create a newsletter" may need
no boundary change at all. That is reported as a hypothesis with the read that
settles it, not as a move -- the same discipline the fourteen-row route audit
used.

**CORRECTED BY:** `_audit/2026-09-05-the-newsletter-create-route.md` -- the hypothesis above, that `M C50` may need no boundary change because `/article/new/` is already allowed, is refuted by a third address the live page draws.

The live newsletters
page draws `/article/newsletter/new/`, which
`readonly.is_read_url` refuses. The measurement in that paragraph stands and
only its inference falls, which is why this is a back-pointer rather than a
rewrite. The prescribed settling read -- re-censusing `/article/new/` with its
menus pressed -- is also superseded: it costs a composer load that may autosave
a draft, and the page answered the question from the outside for nothing.

**THE STANDING TRAP IT PRINTS IN ITS OWN OUTPUT: ALLOWED IS NOT SERVED.**
`/in/me/details/interests/` is on the allowlist, was admitted for this
blocker's precondition, and REDIRECTS. A route table that did not say so would
be read as a list of pages.

### 9.2 `linkedin_server.shape.subscription_row` -- the gate that must NOT reuse its sibling's rule

`tests/test_subscription_row.py`, 11 tests, three of them planted mutations.

**THE MUTATION THAT MATTERS IS NOT A DELETION.** It is
`membership_row`'s own rule -- publish the name as written when the identity
substitutions leave it unchanged -- applied here. That rule is correct for a
group and unsafe for a newsletter, and the difference is MEASURED::

    census_substitute("Weekly Notes by Savita Krishnan")
        -> "Weekly Notes by Savita Krishnan"     UNCHANGED

A person's name carries no urn, no `/in/` path, no possessive and no six-digit
run, so nothing in that check can see one -- while a newsletter's title and
slug routinely ARE one. A reader generalising the group gate would write
exactly this mutation and it would look like a gate doing its job.

**EACH MUTATION'S INPUT WAS CHOSEN FROM THE BRANCH STRUCTURE, NOT FROM THE
MODEL OF THE RISK**, which is this project's 2026-09-05 law one level down:

* the foreign-marker branch is NOT testable with a bare `/in/<member>/` href --
  with the branch deleted that input falls through to the newsletter-marker
  check and is refused THERE, same verdict, different reason, mutation
  survives. What needs the branch is
  `/in/<member>/recent-activity/newsletters/<newsletter>/`, a MEMBER'S OWN
  newsletter tab, which carries both markers at once;
* the constant-href rule is NOT testable with a plain newsletter href -- it
  shapes to the constant and the mutation is byte-identical. What needs it is
  `?authorProfile=<a bare member token>`, which survives the substitutions
  because `/in/` is the only member shape they know.

**AND THE FINDING IS BIGGER THAN THE GUARD. The same hole is in the group
gate**: a group named after a person passes `membership_row`'s name check for
the identical reason. The base rate is lower; the mechanism is the same. Owner
by artifact -- `shape.membership_row`, `tests/test_membership_row.py` -- is the
groups-events wave, so it is reported rather than fixed here.

**THE LIMIT IS ASSERTED IN THE SUITE RATHER THAN CONFESSED IN A DOCSTRING.**
`census_redact_rare` is a CAPITALISED-RUN rule, not a name detector:
`notes by alex` survives it.
`test_the_redactor_is_a_caps_run_rule_and_NOT_a_name_detector` pins that, and
tells a future reader to re-measure and rewrite rather than delete if the floor
ever rises. This package has no instrument that can decide whether a string is
a person's name, and that is a finding, not a TODO.

### 9.3 `_audit/_scratch/_probe_newsletter_refreeze_attribution.py` -- a stronger attribution than "it moved"

The variant of the search-appearances removal control that handles the
MULTI-LINE `re.compile` construct: the sibling probe filters on the call and
the needle appearing on ONE line, and dropping only the pattern line would
leave a bare `re.compile()` behind -- a different edit, not a removal. This one
walks out to the enclosing construct and ASSERTS the shape before deleting
anything, so a layout change cannot make it silently delete the wrong lines.

**IT PRODUCED THE STRONGEST FORM OF THIS EVIDENCE THIS PROJECT HAS RECORDED:**

    pinned, and live on disk                     a8ea5dcf4f8b3d52
    without the newsletters root                 6f82ef147356ce5d   COVERED
    without the Pages sibling                    052961dfb7a8ed83   COVERED
    CONTROL: without a needle no line carries    a8ea5dcf4f8b3d52   0 lines

The tree MINUS this wave's line hashes to EXACTLY THE PREVIOUSLY PINNED VALUE.
"A digest that moves when a line is removed covers that line" proves the line
is in there; this proves it is the ONLY allowlist change in the tree, so no
neighbour's uncommitted work is riding inside the re-pin. **In a tree several
waves are writing, that is the difference between an attribution and a
coincidence.**

### 9.4 A claim NOT made, recorded because the omission is the instrument

Every earlier re-freeze in `tests/test_readonly_boundary_invariant.py` verifies
its digest under Python 3.13 AND 3.10 before writing it down. **This box has no
3.10** -- measured, not assumed: the four sibling venvs under `mcp-servers/`
are all 3.13.14 and there is no `py` launcher. The 3.10 reading exists and is
CI's (`ubuntu-latest` x 3.10 is a matrix cell), so the entry says ONE
interpreter and names where the second lives.

Writing "verified under both" would have cost nothing, matched every
neighbouring entry, and been false. A register whose entries are shown failing
is worth nothing if its prose is not held to the same bar.

---

## 10. The LOAD A probe, and the failure it was caught in

Added 2026-09-05 by the search-appearances wave. **APPENDED, not inserted.**

`scripts/_probe_search_appearances_live.py` -- two loads of his own
search-appearances page through `dom.read_search_appearances`, attach mode, no
profile lock. Record: `_audit/2026-09-05-search-appearances-load-a.md`.

**DECLARED DISPOSABLE AS A PROBE.** It answered one question once and the
answer is written down. What is NOT disposable is the shape of its defect.

### 10.1 A verdict function is an instrument, and this one failed on live data

Its `verdict()` printed, on reading 5 member links: *"the record does not
merely count, it NAMES. The emission is identifying."*

`anchors.person` counts `/in/` hrefs inside `main`. Five is a true count of
member links. It does not establish what they point at -- the searchers, a
"people also viewed" rail, and **his own nav link** all produce that number.
An integer answering *"are there member links here"* was read as answering
*"does the record name the searchers"*.

**IT WAS NOT CAUGHT BY A MUTATION. It was caught by reading the output against
the question.** Every guard in section 6 was red-proofed; this function was
not, because it emits prose rather than a value an assertion could pin. That
is the gap worth carrying forward: **the reading half of a probe gets the same
scrutiny as the measuring half, and it is the half no mutation test reaches.**

The pattern that would have prevented it, and it is already this repository's
own: a count is not the property. `linkedin_send_message`'s own documentation
says *"A COUNT IS NOT THE PROPERTY"* about committed recipients. The same
sentence was true here one surface over and nobody carried it across.

### 10.2 The two-readings rule earned its keep

Both loads returned identical values in every field -- 108, 13, 5, 0, 18,
2005 chars. That is what makes them a measurement rather than a sample, and it
answered a second question for free: **the badge question the census key's own
comment leaves open.** Nothing observable was spent between the loads.

Had the two disagreed, the probe says so and claims nothing -- the branch
exists and is the reason the numbers above can be quoted.

### 10.3 What the reader's conservative branch cost, measured

Both metric labels returned `<redacted>` because `entity_linked` came back
`unwalked`: the six-hop ancestor walk did not reach a page root, and anything
but a flat `no` costs the label. The numbers are proven and their captions are
not.

**This is the failure the constant's docstring predicted in advance** -- *"a
visible miss, which is the failure to have"* -- and it fired on the first live
run. Recorded because the obvious repair is wrong: raising the hop budget
makes the walk reach `main`, which contains every link on the page, and then
EVERY label is redacted. The fix is a capture of the real DOM shape.

And one thing the live run did NOT exercise: `pairs_withheld` was 0. Only two
numberish pairs exist on that render, so **the primary defence -- withholding
the label in the page -- was never exercised against live markup** and remains
proven only against the synthetic fixture.

### 9.5 The enumeration guard caught this wave too, and it changed the code

Added after 9.2 rather than folded into it, because the entry above was written
before the catch and rewriting it would erase the sequence.

`tests/test_urn_substitution_covers_the_class.py::test_the_consumers_of_this
_predicate_are_the_ones_that_were_considered` went RED on
`shape.subscription_row`. **Second catch in two days, and the second time the
consideration it forces changed the function** rather than being written down
and waved through.

**WHAT IT FOUND.** `subscription_row` called `census_substitute` twice and the
second call was a PUBLISHER -- the first caller in this package to emit that
predicate's raw output from a per-record path. The href call was already safe:
it decides only, and the emitted href is a module literal, for the reason the
same file records -- a bare member token in a query survives these
substitutions, measured on this very shape,
`/newsletters/<slug>/?authorProfile=<token>` shaping to
`/newsletters/<newsletter>/?authorProfile=<that same token>`.

**THE FIX** is `census_shape`: the same substitutions PLUS the length and
charset gate, so an uncertifiable title comes back `<opaque>` -- a refusal that
keeps its marker -- instead of being emitted. Measured identical on every
title the module's tests carry and different exactly where it should be. Both
uses are now REFUSAL TESTS, so a widening of the urn pattern cannot move what
the function publishes: structural rather than argued.

**AND THE PART WORTH KEEPING IS WHY A TARGETED RUN COULD NOT HAVE FOUND IT.**
This wave ran `test_shape.py`'s neighbours and `test_membership_row.py` -- which
NAMES this guard in its own docstring -- and still missed it, because the guard
lives in a third file and fires on *somebody added a caller*.

> **A guard that fires on a NEW CALLER cannot be found by running the tests of
> the thing you added.** It is not in your file, not in your feature's file,
> and not reachable from either by reading. Only the full suite reaches it.

So a targeted set is a sound check for what a change BREAKS and an unsound one
for what a change JOINS. Anything adding a caller to a shared predicate,
registering a tool, or extending an enumerated family owes the suite a full
run before it commits -- or it is relying on the next wave's run to find it.

### 9.6 A shared-tree suite run over-reported the red count by 150 percent

The push-freeze file already requires the gate to be a
`git clone --no-hardlinks` rather than a worktree. **What was not on the record
is the size of the error, and it is bigger than "a bit noisy".** Measured today,
three runs of the same suite:

    SHARED TREE, HEAD moving under the run   10 failed, 4040 passed  29:37
    CLEAN CLONE at that HEAD                  4 failed, 4043 passed  25:33
    CLEAN CLONE one commit later, targeted    3 failed,  261 passed

**SIX OF THE TEN DID NOT EXIST.** Four waves committed during the 30-minute run;
pytest imports from the WORKING TREE, and the working tree moved. The six named
real files with real-sounding assertions -- a publish-post audience guard, a
server-surface registration, three staleness tests, an emission-point
declaration -- and every one of them passed when its file was run directly.

**THE COST IS NOT THE NOISE, IT IS THE ROUTING.** A wave clearing that queue
would have sent six owners to look at nothing, and the push-freeze file's own
rule -- sort a red queue by WHAT THE ASSERTION IS ABOUT before clearing it --
does not help here, because the assertions are about exactly what they say. The
only thing that separates a phantom from a red is WHERE the suite ran.

**THE TELL, so it can be caught without a 25-minute clone:** a failure that
passes when its file is run alone, in a tree with live writers, is a phantom
until a clone says otherwise. Run the file directly FIRST -- it costs seconds --
and only clone for the ones that survive that.

**AND THE COROLLARY FOR REPORTING:** a shared-tree run's count is not a gate
reading and must never be relayed as one. State the tree, not the SHA; and if
the tree had writers, state that too, because the number is about them as much
as about the code.

### 9.7 The same hole, and NOT the same remedy -- groups-events measured it

Appended because 9.2 above is a STANDING INSTRUCTION and is one inference away
from being wrong. It reports that `membership_row` has the same defect as the
newsletter case -- true, confirmed by its owner -- and a reader will infer that
the newsletter fix transfers. **It does not, and the counter-measurement is
theirs rather than mine:**

    "Node.js Developers"     -> <redacted>
    "Node Developers India"  -> <redacted>
    "Savita Krishnan"        -> <redacted>

Every plausible GROUP name is a run of two or more capitalised words, so
unconditional `census_redact_rare` blanks the payload along with the leak and
the reader degenerates into a count. A newsletter TITLE keeps a readable shape
through the identical rule -- `<redacted> by <redacted>` still says the thing is
authored -- which is why redact-always is right for `subscription_row` and wrong
for `membership_row`.

**SO THE SHARED FINDING IS THE MECHANISM, NOT THE FIX.** They declared the
limit instead: the docstring records it with the measurement, one test publishes
the person-named group and asserts it ships (a known defect recorded so that
FIXING it turns a test red rather than passing in silence), and a second
measures the unconditional redaction blanking three real group names so the
trade gets revisited if it changes. Nothing consumes `membership_row` yet, so
the hole is real and not live, and both halves are in one sentence. What would
close it is a name-free reader, which is a ruling and is on the lead's desk.

**THE GENERAL FORM, which is why this is in the register and not only in a
commit:** two functions can share a defect and not share a remedy, because a
remedy is judged against what the payload is FOR. Handing a peer your fix along
with your finding invites them to adopt a trade they never measured. Hand over
the measurement and let them take their own -- and when they decline it, that is
a result, not a disagreement.

**AND ONE ROOT CAUSE OF THEIRS WORTH STEALING.** Three of the four
`test_navigation_is_never_derived` findings against their files had a SINGLE
cause: `_relation` had locals named `before` and `after`, and that guard tracks
tainted names ACROSS A MODULE rather than per scope, so those names were tainted
everywhere in the file -- including three prints that tally shaped control names
and touch no url. Renaming cleared all three. Assigning to a variable does not
help, because the fixed point follows the binding; the sanctioned route is
`_SANITISERS`. Before editing a print that guard flags, check whether the taint
came from a NAME COLLISION somewhere else in the file.

### 9.8 The guard flagged the right line for the wrong value, and that decided the remedy

`test_navigation_is_never_derived` went red on `scripts/mcp_probe.py`, two
sites. 9.7 above invited the reader to check for a NAME COLLISION first, so
that was checked first, and the answer was no: the cause there was locals
tainted module-wide by an assignment elsewhere, and the cause here is the
hard-coded `_TAINTED_ATTRS = {"url"}` firing on an Attribute literally spelled
`.url`. **Same guard, same red, different cause -- the remedy did not carry
over, which is 9.7's own point applied back to it.**

MEASURED: exactly two `.url` sites exist in that file, both `options.url`, and
they are the whole root cause. Simulating the rename alone takes the tainted-name
set from ten names to zero and both violations to none; the second site was
tainted only transitively through `result = probe(options.url, ...)`.

**WHY IT WAS NOT DECLARED, and this is the transferable part.** A
`KNOWN_TAINTED_OUTPUT` entry is keyed on the WHOLE SINK EXPRESSION. Declaring
`print(json.dumps(result, indent=2))` tolerates that line forever, whatever
`result` later holds -- and `result` holds `call_result`, the verbatim payload
of any tool `--call` names. `mcp_probe.py --call linkedin_my_profile` would have
put the operator's profile into whatever transcript ran it, which is the channel
all three 2026-09-03 slug leaks used.

So the guard was RIGHT ABOUT THE LINE AND WRONG ABOUT THE VALUE, and a
declaration would have permanently blessed the real risk while arguing about the
false one. `options.url` is an argparse Namespace holding a caller-typed address;
that file's imports are exactly `argparse, json, os, sys, time, urllib` and no
browser exists in it.

The fix was therefore three things and only the first is about the guard:
a `_PRINTABLE_IN_FULL` allowlist so a payload prints in full only for tools
measured to carry no identity (one entry) and everything else reports keys and
TYPE names; `dest="endpoint"` so the attribute stops claiming to be a browser
url while the FLAG stays `--url` and callers are untouched; and
`test_mcp_probe_has_no_browser_surface`, an exact import allowlist that pins the
claim the rename rests on. **The third is what makes the rename not a dodge** --
without it, a browser arriving in that file later goes unseen, because the guard
is now looking for an attribute the file no longer has.

**AND A DECLARATION THAT WOULD HAVE BEEN VACUOUS, caught by measuring it.** The
slug-shaped fixture first fired `test_no_committed_identity`; a `DECLARED_PLANTS`
entry was written, and then the replacement value was measured and found NOT TO
BE COUNTED AT ALL -- `synthetic-not-a-real-person` contains `a-real-person`,
already in that guard's `SYNTHETIC_SLUG_TOKENS`. The entry was withdrawn and the
neighbour's file reverted untouched. **The token is strictly safer than the
declaration: it exempts one VALUE, where a pinned count exempts any one slug in
the file.** Measured both ways -- the file reads clean, and the same file plus
one real-looking slug goes red. Before writing a declaration, measure that the
guard actually counts the thing you are declaring.

**ON WHETHER THE GUARD IS OVER-BROAD: it is, and it should stay that way.**
`_TAINTED_ATTRS` taints any `.url` whatever holds it, and its own comment says
naming the holder objects "would be a list to keep in step". That generalisation
is true of `linkedin_server/`; `scripts/mcp_probe.py` is its first counterexample
and `scripts/` will accumulate more. Narrowing it costs a list that goes stale
silently; the coarseness costs a rename. It found a real leak here BY being
coarse, which settles the trade.

---

## 11. The retire-rulings wave, 2026-09-05

### 11.1 `scripts/_probe_retire_ruling_boundary.py` -- the two gates, reported separately

**WHAT IT IS FOR.** Deciding whether "the boundary refuses this" is EVIDENCE or
merely TRUE. `readonly.assert_read_url` runs the forbidden-substring loop first
and raises on the first hit, so every refusal names a substring and stops. This
probe asks the two questions independently -- does any forbidden substring hit,
and would any allowlist pattern admit it -- and prints a CLASS per address:

    FORBIDDEN xN  N substrings somebody wrote, each with an argument beside it
    NO-PATTERN    the default-closed allowlist, which decided nothing here

**WHY THE CLASS IS THE WHOLE INSTRUMENT.** This repository's own rule is that a
general mechanism which merely happens to block something is a GAP WITH A NAMED
BLOCKER and may not be laundered into a decision. A verdict of REFUSED cannot
tell those apart; the class can. Measured over the twelve DECIDE-RETIRE
capability families: **exactly ONE meets a written substring. Eleven meet
NO-PATTERN.** So eleven retirement rulings had to stand on the capability rather
than on the boundary, and the probe is what made that visible instead of
tempting.

**SHOWN FAILING THREE WAYS** before being leaned on --
`_audit/_scratch/_redproof_retire_boundary.py`, all three killed:

* empty allowlist -> the must-allow controls fail and the run aborts, exit 1;
* the substrings covering the settings family removed -> the class falls from
  FORBIDDEN to NO-PATTERN while the VERDICT stays REFUSED, which is exactly the
  discrimination claimed;
* empty forbidden list -> the classifications go from 8 to 0.

**AND IT PRINTS EVERY HIT, NOT THE FIRST, BECAUSE THE MUTATION THAT SURVIVED
SAID TO.** Mutation 2 originally removed only `/psettings/` and did NOT change
the classification. The instinct is to enlarge the mutation; the rule is to ask
which input makes that entry the only thing standing. **None does** -- the bare
`settings` substring, one of the ten added in the class fix, covers every
`/psettings/` address too, so the settings family is refused TWICE by two
independently written entries and no single-entry narrowing frees it. Reporting
only the first hit is precisely the defect `readonly.py` records having misled
three readers, committed by the probe written to avoid it. **"Covered twice" is
a different fact from "covered once" and a first-hit verdict cannot say it.**

**EVERY ADDRESS IS MARKED CITED OR ASSUMED IN THE OUTPUT.** Where no census row
names a url the probe invents one and says so, because an assumed address proves
what the boundary does with a SHAPE and cannot prove LinkedIn serves the
capability at that shape. The blockers ledger declined to invent an address for
this same family; the marking is how the invention is kept honest rather than
avoided.

### 11.2 A ruling written against a FAMILY survives a wrong row id; one written against ids does not

Not a script -- a technique, and it is the one that made a whole queue rulable.

The blockers ledger assigned all 409 GAP rows to blockers and published only the
COUNTS; the row-to-blocker map was never written down and the classifier is not
on disk. So eleven of twelve row sets had to be reconstructed, and **a wrong row
id retires the wrong capability silently, into the one state nobody re-opens to
check.**

The containment: **write the ruling against the capability FAMILY, and carry the
id list as a marked reconstruction.** Two rulings whose membership was soft were
written to state their outcome under BOTH readings, and the arithmetic was shown
identical either way. A blind second reconstruction -- handed the counts and the
R/W splits and not the answer -- reproduced all twelve sets and named the same
three one-row substitution risks.

**THE DEFLATION IS PART OF THE ENTRY, and the blind reader wrote it: two readers
agreeing rules out idiosyncrasy and NOT a shared misreading, because both read
the same census. And on a one-row blocker an R/W split is a two-bit check**, so
six of the twelve rest on their capability text being unique in the corpus
rather than on arithmetic.

### 11.3 A retirement must name the fact that reopens it, or it is a wall

The standing form this wave used, and it is cheap enough to be mandatory: every
retired row carries a REOPENER concrete enough to check, and each is attributed
to who can establish it -- LinkedIn shipping something, one capture, one probe
run, or the operator. Thirteen rulings produced thirteen reopeners, of which
**three are one capture each and two of those three are the SAME capture**.

The corollary that does the real work: a ruling is scoped to an ACT and states
what it does NOT reach. Retiring "broadcast a Live" must not retire "read a Live
event page"; retiring "boost a post" must not retire "read a post's analytics" --
which in that case is the best value-per-risk read left in its slice. **A
retirement that quietly walls off its neighbours is the failure mode, and the
only defence is writing the neighbour down.**

## 12. The groups-surface wave, 2026-09-05

### 12.1 `scripts/_probe_groups_menu.py` -- opening a menu without reading a name

**WHAT IT IS FOR.** Reading the contents of a per-row overflow menu on a
surface where every row is named after something, and where the name might be a
person's. It presses each disclosure, reads the menu, presses Escape, and
publishes labels that have been through `census_shape` AND `census_redact_rare`
with a REAL tally.

**THE REUSABLE IDEA IS WHY IT OPENS ALL FIVE.** The count rule --
furniture repeats and a name does not -- is the only thing separating a menu
verb from an entity's name, and **one menu has no tally.** Opened across five
rows, a verb LinkedIn draws on every row appears five times and survives; a
label carrying one row's own name is a singleton and is redacted with no
special case. Pressing ONE menu would have produced a payload in which every
capitalised label is redacted, which is the degenerate answer this surface was
already warned about. **If the count rule is your only protection, take the
measurement at the window where a count exists.**

**AIMED STRUCTURALLY BECAUSE THE LABELS COULD NOT DO IT.** The measured per-row
control labels were `More` five times and one label carrying an entity name, so
a name-based aim reaches four rows of five or reaches a name. The rule used
instead: from each button declaring `aria-expanded`, walk up; the FIRST
ancestor holding at least one group anchor is the row, and the control
qualifies only if that ancestor holds EXACTLY ONE. No budget and no depth
limit.

**SHOWN FAILING.** The attach refusal fires with the flag unset (exit 2). The
taint guard was shown firing on a planted `print` of a landed url in a sibling
file and green on this one.

**THREE DEFECTS IT FOUND IN ITSELF, each from its own output:**

* **Run 1 read menu ROLES alone** and reported "nothing drew" while
  `aria-expanded` went true on all five presses. This surface draws NO
  `[role=menu]` content at all. The sibling `_probe_comment_overflow_menu.py`
  learned the exact opposite on its surface -- there the census delta was blind
  and the roles were visible. **WHICH READER IS BLIND IS A PROPERTY OF THE
  SURFACE, NOT OF THE READER**, so neither alone may report an empty menu.
* **Run 2 double-shaped the arrived names.** They come out of
  `read_surface_census` already shaped; shaping them again opaqued three
  distinct labels into one identical string. **A double-shaped string and a
  redacted one are indistinguishable**, so the reader cannot tell "LinkedIn's
  label is unshapeable" from "this probe shaped it twice".
* **Run 3 printed its badge diagnostic only on the failing branch.** The
  comparison that mattered was between two PAGES and needed both sides. **A
  diagnostic available only on failure cannot support a diagnosis that needs
  both readings.**

### 12.2 `linkedin_server/groups.py` -- the absent parameter as a safety property

**WHAT IT IS FOR.** Counting group memberships without ever touching a name.
`shape.membership_row` publishes a name under a stated, tested limit -- a group
named after a person ships that person's name -- and its own docstring says the
fix is a ruling rather than a refactor. This is the ruling: **no name is a
parameter of any function in the module.**

**THE PATTERN WORTH COPYING IS THE TEST, NOT THE CODE.** The safety claim is an
ABSENCE, so it is asserted on `inspect.signature` rather than on behaviour. A
future edit adding a `name` parameter would look reasonable in a diff and
silently reintroduce the class; the signature test is what makes it red.
**A filter has to keep up. An absent parameter does not.**

**TWO STRUCTURAL REFUSALS, both measured rather than tuned:**

* the query and fragment are DROPPED before any check runs, which closes the
  escape `membership_row` measured -- a member token in a query survives the
  census substitutions intact;
* a NON-NUMERIC segment is refused, **because a slug is a name**. Measured over
  a live capture: 10 of 10 group segments are pure digits at lengths 5-8, zero
  non-numeric, zero carrying a query. The rule refuses nothing real.

**A DIGEST WAS CONSIDERED AND REJECTED**, and the reasoning generalises: group
ids run to eight digits, so a digest over that domain is brute-forceable end to
end. **A digest over a small domain is a lookup table wearing a redaction's
costume** -- worse than publishing the value, because it buys the reader's
trust.

**SHOWN FAILING.** Both refusal branches killed by planted mutation, on inputs
where the branch under test is the ONLY thing standing. The obvious inputs
prove neither: a bare member path still refuses with the foreign branch
deleted, because it falls through to "not a group href". The sharp inputs are a
group href whose segment is a person's name, and a group path that also carries
a member segment.

### 12.3 A CONTAINMENT RULE IS NOT SYMMETRIC

**The finding, and it cost a wrong answer that was caught by its own control.**
`_probe_membership_tally_live.py` ran the SAME stopping rule as 12.1 -- the
first ancestor holding exactly one group anchor -- but from the ANCHOR instead
of from the BUTTON. It found ZERO membership rows against FIVE, on the same
page, in the same hour.

> "The first ancestor holding exactly one X" does not name a ROW. It names THE
> SMALLEST ELEMENT CONTAINING WHAT YOU STARTED FROM, and the two coincide only
> when the start point is outside X's own subtree.

From the button you must climb past the button's branch to reach the anchor, so
you land on their common parent. From the anchor you stop at its own tight
wrapper, which contains no control, and every row reads as having none.

This project already knows that **a budget on how FAR a walk goes is not a rule
about where it stops**. This is the other half: **a rule about where it stops
is not complete until it says where it STARTS.**

**AND THE PROBE REFUSED TO PUBLISH THE ZERO**, on the stated grounds that three
instruments disagreeing is the finding and not a count. That refusal is what
surfaced it. A reader that had printed "0 memberships" would have been believed
-- it is a plausible number for an account that might have none.

### 12.4 THE SECOND SPELLING OF THE IDENTIFIER RULE: prose is not exempt

**Measured twice in ten minutes on one file.** The identity guard fired on a
member path written as `/in/` plus a sixteen-character hyphenated run. It was
RENAMED rather than declared -- a declaration permanently widens what the guard
tolerates for that file and a rename widens nothing.

**Then the comment explaining the rename quoted the removed string verbatim,
and the file stayed red at exactly the same count**, with the defect now living
in the explanation. The guard could not tell the difference and was right not
to.

> **A NOTE ABOUT A REMOVED VALUE MUST DESCRIBE ITS SHAPE, NEVER REPRODUCE IT.**

Prose feels exempt from the identifier rule because it is only prose. It is
not. And the ordering is the third instance recorded on this project: reading
the rule beforehand prevented nothing; running the pair caught it in a minute.

**THE PAIR THAT PROVES A RENAME IS NOT VACUOUS**, and it is cheap enough to be
mandatory: red with the value, green after the fix, **red again with a fresh
value of the same class that carries no synthetic token**. Without the third
step a "fix" that exempts nothing looks identical to one that works.

### 12.5 A GUARD FIRING IS AN INVITATION TO LOOK, NOT ONLY TO DECLARE

`groups.py` first shaped the path with `census_substitute`, which made it a new
consumer of that predicate and turned the pinned-consumer guard red -- a consent
guard that exists so a new caller "shows up in a diff instead of in an
INCIDENT". **Declaring was available and looking was better.** The function
already split the path, so an exact SEGMENT match was available and is strictly
tighter than a substring search over a shaped string; and the coupling was
backwards anyway, since `census_substitute` blanks six-digit runs, which is the
exact shape of the identifier being published.

**The guard improved the design rather than being satisfied.** That is the
outcome a consent guard is for, and it is only available to somebody who treats
the red as a question.

### 12.6 PROVISIONAL-UNSMOKED: `scripts/_probe_group_row_affordances.py`

**ADMITTED IN THE UNSMOKED STATE, DELIBERATELY, WITH ITS CONTROL WRITTEN OUT.**
It would settle the four JOIN rows by reading what LinkedIn draws on a
SUGGESTION row -- the rows that have no overflow menu and are therefore
invisible to 12.1. It has never produced a reading: three attach attempts
aborted in the CDP handshake while port 9224 answered `/json/version` normally
and the browser process stayed alive. **Contention, measured rather than
assumed, and nothing was killed or restarted to get around it.**

**THE CONTROL IT MUST PASS ON ITS FIRST REAL RUN IS STATED IN THE FILE so a
successor cannot grade it after the fact: it must resolve exactly FIVE rows
carrying a disclosure**, because it uses a THIRD stopping rule and the other
two both measured five. The file prints AGREE/DISAGREE on that comparison
rather than leaving it to a reader.

The register's law is that an instrument enters only if it has been SHOWN
FAILING. This one has -- its refusal path and its abort path both fire. What it
has not done is produce a number, and the entry says so in its first line
rather than in a footnote.

---

## 13. The newsletter-build wave, 2026-09-05

Appended, not inserted. Two instruments and one law. The law is the part that
travels: the other two are its receipts.

### 13.1 A GUARD'S SCOPE IS NOT ITS NAME, and this one was doing duty it could not do

`tests/test_navigation_is_never_derived.py` is the consent guard this package
reaches for. Four mutations were planted in a live probe:

    print the landed url directly                      RED
    navigate to a url the page chose                   RED
    smuggle the landed url through an f-string         RED
    print a raw accessible name off an anchor          GREEN

**The fourth is the only one of the four that puts a PERSON in a transcript,
and it is the one that passed.** Its taint sources are a `goto` return and a
`.url` attribute -- urls, and nothing else -- so a title read with `inner_text`
is invisible to it.

**That file is not wrong and it says so itself**: *"'This function is safe' was
never true; 'this function is safe for urls' is."* What nobody had written down
is that the uncovered half is the half with the names in it, and that three
waves were relying on the covered half while reading rendered text.

**THE TRANSFERABLE FORM.** A guard named for one leak accrues authority over
the whole class it seems to be about. Nothing in this repository said "the
consent guard" was a url guard -- the name did, quietly, and only a mutation
that a reader expected to fail said it out loud.

### 13.2 `tests/test_page_text_is_never_printed.py` -- the sibling rule

Fourteen tests. Five synthetic RED cases, five GREEN, an inventory pinned per
file, and that inventory demonstrated red three ways -- an entry one too low, one
too high, and absent for a file that has sites.

**IT IS A SEPARATE FILE BECAUSE THE SANITISERS DO NOT TRANSFER.** `_relation`
provably carries no substring of its input -- FOR A URL. Hand it a person's name
and it returns `SERVED, exact`, which discards the question rather than
answering it. Adding page text to the same taint set would credit every entry on
`_SANITISERS` with cleaning text on an argument only ever made about addresses.
**A shared taint set with unshared sanitisers is one rule that is wrong half the
time and says so nowhere.** The engine -- fixed point, sink list, counting and
comparison carve-outs -- is IMPORTED rather than copied, which is that file's own
principle about two implementations drifting.

**THE OBJECTION WAS MET WITH A NUMBER, NOT AN ARGUMENT.** That file declines to
taint response bodies because *"a rule whose true positives arrive buried in
false ones gets declared into uselessness."* The same objection applies to page
text, so it was measured::

    sanitisers as they stand                                    81 sites
    + census_shape, census_redact_rare, census_substitute       79
    + subscription_row, membership_row, invitation_badge        79

**Crediting every shaping function in the package removes 2 of 81.** These sites
are not printing shaped text through a shaper the rule cannot see; they are
printing text that never met a shaper. The feared flood is 2.5 percent, because
the machinery that would have caused it already exists -- `_COUNTING_CALLS`
absorbs `len(text)` and the `Compare` carve-out absorbs `"x" in text`.

**AND ITS SANITISER LIST IS DELIBERATELY EMPTY**, which is a finding rather than
a gap: `census_substitute` returns a plain human name unchanged, `census_shape`
is a length and charset gate that returns a short plain name verbatim, and
`census_redact_rare` is a capitalised-run rule. This package has no instrument
that can decide whether a string is a person's name, and an empty list is where
that finding becomes structural instead of documentary.

### 13.3 A PLANTED RED CASE FOUND A HOLE IN THE ENGINE IT INHERITED

`_tainted_names` walks `Assign` and `AnnAssign` only. So::

    rows = await page.evaluate(JS)
    for row in rows:
        print(row["title"])

taints `rows` and never `row`. **Iteration is a binding and the engine did not
know it.** That is the most natural way to handle page data in this codebase,
and **the same hole exists in the url rule** for a list of landed addresses.

Adding `For`, `AsyncFor`, comprehensions, `with ... as` and the walrus moved the
measurement from **81 sites in 22 files to 111 in 25** -- so **30 sites, 27
percent of the class, were hidden by that one omission.**

**IT WAS FOUND BY A CASE FAILING, NOT BY READING THE ENGINE.** The case was
written because it is the shape a reader takes; the engine disagreed with it. A
green-only run would have passed the version that could not see a third of the
class -- which is the whole argument for showing a rule failing before trusting
its greens.

### 13.4 `linkedin_server.newsletters` -- a reader whose AIMING RULE CAN FAIL

`tests/test_newsletter_reader.py`, 15 tests, in a real headless page so the
selector is actually executed. Five planted mutations, five killed.

**THE COUNT IS `distinct`, NOT `anchors`.** Measured live: ten anchors, five
newsletters -- every row drawn twice, once around an illustration with no text
and once around the title. A reader publishing the anchor count answers **ten**
to the one question the surface was opened to settle, and looks entirely correct
doing it.

**THE AIMING RULE SHIPS WITH ITS OWN REFUTATION, and that is the reusable part.**
The first paragraph is the title because its normalised text is a PREFIX OF THE
SLUG in five rows of five and the second paragraph's is in none -- the slug being
an independent witness, derived by LinkedIn from the title, that names nobody.
**That comparison is not discarded once the measurement is taken.** It ships as a
per-row boolean, so a page that reorders the paragraphs makes the reader SAY SO
instead of publishing a description as a title.

> **A reader whose aiming rule cannot fail is not aimed. It is guessing, and
> reporting the guess as data.**

Its limit is stated rather than guarded against: the rule is a STRICT prefix and
assumes the slug is not truncated, which five titles of 11 to 26 characters
could not have shown either way. Widening it to "either is a prefix of the other"
would absorb that case and make the control much harder to fail, which is the
property it exists for.

### 13.5 A SURVIVING MUTATION SENT ME TO THE FIXTURE, NOT TO THE MUTATION

Of the five planted mutations, "drop the deduplication" first came back GREEN.
The instinct is that the mutation was too small. Measured, it was the fixture:
the illustration anchors are dropped by the paragraph check BEFORE the dedup is
reached, so on the live page the ten-becomes-five collapse is done by that check
alone and **the dedup branch had no reaching input at all.** My own docstring had
credited the dedup with the collapse; the mutation said otherwise.

The fixture now draws an ELEVENTH anchor -- two text anchors on one href -- so
that row is where the dedup is the only thing standing. **A fixture that only
mirrors the page leaves a live branch unexercised**, and a branch no input
reaches is untested however many times the suite runs. That is this project's
2026-09-05 law -- when a mutation survives, ask which input would make that
branch the only thing standing -- arriving on a fixture rather than on a test.

### 13.6 The obligation this surface inherits, and why a zero discharged half of it

`/mynetwork/` is refused on the belief that opening it consumes the pending
invitation badge, so any read under it reads `dom.read_invitation_badge` before
and after. Both loads: 0 to 0, `state=read` at all four ends, no other nav badge
moved, two of six badges non-zero at every end so the reader is proven to resolve
real values.

**THE SIBLING PROBE STOPS ON A ZERO BEFORE, AND IS RIGHT TO. THIS ONE MUST NOT,
AND THE DIFFERENCE IS THE QUESTION.** `_probe_connections_badge_cost.py` asks
what the address COSTS, and a zero cannot decrement, so an "unchanged" would
agree with a story it had no power to refute. This probe asks whether the read
SPENT something it passed, and a zero answers that by absence.

    SAFETY   discharged -- nothing pending was consumed, because nothing was pending
    COST     UNMEASURED, and it stays unmeasured until a day the badge is not zero

Both lines are printed together so neither can be read as the other. **Copying
the sibling's gate unexamined would have refused to take the read at all** --
blocked by a proxy whose zero is the very thing that proves the read harmless.
Same instrument, same reading, opposite verdicts.

### 12.7 `scripts/_probe_group_settings_route.py` -- classify an href without following it

**WHAT IT IS FOR.** Deciding whether a control that is DRAWN on an admitted
page is also a ROUTE this server may take. It reads the control's href and
classifies it against the two gates INDEPENDENTLY -- forbidden substrings, and
the allowlist -- navigating nowhere and printing no address.

**THE REUSABLE SENTENCE:**

> **A CONTROL BEING DRAWN IS NOT A ROUTE.**

Two census rows were filed as "one press away on an address we already open"
because `Update your settings` appears on every membership row. Measured: all
five are `<a>` elements whose href meets **two** forbidden substrings,
`/psettings/` and `settings`. They are DOUBLE-refused and need a denylist
exemption, which is a heavier act than an allowlist addition.

It cost nothing to find out only because an href can be classified without
being followed. **Costing a row off "the control is right there" would have
filed two rows one boundary change from reachable when they are two** -- and
nothing downstream would have contradicted it until somebody tried.

**THE CLASS IS THE INSTRUMENT, NOT THE VERDICT.** Inherited from 11.1 and
worth restating because it generalises past retirement rulings: a verdict of
REFUSED cannot separate "somebody wrote a substring against this" from "the
default-closed allowlist decided nothing", and this repository's rule is that
a general mechanism which merely happens to block something is a GAP WITH A
NAMED BLOCKER rather than a decision.

**AIMED BY A LABEL, AND THE LABEL IS FURNITURE BY MEASUREMENT.** `Update your
settings` tallied 5 across the rows and 10 across the menus, so the same count
rule that redacts a singleton keeps it -- which is what makes it safe to write
into a tracked file and safe to match on. A label appearing once would be a
name.

### 12.8 THE CONTROL EXPERIMENT THAT PROVED A TAB CLOSE, AND WHY A PAIR COULD NOT

**The problem in one line: on a browser a dozen waves share, a before-and-after
pair around your own action measures the FLEET, not your action.**

Three runs of a real probe with the close in place gave `+1, -1, +1`. That is
consistent with a working close and with a broken one, because neighbours open
and close tabs in the same seconds.

What settled it was a MINIMAL script run three times each way, with the close as
the only difference:

    WITHOUT close   deltas [1, 0, 2]   sum +3
    WITH close      deltas [0, 1, -1]  sum  0

**A DIFFERENCE MEASURED AGAINST A CONTROL SURVIVES NOISE THAT A DIFFERENCE
MEASURED AGAINST ZERO CANNOT.** The noise did not go away; it stopped being
confounded with the effect. Reach for this shape whenever the thing you are
measuring shares its instrument with other actors -- which on this project is
the browser, the git index, and the test tree.

**THE UNDERLYING DEFECT, root-caused and NOT fixed centrally on purpose:** in
attach mode `BROWSER._page()` calls `ctx.new_page()` and caches it, and
`session()`'s `finally` only touches an idle timer, so **the tab outlives the
process.** 42 scripts call `session()`; 5 closed their page. The fix went in
the PROBES and not in `browser.py`, and the reason is LIFETIME rather than
code: the MCP server reuses that cached page across tool calls on purpose, so a
per-session close there churns tabs for a different caller. **The same line of
code is correct in one caller and wrong in another, which is why it is not a
drive-by.**

Close the PAGE, never the CONTEXT -- the context is the operator's signed-in
session.

### 12.9 A CONSTANT SIZED FOR ONE SESSION IS A FLEET-WIDE OUTAGE WAITING

`cdp_bridge.ATTACH_TIMEOUT_MS` was a hardcoded 15s, chosen when the browser
belonged to one session. Shared by a dozen waves that each leak a tab, the
handshake -- which enumerates every CDP target -- crossed it, and **every
wave's live work became a coin flip.** Five consecutive refusals on this
surface alone.

**AND THE REFUSAL TEXT POINTED AT THE ONE THING THAT WAS NOT WRONG:** it
explains at length that Chrome must be running and how to start it, while port
9224 was LISTENING, `/json/version` answered in 0.07s and the process was
alive. That is this project's own scar in a new place -- a refusal naming what
it did NOT match instead of what it SAW.

The remedy was an env override with the DEFAULT UNCHANGED, so nobody who does
not set it sees a difference. **The knob is not the fix and the comment at the
site says so**: raising a timeout buys time against unbounded growth, and 12.8
is the actual repair. What the knob buys is that a wave which cannot get a slot
has something to try OTHER than killing a browser it does not own -- and five
refusals in a row is exactly when somebody reaches for that.

### 12.10 CLEARING A NEW GUARD: count it out, do not declare it in

**The situation is going to recur, because a guard extended today catches
yesterday's files.** The page-text rule extended the taint engine from URLs to
text-extraction sinks and caught this wave's newest probe at three sites: a
count, a dict of HTML tag names, and a class string made entirely of this
repository's own vocabulary.

**EVERY ONE WAS SAFE IN SUBSTANCE AND THE GUARD WAS STILL RIGHT.** None of that
safety is visible to it, and a later edit to any of those expressions could
carry a name past a review that had already happened. The surface makes it
concrete: `census_substitute` returns a plain human name UNCHANGED -- measured
on this project, this week -- so a group page's text can carry a member's name
that neither the url rule nor the shaper would catch.

**THREE REMEDIES EXIST AND THEY ARE NOT EQUAL:**

| remedy | what it tolerates afterwards |
|---|---|
| bump the pin | the sites, forever, unreviewed. **The bulk re-baseline this register already records as where a real guard goes to die** |
| declare the site | that whole SINK EXPRESSION forever, whatever it later holds |
| **remove the site** | nothing |

The third was taken: the tainted values are read ONLY inside `len()` and inside
comparisons, so what reaches a print is an integer or a string the file
authored. **Counting a thing is what this package does instead of printing it**
-- the guard's safe exits are not a loophole, they are the discipline written
as a rule.

**AND THE OUTPUT GOT BETTER, WHICH IS THE PART NOBODY EXPECTS.** "Emit a count"
reads as a loss of information. It was not: the rewrite replaced one class
string per control with a per-needle tally, so the report now says WHICH
forbidden substrings were met and how many controls met each, where before it
said only that some were met.

**NOTE FOR WHOEVER CLEARS A GUARD ON THEIR OWN INSTRUMENT.** The author of this
guard left these sites RED rather than folding them into its own baseline on
the day it was built. That is the correct move and it is worth copying: a guard
whose first act is to absolve the files its author could see is a guard that
has never refused anything.

### 12.11 `scripts/count_census_states.py` -- the census count, reproducible from a clone

Counts the state of every capability row in `_audit/_census/` and reports the
totals. It exists because **the number it produces is this repository's most
quoted figure and could not be re-derived by anybody with a clone.** Every count
behind 409 was taken with a script under `_audit/_scratch/`, which `.gitignore`
excludes deliberately, so the instrument and the headline lived on one disk.

    ./venv/Scripts/python.exe scripts/count_census_states.py
    ./venv/Scripts/python.exe scripts/count_census_states.py --expect J=99,P=79,M=109,N=122
    ./venv/Scripts/python.exe scripts/count_census_states.py --unstated

**SHOWN FAILING, IN BOTH DIRECTIONS, 2026-09-05.** The `--expect` control is the
thing that can be wrong, so it is the thing demonstrated:

    --expect J=84,P=73,M=99,N=113   (the true counts)     rc=0   MATCH
    --expect J=99,P=79,M=109,N=122  (the frozen counts)   rc=1   MISMATCH

An `--expect` that could only pass would certify nothing. Note the exit code is
the assertion -- piping the run through `tail` swallows it, which is how a
MISMATCH can print and still look green in a terminal.

**THE THING IT REPORTS THAT NO PREVIOUS COUNTER DID: `--unstated`.** It lists
rows sitting in a capability table that carry NO recognised state at all.
Measured the day it was written: **`N 132` is GAP, says so in its own note, and
is invisible to every counter in this repository**, because its state cell was
replaced with a sentence -- a live-read result written where the state belongs.
So a GAP row left the numerator with no ruling, no amendment, and no diff that
looks like a state change.

**AND THE WARNING THAT COMES WITH IT.** This counter and the older scratch one
were written by different authors and BOTH return the same figure, because both
share the same assumption about where a state lives. **Agreement between two
instruments sharing a defect is not corroboration.** `N 132` was found by a git
diff of the census against a dated commit -- a different instrument asking a
different question. A counter that cannot report what it could not see
under-reports in silence, which is what `--unstated` is for.

**WHAT IT DELIBERATELY DOES NOT DO: compute a denominator.** Rows are not
capabilities. `profile.md` collapses two blocks -- `O6-O20` is one line standing
for 15 capabilities, the `P-R` block one line standing for 45 -- so the published
761 is 705 table rows + 59 expansions - 2 stateless rows, while the GAP numerator
is a plain row count over the same 705. Correcting a capability total from a row
parse is an error this corpus has already refused once, at `93ff6ae`, for exactly
this reason. **An instrument that reports only what it measures is worth more
than one that derives a second number it cannot check.**

Companion record: `_audit/2026-09-05-census-recounted.md`.

### 12.12 `scripts/enumerate_gap_rows.py` -- the census count, by ID and at any ref

12.11 says how MANY rows carry each state. It does not say WHICH, and that gap
is why the ledger that split 409 GAP rows across 97 blockers was unauditable for
two days: the classifier was never committed, so a per-blocker count could not
be distinguished from a per-blocker guess, and a re-cost could not be told from a
miscount.

    ./venv/Scripts/python.exe scripts/enumerate_gap_rows.py --control
    ./venv/Scripts/python.exe scripts/enumerate_gap_rows.py --ref 1c08e5f --count-only

**IT IMPORTS 12.11 RATHER THAN REPARSING**, and states the price in its own
docstring rather than leaving it to be discovered: **it inherits that parse's
blind spots exactly.** A row whose state cell is prose is invisible to both, for
the same reason and at the same moment. A shared parse is not a second opinion
and this file does not pretend to be one.

**`--control` GUARDS A REPLICATION AND NOTHING MORE.** One behaviour could not be
imported because it lives inside 12.11's `main()` with no seam -- the network
slice's admin-only table has no state column, so `N A<digits>` is forced to GAP.
The control re-runs 12.11 as a subprocess and fails on any per-slice
disagreement. **It cannot detect a defect the two share, because they share the
parse by design**, and 12.11's own entry is the receipt for why that distinction
must be written down rather than assumed.

**`--ref` IS THE HALF THAT PAID.** It reads the four slices out of a git object,
so a frozen row set is recoverable rather than merely remembered. Measured with
it, 2026-09-05: the census at `1c08e5f` enumerates **99 / 79 / 109 / 122 = 409**,
reproducing the ledger's four per-slice figures and not merely their total --
**two errors of opposite sign cancel in a total and cannot cancel in four
figures at once.** And the frozen set diffs to today's row by row: 40 rows have
left GAP, 1 has entered (`P L2b`), 409 - 40 + 1 = 370, which is what 12.11
returns. Before this, 409 and 370 were two numbers from two passes.

**A TWO-POINT DIFF CANNOT SEE A ROUND TRIP.** `N 132` was countable at
`1c08e5f`, invisible by `990bbd3^`, and countable again after `083a872`. Both
endpoints agree and the middle does not. Sample a third ref before claiming a
row never moved.

### 12.13 `scripts/build_blocker_map.py` + `tests/test_blocker_map_is_derived.py` -- a map that cannot silently stop being derived

Joins `_audit/_census/blocker-assignments.tsv` (the evidence, one line per
assignment with its committed source) to the row set from 12.12, and diffs the
recount against the ledger's published per-blocker counts. Emits
`_audit/_census/blocker-map.tsv`.

**THE HEADLINE IT PRODUCES IS THE UNASSIGNED COUNT**, currently 287 of 409, and
that is deliberate. A map that silently mixes derived and inferred assignments
**manufactures auditability, which is worse than the honest silence it replaces**
-- so a row no committed source names is `UNASSIGNED`, and there is no `INFERRED`
class because there are no inferred rows. The strongest single candidate found
(`N 132` completing `ANALYTICS-CONTROLS-UNPRESSED` by elimination over its
family) was deliberately LEFT unassigned for exactly this reason.

**SHOWN FAILING IN FIVE DIRECTIONS**, four planted and one that arrived by
itself:

    delete one evidence line             ratchet + map-drift red
    double-assign an already-mapped row  DOUBLE-ASSIGNED
    plant an id matching no census row   UNRESOLVED
    plant a 2nd row on a 1-row blocker   over-count + map-drift red
    break the ledger table header anchor "blockers the parse does not know"

**THE FIFTH IS THE ENTRY'S WHOLE ARGUMENT, because it was not planted.** One
hour after the guard was written, a neighbouring wave appended 19 lines to the
ledger (`f7594c0`, 1546 -> 1565 lines); both its tables slid 28 rows down, and
`ledger_counts()` -- which read them out of a HARDCODED LINE WINDOW -- lost the
cost-0 table entirely. Nine blockers parsed as absent, `.get(b, 0)` turned absent
into zero, and four legitimate blockers read as over-counted.

**A reading pinned to a POSITION in a file other waves are appending to.** Both
tables are now found by their HEADER ROW.

**AND THE DEFECT IN THE MESSAGE WAS WORSE THAN THE DEFECT IN THE PARSE.** The
assertion reported *"a committed source and the ledger disagree about which rows
are in a set"* -- a cause it had never observed. It had SEEN four blockers
missing from a lookup and REPORTED a data disagreement, sending its reader
hunting something that did not exist. **`refusals-must-name-what-they-saw`,
inside a guard written to enforce exactly that discipline.** It is now two
assertions that cannot be confused: *does the parse know this blocker at all*
comes first, and says to check the parse before treating anything as a
disagreement.

**THE RATCHET IS A CEILING, NOT A PIN.** `UNASSIGNED` may fall freely --
somebody finding a committed source that names more rows is the point of the
artifact and must not need permission. It may not rise. And the dangerous
direction is asserted separately and never merged: a blocker holding MORE rows
than the ledger published is two committed sources disagreeing about set
membership, which is a finding for a person, not a number to absorb. That
assertion has already caught one -- `M C52` is claimed by `HASHTAG-EXISTENCE`
(the ledger's own Amendment A13) and by `FEED-PREFERENCES`
(`2026-09-05-settings-tail.md`), and the row's text supports both.

Companion record: `_audit/2026-09-05-blocker-map.md`.

## The jobs-requeue wave, 2026-09-05

Four instruments, and one of them answers a question no probe in this
repository was asking.

### 14.1 THE LANDED-ADDRESS CHECK -- the one to copy

    scripts/_probe_job_alerts_live.py

`assert_read_url` gates the REQUESTED url and NEVER re-checks the LANDED one.
`tests/test_readonly_boundary_invariant.py` has recorded this about
`/messaging/` since August and calls it *"harmless today ... and a trap the
moment anyone adds that check."*

**THE CHECK IS ONE LINE AND IT FIRED ON THE FIRST ADMITTED ADDRESS IT WAS
POINTED AT:** ask the shipped predicate about the address the browser actually
came to rest on.

    landed = await BROWSER.goto(page, url)
    landed_admitted = readonly.is_read_url(str(landed))

An admitted address frozen nine minutes earlier redirected to a path the
allowlist REFUSES. **This repository has 32 allowlist patterns and, before
this, none of them had been asked the question.** It costs nothing on top of a
page load a probe is already taking.

**SHOWN FAILING:** the control (`/jobs/search/?keywords=...`) answers YES on
the same run the subject answers NO, so the check is shown discriminating
rather than shown refusing.

### 14.2 The boundary line-attribution probe, and why this one is TRACKED

    scripts/_probe_boundary_line_attribution.py <needle> <expected-old-digest>

Drops the lines carrying a needle, re-runs the SHIPPED `ast_digest`, and
compares against the previously pinned value: if the tree minus your line
hashes to the old pin, nothing else rode in on your re-freeze.

**IT IMPORTS `ast_digest` FROM `tests/test_readonly_boundary_invariant.py`
RATHER THAN REBUILDING IT.** Four waves reimplemented a shipped instrument in
one day and three got a broken one.

**TWO CONTROLS RUN BEFORE IT WILL PRINT A MEASUREMENT.** A needle NO line
carries must drop 0 lines and move 0 digests; dropping a DIFFERENT,
pre-existing entry must land on a digest that is neither pin. Without the
second, a check that returned the pinned value for any deletion would look
like it worked.

**AND IT IS TRACKED, WHICH ITS PREDECESSOR WAS NOT.** The previous re-freeze
recorded that its attribution probe lived under `_audit/_scratch/`, is
gitignored, and **does not survive a clone** -- so the evidence had to live in
a comment. This one can be re-run.

### 14.3 The family-pattern planter

    scripts/_probe_alerts_family_pattern.py

Compiles the family pattern a wave would naturally reach for, applies it to a
COPY of the roster, and reports per address: does a forbidden substring bite,
does anything admit it today, would the family admit it.

**THE NUMBER THAT MATTERS IS THE INTERSECTION:** addresses the family admits
where NO substring bites are refused today by nothing but the absence of a
rule. On `/jobs/alerts/` that set is FOUR and one of them is a `pause` VERB --
a write nothing defends. Generalises to any root: point it at a new namespace
before writing an allowlist entry there.

### 14.4 The refusal-table precondition guard

    tests/test_the_refusal_table_needs_a_spec.py

`writes._NINE_REFUSALS` is keyed by action and its only consumer takes a
`WriteSpec`, so a key for an action not in `SANCTIONED_WRITES` is unreachable.
Two waves read the table's two blocker shapes as an invitation to file an
unopened-surface row there at no cost. It is not that door.

**THE VACUITY IS THE WHOLE DIFFICULTY.** The table is EMPTY, so "every key is
registered" passes over zero keys. Every assertion is PAIRED with a plant --
an unregistered key that must be flagged, a registered one that must not be,
and a test that the two plants are genuinely different cases so a fixture that
was secretly registered cannot make the pair agree for the wrong reason.

### 14.5 Two instrument failures worth the register more than the instruments

**A TALLY OVER THE WRONG DICTIONARY KEY.** `control["name"]` returned ZERO for
every word on every page -- including `on`, across 185 controls of a page
LinkedIn certainly labels in English. The census publishes `shape`. Reported
as-is it would have been *"no alert controls are drawn"*: a finding about a
key, wearing a finding about LinkedIn.

**A CONTAINMENT TEST THAT FAILED ON ITS OWN CONTROL.** Comparing whole URLs
read False for a page that certainly served, because LinkedIn reorders a query
string. It was measuring the query, not the route. Comparing PATHS fixed it --
and only then did the subject's False mean anything.

Both ran in the flattering direction and neither was caught by reasoning.
**Both were caught by the control disagreeing**, which is the argument for
paying for a control on every probe rather than on the ones that feel risky.

### 14.6 The taint guard shapes probe code, and the shape is worth knowing

`tests/test_navigation_is_never_derived.py` is a fixed point over BINDINGS, not
over types. It refused `print(f"...{kept}")` for two BOOLEANS that structurally
cannot carry an address, and it refused a helper that RETURNED a literal label
because the helper was called with a tainted argument.

**THE TWO ROUTES THAT NEED NO `_SANITISERS` ENTRY**, and a declaration
permanently widens what the guard tolerates:

* **branch to literals at the print site** -- `if kept: print("...yes")`;
* **print INSIDE the loop**, so the print expression is bound to a label that
  came from a module constant rather than from the browser;
* and `len()` of a tainted value is a form the guard already recognises, which
  `_relation` documents about itself.

Companion record: `_audit/2026-09-05-jobs-requeue.md`.

## 15. The profile version-skew gate, 2026-09-19

    linkedin_server/profile_version.py      the gate
    tests/test_profile_version_gate.py      its control, 36 tests

Refuses a Playwright launch when the persistent profile's `Last Version` stamp
is NEWER than the chromium about to open it. Commits `27aa37e`, `7b26c00`,
`3f6235e`.

### 15.1 A NET IS NOT A GATE, and the difference is where it runs

`session_store.restore_into_context` had stood for three weeks as the answer to
the downgrade that cost the signed-in session on 2026-08-25. It is not an
answer, and reading its own docstring says why: it runs AFTER
`launch_persistent_context`, it is "additive and conditional", and "every
failure path returns restored: False". By the time it is asked anything,
Chromium has already migrated the profile and moved it aside.

**THE TEST THAT SEPARATES THE TWO, and it is two questions, not one:**

* does it run BEFORE or AFTER the step that cannot be undone?
* when it fails, does anything go red -- or does it return a falsey field into
  a log line nobody reads?

A mechanism that answers "after" and "returns falsey" is a net. Nets are worth
having and this one is; what it must not do is occupy the slot where a gate
was never built, which is what it had been doing.

The rule it was standing in for existed only as PROSE -- a comment in
`browser.py`, a docstring in `start_chrome.ps1`, a paragraph in the handoff
file. Three statements of a rule and no consequence.

### 15.2 WHEN A GATE FAILS OPEN, AUDIT THE READ, NOT THE COMPARE

This gate allows on every uncertainty: no stamp file, unparseable stamp,
unresolvable chromium version. That is correct -- you cannot prove a downgrade
you cannot read, and failing closed would let one corrupt byte block every tool
in the server.

**But it means no input problem ever surfaces as an error. It surfaces as a
silent pass on exactly the input the gate exists to refuse.** A leading BOM
leaves the stamp as `\ufeff153.0.8010.48`, misses the version pattern, and the
downgrade proceeds -- reported as `stamp_unparseable`, which reads like a
diagnosis and is actually the failure. Fixed by reading `utf-8-sig`.

**GENERALISES:** for any fail-open check, the decode and the parse are part of
the attack surface and the comparison is not. Review effort goes where the
silence is.

### 15.3 A VERSION COMPARISON IS NEVER A STRING COMPARISON, and the data hides it

`"152.0.7977.77" > "151.0.7922.34"` is True as text and would have passed
review. `"9.0.1.0" > "10.0.1.0"` is also True as text, and wrong.

**The live skew on this box sorts correctly either way**, so the bug could not
have been found on the data anyone was looking at. It needs its own case,
asserted in the direction the real data cannot exercise, with a control in the
opposite direction so the case is not passing because the gate stopped
refusing anything.

### 15.4 Verifying a `.ps1` you must NOT run

`scripts/start_chrome.ps1` starts Chrome. Its skew warning was misstating a
version and could not be tested by running the script.

**THE INSTRUMENT:** parse the shipped file with
`[System.Management.Automation.Language.Parser]::ParseFile`, assert zero parse
errors, `Find` the `FunctionDefinitionAst` by name, and `Invoke-Expression` its
`.Extent.Text` -- the function's OWN shipped source, not a copy retyped into
the harness. Then call it with arguments that exercise each arm. Reusable for
any script whose side effects make a live run unacceptable, and the parse
check alone is worth having: it is a syntax gate over the whole file for free.

### 15.5 THE POWERSHELL NATIVE-STDERR TRAP -- latent in every script here

Under `$ErrorActionPreference = 'Stop'`, Windows PowerShell 5.1 wraps each line
of a NATIVE command's REDIRECTED stderr in an ErrorRecord, and Stop makes the
first one TERMINATING. Measured:

    CAUGHT:  System.Management.Automation.RemoteException
    MESSAGE: Task was destroyed but it is pending!

That is playwright's ordinary teardown noise becoming a control-flow event.
Adding `2>$null` to hide it is what broke the function, on a box where it
resolves perfectly. It failed CLOSED -- no number rather than a wrong one --
so nothing was misreported, but the warning would have been permanently
numberless with no visible cause.

**Every `.ps1` in `scripts/` that sets Stop at file level and redirects a
python or node child's stderr has this, whether or not anyone has noticed.**
The fix is to scope `$ErrorActionPreference = 'Continue'` inside the function
that owns its own try/catch, not to drop the redirect.

### 15.6 `python -` puts the CURRENT DIRECTORY on `sys.path`

An arm of the harness deliberately passed a WRONG module root and passed
anyway, because cwd happened to be the repo. **Any check of an import path, run
from inside the repo, is measuring cwd and not the argument.** Run those arms
from `C:\`.

Same family as the 2026-09-05 finding that a targeted run clears SHAPE
violations but never ENUMERATION ones: what the check can see is decided by
where it runs, not only by what it asserts.

### 15.7 A GATE'S WORTH IS ITS CALL-SITE CENSUS, and it is one grep

    grep -rn 'launch_persistent_context' --include='*.py' linkedin_server/ scripts/
      linkedin_server/browser.py:239      <- the call site, gated
      linkedin_server/preflight.py:5      <- a docstring quoting the error text

    grep -rn 'user_data_dir' --include='*.py' linkedin_server/ scripts/
      linkedin_server/browser.py:240      <- the same call

One call site, so the gate is THE door and not one of several. **State the
census, not the intent**: "nothing else launches" is a claim, and the two greps
are the measurement. A gate on one of four doors and a gate on the only door
are different objects that read identically in a commit message.

### 15.8 An assumption you cannot discharge becomes a test, not a comment

In HEADLESS mode this gate reads the version of a binary that is NOT the one
about to run: Playwright publishes one executable path and it is the HEADFUL
chromium, while a headless launch uses a separate `chrome-headless-shell` whose
path the Python API does not expose (`preflight` measured that on 2026-08-22).
The gate is right headless only because Playwright rolls both at one revision
and one version.

That is an assumption about somebody else's release process -- the kind that
stops being true silently, in the direction of PASSING. It is now asserted
against the installed package's own `browsers.json`, as AGREEMENT rather than
as a number, so a routine browser roll needs no edit and a decoupling turns it
red.

**GENERALISES:** when a check rests on an upstream invariant you did not
choose, the cheap move is not a comment. It is one assertion against the
upstream artifact that already states it.

### 15.9 Where the version came from, and why not the obvious places

NOT a constant (`151` would be wrong after the next upgrade, silently, in the
direction of passing) and NOT by running the binary (a launch is the thing
being gated). Read off the path Playwright itself published, which `preflight`
had already resolved -- so no second query and no reimplementation of the
locating machinery:

    <browsers>/chromium-1234/chrome-win64/151.0.7922.34.manifest

**The version is the NAME of a file beside the executable.** Fallback for a
layout without it (every Linux cell): the revision is in the path and the
package ships `driver/package/browsers.json` mapping revision to
`browserVersion`. Both routes are live -- the CI matrix runs two ubuntu cells
and one windows, so the matrix exercises them rather than an argument.

### 15.10 THE FULL SUITE EARNED ITS 21 MINUTES, and a clean clone did not

This wave ran, in increasing order of cost and apparent authority: the new
test file; the four affected files; the same five files IN A CLEAN CLONE. All
green. The full suite then found a red that is this wave's:

    FAILED tests/test_readers_outside_dom_are_a_pinned_inventory.py
      newly unwired: ['profile_version.read_profile_stamp']

**A CLEAN CLONE IS NOT A STRONGER VERSION OF A TARGETED RUN. It is the same
SCOPE with less contamination.** It answers "does my slice depend on somebody's
uncommitted file", which is worth knowing and is what it was run for. It cannot
answer "did adding a module change a fact about the PACKAGE", because that
question is not inside the files I named -- and I named the files.

This is 2026-09-05's law arriving from a new direction. That entry said a
targeted run clears SHAPE violations and never ENUMERATION ones, because an
enumeration guard fires on *somebody added one* and that condition does not
exist until it is added. The new half: **isolating the tree does not convert a
targeted run into a whole-package one.** Sorting reds by what the assertion is
ABOUT has a companion question -- what is the assertion QUANTIFIED OVER? A
guard whose subject is "every module in the package" is only ever answered by
running it over every module in the package.

Practical form: **adding a FILE to `linkedin_server/` is an enumeration event.**
Whatever else a wave runs, it owes the package-scope guards -- this one,
`test_reader_reachability`, `test_page_text_is_never_printed`,
`test_a_person_name_is_never_a_literal` -- which together take about 30 seconds
and would have caught this before the commit rather than after it.

### 15.11 The guard was right about the NAME, which is the rarer outcome

The remedy was NOT a line in `KNOWN_UNWIRED`. That dict is empty and its own
docstring says why: *"Do not read the empty dict as permission to add a line to
it; read it as the state a new line would break."*

The detector selects `read_*` functions no OTHER module calls. Every other
`read_*` in the package is an entry point somebody calls; this one was a step
inside `check()`, and the module IS wired -- `browser.start()` calls
`assert_no_downgrade`. So the function was reachable and was claiming a
vocabulary it did not belong to. Renamed `_read_profile_stamp`, matching the
three private helpers already beside it.

**Declaring would have moved "readers nobody can call" from a measured ZERO to
a declared ONE, permanently**, to avoid a rename. When a guard fires on
something you just wrote, the first question is not how to declare it -- it is
whether the guard has just told you something true about your own code.

## 16. The content tail, 2026-09-19

### 16.1 `tests/test_a_retired_row_rests_on_a_live_assertion.py`

**A CENSUS ROW RETIRED ON A SHIPPED ASSERTION GOES RED WHEN THAT ASSERTION
LEAVES.** For each retired row the guard reads the census STATE and the SHIPPED
ASSERTION together, so deleting a name from
`test_no_write_tool_names_a_third_party.FORBIDDEN_PARAMETER_NAMES` turns the
rows resting on it red rather than leaving three retirements standing on a rule
nobody ships any more.

`scripts/count_census_states.py` cannot do this and is not failing to: it counts
STATES, so a row retired on a live rule and a row retired on a rule deleted last
week are the same green to it. **That gap is the entire subject.**

**SHOWN FAILING THREE WAYS, each against a COPY so no contended file was
edited, and two of the three carry a discrimination case:**

    natural, before the census edit   RED   3 failed / 5 passed -- the STATE
                                            check red on all three rows while
                                            the ASSERTION check was GREEN on all
                                            three
    MUT-1  a row deleted from a copy   RED   named MISSING rather than passed over
           discrimination C10          PASS  the mutation is row-specific
           control: census readable    PASS  so the red is about the row
    MUT-2  'collaborators' removed
           from the forbidden set      RED   named the assertion
           discrimination C10          PASS  C10 rests on 'mentions'

**THE NATURAL RED IS THE ONE WORTH COPYING AND IT COST NOTHING.** Written
BEFORE the census was edited, the guard failed on exactly the property that was
not yet true and passed on the property that already was. That is a
discrimination proof obtained from the tree as it stood, with no mutation at
all -- and it is only available if you write the guard before you make the
change it will assert. Written afterwards it would have gone green on the first
run and proved nothing.

**TWO CONTROLS, because a guard that reads an empty corpus refuses nothing:**
the census must parse >= 80 `C` rows and contain `C1`, and the imported
forbidden set must hold >= 10 names. A slice rename or a table reformat would
otherwise leave every assertion passing over zero rows and reading as coverage.

**WHAT IT DOES NOT ASSERT, stated so it is not read as wider than it is:** it
does not claim any row is CORRECTLY retired -- that is a judgement no test makes
-- and it does not require a row to retire because a rule exists. It asserts
only that a retirement and its stated reason cannot be separated.

### 16.2 The law it discharges, and why prose could not

The article-publish wave closed with this and could do nothing else with it:

> **A RULING NOT ATTACHED TO THE ROW IT DECIDES GETS RE-DERIVED.** Four of this
> wave's six blockers were answerable from documents already in the tree --
> the operator's typing ruling living in a TEST DOCSTRING, A9's
> closed-vocabulary decision, the ledger's own merge rule, and an existing
> EXCLUDED-RULED note. Nobody had joined any of them to the rows they settle.

It wrote the law into an audit document, which is asserted by nothing. **Two
weeks later its own two ruled rows still read GAP**, because the same wave had
correctly declined to edit the ledger in the time it had and nobody picked the
intention up. The law described its own future accurately and could not prevent
it.

**THIS IS SECTION 3'S DISEASE ONE LEVEL UP.** There, a guard measured a NAME
instead of a CONTRACT. Here, a finding was recorded as PROSE instead of as an
assertion -- and prose is the guard that can never fire. The remedy is the same
shape both times: bind the claim to something a test can read.

### 16.3 A NEW INSTANCE OF THE STAGING WINDOW, and the reading that failed was the good one

Recorded because the register already holds two instances and this one narrows
the rule rather than repeating it.

Commit `ccbc62f` carries 12 insertions where 11 were staged. The twelfth is
another wave's census row, written in the seconds between the check and the
commit. The wave had staged by name, run the identity sweep AFTER staging, and
read **`git diff --cached` LINE BY LINE** -- eleven rows, all its own.

**`--only` WAS WORKING EXACTLY AS DESIGNED AND COULD NOT HELP.** It kept two
other waves' dirty census slices out of the commit, which is the failure it
exists to prevent. The neighbour's line was inside a path this wave legitimately
named.

**THE NARROWING:** the register's existing entries record that `--numstat` is
the file-level check wearing the line-level check's costume. True, and
insufficient as a remedy. **A line-level `git diff --cached` is the correct
check and it still loses, because the window is not between the flag and the
commit -- it is between the READ and the commit, and no flag moves that.**
Reading the staged lines narrows it to seconds. It does not close it.

Handled per the sanctioned protocol: adopt-commit, credit in a follow-up
(`aecec70`), the swept content checked for disclosure (shipped identity sweep,
PASS, 0 hits), the neighbour's line left byte-identical, and the author NOT
guessed -- a send to a guessed idle name forks that agent, so it was routed to
the lead who holds the roster.

### 16.4 A MEASUREMENT I WATCHED GO STALE INSIDE THE PARAGRAPH WRITTEN TO RECORD IT

The same wave wrote `GAP 366 / EXCLUDED-RULED 233` into an audit section, and
the counter run **in the same minute** read `GAP 362 / EXCLUDED-RULED 234`.
Neither reading was wrong: three census slices were dirty and other waves were
retiring rows while the sentence was being typed.

**SO A CENSUS TOTAL IN A MULTI-WRITER TREE IS A READING WITH A TIMESTAMP AND
NEVER A STATE.** What a wave can honestly publish is its own DELTA, named row by
row. This is `relayed-measurements-go-stale` arriving at a distance of about
forty seconds, which is shorter than anybody had previously measured it.

---

## 14. The article-publish wave, 2026-09-05 -- LIFTED FROM WHERE IT WAS STRANDED

**THIS ENTRY IS NOT THIS WAVE'S WORK AND I DO NOT VOUCH FOR IT.** It is lifted
VERBATIM from `_audit/2026-09-05-article-publish.md` section 10, where its
author parked it with the instruction *"Whoever holds `INSTRUMENTS.md` can lift
the block below verbatim; it is written as a register section and needs no
editing."*

**IT HAD BEEN STRANDED FOR TWO WEEKS.** Its author staged it into this file and
found the staged diff carried 118 lines of which 49 were another wave's, backed
their own 69 lines out, left the neighbour's byte-identical, and moved the entry
to their audit document -- exactly the behaviour this register prescribes. The
register then went 13 -> 15 and neither instrument below appears anywhere in it.
**The correct move under contention left the entry unreachable, and nobody
noticed for a fortnight.** That is the cost of the append-only hazard stated as
a number rather than as a risk.

**ITS NUMBER IS OUT OF ORDER ON PURPOSE.** Section 14 is the slot its author
predicted would be taken; it was not taken, it was left empty. This file is
APPEND-ORDERED by its own header rule -- *an in-place insert into a contended
file loses somebody's work* -- so the entry is appended here and numbered 14,
which is what that rule costs and what the header already warns a reader to
expect.

### 14.1 `tests/test_no_write_tool_names_a_third_party.py`

Parses `server.py` with `ast`, enumerates every `linkedin_*` function, and
refuses a parameter whose VALUE would be another member carried into published
content -- `mention(s)`, `tag(s)`, `collaborator(s)`, `invitee(s)`, `celebrant`,
`honoree`. Shown failing under a planted `mentions` parameter; a `tag` case
stays green under that mutation, which is the discrimination proof. Carries a
control pinning >= 30 tools parsed, because a rename of the `linkedin_` prefix
would otherwise leave every case passing over an empty corpus.

**THE PATTERN WORTH REUSING: EXEMPT BY NAME, NEVER BY SILENCE.**
`audience`/`visibility` are ADMISSIBLE under Amendment A9's closed-vocabulary
ruling and are listed in a `RULED_ADMISSIBLE` constant with A9 cited, plus a
third test asserting the two sets stay disjoint. A guard that forbade them by
omission would read, six weeks from now, as forbidding the very parameter a
written ruling permits -- and nobody would be able to tell the omission from a
decision.

### 14.2 `tests/test_the_audience_reader_arrives_with_its_contract.py`

`server._composer_audience_is_readable()` lifts `linkedin_publish_post`'s
refusal by FEATURE DETECTION -- `callable(getattr(dom, _COMPOSER_AUDIENCE_READER,
None))`. The reasoning beside it is sound: keying on the capability beats a
boolean that must be flipped by hand and goes stale.

**THE PROPERTY NOBODY WROTE DOWN: the act that re-arms an IRREVERSIBLE broadcast
under his own name is DEFINING A FUNCTION WITH THAT NAME.** A stub sketching the
interface satisfies `callable()` and opens the gate.

**That is section 3 of this register, arriving where it costs the most.**
`_redact` entered `_SANITISERS` on the strength of its name and carried no slug
rule at all; `_relation` was later admitted WITH the test that proves its
contract. This writes the same requirement BEFORE the reader exists, which is
the only order in which it is free.

The guard: if `dom.read_post_composer_audience` exists, a contract test for it
must exist too. Two controls -- the exact keyed string, and that the live
refusal still returns `audience_unread` -- so a rename fails there with a reason
instead of leaving the guard watching an attribute nothing consults.

**SHOWN FAILING IN-SUITE RATHER THAN IN A SIDE SCRIPT**, by monkeypatching the
name onto `dom` and asserting the guard turns red. Two details worth copying:
the demo **branches** and states which branch it took, so it cannot silently
invert into a vacuous pass once a contract test lands; and the main assertion
**skips** today with its reason rather than passing, because a test that passes
because its subject is absent is the worst green available.

### 14.3 Verified at lift time, 2026-09-19, rather than taken on trust

The entry above is the author's text. These are re-measurements of its two
load-bearing claims, taken by the lifting wave because a register entry is a
STANDING INSTRUCTION and a stale one is worse than an absent one:

    grep -n _composer_audience_is_readable linkedin_server/*.py
      server.py:6871  def _composer_audience_is_readable
      server.py:7031  if not _composer_audience_is_readable():

**One definition, one call site, both inside `linkedin_publish_post`** -- so
14.2's gate is still exactly as narrow as it describes. And both files still
pass at this tree, run together with the three surfaces they guard: **63 passed**.

### 16.5 SUCCESSOR TO 16.3 -- "no git-level fix" is wrong. It is a TRADE.

**Appended rather than edited into 16.3, under this register's own law: an entry
that is TRUE but one inference from being WRONG gets a successor, never a
charitable reading.** 16.3 is accurate about the window it measured and its
closing sentence overstates the conclusion. The correction came from the lead,
within the hour, and it is the useful half.

16.3 says the window is between the READ and the COMMIT and that no flag moves
it. True. It then implies there is nothing to choose between the two commit
forms. **There is, and it is a choice about WHICH NEIGHBOUR BEHAVIOUR YOU ARE
EXPOSED TO:**

    git commit --only <paths>   commits the WORKING TREE for those paths
                                PROTECTS from a neighbour's STAGED files
                                EXPOSES to their UNSTAGED edits inside yours

    git commit (plain)          commits the INDEX exactly as staged
                                PROTECTS from a neighbour's working-tree edits
                                EXPOSES to anything they STAGED

Neither is airtight. **So the form is chosen by what the neighbours around that
file actually DO, not by which flag is safer in general:**

* **A shared census slice or register -- several waves EDITING, rarely staging
  -- takes the INDEX form.** That is the case 16.3 lost: the neighbour's line
  arrived in the working tree, which is precisely the side `--only` exposes.
* **Your own new module while others stage freely takes `--only`.** That is the
  case it WON in the same commit, keeping two other waves' dirty census slices
  out.

**THE REFUSAL THAT MAKES THE INDEX FORM SAFE, and it is the transferable part:**
stage by name, then require

    git diff --cached --name-only

to equal EXACTLY your one path, and abandon-and-reset the path if it does not.
That does not close the window either -- it narrows it to the check-to-commit
gap. **What it changes is the FAILURE MODE: a rider becomes an ABORT instead of
a surprise**, and an abort is recoverable where a mis-attributed commit is
something you must then credit rather than undo.

**WHAT DOES NOT CHANGE, and it is the part that actually holds:** when you lose
the race anyway, adopt and credit, never rewrite. Rewriting HEAD in a tree
several waves are writing trades a mis-attributed line for something genuinely
hard to undo. 16.3's resolution stands; only its last sentence needed this.

**AND NOTE HOW THIS ENTRY CAME TO EXIST.** 16.3 was committed as a register
section -- a standing instruction -- roughly four minutes before it was
corrected. It was not caught by its author re-reading it. **A peer who had been
running the other form behind a refusal read the claim and knew it was a trade
from having paid for both sides.** That is the register's own section 3 disease
in the mildest possible form: an entry that measured its own instance correctly
and generalised one step too far, which is exactly the class a second reader
catches and the author cannot.

### 16.6 16.5's REFUSAL FIRED ON ITS FIRST USE, and the same run named the other form

Not a demonstration this wave constructed. It is what happened when 16.5 was
committed, four minutes after being written, against this file.

    git add _audit/INSTRUMENTS.md
    git diff --cached --name-only
      _audit/2026-09-19-hashtag-surface-live-evidence.md     <-- not mine
      _audit/INSTRUMENTS.md
      _audit/_census/messaging-and-content.md                <-- not mine

    -> REFUSAL. git reset HEAD _audit/INSTRUMENTS.md

**A plain commit would have swept two of another wave's files into a register
commit about not sweeping other waves' files.** The refusal turned that into an
abort, which is exactly the failure-mode change 16.5 claims and the only thing
it claims.

**AND THE SAME READING THEN CHOSE THE OTHER FORM, which is 16.5's actual
point.** The neighbour was STAGING, not merely editing -- so by 16.5's own table
this file was no longer the index-form case, and `--only` was correct for this
commit. It committed 56 insertions, **zero of theirs**, and **left their staged
index intact** (re-checked after: the same three paths, now grown to three,
still staged and untouched).

    the form is not a habit. it is a reading of what the
    neighbours are doing AT THAT MOMENT, and the reading is
    one command.

**By the time of the second check the neighbour's staged set had grown from two
paths to three** -- inside the span of a single commit. That is the window 16.3
measured, seen from the other side, and it is why the refusal is worth more than
the flag: the flag is a standing choice, and the window is a moving fact.

**WHY THIS IS ADMITTED AS A DEMONSTRATION AND NOT AS AN ANECDOTE.** This
register's bar is that an instrument enters only if it has been SHOWN FAILING. A
refusal is shown failing when it REFUSES something real, and this one did, on a
live tree, on its first use, with the thing it refused named. A planted version
would have been weaker evidence: this one did not know it was being tested.

## 17. The read tail, 2026-09-19

### 17.1 `tests/test_a_covered_row_names_the_artifact_that_covers_it.py`

**A COVERED census row goes RED when the artifact covering it leaves.** The
sibling of 16.1 and the other half of the same law: that one binds an
EXCLUDED-RULED row to the RULE that excluded it, this one binds a COVERED row
to the CODE that covers it. A census that can drift one way can drift the
other, and only the first direction had ever been looked for here.

**THE ASSERTION THAT EARNS ITS PLACE IS A PASSTHROUGH.** `verified_job` is set
inside `dom.read_job_insight_panels`'s returned dict and reaches a caller ONLY
because `server.py` assigns that WHOLE dict to `insights`. So

    grep -n "verified_job" linkedin_server/server.py     -> nothing

and a field set in `dom.py` and named nowhere else looks exactly like a dead
field. **A FIELD-NAME GREP CANNOT SEE A DICT THAT PASSES THROUGH BY REFERENCE**,
which makes a passthrough the coupling most worth asserting: either end can be
edited away and nothing in between notices. Both ends and the join are
asserted, the join off the AST.

Shown failing three ways against copies, each with a discrimination case that
stays green: `insights` assigned something else (RED, J10 chain still passes);
`COMPANY_FILTER_KEY` renamed (RED, K10 join still passes); a banked row reverted
to GAP (RED naming the row, K10 still passes). Plus a control that both slices
are readable.

**FIRST-RUN BUG, recorded because this register has measured that every fresh
instrument has one:** `ast.unparse` renders string subscripts with SINGLE
quotes, so a target check written `["insights"]` never matched and the guard
failed for a reason unrelated to the code under test.

### 17.2 `scripts/_probe_job_collections_live.py`, and the control that fired TWICE

**ADMITTED AS AN INSTRUMENT BECAUSE ITS CONTROL REFUTED ITS OWN AUTHOR TWICE,
on live inputs, without being planted.** That is a stronger demonstration than
a mutation: it did not know it was being tested.

    marker 1  "/jobs/view/" hrefs        0 on the target page
              SAME MARKER on /jobs/search/, which certainly lists jobs
                                         0  -> the zero measured the MARKER
    marker 2  control["href"]            "(no href)" on 147 of 147 controls
                                         -> looks exactly like a page with no
                                            links, and is the boundary working

**THE MEASUREMENT THAT MATTERS TO EVERY FUTURE READER ON THESE SURFACES:**
`dom.read_surface_census` carries **`has_href`** and **`href_shape`** and
**never hands out a raw href by construction.** Asking it for `href` returns a
shape indistinguishable from absence. It is a CENSUS -- it counts and shapes --
and shaping is exactly what makes it unusable as a parser. That is the shaper
doing its job, not a defect, and it is worth one sentence in a brief rather than
an hour per wave.

**THE OTHER DISCIPLINES IT CARRIES**, all copied rather than invented: the
boundary is asked BEFORE any navigation; `_relation` is byte-identical to the
groups/events copy that was admitted to `_SANITISERS` WITH the test proving its
contract; the invitation badge is read before and after (**identical**, so the
load consumed nothing -- a counter that must NOT move and does not is the only
evidence the instrument can tell the difference); it REFUSES to run without
`LINKEDIN_CDP_ATTACH=1`; and it closes the tab it opened -- **the page, never
the context.**

**AND ONE INSTABILITY IT RECORDED RATHER THAN SMOOTHED:** the same address read
75 controls on one run and 93 about five minutes later. A count off that surface
is a reading with a timestamp.

### 17.3 `linkedin_server/collections_page.py` -- the vocabulary travels INTO the page

**THE THIRD AND STRICTEST POINT ON A LINE THIS REGISTER ALREADY HOLDS.**
`groups.py` is structurally name-free because no name is a PARAMETER; `menus.py`
is structurally name-free because `classify` is pure and returns only its own
literals. Both still let a page string enter the process.

**This one does not.** The vocabulary is shipped INTO the page, the comparison
happens in the document, and what crosses the CDP boundary is a POSITION IN A
TUPLE defined in the module. A label is not redacted, not shaped, and not
present -- which needs no argument about what a shaper can recognise.

Out-of-range REFUSES rather than clamps, because a clamp silently renames one
grouping to another. A zero card count is kept distinct from an absent one.

**ADMITTED ON A CONTROL THAT SHIPS WITH IT, and the reason is the transferable
part.** Its first live read matched ZERO of five, and **a matcher that returns
zero everywhere is indistinguishable from a broken one**. The same in-page code
therefore runs against a DETACHED container built from a synthetic fixture --
no navigation, no page load -- and matched **5 of 5 plus 1 decoy unmatched**, so
it matches AND discriminates.

    THE RULE: a reader whose answer is a COUNT must ship the input that
    makes its count non-zero. Otherwise "nothing found" and "nothing
    works" are the same output, and only one of them is a finding.

With that control firing, the live zero became a measurement: 79 nodes scanned
across headings, tabs and buttons, none of the five matched, identical across
two reads, on a page carrying 53 cards. Shown failing besides: a clamping
`term_for` and an alphabet leak, each with a discrimination case, plus an
in-suite reorder demo asserting the SPECIFIC harm -- that the same index
resolves to a different term.

## 18. The anchor reader, 2026-09-19

### 18.1 `linkedin_server/anchors.py` -- route SHAPE, and the hazard class is counted

The fourth and strictest point on section 17's line. `groups.py` takes hrefs
somebody else read; `menus.py` is handed a label and returns only its own
literals; `collections_page.py` ships a vocabulary in and gets an index back.
**This does the same for ROUTES, and the reason it had to is sharper: an anchor
reader that can see hrefs can see `/in/<slug>`, and a slug is a name.**

Closed alphabet of 13 route classes. `member_profile` is index 0 and is
COUNTED, NEVER DESCRIBED. `term_for` REFUSES out of range rather than clamping,
**because a clamp at the low end renames anything into the hazard class.**

### 18.2 THE LAW: A PREDICTED HARM IS NOT A MEASURED ONE, AND MINE WAS BACKWARDS

The segment rule -- a route term must be a whole path segment at a fixed
position -- is `menus.py`'s `Star Anise` scar generalised. Writing it, I also
wrote down the harm I expected from the containment version: *a name-bearing
anchor moves OUT of `member_profile`.*

**Run in a page against the control fixture, it did the reverse:**

    member_profile   1 -> 4       help_article  1 -> 0
                                  messaging     1 -> 0
                                  school_page   1 -> 0

`in` is a substring of `linkedin`, `messaging` and `institute`. **Three
non-member routes were swept INTO the hazard class.** Over-reporting it is not
the safe direction: it makes the one count a caller must never publish
per-record wrong by 4x.

**AND THE DEMONSTRATION UNDERSTATED ITS OWN RESULT.** Its branch tested only
whether the count FELL, and printed *"member_profile held; the harm landed on
other classes"* -- while the hazard count had quadrupled. **A harm check written
from the author's model of the risk reads the measurement through that model.**
Section 14's law one level on: there the probe INPUT came from the author's
model; here the probe's INTERPRETATION did.

    Practical form: when a mutation demo reports "no harm on the axis I
    watched", diff EVERY class before believing it. The axis you did not
    watch is where a prediction that was wrong shows up.

### 18.3 A CONTROL WITHOUT A WRITTEN EXPECTATION CANNOT FAIL

`CONTROL_EXPECTATION` is a dict in the module covering all 13 classes, and the
probe ABORTS unless the fixture reproduces it exactly. The fixture carries the
two anchors a containment design gets wrong -- a COMPANY slug containing the
`school` term, and a MEMBER slug containing the `company` term. **Synthetic and
deliberately not people**, for the reason `menus.py` uses a spice.

### 18.4 A SINGLE RUN OF A COMPARISON IS NOT A COMPARISON

Interleaved live reads gave, in run 1: premium repeats, collections does not --
which reads as *the reader is deterministic and the surface is not*. **Run 2,
minutes later, flipped both.**

> A control proves an instrument CAN speak; only REPETITION proves what it said
> was stable. That applies to a DISCRIMINATION exactly as it applies to a
> reading, and a discrimination is the more tempting one to publish because it
> arrives sounding like a conclusion.

**Where determinism is actually readable: the DETACHED fixture**, which holds
the input constant and reproduced its expectation on every run. A live repeat
varies the DOM and the reader together and can separate neither.

### 18.5 Found by reading the stream, not the exit code

`_badge` printed the invitation badge's raw `label`, which came back as a nav
element's accessible name -- a raw page string, in a wave whose whole subject is
not marshalling those. It carries no member name today, **and that is a fact
about what LinkedIn happens to put there rather than a property anything
enforces**; the navigation taint guard does not cover it, because a badge is not
navigation-derived. Now counted with a `label_present` flag, not shown.

## 19. The verdict certifier, 2026-09-19

`tests/test_a_verdict_earns_its_entry.py`. Built from the brief at
`_audit/2026-09-19-the-sanitiser-list-holds-two-kinds.md`; the wave's own
close is `_audit/2026-09-19-verdict-certifier.md`.

`_SANITISERS` holds two kinds of function and its certifier understands one.
SHAPERS map input to a derived output and are safe iff no input survives AND
they discriminate. VERDICT FUNCTIONS map input to one of a closed enumerated
set and are safe iff no input survives AND the alphabet is closed. **Four
proofs, every one shown failing in BOTH directions.**

    non_constant_returns   every return is a bare ast.Constant
    falls_off_the_end      no implicit None escapes a fallthrough
    measured_alphabet      the constant set, read off the AST
    members_spoken         two DIFFERENT members actually returned

### 19.1 THE INVERSION IS A MEASUREMENT HERE, NOT A PARAGRAPH

The brief's central claim is that the shaper table does not merely misfit a
verdict function, it **scores it backwards**. That shipped as prose, and prose
is what a later tidier overrules. It now runs as a control against the
sibling's **real** `MUST_DISCRIMINATE`, imported rather than copied so it
cannot drift away from the table it names:

    honest(url) -> one closed verdict for both halves   FAILS the arm
    leaky(url)  -> "landed on " + url                   PASSES the arm

Both directions asserted, so a table that separated nothing would also fail
this. **The shaper table is not blind, it is MIS-AIMED** -- its needle arm
still refuses the leak its discrimination arm rewards, and the two are welded
together over there. That is why widening the shaper table was never a
loosening, and the argument is now re-runnable rather than re-readable.

### 19.2 THE MUTATIONS, AND THE BOTH-DIRECTIONS RULE

Nine planted, nine died, zero survivors. Every proof is broken BOTH ways --
accept-everything and reject-everything -- because a check that refuses
everything certifies nothing and fails in the direction that looks like
diligence.

    M1  non_constant_returns -> []              6 derived-return arms die
    M2  non_constant_returns -> ['no']          both accept arms die
    M3  measured_alphabet -> frozenset()        the gained-member arm dies
    M4  members_spoken -> {'a','b'}             the mute-verdict arm dies
    M5  _returns_of -> naive ast.walk           the nested-return arm dies
    M6  falls_off_the_end -> False              the fallthrough arm dies
    M7  falls_off_the_end -> True               the fallthrough arm dies
    M8  _always_exits -> True                   the fallthrough arm dies
    M9  members_spoken -> one member            the mute-verdict arm dies

M5 earns its own line: it proves the false-red arm was MEASURED and not
assumed. The naive `ast.walk` really does count a nested helper's `return x`
as the outer function's alphabet, which would fail an honest verdict function
for a reason its author cannot fix -- and a false red is how a check gets
deleted.

### 19.3 THE PROTOCOL ABOVE WAS VIOLATED, AND THE WINDOW IS MEASURED

**Disclosed unprompted rather than found in review.** The first run of this
study planted its mutants in the LIVE `tests/` directory, writing
`test_zzz_mutant_scratch.py` and deleting it in a `finally`. The preamble of
this file says to copy the tree to a scratch directory first, and it says to
read it BEFORE planting a mutation. It was read after.

**The window, and why it differs from section 0's receipt.** Eight runs, each
leaving a collectable test file in a shared `tests/` for roughly one to two
seconds -- call it twelve seconds total. **No existing file was modified, so
there was no clobber risk**, which is the material difference from the wave
that mutated a real `writes.py`. The realistic failure was another wave's
`pytest tests/` picking up a file that then vanished, producing unexplained
reds in somebody else's run and costing them a triage. Non-destructive, and
still not mine to spend.

It was then **re-run under the protocol in full**: tree copied, resolution
under the copy ASSERTED rather than confirmed, one mutation at a time, only
the selector that should die, the file restored after each, and a clean
control run at both ends. Both compliant control runs report `16 passed,
4 skipped`. The numbers in 19.2 are from the compliant run.

### 19.4 A CONTROL THAT SELECTED NOTHING, IN THE HARNESS THAT ENFORCES CONTROLS

The compliant harness's own control step built its pytest node id by appending
`"::"` unconditionally, so both the before and after control runs selected
**zero tests** and printed `no tests ran` -- a control that could not fail,
inside the study whose entire purpose is proving that checks can. It reported
`final control passed: False` and was caught by READING THE OUTPUT rather than
the exit code.

The repair is a guard rather than a fix: `run_selector` now asserts that
`"no tests ran"` is not in the summary line, so a selector that matches nothing
raises instead of reading as a pass.

> **A HARNESS THAT PROVES CONTROLS IS NOT EXEMPT FROM NEEDING ONE.** This is
> the third time in one wave that the instrument caught its own author: the
> no-discrimination test matched its own assertion text, the AST walk compared
> nodes with `==` instead of identity, and the first mutation harness's regex
> missed every target because they carry return annotations -- reading text
> where it should have read structure, which is this file's whole subject
> arriving in the tool that measures it.

### 19.5 WHY THE ENROLMENT TABLE IS EMPTY, AND WHY THAT IS THE ENTRY

`VERDICTS` ships with no real rows. Three candidates were measured against all
four proofs -- `_landing_class` (5-member alphabet) and `is_read_url`
(`True`/`False`) certify today; `_why_refused` is refused on one
`%`-interpolated return whose token comes from a runtime module attribute.
**None was enrolled, because this wave wrote none of them.** Enrolment ASSERTS
a contract is safe and that is the author's claim to make; a measurement is not
an enrolment.

An empty table makes every parametrized arm SKIP, which is why the controls
above are not decoration -- they are the only thing holding the file up until a
first row lands. `test_the_enrolment_table_is_empty_by_design` pins the
emptiness so the first enrolment is a deliberate act and not a quiet one, the
same handshake as the `_SANITISERS` pin in the sibling file.

### 19.6 THE HARNESS IS DISPOSABLE, AND THE MEASUREMENT IS NOT

The mutation harness is **declared disposable** rather than harvested: it
rewrites a tree and plants mutants, which is a thing to do deliberately under
the protocol above and not a thing to leave lying in `scripts/`. What is
durable is this entry plus the four proof functions, which are importable from
the test module and were used exactly that way to measure the three candidate
sites without enrolling any of them.

## 20. The CI instruments, 2026-09-19

CI had been red since 2026-09-05 and unrun since. These three are what recovered
it. Each is entered because it was **shown failing** — the register's own second
law — and each names the control that showed it.

### 20.1 THE LAW: A PROBE THAT CANNOT REACH THE DEFECT RETURNS THE SAME GREEN AS HEALTH

The inherited premise was *"history-dependent tests cannot resolve SHAs on an
orphan branch."* It was TRUE. It was "refuted" by grepping
`rev-list|rev-parse|log|cat-file|merge-base`, finding two files, running them
against a shallow clone, and getting **27 passed in 19.42 s**.

**That grep cannot match `git show <sha>:<path>`**, which is the shape that
actually breaks. The measurement was real; the instrument was blind; the
conclusion was wrong for 8.5 hours, during which the whole suite was paid for
locally.

**Before trusting a clean probe, show it going RED on a known-bad input.** A
green from an instrument that cannot see the defect is indistinguishable from a
green from a healthy system, and it is the more dangerous of the two because it
closes the question.

### 20.2 The shallow-vs-full clone control — does this suite need history?

```bash
git clone --quiet --depth 1 --single-branch --branch <b> "file://$PWD" /tmp/shallow
git clone --quiet           --single-branch --branch <b> "file://$PWD" /tmp/full
# run the same file in each
```

**SHOWN FAILING, same commit, same tests:** shallow **1 passed, 6 errors**; full
**6 passed, 1 failed**. Both arms bite — the shallow arm reproduces CI's
`ERROR at setup`, and the full arm's single failure was a real defect the errors
had been hiding (a census map with 427 data lines against 409 frozen GAP rows).

**What it settled:** `actions/checkout` defaults to `fetch-depth: 1`, and this
suite pins frozen baselines by literal SHA (`build_blocker_map.FROZEN_REF =
"1c08e5f"`, `test_connections_reader` pins `84dccba`). Fix is one line per
checkout step. **This control is the cheapest way to answer "is a shallow
checkout enough" for any repo, and it answers in seconds.**

### 20.3 `uv run --python <floor>` — run a CI matrix cell on a box that has no such cell

```bash
uv run --quiet --python 3.10 --with pytest --no-project -- \
    python -m pytest tests/<file>.py -q -p no:cacheprovider
```

The build box is **windows py3.13 only**; the matrix is ubuntu 3.10, ubuntu
3.13, windows 3.13. Two of three cells had never been exercised here.

**SHOWN FAILING:** `test_the_package_compiles_on_its_oldest_python.py` reported
**4 failed** on a real 3.10 while passing on 3.13. After the fix, the same
command **immediately surfaced a SECOND instance of the identical bug**. An
8-minute CI round trip surfaces those one at a time.

**The bug class it catches: A GUARD WRITTEN TO POLICE A LOWER BOUND, ONLY EVER
EXECUTED ABOVE THAT BOUND.** `lint.violations()` calls `ast.parse`, and its
fixtures are PEP 701 constructs — legal from 3.12, a `SyntaxError` before it —
so on the floor the PARSER refused the fixture before the rule could fire. The
guard for the 3.10 floor could not itself run on 3.10.

**LIMIT, stated because it matters:** this does NOT cover the ubuntu-vs-windows
axis. Path separators, drive letters, junctions, symlink privileges and POSIX
absolute paths still need a real Linux runner — and that axis produced its own
defect the same day (20.4). For those, CI is the only instrument.

### 20.4 THE LAW, SECOND FORM: A CONTROL THAT CANNOT FIRE ON A PLATFORM CERTIFIES NOTHING THERE

`test_that_forced_failure_can_actually_fail` exists to prove the path-scrubbing
assertion CAN fail. It did that by asserting the unscrubbed message carries a
**DRIVE LETTER** — which is only how "absolute" looks on Windows. On ubuntu the
message read a POSIX path and the control failed **in its own words**: *"the
unscrubbed message carried no drive letter, so the assertion above proves
nothing on this platform."*

**It was right about itself.** The repair is `ABSOLUTE_PATH = DRIVE_LETTER if
os.name == "nt" else POSIX_ABSOLUTE`, verified in BOTH directions: it matches
CI's real unscrubbed message and does NOT match the scrubbed relative one, so it
cannot go inert either way.

**THREE VARIANTS OF THIS ONE LAW LANDED ON 2026-09-19**, and all three looked
green: a control that could not fire on Linux; an identity guard silently
disarmed in every worktree (gitignored wordlist, and git does not carry ignored
files into a linked worktree); and a floor guard that could not run on its floor.

### 20.5 The two-root resolver probe — which tree is being gated?

```python
spec = importlib.util.spec_from_file_location("bg", "<gate>.py")
m = ...; spec.loader.exec_module(m)
print(m._tree_being_committed(), m._tooling_root())   # run from main AND from a worktree
```

**SHOWN DISCRIMINATING:** from the main checkout both roots are the same; from a
linked worktree content=worktree, tooling=main, venv still reachable. The
unfixed copy collapses both to the script's own checkout.

**What it settled:** the boundary gate read one tree's INDEX and ran the other
tree's FILES, because `REPO = Path(__file__).resolve().parent.parent` and
`.git/hooks` is shared. Both directions were live and the dangerous one is
silent — a guard a worktree commit BREAKS was checked against main's clean copy
and ALLOWED.

**The distinction the probe makes visible: GIT QUERIES RIDE `GIT_INDEX_FILE`;
FILESYSTEM READS FOLLOW `REPO`.** Measured from a probe hook: git exports
`GIT_DIR` and `GIT_INDEX_FILE` absolute into every hook, so `git diff --cached`
answers for the worktree even with `cwd` forced to main — which is why the
identity gate was correct by construction and must NOT be "fixed" the same way.
Pointing its `REPO` at the worktree would lose the gitignored wordlist and hit
`if not wordlist: ... ALLOWING`.

### 20.6 DISPOSABLE, declared

`scripts/purge_denied_term.py` is **not** disposable and already shipped; it is
the tool that unblocked a 14-day push freeze in four minutes. The ad-hoc probe
hook used in 20.5 (`core.hooksPath` pointed at a scratch dir for one commit) IS
disposable — its finding is recorded above and the technique is one line.

## 21. The blocker-map instruments, 2026-09-19

Four checks built while closing the eight blockers still PARTIAL. Two of them
caught their own author before they caught anything else, which is why they are
here rather than in a progress file.

### 21.1 `scripts/_check_jobs_range_directions.py` -- the 19 blockers nobody was watching

`_check_published_split.py` compares each blocker's held R/W split against the
ledger's published split, and SKIPS any blocker holding a jobs-slice row. Its
docstring says why: `jobs.md` keys direction by RANGE, not by row id. **That
was 19 of 88 published splits unwatched, including `COMPANY-PAGE-SURFACE`, the
largest PARTIAL in the map.** The ranges are machine-readable -- section 2 is a
table `| rows | gap | shape | R/W | REV |` whose first cell is a range spec --
so this expands them. 19 skipped -> 14 readable, 5 still blind.

**THE LAW IT ADDS: THE SAME NOTATION MEANS DIFFERENT THINGS IN A PER-ROW TABLE
AND IN A RANGE TABLE.** In `messaging-and-content.md` an `R/W` cell means THAT
ROW both reads and writes. In `jobs.md` section 2 a `R + W` cell means the
BLOCK contains both -- `70-73` is "resume upload, list, delete, download", four
rows of mixed direction, not four rows that each do both.

**SHOWN FAILING, AND IT FAILED IN THE DIRECTION THAT LOOKS LIKE A FINDING.**
The first draft mapped `R + W` to `RW`. That put 5 phantom `RW` rows into
`FILE-UPLOAD-UNSANCTIONED` and 7 into `OPEN-TO-WORK-MODAL`, and both then
reported **OVER on a direction no row in them carries** -- two new over-runs
that would have been argued rather than doubted. Compound cells now resolve
nothing and the unresolved count is printed, so the reading's coverage is
visible instead of implied.

**CONTROLS.** `--control-blind` blanks one range's direction cell and requires
its rows to move into UNRESOLVED rather than keep a stale reading.
`--control-overrun` inflates one blocker's held writes and requires the printed
table to NAME it -- **and it injects into a blocker the report calls "within
split" on the real data.** The first version injected into
`COMPANY-PAGE-SURFACE`, which the report already names for a different
direction, so the control passed whether or not the injection did anything: it
was measuring the baseline, not the instrument.

### 21.2 `scripts/_check_refile_destination_credit.py` -- COMPLETE over a blocker that is short

`RE_FILED` fixed the SOURCE side of a re-file: a blocker short a row that now
lives elsewhere reads ACCOUNTED rather than PARTIAL. **Nothing fixes the
DESTINATION side.** The moved row still counts toward the receiving blocker's
published total, so an incoming re-file pays for one of ITS OWN published rows
that nobody recovered, and the verdict prints *"COMPLETE -- every published row
recovered"* over a blocker that has not recovered them.

    SEARCH-RESULTS-SURFACE   publishes 21, holds 21, 4 incoming -> 17 of 21
    FEED-PREFERENCES         publishes  1, holds  1, 1 incoming ->  0 of 1

**THE LAW: A COUNT-NEUTRAL MOVE IS INVISIBLE TO EVERY COUNT ASSERTION, BY
CONSTRUCTION.** That is the same structural blindness `_check_published_split`
exists for, one level up -- and the split caught one of these as "+1R on
`SEARCH-RESULTS-SURFACE`" when the real figure is four rows.

**CONTROL.** `--control` adds a synthetic incoming re-file at a blocker the
real data does not name, and requires the report to name it.

### 21.3 `scripts/_sweep_frozen_rows.py` -- the sweep every "family exhausted" verdict was run by hand

Telling a MISSED ROW from an OVER-COUNT means answering one question: does any
UNASSIGNED row belong to this family? Every such verdict in this repository has
rested on somebody running that sweep by hand and committing only the
conclusion, so the next wave re-ran it from memory and the one after took the
conclusion on trust.

**IT IS EVIDENCE FOR THE NEGATIVE ONLY, and the docstring says so.** A name
match is not evidence for an assignment. But if a word naming a blocker's
family returns rows and every one is already filed, the family is closed.

**CONTROL, BOTH ARMS, BECAUSE ONE ARM PROVES NOTHING.** A word the frozen set
certainly contains must return hits; a word it cannot contain must return none.
A sweep that only ever confirms cannot be shown to discriminate; one that only
ever misses cannot be shown to see.

### 21.4 `scripts/_check_duplicate_rows_share_a_blocker.py` -- and a shape pairwise similarity cannot see

Built to test one premise: `blocker-assignments.tsv` admits `P B7` to
`BADGES-SURFACE` on an arithmetic requiring that `B8` and `K9` *"collapse to
one slot"* -- that one blocker cannot hold two frozen rows of one capability.
Measured: **15 near-duplicate pairs are filed to ONE blocker, 6 of them
intra-slice.** The premise is false.

**THE SECOND ARM IS THE ENTRY.** A compound row split across a slice boundary
into halves is INVISIBLE to pairwise similarity: `M C79` *"Follow or unfollow
member articles"* scores **0.50** against each of `N 41` and `N 42`, under any
useful threshold, while its token set is wholly CONTAINED in their union. A
wave running only the pairwise arm reports the two halves as unrelated to a row
sitting in the very blocker they are candidates for.

**SHOWN FAILING AS A COINCIDENCE GENERATOR.** Bare containment returned **1217
hits** -- nearly all a row plus an unrelated bystander carrying the one missing
word. Three STRUCTURAL constraints cut it, each describing the shape rather
than tuning the output: the two halves live in one slice and the compound in
another; neither half may cover less than half the compound's tokens; neither
may already contain the whole. **A detector tuned until it agrees with the
reader is the reader wearing an instrument's clothes**, which is why the fix is
stated as three shape rules and not as a threshold.

**CONTROLS, ONE PER ARM.** Pairwise must find `M C83`/`P L4`, which
`2026-09-19-the-five-requests-ruled.md` names by hand. Containment must find
`M C79` inside `N 41` + `N 42`, which `2026-09-19-partial-blockers-closed.md`
names by hand. An arm that misses its known pair is blind and its silence means
nothing.

### 21.5 THE METHOD THAT PAID BEST: CHECK THE CLAIMS YOU DO NOT NEED

`network.md:590` is a table of eight family claims and one verdict needed
exactly one of them. Checking the other seven:

    5 of 8 direction counts reconcile.  3 are wrong, each by exactly one.
    8 of 8 id lists are right.

So the table is reliable for WHICH ROWS are in a family and only 5-of-8
reliable for HOW MANY read and write -- and the verdict happened to need the id
list for its exclusion and a direction count that was among the five. **Leaning
on the direction count alone would have been one wrong claim from a wrong
verdict, with nothing to signal it.** The same method priced two other sources
the same hour: `scripts/_probe_jobs_tail_boundary.py` transcribes three row
ranges, the two checkable ones land on the published count exactly and the
third -- the contested one -- over-names by one; and `linkedin_server/menus.py`
groups menu terms under blocker-named headings whose sizes are 10/7/2/1 against
published 10/2/1/4, which is why membership there was reported as necessary and
not sufficient.

### 21.6 DISPOSABLE, declared

Nothing from this wave is disposable. All four scripts are committed under
`scripts/` and all four carry controls.

## 22 THE IMPACT GATE, AND THE THREE MUTATIONS THAT KILL IT

`scripts/impact_gate.py` -- selects the tests a change can break, runs exactly
those plus a corpus-wide floor, and prints what it did NOT run.
Control: `tests/test_impact_gate_selects_data_dependencies.py`, 13 tests.

**WHY IT IS ADMITTED.** A selector is the hardest thing in this repository to
red-proof, because the two ways it can be broken look identical from outside:
one that returns EVERYTHING never refuses, one that returns NOTHING never
fires, and both print calmly. So every rule in it is disarmable by keyword and
the control asserts BOTH arms of each.

### 22.1 THE MUTATION THAT KILLS IT, run 2026-09-20

    scripts/impact_gate.py   data_coupling: bool = True  ->  False

    3 failed, 10 passed in 4.37s
      test_the_census_ledger_selects_the_test_that_caught_it
      test_the_census_evidence_table_selects_it_too
      test_the_selection_travels_the_two_hop_chain_and_not_a_coincidence

Restored, `diff -q` clean, 13 passed in 10.9s. The negative arm
(`test_reverting_the_data_rule_loses_the_test_again`) runs the disarmed
selector on every CI cycle and asserts it reaches NOTHING -- so a selector
rewritten to return the whole suite reddens the negative arm, and one rewritten
to return nothing reddens the positive arms. There is no broken selector that
passes both.

### 22.2 THE DEFECT IT EXISTS FOR, reproduced before it was built

Staging the reverse of `5d0efb5` -- the `**CORRECTED BY:**` marker that split a
table `scripts/build_blocker_map.py` parses -- and putting it to the existing
`scripts/pre_commit_boundary_gate.py`:

    boundary gate:  exit 0, ZERO bytes of output, ZERO tests run
    truth:          tests/test_blocker_map_is_derived.py, 2 failed in 1.16s

`staged_paths()` keeps only `*.py`, so a `.md` never reaches the coupling rule;
and a data file defines no module-level constants, so reaching it would not
help. **A document that is also a DATA SOURCE is read by a PATH, and a path is
not a name.** The finished gate refuses the same tree in 25.7s, naming three
failures. `test_the_shipped_constant_rule_is_still_blind_to_this` pins the old
rule's blindness so a later simplification back onto it cannot be quiet.

### 22.3 PROSE IS NOT DEPENDENCY -- the calibration, with its numbers

Scanning RAW source for the ledger's name selected **158 of 170** test files;
making the text edge non-transitive took it to 93; three precision fixes took
it to 4, each found by checking a sample rather than by reasoning:

    strip comments + docstrings (tokenize + AST)      93 -> 9
      cause: readonly.py:2045 cites it in a # comment,
             server.py:185 quotes it in a docstring. Neither opens it.
    directory token requires a SWEEP VERB              9 -> 5
      cause: repo_paths.py holds Path("_audit") / "_sanitisation_key.json",
             naming the folder to reach ONE file in it.
    drop bare \bwalk\b, spell it os.walk               5 -> 4
      cause: it matched ast.walk, which traverses a syntax tree
             and no directory at all.

A selector returning 93% of the tree is not selecting; it is laundering a full
run through a narrowing story, which is worse than an honest full run because
it claims to have reasoned.

### 22.4 THE CORPUS-WIDE FLOOR, and the check it nearly disarmed

`always_run_files()` derives the tests whose file enumeration takes no input
from the diff -- `git ls-files`, a repo-root walk, or a sweep spanning two or
more top-level folders. 13 files, 1797 tests, 25.6s. They are coupled to
EVERYTHING and therefore selectable by nothing, so they run unconditionally.
Derived rather than listed, and
`test_the_floor_is_derived_and_still_finds_the_two_proven_guards` fails by name
if the detector ever narrows past `test_no_committed_identity.py` or
`test_page_text_is_never_printed.py`.

**THE TRAP, RECORDED BECAUSE IT IS THIS REGISTER'S OWN DISEASE.** The floor is
never empty. Had the plan been one merged list, the gate's "empty impact set"
alarm could never have fired again -- permanently satisfied by a guarantee that
says nothing about whether the analyser worked. A check that cannot fail,
introduced by the change meant to make the gate safer, and invisible because
everything stays green. `Impact.selected` and `Impact.always_run` are separate
fields, the alarm tests `selected`, and
`test_the_floor_does_not_mask_an_empty_selection` asserts it.

### 22.5 THE GUARD THAT CONVICTED THE GATE'S OWN AUTHOR

First dogfood run -- the gate applied to its own staged change -- came back RED:

    tests/test_an_outage_is_never_filed_as_an_absence.py
      ::test_no_probe_returns_a_falsy_datum_from_an_exception_handler
      impact_gate.py:225

`code_text()` returned `""` from an `except OSError`. Empty string means "this
file mentions nothing"; unreadable means "unknown" -- the same value to every
caller, so an I/O error would have silently REMOVED a candidate from the plan.
That is the exact failure the gate exists to prevent, reproduced inside the
gate, found by the suite rather than by its author. Repaired by taking the
remedy the guard itself named -- `None`, and widen at the call site -- rather
than the one that clears the red.

### 22.6 DISPOSABLE, declared

Nothing. `scripts/impact_gate.py` is committed with its control, and
`scripts/impact_gate_suite_size.json` is a cached denominator stamped with the
commit it was taken at, so its staleness is visible rather than assumed. The
probe used to size the floor was a scratch file and IS disposable; its result
is the derivation in `always_run_files()`, which is checked by 22.4.

## 23. THE NEWSLETTER BUILD WAVE, 2026-09-20

### 23.1 `scripts/_probe_newsletter_surface_shape.py` -- READ THE CAPTURE AGAIN

**THE PATTERN, AND IT IS THE ENTRY'S REAL SUBJECT: A LIVE RUN'S CAPTURE
ANSWERS MORE QUESTIONS THAN THE RUN ASKED, AND RE-READING IT COSTS NOTHING.**

`scripts/_probe_newsletter_subscriptions_live.py` opened the newsletters
manager on 2026-09-05, wrote FOUR questions into its own header, answered two,
and left two open. Those two sat open for fifteen days -- behind a page load
that had already been paid for, on an account where the load is the expensive
part. This probe answers both offline, in seconds, with no browser, no network
and no counter of anybody's spent.

Generalised: **before costing a live read, ask whether a capture on disk
already holds the answer.** This repository gitignores its captures precisely
because they are made of other people's publications, which makes them easy to
forget and cheap to re-interrogate.

### 23.2 THE PATH REDUCER THAT INVERTS THE ALLOWLIST

The sibling `_probe_events_surface_shape.py` reduces a path by replacing the
segment AFTER a known keyword. That leaves a segment somewhere the author did
not anticipate surviving verbatim.

This one inverts it: `shape.census_substitute` runs first (so the placeholders
this repository authors survive as themselves), then **EVERY segment outside a
closed product vocabulary becomes `<seg>`.** A surviving identifier stops being
unlikely and becomes impossible. Cost: an unfamiliar product word reads as
`<seg>` until somebody adds it, which is the safe direction.

### 23.3 THE CONTROLS, AND ONE OF THEM IS THE WHOLE FINDING

The findings here are ZEROS -- no analytics route, no subscribe control, no
unsubscribe control -- and **a zero out of a broken matcher is
indistinguishable from a zero out of a page.** So:

* `--control` runs the identical word census over a synthetic document that
  DOES carry every finding word and requires each to be NAMED. Without it a
  zero here is not a measurement, and the script says so in its own output:
  *"A zero above is a measurement ONLY if --control passes."*
* The reducer is shown CHANGING a person-shaped slug. The needle is READ OUT
  OF THE TRACKED FIXTURE at run time rather than pasted, so no new invented
  person enters the tree and the control follows the corpus. A missing needle
  is a VOID, not a skip.
* CROSS-INSTRUMENT AGREEMENT: the newsletter-anchor total must equal the 10
  that `newsletters.read_newsletter_subscriptions` measured through Playwright
  on the same page. A regex and a DOM walk are different instruments, so
  agreement is evidence and disagreement VOIDS every tally below it.
* An impossible attribute must stay at zero -- **AND VOIDS THE RUN WHEN IT
  DOES NOT, which the first draft did not do.** That draft printed `FAIL` and
  then printed every tally below it with exit 0: a check that announces its
  own failure and certifies anyway, which is WORSE than not having it, because
  the word FAIL ends up four screens above a table that reads as data. Found
  by planting a matcher that cannot stay silent and running it, not by reading
  the code. **`scripts/_probe_events_surface_shape.py` has the identical shape
  and the identical gap** -- measured, its `silent` result is printed and never
  branched on -- and it is NAMED here rather than edited, because it is another
  wave's instrument and a one-line fix with the evidence attached is cheaper
  for its owner than a surprise in their diff.
* **AN ABSENT CAPTURE RETURNS 2 AND PRINTS NOTHING READABLE AS A TALLY.** A
  linked worktree carries no gitignored files, so this script run from one
  finds nothing, and an absence reported as a zero would have said *the page
  draws no analytics* about a file that was not there.

### 23.4 PRESENCE IS NOT A SIGNAL; THE ENCLOSING CONTAINER IS

Every needle is reported with its LANDMARK STACK -- tag names only, which name
nobody. That is what separated a create route that is the section's own header
action from one that would have been global chrome, and it is the difference
between an account-specific eligibility fact and a string every member sees.
The shipped reader inherits it: `newsletters.CREATE_SELECTOR` is scoped to
`main` and the document-wide count ships BESIDE it so the two can be seen
diverging.

**AND THE FIXTURE CARRIES THE DECOY THAT MAKES THAT ASSERTION REAL.** A second
create route outside `main`, which the live page does not draw -- the same
deliberate divergence as its eleventh anchor. `test_the_naive_document_wide_
selector_is_shown_getting_it_wrong` installs the obvious wrong implementation
by monkeypatch and measures it reporting 2/0 against the shipped 1/1. The
mutation is planted and fired, not described in a comment.

### 23.5 A LOCATOR THAT CAN MATCH DOCUMENTATION IS NOT LOCATING MARKUP

Caught on its own first run. `test_the_fixture_draws_the_create_route_twice_
and_only_one_is_in_main` located `<main>` with a bare `find` over the fixture
source -- and the fixture's own HEADER COMMENT, amended in the same commit,
names the `<main>` wrapper in prose. The locator hit the explanation, put the
decoy on the wrong side of the tag, and the test went red with a coordinate
triple that made no sense until the comment was read. Fixed by stripping HTML
comments before locating. **Any assertion that searches a fixture's SOURCE
rather than its DOM is searching its documentation too.**

### 23.6 DISPOSABLE, declared

Three scratch scripts in the session scratchpad -- an href tally, an element
and vocabulary census, and a landmark-stack locator for one word. All three are
superseded by the committed probe, which does what they did with controls.
Their results are the numbers in `_audit/2026-09-20-newsletter-built.md` and in
the probe's own output.

## 24 · THE LIVE-CAPTURE WAVE, 2026-09-20

`scripts/_probe_premium_surfaces_shape.py`. Six Premium-bearing surfaces,
captured live to `_state/` once and re-readable offline for ever. Five
controls, **each driven into its failing state in-process and each returning
non-zero**, then passing again afterwards.

### 24.1 A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE

**The finding that would have inverted this wave's headline answer.** Three of
the six captures are about 1.4 MB and over 99 percent of that is the Ember
bundle, the i18n dictionaries and the lix blob -- rendered text is 0.2 to 2.5
percent of the document. Counting `inmail` over the RAW document returns 16 to
21 on three surfaces and **0 on all six** once `<script>`, `<style>` and
LinkedIn's `<code>` model payloads are stripped.

The first census here counted raw, and would have reported an InMail balance
present on three surfaces -- the exact opposite of the truth, on the one census
row the operator had asked about directly, with a number attached to make it
look measured. **Both counts now ship side by side, because the gap between
them is the finding.** The control: a needle repeated 400 times inside a
`<script>`, plus a drawn word that must survive; disarming `STRIPPED_TAGS`
voids the run.

### 24.2 A BUDGET-SHAPED REDUCER RULE LETS A PROFILE SLUG THROUGH

**Found by reading my own stdout, not my own code.** The reducer's first
version replaced a path segment only when it was LONG or DIGIT-BEARING. A
profile slug is neither, so `/in/<a real person>` printed verbatim -- a third
party's, and the operator's own -- into a terminal, off captures of his own
pages.

**A length-and-digit rule is a budget, and a budget is not a rule about WHERE
a match may land.** The rule that works is positional and unconditional: the
segment AFTER a member-bearing prefix (`in`, `company`, `school`,
`newsletters`, `pub`, `profile`, `organization`, `groups`, `showcase`) is
replaced whatever it looks like. Control 3 is built from that failure and
reproduces it on demand: reverting to the old rule reports **3 of 4 inputs
leaked** and voids the run. Nothing reached a tracked file; the captures that
carry names are gitignored and stayed there.

### 24.3 A ZERO NEEDS A NON-ZERO BESIDE IT, AND A VERDICT NEEDS A SECOND VERDICT

Two controls of the same shape. The census control names 19 needles on a
synthetic document carrying all of them, so a zero on a real page is a
reading; blinding `visible_text` voids it. The lix control puts a two-flag
blob carrying `enabled` and `control` to the treatment parser and requires it
to distinguish them -- because the wave's headline flag reads `control`, and a
parser that can only ever emit one value would say exactly that on any input.
Across the real capture it parses **376 flags spanning 26 distinct
treatments**, which is what makes the one `control` a measurement.

### 24.4 AN ABSENCE IS NOT A ZERO, AND IT EXITS 2

`_state/` carries no files in a linked worktree. A run that cannot find the
captures prints what is missing and **exits 2 without tallying anything** --
driven by pointing it at a nonexistent directory. These documents embed a
member urn inside the lix `trackingInfo` blob, measured, which is the concrete
reason they may never be committed rather than a general caution.

### 24.5 A GUARD THAT READS A DIRECTORY AS A FILE

Not this wave's instrument, and found by running the gate rather than reading
it. `committable_files()` in `tests/test_no_committed_credential.py` sweeps
tracked PLUS untracked-not-ignored, which is right. But git reports an
embedded repository as a single DIRECTORY entry, and 23 Claude Code agent
worktrees under `.claude/worktrees/` therefore arrived as 22 directories that
were handed to `read_text()`. **22 reds on a tree whose own diff was clean,
blocking every wave on the box.** Repaired at the INPUT -- `.claude/worktrees/`
ignored and declared `LOCAL_STATE` -- rather than by teaching the guard to
tolerate a directory, because the directory never belonged in the swept set.

### 24.6 STILL CANNOT FAIL, AND IT IS NOT MINE

**SUPERSEDED BY SECTION 27, AND THE SUPERSESSION IS THE LESSON.** I wrote
that `scripts/_probe_events_surface_shape.py`'s must-stay-silent control was
printed and never branched on, still unfixed at `8b58dcb`, and noted this was
**the second register entry to name it by hand**.

It was fixed in `2fba253`, and section 27 then did the thing neither naming
did: it COUNTED the shape. **56 of 88 probe files, 129 of 762 control-like
readings never branched.** Two hand-written paragraphs found one instance;
one census found 129. **When a defect turns up a second time, that is the
signal to count it, not to report it again.**

### 24.7 DISPOSABLE, declared

Four scratchpad scripts: a banking MCP client that writes a tool's payload to
`_state/` and prints only a shape, a six-page capture driver, and two
role-play probes (the second re-reading the first's address at three settle
depths). Their results are the numbers in
`_audit/2026-09-20-the-live-capture.md`. The capture driver's job is done --
the captures it wrote are on disk and the committed probe reads them.

## 25. THE SURFACE-CLASS ADJUDICATION, 2026-09-20

Appended, not inserted -- see this file's preamble; find these by NAME.

One instrument, `scripts/classify_surface_blockers.py`, with
`tests/test_surface_class_is_derived.py` (13 tests). Full write-up in
`_audit/2026-09-20-the-surface-class.md`.

### 25.1 `classify_surface_blockers` -- a membership rule that RUNS

**WHY IT EXISTS.** `_audit/2026-09-20-the-contingent-writeoffs.md` s3.1
published a class named `SURFACE?` at 22 blockers / 139 rows / 108 GAP. The
classifier was never committed and its three inputs are gitignored and gone,
so the membership survives only as three integers -- and **186,629,988,917,605
distinct 22-blocker subsets of the residual pool fit them exactly.** The same
defect `build_blocker_map.py` exists to end, one level up.

**SHOWN FAILING in five directions**, each planted against a COPY of the ledger
in the scratchpad with the module's `LEDGER`/`MAP` constants repointed, so
nothing tracked was touched:

    ranked table header broken        every boundary cell reads as absent
    cost-0 table header broken        its blockers read as missing entirely
    one ranked row deleted            97/409 stops closing
    SURFACE blocker in neither table  a map/ledger membership disagreement
    boundary cell IS a surface fact   headline count must move 0 -> 1

### 25.2 `A-ZERO-FROM-A-BRANCH-THAT-CANNOT-FIRE` -- the mutation that matters

The wave's headline is a ZERO: none of the 26 blockers is blocked by a surface
fact. **A zero is the most dangerous shape a finding can take**, because a
branch that never fires and a branch that fires and finds nothing print the
same character. `test_the_surface_fact_branch_can_fire` plants a boundary cell
reading "LinkedIn draws no such page" and REQUIRES the count to become 1 and
the blocker to be named.

It earned its place twice over: the red-proof harness itself reported
`*** DEAD BRANCH` on its first run because it built the planted ledger and
never passed it, then failed again asserting `"surface fact: 1"` against a
program that prints `"SURFACE fact: 1"`. **Both defects were in the checker,
not the checked.** A mutation of the classifier (`return "SURFACE-FACT"` ->
`"NONE-STATED"`) turns exactly this one test red and leaves the other twelve
green, which is what a discriminating guard looks like.

### 25.3 `A-HAND-WRITTEN-LOOKUP-NEEDS-A-DUPLICATE-CONTROL`

`SURFACE_ADDRESSES` maps each blocker to a candidate base address, checked
against the live boundary. It is hand-written, so a copy-paste puts one
blocker's address on another and the report then prints a verdict for a page
that blocker has nothing to do with. **That is not hypothetical: it shipped.**
`CREATOR-HUB-SURFACE` was given the identical address as its sibling
`CONTENT-ANALYTICS-SURFACE` and was counted into a headline on the strength of
it -- caught by an evidence sweep reading a 2026-09-19 document, not by the
author.

`test_no_two_blockers_share_a_base_address_undeclared`. A shared address is not
banned -- `/messaging/` genuinely draws three of these surfaces -- it must be
DECLARED, which turns a silent copy-paste into a statement somebody wrote down.
The guard ALSO fails when the declaration drifts from the table, because a
stale declaration launders a real duplicate. **SHOWN FAILING** by re-inserting
the original bug:

    AssertionError: these base addresses are shared by more than one blocker
    without being declared in DELIBERATE_SHARES, so at least one of them is
    reporting a verdict for a page it does not own:
    {'/analytics/creator/content/': ['CONTENT-ANALYTICS-SURFACE',
                                     'CREATOR-HUB-SURFACE']}

**The general form, worth copying:** any lookup table a human types, whose
entries are compared against a live system, needs a control that the entries
are DISTINCT unless distinctness was deliberately waived. Without it a
duplicate is indistinguishable from a measurement.

### 25.4 `REFUSED-IS-NOT-ABSENT`, and its sharper twin `ALLOWED-AND-STILL-WRONG`

The converse of s9.1's standing ALLOWED IS NOT SERVED, and the reason this
wave banked zero rows. A probe that runs candidate URLs through
`readonly.assert_read_url` and reports them refused has measured OUR GATE, not
LinkedIn. Filing such a refusal as a surface absence writes a fact about this
repository into the census as a fact about the world.

**And the twin, measured in-class on `JOB-ALERTS-SURFACE`:** `/jobs/alerts/` is
ALLOWED by the boundary and LinkedIn **redirects away from it, twice
reproducibly with a control serving correctly at both ends of the session**. So
a pattern can be ALLOWED-AND-STILL-WRONG -- matching nothing LinkedIn resolves
to -- and a naive `is_read_url` check reports the row addressable when the one
live test on record says the address does not serve.

**THE CROSS-INSTRUMENT CONTROL THIS IMPLIES**, and it is cheap:
`test_the_two_boundary_entry_points_agree_on_every_candidate` asserts
`is_read_url` and `assert_read_url` return the same verdict for all 26
addresses (measured: 0 disagreements). The classifier asks the predicate; a
capture calls the asserting form. If they ever diverge, "reachable for a
capture" stops being well defined and every number built on it is ambiguous.

### 25.5 A TOOL THIS WAVE MEASURED AND DID NOT WRITE -- `find_blocker_reason`

Not an entry for this register's usual purpose; a WARNING about one already in
it. Measured across the 26 SURFACE blockers: **286 mentions, 93 ranked, 193
blind (67.5%)**. A fixed-seed sample of 51 blind mentions read in context came
back **42 substantive / 9 incidental**.

**THE MECHANISM: a document that argues by CENSUS ROW ID -- this campaign's own
convention -- instead of repeating the blocker's compound name is nearly
invisible to a same-line co-occurrence test.** All three flagship
`SEARCH-RESULTS-SURFACE` admission documents and both 2026-09-20 build-wave
reports are blind for their own blocker. Precision is fine (18 of 19 top-ranked
non-census documents substantive); **recall is the defect**. Its silence is
UNKNOWN, never absence, and no `reason_doc` column may be derived from it.

### 25.6 DISPOSABLE, declared

A subset-counting script (the 1.87e14 figure), a fixture-corpus path-family
tally, and the standalone red-proof harness. The first two produced numbers now
quoted in the wave document; the third is superseded by the committed test
file, which plants the same five defects and is re-runnable in CI.

### 25.7 `A-WATCHER-THAT-EXITS-ZERO-WHEN-IT-NEVER-SAW-A-VERDICT`

**Found 2026-09-20 in the CI-reporting path every wave uses.** Not a test: the
command waves run to decide whether to report a run green.

`gh run watch <id> --exit-status` is documented to exit non-zero when the run
fails. **It also exits ZERO when it never learns the run's conclusion at all.**
Four watches in this wave returned exit code 0 and their transcripts end:

    * every shard reported (ID 106027531906)
    failed to get run: HTTP 403: API rate limit exceeded for user ID ...
    [exited with code 0]

The watcher polled, lost the API to a fleet-wide 403 (5,000/hr is shared across
every tool and agent, and several waves were pushing at once), gave up, and
**reported success by exiting 0**. Four background tasks then notified
"completed (exit code 0)", which reads exactly like four green runs.

**THE SHAPE IS THIS REPOSITORY'S OWN STANDING RULE, arriving from outside the
codebase:** verify by ARTIFACT, never by exit code, because a loop that
exhausts its attempts exits 0. It has been written here about retry loops. It
is equally true of a WATCHER, and a watcher is more dangerous because its exit
code is the only thing a notification carries.

**THE CHECK, and it costs one command.** Never report a conclusion from the
watcher's exit code. Read the conclusion back:

    gh run view <id> --json status,conclusion,headSha

and if THAT call fails, the run's state is UNKNOWN -- which is a different
answer from green and must be reported as such. A rate-limited query is an
outage, not a measurement: this is the same law as
`A-BLIND-CHANNEL-MUST-NOT-REPORT-A-CLEAN-ABSENCE` (s2.2), and the same one a
memory in this project already records -- a probe with no `except` turns an
infrastructure outage into a finding about the platform.

**WHAT IT COST HERE: nothing, because the exit codes were disbelieved** and the
run list had already been read as an artifact for the two commits that matter.
Recorded so the next wave does not spend the discovery again, and so that
"exit code 0" never again appears in a wave report as evidence of a green CI.

**A SECOND-ORDER NOTE WORTH HAVING.** `gh api rate_limit` reported
`core: 5000/5000, used 0` while `gh run list` and `gh run view` both returned
403 in the same minute. **The bucket that is exhausted is not the bucket that
endpoint reports**, so "rate_limit says we are fine" does not license a retry.
Treat the 403 itself as the measurement.

## 26. THE THIRD CAUSE, AND A CONTROL THAT PASSED WHILE ITS REPORT LIED, 2026-09-20

### 26.1 `scripts/_check_published_split.py` -- it printed two words for two unrelated situations

The report classified nothing. It printed `OVER on R` for a blocker whose
surplus was four rows that ARRIVED on committed re-files, and `OVER on R` for a
blocker where nothing had arrived, nothing was missing, and the count closed
exactly. Its docstring named two causes -- a row LOST, a row RE-FILED OUT --
and both describe movement AFTER publication. **The third is an error AT
publication, and a report that cannot show it will have its one instance read
as one of the other two.**

**THE LAW: A CAUSE THE INSTRUMENT CANNOT NAME GETS ATTRIBUTED TO THE NEAREST
CAUSE IT CAN.** That is not a gap in coverage, it is a manufactured wrong
answer, and it is the same shape as a line-number citation rotting into a
plausible one rather than a dangling one.

**THE DISCRIMINATOR WAS ALREADY WRITTEN, ONE FILE AWAY, AND NOBODY CALLED IT.**
`_check_refile_destination_credit.publishers()` (register 21.2) knows which
rows arrived from elsewhere. Subtracting their directions from `held` separates
the causes in three lines:

    RE-FILED-IN   the over-run vanishes once arrivals are subtracted
    LOST          own rows fall short of the published total
    AT-BIRTH      count COMPLETE, nothing incoming, and STILL over

No new instrument was written. The import was the whole fix, which is the
second time in this register that the answer was to call a shipped tool rather
than build a cousin of it.

**WHAT IT CONVICTED, and the arithmetic is the conviction rather than the
verdict:** `NEWSLETTER-SURFACE` published `1R/11W` over twelve rows while the
whole newsletter family in the frozen 409 holds **ten** writes. Eleven writes
do not exist, so no subset, no re-file and no lost row could ever have produced
that cell. The read-side version of the same argument -- every 12-subset of the
thirteen holds at least two reads -- is weaker, because it depends on which
twelve were chosen. **A supply argument beats a subset argument: one of them
has to know which rows were picked and the other does not.**

### 26.2 THE CONTROL WAS SHOWN FAILING, AND ONE OF THE MUTATIONS CONVICTED THE CONTROL

Three mutations, each applied in-process and reverted, each required to turn a
control red:

| mutation | `--control` (pre-existing) | `--control-causes` (new) |
|---|---|---|
| classifier returns one word always | exit 0, BLIND | exit 1, 2 of 3 WRONG |
| `_incoming()` stubbed to `{}` | n/a | exit 1, `DEAD, the subtraction reaches nothing` |
| clean-victim pool starved | n/a | exit 2, REFUSES to inject |

**THE SECOND ROW IS THIS ENTRY'S REASON FOR EXISTING, BECAUSE ON ITS FIRST
VERSION IT READ EXIT 0.** With the incoming derivation stubbed dead, all three
injected cases still classified correctly -- while the report four lines above
called `SEARCH-RESULTS-SURFACE` AT-BIRTH, the one verdict reserved for a
published figure that was wrong when written, handed to a blocker whose surplus
is four documented arrivals.

**THE LAW: A CONTROL THAT SUPPLIES THE INPUT WHOSE DERIVATION IT PROTECTS
CERTIFIES AN INSTRUMENT THAT IS ALREADY LYING.** The RE-FILED-IN injection
planted its own arrival into the table, so it exercised the classifier's LOGIC
and never its INPUT. Repaired with a derivation-liveness assertion -- arrivals
derived from `publishers()` must equal the `RE_FILED` row count and must not be
zero:

    HEALTHY            arrivals 5 against 5 RE_FILED rows -- LIVE       exit 0
    _incoming STUBBED  arrivals 0 against 5 RE_FILED rows -- DEAD       exit 1

The victim-selection guard is register 21.1's lesson applied with the sign
flipped: injecting a CLASS into a blocker the report already names would
compare the injected class against the real one and read as a
misclassification, so the victims are chosen from an asserted-clean pool and
the control REFUSES rather than injecting anywhere when fewer than three exist.

### 26.3 `scripts/_check_jobs_range_directions.py` -- it widened the COVERAGE and dropped the READING

This file exists to show the twenty blockers the split check SKIPS. It already
imported that check. It still printed a bare `OVER on R` for
`COMPANY-PAGE-SURFACE` -- the third known over-run and the ONLY one the narrow
report cannot see at all -- while the sibling one import away had just learned
to say which of three causes it was.

**THE LAW: WIDENING WHAT AN INSTRUMENT CAN SEE IS NOT THE SAME AS WIDENING
WHAT IT CAN SAY, AND THE SECOND IS THE ONE A READER USES.** A report that
reaches further and reports more coarsely has moved a blind spot rather than
closed one -- and the blocker only this report can see was the one getting the
coarsest verdict available.

One import later the whole known set is named, and the third answer is new:

    SEARCH-RESULTS-SURFACE   RE-FILED-IN   four rows arrived on committed re-files
    NEWSLETTER-SURFACE       AT-BIRTH      corrected in the ledger, 24.1
    COMPANY-PAGE-SURFACE     LOST          own 16 against a published 18

**AND TWO INSTRUMENTS THAT DO NOT KNOW ABOUT EACH OTHER AGREE ON IT.**
`_check_open_slots.py` independently lists `COMPANY-PAGE-SURFACE` with 2
FILLABLE slots -- slots whose row is neither re-filed nor a ruled phantom, i.e.
rows genuinely missing. `LOST` is the same fact reached from the direction
column instead of the slot table. A verdict two unrelated parses produce is
worth more than a verdict one produces twice.

**THE NEW ASSERTION, SHOWN FAILING.** `--control-overrun` already required the
table to NAME an injected over-run; it now also requires the CAUSE to read
`OVER-COUNT`, which is the only honest verdict for a blocker holding 99 more
rows than it published. Stub the classifier to one word and it reads
`expected OVER-COUNT, got RE-FILED-IN -- WRONG`, exit 1. Healthy: plain,
`--control-blind` and `--control-overrun` all exit 0.

**AND THE GAP IN IT IS STATED HERE RATHER THAN DISCOVERED LATER.** Dropping
the incoming subtraction does NOT move this control: its victim has no
incoming rows and neither does `COMPANY-PAGE-SURFACE`. That mutation is caught
by the sibling's derivation-liveness assertion (24.2), where the derivation
lives. **A control that cannot fail for a given defect should say which file
catches that defect, not imply it catches everything beside it.** Building a
second copy here would have been the cheaper-feeling move and would have
produced two controls testing one thing.

### 26.4 DISPOSABLE, declared

Five scratch scripts in the session scratchpad: the 13/3R-10W re-measurement at
three refs, the whole-line needle widener, the partition-closure arithmetic,
the incoming-subtraction prototype, and the ledger red-reproduction that
repoints `build_blocker_map.LEDGER` at an edited copy. The first two are
superseded by the shipped `scripts/_sweep_frozen_rows.py newsletter`, which was
used as the cross-instrument control and agrees exactly. The third is
superseded by the shipped `scripts/_check_open_slots.py`, whose open-slot table
answers the same question directly. The fourth shipped, as the import in 24.1.
**The fifth is the only one worth re-deriving and the technique is two lines**
-- `bbm.LEDGER = <a copy>` prices a ledger edit against every shipped assertion
without touching a tracked file, and it is how the option of ruling the two
handed-over defects together was costed before it was declined. Their results
are in `_audit/2026-09-20-the-split-ruling.md`.

## 27. `scripts/detect_unbranched_probe_controls.py` -- 129 controls that print FAIL and certify anyway, 2026-09-20

### 27.1 THE CENSUS, AND WHY IT IS A DIFFERENT CLASS FROM A SINGLE FIX

Section 23.3 already named one instance of this defect by hand:
`scripts/_probe_events_surface_shape.py`'s `silent` control, printed and never
branched on, fixed in commit `2fba253`. This entry is what happened when the
same shape was asked to be COUNTED rather than described: an AST-based census
over every `scripts/_probe_*.py` file, run under a wave lead by an implementer
who reported the number rather than the feeling. Full write-up:
`_audit/2026-09-20-control-census.md`.

**56 of 88 probe files carried at least one never-branched control. At the
instance level: 129 of 762 control-like readings never branch (17%), 630
branch correctly, and 13 more are assigned and never even read.** Both
denominators matter and neither alone is honest: the file count alone reads
as "most of the corpus is broken" (it repeats a claim the census's own author
first put to the operator before re-deriving the instance share), and the
instance count alone hides that the defect concentrates rather than
spreading evenly (distribution is in the write-up).

**Independently replicated**, same detector, main tree, by the wave lead:
`with_finding=56` exactly. The one-file, one-instance delta (89 files, 130
instances there against 88/129 here) is `scripts/_probe_premium_surfaces_
shape.py`, an untracked probe a live browser wave was writing at the moment
of the run -- the tool's own drift check named it.

### 27.2 THE CONTROL PAIR: SAME FILE, TWO SHAS, OPPOSITE VERDICTS

A single calibration file is a check that cannot fail if nobody re-derives it
against what actually changed. `scripts/_probe_events_surface_shape.py` was
the working calibration target mid-census -- until it was independently fixed
(the same repair section 23.3 had already named) WHILE the census was
running, in the SAME shared worktree. That turned the textbook positive into
a negative between one read and the next, which is precisely the shown-
failing proof this register asks for, arriving uninvited: the wave lead's
ruling was to keep the ORIGINAL committed shape as a frozen synthetic
positive and pair it with the repaired shape as a discrimination control --
same file, same variable, two shas, opposite verdicts, proving the detector
reads content rather than asserting a fixed answer. That pair is now
permanent, as inline fixtures (not a git reference, which would eventually
stop meaning anything once the real file changes again) in
`tests/test_probe_controls_are_never_decorative.py`.

Receipt, `scripts/_check_unbranched_control_detector_can_fail.py`, run
2026-09-20:

```
A/B. same shape, one branch apart -- must flip verdict
PASS   A: broken fixture flags `silent`
PASS   B: fixed fixture does NOT flag `silent`
PASS   B: fixed fixture's `silent` reads as correctly branched

C. an `if` beside the print that tests a DIFFERENT variable
PASS   C: `hits` is still flagged despite the nearby `if needle == ...`

D. the ratchet itself must be able to go RED
PASS   D: removing one real baseline entry (('_probe_add_section_menu.py', 'main', 'controls')) from view makes the ratchet report it as new
PASS   D control: with the FULL baseline, that entry is NOT reported

all demonstrations behaved as stated
```

Demonstration C is the sharper of the two shapes this instrument has to
tell apart, and it is the one a cheaper check would get wrong: an `if`
sits in the SAME loop body as the print, one line away, and it is still not
a branch on the printed variable, because it tests `needle` rather than
`hits`. A detector that credits any nearby `if` as covering any nearby
variable would have cleared this and every row like it.

### 27.3 A RATCHET, NOT AN EXACT PIN -- AND WHY THIS REPO'S OWN IDIOM WAS REJECTED

`scripts/_check_tool_count_pin_control.py` (section unlisted, but its
receipt is the model this entry followed most closely) pins an EXACT
count and forces a review moment on every bump. That idiom was considered
and rejected here on purpose: this corpus gains new probe files from
unrelated waves most days (24.1's replication found one mid-flight), so an
exact global count would fail as often on someone else's unrelated
addition as on a real regression, and a guard that cries wolf gets
`--no-verify`d. Instead, `scripts/probe_controls_known_decorative_
baseline.json` pins the 129 findings by `(file, function, variable)` and
`tests/test_probe_controls_are_never_decorative.py::
test_probe_corpus_has_no_new_decorative_control` fails ONLY on a finding
outside that set. Shrinking the baseline as the backlog gets fixed is
invited, not required -- demonstration D above proves the mechanism can
still go red with the real baseline missing a real entry, which is what
makes "not required" different from "cannot detect."

### 27.4 THE FALSE-POSITIVE MECHANISM THIS ENTRY DISCLOSES RATHER THAN HIDES

The marker list (`PASS`, `FAIL`, `CONTROL`, `VOID`, ...) is matched as a
bare case-insensitive substring, exactly as specified when this was built.
Bare `pass` and `void` can embed inside an unrelated word. Measured, not
assumed: a corpus-wide sweep for known embeddings (`passes`, `password`,
`bypass`, `avoid`, ...) found exactly ONE site where this fires --
`scripts/_probe_messaging_menu_enumeration.py`, function
`_report_overlaps`, variables `one` and `overlap_label`, whose only marker
hit is `pass` sitting inside the parameter name `passes: dict` -- **2 of the
129 findings (1.6%), both at this one site, nowhere else in the corpus.** A
stricter word-boundary regex was tried and rejected: it also rejects
legitimate inflections with a trailing letter (plural `controls`), which
would have thrown away a hand-verified TRUE positive
(`scripts/_probe_groups_menu.py`'s `stuck`) to fix a problem that affects
1.6% of findings. Documented in the detector module's own docstring so the
next person who re-tightens the marker rule re-runs the comparison rather
than assuming a boundary regex is free.

### 27.5 WHAT IS SHIPPED, WHAT IS NOT

Shipped (tracked, not disposable): `scripts/detect_unbranched_probe_
controls.py` (the detector, importable), `scripts/probe_controls_known_
decorative_baseline.json` (the 129-entry ratchet baseline),
`tests/test_probe_controls_are_never_decorative.py` (the guard, run on
every test pass), `scripts/_check_unbranched_control_detector_can_fail.py`
(this entry's receipt generator, re-run whenever the detector's marker or
sink logic changes).

DISPOSABLE, declared: the census run's scratch materialization of a frozen
`git stash create` snapshot, its per-file JSON dump, and the cost-ranking
cross-reference script -- all session-scratchpad only, never committed.
Their numbers live on in `_audit/2026-09-20-control-census.md`, which is
the durable artifact; the scratch scripts that produced it are not.

### 27.6 WHAT THE CENSUS COST, RANKED -- FOR THE FIXER, NOT AS A VERDICT

The census does not itself say which of the 129 findings matter. Cross-
referenced against `_audit/_census/*.md`: 5 of the 56 flagged files sit
directly under a census row that is BANKED (moved off GAP on a state such
as `COVERED-PROVEN`), meaning that row's claim was concluded using this
exact probe's output while the probe's own self-check on itself was
decorative. Ranked by that fact, not by finding count alone:

* `scripts/_probe_small_measures_live.py` (5 findings) -- underlies
  `_audit/_census/jobs.md` row 15 (`COVERED-PROVEN`), the "All filters"
  panel, where the row's own evidence text calls this probe "shown failing
  before admission." The irony is the finding: a probe vetted for ITS
  addition can still carry a decorative control on a DIFFERENT variable
  than the one it was vetted on.
* `scripts/_probe_job_collections_live.py` (3 findings) -- underlies
  `_audit/_census/jobs.md` row 42 (`COVERED-PROVEN`), job collections and
  their five groupings.
* `scripts/_probe_creator_content_analytics.py` (2 findings) -- underlies
  `_audit/_census/messaging-and-content.md` row C40 (`COVERED-PROVEN`),
  creator analytics.
* `scripts/_probe_job_search_result_sets.py` (1 finding) -- underlies FIVE
  `_audit/_census/jobs.md` rows at once (9, 11, 12, 13, 14, all
  `COVERED-PROVEN`), the job-search filter parameters, all five citing the
  same instrument and evidence block.
* `scripts/_probe_membership_sections.py` (1 finding, `silent`, the same
  must-stay-silent shape as this entry's own calibration positive) --
  underlies `_audit/_census/network.md` row 162 (`COVERED-CANNOT-DELIVER`).

The other 51 flagged files either sit under a row still marked `GAP` or
`EXCLUDED-RULED` (2 files -- no live claim is banked on them yet), are
named only in a journal write-up rather than a census row (43 files), or
were not found cited anywhere searched (6 files). Full per-file breakdown:
`triage-by-cost.json`, referenced from `_audit/2026-09-20-control-census.md`.
This is not a claim that the 5 banked rows are WRONG -- a decorative
control does not mean the probe's finding was false, only that the probe
never checked whether it could have been. The fixer's cheapest next step is
those 5, because they are the only ones where something already rests on
the answer.

## 28. THE BLOCKER-REASON LOCATOR, MEASURED BEFORE IT WAS BUILT ON, 2026-09-20

### 28.1 `tests/test_the_blocker_reason_locator_states_its_recall.py` -- a recall number, pinned

ADMITTED. Shown failing 10 of 10 against `scripts/find_blocker_reason.py` as of
`8b58dcb`, loaded out of git into a temp file and re-run through the same
assertions. It pins four properties: the one miss a human found by hand, two
recall floors, the exclusion of generated artifacts from candidacy, and -- the
unusual one -- a CEILING on at-rank-1 accuracy that fails if the locator ever
gets good enough that the column's shape should be re-decided.

**THE VALIDATION SET IS THE INSTRUMENT'S WHOLE VALUE, AND IT IS NOT THE TOOL'S
OWN OUTPUT.** It is six blockers a sibling wave's child researched by hand, with
the documents it named in its deliverable before this work began. A tool
evaluated on the cases it found is measuring itself, and every recall number
this repository has published for a locator before now was of that shape.

### 28.2 THE FALSE RED I ALMOST BANKED, and the assertion that now prevents it

The first run of the red harness reported `candidates()` returning **0**
documents for every blocker, which looked like a spectacular confirmation. It
was a harness defect: the old module computes `ROOT` from `__file__`, the
harness had written it to a temp directory, and it was scanning an empty tree.
A zero from a real corpus and a zero from no corpus are the same integer.

The harness now asserts its corpus size before it trusts any result --
`assert len(list(old.AUDIT.rglob("*.md"))) > 100`. **A red is a measurement and
has to be defended exactly as hard as a green**, and a red that agrees with your
hypothesis is the one you will not check.

### 28.3 FOUR DEFECTS IN ONE WORD LIST, AND ONLY ONE WAS "ADD MORE WORDS"

Diagnosed and measured SEPARATELY, because each has a different fix and three of
them are invisible to the obvious remedy:

* **A STEM WRAPPED IN `\b(...)\b` MATCHES NOTHING.** The list was written with
  stems -- `refus`, `measur`, `admit` -- and every one was dead. `measur` matched
  zero occurrences in a corpus carrying "measured" 1910 times. The comment above
  the regex read "deliberately broad"; the regex was the opposite. **A vocabulary
  can be silently empty and still look carefully chosen.**
* **A PHYSICAL LINE IS NOT A UNIT OF ARGUMENT.** Scoring required the needle and
  an argue-word on one line, over a corpus hard-wrapped at 76 columns (mean
  non-blank line 70.6 chars, median 75). It was measuring typography -- and
  DIRECTIONALLY, because a `.tsv` record is one line (mean 544.5) and carried
  every word of a record on the needle's own line.
* **THE GENERATED INDEX WON 59 OF 97 RACES.** The top-ranked "document that
  argues this blocker's reason" was `blocker-map.tsv`, which restates
  assignments and argues nothing -- and is the file the proposed column would be
  written into, making the derivation a fixpoint on its own content. The
  hand-written evidence TSV beside it is deliberately NOT excluded, and the test
  asserts that distinction rather than banning a file extension.
* **THE JOIN KEY WAS WRONG.** The needle was the blocker NAME; this corpus
  argues by census ROW ID. A build report argues at length about `J 40` and
  names its blocker twice in the whole file.

Recall against the hand-built set, 1 of 8 -> 8 of 8 found, 0 of 8 -> 4 of 8 at
rank 1. **The fixes were measured one at a time, and the known-miss case passes
as a CONSEQUENCE of the vocabulary repair rather than as its target** -- which
is the difference between a repair and a tool tuned to its own test.

### 28.4 THE SHAPE A MEASURED RECALL FORCED ON A DERIVED COLUMN

`reason_doc` ships, but it may not carry a bare path: at 4-of-8 at rank 1 a path
in a table cell is a coin flip wearing a fact's clothes, and a table reads as
data rather than as a claim. Every populated cell begins
`CANDIDATE-<rank>-OF-<n> SCORE-<n>`, and a test asserts that no cell is ever a
bare path. **The measurement did not just qualify the column, it specified its
format.**

The fixpoint was verified rather than argued: `--write` twice, byte-identical.

### 28.5 A ROW THAT LOSES ITS ASSIGNMENT IS NOT A ROW THAT WAS DELETED

A control was commissioned on the premise that a union merge had resurrected a
deleted census row. The pickaxe refuted it: exactly one commit ever touched
those row texts and it is the one that created them, and the repository has no
`.gitattributes`, so no union driver was ever configured. What had actually been
removed was the rows' BLOCKER ASSIGNMENT, in a different file, on a different
object. **Two different deletions wearing one sentence.** The refutation was
worth more than the confirmation would have been: it established that no census
row has ever been deleted in this tree, which turned a bookkeeping chore into a
ruling.

### 28.6 DISPOSABLE, declared

Five scratch scripts in the session scratchpad -- a reproduction of the reported
miss, a corpus-geometry and top-candidate census, a three-way mechanism
isolator, a five-variant recall harness, and a row-join A/B. All five are
retired in favour of the committed test, which pins the properties they
discovered. Their numbers are recorded in this wave's own audit document,
`_audit/2026-09-20-the-three-held-defects.md` section 2.

### 28.7 A SAME-DAY PEER REVIEW CAUGHT A REAL GAP: THE RATCHET WAS ONE-WAY

Commit `94e4601` landed on a branch another wave (`_audit/2026-09-20-the-
floor-again.md`) was also writing to, and that wave reviewed it because it
was now theirs to have reviewed. Two findings, addressed here rather than
left standing:

**1. The baseline was a ONE-WAY ratchet; this repository's established
pattern for the identical shape is TWO-WAY.** `tests/test_page_text_is_
never_printed.py`'s `KNOWN_TEXT_SINKS` states its own rule: "asserted as an
EXACT MAPPING, so it cannot rot in either direction: a file that gains a
site fails, and a file that is FIXED also fails until its entry is
corrected. The documentation of a defect may not outlive the defect." The
first cut of `test_probe_corpus_has_no_new_decorative_control` only failed
on GAINED (a new finding outside the baseline); it stayed green forever on
LOST (a baseline entry the detector no longer finds), so a fixed control
could sit in the tracked baseline indefinitely with nothing prompting its
removal. FIXED: the test is renamed `test_probe_corpus_baseline_is_an_
exact_mapping` and now fails on either direction, with GAINED and LOST
reported separately (same message shape as `KNOWN_TEXT_SINKS`'s own test,
deliberately). The corpus-churn concern that motivated the one-way version
in the first place still holds and did not require abandoning the
two-way check: matching is on `(file, function, variable)`, not a global
count, so an unrelated wave's brand-new probe file cannot trip either
direction -- only a change to one of the 129 pinned sites can. Demonstration
E in `scripts/_check_unbranched_control_detector_can_fail.py` now proves the
LOST direction can go red (a fabricated baseline entry is correctly
reported lost), alongside D's original proof that GAINED can. Receipt,
re-run after the fix:

```
D. the ratchet's GAINED direction must be able to go RED
PASS   D: removing one real baseline entry (('_probe_add_section_menu.py', 'main', 'controls')) from view makes the ratchet report it as GAINED
PASS   D control: with the FULL baseline, that entry is NOT reported

E. the ratchet's LOST direction must be able to go RED
PASS   E: adding one FABRICATED baseline entry makes the ratchet report it as LOST
PASS   E control: no REAL baseline entry is reported lost at this moment (if this fails, the corpus moved under this check -- see [])
```

**2. Three of the 129 pinned entries are a live dispute, not a settled
false positive, and this entry does not resolve it.** The review named
`_probe_events_surface_shape.py`'s `rows_with_any` and `note` as "display
values, not controls," and `hits` as "correctly not branched, because the
must-fire control was hoisted above it and IS branched" -- a semantically
equivalent sibling variable already gates the same condition the census's
marker-only rule cannot see. Checked directly rather than taken on trust:
the file's code is UNCHANGED since commit `2fba253` (`git status` clean),
and re-running the detector against it live still returns exactly these
three, mechanically correct under the rule as written (section 24 above and
the census's own section 6 already named "control" as domain-overloaded
vocabulary in this exact corpus -- LinkedIn UI controls and self-check
controls share the one word). Left alone rather than resolved unilaterally:
narrowing the marker vocabulary to tell the two apart is a real, separable
piece of work with its own false-positive/false-negative tradeoff, it was
not this task's brief, and the two-way ratchet built for point 1 means it
is no longer possible for this dispute to be forgotten by default -- it
sits in the baseline, live, until someone with the standing to adjudicate
the marker question does.


## 29 · RECORD THE LANDING URL, NOT THE EXIT CODE (live-capture, 2026-09-20)

Not a new script -- a rule that two measurements forced, and the scratchpad
probes that produced them are declared disposable at the end.

### 29.1 ALLOWED-AND-STILL-WRONG: two specimens in one session

**A load that succeeds at a DIFFERENT ADDRESS is indistinguishable from a load
that succeeded**, to every check that does not compare the landing url against
the requested one.

    requested /jobs/alerts/   ALLOWED by our own gate   ->  landed /jobs/jam
    requested /messaging/     ALLOWED by our own gate   ->  landed /messaging/thread/<id>

Both returned pages. Both would have been scored PASS by anything watching for
an exception or a status code. `/jobs/alerts/` had been admitted since
2026-09-05 with a comment stating in capitals that nobody had opened it, and
its redirect had been measured that day and then **left unnamed for fifteen
days** -- the landing was narrowed to `/jobs/<three characters>` and SIXTEEN
three-letter spellings were enumerated against it. `jam` was not among them.

**ENUMERATING CANDIDATES IS NOT A SUBSTITUTE FOR READING WHERE THE BROWSER
WENT.** The search space looked small enough to guess, which is exactly the
condition under which guessing replaces measuring.

**AND "OUR LIST ADMITS IT" IS A FACT ABOUT OUR LIST.** Whether LinkedIn serves
an address is a fact about LinkedIn, and no amount of reading `readonly.py`
can answer it. Any wave that concludes a surface is reachable because the gate
says ALLOWED has measured its own configuration.

### 29.2 A NEEDLE SET THAT SCORES 0 ON ONE PAGE AND 7 ON ITS SIBLING IS A CONTROL

The compose-toolbar question was put to a ten-word vocabulary -- emoji, gif,
attach, photo, image, file, video, sticker, record, audio -- read off
aria-labels rather than text.

    /messaging/           0 of 10
    /messaging/compose/   7 present, 3 absent, plus 2 file inputs

**The discrimination IS the proof the instrument works**, and it costs nothing
extra because the second page was being loaded anyway. A vocabulary that
returns zero everywhere and a vocabulary that returns hits everywhere are both
broken; one that splits between two sibling pages in the same session is
neither. Prefer a paired reading to a synthetic control whenever a natural
negative page is already in the batch.

### 29.3 SAMPLING THE PAGE LINKEDIN CHOSE IS NOT SEARCHING FOR A STATE

`/messaging/` lands inside one thread. So a row asking *can this server read a
GROUP thread* cannot be answered there at all: what is available is *is the
thread LinkedIn opened a group thread*, which is a different question with a
different denominator. Three conversations were drawn out of an unknown N.

**THREE ANSWERS MUST NOT COLLAPSE INTO EACH OTHER**, and only the third was
true here:

    the surface is absent                      a claim about LinkedIn
    the account holds no instance of it        a claim about this account
    no admitted address can enumerate the set  a claim about US

Banking the first on evidence for the third is how a MEASURED-ABSENT gets
filed on a reading that never had a needle. The blocker was re-aimed to the
third, which wants an ADDRESS rather than a capture.

### 29.4 A SOURCE COUNT IS NOT A PAGE COUNT, ON A THIRD PAGE NOW

Entry 24.1 found this on six captures; `/preload/sharebox/` makes it eight.
The bundle names `draft` **fifteen** times and the page draws it **zero**.
Reported with the caveat that the preload stub has no `<main>` and 763
rendered characters, so the absence is of the STUB and not of the product --
a weaker claim than the number alone would support, and it is the claim made.

### 29.5 DISPOSABLE, declared

Three scratchpad probes: a five-target capture driver, a landing-url namer,
and an offline analyser over the captures. Their results are section 12 of
`_audit/2026-09-20-the-live-capture.md`; the captures they wrote are in
`_state/` and re-readable without them.

---

## 30. The names-that-do-not-exist wave, 2026-09-20

### 30.1 `scripts/check_asserted_names_resolve.py` -- A NAME AN AUDIT DOCUMENT ASSERTS MUST RESOLVE

A citation to something that does not exist does not rot into an obviously
dangling reference. **It rots into a PLAUSIBLE WRONG ANSWER**, which stops the
reader instead of sending them looking. Four separate waves hit that class on
one day and none of them was looking for it.

The hard part is that a document may legitimately name something absent. The
rule was read off the corpus rather than invented: **this corpus already MARKS
its proposals** -- "New blocker:", a "(proposed)" column header, "Re-file as",
"a SPECIFICATION, not a build", a modal, or the document disclosing the absence
itself. The burden of marking is the author's, and an unmarked name in a
referential position is an assertion because a reader has nothing else to go on.

Measured over 166 files / 78,656 lines: precision 1.00 and recall 1.00 on both
kinds, over a COMPLETE census of their decision space rather than a sample --
tools n=4 occurrences, blockers n=234. 4 asserted-and-absent citations, all in
one document. Full workings: `_audit/2026-09-20-names-that-do-not-exist.md`.

### 30.2 A GUARD CAN DISARM ITSELF BY DOCUMENTING ITSELF

**Shown failing in the live tree within an hour, with nothing planted, and CI
reproduced it on three platforms.**

`tool_registry()` shipped scanning raw text of `linkedin_server/`, `scripts/`
and `tests/`. Then the guard was committed -- with a docstring naming its worked
examples and a test planting a control needle. Those strings landed in the
scanned directories, the registry swallowed them, and the next run reported ZERO
absent tool names, with the pin going red in the direction that reads "these
defects were REPAIRED". Nothing had been repaired.

**This is the corpus's own defect one level up: writing ABOUT a name is not the
name existing.** A test's string literal and an audit sentence are the same kind
of thing, and a registry that reads one but not the other draws the line in the
wrong place.

Two candidate fixes were MEASURED AND REJECTED before the third was taken.
Scoping to `linkedin_server/` alone convicts a document for quoting a shipped
`FORBIDDEN_TOOLS` contract; restricting to AST identifiers loses 26 of 72 corpus
tokens, because real tool names live in string literals here. **The defect was
never the extraction technique. It was the scope.**

THE GENERAL FORM, for any guard that resolves names against a tree: **a guard
must not read its own commentary as evidence.** The fix is NOT to rename the
fixtures -- that tunes the test to dodge the bug and leaves production blind.
`test_the_registry_cannot_absorb_a_name_from_its_own_instruments` names the four
exact strings that did it.

### 30.3 A UNION CLAIM OVER A REDUNDANT CORPUS CANNOT SEE A NARROWING

`test_the_table_slot_still_reproduces_the_registry` asserted that all 97 ledger
blockers still appear SOMEWHERE in the slot's output, and its docstring called
that "the whole precision argument for the slot, asserted rather than believed".
A red-proof narrowed the header predicate from a substring test to an exact
match -- removing twelve genuinely blocker-labelled columns -- and **the test
passed cleanly**, twice, on two independent clean baselines. This corpus is
redundant enough that every one of the 97 is also cited elsewhere.

Repaired by exercising the predicate DIRECTLY, a synthetic one-row table per
header spelling through the real code path. The union test is KEPT beside it:
collapse and narrowing are different failures and only one was covered.

**AND THE SAME MUTATION KILLED A SECOND, UNPREDICTED MARKER CLASS.** Its three
corpus examples sat under two of the same header spellings. **A single-selector
red-proof under-reports the blast radius of its own mutation**, and a reviewer
who ran only the named selector would ship believing one gap was closed.

### 30.4 A MECHANISM THAT IS CORRECT AND LOAD-BEARING NOWHERE

Deleting the guard's 4-space-indented-block handling changed nothing: 38
candidate sites before, 38 after, across 167 files. The document that motivated
it is doubly defended by an independent registry path, and no other indented
block in the corpus carries a candidate-shaped name.

It was NOT deleted -- "nothing in today's corpus needs it" is an argument about
today. A synthetic indented block was added to a control instead, so the path is
exercised by the only thing that will notice. **Register the state explicitly:
a component nothing exercises is one edit from silently ceasing to work, and it
looks identical to one that is load-bearing.**

### 30.5 TWO NUMBERS THIS WAVE GOT WRONG, BOTH CAUGHT BY A READER

* **Per-spelling counts that did not sum.** 347 + 7 + 5 + 4 + 2 + 2 against a
  stated total of 13 non-bare. The measurement attributed each selection to
  EVERY blocker column in its table, so two-column tables double-counted.
  Re-measured per originating column: 347 + 5 + 4 + 2 + 2 = 360, and one
  spelling carries zero. **A number that does not sum is a number nobody
  checked.** A child pasted both figures, flagged the discrepancy, and declined
  to reconcile it silently; that is the only reason it was found.

* **A window that measured text WRAPPING.** The name-scoped absence rule was
  line-bounded, so a disclosure split across a line break did not register and
  the guard convicted a reflowed sentence. Markdown renders that as one
  paragraph. Fixed to span whitespace. The 120-character width remains a
  threshold nobody derived and the ledger says so.

### 30.6 DISPOSABLE, declared

Twelve scratch probes in the session scratchpad -- candidate-population
extraction, per-phrase slot scoring, registry-variant comparison, and the
frozen-snapshot census. All are superseded by the committed guard, which does
what they did with controls. Their numbers are the tables in
`_audit/2026-09-20-names-that-do-not-exist.md`.

---

## 31. THE WRITE-OFF REASON KINDS, AND A CORPUS THAT TURNED OUT TO BE A POINTER GRAPH, 2026-09-20

`scripts/classify_writeoff_reasons.py` + `_audit/_census/reason-kind-adjudications.tsv`,
guarded by `tests/test_writeoff_kinds_are_derivable.py` (71 tests, 8.7s).
Full argument: `_audit/2026-09-20-the-reason-kinds.md`.

**WHAT IT MEASURES.** Every census row in a write-off state -- EXCLUDED-RULED, XR,
MEASURED-ABSENT, COVERED-CANNOT-DELIVER -- rests on a reason, and the corpus spells several
different kinds of thing identically. The classifier sorts all **309** by the kind of fact
the reason asserts: **US-RULING** (somebody decided it), **US-BOUNDARY** (a line somebody
typed in an allow/deny list), **WORLD-FACT**, **ACCOUNT-FACT**, **PROCESS-FACT**. The split
that does the work is two-way: the first two are OURS and re-checkable by reading this
tree; the other three are CONTINGENT and go stale silently. Result at `cd08e05`:
**64 contingent, 40 of them carrying no reopener** -- which is the re-examination list.
That 64 was PREDICTED at 54 and then hit exactly, by implementing the section-heading
resolution the earlier draft had named as the missing piece.

### 31.1 THE LAW IT SERVES, AND WHY THE UNIT OF ADJUDICATION IS NOT THE ROW

127 of the 309 reason cells -- 41% -- are NOT reasons, they are POINTERS; `network.md`'s
median write-off reason cell is FOURTEEN CHARACTERS. Six dialects, three of which were
found by reading the UNCLEAR bucket rather than by design. The most invisible is the
SECTION HEADING: `### K. Recommendations (10) -- all EXCLUDED-RULED under R3`, where not
one of the ten rows beneath carries that attribution in any cell. It is scoped on a
measurement -- exactly ONE heading in the census cites an R-code without being a ruling
heading -- and `--check` fails if that stops being true. The first draft keyword-matched
each pointer row against the whole 926-to-2735-character body it pointed at, and a row whose
entire cell is `R2` came out `ACCOUNT-FACT+US-BOUNDARY+US-RULING` -- a three-kind verdict
carrying no information. **Eleven rulings carry 72 rows, so the ruling is adjudicated once
by hand and the rows inherit**, which is what the census means when it writes `R2`.

### 31.2 SHOWN FAILING -- 6 of 7 mutations RED, 1 GREEN BY DESIGN

Driven over mutated SANDBOX copies; no committed file written.

    M1  empty network.md of all 101 write-offs, leave J/P/M at 48/112/48   RED  (exit 1)
    M2  reword R2's pinned quote by two words                              RED
    M3  move J 134 out of a write-off state                                RED
    M4  delete the whole ### R5 ruling section                             RED
    M5  empty all four slices                                              RED  (exit 1)
    M7  plant one row between P D14 and P D15                              RED
    M8  one space in a CAPABILITY cell, reason untouched                   GREEN (calibration)

**M1 IS THE PER-FILE PROOF.** With `network.md` at zero the other three slices still hold
208 write-off rows, so a UNION assertion over 309 would pass. A union assertion over a
redundant corpus cannot detect a lost source. **M8 is not decorative:** a harness where
every mutation goes red is not discriminating, it is broken.

**TEN SIGNALS FIRE ZERO TIMES AND ALL TEN NEEDLES WERE PROVED ALIVE** against synthetic
positives, including the whole PROCESS-FACT class. A needle that never fires and a fact that
is never true look identical in a count; that is what makes the PROCESS-FACT zero a
measurement rather than a broken regex.

### 31.3 FOUR DEFECTS THE HARNESSES FOUND -- THREE IN THE INSTRUMENT, ONE IN A HARNESS

**In the instrument, silently wrong across 46 rows.** Backreference inheritance recovered its
donor by re-parsing the label `backref<-P D14` with a non-whitespace capture. **Every row key
in this corpus contains a space**, so the capture stopped at `P`, the lookup missed, and
INHERITANCE NEVER RAN. No error, no warning -- every `same` row came out UNCLEAR, which looks
exactly like a census that never wrote a reason. Fixed by storing the donor on the row
instead of encoding it in a display string.
**UNCLEAR fell 50 -> 33 and contingency rose 49 -> 54.**

**In the harness, the same disease one level down.** M1's first version rewrote state cells
with one regex and left 12 of network.md's 101 write-offs standing, because the corpus also
writes `EXCLUDED-RULED (R11)` and a bolded `COVERED-CANNOT-DELIVER`. The per-file control
then passed CORRECTLY and was one step from being recorded as *a control that cannot fail*.
**ASSERTING THAT A MUTATION CHANGED BYTES IS NOT ASSERTING THAT IT ACHIEVED ITS INTENT** --
every mutation now asserts its postcondition first. Compounding it: that same M1 was
asserting against `build()`'s problems list while the per-file control lives in
`main(--check)`, so it was testing the wrong surface entirely.

**A CONTROL THAT COULD NOT FAIL, in the instrument, found by the second reader.** The
per-file control's second half read `unkinded = [r for r in sub if not r.kind]`, and
`finalise` sets `r.kind = "UNCLEAR"` on an empty kind set -- so `r.kind` is NEVER falsy and
that branch was unreachable. It printed "all N write-off rows carry a kind" over 309 rows
and could never have said anything else. **Second instance of this shape in one wave, so it
is counted rather than reported again.** REPLACED with the invariant that actually broke:
a row resolved through a pointer must carry at least what it points at. With inheritance
disabled the replacement convicts 102 rows across all four slices and names each one; the
tautology stayed green through all of them.

**A DOCSTRING CLAIM THE CODE DID NOT HONOUR.** `forbidden_keys()` promised every fallback
path "SAYS SO in the run header"; `FKEYS_SOURCE` was assigned once and read nowhere, so a
reader of a FALLBACK run could not tell it was one. An artifact claiming more than it ran --
the exact defect this wave audits the census for -- inside the auditing instrument. Fixed.

### 31.4 THE LAW THIS ENTRY ADDS: A HAND JUDGEMENT MUST INVALIDATE ITSELF

A derived classification tracks the text for free, but the 12 hand adjudications cannot.
So each one **pins a verbatim single-line quote from the thing it rules on**, and `--check`
fails when that quote stops being present (M2, M3). When somebody rewrites a reason out from
under a hand judgement, the judgement goes RED rather than silently mislabelling the row.

This is why the tag was NOT written into the census cells, which was the obvious design: an
in-cell tag is still hand-maintained, written once against the reason that was there that
day, and **a wrong tag that travels with the row is worse than no tag because it looks
maintained**. Keys are ROW IDS, never line numbers -- s4.1 of
`_audit/2026-09-20-the-contingent-writeoffs.md` measured all six of the census's
line-number locators drifting 48 to 51 lines, one landing on a different row that read
COVERED-PROVEN.

### 31.5 A CENSUS DEFECT WORTH ITS OWN LINE

`network.md` section K is headed *"### K. Recommendations (10) -- all EXCLUDED-RULED under
R3"*, and **not one of `N 119`-`N 128` carries that attribution in any cell** -- those rows
have no note column at all. Confirmed from two directions: R3's own body declares 13 rows,
and a parse looking for an `R<n>` token in every cell of every row finds 4. The difference
is exactly those ten. Five of the nine codes that declare a row set match element for
element, so this is not a slack parse.


### 31.6 WHEN THE TOOL MOVES, PIN THE TOOL AND HASH IT AT BOTH ENDS

The standing freeze discipline is `git stash create`, which pins the CORPUS. That is the
wrong constraint when **the instrument is the thing under test**. This instrument moved
four times during its own mutation run and HEAD advanced through four commits while the
harness was working.

What the harness did instead, and it is better than the freeze that would have been
prescribed: **it hashed the instrument at harness start and at harness end, asserted the
two matched, and pinned every published number to the classifier committed at a named
ref** -- then tabulated the disagreeing earlier baseline ALONGSIDE rather than dropping it.

**A number produced by an instrument that changed underneath you is not attributable to
anything.** Corpus-freezing does not detect that; a start/end hash of the tool does, and
costs two lines.

### 31.7 TWO WRITERS, ONE PATH -- THE SECOND INSTANCE TODAY, SO IT IS COUNTED

`e1b44b0` committed an 11-test version of `tests/test_writeoff_kinds_are_derivable.py`.
`dd73d37` replaced it WHOLESALE with a colder, better 69-test version written independently
at the same path, and **two unique tests went with it**. One was restored because it fell
inside the new mutation set; the other, `test_every_ruling_section_is_adjudicated`, had to
be lifted VERBATIM from `e1b44b0` afterwards.

**A test that was committed and then silently disappeared under a file collision is a
coverage regression regardless of whose file was better.** It is also the same root cause
as the index-side sweep recorded elsewhere today, which took 208 lines of a live wave's
staged work: **the hazard is two writers and one path; the git index and the filesystem are
merely two ways it lands.**

RULE: a wave creating a file at a path a sibling might also target CHECKS FOR IT BEFORE
WRITING, not after. And when restoring a dropped test, lift it unchanged -- guessing at the
intent of a test is how a test gets weakened while looking restored.

### 31.8 DISPOSABLE, declared

Five scratch probes in `_audit/_scratch/`: the replacement-control proof (`_prove_inherit_control.py`, which reproduces the dead-inheritance defect and asserts the new control convicts it), the reason-length profile, the signal-frequency
miner (own-cell vs inherited firing), the Premium-section state tally, and the mutation
driver `_mutate_kinds.py`. The first three are superseded by the committed classifier's own
reporting; the fourth is superseded by the pytest guard, which runs the same mutations with
postcondition assertions. Their numbers are the tables in
`_audit/2026-09-20-the-reason-kinds.md`.

## 32. The sanitiser-scope wave, 2026-09-20

### 32.1 A PROOF'S CORPUS IS PART OF THE ENTRY, AND A GUARD MAY CONSULT ONLY ENTRIES PROVEN FOR ITS OWN KIND

`tests/test_page_text_is_never_printed.py` imported the url rule's
`_is_sanitiser_call` and ORed it into a taint walk whose sources are sixteen TEXT
readers. Every name that predicate matches -- `_shape_of`, `_redact`, `_relation`
-- is certified by a needle table of **eight url-bearing lines and nothing else**.
So a page-text site wrapped in any of them was reported CLEAN on the strength of
a proof about addresses.

**Nobody ruled that. It fell out of an import.** The words "page text", "prose"
and "display name" appear nowhere in the certifier.

It was not theoretical. `scripts/_probe_messaging.py::_redact` returns an
invented display name **byte-identical** on 3 of 6 realistic page-text shapes --
a card byline, plain prose, a name beside a lowercase word -- while correctly
HOLDING on the url it was proven for. It is not broken; it is correctly scoped,
and the scope was written in a docstring where no check could read it.

THE GENERAL FORM, for any guard that stops at a certified helper: **a
certification names a corpus, and the entry must carry that corpus with it.**
`PROVEN_FOR` maps each guarded name to the kind of value it was measured
against; `GUARD_SCOPE` maps each guard to the kind it taints;
`test_a_guard_consults_only_sanitisers_proven_for_its_own_kind` asserts
`consults == (kind == SCOPE_URL)` -- **both directions in one assertion**,
because written one-sided the check still passes if the URL rule LOSES its own
stop, which would silently forbid that rule's own fix.

SHOWN FAILING, against the real pre-fix source rather than a stub:

```
HEAD source names _is_sanitiser_call    : True      <- RED
working source names _is_sanitiser_call : False
the url rule itself names it            : True      <- and must
```

`_names_used` parses rather than greps and counts an import with no call, because
a symbol in a namespace is one word from being a stop condition again. It is
shown rejecting a docstring that mentions the name -- what a grep would match,
and this corpus writes `_is_sanitiser_call` in prose a dozen times.

**TWO OVERLAPPING DEFENCES WERE MUTATED SEPARATELY**, per the standing law.
Restoring the OR in memory: the walker's five red cases fire (mechanism a) AND
the certifier's structural check fires (mechanism b). Removing either leaves the
other convicting.

### 32.2 BUILD BOTH VARIANTS FROM SOURCE TEXT -- NEVER IMPORT A MODULE YOU ARE EDITING

**This one convicted itself the same hour.** To measure what the fix newly
flags, a child was briefed to sweep the tree with two walkers, taking the
"before" variant by importing `text_violations` from the real module. The module
was then edited underneath it. Both variants became the fixed walker, they agreed
on all 178 files, and the delta was reported as zero.

**A corpus you told somebody to read can go stale while they read it**, and the
result looks exactly like a clean measurement.

The brief's mandatory control caught it -- the two variants had to be SHOWN
DISAGREEING on planted cases before any agreement counted, and the child reported
`CONTROL 2 overall: FAIL` rather than presenting the agreement. **The defect was
in the brief, not the work.**

THE INSTRUMENT, reusable for any before/after guard comparison: load the BEFORE
variant from `git show <sha>:<path>` and the AFTER from disk, `exec` both into
separate module objects, and gate the whole sweep on a disagreement control:

```
pre-fix  walker names _is_sanitiser_call in its namespace : True
post-fix walker names _is_sanitiser_call in its namespace : False
  5 of 7 planted cases disagree
  UNWRAPPED -- both must flag    pre=[(2,'print')] post=[(2,'print')] agree
  len() -- both must stay clean  pre=[]            post=[]            agree
```

The two AGREE rows are as load-bearing as the five DISAGREE rows: they show the
variants agree exactly where they must, so the disagreement is one condition
rather than two different programs. Corrected result: 179 files, 111 sites before
and after, **0 newly flagged, 0 unflagged**, and `post == KNOWN_TEXT_SINKS`
exactly.

### 32.3 A VACUOUS LOOP DECLARED BEATS A PARAMETRIZE THAT SKIPS

`test_no_claimant_declares_page_text_without_surviving_the_text_table` checks
ZERO claimants today, because nothing declares `SCOPE_TEXT`. Its docstring says so
in its first line and it asserts its own checked-count, so the day something does
declare TEXT the reader can see it stopped being vacuous.

The alternative is in the same repository: `tests/test_a_verdict_earns_its_entry.py`
has **four tests that SKIP** with *"got empty parameter set"*. A parametrize over
an empty table does not announce that it checked nothing -- it announces a skip,
which reads like a pass in a green run.

The table is made real by two controls over functions that EXIST, not stubs:
`_probe_messaging.py::_redact` is shown FAILING it (3 of 6 shapes) while still
holding its url needle, and `_probe_search_render_timeline.py::_redact` -- the
same name, a different function, allowlist-based -- is shown PASSING all six.
**Two functions, one spelling, opposite results**, which is also the plainest
statement of why a name-matched stop cannot be trusted.

### 32.4 THE NAME-BASED STOP CANNOT BE REPLACED HERE, AND THE COLLISION IS NOW DOCUMENTED RATHER THAN LATENT

Asked directly and answered honestly: **no.** These guards are pure AST analysis,
per module, and deliberately so -- resolving a call to a definition needs either
an import graph plus scope analysis (which still cannot resolve a rebinding, a
dict of functions, or a call through a parameter) or importing all 179 scanned
modules, which for a directory of live browser probes means executing them.
Every scanned file is standalone by design, which is what makes a name the only
handle there is.

What was done instead is to raise the cost of the name: enrolment already
demands a written claim per claimant, `test_every_relation_definition_is_byte_identical`
already refuses two different bodies under `_relation`, and `PROVEN_FOR` now
makes the name carry its corpus.

**THE RESIDUAL, NAMED:** nothing asserts the `_redact` bodies are one function
the way `_relation`'s are -- and they are genuinely two different functions doing
two different jobs, so the honest repair is a RENAME, not reconciliation. A
rename vouches for nothing, which is why it is available to anyone, and it was
not taken unilaterally. Left for its owners, in the open.
### 32.5 A TABLE-DRIVEN GUARD NEEDS THE ENUMERATION HALF, AND I SHIPPED ONE WITHOUT IT

`test_a_guard_consults_only_sanitisers_proven_for_its_own_kind` iterates its own
declaration table, so a new consumer of the url-proven predicate would be invisible
to it. **Committed that way, by the wave that spent the afternoon fixing exactly this
class.** The enrolment half of this same file exists because a claimant inherits trust
the instant it is typed; a CONSUMER inherits it the same way.

The repair is the pattern already in the file: enumerate off the TREE, subtract the
table, and assert the enumeration is non-empty so the subtraction is over something.

THE MUTATION THAT TAUGHT ME MOST CAME BACK GREEN. Dropping the page-text row from the
table fired nothing, because after the fix that file is no longer a USER -- the
containment is one-way, users are a SUBSET of the declarations, and the
declared-but-not-a-user row IS the fix. **A wrong mutation is cheap; a wrong mutation
that returns the colour you expected is not.** Re-run against a real user made
undeclared, and against an invented new one: both red.

---

## 33 · WATCH THE WHOLE LOAD, NOT THE SETTLED DOM (premium4-analyticsshape, 2026-09-20)

Not a new script -- a method, plus the expression that runs it. Section 7 of
`_audit/2026-09-20-the-profile-views-recapture.md` records why it is registered
as a method rather than committed to `scripts/`: the probe holds an address
literal, and `tests/test_navigation_is_never_derived.py` sweeps `scripts/*.py`.

### 33.1 A SETTLED READ CANNOT REFUTE "ATTACHED AFTER HYDRATION"

`dom.py` records that `data-view-name` on the profile-views surface is
"attached by the client AFTER hydration or not at all". **Every reading of that
page for seventeen days -- including two of mine -- was taken at settle, and a
settled read cannot tell `never attached` from `attached, then replaced`.** The
two possibilities have identical evidence at t=infinity, so no number of
repeated settled samples distinguishes them. Repetition proves stability; it
cannot cross a gap in WHEN you looked.

The fix is to sample the whole lifecycle. One open tab, `Runtime.evaluate` over
raw CDP at ~3 Hz through a navigation someone else triggers, printing only when
the tuple CHANGES:

    (() => { const m = document.querySelector('main'); return {
       r: document.readyState,
       dvn: document.querySelectorAll('[data-view-name]').length,
       ml: m && m.innerText ? m.innerText.length : -1,
       an: document.querySelectorAll('a[href*="/in/"]').length,
       dl: document.documentElement.outerHTML.length }; })()

155 polls over 55s, against a fresh server-driven load:

    t+s    ready      dvn  main_chars  /in/    doc_len
     0.2   complete     0        1835     7     143554
     3.6   loading      0          -1     0      23413
     4.0   complete     0         151     0     539626
     5.2   complete     0        1404     7     112699
     5.8   complete     0        1555     7     125995
     7.1   complete     0        1835     7     143556
    PEAK data-view-name = 0

### 33.2 THE CONTROL IS THE OTHER COLUMNS, AND IT IS FREE

**SHOWN ABLE TO SPEAK, in the same table that carries the zero.** The probe
tracked `main` from absent through 151, 1404, 1555 to 1835 characters, the
document from 23 KB through a 539 KB peak down to 143 KB, and `/in/` anchors
from 0 to 7 -- while printing 0 for the target at all 155 samples.

A zero standing beside four columns that moved is a reading. A zero standing
alone is an unproven instrument. **Poll several quantities you EXPECT to move
alongside the one you expect not to, and the control costs one extra key in
the returned object.** This is cheaper than the paired-page control of 29.2 and
works where no sibling page exists.

### 33.3 THE FAILURE IT CAUGHT, WHICH WAS A DIAGNOSIS AND NOT A BUG

The method refuted a same-day audit ruling that an empty `view_names` was "a
proven scope artifact". It is not: the attribute is absent document-wide at
every instant. The defect was real, the fix was correct, and **the fix had
already landed before the reading that diagnosed it** -- `353c04f` is an
ancestor of the serving process's `loaded_commit`. The reader returns the same
numbers either way, because on that page all 61 `<p>` and all 5 `<label>` are
inside `main` already.

**AN INSTRUMENT THAT RETURNS `[]` CANNOT TELL YOU WHICH `[]` IT IS.** "Absent
from the page" and "outside my scope" are one value at the call site. The
general repair is the one 2b used: measure BOTH scopes in the same pass and
return both counts, so the difference is data instead of inference.

### 33.4 TWO PARSE MISSES THIS REGISTERS AGAINST MYSELF

Both were zeros from patterns that had never been shown returning non-zero.

    grep 'href="/in/'  on the fixtures     -> 0    the file uses the ABSOLUTE form; truth 4
    row.get('url'/'profile_url'/'link')    -> 0    the key is 'profile';           truth 6 of 10

Neither reached a verdict, both because a later measurement happened to
contradict them. **Shape a probe's needle against ONE known-present specimen
before trusting its zero** -- the same law as 33.2, applied to a grep.
---

## 34. THE PREMIUM-FOUR WAVE: A DENOMINATOR, AND A READER THAT COUNTED THE WRONG TIER, 2026-09-20

**THIS SECTION WAS WRITTEN AS 29 AND IS PUBLISHED AS 31.** The wave computed
29 from a maximum of 28 at `dc5aaa6` and said in this paragraph that it should
be renumbered if it collided. It collided: `live-capture` published 29 and
`names-that-do-not-exist` published 30 while this wave was in its own worktree,
so the integration took 31 -- and then collided A SECOND TIME, in the
twenty minutes the integration itself took: the `reason-kinds` wave landed
31 on master first. Renumbered to 32, then to 33, then to 34 -- three more
collisions inside one integration, because `sanitiser-scope` was pushed off
31 too and landed on 32 and then 33 ahead of me. **PUBLISHED AS 34.**

**AND THE LAST OF THOSE WAS INVISIBLE TO THE GUARD.** `sanitiser-scope`
spells its heading `## 33 The sanitiser-scope wave` with NO separator after
the number, and `tests/test_the_register_numbers_are_unique.py` matched
`^##\s+(\d+)\s*[. or a middle dot]` -- so it could not see that section at all, reported
the register as unique while it carried TWO section 33s, and I only found
the collision by reading the headings myself. That guard is widened in this
same commit and the specimen is 34.9. `tests/test_the_register_numbers_are_unique.py` is
the guard that makes the collision visible at merge time rather than to a
reader months later, and its rule -- renumber the INCOMING section, never the
published one -- is what was applied here. Citations elsewhere in this commit
that pointed at 29.2 were moved to 34.2 in the same edit.

### 34.1 `scripts/drawn_route_corpus.py` -- the denominator, taken from what LinkedIn drew

ADMITTED. Six controls, **each driven into its failing state in-process, and
the run exits non-zero when any of them cannot be made to fail.**

    control                                    driven state              result
    1 the anchor rule excludes a non-anchor    <link> retagged as <a>    admits 2, FAIL
    2 a bundled anchor is not drawn            STRIPPED_TAGS emptied     admits 2, FAIL
    3 the reducer still changes a name         per-case needles          0 of 4 leak
    4 no placeholder survives substitution     SUBSTITUTIONS emptied     "<entity>" survives, FAIL
    5 an empty corpus refuses, not zeroes      empty file                raises, PASS
    6 controls 1/2/4 all fail when broken      --                        3 of 3

**WHY IT EXISTS, AS A NUMBER.** `scripts/blast_radius.py` is the shipped answer
to "what would this candidate pattern newly admit". Run over its own corpus for
four candidates and five over-broad mutations -- including a bare `.*` wildcard
over `/premium/` -- **all nine measured +0.** Counted:

    corpus size                           67
    addresses under /jobs/collections/     0
    addresses under /premium/              0
    addresses under /analytics/            1   (already admitted)

The instrument is not broken and its docstring states the limit in advance. The
zero is a fact about the denominator. Over this file's corpus -- 44 route
shapes, every one produced by a DRAWN ANCHOR on six live captures, reduced by
the SHIPPED reducer, substituted to sanctioned tokens, written to a TRACKED
fixture because `_state/` exists in neither a clone nor CI -- the same nine
separate: narrow +1 each, `/premium/<class>/` +3, `/premium/.*` +4, `/jobs/.*`
+3.

**CONTROL 3 CONVICTED A CLEAN REDUCER ON ITS FIRST RUN, AND THE LEAK WAS IN THE
CONTROL.** It derived its needle by segment position -- index `[1]`, which is
the identifying segment after a member-bearing prefix and is the literal `view`
in `/jobs/view/<id>`. It voided a clean run. **A needle derived by position
from the input is a rule about the inputs that happened to be listed.** Fixed
by naming the needle per case.

### 34.2 TWO DEFECTS IN `scripts/_probe_premium_surfaces_shape.py`, NEITHER EDITED HERE

Found by building 34.1. Both belong to another wave's file and are recorded
with their evidence rather than fixed in a surprise diff.

1. **It asks `is_read_url` about shapes that still carry the literal
   `<entity>`/`<opaque>` placeholders.** No allowlist regex can match an angle
   bracket, so every placeholder-bearing shape reads REFUSED by construction.
   It under-reports admitted by two on this corpus: `/jobs/view/<opaque>` and
   `/messaging/thread/<opaque>` are both admitted in fact. Its "7 admitted, 36
   refused" is a lower bound on the first and an upper bound on the second.

2. **Depth-3 truncation displays a refused CREATE route as an admitted read.**
   The only role-play anchor drawn anywhere is
   `/learning/role-play/scenarios/new`; truncated to three segments it becomes
   the listing address, which IS admitted, and the table prints ADMITTED beside
   it. **The owning wave's PROSE has this right; its instrument's TABLE does
   not**, and a later reader consults the table.

### 34.3 AND A HYPOTHESIS OF MINE ABOUT THAT PROBE, REFUTED

I expected its raw `href="..."` extraction to inflate its inventory with
strings no anchor draws. Measured over the same six captures through the same
reducer: **43 and 43, difference 0.** The shipped inventory is right. It is
right by luck of this corpus rather than by construction -- a `<link href=>` on
some future capture would enter it and nothing would say so -- which is a
different sentence and the one kept.

### 34.4 `linkedin_server/job_collections.py` -- and the reader that counted the wrong tier

ADMITTED, with `tests/test_job_collections.py` (29 assertions over a real
headless page) and `tests/test_premium_four_boundary.py` (50, pure).

**THE RECEIPT IS A DEFECT IN MY OWN SHIPPED-AND-GREEN CODE.** The first reader
counted hydrated cards, because that is what a job card looks like. The list
has two tiers:

    metric                    recommended   search
    list slots (tier 1)                24       25
    hydrated cards (tier 2)             7        7
    cross-tier id equality            7/7      7/7

It would have reported **7 postings where the collection holds 24** -- 3.4x
low, on the surface the operator named, with 23 tests passing against it.
**IT WAS CAUGHT BY A BOUNCE ISSUED FOR AN UNRELATED REASON**: a slice returned
without its control transcript, the bounce also asked for one number nobody had
taken, and taking that number surfaced the second tier.

**THE SCOPING PROOF, SHOWN BOTH DIRECTIONS.** The fixture carries a DECOY slot
outside `main`, hydrated so it decoys both tiers. The suite installs the naive
document-wide selector and measures it: 11 slots in main and 0 outside against
the shipped 10 and 1 -- **and publishing the decoy's posting id as one of his**.
Driven the other way, with the shipped reader's scope removed, all five shipped
assertions fail.

**THE DECOY IS LOAD-BEARING FOR A MEASURED REASON.** On both real captures
every candidate selector agrees exactly across the two scopes -- 24==24, 25==25,
7==7, 7==7 -- so a scoping claim proved against the captures alone would prove
nothing at all.

### 34.5 THE LAW THIS WAVE ADDS

**A DENOMINATOR THAT CANNOT SEE YOUR CHANGE REPORTS ZERO, AND ZERO READS AS
SAFE.** A blast-radius tool, a coverage number and a needle census all fail the
same way: they answer honestly about a set nobody checked contains the thing
being asked about. The repair is not a better tool -- 34.1 imports the shipped
one unchanged -- it is to **count the denominator before believing the
numerator**, and to keep an assertion that the corpus still DISCRIMINATES, so
the day it stops the suite says so instead of reporting reassuring zeros.

### 34.6 THE INTEGRATION'S LAW: A SCOPED GATE CANNOT SEE A TEST THAT ASSERTS AN ABSENCE

Added 2026-09-20 by the integration that merged this wave, from a defect the
merge found in the wave itself. Full argument:
`_audit/2026-09-20-the-premium-integration.md` section 3.

**THE SPECIMEN.** This wave admitted `/analytics/recruiter-views` and its entry
opened *"NEVER RECORDED ANYWHERE IN THIS REPOSITORY BEFORE 2026-09-20."* The
tree disagreed at the merge base: commit `4c2de7e`, 2026-09-05, had put that
exact address in `tests/test_analytics_creator_boundary.py`'s refused-neighbours
table, reason *"DRAWN BY THE PROFILE-VIEWS PAGE, twice, and not admitted"*, and
the drawn url had been sitting in two TRACKED fixtures the whole time.

**THE FILE IS UNCHANGED AT THE BASE AND AT THE WAVE TIP, so the wave's own tree
was already red on it before any merge.** Its freeze reported a PASS over 29
files and 1354 tests; that file was not among them.

**THE LAW.** `scripts/impact_gate.py` already records that a NAME-based impact
rule waved a markdown edit through to a red parser -- a file type the analyser
skips. This is the same defect through the other door, and it is worse because
no file-type fix reaches it:

> **A scoped gate can find the tests that NAME the code you changed. It cannot
> find the tests that assert the ABSENCE of what you just added.** A refusal
> test -- "this address stays refused", "this count is exactly N" -- is that
> assertion, and the name it would be keyed on does not exist in the tree until
> the moment you add it. The coupling edge runs BACKWARDS in time from the
> analyser's point of view.

**THE CHEAP MITIGATION, stated as a rule rather than built here.** Any change
that ADDS a member to a guarded collection -- an allowlist entry, a sanctioned
mutation, a detector -- must also run the tests that assert that collection's
SIZE or its refusals, and those are findable by the collection's NAME even when
the new member's name is not. `_ALLOWED_URL_PATTERNS` is named by
`test_analytics_creator_boundary.py` and would have been caught by exactly that
rule.

**SHOWN FAILING, and it fired on its own author.** The 2026-09-05 count test
said in its docstring that it existed so *"a fourth analytics page cannot arrive
unnoticed"*. A fourth arrived on 2026-09-20 and it noticed -- at merge time,
three tests red, having never been run by the wave that tripped it. The tripwire
worked; the gate that should have shown it to its author did not.

### 34.7 AND A BASELINE THAT IS RE-SYNCED IS A MIRROR WEARING A HISTORICAL NAME

Same integration, second finding, full argument in section 4 of that document.

`tests/test_readonly_boundary_invariant.py` carries `DENYLISTS_AT_A76FE32`,
documented as *"the four denylist digests as they stood at `oldsha14`"*, so that
"the write widened nothing" is checkable rather than a sentence in a comment.
Measured across all 39 commits that have touched the file, both dicts extracted
by `ast` from each committed blob:

    commits where the baseline dict exists             36
    commits where it was REWRITTEN                     25
    commits where a shared key held a DIFFERENT value   0

Never once, not even transiently. Every baseline change landed in the same
commit as the corresponding pin change, and the 7 pin-only changes each moved
only a key the baseline does not carry. The lockstep has an origin: the live pin
was ITSELF named `READONLY_AST_AT_A76FE32` before the baseline was split out of
it. The dict is named for a commit that no longer resolves in this repository.

**SHOWN FAILING -- or rather, shown UNABLE to fail.** Eight single-structure
edits applied in memory to master's `readonly.py`, both test bodies evaluated:

    edits that red BOTH tests              5
    edits that red the PIN test only       3
    edits that red the BASELINE test only  0

**THE LAW.** A baseline constant exists to disagree with the live value. **The
moment updating it becomes part of the routine that updates the live pin, it
stops being a baseline and becomes a second copy** -- and a second copy asserts
nothing the first did not, while still reading like independent corroboration to
anyone counting green checks. The tell is not the values; it is the EDIT
PATTERN. If every commit that touches A also touches B, B is not measuring A.

The integration removed the one key that every READ admission forced to be
re-synced, so a read admission can no longer touch that dict at all. It did NOT
claim the repair restored the check's power: the four remaining values still
equal the live pin's, the test still cannot fail alone, and the docstring now
says so. Whether to delete it outright is left as a ruling.

### 34.8 THE DECORATIVE-CONTROL DETECTOR FLAGS A CONTROL'S INPUTS, AND ITS RATCHET HAS NOWHERE TO SAY SO

Found by the integration that merged this wave, while triaging a red the merge
caused. Full reading of all four specimens:
`_audit/2026-09-20-the-premium-integration.md` section 9.

`scripts/detect_unbranched_probe_controls.py` and its ratchet
`scripts/probe_controls_known_decorative_baseline.json` (section 27, 129 rows)
went red on four new findings in this wave's
`scripts/_probe_analytics_list_shape.py`. **THREE OF THE FOUR ARE THE DETECTOR
FLAGGING A CONTROL FUNCTION'S INPUT VARIABLES, NOT ITS RESULT:**

    _probe_analytics_list_shape.py:886  control()    -> expected
    _probe_analytics_list_shape.py:925  break_demo() -> expected
    _probe_analytics_list_shape.py:925  break_demo() -> html

At both sites the statement is `html, expected = _build_control_doc()` -- a
tuple unpack of the control FIXTURE. The results are branched, and well:
`control()` runs three controls, each `if <bad>: print VOID; return 1`;
`break_demo()` accumulates `overall_ok = overall_ok and not ok` over two induced
breaks and branches on it. These are among the better-branched control functions
in the tree, and the detector reports them as decorative.

**THE DETECTOR IS SCOPED BY THE ENCLOSING FUNCTION'S NAME AND MARKER WORDS**, so
every local inside a function called `control()` is a candidate. The class is
already IN the published census -- `_probe_add_section_menu.py / main / html`
is the same shape and has been a baseline row since it was generated. So an
unknown fraction of the headline number 129 is not decorative controls at all.
**That number is cited as a finding; it is at least partly a measurement of the
detector.** Nobody has counted which rows are which, and this entry does not
either -- it establishes only that the class exists inside the census, with four
fresh specimens read line by line.

**AND THE RATCHET CANNOT RECORD A TRIAGE.** Its failure message instructs a
committer to *"add it to the baseline with a one-line reason"*. The file's rows
are bare `(file, function, variable, line)` tuples with **no reason field**, and
all 129 carry none. So the mechanism the guard names does not exist in the
format the guard reads:

> **A TRIAGE TABLE WHOSE ENTRIES CANNOT CARRY THEIR TRIAGE IS A CENSUS WEARING A
> RATCHET'S NAME.** It still ratchets -- a new finding does go red -- but the
> judgement that cleared each row is unrecoverable, so the next reader cannot
> tell a reviewed-and-accepted reading from a rubber stamp, and cannot tell a
> real decorative control from a detector artifact.

Compare `NOT_A_CORRECTION` in
`tests/test_a_correction_is_findable_from_the_claim.py`, which solves exactly
this problem in the same repository: its key is the pair and its VALUE is the
written reason, so every triage is readable beside the thing it triaged. That is
the shape this baseline wants.

**NOT REPAIRED HERE, deliberately.** Changing a detector that produced a
published 129-row census, or migrating the ratchet to a reasoned format, is a
wave and not a merge step. What the integration did do is grow the ratchet by
four with every specimen argued in the audit, and write a pointer into the
file's own `_comment` and `generated_from` so a reader of the JSON is sent to
the reasons rather than left with four more bare tuples.

### 34.9 THE UNIQUENESS GUARD COULD NOT SEE TWO OF THE SECTIONS IT GUARDS, AND CALLED ONE OF THEM A GAP

Found by this integration, at the cost of a fifth renumber. The guard is
`tests/test_the_register_numbers_are_unique.py`, section 24's own instrument,
and it is widened in the same commit as this entry.

**THE DEFECT.** Its heading pattern required a separator after the number:

    HEADING = re.compile(r"^##\s+(\d+)\s*[.MIDDOT]", re.M)

Two committed sections carried something other than `.` or a middle dot after
the number, and matched neither spelling. **THEY ARE NOT THE SAME DEFECT, and
this entry originally said they were:**

    ## 22 THE IMPACT GATE, ...        an ordinary SPACE -- a real spelling
    ## 33<SOH> The sanitiser-scope    a literal 0x01 CONTROL BYTE

The second was corruption, not style. A resolver built `f"## {hi+1}\1"` inside
a shell heredoc; the heredoc passed `\1` through and Python read it as `\x01`
rather than as a regex backreference. Its own wave found and repaired it at
`771b323` -- independently of this entry, within the same hour -- and renumbered
that section to 32, where its deliverable's citation already pointed.

**THE CORRECTION MATTERS TO THE FIX.** Widening the pattern legitimises the
FIRST spelling; it must NOT be allowed to paper over the second, because a
widened regex would have SILENTLY ACCEPTED the corrupt heading instead of
reporting it. So the control asserts both halves: section 22 is seen, AND no
register heading carries a control byte at all. Today section 22 is the only
surviving specimen of the real spelling, and the control says so, so it will
speak if that ever stops being true.

**SHOWN FAILING, on the state the register was actually in.** This integration
renumbered its own section onto 33 because the guard reported the register
unique, and 33 was not free. The real test body, run against that register:

    register carrying TWO '## 33' headings
      OLD pattern   30 headings seen   duplicates: NONE   <-- PASSED, wrongly
      NEW pattern   32 headings seen   duplicates: ['33']

    after renumbering mine to 34
      OLD pattern   30 headings seen   duplicates: NONE
      NEW pattern   32 headings seen   duplicates: NONE

    sections the OLD pattern could not see at all: ['22', '33']
      -- '33' repaired at 771b323 the same hour; '22' survives and is pinned

The collision was found by READING THE HEADINGS BY HAND, not by the guard whose
entire purpose is to find it. A duplicate would have shipped.

**AND THE ARTIFACT HAD BEEN PROMOTED TO DOCUMENTATION.** The guard's docstring
said the register *"already has a real gap at 22"*, and used that supposed gap
to justify not enforcing contiguity. There is no gap. Section 22 is at line
3736 and always has been; the guard could not see it, reported its absence, and
a later reader wrote the absence down as a property of the register.

> **A NUMBER YOUR INSTRUMENT CANNOT SEE COMES BACK AS A FACT ABOUT THE THING
> YOU ARE MEASURING.** Not as an error, not as a gap in coverage -- as a
> feature of the subject, in prose, in the instrument's own file, where the next
> reader inherits it. This is the same shape as the empty-denominator zero in
> 34.1 and the mirror baseline in 34.7: three instruments in one register, each
> reporting cleanly about a set that did not contain what was being asked about.

**THE FIX IS ONE CHARACTER CLASS** -- `r"^##\s+(\d+)\b"` -- plus a control that
is two-sided: it asserts the NEW pattern convicts the duplicate AND that the OLD
pattern did not, so the widening is shown doing work rather than decorating. The
control also pins the exact two sections the old pattern missed, so if either
heading is ever normalised the control says so instead of silently passing.

**NOT FIXED: the numbering scheme itself.** Five waves computed "the next
integer" from the same stale maximum for one section today, and three of the
renumbers happened inside this single integration. The guard makes the collision
visible at merge time, which is worth having; it does not make appending to a
register concurrent-safe, and nothing here claims it does.

### 34.10 FOUR INSTRUMENTS IN ONE DAY MATCHED A NAME AND COULD NOT SEE THE STRUCTURE

Not a new instrument. A class, counted only because this integration tripped
all four inside one merge and the fourth had been holding master red.

    instrument                              matched            could not see
    -------------------------------------   ----------------   ---------------------
    detect_unbranched_probe_controls.py     the enclosing      that `html`/`expected`
      (34.8)                                function's NAME    are control INPUTS
    test_the_register_numbers_are_unique    `## N` + a         a space, and a 0x01
      (34.9)                                separator          control byte
    test_probe_interaction_budget           the VERB `fill`    the RECEIVER --
      (this entry)                                             textwrap vs a page
    scripts/pre_commit_boundary_gate.py     module-level       a test that asserts
      (34.6, the scoped gate)               NAMES              an ABSENCE

**THE FOURTH, MEASURED.** `tests/test_probe_interaction_budget.py` refuses a
probe script that makes a gated interaction nobody declared. From `1ab1ca8`
(12:55) it convicted this line in `scripts/classify_writeoff_reasons.py`:

    print(f"\n=== TIER {rank}: " + textwrap.fill(

`textwrap.fill` wraps a string. `page.fill` types into LinkedIn. The scanner
matches the verb and cannot see the receiver, and the module opens no browser
at all -- it is an offline classifier over a census TSV.

**IT HELD MASTER RED FOR FORTY-FOUR MINUTES ACROSS EVERY WAVE'S CI.** Measured
by run, not inferred: `d6b7e4b` SUCCESS; `1ab1ca8`, `bbc8dde` and `771b323` all
FAILURE, one failed test per cell on all three platform cells, the same test
each time. **That is the condition this repository has spent the day naming: a
red master makes a NEW red unreadable, so the next wave's genuine failure
arrives looking exactly like the standing one.** The premium-four integration's
own CI run was red for this reason and for no other.

Declared as a false positive on the table's own terms -- the guard names the
three responses and forbids the third by name: *"If the call is right, add it
to DECLARED with the reason and the bound. If it is a false positive, declare
it as one. Do NOT widen OPEN_CLASSES to clear this: that silences the verb
everywhere at once."* Exact precedent already sat in the table:
`_probe_badge_and_language_affordances.py` / `http_post`, a JavaScript
`Set.delete` read as an HTTP DELETE.

**THE COMMON SHAPE, and it is worth more than any of the four.** Each of these
instruments is a text matcher standing in for a structural question:

> **Is this identifier the thing I care about, or does it merely SPELL like
> it?** A name is evidence about a name. The question every one of these
> guards is actually asking is about a RECEIVER, a SCOPE, a BYTE or a
> DIRECTION -- none of which a name carries.

The repository already knows this: `read-the-structure-not-the-text` is a
standing memory, and three of these four parse Python with `ast` somewhere
else in the same file. The gap is not knowledge, it is that a name-matcher is
cheap to write and its false positives are quiet until somebody counts them.

**WHAT IS NOT CLAIMED.** No count of how many of the register's published
totals are inflated by this class. 34.8 establishes that at least some of the
129-row decorative-control census is detector artifact; nobody has measured how
much, and this entry does not either.

---

## 35. THE POINTER-GRAPH WAVE: A CENSUS ROW WHOSE ARGUMENT MOVES WITHOUT IT, 2026-09-20

**THIS SECTION WAS WRITTEN AS 35 against a maximum of 34 at `0882d35`.** Several
waves append here at once, and the standing rule is renumber the INCOMING section,
never the published one. If `tests/test_the_register_numbers_are_unique.py` fires
on this, renumber it and move 35.1 and 35.2 with it.

### 35.1 `scripts/measure_pointer_graph.py` -- the pin, and the guard over it

ADMITTED. 69 census reason cells lead with the word `same` and inherit the reason of
the nearest substantive row above them IN THE SAME TABLE. Nothing marks a row as
load-bearing for the rows beneath it, so a row inserted mid-table re-points every
dependent below it and changes its published classification with no edit to those
rows. **Measured over the whole corpus, not argued:** 71 insertion slots, 48 of which
move a verdict, **45 distinct write-off rows movable by an edit that never touches
them** -- and on the single plant, `count_census_states.py` reported the added row
(`stated rows 704 -> 705`) with ZERO lines naming the three rows whose verdicts had
just changed, while `build_blocker_map.py --check` was byte-identical.

`--pin` writes the graph to `_audit/_census/pointer-graph.tsv`; `--check` re-derives
it and convicts a pointer whose argument moved. The pin carries the donor's KIND
rather than its TEXT, deliberately: prose here is appended to several times a day and
a guard that cries wolf gets switched off. **The cost is published on every green
run** -- a donor rewrite that changes the ARGUMENT without changing its KIND passes
this guard.

    control                      mutation                                     result
    G1 re-point                  plant a substantive row above P D15          RED
    G2 donor rewrite             replace P D14's own reason, same position    RED
    G3 source goes dark          blank jobs.md's 13 pointers, 56 remain       RED
    G4 empty pin                 pin reduced to its header                    RED
    G5 CALIBRATION               whitespace in P D15's capability cell        GREEN

`--selftest` drives all five and exits non-zero if any behaves otherwise; the wrapper
is `tests/test_pointer_graph_guard.py` (3 tests, 26s), which asserts each control by
NAME so a control silently deleted from the instrument fails the suite instead of
shrinking it to a green nothing. G3 is asserted PER SLICE because a union assertion
over a redundant corpus cannot detect a lost source. **A second refusal is admitted
with its own red proof:** `--plant-sweep --plant-reason same` plants a cell that
cannot become a donor, finds zero verdict changes, and REFUSES (exit 1) rather than
reporting a clean sweep.

### 35.2 THREE DEFECTS IN THIS WAVE'S OWN INSTRUMENT, AND THE ONE THAT CAUGHT THEM

1. **The selftest went red on all five controls, calibration included.** Its sandbox
   is `git archive HEAD`, chosen so an uncommitted edit cannot leak into a
   measurement -- and the instrument on trial was uncommitted, so the sandbox did not
   contain it. **G5 is what convicted it.** A harness in which the control that must
   PASS also fails is announcing it is broken; without a calibration, five reds read
   as five successes.
2. **A refusal was computed and never printed.** The per-slice check built the
   sentence *"jobs.md contributed ZERO positional pointers"*, put it in the failure
   tally, and printed nowhere. The run went red with a count and no cause.
3. **A control claimed more than it ran.** The single-plant path printed *"rows that
   survived EVERY plant unchanged: 43"* after planting one row, over 43 rows nothing
   was planted near. It now refuses that claim unless `--plant-sweep` earned it.

**THE LAW THIS WAVE ADDS: BYTE-IDENTITY ON THE COUNTERS IS NECESSARY AND NOT
SUFFICIENT FOR A CENSUS NOTATION CHANGE.** The obvious repair -- rewrite `same` to
`same as P D14` -- was built and priced rather than judged. It left
`count_census_states.py` and `build_blocker_map.py` byte-identical **and moved three
published classifier verdicts**, one from `US-RULING` to `UNCLEAR`: `P G3`'s entire
cell is `same ruling`, and the US-RULING signal fires on that ADJACENCY, which three
inserted tokens break. Neither counter reads a reason cell, so neither could ever have
seen it. Any future notation change over these files needs
`classify_writeoff_reasons.py` in its proof. The rewrite was refused; see
`_audit/2026-09-20-the-pointer-graph.md` section 4 for the other three axes it was
priced on, including that it buys no safety at all while the resolver still resolves
by position.

**NOT AN INSTRUMENT, RECORDED SO IT IS NOT REDISCOVERED A FIFTH TIME.**
`count_census_states.cells()` splits on `|` without honouring the markdown escape
`\|`. Four lines carry one, all in `jobs.md`; the STATE is read correctly on every one
of them -- which is why no instrument has noticed -- and the REASON is read as a
truncated tail (`J 103`: 795 chars seen, 1322 held). No census number and no pointer
count is affected. Found by a child forbidden to import the shipped parser, which is
the argument for briefing one that way.

---

## 36. THE FIVE PROBES UNDER A BANKED ROW, 2026-09-20

The 129-row decorative-control census (section 27) ranked five probe files as
TIER 1: the ones a census row had already been banked on. This wave took those
five. Full reading: `_audit/2026-09-20-the-five-under-banked.md`.

**ALL NINE BANKED ROWS HOLD. TWO OF TWELVE FLAGGED INSTANCES WERE REAL
DECORATIVE CONTROLS.** Both are repaired; neither repair moved a row.

### 36.1 `scripts/_check_repaired_probe_controls_can_fail.py` -- SHOWN FAILING

The receipt this register requires before a repair is believed. Ten
demonstrations, two kinds. BEHAVIOURAL: the real `_analyse` from
`scripts/_probe_membership_sections.py` over two synthetic captures built in
the script, one `<h9>` apart, which must return opposite verdicts -- plus the
same function over the REAL gitignored capture, which reports LOUDLY when the
file is absent rather than skipping, because a worktree carries no gitignored
file and a silent skip there reads as a pass. MECHANICAL: the detector run over
the HEAD blob and over the working file, where the variable must be a FINDING
at HEAD and CORRECTLY BRANCHED now -- same file, two shas, opposite verdicts,
the shape section 27's own calibration used.

```
PASS   A1: the clean capture returns True (3 anchors, no <h9>)
PASS   A2: the SAME capture plus one <h9> returns False
PASS   A3: the two verdicts differ
PASS   A4 control-for-the-control: a clean capture with the WRONG expected
       count also returns False, by the OTHER control
PASS   A-LIVE1: the real groups capture still returns True with the control
       now gating -- the banked reading survives
PASS   A-LIVE2: and it does so because the control read 0
   pre-repair blob: 0882d35 (pinned, never HEAD)
PASS   B: _probe_membership_sections.py _analyse() -> 'silent' is a FINDING at 0882d35
PASS   B: ... is CORRECTLY BRANCHED in the working tree
PASS   B: _probe_creator_content_analytics.py main() -> 'feed_hits' is a FINDING at 0882d35
PASS   B: ... is CORRECTLY BRANCHED in the working tree

all 10 demonstrations behaved as stated
```

**AND IT READ `HEAD:` UNTIL THE COMMIT LANDED.** The first version of this
receipt passed ten of ten and went RED ON TWO the instant the repair was
committed, because HEAD then WAS the repair and the "before" side became the
"after" side. Caught by the full suite, not by reading.

> **A RECEIPT PINNED TO A MOVING REFERENCE STOPS BEING A RECEIPT AT THE MOMENT
> IT IS MOST LIKELY TO BE BELIEVED** -- the commit that makes the fix real is
> exactly the event that re-points the reference at the fix. It is now pinned
> to `0882d35`, and if that blob ever stops resolving the demonstration says
> so and FAILS rather than skipping.

**AND THE RECEIPT WAS SHOWN NON-VACUOUS**, which is the half a receipt
generator usually skips. Demonstration A2 was re-run against the PRE-REPAIR
blob at HEAD `0882d35`, loaded as a module so the real committed code ran:

```
COUNTER-CHECK against the PRE-REPAIR source (HEAD 0882d35):
  A1 clean  -> True
  A2 broken -> True
  HEAD's own line: ['CONTROL must stay silent: 1 FAIL']
VERDICT: A2 would have FAILED at HEAD, so the receipt is not vacuous.
```

**The committed code printed FAIL and returned True in the same run.** That is
the census's defect, caught in the act, in a file under a banked row.

### 36.2 THE HONEST LIMIT OF THE REPAIRED CONTROL

`IMPOSSIBLE_HEADING` is `<h9>`, a level HTML does not have, so this control
reads 0 by construction on any real capture. **The repair proves the WIRING
refuses; it does not make the needle strong.** An assertion satisfied by an
empty result still cannot fail, and the injected-`<h9>` demonstration exists
because the live green could not have told me the difference. Registered as a
limit rather than smoothed, because a control that comes back the colour you
expected is the one nobody re-examines.

### 36.3 TWO DEFECT CLASSES A VARIABLE-BASED DETECTOR CANNOT SEE

Found by reading the five files, not by the detector, and neither appears in
the 129 in any form.

**A DISCARDED RETURN BINDS NO VARIABLE.**
`scripts/_probe_small_measures_live.py` states a contract in its docstring --
*"If a page control fails, this file prints SUSPECT against that surface and
does not offer its target counts as a reading"* -- and honoured it on ONE
surface of three. `read_events` and `read_feed_hashtag_context` called
`await _page_control(...)` as a bare statement and dropped the boolean. The
detector hunts a variable nobody branches on; here there is no variable. Both
sites now bind and branch.

> **A CONTROL WHOSE RESULT IS NEVER BOUND IS INVISIBLE TO A DETECTOR THAT
> LOOKS FOR AN UNUSED BINDING, AND IT IS THE SAME DEFECT ONE STEP EARLIER.**

**A VERDICT PRINTED FOR A HUMAN TO EVALUATE.**
`scripts/_probe_creator_content_analytics.py` prints *"structural fields EQUAL
to the feed: N of M"* then *"IF THAT IS MOST OF THEM, THIS ADDRESS IS SERVING
THE FEED"*, and returns 0 either way. For a declared CAPTURE that is a design
choice and it is NOT repaired here; it is written down so the next reader
knows the sentence is an instruction to a person, not a branch.

### 36.4 TWO MORE FALSE-POSITIVE MECHANISMS IN THE DETECTOR, MEASURED

Disclosed in `scripts/detect_unbranched_probe_controls.py`'s own docstring
beside the `passes` mechanism it already carried. The detector is NOT changed:
narrowing the marker rule moves a published census and is a wave of its own.

**THE BARE PYTHON `pass` STATEMENT.** The marker "pass" matches the keyword,
which is the idiomatic body of a swallowed `except` and therefore lands inside
the window of any value read in a `try`. Sweep: strip every line that is a bare
`pass` statement from each finding's window, re-test for a marker, count the
findings that lose their last one. **4 of 133 (3.0%)** as measured before this
wave's two repairs, and the same 4 of 131 (3.1%) after -- larger either way
than the 1.6% `passes` mechanism already disclosed. The denominator is dated
because it moved inside this wave.

**A WINDOW THAT REACHES A BANNER.** The window runs to the first later sibling
whose subtree sinks the name, which for a report accumulator flushed by a
printing `_write()` spans whatever the probe announced in between.
`_probe_job_search_result_sets.py main() -> lines` is flagged solely because an
`emit("positive control keyword: ...")` string sits ten lines into a 28-line
window. It is the single TIER-1 finding with five banked rows behind it, and it
is not a control at all.

**A PROXY FOR THE OPEN MARKER DISPUTE, offered without ruling on it.**
`tests/test_probe_controls_are_never_decorative.py` records an unresolved
question about three `_probe_events_surface_shape.py` entries where the marker
vocabulary collides with LinkedIn UI "control". Counted 2026-09-20: **56 of the
131 live findings (42.7%) have `control` as their ONLY marker, with no PASS /
FAIL / VOID / must-fire / must-stay-silent / sanity / agree vocabulary anywhere
in the name or window.** An upper bound on the class, not a verdict -- a real
control can be named without verdict words. The three disputed entries sit
inside that 56.

### 36.5 THE RATCHET NOW CARRIES ITS TRIAGE, WHICH 34.8 ASKED FOR

133 -> 131, GAINED 0, LOST 2, both removed rather than left to rot.

Section 34.8 diagnosed the hole and declined to fix it -- *"a triage table
whose entries cannot carry their triage is a census wearing a ratchet's
name"*, and migrating the format *"is a wave and not a merge step"*. This was
a wave. `scripts/probe_controls_known_decorative_baseline.json` gained an
**optional** `reason` string; ten entries carry one, 121 do not, and the
difference is the point: an entry without a reason is visibly untriaged rather
than silently assumed reviewed.

`test_baseline_file_is_well_formed` asserts the field's shape and that it has
not been WIPED -- a regeneration straight from the detector emits no reasons
and would erase every triage ever recorded. **Deliberately no count floor**: a
floor is an incentive to write reasons in bulk, which is the rubber stamp 34.8
warned about. Shown failing on three doctored inputs against one control, with
the shipped test function imported rather than re-implemented:

```
PASS   1. reasons stripped must go RED                RED as required
PASS   2. a blank reason must go RED                  RED as required
PASS   3. an unknown field must go RED                RED as required
PASS   4. CONTROL: the real file must stay green      green
```

**AND THE BASELINE'S OWN COMMENT WAS STALE.** It told a reader the test *"does
NOT require this file to shrink when an old one is fixed"*. The test has been a
two-way ratchet since the peer review that caught it being one-way. A reader
obeying the comment would have left both repaired entries in place and gone
red. Rewritten.

### 36.6 THE LAW THIS WAVE ADDS, AND THE CENSUS FINDING DID NOT FIND IT

Five banked rows cite one instrument, one session, one evidence document. The
document is a composite of TWO runs and names only one; the raw output path it
points at had been overwritten twice, forty minutes before the document was
written; and the two runs disagree about the drift floor -- 0 in the run the
five rows quote, 4 in the run made twenty minutes later. On the stricter floor
four rows get stronger (MOVED 14, 14, 12, 14 above a 4-id floor) and one flips:
`f_JT=F moved 2 -- WITHIN DRIFT (4), not evidence`.

> **A THRESHOLD MEASURED PER SESSION MUST BE QUOTED WITH ITS SESSION, OR THE
> FRIENDLIEST SESSION BECOMES A PROPERTY OF THE SURFACE.**

**AND THE WHOLE EVIDENCE CHAIN FOR THOSE FIVE ROWS ENDS OUTSIDE THE
REPOSITORY.** The raw output was overwritten twice the same hour, and the
progress document holding the surviving prose is under `_audit/_scratch/`,
which `.gitignore:156` quarantines unconditionally -- `git ls-files
_audit/_scratch/` returns nothing. The cells CITE rather than DEFER so
`tests/test_no_committed_document_defers_to_an_ignored_path.py` is right to
pass them; the narrower problem is that the numbers are stated in the row and
checkable nowhere, so an over-stated one survives until somebody opens a
machine that still has the file.

The probe understood this -- it takes the stability control LAST, on purpose,
so it spans the whole session -- and five census cells then copied one
session's number across as though it described LinkedIn. The cells are
corrected in place with a declared CORRECTS/CORRECTED BY pair; no row's state
moved, and the case for moving row 11 anyway is written out for whoever owns
the census.

**THE POINT FOR THIS REGISTER: none of that came from the census finding.** The
flagged control in that file was an accumulator. A decorative control is a
defect you can grep for. This one was reachable only by opening the evidence
and reading it against the outputs still on disk.

### 36.7 DISPOSABLE, declared

The three edit scripts, the counter-check harness, the baseline updater and the
doctored-baseline demonstration were scratchpad-only and are not shipped. The
two receipts that matter are re-runnable from the repo:
`scripts/_check_repaired_probe_controls_can_fail.py` and the detector itself.
The two gitignored captures copied into this worktree to re-run section 1 are
ignored here as everywhere and are not part of any commit.

---

## 37. THE SHA-CITATION WAVE: KIND BEFORE RESOLUTION, THIRD COSTUME (sha-repair-sixty, 2026-09-20)

### 37.1 `scripts/check_cited_shas_resolve.py` -- every cited SHA must resolve in a CLONE

**ADMITTED, AND SHOWN FAILING.** The red proof is
`tests/test_a_cited_sha_resolves.py::test_the_detector_finds_a_planted_citation`:
a planted one-line document whose only citation is a seven-character hex token
that names no object is extracted as exactly one candidate and convicted. Its
mirror, `test_a_resolvable_citation_is_not_convicted`, plants the same sentence
with `HEAD`'s own abbreviation and asserts zero findings -- because an
instrument that resolves NOTHING reports everything missing and looks exactly
like a finding.

**THE GUARD CONVICTED THIS ENTRY ON ITS FIRST RUN, and that is the second time
today a check has fired on prose DESCRIBING its own mechanism.** The paragraph
above originally quoted the planted sentence verbatim, which put a deliberately
nonexistent token into a real commit slot in a tracked document. The test file
is not scanned; the register is. Same shape as this repository's
correction-marker guard reading a sentence about markers AS a marker: **prose
about a mechanism is indistinguishable from the mechanism to a matcher that
only looks at shape.** Quoted in paraphrase here for that reason.

**WHAT IT ASSERTS.** A short SHA in an audit document is a promise a reader can
check. The predicate is `git merge-base --is-ancestor <sha> master`, read by
exit code, **never `git cat-file`**. That distinction is the instrument, not a
detail: this repository keeps a `pre-purge-restore` tag and 80+
`worktree-agent-*` branches, so `cat-file` answers "commit" for objects no
clone can reach. `test_ancestry_not_existence_is_the_predicate` pins it by
taking a real off-`master` branch tip and asserting `cat-file -e` exit 0,
`--is-ancestor` exit 1, and `guard.resolves(...) is False`. That control
asserts its own fixture exists FIRST and fails loudly rather than skipping --
if the branch is ever deleted, a skipping control would silently let the guard
become the broken thing it replaced.

**FOUND, on first run: 22 distinct SHAs across 29 citations in 19 documents.**
Pinned, not repaired -- other waves' territory, three of them live. Two-way
ratchet: red on a new one, red when a pinned one disappears.

### 37.2 THE LAW, IN ITS THIRD COSTUME IN ONE DAY

> **A ZERO FROM A RESOLVER MEANS "NOT OF THIS KIND, OR ABSENT", AND IT CANNOT
> DISTINGUISH THEM. DECIDE WHAT A TOKEN IS BEFORE ASKING A RESOLVER ABOUT IT.**

Three waves hit it on 2026-09-20 wearing three different costumes, and **the
third one proves no shape filter can be the answer**, because the corpus
supplies counter-examples in both directions:

| direction | receipt |
|---|---|
| a filter removing NOISE | 280 of 340 "dangling SHAs" were `a`+digits help-article ids |
| the SAME filter removing SIGNAL | `a540461` and `a604394` are that exact shape **and are real commits**; `a604394` does not resolve, and the filter that fixes the 280 deletes the finding |
| the companion "not all digits" filter | `5480246`, `5581950` and `9580360` are all-digit real SHAs -- and `9580360` is a **live twin inside a repair's own mapping table** |

A filter that drops a repair's own output is not removing noise. **The SLOT
decides; the shape cannot.** One slot phrase was measured and DROPPED for the
register: a bare ``in `X` `` selects 44 occurrences and 8 are help-article ids,
including a document naming the kind in the same clause.

### 37.3 A REPAIRED CITATION AND AN UNREPAIRED ONE HAVE THE SAME TOKEN SHAPE

This is why the guard has suppressors at all, and it is the finding that makes
a shape-only census unusable on this corpus. The August repair KEPT all 24 dead
hashes -- it had to; the dead hash is the key a reader arrives with -- and
added a mapping table plus a top-of-file declaration. **A guard that fires on
that punishes the repair and gets switched off.** Every suppressor is quoted
from the corpus rather than invented. The disclosure suppressor exists because
the guard's first run convicted the sentence *"and no clone can reach
`5a69147`"* -- a document being correct out loud in the guard's own recommended
words.

### 37.4 A UNION ASSERTION OVER A REDUNDANT CORPUS CANNOT DETECT A LOST SOURCE

**Registered against myself.** My first mutation control stripped one mark and
asserted the citation came back. It failed on both cases -- not because the
suppressors are broken but because they OVERLAP: both repaired documents carry
a declaration AND a mapping table, so removing either leaves the other covering
the token. Had the mapping-table parser broken later, a "is it still
suppressed?" test would have stayed green on the declaration alone and the
parser would have been dead code nobody noticed. **Controls now assert PER
SOURCE:** break one mark, and *that verdict* must stop being handed down, with
a separate full-strip case for the union.

### 37.5 A SUPPRESSOR WITH NO EXCLUSIVE CORPUS EXAMPLE IS A HOLE, AND I SHIPPED ONE

Chasing 37.4 showed `MARKED-DEAD-DOC` claims only **2** real sites, both on
hashes that resolve anyway: everything it would cover is already covered by
`MARKED-MAPPED`. It is KEPT rather than deleted -- declaring a document's SHAs
dead *without* a mapping table is exactly what you do when no honest twin
exists, and a guard that convicts that repair is a guard that gets switched off
-- but it is now controlled on a **planted** document, with its thinness stated
in the test's own docstring rather than left to look load-bearing.

### 37.6 THE ONE SHAPE RULE THAT SURVIVED, AND WHY IT IS ADMISSIBLE

`DIGEST_LENGTHS = {16}`. Not a guess: a printed table of what was seen at every
length over the guard's own candidate set -- 7 (186/29/22), 8 (1/0/0),
12 (10/2/0), 16 (0/0/3). Commit citations here are 7, 8 or 12 characters
(12 because `linkedin_server_info` reports `build.code.commit` at that width);
no resolving citation is 16, and all three 16-character tokens in a commit slot
are 64-bit content digests. Corpus-wide: 47 distinct 16-hex tokens, zero
resolve. `test_the_digest_bound_hides_no_resolving_citation` re-derives that
from the live corpus and reds if any 16-char token ever resolves. **The bound
excludes 16 ALONE** -- not 32, 40 or 64, because a full SHA is a legitimate
citation and a symmetrical-looking rule is not evidence.

### 37.7 DISPOSABLE, declared

The census, reconciliation and slot-measurement scripts written for this wave
(token extraction, kind bucketing, the boundary-difference finder, the
length-bound measurement) are **DISPOSABLE**. Everything durable in them is
either inside `check_cited_shas_resolve.py` or written out with its numbers in
`_audit/2026-09-20-the-sixty-dangling.md`. They are not registered.

### 37.8 THREE MORE, FOUND BY RUNNING THE FINISHED GUARD AT THE TREE IT WAS ADDED TO

Writing the controls found 37.4 and 37.5. Pointing the committed instrument at
the corpus it had just joined found three the controls could not, because a
guard's own documentation is part of the corpus it scans.

**A DOCUMENT QUOTING THE DECLARATION WAS TREATED AS MAKING ONE.** The audit
report for this wave quotes *"EVERY SHORT SHA IN THIS FILE IS DEAD"* twice, as
discussion. The unbounded pattern read it as a declaration and cleared every
citation in the reporting document: `MARKED-DEAD-DOC` 2 -> 9, and **the guard
got quieter**. Fixed positionally, bounded to the first 40 lines, against a
measured 3 and 3 for the two real declarations -- because a declaration is
something a reader meets BEFORE the citations it covers, so one at line 242
protects nothing at line 20.

**THIRD INSTANCE OF ONE SHAPE IN THIS REGISTER.** The correction-marker guard
read a sentence about markers AS a marker and fixed it by anchoring at line
start. 37.1 above quoted a planted citation into a live commit slot and was
convicted. Now this.

> **PROSE ABOUT A MECHANISM IS INDISTINGUISHABLE FROM THE MECHANISM TO A
> MATCHER THAT ONLY LOOKS AT SHAPE.** Every guard whose documentation lives
> inside its own corpus pays this, and the payment is always the same: the
> guard goes QUIET, never loud.

**MARKDOWN EMPHASIS INSIDE A PHRASE DEFEATED A MATCH.** This corpus writes
*"does **not** resolve"* as readily as the plain form, and every emphasised
disclosure was invisible to `do(?:es)\s+not\s+resolve`. Emphasis is stripped
before the search now; backticks are not, since a disclosure names its SHA in
them.

**THE GUARD CONVICTED ITS OWN TEST SUITE.** Two positive controls resolved
`HEAD` and asserted reachability. They passed all afternoon and went red the
instant the wave made its own commit -- because the suite runs from a
`worktree-agent-*` branch whose HEAD is not an ancestor of `master`, which is
precisely the defect the guard finds. **A test suite that assumes its own
branch is published is the same error as a wave reporting its work by a SHA on
that branch**, and it was committed in the file whose subject is that error.
Controls now resolve `master`, and `_on_master()` fails loudly rather than
skipping if it cannot.

---

## 41. THE REOPENER TRIGGERS: A WRITE-OFF THAT RESTS ON A FACT NOBODY RE-CHECKS, 2026-09-20

Full record: `_audit/2026-09-20-the-reopener-triggers.md`.

A write-off resting on a fact about the operator, his account or the world is
excluded WHILE THAT FACT HOLDS. With no stated reopener it reads exactly like a
permanent exclusion, and the census shrinks its own denominator by an amount
nobody ruled. The discipline already existed here and was applied to exactly
one queue -- `2026-09-05-decide-retire-rulings.md` s6 gives all twelve of its
retirements a concrete reopener AND names who can establish it. The other queue
was exempt, and the exemption was measurable: **15% still GAP with a reopener,
91% without.**

### 41.1 `scripts/check_contingent_writeoffs_carry_a_reopener.py` -- ADMITTED, SHOWN FAILING THREE WAYS

Fails the run if a write-off row is CONTINGENT (`WORLD-FACT` / `ACCOUNT-FACT` /
`PROCESS-FACT`, per the shipped classifier) and names no `REOPENER` in its
RESOLVED text. It imports `classify_writeoff_reasons` rather than reparsing.

**RESOLVED, NOT RAW, AND THAT IS LOAD-BEARING.** 127 write-off reason cells are
POINTERS and 21 rows carry no reason cell at all (`N 67`-`78`, `N 119`-`128`
ship four-column tables). A guard reading the raw cell would demand the
impossible of a fifth of the corpus.

**THE RED IS THREE REDS, AND EACH COVERS A BLIND SPOT OF THE OTHERS.** A verdict that
fires on an injected row proves nothing about whether the WALK would ever hand
it one -- that gap is exactly the shape of the decorative controls this repo
has been finding all day. So `--demonstrate-red` runs: (1) a synthetic row,
convicted, **plus the same row carrying a reopener, cleared** -- a rule that
convicts both is not discriminating, it is just failing; (2) an END-TO-END red
that copies the four census files to a temp dir, plants one row inside a live
table, repoints the walker and runs the shipped `build()` pipeline. It asserts
the walk FINDS the row, the guard FAILS, and the failure NAMES it; **(3) a cell
whose only reopener-shaped text is the sentence "reopens nothing", convicted --
see 41.4, the defect that made the first two insufficient.**

Four decorative holes closed and named in the docstring: per-slice liveness
(never a union assertion -- a union over a redundant corpus cannot detect a
lost source); SELF-RETIRING exemptions (the guard fails when a pinned row no
longer needs its pin); it prints what it did NOT check; and red 2 above.

### 41.2 `scripts/_check_cells_honours_escaped_pipe.py` -- ADMITTED, SHOWN FAILING

**THIS CLOSES SECTION 35's "NOT AN INSTRUMENT" ENTRY.** `cells()` split on `|`
without honouring the markdown escape. The control carries the pre-fix
implementation VERBATIM -- a control that describes a bug in prose cannot fail
when the bug returns -- and asserts the old code fails **exactly four of six**
specimens: the two carrying no escape must still pass, or the repair's subject
would be the parse in general rather than the escape.

Corpus half: old vs new over every line of five census files. **5 lines carry
an escaped pipe, 5 lines differ, and the sets are equal** -- the repair does its
job and nothing else. `J 103`: 795 chars read of the 1320 it holds.

**AN EMPTY DISAGREEMENT SET IS A LOUD EVENT.** If the corpus stops carrying an
escaped pipe the corpus half exercises nothing, so it says so and returns
non-zero rather than printing ok over a vacuum.

**NO REGEX, DELIBERATELY.** The standard lookbehind for "a backslash not
preceded by a backslash" is wrong at a doubled backslash; a left-to-right scan
has no such case to get wrong.

**AND IT MOVED NOTHING BUT THE TEXT**, which section 35 required of any
notation change over these files: census counts identical before and after, and
`classify_writeoff_reasons.py --tsv` byte-identical on all six verdict columns
for all 310 rows.

### 41.3 THE LAWS THIS WAVE ADDS

**A REOPENER BELONGS WHERE THE CONTINGENT FACT IS ASSERTED, NOT ON EVERY ROW
THAT INHERITS IT.** 16 of the 37 repaired rows resolve through a pointer into a
shared ruling and 10 have no cell to write in. Copying a clause onto 37 cells
is hand-maintenance by another name -- the classifier's own design section
rejected the in-cell tag because a sibling rewriting a reason leaves the tag
behind, and a WRONG tag that travels with a row is worse than none. **The cost
is that a backreference resolves BY POSITION and can silently re-point, which
is the argument for a GUARD rather than a one-time repair.**

**A WORLD-FACT SITTING BESIDE A RULING IS COLOUR, NOT THE LOAD-BEARING REASON
-- AND A REOPENER WRITTEN ON THE COLOUR IS A TRIGGER THAT CAN NEVER FIRE.**
Five rows are this shape. `N 10` asserts *"LinkedIn DOES offer this"*, which is
the live-LOOKING half and reopens nothing: it is already true and the row is
excluded anyway by `R5`, which is ours and is the half that can actually move.
`P D13`/`D14`: a Help article resolving supplies field names and does not touch
the `/edit/` ruling. Those cells now say so explicitly, because **a reader who
takes the contingent-looking clause for the trigger has it exactly backwards.**

**A TRIGGER THAT EXISTS IN CODE AND IS NOT NAMED IN THE CELL IS INVISIBLE.**
`N 118`'s reopener had been shipping since 2026-09-04 --
`dom.read_profile_detail_entries` re-takes the reading on every call. It lacked
the word `REOPENER`, so no sweep could see it and the row read as permanently
closed. Zero new code, one clause.

**A MEASUREMENT IS NOT A RULING, AND THE CENSUS HELD ONE FACT UNDER TWO STATE
WORDS.** `J 127`, `M M4` and `N 157` assert that the InMail balance is not
rendered; `J 127` read MEASURED-ABSENT and the other two read EXCLUDED-RULED.
`M M4` and `N 157` are now MEASURED-ABSENT. Three supports, none of them this
wave's: `9a140a3` files `M 4` as WORLD-FACT in the table built to draw that
line; `network.md` s2's definition fits unstretched; and **`readonly.py` ADMITS
`/premium/my-premium/` -- a row whose page we are allowed to open, and did
open, cannot be written off as a refusal.** `2026-09-20-the-first-firing.md`
s4d named the defect, declined it on timing and wrote *"the owner of the state
vocabulary can rule it in one line"*; this is that line. GAP untouched, 704
stated rows untouched.

**AND THE HANDED-DOWN NUMBER WAS RIGHT ABOUT THE WRONG POPULATION.** The brief
said ~40. Over all write-off states it is exactly 40; over `EXCLUDED-RULED` +
`XR` it is **37**. The other three sit in `COVERED-CANNOT-DELIVER` and
`MEASURED-ABSENT`. Re-deriving cost one run of a shipped instrument.

### 41.4 THE GUARD WAS GREEN ON A CELL THAT SAID THE OPPOSITE, AND ONLY A MUTATION FOUND IT

**The first version of 41.1 could not fail in the exact case it exists for.**
It reused `classify_writeoff_reasons.REOPENER`, which is
`REOPEN(?:ER|S)\b` CASE-INSENSITIVE. That is right for its own job -- reporting,
where over-reach is free -- and wrong for a gate, because it matches the
ordinary verb.

Found by MUTATION, never by re-reading: stripping the real `REOPENER:` clause
out of `P D13` and `P D14` left the guard **green**, because both cells also
contain the sentence *"the Help-article half REOPENS NOTHING"*. **A cell could
state in prose that nothing reopens it and thereby satisfy a check whose entire
subject is whether something does.** The sentences were written by this wave, in
the same pass, for a good reason (see 41.3) -- which is the uncomfortable part:
the guard and the text that defeated it came from one author on one afternoon.

**THE DISCRIMINATOR IS CASE, AND IT WAS MEASURED BEFORE IT WAS ADOPTED.** The
house marker is always SHOUTED (`REOPENER:`, `REOPENER, NAMED:`, `REOPENER a
parser over either capture`); the ordinary verb is not. Over the whole corpus
exactly **five** contingent rows pass the loose regex with no shouted marker,
and all five are the `D13`/`D14` family that prompted this -- so tightening to
`REOPENER\b` convicts the mutation and **moves nothing else**.

**NOT NARROWED FURTHER, DELIBERATELY.** `REOPENER: none plausible` and
`REOPENER: nothing that keeps the shape` must keep passing -- an argued "this is
genuinely permanent" is a real answer to the question, and three of
`decide-retire-rulings.md` s6's twelve are written that way. **The defect is an
UNMARKED sentence, never a negative verdict somebody defended.**

It is now RED 3 of the guard's `--demonstrate-red`, asserting both halves: that
the loose regex DOES match the negative sentence (or the control has stopped
exercising the defect) and that the shouted marker does NOT.

**THE LAW: A GATE MAY NOT BORROW A REPORTER'S PREDICATE.** The same regex is
correct in a report and decorative in a guard, because over-matching costs a
reporter nothing and costs a gate everything. Reuse the instrument, re-derive
the threshold.

### 41.5 A GUARD NOBODY RUNS HAS ALREADY STOPPED WORKING

`tests/test_contingent_writeoffs_carry_a_reopener.py` wraps 41.1 so CI runs it,
following `test_pointer_graph_guard.py`. Two tests, and **the second is the one
that matters**: a green property test is ambiguous between "the census is
clean" and "the guard was broken into something that cannot speak" -- an import
returning nothing, a walk finding no rows, a predicate inverted. So the second
test re-runs `--demonstrate-red` and asserts each red's marker string
individually, because a demonstration that silently skipped its expensive half
would still exit 0.

### 41.6 PROSE WRITTEN INTO A CLASSIFIED CORPUS IS DATA, NOT COMMENTARY

**The pointer-graph guard convicted this wave, on four words.** A reopener
added to `P D14` contained *"each on his own ruling"*; `his own` matches the
shipped `AF:his-thing` signal, so `D14`'s verdict moved to include
`ACCOUNT-FACT` -- and `D15`-`D17`, which resolve to `D14` by backreference,
were suddenly resting on an argument different from the one they were pinned
against. `P D14` is an `/edit/` family row and nothing about it is a fact about
the account.

**THE GUARD OFFERS `--pin` AS THE REMEDY AND TAKING IT WOULD HAVE BEEN WRONG.**
Re-pinning bakes the new verdict in; here the new verdict was a false
`ACCOUNT-FACT`, and it would have propagated to three inherited rows. **A
re-pin makes the guard agree with whatever you just did, so the question a red
pin asks is "did you mean this", never "make this go away."** Reworded; the
verdict returned and the pins held untouched.

**SO EVERY KIND CHANGE A CENSUS EDIT CAUSES GETS DIFFED, THE WAY A PARSER
CHANGE DOES.** These cells are INPUT to a running classifier with 12 pinned
adjudications and 69 pinned pointers hanging off them. This pass moved three
verdicts, kept two deliberately (`M M4` gains `ACCOUNT-FACT` and thereby AGREES
with its twin `J 127`; `N 10` fires `operator-must-act`, the same phrasing the
`CONTACT-IMPORT` reopener uses) and reworded one.

**AND A `+-2` LINE WINDOW OVER A MARKDOWN TABLE IS A `+-2` CAPABILITY WINDOW.**
The correction-findability scan flagged `M M5`, which no wave touched: it sits
one line under `M M4`, whose cell now opens `STATE CORRECTED`. Every table row
is one line, so the heuristic's reach is two neighbouring capabilities. That is
a real cost of the window on this corpus, paid in a triage entry exactly as its
own comment says it should be.
