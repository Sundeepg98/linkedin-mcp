# Reds triage, 2026-09-05 -- sorting the queue before clearing it

Wave: `reds-triage`. Brief: the full suite reports 9 failures across two
independent readings taken on a moving tree (4827 passed / 9 failed, 16m27s;
4758 passed / 9 failed, 16m46s). Establish which are real, sort by what each
assertion is ABOUT, and clear only what may honestly be cleared.

**Nothing was pushed.**

## THE HEADLINE: a clean clone says THREE, not nine

    3 failed, 4864 passed, 11 skipped, 1 xfailed   in 1678.56s (27:58)
    clone of 693f488, git clone --no-hardlinks, run serially

**Six of the nine did not exist.** They are the moving-tree class that
over-reported this repo's red count by 150% earlier today -- ten failures where
a clean clone showed four. Not one of the three survivors is a defect in
product code, and **not one of them may be cleared by this wave.** All three are
guards refusing correctly, each owed by a wave that is not this one.

**Zero reds cleared. Three left standing on purpose. Six dissolved as phantoms.**

That is the whole result, and the count is the least interesting part of it:
a queue of nine that is really a queue of three, none of which is a bug, is a
queue whose main cost was the six hours somebody could have spent chasing it.

## Method, and why it runs in this order

Three instruments, in a fixed order, because the cheapest one disqualifies the
most candidates:

1. **Targeted run first.** A failure that PASSES when its own file is run alone,
   in a tree with live writers, is a phantom until a clone says otherwise. It
   costs seconds. Two of the three survivors were confirmed real this way in
   39 seconds, before any clone finished.
2. **A clean clone is the authority.** Run with the shared venv's interpreter
   from the clone's own working directory. **Verified rather than assumed:** the
   clone's own package is the one imported, checked by printing
   `linkedin_server.__file__` and reading the path back. A clone gate that
   imports the shared tree is the shared tree wearing a clone's costume.
3. **A second, concurrent shared-tree run**, kept only as a comparison -- never
   as the authority.

### The tree did not stay quiet, and the reading is dated by the TREE

It was quiet at 23:17 by the box: four untracked files, no modified tracked
file. By 23:27 HEAD had moved from `693f488` to `d5f6409`,
`linkedin_server/readonly.py` carried 52 uncommitted lines from a live writer,
and three more untracked scripts had appeared.

So the authority reading is dated by its tree and not by "HEAD": it is the clone
of `693f488`. The commit that landed underneath it touched two census TSV files
and two scripts, and **neither script opens a browser session** -- checked, not
assumed, because the tab guard scans that directory. It therefore cannot reach
any red classified here. Stated so the gap is visible rather than glossed.

**And the untracked files matter to exactly one of these guards.** The tab guard
globs `scripts/*.py` off the working tree, so an untracked probe would inflate
it in the shared tree and vanish in the clone -- a phantom by construction. It
was measured instead of assumed: all 41 counted leakers are tracked, and the
four shared-tree-only scripts open no session. The two trees agree at 41.

## Classification table

| # | test | what the assertion is ABOUT | class | disposition |
|---|---|---|---|---|
| 1 | `test_a_person_name_is_never_a_literal::test_every_person_constant_holds_a_declared_invented_name` | a person-carrying constant that is not on the declared-invented table | **guard correctly refusing on an UNDECLARED value** | **LEFT RED.** Owner `fc10b99`. Precedent `a5a988a`. |
| 2 | `test_a_probe_closes_its_own_tab::test_the_tab_leak_only_ever_shrinks` | a ratchet on how many session-opening scripts never close their tab | **ratchet correctly refusing: one genuine new leak** | **LEFT RED.** Real leak owed by `ae469cc`. Pin defect quantified below. |
| 3 | `test_click_is_not_its_own_evidence::test_a_click_that_does_commit_reaches_the_body_and_the_send` | the positive path through the recipient gate on `send_message` | **guard correctly refusing after a deliberate fail-closed ruling** | **LEFT RED.** Owed by `9503723`. |
| 4-9 | six failures present in both 9-failure readings | -- | **PHANTOM, moving tree** | Dissolved by the clone. |

## The three, one at a time, with the reason each stays

### 1. The undeclared needle -- and a wave already refused to clear it

The guard prints its own remedy: *"If it is invented, add it to the table --
that edit is the check."* The offending value is the module-level `NEEDLE`
constant at `tests/test_recommendation_tally.py:71`. It is not spelled here on
purpose: a synthetic value that is already tracked in one place does not need a
second home, and this document is not that home.

**It is UNDECLARED, not real.** Corroborated independently of the guard: the
shipped exact-value sweep passes over the whole tree --

    scripts/sweep_tracked_for_identity.py -> PASS: 0 hits across 381 swept files

so the red is about a missing declaration and nothing else. That is this repo's
standing law -- a red identity guard proves a value is UNDECLARED and never that
it is REAL -- holding for the fourth time today.

**Why this wave does not declare it.** The owner is `fc10b99`, established by
ordering rather than by name. And a wave has already been here: `a5a988a`
declared its OWN needle in the same table, named this one as belonging to
`fc10b99`, and left it red deliberately, writing *"Declaring somebody else's
needle would be adopting their disclosure, not helping them."* That is the
correct call and clearing it now would overturn a ruling on no new evidence.

**The edit is one line and it is not mine to make.** The guard has been red since
19:15:46, which is roughly two hours before the wave that documented it existed.

### 2. The tab ratchet -- the guard caught exactly one real leak, and the pin over-counts

**Do not widen the pattern.** `CLOSES_PAGE` names three receiver names
(`page`, `tab`, `_own_page`); seven tracked scripts close their page correctly
using a fourth, `page_ref`, and every one is counted as a leaker. Widening a
shared accept-pattern to clear a red is how a guard dies -- and this pattern is
deliberately receiver-named because a bare `.close()` matched a file handle once
and did.

The number is separable, and separating it is the finding. Measured by
re-deriving the leaker set at the pin's own commit and at HEAD:

| tree | counted leakers | of which close via `page_ref` | REAL leaks |
|---|---|---|---|
| `002a9dd` (where the pin was set to 39) | 39 | 6 | **33** |
| HEAD | 41 | 7 | **34** |

    added to the counted set since the pin:
      _probe_contact_info_panel.py    closes via page_ref   -- MISCOUNTED
      _probe_premium_entitlement.py   no close() at all     -- A REAL LEAK

**So the ratchet fired for a real reason.** One genuine new leak entered the
corpus, owed by `ae469cc`; the remedy is a `finally` that closes the PAGE, never
the context. The other `+1` is the pin's own defect, and **that defect predates
the pin** -- 6 of the original 39 were already miscounted, so the pin has never
measured the quantity its docstring names. It counts scripts the pattern cannot
see closing, which is not the same set as scripts that leak.

**Why it cannot be cleared here, stated as arithmetic rather than as reluctance:**
fixing the one real leak takes the counted set to 40, which is still above 39.
The red therefore clears only by widening the pattern (forbidden) or by renaming
a variable in up to seven other waves' scripts (not this wave's artifacts).
There is no third option, so the honest outcome is the report.

### 3. The recipient gate refusing the positive path -- a ruling, not a regression

`9503723` made `dom.SELECTED_RECIPIENT_JS` require a WORD-BOUNDED match, and
counted digits as word characters **deliberately**, in its author's words so that
*"a label running a name onto a connection degree must refuse rather than
match."*

The fixture in the failing test builds its chip label as `Remove ` plus the
option row's `textContent`, and that row is name and degree run together with no
separator -- so the needle is followed immediately by a digit and the gate
refuses with `3_needle_does_not_match`. **The guard is doing precisely what its
author designed it to do, on precisely the shape he named.**

The commit says so itself, before this red existed:

> IT MAY REFUSE A LEGITIMATE RECIPIENT ON A REAL CHIP. That is the ruling, not a
> regression. [...] too strict costs a retry, too loose commits a stranger to an
> irreversible message under his name.

**What actually went wrong is coverage, not judgement.** That commit reports
*"27 passed across this file and tests/test_send_message_gate.py"* -- two files.
A third file exercises the same gate through `perform`, and it was not run. This
is the enumeration class the freeze document already names: a targeted run
clears SHAPE violations and never ENUMERATION violations, and the wave had no
way to see a caller it did not know about.

**Why it stays red.** `send_message` is one of the five irreversible writes.
Clearing this red means either loosening a fail-closed gate on that surface, or
rewriting another wave's positive-path fixture to model a chip label **nobody has
observed** -- the same commit states plainly that no chip has ever been read.
Both are rulings for the gate's owner. A triage wave does not get to make either
one by editing a fixture until the suite turns green.

## The two the brief asked about that are NOT red, and the measurements that say so

**The strict xfail has NOT outlived its defect.** The clone reports `1 xfailed`,
and a targeted run shows the same. `test_a_run_that_pressed_no_send_should_report_not_performed`
is still failing for its recorded reason, so the marker is still correct and
`strict` has not converted an XPASS into a failure. **Nothing to do, and removing
the marker would be wrong.** It remains the tripwire it was built to be: the day
`performed` stops reporting `"unknown"` where `False` is certain, this test
XPASSes and the suite goes red.

**The order-dependent login red did not reproduce.** `test_server_surface::test_both_login_names_are_registered_and_the_old_one_forwards`
was predicted verbatim by the freeze document as *"a red belonging to nobody who
ran it"*, with two readings disagreeing about which order breaks it. Measured at
this tree:

| run | result |
|---|---|
| the test alone | 1 passed |
| its own module alone | 50 passed |
| `test_events_home_reader` + the inventory guard + `test_server_surface` | 75 passed |
| `test_events_home_reader` + `test_server_surface` | 69 passed |
| the inventory guard + `test_server_surface` | 56 passed |
| **the full suite, clean clone, serial** | **passed** |

**Neither documented order reproduces it, and the full serial clone does not
either.** So the direction is not settled by preferring one report over the
other -- both are now refuted at this tree, which is a different and better
outcome than picking a winner. The standing hypothesis in the freeze document
(that importing `linkedin_server.events` early changes package import order)
is untouched by this: it was checked for the obvious mechanism and there is no
`importlib.reload` of `server` anywhere in `tests/`, so that particular
explanation is not the one.

**What this does NOT establish.** A test that passes in one full-suite ordering
is not a test shown to be order-independent; it is one sample. The suite has no
`pytest-randomly`, so serial collection order is stable and this reading will
reproduce -- which is exactly why it says nothing about the sharded or
xdist-distributed orders CI will use. Recorded as an open item, not as a fix.

## The six phantoms, and the one thing worth carrying from them

They are not enumerated by name because the readings that produced them were
taken on a tree that has since moved, and naming a phantom from a stale run
would be recording a reading as a fact -- the exact error this document exists
to sort out. What is worth carrying is the ratio:

    reported on a moving tree      9
    real, in a clean clone         3
    over-report                    200%

The earlier instance today ran at 150%. **This is worse, and both are the same
mechanism:** pytest imports from the working tree, so a suite reading in a tree
with live writers is a statement about a tree that existed for part of the run
and nowhere afterwards. The remedy is not care. It is a clone, and the clone
must be shown importing itself.

## Instruments

**A leaker-set differ** (used for section 2, not yet harvested): re-derives the
tab guard's counted set at any two revisions straight out of `git show`, splits
the counted leakers from the REAL ones by looking for a close under any receiver
name, and diffs the two sets. It is what turns *"41, up from 39"* into *"one
genuine new leak, one miscount, and a pin that has never measured what it
names"*. Its value is that it reads the corpus at a REVISION rather than off the
working tree, so it cannot be fooled by an untracked file -- which is the
failure mode that produced six of the nine reds above.

**The control that matters for any clone gate**, and it is one line: print
`linkedin_server.__file__` from inside the clone before trusting a single number
it reports.
