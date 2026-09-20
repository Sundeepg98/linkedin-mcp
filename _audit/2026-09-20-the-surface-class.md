# The SURFACE? class, adjudicated

The brief: `SURFACE?` covers "roughly 22 blockers, 139 rows, 108 still GAP",
has been NAMED and never ADJUDICATED, and is the largest block of census rows
whose disposition nobody has ruled. For each blocker, one question: is the row
blocked by a fact about the SURFACE (LinkedIn does not draw this thing, does
not serve this address) or by a fact about US (nobody built the reader, nobody
captured the page)?

Measured offline against committed evidence. There is no live LinkedIn session
in this environment -- the `linkedin` MCP server failed to connect at session
start -- so nothing below rests on a page load, and every number is re-derivable
from the repository by running the commands named.

Worktree cut from `8b58dcb`. All counts stamped 2026-09-20.

---

## 0. THE HEADLINE, IN FOUR LINES

1. **The class as published cannot be enumerated.** Its classifier was never
   committed and its inputs are gitignored and gone. 186,629,988,917,605
   distinct 22-blocker subsets fit its three published integers.
2. **Re-derived under a committed rule:** 26 blockers, 167 rows, 140 still GAP
   (25 / 164 / 137 if you exclude the one the source document filed elsewhere).
3. **Zero of the 26 are blocked by a surface fact.** Every one carries a
   boundary cell naming an artifact of THIS repository -- an allowlist entry, a
   denylist exemption, or a WriteSpec. The class name asserts the opposite of
   what its own ledger says.
4. **Rows banked out of GAP: 0.** Nothing here moves a row, and the reason is
   in section 6. Rows inflated: 0.

---

## 1. THE COUNT, DERIVED

Not copied. `scripts/build_blocker_map.py --write` regenerates
`_audit/_census/blocker-map.tsv` from the census; re-running it in this
worktree rewrote the file **byte-identically** (`git status` clean), so the
committed map is current rather than assumed current.

    frozen GAP rows at 1c08e5f     409
    ledger blockers parsed          97   rows 409
    rows still GAP today           301   (+1 entered since freeze: P L2b)
    today's GAP total, derived     302

Cross-checked against the shipped counter, `scripts/count_census_states.py`,
run as a separate process: `GAP 302` over 704 stated rows. Two instruments,
one integer.

### 1.1 The membership rule

`scripts/classify_surface_blockers.py` (new; section 5) selects every blocker
whose NAME contains `SURFACE`. Syntactic and total -- nothing hand-picked,
nothing hand-dropped, because a judgement is what produced an unreproducible
class the first time.

| rule | blockers | rows | GAP today |
|---|---:|---:|---:|
| name contains `SURFACE` | **26** | **167** | **140** |
| the same, minus `PREMIUM-JOBS-SURFACES` (the source document filed it under ACCOUNT, and four sibling agents hold it) | **25** | **164** | **137** |

Both numbers are published because the brief's "roughly 22 / 139 / 108" matches
neither, and which one you want depends on whether you honour the source
document's own ACCOUNT placement. **Neither is the published class** -- see 1.2.

---

## 2. THE PUBLISHED CLASS IS NOT A SET, AND CANNOT BE MADE ONE

`_audit/2026-09-20-the-contingent-writeoffs.md` s3.1 publishes:

| subject the name asserts | blockers | rows | still GAP |
|---|---:|---:|---:|
| **SURFACE?** -- a surface whose existence FOR HIM is contingent | 22 | 139 | 108 |

**Its other three classes reproduce exactly.** That document prints OPERATOR,
ACCOUNT and WORLD as explicit blocker lists; summing those names against the
live map gives `(1, 15, 14)`, `(7, 19, 14)` and `(18, 45, 18)` -- identical to
its table, all three. So the map has not drifted and the arithmetic is sound.

**SURFACE? and CODE are the two it never listed.** They are the residue: 69
blockers, 330 rows, 255 GAP, split 22/47 by a classifier that
* was **never committed** (`git log -S` finds it nowhere), and
* read three inputs -- `_audit/_scratch/_contingent-ledger-sweep.tsv` and two
  siblings -- which are **gitignored by design and are no longer on disk**.

So membership is recoverable only from the three published integers. It is not:

    22-blocker subsets of the 69-blocker pool
    totalling exactly 139 rows and 108 GAP:   186,629,988,917,605

**This is the defect `build_blocker_map.py` was built to end, one level up.**
That file's own docstring indicts the 2026-09-03 ledger for publishing a
division as counts with the classifier uncommitted, so "nobody could tell a
RE-COST from a MISCOUNT". The sweep that indicted it then did the same thing.
The source document is honest about this in its limits, s7.6 -- *"the SURFACE?
class of 22 is a guess about names, not a measurement of reasons"* -- but the
three integers are what later readers quote, and a limits section is not
reachable from a number.

**Handed over as a census defect, not fixed here:** any future by-subject
classification must ship its classifier in `scripts/`, as this wave's does.

---

## 3. THE ADJUDICATION, AND THE COLUMN IT TURNS ON

The class name asserts a fact about LinkedIn. The ledger's own per-blocker
`boundary` cell asserts what would have to be BUILT. Its legend, in
`_audit/2026-09-03-linkedin-gap-blockers.md` under the cost legend:

    D  boundary LISTS needing an exemption or edit -- one per list, not per entry
    T  tools written or edited
    W  a new WriteSpec + gate + consent text, costed 3, once per blocker
    R  an operator ruling

`D` and `W` are artifacts of THIS repository. And the column carries an
explicit non-staleness warrant, added to the ledger head by
`_audit/2026-09-20-the-decides.md`:

> the ROW COUNTS in the ranking tables below are freeze figures from 2026-09-03
> and have not been maintained ... **the COST and boundary columns here are
> properties of the work and do not go stale.**

So this wave re-derives every row count live and reads the boundary cell as
published, each on the warrant that document gives it. That is the opposite of
the trap in this corpus -- taking a table as data rather than as a claim.

### 3.1 The measurement

    REASON CLASS over the 26 selected blockers
      ADDRESSABILITY-OURS     23 blockers   159 rows   134 GAP
      WRITER-OURS              3 blockers     8 rows     6 GAP

    SURFACE-named blockers whose boundary cell asserts a SURFACE fact: 0
        none -- every selected blocker's boundary cell names an artifact of
        THIS repo (an allowlist entry, a denylist exemption, or a WriteSpec)

**23 of 26 are refused by our own URL boundary. 3 of 26 are already addressable
and lack only a write contract. None of the 26 is recorded as a page LinkedIn
does not draw.**

### 3.2 The control, because a tally without a denominator is not a measurement

Same classifier over the 68 blockers the rule did NOT select:

    NONE-STATED             43 blockers
    ADDRESSABILITY-OURS     13 blockers
    WRITER-OURS             12 blockers

**63% of the unselected blockers need no boundary change at all; 0% of the
selected ones are in that position.** The rule selects something real. Had the
two tallies looked alike, the finding would have been an artifact of how the
ledger costs everything, and this section is what would have shown it.

### 3.3 What this does NOT license

A boundary cell proves the ledger **costed a build against the address**. That
is evidence about how the row was filed. **It is not a measurement that
LinkedIn draws the surface**, and no such measurement is claimed here for any
of the 26.

The inverse error is already recorded in this repo as a standing trap,
`_audit/INSTRUMENTS.md` s9.1: **ALLOWED IS NOT SERVED** -- `/in/me/details/
interests/` is on the allowlist, was admitted for a blocker's precondition, and
REDIRECTS. This wave is careful about its converse, **REFUSED IS NOT ABSENT**:
a probe that runs candidate URLs through `readonly.assert_read_url` and reports
them dead has measured OUR GATE, not LinkedIn. Both directions were briefed to
the evidence sweep in section 4 for exactly this reason.

### 3.4 THE LEDGER'S BOUNDARY CLAIM IS STALE, AND IT CARRIES A WARRANT SAYING IT CANNOT BE

The ledger head states, added 2026-09-20:

> the COST and boundary columns here are **properties of the work and do not go
> stale**.

**That warrant is false for the boundary column, and it is falsifiable by
running one line.** A cell reading `allowlist +1` bills a pattern that is still
owed. The live boundary is `linkedin_server.readonly._ALLOWED_URL_PATTERNS`,
**35 patterns at this commit**. Putting each blocker's base address through the
shipped `readonly.is_read_url`:

    base address ALREADY ALLOWED while the ledger still bills an
    allowlist entry:                                      16 of 26

    ARTICLE-SURFACE             /article/new/                       ALLOWED
    BADGES-SURFACE              /in/me/                             ALLOWED
    COMPANY-PAGE-SURFACE        /company/example/                   ALLOWED
    CONTENT-ANALYTICS-SURFACE   /analytics/creator/content/         ALLOWED
    CREATOR-HUB-SURFACE         /analytics/creator/content/         ALLOWED
    EVENTS-SURFACE              /events/                            ALLOWED
    GROUPS-SURFACE              /groups/                            ALLOWED
    INMAIL-COMPOSE-SURFACE      /messaging/compose/                 ALLOWED
    JOB-ALERTS-SURFACE          /jobs/alerts/                       ALLOWED
    JOB-COLLECTIONS-SURFACE     /jobs/collections/recommended/      ALLOWED
    MESSAGE-REQUESTS-SURFACE    /messaging/                         ALLOWED
    NEWSLETTER-SURFACE          /mynetwork/network-manager/newsletters/  ALLOWED
    POST-DRAFT-SURFACE          /preload/sharebox/                  ALLOWED
    PREMIUM-JOBS-SURFACES       /premium/my-premium/                ALLOWED
    SCHOOL-PAGE-SURFACE         /school/example/                    ALLOWED
    SEARCH-APPEARANCES-SURFACE  /analytics/search-appearances/      ALLOWED

**And what is still refused, printed because a refusal that names only its
misses is half a measurement:**

    RECOMMENDATIONS-SURFACE     /in/me/details/recommendations/     refused
    RESUME-TOOLS-SURFACE        /resume-builder/                    refused
    SAVED-POSTS-SURFACE         /my-items/saved-posts/              refused
    SEARCH-HISTORY-SURFACE      /search/history/                    refused
    SEARCH-RESULTS-SURFACE      /search/results/people/?keywords=   refused
    SERVICES-PAGE-SURFACE       /services/page/                     refused
    SKILL-PAGE-SURFACE          /skill/example/                     refused

The address table is a stated CLAIM, not a derivation -- it is written out in
`SURFACE_ADDRESSES` in the classifier precisely so it can be argued with, and
every address is printed beside its verdict on every run. Slugs are the literal
word `example`; no real company, school or member token is in a tracked file.

**WHAT THIS BOUNDS, exactly.** It says the blocker's BASE page can be reached
through the sanctioned path with no boundary edit. It does NOT say every row's
specific target is allowed -- `GROUPS-SURFACE` is billed `allowlist +2` and a
group's deeper pages may well be among the refused. And it emphatically does
not say the page renders anything: **ALLOWED IS NOT SERVED**, and
`/in/me/details/interests/` is the standing counter-example -- on the allowlist,
admitted for a blocker's precondition, and it REDIRECTS.

### 3.5 WHY THE CLASS STAYED UNADJUDICATED FOR SEVENTEEN DAYS

The capture path runs through the same gate the blocker is about.
`scripts/_capture_toggle_states.py` states it in its own docstring:

> Every navigation goes through ``readonly.assert_read_url`` and the rate
> limiter, **exactly as a tool does**; nothing here clicks anything.

So for any blocker whose address the gate refuses, **the measurement that would
settle whether LinkedIn draws the surface is itself gated behind the change the
blocker is filed as needing.** You cannot look until you have already paid. The
same script shows the constraint steering what gets measured -- it picks one of
its five targets because it needs "no new surface and no new allowlist entry".

That is the structural reason this class sat unmeasured, and it is a far better
explanation than any per-blocker guess. **It also means the deadlock is already
broken for 16 of the 26 and nobody noticed**, because the allowlist grew while
the ledger's cost column did not.

---

## 4. PER-BLOCKER RULINGS

(Section 4 is filled from the evidence sweep; see 4.0 for method.)

### 4.0 Method

Three read-only sweeps over the 26, briefed to separate EXISTENCE (does
LinkedIn render it), ADDRESSABILITY (does our boundary allow it) and READER
(does a parser exist), to quote rather than paraphrase, and to report what a
capture DID contain rather than only what it lacked. Prior art was required to
be searched before any new evidence was generated, via the shipped locator
`scripts/find_blocker_reason.py`.

---

## 5. THE INSTRUMENT, AND ITS FAILING-STATE RECEIPT

`scripts/classify_surface_blockers.py` -- derives the class membership and each
blocker's reason class from committed sources. It exists because the thing it
replaces was a set of integers with no classifier behind them.

**It is shipped SHOWN FAILING.** Five planted defects, each applied to a COPY
of the ledger in the scratchpad with the module's `LEDGER`/`MAP` constants
repointed, so nothing tracked was touched:

    CONTROL  untouched ledger + map                        rc=0  GREEN
    CASE 1   ranked table header removed                   rc=1  RED
             FAIL: the ranked table header is no longer present ...
             (+26 consequent FAILs, one per selected blocker)
    CASE 2   cost-0 table header removed                   rc=1  RED
    CASE 3   one ranked row deleted (97/409 stops closing)  rc=1  RED
    CASE 4   map carries a SURFACE blocker absent from
             both ledger tables                            rc=1  RED
             FAIL: PHANTOM-SURFACE is in the map but in NEITHER ledger table
    CASE 5   MUTATION: a boundary cell made a genuine
             surface fact                                  rc=0, count 0 -> 1
             SURFACE-FACT  1 blockers  21 rows  21 GAP
             SEARCH-RESULTS-SURFACE boundary='LinkedIn draws no such page'

**Case 5 is the one that matters and it is why the other four are not enough.**
The headline of this document is a ZERO. A zero produced by a branch that
cannot fire certifies nothing -- this repo has shipped five such checks and
found each one later, expensively. Case 5 plants a boundary cell that IS a
surface fact and requires the classifier to name it; the count moves 0 -> 1 and
the blocker is printed. The zero in 3.1 is therefore a reading, not a default.

Cases 1 and 2 reproduce a defect this corpus has already paid for: on
2026-09-05 nineteen appended lines slid both ledger tables 28 lines down and
four blockers silently read as published 0. Both tables here are located by
HEADER ROW, never by offset, and a missing header is a loud failure.

### 5.1 Two bugs in the red-proof itself, recorded because the pattern is the finding

The harness was wrong twice before it was right, and the classifier was correct
both times:

1. Case 5 built the planted ledger and **never passed it** -- the case ran on
   clean input and reported `*** DEAD BRANCH`. A red-proof that silently tests
   the wrong input manufactures exactly the false alarm it exists to prevent.
2. The fixed harness then asserted on `"surface fact: 1"` while the program
   prints `"SURFACE fact: 1"`. Case-sensitive string matching against a
   program's prose: the assertion failed on a report that was correct.

Every fresh instrument built in a session has had a bug on its first attempt in
this project's history. Two of the three defects found in this wave's own
tooling were in the checker, not the checked.

---

## 6. THE LEDGER

| | |
|---|---:|
| rows banked OUT of GAP | **0** |
| rows inflated | **0** |
| rows re-attributed | **0** (see below) |
| blockers adjudicated | see s4 |
| census defects handed over | s2, s7 |

**Why zero rows moved, stated plainly.** Nothing in section 3 is a measurement
that a surface is absent, so nothing there can carry a row to
`MEASURED-ABSENT` or `EXCLUDED-RULED`. The finding is that the rows are
mis-CLASSED, not that they are mis-STATED: they are correctly GAP, and their
blockers already name -- in the ledger's own boundary column -- what is
missing. Re-attributing them to differently-named blockers would move 137 rows
between labels while changing no fact, and `blocker-map.tsv` is derived from
evidence lines rather than from rulings, so such a move would have to be
manufactured as evidence. That is the ratchet this corpus has been bitten by
before.

---

## 7. WHAT THIS WAVE COULD NOT RULE, AND THE EXACT COST OF RULING IT

(Filled from the evidence sweep.)
