# The row walk: all 24 unassigned rows, read from the row side

**A SECOND INDEPENDENT READING.** Two sibling waves walk the same 24 rows from
the BLOCKER side. This one walks them from the ROW side and did not read what
they filed. Where we agree, the agreement is the only correctness evidence this
census has. Where we disagree, the disagreement is worth more, because it is the
only thing that can show the method has spread.

**Result: 2 filed, 22 declined, each with its reason.** Four ruling requests, one
probable mis-assignment inside the already-recovered 385, and one arithmetic
coincidence that a future wave will otherwise walk straight into.

---

## 0. WHAT I MEASURED, AND DISK AGREED

Tree `262bab6`, worktree clean at start. `scripts/build_blocker_map.py`
(read-only; `--write` deliberately not run, three waves regenerating one derived
file would collide):

    frozen GAP rows at 1c08e5f    409
    assigned from committed        385
    UNASSIGNED                      24

The 24 are exactly the set named in my brief. **One correction to the brief's
navigation, not its content:** the brief says the unassigned rows carry an EMPTY
column 2 in `_audit/_census/blocker-map.tsv`. They do not -- they carry the
literal token `UNASSIGNED` in both column 2 and column 3. A reader filtering on
emptiness finds nothing and could conclude the set is closed.

**The venv is gitignored, so it is absent from every worktree** (the standing
worktree hazard). `./venv/Scripts/python.exe` does not exist here; the main
checkout's interpreter was used against this worktree's files.

---

## 1. THE TRAP AT THE TOP, BECAUSE IT WILL COST SOMEBODY A DAY

Summing every unfilled slot across the published division at this tree:

    PARTIAL blockers   13   slots open   16
    ABSENT  blockers    4   slots open    8
    ------------------------------------------
    TOTAL OPEN SLOTS                     24
    UNASSIGNED ROWS                      24

**24 and 24. It is a coincidence, and treating it as a closure argument is the
single most expensive mistake available in this file.** Neither sibling can see
this identity, because each holds only one half of it (16 or 8). I can, and the
first thing to do with it is disarm it.

**Three independent proofs that the matching is NOT one-to-one**, each resting
on a committed source rather than on my arithmetic:

1. **`FOUND-A-JOB-FLOW` (1W) has no census row at all.**
   `_audit/2026-09-19-the-empty-blockers.md:240-250` measured it: *"The strings
   'found a job' and 'no longer looking' appear nowhere in any census file...
   this may be a row that was never enumerated rather than one that is lost."*
   I re-ran that search and confirm zero hits across `_audit/_census/`. A
   published slot pointing at no row.

2. **`HASHTAG-EXISTENCE`'s open slot cannot take any unassigned row**, because
   the ledger's own amendment enumerates that blocker's three rows BY ID
   (`_audit/2026-09-03-linkedin-gap-blockers.md:1174-1177`) and none of the
   three is unassigned. Section 4.12 below.

3. **`P B8` is not a row wanting a blocker, it is a duplicate wanting
   subtraction** -- same capability, same Help Center article id, same reason
   cell as `P K9`. Section 4.23. If the duplicate register takes it, the pool is
   23 rows against 24 slots.

**So at least one slot has no row and at least one row has no slot, in the same
division.** The equality is two independent errors landing on the same integer.
This corroborates, by a different route, the finding at
`_audit/2026-09-19-routing-the-unassigned.md:150-163` -- *"some rows have no
hole, and some holes have no row"* -- which reached it from a 26-vs-24 gap that
has since closed to 24-vs-24. **Its arithmetic moved; its conclusion did not.**
That is a stronger result than the original, because the conclusion now survives
the disappearance of the evidence that first suggested it.

**Therefore no row below is filed on counting alone.**

---

## 2. THE METHOD, STATED BEFORE THE VERDICTS SO IT CAN BE CHECKED AGAINST THEM

A committed source naming the row, at a locator a reader can open. The standing
classes: `LEDGER-EXPLICIT`, `LEDGER-AMENDMENT`, `RECON-CENSUS-COMMITTED`,
`RECON-DOC`.

**The one discriminator I allowed myself, and the line it draws:**

> A committed enumeration forces rows only when the enumeration is CO-EXTENSIVE
> with the blocker -- same family, same count, and the split closes with zero
> headroom. An enumeration LARGER than the blocker (18 census rows against a
> 1-row blocker) cannot force anything; getting from it to a single row takes
> elimination, and elimination is what this campaign has refused all round.

That line is why I file `M M35` and `M M49` (an 11-member census group against a
10-slot blocker, one member already filed elsewhere, split closing exactly) and
do NOT file `M M5` (an 18-member census group against a 1-slot blocker), even
though `M M5` is the more satisfying find. **The rule was fixed before either
verdict, and it cuts against my own best discovery.**

---

## 3. WHAT I FILE -- TWO ROWS, AND THEY CLOSE A BLOCKER

### `CONVERSATION-OVERFLOW-MENU` 8 of 10 -> 10 of 10: `M M35`, `M M49`

Published `10 | 1R/8W/1RW` at `_audit/2026-09-03-linkedin-gap-blockers.md:187`.

**THE SOURCE IS A COMMITTED CENSUS ENUMERATION AND IT IS CO-EXTENSIVE WITH THE
BLOCKER.** `_audit/_census/messaging-and-content.md:498`:

> **Conversation management** (archive, restore, mute, star, mark read/unread,
> bulk, leave, **layout**, windows, search, **delivery indicators**) | 11 | W |
> REV except leave | **Every one is a per-conversation overflow-menu item** and
> that menu has never been opened

Eleven members. Ten published slots. Mapping each member to its row and its
current blocker:

    archive              M27   filed   LEDGER-AMENDMENT
    restore              M28   filed   LEDGER-AMENDMENT   (the 1RW)
    mute                 M29   filed   LEDGER-AMENDMENT
    star                 M30   filed   LEDGER-AMENDMENT
    mark read/unread     M31   filed   LEDGER-AMENDMENT
    bulk                 M32   filed   LEDGER-AMENDMENT
    leave                M25   filed   LEDGER-AMENDMENT
    windows              M36   filed   LEDGER-AMENDMENT
    search               M34   filed ELSEWHERE -- MISSING-PARAM-MESSAGING
    layout               M35   UNASSIGNED   W   (messaging-and-content.md:366)
    delivery indicators  M49   UNASSIGNED   R   (messaging-and-content.md:380)

**Eleven members, one filed elsewhere, ten remain for ten slots.** The split
closes with zero headroom: `M28` is the `1RW`; `M49` is the `1R`; `M25 M27 M29
M30 M31 M32 M36 M35` are the `8W`. **Both count and split close exactly, and
neither can be extended without over-running the published number.**

**Direction is taken from the PER-ROW column, not a range-keyed one.** This
matters because the range-keyed column was the subject of Request 4. Here the
census's section-1 table states it row by row: `M49 | Read message delivery /
read indicators | a569649 | GAP | R | REV` and `M35 | Choose Messaging inbox
layout | a7449032 | GAP | W | REV`. A per-row cell is strictly stronger than the
grouped column that ruling adjudicated.

**BOTH ROWS WERE REFUSED BY A COMMITTED RULING AND I AM OVERTURNING BOTH
GROUNDS, SEPARATELY.**

**`M M35` -- the stated ground was arithmetic and it has expired.**
`_audit/2026-09-19-the-three-ruling-requests-ruled.md:53-58` refused it because
*"A row admitted by a count it SHARES WITH A RIVAL is not admitted"*; the rival
was `M M10`. The same ruling, at its line 68, sent `M M10` to
`THREAD-REPLY-BOX`, and `M M10` is filed there today. **The rival is gone by the
ruling's own instruction.** (`_audit/2026-09-19-routing-the-unassigned.md`
reported this too; I reached it independently and confirm it.)

The ruling's *other* objection -- that `M35` fails the single-conversation test
-- does not survive contact with the blocker's own membership. **`M36` "Manage
how new conversations open (conversation windows)" is an inbox-level setting,
not an act on one conversation, and it is filed to this blocker by
`LEDGER-AMENDMENT`.** The ledger's own author already placed a non-per-
conversation row here. A discriminator the blocker's existing membership already
violates cannot exclude a new row.

**`M M49` -- the stated ground is substantive and it misidentifies the row.**
The ruling refused it saying *"Read receipts are a setting, not a menu item."*
**That sentence describes `M37`, not `M49`.** `M37` "Turn read receipts and
typing indicators on or off" is the setting, and it is filed to
`MESSAGING-SETTINGS` (`messaging-and-content.md:368`). `M49` is *"**Read**
message delivery / read indicators"*, and its own cell draws the distinction
explicitly: *"`linkedin_open_messaging` returns per-row unread flags for HIS
state; **the sender-side indicators are a different signal** and were never
enumerated."* Observing a sender-side indicator is not toggling a preference.

**This is the disagreement I most want a sibling to check.** The routing pass
noticed `M35`'s ground had moved but ACCEPTED `M49`'s as substantive
(`routing-the-unassigned.md:199-202`, *"so on that reading `M M49` has no home
at all"*). I am refuting the substantive ground itself, by reading the two rows
side by side.

**Filed as `RECON-DOC`**, appended to `_audit/_census/blocker-assignments.tsv`.
Nothing already in that file was rewritten.

---

## 4. WHAT I DECLINE -- TWENTY-TWO ROWS, EACH WITH ITS REASON

### 4.1-4.2 `J 18`, `J 19` -- recent searches, view and clear

**DECLINED, AND I AM RAISING THE SLOT AS CONTESTED. This is my strongest
disagreement with the already-recovered 385.**

`SEARCH-HISTORY-SURFACE` is published `2 | 1R/1W | allowlist +1, denylist x1,
WriteSpec`. The map holds it COMPLETE with `N 95` (R) and `N 96` (W).

**The jobs pair matches the published BOUNDARY; the network pair carries no
boundary evidence at all.** `_audit/_census/jobs.md:428`:

> 18-19 | recent searches read / clear | **a new read surface
> (`/jobs/search-history/` or equivalent) on the allowlist**; the clear is a
> destructive verb and `"delete"`/`"remove"` are **on the mutation-verb
> denylist** | R + W | clear is NOT reversible

That is all three published components -- allowlist +1, denylist x1, WriteSpec
-- plus a NAMED ADDRESS, in one sentence. Against it, `network.md:351-352`:

    | 95 | View and re-run a recent search | R | GAP | |
    | 96 | Clear your search history      | W | GAP | NOT-REV |

**An empty reason cell and the string `NOT-REV`.** Measured: `network.md`
mentions search history in exactly those two lines and nowhere else, and that
slice has no "what each gap would take" section. There is no boundary text for
`N 95`/`N 96` anywhere in the corpus.

**And the filing that holds the slots was admitted by count and split alone.**
`_audit/2026-09-05-settings-tail.md:222` files them with its method stated
against itself: *"Row ids located and cross-checked (**row-level lookup
delegated**; verified against the ranked table's own counts and R/W splits)."*
`J 18`/`J 19` match that count (2) and that split (1R/1W) identically. **By the
standing rule that a row admitted by a count it shares with a rival is not
admitted, that filing does not survive the existence of the rival.**

**The same document's headline claim is falsified if its rows are the jobs
pair.** Its finding is *"Not one of the eight names an in-product address"* --
true of `N 95`/`N 96`, false of `J 18`/`J 19`, which name `/jobs/search-history/`.

**MY DIAGNOSIS IS NOT "SURPLUS", IT IS A MISSING BLOCKER.** `N 95`/`N 96` sit in
`network.md` section H, *People search and discovery*; `J 18`/`J 19` are job
search history. The ledger's own MERGE RULE
(`2026-09-03-linkedin-gap-blockers.md:160-163`) says *"two blockers merge only
when THE SAME SINGLE ACTION closes both. Different surfaces stay different
blockers."* People-search history and job-search history are different surfaces,
so the division should carry TWO blockers here and carries one.

**I did not unfile `N 95`/`N 96`** -- not my rows, and an append-only file is not
the place to contest somebody else's line. **Ruling request A.**

### 4.3-4.7 `J 78`, `J 79`, `J 80`, `J 82`, `J 83` -- Premium apply extras

**DECLINED, concurring with three prior declines, and I add one observation.**

`PREMIUM-APPLY-SURFACES` publishes 5. A committed probe names six:
`scripts/_probe_jobs_tail_boundary.py:63` -- `# 61 PREMIUM-APPLY-SURFACES --
census rows J78-J83`. (Confirmed that `61` there is the LEDGER INDEX, not a row
id -- the false-positive class registered at
`_audit/2026-09-19-the-empty-blockers.md:255-259`. I re-derived it independently
from the ledger table before reading that registration.)

Six candidates, five slots, and **the `1R` that once separated them has been
retired as a discriminator** by Request 4
(`2026-09-19-the-three-ruling-requests-ruled.md`, *"That `1R` may no longer be
cited as evidence in any filing"*), after `J 82` was filed on it and retracted at
`0aca3d0`. No discriminator remains.

**WHAT I ADD: the blocker is a merge the ledger's own merge rule forbids.**
`jobs.md:437` says of this exact group *"**each is a distinct surface**"*. The
merge rule admits a merge only when one action closes both. Six distinct
surfaces under one blocker is not a classification, it is a bucket -- which is a
better explanation for the six-against-five than a lost sixth slot.

### 4.8 `J 81` -- verify account to raise the Easy Apply limit

**DECLINED, AND RAISED AS A RULING REQUEST AGAINST A COMMITTED RULING.**

`ACCOUNT-VERIFICATION` is published 3 and holds `P A24` and `P N14`. `J 81` is
the only verification-shaped row left in the corpus. Request 2a
(`2026-09-19-the-three-ruling-requests-ruled.md`) ruled against moving it:

> The recommendation was to drop `J 81` on a subject test -- *the subject is the
> account rather than an application.* **That test is the reader's.** The
> census's own sectioning is the source's, and it places `J 81` in section D,
> Applying.

**I think that ruling answers the wrong question, and the ledger supplies the
right one.** The ASSIGNMENT RULE
(`2026-09-03-linkedin-gap-blockers.md:166-169`) is itself a committed first-party
rule: *"one blocker per row, the EARLIEST binding constraint."* Section D says
what the capability is FOR (applying). The assignment rule asks what stops it
FIRST, and what stops `J 81` first is that no account can be verified. **Purpose
and blocker are different axes, and the ledger names the blocker axis
explicitly.**

Two supports. **The section test proves too much:** `J 78`-`J 83` are ALL in
section D, so sectioning cannot discriminate within the block it is being used to
defend. **And the blocker already spans slices:** its two filed rows are both
`profile.md` rows, so "wrong slice" was never the bar.

**If this ruling flips, six rows resolve at once and two blockers close** --
`ACCOUNT-VERIFICATION` at 3 of 3, and `J 78 79 80 82 83` becoming exactly five
for `PREMIUM-APPLY-SURFACES`' five slots. **That is precisely why I am not
filing it.** An outcome that tidy is the strongest possible motive to misread the
evidence, and the tidiness is not itself evidence. **Ruling request B.**

### 4.9-4.10 `J 99`, `J 100` -- career-interests visibility, signal interest

**DECLINED. Surplus to a blocker that closes without them on a
LEDGER-AMENDMENT-grade source.**

`jobs.md:439` groups them: *"92-100 | every job-preference FIELD, Minimum Pay,
**recruiter visibility** | all live behind the same modal as rows 89-91."* Nine
jobs rows plus `P I13`-`I16` is thirteen candidates; `OPEN-TO-WORK-MODAL`
publishes eleven and is COMPLETE on Amendment E's frozen-set membership.

**The census names them in the family and the division has no room.** No other
blocker is named for job preferences. The map's own note already records this as
the open question; I reach the same verdict independently and add nothing that
would move it. (`J 99` is additionally EXCLUDED-RULED today by container
inheritance from `P I12`; that changes its state, not its frozen membership.)

### 4.11 `J 150` -- enhanced recruiter message, Writing Assistant

**DECLINED. A committed source names the fork and the census picks the side with
no room on it.**

`_audit/2026-09-05-decide-retire-rulings.md:84` -- *"`AI-ASSIST-MESSAGING` |
`M M40`, `M M51` | 2/2 | 2W matches | **DERIVED** -- three rows share the family
(`J 150` is the third)"* -- and line 115 states the alternative: *"`J 150`, if
Writing Assistant was read as AI-assist rather than as an addressing failure."*

**The census reads it as neither.** `jobs.md:447`: *"US-only Premium overlay on a
compose surface. Blocked behind the same wall as `send_message`: **nothing here
can verify a send**."* That is a send-VERIFICATION wall. It is not the
ADDRESSING wall (`messaging-and-content.md:496`, *"no working way to address a
human being"*), and no published blocker is named for send-verification.

So: AI-assist reading -> blocker full at 2/2. Addressing reading -> the census
does not make it. **Genuinely ambiguous, and the ambiguity is the source's own.**

### 4.12-4.13 `N 59`, `N 60` -- follow and unfollow a hashtag

**DECLINED, AND THE DECLINE IS FORCED BY A COMMITTED ROW-ID ENUMERATION RATHER
THAN BY A COUNT. This is a stronger reason than the one on record.**

The ledger's amendment (`2026-09-03-linkedin-gap-blockers.md:1174-1177`)
enumerates this blocker's three published rows in a table, by id:

    | row     | as published        | at HEAD                          |
    | `N 194` | `HASHTAG-EXISTENCE` | `SEARCH-RESULTS-SURFACE`         |
    | `C 11`  | `HASHTAG-EXISTENCE` | EXCLUDED-RULED, not GAP          |
    | `C 52`  | `HASHTAG-EXISTENCE` | `HASHTAG-EXISTENCE`, unchanged   |

**"As published" is the frozen division. The three rows are `N 194`, `C 11`,
`C 52`.** Neither `N 59` nor `N 60` is among them, and no count-based argument is
needed to say so. The prior decline
(`routing-the-unassigned.md`) rested on the two rows being rivals for one slot;
correct in outcome, but the enumeration settles it outright.

**A CONSEQUENCE I MUST REPORT: `N 61`'s filing looks wrong.** The map files
`N 61` to `HASHTAG-EXISTENCE` as `RECON-DOC`, reasoned as *"the only R"*. The
amendment's enumeration excludes it, and a `RECON-DOC` inference cannot outrank a
`LEDGER-AMENDMENT` row-id list. **The blocker's open slot belongs to `C 52`,
which is currently filed to `FEED-PREFERENCES`.**

**And the map is reading two different columns of that table at once:** it took
the "at HEAD" column for `N 194` (filed to `SEARCH-RESULTS-SURFACE`) and the "as
published" column for `C 11` (filed here). Membership is a fact about the frozen
set; one column has to govern. **Not my row and not my file to repair --
reported. Ruling request C.**

### 4.14-4.15 `N 41`, `N 42` -- follow a member from an article, unfollow articles

**DECLINED. Two write candidates, one write slot, no discriminator.**

`ARTICLE-SURFACE` publishes `6 | 1R/5W` and holds `C46 C48 C49 C78 C79` -- one W
slot open. Both `N 41` and `N 42` are W (`network.md:269-270`), and both reason
cells read, in full, `REV`. **No cell, no enumeration and no ruling separates
them.**

The standing decline calls them *"cross-slice duplicates of `C79`"*
(`routing-the-unassigned.md`). **I think that is half right and the wrong half is
load-bearing.** `M C79` is *"Follow or unfollow member articles"* -- a BUNDLED
row -- and the cross-slice wave's own rule
(`2026-09-19-cross-slice-rulings.md:687-690`) says *"**A bundled row is not a
clean duplicate and must not be subtracted as one**."* So `N 42` is at most a
partial duplicate, and `N 41`, whose object is the MEMBER rather than the
articles, is not obviously one at all. **The decline stands on the rival-sharing
ground; it should not stand on the duplicate ground.**

### 4.16 `N 51` -- mute a company

**DECLINED, and the exclusion is positive rather than an absence.**

No published blocker is named for muting; the row's cell is *"REV. `mute` 0
hits"*, and its sibling `N 43` (mute a person from a feed post) is filed to
`FEED-ITEM-OVERFLOW-MENU`, COMPLETE at 5 of 5.

**`COMPANY-PAGE-SURFACE` has two open slots and does NOT admit this row:**
`network.md` section 6 enumerates that family by id -- *"**Company pages** | 33,
47, 53, 54, 101, 102, 104 (7)"* -- and 51 is not in it. **A committed
enumeration excludes it from the only open blocker it resembles.**

### 4.17 `M C82` -- share a Newsletter Page

**DECLINED, and I can name what displaced it.**

`NEWSLETTER-SURFACE` is COMPLETE at 12 of 12. The census's own group names share
as a member -- *"Newsletters (create, manage, multiple, Newsletter Page,
**share**, subscribe/unsubscribe)"*.

**The twelve that hold the slots include a confirmed duplicate pair.**
`_audit/2026-09-19-cross-slice-rulings.md:681` lists *"`P L4` / `M C83`
newsletter analytics 0.778"* among its confirmed cross-slice duplicates, and
BOTH are filed here. Line 689 adds that `M C80` *"Subscribe or unsubscribe"*
bundles `N 55` and `N 56` -- and all three of those are filed here too.

**So the blocker is not full of twelve distinct capabilities; it is full of
duplicates, and `C82` is a distinct capability crowded out by them.** If the
duplicate register subtracts `P L4`, `C82` has a forced home. **Ruling request D**
-- and note it is discharged by the duplicate register rather than by a blocker
ruling.

### 4.18 `M M5` -- send an Open Profile message

**DECLINED BY MY OWN STATED RULE, AND IT IS THE DECLINE I LIKE LEAST. This is my
most likely disagreement with the wave working the absent blockers.**

`MESSAGE-ADDRESSING` is published `1 | 1W` and is EMPTY. The standing position
(`_audit/2026-09-19-the-empty-blockers.md:240-246`) is that no committed source
names a census row for it.

**There is a candidate, and it is strong.** `messaging-and-content.md:496` names
an 18-row group including *"**Open Profile**"* whose stated blocker is exactly
this one: *"All blocked upstream by s3.1: **there is no working way to address a
human being on this surface**."* The same line carves out exactly one exception
-- *"`M47` is the exception worth pulling forward -- responding to an inbound
Recruiter InMail **needs no addressing at all**"*. Of that group, every member
but `M M5`, `M M13` and `M M47` is filed elsewhere; `M47` is carved out by the
source; `M13` has an unrivalled home at `PER-MESSAGE-OVERFLOW-MENU`. And in the
send-a-message family `M1`-`M5`, **`M M5` is the only row that was GAP at the
freeze** -- `M1` and `M2` are COVERED-CANNOT-DELIVER, `M3` and `M4`
EXCLUDED-RULED -- against a blocker publishing exactly one row, and the direction
matches (`M5` is W).

**I am not filing it, because the enumeration is 18 rows against a 1-row blocker
and only elimination gets from one to the other.** That is the line I drew in
section 2 before I found this, and it would be worth nothing if I moved it now.
**Ruling request E, with my recommendation: file it.**

**A related correction for whoever rules:** `_audit/2026-09-19-blocker-table-
refresh.md:37` identifies this blocker's row as `M 1`. `M 1` is
COVERED-CANNOT-DELIVER in the census (`messaging-and-content.md:332`) and is
absent from the frozen 409 -- the map's M-block starts at `M M5`. **`M 1` cannot
be this blocker's published row**, so that identification should not be relied on
to keep the slot shut.

### 4.19 `M M13` -- forward a message

**DECLINED. Best candidate, no rival, still not forced -- and the difference
from `M35`/`M49` is the whole point.**

`PER-MESSAGE-OVERFLOW-MENU` publishes `2W` and holds `M M11` (edit a sent
message). Among the per-message actions in the census's composition group, react
has `MESSAGE-REACTION`, reply-in-thread has `THREAD-REPLY-BOX`, edit has this
blocker -- **forward is the only per-message action left without a named
blocker, and there is no rival for the slot.**

**But no committed source puts it in that menu.** `M11`'s cell opens *"per-
message overflow menu, never opened"*; `M13`'s cell
(`messaging-and-content.md:344`) reads *"never named; forwards a third party's
words to another third party"*. The composition group that contains both is 18
rows spanning many blockers -- **not co-extensive with this 2-row blocker**, so
by my own rule it cannot force. Concurs with
`_audit/2026-09-19-the-empty-blockers.md:234-237`, *"admitted by resemblance...
chosen, not forced."*

### 4.20 `M M35`, 4.21 `M M49` -- FILED, see section 3.

### 4.22 `M M47` -- respond to a Recruiter InMail

**DECLINED. The census positively excludes it from the only wall that would have
placed it, and no published blocker replaces it.**

`messaging-and-content.md:496` carves it out of the addressing group by name:
*"`M47` is the exception worth pulling forward -- responding to an inbound
Recruiter InMail needs no addressing at all, because the thread already exists
and is already on the read allowlist."* Its own row (line 378) calls it *"a
structured response with its own affordances, and... the single most job-hunt-
relevant messaging action in this slice."*

**A row the census singles out as needing only a `WriteSpec` on an already-
allowlisted surface, and the published division has no name for it.** This reads
as a missing blocker rather than a lost row, and unlike the rest of the residue
it is cheap: no new address, no capture.

### 4.23 `P B8` -- Top Voice badge show / hide

**DECLINED, and it does not belong in this backlog at all. It belongs in the
duplicate register.**

    profile.md:244 | B8 | Top Voice badge show / hide | W | GAP | `a1577365`; no tool, no reason |
    profile.md:420 | K9 | Show / hide the Top Voice badge | W | GAP | `a1577365`; no tool, no reason |

**Same capability, same Help Center article id, same reason cell, verbatim.**
`P K9` holds the `BADGES-SURFACE` slot on a tiebreak the ruling itself recorded
as *"A PICK RESOLVED ON A WEAK TIEBREAK, not an inference from evidence. It is
not a precedent."*

**`P B8` is therefore not an unassigned row; it is a duplicate awaiting
subtraction**, and while it is counted as a row wanting a blocker the residue is
overstated by one. This is the third proof in section 1.

### 4.24 `P D24` -- open to volunteering

**DECLINED, concurring, and the arithmetic that nearly forced it is the reason to
distrust it.**

`OPEN-TO-HIRING-MODAL` publishes `5 | 1R/4W` and holds `P J1 J2 J3` (W) and
`P J4` (R) -- one W slot. `D24` is a W whose cell names the same control as
`J1`'s: *"Reached from the `Open to` button, one of the three items measured on
his account."* **The arithmetic closes exactly, and it should not be allowed to.**
The blocker is named HIRING; this row is volunteering; the ledger carries a
separate blocker per `Open to` item (`OPEN-TO-WORK-MODAL`,
`SERVICES-PAGE-SURFACE`), so a volunteering row wants a fourth that does not
exist. A wave routed here opens the wrong tab.

**THE SLOT'S OTHER CANDIDATE IS ALSO DEAD, which makes this a hole with no row.**
`P B7` *"#Hiring photo frame apply / remove"* is the same capability as `P J2`
*"#Hiring photo frame add / remove"*, which is **already filed to this blocker**.
A duplicate of a row already inside cannot fill the slot beside it. So
`OPEN-TO-HIRING-MODAL`'s fifth slot has no valid candidate at all -- a fourth
independent confirmation of section 1.

---

## 5. SUMMARY

| row | verdict | blocker | ground |
|---|---|---|---|
| `J 18` | DECLINE - contested slot | `SEARCH-HISTORY-SURFACE` | boundary evidence favours it over the filed `N 95`; request A |
| `J 19` | DECLINE - contested slot | `SEARCH-HISTORY-SURFACE` | as `J 18`, against `N 96` |
| `J 78` | DECLINE | `PREMIUM-APPLY-SURFACES` | 6 named for 5 slots; discriminator retired |
| `J 79` | DECLINE | as above | as above |
| `J 80` | DECLINE | as above | as above |
| `J 81` | DECLINE - ruling request B | `ACCOUNT-VERIFICATION` | assignment rule selects the act; ruling used sectioning |
| `J 82` | DECLINE | `PREMIUM-APPLY-SURFACES` | filed once on the `1R` and retracted at `0aca3d0` |
| `J 83` | DECLINE | as above | as above |
| `J 99` | DECLINE | `OPEN-TO-WORK-MODAL` | census names it in the family; blocker COMPLETE without it |
| `J 100` | DECLINE | as above | as above |
| `J 150` | DECLINE | none forced | source names the fork; census picks the full side |
| `M M5` | DECLINE - ruling request E | `MESSAGE-ADDRESSING` | strong, but 18-row group vs 1-row blocker |
| `M C82` | DECLINE - ruling request D | `NEWSLETTER-SURFACE` | displaced by a confirmed duplicate pair inside the blocker |
| `M M13` | DECLINE | `PER-MESSAGE-OVERFLOW-MENU` | unrivalled but unnamed; chosen, not forced |
| `M M35` | **FILE** | `CONVERSATION-OVERFLOW-MENU` | census group of 11 closes on 10; rival left by ruling |
| `M M47` | DECLINE | none exists | census carves it out of the addressing wall by name |
| `M M49` | **FILE** | `CONVERSATION-OVERFLOW-MENU` | the only `R` left in the group; refusal described `M37` |
| `N 41` | DECLINE | `ARTICLE-SURFACE` | two W candidates, one W slot |
| `N 42` | DECLINE | as above | as above |
| `N 51` | DECLINE | none exists | excluded from company family by row-id enumeration |
| `N 59` | DECLINE | `HASHTAG-EXISTENCE` | amendment enumerates the 3 rows; not among them |
| `N 60` | DECLINE | as above | as above |
| `P B8` | DECLINE - duplicate register | n/a | identical capability, article id and cell as `P K9` |
| `P D24` | DECLINE - ruling request | `OPEN-TO-HIRING-MODAL` | arithmetic closes; the name does not |

**UNASSIGNED 24 -> 22.**

---

## 6. WHERE I MOST EXPECT A SIBLING TO DISAGREE

Ranked by how informative the disagreement would be.

1. **`M M35` / `M M49`.** I file two rows a committed ruling refused. A sibling
   working `CONVERSATION-OVERFLOW-MENU` from the blocker side sees the same two
   holes and the same `1R`/`1W` split, and may well honour the ruling. **If they
   decline, the question to settle is narrow: does `messaging-and-content.md:498`
   enumerate this blocker, or merely resemble it?**
2. **`J 18` / `J 19`.** I say the filed `N 95`/`N 96` are the weaker claim. A
   blocker-side wave reads `SEARCH-HISTORY-SURFACE` as COMPLETE and never opens
   the question.
3. **`M M5`.** The absent-blockers wave owns `MESSAGE-ADDRESSING`. I found a
   candidate and declined it on a rule; they may file it, or may still be
   working from the `M 1` identification I show cannot be right.
4. **`J 81`.** I argue against a ruling that was already made once, deliberately,
   with reasons. A sibling that honours it is not obviously wrong.
5. **`N 61`** is not my row and not in my set, but I report it as a probable
   mis-assignment inside the recovered 385. **A census with one wrong filing in
   it is worse than one with a hole**, and this is the only one I found.

## 6b. TWO ROW-ID ENUMERATIONS SWEPT AFTERWARDS, BECAUSE THAT CLASS HAS BEATEN THIS CAMPAIGN TWICE

Row-id enumerations are the strongest class in this corpus short of the ledger,
and two separate passes have been refuted by one they had not swept. So all four
slices were re-swept for enumerations covering my 24. **Two were found. Neither
changes a verdict; both sharpen one.**

**`profile.md:563-566` -- section 5.3, "Surfaces nobody in this repo has ever
named (64)":**

    A23, A24, B7-B10, C8, D24, D25, D27-D29, E6, E7, F1, F2, F6-F9, G2, G6, G7,
    H1-H11, I13-I16, J1-J4, K8-K10, L1-L8, M11, M12, N12-N14, N25, N30, N31,
    O3, O5, O23

It covers `P B8` and `P D24`. **It cannot force either** -- 64 rows against any
blocker is the non-co-extensive case my section-2 rule excludes. What it does do
is put `B7`-`B10`, `J1`-`J4` and `K8`-`K10` in ONE enumerated bucket, which is
where both duplicate pairs I rely on live: `B8`/`K9` (section 4.23) and
`B7`/`J2` (section 4.24). **Both pairs are intra-bucket, so neither rests on my
pairing them across unrelated parts of the slice.**

**`network.md:1026` -- section 9.2, "Attempted and NOT reached -- named holes":**

> **Hashtag following** (`answer/a528144`) | 404 on all four URL forms tried |
> **Rows 59-61** are a floor, not a saturation claim

**This makes the `N 61` anomaly worse, and it is the reason I am reporting it
rather than leaving it.** The census groups 59, 60 and 61 as ONE family with one
cause. The ledger amendment enumerates `HASHTAG-EXISTENCE`'s three published rows
as `N 194`, `C 11`, `C 52` -- **none of the three.** So either all three of
59-61 belong to that blocker (and it is published at 3 with the wrong three), or
none does. **`N 61` alone is the one combination no source supports**, and it is
the combination the map currently holds.

The same section also carries a named hole for `N 51`: *"**Mute article** ...
the body served contained zero mute content across three URL forms. Mute's
EXISTENCE is established from two other directly-fetched pages; the exact mute
mechanics are not."* Consistent with section 4.16 -- mute is a measured hole in
the census, not a blocker in the division.

---

## 7. WHAT THIS DOES NOT CLAIM

Locating a row does not measure it, unblock it or schedule it. All 24 remain GAP
or EXCLUDED-RULED for the reasons their cells give. The two rows I filed are
`MEASURE`-blocked on a conversation overflow menu nobody has opened, exactly as
they were before I named their blocker.

**I did not read what either sibling filed, and I did not divide the set with
them.** Every verdict above is reached from the corpus.
