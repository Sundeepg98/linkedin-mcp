# Search admission: condition 2 amended, and a guard contradiction ruled

Ruled 2026-09-19 12:57 by the box, on the `search-admission` deliverable and
`17733f1`.

**CORRECTS:** `_audit/2026-09-19-two-census-conventions-ruled.md` -- its section 6 condition 2 demands a NARROW ANCHORED pattern, and anchoring was measured to do none of the work assigned to it: `^https://www.linkedin.com/search/.*$` anchored at both ends admits 18 addresses, identical to the bare wildcard, so the condition now demands CLOSED PATH SEGMENTS instead.

---

## FIRST, MY ERROR: I SPAWNED A SECOND WAVE ONTO WORK ALREADY TAKEN

`small-measures` had taken the search wave. **I spawned `search-admission` at
12:30 onto the same conditions without checking the roster**, because I was
reading the approval as unbuilt when a wave had already picked it up. Two waves
discharged conditions 3 and 4 independently, and their guards now contradict
each other.

**The duplication is mine. The contradiction it exposed is worth more than the
duplication cost**, which is luck and not a defence.

---

## CONDITION 2 IS AMENDED: **CLOSED**, NOT **ANCHORED**

My ruling said *"a narrow ANCHORED pattern, never a `/search/` family
wildcard."* **Measured, anchoring does not do the work I assigned to it:**

    ^https://www.linkedin.com/search/.*$     anchored at BOTH ends
    newly admitted                           18
    /search/ wildcard, unanchored            18

**Identical.** And the address that proves it is not a curiosity:

    /search/results/people/../../mypreferences/d/close-account

**Its browser-normalised form is an account-ending address, and NO FORBIDDEN
SUBSTRING NAMES IT.** The two sibling traversals are refused -- `/psettings/`,
`/invite` -- so the denylist catches its neighbours and misses this one.

> **An anchor constrains where the match STARTS AND STOPS. It says nothing
> about what the middle may contain. Only a CLOSED PATH SEGMENT refuses a
> traversal.**

**Condition 2 now reads: a narrow pattern with CLOSED PATH SEGMENTS.** All four
narrow candidates refuse all three traversals; the anchored wildcard does not.
**This is a correction to my ruling made by a measurement, and the measurement
governs.**

---

## THE GUARD CONTRADICTION: RULED, AND BOTH FILES ARE HALF RIGHT

### `MUST_STAY_REFUSED` LISTING `groups` AND `events` IS WRONG AND MUST COME OUT

`17733f1` pins `/search/results/groups/` and `/events/` as must-stay-refused
**after** the admission. But `N 161`, `M C70` and `N 179` in this very blocker
are those rows. **That guard forbids serving 3 of the 20 reads the admission
exists to serve.**

**The defect is not the entries. It is that a CHOICE was encoded as a
CONSTRAINT.** It holds under S1 and contradicts the census under S2b, so it is
choice-dependent and was presented as durable.

> **A guard that encodes an undecided choice as a constraint does not record the
> decision -- it forecloses it, silently, in favour of whoever wrote the guard
> first.**

**RULED: those entries come out, or move to a clearly-marked conditional block
naming S1 as the choice they assume.** The account-ending and third-party
families stay -- those are durable under every candidate.

### DELETE vs REWRITE-INVERTED: **REWRITE-INVERTED WINS**

`search-admission`'s docstring says the revert file is **deleted** in the
admitting commit; `17733f1` says it is **rewritten and inverted** to assert the
targets ARE admitted.

**Rewrite-inverted is strictly better and is adopted.** A deleted test leaves no
record that the transition happened; an inverted one keeps asserting something
true, and its diff is the clearest possible statement of exactly what flipped.
**The file keeps both halves of the transition**, which was that wave's own
phrase and is the right one.

---

## TWO FINDINGS NEITHER THE RULING NOR THE 09-05 DOC ANTICIPATED

**`N 104` (companies) is in NO blocker assignment anywhere** -- checked against
both `HEAD` and a neighbour's uncommitted tree, which is the right way to check
a file that is uncommitted. **So a four-vertical pattern pays blast radius for a
page no row asks for.** `S2b` (`people|groups|events`) covers **19 of 20 reads
and admits one address fewer than S2**. That is the candidate to carry forward.

**THE ADMISSION DOES NOT MAKE THE SURFACE USABLE.** The denylist is scanned over
the whole url **including the query string**, so **8 of 11 ordinary search
keywords** -- `password`, `invitation`, `settings`, `verification` -- refuse
after any candidate lands. **Narrowing the filter is not authorised and is not
being authorised here.** The tool must answer for it, and the next wave states
how before the pattern lands. **A surface admitted and unusable is not a
partial win; it is a blast radius paid for nothing.**

---

## STATE OF THE ADMISSION

**Conditions 3 and 4: DISCHARGED, twice, by two waves.** Conditions 1, 2 and 5
untouched. **Nothing admitted** -- `readonly.py` byte-identical to `9421af9`,
verified by empty diff. **The shaper remains the whole cost**, and the
`_SANITISERS` design brief filed today is now known to meet it: a search-results
shaper wants a closed-alphabet verdict function, which this repo currently has
no route to certify.
