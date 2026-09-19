# `_VERDICTS` and its certifier, built

Built 2026-09-19 by `verdict-certifier` from the brief at
`_audit/2026-09-19-the-sanitiser-list-holds-two-kinds.md`. That brief was filed
rather than built against a closing deadline; this is the build.

**CORRECTS:** `_audit/2026-09-19-the-sanitiser-list-holds-two-kinds.md` -- two measurements taken by building it: the two of three sites that certify are `_landing_class` and `is_read_url`, not the pair that brief's amendment implies, because `_why_refused` is refused a second time by the new proof over its interpolated return; and that brief states `_landing_class` returns three verdicts where the AST measures five.

**Artifact:** `tests/test_a_verdict_earns_its_entry.py` -- 16 passed, 4 skipped.
**`tests/test_a_sanitiser_earns_its_entry.py`: 86 passed, NOT EDITED.**
**Mutation study: 8 mutations, 8 caught, ZERO survivors.**

---

## WHAT WAS BUILT

Four proofs, each a named function so a control can hand it input it must
reject. A predicate only ever run on data that passes has never been shown to
reject anything.

    non_constant_returns(source, fn)   PROOF 1   every return is a bare constant
    falls_off_the_end(source, fn)      PROOF 1b  no implicit None escapes
    measured_alphabet(source, fn)      PROOF 2   the constant set, off the AST
    members_spoken(fn, arity, CORPUS)  PROOF 3   two DIFFERENT members returned

**PROOF 1b was not in the brief and closes a real gap the other three cannot
see.** A function whose last branch falls through returns `None` at runtime
while the AST shows only the returns that were written, so `measured_alphabet`
and the declared alphabet AGREE and the entry's promise is still false:

    def v(u):
        if u:
            return "yes"
        # falls through -- returns None, and nothing else here sees it

It is a **completeness** defect, not a leak -- an implicit `None` carries no
input, so the needle half holds. What breaks is the enumeration a downstream
print is trusted against. The check is conservative (it models a trailing
return, a raise, or an if/else whose every branch exits) and its repair is one
explicit return. None of the three real sites is flagged by it.

`VERDICTS` keeps `ENROLLED`'s discipline widened by one field:
`(filename, function name) -> (arity, alphabet)`. The alphabet is **enumerated,
not counted** -- a count survives one verdict being renamed into another. It is
compared against the AST measurement, so an entry goes RED if its function
gains or loses a member.

**There is no discrimination requirement, and the absence is ASSERTED rather
than left to be noticed** (`test_this_file_has_no_discrimination_requirement`).
A future tidier seeing one arm the sibling has and this file lacks would
restore it; that test is the note saying the gap is the design.

`test_no_name_is_on_both_lists` keeps the two lists disjoint. The guard matches
`func.id in _SANITISERS` -- by spelling, corpus-wide -- so one spelling may
carry only one contract, or the guard cannot tell which it is looking at.

---

## THE CONTROLS, SHOWN FAILING

An instrument enters only if it has been shown failing. With an empty
enrolment table these are the **only** things running, so they carry the whole
claim.

| control | what it shows | shown by |
|---|---|---|
| 6x derived return | f-string, `%`, `.format`, concatenation, bare name, bare `return` -- each REJECTED | `test_the_proof_would_catch_a_derived_return` |
| closed verdict accepted | the proof is not `return ['no']`; a check that rejects everything certifies nothing and fails in the direction that looks like diligence | `test_the_proof_accepts_a_genuinely_closed_verdict` |
| boolean alphabet accepted | the brief's third instance in miniature | `test_the_proof_accepts_a_boolean_alphabet` |
| gained member caught | the alphabet's RED-on-change claim is true | `test_the_alphabet_proof_would_catch_a_gained_member` |
| constant verdict caught | `return "x"` satisfies BOTH AST proofs completely; only proof 3 catches it | `test_the_speaking_control_would_catch_a_constant_verdict` |
| nested return not counted | the false-red arm -- the naive `ast.walk` version FAILS this | `test_nested_returns_are_not_counted_as_this_functions_alphabet` |

### THE INVERSION IS NOW MEASURED, NOT ARGUED

The brief's central claim -- that the shaper table does not merely misfit a
verdict function but **scores it backwards** -- shipped as prose, and prose is
what a future tidier overrules. It now runs as a control against the sibling's
**real** `MUST_DISCRIMINATE`, imported rather than copied so the measurement
cannot drift away from the table it names:

| fixture | what it is | shaper's discrimination arm |
|---|---|---|
| `honest(url)` -> one closed verdict per pair | the property a verdict SHOULD have | **FAILS it** |
| `leaky(url)` -> `"landed on " + url` | carries its input into its output | **PASSES it** |

Both directions are asserted, so the control cannot be satisfied by a table
that separates nothing. And the second half of the argument is asserted too:
proof 1 still rejects the leaky fixture. **The shaper table is not blind, it is
MIS-AIMED** -- its discrimination arm rewards the leak while its needle arm
still refuses it, and the two are welded together in the sibling. That is the
whole reason widening the shaper table was never a loosening.

### THE MUTATION STUDY: EVERY PROOF BROKEN, EVERY BREAK CAUGHT

Controls that have only been seen passing certify nothing -- this file's own
subject. So each proof was replaced with a no-op and the suite re-run:

| mutation | survived? | caught by |
|---|---|---|
| M1 `non_constant_returns` accepts everything | NO | the 6 derived-return arms; the inversion control |
| M2 `non_constant_returns` rejects everything | NO | both accept arms; nested-return; fallthrough |
| M3 `measured_alphabet` always empty | NO | gained-member; both accept arms; fallthrough |
| M4 `members_spoken` always two members | NO | the mute-verdict arm |
| M5 `_returns_of` uses a naive `ast.walk` | NO | the nested-return arm |
| M6 `falls_off_the_end` says all closed | NO | the fallthrough arm |
| M7 `falls_off_the_end` says all fall through | NO | the fallthrough arm |
| M8 `_always_exits` always True (no branch analysis) | NO | the fallthrough arm |

**SURVIVING MUTANTS: 0 of 8.** Every proof is broken in BOTH directions --
accept-everything and reject-everything -- because a check that refuses
everything certifies nothing and fails in the direction that looks like
diligence. M5 is worth naming on its own: it confirms the false-red arm was
measured rather than assumed, since the naive walk really does count a nested
helper's `return x` as the outer function's alphabet.

**The harness is DECLARED DISPOSABLE, with the reason.** It writes a mutant
into `tests/` under a temporary name and deletes it in a `finally`, which is
unsafe in a tree several waves write to concurrently -- a stray collected file
would land in someone else's suite run. The measurement above is the durable
artifact; the tree was verified clean afterwards. Its own first version failed
for this file's exact subject: a regex missed every target because they carry
return annotations, and it was rewritten to work off the AST.

**Two defects were caught by the file's own first run, not by reading:**

1. `test_this_file_has_no_discrimination_requirement` scanned for its needle
   spelt literally and **matched its own assertion text**. A self-scanning
   check cannot be its own evidence; the needle is now built at runtime.
2. `_returns_of` compared AST nodes with `in`, which is `==` on nodes rather
   than identity. Fixed to `id()`; control 6 is the arm that holds it.

---

## THE THREE SITES, RE-RUN. **THE COUNT IS TWO OF THREE, AND THE BRIEF NAMED THE WRONG TWO.**

**All three proofs were run against all three, end to end -- not proof 1 alone.**

| site | P1 non-constant returns | P2 measured alphabet | P3 members spoken | result |
|---|---|---|---|---|
| `_landing_class` | 0 | 5 | 4 of 5 | **CERTIFIABLE** |
| `is_read_url` | 0 | 2 (`True`/`False`) | 2 of 2 | **CERTIFIABLE** |
| `_why_refused` | **1** | 3 constant (+1 open) | 2 | **REFUSED by P1** |

`_why_refused` passes P3 and its constant returns are clean; it fails on one
return and nothing else. The loader was proved against a PACKAGE module too,
not only `scripts/` -- `readonly.py` loads and `is_read_url` speaks both
members -- so the first enroller of the brief's third instance does not
inherit a broken loader.

### `_why_refused` is refused again, by a different instrument, correctly

One return is not a constant:

    "FORBIDDEN SUBSTRING %r (a deliberate class ban)" % token

Its docstring's claim is true -- the token is this package's own constant, not
a string read off a page -- **but the AST cannot prove it.** `token` is drawn
from a module attribute resolved at runtime, so the structural alphabet is
`3 + len(_FORBIDDEN_URL_SUBSTRINGS)`: open, in the only sense this proof can
measure. The other three returns are constants and measure clean.

So the function that opened the brief by being refused by the shaper table is
refused by the verdict certifier too, for a **different and also correct**
reason. It is safe in fact and unprovable as written. The route to enrolment is
its author's: hoist the token to a constant verdict per token, or return a
closed verdict and print the token separately.

### `_landing_class`: the prose undercounted its alphabet by two

The brief names three members. **Measured: five** -- the two `REDIRECTED-TO-FEED`
and `REDIRECTED-ELSEWHERE` arms are not in the prose. Nothing was wrong with the
function; the prose was a reading, and this is exactly why the alphabet is
measured off the AST rather than copied from a description.

### `is_read_url`: two members, `True` and `False`

The tightest closed alphabet in the repository.

---

## THE ONE DEVIATION FROM THE BRIEF, ARGUED NOT QUIET

The brief's rule 1 says **string** constant. Taken literally that makes
`is_read_url` -- which the brief itself calls "the clearest of the three" --
permanently unrepresentable, and a certifier that cannot admit the case that
motivated it is self-refuting.

`ALLOWED_VERDICT_TYPES = (str, bool, NoneType)`. **This is not a loosening.**
The property proved is that no input survives, and it is carried entirely by
the node being `ast.Constant`, which admits no interpolation, concatenation,
name or call whatever the value's type. A two-member boolean alphabet is
strictly tighter than any string alphabet. Types are enumerated rather than
left open, and an entry declares which it means.

**This is a ruling the brief's author should confirm or overturn.** It is
recorded here and in the module docstring rather than left in the diff.

---

## WHAT WAS REFUSED

**`VERDICTS` ships EMPTY of real rows.** All three candidates measure as
described above and **none was enrolled**, because this wave wrote none of
them. Enrolment ASSERTS a contract is safe -- a claim only the author may make,
and the brief says that discipline must not be relaxed for the new list. A
measurement is not an enrolment. The three measurements are here; the rows are
their owners' to take.

**Consequence, stated rather than hidden: the three parametrized tests SKIP on
an empty parameter set.** That is honest and it is why the controls exist --
they are not decoration, they are the only thing holding the file up until a
first row lands.

**The guard was NOT wired to consult `VERDICTS`.** With the table empty that
change would move no red and would be an untested widening of the taint
engine's trust. Wiring it is the next act, and it belongs after a first real
row.

**`_SHAPERS` was not created and `tests/test_a_sanitiser_earns_its_entry.py`
was not opened for editing.** The brief says the present table stays verbatim
and every existing entry stays certified by the test that certified it. The
strongest form of that is a file with no diff: 86 passed, unchanged. Renaming
`ENROLLED` to `_SHAPERS` would have been a cosmetic edit to a concurrently
appended table for no measured gain.

**Nothing was enrolled, wired, renamed or re-added.** The interim posture the
brief calls honest is intact.

---

---

## THE OPEN QUESTION IS ALREADY ANSWERED IN THE CODE, BY A BETTER ROUTE

The brief asks that `role` be **ruled rather than assumed**, and calls it the
one place the closed-alphabet argument may not hold. Re-measured on the live
file rather than on the brief's quotation of it: **the question is moot, and
the repair already in the tree is stronger than the ruling the brief was
waiting for.**

The line no longer prints the attribute. It prints a **membership projection**:

    role_shown = "absent" if role is None else (
        "/".join(t for t in ROLE_VALUES if role == t) or "UNKNOWN-ROLE")

The page's value is compared against this file's own tuple and anything
unmatched renders `UNKNOWN-ROLE`. So the printed alphabet is
`{"absent"} + ROLE_VALUES + {"UNKNOWN-ROLE"}` -- **closed by this file's
constants, not by the ARIA spec.** The file's own comment says so, and refuses
the spec argument explicitly: the tuples "are NOT a claim that ARIA roles are a
closed set ... that holds even if the spec is open, even if LinkedIn invents a
value, and even if this tuple is wrong -- which is the whole reason to prefer
matching to trusting." It also keeps `absent` distinct from `UNKNOWN`, so an
attribute the page did not set is not folded into one it set to something
unnamed.

**RULING: the closed-alphabet argument was never needed here.** A claim about
the world (the spec is closed) was replaced by a claim about this file (these
are the tokens it will print). The first can be falsified by a page; the second
cannot. **This is a THIRD safe shape, beside shapers and verdicts:**

    PROJECTION   input -> a member of THIS FILE'S constants, or UNKNOWN-<attr>
                 SAFE BY CONSTRUCTION, whatever the input alphabet is

It is also **the repair route for `_why_refused`**, which is the one site still
refused. Its interpolated `token` is drawn from `readonly._FORBIDDEN_URL_SUBSTRINGS`
-- this package's own tuple -- so the same projection closes it: match the
token against that tuple and return a constant verdict, or return the class
name and print the token separately. That is its author's edit to make, and it
needs no exemption and no rename.

---

## AND THE BRIEF'S COUNT OF BLOCKED SITES IS STALE. RE-MEASURED, NOT RELAYED.

The brief says three real sites are blocked. Measured on the tree as it stands
today, **`tests/test_navigation_is_never_derived.py` is GREEN: 333 passed.**

`is_read_url` was named as "standing in an orphaned red two waves declined to
own". **That red is gone**, and not by an enrolment: the call site now prints
`is_read_url={admitted is True}`, a comparison yielding a literal bool, beside
the `role_shown` projection above. The repairing comment cites "the
verdict-function filing" by name -- so somebody read this brief and
deliberately routed around its open question rather than waiting on it.

So the live count of sites blocked on `_VERDICTS` is **one, not three**:

    _landing_class   unenrolled, certifiable today, its author's row to take
    is_read_url      unenrolled, certifiable today, and no longer in a red
    _why_refused     the only one genuinely blocked, and it is blocked by its
                     own interpolated return rather than by a missing list

**A number handed from one document to another is a reading with a timestamp
the reader cannot see.** The brief's three was accurate when written this
morning and is not accurate now. Nothing here criticises it; it is the reason
the re-run was the first instruction.

---

## WHAT BLOCKED THE COMMIT, AND IT IS NOT MINE

`tests/test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged`
is **RED AT HEAD** with four untriaged candidate pairs, all in census files this
wave never opened:

    _audit/_census/jobs.md:156     cites 2026-08-30-linkedin-undo.md
    _audit/_census/jobs.md:157     cites 2026-09-19-tier1-fires.md
    _audit/_census/profile.md:164  cites 2026-09-19-tier1-fires.md
    _audit/_census/profile.md:165  cites 2026-08-31-linkedin-finish.md

Proven not this wave's: `git status` shows both files unmodified here, and the
rows are present in `git show HEAD:`. The boundary gate couples nine test files
to any staged test file, so this red blocks the certifier from landing.

**It was not bypassed and their rows were not edited.** Declaring what corrects
what is a claim about two documents, and making it for a row somebody else
wrote is the same act this whole wave exists to refuse. Relayed to the
coordinator for the owning waves.

**This wave's own correction pair IS declared**, both halves: a `CORRECTS:`
marker at the top of this file and a `CORRECTED BY:` back-pointer written into
the brief. A corrector can name its target; the target cannot name its
corrector, so the back-pointer is the corrector's job.

---

## NEXT

1. The author of `_landing_class` and the owner of `is_read_url` each add one
   row. Both certify today with no exemption and no rename. Adding a row turns
   `test_the_enrolment_table_is_empty_by_design` red on purpose -- that red is
   the handshake, not a failure.
2. `_why_refused`'s author takes the projection route above, or leaves it
   unenrolled. The current interim posture stays correct either way.
3. Wire the taint guard to consult `VERDICTS` once a first row exists, with the
   mutation arm that shows the wiring failing. Not before: with an empty table
   it would move no red and would be an untested widening of the engine's trust.
4. The four census correction pairs, by their owners.
5. Consider whether PROJECTION deserves its own certifier, or whether the
   pattern is better left as a repair that needs no list. It has one live
   instance; one instance is a case, not a kind. The brief's own standard was
   two in ten minutes.

Attribution check on this wave's commits: `git log origin/master..HEAD
--format=%B | grep -ci co-authored` reads **0**.
