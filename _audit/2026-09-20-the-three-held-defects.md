# The three held defects

Three census defects that were measured, written up, and then left unapplied.
This wave re-verified each against the live tree before touching it, applied
what could be applied safely, and ruled on what could not.

**CORRECTS:** `_audit/2026-09-20-the-contingent-writeoffs.md` -- the SUBSTANCE of its `J 40` and `J 57` overturns re-verified and HELD, but three things in the prescribed replacements did not: they name a server tool `linkedin_applied_jobs` that exists nowhere in this repository, the fixture denominator is 20 where a recursive enumeration finds 22, and the blocker they re-file onto cannot be created without a ledger act that breaks three pinned assertions.

Everything below is offline: no browser, no LinkedIn session, no page load, no
write fired. Tree at `8b58dcb` when the measurements were taken.

---

## 0. THE LEDGER, UP FRONT

| | |
|---|---|
| rows banked OUT of GAP | **0** |
| rows inflated | **0** |
| census rows whose STATE changed | **0** |
| census rows whose REASON was corrected | **6** (`J 40`, `J 57`, `N 149`, `N 150`, `N 151`, `N 160`) |
| `count_census_states.py` before and after | 704 stated rows / 302 GAP, both runs |
| `build_blocker_map.py` output before and after the census edits | byte-identical |

**Nothing moved a number, and that is the correct outcome rather than a thin
one.** All three defects are defects of REASON, not of state. A reason cell that
asserts something untrue and a reason cell that asserts something true describe
the same capability in the same state; what differs is whether the next person
re-examines it. Two of the three could not be executed as prescribed at all, and
section 3 explains why that is a finding rather than a failure to act.

---

## 1. DEFECT 1 -- `J 40` and `J 57`, written off on reasons measured false

### 1.1 What was re-verified, and whether it still held

The prior wave's section 1.2 made fourteen factual claims. Every one was
re-measured independently against the live tree before anything was applied.

| claim | verdict | evidence |
|---|---|---|
| `J 40` is GAP, and its cell says "Not on any surface this server reads" | **HELD** | shipped parse, `jobs.md` line 226 |
| `jobs_search_hydrated.html` carries "1 company alum works here" | **HELD** | line 528 |
| `job_detail_following_hydrated.html` carries "Company alumni from ..." | **HELD** | byte offset 15668, inside a `<p>` |
| "20 committed HTML fixtures, 2 carry the field, 18 do not" | **MOVED on the denominator, HELD on the substance** | 22 fixtures recursively, 20 at depth 1; still exactly 2 carriers |
| the UN-HYDRATED twins read zero on every needle | **HELD**, by name | the discriminator survives |
| nothing in `linkedin_server/` extracts it | **HELD, and the widening did not refute it** | 2 `alum` hits, both hazard comments; 244 widened hits across five more needles, 0 extractors |
| both addresses still admitted | **HELD** | 35 allowlist patterns / 33 forbidden substrings; both ALLOWED, control refuses twice |
| `J 57` is GAP and sits in section C | **HELD** | line 248, under "### C. Saved jobs and the job tracker (16)" |
| rows 47-49 are COVERED-PROVEN | **HELD** | all three read `CP` |
| those rows are served by `linkedin_saved_jobs`, `linkedin_applied_jobs`, `linkedin_draft_applications` | **REFUTED, two of three** | see 1.2 |
| `referral_join.py` reads another platform's DB read-only | **HELD** | source |
| `warm_referrals` keys on COMPANY, not on a job | **HELD** | source |
| `load_proximity` reads a static extract | **HELD**, and it is 31 days stale | dated 2026-08-20 |
| nothing in the skill reads LinkedIn's own tracker | **HELD** | five needles, zero hits |

### 1.2 The one refutation, and why re-verification was not a formality

The replacement cell written for `J 57` names three tools. Measured at HEAD:

* `linkedin_saved_jobs` is real, but it serves `J 45` "Read the Saved list", not
  `J 47`.
* **`linkedin_applied_jobs` does not exist.** Repo-wide it occurs in exactly one
  place: the document that proposed the replacement. It is not a tool, not a
  docstring, not a test.
* `J 47` and `J 48` are both served by `linkedin_my_applications`.
* Only `linkedin_draft_applications` is named correctly.

Applying the replacement verbatim would have published a tool name this server
does not have, into the census, as a supporting citation for an overturn. The
cell as applied names only the two verified tools.

### 1.3 What was applied

Both reason cells were rewritten. States were NOT touched -- both rows remain
GAP, and `J 40` keeps its `SKILL` tag because the skill genuinely does serve it.
`J 57` LOSES its `SKILL` tag, because the measurement is precisely that the
skill does not serve that row.

`J 40`'s cell now states the field is PRESENT AND UNPARSED rather than absent,
carries the two captures, carries the un-hydrated twins as the discriminator,
and carries a cost, a reopener and a WHO. `J 57`'s cell states that the skill's
join is on a different platform, a different key and a static extract, names the
two verified tracker tools and row 40 as the two halves that already exist, and
records that the missing piece is the JOIN. It also carries forward the warning
that the skill's adjacent join is more valuable than this row and must not be
deleted when this one is built.

### 1.4 What could NOT be applied, and why it is queued rather than done

The prior wave prescribed re-filing both rows onto a NEW blocker,
`PROXIMITY-NOT-PARSED`. Measured: that name occurs zero times in the ledger,
zero times in `blocker-map.tsv`, zero times in `blocker-assignments.tsv`, and
nowhere in the repository except the document that proposed it.

Creating it is a LEDGER act, not a map act, and it breaks three pinned things:

1. `test_no_blocker_recounts_higher_than_the_ledger_published` fails on its
   FIRST assertion -- not the over-count one. `unknown` would be
   `['PROXIMITY-NOT-PARSED']`, a blocker the ledger parse does not know at all.
2. `build_blocker_map.py`'s per-blocker table iterates the ledger's published
   set, so a new name holds rows and is INVISIBLE in the verdict list.
3. The header counts are hardcoded at 97, so "blockers with at least one
   recovered row" would print 95 of 97 with the 95 counting a blocker that is
   not one of the 97.

Adding a `RE_FILED` entry clears the PARTIAL verdict but not the `unknown`
assertion, which keys on the ledger and not on `RE_FILED`. Publishing a new
blocker in the ledger's tables would break
`test_the_ledger_tables_still_total_97_blockers_and_409_rows`.

**So the re-file is DEFERRED with its decision point named: it needs either a
ledger amendment that publishes the blocker and re-totals 97/409, or a re-file
onto a name the ledger already knows. Neither is this wave's to choose.** The
substance is now recorded on the rows themselves, so the next person meets the
measurement rather than the write-off.

---

## 2. DEFECT 2 -- the `reason_doc` column, and the instrument under it

### 2.1 The column was specified against an instrument nobody had measured

`scripts/find_blocker_reason.py` ranks, per blocker, the documents that ARGUE
its reason. A sibling wave's child reported that it had missed the most relevant
document for `SERVICES-PAGE-SURFACE` and found that document only by hand.

That report reproduced exactly. `candidates('SERVICES-PAGE-SURFACE')` returned
three documents and the hand-found one was not among them -- and the CLI never
entered into it, because the omission is in the function's return value. Before
adding a derived column on top of it, the instrument was measured.

### 2.2 Recall, against a set the tool did not build

The validation set is the six blockers that sibling's child researched BY HAND,
with the documents it named in its own deliverable, written before any of this
work began. A tool evaluated on the cases it found is measuring itself.

| variant | found anywhere | in top 3 | at rank 1 | top answer is the generated map |
|---|---|---|---|---|
| **as shipped at `8b58dcb`** | **1 of 8** | 0 of 8 | **0 of 8** | **59 of 97** |
| + F1 vocabulary only | 3 of 8 | 1 of 8 | 0 of 8 | 72 of 97 |
| + F2 paragraph scope only | 3 of 8 | 1 of 8 | 0 of 8 | 19 of 97 |
| + F1 + F2 | 6 of 8 | 4 of 8 | 1 of 8 | 3 of 97 |
| + F1 + F2 + F3 | 6 of 8 | 5 of 8 | 0 of 8 | 0 of 97 |
| **+ F4 row-id join (shipped)** | **8 of 8** | **7 of 8** | **4 of 8** | **0 of 97** |

**THE MIDDLE THREE ROWS AND THE LAST TWO WERE TAKEN WITH REGEXES THAT DIFFER BY
ONE ALTERNATION, and saying so is cheaper than a reader finding it.** The F1
experiment stemmed `blocked` to `block(?:ed|s|ing)?`. That was narrowed back to
`blocked` alone before shipping, because bare "block" is a LinkedIn capability
-- block a member -- and would have fired across the whole messaging census. The
last two rows are the shipped vocabulary; the middle three are the experiment,
and the difference moves one hand-found document by one rank. It changes no
conclusion, which is why it is a footnote and not a re-run.

**A column derived from the shipped tool would have named the generated map as
the document arguing the reason for 59 of 97 blockers** -- and the map is the
file the column lives in.

### 2.3 Four defects, each diagnosed separately so the repair is aimed

**F1 -- every STEM in the vocabulary was dead.** The word list was written with
stems (`refus`, `measur`, `admit`) and wrapped in `\b(...)\b`. A trailing word
boundary after a stem can never match. So `measur` matched NOTHING, in a corpus
where the word "measured" alone appears 1910 times:

    measured 1910   measurement 742   refused 811   refusal 626
    admitted  497   rulings     156   proven  292   shown   334

The comment above the regex said "deliberately broad". The regex delivered the
opposite. Restoring the intended suffixes adds no new concept.

**F2 -- the scoring unit was one physical LINE in a hard-wrapped corpus.**
Measured: `_audit/**/*.md` has a mean non-blank line length of 70.6 characters
and a median of 75 -- hard-wrapped at about 76 columns -- while
`_audit/**/*.tsv` averages 544.5. A sentence spans several lines, so requiring
the blocker name and an argue-word on ONE line measures TYPOGRAPHY. And the bias
is directional: a TSV record is one line, so the derived indexes carried every
word of a record on the blocker's own line and won.

**F3 -- the generated map competed with the prose, and would have been its own
input.** `blocker-map.tsv` is derived from `blocker-assignments.tsv`. It cannot
argue a reason. Worse, with the column added, the locator's answer would depend
on a file the locator's answer is written into -- a fixpoint, since a document
path containing "rulings" would raise that blocker's score for the map itself.
It is now excluded from candidacy by name. `blocker-assignments.tsv` is NOT
excluded: it is hand-written evidence whose notes genuinely argue, and asserting
that distinction is part of the guard.

**F4 -- the join key was the blocker NAME, and this corpus argues by ROW ID.**
A build report argues at length about `J 40` and names its blocker twice in the
whole file. The blocker-to-rows mapping already exists in the artifact being
extended, so the join costs nothing. It is not uniformly better and the one
regression is stated rather than buried: `GROUPS-SURFACE`'s hand-found document
fell from rank 7 to rank 14, because that blocker holds 30 rows and the row net
is correspondingly wide. **Scores are comparable WITHIN a blocker, never
across.**

### 2.4 The re-derived headline, which is worse than the one it replaces

    blockers                                    97
    best argument IS in a reachable document    18
    best argument NOT in a reachable document   79
    NO-ARGUMENT-FOUND, argued nowhere at all     0

Run against the old tool at this same tree, the same three lines read 97 / 9
unreachable / 8 orphaned. **The old "9" was an artifact of the generated map
winning 59 of 97 races, because the map is itself on the reachable list.** With
the map excluded and the recall repaired, the honest figure is that 79 of 97
blockers have their best argument outside the seven documents a reader starting
at the blocker table ever reaches. The orphan count collapsing to zero is the
other half of the same repair: every blocker is argued somewhere.

### 2.5 The column as shipped, and the shape the measurement forced

`reason_doc` is now the tenth column of `_audit/_census/blocker-map.tsv`,
derived on every `--write`, never hand-maintained. It was appended rather than
inserted, so the three columns downstream guards key on are untouched.

**It never carries a bare path.** At 4-of-8 at rank 1, a bare path would be a
coin flip wearing a fact's clothes, and a table reads as data rather than as a
claim -- this repository has already pushed a defect of exactly that family.
Every populated cell states its own rank and score:

    CANDIDATE-1-OF-7 SCORE-11 _audit/2026-09-20-the-contingent-writeoffs.md

with `NO-BLOCKER-ASSIGNED` for unassigned rows and `NO-ARGUMENT-FOUND` where
the locator finds nothing. All rows of a blocker share the value, because the
claim is about the blocker's reason and not about the individual row's.

**The fixpoint was verified rather than assumed:** `--write` run twice produced
a byte-identical file. That only holds because of F3, and it is the property
that makes the column safe to derive from a corpus it lives in.

### 2.6 The other defect fixed while in the file

The default run printed three aggregate counts and an orphan list -- only what
failed a filter. Two readers in one day, including the tool's own author, took
that for a recall bug, because a blocker with a perfectly good best document
looked identical to one with none. A refusal that reports only what it did NOT
match is half a measurement. The default now prints the whole per-blocker
ranking and names the file it did not scan.

Separately, the corpus was re-read and re-scanned once per blocker -- 97 full
passes, over two minutes. It is now read once and matched in a single pass:
**4.4 seconds**, and the guard test over it runs in 6.9.

---

## 3. DEFECT 3 -- the `OWNED-BY-A-SIBLING-SLICE` re-file. THE RULING

### 3.1 What the re-file literally instructs

Queue cell: one word, `RE-FILE`, which the ledger's own queue table defines as
*"Nothing to do but correct the census"*. The why cell, verbatim:

> `N 149 150 151 160` -- network records these as owned by the messaging slice,
> and messaging counts them too

Two things that text does and does not say, because the ruling turns on it:

1. **It does not say "move these rows."** No sentence says move, relocate,
   transfer or re-home. The prescribed act is a bookkeeping correction.
2. **The correction it prescribes is a SUBTRACTION, and the ledger states the
   direction and the amount** -- *"So 409 is at least 4 over-counted."* The
   remedy is to stop counting four rows.

So the whole instruction rests on one asserted premise: *messaging counts them
too*.

### 3.2 The premise, tested row by row

| row | capability | twin in the messaging slice | premise |
|---|---|---|---|
| `N 149` | Report a message | **`M M38`** Report a message as spam, GAP, under `REPORTING-FLOWS` | **TRUE** |
| `N 160` | Send, receive and manage message requests | **`M M6` `M M7` `M M8`** send / accept / decline, all GAP, under `MESSAGE-REQUESTS-SURFACE` | **TRUE** |
| `N 150` | Report a whole conversation thread | **NONE** | **FALSE** |
| `N 151` | Mark a system-flagged message as safe instead of reporting it | **NONE** | **FALSE** |

The zeros are measurements, not glances. Thirty-four needle spellings over
`messaging-and-content.md`, and -- the part the prior wave did not do -- the
SAME thirty-four over `jobs.md`, `profile.md` and `mcp-inventory.md`, with every
non-zero hit read and adjudicated individually. The nearest candidates in the
other slices are a job-posting report, a recommendation-feed dismissal and this
server's own safety machinery; none is a twin. Id-free and repo-wide, the
strings "whole conversation thread" and "system-flagged" occur nowhere outside
the audit tree.

### 3.3 THE RULING

**The re-file is HALF-SOUND, and it may not be executed on either half today.**

**On `N 150` and `N 151` it is wrong, and not in the way it looked.** The
problem is not that the destination slice is the wrong one. Measured across all
four slices and the tool inventory, **there is no destination anywhere.**
Executing the subtraction on these two rows removes two capabilities that no
slice holds, so the census would simply stop describing them. They stay in
`network.md`, and both cells now carry that measurement, so the next reader
meets it rather than the premise.

**On `N 149` and `N 160` the premise is true, but executing it is still not this
wave's call, for three measured reasons:**

1. **There is no precedent in this tree for deleting a capability row.** A
   pickaxe over the full history of `network.md` finds no row text ever removed.
   The nearest analogue -- the messaging slice's own reconciliation, which is a
   model of the work in every other respect -- subtracted in PROSE ONLY: its
   four rows are still table rows with live states and are still counted, 142 by
   machine against 138 in prose. **The precedent everyone points at moved no
   machine number and deleted nothing.**
2. **The twins carry DIFFERENT blockers** from the rows they twin
   (`REPORTING-FLOWS`, `MESSAGE-REQUESTS-SURFACE`, against
   `OWNED-BY-A-SIBLING-SLICE`). A re-file is therefore an accounting act across
   two blockers and a published count, not a move inside one.
3. **The section headings carry their own counts.** `### M. Blocking,
   reporting, muting (14)` holds exactly 14 rows and `### N. Reaching a person
   directly (6)` holds exactly 6. Removing any row leaves a heading asserting a
   number its table no longer holds -- a second stale claim created by the act
   that fixes the first.

**The open decision, named so it can be taken:** does this census de-duplicate
by DELETING the duplicate row, or by MARKING it and leaving it in place? The
only precedent is marking. Nobody has ruled. Until somebody does, the re-file
stays queued -- and it is now queued against rows that carry the measurement,
rather than against rows that carry the premise.

### 3.4 The arithmetic, and one over-claim it exposes

Relocation of all four rows would be 0 rows / 0 GAP net: the census counts all
four slices. The ledger's own *"409 is at least 4 over-counted"* is therefore
**2 genuine de-duplications and 2 capability deletions**, which makes the
over-count claim an over-claim by 2 on this blocker.

### 3.5 The hazard in the brief, measured and NOT reproduced

The brief warned that a union merge had RESURRECTED a deletion, restoring rows
`N 95` and `N 96`. **That could not be reproduced and the evidence runs the
other way.** Both rows are present and GAP today; a pickaxe over the full
history of the file shows exactly ONE commit ever touched either row text, and
it is the commit that CREATED them. There is no removal, therefore no
restoration. The repository has no `.gitattributes` at all, so no union merge
driver is configured for these files or ever was.

What DID happen is a different object with the same words: the two rows'
BLOCKER ASSIGNMENT was deliberately removed, `SEARCH-HISTORY-SURFACE` was
swapped onto `J 18`/`J 19`, and that removal currently holds.

**This strengthens the ruling rather than weakening it.** The control was meant
to show whether a deliberate census-row deletion survives here. It cannot,
because no census row has ever been deleted in this tree -- which is precisely
why `N 150` and `N 151` would be the first, and why that is a ruling and not a
chore.

---

## 4. THE BEFORE / AFTER DIFF, as required

`scripts/build_blocker_map.py --check` before any edit, and `--write` after all
of them. The ENTIRE diff:

    119a120,124
    >
    > reason_doc  blockers with a ranked candidate  97 of 98
    >   the cell carries RANK and SCORE, never a bare path: the locator's
    >   measured at-rank-1 is 4 of 8 (see find_blocker_reason.py)
    >
    > wrote _audit/_census/blocker-map.tsv  409 data lines

Every other line is identical: 409 frozen GAP rows, 97 blockers / 409 rows
parsed, 390 assigned, 19 UNASSIGNED, 86 complete / 8 partial / 3 absent, 108
rows left GAP since the freeze, 1 entered (`P L2b`), 302 today, and the same six
`J 78`-`J 83` NAMED-UNFILEABLE rows. **The census edits moved nothing, and the
column added nothing but itself.** Re-running `--write` after the census edits
produced output byte-identical to the run before them.

### 4.1 And again after merging master, because a derived column must be re-derived

`origin/master` gained the `live-capture` wave's commit while this wave ran, and
it touches the SAME two census files. Merged in here rather than left for the
integrator. It auto-merged with no conflict, and **both sides were verified by
RE-READING the files rather than by trusting the merge**: that wave's two
promotions and all six of this wave's corrected cells are present on disk. There
is no row overlap at all -- it edited `J 123`, `J 136`-`J 138` and `N 135`.

Its two promotions are COVERED-UNFIRED to COVERED-PROVEN, so the GAP numerator
does not move. Re-measured on the merged tree, every figure above is unchanged:
704 stated rows, 302 GAP, 409 frozen, 97 blockers / 409 rows, 390 assigned, 19
UNASSIGNED, 86 complete / 8 partial / 3 absent, 108 left, 1 entered, 302 today.

**`reason_doc` DID move, for eleven blockers, and that is the column working.**
The merge added a 501-line audit document, which is corpus the locator reads.
Nine of the eleven are candidate-count increments. One is substantive:
`OWNED-BY-A-SIBLING-SLICE` goes from score 2 to score 6 and now points at this
document, which argues that blocker at length where the previous best merely
named it. A cached column would have kept the old answer and been quietly wrong;
this one was re-derived and committed.

---

## 5. INSTRUMENTS

### 5.1 The locator recall guard

`tests/test_the_blocker_reason_locator_states_its_recall.py` -- 27 checks over
the locator: the known miss, the recall floors, the generated-artifact
exclusion, the rank-1 ceiling that guards the column's shape, the column's own
cell format, and a parametrised assertion that every stem in the vocabulary
matches its word forms.

**SHOWN FAILING**, against the module as of `8b58dcb`, loaded from git and
pointed at the real corpus (the first attempt scanned an empty directory and
produced a false red, which is why the harness now asserts its corpus size
before trusting a zero):

    FAILED  test_the_known_miss_is_found
            candidate list is 3 documents and does not contain
            _audit/2026-09-20-the-contingent-writeoffs.md
    FAILED  test_recall_against_a_hand_built_set_does_not_regress
            finds 1 of 8 hand-found documents anywhere, floor is 8
    FAILED  test_no_generated_artifact_is_ever_a_candidate
            generated artifacts appear as candidates:
            {'_audit/_census/blocker-map.tsv': 81}
    FAILED  test_every_stem...[measured] [refused] [refusal] [admitted]
            [rulings] [proven] [shown]     -- 7 parametrised cases
    10 FAILED, 0 passed against the old module.

The rank-1 assertion is a CEILING and will fail if somebody genuinely improves
the ranking. That is deliberate: at that point the column's shape should be
re-decided rather than inherited.

### 5.2 The unpublished-blocker check in `build_blocker_map.py`

Section 1.4 could only be written because a TEST catches a blocker the ledger
does not publish. The SCRIPT said nothing: its per-blocker table iterates the
published set, so rows filed onto an unpublished name are simply absent from
it, and its two headline counts were written against a hardcoded 97. A reader
running `--check` on the re-file this wave declined would have seen a clean
table with two rows quietly missing.

It now prints what it DID see, and fails. Control and mutation, the mutation
injected by wrapping `build()` rather than by editing the shared evidence file,
which is another wave's ground:

    CONTROL    unmodified build                                 exit 0, silent
    MUTATION   J 40 and J 57 filed onto PROXIMITY-NOT-PARSED    exit 1

      FAIL: the map holds 1 blocker(s) the ledger does not publish, so they
      appear NOWHERE in the per-blocker table below and are not counted in
      any total on this page:
        PROXIMITY-NOT-PARSED   holds 2 row(s), published nowhere

The two headline counts are now derived from the parsed ledger rather than
from the literal 97, so they cannot report a total that includes a blocker
which is not one of them.

---

## 6. DEFECTS HANDED ON

1. **`linkedin_applied_jobs` does not exist** and is named as a server tool in
   the document named in this file's own marker above. The source document now
   carries the back-pointer.
2. **`PROXIMITY-NOT-PARSED` cannot be created without a ledger act.** Section
   1.4 prices it. Needs a ruling.
3. **De-duplication policy is unruled.** Delete the duplicate row, or mark it?
   Section 3.3. `N 149`/`N 160` are blocked on this and so is every future
   cross-slice re-file.
4. **The map's locator for these four rows has rotted.** It records
   `L296,L537,L647`; the real occurrences are at L325 and L558 and there is no
   third. A line-number citation does not dangle, it rots into a plausible wrong
   answer. Cite symbols or row ids.
5. **`N 95`/`N 96` carry a live contradiction** between two same-day documents,
   one saying the pair is settled onto the jobs rows and the other saying they
   were carved back. Nobody has closed it.
6. **A new blocker name was structurally invisible** in
   `build_blocker_map.py`'s per-blocker verdict table, and its header counts
   were hardcoded at 97. **FIXED HERE** -- see section 5.2. The script now
   names any blocker the ledger does not publish, says that such a blocker
   appears nowhere in the table below it, and fails.
7. **Section heading counts are hand-maintained** and will go stale on the first
   row that moves. Nothing derives them.
8. **The InMail ledger file the skill models a balance from does not exist**, so
   `credits()` runs entirely on a hardcoded fallback. Relevant to `J 127`, not
   to any row this wave touched.

---

## 7. WHAT THIS WAVE DID NOT DO

No browser, no session, no write, no page load. It did not touch the published
split, `M C82`, the `SURFACE?` blocker class, gate-floor latency, the live
capture or the SHA-citation repair -- all live in sibling worktrees. It did not
change a single census STATE, did not create or retire a blocker, and did not
execute either half of the queued re-file.
