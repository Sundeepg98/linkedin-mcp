# A whole-tracked-corpus sweep for blocker evidence -- 6 rows recovered, 22 contradictions read by hand, 4 of them real

**UNASSIGNED moved 284 -> 278.** `_audit/_census/blocker-assignments.tsv` gained
six lines (all `RECON-DOC`), `_audit/_census/blocker-map.tsv` was regenerated
from them (`scripts/build_blocker_map.py --write`), and
`tests/test_blocker_map_is_derived.py`'s ratchet was lowered to match. 7
passed.

This document is the record of what a wider sweep found and did NOT apply --
the ledger-plus-amendments evidence already harvested by this wave's earlier
passes is one source; this pass scanned every tracked file (`_audit/*.md`,
`_audit/_census/*.md`, `linkedin_server/*.py`, `scripts/*.py`, `tests/*.py`,
and the evidence files themselves) for the literal co-occurrence of a blocker
name and a census row id, then diffed the result against the committed map.

---

## 1. THE METHOD, AND TWO BUGS FOUND BEFORE ANYTHING WAS COMMITTED

**Raw scan:** every tracked file, every line containing one of the 97 blocker
names, a context window (that line +/- 6, or the single line for a markdown
table row), regexed for the `SLICE ID` grammar (`J 24`, `P B4`, `M M37`,
`N 149 150 151 160`, `J 132-J 145`, and the bare-sub-id case the census itself
warns about, `C 11` unqualified). 1006 rows of raw evidence (this scan's own
full output, gitignored: `_audit/_scratch/_blocker-rowid-evidence.tsv`).

**Diffed against `scripts/build_blocker_map.py`'s own `build()`** (imported,
not reimplemented) against the frozen 409-row GAP set: 412 candidates carried
a confident, fully-qualified id; 191 CONFIRMED the committed map, 128
apparently CONTRADICTED it, 63 were raw mentions of a currently-UNASSIGNED
row (some of those mutually disagreeing with each other -- 15 rows where my
own scan named more than one blocker for the same row, left alone).

**That 128-CONTRADICTS number was mostly an artifact, not a finding.** A
fixed +/-6-line window spans more than one claim in this repository's dense
enumeration prose -- the ledger's own "A2. THE BOUNDARY: THREE NUMBERS"
appendix lists several unrelated blockers' row-movements a few lines apart,
and a probe script's section-divider comments (`# --- 52 PEOPLE-FOLLOW-LISTS
---`) sit close to a code tuple that names a completely different blocker for
an unrelated id. A proximity filter (keep a candidate only if its blocker is
the NEAREST blocker-name text to the id) cut 128 to 70; a second filter
requiring the id and the blocker name to share a blank-line-delimited
paragraph in the actual file (not just the fixed window) cut that to 22. Both
filters are mechanical and conservative -- see `refine_proximity.py`'s
docstring in the scratch dir for the exact algorithm.

**A tokenizer bug was caught by this refinement, before it reached the
evidence file.** The SLICE-letter matcher had no word-boundary guard, so the
last letter of an ordinary English word immediately followed by a number read
as a slice anchor: `_audit/2026-09-05-article-publish.md`'s sentence "**THE
CAVEAT ON 64**" tokenized as `SLICE "N"` (the N of "ON") + `ID "64"` = a
fabricated `N 64`, which briefly sat in this pass's own "safe to add" list
under `GROUPS-SURFACE` until a manual read of the source (which is about
`MENTION-TAG-CONTROLS`, ledger rank 64, not a census row at all) caught it.
Fixed by requiring both `SLICE` and `ID` tokens to sit on a non-alphanumeric
boundary on both sides. This is a defect in this pass's own instrument, not
in any committed file, and is recorded here because the failure mode --
prose containing "IN 12", "ON 5", "AN 8" and the like -- will recur if this
scan is ever re-run without the fix (the fixed scanner is NOT itself
committed; it lives in the session scratch dir, per this slice's brief).

Separately (found and fixed by a sibling agent in this same wave, not this
pass, while this pass was running): `ledger_counts()`'s hardcoded
`text[140:311]` line slice had gone stale as the ledger grew, silently
truncating the 9-row cost-0 table out of the parse. That fix landed at
`f7594c0` and is why this pass's baseline reads 97 blockers / 409 rows rather
than the 88/359 a run five minutes earlier would have shown. Recorded here
only because this pass's own first "fresh" reading briefly showed the two
downstream test failures that bug causes, before the sibling's fix was
visible on disk.

Every surviving candidate -- all 6 additions and all 22 refined
contradictions -- was then read by hand against its source before this
document or the evidence file was written.

---

## 2. THE SIX ADDITIONS

All six are `RECON-DOC`: none is the 2026-09-03 ledger itself, and no commit
was found that acted on any of them by changing a row's state.

| row | blocker | source | why |
|---|---|---|---|
| `M C61` | `GROUPS-SURFACE` | `scripts/_probe_group_row_affordances.py:36` | "the five suggestion rows have no join control ... the join rows are `N 63`, `N 163`, `M C61`" -- corroborated independently in `_audit/2026-09-05-groups-surface-measured.md:213`, table 5.4 |
| `N 63` | `GROUPS-SURFACE` | same | same sentence |
| `N 163` | `GROUPS-SURFACE` | same | same sentence |
| `M C70` | `SEARCH-RESULTS-SURFACE` | `_audit/2026-09-05-groups-surface-measured.md:213` | table 5.4 explicitly carves this OUT of the document's own GROUPS-SURFACE allowlist need: "search inside Groups ... belongs to `SEARCH-RESULTS-SURFACE`, which is queued DECIDE and is not this blocker's to inherit" |
| `N 161` | `SEARCH-RESULTS-SURFACE` | same | same row |
| `N 57` | `NEWSLETTER-SURFACE` | `linkedin_server/readonly.py:684,708` | "`NEWSLETTER-SURFACE`'s reader-side rows -- `N 57` ... and its four neighbours" and later "five of this blocker's reader-side rows (`N 55`, `N 56`, `N 57`, `N 58`, `M C80`)" |

**`N 57`'s four named neighbours were NOT added.** `N 55`, `N 56`, `N 58` and
`M C80` are also claimed elsewhere (the ledger's own A9-adjacent
redaction-fork discussion ties `N 55`, `N 56`, `M C80` to
`OWNED-BY-A-SIBLING-SLICE`, `EVENTS-SURFACE` and `GROUPS-SURFACE` in the same
breath) -- this pass's own self-conflict check caught the disagreement and
left all four out. Section 4 below has the detail.

**Per-blocker headroom was checked before writing, not after:** `--write`
refuses EVERYTHING if even one blocker would recount above its published
ceiling. `GROUPS-SURFACE` 4 -> 7 of 32 published, `SEARCH-RESULTS-SURFACE`
0 -> 2 of 21, `NEWSLETTER-SURFACE` 0 -> 1 of 12 -- all well clear.

---

## 3. FOUR REAL CONTRADICTIONS, LEFT FOR A PERSON

None of these four was applied. Each is a disagreement between committed
sources (or a source disagreeing with itself), which is a finding to be
adjudicated, never a number a script should absorb.

**A. `N 194` -- committed as `HASHTAG-EXISTENCE`, but the ledger's own later
text moves it.** `_audit/2026-09-03-linkedin-gap-blockers.md:1270`: "`-2
HASHTAG-EXISTENCE` re-filed: `N 194` out to `SEARCH-RESULTS-SURFACE`"; `:1298`:
"`SEARCH-RESULTS-SURFACE` goes 21 -> 22 rows (21 + `N 194` = 22)";
`_audit/2026-09-05-decide-retire-rulings.md:973`: "`N 194` from MEASURE into
`SEARCH-RESULTS-SURFACE` (DECIDE)". This reads as the highest-confidence of
the four: the ledger's own arithmetic (21 -> 22, tied to this exact id) agrees
with itself across two files. The currently-committed `HASHTAG-EXISTENCE`
assignment for `N 194` appears to predate this move.

**B. `J 116`-`J 120` -- committed as `MATCH-DETAILS-COLLAPSED`, but an
amendment proposes a rename the ledger never ruled on.**
`_audit/2026-09-03-linkedin-gap-blockers.md:1236-1242`: "`J 116 117 118 119
120` are not 'a render behind a click', so the blocker's NAME is wrong ... 
closer to `AI-INTERVIEW-PRODUCT` (14 rows, DECIDE-RETIRE) than to the
unopened-menu class. Proposed rename: `AI-ASSISTANT-OVERLAY` -- a proposal,
not a ruling." Neither the committed name nor the comparison name
(`AI-INTERVIEW-PRODUCT`) is what the passage actually settles on -- it
proposes a THIRD name, `AI-ASSISTANT-OVERLAY`, which is not one of the 97 and
was never ruled. Recorded as-is rather than filed under either side.

**C. `M C52` -- committed as `HASHTAG-EXISTENCE` via the ledger's bare `C 52`,
but `_audit/2026-09-05-settings-tail.md:224` names it unambiguously for a
different blocker.** The ledger's own HASHTAG-EXISTENCE table
(`:1157-1158`) writes the sub-id BARE -- "`C 52`" -- which is exactly the
ambiguity the census warns about (`profile.md` and `messaging-and-content.md`
both have a `C` section). Whoever resolved it to `M C52` for the committed
map may have resolved it correctly by topic (hashtags read as a
messaging-and-content capability) -- but `settings-tail.md`'s own table,
which spells the id fully qualified, unambiguous, no guess required, lists:
"| `FEED-PREFERENCES` | `M C52` | 1W | no -- a Help Center article id only |".
Two committed sources now name the SAME fully-qualified id for two different
blockers. One of them is wrong, or the ledger's bare `C 52` was never `M C52`
at all.

**CORRECTED BY:** `_audit/2026-09-19-blocker-conflicts.md` -- the dichotomy above is false on both sides: exactly one census slice carries a C 52 at all, so the bare id is unambiguous, and neither source is mistaken, because the row's capability was rewritten from "Follow a hashtag / topic" to feed preferences seventeen hours before A13 was written, so the two sources read different capabilities under one id. Resolved to FEED-PREFERENCES and applied 2026-09-19.

**D. `M 24` / `M 42` -- the source itself flags the uncertainty.**
`_audit/2026-09-05-decide-retire-rulings.md:114`: "| `MESSAGING-SETTINGS` |
`M M42` | `M M24`, if the classifier put `M 42` rather than `M 24` in
`GROUP-CHAT-SURFACE` |". This is a hypothesis inside an audit document, not an
assertion -- the investigating wave was itself unsure which of `M 24` /
`M 42` the lost classifier meant and which blocker it landed in. Left exactly
as unresolved as its own source leaves it.

---

## 4. EIGHTEEN MORE, READ AND SET ASIDE AS SCANNER NOISE

The remaining 18 of the 22 refined "contradictions" were read against source
and are not real: the committed map already has each of these right, and the
scan's proximity heuristic was fooled by one of two shapes recurring in this
corpus:

* **A short paragraph naming two blockers, each tied to an adjacent but
  different id run.** `_audit/2026-09-03-linkedin-gap-blockers.md:394-401`:
  "Rows `J 9 11 12 13 14 151`. The company filter `J 10` sits one blocker
  along (`COMPANY-ID-RESOLVER`)" -- `JOB-SEARCH-PARAMS` and
  `COMPANY-ID-RESOLVER` sit four words apart, and the heuristic occasionally
  attached the wrong id run to the wrong name. Accounts for 7 of the 18
  (`J 9`, `J 11`-`J 14`, `J 151` misread toward `COMPANY-ID-RESOLVER`; `J 10`
  misread toward `JOB-SEARCH-PARAMS`). Verified against the source: the
  committed map already reads `J 10` = `COMPANY-ID-RESOLVER` and the rest =
  `JOB-SEARCH-PARAMS`, which is what the sentence actually says.

* **A code section-divider comment mistaken for a claim.** Both
  `scripts/_probe_network_tail_boundary.py:44` (`P E6`, tagged `ENDORSE` in
  its own tuple, sitting just above a `# --- 52 PEOPLE-FOLLOW-LISTS ---`
  divider for the NEXT block) and `:51` (`N 38`, tagged `FOLLOW-LISTS` in its
  own tuple, just above a `# --- 21 SERVICES-PAGE-SURFACE ---` divider) --
  the divider names the section that FOLLOWS it, not the tuple above it. The
  committed map already has both rows right (`ENDORSE-SUBSTRING-OVERREACH`
  and `PEOPLE-FOLLOW-LISTS` respectively -- the latter added by a sibling
  slice in this same wave while this one was running).

* **Adjacent bullet points in a code comment list.**
  `linkedin_server/readonly.py:604-608` lists four addresses in a row; `N 165`
  belongs to the THIRD bullet ("THE ATTENDEE LIST"), and "`SEARCH-RESULTS-
  SURFACE` again" belongs to the FOURTH ("`/search/results/events/`") --
  adjacent text, different bullets. The committed `GROUPS-SURFACE` assignment
  for `N 165` is independently corroborated by the ledger itself: "`N 165`, a
  group's member list" (section 5, item 4).

---

## 5. FIFTEEN ROWS WHERE THIS SCAN DISAGREED WITH ITSELF

Currently-UNASSIGNED rows where the raw scan named MORE than one blocker
across different files (or different passages of the same file), and were
therefore excluded from section 2 without adjudication:

    J 150    AI-ASSIST-MESSAGING (x3) / GROUP-CHAT-SURFACE / MESSAGING-SETTINGS
    M C80    EVENTS-SURFACE / GROUPS-SURFACE / OWNED-BY-A-SIBLING-SLICE
    M C83    EVENTS-SURFACE / GROUPS-SURFACE / OWNED-BY-A-SIBLING-SLICE
    N 55     EVENTS-SURFACE / GROUPS-SURFACE / OWNED-BY-A-SIBLING-SLICE
    N 56     EVENTS-SURFACE / GROUPS-SURFACE / NEWSLETTER-SURFACE / OWNED-BY-A-SIBLING-SLICE
    N 179    EVENTS-SURFACE / SEARCH-RESULTS-SURFACE
    N 188    EVENTS-SURFACE / SEARCH-RESULTS-SURFACE
    N 189    EVENTS-SURFACE / SEARCH-RESULTS-SURFACE
    N 44     PEOPLE-FOLLOW-LISTS / SERVICES-PAGE-SURFACE
    P H1     HASHTAG-EXISTENCE / INVITE-NOTE-PARAM / SERVICES-PAGE-SURFACE
    P H2     HASHTAG-EXISTENCE / INVITE-NOTE-PARAM / SERVICES-PAGE-SURFACE
    P H10    HASHTAG-EXISTENCE / INVITE-NOTE-PARAM / SERVICES-PAGE-SURFACE
    P H11    HASHTAG-EXISTENCE / SERVICES-PAGE-SURFACE
    P H9     INVITE-NOTE-PARAM / SERVICES-PAGE-SURFACE (x3)
    P L4     EVENTS-SURFACE / GROUPS-SURFACE / OWNED-BY-A-SIBLING-SLICE

Most of the `P H*` and the `OWNED-BY-A-SIBLING-SLICE`-adjacent rows look like
the same two scanner-noise shapes from section 4 (a probe script's per-row
tuples sitting close to unrelated section dividers or ruling text); none was
read to the same depth as sections 2-4 because none is a clean single-blocker
claim to begin with. Left exactly as UNASSIGNED. Not re-scanned further under
this slice's brief.

---

## 6. TWO ROWS THAT WOULD HAVE EXCEEDED THE LEDGER'S PUBLISHED COUNT

Excluded from section 2 automatically, before any human read, because
applying them would have pushed `ANALYTICS-CONTROLS-UNPRESSED` to 5 rows
against a published 4 (current committed recount: 3):

    ANALYTICS-CONTROLS-UNPRESSED  J 28   _audit/2026-09-03-linkedin-gap-blockers.md:491
    ANALYTICS-CONTROLS-UNPRESSED  N 132  _audit/INSTRUMENTS.md:2531

Both pointers are as recorded 2026-09-06 and both name TRACKED files, so they
can be checked from a clone. They were previously deferred to
`_audit/_scratch/_would-exceed-published.tsv` -- 168 bytes, a header and these
two rows -- which is gitignored and reaches no clone and no worktree. INLINED
2026-09-19 rather than tracked: a two-row pointer list is not evidence that
needs a home, it is a sentence, and the quarantine in `.gitignore` exists so
working notes do not ship. Nothing else in that file was load-bearing; it held
nothing but these two lines.

Not investigated further -- `test_no_blocker_recounts_higher_than_the_ledger_
published` exists precisely so this class of disagreement reaches a person
rather than a script.

---

## 7. WHAT THIS DOES NOT CLAIM

No row's STATE was touched or re-adjudicated -- this document and the six
added lines only say which blocker a row belongs to, never whether it is
GAP, EXCLUDED-RULED, or anything else. The four contradictions in section 3
are not resolved here; resolving them means editing
`_audit/_census/blocker-assignments.tsv` by hand and re-running
`scripts/build_blocker_map.py --write`, which is a ruling this document
declines to make on someone else's behalf.
