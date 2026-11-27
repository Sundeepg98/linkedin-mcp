# Integration 7, 2026-11-27: the five wave-7 lanes onto master 68a4ff7, and the wave's rulings

Integrator lane `integrator7`, worktree branch `integration7` from master
`68a4ff7` (integration 6's head; master CI 45949625879 green on it). Task:
merge the certified heads of prof7, jobs7, msg7, settings7 and net7, each
`--no-ff`, in that order; register the wave's rulings; apply two of them;
re-derive every pin; one lane CI run on the combined head, read by sha. The
orchestrator fast-forwards master; this lane never touches it.

Offline throughout: no LinkedIn load, no port 9224, no Chrome. Scratch tools,
commit messages and gate outputs sat in the main checkout's gitignored lane
scratch. This record and its rulings record were drafted there as the work
went, and placed at their `_audit/` paths at the registration commit, so no
untracked document sat under `_audit/` during a merge.

Pattern read: integration 6's record and rulings record (its section 2 is the
method), and the cross-lane critic's report over the five heads, which was
this merge's map. Every figure the critic gave was re-measured here on the
merged tree; where this record differs, it says so and why.

## 1. The heads, each read by sha

Every head descends from `68a4ff7`, the merge-base with master (measured).

| # | lane | head merged | certified sha, lane CI run (by sha) | what it brings |
|---|---|---|---|---|
| 1 | prof7 | 754bf9a | 4f84353, 45994909996 success, 6 of 6 | SELF-LOADER (`self_profile.await_rewrite`); his volunteering page's drawn spelling admitted, its id from his arguments only; THE one exact matcher (EXACT-MATCH-REFUSES-ANY-WHITESPACE); nine cells re-aimed for session 14; no row moves |
| 2 | jobs7 | 891a520 | 891a520, 45994206737 success, 6 of 6 | the AI job search as the keyword search's own route; refuse before load on a retired route; J 31's AI arm; the Insights tables read by their summaries; the Products tab; J 1, J 20, J 40, J 31, J 169 GAP -> COVERED-UNFIRED, J 174 new at COVERED-UNFIRED, J 171-J 173 and J 175 new at GAP; the Learning saved list admitted |
| 3 | msg7 | 7e9f61b | 7e9f61b, 45996312582 success, 6 of 6 | `linkedin_save_post`, its receipt a change against a baseline (SAVE-RECEIPT-NEEDS-A-CHANGE); the notifications page's server-driven read; M C36 GAP -> COVERED-UNFIRED, M C75 COVERED-PROVEN -> COVERED-UNFIRED, M C70 GAP -> MEASURED-ABSENT; his saved-posts list admitted |
| 4 | settings7 | 95123f6 | ef3b703, 46015381304 success, 6 of 6 | his Verifications and Manage Premium account pages read (`linkedin_my_verifications`, `linkedin_my_premium_account`); his search history, data-download and contact-syncing pages admitted by name; P K1 and P N22's subscription half GAP -> COVERED-UNFIRED, P N32 new at GAP (P-N22-SPLITS); P I12 and P I13 re-measured on the Preferences dialog their load drew |
| 5 | net7 | fc38e7f | 252c20f, 46001861886 success, 6 of 6 | four people-search facets (`followerOf`, `schoolFilter`, `industry`, `activelyHiring`) and his Premium networking matches (`linkedin_premium_matches`); N 82, N 86, N 88, N 89, N 26b and N 199 GAP -> COVERED-UNFIRED, N 93 and N 27 GAP -> MEASURED-ABSENT; `/mynetwork/discovery-see-all/` and the received tab's leaf admitted; the curation receipt reads a change (FEED-CURATION-RECEIPT-NEEDS-A-CHANGE) |

PROF7. Its branch head `754bf9a` stands on the certified `4f84353`, and
`git diff --stat 4f84353 754bf9a` reads one file, `_audit/2026-11-27-prof7.md`
(18 insertions, 15 deletions): record-only, so `754bf9a` is the head merged,
as the brief orders. `4f84353` supersedes `3236dfb`, the sha the cold
verifier read; its fix is EXACT-MATCH-REFUSES-ANY-WHITESPACE, the verifier's
MAJOR.

JOBS7. `891a520` supersedes `b3d5341`, the sha the cold verifier read: three
files of text (its record, `J 1`'s cell, `job_search_route.py`'s
docstrings), the verifier's MINOR.

MSG7. `7e9f61b` supersedes `5beac57`, the sha the cold verifier read:
SAVE-RECEIPT-NEEDS-A-CHANGE (the verifier's finding 2), the notifications
`side_effect` text (finding 3) and the corrected claims (finding 1).

SETTINGS7. The orchestrator's disk note `_TEAM_LEAD_settings7.md` (headed
20:06 IST) named the head: `95123f6`, record-only over the certified
`ef3b703`, whose lane CI 46015381304 succeeded; merge it fourth. Read here by
sha at 20:06: run 46015381304, headSha `ef3b703` in full, branch
`ci/settings7`, completed success, 6 of 6 jobs; `95123f6`'s only parent is
`ef3b703` and `git diff --stat ef3b703 95123f6` reads
`_audit/2026-11-27-settings7.md` alone (41 insertions, 2 deletions); it
descends from `68a4ff7`. Deleted at 20:06:11 as the ack, a copy kept in this
lane's scratch. `ef3b703` supersedes `a8c5da1` (the sha the cold verifier
read, whose P I12 / P I13 premise it REFUTED) and `ce96fda`: the two cells
re-measured on the Preferences dialog their load drew, queue line 73 dropped
and line 24 grown to 13 rows, J 87's absence narrowed to the measured labels,
and `verifications_page._consent` naming two sections and a failed count
instead of None (the verifier's F1 to F3).

NET7. The orchestrator's disk note `_TEAM_LEAD_net7.md` (headed 18:32 IST)
named the head: `252c20f`, certified after its fix round
(FEED-CURATION-RECEIPT-NEEDS-A-CHANGE), lane CI 46001861886, its branch head
`fc38e7f` record-only on top, to be merged LAST, after settings7. Read here
by sha at 18:32: run 46001861886, headSha `252c20f`, completed success, 6 of 6
jobs; `git diff --stat 252c20f fc38e7f` reads `_audit/2026-11-27-net7.md`
alone (33 insertions, 11 deletions); `fc38e7f` descends from `68a4ff7`. The
note was copied to this lane's scratch and deleted at 18:32:30 as the ack; the
merge commit is the receipt. `252c20f` supersedes `09bac99` (the sha the cold
verifier read) and `e4f6238`.

## 2. The merges, and the conflicts resolved by judgement

Method on every merge, integration 6's: `git merge --no-ff --no-commit`; the
derived views (`_audit/INDEX.md`, `_audit/RULINGS.md`,
`_audit/_census/blocker-map.tsv`) taken from this side and regenerated by
their own `--write` to a fixed point (two passes), never by hand; the census
tables merged BY KEY from the three blobs, never by hunk, and a table git
merged clean compared against the keyed merge; then the three `--check`s,
`census_completion.py --check`, the six table checkers and
`check_cited_shas_resolve.py`, all green before each commit. Each pin both
sides moved is SET to what `--check` measured on the merged tree; every count
in prose or a test is measured on the merged tree (`readonly` imported,
`mcp.list_tools()`), never summed.

(merged 1, prof7 754bf9a, as 51243e7.) Conflict-free: HEAD was the merge
base, and the merged tree is byte-identical to `754bf9a`'s (`git write-tree`
52326ba against `754bf9a^{tree}`). The views regenerate to that same tree;
all eleven gates green. The committed-blob identity test on the clean tree
after the commit: 1390 passed in 55 s, run to its end before merge 2 touched
the tree (integration 6's lesson).

(merged 2, jobs7 891a520.) Seven files conflicted, measured first with
`git merge-tree --write-tree`.
- `next-step.tsv`: merged by key (the row id) from the three blobs. The one
  hunk was adjacent rows: `P L7` is prof7's re-aim, `P M1`, `P M3` and `P M4`
  jobs7's; no key was moved by both sides. 517 rows: 27 from prof7, 11 from
  jobs7, 4 added and 5 deleted by jobs7. `capture-queue.tsv` and
  `jobs-directions.tsv` merged clean, and each equals the keyed merge
  (asserted).
- INSTRUMENTS: the orchestrator's `resolve_instruments_order.py`, its own
  code run through integration 6's scratch wrapper so that it reads this
  worktree's file (in place it resolves the main checkout's, whose `git
  status` read unmodified after the run). Section 114 (jobs7) now precedes
  117 (prof7). The numbers were pre-assigned per lane, so none collides and
  none is renumbered.
- The lane-K ledger: the union, prof7's two questions
  (`Q-SELF-ROOT-FORM-LINKS`, `Q-VOLUNTEERING-ID-FROM-HIS-ARGUMENTS`) then
  jobs7's three (`Q-J169-SENIORITY`, `Q-J170-ROW-CONTROL`,
  `Q-LEARNING-SPLITS`); a containment check found every line either side
  added present (54 and 45 lines, 0 short).
- The read boundary's freeze, `tests/test_readonly_boundary_invariant.py`:
  both lanes re-froze `_ALLOWED_URL_PATTERNS` from the base's
  `5d3109ee0aa96e48`, prof7 to `10c0a7637b7c3ca8` and jobs7 to
  `efcaa36167e42ccf`. The merged `readonly.py` hashes to `a3510436178fb711`
  with the test's own `ast_digest`, and that is the only key moved from
  `68a4ff7`. ATTRIBUTED in value space: the merged list (103 entries) minus
  jobs7's one entry equals prof7's list and hashes to its digest, and minus
  prof7's one entry equals jobs7's. Both comment chains are kept verbatim,
  with one note naming the merged value.
- The messaging slice's allowlist cell: both lanes wrote **102** and "82
  were added", each naming its own line as the most recent. Measured on the
  merged tree, importing `linkedin_server.readonly`: **103** patterns, so
  "83 were added". THE CELL HAD GROWN PAST A GUARD'S WINDOW:
  `tests/test_the_census_prose_matches_the_boundary.py::test_the_reachable_surfaces_are_named_in_the_census`
  reads section 4's first 6000 characters for the reachable surfaces' names,
  and with both lanes' clauses `events` sat at 6159 (each lane alone: 5875
  and 5863). It failed once, on that. The cell now gives the two lines one
  clause, and admit5-26's five-line clause its ruling ids only, in lane
  settings7's own wording (settings7 shortened it the same way on its
  branch, for the same room); `events` sits at 5761, every ruling id and row
  id the clauses named still in the cell. The batch then passed (469 tests).
- INDEX.md, RULINGS.md and blocker-map.tsv regenerated; each `--check`
  clean (310 documents; 182 rulings; 409 map lines).
- `readonly.py`, `server.py`, `profile.md`, `capture-queue.tsv` and
  `reader_leak_baseline.json` merged clean. The baseline is valid JSON
  holding both lanes' keys (jobs7's four `company_tabs` readers beside
  prof7's).
- Committed as 01a2845. The committed-blob identity test on the clean tree
  after it: 1403 passed in 60 s.

(merged 3, msg7 7e9f61b.) Nine files conflicted, measured first with
`git merge-tree --write-tree`.
- `capture-queue.tsv`: merged by key (the surface id) and msg7's six new
  lines RENUMBERED, rank 142 -> 149 to 147 -> 154 (section 3). msg7 deleted
  five lines (`C-MSG26-1`, `C-MSG26-4`, `admit-search-results-content`,
  `comments-metric-spelling`, `feed-menus`), none of them moved by prof7 or
  jobs7, so each is deleted; no line was moved by both sides. 106 lines.
- INSTRUMENTS: ours held sections 114 and 117, msg7's side 116. The
  orchestrator's resolver orders the two SIDES by each one's first heading,
  which would have written 114, 117, 116; a scratch tool split both sides into
  their sections and wrote them in number order, 114, 116, 117. Containment:
  0 lines of either side short.
- The lane-K ledger: the union, prof7's and jobs7's five questions then
  msg7's six; 0 short.
- `census_completion.py`: seven pins both sides moved, each comment chain the
  union and each value SET to what `--check` measured on the merged tree:
  adjudicated 267, delivered_broad 178, gap 515, unfired 83, b1_no_ruling
  55, achievable 710, capabilities_achievable 723. (Cross-check only: each is
  the base plus both sides' measured moves, e.g. gap 518 - 1 - 2.) The pins
  that merged clean were right: `--check` named no other.
- The read boundary's freeze: `_ALLOWED_URL_PATTERNS` re-frozen to
  `947dcb23d73c0491` (104 entries), the only key moved from `68a4ff7`;
  attributed: minus msg7's entry it hashes to merge 2's `a3510436178fb711`,
  minus prof7's and jobs7's two to msg7's `3f12a2c2143c6576`.
- The messaging slice's section 4: the allowlist cell reads **104** patterns,
  "84 were added" (measured), the three wave-7 lines in one clause; the
  reachable-surfaces row is msg7's, which adds its sixth surface, saved
  posts (ours was the base's line).
- ONE LINE MERGED CLEAN AND WRONG: `server.py`'s docstring still read "One
  hundred and seven is ``len(await mcp.list_tools())``", citing
  `test_the_surface_is_exactly_the_one_hundred_and_seven_tools`, a test msg7
  had renamed on its own branch. Measured on the merged registry: 108 tools,
  164 parameters, `SANCTIONED_WRITES` 41, `PERFORMABLE` 36,
  `SANCTIONED_MUTATIONS` 22. It now reads one hundred and eight and cites the
  test by its name.
- `server.py`, `writes.py`, `readonly.py`, `profile.md`, `next-step.tsv` and
  `reader_leak_baseline.json` merged clean. `next-step.tsv` equals the keyed
  merge (asserted). A containment check on the code: `writes.py` 0 of 254
  added lines short, `readonly.py` 0 of 43; `server.py` reads one `)` short,
  which is one side removing one and msg7 adding one (base 59, ours 58, msg7 60, merged 59).
- Committed as c989546. Identity after it: 1409 passed in 43 s.

(merged 4, settings7 95123f6.) Nineteen files conflicted. Live session 13
raised the flag at 20:01:55; it was gone by the first test run (20:15), and
every run read it first and ran serially in the foreground.
- `server.py`: the end-of-file lane blocks rebuilt from the blobs, integration
  6's tool: after build-msg2's end marker, msg7's block (54 lines) then
  settings7's (86), each byte-identical to its side, then the base's `main()`.
  The three docstring hunks re-derived on the merged registry: 110 tools = 70
  read + 36 write + 4 write-shaped; msg7's `linkedin_save_post` the
  hundred-and-eighth, settings7's two reads the hundred-and-ninth and
  hundred-and-tenth (its branch counted them the 108th and 109th); the count
  sentence cites the renamed test. A containment check found only the
  rewritten count lines short.
- `readonly.py`: the union, msg7's saved-posts line then settings7's three
  admissions; it parses, and imports at 107 patterns and 18 pattern
  exemptions. The boundary freeze: `_ALLOWED_URL_PATTERNS` `18413e5f8838d54c`,
  attributed (minus settings7's three entries it hashes to merge 3's
  `947dcb23d73c0491`, minus the other lanes' three to settings7's
  `0c47f74920c44695`); `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS` merged clean at
  settings7's `59a59624d142d203`, which is the merged digest, only settings7
  having moved it.
- README, `test_server_surface.py`, `test_every_tool_is_on_the_surface.py`,
  `test_the_tool_surface_is_pinned_so_a_row_must_move.py`: 110 tools, 164
  parameters (settings7's two reads take none), 70 not in
  `SANCTIONED_WRITE_TOOLS`; the count-named test renamed
  `..._one_hundred_and_ten_tools`, both lanes' rename notes kept under it.
- `test_the_error_url_is_ruled_per_site.py`: the tally read off the merged
  `DECLARED` table, WITHHELD 26, ASKED_FOR 24, PASSTHROUGH 1, 51.
- `LIVE_FIXTURE_COUNTS`: `live12` 56 and `live11` 62, counted on disk.
- The population: 783 (J 174, P 238, M 155, N 216), `census_row_pin.json`
  regenerated by `pin_census_rows.py --write`, the two literal pins set to it.
- `census_completion.py`: eleven hunks (one of them comments only, its value
  line outside the hunk) and ten pins SET from `--check`: stated_rows 783,
  capabilities 796, capabilities_achievable 724, achievable 711, adjudicated
  269, delivered_broad 180, gap 514, unfired 85, b1_no_ruling 57, and
  gap_read 64. ONE MERGED CLEAN AND WRONG: gap_read, which both lanes moved
  66 -> 65 by different rows (msg7's `M C70` left GAP; settings7's `P K1` and
  `P N22` left and `P N32` entered), so the two equal lines merged as one 65.
- The messaging allowlist cell: BOTH sides read **104** and "84 were added",
  the same numbers by different lines, the equal-move trap in prose. Measured:
  107 and 87; the six wave-7 lines in one terse clause per lane.
- `capture-queue.tsv`: by key; settings7's six new lines renumbered 142-147 ->
  155-160 (section 3), its four deleted base lines deleted, its one moved line
  (24, the attended Open-to-Work editor, now 13 rows) taken.
- INSTRUMENTS: 114, 116, 117, 118 in number order, 0 lines short. The table
  checkers, `next-step.tsv` and `read-addresses.tsv` (each equal to its keyed
  merge) and the eleven gates green.
- Committed as 3f3dc74. Identity after it: 1424 passed in 72 s.

(merged 5, net7 fc38e7f, LAST.) Twenty files conflicted.
- `next-step.tsv`, `read-addresses.tsv`, `exclusion-basis.tsv`: merged by key
  from the three blobs, no key moved by both sides. `network.md`'s one hunk
  resolved row by row against the base (settings7's `N 96` beside net7's
  `N 97` and `N 98`), and all four slices checked row by row against the
  three blobs: 0 problems.
- `capture-queue.tsv`: by key, with net7's mirror of settings7's
  manage-syncing line COLLAPSED onto settings7's, as the critic and both lanes
  asked; the two differed in exactly two cells, the rank (145 against 158)
  and the address verdict (net7's branch refused the address it had not
  admitted). Its `needs` cell set to `-`. net7's one new line renumbered 142
  -> 161; net7's three deleted lines (`admit-mynetwork`,
  `admit-premium-matches`, `search-people-first-degree`) deleted.
- `read-addresses.tsv`: `N 32` NEEDS-SESSION -> ADMITTED at
  `https://www.linkedin.com/mynetwork/settings/manage-syncing` (both slash
  forms admitted, measured), the critic's section 6.4 finding: every lane left
  it, and no checker flagged it. Its gate MEASURE, its note citing settings7's
  admission and keeping the prior note.
- `server.py`: the tail rebuilt again (msg7 54 lines, settings7 86, net7 44);
  111 tools = 71 read + 36 write + 4 write-shaped, 168 parameters; net7's
  `linkedin_premium_matches` the hundred-and-eleventh (its branch counted it
  the 108th). README, the surface tests and the count-named test
  (`..._one_hundred_and_eleven_tools`) follow; 71 not in
  `SANCTIONED_WRITE_TOOLS`; 168 parameters pinned.
- `readonly.py` merged clean: 109 patterns, 19 pattern exemptions, 33
  forbidden substrings, the critic's figures; 0 lines of either side short.
  The freeze: `_ALLOWED_URL_PATTERNS` `311b43fe823f84e5` and
  `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS` `3fdfb5719f05d4b5`, each attributed
  both ways (minus net7's entries, the four lanes' values; minus the four
  lanes', net7's).
- ONE MORE MERGED CLEAN AND WRONG, the one the critic named:
  `test_job_alerts_read_boundary.py`'s exemption-count assert. Both lanes
  moved it 17 -> 18 with different comments; the comments conflicted, and the
  assert, outside the hunk, merged as one 18. Measured: 19.
- The error-url tally: 26, 25, 1, total 52 (the critic's DERIVED 52, measured).
- `census_completion.py`: thirteen hunks, `PINNED_B1_ROWS` the union, and
  twelve pins SET from `--check`: gap 506, adjudicated 277, delivered_broad
  186, unfired 91, achievable 709, capabilities_achievable 722, out_of_scope
  74, gap_read 56, b1_no_ruling 63, b3_admitted 32, b3_refused 17,
  b3_needs_session 5. The critic's merged headline, CONFIRMED by measurement,
  except b3_admitted 32 and b3_needs_session 5 against its 31 and 6: the
  `N 32` move, which the critic derived would give exactly those.
- `EXPECTED_GAP_ROWS` (`tests/test_gap_rows_on_refused_addresses.py`): 77,
  measured by the walk; net7's branch read 79 and predicted 76. The critic
  measured 77.
- `reader_leak_baseline.json`: merged by key, 298 + net7's one = 299 readers,
  dumped as its writer dumps (sorted keys, two-space indent).
- The messaging allowlist cell: 109 patterns, 89 added, the wave's eight
  lines. It FAILED the prose guard's window once more, this time on `creator`
  (the guard looks for every reachable surface's first word within 6000
  characters); the wave-7 clause cut to its ruling ids, and `creator` sits at
  5874.
- INSTRUMENTS 114 to 118 in number order, 0 lines short.
- The lane records' rank citations: section 3.
- Committed as 197fd61. Identity after it: 1436 passed in 51 s.

## 3. The capture queue's rank collisions, and the map

Four lanes each minted their new queue lines' ranks from 142, so at the base
of this integration ranks 142 to 147 were each taken three or four times. The
collision is quiet: `check_next_step` joins the queue on its `surface-id` and
never reads `rank`, and no test reads it. The critic's suggestion, and the
brief's order: keep jobs7's 142-148 (merged first of the four), renumber the
others from 149 in merge order. Each merge took the queue BY KEY from the three
blobs (`queue_merge_renumber.py`, scratch), renumbering the incoming lane's new
lines in that lane's own rank order; a line both sides moved, or a line one
side deleted and the other moved, would have been refused (none was).

| lane | surface id | rank on its branch | rank merged |
|---|---|---|---|
| jobs7 | `C-JMN-2b` | 142 | 142 |
| jobs7 | `C-LRN-1` | 143 | 143 |
| jobs7 | `C-LRN-2` | 144 | 144 |
| jobs7 | `C-J170-1` | 145 | 145 |
| jobs7 | `C-J173-1` | 146 | 146 |
| jobs7 | `C-LRN-3` | 147 | 147 |
| jobs7 | `C-J111-1` | 148 | 148 |
| msg7 | `C-MSG7-1` | 142 | 149 |
| msg7 | `C-MSG7-2` | 143 | 150 |
| msg7 | `admit-my-items-saved-posts` | 144 | 151 |
| msg7 | `admit-feed-hashtag` | 145 | 152 |
| msg7 | `following-list-unfollow` | 146 | 153 |
| msg7 | `post-analytics-comments` | 147 | 154 |
| settings7 | `admit-manage-purchases-payments-purchases` | 142 | 155 |
| settings7 | `admit-mypreferences-m-search-history` | 143 | 156 |
| settings7 | `admit-mypreferences-m-download-my-data` | 144 | 157 |
| settings7 | `admit-mynetwork-settings-manage-syncing` | 145 | 158 |
| settings7 | `admit-mypreferences-m-manage-data-and-activity` | 146 | 159 |
| settings7 | `admit-mypreferences-d-categories-profile-visibility` | 147 | 160 |
| net7 | `admit-mynetwork-discovery-see-all` | 142 | 161 |
| net7 | `admit-mynetwork-settings-manage-syncing` (its mirror) | 145 | collapsed onto 158 |

THE CITATIONS. The ranks are cited in the lanes' records, and the brief allowed
updating them or annotating the map beside them. Each citation of a renumbered
rank is ANNOTATED in place, its words kept: "rank 142 (now 161)", by a scratch
tool that touches only a number following "rank" (and, in settings7's record,
"queue line" or "line"), and only numbers in the map. net7's record: 10 lines
(rank 142 four times, rank 145 six; its own rank-143 line, gone, left as
written); settings7's: 5 (queue lines 145, 146 and 147); jobs7's 7 citations
keep their ranks; msg7's record cites none. The census tables cite no rank:
the queue and `next-step.tsv` join on the surface id.

## 4. The rulings registered, and the two applied here

Thirty-four rulings, each the orchestrator's, each on its own `RULED:` line with
its words quoted and its reopener ("none stated" where the words name none),
in `_audit/2026-11-27-rulings-integration-7.md`. The register entries are in
`scripts/build_rulings_index.py`, after integration 6's, and `_audit/RULINGS.md`
is regenerated from them: 182 -> 216 rulings, every anchor resolving and every
declaration accounted for.

| group | rulings |
|---|---|
| msg7 (12:35, 13:30, 17:20), nine | ADMIT-NOW-LANDING-IN-SESSION-14 (its scope including jobs7's `J 175`), SAVE-POST-UNDER-OWN-CURATION, FEED-UNFOLLOW-ROUTES-UNDER-D6, CAPTURE-SHOWS-READER-BLIND-DEMOTES, ARTICLE-EDITOR-PRESSES, GROUP-SEARCH-MEASURED-ABSENT, COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN (minted), HASHTAG-ADMISSION-WAITS-FOR-A-REFUSING-BASIS, SAVE-RECEIPT-NEEDS-A-CHANGE |
| settings7 (12:55), two | P-N22-SPLITS, VERIFICATION-DELETE-HELD (each the merge notes' own name; aliases `Q-P-N22-SPLITS`, `Q-VERIFICATION-DELETE`) |
| prof7 (22:21 the day before; 13:00, 13:10, 17:20), six | SELF-LOADER-WAITS-FOR-THE-REWRITE, SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH (amended 13:10), KEY-SKILLS-ADD-HELD, CREATOR-IDEAS-NOT-ABSENT-ON-ONE-SURFACE, VOLUNTEERING-FALLBACK-BOUNDARY, EXACT-MATCH-REFUSES-ANY-WHITESPACE |
| net7 (13:25, 17:20, 17:50), seven | KEYWORD-FIELDS-MEASURED-ABSENT, GROW-SUGGESTIONS-BY-ADMISSION-NOT-SCROLL, CONTACTS-PAGE-FROM-THE-SETTINGS-NAV, CONNECTIONS-CONTROLS-MEASURED-ABSENT, RECEIVED-LEAF-ADMITTED-WITH-ITS-READER (minted), RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES, FEED-CURATION-RECEIPT-NEEDS-A-CHANGE |
| jobs7 (13:45, 14:05, 14:30, 15:51), nine | REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE, JOB-ALERT-ROW-CONTROL-ATTENDED, LEARNING-ROWS-SPLIT (re-ruled 14:05), J169-SPLITS-SENIORITY-REAIMED-UNDER-D6 (AMENDED), J169-BY-ITS-OWN-WORDS (AMENDS it), JOB-OPENINGS-BY-FUNCTION-ADDED, J114-READS-ITS-OWN-TABLE, J175-ADMISSION-PASSES-NO-ACT-SUBSTRING (minted), J111-SPLITS-PRODUCTS-FROM-SERVICES |
| the live lane (13:35), one | INBOX-SEARCH-IS-NOT-A-D1-SEARCH (no row moves) |

The brief's 28 are the critic's 23 named rulings and its 5 answers without an
id. Three of those five got a new id here, each written to match the question
a reader would bring. The other two, settings7's answers, are named in the
orchestrator's own 12:55 merge-notes entry, so those names are used. The six
late ones complete the 34. Four existing entries' notes were brought up to
date (the rulings record, section 7): RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE,
FAILED-REPROOF-DEMOTES, VERIFICATIONS-PAGE-ADMITTED and
VOLUNTEERING-BARE-SPELLING-FIRST. The lanes' answered questions sit in the
lane-K ledger's section 7 from their own merges. Each is registered as its
ruling's alias.

APPLIED HERE (a), J111-SPLITS-PRODUCTS-FROM-SERVICES. The current state of each
row was verified on the merged tree before the move, and the script that wrote
the move asserted it.

| row | from | to | how |
|---|---|---|---|
| J 111 | GAP | COVERED-UNFIRED | capability narrowed to "Company Page Products tab", its Products half built by lane jobs7 (`linkedin_company_page_tab(tab="products")`, `company_tabs.read_products_tab`, session 12's load 21) and never fired; one dated note; `PINNED_B1_ROWS`, held by no ruling |
| J 176 | (new) | GAP | "Company Page Services tab", source `a550270` as J 111's, the next free J id; its step CAPTURE `C-J111-1` (queue rank 148, its rows cell `J 111` -> `J 176`); `next-step.tsv` and `jobs-directions.tsv` take its line (the Services tab's own address, admitted by lane A 2026-10-10) |

The population moved 783 -> 784 (`census_row_pin.json` by its own writer, the
two literal pins with it). It moved the pins as `--check` measured: adjudicated
278, delivered_broad 187, unfired 92, stated_rows 784, capabilities 797,
capabilities_achievable 723, achievable 710, b1_no_ruling 64. The gap is
unchanged at 506, because one row left GAP and one entered it.

APPLIED HERE (b), RECEIVED-LEAF-SERVES-THE-INVITATION-WRITES. It is registered
as the ruling that ACCEPTS net7's shared `invitation_manager._RECEIVED_PATHS`
as built. The N 15 / N 16 writes proceed on
`/mynetwork/invitation-manager/received/`. The target stays operator-named,
the grant and press gates are unchanged, and the tuple is confined to the
invitation manager. No code and no row change for it. The cold verifier's
MAJOR on net7 (F1) is answered by it.

THE OTHER STATE THIS INTEGRATION SET, both on the brief's order:
- `N 32`'s read-address line moved NEEDS-SESSION -> ADMITTED (merge 5);
- the manage-syncing queue line's `needs` cell set to `-` (merge 5).

No census row moved state in a merge: each lane's moves were its own,
certified on its branch.

## 5. Pins, re-derived from the merged tree

`census_completion.py --check` ends "every headline figure matches its pin" on
every commit. Every pin that moved was SET to what `--check` measured on that
commit's tree, with a dated comment. None was summed.

| pin | 68a4ff7 | merge 1 | merge 2 | merge 3 | merge 4 | merge 5 | registration |
|---|---|---|---|---|---|---|---|
| stated_rows | 777 | 777 | 782 | 782 | 783 | 783 | 784 |
| capabilities | 790 | 790 | 795 | 795 | 796 | 796 | 797 |
| capabilities_achievable | 719 | 719 | 724 | 723 | 724 | 722 | 723 |
| achievable | 706 | 706 | 711 | 710 | 711 | 709 | 710 |
| out_of_scope | 71 | 71 | 71 | 72 | 72 | 74 | 74 |
| adjudicated | 259 | 259 | 265 | 267 | 269 | 277 | 278 |
| delivered_broad | 171 | 171 | 177 | 178 | 180 | 186 | 187 |
| delivered_strict | 96 | 96 | 96 | 95 | 95 | 95 | 95 |
| gap | 518 | 518 | 517 | 515 | 514 | 506 | 506 |
| unfired | 75 | 75 | 81 | 83 | 85 | 91 | 92 |
| gap_read | 66 | 66 | 66 | 65 | 64 | 56 | 56 |
| gap_write | 347 | 347 | 347 | 346 | 346 | 346 | 346 |
| b1_standing | 27 | 27 | 27 | 28 | 28 | 28 | 28 |
| b1_no_ruling | 48 | 48 | 54 | 55 | 57 | 63 | 64 |
| b3_admitted | 38 | 38 | 38 | 37 | 37 | 32 | 32 |
| b3_refused | 15 | 15 | 15 | 15 | 18 | 17 | 17 |
| b3_needs_session | 11 | 11 | 11 | 11 | 7 | 5 | 5 |

THE CRITIC'S MERGED HEADLINE, CONFIRMED by measurement on merge 5's tree:
- gap 506, adjudicated 277, delivered_broad 186, delivered_strict 95;
- unfired 91, stated_rows 783, achievable 709, out_of_scope 74;
- capabilities 796, capabilities_achievable 722, gap_read 56, gap_write 346;
- gap_unknown 104, b1_no_ruling 63, b1_standing 28, b3_refused 17;
- jobs_gap 104, jobs_admitted 42.

Two figures differ: b3_admitted 32 and b3_needs_session 5, against the
critic's 31 and 6. Both are the `N 32` move, which the critic derived would
give exactly those two. The J 111 split then moved the population figures by
one (the registration column).

The other counts, each measured on the head:
- the surface: 107 -> 111 tools, 162 -> 168 parameters (71 read, 36 write, 4
  write-shaped); `SANCTIONED_WRITES` 41, `PERFORMABLE` 36,
  `SANCTIONED_MUTATIONS` 22;
- the read boundary: 101 -> 109 allowlist patterns, 17 -> 19 pattern
  exemptions, 2 substring exemptions, 33 forbidden substrings;
- the error-url tally: 44 -> 52 (WITHHELD 26, ASKED_FOR 25, PASSTHROUGH 1);
- `LIVE_FIXTURE_COUNTS`: live11 62, live12 56;
- the refused-address walk: `EXPECTED_GAP_ROWS` 77;
- the population: 777 -> 784 (J 175, P 238, M 155, N 216), 74 out of scope;
- the next-step ledger: 518 -> 506 rows;
- the capture queue: 98 -> 106 lines;
- the reader-leak baseline: 299 readers;
- the rulings register: 182 -> 216.

## 6. INSTRUMENTS

The orchestrator pre-assigned one section number to each lane: 114 jobs7, 115
net7, 116 msg7, 117 prof7, 118 settings7 (119 is live-s13's, not merged
here). So no number collided, and none was renumbered. ORDER did need care.
Merge order is not section order, so each merge from the second on met one
append conflict.
- Merge 2 used the orchestrator's `resolve_instruments_order.py`, run on this
  worktree's file through integration 6's wrapper.
- From merge 3 on, one side already held several sections. The orchestrator's
  tool orders the two SIDES by each one's first heading, which would have
  written 114, 117, 116.
- A scratch tool split each side into its `## N.` sections, refused a number
  held twice, and wrote them in number order.
- After each merge, a containment check found 0 added lines short.
- The head holds 114, 115, 116, 117 and 118 in order.

Declared disposable, none shown failing on a planted defect: this lane's
scratch tools. They are:
- the gate, batch and regen runners;
- the keyed TSV merge and the keyed queue merge with renumbering and collapse;
- the hunk resolver and its per-file specs;
- the union and containment checks;
- the section orderer;
- the boundary digest attribution;
- the tail rebuilder (integration 6's);
- the slice row-by-row check;
- the JSON key merge;
- the rank annotator;
- the measurement script and the J 111 applier.
Each answered one question for this record.

## 7. Gates

Each merge, before its commit, passed these, all green:
- the three derived-view `--check`s after `--write` to a fixed point;
- `census_completion.py --check`;
- `check_next_step`, `check_read_addresses`, `check_jobs_directions`,
  `check_write_classes`, `ruling_holds`, `check_exclusion_basis`;
- `check_cited_shas_resolve`.

Identity:
- the pre-commit gate on every commit: 226 spellings, 0 hits;
- the committed-blob test on the clean tree after each merge commit, each run
  to its end before the next merge touched the tree: 1390, 1403, 1409, 1424
  and 1436 passed.

The scoped tests ran in batches, serially (`-p no:randomly`, no `-n`), each
run reading the live flag first. Live session 13's flag stood from 20:01:55
and was down at every test run from 20:15. The full suite is CI's.

| tree | what | result |
|---|---|---|
| merge 2 | the boundary, the census prose, five admission files, the self-loader (9 files) | 1 failed and 438 passed (the prose window, section 2), then 469 passed |
| merge 2 | the register numbers, the derived views, next-step, directions, corrections, row pins (8 files) | 129 passed, 50 s |
| merge 2 | the reader-leak guard, the harness, the press, orphans, the surface, the tools (6 files) | 1516 passed, 192 s, OVER the 2-minute cap |
| merge 3 | the boundary, the prose, five admission files (8 files) | 440 passed, 6 s |
| merge 3 | the register, the views, next-step, corrections, row pins, the literal guard, triage, write classes (9 files) | 157 passed, 79 s |
| merge 3 | the surface and count pins, msg7's save and notifications (7 files) | 257 passed, 31 s |
| merge 3 | the writes tables, receipts, strict presses, spec claims (5 files) | 256 passed, 176 s, OVER the cap |
| merge 3 | the reader-leak guard | 1061 passed, 112 s |
| merge 3 | the envelope guard, the harness | 157 passed, 41 s |
| merge 4 | the boundary, the prose, four admission files | 155 passed, 5 s |
| merge 4 | the surface and count pins, settings7's two readers (7 files) | 274 passed, 21 s |
| merge 4 | the error-url tally, the row pins, the literal guard, next-step, the register, corrections | 126 passed, 50 s |
| merge 4 | the derived views, the harness, the envelope guard | 211 passed, 94 s |
| merge 4 | the reader-leak guard | 1067 passed, 107 s |
| merge 5 | the boundary, the prose, five admission files, the invitation manager and acts, readonly (10 files) | 1 failed and 812 passed (the prose window, section 2), then 813 passed |
| merge 5 | the surface and count pins, net7's matches, facets, fixtures and people readers (10 files) | 488 passed, 31 s |
| merge 5 | the tally, the refused-address pin, next-step, the literal guard, the register, corrections, row pins, the curation receipt, the harness (9 files) | 290 passed, 75 s |
| merge 5 | the derived views, the envelope guard | 60 passed, 31 s |
| merge 5 | the reader-leak guard | 1070 passed, 106 s |
| merge 5 | the writes tables | 163 passed, 137 s, OVER the cap alone |

## 8. Questions, and items for others

- Q1, THE PROSE GUARD'S WINDOW. `tests/test_the_census_prose_matches_the_boundary.py`
  looks for every reachable surface's first word within the first 6000
  characters of the messaging slice's section 4, and the allowlist cell in
  front of them grows with every admission's history. It failed twice here:
  merge 2 on `events` at 6159, merge 5 on `creator`. Each lane alone passed;
  the merged cell is longer than any one lane's. Each time the newest clauses
  were cut to their ruling ids, in settings7's own way. The cell now names
  wave 7 in one clause of ruling ids, and `creator` sits at 5874. Ground: the
  window is a character count over a narrative cell that only grows. The
  question: accept the condensing, or have the guard read the
  reachable-surfaces row (or section 4 to its end) instead of 6000
  characters?
- Q2, SELF-LOADER-WAITS-FOR-THE-REWRITE REGISTERED. Integration 6 held it was
  "a specification of work ... it answers no question" (its rulings record,
  section 8). The critic and the brief count it among the 28 owed. It is
  registered, with integration 6's ground quoted. Accept?
- Q3, THE IDS. COMMENTS-METRIC-NOT-ABSENT-ON-ONE-DROPDOWN (msg7's answer 6a),
  RECEIVED-LEAF-ADMITTED-WITH-ITS-READER (net7's answer 6) and
  J175-ADMISSION-PASSES-NO-ACT-SUBSTRING (jobs7's 14:30 check) are new.
  settings7's two use the names in the orchestrator's own 12:55 entry,
  P-N22-SPLITS and VERIFICATION-DELETE-HELD; the critic had read them as
  unnamed. Accept?
- Q4, "REGISTRATION OWED AT INTEGRATION 7" is left as written wherever the
  lanes wrote it: cells, ledger answers, pin comments, code comments and
  records, about 60 places. Each was true when written, and the register now
  discharges it. Accept, or sweep them?
- Q5, J 111's CAPABILITY. It is narrowed to "Company Page Products tab", and
  J 176 is "Company Page Services tab", as `J 37` / `J 170` were split.
  `J 176` inherits J 111's directions line, re-aimed at the Services tab's
  own admitted address. Accept?
- FOR WAVE 8:
  - `tests/test_writes.py` alone takes 137 s, over the 2-minute local cap, so
    a local gate on `writes.py` needs scoping;
  - the prose window (Q1);
  - the job pipeline's LinkedIn leg, which refuses a located search before
    any load (the critic's section 6.1, already on the orchestrator's list).

## Lessons

- THE EQUAL-MOVE TRAP IS NOT ONLY IN PINS. At merge 4 the allowlist prose
  cell read 104 and "84 were added" on BOTH sides, the same numbers by
  different lines. At merge 5 an exemption-count assert sat just outside a
  hunk whose comments conflicted, and merged clean as one 18. `gap_read`
  merged as one 65. Every count was measured on the merged tree, conflicted
  or not, and that is what caught all three; a reading of the conflict hunks
  would have kept each wrong value.
- A SIDE IS NOT A SECTION. A resolver that orders the two sides of an append
  conflict by each side's first heading is right only while each side holds
  one section. After two merges one side holds several. The general form
  splits each side into its sections and orders those.
- A CHARACTER WINDOW OVER A GROWING CELL FAILS AT INTEGRATION, NEVER ON A
  LANE. Each lane's cell fit; the merged cell, holding every lane's clause,
  did not, twice. Integration is where narrative cells reach their longest.
- A QUIET COLLISION COSTS ITS PROSE. The rank collision broke no check, so the
  key-based merge fixed it in the table for free. Its whole cost was the
  citations in four records, and annotating them in place kept each
  record's words.
- FOREGROUND, WITH A TIMEOUT, THROUGHOUT. After the orchestrator's 20:06 order,
  every step ran in the foreground with an explicit timeout, so nothing this
  lane started was pending at any turn's end.
