# Integration 3, 2026-11-26: four certified heads onto master, and the rulings since 2026-11-25 22:30

Integrator lane `integrator-26`, worktree at master 4c62196 (this lane's own
integration-2 head, fast-forwarded and pushed, master CI green). Task: merge
four certified heads, each based on 4c62196, each `--no-ff`, conflicts
resolved by measurement; register every orchestrator ruling recorded from
"2026-11-25 22:30 IST" to the end of the orchestrator's merge notes, and apply
the row moves each implies by its row's own bar; re-derive every pin; one
lane CI run on the combined head, read by sha.

During the four merges a live session (lane live-s11, session 11) was running
on this box with the live flag raised, so every local test run was targeted
and serial (`-p no:randomly`, no `-n`), checked against the flag before it
started. The lane's process exited at about 01:30 IST and the box rebooted.
The registration pass resumed at 09:03 IST with the flag absent, and ran
scoped gates only, each checked against the flag first. Offline throughout:
no LinkedIn load, no port 9224, no Chrome.

Session 11's own head (lane live-s11) is the fifth merge of this set. It lands
on top of the registration head, and only the head certified after it goes to
master.

Pattern read: `_audit/2026-10-26-integration-2.md`.

## 1. The heads, each certified on its own lane CI, read by sha

| # | lane | head | lane CI run (by head sha) | what it brings |
|---|---|---|---|---|
| 1 | build-p26 | 966e176 | 45662325211 success | `P L2b` GAP -> COVERED-UNFIRED on `linkedin_my_followers_list`; 81 tools; 11 rows re-pointed |
| 2 | build-jmn26 | 3e606d0 | 45671409359 success | `J 108`, `J 31` GAP -> COVERED-UNFIRED; `linkedin_set_search_job_alert` and its inverse; 11 rows re-pointed |
| 3 | admit26 | edfbb50 | 45668398409 success | 0 ADMIT rows left: 99 became 52 CAPTURE, 1 TARGET, 46 RULING; 26 rows admitted on 10 spellings; owns the `readonly.py` admission lists |
| 4 | apply-26 | b865dc9 | 45665387031 success | the multi-step apply walker and the answer bank, unwired; queue lines C-J68-1..3; no row moved |

## 2. The order, and why

Chosen by MEASURED conflict surface, not by guess. `git merge-tree
--write-tree` over all six pairs (each pair shares base 4c62196) gave the files
each pair conflicts in, the three derived views excluded (they are
regenerated, never resolved):

| pair | conflicted files besides the derived views |
|---|---|
| build-p26 x build-jmn26 | 9: README, the lane-K ledger record, INSTRUMENTS, capture queue, `server.py`, `census_completion.py`, the three surface tests |
| admit26 x build-p26 | 5: the ledger record, INSTRUMENTS, capture queue, next-step, `profile.md` |
| admit26 x build-jmn26 | 4: the ledger record, INSTRUMENTS, capture queue, next-step |
| each of the three x apply-26 | 2: INSTRUMENTS, capture queue |

The first merge onto the base is conflict-free, and merge k resolves the union
of its conflicts with every head already merged. Scored over all 24 orders,
the minimum is 16 distinct file resolutions in all, with a peak of 9 in one
merge. Every order at that minimum puts the two builds together and admit26
after both. Of those, this lane took **build-p26 -> build-jmn26 -> admit26 ->
apply-26** (per merge: 0, 9, 5, 2):

- the heaviest conflict, the two builds' `server.py` tool blocks, pins and
  surface tests, is resolved on a tree holding only those two heads;
- admit26 then resolves its five census-table conflicts once, against both
  builds at once;
- apply-26, the lightest (2 files, no row moved), goes last;
- of the two builds, the smaller change set (30 files to 37) goes first.

## 3. Merges, and the conflicts resolved by judgement

(merged 1, build-p26 966e176.) Conflict-free: HEAD was the merge base, and the
merged tree is byte-identical to build-p26's certified tree (`git write-tree`
against its `^{tree}`). Its `P L2b` move stands on its row's own bar: the reader
is aimed at the live lane's session-2 skeleton of the list, with synthetic
people only as values.

(merged 2, build-jmn26 3e606d0.) Eleven conflicts, two of them derived views.
Every census row checked three-way (base 4c62196, ours build-p26, theirs
build-jmn26): no row moved by both sides; `next-step.tsv` 539 -> 536 (ours -1,
`P L2b`; theirs -2, `J 108` and `J 31`), measured.

- PINS, AN EQUAL MOVE ON FIVE KEYS: each lane moved adjudicated 235 -> 236 for
  a DIFFERENT row (`P L2b`; `J 108`), and build-jmn26 moved it again for
  `J 31`; the same shape on delivered_broad, gap, unfired and b1_no_ruling.
  Both lanes' comments kept, each pin then SET TO WHAT `census_completion.py`
  MEASURED: adjudicated 238, delivered_broad 158, gap 535, unfired 41,
  b1_no_ruling 25. A text merge would have kept one +1 too few on every one.
- REGISTRATION TAIL: both lanes appended one block after lane B1's
  `lb1-audience` block, and git interleaved them into two hunks. Rebuilt as
  build-p26's block (marker to end marker), then build-jmn26's, each
  byte-identical to its own side. Registry MEASURED: 83 tools, 134
  parameters, 24 performable writes, 3 refusing, 56 reads; the registered set
  is exactly ours plus build-jmn26's two tools.
- `server.py` docstring, the three surface tests and README re-derived to 83:
  headline "eighty-three tools, twenty-four of which write"; the split 56 + 24
  + 3; README 83 / 56 / 27 (its guard counts sanctioned writes: 25 + 2); the
  cited test renamed `..._eighty_three_tools`; build-jmn26's branch paragraph
  replaced by one dated paragraph, as build-p26 did for lane B1's child.
- CAPTURE QUEUE, KEYED BY SURFACE ID: its first column is a running rank, and
  both lanes appended at the same next ranks (102, 103), so a rank key reports
  false conflicts. Merged by surface id instead: 104 lines (ours 99 plus
  build-jmn26's 5); ours' new lines keep 102-103 and build-jmn26's five
  (C-JMN-1..4, t-named-search-card) are RENUMBERED 104-108 in their own order.
  Nothing cites a queue line by rank (measured: citations are by surface id).
- The lane-K ledger record: both lanes appended questions at the same point;
  the union, build-p26's three then build-jmn26's two, each a pure addition.
- INSTRUMENTS: build-p26's 100 then build-jmn26's 101, by heading order.

(merged 3, admit26 edfbb50.) The five conflicts the measurement predicted,
plus the derived views. Every census row checked three-way (base 4c62196,
ours the two builds, theirs admit26): no row moved by both sides; no pin moved
(`census --check` clean, unedited), because admit26 re-pointed next steps and
moved no state.

- CAPTURE QUEUE, keyed by surface id: 86 lines. admit26 deleted 21 lines and
  added 3, renumbered 109-111 after ours' 108. TWO LINES BOTH SIDES MOVED,
  each resolved cell by cell:
  - `in-me-profile`: build-p26 added `P A25` and `P D25` with two link
    presses; admit26 added the twelve section-form rows (`P D11` to `P D23`,
    `P D29`). `rows` is the ordered union, 20 rows on one load, so
    rows_unblocked and rows_per_load are RECOUNTED from it (20, 20.0) rather
    than summed; both sides' text cells were pure appends and keep both.
  - `admit-in-me-details-recommendations`: admit26 re-gated the line on
    `Q-RECOMMENDATIONS-DETAIL-PAGE` (session, needs, verdict, plan), and
    build-p26 added `P F1` (13 rows). Disjoint cells, each from its mover.
- `next-step.tsv`: ours moved 25 rows, admit26 99, none both. ONE EDIT BY
  JUDGEMENT: `P F1`, which build-p26 had put on the recommendations line with
  an ADMIT step, follows that line to `RULING:Q-RECOMMENDATIONS-DETAIL-PAGE`.
  A queue line that needs a ruling holds every row it lists at that ruling
  (`check_next_step.py`), and build-p26's own note says all 13 lines move
  together.
- `profile.md`: eight rows in hunks, each moved by one side only.
- The lane-K ledger record: the union again (ours' 76 lines, admit26's 161).
- INSTRUMENTS: admit26's section is 102, so the tail reads 100, 101, 102.

(merged 4, apply-26 b865dc9.) The two conflicts the measurement predicted, plus
the derived views. No row moved on apply-26 and no pin moved.

- CAPTURE QUEUE, keyed by surface id: apply-26's three lines `C-J68-1..3`
  appended with their ids kept (C-J68-IDS-KEPT, section 4), ranks renumbered
  112-114; 89 lines.
- INSTRUMENTS: apply-26's section is 99, placed before 100 by heading order.

## 4. The rulings registered

Forty-one rulings, every one the orchestrator's, each with an id on a `RULED:`
line, its own words quoted, and its reopener ("none stated" where the words
name none). The register entries are in `scripts/build_rulings_index.py`, and
`_audit/RULINGS.md` is regenerated from them. Two documents hold the
declarations, because a ruling takes its date from its document's name:

- `_audit/2026-11-25-rulings-end-of-wave.md`: thirty-eight rulings, from the
  entries of 2026-11-25 at 22:30, 22:40, 22:50, 23:08, 23:35 and 23:40.
  - The live plan (L1): L1-D1-RIDERS-RIDE, L1-D2-GROUPS-FROM-HIS-MEMBERSHIPS,
    L1-D3-MEDIA-CHOOSER-INTERCEPTED, L1-D4-NEUTRAL-READ-VALUES.
  - The convention and P O23: MEASURED-ABSENT-OR-PRECONDITION,
    P-O23-D5-ON-ITS-OWN-WORDS.
  - The owed registrations: ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC
    (Q-ORG-IDENTITY), B5-RAIL-JOIN-DOES-NOT-DISCHARGE,
    B5-GROUP-COMPOSER-OPENS-EMPTY, B5-INVITE-DIALOG-IS-A-LIST (the three B5
    answers), M-C18-EDITOR-OPENS-UNSAVED, M-C97-LINK-KEYED-DELETE,
    M-C29-DESIGN-FIRST.
  - apply-26's seven: APPLY-DRY-WALK-FIRES-THE-STEP-ROWS,
    SCREENING-QUESTION-RECORD, REFUSED-APPLY-DISCARDS-ITS-DRAFT,
    L3-OPENS-WITH-A-DRAFT-RESIDUE-READ, C-J68-IDS-KEPT,
    JOBHUNT-HOME-KEEPS-ITS-MEANING, JOBHUNT-ROOT-RESOLUTION-ORDER.
  - build-p26's four: EDITOR-TYPEAHEAD-SANCTIONED, ABSENT-ON-HIS-ACCOUNT-PER-ROW,
    OWN-PROFILE-SCROLL-SANCTIONED, LINKS-ARE-NOT-DISCLOSURES.
  - admit26's ten: RECOMMENDATIONS-DETAIL-PAGE-ADMITTED,
    OPEN-TO-WORK-EDITOR-ATTENDED-ONLY, VOLUNTEERING-BARE-SPELLING-FIRST,
    VERIFICATIONS-PAGE-ADMITTED, NAME-BEARING-ADDRESS-REDACTION-SCOPE,
    AI-GENERATION-IS-A-NON-OUTWARD-WRITE, AI-COACH-OUTSIDE-PURPOSE,
    COURSE-VIDEO-OUTSIDE-PURPOSE, AD-LIBRARY-OUTSIDE-PURPOSE,
    RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE. The order named eleven; the
    notes name ten question ids, so ten are registered.
  - build-jmn26's four: N-102-MOVES-WITH-J-108, J-19-BUILT-BEHIND-THE-GRANT,
    J-110-SPLITS-HOME-AND-POSTS, J-163-RECEIPT-ONLY-WRITE.
- `_audit/2026-11-26-rulings-search-route.md`: the three from the entry of
  2026-11-26 at 01:20, on the classic job search's retirement:
  SEARCH-ROUTE-CLASSIC-PRIMARY (Q-SEARCH-ROUTE-POLICY),
  FILTER-REQUERY-COUNTS-AS-A-SEARCH (Q-FILTER-FIRES-SEARCH-CAP),
  RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE (Q-RETIRED-ROUTE-ROWS).

Each id that answers a ledger question carries that question's id as an alias.
`N-102-MOVES-WITH-J-108` supersedes the outcome integration 2's section 6
recorded for `N 102`. The two records carry the `CORRECTS` / `CORRECTED BY`
pair.

NOT registered, because none is a ruling here:

- `Q-AWAY-MESSAGE` (row `M M39`): put to the operator at 22:25 and still
  awaiting his answer.
- session 11's live finding that the `/in/me/` redirect no longer carries
  `isSelfProfile`: a fix lane is owed.
- the 09:10 entry's correction about naukri-gate26: a ruling in another
  repository, outside the entries this pass was given.

## 5. The rows the rulings moved, and the rows they left

MEASURED from merge 4's head against the registration tree, by the census's
own walker and keyed diffs of `next-step.tsv` and `capture-queue.tsv`.

State moves (eight rows, seven of them existing rows):

| row | from -> to | ruling |
|---|---|---|
| `J 153` | GAP -> EXCLUDED-RULED | COURSE-VIDEO-OUTSIDE-PURPOSE (OUTSIDE-THE-PRODUCT-PURPOSE) |
| `J 155` | GAP -> EXCLUDED-RULED | AI-COACH-OUTSIDE-PURPOSE |
| `J 159` | GAP -> EXCLUDED-RULED | AD-LIBRARY-OUTSIDE-PURPOSE |
| `P A14` | GAP -> MEASURED-ABSENT | ABSENT-ON-HIS-ACCOUNT-PER-ROW, under MEASURED-ABSENT-OR-PRECONDITION: a surface not offered to his account (no editor capture draws a postal-code control; build-p26's record, section 2) |
| `P A15` | GAP -> MEASURED-ABSENT | the same, for the location display choice |
| `N 102` | GAP -> COVERED-UNFIRED | N-102-MOVES-WITH-J-108: no distinct capability, so it moves with its sibling |
| `J 110` | GAP -> COVERED-UNFIRED | J-110-SPLITS-HOME-AND-POSTS: the row keeps the Home half, built on the real Home-view capture |
| `J 168` | enters, GAP | the Posts half of `J 110`, split under COMPOUND-ROW-SPLITS-ONLY-ON-STATE; next step BUILD on `tests/fixtures/live9/company_root_posts_view.html` |

The split's new row is NUMBERED, `J 168`, not `J 110b`.
`scripts/check_jobs_directions.py` takes jobs row ids as numbers only
(`[0-9]{1,3}`), and the jobs slice has no suffixed row. So the Posts half
takes the slice's next number past its maximum, 167. `N 168` set the same
precedent in its own slice: a split that took the next number. The checker is
unchanged. The census population moves 773 -> 774 for this one row
(`tests/census_row_pin.json`, re-pinned).

Side tables, each re-checked green:

- `jobs-directions.tsv`: the lines for `J 153`, `J 155` and `J 159` are gone,
  and `J 110`'s line is re-keyed to `J 168` (still R, ADMITTED, refused by
  RULING on the Posts tab).
- `exclusion-basis.tsv`: +5 lines. `J 153`, `J 155` and `J 159` are class B
  under OUTSIDE-THE-PRODUCT-PURPOSE. `P A14` and `P A15` are class M+, with
  evidence RECORDED and their sources in build-p26's record.
- `read-addresses.tsv`: `N 102`'s line is gone.
- `write-classes.tsv`: the lines for `P A14` and `P A15` are gone (both R3).
- `scripts/triage_read_gap_rows.py`: `N 102`'s two entries are gone, as for a
  row that left GAP.

Next steps re-pointed (42 rows, each state unchanged, GAP; each row's cell
gains a dated note naming its ruling):

| ruling | rows | from -> to |
|---|---|---|
| EDITOR-TYPEAHEAD-SANCTIONED | `P A11`, `P A13`, `P A17` | RULING:Q-EDITOR-TYPEAHEAD -> CAPTURE:C-B1a |
| ABSENT-ON-HIS-ACCOUNT-PER-ROW | `P K8` | RULING:Q-ABSENT-ON-HIS-ACCOUNT -> PRECONDITION (a Top Voice badge awarded to his account) |
| OWN-PROFILE-SCROLL-SANCTIONED | `P D26` | RULING:Q-OWN-PROFILE-SCROLL -> CAPTURE:in-me-profile |
| LINKS-ARE-NOT-DISCLOSURES | `P A25`, `P D25` | CAPTURE:in-me-profile -> RULING:Q-SELF-PROFILE-QUERY-VARIANT (new ledger question) |
| RECOMMENDATIONS-DETAIL-PAGE-ADMITTED | `N 121`-`N 123`, `N 125`-`N 128`, `P F1`, `P F5`-`P F9` (13) | RULING:Q-RECOMMENDATIONS-DETAIL-PAGE -> ADMIT (the recommendations detail page) |
| OPEN-TO-WORK-EDITOR-ATTENDED-ONLY | `P B6`, `P I2`-`P I11` (11) | RULING:Q-OPEN-TO-WORK-EDITOR -> CAPTURE, in a session he attends |
| VOLUNTEERING-BARE-SPELLING-FIRST | `P D24` | RULING:Q-VOLUNTEERING-PROFILE-ID -> ADMIT (the bare spelling first) |
| VERIFICATIONS-PAGE-ADMITTED | `P K1`, `P K7` | RULING:Q-VERIFICATIONS-PAGE -> ADMIT (the verifications page) |
| NAME-BEARING-ADDRESS-REDACTION-SCOPE | `M C80`, `M C82`, `M C101`, `N 55`, `N 56` | RULING:Q-NAME-BEARING-ADDRESS-REDACTION -> ADMIT (the newsletter page, on its drawn slug shape) |
| M-C18-EDITOR-OPENS-UNSAVED | `M C18` | TARGET -> CAPTURE:own-post-reactions (the editor opened and closed unsaved) |
| M-C97-LINK-KEYED-DELETE | `M C97` | RULING:Q-NOTIFICATION-KEY -> CAPTURE:C-I3-1 (the live uniqueness capture) |
| J-163-RECEIPT-ONLY-WRITE | `J 163` | RULING:Q-ONE-SHOT-FEEDBACK -> BUILD behind the grant, on `tests/fixtures/live8/recommended.html` |

The four ADMIT targets are ruled admissible but NOT yet admitted in code. An
admission is an edit to `readonly.py`'s lists, made red-first, and admit26 owns
those lists. So each row's next step is that admission. Each queue line it
waits on reads "ADMIT: <ruling id>" and its session reads "after its
admission". The integrator made no boundary edit.

The capture queue goes from 89 to 87 lines:

- three lines are gone: the ad-library, AI-coach and course-video lines;
- one is added: `C-I3-1`, rank 115, one load of `/notifications/` with no
  press, counting how many cards share each card's link;
- nine change: `C-B1a`; the recommendations, verifications, volunteering and
  newsletter lines; the Open To Work line; `in-me-profile` (the three vetoed
  link presses, build-p26's two and admit26's one, and `P A25`/`P D25` out;
  `P D26` in, with its scroll and no press; 19 rows recounted);
  `own-post-reactions` (+`M C18`); and `t-named-post` (`M C18` and its target
  out).

Rows LEFT, because the ruling's words do not settle them:

- `N 118`, `P E7` (MEASURED-ABSENT-OR-PRECONDITION: "Reconcile N 118, P E7 and
  the K8 note under it"). Both stay MEASURED-ABSENT. The convention separates
  "does not offer the capability to this account at all" from "offered, but
  needs an account state he lacks". `N 118`'s own cell records that "two
  worlds fit the evidence and nothing on his own account separates them --
  LinkedIn draws the line only for a skill someone endorsed, or it stopped
  drawing it". `P E7` is the same capability. Choosing either world would be
  a guess. The K8 note is reconciled (`P K8` above).
- `P O23` (P-O23-D5-ON-ITS-OWN-WORDS: "adopt D5 NOT-AN-ACT ONLY if the D5 text
  covers it on its own words"). It is not adopted. D5 reads: "A consequence
  of an act that has no control of its own is recorded on the row of the act
  that incurs it", and its REOPENER is "LinkedIn draws a control that turns
  the consequence on or off". The notification of a profile change HAS such a
  control: `P O17`, the switch "Share key profile updates". So D5's words do
  not cover `P O23`, and the row stays GAP on its PRECONDITION.
- `J 78`, `J 116`-`J 120`, `J 126`, `P S2` (AI-GENERATION-IS-A-NON-OUTWARD-WRITE:
  "allowed behind the grant, one capture per feature, quota effect recorded
  on the row"). The ruling settles the class. It names no route to the
  capture. Each row's queue line loads an address the read boundary refuses:
  the guide overlay for `J 78`, `J 116`-`J 120` and `J 126`, and the enhance
  overlay for `P S2`. The ruling makes that load a write behind the grant,
  which no capture line can take, because the ledger has no capture class for
  a load behind the write grant. So each row keeps its step,
  `RULING:Q-AI-GENERATING-LOADS`, and its four queue lines keep their session
  "after Q-AI-GENERATING-LOADS".
- `M C79`, `N 41`, `N 42` (NAME-BEARING-ADDRESS-REDACTION-SCOPE: "article page
  after a capture spells it"). No capture has spelled the article address.
- `P M11` (RESUME-BUILDER-UNDER-ARTICLE-COMPOSER-CAPTURE: "once a capture
  finds where LinkedIn draws it"). No capture has.
- `N 104` (ORG-NAME-AT-RUNTIME-LINK-IF-NUMERIC: "link only if numeric; N 104's
  bar still unmet -> GAP"). The ruling keeps the row GAP in its own words.
- `M C29` (M-C29-DESIGN-FIRST: "design-first, queued for the next build
  wave"). The words name a wave, not a step. The row already waits on
  `CAPTURE:C-JMN-4`, the capture build-jmn26 named for its options.
- Rows already where their ruling puts them: `J 19`, at BUILD on
  `tests/fixtures/live2/j18.html` (J-19-BUILT-BEHIND-THE-GRANT); `J 61`-`J 65`,
  at TARGET until he names a posting (APPLY-DRY-WALK-FIRES-THE-STEP-ROWS); and
  `N 63`, `M C61`, at `CAPTURE:C-B5-1` (B5-RAIL-JOIN-DOES-NOT-DISCHARGE).
- `M M39`: its question is not ruled (section 4).

Rulings that move no row by their nature: the four L1 rulings (session 11's
loads), the B5 composer and invite-dialog answers (captures already queued),
apply-26's code and session rulings, and the three search rulings. The first
two search rulings govern code and each session's budget. The third moves
rows only when a capture shows the classic search no longer serves, and no
such capture exists yet.

## 6. Pins, re-derived from the merged tree

Each pin was SET to what `census_completion.py --check` measured on the tree
in hand, and never summed. Base 4c62196, merge 4's head, and the registration
tree:

| pin | 4c62196 | merge 4 | registration |
|---|---|---|---|
| stated_rows | 773 | 773 | 774 |
| adjudicated | 235 | 238 | 245 |
| delivered_broad | 155 | 158 | 160 |
| unfired | 38 | 41 | 43 |
| gap | 538 | 535 | 529 |
| out_of_scope | 63 | 63 | 68 |
| achievable | 710 | 710 | 706 |
| capabilities | 786 | 786 | 787 |
| capabilities_achievable | 723 | 723 | 719 |
| gap_read | 79 | 78 | 77 |
| gap_write | 361 | 361 | 359 |
| gap_unknown | 98 | 96 | 93 |
| b1_no_ruling | 22 | 25 | 27 |
| b3_admitted | 47 | 47 | 46 |
| b3_needs_session | 14 | 13 | 13 |
| jobs_gap | 98 | 96 | 93 |
| jobs_dir_r | 33 | 32 | 30 |
| jobs_dir_w | 57 | 56 | 56 |
| jobs_dir_rw | 8 | 8 | 7 |
| jobs_admitted | 30 | 29 | 29 |
| jobs_refused | 10 | 10 | 7 |

The tool surface is 80 -> 83 tools, as the order predicted (80, plus
build-p26's 1, plus build-jmn26's 2, with no overlap), with 128 -> 134
parameters, all measured at merge 2. The census population is 773 -> 774
(`J 168`). `PINNED_B1_ROWS` gains `J 110` and `N 102`, COVERED-UNFIRED rows
held by no ruling.

The four jobs pins were WITHHELD while the split row carried the id `110b`.
The side table refused it, so the census could not compute them. They were
re-derived once it read `J 168`.

The write-class split is 16 R1 + 34 R2 + 320 R3 = 370 (was 322 R3). In
`scripts/check_write_classes.py`, `P A14` stops being a known-IN control,
because it is no longer a write-direction GAP row. It becomes a known-OUT
answer, and `P A24` takes its place, still GAP on a PRECONDITION.

Census on the registration tree: DELIVERED broad 160 / 706 achievable (22.7%),
strict 117; GAP 529; 774 rows published, 68 out of scope.

## 7. Gates

- Per merge, and again on the registration tree, all green:
  `census_completion.py --check` ("every headline figure matches its pin"),
  `check_next_step`, `check_read_addresses`, `check_jobs_directions`,
  `check_write_classes`, `ruling_holds`, `check_exclusion_basis`,
  `check_cited_shas_resolve`, and `triage_read_gap_rows`.
- The derived views (INDEX, RULINGS, blocker map) were regenerated last after
  every record edit, then `--check` on all three.
- Serial runs under the live flag that went over the 2-minute local cap,
  measured and recorded rather than cut:
  - `tests/test_no_committed_identity.py`, after merge 1: 1170 passed in 144 s;
  - merge 2's surface gate (six files): 213 passed in 126 s;
  - merge 3's boundary gate (five files): 165 passed in 132 s.
  Each ran once. The full suite is CI's.

## 8. Open items this pass leaves

- The four ADMIT targets: the recommendations detail page, the verifications
  page, the bare volunteering spelling, and the newsletter page on its drawn
  slug shape. Each is ruled admissible and needs its `readonly.py` admission,
  red-first, in the next admission pass. Twenty-one rows wait on them.
- `in-me-profile`'s session column still reads 9, though build-p26's notes say
  sessions 9 and 10 did not take it. Session 11's records edit the queue for
  the loads they took, so the value is left for that merge.
- `Q-SELF-PROFILE-QUERY-VARIANT` (`P A25`, `P D25`): a new ledger question
  that LINKS-ARE-NOT-DISCLOSURES owes the orchestrator.
- The AI-generation rows, the article rows, `P M11`, `N 118` and `P E7`, each
  left in section 5 on the ruling's own words.
