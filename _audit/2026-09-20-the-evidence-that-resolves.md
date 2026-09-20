# The evidence that resolves: 22 citations repaired, and 9 banked rows nobody can check

**Wave:** evidence-that-resolves. **2026-09-20.** Base `e6b11e5`, merged forward
three times as `master` moved under the wave -- `96e90f3`, `724d327`, then
`c0cab56` and `043a292` -- and every figure below is the reading AFTER the last
of those. Text and git archaeology only: no browser, no LinkedIn surface, no
page load.

One question, two artifacts: **can a reader starting from a clone reach this
corpus's evidence?**

    HALF A  22 dangling SHA citations       ->  22 of 22 REPAIRED, 0 unrepaired
    HALF B  banked rows resting on evidence
            no clone can reach              ->  9   (exact; of 94 banked rows)

**HALF B's ANSWER MOVED WHILE THE WAVE RAN, AND RE-MEASURING RATHER THAN
RELAYING IS THE ONLY REASON IT IS RIGHT.** It read 7 at first measurement, 7
again after the first merge, and 9 after the second, when a sibling wave banked
thirteen further rows and two of them cited `_audit/_scratch/`. A third reading
briefly said 8 and was wrong for a different reason, in section *"the merge
moved the denominators"* below.

---

## HALF A -- THE 22, AND THE THING THE PREVIOUS WAVE COULD NOT SEE

`_audit/2026-09-20-the-sixty-dangling.md` found 22 distinct SHAs across 29
citations in 19 documents that no clone resolves, pinned them, and deliberately
did not repair them. Its diagnosis of the cause was exactly right: each was a
commit made on a `worktree-agent-*` branch by a wave that then wrote up its work
citing that SHA, on a branch that never merged.

**What it did not measure, because pinning does not require it: every one of
those 22 commits has an exact twin on `master`.** The branch never merged; the
WORK was re-applied. So all 22 are repairable by remap, and none needed an
"it never landed" annotation.

### The twin table, and the seven checks behind every row

| dead | live | dead | live | dead | live |
|---|---|---|---|---|---|
| `f6ddfe3` | `8450abd` | `c1991ac` | `0aca3d0` | `eed87a5` | `097626a` |
| `ae1894b` | `3c0b3e1` | `744a1f4` | `f370443` | `59192ac` | `de2d4bf` |
| `c4d2be2` | `5073827` | `7668b40` | `bd0cfad` | `889f488` | `1c84d34` |
| `1349fe6` | `81c8534` | `a5a988a` | `4ac5b61` | `5c5ebf9dda43` | `851bf80d5e8a` |
| `a604394` | `9e28aec` | `12c20e1` | `e72af67` | `70d7c0f62e97` | `f66107c2c17b` |
| `7bca683` | `29e4613` | `569dc5e` | `09f9961` | `ded0048` | `eb1b6e8` |
| | | `d588034` | `5952ace` | | |
| | | `c48ec60` | `a0379d5` | | |
| | | `66e2038` | `266d030` | | |
| | | `806360a` | `1b94540` | | |

**22 of 22 clean on all seven**, and a plausible-looking remap is exactly the
failure this repair must not commit, so the checks are listed with what each one
rules out:

| check | what it rules out |
|---|---|
| the live hash is an ancestor of `master` | a twin that is itself branch-only |
| the dead hash is NOT an ancestor of `master` | a citation that was never broken |
| subjects byte-identical | the wrong commit with a similar message |
| author identity and date byte-identical | a re-authored or amended commit |
| **`git patch-id --stable` identical** | **a commit that says the same and DOES something different** |
| that subject occurs EXACTLY ONCE on `master` | an ambiguous key a reader cannot follow |
| the dead hash prefixes exactly ONE object | an abbreviation that resolves two ways |

`patch-id` is the load-bearing one. A subject match alone would satisfy a
re-derived commit carrying different text -- which is the specific hazard the
integrator named, and the reason it warned that a hash carrying different text
is worse than an annotation. **Identical patch-ids say the content is the same,
not merely the message.**

**THE CONTROLS, because seven checks that cannot fail certify nothing:**

    master^0 is an ancestor of master                  True   (expect True)
    integrate-1821 tip is an ancestor of master         False  (expect False)
    two unrelated master commits share a patch-id       False  (expect False)
    a subject no commit has, counted on master          0      (expect 0)

### The repair, and why the dead hash stays

`_audit/2026-09-20-the-sixty-dangling.md` already ruled it and this wave did not
re-open it: **a rewritten hash is the key a reader arrives with and must be
kept.** So nothing was overwritten. Each of the 19 documents gained:

1. a **SHA NOTE** under its title naming its branch-only hashes;
2. a **`## Dead hashes, recovered`** table at the foot -- the corpus's own form,
   the one the 2026-09-03 repair used and the sixty-dangling wave re-verified
   22 of 22 clean -- mapping each dead hash to its subject and its live twin.
   **27 rows across 19 documents.**

and, at 21 of the 26 (token, document) citation sites, a marker in the prose:

    Applied at `c4d2be2` (branch-only; on `master` at `5073827`).

**THE MARKER'S SHAPE IS THE POINT, NOT ITS WORDING.** ``on `master` at `X` ``
places the live hash in the ``at `X` `` slot `check_cited_shas_resolve.py`
already reads, so **a marker naming a hash that does not resolve is convicted by
the existing, already-controlled matcher.** No new matcher was needed for that
half, which is how the brief's second trap was avoided rather than argued with.

**FIVE SITES ARE DELIBERATELY UNMARKED, and the reason is the same each time:
the line is not that document's own prose.**

| document | sites | why |
|---|---|---|
| `2026-09-19-groups-admission.md` | 3 | inside an indented verbatim transcript |
| `2026-09-19-blocker-table-refresh.md` | 1 | inside a block the document itself labels as another wave's words, left byte-identical |
| `2026-09-19-the-first-sanctioned-press.md` | 1 | inside the quoted record banner the document exists to preserve |

**Editing a transcript to improve it falsifies it.** Those five are covered by
the note and the table, and each document's own note says which.

### A repaired citation is now distinguishable from an unrepaired one BY THE PARSER

That was the brief's first trap. The answer is not a new marker vocabulary --
it is that `MARKED-MAPPED` and `UNRESOLVED` are different verdicts, and the
suppressor that hands down the first now **pays for itself**.

`MARKED-MAPPED` is the strongest suppressor this guard has: one table row
silences a dead hash at every site in its document. Until today it fired on the
mere PRESENCE of the hash in column 0. A row naming a garbage live hash, or
none, switched the guard off just as effectively as a correct one. **A repair
nobody can check is this guard's own defect wearing its uniform.**

`broken_remaps()` now requires, per row: a live hash exists; it resolves as an
ancestor of `master`; the subject cell byte-matches that commit's real subject;
and the row does not map a hash to itself. **Shown failing four ways** on
planted rows, with a positive control on a correct row so the red proves
something.

**AND IT CONVICTED THE CORRECT REPAIR ON ITS FIRST RUN.** It red-flagged
`94600de` and `db99276` in `2026-08-24-perform-save-unsave.md`, whose rows read
`| ... | **UNMAPPED** -- see below | -- | UNMAPPED |` above two paragraphs
explaining that every positional candidate is already claimed on better
evidence. The sixty-dangling wave had already ruled on precisely that:
*"'UNMAPPED' is not a shortfall. A guessed hash has no twin to find. Recording
the gap IS the repair."* A guard that convicts the honest annotation is a guard
that gets switched off, so a row that **declares** no twin (`UNMAPPED`, or
`NEVER-LANDED` for the neighbouring class) is counted and printed rather than
convicted -- and the exemption is controlled by defeating it: the same row with
an ordinary confidence cell is still a finding. **Silent and honest are
different, and that difference is the whole check.**

### The arithmetic, stated so a quieter guard would show

The brief's warning was that this corpus has three times mistaken prose about a
mechanism for the mechanism, and each time **the guard got quieter**. So the
before/after was taken as counts, not as a green:

| verdict | before | after | delta | expected |
|---|---:|---:|---:|---|
| commit-slot occurrences | 263 | 285 | **+22** | 21 markers, +1 from a subject quoted into a table |
| CANDIDATE | 224 | 216 | **-8** | +21 new live hashes, -29 sites now mapped |
| MARKED-MAPPED | 14 | 44 | **+30** | the 29 sites, +1 new |
| MARKED-DISCLOSED | 16 | 16 | **0** | the note avoids every disclosure phrase |
| MARKED-CROSS-REPO | 7 | 7 | 0 | untouched |
| MARKED-DEAD-DOC | 2 | 2 | 0 | untouched |
| findings | 29 | **0** | -29 | |

Every delta lands on its prediction exactly. **`MARKED-DISCLOSED` holding at 16
is the one that matters most**, and it is not luck: the SHA NOTE's wording was
written to avoid `does not resolve`, `cannot reach`, `no clone can reach`,
`unresolvable`, `is dead` and `nowhere on` -- because if the note ALSO disclosed,
every repaired token would be covered twice and the per-source mutation control
could no longer show the mapping table doing the work. That is the
"a union assertion over a redundant corpus cannot detect a lost source" defect,
which the previous wave paid for and wrote down.

### TWO DEFECTS IN MY OWN REPAIR, FOUND BY MEASURING IT RATHER THAN READING IT

The first pass of the repair looked correct, the guard went green, and both of
these were still present.

**1. SIX MARKERS WERE VERIFIED BY NOTHING.** `candidates()` scans line by line.
Six markers wrapped between `at` and the backtick, so their live hashes sat in
no slot at all -- the self-verification that justifies the marker's shape was
simply absent on six of twenty-one, and the guard was green anyway.

**2. ONE REPAIRED TOKEN VANISHED INSTEAD OF READING AS REPAIRED.** `806360a`
sits in the `landed-after` slot, which needs `` `HEX` land `` adjacent on one
line. The marker went between them. The token then appeared in NO slot, so the
guard stopped seeing it entirely -- **and a citation the guard cannot see is
indistinguishable from one somebody deleted.** The whole wave is about that
distinction.

Both are pinned by `test_every_inline_remap_marker_is_self_verifying`, which is
itself mutation-controlled (`test_the_marker_matcher_convicts_a_wrapped_marker`
breaks a marker the same way and asserts the token leaves the slot). A third
non-uniformity -- one marker wrapping between `` `master` `` and `at`, still
verified but in a second spelling -- was caught by that test's count floor and
made canonical, **because a matcher that tolerates two spellings will one day
tolerate three and then miss one.**

### THE FOURTH INSTANCE OF THAT SHAPE, AND THE FIRST ONE THAT WENT THE RIGHT WAY

This document quotes the marker verbatim, three sections above, to explain it:

    Applied at `c4d2be2` (branch-only; on `master` at `5073827`).

**That is a real citation of a branch-only hash, in a document with no mapping
table, and the guard convicted it** -- one finding, named, at this file's own
line 85, on the first run after the file was written.

The repository has now hit "prose about a mechanism is indistinguishable from
the mechanism" four times. The first three all failed the same way: the matcher
read the quote AS the mechanism and **the guard got quieter** -- a
correction-marker guard reading a sentence about markers as a marker; the
instrument register quoting a planted citation into a live commit slot; and
`MARKED-DEAD-DOC` going 2 -> 9 when the reporting document quoted the
declaration.

This one went the other way, and it went the other way BY CONSTRUCTION rather
than by luck. The marker is deliberately **not** a suppressor -- the mapping
table is -- so quoting a marker cannot clear anything; it can only add a
citation that must then be answered. `test_a_marker_alone_suppresses_nothing`
pins exactly that.

**So this document carries its own `## Dead hashes, recovered` table**, at the
foot, with the one row it owes. Held to the same discipline as the nineteen it
repaired, by the same check, which then verified its live column.

### The pin is now EMPTY, and that is stronger than 26

`tests/test_a_cited_sha_resolves.py` `PINNED` went from 26 (token, document)
rows to `set()`. The two-way ratchet still runs. **With nothing pinned, any
regression in any suppressor puts a citation straight back into `bad` and the
test goes red naming it** -- where a pin of 26 absorbed exactly those
regressions silently for those 26. The one direction an empty pin cannot cover
is the detector going blind, and that is held by the planted-citation red proof,
the every-suppressor-fires control, and the new mapping-row red proof.

---

## HALF B -- WHAT A CLONE CANNOT REACH. **THE COUNT IS 9.**

**MEASURED, NOT DEMOTED.** Moving a row out of a banked state is a ruling and it
is not mine. Below is the count and the per-row list with the specific artifact
named.

### The denominators, printed because a finding without them is not a measurement

**Re-measured after each of two merges of `master`, because the census moved
under this wave three separate times while it ran.** Figures below are the
final reading, at the second merge.

    census slices read                     4
    table lines seen                     929
      rows naming a state                704
      rows naming none                   197   headers, summary tables, prose
      rows naming several                  0   NOT guessed at
      state-legend rows                   28   the state IS the row id
      MISSPELLED state cells               0   shipped `dialect_of`
    rows in a BANKED state                94   (79, then 81, then 94)
    evidence artifacts cited             126   (87, then 93, then 126)
      TRACKED                            110
      GITIGNORED                          15
      ABBREVIATED                          1   reachable, but not as written
      ambiguous / unclassifiable           0

**THE STATE VOCABULARY IS IMPORTED, NOT REBUILT.**
`scripts/count_census_states.py` already owns this problem and owns it better:
it holds `ER`, `CCD` and `CANNOT-DELIVER` beside the long forms, each admitted
with its receipt, and `tests/test_state_cell_dialects_refuse_loudly.py` guards
it. A hand-rolled vocabulary here would have been the third in this repository.
**The switch was measured, not assumed to be a tidy-up: the banked count stayed
79 and the finding count stayed 7.** What it buys is the dialects and a loud
report if a slice ever invents a new one -- and an import-time refusal if a
spelling this file banks ever leaves the shipped vocabulary, so the two can
never drift apart silently.

It also produced one false positive worth recording, because the scoping is now
load-bearing: the shipped `dialect_of` reports `ABSENT` twice, both on
`network.md` lines 171-172, in a two-column table about page ADDRESSES where
`ABSENT` means the page is not drawn. It is a shouted word built only from the
state vocabulary's own atoms, so the heuristic cannot help but see it. The
dialect report is scoped to rows with at least four cells -- a capability row's
shape in these slices -- because crying wolf here is expensive in the one place
this instrument most needs to be believed.

### THE ANSWER

    BANKED ROWS RESTING ON AT LEAST ONE ARTIFACT NO CLONE CAN REACH   9
      of those, rows with NO reachable artifact at all                0
    BANKED ROWS DESCRIBING A LIVE RUN WITH NO TRACKED SCRIPT         26

**IT WAS 7 WHEN THIS WAVE STARTED AND 7 AFTER THE FIRST MERGE. THE SECOND MERGE
MADE IT 9, AND THAT IS THE FINDING RATHER THAN A NUISANCE.** A sibling wave
banked thirteen more rows, and two of them -- `jobs.md` 27 and 151 -- cite
`_audit/_scratch/` paths. **This is not an inherited mess being counted down;
the generator is live.** A row banked today can land in this set tomorrow,
which is precisely what a two-way ratchet is for and why the pin is worth more
than the number.

### THE MERGE MOVED THE DENOMINATORS AND NOT THE ANSWER, AND IT NEARLY MOVED THE ANSWER

Three of the four slices changed on `master` while this wave ran. Re-measuring
after the merge -- rather than relaying the figure taken before it -- is the
whole of why the number above is 7 and not 8.

The re-run reported **8**. The new row was `messaging-and-content.md` `M4`,
which `master` had just corrected from `EXCLUDED-RULED` into `MEASURED-ABSENT`
-- so it entered the banked population for the first time, bringing its
citations with it. One of them is `perform.md:3462-3487`, and **no tracked file
is named `perform.md`**, so the strict rule classed it NOT-IN-REPO and it
counted.

**It should not count, and the reason is checkable.** Exactly one tracked
basename ENDS with that name -- `_audit/2026-08-31-linkedin-perform.md` -- and
the line number settles it beyond argument: that file has **4,966 lines** while
the only other candidate containing "perform" has **298**, so line 3462 exists
in precisely one of them.

> **THE EVIDENCE IS REACHABLE; THE PATH AS WRITTEN IS NOT. Those are different
> complaints, and folding the second into the first inflates the one integer
> this instrument exists to state exactly.**

So `ABBREVIATED` is its own class: printed in full with the row that carries
it, and NOT counted as a finding. It is a real thing to fix -- the citation
should name the file -- and it is not a reader who cannot reach the evidence.
The mirror is asserted in both directions, or the class would be a hole rather
than a distinction: a name matching nothing is still NOT-IN-REPO, and a name
matching exactly is still TRACKED.

**The 7 were the same 7 rows as before that merge**, and the pin -- keyed on
(slice, row id, state) rather than on a line number -- held across it while
`network.md` row 136 moved from line 439 to 458.

### The 7, with the artifact named

| slice | row | state | line | the artifact a clone cannot reach | class |
|---|---|---|---:|---|---|
| `jobs.md` | 9 | COVERED-PROVEN | 190 | `_audit/_scratch/_progress-job-search-params.md`, `_audit/_scratch/_probe-jobsearch-result-sets-run2-17loads.txt` | GITIGNORED |
| `jobs.md` | 11 | COVERED-PROVEN | 192 | same two | GITIGNORED |
| `jobs.md` | 12 | COVERED-PROVEN | 193 | same two | GITIGNORED |
| `jobs.md` | 13 | COVERED-PROVEN | 194 | same two | GITIGNORED |
| `jobs.md` | 14 | COVERED-PROVEN | 195 | same two | GITIGNORED |
| **`jobs.md`** | **15** | COVERED-PROVEN | 196 | `_audit/_scratch/_probe-small-measures-live.txt` | GITIGNORED |
| **`jobs.md`** | **27** | COVERED-PROVEN | 208 | `_audit/_scratch/_for-small-measures-covered-vs-gap.tsv` | GITIGNORED |
| **`jobs.md`** | **151** | COVERED-PROVEN | 422 | `_audit/_scratch/_progress-job-search-params.md` | GITIGNORED |
| **`network.md`** | **136** | MEASURED-ABSENT | 458 | `_audit/_scratch/_progress-analytics-creator.md`, `_audit/_scratch/_live-analytics-controls-4.txt` | GITIGNORED |

**Five of the nine are the five the previous wave found by hand. Four are new**
-- `jobs.md` rows 15, 27 and 151, and `network.md` row 136. None was reachable
from the five-under-banked wave's starting point: that wave was routed to its
five by a control census, and rows 27 and 151 were not in a banked state at all
until a sibling wave banked them hours later, in the window this wave ran.

`network.md` row 136 is the sharper of the two: **it is MEASURED-ABSENT**, a
state that claims a live reading showed LinkedIn draws nothing, and both
artifacts behind that reading are in `_audit/_scratch/`.

**ALL 15 UNREACHABLE ARTIFACTS ARE `_audit/_scratch/` PATHS**, quarantined by
`.gitignore:156`. Not one absolute local path, not one session-local capture
outside `_scratch`, not one citation of a file that never existed. The class is
narrower than the brief's list allowed for, and that is the finding: **there is
one hole, not five, and it has a name.**

### Where I DISAGREE with the wave that found the five, narrowly

`_audit/2026-09-20-the-five-under-banked.md` writes that for rows 9 and 11-14
*"the entire evidence chain ends outside the repository"*. Measured at artifact
granularity that is not so: **each of those five also cites four TRACKED
artifacts**, and the strict count of banked rows with no reachable artifact at
all is **0**.

That does not make the earlier wave wrong; it makes the two statements about
different things. Its claim is about the chain behind **the numbers** -- the
drift floor, the id movements -- and those really do terminate in `_scratch`.
Mine is about every artifact the cell names. **This instrument cannot bind a
claim to the artifact that backs it**, so it cannot confirm the narrower
statement, and it does not contradict it. Stated because "0 rows with no
reachable evidence" would otherwise read as a refutation, and it is not one.

### The 24 rows describing a run with no tracked script

Weaker evidence, reported separately and not counted in the 9. These cells say
a live reading was taken -- *loads*, *one session*, *fired live*, *measured
live* -- and name no tracked script that could take it again.

    jobs.md          59, 123, 127
    messaging-and-content.md   M1, M44, C60, C74
    network.md       44, 52, 101, 135, 136, 155, 173, 181
    profile.md       A2, A5, A7, A10, A12, A16, A18, A20, G7

**THIS ONE IS SOFT AND I AM SAYING SO.** The vocabulary is a heuristic; a row
can describe a reading taken through an MCP tool call, which is re-runnable
without any script in `scripts/`. It is offered as a second, separate number for
the ruling, not folded into the 9.

### The instrument, and the vacuous pass it cannot have

`scripts/check_banked_evidence_is_reachable.py`. The brief named the exact
hazard: `sweep_blobs_for_identity.py --help` took `--help` as a git range, swept
0 blobs and printed **"PASS: 0 hits across 0 blobs"**. A garbage argument
produced a green from a safety tool. Every denominator here is a refusal point:

| condition | exit |
|---|---|
| a named census slice is missing | 2 |
| a slice parses to zero table rows | 2 |
| zero rows in a banked state anywhere | 2 |
| zero evidence artifacts across all banked rows | 2 |
| an argument that is not a known slice | 2, naming it |
| `--help` / `-h` | usage, 0 |

and a PASS is only printed when all of those are non-zero, with the
denominators above it on every run.

### FOUR DEFECTS THIS INSTRUMENT FOUND IN ITSELF, ALL BY MEASURING

**1. A LINKEDIN ROUTE IS NOT A PATH, and the failure was loud by luck.** These
slices are full of `/jobs/collections/recommended/` and `/in/me/details/skills/`.
The first extractor admitted them; the first run died inside `git check-ignore`
on a token cleaned down to `/`. **That was the good outcome.** Had
`check-ignore` merely shrugged, every route would have been classified ABSENT,
the instrument would have reported hundreds of unreachable artifacts, and the
real seven would have been invisible inside the noise.

**2. FOUR BANKED ROWS WERE BEING DROPPED BY A STATE SPELLING.** The corpus
writes `**CP 2026-09-19**`, `**COVERED-PROVEN 2026-09-05**` and
`MEASURED-ABSENT `SKILL``. A matcher comparing the whole cell read them as
unknown states. **They were visible only because this file PRINTS every state
spelling it does not recognise** instead of silently treating it as not-banked
-- a refusal that names only what it did not match is half a measurement, and
here the other half was four rows of the answer.

**3. A STALE STATE COLUMN, AND 121 ROWS SKIPPED ON WIDTH.** Finding the state
column by header index carries that index into the NEXT table: `network.md`'s
summary table (`| family | rows | read/write | reversible | shape |`) was read as
five rows with a state of `REV`. And requiring a row's cell count to match its
header's silently discarded 121 rows across four slices, some of them malformed
capability rows. The state cell is now found **by value**, with the header as
the tiebreak and multiple candidates reported rather than guessed at. Ten
state-legend rows (`| COVERED-PROVEN | 21 | 14.0% | 21 |`) were inflating the
denominator and are now excluded and counted.

**4. A WINDOWS LINE-ENDING TURNED EVERY GITIGNORED ARTIFACT INTO "ABSENT".**
`git check-ignore --stdin` was fed newline-separated paths through a `text=True`
pipe, which translates `\n` to `\r\n`. Git took the `\r` as part of the path and
echoed it back C-quoted:

    {'"_audit/_scratch/_progress-job-search-params.md\\r"'}

Non-empty set, exit code 0, nothing to notice, and every membership test missed.
All 13 gitignored artifacts were classified ABSENT. **The headline count did not
move, because both are findings -- the CLASS was wrong on all 13, and the class
is the difference between "deliberately excluded" and "was never there".** Found
by probing one known-ignored path, not by reading the code. Now NUL-separated
and pinned.

---

## THE LEAD'S RULING, VERIFIED BEFORE OBEYED -- AND IT IS REFUTED ON ITS CENTRAL CLAIM

`_TEAM_LEAD_THE_22_ARE_THE_22.md` reached this worktree mid-wave. It reports 22
commits on eight local-only branches whose subjects appear nowhere in master's
log, lists them, and states: *"Your brief handed you 22 distinct SHAs across 29
citations in 19 documents. **These are the same 22.**"* It then derives an
instruction: *"the honest repair for most of these is not 'find the equivalent
hash' -- it is to say the work landed by a different route."*

**The two sets are disjoint. Intersection: 0.** Measured by full SHA, not by
abbreviation, so two spellings of one commit could not read as two commits.

Run against the ruling's own test -- does each commit's subject appear on
`master`? -- the two populations separate perfectly:

| population | subject present on master | absent |
|---|---:|---:|
| the ruling's 22 | **0 of 22** | 22 |
| the 22 cited in the corpus | **22 of 22** | 0 |

**Controls:** `master`'s own subject counted on `master` returns 1; a subject no
commit has returns 0.

The ruling's 22 are the commits that genuinely never landed. The corpus's 22 all
landed. **Both sets number 22, and that coincidence is the whole trap** -- it is
the same shape as the census at `_audit/2026-09-20-the-chain-verification.md`:
a correct measurement of the wrong population, which would have "corrected" six
correct rows had it been relayed rather than checked.

The cross-check the ruling offers is where the conflation entered: `5581950`,
`86b8ed5`, `fa5a314`, `f85e959`, `0f711c1` and `76caeb6` do appear in the
dangling tables of `2026-09-20-the-six-unremapped.md` and
`2026-09-19-four-defects-fixed.md`. **Those are the six-unremapped population, a
third set** -- `_audit/2026-09-20-the-sixty-dangling.md` names `5581950` as *"one
of the SIX that `2026-09-20-the-six-unremapped.md` repaired"*. So the overlap is
real; it is just not with the 22 in my brief.

**WHAT DOES NOT CHANGE.** Everything else in that ruling holds and was obeyed:
nothing was pushed, no local-only branch was published or proposed for
publishing, and `96e90f3` was merged forward before freezing (and `724d327`
after it). **Its warning is also correct as a principle** -- a citation repaired
to a hash carrying different text is worse than an annotated one -- and the
`patch-id` check is exactly what discharges it, which is why that check is in
the table rather than a subject match alone.

**WHAT THE LEAD SHOULD DO WITH THIS.** The ruling's 22 are a real and unrepaired
population, with a real instruction attached that is right for them and wrong
for mine. They need the `NEVER-LANDED` annotation, which
`check_cited_shas_resolve.py` now accepts as a declared no-twin confidence value
-- so the machinery exists, aimed at the other 22, and the work is somebody's.

---

## THE THIRD JOB: THE SWEEP'S VACUOUS PASS, AND A RULING I HAD TO MAKE AGAINST MYSELF

`scripts/sweep_blobs_for_identity.py --help` took `--help` as a git range,
swept 0 blobs and printed **"PASS: 0 hits across 0 blobs"**. Root cause: `_git`
returned `out.stdout` and discarded `returncode` and `stderr`, so a failed
`rev-list` produced an empty commit list and the tool fell into its `PASS:`
branch. The module already had a "MUTE CHECK" for an empty NEEDLE set and none
for an empty CORPUS; that asymmetry was the bug.

**WHAT SHIPPED, STATED FIRST BECAUSE THE RULING WENT ROUND TWICE:**

| case | exit | line |
|---|---:|---|
| range git cannot resolve | **2** | `REFUSING TO SWEEP:` naming the range and git's stderr |
| range resolves, 0 commits | **2** | `REFUSING TO SWEEP:` saying the range RESOLVED and was empty |
| commits > 0, 0 blobs after exemptions | **2** | same, naming the commit count |
| commits > 0, blobs > 0 | 0 / 1 | unchanged |

No refusal line begins with `PASS` or `FAIL`.

**AND IT WENT ROUND TWICE BECAUSE I ACCEPTED A NORMATIVE CLAIM ON THE STRENGTH
OF A MEASURED FACT ATTACHED TO IT.** The brief specified exit 2 for a resolvable
but empty range. A lead note said the opposite -- a legitimately empty range
must keep passing -- and offered `origin/master..HEAD`, which is
`purge_denied_term.py`'s real invocation and really did resolve to 0 commits at
that moment. **I checked the fact, found it true, and let it carry the claim.
They are separable and I did not separate them.** I withdrew the clause and
ruled exit 0; the slice built and tested it in full; the note was then corrected
by its own author, and the slice paused a second time rather than guess.

**THE ARGUMENT THAT SETTLES IT, and neither of us had it at the time:**

> **AN EMPTY RESULT IS AMBIGUOUS BETWEEN "THERE IS GENUINELY NOTHING TO CHECK"
> AND "I WAS POINTED AT THE WRONG HISTORY", AND THE TOOL CANNOT TELL THEM
> APART.** A misconfigured upstream, a detached HEAD, a typo'd ref that happens
> to resolve, a fresh clone with no `origin/master` -- each yields zero commits
> while unpushed work exists outside the measured range. A safety tool may not
> resolve that ambiguity in the reassuring direction.

So the emptiness does not prove the repository is synced; it proves the RANGE is
empty, and those are different claims. My "don't hard-fail the healthy case"
was answered by the asymmetry: exit 2 on a genuinely synced repo costs one line
the caller already explains, because it prints `commits in range: 0` beside the
verdict. PASS on a wrongly-aimed range authorises a push on a check that
inspected nothing -- the original `--help` bug with a different cause and the
same lie.

**THE INVARIANT:** *the verdict line may never imply a sweep that did not
happen, and a denominator of zero must appear in the line that reports it.*

**AND THE NON-`PASS`/`FAIL` PREFIX IS LOAD-BEARING TWICE OVER.**
`purge_denied_term.py` renders a non-matching line as `(no verdict)`, which
blocks the push under its own *"both sweeps must read PASS before pushing"*
rule. It must NOT be spelled `FAIL`, because that script's closing line is
*"If either FAILs, run: `git reset --hard <tag>`"* -- **FAIL there names a
DESTRUCTIVE remedy.** A refusal meaning "I could not establish anything" may
not be spelled as the word that tells an operator to hard-reset.

### THE REJECTED THIRD OPTION, RECORDED WITH ITS ARGUMENT

The intermediate build was not either of the two positions being argued. It
exited 0 but emitted **tagged** verdicts -- `PASS (NOTHING IN RANGE)` and
`PASS (NOTHING SWEPT)` -- and never the bare `PASS: 0 hits across 0 blobs`.
That is a considered answer to the real problem and it is rejected on a fact
rather than on preference. `purge_denied_term.py` selects the verdict with

    l.startswith(("PASS", "FAIL"))

**so `PASS (NOTHING IN RANGE)` starts with `PASS` and the tag is invisible to
the machine that consumes it.** The script's own rule -- *"Both sweeps must
read PASS before pushing"* -- is machine-shaped language a human applies by
scanning for a word, and a tag that informs the reader while doing none of the
check's work is this corpus's recurring defect wearing a helpful face. **It is
the fifth appearance of that shape today and the first one I wrote myself**,
after reading the selector line in the slice's own report.

The asymmetry finishes it. Build 1 wrong costs a moment's confusion in a rare
no-op, and the caller prints `commits in range: 0` beside the verdict so the
reader sees why. Build 2 wrong authorises a push that puts a real person's
identifier in a public repository -- which this project has already established
is not undoable: a force-push leaves retained objects resolvable by SHA, and
only delete-and-recreate removed them, at the cost of this account's PR history.
**FAIL-CLOSED BEATS FAIL-INFORMATIVE WHEN THE MISS IS IRREVERSIBLE.**

The tagged form is kept on the record because it IS the right treatment for a
NON-empty sweep that wants to state what it covered. It is wrong only where a
machine reads the first word.

Two things from that slice survive both reversals and are worth keeping. Its
static control for "no code path prints the bare sentence" first text-searched
the whole file and hit the docstring's own explanation of the invariant, then
searched past the docstring and hit two comments that also have to name the
sentence to explain it -- **the same prose-about-a-mechanism shape, for the
fifth time today.** It landed on walking the AST for string-literal CONSTANT
nodes and excluding docstrings by node identity; comments are not AST nodes, so
they fall out for free. **That is the only version of that check that does not
convict its own explanation.** And its live-caller test reads
`origin/master..HEAD`'s real state and asserts whichever branch that implies --
which earned itself immediately, because the range went from 0 commits to 1
while the ruling was being argued.

**THE PROCESS NOTE, because it is the transferable part.** The slice was told
one thing by its brief, the opposite by a note on disk, and then the opposite
again. **It paused both times and built neither on its own judgement.** Had it
silently picked either way, nobody would have found that the first note was
wrong -- and it was the pause, not the code, that produced the argument above.

## HONEST LEDGER

**WHAT I DID NOT SETTLE.**

1. **Half B's 24 "no re-runnable script" rows are a heuristic**, not a
   measurement, and I have not separated the rows whose reading came through an
   MCP tool call from those whose method is genuinely gone. Handed up as its own
   number, deliberately not folded into the 9.
2. **The instrument binds a row to its ARTIFACTS, never a claim to the artifact
   that backs it.** So it cannot confirm the narrower statement that the numbers
   in rows 9 and 11-14 have no reachable backing, and it does not contradict it.
3. **Recall is unmeasured.** I know what the extractor selects; I do not know
   how many evidence artifacts are cited in a form none of its rules admit. The
   `AMBIGUOUS` count is 0 today, which is consistent with a clean corpus and
   equally consistent with an extractor that is too narrow to be ambiguous.
4. **I did not repair Half B.** Committing a `_scratch` artifact is a decision
   about what belongs in a public repository and it is not mine; demotion is a
   ruling and it is not mine either. The measurement is above.
5. **I did not verify the lead's list of eight local-only branches**, only that
   its 22 commits exist, that their subjects are absent from `master`, and that
   they are disjoint from mine. I did not enumerate branches or inspect blobs on
   them, and I did not push, fetch or modify any ref.
6. **The 5 unmarked citation sites depend on a reader reaching the note or the
   table.** A reader who lands on `groups-admission.md:413` from another
   document's line citation still meets a bare `744a1f4` in a transcript. The
   mapping table covers it for the guard; it does not put the twin in front of
   that particular reader, and I chose the transcript's integrity over that.
7. **Three reds arrived from a guard I had not run before committing.**
   `test_a_correction_is_findable_from_the_claim.py` refused the full impact
   gate on this document: one `CORRECTS:` marker whose reason ran onto the next
   line and so read as absent, a missing `CORRECTED BY:` back-pointer in each
   corrected document, and two untriaged candidate pairs. All four are fixed in
   the follow-up commit. **The corrected documents now lead a reader here**,
   which is the property that rule exists for: a corrector can name what it
   corrects, and the corrected document cannot name its corrector unless
   somebody writes it in.

**WHAT CHANGED IN THE TREE.**

    _audit/  x19                                repaired: note + table (+21 markers)
    _audit/2026-09-20-the-evidence-that-resolves.md   this document
    _audit/INSTRUMENTS.md                       section 40
    scripts/_repair_branch_only_citations.py    NEW -- the repair receipt, idempotent
    scripts/check_cited_shas_resolve.py         remap rows now verified; empty-corpus gate
    scripts/check_banked_evidence_is_reachable.py  NEW -- the Half B instrument
    scripts/sweep_blobs_for_identity.py         the vacuous pass, fixed
    tests/test_a_cited_sha_resolves.py          pin 26 -> 0; 9 new controls
    tests/test_banked_evidence_is_reachable.py  NEW -- 28 controls and the pin of 7
    tests/test_sweep_blobs_refuses_a_vacuous_pass.py  NEW

**CORRECTS:** `_audit/2026-09-20-the-sixty-dangling.md` section 6 -- it records
the 22 as NOT REPAIRED and pinned, with the pin standing at 26 (token, document)
rows. All 22 are repaired as of this document and `PINNED` is now empty; the
section's reasoning for deferring (nineteen documents, three waves live) was
correct at the time and those waves have since merged.

**CORRECTS:** `_audit/2026-09-20-the-five-under-banked.md` section 8 -- its "the ENTIRE evidence chain ends outside the repository" is narrower than it reads.
Its words are *"for rows 9, 11, 12, 13 and 14 the entire evidence chain ends
outside the repository"*. Measured at artifact granularity those five rows each also cite
four TRACKED artifacts, and the corpus-wide count of banked rows with NO
reachable artifact is 0. The narrower claim -- that the chain behind the
NUMBERS terminates in `_audit/_scratch/` -- is not contradicted and is not
checkable by this instrument.

## Dead hashes, recovered

Added 2026-09-20, by this document about itself. It quotes one in-line repair
marker verbatim in order to explain the marker's shape, and that quote is a
real citation of a branch-only hash. The marker is not a suppressor by design,
so quoting it clears nothing -- it adds a citation, and this is the answer.
The live column below was verified by `broken_remaps()` on the same run that
convicted the quote.

| dead hash | subject (the durable reference) | live hash | confidence |
|---|---|---|---|
| `c4d2be2` | census(blockers): two of the four contradictions resolve, and two genuinely do not | `5073827` | CONFIRMED |
