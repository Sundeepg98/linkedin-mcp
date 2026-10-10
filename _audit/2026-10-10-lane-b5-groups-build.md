# Lane B5, 2026-10-10: the groups build

Build lane B5 (`lb5-groups-build`) of the census, briefed by the orchestrator at
15:18 IST on nine rows lane K's ledger (`_audit/_census/next-step.tsv`) marked
`next=BUILD`: the group home (`N 63`, `N 163`, `N 168`, `N 197`; `M C61`,
`M C64`, `M C69`) and the group members list (`N 165`, `N 177`). Standing rules:
`_state/LANE-STANDING-RULES.md` (gitignored). Offline throughout: no LinkedIn
load, no port 9224, no Chrome started or stopped.

## 1. What moved, and what did not

| row | from | to | on |
|---|---|---|---|
| `N 165` view the member list of a group he belongs to | GAP | COVERED-UNFIRED | `linkedin_group_members`, built over the live skeleton of a member list |
| `N 177` find people he knows through shared group membership | GAP | COVERED-UNFIRED | the same read: each member's degree as LinkedIn draws it; he knows the `1st` ones |
| `N 197` copy a group's link | GAP | COVERED-UNFIRED | CALLER-COMPOSITION-UNDER-D6: `linkedin_group_memberships` -> `linkedin_group_page`'s new `group_link` |
| `N 63`, `M C61` join a group | GAP | GAP | the capture draws no join control for its own group (section 4.1) |
| `N 163` request to join | GAP | GAP | the capture draws no request control (section 4.2) |
| `N 168`, `M C69` invite connections to a group | GAP | GAP | trigger captured; the dialog it opens is not (section 4.3) |
| `M C64` post in a group | GAP | GAP | trigger captured; the group composer is not (section 4.4) |

None is PROVEN: nothing was fired. Each moved row's cell says so and names this
record.

## 2. What was built

### 2.1 `linkedin_server/group_roster.py` and `linkedin_group_members(group_id)`

ONE page of a group's member list, as people records. The address is
`member_rosters.compose("group_members", <digits>)` -- the roster line
`MEMBER-ROSTERS-AS-BOUNDED-READS` admitted on 2026-09-24 -- and the tool reads
nothing unless the landing is that group's member list
(`group_roster.landed_on_the_members_page`: host LinkedIn, path exactly
`groups/<same digits>/members`). A group whose members LinkedIn does not show
him lands elsewhere; the tool then returns no people and says why, and never
publishes the landing.

THE CAPTURE. The live lane's session 2 (2026-09-28) tracked one member list as
`tests/fixtures/live2/group_members.html`. Measured on all 20 rows, not a
sample: one list (`ul.groups-members-list__results-list`, labelled `Members`);
each row (`li.groups-members-list__typeahead-result`) holds exactly one member
link (`a.ui-entity-action-row__link`) and inside it the name
(`.artdeco-entity-lockup__title`, its own text), the headline
(`.artdeco-entity-lockup__subtitle`, on all 20) and the visible degree
(`.artdeco-entity-lockup__degree`, on 16; 4 rows draw an empty badge) beside its
screen-reader copy (`.a11y-text`); beside the link, a `Message` button whose
label carries the member's name; after the list, a finite-scroll load button.
These classes are LinkedIn's component names, not generated hashes.

WHAT IS READ: the link's href (canonical profile link), the name, the headline
and the degree -- the four declared fields of `people_data.Person`. NEVER READ:
the screen-reader copy, the Message button and its label, the presence text,
the photo's alt, a badge icon's label, the group's title above the list, the
search box. The load button is counted (`more_members_control_drawn`) and never
pressed; nothing scrolls; at most `MAX_ROWS_READ` (25) rows are tried, above the
capture's 20.

THE SIX PEOPLE-DATA-MITIGATIONS, each in `tests/test_group_members.py`, each with
a control that fails:

| mitigation | the check | its control |
|---|---|---|
| 1 declared fields only | every envelope's keys are `PERSON_SHAPE`, the payload is `people` + `people_denominators` | (shape test; the record type refuses an extra field by construction) |
| 2 sanitised and marked | a name laced with a zero-width space and a right-to-left override comes back clean; every record carries the untrusted marker | `test_THIS_CONTROL_CAN_FAIL_the_lace_really_reached_the_page`: the raw title held both characters |
| 3 never stored | no module-level container, no file, print or logger call (AST); a failure counted by TYPE, never quoted | the shipped `containers_written_at_module_level` plants (people-search file) |
| 4 bounded | 40 distinct rows drawn, 25 read; only finds and reads are awaited; the load button pressed 0 times, the page did not move | `test_THIS_CONTROL_CAN_FAIL_a_press_or_a_scroll_is_refused` (click, wheel, scroll plants caught) |
| 5 visible only | a hidden row is skipped as `not_visible`; a member drawn `LinkedIn Member` stays that | -- |
| 6 not a target | no write tool reaches the reader through any helper; the one importer is `server.py` | `test_THIS_CONTROL_CAN_FAIL_a_write_tool_behind_a_helper_is_found` |

And the leak check over the whole payload: a needle is planted in every
never-read place (seven), and none crosses -- with its control,
`test_THIS_CONTROL_CAN_FAIL_a_reader_aimed_at_the_badge_carries_the_screen_reader_copy`:
aim the headline at the badge's screen-reader copy and the needle crosses.

HOW THE TESTS RUN. No new fixture is committed. Each scenario loads the TRACKED
skeleton into a local headless Chromium with every request aborted, fills
synthetic people into the person slots (the declared `someone-example` slugs,
`Example Member NN`, `Synthetic headline NN`), plants the needles, and runs the
reader or the tool. All scenarios share one browser launch: a launch per test
cost 254 s for this file; shared, 69 s (44 tests).

### 2.2 `group_link` on `linkedin_group_page` (N 197)

`group_page.group_link(identifier, same_group)` returns
`https://www.linkedin.com/groups/<digits>/` -- `group_page_url`'s address for the
caller's own digits -- ONLY when `same_group` is True, i.e. the navigation to
that address landed on a page whose group id reduced to the same digits. Any
other landing returns `None`; the landing is never published. No parameter was
added, so the tool surface's parameter pin moved by one only for the new tool.
Three tests in section 5 of `tests/test_group_members.py`, over the live
skeleton of a group page: same group -> the link; the feed or another group ->
`None`, the other group's id nowhere in the envelope.

### 2.3 Red first

- On the base tree (`f93104c`), with only `tests/test_group_members.py` added:
  collection fails, `ImportError: cannot import name 'group_roster' from
  'linkedin_server'` (1 error, 0 tests run).
- With the build: 44 passed. The controls above are the per-guard reds.
- The page-string guards: `tests/reader_leak_baseline.json` regenerated (186
  readers): `group_roster:read_group_members` is
  `not_driven:reaches a people-record builder and built no record` -- the
  generic planted page's hrefs are not member links, so its one row is skipped
  as `no_member_link`; the leak evidence for this reader is the needle run over
  the real skeleton above. `tests/tool_envelope_baseline.json`:
  `linkedin_group_members` is `not_driven:never read the page`.

### 2.4 Sites that moved with the surface

`tests/test_every_tool_is_on_the_surface.py` (62), `tests/test_server_surface.py`
(62 tools, 45 non-write, the headline, the test's name),
`tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py` (62 tools, 98
parameters, with the census decision), `people_data.PEOPLE_TOOLS`,
`tests/test_every_orphan_module_is_ruled.py` (the `member_rosters` entry deleted
on its own instruction), `tests/test_member_rosters.py` (its section 6 now
asserts the one importer), `member_rosters.py`'s docstring.

## 3. The census

Pins re-derived on the measured values `scripts/census_completion.py` printed,
never by hand. On the lane's branch over master `f93104c`: `adjudicated` 186 ->
189, `delivered_broad` 130 -> 133, `gap` 585 -> 582, `gap_read` 98 -> 95,
`unfired` 21 -> 24, `b1_no_ruling` 9 -> 12. RE-DERIVED AT THE MERGE OF MASTER
`0103810` (lane U's attachments, lane K's rulings applied), on the merged
tree: `adjudicated` 216, `delivered_broad` 138, `gap` 555, `gap_read` 89,
`unfired` 27, `b3_admitted` 38 (master's 213, 135, 558, 92, 24 and 41 with this
lane's three rows), `b1_no_ruling` 12. `N 165`, `N 177` and `N 197` join
`PINNED_B1_ROWS[NO_RULING]` (reads no ruling holds), and
`tests/test_a_covered_row_names_the_artifact_that_covers_it.py` pins the three
at COVERED-UNFIRED with the chain they rest on (shown failing on a renamed
copy), so an unannounced promotion goes red. The three leave `read-addresses.tsv` (bucket 3) and `next-step.tsv`
(GAP rows only) -- each table's checker went red naming them and is green after.
Derived views regenerated: `_audit/INDEX.md`, `_audit/RULINGS.md`,
`_audit/_census/blocker-map.tsv`.

## 4. The six rows left GAP, each with its exact reason

`tests/fixtures/live2/group_home.html`, the capture lane K queued all seven
group-home rows on (basis INFERRED), counted 2026-10-10 by a stdlib parse of the
skeleton:

- it is a MEMBER's view: one closed share box
  (`share-box-feed-entry__closed-share-box`, 4 buttons), one invite control
  (`button[data-test-invite-connections-cta]`), the group's action menu
  (`groups-action-dropdown__trigger`, 3 closed items, labels blanked), a Share
  menu, and a link to the members tab;
- it draws NO join or request control for its own group;
- its 5 `Join` buttons (`groups-recommendations__item-join-button`) are all
  inside the 5 rows of the recommendations rail, one per row, each row carrying
  one OTHER group's anchor;
- it draws 0 dialogs.

### 4.1 `N 63`, `M C61` -- join

A join fired at a group he names presses that group's own control, drawn on its
page for a NON-member. No such page has been captured, so a build aimed there
would rest on synthetic markup, which moves no row. BLOCKER: capture **C-B5-1**.
The inverse is already built (`linkedin_withdraw_from_group`, `N 64`, `M C63`).

### 4.2 `N 163` -- request to join

The request control is drawn on an approval-gated group's page for a
non-member: not captured. BLOCKER: capture **C-B5-2**. AND ITS INVERSE CANNOT BE
BUILT IN THE SAME CHANGE BEFORE A REQUEST EXISTS: withdrawing a pending request
(`M C62`) presses a control drawn only on a pending request, so that capture is
taken right after the first request he names, and no request is fired before
its withdrawal is built on it.

### 4.3 `N 168`, `M C69` -- invite connections

The trigger is captured; the dialog it opens -- where the connection he names is
chosen and the invitation sent -- is not. BLOCKER: capture **C-B5-3**. Whether a
sent group invitation can be withdrawn is unmeasured.

### 4.4 `M C64` -- post in a group

The trigger (the closed share box) is captured; the composer it opens inside a
group is not, and the shipped `linkedin_publish_post` loads `/preload/sharebox/`,
the feed's own composer, which cannot be aimed at a group. BLOCKER: capture
**C-B5-4**. Its undo is deleting his own post (`outward_classes`
`delete_own_post`, NEEDS-CAPTURE).

### 4.5 The capture specs (for the live lane's queue; lane K owns the queue)

Each is ONE load inside `LIVE-BUDGET-40-LOADS`, and every page kept as a
skeleton only (pages here show other people). The group ids are his to name
and are never written to a tracked file.

| id | rows | load | press | keep |
|---|---|---|---|---|
| C-B5-1 | N 63, M C61 | `/groups/<id>/` of an OPEN group he names and does not belong to | none | the header region's skeleton; whether a control named exactly `Join` is drawn there, and where |
| C-B5-2 | N 163 (then M C62) | `/groups/<id>/` of an APPROVAL-GATED group he names and does not belong to | none | the header's skeleton; whether a request control is drawn, its exact label |
| C-B5-3 | N 168, M C69 | `/groups/<id>/` of a group he belongs to | the invite control, as a disclosure (CAPTURE-PRESS-UNDER-PROBE-RULE); then, if the dialog draws a search box, the name of ONE connection he names typed into it | the dialog's skeleton before and after typing (per row: the member link, the selection control, the send control); Escape; record that nothing was selected and no confirmation appeared |
| C-B5-4 | M C64 | `/groups/<id>/` of a group he belongs to | the share box's trigger (opens the composer; nothing typed) | the composer dialog's skeleton: its audience line, the editor, the Post control, the close control; closed with nothing typed; record whether a discard prompt appeared |

## 5. LIVE-PROOF SPECS for the moved rows

All three are READS: no grant, no inverse. Records hold counts, booleans and
hashes -- never a member's name, headline, slug or a group id
(PEOPLE-DATA-MITIGATIONS 3).

**`N 165` -- `linkedin_group_members(group_id=<a group he belongs to>)`.** Loads:
1 (the id from the live lane's own state of a group his memberships returned; 3
more if it must come from a fresh `linkedin_group_memberships`, which brackets
on the feed). Banks PROVEN when: `ok` True, `pages_loaded` 1,
`landed_on_the_members_page` True, `people_returned` > 0 and equal to
`rows_attempted` minus the skips, `failed` empty, every record carrying exactly
the four fields and the marker. Recorded: the denominators, and
`more_members_control_drawn`. STOP-ALL: a landing that is not the member list;
an authwall; any restriction, warning or rate-limit interstitial after the load
(the ruling's own reopener); any `failed` entry. Never pressed: the load button;
never repeated for a second page.

**`N 177` -- the same fire.** Banks PROVEN when, in addition, at least one
returned member has `degree` `1st` (the count recorded, not who). If the group
draws no first-degree member, `N 177` stays UNFIRED with the count recorded
(a zero cannot say whether the reader or the group is empty), and the next
fire takes a group he names with a connection in it.

**`N 197` -- `linkedin_group_page(group_id=<a group he belongs to>)`.** Loads: 1.
Banks PROVEN when `landed_on_the_same_group` is True and `group_link` equals the
address composed from the id he passed (recorded as a boolean, and the id's hash).
The composition's first part, `linkedin_group_memberships`, is already PROVEN
(`N 173`). STOP-ALL: an authwall or a landing elsewhere; `group_link` non-null on
a landing that was not the same group (a defect: stop and report).

## 6. Questions for the orchestrator

1. **A join route that IS captured.** `group_home.html` draws a `Join` button on
   each recommendation row of a group page, each row carrying exactly one group
   anchor. A write `join` taking the group to join and a group page he names on
   which it is recommended could be built today on real markup, its inverse
   already built. Does joining a group LinkedIn recommends discharge `N 63` /
   `M C61` (D6), or only a join from the group's own page (C-B5-1)? Ground:
   section 4 counts; the row's own text, "Join a LinkedIn group".
2. **C-B5-4 presses a composer trigger.** CAPTURE-PRESS-UNDER-PROBE-RULE lists
   "a menu, a folder, a filter panel, or a list" and types only into a SEARCH box,
   "never a composer or an editor". Opening a composer with nothing typed is the
   question ARTICLE-COMPOSER-CAPTURE answered for `/article/new/`; is the group
   composer's opening permitted the same way?
3. **C-B5-3 opens a dialog listing his connections and types a name into its
   filter.** Is that dialog "a list" under CAPTURE-PRESS-UNDER-PROBE-RULE, and
   its filter "a SEARCH box"?
4. **The ledger's next step for the six rows left GAP.** They keep
   `next=BUILD:tests/fixtures/live2/group_home.html` in `next-step.tsv`, which
   section 4 shows that capture cannot serve; each now needs
   `CAPTURE:C-B5-1..4` (section 4.5) and a line in `capture-queue.tsv`, whose
   verdicts lane K's generator re-drives -- so the re-queue is lane K's, not
   written here. (CALLER-COMPOSITION-UNDER-D6, which `N 197`'s cell cites, came
   onto this branch registered with master `0103810`.)

## 7. Gates

- `tests/test_group_members.py`: 44 passed (69 s), serially, no live session
  running at any run (the flag file checked before each).
- Touched tests and their direct importers (`test_no_committed_identity`,
  `test_every_tool_is_on_the_surface`, `test_server_surface`,
  `test_the_tool_surface_is_pinned_so_a_row_must_move`,
  `test_every_orphan_module_is_ruled`, `test_member_rosters`, `test_group_page`,
  `test_a_people_reader_reads_one_page`): 1488 passed, 1 failed -- the server
  surface's headline, still "sixty-one" -- fixed in the census commit.
- Census instruments: `census_completion.py` "every headline figure matches its
  pin"; `check_read_addresses.py` GREEN 95 of 95; `check_next_step.py` GREEN
  (582); `check_write_classes.py`, `check_jobs_directions.py`, `ruling_holds.py`
  GREEN.
- On the tree merged with master `2b165fd`: `tests/test_group_members.py`,
  `test_the_tool_surface_is_pinned_so_a_row_must_move` and
  `test_every_tool_is_on_the_surface`: 129 passed (132 s); every census checker
  above GREEN again (`check_read_addresses` 89 of 89, `check_next_step` 555).
- The full suite runs on CI (section 8).

## 8. Merges and certification

- Merged `origin/master` `0103810` (lane U's `linkedin_send_attachment`, lane
  K's ledger rulings and census moves): nine files conflicted, each resolved by
  measurement -- the tool surface read off the merged registry (63 tools, 101
  parameters, 45 reads), the census pins printed on the merged tree,
  `network.md`'s `N 197` beside lane K's `N 198` exclusion, `next-step.tsv`
  keeping lane K's `N 178` and dropping `N 177`, `N 197` and the excluded
  `N 198`, INSTRUMENTS keeping lane U's section 84 and this lane's 93, and
  the derived views and both page-string baselines regenerated. Then
  `2b165fd` (lane G2's record conversions), clean.
- CI, first push: `3b66370` to `ci/worktree-agent-a4cc861612983721b`, run
  `38047812344`: RED, 9 failures in 3 of 4 shards, each a site this lane had
  not moved, none a regression of a shipped behaviour: the reader-triage table
  (the new reader named in `WHAT_WOULD_DRIVE_IT`), the correction-pair guard
  (two table-row proximities declared on `NOT_A_CORRECTION`), the server
  instructions' people-tool list, README's headline and module listing, the
  server docstring's headline, and the pointer-graph guard with its two
  self-tests (`M C64`'s new note read as an ACCOUNT-FACT through the words
  "his own", which re-classified the argument `M C65` and `M C66` inherit;
  reworded, and the guard reads PASS on all 64 pinned pointers).
- CI, second push: the run named in the lane's final message.

## 9. The cold review, and what changed on it

One cold reviewer (a child, read-only, never warm to this build) answered seven
questions against `466c230` / `45592c0`: 1 DEFECT, 9 GAP, 7 OK. Dispositions:

| finding | disposition |
|---|---|
| DEFECT: mitigation 3's static check let `Path(...).open("w")` + `json.dump` through, with no control | FIXED: `stores_anything` reads imports of writers, writing names and writing methods; four plants each caught, the reviewer's first |
| GAP: a screen-reader-only span inside the headline crossed | FIXED: the headline is held to the name's nested-text rule -- ABSENT and counted, never read with the child |
| GAP: mitigation 5's per-field visibility check had no control | FIXED: a hidden name alone (row skipped `not_visible`) and a hidden headline alone (ABSENT, counted) |
| GAP: `group_link` published on a blank page at the same address (`reader_blind`) | FIXED: it publishes only on reach `feed_drawn` or `ambiguous`; a blank page and three other states withhold it |
| GAP: `landed_on_the_same_group` does not check the host | NOT CHANGED: shared with `N 175`'s shipped reader; the members-page check this lane wrote does check it. Named for the owner of `group_page` |
| GAP: `N 165` asks for the FULL list; the read is one page | KEPT, by the ruling: MEMBER-ROSTERS-AS-BOUNDED-READS admits a roster as one page per call and names `N 165` among the rows it governs; the cell says the bound is the row's limit |
| GAP: "a needle in every place" overclaimed (the search box has none) | FIXED in the cell: seven places, named |
| GAP: no DELTA block in `network.md` | ADDED, re-derived with `count_census_states.py` |
| GAP: the shared leak guards never drive this reader | KEPT, stated: `WHAT_WOULD_DRIVE_IT` names the skeleton drive in `tests/test_group_members.py` |
| GAP: `tests/test_group_members.py` over two minutes on a loaded box | NOTED: one browser launch for the file; 69 s on a quiet box |
| OK x7 | mitigations 1, 2, 4, 6; no named place leaks; no press, scroll or second load; `group_link` only ever the caller's digits; the six GAP reasons true of the skeleton |
