# 2026-11-26 -- lane selfprofile26: his own profile, asserted without the url marker

Lane: selfprofile26. Worktree branched from master 4c62196 (certified). All work
OFFLINE: built against the live lane's session-11 skeletons (read-only, its
gitignored state) and committed fixtures; nothing reaches LinkedIn. Session 11
was live when the lane began (`_state/LIVE_SESSION_ON`), so those runs were
targeted and serial; the session had ended by the first green run. The lane was
cut at about 01:30 IST when the CLI exited and the box rebooted; it resumed at
09:25 IST on an intact tree (HEAD 4c62196, the WIP as the orchestrator measured
it) and finished from there.

| item | status |
|---|---|
| 1. the regression, measured | MEASURED on session 11's own skeletons and logs |
| 2. the structural signal | CHOSEN and MEASURED: 4 on the new landing, 4 on each older self capture, 0 on every tracked capture of another member's profile |
| 3. the sites | FIXED offline: the three named, plus the census item veto (found by reading the loader's callers) and the live harness's two steps |
| 4. tests, red first | RED on 4c62196's code (46 failed); GREEN on the fix; four mutations, every one now caught |
| 5. census | NO EDIT; the rows affected are named in section 5 |
| 6. CI | section 7 |

---

## 1. The regression

LinkedIn's `/in/me/` redirect stopped carrying `isSelfProfile`. Session 11's two
early loads of `/in/me/` (ledger loads 1 and 2, 23:18:58 and 23:19:26) landed on
the member path with NO query string at all, and the package's self-profile
loader refused both as `self_assertion_unreadable`: it retries an absent marker
once, so the two loads are one refused call. The live lane's runner then stopped
relying on the marker and asserted self from the redirect plus owner-only words
in the top card (`run_profile.log`: relation `SERVED, same depth, different url`;
"owner-only controls visible in the top card: 3").

The marker is gone from the page too, not only from the landing url:

| capture | `isSelfProfile` occurrences |
|---|---|
| tracked `live2/in_me.html`, `live3/in_me.html`, `live8/in_me.html` (older self captures) | 28 each |
| session 11 `in_me_profile.skeleton.html` (the new landing) | 0 |
| session 11 `in_me_more-open.skeleton.html` | 0 |
| session 11 `in_me_photo-open.skeleton.html` | 1, on one link inside the photo dialog, not on the landing |

The 28 old `/in/<member>/?isSelfProfile=...` links became plain `/in/<member>/`
links on the new landing (root links on the member: 38 + 28 then, 65 now).

Everything that anchored on the marker refuses his own profile:
`server._self_assertion_state` through `server._goto_self_profile_asserted`,
`press.self_landing`, and C1 of the authorship check in
`linkedin_my_activity_items` (the same loader). Section 3 names the others.

---

## 2. The structural signal, measured before anything was built on it

**THE SIGNAL.** An `<a>` with an accessible name whose `href` is
`https://www.linkedin.com/in/<the landed member>/edit/...` -- LinkedIn's own
editor controls for the profile on screen. A relation, not a presence: the
member in the control's href must be the member the landing names.

**THE MEASUREMENT** (offline, counts and shapes only; the scratch probes are
declared disposable in INSTRUMENTS section 104, and the measurement itself is
kept as `test_the_signal_on_every_tracked_profile_capture`):

| capture | edit routes under `/in/<landed member>/edit/` | of those carrying an accessible name | edit routes under another member's path |
|---|---|---|---|
| session 11 landing (`in_me_profile.skeleton.html`, keyed) | 4 | 4 | 0 |
| session 11, top-card More open / photo dialog open | 4 / 11 | -- | 0 / 0 |
| tracked copy of the session 11 landing (`tests/fixtures/live11/in_me_profile.html`) | 4 | 4 | 0 |
| tracked copies of the same landing with the top-card menu open / the photo dialog open (`live11/in_me_more_open.html`, `live11/in_me_photo_open.html`) | 4 / 11 | 4 / 7 | 0 / 0 |
| tracked `live2/in_me.html`, `live3/in_me.html`, `live8/in_me.html` | 4 each | 4 each | 0 |
| tracked `live2/first_degree_profile.html` (another member) | 0 | 0 | 0 |
| tracked `live3/named_profile.html` (another member) | 0 | 0 | 0 |
| tracked `live3/m1_after_press.html` (another member, after its Message press) | 0 | 0 | 0 |
| untracked session 7 `named.skeleton.html` (another member, keyed) | 0 | -- | 0 |
| the session 11 landing re-landed under a different member path | 0 | 0 | 4 |

On the keyed session-11 skeleton the relation was checked against the landed
member itself: the live runner's own record of the landed segment, shaped with
the session's key in-process and compared token for token (printed as booleans
and counts only). All 4 edit routes name the landed member; the 10 other
members the page draws are linked at their profile roots only.

**THE ROUTE TAILS**, matched under the session's key against LinkedIn path
words only (nothing personal was hashed): `/edit/intro/`,
`/edit/forms/summary/new/`, `/edit/forms/<29 characters>/new/` and
`/edit/<18 characters>/`. The first two are exactly the first two entries of
`dom.PROFILE_EDITOR_HREFS`, measured on his profile on 2026-08-30. Every tracked
self capture since session 2 carries four routes of the same shapes (two
`edit/x/`, two `edit/x/x/x/`). (The same keyed comparison confirms that the
outbound wrapper named below is `/safety/go/?url=...` and that the one marker
inside the photo dialog reads `isSelfProfile=true`.)

**WHAT WAS NOT CHOSEN, AND WHY.**

* The live runner's owner-only WORDS (`Open to`, `Enhance profile`, `Add
  profile section`, `Resources`), and a `<button aria-label="Edit">` drawn on
  his profile and not on the named one: label text, which this package does
  not read into a decision (press condition 2), and localised.
* `/in/<member>/overlay/...` links: drawn on other members' profiles too (2 on
  each tracked one: contact info).
* `/analytics/...` links: owner-only in practice but not a relation -- nothing
  ties them to the member the url names.
* The viewer's own "complete your profile" editor link: drawn on pages that
  are NOT his profile (one each on tracked `live1/overview.html`,
  `live1/post_summary.html`, `live2/memberships.html`, as
  `/in/<viewer>/edit/.../?profileFormEntryPoint=...`, with NO accessible
  name). On a stranger's profile such a link names the viewer, not the page --
  which is why the relation, and the accessible name, are required.

**WHAT IS STILL UNMEASURED, stated as such.** No capture shows a member's OWN
content linking to `/in/<that member>/edit/...` on their profile; LinkedIn
wraps outbound links in content (`/safety/go/?url=...`, measured on this
landing) and the accessible-name requirement excludes a plain linkified URL.
The gates that matter most never meet the case: the loader only ever loads
`/in/me/`, which resolves to the signed-in member by construction.

---

## 3. The rule, and the sites

**THE RULE** (`linkedin_server/self_profile.py`, one implementation for every
site):

* the url marker says `true`: SELF, exactly as before;
* the url marker says anything else: NOT SELF, settled, never retried, as before;
* NO marker, and the page draws at least one edit control for the landed member
  and NO edit route for any other member: SELF, by structure;
* no marker and an edit route under ANOTHER member's path: AMBIGUOUS -- refused
  at once, never retried, and the refusal names the counts;
* no marker and nothing either way, a reading that failed, or a landing that is
  not a member's profile root (the self alias `me` included): ABSENT, retried
  once as before, then refused naming what was seen.

Never "any profile under /in/": the landing must be a profile ROOT on
`https://www.linkedin.com`, its segment must pass a closed alphabet before it is
written into an XPath literal, and the structure must name that member. The
counts are LOCATOR counts -- no script is injected, so no `page.evaluate`
waiver is spent (the budget is pinned at 25, DOM-WAIVER-25-J110) -- and only
three integers cross back. A refusal's `self_evidence` is closed words and
those integers; the landing is never quoted.

**THE SITES.**

| # | site | what anchored on the marker | the fix |
|---|---|---|---|
| 1 | `server._self_assertion_state` / `server._goto_self_profile_asserted` -- the editor gate `_establish_self_owned_editor` (`linkedin_profile_editor_fields`, `linkedin_profile_editor_values`) | the loader read only the url; ABSENT twice was a refusal | the loader asks the page when the url does not answer; `_self_assertion_state` stays the marker's half; returns `(landed, state, loads, saw)` |
| 2 | `press.self_landing` (and through it `admitted_address`, `check_address`, `sensitivity_basis`, `check_reading`, `check_basis`, `evaluate`, `disclose`) | admission of the landed member path needed `isSelfProfile=true` | `self_landing(url, edit_routes)`; `disclose` counts the structure ONLY for a member root with no marker, before the pre-press verdict and again before the post-press one; every other page is still decided without being touched |
| 3 | C1 of the authorship check in `linkedin_my_activity_items` | the same loader | the same loader; C2 and C3 unchanged |
| 4 | **`server._own_item_veto`** -- the census's `feed_item` veto (`linkedin_surface_census("feed_item", item=...)`) | the same loader, and it names neither `isSelfProfile` nor the parameter constant, so a grep for the marker does not find it | the same loader and the shared refusal |
| 5 | **the live harness**, `scripts/_probe_live_lane_session_2.py`: `_in_me` (requires the loader's TRUE) and `_in_me_more` (calls `press.self_landing(page.url)`) | the loader's 3-tuple and the url-only `self_landing` | 4-tuple; `_in_me_more` takes the gate's own structural reading first, as `disclose` does |

**FAIL-CLOSED, as a structural change.** Sites 1, 3 and 4 refused FALSE and
ABSENT by name and went ON with anything else -- a gate that opens for every
state somebody adds later. All three now refuse whatever is not TRUE, through
one builder (`server._self_profile_refusal`).

**WHAT SUCCESS NOW SAYS.** The ownership and authorship blocks carry
`self_signal` -- `url_marker` or `edit_controls` -- and `self_assertion_present`
is true when either answered. The `how` strings name both signals.

**NOT A SITE, checked rather than assumed.** `writes._assert_landed_on_target`'s
self-profile rule compares the PATH after the member segment and rests on the
request being `/in/me/`; it never read the marker. `browser.goto` returns the
landed url and asserts only the requested one. `named_profile` folds segments
for a named member's landing and never reads the marker. The `isSelfProfile`
in `tests/test_fixtures_hold_only_synthetic_people.py` (`SELF_PROFILE_MARK`)
skips interface text on marked self links; the new fixture's text is all `x`,
so it reads nothing there either way.

---

## 4. Tests, red first

**THE FIXTURE.** `tests/fixtures/live11/in_me_profile.html` -- session 11's
skeleton of the landing through the live harness's own shipped `tracked_copy`:
strict ASCII, no keyed shape, every value `x` (so every member segment is `x`),
id references as `k`+hash, 243,094 characters. This lane first built its own
copy (the harness's function, imported, over the same skeleton) and committed
it in a fixtures directory of its own; the live lane's session
11 merge then landed its 48 tracked copies on master, and the two files were
BYTE-IDENTICAL (one sha-256). At the merge of master 7760a5f this lane's copy
was removed and every test points at the live lane's. The controls
are the tracked captures already in the repository (another member's profile:
`live2/first_degree_profile.html`, `live3/named_profile.html`,
`live3/m1_after_press.html`) plus the SAME real landing re-landed under a
different member path.

**THE TESTS.** `tests/test_self_profile_without_the_url_marker.py` drives every
site through a SHIPPED entry point over the real landing, in a local headless
Chromium whose page answers from tracked files and aborts every other request:

| test | site | on the fix |
|---|---|---|
| `test_the_signal_on_every_tracked_profile_capture` | the measurement, kept | 4/4/0 on the new landing and the three older self captures; 0/0/0 on all three other-member captures; 0/0/4 on the landing re-landed elsewhere |
| `test_the_editor_gate_establishes_his_ownership_on_the_new_landing` | 1 | both editor tools: ownership established by `edit_controls`, same member, editor loaded, 2 pages, 0 clicks |
| `test_the_editor_gate_refuses_every_other_landing_and_names_what_it_saw` | 1, CONTROL | another member's real profile: `self_assertion_unreadable` after 2 loads, editor never loaded, `self_evidence` 0/0/0; the landing re-landed elsewhere: `self_profile_ambiguous` after 1 load |
| `test_c1_of_the_authorship_check_holds_on_the_new_landing` | 3, and CONTROL | C1 holds on load 1 and the refusal moves to C2 (`no_overflow_controls`: the tracked copy's labels are `x`); with a synthetic rail in `main` his two item keys come back; the same rail in another member's real profile publishes none |
| `test_the_census_item_veto_reads_his_rail_on_the_new_landing` | 4, and CONTROL | veto verified, the item page loaded after one profile load; on another member's profile the item page is never loaded |
| `test_the_press_gate_sees_his_profile_on_the_new_landing` | 2, and CONTROLS | `[aria-haspopup]` reaches `control_judged_an_action` and `[aria-expanded]` `control_not_judged` (the per-control judgements only his profile has); both other-member captures and the re-landed landing stay `address_not_admitted`, terminal; 0 clicks |
| `test_the_pure_press_gate_takes_the_structural_reading_and_says_so` | 2 | `check_address(url, edit_routes=...)` is `{admitted, self_landing}`; without the reading the url-only gate is unchanged |
| `test_the_live_harness_sees_his_profile_on_the_new_landing` | 5, and CONTROL | `_in_me` gets past the self check; `_in_me_more` stops at the opener rule (both bars draw with no stylesheet) instead of `not_on_his_profile`; another member's profile still `not_on_his_profile` |
| the rule as a table, the member-root guard, the alphabet guard, the marker's own reading | `self_profile` | 14 + 13 + 7 + 1 pure cases |

And in `tests/test_activity_items.py` (A2's synthetic markup, isolating C1 as
A3 does): `test_c1_holds_by_structure_when_the_url_carries_no_marker`,
`test_an_edit_control_for_another_member_is_ambiguous_and_reads_nothing`, two
new rows in `EVERY_PATH` (so the privacy sweep covers both new paths, with the
member slug in the markup and absent from every answer), and the refusal-code
enumeration gains `self_profile_ambiguous`. Its harness forwards `locator`
unrecorded, so `scripts` still holds exactly what the tool executed.

**RED, against the base tree's code (4c62196), the final test files:** 46
failed, 11 passed. 37 of the failures are `ImportError: cannot import name
'self_profile'`; every behavioural one is the regression itself --
`self_assertion_unreadable` from both editor tools, the activity tool and the
census veto; `address_not_admitted` from the press gate on his own landing;
`_Anomaly: self_assertion_not_true at in_me` from the harness; `self_evidence`
missing; the enumeration missing `self_profile_ambiguous`. The 11 that pass on
the base are the fixture's own integrity check and the 10 privacy sweeps.

**GREEN, the same 57 on the fix:** 57 passed (88.6 s, four workers, no live
session on the box).

**RED AGAIN, after the last test edits, on a clean export of 4c62196**
(`git archive` into the scratch directory, the final test files and the fixture
copied in): 46 failed, 11 passed, 1 error -- the error is `tests/test_press.py`
failing at import on `self_profile`, which holds the new press test too.

**THE PRESS GATE'S OWN TEST, NARROWED FOR ONE ROW, AND WHY.**
`test_a_refused_press_never_touches_the_page` asserted `page.selectors == []`
for every row. Its row `/in/another-person/` -- a member profile root with no
marker -- is now asked three locator COUNTS before its verdict: since
2026-11-25 his own landing has exactly that shape, so whether such a page is
his is no longer a function of the url, and the module's own rule ("every
refusal a URL can predict is taken before the page is touched") no longer
covers it. The assertion now admits exactly the three locators
`self_profile.edit_route_selectors` names for that url's member and nothing
else; no click and no key, for every row, as before. The new
`test_a_member_root_with_no_marker_is_counted_and_refused_untouched` pins
that: exactly those three selectors, `address_not_admitted` (terminal), the
counts named in `self_evidence`, no address in it. The alternative -- the
CALLER hands the gate a reading -- was rejected on this module's own ground:
a basis a caller can assert is a basis a caller can invent.

**MUTATIONS** of `self_profile.py`, each run against the new test file on a
scratch copy of the tree (never this worktree):

| mutation | failed |
|---|---|
| any member profile root with no marker is self ("any profile under /in/") | 9 -- every control: another member's profile admitted by the editor gate, the activity reader, the census veto, the press gate and the harness |
| the relation dropped (an edit route under ANY member's path counts as the landed member's) | 1 -- the measurement test (the re-landed landing reads 4/4/4) |
| the veto dropped (edit routes for another member no longer refuse) | 3 |
| the accessible name dropped | 0, on the first run |

**THE ZERO WAS A MISSING CONTROL, AND IT IS ADDED.** Every capture's edit
routes are named, so nothing in the suite could tell an edit CONTROL from a
plain link to an editor. The rule exists for exactly that: a member's own text
linking to their own editor must establish nothing. The control now in the
measurement test, the editor gate's refusals and the press gate's: another
member's real profile carrying `<a href=".../in/x/edit/intro/">` named only by
its text -- read 0/1/0, refused everywhere. The rerun: 3 failed, the press
gate admitting that profile among them. Green: 44 passed.

**THE PEOPLE GUARD MET A NEW SLOT SHAPE IN THE NEW MARKUP, AND THE SLOT WAS
NARROWED, NOT THE FIXTURE -- TWICE, IDENTICALLY.** With the fixture staged,
`tests/test_fixtures_hold_only_synthetic_people.py` refused it: 9 member links
whose aria-label "matches no template", all one value. Opened at the lines it
named: each post's Send control, drawn in the new markup as an `<a>` to the
author's profile labelled exactly `Send` -- a word the guard already declares
interface text (`MEMBER_LINK_INTERFACE_WORDS`, measured 2026-09-28 as TEXT
inside member links), arriving in the label slot instead. The guard's own
remedy is "narrow the slot rule; never declare interface text a person", so the
label slot now skips those same words compared whole and exactly, with the
measurement recorded beside the set. Two tests: the skip as the capture draws
it (and the link's text slot still read), and
`test_THIS_CONTROL_CAN_FAIL_an_interface_label_is_exact` -- a name in the
label, or a label that only CONTAINS an interface word, is taken whole and
convicted as before. Red first: the unnarrowed guard refused the real fixture
(the run above). The live lane met the same 27 sites in its own session-11
copies and landed the SAME one-line narrowing on master, with its own control;
at the merge of 7760a5f this lane took master's file whole and dropped its
duplicate tests -- one narrowing, one control.

**AND ONE OF MY OWN TEST INPUTS WAS SLUG-SHAPED.** After the first commit,
`tests/test_no_committed_identity.py` (which reads the committed blob) refused
the new test file: one linkedin-slug hit, the member-root guard's
percent-encoded input -- four characters of the slug alphabet (an `x` and an
encoded quote) before a bracket. Described, not quoted, here: quoted, this
record would carry the same hit. It names nobody, and the rule is on the
shape, not on intent; the input is now `/in/x]y/`, which tests the same
refusal (a segment outside the closed alphabet) and is not slug-shaped. The pre-commit gate (exact values: 226
spellings, 0 hits) could not have caught it; the shape guard did.

**THE SCOPED GATES, on the fix, no live session on the box:** the new file 44
passed (37.5 s); `tests/test_activity_items.py`, `test_editor_fields.py`,
`test_editor_values.py` 142 passed (58.9 s); `test_press.py` with the
reader-leak guard's driven-set, vacuous-reader and drive tests 159 passed
(81.7 s); `test_live_lane_session_2_harness.py`, `test_surface_census.py`,
`test_tool_envelopes_emit_no_page_string.py` 331 passed (2 min 13 s -- three
whole files in one step, over the 2-minute line by 13 s); `test_readonly.py`,
`test_navigation_is_never_derived.py`, `test_every_orphan_module_is_ruled.py`,
`test_server_surface.py`, the press-gate files, `test_reader_reachability.py`,
`test_the_tool_surface_is_pinned_so_a_row_must_move.py`,
`test_no_message_publishes_a_landing.py` 1,532 passed and 1 skipped -- with one
failure, the press row described above, before it was narrowed.
`scripts/census_completion.py`: every headline figure matches its pin. The
three derived views: see section 7.

---

## 5. Census: no row moved here; the rows the fix affects

**NO CENSUS FILE WAS EDITED** -- the integrator owns the rows. The fix is code
aimed at real captured markup (session 11's landing) and has returned no live
payload, so by the census's own bar it re-proves nothing live. The rows whose
evidence runs through the gates that refused his profile from 2026-11-25:

| row | slice | state now | how this fix touches it |
|---|---|---|---|
| C41 View your own activity feed | messaging-and-content | COVERED-PROVEN (2026-09-23) | its tool, `linkedin_my_activity_items`, refused his profile live on 2026-11-25 (C1); offline on the real landing it reads again. A live re-proof is owed: one `/in/me/` load |
| C42 Address a specific post by identifier (precondition for C25, C32, C34) | messaging-and-content | GAP | rests on the item keys C41's tool returns and on the census `feed_item` veto -- both refused; both restored offline |
| C8 Save profile as a PDF | profile | GAP | the press on the top card's More/Resources opener goes through `press.self_landing` (the live harness's `_in_me_more`), which refused the landing; restored offline |
| the tool table's `linkedin_profile_editor_fields`, `linkedin_profile_editor_values`, `linkedin_my_activity_items` | profile; `mcp-inventory.md` rows 20, 21, 22 (PROVEN-LIVE) | as recorded | every one refused his profile live from 2026-11-25; restored offline |

Not affected, checked: the profile-edit write rows (A8, A19, A21, A22 and the
rest) -- `writes._assert_landed_on_target` never read the marker, and the write
path does not use the self-profile loader.

---

## 6. Questions for the orchestrator

1. **The press gate now READS before refusing one kind of page** -- a member
   profile root with no marker (three locator counts, no click, no key). Ground:
   the press module's rule is "every refusal a URL can predict is taken before
   the page is touched", and since 2026-11-25 this refusal is not
   url-predictable (his own landing has the same shape). One row of
   `test_a_refused_press_never_touches_the_page` was narrowed to admit exactly
   those three locators. If the ruling behind that rule reads "no locator at
   all", the alternative is the caller supplying the reading, which this module
   refuses on principle; I took the first and it is one function to revert.
2. **The live re-proof** of C41 (and of the editor gate) costs one `/in/me/`
   load in the next live session: it would confirm the structural signal live
   and show `self_signal: edit_controls` in the authorship block.

---

## 7. CI

**THE FIRST RUN WAS RED, AND THE CAUSE WAS MY SCOPING.** Run 45755740942 on
`fa11407` (the fix and this record over 4c62196), read by sha through
`scripts/lane_ci.py wait`: failure, shard 1, `2 failed, 4728 passed, 2 skipped`.
The two tests, from the run's own failed log:

* `tests/test_readers_emit_no_page_string.py::test_every_drive_has_its_premise_broken_below`
* `tests/test_readers_emit_no_page_string.py::test_a_drive_on_a_fixture_that_stopped_drawing_its_shape_raises[self_profile:read_edit_routes]`

Every drive in `tests/shipped_drives.py` must have its fixture premise broken in
`FIXTURE_BREAKS` -- a needle that, replaced, makes the drive raise rather than
measure a page nobody draws. This lane added a drive and no break. Its local
gate ran three tests of the guard that owns the table (the driven set, the
vacuous readers, the drive's own verdict) and not the fourth that enumerates
it. The fix is the entry: the four `/in/x/edit/` routes of the landing, replaced,
leave the drive nothing to transcribe and it raises. The scoped gate for the
second run is the guard's whole file.

    A TABLE'S COMPLETENESS IS TESTED WHERE THE TABLE IS OWNED. A SCOPED GATE
    THAT ADDS A ROW RUNS THE WHOLE FILE THAT ENUMERATES THE ROWS.

**MASTER MOVED** to 7760a5f (integration 3: four lanes, session 11's records,
41 rulings) before the second run. Merged into this branch: five conflicts,
resolved by id -- `tests/shipped_drives.py` (master's follower-list drive and
this lane's edit-route drive, both kept); `_audit/INSTRUMENTS.md` (master's
99-103, then 104, in number order); the people guard (master's file whole, see
section 4); `_audit/INDEX.md` and `_audit/RULINGS.md` (master's, then each
regenerated by its own `--write`; the blocker map too, unchanged in content).
`linkedin_server/server.py` and `tests/reader_leak_baseline.json` merged
cleanly. The duplicate fixture was removed and the tests repointed at the live
lane's byte-identical copy (section 4).

**CERTIFIED: `7732686`** -- the merge of master 7760a5f (`06abacc`) and the premise-break fix (`7732686`) over the fix and this record, on `ci/worktree-agent-selfprofile26`, run 45778142645, read by sha through `scripts/lane_ci.py wait`: success, all four test shards, 9 min 26 s wall. The push's own sweep: 0 hits across 1,258 blobs, 226 needles; the pre-commit gate on every commit: 0 hits against 226 spellings. The scoped gates on the merged tree before the push: the reader-leak guard's whole file 812 passed (74.8 s); the new file, `test_press.py` and `test_activity_items.py` 235 passed (37.0 s); the editor files, `test_server_surface.py`, `test_readonly.py`, `test_navigation_is_never_derived.py` and the live-harness file 1,424 passed, 1 skipped (103.0 s); the outside-dom reader inventory 6 passed; the three derived views match.

The commit that writes this paragraph changes only this file, and the lane holds for integration 4.
