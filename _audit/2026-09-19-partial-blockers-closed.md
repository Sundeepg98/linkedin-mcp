# The thirteen PARTIAL blockers, worked blocker-first

**ONE ROW FILED, TWELVE DECLINED, AND THE DECLINES ARE THE RESULT.** Sixteen
holes were in scope. One is closed. **Every one of the remaining fifteen now
carries a NAMED reason no unassigned row goes into it**, and for four of them the
row the published count expects has been identified outright -- it is already in
this map, under the blocker that later claimed it.

Two findings here are about the ARTIFACT rather than the rows, and both change
what a future pass should do: a blocker reading PARTIAL does not mean a row was
lost (section 1), and the *"at least two holes cannot be filled"* bound that
closed the previous pass **is zero, and is zero by construction** (section 5).

    UNASSIGNED           24  ->  23
    complete blockers    80  ->  81
    partial blockers     13  ->  12
    map                  409 data lines, 409 frozen rows, no duplicate row_id
    tests/test_blocker_map_is_derived.py                          7 passed

Arrival reading, taken by me before any edit, `262bab6`:

    frozen GAP rows at 1c08e5f     409
    assigned from committed sources     385
    UNASSIGNED                           24
    ledger blockers parsed              97  rows 409

**It matched the brief exactly**, so nothing here works from a different tree.

**TWO CORRECTIONS TO THE BRIEF, RECORDED BECAUSE ONE OF THEM COULD HAVE COST A
SEARCH AND DID NOT.** (1) The brief said an unassigned row shows as an EMPTY
column 2; it does not, it carries the literal `UNASSIGNED`, and a filter on
emptiness returns nothing SILENTLY. I used `$2=="UNASSIGNED"` from my first
extraction, so the pool I worked was the right 24. (2) The brief framed the
partial shortfall (16) plus the absent blockers' rows (8) as *"the same 24 rows
viewed two ways"*, and a later correction called the match a coincidence.
**Neither is right, and section 5 shows why: the two totals are an IDENTITY,
forced equal by the builder's own assertions -- while the MATCHING between holes
and rows genuinely fails.** The correction's substance is right and its
arithmetic is not, and the distinction is load-bearing: it is precisely because
the totals must balance that they can never report the mismatch.
(The worktree carries no `venv/` -- it is gitignored -- so the interpreter used
throughout is the main checkout's `venv/Scripts/python.exe` running the
worktree's own copy of each script, which resolves `ROOT` from `__file__` and
therefore reads and writes this worktree.)

---

## 1. THE HEADLINE, AND IT IS ABOUT THE ARTIFACT RATHER THAN THE ROWS

**A blocker reading PARTIAL is AMBIGUOUS between two completely different facts,
and the map has no column that tells them apart:**

1. a published row was **lost** -- nobody can say which row it was; or
2. a published row was **RE-FILED OUT** to another blocker by a later committed
   document, and **the map still holds it, under its new name.**

Case 2 is not a hole. Nothing is missing, nothing can be added, and a wave sent
to "close" it will burn itself looking for a row that is sitting two lines away
in the same file.

**Measured in my thirteen: case 2 accounts for four of the sixteen holes
outright, and the direction arithmetic confirms every one of them on the nose.**

| blocker | short by | the row(s) the published count expects | where the map has it now | confirmed by |
|---|---|---|---|---|
| `GROUPS-SURFACE` | 2, **both READS** | `N 161`, `M C70` -- both **R** | `SEARCH-RESULTS-SURFACE` | W side is FULL, 20 of 20 |
| `EVENTS-SURFACE` | 1, **a READ** | `N 179` -- **R** | `SEARCH-RESULTS-SURFACE` | W side is FULL, 11 of 11 |
| `HASHTAG-EXISTENCE` | 1 (2 on the ledger's own reading) | `N 194` (**R**), `M C52` (**W**) | `SEARCH-RESULTS-SURFACE`, `FEED-PREFERENCES` | the three ids' directions reproduce the published `1R/2W` exactly |

**Why the direction check is what makes this a finding and not a story.** Each
of those three blockers is short on exactly ONE side of its published split, and
the rows that left carry exactly that direction. `GROUPS-SURFACE` publishes
`12R/20W`; the map holds `10R/20W`; the two carved out are both reads. A wrong
guess would have had to land on the right side twice.

**Two of the three carve-outs are concessions by the losing side**, which is the
strongest shape a re-file can have:

* `_audit/2026-09-05-groups-surface-measured.md` table 5.4, about
  `GROUPS-SURFACE`, giving two rows away: *"`N 161`, `M C70` | search inside
  Groups -- `/search/results/groups/` belongs to `SEARCH-RESULTS-SURFACE`, which
  is queued DECIDE and is **not this blocker's to inherit**"*.
* `_audit/2026-09-05-events-surface-recosted.md` L252, about `EVENTS-SURFACE`,
  giving one away: `N 179` *"MISFILED ... It is not blocked by the events
  surface."*

**THE RECEIVING BLOCKER ABSORBS THEM AND STILL CLOSES**, which is the check that
the bookkeeping is honest rather than double-counted: `SEARCH-RESULTS-SURFACE`
holds all four carve-ins (`N 161`, `N 179`, `N 194`, `M C70`) and is COMPLETE at
21 of 21, because `N 95` and `N 96` were carved BACK to `SEARCH-HISTORY-SURFACE`,
which publishes 2 and is COMPLETE holding exactly those two.

### The `HASHTAG-EXISTENCE` case is the sharpest, and it also convicts a filed row

**The ledger's own body enumerates this blocker's three published rows**, which
is `LEDGER-EXPLICIT` -- the strongest class in this corpus, the lost classifier's
author writing about the division he published. `_audit/2026-09-03-linkedin-gap-
blockers.md` L1171-L1180, under the sentence *"The three rows do not share a
blocker:"*, tables them:

| row | as published | at HEAD |
|---|---|---|
| `N 194` | `HASHTAG-EXISTENCE` | `SEARCH-RESULTS-SURFACE` |
| `C 11` | `HASHTAG-EXISTENCE` | EXCLUDED-RULED |
| `C 52` | `HASHTAG-EXISTENCE` | `HASHTAG-EXISTENCE`, unchanged |

and concludes *"So `HASHTAG-EXISTENCE` becomes a ONE-ROW blocker."*

**Their directions, read off the census row tables, are `N 194` R, `M C11` W,
`M C52` W -- which is the published `1R/2W`, exactly.** Three ids named by the
author, reproducing the published split with no residue. That is as close to the
lost classifier as this repository gets.

**CONSEQUENCE, AND I AM REPORTING IT RATHER THAN ACTING ON IT.** The map
currently carries `N 61` here on `RECON-DOC` (`network.md` L292-L294), admitted
on the reasoning *"three hashtag rows carry EXISTENCE UNCERTAIN; `N 61` is the
only R"*. `N 61` is **not one of the three the ledger names**, and it occupies
the R slot that the ledger gives to `N 194`. The two readings cannot both be
right.

**I did not remove it, and the reason is a real ambiguity rather than caution.**
This artifact mixes two conventions without declaring either:

* `N 194` and `M C52` are filed **AT HEAD** (under the blockers that later
  claimed them), while the counts they are checked against are **AS PUBLISHED**.
* Under the at-head convention `N 61` in `HASHTAG-EXISTENCE` is defensible: it
  carries the existence-uncertainty cell the blocker is named for.
* Under the as-published convention it is refuted outright.

**The convention ambiguity is the defect, not the row.** It is also the
mechanism behind section 1's whole finding: a map that records at-head filings
and checks them against as-published counts will manufacture a PARTIAL for every
re-file that ever happened, permanently, and no amount of searching will close
one. **Ruling request A below.**

---

## 2. WHAT I FILED -- ONE ROW

### `THREAD-REPLY-BOX` 1 -> 2 of 2, COMPLETE: `M M47`

Commit `5047e8d`. `LEDGER-AMENDMENT`, `_audit/2026-09-03-linkedin-gap-
blockers.md` L758-L764.

**The ledger pairs this row with the row already filed here.** Amendment A23 is
about commit `81c5c9b`, which *"added `read_thread_reply_surface` to `dom.py`"*.
It names the two rows that reader does NOT close, and moves this blocker's cost
in the same breath:

> *"`M10` and `M47` stay GAP. What changed is the cost: `THREAD-REPLY-BOX`'s
> capture is paid, so it drops from 6 to 5 -- and `M47`, responding to an inbound
> Recruiter InMail ... is now the nearest write in the package that needs no
> address at all."*

**Two further committed sources pair the same two ids, neither written by me:**

1. `_audit/2026-09-05-routes-already-admitted.md` L175 tables the address
   `/messaging/thread/<id>/` against *"`M M47`, `M M10` and the per-message
   menu"* -- and separates BOTH from the per-message menu, which is where
   `M M11` sits. The same document already supplies four assignments this map
   trusts.
2. **Tracked code.** `scripts/_probe_route_vs_surface.py` L103 probes the literal
   tuple `("M M47 M M10", "one conversation", f"{BASE}/messaging/thread/...")`
   -- the two ids as ONE unit on ONE address.

**COUNT AND SPLIT BOTH CLOSE EXACTLY.** Published 2 rows, `2W`. `M M10` is W and
`M M47` is W. 2 of 2.

**NO RIVAL WITH ROOM, measured rather than assumed.** Every `M47` mention in the
tracked corpus was enumerated (`git grep`, 9 hits, all read).
`INMAIL-COMPOSE-SURFACE` is COMPLETE at 1 of 1 on `J 129`,
`AI-ASSIST-MESSAGING` COMPLETE at 2, `MESSAGE-REQUESTS-SURFACE` COMPLETE at 4.

**THIS REVERSES A DECLINE MADE EARLIER TODAY, AND THE REASON IT WAS MADE IS
WORTH KEEPING.** `_audit/2026-09-19-routing-the-unassigned.md` s2.5 declined
`M47` because the census calls it *"the exception worth pulling forward ... it
needs no addressing"* and **"no published blocker corresponds to that"**. That
search was for a blocker whose NAME means needs-no-addressing, and none exists.
It did not test whether a committed source names the row for a blocker that
already exists. Three do. And the census cell it quoted is not contradicted --
needing no address is exactly why A23 calls `M47` *"the nearest write in the
package that needs no address at all"*, in the sentence that pays this capture.

---

## 3. THE TWO I NEARLY FILED, AND WHAT STOPPED EACH

These are recorded at length because a decline that cannot be audited is worth
no more than a guess, and in both cases the argument that beat me was already on
disk.

### 3.1 `CONVERSATION-OVERFLOW-MENU` -- I had it at 10 of 10, and the evidence is MEASURABLY COARSE

**The case I built, and it looked forced.** `messaging-and-content.md` L498
enumerates an eleven-item family and states the blocking MECHANISM, not merely a
subject:

> *"**Conversation management** (archive, restore, mute, star, mark read/unread,
> bulk, leave, **layout**, windows, search, **delivery indicators**) | 11 | W |
> ... **Every one is a per-conversation overflow-menu item** and that menu has
> never been opened ... One capture of an open conversation overflow menu would
> settle **eleven rows at once**."*

The eleven names map to eleven ids, uniquely, with no leftovers: `M25 M27 M28
M29 M30 M31 M32 M34 M35 M36 M49`. Exactly one of them (`M34`) is published as
its own blocker, `MISSING-PARAM-MESSAGING`, 1 row, COMPLETE. **Ten remain
against a blocker that publishes ten.** The map holds eight (`7W + 1RW`); the
published split is `1R/8W/1RW`; the two outside are `M M35` (**W**) and `M M49`
(**R**) -- which is exactly `1W` and `1R`. Count, membership and split all land.

**WHAT REFUTED IT: the cell fails the coarseness test that this campaign's own
Request 4 established, and fails it on its own members.** Request 4 ruled that
when two first-party sources disagree you prefer the one whose precision is
MEASURABLE, and it upheld the jobs section-2 column by testing it for
coarseness. I ran the same test here. The cell publishes `11 | W`. Its own
eleven members, in the same file's row table, are:

    W     M25 M27 M29 M30 M31 M32 M35 M36      8
    R+W   M28                                  1
    R     M34, M49                             2

**Three of eleven are mislabelled -- including both of the two rows my case
depended on.** A cell that cannot tell R from W for 27 per cent of its own
members cannot carry a mechanism claim about those same members strong enough to
overturn a ruling. Where the jobs column passed that test, this one fails it.

**AND THE RULING IT WOULD HAVE OVERTURNED USED THE BLOCKER'S OWN NAME.**
`_audit/2026-09-19-the-three-ruling-requests-ruled.md` refused both rows on
*"does this act on a single conversation"*, which it correctly describes as
*"the blocker's own name restated, not a test invented to fit"*. An inbox LAYOUT
is not per-conversation; a delivery INDICATOR is per-message. The ledger's own
A13 measurement agrees about the mechanism -- the trigger is absent from the DOM
and *"the conversation row reveals it on hover"*, a PER-CONVERSATION-ROW control.

**A SECOND DEFECT IN THE SAME ARGUMENT, counted.**
`_audit/2026-09-19-routing-the-unassigned.md` s2.3 raises this as a ruling
request and states *"**Nine** of those eleven are filed to
`CONVERSATION-OVERFLOW-MENU`; the two that are not are exactly `M M35` and
`M M49`"*. **It is eight, not nine, and three are not filed there, not two** --
`M34` is the third. I counted them off the map.

**VERDICT: DECLINED, and the open ruling request is answered rather than left
hanging.** Both slots stay empty, on stronger grounds than the ruling had: the
new evidence offered in support of reopening is the coarsest cell in the slice.

### 3.2 `CONTENT-ANALYTICS-SURFACE` -- a swap that closed two blockers, refuted by an ADDRESS

**The case I built.** `messaging-and-content.md` section 2 groups
*"**Analytics** (post, comment, creator, **newsletter**) | 4 | R"* and
*"**Newsletters** (create, manage, multiple, Newsletter Page, **share**,
subscribe/unsubscribe) | 6 | W"*. Both map cleanly: Analytics = `C38 C39 C40
C83`; Newsletters = `C50 C51 C84 C81 C82 C80`. But the map holds `M C83`
(analytics, R) inside `NEWSLETTER-SURFACE` and leaves `M C82` (share, W)
UNASSIGNED. The swap -- `C82` in to `NEWSLETTER-SURFACE`, `C83` out to
`CONTENT-ANALYTICS-SURFACE` -- closes `CONTENT-ANALYTICS-SURFACE` at 5 of 5 with
its split `5R` exact, keeps `NEWSLETTER-SURFACE` at 12, moves its split from
3R to 2R against a published `1R`, and consumes an unassigned row.

**WHAT REFUTED IT: two committed sources say this blocker is ONE ADDRESS, and it
is not the newsletter one.**

1. **The shipped test.** `tests/test_blocker_map_is_derived.py` L455-L463 records
   the filing of the four rows that are here: *"`M C38`'s census note names an
   `/analytics/creator/` address, **which is the allowlist +1 the ledger
   charges** -- cost and measured address agreeing from opposite ends."* And it
   closes the door I was walking through: *"**The fifth is NOT guessed: every
   other analytics row is already filed on a stronger source** (`P L1`, `P L8`
   by census section; `P L4` by shipped code)."* `M C83` is filed on shipped
   code too -- `linkedin_server/readonly.py` -- the same class as `P L4`.
2. **Shipped code names `C83`'s address and refuses it separately.**
   `readonly.py`'s newsletter admission lists, under WHAT IT DOES NOT ADMIT:
   *"`/newsletters/<slug>/analytics/`   census `M C83`, `P L4`"*. That is a
   different root from `/analytics/creator/content/`, and the ledger prices this
   blocker at **allowlist +1**, not +2.

**THE GENERAL LESSON, and it is the one I would carry to the next pass: a census
FAMILY groups by SUBJECT; a BLOCKER groups by WHAT BLOCKS IT.** Newsletter
analytics is analytics by subject and a newsletter address by blocker. Where the
two cut differently the blocker's own cost and address win, because those are
the things a wave sent to close it actually has to buy.

**VERDICT: DECLINED.** `M C82` stays UNASSIGNED; `M C83` stays where shipped code
puts it. I had this filed in draft and the instrument took it back off me.

---

## 4. THE REMAINING TEN DECLINES

Each states the hole's DIRECTION first, because the published split does most of
the excluding, and then what was considered.

### `GROUPS-SURFACE` 30 of 32 -- 2 holes, **both READS**

W side FULL at 20 of 20, so **every write in the candidate pool is excluded by
arithmetic before any reading of it** (`N 41 N 42 N 51 N 59 N 60 P B8 P D24
M C82 M M13 M M35 M M5 J 150 J 78-83`). Both carve-outs are reads. **No
unassigned row in the pool is a groups read.** See section 1.

### `COMPANY-PAGE-SURFACE` 16 of 18 -- the split is INTERNALLY CONTESTED

The map holds **14R/2W** against a published **13R/5W**: one read OVER and three
writes SHORT, while the count is short by two. That is not a hole, it is a
disagreement, and it is already an open ruling request (routing-the-unassigned,
Request 1: the ledger's `13R` against two first-party enumerations naming 14
reads). **A row cannot settle it.**

**`N 51` "Mute a company" is the only company-ish write in the pool and it is
excluded by the very source that banked four rows here.** `network.md` L584
enumerates the family by row id -- *"| **Company pages** | 33, 47, 53, 54, 101,
102, 104 (7) | 6 READ, 1 WRITE |"* -- and that cell is PRECISE (I ran the
coarseness test: the seven ids are 6R/1W exactly). The same table lists `N 51`
in a DIFFERENT family, *"Groups, articles, misc follow | 37, 41, 42, 43, 49, 50,
51, 63, 64, 76"*. **You may not cite an enumeration for what it includes and
ignore what it excludes.**

### `EVENTS-SURFACE` 17 of 18 -- 1 hole, **a READ**

W side FULL at 11 of 11. `N 179` (R) is the row, carved out by the events wave's
own concession. See section 1. No unassigned events read exists.

### `ARTICLE-SURFACE` 5 of 6 -- 1 hole, **a WRITE**

The R slot is already filled (`M C48` *"View all your articles"*). The candidates
are `N 41` *"Follow a member from one of their articles"* and `N 42` *"Unfollow
the articles of a member you are not connected to"*, both W.

**Neither is forced, and the reason is sharper than "two candidates, one slot".**
`M C79` *"Follow **or unfollow** member articles"* is **already filed in this
blocker**. `N 41` and `N 42` are that one row split into its two halves across a
slice boundary -- **jointly** a duplicate of a row already here. Taking either
half alone would put half a duplicate in a blocker that already holds the whole.
They belong in the duplicate register, which
`_audit/2026-09-19-routing-the-unassigned.md` s2.4 already flagged and which I
confirm.

### `CONTENT-ANALYTICS-SURFACE` 4 of 5 -- 1 hole, **a READ**. See 3.2.

### `OPEN-TO-HIRING-MODAL` 4 of 5 -- 1 hole, **a WRITE**

`P D24` *"Open to volunteering"* is a W whose cell reads *"Reached from the
`Open to` button, **one of the three items**"* -- the same button `P J1` names,
and the arithmetic closes exactly.

**I decline it, and I can put the reason more precisely than "the name is
wrong".** The `Open to` button draws THREE items. Two have blockers of their own
-- `OPEN-TO-WORK-MODAL` (11, COMPLETE) and `OPEN-TO-HIRING-MODAL` (5). **There is
no blocker for the third.** So `P D24` is a member of the "surplus to the
published division" class: a row the census places in a family the ledger never
gave a home. It is not a row `OPEN-TO-HIRING-MODAL`'s count expects; it is a row
whose own blocker was never published. A wave routed to `OPEN-TO-HIRING-MODAL`
on this row arrives at the wrong tab of the right modal.

Its rival `P B7` is inside `BADGES-SURFACE`, COMPLETE at 5 of 5; taking it would
break a closed blocker to close another.

### `CREATOR-HUB-SURFACE` 3 of 4 -- 1 hole, **a READ**

**Profile section L is exhausted.** All eight of its frozen rows have homes:
`L1 L7 L8` here, `L2` to `PARSER-ON-A-LOADED-PAGE` by **`LEDGER-EXPLICIT`**,
`L3 L4` to `NEWSLETTER-SURFACE`, `L5` to `LIVE-BROADCAST`, `L6` to
`AUDIO-EVENTS-EXISTENCE`. `L2b` was **split from `L2` on 2026-09-04 by a team-lead
ruling** -- after the 15:53 freeze -- so it is not in the 409 and cannot be the
fourth row. **No unassigned row is a creator-hub read.**

### `POST-COMMENT-CONTROLS` 3 of 4 -- 1 hole, **a WRITE**

**The nine-row comment surface is exhausted, 9 for 9.** `messaging-and-content.md`
section 2 names it *"(reply, media, mention, sort, edit, comment-on-comment
reaction, turn off/limit, hide, verified filter)"*; the ids are `C26 C27 C28 C29
C30 C34 C23 C24 C90`, and every one has a home: four in `COMMENT-IDENTIFIER`
(COMPLETE at 4), three here, `C27` in `FILE-UPLOAD-UNSANCTIONED` (COMPLETE at
16), `C28` in `MENTION-COMPOSITION-RULING` (COMPLETE at 2). **No unassigned row
in the pool is a comment row at all.** The fourth row is either inside one of
those complete neighbours -- which is a ruling, not a filing -- or outside the
comment family.

(Note: this same cell publishes `9 | W` while `C29` is `R`, so it is coarse in
the direction column too. I used it only for MEMBERSHIP, and membership is
checkable against the row table.)

### `ACCOUNT-VERIFICATION` 2 of 3 -- direction unconstrained (cost-0 table publishes no split)

`J 81` *"Verify account to raise the Easy Apply daily limit"* is the only
candidate, and it is the sharpest near-miss in the set: the blocker's cost cell
says *"the new `verification` substring probably bites"*, the row's capability
text literally begins *"Verify account"*, and taking it would close TWO blockers
at once -- `PREMIUM-APPLY-SURFACES` publishes 5 and has six candidates
(`J 78-83`), so removing one closes it exactly.

**I decline on two grounds, and the second is the one that decides it.**

1. **The arithmetic is a constraint, not a licence.** Six-for-five says one of
   the six is out. It does not say which, and the only thing nominating `J 81`
   is its name.
2. **The source classifies it, and a reader's test does not outrank that.**
   `jobs.md` section 2 groups the block as *"| 78-83 | Premium apply extras
   (cover-letter AI, Top Choice, **limits**, self-ID) | ... | W |"* -- and
   `J 81`/`J 82` are the **limits** pair. The census places it in Applying. The
   name-match is mine; the grouping is the source's.

This is the same test the 12:26 ruling applied to this row, and its retraction
did not touch it -- what was retracted there was the filing of `J 82` on the
ledger's `1R`, a discriminator Request 4 has since retired.

### `HASHTAG-EXISTENCE` 2 of 3 -- explained, and a filed row is contested. See section 1.

### `PER-MESSAGE-OVERFLOW-MENU` 1 of 2 -- 1 hole, **a WRITE**

`M M13` *"Forward a message"* is the only candidate and its census cell reads
*"never named; forwards a third party's words to another third party"* -- **it
does not name the menu**. `M M11`, the row that IS filed, is here because its
own reason cell reads *"per-message overflow menu, never opened"*: the blocker's
name in the census's own words. **The asymmetry is the whole answer** -- one row
is named by its source and the other resembles the blocker. I concur with
`_audit/2026-09-19-the-empty-blockers.md` s4: *"a row admitted by resemblance is
chosen, not forced."*

---

## 5. THE BOUND DOES NOT REPRODUCE, AND IT CANNOT

`_audit/2026-09-19-routing-the-unassigned.md` s2.1 computed that **at least two
holes cannot be filled however perfectly every remaining row is placed**, and
called it *"arithmetic, not judgement"*:

    HOLES still open across 18 blockers      26
    UNASSIGNED frozen-GAP rows left          24
    holes that CANNOT be filled              >= 2

**I re-measured it across ALL 97 blockers, and it is zero:**

    partial blockers        12    deficit   15
    absent blockers          4    deficit    8
    -----------------------------------------
    HOLES total                             23
    UNASSIGNED rows                         23
    holes with no row to put in them         0

**AND IT IS ZERO BY CONSTRUCTION, NOT BY LUCK.** The two numbers being
differenced are the same number:

* the ledger's tables total exactly 409 (the builder FAILS if they do not);
* the frozen GAP set is exactly 409 (same assertion);
* assigned + unassigned = 409 (same assertion);
* **no blocker may hold MORE than its published count** -- the builder prints
  `FAIL: the map assigns MORE rows than the ledger published` and refuses to
  write.

With every deficit therefore non-negative, `sum(published - held)` over all
blockers is `409 - assigned`, which is UNASSIGNED itself. **The holes and the
loose rows are one quantity counted twice, and their difference is always
exactly zero.** The comparison cannot yield a positive residue while the
builder's own assertions hold, so the `>= 2` was never a bound on anything.

**THE MOST LIKELY MECHANISM, and I say likely because I did not measure that
tree:** the 26 was summed over PARTIAL blockers only ("across the eighteen
blockers still short") and then differenced against the WHOLE unassigned pool,
which also owes rows to the four blockers holding nothing. A deficit taken over
a subset, compared against a denominator taken over the whole -- the same shape
as the 2026-09-05 defect where a count was compared to a set it was not computed
over.

**WHAT THAT DOES AND DOES NOT CHANGE.** It does NOT rehabilitate the residue:
sections 1-4 show that fifteen of my fifteen holes have a NAMED reason no
remaining row goes in them, which is a stronger statement than an arithmetic
bound and does not depend on one. What it removes is a false comfort -- *"a
perfect router still ends with two holes"* -- that would let a future pass stop
early and call the slack structural. **The slack is zero. Every hole that stays
open stays open on evidence, and has to be argued.**

### The fifteen, classified

    A  EXPLAINED -- the row is in the map under another blocker    4
    B  NO CANDIDATE IN THE POOL AT ALL                             2
    C  A CANDIDATE EXISTS AND A COMMITTED SOURCE EXCLUDES IT       7
    D  THE PUBLISHED SPLIT IS CONTESTED, so no row settles it      2
                                                                  --
                                                                  15

A = `GROUPS-SURFACE` 2, `EVENTS-SURFACE` 1, `HASHTAG-EXISTENCE` 1.
B = `CREATOR-HUB-SURFACE` 1, `POST-COMMENT-CONTROLS` 1.
C = `CONVERSATION-OVERFLOW-MENU` 2, `ARTICLE-SURFACE` 1,
`CONTENT-ANALYTICS-SURFACE` 1, `OPEN-TO-HIRING-MODAL` 1,
`ACCOUNT-VERIFICATION` 1, `PER-MESSAGE-OVERFLOW-MENU` 1.
D = `COMPANY-PAGE-SURFACE` 2.

**Not one of the fifteen is a hole whose row is sitting unclaimed in the pool.**
That is the honest close: the remaining PARTIALs in this set are not a search
problem, and a pass that treats `UNASSIGNED > 0` as a reason to keep filling will
manufacture exactly the guesses this map exists to keep out.

---

## 5A. THE TOTALS ARE AN IDENTITY; THE MATCHING IS NOT. THE SPLIT IS WHAT SEES IT.

**Two things are being conflated whenever the 24 is discussed, and separating
them is the whole use of section 5.**

* **THE TOTALS** -- holes vs unassigned rows. **Forced equal, always** (section
  5). This tells you nothing and can never tell you anything.
* **THE MATCHING** -- whether a valid assignment exists that fills every hole.
  **It does not**, and sections 1-4 name fifteen reasons why not. Some published
  slots have no row in the corpus; some rows in the pool belong to families whose
  blocker is already COMPLETE without them.

**THE IDENTITY IS EXACTLY WHAT HIDES THE MISMATCH.** A quantity that must
balance cannot report an imbalance. So the aggregate is not a weak signal here
-- it is a guaranteed-silent one, and any future pass that watches it will watch
it stay at zero while the matching fails underneath.

### What DOES see it: the published R/W split, which nothing checks

**The builder asserts on COUNTS and never on the SPLIT**, although the ledger
publishes a split for 88 of the 97 blockers and it was my primary discriminator
all session. That gap is not theoretical. I measured it across all 97:

    blockers with a published split                               88
    blockers OVER on some direction                                2
    blockers SKIPPED, a held row's direction unreadable           19

    OVER on R   NEWSLETTER-SURFACE        published R1  W11   held R3  W9
    OVER on R   SEARCH-RESULTS-SURFACE    published R19 W2    held R20 W1

**Both are COMPLETE on their counts, so the shipped assertion sees nothing.**
A third, `COMPANY-PAGE-SURFACE` at **14R held against 13R published**, is among
the NINETEEN SKIPPED, and the limitation is stated rather than hidden: `jobs.md`
keys direction by RANGE (`106-114`) and not by row id, so no `J` row's direction
is readable and any blocker holding one is skipped. I established that case by
hand in section 4; it is already an open ruling request. **Nineteen skipped
against 88 is the honest size of this instrument's blind spot, and closing it
means giving `jobs.md` a per-row direction column, not patching the reader.**

**AND ALL THREE TRACE TO SECTION 1's MECHANISM.** A re-file is count-neutral
across the pair of blockers, so the count assertion is structurally blind to it
-- but it MOVES THE SPLIT, and `SEARCH-RESULTS-SURFACE`'s own assignment note
concedes this in writing: *"the split is not claimed for the post-freeze set ...
That is what a re-file does."*

**PROPOSED INSTRUMENT, and it arrives already shown failing** -- three named
blockers, three named rows, on today's tree. It must ship as a REPORT first, not
as an assertion: two of the three violations are documented and deliberate, so a
red gate would fail CI on work that was ruled correct. The right shape is a
printed `split delta` column beside the existing count delta, and a rule that a
NEW over-run must be argued. **Ruling request D.**

---

## 6. RULING REQUESTS THIS PASS RAISES

**A. DECLARE THE MAP'S CONVENTION: as-published, or at-head?** It currently
mixes them and checks at-head filings against as-published counts, which
guarantees a permanent PARTIAL for every re-file that ever happens. Whichever way
it goes, the fix is a COLUMN (`re-filed-from`), not a search. Until then the
verdict string *"PARTIAL -- N row(s) named by no committed source"* is **false
for at least four of my thirteen**, where the rows ARE named, in this map, by
committed sources.

**B. `N 61` in `HASHTAG-EXISTENCE`.** `LEDGER-EXPLICIT` names three ids whose
directions reproduce the published split exactly, and `N 61` is not among them.
Left in place pending A, because A decides it.

**C. `CONVERSATION-OVERFLOW-MENU` request 2 is ANSWERED, not pending.** The
evidence offered for reopening (L498) mislabels the direction of three of its own
eleven members, including both rows at issue. Recorded so the request is not
re-raised a third time on the same cell.

**D. CHECK THE PUBLISHED SPLIT, AS A REPORT.** Section 5A: three blockers hold
more rows of a direction than the ledger published, all three invisible to the
count assertion, and the split is the only thing that can see a re-file. Report
first, assert later -- two of the three are deliberate.

**E. TWO OF MY THIRTEEN LOOK LIKE LEDGER OVER-COUNTS RATHER THAN LOST ROWS, AND
I AM NOT RULING IT.** `CREATOR-HUB-SURFACE` (4R published, 3 held) and
`POST-COMMENT-CONTROLS` (1R/3W published, 3 held) are my class B: in both, the
census family the blocker is named for is **exhausted with every member homed**
-- profile section L, 8 frozen rows, all filed; the comment surface, 9 rows, all
filed -- and **no unassigned row in the whole pool is a member of either
family.** That is the shape of *"the ledger published a count the corpus never
supported."* It is also the shape of *"the fourth row sits inside a COMPLETE
neighbour and one of those neighbours is over-published"*, and I cannot
distinguish the two from where I stand. **Naming which is a ruling, not a
search**, and the thing that would decide it is request D: if a neighbour is
over-published, its split will say so.

---

## 7. METHOD NOTE: A HAZARD NOW SEEN AT A SECOND SITE

An exhaustive sweep of the corpus for row-id ENUMERATION LINES (all 147 tracked
`.md` files, run as a closed-form slice and reviewed here) reproduced every
enumeration this pass leaned on and added none that changes a verdict. It did
independently re-find a trap that `_audit/2026-09-19-the-empty-blockers.md` s4
recorded once:

> **BLOCKER RANKS AND CENSUS ROW IDS SHARE A NUMBER SPACE.** The empty-blockers
> wave was nearly taken in by *"ROW 57 MESSAGE-ADDRESSING"*, where 57 is the
> blocker's LEDGER INDEX. The sweep found a second, worse instance: the ledger's
> own L1571 reads **"Blockers 72, 78, 79, 80, 85, 86 and 87 are each charged
> `allowlist +1`"** -- which collides numerically with the `J 78`-`J 83` range
> that `PREMIUM-APPLY-SURFACES` and `ACCOUNT-VERIFICATION` both contest, and with
> `J 85`/`J 86`, contested between `COMPANY-PAGE-SURFACE` and
> `JOBCARD-OVERFLOW-MENU`. A bare-number grep over the ledger lands on it.

**One instance is an anecdote; two make it a rule.** Any sweep of this corpus for
bare row numbers must require a slice letter or a corroborating context token,
and must print what it MATCHED rather than only what it did not -- which is this
project's own standing lesson about refusals, pointed at its own searches.

---

## WHAT THIS DOES NOT CLAIM

Locating a row measures nothing and unblocks nothing. `THREAD-REPLY-BOX` is
MEASURE at cost 5 and `M M47` is still GAP for the reason its cell gives. The
four explained deltas free no work; they free a future wave from looking.

**And I did not reach a fixed point on the artifact.** I reached one on the
question I was given: for every one of the sixteen holes, the row its published
count expects is either filed, identified elsewhere, or shown to have no
candidate -- and each of those three verdicts is checkable from committed
sources by a reader who trusts nothing I wrote.
