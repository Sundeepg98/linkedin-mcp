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
section 9.

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
* **THE BOUNDARY ANSWERS, BEFORE ANY SESSION OPENS.** `boundary_verdict` puts
  the composed address to `readonly.assert_read_url` -- the door itself, the
  same call `BROWSER.goto` makes first, not a copy of its decision. A keyword
  that trips a forbidden substring (8 of 11 ordinary keywords per the
  2026-09-19 preconditions audit B.4) comes back structured: the boundary's
  own kind (`write_attempt_blocked`), the substring (published only when it
  is a member of the boundary's own tuple), whether a read pattern admits the
  address, which argument carried it, and a sentence written for a person who
  was searching -- not "not a read surface". Zero pages loaded, no session
  opened, the denylist not narrowed.
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
    tests/test_people_search_readers.py    NEW. 105 tests, section 6
    tests/test_server_surface.py           comment only: "NO PARAMETERS AT ALL" amended
    _audit/_census/network.md              seven cells, section 7
    _audit/_census/read-addresses.tsv      the seven lines removed: the rows left bucket 3

The `server.py` hunk is the tool, one import line and three lines of the
module docstring. No tool was added, so the tool count stays 51.

## 5. Per row

    row    verdict                 what it rests on
    N 79   BUILT, COVERED-UNFIRED  keywords, LinkedIn-authored spelling (MEASURED)
    N 194  BUILT, COVERED-UNFIRED  the same reader; composes the exact address the table held
    N 84   BUILT, COVERED-UNFIRED  currentCompany JSON list, LinkedIn-authored (MEASURED)
    N 87   BUILT, COVERED-UNFIRED  pastCompany: bare on record, list DERIVED
    N 94   BUILT, COVERED-UNFIRED  geoUrn two-value list DERIVED; composes the table's own address
    N 85   BUILT, COVERED-UNFIRED  connectionOf never LinkedIn-authored; list DERIVED
    N 172  BUILT, COVERED-UNFIRED  the same reader as N 85

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
  substring and `a_read_pattern_admits_the_address` True, the three clean ones
  are admitted, and the eleven split 8 / 3 exactly as B.4 measured. The
  refusal reading is driven beside `check_read_addresses.kind_of_refusal` over
  the same refusals, so a reworded gate sentence turns both red together; a
  gate sentence naming a substring outside the boundary's tuple publishes no
  substring. A boundary refusal and an argument refusal each open NO session.
* **NOTHING COMES BACK.** The driven payload carries no plant and none of the
  five argument values; `query_kept` reads the planted foreign values as
  `different_values`, never as kept. Seventeen refused arguments (slugs, the
  Arabic-Indic digits `str.isdigit()` accepts, over-long runs, empty members,
  duplicates, over budget, a short token, a control character, an over-long
  keyword) each name their argument and never their value. A keyword carrying
  a no-break space or a zero-width joiner -- ordinary in several Indian
  scripts -- is NOT refused: control characters are refused by Unicode
  category `Cc`, not by `str.isprintable()`, which is False for both (found in
  self-review after the first commit and fixed in the last).
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

PENDING -- filled in after the census commit.

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

## Live queue

Every call is ONE people search and ONE page load. `D1-SEARCH-AS-READS` caps a
live session at FIVE test searches, so the six calls below are two sessions:
the first five, then the member row once the operator names a member. No value
below identifies the operator; the member token and any organisation id are
supplied at fire time and written into no tracked file.

What banks a row, for every line: `ok` True, `landed_on_people_search` True,
`query_kept.<argument>` `verbatim` or `same_values`, `results.person_results`
at least 1, `panel_wait.settled` True and `denominators.values_refused` 0.
`absent` or `different_values` convicts the spelling (the row goes back to GAP
with the finding); `person_results` 0 banks nothing, because hidden, empty and
a dropped facet read alike.

    N 79   linkedin_people_search_shape(keywords="engineer")                 1 load, search 1/5; banks the keyword row -- and records the scope judgement its cell asks for (PROVEN, or COVERED-CANNOT-DELIVER for a count-only answer)
    N 194  linkedin_people_search_shape(keywords="#hiring")                  1 load, search 2/5; banks as N 79, the same scope judgement
    N 84   linkedin_people_search_shape(current_company_ids="<id>")          1 load, search 3/5; <id> = the numeric Page id linkedin_job_detail resolves as company_id on a posting at any employer that is not his (the J 10 route, fired live 2026-09-20); banks on query_kept.current_company_ids
    N 87   linkedin_people_search_shape(past_company_ids="<id>")             1 load, search 4/5; <id> as for N 84, from a different posting; query_kept.past_company_ids also settles the DERIVED list spelling
    N 94   linkedin_people_search_shape(keywords="engineer", location_ids="103644278,101165590")  1 load, search 5/5; two country-level geo ids (the United States and the United Kingdom as publicly documented -- UNVERIFIED here, from recall; neither his city nor his country); banks on query_kept.location_ids with both ids sent, and settles the DERIVED two-value list
    N 85   linkedin_people_search_shape(connections_of="<token>")            1 load, search 1/5 of a SECOND session; <token> = ONE member he names, e.g. the recipient_id linkedin_connections returns for a 1st-degree connection he picks; banks on query_kept.connections_of and settles the never-LinkedIn-authored key
    N 172  (the same call as N 85, no second load)                           0 extra loads; banks with N 85, and person_results at least 1 also answers its own question: that member's connections are shown to this account
