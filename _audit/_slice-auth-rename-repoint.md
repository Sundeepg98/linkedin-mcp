# Slice: repoint tests after the linkedin_login rename

Scope: `tests/` only. No file under `linkedin_server/` was touched. Nothing committed.

## Result

| measure | before | after |
|---|---|---|
| tests COLLECTED | 1481 | 1482 |
| tests PASSED | 1463 | **1482** |
| tests FAILED | 18 | 0 |

`python -m pytest -q` -> `1482 passed in 391.67s`. Collected count went UP by one
(the new alias test); no test was deleted, skipped or xfailed. The only `def test_`
lines in the diff are one rename and one addition -- verified with
`git diff -U0 -- tests/ | grep -E "^[-+].*def test_"`.

## The live failure list was 18, not the 12 in the brief

The brief named 12 and said to run the suite for the live list. It is 18: the six
extra are the six parametrizations of
`tests/test_tools.py::test_an_auth_wall_bounce_is_not_authenticated_not_an_empty_list`,
which asserts the auth-wall refusal message names the login tool. Same class as
the rest -- a stale assertion on the old spelling -- so it was repointed the same
way. Flagged rather than absorbed silently.

## Every test changed, and why

### tests/test_server_surface.py

| test | change | reason |
|---|---|---|
| module docstring | `nineteen tools, fifteen of which read LinkedIn` -> `twenty tools, sixteen of which do not write` | count moved 19->20; also records that "read LinkedIn" was never what the second number counted (login/logout/cdp_status/server_info were always inside it) |
| `EXPECTED_TOOLS` | added `linkedin_login`; **`linkedin_login_browser` kept** | both names are registered, so both belong in a set-equality check |
| `test_the_surface_is_exactly_the_nineteen_tools` -> `..._twenty_tools` | renamed; `len(tools) == 19` -> `20`; `len(set(tools) - SANCTIONED_WRITE_TOOLS) == 15` -> `16` | precedent set by its own docstring: the name is a claim and gets re-measured. Docstring now records that this fourth rename is UNLIKE the first three -- twenty NAMES over nineteen capabilities, because a rename added a name, not a tool |
| `test_the_login_tool_promises_never_to_touch_a_credential` | lookup moved from `linkedin_login_browser` to `linkedin_login` | the "never sees, types, stores or transmits a password" sentence lives verbatim in the canonical tool's docstring; the alias's docstring refers to the property but does not repeat the sentence, so the old lookup was asserting the promise against the wrong text |
| `test_both_login_names_are_registered_and_the_old_one_forwards` | **NEW** | see below |

### tests/test_auth.py

| test | change |
|---|---|
| `test_session_info_says_the_login_outlives_a_restart` | `on_expiry` must name `linkedin_login` and must NOT name `linkedin_login_browser` |

### tests/test_session_info_offline.py

| test | change |
|---|---|
| `test_the_durability_block_survives_the_offline_path` | same pair on the browserless path (both paths render the same `ON_EXPIRY` constant) |

### tests/test_auth_lifecycle.py (8)

| test | change |
|---|---|
| `test_renewal_says_there_is_no_silent_renew_and_says_why` | `renewal["why"]` names the canonical tool, not the alias |
| `test_the_live_path_carries_renewal_too` | same, live path |
| `test_the_mechanism_answers_in_its_own_words` | `renewal["mechanism"]` names the canonical tool -- and the cross-server comparison this test is about is why the spelling moved |
| `test_the_two_new_keys_survive_an_unreadable_jar` | same, unreadable-jar path |
| `test_the_preview_says_what_the_sign_in_cost_and_how_to_get_back` | `preview["recovery_is_by_hand"]` names the canonical tool |
| `test_an_unconfirmed_logout_does_not_claim_a_verdict` | `recover_by == "linkedin_login"` |
| `test_a_confirmed_logout_states_the_scope_the_loss_and_the_way_back` | `recover_by == "linkedin_login"` |
| `test_a_logout_never_raises_on_a_path_that_is_not_a_profile` | `recover_by == "linkedin_login"` |

### tests/test_tools.py (1 test, 6 params)

| test | change |
|---|---|
| `test_an_auth_wall_bounce_is_not_authenticated_not_an_empty_list[6 params]` | the refusal message names `linkedin_login`, not the alias |

## One repoint that STRENGTHENED rather than translated

Every prose assertion above was `"linkedin_login_browser" in <text>`. Translating it
to `"linkedin_login" in <text>` and stopping there would have produced a check that
CANNOT FAIL against the pre-rename string, because the retired name contains the
canonical one as a substring. Measured:

```
positive-only  vs OLD string -> True   (the trap: cannot fail)
positive-only  vs NEW string -> True
repointed pair vs OLD string -> False  (catches a regression)
repointed pair vs NEW string -> True
```

So each of those eight sites asserts BOTH halves: the canonical name is present and
the deprecated one is absent. That is true of the product today -- `auth.py` names
only `linkedin_login` in `ON_EXPIRY`, `renewal.why`, `renewal.mechanism`,
`preview.recovery_is_by_hand` and the auth-wall message -- and it is the property
being repointed to, so it is asserted rather than assumed.

The three `recover_by ==` sites are equalities and needed no companion negative;
they already fail on the old value. Noted in the comment there.

## The deprecated alias: STILL COVERED, and more than before

**Yes.** `linkedin_login_browser` is covered by four things, one of them new:

1. `EXPECTED_TOOLS` set-equality in `test_the_surface_is_exactly_the_twenty_tools` --
   the alias must be registered or the surface test fails. It was NOT removed.
2. `test_every_tool_documents_itself` -- the alias's own description is held to the
   same >= 120 char minimum as every other tool.
3. `test_no_tool_name_implies_a_write` and the rest of the file's per-tool sweeps run
   over it unchanged.
4. **NEW: `test_both_login_names_are_registered_and_the_old_one_forwards`** -- asserts
   both names are registered, then DRIVES the deprecated name with
   `login_via_browser` stubbed and measures where the call lands: the alias must reach
   the same sign-in with the same `wait_seconds` and return its answer unchanged. The
   canonical name is then driven through the identical stub as a control, so the
   assertion means "forwards" rather than "answers plausibly".

No test was repointed off the alias onto the canonical name and left at that. The one
lookup that did move -- the password-promise test -- moved because the sentence it
asserts lives in the canonical docstring; the alias did not lose coverage, it gained
the forwarding test.

### The new test was shown FAILING before it was kept

Mutation-probed out-of-tree (no product file touched):

```
MUTATION 1 (alias stops forwarding, answers on its own) -> CAUGHT
MUTATION 2 (alias forwards but drops wait_seconds)      -> CAUGHT
CONTROL   (real alias)                                  -> PASSES
```

## Could not repoint honestly

None. All 18 failures were stale assertions and every one was repointed to the new
invariant. Nothing was deleted, weakened, skipped or xfailed, and no failure looked
like a product bug.

## Two observations, NOT acted on (outside this slice)

1. **`linkedin_server/server.py`'s module docstring is stale.** It opens *"The tool
   surface: seventeen tools, fourteen of which read LinkedIn. THE OTHER THREE
   WRITE..."* -- the live surface is 20 tools and 4 writes. No test asserts that
   docstring, so the suite is green with it wrong. It is product code and the brief
   forbids touching `linkedin_server/`, so it is reported, not fixed. Note the same
   docstring already says *"Counts in this docstring are re-measured per wave, not
   carried"*, which is the rule it is currently breaking.
2. **The three new machine-readable keys have no test.** `reauth_tool` (None),
   `reauth_absence_is_deliberate` (True) and `call_instead` ("linkedin_login") are
   asserted nowhere -- `test_the_two_new_keys_survive_an_unreadable_jar` refers to an
   earlier pair (`uses_browser` / `mechanism`), not these. `call_instead` in
   particular is the machine-readable half of this very rename and is currently
   unpinned: it could be reverted to the old spelling, or dropped, without a red
   test. Adding that coverage is beyond "repoint what is failing", so it is flagged
   for the lead rather than done.

## Verification

- `python -m pytest -q` -> **1482 passed**, 0 failed.
- Collected: 1481 before, 1482 after (did not go down).
- Files edited, all with **zero bytes > 127**:
  - `tests/test_auth.py` (23865 bytes)
  - `tests/test_auth_lifecycle.py` (44591 bytes)
  - `tests/test_server_surface.py` (58066 bytes)
  - `tests/test_session_info_offline.py` (14606 bytes)
  - `tests/test_tools.py` (46650 bytes)
- `git status`: the only modified files beyond the two `linkedin_server/` files that
  were ALREADY dirty when this slice started are the five test files above. Nothing
  committed. No browser, Playwright or `scripts/` execution at any point.
