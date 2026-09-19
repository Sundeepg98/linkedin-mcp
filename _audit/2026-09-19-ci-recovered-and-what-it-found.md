# CI recovered after 14 days dark, and the eight defects it found in its first hour

**System of record for 2026-09-19.** Commit messages carry the detail; this is
the joined-up account, because the individual fixes read as unrelated and were
not.

## The two blockers, which looked like one and were not

**1. 459 commits unpushed for 14 days.** Cause: three blobs carrying a denied
term in `_audit/2026-09-05-jobs-tail.md:403`. The working tree was fixed the
same hour it appeared (`1eae6ff`); only historical blobs kept it.
**`scripts/purge_denied_term.py` had existed since that day** -- rehearsed twice
on a clone, refusing published commits, taking a restore tag -- and was never
run. Running it took four minutes. Both shipped sweeps then read PASS and master
was pushed.

**2. CI red since 2026-09-05, and pushing did NOT fix it.** Cause:
`actions/checkout` defaults to `fetch-depth: 1`. The census tests resolve a
FROZEN BASELINE BY LITERAL COMMIT SHA (`build_blocker_map.py` sets
`FROZEN_REF = "1c08e5f"`; `test_connections_reader.py` pins `84dccba`). On a
depth-1 checkout those objects are absent and the tests ERROR AT SETUP. Measured
on run `35447846889` against a commit whose history was complete **on the
server**: 36 such errors, 14 of 19 jobs red.

**Conflating the two is what cost the day.** Unblocking the push felt like it
should fix CI; when it did not, the natural move was to re-blame the push.

## The probe that "cleared" a true premise

The orphan-branch premise -- *history-dependent tests cannot resolve SHAs there*
-- was correct. It was "refuted" by grepping for
`rev-list|rev-parse|log|cat-file|merge-base`, finding two files, running them
against a shallow clone and getting *27 passed in 19.42s*.

**That grep cannot match `git show <sha>:<path>`,** which is the shape that
breaks. **A green result from a probe that cannot reach the defect is
indistinguishable from a green result from a healthy system.**

The control that settles it, kept because it is reusable:

```
git clone --depth 1 --single-branch --branch <b> file://<repo> <tmp>   # 1 passed, 6 errors
git clone           --single-branch --branch <b> file://<repo> <tmp>   # 6 passed, 1 failed
```

The `1 failed` in the full clone was a real defect the errors had been hiding.

## The eight defects, all real

| # | what | whose |
|---|---|---|
| 1 | census map: 427 data lines against 409 frozen GAP rows | **mine**, 1h old |
| 2 | `SEARCH_RESULTS_JS` / `FILTER_PANEL_JS` executed but undeclared | search wave |
| 3 | `search_results` module imported by nothing, unruled | search wave |
| 4 | six undeclared skips, four of them a table parametrised over nothing | mixed |
| 5 | `.gitignore` line removing worktrees' UNCOMMITTED files from the sweep | **mine**, 1h old |
| 6 | two unwired readers undeclared | search wave |
| 7 | two untriaged correction candidates | today's landings |
| 8 | a control that **could not fire on Linux** | pre-existing |
| 9 | a user-home path in a tracked comment | **mine**, 1h old |

**#8 is the one worth keeping.** `test_that_forced_failure_can_actually_fail`
exists to prove the path-scrubbing assertion CAN fail, and did so by asserting a
DRIVE LETTER -- which is only how "absolute" looks on Windows. On ubuntu it
failed in its own words: *"the unscrubbed message carried no drive letter, so
the assertion above proves nothing on this platform."* **It was right about
itself.** A check that cannot fail certifies nothing, and that law had defeated
a check written to enforce it. The build box is windows-only; no number of local
runs could find it.

**#9 is the guard working on its author.** Documenting #8, the literal CI path
was pasted into a tracked comment and the exact-value identity sweep refused it
on all three platforms. It classifies by SHAPE so it never has to adjudicate
whose name is safe. Until earlier the same evening that guard was **silently
disarmed in every worktree** -- gitignored wordlist, and git does not carry
ignored files into a linked worktree -- so this would have sailed through.

## What changed structurally

* `fetch-depth: 0` on both checkout steps.
* The pre-commit hook keeps **only** the identity gate. The boundary gate moved
  to CI, which its own docstring asked for. Measured: a commit went from
  142-240s to **~620ms**. The 240s was also a CONCURRENCY tax -- one index lock
  serialises the whole fleet.
* The hook resolves TWO roots from git, deliberately different answers:
  interpreter and gate scripts from `--git-common-dir` (the checkout owning
  `venv/`), the tree being gated from `--show-toplevel`. One root for both broke
  it twice in one day.
* `scripts/push_ci.sh` publishes a parentless commit for a tree whose history
  cannot be published -- and now says plainly that it is NOT a working CI target
  for this suite, correcting its own earlier claim.

## Census position, for the record

Derived from `scripts/build_blocker_map.py` on this commit:

```
rows that have LEFT GAP since the freeze   107
rows still GAP today                       302
blockers: complete 80   partial 13   absent 4
assignments: 435 rows over 387 distinct rows, 143 blockers
```

**107 of 409 frozen rows resolved, 26%.** That is the honest denominator: the
set the ledger froze, not a set chosen after the fact.
