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


---

## 5. THE FIRST SANCTIONED PRESS CONVICTED TWO OF ITS OWN CONDITIONS

Ruled 2026-09-19 11:50, on the wave's own report of the press it was authorised
to take. **It executed the press, then argued that two of the four conditions
pass whether or not the thing they describe occurred** -- including one that,
read strictly, would have made that press a REFUSAL.

**It declined to rule on that itself**, with the right reason: *"a wave arguing
its own permitted press should have been refused is exactly the argument that
should be made by someone else."*

### WHAT ACTUALLY HAPPENED, AND IT IS CLEAN

    1  is_read_url True, check_address admitted True   BOTH BEFORE ANY LOAD
    2  shape '[aria-expanded]' a KEY from SANCTIONED_SHAPES, no selector, no label
    3  priced_by ['invitations','notifications_unread'], both read, neither None
    4  closure verified, AND MEASURED INDEPENDENTLY OF THE GATE:
         BEFORE  expanded_true 0  expanded_false 9  dialogs 0  shape_total 9
         AFTER   expanded_true 0  expanded_false 9  dialogs 0  shape_total 9

CDP pages 10 before, 10 after. Page closed in a `finally`. **The page was left
exactly as found and that is established outside the gate, which is the part
that matters most and is not in dispute.**

**It banked nothing.** `N 133` / `N 134` stay GAP.

### DEFECT ONE: CONDITION 4 CANNOT WITNESS DISCLOSURE

Four lines of `press.disclose`, in this order:

    expanded_before = await locator.get_attribute("aria-expanded")
    await locator.click(...)
    await page.keyboard.press("Escape")        # DISMISSED FIRST
    expanded_after  = await locator.get_attribute("aria-expanded")

**`expanded_after` is read AFTER the dismissal.** Nothing reads the control while
it is open, and `check_closure` requires before == after -- **which a successful
Escape guarantees whether or not anything ever opened.**

> **TWO READINGS CANNOT DESCRIBE THREE STATES.**

**Shown, not argued.** `tests/test_the_press_gate_cannot_witness_disclosure.py`
builds three pages that differ IN THE WORLD -- the control really opens; the
press lands on nothing; it opens AS A DIALOG while the control's own
`aria-expanded` never moves -- and `disclose` returns **one identical verdict for
all three.** Its control is a fourth case, a moved counter, **shown SEPARATING
through the same comparison, because a test asserting things are
indistinguishable passes trivially if it is comparing the wrong thing.**

**RULED: the gate is SAFE and BLIND, and those are different properties.** It
proves the page was left as found. It cannot show that anything was disclosed,
so **no row may be banked on a press verdict alone.** The witness fix is
verified, not proposed, and its two design points are adopted as ruled:

* **AN ENUMERATED CLOSED SET, NEVER A CALLER'S CALLABLE.** *"A seam taking
  arbitrary code at the open moment is a press seam wearing an observer's
  clothes -- it reintroduces exactly what `SANCTIONED_SHAPES` prevents, at the
  most privileged instant."*
* **IT READS THE PAGE, NOT ONLY THE CONTROL, AND IT IS A PAIR.** The dialog case
  decides it: a one-attribute witness sees false while a dialog is open and
  **reports real disclosure as a MISS** -- a false negative that *"manufactures
  a confident wrong answer where there was an honest silence."*
* **THE WITNESS IS NOT A FIFTH CONDITION.** Permission stays decided on safety
  alone. Folding disclosure in *"would turn a reading into a gate and refuse a
  safe press for being uninformative."*

**And the correction of the correction is the transferable part:** the wave first
filed the ambiguity as a limit of THAT RUN, then corrected it to a limit of the
GATE. *"A limit of a run is fixed by running again, and this one cannot be -- a
later wave reading my original wording would spend a press on his live account
to learn nothing."*

### DEFECT TWO: CONDITION 3 CHECKS READABILITY AND CALLS IT PRICING

`check_counters` refuses `no_counter_prices_this_press` when
`set(before) & set(after)` is empty -- **a test for whether a counter was READ
at both ends, never for whether it COULD HAVE MOVED.**

> **`priced_by` names counters shown READABLE, not counters shown SENSITIVE.**

The ruling's own words are the stronger ones -- *"where no counter can price a
press, unmeasurable resolves AGAINST the press"* -- and the implementation's
reading of "can price" is the weaker. **Invitations and unread notifications are
nav badges; no derived reason either responds to expanding a filter panel on an
analytics page.** They are the same class as the nav badges already recorded as
the wrong instrument for a feed press: **a counter that cannot move for the act
in question prices nothing.**

**So condition 3 on that surface can be shown PASSING and CANNOT BE SHOWN
CAPABLE OF FAILING** -- which is this repo's own definition of a check that
certifies nothing.

### RULED, AND IT IS NOT "REFUSE", BECAUSE THAT ANSWER IS ALSO WRONG

Requiring a counter shown SENSITIVE would be unsatisfiable almost everywhere:
**sensitivity can only be established by a press of that class moving the
counter, which for an outward counter is the write the gate exists to
prevent.** A condition nothing can satisfy is not a stricter gate, it is a
disabled one -- and a per-capability bar above the shipped one is theatre that
costs coverage.

**CONDITION 3 IS SATISFIED IN EITHER OF TWO WAYS, AND THE VERDICT MUST SAY
WHICH:**

    (a) A COUNTER SHOWN SENSITIVE to this press class -- as `off_state` was
        derived for a feed press, from what the label MEANS.
    (b) A STRUCTURAL ARGUMENT that no OUTWARD effect is possible from this
        surface -- made explicitly, recorded, and open to refutation.

**What is NOT sufficient is (c): a counter that was merely readable.** That is
what happened here, and it is why `priced_by: ['invitations',
'notifications_unread']` overstates what was established.

**So the press was SAFE and its VERDICT OVERSTATED ITS EVIDENCE.** The act was
permissible -- expanding a panel on his own analytics page, no third party, page
proven unchanged. What was not established is the thing condition 3 exists to
establish. `priced_by` should have read `[]`, with the structural argument in
its place.

**`press.disclose` must distinguish the three cases in its verdict**, and a
readable-only counter may no longer be reported as pricing anything.

### WHY THIS DOES NOT UNDO THE PRESS

Condition 4's independent measurement stands: the page was left as found, proven
outside the gate, on every field. Conditions 1 and 2 are untouched. **The defect
is in what the record CLAIMED, not in what was done** -- and it was found, shown
failing, and handed over by the wave that would have looked best leaving it
alone.


---

## 6. SEARCH RESULTS: ADMISSION APPROVED IN PRINCIPLE, CONDITIONAL ON THE
##    SHAPER LANDING IN THE SAME COMMIT

Ruled 2026-09-19 12:00, on a backlog item filed costed rather than relayed as
blocked.

### THE MEASUREMENT THAT FORCED IT

`SEARCH-RESULTS-SURFACE` is **the largest reader-reachable blocker in the
census: 20 rows, every one a READ, and NO ADMITTED ADDRESS for any of them.**

> **It is not waiting on a reader, an instrument, or a measurement. It is
> waiting on a decision nobody has made.**

And this repository's own record says it has been reported before -- *"people
search had no address at all, logged in my own audit as 23 gaps nobody
considered"* -- against a standing rule that **a refusal reported twice is a
design gap wearing a safety costume**, and that the second report is the one to
engineer past rather than relay.

**This is the seventh time this class has been reported blocked. Refusing again
is not caution; it is the design work not being done.**

### RULED: APPROVED IN PRINCIPLE. FIVE CONDITIONS, ALL BINDING.

**1. ADMISSION AND A NAME-FREE SHAPER LAND IN THE SAME COMMIT, OR NEITHER
LANDS.** Search results **are made of other people.** An admitted address with
no shaper in front of it hands this server a surface denser in third-party
identity than anything else on the platform -- and the entire boundary exists
to prevent exactly that. The wave that raised this said so before I did, which
is why the admission is being granted at all.

**The shaper is the shipped pattern, not a new one:** structurally name-free on
`inspect.signature`, closed output alphabet, vocabulary shipped INTO the page
and an index or token returned -- `groups.py`, then `menus.py`, then
`anchors.py`, each sharper than the last. **A slug is refused BECAUSE a slug is
a name**, and that rule does not soften because the page is a search result.

**2. A NARROW ANCHORED PATTERN. NEVER A `/search/` FAMILY WILDCARD.** This is
the boundary trap and it is measured: `close-account` is refused by **no pattern
matching it**, and a settings-family wildcard would admit **six** account-ending
spellings, **three defended by nothing but the absence of a rule.** A
`/search/` wildcard is that risk on a bigger surface.

**3. THE BLAST RADIUS IS MEASURED BEFORE THE PATTERN LANDS**, and the guard is
shown failing on what it must still refuse. What else does this pattern admit?
Answer it with `is_read_url` on concrete URLs -- **never with a substring grep
over the patterns**, which reported 32 of 32 matching a needle in this very
wave and is the grep-instead-of-parse error this repo keeps paying for.

**4. A REVERT PATH EXISTS BEFORE THE ADMISSION, NOT AFTER.** The pattern's
removal is one line; the test that shows the address refused must be written
and shown failing BEFORE the pattern is added, so the rollback is proven rather
than assumed. Amendment A10's shape.

**5. NOTHING IS FIRED FROM THAT SURFACE.** No connect, no follow, no message, no
invitation, however reachable the controls become. **Reading a result page
invites nobody and messages nobody** -- that is the whole basis of this
admission and it does not extend one step further.

### THE BOUND, AND IT TRAVELS WITH THE RULING

**This admits a READ of a page listing other people. It does not admit
ANYTHING ABOUT THOSE PEOPLE leaving this server.** The shaper is not a courtesy
attached to the admission; **it is the condition of it.** An implementation that
admits the address and defers the shaper to a later wave has not partially
satisfied this ruling -- it has violated it.

**And this is the first admission granted on a THIRD-PARTY-DENSE surface.** Like
the first structural argument, it is the one most likely to be cited later as a
precedent for something weaker. **It is not a precedent for admitting a surface
because its rows are reads.** It is granted because reads of this page invite
nobody, a shaper exists as a shipped pattern, the blast radius is measurable,
and the refusal has now been reported seven times.

### WHAT WOULD REOPEN IT, IN EITHER DIRECTION

* A measured case of the shaper emitting a name, a slug, a member id or an urn
  from that surface -- which revokes the admission, not merely the shaper.
* A control on that page that addresses a person and is reachable by a read.
* Or, the other way: a later wave showing the narrow pattern is TOO narrow to
  serve the 20 rows, which is a request to widen it and gets its own blast
  radius, not an extension of this one.
