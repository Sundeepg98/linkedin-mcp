claude-opus-5-5[1m]

# Census cleanup: six statements the census makes about itself, measured against today

**CORRECTS:** `_audit/_census/messaging-and-content.md` -- row `C42` read *"no tool in this server returns one"* (a post identifier); since `C41` was proven today, `linkedin_my_activity_items` returns one for every post of his own. The premise still holds for other people's posts, and the state is not re-decided.

**CORRECTS:** `_audit/2026-09-23-bucket3-addresses.md` -- it sized "blocked on nothing" at 5 of 67 without asking the rulings, counting `M M49` on a messaging thread while `DO-NOT-OPEN-MESSAGING` stood, which made the size 4. The operator lifted that ruling at 18:15 the same day (5 again), and the calls registered later that evening decided what eight RULING rows waited on, seven of which now need only a reader, so the size is 12 under the rulings as they now are (section 12). The checker asks the holds on every run; the gates are re-judged by hand when a ruling lands.

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

**AND THE REGISTER CAUGHT UP THE SAME EVENING (section 11).** Master 53ba1b6
registered ruling (b) and the orchestrator's delegated calls; this branch
merged it and finished the holds. The state after that merge:

    item 1   bucket 1 is 15 held by a standing ruling (every write, at a
             target he names) / 0 relayed / 0 pending / 6 held by no ruling
    item 6   unchanged: blocked on nothing is 5 of 67, and no hold binds a
             page any more

**AND TWO MORE CALLS WERE REGISTERED LATER THAT EVENING (section 12).** Master
4a57b75 registered `SELF-PROFILE-EDITS-NOT-OUTWARD` and
`OTHER-MEMBER-IDS-AS-READS`; this branch fast-forwarded to it, released six
writes and re-gated thirteen bucket-3 rows. The state NOW:

    item 1   bucket 1 is 9 held by a standing ruling / 0 relayed / 0 pending
             / 12 held by no ruling, 6 of them writes RELEASED by
             SELF-PROFILE-EDITS-NOT-OUTWARD
    item 6   blocked on nothing is 12 of 67; the gate column reads READER 9,
             PRESS-PERMITTED 3, MEASURE 8, BUILT-UNFIRED 4, PRESS 5, RULING 4

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
`b1_no_ruling` 2 (renamed from the first build's `b1_write_ruling` and
`b1_other_standing`), and `PINNED_B1_ROWS` holds the three groups row by row.
Demonstration D, re-run after the ruling, passes the same way: `N 1` is named
moving from `OPERATOR-NAMES-THE-TARGET` to NO RULING, and no GAP figure moves.
Everything below in this section is the state as first built and committed,
before the ruling reached the wave. The mechanism is unchanged; what moved is
the holds table, five cells, and the pins' names and values.

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
COVERED-PROVEN), and `C25` / `C32` are aimable at them. Both are unfired; the
write ruling held them until 18:15, and since then they wait on a target the
operator names (section 7). For anybody else's post the premise stands: no reader here
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

**DONE.** `tests/test_triage_read_gap_rows.py`, nine tests (collected: 9):
green on the real tree; a verdict planted into `TRIAGE` for a row that has left
GAP (found at runtime off `census_completion.walk()`, the first read-direction
P/N row outside GAP) named by CONTROL 4; a MISSING verdict named; all four
built-in plants refused, EACH BY ITS OWN CONTROL'S SENTENCE (review tightened
this: the child's draft accepted any refusal, which would have stayed green with
CONTROL 7 dead); CONTROL 7's dict checked against the real table; and the
population CONTROL 4 compares asserted non-empty and equal to the key set.

**SHOWN FAILING ON THE REAL FILE, by the child, verified from its report:**

    sha256[:16] before plant   cba598f18ad3d209
    planted                    N 53 back into TRIAGE, verdict SERVED (it is COVERED-PROVEN)
    pytest                     2 failed, 7 passed -- test_green_on_the_real_tree and
                               the population test, both naming N 53
    restored                   sha256 identical, all 64 characters compared
    pytest                     9 passed

(The count is nine before and after review. Review changed what the four plant
cases assert, not how many there are. An earlier version of this sentence said
review split one test into four; that was untrue, and the collected count
settled it.)

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
                                                                             touches 17 rows, none
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

Then green, 67 of 67, blocked on nothing 4. Seven plants in
`tests/test_read_addresses.py`, each into a copy of the real table and each
required to name its row: the row planted back to READER; a held page under a
PRESS gate; a held page whose note cites nothing; STANDING-RULING off its
ruling's page; STANDING-RULING citing nothing; a PENDING question planted onto a
page, convicting a row the test itself makes blocked on nothing (so it does not
depend on which rows are blocked on nothing today); and `census_completion`
withholding the split. Plus one check that the edge had a real row to check.

**After 18:15 the tests were reworked, because no admitted row sits on a held
page any more and a plant needs one.** Each now installs its OWN hold on a page
it chooses, into the holds table the edge reads, and requires the row named.
Nine tests in all (37 in the file): the real table passes the edge and at
least one surface hold exists; a row made blocked on nothing on a held page; a
held page under a PRESS gate; a held page whose note cites nothing;
STANDING-RULING off its ruling's page; STANDING-RULING citing nothing; a
PENDING question convicting a row the test makes blocked on nothing; a note
still citing a LIFTED ruling; and `census_completion` withholding the split.

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

**RUN, all on this worktree, all offline:**

    scripts/impact_gate.py --against b0d3ab8   PASS over 46 test files (2184 tests),
      at the wave's third commit               479.5 s wall. 18 changed paths; the 17
                                               corpus-wide guards ran unconditionally,
                                               4 sweeps inside them answering on the
                                               CHANGE rather than the tree (the gate's
                                               own induction step). NOT CHECKED, said
                                               by the gate: 171 of 217 test files,
                                               roughly 3910 of 6094 tests. Local and
                                               Windows-only
    the new and changed test files             81 passed: test_ruling_holds 35,
                                               test_read_addresses 37,
                                               test_triage_read_gap_rows 9
    the correction and cited-SHA guards        41 passed before the second commit;
                                               both again inside the gate's 46
    scripts/census_completion.py --check       exit 0
    scripts/_check_census_completion_can_fail.py
                                               ALL FOUR DEMONSTRATIONS PASS, before
                                               and after the ruling
    scripts/check_read_addresses.py            GREEN, 67 of 67; blocked on nothing 5
    scripts/ruling_holds.py                    GREEN
    scripts/triage_read_gap_rows.py            exit 0, 54 of 54; each --plant exits 1
    scripts/count_census_states.py --expect J=56,P=55,M=77,N=86
                                               all four MATCH, GAP 274
    scripts/pin_census_rows.py                 no drift
    scripts/reader_closable_blockers.py        controls 1-4 OK; its one unjoined GAP
                                               row predates this wave (the map's 409
                                               row ids are identical to b0d3ab8's)
    the three generators, per commit           --check green, and a second --write
                                               sweep changed nothing
    the pre-commit identity gate               0 hits, every commit
    the commit messages                        no attribution line, checked
    a cold verifier                            9.1

**THE GATE'S PRINTED PLAN IS ABRIDGED, AND I MISREAD IT ONCE.** It lists 40 of
the 46 files and ends "... and 6 more selected"; `tests/test_triage_read_gap_rows.py`
is one of the six not printed, so a filter over the printed list made it look
unselected. Calling `impact_set` directly shows it in the plan, reached through
`census_completion.py` and as a changed test file. The selection is sound; the
listing is short.

**THE REGENERATED BLOCKER MAP, WHICH NO OTHER SECTION NAMES.** Every change is in
its `reason_doc` column and nothing else. The candidate count grew because new
documents joined the corpus the locator ranks, and for twelve rows the rank-1
candidate is now this audit, where it was the bucket-3 audit: the ten
CONVERSATION-OVERFLOW-MENU rows, whose blocker includes `M M49`, and the two
POLL-SURFACE rows, whose blocker includes `M C85`. The locator scores
paragraphs that argue a blocker's ROWS, and this audit argues about those two
rows more often than any other document. It ranks what argues a row, not where
a blocker's reason is written, and its own docstring puts its rank-1 recall at
4 of 8. No row id, blocker, state or other column moved.

**NOT RUN, and why:**

* **The full suite.** 171 of 217 files, by the gate's own count. CI runs the
  whole suite on three platforms on push, and this wave does not push.
* **Anything live.** Every reading here is the census, the boundary called
  in-process, the register, or a script over them.
* **The gate over this section's own edit.** A document cannot quote the gate
  that checks its last edit, so the re-run over the final commit is in the
  wave's final message.

### 9.1 A cold verifier, and what it found

An implementer child with no part in the work, briefed with an eight-item
checklist and read-only on the worktree, re-derived each claim from the tree:
bucket 1 row by row from the census cells by hand; bucket 3 from the checker;
the 33 admitted rows against the register and the round-two rulings by its own
judgement; the sibling wave's four rows untouched (`git diff` against b0d3ab8);
no census state or direction moved across all 704 rows (both versions parsed
with the shipped functions); hygiene over every added line (ASCII, no absolute
path, no six-digit urn, no name, no attribution line); the two marker pairs;
and four spot checks. **Seven of eight matched. The one mismatch was mine:**
section 6.1 said the search-admission ruling touches 18 admitted rows, and it
touches 17 (`N 79` to `N 94` without `N 83`, plus `N 172` and `N 194`). Fixed
in place. It also noted that the blocker map's diff was named nowhere in this
document, now named above, and that section 2 still said the write ruling held
`C25` / `C32` after the ruling, now brought to the cell's wording.

### 9.2 The forced predictions, scored

    item 6, one row on a forbidden page, 5 -> 4     MET before 18:15: the edge named
                                                    M M49 and nothing else. The ruling
                                                    then moved the answer back to 5
    item 1, 15 / 2 / 2 / 2, no row moved            MET, row for row
    item 4, green on the removal alone, 54 left     MET; the other edits to that
                                                    file were additions

**AND TWO STATEMENTS OF MINE THE MEASUREMENTS DID NOT BEAR OUT:** "touches 18 rows"
(it is 17, found by the cold verifier) and "ten tests" with a review "split into
four" (it is nine before and after review, found by counting the collection).
Both are fixed in this document.

---

## 10. FOR THE ORCHESTRATOR AND THE OPERATOR

### 10.1 At merge

**[Settled the same evening, section 11: ruling (b) and the target condition
are registered, both notes below about the register are acted on, and the
lifted list is now read against the register.]**

* **Registering ruling (b).** `scripts/ruling_holds.py` carries it as
  `OPERATOR-NAMES-THE-TARGET`, status RELAYED, binding every write. The day the
  register carries that id, `register_problems` goes RED on purpose ("mark it
  STANDING"): flip the status there, and its BINDS must then read "every
  write...". If the register entry takes a DIFFERENT id, rename the hold and
  the five census cells that cite it (`J 103`, `J 104`, `J 128`, `M M33`,
  `M M43`) in the same commit, or the RELAYED entry never sees that it was
  registered. And nothing here reads the lifted list against the register:
  it is the register entry that makes `DO-NOT-OPEN-MESSAGING` and
  `NO-IRREVERSIBLE-WRITE-IS-FIRED` stop reading STANDING.
* **The sibling wave's four rows.** If it banks any of `P O3`, `N 134`, `M C72`,
  `M C85`: its line leaves `read-addresses.tsv`, the `b3_` pins move, and
  `scripts/triage_read_gap_rows.py` loses the matching `TRIAGE` key (it holds
  `P O3` and `N 134`). `tests/test_triage_read_gap_rows.py` goes red naming the
  key until that is done, which is what item 5 is for.
* **Generated files.** `_audit/INDEX.md`, `_audit/RULINGS.md` and the blocker
  map are regenerated here and will conflict with any sibling that regenerated
  them. Regenerate at the merge head; do not hand-merge either side.
* **Pins this wave owns in `scripts/census_completion.py`:** the four `b1_`
  counts and `PINNED_B1_ROWS`, `b2_d3_rows` 4, and `b3_blocked_on_nothing` 5
  (the same value HEAD had, with its history now in the comment).

### 10.2 What needs the operator

**[Both answered the same evening, as the orchestrator's calls under the
operator's delegation and overridable by him -- section 11. Neither needs him
now unless he overrides.]**

1. **`N 20` and `N 45`: may one `linkedin_notifications` call spend his unread
   notification state?** Ruling (b), as relayed, names connecting, messaging,
   applying, posting and opening messaging; it does not name the notifications
   page, whose cost falls on his own badge and does not come back. Both rows
   cite the question and stay held by it until he answers. This is the third
   wave to reach them.
2. **The two messaging reads under ruling (b).** For `M M33` and `M M43` the
   "target he names" is his own inbox, and what he accepts per fire is that
   opening it lands in a conversation LinkedIn chooses and can mark that
   person's message read. If he meant a standing permission for inbox reads
   rather than a per-fire one, these two rows move from "waits on a named
   target" to a session. (`M M49` is not in that position: it is a bucket-3
   row with no reader yet, blocked on nothing for BUILDING one; only its first
   fire would meet the same question.)

### 10.3 A decision that is the orchestrator's, priced

**`M C42`'s state.** The registered `EXCLUDED-RULED-ADMISSION` admits four
grounds; the 2026-09-21 what-was-ruled report (question Q5) found the row's
only ground is none of them, and today's fire removed that ground's force for
his own posts. Moving it to GAP is what the register already implies. Priced:
`out_of_scope` 315 -> 314, `achievable` and `capabilities_achievable`
389 -> 390, `adjudicated` 430 -> 429, `gap` 274 -> 275, `gap_read` 67 -> 68,
one new line in `read-addresses.tsv` (its class is a judgement: no known page
draws another member's post key, which reads UNDETERMINED), and the messaging
`--expect` 77 -> 78. It was left because it is a state move the brief did not
ask for, made on the same day a sibling is moving rows on the same slice.
**Recommendation: move it at merge, after the sibling's rows land.**

### 10.4 Found and not fixed, outside the six items

* `scripts/triage_read_gap_rows.py`'s CONTROL 6 cannot fail as written: the
  set it inspects is computed from `SCOPE`, which can never name an index
  file. The docstring now says what it does; making it able to fail is not
  one of the six items.
* The gate's abridged listing (9, above) hid a selected file from a reader.
  Not a selection defect; a listing that could say which six it omitted.

---

## 11. THE REGISTER CATCHES UP: THE MERGE WITH MASTER 53ba1b6, AND THE HOLDS FINISHED

**THE ORDER, CHECKED AGAINST DISK FIRST.** At 20:05 the orchestrator ordered
this branch to merge master and finish the holds, IF this branch stood at its
fourth commit and master at 53ba1b6. Both held when measured at 20:08 by the
box clock, with b0d3ab8 as the common base. Master had added lane L2's merge
and the register entries for the rulings of 2026-09-23, recorded in
`_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`, and each entry
this wave depends on was read before anything was changed. The document names
who decided each one: the operator ruled the write class (b), that he names
every live target, and that his own notification state and his own view are
the orchestrator's to decide. The orchestrator's calls under that delegation,
each overridable by him, include the two that move rows here: loading
`/notifications/` is permitted, and reading his own inbox needs no per-fire
go-ahead. **One precision against the order's wording:** the notifications
entry is registered with status STANDING, as a permission that answers the
question, not with a status reading ANSWERED. The substance is the order's.

**THE MERGE, IN ITS OWN COMMIT.** Two conflicts were real, and each was taken
from the two commits' own lines rather than retyped: in the address table,
`M M49` from this branch and `M C29` from lane L2 (adjacent lines, one change
each); in the instrument register, both sides had appended a section after 57,
and lane L2's 59 is kept ahead of this wave's 60. The three generated files
were regenerated twice, to a fixpoint, and never hand-merged.

**AND AT THE MERGE THE HOLDS TABLE SAID SO ON ITS OWN.** Before anything was
flipped, `scripts/ruling_holds.py` exited 1 with exactly these two problems,
on real data with nothing planted:

    OPERATOR-NAMES-THE-TARGET: RELAYED here, and the register now carries it
      -- mark it STANDING, so its BINDS is checked from now on
    NOTIFICATIONS-UNREAD-SPEND: PENDING here, and the register now holds
      ['NOTIFICATIONS-UNREAD-SPEND'] binding /notifications/ -- the question
      looks answered; re-read every row that cites it

They are the two tripwires section 1 built into the table, firing on the
event they were built for. The merge commit keeps that red, and the next
commit clears it.

**THE FLIP:**

    holds table       OPERATOR-NAMES-THE-TARGET is STANDING, and the only hold.
                      The register's BINDS for it reads "every outward write";
                      the check on a write hold now accepts that spelling and
                      still refuses "one write only"
    lifted list       DO-NOT-OPEN-MESSAGING (the register says SUPERSEDED),
                      NO-IRREVERSIBLE-WRITE-IS-FIRED (AMENDED), and the
                      notifications question (STANDING, as a permission).
                      NEW: each entry names the status the register gives it
                      and the checker compares, which closes the gap 10.1
                      named -- nothing had read this list against the register
    census cells      M M33, M M43, N 20, N 45 lose their HELD BY markers and
                      say in prose why no ruling holds them; J 103, J 104,
                      J 128 keep theirs and name the registered ids; C42's
                      cell and the messaging DELTA note name them too
    address table     M M49's note names both registered rulings; its gate
                      stays READER

**THE NEW BUCKET-1 SPLIT, AND THE PINS THAT MOVED:**

    held by a STANDING ruling
      OPERATOR-NAMES-THE-TARGET          15   W 12 by the R/W cell, 3 cited
    held by a RELAYED ruling              0
    waiting on a PENDING question         0
    held by NO ruling                     6   J 121, J 122, M M33, M M43,
                                              N 20, N 45
    CHECK: 15 + 0 + 0 + 6 = 21

    b1_standing       0 -> 15
    b1_named_target  17 -> renamed b1_relayed, now 0: the pin names what a
                          status COUNTS, not which ruling holds it today
    b1_pending        2 -> 0
    b1_no_ruling      2 -> 6
    PINNED_B1_ROWS    re-pinned to the two groups above

No other pin moved: `unfired` 21, `b2_d3_rows` 4, `b3_blocked_on_nothing` 5.
What remains for the six held by no ruling is not a ruling: a session for
M M33, M M43, N 20 and N 45, and a press and a reader change for J 121 and
J 122.

**THE PAGE EDGE HAS NOTHING TO FIRE ON TODAY, SAID RATHER THAN HIDDEN.** With
the question answered, no hold binds a page. `ruling_problems` is green on the
real table because there is nothing for it to catch; each of its tests
installs a hold of its own, and one installs a hold on a real admitted row's
page to show the real table going red.

**ONE CLASSIFICATION IS STILL THIS TABLE'S, NOT THE REGISTER'S.** The register
binds the target condition to every OUTWARD write; this table holds all 15
census writes with it. Six of them -- `P A8`, `P A11`, `P A13`, `P A17`,
`P A19`, `P A21` -- are edits to his own profile fields: reversible, and
visible to anyone who opens his profile, while `OUTWARD-ACTS-NEED-THE-OPERATOR`
routes to him only acts toward other people or ones that cannot be undone.
Whether those six are outward is the orchestrator's call; until it is made
they stay held, the direction that cannot fire anything by mistake.
**[Made later the same evening and registered as
`SELF-PROFILE-EDITS-NOT-OUTWARD`; the six are released: section 12.]**

**WHAT THE NEW RULINGS BEAR ON, AND WHAT WAS NOT TOUCHED.** Three registered
rulings bear on bucket-3 gates, and re-gating those rows was not part of this
order:

    D1-SEARCH-AS-READS           N 79, N 93, N 94, N 194: gate RULING, first
                                 gate D1, which is now decided. (N 172 also
                                 needs another member's identifier, D3's
                                 other-people question, still open)
    IN-ME-NO-BLANKET-BAR         P D28, P J4, N 76: gate PRESS, first refusal
                                 the missing /in/me/ sensitivity basis
    VIEW-SWITCH-PRESS-RESTORED   M C29 (a sort is a selection) and N 133 (a
                                 filter): gate PRESS -- lane L2's rows

Their notes still describe those decisions as unmade. No class count and no
blocked-on-nothing figure moves until someone re-gates them, and what each
becomes -- READER, PRESS-PERMITTED or MEASURE -- is a judgement per row.
**[Re-gated later the same evening, with three more rows found on disk and
the other-people question answered by a registered call: section 12.]**

**GATES FOR THIS SECTION** are reported in the wave's final message: a
document cannot quote the gate that checks its own last edit.

---

## 12. THE SECOND FOLLOW-UP: SIX WRITES RELEASED, THIRTEEN ROWS RE-GATED

**THE ORDER, CHECKED AGAINST DISK FIRST.** The orchestrator's second order,
the evening of 2026-09-23: IF master is still 4a57b75 and this branch 6fae42c,
merge master; release the six self-profile-edit holds under
`SELF-PROFILE-EDITS-NOT-OUTWARD`; re-gate the bucket-3 rows whose notes still
describe decisions as unmade; re-derive and re-pin; regenerate; gate; commit;
do not push. Both SHAs held when measured, before any edit. `git merge master`
fast-forwarded to 4a57b75, which registers two more of the orchestrator's
delegated calls, each overridable by the operator and each recorded in
`_audit/2026-09-23-rulings-write-class-and-delegated-calls.md`:
`SELF-PROFILE-EDITS-NOT-OUTWARD` (edits to his own profile fields are not
outward acts: no other person is targeted and each edit reverses; a live proof
runs with notify-network off, restores the field in-session, proves it by a
before/after reading, and never touches a field that broadcasts by nature) and
`OTHER-MEMBER-IDS-AS-READS` (another member's id in a search facet is a
permitted read when it comes from the tool's arguments, never from page
content, and is never stored in a tracked file). Every instrument was green at
4a57b75 before the first edit.

**ONE PLACE WHERE DISK AND THE ORDER DIFFERED, AND DISK WAS FOLLOWED.** The
order named ten rows. The address table at 4a57b75 carried thirteen whose notes
describe a question as unmade that a registered call has since decided: the
ten, and `N 84`, `N 85` and `N 87`, which lane L2 had moved from PRESS to
RULING that afternoon on the words *"Composing one is D1"* (and, for `N 85`,
D3's other-people cause). The order's list matches the bucket-3
audit's nine RULING rows plus the press rows, which predate that move. Same
rulings, same evidence, so all thirteen were re-gated; each is one line of the
table and can be put back on its own.

### 12.1 THE RELEASE, AND WHY IT IS A MARKER

The write hold binds every OUTWARD write, and a W row is held by it through
its R/W cell with no marker (section 1). A class of writes the register calls
not outward can therefore leave the hold only by saying so IN ITS OWN CELL,
never by where it sits in the census: a row's section is its topic, not its
class. The marker is ``**RELEASED BY `<ID>`**``.

    scripts/ruling_holds.py   ROW_RELEASES, one entry today
                              (SELF-PROFILE-EDITS-NOT-OUTWARD), and
                              RELEASED_BY_MARKER. hold_of: a W row citing a
                              known release is held by no ruling. REPORTED,
                              never counted: a release this census does not
                              know, a release on a row that is not a write
                              (a jobs row included -- jobs.md has no R/W
                              column), and a release beside the write hold's
                              own HELD BY. register_problems: every release
                              must be registered, STANDING, and not also a
                              hold or a lifted hold
    profile.md                P A8, P A11, P A13, P A17, P A19, P A21 carry
                              the marker, and the ruling's proof conditions
                              in words
    census_completion.py      bucket 1 prints the released writes as a subset
                              of "held by NO ruling", with a new pin,
                              b1_released; bucket 2 no longer says the last
                              step of EVERY write is his, and counts the
                              still-GAP writes whose own cell cites a release
                              (0 today: the six are the bucket-1 rows)

**THE NEW BUCKET-1 SPLIT:**

    held by a STANDING ruling
      OPERATOR-NAMES-THE-TARGET           9   W 6 by the R/W cell, 3 cited
                                              J 103, J 104, J 128, M C1,
                                              M C25, M C32, N 1, N 46, N 48
    held by a RELAYED ruling              0
    waiting on a PENDING question         0
    held by NO ruling                    12   J 121, J 122, M M33, M M43,
                                              N 20, N 45, and the six below
      of which writes RELEASED            6   P A8, P A11, P A13, P A17,
                                              P A19, P A21
    CHECK: 9 + 0 + 0 + 12 = 21

**WHAT A RELEASE DOES NOT DO.** It takes the named-target condition off; it
fires nothing. The six still need a session, and each proof is bound by the
ruling's four conditions, which ride in the cell.

### 12.2 THE RE-GATE, ROW BY ROW

Each row's gate and note in `_audit/_census/read-addresses.tsv` now cite the
ruling by id; each census cell whose words the ruling changed carries a dated
RE-GATED note (network.md rows 76, 79, 84, 85, 87, 93, 94, 133 and 194;
messaging-and-content.md row C29). The one row without a note has an empty
cell, left so.

    row    ruling                            gate                what it needs now
    N 79   D1-SEARCH-AS-READS                RULING -> READER    a keyword-taking reader; a keyword
                                                                 that trips a forbidden substring
                                                                 gets the boundary's own refusal
    N 194  D1-SEARCH-AS-READS                RULING -> READER    the same reader: the hashtag is
                                                                 a keyword
    N 94   D1-SEARCH-AS-READS                RULING -> READER    a reader composing the location
                                                                 facet; the ruling bounds each
                                                                 search, not the number of values,
                                                                 so the cell's second question goes
                                                                 with the first
    N 84   D1-SEARCH-AS-READS (disk)         RULING -> READER    currentCompany: 16 LinkedIn-authored
                                                                 hrefs on record (lane L2)
    N 87   D1-SEARCH-AS-READS (disk)         RULING -> READER    pastCompany: a LinkedIn-authored
                                                                 canned search on record
    N 172  OTHER-MEMBER-IDS-AS-READS + D1    RULING -> READER    connectionOf, the id from tool
                                                                 arguments only, never stored
                                                                 (census cell empty; no note)
    N 85   OTHER-MEMBER-IDS-AS-READS + D1    RULING -> READER    the same spelling as N 172
           (disk)
    N 93   D1-SEARCH-AS-READS                RULING -> MEASURE   decided, but no spelling is on
                                                                 record for its five fielded
                                                                 keywords: lane L2's census of
                                                                 LinkedIn-authored people-search
                                                                 keys holds `keywords` only, and a
                                                                 repository search for four common
                                                                 fielded spellings found none
    P D28  IN-ME-NO-BLANKET-BAR              PRESS  -> MEASURE   no control to judge: distinct_langs
                                                                 1, and its measuring document says
                                                                 it does not prove one exists
    P J4   IN-ME-NO-BLANKET-BAR              PRESS  -> MEASURE   the one press on record opens three
                                                                 options and no state; where the
                                                                 state renders is unknown
    N 76   IN-ME-NO-BLANKET-BAR              PRESS  -> PRESS     judged on evidence the trigger is a
                                                                 disclosure shape, but the shipped
                                                                 gate still refuses /in/me/ (12.4):
                                                                 a build, then a session
    M C29  VIEW-SWITCH-PRESS-RESTORED        PRESS  -> MEASURE   permitted with the view restored;
                                                                 the control was never captured, and
                                                                 his own permalinks are addressable
                                                                 since C41 fired
    N 133  VIEW-SWITCH-PRESS-RESTORED        PRESS  -> MEASURE   applying a filter is permitted with
                                                                 the view restored; what a pill
                                                                 opens is in no capture

**EACH CONTROL WAS JUDGED ON ITS EVIDENCE, AS THE ORDER SAID -- NO BLANKET
MOVE.** Two of the thirteen did not become readers although their decision was
made: the fielded-keyword row, because a reader needs a spelling nobody has
seen, and the follow-link row, because the code has not taken the ruling. No
restore-and-prove press exists yet: `press.disclose` closes by Escape and
checks `aria-expanded`, which cannot put a selection back, so the two
view-switch rows also need that press built after their capture -- unless the
viewer-filter capture shows the opened pill carrying per-option counts, which
lane L2 named as the question and which an already-permitted disclosing press
would then deliver.

### 12.3 WHAT MOVED

    gate column (33 ADMITTED)   READER 2 -> 9, PRESS-PERMITTED 3 -> 3,
                                MEASURE 3 -> 8, BUILT-UNFIRED 4 -> 4,
                                PRESS 9 -> 5, RULING 12 -> 4,
                                STANDING-RULING 0 -> 0
    BLOCKED ON NOTHING          5 -> 12 of 67: M C72, M C85, M M49, N 79,
                                N 84, N 85, N 87, N 94, N 134, N 172,
                                N 194, P O3
    pins                        b3_blocked_on_nothing 5 -> 12,
                                b1_standing 15 -> 9, b1_no_ruling 6 -> 12,
                                b1_released NEW at 6, b2_d3_rows 4 -> 3
                                (N 172 left D3's list: the ruling answers the
                                cause it was filed for), PINNED_B1_ROWS
                                re-pinned (the six P A rows from
                                OPERATOR-NAMES-THE-TARGET to NO RULING)
    unmoved                     every other pin, the class split
                                (ADMITTED 33 / REFUSED 24 / NO-ADDRESS 2 /
                                NEEDS-SESSION 6 / UNDETERMINED 2), unfired 21

The seven new blocked-on-nothing rows are all people-search readers, so a live
proof of any of them spends the session budget D1 sets: at most 5 test
searches, and never a value that identifies the operator.

The census_completion report now LISTS the blocked-on-nothing rows off the
table instead of sending the reader to the bucket-3 audit, which names the
five of its own day and cannot say the table has moved.

### 12.4 FOR THE ORCHESTRATOR

**THE SHIPPED PRESS GATE HAS NOT TAKEN `IN-ME-NO-BLANKET-BAR`.** Measured
in-process on this branch, 2026-09-23 about 21:30 IST: `press.check_basis` for
`/in/me/` returns `no_sensitivity_basis` -- *"no basis is declared for this surface, so
condition 3 has no way to be satisfied here"* -- the blanket bar the ruling
removes. For every `/in/me/` press the code and the register now say different
things. `linkedin_server/press.py` is shipped code outside this order, so it
was not touched: a build item. The follow-link row still gated PRESS waits on
it, and the two `/in/me/` rows now gated MEASURE would meet it the moment a live
look found their control.

**`N 174` STILL READS RULING, AND IS NOT A DECISION NOBODY HAS MADE.** It is
observable only once a pending group-join request exists, and creating one is a
write at a real group. Ruling (b) lifted the read-only rule, and a join request
acts toward other people, so `OPERATOR-NAMES-THE-TARGET` makes the group his to
name: what it waits on is his naming one. Left as it was: the order did not name it, and the gate this
table has for a ruling made -- STANDING-RULING -- is for a page a hold binds,
which this is not. A read row waiting on a write's target is a shape the table
cannot yet say; a small design question for whoever owns the gate column. So
RULING now means four rows: this one, `P C8` (D4, the package's own browser
context), `N 82` (a label reading this surface forbids) and `N 132` (D6,
whether two addresses discharge a row named for a control). No registered call
reaches D4 or D6.

**THE READ TRIAGE IS KEPT AS ITS DAY'S READING, AND NOW SAYS SO FOR FOUR MORE
ROWS.** `scripts/triage_read_gap_rows.py` gains `DECIDED_SINCE_TRIAGE`
(`N 79`, `N 94`, `N 172`, `N 194`: RULING verdicts a registered call has since
decided) and a CONTROL 8 that refuses an entry whose row does not carry RULING,
shown refusing by a new plant. Its `P D28` line had the measuring document
saying it "proves no pressable control exists"; the document says it "does not
prove a pressable control exists", and the line now says that.

**MASTER MOVED TWICE WHILE THIS RAN.** First to 1cfb962 (lanes L1 and Y), then,
during the gates, to c8fa6ea (the live readers wave). This branch stays on
4a57b75, as the order set, and is gated against it. Their changes touch other
lines of the same files: L1 admitted seven reads, every one gated MEASURE, and
built one read into bucket 1; the readers wave re-gated its four rows and
re-pinned blocked on nothing to 1 (`M M49` alone). So the merge has to
re-derive the pins rather than take either side. By the arithmetic of the
diffs against c8fa6ea, to be measured at the merge: bucket 1 is 9 standing /
0 / 0 / 13 held by no ruling (6 of them released) of 22, and blocked on
nothing is 8 of 66 -- `M M49` and the seven people-search readers above.
Master's `press.py` changed too, and still declares no basis for `/in/me/`
(read from its source, not run).

### 12.5 THE BLOCKER MAP

**NO BLOCKER'S FIRST CANDIDATE MOVED.** The locator behind the map's
`reason_doc` column counts, per blocker, the paragraphs that mention one of its
rows. The first draft of this section repeated row ids across many
paragraphs, and on regeneration this document took first place for two
blockers it does not discuss: one holding 30 group rows, one holding three
off-platform rows. The ids were gathered into the tables above and the map
regenerated, and those two point where they pointed before. What remains in
the regenerated map is scores only: two blockers this document already led
gain one and two points, and one gains a candidate without changing its
first.

### 12.6 GATES

Reported in the wave's final message, for the reason section 11 gives.
