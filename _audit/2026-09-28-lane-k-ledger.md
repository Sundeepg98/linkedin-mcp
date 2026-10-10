# Lane K: the next-step ledger and the capture queue

Lane K of the capability census, briefed by the orchestrator on 2026-09-28
22:55 IST, paused before any work landed, and relaunched on 2026-10-10 from
master 3c8edc2 (CI green). Offline throughout: no page was loaded, no port
was touched, and no live capture was taken. The live lane was running a
session on the same box the whole time, so every test run here was targeted
and serial.

THE QUESTION: for every GAP row, what is the NEXT step -- and which live
captures unblock the most rows per page load? Live page loads are the scarce
resource (the operator's ruling of 2026-09-23: 40 loads a session, 20 s or
more apart, at most 5 searches, one live lane).

This document is written as the lane goes; each section says what it rests on.

## 1. Method

The population is the shipped walk, never a re-parse: every row
`scripts/census_completion.py` reads as GAP (its `walk_cells()`, which
`scripts/enumerate_gap_rows.py` and the row pin cross-check). At the base it
was 587 rows -- 91 R + 7 R+W + 381 W outside `jobs.md`, and 108 `jobs.md`
rows whose direction lives in `_audit/_census/jobs-directions.tsv` (60 W,
40 R, 8 R+W). After section 2's two exclusions it is 585.

Each row is joined to the four side tables that already hold part of the
answer:
- `_audit/_census/blocker-map.tsv` -- 327 GAP rows by blocker at the base,
  260 in no map;
- `_audit/_census/write-classes.tsv` -- 381 write rows at the base: 253
  classify-only, 128 queued on a named blocker;
- `_audit/_census/read-addresses.tsv` -- the 98 read rows outside `jobs.md`,
  each address driven through `readonly.is_read_url`;
- `_audit/_census/jobs-directions.tsv` -- the 108 `jobs.md` rows.

A row's next step is the FIRST thing that must happen before anything else
can, in this order: a ruling nobody has made; a right or object he does not
hold; a target only he can name; an address the boundary refuses; a live
capture; a build on a capture that already exists. The rulings registered in
this lane's first commit are applied as written, and the rows other lanes own
are marked as theirs.

## 2. The purchase exclusions

The ruling PURCHASES-STAY-MANUAL (the orchestrator, 2026-09-28, registered in
this lane's first commit) reads: a purchase -- Premium, InMail credits, ads,
boosts, any paid upgrade -- is not built; its row is EXCLUDED-RULED with the
reopener "he names a purchase to automate". The brief allows this lane one
kind of row move: a purchase row whose own cell meets the bar.

Every GAP row was searched for the vocabulary of a spend (purchase, buy,
paid, payment, upgrade, subscription, credit, boost, sponsor, promote,
advertise, ad, billing, checkout, price). Thirty-one rows matched a word;
two are purchases:

    row     capability                      the cell's own words
    P S9    Change the Premium plan         "changing the plan is a purchase"
    M C71   Boost a post (paid promotion)   "the only capability in this slice
                                             that costs currency"

The rest are not purchases, each for a reason on its face: an InMail send
spends a credit his Premium already includes (`M M2`, `N 156`, `N 158`), the
advertising rows are settings about ads (`P P10` to `P P14`, `P P15`), `P N22`
is the read of his subscriptions, `J 159` searches the Ad Library, `N 200`
hides an ad, and the rest match a word in passing.

Both rows move GAP -> EXCLUDED-RULED. Each cell keeps its prior text, gains
the ruling, its document and the reopener, and says the named blocker no
longer decides the state. `_audit/_census/exclusion-basis.tsv` files both
under a new family, PURCHASES-STAY-MANUAL (made by the ORCHESTRATOR, op=NO),
registered in `scripts/check_exclusion_basis.py` with the ruling's two
anchors; the table is 40 of 40, no structural problem. Both lines leave
`_audit/_census/write-classes.tsv`, whose population is write-direction GAP
rows only, and the act `purchase` leaves the closed vocabulary with its one
line, as `outside-the-classes` did.

The pins, each MEASURED on this tree by the instrument that owns it:

    census_completion.PINNED   out_of_scope 38 -> 40, achievable 733 -> 731,
                               capabilities_achievable 747 -> 745,
                               adjudicated 184 -> 186, gap 587 -> 585,
                               gap_write 381 -> 379
    write-class split          (16, 37, 336) -> (16, 37, 334), 387 lines
    messaging triage headline  131 {R 16, W 111, R+W 4} -> 130 {R 16, W 110,
                               R+W 4}
    GAP rows on refused        78, unchanged: `P S9`'s address is refused by
      addresses                allowlist silence, which that check ignores
                               by design
    blocker map                one line: `M C71`'s state today

No other figure moved: the delivered lines, bucket 1, bucket 3 and the jobs
figures read as they did.
