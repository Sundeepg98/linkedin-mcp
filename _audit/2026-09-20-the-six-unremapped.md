# The six unremapped: SHAs off master's history, and where their content actually lives

Task: repair 11 citations of six commit SHAs (`fa5a314`, `f85e959`, `0f711c1`,
`76caeb6`, `86b8ed5`, `5581950`) across three tracked documents, none of which
resolves as an ancestor of `master`. This is the mapping, the evidence, and the
disposition recommendation for the branches that hold them, including a
mid-task extension the coordinator asked for: the same question over the eight
sibling branches next to `integrate-1821`, not just `integrate-1821` itself.

**PREDICATE USED, STATED SO A LATER READER DOES NOT HAVE TO GUESS:**
`git merge-base --is-ancestor <sha> master`, read by EXIT CODE only (0 =
ancestor, 1 = not). This is NOT `git cat-file -t`, which the prior 670-citation
repair used and which returns `commit` for any object reachable from ANY ref,
local branch or tag -- proving the object exists, never proving it is on
`master`'s line. All six SHAs return exit 1 against `master` and exit 0 against
`integrate-1821`, re-verified in this session at master `8b58dcb8`.

---

## 1. RE-VERIFICATION

**The 11 citations, re-swept just now** (`git grep`, the whole tracked tree,
not only the three named files):

    _audit/2026-09-19-four-defects-fixed.md        4   0f711c1, 76caeb6, 5581950, 86b8ed5
    _audit/2026-09-19-search-shaper.md              5   fa5a314, f85e959, 0f711c1, 76caeb6 (x2)
    _audit/2026-09-19-routing-the-unassigned.md     2   86b8ed5, 5581950
    TOTAL                                          11

No fourth file exists. The count matches the brief exactly.

**Branch containment, exact** (`git branch --contains <sha> --list
"worktree-agent-*" "integrate-1821"`), replacing the `worktree-agent-*`
wildcard the source document used for `86b8ed5` with the one branch it
actually names:

| sha | resolves via |
|---|---|
| `fa5a314`, `f85e959`, `0f711c1`, `76caeb6` | `integrate-1821`, `worktree-agent-a4a7c41bdf3ec4b68` |
| `86b8ed5`, `5581950` | `integrate-1821`, `worktree-agent-aa255d5b6ed0788c7` |

**Zero twins, re-checked rather than trusted.** `master` carries commits with
author-dates in the same 18:02-18:26 IST window on 2026-09-19 (`022c74c3`,
`ea4ee5c9`, `876444ee`, `8e5e5cb1`, `7a6d1dfc`), so the date alone does not
distinguish; none shares a subject line with any of the six, so the
(author-date, subject) predicate the prior repair used returns zero here, as
the brief said. A remap on that predicate is not available for these six and
none is forced.

---

## 2. WHAT ACTUALLY HAPPENED (a squash-replay, not a rewrite)

`master` never merged `integrate-1821`. Commit `fa13985` ("integrate:
eight waves' work, replayed as content onto the purged history",
2026-09-19T19:44:51+05:30) is a single commit whose diff against its parent
equals the CONTENT of `a867dd4..integrate-1821` -- the combined effect of
eight parallel agent branches that day, landed with none of their own commit
objects. Its own message states why: `scripts/purge_denied_term.py` had
rewritten every SHA in the unpushed range to remove three blobs carrying a
real denied term, and rebasing the eight branches back onto that purged line
resurrected the purged blobs (measured, per that commit's own text); the
rebased attempt was deleted rather than pushed, and the branches were instead
replayed as one tree diff, with none of their parents.

Confirmed this session: `fa13985` is the SOLE commit in `master`'s history for
`linkedin_server/search_results.py` and `tests/test_search_results.py`
(`git log --follow master -- <path>` returns exactly one hit for each), and
one of exactly two for `_audit/2026-09-19-search-shaper.md` and
`_audit/2026-09-19-routing-the-unassigned.md` (the second hit is a later
same-day follow-up doc edit, named per row below). `git blame` on every region
cited in section 3 attributes the sampled lines to `fa13985` with no
subsequent master-side edit.

---

## 3. THE MAPPING, ROW BY ROW, WITH EVIDENCE

**None of the six needs "no master commit carries this content."** All six are
on `master`. None gets a literal SHA substitution either: swapping, say,
`76caeb6` for `fa13985` in a citing table would itself be the "plausible wrong
answer" the brief warns about, since `fa13985` carries eight waves' combined
work and is not `76caeb6`'s twin -- it is a container `76caeb6`'s work is one
ingredient of. The repair is an ANNOTATION at each citation site.

### `fa5a314` -- the route half (dom.py, search_results.py, tests)

MASTER COMMIT: `fa13985`. VERBATIM.

The module docstring `fa5a314` wrote for `linkedin_server/search_results.py`
("Shape a SEARCH RESULTS page. No address, query or name crosses the
boundary." through "## CLOSURE ONE: THREE CLOSED SEGMENTS, WHICH IS CONDITION
2 IN CODE", master lines 1-33) is byte-identical to `git show
fa5a314:linkedin_server/search_results.py`'s opening. `git log --follow
master -- linkedin_server/search_results.py` returns only `fa13985`; the file
has not been touched again since.

### `f85e959` -- "this deliverable's first version" (the audit doc itself)

MASTER COMMIT: `fa13985`, NOT A TWIN -- the doc was rewritten on the branch
before the replay.

`f85e959` added `_audit/2026-09-19-search-shaper.md` at 189 lines, titled "The
search-results shaper: built, controlled, and it admits nothing" (only the
route half existed yet). A later branch commit, `76f0c3e9` ("audit(search):
both halves, the brief's count corrected, and what still stands before
admission"), rewrote it to 266 lines before the replay -- 224 insertions, 147
deletions against `f85e959`'s own text, measured with `git diff --stat f85e959
fa13985 -- <path>`. `fa13985` carries that later state, which is what `master`
holds today (title now "both halves, controls shown red, and nothing
admitted"). This is genealogy, not coincidence: `f85e959`'s own text already
reads "`groups.py` -> `menus.py` -> `anchors.py`, each sharper than the last,
all one" and carries "ATTRIBUTION: 0" and a "CONTROLS SHOWN FAILING" heading,
and all three phrases survive verbatim in master's version today.

### `0f711c1` -- CONTROL_EXPECTATION computed (dom.py, search_results.py, tests)

MASTER COMMIT: `fa13985`. Mostly verbatim; one heading later extended by
`76caeb6` itself, in the same file, same session.

`CONTROL_EXPECTATION` is a real dict at `linkedin_server/search_results.py:625`
today; `git blame` attributes the line to `fa13985`. The "TWO LIMITS, MEASURED
RATHER THAN ARGUED" section `0f711c1` wrote is on `master` verbatim for its
first two limits (case sensitivity; the percent-encoded traversal) -- but the
HEADING now reads "THREE LIMITS, MEASURED RATHER THAN ARGUED", because
`76caeb6` (the very next commit against this file) appended a third limit and
renamed the heading in the same diff (`git show 76caeb6 --
linkedin_server/search_results.py` shows the literal `-## TWO LIMITS...` /
`+## THREE LIMITS...` hunk). Ordinary same-author, same-session iteration, not
a replay artifact.

### `76caeb6` -- the filter half (dom.py, search_results.py, tests)

MASTER COMMIT: `fa13985`. VERBATIM.

`FILTER_CONTROL_EXPECTATION` (search_results.py:555) and `tally_filters`
(line 478) are on `master` today; `git blame` on both = `fa13985`. The section
`76caeb6` titled "WHICH CENSUS ROWS THIS SERVES, AND THE ONE IT MUST NOT" and
its "sixteen consecutive FILTER rows" sentence are verbatim on master lines
88-102 today.

### `86b8ed5` -- census, six rows (blocker-assignments.tsv, blocker-map.tsv, doc)

MASTER COMMIT: `fa13985` for the doc and for three of six rows verbatim. The
other three rows each had a SECOND, DIFFERENT commit act on them afterward --
stated per row, because "carried by `fa13985`" is not equally true of all six:

| row | fate on master | evidence |
|---|---|---|
| `COMPANY-PAGE-SURFACE` N 47 | verbatim | byte-identical to `86b8ed5`'s own diff; `git blame` traces the line to `fa13985` |
| `COMPANY-PAGE-SURFACE` N 53 | verbatim | same |
| `COMPANY-PAGE-SURFACE` N 54 | verbatim | same |
| `COMPANY-PAGE-SURFACE` N 33 | verbatim PLUS a same-branch appendix | `fa13985` carries `86b8ed5`'s text unchanged; a later same-branch commit, `1d14fb4e` ("census: N 104, which my own arithmetic had refused..."), appends a dated "AMENDED 18:4x BY ITS OWN AUTHOR" paragraph to the SAME cell, noting the 13R count is now contested. Nothing of `86b8ed5`'s original text is removed. |
| `HASHTAG-EXISTENCE` N 61 | carried, then withdrawn by unrelated LATER master-side work, for a stated reason | `fa13985` adds it verbatim (confirmed: its diff carries a `+` line matching `86b8ed5` character for character). Three hours later, on `master`'s own line -- not the replay -- `c8dd0098` ("the row walk...") reports it as a probable mis-assignment against the ledger's own row-id enumeration of `HASHTAG-EXISTENCE`, explicitly without repairing it ("Not my rows, not my file to rewrite"); `201b757e` ("rule all five requests...") then removes the row: "N 61 REMOVED from HASHTAG-EXISTENCE -- the ledger enumerates that blocker's three rows by id and N 61 is not among them. Two waves found it independently." The row is not on `master` at HEAD. This is ordinary subsequent project work reversing one finding on its own evidence, not a defect of the replay. |
| `PER-MESSAGE-OVERFLOW-MENU` M M11 | conclusion kept, text replaced by an independent parallel commit | `86b8ed5`'s own text (locator `L342`) is not on `master`. In its place is a differently-worded row (locator "M11 row", axis-numbered prose) written by `937b6b71` ("census: five forced rows into four empty blockers..."), a commit that is neither an ancestor nor a descendant of `86b8ed5` (`git merge-base --is-ancestor` fails both directions) yet reaches the same M M11 -> `PER-MESSAGE-OVERFLOW-MENU` filing independently, ten minutes before `5581950`. The merge that combined the eight branches (`50e00eb7`) shows the literal conflict resolution in one hunk: a `+` for `937b6b7`'s text, a `-` for the `L342` text. `86b8ed5`'s specific contribution to this one row did not survive; the row's conclusion did, credited on `master` to a different, independently-arrived-at source. |

### `5581950` -- census, nine rows

MASTER COMMIT: `fa13985` for the doc and for one of nine rows verbatim. Four
rows were superseded by the SAME parallel commit as M M11 above (`937b6b71`);
four more were rewritten in place by a same-branch follow-up (`bedfb027`)
fourteen minutes later:

| row | fate on master | evidence |
|---|---|---|
| `COMPANY-PAGE-SURFACE` J 86 | verbatim | byte-identical to `5581950`'s own diff |
| `FEED-CONTENT-READ-RULING` M C43 | conclusion kept, text superseded | master's locator reads "C43, C74 rows" (axis style); `5581950`'s own text (locator "L432, L46...") is not on `master`. Written instead by `937b6b71`, same mechanism as M M11 above -- confirmed by direct diff of both sources' text for this row |
| `FEED-CONTENT-READ-RULING` M C74 | conclusion kept, text superseded | same, by `937b6b71` |
| `MESSAGE-REACTION` M M48 | conclusion kept, text superseded | same, by `937b6b71`; `937b6b7`'s own text for this row states "A PRIOR WAVE ALREADY RELEASED THIS ROW IN WRITING" -- it names `5581950`'s finding rather than contradicting it |
| `INMAIL-COMPOSE-SURFACE` J 129 | conclusion kept, text superseded | same, by `937b6b71` |
| `POST-COMMENT-CONTROLS` M C90 | conclusion kept, text rewritten same-branch | `bedfb027` ("census: POST-COMMENT-CONTROLS 3 of 4 and THREAD-REPLY-BOX 1 of 2...", same branch as `5581950`, 14 minutes later) re-adds all four of its own rows with new locator text ("C90 row" etc.) before the replay |
| `POST-COMMENT-CONTROLS` M C23 | same | same, `bedfb027` |
| `POST-COMMENT-CONTROLS` M C29 | same | same, `bedfb027` |
| `THREAD-REPLY-BOX` M M10 | same | same, `bedfb027` |

Total: 1 verbatim + 4 superseded-by-`937b6b71` + 4 rewritten-by-`bedfb027` = 9.
Every row-to-blocker ASSIGNMENT `5581950` made is the assignment `master` holds
today. Unlike `86b8ed5`'s N 61, none of the nine was reversed on the merits;
all nine decisions survive, by three different routes.

---

## 4. WHY AN ANNOTATION, NOT A TABLE-CELL REMAP

A dangling SHA is honest about its own uselessness; a remapped SHA that looks
plausible is not, because it cannot be caught afterward. `fa13985` is cited in
every row above as the CARRIER, never as a stand-in for what the original
commit specifically did -- and where a later, different commit is the one that
actually carries a given row's surviving text (`937b6b71`, `bedfb027`,
`1d14fb4e`, or the removal at `201b757e`), that commit is named too, because
"carried by the replay" would otherwise overclaim uniformity across six
commits that did not, in fact, all fare the same way.

---

## 5. THE NINE-BRANCH FAMILY (raised mid-task by the coordinator; measured, not inherited)

The coordinator reported: `integrate-1821` plus eight `worktree-agent-*`
branches (`a192c75aa377ee39a`, `a4a7c41bdf3ec4b68`, `a896bdebfb02c851d`,
`aa255d5b6ed0788c7`, `ab006be91a74fe603`, `adefb1d1eadc098c6`,
`ae3487dbfd329de80`, `afec6d8942ca86cc6`) share a 2026-09-05 merge-base with
`master` and add zero files `master` lacks, but flagged that only
`integrate-1821` had been checked at the CONTENT level (census GAP /
COVERED-UNFIRED), and asked that the check either be extended to all nine or
the gap be stated plainly. Extended below, on three independent axes, all
re-run in this session rather than assumed.

**Axis 1 -- shared ancestry.** `git merge-base master <branch>` returns the
identical commit, `0a3c002e`, for all nine. Confirmed, all nine, this session.

**Axis 2 -- file existence.** `git diff --diff-filter=A --name-only master
<branch>` (files present in the branch, absent from master) returns 0 for all
nine. This is a different command from the coordinator's `comm -13` over
`ls-tree` listings, cross-checking the same claim by a different route; both
agree.

**Axis 3 -- content-level census state**, master's own instrument
(`scripts/enumerate_gap_rows.py --ref <branch> --state <GAP|COVERED-UNFIRED>
--count-only`) held constant and pointed at each ref in turn:

| ref | GAP | COVERED-UNFIRED |
|---|---:|---:|
| `master` (baseline) | 302 | 29 |
| `integrate-1821` | 303 | 27 |
| `worktree-agent-a896bdebfb02c851d` | 303 | 27 |
| `worktree-agent-a192c75aa377ee39a` | 311 | 27 |
| `worktree-agent-a4a7c41bdf3ec4b68` | 311 | 27 |
| `worktree-agent-aa255d5b6ed0788c7` | 311 | 27 |
| `worktree-agent-ab006be91a74fe603` | 311 | 27 |
| `worktree-agent-adefb1d1eadc098c6` | 311 | 27 |
| `worktree-agent-ae3487dbfd329de80` | 311 | 27 |
| `worktree-agent-afec6d8942ca86cc6` | 311 | 27 |

`master`'s GAP/COVERED-UNFIRED numbers were independently reproduced in this
session (302/29) before any branch was measured, using system Python against
the identical script -- the venv named in this task's brief does not exist in
this worktree (checked; worktrees do not carry it), and the script has zero
third-party imports, so system Python is an exact substitute here. `master`
scores AHEAD OF OR EQUAL TO every one of the nine on both numbers: lower GAP
is better (fewer unresolved rows) and higher COVERED-UNFIRED is better (more
rows past GAP). Seven of the eight individual branches read WORSE than
`integrate-1821` itself (311 vs 303 GAP), which is the expected shape once you
know each branch is ONE of the eight waves' own isolated work and
`integrate-1821` is their union -- a part cannot out-census the whole it is
part of, and the whole already trails `master`.

**The one gap the coordinator's weaker check could not see, closed:** file
EXISTENCE says nothing about a file present on both sides holding different
CONTENT. Checked this session, `git diff --shortstat master <branch>` for all
nine shows real per-branch diffs (543-723 insertions across 156-164 files
each, exact per-branch numbers on file) that `--diff-filter=A` is blind to by
construction. Traced rather
than waved away: 19 of the 85 modified files (sampled on
`worktree-agent-a192c75aa377ee39a`, cross-checked on `integrate-1821`) are
`_audit/2026-09-05-*.md` documents, and the one common to both samples,
`_audit/2026-09-05-jobs-tail.md`, differs from `master` by exactly 4
insertions / 4 deletions on BOTH branches checked -- consistent with, not
additional to, the ALREADY-DOCUMENTED reason these branches were never
rebased onto `master` in the first place: `fa13985`'s own commit message
states that `scripts/purge_denied_term.py` rewrote `master`'s history to
remove three blobs reachable from `_audit/2026-09-05-jobs-tail.md:403`, and
that rebasing these branches onto the purged line resurrected those blobs.
Seven more of the 85 are `_census/`/`INSTRUMENTS.md` files, which are EXPECTED
to differ given the census kept moving on both lines after the 2026-09-05
split. The remaining ~59 files average under four changed lines each -- small
divergent-edit residue, not a concealed body of work.

**STATED PLAINLY, per the coordinator's own ask:** this closes the file-content
gap for the SAMPLE checked (`a192c75aa377ee39a` in full, `integrate-1821` on
the one shared file), not for a line-by-line audit of all nine branches' full
543-723-line diffs. A full audit of every changed line on all nine was judged
out of scope for a citation-repair task once three independent axes (shared
ancestry, zero added files, master ahead on the one domain-specific metric
that matters here) agreed; if a future reader wants byte-level certainty on
the other seven branches' residue, that is a separate, boundable piece of
work, not a gap this document is hiding.

---

## 6. DISPOSITION RECOMMENDATION

**`integrate-1821`: KEEP, do not delete, do not push, do not modify.** It is
the one branch that alone resolves all six cited SHAs (the two sibling
branches below only cover a subset each); three tracked documents point into
it by SHA today and this document is a fourth. There is no INTEGRATION reason
to keep it -- section 5 shows it adds nothing `master` lacks and trails
`master` on the metric that matters to this repository -- but there is an
EVIDENCE reason: deleting it turns a resolvable-with-effort citation into an
unresolvable one, and that is the harm this whole repair exists to avoid
causing a second time. A tag alongside it (mirroring the standing
`pre-purge-restore` precedent in this same repository) would let a routine
branch sweep remove the BRANCH NAME later without losing the commit it points
at; I have not created one, since naming and placing a fleet-wide anchor tag
is a repository-hygiene decision for whoever owns that sweep, not a citation
repair.

**`worktree-agent-a4a7c41bdf3ec4b68` and `worktree-agent-aa255d5b6ed0788c7`:
redundant resolvers, safe to keep, safe to delete once `integrate-1821` is
anchored.** Everything either one resolves, `integrate-1821` also resolves.
Neither costs anything to keep; neither is load-bearing on its own once
`integrate-1821` is protected.

**The other six (`a192c75aa377ee39a`, `a896bdebfb02c851d`,
`ab006be91a74fe603`, `adefb1d1eadc098c6`, `ae3487dbfd329de80`,
`afec6d8942ca86cc6`): no citation in this repository's tracked documents
resolves through any of them.** Section 5 measured them equal to or behind
`integrate-1821` on every axis checked. From a pure content standpoint they
are deletable; NONE showed a live-worktree marker (`+`) in `git branch -a` at
measurement time, which is reassuring but not authorization. I am not
deleting them: their disposition is a fleet-hygiene call belonging to whoever
manages the other seven agents' worktrees, and it sits outside a closed-form
citation-repair slice. Recorded here so the call can be made with the
measurement in hand rather than repeated from scratch.

---

## 7. WHAT WAS APPLIED TO THE THREE DOCUMENTS

No SHA in any of the three documents was rewritten or deleted. Each of the 11
citation sites now carries, immediately outside its table (never inside a
table body, per this task's own standing hazard), a short dated note: the SHA
does not resolve on `master`, which branch(es) it resolves through, and a
pointer to this document for the row-level mapping. `_audit/2026-09-19-search-shaper.md`
and `_audit/2026-09-19-routing-the-unassigned.md` needed only that. `_audit/2026-09-19-four-defects-fixed.md`
section 4.2 additionally predicted, in its own words, that its four SHAs
"become ancestors when the integrator merges" -- measured now to not be
happening and, per section 5 above, not likely to -- so that document carries
a proper `CORRECTED BY:` back-pointer to this one, and this document carries
the matching `CORRECTS:` declaration, verified against
`tests/test_a_correction_is_findable_from_the_claim.py`.

**CORRECTS:** `_audit/2026-09-19-four-defects-fixed.md` -- section 4.2 predicts its four listed SHAs "become ancestors when the integrator merges"; measured 2026-09-20, no merge happened, master instead carries their content by a squash-replay (commit fa13985), and a nine-branch measurement (section 5 above) found none of the branches on that line would add anything master lacks, so a merge integrating them is neither pending nor likely and the four remain permanently non-ancestors of master.

---

## 8. PREDICATE, FILES, TESTS

**Predicate actually run for the off-master verdict, throughout this
document and in the commit that ships it:** `git merge-base --is-ancestor
<sha> master`, read by exit code. Never `git cat-file -t`.

**Files touched:**

    _audit/2026-09-20-the-six-unremapped.md          (new, this document)
    _audit/2026-09-19-search-shaper.md               (annotation added, table untouched)
    _audit/2026-09-19-routing-the-unassigned.md      (annotation added, table untouched)
    _audit/2026-09-19-four-defects-fixed.md          (CORRECTED BY: paragraph added, table untouched)

**Verified by artifact, not by exit code alone:** every row-level claim above
was checked against the actual git object (`git show <sha>:<path>`, `git
blame`, `git log --follow`, `git diff --stat`), not inferred from commit
subjects. `scripts/build_blocker_map.py --check` was run before and after the
three document edits; its output is unchanged (no table in
`_audit/_census/blocker-map.tsv` was touched by this task, and the check
output matches byte-for-byte).
