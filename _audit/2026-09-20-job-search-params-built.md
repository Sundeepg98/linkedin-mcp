# JOB-SEARCH-PARAMS, built -- 2026-09-20

Wave `build-job-params`, branch `worktree-agent-a73bb3e74aba894ec`, from master
`8efa310`. Four commits, no push (sibling worktree branches are not pushed on
this repo; the wave lead integrates).

    576f5e6  feat(jobs): several locations is several loads, because both url
             spellings were measured wrong
    cf76e17  test(jobs): two of my own guards could not fail, and a mutation
             run is what said so
    e3f9097  instrument: the multi-location guards, shown failing on demand
             rather than once

---

## THE HEADLINE: THE BRIEF SAID SIX ROWS. ONE WAS STILL GAP.

I was briefed "6 rows, cost 1, ratio 6.00, the cheapest real build in the
census". **Five of the six had already left GAP before this wave started**, and
the committed tree said so at `8efa310` -- I measured it in my first two tool
calls, before any decision, and the wave lead sent the same correction
independently an hour later.

The reading, from `_audit/_census/blocker-map.tsv` **as committed and
unedited**, `state_at_freeze -> state_today`:

    J 9     GAP -> COVERED-PROVEN     Filter: Easy Apply only
    J 11    GAP -> COVERED-PROVEN     Filter: Employment type / job type
    J 12    GAP -> COVERED-PROVEN     Filter: Under 10 applicants
    J 13    GAP -> COVERED-PROVEN     Filter: In your network
    J 14    GAP -> COVERED-PROVEN     Filter: Fair chance employer
    J 151   GAP -> GAP                Filter by MULTIPLE simultaneous locations

`scripts/rank_live.py` on master agrees and now reports `JOB-SEARCH-PARAMS pub
6 held 6 stillGAP 0 drift -6` -- the 0 being this wave's work, the -6 being the
ledger's frozen table.

**I did NOT re-close a closed row, and I checked rather than assumed**, because
"the census says closed and the capability is absent" is the worse defect. The
live tool surface carries all five:

    _BOOLEAN_FILTERS = (('easy_apply','f_AL'), ('under_ten_applicants','f_EA'),
                        ('in_your_network','f_JIYN'),
                        ('fair_chance_employer','f_FCE'))
    _JOB_TYPE        = 7 values -> f_JT
    mcp.list_tools() reports easy_apply, job_type, under_ten_applicants,
                     in_your_network, fair_chance_employer all PRESENT

Census and code agree on all five. Nothing was padded to match the brief.

---

## PER ROW

| row | capability | state | what proves it |
|---|---|---|---|
| J 9 | Filter: Easy Apply only | **already COVERED-PROVEN**, untouched | shipped 2026-09-04, banked 2026-09-19. Re-verified this wave against the live tool surface and `tests/test_job_search_result_window.py` (6 tests green). Not my work. |
| J 11 | Filter: Employment type / job type | **already COVERED-PROVEN**, untouched | as above; `server._JOB_TYPE` -> `f_JT`, 7 values. |
| J 12 | Filter: Under 10 applicants | **already COVERED-PROVEN**, untouched | as above; `f_EA`. |
| J 13 | Filter: In your network | **already COVERED-PROVEN**, untouched | as above; `f_JIYN`. |
| J 14 | Filter: Fair chance employer | **already COVERED-PROVEN**, untouched | as above; `f_FCE`. |
| J 151 | Filter by MULTIPLE simultaneous locations | **SHIPPED this wave. GAP -> COVERED-UNFIRED** | `tests/test_job_search_multiple_locations.py`, 27 tests. The load-bearing one is `test_a_fan_out_builds_one_url_per_place_and_never_joins_them`. See below. |

---

## J 151: WHAT SHIPPED, AND WHY IT IS NOT A PARAMETER

The ledger costed all six rows at 1, as though the sixth were one more dict.
**It is not, and that is a measurement the previous wave already took.** On
2026-09-05, with city A alone returning 7 postings and city B alone 7, sharing
2:

    location=A%2C%20B       KEPT by LinkedIn. 7 postings, of which ZERO are
                            A-only and ZERO are B-only -- the comma-joined
                            string geocodes somewhere neither search reaches.
    location=A&location=B   STRIPPED. LinkedIn serves the LAST city alone
                            (0 of A-only, 5 of B-only).

Both spellings are WRONG rather than unmeasured, so neither ships. That reading
named the honest route in its own words -- *"two searches, one per city, is the
correct route today"* -- and **this is that route moved inside the tool.**

### The shape

`linkedin_search_jobs(locations="<place>; <place>")` -- SEMICOLON-separated.
One `/jobs/search/` load per place, merged **round-robin** and de-duplicated by
`job_id`. Every row gains `found_in` (the place whose search returned it
first); `searches` reports per place what it gave, including a place that gave
nothing; `pages_loaded` is the load count.

* `linkedin_server/jobfilter.py` -- `locations_plan` (the verdict),
  `split_locations`, `comma_count`, `merge_location_reads` (the merge),
  `LOCATIONS_SEPARATOR`, `MAX_LOCATIONS`.
* `linkedin_server/server.py` -- the `locations` parameter, and `_search_url`,
  the ONE function through which a location reaches a url.

### Three decisions worth arguing about, and the reasoning behind each

**1. The separator is a semicolon, and that is the whole safety argument.** A
comma is part of a place's own spelling -- LinkedIn writes places as "City,
Region, Country" -- so a comma-separated list cannot be parsed back into the
places that went into it, and BOTH readings fail silently: split a qualified
place on its commas and you search three things that are not places; do not
split it and a caller who comma-separated two cities hands LinkedIn the exact
string measured to geocode elsewhere. No parse is right for both.

**So `locations` naming only ONE place is REFUSED rather than run.** A lone
entry is either a caller who wanted `location`, or a caller who comma-separated
two cities and is one load from the measured failure. Both readings are cleared
by the same one-line fix on the caller's side, so refusing costs nothing and
guessing costs a shortlist built on a city nobody asked for.

**2. The merge is round-robin, not concatenation.** Concatenation is the
obvious merge and it is silently wrong at this tool's own measured numbers: the
window was measured at 7 postings per load, so three places is up to 21 rows
against a default `limit` of 25 and five places is up to 35. A concatenated
list trimmed to the limit drops the LAST places entirely -- `capped` true, and
nothing saying which place vanished. Round-robin makes the trim fall evenly;
order WITHIN a place is untouched, so LinkedIn's own ranking for that city is
preserved exactly.

**3. Every refusal reports COUNTS and never the value.** A place name a caller
typed is not a third party's identity the way a company slug is, but nothing in
these refusals NEEDS the text to explain itself, and a refusal that quotes its
input is one edit from quoting an input that should never be echoed. The
single-entry refusal reports `describe_shape` plus a comma COUNT, which is
exactly the diagnostic a caller acts on.

---

## WHAT THE BOUNDARY CHANGE ADMITS: NOTHING. MEASURED, NOT ASSUMED.

**There is no boundary change.** Stated precisely, because "no security change"
is the kind of claim that should be checkable:

* **No new address.** Every load is `/jobs/search/?keywords=...&location=...`,
  already on the read allowlist since the first commit. Only the `location`
  VALUE differs between loads, and it was already caller-supplied text.
* **No new admission**, therefore no name-free shaper is owed. Nothing in this
  change can return another person's name, slug or urn that the existing
  single-location search could not.
* **No new injected script**, so `INJECTED_SCRIPTS` in `tests/test_readonly.py`
  is untouched. No new `evaluate` call site, so the `EXECUTED_SCRIPTS` count
  and the `dom.py` waiver cap do not move.
* **No character class was widened.** No `\d` was added anywhere; no id or slug
  pattern was touched. (The one place this wave counts digits at all is a job
  id already parsed by existing code.)
* **`linkedin_server/readonly.py` was NOT edited.**

Evidence: the boundary and inventory set passes untouched -- 1172 tests across
`test_readonly`, `test_readonly_boundary_invariant`, `test_launch_boundary`,
`test_api_call_sites`, `test_blast_radius`, `test_every_orphan_module_is_ruled`,
`test_surface_census`, `test_reader_reachability`, `test_no_committed_identity`,
`test_a_person_name_is_never_a_literal`, `test_path_hygiene`.

### What it CANNOT reach, stated rather than glossed

**LinkedIn's own CROSS-LOCATION RANKING.** No request names two places, so what
comes back is several per-city windows merged. Postings that a genuine
one-request multi-location search would have ranked BETWEEN the cities were
never in any page this read. A caller comparing this against LinkedIn's web ui
will see a different set, and the reason is structural -- which is why the
result carries a `note` saying so and the docstring says it twice.

Reaching the real one-request form still needs LinkedIn's numeric place ids,
which a posting does not carry and which only a further page load could
resolve. **Nobody here has them, and this wave did not go and get them: no
browser session was opened.**

`jobfilter.MAX_LOCATIONS = 5` is **a cost budget on this server, not a measured
LinkedIn limit**, and is declared as one in the source, in the refusal text,
and in a test that pins it as a literal.

### Why COVERED-UNFIRED and not COVERED-PROVEN

No browser session was opened this wave (reads only, no writes, per the brief).
**Nothing here has seen the fan-out return a live payload.** The siblings J 9
and J 11-14 were verified LIVE against result sets; this one is verified
offline against a driven page. That is a statement about the evidence class,
not a hedge about whether the capability exists.

**The one live reading worth taking**, for whoever next has a session: fire
`locations` with two cities and confirm the two navigations land where they
were sent and that the merged set is the union of the two single-city sets. The
per-load behaviour is already measured; what is unfired is the fan-out through
the real browser.

---

## GUARDS, AND ALL FOURTEEN SHOWN FAILING

`scripts/_check_location_guards_can_fail.py` plants fourteen mutations one at a
time, runs the single test node that should catch each, and restores the file
in a `finally`. It refuses to run on a dirty tree and asserts the tree is clean
again before printing. **Current result: caught 14 of 14.**

    naive fan-out: comma-join the places into ONE url              RED (caught)
    naive fan-out: append the location key once per place          RED (caught)
    merge by concatenation instead of round-robin                  RED (caught)
    stop de-duplicating by job_id                                  RED (caught)
    decide the plan AFTER the first page load                      RED (caught)
    let a single entry through instead of refusing the comma trap  RED (caught)
    quote the caller's place in the refusal                        RED (caught)
    raise the ceiling so it refuses nothing                        RED (caught)
    a SECOND url builder appears beside the funnel                 RED (caught)
    the merge helper is RENAMED out from under its call site       RED (caught)
    the banked row silently reverts to GAP                         RED (caught)
    the parameter pin is left at 61                                RED (caught)
    the source_url ruling is withdrawn                             RED (caught)
    the ruling names ONE site where there are two                  RED (caught)

### TWO OF MY OWN GUARDS COULD NOT FAIL, AND THE FIRST RUN IS WHAT SAID SO

Both were committed green in `576f5e6` and **neither would have been found by
running the suite, because a check that cannot fail passes.**

1. **`test_the_ceiling_refuses_one_more_than_it_accepts` built BOTH its inputs
   out of `jobfilter.MAX_LOCATIONS`.** Raising the constant from 5 to 500
   raised the test's own inputs with it, so the cap refused nothing and the
   assertion stayed green. *A check whose input is derived from the value under
   test measures the derivation, never the value.* Fixed by pinning the literal
   5, which makes re-costing the budget fail here deliberately.

2. **`test_the_multi_location_chain_is_still_whole` matched its function names
   as SUBSTRINGS.** Renaming `merge_location_reads` to
   `merge_location_reads_renamed` left `"def merge_location_reads"` in the
   source -- the old name is a PREFIX of the new one -- so the chain read whole
   while `server.py`'s call site pointed at nothing. A rename is the likeliest
   way that link breaks and it was the one shape the check could not see. Now
   matched as AST `FunctionDef` names.

### TWO EXISTING GUARDS FIRED, AND BOTH WERE RIGHT

1. **`tests/test_tools.py::test_the_tool_says_it_takes_one_location`** went red
   the moment the capability landed, **exactly as its own docstring promised**:
   *"a test that reads the docstring fails the moment the argument becomes a
   list and nobody updated the prose."* Its claim was retired by the build, so
   it is **REPLACED, not deleted**, by
   `test_the_tool_says_how_it_reaches_several_locations`, which demands MORE:
   the two measured-wrong spellings still named, the several-loads cost stated,
   and the `Args:` block checked on BOTH lines (the old guard's own red-proof
   had found that a paragraph high in a docstring does not reach a caller who
   reads `Args:` and stops).

2. **`tests/test_the_source_url_split_was_never_ruled.py::test_every_emission_point_is_declared`**
   refused `merge_location_reads` for writing `source_url` at two sites with no
   ruling. **I had not run this file; a delegated inventory slice found it.**
   Declared `PASSTHROUGH` with count 2, on that table's own logic -- the
   category describes what the SITE does, not where its value came from, which
   is why `shape.envelope` is PASSTHROUGH although several of its callers are
   declared UNMEASURED. What the category does NOT cover is said in the
   declaration: site 2 SELECTS one url out of N, so a caller reading
   `source_url` on a fan-out gets the FIRST place's search. That is answered in
   the payload rather than hidden -- every url is in `searches`.

---

## WHAT I CHANGED

    linkedin_server/jobfilter.py    +322  LOCATIONS_SEPARATOR, MAX_LOCATIONS,
                                          split_locations, comma_count,
                                          locations_plan, merge_location_reads
    linkedin_server/server.py       ~+130 the `locations` parameter, _search_url,
                                          the fan-out loop, the fan-out note,
                                          the rewritten location docstring
    tests/test_job_search_multiple_locations.py   NEW, 27 tests
    tests/test_tools.py                    the replaced docstring guard, the
                                           query echo gains `locations: None`
    tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py
                                           pin 61 -> 62 parameters, 44 tools
                                           unchanged, with the re-pin argued
    tests/test_a_covered_row_names_the_artifact_that_covers_it.py
                                           J 151 banked + the chain test
    tests/test_the_source_url_split_was_never_ruled.py   the PASSTHROUGH ruling
    scripts/_check_location_guards_can_fail.py    NEW, the mutation battery
    _audit/_census/jobs.md                 J 151 GAP -> COVERED-UNFIRED, and
                                           the summary row's costing corrected

**`_audit/_census/blocker-map.tsv` is DERIVED and is deliberately left stale** --
its J 151 row still reads `GAP`. Per the brief, `scripts/build_blocker_map.py
--write` was NOT run; the wave lead regenerates it once after integrating.
`tests/test_blocker_map_is_derived.py` passes as it stands.

### A note on place names in the test file

Every proper noun in `tests/test_job_search_multiple_locations.py` is already in
the tracked tree -- "Riverton", "Fairhaven", "Ashgrove", "Northgate" are this
repository's own invented vocabulary, used 86, 82, 56 and 10 times respectively
before the file existed. **Coining a new placename would have been the riskier
move**: a plausible-sounding invention is one search away from being somewhere
real, and the identity wordlist that would otherwise catch it is gitignored, so
it runs DISARMED in a worktree. My first draft used two invented names and both
turned out to be real places; they were replaced before the first commit.

---

## HONEST RESIDUE

* **The fan-out has never been fired live.** That is the single thing standing
  between COVERED-UNFIRED and COVERED-PROVEN, and it needs a browser session
  this wave was told not to open.
* **`MAX_LOCATIONS = 5` is a guess with a reason, not a reading.** Nobody has
  measured whether LinkedIn cares how many searches arrive in a minute. The
  number bounds THIS server's cost and says so in three places.
* **De-duplication is by `job_id` and only by `job_id`.** A row that carries no
  job id cannot be compared against anything and is kept as it stands;
  `searches[].unkeyed` counts them, so the de-dupe says what it could not speak
  about rather than staying silent.
* **The `searches[].source_url` values are relayed raw**, as
  `_read_cards` already emits them (declared UNMEASURED there). The fan-out
  does not make that better or worse; it relays N of them where there was one.
* **The ledger's ranking table at `_audit/2026-09-03-linkedin-gap-blockers.md`
  L171-188 still publishes 6 rows for this blocker.** It was 1 before this wave
  and is 0 after. `scripts/rank_live.py --drift` on master reports the gap; the
  frozen table does not, and nobody amends a table.
