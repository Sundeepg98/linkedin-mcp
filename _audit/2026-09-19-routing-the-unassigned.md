# Routing the unassigned

**UNASSIGNED 40 -> 24.** Sixteen rows routed, each on a committed source. Six
blockers closed. The rest are routed to a REASON, which is the other half of
the job and the longer half of this file.

## READINGS

| when | by | UNASSIGNED | note |
|---|---|---:|---|
| 17:55:43 IST | box | 40 | arrival, worktree `23d5daa` |
| ~18:0x | box | 34 | first pass, committed `86b8ed5` |
| 18:23:29 IST | box | 25 | second pass, committed `5581950` |
| close | box | 24 | third pass |

**ONE STAMP IN THE FIRST VERSION OF THIS FILE WAS NOT TAKEN AND IS CORRECTED
HERE.** It recorded a close reading at "18:09 IST". The box said 18:06 when I
was resumed, so that stamp was my own sense of the clock rather than a
measurement, and it was fast by at least three minutes. The reading itself (34)
was real; only the time was invented. An agent's clock is not an instrument,
and the correct repair is to say when the number was taken or not claim a time
at all.

---

# PART 1 -- THE SIXTEEN ROUTED

## `COMPANY-PAGE-SURFACE` 10 -> 16 of 18: `N 33`, `N 47`, `N 53`, `N 54`, `N 104`, `J 86`

The blocker already held two rows on the census's blocker cell reading
`No /company/`. Four more carry that identical cell. **I applied a committed
standard rather than inventing one.**

Then `network.md` section 6 turned out to enumerate the family **by row id**:

    | **Company pages** | 33, 47, 53, 54, 101, 102, 104 (7) | 6 READ, 1 WRITE |

`J 86` comes from a different sentence -- `jobs.md` section 2 covers two rows at
once, *"85-86 | undo a dismissal, \"I'm interested\" | posting-card and
company-page controls"* -- read positionally, the same way `J 70` was split from
`J 71`-`J 73`.

## `POST-COMMENT-CONTROLS` 0 -> 3 of 4: `M C90`, `M C23`, `M C29`

`M C90`'s reason cell ends *"a per-post comment control"* -- the blocker's three
words. **The string occurs in exactly one row of the corpus.**

`M C23` "Turn off or limit comments on your post": the phrase *"on your post"*
occurs in exactly three rows, and the third (`C24`) is in a blocker that is
published `4W` and COMPLETE. `C23` and `C24` share a MENU -- `C24`'s entire
reason cell is *"same menu"* -- and the committed discriminator splits them:
`tests/test_blocker_map_is_derived.py` says `COMMENT-IDENTIFIER` is *"the
operations that require naming WHICH comment"*. Hiding a comment names one;
turning comments off does not.

`M C29` is forced by direction over a committed enumeration. `messaging-and-
content.md` section 2 lists the comment surface as nine named items; **exactly
one of the nine is an R**; the two blockers that divide that surface are `4W`
and `1R/3W`; a `4W` blocker has no read slot to offer.

## `FEED-CONTENT-READ-RULING` 0 -> 2 of 2, COMPLETE: `M C43`, `M C74`

*"no tool returns"* occurs in exactly three rows; the third is in a COMPLETE
blocker and cannot move. The two that remain are both R against a published
`2R`, and both are `/feed/` addresses. Independently corroborated: section 2's
*"Reading content (feed, post text, own articles, group search,
share-off-platform, feed preferences) | 6 | R"* -- the other four are filed to
four different blockers.

## `MESSAGE-REACTION` 0 -> 1 of 1, COMPLETE: `M M48`

**A sibling row names this row by id.** `C91`'s reason cell reads *"Reactions
have a third surface -- posts, messages (M48) and group conversations -- and the
repo names only the first"*.

**I had declined `M M48` at 18:06 as a capability-column name match.** That was
right on the evidence I had and wrong on the evidence that exists. Recorded in
the row's own note, not quietly reversed.

## `INMAIL-COMPOSE-SURFACE` 0 -> 1 of 1, COMPLETE: `J 129`

Both candidates are W, so direction could never separate them -- **the
discriminator is lexical**, the kind Request 2b taught. *"compose surface"*
occurs in exactly two rows; *"compose surface for inmail"* in exactly one.
`J 150` is excluded by its own cell, which names the send-verification wall on
the ordinary composer and no InMail at all.

## `THREAD-REPLY-BOX` 0 -> 1 of 2: `M M10`

Two committed sources. The ruling itself, at L68: *"`M M10` stays available to
`THREAD-REPLY-BOX`, where it is the best candidate."* And the census
independently: *"A reply-in-thread editor has never been censused."*

## `HASHTAG-EXISTENCE` 1 -> 2 of 3: `N 61`

`M C11` is already here by LEDGER-AMENDMENT and is W, leaving `1R/1W`. Three
hashtag rows carry *"EXISTENCE UNCERTAIN ... may have RETIRED"*; **`N 61` is the
only R**.

## `PER-MESSAGE-OVERFLOW-MENU` 0 -> 1 of 2: `M M11`

Reason cell opens *"per-message overflow menu, never opened"*. The string occurs
in exactly one row of the corpus.

---

# PART 2 -- THE TWENTY-FOUR NOT ROUTED

## 2.1 THE CLASS I DID NOT EXPECT TO FIND: SURPLUS TO THE PUBLISHED DIVISION

**Seven of the remaining rows are named by the census's own grouping as members
of a family whose blocker is published COMPLETE WITHOUT THEM.** They are not
lost. There is no room for them.

| row | the family the census puts it in | the blocker | state |
|---|---|---|---|
| `J 18`, `J 19` | *"18-19 recent searches read / clear ... `/jobs/search-history/`"* | `SEARCH-HISTORY-SURFACE` | COMPLETE 2 of 2, both rows network-slice (`N 95`, `N 96`) |
| `J 28` | *"24-30 posting-side insight panels (... report-closed)"* | `CLOSED-SINCE-CENSUS` 7/7 and `PANEL-NOT-OBSERVED` 3/3 took the other six | both COMPLETE |
| `M C82` | *"Newsletters (create, manage, multiple, Newsletter Page, share, subscribe/unsubscribe)"* | `NEWSLETTER-SURFACE` | COMPLETE 12 of 12; it holds `C50 C51 C80 C81 C83 C84` and not `C82` |
| `J 100` | *"92-100 every job-preference FIELD ... recruiter visibility"* | `OPEN-TO-WORK-MODAL` | COMPLETE 11 of 11 |
| `J 150` | Writing Assistant = AI assist | `AI-ASSIST-MESSAGING` | COMPLETE 2 of 2 |
| `N 51` | *"Groups, articles, misc follow | 37, 41, 42, 43, 49, 50, 51, 63, 64, 76"* | no blocker is named for mute; its cell says *"`mute` 0 hits"* | none exists |

**THIS IS A FINDING ABOUT THE LEDGER, NOT ABOUT THESE ROWS.** In at least four
places the published per-blocker count is ONE SHORT of the census's own
enumeration of the same family. That is a better explanation for a chunk of the
residue than "the classifier's rows were lost": some of them were never given a
home. It is also falsifiable -- if the ledger's counts are right, then each of
these rows belongs to some blocker nobody has connected it to, and naming which
is a ruling.

### AND THE BOUND THAT PROVES IT IS NOT JUST MY READING

Summing every deficit across the eighteen blockers still short of their
published count:

    HOLES still open across 18 blockers      26
    UNASSIGNED frozen-GAP rows left          24
    ------------------------------------------
    holes that CANNOT be filled from the
    remaining rows, however perfectly
    every one of them were placed            >= 2

**That is arithmetic, not judgement.** Even a perfect router ends with at least
two holes and zero rows to put in them. Combined with the seven rows in the
table above -- rows the census names in a family whose blocker is COMPLETE
without them -- the published division and the census enumeration do not
reconcile in both directions at once: **some rows have no hole, and some holes
have no row.** Any future pass that treats "UNASSIGNED > 0" as a search target
will burn itself on that.

## 2.2 CONTESTED BY AN EXISTING RULING REQUEST -- 7 rows

`J 78 J 79 J 80 J 81 J 82 J 83` (`PREMIUM-APPLY-SURFACES`, 0 of 5) are the
subject of Request 4, already ruled *for the census and against the ledger's
`1R`* -- which explicitly **does not fill the blocker**: a committed probe names
six rows for five slots and cannot say which is out. `J 81` is additionally
`ACCOUNT-VERIFICATION`'s contested third slot. Untouched.

## 2.3 DELIBERATELY LEFT EMPTY BY A RULING, AND I FOUND NEW EVIDENCE -- 2 rows

`M M35` and `M M49` were refused at `12c20e1` on the ruling's own sentences.
**I am not overturning a ruling. I am reporting that its stated ground moved.**

`messaging-and-content.md` L498 enumerates *"Conversation management (archive,
restore, mute, star, mark read/unread, bulk, leave, **layout**, windows, search,
**delivery indicators**) | 11"*. Nine of those eleven are filed to
`CONVERSATION-OVERFLOW-MENU`; the two that are not are exactly `M M35` (layout)
and `M M49` (delivery indicators) -- and the blocker's unfilled split is exactly
`1R` and `1W`, which is exactly their two directions.

**And the reason `M M35` was refused no longer holds.** It was refused as *"a
row admitted by a count it SHARES WITH A RIVAL"*. The rival was `M M10` -- which
is now filed to `THREAD-REPLY-BOX`, **on the ruling's own instruction**. The
count is no longer shared.

`M M49`'s refusal was substantive, not arithmetical (*"read receipts are a
setting, not a menu item"*), and `MESSAGING-SETTINGS` is COMPLETE at 5, so on
that reading `M M49` has no home at all.

**This is a ruling request, not a bank.** Section 45's lesson is that the field
moving is a legitimate reason to re-ask; section 50's is that a recommendation
is not a permission to act on itself. Both apply here.

## 2.4 DECLINED ON A DISCRIMINATOR I COULD HAVE BENT AND DID NOT -- 4 rows

**`J 85` "Undo a dismissal".** Same sentence as `J 86`, which I banked. The
sentence says *"posting-card ... controls"*. The only blocker named for that
card is `JOBCARD-OVERFLOW-MENU`, which claims an **overflow menu the census
never mentions**. `COMPANY-PAGE-SURFACE` claims exactly what the census said and
no more; `JOBCARD-OVERFLOW-MENU` claims more. That asymmetry is the whole reason
one half of one sentence is banked and the other is not. **Measured, not
assumed:** `"job card"` returns ZERO hits corpus-wide, and `"overflow"` returns
no unassigned row at all -- so that blocker's two slots have no lexical
candidate of any kind.

**`N 41`, `N 42`** look like `ARTICLE-SURFACE`'s one open write slot. They are
not: `M C79` *"Follow or unfollow member articles"* is **already in that
blocker**, and it is the *"follow member articles"* item of the census's own
Articles group. `N 41`/`N 42` appear to be **cross-slice duplicates of `C79`** --
which falls under the standing duplicate hold, and they are not in the duplicate
register yet. Flagged for it rather than filed.

**`P D24` "Open to volunteering"** is the sharpest near-miss of the day and I am
declining it anyway. `OPEN-TO-HIRING-MODAL` publishes `1R/4W` and holds `P J1`
`J2` `J3` (W) and `J4` (R) -- one write slot -- and `D24` is a write whose cell
reads *"Reached from the `Open to` button, **one of the three items** measured on
his account"*, the same button `J1`'s cell names. The arithmetic closes exactly.
**I am not taking it because the blocker is named HIRING and this row is
volunteering**, and a wave routed there arrives at the wrong modal tab. That is
the case the `B8`/`K9` ruling called the opposite of a harmless coin-flip. It
also has a live rival: `P B7` is a `#Hiring` row sitting in `BADGES-SURFACE` on a
count-admission the ruling itself flagged. **Filed as a ruling request.**

## 2.5 KNOWN AND CORRECTLY PARKED -- 3 rows

`P B8` is the id that lost the `B8`/`K9` tiebreak; it is not lost, it is the same
capability under the other id. `M M13` "Forward a message" was declined by
section 54 **on a run**. `M M47` is named by the census as *"the exception worth
pulling forward"* from the composition group -- it needs no addressing -- and no
published blocker corresponds to that.

---

# PART 3 -- METHOD, AND WHERE IT BEAT ME

**The instrument.** A corpus-wide cell matcher that takes a phrase, returns
every census row containing it, and prints each row's CURRENT blocker and
direction. It is deliberately not a scorer: a phrase that also matches four rows
belonging to a COMPLETE blocker is not a discriminator, and you can only see
that if the already-filed hits are printed too. **Controlled before use** --
reproduced `PICKER-SURFACES` at exactly 2, and returns 0 on a nonsense phrase.

**Where the matcher was not the answer at all: the row-id enumerations.** Four
of my sixteen came from lines that list ids outright. They are the strongest
class in this corpus short of the ledger and **nobody had swept for them**.

**AND IT REFUTED ME TWICE, WHICH IS THE ONLY REASON TO TRUST THE OTHER
FOURTEEN.**

1. I declined `M M48` on the grounds that it was a capability-column name match.
   A sibling row named it by id.
2. **I declined `N 104` on arithmetic, and the arithmetic was the weakest thing
   in the room.** I wrote that "a fourteenth read cannot enter a published
   `13R`" and called it the instrument refusing a row. Then `network.md` L584
   named `N 104` in a committed row-id list -- and the same list shows the count
   itself cannot be right: **8 jobs reads plus 6 network reads is FOURTEEN
   against a published `13R`.** I had treated a derived count as authority over
   a first-party list. The note on `N 33` is amended in place to say so.

**THE `13R` IS THEREFORE CONTESTED and is Request 5 below.** Banking `N 104`
does not settle it; it records that a contested count cannot refuse a row a
committed list names. If the ruling goes the other way, `N 104` comes back out
and the other six stay, because each carries the `No /company/` cell in its own
right.

## RULING REQUESTS THIS PASS RAISES

1. **`COMPANY-PAGE-SURFACE` `13R` vs 14 named reads.** Ledger split against two
   first-party enumerations. Same class as Request 4 -- no reader in it.
2. **`M M35` / `M M49`:** the ground for refusing `M M35` (a count shared with a
   rival) was removed when that rival was filed elsewhere on the ruling's own
   instruction, and L498 is an enumeration the ruling did not cite.
3. **`P D24`:** `OPEN-TO-HIRING-MODAL` closes exactly on it or on `P B7`, and the
   blocker's NAME fits neither a volunteering row nor a row already banked
   elsewhere.
4. **The surplus class (2.1):** four published counts are one short of the
   census's own enumeration of the same family. Either the counts are wrong or
   seven rows belong to blockers nobody has connected them to.

## WHAT NONE OF THIS CLAIMS

Locating a row does not measure it, unblock it or schedule it. Every row here is
still GAP for the reason its cell gives. `INMAIL-COMPOSE-SURFACE` is BLOCKED at
cost 8 and spends a credit; `FEED-CONTENT-READ-RULING` is DECIDE at cost 3 and
the decision is untaken; `POST-COMMENT-CONTROLS` is MEASURE at cost 6.

**I did not reach a fixed point.** I reached a point where every remaining row
has a NAMED reason it cannot be routed, and four of those reasons are questions
for somebody with standing to answer them.

---

# ADDENDUM 2026-09-20 -- THE TWO COMMIT CITATIONS IN THE READINGS TABLE

Appended at the end rather than inline by the table, so no line number any
other tracked document cites into this file moves.

`86b8ed5` and `5581950` (READINGS table, above) do not resolve on `master`.
Both are ancestors of `integrate-1821` and of
`worktree-agent-aa255d5b6ed0788c7` only. The rows each filed are on `master`
regardless: all six of `86b8ed5`'s (`COMPANY-PAGE-SURFACE` N 33 / N 47 / N 53
/ N 54, `PER-MESSAGE-OVERFLOW-MENU` M M11, `HASHTAG-EXISTENCE` N 61) and all
nine of `5581950`'s were present in `_audit/_census/blocker-assignments.tsv`
at the point `master` carried them in, by commit `fa13985`. Two of the
fifteen did not stay: N 61 was later taken out on its own evidence by
unrelated project work, and M M11's text (not its conclusion) was overtaken
by an independent commit that reached the same filing on a separate branch. A
few more of the nine (`M C23`, `M C29`, `M C90`, `M M10`) carry evidence text
a later same-branch commit rewrote before the replay; the row's own
assignment is unchanged in every one of those. Row-by-row evidence:
`_audit/2026-09-20-the-six-unremapped.md`.
