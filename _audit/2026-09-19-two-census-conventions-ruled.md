# Two census conventions, ruled

Both were surfaced by `settings-tail`'s cross-slice wave, both were **routed
rather than taken** because a census-wide convention has an owner, and both are
the lead's to give: they are reversible, non-outward-facing, and change no act
against any person.

---

## 1. A RULING IS CITED BY ITS SYMBOL, UNDER ONE CANONICAL ID

### The measurement

One sentence -- `server.py`, in `linkedin_update_setting`, *"is admitted by name
or not at all"* -- appears in the census under **three names**:

| slice | appears as | citable? |
|---|---|---|
| `network.md` | **R11**, with scope and a 21-row list | yes |
| `messaging-and-content.md` | **MESSAGING-SETTINGS (3.10)** | yes, but a *different* id |
| `profile.md` | bare prose, **"settings family"**, 7 rows | **no** |

**A ruling that is RE-DERIVED rather than CITED cannot propagate, because there
is nothing to search for.** That is the mechanism under the whole cross-slice
disagreement class -- not merely that one slice omits citations, but that the
same rule wears three identities, so even a diligent reader of two of them
cannot know they are one.

### The case that proves it, and it is recursive

`M M42`'s note records it was re-filed on 2026-09-05, *"NOT a new decision -- the
operator already made it and **two census slices applied it differently**"*.

**And that wave left its own twin `N 170` GAP for two weeks.** The disease
recurred inside its own cure.

The wave reporting this then added the fourth instance against itself: it had
quoted that same sentence the same day, **having read R11 in the same session**.
**Four encounters before anybody joined them.**

### RULED

**Every ruling has ONE canonical id, and every citation of it resolves to the
SYMBOL, never to a line number and never to a re-derived phrase.**

    canonical    server.py::linkedin_update_setting
    aliases      R11  ·  MESSAGING-SETTINGS (3.10)  ·  "settings family"

* The symbol, because **the line has already drifted** -- this repo measured six
  retirements citing `server.py:6476-6484`, a range that is now a different
  function, and a reader who opens it finds a plausible unrelated answer rather
  than an error.
* **Aliases are kept, not deleted.** They are how existing readers find the rule,
  and deleting them would strand every document that uses one. They are
  *mapped*, and the map is the artifact.
* **A bare prose reason is not a citation** and may not carry a verdict alone. A
  row whose only basis is `settings family` is a row whose basis cannot be
  checked. Those seven get the canonical id or they get re-adjudicated.

**This does not invalidate a single existing verdict.** A prose ruling is still a
ruling. It becomes *propagatable*, which is the property it was missing.

### What would reopen it

A measured case where a rule genuinely has no symbol to anchor on -- an operator
ruling with no code behind it, of which this census has **225**. Those need a
canonical id of their own form, and that is a second pass, not this one.

---

## 2. A CONTAINER'S EXCLUSION PROPAGATES TO ITS CONTENTS ONLY WHEN THE
##    EXCLUSION IS UNREACHABILITY

### The question

`P I12` is the career-interests **page**, EXCLUDED-RULED because *zero of 237
urls reach one*. `J99` is a **control on that page**, still GAP. They score high
against each other and share a distinctive token, and they are **not the same
capability**.

The wave declined to flip it, correctly: *"whether a ruled-out container rules
out its contents is unanswered, and the OTW editor is the standing
counterexample."*

### RULED -- it depends on WHY the container was excluded, and the two cases
### point opposite ways

**UNREACHABILITY PROPAGATES.** If the container is excluded because nothing can
reach it, then nothing can reach a control *on* it either. You cannot press a
button on a page you cannot load. `P I12` -> `J99` is this case: zero of 237
urls reach the page, so the control inherits the exclusion, and `J99` may be
filed EXCLUDED-RULED **citing the container's measurement, not re-deriving it**.

**A RULING ABOUT THE CONTAINER'S OWN ACT DOES NOT PROPAGATE.** If a container is
excluded because publishing it, or writing to it, was ruled out, that says
nothing about READING its contents. The OTW editor is the standing
counterexample and it stays: reading the state is built, writing it is ruled
out, **and the states are SUPPOSED to differ.**

**The test, in one line: does the container's exclusion make the content
UNREACHABLE, or merely UNWANTED?** Unreachable propagates. Unwanted does not.

**Either way the content row must CITE the container's row**, so the dependency
is visible and a reopener on the container reaches the content. An inherited
exclusion with no pointer is how a container reopening silently leaves its
contents wrongly closed.

### What would reopen it

A container measured unreachable that nonetheless has a reachable content --
which would mean the unreachability measurement was incomplete rather than that
this rule is wrong.

---

## A THIRD RELATION, NOT A DISAGREEMENT AND NOT RULED HERE

**Read vs write of one subject.** The `COVERED-PROVEN` vs `EXCLUDED-RULED` class
is mostly this, and **those states are supposed to differ** -- reading a setting
is built, writing it is ruled out. Nothing to reconcile.

**The bound on that reading is stated by the wave that made it, against itself:**
its R/W extractor returned **74% unknown**, because the column sits at a
different index per slice, so the automated check *"mostly measured my own
parser"*. The conclusion rests on hand-inspecting ten of nineteen and is
reported as such.

**That is the third instrument this round defeated by a positional assumption**
-- a provenance reader that read the wrong column, a retirement guard whose row
pattern saw one id family of two, and now this. **Parse the structure; never
index into it.**


---

## 3. A CLASS FILTER THAT CATCHES AN ADDRESS INCIDENTALLY IS A BLOCKER,
##    NOT A DECISION

Added 2026-09-19 11:14, on a request from `small-measures`, which declined to
bank eight rows and asked rather than stretched.

### The measurement

`FORBIDDEN-CLASS-FIX-LANDED`, 8 rows, cost 0. Machine-verified:

    /public-profile/settings    is_read_url False    caught by "settings"
    /uas/login                  is_read_url False    caught by "/uas/"
    /badges/profile/create      is_read_url False    caught by "/create"

So the addresses are genuinely refused. **The question is whether being refused
by a filter written for a CLASS amounts to a RULING on the CAPABILITY.**

### RULED: NO. THEY STAY GAP, WITH THE BLOCKER NAMED PRECISELY.

A denylist substring written to stop a class of addresses is **a general
mechanism that happens to catch this one.** Nobody weighed this capability;
nobody decided it was out of scope. The prior wave recorded exactly that at
ledger L118-123 -- *"a GAP with a NAMED BLOCKER, not laundered into a
decision"* -- and that reasoning stands.

**The requesting wave reached the same answer from its own prior work, in the
opposite direction, which is what makes this a convention rather than a
one-off.** It banked `M C62` this morning **because** `delete_or_withdraw_
anything` names the **ACT**, and it called the url match the weak half. Here no
rule names the capability and only a class filter catches an address
incidentally. **Banking these would have contradicted its own reasoning from
four hours earlier.** Consistency with your own morning is a better test than
consistency with a ledger.

### THE GENERAL FORM

    a rule that names the ACT            ->  EXCLUDED-RULED
    a filter that catches the ADDRESS    ->  GAP, blocker named
    an address measured UNREACHABLE      ->  see section 2

**The three are different states and the difference is WHO DECIDED WHAT.** A
rule about an act is a decision about the capability. A filter about an address
is a decision about a class of URLs that this capability happens to live in. An
unreachability measurement is not a decision at all -- it is a fact about
LinkedIn.

**Name the blocker precisely: "refused by a class filter written for a different
purpose."** That is a distinct blocker from "nobody built it" and from "ruled
out", and collapsing them loses the information a future reader needs: **these
eight are one narrowing away from buildable, and an EXCLUDED-RULED row is not.**

### NARROWING THE FILTER IS NOT AUTHORISED BY THIS RULING

The obvious next thought -- *narrow "settings" so it stops catching
`/public-profile/settings`* -- is **a separate decision with its own cost, and
it is the dangerous direction.**

This repo already measured that `close-account` is refused by **no pattern
matching it**, and that a settings-family wildcard would admit **six**
account-ending spellings, **three defended by nothing but the absence of a
rule.** A narrowing is that risk run in reverse: it must come with **a measured
blast radius -- what else does the narrowed filter now admit --** and a test
shown failing on the admissions it must still refuse.

**So: the rows stay GAP, the blocker is named, and the narrowing is a costed
piece of work nobody has scoped.** Filing them EXCLUDED-RULED would have hidden
eight buildable rows behind a decision nobody made.

### What would reopen it

A rule that names one of these **acts** rather than their addresses. Then it is
section 3's first line and the row is EXCLUDED-RULED on that rule, cited by
symbol per section 1.


---

# AMENDMENT A -- 2026-09-19 11:20

Three corrections from the wave that requested the original rulings, plus one
from the wave that applied them. **The first EXTENDS section 2 rather than
fixing it.**

## A1. AN INHERITED EXCLUSION CARRIES THE CITATION, NEVER THE REOPENER

Section 2 requires a content row inheriting a container's exclusion to CITE the
container, so a reopener on the container reaches the content. **That is right
and it is not enough.**

`P I12` was excluded on measured URL-UNREACHABILITY -- zero of 237 urls reach
the page -- so **its reopener is about a url appearing. A CLICK ROUTE to that
container would not be caught by it**, and the OTW editor is the standing case
that click routes exist where url routes do not.

So `J99` was given a **narrower reopener than its container's**: an observed
click route, which `I12`'s own note does not state.

**RULED, extending section 2: an inherited exclusion carries the container's
CITATION, never automatically its REOPENER.** The content row must ask what
would make IT reachable, which may be a different event. **An inherited reopener
is a silent assumption that the two share a failure mode.**

## A2. THE READ/WRITE READING'S EVIDENCE IS SUPERSEDED; ITS CONCLUSION IS NOT

The section headed *"A THIRD RELATION"* records that reading as resting on
hand-inspecting ten of nineteen with a 74%-unknown extractor. **Superseded.**

The conclusion holds -- all nineteen false, no row moved, none should -- but now
on: **5** decidable from the census's own column, **5 more** from the jobs
ranges table (**8 of those 10 are opposite-direction pairs**, a read and a write
of one subject whose states are SUPPOSED to differ), and **9** settled on
**capability identity** -- following a company vs an off-platform Follow widget
on someone else's site; saved JOBS vs saved RESUMES; a job-search location
filter vs a people-search one.

**AND THE SHARPER SELF-CORRECTION.** That wave had called the class **"84%
unanswerable"**:

> **That was true of answering it BY DIRECTION. Answering it BY CAPABILITY
> IDENTITY was always available, and nine were settled that way with no column
> at all. "Unanswerable" was a fact about THE ROUTE I CHOSE, not about the
> question.**

**Before recording anything as unanswerable, name the route that failed and ask
what other route exists.** An unanswerable finding is a claim about the world; a
failed route is a claim about you, and both end in not knowing.

## A3. THE COLUMN IS CHEAPER THAN ITS OWN SCOPE SAID

`jobs.md` **already carries R/W for 84 of its 151 rows**, in section 2's ranges
table keyed by RANGES rather than ids -- 37 R, 26 R+W, 21 W, **zero conflicts.**

    free from committed evidence     3  ->  87
    judgement / leave empty         66  ->  ~64
    unreliable twins                47  ->  unused, now unnecessary

**The empty-beats-guessed ruling survives and is cheaper to honour:** the 84 are
not a guess laundered into a schema, they are a value the file already recorded.

**HOW IT WAS FOUND:** its own output showed a row with state `R` -- **which is
not a state.**

> **An impossible value in your own output is a better lead than a plausible
> one.**

## A4. THE MAP IS SOUND, AND WHY IS THE KEEPER

409 ids checked, **406 exact, 13 ambiguous all resolving correctly, ZERO
pointing at a non-existent row.**

**The map carries capability TEXT beside the id, and the redundancy that looks
like verbosity is what makes the join auditable.** The wave's own scratch parser
hit the ambiguity precisely because it joined on the id alone. **Join on
`(id, capability)`, or verify, or you are guessing.**

**A correction to a correction:** a stricter re-run reported 8 duplicates where
the first reported 13. **The stricter run was wrong; 13 is definitive.** *"The
tell was that two readings disagreed at all"* -- a disagreement between two of
your own passes is a fact about your instrument before it is a fact about the
data.

## A5. THE LEAD'S OWN ORPHAN SCAN WAS WRONG, IN THE SHAPE IT HAD JUST CRITICISED

The lead reported five unreachable reader modules from an AST import graph,
having first reported two of them wrongly from a grep and said so.

**The AST scan was also wrong.** It recorded, for the top-level entrypoint, only
the imported SYMBOL and not the SUBMODULE -- so `from linkedin_server.transport
import serve_http` at `linkedin.py:26` never registered, and `transport` was
reported dead while being imported by the program's entry point. It also missed
`press`.

**The orphan list is 7, not 5, and one of the five was never an orphan.**

> **A scan whose scope excludes the caller reports the callee as dead.**

Two wrong instruments in one hour on one question, both the lead's, each caught
by a wave. The standing form of this is already in the repo -- parse, do not
grep -- and the missing half is: **parsing is not enough if the parse is
asymmetric across the corpus.**


---

## 4. A DISCOVERY PROBE MAY NOT NAVIGATE TO A REFUSED ADDRESS, EVEN TO FIND OUT
##    WHETHER IT SHOULD BE ADMITTED

Added 2026-09-19 11:25, on the one case `messaging-measure` could close neither
by routing nor by hand-guarding.

### The measurement

`_probe_in_progress` tries five `?stage=` values to discover which one renders
rows. Measured against the shipped predicate:

    draft         ADMITTED        in-progress    REFUSED
    applied       ADMITTED        inprogress     REFUSED
                                  in_review      REFUSED
                                  /jobs-tracker/ REFUSED

**Neither routing nor hand-guarding is available: both call the same check and
both raise on three of five.** The wave stated the tension exactly:

> **A probe that can only try values already known to be admitted cannot
> discover which value is real.**

That is true, and it is the argument for admitting the addresses -- not the
argument for navigating without the check.

### RULED: THE CHECK STANDS. THE PROBE MUST NOT TRY REFUSED VALUES.

**The allowlist is the boundary, and a measurement is not an exemption from
it.** Every bypass in this repo's history was taken for a reason that sounded
like this one. If the reason is good, it is good enough to admit the address
properly -- and if it is not good enough to admit the address, it is not good
enough to navigate there unchecked.

**What the probe does instead:** constrain it to the two admitted values, and
record in its own docstring that the other three are UNMEASURED, naming them, so
the absence is a stated limitation rather than a silence. **A probe that reports
"these three were never tried, and why" is worth more than one that tried them
without permission.**

**The discovery question stays open and is answerable** -- by an admit-and-
measure wave carrying its own blast radius and a revert path, which is Amendment
A10's shape. That is a costed piece of work with an owner, not a side effect of
a probe run.

### WHY THIS IS NOT THE SAME AS THE SEVEN THAT WERE FIXED

The seven were navigating to **admitted** addresses without calling the check --
a missing guard on a legitimate act, and fixing them changed nothing they
measure. **This one is a request to navigate to a REFUSED address**, which is
the act the boundary exists to prevent. The distinction is the whole ruling:

    guard missing on an admitted address   ->  FIX IT, and it costs nothing
    navigation to a refused address        ->  REFUSED, admit it first or
                                               record it unmeasured

### What would reopen it

An admit-and-measure wave establishing that those three addresses are read-safe,
after which they are admitted and the probe needs no exemption at all.

---

## A NOTE ON WHAT THE SEVEN FIXES PROVED, WHICH IS MORE THAN THE COUNT

**"Routing changes nothing they measure, and that is checkable, not hoped."**
`NAV_TIMEOUT_MS` *is* 45_000 -- the exact value every raw call hardcoded -- and
the door's settle is the same networkidle-then-flat-wait against the same
`SETTLE_MS`. **The door is a strict superset**, so routing was provably free.

**Three were hand-guarded rather than routed, because routing would have DELETED
A MEASUREMENT rather than changed a wait:** one captures the document *before*
the settle, and a door that settles cannot yield a pre-settle document at all;
one waits for **a control, not a clock**, its own comment recording that
settling returned UNKNOWN on four postings that were running. **Hand-guarding is
a fix, not a concession** -- `assert_read_url` lifted out of the door into the
same position in the sequence.

**And the instrument's own precision limit, recorded rather than hidden:** one
file it flagged was not a hole -- the url comes from an env var and **the CALLER
checks it.** *"A function-scoped detector cannot see a guard in the caller."*
Routed anyway, because it was the only probe with **neither** half of the door
and no rate discipline at all on a shared account.
