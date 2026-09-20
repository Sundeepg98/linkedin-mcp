# Names that do not exist

**Wave:** names-that-do-not-exist. **Date:** 2026-09-20.
**Corpus measured:** the 166 tracked files under `_audit/` at `8b58dcb`, 78,656
lines, 5.1 MB -- the corpus as other waves left it, before this wave wrote into
it.

A citation to something that does not exist does not rot into an obviously
dangling reference. **It rots into a PLAUSIBLE WRONG ANSWER**, which stops the
reader instead of sending them looking. A tool name that reads like the other
forty-five is believed. A blocker name in the right shape is believed. That is
why four separate waves hit this class on one day and not one of them was
looking for it.

This document is the guard, its assertion-versus-proposal rule, the evidence for
that rule, its precision and recall with denominators, the corpus count, and an
honest ledger of what it does not reach. **It fixes nothing.** Three sibling
waves hold the documents and census files involved, and the fixer should not be
the detector.

**Ships:**

| artifact | what it is |
|---|---|
| `scripts/check_asserted_names_resolve.py` | the guard. 0.5s over the whole corpus |
| `tests/test_an_asserted_name_resolves.py` | five controls and the pin, 7 tests |

**Headline:** **4 asserted-and-absent citations, all in one document.** And one
finding about the instrument itself that is worth more than the four: **the
guard disarmed itself by documenting itself, inside an hour, in the live tree.**
Section 7.

---

## 1. The design question, answered first

**What distinguishes "this document claims X exists" from "this document
discusses X"?**

I did not answer it from intuition. I extracted the complete candidate
population first and read it. The answer the corpus gave back is better than any
rule I would have invented:

> **THIS CORPUS ALREADY MARKS ITS PROPOSALS.** Every document that mints a name
> says so, in the author's own words. The defects are the documents that mark
> nothing.

The burden of marking is the author's, because the author is the only party who
knows. A name written in a referential position with **no mark** is an
assertion, because a reader has nothing else to go on. That is not a heuristic
about English; it is a measured property of how this corpus is written.

The marks, each quoted from the corpus, each now a suppressor in the guard:

| mark | corpus receipt |
|---|---|
| `MARKED-PROPOSAL` | `2026-09-05-decide-retire-rulings.md:478` -- *"**New blocker: `LINK-FOR-OFF-PLATFORM-USE` -- 2 rows, 2R, queue BUILD, cost 2**"* |
| `MARKED-PROPOSAL-TABLE` | `2026-09-20-the-decides.md:187` -- a column headed *"successor blocker (proposed)"*, whose own cells write *"`PICKER-SURFACES` (exists)"* for the two that do |
| `MARKED-PROPOSAL-DOC` | `2026-09-05-decide-retire-rulings.md:953` -- the same document's ruling table, re-citing a blocker **it opened 653 lines earlier** |
| `MARKED-HYPOTHETICAL` | `2026-09-03-linkedin-gap-blockers.md:791` -- *"A single `NO-ADDRESS` blocker **would** have..."* |
| `MARKED-ABSENT` | `2026-09-20-the-decides.md:95` -- *"`AI-INTERVIEW-RESULTS-NO-ADDRESS` **exists only in** `_audit/2026-09-05-decide-retire-rulings.md` lines 300-303"* |
| `MARKED-SPEC-DOC` | `2026-09-05-leave-group-writespec.md:7` -- *"**This is a SPECIFICATION, not a build.**"*, in the document whose field table reads `tool_name` = `linkedin_leave_group` |

Two of those are DOCUMENT-scoped and **name-specific**, which is load-bearing
in both directions. Name-specific, so a document that legitimately opens one
blocker is not thereby excused for citing a different unregistered one.
Document-scoped, because the damage model is *a reader is stopped*: a reader of
`2026-09-20-the-decides.md` meets its line 95 and is not stopped.

### 1.0 This document is bound by its own rule, and discharges it here

A report about absent names is a document full of absent names. The guard scans
`_audit/`, so it scans this file, and when it first did it convicted this
report eight times. **That is correct behaviour and it is not being special-cased
away.** A reader who meets a name in a table here is owed the same disclosure as
a reader who meets it anywhere else, and the only honest way to earn silence is
to say the true thing plainly:

* **`linkedin_applied_jobs` does not exist** anywhere in `linkedin_server/`.
  The write-off that names it is wrong; the real tools are
  `linkedin_my_applications` and `linkedin_draft_applications`.
* **`linkedin_leave_group` does not exist** as a built tool. It is the
  `tool_name` field of a WriteSpec that says of itself *"This is a
  SPECIFICATION, not a build."*
* **`linkedin_my` does not exist** and never did. It is the elided middle of a
  pytest diff, `{'linkedin_my...n_saved_jobs'}`, not a citation at all.
* **`linkedin_read_inbox` does not exist.** It is named twice in one document,
  once under a modal and once as work to be done.
* **`PROXIMITY-NOT-PARSED` and `ALERTS-PAGE-UNREAD` are not one of the 97**
  blockers the ledger published.
* **`linkedin_zzz_not_a_real_tool` does not exist**, deliberately. It is a
  fabricated control needle, named here only because section 7.1 is about the
  hour it stopped being one.
* `linkedin_zzz_planted_tool` does not exist. `linkedin_zzz_quoted_output`
  does not exist. `linkedin_zzz_indented_quote` does not exist. Every `ZZZ-`
  name in this document does not exist. All are needles planted to prove
  something could fail, and **a report that names its own needles owes the
  reader the disclosure it demands of everyone else.**

The guard is silent on this file now, and it is silent for the reason it is
silent on the other 162 clean documents: **the marks were discharged.** No
suppression was added, no path was excluded, and
`scripts/check_asserted_names_resolve.py` contains no mention of this
document's name. If a future edit removes those sentences, this file goes red
like any other.

### 1.1 The half that does more work than the rule: KIND

For blocker names the dominant error is not proposal-versus-assertion at all.
**The UPPER-KEBAB shape in this corpus is shared by at least seven closed
vocabularies**, and asking "does this token exist?" without first asking "which
registry is it drawn from?" is what builds the guard nobody reads.

Measured: **234 occurrences of a backticked UPPER-KEBAB token that is not one of
the ledger's 97**, 78 distinct. Sorted by what they actually are:

| vocabulary | occurrences | examples |
|---|---:|---|
| census state cells | 67 | `EXCLUDED-RULED` 24, `COVERED-CANNOT-DELIVER` 15, `COVERED-PROVEN` 7 |
| evidence classes | 48 | `LEDGER-EXPLICIT` 11, `RECON-DOC` 15, `MEASURED-ABSENT` 7 |
| refusal / probe returns | 25 | `REFUSED-BY-SUBSTRING` 7, `ALLOWLIST-SILENCE` 4, `AUTH-WALL` |
| `INSTRUMENTS.md` entry names | 17 | `A-SKIP-IS-NOT-A-RED`, `GUARDS-ITS-OWN-COPY` |
| section / block labels | 15 | `P-R` 12, `COMPANY-PAGE`, `PREMIUM-JOBS` |
| map and close classes | 9 | `EMPTY-CERTAIN` 5, `DOUBLE-ASSIGNED`, `NOT-GAP-AT-FREEZE` |
| build/verify states | 3 | `PROVEN-LIVE`, `TESTED-ONLY`, `KNOWN-BROKEN` |
| queue verdicts | 3 | `DECIDE-RETIRE` 2, `RULING-FORK` |
| **genuinely blocker-position** | **13** | the population this guard is about |

**A guard that fired on the shape would run at 13/234 = 5.6% precision.** It
would be suppressed inside a day, and a suppressed guard certifies nothing.

So a blocker candidate must sit in a **SLOT** -- a position this corpus's own
grammar reserves for a blocker reference.

---

## 2. The slot, measured phrase by phrase

Candidate slot phrases were **not guessed**. Each was run over the corpus and
scored by how many ledger blockers versus other-vocabulary tokens it selects.
Four were dropped on that evidence.

| phrase, immediately before the name | selected | named a ledger blocker | other vocabulary |
|---|---:|---:|---:|
| `` under `X` `` | 23 | 21 | 2 (both are findings, not noise) |
| `` blocker `X` `` | 9 | 4 | 5 (all 5 are findings) |
| `` filed under `X` `` | 4 | 4 | 0 |
| `` belongs to `X` `` | 3 | 3 | 0 |
| `` behind `X` `` | 1 | 1 | 0 |
| `` the blocker `X` `` | 1 | 1 | 0 |
| **DROPPED** -- `` filed as `X` `` | 2 | 0 | 2 -- an `INSTRUMENTS` entry name, a `RECON-DOC` |
| **DROPPED** -- `` stays `X` `` | 1 | 0 | 1 -- `RULING-FORK`, a queue verdict |
| **DROPPED** -- `` is now `X` `` | 1 | 0 | 1 -- `EMPTY-CERTAIN`, a close class |
| **DROPPED** -- `files this blocker as` | 1 | 0 | 1 -- `DECIDE-RETIRE`, a queue verdict |

Two further slot forms were added after measurement:

**A markdown table cell under a column whose header names blockers, where the
name IS the cell.** This is the strongest slot evidence in the corpus:
**360 cells selected, and the DISTINCT names it selects contain all 97 of the
ledger's blockers** plus the five unapplied mints of section 5.1. The slot
reproduces the registry by position alone.

The predicate is a SUBSTRING test on the header, and the distribution says why:
347 of the 360 selections sit under the bare word `blocker`, and 13 sit under
four other spellings -- `successor blocker (proposed)` 5, `the blocker` 4,
`new blocker` 2, `blocker name` 2. A fifth, `first blocker, corrected`, matches
the predicate and carries no names today. Those parts sum to the total, which
is not decoration: **the first version of this table did not sum.** It
attributed each selection to every blocker column in its table, so
two-blocker-column tables double-counted and the parts came to 20 against a
total of 13. A child reading the report caught the arithmetic and declined to
reconcile it silently, which is the only reason it was caught at all.

*"The name IS the cell" is load-bearing, not tidiness.* `_census/profile.md`
heads its fifth column `evidence / blocker` and fills it with prose, so a
contains-test convicted a `STILL-UNKNOWN` sitting inside a reason sentence.
Requiring the whole cell drops that one and keeps all 97.

**The word AFTER the name** -- *"A single `NO-ADDRESS` blocker"*. Two selections
corpus-wide, one a ledger blocker, one cleared by its own modal. Thin, and kept
anyway: leaving it out would have hidden `NO-ADDRESS` behind an **accident** of
the prefix rule rather than behind the marker that actually excuses it, and a
guard whose silences are accidents cannot be audited.

### 2.1 Quoted material is not the document speaking

The corpus quotes source two ways: ``` fences (2,127 lines) and **4-space
indented blocks (5,405 lines)** -- 7,532 lines, 9.5% of the corpus, and the
indented form is the larger half. The guard shipped handling only fences, and
`_audit/_slice-parity-census.md:475-490` reproduces
`tests/test_server_surface.py`'s `FORBIDDEN_TOOLS` set in an indented block --
twelve write-tool names the suite exists to keep OUT of the surface -- which the
guard convicted as invented. Eight false positives.

An indented run counts as a block only when a blank line precedes it, which is
what markdown itself requires; without that, every wrapped table cell and
continued list item is swallowed and the guard goes quiet in places nobody can
predict.

**AND THE HONEST PART: THIS MECHANISM IS LOAD-BEARING NOWHERE IN THE CORPUS
TODAY, MEASURED.** A red-proof deleted the indent handling outright and the
guard's corpus-wide candidate count did not move by one -- 38 before, 38 after,
the same 4 findings. The parity census is **doubly defended**: `CONTRACT_MODULES`
puts those sixteen names in the registry independently, by a path `fenced()`
never touches, so they resolve before block detection is ever consulted. The two
fixes were developed against the same eight false positives and are now
redundant for that document, and no OTHER indented block in 167 files carries a
candidate-shaped name.

That is exactly the state in which a component rots unnoticed, so it is written
down rather than quietly kept: the indented-block path is now exercised by a
synthetic block inside `test_a_marked_name_is_not_convicted`, which is the only
thing that will notice if it breaks. It was not deleted, because "nothing in
today's corpus needs it" is an argument about today and the next document to
quote an indented `FORBIDDEN_*` list is one commit away.

---

## 3. Precision and recall, with denominators

Both kinds are measured over a **complete census of their decision space**, not
a sample. A guard can only ever fire where a name fails to resolve and the line
is the document speaking, so that set is the denominator, and it is small enough
to label exhaustively by hand.

All numbers below are against the FROZEN `8b58dcb` corpus -- documents written
by other waves, before this report existed.

### 3.1 TOOL names -- complete population, n = 4 occurrences

72 distinct `linkedin_*` tokens appear in the corpus. 69 resolve against the
registry. The 3 that do not are the **entire** decision space, at 4 sites. Every
one is labelled:

| site | name | hand label | guard verdict | agree |
|---|---|---|---|:-:|
| `2026-09-20-the-contingent-writeoffs.md:265` | `linkedin_applied_jobs` | ASSERT | `ASSERTED-ABSENT` | yes |
| `2026-08-25-cannot-vs-will-not.md:234` | `linkedin_read_inbox` | discuss (modal) | `MARKED-HYPOTHETICAL` | yes |
| `2026-08-25-cannot-vs-will-not.md:421` | `linkedin_read_inbox` | discuss (build-it) | `MARKED-PROPOSAL` | yes |
| `2026-09-05-leave-group-writespec.md:31` | `linkedin_leave_group` | discuss (spec) | `MARKED-SPEC-DOC` | yes |

**precision 1/1 = 1.00. recall 1/1 = 1.00. false positives 0/3.**

A fourth token, `linkedin_my`, is NOT in the decision space and that is the
right answer. It is the **elided middle** of a pytest assertion diff,
`{'linkedin_my...n_saved_jobs'}`, inside a fenced block -- not a truncated
citation but a rendering artifact. Quoted tool output is not the document
speaking, and a guard that read it as a claim would convict the corpus for
pasting a traceback.

### 3.2 BLOCKER names -- complete population, n = 234 occurrences

Every one of the 234 was hand-labelled from a full-context worksheet. 221 are
some other vocabulary and are not in a blocker slot; 13 are blocker-position.
Those 13, in full:

| site | name | hand label | guard verdict | agree |
|---|---|---|---|:-:|
| `the-contingent-writeoffs.md:138` | `ALERTS-PAGE-UNREAD` | ASSERT | `ASSERTED-ABSENT` | yes |
| `the-contingent-writeoffs.md:232` | `PROXIMITY-NOT-PARSED` | ASSERT | `ASSERTED-ABSENT` | yes |
| `the-contingent-writeoffs.md:269` | `PROXIMITY-NOT-PARSED` | ASSERT | `ASSERTED-ABSENT` | yes |
| `decide-retire-rulings.md:300` | `AI-INTERVIEW-RESULTS-NO-ADDRESS` | mint | `MARKED-PROPOSAL` | yes |
| `decide-retire-rulings.md:953` | `AI-INTERVIEW-RESULTS-NO-ADDRESS` | mint, same doc | `MARKED-PROPOSAL-DOC` | yes |
| `decide-retire-rulings.md:478` | `LINK-FOR-OFF-PLATFORM-USE` | mint | `MARKED-PROPOSAL` | yes |
| `decide-retire-rulings.md:954` | `LINK-FOR-OFF-PLATFORM-USE` | mint, same doc | `MARKED-PROPOSAL-DOC` | yes |
| `the-decides.md:15` | `AI-INTERVIEW-RESULTS-NO-ADDRESS` | doc discloses absence | `MARKED-ABSENT` | yes |
| `the-decides.md:289` | `AI-INTERVIEW-RESULTS-NO-ADDRESS` | doc discloses absence | `MARKED-ABSENT` | yes |
| `the-decides.md:189` | `UPLOAD-WIRING-UNBUILT` | proposal column | `MARKED-PROPOSAL-TABLE` | yes |
| `the-decides.md:190` | `COMPOSER-PRESS-REFUSED` | proposal column | `MARKED-PROPOSAL-TABLE` | yes |
| `the-decides.md:193` | `RESUME-MANAGER-ADDRESS` | proposal column | `MARKED-PROPOSAL-TABLE` | yes |
| `gap-blockers.md:791` | `NO-ADDRESS` | modal | `MARKED-HYPOTHETICAL` | yes |

**precision 3/3 = 1.00. recall 3/3 = 1.00. false positives 0/231.**

The 221 non-slot occurrences are silent because of the SLOT, and the 10 slotted
ones are silent because of a MARK -- two independent mechanisms, and the second
is only reachable because the first did its job.

**RECALL AT THE OCCURRENCE LEVEL IS NOT 1.00 AND THE TABLE ABOVE WOULD HIDE
THAT.** `PROXIMITY-NOT-PARSED` occurs four times in its document; the guard
sees two. The other two, at lines 329-330, sit in a `| row | verdict | what
replaces it |` table -- a proposal column by meaning, but not one the header
regex matches, so they are not suppressed, they are simply **out of slot**.
Occurrence recall on that name is 2/4 = 0.50; **document recall is 1/1**, and
document recall is the number that matters, because the unit a reader is
stopped in is a document. Stated rather than buried:

> **The guard finds every affected DOCUMENT. It does not claim to find every
> affected LINE.** Its output is a starting point for a fixer, not a worklist.

---

## 4. The calibration positives, shown firing

```
$ ./venv/Scripts/python.exe scripts/check_asserted_names_resolve.py
candidate sites considered : 38
cleared by an author mark  : 34
ASSERTED and ABSENT        : 4
NOT checked: unbackticked UPPER-KEBAB outside a slot, prose names of no fixed
vocabulary, whether a RESOLVING citation points at the right thing, and locator
line numbers.

_audit/2026-09-20-the-contingent-writeoffs.md:138  BLOCKER ALERTS-PAGE-UNREAD  [ASSERTED-ABSENT]
    * `J 37a` LIST the alert set -- **GAP**, blocker `ALERTS-PAGE-UNREAD`.
_audit/2026-09-20-the-contingent-writeoffs.md:232  BLOCKER PROXIMITY-NOT-PARSED  [ASSERTED-ABSENT]
    **REPLACEMENT.** `J 40` -- **GAP**, blocker `PROXIMITY-NOT-PARSED`, queue
_audit/2026-09-20-the-contingent-writeoffs.md:265  TOOL linkedin_applied_jobs  [ASSERTED-ABSENT]
    `linkedin_applied_jobs`, `linkedin_draft_applications` -- and the proximity
_audit/2026-09-20-the-contingent-writeoffs.md:269  BLOCKER PROXIMITY-NOT-PARSED  [ASSERTED-ABSENT]
    **REPLACEMENT.** `J 57` -- **GAP**, blocker `PROXIMITY-NOT-PARSED` (BLOCKED
```

Calibration positives 1 and 2 fire. So does a **third the brief did not name**:
`ALERTS-PAGE-UNREAD`, in the same document, by the same mechanism.

### 4.1 The negatives, shown NOT firing

The `--all` listing is the receipt: 34 of 38 candidate sites are cleared, and
every one of the six marker classes is earned by a real corpus line. Section 3's
two tables label all 17 sites in the frozen corpus.
`test_every_marker_class_fires_on_the_real_corpus` asserts that none of the six
is dead code, because a suppressor with no example is untested width that can
only ever excuse something in future.

### 4.2 Positives 3 and 4 are NOT of this class, and the brief is corrected

Two of the four calibration positives I was handed do not belong to the
asserted-but-absent class. Both were re-measured rather than assumed.

**`inmail_ledger.json` -- the document is RIGHT, and a guard firing here would
be the defect.** It has exactly ONE occurrence in the tracked tree:

```
$ git grep -n "inmail_ledger" -- .
_audit/2026-09-20-the-contingent-writeoffs.md:315:`mcp-servers/_audit/inmail_ledger.json`. **That file does not exist.** The
```

The sentence naming it is the sentence reporting its absence. The census cell it
is said to bear on does not cite it at all -- `_census/jobs.md:362` for `J 131`
names `referral_join.py` and `inmail-targeting.md`, and no ledger. Under the
rule in section 1 this is `MARKED-ABSENT`. It is also **out of tree**:
`mcp-servers/_audit/` is a sibling directory of this repository, unresolvable
from any clone, and a guard that convicted it would convict every CI run.
**Firing here would mean convicting a document for correctly reporting a
defect** -- which is precisely how a guard earns the suppression that makes it
worthless.

**`L296,L537,L647` -- a real defect, a different class, and the brief's own
correction is itself wrong.** Verified by reading all six lines at `8b58dcb`:

| line | what is actually there | relevant to `N 149/150/151/160`? |
|---|---|:-:|
| L296 | *"(five places searched, reported UNFOUND rather than guessed)."* | no |
| L537 | *"18 my blocker is a surface name and nothing more."* | no |
| L647 | *"390   at 23f04f1"* | no |
| L325 | the `OWNED-BY-A-SIBLING-SLICE` cost row, naming the four ids | **yes** |
| L558-559 | *"is a measured double-count"* / the four ids | **yes** |
| L669 | *"**-4, DOUBLE-COUNTED** -- `N 149 150 151 160`"* | **yes** |

All three cited locators are wrong -- that much the brief had right. But the
brief says *"the real occurrences are `L325` and `L558`, and there is no
third."* **There is a third, at L669.** A correction that is itself off by one
occurrence is the same failure one turn later, and it is the reason this wave
re-measured every number it was handed rather than carrying it.

This defect lives in the `locator` column of `_audit/_census/blocker-map.tsv`
and `blocker-assignments.tsv`, which sibling waves own and which this wave is
forbidden to edit. It is **measured and handed over** in section 6, not gated.

---

## 5. The corpus count

**4 asserted-and-absent citations, in 1 document, across 2 kinds.**

| document | kind | name | occurrences |
|---|---|---|---:|
| `_audit/2026-09-20-the-contingent-writeoffs.md` | BLOCKER | `PROXIMITY-NOT-PARSED` | 2 |
| `_audit/2026-09-20-the-contingent-writeoffs.md` | BLOCKER | `ALERTS-PAGE-UNREAD` | 1 |
| `_audit/2026-09-20-the-contingent-writeoffs.md` | TOOL | `linkedin_applied_jobs` | 1 |

By kind: **BLOCKER 3, TOOL 1.** By document: **one document, 165 clean.**

That a single document carries all four is a finding in itself, and it is not
luck. The other 165 documents were written by waves that marked their proposals.

### 5.1 A second class this wave found and is NOT gating: unapplied mints

Two blockers were **opened by a committed ruling** and never entered the ledger:

| blocker name | minted at | rows it claims | in the ledger's 97? |
|---|---|---:|:-:|
| `AI-INTERVIEW-RESULTS-NO-ADDRESS` | `2026-09-05-decide-retire-rulings.md:300` | 3 | no |
| `LINK-FOR-OFF-PLATFORM-USE` | `2026-09-05-decide-retire-rulings.md:478` | 2 | no |

Three more sit in `2026-09-20-the-decides.md`'s *"successor blocker (proposed)"*
column: `UPLOAD-WIRING-UNBUILT` (3 rows), `COMPOSER-PRESS-REFUSED` (5),
`RESUME-MANAGER-ADDRESS` (1).

**These are correctly marked and the guard is correctly silent on them.** They
are not citation defects; they are **rulings nobody applied**, which is a
different problem with a different owner. `2026-09-20-the-decides.md:95` already
says so about the first one in its own words. Reported here so the count is not
mistaken for zero.

---

## 6. Ledger: what this guard does not reach, and why

**What is GATED:** TOOL names and BLOCKER names. Both at measured precision 1.00
over a complete census of their decision space.

**What is MEASURED AND HANDED OVER, not gated.** Each is here because narrowing
honestly beats shipping a check that gets suppressed -- the brief's own
instruction, and this repository's most expensive recurring failure.

### 6.1 FILE PATHS -- measured, narrowed, and NOT gated

**7,956 path-shaped citations** in the corpus. Buckets: RESOLVES_TRACKED 5,595,
UNRESOLVED 2,318, OUT_OF_TREE 43, AMBIGUOUS_BASENAME 0.

**The 2,318 is a precision artifact and I will not report it as a defect
count.** A fixed-seed hand-read of 60 of them (`random.Random(20260920)`, method
stated so it is reproducible) classified every row:

| what it actually was | of 60 |
|---|---:|
| not a path at all -- ratios, glob and regex fragments, route segments | 24 (40.0%) |
| read/write-capability shorthand -- `R/W`, `1R/4W`, `12R/20W`, the census tables' own notation | 16 (26.7%) |
| gitignored runtime path -- `_state/*`, `venv/Scripts/python.exe`, capture html | 7 (11.7%) |
| a bare directory, not a file | 6 (10.0%) |
| resolvable, blocked only by a pytest `::testname` suffix | 5 (8.3%) |
| out of tree -- the cross-repo `SKILL.md` | 2 (3.3%) |
| **a real defect** | **0 (0.0%)** |

Two near-misses were deliberately kept OUT of the shorthand class despite
matching its shape: `CR/LF` and `read/unread`. A class that absorbs everything
resembling it stops being a measurement.

So the broad bucket is shorthand containing a slash, not dead references. **A
guard that cried 2,318 would be suppressed within a day.** It is not gated.

**The narrow subset IS clean enough to read by hand.** `STRICT` = backticked,
directory-bearing, first segment a real top-level entry, known extension:
**1,988 rows, 1,854 resolving, 134 unresolved.** All 134 were read:

* **121** cite `_audit/_scratch/*`, `_audit/_probe-*` or other gitignored
  working artifacts -- most say "gitignored" or "untracked" in their own line.
* **12** cite `tests/test_*.py` from `2026-08-31-jobcore-paths.md`, which is
  explicitly comparing against a SIBLING project's suite. Real files, wrong
  repo, and no prefix rule can reach them because they carry no marker.
* **1 is a genuine defect**, verified independently at `8b58dcb`:

> `_audit/INSTRUMENTS.md:1180` reads *"...over
> `tests/fixtures/search_appearances_synthetic.html`"*, present tense. That path
> does not exist. The fixture lives at
> `tests/fixtures/synthetic/search_appearances_synthetic.html` -- it was moved
> into a `synthetic/` subdirectory and the citing line never followed. Both
> commits that touched it (`4958fe3`, `2d13a41`) predate `8b58dcb`.

**1 defect in 194 hand-read citations.** The corpus's path citations are
overwhelmingly sound.

### 6.2 LOCATORS -- a resolving path is not a working citation

A `path:line` whose FILE exists says nothing about the LINE. **851 citations
carry a locator into a resolved file.** Two buckets, both computed against
`8b58dcb` blobs:

| bucket | n | meaning |
|---|---:|---|
| `LOCATOR_OUT_OF_RANGE` | **2** | the target has FEWER lines than the locator names. Outright wrong. |
| `LOCATOR_SUSPECT` | 529 | the target has commits after the last commit touching the CITING document. Unverifiable by the reader, not necessarily wrong. |
| OK | 320 | the target has not moved since the citation was written |

Both out-of-range hits verified independently:

| citation | target | target length at `8b58dcb` |
|---|---|---:|
| `_audit/2026-09-19-the-remaining-partials.md:166` | `2026-09-19-the-three-ruling-requests-ruled.md:400` | **263 lines** |
| `_audit/_census/mcp-inventory.md:206` | `_audit/2026-08-31-linkedin-lift.md:1456` | **1,299 lines** |

Plus the brief's own `L296,L537,L647` case in section 4.2, which is IN range and
therefore invisible to this check -- which is exactly why 529 SUSPECT is
reported rather than swept up. **A line number is not an anchor in a live tree**
(`INSTRUMENTS` 3.5), and none of this is gated: the second bucket is a
"nobody can verify this" signal, not a defect count, and the census files
involved belong to sibling waves.

**A third locator convention exists and is NOT handled:** pytest node ids,
`path/test_x.py::test_name`, 93 lines. Named rather than guessed at.

### 6.3 CENSUS ROW IDS -- an honest zero, backed by a live control

**12,134 row-id citations.** RESOLVES 9,779, UNRESOLVED 232, AMBIGUOUS 2,123.
By citation form: canonical 7,357, range 3,690, bare-number 759, run 328.

The gateable subset is `STRICT` -- backticked, canonical form, explicit prefix:
**2,814 occurrences, 2,399 resolving, 408 ambiguous, and 7 unresolved.** All
seven were hand-read and **not one is a hallucinated row citation**:

| site | id | what it actually is |
|---|---|---|
| `2026-09-05-blocker-map.md:672,677` | `P 0`, `N 05`, `N 09`, `N 2026` | a PRIOR wave's audit of bad-id extraction, quoting its own junk examples -- *"fragments of a date in a source comment, wearing the exact shape of a network row id"* |
| `2026-09-19-four-defects-fixed.md:221` | `L 63` | a line locator: *"the line at `L63` must..."* |
| `2026-09-19-messaging-menu-enumeration.md:122` | `A 0`, `B 0` | DOM set counts: *"It returns `A 0, B 0, shared 0`"* |

All three verified independently at `8b58dcb`. **Zero asserted-absent row ids.**

A zero is only worth reporting when the detector can speak, so it was asserted
rather than printed: synthetic `` `J 9999` `` and `` `M C9999` `` come back
UNRESOLVED, synthetic `` `J 40` `` comes back RESOLVES.

Two things that make this kind hard, named rather than smoothed over:

* **The prefix alphabet must be DERIVED from the census, never listed.** An
  early pass accepted a bare `L` prefix -- which this census does not have,
  though `P L` does -- and range-expanded 16,000 line locators into phantom row
  ids. Deriving the alphabet from the built universe collapsed UNRESOLVED from
  16,083 to 232.
* **2,123 AMBIGUOUS is not a defect count either.** The largest cluster,
  `A13`/`A1`/`A9` (224), is the ledger's **Amendment rounds**, which share the
  row-id surface grammar exactly. The `M` and `C` entries are likelier real
  slice collisions. This wave did not adjudicate them; the number is handed
  over as the size of what is uncovered.

### 6.4 COMMIT SHAS -- 325 that no clone can resolve, and one that matters

**791 distinct hex tokens** in the corpus. Resolved against this repository:

| bucket | distinct | occurrences |
|---|---:|---:|
| resolves, ancestor of master | 309 | 945 |
| resolves, NOT an ancestor (the superseded pre-purge line) | 99 | 295 |
| `DANGLING_COMMITISH` -- 7-8 chars, resolves nowhere | **325** | 772 |
| mid-length 9-15, unclassified | 13 | 40 |
| `NOT_A_COMMITISH` -- 16+ even, content digests and urns | 36 | 99 |
| `LONG_ODD_UNRESOLVED` -- `worktree-agent-<hex>` fragments | 5 | 10 |

**The split is the whole point.** A raw "383 unresolved SHAs" merges commit
citations with content digests, LinkedIn urns, and branch-name fragments, and
means nothing. Four more were removed from the dangling count after being
identified as single hyphen-segments of LinkedIn opaque UUIDs -- 8 characters
long, passing a length gate, never a sha at all.

**The one that matters, verified here rather than relayed:**

```
$ git cat-file -e a8684146^{commit}
fatal: Not a valid object name a8684146^{commit}
$ git grep -c "a8684146" -- _audit
_audit/2026-09-20-the-contingent-writeoffs.md:1
_audit/_census/jobs.md:10
```

`a8684146` is cited **11 times**, ten of them in the EVIDENCE column of
`_census/jobs.md` rows 49-57 and 68-69 -- *"| 49 | Read the In Progress / Draft
list | a8684146 | CP | ..."*. **Nine census rows rest their evidence on a
commit no clone can resolve.** This is the asserted-but-absent class exactly,
in the corpus's most load-bearing file, and a sibling wave owns the repair.

### 6.5 CI RUN-ID CITATIONS -- the class is real here but small, and the trap is a trap

This corpus proves greenness by citing GitHub Actions run ids. That is a name
asserted to exist with a property attached, and it fails two ways a reader
cannot see: the id resolves but nobody read its conclusion, or it is green on a
commit that is not the branch HEAD, certifying a prefix rather than what
shipped.

**113 run-id-shaped occurrences, 37 distinct.** Buckets: 94 carry no verdict
word nearby, 10 carry a verdict AND a sha, 9 carry a verdict and no sha.

**The trap, and it is specific to this repository: LinkedIn job ids are also
bare 10-digit integers.** The most-cited "run ids" are job postings --
`4456021840` (31 citations), `4423880462` (17), `4448301715` (11). Genuine CI
run ids here are consistently **11 digits in the 32-35 billion range**, and
there are only a handful (`32661307599`, `32688677004`), both of which do carry
a sha. One 10-digit job id landed in the verdict-bearing bucket purely through
line proximity -- `linkedin_job_detail("4423880462")` on one row and an
unrelated failure sentence on the next.

**No GitHub API call was made.** A rate-limited 403 is indistinguishable from a
real answer, and this wave hit exactly that while reading its own CI run
(section 8). A text census is what is defensible without the API, and it is
reported as a text census.

### 6.9 Things I could not separate, stated plainly

1. **Occurrence-level recall on blockers is 0.50 on the one name where it can be
   measured** (`PROXIMITY-NOT-PARSED`, 2 of 4 sites). The two missed sites sit
   in a `what replaces it` column. I did **not** add `replaces` to the
   proposal-header regex, and the reason is a rule rather than a preference:
   widening a suppressor to match one document's phrasing is how a guard gets
   tuned toward green. Adding it would have suppressed nothing that is not
   already caught elsewhere in the same document, and would have bought a
   silence I could not later audit.

2. **An unbackticked blocker name in prose is invisible to the guard.** The
   corpus writes blocker names in backticks with high consistency, but "high"
   is not "always" and I did not measure the exception rate, because doing so
   requires deciding which bare UPPER-KEBAB tokens are blocker references --
   the 5.6%-precision problem the slot exists to avoid. This is an honest hole,
   not a covered case.

3. **A test fixture and a shipped contract are not mechanically separable, and
   the guard does not pretend otherwise.** `tests/test_server_surface.py`'s
   `FORBIDDEN_TOOLS` and this wave's own `PINNED` tuple are both module-level
   constants holding whole-string tool names in a test file. Nothing in their
   structure tells them apart. The guard resolves this by ADMITTING ONE MODULE
   BY NAME, in a one-line list with the reason written beside it, rather than by
   inventing a rule that would be wrong the first time somebody tested it.

4. **The guard cannot tell a RESOLVING citation that points at the wrong thing.**
   `linkedin_saved_jobs` serves `J 45`, not `J 47`; `J 47`/`J 48` are both
   `linkedin_my_applications`. Every one of those names resolves, so every one
   passes. Row-to-artifact correctness is a different instrument and this guard
   does not pretend to it.

5. **A name absent from the tree but present in an UNTRACKED file reads as
   absent.** Correct for CI, which sees only the tracked tree, and worth saying
   because a reader in the main checkout may find the file sitting on disk.

6. **The disclosure window is 120 characters and nothing makes that the right
   number.** It was line-bounded at first, which measured the author's text
   WRAPPING rather than what they wrote -- a disclosure split across a line
   break did not register, and the guard convicted a sentence for being
   reflowed. It now spans whitespace, which is how markdown renders a
   paragraph. The 120 itself is still a threshold nobody derived: a disclosure
   further than that from its name is invisible, and a disclosure closer than
   that but about a DIFFERENT name will excuse the wrong one. Neither failure
   was observed in this corpus; both are reachable.

---

## 7. The instrument, shown failing -- starting with the time it failed for real

**An instrument enters `INSTRUMENTS.md` only if it has been SHOWN FAILING.**
This one was shown failing in the live tree within an hour of landing, with
nothing planted, and the failure is the same defect class the guard exists to
catch -- one level up.

### 7.1 The guard disarmed itself by documenting itself

`tool_registry()` shipped scanning raw text of `linkedin_server/`, `scripts/`
and `tests/` for anything matching `linkedin_[a-z0-9_]+`. Measured correct:
4 findings, matching a hand census of all 72 tokens.

Then the guard was **committed**. Its own module docstring names
`linkedin_applied_jobs` as the worked example and `linkedin_leave_group` as the
spec-document example. Its test module plants `linkedin_zzz_not_a_real_tool` as
a control needle and writes `linkedin_applied_jobs` into the pin. Every one of
those strings landed in `scripts/` and `tests/`. On the next run:

| what should have happened | what happened |
|---|---|
| 4 findings | **0 findings** |
| the control needle convicted | absorbed -- the planted name registered itself as real before the classifier saw it |
| `MARKED-SPEC-DOC` earns its keep | dead -- **the guard's prose ABOUT a case made the case stop occurring** |
| the pin holds | red in the "these defects were REPAIRED" direction |

**Nothing was repaired.** `linkedin_applied_jobs` is a live defect and the
instrument built to catch invented names was manufacturing the appearance of
their repair, by quoting them.

This is the corpus's defect exactly: **writing ABOUT a name is not the name
existing.** A test's string literal and an `_audit/` sentence are the same kind
of thing, and a registry that reads one but not the other draws the line in the
wrong place.

**The smallest fix was measured and rejected.** Scoping the registry to
`linkedin_server/` alone convicts `_slice-parity-census.md` for quoting
`FORBIDDEN_TOOLS` -- names that are real because they are a shipped contract.
Restricting to AST identifiers was measured too: 26 of 72 corpus tokens would
have gone absent, because real tool names live in string literals here
(`shape.py` maps "LinkedIn Apply to this job" -> `linkedin_apply`). **The defect
was never the extraction technique. It was the scope.**

What shipped: the registry is `linkedin_server/`, plus **one** module admitted
by name because its subject matter IS a name enumeration, whole-string constants
only. This guard's own test module is not on that list and must never be.
`test_the_registry_cannot_absorb_a_name_from_its_own_instruments` names the four
exact strings that did it, so it is a regression test for a real event rather
than a hypothetical.

The fix was NOT to rename the fixtures. That would have tuned the test to dodge
the bug and left production blind -- the `linkedin_leave_group` suppressor would
have stayed dead, and the next real invented name that anyone documented would
have disappeared the same way.

### 7.2 The planted battery -- nine mutations, and the two that did NOT go red

Run under this repository's standing protocol: never in the live tree; copy
`linkedin_server`, `tests`, `scripts`, `_audit` and `pytest.ini` to scratch;
ASSERT (not confirm) that the module resolves under the copy AND that the repo
path is absent from it; one mutation at a time; only the selector that should
die; restore by re-copying that one file, `diff`-verified empty; finish on a
clean control run.

| # | mutation | expected | result |
|---|---|---|---|
| R1 | append an unmarked `blocker \`ZZZ-PLANTED-BLOCKER\`` line to a corpus doc | pin RED | **RED**, naming document and blocker |
| R2 | append an unmarked `\`linkedin_zzz_planted_tool\`` line | pin RED | **RED**, naming the TOOL |
| R3 | rewrite the two pinned `PROXIMITY-NOT-PARSED` sites to a REAL blocker | pin RED in the `repaired` branch | **RED**, in the right branch |
| R4 | `classify()` returns `[]` | detector control RED | **RED** |
| R5 | add `"MARKED-NOTHING-EVER"` to `MARKERS` | dead-suppressor test RED | **RED**, naming it |
| R6 | narrow the header predicate to an exact match | slot control RED | **GREEN. See 7.3.** |
| R7 | restore the old `CODE_DIRS` (put the self-disarm bug back) | registry control RED | **RED**, and it reproduced the original event one for one |
| R8 | delete `fenced()`'s indented-block handling | pin RED on the parity census | **GREEN. See 7.4.** |
| R9 | `classify()` returns `[]`, run BOTH controls | positive RED, negative GREEN | **exactly that** |

**R9 is the pairing proof and its finding is a sentence worth keeping:** under a
dead `classify()`, `test_the_detector_finds_a_planted_assertion` goes RED while
`test_a_marked_name_is_not_convicted` stays GREEN. **Neither is valid alone.**
The negative control is satisfied both by working suppressors and by a detector
that does no work; the positive control is satisfied both by working suppressors
and by a detector that convicts everything. Each rules out exactly the failure
the other cannot see.

### 7.3 R6: the slot control was a union claim, and could not fail

Narrowing the header predicate from a substring test to an exact match removes
twelve genuinely blocker-labelled columns from the corpus -- and
`test_the_table_slot_still_reproduces_the_registry` **passed cleanly**. Its
docstring called itself "the whole precision argument for the slot, asserted
rather than believed". It was not.

The reason is the corpus, not the code: the test asks whether all 97 ledger
blockers appear SOMEWHERE in the slot's output, and this corpus is redundant
enough that every one of them is also cited under a bare `blocker` header or in
a backtick phrase slot elsewhere. **A union claim over a redundant corpus cannot
see a narrowing.** Confirmed twice, on two independent clean baselines, and
diagnosed read-only with the mutation still live rather than by tuning it.

Repaired by exercising the predicate DIRECTLY -- a synthetic one-row table per
header spelling, through the real code path. Re-run against the repair
(**R6-PRIME**): the new test goes RED naming all five non-bare spellings; the
union test stays green, now for a reason its own docstring states. Both are
kept: **collapse and narrowing are different failures.**

**R6-PRIME-B, and it is a lesson about red-proofs rather than about this
guard.** The same mutation was predicted to kill one marker class. It killed
**two**: `MARKED-PROPOSAL-TABLE` as expected, and `MARKED-PROPOSAL-DOC`
unpredicted -- because that suppressor's only three corpus examples sit under
the headers `new blocker` and `blocker name`, two of the same five spellings.
One column-exclusion, two independently-named downstream consumers. **A
single-selector red-proof under-reports the blast radius of its own mutation**,
and a reviewer who ran only the named selector would have shipped believing one
gap was closed.

### 7.4 R8: a mechanism that is correct and load-bearing nowhere

Deleting the indented-block handling changed nothing: 38 candidate sites before,
38 after, the same 4 findings, across 167 files. The document that motivated it
is **doubly defended** -- `CONTRACT_MODULES` puts those sixteen names in the
registry by a path `fenced()` never touches -- and no other indented block in
the corpus carries a candidate-shaped name.

Not deleted. "Nothing in today's corpus needs it" is an argument about today,
and the next document to quote an indented `FORBIDDEN_*` list is one commit
away. Instead the synthetic document in `test_a_marked_name_is_not_convicted`
now carries an indented block of its own, so the path is exercised by the only
thing that will notice if it breaks.

### 7.5 What the battery cost, and what it bought

Nine mutations. **Seven behaved. Two did not, and the two that did not are the
whole value of running it.** One exposed a control that could not fail, in the
module whose own docstring explains why that is the expensive kind; the other
exposed a mechanism nothing exercises. Neither was reachable by reading the
code, and neither would have been found by a battery that tuned its mutations
until they went red.
