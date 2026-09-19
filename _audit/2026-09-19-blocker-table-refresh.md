# The blocker table, refreshed -- 14 blockers are already empty and 53 cannot be checked at all

> **QUOTE THESE NUMBERS, NOT SECTION 3's.** Every per-blocker row count in
> `_audit/2026-09-03-linkedin-gap-blockers.md` section 3 is dated 2026-09-03
> and rows have moved since. That document is the historical record and is
> **deliberately not edited** -- another wave is adjudicating conflicts inside
> it. This document supersedes its COUNTS and nothing else: its assignment
> rule, its cost model and its reasoning all still stand.
>
> **The figures to quote: 14 EMPTY-CERTAIN, 1 EMPTY-UNCERTIFIABLE, 53
> UNLOCATABLE, 29 LIVE, across 97 blockers and 409 published rows.**
>
> Derived 2026-09-19 09:43 by `scripts/blocker_table_refresh.py`, whose
> controls are reproduced in s1. **RE-DERIVE RATHER THAN RE-QUOTE, and this
> document proved its own point while being written: the first derivation at
> 09:36 read 13 EMPTY-CERTAIN over 28 rows; seven minutes later it read 14
> over 30**, because another wave retired `M C10` and `M C28` in between (s8).
> A published count is a reading with a timestamp, including this one.

## Why this exists, and the cost it is meant to stop

**A wave briefed off section 3 arrives at a closed door.** Measured 2026-09-19:
of seven blockers in one assignment, **two had left GAP entirely before the
wave began** -- `PANEL-NOT-OBSERVED` (retired 2026-09-05) and
`MESSAGE-ADDRESSING` (`M 1` moved to COVERED-CANNOT-DELIVER in `02e617d`,
2026-09-05). Section 3 still lists both as live MEASURE work. Nothing in the
table said otherwise, and nothing could: **a published count is a reading with
a timestamp.**

## 1. THE INSTRUMENT, AND WHAT GATES IT

`scripts/blocker_table_refresh.py`. **It reparses nothing.** It imports
`build_blocker_map`, which imports `enumerate_gap_rows`, which imports
`count_census_states` -- the shipped counter. Four waves reimplemented a
shipped instrument on 2026-09-05 and three got a broken one.

**THE CONSEQUENCE IS INHERITED AND STATED RATHER THAN HIDDEN:** a census row
whose state cell is prose is invisible to all four of us for the same reason.
A shared parse is not a second opinion.

Controls, run before any number is printed, and **shown failing before the
instrument was trusted**:

    1. CROSS-INSTRUMENT  derived here 363   shipped counter (subprocess) 363   PASS
    2. blockers parsed             97  expected    97  PASS
    2. published rows             409  expected   409  PASS
    2. recovered == assigned      134  expected   134  PASS
    3. MUST-BE-ABSENT blocker not present                PASS
    4. EMPTY-CERTAIN implies full recovery AND zero live  0 violations  PASS
    4. EMPTY-UNCERTIFIABLE implies zero live              0 violations  PASS

Control 1 is the load-bearing one: the counter is run as a **subprocess**, not
imported, so two instruments reach the same integer without sharing a process.

**CONTROL 4 IS THE ONE WORTH COPYING, and it was added after the first three
passed.** Controls 1-3 catch a miscount. None of them catches the failure that
would actually mislead a reader: calling a blocker EMPTY-CERTAIN when rows of
it cannot be located. Planted as a mutation, that produced a clean table
saying *safe to close* about a blocker with 1 of 3 rows accounted for --
and control 4 caught it and **named the blocker**:

    4. EMPTY-CERTAIN implies full recovery AND zero live  1 violation  FAIL
          HASHTAG-EXISTENCE: recovered 1 of 3, live 0

A second planted mutation (an off-by-one in the GAP derivation) failed control
1 at 362 against the subprocess's 363.

## 2. THE FOUR CLASSES, AND WHY THE SPLIT IS THE POINT

Only **134 of 409** frozen GAP rows are named against a blocker by any
committed source. So for most blockers, *"every row I can find has left GAP"*
is **not** *"the blocker is empty"*.

| verdict | meaning |
|---|---|
| `EMPTY-CERTAIN` | recovered == published AND zero recovered rows still GAP. Every row the ledger claims is accounted for, and every one has left. **Safe to close.** |
| `EMPTY-UNCERTIFIABLE` | zero recovered rows still GAP, but recovered < published. Suggestive, **not closeable** -- the unlocated remainder is unmeasured, not absent. |
| `LIVE` | at least one recovered row is still GAP. |
| `UNLOCATABLE` | no committed source names any row against it. The published count cannot be checked at all. |

    EMPTY-CERTAIN           14 blockers     30 published rows
    EMPTY-UNCERTIFIABLE      1 blocker       3 published rows
    UNLOCATABLE             53 blockers    175 published rows
    LIVE                    29 blockers    201 published rows

## 3. PRIORITY 1 -- THE FOURTEEN ALREADY EMPTY

**Each of these is a wave that would otherwise be briefed at a closed door.**
Every published row is accounted for and every one has left GAP.

| blocker | pub | cost | queue as filed |
|---|---:|---:|---|
| `CONTACT-IMPORT` | 5 | 1 | DECIDE-RETIRE |
| `MESSAGING-SETTINGS` | 5 | 1 | DECIDE-RETIRE |
| `HELP-CENTER-FORM` | 3 | 1 | DECIDE-RETIRE |
| **`PANEL-NOT-OBSERVED`** | **3** | **1** | **MEASURE** |
| `AI-ASSIST-MESSAGING` | 2 | 1 | DECIDE-RETIRE |
| `LIVE-BROADCAST` | 2 | 1 | DECIDE-RETIRE |
| `MENTION-COMPOSITION-RULING` | 2 | 1 | DECIDE-RETIRE |
| `PARSER-ON-A-LOADED-PAGE` | 2 | 2 | BUILD |
| `DEVICE-GEOLOCATION` | 1 | 1 | DECIDE-RETIRE |
| **`FEED-PREFERENCES`** | **1** | **7** | **BUILD** |
| `MOBILE-APP-ONLY` | 1 | 1 | DECIDE-RETIRE |
| `PAID-BOOST` | 1 | 1 | DECIDE-RETIRE |
| `SIGNIN-INTERSTITIAL` | 1 | 1 | DECIDE-RETIRE |
| `VOICE-CAPTURE` | 1 | 1 | DECIDE-RETIRE |

**Ten of the fourteen were already queued DECIDE-RETIRE** and those
retirements landed 2026-09-05 (one of them 2026-09-19) -- so for those,
section 3 is merely trailing its own resolved queue. **The four queued for
EXECUTION work are the expensive ones, because there is nothing left to
execute:**

* **`PANEL-NOT-OBSERVED`, queued MEASURE.** Its three rows retired 2026-09-05.
  A wave was briefed to measure it on 2026-09-19 and found the door shut. Its
  retirement carries a live REOPENER (*"the control at 1/1/0 AND a target
  needle non-zero"*), which that wave fired on today's render: control read
  1/1/0, every target zero, **reopener did not trip**. See
  `_audit/_census/jobs.md:156,160,161`.
* **`FEED-PREFERENCES`, queued BUILD at cost 7.** Its single row `M C52` went
  EXCLUDED-RULED on 2026-09-19 -- and see s4, because its price was also in
  the wrong currency. Two independent defects on a one-row blocker.
* **`PARSER-ON-A-LOADED-PAGE`, queued BUILD at cost 2.**
* `MESSAGING-SETTINGS` and `CONTACT-IMPORT` are the two largest at 5 rows each.

## 4. PRIORITY 2 -- THE CURRENCY ERROR, AND IT RUNS BOTH WAYS

**35 of 97 blockers, carrying 192 of 409 published rows -- 47% of the census
-- are priced in `allowlist +N` currency.**

### 4.1 Where addresses have actually been measured, the price is wrong 80% of the time

`_audit/2026-09-19-settings-tail-addresses.md` pinned all 20 real
`/mypreferences/` addresses (`tests/test_the_settings_index_addresses_are_pinned.py`,
5 tests, shown failing before admission):

    allowlist match                                    2
    FORBIDDEN SUBSTRING /mypreferences/d/categories/   6
    FORBIDDEN SUBSTRING /settings/                     5
    FORBIDDEN SUBSTRING (named, one each)              5
    NO PATTERN MATCHES                                 3

> **A refusal by forbidden substring cannot be lifted by adding an allowlist
> pattern. That gate runs BEFORE the allowlist loop is consulted at all.**

So for **16 of 20** addresses the boundary cost is not `allowlist +1`; it is
*narrow a standing forbidden substring* -- a far more expensive and more
dangerous edit, and one nobody has costed.

**All seven settings-family blockers carry the identical wrong price:**

| blocker | pub | live | boundary as filed | cost | queue |
|---|---:|---:|---|---:|---|
| `FEED-PREFERENCES` | 1 | 0 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `MULTILANG-PROFILE` | 2 | 2 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `ACTIVITY-VIEW-SETTING` | 1 | 1 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `EMBED-SETTING` | 1 | 1 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `LEARNING-CERTIFICATE` | 1 | 1 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `OPEN-PROFILE-SETTING` | 1 | 1 | `allowlist +1, WriteSpec` | 7 | BUILD |
| `SKILL-PAGE-SURFACE` | 1 | 1 | `allowlist +1, WriteSpec` | 7 | BUILD |

### 4.2 It runs the other way too, and my own blocker is the instance

`ADD-SECTION-MENU` is filed **`boundary: none`, cost 3, MEASURE**. Measured
2026-09-19: the add-a-section control is three ANCHORS with no ARIA disclosure
evidence, and their target reads **`is_read_url=False` with
`forbidden_tokens_present=[]`** -- **undeclared, NOT forbidden.** So it needs
an allowlist entry it is not charged for. A blocker priced at zero that costs
one.

> **The two errors share a mechanism: the price was set from a GUESS about
> which gate would refuse the address, by people who did not have the
> address.** The census already warned of this -- *"an `allowlist +1` on a
> settings row is a PLACEHOLDER FOR AN UNKNOWN -- nine instances measured, 0
> of 9 rows names an in-product address."*

### 4.3 How far it generalises -- bounded honestly

**I cannot extend this to the other 28 allowlist-priced blockers, and I will
not pretend to.** The settings family is the only one whose addresses anybody
has measured. What IS derivable:

* **20 of the 35 allowlist-priced blockers are `UNLOCATABLE`** -- not one of
  their rows can be named from a committed source. **Their price is attached
  to a membership nobody can enumerate.** You cannot cost a boundary change
  for rows you cannot list.
* Of the 15 that are locatable, 7 are the settings family above and are
  measured wrong.

**The route to settling the rest is to measure addresses, not to re-cost from
the desk** -- exactly what the settings wave did, and the reason its numbers
are usable.

## 5. PRIORITY 3 -- MIS-QUEUED

**37 of the 53 `UNLOCATABLE` blockers are queued for execution work:**

    MEASURE   19
    BUILD     18
    DECIDE     7
    RE-FILE    4
    BLOCKED    4
    NOT-OURS   1

**A BUILD or MEASURE order against a blocker whose rows nobody can enumerate
is an order to work on an unknown set.** The first artifact those 37 need is
not a build and not a measurement -- it is a row assignment, which is
`skew-gate`'s evidence-line work this round.

Individually mis-queued, on measured grounds:

| blocker | filed | should be | why |
|---|---|---|---|
| `PANEL-NOT-OBSERVED` | MEASURE | CLOSED | three rows retired 2026-09-05; reopener fired 2026-09-19 and did not trip |
| `FEED-PREFERENCES` | BUILD | CLOSED | single row EXCLUDED-RULED 2026-09-19 |
| `ADD-SECTION-MENU` | MEASURE | DECIDE | the address is undeclared; no measurement moves it, only a ruling |
| `AUDIO-EVENTS-EXISTENCE` | MEASURE | DECIDE | needs a consent ruling on opening a creation composer, not a read |

`AI-INTERVIEW-PRODUCT` is worth a line although it stays LIVE: **14 published,
14 recovered, only 3 still GAP.** It is 79% drained and still filed at 14.

## 6. WHAT THIS DOCUMENT CANNOT SEE

1. **A RE-FILE READS AS AN ABSENCE.** This is the sharpest limitation and it
   produced the one `EMPTY-UNCERTIFIABLE`. `HASHTAG-EXISTENCE` publishes 3
   rows and recovers 1 (`M C11`). Its other two were **not lost -- they were
   re-filed**: `N 194` to `SEARCH-RESULTS-SURFACE` (LEDGER-AMENDMENT) and
   `M C52` to `FEED-PREFERENCES` (RECON-DOC). The instrument sees a row that
   is no longer assigned to a blocker as unrecovered, and cannot tell that
   from a row nobody ever assigned. **So `HASHTAG-EXISTENCE` is very probably
   empty and this document declines to certify it**, which is the honest
   output rather than a hedge.
2. **275 of 409 rows are UNASSIGNED**, so 53 blockers get no verdict beyond
   "cannot be checked". That is not a gap in this instrument; it is the
   headline finding of `_audit/2026-09-05-blocker-map.md` restated with
   today's states.

   > **MOVED DOWNWARD LATER THE SAME DAY -- quote 268.** `ae1894b` recovered
   > seven rows and closed three blockers at their published counts. The
   > figures above were correct when measured and are left standing rather
   > than rewritten; finding 6.1 asks for a pointer, not for a document that
   > edits its own history to look prescient. **RE-DERIVED with this
   > document's own script rather than recomputed by hand**, per its header:
   >
   >     EMPTY-CERTAIN           13 -> 14 blockers    28 -> 30 published rows
   >     EMPTY-UNCERTIFIABLE      1 ->  1 blockers     3 ->  3 published rows
   >     UNLOCATABLE             53 -> 50 blockers   175 -> 168 published rows
   >     LIVE                    30 -> 32 blockers   203 -> 208 published rows
   >
   > **THREE BLOCKERS LEFT `UNLOCATABLE`, AND ONE OF THEM IS A PRIORITY-1
   > ENTRY THIS DOCUMENT COULD NOT SEE.** `MENTION-COMPOSITION-RULING` is now
   > `EMPTY-CERTAIN` -- 2 published, 2 recovered, **0 live** -- and it is
   > queued **DECIDE**. That is exactly the shape section 3 is about: a
   > blocker queued for a ruling that has nothing left to rule on. It belongs
   > in the priority-1 table above and is not added there by me, because that
   > table is this document's own derivation and re-running the script is the
   > sanctioned way to refresh it.
   >
   > The other two became `LIVE` rather than empty: `COLLABORATIVE-CONTENT`
   > 4 recovered / 3 still GAP, `PUBLISH-POST-AUDIENCE-PARAM` 1 / 1. Both were
   > uncheckable before and are checkable now, which is the point of recovery
   > rather than a verdict about them.
3. **The shared-parse blind spot**, inherited from `count_census_states`: a
   row whose state cell is prose is invisible. `N 132` is the known instance.
4. **`published` is the ledger's own 2026-09-03 figure** and some of those
   counts are themselves disputed -- `_audit/2026-09-06-corpus-sweep-blocker-evidence.md`
   has four open conflicts. This document refreshes STATES against published
   counts; it does not adjudicate the counts.

## 7. HANDOVER

**No new assignable rows are handed over.** I looked: the rows this wave
touched are already assigned (`M C52` to `FEED-PREFERENCES` as RECON-DOC,
`N 194` to `SEARCH-RESULTS-SURFACE` as LEDGER-AMENDMENT, both landed by other
waves). `skew-gate` owns the evidence file this round; `blocker-map.tsv` is
GENERATED by `scripts/build_blocker_map.py --write` from
`_audit/_census/blocker-assignments.tsv` and **was not edited here**.

To re-derive:

    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py --control
    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py
    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py --tsv

## 8. A SECOND SIGNAL ON THE LIST ANYBODY WILL ACT ON

Section 3 is the one output a reader will act on, and it is derived from row
STATE alone. **State says a row left GAP. It does not say anybody RULED it
closed** -- a row can leave GAP because a wave measured it, and it can leave
because a wave re-stated it. A blocker closed on this list deserves the
difference, so every row was independently checked for a closure CITATION in
its own census cell:

    ./venv/Scripts/python.exe scripts/blocker_table_refresh.py --provenance

**RESULT: 29 of the 30 rows cite a committed closure document.** Twenty-six
cite `_audit/2026-09-05-decide-retire-rulings.md`; the rest cite the dated
ruling that moved them.

**The one exception is not a gap in provenance, it is a limit of my needle.**
`P L2` (own follower count, `PARSER-ON-A-LOADED-PAGE`) cites
`scripts/_probe_endorse_and_follow_lines.py` and a dated live measurement
instead of an audit document, and the needle only matches `_audit/*.md`. A
probe script is arguably the stronger citation of the two.

### The provenance reader was WRONG TWICE before it was right, and both are worth recording

**Both failures produced a CLEAN, CONFIDENT, FALSE result**, which is why this
mode now ships with a control of its own.

1. **It read the wrong COLUMN.** `enumerate_gap_rows.rows()` yields `c[1]`,
   documented as `first_prose_cell` -- the CAPABILITY column. Closure
   citations live in the NOTE column. Pointed at `c[1]`, the mode reported
   *"no row carries a closure citation"* for **every row in the list**,
   including rows whose citations had been written by hand an hour earlier.
   Caught only because the author recognised a cell he had written himself.
2. **It read the wrong ROWS.** The replacement kept every pipe-table row and
   read **770 against the census's 704**. A census slice contains other
   tables and **ids collide across them**: `| 17 |` appears twice in
   `jobs.md` -- once as the census row carrying its retirement citation, once
   in an unrelated analysis table -- and the second silently overwrote the
   first, so `J 17` reported as citing nothing.

> **A READER POINTED AT THE WRONG COLUMN, AND A READER THAT MATCHES TOO MUCH,
> BOTH REPORT A TIDY ABSENCE.** Neither errors loudly. The fix in both cases
> was to adopt the shipped enumerator's filter condition for condition, and
> the control that now guards it is an equality: rows read must equal the
> shipped counter's stated-row total, and a row known to carry a citation must
> yield one.

Controls now reported before any provenance line is printed:

    a row known to cite a closure (J 25) yields one   PASS
    a string with no citation yields none             PASS
    rows read 704 == shipped stated rows 704          PASS

## 9. THIS DOCUMENT WENT STALE WHILE IT WAS BEING WRITTEN

The first derivation, 09:36 by the box: **13 EMPTY-CERTAIN over 28 rows.**
The second, 09:43: **14 over 30.**

`MENTION-COMPOSITION-RULING` joined in between, because another wave moved
`M C10` and `M C28` to EXCLUDED-RULED with a retirement dated 2026-09-19 --
neither row touched by this wave. Seven minutes.

**That is not an embarrassment to put in a footnote; it is the finding this
document exists to make, arriving to its own author.** Section 3's counts are
wrong for exactly the same reason, and they had sixteen days rather than seven
minutes to drift. **Re-derive. The script takes seconds and needs no browser.**
