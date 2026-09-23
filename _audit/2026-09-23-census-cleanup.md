claude-opus-5-5[1m]

# Census cleanup: six statements the census makes about itself, measured against today

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `C42` read *"no tool in this server returns one"* (a post identifier); since `C41` was proven today, `linkedin_my_activity_items` returns one for every post of his own. The premise still holds for other people's posts, and the state is not re-decided.

**CORRECTS:** `_audit/2026-09-23-bucket3-addresses.md` -- it sized "blocked on nothing" at 5 of 67 without asking the rulings, counting `M M49` on a messaging thread while `DO-NOT-OPEN-MESSAGING` stood, which made the size 4. The operator lifted that ruling at 18:15 the same day, so the size is 5 again under the rulings as they now are, and the checker now asks them.

Wave `census-cleanup`, 2026-09-23, from master `b0d3ab8` (the merge of the
bucket-1 and bucket-3 waves). **OFFLINE THROUGHOUT.** No browser was started or
attached to, no page was loaded, port 9224 and the persistent profile were not
touched. Everything below is the census, the shipped boundary called
in-process, the rulings register, and the scripts that read them.

**WRITTEN AS THE WAVE RUNS.** Section 0 was written before any file was edited.

**AND THE RULINGS MOVED MID-WAVE.** At 18:15 IST the operator made a ruling that
reached this wave at about 18:25, after its second commit; section 7 records it
and what it changed. Sections 1 to 6 keep what was measured and built before
it, each opening with its state AFTER it:

    item 1        bucket 1 is 0 standing / 17 waiting on a live proof against
                  a target he names / 2 pending / 2 on no ruling
                  (before: 15 + 2 held by standing rulings / 2 / 2)
    item 6        blocked on nothing is 5 of 67 (it was 4 for part of the
                  day); the edge stays, reading the holds as they now are
    items 2 to 5  unchanged by the ruling, except that C42's cell now says
                  C25 and C32 wait on a named target

---

## 0. THE PLAN, WRITTEN BEFORE ANY EDIT

### 0.1 The denominator: six items, all six to be done

| # | the statement | where it lives | what today's measurement says |
|---|---|---|---|
| 1 | bucket 1 is "blocked on a live browser session ... a session is the entire remaining cost" | `scripts/census_completion.py` | the bucket-1 audit, section 3: of the 21 COVERED-UNFIRED rows, 15 are writes held by the standing write ruling, 2 are held by the standing messaging ruling, 2 wait on an operator question about the notifications badge, 2 need a press or a reader change. A session is the whole cost for none of them |
| 2 | row `M C42`: "no tool in this server returns one" (a post identifier) | `_audit/_census/messaging-and-content.md` | `linkedin_my_activity_items` returned eight activity keys live today for his own posts (`M C41`, COVERED-PROVEN) |
| 3 | `M C83` is listed under decision D3 | `scripts/census_completion.py::RULING_BLOCKED_NAMED` | the shipped boundary's newsletters comment: the refused spelling was never observed served, and the row waits on a live read. D3 answered either way leaves it where it is |
| 4 | the read triage's verdict table | `scripts/triage_read_gap_rows.py` | red at HEAD: five rows it holds verdicts for (`N 33`, `N 53`, `N 54`, `N 83`, `N 175`) are no longer GAP |
| 5 | (absence) nothing runs item 4's script | `tests/` | that absence is how it went red unannounced |
| 6 | bucket 3's "blocked on nothing" is 5 of 67 | `_audit/_census/read-addresses.tsv`, the bucket-3 audit, `scripts/census_completion.py` | the split never consulted standing rulings; `M M49`'s page is a messaging thread, and `DO-NOT-OPEN-MESSAGING` forbids opening messaging |

### 0.2 Design decisions, taken before building

* **Bucket 1 is DERIVED, not typed (item 1).** The hold of each COVERED-UNFIRED
  row comes from the census itself: its R/W cell where it has one (every W row
  is held by `NO-IRREVERSIBLE-WRITE-IS-FIRED`, which binds every write), and
  otherwise the ruling or question its own cell CITES as its hold, with a
  marker a parser can read. `jobs.md` has no R/W column and
  `_audit/2026-09-21-the-jobs-direction.md` argues against adding one, so its
  three unfired writes cite the write ruling in their cells instead; a hold
  citation is not a direction column. Rows citing nothing are "held by no
  ruling", and the two that are (`J 121`, `J 122`) say in their own cells why.
* **The sub-counts are pinned, and so is the ROW MEMBERSHIP of each.** A count
  pin cannot see two rows swapping holds; a row pin names the row that moved.
* **`census_completion.py` still runs in a copy holding only `scripts/`,
  `_audit/_census/` and the row pin** (`scripts/_check_census_completion_can_fail.py`
  builds exactly that). The rulings register is importable only with `tests/`
  present, so the completion figure counts citations and does NOT resolve them;
  resolving every cited id against the register is a separate checker's job,
  the architecture the bucket-3 wave used for its source column.
* **A new gate for bucket 3 (item 6), because the existing one would say
  something untrue.** The gate `RULING` means "a named, UNMADE decision comes
  first". `DO-NOT-OPEN-MESSAGING` was made on 2026-08-31. Filing `M M49` under
  `RULING` would put a decided question back into the operator's open queue, so
  the row gets `STANDING-RULING`: a ruling already made holds the page, and what
  would move the row is lifting or narrowing it.
* **The checker edge (item 6) reads its rulings from one place.** A small table
  names each ruling that holds a SURFACE, with the surface; a standing entry is
  re-resolved against the register's own BINDS value on every checker run, and
  a pending entry is re-resolved against the document that put the question and
  fails the moment a registered ruling binds the same surface (the question has
  then been answered, and every row citing it needs re-reading).
* **The sibling wave's four rows are not edited.** `P O3`, `N 134`, `M C72` and
  `M C85` belong to the live wave firing them today: their census cells and their
  lines in the address table are untouched here. Anything item 6 finds about
  them is recorded in section 6 for the orchestrator to apply at merge.

### 0.3 Forced predictions, logged before building

* Item 6: of the 33 ADMITTED rows, exactly ONE (`M M49`) sits on a surface a
  standing ruling forbids, and blocked-on-nothing falls **5 -> 4**. The other
  standing rulings either permit the pages the 33 sit on or bind acts none of
  them performs.
* Item 1: the derivation reproduces the bucket-1 audit's 15 / 2 / 2 / 2 with no
  row in a different bucket from the one that audit typed.
* Item 4: removing the five rows turns the script green with no other edit
  needed, and the table holds 54 verdicts afterwards.

### 0.4 Stop rule

Nothing live, whatever a measurement suggests. A finding that would need a
browser is written down and left.

---

## 1. ITEM 1 -- BUCKET 1, DERIVED FROM THE CENSUS AND THE RULINGS

**AFTER 18:15 (section 7), THE SAME DERIVATION PRINTS:**

    held by a STANDING ruling -- made, registered, in force:     none
    held by a RELAYED ruling -- made, not yet in the register:
      OPERATOR-NAMES-THE-TARGET               17   W 12 by the R/W cell, 5 cited
        J 103, J 104, J 128, M C1, M C25, M C32, M M33, M M43, N 1, N 46,
        N 48, P A8, P A11, P A13, P A17, P A19, P A21
    waiting on a PENDING question to the operator -- NOT a ruling:
      NOTIFICATIONS-UNREAD-SPEND               2   N 20, N 45
    held by NO ruling                          2   J 121, J 122
    CHECK: 0 + 17 + 2 + 2 = 21, and COVERED-UNFIRED is 21

The pins read `b1_standing` 0, `b1_named_target` 17, `b1_pending` 2 and
`b1_no_ruling` 2, and `PINNED_B1_ROWS` holds the three groups row by row.
Everything below in this section is the state as first built and committed,
before the ruling reached the wave; the mechanism is unchanged, and only the
holds table and five cells moved.

**DONE.** `scripts/census_completion.py` no longer calls bucket 1 "blocked on a
live browser session". It prints what holds each COVERED-UNFIRED row, and every
number is computed:

    COVERED-UNFIRED                           21   DERIVED from the state
    held by a STANDING ruling -- made, and in force:
      NO-IRREVERSIBLE-WRITE-IS-FIRED          15   W 12 by the R/W cell, 3 cited
        J 103, J 104, J 128, M C1, M C25, M C32, N 1, N 46, N 48, P A8,
        P A11, P A13, P A17, P A19, P A21
      DO-NOT-OPEN-MESSAGING                    2   cited
        M M33, M M43
    waiting on a PENDING question to the operator -- NOT a ruling:
      NOTIFICATIONS-UNREAD-SPEND               2   cited
        N 20, N 45
    held by NO ruling -- the cell says what    2
      J 121, J 122
    CHECK: 15 + 2 + 2 + 2 = 21, and COVERED-UNFIRED is 21

**HOW EACH NUMBER IS DERIVED.** A W row is held by the write ruling because its
census R/W cell says W and the register's BINDS for that ruling is "every write
in the server". Every other row is held by what its OWN cell cites with the
marker ``**HELD BY `<ID>`**``, read by `ruling_holds.HELD_BY_MARKER`. A mention
of a ruling id without the marker is not a hold, because cells cite rulings as
arguments for many reasons. No citation and not a write is "held by NO ruling",
which is a finding about the rulings, and `J 121` and `J 122` carry it: both
were fired on 2026-09-20 and 2026-09-23 and neither banked, one needing a
press behind `Show Premium Insights`, the other a reader with a skills key.

**THE SEVEN CITATIONS ADDED TO THE CENSUS**, each at the end of the row's own
reason cell, dated:

    jobs.md                  J 103, J 104   the write ruling (the slice has no R/W column)
                             J 128          the write ruling AND the messaging ruling
                                            (the register lists `linkedin_send_message`
                                            among the messaging ruling's own names);
                                            the write ruling is the one counted
    messaging-and-content.md M33, M43       `DO-NOT-OPEN-MESSAGING`
    network.md               20, 45         `NOTIFICATIONS-UNREAD-SPEND`, marked in the
                                            cell as an OPEN QUESTION and not a ruling

No state and no direction moved: `scripts/count_census_states.py` reads the same
states and `reader_closable_blockers.direction_of` the same directions,
because both are value-based and bounded (a state is the first cell whose first
word is a state; a direction cell is at most four characters).

**WHERE THE HOLDS LIVE.** `scripts/ruling_holds.py` (new) holds three entries --
the write ruling (binds every write), `DO-NOT-OPEN-MESSAGING` (binds
`/messaging/`), and the pending notifications question (binds
`/notifications/`). Its `register_problems` re-reads every STANDING entry out
of `build_rulings_index.REGISTER` and fails when the id is gone, no longer
STANDING, or its BINDS no longer names the surface; a PENDING entry is
re-resolved against the document that put the question (the words required
exactly once in `_audit/2026-09-23-bucket1-fires.md`) and fails the moment a
registered ruling binds `/notifications/`, because the question has then been
answered. `census_completion.py` imports the module and never the register:
`build_audit_index` imports a module under `tests/` at import time, and
`scripts/_check_census_completion_can_fail.py` runs the completion figure inside
a copy of the tree holding only `scripts/`, `_audit/_census/` and the row pin.

**WHY THE PENDING ID IS NAMED LIKE A RULING AND IS NOT ONE.** The question had no
handle anywhere in the corpus (searched: no id, no D-number). A cell needs a
symbol to cite, so it got one, `NOTIFICATIONS-UNREAD-SPEND`, and every place it
is printed says PENDING or OPEN QUESTION beside it. It stops being cited the day
he answers, either way.

**PINNED, AND BY ROW.** Four count pins (`b1_write_ruling` 15,
`b1_other_standing` 2, `b1_pending` 2, `b1_no_ruling` 2) and `PINNED_B1_ROWS`,
the membership of each. `bucket1_moves` compares every row's derived hold with
its pinned one and `--check` fails naming the row -- ENTERED, LEFT, or moved
from one hold to another. The row pin exists because a count cannot see two
rows swap; `tests/test_ruling_holds.py` plants exactly that swap and asserts both
rows named with every count unchanged.

**SHOWN FAILING ON THE REAL CENSUS FIRST.** Before any citation was written, the
new derivation ran against HEAD's cells: 12 held by the write ruling, 9 by no
ruling, and `--check` exit 1 naming exactly the seven rows whose holds existed
only in prose -- `J 103`, `J 104`, `J 128`, `M M33`, `M M43`, `N 20`, `N 45`.
The citations then brought it to 15 / 2 / 2 / 2 with no row on a different hold
from the one the bucket-1 audit's section 3 typed by hand.

**THE PRESS LIST WAS REMOVED, AND WHY.** `PRESS_BLOCKED_NAMED` listed `N 134` and
`P O3` under bucket 1 with the comment "the remaining cost is a session and
nothing else". Both are GAP reads, so bucket 3 counts them already, off the
measured address table, which gates them PRESS-PERMITTED together with `M C72`
and names in each note what must be built before a session helps (a name-free
shaper, a caller wiring the counter). Listing two of the three again, as
session-only, double-counted them under a premise the table does not hold. The
"bucket 1, named" line that summed the two lists went with it.

**A FOURTH DEMONSTRATION** in `scripts/_check_census_completion_can_fail.py`:
D moves one COVERED-UNFIRED row W to R inside the scratch copy. Run:
the row chosen at runtime was `N 1`; `b1_write_ruling` 15 -> 14 and
`b1_no_ruling` 2 -> 3 moved, the row control printed *"N 1: pinned as held by
NO-IRREVERSIBLE-WRITE-IS-FIRED, now held by NO RULING"*, and no GAP figure
moved. All four demonstrations pass, the byte-restored copy green again.

---

## 2. ITEM 2 -- ROW `M C42`

**DONE, as a premise and not a state.** The cell now opens with what is true
today: for his OWN posts a tool in this server returns the identifier
(`linkedin_my_activity_items`, eight activity keys live on 2026-09-23, `C41`
COVERED-PROVEN), and `C25` / `C32` are aimable at them and stay unfired under
the write ruling. For anybody else's post the premise stands: no reader here
hands out a third party's item key (`linkedin_comment_on_item`'s own docstring)
and `/feed/` was measured drawing zero item permalinks
(`linkedin_my_activity_items`'s docstring). The 2026-08-31 quotation is kept
after it as the record. The slice's counts section carries the back-pointer
marker naming this document and a DELTA block: NO STATE MOVED, 142 rows and 77
GAP before and after.

**THE STATE IS LEFT, DELIBERATELY, AND IT IS THE THIRD TIME THE ROW HAS BEEN
REACHED.** Its only ground is the quotation, and the 2026-09-21 what-was-ruled
report (question Q5) already found that ground to be a statement about this
server's build state -- GAP's own definition -- and not one of the four grounds
`EXCLUDED-RULED-ADMISSION` admits. Today's fire removes the quotation's force for
his own posts. So the state word is not supportable on the register's own
terms, and I did not move it, for one reason: moving `C42` to GAP puts a new
read row into bucket 3 (achievable 389 -> 390, `gap` 274 -> 275, `gap_read`
67 -> 68, the address table +1 line, the messaging `--expect` 77 -> 78) on the
same day a sibling wave is moving bucket-3 rows on this slice, and the class
that row takes in bucket 3 is itself a judgement (its payload for other people's
posts has no known page). That is a decision for whoever merges both waves, and
section 10 puts it there with the cascade priced.

---

## 3. ITEM 3 -- `M C83` UNDER D3

**DONE.** `RULING_BLOCKED_NAMED` holds four rows. D3 asks whether a reasoned
refusal written into the allowlist counts as an EXCLUDED-RULED ground; for
`M C83` the refused spelling was never observed served -- the shipped boundary's
newsletters entry: *"`M C83` and `P L4` are not one allowlist line away from
anything: they are waiting on a LIVE READ that establishes which address
serves"*. So D3 answered yes cannot bank it and answered no leaves it where it
is. Its first need is that live read, which bucket 3 already counts (the
address table has it NEEDS-SESSION).

**WHAT DERIVED FROM THE LISTING, AND WHAT HAPPENED TO EACH:**

    the bucket-2 line "one undecided question, five rows"   now "(D3)", the count printed
                                                             from the list: 4
    bucket 3's "named elsewhere here as needing a ruling"   5 -> 4, computed
    the count itself                                        was pinned nowhere; now
                                                             `b2_d3_rows` 4
    the address table's `M C83` note                        its conflict note now
                                                             records the removal and why
    the bucket-3 audit, section 11 item 3                   a bracketed note: settled

Two dated documents quote the old five as of their own date
(`_audit/2026-09-21-what-100-percent-means.md` and the bucket-1 audit's figures
table) and are left as the readings of their day.

---

## 4. ITEM 4 -- `scripts/triage_read_gap_rows.py`

**DONE, by an implementer child, reviewed line by line before it entered.** Red at
HEAD on CONTROL 4 naming exactly `N 33`, `N 53`, `N 54`, `N 83`, `N 175`
(reproduced first). The five entries are removed and a comment block records
where each went, measured with `census_completion.walk()`:

    N 33   COVERED-CANNOT-DELIVER   (its 2026-09-21 verdict: BUILDABLE)
    N 53   COVERED-PROVEN           (SERVED)
    N 54   COVERED-CANNOT-DELIVER   (BUILDABLE)
    N 83   COVERED-PROVEN           (BUILDABLE)
    N 175  COVERED-CANNOT-DELIVER   (BUILDABLE)

The table holds 54 verdicts, equal to the 54 read-direction GAP rows of the two
slices, and the script exits 0.

**TWO FURTHER THINGS IN THE SAME FILE, BECAUSE THEY WERE UNTRUE STATEMENTS IN A
FILE THIS WAVE OWNED.** (a) Four of its verdicts (`P F1`, `P H11`, `P L4`,
`N 61`) are the 2026-09-21 reading that the bucket-3 table has measured past;
the triage alphabet has no class for MEASURE or NEEDS-SESSION, so the letters
are kept and a new dict, `MEASURED_PAST_BY_BUCKET3`, names the four with what
the table found, printed after the tally. CONTROL 7 refuses the moment one of
those keys stops carrying a verdict, so the annotation cannot outlive its row,
and a fourth plant, `--plant stale-annotation`, shows it refusing. (b) The
docstring said CONTROL 5 proves the corpus exclusion "by equality" and that the
script reads FOUR slices; the exclusion is CONTROL 6, it refuses on an index
file rather than comparing sets, and the script reads TWO slices.

---

## 5. ITEM 5 -- A TEST THAT RUNS IT, SHOWN FAILING

**DONE.** `tests/test_triage_read_gap_rows.py`, ten tests: green on the real
tree; a verdict planted into `TRIAGE` for a row that has left GAP (found at runtime off
`census_completion.walk()`, the first read-direction P/N row outside GAP) named
by CONTROL 4; a MISSING verdict named; all four built-in plants refused, EACH BY
ITS OWN CONTROL'S SENTENCE (review tightened this: the first draft accepted any
refusal, which would have stayed green with CONTROL 7 dead); CONTROL 7's dict
checked against the real table; and the population CONTROL 4 compares asserted
non-empty and equal to the key set.

**SHOWN FAILING ON THE REAL FILE, by the child, verified from its report:**

    sha256[:16] before plant   cba598f18ad3d209
    planted                    N 53 back into TRIAGE, verdict SERVED (it is COVERED-PROVEN)
    pytest                     2 failed, 7 passed -- test_green_on_the_real_tree and
                               the population test, both naming N 53
    restored                   sha256 identical, all 64 characters compared
    pytest                     9 passed

(Nine at that point; review then split one test into four parametrized cases.)

---

## 6. ITEM 6 -- THE 33 ADMITTED ROWS AGAINST EVERY STANDING RULING

**AFTER 18:15 (section 7): BLOCKED ON NOTHING IS 5 OF 67 AGAIN.** `M M49` is
READER once more, and its note opens *"Was held by DO-NOT-OPEN-MESSAGING; lifted
by the operator 2026-09-23 18:15"*. `b3_blocked_on_nothing` is back at 5 and no
row carries STANDING-RULING. The edge is unchanged and green, because it reads
the holds as they now are. No admitted row sits on a held page today -- the one
surface hold left is the notifications question, and no admitted row is on
`/notifications/` -- so its tests install their own holds on pages they choose.
Everything below in this section is the re-check as first done. It stays the
record of why the edge exists: run on the table as it stood, it named `M M49`
and nothing else.

    BLOCKED ON NOTHING, after 18:15    5   M M49, M C85 (READER);
                                           P O3, N 134, M C72 (PRESS-PERMITTED)

### 6.1 The rulings consulted

All 37 entries of `_audit/RULINGS.md`, by what they bind, plus the four rulings in
`_audit/2026-09-05-lead-rulings-round-two.md` the register does not carry
(`INVITE-NOTE-PARAM`, `RECOMMENDATIONS-SURFACE`, `SERVICES-PAGE-SURFACE`,
`PROFILE-PDF-DOWNLOAD`), plus the pending notifications question.

**Mechanical half** (a disposable join of each ADMITTED row's page against every
register entry whose BINDS is an address family): four entries name a path.

    DO-NOT-OPEN-MESSAGING                       /messaging/        FORBIDS   touches M M49
    SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS   /search/results/   permits reading; bars firing
                                                                             touches 18 rows, none
                                                                             blocked on nothing
    PERMALINK-READ-IS-ALLOWED                   /feed/update/<urn>/  permits  touches M C29, M C85
    ONE-NAMED-SETTINGS-PAGE-AT-A-TIME           /mypreferences/d/  touches no admitted row

**Judged half**, the rulings that bind an act or a content class:

    NO-IRREVERSIBLE-WRITE-IS-FIRED   binds writes. Holds a READ only if the read needs a
                                     write first: N 174 (a pending join request; already
                                     RULING under GROUPS-ADDRESS-BUYS-NO-WRITE) and,
                                     CONDITIONALLY, M C85 (see 6.4)
    FEED-CONTENT-READ-RULING         counts and relations only: permits M C72's counter
                                     and M C85's poll counts; forbids neither page
    DISCLOSING-PRESS-PERMITTED       permits the presses P O3, N 134, M C72 rest on; its
                                     outright refusals (navigate, submit, compose, type, a
                                     third party's surface) touch none of the three
    SCROLL-NOT-SANCTIONED            already named in P F1's note (MEASURE)
    RECOMMENDATIONS-SURFACE,
    SERVICES-PAGE-SURFACE            READS YES: P F1, P H11 (MEASURE)
    PROFILE-PDF-DOWNLOAD             YES IN PRINCIPLE: P C8 (RULING, D4)
    the pending notifications        binds /notifications/: no admitted row is there
      question
    the other 25 register entries    bind census conventions, output shapes or write
                                     admission; none binds a page any of the 33 is on

### 6.2 The split, re-derived -- as it stood before 18:15

    ADMITTED 33 -- unchanged; the class is the boundary's, and the boundary admits M M49's page
      READER             1   M C85
      PRESS-PERMITTED    3   P O3, N 134, M C72
      MEASURE            3   P F1, P H11, P K8
      BUILT-UNFIRED      4   N 80, N 81, N 88, N 89
      PRESS             12
      RULING             9   (a decision nobody has made)
      STANDING-RULING    1   M M49 -- HELD BY `DO-NOT-OPEN-MESSAGING`
    BLOCKED ON NOTHING   4   of 67 (was 5): M C85, P O3, N 134, M C72

**Before 18:15 the derived number was 4, as the orchestrator then expected, and
it rested on one unverified render (6.4).** It was re-pinned 5 -> 4 in this
wave's second commit, and back to 5 in its third, after the ruling. No other
`b3_` pin moved either time, because the row stays ADMITTED.

**A NEW GATE, NOT THE OLD `RULING`.** `RULING` is a decision nobody has made and
belongs in the operator's open queue; `DO-NOT-OPEN-MESSAGING` was made on
2026-08-31. Filing `M M49` under `RULING` would have put a decided question back
into that queue. `STANDING-RULING` says a ruling in force holds the page, and
the row's note cites it with the same `HELD BY` marker the census cells use.

### 6.3 The checker edge, shown failing on the real defect

`check_read_addresses.ruling_problems` (pure, reads `ruling_holds`) refuses the
table when a row gated READER or PRESS-PERMITTED sits on a page a hold binds;
when a STANDING hold's page carries any gate but STANDING-RULING, or a PENDING
one's any gate but RULING; when a held page's note does not cite its hold; and,
conversely, when a STANDING-RULING row cites no standing hold or sits off the
page the cited hold binds. `census_completion.bucket3_split` runs it too, so a
blocked-on-nothing figure over a table the rulings contradict is WITHHELD.
`main` also runs `ruling_holds.register_problems`.

**RUN FIRST AGAINST THE TABLE AS HEAD HAD IT**, before `M M49`'s line was
touched: exit 1, exactly two problems, both `M M49` --

    M M49: classed blocked on nothing (gate READER), but its page
           /messaging/thread/2-ABCdef123/ sits on /messaging/, which
           DO-NOT-OPEN-MESSAGING holds (STANDING)
    M M49: its page sits on /messaging/, so its note must cite
           HELD BY `DO-NOT-OPEN-MESSAGING`

Then green, 67 of 67, blocked on nothing 4. Eight plants in
`tests/test_read_addresses.py`, each into a copy of the real table and each
required to name its row: the row planted back to READER; a held page under a
PRESS gate; a held page whose note cites nothing; STANDING-RULING off its
ruling's page; STANDING-RULING citing nothing; a PENDING question planted onto a
page, convicting a row the test itself makes blocked on nothing (so it does not
depend on which rows are blocked on nothing today); `census_completion`
withholding the split; and the edge asserted to have a real row to check.

**WHAT THE EDGE CANNOT SEE.** A hold that binds an ACT is not readable off an
address. A row held by the write ruling -- which `M C85` would be if its poll
results render only after a vote -- has to say so in its note, and nothing
checks that it does.

### 6.4 The sibling wave's four rows -- recorded, NOT edited

`P O3`, `N 134`, `M C72` and `M C85` belong to the live wave firing them today.
None of their census cells or address-table lines was touched. The re-check
changes the class of none of them:

    P O3, N 134   /analytics/profile-views/, PRESS-PERMITTED. His own analytics page;
                  no ruling binds it; the disclosing press is permitted and none of its
                  outright refusals applies. Stays blocked on nothing.
    M C72         /feed/, PRESS-PERMITTED. The feed-content ruling permits a count; the
                  press is a disclosure. Stays blocked on nothing.
    M C85         /feed/update/<urn>/, READER. The permalink ruling permits the read and
                  the feed-content ruling permits counts. BUT its own line already marks
                  it UNVERIFIED whether poll results render before a vote, and a vote is
                  an irreversible write: if they render only after one, the read waits on
                  a write -- since 18:15 a write he must name the target of -- and the
                  row leaves blocked on nothing (4 of 67 after the ruling). The live fire
                  settles it. Separately, a permalink needs a post key, and the only tool
                  here that returns one returns his own posts' keys (item 2).

**AT MERGE:** if the sibling banks any of the four, `read-addresses.tsv` loses
that row's line, `b3_admitted` and `b3_blocked_on_nothing` move, and
`scripts/triage_read_gap_rows.py` needs the matching `TRIAGE` key removed (it
holds `P O3` and `N 134`); `tests/test_triage_read_gap_rows.py` goes red naming
the key until it is, which is the point of item 5.

---

## 7. THE 18:15 RULING, RELAYED MID-WAVE, AND WHAT THIS WAVE DID WITH IT

**WHAT ARRIVED.** A note from the orchestrator at the worktree root, file time
18:17:21 IST, read at about 18:25 by the box clock, after this wave's second
commit. It relays that at 18:15 the operator ruled "(b)", in its words:

> the linkedin MCP may connect, message, apply, post AND OPEN MESSAGING on his account

-- lifting `DO-NOT-OPEN-MESSAGING`, the read-only rule and the apply, connect
and InMail cut. It asked for three things inside this wave's six items and
nothing outside them: class no row as held by the messaging ruling, and record
`M M49` as "was held by DO-NOT-OPEN-MESSAGING; lifted by the operator
2026-09-23 18:15"; make the edge read the rulings as they now are; and have
bucket 1 say that the writes and the two messaging reads are held only by the
need for a live proof against a target he names. The note was deleted after
acting, as it asked, and never committed.

**VERIFIED BEFORE OBEYED.** Disk disagrees with the note in one place: the rulings
register still carries `DO-NOT-OPEN-MESSAGING` and
`NO-IRREVERSIBLE-WRITE-IS-FIRED` as STANDING. The note names that lag itself --
the orchestrator records the ruling in the register at merge -- so it is not
the kind of disagreement that should stop the order, and it is stated here as
the note asked. Everything else the note assumed matched disk: the edge
existed, `M M49` was the only admitted row on a messaging page, and the 15
writes and `M M33` / `M M43` were the rows it named.

**HOW IT WAS APPLIED -- one table, and the cells that cite it:**

    scripts/ruling_holds.py   the two rulings leave ROW_HOLDS for
                              LIFTED_ROW_HOLDS, so a cell or note still citing
                              either as a hold goes red instead of counting.
                              OPERATOR-NAMES-THE-TARGET enters, status RELAYED
                              (made, not yet in the register), binding every
                              write. Its record is the quotation above, required
                              exactly once in this document, and it fails the
                              moment the register carries its id, so that it
                              becomes STANDING with its BINDS checked
    census cells              J 103, J 104, J 128, M M33, M M43 now cite
                              OPERATOR-NAMES-THE-TARGET; the ruling that held
                              each until 18:15 is kept as history in lowercase
                              prose, which the marker does not read. C42's cell
                              says C25 and C32 wait on a named target. N 20 and
                              N 45 keep the open question
    read-addresses.tsv        M M49 back to READER, its note opening with the
                              record line the note asked for
    census_completion.py      bucket 1 grouped STANDING / RELAYED / PENDING /
                              none, the lifted two printed as lifted; bucket 2's
                              write sentence names what governs a write now;
                              b3_blocked_on_nothing back to 5 with its history

**WHAT THE NOTE DID NOT COVER, LEFT AS IT WAS.** The notifications question.
Ruling (b), as relayed, names connect, message, apply, post and opening
messaging, not the notifications page, whose cost falls on HIS unread badge.
`N 20` and `N 45` therefore stay on the open question. And for the two
messaging reads the "target he names" is his own inbox: what he accepts, per
fire, is that opening it lands in a conversation LinkedIn chooses and can mark
that person's message read.

---

## 8. INSTRUMENTS

Registered in `_audit/INSTRUMENTS.md` section 60 (numbered past the next free
integer so siblings forked from the same master do not collide):
`scripts/ruling_holds.py` with `tests/test_ruling_holds.py`; the bucket-1
derivation and its row pin in `scripts/census_completion.py`, with demonstration
D; the ruling edge in `scripts/check_read_addresses.py`; and
`tests/test_triage_read_gap_rows.py` over the repaired triage.

**DECLARED DISPOSABLE:** the scratch join of the 33 admitted rows against the
register (6.1), and the two scratch scripts that rewrote `M M49`'s cells --
first to STANDING-RULING, then back to READER after the ruling. What each
measured is recorded above, and the edge re-derives the part that matters on
every run.

---

## 9. GATES

(Filled in after the commits: what ran, what it said, and what did not run.)

---

## 10. FOR THE ORCHESTRATOR AND THE OPERATOR

(Filled in at the end.)
