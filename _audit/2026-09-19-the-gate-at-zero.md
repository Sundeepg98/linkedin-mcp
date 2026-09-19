# The gate at zero: six reds, five repaired, one handed back

Wave `gate-zero`, 2026-09-19. Sole writer, and that was measured at 15:30
before any edit rather than assumed: no `git` processes, no `.git/index.lock`,
and the only python processes in this tree were the two MCP server workers
started at 11:19.

**The brief said six. Six reproduced, in 3.34 seconds, all offline.** Every one
is a text or registry guard; not one needed a browser session, a probe, or a
live surface.

    15:30:49   6 failed   -- exactly the six named in the brief
               5 repaired
               1 REFUSED AND HANDED BACK -- section 5

---

## 1. WHAT EACH RED ACTUALLY ENCODED

Three of the six were not what their headline said, and the brief was right to
flag that its own reading of the last three was untested.

| red | the brief's guess | what it was |
|---|---|---|
| marker reasons | the guard may mis-parse | guard correct; two reasons wrapped at 12 chars |
| untriaged pairs | 8 pairs, one recursive | 8 pairs: 1 real, 7 mentions -- and one defect hiding behind one of them |
| tab-leak ratchet | "may have grown" | ratchet correct; a CORRECT close, misread by a variable name |
| ci timings | "stale, the suite grew" | exactly that -- the only guess that held |
| click commits | no read offered | a live write-path gate, red 14 days. HANDED BACK |
| both rules reject | "the control may have changed" | the control passed; a fifth count pin was missed |

---

## 2. THE TWO MARKER REASONS -- THE GUARD IS NOT MIS-PARSING

**Established before repairing, as instructed.** The parser takes everything
after the LAST backtick on a marker line and compares its length against a
**20-character minimum**. The two reported lines carry:

    :51    "it lists two"    12 characters
    :184   "its boundary"    12 characters

The rest of each reason continues on the next line. The parser reads one line,
**and that is its stated rule** -- its own failure text says a marker must say
in one line what it did.

**IT IS NOT OVER-STRICT, AND THAT IS A MEASUREMENT RATHER THAN AN OPINION.**
The corpus carries **70 markers; 68 clear the bar** -- and several of those
also wrap, at 22, 24 and 25 characters. A 20-character bar is low enough that
any real opening clause clears it. These two broke one clause too early.

**SO THE GUARD WAS NOT TOUCHED. The two lines were RE-WRAPPED**, which is
typesetting rather than padding, and the difference was made checkable instead
of claimed:

    whitespace-normalised text, before vs after:  IDENTICAL

That assertion ran inside the edit and would have aborted it. No word was
added, removed or changed. Only the column where a clause breaks moved.

### A SECOND DEFECT WAS SHELTERING BEHIND THE FIRST

Repairing the reason turned a *different* test red, and this is a real finding
about the guard's own structure:

> **A MALFORMED MARKER IS INVISIBLE TO THE PAIRING RULE.** The parser records
> the malformation and then skips the line, so the declaration never enters the
> map the back-pointer test reads. While the reason was too short, the
> declaration could not be checked at all.

The marker at :184 declares a real correction whose target carried **no
back-pointer whatsoever**. Fourteen days of a declared correction that a reader
starting from the claim could not follow -- which is the exact defect that file
exists to catch, sheltering inside a second defect on the same line. The
back-pointer is now written.

---

## 3. THE EIGHT PAIRS: ONE REAL, SEVEN MENTIONS

Each was read at its line before triage, and for each I recorded **which
vocabulary word fired and where** rather than deciding from the pair alone.

**THE ONE REAL ONE IS DECLARED WITH A MARKER PAIR, NOT TRIAGED.** A section
headed *"A COUNT CORRECTION IN A DOCUMENT FROM EARLIER TODAY"* names a
sibling's section 4 as stating twenty-one remaining rows and then tabling seven
buckets that sum to twenty-two. The forward marker sits in the corrector; the
back-pointer sits **under the heading of the corrected section**, not at the
top of the file, because a reader arriving from a citation lands at the section
and never sees a file header.

**THE SEVEN MENTIONS FALL INTO EXACTLY THREE SHAPES.**

**(a) THE RECURSIVE ONE -- three pairs.** A wave's write-up carries a table of
test failures it observed and attributed elsewhere; its columns are `failure`
and `whose`. The vocabulary is not a verb about the cited documents. It is the
word *correction* **inside a test's own name**, quoted verbatim in the failure
column.

> **The guard cannot distinguish "X corrects Y" from "X reports that a test
> whose name contains _correction_ fired on Y."** The brief predicted this
> shape; it is here three times.

**(b) A SUBSTRING OF AN UNRELATED WORD -- two pairs.** `stale` matched inside
**`staleness`**. The phrase is *"all four are the staleness diagnostic"* -- the
name of a field in a tool's payload. One substring, in a 4.7k-character census
cell, pulled in **both** citations on that line.

**(c) VOCABULARY BELONGING TO A THIRD PARTY -- two pairs.** One is a provenance
note recording which commit-state of a document was ruled against, naming the
commits at which **its own author** repaired it; naming where a document was
fixed is the opposite of claiming it is broken. The other is an evidence
pointer whose window happens to contain a parenthetical about a self-correction
**inside a third document**, plus a neighbouring row that corrects **a census
row, not a document**.

**Ratio: 1 real in 8.** That file's own header documents 26 of 27 as mentions
and argues from the ratio that the vocabulary alone cannot be the check. This
pass reproduces the argument on a fresh sample.

---

## 4. THE RATCHET DID NOT MOVE, AND NOTHING WAS LEAKING

**A ratchet bumped to go green has stopped being a ratchet**, so the first
question was which script was new. Answered with the ADDING commit
(`--diff-filter=A`) rather than the last-touched one -- a different query that
would have named seven innocent files:

    leakers added since the ratchet was set:  exactly one, 022b0ce, 11:32 today

Then the refuting query, which is the one that mattered: **does that script
actually leak?**

**IT DOES NOT.** It closes its tab in a `finally`, with the right comment --
*"THE PAGE, NEVER THE CONTEXT"* -- and it holds the page in a variable outside
the `async with` so the `finally` reaches it on the abort paths too. That is
*better* than closing inside the block, not worse.

**The detector names its receiver** -- `page`, `tab`, `_own_page` -- and the
comment above it says why: *".close() alone matches a file handle, and did."*
This script spelled its holder `page_ref`, which is not on that list.

> **A correct close spelled with an unsanctioned name reads as a leak.** The
> count stood at 40 because of a variable name.

**REPAIRED BY RENAME; THE RATCHET WAS LEFT AT 39, UNTOUCHED.** `_own_page` is a
name the detector already sanctions and four sibling probes already use, so
there was a convention to join rather than a guard to widen. **The detector was
deliberately NOT widened**: its narrow receiver list is the design, and
admitting one more spelling is how a guard that catches file handles stops
catching them.

**AND THE COUNT MUST NOT BE READ AS A FIX.** 40 -> 39 here is a rename. No tab
that was leaking stopped leaking. The other 39 still leak, and each still
belongs to its own wave.

---

## 5. THE ONE I REFUSED, AND IT IS A LIVE WRITE-PATH GATE

`test_a_click_that_does_commit_reaches_the_body_and_the_send` **is not repaired
and is handed back.** It encodes a ruling, and the brief's stop condition is
written for exactly this.

### WHAT IT IS

It is the **positive control for a file full of refusals.** Its own docstring:
*"A file full of refusals passes perfectly against a `perform` that refuses
unconditionally. This is the test that fails if the flow stops working."*
**While it is red, every refusal assertion in that file is uncertified.**

The tool behind it is on the surface, live, and **performs** -- the one tool in
this package that reaches another human being.

### WHEN IT WENT RED -- MEASURED, NOT INFERRED

The single test, run in two detached worktrees across the one commit that could
have done it:

    90e9716   the parent                       1 passed
    9503723   word-bounded recipient gate      1 failed

**Red since 2026-09-05 19:16 -- fourteen days.** The commit that tightened a
safety gate broke that gate's own positive control and shipped, and nobody saw
it because every wave ran the files it was editing. **That is the failure this
campaign root-caused today, with a fourteen-day-old instance still in the
tree.**

### THE MECHANISM -- MEASURED WITH THE SHIPPED MATCHER

The shipped in-page matcher was **imported, never reimplemented**, and run over
four candidate chip labels in headless chromium on synthetic markup. Nothing
reached LinkedIn; no CDP, no profile, no probe.

    Remove Quillfeather Nimblewick1st            matches=0   REFUSES
    Remove Quillfeather Nimblewick 1st           matches=1   proceeds
    Remove Quillfeather Nimblewick               matches=1   proceeds
    Remove ...Nimblewick 1st degree Staff ...    matches=1   proceeds

**The matcher refuses exactly one shape: the one where the degree badge runs
into the name with no separator.** The test's double builds precisely that
shape -- it sets the chip's accessible name from the suggestion row's *whole*
text, and the row is drawn as two adjacent spans with nothing between them.

Note the fourth line: **the measured live row shape proceeds.** The tightening
did not close the surface. It closed one spelling.

### WHY I WILL NOT REPAIR IT

**The separator is an open question that the same file names as open.** Its own
row helper is commented *"THE SEPARATOR IS THE VARIABLE UNDER TEST"* and
*"WHICH ONE LINKEDIN DRAWS HAS NEVER BEEN READ, and cannot be read the obvious
way: the accessible names on that listbox belong to other people."* The gate's
docstring adds that **no chip has ever been observed.**

So the double picked one side of a question the file says is unanswered, and
**turning the control green means picking the other side.** Both are guesses
about an unobserved surface, and the guess decides whether a gate on an
irreversible message to a named person proceeds.

The gate's own docstring has already ruled on the direction:

> *"IT MAY NOW REFUSE A LEGITIMATE RECIPIENT. That is the ruling and not a
> regression... too strict costs a retry, too loose commits a stranger to an
> irreversible message under his name."*

**A change that makes it proceed is a change to that ruling, and the ruling is
not mine.** Loosening the matcher is refused outright: it was tightened on a
measurement showing a bare substring test letting a stranger through in two
ways.

### WHAT I RECOMMEND, FOR WHOEVER RULES

**Do not pick a side. Run the control over BOTH shapes and assert the verdict
is shape-determined** -- run-together refuses with the needle-mismatch
condition, separated proceeds to body and send. That restores the
pipeline-is-alive claim on the shape that can proceed, **pins the run-together
refusal as a finding instead of hiding it**, and answers neither half of the
open question. The double's option helper gains the separator parameter its
own sibling already has. The matcher is untouched.

### THE COST OF THIS STOP, MEASURED

**It strands nobody.** The hook runs a staged test file plus the files COUPLED
to it. That computation was run rather than assumed:

    tests/test_navigation_is_never_derived.py     7 coupled   reds among them: NONE
    tests/test_no_committed_identity.py          18 coupled   reds among them: NONE

**None of the six reds is coupled to either held file.** The cost of leaving
this one red is that the tree is one red instead of zero. No finished work by
any wave is held behind it.

---

## 6. THE FIFTH COUNT PIN, AND WHY A SWEEP MISSED IT

The test whose name begins *both rules reject* is a control, and **the control
passed.** Both rules ran green over the defective registry reading first. What
failed was a tool-count assertion at the bottom of the same function.

**Measured off the registry on this tree, not relayed from the commit that
moved the other sites:** 44, with both of today's new read tools present. The
surface moved, so the pin was behind -- a legitimate ratchet move, bumped with
the two tools that moved it named, which is that file's own standing
requirement.

An earlier commit moved four sites under a message reading *"the pin was the
LAST site to move."* It was not. This was the fifth.

> **A count pinned in two files is two pins.** A sweep that greps for the
> NUMBER finds every site spelled in digits. A sweep that greps for the test
> NAME finds only its own file. The second is what happened.

Re-checked rather than assumed: with the pin standing at 42 against a real 44,
the test failed **there and nowhere else**, so the demonstration above it --
which compares a two-entry reading by content -- cannot reach the number.

---

## 7. THE TIMINGS TABLE -- REGENERATED, NOT RE-THRESHOLDED

The one red the brief guessed right. The table was measured on 2026-09-05 and
the suite has grown 66 files since, so it priced 92 of 158 -- below the
two-thirds line.

**THE THRESHOLD WAS NOT TOUCHED.** Two thirds is the line the file argues for,
and lowering a coverage bar to match a table nobody regenerated is the table's
problem wearing the test's name.

    92 files / 3660 tests / 1647.6s   ->   157 files / 5736 tests / 946.1s

Regenerated by the recipe the module documents, from a full serial run on a
**detached worktree** -- single-writer by construction, which is the only
honest place to take a whole-tree measurement while a neighbour's uncommitted
work sits in the main tree.

**THE PROVENANCE LINE SAYS THE BOX WAS NOT QUIET.** Short foreground batches
overlapped parts of the run, so individual seconds are slightly inflated and
the label records that rather than implying a clean room. Tolerable here for
the reason the module states: membership comes from live collection every time
and only WEIGHT comes from this file, so a skewed table can unbalance a shard
and cannot lose a test.

---

## 8. THAT RUN IS ALSO AN INDEPENDENT READING OF THE BRIEF'S NUMBER

Taken before any of my edits landed, on a clean worktree with **none** of the
working tree's untracked files and **none** of the neighbour's uncommitted
changes:

    6 failed, 5636 passed, 11 skipped, 1 xfailed in 958.89s (15:58)
    FAILED lines counted: 6   summary line: 6   -- capture complete
    and they are EXACTLY the six the brief named

**The brief's reading reproduces on a tree that shares none of its
contamination.** The working-tree run at 15:13 read 6 with the neighbour's
uncommitted work present; this one reads 6 without it. So that work is neither
causing nor masking a red, which is worth knowing before anyone decides what to
do with it.

The passed counts differ -- 5723 against 5636 -- and the reason is structural,
not a discrepancy: a worktree checkout has no untracked files, and one of the
working tree's untracked files is a TEST FILE (section 9).

---

## 9. THREE THINGS IN THE TREE THAT WERE NOT IN THE BRIEF

**None of these was repaired by me. Each is somebody's ruling.**

### (a) THE RULED-UNLANDED GROUPS ADMISSION IS SITTING APPLIED IN THE TREE

`linkedin_server/readonly.py` plus two of its test files are MODIFIED and
uncommitted -- **185 insertions, last written 14:01-14:05** -- and the added
lines are the groups boundary work: the `[0-9]` alphabet argument, the member
roster, the closed-segment reasoning. It is a **subset** of the saved recovery
patch, 259 diff lines against that patch's 676.

**The ruling is that this does not land.** It is currently one `git add -A` or
one `git commit -a` away from landing anyway. Both are already banned by house
rule, which is the only thing standing between the ruling and its opposite.

I did not touch it, did not stage it, and used `--only` on named paths for
every commit so that nothing could sweep it in. **Flagging it rather than
resolving it: whether it is reverted, left, or landed is the lead's call, and
"it was uncommitted so I tidied it" is how a ruling gets undone by helpfulness.**

### (b) THREE OF THE FOUR RECOVERY PATCHES ARE NOW OBSOLETE

The patch convention was instituted this afternoon so the index would not be
the only copy of three stranded repairs. **All three have since landed**, and
each patch's target names the commit that carries it:

    _RECOVER_arity_message.patch        -> landed 889f488, 14:42
    _RECOVER_declaration_REGIONS.patch  -> landed 4cc53f9, 14:38
    _RECOVER_taint_fix.patch            -> landed db453e7, 14:27
    _RECOVER_groups_admission.patch     -> NOT landed, and ruled not to

**They are not free to leave lying there.** Untracked tree-root files are
swept, and one member of this family already forced a safety guard to be
narrowed this afternoon when a diff-added decorator line read as an email
address. Three stale copies of landed work keep paying that cost for nothing.

**I did not delete them.** They are another wave's safety copies under a
convention the lead instituted, and deleting them is ten seconds for whoever
owns that convention and an unreviewable act for me.

### (c) A TEST FILE IS UNTRACKED, SO IT IS IN NOBODY'S CLONE

`tests/test_the_groups_id_segment_is_closed.py` is untracked. It runs in this
working tree and **in no clone, no worktree and no CI checkout** -- which is
precisely the local-passes/clone-fails divergence that the correction guard's
own corpus rule was rewritten to eliminate, reappearing one directory over.
It is the control for the groups admission, so it is untracked for a coherent
reason; it is still a test whose verdict depends on which tree it runs in.

---

## 10. THE FINAL NUMBER

**Taken on a detached worktree at `66e2038` -- single-writer by construction,
and zero commits landed across the window, which is checked rather than
asserted: the last commit was `66e2038` at 15:57:46, and `git log` over
15:58:00-16:15:00 returns nothing.**

    WINDOW      15:58:13 - 16:14:18 by the box, 962.91s (16:02)
    RESULT      1 failed, 5641 passed, 11 skipped, 1 xfailed
    CAPTURE     FAILED lines counted: 1    summary line: 1    -- complete
    THE ONE     test_a_click_that_does_commit_reaches_the_body_and_the_send

    COMMITS     5   (four repairs + this document)
    ATTRIBUTION 0   across all 437 unpushed commits, swept for five patterns:
                    the co-author trailer, the session trailer, the
                    "Generated with" line, the session-link host, and the
                    tool's noreply address

**Six to one.** The one remaining is the write-path gate of section 5, left red
deliberately, with the repair specified and the ruling left to whoever owns it.

**THAT NUMBER IS FOR THE FOUR REPAIR COMMITS, NOT FOR THE TREE THIS DOCUMENT
LANDS IN, AND THE DIFFERENCE IS NOT PEDANTRY.** This file enters a corpus that
several guards scan, and it demonstrably CAN move one of them -- it tripped the
identity sweep while still a draft (section 11). So the gate is re-measured at
the commit that carries it, and the second number is appended below. Reporting
the pre-document run as the state of the tree would be the subset-as-the-gate
failure this campaign spent the day root-causing, in its politest form.

### AND THE COUNT IS NOT THE CLAIM -- HERE IS WHAT THE FIVE ACTUALLY COST

**Two of the five were not repairs to the thing that was red.**

    marker reasons    a RE-WRAP; the guard was right and was not touched
    tab ratchet       a RENAME; nothing was leaking and the ratchet held at 39
    triage            7 mentions recorded, 1 real correction declared
    the pin           a real ratchet move, with the two tools that moved it
    the timings       a real regeneration, from a real run

**Only two of the five moved a number, and both moved because the thing they
count had genuinely moved.** Nothing was bumped to go green, no guard was
loosened, and no threshold was lowered. Where a guard looked wrong it was
measured first and turned out to be right twice -- which is the result that
would have been hardest to notice if the goal had been the count.

---

## 11. METHOD, AND THE TWO PLACES IT CHANGED THE ANSWER

**RUN THE QUERY THAT WOULD REFUTE THE PREMISE.** The brief said so and it paid
twice, both times against my own working hypothesis:

* "A leaker was added" -> **the script does not leak.** The refuting query was
  *does it close?*, not *is it new?*, and asking the second alone would have
  produced a correct-looking repair to correct code.
* "The guard may mis-parse" -> **the guard is right**, and 68 of 70 markers in
  the corpus prove the rule is workable rather than pedantic.

**A SCAN THAT CANNOT SEE THE FILE CANNOT CLEAR IT.** My first check of this
document against the correction guard passed while the document was untracked
-- and the corpus is tracked-only BY DESIGN, so that pass was vacuous and said
nothing. Re-run with the file staged into a PRIVATE index, the corpus reads 130
documents including this one, and the green means something. **The shared index
was never touched**, which is the same mechanism the house rule prescribes for
committing a new file, used one step earlier as an instrument.

**IMPORT THE SHIPPED MATCHER, DO NOT REWRITE IT.** The chip-shape measurement
in section 5 runs the package's own in-page comparator against four labels. A
reimplementation would have been a second instrument to debug, and the finding
turns entirely on one character of its boundary rule.

### AND THE IDENTITY SWEEP CAUGHT THIS DOCUMENT, WHICH IS WORTH WRITING DOWN

Running the corpus guards against the staged draft was not a formality. **The
exact-value identity sweep returned a HIT on this file.** An earlier draft of
section 10 listed the five attribution patterns as literal strings, and two of
them -- a host and a noreply address -- are real entries in the operator's own
identity corpus.

> **I put two identity strings into a tracked document while writing the
> paragraph that certifies this tree carries none.**

Repaired by **naming the patterns instead of quoting them**, which is the
rename-before-declare order this repository already uses on that guard and
costs the sentence nothing: the sweep still ran over the literals, and a report
does not need to reproduce them to say so. Re-measured after: **PASS, 0 hits
across 475 swept files.**

**AND THE CONTROL IS WHAT MADE IT ATTRIBUTABLE.** Three guards went red on the
staged draft, and the obvious reading -- all three are mine -- was wrong. A
private index that was a PURE COPY, with this document NOT added, was run
against the same guard: it PASSED. So exactly one of the three belonged to this
file, and the other two are a subset-ordering effect that does not reproduce in
a full-suite run. **Without that control I would have repaired two things that
were not broken**, which is the same shape as section 4.

**MEASURE THE COST OF A STOP BEFORE CHOOSING IT.** Before refusing the sixth I
computed the hook's coupled sets for both files the fleet is waiting on. Had a
red been coupled to either, the calculus changes and the refusal would have
needed to go up immediately rather than in a write-up.

**AND THE TRAILING-COMMAND TRAP FIRED AGAIN, ON ME.** The harness reported the
certifying run as *exit code 0*. The run exited **1** -- pytest's code for a
failing suite -- and the chain ended in a `tail`, so the shell returned the
tail's status. **The artifact was verified instead of the exit code and the
discrepancy was visible immediately**, which is the standing rule in this repo
doing exactly the job it was written for. Anyone reading an exit code from a
chain in this session should assume it belongs to the last command in it.
