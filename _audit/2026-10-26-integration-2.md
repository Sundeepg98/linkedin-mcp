# Integration 2, 2026-10-26: five pending lane heads onto one certified head

Integrator lane `integrator-26`, worktree branched from master f339459. Task:
merge five local branch heads in order, each `--no-ff`, each conflict
resolved by measurement against the merge base; pins and counts re-derived,
never summed. One certified head at the end, certified by `lane_ci.py push`.

Standing rules: `_state/LANE-STANDING-RULES.md` (main checkout, gitignored).
Offline: no LinkedIn load, no port 9224, no Chrome. Full suite CI-only.

Pattern read: `_audit/2026-10-10-integration.md`.

## 1. Merged, in order

| # | head | feature | merge-base | notes |
|---|---|---|---|---|
| 1 | becc3a7 | J 110: `linkedin_company_page_home` | 16ee59a | +2 commits |
| 2 | 1935c25 | J 108: `linkedin_company_people_insights` (Playwright-locator reader, session-2 capture) | 16ee59a | +4 commits |
| 3 | 3e70900 | N 102: `linkedin_company_people_insights` (record reader, synthetic fixture) | 71d83ca | +3 commits. FLAGGED UNFINISHED in the previous session; pre-merge gate check below. |
| 4 | 53f5c3a | lane A: +32 commits, P M9 / J 77 EXCLUDED-RULED, M C70/C93 ADMITTED, M C101 GAP; carries NEW `_audit/2026-10-10-rulings-lane-a-questions.md` | 6c65815 | UNCERTIFIED: its ci/ run 38056930283 was red and its fixes post-date that run; this lane's push certifies it. |
| 5 | a7026d8 | lane B1: +20 commits, P A22, P L8, P L1 COVERED-UNFIRED | 6c65815 | its ci/ ref 9911b3d was red; re-certified by this push. LAST: most diverged. |

## 2. Pre-merge check on head 3 (N 102)

The brief flagged N 102 unfinished. Rule: merge only if the last commit is
complete (record written + gates green at that commit); if the last commit's
record says the item is incomplete or its last gate failed, skip it.

Measured: head 3's three commits touched NO `_audit/` file and NO census
file (`git diff --name-only 71d83ca 3e70900 -- _audit/` is empty). Its last
commit is a child-branch commit; the census decision for N 102 was deferred
to the lane lead ("census edits are the lane lead's" is not its own words but
the pattern every child commit here follows -- 6b2e89f explicitly says the
child does not move a row). Row `N 102` in `_audit/_census/network.md` still
reads GAP on that head (line 642, checked against base 71d83ca: unchanged).
So the branch builds the reader but the ROW never moved and no record was
written.

DECISION: HEAD 3 (N 102) IS SKIPPED, NOT MERGED. Three grounds, each
measured against the merge base or the merged tree:

1. THE TOOL NAME IS TAKEN. Head 2 (J 108) is already merged at this tree and
   owns `linkedin_company_people_insights`, with a Playwright-locator reader
   over the session-2 capture. Head 3 (N 102) registers the SAME tool name
   but through a different module body (a record reader over a synthetic
   fixture builder). A trial merge of head 3 onto the post-J-108 tree hit an
   ADD/ADD conflict on `linkedin_server/company_people_insights.py` and
   `tests/test_company_people_insights.py` (the two files carry two distinct
   implementations, their git blobs do not match), plus content conflicts
   across every count/record/test file. Merging it would register two
   functions under one tool name in the same registry -- impossible -- and
   would have to pick one reader and discard the other's tests, fixtures and
   baselines. That pick is the lane lead's or the orchestrator's, not an
   integrator's: it is a census decision (row N 102 vs row J 108) and this
   lane has no authority to bank either.

2. THE COMPLETION BAR WAS NOT MET. The brief's skip rule: merge only if the
   last commit is complete (a record written + the last gate green at that
   commit). Head 3's last commit (3e70900) touches NO `_audit/` file
   (`git diff --name-only 71d83ca 3e70900 -- _audit/` is empty), so no
   record for N 102 was written on the branch. And the census row N 102 in
   `_audit/_census/network.md` still reads GAP on that head (line 642; its
   own text says "a reader is the owner's; no state moves on a capture" and
   the capture is the open condition). The last commit's message describes a
   count-prose/visibility fix, not a green gate on the item it was named for.

3. THE MISSING STEP (recorded so the lane lead knows exactly what is owed, if
   N 102 is ever re-opened): (a) a record under `_audit/` naming N 102;
   (b) a move of the census row N 102 GAP -> COVERED-UNFIRED on the
   evidence of its own reader; and (c) a ruling on which of the two
   `linkedin_company_people_insights` implementations (J 108's Playwright
   reader, now merged; N 102's record reader, skipped) the registry keeps --
   the one that loses has its tests, fixtures and baseline entries retired.

Skipped per the brief's own skip path; the branch head is left unmerged and
no tool, record or row of N 102 is on this tree.

## 3. Conflicts resolved by judgement

(merged 1, becc3a7, J 110) The merge base 16ee59a is OLD relative to our
worktree head: base held 61 tools, our side advanced to 72, theirs advanced a
sibling to 62 (adding only `linkedin_company_page_home`). Resolved by union,
measured never summed:
- `people_data.py`: two different 5th record types -- ours'
  `Organisation` (lane G2, a Page's name+link) and theirs' `OrganisationProse`
  (J 110, a Page's prose) -- both kept in `RECORD_TYPES`, `TEXT_FIELDS`,
  `as_record` and `text_fields`; `PEOPLE_TOOLS` is the union of the two
  lists. Class bodies auto-merged.
- `server.py` docstring: ours' full history kept; theirs' J 110 paragraph
  grafted as the newest entry; the headline re-derived from the merged
  registry as **seventy-three tools, twenty-two of which write** (72 + their
  one read; their J 110 is a read, so the write count is ours' 22). The
  three-way split line: **FIFTY-ONE read, TWENTY-TWO write, ZERO
  write-shaped**; sum 51 + 22 + 0 = 73. The parenthetical count-chain keeps
  the base's entry as "Fifty, twenty-two and seventy-two on master at this
  integration's base" and adds this merge's entry.
- `server.py` registration: the merge interleaved ours' lane B2/B3/B4
  blocks with theirs' company_home block; rebuilt whole in merge order --
  ours' blocks (B2 verticals, B3, B4) kept in place, theirs'
  `company_page_home` block inserted after ours' `set_similar_jobs_alert`
  and before `unset_similar_jobs_alert` (a single contiguous J 110 block
  with its own `from linkedin_server import company_home` import, exactly as
  theirs wrote it). No tool dropped: merged tool set = ours' 72 +
  `linkedin_company_page_home` = 73, verified by `comm` against both sides.
- Test files: record-type sets, the read-only names list, and the count
  chains all UNIONED; the two divergent `assert len(tools)` pins merged to
  the measured 73 (with the non-write count 51), and the pinned-surface
  counts re-derived by measurement as **73 tools, 116 parameters**
  (the auto-merged `PINNED_TOOL_SURFACE` dict was parsed, not summed).
  `test_every_tool_is_on_the_surface.py`'s `assert len(_tool_names())` moved
  72 -> 73.
- `README.md`: headline re-derived to "Seventy-three tools ship. Fifty-one
  read. Twenty-two write."; the module listing's count moved to
  "the seventy-three tools"; both sides' history chains kept as evidence,
  each entry describing its own tree.

Gate: the targeted surface + record tests ran after resolution (results in
section 5).

(merged 2, 1935c25, J 108) The J 108 branch head (62 tools on its own
branch, off base 16ee59a) onto the post-merge-1 head (73 tools). The
branch's only addition is one tool, `linkedin_company_people_insights`
(J 108, the People tab's insight cards as categories and counts), and its
new record type `people_data.Category`; the merged tool set is 73 + 1 = 74,
measured off the merged registry (verified by `comm` against both sides:
the branch's delta vs base is exactly `linkedin_company_people_insights`).

Conflicts resolved by union, against the merge base:
- `people_data.py`: `RECORD_TYPES` now carries all three divergent record
  types -- ours' `Organisation` (lane G2) and `OrganisationProse` (J 110)
  plus the branch's `Category` (J 108) -- and the `PEOPLE_TOOLS`,
  `TEXT_FIELDS` (`CATEGORY_SHAPE`), `as_record` and `text_fields` sites all
  union the three. The `Category` class body auto-merged.
- `server.py` docstring: the branch's J 108 paragraph grafted as THE
  SEVENTY-FOURTH; headline re-derived as **seventy-four tools, twenty-two
  of which write** (74; J 108 is a read, so the write count is held at
  22). The three-way split: **FIFTY-TWO read, TWENTY-TWO write, ZERO
  write-shaped**; sum 52 + 22 + 0 = 74.
- `server.py` registration: the branch's single J 108 block (its own
  `from linkedin_server import company_people_insights, member_rosters`
  import and tool) sits after the J 110 `company_page_home` tool, before
  `unset_similar_jobs_alert`... i.e. the two new reads are each kept whole
  in their own contiguous block, in merge order (J 110 block, then J 108
  block), so no function is split. No tool dropped: 74 measured.
- `test_every_orphan_module_is_ruled.py`: the merged tree wires BOTH
  `search_verticals` (lane B2's search readers import it) and
  `member_rosters` (B5's `group_roster` and J 108's
  `company_people_insights` import it), so BOTH entries that were in the
  base dict are deleted in the merged tree; the union's dict is empty, and
  the note records that two entries were removed and why.
- `test_member_rosters.py`: on the merged tree `server.py` is still the
  sole importer of `member_rosters`, and there are exactly two
  `compose` calls in it -- the group tool names the roster through
  `group_roster.ROSTER` (an attribute) and J 108 names `"company_people"`
  as a literal. The test's single-importer assertion is unchanged; the
  compose-names assertion is re-derived to name BOTH rosters (one literal,
  one attribute) rather than the branch's single-literal version.
- `test_readers_emit_no_page_string.py`: the branch's
  `company_people_insights:read_people_insights` RETURNS_RECORDS entry and
  its drive-breaks fixture join ours' set.
- `shipped_drives.py`: the branch's `read_people_insights_as_shipped`
  drive joins the shipped-drives registry.
- `tests/tool_envelope_baseline.json`: the branch's
  `linkedin_company_people_insights` not_driven entry unions with ours'
  `linkedin_company_page_home` entry; the tools count is 74.
- `tests/test_server_surface.py`, `tests/test_every_tool_is_on_the_surface.py`,
  `tests/test_the_tool_surface_is_pinned_so_a_row_must_move.py`: both sides'
  count chains kept as evidence; the divergent `assert len(tools)` pins
  merged to the measured 74 (non-write 52); the pinned-surface counts
  re-derived by measurement as **74 tools, 117 parameters** (the
  auto-merged `PINNED_TOOL_SURFACE` dict was parsed, not summed).

Gate: the targeted surface + record + reader tests ran after resolution
(results in section 5).

(merged 4, lane A's head, its subject "tests: the seven reds of CI run
38056930283 -- neighbours that assumed the content vertical refused, and the
gap-row pin"; merge base 6c65815, 32 commits.) Lane A's branch held 63 tools;
its only new tool is `linkedin_tracker_stage(stage, limit)`, a read. The merged
registry measures **75 tools, 119 parameters, 22 that write, 53 that do not**
(`mcp.list_tools()` and `writes.PERFORMABLE` on the merged tree). Lane A was
UNCERTIFIED when merged: its ci/ run 38056930283 was red and its fixes post-date
that run; this lane's push certifies the merged head.

Census rows (the four `.md` slices), resolved per row against the base blob,
each row taken whole from the side that moved it; NO row was edited by both:
- `jobs.md`: rows 71, 72, 73, 77, 156, 160 from lane A; 74, 75, 76, 161 from ours.
- `network.md`: rows 19, 38, 39, 199 from lane A; 20, 37, 200 from ours.
- `messaging-and-content.md`: C70, C101 from lane A; C69, C100 from ours.
- `profile.md`: M4, M5, M6, M9, P15 from lane A; M7, M8, M10 and P4-P14,
  P16-P23 from ours.

Census tables (`next-step`, `capture-queue`, `jobs-directions`,
`read-addresses`), a three-way merge per row key (slice + row id for the two
side tables), deletions counted as moves: zero rows in conflict. Moved by ours
/ lane A: next-step 29 / 54, capture-queue 4 / 27, jobs-directions 2 / 24,
read-addresses 14 / 20. Line counts reconcile with each side's own adds and
deletes: 559-12-5 = 542, 95+1-4 = 92, 148-2-4 = 142, 136-10-1 = 125. One
capture-queue line (32, `admit-newsletters-id`) was edited by both sides on
DISJOINT cells and merged cell by cell: lane A rewrote its ADMIT step (after
the log redaction NAMED-ADDRESS-NEEDS-LOG-REDACTION requires); ours added `N 56`
to the rows it serves with their count. Each table's own checker is GREEN.

`scripts/census_completion.py`: twelve pins, each SET TO THE VALUE THE SCRIPT
MEASURED on the merged tree (both lanes' comments kept above each); the
NO_RULING list is the union (`P O17` from ours; `J 38`, `J 50`, `J 51` from
lane A). The moves agree with lane A's own row moves (J 38, J 50, J 51 GAP ->
COVERED-UNFIRED; P M9, J 77 GAP -> EXCLUDED-RULED): adjudicated +5,
delivered_broad, unfired and b1_no_ruling +3, gap -5, achievable -2.

Resolved by judgement, one line each:
- `server.py` / `README.md` / the three surface tests: both sides' count
  histories kept as evidence; every headline, split and pin re-derived off the
  merged registry (75 / 53 / 22 / 119), never summed.
- `README.md`, hunk 2: a connective only ("AND" on ours, "BEFORE THAT IT READ"
  on lane A) on one history line; ours' wording kept, since in the merged file
  the line follows lane U's paragraph exactly as it does on ours.
- `INSTRUMENTS.md`: lane A's section 83 placed BEFORE ours' 90, 91 and 93,
  ascending within the block both sides appended; the older 88-then-84 order
  is untouched. The register's own test checks uniqueness, not order.
- Derived views regenerated twice to a fixed point, never hand-merged: the
  audit index over 276 documents (274 + lane A's two), the rulings register at
  95 (90 + the five in lane A's rulings document), the blocker map 409 lines.

A FINDING ABOUT MERGE 2, RECORDED RATHER THAN SMOOTHED OVER: ours' `README.md`
still read "Seventy-three tools ship" after merge 2 although the registry held
74. The J 108 branch never touched README, so merge 2 auto-merged a stale
headline, and merge 2's targeted gate did not include
`tests/test_the_other_two_count_claims_are_pinned_too.py`, the guard on that
line. The merge-2 commit therefore carried a headline that guard would fail.
It is corrected here by measurement (75 / 53 / 22), and that guard is in every
later gate of this lane.

THE PENDING RULINGS DOCUMENT TRAVELLED WITH THIS MERGE:
`_audit/2026-10-10-rulings-lane-a-questions.md`, registered on lane A's branch
and never on master. It is the orchestrator's; this lane did not rule on it and
did not edit it. Its five rulings now appear in the derived register.

Gate after merge 4 (sharded, 104 s, inside the 2-minute cap): lane A's 20
test files, the three surface tests, the prose-count guards and every test
that reads a file resolved here -- 1600 passed, 4 failed, all four in
`tests/test_readonly.py` and all four about `company_home.py`, which came in
with merge 1 (J 110), not with lane A. See "J 110's off-boundary script"
below; the merge itself is committed first, the fix in its own commit.

### J 110's off-boundary script, found at merge 4 and fixed in its own commit

The merge-4 gate failed four tests in `tests/test_readonly.py`, all about
`linkedin_server/company_home.py` (J 110, merged at merge 1):

- `test_no_module_contains_an_UNSANCTIONED_mutating_call[company_home.py]`
- `test_every_sanctioned_entry_is_actually_present`
- `test_the_package_contains_exactly_as_many_mutating_calls_as_are_listed` (17 against 16)
- `test_the_scripts_executed_are_exactly_the_ones_declared` (`HOME_JS` undeclared;
  behind it, the executed-script pin read 25 where 26 call sites ran)

NOT A MERGE DEFECT: J 110's own branch head runs the same unwaived
`page.evaluate(HOME_JS, ...)` at the same line, and both guards already
existed at its base 16ee59a, so that branch was red on these four by itself.
It was never CI-certified, and merge 1's targeted gate did not include
`tests/test_readonly.py`, so the four arrived unseen until merge 4.

THE RULE IT BROKE, AND THE ONE WAY OUT. A `# readonly-ok` waiver is allowed in
`dom.py` alone (`test_only_dom_module_waives_evaluate`), and every executed
script must be declared from there. `newsletters.py` records the same refusal
and its rule: belong in `dom.py`, or do not inject. The guard's own standard is
that a waiver is spent only where a plain call cannot replace the script.
`HOME_JS` qualifies: it reads the description as raw TEXT RUNS (text nodes
joined, a `br` kept as a line break, aria-hidden and hidden subtrees and the
expander control stepped over and counted) and returns the runs and skips so a
cut text can be told from one that ended. `inner_text()` follows CSS rendering,
not aria-hidden; `text_content()` keeps hidden subtrees; neither counts what it
dropped; a locator never addresses a text node. Read-only, measured: the
script was scanned for every state-changing operation (clicks, focus, scroll,
events, submits, DOM, attribute and style writes, storage, cookies,
navigation, fetch) and none occurs.

THE FIX, VERBATIM, BEHAVIOUR UNCHANGED (an integrator's call, reversible):
- `dom.COMPANY_HOME_JS` is `company_home.HOME_JS` byte for byte (sha256 and
  the 3,022-character length measured before and after), run from ONE call
  site, `dom.read_company_home`, with the waiver. `company_home` keeps the
  vocabulary handed to the page and the shaping of the answer into one
  `people_data.OrganisationProse` record; `dom` calls them. No import cycle
  (`company_home` imports only `coerce` and `people_data`), and `dom.py`
  already imports per-surface modules.
- `tests/test_readonly.py`: `COMPANY_HOME_JS` declared; the executed-script
  pin 25 -> 26 and the `dom.py` waiver budget 24 -> 25 moved TOGETHER, each
  with its reason, as every earlier script did ("the two counts stay one
  apart").
- The reader's key `company_home:read_company_home` -> `dom:read_company_home`
  in the reader-leak baseline (still `returns_records`, a line-level rename in
  sorted position), `DRIVEN_TO`, `FIXTURE_BREAKS` and the shipped drives;
  `server.py` and the J 110 tests call it at its new home.
- No census row moves: `J 110` stays GAP, as its branch left it.

ONE MORE CROSS-LANE FINDING ON THE SAME FILE, A SEMANTIC CONFLICT NO MERGE
MARKER SHOWED: `tests/test_company_home.py::test_the_root_is_admitted_and_the_posts_and_home_tabs_stay_refused`
asserted `/company/<x>/about/` refused. Lane A admitted that address on its own
anchored line (census `J 106`), so on the merged tree it is admitted, measured
through the shipped `is_read_url` (root, about, people, life, products,
services and events admitted; home, posts, jobs, insights and videos refused).
The J 110 test now names `jobs/`, which no ruling reaches, as lane A did for its
own five neighbour tests; `posts/` and `home/` are still asserted refused.

Gate for this fix (sharded, 111 s): the whole of `tests/test_readonly.py`,
the J 110 tests, the reader-leak and tool-envelope drives, the people-reader
closure, the orphan and outside-dom inventories and the surface and prose
guards -- 1787 passed, 1 failed (the about/ neighbour above), then that file
alone after its fix: 21 passed.


## 4. Pins re-derived on the merged tree

(pending)

## 5. Gates and certification

(pending)
