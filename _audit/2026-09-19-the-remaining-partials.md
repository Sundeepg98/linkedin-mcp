# The eight blockers still PARTIAL, and what each one actually is

**Measured at `201b757`, re-measured at `c69d888`. Every number is reproducible
from a committed script and the command is named at each claim.**

    complete 86 -> 87   partial 8 -> 7   UNASSIGNED 21 -> 20

| blocker | pub | held | verdict |
|---|---|---|---|
| `PER-MESSAGE-OVERFLOW-MENU` | 2 | **2** | **FILED** -- `M M13`, on shipped code two waves had not found |
| `OPEN-TO-HIRING-MODAL` | 5 | 4 | **REFUTED FILING** -- `P B7` is misfiled into `BADGES-SURFACE`; a 3-line fix, not mine |
| `COMPANY-PAGE-SURFACE` | 18 | 16 | OVER-COUNT -- **prior wave's finding**, now machine-derived |
| `CONTENT-ANALYTICS-SURFACE` | 5 | 4 | OVER-COUNT -- family closed, 8 of 8 filed |
| `CREATOR-HUB-SURFACE` | 4 | 3 | over-count **CONFIRMED. I attacked it and the attack failed** |
| `POST-COMMENT-CONTROLS` | 4 | 3 | over-count **CONFIRMED, and ruling E's stated reason is factually wrong** |
| `ARTICLE-SURFACE` | 6 | 5 | DECLINED -- prior wave's reason, now mechanised |
| `ACCOUNT-VERIFICATION` | 3 | 2 | DECLINED -- sole candidate cross-claimed and already ruled |

**ONE RED YOU MUST EXPECT.**
`tests/test_blocker_map_is_derived.py::test_the_committed_map_still_matches_what_the_evidence_derives`
fails on exactly one row, `M M13`, because I appended evidence and did **not**
run `--write` as instructed. Verified it is mine and only mine: restoring the
tsv to `b43250b` and re-running gives **7 passed**. `--write` clears it.

---

## 0. THE FINDING THAT IS NOT ABOUT THESE EIGHT

`RE_FILED` fixed the SOURCE side of a re-file and nothing fixed the
DESTINATION. The moved row still counts toward the receiving blocker's
published total, so an incoming re-file silently pays for one of ITS OWN
published rows that nobody recovered.

    ./venv/Scripts/python.exe scripts/_check_refile_destination_credit.py

    SEARCH-RESULTS-SURFACE   publishes 21, holds 21, 4 incoming -> 17 of 21
    FEED-PREFERENCES         publishes  1, holds  1, 1 incoming ->  0 of 1

Both print **COMPLETE -- every published row recovered**. Neither has. Five
published rows are masked; `complete 87` is overstated by two. No count
assertion could have caught it -- a re-file is count-neutral across the pair,
the same structural blindness `_check_published_split.py` exists for, one level
up.

**It is load-bearing for section E.** Ruling E's second test was
*"`SEARCH-RESULTS-SURFACE`'s surplus read is `N 194`"*. The surplus is not one
row; it is four incoming rows masking four outgoing holes, and the split saw
one of them.

---

## 1. `PER-MESSAGE-OVERFLOW-MENU` -- FILED, 2 of 2

**Two waves declined `M M13` on the same sentence and the sentence was false.**

> *"the only candidate (`M13`) is admitted by resemblance, not by any source
> that names the"* blocker -- `_audit/2026-09-19-the-empty-blockers.md:235`,
> and again as *"unrivalled but unnamed; chosen, not forced"*.

`linkedin_server/menus.py:187` -- **shipped package code**, a ruling being
implemented, whose output alphabet is closed so its literals are load-bearing
for behaviour:

    # -- message-level, the PER-MESSAGE-OVERFLOW-MENU family ----------------
    "delete_message":  ("delete message", "delete this message"),
    "edit_message":    ("edit message", "edit this message"),
    "report_message":  ("report message", "report this message"),
    "forward_message": ("forward message", "forward this message"),

The comment heading is the blocker's name verbatim. The row link is not a pick
among candidates: `_sweep_frozen_rows.py forward` returns **exactly one** frozen
GAP row, `M M13 "Forward a message"`.

**THE FREE CONTROL ON THE SAME TABLE, AND IT WEAKENS THE FILING, WHICH IS WHY
IT IS HERE.** That family is BROADER than the blocker. Its seven terms map onto
four frozen-409 rows and two are held elsewhere -- `report_message` is `M M38`
(`REPORTING-FLOWS`, 1 of 1), `reply_to_message` is `M M10` (`THREAD-REPLY-BOX`,
2 of 2) -- while `delete_message` is `M M12`, `EXCLUDED-RULED` **before** the
freeze and absent from the 409 entirely. Nor do the blocks' sizes track
published counts: 10 / 7 / 2 / 1 terms against published 10 / 2 / 1 / 4. **So
menus.py membership alone does not entail blocker membership.**

What closes it is that the family is exhausted once the rows other blockers
name are removed: `M M11` is held here on its own census cell naming this
blocker verbatim, `M M13` is the only member left, it is a W, and the blocker
publishes `2W`. **That is the shape the lead already ruled on** -- the
five-requests ruling section C filed `M35` and `M49` into
`CONVERSATION-OVERFLOW-MENU` on family-plus-split-plus-zero-headroom, over a
census cell that mislabelled direction. This has the same shape and one source
more.

---

## 2. `OPEN-TO-HIRING-MODAL` -- THE ROW EXISTS AND IS MISFILED

Published `1R/4W`; held `1R/3W`. The namesake census section, `profile.md`
*"### J. Open To Hiring (4)"*, holds exactly four rows and **all four are
held**, so the fifth published row is a write outside section J.
`_sweep_frozen_rows.py hiring` returns 8 rows, 0 unassigned; exactly one write
outside section J names `#Hiring`: **`P B7` "#Hiring photo frame apply /
remove"**, in `BADGES-SURFACE`.

**TWO PRIOR WAVES REACHED THIS ROW AND BOTH STOPPED AT THE SAME PLACE.**
`_audit/2026-09-19-routing-the-unassigned.md:211` -- *"`P B7` is a `#Hiring` row
sitting in `BADGES-SURFACE` on a count-admission the ruling itself flagged.
Filed as a ruling request."* `_audit/2026-09-19-partial-blockers-closed.md` --
*"Its rival `P B7` is inside `BADGES-SURFACE`, COMPLETE at 5 of 5; taking it
would break a closed blocker to close another."* **Both treated that 5 of 5 as
settled. It is not, and that is what this section adds.**

### 2.1 The filing says outright that it is not evidence-led

`blocker-assignments.tsv:395` files `P B7` to `BADGES-SURFACE`; the sibling
line's note says:

> *"`B7` IS ADMITTED BY THE ARITHMETIC RATHER THAN BY RESEMBLANCE, and that is
> worth saying because "#Hiring photo frame apply / remove" does not read like
> a badge. It is section B's FRAMES entry. But the published 3W cannot be
> filled without it ... The count admits it; I would not have on the name."*

That arithmetic has one load-bearing premise: `B8` and `K9` *"collapse to one
slot"* -- one blocker cannot hold two frozen-GAP rows of one capability.

### 2.2 The premise is refuted twice

**(i) A committed enumeration two weeks older than the filing.**
`_audit/2026-09-05-profile-rest.md:102-110`, *"## 2. ROW 43 `BADGES-SURFACE` --
what the five rows actually are"*, lists them: **`K8` (R), `K10` (R), `K9` (W),
`B8` (W), `B9` (W)** -- five rows, `2R/3W`, the published split exactly, **with
no `B7` and no collapse required**. It then argues the ledger over-counted by
one because `B8 == K9`, a complaint that only makes sense if the ledger's five
held BOTH -- which excludes `B7`.

**(ii) Measurement.** `scripts/_check_duplicate_rows_share_a_blocker.py` finds
23 near-duplicate pairs in the frozen 409; **15 are filed to ONE blocker, 6 of
those intra-slice** (`M C50`/`M C81` inside `NEWSLETTER-SURFACE`,
`J 118`/`J 119`, `P I14`/`P I15`, `N 84`/`N 87`, `N A7`/`N A8`). Two rows of
one capability sharing a blocker is the ledger's ordinary behaviour.

### 2.3 What follows

    BADGES-SURFACE         K8(R) K10(R)  B8(W) B9(W) K9(W)  = 2R/3W = published
    OPEN-TO-HIRING-MODAL   J4(R)         J1 J2 J3(W) B7(W)  = 1R/4W = published

Both close exactly, nothing left over, nothing missing. **And it DISSOLVES a
ruling rather than overturning one:** request 3 of
`2026-09-19-the-three-ruling-requests-ruled.md:400` picked `K9` over `B8` and
recorded itself as *"A PICK ON A WEAK TIEBREAK ... citing a coin-flip."* That
coin-flip existed only because `B7` had taken a write slot. With `B7` where it
belongs both are in and there is no tiebreak.

**I FILED NOTHING HERE AND THE REASON IS MECHANICAL.** The correction is a SWAP
and this wave is append-only: appending `OPEN-TO-HIRING-MODAL P B7` trips
`DOUBLE-ASSIGNED`; appending `BADGES-SURFACE P B8` alone trips *"the map
assigns MORE rows than the ledger published"*. Three lines, and they are yours:

    delete   blocker-assignments.tsv:395   BADGES-SURFACE   P B7
    append   BADGES-SURFACE        P B8  RECON-DOC  _audit/2026-09-05-profile-rest.md  L102-L110
    append   OPEN-TO-HIRING-MODAL  P B7  RECON-DOC  _audit/2026-09-05-profile-rest.md  L102-L110

**I deliberately did NOT write a `RE_FILED` entry**, although it would have been
append-only and would have turned the verdict green. `RE_FILED` means *a later,
better-evidenced decision moved this row*; here the later decision was the
worse-evidenced one. Recording a refuted filing as a deliberate re-file prints
ACCOUNTED over a correction -- the ratchet-pointing-backwards the convention
ruling named. **Checked:** all three `B7` mentions in
`tests/test_blocker_map_is_derived.py` (466, 580, 582) are `#:` comments, so no
assertion pins it -- but run the suite.

---

## 3. `COMPANY-PAGE-SURFACE` -- OVER-COUNT (a prior wave found this first)

**Attribution before anything else.**
`_audit/2026-09-19-partial-blockers-closed.md` already measured *"14R/2W against
a published 13R/5W: one read OVER and three writes SHORT ... That is not a hole,
it is a disagreement"*, already ran the coarseness test on `network.md`'s seven
ids, and already excluded `N 51` with the line I would have wanted to write:
**"You may not cite an enumeration for what it includes and ignore what it
excludes."** It is also an open ruling request. I add one thing: it was done by
hand, and it is now **machine-derived**.

`_check_published_split.py` SKIPS this blocker by design -- `jobs.md` keys
direction by RANGE, so it cannot read a `J` row.
`scripts/_check_jobs_range_directions.py` reads those ranges:

    OVER on R   COMPANY-PAGE-SURFACE   published R13 W5   held R14 W2   short on W

19 blockers the split check could not see -> **14 readable, 5 blind**, and the
only over-run among the 14 is this one. Two committed enumerations supply the
figure: `network.md:590` *"Company pages | 33, 47, 53, 54, 101, 102, 104 (7) |
6 READ, 1 WRITE"*, plus `jobs.md` section 2's `106-114 | R` (nine reads less
`J 112`, the school row) and `85-86 | W`. 6R+8R = 14 reads; 1W+1W = 2 writes.
**The family cannot supply five writes; it contains two.**

### 3.1 The free control on my own source changed what I can claim

`network.md:590` makes **eight** family claims and I need one. Checking the
seven I do not need:

    OK   Company pages                 ids= 7 (claims  7)  R6 W1   (claims R6 W1)
    OK   Following people (read side)  ids= 4 (claims  4)  R3 W1   (claims R3 W1)
    OK   Contact import                ids= 5 (claims  5)  R0 W5   (claims R0 W5)
    OK   Reporting and hiding          ids= 7 (claims  7)  R0 W7   (claims R0 W7)
    OK   Profile-view analytics        ids= 5 (claims  5)  R5 W0   (claims R5 W0)
    OFF  People search + 13 filters    ids=18 (claims 18)  R17 W1  (claims R18 W0)
    OFF  Newsletters + hashtags        ids= 7 (claims  7)  R2 W5   (claims R3 W4)
    OFF  Groups, articles, misc follow ids=10 (claims 10)  R1 W9   (claims R2 W8)

**Three of eight direction counts are wrong, each by one. All eight ID LISTS
are right.** That is exactly the split the argument needs: the part excluding
`N 51` is the id list (8 of 8 reliable); the `6R/1W` is a direction count and is
one of the five that reconcile, re-derived here from the per-row column rather
than taken on trust. Had I leaned on the direction count alone I would have been
one wrong claim from a wrong verdict and would not have known.

---

## 4. `CONTENT-ANALYTICS-SURFACE` -- OVER-COUNT

    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py analytics
    'analytics' -- 8 of 409 frozen GAP rows, 0 UNASSIGNED

The entire pool holds **one** read of any kind (`N 61`, a hashtag row). The two
rows that could close this blocker are held elsewhere on stronger sources:
`P L4` by `readonly.py:866` (shipped code citing the census id) and `P L2` by
`LEDGER-EXPLICIT` (`2026-09-03-linkedin-gap-blockers.md:440-442`). See section 5
-- this is one half of a single two-row over-count, not an independent hole.

---

## 5. `CREATOR-HUB-SURFACE` and `POST-COMMENT-CONTROLS` -- I ATTACKED THE RULING AND ONE ATTACK FAILED

Ruling E reads: *"Both over-published neighbours are over **on R**, and both
shortfalls are **R**."*

### 5.1 `POST-COMMENT-CONTROLS`' shortfall is not R. It is W.

Published `1R/3W`, held `1R/2W` -- `M C23` (W), `M C90` (W), `M C29` (R). The
read side is **full**. The ruling's premise is false for this half.

**The verdict survives on a stronger argument than the one given.** After the
`J`-range reader, **83 of 88 published splits are watched and not one blocker is
OVER on W.** The row cannot be in a neighbour over on the shortfall's direction
because no such neighbour exists. (The five still blind --
`AI-INTERVIEW-PRODUCT`, `FILE-UPLOAD-UNSANCTIONED`, `JOBCARD-OVERFLOW-MENU`,
`OPEN-TO-WORK-MODAL`, `PANEL-NOT-OBSERVED` -- are not comment surfaces.) And
`_sweep_frozen_rows.py comment` returns 15 rows, **0 unassigned**; the four rival
comment writes are all in `COMMENT-IDENTIFIER`, COMPLETE at 4 of 4.

### 5.2 `CREATOR-HUB-SURFACE`: the neighbour DOES hold a row of its family

The ruling's test was *"Neither neighbour holds a creator-hub or comment-surface
row."* For creator-hub that is **false**: `NEWSLETTER-SURFACE` holds `P L4`
*"Newsletter analytics"*, a `profile.md` **section L** row -- and section L
membership is the whole evidence on which `P L1`, `P L7`, `P L8` were filed
here.

### 5.3 THE REFUTATION I BUILT, AND WHY IT DIED

I took it further than noting the error. The argument was:

1. `readonly.py`'s newsletter comment claims rows for the blocker in two
   explicit halves -- *"five of **this blocker's** reader-side rows (`N 55`,
   `N 56`, `N 57`, `N 58`, `M C80`)"* and five author-side (`M C50`, `M C51`,
   `M C81`, `M C84`, `P L3`). **Ten rows, `1R/9W` -- and the ledger publishes
   `1R`/11W. The READ count agrees exactly.**
2. The remaining two came from a different kind of sentence: `"/newsletters/
   <slug>/analytics/   census M C83, P L4"` sits under *"WHAT IT DOES NOT
   ADMIT"*, an ADDRESS-refusal list. The same file writes a BLOCKER NAME when it
   means a blocker (`"/search/results/events/   SEARCH-RESULTS-SURFACE again"`)
   and `"census <id>"` when it means rows.
3. So the filing's *"5 + 5 + 2 = 12"* promoted an address annotation to a third
   blocker half -- and doing so took the held reads from 1 to 3, breaking an
   agreement with the published `1R` that had been exact.

**WHAT KILLED IT.** `_audit/2026-09-19-partial-blockers-closed.md` section 3.2
already ran the mirror of this move (`M C83` out to `CONTENT-ANALYTICS-SURFACE`,
`M C82` in) and declined it on a principle I should not have needed twice:

> **"a census FAMILY groups by SUBJECT; a BLOCKER groups by WHAT BLOCKS IT."**
> Newsletter analytics is analytics by subject and a newsletter address by
> blocker. Where the two cut differently the blocker's own cost and address win.

`P L4`'s address is `/newsletters/<slug>/analytics/`. `CREATOR-HUB-SURFACE` is
priced `allowlist +1` and that is not its address. And the tracked probe
`scripts/_probe_newsletter_routes.py:117` says it in its own voice:
*"--- analytics, filed here by name and costed elsewhere ---"*. **Filed here.**

**So: over-count CONFIRMED for `CREATOR-HUB-SURFACE`, and the strongest
available attack on it is recorded as failing rather than left for the next
wave to re-run.**

### 5.4 One piece of the attack survives, and it is about the instrument

`NEWSLETTER-SURFACE` publishes `12 | 1R/11W`. The newsletter family in the
frozen 409 is **13 rows: 10 W and 3 R** (`_sweep_frozen_rows.py newsletter`).
**No subset can be `1R/11W` -- eleven writes do not exist.** So the split
check's *"`NEWSLETTER-SURFACE` OVER on R"* is a reading against a published
split the corpus cannot satisfy, not evidence that a row is misfiled. **Ruling
E's discriminator was the split; for one neighbour the split is unsatisfiable
and for the other the surplus is four rows rather than one (section 0). The
conclusion was right; the instrument under it was not load-bearing.**

### 5.5 The two over-counts are one over-count

`CONTENT-ANALYTICS-SURFACE` (5R, 4 held) and `CREATOR-HUB-SURFACE` (4R, 3 held)
are each short one read and the corpus offers **zero** unclaimed analytics
reads. The cluster -- 5R + 4R + `ANALYTICS-CONTROLS-UNPRESSED` 4R = **13
published reads** -- holds **11**. `_audit/_scratch/_would-exceed-published.tsv`
independently confirms the third is at its ceiling: it records a source naming a
*fifth* row (`N 132`) for a blocker published at 4. **Not two independent holes;
one two-row over-count counted twice.**

---

## 6. `ARTICLE-SURFACE` -- DECLINED, and I retract the discriminator I proposed

Published `1R/5W`, held `1R/4W`; the shortfall is one write.
`_sweep_frozen_rows.py article` returns 10 rows, **2 unassigned**: `N 41` and
`N 42`, both W.

**The prior wave's reason is sharper than "two candidates, one slot" and I adopt
it.** `_audit/2026-09-19-partial-blockers-closed.md`: `M C79` *"Follow **or
unfollow** member articles"* is already in this blocker; `N 41` and `N 42` are
that one row split into halves across a slice boundary, so **jointly** a
duplicate of a row already here. Taking either half alone puts half a duplicate
in a blocker holding the whole.

**Mechanised, because it was found by reading.** A pairwise Jaccard detector
cannot see this shape -- `M C79` scores **0.50** against each half, below any
useful threshold -- so
`scripts/_check_duplicate_rows_share_a_blocker.py` carries a second arm:
`tok(M C79)` is wholly **contained** in `tok(N 41) | tok(N 42)`. Its control
requires it to find this pair, and bare containment was first measured as a
coincidence generator (1217 hits) before three structural constraints cut it.

**I RETRACT A DISCRIMINATOR I HAD DRAFTED.** I was going to route this as *"the
ledger charges one `allowlist +1`; whichever half needs the article address is
forced."* That is dead: `messaging-and-content.md`'s own `C48` note records
*"**MEASURED 2026-09-19: no article read row is one pattern away** ...
`ARTICLE-SURFACE`'s single `allowlist +1` is owed **at least twice**"*. A
published cost already known to be short cannot force anything. **The route that
remains is the duplicate register, which two waves have now flagged it for.**

---

## 7. `ACCOUNT-VERIFICATION` -- DECLINED, and it is NOT an over-count

`_sweep_frozen_rows.py verif` returns 5 rows, **1 unassigned**: `J 81`. The row
exists. It is **contested**, which is a different verdict from an over-count.

**THE MAP'S OWN REASON STRING IS FALSE HERE AND I DID NOT LEAN ON IT.** The
unassigned cell reads *"no committed source names this row against any
blocker"*; `scripts/_probe_jobs_tail_boundary.py:62` does --
*"# 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83"*. For `J 78`-`J 83` that
string is an unspecialised default, not a measurement.

**And the probe earns its weight on the claims nobody needed.** It transcribes
three ranges; the two checkable ones land exactly -- `JOB-ALERTS-SURFACE`
published 7 against *"31-36, 41"* = 7, `TRACKER-ROW-MENU` published 3 against
`J54-J56` = 3. The third is the contested one and over-names by exactly one:
`PREMIUM-APPLY-SURFACES` published **5** against `J78`-`J83` = **6**. Exact
where checkable, over by one where it is not: the six-against-five is real, not
carelessness.

Three reasons not to take it:

1. **Cross-claimed.** `PREMIUM-APPLY-SURFACES` is one of the three ABSENT
   blockers, 0 of 5, and its candidate set is those six rows. Taking `J 81` is a
   cross-wave adjudication, and that wave is live.
2. **Already ruled.** `2026-09-19-the-three-ruling-requests-ruled.md:90-93` --
   *"That test is the reader's. The census's own sectioning is the source's, and
   it places `J 81` in section D, Applying. When a reader's test and the
   source's classification disagree, the source wins."*
3. **Its own filing declined it on purpose** (`blocker-assignments.tsv:401`):
   *"Taking it now would be acting ahead of my own filed request."*

**Direction cannot break the tie and I checked**: this blocker sits in the
cost-0 table, which publishes no split, so the discriminator that settled
`CONVERSATION-OVERFLOW-MENU` does not exist here.

---

## 8. THE ARITHMETIC THAT MAKES FIVE OVER-COUNTS THE EXPECTED ANSWER

A sibling measured **21 unassigned rows against 12 fillable slots, and 9 rows
for which no slot exists at all**. My eight own most of those slots, so this is
exactly where the pressure to find each one a row lives -- and it disarms the
move I would otherwise have been tempted into. *"The only unassigned row left
that could plausibly fit"* would have filed `N 51` into `COMPANY-PAGE-SURFACE`
and one of `N 41`/`N 42` into `ARTICLE-SURFACE`. **Both are declined above and
neither decline rests on the pool being empty** -- they rest on a committed id
list that excludes the row, and on a joint duplicate of a row already held.

**The two things I did positively are not that move.** `M M13` was filed on
shipped code naming the blocker's family, after the free control on that same
source was run and reported against it. `P B7` is not an unassigned row looking
for a home at all -- it is an assigned row whose filing a committed source
contradicts by enumeration, and that claim holds whether the pool is empty or
holds fifty rows.

**A negative worth recording.** `_audit/_scratch/_would-exceed-published.tsv`
enumerates rows a committed source names for a blocker that would exceed its
published count. It has two entries and **none of my eight appears**. For these
blockers the problem is not competing claimants; nobody claims the slot. (That
file is gitignored and absent from this worktree -- read it from the main
checkout. A file missing from a linked worktree is not a file that does not
exist.)

---

## What I committed

**Filed: one row.** `PER-MESSAGE-OVERFLOW-MENU  M M13`, class `RECON-DOC`,
source `linkedin_server/menus.py:187-193`. No `RE_FILED` entry was added;
section 2 says where one would have been a lie.

**Four instruments, each shown failing.**

| file | measures | control |
|---|---|---|
| `_check_jobs_range_directions.py` | a `J` row's direction, off `jobs.md`'s range groupings; 19 skipped -> 14 readable | `--control-blind` blanks a range cell and requires its rows to go UNRESOLVED; `--control-overrun` inflates a blocker the report calls "within split" and requires the table to NAME it |
| `_check_refile_destination_credit.py` | published rows masked by an incoming re-file | `--control` injects a synthetic incoming re-file at a blocker the real data does not name |
| `_sweep_frozen_rows.py` | every frozen row matching a word, with direction and holder | `--control`, both arms: a word the set contains must hit, one it cannot contain must not |
| `_check_duplicate_rows_share_a_blocker.py` | duplicate pairs sharing a blocker; and a compound row split into halves in another slice | each arm must find the pair a committed audit names by hand |

**Two of them caught me.** The range reader's first draft mapped a `R + W`
range cell to `RW` -- in a per-row table that means the row does both, in a
RANGE table it means the block contains both -- putting 5 phantom `RW` rows into
`FILE-UPLOAD-UNSANCTIONED` and 7 into `OPEN-TO-WORK-MODAL`, which then reported
OVER on a direction no row carries. The duplicate detector's containment arm
returned **1217** hits before three structural constraints cut it to a
reader-sized list.

## For the lead

1. **`P B7` is a three-line correction** (section 2.3) closing
   `OPEN-TO-HIRING-MODAL` at 5 of 5, keeping `BADGES-SURFACE` at 5 of 5, and
   retiring the `B8`/`K9` coin-flip. It needs a delete, so it is not mine.
2. **Run `--write`.** One test is red, on the one row I filed, by design.
3. **`complete` is overstated by two** (section 0). Fixing it means debiting a
   destination for incoming rows -- a change to the verdict logic, not to
   `RE_FILED`.
4. **The ledger's per-blocker counts are wrong in BOTH directions.** Five of my
   eight are over-counts against enumerated, closed families; a sibling found
   four blockers published ONE SHORT of their family. That is a better
   explanation for a chunk of the 20 unassigned than a lost classifier.
5. **Two stay open on purpose**, and the honest route for `ARTICLE-SURFACE` is
   the duplicate register, not the address measurement I drafted and retracted.
