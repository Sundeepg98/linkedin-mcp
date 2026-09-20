# Names that do not exist

**Wave:** names-that-do-not-exist. **Date:** 2026-09-20. **Tree:** `8b58dcb`.
**Corpus measured:** the 166 tracked files under `_audit/`, 78,656 lines, 5.1 MB.

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
| `scripts/check_asserted_names_resolve.py` | the guard. 2.1s over the whole corpus |
| `tests/test_an_asserted_name_resolves.py` | four controls and the pin, 6 tests |

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
| `MARKED-PROPOSAL-DOC` | `2026-09-05-decide-retire-rulings.md:953` -- the same document's ruling table, re-citing the blocker **it opened 653 lines earlier** |
| `MARKED-HYPOTHETICAL` | `2026-09-03-linkedin-gap-blockers.md:791` -- *"A single `NO-ADDRESS` blocker **would** have..."* |
| `MARKED-ABSENT` | `2026-09-20-the-decides.md:95` -- *"`AI-INTERVIEW-RESULTS-NO-ADDRESS` **exists only in** `_audit/2026-09-05-decide-retire-rulings.md` lines 300-303"* |
| `MARKED-SPEC-DOC` | `2026-09-05-leave-group-writespec.md:7` -- *"**This is a SPECIFICATION, not a build.**"*, in the document whose field table reads `| \`tool_name\` | \`linkedin_leave_group\` |` |

Two of those are DOCUMENT-scoped and **name-specific**, which is load-bearing
in both directions. Name-specific, so a document that legitimately opens one
blocker is not thereby excused for citing a different unregistered one.
Document-scoped, because the damage model is *a reader is stopped*: a reader of
`2026-09-20-the-decides.md` meets its line 95 and is not stopped.

### 1.0 This document is bound by its own rule, and discharges it here

A report about absent names is a document full of absent names. The guard scans
`_audit/`, so it scans this file, and when it first did it convicted this
report eight times. **That is correct behaviour and it is not being special-cased
away.** A reader who meets `linkedin_applied_jobs` in a table here is owed the
same disclosure as a reader who meets it anywhere else, and the only honest way
to earn silence is to say the true thing plainly:

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

The guard is silent on this file now, and it is silent for the reason it is
silent on the other 160 clean documents: **the marks were discharged.** No
suppression was added, no path was excluded, and
`scripts/check_asserted_names_resolve.py` contains no mention of this
document's name. If a future edit removes those sentences, this file goes red
like any other.

### 1.1 The half that does more work than the rule: KIND

For blocker names the dominant error is not proposal-versus-assertion at all.
**The UPPER-KEBAB shape in this corpus is shared by at least seven closed
vocabularies**, and asking "does this token exist?" without first asking "which
registry is it drawn from?" is what builds the guard nobody reads.

Measured: **235 occurrences of a backticked UPPER-KEBAB token that is not one of
the ledger's 97.** Sorted by what they actually are:

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

**A guard that fired on the shape would run at 13/235 = 5.5% precision.** It
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
**358 cells selected, 353 naming a ledger blocker, and the DISTINCT names it
selects are exactly the ledger's 97.** The slot reproduces the registry by
position alone. That property is asserted in
`test_the_table_slot_still_reproduces_the_registry`, not merely recorded here.

*"The name IS the cell" is load-bearing, not tidiness.* `_census/profile.md`
heads its fifth column `evidence / blocker` and fills it with prose, so a
contains-test convicted a `STILL-UNKNOWN` sitting inside a reason sentence.
Requiring the whole cell drops that one and keeps all 97.

**The word AFTER the name** -- *"A single `NO-ADDRESS` blocker"*. Two selections
corpus-wide, one a ledger blocker, one cleared by its own modal. Thin, and kept
anyway: leaving it out would have hidden `NO-ADDRESS` behind an **accident** of
the prefix rule rather than behind the marker that actually excuses it, and a
guard whose silences are accidents cannot be audited.

---

## 3. Precision and recall, with denominators

Both kinds are measured over a **complete census of their decision space**, not
a sample. A guard can only ever fire where a name fails to resolve, so that set
is the denominator, and it is small enough to label exhaustively by hand.

### 3.1 TOOL names -- complete population, n = 5 occurrences

72 distinct `linkedin_*` tokens appear in the corpus. 68 resolve against the
tree. The 4 that do not are the **entire** decision space, at 5 sites. Every one
is labelled:

| site | name | hand label | guard verdict | agree |
|---|---|---|---|:-:|
| `2026-09-20-the-contingent-writeoffs.md:265` | `linkedin_applied_jobs` | ASSERT | `ASSERTED-ABSENT` | yes |
| `2026-08-25-cannot-vs-will-not.md:234` | `linkedin_read_inbox` | discuss (modal) | `MARKED-HYPOTHETICAL` | yes |
| `2026-08-25-cannot-vs-will-not.md:421` | `linkedin_read_inbox` | discuss (build-it) | `MARKED-PROPOSAL` | yes |
| `2026-09-05-leave-group-writespec.md:31` | `linkedin_leave_group` | discuss (spec) | `MARKED-SPEC-DOC` | yes |
| `_slice-activity-items.md:537` | `linkedin_my` | not a name at all | never reaches the classifier (fenced) | yes |

**precision 1/1 = 1.00 (n=1 fired). recall 1/1 = 1.00 (n=1 should fire).
false positives 0/4 (n=4 should not fire).**

`linkedin_my` deserves its own line. It is not a truncated citation; it is the
**elided middle** of a pytest assertion diff, `{'linkedin_my...n_saved_jobs'}`,
inside a fenced block. Quoted tool output is not the document speaking, and a
guard that reads it as a claim would convict the corpus for pasting a traceback.

### 3.2 BLOCKER names -- complete population, n = 235 occurrences

Every one of the 235 was hand-labelled from the full-context worksheet. 222 are
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

**precision 3/3 = 1.00 (n=3 fired). recall 3/3 = 1.00 (n=3 should fire).
false positives 0/232 (n=232 should not fire).**

The 222 non-slot occurrences are silent because of the SLOT, and the 10 slotted
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
candidate sites considered : 17
cleared by an author mark  : 13
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

Positives 1 and 2 -- `linkedin_applied_jobs` and `PROXIMITY-NOT-PARSED` -- fire.
So does a **third the brief did not name**: `ALERTS-PAGE-UNREAD`, in the same
document, by the same mechanism.

### 4.1 The negatives, shown NOT firing

The `--all` listing is the receipt: 13 of 17 candidate sites are cleared, and
every one of the six marker classes is earned by a real corpus line. Section 3's
two tables label all of them. `test_every_marker_class_fires_on_the_real_corpus`
asserts that none of the six is dead code, because a suppressor with no example
is untested width that can only ever excuse something in future.

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
from any clone, and a guard that convicts it would convict every CI run.
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

| blocker | minted at | rows it claims | in the ledger's 97? |
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

_(sections 6.1-6.4 below carry the path, row-id, SHA and locator censuses.)_

### 6.5 Things I could not separate, stated plainly

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
   the 5.5%-precision problem the slot exists to avoid. This is an honest hole,
   not a covered case.

3. **The guard cannot tell a RESOLVING citation that points at the wrong thing.**
   `linkedin_saved_jobs` serves `J 45`, not `J 47`; `J 47`/`J 48` are both
   `linkedin_my_applications`. Every one of those names resolves, so every one
   passes. Row-to-artifact correctness is a different instrument and this guard
   does not pretend to it.

4. **A name absent from the tree but present in an UNTRACKED file reads as
   absent.** Correct for CI, which sees only the tracked tree, and worth saying
   because a reader in the main checkout may find the file sitting on disk.

---

## 7. The instrument, shown failing

_(section 7 carries the red-proof battery: six mutations, six reds.)_
