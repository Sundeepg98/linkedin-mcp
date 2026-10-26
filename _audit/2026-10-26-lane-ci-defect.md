# 2026-10-26 lane-ci defect -- `wait` printed only the exit-code banner on a red run

Lane: lane-ci-fix-26. Branch from `master f339459` (= origin/master).

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
