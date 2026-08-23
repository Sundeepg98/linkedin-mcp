# The click, and the row of a table that is not one -- `5277dfc`..`db99276`

**What a caller can now do that it could not before.** Save a job posting, in two
calls. The first performs nothing: it loads the posting and his saved list, and returns a block
naming the job by title and employer, which way the toggle moves, where each fact was read from,
and how to undo it. The second redeems a single-use token from that block. **What still cannot
happen without him present: anything.** The flag is off in a fresh process; a grant exists only
after a human has been shown a gate built from a live read; it works once and dies in 120s, which
makes a scheduled write structurally impossible rather than discouraged. **No live write has been
executed.**

**`unsave_job` is built, gated, and refuses.** Not a missing code path -- a missing ROW. LinkedIn
identifies the save control by accessible name, and every capture this repo holds (four postings,
both hydration states, two days) shows `aria-label="Save the job"`, the OFF state. The ON state
cannot be photographed: there is nothing saved on the account to photograph it on. `"Saved"` and
`"Unsave the job"` are both plausible and neither has been seen, so `anchor_label_for` returns
`None` and `perform` refuses with that reason rather than "not implemented" -- which invites
somebody to implement it by picking a string. **The first supervised save IS the measurement**:
`perform` reads the label the control changed into and reports it as
`newly_observed_save_label`, for a human to write into `shape.SAVE_LABELS`.

## The scanner kept its teeth

The exception is a POLICY beside an unchanged MEASUREMENT, not a relaxed rule.
`scan_source_for_mutations` is byte-identical and still reports the click; `SANCTIONED_MUTATIONS`
is one line, keyed `(path, function, kind)`, and `partition_mutation_hits` splits a scan while
conserving every hit. Each third of the triple refuses something real, **all five shown failing**:
the wrong file, the wrong function, the wrong kind, a closure one scope down (attribution is
INNERMOST, so a nested helper inherits nothing), and module level.

**The hole I found in my own list, and closed.** A SECOND click inside `perform` is the same
triple as the first, so the partition cannot see it and a set comparison passes. The count can:
the package is asserted to hold exactly as many mutating calls as the list has entries. That is
asserted in `test_readonly.py` and shown failing on the real file in `test_writes.py`.

## The re-freeze, and the half of it that is a claim about the write

`026359e`, its own commit. Baseline moved `oldsha14` -> `5277dfc`. Two digests moved,
four did not, and **the four are the argument**: the navigation allowlist, the forbidden list, the
scanner's patterns and the JS tokens are byte-identical across the change. `DENYLISTS_AT_A76FE32`
keeps the pre-write values so that is CHECKABLE rather than asserted. `SANCTIONED_MUTATIONS`
joined `PINNED` -- the only one of the five that GRANTS, and a boundary of four denylists and one
allowlist is only as frozen as its allowlist. Shown failing on a second entry.

**Verified under 3.13.14 AND 3.10.19**, all six identical. A single-version local run cannot
verify a version-independent claim; that lesson cost this file three red CI runs the day before.

## What the tests can and cannot say

Measured before a line of test was written, with every request intercepted and aborted so an
attempt would register even if it could not complete: the four posting fixtures contain **zero
script tags**, attempt **zero requests** on load and **zero** on click, do not navigate, and do
not move the DOM. The click is real and dispatches in ~20ms.

**That last property is also the ceiling.** Because the fixture DOM does not move, these tests
prove the machinery clicks the right thing under the right conditions and **can never prove that
clicking it saves a job.** Only a supervised run settles that. Recorded here rather than left for
a reader to infer.

## Five gates, and the one that replaced a promise this seam could not keep

Flag; a grant `consume()` has already burned (`perform` does not redeem its own permission); the
rebuilt write url with the forbidden list unshortened; the read door on the same navigation; and
**a live re-read of the control about to be clicked**.

The old docstring promised the click would "re-check the observation's age". That cannot work, and
the arithmetic says so: an observation dies in 30s and a grant lives 120s, because one is a reading
of LinkedIn and the other is a human deciding. Enforcing 30 refuses every confirmation a person
took time over; enforcing 120 is the grant check under a second name. So the age is REPORTED and
the precondition is a fresh reading of the button -- strictly stronger, free (the page must be open
to be clicked), and for `save_job` an INDEPENDENT corroboration, since the preview took its
direction from the list and this takes it from the control.

**Nothing raises after the click.** Once the button is pressed, that it was pressed is the most
important fact there is; an exception on the way home replaces it with a stack trace the operator
answers by retrying, which on a toggle performs the opposite action. `performed` is `True`,
`False` or `"unknown"`. Verification is read from a DIFFERENT surface -- the saved list with
LinkedIn's own per-tab count -- never the button just pressed.

## The mutation run, and the three it found

20 mutants, **17 killed on the first pass**. The three survivors were each verified behavioural by
probe rather than assumed. Two diagnoses are worth more than their fixes:

- **`perform` skipping `assert_write_url` left the suite green** -- and that is a FACT about these
  two actions, not a missing test. Every url the write door would refuse for save or unsave is one
  the read door refuses a line later. The doors overlap completely, so no input distinguishes them
  and no behavioural test can exist. That overlap IS defence in depth, and it is exactly why the
  call must not be dropped as redundant: the read allowlist is not maintained with writes in mind.
  Closed STRUCTURALLY, with its own control.
- **`save_state` guessing `not_saved` for an unseen label left the suite green because that branch
  is UNREACHABLE.** `dom.SAVE_CONTROL` matches only the known label, so an unknown one gives count
  0 and the count branch answers first. Dead code today; live the moment `SAVE_LABELS` gains its
  second row, which is the entire plan for unsave. Tested now rather than while somebody is midway
  through adding that row -- and `"Save"` is in the parametrised set deliberately, one character
  from the real label. Added the anti-drift check the FOLLOW pair still does not have:
  `dom.SAVE_LABELS_SEEN` and `shape.SAVE_LABELS` live in modules that do not import each other.
- **`_write_tool` losing its writes-off short-circuit left the suite green** because the caller
  still gets an error -- after Chromium has LAUNCHED. The test now asserts the POSITION, not the
  outcome: `BROWSER.session` is replaced with something that raises. Its control arms the trap with
  writes on and confirms the session IS reached.

Re-verified by re-applying all three to an isolated copy: 8 failures, all three killed.

## The documents that still said this server cannot write

Ranked by damage. `mcp.instructions` was the worst -- it is read INSTEAD of the source by every
client model, and it said *"Every tool reads; none of them changes anything on LinkedIn."* It now
names both writes and says **NEVER CONFIRM ON HIS BEHALF**. Then README's opening (*"There is no
write path in this repository"*), README's scanner section (*"It finds none"*), and pyproject's
description. Each keeps the sentence it replaced, because a document that quietly swaps a claim
teaches a reader nothing about which claims to trust.

**And a test that had quietly stopped testing itself.**
`test_server_info_declares_the_boundary_and_lists_no_writes` asserted `read_only is True` and
PASSED after the write landed -- the flag is unset in a test process, so the computed value is True
for the right reason. Split in two, flag off and flag on, so hardcoding either field back to a
literal passes one and fails the other.

`linkedin_server_info` reports three fields, not two, because "this server has a write path" and
"this process can perform a write" are different facts: `read_only` and `writes_available` are
about the PROCESS, `writes_sanctioned` about the CODE. The capability may not hide behind an unset
environment variable.

## Not mine, and left alone

- **`ci.yml`'s header comment is stale** -- it describes 1092 tests and a 112/936/6/38 split. The
  suite is now 1285. `wire-linkedin-state` flagged this on 2026-08-23 and did not edit it either,
  because `ci-for-newest` may own that file.
- **`_audit/_instruments/` is NOT in this repo.** It sits one level up, at
  `mcp-servers/_audit/_instruments/`, holding `boundary_digest_option2_probe.py` and its control.
  I reported it missing after looking only inside `linkedin/`; it exists, and the lead ran it from
  the parent root. Worth knowing because a brief that names it with a repo-relative path will send
  the next agent looking in the wrong place.
- **`_audit/_slice-*.md` is NOT gitignored**, contrary to what I assumed when briefing a child --
  it caught the error. `.gitignore` covers only `_audit/_probe-*.html`, `_audit/*_raw.html`,
  `_audit/_fixture_sanitisation_check.txt` and `_audit/_sanitisation_key.json`. Four `_slice-*.md`
  files now sit untracked and un-ignored, which is `git add -A` exposure. I did NOT add a pattern:
  two `_slice-*.md` files are TRACKED (`_slice-cookie-jar.md`, `_slice-parity-census.md`), so a
  blanket ignore would be a rule whose own set already contradicts it. Operator's or lead's call.
- `follow_company` and `set_open_to_work` remain sanctioned and NOT performable, refused by name in
  `PERFORMABLE` with their reasons.

## Measured

All at `5a69147` unless stated.

| | |
|---|---|
| suite, CPython 3.13.14 (win32) | **1300 collected, 1300 passed, 0 skipped, 0 failed, 0 errors**, 356s |
| `scripts/ci_full_run_check.py` | **exit 0** -- collected 1300, executed 1300, none skipped, none deselected |
| suite, CPython 3.10.19 (win32) | 1282 passed / 0 skipped / gate exit 0 **at `026359e`**; the digest re-verified at `5a69147` |
| boundary digests | 6, **identical under 3.13.14 and 3.10.19**; independently re-confirmed at `5a69147` by the lead via `mcp-servers/_audit/_instruments/boundary_digest_option2_probe.py` -- 13 of 13 functions match, 0 mismatches |
| mutants | 20 applied, **17 killed** first pass, 3 closed, all 3 re-killed; 3 more re-killed after the refactor |
| package mutating calls | **1** (sanctioned), **0** unsanctioned |
| tools | 14 -> **16** |
| live writes executed | **0** |

**The one deliverable NOT produced: a CI run id.** It needs a push to `origin/master`, which is
outward-facing and spends metered runner minutes on a private repo (`ci.yml`'s own header notes a
Windows minute bills at 2x). That is the operator's to trigger, not something a task assignment
authorises, so the branch sits 6 commits ahead of `origin/master` un-pushed. What CI would check
was run locally instead: the whole suite on both interpreters plus the completeness gate that
refuses a skip or a deselection. **The gap is the OS axis only** -- both local runs are win32,
where CI's 3.10 cell is ubuntu.

**A caveat on the two "green locally is not green" mechanisms this wave could still hit.** The
skip-counted-as-a-pass one is closed (gate exit 0, `skipped=0`). The interpreter one is closed for
the boundary digest specifically, measured rather than argued. The gitignored-file one is closed by
the sweep. The history one does not apply -- nothing added here reads git history.
