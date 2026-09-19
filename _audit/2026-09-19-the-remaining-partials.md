# The eight blockers still PARTIAL, and what each one actually is

**Measured at `201b757` and re-measured at `0adc21d`. Every number below is
reproducible from a committed script; the commands are named at each claim.**

Headline: **one of the eight is a filing error next door, five are ledger
over-counts, two are contested two-way picks that stay open.** Zero rows were
filed. The most valuable finding is not in the eight at all -- it is that
`RE_FILED` credits a re-file's DESTINATION for a row it never published, which
makes two blockers print COMPLETE while short.

| blocker | pub | held | verdict |
|---|---|---|---|
| `COMPANY-PAGE-SURFACE` | 18 | 16 | **OVER-COUNT**, refuted on the split by two committed enumerations |
| `ARTICLE-SURFACE` | 6 | 5 | **DECLINED** -- two candidates, one slot, discriminator named |
| `CONTENT-ANALYTICS-SURFACE` | 5 | 4 | **OVER-COUNT** -- family closed, 8 of 8 filed |
| `OPEN-TO-HIRING-MODAL` | 5 | 4 | **REFUTED FILING** -- `P B7`, misfiled into `BADGES-SURFACE` |
| `CREATOR-HUB-SURFACE` | 4 | 3 | over-count **CONFIRMED, spine replaced** |
| `POST-COMMENT-CONTROLS` | 4 | 3 | over-count **CONFIRMED, ruling E's stated reason is wrong** |
| `ACCOUNT-VERIFICATION` | 3 | 2 | **DECLINED** -- sole candidate cross-claimed and already ruled |
| `PER-MESSAGE-OVERFLOW-MENU` | 2 | 1 | **DECLINED** -- sole candidate admitted by resemblance only |

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
published rows are masked and `complete 86` is overstated by two. No count
assertion could have caught it: a re-file is count-neutral across the pair,
which is the same structural blindness `_check_published_split.py` exists for,
one level up.

**This is load-bearing for section E below**, because ruling E's second test
was *"`SEARCH-RESULTS-SURFACE`'s surplus read is `N 194`"*. The surplus is not
one row. It is four incoming rows masking four outgoing holes, and the split
saw one of them.

---

## A. `COMPANY-PAGE-SURFACE` -- 18 pub / 16 held -- LEDGER OVER-COUNT

**The count is short two and the SPLIT is wrong in both directions at once,
which is why no assertion has ever seen it.** `_check_published_split.py` skips
this blocker by design -- `jobs.md` keys direction by RANGE, so it cannot read
a `J` row. `scripts/_check_jobs_range_directions.py` (committed `da72649`)
reads those ranges:

    OVER on R   COMPANY-PAGE-SURFACE   published R13 W5   held R14 W2   short on W

**Two committed row-id enumerations say the ledger's `13R/5W` is not what the
corpus holds.**

1. `_audit/_census/network.md:590` -- the slice's own family table:
   *"**Company pages** | 33, 47, 53, 54, 101, 102, 104 (7) | 6 READ, 1 WRITE"*.
   Seven rows by id, six reads and **one** write. The map holds exactly those
   seven.
2. `_audit/_census/jobs.md` section 2 -- *"106-114 | company and school Page
   tabs, Premium insights | ... Largest single block of pure-read GAPs on this
   census (9 rows) | R"*, and *"85-86 | undo a dismissal, "I'm interested" |
   posting-card and company-page controls | W"*. Nine reads of which `J 112`
   is the school row (`SCHOOL-PAGE-SURFACE`, COMPLETE 3/3), leaving eight; plus
   `J 86` as the one write.

6R + 8R = **14 reads**. 1W + 1W = **2 writes**. The ledger published 13R/5W.
**The family the census enumerates cannot supply five writes; it contains two.**

### A.1 The free control on my own source, and it changed what I can claim

`network.md:590` is a table of **eight** family claims and I need **one**.
Checking the seven I do not need prices the one I do. Each claim is an id list
plus a direction count, both checkable against the census's own `R/W` column:

    OK   Company pages                 ids= 7 (claims  7)  R6 W1   (claims R6 W1)
    OK   Following people (read side)  ids= 4 (claims  4)  R3 W1   (claims R3 W1)
    OK   Contact import                ids= 5 (claims  5)  R0 W5   (claims R0 W5)
    OK   Reporting and hiding          ids= 7 (claims  7)  R0 W7   (claims R0 W7)
    OK   Profile-view analytics        ids= 5 (claims  5)  R5 W0   (claims R5 W0)
    OFF  People search + 13 filters    ids=18 (claims 18)  R17 W1  (claims R18 W0)
    OFF  Newsletters + hashtags        ids= 7 (claims  7)  R2 W5   (claims R3 W4)
    OFF  Groups, articles, misc follow ids=10 (claims 10)  R1 W9   (claims R2 W8)

**Three of the eight direction counts are wrong, every one by exactly one. All
eight ID LISTS are right.** So the table is reliable for *which rows are in a
family* and only 5-of-8 reliable for *how many read and how many write*.

That is precisely the split my argument needs, and it survives:

* The part that **excludes `N 51`** is the id list -- 8 of 8 reliable.
* The part that supplies **6R/1W** is a direction count -- and it is one of the
  five that reconcile, checked here against the per-row column rather than
  taken from the table.

**Had I leaned on the direction count alone I would have been one wrong claim
away from a wrong verdict, and I would not have known.** The seven claims I did
not need are what told me which half of the source to trust.

**The one unassigned candidate is refused, and named.**
`./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py "company"` returns
`N 51` *"Mute a company"* as the only unassigned company-shaped write. It is
refused on the same table that admitted the other seven: `network.md:590` puts
`N 51` in *"Groups, articles, misc follow | 37, 41, 42, 43, 49, 50, 51, 63, 64,
76"*, not in the Company pages family. Its census cell reads *"REV. `mute` 0
hits"* -- a tool gap, where every company-page row in this blocker carries
*"No `/company/`"*, the address gap the blocker is priced for.
`_audit/2026-09-19-routing-the-unassigned.md:122` reaches the same place
independently: *"no blocker is named for mute"*.

**VERDICT: LEDGER OVER-COUNT of two, evidenced by enumeration rather than by
exhaustion of search.** The ledger over-published this blocker's write side by
three and under-published its read side by one; the two errors partly cancel,
which is why the count shows only `-2`.

---

## B. `ARTICLE-SURFACE` -- 6 pub / 5 held -- DECLINED, and the discriminator is named

Published `1R/5W`; held `1R/4W`. The shortfall is **one write**.

`./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py article` returns 10
frozen-GAP rows, **2 unassigned**: `N 41` *"Follow a member from one of their
articles"* and `N 42` *"Unfollow the articles of a member you are not connected
to"*. Both are writes. **Two candidates, one slot.**

The messaging slice's article rows are exhausted: `C46 C48 C49 C78 C79` are
held, `C36` is `SAVED-POSTS-SURFACE`, `C45` is `FILE-UPLOAD-UNSANCTIONED`,
`C76` is `COLLABORATIVE-CONTENT`. So the sixth published row is a write from
outside messaging, and only these two exist.

**I am not picking.** A wrong pick here is not the harmless kind -- it sends a
wave to the wrong surface, which is the standard the `B8`/`K9` ruling set and
the reason `M35` and `J 81` were left open. The two committed readings point
opposite ways and neither settles it:

* `_audit/2026-09-19-unfired-but-built.md:118` groups *"`N 37`, `N 40`, `N 41`,
  `N 42` | follow / unfollow a **PERSON**"* -- which argues both are
  person-follow rows, not article-surface rows.
* `_audit/2026-09-19-routing-the-unassigned.md:200` calls them *"cross-slice
  duplicates of `C79`"* and parks them under the standing duplicate hold.
  Measured here, they are not: against `C79` *"Follow or unfollow member
  articles"* both score Jaccard **0.50**, under the 0.55 threshold at which the
  detector in section D finds every pair the corpus is known to contain. `C79`
  is one compound row; these are two narrower ones.

**THE DISCRIMINATOR IS LEXICAL AND CHEAP, and it is the one that unstuck
`INVITATION-SUBSTRING-BLOCKED`.** The ledger charges this blocker **one**
`allowlist +1`. So: what address does each capability require? `N 41`'s act
happens on an article page, the same address the blocker's other five rows
already need and the same one the single `allowlist +1` buys. If `N 42`'s
unfollow lives at a different address, the published cost forces `N 41` and the
pick stops being a guess. **Routed as a measurement, not filed.**

---

## C. `CONTENT-ANALYTICS-SURFACE` -- 5 pub / 4 held -- LEDGER OVER-COUNT

Published `5R`; held `4R`. The shortfall is **one read**.

    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py analytics
    'analytics' -- 8 of 409 frozen GAP rows, 0 UNASSIGNED
    -> every row naming 'analytics' is filed; the pool holds none

The whole pool contains exactly **one** read of any kind (`N 61`, *"View your
followed hashtags"*), and it is a hashtag row. There is no analytics read left
to find.

The two rows that could close this blocker are held elsewhere **on stronger
sources than any claim this blocker can make**:

* `P L4` *"Newsletter analytics"* -> `NEWSLETTER-SURFACE`, on shipped package
  code naming the row id: `linkedin_server/readonly.py:725-765`, refusal list
  entry *"/newsletters/<slug>/analytics/ census M C83, P L4"*.
* `P L2` *"Own follower count and follower list"* -> `PARSER-ON-A-LOADED-PAGE`,
  class `LEDGER-EXPLICIT` -- the ledger itself names both its rows at
  `2026-09-03-linkedin-gap-blockers.md:440-442`.

**VERDICT: LEDGER OVER-COUNT of one.** And see section E: this is not an
independent hole. It is one half of a single two-row over-count.

---

## D. `OPEN-TO-HIRING-MODAL` -- 5 pub / 4 held -- THE ROW EXISTS AND IS MISFILED

**This is the one that is not an over-count, and it is the most consequential
thing in this file after section 0.**

Published `1R/4W`; held `1R/3W`; the shortfall is **one write**. The blocker's
namesake census section, `profile.md` *"### J. Open To Hiring (4)"*, contains
exactly four rows -- `J1 J2 J3` (W) and `J4` (R) -- and **all four are held**.
So the fifth published row is a write outside section J.

    ./venv/Scripts/python.exe scripts/_sweep_frozen_rows.py hiring
    'hiring' -- 8 of 409 frozen GAP rows, 0 UNASSIGNED

Exactly one write outside section J names `#Hiring`: **`P B7` "#Hiring photo
frame apply / remove"**, currently filed to `BADGES-SURFACE`. It is the
near-twin of held `P J2` *"#Hiring photo frame add / remove"* -- Jaccard 0.67,
and one of only six near-duplicate pairs in the frozen 409 that are **split
across two blockers**.

### D.1 Its current filing says outright that it is not evidence-led

`_audit/_census/blocker-assignments.tsv:395` files `P B7` to `BADGES-SURFACE`.
The note on the sibling line says it plainly:

> *"`B7` IS ADMITTED BY THE ARITHMETIC RATHER THAN BY RESEMBLANCE, and that is
> worth saying because "#Hiring photo frame apply / remove" does not read like a
> badge. It is section B's FRAMES entry. But the published 3W cannot be filled
> without it ... The count admits it; I would not have on the name."*

That arithmetic has exactly one load-bearing premise: that `B8` and `K9`
*"collapse to one slot"*, i.e. that one blocker cannot hold two frozen-GAP rows
of the same capability. **Drop the premise and `B7` is not needed.**

### D.2 The premise is refuted twice over

**(i) By a committed enumeration that predates the filing by two weeks.**
`_audit/2026-09-05-profile-rest.md:102-110` sets out
*"## 2. ROW 43 `BADGES-SURFACE` -- what the five rows actually are"* and lists
them: **`K8` (R), `K10` (R), `K9` (W), `B8` (W), `B9` (W)**. Five rows, `2R/3W`,
the published split exactly -- **with no `B7` and no collapse required.** It
then argues the ledger over-counted by one because `B8 == K9`, a complaint that
only makes sense if the ledger's five contained BOTH -- which excludes `B7`.

**(ii) By measurement.** A near-duplicate detector over all 409 frozen rows
(Jaccard >= 0.55 on capability tokens, control: it must find the `M C83`/`P L4`
pair the five-requests ruling names by hand -- it does) finds **23 pairs, 15 of
them filed to ONE blocker, 5 of those intra-slice**:

    M C50 / M C81   INTRA   both NEWSLETTER-SURFACE     Create a newsletter / Create a Newsletter Page
    J 118 / J 119   INTRA   both MATCH-DETAILS-COLLAPSED
    P I14 / P I15   INTRA   both OPEN-TO-WORK-MODAL
    N  84 / N  87   INTRA   both SEARCH-RESULTS-SURFACE
    N  A7 / N  A8   INTRA   both ADMIN-RIGHTS-NOT-HELD

**Two rows of one capability sharing a blocker is the ledger's ordinary
behaviour, intra-slice included.** Nothing forces `B8` and `K9` into one slot.

### D.3 What follows, and what I did not do

With `B7` removed, both blockers close on their published splits with nothing
left over and nothing missing:

    BADGES-SURFACE          K8(R) K10(R)  B8(W) B9(W) K9(W)   = 2R/3W = published
    OPEN-TO-HIRING-MODAL    J4(R)         J1 J2 J3(W) B7(W)   = 1R/4W = published

A second wave reached the same conclusion independently:
`_audit/2026-09-19-routing-the-unassigned.md:211` -- *"`P B7` is a `#Hiring` row
sitting in `BADGES-SURFACE` on a count-admission the ruling itself flagged.
Filed as a ruling request."*

**AND IT DISSOLVES A RULING RATHER THAN OVERTURNING ONE.** Request 3 of
`_audit/2026-09-19-the-three-ruling-requests-ruled.md:400` picked `K9` over `B8`
and recorded itself as *"A PICK ON A WEAK TIEBREAK ... Anything citing this line
as authority for resolving a duplicate is citing a coin-flip."* That coin-flip
existed **only because `B7` had consumed a write slot**. With `B7` where it
belongs, both `B8` and `K9` are in and there is no tiebreak to lose.

**I FILED NOTHING, AND THE REASON IS MECHANICAL, NOT CAUTIOUS.** The correction
is a SWAP and my mandate is append-only. Appending `OPEN-TO-HIRING-MODAL P B7`
would trip the map's `DOUBLE-ASSIGNED` assertion; appending `BADGES-SURFACE
P B8` alone would trip *"the map assigns MORE rows than the ledger published"*.
The fix is three lines and it is the lead's:

    delete   blocker-assignments.tsv:395   BADGES-SURFACE   P B7
    append   BADGES-SURFACE          P B8   RECON-DOC   _audit/2026-09-05-profile-rest.md   L102-L110
    append   OPEN-TO-HIRING-MODAL    P B7   RECON-DOC   _audit/2026-09-05-profile-rest.md   L102-L110

**I DELIBERATELY DID NOT WRITE A `RE_FILED` ENTRY FOR IT**, although that would
have been append-only and would have turned the verdict green. `RE_FILED` means
*a later, better-evidenced decision moved this row*. Here the later decision was
the worse-evidenced one. Recording a refuted filing as a deliberate re-file
would print ACCOUNTED over a correction and is exactly the ratchet-pointing-
backwards the convention ruling named.

**Checked before proposing it:** every mention of `B7` in
`tests/test_blocker_map_is_derived.py` (lines 466, 580, 582) is a `#:` comment.
No assertion pins `B7` to `BADGES-SURFACE`, so the swap does not red the suite --
but run it.

---

## E. `CREATOR-HUB-SURFACE` and `POST-COMMENT-CONTROLS` -- the ruling I was asked to break

**Both verdicts stand. Both stated reasons are wrong, and one of them is wrong
about a fact anybody can check.**

Ruling E (`_audit/2026-09-19-the-five-requests-ruled.md`) reads: *"Both
over-published neighbours are over **on R**, and both shortfalls are **R**."*

### E.1 `POST-COMMENT-CONTROLS`' shortfall is not R. It is W.

Published `1R/3W`. Held `1R/2W` -- `M C23` (W), `M C90` (W), `M C29` (R). The
read side is **full**; the write side is short one. The ruling's premise is
false for this half of it.

**The verdict survives, on a stronger argument than the one given.** After the
`J`-range reader, **83 of the 88 published splits are watched, and not one
blocker anywhere is OVER on W.** The row cannot be sitting in a neighbour that
is over on the shortfall's direction, because no such neighbour exists. (The
five still blind are `AI-INTERVIEW-PRODUCT`, `FILE-UPLOAD-UNSANCTIONED`,
`JOBCARD-OVERFLOW-MENU`, `OPEN-TO-WORK-MODAL`, `PANEL-NOT-OBSERVED` -- none is a
comment surface.)

And the family is closed: `_sweep_frozen_rows.py comment` returns 15 rows,
**0 unassigned**; the four rival comment writes are all in `COMMENT-IDENTIFIER`,
COMPLETE at 4 of 4. **OVER-COUNT CONFIRMED.**

### E.2 `CREATOR-HUB-SURFACE`'s neighbour DOES hold a row of its family

The ruling's test was *"Neither neighbour holds a creator-hub or comment-surface
row."* For creator-hub that is **false**. `NEWSLETTER-SURFACE` holds `P L4`
*"Newsletter analytics"* -- a `profile.md` **section L** row, and section L
membership is the entire evidence on which `P L1`, `P L7` and `P L8` were filed
to `CREATOR-HUB-SURFACE`. The neighbour holds a row of exactly this family.

**The verdict still stands, on the ground the ruling should have used:** `P L4`
is not filed to `NEWSLETTER-SURFACE` by section membership but by
`readonly.py:725-765`, shipped package code naming the row id. Section
membership does not overturn shipped code that names the row. Nor does it
overturn `LEDGER-EXPLICIT`, which is what holds the other candidate, `P L2`.

### E.3 And the discriminator the ruling used is unsound for that neighbour

`NEWSLETTER-SURFACE` publishes `12` rows at `1R/11W`. The newsletter family in
the frozen 409 is **13 rows: 10 W and 3 R** (`_sweep_frozen_rows.py newsletter`).
**No subset of it can be `1R/11W` -- eleven writes do not exist.** The shipped
code's own enumeration of this blocker totals 12 and contains three reads.

So the split check's *"`NEWSLETTER-SURFACE` OVER on R"* is a reading against a
published split the corpus cannot satisfy, not evidence that a row is misfiled.
**Ruling E's discriminator was the split, and for one of its two neighbours the
split is unsatisfiable; for the other (section 0) the surplus is four rows, not
one.** The conclusion was right. The instrument it leaned on was not load-bearing.

### E.4 The two over-counts are one over-count

`CONTENT-ANALYTICS-SURFACE` (5R, 4 held) and `CREATOR-HUB-SURFACE` (4R, 3 held)
are each short one read, and the corpus offers **zero** unclaimed analytics
reads for either. The analytics cluster --
`CONTENT-ANALYTICS-SURFACE` 5R + `CREATOR-HUB-SURFACE` 4R +
`ANALYTICS-CONTROLS-UNPRESSED` 4R = **13 published reads** -- holds **11**, and
every other analytics read in the corpus is filed on shipped code or on the
ledger itself. **These are not two independent holes. They are one two-row
over-count in one family, counted twice.**

---

## F. `ACCOUNT-VERIFICATION` -- 3 pub / 2 held -- DECLINED, and it is NOT an over-count

`_sweep_frozen_rows.py verif` returns 5 rows, **1 unassigned**: `J 81` *"Verify
account to raise the Easy Apply daily limit"*. The row exists. It is not
missing; it is **contested**, and that is a different verdict from an
over-count.

**THE MAP'S OWN REASON STRING IS FALSE HERE AND I DID NOT LEAN ON IT.** The
unassigned cell reads *"no committed source names this row against any
blocker"*; a tracked probe does -- `scripts/_probe_jobs_tail_boundary.py:62`,
*"# 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83"*. For `J 78`-`J 83` that
string is an unspecialised default, not a measurement, and it is not evidence of
absence.

**And the probe earns its weight on the claims nobody needed.** It transcribes
three row ranges; two are checkable against the ledger and land exactly --
`JOB-ALERTS-SURFACE` published 7 against *"31-36, 41"* = 7, `TRACKER-ROW-MENU`
published 3 against *"J54-J56"* = 3. The third is the contested one and
over-names by exactly one: `PREMIUM-APPLY-SURFACES` published **5** against
`J78`-`J83` = **6**. A transcriber that is exact where it can be checked and
over-names by one where it cannot is telling you the six-against-five is real,
not that it was careless.

Three reasons not to take it, in ascending order of weight:

1. It is cross-claimed. `PREMIUM-APPLY-SURFACES` is one of the three ABSENT
   blockers -- 0 of 5 -- and its candidate set is `J 78`-`J 83`, six rows, all
   six of them in the unassigned pool. Taking `J 81` is a cross-wave
   adjudication, not a recovery, and that wave is live.
2. A committed ruling already weighed the subject test and rejected it:
   `_audit/2026-09-19-the-three-ruling-requests-ruled.md:90-93` --
   *"The recommendation was to drop `J 81` on a subject test ... **That test is
   the reader's. The census's own sectioning is the source's, and it places
   `J 81` in section D, Applying.** When a reader's test and the source's
   classification disagree, the source wins."*
3. The blocker's own filing declined it on purpose and said why
   (`blocker-assignments.tsv:401`): *"Taking it now would be acting ahead of my
   own filed request."*

**Direction cannot break the tie here and I checked**: this blocker sits in the
ledger's cost-0 table, which publishes no `R/W` split at all, so the
discriminator that settled `CONVERSATION-OVERFLOW-MENU` does not exist for it.
2 of 3, and the third is a live contest between two waves.

---

## G. `PER-MESSAGE-OVERFLOW-MENU` -- 2 pub / 1 held -- DECLINED

Published `2W`; held `M M11` *"Edit a sent message (60-min window)"*, whose
census cell names this blocker verbatim: *"per-message overflow menu, never
opened"*.

**The obvious twin is not available and that is a measured fact, not an
oversight.** `M M12` *"Delete a sent message (60-min window)"* -- same Help
article `a550661`, same window, the other classic item of that menu -- was
already `EXCLUDED-RULED` when the census froze, so **it is not among the 409**
and cannot be this blocker's second row.

That leaves `M M13` *"Forward a message"* as the only remaining `M`-block write
(`M14`-`M18` are `FILE-UPLOAD-UNSANCTIONED`/`PICKER-SURFACES`, `M10` is
`THREAD-REPLY-BOX`, `M19` is `VOICE-CAPTURE`). Its census cell reads *"never
named; forwards a third party's words to another third party"* -- it does not
name this menu or any other. **Admitting it would be filing on my own knowledge
of LinkedIn's UI, which is not a committed source**, and
`_audit/2026-09-19-the-empty-blockers.md:235` already recorded the same
objection: *"candidate (`M13`) is admitted by resemblance, not by any source
that names the"* it.

`_sweep_frozen_rows.py overflow` returns **0** frozen-GAP rows -- the word lives
in reason cells, never in a capability -- so there is no lexical candidate of
any kind beyond `M13`.

**ROUTED AS A MEASUREMENT.** The messaging census names the cure for its own
neighbour at `messaging-and-content.md:498`: *"One capture of an open
conversation overflow menu would settle eleven rows at once."* The per-MESSAGE
menu is the same class and one capture settles this blocker's second row either
way. 1 of 2, declined rather than guessed.

---

---

## H. THE ARITHMETIC THAT SAYS FIVE OVER-COUNTS IS THE EXPECTED ANSWER

A sibling measured the shape of the residue: **21 unassigned rows against 12
fillable slots, and 9 rows for which no slot exists at all.** On the most
conservative count it is 14 slots against 21 rows. My eight own most of those
slots, so this is exactly where the pressure to find each one a row lives.

**It predicts what I found.** Five of eight are over-counts. And it disarms the
one move I would otherwise have been tempted into: *"this is the only
unassigned row left that could plausibly fit"* is unsound when nine rows have
no slot anywhere -- a single plausible candidate is the shape of a coincidence,
not of a match. That reasoning would have filed `N 51` into
`COMPANY-PAGE-SURFACE`, `M M13` into `PER-MESSAGE-OVERFLOW-MENU`, and one of
`N 41`/`N 42` into `ARTICLE-SURFACE`. **All three are declined above and none of
the declines rests on the pool being empty** -- they rest on a committed id list
that excludes the row (A), on a cell that names no menu (G), and on a live
two-way contest (B).

**Section D is not that move, and the distinction is the whole reason it is
worth acting on.** `P B7` is not an unassigned row looking for a home. It is an
ASSIGNED row whose filing a committed source, two weeks older than the filing,
contradicts by enumeration. The claim is documentary, not arithmetical: it
would hold if the pool were empty and it would hold if the pool held fifty rows.

**A negative worth recording.** `_audit/_scratch/_would-exceed-published.tsv`
enumerates rows a committed source names for a blocker that would exceed its
published count. It holds two entries, both `ANALYTICS-CONTROLS-UNPRESSED`
(`J 28`, `N 132`), and **not one of my eight appears in it.** For these
blockers the problem is not competing claimants; it is that nobody claims the
slot. (That file is gitignored and absent from this worktree -- read from the
main checkout. A file missing from a linked worktree is not a file that does
not exist, which is the same trap that silently disarmed the identity guard
earlier today.) It also independently confirms the ceiling section E.4 leans
on: `ANALYTICS-CONTROLS-UNPRESSED` is full at 4 of 4 and a fifth claimant
already exists, so it cannot absorb `CONTENT-ANALYTICS-SURFACE`'s or
`CREATOR-HUB-SURFACE`'s missing read.

---

## What I filed, and what I changed

**Filed: nothing.** No row was added to `blocker-assignments.tsv` and no entry
was added to `RE_FILED`. Section D explains the one case where an append would
have turned a verdict green and why it would have been a lie.

**Committed: three instruments, each shown failing.**

| file | what it measures | control |
|---|---|---|
| `scripts/_check_jobs_range_directions.py` | direction of a `J` row, off `jobs.md`'s range groupings. 19 blockers the split check skipped -> 14 readable, 5 blind | `--control-blind` blanks a range's direction cell and requires its rows to go UNRESOLVED; `--control-overrun` inflates a blocker the report calls "within split" and requires the table to NAME it |
| `scripts/_check_refile_destination_credit.py` | published rows masked by an incoming re-file | `--control` injects a synthetic incoming re-file at a blocker the real data does not name |
| `scripts/_sweep_frozen_rows.py` | every frozen-GAP row matching a word, with direction and holder | `--control`, both arms: a word the set contains must hit, one it cannot contain must not |

**One of them caught me.** The first draft of the range reader mapped a
`R + W` range cell to `RW`, which put 5 phantom `RW` rows into
`FILE-UPLOAD-UNSANCTIONED` and 7 into `OPEN-TO-WORK-MODAL`; both then reported
OVER on a direction no row carries. In the per-row census tables `R/W` means
that row does both; in a RANGE table it means the block contains both. The
reader now resolves nothing from a compound cell and prints how many rows that
costs.

## For the lead

1. **`P B7` is a three-line correction** (section D.3) that closes
   `OPEN-TO-HIRING-MODAL` at 5 of 5, keeps `BADGES-SURFACE` at 5 of 5, and
   retires the `B8`/`K9` coin-flip. It needs a delete, so it is not mine.
2. **`complete 86` is overstated by two** (section 0) and two COMPLETE verdicts
   are false. Fixing it means debiting a destination for incoming rows -- a
   change to `build_blocker_map.py`'s verdict logic, not to `RE_FILED`.
3. **Five of the eight are ledger over-counts** against a corpus whose families
   are enumerated and closed. Combined with
   `_audit/2026-09-19-routing-the-unassigned.md`'s mirror finding -- four
   blockers published ONE SHORT of their family -- the ledger's per-blocker
   counts are wrong in both directions, and that is a better explanation for a
   chunk of the 21 unassigned than a lost classifier.
4. **Two stay open on purpose** (`ARTICLE-SURFACE`, `PER-MESSAGE-OVERFLOW-MENU`)
   and each has a named, cheap measurement that ends it: one address question,
   one menu capture.
