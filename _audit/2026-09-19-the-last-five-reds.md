# THE LAST FIVE REDS: WHAT EACH ONE ACTUALLY ENCODED

> **SHA NOTE, added 2026-09-20.** The short hashes `59192ac` and `889f488` cited
> below were committed on a `worktree-agent-*` branch that never merged, so
> they are reachable only from that branch and never from `master`. **The work
> itself landed.** Mapped to their `master` twins -- identical subject, identical
> author date, identical `git patch-id` -- under **"Dead hashes, recovered"**
> at the foot of this file; each is kept in place here because a short hash
> is the key a reader arrives with.

Wave `gate-green`. All numbers stamped with when they were taken, by the box.

    reproduced          14:38    5 failed, on the five named
    green at HEAD       15:09    5 passed
    commits             7d8ebf1, 385eeda, 28eadd7
    AI attribution      0        across origin/master..HEAD
    full suite          NOT RUN  -- a neighbour committed mid-wave (59192ac).
                                 See "What was not measured" at the end.

---

## THE HEADLINE FINDING: THERE WERE SIX, NOT FIVE

**A sixth failing assertion was masked behind the fifth.**
`test_the_url_guard_still_refuses_compose_even_though_it_was_not_consulted`
asserts the count at line 262 and then runs a loop at line 271. pytest stops at
the first failing assertion, so the loop was never reached and never reported.
It fails too:

```
for path, function, kind in readonly.SANCTIONED_MUTATIONS:
    if kind != "click":
        assert (path, function) == ("linkedin_server/writes.py", "perform")
```

`("linkedin_server/press.py", "disclose", "press")` is a non-click that does
**not** live in `writes.perform`. Measured 14:39: the loop returns one
offender. This is substantive rather than a count, and it was invisible while
the count above it was red.

> **A COUNT ASSERTED ABOVE A PROPERTY HIDES THE PROPERTY.** The cheap
> assertion fails first and reports itself as the whole state of the test.

---

## BLOCKER A -- AND THE BRIEF'S PREMISE ABOUT IT WAS WRONG

The brief said the two docstring reds were *"likely the same growth reaching a
split/sum stated elsewhere"* and told me to check rather than assume. Checked:
**they are neither a count nor a ruling. A safety guard is genuinely firing.**

### RED 1 -- `test_the_surface_is_exactly_the_fortytwo_tools` -- A COUNT

**Measured off the registry, 14:38: `len(await mcp.list_tools())` is 44.** The
brief's 44 is right and its earlier AST count of 46 was wrong -- an AST count
of the `@mcp.tool()` decorator is not a count of the registered surface.

`linkedin_creator_analytics` (4272994) and `linkedin_job_collections`
(633312f) shipped and four sites had to move: `EXPECTED_TOOLS`,
`assert len(tools)`, the read split 30 -> 32, and the test's own NAME.

**THE PIN WAS THE LAST OF FOUR SITES TO MOVE, NOT THE FIRST.** `server.py`'s
headline and `README.md` moved on the day; the two sentences a hundred lines
below that headline moved a day later; the pin moved today, by a third party.
`server.py`'s docstring had recorded the debt verbatim -- *"renaming it belongs
in test_server_surface.py's own repair with its own reasoning"* -- which is
correct routing and also shows the limit of routing by docstring:

> **A DEBT WRITTEN DOWN IN A DOCSTRING IS NOT ASSIGNED TO ANYBODY.** It waits
> for whoever next runs the suite. In the meantime the pin asserts the old
> number with full confidence, because **a pin is not a notification.**

The four citations of the old test name in `server.py` moved with the rename.

### REDS 2 AND 3 -- A GUARD FIRING ON A LINKEDIN LABEL

`readonly.docstring_write_claims` reads the verb inside **`Feed post`** -- a
heading LinkedIn draws on the analytics page, which the new tool's docstring
quotes -- as a claim that the tool posts. Red 3 is the CONTROL for red 2, so it
failed for the same cause rather than independently: it plants a write claim in
one read tool and asserts exactly one offender comes back; a real second
offender makes that set two.

**Two repairs were refused and one taken:**

| option | verdict |
|---|---|
| add the tool to `DOCSTRING_WRITE_TOOLS` | REFUSED. That list exempts the two tools that DO write. A read tool in it advertises a read as a write and blinds the guard to the next drift. `test_writes.py`'s own standard: *a check softened to accommodate a shipped capability has stopped being a check.* |
| widen the guard to skip backticked spans | REFUSED. It silences the verb everywhere a backtick appears, a real write claim included. Both of this repo's other prose guards refuse the same move in their own words. |
| say the negative the paragraph always meant | TAKEN. `h2` carries NO analytics heading. `_NEGATORS` exists precisely so a docstring can state a boundary plainly. |

The constraint is recorded in a **comment** above the tool, not in the
docstring, because a comment is not scanned -- otherwise the next editor to
"simplify" that paragraph turns the suite red with no clue why.

---

## BLOCKER B -- THE RULING, AND WHERE I COULD NOT FOLLOW IT

Both reds assert `len(readonly.SANCTIONED_MUTATIONS) == 5`. It is 7 at HEAD
(verified against HEAD's blob, not just the worktree, 14:39 -- the foreign
groups WIP in `readonly.py` does not touch the list).

### THE RULING WAS FOLLOWED: NOT BUMPED

Each of the two comment blocks had already been extended three times --
"THREE SINCE 2026-09-01", "FOUR SINCE 2026-09-02", "FIVE SINCE 2026-09-04" --
the same three paragraphs copied verbatim into both tests, each time by
somebody who had just found it red. A `7` would be the fourth version.

**THE DIAGNOSIS UNDERNEATH IT, stated as the rule I acted on:**

> A count **of another module**, asserted in a file about messaging, has no
> reader at the moment it goes stale. Nothing that moves `SANCTIONED_MUTATIONS`
> opens this file. It is found by whoever runs the suite next -- the one person
> with no standing to say what the right number is -- so they bump it.

The second copy's own comment said the quiet part: *"THE COUNT IS ALL THIS TEST
ASSERTS ABOUT IT."* So once the number went stale, that test asserted nothing
about the list at all, and passed for three admissions before it stopped.

### THE SAME LITERAL WAS KEPT, DELIBERATELY, IN A DIFFERENT FILE

`tests/test_readonly.py` keeps `== 7` and `test_server_surface.py` keeps
`== 44`, both hand-maintained, in the same hour these two were removed.

> **THE DIFFERENCE IS OWNERSHIP, NOT ARITHMETIC.** `test_readonly.py` pins
> `SANCTIONED_MUTATIONS` **entry by entry, in order** -- an admission cannot
> arrive quietly past a full-content pin, and the person who widens the list
> already has that file open. `test_server_surface.py`'s whole subject IS the
> tool surface. **A count belongs in the file that owns the claim.**

I briefly deleted `assert len(tools) == 44` on the ground that it is implied by
the set equality above it and so cannot fail independently. **I reversed that.**
This repository has already weighed that exact trade in `test_readonly.py` and
kept the constant *"because the constant is what makes a widening visible in a
diff"*. Precedent followed rather than re-litigated.

### THE SHIPPED INSTRUMENT: THE BRIEF NAMED THE WRONG ONE

The brief said `readonly.py` ships
`test_the_stated_guarantee_matches_the_sanctioned_list` *"doing exactly this"*
and to import it. **Refuted by reading it.** That file (a) is a test module,
not something `readonly.py` ships, and (b) compares **prose against the list**.
It exposes `_claimed_counts()`, `_assertions()`, `_docstring()` -- nothing a
test wanting to assert the list against its own contents can use. There is
nothing importable there for this purpose.

**The instrument that does fit is `tests/test_probe_interaction_budget.py`**,
and it fits exactly:

* `OPEN_CLASSES` -- verbs that are a read in effect (click, hover, evaluate...)
* `gated_classes()` -- **derived by subtraction** from
  `readonly._MUTATION_CALL_PATTERNS`, so a detector class added tomorrow is
  gated by default without an edit here
* `DISMISS_KEYS` -- `press` is split **by its argument**: `Escape` dismisses,
  `Enter` submits, same call and opposite acts

That is imported, not rebuilt.

### WHY THE PROXY KEPT BREAKING

The loop read `all(kind == "click")` until 2026-09-01, was re-aimed to "not a
click implies `writes.perform`", and its own comment recorded the lesson
exactly right -- *"the proxy broke while the property held"*. Then it broke
again, the same way, four hours before this wave started.

> **A SHAPE-BASED PROXY FOR A CLASS-BASED PROPERTY BREAKS EVERY TIME THE
> CLASSES MOVE.** "Not a click" and "lives in `writes.perform`" are both
> descriptions of the list **as it happened to be**. The property underneath
> has never changed: *nothing reachable from a read path may hand LinkedIn
> input.*

### THE CEILING: EXPRESSED, BUT NOT AS A NUMBER

**THE DECLARED CEILING IS ZERO** -- zero read-path gated interactions -- and
zero is the only ceiling here that is not a ratchet. Any other number would be
raised one admission at a time by whoever met it. This one cannot be raised
without somebody arguing that a read path may type, upload or submit, which is
a ruling made in `readonly.py` and in `OPEN_CLASSES`, **neither of which is
this file.** The borrowed instrument states the refusal itself: *"Do NOT widen
OPEN_CLASSES to clear this: that silences the verb everywhere at once."*

### WHAT I REFUSED TO DO, AND WHY

**A CEILING AS A NUMBER.** `<= 7` differs from `== 7` only in tolerating
shrinkage. It goes stale on the next admission and is bumped by the same person
for the same reason, wherever it is stored. A number was not honest here.

**"EACH ENTRY NAMES THE RULING THAT ADMITTED IT" -- NOT DONE.** Checked all
seven entries. **Only the press pair cites a ruling document**
(`_audit/2026-09-19-the-disclosing-press-ruling.md`). Entries 1, 2, 5, 6 and 7
argue in place with a date and no citation. Implementing that half would mean
retro-fitting ruling references onto five admissions this wave did not make and
cannot locate -- **inventing provenance**, which is worse than the gap. It is
left undone and reported rather than approximated.

### SHOWN FAILING

`_read_path_gated` returns `[]` on the live tree, which is also what a rule
with a typo returns. So it is run over synthetic lists with a fake source
lookup, across all four decisions it makes:

    open verb on a read path              allowed
    gated verb inside the drain point     allowed
    gated verb on a read path             REFUSED
    press with Escape / press with Enter  allowed / REFUSED

A second test reads the live press call's KEY out of `press.py`, because a
`(path, function, kind)` triple cannot say which key it sends and the
disclosing-press ruling turns on that being a dismissal.

Also corrected: a docstring sentence in the same test claiming *"there is no
typing call site"* and *"exactly two clicks"*. Both false -- a fill was
sanctioned 2026-09-01, and there are three clicks. **Quoted rather than
deleted**, per this repo's correction convention. It went stale in the same
direction as the numbers under it, in the same file, unnoticed for the same
reason.

---

## COMMITS, VERIFIED AT HEAD

| sha | what | files |
|---|---|---|
| `7d8ebf1` | the write-claim guard fired on a LinkedIn LABEL | `server.py` |
| `385eeda` | forty-two becomes forty-four; the pin was the LAST site to move | `server.py`, `test_server_surface.py` |
| `28eadd7` | a count of another module, and a proxy that broke twice | `test_messaging_overview.py` |

Each verified with `git log --oneline -1` and `git show --stat` after landing,
never from an exit code. No `--no-verify`: all three passed the hook, which ran
the boundary test and 2 then 8 coupled files. No `git add -A`; every commit was
`--only` by path. `.git/index.lock` was uncontended -- all three landed on
attempt 1, with a retry loop armed and never needed.

**RENAMES, so the lead's list still resolves:**

    test_the_surface_is_exactly_the_fortytwo_tools
      -> test_the_surface_is_exactly_the_fortyfour_tools
    test_the_click_is_on_the_sanctioned_list_and_the_list_is_still_short
      -> test_the_click_is_on_the_sanctioned_list_and_is_a_read_in_effect

---

## WHAT WAS NOT MEASURED, SAID PLAINLY

**THE FULL SUITE WAS NOT RUN.** A neighbour committed `59192ac` (branch-only; on
`master` at `de2d4bf`) between my
second and third commits, so I was not the only writer, and the brief's own
finding is that an interval over a mutating tree inflates the count. What WAS
run, each stamped:

    14:43   test_the_other_two_count_claims / test_prose_that_makes_a_claim   34 pass
    14:44   test_readonly.py (with foreign groups WIP applied)                250 pass
    14:46   the 8 files coupled to test_messaging_overview                    745 pass
    14:48   test_writes.py                                                    163 pass
    14:59   the full hook set for commit B                                    497 pass
    15:07   the full hook set for commit C + test_probe_interaction_budget    804 pass
    15:09   the five named reds                                              5 pass

**That is a named subset, not the gate.** Anything outside those files is
unmeasured by this wave.

**THREE FILES ARE STILL MODIFIED AND ARE NOT MINE** -- `readonly.py`,
`test_readonly.py`, `test_readonly_boundary_invariant.py`, plus the untracked
`tests/test_the_groups_id_segment_is_closed.py`. That is `groups-admit`'s
admission, left exactly where it was. The four `_RECOVER_*.patch` files at tree
root are untouched; landing them is the lead's call and not this wave's.

## Dead hashes, recovered

Added 2026-09-20. The hashes mapped here were made on a `worktree-agent-*` branch
that never merged, so the citation was never checkable from a clone -- NOT
because history was rewritten, but because the branch carrying the commit was
never published. **The underlying work did reach `master`**, re-applied under a
new hash.

Method, measured per pair rather than inferred from ordering: the live hash is
an ancestor of `master` and the dead hash is not; both commits carry a
byte-identical SUBJECT and a byte-identical author identity and date;
`git patch-id --stable` returns the SAME id for both, so the CONTENT is
identical and not merely the message; that subject occurs EXACTLY ONCE on
`master`, so the key is unambiguous; and the dead hash prefixes exactly one
object, so a reader typing it gets one answer. The four controls that show those
checks can fail, and the whole 22-row table, are in
`_audit/2026-09-20-the-evidence-that-resolves.md`.

| dead hash | subject (the durable reference) | live hash | confidence |
|---|---|---|---|
| `59192ac` | audit(last-two): the gate at 889f488, and a worktree that disarms half a guard | `de2d4bf` | CONFIRMED |
| `889f488` | guard(navigation): a split in ARITY is impersonation, not drift -- say which | `1c84d34` | CONFIRMED |
