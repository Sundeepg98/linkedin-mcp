# The five requests the three-wave round raised, ruled

**All five were adjudicable from committed evidence. None needed anything only
the operator knows, and calling them "ruling requests" invited a permission
answer to a measurement question.** That is the specific failure: presenting a
technical unknown as a permission question hides that nobody did the work.

---

## A. THE MAP'S CONVENTION — RULED: at-HEAD membership, plus `RE_FILED`

**The defect, measured.** The map recorded **at-HEAD** membership and compared it
against **as-published** counts. Those answer different questions, so every
deliberate re-file produced a permanent PARTIAL, and the verdict string
*"PARTIAL -- N row(s) named by no committed source"* was **false for three of
thirteen**: a committed source names those rows AND names where they went.

**Ruled at-HEAD, not as-published, and the reason is a near-miss.** I leaned
as-published until I checked what it would undo. `M C52` was moved to
`FEED-PREFERENCES` on 2026-09-19 reversing a LEDGER-AMENDMENT on four
measurements — one being that the note keeping it in `HASHTAG-EXISTENCE` quoted
the row as *"follow / unfollow topics/hashtags"* while the capability cell
contains **no occurrence of "hashtag"**. The misquote was doing the work.
**A convention that reverses a better-evidenced later reading is not a
convention; it is a ratchet pointing backwards.**

So membership follows the best current evidence and `RE_FILED` carries the
history. A published row is **ACCOUNTED** if it is held or listed as re-filed;
anything else stays PARTIAL and still means what it says.

**Effect: complete 83 -> 86, partial 11 -> 8.** No row moved; three verdicts
stopped lying.

## B. `N 61` IN `HASHTAG-EXISTENCE` — RULED: removed

The ledger amendment (`2026-09-03-linkedin-gap-blockers.md:1171-1180`)
enumerates this blocker's three published rows **by id** — `N 194`, `C 11`,
`C 52` — and `N 61` is not among them. **Two waves found this independently.**
Removed; the row returns to the unassigned pool, where it is honest.

The blocker now reads **3 published, 1 held, 2 re-filed = ACCOUNTED**, which is
the first time its line has been true.

## C. `CONVERSATION-OVERFLOW-MENU` — RULED: both waves are right, about different things

**The cell is dead as evidence.** `messaging-and-content.md:498` labels all
eleven members `W`; measured here, `M34` (search) and `M49` (delivery
indicators) are **R**. A cell that mislabels its own members' direction cannot
enumerate a blocker.

**The filing stands anyway, on the blocker's own split.** Published `1R/8W/1RW`
= 10. Eight were filed: 7W plus `M28` (R+W), so the RW slot was taken and one W
and the one R slot were open. `M35` is W, `M49` is R. They fill exactly those,
closing at `1R/8W/1RW` with zero headroom.

**These are compatible, and the second follows from the first**: the cell's
coarse `W` is precisely why it cannot be used to *exclude* an R row.

## D. THE PUBLISHED-SPLIT CHECK — RULED: report now, gate once the deliberate over-runs are declared

`scripts/_check_published_split.py` reports two blockers over on R —
`NEWSLETTER-SURFACE` (published R1, holds R3) and `SEARCH-RESULTS-SURFACE`
(published R19, holds R20) — both **COMPLETE on counts and therefore invisible
to the count assertion**. A re-file is count-neutral across the pair; only the
split can see one.

It stays a report because two of the three known over-runs were ruled
deliberate, and a gate that fires on a ruled-deliberate state teaches people to
bypass it. **Promote to gate when the deliberate ones are declared in a table,
the same shape as `RE_FILED`.**

## E. `CREATOR-HUB-SURFACE` AND `POST-COMMENT-CONTROLS` — RULED: LEDGER OVER-COUNTS

The wave said it could not distinguish *"the ledger published a count the corpus
never supported"* from *"the row sits inside an over-published neighbour"*, and
that request D decides it. **D was runnable, so I ran it.**

Both over-published neighbours are over **on R**, and both shortfalls are **R**.
So the test is whether either neighbour holds a row belonging to these families:

* `NEWSLETTER-SURFACE`'s surplus reads are `N 57` (view your subscriptions) and
  `P L4` (newsletter analytics — the same capability as `M C83` in another
  slice, i.e. its own cross-slice duplicate).
* `SEARCH-RESULTS-SURFACE`'s surplus read is `N 194`, a hashtag-search row —
  now recorded in `RE_FILED` under `HASHTAG-EXISTENCE`, which is where it came
  from.

**Neither neighbour holds a creator-hub or comment-surface row.** The missing
rows are not next door. Both are ledger over-counts.

---

## What made all five decidable

**Every one turned on a measurement somebody could take.** The only thing
standing between them and an answer was somebody running the instrument the
previous wave had already shipped, or reading the two columns of a ledger table
and noticing the map was reading one of each.
