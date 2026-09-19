# Four defects found in passing, fixed

Wave `census-defects`, 2026-09-19. All four were reported by
`_audit/2026-09-19-the-four-absent-blockers.md` section 5, by a wave that
correctly refused to widen its own scope. Every fix below ships with a control
that was SHOWN FAILING before it passed.

**HEADLINE NUMBERS, so nobody has to read to find them.**

| number | before | after | moved? |
|---|---:|---:|---|
| frozen GAP rows at `1c08e5f` -- **the 409** | 409 | **409** | **NO** |
| frozen STATED rows at `1c08e5f` -- the 690 | 690 | **692** | yes, +2 |
| GAP rows at HEAD | 303 | 303 | no |
| STATED rows at HEAD | 704 | 704 | no |
| UNASSIGNED rows the map calls unnamed | 21 | 15 | 6 reclassified, none filed |

**Nothing was renumbered, re-filed or moved.** No census row changed state, no
row changed id, `blocker-assignments.tsv` was not touched, and
`build_blocker_map.py --write` was NOT run.

---

## 1. A STATE-CELL DIALECT SILENTLY DELETED ROWS FROM THE CENSUS

### 1.1 What it was

`scripts/count_census_states.state_of` returned the empty string for a state
cell it could not spell. An empty string removes a row from the NUMERATOR and
the DENOMINATOR at the same instant -- no error, no exception, and no diff that
looks like a state change. `messaging-and-content.md` wrote `**CANNOT-DELIVER**`
where the shipped vocabulary held only `COVERED-CANNOT-DELIVER`, so the rows
wearing it were in neither.

`XR` was the same class a fortnight earlier: 23 correctly-written verdicts
invisible because `jobs.md` used its own short spelling. Two instances make it
a class, and a class gets a guard rather than a third correction.

### 1.2 The sweep, and what it found -- IT IS TWO ROWS, NOT ONE

The brief named `M 1`. Swept properly it is **`M M1` AND `M M2`**. `M M2`
"Send an InMail to a non-connection" carries the identical cell and is named in
no document anywhere in this repository.

    scripts/census_dialect_sweep.py --all-history --withdraw CANNOT-DELIVER

    commits that have ever touched the four counted slices: 61
    distinct (file, row, dialect) triples across ALL history: 2
      messaging-and-content.md row M1  CANNOT-DELIVER  in 11 commits  2026-09-03..2026-09-05  state_of=['NOTHING']
      messaging-and-content.md row M2  CANNOT-DELIVER  in 11 commits  2026-09-03..2026-09-05  state_of=['NOTHING']

So: **two rows, hidden for eleven commits across three days, and nothing else
in the entire history of this census.** `02e617d` (2026-09-05) rewrote both
cells to the long spelling, which is why HEAD reads zero and why this only ever
mattered to a reader of history -- which is exactly who the frozen `--ref
1c08e5f` reading serves.

The sweep covers **every** markdown file under `_audit/_census/`, not just the
four counted slices. `mcp-inventory.md` runs a deliberately different
vocabulary (`PROVEN-LIVE`, `TESTED-ONLY`, `KNOWN-BROKEN`) and is clean for a
reason worth stating: those spellings share no complete WORD SET with the census
states, so they are a different language rather than a misspelling of this one.

### 1.3 THE NUMBER THIS MOVES, AND THE NUMBER IT DOES NOT

    enumerate_gap_rows.py --ref 1c08e5f --state ALL   690  ->  692
    enumerate_gap_rows.py --ref 1c08e5f --state GAP   409  ->  409

**THE 409 DOES NOT MOVE, AND THAT IS A MEASUREMENT RATHER THAN A HOPE.** Both
hidden rows were CANNOT-DELIVER; neither was ever GAP at any point in its
history. The denominator was wrong by two; the numerator was right.

**A HALF-CORRECTION TO THE REPORTING WAVE, and it is the half that matters.**

**CORRECTS:** `_audit/2026-09-19-the-four-absent-blockers.md` -- section 5 item 4 says the dialect cost `M M1` its membership in "the 690 and the 409"; the 409 half is wrong, because the row was CANNOT-DELIVER and was never GAP, and measured at `1c08e5f` the stated rows go 690 to 692 while GAP stays 409.

That document's own section 4.2 already says it in terms -- *"the row has never
been GAP at any point in its history"* -- so this corrects a SUMMARY that
overstated its own measurement, not the measurement, which was right. It is
declared as a correction rather than merely noted here because a reader
starting from the claim cannot find a note: the back-pointer is the only thing
that makes a correction reachable from the thing it corrects.

### 1.4 The fix

* `scripts/count_census_states.py`
  * `STATES` gains `CANNOT-DELIVER` **under its own key**, never folded into
    `COVERED-CANNOT-DELIVER` -- the same treatment `XR`/`CP`/`CU`/`CCD` get,
    because a counter that silently merges two spellings cannot show you that a
    slice used two. The receipt is in the file.
  * New: `STATE_ATOMS`, `UnknownStateDialect`, `dialect_of`, `classify`.
  * `state_of` now **RAISES** on a dialect instead of returning `''`. `''` now
    means one thing only: the row carries no state cell at all.
  * `main()` collects dialects, prints them under their OWN heading -- never
    mixed into `--unstated`, because the two need opposite fixes -- and exits
    non-zero.
* `scripts/enumerate_gap_rows.py` -- `rows(ref, dialects=None)` refuses by
  default; pass a collector to report them all instead.
* `scripts/build_blocker_map.py` -- `build()` collects dialects into
  `problems`, so the map refuses to WRITE while one is open.
* `tests/test_census_rows_carry_a_state.py` -- now names the CAUSE. A PROSE
  cell is a defect in the row; a DIALECT is a defect in the vocabulary, and
  rewriting the row to satisfy the test would destroy the evidence.

**WHAT A DIALECT IS, stated so it can be argued with:** a cell that is ENTIRELY
a verdict (one to three shouted words, nothing else), where every word is a word
the shipped vocabulary is built from, and the combination is not in the
vocabulary. Prose does not qualify. A neighbouring vocabulary does not qualify.

### 1.5 The controls

**Red first.** The first detector drafted flagged **101 cells at HEAD** --
every `R`, `W` and `REV` column and the whole of `mcp-inventory.md`. A detector
that loud gets switched off within the day, so it was narrowed until it fired on
the real defect and nothing else, and the false positives it once produced are
now pinned as tests.

**`tests/test_state_cell_dialects_refuse_loudly.py` -- 35 tests. With the fix
reverted on disk: 35 failed. With it restored: 35 passed.** Not a fixture:

* `state_of` on the **genuine frozen `M1` row, read out of `1c08e5f` by `git
  show`**, with the spelling withdrawn, raises -- and returned `''` before.
  That is the historical defect reproduced, not a model of it.
* The frozen enumeration is asserted **in both directions**: 692 with the
  spelling taught, 690 with it withdrawn. Pinning only 692 would pass just as
  happily if the detector were deleted.
* 409 asserted under BOTH readings, plus that the two recovered rows are
  `CANNOT-DELIVER` and not GAP.
* `N 174`'s real prose cell (`**MEASURED AND DELIBERATELY NOT CLOSED ...**`,
  which opens on a vocabulary word) must NOT be a dialect. The false positive
  designed out, pinned.
* Both halves of the detector: seven strings that must be dialects, fifteen
  that must not.

**`scripts/census_dialect_sweep.py --control`** withdraws the taught spelling,
re-sweeps `1c08e5f`, and FAILS unless it recovers exactly `M1` and `M2`. A
sweep that reports nothing is indistinguishable from a sweep that cannot see.

**AN INSTRUMENT DEFECT CAUGHT BY ITS OWN CONTROL.** The first `--all-history`
run returned **0 triples** and was nearly written up as "the dialect never cost
anything". It returned 0 because the spelling was by then TAUGHT, so the sweep
was blind to it by construction -- true about today, useless about the past.
Hence `--withdraw`, which is not a convenience but the archaeology: without a
withdrawal the sweep asks *is anything hidden from the counter as it stands
now*; with one it asks *what did this spelling cost before anyone taught it*.

### 1.6 One consequence for the integrator

`build()`'s frozen row set gains `M M1` and `M M2`. An evidence line naming
either now reports `NOT-GAP-AT-FREEZE` instead of `UNRESOLVED id` -- a strictly
better diagnosis, and relevant to `MESSAGE-ADDRESSING`, whose only named row is
`M M1`. It confirms rather than disturbs that wave's conclusion: the row is
visible now and it is still not GAP, so the published count still has no
referent inside the 409.

---

## 2. THE MAP'S `UNASSIGNED` REASON CELL WAS FALSE FOR `J 78`-`J 83`

### 2.1 What it was

Every unassigned row carried one generated sentence: *"no committed source
names this row against any blocker"*. That is a **universal negative asserted
from a lookup in ONE file**, and it was false for six rows:
`scripts/_probe_jobs_tail_boundary.py` (tracked) carries, at the line the
generator now computes:

    # 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83.

The defect is bigger than six cells. The sentence was never a measurement for
ANY row -- it was a default that happened to be true for most of them.

### 2.2 Why the six still cannot be filed

The probe names **six** rows; the ledger publishes `PREMIUM-APPLY-SURFACES` at
**five** (`2026-09-03-linkedin-gap-blockers.md`, ranked table row 61). Filing
all six trips the over-count assertion. Filing five of six is a CHOICE wearing a
forced row's clothes -- the exact reasoning that pulled `J 82` back out of this
same blocker earlier today. So the rows stay UNASSIGNED and the CELL changes.

### 2.3 The fix

`scripts/build_blocker_map.py` gains `NAMED_BY_PROBES`, `PROBE_MARK`,
`_expand`, `probe_marks()` and `unassigned_row()`. The cell now reads, for each
of the six:

    NAMED-UNFILEABLE -- named against PREMIUM-APPLY-SURFACES by
    scripts/_probe_jobs_tail_boundary.py:L63, the mark names 6 rows and the
    ledger publishes PREMIUM-APPLY-SURFACES at 5; filing them all would trip
    the over-count assertion, and filing 5 of 6 would be a CHOICE wearing a
    forced row's clothes

and for a row nothing names, the default now states its own scope instead of
asserting a universal:

    no line in blocker-assignments.tsv files this row, and no probe mark in
    scripts/_probe_jobs_tail_boundary.py names it

**EVERYTHING IS DERIVED, NOTHING IS RETYPED.** The blocker name, the row range,
the row count and the line number are parsed out of the probe on every run; the
published count comes from the ledger's own tables. A hand-written cell would
have gone stale in silence. If the mark stops parsing, `probe_marks()` returns a
PROBLEM, `build()` carries it, and the map refuses to write rather than
reverting to the sentence that was measured false.

**TWO COLUMNS WERE DELIBERATELY LEFT ALONE.** `blocker` and `evidence_class`
stay `UNASSIGNED`. Naming a row is not filing it, and those two columns are
what `test_blocker_map_is_derived.test_the_committed_map_still_matches_what_the_
evidence_derives` pins against the committed `blocker-map.tsv` that a sibling
regenerates. Moving the distinction into `evidence_class` would have turned a
sibling's tree red to make a point that belongs in the reason cell. The tag
lives at the head of the NOTE, where it is still greppable, and the previously
empty `source` and `locator` columns now carry the citation.

### 2.4 The controls

`tests/test_the_unassigned_reason_is_not_a_default.py`, 13 tests:

* The PREMISE is measured before anything is asserted about the cell: if the
  probe stops naming the six, the test says so rather than asserting a story.
* The computed locator is checked against the file -- the line at `L63` must
  actually contain the mark, so a citation cannot rot into a plausible wrong
  answer.
* `THE_FALSE_DEFAULT` is kept verbatim and asserted ABSENT from both branches,
  so the old sentence cannot come back unnoticed.
* **The derivation is proved to be one**: feed `unassigned_row` a published
  count of 5, 9, and missing-entirely, and the cell's argument changes each
  time. That is what separates a derivation from a sentence that happens to be
  true today.
* **The failure mode fires**: point `NAMED_BY_PROBES` at a probe with no mark
  and at a file that does not exist -- each returns a problem, and the six rows
  fall back to the SCOPED default, never the universal negative.
* The row-spec grammar, on all three real marks plus edge cases.

---

## 3. A DEFERRED-TO DOCUMENT IS NOT TRACKED

### 3.1 The ruling: THE REFERRERS ARE THE DEFECT

The deciding question is whether anything in section 47 is load-bearing for a
claim the referring documents make. **It is not**, and the fork resolves on
that:

* `2026-09-19-the-empty-blockers.md` **quotes every cell it uses, verbatim**
  (`"8 candidates for 2 slots; 21 survive the split"`). Its own section 3
  records being MISLED by section 47 and getting three blockers wrong. Nothing
  rests on re-reading it -- the document already treats it as a hazard.
* `2026-09-19-blocker-map-ruling-requests.md` deferred for the remaining
  blockers' candidate counts. That is **DERIVABLE from committed code**:
  `scripts/build_blocker_map.py --check` recomputes every per-blocker hole from
  committed sources on demand. The document's own next paragraph already
  restates the closing arithmetic (31 / 10 / 10).

Four more reasons not to track it:

1. **The quarantine is a RULING with a dated rationale**, committed in
   `.gitignore` (the `_audit/_scratch/` entry) and pinned by
   `tests/test_every_ignore_entry_is_declared.py`. Its stated purpose is that
   working notes cannot be swept into a commit. Carving an exception is how a
   rule its own repo violates gets deleted, taking the protection with it --
   which that comment block says in as many words.
2. **The file is a live work log, not an artifact**: 1317 lines, eleven
   chronological passes with wall-clock banners, first-person narration, dead
   ends and self-corrections. Section 47 is one table inside it.
3. **It goes stale in minutes.** Section 47 is a 12:21 snapshot; a document
   that trusted it was wrong about three blockers by 12:40. Committing it
   freezes a quotation that was already aging when it was cited.
4. **It was still being written tonight** (68980 bytes, mtime 22:40). Committing
   a moving target is how a stale reading becomes a permanent one.

### 3.2 What was corrected

* `_audit/2026-09-19-blocker-map-ruling-requests.md` -- the deferral is replaced
  with the claim stated here, the path demoted to PROVENANCE with the reason it
  cannot be read, and a pointer to the instrument that RECOMPUTES the
  enumeration instead of a copied table that would age from the moment it landed.
* `_audit/2026-09-19-the-empty-blockers.md` -- both references marked, at first
  mention and at the deferral.
* **A THIRD INSTANCE THE GUARD FOUND, that nobody had looked for:**
  `_audit/_census/network.md` section 9.2 deferred the enumeration of 24
  linked-but-unwalked pages to `_audit/_scratch/_census-hc-following.md`. Marked.
  This is the argument for the guard existing at all -- two waves had read the
  defect report naming the first two and nobody asked whether there were others.
  **It is a NOTE cell in a "what was not walked" table: no row id, no state
  cell, no count, nothing renumbered or moved.**

### 3.3 The second scratch file, raised mid-task

`_audit/_scratch/_would-exceed-published.tsv` was flagged as load-bearing for a
live wave. **Measured: it is 168 bytes -- a header and two data rows** -- and
its single committed referrer already states the count inline and already says
the path is gitignored. Its mtime is 2026-09-06 00:01, thirteen days old.

Neither branch of the fork fits a two-row pointer list, so it took the third
road: **the two rows were INLINED** into
`_audit/2026-09-06-corpus-sweep-blocker-evidence.md`. Both point at TRACKED
files, so they are now checkable from a clone, and the dependency is gone
rather than relocated. Consistent with the ruling: load-bearing content gets
STATED in the committed document; the scratch file stays scratch.

### 3.4 The control

`tests/test_no_committed_document_defers_to_an_ignored_path.py`, 8 tests.

**The scope is what makes it keepable, and it was measured before it was
written.** Over the 150 tracked documents under `_audit/`: **60 paragraphs name
a file under `_audit/_scratch/`, and only ONE deferred without saying the path
was unreadable.** The repository already has the convention --
`test_readonly_boundary_invariant.py` writes *"which is gitignored, so THE
EVIDENCE DOES NOT ..."* -- and 59 of 60 keep it. A guard demanding a marker on
every MENTION would have been red on thirty documents on the day it landed, so
it fires only on DEFERRAL (the claim is not here; go and read it) and not on
CITATION (the claim is here; the path is provenance).

**Shown failing on three REAL paragraphs**, kept verbatim in the test: the
pre-fix text of both referring documents and the `network.md` cell. Four
negative fixtures pin the other side -- an ordinary citation, a marked
deferral, a mention of the directory rather than a file, and a deferral to a
TRACKED path -- so the guard cannot be widened into one that flags citations.

---

## 4. THREE CITED SHAs OFF THE HISTORY LINE

**No citation was rewritten. The integrator owns that repair.** This section is
classification only.

### 4.1 All three are the same class -- CONFIRMED

Measured directly in this worktree:

| cited | resolves | ancestor of HEAD | twin in history | twin's author-date + subject |
|---|---|---|---|---|
| `12c20e1` | yes | **no** | `e72af67` | identical, and `e72af67` IS an ancestor |
| `1349fe6` | yes | **no** | `81c8534` | identical, and `81c8534` IS an ancestor |
| `c1991ac` | yes | **no** | `0aca3d0` | identical, and `0aca3d0` IS an ancestor |

Each old/new pair shares author-date to the second AND subject character for
character (12:27:28, 12:31:30, 12:41:30 IST). **All three meet every condition
of the rewrite class. None is a different defect.**

### 4.2 BUT A SECOND CLASS EXISTS, AND IT IS NOT A DEFECT -- DO NOT REPAIR IT

Sweeping the tracked tree for every cited hex token that is a real commit object
turns up **four more** off-history SHAs that the rewrite does NOT explain:

| sha | cited in | twins | branches containing it |
|---|---|---:|---|
| `0f711c1` | `2026-09-19-search-shaper.md` | **0** | `integrate-1821`, `worktree-agent-a4a7c41bdf3ec4b68` |
| `76caeb6` | `2026-09-19-search-shaper.md` | **0** | `integrate-1821`, `worktree-agent-a4a7c41bdf3ec4b68` |
| `5581950` | `2026-09-19-routing-the-unassigned.md` | **0** | `integrate-1821`, `worktree-agent-aa255d5b6ed0788c7` |
| `86b8ed5` | `2026-09-19-routing-the-unassigned.md` | **0** | `integrate-1821`, `worktree-agent-*` |

These are **unmerged sibling work, not rewrite casualties**, and the
discriminator is mechanical: their **author-date equals their committer-date**
(18:02-18:26 IST tonight), which a filter-repo style rewrite never leaves --
the rewrite preserves author-date and moves committer-date. They have zero
twins because they have not been replayed; they simply are not on this branch
yet. `integrate-1821` holds 477 commits this branch does not.

**THE OPERATIONAL WARNING:** a repair map keyed on "cited sha is not an ancestor
of HEAD" would sweep these four in and rewrite four CORRECT citations into
something else. The repair must be keyed on **"has an identical (author-date,
subject) twin that IS an ancestor"**, which is exactly the three in 4.1 and
excludes all four here. The four need no action: they become ancestors when the
integrator merges.

---

## 5. WHAT THIS WAVE DID NOT DO

* Did not run `build_blocker_map.py --write`. The `.tsv` still carries the old
  reason strings and will pick up the new ones on the integrator's regeneration.
* Did not touch `_audit/_census/blocker-assignments.tsv`.
* Did not move, renumber or re-file any census row, and did not change any
  row's state. The only census-slice edit is one NOTE cell in `network.md`
  section 9.2 (a "what was not walked" table, no row id, no state, no count) --
  revertible in one line if a sibling conflicts.
* Did not rewrite any commit sha citation.
* Did not change any FINDING in `2026-09-19-the-four-absent-blockers.md`. One
  line was added to it: the `CORRECTED BY:` back-pointer this corpus requires,
  so that a reader arriving at section 5 item 4 can reach the correction in 1.3.
  Its measurements are untouched, and its section 4.2 was right all along.
  **That back-pointer was NOT in the first draft of this wave** -- the intent
  was to state the correction here and leave their document alone. The shipped
  guard `tests/test_a_correction_is_findable_from_the_claim.py` refused it, and
  refused correctly: a correction nobody can find from the claim is not one.

## 6. FILES

Changed:

    scripts/count_census_states.py
    scripts/enumerate_gap_rows.py
    scripts/build_blocker_map.py
    tests/test_census_rows_carry_a_state.py
    tests/test_a_correction_is_findable_from_the_claim.py   (NOT_A_CORRECTION entry)
    _audit/2026-09-19-blocker-map-ruling-requests.md
    _audit/2026-09-19-the-empty-blockers.md
    _audit/2026-09-06-corpus-sweep-blocker-evidence.md
    _audit/_census/network.md                               (one note cell)

Added:

    scripts/census_dialect_sweep.py
    tests/test_state_cell_dialects_refuse_loudly.py
    tests/test_the_unassigned_reason_is_not_a_default.py
    tests/test_no_committed_document_defers_to_an_ignored_path.py

## 7. FOR THE INSTRUMENT REGISTER

`scripts/census_dialect_sweep.py` -- sweeps every file under `_audit/_census/`
for state cells the shipped counter cannot spell, at HEAD, at a `--ref`, or
across `--all-history`. **Admitted with its control shown firing**: `--control`
withdraws a taught spelling and fails unless it recovers the two known rows.
Carries the `--withdraw` lesson in its docstring: a taught dialect is invisible
to a history sweep by construction, and the run that returned 0 because of it
was nearly believed.
