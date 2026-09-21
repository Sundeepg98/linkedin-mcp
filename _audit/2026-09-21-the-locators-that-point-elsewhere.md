# The locators that point elsewhere

`scripts/check_asserted_names_resolve.py` ends every run by printing what it did
not check. Two clauses of that line were:

> `whether a RESOLVING citation points at the right thing, and locator line numbers.`

All the damage was inside those two clauses. This wave went and looked, repaired
what it found, and made the looking automatic.

**The guard was not broken.** It said where it does not look. That sentence is
the most valuable thing it has, and this document exists because it was true.

---

## 1. THE MEASUREMENT -- MY OWN POPULATION, MY OWN INSTRUMENT

A prior measurement of this defect exists in another wave's gitignored scratch.
It was read AS EVIDENCE and re-derived from zero; nothing below is inherited.
Where the two agree that is stated, because two independent instruments agreeing
is worth more than either.

### 1.1 The population, stated so it can be argued with

`_audit/_census/blocker-assignments.tsv` holds **390 data rows** (lines opening
`>` are commentary, and the `blocker<TAB>row_id<TAB>...` header is not data).
Of those, **94 name one of the four census slices in their `source` column** --
`_audit/_census/{jobs,profile,messaging-and-content,network}.md`. Those 94 are
the only rows where "does this locator resolve to the census row it claims" is
even a meaningful question, and they are this wave's subject.

| source slice | assignment rows |
|---|---:|
| `_audit/_census/messaging-and-content.md` | 35 |
| `_audit/_census/jobs.md` | 25 |
| `_audit/_census/network.md` | 18 |
| `_audit/_census/profile.md` | 16 |
| **total in subject** | **94** |

The other 296 rows cite a ledger, a probe script or a server module. They are
out of subject and are named as such in section 6.

Those 94 rows carried three locator dialects:

| dialect | rows | example |
|---|---:|---|
| bare line number, `L<number>` | 35 | `L200` |
| compound, carrying at least one line number | 41 | `L269-L278 (section G), L389 (section 2 grouping)` |
| row label only | 18 | `C36`, `N25`, `M6-M9 rows` |

Between them the 76 line-number-bearing rows hold **137 `L<number>` tokens**.

### 1.2 The verdicts, counted separately, INCLUDING what did match

Resolution reads the designated line of the source slice and asks which census
row is there. The row index is built with the shipped parser -- `cells()`,
`classify()`, `ROW` and `HEADERS` from `scripts/count_census_states.py` -- rather
than a second copy of it, so this measurement and the census's own 704 cannot
drift apart. Measured at the tree as this wave found it:

**The 35 bare `L<number>` locators:**

| outcome | count |
|---|---:|
| RESOLVES -- lands on the row it is evidence for | **0** |
| WRONG-ROW -- lands on a REAL but DIFFERENT census row | 25 |
| NOT-A-ROW -- lands on prose, a heading or a non-row table line | 6 |
| BLANK -- lands on an empty line | 4 |
| OUT-OF-RANGE / MISSING-FILE | 0 |

**All 137 `L<number>` tokens, including those inside compound locators:**

| outcome | count |
|---|---:|
| RESOLVES | **0** |
| WRONG-ROW | 80 |
| NOT-A-ROW | 43 |
| BLANK | 14 |

**And what DID match, which is the half a refusal usually omits.** The 18
row-label locators were resolved by the same instrument in the same pass:
**14 of 18 resolved as written**. The four that did not are all the same token,
`M6-M9 rows`, which names a RANGE -- rows M6, M7, M8 and M9 each exist, the
compound spelling is not itself a row label. Once ranges are expanded the
row-label dialect resolves at **18 of 18**.

So the file already carried a dialect that works. One dialect resolves at 18 of
18 and the other at 0 of 137, in the same file, written by the same hands.

**And the row-label dialect has never drifted, which is the other half of the
same measurement.** Each of those 18 was blamed to the commit that wrote it and
re-resolved against the slice AS IT STOOD THEN: **18 resolved identically then
and now; 0 differed.** So the contrast is not "one dialect was written more
carefully". It is that over the life of this file, a position-based citation
broke 137 times out of 137 and a key-based citation broke 0 times out of 18 --
which is a fact about what a line number IS, not about who typed it.

### 1.3 WHY THEY ALL FAIL, and it is not carelessness

The obvious reading -- somebody wrote these badly -- is wrong, and git says so.
Each of the 35 TSV lines was blamed to the commit that wrote it, and the source
slice was read AS OF THAT COMMIT:

| at its own birth commit | count |
|---|---:|
| **WAS-CORRECT** -- landed exactly on its own row | **32** |
| WAS-NOT-A-ROW | 2 (`J 18`, `J 19`) |
| WAS-WRONG-ROW | 1 (`M C49`) |

Thirty-two of thirty-five were RIGHT on the day. What moved was the file above
them. The drift is a near-constant per-slice offset, which is exactly what the
sum of every insertion higher up looks like:

| slice | bare-`L` locators | drift measured at HEAD |
|---|---:|---|
| `messaging-and-content.md` | 13 | +63 on twelve; `M C49` reads +62 |
| `network.md` | 11 | +114 on all eleven |
| `jobs.md` | 7 | +79 on five, +84 on the lowest; `J 18` / `J 19` are apart |
| `profile.md` | 4 | +56 on all four |

Two entries in that table are not drift and are called out rather than averaged
in. `M C49`'s +62 is the birth defect showing through: its line number was one
HIGH when written (it named C50, which sits one line below C49), so the same
+63 of file growth measures one short. And `J 18` / `J 19` cite a line in a
DIFFERENT table -- section 2's cost row `18-19` -- so the arithmetic that
applies to a capability row does not apply to them at all. The drift itself is
uniform within each slice; both anomalies are in the citations.

**This is the whole argument for the repair.** A line number is not a citation
that can be written carefully enough. It is a POSITION, and every edit above it
invalidates it without touching it -- silently, into a real but different row.
The two `J 18` / `J 19` exceptions are not counter-examples: their `L428` landed
on a cost-table row, which is a different kind of target, not a mistake.

---

## 2. THE POSITIVE CONTROL

An all-negative result from an uncontrolled instrument is indistinguishable from
an instrument that cannot say RESOLVES at all. The prior measurement returned
zero-resolving across its whole population and had no control; this one does.

The fixture is **manufactured, not found**. It is thirteen hand-written lines
living in `tests/test_a_census_locator_names_its_row.py` as the constant
`FIXTURE`, with its true row locations written beside it in `TRUE_LINES` and
confirmed by counting. A control that finds its fixture in ambient repo state
passes on the box it was written on and fails in every clone.

It deliberately carries every shape the real slices carry: bare numeric labels,
an `L`-prefixed label (because `profile.md` really does number its section L
rows `L1`..`L8`), a bold grouping row, and a compound cost row whose own first
cell reads `2-3`.

```
MANUFACTURED census indexed: 6 row labels, 4 of them stated
   label '1'                    at line(s) [5]   (hand-confirmed: 5)
   label '2'                    at line(s) [6]   (hand-confirmed: 6)
   label '2-3'                  at line(s) [12]   (hand-confirmed: 12)
   label '3'                    at line(s) [7]   (hand-confirmed: 7)
   label 'Grouped roll-up'      at line(s) [13]   (hand-confirmed: 13)
   label 'L1'                   at line(s) [8]   (hand-confirmed: 8)

X 1    cited '1'                                          -> RESOLVES           names=['1']
X 2    cited '2-3'                                        -> RESOLVES           names=['2-3', '2', '3']
X 3    cited '1-3'                                        -> RESOLVES           names=['1', '2', '3']
X L1   cited 'L1'                                         -> RESOLVES           names=['L1']
X 1    cited '1, Grouped roll-up'                         -> RESOLVES           names=['1', 'Grouped roll-up']
X 2    cited '2 (with an annotation the resolver ignores)' -> RESOLVES           names=['2']
X 1    cited '2'                                          -> NAMES-ANOTHER-ROW  names=['2']  -- resolves to 2, none of which is 1
X 1    cited '77'                                         -> NO-SUCH-ROW        names=[]  -- names '77', which is no row in this slice
X 1    cited 'L5'                                         -> LINE-NUMBER        names=[]  -- carries L5, a line number into this slice.
X 1    cited '1, L5'                                      -> LINE-NUMBER        names=['1']  -- carries L5, a line number into this slice.
```

The resolver can say RESOLVES, on six citation shapes, and can reach every
failing verdict it defines. The zero in section 1.2 is therefore a fact about
the file and not about the instrument.

**One thing the control caught that inspection had not.** The first resolver
decided "is this a line number" from the SPELLING `L<digits>`. `profile.md`
numbers eight of its rows `L1`..`L8`, and four locators in this file cite those
rows by label -- `P L1`, `P L6`, `P L7`, `P L8`. That resolver would have
refused all four CORRECT citations and reported them as rot -- the
false-positive failure that gets a guard suppressed. Kind is now decided from
the DATA: a token is
looked up in the slice's own label index first, and only a token that names
nothing there is judged by shape. `L6` resolves in `profile.md` and is refused
in `jobs.md`, which has no L-prefixed rows.

---

## 3. THE REPAIR

**76 locators converted from line numbers to row-label citations.** The repair
is committed as a script, `scripts/_repair_census_locators.py`, carrying all 76
conversions written out with the old value each one asserts it will find. It
refuses rather than guesses if the file has moved, and re-running it is a no-op.
A migration nobody can audit is how the lost 2026-09-03 classifier became
unauditable in the first place.

**Not one new line number was computed.** A freshly-computed line number is a
defect with a later expiry date, not a fix.

| how the new value was derived | rows |
|---|---:|
| `SELF` -- git-derived label IS the row's own id, so it confirms itself | 39 |
| `RANGE` -- a label span, read against the slice to confirm the family | 21 |
| `ANNOT` -- the locator's own words beat the derived label | 9 |
| `GROUP` -- a roll-up row cited by its bold name | 6 |
| `BIRTH` -- the line number was already wrong on the day it was written | 1 |

`SELF` needs no judgment: blame the TSV line, read the slice at that commit,
take the label of the row at the cited line. `J 57`'s `L200` was row 57 at
`eb11edd`, and becomes `57`.

**The four distinct locators where the derivation had to be overruled -- ten
rows in all**, each checked by hand and independently re-checked by a second
reader before it was applied:

- `L269-L278 (section G), L389 (section 2 grouping)`, carried by **seven rows**
  (`J 106`, `J 108`-`J 111`, `J 113`, `J 114`). `L389` derives to row `78-83`,
  "Premium apply extras", which has nothing to do with company Pages. The
  words say "section 2 grouping", and section 2's grouping row for these rows
  is `106-114`, three lines further down. Confirmed by reading both rows: it
  was already stale at `bc721dc`, the commit blame attributes the line to.
  Written as `106-115 (section G), 106-114 (section 2 grouping)`.
- `J 28`, `L207, L435 rows 24-30`. `L435` derives to row `68`; the locator's own
  words say `rows 24-30`, and `24-30` is a real cost-table row six lines above
  the cited one. Written as `28, 24-30`.
- `J 85`, `L286, L437 rows 85-86`. `L437` derives to `78-83`; the words say
  `rows 85-86`, which is the very next line. Written as `85, 85-86`. Its sibling
  `J 86` cites `L438` for the same grouping row and got there correctly, which
  is the cleanest possible demonstration that `L437` is one line short.
- `M C49`, `L439`. Derives to row `C50` -- an off-by-one on the day, not drift.
  Its note reads "as M C46", and `M C46`'s own locator resolved correctly to
  C46. Written as `C49`.

**The principle applied there, stated so it can be disagreed with:** where a
locator's prose annotation contradicts its line number, THE ANNOTATION WINS.
Not because prose is better evidence, but because the two halves of the citation
were written by the same author in the same cell at the same moment, and only
one of them can rot. Preferring the half that cannot rot is not a guess.

**The one line number in the file that never rotted** was `M M5`'s
`L336@1c08e5f` -- COMMIT-ANCHORED, and therefore still resolvable today. The
corpus had already invented the only line-number form that works. It is now
written in words rather than in the `L<n>` shape, so the guard needs no
exception to its own rule.

### 3.1 What could NOT be converted

Within the subject, nothing. All 94 census-sourced locators now name the row
they are evidence for, and the guard says so. What was deliberately NOT
converted:

- **The 296 out-of-subject assignment rows.** Their sources are ledgers, probe
  scripts and server modules. Those files have no row-label vocabulary to cite
  instead, so there is no non-rotting form to convert them TO. Inventing one
  would be worse than leaving them, and the guard names them in its own output
  rather than passing over them.
- **`M M5`'s `(ledger L326)` annotation.** That is a line number into
  `_audit/2026-09-03-linkedin-gap-blockers.md`, not into a census slice, so it
  is out of this guard's subject. It is preserved, now carrying the commit it
  was measured at.
- **No census row STATE was touched.** Four other waves are moving rows. If a
  row's state needs changing, this wave does not name one -- nothing it found
  bears on a state.

---

## 4. EXTEND THE GUARD, OR NOT -- THE VERDICT AND THE ARGUMENT

**Verdict: the repository's subject IS extended, and
`check_asserted_names_resolve.py` is NOT the file that should absorb it. The
coverage ships as a sibling guard, and that guard's honesty line shrinks to
match.**

The argument for bolting it in is real: one guard, one place to read, and the
`NOT checked:` line shrinks without anyone having to notice a second file. The
argument against won:

1. **The subject is a different kind of thing.** That guard's subject is NAMES
   in tracked markdown, resolved against two registries (tools, blockers), with
   a whole apparatus for telling an ASSERTION from a PROPOSAL. A locator is a
   field of a six-column TSV, resolved against a row-label index, and the
   assertion/proposal distinction does not apply to it at all -- there is no
   such thing as a proposed citation.
2. **A red that means two unrelated things gets read as noise.** That guard's
   own docstring says its most expensive recurring failure is a check that
   fires for reasons its readers cannot classify, "gets suppressed, and
   certifies nothing". Its test module's controls are all about names -- marker
   classes, the table slot, the registry. A locator assertion in there would
   make a red ambiguous at exactly the moment somebody is deciding whether to
   care.
3. **Its registry law forbids the coupling.** `CODE_DIRS` is a one-element
   tuple because the guard absorbed names out of its own docstring within an
   hour of shipping. The census index obeys the same law for the same reason,
   and the two registries have nothing in common; merging them would put two
   different "what counts as the subject" rules in one file.

**What extending the SUBJECT without extending the FILE requires, and it is the
part that is easy to skip:** the honesty line must still shrink, because a line
claiming a blind spot the repository no longer has teaches readers to distrust
it. So the line was rewritten to scope what remains and to NAME the instrument
that now covers the rest. A reader who wanted the locator check is sent
somewhere instead of being stopped, which is the principle in that guard's own
docstring applied to itself.

### 4.1 The `NOT checked:` line, before and after

**BEFORE:**

```
NOT checked: unbackticked UPPER-KEBAB outside a slot, prose names of no fixed
vocabulary, whether a RESOLVING citation points at the right thing, and locator
line numbers.
```

**AFTER:**

```
NOT checked: unbackticked UPPER-KEBAB outside a slot, prose names of no fixed
vocabulary, and whether a resolving TOOL or BLOCKER name is the right one for
the sentence it sits in.
NO LONGER on that list, 2026-09-21: locators into a census slice.
`scripts/check_census_locators_resolve.py` resolves every locator in
`_audit/_census/blocker-assignments.tsv` whose source is one of the four
slices, and fails on one that names the wrong row. Line numbers in PROSE
citations (`file.md:123`) are still unchecked by anything.
```

Three changes, each deliberate. The blanket clause "whether a RESOLVING citation
points at the right thing" is narrowed to NAMES, because for locators it is now
checked. "and locator line numbers" is gone. And the last sentence ADDS a blind
spot that the old line hid inside a vaguer one -- prose citations are still
unchecked, and section 6 says how many there are.

The new guard prints its own exclusions on every run, including the count of
rows it holds no index for, so a change in its scope shows up as a number.

---

## 5. THE GUARD, SHOWN FAILING

A check that cannot fail certifies nothing, and this repository has had to remove
several such checks. The pin in `tests/test_a_census_locator_names_its_row.py`
is EMPTY -- the wave repaired what it detected -- which makes showing the red
more important, not less: nobody had ever seen this guard convict.

`scripts/_check_census_locators_can_fail.py` stages a COPY of the four slices
and the assignment file, plants a locator in the COPY, and runs the REAL
command-line entry point. Nothing in the tree is mutated, which is why it is
safe while other waves are writing `_audit/_census/`.

```
==========================================================================
CONTROL -- nothing planted
==========================================================================
assignment rows in the file : 390
in subject (census source)  : 94
locator NAMES its own row   : 94
does not                    : 0
every census locator names the row it is evidence for.
exit 0

==========================================================================
PLANTED -- J 57's locator rewritten to '112', expecting NAMES-ANOTHER-ROW
==========================================================================
assignment rows in the file : 390
in subject (census source)  : 94
locator NAMES its own row   : 93
does not                    : 1

J 57      SERVED-BY-GMAIL-SKILL        112                     [NAMES-ANOTHER-ROW]
        resolves to 112, none of which is 57
exit 1

==========================================================================
PLANTED -- J 57's locator rewritten to 'L200', expecting LINE-NUMBER
==========================================================================
J 57      SERVED-BY-GMAIL-SKILL        L200                    [LINE-NUMBER]
        carries L200, a line number into this slice. A line number is a
        POSITION: every edit above it moves the row without moving the
        number, and it rots into a REAL BUT DIFFERENT row rather than into
        an error. Cite the row label instead -- `57`.
exit 1

==========================================================================
PLANTED -- J 57's locator rewritten to '9999', expecting NO-SUCH-ROW
==========================================================================
J 57      SERVED-BY-GMAIL-SKILL        9999                    [NO-SUCH-ROW]
        names '9999', which is no row in this slice
exit 1

all three plants were convicted, and the control was green.
```

The first plant is the exact shape of the 80 wrong-row citations in section 1.2:
a REAL row, in the right file, of the right shape, that is not the right one.
The second plant is a restoration of `J 57`'s own locator as it stood before
this wave -- so the red proof doubles as a regression test against the repair
being reverted.

`L200` is refused rather than resolved, deliberately. The guard COULD read line
200 and report which row is there; the first draft did. It was removed, because
a guard that resolves line numbers makes writing new ones feel safe -- green
today, rotted on the next edit made above them, with no event to notice. The
job is to make the rotting construct unwritable, not to chase it.

### 5.1 The pin

`PINNED` is an empty frozenset, and the test module says why in its own
docstring: this wave repaired in the same commit that added the guard, so the
expected set of failures is genuinely zero. It fails in both directions like its
sibling -- a new failure is RED, and an entry that disappears is RED asking for
the pin to be narrowed.

An empty pin is the most dangerous kind of green, so it does not rest on itself.
Four controls stand between "no findings" and "a detector that cannot find
anything": the manufactured positive control (section 2), a reachability
assertion for every failing verdict, the planted wrong-row conviction run
through the real `run()` on a copy of the real file, and a measurement that a
row label really is a unique key. Adding an entry to `PINNED` requires naming
the row and saying why it cannot be converted.

---

## 6. RESIDUAL

Named rather than hidden, each with its size measured.

1. **93 PROSE citations of the same shape, corpus-wide, unchecked by anything.**
   `<slice>.md:<number>` appears 93 times across tracked `_audit/` documents.
   Resolved against today's tree: **37 land on a table row, 44 land on a line
   that is not a row, 12 land on a blank line.** So at least 56 are already
   broken, and the 37 that land somewhere are unverifiable because prose carries
   no `row_id` column to check them against. Two documents hold 40 of the 93.
   This is the biggest remaining instance of the defect class and it needs a
   different instrument: the citation has to name its own subject before
   anything can check it.

2. **296 assignment rows whose source is not a census slice.** Their locators
   are line numbers into ledgers, probe scripts and server modules, and they
   rot the same way. A probe script's line numbers rot fastest of all. There is
   no row-label vocabulary in those files to convert to; a per-source anchor
   scheme would have to be designed. The guard prints the count every run.

3. **A stale line number in the range L1-L8 aimed at `profile.md` would pass.**
   That slice numbers its own section L rows `L1`..`L8`, so those eight tokens
   are ambiguous by construction. The collision is eight lines of one file, all
   inside its front matter, and no citation in the corpus points there. On the
   guard's own `NOT checked:` line.

4. **Whether a RESOLVING locator's row actually SUPPORTS its assignment is
   still unchecked.** This wave moved the question from "does it point at the
   right row" to "does the right row say what the assignment claims". That is a
   semantic question and needs a different kind of instrument.

5. **`blocker-map.tsv` was regenerated and absorbed 403 field changes that are
   NOT this wave's.** Attributed per column against the committed file:
   `locator` 76 (this wave, exactly the repair count), `reason_doc` 369 and
   `state_today` 34 (other waves' census movement and corpus growth, which the
   committed map had not absorbed). The committed map was stale relative to its
   own inputs BEFORE this wave touched anything: `build_blocker_map.py --check`
   asserts the ledger totals and never compares the committed file, so a stale
   map passes its own check silently. Worth a separate look.

6. **`M M35`'s `(group of 11)` is an ITEM count, not a row-id enumeration.**
   The grouping row it cites names eleven capability descriptions and states the
   count 11; it does not spell out eleven row ids. `N 104`'s grouping row does
   spell them out. Both are now stable citations, but they are different
   strengths of evidence wearing the same shape, and nothing distinguishes them.

7. ~~The 18 row-label locators were not re-derived from git.~~ **CLOSED in this
   wave, and the answer is in section 1.2:** each was blamed to its own commit
   and re-resolved against the slice as it stood then. 18 resolved identically
   then and now, 0 differed. Nothing is owed here.

8. **`_audit/INSTRUMENTS.md` was deliberately NOT edited, and the three new
   instruments are owed an entry.** `check_census_locators_resolve.py`,
   `_check_census_locators_can_fail.py` and the manufactured fixture all clear
   the register's second law -- each has been shown failing, in section 5 and
   in the control suite. The register was left alone because it is not this
   wave's file and a sibling wave wrote its section 51 today; appending a
   section 52 into a file another wave is holding is how work gets swept into
   the wrong commit. The entry is a one-paragraph append whenever the register
   is quiet.

---

## 7. THE 704 CHECK, AND WHAT WAS AND WAS NOT TOUCHED

`scripts/count_census_states.py`, run before any edit and again after
everything:

| | stated rows | GAP |
|---|---:|---:|
| BEFORE | **704** | 275 |
| AFTER | **704** | 275 |

Unchanged, as it must be: this wave edited the `locator` column of an evidence
file and no census row.

### 7.1 THE GATE WENT RED ON THIS WAVE'S OWN OUTPUT, TWICE

`scripts/impact_gate.py` found no name-based coupling it could trust for a
`.tsv` and a `.md`, so it widened to the whole suite -- and came back
**REFUSED**, twice, on tests this wave had never heard of. Run 1: 1767 tests in
570s, 2 failed. Run 2 after repairing those: 2029 tests in 769s, 1 failed, on a
pair this wave had created while writing up the first failure. Recorded because
a wave that reports only its green run is reporting half of it.

1. `test_the_committed_register_is_what_the_corpus_derives`. `_audit/RULINGS.md`
   prints `documents scanned 216`, and this document made it 217. The register
   was regenerated with `scripts/build_rulings_index.py --write`; the whole diff
   is that one number. Note the trap: `--check` was run BEFORE this document was
   staged and passed, because the register's corpus is `git ls-files` and an
   untracked document is not in it. **A derived-file check run before the new
   file is staged is checking the old corpus.**

2. `test_every_candidate_pair_is_declared_or_triaged`, TWICE -- the second time
   on a pair this wave created while writing up the first. Both got a written
   `NOT_A_CORRECTION` entry naming what would make it wrong.

   - **Section 2 cites `profile.md`** two lines from correction vocabulary.
     Not a correction: the thing corrected is this wave's own uncommitted first
     resolver, and `profile.md` appears beside it as the measurement that
     convicted that draft.
   - **The file manifest below cites `_audit/RULINGS.md`** two bullets from
     `tests/test_a_correction_is_findable_from_the_claim.py`, whose FILENAME
     carries the vocabulary. A bulleted list has no blank lines, so the +-2
     window reaches its neighbours exactly as it does in a table. Regenerating
     a derived file is not correcting it.

   **Neither was answered by rewording the sentence.** Reshaping the input
   until a guard stops objecting is how a guard gets hollowed out, and the
   second pair is the case where rewording was genuinely available -- reorder
   the manifest and it disappears. The guard asked a question with two
   legitimate answers; it got the true one both times.

**Files this wave wrote:**

- `_audit/_census/blocker-assignments.tsv` -- 76 locator cells. No other column.
  Verified field-by-field against `HEAD`: 441 lines before and after, 76 lines
  changed, every change in the `locator` column and nowhere else.
- `_audit/_census/blocker-map.tsv` -- DERIVED, regenerated with
  `scripts/build_blocker_map.py --write`, never hand-merged. See residual 5.
- `_audit/INDEX.md` -- DERIVED, regenerated with
  `scripts/build_audit_index.py --write` to admit this document. 217 -> 218
  tracked documents, 4 insertions and 3 deletions, all of them this document.
- `_audit/RULINGS.md` -- DERIVED, regenerated with
  `scripts/build_rulings_index.py --write`. One line: a corpus count.
- `tests/test_a_correction_is_findable_from_the_claim.py` -- two
  `NOT_A_CORRECTION` entries, named and reasoned. No logic changed.
- `scripts/check_census_locators_resolve.py` -- new guard.
- `scripts/_check_census_locators_can_fail.py` -- new red proof.
- `scripts/_repair_census_locators.py` -- the repair, kept as its own receipt.
- `scripts/check_asserted_names_resolve.py` -- the `NOT checked:` line and the
  matching docstring paragraph. No logic changed.
- `tests/test_a_census_locator_names_its_row.py` -- new.

**Files this wave did NOT touch:** every `_audit/_census/*.md` row state, and
`_audit/INSTRUMENTS.md` (residual 8).
