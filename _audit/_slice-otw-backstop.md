# Slice: set_open_to_work had no backstop behind _direction's unknown gate

Date: 2026-08-31. Branch master, base HEAD 77ecd2b. Working tree only -- nothing
committed, nothing staged.

Files touched (exactly two):

* `D:\workspace\projects\job-hunting\mcp-servers\linkedin\linkedin_server\writes.py`
  -- +27 lines, the guard at lines 2717-2743.
* `D:\workspace\projects\job-hunting\mcp-servers\linkedin\tests\test_writes.py`
  -- +64 lines, the test at line 3234.

`git diff --stat` on the pair: `2 files changed, 91 insertions(+)`. No deletions,
so nothing else in either file moved.

---

## 1. The red, verbatim

Test written first, guard not yet added. Command:

    venv\Scripts\python.exe -m pytest -q "tests/test_writes.py::test_open_to_work_refuses_an_ORIGIN_IT_CANNOT_NAME_AN_AUDIENCE_FOR"

Tail of the failure, exactly as pytest printed it:

    if spec.from_state is None:
        # Not a binary toggle. Open To Work has three states, so the
        # destination cannot be derived and the caller has to name it.
        if not to_state:
            raise WriteAttemptError(
                f"{spec.action!r} has more than two states, so the "
                "destination must be named rather than derived. Choose one of "
                f"{sorted(spec.audiences)}."
            )
        if to_state.strip().casefold() not in spec.audiences:
            raise WriteAttemptError(
                f"{to_state!r} is not a setting this server has ever seen "
                f"LinkedIn render. The known ones are {sorted(spec.audiences)}, "
                "and a gate that cannot say who can see a setting must not "
                "offer it."
            )
        if state.strip().casefold() == to_state.strip().casefold():
            raise WriteAttemptError(
                f"the setting is already {state!r}. Nothing to change."
            )
        out = dict(read_from)
        out.update(
            {
                "currently": state,
                "after": to_state,
    >                   "who_can_see_it_now": spec.audiences[state.strip().casefold()],
                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                "who_will_see_it_after": spec.audiences[
                    to_state.strip().casefold()
                ],
            }
        )
    E           KeyError: 'anyone on linkedin'

    linkedin_server\writes.py:2722: KeyError
    =========================== short test summary info ===========================
    FAILED tests/test_writes.py::test_open_to_work_refuses_an_ORIGIN_IT_CANNOT_NAME_AN_AUDIENCE_FOR
    1 failed in 2.11s

The receipt line is `KeyError: 'anyone on linkedin'` raised at `writes.py:2722`.
A raw dict subscript, not a `WriteAttemptError`. It names nothing the operator
could act on, on the one action this module documents as IRREVERSIBLE IN
AUDIENCE.

The observation driving it carries `state="Anyone on LinkedIn"` -- LinkedIn's
own audience wording elsewhere in their product, chosen so the case under test
is a RENAME rather than a corruption. `to_state` is `"off"`, which is valid, in
`spec.audiences`, and different from the state, so all three existing checks in
the branch pass and execution reaches the subscript.

## 2. The guard added

`linkedin_server/writes.py`, in the `spec.from_state is None` branch, after the
three destination checks and BEFORE `out = dict(read_from)`:

```python
        if state.strip().casefold() not in spec.audiences:
            # THE ORIGIN GETS THE SAME CHECK THE DESTINATION ALREADY HAD.
            # Above this line the state has only been tested for emptiness and
            # for ``unknown``; the block below then subscripts
            # ``spec.audiences[...]`` with it. A relabelled or translated
            # audience -- anything LinkedIn renders that this spec has not met
            # -- came out of that subscript as a raw KeyError rather than a
            # sentence, on the one action whose residue is IRREVERSIBLE IN
            # AUDIENCE. Measured 2026-08-31: state 'Anyone on LinkedIn' raised
            # ``KeyError: 'anyone on linkedin'`` at writes.py:2722.
            #
            # It refuses rather than defaulting, and that is the load-bearing
            # half. A fallback string would let the gate print WHO CAN SEE IT
            # NOW for a setting it cannot identify, which is the exact claim
            # ``_read_profile_state`` already declines to make one layer up.
            #
            # UNREACHABLE THROUGH ``preview`` TODAY, like refusal 1 above:
            # ``_read_profile_state`` casefold-checks the audience itself and
            # returns ``unknown`` on a miss. Kept for the same reason -- it is
            # the guard that catches a future edit routing round that read.
            raise WriteAttemptError(
                f"the current setting reads {state!r}, which is not one this "
                f"server has seen LinkedIn render. The known ones are "
                f"{sorted(spec.audiences)}, and a gate that cannot say who "
                "can see the setting he is in must not offer to change it. "
                + observation.state_why
            )
```

It matches the voice of its siblings: it names the value read, names the
permitted set, says why the gate refuses rather than proceeds, and appends
`observation.state_why` so the refusal carries its own measurement -- the same
tail the wrong-state and unknown refusals already use.

It is deliberately distinguishable from the DESTINATION refusal four lines
above, which says `is not a setting this server has ever seen LinkedIn render`.
The origin refusal says `the current setting reads ...`. Two refusals whose
messages could not be told apart is the defect a cold review already found in
this file once, on the `unknown` gate; the test asserts the destination phrase
is ABSENT so it cannot pass on the wrong refusal.

## 3. Mutation evidence

Three mutations, each run against the single test.

**M1 -- delete the raise (the guard block removed entirely).**

    E           KeyError: 'anyone on linkedin'
    linkedin_server\writes.py:2722: KeyError
    FAILED tests/test_writes.py::test_open_to_work_refuses_an_ORIGIN_IT_CANNOT_NAME_AN_AUDIENCE_FOR
    1 failed in 1.58s

Red, with the original defect. The test is not passing on something else.

**M2 -- ORDER. Guard restored verbatim but moved to AFTER the
`out.update({... spec.audiences[state...] ...})` block.**

    E           KeyError: 'anyone on linkedin'
    linkedin_server\writes.py:2722: KeyError
    1 failed in 1.56s

Still red, and identically so. The subscript raises before the guard is ever
evaluated, so a guard placed after it is dead code. Placement before the
subscript is load-bearing, not stylistic.

**M3 -- the "helpful" repair. Guard deleted and the subscript softened to
`spec.audiences.get(state.strip().casefold(), "UNRECOGNISED")`.**

    >       with pytest.raises(WriteAttemptError) as excinfo:
    E       Failed: DID NOT RAISE WriteAttemptError
    tests\test_writes.py:3285: Failed
    1 failed in 1.57s

Red. This is the mutation that matters most, because it is the repair a future
edit is likeliest to reach for: it makes the crash go away and leaves the gate
printing `who_can_see_it_now: "UNRECOGNISED"` for a setting it cannot identify.
The test rejects it. Note the word UNRECOGNISED is the exact string the
pre-2026-08-23 version of this branch used to print, which the docstring on
`_direction` already records as the bug fixed by moving the unknown check ahead
of the branch; M3 confirms the test would not let it back in.

Guard restored after each mutation; `git diff --stat` on `writes.py` back to
`27 insertions(+)`, 0 deletions, verified after the last restore.

## 4. Verification

    venv\Scripts\python.exe -m pytest -q tests/test_writes.py
    159 passed in 97.86s

    venv\Scripts\python.exe -m pytest -q tests/test_writes_nine.py tests/test_tools.py
    253 passed in 15.35s

Full suite NOT run -- three sibling agents are editing other files in this tree
concurrently. Both edited files are pure ASCII (checked by codepoint scan, not
by eye). Nothing committed, nothing staged, `_state/` untouched, no browser
launched beyond the suite's own local headless Chromium fixture.

## 5. Honest note: is this an observed bug or a shape-closer?

**It is a shape-closer. No real LinkedIn state string is known to trigger it,
and none can today through the supported path.**

The reasoning, traced rather than assumed:

* `set_open_to_work` has `state_from="profile_topcard"`, and the ONLY reader
  that serves that is `_read_profile_state`.
* `_read_profile_state` already performs this exact check on the value it read:
  `if audience.casefold() not in spec.audiences:` and returns `UNKNOWN` with a
  reason.
* `_direction`'s `state == UNKNOWN` gate then refuses. Since 2026-08-23 that
  gate runs BEFORE the multi-state branch, which is what
  `test_open_to_work_refuses_an_ORIGIN_it_could_not_read` pins with its
  `renamed` fixture ("Selected partners").

So a relabelled audience arriving from LinkedIn is caught one layer up and
produces a proper refusal. To reach the `KeyError` the test has to call
`_direction` directly with a hand-built `Observation`, which is the only route
in and is what it does.

What the guard is therefore worth is the same thing refusal 1 in `_direction`'s
own docstring is worth, in that function's own words: *"Unreachable through
`preview`, which always observes first, and kept because it is the guard that
would catch a future edit routing round the read."* Concretely, it closes three
future edits:

1. a second reader added for this spec that does not repeat the audience check
   (the check currently lives in exactly one function and is not enforced by
   anything);
2. the two casefold normalisations drifting apart -- `_read_profile_state`
   validates `audience.casefold()` after a `.strip()`, `_direction` subscripts
   `state.strip().casefold()`; they agree today and nothing asserts that they
   must;
3. any caller reaching `_direction` other than `preview`. There is exactly one
   today, at `writes.py:2952`.

**What this is NOT:** evidence that LinkedIn has ever rendered a fourth
audience, or renamed one of the three. The spec's own `residue` field records
that only ONE of the three states has ever been observed on this account,
`'Recruiters only'` -- so the all-members and off strings in `spec.audiences`
are themselves unobserved, and a rename of any of them would be invisible to
this server until it happened. The guard does not measure that risk; it only
makes the failure a sentence instead of a stack trace when it lands.
