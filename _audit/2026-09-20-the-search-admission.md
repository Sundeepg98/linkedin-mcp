# THE SEARCH ADMISSION: a condition nobody came back to close, closed

**CORRECTS:** `_audit/2026-09-19-search-admission-preconditions.md` -- its section C and its section D item 3 tell the admitting wave to DELETE `tests/test_the_search_results_address_is_refused_before_admission.py`, an instruction the lead superseded at 2026-09-19 13:05, about twenty minutes after that document was written: the ruling is INVERT, not delete, so the transition stays recorded. Its measurements are unaffected; only that instruction is. Detail in section 4.4.

> Wave `search-admission-close`, 2026-09-20. **No browser was opened and no
> LinkedIn page was loaded.** A sibling wave held the single signed-in Chrome
> profile for this round; every number below comes from code on disk, from
> fixtures, or from the shipped classifier driven under V8 by `node`.

`tests/test_every_orphan_module_is_ruled.py` carried
`DELIBERATELY_UNWIRED["search_results"]`: **a capability held on a written
condition**, where `linkedin_server/search_results.py` and its 963-line test
file landed 2026-09-19 and the navigation admission deliberately did not,
because *"a search results page IS a list of other people ... so the admission
is held on the rule that it and a name-free shaper land TOGETHER OR NEITHER
LANDS."* The entry ended: *"THE WAVE THAT WROTE THIS ENDED BEFORE WIRING
IT."*

**All four things that entry named have landed, in one commit. The condition
is CLOSED. A different and smaller gap is now open, it is named below, and it
is not the one the entry was holding.**

---

## 0. THE VERDICT, STATED BEFORE THE EVIDENCE

| the entry required | state |
|---|---|
| a name-free shaper, **proven** | **LANDED.** Proven by measurement, and the measurement found a real leak first |
| the navigation admission for `/search/results/` | **LANDED**, as the people vertical only (candidate S1) |
| a tool that calls it | **LANDED**, `linkedin_people_search_shape` |
| deletion of the held entry | **LANDED**, and there were **TWO** entries, not one |

**WHAT IS NOT ESTABLISHED, AND IT IS NOT THE HELD CONDITION.** This shaper has
never met a live search PAGE. No capture of a `/search/` surface exists in this
repository and none could be made this round. So its **fit** to LinkedIn's
rendered dialect is unmeasured: whether the filter selectors match, whether the
counts are populated, whether the bare address serves a page at all.

**THAT IS A CORRECTNESS GAP, AND THE CONDITION WAS A NAME-FREEDOM ONE.** The
argument joining them is one sentence and it is the crux, so it is stated
rather than left to be inferred:

> **A SHAPER THAT IS COMPLETELY WRONG ABOUT THIS PAGE STILL CANNOT EMIT A
> NAME.** Both readers build their return value out of integer accumulators
> and the Python side rebuilds a fixed set of integer fields from it, so a
> mismatched selector produces WRONG COUNTS, never a leaked string. The
> failure mode of being wrong here is a zero, and a visible one --
> `unmatched_controls` and `values_refused` are in the payload precisely so a
> caller can tell a wrong selector from an empty page.

So the held condition does not depend on the unmeasured thing. **Both
sentences are true at once and collapsing them in either direction would be
the over-claim this campaign exists to stamp out.**

**AND THE ADDRESS, UNLIKE THE PAGE, HAS MET REAL LINKEDIN OUTPUT.** Seven
people-search URLs that LinkedIn itself wrote were already sitting in tracked
captures of OTHER surfaces, and the shipped pattern admits all seven -- section
4.3a, shown failing on two plants.

A reader who wants "the capability is delivered" rather than "the condition is
discharged" should read section 6 and treat this as one browser slot from done.

---

## 1. WHAT `search_results.py` EMITS, FIELD BY FIELD

Derived by calling the real functions, not read off the source.

### 1.1 The two functions that touch a page

`read_results(page, html="")` and `read_filters(page, html="")` are the only
functions in the module that reach a document. Every field either returns is an
`int` or a `list[int]`:

| `read_results` | kind | what it is |
|---|---|---|
| `anchors_seen` | int | how many `<a>` the page held |
| `counts` | list[int] | one count per `RESULT_KINDS` position, 14 long |
| `queries_present` | int | how many hrefs carried a query. **Never what was in it** |
| `numeric_entity` | int | entity segments that were all digits |
| `non_numeric_entity` | int | entity segments that were not |
| `values_refused` | int | **NEW 2026-09-20.** Fields the page answered with a non-integer |

| `read_filters` | kind | what it is |
|---|---|---|
| `controls_seen` | int | the denominator: pressable controls found |
| `counts` | list[int] | one count per `FILTER_TERMS` position, 14 long |
| `matched_controls` | int | controls that matched the shipped vocabulary |
| `unmatched_controls` | int | **the denominator that matters**: a changed selector is visible here rather than silent |
| `empty_labels` | int | controls with no accessible name |
| `values_refused` | int | **NEW 2026-09-20** |

**No string appears in either payload, on any path.** Not a label, not an href,
not a slug, not a query.

### 1.2 The functions that return strings, and why none of them can carry one

Seven public functions return a `str` or a set of them. **Not one of them can
return a string that came from a page**, and the reason differs per group:

* `term_for`, `filter_term_for`, `value_class_for` take an **`int` index** and
  return a literal from a tuple defined in the module. Out of range returns
  `"index_out_of_range"` -- **refused, never clamped**, because index 0 is
  `person_result` and a clamp would rename a page of people into a page of
  companies.
* `emitted_alphabet`, `filter_alphabet` return the closed sets themselves.
* `control_fixture`, `filter_control_fixture`, `adversarial_traversal_route`
  return **the module's own synthetic test markup**, every slug carrying
  `example`.
* `classifier_source`, `filter_matcher_source`, `filter_normaliser_source`
  return **JavaScript lifted out of `dom.py` by brace matching** -- shipped
  source code, not page content.

### 1.3 The one place a document string exists, and where it dies

Inside the page. `dom.SEARCH_RESULTS_JS` reads `href`; `dom.FILTER_PANEL_JS`
reads `aria-label` / `textContent`. **Both compare in the page and return an
integer index**, which is the shipped `groups.py` -> `menus.py` -> `anchors.py`
engine. The vocabulary is shipped IN; a position comes OUT. On this surface
that is not hygiene: a filter label is routinely `Connections of <a person>`,
so the matching happens one layer earlier than `menus.py` does it, precisely
because `menus.py`'s surface has labels that are UI verbs and this one does
not.

---

## 2. THE NAME-FREEDOM PROOF -- AND THE LEAK IT FOUND

**This is a measurement. It was run, it went red, and the red was real.**

### 2.1 What was measured

The two readers were driven with a page whose `evaluate` answers with strings
instead of numbers -- markers planted in every position a document value can
occupy: inside `counts`, in a scalar, as a dict key, nested, and as the whole
payload. Both the **returned value** and any **raised exception** were walked
with `tests/leakwalk.walk`, the repository's own total walker (dict keys as
well as values, bytes both ways, exceptions as `str`, `repr` and per-argument).
That walker was **imported, not rewritten**; this repo has a scar for
re-writing a check it already ships.

### 2.2 THE RESULT: THREE LEAKING PATHS, BEFORE THE FIX

    read_results   a string inside counts            LEAKS VIA EXCEPTION
    read_results   a string in the anchors scalar    LEAKS VIA EXCEPTION
    read_filters   a string inside counts            LEAKS VIA EXCEPTION

    ValueError: invalid literal for int() with base 10: '<the planted name>'

**`int()` puts the value it refused verbatim into its own exception.** The
shipped coercion was `int(value)`. That exception leaves the reader, is caught
by `server._error`, and is rendered through `config.scrub` -- **which
substitutes this server's own PATHS and nothing else**, because a name has no
shape to scrub, a fact `tests/test_no_committed_identity.py` states in its own
first line. So the string reached the caller intact.

**The module's docstring claimed "no string from the document, by
construction".** The construction had an exception-shaped gap in it, and an
integer-only *return value* does not close it, because an exception is not a
return value. The admitting ruling names *"a measured case of the shaper
emitting a name, a slug, a member id or an urn"* as the thing that **revokes
the admission**. This was one, found before the admission rather than after it.

### 2.3 The repair

`_as_int` / `_counts_only` / `_scalars_only` in `search_results.py`. They never
raise and never quote their input: the only things they can return are an
integer they were given and `None`. A refused value is **substituted, never
dropped** -- `counts` is positional and dropping an entry renames every kind
behind it -- and the substitution is **counted** into `values_refused`, so the
anomaly is a visible integer instead of a silent shift or a raised string.

`tally` and `tally_filters` were repaired the same way. Their docstring already
said they *"cannot be handed a needle even by mistake"*; that was a claim about
the parameter's type while the mechanism said something weaker, and it is now
true of the behaviour.

### 2.4 After: ZERO

    LEAKING PATHS: 0

with `values_refused: 1` reported on each formerly-leaking case.

### 2.5 THE GUARD, SHOWN FAILING

`tests/test_the_search_shaper_emits_no_name.py` (35 assertions, green) is the
standing guard. **It is not admitted on the strength of a green run.**
`scripts/_check_the_shaper_leak_guard_can_fail.py` re-runnable, one process:

      case                                          planted   restored
      read_results/a string inside counts           red       GREEN
      read_results/a string in the anchors scalar   red       GREEN
      read_filters/a string inside counts           red       GREEN

    PASS: 3 of 3 went RED under the shipped-until-today coercion and GREEN
          again on its removal.

**The planted defect is not an invented mutation -- it is the code that
shipped**, restored by pointing `_as_int` back at `int`. A control whose defect
is the real previous state needs no argument that it is representative.

The guard file also carries its own internal controls: a detector shown seeing
a plant in a plain return value, in a nested structure, and as a dict key; and
a reader that echoes the page, shown going red.

### 2.5a WHAT THIS PROOF DOES NOT COVER, NAMED RATHER THAN LEFT IMPLICIT

The proof covers the two channels this module owns: what the readers RETURN
and what they RAISE. **There is a third channel and it is not this module's
to close:** an exception raised inside `page.evaluate` by the driver itself,
before the reader gets an answer at all.

Read honestly: the shipped scripts build their return value from integer
accumulators and never interpolate a document string into a thrown error, so
nothing here is known to carry page content out that way -- but that is a
property of `dom.py` and of Playwright, not something the reader can enforce,
and it is **UNMEASURED** rather than proven. It is also not specific to this
surface: every `page.evaluate` in the package shares it. Filed as a general
property, in the same class as the normalisation finding the pre-admission
wave filed and did not fix.

### 2.6 THE DETECTOR WAS WEAK AND ITS OWN CONTROL CONVICTED IT

Worth reporting because it is the kind of thing a wave normally discovers after
the freeze, and because the lead will check this proof.

The tool-level assertions needed a control: a payload that DOES publish the
landed url. The fake browser lands where a browser really lands, and there the
planted name is **percent-encoded**:

    hunted:    Exampleperson Markersurname
    published: ...?keywords=Exampleperson%20Markersurname

**The detector reported that payload CLEAN**, which means every no-leak
assertion in the file was hunting a spelling this surface does not use -- a
query string is exactly where a space stops being a space.

Repaired by generating the hunted set from `leakwalk.url_spellings`, the
shipped helper that exists for this precise scar (a fixture once leaked a real
job title while its check reported *"69/69 forbidden strings absent"*). **2
literals became 9 spellings.** Not repaired by adding `%20` to a hand-written
list, which would have fixed this instance and left the next encoding to be
found the same way.

**The production code was never wrong here** -- the tool publishes a boolean,
not the landed url. What was wrong was the instrument that certified it.

### 2.7 The shipped decision, driven at name-shaped input under V8

`classifyRoute` is lifted out of `dom.SEARCH_RESULTS_JS` by brace matching and
run under `node` over addresses carrying a planted name and slug -- including
`/in/<slug>/`, a `?keywords=<name>` query, and a traversal onto a profile.
Every verdict is integers, and every `term` is inside `emitted_alphabet()`. The
runner is **imported from the shaper's own suite**, not transcribed.

---

## 3. WHICH FIXTURE ROUTE, AND WHY -- STATED PLAINLY

**Route 1 (an existing real capture of a list-of-people page) DOES NOT EXIST.**
Measured two independent ways:

1. `tests/test_no_committed_identity.py` documents
   `tests/fixtures/connections_list.html` as *"Five invented people on an
   invented page: that surface has never been opened by this server, so there
   was no capture to sanitise and nothing here was ever anybody's."*
2. The file's own header says *"IT IS NOT A CAPTURE"*. Structurally: 7727
   bytes, 8 distinct class names, zero `artdeco-*`, zero `data-*`, zero hashed
   classes -- against `job_detail_following_hydrated.html`, a real capture in
   the same directory, which is dense with LinkedIn's hashed-class dialect.

And **no tracked fixture anywhere came from a `/search/` page.** The string
`search/results` appears in four tracked files and in every case it is an
outbound href sitting inside a capture of a *different* surface.

**So Route 2 was the only route available, and I could not have made a capture
without a browser I was told not to touch.**

**BUT THE NAME-FREEDOM CLAIM DOES NOT REST ON A FIXTURE, AND THAT IS NOT A
CONVENIENT ARGUMENT -- IT IS WHY THE PROOF IS STRONGER THAN A FIXTURE WOULD
BE.** Name-freedom here is **input-independent**: the page script builds its
return value out of integer accumulators, and the Python reader rebuilds a
fixed set of integer fields from it. The set of strings that can cross is empty
*for every input*, not merely for the inputs somebody thought to try. A hostile
payload is therefore a **strictly stronger probe than any capture** -- it hands
the reader values no real page would ever produce and asks whether they cross
anyway. A capture would have exercised one input; the adversarial payload
exercises the shape of all of them.

**What a capture WOULD have settled, and nothing here does: correctness.**
Section 6.

---

## 4. THE ADMISSION

### 4.1 The spelling that landed, and the four that did not

    S1   ^https://www\.linkedin\.com/search/results/people/?(\?[^#]*)?$

**Re-measured 2026-09-20** by `scripts/_probe_search_admission_blast_radius.py`
over its 90-address corpus. **The pre-admission audit took its numbers against
32 patterns on disk; there were 41 when I ran it.** Re-derived anyway, because
a figure taken against a different boundary is a figure about a different
boundary:

| candidate | newly admitted |
|---|---:|
| **S1** people only -- **SHIPPED** | **5** |
| S2 four verticals | 8 |
| S2b three verticals with rows | 7 |
| W1 `/search/.*$` anchored (counterfactual) | 18 |
| W2 `/search/` prefix (counterfactual) | 18 |

Identical to the audit's figures despite the pattern count moving 32 -> 41,
which is itself worth recording: the candidates' blast radii are stable against
nine unrelated admissions.

**The number that carries information is 18 against 5.** No forbidden substring
names *any* `/search/` address, so everything in that column is defended by
nothing but the absence of a rule -- **including the address this entry is
for**, which is exactly why the shaper is the condition rather than the
allowlist.

**The wildcard's extra fifteen include an account-ending address.**
`/search/results/people/../../mypreferences/d/close-account` is admitted by W1
and W2 and named by no forbidden substring; the denylist refuses its siblings
`/psettings/` and `/invite` and misses this one. **The anchor is not what
refuses it -- the closed segment is.** W1 is anchored at both ends and admits
it exactly as the bare prefix does.

### 4.2 Why people only, when three more rows sit one alternation away

S2b would have served 19 of 20 reads instead of 16. It was refused, and this is
a judgement call I own:

* This is the **first admission on a third-party-dense surface** and the ruling
  says in as many words that it is the one most likely to be cited later as a
  precedent for something weaker.
* S1 introduces **no new shape to review**: `(\?[^#]*)?$` is what
  `/jobs/search/` and `/notifications/` already carry.
* S2b would have **contradicted a sibling wave's committed guard**
  (`MUST_STAY_REFUSED` lists groups and events), which I would have had to
  overrule while its author was not present.
* **Widening has a named route.** The ruling's own reopening clause treats
  *"the narrow pattern is TOO NARROW to serve the 20 rows"* as a request to
  widen that **gets its own blast radius**. Groups, events and content should
  take that route and arrive with their own measurement.

### 4.3 What the admission does NOT open

Verified against the shipped predicate, not by reading the regex:

    ADMIT   /search/results/people/            /search/results/people
    ADMIT   /search/results/people/?keywords=x
    refuse  /search/results/people/../../mypreferences/d/close-account
    refuse  /search/results/{groups,companies,all,schools,events,jobs,content}/
    refuse  /search/results/peoplefinder/        (the containment trap)
    refuse  /search/results/people/some-slug/    (NO SUB-PATH: no person is addressable)
    refuse  /psettings/member-account/close-account

**`/search/results/people/<anything>/` is refused.** The pattern takes no
sub-path, so the admission cannot be walked from a list of people to any one of
them. That is load-bearing rather than incidental.

### 4.3a THE ONE PIECE OF REAL-LINKEDIN EVIDENCE THIS SURFACE HAS OFFLINE

No capture of a `/search/` PAGE exists. **But LinkedIn links TO the people
search from pages that WERE captured**, so three tracked fixtures carry search
URLs *the platform itself wrote*: the profile-views analytics page draws
"search for who viewed you" links, and a job-detail capture carries a canned
search.

    distinct LinkedIn-authored people-search hrefs found   7
    admitted by the shipped pattern                        7 of 7

They carry `keywords`, `origin`, `currentCompany` and `pastCompany` in varying
order, and one of them has no `keywords` at all. Pinned as
`test_the_pattern_admits_the_spellings_LINKEDIN_ITSELF_EMITS`, which reads
them from the fixtures at run time and never writes them down -- they carry
real query values.

**SHOWN FAILING, on two planted patterns:**

    shipped pattern                  GREEN
    plant: pattern with NO query     red -- refuses an address LinkedIn emits
    plant: admission removed         red
    restored                         GREEN

**This settles the query clause with evidence rather than style.** A
people-search pattern that admitted only the bare address would refuse EVERY
spelling the platform actually produces; `(\?[^#]*)?$` is load-bearing, not
house habit. It also means the structured-query candidate S3 was never as
cheap as it looked -- it would have had to match these four parameters and
their escaped forms.

**WHAT IT DOES NOT ESTABLISH:** anything about the PAGE. It is evidence about
the address, which is the half that could be had offline.

### 4.4 The guards that fired, and the one that did not

**TWENTY-ONE ASSERTIONS ACROSS FIFTEEN FILES WENT RED**, and all of them were
cleared by recording what happened, never by narrowing. **Only nine of them
were in the files this change obviously touches.** The other twelve were found
by running the whole suite, which is the instruction this wave was given
because master was pushed red earlier today on an impact-scoped gate:

* two ratchets in `tests/test_readonly.py` (section 4.4a below);
* `test_the_module_admits_nothing`, which caught this wave's own comment;
* and **six stale COUNT assertions across four files** --
  `test_server_surface` twice over (the total, then `EXPECTED_TOOLS` and the
  read/write split behind it), `test_every_tool_is_on_the_surface`,
  `test_prose_that_makes_a_claim` reading `server.py`'s own module docstring,
  and two in `test_the_other_two_count_claims_are_pinned_too` reading
  `README.md` -- plus `README.md`'s opening headline, which asserts against
  the live registry and was repaired before its test was run, so it is not in
  the eighteen.

**A LANDED TOOL MAKES SEVEN SEPARATE PROSE AND PIN CLAIMS STALE AT ONCE**, in
two files that no impact analysis would reach from a symbol -- `README.md` and
a module docstring -- and not one of those sites mentions `search`, `readonly`
or any symbol in this diff.

* and **three boundary guards belonging to three unrelated surfaces**, each of
  which had used this very address as its canary (section 4.4b). Those three
  were invisible until the whole suite ran, and they are the most interesting
  of the twenty-one.

**AND THE OBVIOUS CONCLUSION FROM THAT IS WRONG, MEASURED.** The sentence this
paragraph first carried was *"a gate scoped to what this diff names would have
had to reach README.md from an edit to server.py to see six of these"*, which
is a good line and is refuted by running the gate. `scripts/impact_gate.py
--plan-only` on this diff:

    impact set   131 of 186 test files (70%)
    verdict      WIDENING TO THE FULL SUITE, because the impact set is at or
                 above the 45% line where running everything costs about the
                 same and answers more
    plus         14 CORPUS-WIDE guards, run unconditionally

**So the shipped impact gate would have caught all six.** It selects
`test_every_tool_is_on_the_surface` directly -- *"via linkedin_server/server.py
-> names the path"* -- and then widens past the question entirely.

The honest reading is narrower than the rhetorical one and more useful: **the
danger is not an impact-scoped gate, it is a gate whose impact set is small
enough to feel safe.** This diff touches `readonly.py` and `server.py`, which
nearly everything imports, so its impact set was never going to be small. A
diff that touched only `README.md` and a census `.md` is the shape that gets a
tiny set, and that is the one this repository was bitten by this morning. The
full-suite instruction was still right for this wave; the reason is that the
run is cheap insurance on an admission commit, not that the gate is broken.

The nine in the obvious files:

* `test_every_search_results_address_is_refused_today` -> **inverted**, split
  into `_ADMITTED_NOW` (3) and `_STILL_REFUSED` (5).
* `test_one_narrow_pattern_is_all_that_stands_between` -> **rewritten to run
  the rollback in the LIVE direction**: it now removes the shipped pattern from
  the live tuple, asserts exactly one pattern was removed, and asserts the
  refusal returns. Before the admission only the hypothetical direction was
  runnable.
* A new `test_the_narrow_candidate_on_record_is_the_one_that_shipped` asserts
  the measured candidate string and the shipped line are byte-identical, so the
  blast-radius numbers cannot come to describe a different artifact.
* `test_search_admission_blast_radius.ADMISSION_TARGETS` -> **split, because
  its two-address prediction half came true.** `/search/results/all/` was
  predicted a target on 2026-09-19 and the admission did not buy it. The failed
  prediction is kept visible as `PREDICTED_BUT_NOT_ADMITTED` and asserted still
  refused, rather than edited down to the outcome.
* The AST boundary freeze and the tool-surface pin were re-pinned.

**`MUST_STAY_REFUSED` (12 addresses) did not go red.** That is the measurement
saying the admission is narrow, and it is the most informative green in this
wave.

### 4.4b THREE OTHER WAVES HAD USED THIS ADDRESS AS THEIR CANARY

**THE MOST USEFUL THING THIS WAVE LEARNED, AND ONLY THE FULL SUITE COULD HAVE
SHOWN IT.** Three boundary tests belonging to three unrelated surfaces each
asserted that `/search/results/people/` stays refused, as the example of what
THEIR admission must not have reached:

    tests/test_premium_four_boundary.py        test_the_neighbours_stay_refused
    tests/test_search_appearances.py           test_the_neighbours_of_that_address_are_still_refused
    tests/test_analytics_creator_boundary.py   test_the_address_this_reading_informs_is_still_refused

**A REFUSED ADDRESS IS LOAD-BEARING FURNITURE IN OTHER WAVES' GUARDS.** It is
the nearest dense third-party surface, so it was the natural thing to point at
when writing "my pattern did not leak into the neighbourhood" -- and admitting
it breaks every one of those sentences at once, in files whose subject has
nothing to do with search.

**NONE OF THEM WAS DELETED AND NONE WAS WEAKENED.** In each case the property
worth guarding was never "that one url is red", it was "THIS admission does
not reach the search family". So each canary was replaced by two spellings
that are still refused -- `/search/results/people/<a sub-path>` and
`/search/results/companies/?keywords=x` -- and the sub-path makes each guard
**strictly stronger than it was**, because it is the spelling that would
address one PERSON rather than the page listing them, and the shipped pattern
takes no sub-path.

The `search_appearances` one needed more than a substitution and got it. Its
case existed because that reading was commissioned to INFORM a ruling on people
search, so admitting the page under consideration would have been using one
load of it as the evidence that authorises it. **That bootstrap is still
forbidden and is not what happened** -- the admission rests on its own ruling,
its own 90-address blast radius and a shaper, none of which is that reading --
and its docstring now says so, because the distinction is the whole reason the
case was written.

### 4.4a THE RATCHET

**A RATCHET IN `tests/test_readonly.py` FIRED.** Two entries there named a
people-search address: one in the blocked-url list, one in
`test_no_previously_forbidden_address_became_readable`. The second carried its
own instruction -- *"pinned here so that admitting it later is a DELIBERATE
EDIT to this table rather than a side effect of some other widening"* -- and
this is that edit.

Both were handled the way the company-page transition four lines below them was
handled on the same day: **recorded rather than silently dropped, and replaced
with the neighbours the admission must NOT have carried.** Two entries became
twelve -- the sub-path (so no row on the page is addressable), the traversal
onto the account-ending address, all six sibling verticals, both family roots,
and the `peoplefinder` containment trap. `tests/test_readonly.py` collected 274
with 2 of them red on this change, and collects 284 all green after -- the ten
are the replacements. **The ratchet is stronger after the admission than
before it**,
which is the only honest way to spend one.

**A STALE INSTRUCTION WAS FOUND AND FLAGGED RATHER THAN OBEYED.**
`_audit/2026-09-19-search-admission-preconditions.md` sections C and D.3 tell
the admitting wave to **DELETE** the revert test. That document was written at
12:46; the lead ruled **invert, not delete** at 13:05 and both guard files were
brought into line. That audit doc was never updated, so it still carries an
instruction that would undo the ruling if followed.

**AND MY FIRST ANSWER TO THAT WAS WRONG, AND A GUARD SAID SO.** I recorded the
correction only in the revert test's docstring, on the reasoning that the
audit doc belongs to another wave and should not be edited. Then
`test_a_correction_is_findable_from_the_claim` went red on this very
document: a `CORRECTS:` marker without a `CORRECTED BY:` back-pointer in the
TARGET is the defect that file exists to prevent, because **a reader starting
from the stale instruction has no way to reach the document that corrects
it.** Declining to touch another wave's file is exactly how that happens.

So the pair is declared properly: a one-line `CORRECTS:` marker at the head of
this document, and a one-line `CORRECTED BY:` back-pointer at the head of
section C of theirs -- additive, naming the superseding ruling, and explicit
that the section's MEASUREMENTS are unaffected and only its instruction is.

---

## 5. THE TOOL

`linkedin_people_search_shape`, **no parameters.**

**Taking no keyword is the privacy design, and it also dissolves a problem the
admitting wave inherited.** A search query is where a person's name is typed;
a tool that accepted one would take a needle as a parameter one layer above
where `test_no_address_or_needle_is_a_parameter_of_any_function` reaches.
Separately, `_audit/2026-09-19-search-admission-preconditions.md` B.4 measured
that **8 of 11 ordinary search keywords** (`password`, `settings`,
`invitation`, `visibility`, `cookies`, ...) are refused by the
forbidden-substring list, and handed the admitting wave the problem of what a
keyword-taking tool should answer when a caller's word trips a write guard.
**It takes no keyword, so the question does not arise.** That inherited item is
discharged by design rather than answered.

It publishes `results.by_kind`, `filters.by_term`, `filters.by_value_class`
(including `person_valued_filters` -- the page offers a way to search *by* a
person, and this server cannot learn or report which), and `denominators`
including `values_refused`. It publishes a **boolean** for whether it landed
where it was sent rather than the landed url, because a landed url is a value
the browser chose and on this surface it can carry a query.

**Condition 5 (nothing is fired) is structural here**: the coroutine reaches
only the two readers, neither takes a confirm token, and nothing presses,
connects, sends or follows a row's control.

The payload carries a `not_claimed` list. **A tool may not claim more than it
ran**, and this one has never run against LinkedIn.

---

## 6. WHAT REMAINS -- ONE BROWSER SLOT

Everything here needs the signed-in profile and nothing else.

1. **Open `/search/results/people/` once and capture it.** Then: does the bare
   address (no query) serve a populated page, or an empty state, or redirect?
   `landed_where_it_was_sent` answers this in the payload.
2. **Do the filter selectors match?** `unmatched_controls` is the number to
   read. A large value with `matched_controls: 0` means the selector list in
   `dom.FILTER_PANEL_JS` does not match LinkedIn's dialect -- the failure is
   visible rather than silent, which is what the denominator is for.
3. **Are the live filter labels decorated?** The module records a measured
   limit: a control labelled `Keywords (first name, last name)` does NOT match
   the single-word term `keywords`, and the census's own wording for `N 93` is
   that decorated form. **The repair, if so, is to add the decorated form to
   the vocabulary as its own phrase -- never to loosen the matcher**, because
   loosening is the mutation that makes `Connections of` match `connections`
   and reports a person-valued filter as a degree filter.
4. **Build the capture-then-scrub fixture**, following
   `scripts/_build_follow_fixtures.py`, which is this repo's only genuine
   capture-then-scrub precedent: the raw capture is deliberately NOT committed
   and the script is the provenance record of what was removed and renamed,
   *"which is the thing a privacy review needs and cannot get from the output
   alone."* Raw capture to gitignored `_state/` only.

   **CAPTURE THE PAGE TWICE -- BEFORE AND AFTER IT SETTLES -- AND COMMIT BOTH.**
   That is not extra diligence, it is the specific defect that precedent
   exists to make reproducible: its `manage_pages_following` pair renders 10
   rows unsettled and 20 settled, and a reader that takes the first render as
   the answer *"reports 'he does not follow X' about eight companies he does
   follow, and reports it with no error."* A search page lazy-loads and
   re-ranks, so it is the same hazard on a surface where the rows are people.
   The pair must NOT be normalised into one fixture.
5. **Then bank the census rows.** They are deliberately NOT banked by this
   wave: `N 79`-`N 94` are served by code that has never met the surface, and
   banking them on that basis would be the over-claim. The tool-surface pin was
   cleared by saying so in the commit message, which is one of the reasons that
   guard names as correct.

---

## 7. FILED, NOT FIXED: THE SAME LEAK EXISTS IN A SIBLING, AND IT IS MEASURED

`linkedin_server/anchors.py` carries the identical `int((raw or {}).get(...))`
shape at five sites. Driven the same way as section 2.1:

    search_results.read_results  (REPAIRED)   returned    clean
    anchors.read_anchors                      ValueError  LEAKS
        "invalid literal for int() with base 10: '<the planted name>'"
    collections_page.read_collections         returned    clean

**`anchors.read_anchors` leaks. `collections_page.read_collections` does not.**

**CORRECTED BY:** `_audit/2026-09-20-the-coercion-leak.md` -- the second half of the sentence above is FALSE: `collections_page.read_collections` leaks on the same path as `anchors.py`, and the survey could not have seen it because that reader reads `raw.get("matches")` and `matches` is not a key in the payload the survey plants, so the list came back empty, the comprehension iterated nothing, and the coercion never ran.

**The reader was never driven, and "not driven" printed as
"clean".** Both siblings are repaired as of that document; the survey in
`scripts/_check_the_shaper_leak_guard_can_fail.py` has been rewritten to drive
every page reader in the package through a page that answers EVERY key, because
a hand-written payload can only exercise the keys its author thought of. The
`anchors` half of the sentence, and every figure in this section about it,
stands.

**THE SURVEY IS PART OF THE TRACKED SCRIPT**, at the end of
`scripts/_check_the_shaper_leak_guard_can_fail.py`, so this filing is
re-runnable from a clone rather than a number somebody wrote down. It PRINTS
and does not fail the script, because those modules are another surface's; a
future wave that repairs them turns it green on its own, and it says so.

It is **not fixed here** and that is a scope decision rather than an oversight:
`anchors.py` is an already-admitted surface with consumers in `company_page.py`
and `server.py`, so repairing it widens this commit's blast radius well past
the surface this wave was sent to close, on the day the lead pushed red master
trusting an impact-scoped gate. The repair is the three helpers in
`search_results.py`, copied. **The reproduction above is the whole brief.**

---

## 8. EVIDENCE, AND EVERY LINE OF IT IS REACHABLE FROM A CLONE

No figure in this document rests on anything in gitignored `_audit/_scratch/`.

| claim | re-derive with |
|---|---|
| 3 leaking paths, then 0 | `scripts/_check_the_shaper_leak_guard_can_fail.py` |
| the guard fires on a real defect | same script, both columns |
| blast radius 5 / 7 / 8 / 18 / 18 | `scripts/_probe_search_admission_blast_radius.py` |
| what the admission does and does not open | `readonly.is_read_url` on the urls in section 4.3 |
| the shipped pattern is the measured candidate | `test_the_narrow_candidate_on_record_is_the_one_that_shipped` |
| the shaper emits integers only | `tests/test_the_search_shaper_emits_no_name.py` |
| the TOOL publishes no name, with a hostile page AND a hostile landed url | `test_the_tool_publishes_no_plant_even_when_the_page_and_the_url_carry_one` |
| the detector hunts 9 spellings, not 2 | `PLANTS` in that file, built from `leakwalk.url_spellings` |
| `connections_list.html` is invented | its own header; `SYNTHETIC_SLUGS` in `tests/test_no_committed_identity.py` |
| the sibling leak (`anchors` LEAKS, `collections_page` clean) | the SIBLING SURVEY section of `scripts/_check_the_shaper_leak_guard_can_fail.py`, same run |
| 21 rows, 20 reads, 16 of them people | `awk -F'\t' '$1=="SEARCH-RESULTS-SURFACE"{print $2}' _audit/_census/blocker-assignments.tsv \| sort -u` |

**THE ROW FIGURES WERE RE-DERIVED, NOT QUOTED.** The tracked census returns
exactly `M C70, N 161, N 179, N 194, N 4, N 79 .. N 94` -- 21 rows; `N 4` is
the one write, leaving 20 reads; `N 79`-`N 94` is 16 of them and is the people
vertical. That matches the pre-admission audit, which is worth saying because
its pattern-count figure did NOT match (32 against 41) and one agreeing number
is not evidence for the next.
