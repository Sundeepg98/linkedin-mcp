# The audit index: 195 documents, 5.4 MB, and no way in but grep

**A NOTE ON HOW THIS DOCUMENT NAMES OTHER DOCUMENTS.** It never puts a
document name in backticks. That is not a style choice -- see section 6. The
correction guard raises a candidate pair whenever its correction vocabulary
sits within two lines of a backticked path that resolves, and this document is
about corrections, so backticked names would make it raise pairs it means
nothing by. Names below are written plain, exactly as the generated index
writes them.

## 1. The gap, and why it is not housekeeping

Measured at the start of this wave:

| what | reading |
| --- | --- |
| tracked markdown documents under `_audit` | 195 |
| total bytes | 5,420,832 |
| documents written on 2026-09-19 | 59 |
| documents written on 2026-09-20 | 32 |
| index of any kind | none |
| anything in `scripts/` that generates one | nothing |

The 190 in the wave brief and the 195 here are both correct readings: the
corpus grew by five while five waves merged, one deliverable each. A count is a
reading with a timestamp, which is the whole subject of this document.

**A corpus nobody can navigate is a corpus nobody re-reads**, and the same day
this was measured produced four count-drifts between a machine-checked constant
and the prose beside it, a section asserting a 22-pattern read allowlist that
had held 42 for a fortnight, a correction marker that was itself stale, and 22
commit ids cited across 19 documents that no clone can resolve. What failed was
never *finding a file*. It was **knowing a document had been overtaken**.

## 2. The answer to the question that was asked

**How many documents are superseded or corrected by something later, and how
many say so themselves?**

| | count |
| --- | --- |
| documents a later document declares a correction of | **39** |
| of those, that say so themselves | **39** |
| documents that declare a correction of another | 51 |
| documents at either end of a cross-document edge | 74 |
| documents that correct themselves later on | 2 |
| documents no correction marker touches at all | 121 |

**The corpus is in better shape than the brief feared, and the reason is
structural rather than lucky.** Every one of the 39 says so itself because the
correction guard makes it impossible not to: a `CORRECTS:` marker with no
matching back-pointer fails, and a back-pointer no document declares fails too.
Both directions are asserted, so a half-finished edit cannot read as a joined
pair. That guard is why the answer to "how many say so themselves" is not a
number to be alarmed by.

**What the 121 means, stated precisely.** It is a fact about markers, not a
verdict on those documents. It says nobody has declared a correction of them.
It does not say nobody has overtaken them -- and the stale 22-pattern section
that opened this wave was in a document with no marker on it at all. The index
prints that distinction in its own preamble rather than letting a blank cell
read as a clean bill of health.

## 3. What the index surfaces, and why each earns its place

_audit/INDEX.md, 1269 lines, six sections, every cell derived.

**Section 1, the counts.** Twenty-one derived numbers, including every number
quoted in this document. Nothing in the index restates a number it did not
compute.

**Section 2, what a later document corrected.** Organised by the CORRECTED
document, because that is where a reader arrives with a stale claim in hand.
Each entry gives the correctors and the reason the corrected document itself
gives, quoted rather than summarised. This is the section the wave exists for.

**Section 3, what a document corrected in itself.** A different relation, kept
separate -- see section 5 below.

**Section 4, what each document corrects.** The same edges from the other end,
so a corrector's reach is visible.

**Section 5, every document by date.** One row per document: date, link, title,
and a marker column reading CORRECTED, corrects, self-corrected, or blank.

**Section 6, what the scan rejected, could not join, or had to repair.**
Printed only when non-empty, because an empty section is a claim. It currently
carries 15 reasons that run past their own line, the tightest admission
margin, 2 lopsided edges, 5 non-ASCII titles and 6 defused citations, each
named with the document and line.

### What could not be derived, and was left out rather than guessed

**A date for the 33 undated documents** (of the 196 in the corpus at freeze).** `git log --diff-filter=A` would supply
one. It is rejected on a receipt: this repository lost 14 days to red CI caused
by `actions/checkout` at `fetch-depth: 1`. `git ls-files` works in a shallow
clone; history does not. An index whose guard cannot run on CI is an index
whose guard gets disabled.

**A last-touched date.** Same reason, plus a worse one: it would make the
committed index a function of history, so every commit touching any audit
document turns the guard red until somebody regenerates. A guard that is red
for reasons nobody can act on is the one people learn to bypass.

**Whether a document is still true.** Only a marker somebody wrote can say
that. Inferring it from prose was measured not to work before this wave: the
correction guard's own lexical scan produced 24 candidate pairs over an earlier
corpus and exactly 1 was a genuine correction. No threshold separates them.

**Any excerpt beyond titles and marker reasons.** Both are quoted from tracked,
swept lines. An excerpt chosen by a script is a place an identifier could reach
a file that did not have one before.

## 4. Five defects the index found on its first run

None of these were looked for. Each fell out of deriving something.

**4.1 -- 65 of 136 correction reasons were truncated where a reader saw them.**
(Closed upstream the same day -- see the addendum in section 7b, which is
where the sequel lives; this section stays as the reading that caused it.)
The shipped `_reason_on` returns everything after the LAST backtick on a marker
line. Its own docstring says *whatever a marker line says after the document it
names*. Those are the same thing only when no backtick follows the cited path,
and marker reasons here quote commit ids, symbols and branch names constantly.
Every one of the 65 is a strict suffix -- text is lost, never invented -- and
13 are cut below 60 characters. The worst returns 29 characters of a
767-character reason. One reads, in full: *". The dated note sits at that
block."* Its real reason is a four-clause re-measurement against a freshly
fetched remote.

**The guard is GREEN on all 65**, because its only check is that the fragment
is 20 characters long, and a fragment can be. The index takes its text from the
end of the citation match instead -- the stated intent implemented -- while
still using the shipped function to decide what is ADMITTED, so the edge set it
advertises is provably the edge set the guard enforces. No test file was
edited.

**4.2 -- three correction pairs are declared twice, and three reasons are
unreadable.** 68 `CORRECTS:` lines and 68 back-pointer lines resolve to 65
distinct pairs. A dictionary keyed by the pair cannot hold two declarations of
it; the second overwrites the first with no error. The guard has that shape
correctly, because it only ever asks whether the pair exists. Anything reading
it for the reason gets the last one written. The index keeps every declaration.

**4.3 -- two edges are lopsided, and that guard cannot see it.** A pair
declared twice in one direction and once in the other. Its both-directions test
is over distinct pairs, so two corrected claims under one back-pointer read to
it as one clean pair. Reported, not ruled on.

**4.4 -- five committed titles carry an em dash in a strict-ASCII repository.**
Found by a test, not by reading: this wave had grepped one date's files by hand,
found ONE, and written a one-entry allowlist. The test convicted it immediately
and named five. A hand count of a corpus, committed inside the fix for hand
counts of corpora.

**4.5 -- the index indexed itself.** Once _audit/INDEX.md is tracked it is
part of its own corpus, and its section 3 quotes four marker-shaped lines
verbatim. The intra-document marker count went 4, then 8, then 12 on successive
regenerations. No fixpoint exists, so `--check` could never pass after
`--write`. Nothing about reading the code suggested this; the red-proof harness
found it on its first run, by failing its opening control.

## 5. The relation the corpus has and the guard has no model for

Four tracked markers sit BEHIND A BLOCKQUOTE. The shipped anchor is
`^\s*(?:\*\*)?(CORRECTS|CORRECTED BY):` and its `^\s*` never consumes `> `, so
it cannot see them. Verified directly rather than reasoned about:
`> **CORRECTED BY:** x` does not match, while `**CORRECTED BY:** x` and
`   CORRECTS: y` both do.

They are in 2026-09-05-cheap-reads.md (three) and
2026-09-05-cheap-reads-build.md (one), and **every one names "this section" or
"this document"**. They are a LATER SECTION CORRECTING AN EARLIER ONE IN THE
SAME FILE -- a relation nobody formalised.

**So widening the anchor would have made things worse.** The guard requires a
marker to name exactly one resolving document; "this section" resolves to none,
so all four would have become malformed and turned a test red on four
well-intentioned annotations.

The measurement that settles it, and which the relayed finding did not include:
**zero blockquoted markers in this corpus name another document.** Widening the
anchor would gain no cross-document edge at all. So nothing in `tests/` was
edited, and the index records the four as what they are, in their own section,
with the line quoted verbatim.

Two guards hold the preconditions that make leaving it alone safe:

* `test_no_blockquoted_marker_names_another_document` -- the day one does, it
  IS an edge the shipped guard cannot see, and somebody adjudicates widening
  the anchor rather than a correction existing that no reader can reach.
* `test_no_marker_hides_inside_a_fenced_code_block` -- the anchor is also
  fence-blind, so an EXAMPLE marker in a code block would read as a
  declaration. Zero today, over 136 declarations and 99,511 lines, measured
  independently by a census slice as well as by the generator.

## 6. Why this index says nothing to the correction guard

_audit/INDEX.md is tracked, so that guard scans it like any other document,
and it raises a CANDIDATE PAIR whenever its correction vocabulary sits within
two lines of a backticked path that resolves. This file is nothing but document
names beside the words CORRECTED and corrects.

Measured with the link text backticked, which is the obvious way to write it:
**490 resolvable citations and 153 candidate pairs.** Every one would have
needed a declaration or a hand-written triage entry, in a guard three other
waves edited the same day, to excuse pairs raised by a file that makes no
claims at all. **An index of a corpus is not a claim about it.**

The remedy was entirely local, and the measurement is what made it possible:
all 490 came from link text, and ZERO came from the reasons quoted verbatim.
So link text is not backticked, and the one quoted title that carried a
resolving spelling is defused -- its backticks removed and not one character of
its text changed, reported by name in the index's section 6. The correction
guard was then run with the index staged and tracked: green.

**AND THIS DOCUMENT TRIPPED THE SAME MECHANISM TWICE, AFTER EXPLAINING IT.**
The paragraphs above were written first, then this file named the generated
index in backticks four times while describing why that must not happen -- one
of them two lines from the word "correction" -- and turned the guard red. It
was fixed, and then the register entry for this wave did it again, in the
paragraph recording the first instance. Three instances in one wave, the last
two inside the prose explaining the defect. **A mechanism you can state exactly
is not a mechanism you have stopped running**, which is the argument for the
guard rather than for the write-up, and the reason this document opens with a
note about how it spells document names.

## 7. Files, and how to run them

| file | what it is |
| --- | --- |
| `scripts/build_audit_index.py` | the generator: `--write`, `--check`, or counts to stdout |
| _audit/INDEX.md | the generated index, 1269 lines |
| `tests/test_the_audit_index_is_derived.py` | 33 tests: the drift check, the preconditions, and the planted controls |
| `scripts/_check_audit_index_guard_can_fail.py` | the red proof: 7 mutations against the real selector |

    python scripts/build_audit_index.py --write
    python scripts/build_audit_index.py --check
    python scripts/_check_audit_index_guard_can_fail.py

### Shown failing

`scripts/_check_audit_index_guard_can_fail.py` copies `_audit` from
`git ls-files` (never a disk walk, or an ignored `_scratch/` note would enter
the corpus under proof), asserts the scratch interpreter loaded the COPY and
not the live tree, then plants seven defects and runs the real pytest selector
against each:

    a line appended to the committed index       RED
    a line deleted from the committed index      RED
    one count flipped by one                     RED
    a document added and not re-indexed          RED
    a title edited and not re-indexed            RED
    a correction declared and not re-indexed     RED
    the corpus gutted to ten documents           RED  (the vacuity floor)

bracketed by a green control run before the first mutation and after the last
restore. A proof that ends on a red says nothing about whether the tree was
restored. Every planted run also asserts the failure is the RIGHT one: an
import error or a collection error would fail the run too and would prove only
that the harness is broken.

The planted controls in the test file run over a SYNTHETIC corpus in
`tmp_path`, never the live tree, because `_audit/` is written continuously by
concurrent waves and this register's own preamble records a wave that proved
three gates by mutating a file another agent was holding uncommitted work in.
`render()` is pure over an explicit document list precisely so the proof needs
no live mutation.

## 7a. The law this wave actually established, and what it cost

**A DERIVED VIEW OF A CORPUS MUST NOT BE AN INPUT TO INSTRUMENTS THAT MEASURE
THAT CORPUS.** The generated index is tracked, so every instrument sweeping
tracked markdown under `_audit` picks it up. It carries every document's title
and 65 correction reasons quoted verbatim. The full suite found two casualties,
neither expected, and they break for DIFFERENT reasons -- which is the general
form rather than one bug twice.

**A ranker gets diluted.** The blocker-reason locator ranks documents by how
well they ARGUE a blocker. An index mentions every blocker-shaped word in the
repository while arguing nothing. GROUPS-SURFACE's real argument fell from rank
1 to rank **17** and that tool's recall floor went red.

**A quote does not carry the quoted document's marks.** One reason quoted here
says a cell names a server tool "and no such tool exists anywhere". The
document that wrote that clears the name with a doc-scoped mark; a quote leaves
the mark behind, so the asserted-name checker read the index as ASSERTING a
tool the corpus was explicitly DENYING. **The index makes no claims; it reports
that others did.**

Both are fixed at each instrument's single corpus entry point -- two additive
edits, each with the reason written beside it -- and one test asserts both
exclusions rather than trusting those comments, because a filter with a long
comment beside it is exactly what a later cleanup deletes. Three instruments
now exclude the index: the correction guard (by the index raising no citation
it can resolve), the locator, and the name checker. A fourth that sweeps this
corpus will pick it up silently, which is why the law is in the register and
not only here.

## 7b. Addendum, same day: 4.1 was closed upstream, and closing it exposed a third class

**SECTION 4.1 ABOVE STAYS AS WRITTEN.** Its "65 of 136" was true when written
and is the evidence for why the fix happened. A number in a record is evidence
of what was known when; correcting it in place destroys that.

The shipped extractor was fixed to read after the first backticked span, with a
test stating the property that no reason may be a strict suffix of the text
after its citation. Reconciling this wave to it found two things that refused
the obvious cleanup.

**The two extractors are not the same rule.** The shipped one anchors on the
first backticked span of ANY kind; this index's anchors on the first span that
resolves AS A CITATION. A marker written with a backticked row id before its
target parts them, and the shipped result then carries the citation inside the
reason. They agree on all 136 markers today -- which is exactly the condition
under which somebody deletes one as redundant. Both are kept, one control
plants the divergence and one watches the live half.

**A third truncation class survived, and the new property test cannot see it.**
The shipped extractor reads ONE PHYSICAL LINE and this corpus hard-wraps at
about 78 columns. 15 of 138 reasons continue onto a following line, hiding
**5,832 characters**; the worst shows a reader 20 characters of a 723-character
reason. The new suffix property convicts **0** of the 15, by construction: it
compares one line against the same line, so a missing continuation satisfies it
exactly. A suffix test cannot detect a tail that was never on the line. The
23-character fragment quoted in the upstream fix is one of these -- read as the
floor admitting a short reason, it is a 465-character reason showing 35.

The index now reads the marker's whole paragraph, and the join is asserted
whitespace-only so nothing can silently reflow quoted prose.

**And the floor is applied to that line-scoped read.** Admission is 20
characters of the marker's OWN line, so a wrapped marker is judged on its first
line alone. One marker clears it by **exactly zero** -- 20 characters admitting
a 723-character reason -- and all five of the tightest five wrap. Nothing is
rejected today; reflow any of those paragraphs by one word and a guard rejects a
long reason saying it carries none. Found by a test fixture tripping it, not by
looking. The index prints the tightest margin every regeneration rather than a
rejection count, because a count of rejections reads zero until the day it does
not: **when a hazard is a distance, publish the distance, not the crossing.**

Teaching the shipped extractor to read a paragraph, and applying the floor to
what it returns, would close both. That is a change to a guard other waves are
editing, so it is reported with the measurement attached rather than done
quietly.

## 8. The exact counts, all derived

**EVERY FIGURE BELOW IS A READING AT FREEZE, 2026-09-20**, and the corpus moved
twice while this wave ran: 190 in the brief, 195 when the generator was first
run, 196 once this document was itself tracked, and 197 after a sibling
wave's deliverable merged under it -- which brought a new correction edge
with it, moving the headline from 38 to 39. Section 1 of the generated
index recomputes all of them on every regeneration, and a guard fails if the
committed index disagrees with the corpus. This table does not; it is a dated
record of what the wave found, which is exactly the thing the index exists to
make checkable.

| reading | value |
| --- | --- |
| tracked audit documents (excluding the generated index) | 197 |
| carrying a `YYYY-MM-DD-` filename date | 164 |
| distinct dates | 13 |
| documents with no level-1 heading | 1 |
| `CORRECTS:` marker lines | 69 |
| back-pointer marker lines | 69 |
| distinct declared correction edges | 66 |
| documents a later document corrects | 39 |
| documents that correct something | 51 |
| documents at either end of a cross-document edge | 74 |
| intra-document correction markers | 4 |
| documents that correct themselves later on | 2 |
| documents no correction marker touches at all | 120 |
| blockquoted markers naming another document | 0 |
| edges missing one of their two markers | 0 |
| edges declared a different number of times in each direction | 2 |
| marker lines rejected as malformed | 0 |
| marker-shaped lines inside a fenced code block | 0 |
| reasons the shipped extractor cuts short | 65 |
| marker lines with exactly one resolving citation | 138 |
| titles carrying a non-ASCII character | 5 |
| quoted strings whose backticked citation had to be defused | 6 |
| generated index, lines | 1269 |

Two independent census slices were run against the generator rather than taken
on trust, and both reproduced it: one counted 136 declarations over 99,511
lines with 0 inside a fence and 0 indented as code, and found 35 lines that
MENTION a marker without being one -- the control set an unanchored pattern
would have eaten. The other counted 162 dated documents, 1 with no heading, 0
titles containing a pipe, 0 containing a backslash, and 5 non-ASCII. Every
figure matched.
