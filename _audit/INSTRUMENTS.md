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
