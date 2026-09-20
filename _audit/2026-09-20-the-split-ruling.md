# THE SPLIT RULING. One cell corrected, one row refused, and they were never
# one decision.

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its ranked table published `NEWSLETTER-SURFACE` at a direction split of one read and eleven writes. The whole newsletter family in the frozen 409 holds only TEN writes, so that cell was not a count of anything and could not have been on the day it was written. The cell now reads the split of the twelve rows the blocker actually holds, derived from the census's own direction column and checkable by a shipped instrument. The ROW COUNT is untouched and is not wrong; section 4 is the argument.

Wave `the-split-ruling`, 2026-09-20, from `8b58dcb`.
Scope: the two census defects `_audit/2026-09-20-newsletter-built.md` handed
over. No capability was built. No browser was opened. No write was fired. Every
measurement below is offline, over committed files and git objects.

---

## 0. THE HONEST LEDGER LINE, FIRST

    rows banked out of GAP          0
    rows inflated                   0   and one was OFFERED -- section 4
    census rows moved               0
    published ROW counts changed    0   the 409 partition is untouched
    blocker-map.tsv bytes changed   0   regenerated, came back identical
    published SPLIT cells changed   1   1R/11W -> 3R/9W, derived not chosen
    capabilities shipped            0   this wave builds nothing
    defects confirmed               1   of the two handed over
    defects DECLINED                1   of the two handed over, with arithmetic
    handover claims re-measured     3   all three agree, section 1
    handover claims SHARPENED       1   the read-side argument is the weak half
    prior art the handover missed   1   and it is a DAY OLDER, section 2
    instruments modified            1   shown failing before it was registered
    instruments NOT written         1   the discriminator already existed
    stale claims corrected in place 2   a docstring and a test comment, both
                                        keeping their text -- 6b and 3a
    defects in my own output        2   a control that passed while the report
                                        lied (9a), and a child brief missing
                                        the line that would have saved it a
                                        turn (10a)
    defects handed on               2   section 7, and neither is newsletter's

**THE SECOND DEFECT IS DECLINED AND THAT IS THE LOAD-BEARING RESULT.** The
handover wave asked that both be ruled together. Ruling them together would
have inflated this blocker by one row against a partition that does not have a
spare, and section 4 shows both shipped instruments going red on exactly that
edit. The two defects live in two different columns of one table row, and only
one of those columns is correctable from evidence that exists today.

---

## 1. THE THREE HANDOVER CLAIMS, RE-MEASURED. ALL THREE AGREE.

A number one agent hands another is a reading with a timestamp the receiver
cannot see, so none of these was taken on trust. Enumeration is the shipped
`enumerate_gap_rows.rows()` over the frozen census at `1c08e5f`; direction is
the census's own R/W column, read at three refs.

### 1a. THIRTEEN newsletter rows -- AGREE

    ref        newsletter-named frozen-GAP rows
    1c08e5f    13      the census commit, the set the ledger divided
    aac33be    13      the ledger's OWN commit
    HEAD       12      N 57 has left GAP since; it is COVERED-CANNOT-DELIVER

    M C50 M C51 M C80 M C81 M C82 M C83 M C84
    N 55  N 56  N 57  N 58
    P L3  P L4

**AND THE NEEDLE WAS WIDENED BEFORE THE COUNT WAS ACCEPTED.** "Newsletter-
NAMED" is a search over the capability cell, which is the claim's own wording,
and a probe aimed by the wording of a claim measures the claim rather than the
system. Re-run over the WHOLE row line at the frozen ref: sixteen rows mention
a newsletter anywhere, of which **thirteen are GAP** -- the same thirteen. The
other three are `N 14` and `N 73`, both `EXCLUDED-RULED` and therefore outside
the 409 entirely, plus a section heading. Twelve further mentions sit in prose
outside any table and name no row. **There is no fourteenth newsletter row
hiding in a note cell.**

### 1b. THE SPLIT IS 3R / 10W -- AGREE

    reads    M C83  N 57  P L4        3
    writes   the other ten           10

Cross-checked against a shipped instrument rather than only against my own
parse: `scripts/_sweep_frozen_rows.py newsletter` prints the identical
thirteen with the identical directions and flags `M C82` as the one
`UNASSIGNED`. Two parses, one answer.

### 1c. ALL THREE READS WERE ALREADY `R` AT `aac33be` -- AGREE

`aac33be` is `docs(blockers): the 409 gaps are 97 blockers`, 2026-09-04 00:40
-- the ledger's birth commit. Reading `messaging-and-content.md`, `network.md`
and `profile.md` out of that object gives 3R/10W, identical to `1c08e5f`.
**Nothing moved between the census and the ledger.** The cell disagreed with
the corpus on the day it was written, which is the handover's central claim and
it is correct.

### 1d. EVERY 12-SUBSET HOLDS AT LEAST TWO READS -- AGREE, computed exhaustively

    12-subsets of 13                        13
      holding exactly 2 reads                3
      holding exactly 3 reads               10
    minimum reads over any 12-subset         2

So `1R` is unreachable by any choice of twelve. **This is the handover's
argument and it is the WEAKER half of the case.** Section 2 is the stronger
one, and it was already in the corpus.

---

## 2. THE STRONGER ARGUMENT WAS ALREADY WRITTEN, A DAY EARLIER, AND THE
## HANDOVER DOES NOT CITE IT

`_audit/2026-09-19-the-remaining-partials.md`, section 5.4, headed *"One piece
of the attack survives, and it is about the instrument"*:

> `NEWSLETTER-SURFACE` publishes `12 | 1R/11W`. The newsletter family in the
> frozen 409 is **13 rows: 10 W and 3 R**. **No subset can be `1R/11W` --
> eleven writes do not exist.**

That is the same defect, found 2026-09-19, by the same shipped sweep, and it is
**strictly stronger than the read-side version**:

    the read-side argument    R >= 2 in every 12-subset       depends on WHICH twelve
    the write-side argument   W <= 10 in the WHOLE family     depends on nothing

The read-side case says the published cell is unreachable *from the thirteen*.
It leaves one escape open, and the escape is not silly: the ledger's twelve
need not have been a subset of the thirteen, and a twelve containing one
non-newsletter write plus one newsletter read would read `1R/11W` honestly.
**The write-side case closes that escape without needing to know which twelve
were chosen**, because eleven writes cannot be drawn from a pool of ten
whatever else is in the set.

I derived the write-side argument independently before finding section 5.4, and
I am recording the prior art rather than the coincidence: the finding is
`2026-09-19-the-remaining-partials.md`'s, the confirmation is the handover's,
and this wave's contribution is the ruling and the correction, not the find.
The handover report cites neither `2026-09-19-the-remaining-partials.md` nor
`2026-09-19-partial-blockers-closed.md` anywhere in its text -- greped, zero
hits -- and presents section 6a as a fresh discovery. It is a re-discovery, and
a re-discovery that arrived by a weaker route.

**THE GENERALISATION, because it is the part that outlives this cell:** section
5.4 ruled it in PROSE, in a document about something else, under a heading that
names an instrument rather than the blocker. Nothing carried it into the
instrument, nothing carried it into the ledger, and twenty-four hours later a
second wave paid for the same measurement again. **A ruling that lives only in
the prose of a document about a neighbouring subject has not been recorded; it
has been mentioned.**

---

## 3. DEFECT 1 -- CONFIRMED, AND CORRECTED

### 3a. WHAT THE CELL NOW READS, AND WHY NOT `3R/10W`

    before   | 19 | `NEWSLETTER-SURFACE` | 12 | 1R/11W  | allowlist +2, ...
    after    | 19 | `NEWSLETTER-SURFACE` | 12 | 3R/9W   | allowlist +2, ...

**The ROW COUNT is not touched.** The correction is confined to the direction
column, and that confinement is the whole reason this half could be ruled
today: the `rows` column is load-bearing for a partition assertion in three
places and the `R/W` column is read by exactly one script.

`3R/9W` rather than the handover's `3R/10W` because the cell describes TWELVE
rows and `3 + 10 = 13`. The twelve are pinned by SHIPPED PACKAGE CODE, not by
this wave's preference: `linkedin_server/readonly.py`'s boundary comment
enumerates the blocker in three named halves -- reader-side five (`N 55`,
`N 56`, `N 57`, `N 58`, `M C80`), author-side five (`M C50`, `M C51`, `M C81`,
`M C84`, `P L3`), analytics two (`M C83`, `P L4`). Five plus five plus two is
twelve, and their directions read 3R/9W off the census column. The shipped
split checker independently reports this blocker as `held R3 W9`.

**AND `M C82` IS NAMED NOWHERE IN THE PACKAGE -- measured, whole directory,
zero hits.** That is the negative half of the same evidence and it is worth
the grep: the enumeration does not merely omit the row, the codebase that
enumerates this blocker has never heard of it. A reader who assumes the
omission was an oversight has something to check rather than a silence to
interpret.

**AND THE ROLE-vs-DIRECTION TRAP IS LEFT STANDING, because it is correct.**
`tests/test_blocker_map_is_derived.py`'s evidence block warns that the
reader-side/author-side halves must not be read as a direction split -- *"THE
1R/11W SPLIT IS NOT CONTRADICTED although it reads as if it is: reader-side is
a ROLE ..., not an operation class, and unsubscribing from one he reads is
still a write."* That comment is defending the cell against a bad argument
(five "reader-side" rows do not mean five reads) and it defends it correctly.
It is not a defence of the cell against the census's own direction column,
which is the argument that convicts it. The comment keeps its text and gains
a dated note beneath it saying which of the two questions it settles.

### 3b. THE CORRECTION IS CHECKABLE, WHICH THE OLD CELL WAS NOT

Before and after, `scripts/_check_published_split.py`:

    before   OVER on R    NEWSLETTER-SURFACE   published R1 W11 RW0   held R3 W9 RW0
    after    (not reported -- published and held agree)

A published cell that no instrument can derive is not a figure, it is a
sentence about a figure. The new one is the output of a parse anybody can
re-run.

---

## 4. DEFECT 2 -- DECLINED. THE COUNT IS NOT HOLDING `M C82` OUT; THE LEDGER
## SIMPLY DID NOT FILE IT HERE.

The handover reports `M C82` "Share a Newsletter Page" as unassigned *"because
admitting it would make thirteen rows against a published twelve -- i.e. the
published number is holding a real row out of the census."* **I disagree, and
the disagreement is arithmetic rather than taste.**

### 4a. THE DIVISION IS A PARTITION, SO THERE IS NO SPARE ROW

The ledger's 97 published counts sum to **409**, which is exactly the frozen
GAP total. So the division is a partition and `M C82` is ALREADY inside
somebody's published count. It is not outside the census waiting to be let in.
The question was never "may this row enter"; it is "whose published share is it
in", and nothing in the handover answers that.

Measured, in one pass over the map:

    UNASSIGNED rows                                     19
    unexplained holes across the other 96 blockers      19
    holes at NEWSLETTER-SURFACE                          0

The nineteen unassigned rows exactly fill nineteen holes, and none of those
holes is here. `NEWSLETTER-SURFACE` is COMPLETE at 12 of 12 with zero incoming
re-files. A shipped instrument says the same thing more directly --
`scripts/_check_open_slots.py` prints the per-blocker open-slot table and
**`NEWSLETTER-SURFACE` does not appear in it at all**, because it has no open
slot. It also prints that 10 of the 19 slots are fillable and **9 rows can
never be filed by anybody**; `M C82` is among the nineteen, and the ledger
offers it no seat here.

**THE HANDOVER DID NOT RUN THAT INSTRUMENT.** It is the check that answers its
own question, it has shipped since 2026-09-19, and it is one command.

### 4b. THE RED REPRODUCTION -- the edit the "one ruling" reading requires

Applied to a COPY of the ledger, with `build_blocker_map.LEDGER` repointed so
no tracked file was touched:

    | 19 | `NEWSLETTER-SURFACE` | 12 | 1R/11W  | ...     ->
    | 19 | `NEWSLETTER-SURFACE` | 13 | 3R/10W  | ...

`scripts/build_blocker_map.py --check`, exit **1**:

    ledger blockers parsed              97  rows 410
      FAIL: the ledger's own tables no longer total 97 blockers / 409 rows
    ...
    NEWSLETTER-SURFACE                 13   12     -1  PARTIAL -- 1 row(s)
      neither held nor named as re-filed by any committed source

`scripts/_check_open_slots.py`, its documented control firing:

    CONTROL FAILED -- the ledger's published total (410), the map's data lines
    (409) and the frozen GAP set (409) must all agree. They do not, so no
    open-slot figure below would be comparable.

**READ THE SECOND LINE OF THE FIRST BLOCK AGAIN.** The edit does not admit
`M C82`. It MANUFACTURES A HOLE for it and then reports the blocker as PARTIAL
-- because publishing a thirteenth row and assigning a thirteenth row are two
separate acts, and the edit performs only the first. The blocker would go from
COMPLETE to PARTIAL on the strength of a change made to close a gap. And
because `--write` refuses while any assertion is red, the map would not
regenerate at all, so **the split correction would have gone down with it.**

### 4c. WHAT WOULD ACTUALLY UNBLOCK IT, stated so the next wave does not
### re-derive it

For `M C82` to enter this blocker, somebody must name the blocker whose
published count is one too high -- a FIFTH ruled phantom, joined to a thirteenth
newsletter row, so the partition still closes at 409.
`scripts/_check_open_slots.py` already carries a RULED-PHANTOM table with four
entries and the convention for adding one. That is a measurable task with a
named artifact, and it is a different task from correcting a split cell.

On today's evidence the likeliest published home is not here at all. `M C82` is
a SHARE action on a Newsletter *Page*, which the handover itself measured to be
an organisation-shaped product -- *"A Newsletter Page is an organisation-shaped
product and no measurement here reaches it"* -- and `COMPANY-PAGE-SURFACE`
carries **two fillable slots**. That is a hypothesis with an address, not an
assignment, and this wave files nothing on it. A bare count match is a birthday
problem; this repository has already declined one row on exactly that ground.

### 4d. AND THE MAP'S REASON CELL FOR `M C82` IS CORRECT -- checked, not assumed

I expected to find the old universal negative here and did not:

    M C82  UNASSIGNED  ...  no line in blocker-assignments.tsv files this row,
                            and no probe mark in
                            scripts/_probe_jobs_tail_boundary.py names it

Both clauses name their lookup and both are true. That is the 2026-09-19 fix
working, and the cell is left alone. **A defect I went looking for and did not
find is worth one line, because the next reader will go looking too.**

---

## 5. SO: ONE RULING OR TWO? -- TWO, and the instrument that separates them is
## `_check_open_slots.py`

The handover's closing recommendation is *"`M C82` AND THE SPLIT CELL ARE ONE
DECISION, NOT TWO. Both say the ledger's published figures for this blocker are
short a row and short two reads."*

**They are two, and the premise they share is false.** The figures are not
short a row. They are short two reads in the DIRECTION column, which is
derivable and was corrected here, and they are exactly right in the ROWS
column, which is a share of a partition with no spare. The two defects sit in
two cells of one table row and that adjacency is the whole of their
resemblance:

| | the `R/W` cell | the `rows` cell |
|---|---|---|
| read by | one script, a report | three assertions and the 409 figure |
| correct value derivable today | YES, from the census column | NO, needs a fifth phantom named |
| changing it moves the partition | no | yes, to 410 |
| verdict | CORRECTED | DECLINED, with the unblocking step named |

Ruling them together is not a tidier version of ruling them apart. It is the
move that takes a correctable cell hostage to an unevidenced one, and section
4b is the measurement of what it costs.

---

## 6. THE INSTRUMENT: THE DISCRIMINATOR EXISTED AND THE REPORT DID NOT CALL IT

The handover asks whether `_check_published_split.py` needs to distinguish the
three causes of a direction over-run. **It does, and I did not need to build
the discriminator, because 21.2 already shipped it.**

`_check_published_split.py`'s docstring frames an over-run as two things:

    a published row was LOST, nobody can say which        -> a real hole
    a published row was RE-FILED OUT and this map HAS it  -> not a hole at all

Both of those describe movement AFTER publication. The third cause is an error
AT publication, and the report cannot show it because it prints published
against held and stops.

**THE DISCRIMINATOR IS ONE SUBTRACTION AND IT ALREADY HAS A HOME.**
`scripts/_check_refile_destination_credit.py::publishers()` returns
`{row id: (blocker that PUBLISHED it, blocker it went to)}`. Subtract the
incoming rows' directions from `held` and the two reported over-runs come apart
cleanly:

    NEWSLETTER-SURFACE
      published rows 12   R1  W11         held rows 12  R3  W9   OVER on R
      own only  rows 12   R3  W9          STILL OVER on R
      count verdict: own 12 vs published 12 -> COMPLETE

    SEARCH-RESULTS-SURFACE
      published rows 21   R19 W2          held rows 21  R20 W1   OVER on R
      own only  rows 17   R16 W1          NOT OVER -- the surplus was incoming
      count verdict: own 17 vs published 21 -> UNDER by 4

Same two words in the report -- `OVER on R` -- and two unrelated situations.
One blocker is over because four rows arrived from three other blockers on
committed rulings, and its OWN rows are four short. The other is over with
nothing arriving, nothing missing, and a count that closes exactly. **Nothing
moved and nothing is lost, so the only thing left that can be wrong is the
published figure.**

So the classification the script now prints:

    RE-FILED-IN    the over-run vanishes once incoming rows are subtracted
    LOST           the blocker is UNDER on its own count; rows are missing
    AT-BIRTH       COMPLETE on count, nothing incoming, and still over

**AND FIXING THE LEDGER WOULD HAVE ERASED THE EVIDENCE.** Once section 3's
correction lands, `NEWSLETTER-SURFACE` stops being reported at all and the
report drops to one over-run -- which reads as RE-FILED-IN, the only cause the
docstring names. The class would have been demonstrated and then deleted in the
same wave. That is the argument for doing both halves and for doing the
instrument FIRST.

### 6a. SHOWN FAILING, because a check that cannot fail certifies nothing

Section 9 carries the exercise: each of the three causes driven into the
classifier, and the classifier shown printing the WRONG one before the fix.

### 6b. AND THE DOCSTRING'S OWN JUSTIFICATION IS AMENDED -- IT WAS ONE OF
### THREE, NOT TWO

The docstring argues it is a report rather than a gate because *"Two of the
three known over-runs are documented and were ruled deliberate, so a red gate
here would fail CI on work somebody decided."* That sentence is doing real
work: it is the reason nobody promoted this check to an assertion.

A delegated read-only sweep of the committed corpus, reviewed here and
spot-checked against git objects before any of it was banked, returns:

**AND IT IS AN INDEPENDENT DERIVATION, WHICH IS WORTH MORE THAN EITHER HALF
ALONE.** The slice was briefed only to find out which two the docstring meant;
it was not told what this wave had concluded, and it reached the same verdict
from committed sources alone. **My uncommitted draft of this very document was
sitting in the tree it read, and it did not use it** -- it found the untracked
file, stopped, flagged a possible concurrent writer, quarantined the file out
of its committed-evidence answer, and reported it in a separate paragraph
marked *"Not committed"*. So the agreement is two derivations meeting, not one
derivation read twice. The one thing the slice supplies that I did not have is
the PROVENANCE below, which no arithmetic would have produced.

| over-run | ruled deliberate by a committed source? |
|---|---|
| `SEARCH-RESULTS-SURFACE` | **YES.** Commit `5a5d2a3`'s own message: *"THE SPLIT IS NOT CLAIMED FOR THE POST-FREEZE SET ... which is what a re-file does"*. Verified by reading the object. |
| `COMPANY-PAGE-SURFACE` | **NO -- open.** Measured twice and called an open ruling request both times; never adjudicated. |
| `NEWSLETTER-SURFACE` | **NO -- refuted.** The only documents that checked the arithmetic ruled the opposite. |

**So it is ONE of three, not two.** And the third is not merely undecided: it
is refuted, twice, a day apart, by two different documents.

**THE PROVENANCE IS THE PART WORTH KEEPING.** The claim entered the record as
*ruling request D* in `_audit/2026-09-19-partial-blockers-closed.md`, which
asserted it at the point of raising it and without adjudicating it, and was
ratified as a ruling in `_audit/2026-09-19-the-five-requests-ruled.md` section
D, which kept the check a report ON THAT PREMISE. Nobody re-derived the count
between the request and the ruling. **A ruling that inherits its premise from
the request that asked for it has not been adjudicated; it has been echoed**
-- and this one then travelled into a docstring, where it became the standing
argument against gating the check that would have caught it.

The sentence keeps its text, because the POLICY it sets is still right, and
gains the corrected count beneath it.

Verified live on the committed, unmodified sibling instrument, since
`COMPANY-PAGE-SURFACE` is the one this file cannot see --
`scripts/_check_jobs_range_directions.py`:

    OVER on R  COMPANY-PAGE-SURFACE  published R13 W5 RW0  held R14 W2 RW0  short on W

---

## 8. THE BEFORE/AFTER, BY ARTIFACT

### 8a. `build_blocker_map.py` -- BYTE-IDENTICAL, WHICH IS THE POINT

    diff  map-BEFORE-ledger.txt  map-AFTER-ledger.txt
    (no differences)

    ./venv/Scripts/python.exe scripts/build_blocker_map.py --write
    wrote _audit/_census/blocker-map.tsv  409 data lines
    git status --short _audit/_census/blocker-map.tsv   ->  (nothing)

The map was regenerated from the corrected ledger and came back the same file,
so `git status` does not list it. **The correction moved zero rows**, and that
is the artifact-level statement of section 5's argument: the `R/W` column and
the `rows` column are not the same claim, and only one of them was touched.

Both readings passed all four of the builder's assertions, including
`assigned + unassigned == 409` and `the ledger's own tables total 97 blockers
and 409 rows`.

### 8b. `_check_published_split.py`

    BEFORE
      OVER on R  NEWSLETTER-SURFACE      published R1 W11  held R3 W9
      OVER on R  SEARCH-RESULTS-SURFACE  published R19 W2  held R20 W1
      blockers OVER on some direction   2

    AFTER
      OVER on R  SEARCH-RESULTS-SURFACE  published R19 W2  held R20 W1
          incoming R4 W0 RW0   own R16 W1 RW0
          CAUSE RE-FILED-IN -- the surplus is rows that ARRIVED here on a
          committed re-file; the published cell is not implicated
      blockers OVER on some direction   1

**THE `2 -> 1` IS EXACTLY WHY THE INSTRUMENT HAD TO CHANGE FIRST.** After the
ledger correction the AT-BIRTH case is gone from the report, and the one
remaining over-run is the cause the docstring already named. A wave that fixed
only the ledger would have left a report that agrees with a docstring which is
wrong about a class it can no longer demonstrate.

### 8c. Unchanged, and checked rather than assumed

`_audit/_census/blocker-map.tsv` (byte-identical), the frozen 409, the 19
UNASSIGNED rows, every census slice, `blocker-assignments.tsv`, and
`_check_open_slots.py`'s open-slot table.

---

## 9. EVERY CONTROL SHOWN FAILING

`--control-causes` is new; `--control` is the pre-existing one and had to keep
passing. Each mutation was applied in-process to the imported module and
reverted.

| mutation | what it models | `--control` | `--control-causes` |
|---|---|---|---|
| the classifier returns the same word every time | the commonest defect in a three-way classifier | exit 0, **BLIND** | exit 1, names 2 of 3 WRONG |
| `_incoming()` stubbed to `{}` | re-deriving instead of importing `publishers()` | not applicable | exit 1, `DEAD, the subtraction reaches nothing` |
| the clean-victim pool starved | register 21.1's recorded failure: injecting into a blocker the report already names | not applicable | exit 2, REFUSES to inject |

Healthy afterwards: plain exit 0, `--control` exit 0, `--control-causes` exit 0.

### 9a. AND THE SECOND MUTATION CAUGHT MY OWN CONTROL, PASSING

On its first version `--control-causes` returned **exit 0** with
`_incoming()` stubbed to nothing -- all three injected cases classified
correctly -- **while the report printed, four lines above, that
`SEARCH-RESULTS-SURFACE` was AT-BIRTH.** That is the verdict this whole
classifier exists to reserve for a published figure that was wrong when it was
written, handed to a blocker whose surplus is four documented arrivals.

The cause is worth naming because it generalises past this file: the
RE-FILED-IN injection plants its own arrival into the `incoming` table, so the
control exercised the classifier's LOGIC and never its INPUT. **A control that
supplies the very input whose derivation it is meant to protect will certify an
instrument that is already lying.** Repaired by asserting the derivation is
live -- arrivals derived from `publishers()` must equal the number of
`RE_FILED` rows and must not be zero:

    HEALTHY                 arrivals 5 against 5 RE_FILED rows -- LIVE            exit 0
    _incoming STUBBED       arrivals 0 against 5 RE_FILED rows -- DEAD ...        exit 1

---

## 7. DEFECTS HANDED ON

1. **`M C82` NEEDS A FIFTH RULED PHANTOM, NOT A COUNT EDIT** -- section 4c. The
   task is: name the blocker whose published count has no referent inside the
   409, so a thirteenth newsletter row and a phantom cancel and the partition
   still closes. `COMPANY-PAGE-SURFACE` is the addressed hypothesis and it is
   not an assignment.
2. **THE SPLIT CHECKER IS STILL BLIND TO 20 OF 88 BLOCKERS** -- it skips any
   blocker holding a row whose direction it cannot read.
   `scripts/_check_jobs_range_directions.py` exists to widen exactly that and
   is a separate script; the two have never been joined, so the count of
   unwatched splits depends on which of the two a reader happens to run.
   `COMPANY-PAGE-SURFACE`, the third known over-run, is on the blind list.
3. **NOT A DEFECT, RECORDED SO IT IS NOT RE-FOUND:** `M C82`'s UNASSIGNED
   reason cell is correct and scoped (section 4d), and the role-vs-direction
   comment in `tests/test_blocker_map_is_derived.py` is correct as written
   (section 3a). Both look like defects from the outside.

---

## 10. FILES, AND ONE DELEGATION DEFECT THAT WAS MINE

Changed:

- `_audit/2026-09-03-linkedin-gap-blockers.md` -- the ranked table's
  `NEWSLETTER-SURFACE` direction cell, and a `CORRECTED BY:` back-pointer.
  **The marker sits in the prose ABOVE the table, after the existing two and
  before the blank line that precedes the header row.** A prior session put
  one BETWEEN a table header and its first data row, which made the ledger's
  parser take zero rows so every blocker read as unknown, and pushed it. The
  before/after in section 8a is the check that it did not happen again.
- `scripts/_check_published_split.py` -- the three-way cause classification,
  `--control-causes`, the derivation-liveness assertion, and two amended
  docstring paragraphs that keep their text.
- `tests/test_blocker_map_is_derived.py` -- a dated scope note under the
  role-vs-direction comment. The twelve enumerated rows are unchanged.
- `tests/test_a_correction_is_findable_from_the_claim.py` -- two
  `NOT_A_CORRECTION` entries, each written after reading the line that
  produced the pair. Both are the INVERSE of a correction: this document
  cites those two because they were right, and right first.

Not changed, deliberately: `_audit/_census/blocker-map.tsv`,
`blocker-assignments.tsv`, every census slice, every published ROW count.

### 10a. THE DELEGATED SLICE, AND THE LINE ITS BRIEF WAS MISSING

`overrun-rulings` was a read-only corpus search. It was reviewed before
anything entered this report, and two of its load-bearing claims were
re-verified here against git objects rather than taken on its word.

**ITS BRIEF DID NOT TELL IT THAT IT SHARES THIS WORKTREE WITH ME**, so it
spent its opening section discovering my uncommitted files and reasoning about
whether a concurrent writer was live. The reasoning was correct and the
quarantine it applied was correct -- that is the model working -- but it was a
turn spent on something one sentence in the brief would have settled. Every
child brief from here carries it.

**AND THE SHARPER HALF, which did not bite today only because the slice was
read-only:** a child that MEASURES while its lead EDITS has a denominator that
moves under it. Such a child should freeze the tree first --
`git stash create`, record the sha, then read every path with
`git show <sha>:<path>` for the rest of its run. That touches neither the
working tree nor the shared stash stack. **And its calibration corpus and its
measured corpus must come from the SAME sha**, or a control proves the
instrument works on a file that is not the one being measured. This wave's own
section 1 is the positive case: every count in it was taken at a named ref, not
from the working tree.

---
