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

**How a red-proof is run here.** Never in the live tree -- several agents write
`linkedin_server/` concurrently and mutating a shared file even briefly can be
picked up or clobbered. Copy `linkedin_server`, `tests`, `scripts` and
`pytest.ini` to a scratch directory, **print `linkedin_server.__file__` and
confirm it resolves under the copy before touching anything**, plant ONE
mutation, run ONLY the selector that should die, restore by re-copying that one
file, repeat. Finish on a clean control run.

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
