# The 117 invisible census rows, classified — and the cause was a DIALECT, not prose

**CORRECTS:** `_audit/2026-09-05-census-recounted.md` — its section 5 describes `--unstated` as listing "every row in a capability table carrying no recognised state". It lists rows in EVERY table, capability or not, and 78 of the 117 are correctly stateless. The same section's open one-row disagreement — "369 is what the instrument reads, 370 is what the census says" — is closed here, toward the census.

Wave `census-hygiene`, 2026-09-05. Commits `083a872` (the restoration) and `ba145db` (the guard).

---

## 1. THE HEADLINE, AND IT IS NOT THE ONE I WAS BRIEFED WITH

The brief was that 117 rows are invisible because a state cell was **replaced with prose**. Measured against the files, **that is true of exactly two rows.** The dominant cause is something else entirely, and it is worse in one specific way: it is invisible to a reader as well as to a parser.

    stated rows   667 -> 704   (+37)
    --unstated    117 ->  80   (-37)
    GAP           369 -> 370   (+1)

**37 rows restored. 80 remain listed and 78 of those SHOULD remain listed.** The two that should not are named in section 5.

## 2. THE 117, CLASSIFIED BY WHAT THE ROW ACTUALLY SAYS

Every row was read. None was assigned a state from its topic.

| n | class | what the cell holds | resolved? |
|---|---|---|---|
| 23 | **`XR` — an unknown dialect** | a correct, deliberate verdict the counter cannot spell | yes, in the instrument |
| 10 | **no state column at all** | `network.md`'s Recommendations table shipped without one | yes |
| 2 | **`CANNOT-DELIVER`** | right verdict, non-canonical spelling | yes |
| 1 | **prose qualifying a state** | `COVERED-PROVEN, WITH A MEASURED RELIABILITY DEFECT` | yes |
| 1 | **prose replacing a state** | `N 132`, the known case | yes |
| 78 | **correctly stateless** | summary tables, headers, reference tables, roll-ups | no, and must stay so |
| 2 | **declared stateless** | `J 58`, `M C53` — the slice says so in prose | no, by the document's own words |

### 2.1 `XR` — 23 rows, and the biggest single thing nobody could see

`jobs.md` spells EXCLUDED-RULED as **`XR`**. It does so 23 times, **in that slice and nowhere else in the four**, and `jobs.md`'s own frozen table reads `EXCLUDED-RULED | 23`. The counter already knows four short forms — `CP`, `CU`, `CCD`, `ER` — so a dialect was expected; this one was simply missing from the set.

**These 23 rows were never defective.** Each carries a written refusal citing repo code — `readonly.py:198`, `server.py:3906`, the mutation-verb denylist. Somebody did the work, wrote the reason, and put it in the right cell. **The instrument could not read it, for a fortnight, in silence.**

> **A row can be invisible while being perfectly written.** The prose class at least leaves a sentence a human reader will notice. A dialect leaves a cell that looks completely normal, and only a counter can tell you it is not being counted.

**FIXED IN THE COUNTER, NOT IN THE CENSUS.** Rewriting 23 of a neighbour's cells to satisfy my own parser is the bulk re-baseline this repository has a standing rule against. `XR` is reported under its own key rather than folded into EXCLUDED-RULED — exactly as `CP`/`CU` already are — because a counter that silently merges two spellings cannot show you that a slice uses two.

### 2.2 The Recommendations table — 10 rows with no state column

`network.md` section K is headed **"Recommendations (10) — all EXCLUDED-RULED under R3"** and its table is `| # | capability | R/W |`. **There is no state column.** Ten capability rows were in no counter's numerator and no counter's denominator, in either direction.

The state column was added and every cell carries the value **the section's own heading states**. No new judgement, and the "precision flag" paragraph below the table — which records that five of the ten are EXCLUDED-RULED *to the letter of the ruling* and *unmeasured to the evidence* — is untouched and still governs.

**Corroborated by an independent number rather than by my reading of the heading:** the counter reads network `EXCLUDED-RULED 75`; subtract the 7 that `census-apply` moved today and the pre-existing figure is 68; the slice's frozen table says **78**. The gap is **exactly these ten**.

### 2.3 The same corroboration, twice more

    jobs.md      frozen EXCLUDED-RULED 23   counter read 15 (all census-apply's)   gap = the 23 XR rows
    messaging    frozen COVERED-CANNOT-DELIVER 2   counter read 0   gap = M1 and M2

**Each restored class predicts a number written down before I arrived, and hits it.** That is the check that matters here, because the alternative — reading a row and deciding what it means — is exactly how a census acquires verdicts nobody ruled.

### 2.4 The two prose rows

* **`P G1`** held `COVERED-PROVEN, WITH A MEASURED RELIABILITY DEFECT`. The verdict is the first token; the counter splits on space and got `COVERED-PROVEN,` **with the comma**, which matches nothing. State restored, qualifier moved into the note beside it.
* **`N 132`** held a live-read sentence. Its own note ends *"This row stays GAP anyway and the reason is narrow."* Restored to `GAP`, sentence kept. This is `search-appearances`' line; `census-apply` routed it rather than rewriting a neighbour's row, and this wave was briefed to make it. **Its verdict is unchanged — only its visibility.**

## 3. THE ONE COUNT THAT MOVED, AND WHY IT SHOULD

**`GAP 369 -> 370`, and it is `N 132` alone.** Section 2 of `census-recounted` says *"369 is what the instrument reads. 370 is what the census says."* That disagreement is now closed, and it closed toward the census. No other restored row was GAP, so no other GAP moved.

The other movements are between non-GAP states: `EXCLUDED-RULED 219 -> 229`, `XR 0 -> 23`, `COVERED-CANNOT-DELIVER 6 -> 8`, `COVERED-PROVEN 24 -> 25`.

**NONE OF THIS IS COVERAGE.** The proven-capability count moved by one row — `P G1`, which was already proven and already written down. Nothing was built today.

## 4. AGAINST THE DENOMINATOR

`stated rows` is a ROW count; 755 is a CAPABILITY count over a basis that collapses two profile blocks (59 capabilities on 2 lines). They are different objects and this document does not divide one by the other.

The honest reconciliation is against the ledger's **705 table rows**:

| slice | ledger rows | stated now | reconciles? |
|---|---|---|---|
| jobs | 151 | 150 + `J 58` declared stateless | **exact** |
| network | 209 | 209 | **exact** |
| profile | 202 | 203 | **+1, not chased** |
| messaging | 143 | 142 + `M C53` tombstone | **exact** |

**704 stated + 1 declared stateless = 705.** Two slices reconcile exactly, and profile is one row over the ledger's 202 while messaging is one under — **they cancel in the total, which is precisely the arithmetic that hides a pair of errors.** I did not chase either and I am not claiming they are the same row.

## 5. WHAT I DID NOT RESOLVE

**Two rows remain unstated that I believe should carry a state, and I did not give them one.**

1. **`N 132`'s five siblings — rows 121, 122, 123, 126, 128** now read EXCLUDED-RULED because the section heading says so, while the paragraph beneath says they are *"to the evidence, unmeasured"*. I transcribed the heading. **If that paragraph is right, five rows are now countable under a state their own document doubts** — visible and possibly wrong, where before they were invisible and possibly wrong. I judge visible-and-doubted better than invisible, and I am flagging it rather than burying it. Owner: whoever holds `network.md` section K.
2. **`profile.md` is one row over its ledger figure.** Unexplained. Section 4.

**And two rows I deliberately left stateless, on the document's own authority:**

* **`J 58` (bulk-unsave)** — `jobs.md` declares it: *"a thing LinkedIn itself does not offer, so it takes no state. The denominator is 150 distinct job capabilities."* Its cell reads `n/a`. **Not a defect. Not invented, not changed.**
* **`M C53`** — a retirement tombstone, every cell `--`, kept *"rather than deleted"* so the id is not silently reused.

**The 78 correctly-stateless rows are not a backlog.** They are four slices' summary tables, table headers the counter's `HEADERS` set does not name, a Help-Center URL reference table, a hole-verdict table, a build-cost roll-up whose rows restate rows counted elsewhere (`J 9-14`, `J 92-100`), and two three-column lists. **A guard that demanded a state from those would be a guard nobody could keep green, and it would be deleted within the week.**

## 6. THE GUARD, AND WHAT ITS FIRST RUN TAUGHT ME

`tests/test_census_rows_carry_a_state.py`, commit `ba145db`. It asserts over exactly the rows where a missing state is a defect: **a row in a table whose own HEADER declares a `state` column.** That table promised a state per row.

**SHOWN FAILING FIRST, on the row that started the class:**

    sha256 BEFORE             959cb67f...469ad3
    PLANTED (N 132's state cell replaced with prose)     rc=1
      "1 row(s) in network.md sit in a table whose header declares a state column"
      1 failed, 4 passed
    sha256 AFTER RESTORE      959cb67f...469ad3      byte-identical: True
    RESTORED                  rc=0     5 passed

The restore came from a **byte copy taken before the edit**, not a retyped string. `git status` on the census directory was clean afterwards.

**THE GUARD'S FIRST RUN FAILED ON ITSELF, AND THAT IS WHERE THE REAL SCOPE CAME FROM.** Scoping on the header word `state` alone red-flagged all four slices' opening summary tables — headed `| state | count | share |`, where `state` names the **row** rather than a cell in it. So the extra condition is that **`state` must not be the FIRST column.** A guard failing on the one thing it exists to ignore is cheap to find and impossible to find by reading.

**Two genuine finds came out of that same first run** — `M M1`/`M M2`'s non-canonical spelling — and are in `083a872`. **The guard paid for itself before it was committed.**

It **imports** `scripts/count_census_states.py` rather than reimplementing its parser. Four waves reimplemented a shipped instrument here in one day and three got a broken one; if the guard and the counter disagreed about where a state lives, the guard would certify a count the counter cannot take.

`DECLARED_STATELESS` holds the two rows above, and a **second test asserts both are still stateless** — so the list can only shrink by measurement. An allowlist nobody prunes is a blind spot wearing an allowlist's name.

## 7. THE METHOD NOTE WORTH KEEPING

The brief handed me a cause — *prose in a state cell* — and a count, 117. **Both were true statements about the instrument's output and neither was a description of the defect.** The 117 is what `--unstated` prints; it prints rows from every table in the file, and its own docstring says it lists rows *"in a capability table"*, which the code never checks.

> **A diagnostic's OUTPUT and a diagnostic's DESCRIPTION drift apart silently, and the description is the half that gets quoted.** Two independent parsers agreed on 406 because both shared an assumption about where a state lives. A third reading — reading the rows themselves — was the only thing that separated 2 real prose cells from 23 rows written correctly in a dialect.

Same shape as everything else in this repository this week: **the number was right, the sentence attached to it was wrong, and the sentence is what travelled.**

## 8. RECEIPTS

    restoration          083a872   4 files, 32 insertions, 17 deletions
    guard                ba145db   tests/test_census_rows_carry_a_state.py, 152 lines
    counter              scripts/count_census_states.py  (XR taught, tracked)
    recount, recomputed  stated rows 667 -> 704 (+37); --unstated 117 -> 80 (-37); GAP 369 -> 370
    red/green            planted -> rc=1 naming 1 row; restored byte-identical -> rc=0, 5 passed
    push                 none. Blocked on an unrelated history rewrite
