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
  DERIVED. **ONE IS ON RECORD SINCE 2026-09-28** (M.3 below): `network`'s
  `["F","S"]`, written raw on link 1 of a first-degree profile's topcard.
* `connectionOf` is on record nowhere LinkedIn wrote it; the key is NAMED by
  `tests/test_the_search_shaper_emits_no_name.py` only. Its value spelling is
  DERIVED from the same grammar. **MEASURED SINCE 2026-09-28** (M.4 below):
  LinkedIn writes it on links 2 and 3 of a first-degree profile's topcard,
  a percent-encoded JSON list holding one member id -- the spelling this lane
  sends.
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

## Follow-up 2026-09-24

The orchestrator's follow-up order (04:28) gave this lane four items after
its merge: D2's search verticals, the member rosters, the WHO rule extended to
WHICH, and the pins. Offline throughout: no browser, no LinkedIn page, no
Chrome profile. One commit per item, each carrying its own census moves, and
this section grows with each commit so the record on disk is never behind the
tree.

### A. Step 0

`HEAD` was `3cee266`, contained in `master` `ff98a7f`; `git merge --ff-only
ff98a7f` fast-forwarded cleanly and the tree was clean. Every measurement
below is taken on that base plus this lane's own commits.

### B. Item 1 -- the search line widened to four closed words

**THE LINE.** `readonly._ALLOWED_URL_PATTERNS`'s people-search entry changed
from `^https://www\.linkedin\.com/search/results/people/?(\?[^#]*)?$` to
`^https://www\.linkedin\.com/search/results/(people|companies|groups|events)/?(\?[^#]*)?$`
-- one entry EDITED, none added, so the pattern count stays 49. It is the S2
spelling `_audit/2026-09-19-search-admission-preconditions.md` measured, a
closed alternation of four literal words and never a `/search/` prefix
(`SEARCH-CONDITION-2-CLOSED`). The groups-root and events-root comments that
listed their search verticals as "not this entry's to inherit" carry a dated
comment-only amendment: admitted now, by the search line, not by them.

**THE BLAST RADIUS, TAKEN BEFORE THE LINE CHANGED** with
`scripts/_probe_search_admission_blast_radius.py` over its 90-address corpus
against the 49 patterns on disk at `ff98a7f`:

    S2   four verticals (this line)          newly admits  3
         companies, groups, events -- each ?keywords=x, nothing else
    S2b  three verticals (not taken)         newly admits  2
    W1   /search/.*$ anchored (counterfactual)  newly admits 13
    W2   /search/ prefix (counterfactual)       newly admits 13
         both including the account-ending traversal

**THE PROBE ITSELF EXITED 1 AT `ff98a7f`, before any edit of mine.** Its
narrow-candidate control required S1 to newly admit something, and a
candidate already on disk newly admits nothing by construction -- so from
the day S1 landed (2026-09-20) the probe convicted the admission it had
measured. The control now asks the question it exists for, of the candidate
D2 took: every address its four words are for is admitted with it installed,
newly or already. Before the line changed that reads 3 newly and 1 already;
after, 0 and 4. All four controls pass after the change, exit 0.

**THE DIGEST.** `_ALLOWED_URL_PATTERNS` `c37e98f84ee443f2 ->
d7b3315318c877d0`, seven of eight digests byte-identical, `<functions>`
unmoved. Attribution: the tree with exactly that one line put back to its
people-only spelling hashes to the prior pin on all eight keys. Recorded in
the ledger in `tests/test_readonly_boundary_invariant.py`.

**`MUST_STAY_REFUSED`, ON `MUST-STAY-REFUSED-ENTRIES-COME-OUT`.** In
`tests/test_search_admission_blast_radius.py` the three vertical entries left
the durable set for `ADMITTED_BY_THE_D2_WIDENING`, under their old names and
asserted the other way; `content`, `schools` and `jobs` moved to
`REFUSED_UNDER_THE_D2_CHOICE`, marked with the choice they assume; the
account-ending and third-party families stayed, and the durable set gained
the account-ending traversal from each of the four words. The count test was
rewritten to pin FOUR over a closed list of twelve vertical words, and a
planted `/search/` prefix is shown turning it and the traversals red.

**THE ORDER'S THREE TESTS**, in `tests/test_d2_search_verticals.py` (101):
every admitted spelling of every word (with and without the slash and a
query) and every address the composer builds over a nine-keyword corpus;
the account-ending traversal and six siblings refused from all four words; 15
planted prefix spellings refused (`companiesx`, `groupsearch`, `events2`, a
changed case, a deep path under a word, a doubled slash), with the control
that a `/search/results/` prefix admits all fifteen. Plus exactly one pattern
admitting each word.

**THE COMPOSER.** `linkedin_server/search_verticals.py::compose(vertical, *,
keywords)` builds the companies, groups or events search from a tool's
arguments only, the way `people_search.compose` builds a people search: the
keyword is validated by `people_search.validated_keywords` -- split out of
`people_search.compose` unchanged, so the rules cannot drift, and lane S's
109 tests stayed green across the split -- sent under `keywords`,
`urlencode`d, no `origin`. It takes no facet (none of these verticals'
facets is on record in any capture) and REQUIRES a keyword (every row it
serves is a search by keyword; the bare vertical page is uncaptured). Pure,
no page, no loop, and a rejected value is described, never quoted.

**CONDITION 1, AND A DEVIATION FROM ITS LETTER THAT THE ORCHESTRATOR SHOULD
SEE.** The search admission's condition 1 reads *"ADMISSION AND A NAME-FREE
SHAPER LAND IN THE SAME COMMIT, OR NEITHER LANDS"*. D2 says of its rows "each
then needs a reader", and this order says readers are built against captures
only -- and a capture needs the admission, because every capture goes through
`BROWSER.goto`, which calls `assert_read_url`. So the address landed without
a reader for the three new words, and what condition 1 protects is held
instead by the absence of any route: nothing in the package imports
`search_verticals` (`tests/test_every_orphan_module_is_ruled.py` holds it
unwired with this as its reason), and the one search tool composes the
people vertical only (pinned in `tests/test_d2_search_verticals.py`). The
shaper itself exists and is the shipped one -- `search_results.read_results`
and `read_filters` return integers whatever page they meet. **The first tool
that opens one of the three words must land with its name-free reader in the
same commit.** If the orchestrator reads condition 1 as binding the ADDRESS
rather than the first read, the rollback is the one line, and every test above
knows how to go back.

**THE OTHER TESTS THE WIDENING MOVED**, each rewritten with the address it
stopped refusing recorded, none deleted: `test_readonly.py` (two BLOCKED
entries inverted into ALLOWED; three `MUST_STAY_UNREADABLE` entries recorded
out), `test_the_search_results_address_is_refused_before_admission.py`
(inverted a second time; the measured candidate is now READ OFF the probe by
name and must equal the shipped line), `test_the_events_boundary_is_root_only.py`,
`test_the_groups_id_segment_is_closed.py` and `test_l1_event_by_id_admission.py`
(the search vertical moved to an ADMITTED-BY-ANOTHER-LINE group asserting no
events or groups line carries it), and `test_analytics_creator_boundary.py`,
`test_premium_four_boundary.py`, `test_search_appearances.py` (a companies
canary replaced by the content vertical, still refused).

**THE CENSUS.** In `_audit/_census/read-addresses.tsv`, `N 104`, `N 161` and
`N 179` went REFUSED -> ADMITTED, gate MEASURE, source
`linkedin_server/search_verticals.py::compose`, each prior note kept; `M C70`
stays REFUSED on its content-vertical address, its groups spelling now an
admitted also-driven line. Each of the four cells carries a dated paragraph;
no STATE moved. `census_completion` pins `b3_admitted 40 -> 43`,
`b3_refused 38 -> 35`, re-pinned in the same commit with the reason. The
triage's three D2 annotations now say the address is on the boundary.

**TWO GUARDS WENT RED ON THE ITEM-1 COMMIT, AND A SECOND COMMIT FIXED THEM**
(3824 passed and 2 failed over the 18 always-run guards and the touched
files). `tests/test_ci_shard.py`: the committed timings priced 157 of
236 live test files, under its two-thirds line, because one test file was
new; that file is priced from a serial run of it alone, under a new
`_amended` provenance key, rather than by a full local run. And the
correction guard: `M C70`'s cell now cites this record two lines from the
cell's own 2026-09-21 correction vocabulary, triaged NOT_A_CORRECTION with
the line read.

### C. Item 2 -- member rosters as bounded reads

**THE FOUR LINES**, at the end of `readonly._ALLOWED_URL_PATTERNS`, one per
roster `MEMBER-ROSTERS-AS-BOUNDED-READS` names:

    ^https://www\.linkedin\.com/groups/[0-9]{1,20}/members/?$                  N 165, N 177
    ^https://www\.linkedin\.com/events/[0-9]{1,20}/attendees/?$                N 188 (N 189 filtered)
    ^https://www\.linkedin\.com/company/[A-Za-z0-9%\-_]{1,100}/people/?$       N 102, J 108
    ^https://www\.linkedin\.com/school/[A-Za-z0-9%\-_]{1,100}/people/?$        N 99, N 100, J 112

Groups and events take the closed numeric segment their id entries already
use. Company and school take the root entries' class, slug AND number: the
captures in `_state/` draw the People tab by slug (by shape: twice on the
company-root capture and twice on a school capture, which draws its own tabs
under `/company/`, never `/school/`), and the `/company/` entry's argument --
a numeric request lands on the slug -- applies unchanged. No line takes a
query or a deeper path.

**THE BLAST RADIUS, BEFORE THE LINES LANDED**, with the shipped
`blast_radius.newly_admitted` over 197 addresses (its 67 plus 130
roster-family spellings: page and filter queries, deeper paths, traversals
onto a profile and an account ending, slugs where the family is numeric,
non-ASCII and over-long ids, dotted segments, a case change, a glued tab
word): groups +2, events +2, company +4, school +4 -- exactly the targets,
nothing unexpected, nothing newly refused. The control: a `/groups/<id>/.*`
family admits 23 over the same corpus.

**THE DIGEST.** `_ALLOWED_URL_PATTERNS` `d7b3315318c877d0 ->
a13f66bebba387cd`, 49 -> 53; the tree minus exactly the four lines hashes to
the prior pin on all eight keys; a needle no line carries moves nothing, and
dropping the pre-existing `/groups/discover/` line instead lands on
`1018aafe63a9f35c`. The six entries that carried the 2026-09-05 refusal
(groups root and id, events root and id, school, company) each gained a dated
comment-only amendment pointing at the roster lines; their refusal text
stands as written.

**`linkedin_server/member_rosters.py::compose(roster, identifier)`** is the
only place the package assembles a roster address: one address per call from
a caller-supplied numeric id, validated by `group_page.group_page_url` for a
group, `company_page.company_identifier` for an organisation, and the same
ten-ASCII-digit, twenty-long rule for an event or a school. Slugs, urns,
non-ASCII digits and over-long runs are refused and described, never quoted.
Nothing in the package imports it (orphan ruling recorded): readers are built
against captures only, and no roster page has been captured.

**THE CONDITIONS, EACH WITH A TEST** (`tests/test_member_rosters.py`, 111):

    1  one page, no automatic pagination   no second page admitted for any
       roster, nine spellings each; A PLANTED PAGINATION LOOP walks ?page=
       and ?start= through assert_read_url and is refused at every step
       past the first; the control installs a query-admitting roster line
       and the loop's second step goes through. compose takes (roster,
       identifier) and nothing else. A pagination-findings guard holds the
       module to no loop, comprehension, await or navigating attribute, and
       six planted paginators (a for over pages, a navigating while, a
       comprehension, a scroll, a show-more press, a page-side import) are
       each convicted.
    2  the id from the tool's arguments     eight refused id shapes on all
       four rosters; the composer and the boundary agree on the numeric
       rosters segment for segment; on company and school the composer is
       STRICTER (no slug), asserted; lane G's navigation-derivation guard,
       both walks and the reader walk, green over the module.
    3  nothing in a tracked file            a storage guard (no open, write,
       dump, and no json/pickle/sqlite/csv/os/io/logging import), with four
       planted stores convicted.
    4  inside the live budget               LOADS_PER_CALL is 1, and the
       ruled forty is the register's LIVE-BUDGET-40-LOADS.
    5  the rows GAP, blocked on a reader    the census, below.

**THE OTHER TESTS THE ROSTERS MOVED**, each inverted with what it used to
assert recorded, none deleted, names kept where an audit cites them:
`test_readonly.py` (two BLOCKED entries inverted into ALLOWED; the roster's
second page and a profile under the tab stand in; the membership-roots test
now asserts each roster on its own line; the "refused by ONE gate" test's
last assertion inverted, same name; the SHOWN-FAILING control now plants a
family and admits the roster's second page), `test_the_groups_id_segment_is_closed.py`,
`test_the_events_boundary_is_root_only.py` (its family control re-measured:
8 of 11), `test_l1_event_by_id_admission.py` (its carrier fragment tightened,
because the attendee line begins with the same characters),
`test_company_page_boundary.py` (its mutation baseline now removes the root
entry by exact text), `test_company_page.py`, `test_company_root.py`,
`test_group_page.py`, `test_school_and_collections_boundary.py`.

**THE CENSUS.** Bucket 3: `N 165`, `N 177`, `N 188`, `N 102`, `N 99` and
`N 100` REFUSED -> ADMITTED, gate MEASURE; `N 189` stays REFUSED on its
filtered spelling (the roster line takes no query) with the bare roster now
an admitted also-driven line; `N 178` unchanged. The jobs side table: `J 108`
and `J 112` REFUSED -> ADMITTED, MEASURE. Pins: `b3_admitted 43 -> 49`,
`b3_refused 35 -> 29`, `jobs_admitted 11 -> 13`, `jobs_refused 26 -> 24`.
**TWO ROWS THE ROSTER DECISION DID NOT LIST MOVED WITH THEIR ADDRESS**: `N 100` (the
same alumni tab as `N 99`) and `J 112` (a school's alumni tab). `N 100` is a
pinned pointer to `N 99`, and the pointer graph went red when `N 99`'s
verdict kind moved (US-BOUNDARY -> US-BOUNDARY|US-RULING); that move is the
point of the commit, so the graph was re-pinned (one line) and `N 100`'s
cell says so rather than moving silently. No STATE moved. The triage's four
roster annotations now say the admission is made.

**THREE GUARDS WENT RED ON THE ITEM-2 COMMIT, AND A SECOND COMMIT FIXED THEM**
(3895 passed, 3 failed). The identity guard read a urn spelled with a digit
run in the new test file's refusal corpus -- now built from the invented id,
as the groups boundary test builds its own. The census prose guard compares
the allowlist count the messaging slice states with the shipped tuple, which
had grown to 53; the slice's cell now says 53 and names the rosters and the
D2 edit. And the citation guard wanted `J 112`'s citation of this record
triaged: the word it matched sits in that row's own sentence about a
containment matcher.

### D. Item 3 -- the WHO/WHICH rule, row by row

The rule as ordered: a row whose payload is WHO (people) or WHICH (items of
other people's content, such as groups or events), served by a count-only
reader, is GAP, its blocker the name-free shaper doctrine pending the
operator's question, with a REOPENER; a row whose payload is an AGGREGATE or a
FILTER, delivered by a count or aggregate reader, can reach COVERED-UNFIRED
once built. Each row below is decided by its OWN words, and the reason is
written into its cell (and its address-table note).

**NO ROW'S STATE MOVED**: every row here is GAP before and after, because no
reader exists -- none of these pages has been captured. What moved is each
row's BLOCKER, and for six rows the address table's gate.

| row | its words | payload | verdict | gate |
|---|---|---|---|---|
| `N 104` | Find an organization's Page by searching for it | an organisation's Page | REACHABLE, if the page draws numeric ids | MEASURE |
| `N 161` | Search for groups by name or keyword | WHICH groups | doctrine | MEASURE -> RULING |
| `N 179` | Search for events by keyword ... Events tab | WHICH events | doctrine | MEASURE -> RULING |
| `M C70` | Search for content within Groups | WHICH posts | doctrine, and an unmeasured address | n/a (refused) |
| `N 165` | View the full member list of a group | WHO | doctrine | MEASURE -> RULING |
| `N 177` | Find people you know through shared group membership | WHO | doctrine | MEASURE -> RULING |
| `N 188` | View the complete attendee list of an event | WHO | doctrine | MEASURE -> RULING |
| `N 189` | See which of your 1st-degree connections ... attend | WHO | doctrine, and a refused filtered spelling | n/a (refused) |
| `N 100` | Use a school's alumni tab to find and contact alumni | WHO, and a write | doctrine for the read half | MEASURE -> RULING |
| `N 178` | See which groups a member belongs to | WHICH, on a third party's profile | doctrine, and NEEDS-TARGET | n/a (refused) |
| `N 102` | Read employee insights on a Page's People tab | AGGREGATE | REACHABLE once built | MEASURE |
| `J 108` | People tab (titles, study areas, skills, how connected) | AGGREGATE | REACHABLE once built; one facet may be WHO | MEASURE |
| `N 99` | View the Alumni page for your school | AGGREGATE | REACHABLE once built | MEASURE |
| `J 112` | School Page Alumni tab | AGGREGATE | REACHABLE once built | MEASURE |

The doctrine rows carry, verbatim in their cells: "BLOCKER, NAMED: the
name-free shaper doctrine (`_audit/2026-09-05-lead-rulings-round-two.md`: this
server does not publish names), pending the operator's question on returning
names at runtime" -- with "here, which groups / events / posts" on the WHICH
rows -- and a REOPENER naming the ruling that would reopen each: the operator
ruling that a search may return which groups, events or posts it found, or
that roster reads may return who, at runtime.

**THE NUMERIC-ID QUESTION FOR `N 104`, ANSWERED.** Yes, on the row's own
words, IF the companies results page draws a numeric organisation id per
result. The row's query names the organisation; what it lacks is where the
Page is, and the package already publishes an organisation by its numeric
Page address (`company_page.company_page_url`, "a digit run cannot be a
name"). A reader returning `company_page_url(<id>)` per result therefore
delivers "find an organization's Page by searching for it": the search is his
keyword, the Page is its address. The limit, stated: the Pages come back in
LinkedIn's order and by address, so where a name is ambiguous the choice is
his. And the branch that says no: if the cards carry slugs only, the reader
cannot publish them (a slug is a name) and cannot resolve them to numbers
without a load per result aimed by page content, which the navigation-
derivation guard forbids. Capture F.1 reads which branch the page is on.

**WHY THE SAME ANSWER DOES NOT CARRY TO `N 161` OR `N 179`**, which a reader of
the table above might expect, given that group and event ids are digit runs
too. Two reasons, both the rows' own: (1) their keyword DISCOVERS items he does
not already know -- "by name or keyword", "by keyword" -- so the payload is
which items exist, where `N 104`'s query already names the organisation; and
(2) the census has ruled on exactly this pairing already.
`linkedin_group_memberships` publishes the numeric ids of the groups LinkedIn
recommends (its `others` tally carries `identifiers`), and `N 162` -- browse
recommended groups -- is COVERED-CANNOT-DELIVER all the same: how many, never
which. `N 180` is the events twin. An id says where a group is; it does not
say which group it is.

**`N 100` AND `J 112` ARE NOT ON THE ORDER'S LIST** and were decided anyway,
because the item-2 admission moved their address: `N 100` is `N 99`'s tab with
a WHO payload and a write half; `J 112` is `N 99`'s tab in the jobs slice, an
AGGREGATE.

### E. Item 4 -- pins and gates

**PINS RE-DERIVED ON THIS BRANCH, each in the commit that moved it.** No STATE
moved anywhere in this follow-up, so every state-derived figure --
`gap`, `adjudicated`, `delivered`, `unfired`, `PINNED_B1_ROWS`, and
`RULING_BLOCKED_NAMED` (still empty) -- is what `ff98a7f` left. What moved:

    readonly digest   _ALLOWED_URL_PATTERNS  c37e98f84ee443f2 -> d7b3315318c877d0   item 1
                                             d7b3315318c877d0 -> a13f66bebba387cd   item 2
                      seven of eight unmoved each time; attribution shown both times
    census_completion b3_admitted   40 -> 43 -> 49      b3_refused  38 -> 35 -> 29
                      jobs_admitted 11 -> 13            jobs_refused 26 -> 24
    pointer graph     N 100 -> N 99, donor kind US-BOUNDARY -> US-BOUNDARY|US-RULING
    ci shard timings  two new test files priced, each from a serial run of
                      itself alone, under an _amended provenance key
    triage            seven DECIDED_SINCE_TRIAGE annotations (N 99, N 100,
                      N 102, N 104, N 161, N 177, N 179); key set unchanged
    orphan rulings    + search_verticals, + member_rosters
    census prose      the allowlist-count row, 49 -> 53

The tool-surface pin is untouched (51 tools, 74 parameters): no tool was
added, and `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` is
green. The address table's gates moved in item 3 (six rows MEASURE ->
RULING); no figure pins the gate split, and the one that could matter --
BLOCKED ON NOTHING -- is 2 before and after.

**GATES RUN, on the final committed tree:** the census instruments --
`census_completion --check` (every figure matches its pin),
`check_read_addresses` (GREEN 94 of 94), `check_jobs_directions` (GREEN 92 of
92), `triage_read_gap_rows` (every control it prints, 1 and 3-9, OK), `ruling_holds` (GREEN),
`check_write_classes` (GREEN), `pin_census_rows` (no drift),
`measure_pointer_graph --check` (pass), and the three generators `--check`
(INDEX, RULINGS, blocker map at their fixed points) -- and one pytest run over
58 test files, 4657 passed and 0 failed in 4m48s: the always-run corpus guards
(18 at the base and 19 now, because `tests/test_member_rosters.py` joined
them -- it sweeps the package for importers, so every future gate runs it,
about two seconds), the navigation-derivation guard among them; the two
page-string guards; this follow-up's four test files; the lane's
people-search tests; and every test file the admissions touched or that pins
a search, roster, company, school, group or event address. Then, while the
cold verifier ran, the other 30 test files that touch the read boundary at
all (every file naming `is_read_url`, `assert_read_url` or the allowlist):
1161 passed, 4 skipped, 0 failed. [The first version of this paragraph said
57 files and 18 guards; the cold verification counted 58 and 19.]

**GATES NOT RUN, and why.** `impact_gate --against ff98a7f --plan-only`:
34 changed paths select 192 of 237 test files (81%), past its 45% line, so it
WIDENS TO THE FULL SUITE -- and the order says not to run that locally; CI
certifies at merge. Nothing live: no browser, no LinkedIn page, no Chrome
profile.

#### E.1 The session-2 budget, and the order to spend it in

`LIVE-BUDGET-40-LOADS` caps a session at forty page loads; `D1-SEARCH-AS-READS`
at five test searches. The lane S live queue already holds four people
searches. Priorities follow section D: a capture is worth a load now only if
the row it serves can move when its reader is built.

    P1  moves a row once its reader is built
        N 84, N 87, N 94   people searches (the live queue)     3 loads, 3 searches
        N 104  F.1         companies search                      1 load,  1 search
        N 102 / J 108 F.5  company People tab                    1 load
        N 99 / J 112  F.6  school alumni tab                     1 load
    P2  measures an address a later admission needs
        M C70  F.4         a group page's search control         1 load
        N 188/189 F.8/1    an event page's attendee control      1 load (the L1 `event` key)
    P3  moves no row until the operator answers the doctrine question
        N 161  F.2 groups search; N 179 F.3 events search        2 loads, 2 searches
        N 165 / N 177 F.7  group member list                     1 load
        N 188  F.8/2       attendee list, if F.8/1 draws it      1 load
    NEEDS-TARGET
        N 85   people search on a member he names                1 load, 1 search
        N 178  F.9         a member's profile, and his ruling    not in session 2

P1 and P2 together are 8 loads and 4 searches, plus the two
`linkedin_job_detail` loads that resolve organisation ids for `N 84` and
`N 87` (F.5 reuses `N 84`'s) -- ten loads, well inside forty, and four
searches of five. TEN IS A FLOOR: every harness run is bracketed by the
control page before and after (two more loads a run, the L1 harness's
convention), which the cold verification pointed out this sum left out; two
runs still stay under twenty. P3's two searches would take the session to six
with the people queue, so they wait for a later session or for the operator's
answer, which would also make them worth their loads.

### F. Capture specs for live session 2

Every capture below is ONE page load through `BROWSER.goto` (which asserts
the address admitted), with `page.content()` written to a gitignored
`_state/` file and never committed. Nothing is typed, pressed, scrolled or
submitted, and the live session's standing brackets apply (the control page
before and after, the anomaly rule). Every address is composed by this
package's composers from values supplied at fire time; no value below
identifies the operator, and none is written into a tracked file. What is
read out of each capture afterwards is offline, by SHAPE and COUNT: never a
name, a slug, a title or a query value.

**THE SEARCH CAP BINDS THE WHOLE SESSION.** `D1-SEARCH-AS-READS`, carried to
every vertical by D2, allows five test searches per live session. The lane S
live queue above already holds four people searches, and F.1-F.3 are three
more, so the session budget is set in section E.

#### F.1 `N 104` -- the companies search

* **Page.** `search_verticals.compose("companies", keywords="robotics")` ->
  `https://www.linkedin.com/search/results/companies/?keywords=robotics`. A
  generic industry word, naming no employer of his; for the row's own proof a
  later fire would search an organisation's NAME, which is what the row does.
* **State.** Signed in; the control page served; nothing pressed.
* **Why the load changes nothing.** A results page lists organisations and is
  READ: reading it follows, messages and invites nobody -- condition 5 of the
  search admission. No member profile is loaded, so nobody is left a
  who-viewed record. The one trace is self-only: LinkedIn may add the keyword
  to his own recent searches, which is the cost the five-search cap prices.
* **What to read off it.** Landed on the companies vertical by closed-segment
  equality; the number of result cards; **whether each card carries a
  NUMERIC organisation id** (a `/company/<digits>/` href or a digit-bearing
  entity urn) or slugs only, counted by shape; the results-count element;
  whether a pagination control is drawn (never pressed); and the shipped
  `search_results.read_results` / `read_filters` run over the capture offline.
* **What it decides.** Whether a reader can return
  `company_page.company_page_url(<digits>)` per result (section D gives the
  row's verdict on that).
* **Cost.** 1 load, 1 of the session's 5 searches.

#### F.2 `N 161` -- the groups search

* **Page.** `search_verticals.compose("groups", keywords="open source")` ->
  `https://www.linkedin.com/search/results/groups/?keywords=open+source`.
* **State.** As F.1.
* **Why the load changes nothing.** As F.1. A results page may draw a join
  control per group; joining is a write with its own row, and nothing is
  pressed.
* **What to read off it.** Landed vertical; result cards; group ids by shape
  (`/groups/<digits>/`, the form `groups.py` counts); the results count;
  whether join controls and pagination are drawn (counted, never pressed).
* **Cost.** 1 load, 1 search.

#### F.3 `N 179` -- the events search

* **Page.** `search_verticals.compose("events", keywords="developer
  conference")` -> `https://www.linkedin.com/search/results/events/?keywords=developer+conference`.
* **State.** As F.1.
* **Why the load changes nothing.** As F.1. An event card may draw an attend
  or register control; attending is `N 185`'s write, and nothing is pressed.
* **What to read off it.** Landed vertical; result cards; event ids by shape,
  and whether the SLUG form (the event's title run into its id) is what the
  cards link, which the boundary does not admit; the results count; attend
  controls and pagination drawn (counted, never pressed).
* **Cost.** 1 load, 1 search.

#### F.4 `M C70` -- where LinkedIn searches inside a group

* **Page.** `/groups/<id>/` (admitted since 2026-09-19), `<id>` a group he
  belongs to, supplied at fire time -- the numeric ids
  `linkedin_group_memberships` returns are the source, passed as an argument
  and not read off a page by any code.
* **State.** As F.1. NO search is fired: this load finds the address, it
  does not use it.
* **Why the load changes nothing.** A group he belongs to, opened by its
  numeric id, is the load `linkedin_group_page` made three times on
  2026-09-21 (`N 175`); an entity page leaves nobody a view record.
* **What to read off it.** The search control the page draws: its form
  action or href by SHAPE -- which vertical (`content`?), which parameter
  names carry the group -- never a value. If it is the content vertical with
  a group facet, the row needs a ruling to widen the search line to
  `content`, which D2 did not make; if it is its own address, that address
  needs its own admission.
* **Cost.** 1 load, 0 searches.

#### F.5 `N 102` and `J 108` -- a company's People tab

* **Page.** `member_rosters.compose("company_people", "<id>")` ->
  `https://www.linkedin.com/company/<id>/people/`. `<id>` is the numeric
  organisation id of a LARGE organisation that is not his employer, current
  or past -- the `company_id` `linkedin_job_detail` resolves on a posting. The
  live queue's `N 84` call already resolves one such id in the same session,
  so this costs no extra load for the id.
* **State.** Signed in; nothing pressed, nothing scrolled.
* **Why the load changes nothing.** An organisation's page emits no view
  receipt to anybody -- the cause the `/company/` entry turns on. The tab
  lists members and loads none of their profiles, so nobody is left a
  who-viewed record. A follow or connect control drawn beside a member is a
  write, and nothing is pressed.
* **What to read off it.** Where it landed (did the number redirect to the
  slug? by shape); the INSIGHT panels -- how many, and whether each is a
  count-bearing chart drawn on the first load or behind a "next" press (a
  press would be a PRESS gate, not a reader); the number of member cards
  (`anchors.read_anchors`' member-profile count); whether a "show more"
  control is drawn (never pressed).
* **What it decides.** Whether an aggregate reader can deliver both rows from
  the first page alone (section D).
* **Cost.** 1 load.

#### F.6 `N 99` (and `N 100`, `J 112`) -- a school's alumni tab

* **Page.** `member_rosters.compose("school_people", "<id>")` ->
  `https://www.linkedin.com/school/<id>/people/`. `<id>` is a numeric school
  id the operator supplies at fire time, and for the CAPTURE it is a school
  that is not his campus: the capture reads the page's structure, and the
  row's own proof -- his school -- is a later, separate fire.
* **State.** As F.5.
* **Why the load changes nothing.** As F.5: a school is an organisation page,
  and the tab loads no member's profile.
* **What to read off it.** First, WHERE IT LANDS -- a captured school page
  draws its own tabs under `/company/<slug>/`, so the numeric school address
  may redirect there, which the landing shape shows (both spellings are
  admitted); then the same readings as F.5.
* **Cost.** 1 load.

#### F.7 `N 165` and `N 177` -- a group's member list

* **Page.** `member_rosters.compose("group_members", "<id>")` ->
  `https://www.linkedin.com/groups/<id>/members/`, `<id>` a group he belongs
  to, from the numeric ids `linkedin_group_memberships` returns, passed at
  fire time.
* **State.** As F.5.
* **Why the load changes nothing.** A member of a group can open its member
  list; the list loads no member's profile; joining, leaving and messaging
  are writes and nothing is pressed.
* **What to read off it.** Member cards (member-profile anchor count); any
  drawn member COUNT; whether connection-degree badges are drawn per card
  (`N 177` is about people he knows); "show more" drawn, never pressed.
* **Cost.** 1 load.

#### F.8 `N 188` and `N 189` -- an event's attendees

* **Step 1.** `/events/<id>/` (admitted since 2026-09-23; the L1 harness's
  `event` key already loads it), `<id>` an event he can open, supplied at
  fire time. Read the attendee control's href BY SHAPE -- is it
  `/events/<id>/attendees/`, or a people search carrying an event facet? --
  and press nothing. Also read, by shape, the address the 1st-degree filter
  is drawn with, if one is drawn (`N 189`).
* **Step 2, ONLY if step 1 draws `/events/<id>/attendees/`.**
  `member_rosters.compose("event_attendees", "<id>")`, once. If the list is
  a people search with an event facet instead, stop: that is a people-search
  facet, D1 governs it, and `people_search.compose` would need the facet --
  a composer change, not this admission -- and the roster line should then be
  withdrawn as a page LinkedIn does not serve.
* **Why the loads change nothing.** An event page is an entity page; attending
  is `N 185`'s write and nothing is pressed.
* **Cost.** 1 load, or 2; step 1 is shared with the `event` key.

#### F.9 `N 178` -- NEEDS-TARGET

* **Page.** Another member's profile, at the section that lists their groups
  (their interests, the groups tab). It is REFUSED by the boundary: the
  third-party profile pattern was removed on his own call of 2026-09-04,
  and `PERMANENTLY_FORBIDDEN` names the act.
* **Why the load is NOT nothing.** Loading another member's profile leaves
  that member a who-viewed record: an act toward that person, so
  `OUTWARD-ACTS-NEED-THE-OPERATOR` governs it and HE NAMES THE MEMBER. Even
  then the address needs a boundary decision that reverses his own
  2026-09-04 ruling, which is his, not a lane's.
* **State.** NEEDS-TARGET. Not in session 2 unless he names a member and
  rules on the address.
* **Cost.** 1 load, when he does.

### G. The cold verification, and what it changed

One cold pass by a `general-purpose` child after the four items, briefed to
find what is wrong rather than to confirm, read-only, with its own
adversarial corpora (1557 spellings of its own), its own AST diff of the
boundary, the shipped digest function, extracted trees of three commits and
the WHATWG URL parser in Node for landings. Its verdicts: the boundary diff,
the digests, every blast-radius number, reachability, census consistency and
the instruments PASS; 44 of the record's numbers MATCH. It ran 2065 tests on
its own list and 4535 on a 55-file gate of its own choosing, 0 failed. It
FAILED three checks, and each is answered below.

**1. AN ENCODED DOT SEGMENT WALKED PAST THE BOUNDARY (MEDIUM) -- FIXED.** The
two new People-tab lines carried the root entries' class, `%` included, and
admitted `/company/%2e%2e/people/`: the URL standard reads `%2e%2e` as `..`,
so a browser lands on `/people/`, which the boundary refuses and `goto` never
re-checks. The root lines had the same hole, older (`/company/%2e%2e/` and
`/school/%2e%2e/` landed on the site root), and their own comments promised
a dotted slug fails closed. The 197-address corpus held literal dots only.
Fixed on all four lines -- `%` dropped from the People lines, a lookahead
refusing a segment of one or two encoded dots on the roots -- with
`company_page.slug_is_addressable` refusing the same six spellings so the
root/shaper coupling still agrees. Over 1705 addresses (the shipped corpus,
the verifier's 1562, 96 more): 90 newly refused, nothing newly admitted,
percent-encoded names still admitted on the roots. Digest `a13f66bebba387cd ->
17409e16e7abbcc8`. Reach before the fix was nil (nothing composes such an
address), so this was defence in depth, not an open route.

**2. THREE PROBES HELD A CONTROL THE ADMISSIONS OPENED (MEDIUM) -- FIXED.**
`_probe_newsletter_routes.py` and `_probe_route_vs_surface.py` refused to
certify their tables, and `_probe_unmeasured_surface_addresses.py` failed
its control and exited 0 anyway. Each control is re-aimed at the People
tab's query spelling, the class it held; the last probe now exits 1 on a
failed control; and `_probe_route_vs_surface.py`'s OTHER control, the people
search, had failed since 2026-09-20 unnoticed and is re-aimed at the content
vertical. `_probe_company_family_blast.py` was removing two `/company/`
entries by prefix again -- the defect its own comment records from its first
run -- and now removes the root by its full text. All four exit 0 with every
control passing.

**3. A SHIPPED PAYLOAD STATED A FALSE BOUNDARY FACT (MEDIUM) -- FIXED.**
`company_root`'s `count_read` verdict told every caller the People tab "is
refused by the read boundary", as did `linkedin_company_page_counts`'
description and `company_page`'s docstrings. Each now says the tab is not
opened by that tool, and is admitted on its own roster line that no tool
reads yet.

**THE LOWER FINDINGS, AND WHAT WAS DONE.** The roster test's import walk was
blind to relative imports; it now uses the orphan test's reader, with five
planted forms. Its condition-4 test now says it cannot catch a budget overrun
-- the budget is carried by process, not code. `ROSTER-ENUMERATION` in
`scripts/check_exclusion_basis.py` needed nothing: it is already in `EMPTIED`,
so a row filed on it fails the run. The PINNED comment in
`census_completion.py` now says six of the moved rows were re-gated RULING;
the triage's `N 178` annotation carries its item-3 verdict;
`search_verticals.ROWS_SERVED` is renamed `ROWS_NAMED_BY_THE_RULING`, because
`M C70` is named for groups and its page is not the groups search; and the
kept prior notes that still said "refused" carry a dated marker. Section E's
counts are corrected (58 files, 19 always-run guards) and E.1 prices the
bracket loads.

**LEFT AS THEY ARE, and why.** The two red intermediate commits (the item-1
and item-2 commits each failed a corpus guard, repaired by the commit after)
stay: history is not rewritten here, and the merge can squash each pair.
Fifteen non-ASCII bytes in `_audit/_census/network.md` are on four lines this
lane never touched. The school People line admits a spelling no capture draws
-- capture F.6 decides, and the line should go if the tab lives only under
`/company/`. The argument separating `N 161` from `N 104` ("discovers" against
"names") is weaker than the rule it supports; the verdict stands on the rule.
And condition 1 of the search admission still needs the orchestrator's
reading (section B).

**THE FIX, RE-CHECKED WITH THE VERIFIER'S OWN INSTRUMENT** (its break script,
re-run on the fixed tree rather than a second pass): dot segments 133 of 133
refused (8 admitted before), encoded `;` parameters 28 of 28, the root lines'
encoded dots 7 of 7. What it still admits is 17 addresses of two pre-existing
kinds: the search line's open query shape (`?` alone, `??`, a second `?`
inside the query -- a query cannot move the path, and S1 carried the same
shape since 2026-09-20), and an encoded slash INSIDE one root-line segment
(`/company/a-company%2Fpeople/`), which a browser keeps encoded; whether
LinkedIn's server decodes it before routing is UNVERIFIED, and it is filed
here, not changed.

## Integration (follow-up) 2026-09-24

The orchestrator's integration order of 08:32: merge `master` `1902fcb`;
rewrite the blocker of the nine WHO/WHICH rows, and of `N 79`, `N 194` and
`N 172` from the first pass, on the operator's answer of 08:11
(`NAMES-AT-RUNTIME`, registered on that commit with the orchestrator's
`PEOPLE-DATA-MITIGATIONS` and `OUTWARD-CLASSES-BUILT-BEHIND-GRANTS`);
re-derive the pins; run the gates; commit. The same order accepted section
B's reading of condition 1 of the search admission: the admission is inert
until a reader lands, and the reader now returns names under the six
mitigations.

### J.1 The merge of `master` `1902fcb` (`3a7da6b`)

Master since `ff98a7f` carried the live lane's session 1, rulings batch 4,
lanes L7 and Y2, the fix after L7, and the names-at-runtime calls. Conflicts,
and how each was resolved:

    census slices     jobs.md, network.md: row by row against the base, each
                      row from the side that changed it -- Y2's appended
                      evidence on J 107, J 109, J 110, J 111, N 103, N 176;
                      this lane's cells on J 108, J 112, N 102, N 104, N 177,
                      N 178. No row was changed on both sides.
    read-addresses    this lane's M C70 and N 161 lines; M C72 and N 134 gone,
                      as master removed them (proven live, out of bucket 3)
    pointer-graph     this lane's N 100 donor kind; master's removal of the
                      N 134 and N 135 pointers
    boundary ledger   both entries kept: the two sides moved DIFFERENT tables
                      -- master SANCTIONED_MUTATIONS e79a701b37ae9c39, this
                      lane _ALLOWED_URL_PATTERNS 17409e16e7abbcc8
    census pins       both histories kept; the four moved figures MEASURED on
                      the merged tree, never summed from the two sides' claims
    shard timings     master's table and convention; this lane's two test
                      files re-priced on the merged tree

**THE ENCODED DOT-SEGMENT FIX SURVIVED THE MERGE INTACT**, shown with the
cold verifier's own break script on the merged boundary, not a new one: 0 of
133 dot-segment spellings admitted, and 0 of the 7 encoded dots on the
pre-existing root lines. The script still admits 17 addresses, the same 17
as when the fix was re-checked (section G), in two pre-existing kinds -- 15
open query shapes on the search line and 2 encoded slashes inside one root
segment -- and for all 17 the browser's landing is the string itself: its
list of admitted addresses whose landing differs is empty.

The generated files (`_audit/INDEX.md`, `_audit/RULINGS.md`, the blocker
map) were already at their fixed point for the merged corpus. The merge
was gated after it was made (made 08:43, the run finished 08:51), on the
tree J.2's squash re-used byte for byte: 4691 passed, 0 failed, including
`tests/test_gap_rows_on_refused_addresses.py` and
`tests/test_the_package_compiles_on_its_oldest_python.py`.

### J.2 The two gate-fix pairs, squashed

The order allowed squashing each gate-fix pair into its item only if that
was clean. Section G had left both in place (the item-1 and item-2 commits
each failed a corpus guard, and the commit after each repaired it). A rebase
would have had to re-make the merge and re-resolve every conflict in it, so
the squash was done by plumbing instead: each rewritten commit reuses its
ORIGINAL TREE, byte for byte, so nothing was resolved twice. The merge was
re-made from its own tree with the same second parent, `1902fcb`. Authors,
committers and dates are the originals'. The only new text is the two
squashed messages, each the item's message followed by its fix's.

    the D2 item and its gate fix        -> one commit (`bfeeb61`)
    the rosters item and its gate fix   -> one commit (`b9b3df2`)
    every later commit, tree for tree   -> the merge (`3a7da6b`) and this
                                           integration's census commit
                                           (`e251be7`)

Before the branch moved, three things were checked. Every new commit's tree
hashes equal to its original's, and the new tip's tree equals the old tip's.
Nothing cited a rewritten hash: no tracked file and no commit message on the
branch. No other branch or tag contained any of them, and none was ever on
`master`. The branch was moved with an old-value check, so a concurrent
writer would have made the move refuse. No commit on the branch now holds an
item without its gate fix.

### J.3 Names at runtime, row by row

**NO ROW'S STATE MOVED.** Every row below is GAP before and after: no
reader returns names yet. What moved is each row's BLOCKER, and for nine of
them the address table's gate. Each cell keeps the doctrine paragraph it was
blocked on as that day's record and gains a paragraph after it, opening
"NAMES AT RUNTIME, 2026-09-24", which says the doctrine question is answered
and names what holds the row now. Each earlier address-table note is kept
after a marker naming what answered it.

| row | payload | holds it now | gate before | gate now |
|---|---|---|---|---|
| `N 79` | WHO | a name-returning reader | RULING | READER |
| `N 194` | WHO | a name-returning reader | RULING | READER |
| `N 172` | WHO | a name-returning reader; the member from tool arguments only | RULING | READER |
| `N 161` | WHICH groups | the reader, and capture F.2 | RULING | MEASURE |
| `N 179` | WHICH events | the reader, and capture F.3 | RULING | MEASURE |
| `N 165` | WHO | the reader, and capture F.7 | RULING | MEASURE |
| `N 177` | WHO, by degree | the reader, and capture F.7 | RULING | MEASURE |
| `N 188` | WHO | the reader, and capture F.8, which also finds the address | RULING | MEASURE |
| `N 100` | WHO, and a write | the reader and capture F.6, for the read half | RULING | MEASURE |
| `N 189` | WHO, filtered | the reader, capture F.8, and an address | refused | refused |
| `N 178` | WHICH, on another member's profile | the reader, and a member he names | refused | refused |
| `M C70` | WHICH posts | the reader, capture F.4, and an admission | refused | refused |

"The reader" in every row is the same thing: a name-returning reader held to
`PEOPLE-DATA-MITIGATIONS`, on the shared people-record foundation lane G is
building. The first three are READER because their page is already captured
(the live lane's session 1 loaded the people-search results page through
`linkedin_people_search_shape`: `_audit/2026-09-23-live-lane-session-1.md`,
entry 5, item 9); the next six are MEASURE because nobody has captured
theirs.

**WHAT THE READER GATE COUNTS HERE, STATED.** The census counts a row
BLOCKED ON NOTHING when it is ADMITTED and gated READER or PRESS-PERMITTED,
so the three READER rows move that figure from 5 to 8. For these three it
means blocked on no decision and no measurement. It does NOT mean buildable
today: their reader waits on lane G's foundation, a build this lane does not
own.

**TWO QUESTIONS THE ANSWER LEAVES OPEN, for the orchestrator.**

1. `M C70` asks for posts. The mitigations declare a person's record and a
   group's or event's record, and no post's. Before any reader returns what
   a search inside a group finds, somebody has to declare a post's fields.
   A post is another member's text: is it a title and a link, like a group,
   or more?
2. `N 178` reads which groups a member belongs to, off that member's
   profile. `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET` loads such a profile
   only inside an outward act whose target the operator names, and never for
   a measurement. This row is a read, not an outward act, so even with a
   member he names it has no route. Delivering it needs his decision that a
   named member's profile may be loaded for a read; otherwise it stays GAP
   on that, NEEDS-TARGET either way.

### J.4 Pins, re-derived on the final tree

    readonly.py AST digests      8 of 8 equal their pins; no change since
                                 the merge
    census_completion            b3 admitted 51, refused 37; jobs admitted
                                 13, refused 34 (all measured at the merge);
                                 b3_blocked_on_nothing 5 -> 8 in this
                                 integration, with its history line
    pin_census_rows              no drift: the live population is the pin
    pointer graph                PASS, 66 pinned pointers
    address table                GREEN 104 of 104: READER 8, MEASURE 25,
                                 BUILT-UNFIRED 4, PRESS 8, RULING 6 (none of
                                 them this lane's rows), BLOCKED ON NOTHING 8
    jobs side table              GREEN 107 of 107
    triage                       every control OK (1, 3-9); the
                                 DECIDED_SINCE_TRIAGE notes for the nine rows
                                 name the new blocker and gate, and keep the
                                 verdict letter RULING, which CONTROL 8 needs
    tool surface                 untouched: no tool added or removed
    shard timings                the follow-up's two files priced at the
                                 merge, serially on the merged tree
                                 (3.947 s and 4.245 s); the first pass's
                                 file, never priced before, priced now,
                                 alone and serially on the final tree
                                 (109 tests, 9.139 s); 168 files priced

### J.5 Gates

**RUN, on the integration's census commit**, whose tree J.2's squash
re-used byte for byte (the record's own commit adds
this section and the one timing, and is gated by the corpus-wide guards and
the three generators after it):

- The census instruments: `census_completion --check` (every figure
  matches its pin), `check_read_addresses` (GREEN 104 of 104),
  `check_jobs_directions` (GREEN 107 of 107), `triage_read_gap_rows`
  (controls 1 and 3-9 OK), `ruling_holds` (GREEN), `check_write_classes`
  (GREEN, 339 lines), `check_exclusion_basis` (70 of 70, no structural
  problem), `pin_census_rows --check` (no drift),
  `measure_pointer_graph --check` (PASS, 66), and the three generators
  `--check` (the audit index, the rulings index, the blocker map).
- The verifier's break script, as J.1 gives it.
- One pytest run over 121 test files: the impact gate's own selection for
  this integration's staged diff (68 files, the 20 corpus-wide guards among
  them), every test file that names the read boundary (69), and ten named by
  the order or this lane, `tests/test_gap_rows_on_refused_addresses.py` and
  `tests/test_the_package_compiles_on_its_oldest_python.py` among them:
  7223 passed, 4 skipped, 1 xfailed, 0 failed, in 16m48s on six
  workers. The JUnit report agrees: 7228 cases across 120 files, the
  121st path being `tests/conftest.py`, which holds none.

**THE FIRST ATTEMPT AT THAT RUN RAN NOTHING.** The file list was written in
text mode on Windows, so every path ended in a carriage return, and pytest
collected zero tests ("no tests ran", exit 5). An exit of 5 is not a pass,
and nothing was read off it: the list was rewritten with bare newlines,
counted (121 paths, no carriage return), and run again.

**NOT RUN, and why.** `impact_gate --against 1902fcb --plan-only`: 226 of
245 test files (92%), past its 45% line, so it WIDENS TO THE FULL SUITE,
which the order says not to run locally; CI certifies at merge. Nothing
live: no browser, no LinkedIn page, no Chrome profile.

### J.6 The session-2 plan and the capture specs, after the answer

**E.1'S THIRD TIER NO LONGER HOLDS ITS REASON.** P3 was "moves no row until
the operator answers the doctrine question". He has answered, so each P3
capture now moves a row once the name-returning reader lands, which is P1's
reason. Joined to P1, the session wants six searches -- `N 84`, `N 87`,
`N 94`, `N 104`, `N 161` and `N 179` -- and `D1-SEARCH-AS-READS` allows five.
The order that fits: the three people searches first (they fire readers
already built); then `N 104`'s companies search (its reader returns Page
addresses, not names, so it does not wait on lane G); then ONE of `N 161`
and `N 179`, the other to the next session. Loads stay well inside forty:
the ten E.1 counted, plus three of P3's four (one search waits), thirteen
before the bracket loads.

**THE CAPTURES THEMSELVES, AND MITIGATION 3.** Section F writes each page's
full content to a gitignored file, the way this repository has always
captured: `scripts/_build_job_list_skeleton.py` builds a committed skeleton,
keeping only the attributes its reader reads, from a raw capture that stays
local and is never committed. F was written before `PEOPLE-DATA-MITIGATIONS`,
whose third mitigation says no third party's name, headline or link is
written to a tracked file, a log, an error field, a receipt, a cache or a
fixture; that fixtures use synthetic people; and that live evidence records
counts and hashes. Whether a gitignored raw capture is such a store is
decided nowhere. This lane reads it as one, for a page OF people, and adopts
the stricter form for its own specs from here. Nothing F asks to read off a
capture is lost by it, since all of that is read by SHAPE and COUNT:

- The skeleton reduction moves INTO the session: the page is reduced before
  anything is written, every text node and every attribute value replaced
  by its shape (digit run, letter run, length) and a hash; tags, attribute
  names and classes are kept, since a reader's selectors are built on those.
- What F asks for -- landed vertical, card counts, ids by shape, controls
  drawn -- is computed from the skeleton, and only counts and hashes are
  recorded.
- The name-returning reader's fixtures are synthetic people poured into that
  skeleton, never a captured page.

The session-1 capture of the people-search page was made before the
mitigations were registered and sits in the live lane's gitignored state;
this lane has not touched it. Whether it is reduced the same way, and
whether this reading holds at all, is the orchestrator's call.

### J.7 What comes next

After lane G lands the shared people-record foundation, not before: switch
`linkedin_people_search_shape` to return names through it, and build the
roster and vertical readers on it -- their composers, `member_rosters` and
`search_verticals`, exist and nothing calls them yet -- each held to all six
mitigations and each mitigation shown failing without its code, as the call
requires. `N 79`, `N 194` and `N 172` then become COVERED-UNFIRED, and
`tests/test_people_search_readers.py`'s `ROW_STATES` table moves with them in
the same commit. The six MEASURE rows then need their captures, in the order
J.6 gives.

## Names returned 2026-09-27

The orchestrator's order of 2026-09-27 20:05: with lane G's people-record
foundation on master, "people search and rosters return names". Three parts:
(a) the people search and the readers for `N 79`, `N 194` and `N 172`
return WHO as people records under all six mitigations, each with a test that
can fail, built over captured markup only; (b) the rosters, read where a
capture exists and specified for capture where none does, admitting no
address a capture has not shown served; (c) the census moved only where a
reader returns names, every pin re-derived, and an AST duplicate-key check
over the pinned dicts.

### K.1 Step 0, checked against disk before it was obeyed

Master was at `52b55b6`; this branch's `d296684` was already inside it, so
the worktree moved by fast-forward and nothing was merged. `people_data.py`,
`PEOPLE_TOOLS` and the four named guards were on master, and
`NAMES-AT-RUNTIME`, `PEOPLE-DATA-MITIGATIONS` and
`PREVIEW-NAMES-THE-RESOLVED-TARGET` were registered. Disk agreed with the
order. One thing from the previous section's own gates: the local run over
`d296684`'s four paths stopped at 99% when the session was interrupted on
2026-09-24 -- no summary line and no failure mark in its progress -- and CI
on master has run over that commit since.

### K.2 What was built

**`linkedin_server/people_results.py`, a module of its own, not
`people_search.py`.** That module composes the address, and its proof that
no page value can reach an address is that it touches no page -- asserted on
its syntax tree. A reader takes a page, so it lives beside it, and the proof
is intact. `read_result_people(page)` returns
`{"people": [<Person envelope>, ...], "people_denominators": {...}}`. As first
committed (`a734527`) it read through Playwright LOCATORS, which re-find
their element on every call; after the cold verification (K.9) it pins every
card to an ELEMENT HANDLE before any text is read, reads only through those
handles, and reads both links again after the text. Either way it runs no
script: the one-page and page-string guards reach it with no new evaluate
waiver and no change to `dom.py`.

**`linkedin_people_search_shape(include_names=False)`.** Off by default, the
package's opt-in for a people payload (`linkedin_open_messaging` set it
first), so the tool's default is unchanged -- the shape and nobody -- and the
four FILTER rows it delivers are untouched. With it, the envelope carries
`people`, `people_denominators` and `names_included`. `include_names` is not
handed to `compose`: it decides what is read, never where the tool goes.

**`server.py`, touched in two places and nothing else:** the tool (its
parameter, its docstring and five lines of its body) and one sentence of the
server instructions, which name every people tool -- a guard holds that
sentence equal to `PEOPLE_TOOLS`, so adding the tool to one without the other
fails. `people_data.PEOPLE_TOOLS` gains the tool in the same change, as its
own comment requires.

### K.3 The capture, read for structure only

The one capture of a people-search results page is the live lane's, from
session 1: a gitignored file in that lane's worktree, 174,412 bytes. It was
read OFFLINE by scratch scripts that print tags, attribute names, text SHAPES
(length, word count, character classes) and a closed list of interface words
-- never a name, a headline, a place or a slug. Measured on every result, not
a sample:

    results                          10, the ten children of one list
    rows drawn with no member link   0
    each result                      ONE link to the member, holding a second
                                     link to the same member -- the name
    the title paragraph              exactly one member link, then one text:
                                     the degree, "2nd" on all ten
    the column beside it             exactly three elements on all ten: the
                                     title and two link-free lines
    line 1 (the headline)            28 to 181 characters; a '|' or the word
                                     'at' on all ten
    line 2 (the location)            27 characters, 3 words, a comma: all ten
    mutual connections               19 links to OTHER members (one result
                                     names one, nine name two), all inside
                                     the results
    member hrefs                     all 40 absolute, 39 of them bare
                                     `/in/<slug>/`, one a level deeper
    class names                      generated hashes; the reader reads none

**THE "17 PERSON RESULTS" OF THE SESSION RECORD IS A COUNT OF LINKS,
MEASURED.** The shipped counter's `person_result` is an anchor whose route is
`/search/results/people`, so it counts links TO a people search, not people.
Counted on the capture: 17 of its 77 anchors carry that route -- the ten
results' "other mutual connections" links, and seven more on a second line
some results draw -- while the page drew ten results. The census cells
quoting the 17 are answered in their own new paragraphs.

**THE SHIPPED READER, RUN OVER THE REAL CAPTURE.** In a headless browser
whose every request was aborted, the capture converted to XHTML in memory
(so no copy of it touched disk) and imported through an XML parser:
`read_result_people` returned all ten, zero skipped, zero failed; every
record exactly the four declared fields and the marker; the degree "2nd" on
all ten; and each name and headline EQUAL, compared by digest in memory, to
the capture's own static reading. Nothing of any person was printed.

### K.4 The fixture, and the builder that made it

`scripts/_build_people_search_skeleton.py` turns a capture into
`tests/fixtures/synthetic/people_search_results.html`: the first three results,
every tag and every nesting kept -- including the link inside a link -- and
every text and attribute value replaced. Results and mutual connections
become seven declared synthetic people with their declared slugs (the pairs
invented for `connections_list.html`, so no declaration was added);
headlines and the place are invented; the degree, "Connect", punctuation and
"<n> other mutual connections" are kept as interface text; an href is
rebuilt from its parts and a kept attribute keeps only a value from its
closed set. It prints counts only -- over the capture: 10 results, 3 kept, 7
people, 0 labels dropped, 0 attribute values dropped, 0 placeholder hosts,
and 4 text nodes it could not classify, written as "Example text" (the same
pair in two results: a one-character punctuation and a two-word phrase with
digits linking to a people search; the reader reads neither) -- and the
structure digest `hljfpfdmkfekafdh`.

**WHY XHTML.** A page built with DOM calls can hold a link inside a link;
HTML's parser cannot, and closes the outer link at the inner one. So the
fixture is well-formed XHTML and the tests import it through an XML parser,
and a test shows the HTML parser losing the shape -- the reader then finds
no card at all.

**WHAT PINS IT.** Run over the fixture, the builder reproduces it byte for
byte, which pins the text and the order people first appear -- a normal
form -- and the builder's own changes. The STRUCTURE is pinned by the digest
the builder printed over the capture, recomputed from the fixture by a test
whose control deletes every photo figure; whoever holds a capture can
re-derive it (K.9, finding 3).

The previous section's J.6 proposed reducing a capture inside the live
session before anything is written. This build reduced the capture the live
lane had already written, in the way `scripts/_build_job_list_skeleton.py`
does: the capture stays in that lane's gitignored state, untouched, and
nothing from it was copied into a tracked file. Whether session 2 reduces in
the session is still the orchestrator's call.

### K.5 The six mitigations, each with a test that can fail

`tests/test_people_search_names.py`, 73 tests, every browser headless
with every request aborted:

    0  the fixture: XML, a link in a link per result, the captured column
       shape, only declared synthetic people; its fixed point, its structure
       digest, and the builder's refusals
    1  the reader over the fixture returns the three results as people, and
       nobody else -- no mutual connection, no place, no furniture; the HTML
       parser's version of the page returns nobody
    2  M1 declared fields only: every person exactly a record, nothing else
       in the result; a record carrying the location is convicted; the
       location's text never READ (every text a handle returned, spied)
    3  M2 sanitised and marked: a name laced with a zero-width space and a
       direction override, and an instruction-shaped headline, come back
       inert and marked; a control shows the page really drew the lacing
    4  M3 never stored: the TOOL driven end to end with the plant as a
       result's name and headline -- the plant only inside the three records
       -- and a second plant as a mutual connection's name, which crosses
       nowhere, not even inside a record; a failure counted by type, never
       quoted; nothing logged on the success path, at any logger; no file
       written; no state kept between calls, in any shape
    5  M4 one page: one navigation, pages_loaded 1, no paging parameter, the
       tool a declared people tool, the ceiling enforced, and an allowlist
       of the calls the reader may await -- no hover, wheel, scroll or key
    6  M5 visible only: a result drawn as "LinkedIn Member" comes back as
       exactly that while hidden copies still name the person; a row with no
       member link is not read; only href is read; no script is run; a hidden
       card, and text nested in the name link, are refused
    7  M6 not a target: only the server imports the reader, and no write
       tool reaches it through any chain of helpers
    8  without include_names the tool returns nobody and never calls the
       reader; with it, the same drive returns the three
    9  the verifier's drawings: each refused or absent and counted, a
       re-render mid-read and a node reused mid-read included; the one
       declared limit as a strict xfail
   10  the verifier's other surviving routes, each with its control

**SHOWN FAILING ON THE READER ITSELF.** Over the first reader, four
defects planted one at a time were each caught. Over the reader as
rewritten, fifteen are planted -- the verifier's surviving routes among
them -- and that check is recorded in K.11, with the final gates.

Lane G's guards reach the reader without an entry being written for it: the
one-page guard derives the tool as a people tool, the page-string guards
drive the reader (its baseline verdict `clean` -- vacuous on the success
path, K.9 finding 2), and the instructions guard holds the named tools equal
to `PEOPLE_TOOLS`.

### K.6 The census

**THREE ROWS MOVE GAP -> COVERED-UNFIRED:** `N 79`, `N 172` and `N 194`,
each cell opening on the paragraph that moved it; the WHO-rule and
names-at-runtime paragraphs stay after it as those days' record. Not PROVEN:
nothing fired. They leave the address table (104 -> 101 lines), enter
bucket 1 held by no ruling, and leave the triage's read-GAP set (77
verdicts; every control OK). The tool-surface pin moves 90 -> 91 parameters
with the rows named.

**PINS, RE-DERIVED AND MEASURED:**

    adjudicated            179 -> 182
    delivered_broad        117 -> 120
    unfired                 38 ->  41
    gap                    591 -> 588
    gap_read               104 -> 101
    b3_admitted             49 ->  46
    b3_blocked_on_nothing    7 ->   4
    b1_no_ruling            23 ->  26

**THE ROWS THAT WAIT ON A CAPTURE STAY GAP**, each cell gaining a paragraph
that says the foundation has landed and names what holds it now -- the
capture, then a reader over it: `N 161` (F.2), `N 179` (F.3), `M C70` (F.4,
and a post's declared fields), `N 100` (F.6), `N 165` and `N 177` (F.7),
`N 188` and `N 189` (F.8), and `N 178` (a decision of the operator's, then
F.9). The aggregate rows `N 99`, `N 102`, `J 108` and `J 112` and the
companies search `N 104` return no names and were not touched.

**AST DUPLICATE-KEY CHECK.** Every dict literal in the package, the scripts
and the tests (4,026) and every JSON file under tests and scripts (13), keys
compared as literals and as names. The pinned dicts -- `PINNED` 37 keys,
`PINNED_B1_ROWS`, `TRIAGE` 77, `DECIDED_SINCE_TRIAGE` 9,
`MEASURED_PAST_BY_BUCKET3` 4, `ROW_STATES` 7, `PINNED_TOOL_SURFACE` 57,
`COVERED_ROWS` 9, `TARGET_KIND_CLASS` 12, `NOT_A_CORRECTION` 212 -- carry no
duplicate. ONE DUPLICATE ON THE TREE, not in a pin and not this lane's:
`tests/test_selectors_resolve.py` gives the key `settings_radio_label_selector`
twice, once for "Always on" and once for "Device settings", so the second
replaces the first and the "Always on" label selector is never resolved --
though the comment on the second says both are resolved so that a break in
either spelling fails there. Reported, not edited: the fix is to give the
second its own key.

### K.7 The rosters: no capture exists, so each waits on one

No roster page has ever been captured -- not a group's members, an event's
attendees, nor a company's or school's People tab -- so no roster reader was
written: a reader over no markup would be a guess, and the order forbids
one. No address was admitted in this build. CHECKED ON DISK, not assumed:
every capture whose file name or links suggest a roster was read for route
shapes and member-link counts only. The school, groups and events captures
of 2026-09-20 draw 1, 0 and 0 member links -- none is a list of people --
and the company roots and a group's feed LINK to roster addresses
(`/company/<seg>/people`, `/groups/<num>/members`) without being them. That
shows LinkedIn draws those addresses; it does not show them served. One
detail for F.5: LinkedIn's own links to a Page's People tab carry the
company's SLUG, while `member_rosters.compose` spells the tab with the
numeric id, so the capture should load the numeric spelling and record
whether it is served or redirected. **THE FOUR ROSTER LINES ADMITTED
ON 2026-09-24 WERE ADMITTED BEFORE ANY CAPTURE SHOWED THEM SERVED**
(MEMBER-ROSTERS-AS-BOUNDED-READS, with the orchestrator's acceptance). They
stay; whether they should wait on a capture instead is a question below.

**THE CAPTURE SPECS FOR SESSION 2, restated for a names reader.** Each is
ONE page load through `BROWSER.goto`, composed from values supplied at fire
time, nothing typed, pressed or scrolled:

    spec  rows              address (composer)                         loads
    F.5   N 102, J 108      a Page's People tab                        1
                            member_rosters.compose("company_people", <id>)
    F.6   N 99, N 100,      a school's People tab                      1
          J 112             member_rosters.compose("school_people", <id>)
    F.7   N 165, N 177      a group's member list                      1
                            member_rosters.compose("group_members", <id>)
    F.8   N 188, N 189      an event's attendee list                   1, +1 if
                            member_rosters.compose("event_attendees",  the page
                            <id>), or where the event page draws it    draws it
                                                                       elsewhere
    F.2   N 161             a groups search (1 of D1's five searches)  1
    F.3   N 179             an events search (1 search)                1
    F.4   M C70             the group page's own search control        1

**WHAT EACH CAPTURE MUST ANSWER**, all of it read offline by SHAPE and COUNT
and never by value:

1. Served or redirected: the landed address against the one asked for.
2. The list: how many rows; the list's container; whether each row is one
   link holding the name link, as the search draws it, or not.
3. Per row: which element holds the NAME (a member link's own text?);
   whether a HEADLINE line is drawn and where; whether a DEGREE badge is
   drawn; whether a member link is absolute or relative, a slug or an urn.
4. Rows drawn with NO member link, and what they say ("LinkedIn Member" or
   otherwise) -- counted; none is ever resolved.
5. How further rows load -- a show-more control, a scroll, a page parameter
   -- counted, never pressed: a reader reads one page.
6. For the aggregate tabs (F.5, F.6): the insight blocks, their facet counts
   and their headings' vocabulary.
7. For a groups or events search (F.2, F.3): each result's title element and
   link, and whether the result is one link holding the title link.

Each capture is then reduced to a committed skeleton by a builder of the
kind `scripts/_build_people_search_skeleton.py` is, and the reader written
over it. Session 2 also has three new rows to FIRE -- `N 79`, `N 172` and
`N 194` are COVERED-UNFIRED -- one people search each with
`include_names=True`, which, with F.2 and F.3, is five searches: D1's whole
budget. The people searches for `N 84`, `N 87` and `N 94` can be those same
fires, since each returns the shape and the names at once.

### K.8 Gates

**ON THE BUILD COMMIT (`a734527`):**

- The census instruments: `census_completion --check` (every figure matches
  its pin), `check_read_addresses` (GREEN 101 of 101), `check_jobs_directions`
  (GREEN 109 of 109), `triage_read_gap_rows` (controls 1 and 3-9 OK, 77
  verdicts), `ruling_holds` (GREEN), `check_write_classes` (GREEN, 385
  lines), `check_exclusion_basis` (43 of 43, no structural problem),
  `pin_census_rows --check` (no drift), `measure_pointer_graph --check`
  (PASS, 65), and the three generators `--check` (the audit index at 257
  documents, the rulings index at 67 rulings, the blocker map).
- Lane G's people guards, the document guards and this lane's tests, one
  sharded run over 24 files: 3,332 passed, 1 skipped -- the whole-tree
  navigation complement, which runs only where `CI` is set.
- The AST duplicate-key check (K.6).
- `impact_gate --against 52b55b6`: 213 of 265 test files (80%), past its 45%
  line, so it WIDENED TO THE FULL SUITE, run locally and sharded: 10,967
  passed, 9 failed, 9 skipped, 1 xfailed, in 34m38s. **THE NINE REDS WERE MY
  OWN COMMIT, NOT THE CHANGE.** Seven are in
  `tests/test_stale_process_is_announced.py`, which compares the commit a
  process loaded with HEAD on disk; the suite had loaded the build commit,
  and my follow-up commit (`5c0594d`) landed while it ran, so every
  staleness-sensitive test saw a moved HEAD. The three files, re-run on a
  quiet tree: 81 passed. The lesson is procedural and is applied below:
  nothing is committed while a gate runs.

**ON THE REWORK (`ddfb133`)**, before it was committed: the names file,
72 passed and 1 xfailed (the declared limit); and the targeted set -- lane
G's people guards, the page-string and reader guards, the identity and
fixture guards, the census tests and the three stale-process files --
3,452 passed and 1 failed on the first pass: the identity guard read a
planted source string in the new test file -- a decorator written with its
module name -- as an email address. The plant now imports the decorator by
name; the names file and the identity guard re-run: 73 passed, 1 xfailed,
and the guard clean for the file. The full suite, the mutation check and
the census instruments on the final tree are K.11, run with nothing edited
or committed while they ran.

**NOT RUN, and why.** CI: nothing is pushed, by the order; it certifies at
merge. Nothing live: no browser session, no LinkedIn page, no Chrome profile
-- every browser here was a headless test browser with every request
aborted.

### K.9 The cold verification, and what it changed

One cold pass by a general-purpose child over `a734527`, briefed to find
what is wrong, read-only and offline; it exported the commit with
`git archive` so it tested the commit and not the working tree, and touched
the capture only through the lane's counts-only scripts, after reading them.
Its verdicts:

    1  the reader                FAIL, MEDIUM
    2  the tests                 CONCERN, MEDIUM
    3  the fixture and builder   content PASS; provenance CONCERN, LOW-MEDIUM
    4  server.py                 PASS, one CONCERN
    5  the census                PASS, one LOW
    6  other claims              four overclaims, two LOWs, one pointer gap
    7  the seven guard files     PASS, 914 of 914

**1. THE READER RETURNED WRONG ANSWERS WITH CLEAN DENOMINATORS, ON DRAWINGS
THE CAPTURE NEVER SHOWED -- AND THE DOCSTRING SAID IT COULD NOT.** On the
captured page it was right: ten of ten names and headlines, nothing outside
a record. But the verifier drew the fixture's page other ways, and:

    C  headline without its paragraph, one more line after the location
                                    -> the location as the headline
    D  the location drawn before the headline
                                    -> the location as the headline
    F  each title out of its paragraph, the list inside one, a banner beside
                                    -> the banner as every headline
    H  a mutual connection's link holding a link to the same member
                                    -> the mutual returned as a person
    REORDER  the list re-rendering between the link reads and the text reads
                                    -> one member's name on another's link
    G1/G2  a card hidden with display:none or the hidden attribute
                                    -> returned
    G3  clip-hidden text inside the name link
                                    -> welded to the name

Each came from one mechanism: the reader re-found its elements with
locators at every read, bounded nothing to the card, counted lines rather
than checking the captured shape, and tested no visibility. THE READER WAS
REWRITTEN in the commit that lands this section: every card pinned to an element handle before any
text is read; the title paragraph required to sit inside its own card; the
headline read only in the captured shape (first of three siblings, the other
two one link-free line each); a nested card, an invisible card or name link,
and a name link holding text in a nested element each refused and counted;
both links read again after the text, and a card whose links moved refused
(`changed_while_read`). Every drawing above is now a test in section 9 of the
test file, run on the new reader: C, F, H, G1-G3 and REORDER refused or
absent and counted, each name on its own link. D IS THE ONE LIMIT NO
STRUCTURE CAN CLOSE -- the two lines differ only by position and by
generated class hashes -- so it is DECLARED, in the reader's docstring and
as a strict xfail that fails the day it starts passing.

**2. THE TESTS HELD EACH MITIGATION BY SECTION, NOT EACH RULE.** Of the
verifier's seventeen planted defects, eight passed the committed names file,
and five passed all six guard files (852 tests): the title-is-its-own-member
check removed, the exactly-two-lines check removed, a name logged, a name
written to a file, and a module cache built with `dict()`. And lane G's
package-wide reader guard drives this reader to "clean" VACUOUSLY: its
planted page answers every href with the plant, which is no member link, so
the reader skips its one card before reading any text. Answered in section
10 of the test file: a root-logger capture over the planted success path, a
file-write spy around the reader, a container check that finds call-built
containers, subscript and augmented stores and caching decorators (with five
planted controls), an ALLOWLIST of the calls the reader may await on a page
or a handle (a hover, a wheel, a scroll and a key press refused), and the
write-tool reach made transitive through helpers. The generic guard's vacuous
"clean" is lane G's instrument and is reported, not changed here.

**3. THE FIXTURE.** Content PASS: only declared synthetic people and slugs.
But the builder kept a foreign host, a query after a bare host and short
free-form attribute values verbatim; now an href is rebuilt from its parts
(foreign host replaced, query and fragment always dropped) and a kept
attribute keeps only a value from its closed set, each replacement counted
and a test driving all three. And the fixed point proved a NORMAL FORM, not
provenance: deleting every photo figure, every badge or the hidden copy of a
name was still a fixed point. The builder now prints a STRUCTURE DIGEST --
tags and nesting only -- which it printed over the capture as
`hljfpfdmkfekafdh`, pinned in the test file with a structural hand edit as
its control. Writing the builder's test found one more defect of its own:
with a single result card, `list_of` took the card itself as the list and
emitted the whole document; it now takes a strict ancestor, and the fixture
rebuilt from the capture is byte-identical.

**4. `not_claimed` said "no result is ever named"** in the envelope that
names them. It now says so only without `include_names`.

**5. FIVE TRIAGE REASONS** still said the foundation was being built; each
now says it landed.

**6. OTHER.** The two overclaims (the reader's "never as a guess", the
fixture's "provenance") are restated as what is checked.
`result_cards_read` counted cards TRIED and is renamed
`result_cards_attempted`. An absent headline and an empty one are the same
empty string in a closed record; the tool's docstring now says so, and
`headline_unread` counts the first. Seven pointers -- six census cells and
the tool-surface pin's comment -- cited a section of this record that the build
commit (`a734527`) did not carry, and nor did the rework commit; this section
lands in the commit after the integration (K.10), and they resolve from
there on. And one INFORMATIONAL point for the orchestrator: by
handing a client names, this reader raises the practical exposure of the two
declared name-aimed write debts (`send_invitation`, `send_message`,
`tests/test_no_write_is_aimed_by_a_name.py`); each record carries the link,
so converting them to link-aimed targets is the natural next step, not
taken here.

**AND ONE FINDING ABOUT MY OWN SCRATCH INSTRUMENT.** The verifier declined to
run the structure script in its skeleton mode: it printed, beside each text
node's length and word count, a 24-bit unsalted hash of the text -- enough to
confirm a guessed name. Two such skeletons (two results) were printed into
this lane's session log on 2026-09-27, never into a tracked file or a
commit. The hash is removed from that script and from its sibling; neither
prints anything about a text but its shape now.

### K.10 Integration of master `ae24426`

Master had moved from `52b55b6` to `ae24426` by the end: lane G's residuals,
its model-id guard, and its preview-record work. Merged once, measured on
the merged tree, no delta added:

    conflict            scripts/ci_shard_timings.json -- master's table taken,
                        this lane's names file re-priced on the merged tree
                        (73 tests, 71.6 s alone and serially)
    merged cleanly      linkedin_server/server.py (master's instructions edit
                        sits three lines below this lane's sentence),
                        linkedin_server/people_data.py (this lane's
                        PEOPLE_TOOLS entry beside master's ABSENT), and this
                        record (both sides removed the same model-id line)

**ONE CHANGE THE MERGE REQUIRED, AND IT IS A BETTER ANSWER THAN MINE.**
Master's `people_data.ABSENT`: a headline the reader did not read is now
`null`, not the empty string, so "none drawn here" and "an empty one" are
different states in the record itself. The reader already handed `None` for
a headline it could not place, so its records carry ABSENT unchanged; three
tests now expect ABSENT where they expected `""`, and the tool's docstring,
which said a record could not tell the two apart, now says it can. That
closes the verifier's finding 6.8 in the record rather than only in prose.

**PINS, RE-DERIVED ON THE MERGED TREE:** `census_completion --check` --
every figure matches its pin (the merge moved no census figure);
`check_read_addresses` GREEN 101 of 101; `check_jobs_directions` GREEN 109 of
109; `pin_census_rows --check` no drift; `measure_pointer_graph --check` PASS,
65; triage, `ruling_holds`, `check_write_classes` (385) and
`check_exclusion_basis` (43 of 43) green; the tool surface 57 tools and 91
parameters. The AST duplicate-key check over the merged tree (4,044 dict
literals, 13 JSON files): every pinned dict clean, and the one duplicate is
still `tests/test_selectors_resolve.py`'s. The surface pin, the names file,
`test_people_data.py` and the one-page guard on the merged tree: 296
passed, 1 xfailed.

### K.11 The final gates

The full suite through the impact gate, the mutation check over the reader
as rewritten, and the census instruments, run on the commit that carries
this section (`f19e316`), in that order and never two at once -- the
mutation check rewrites the reader on disk, and the suite's staleness tests
compare the modules a process loaded with the disk -- with nothing edited or
committed while they ran:

- `impact_gate --against 52b55b6`: 59 changed paths select 246 of 266 test files (92%), past its
  45% line, so it WIDENED TO THE FULL
  SUITE, run locally and sharded: PASS, all 11,060 tests, in
  1,478.9 s (24m39s).
- The mutation check: fifteen defects planted in `people_results.py` one at
  a time, the names file run over each, the file restored after each and its
  bytes compared:

    headline read off the location line                 7 red
    a result nested in another is read                  1 red
    a hidden card is read                               0 red, then 1 (below)
    the title's paragraph not bounded to its result     1 red
    nested text in the name link read with the name     3 red
    the links not read again after the text             1 red
    each card re-found at its turn, not pinned first    4 red
    the line count not checked                          2 red
    the title's own-member check removed                1 red
    a failure quoted instead of counted by type         1 red
    each name logged                                    1 red
    each name written to a file                         1 red
    a module cache built by a call                      1 red
    a hover over every card                             5 red
    a wheel scroll before the read                      3 red

  FOURTEEN OF FIFTEEN ON THE FIRST RUN. The fifteenth -- the CARD's
  visibility check removed -- stayed green because the NAME LINK's own check
  refuses every display-based hiding: a display:none or hidden card hides
  its link too. The two differ on one drawing only, a card hidden by
  visibility:hidden whose name link sets visibility:visible, and that is
  now a test (with a control showing the link really is shown there); run
  over that mutant alone, it is 1 red. So fifteen of fifteen, and the
  reader restored and byte-compared after every one.

- The discriminating test's own commit, gated by the impact gate over its
  staged change: 52 files, 2,755 tests (the 25 corpus-wide guards among
  them), PASS -- and 214 of 266 files not run, said by the gate itself.
- The census instruments and the generators, on the final tree, each at
  the figures K.10 gives: every census figure at its pin, the address
  tables GREEN 101 of 101 and 109 of 109, the row pin without drift, the
  pointer graph PASS 65, triage, ruling holds, write classes (385) and the
  exclusion basis (43 of 43) green, and the three generators at their
  fixed point.

**NOT RUN, and why.** CI: nothing is pushed, by the order; it certifies at
merge. Nothing live: no browser session, no LinkedIn page, no Chrome profile.

**MASTER MOVED AGAIN WHILE THESE RAN**, to `b6993e5`: the live lane's
session-2 preparation. It was not merged -- the order integrates once, and
that was `ae24426` (K.10) -- but it was MEASURED against this branch: a
read-only three-way merge of this branch and that master (`merge-tree`)
finds no conflict. Two files overlap (`_audit/_census/messaging-and-content.md`
and `tests/reader_leak_baseline.json`), on different lines; master did not
touch `scripts/census_completion.py` since `ae24426`, so the census pins this
branch carries stay the merged tree's -- DERIVED, not measured on a merged
tree.

**THE SESSION-2 PLAN ALREADY FOLDS IN THIS RECORD'S CAPTURE SPECS**
(`_audit/2026-09-27-live-session-2-plan.md`): its five searches are `N 104`
and `N 161` (captures) and `N 94`, `N 84`, `N 87` (the shipped people
search), `N 179` deferred; it captures a group's member list (`N 165`,
`N 177`) and a Page's People tab (`N 102`, `J 108`), with the school tab and
an event's attendees conditional or later. It was written before
`include_names` existed. ONE RECOMMENDATION, AT NO COST: pass
`include_names=True` on the people searches it already fires -- same load,
same search -- so the names reader meets the live page; a keyword on one of
them fires `N 79` as well. `N 172` needs a member token, and so a sixth
search, and `N 194` a hashtag keyword: both wait on a later session.

### K.12 Questions for the orchestrator

1. **The four roster admissions.** They were made on 2026-09-24 under
   MEMBER-ROSTERS-AS-BOUNDED-READS and before any capture. The order of
   2026-09-27 admits no address a capture has not shown served. Keep them
   (the composers are unwired, so nothing can open them), or withdraw them
   until F.5-F.8 show them served? Either is one commit.
2. **`M C70`'s post.** The foundation still declares a person, a group and an
   event, and no post.
3. **`N 178`** still needs his decision to load a member's profile he names
   for a read, outside an outward act.
4. **The duplicate key** in `tests/test_selectors_resolve.py` (K.6), for
   whichever lane owns that file.
5. **The two name-aimed write debts.** `send_invitation` and `send_message`
   are aimed by a name (`tests/test_no_write_is_aimed_by_a_name.py` declares
   them as debt). The people search now hands a client names, each with its
   link, which raises their practical exposure: two results can share a
   name. Converting both to take the link is the natural next step, and a
   separate lane's.
6. **Lane G's reader guard is vacuous on this reader's success path**
   (K.9, finding 2): its planted page answers every href with the plant,
   which is no member link, so the reader skips its one card before reading
   any text. This lane's own file drives the success path; whether the
   generic guard should learn to plant a member link is lane G's to decide.

### K.13 The orchestrator's calls, and the integration of master `687b07c`

The orchestrator's order of 2026-09-27 23:36: integrate master `687b07c`,
then this branch merges next. Checked against disk first: this branch at
`996424e` and clean, master at `687b07c` with `b6993e5` inside it and lane
L5's named-person route on top. Disk agreed.

**THE CALLS ON K.12's QUESTIONS**, recorded as made:

1. The four roster admissions STAY: they are what lets session 2 capture
   those pages; the rows stay GAP until a capture and a reader exist.
2. `M C70`'s post record goes to lane G later, after a capture shows the
   fields. Nothing here.
3. `N 178` is the OPERATOR'S call: the read would reverse his own removal of
   the third-party profile pattern on 2026-09-04. It is put to him; nothing
   is built.
4. The duplicate key in `tests/test_selectors_resolve.py` is fixed on master
   (lane L5) -- and this merge's duplicate-key check finds none.
5. The name-aimed `send_invitation` and `send_message` debts go to lane L5
   next.
6. The reader guard's success-path gap goes to lane G.
7. `include_names=True` on session 2's people searches goes into the live
   lane's go order.

**THE MERGE.** Three conflicts, each resolved by measurement:

    tool-surface pin     both histories kept; the registry MEASURED at 59
                         tools and 96 parameters -- master's 59 and 95, and
                         this branch's `include_names`
    census pins          both histories kept, and four figures re-derived on
                         the merged tree
    shard timings        both sides' entries (this branch's names file,
                         lane L5's named-profile route and people seam), no
                         key changed on both sides; 187 files, 1,882.2 s,
                         re-derived (`_tests` is the first measurement's
                         5,736, which neither side moves)

**THE CENSUS PINS SHOWED THE HAZARD THIS REPOSITORY HAS NAMED BEFORE.** Each
side had moved `delivered_broad` and `unfired` by three from the same base --
this branch by `N 79`, `N 172`, `N 194`, lane L5 by `N 2`, `N 4`, `M M1` -- so
git saw the two sides' value lines as EQUAL and merged them as one, three
short; the conflicts were only in the comments. Measured on the merged tree:

    adjudicated        183   (this branch 182, master 180, base 179)
    delivered_broad    123   (both sides 120, base 117)
    gap                587   (this branch 588, master 590, base 591)
    unfired             44   (both sides 41, base 38)

Every other figure, and every bucket-1 hold, matched its pin on the merged
tree without a change.

`server.py`, both census slices and the reader-leak baseline -- each
changed on both sides since `ae24426` -- merged without a conflict, and
were read after the merge rather than trusted: the instructions still name
the four people tools that `PEOPLE_TOOLS` holds (`people_data.py` is this
branch's change alone; master did not touch it), and the network slice
holds lane L5's `N 2` and `N 4` and this branch's three rows, each once.
The reader, its fixture and its test file are byte-identical to `996424e`.
The derived views were already at their fixed point (the audit index at 258
documents, the register at 67 rulings, the blocker map), every register
entry kept. The AST duplicate-key check over the merged tree: 4,242 dict
literals and 13 JSON files, 0 duplicates. The census instruments: all green
(the address tables 101 of 101 and 109 of 109, the pointer graph at master's
64, the exclusion basis at master's 42).

**A DISCLOSURE, BECAUSE THE ORDER'S WARNING APPLIES BACKWARDS.** Two test
files in this suite (`tests/test_apply_modal_fixture.py`,
`tests/test_verification_that_could_not_read.py`) send a headless Chromium to
www.linkedin.com -- no cookies, no profile, no port 9224. This lane's two
WHOLE-SUITE runs on 2026-09-27 (K.8's on the build commit, K.11's on the
record commit) ran before the order named that, without lane L5's offline
plugin, so those tests made their requests in both. No targeted gate of this
lane ever included either file. Every run from here uses the plugin.

**THE GATES, ON THE MERGE COMMIT `e15e507`** -- this branch's own, which
until this branch merges resolves here and nowhere on `master` -- in this
order and never two at once, with nothing edited or committed while they
ran. Every pytest run loaded lane L5's offline plugin (`-p np_offline`, its
directory on `PYTHONPATH`, its log named by `NP_OFFLINE_LOG`):

- The readers under lane G's guards and lane L5's people seam: 2,363
  passed, 1 xfailed (the declared `KNOWN_LIMIT`, strict), in 121.1 s. The
  plugin aborted nothing there; none of those files opens a page off the
  box.
- `impact_gate --against 687b07c`: 17 changed paths select 222 of 272 test
  files (82%), past its 45% line, so it WIDENED TO THE FULL SUITE, run
  locally and sharded: PASS, 11,490 tests by pytest's own count (the gate
  prints one sum), in 1,145.2 s (19m05s).
- THE PLUGIN'S LOG, read after that run: 11 requests aborted, every one to
  https://www.linkedin.com, one from each of the 11 tests the order named --
  7 in `tests/test_apply_modal_fixture.py`, 4 in
  `tests/test_verification_that_could_not_read.py` -- and none from any
  other test. Those 11 passed with their navigations aborted. What the
  plugin cannot see, a request made outside Playwright, it does not claim,
  and neither does this record.
- The census instruments and the three generators: every census figure at
  its pin (the four above among them); the address tables GREEN 101 of 101
  and 109 of 109; the row pin without drift; the pointer graph PASS, 64 of
  64; both triage scripts green; the holds green; write classes GREEN, 385
  lines; the exclusion basis 42 of 42; and the generators at their fixed
  point -- the audit index at 258 documents, the register at 67 rulings,
  the blocker map deriving today's GAP as 587.

**NOT RUN, and why.** CI: nothing is pushed, by the order; it certifies at
merge, on three platforms where this gate ran on one. Nothing live: no
browser session against LinkedIn, no Chrome profile, no port 9224. The
mutation check and the cold verification were not re-run: the reader, its
fixture and its test file are the bytes they ran over. The observed read
map the impact gate consults was recorded at `5c910e4`, not at this commit,
as the gate itself prints; the run widened to the full suite, so no
selection here rests on it.

## The offline frontier 2026-09-28

The orchestrator's order of 2026-09-28 01:30: the still-GAP rows bucket 3
calls BLOCKED ON NOTHING -- the address admitted, no ruling on the page, no
press refused -- were five, measured at 01:25: `M M53`, `N 195`, `P K1`,
`P S5` (read direction) and one jobs row. For each, build a reader where a
capture on disk shows the field the row wants and move the row to
COVERED-UNFIRED; where none does, build nothing and write the capture spec
here for session 2's plan. Say for each why it was still unbuilt, from its
cell and from disk, before deciding.

### L.1 Step 0, checked against disk before it was obeyed

Master at `64afa6c`, holding this branch's last commit and lane G's network
guard -- `tests/network_guard.py`, registered by `tests/conftest.py`'s
`pytest_plugins`, so no test reaches the network and lane L5's plugin is no
longer needed. This branch fast-forwarded to it. `census_completion` named
the same four read rows as BLOCKED ON NOTHING, 4 of 101, and
`check_jobs_directions` one jobs row, `J 107`. Disk agreed.

### L.2 Why each was still unbuilt, and the verdict

**`M M53` -- the composer's presence. VERDICT (a), BUILT.** Gated READER
since lane Y2's completeness pass (2026-09-24), blocker
PARSER-ON-A-LOADED-PAGE: `linkedin_compose_fields` already loads the page.
Why it waited: the cell's own design -- key the status to a caller-supplied
thread and publish no name -- was written before NAMES-AT-RUNTIME, when a
people read could not return names; the ruling came on 2026-09-24 and the
people-record foundation it needs landed on 2026-09-27 (lane G). The
capture (`_state/cap-ct-compose.html`, 2026-09-20) draws seventeen
suggestion cards, sixteen of them people, each with a status line.

**`N 195` -- Premium's recruiter insights. VERDICT (a), BUILT.** Gated
READER since the same pass, blocker PREMIUM-READER-NOT-BUILT, and lane Y2's
integration decided WHO-WHICH-COUNTS-ARE-NOT-DELIVERY does not hold it: the
page names no member. Why it waited: its only capture is the live lane's
(session 1, 2026-09-23), gitignored in that lane's worktree, and no lane had
read it for structure; its viewers are people, and a record channel for
them landed on 2026-09-27.

**`P S5` -- the two engagement cards. VERDICT (a), BUILT.** Gated READER
since the same pass, blocker PARSER-ON-A-LOADED-PAGE, with the cell's
condition that the employer the first card names is not published. Why it
waited: that condition wants the sentence reduced INSIDE the page, which is
a script, and a script outside `dom.py` is refused by `tests/test_readonly.py`
-- this lane's first draft met exactly that refusal; nobody had put the read
into the shipped reader's own script. The capture
(`_state/cap-search-appearances.html`, 2026-09-20) draws both cards.

**`J 107` -- see all jobs at one employer. VERDICT (a), BUILT.** Gated
READER since lane D (2026-09-24), which measured that the shipped route
returns only the postings matching a keyword and named the build: let
`company_id` stand in for the keyword in `linkedin_search_jobs`' guard. Why
it waited: the build was in `server.py`, which lane D did not own, and nobody
took it. No capture is needed: the page is the search results page the
shipped reader already reads, and the change is to the guard, not the
reading.

**`P K1` -- the Verifications section. VERDICT (b), NOT BUILT.** Gated
READER since lane R's merge (2026-09-24), on the cell's words that the
section sits on the admitted own profile. Nothing on disk shows it. The three
captures of his own profile (the live lane, 2026-09-23) draw a verification
BADGE on his name -- an icon whose label names his verifications -- and no
section; the settings index (same session) draws Verifications only as a
link to `/mypreferences/d/verifications/`, which the boundary refuses; the
Premium hub (2026-09-20) links `/trust/verification/`, also refused. ALLOWED
IS NOT SERVED: the row was never blocked on nothing. The address table
re-gates it MEASURE, and the capture spec is L.4.

### L.3 What was built

- **`J 107`.** `linkedin_search_jobs` admits a keyword-less call exactly
  when `company_id` is given, and that call's url carries no `keywords` key:
  `/jobs/search/?f_C=<id>`, the address lane D measured the boundary
  admitting. Every other call builds the url it always built.
  `tests/test_a_company_search_needs_no_keyword.py`: the employer-only url,
  the refusal of a call with neither (the control), the slug refusal, the
  keyworded url.
- **`P S5`.** The shipped reader's own script, `dom.SEARCH_APPEARANCES_JS`,
  now also reduces the two engagement cards -- an integer, a section word
  compared against a closed list passed in, a boolean -- and
  `dom.read_search_appearances` returns them as `engagement`, which
  `linkedin_search_appearances` carries off the same load. No new waiver
  and no new script. The employer never leaves the page: the pattern stops
  at the word before it. `tests/test_profile_engagement_cards.py`.
- **`N 195`.** `linkedin_recruiter_insights()` and
  `recruiter_views.read_recruiter_views`, reading with Playwright's own
  find-and-read calls and no script: the two counts under keys the module
  declares, the time range in days, each chart's points (a date and a
  count -- the trend itself), and each recruiter viewer as a people record
  named by LinkedIn's "Recruiter at <employer>" line, the industry its
  headline, no link, anonymous -- the way `linkedin_who_viewed_me` returns a
  viewer drawn that way. The employer's Page link is never returned.
  `tests/test_recruiter_insights.py`.
- **`M M53`.** `linkedin_messaging_presence()` and
  `presence.read_suggested_presence`: each card pinned as an element handle
  before anything is read from it, so a name, a headline and a presence come
  from one card; each person a record (name, headline, no link) beside a
  presence word from a closed three; a group conversation and a hidden card
  counted and skipped. `tests/test_messaging_presence.py`.

THE SIX MITIGATIONS, for the two people reads, each with a test that can
fail: declared fields only (the row's keys and the record's shape, exactly);
sanitised and marked untrusted (a name laced with a zero-width space and a
direction override comes back clean, with a control showing the lace reached
the page); never stored (no module-level state, no file opened, nothing
logged); one page per call and nothing but finding and reading (one
navigation, and an allowlist of read calls with a planted hover or scroll
refused); visible only (a hidden row and a row inside an `aria-hidden`
container counted, and nothing of it returned -- the presence reader reads
nothing of a hidden card, and the recruiter reader reads a hidden link's
address and text only to decide whether it is a viewer row, which the cold
review found this line overstating, L.6 F16); never a target (no link in any
record, and no write tool reaches either reader through any helper).

THE FIXTURES are skeletons of their captures, built by
`scripts/_build_capture_skeleton.py`, one plan per page: the structure kept,
every word a member wrote replaced from the declared synthetic tables, the
company ids the identity guard's declared ones, and a structure digest
printed from the capture and pinned in each test file -- since the cold
review (L.6 F13) over the attributes the readers select on as well as the
tags, each digest with a control that moves it by one attribute. It prints
counts only. What no rule named was written as a placeholder and counted: none on
the engagement cards or the suggestions, and on the recruiter page four text
nodes (the charts' axis sentences) and six labels (the section's, the time
filter's, and the two viewers' icon and image labels).

THE GUARDS THIS MET, each answered in the same change: the evaluate waiver
rule (the first draft ran its own scripts from new modules, and the rule
refused it; the S5 read moved into the shipped script and the two people
readers dropped scripts altogether); the tool surface, 61 tools and 96
parameters on this branch, pinned with the census decision -- 60 and 93
once master's retirement of `linkedin_send_message` came in (L.7); the
server surface, 61 tools and 43 that do not write (60 and 43 after the
merge), at every count site, in the server docstring and in the README's
module map; `known_side_effects`' messaging clause and its
README copy, which now name `linkedin_messaging_presence` among the tools
that load a messaging address and open no conversation; `PEOPLE_TOOLS` and
the instructions sentence; the source-url declarations (both SHAPED, as
`linkedin_search_appearances` is); and the identity guard, which caught an
undeclared company id in the first recruiter fixture.

THE LEAK HARNESS DRIVES BOTH PEOPLE READERS AS THEY SHIP -- which the
first build could not say. That build's readers pinned element handles the
planted page's element stand-in cannot answer, and the baseline recorded
`presence:read_suggested_presence` and `recruiter_views:read_recruiter_views`
"not_driven:raises RuntimeError", beside four recruiter helpers the guard
discovered as readers of their own. After the cold review each reader asks
the page once per named query and reads the handles it is handed, so the
guard discovers one recruiter reader where it found five; on its signature
drive each reads, reaches its record builder and builds none -- NO_RECORD.
Master's guard, since lane G's triage of 2026-09-28, lets no reader rest
there silently: it is driven from a tracked fixture, or it says what would
drive it. Both have a tracked fixture, so both got a drive in
`tests/shipped_drives.py` at the merge (L.7): the planted page answered with
the skeleton's structure -- which element each named query finds -- and the
one drawn string each success path keys on (a person card's presence line;
the first chart's metric label and a viewer row's "Viewed 2w ago"), and the
plant everywhere else. Each comes back `returns_records`, the plant inside
one people record and nowhere else, having read the page (1 and 4 entry
reads) with nothing failed; each raises, not driven, on a copy of its
fixture with that drawn string reworded. The regenerated baseline differs
from master's by those two lines only. Their files drive the rest with
plants: laced names, a planted status word, a planted actor and section, a
planted point label, a planted photo label and a failing page, each shown to
reach the page and never the output.

THE ENGAGEMENT CARDS SIT UNDER VERDICTS THAT WERE ALREADY `returns_text`
(the cold review's F10): `dom:read_search_appearances` and
`linkedin_search_appearances` were recorded so before this lane, so neither
harness can go red on a new leak through `engagement`. What guards it is
`tests/test_profile_engagement_cards.py`'s own: a PageString drive of the
reduction, and a hunt for the employer over the reading and the envelope.

THE PLANTED MUTATIONS, one defect at a time, the named test file run over
each, the source restored after each and its bytes compared -- run on the
merged tree, `87e5250`, since the readers' restructure and master's merge
both moved the code under them (at the build they were 5, 7, 10 and 8
mutants; the cold review's fixes added the rest):

    J 107   7 of 7 red    the old guard; no guard; a blank employer counted
                          as one; an empty keywords key kept; a keyworded url
                          losing its keyword; a digit that is no Page id
                          accepted; a None keyword echoed raw
    P S5    9 of 9 red    the employer captured beside the number; the
                          number crossing as text; the comma kept; every
                          actor "someone"; a hidden card read; a page value
                          taken uncoerced; the page's section word returned;
                          a drawn card not counted; a multi-word section
                          dropping the card
    N 195  21 of 21 red   a hidden viewer read; the View-insights twin read
                          as a viewer; the page's label as the key; a viewer
                          not anonymous; the raw line as the name; the comma
                          kept; the chart's card not its parent; a chart kept
                          to its first point; a module-level cache; two
                          loads; a query dropping the row; the spelled-out
                          time not a viewer row; a time in other digits
                          leaving; a chart naming no metric not counted; the
                          signed-out wall not refused; one failing region
                          stopping the other charts; one failing link
                          stopping the other viewers; a failure counted by
                          its message; the page-level failure carrying the
                          exception's message; the range taking a bare
                          number; the range taking any number the filter
                          draws
    M M53  14 of 14 red   a hidden card read; a group read as a person; the
                          page's presence word returned; the status line
                          captured whole; the raw line as the name; the
                          photo's label as the name; a module-level cache;
                          two loads; only the cards read counted; the
                          signed-out wall not refused; one failing card
                          stopping the others; a failure counted by its
                          message; the page-level failure carrying the
                          exception's message; a status word outside the
                          three kept

TWO SURVIVED A FIRST RUN, AND EACH WAS ANSWERED BY THE TEST THAT WAS
MISSING, never by weakening the mutant. `P S5`'s section word, at the build:
the script already nulls an unknown word, so the Python check was untested,
and a test now drives that step directly. `N 195`'s range taking a bare
number, on the merged tree: no test drew a filter of another shape, and one
now draws "Past 2 weeks" and "90" and reads null -- after which that mutant,
and a wider one taking any number the filter draws, are red.

### L.4 CAPTURE SPEC, `P K1`

For session 2's plan, one load:

    address   https://www.linkedin.com/in/me/  (admitted; lands on his own
              profile)
    loads     1 -- no press, no scroll beyond what the page draws on load
    keep      the page content, gitignored, as session 1's captures are

It must answer, from the capture's structure and never its text:

1. Is a verifications SECTION drawn anywhere on the profile -- a heading and
   items -- or only the badge on his name?
2. If only the badge: is it a link, and to which address shape
   (`/mypreferences/d/verifications/` and `/trust/verification/` are both
   refused by the boundary today), or a control that opens an in-page
   dialog?
3. What each verification draws -- its kind, who verified it, when -- by
   shape: the fields a reader would return.

If 1 is no and 2 is a dialog, the row is gated by a PRESS, and the next
question is whether the press gate permits opening that badge; if 2 is a
link to a refused address, the row needs an admission. Neither is blocked on
nothing.

### L.5 The census

Four rows GAP -> COVERED-UNFIRED, each cell opening on a dated paragraph
naming the tool, the reader and the test file, with the earlier text kept
after it: `M M53`, `N 195`, `P S5`, `J 107`. `P K1` stays GAP, its cell
opening on why, and its address-table line re-gated READER -> MEASURE. The
three read rows left `_audit/_census/read-addresses.tsv` and `J 107` left
`_audit/_census/jobs-directions.tsv`; `P S5` and `N 195` left the read-gap
triage, recorded beside the rows that left before them.
`tests/test_the_offline_frontier_rows.py` holds all five to this.

PINS, re-derived on the branch's tree at the build and never summed --
thirteen census figures moved, and `PINNED_B1_ROWS` gains the four rows
under no ruling. The same thirteen were re-derived again on the merged tree
over master `0867bda`, from master's values (L.7).

    adjudicated                183 -> 187     gap                  587 -> 583
    delivered_broad            123 -> 127     gap_read             101 -> 98
    unfired                     44 -> 48      gap_unknown          109 -> 108
    b1_no_ruling                26 -> 30      jobs_gap             109 -> 108
    b3_admitted                 46 -> 43      jobs_dir_r            41 -> 40
    b3_blocked_on_nothing        4 -> 0       jobs_admitted         13 -> 12
    jobs_blocked_on_nothing      1 -> 0

BUCKET 3 NOW HOLDS NO ROW BLOCKED ON NOTHING, read or jobs. The address
tables GREEN 98 of 98 and 108 of 108. The tool surface 61 tools and 96
parameters, measured off the registry (60 and 93 after the merge). The AST
duplicate-key check -- every dict literal in `linkedin_server/`, `scripts/`
and `tests/`, and every JSON file in `tests/` and `scripts/`: 4,311 dict
literals and 13 JSON files, 0 duplicates.

### L.6 The cold review, and what it changed

A cold verifier read the build read-only -- the two commits from `64afa6c`
-- and returned sixteen findings: no blocker, one major, six minor, nine
notes. Twelve were answered in code and tests, one was settled by
measurement, one is recorded, one is declined with its reason, and one is
not done.

- **F2, MAJOR (`M M53`).** A signed-out load came back ok with nobody
  suggested: the login wall draws no suggestion card. Both people tools now
  refuse the wall before reading (`assert_not_authwall`), each with a test
  that lands on it.
- **F1 (`J 107`).** The company verdict took `isdigit`, which admits a
  superscript two, circled and fullwidth digits, and "0". It takes ASCII
  digits that are not all zeros.
- **F12 (`J 107`).** A `None` keyword spent a load and then raised at the
  echo; it is echoed as an empty string.
- **F8 (`J 107`), DECLINED.** `keywords` stays required. A default of `""`
  was tried, and the tool-envelope guard stopped driving
  `linkedin_search_jobs` -- it builds only required arguments -- so the
  schema nicety would have cost a guard. The docstring says to pass an empty
  keywords.
- **F3, F15, F11 (`N 195`).** A viewer link is matched on its path, so a
  query or a fragment LinkedIn adds no longer drops the row; both time
  notations ("2w" and "2 weeks") are viewer rows; a time leaves only in this
  package's spelling with ASCII digits.
- **F4 (all three).** Seen beside read, everywhere a row could be drawn in a
  shape the reader does not know: chart regions, insights links and viewer
  rows; cards drawn beside cards read; a multi-word section counted
  unrecognised, not dropped.
- **F9 (`P S5`).** The click card's `anonymous` became `actor`, "someone"
  or "other" -- never a claim about a named member.
- **F7 (both).** The readers raise `ExtractionFailedError`, the type only,
  with the dom readers' landing describer, under the WITHHELD ruling; the
  error-url register moved 20 -> 22 sites on the branch.
- **F16 (`N 195`).** "A hidden row is counted and not read" was stronger
  than the code, which reads a hidden link's address and text to decide
  whether it is a viewer row. The docstring and L.3 say "counted, and
  nothing of it returned" now.
- **F13 (fixtures).** The structure digest covers the attributes the readers
  select on; three digests re-pinned, each with an attribute control.
- **F5 (`M M53`).** The synthetic-people fixture guard gains the composer
  card's two person slots, each with a planted control, and declares the
  one invented group title the fixture draws.
- **F6 (`N 195`), SETTLED BY MEASUREMENT.** The dates are the UTC date of
  each point's epoch, and the capture says that is the date the chart
  means: all 26 of its points sit at UTC midnight, each a Thursday.
- **F10 (`P S5`), RECORDED** in L.3, under the leak harness.
- **F14 (tests), NOT DONE.** The fixture tests launch a Chromium per read --
  143.6 s, 119.2 s and 47.9 s for the three files, measured under load. A
  module-scoped browser would cut that; it is a change to
  `tests/xhtml_page.py` left for a pass on gate cost.

AND ONE CHANGE NO FINDING ASKED FOR: each people reader asks the page once
per named query and hands the elements to its steps, and one element that
cannot be read is counted by its exception's type -- never its message --
while the rest are read (`charts_failed`, `links_failed`, `cards_failed`).
That made them drivable as they ship (L.3), and a bad card no longer costs
the whole reading.

THE COMMITS, each on this lane's branch and nowhere on `master` until the
branch merges: `b862f40` J 107's guard; `d3bad01` the three readers and the
census; `3d5267b` the five guards the full suite named; `77885a9` the cold
review's fixes; `1a3fab9` one page entry per reader -- and, nowhere on
`master` either, `87e5250`, the merge of master `0867bda`, and `c40fba9`,
the CDP port guard (L.8), which is nowhere on `master` until then too.

### L.7 The integration of master `0867bda`

Master had moved from `64afa6c`: lane L5 retired `linkedin_send_message` --
no write is aimed by a name -- and re-aimed `linkedin_send_invitation` by a
profile link; lane G triaged the 22 readers its guard could not drive,
drove six from tracked fixtures, and made every other one say what would
drive it. Merged once, at the end. Nine files conflicted, each a count or a
sentence both sides had moved, and each was measured rather than chosen:

- THE SURFACE: 60 tools -- 43 read, 17 write -- and 93 parameters, off
  `mcp.list_tools()` on the merged tree (61, 43, 18 and 96 on this branch;
  58, 41, 17 and 93 on master). The server docstring's headline and split,
  the README headline and module map, both surface pins and the non-write
  split say so, each keeping both histories beside it.
- `known_side_effects`' messaging clause and its README copy: L5's text,
  without the retired tool, with `linkedin_messaging_presence` kept.
- THE ERROR-URL REGISTER: WITHHELD 13, asked-for 7, passthrough 1 -- 21
  sites -- and no address in scope 10 (master 11 and 19).
- THE TRIAGE SPLIT: the messaging slice's GAP rows 131 -- R 16, W 111,
  R+W 4 -- master's 132 less `M M53`.
- THE READER BASELINE, regenerated by its writer after the two drives
  landed (L.3): it differs from master's by this lane's two readers only,
  both `returns_records`.
- THE CENSUS PINS, re-derived on the merged tree, never summed -- the
  thirteen this lane moves, from master's values:

      adjudicated                182 -> 186     gap                  588 -> 584
      delivered_broad            124 -> 128     gap_read             101 -> 98
      unfired                     45 -> 49      gap_unknown          109 -> 108
      b1_no_ruling                26 -> 30      jobs_gap             109 -> 108
      b3_admitted                 46 -> 43      jobs_dir_r            41 -> 40
      b3_blocked_on_nothing        4 -> 0       jobs_admitted         13 -> 12
      jobs_blocked_on_nothing      1 -> 0

  and `PINNED_B1_ROWS`' NO_RULING gains `J 107`, `M M53`, `N 195` and
  `P S5`. Four of the thirteen read differently on the branch -- 187, 127,
  583 and 48 -- because master had moved `M M2` back to GAP and `N 155` to
  COVERED-UNFIRED; all four conflicted, and each was measured.
  `census_completion --check`: every headline figure matches its pin.
- THE BLOCKER MAP regenerated to its fixed point: `J 107`'s state today,
  and three candidate counts the merged corpus moved.

### L.8 Found while gating: the suite reached the CDP port

The brief says never port 9224. A reading of the tool-envelope harness while
gating found that the suite does not keep that: it drives every tool on a
planted page, `linkedin_cdp_status` among them, and that tool's
`cdp_bridge.probe()` opens `http://127.0.0.1:9224/json/version` with
`urllib`. `tests/network_guard.py` covers what a test's browser requests and
says it leaves out a request made outside a browser -- adding that no test
makes one -- and it admits loopback by design, so nothing refused this one.

MEASURED, NOT INFERRED, and without touching the port: a recording plugin
that refuses any connection to the CDP port before it is attempted, shown
first refusing the shipped probe, then run over
`tests/test_tool_envelopes_emit_no_page_string.py` -- one connection per
run, from that module's `verdicts` fixture. Nothing listened on 9224 when
that was measured (the OS listen table). Whether anything listened while
this lane's earlier gates ran that file is not known, and each did; while a
live session is attached, the operator's Chrome answers such a probe.

FIXED IN TWO PLACES, in its own commit, separable from the frontier:

- AT ITS SOURCE: the envelope harness's `drive_tool` stubs the probe,
  answering as a closed port does -- which also covers the harness's
  standalone runs, where no pytest plugin applies.
- FOR THE NEXT ONE: `tests/cdp_port_guard.py`, registered by
  `tests/conftest.py` beside the network guard, refuses every connection a
  test makes to the configured CDP port -- `ConnectionRefusedError`, what a
  closed port answers -- and fails that test by name.
  `tests/test_no_test_reaches_the_cdp_port.py` shows it refusing the shipped
  probe, leaving another port alone, failing a planted test loudly in its
  own process (pointed at a port nothing listens on), and the harness
  reaching the port no more.

FIVE PLANTED DEFECTS, each red and each restored byte-identical, run with
the configured CDP port moved to an ephemeral loopback port nothing listened
on, so no mutant could reach 9224: the harness's stub removed (the envelope
module errors at its fixture, REACHED FOR THE CDP PORT, and the harness test
fails); the guard never refusing a `connect`; nor a `connect_ex`; a refusal
never failing its test; the guard refusing every port.

`tests/network_guard.py`'s sentence that no test makes a request outside a
browser is left as lane G wrote it, for lane G: this lane did not edit that
file.

### L.9 Gates

On `d78b143` -- the final tree before this section, on this branch and
nowhere on `master` until it merges -- with nothing edited or committed
while they ran; master was still `0867bda` at the end, so the merge of L.7
is the one integration:

- THE IMPACT GATE against master: 48 changed paths, 259 test files selected
  and 26 corpus-wide; it WIDENED TO THE WHOLE SUITE because
  `tests/conftest.py` changed (L.8), which it has no model of. PASS over
  11,622 tests in 1,301.5 s, sharded (`-n auto --dist loadfile`), 0 failed.
  The gate prints the total only, on a pass. The CDP port guard was armed
  in every worker, and no test reached the port -- a test that had would
  have failed by name.
- THE CENSUS INSTRUMENTS, thirteen, every exit 0: `census_completion
  --check`, every headline figure matches its pin; `check_read_addresses`
  GREEN 98 of 98; `check_jobs_directions` GREEN 108 of 108;
  `pin_census_rows`, no drift; `measure_pointer_graph`, 0 pointers added;
  both triage scripts; `ruling_holds` GREEN; `check_write_classes` GREEN,
  386 lines; `check_exclusion_basis`, 42 of 42, 0 untraced.
- THE THREE DERIVED --checks, among those thirteen: `_audit/INDEX.md`
  matches the corpus (258 documents), `_audit/RULINGS.md` matches (67
  rulings), and the blocker map is the derived map, every column of every
  line.
- THE AST DUPLICATE-KEY CHECK: 4,337 dict literals and 13 JSON files, 0
  duplicates.
- THE PLANTED MUTATIONS on the merged tree (L.3, L.8): 51 of 51 red over
  the four rows and 5 of 5 over the CDP port guard, every source restored
  byte-identical.

This section's own commit changes only this document; it gets the impact
gate for that path, and nothing else.

### L.10 What was not run

- NOTHING LIVE. `M M53`, `N 195`, `P S5` and `J 107` are COVERED-UNFIRED:
  no page was loaded on LinkedIn. Whether LinkedIn's default location
  narrows a keyword-less employer search stays unverified. **ANSWERED THE
  SAME DAY BY THE LIVE LANE'S SESSION 3: IT DOES** -- M.5 below.
- `P K1`'s CAPTURE: the spec is L.4, for session 2's plan.
- CI: nothing is pushed, so the suite ran on this Windows box only; the
  Linux and macOS cells did not run.
- THE COLD REVIEW'S F14: the fixture tests still launch a Chromium per read.
- A SECOND COLD REVIEW of what changed after the first -- the restructure,
  the drives, the merge and the CDP port guard -- was not run.

## Four people-search items 2026-09-28

The orchestrator's order of 2026-09-28 15:10: four small items, all in this
lane's people-search code, offline. (1) `N 30` to COVERED-UNFIRED by
D6-CAPABILITY-OVER-AFFORDANCE, his ruling, as `N 4`'s was -- its fire needs a
member he names, and its R2 stays recorded as incidental capture. (2) `N 31`,
blocked on nothing: add LinkedIn's `network` facet to the people search
exactly as the capture writes it, values from tool arguments only, the member
named, results as people records under the six mitigations, a test that can
fail and a planted mutation; then COVERED-UNFIRED. (3) `N 85`'s `connectionOf`
spelling from DERIVED to MEASURED, citing the capture, and the pointer
instrument that pins that cell re-pinned. (4) `J 107`, proven in session 3:
`linkedin_search_jobs`' docstring to say that for every posting at an
employer the caller passes location "Worldwide", pinned by a test.

### M.1 Step 0, checked against disk before it was obeyed

At 15:08 the local `master` stood at `854f9ea`, the remote at `a9cb2e3`, and
this branch's last head, `ff42daa`, was an ancestor of `854f9ea` -- the
offline frontier was in. No CI run existed for `854f9ea` at 15:09; one
started at 15:10 and finished green -- 20 of 20 jobs, queried by the full
SHA, never by `--limit 1` -- before anything here was built on it. The
branch then fast-forwarded to it. Disk agreed with the order: `N 30` and
`N 31` GAP with lane L5's cells; the capture's three topcard links (link 1
`origin`, `connectionOf`, `network`; links 2 and 3 `origin`, `network`,
`connectionOf`); `N 85` reading DERIVED; `J 107` COVERED-PROVEN with its note
that the docstring should say so.

### M.2 `N 30`: COVERED-UNFIRED by D6, as he decided

No code moved for it. `linkedin_people_search_shape(connections_of=<member
token>, include_names=True)` already composes the `connectionOf` link 1
writes and returns the member's connections as people records -- the route
`N 172` is COVERED-UNFIRED on. The cell opens on that paragraph, says the
fire needs a member he names (a token he chooses, never one taken from a
page), keeps R2 recorded as incidental capture in lane L5's words, and keeps
L5's paragraph after it. Link 1's two-value `network` narrows nothing for a
first-degree member, and the tool can send it now (M.3).

### M.3 `N 31`: the `network` facet, as the capture writes it

`people_search.FACETS` gains `("network", "network", NETWORK_DEGREE, 2)`,
BEFORE `connectionOf`, and the tool gains `network` (one parameter, no tool).
Everything about it was taken from the capture and lane L5's measurement of
it, and nothing else:

- THE KEYS AND THEIR ORDER: `network` then `connectionOf`, as links 2 and 3
  (the shared-connections links) write them; `origin` is never sent, as for
  every facet here.
- THE VALUE: a percent-encoded JSON list, `network` = `%5B%22F%22%5D` --
  13 characters, 3 of them letters, the shape L5 measured on links 2 and 3 --
  beside `connectionOf`'s percent-encoded list of one member id, the grammar
  `people_search.compose` already sent.
- THE VOCABULARY: LinkedIn's two captured letters, `F` (his first degree) and
  `S` (his second), in the order link 1 lists them whatever order the caller
  writes. A third degree is on record nowhere here, so it is refused, not
  guessed; so are a lower-case letter and a word. At most two, a repeat
  refused rather than dropped.
- THE MEMBER: `network` without `connections_of` is refused before any
  session opens (`network_needs_a_named_member`), so the member is always
  one the caller named -- the order's condition.
- THE PEOPLE: the search's results come back through
  `people_results.read_result_people` when the caller passes
  `include_names=True`, the reader `tests/test_people_search_names.py` holds
  to the six PEOPLE-DATA-MITIGATIONS; driven here over the same captured
  results skeleton, with the facet, it returns three records of exactly the
  declared shape, one page, and nothing about anybody outside them.

**A FINDING, PUT TO THE ORCHESTRATOR RATHER THAN BUILT.** LinkedIn writes
`network` ALONE, once, in the tracked captures: the connections-page capture,
`tests/fixtures/live2/n23.html`, draws a link to `/search/results/people/`
with `network` and `origin` and no member -- a search of his own network by
degree, which is `N 81`'s question ("Filter a people search by Degree of
connections", GAP). The order made a named member the facet's condition, so
this build refuses `network` alone; lifting that condition, on a D1 facet
LinkedIn writes, is what would deliver `N 81`. The composer's docstring says
so. Its first draft said LinkedIn writes the facet only beside a member; the
captures said otherwise before anything was committed, and that sentence
never shipped. **THAT LAST CLAUSE WAS NOT SO, FOUND AT N.1 BELOW:** the same
sentence did ship, in `tests/test_shared_connections_search.py`'s module
docstring (`a7f954f`), and was replaced there with the `N 81` build. **AND THE
FINDING WAS RULED THE SAME DAY (17:02): YES** -- N.2.

`tests/test_shared_connections_search.py`: the capture still draws the three
links (a premise check); the composed keys in the capture's order, with a
control that the other order is convicted; the value in L5's shape, with a
control that the raw spelling is not it; both degrees in link 1's order;
eight refusals; the member rule at the composer and at the tool, with zero
sessions; the boundary admitting all three degree sets; the people records;
a dropped facet reading `absent` and link 1's raw spelling `same_values`; and
the census cells. EIGHT PLANTED DEFECTS, each red, each source restored
byte-identical: `network` written after `connectionOf` (2 red); sent without
a member (4); any letter taken as a degree (6); a third degree guessed into
the vocabulary (1); the caller's order kept (1); one degree only (4); the
tool not handing `network` to the composer (2); `network` sent raw (1).

### M.4 `N 85`: the spelling MEASURED

The cell's evidence sentence now reads MEASURED, 2026-09-28: LinkedIn writes
`connectionOf` on links 2 and 3 of the first-degree topcard
(`tests/fixtures/live2/first_degree_profile.html`), a percent-encoded JSON
list of one member id -- the spelling `people_search.compose` sends -- with
lane L5's measurement of the shapes named, and the earlier DERIVED reading
kept in the same sentence as what it read until then. The composer's own
evidence table moved with it: `connectionOf` and `network` MEASURED, and "a
two-member list is on record for no facet at all" now names the one on
record, `network`'s `["F","S"]` on link 1. This record's section 2 made both
claims on 2026-09-24; each carries a pointer to this section in place.

THE POINTER INSTRUMENT, FOUND BY MEASUREMENT. The N 85 edit was made alone
first and everything that could pin the cell was run over it: the thirteen
census instruments and generators, every one green, and the impact gate over
the network slice, 54 test files and 3,169 tests, PASS. No mechanical check
pins the cell's evidence sentence.

The instrument that pins the cell's relation to the claim it updates is the
back-pointer guard -- the test named for a claim being findable from its
update. Its entry for the network slice and this record stated that no
network row withdraws anything the record says. With `N 85` reading MEASURED
against this record's DERIVED, that reason was no longer true, so the entry
was re-pinned in the same commit -- the record now carries the update in
place, beside its own claim -- and the guard is green on it.

### M.5 `J 107`: the docstring says what session 3 measured

`linkedin_search_jobs`' paragraph on an employer's postings used to say that
whether LinkedIn's default location narrows a keyword-less employer search
was UNVERIFIED. Session 3 answered it: the no-location and "Worldwide"
searches of one employer shared 0 of their 7 postings. The paragraph now says
"For every posting at an employer, pass location "Worldwide"." with the
measurement beside it. `tests/test_a_company_search_needs_no_keyword.py` pins
the sentence and the measurement, convicts the words it replaced (a control
on the old paragraph, verbatim), and drives the call the sentence prescribes
-- one navigation, the facet and the place, no keywords key. THREE PLANTED
DEFECTS, each red: the instruction dropped; the open question left in; the
measurement dropped with the instruction kept. `J 107`'s cell notes that the
docstring says so now; its state does not move.

### M.6 Pins, each re-derived on the edited tree

    census_completion   adjudicated 182 -> 184    gap 588 -> 586
                        delivered_broad 128 -> 130    gap_read 102 -> 100
                        unfired 34 -> 36          b1_no_ruling 15 -> 17
                        b3_admitted 45 -> 43      b3_blocked_on_nothing 1 -> 0
    PINNED_B1_ROWS      NO_RULING gains `N 30` and `N 31`
    count_census_states network.md COVERED-UNFIRED 12 -> 14, GAP 163 -> 161;
                        all slices GAP 586, stated rows 770
    tool surface        61 tools, 95 -> 96 parameters, off the registry
    address table       `N 30` and `N 31` left it: 102 -> 100 rows
    read triage         `N 30` and `N 31` left it, noted beside the rows that
                        left before them

BUCKET 3 AGAIN HOLDS NO ROW BLOCKED ON NOTHING. Nothing was summed: each
figure is the instrument's reading of the tree it pins.

### M.7 Gates

Offline throughout, with nothing edited or committed while a gate ran.

- THE IMPACT GATE against master, on `a7f954f` (the four items): 15 changed
  paths, 211 of 285 test files selected, so it WIDENED TO THE WHOLE SUITE --
  12,294 passed and 2 FAILED, both in `tests/test_server_surface.py`: the
  docstring guard read the new paragraph's line-opening "add" as a read tool
  claiming a write. Reworded in `53ef478`, not exempted -- and one more verb
  the full docstring carried below the description the guard reads, reworded
  with it, so `readonly.docstring_write_claims` finds nothing in the whole
  docstring now. Re-run on `53ef478`: widened again, PASS over the whole
  suite, 12,306 tests in 1,961.9 s, sharded. Both heads are on this branch
  and nowhere on `master` until it merges.
- THE CENSUS INSTRUMENTS, thirteen, on `a7f954f`, every exit 0:
  `census_completion --check` every headline figure matches its pin;
  `check_read_addresses` GREEN 100 of 100; `check_jobs_directions` GREEN 108
  of 108; `pin_census_rows` no drift; `measure_pointer_graph` 0 pointers
  added; both triage scripts; `ruling_holds` GREEN; `check_write_classes`
  GREEN, 386 lines; `check_exclusion_basis` 38 of 38. Among them the three
  DERIVED --checks: `_audit/INDEX.md` (259 documents), `_audit/RULINGS.md`
  (68 rulings) and the blocker map, each at its fixed point.
- THE IDENTITY CHECK ON THE COMMITS, `scripts/sweep_blobs_for_identity.py`
  over `854f9ea..53ef478`: 2 commits, 982 blobs, 226 needles, 0 hits -- and
  the pre-commit gate on each commit's index.
- THE STANDING LITERAL-REPEAT GUARD, green in both whole-suite runs; the AST
  duplicate-key check, 4,457 dict literals and 13 JSON files, 0 duplicates.
- THE PLANTED MUTATIONS: 8 of 8 red for `N 31`, 3 of 3 for `J 107`'s
  docstring (M.3, M.5).

Master was still `854f9ea` when the gates ended, so there was nothing to
integrate: this branch is master and its own commits.

### M.8 What was not run

- NOTHING LIVE: `N 30` and `N 31` are COVERED-UNFIRED. Whether LinkedIn
  applies the `network` facet to the results, and what a `connectionOf`
  results page draws, only a fire at a member he names will say
  (`query_kept` reports it then).
- CI: nothing is pushed, so the suite ran on this Windows box only.
- `N 81`: LinkedIn's `network` alone, drawn on the connections page, is not
  built; the order's named-member condition refuses it (M.3). **BUILT AT
  17:02 ON HIS CALL** -- N.2.
- A COLD REVIEW of this order's change was not run.

## N 81, the degree filter 2026-09-28

The orchestrator's call of 17:02, on the finding in M.3: YES. Allow `network`
WITHOUT a named member, as the connections-page capture shows LinkedIn
writing it -- a degree filter targets no one, so mitigation 6 is untouched,
and it is a LinkedIn-written facet from tool arguments (D1). Keep exactly F
and S. Beside `connections_of` it stays `N 31`'s shape. Tests for both shapes
and a refused letter, planted mutations, `N 81` to COVERED-UNFIRED, every pin
re-derived. And a merge-order hold: lane L5's first-contact path lands first;
this lane integrates master once it is on L5's head with CI green, gates
again, and reports.

### N.1 Step 0

At 17:01 this branch stood at `6dc74c3` -- nowhere on `master` until this
branch merges -- clean. The local `master` had
moved past `854f9ea` to L5's head, `0e1040b`, which contains `dc6e349`; the
remote was still at `854f9ea`, and no CI run existed for `0e1040b`. So the
build went on `6dc74c3`, as ordered, and the integration waits.

What disk said about the facet alone: `tests/fixtures/live2/n23.html` draws
exactly one people-search link -- `network` then `origin`, no member. Its
VALUE shape is on record nowhere: the live lane's gitignored skeleton of that
page holds a placeholder token in the value's place (its class mask, printed
without its letters, is a braced pair of alphanumeric runs), and so do the
first-degree links' values in the other skeletons read this way. So the
facet alone is sent in the grammar measured on the shared links -- a
percent-encoded JSON list -- and `query_kept` reports what LinkedIn keeps of
it on the first fire.

AND ONE CLAIM OF THIS RECORD DID NOT HOLD. M.3 said the sentence "LinkedIn is
on record writing it only beside `connectionOf`" never shipped. It shipped,
in the new test file's module docstring, in `a7f954f`. It is replaced there
now, and M.3 carries a pointer to this paragraph in place.

### N.2 What was built

- `people_search.compose` no longer refuses `network` alone: the facet is a
  search of his own network by degree -- `network="F"` searches his own
  connections, with a keyword or any other facet beside it. The refusal
  literal `network_needs_a_named_member` is gone.
- Both shapes, each as LinkedIn writes it: ALONE, the connections page's --
  `network`, and `origin` never sent; BESIDE `connections_of`, the shared
  links' -- `network` before `connectionOf`. The value is the same in both.
- The vocabulary is unchanged: `F` and `S` only, in link 1's order; anything
  else refused before a session opens, alone or with a member.
- The tool's docstring and the composer's say both shapes, and the composer's
  evidence table says the alone value's shape is on record nowhere.

`tests/test_shared_connections_search.py`, 52 tests: the connections page
still draws the facet alone (a premise check); the alone address writes the
page's keys, less `origin`, with the same value as the shared shape; the two
shapes side by side, with a control that the alone check convicts the shared
address; the facet beside a keyword, a company and a place; the refusals of
eight values outside F and S in BOTH shapes, with a control that F, S and
F,S build in both; the tool refusing a third degree before any session, in
both shapes; both shapes admitted by the shipped boundary, with and without
a keyword; and the tool driven with the facet alone over the captured
results skeleton -- three people records of exactly the declared shape, one
page, the facet applied and kept, nothing about anybody outside the records.
The admission corpus of `tests/test_people_search_readers.py` takes the
facet too, alone and in every pair.

TEN PLANTED DEFECTS, each red, each source restored byte-identical: the
member rule restored (10 red); the facet silently dropped when alone (6);
`origin` sent with it, as the capture writes it (6); `network` after
`connectionOf` (3); any letter taken as a degree (14); a third degree guessed
(4); the caller's order kept (1); one degree only (6); the tool not handing
`network` to the composer (4); `network` sent raw (2).

### N.3 The census

`N 81` GAP -> COVERED-UNFIRED, its cell opening on the paragraph that moved
it and keeping the 2026-09-21 record after it: the filter-panel route is
still refused, and the row no longer waits on it. It left the address table
and the read triage. `N 31`'s cell says the facet stood alone from 17:02.

    census_completion   adjudicated 184 -> 185    gap 586 -> 585
                        delivered_broad 130 -> 131    gap_read 100 -> 99
                        unfired 36 -> 37          b1_no_ruling 17 -> 18
                        b3_admitted 43 -> 42
    PINNED_B1_ROWS      NO_RULING gains `N 81`
    count_census_states network.md COVERED-UNFIRED 14 -> 15, GAP 161 -> 160
    tool surface        61 tools, 96 parameters: no parameter moved

**A FINDING FOR THE ORCHESTRATOR, NOT ACTED ON.** With the facet alone, two
more GAP rows have a route the package's own search now composes: `N 25`
("Search your connections by name": `network="F"` with a keyword) and `N 26`
("Filter your connections by location, company, school, industry":
`network="F"` with `location_ids` or `current_company_ids`; school and
industry have no facet here). Each is blocked today on the connections
page's query variants, which the boundary refuses. Whether the people search
restricted to his first degree discharges them is a D6 question -- the
payload differs (a people search ranks and pages; the connections page lists
every connection) -- and D6 moves have been his.

### N.4 The integration of master `0e1040b`, lane L5's head

The build was committed on `6dc74c3` as `aa1b507`. Master's CI for
`0e1040b` finished green at 17:12 -- 20 of 20 jobs, queried by the full SHA
-- and the remote `master` stood on it. It was merged once, as `94bb86f`: no
file conflicted. Lane L5 touched messaging -- `dom.py`, `named_profile.py`,
`writes.py`, the message path in `server.py`, the reader baseline and three
tests -- and this branch the people search, the jobs docstring, and the
network and jobs census cells with their side tables. `aa1b507` and
`94bb86f` are on this branch and nowhere on `master` until it merges.

EVERY PIN RE-DERIVED ON THE MERGED TREE, NEVER SUMMED: `census_completion
--check` -- every headline figure matches its pin (adjudicated 185, gap 585,
unfired 37, b1_no_ruling 18, b3_admitted 42) -- and no bucket-1 row off its
hold; `count_census_states` GAP 585 of 770 stated rows; the tool surface 61
tools and 96 parameters off the registry; the address table 99 of 99 GREEN.
The merge moved none of them.

### N.5 Gates

On `94bb86f`, the integrated tree, offline, with nothing edited or committed
while they ran:

- THE IMPACT GATE against master: 15 changed paths, 212 of 286 test files
  selected, so it WIDENED TO THE WHOLE SUITE -- PASS over 12,402 tests in
  1,033.8 s, sharded, 0 failed.
- THE CENSUS INSTRUMENTS, thirteen, every exit 0, the three DERIVED
  --checks among them: `_audit/INDEX.md` (259 documents), `_audit/RULINGS.md`
  (68 rulings) and the blocker map, each at its fixed point.
- THE IDENTITY CHECK ON THE COMMITS: `scripts/sweep_blobs_for_identity.py`
  over `0e1040b..94bb86f` -- 5 commits, 1,008 blobs, 226 needles, 0 hits --
  and the pre-commit gate on every commit's index.
- THE STANDING LITERAL-REPEAT GUARD green in the whole suite; the AST
  duplicate-key check 4,498 dict literals and 13 JSON files, 0 duplicates;
  the cited-SHA guard green.
- THE PLANTED MUTATIONS: 10 of 10 red for `N 81` (N.2).

This section's own commit changes only this document and the regenerated
blocker map; it gets the impact gate for those paths.

### N.6 What was not run

- NOTHING LIVE: `N 81`, like `N 30` and `N 31`, is COVERED-UNFIRED. Whether
  LinkedIn keeps the facet alone, and in what spelling, only its first fire
  says (`query_kept`).
- CI on this branch: nothing is pushed; the suite ran on this Windows box.
- A COLD REVIEW of the `network` facet's two shapes was not run.
- `N 25` and `N 26`: not moved -- a D6 question (N.3).
