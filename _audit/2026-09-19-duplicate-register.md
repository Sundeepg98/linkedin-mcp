# The duplicate register — a KNOWN and QUANTIFIED overcount, not a subtraction

**Nothing here is subtracted.** Per the ruling: these have no documented
conditional, so acting on them is a new decision. What they had been was an
*unknown* overcount; this makes it a known one.

**Sequencing note:** the ruling held these until `761` reconciled. **It
reconciled** (`3ecd102`) — the derivation reproduces to within one row, both
collapsed blocks exist, and `P-R` is a section heading a regex of mine could not
match. So the dependency is discharged; the remaining block is the absence of a
conditional, which is unchanged.

---

## 1. THE HEADLINE NUMBER, DECOMPOSED

I reported **13 confirmed**. Adjudicating each against its twin's full text
splits them three ways, and **only the first group is subtractable under my own
rule**:

| class | count | subtractable? |
|---|---:|---|
| **CLEAN** — near-identical capability, both sides agree on state | **10** | yes, if ever ruled |
| **CONTAINMENT** — one side is a subtype of the other | 1 | **no** — needs a ruling on which survives |
| **BUNDLED** — one row spans two rows in the other slice | 2 | **no** — *a bundled row is not a clean duplicate and must not be subtracted as one* |

**So the quantified overcount is 10 capabilities, not 13**, with 3 more that are
real relationships and wrong to treat as identities.

## 2. THE TEN CLEAN DUPLICATES

Every pair verified live on both sides; both states normalised and **agreeing**.

| # | row | capability | twin | state (both) |
|---|---|---|---|---|
| 1 | `J 76` | Opt out of saving job-application data | `P M7` | EXCLUDED-RULED |
| 2 | `J 89` | Turn Open to Work on / off | `P I2` | EXCLUDED-RULED |
| 3 | `J 74` | "Share resume data with recruiters" toggle | `P M8` | EXCLUDED-RULED |
| 4 | `P F5` | Delete a recommendation you sent | `N 125` | EXCLUDED-RULED |
| 5 | `P E8` | Opt out of endorsements entirely | `N 115` | EXCLUDED-RULED |
| 6 | `M M1` | Message a 1st-degree connection | `N 155` | COVERED-CANNOT-DELIVER |
| 7 | `P L4` | Newsletter analytics | `M C83` | GAP |
| 8 | `M M4` | InMail credit balance | `N 157` | EXCLUDED-RULED |
| 9 | `P O22` | The list of members you have blocked | `N 143` | EXCLUDED-RULED |
| 10 | `P E6` | Hide / show an endorsement received | `N 114` | GAP |

**#8 is a TRIPLE, not a pair.** `jobs 127` states the same InMail-balance
capability as a third row. It is not counted again above, but **a subtraction
there removes two rows, not one**, and whoever rules should know that before
arithmetic.

## 3. THE THREE THAT ARE NOT CLEAN, AND WHY EACH IS DIFFERENT

* **CONTAINMENT — `M M38` *Report a message as spam* vs `N 149` *Report a
  message*.** Spam is a *subtype* of reporting. Subtracting either loses a
  distinction the census may want; the ruling is which grain the census keeps.
* **BUNDLED — `M C80` *Subscribe or unsubscribe to a newsletter* spans `N 55`
  *Subscribe* and `N 56` *Unsubscribe*.** One row against two. **Subtracting
  `C80` removes two capabilities and one row, and the counts diverge.**
* **BUNDLED — `P O21` *Block / unblock a member* against `N 142` *Unblock*.**
  `O21` carries both halves; `N142` carries one.

**This is the collapsed-block problem at a scale of two**, and it is the same
shape as `O6-O20` holding fifteen capabilities in one row — which is what hid
four double-counts from every lexical pass until they were read by hand.

## 4. WHAT THIS REGISTER DELIBERATELY DOES NOT DO

* **No subtraction, no state change, no census row edited.** The four executed
  earlier had a written conditional in `messaging-and-content.md` s10 and its
  trigger was measured met. **These have no conditional**, and
  `profile.md`/`jobs.md` carry no reconciliation register at all.
* **No tail estimate.** 229 same-state candidates were swept; **13 were read and
  adjudicated; 216 were not.** Head precision was 13 of 16, and the head is
  where a lexical matcher is strongest — its ordering **concentrates truth
  without separating it**, measured twice today. `229 x 0.81` would be a
  fabrication with a decimal point.
* **No claim that these are all of them.** The method is lexical and cannot see
  a paraphrase sharing no vocabulary, and it demonstrably cannot see a collapsed
  block at all.

## 5. HOW THE POPULATION WAS FOUND, because it inverts the obvious search

**A different-state filter selects AGAINST true duplicates**, because two slices
stating one capability usually agree about it. Every precision figure reported
for this matcher — 7 of 15, and a sibling's 1 of 61 — **was measuring the
filter, not the matcher.**

Measured contrast once the filter was corrected: **13 of 16 at the head, against
7 of 15.**

**And the correction itself was a bug of mine:** `jobs.md` writes `XR` where the
other slices write `EXCLUDED-RULED`, so every pair agreeing in two dialects read
as a disagreement and was dropped. `count_census_states.py` **documents that
exact defect against itself** — `XR` cost it 23 invisible rows, *"a dialect this
instrument did not speak"* — and I read that docstring the same morning and
wrote the same defect anyway.
