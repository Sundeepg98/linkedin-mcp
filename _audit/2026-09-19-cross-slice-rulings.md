# Only one slice names its rulings, and that is why verdicts do not propagate

**THE HEADLINE.** Of 233 candidate cross-slice disagreements, **133 are GAP vs
EXCLUDED-RULED** — the class where a ruling exists on one side. Joining all 133
back to the ruling behind the EXCLUDED-RULED verdict gives the structural
result: **32 cite a named ruling and all 32 are in `network.md`. The other 101
cite nothing.** The propagation failure is not random. One slice built a ruling
register and the rest did not, so one slice's verdicts can be checked and
followed, and everyone else's cannot.

**233 IS A CANDIDATE COUNT AND IS NOT A FINDING COUNT.** Measured precision on
the head of the list is **7 true / 8 false**, hand-counted. Everything below is
adjudicated against a named artifact or it is not claimed.

---

## 1. WHERE THE UNCITED VERDICTS LIVE

    profile.md   57      network.md   24      messaging   14      jobs.md   6

**`profile.md` holds 57 verdicts with no citable basis in the row.** Its reasons
recur as prose instead of ids — `settings family` x7, `composer` x6, `never
loaded` x3. **A prose ruling is still a ruling; it simply cannot be propagated
by anyone who did not write it.** That is the whole mechanism of this failure
class, stated in one line.

## 2. THE DISCRIMINATOR — a propagation failure is not a considered exception

Two rows can both sit GAP beside an EXCLUDED-RULED twin and mean opposite
things, and the census already distinguishes them in prose:

| row | what its note says | reading |
|---|---|---|
| `M C69` Invite connections to a group | *"reaches third parties; `/invite` is a forbidden substring"* | **states the ruling's own premise and files GAP anyway** — a propagation failure |
| `P E6` Hide / show an endorsement received | *"`/endorse` is a forbidden substring. **The written reason does not reach this act**"* | **argues the ruling's scope excludes it** — a considered exception |

**So the test is not "is there a ruling nearby". It is whether anybody weighed
its SCOPE.** `E6` did and said so; `C69` did not. I flipped `C69` and left `E6`
exactly where it is — a row that reasons about a ruling and declines it is doing
the thing this document is asking for, not failing to.

## 3. TEN ROWS FLIPPED, EACH NAMING ITS ARTIFACT

Every premise was re-verified against the **shipped predicate at this tree**
rather than read out of the ruling's prose:

    /invite  /connect  invitation  /withdraw       all on _FORBIDDEN_URL_SUBSTRINGS
    /mypreferences/d/categories/                   on it too
    categories/notifications, categories/privacy   is_read_url = False
    premium/my-premium (both spellings)            is_read_url = True

### 3.1 Four rulings that reached one slice and not its twin (`c95e09b`)

| row | artifact |
|---|---|
| `P B10` Open Profile setting | **R11**, twin `N159`. Corroborated independently: the settings index draws 20 addresses and this toggle is not among them, so it sits behind a denylisted `categories/` page. Was GAP on the words *"no tool, no reason"* |
| `M C69` Invite connections to a group | **R2** — and the row's own note stated R2's premise |
| `M M24` Group-chat notification settings | **R11**; its own note calls it *"a settings sub-surface"*, and that category page measures unreadable |
| `M M5` Send an Open Profile message | **R9** (four independent rulings), twin `N158`; the note also states **R4**'s condition |

### 3.2 Six Open-To-Work rows propagated into `jobs.md` (`539752b`)

`J92`–`J97` → EXCLUDED-RULED, each naming its `profile.md` twin `I4`–`I10`.

**The second artifact needs no second slice**: `jobs.md`'s own collapsed-block
note says *"92-100 all live behind the same modal as rows 89-91"* — and 89, 90,
91 are **XR in that same slice**. It already excludes the rows it says share the
blocker.

**The counter-argument is written into the rows**, not buried: the 2026-09-05
wave called this an operator-present DECIDE row, and one consented capture
reopens the block. This makes `jobs.md` agree with the state the census owner
already chose for the same capabilities. **It does not make the ruling.**

## 4. WHERE THE FALSE PAIRS CLUSTER, so the next reader does not re-find them

Precision is worst exactly where the shared word is most generic:

* **`settings family` — 1 true of 7.** "Settings" collides across unrelated
  capabilities: interface language vs people-search profile-language filter;
  two-step verification vs a job posting's verification badge; the blocked-list
  vs the following-list. The one true pair (`P N26` / `M C89`, mentions and
  tags) was **already measured by a sibling today** and left alone.
* **"send X to a 1st-degree connection"** matches message, recommendation,
  endorsement and removal — four capabilities, one phrase.
* **"report X"** matches report-a-profile, report-a-job and report-a-message.

**`M M6` "Send a message request" was NOT flipped**, and the reason is the
discipline rather than the verdict: the matcher paired it with `N158`, which is
specifically the Open Profile message. There is no twin for a message request,
so there is no propagation artifact — and a flip justified only by a similarity
score is the thing this document exists to avoid.

## 5. THE SEAM, AND WHAT WENT THE OTHER WAY

The ruling is that two slices disagreeing is this wave's; a row contradicted by
**shipped code** belongs to the code seam, because a slice is a claim and the
package is the thing. **`jobs.md 127` (InMail balance) is both, so it went
there** — GAP on the claim *"the boundary entry and reader are NOT built"* while
`is_read_url` returns **True** for both spellings. Handed over with its
adjudication and a bounded 61-pair candidate list, not flipped here.

## 6. WHAT THIS METHOD CANNOT SEE

It is **lexical, not semantic**: a true paraphrase sharing no vocabulary never
appears as a candidate at all. Collapsed blocks — `profile.md` states 15 and 45
capabilities as single rows — dilute against any single matching row. A
capability that is a row in one slice and prose in another is invisible. And the
sweep's own calibration found two defects worth keeping on record:
a corpus-frequency stopword cutoff that stripped `job` as filler and broke the
very pair it was calibrated on, and **`difflib.SequenceMatcher.ratio()` being
asymmetric** — 0.533 vs 0.667 on the same two strings depending on argument
order, while the loop fixed that order alphabetically.

**So the honest statement of extent is: at least ten rows, a measured ~50%
precision at the head, and an unknown tail.** Not 233.
