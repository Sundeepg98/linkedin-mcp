<!-- secret-scan-allow: git-sha -->
(The long hex strings throughout this file are git commit and stash SHAs --
public repo history cited as evidence, e.g. the snapshot sha
ea9954be9a4e06b757a21c51e01a021866ce5094 and commit 94e4601 -- not secrets.)

Census: probe controls that never branch
scripts/_probe_*.py, run from a wave-lead worktree of this repo.
Run 2026-09-20. CENSUS ONLY -- no repo file was modified or committed by this task.

=======================================================================
0. WORKTREE IS SHARED BY DESIGN. Measured from a FROZEN SNAPSHOT, not the
   live tree. Escalated to team-lead first (msg_id
   5a3d8a72-b4ed-44c4-b6b0-42029abe731f); ruling received (msg from
   team-lead, "RULING: take (b)...") and applied exactly as directed
   before this final version was written.
=======================================================================

SEQUENCE OF EVENTS: while reading the calibration file
(scripts/_probe_events_surface_shape.py) a second time, it no longer
matched the brief's quotes -- `git status --porcelain` showed it modified,
plus a lead-note addressed to a different teammate ("floor-two") and two
untracked test files, neither created by this task. Escalated rather than
guessing. The ruling that came back, in full, in order of consequence:

  1. TAKE SNAPSHOT (b) -- `git stash create`, record the sha, read every
     file for the rest of the run via that frozen sha, never the live
     tree. (a) HEAD-only would score another agent's already-landed fix as
     an open defect; (c) the live tree is a denominator that moves while
     counting it, which is not a census.
  2. CALIBRATION AND CORPUS MUST SHARE ONE SNAPSHOT. Testing the detector
     against HEAD and then counting a DIFFERENT snapshot proves the
     detector works on a file that is not even in the corpus being
     measured.
  3. THE ORIGINAL POSITIVE CONTROL HAS BEEN REPAIRED. In the snapshot,
     `silent` is now correctly branched (`if silent: ...; return 1`), so
     inside the corpus being measured this file is a NEGATIVE, not the
     textbook positive the brief described. A single calibration file that
     always returns a finding regardless of content is a check that cannot
     fail; it certifies nothing.
  4. THE FIX: keep HEAD as a SYNTHETIC positive (frozen, immune to any
     edit, requires a FINDING), and add a PAIRED discrimination check --
     the SAME file, SAME variable, in the snapshot, must come back
     CORRECTLY BRANCHED. Same file, two shas, opposite verdicts, proves
     the detector discriminates rather than merely asserts.
  5. THE TREE WILL NOT GO QUIET. This worktree belongs to the wave lead
     and is shared with sibling children by design -- waiting for
     exclusivity was the wrong ask, and the snapshot is the adaptation,
     not a workaround for a temporary condition.

EXECUTION, in order:
  a. `git stash create "control-census-snapshot-2026-09-20"` ->
     `ea9954be9a4e06b757a21c51e01a021866ce5094`. Confirmed this neither
     touched the working tree (`git status --porcelain` unchanged
     immediately after) nor the shared stash stack (`git stash list`
     stayed empty -- `stash create` builds the commit object without
     pushing a stash entry).
  b. Materialized all 88 `scripts/_probe_*.py` paths from that sha via
     `git show <sha>:<path>`, one file at a time, into
     snapshot_corpus/scripts/ next to the detector (script:
     materialize_snapshot.py). 88/88 succeeded.
  c. Re-derived calibration directly from the SNAPSHOT's actual content
     (not assumed from an earlier read) -- see section 2.
  d. Ran the corpus pass ONLY against the materialized snapshot
     directory, never the live worktree.

RESULT: both controls pass (section 2). The corpus tally is IDENTICAL to
the interim live-tree numbers reported earlier (56 files, 129 instances) --
this is not a coincidence to be suspicious of: the snapshot was taken
minutes after that earlier read and this one file's finding-relevant
content had not moved again in between (confirmed by direct inspection,
section 2). Disk moved AGAIN after the snapshot was taken (this task was
notified of a further edit to this same file partway through applying the
ruling) -- irrelevant to this report, because the snapshot is an immutable
git object and everything below was read from it, not from the live tree.
The single file involved throughout is
scripts/_probe_events_surface_shape.py; no other file in the corpus was
ever implicated.

=======================================================================
1. CORPUS COUNT
=======================================================================
`scripts/_probe_*.py` in the worktree: 88 files (globbed and counted with
`ls scripts/_probe_*.py | wc -l`, confirmed, not assumed). Reconfirmed
independently inside the frozen snapshot: `git ls-tree -r --name-only
<sha> -- scripts/` also lists exactly 88 matching paths, and the
materializer (section 0) wrote 88/88 without a failure -- the detector
itself refuses to proceed if this count is not exactly 88 (a hard gate,
not a printed warning).

=======================================================================
2. CALIBRATION -- TWO PAIRED CONTROLS, per the lead's ruling
=======================================================================
Snapshot sha: ea9954be9a4e06b757a21c51e01a021866ce5094
(`git stash create`, taken 2026-09-20, never pushed to the shared stash
stack, working tree untouched by it).

--- CONTROL A: SYNTHETIC POSITIVE, against the IMMUTABLE HEAD blob ---
File: calib_head/_probe_events_surface_shape.py (git show HEAD:..., 278
lines, byte-identical to the file the brief quotes). This file is NOT part
of the corpus being measured -- it exists solely to prove the detector CAN
find this defect shape at all.

  POSITIVE 1 (silent, must-stay-silent control, line 181):
    Found as a FINDING. num_loads=2 (both inside the single two-line print
    call), 0 non-sink loads. CORRECT.
  POSITIVE 2 (hits, Q4 needle-sweep loop, line 255):
    Found as a FINDING. num_loads=1, 0 non-sink loads. The nearby
    `if needle == "/events/":` branches on `needle`, never on `hits` --
    confirmed by reading the source directly. CORRECT.
  NEGATIVE (agree, line 186):
    Found in branched_controls, NOT in findings. num_loads=2, 1 non-sink
    load -- `if not agree: ...; return 1` at line 189. CORRECT.

  ALL THREE VERDICTS REPRODUCED (all_three_verdicts_correct: true).

--- CONTROL B: DISCRIMINATION CHECK, against the SNAPSHOT (the corpus's
    OWN copy of the same file) ---
File: snapshot_corpus/scripts/_probe_events_surface_shape.py, materialized
from sha ea9954be9a4e06b757a21c51e01a021866ce5094. Re-derived fresh from
this exact content (not assumed from the earlier HEAD read or from any
prior look at the live tree):

  silent (line 206): now `if silent: ...; return 1` at lines 209-213.
    Result: found in branched_controls, NOT in findings.
    silent_now_correctly_branched: true.
  must_fire (line 233, a SECOND repair present in this same snapshot,
    not seen in the earlier live-tree read): `if not must_fire: ...;
    return 1` at lines 237-241. Result: found in branched_controls, NOT in
    findings. must_fire_correctly_branched: true.
  hits / note (Q4 per-needle loop, line 306): UNCHANGED shape -- still
    computed and only printed; the loop's own comment now reads
    "the must-fire control, checked and branched on above", i.e. the
    author moved the real gate to `must_fire` and left this loop as an
    acknowledged display-only listing. Mechanically still a finding by
    this census's definition (never branched on ITSELF); flagged as lower
    priority in section 6 for exactly this reason -- a real,
    correctly-branched control now exists elsewhere in the same file for
    the same underlying question.

  discrimination_proven: true -- same file, same variable (`silent`),
  HEAD says FINDING, this snapshot says CORRECTLY BRANCHED. That is the
  proof the detector reads content rather than asserting a fixed answer.

The corpus pass ran only after BOTH controls passed (two hard gates in the
script; either failing aborts before the corpus is touched).

=======================================================================
3. METHOD (summary -- full logic is the comments in the detector script)
=======================================================================
Script: detect_unbranched_controls.py, same directory as this report.
AST-based (Python `ast`, not regex), per function (nested defs are their
own scope, so a local wrapper like `emit()` does not pollute `main()`'s
variable set):

  - CANDIDATES: every simple-Name assignment target (Assign, AugAssign,
    AnnAssign, NamedExpr, for-loop target) local to a function.
  - SINKS: `print`, plus any locally-defined function whose own body calls
    `print` at least once (catches thin wrappers such as
    `emit(text): print(text); lines.append(text)` -- confirmed present in
    8 of the 88 files: job_search_filter_params, job_search_paging_stride,
    job_search_result_ceiling, job_search_result_sets, match_details_control
    (all `emit`), search_render_timeline (`say`), badge_and_language_
    affordances, contact_info_panel (`report`, checked and found to be a
    plain multi-line print formatter, not a value-transforming wrapper).
  - PRINT-ONLY: for every Load of a candidate name, climb its AST ancestors;
    if a Call to a sink is reached before any statement boundary, that load
    is print-only (this correctly follows the value through `.format()`,
    `%`-formatting, ternaries, comparisons, and plain-function reformatting
    such as `_label_relation(label)`, since none of those are statement
    boundaries -- verified by hand, see section 5).
  - CONTROL-LIKE gate: the brief's marker list (case-insensitive substring:
    PASS, FAIL, CONTROL, must fire, must stay silent, must be, VOID,
    sanity, expected, AGREE, DISAGREE), matched against the variable's own
    name OR a NARROW window -- the assignment plus, climbing outward
    through enclosing blocks only as far as needed, the first later
    sibling statement (at whichever level the search succeeds) whose
    subtree contains a sink call referencing the name. This window is
    deliberately local (not "the whole function") specifically so a marker
    word sitting in unrelated code elsewhere cannot manufacture a false
    CONTROL-LIKE classification, and it is exactly wide enough to catch
    POSITIVE 2's shape (the marker sits in a sibling `if` that branches on
    a DIFFERENT variable, not in the print statement itself).
  - FINDING = control-like AND every load of the name is print-only
    (>=1 load required; a control-like name with ZERO loads anywhere --
    i.e. assigned and never even printed -- is tracked separately as
    "unused", see section 7, not counted as this defect).

=======================================================================
4. HEADLINE NUMBERS
=======================================================================
  Corpus:                                    88 files
  Parse failures (unclassified):              0
  Files with NO control marker at all:        2
  Files with markers, ALL controls branched
    ("clean"):                                30
  FILES WITH >=1 NEVER-BRANCHED CONTROL
    (THE HEADLINE COUNT):                     56
  Total never-branched FINDING instances:     129   (across those 56 files,
                                                      all read from the one
                                                      frozen snapshot sha --
                                                      see section 0)
  Control-like-but-correctly-branched
    instances (context, not a defect):        630
  "Unused" controls (assigned, control-like,
    never even read) -- separate category:    13, across 11 files

  2 + 30 + 56 = 88. Checked.

4a. INDEPENDENT REPLICATION (team-lead, same day)
-------------------------------------------------
The lead ran this same detector against the main tree independently and
got with_finding=56 EXACTLY, corroborating the headline file count from a
separate invocation. The lead's run differed by +1 file and +1 instance:
89 files / 130 instances there against 88 / 129 here. The delta is
explained, not a discrepancy: the main tree carries one extra untracked
probe, `scripts/_probe_premium_surfaces_shape.py`, that a live browser
wave was writing at the moment of the run -- and this detector's own drift
check (section 0's method, generalised) named that exact file rather than
silently absorbing it into the tally. Both readings are consistent with
one another once that file is accounted for.

4b. TWO DENOMINATORS, BOTH TRUE, AND THEY SAY DIFFERENT THINGS
----------------------------------------------------------------
"56 of 88 files affected" (64%) and "129 of 762 control-like instances
never branch" (17%) are BOTH correct, and reporting only the first
overstates the defect: it was repeated to the operator as "64% of probe
files are affected," which reads as though the corpus is mostly broken,
before this instance-level number existed to correct it.

  FILE-LEVEL:      56 of 88 files carry >=1 never-branched control  (64%)
  INSTANCE-LEVEL:  129 of 762 control-like readings never branch    (17%)
                   630 of 762 branch correctly                      (83%)
                    13 of 762 are assigned and never even read       (2%)

A file with ONE decorative control among a dozen sound ones is not the
same object as a file whose every control is theatre, and the file-level
count alone cannot tell those two apart. The distribution below is what
actually separates them.

4c. DISTRIBUTION -- A LONG TAIL, NOT AN EVEN SPREAD
-------------------------------------------------------
Findings per flagged file, all 56 files:

  findings/file | files | share of the 56 | cumulative files
  ------------- | ----- | --------------- | ----------------
        1       |  19   |      33.9%      |  19
        2       |  19   |      33.9%      |  38
        3       |   9   |      16.1%      |  47
        4       |   3   |       5.4%      |  50
        5       |   4   |       7.1%      |  54
        6       |   1   |       1.8%      |  55
        7       |   1   |       1.8%      |  56

  19 + 19 + 9 + 3 + 4 + 1 + 1 = 56 files. 1*19+2*19+3*9+4*3+5*4+6*1+7*1
  = 19+38+27+12+20+6+7 = 129 instances. Checked both ways.

68% of flagged files (38 of 56) carry just 1 or 2 decorative controls each
-- most likely a single overlooked self-check in an otherwise-sound probe,
not a probe whose entire control discipline failed. Only 16% (9 of 56)
carry 4 or more, and the worst is 7
(`scripts/_probe_add_section_menu.py`), not dozens. This is a LONG TAIL of
single-instance files with a SHORT, identifiable head of more heavily
affected ones -- a materially different remediation shape from "129 spread
evenly across the corpus," and it means a fixer working file-by-file from
the head of this list retires a large share of the total quickly.

=======================================================================
5. FALSE-POSITIVE CHECK (hand inspection)
=======================================================================
16 findings were hand-inspected by opening the source at the reported line
and reading the surrounding function in full (not just trusting the
tool's own line snippet, which for a multi-line print statement only shows
its FIRST physical line and can look misleading -- e.g. `before` in
_probe_group_settings_route.py:164 looked unused in the print's first
line, but the print is a two-line f-string and `before.get(...)` is on the
second line; confirmed by reading both lines).

Spread across both marker strengths and both assignment kinds:

  TRUE POSITIVE, confirmed by reading the source (14):
   1. _probe_add_section_menu.py:436       pop_shown   (printed only, via a
      multi-line f-string; the tool's own single-line print_src snippet
      under-showed this -- confirmed by reading lines 436-449 in full)
   2. _probe_connections_badge_cost.py:196 label       (printed only, via
      a helper `_label_relation(label)` whose result feeds `%`-formatting
      into print -- confirmed the helper does not branch on it either)
   3. _probe_group_settings_route.py:164   before      (printed only, via
      `.get()` calls on the print statement's second physical line)
   4. _probe_events_surface_shape.py:307   note        (same Q4 shape as
      calibration POSITIVE 2; per the frozen snapshot, the real gate for
      this question moved to `must_fire` elsewhere in the same file, and
      this specific loop is now an acknowledged display-only listing --
      see section 2, control B)
   5. _probe_groups_menu.py:544            stuck       ("menus still
      expanded after Escape" -- computed, displayed, nothing checks
      `if stuck:` even though the surrounding block otherwise gates on
      `control_ok` and `navigated`)
   6. _probe_membership_tally_live.py:222  overlap     (a disjoint-sets
      dict; all 4 of its keys, including the boolean `disjoint`, are only
      ever interpolated into one print, never tested)
   7. _probe_newsletter_subscriptions_live.py:505 read_count (printed
      twice via %-formatting at two different call sites, never compared)
   8. _probe_small_measures_live.py:418    census      (single print,
      never branched)
   9. _probe_small_measures_live.py:439    main_text   (printed via a
      derived length calculation, never branched; confirmed against two
      OTHER same-named locals in sibling functions in the same file that
      follow the identical printed-only pattern)
  10. _probe_job_search_result_ceiling.py:165 viewport_w (a -1 sentinel
      for "viewport never captured" that is only ever displayed, never
      checked for the sentinel value)
  11. _probe_job_collections_live.py:269   second      (printed via
      `.get()` twice, never branched)
  12. _probe_contact_info_panel.py:345     badge_before (printed via
      `.get()`, never branched)
  13. _probe_membership_sections.py:136    silent      (the SAME
      must-stay-silent shape as the calibration file's own POSITIVE 1,
      independently present in a second file -- strong cross-file evidence
      this is a recurring authored pattern, not a one-off)
  14. _probe_newsletter_surface_shape.py:458-459 hits/note (the SAME Q4
      must-fire-needle shape as calibration POSITIVE 2, independently
      present in a second file, right down to the "<- must fire; a zero
      voids this sweep" comment text)

  BORDERLINE, mechanically correct but weaker on the merits (2):
  15. _probe_add_section_menu.py:260 case_label (run_detector_control) --
      the loop's REAL verdicts (rel_ok, press_ok) ARE correctly branched
      two lines later (`if not (rel_ok and press_ok): ok = False`);
      `case_label` itself is a display tag riding in the same print
      statement, not itself a check. Matches the letter of the rule
      (printed only, never branched) but is closer to the calibration's
      `needle` (an identifying value) than to its `hits` (the tested
      quantity). Flagged, not removed -- see section 6.
  16. _probe_messaging_menu_enumeration.py:552 one / overlap_label
      (_report_overlaps) -- confirmed FALSE-POSITIVE MECHANISM: its ONLY
      marker hit is "pass", and the ONLY place "pass" appears in its
      window is inside the parameter name `passes: dict`, not any PASS/
      FAIL text. Separately, on the merits, the surrounding prose reads as
      a deliberate "report for a human to eyeball, not an automated gate"
      design choice, not a forgotten branch. See section 6 for the
      corpus-wide sweep this triggered.

  RESULT: 14/16 (87.5%) clean true positives on direct source reading;
  the other 2 are disclosed, explained edge cases, not silent noise.

=======================================================================
6. TIGHTENING PASS: marker-embedding and loop-target risk, QUANTIFIED
=======================================================================
Finding #16 above showed a concrete mechanism: a short marker ("pass")
matching as a substring of an unrelated word ("passes", a parameter name).
This was swept for across the whole corpus, not just patched locally.

  a) Corpus-wide sweep for KNOWN bad embeddings (passes/password/passenger/
     passport/bypass/compass/surpass/encompass/trespass for "pass";
     avoid/devoid for "void") with NO other, unrelated marker hit anywhere
     in the same finding's window:
       2 of 129 findings (1.6%) -- both at the SAME site:
       _probe_messaging_menu_enumeration.py:552, variables `one` and
       `overlap_label` (finding #16 above and its sibling).
     No other file in the corpus has a finding whose control-like status
     depends solely on one of these embeddings.

  b) A separate, stricter word-boundary regex was also tried
     (`(?<![a-z])marker(?![a-z])`) as a second cross-check, BEFORE/AFTER:
       BEFORE (loose, as specified in the brief):  129 findings, 56 files
       AFTER  (strict word-boundary):                91 findings, 41 files
     This 30% drop is NOT trustworthy as a clean false-positive figure,
     and is NOT being used to revise the headline count: the strict regex
     also rejects legitimate inflections with a following letter, e.g.
     "controls" (plural of "control") fails `(?![a-z])` because of the
     trailing "s". This is exactly why _probe_groups_menu.py's `stuck`
     (hand-confirmed TRUE POSITIVE in section 5, #5) disappears under the
     strict version -- its marker was "control" hitting the word
     "controls" nearby, a legitimate variant, not an embedding error. The
     strict pass is reported for transparency, not adopted: it trades a
     rare, identified 1.6% embedding problem for a much larger, unquantified
     rate of rejecting genuine plurals. Sections 6a (targeted, checked by
     hand) is the trustworthy number; 6b (blanket regex) is reported only
     to show it was tried and why it was not used.

  c) FOR-LOOP-TARGET share: 33 of 129 findings (25.6%) are for-loop/
     async-for iteration variables rather than computed Assign/AugAssign/
     NamedExpr values (full list has an "assign_kind" column in
     control-census.json). Finding #15 above (case_label) is one of
     these, and is the weakest of the 16 hand-checked. RECOMMENDATION:
     treat the 96 assign-kind findings as higher confidence and the 33
     for_target-kind findings as needing a second look before being acted
     on individually -- a for-loop target is often a display label riding
     next to a properly-branched verdict rather than an independent
     forgotten check. This is a visible column in the full table (section
     8) and in control-census.json, not a silent adjustment to the
     headline count.

  NET: after both checks, the headline count (56 files, 129 instances) is
  KEPT AS-IS -- the one concretely proven false-positive mechanism (1.6%,
  both instances at one site) is called out by name rather than patched
  out, and the for-loop-target caveat is surfaced as a column rather than
  a silent filter, so whoever acts on this table can apply either cut
  themselves.

=======================================================================
7. WHAT WAS NOT A FINDING (context, for completeness)
=======================================================================
  - "Unused" controls (13, across 11 files): a control-like name assigned
    and NEVER read at all, not even printed. Hand-checked: 11 of these 13
    are Python's own "deliberately discarded" convention (`_`, `_url`,
    `_depth`, `_selector`, `_hrefs`, `_a`, `_b`, `_rest` -- leading
    underscore, tuple-unpacked and intentionally unused), not a version of
    this defect. The remaining 2
    (_probe_analytics_controls_live.py:516 `_href_shapes`,
    _probe_interests_entity_shaping.py:134 `shape`) are also underscore-
    or shadow-named and were not investigated further -- flagged here as
    NOT examined in depth, since they are a different defect shape
    (dead/unused value, not "computed-printed-never-branched") outside
    this census's scope.
  - branched_controls (630 instances): control-like names that DO have at
    least one non-print-nested load somewhere -- i.e. the tool found real
    branching and correctly did not report them. Not enumerated in full in
    this report (they are in control-census.json under each file's
    "branched_controls" key) since they are explicitly NOT the defect.

=======================================================================
8. FULL FINDINGS TABLE (129 rows, all read from the frozen snapshot
   ea9954be9a4e06b757a21c51e01a021866ce5094 -- see section 0)
=======================================================================
Columns: file | line (of the assignment) | function | variable |
marker(s) matched | kind (assign = computed value, for_target = loop
iteration variable, see section 6c) | branched? (always NO -- this table
is exactly the findings list; branched instances are not enumerated here,
see section 7).

| file | line | function | variable | marker(s) matched | kind | branched? |
|---|---|---|---|---|---|---|
| _probe_add_section_menu.py | 260 | run_detector_control | case_label | control, fail, pass | for_target | NO |
| _probe_add_section_menu.py | 330 | main | html | control, must be, pass | assign | NO |
| _probe_add_section_menu.py | 376 | main | controls | control, expected | assign | NO |
| _probe_add_section_menu.py | 412 | main | shown | control, expected | assign | NO |
| _probe_add_section_menu.py | 436 | main | pop_shown | control | assign | NO |
| _probe_add_section_menu.py | 439 | main | exp_shown | control | assign | NO |
| _probe_add_section_menu.py | 442 | main | role_shown | control | assign | NO |
| _probe_alerts_family_pattern.py | 115 | _run_controls | label | control, expected, fail | assign | NO |
| _probe_alerts_family_pattern.py | 116 | _run_controls | why | control, expected, fail | assign | NO |
| _probe_analytics_controls_live.py | 606 | press_pass | vanished | control, fail | assign | NO |
| _probe_anchor_surfaces_live.py | 141 | _control | disagree | agree, disagree | assign | NO |
| _probe_apply_flow.py | 333 | main | apply_url | control, pass | assign | NO |
| _probe_apply_flow.py | 377 | main | settled | control, pass | assign | NO |
| _probe_comment_identifier.py | 364 | main | anchors | agree, control, void | assign | NO |
| _probe_comment_identifier.py | 371 | main | position | agree, control, void | for_target | NO |
| _probe_comment_overflow_menu.py | 246 | main | anchors | control | assign | NO |
| _probe_comment_overflow_menu.py | 267 | main | position | control | for_target | NO |
| _probe_comment_overflow_menu.py | 301 | main | key | control | for_target | NO |
| _probe_connections_badge_cost.py | 195 | main | href | control | assign | NO |
| _probe_connections_badge_cost.py | 196 | main | label | control | assign | NO |
| _probe_connections_badge_cost.py | 216 | main | live | control | assign | NO |
| _probe_contact_info_panel.py | 345 | main | badge_before | control, expected | assign | NO |
| _probe_contact_info_panel.py | 346 | main | badge_after | control, expected | assign | NO |
| _probe_creator_content_analytics.py | 275 | main | vocab | expected | assign | NO |
| _probe_creator_content_analytics.py | 315 | main | feed_hits | expected | assign | NO |
| _probe_details_url_breadth.py | 144 | main | files | control | assign | NO |
| _probe_details_url_breadth.py | 146 | main | mention_in | control | assign | NO |
| _probe_events_home_live.py | 268 | main | on_events | agree, control, fail | assign | NO |
| _probe_events_row_menu.py | 206 | main | census | control | assign | NO |
| _probe_events_surface_shape.py | 274 | main | rows_with_any | control | assign | NO |
| _probe_events_surface_shape.py | 306 | main | hits | control | assign | NO |
| _probe_events_surface_shape.py | 307 | main | note | control | assign | NO |
| _probe_feed_counter_search.py | 106 | _run | reaction | control | assign | NO |
| _probe_feed_counter_search.py | 107 | _run | key | control | for_target | NO |
| _probe_feed_counter_search.py | 116 | _run | selector | control | for_target | NO |
| _probe_free_reads_shapes.py | 391 | _report_census | counts | control | assign | NO |
| _probe_group_row_affordances.py | 210 | main | before | control | assign | NO |
| _probe_group_row_affordances.py | 233 | main | with_menu | agree, disagree | assign | NO |
| _probe_group_row_affordances.py | 234 | main | without | agree, disagree | assign | NO |
| _probe_group_settings_route.py | 160 | main | control_before | control | assign | NO |
| _probe_group_settings_route.py | 164 | main | before | control | assign | NO |
| _probe_group_settings_route.py | 189 | main | control_after | control | assign | NO |
| _probe_group_settings_route.py | 244 | main | tags | control | assign | NO |
| _probe_groups_events_live.py | 185 | _read | counts | control | assign | NO |
| _probe_groups_events_live.py | 215 | _settle | agree | agree, control, disagree | assign | NO |
| _probe_groups_events_live.py | 355 | main | marker | agree, control, disagree, pass | for_target | NO |
| _probe_groups_locator_walk.py | 236 | main | label | control | for_target | NO |
| _probe_groups_locator_walk.py | 236 | main | tally | control | for_target | NO |
| _probe_groups_menu.py | 346 | main | groups_controls | control | assign | NO |
| _probe_groups_menu.py | 544 | main | stuck | control | assign | NO |
| _probe_interests_entity_shaping.py | 266 | main | kind | control, fail | for_target | NO |
| _probe_interests_entity_shaping.py | 270 | main | verdict | control, fail | assign | NO |
| _probe_interests_entity_shaping.py | 286 | main | href_reds | control | assign | NO |
| _probe_job_alerts_live.py | 308 | _read | counts | control | assign | NO |
| _probe_job_collections_live.py | 216 | _read | counts | control | assign | NO |
| _probe_job_collections_live.py | 268 | main | first | control, must be | assign | NO |
| _probe_job_collections_live.py | 269 | main | second | control, must be | assign | NO |
| _probe_job_search_filter_params.py | 1292 | main | lines | fail, pass | assign | NO |
| _probe_job_search_filter_params.py | 1307 | main | p1_negative | fail, pass | assign | NO |
| _probe_job_search_filter_params.py | 1308 | main | p1_stopped | fail, pass | assign | NO |
| _probe_job_search_filter_params.py | 1310 | main | diagnosis | control, fail, pass | assign | NO |
| _probe_job_search_filter_params.py | 1342 | main | cards | fail | assign | NO |
| _probe_job_search_paging_stride.py | 164 | main | rows | fail | assign | NO |
| _probe_job_search_paging_stride.py | 164 | main | dropped | fail | assign | NO |
| _probe_job_search_result_ceiling.py | 157 | main | dropped | fail, pass | assign | NO |
| _probe_job_search_result_ceiling.py | 160 | main | refused | fail, pass | assign | NO |
| _probe_job_search_result_ceiling.py | 162 | main | all_anchors | fail, pass | assign | NO |
| _probe_job_search_result_ceiling.py | 163 | main | list_items | fail, pass | assign | NO |
| _probe_job_search_result_ceiling.py | 165 | main | viewport_w | fail, pass | assign | NO |
| _probe_job_search_result_sets.py | 722 | main | lines | control | assign | NO |
| _probe_jobs_tail_boundary.py | 124 | main | label | control, expected, fail | for_target | NO |
| _probe_landed_address_sweep.py | 275 | main | measured | agree, control, fail, pass | assign | NO |
| _probe_landed_address_sweep.py | 289 | main | label | control, fail | for_target | NO |
| _probe_landed_address_sweep.py | 289 | main | url | control, fail | for_target | NO |
| _probe_match_details_control.py | 201 | main | html_len | control, fail | assign | NO |
| _probe_match_details_control.py | 202 | main | text_len | control, fail | assign | NO |
| _probe_match_details_control.py | 309 | main | anchors | control | assign | NO |
| _probe_match_details_control.py | 310 | main | overlay | control | assign | NO |
| _probe_membership_sections.py | 136 | _analyse | silent | control, fail, must stay silent, pass | assign | NO |
| _probe_membership_tally_live.py | 191 | main | badge_before | control, expected | assign | NO |
| _probe_membership_tally_live.py | 222 | main | overlap | control | assign | NO |
| _probe_membership_tally_live.py | 240 | main | name | control | for_target | NO |
| _probe_membership_tally_live.py | 240 | main | tally | control | for_target | NO |
| _probe_messaging.py | 332 | main | what | control | for_target | NO |
| _probe_messaging.py | 332 | main | pattern | control | for_target | NO |
| _probe_messaging_hidden_controls.py | 215 | _run | undisplayed | control, fail | for_target | NO |
| _probe_messaging_hidden_controls.py | 216 | _run | flag | control, fail | assign | NO |
| _probe_messaging_menu_enumeration.py | 552 | _report_overlaps | overlap_label | pass | for_target | NO |
| _probe_messaging_menu_enumeration.py | 552 | _report_overlaps | one | pass | for_target | NO |
| _probe_messaging_surface_census.py | 362 | _run | key | control | for_target | NO |
| _probe_network_tail_boundary.py | 115 | run_controls | why | control, expected | for_target | NO |
| _probe_network_tail_boundary.py | 116 | run_controls | seen | expected | assign | NO |
| _probe_newsletter_routes.py | 161 | main | why | fail | for_target | NO |
| _probe_newsletter_subscriptions_live.py | 407 | _run | live | control | assign | NO |
| _probe_newsletter_subscriptions_live.py | 505 | _run | read_count | control | assign | NO |
| _probe_newsletter_surface_shape.py | 331 | run_word_census | note | expected, must fire, must stay silent | assign | NO |
| _probe_newsletter_surface_shape.py | 433 | main | queried | agree, disagree | assign | NO |
| _probe_newsletter_surface_shape.py | 441 | main | count | agree, disagree | for_target | NO |
| _probe_newsletter_surface_shape.py | 444 | main | mark | agree, disagree | assign | NO |
| _probe_newsletter_surface_shape.py | 458 | main | hits | must fire, void | assign | NO |
| _probe_newsletter_surface_shape.py | 459 | main | note | must fire, void | assign | NO |
| _probe_off_platform_controls.py | 133 | read_surface | html | control, must be, pass | assign | NO |
| _probe_premium_entitlement.py | 296 | _run | live | control | assign | NO |
| _probe_profile_modal_presence.py | 300 | run_controls | label | expected, fail, pass | for_target | NO |
| _probe_profile_modal_presence.py | 390 | press_add_section | census_like | control | assign | NO |
| _probe_profile_sections_live.py | 250 | main | count | control | for_target | NO |
| _probe_profile_sections_live.py | 251 | main | mark | control | assign | NO |
| _probe_reaction_on_label.py | 88 | main | key | control | for_target | NO |
| _probe_retire_ruling_boundary.py | 160 | main | label | control, expected, fail | for_target | NO |
| _probe_retire_ruling_boundary.py | 160 | main | provenance | control, expected, fail | for_target | NO |
| _probe_route_vs_surface.py | 155 | main | why | fail | for_target | NO |
| _probe_search_admission_blast_radius.py | 262 | main | line | fail | for_target | NO |
| _probe_search_appearances_live.py | 99 | verdict | name | fail | for_target | NO |
| _probe_small_measures_followup.py | 200 | run_detector_control | verdict | expected, fail, pass | assign | NO |
| _probe_small_measures_followup.py | 392 | part_b_suggested_filters | html | pass | assign | NO |
| _probe_small_measures_followup.py | 393 | part_b_suggested_filters | main_text | pass | assign | NO |
| _probe_small_measures_followup.py | 428 | part_c_hashtag_partition | main_text | fail, pass | assign | NO |
| _probe_small_measures_followup.py | 443 | part_c_hashtag_partition | sums | fail, pass | assign | NO |
| _probe_small_measures_live.py | 227 | run_detector_control | verdict | expected, fail, pass | assign | NO |
| _probe_small_measures_live.py | 270 | _needles | main_text | pass | assign | NO |
| _probe_small_measures_live.py | 302 | read_jobs_search | census | control | assign | NO |
| _probe_small_measures_live.py | 418 | read_events | census | control | assign | NO |
| _probe_small_measures_live.py | 439 | read_feed_hashtag_context | main_text | pass | assign | NO |
| _probe_typeahead_commit.py | 385 | main | why | control | assign | NO |
| _probe_typeahead_commit.py | 661 | main | send | control | assign | NO |
| _probe_unmeasured_surface_addresses.py | 343 | main | failed | control, fail, pass | assign | NO |
| _probe_unmeasured_surfaces_live.py | 354 | _report_census | counts | control | assign | NO |
| _probe_unmeasured_surfaces_live.py | 431 | _report_href_kinds | other | control | assign | NO |
| _probe_which_item_is_reacted.py | 145 | main | key | control | for_target | NO |

Note on _probe_events_surface_shape.py rows above (lines 274/306/307): these
are the 3 findings in this file as of the frozen snapshot sha
ea9954be9a4e06b757a21c51e01a021866ce5094 -- rows_with_any, hits, note.
`silent` (line 206) and `must_fire` (line 233) are NOT in this table: both
are correctly branched in this snapshot and appear only in
control-census.json's "branched_controls" list for this file. See section
2 for the paired control that specifically proves the detector reads
`silent`'s repair correctly rather than reporting it by rote.

=======================================================================
9. FILE-LEVEL LISTS
=======================================================================
Files with NO control marker at all (2):
  _probe_attach_continuity.py
  _probe_interests.py

Files with markers, zero findings -- "clean" (30):
  _probe_alert_keywords_survive_shaping.py
  _probe_apply_route_screen.py
  _probe_badge_and_language_affordances.py
  _probe_boundary_line_attribution.py
  _probe_company_family_blast.py
  _probe_company_path_segments.py
  _probe_compose_file_inputs.py
  _probe_endorse_and_follow_lines.py
  _probe_feed_kinds_in_corpus.py
  _probe_feed_kinds_live.py
  _probe_file_inputs_live.py
  _probe_first_sanctioned_press.py
  _probe_follow_on_posting.py
  _probe_following.py
  _probe_group_memberships_tool_live.py
  _probe_groups_events_capture.py
  _probe_in_progress.py
  _probe_intro_editor_controls.py
  _probe_invitation_rail_disagreement.py
  _probe_manage_pages_both.py
  _probe_membership_signal_in_corpus.py
  _probe_messaging_family_off_the_feed.py
  _probe_notify_cost_precondition.py
  _probe_open_to_work_payload.py
  _probe_radio_click_target.py
  _probe_sdui_action_resolver.py
  _probe_search_render_timeline.py
  _probe_self_details_url.py
  _probe_thread_reply_surface.py
  _probe_where_the_editor_lives.py

Files with >=1 finding, instance count each (56 files, 129 instances):
    7  _probe_add_section_menu.py
    2  _probe_alerts_family_pattern.py
    1  _probe_analytics_controls_live.py
    1  _probe_anchor_surfaces_live.py
    2  _probe_apply_flow.py
    2  _probe_comment_identifier.py
    3  _probe_comment_overflow_menu.py
    3  _probe_connections_badge_cost.py
    2  _probe_contact_info_panel.py
    2  _probe_creator_content_analytics.py
    2  _probe_details_url_breadth.py
    1  _probe_events_home_live.py
    1  _probe_events_row_menu.py
    3  _probe_events_surface_shape.py   (frozen snapshot read -- see section 0)
    3  _probe_feed_counter_search.py
    1  _probe_free_reads_shapes.py
    3  _probe_group_row_affordances.py
    4  _probe_group_settings_route.py
    3  _probe_groups_events_live.py
    2  _probe_groups_locator_walk.py
    2  _probe_groups_menu.py
    3  _probe_interests_entity_shaping.py
    1  _probe_job_alerts_live.py
    3  _probe_job_collections_live.py
    5  _probe_job_search_filter_params.py
    2  _probe_job_search_paging_stride.py
    5  _probe_job_search_result_ceiling.py
    1  _probe_job_search_result_sets.py
    1  _probe_jobs_tail_boundary.py
    3  _probe_landed_address_sweep.py
    4  _probe_match_details_control.py
    1  _probe_membership_sections.py
    4  _probe_membership_tally_live.py
    2  _probe_messaging.py
    2  _probe_messaging_hidden_controls.py
    2  _probe_messaging_menu_enumeration.py
    1  _probe_messaging_surface_census.py
    2  _probe_network_tail_boundary.py
    1  _probe_newsletter_routes.py
    2  _probe_newsletter_subscriptions_live.py
    6  _probe_newsletter_surface_shape.py
    1  _probe_off_platform_controls.py
    1  _probe_premium_entitlement.py
    2  _probe_profile_modal_presence.py
    2  _probe_profile_sections_live.py
    1  _probe_reaction_on_label.py
    2  _probe_retire_ruling_boundary.py
    1  _probe_route_vs_surface.py
    1  _probe_search_admission_blast_radius.py
    1  _probe_search_appearances_live.py
    5  _probe_small_measures_followup.py
    5  _probe_small_measures_live.py
    2  _probe_typeahead_commit.py
    1  _probe_unmeasured_surface_addresses.py
    2  _probe_unmeasured_surfaces_live.py
    1  _probe_which_item_is_reacted.py

=======================================================================
10. WHAT WAS NOT EXAMINED
=======================================================================
  - No file failed to parse (0 unclassified by that route) -- all 88 are
    valid Python 3 per `ast.parse`.
  - Nothing dynamic (`exec`, `eval`, reassignment of the `print` builtin)
    exists anywhere in the corpus -- checked by grep across all 88 files
    before writing the detector, zero matches for either.
  - No file uses `logging` instead of, or alongside, `print` -- checked by
    grep, zero matches. `print` (plus the 8 files' local wrappers, listed
    in section 3) is the complete sink inventory; nothing was assumed.
  - Indirect printing through an intermediate variable (e.g.
    `msg = f"...{x}..."; print(msg)`, where the sink-nesting climb would
    stop at the `msg = ...` assignment statement before ever reaching
    `print`) is OUT OF SCOPE for this detector -- it would under-count
    (miss a genuine finding), never over-count. Not swept for separately;
    flagged as a known limitation rather than silently absent.
  - Variable-name shadowing/reuse within one function (the same name bound
    twice for two logically unrelated purposes) is not distinguished --
    all loads of a name are pooled across the whole function scope. This
    can only make the detector MORE conservative (a later, unrelated
    branch on a reused name would mask an earlier real finding), not
    inflate the count. Not swept for; flagged as a known limitation.
  - Python comprehension scoping (a comprehension's own loop variable is
    technically its own scope) is approximated as "same scope as the
    enclosing function" -- this could rarely conflate an outer variable
    with a same-named comprehension-internal one. Not swept for
    separately; flagged as a known limitation, believed rare given the
    corpus's style (checked by spot reading, not exhaustively).
  - The 630 branched_controls and 13 unused_controls instances are not
    individually hand-verified beyond the samples in sections 5 and 7 --
    they are explicitly the NOT-a-finding buckets, included in
    control-census.json for anyone who wants to re-derive or spot-check
    them, but not walked line-by-line here.

=======================================================================
11. FILES
=======================================================================
Snapshot sha: see section 0/2 (git stash create, never pushed to the
shared stash stack).

The detector script, the snapshot materializer, the materialized 88-file
snapshot corpus, the frozen HEAD reference copy, and the raw machine-
readable findings (control-census.json, all fields including window_text,
the synthetic_positive_control and discrimination_control results, and the
branched_controls / unused_controls buckets) all lived in this session's
scratchpad -- outside this repo, on the machine that ran this census, never
committed or intended to be, and not reproducible from an absolute path
that only made sense on that one machine. Re-deriving them is cheap:
`scripts/detect_unbranched_probe_controls.py` (committed, see section 12)
IS that detector, ported and importable; running it against any commit or
snapshot reproduces the same JSON shape. Nothing in this write-up depends
on the scratchpad copies still existing.

THIS report is committed at `_audit/2026-09-20-control-census.md` in this
repo (commit `94e4601` and after).

The snapshot commit object created by `git stash create` is reachable only
by its sha (it was never attached to any ref or the stash stack), so it is
invisible to `git status`, `git log`, and `git stash list` alike, and will
be garbage-collected in the ordinary course of the repo's housekeeping --
it does not need to be, and should not be, cleaned up by hand.

At the time the census itself ran (sections 0-9 above), no file inside the
repo worktree was created, modified, or committed. That changed afterward,
on explicit instruction: see section 12.

=======================================================================
12. THE GUARD, SHIPPED -- AND THE 129 RANKED BY WHAT THEY COST
=======================================================================
Directed by the wave lead, after this census: harvest the detector into
the repo as a real guard (not fix any of the 129 -- a separate fixer does
that), and rank the findings by which ones a census row was actually
banked on, so the fixer has a short list rather than 129 undifferentiated
rows. Both are now done and COMMITTED (commit `94e4601`, this repo,
this branch):

  scripts/detect_unbranched_probe_controls.py               (the detector)
  scripts/probe_controls_known_decorative_baseline.json     (129-entry ratchet)
  tests/test_probe_controls_are_never_decorative.py          (the guard test)
  scripts/_check_unbranched_control_detector_can_fail.py     (receipt generator)
  _audit/INSTRUMENTS.md entry 24                              (the write-up)

Full detail -- the discrimination-pair receipt, the ratchet design and why
an exact-count pin (this repo's own established idiom for this exact
situation) was rejected in favour of a baseline keyed on
(file, function, variable), and the same false-positive mechanism from
section 6 disclosed again in the guard's own docstring -- lives in
INSTRUMENTS.md entry 24 rather than duplicated here. The guard does NOT
gate on the pre-existing 129; it gates on any NEW one, so it is live in the
test suite today without blocking on the backlog being cleared first.

12a. RANKED BY COST, NOT BY COUNT
-------------------------------------
A never-branched control is not automatically a wrong answer -- it means
the probe's self-check was decorative, not that its finding was false.
What separates a finding that merely LOOKS bad from one that actually
THREATENS something already concluded: whether a census row in
`_audit/_census/*.md` was moved off GAP using that exact probe's output.
Cross-referenced all 56 flagged files against the five census slice files
and the other 160 `_audit/*.md` write-ups (script: triage_by_cost.py,
scratchpad-only, not shipped -- its output is what this section reports):

  TIER 1 -- underlies a BANKED census row (COVERED-PROVEN or
            COVERED-CANNOT-DELIVER): 5 files. THE ACTIONABLE LIST.
  TIER 2 -- cited in a census row, but that row is still GAP or
            EXCLUDED-RULED (nothing banked on it yet): 2 files.
  TIER 3 -- no census-table row, but named in an _audit/ journal write-up:
            43 files.
  TIER 4 -- not found cited anywhere searched: 6 files.
  5 + 2 + 43 + 6 = 56. Checked.

TIER 1, IN FULL -- the fixer's cheapest high-value next step:

  1. scripts/_probe_small_measures_live.py (5 findings) -- underlies
     _audit/_census/jobs.md row 15, "The All filters panel as a surface",
     COVERED-PROVEN. That row's OWN evidence text names this probe
     "shown failing before admission" -- and it still carries 5 decorative
     controls of its own on OTHER variables (verdict, main_text x3,
     census x2 across different functions). Being vetted on one control
     does not mean every control in the same file was.
  2. scripts/_probe_job_collections_live.py (3 findings: counts, first,
     second) -- underlies _audit/_census/jobs.md row 42, job collections
     and their five groupings, COVERED-PROVEN.
  3. scripts/_probe_creator_content_analytics.py (2 findings: vocab,
     feed_hits) -- underlies _audit/_census/messaging-and-content.md row
     C40, creator analytics, COVERED-PROVEN.
  4. scripts/_probe_job_search_result_sets.py (1 finding: lines, line 722)
     -- underlies FIVE rows at once in _audit/_census/jobs.md (9, 11, 12,
     13, 14 -- the job-search filter parameters), all COVERED-PROVEN,
     all citing the same instrument and evidence block.
  5. scripts/_probe_membership_sections.py (1 finding: `silent`, line 136
     -- the SAME must-stay-silent shape as this census's own calibration
     positive) -- underlies _audit/_census/network.md row 162, browsing
     groups recommended from shared attributes, COVERED-CANNOT-DELIVER.

None of this claims the 5 banked rows are WRONG -- a decorative control
does not mean the probe's conclusion was false, only that the probe never
checked whether it could have been. That is precisely why it is ranked
rather than fixed here: whether each of these 5 rows' claims still holds
once its control actually branches is a measurement, and this task's brief
was census and harvest, not repair.

Raw ranking data (all 56 rows, all four tiers, with the exact census-row
citations and journal mentions found per file) lived in this session's
scratchpad as `triage-by-cost.json`, alongside the other scratchpad
materials named in section 11 -- not committed, not needed to reproduce
this section: the ranking itself, in full, is written out in 12a above.
