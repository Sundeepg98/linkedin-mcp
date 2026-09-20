# The SURFACE? class, adjudicated

**CORRECTS:** `_audit/2026-09-20-the-decides.md` -- the warrant it wrote into the ledger head, *"the COST and boundary columns here are properties of the work and do not go stale"*, is FALSE for the boundary column. That column bills an `allowlist +N` for a pattern still owed, and the allowlist has grown since 2026-09-03: **15 of the 25 undisputed SURFACE-named blockers have their base address ALREADY ALLOWED** by the live 35-pattern boundary while the cell still bills the entry. The COST half of the claim is untouched here; only the boundary half falls. Detail and the per-blocker table in section 3.4.

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its ranked table boundary column is stale in the same 15 cells, which is where a reader meets the claim. Section 3.4.

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
   what its own ledger says. **Reached three more times independently**, by
   three read-only sweeps over disjoint blocker sets, working from the rows
   rather than from that column (s4.2).
4. **The class was never blocked on LinkedIn; it was blocked on a circularity.**
   The capture path runs through the same gate the blocker is about, and a
   ruling forbids navigating to a refused address even to find out whether it
   should be admitted. **You cannot look until you have already paid** (s3.5).
   For 15 of 25 that deadlock silently broke -- the allowlist grew while the
   ledger's cost column did not (s3.4).
5. **Rows banked out of GAP: 0.** Nothing here moves a row, and the reason is
   in section 6. Rows inflated: 0. 13 blockers are named CANNOT-TELL and
   costed; **six of them are answered by three page loads** (s7.1).

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
    allowlist entry:                                      15 of 25
    (denominator excludes 1 blocker whose address is DISPUTED)

    ARTICLE-SURFACE             /article/new/                       ALLOWED
    BADGES-SURFACE              /in/me/                             ALLOWED
    COMPANY-PAGE-SURFACE        /company/example/                   ALLOWED
    CONTENT-ANALYTICS-SURFACE   /analytics/creator/content/         ALLOWED
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

**And the one the evidence sweep took off the board, which is the part of this
section I got wrong:**

    CREATOR-HUB-SURFACE   /analytics/creator/content/ -> ALLOWED
                          /creator-hub/               -> refused     DISPUTED

My first cut of the address table gave `CREATOR-HUB-SURFACE` the **identical
address as its sibling** `CONTENT-ANALYTICS-SURFACE` -- a duplicate, which is a
guess wearing a measurement's clothes, and it counted a whole blocker into the
"already allowed" tally on the strength of it. The group-B sweep caught it
against `_audit/2026-09-19-what-a-reader-could-actually-close.md`, whose table
"REFUSED BY THE READ BOUNDARY" gives `/creator-hub/` and reports it REFUSED.
**Two addresses, opposite verdicts, no capture either way.** It is now held in
`DISPUTED_ADDRESSES`, printed with both candidates and both verdicts, and
**excluded from the denominator** -- which is why this section says 15 of 25 and
not 16 of 26. A guard requires a disputed entry to carry at least two distinct
addresses, so "disputed" cannot become a quieter way of dropping a blocker out
of a number.

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
broken for 15 of the 25 and nobody noticed**, because the allowlist grew while
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

**A CONTAMINATION I CAUSED AND THEN MEASURED.** My own three artifacts landed
in the shared tree at `9d15c11`, AFTER the sweeps were briefed, and all three
name all 26 blockers -- so the raw grep in their briefs began hitting this
wave's own output. Measured rather than assumed: the shipped locator is NOT
affected (this document appears as a candidate for **0 of the 26**, because it
scans `_audit/` only and scores a line only when it carries an argument word;
`SKILL-PAGE-SURFACE` still reports ORPHANED after my commit). Only the raw grep
needed the exclusion, which was issued as a disk ruling.

**The contamination was real and it landed.** One sweep verified the exclusion
empirically against its own already-completed grep set rather than taking it on
my word, and found none of the three present. **Another had already cited them
as corroborating ADDRESSABILITY evidence in 6 of its 10 sections**, removed all
six and rewrote around them. **No verdict moved**, because every surviving
addressability conclusion rested on that sweep's own direct
`readonly.is_read_url()` calls against production code plus documents from
2026-08-22 to 2026-09-19. Where one of my artifacts had been the only source
for a candidate address, the section now says plainly that no address is on
record in the included corpus rather than citing my guess -- which is the
better answer and was produced by removing mine.

**A citation of this wave's own artifacts is rejected wherever it appears
below.** I am the integrator, so that filter runs here regardless of whether
any message was delivered.

**AND THE FILTER IS ASYMMETRIC, WHICH IS THE POINT.** The third sweep did not
exclude my address table; it cross-checked against it and reported **"6 of 9
corroborate cleanly"** plus one conflict. Those six agreements are **NOT
independent corroboration** -- they are my classifier agreeing with the corpus
my classifier was built from, and they are counted as evidence nowhere in this
document. That is the 35-cell-ceiling failure this campaign has already paid
for once: axes extracted from the samples, so coverage measured the map and
every felt saturation was wrong by construction.

**A CONFLICT with my output is not circular**, because shared provenance cannot
manufacture a disagreement. So the two dissents from that same sweep are kept
and given weight: the `CREATOR-HUB-SURFACE` address conflict, which found a
real bug in my table (s3.4, s5.0), and the `INMAIL-COMPOSE-SURFACE` tension --
`/messaging/compose/` reads ALLOWED, but the census row asks for a surface
**"distinct from the message composer"**, so ALLOWED there may only mean the
ordinary composer the row already rules out is reachable. That one is recorded
unresolved.

### 4.1 Group A -- the six with recent sibling activity

| blocker | rows / GAP | EXISTENCE, as measured | ruling |
|---|---:|---|---|
| `NEWSLETTER-SURFACE` | 12 / 11 | list page **live-loaded 2026-09-05**, capture re-read 2026-09-20 | **US-FACT** for the list rows |
| `GROUPS-SURFACE` | 30 / 21 | root **live-fired 2026-09-05** | **US-FACT**; per-group page CANNOT-TELL |
| `EVENTS-SURFACE` | 17 / 13 | root **live-loaded twice**, cross-instrument agreement | **US-FACT**; per-event page CANNOT-TELL |
| `COMPANY-PAGE-SURFACE` | 16 / 15 | **referenced, never opened** -- 86 hrefs across 22 captures | **US-FACT** for tabs; root render CANNOT-TELL |
| `SERVICES-PAGE-SURFACE` | 11 / 11 | create entry point **live-measured on 5 captures**; the Page itself never captured | **CONTINGENT** -- see 4.1.2 |
| `SEARCH-RESULTS-SURFACE` | 21 / 21 | **never measured**, and the artifacts say why | **CANNOT-TELL**, see 4.1.1 |

**Read the EXISTENCE column, because it is the one the class name is about.**
Four of the six surfaces have been SEEN. None of the six is recorded anywhere as
a page LinkedIn does not draw. **Nothing here supports a MEASURED-ABSENT ruling
for any row, and nothing here is a surface absence.**

#### 4.1.1 `SEARCH-RESULTS-SURFACE` -- 21 rows, and the circularity is the campaign's own words

The largest all-GAP blocker in the class, and the one where the deadlock in s3.5
is stated by the artifacts themselves rather than inferred by me.
`_audit/2026-09-19-search-shaper.md`:

> **NOT CLAIMED:** that this shaper has ever seen a live search page. It has
> not, and the emission question the 2026-09-05 measurement left open (**"the
> evidence path is CIRCULAR: the measurement that would justify opening the
> surface can only be completed by opening it"**) is untouched by this work.

`_audit/2026-09-19-search-admission-preconditions.md` confirms it operationally:
every `/search/` address is refused today, and a ruling **forbids a discovery
probe from navigating to a refused address even to find out whether it should be
admitted**. Independently re-confirmed on disk this wave: no `/search/results/`
pattern exists in `readonly.py`; every such string in the file is inside a
comment. So this blocker is not stale -- it is current, and genuinely shut.

A reader exists (`linkedin_server/search_results.py`) and is **confirmed not
wired to any tool**; its controls ran against synthetic fixtures and a
JavaScript classifier executed under V8, never against a real capture. What the
shaper "knows" about the page is a modelled vocabulary, not a measurement.

**A real defect surfaced by that wave, recorded here because it prices the
fix:** an anchored family wildcard `^https://www\.linkedin\.com/search/.*$`
admits a path-traversal string that normalises onto an account-ending address,
and no forbidden substring catches it. **"Anchored" does not mean "closed".**
Whoever admits the pattern inherits that.

#### 4.1.2 `SERVICES-PAGE-SURFACE` -- the one genuinely contingent blocker, and it is not contingent on LinkedIn

11 rows, all still GAP. The entry point to CREATE a Service Page is rendered on
his profile -- measured across five committed captures, via the `Open to` menu
resolving to exactly three items. He has never used it. `P H11` is the section
that appears once a Service Page EXISTS, and it does not exist.

**So the reason is a fact about the OPERATOR, not about LinkedIn or about us.**
Under the vocabulary of `_audit/2026-09-20-the-contingent-writeoffs.md` s0 this
is **TRUE BUT CHANGEABLE, at the cost of one operator action** -- the same shape
as `ADMIN-RIGHTS-NOT-HELD`, and spelled nowhere in the census.

**CONDITION, named so this does not go stale the way the write-offs did:** the
ruling holds only while he has no Service Page. **REOPENER:** he creates one, or
a capture of `/in/me/` shows a "Providing services" section. **WHO CAN
ESTABLISH IT:** the operator, then a capture.

And the sweep independently caught the staleness of 3.4 from the other
direction: this blocker's `allowlist +1` is **NOT OWED** -- `P H11` renders on
`/in/me/`, which is already open.

### 4.2 Groups B and C -- the remaining nineteen

Group C, ten blockers, reached the class finding independently and said so:

> **Zero of these ten carry a committed claim that LinkedIn does not draw or
> serve the surface.** That matches [the] cross-blocker finding (zero of 26
> SURFACE-named blockers assert a surface fact) exactly, and **I reached it
> independently, per-row, before reading that document's headline number.**

That is the strongest form the finding takes: three sweeps, three disjoint
blocker sets, one conclusion, reached from the rows rather than from the ledger
column I measured. **Across all 26 blockers, not one committed artifact asserts
that LinkedIn fails to draw the surface.**

Group B's own summary of its nine is the same shape, with the sharp edge below:

> Two of nine (`JOB-ALERTS-SURFACE`, `JOB-COLLECTIONS-SURFACE`) have real,
> committed, controlled LIVE reads behind them; the other seven do not. For
> those seven, the ledger's `allowlist +N` / `WriteSpec` boundary tags are
> frequently **HYPOTHESES about what blocks the row** (stated as such in the
> probe scripts themselves), not measurements.

### 4.3 `JOB-ALERTS-SURFACE`, the one measured surface fact in the class -- and it is not an absence

This is the most important single correction to section 3.4 and it comes from
the sweep, not from me. `/jobs/alerts/` is **ALLOWED by our boundary and still
wrong**:

> LinkedIn redirects `/jobs/alerts/` to a different path at the same depth,
> **twice reproducibly, with the control serving correctly at both ends of the
> session**. ... It cannot be changed correctly until somebody names the landed
> spelling.

So a pattern can be **ALLOWED-AND-STILL-WRONG** -- matching nothing LinkedIn
resolves to. A naive `is_read_url` check reports the row addressable when the
one live test on record says the address does not serve. It is the same family
as the standing ALLOWED IS NOT SERVED trap already registered in this repo's
instrument register, sharpened: there the page served and redirected, here the
spelling may resolve to nothing at all. **Section 3.4's "already allowed" is a statement about OUR GATE and
nothing more; this blocker is the in-class proof.**

**And the surface itself is not absent.** The alerts exist -- `readonly.py`'s
own comment says *"the correct response is to CHANGE THIS PATTERN, not to
conclude he has no alerts -- the skill's own inventory says he has five."* The
measured fact is about a SPELLING, not about a capability. Filing it as a
surface absence would be exactly the error this wave exists to catch.

**A defect handed over:** the comment shipping above that pattern in
`readonly.py` still reads *"Nobody has opened this page ... not one byte of it
says LinkedIn serves that spelling"* -- while the 2026-09-05 live redirect
finding already answered it. **The code's own comment is stale in the direction
that sounds careful**, which is the hardest kind to notice.

### 4.4 What the 26 actually divide into

| disposition | blockers | what it means |
|---|---:|---|
| **US-FACT** -- reader, WriteSpec, boundary or ruling missing | 11 | stays GAP; the ledger already names the artifact |
| **CANNOT-TELL** -- nobody captured the page | 13 | stays GAP; costed in s7 |
| **CONTINGENT (operator)** -- `SERVICES-PAGE-SURFACE` | 1 | stays GAP; condition + reopener now named |
| **ADDRESS DISPUTED** -- `CREATOR-HUB-SURFACE` | 1 | stays GAP; two sources, opposite verdicts |
| **MEASURED-ABSENT** -- LinkedIn does not draw it | **0** | -- |

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

### 5.0 The control that came from a bug in this wave's own table

`test_no_two_blockers_share_a_base_address_undeclared`. `SURFACE_ADDRESSES` is
hand-written, so a copy-paste puts one blocker's address on another and the
live-boundary section then reports a verdict for a page that blocker has
nothing to do with. **That is not hypothetical: it happened here**, and an
evidence sweep found it, not me (s3.4).

A shared address is not banned -- `/messaging/` genuinely draws the group-chat
list, the message-request list and the compose toolbar, and `/preload/sharebox/`
serves two more. It must be **DECLARED**, which turns a silent copy-paste into
a statement somebody wrote down. The guard also fails if the declaration
DRIFTS from the table, because a stale declaration is worse than none: it
launders a real duplicate.

**SHOWN FAILING**, by re-inserting the exact bug:

    AssertionError: these base addresses are shared by more than one blocker
    without being declared in DELIBERATE_SHARES, so at least one of them is
    reporting a verdict for a page it does not own:
    {'/analytics/creator/content/': ['CONTENT-ANALYTICS-SURFACE',
                                     'CREATOR-HUB-SURFACE']}

### 5.1 Three bugs in this wave's own tooling, recorded because the pattern is the finding

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
| census state cells edited | **0** |
| blockers adjudicated | **26 of 26** |
| blockers ruled US-FACT | 11 |
| blockers ruled CANNOT-TELL, named and costed | 13 |
| blockers ruled CONTINGENT with a reopener | 1 |
| blockers whose ADDRESS is disputed | 1 |
| blockers ruled MEASURED-ABSENT | **0** |
| census defects handed over | **7** (s8) |
| instruments shipped, shown failing | 1 (s5) |
| defects found in this wave's OWN tooling | 3 (s5.1, s3.4) |

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

**13 of the 26 are CANNOT-TELL-WITHOUT-A-CAPTURE.** That is a real outcome,
not a failure: the question is whether LinkedIn draws a page, and no committed
artifact answers it because nobody has opened the page. Each is named with the
exact address that would settle it.

### 7.1 The two cost classes, and why they differ by a ruling rather than by effort

**CLASS 1 -- address already ALLOWED. Cost: one page load.** No boundary edit,
no ruling. The capture path (`readonly.assert_read_url`) already admits these,
cross-checked against both entry points with 0 disagreements.

    CONTENT-ANALYTICS-SURFACE   /analytics/creator/content/     existence of creator mode
    GROUP-CHAT-SURFACE          /messaging/                     a group thread in the inbox
    MESSAGE-REQUESTS-SURFACE    /messaging/                     a pending request
    PICKER-SURFACES             /messaging/                     the compose toolbar
    INMAIL-COMPOSE-SURFACE      /messaging/compose/             a surface distinct from the composer
    POLL-SURFACE                /preload/sharebox/              the poll control
    POST-DRAFT-SURFACE          /preload/sharebox/              the draft control
    RESUME-TOOLS-SURFACE        /premium/my-premium/            resume builder entry
    COMPANY-PAGE-SURFACE        /company/<slug>/                the root render
    JOB-ALERTS-SURFACE          /jobs/alerts/                   NAME THE REDIRECT TARGET

**A caveat that costs nothing to state and would cost a wave to discover:**
four of those ten are the SAME page. `/messaging/` settles three blockers and
`/preload/sharebox/` settles two. **Six of the ten CANNOT-TELLs in class 1 are
answered by three page loads.**

**CLASS 2 -- address REFUSED. Cost: an operator RULING, then a boundary entry,
then the page load -- in that order.** Not because the edit is hard, but
because a committed ruling forbids the shortcut:

> a ruling forbids a discovery probe from navigating to a refused address
> **even to find out whether it should be admitted**

That is s3.5's deadlock in its operative form. These three carry it:

    SAVED-POSTS-SURFACE     /my-items/saved-posts/        2 rows
    SEARCH-HISTORY-SURFACE  address NEVER FOUND           2 rows
    SKILL-PAGE-SURFACE      address is a GUESS            1 row

`SEARCH-HISTORY-SURFACE` and `SKILL-PAGE-SURFACE` are worse than refused --
**nobody has established the real address at all**, so even the allowlist
pattern cannot be written yet. The sweep called `SKILL-PAGE-SURFACE` the
weakest evidence of its ten; the only address anywhere in the corpus for it is
a guess.

**A correction to my own use of the word ORPHANED.** The shipped locator
reports `SKILL-PAGE-SURFACE` as argued in no document, and I quoted that early
in this wave as a finding. **Section 8.4 measures that tool missing 67.5% of
the mentions in this corpus, so its silence is UNKNOWN and not absence.** The
honest statement is that no argument for this blocker has been FOUND, by a tool
now known to under-report and by one sweep's manual reading -- not that none
exists. This is the same shape as the standing lesson that you can grep a
codebase for what it refuses but never for what nobody considered.

### 7.2 The single biggest unknown, priced on its own

`SEARCH-RESULTS-SURFACE` -- **21 rows, every one still GAP, the largest
all-GAP blocker in the class.** Class 2, and it additionally carries a live
security finding: an anchored family wildcard admits a path-traversal string
that normalises onto an account-ending address and no forbidden substring
catches it. **Cost: one operator ruling on which of four candidate patterns to
admit (already enumerated and blast-radius-measured by a sibling, deliberately
not chosen), then the pattern, then a capture of
`/search/results/people/?keywords=<term>` which serves 16 of the 21 rows.**
It is the highest rows-per-capture item in the entire class and it is gated on
a decision, not on work.

### 7.3 What I declined to do, and why

**I did not open a page.** The `linkedin` MCP server failed to connect at
session start, so no live read was available to me -- but I would not have
taken one without a ruling anyway for the class-2 addresses, and the class-1
captures belong to a wave that can sanitise and freeze a fixture properly
rather than to an adjudication pass.

**I did not re-file a single row to a differently-named blocker**, although
s3 establishes that 23 of 26 are addressability facts. `blocker-map.tsv` is
DERIVED from evidence lines; a re-attribution would have to be manufactured as
evidence to make the map follow. Moving 137 rows between labels while changing
no fact is the ratchet this corpus has already been bitten by.

---

## 8. CENSUS DEFECTS HANDED OVER

1. **A published classification with no committed classifier** (s2). The
   `SURFACE?`/`CODE` split is unrecoverable -- 1.87e14 subsets fit. Any future
   by-subject classification must ship its classifier in `scripts/`.
2. **The ledger's boundary column is stale in 15 cells** (s3.4) and carries an
   explicit warrant saying it cannot be. Corrected with a declared pair; the
   warrant's COST half stands.
3. **A stale comment in shipping code** (s4.3): `readonly.py` above the
   `/jobs/alerts/` pattern still says nobody has opened the page, after a live
   redirect measurement answered it. Stale in the direction that sounds careful.
4. **`scripts/find_blocker_reason.py` misses two thirds of the argument in
   this corpus, and its silence is NOT absence. Now measured.** It scored the
   most substantive `SERVICES-PAGE-SURFACE` document at ZERO; a follow-up
   measurement over all 26 blockers found:

       mentions of a blocker across _audit/          286
       ranked with a score > 0                        93   (32.5%)
       BLIND -- mentioned, scored zero               193   (67.5%)

   A fixed-seed random sample of 51 of the 193 blind mentions, read in
   context, came back **42 substantive / 9 incidental (82%)** -- and all 9
   incidental trace to just 4 mechanical accounting documents that score zero
   for that mention while scoring substantively elsewhere in the same file.

   **THE MECHANISM, verified by grep rather than inferred: a document that
   argues by CENSUS ROW ID -- this campaign's own convention -- instead of
   repeating the blocker's compound name is nearly invisible to a same-line
   co-occurrence test.** `2026-09-19-events-surface.md` and
   `2026-09-20-company-page-built.md` each contain their blocker's name
   exactly twice, title plus one scope line, and never beside an argue-word.
   **All three flagship `SEARCH-RESULTS-SURFACE` admission documents and both
   2026-09-20 build-wave reports are blind for their own blocker.**

   The other direction was measured too, because a blind-spot number without
   its false-positive counterpart is half a measurement: of 19 top-ranked
   non-census documents, **18 were substantive and 1 was a false positive**
   (a mechanical table whose status word "BLOCKED" is on the argue-list).
   **Precision is high; recall is the defect.** Also noted: both census TSVs
   rank top-2 for all 26 with no exception and are near-duplicates by
   construction, so the RANKED count overstates source diversity.

   **Do not derive a `reason_doc` column from this tool.** It is also
   quadratic -- it re-scans the whole corpus once per blocker across 97, over
   120 seconds -- so it is both slow and, more importantly, wrong in the
   direction that reads as "nobody argued this".
5. **Same-day documents disagreeing without either marked superseding** --
   `BADGES-SURFACE`'s B7-vs-B8 row set, and `CONTENT-ANALYTICS-SURFACE` carrying
   both "OVER-COUNT" and "family closed, 8 of 8 filed" in one document.
   Reported by the sweep verbatim, adjudicated by nobody.
6. **`_audit/2026-09-20-company-page-built.md` claims rows PARTIAL/SHIPPED
   while `blocker-map.tsv` reads GAP**, and the document admits it. **The
   derived map is the authority and the prose document is a claim.** The repair
   is to move the census cell so the map follows -- never to edit the map.
7. **`JOB-ALERTS-SURFACE` changed shape mid-wave**, split by today's
   write-offs document into `ALERTS-PAGE-UNREAD` plus a write-only remainder.
   Any table built from the 2026-09-03 ledger predates the split.
