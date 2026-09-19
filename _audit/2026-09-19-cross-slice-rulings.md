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

---

# AMENDMENT A — the deepest reason: ONE ruling, THREE names, nothing to search for

Section 1 says one slice named its rulings and the rest did not. That is true and
it is not the whole mechanism. **The same shipped ruling has been independently
re-derived and re-named in three slices**, which is why no amount of diligence
inside any one of them could have found the others.

One sentence in the package, `linkedin_server/server.py:7371` (in
`linkedin_update_setting` — **cite the symbol, the line has already drifted
once**):

> *...is admitted by name or not at all.*

and three census names for it:

| slice | how it appears | citable? |
|---|---|---|
| `network.md` | **`R11`** — *"the settings family is admitted by name or not at all"*, with a scope and a 21-row list | yes |
| `messaging-and-content.md` | **`MESSAGING-SETTINGS` (3.10)** — *"a setting is admitted by name or not at all"* | yes, under a different id |
| `profile.md` | bare prose **`settings family`**, 7 rows, no id and no citation | **no** |

**A ruling that is RE-DERIVED rather than CITED cannot propagate, because there
is nothing to search for.** Three waves each read the same sentence in the same
file, each wrote down a correct verdict, and each invented a name for it. Any
reader auditing `R11` finds 21 rows and stops; the other two names are invisible
to that search.

## A1. The case that proves it, because the disease recurred inside its own cure

`M M42`'s note, written 2026-09-05:

> **RE-FILED as EXCLUDED-RULED under `MESSAGING-SETTINGS` (3.10). NOT a new
> decision — the operator already made it and TWO CENSUS SLICES APPLIED IT
> DIFFERENTLY.**

A wave diagnosed this exact disease, on this exact capability, named it
correctly, fixed the messaging side — **and left its own twin `N 170` GAP for
two weeks.** Flipped here (`260e29d`).

**The propagation failure recurred inside the act of fixing a propagation
failure**, and it did so because the fix introduced the third name rather than
citing the first.

## A2. I walked past it too, which is the honest part

My own settings-tail wave on 2026-09-19 quoted this same sentence — from
`server.py:6874`, as the line then was — and treated it as the shipped ruling
governing that surface. **I did not recognise it as the ruling the census
already files under two other names**, and I had read `network.md`'s R11 in the
same session. Four encounters with one sentence before anyone joined them.

## A3. The remedy is a name, not a re-derivation

Nothing here needs a new decision. What it needs is that the three names resolve
to one, and the only durable anchor is **the symbol in the package** —
`linkedin_update_setting` — since the line number has already moved and one
census note says so in its own text. That is a single edit to three slices and a
ruling nobody has to make.

**I have not made it**, because renaming a ruling across three slices is a
census-wide convention change with an owner, and my mandate here is rows that
disagree — not the register they cite. Routed with the evidence rather than
taken.

---

# AMENDMENT B — two more relation types the matcher cannot see

Section 4 lists where false pairs cluster by SHARED PHRASE. Two further classes
are structural rather than lexical, and neither is a disagreement at all.

## B1. CONTAINER and CONTENT — a page ruled out, a control on it still GAP

    P I12  Job preferences / career-interests page        EXCLUDED-RULED
           ("measured: zero of 237 urls reach one")
    J 99   Control career-interests visibility to recruiters   GAP

**These are not the same capability.** One is the SURFACE, the other is a
CONTROL on it. The matcher scores them alike because they share the distinctive
token `career-interests`, and a wave working from the score alone would flip the
control because its container is ruled out.

**I did not flip it.** Whether a ruled-out container rules out its contents is a
question nobody in this census has answered, and it is a different question from
the one this wave was given. A page measured unreachable across 237 captured
urls is not the same claim as a control being unreachable — the Open-To-Work
editor is exactly the case where the surface has no url and the controls are
still reachable, by a click.

**So this is a third relation type**, beside "same capability" and "different
capability", and it needs a ruling rather than an adjudication.

## B2. READ vs WRITE of one subject — states that are SUPPOSED to differ

The `COVERED-PROVEN vs EXCLUDED-RULED` class (19 pairs) looks like the sharpest
contradiction available — one slice says built, the other says will-not-build.
**Hand-reading the ten highest-scoring shows it is mostly not a contradiction at
all:**

    jobs 88  READ the current Open to Work state    COVERED-PROVEN
    P I2     Turn Open To Work on or off            EXCLUDED-RULED

Reading a value is built; writing it is ruled out. **Both are correct, and the
states are supposed to differ.** The same shape recurs across the class: read
the Who's-Viewed list vs unsubscribe from its emails; read notifications vs
manage them; filter by employment type vs edit employment type on a position.

**THE LIMIT, AND IT IS A LIMIT ON ME, NOT ON THE DATA.** I tried to confirm this
across all 19 by extracting each row's R/W column and counting opposite pairs.
**The extractor failed: 74% of that subset came back "unknown"**, because the
R/W column sits at a different index in each slice's table and my heuristic
could not find it. So:

> **The read/write reading rests on hand-inspecting ten pairs, not on a
> measurement over nineteen.** The automated check I ran does not support it and
> does not contradict it — it mostly measured my own parser.

Reported that way rather than dropped, because a number that turns out to be
about the instrument is exactly the thing this repository keeps catching late.
The cheap fix, for whoever wants the count: parse the R/W column per slice from
that slice's own header row instead of guessing its index.

---

# AMENDMENT C — B2 IS REFUTED, and the real answer is a hole in the corpus

Amendment B2 said the `COVERED-PROVEN vs EXCLUDED-RULED` class is mostly READ vs
WRITE of one subject, and flagged that my check returned 74% unknown. **I rebuilt
the check properly and it does not support B2.**

## C1. The parser was guessing; the deeper cause is structural

The fix was to read each table's OWN header rather than assume a column index.
Headers repeat per section and the four slices do not agree:

    jobs.md      | # | capability | source | state | tool/reason |     NO R/W COLUMN
    profile.md   | # | capability | R/W | state | evidence |           R/W present
    messaging    | # | capability | Help Center | state | R/W | REV |  R/W present
    network.md   | # | capability | R/W | state | note |               R/W present

Measured across the whole census:

    jobs                   151 rows,   0 with R/W    <- records direction NOWHERE
    profile                202 rows, 199 with R/W
    messaging-and-content  143 rows, 138 with R/W
    network                209 rows, 208 with R/W

**One of the four slices does not record read-versus-write at all.** So for any
pair with a `jobs.md` side, the direction question is **not answerable from the
census by anyone**, however well they parse it. My earlier "74% unknown" was not
a parser defect to be fixed — it was this hole, wearing a parser defect's
costume.

## C2. The answer to "is this a third class or an artefact": NEITHER, YET

| | of 19 |
|---|---:|
| have a `jobs.md` side, so direction is unrecorded | **14 (74%)** |
| adjudicable from the census's own column | **3** — 2 same direction, 1 opposite |

Three pairs cannot decide a class. And inferring direction from the capability
TEXT instead — a weaker source, and the one my hand-reading actually used —
gives **4 opposite / 6 same / 9 ambiguous**: no dominant pattern either.

> **So B2's read/write reading is withdrawn.** I hand-read ten pairs, saw a
> pattern in their wording, and generalised it to nineteen. The census's own
> column can confirm it for three, and text inference puts "opposite" at 21%.

**The honest verdict for the lead: the 19 are 84% unanswerable, and the reason
is a missing column rather than anything about the pairs.** Assigning the class
to anyone before that hole is named would hand them a question the corpus cannot
answer.

## C3. What this costs elsewhere, including my own earlier work

`jobs.md` is **151 of 705 rows**. Any analysis that keys on R/W — a blocker's
published `11W` split, a read-only/write-only queue, a boundary cost that turns
on whether a row is a read — **silently loses a fifth of the census**, and loses
it as "unknown" rather than as an error.

**It bears on my own blocker-20 mistake.** I called `11 rows, 11W` a match "on
two independent axes". The `W`-ness of the real set (`J92`–`J98` + `I13`–`I16`)
is knowable for the `profile.md` half and **unrecorded for the seven `jobs.md`
rows** — so even the axis I thought I had was half absent. The test was weaker
than I understood at the time I over-claimed it.

**The cheap repair is a column, not a ruling**, and it is not mine: adding `R/W`
to `jobs.md`'s five table headers is a slice-owner's edit. Routed with the
number attached — 151 rows, 0 recorded — so whoever takes it knows the size.

---

# AMENDMENT D — what the 61-pair handoff came back as, and what it says about the RANKING

`small-measures` adjudicated the whole 61-pair COVERED-vs-GAP list I handed over
(`de48d76`) and the result is **1 true of 61**. Their finding outranks the row,
and it is about my instrument rather than theirs, so it belongs here.

## D1. Verified in my own data, not accepted from theirs

The one true pair — `P K10` / `J 27`, the verification badge on a posting —
scores **0.589** in my list. Checking the distribution of the file I handed over:

    scores above it:  0.869  0.712  0.683  0.595      <- four pairs, ALL FALSE
    the true pair:    0.589                           <- rank 5 of 61

**Every pair scoring higher than the only true one is false.**

## D2. The accurate statement, which is narrower than "the ranking is useless"

With one true pair in 61, chance would put it at rank ~31. It came back at rank
5 — **the top 8%** — so the score does carry signal. But:

> **The ordering CONCENTRATES truth without SEPARATING it.** Any cutoff above
> rank 5 loses the only true pair, and every cutoff at or below rank 5 admits
> four false ones first.

**So "precision at the head" — the framing I used in section 1 and in the
handoff README — overstates how usable the ordering is.** It reports a rate and
implies a strategy (work from the top), and the strategy does not follow from the
rate. A 7-true-of-15 head is not 7 findings you can reach before the 8 others.

## D3. What I should have handed over instead

Not a ranked list. **A list sorted by whether the EXCLUDED-RULED or COVERED side
carries a citable basis** — because that is the property that predicted every
one of my own thirteen flips, and it is checkable without judgement. Score never
predicted a single one of them; the presence of a nameable ruling predicted all
of them.

The handoff README did give the working discriminator (*do neighbouring rows
agree across the two slices*), and that is what `small-measures` used. **The
score column should have been dropped from it rather than led with.**

## D4. And the lexical ceiling, stated with their number

They measured `"Filter: Location"` against `"Filter by Locations"` at **0.595** —
a false pair outscoring the true one. **A lexical matcher cannot tell a
capability from a capability it shares a noun with**, and no threshold repairs
that, because the failure is not in the cutoff but in what is being measured.
Section 6's "lexical, not semantic" limit is that same fact; this is its cost
measured in a real adjudication rather than predicted.

---

# AMENDMENT E — the 19 are CLOSED. All nineteen are false, and the column was blocking a METHOD, not the question.

## E1. The verdict

**19 of 19 are false pairs. `COVERED-PROVEN vs EXCLUDED-RULED` is an artefact of
the matcher, not a third class.** No row moved and none should.

Ten were decidable from a recorded direction — five from the census's own R/W
column, and **five more from `jobs.md`'s ranges table, found while writing
this** (scope Amendment A). Of those ten, **eight are opposite-direction pairs**:

    read notifications        [R]  vs  manage notification settings  [W]
    mark notifications read   [W]  vs  read notifications            [R]
    Who's-Viewed list         [R]  vs  unsubscribe from its emails   [W]
    filter by employment type [R]  vs  edit employment type on a job [W]
    filter by employment type [R]  vs  the OTW employment-type field [W]

**A read and a write of one subject are not one capability, and their states are
supposed to differ.** The two same-direction pairs are false for a different
reason — `see who you blocked` matched `the groups you belong to` and `the Pages
you follow` on the phrase *list of*.

The nine without a recorded direction are false on **capability identity**:
following a company vs **pressing an off-platform Follow widget on someone
else's website** (ruled out under `OFF-PLATFORM-WIDGET`); saved JOBS vs saved
RESUMES; a job-search location filter vs a people-search location filter — the
exact pair `small-measures` measured at 0.595, outscoring a true pair.

## E2. B2's mechanism is RESTORED; its generalisation stays withdrawn

Amendment B2 said this class is mostly read-versus-write. Amendment C withdrew
that **for lack of evidence** — 74% unanswerable. With ten now decidable,
**eight are exactly that shape.**

> **B2's MECHANISM was right. B2's GENERALISATION — asserting it over nineteen
> from ten hand-read — was not, and withdrawing it was still correct.**

The difference is the whole point: C did not withdraw a wrong idea, it withdrew
an unevidenced one. **A mechanism that later turns out true does not
retrospectively justify having asserted it without measurement**, and the
evidence that vindicates it arrived only because the withdrawal sent me looking
for a column instead of arguing from wording.

## E3. And the sharper correction: the column was blocking a METHOD

I reported this class as "84% unanswerable". That was true of answering it **by
direction**. **Answering it by capability identity was always available** —
nine of the nineteen are settled by reading what the two rows describe, and
needed no column at all.

> **"Unanswerable" was a fact about the route I had chosen, not about the
> question.** The missing column blocked the cheap mechanical test; it never
> blocked the expensive manual one, and I did not say so at the time.

**This does not deflate the column's value elsewhere** — a blocker's published
R/W split, a read-only queue, and a boundary cost that turns on direction all
genuinely need it, and `skew-gate` declined a surface on exactly that ground.
It does deflate the urgency I attached to it *for this class*.

## E4. What remains, so the next reader does not re-derive it

**Nothing.** The 19 are adjudicated and closed. The nine that "needed the column"
did not need it; their verdicts rest on capability identity and are recorded
above.

**When the column lands, the only work here is confirmation**, and it is a
lookup: the nine rows are `J89, J90, J88 (x2), J103, J104, J45, J3, J91`, whose
expected directions from their capability text are `W, W, R, R, W, W, R, R, W`.
**If any measured value contradicts that list, the pair is worth re-opening; if
they match, nothing changes.** That is the whole residual obligation.

---

# AMENDMENT F — the SAME-STATE pairs, and why I had been mining the worst subset

## F1. The structural reason my precision was poor

I spent this round on the **different-state** pairs and measured their precision
at ~7-of-15, with `small-measures` finding 1-of-61 in one class. **The
explanation is in the selection, not in the matcher:**

> **A different-state filter selects AGAINST true duplicates**, because two
> slices stating one capability usually agree about it. So the class I was
> mining is the one where a true duplicate is least likely to be, by
> construction.

The same-state class (264 pairs) is where they actually live. Hand-reading its
twelve highest-scoring pairs: `Opt out of saving job-application data` /
`Opt out of saving job application data` (0.987); `Turn Open to Work on / off` /
`Turn Open To Work on or off` (0.972); `Delete a recommendation you sent` /
`Delete a recommendation you have sent` (0.889). **Eleven of twelve are
plainly one capability.**

**This does not rescue the score.** It says the score was being applied to a
population selected against it.

## F2. But the double-count is DELIBERATE, BOUNDED, and already registered

Before treating any of that as an over-count I checked whether the census
intends it. **It does, and it says so.** `messaging-and-content.md` section 10:

> *"Flagged rather than deleted, per the lead's instruction that double-counting
> is preferable to dropping between two agents. **These rows are still counted in
> this file's 142.** If the sibling's slice claims them, subtract exactly the
> rows named here."*

And `network.md` records removing **26 duplicates plus 16 recovery rows** that
belonged to other slices. **So one slice removed its duplicates and another
deliberately kept and registered its own, with a subtraction condition.**

**The denominator is not silently inflated. It carries a documented, conditional
correction that nobody had evaluated.**

## F3. The condition is MET for four of the sixteen

Hand-read against `network.md`'s group and event rows — **not** matched by score,
for the reason in F4:

| flagged row | network twin | condition |
|---|---|---|
| `M C60` Access your LinkedIn Groups | **`N 173`** Access the list of groups you belong to | **MET** — both COVERED-PROVEN |
| `M C61` Join a group | **`N 63`** Join a LinkedIn group | **MET** |
| `M C63` Leave a group | **`N 64`** Leave a LinkedIn group | **MET** |
| `M C69` Invite connections to join a group | **`N 168`** Invite your connections to join a group | **MET** |
| `C62`, `C64`–`C68`, `C91`, `C57`, `C92`, `C59`, `C75` | none | not met — correctly still counted |

**Reported, not executed.** Subtracting rows changes a published denominator and
belongs to the slice owners; what was missing was the factual half, and that is
now measured.

**`C69`/`N168` is closed** (`52b80c7`) — and I had to close it because **my own
flip of `C69` opened it**: I moved the messaging row and left its network twin
GAP, which is the exact failure this round documents.

## F4. A fourth badly-chosen threshold, reported

I first matched the sixteen flagged rows by similarity at a 0.62 bar. It
returned **nine twins of which only three were real** — `"Create a LinkedIn
Event"` matched `"Leave a LinkedIn group"` at **0.67**, and `"Post content in a
group feed"` matched `"Report a post or a comment in your feed"` at 0.63.

**That is the fourth threshold I have picked badly today**, after the feed size
bar, the `fields==11` verdict and the stricter duplicate-id run. The pattern is
consistent enough to state as a rule rather than an apology:

> **The score generates candidates. It must never settle one.** Every true
> finding this round came from an artifact — a ruling id, a code predicate, a
> neighbour that agrees — and none came from a number I chose.

---

# AMENDMENT G — an OPEN QUESTION in the corpus, answered: four of twelve are double-counted

`network.md:1113` carries an open question nobody had answered:

> *"**Whether rows 67-78 are double-counted against `_audit/_census/profile.md`.**
> Both slices map the settings family under the same R11 ruling. Resolving it
> requires comparing this table against that file's 145-row settings walk
> row-by-row, which is a **top-level de-duplication job, not a slice one.**"*

**The answer is YES for four of the twelve**, and the reason it stayed open is
structural rather than anybody's oversight.

## G1. The four

`profile.md`'s `O6-O20` is a **COLLAPSED block — fifteen capabilities stated as
one row** — and its own summary enumerates them. Read against network's table:

| network row | the item inside `P O6-O20` that claims it |
|---|---|
| `N 67` Limit who can follow you to your 1st-degree connections | *"who can follow you"* |
| `N 68` Allow everyone on LinkedIn to follow you | *"who can follow you"* |
| `N 71` Set who can see the members you follow | *"who can see members you follow"* |
| `N 74` Choose whether your connections can see your connections | *"connection-list visibility"* |

**Eight are NOT double-counted** and the distinction is legible: `N69`/`N70`
(primary action on your profile), `N72`/`N73`/`N75` (who may send or follow
invitations), `N77` (appearing in another member's followers list), `N78`
(activity notifications) — **none appears in `O6-O20`'s fifteen**, and `N76` is
not a settings row at all.

## G2. Why it stayed open, and it is a blind spot I had already written down

**A collapsed block is invisible to a lexical matcher.** `profile.md` states
fifteen capabilities in one row, so `"Limit who can follow you to your 1st-degree
connections"` is scored against a fifteen-item summary string and scores
nothing. **My own sweep's stated limits name exactly this** — *"collapsed blocks
dilute against any single matching row"* — and this is that limit costing a real
finding for weeks.

**It was not found by scoring. It was found by reading `O6-O20`'s own list**,
after the open question pointed at the range. The score never surfaced it and
never could.

## G3. NOT EXECUTED, and the reason is the document's own

Unlike `messaging-and-content.md` s10 — which carried a written conditional whose
trigger I measured and then fired — **there is no conditional here.** `profile.md`
and `jobs.md` carry **no reconciliation register at all**; only `messaging` has
one and only `network` recorded removing duplicates at harvest.

And the network note states its own authority: *"a top-level de-duplication job,
not a slice one."* **Subtracting four capabilities from a collapsed block is a
new decision, not the execution of an old one**, and the block's arithmetic
(15 capabilities in 1 row) means the correction is to a stated capability count
rather than to a row.

**So this is reported with the evidence and the four named, for a ruling.** What
was missing was never the authority — it was the measurement, and that part is
now done.
