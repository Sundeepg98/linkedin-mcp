claude-opus-5-5[1m]

# Lane S -- people-search readers (2026-09-24)

Worktree branch `worktree-agent-a8a566ecd397e5d82`, based on `master` 9c219c8.
Written as the lane goes; a later section corrects an earlier one only where it
says so. Offline throughout: no LinkedIn, no Chrome, no port 9224, no
`_state/chrome-profile`. Raw captures under the main checkout's `_state/` were
read for parameter NAMES and value SHAPES only, and nothing from them was
copied into a tracked file.

## 0. Status

BUILT. All seven rows moved GAP -> COVERED-UNFIRED, none NEEDS-CAPTURE, none
blocked. Nothing re-pinned; the pin moves are listed in section 8. Gates in
section 9, including two real failures the lane's own impact gate found and
the lane fixed.

AT INTEGRATION (section Integration 2026-09-24): the WHO rule kept four of
the seven COVERED-UNFIRED (`N 84`, `N 85`, `N 87`, `N 94`, the filters) and
left three GAP (`N 79`, `N 172`, `N 194`, whose payload is WHO); every pin was
measured afresh on the tree merged with `master` `d65759f` and re-pinned.

## 1. The set, derived from the table

Derived from `_audit/_census/read-addresses.tsv` at 9c219c8: class ADMITTED and
gate in `check_read_addresses.BLOCKED_ON_NOTHING` (READER, PRESS-PERMITTED).
Eight lines answer; seven are the people search and one is not:

    row     gate    address in the table
    N 79    READER  /search/results/people/?keywords=placeholder
    N 84    READER  /search/results/people/
    N 85    READER  /search/results/people/
    N 87    READER  /search/results/people/
    N 94    READER  /search/results/people/?geoUrn=<a two-value list>
    N 172   READER  /search/results/people/?connectionOf=placeholder-member
    N 194   READER  /search/results/people/?keywords=%23hiring
    M M49   READER  /messaging/thread/<id>/      (not people search; not this lane)

The seven agree with the brief. No difference to report.

## 2. What the record says about the spellings (measured offline)

A throwaway stdlib parser (declared disposable in section 11) read every
people-search href in the 25 raw captures under the main checkout's gitignored
`_state/` and printed parameter NAMES and a SHAPE per value -- never a value,
an href or a name. `origin` values are LinkedIn enums and were printed only
when they matched `[A-Z_]{3,40}`.

    capture                      hrefs  what LinkedIn wrote
    company root                   1    currentCompany = JSON list, one 8-digit id,
                                        percent-encoded; origin COMPANY_PAGE_CANNED_SEARCH
    a job collection               1    currentCompany = bare 5 digits; schoolFilter bare;
                                        origin JOB_PAGE_CANNED_SEARCH
    profile views (two captures)  16    keywords text; currentCompany = bare 6/8/9 digits;
                                        geoUrn = bare 8 digits (beside industry bare);
                                        origin WHO_VIEWED_ME
    search appearances             4    keywords text; currentCompany bare; industry bare
    premium hub, role-play         2    activelyHiring = JSON string; activelyHiringForJobTitles
                                        = JSON list
    badges                         1    keywords only, no origin

And from the tracked fixtures: `pastCompany` = bare digits in the committed
job-detail fixture's canned search (origin JOB_PAGE_CANNED_SEARCH).

What that settles, and what it does not:

* `keywords` is LinkedIn-authored, spaces written `+`, and a keywords-only
  href with NO `origin` is LinkedIn-authored too -- so `origin` is optional
  and this lane sends none.
* LinkedIn's faceted grammar on this surface is JSON: a list per facet
  (`currentCompany` on the company root, `activelyHiringForJobTitles`) or a
  JSON string (`activelyHiring`). Two facets, three captures.
* `pastCompany` and `geoUrn` are on record only BARE and single-valued. A
  JSON list for them is DERIVED from the sibling facet, not recorded.
* A list of MORE THAN ONE value is on record for no facet at all. The
  two-value `geoUrn` list is the same JSON grammar with two members --
  DERIVED.
* `connectionOf` is on record nowhere LinkedIn wrote it; the key is NAMED by
  `tests/test_the_search_shaper_emits_no_name.py` only. Its value spelling is
  DERIVED from the same grammar.
* No capture of a people-search RESULTS page exists; the page half of every
  row rests on the shipped readers' 2026-09-21 live firings.

## 3. Design

**Extend, do not add.** `linkedin_people_search_shape` gains five optional
arguments; with none it opens exactly the address it opened before, byte for
byte, so the no-argument firing the Locations row banked on is untouched
(asserted by `test_no_argument_composes_exactly_the_address_the_tool_always_opened`
and `test_the_no_argument_call_is_the_call_it_always_was`).

    argument              LinkedIn key    value accepted                        spelling sent
    keywords              keywords        free text, 1..200 characters          urlencoded, + for space
    current_company_ids   currentCompany  1..5 organisation ids, comma-sep      JSON list
    past_company_ids      pastCompany     1..5 organisation ids, comma-sep      JSON list
    location_ids          geoUrn          1..5 geo ids, comma-sep               JSON list
    connections_of        connectionOf    one member token (ACoAA...)           JSON list

* **ONE PLACE COMPOSES.** A new pure module, `linkedin_server/people_search.py`:
  no page parameter anywhere, no browser or dom import, no navigation, no
  coroutine. It takes the tool's arguments and nothing else, validates each,
  and returns a verdict -- `built` with the address, or a refusal naming the
  argument and describing the SHAPE of what it saw (`jobfilter.describe_shape`),
  never the value. Organisation ids go through the shipped
  `company_page.company_identifier` (the ten ASCII digits, bounded at 20); geo
  ids through the same rule restated; a member id must carry the member-token
  shape the identity guard already knows (`ACoAA` plus 10..59 of
  `[A-Za-z0-9_-]`), so a SLUG -- a name -- is refused by shape. Empty members,
  duplicates and more than the per-argument budget are refused, never
  repaired.
* **THE BOUNDARY ANSWERS, BEFORE ANY SESSION OPENS.** `boundary_verdict` asks
  the door -- `readonly.is_read_url`, the non-raising form `press.py` already
  uses as a pre-check; nothing here can admit what it refuses. A keyword that
  trips a forbidden substring (8 of 11 ordinary keywords per the 2026-09-19
  preconditions audit B.4) comes back structured: the kind `BROWSER.goto`
  would raise (`write_attempt_blocked`), the boundary's OWN forbidden
  substrings the address carries, read off its tuple in its order (so only
  the package's constants can appear, and the first is the one the gate
  names), which argument carried them, and a sentence written for a person
  who was searching -- not "not a read surface". Zero pages loaded, no
  session opened, the denylist not narrowed. **CHANGED IN THE LANE, ON ITS
  OWN GATE'S FINDING:** the first version called `readonly.assert_read_url` and read
  the gate's refusal sentence; `tests/test_api_call_sites.py` pins that
  function's callers to the two navigation paths, the lane's impact gate
  convicted the third caller, and the explanation now reads the tuple the
  way `scripts/_probe_landed_address_sweep._why_refused` does.
* **NOTHING IS ECHOED.** No keyword, id or member token comes back. The
  payload says WHAT was applied as counts (`query_applied`) and, per
  argument, what LinkedIn did with it in the address it settled on
  (`query_kept`): `verbatim` / `same_values` / `different_values` / `absent`
  / `unreadable` -- a closed alphabet computed by `landing_verdict` from the
  landing and the composed address; the landing itself is never published.
  `landed_on_people_search` says whether the settled address is still the
  people vertical, by closed-segment equality.
* **THE PAGE HALF IS THE SHIPPED ONE.** `search_results.read_results` and
  `read_filters_when_settled`, unchanged. Counts only. Condition 1 of
  `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS` (a name-free shaper) is not
  relaxed by D1: a keyword can now be PASSED; nothing about the people it
  finds can leave. Condition 5 (nothing fired from this surface) is
  untouched: no press, no confirm token.

## 4. What was built

    file                                   what
    linkedin_server/people_search.py       NEW. compose, boundary_verdict, refusal_envelope,
                                           landing_verdict; pure
    linkedin_server/server.py              linkedin_people_search_shape: five optional
                                           arguments, the composition, the boundary check
                                           before the session, query_applied / query_kept /
                                           landed_on_people_search; the docstring's
                                           no-parameter paragraph and the module docstring's
                                           sentence amended in place
    linkedin_server/search_results.py      comment only: PEOPLE_SEARCH_URL's "Nothing today
                                           passes one" amended
    linkedin_server/readonly.py            comment only, AST unchanged: the people entry's
                                           "sends no query at all" amended
    tests/test_people_search_readers.py    NEW. 107 tests, section 6
    tests/test_server_surface.py           comment only: "NO PARAMETERS AT ALL" amended
    tests/test_a_correction_is_findable_   one NOT_A_CORRECTION entry: network.md cites this
      from_the_claim.py                    record beside the word `mistake`, which is inside
                                           row 79's kept prior cell (section 9)
    _audit/_census/network.md              seven cells, section 7
    _audit/_census/read-addresses.tsv      the seven lines removed: the rows left bucket 3

The `server.py` hunk is the tool, one import line, and in the module
docstring one line edited and four added. No tool was added, so the tool
count stays 51.

## 5. Per row

    row    verdict                 what it rests on
    N 79   BUILT, COVERED-UNFIRED  keywords, LinkedIn-authored spelling (MEASURED)
    N 194  BUILT, COVERED-UNFIRED  the same reader; composes the exact address the table held
    N 84   BUILT, COVERED-UNFIRED  currentCompany JSON list, LinkedIn-authored (MEASURED)
    N 87   BUILT, COVERED-UNFIRED  pastCompany: bare on record, list DERIVED
    N 94   BUILT, COVERED-UNFIRED  geoUrn two-value list DERIVED; composes the table's own address
    N 85   BUILT, COVERED-UNFIRED  connectionOf never LinkedIn-authored; list DERIVED
    N 172  BUILT, COVERED-UNFIRED  the same reader as N 85

AT INTEGRATION the WHO rule re-decided three of these by their row text:
`N 79`, `N 194` and `N 172` are GAP, the reader built and unchanged. See
Integration 2026-09-24, I.2.

**WHY NONE IS NEEDS-CAPTURE.** No new page reader was built. The page half of
every row is the shipped shaper, which fired live on this page on 2026-09-21,
so no capture-derived fixture was needed and none was made. What is not on
record for four of the rows is a URL SPELLING, not a page structure -- and it
is settled on the first fire by `query_kept`, built for exactly that, rather
than by a capture. **IF THE BRIEF'S "CONCRETE" RULE IS READ TO COVER
SPELLINGS**, the rows it touches are N 85 and N 172 first (the key itself was
never LinkedIn-authored), then N 94 (no multi-value list on record for any
facet) and N 87 (list form derived from a sibling facet). That is the
orchestrator's call; the build does not change with it, only the state.

**THE SCOPE QUESTION EVERY ROW CARRIES, AND IT IS STATED IN EACH CELL.** The
payload is the search's SHAPE -- how many person results the first page draws,
which known filters it offers -- never who. For the filter rows and the
several-locations row that is the capability (the filter is applied). For
N 79 and N 194 ("search for a person", "find hiring managers") a count-only
answer may be judged not to be the capability, as `N 162` and `N 180` were
judged COVERED-CANNOT-DELIVER for the same shaper limit after they fired. The
cells leave that judgement to the banking fire rather than pre-empting it in
either direction. For N 172 the count is the row's own question -- are that
member's connections shown to this account -- in one direction only: a
nonzero says yes; a zero says nothing.

## 6. What the tests prove (`tests/test_people_search_readers.py`)

The brief asked for two properties; each has a test and a control shown
failing on the same run.

* **EVERY COMPOSED ADDRESS IS ADMITTED.** A corpus of every argument alone,
  every pair and all five together, each facet at its value ceiling (26
  addresses), driven through `readonly.is_read_url`, `boundary_verdict` and
  the census instrument's own reader `check_read_addresses.refusal_of`. Control:
  `test_THIS_CONTROL_CAN_FAIL_the_admission_check_can_say_refused` -- the same
  three say REFUSED for `keywords=settings`.
* **NOTHING PAGE-DERIVED CAN ENTER AN ADDRESS.** Three layers. (a) The
  composer's AST: no `page` parameter, no coroutine, no browser, dom, playwright
  or server import, no `.goto` / `.evaluate` / `.content` / `.locator`.
  (b) The tool's AST: exactly one `people_search.compose` call, keyword-only,
  each argument its own parameter of the same name, and exactly one
  `BROWSER.goto`, whose target is `composed['url']`. (c) Driven: a recording
  browser whose page answers every read with a planted name and whose landing
  appends a planted name, a planted slug and a STRANGER's member token under
  the tool's own keys -- the tool navigates exactly once, to the composed
  address. Control: `test_THIS_CONTROL_CAN_FAIL_the_recorder_convicts_a_second_navigation`.
  The repository's own taint guard, `tests/test_navigation_is_never_derived.py`,
  runs over the new code as well (section 9).
  **SHOWN FAILING ON THE REAL TOOL, NOT ONLY ON A FABRICATED LOG.** A
  disposable mutation run lifted the tool's body out of `server.py`, planted
  one line -- a second `BROWSER.goto(page, landed)`, to the address the
  browser chose -- and drove the mutant with the committed recording browser:
  the unmutated tool navigated once and passed, the mutant navigated twice and
  the committed assertion raised. The same planted source put through the
  taint guard's own `violations()` reads 1 violation, at the planted line;
  the unmutated `server.py` reads 0 (and 0 output-sink violations). Two
  instruments sharing no mechanism convict the same derived navigation.
* **THE BOUNDARY'S OWN ANSWER.** All eight B.4 keywords refuse with their
  substrings, the three clean ones are admitted, and the eleven split 8 / 3
  exactly as B.4 measured. The explanation is held against the census
  instrument's reading of the gate's own sentence
  (`check_read_addresses.refusal_of`): for every B.4 keyword, and for a
  keyword carrying two substrings, the first substring listed is the one the
  gate names. A refusal the tuple cannot explain lists nothing; a word planted
  in the DOOR's tuple is refused by the door and named exactly; the composer
  never calls `assert_read_url`. A boundary refusal and an argument refusal
  each open NO session.
* **NOTHING COMES BACK.** The driven payload carries no plant and none of the
  five argument values; `query_kept` reads the planted foreign values as
  `different_values`, never as kept. Seventeen refused arguments (slugs, the
  Arabic-Indic digits `str.isdigit()` accepts, over-long runs, empty members,
  duplicates, over budget, a short token, a control character, an over-long
  keyword) each name their argument and never their value. A keyword carrying
  a no-break space or a zero-width joiner -- ordinary in several Indian
  scripts -- is NOT refused: control characters are refused by Unicode
  category `Cc`, not by `str.isprintable()`, which is False for both (found in
  self-review after the first commit and fixed in a later one).
* **THE LANDING VERDICT** reads verbatim, same_values (a re-spaced keyword, a
  bare id for a list, a reordered list), different_values, absent and
  unreadable, and False for another vertical, a wall, another host and a
  traversal; its output is the closed alphabet whatever the landing holds.
* **THE CENSUS CHAIN.** The seven rows read COVERED-UNFIRED and each cell names
  `people_search` and `linkedin_people_search_shape`; the four functions, the
  four facet keys and the tool's five parameters are asserted as a chain, with
  a control that convicts a renamed function.

## 7. The census

Each of the seven `_audit/_census/network.md` cells is rewritten
GAP -> COVERED-UNFIRED with a dated lead naming the tool, the module, the
ruling, the evidence class of its spelling, the scope, the live queue and the
guarding test, and the whole prior cell is kept after `PRIOR CELL, KEPT:` (the
`connectionOf` group-member row had none, and says so). No cell cites a hold
with the `HELD BY` marker: D1 and OTHER-MEMBER-IDS permit; they do not hold. So
every row enters bucket 1 held by no ruling.

The seven `read-addresses.tsv` lines are removed: the rows left bucket 3, and
`check_read_addresses` refuses a line for a row that has left it. Measured
after the edit: GREEN, 59 of 59 bucket-3 rows.

## 8. Expected pin moves -- NOT re-pinned, per the brief

AT INTEGRATION these were measured afresh on the merged tree and re-pinned,
as the integration order asked; the values are in Integration 2026-09-24, I.3.

    scripts/census_completion.py PINNED (census_completion --check, red on exactly these)
      adjudicated              434 -> 441   (+7)
      delivered_broad          100 -> 107   (+7)
      gap                      270 -> 263   (-7)
      unfired                   25 ->  32   (+7)
      gap_read                  66 ->  59   (-7)
      b3_admitted               40 ->  33   (-7)
      b3_blocked_on_nothing      8 ->   1   (-7; M M49 alone)
      b1_no_ruling              15 ->  22   (+7)
      every other pin unchanged: stated_rows 704, delivered_strict 75,
      b3_refused 16, b1_standing 10, b1_released 6, b2_d3_rows 3, jobs_* all

    scripts/census_completion.py PINNED_B1_ROWS
      NO RULING gains N 79, N 84, N 85, N 87, N 94, N 172, N 194 (7 ENTERED)

    tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py
      "linkedin_people_search_shape": () ->
          ("connections_of", "current_company_ids", "keywords",
           "location_ids", "past_company_ids")
      PINNED_PARAMETER_COUNT 69 -> 74; PINNED_TOOL_COUNT stays 51
      (the census rows this surface change serves move in the same branch)

    scripts/triage_read_gap_rows.py (its CONTROL 4 re-derives the read-GAP set)
      TRIAGE loses N 79, N 84, N 85, N 87, N 94, N 172, N 194
      DECIDED_SINCE_TRIAGE loses N 79, N 94, N 172, N 194
      (the merge of lane L1 removed P G6 from TRIAGE the same way)

    UNCHANGED, measured: tests/census_row_pin.json (population 704 -- a state
    move is not a population move), check_read_addresses GREEN, ruling_holds
    GREEN, the tool count 51.

    Downstream readings that move and are not pins: reader_closable_blockers
    SEARCH-RESULTS-SURFACE GAP 20 -> 14 (reader-reachable 19 -> 13), and
    GROUPS-SURFACE loses N 172; count_census_states GAP 270 -> 263,
    COVERED-UNFIRED +7; blocker-map.tsv regenerated (a generated file).

## 9. Gates

Every lane commit went through the pre-commit identity gate (0 hits each
time). The lane's commits are branch-only until the merge.

**THE CENSUS INSTRUMENTS**, on the census commit and again on the final tree:

    census_completion --check      exit 1 on EXACTLY the 8 figures and the 7
                                   bucket-1 rows of section 8 -- expected, not
                                   re-pinned
    check_read_addresses           GREEN, 59 of 59 bucket-3 rows
    ruling_holds                   GREEN
    pin_census_rows --check        no drift (704)
    triage_read_gap_rows           exit 1 on CONTROL 4 only, naming exactly the
                                   seven rows -- expected, section 8
    build_audit_index / build_rulings_index / build_blocker_map --check
                                   exit 0 after every regeneration (fixed point)

**THE FIRST IMPACT GATE** (`scripts/impact_gate.py --against 9c219c8`), run in
the background on the census commit. The impact set was 184 of 235 test files
(78%), so it widened to the FULL SUITE: 15 failed, 9050 passed, 8 skipped,
1 xfailed, in 1975 s. Every failure classified:

    expected -- the pins section 8 lists, not re-pinned (4)
      test_ruling_holds::test_bucket_one_is_derived_and_sits_on_its_pins
      test_the_tool_surface_is_pinned_so_a_row_must_move::...[linkedin_people_search_shape]
      test_triage_read_gap_rows::test_green_on_the_real_tree
      test_triage_read_gap_rows::test_the_control_4_population_is_not_empty_and_equals_the_key_set
    REAL, and fixed in the lane (2)
      test_api_call_sites::test_assert_read_url_is_called_only_on_the_navigation_paths
        -- boundary_verdict was a THIRD caller of assert_read_url; it now
           decides with is_read_url and explains from the tuple (section 3)
      test_a_correction_is_findable_from_the_claim::test_every_candidate_pair_is_declared_or_triaged
        -- network.md cites this record within two lines of `mistake`, a word
           inside row 79's KEPT prior cell; triaged NOT_A_CORRECTION with the
           reason, after reading the line
    environmental -- green on the clean committed tree, 22 of 22 (9)
      test_stale_process_is_announced (7), test_server_surface::
      test_both_login_names_are_registered_and_the_old_one_forwards,
      test_publish_post_names_its_audience::test_it_stops_refusing_the_moment_the_audience_can_be_read
        -- the self-review commit was edited INTO the working tree while the
           suite ran (the stale-process tests compare loaded modules with the
           disk), on a box carrying 33 python processes from several lanes

**THE COLD VERIFICATION** -- one pass by a child, on the tree before the two
fixes above, 14 claims, all VERIFIED, zero refuted: the commit messages carry
no attribution; exactly seven network.md lines changed and each keeps its prior
cell verbatim; exactly seven address lines left and `check_read_addresses` is
green; the census pins move by exactly section 8; its own fuzzers built 6480
argument combinations (4320 composed, every one admitted, no foreign key) and
157 landings (never raises, closed alphabet), and its own fake browser drove
the real tool (one navigation, to the composed address, no argument echoed; a
refused keyword and a refused slug opened no session); 1387 of 1388 selected
tests passed, the one failure the tool-surface pin; and a cold read of this
record found no claim the files contradict. Its only defect is the one
section 10 already names (a failed navigation quotes the composed address).
It also found the `unreadable` landing verdict hard to reach: it is reachable,
through an unbalanced IPv6 bracket, which `urlsplit` refuses and the lane's
test drives.

**AFTER THE FIXES**: `tests/test_people_search_readers.py` (107),
`tests/test_api_call_sites.py` and `tests/test_a_correction_is_findable_from_the_claim.py`:
131 passed.

**THE FINAL IMPACT GATE** (`--against 9c219c8`), on the fix commit with a
clean tree and nothing edited during the run: 189 of 235 files selected (80%),
widened to the FULL SUITE -- 5 failed, 9064 passed, 8 skipped, 1 xfailed, in
2390 s, on a box running three other lanes' gates at the same time.

    expected -- section 8's pins, not re-pinned (4)
      test_ruling_holds::test_bucket_one_is_derived_and_sits_on_its_pins
      test_the_tool_surface_is_pinned_so_a_row_must_move::...[linkedin_people_search_shape]
      test_triage_read_gap_rows::test_green_on_the_real_tree
      test_triage_read_gap_rows::test_the_control_4_population_is_not_empty_and_equals_the_key_set
    environmental (1)
      test_click_is_not_its_own_evidence::test_the_refusal_says_when_a_matcher_would_have_separated_them
        -- a writes-gate file this lane does not touch (selected through
           readonly.py's comment-only edit); run alone on the same commit it
           passes, 30 passed and its known strict xfail, in 374 s -- a slow
           file, red once under a saturated box and green alone

Both real failures of the first run are gone, and nothing new of the lane's
own is red.

**NOT RUN**: no live fire (the lane is offline by its brief); no CI (nothing is
pushed); the full suite was not re-run after this record's own last edit,
which touches only this file and the generated views, each held at a fixed
point by its own `--check`.

## 10. Found and not fixed

* **A FAILED NAVIGATION QUOTES THE COMPOSED ADDRESS.** `BROWSER.goto` wraps a
  Playwright failure as `navigation to {url} failed: ...`, and `_error`
  publishes it. On this tool that address carries the caller's own keyword,
  ids and member token. They are the caller's values, not the page's, and the
  same is true of every tool whose address carries an argument
  (`linkedin_search_jobs` quotes its keywords the same way) -- but it is the
  one path by which a `connections_of` token comes back. `browser.py` is
  shared and outside this lane; recorded, not changed.
* **KEPT IS NOT FILTERED.** `query_kept` says what LinkedIn left in the
  address it settled on. A name-free proof that a facet FILTERED the results
  would need result identities this surface may not publish; the strongest
  name-free reading is kept plus results drawn, and the live queue banks on
  that and says so.
* **NO TOOL RESOLVES A GEO ID.** `location_ids` takes LinkedIn's numeric geo
  ids and nothing in this server turns a place into one; organisation ids
  come from `linkedin_job_detail` and `linkedin_followed_companies`, member
  tokens from `linkedin_connections`. A place resolver would be a keyword
  search of its own, and none was built.

## 11. Instruments

Registered as `_audit/INSTRUMENTS.md` section 66: the admission corpus, the
recording-browser derivation check, and `people_search.landing_verdict` --
each with the control that shows it failing.

Declared disposable (scratchpad, not tracked):

* `facet_shapes.py` -- the capture parser of section 2. Printed names and
  shapes only; its finding is recorded above and nothing ships on it except
  the spelling decision it informed.
* `census_edit.py` -- rewrote the seven census cells, refusing on any
  surprise; its result is the diff.
* `ascii_escape.py` -- rewrote two non-ASCII string literals in the new test
  file as escapes.
* `mutation_derived_nav.py` -- the mutation run of section 6: planted a
  derived second navigation into a copy of the tool body and drove it. Its
  result is recorded in section 6; the committed controls stand without it.
* `bmap_summary.py` -- summarised the regenerated blocker map's diff by
  column, to confirm no blocker's first reason candidate moved.
* `lane_s_*` drafts -- text of this lane's own edits staged outside the tree
  while the cold verifier read it; the edits themselves are in the commits.
* The cold verifier's own scripts (`check_c6.py` .. `check_c13.py`) and its
  report `cold_verify_lane_s.txt` -- its results are summarised in section 9.

## Integration 2026-09-24

Ordered by the orchestrator at 03:20. Sampled on disk before obeying: HEAD
`fe07ba6`, tree clean, `master` at `d65759f` -- what the order said. The lane's
commits before the merge end at `fe07ba6`, which is on the lane branch only:
until this merge lands it is nowhere on `master`, and no clone can resolve it.
The merge commit is the one that carries this section (a commit cannot name
its own hash). Where this section and sections 0 to 11 disagree, this section
is the later reading.

### I.1 The merge of `master` `d65759f`

`d65759f` carries rulings batch 3 (the search verticals, the unregistered
refusals, member rosters as bounded reads, passive costs) and lane R's merge
(245 exclusions back to GAP with their blockers named). Six paths conflicted:
three by content, three generated.

    path                              resolution
    _audit/_census/network.md         ONE hunk, rows 170-172: 170 and 171 from master
                                      (lane R's return; 171 filed NOT-AN-ACT), 172 from
                                      the lane. The lane's other six rows merged clean --
                                      master touched none of them.
    _audit/_census/read-addresses.tsv RE-DERIVED: master's table (lane R's re-derivation)
                                      plus this lane's moves on the merged census. The
                                      four FILTER rows' lines leave; the three WHO rows
                                      keep theirs, re-gated READER -> RULING; master had
                                      already dropped N 171's.
    _audit/INDEX.md, _audit/RULINGS.md,
    _audit/_census/blocker-map.tsv    generated: master's side taken to clear the
                                      conflict, every resolved path staged, then
                                      regenerated to a fixed point (two sweeps, --check)

No textual conflict, integrated by hand: `scripts/triage_read_gap_rows.py`
keeps master's RETURNED class and CONTROL 9; TRIAGE loses `N 84`, `N 85`,
`N 87`, `N 94`; DECIDED_SINCE_TRIAGE loses `N 94` and re-words `N 79`, `N 172`,
`N 194` -- the triage-day decision was made, the reader was built, and a
different question now holds each. All nine controls OK. `_audit/INSTRUMENTS.md`
merged in number order with no conflict: 64 (with lane R's 64.3), 65, 66.

### I.2 The WHO rule, row by row

The orchestrator's census call, 03:20: a row whose capability's payload is
WHO -- a person, or a set of people -- served by a reader that publishes only
counts, is NOT delivered, on the precedent of `N 162` and `N 180`; a FILTER, or
a count the reader's output proves, stays COVERED-UNFIRED. Each row decided on
its own words:

    row    row text                                              payload  state
    N 79   Search for a person by keyword or natural-language    WHO      GAP
           query
    N 194  Find hiring managers through the #Hiring hashtag      WHO      GAP
           in search
    N 172  View a fellow group member's connections only after   WHO      GAP
           connecting with them
    N 84   Filter by Current company                             FILTER   COVERED-UNFIRED
    N 85   Filter by Connections of                              FILTER   COVERED-UNFIRED
    N 87   Filter by Past company                                FILTER   COVERED-UNFIRED
    N 94   Add more than one location to a single search         FILTER   COVERED-UNFIRED

* `N 79` and `N 194`, as the order expected: a person, and hiring managers.
* `N 172` on its words: to VIEW a member's connections is to see a set of
  people. The count the reader publishes answers a narrower question -- are
  that member's connections shown to this account at all -- and in one
  direction only (a nonzero says yes, a zero says nothing). Section 5 argued the
  count was this row's question; that reading is withdrawn here.
* `N 85` is a filter whose VALUE is a person. The capability is the filter, the
  reader applies it, and what it publishes is the filtered search's shape.
* `N 94`'s capability is the shape of a query, several locations in one search.

Each GAP cell now opens on the rule and carries, in its own words: BLOCKER,
NAMED: the name-free shaper doctrine (`_audit/2026-09-05-lead-rulings-round-two.md`:
this server does not publish names), pending the operator's question on
returning names at runtime; REOPENER: the operator rules that people reads may
return who at runtime. The build stays in the cell, below the rule, as that
day's record. No `HELD BY` marker is written: no hold in `scripts/ruling_holds.py`
binds these rows, and a marker would claim one. In the address table the three
are gated RULING -- a decision the operator has not made -- with the same
blocker and reopener in the note. **Nothing is built around the doctrine in
either direction: the reader is unchanged.** Each FILTER cell carries one
added sentence saying why the rule does not reach it.

### I.3 Pins, re-derived on the merged tree

Measured on the merged tree, not applied as deltas from `9c219c8`; section 8's
forecast was taken against seven rows moving and is replaced by this table.

    scripts/census_completion.py PINNED        master d65759f   merged
      adjudicated                                    190          194
      delivered_broad                                101          105
      gap                                            514          510
      unfired                                         26           30
      gap_read                                        98           94
      b3_admitted                                     44           40
      b3_blocked_on_nothing                            9            2   (M M49, P K1)
      b1_no_ruling                                    16           20
      every other pin unchanged: stated_rows 704, capabilities 762,
      capabilities_achievable 648, out_of_scope 70, achievable 634,
      delivered_strict 75, cannot_deliver 19, gap_write 324, gap_unknown 92,
      b3_refused 38, b1_standing 10, b1_released 6, b2_d3_rows 0, jobs_* all

    scripts/census_completion.py PINNED_B1_ROWS
      NO RULING gains N 84, N 85, N 87, N 94 (20 rows)

    tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py
      linkedin_people_search_shape: () -> (connections_of, current_company_ids,
      keywords, location_ids, past_company_ids); PINNED_PARAMETER_COUNT
      69 -> 74 on the merged surface; PINNED_TOOL_COUNT 51 unchanged

    scripts/triage_read_gap_rows.py
      TRIAGE 75 verdicts (four keys fewer); DECIDED_SINCE_TRIAGE 13

`census_completion --check` reads "every headline figure matches its pin" on
the merged tree. `tests/test_people_search_readers.py` pins the per-row states
the rule gave (four COVERED-UNFIRED, three GAP with the blocker and the reopener
named), and that the three WHO rows sit in the address table gated RULING.

### I.4 Gates on the merged tree

The merge commit, then two small commits after it (a hash disclosure; two
guard repairs). The tree was clean during every run.

    census_completion --check              every headline figure matches its pin
    check_read_addresses                   GREEN, 94 of 94 bucket-3 rows
    check_write_classes                    GREEN, 325 lines
    ruling_holds                           GREEN
    pin_census_rows --check                no drift (704)
    triage_read_gap_rows                   all nine controls OK
    check_contingent_writeoffs_carry_a_reopener   exit 0
    check_cited_shas_resolve               exit 0 -- once the pre-merge head
                                           `fe07ba6` was disclosed branch-only;
                                           it had flagged that hash
    build_audit_index / build_rulings_index / build_blocker_map --check
                                           exit 0, at a fixed point
    (all re-run on the final tree, the same results)

**THE IMPACT GATE WIDENED, SO IT WAS NOT RUN.** `scripts/impact_gate.py
--against d65759f --plan-only`: 17 changed paths select 193 of 235 test files
(82%), and the gate widens to the full suite. By the order -- six lanes share
the box -- that suite was NOT run locally; CI runs it after the merge.

**RUN INSTEAD, `-n 4`**: the 17 corpus-wide guards the impact gate itself
derives (identity, credential, correction, asserted names, the navigation
derivation, page text, the census row total and the rest), the lane's tests,
the two page-string guards, and every test coupled to the census instruments
or to a file the lane changed -- 51 files. **First run: 2 failed, 4011
passed**, and both reds were the lane's own new cell text:

* `test_a_correction_is_findable_from_the_claim` -- network.md now cites the
  doctrine's document on row 79, whose kept prior cell carries the word
  `mistake` (the tool docstring it quotes). Triaged NOT_A_CORRECTION, with the
  reason, after reading the line.
* `test_an_asserted_name_resolves` -- rows 85 and 172 said "under
  `OTHER-MEMBER-IDS-AS-READS`", and "under" is one of that guard's blocker
  slot words, so a ruling id read as a blocker name. Reworded "as ...
  permits"; no blocker is named there.

**After both repairs**: the 23 census-coupled and corpus files plus the lane's
tests, re-run: **1428 passed, 0 failed.** The lane's test file holds 109 tests.

**NOT RUN**: the widened full suite (CI, after the merge); any live fire.

### I.4a Master moved during the integration: lane G at `209a831`

While these gates ran, `master` advanced to `209a831` -- lane G's guard
hardening: error fields carry exception types, the navigation guard sees
values a reader returned, the hash-citation guard case-folds its slot words,
the reason locator reads a conflicted path once, register section 67. As the
order said, it was merged the same way, in a second merge commit on this
branch.

    path                   resolution
    _audit/INSTRUMENTS.md  both sides appended at the end; kept in number
                           order, 66 (this lane) then 67 (lane G)
    _audit/INDEX.md        generated; master's side taken, every path staged,
                           then INDEX.md, RULINGS.md and blocker-map.tsv
                           regenerated in two sweeps, --check at a fixed point

No census file changed on master's side, so no pin moves: the pins of I.3
stand, and the census instruments re-run on the merged tree read the same --
`census_completion --check` matches every pin, `check_read_addresses` GREEN
94 of 94, triage all nine controls OK, `check_write_classes` GREEN,
`pin_census_rows` no drift, `ruling_holds` GREEN. Lane G's hardened guards
were run against this lane's code with the selection that touches it -- the
navigation guard, both page-string guards on the new `tests/plantedpage.py`,
the hash-citation guard, the reason locator's own test, the lane's 109 tests,
the tool-surface pin, the corpus and census guards: **2311 passed, 0 failed.**

### I.5 What the follow-up inherits

* The live queue below is re-cut: the three WHO rows bank on no fire under the
  rule, so the queue is the four filters, and they fit one session.
* D2's verticals and the member-roster admissions arrive after this merge.

## Live queue

Every call is ONE people search and ONE page load. `D1-SEARCH-AS-READS` caps a
live session at FIVE test searches; the four calls below are one session of
four, or three and then `N 85` once the operator names a member. No value
below identifies the operator; the member token and any organisation id are
supplied at fire time and written into no tracked file.

What banks a row, for every line: `ok` True, `landed_on_people_search` True,
`query_kept.<argument>` `verbatim` or `same_values`, `results.person_results`
at least 1, `panel_wait.settled` True and `denominators.values_refused` 0.
`absent` or `different_values` convicts the spelling (the row goes back to GAP
with the finding); `person_results` 0 banks nothing, because hidden, empty and
a dropped facet read alike.

    N 84   linkedin_people_search_shape(current_company_ids="<id>")          1 load, search 1/5; <id> = the numeric Page id linkedin_job_detail resolves as company_id on a posting at any employer that is not his (the J 10 route, fired live 2026-09-20); banks on query_kept.current_company_ids
    N 87   linkedin_people_search_shape(past_company_ids="<id>")             1 load, search 2/5; <id> as for N 84, from a different posting; query_kept.past_company_ids also settles the DERIVED list spelling
    N 94   linkedin_people_search_shape(keywords="engineer", location_ids="103644278,101165590")  1 load, search 3/5; two country-level geo ids (the United States and the United Kingdom as publicly documented -- UNVERIFIED here, from recall; neither his city nor his country); banks on query_kept.location_ids with both ids sent, and settles the DERIVED two-value list
    N 85   linkedin_people_search_shape(connections_of="<token>")            1 load, search 4/5, or 1/5 of a later session; <token> = ONE member he names, e.g. the recipient_id linkedin_connections returns for a 1st-degree connection he picks; banks on query_kept.connections_of and settles the never-LinkedIn-authored key

NOT QUEUED, and why: `N 79`, `N 194` and `N 172`. A fire of the same reader
would prove the reader and bank nothing: under the WHO rule a count does not
deliver those rows. They move when the operator answers the question on
returning names at runtime -- and the reader they would then need is not the
one this lane built.
