# WHAT IS REACHABLE NOW: 68 read rows, two banked, and the read-direction sweep is blind to a whole slice

**CORRECTS:** `_audit/2026-09-21-the-read-triage.md` -- its headline "19 buildable of 59 read rows" is superseded on both numbers. The denominator is **68**, not 59, because that wave scoped itself to profile and network, and the jobs slice holds 29-to-31 read rows that no direction-based sweep in this repository can see. Of its 19 buildable, **three were built and fired the same day and all three came back CANNOT-DELIVER**, twelve are behind a press since REFUSED terminally, and one banked. Nothing in that document was wrong when written; every one of its verdicts that I re-took reproduced.

**CORRECTS:** `_audit/_census/jobs.md` -- row `40` moves COVERED-UNFIRED to COVERED-PROVEN on a live firing, against the bar that row's own author pre-registered.

**CORRECTS:** `_audit/_census/network.md` -- row `53` moves GAP to COVERED-PROVEN on a live firing; row `134`'s evidence cell gains the witness result, state unchanged.

**CORRECTS:** `_audit/_census/profile.md` -- row `O3`'s evidence cell gains the same, state unchanged. Its reason was `no tool, no reason`; there is now a reason.

**2026-09-21. Wave `what-is-reachable-now`, base `09b5f17`. READ-ONLY throughout.
`writes_enabled()` False. Nothing was connected to, followed, messaged, invited,
applied to, saved or posted. One sanctioned disclosing press was taken through
the shipped gate on his own analytics page, under a ruling, with all four
conditions run and reported. The browser was ATTACHED to, never launched, and it
is still up.**

---

## 0. THE ANSWER, FIRST

**Three things are buildable today. Two of them I built and banked. The other
sixty-five are gated, and the gates are now named precisely enough to schedule.**

    read-direction GAP rows, re-derived            68      (was 59; see section 2)
    banked this wave                                2      J 40, N 53
    measurements taken that banked nothing          2      the witness, the settle
    rows whose BLOCKER changed kind                 2      N 134, P O3
    rows re-priced because a boundary moved today  16      section 3

**AND THE MOST USEFUL SENTENCE IS NOT ABOUT A ROW.** The two shipped instruments
that answer "which rows could a reader close" **disagree with each other, and
both are blind to the same 56 rows**:

> `scripts/triage_read_gap_rows.py` counts a row as a read only when its
> direction cell is exactly `R`; `scripts/reader_closable_blockers.py` counts
> `R` **and** `R+W`, and says so in its own header. **Today's
> `COMPOUND-ROW-SPLITS-ONLY-ON-STATE` ruling is the one that manufactures
> `R+W` cells** -- it says a direction divergence is repaired in the cell as
> `R+W` rather than by a split -- so the stricter instrument will shed a row
> every time that ruling is applied. It is one row today (`P M11`). It was
> zero yesterday.

> And **`jobs.md`'s per-row tables carry no direction column at all**, so
> `direction_of` returns `unknown` for all 56 of its GAP rows and every
> read-direction sweep silently reports jobs as zero. `J 0` is a fact about a
> table shape, not about jobs. `_audit/2026-09-21-the-jobs-direction.md`
> measured the real answer -- **29 `R` plus 2 `R/W` of 57** -- by reading
> section 2's ROW-RANGE table, which is where that slice keeps its directions.

---

## 1. THE COUNTS, RE-DERIVED FROM THE SHIPPED COUNTER

Nothing here is inherited. `scripts/count_census_states.py`, run on this tree.

**BEFORE this wave's edits:**

    jobs.md                    stated rows 150   GAP 56
    profile.md                 stated rows 203   GAP 55
    messaging-and-content.md   stated rows 142   GAP 77
    network.md                 stated rows 209   GAP 86 (87 before N 53)
                                            ----
                               stated rows 704   GAP 275

**AFTER, and this is the control that matters:**

    ./venv/Scripts/python.exe scripts/count_census_states.py --expect J=56,P=55,M=77,N=86
    -> all four MATCH, GAP control expected 274 measured 274 MATCH
    -> stated rows 704

**`stated rows` is 704 before and after, as required.** No row was split, none
was added, none was deleted. Two rows changed state and the moves are visible in
the per-state lines: jobs `CP 20 -> 21`, `CU 4 -> 3`; network `GAP 87 -> 86`,
`COVERED-PROVEN 6 -> 7`.

### 1.1 EVERY COUNT THE BRIEF HANDED ME WAS STALE, AND SO WAS EVERY COUNT IN THE DOCUMENT IT CITED

Stated plainly because this is the seventh time in two days:

    source                                          said     measured today
    the brief                                       59 read rows        68
    2026-09-21-the-read-triage.md  --expect         J=57,P=55,M=82,N=91 (285)
    2026-09-21-the-fourteen-fired.md  --expect      J=57,P=55,M=82,N=90 (284)
    2026-09-21-the-fires-and-the-controls.md        J=57,P=55,M=82,N=87 (281)
    this wave, before its own edits                 J=56,P=55,M=77,N=86 (275)

The six that left between 281 and 275 are not mine: `J 40` left GAP when it was
BUILT this morning, and five messaging rows closed in the write-ceiling wave.
**Every one of those documents was correct when it was written.** The lesson is
not that anybody was careless; it is that a count in this corpus has a half-life
of hours, so a document should print the COMMAND and not only the number.

---

## 2. THE DENOMINATOR IS 68, AND WHERE THE EXTRA NINE CAME FROM

Read-direction GAP rows, by slice, taken with the SHIPPED `direction_of`
(value-based, not positional) over the shipped `cells()`/`classify()`:

    jobs.md                     0      <- AND THIS IS THE FINDING, NOT A ZERO
    profile.md                 18      (17 pure R, plus P M11 at R/W)
    messaging-and-content.md   12
    network.md                 38      (42 less N 33, N 54, N 83, N 175)
                               --
                               68

`scripts/reader_closable_blockers.py` agrees: **68 reader-reachable of 274
still-GAP rows**, and *"a reader cannot be the remaining cost for 206 of them."*

**THE SHIPPED TRIAGE INSTRUMENT REFUSED TO PRINT A TALLY, AND IT WAS RIGHT TO.**
`scripts/triage_read_gap_rows.py` carries a hand-authored verdict table keyed to
the 59 rows of 2026-09-21 morning. Run today it fails its own CONTROL 4:

    read-direction GAP rows in P+N   55
    rows carrying a verdict          59
    VERDICT for N 175, which is NOT a read GAP row today
    VERDICT for N 33,  which is NOT a read GAP row today
    VERDICT for N 54,  which is NOT a read GAP row today
    VERDICT for N 83,  which is NOT a read GAP row today
    REFUSING TO REPORT: 1 control failure(s).

That control was built to catch exactly this -- *"a row LEAVING the read-GAP set
leaves a verdict behind pointing at nothing"* -- and four rows left it in one
day. **I did not repair its table.** Re-keying it to today's set would make it
green for a few hours and would re-create, in a shipped instrument, the same
hand-maintained snapshot that has now gone stale seven times. Its refusal is
more informative than its tally would be.

**ITS 55 AND MY 56 ARE BOTH CORRECT AND THE GAP BETWEEN THEM IS THE `R+W`
DISAGREEMENT** described in section 0: line 330 of that file reads
`reads = {k for k, d in gap.items() if d == "R"}`, which drops `P M11`.

---

## 3. THE ROWS I RE-PRICED, AND WHICH BOUNDARY MOVED

### 3.1 THREE ROWS THE TRIAGE CALLED BUILDABLE WERE BUILT, FIRED, AND CANNOT DELIVER

Boundary that moved: **not a boundary at all -- a measurement.** They were built
and fired between that document and this one.

| row | triage said | today | what the fire found |
|---|---|---|---|
| `N 33` | BUILDABLE | **COVERED-CANNOT-DELIVER** | fired against six organisation Pages, `ok` 6 of 6, and the number it publishes is ONE SHORT |
| `N 54` | (its neighbour) | **COVERED-CANNOT-DELIVER** | clean `count_read` on 6 of 6 with six distinct values -- and the count is not attributable to the Page it was read from |
| `N 175` | BUILDABLE, "a named, non-trivial price" | **COVERED-CANNOT-DELIVER** | `ambiguous` on all three groups, because its positive branch cannot fire at all |

These are out of GAP and out of my scope, and they are the single most useful
correction available to a scheduler: **the triage's "BUILDABLE" column was a
claim about an address and a reader, never a claim that the page draws what the
row wants**, which that document says about itself in its own section 7. Three
of three went the other way.

### 3.2 TWELVE SEARCH-FILTER ROWS: THE PRESS IS REFUSED, SO THE BLOCKER CHANGED KIND

Boundary that moved: **`_audit/2026-09-21-the-all-filters-press.md`.**

`N 80`, `N 81`, `N 84`-`N 93` were 12 of the triage's 14 "BUILT AND UNFIRED,
needs one browser slot". **The browser slot happened** (wave `fire-the-fourteen`)
and **only `N 83` banked**. The remaining twelve are behind the `All filters`
panel, and pressing it is now settled as REFUSED at conditions 2 and 3 of
`DISCLOSING-PRESS-PERMITTED` -- condition 2 **terminally**, because the control
declares neither `aria-expanded` nor `aria-haspopup` and no caller naming a
sanctioned shape can ever reach it.

**RE-PRICED: these are not "needs a browser slot". They need a RULING or a new
INSTRUMENT, and the instrument is the expensive one.** The all-filters wave
measured the only press-free route -- the terms read nonzero in the navigation's
response bodies -- and priced it: *a reader over response bodies that this
package does not have, whose admission is heavier than the press.*

`N 82` is the one to read before trusting any of it: it MATCHED LIVE and was
still refused, because nothing available can tell a people filter from a job
promo without reading a label, and reading the label is the one thing that
surface forbids.

### 3.3 `N 134` AND `P O3`: THE BLOCKER IS NOW EXACTLY ONE UNBUILT ARTIFACT

Boundary that moved: **this wave** (section 4.3) plus commit `84cd587`.

### 3.4 THE BOUNDARY I EXPECTED TO HAVE MOVED, AND HAD NOT

I briefed a slice on the premise that `readonly.py` changed today at `24aabf2`
and that the triage's address verdicts were therefore stale. **That premise is
false and the slice said so rather than working around it.**

> `git show 24aabf2 -- linkedin_server/readonly.py` is **comment-only**. No
> regex in `_ALLOWED_URL_PATTERNS` and no entry in
> `_FORBIDDEN_URL_SUBSTRINGS` was added, removed or edited. The commit's own
> message says it: *"Boundary: no address admitted, no write added, no ruling
> resolved."*

**30 addresses re-driven through `readonly.is_read_url`: AGREES 30, MOVED 0,
NEW 0.** What `24aabf2` changed is reachability BY TOOL -- two new callers can
navigate to addresses that were already admitted -- which is a different axis
from the one the predicate measures, and confusing the two is how
`ALLOWED-AND-STILL-WRONG` became a named category in this repository.

Evidence: `_audit/_census/_wave-address-recheck.tsv`, which also lists nine
addresses named in the triage with **no recoverable literal** -- the document
states a verdict without ever giving the url string, so it cannot be re-driven
and is taken on that document's word. That is a small, real hole in the corpus's
re-derivability and it is recorded rather than papered over.

---

## 4. WHAT I BANKED, AND THE DISCRIMINATION BEHIND EACH

### 4.1 `J 40` -- per-job network proximity. COVERED-UNFIRED -> COVERED-PROVEN

**THE BAR WAS PRE-REGISTERED BY THE ROW'S OWN AUTHOR, BEFORE ANY FIRE**, which
is why this is a bank and not a bar invented to fit a result. `jobs.md`'s THIRD
DELTA:

> The reader was exercised and read back -- over four committed captures, in a
> real headless browser, in both of LinkedIn's layouts -- but never against
> LinkedIn. By this slice's own standard a fixture is not a fire, so **it enters
> at COVERED-UNFIRED and moves to COVERED-PROVEN on one live search.**

Four live runs through the shipped `linkedin_search_jobs` and
`linkedin_job_detail` (`scripts/_probe_proximity_live.py`, attach mode,
provenance printed per run). Every reading reproduced across all four.

**THE DISCRIMINATION, on three axes:**

1. **WITHIN SURFACE.** 1 of 14 distinct postings drew `count_read` /
   `company_alum`; 13 omitted the key. **A dead selector omits it on all 14** --
   that is the failure mode, and it is excluded.
2. **ACROSS SURFACE.** That same posting read `count_read` on the search card
   and `relation_only` on the detail page. **This asymmetry is a PREDICTION the
   reader's design made before any browser ran** -- the detail page draws the
   relation as a heading over a face pile and states no number -- so it is
   falsifiable, and a defaulted field cannot produce it.
3. **THE LEAK GATE NEVER FIRED.** Every emitted value was `int` or `None` on
   every reading of every run.

**WHAT DID NOT BANK, AND IT IS IN THE CELL:** the COUNT axis discriminates
nothing. Every count read was `2`, n=1 distinct posting. **This fire proves the
reader REACHES the live field; it does not prove the number is right**, and the
`N 54` lesson -- a clean, discriminating count that was wrong by one -- is
untouched by it.

**THE PROBE CONVICTED ITSELF TWICE AND BOTH ARE WORTH MORE THAN THE ROW.**

* **It reported `count_read 3` where the truth is 1.** Three searches returned
  21 cards; one popular posting matched all three terms and was rendered three
  times. **Counting CARDS reports one fact three times** -- precisely the
  "de-duplicate on the fact, not the match" hazard `find_proximity` closes
  INSIDE a card, reappearing in the instrument built to measure it. Now
  reported per distinct job id, with the card figure kept beside it.
* **Its first verdict function was blind to the signal.** It excluded the
  `(key absent)` class from the tally, so 3-drawn-against-18-absent read
  `UNDISCRIMINATED` **over a denominator of 3** -- reading only the rows that
  already agreed. Since `parse_job_card` OMITS the key when nothing is drawn,
  absent-everywhere IS the dead-reader signature and present-on-some IS the
  discrimination. Both cases are now controls.

**THE GATE WAS SHOWN FAILING BEFORE IT CERTIFIED ANYTHING.**
`scripts/_check_the_proximity_leak_gate_can_fail.py` plants a string in each of
three slots, a whole-reading string, an unexpected key and a `bool` (which a
naive `isinstance(x, int)` admits, since `isinstance(True, int)` is True), and
asserts the gate refuses each **without ever quoting the value it refused** --
the scar being that `int()` puts its refused input verbatim into its own
`ValueError`. It also asserts the clean shapes are admitted, so it is not a gate
that refuses everything.

### 4.2 `N 53` -- a Page's follower count. GAP -> COVERED-PROVEN

`network.md`'s own standard: *"a tool exists AND an audit records it firing live
and returning what it claims."*

Fired at zero extra page load, riding the same `linkedin_job_detail` calls.

    company_about.state = "read"   on 10 of 10 postings carrying the card
    followers            integer   on those 10, 10 DISTINCT VALUES
    magnitude spread               4-digit x1, 5-digit x4, 6-digit x5

**WHY `state == "read"` IS THE LOAD-BEARING FIELD AND NOT `followers`.** `read`
is the all-four-fields-parsed state, and it is reachable only when the About
card's own opening name AGREES with `dom.read_job_identity`'s company. **So the
attribution check passed live on ten postings neither fixture author
controlled** -- the mismatch state is `unnamed`, and it never appeared.

**IT DISCRIMINATES FROM ITS OWN NEIGHBOUR, which is the test that matters
here.** `N 54` asks how many of HIS CONNECTIONS follow a Page and read 2-to-11.
This row asks TOTAL followers and read 4-to-6 digits. A reader returning the
neighbour's quantity would be visible immediately; it is not.

**AND IT IS STRUCTURALLY IMMUNE TO THE DEFECT THAT KILLED `N 54`** -- audited in
source BEFORE the fire, not rationalised after
(`_audit/_census/_slice-n53-follower-chain.md`):

| the `N 54` defect | `N 53`'s reader |
|---|---|
| phrase matched as a SUFFIX of `<entity> & n other connections follow this page` | `shape._ABOUT_FOLLOWERS` is `^([\d,N]+)\s+followers$` -- **fully anchored**, a suffix collision is impossible |
| ran page-wide; the phrase occurred 5-8 times per Page, never once | `dom.read_company_about_card` is scoped to ONE card element |
| -- | reads `inner_text`, **not** `textContent`, so the `aria-hidden` / `visually-hidden` merge does not reach it |
| -- | its `int()` sits behind an `isdigit()` gate, so the coercion can never quote a refused value |

**THE ONE ITEM I DID NOT CLOSE**, written into the cell so the next reader
inherits a fact rather than a silence: the OCCURRENCE COUNT inside the card --
*exactly one line matches* -- was not instrumented. The anchor makes a collision
structurally implausible rather than measured. The slice that set the bar listed
six discriminators; this fire closes five.

### 4.3 TWO MEASUREMENTS THAT BANKED NOTHING AND WERE WORTH TAKING

**THE WITNESS FIRED. THE PANEL OPENS.** `N 134`'s cell has said since
2026-09-19 that a permitted press could not be told from a press that missed:
*"the panel opened and Escape closed it, or the press did nothing at all.
Nothing in the run distinguishes them."* The witness has since been built. I ran
`scripts/_probe_first_sanctioned_press.py` **unmodified**, having first run the
four conditions -- three settle offline (`admitted: True`; `shape_ok: True`;
`basis_declared: True, basis: structural`, the one complete structural argument
in `press.SENSITIVITY_BASES`):

    "witness": {"disclosed": true, "moved": ["expanded_true", "menus"],
                "witnessed_by": ["dialogs","expanded_true","listboxes","menuitems","menus"]}

**`disclosed: true`, for the first time.** The press does not miss.

**AND CLOSURE WAS REFUSED -- WHICH IS A FINDING ABOUT THE GATE, NOT THE PRESS.**
`expanded_false` 8 -> 9 and `shape_total` 8 -> 9, so `check_closure` reported
NOT-left-as-found and the probe STOPPED rather than retried. **I resolved that
without pressing anything again**, which is the whole point:
`scripts/_probe_analytics_settles_without_a_press.py` loads the page and reads
the same counts three times over eight seconds, **pressing nothing**:

    shape_total     9 -> 9 -> 9
    expanded_false  9 -> 9 -> 9
    expanded_true   0 -> 0 -> 0      dialogs  0 -> 0 -> 0

The never-pressed settled value is **9 -- exactly what the press run read
AFTER**. It is the BEFORE reading of 8 that is the outlier, on a page a
2026-09-19 capture also measured at 9. **The press left the page in the state a
page nobody touches holds**, with nothing open at either end of either run.
`check_closure` compares two absolute readings and cannot separate *"the press
left a control behind"* from *"the first reading was taken before the page
finished drawing"* -- the same read-too-early class as the people-search panel
race, now in the press gate's closure condition. It fails safe. Why that one
reading was 8 is NOT established, and **no second press was taken to chase it.**

---

## 5. WHAT I LEFT, WITH THE BLOCKER NAMED AND ITS KIND

Kinds: **ADDRESS** (nothing admits it), **RULING** (somebody must decide),
**INSTRUMENT** (something must be built), **MEASUREMENT** (nobody has looked).

### 5.1 THE TWO ROWS WHOSE BLOCKER I SHARPENED TO A SINGLE ARTIFACT

| row | kind | the blocker, now exactly one thing |
|---|---|---|
| `N 134` | **INSTRUMENT** | a NAME-FREE CONTENT SHAPER for the disclosed panel. Not a ruling (granted), not the mechanism (shipped), not "does the press work" (measured above). Nothing in `dom.py` or `shape.py` names notable or interesting viewers; `press.disclose` has NO caller in the package |
| `P O3` | **INSTRUMENT** | the same artifact, same surface. Its reason cell read `no tool, no reason`; there is now a reason |

**AND THE PRICE OF THAT ARTIFACT IS MEASURED, WHICH IS WHY IT IS NOT CHEAP.**
The panel is made of OTHER PEOPLE. `dom.py`'s `# readonly-ok` waiver budget is
**AT its cap of 22 with ZERO remaining**, so the shaper must reuse an
already-declared in-page script or the cap moves and needs its own argument. And
`textContent` merges an `aria-hidden` visible copy with a `visually-hidden`
screen-reader copy that on people surfaces CARRIES THE EMPLOYER NAME.

### 5.2 THE SIX DECISIONS, ALL STILL UNMADE, COVERING 18 ROWS

I queried `_audit/RULINGS.md` before calling any of these unruled -- 36
registered rulings, and **none of them answers any of these six**. That register
exists because four people concluded "nobody ruled this" about something that
was written down; this is what it looks like when the query comes back empty.

| id | question | rows | kind |
|---|---|---|---|
| D1 | may a search keyword be passed? | `N 79`, `N 93`, `N 94`, `N 194` | RULING |
| D2 | widen the search admission past the people vertical? | `N 104`, `N 161`, `N 179` | RULING |
| D3 | **does a reasoned allowlist refusal count as "written"?** | `N 99`, `N 100`, `N 172`, `N 177`, `N 178`, `M C83` | RULING |
| D4 | may this package create its own browser context? | `P C8` | RULING |
| D5 | is a passive cost a capability row? | `N 171`, `N 183` | RULING |
| D6 | do two addresses discharge a row named for a control? | `N 132` | RULING |

**D3 IS THE ONE TO TAKE AND IT HAS NOW BEEN RE-FILED THREE TIMES.**
`_audit/2026-09-19-the-read-rows.md` called it *"the single highest-yield
decision left in this row set"*; the read triage re-filed it unchanged two days
later noting it was named in exactly one document out of every document under
`_audit/`; the open-queue re-filed it again. **It banks six rows at once and
settles every future boundary-blocked row.** It is cheap, it is nobody's
measurement, and it has outlived three waves that each correctly identified it
as the best available move and then could not make it.

### 5.3 THE REST OF THE SIXTY-EIGHT, BY KIND

    ADDRESS      15   the surface exists and nothing admits it. TWO SUB-KINDS,
                      and the census has repeatedly recorded one as the other:
                      REFUSED (a forbidden substring names it -- it fires
                      BEFORE the allowlist, so the row needs a pattern AND an
                      exemption, a DOUBLE cost) vs ABSENT (nothing names it
                      either way). P L2b, P M12, N 61, N A3, N A5 are REFUSED;
                      the other ten are ABSENT
    RULING       18   section 5.2
    PRESS         5   P A25, P D28, P J4, N 76, N 133 -- behind a control this
                      package does not sanction pressing. N 133 is the
                      neighbour most likely to be swept in by accident: it
                      applies a FILTER, and applying a filter SUBMITS, which
                      the ruling refuses by name
    INSTRUMENT   14   the 12 all-filters rows (5.2 above measures the only
                      press-free route and prices it above the press), plus
                      N 134 and P O3
    MEASUREMENT  14   an admitted address and a shipped reader, and nobody has
                      looked. Concentrated in jobs: J 110 and J 116-120 are
                      boundary 0 with a parser as their only cost, and the
                      panel has never been captured

**AND ONE THAT IS NOT A DECISION THOUGH IT LOOKS LIKE ONE.** `N 174` -- view the
groups you have requested to join -- is unmeasurable by any read on this
account's current state: a pending request must EXIST for the surface to be
observable, and creating one is a WRITE at a real group. Its refusal to retire
on a comfortable zero is correct. *A reading no instrument can fail is not a
reading.*

### 5.4 WHAT I DID NOT DO, STATED SO NOTHING HERE READS AS MORE THAN IT IS

* **I pressed once**, on his own analytics page, under a ruling, with all four
  conditions run and reported. I pressed nothing else. I did not press
  `All filters` -- it is refused, and running the four checks is how I know
  rather than something I decided.
* **I read no label, no name, no employer, no url.** Every probe here emits
  integers, positions in shipped closed alphabets, and verdicts.
* **I did not repair `triage_read_gap_rows.py`'s stale table**, and section 2
  says why. I did not repair the `R` vs `R+W` disagreement either: which
  instrument is right is a convention question, and inventing an answer to make
  two numbers agree is the failure the blocker map exists to prevent.
* **I did not re-price the 12 all-filters rows in their cells.** The all-filters
  wave already corrected all twelve this morning and the correction is right;
  re-writing them to say the same thing in my words would destroy the record of
  who found it.
* **`J 57` remains unbuilt.** It is unblocked now that `J 40` ships, and its own
  caveat is recorded rather than hidden: the Applied tab reads zero, so the join
  would be vacuous on today's account.

---

## 6. THE GATE

Staged first, then `scripts/impact_gate.py`. Verbatim:

      PASS over the 43 file(s) above (2093 tests) -- AND OVER NOTHING ELSE.
      NOT CHECKED: 164 of 207 test files (79.2% of the suite by file).
      The corpus-wide guards DID run, so the identity, credential and page-text
      sweeps cover the whole tree. Everything else above is unexamined.
      That is roughly 4001 of 6094 tests unrun (65.7%), against a suite count taken 2026-09-20 at 970a276.
      Wall clock: 997.7s.
      THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
      certifier; a green gate here is not a reason to shrink that matrix.

The impact set is 43 of 207 files, **20.8%**, so it is well under the ~45%
widening threshold and no widening notice was printed.

### 6.1 THE GATE REFUSED TWICE BEFORE IT PASSED, AND BOTH REFUSALS WERE RIGHT

Recorded because a wave that reports only what it found, and not what caught
it, is reporting half a run. **All three failures were mine.**

**1. THE IDENTITY SHAPE GUARD REFUSED MY OWN SYNTHETIC PLACEHOLDER.** The
address re-check TSV spelled a numeric organisation id as a run of ten zero
digits, and ten digits after `/company/` matches the company-id SHAPE:

    REFUSED: a file this commit would write carries an UNDECLARED identifier shape.
      _audit/_census/_wave-address-recheck.tsv:6  [company id]  /c..00 <19 chars>

**A SHAPE MATCH MEANS UNDECLARED, NOT REAL** -- the value was synthetic and the
guard cannot know that, which is exactly why the right repair is the one the
guard names first: change the content, not `DECLARED_PLANTS`, *"since a
declaration permanently widens what the guard tolerates for that file."* The
rows now read `/company/NUMERIC-ID/` with a header comment recording what was
actually driven, and the verdicts are unaffected because the allowlist pattern
accepts a digit run rather than a particular one. **Worth noting against the
standing scar that a worktree carries no gitignored files:** the EXACT-VALUE
half of that gate is disarmed here for that reason, and it is the SHAPE half
that fired. One of two halves live is not the same as a guard passing.

**2. THE TAB-LEAK RATCHET CAUGHT BOTH MY PROBES, AND THEY WERE ALREADY CLEAN.**
`test_the_tab_leak_only_ever_shrinks` went 39 -> 41. Both probes close their own
page in a `finally` and neither ever touches the context -- but the detector
matches by NAME, `\b(page|tab|_own_page)\s*\.\s*close\s*\(`, and my variable was
`own`. **A genuinely clean probe read as a leak.** The sibling probe's own
comment predicts this precisely: *"a probe that cleans up by a route the
detector cannot see would have pushed the pin UP while actually being clean."*
Bound to `page` before closing, in both files, with the reason written at the
call site. The pin stays at 39; I did not lower it and I did not raise it.

**3. THE CORRECTION GUARD CAUGHT A MARKER NAMING TWO DOCUMENTS.** My opening
`CORRECTS:` line named the read-triage document and mentioned `jobs.md` in the
same sentence; the parser takes ONE target per marker, so it registered as
malformed and the three back-pointers I did write went unchecked behind it.
**This is the identical defect the read-triage wave recorded this morning** --
*"A marker naming TWO documents on one line declared only one -- so the fix was
two markers, not a longer one"* -- and I reproduced it within hours of reading
it. Rephrased to name one, back-pointers written into all four corrected files,
and the five remaining candidate pairs triaged onto `NOT_A_CORRECTION` with a
reason each **after reading the line**. All five are one shape: a census cell
citing its OWN EVIDENCE, which runs corrector <- corrected, the opposite
direction from a correction.

---

## 6.2 THE CHANGED-WORLD NOTICE, AND WHAT IT DID AND DID NOT INVALIDATE

A `_TEAM_LEAD_*.md` ruling landed at the worktree root at 17:22, while this wave
was staging. It reports that master moved from my fork point `09b5f17` to
`f729a2a` underneath me, and instructs: **`linkedin_server/server.py` moved by 47
lines; if any slice read, drove or counted anything in that file, RETAKE it --
do not reconcile by reading your notes against the new file.**

**THAT REACHES THIS WAVE DIRECTLY.** `scripts/_probe_proximity_live.py` drives
`server.linkedin_search_jobs` and `server.linkedin_job_detail`, so both banks
rest on that file's bytes, and the probe records `sha256_server.py` per run for
exactly this reason.

**I DID NOT RECONCILE BY EYE, AND I DID NOT NEED TO RE-FIRE.** Judging a diff
"comments only" by reading it IS the reconciliation the ruling forbids, so the
question was settled mechanically: parse both revisions, strip every docstring,
compare the ASTs.

    file        linkedin_server/server.py
    ref A       09b5f17      ref B  f729a2a
    AST chars   313597 vs 313597
    EXECUTABLY IDENTICAL.

Every difference between the two revisions lies inside a docstring or a comment
-- the 46 insertions are `_error`'s expanded docstring and a declaration comment
in `linkedin_premium_job_collection`, and the 1 deletion is the old one-line
docstring. **No statement, no expression and no non-docstring constant differs,
so the two files cannot behave differently and a measurement taken against one
is valid against the other.** The instrument is
`ast_equal.py`, run from the scratchpad and reported here rather than shipped,
because it is a general-purpose two-ref comparison with no home in this package's
register; a wave that wants it should lift it deliberately.

**THE NEW RULING DOES NOT TOUCH ANY OF MY SIX.** `RULINGS.md` gained exactly one
entry, `ERROR-MESSAGE-RULED-AT-THE-RAISE`: what an error envelope's `message` may
carry is decided WHERE THE VALUE ENTERS the exception, never where it leaves,
because a page value inside a stdlib `ValueError` is indistinguishable at the
envelope from any other. **I checked it against D1-D6 before re-deriving them and
it answers none of them**, which is the check that register exists to make cheap.
It does bear on this wave's instruments, and confirms them: my probes sit at the
ENVELOPE end, where only `type(exc)` and `str(exc)` survive, so reporting the
TYPE alone and never the message is the conservative-correct behaviour at that
position -- and the ruling explains why it has to be.

### THE ONE THING THE LEAD NEEDS BEFORE MERGING THIS

**A GUARANTEED TEXTUAL CONFLICT IN `tests/test_a_correction_is_findable_from_the_claim.py`,
AND ITS RESOLUTION IS TO KEEP BOTH SIDES.**

    master  f729a2a   @@ -185,6 +185,54 @@   CORRECTION_VOCABULARY
    this wave          @@ -185,6 +185,62 @@   CORRECTION_VOCABULARY

Both hunks open at line 185 and both insert entries into `NOT_A_CORRECTION`
immediately after its opening brace. The entries are INDEPENDENT -- master's
belong to the `what-the-browser-said` wave, mine are the five census-cell-cites-
its-own-evidence pairs in section 6.1 -- and the dict is keyed by
`(corrector, target)` pairs that do not collide. **Taking either side alone will
turn the guard red for the other wave's pairs.** This is a textual conflict with
a semantic non-conflict underneath it, which is the kind that gets resolved wrong
in a hurry.

---

## 7. EVIDENCE: EVERY NUMBER HERE IS RE-DERIVABLE FROM A CLONE

| claim | re-derive with |
|---|---|
| 704 stated rows, GAP 274 | `scripts/count_census_states.py --expect J=56,P=55,M=77,N=86` |
| 68 read-direction GAP rows | `scripts/reader_closable_blockers.py` -- its TOTAL line |
| the shipped triage refuses | `scripts/triage_read_gap_rows.py` -- CONTROL 4 |
| the `R` vs `R+W` disagreement | `triage_read_gap_rows.py` line 330 against `reader_closable_blockers.py`'s own header |
| jobs has no direction column | `jobs.md`'s per-row table header: `# \| capability \| source \| state \| reason` |
| J 40's live fire | `LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 python scripts/_probe_proximity_live.py 12` |
| the leak gate can fail | `scripts/_check_the_proximity_leak_gate_can_fail.py` -- 6 planted defects, all refused, none quoted |
| the witness fired | `scripts/_probe_first_sanctioned_press.py`, unmodified |
| the page settles at 9 with nothing pressed | `scripts/_probe_analytics_settles_without_a_press.py` |
| the four press conditions offline | `_audit/_census/_slice-analytics-press-preflight.md` section 1 |
| N 53 is not vulnerable to the N 54 defect | `_audit/_census/_slice-n53-follower-chain.md` section 3 |
| 24aabf2 moved no address | `_audit/_census/_wave-address-recheck.tsv` -- AGREES 30, MOVED 0 |
| the waiver budget is exhausted | `_slice-analytics-press-preflight.md` section 5, against `tests/test_readonly.py` |

**WHAT THIS WAVE DID NOT ESTABLISH:**

* **That `J 40`'s COUNT is correct.** n=1 distinct posting, one value.
* **That exactly one line matches `_ABOUT_FOLLOWERS` inside a card.** Structural
  argument, not a measurement.
* **Why the press run's BEFORE reading was 8** on a page that otherwise holds 9
  from t+0.
* **Anything about the 12 all-filters rows** beyond what the wave that measured
  them reported. I re-read their evidence; I took no new reading there.

---

## 8. THE LEDGER LINE

    read-direction GAP rows re-triaged                       68
    rows banked to COVERED-PROVEN                             2   J 40, N 53
    rows moved out of GAP                                     1   N 53
    rows inflated                                             0
    census cells corrected with a MEASUREMENT                 2   N 134, P O3, state unchanged on both
    rows re-priced because a boundary moved today            16   3 CANNOT-DELIVER + 12 press-refused + 1 banked
    measurements taken that banked nothing                    2   both worth more than a row
    defects found in THIS WAVE'S OWN instrument                2   both fixed, both now controls
    guards that fired on MY output                             3   all three right: section 6.1
    guard floors moved to pass                                 0   the tab pin stays at 39
    premises in my own brief refuted by disk                   2   section 3.4, section 2
    instruments shipped                                        3   two probes and a control, shown failing
    presses taken                                              1   ruled, four conditions run and reported
    presses taken to chase a hypothesis                        0
    guard floors lowered to pass                               0
    stated rows                                              704   before and after

**THE ONE-LINE READING. Sixty-eight rows read, two banked on live fires whose
bars were set before the fires ran, and sixty-five left with a blocker named to
its kind. The most valuable thing found is not a row: both shipped instruments
that answer "what could a reader close" are blind to an entire slice's 56 rows,
they disagree with each other about a class of cell that a ruling made this
morning actively creates, and the highest-yield decision in the corpus has now
been correctly identified by four consecutive waves and made by none of them.**
