# 2026-10-26 lane-ci defect -- `wait` printed only the exit-code banner on a red run

Lane: lane-ci-fix-26. Branch from `master f339459` (= origin/master).

**STATUS 2026-11-25: the first pass below was INCOMPLETE.** It named the
failing test on a one-failure log; on the first live four-failure log it read,
it named three. The second pass, and the lane's CI history read by head sha,
are at the end of this record ("Second pass").

## The measured defect

On lane run **38060371469** (red, shard 0) `scripts/lane_ci.py wait` printed only
`##[error]Process completed with exit code 1.` and no test id. The failing test
was visible to a human who pulled `gh run view 38060371469 --log-failed` and
grepped -- so the data was in the log, the extractor just could not name it.

## Fixture source: LIVE LOG

`gh run view 38060371469 --log-failed` was still retrievable (97 lines) at
2026-10-26. It was captured verbatim to scratch and transcribed into
`tests/test_lane_ci.py` as `LOG_RS` -- NOT a reconstruction. Recorded here so the
fixture's provenance is a measurement, not an assumption.

## Why the current extractor missed it

CI runs the suite with `pytest -q -rs` -- **NOT** `-rf`. A `-rs` run prints a
"short test summary" that contains only SKIPPED/PASSED-by-id lines; it does NOT
print `FAILED tests/...::test` id lines. So in a real `-rs` red log the failing
test id rides three other line classes:

- the sub-banner `______ test_name ______` that opens each FAILURES block
- the FIRST `E       AssertionError: ...` line -- the message
- the `tests/file.py:NNN: Reason` reference line that closes the block

The shipped regex `_FAIL_LINE = (FAILED|ERROR) \S|##\[error\]|REFUS` matches NONE
of those. Measured on the live log, the unpatched extractor returned exactly one
line: the process banner. That is the red.

## Red output (unpatched extractor)

Against the unpatched extractor, `tests/test_lane_ci.py` ran **5 failed, 41
passed** in 7.72s. The two load-bearing reds, verbatim (abridged to the
assertion and the failing-test ids):

```
FAILED tests/test_lane_ci.py::test_the_rs_log_yields_the_failing_test_id_not_just_the_exit_banner
FAILED tests/test_lane_ci.py::test_the_second_failure_block_keeps_its_own_identity_lines
FAILED tests/test_lane_ci.py::test_a_red_run_whose_log_has_no_failing_lines_says_so
FAILED tests/test_lane_ci.py::test_a_red_run_whose_log_is_only_progress_lines_says_so
FAILED tests/test_lane_ci.py::test_the_rs_log_through_wait_prints_the_failing_test_id
5 failed, 41 passed in 7.72s
```

The end-to-end red (`test_the_rs_log_through_wait_prints_the_failing_test_id`)
printed, for a red run fed the real `-rs` log:

```
run 7: failure:failure  jobs=1  wall=5m00s
  failed job: pytest (ubuntu-latest, py3.13, shard 1)
    ##[error]Process completed with exit code 1.
```

-- the banner and nothing else. That is the defect, reproduced by the test.

## Green (post-fix)

The same file ran **46 passed** in 4.72s. The fixed extractor on the live log
of run 38060371469 returns five lines: the sub-banner
(`test_no_new_unresolvable_citation_appears`), the first `E` line
(`AssertionError: NEW unresolvable SHA citation(s)...`), the second `E` line,
the reference line (`tests/test_a_cited_sha_resolves.py:779`), and the process
banner. The negative controls confirm an empty log and a progress-only log both
say `no failing lines found` rather than print silently.

## Fix

Extend `first_failing_lines` to also surface the four new line classes, while
keeping the classes it already handled (`FAILED`, `ERROR`, `##[error]`, `REFUS`)
working -- additions, not replacements. Per-text dedup stays, so the banner, the
totals line and repeated E lines do not flood the section. Add a
`no failing lines found` negative control so a red verdict whose log has no
failing class does not print silently.

## Instrument

`INSTRUMENTS.md` section 98 (append at end). Admitted by the red shown above:
the extractor demonstrably returned only the banner on a real red log, and a
test now proves it must return the test id.

## Second pass (2026-11-25): every failing test, as a node id

### The lane's CI history, read by head sha

| head | run | date | verdict | what failed |
|---|---|---|---|---|
| `cfee8d6` | 40325341840 | 2026-10-26 | failure | this lane's own: `test_the_audit_index_is_derived.py::test_a_non_ascii_title_is_declared_and_reported` (the record's H1 carried U+2014 and the committed index had not been regenerated over it), plus the shared family below |
| `cf76014` | 40371662148 | 2026-10-26 | failure | the shared family only: `test_apply_modal_fixture.py` x3 (`test_an_apply_now_reaches_the_gate`, `test_a_proceeding_gate_appends_the_second_click`, `test_the_submit_gates_refusal_reaches_the_caller`) and `test_verification_that_could_not_read.py::test_the_two_receipts_do_not_print_the_same_place` |
| `3db8aae` (merge of origin/master `30582f4`) | 45636341584 | 2026-11-25 | **success** | nothing |

The shared family was NOT this lane's, and that is now measured rather than
inferred: master's own run 40314801175 on this lane's base, which carries none
of this lane's changes, failed the same four sub-banners; the fixes lane traced
them to an unpinned playwright resolving 1.64.1 (`INSTRUMENTS.md` section 95);
and the same lane code went green once `cab0ae7` was merged under it.

### The merge, and the count git got wrong

Merging origin/master (`30582f4`) conflicted in two places, both at the end of
an append-ordered file. `INSTRUMENTS.md`: master appended section 95 and this
lane section 98, both after 93; resolved as a pure union in heading-number
order, 95 then 98 (+45 lines against master, +35 against the lane head, zero
removed either way). `INDEX.md`: regenerated, never hand-merged (275
documents). And one silent one: `RULINGS.md` merged WITHOUT a conflict,
because both sides had made the identical edit "documents scanned 272 -> 273";
the merged corpus derives 274. Two equal +1s merge as one.

### What the first pass printed on a real four-failure run

Lane run 40371662148 was the first live red run the fixed extractor read. Its
`--log-failed` (374 lines, two failed shards) was re-fetched and both
extractors were run over it, as shipped:

| extractor | lines printed | failing tests named |
|---|---|---|
| base (`f339459`) | 3 | 0 of 4 -- a skip reason, the exit banner, a docstring line |
| first pass | 20 (the cap) | 3 of 4 -- the fourth block, and shard 1's banner, fell past the cap |
| second pass | ids first, then the capped detail | **4 of 4**, as node ids |

The first pass kept every `E` line and every `tests/...:NNN` frame, so twenty
lines ran out one block early. Its own comment said "the first E line"; the
code took them all. The cap is right for detail and wrong for the ids, so the
ids are now read on their own (`failing_test_ids`) and `_report` prints all of
them first, with the count it withheld past `ID_LIMIT` (50).

### Two shapes measured, one of them caught only by the real log

- A LONG NAME IS PADDED WITH ONE UNDERSCORE. Measured with `pytest -q -rs`
  and COLUMNS=80 (CI's fallback width): an 84-character test name prints as
  `_ name _`. Both banner patterns wanted four, so such a test vanished from
  the report entirely. Both now admit any fill width.
- THE FRAME SEPARATOR IS NOT A BANNER. Widened, the pattern took pytest's
  `_ _ _ ... _` (drawn between the frames of a long traceback; lines 83 and 97
  of that log) for a failing test, and printed five ids for four failures.
  The transcribed fixture had passed: it copied only lines the OLD pattern
  matched, so it never carried the separator. Running the shipped `_report`
  over the real log is what caught it. The title may no longer start with
  fill.

Red first, both rounds: 10 failed / 47 passed before the id list; 3 failed /
55 passed once the real log's two separators joined the fixture; 58 passed
after. Over both real red logs the shipped `_report` names 1 of 1 and 4 of 4,
and prints no separator.

### Known limit, left as found

The `REFUS` class predates this lane (it is in the base's pattern) and matches
uppercase prose: on run 40371662148 it printed a skip reason ("The REFUSAL")
and a test's docstring ("a recorder that REFUSES"). Two noise lines in the
detail view, none in the ids, which never read that class. Not this lane's
defect; anchoring `REFUS` to the gate's own refusal output would be a
separate, small change.

### Also fixed in passing

The prefix stripper held a literal, invisible U+FEFF inside a string; it is
spelled `chr(0xFEFF)` now. And the OS temp cleanup had wiped this lane's
scratch between sessions; both red logs were re-fetched, read-only, for the
measurements above.
