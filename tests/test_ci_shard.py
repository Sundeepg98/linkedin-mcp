"""The shard split is a PARTITION, and both halves of that are shown failing.

WHY THIS FILE EXISTS. ``scripts/ci_shard.py`` lets CI run this suite in six
jobs instead of one. That trade is only safe while one property holds: the six
jobs together run exactly the tests the one job ran. Break it and the gate goes
GREEN HAVING RUN LESS, which is the failure this repository has catalogued
under a dozen names and the only one that gets worse the more you trust it.

There are two ways to break it and they need two different instruments:

* the SPLIT can be wrong -- a file in no shard, a file in two, a file the
  packer invented. That is checkable here, offline, over any weight map, and
  :func:`partition_problems` below is the check.
* the RUN can be wrong -- every shard's own numbers add up while one shard
  never ran at all. Nothing inside a surviving shard can see that, so it is
  checked across shards by ``scripts/ci_shard_totals.py``, and the controls
  for that guard are in the second half of this file.

EVERY CHECK HERE HAS A CONTROL THAT MAKES IT FAIL. A partition test that has
only ever been shown a correct partition proves nothing about a broken one, so
:func:`_drops_a_file` and :func:`_duplicates_a_file` are deliberately wrong
packers, and the tests that use them assert both that the check refuses AND
that its message NAMES the file -- because a refusal that reports only a count
is half a measurement, which this repository learnt over three rounds.

ON THE WEIGHTS USED HERE. ``REAL_SHAPE`` is the per-file test-count
distribution this suite had at e0dc8f9 (92 files, 3660 tests). It is a SHAPE to
pack, not a claim about today's suite: nothing breaks when the suite grows, and
freezing it is what makes the balance assertion below deterministic instead of
a number that drifts with every file anybody adds.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _load(name: str, filename: str):
    """Load a script as a module, the way tests/test_identity_gate.py does."""
    path = REPO / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


shard = _load("_ci_shard", "ci_shard.py")
totals = _load("_ci_shard_totals", "ci_shard_totals.py")
#: Loaded here rather than in a file of its own because ONE RULE now lives in
#: both scripts -- an xfail is not a skip -- and whoever changes it in one
#: should meet the control for the other in the same place. The same argument
#: tests/test_prose_that_makes_a_claim.py makes for keeping its three together.
full_run = _load("_ci_full_run_check", "ci_full_run_check.py")

#: The distribution measured at e0dc8f9. See the module docstring.
REAL_SHAPE = [
    279, 242, 201, 165, 163, 146, 144, 137, 124, 89, 71, 61, 58, 57,
    56, 54, 53, 51, 50, 49, 48, 47, 44, 42, 42, 41, 40, 38, 37, 35, 34,
    33, 30, 28, 28, 28, 28, 28, 27, 27, 25, 24, 24, 22, 22, 21, 20, 20,
    20, 20, 19, 19, 19, 18, 18, 18, 18, 17, 17, 16, 16, 16, 15, 15, 14,
    13, 12, 11, 11, 11, 11, 10, 10, 10, 10, 10, 10, 9, 9, 9, 8, 8, 8,
    8, 7, 7, 6, 6, 6, 5, 5, 2,
]

#: Weight maps to pack. Named, because a failure that says "case 3" sends the
#: reader to count list literals.
SHAPES = {
    # The real one, and the reason the packer sorts by weight at all.
    "real": REAL_SHAPE,
    # Everything identical: the case where any packer looks good, kept so that
    # a bug that only shows up on flat input is not invisible.
    "uniform": [10] * 40,
    # One file bigger than a whole shard's fair share. No packer can balance
    # this and none should pretend to; what matters is that it still
    # partitions.
    "one giant": [5000] + [3] * 30,
    # Descending by one, so almost every tie-break is exercised.
    "staircase": list(range(40, 0, -1)),
    # Two weights only, which produces many exact ties between shards.
    "two values": [7, 1] * 25,
    # FLOATS, because the real weight is seconds and not tests. Shaped like
    # this suite's actual profile: a couple of enormous files, a long tail of
    # near-zero ones, and nothing tidy in between.
    "seconds": [180.6, 131.3, 118.3, 74.5, 63.4, 62.7, 60.0, 58.9, 56.7,
                55.4, 50.3, 47.9, 12.1, 8.4, 6.2, 5.5, 3.8, 3.2, 2.3, 1.7,
                1.1, 0.9, 0.7, 0.4, 0.3, 0.2, 0.115, 0.1, 0.065, 0.05],
    # The smallest interesting case: as many shards as files.
    "tiny": [4, 3, 2, 1],
}


def weights_for(shape: str) -> dict[str, int]:
    """Name the files by INDEX, so alphabetical order is not weight order.

    Deliberate: a packer that happened to work only because the heaviest file
    sorted first would pass over the real suite's names by luck. Here
    ``tests/test_000.py`` is the heaviest and ``tests/test_091.py`` the
    lightest, so alphabetical order and weight order agree -- and the shuffled
    twin below disagrees with both.
    """
    return {
        f"tests/test_{index:03d}.py": count
        for index, count in enumerate(SHAPES[shape])
    }


def partition_problems(shards: list[list[str]], weights: dict[str, int]) -> list[str]:
    """Every way ``shards`` fails to be a partition of ``weights``' files.

    Returns all of them, each naming the FILE. A list of problems rather than
    an assertion so that the controls below can read the message and confirm it
    identifies the file it is complaining about.
    """
    problems: list[str] = []
    placement: dict[str, list[int]] = {}
    for index, group in enumerate(shards):
        for path in group:
            placement.setdefault(path, []).append(index)

    for path in sorted(weights):
        where = placement.get(path, [])
        if not where:
            problems.append(f"{path} is in NO shard")
        elif len(where) > 1:
            problems.append(f"{path} is in shards {where}, not one of them")
    for path in sorted(placement):
        if path not in weights:
            problems.append(f"{path} is in a shard but in no collection")

    packed = sum(weights[path] for path in placement if path in weights)
    expected = sum(weights.values())
    if packed != expected:
        problems.append(f"{expected} tests collected, {packed} tests packed")
    return problems


# ---------------------------------------------------------------------------
# The split partitions the suite
# ---------------------------------------------------------------------------


#: Every (shape, width) the sweep below runs. Built by comprehension and NOT
#: by two stacked parametrize decorators, because the cross product would ask
#: the four-file shape for sixteen shards -- which is refused, correctly, and
#: would have to be waved through with ``pytest.skip``. This suite's CI gate
#: fails on ANY skip, by design, so a case that cannot run must not be
#: generated rather than generated and excused.
SPLITS = [
    (shape, of)
    for shape in sorted(SHAPES)
    for of in (1, 2, 3, 4, 5, 6, 7, 8, 11, 16)
    if of <= len(SHAPES[shape])
]


@pytest.mark.parametrize(
    "shape, of", SPLITS, ids=[f"{shape}-of{of}" for shape, of in SPLITS]
)
def test_the_split_is_a_partition(shape, of):
    """Across many n, not just the one CI uses.

    A packer can be correct at n=6 and lose a file at n=1 (one shard, and an
    off-by-one in the tie-break) or at n=len(files) (every shard holding
    exactly one). Both ends are in this sweep.
    """
    weights = weights_for(shape)
    plan = shard.plan_shards(weights, of)
    assert len(plan) == of
    assert partition_problems(plan, weights) == []

    # NO SHARD IS EVER EMPTY, which is a property of LPT rather than a wish:
    # the first `of` files each land in a different empty bin, because an empty
    # bin has load 0 and ties break on the lower index. It is asserted because
    # of what an empty one would do -- the workflow runs `pytest $(cat
    # shard-files.txt)`, and pytest with no file arguments runs the WHOLE
    # SUITE. An empty shard would not be a fast job; it would be a 27-minute
    # one that quietly duplicates everything.
    assert all(plan), plan


def test_the_sweep_has_not_quietly_thinned_out():
    """A parametrised sweep can lose coverage without losing a test.

    Shrink a shape below a width and that width simply stops being generated:
    the run stays green, the count drops, and nothing says so. Six shapes are
    large enough for all ten widths and "tiny" for four of them, so the sweep
    is 64 cases. If that number changes, the change was either deliberate or
    the coverage this file claims is no longer the coverage it has.
    """
    assert len(SPLITS) == 64, sorted({shape for shape, _ in SPLITS})


def test_more_shards_than_files_is_refused_not_silently_empty():
    """An empty file list handed to pytest runs the WHOLE SUITE.

    That is the trap this refusal exists for: an empty shard would not run
    nothing, it would run everything, and the only symptom would be one job in
    the matrix taking 27 minutes while its siblings took four.
    """
    weights = weights_for("tiny")
    with pytest.raises(SystemExit) as raised:
        shard.plan_shards(weights, len(weights) + 1)
    assert "5 shards over 4 test files" in str(raised.value)


@pytest.mark.parametrize("of", [0, -1])
def test_a_nonsense_shard_count_is_refused(of):
    with pytest.raises(SystemExit) as raised:
        shard.plan_shards(weights_for("uniform"), of)
    assert "at least 1" in str(raised.value)


# ---------------------------------------------------------------------------
# The partition check itself, shown failing
# ---------------------------------------------------------------------------


def _drops_a_file(weights: dict[str, int], of: int) -> list[list[str]]:
    """A packer that loses exactly one file. The mutation the guard is for."""
    plan = shard.plan_shards(weights, of)
    plan[0] = plan[0][1:]
    return plan


def _duplicates_a_file(weights: dict[str, int], of: int) -> list[list[str]]:
    """A packer that runs one file twice -- green, slower, and still wrong."""
    plan = shard.plan_shards(weights, of)
    plan[1] = sorted(plan[1] + [plan[0][0]])
    return plan


def _invents_a_file(weights: dict[str, int], of: int) -> list[list[str]]:
    """A packer naming a file collection never reported."""
    plan = shard.plan_shards(weights, of)
    plan[0] = sorted(plan[0] + ["tests/test_not_collected.py"])
    return plan


def test_the_partition_check_catches_a_dropped_file():
    """CAN-IT-FAIL, and the message must NAME the file."""
    weights = weights_for("real")
    lost = shard.plan_shards(weights, 6)[0][0]
    problems = partition_problems(_drops_a_file(weights, 6), weights)
    assert problems, "a packer that dropped a file was called a partition"
    assert any(lost in problem and "NO shard" in problem for problem in problems), problems


def test_the_partition_check_catches_a_duplicated_file():
    weights = weights_for("real")
    twice = shard.plan_shards(weights, 6)[0][0]
    problems = partition_problems(_duplicates_a_file(weights, 6), weights)
    assert any(twice in problem and "in shards" in problem for problem in problems), problems


def test_the_partition_check_catches_an_invented_file():
    weights = weights_for("real")
    problems = partition_problems(_invents_a_file(weights, 6), weights)
    assert any("test_not_collected.py" in problem for problem in problems), problems


def test_the_partition_check_passes_a_correct_split():
    """THE CONTROL FOR THE CONTROLS. A check that refuses everything satisfies
    all three tests above and is useless in the way that gets a gate deleted on
    its first morning."""
    weights = weights_for("real")
    assert partition_problems(shard.plan_shards(weights, 6), weights) == []


# ---------------------------------------------------------------------------
# Determinism and balance
# ---------------------------------------------------------------------------


def test_the_split_does_not_depend_on_insertion_order():
    """Same files, same weights, a dict built backwards: the same plan.

    Collection order comes from pytest, which walks the filesystem. If the plan
    moved with it, two jobs in the same matrix could disagree about which shard
    owns a file -- and the totals would still add up, because every file would
    still be run once by SOMEBODY. The failure would be invisible and the fix
    would be a week of confusion, so the ordering is pinned here.
    """
    weights = weights_for("real")
    backwards = dict(reversed(list(weights.items())))
    assert shard.plan_shards(backwards, 6) == shard.plan_shards(weights, 6)


def test_the_split_is_stable_across_calls():
    weights = weights_for("staircase")
    assert shard.plan_shards(weights, 5) == shard.plan_shards(weights, 5)


@pytest.mark.parametrize("of", [4, 6, 8])
def test_the_real_shape_packs_within_one_percent(of):
    """The claim the docstring makes about balance, asserted rather than told.

    Round-robin over 92 alphabetical names -- the obvious implementation, and
    the one this replaced -- puts 279 tests and 242 tests in different shards
    and leaves a spread of hundreds. LPT keeps it inside 1% of the mean, and
    this is the test that notices if somebody simplifies the packer back.
    """
    weights = weights_for("real")
    loads = [
        sum(weights[path] for path in group)
        for group in shard.plan_shards(weights, of)
    ]
    mean = sum(loads) / of
    assert max(loads) - min(loads) <= max(5, 0.01 * mean), (loads, mean)


def test_a_file_larger_than_a_shard_does_not_break_the_split():
    """No packer can balance one 5000-test file across six shards. It must
    still partition, and the oversized shard must be the one holding it."""
    weights = weights_for("one giant")
    plan = shard.plan_shards(weights, 6)
    assert partition_problems(plan, weights) == []
    biggest = max(plan, key=lambda group: sum(weights[path] for path in group))
    assert max(weights, key=weights.get) in biggest


# ---------------------------------------------------------------------------
# The weights: a committed measurement that cannot lose a file
# ---------------------------------------------------------------------------
#
# The split is weighted by MEASURED SECONDS from scripts/ci_shard_timings.json,
# not by test count. That was not the first design and the correction was
# measured: at n=6, weighting by test count produced shards of
# 244/177/207/272/575/172 seconds -- a gate twice as slow as it needed to be,
# while the test counts looked balanced to within five. The per-test cost in
# this suite spans 0.005s to 14.9s.
#
# Committing a measurement brings a staleness risk, and these tests pin the one
# property that makes the risk survivable: MEMBERSHIP comes from live
# collection and only the WEIGHT comes from the table, so a stale table
# unbalances a shard and can never lose a test.


def test_the_key_set_is_collection_never_the_timings():
    """A file the timings have never heard of is still sharded; a file they
    remember but collection no longer reports is gone. Both directions."""
    counts = {"tests/test_new.py": 4, "tests/test_known.py": 10}
    timings = {"tests/test_known.py": 30.0, "tests/test_deleted.py": 900.0}
    packed = shard.pack_weights(counts, timings)
    assert set(packed) == set(counts)
    assert packed["tests/test_known.py"] == 30.0


def test_an_unpriced_file_is_estimated_at_the_measured_mean_rate():
    """Not the median. In this suite the median is 0.10 s/test and the mean is
    0.45, because most files are cheap and a few are enormous -- and a new file
    is as likely to be a browser module as a static guard."""
    counts = {"tests/test_priced.py": 10, "tests/test_new.py": 4}
    timings = {"tests/test_priced.py": 20.0}
    packed = shard.pack_weights(counts, timings)
    assert packed["tests/test_new.py"] == pytest.approx(4 * 2.0)


def test_with_no_timings_at_all_the_weight_falls_back_to_test_count():
    """Worse balance is not a broken gate. A splitter that refused to run
    without a measurement would take CI down over a tuning parameter."""
    counts = {"tests/test_a.py": 3, "tests/test_b.py": 7}
    assert shard.pack_weights(counts, {}) == {
        "tests/test_a.py": 3.0,
        "tests/test_b.py": 7.0,
    }


def test_a_missing_timings_file_reads_as_no_timings(tmp_path):
    assert shard.load_timings(tmp_path / "not-here.json") == {}


def test_the_committed_timings_are_a_measurement_of_this_repository():
    """The table ships with provenance or it does not ship: seconds with no
    commit, machine or date against them cannot be judged stale by whoever
    finds them next. And every path in it must LOOK like a test file, or the
    table is measuring something else."""
    document = json.loads(
        (REPO / "scripts" / "ci_shard_timings.json").read_text(encoding="utf-8")
    )
    assert document["_measured"].strip(), document
    seconds = document["seconds"]
    assert len(seconds) == document["_files"]
    assert all(name.startswith("tests/") and name.endswith(".py") for name in seconds)
    assert all(value > 0 for value in seconds.values())
    assert round(sum(seconds.values()), 1) == pytest.approx(
        document["_total_seconds"], abs=0.5
    )


def test_the_timings_table_still_prices_most_of_the_suite():
    """A table that has fallen behind the suite is fine; a table that prices
    almost none of it is a table nobody regenerated, and the split silently
    degrades to test counts. Two thirds is the line: below it, the balance
    claim in scripts/ci_shard.py's docstring is no longer about this suite.
    """
    priced = set(shard.load_timings())
    live = {path.name for path in (REPO / "tests").glob("test_*.py")}
    covered = {name for name in priced if name.split("/")[-1] in live}
    assert len(covered) >= 2 * len(live) / 3, (len(covered), len(live))


def test_writing_timings_without_provenance_is_refused(tmp_path):
    collected = tmp_path / "collected.txt"
    collected.write_text(SAMPLE, encoding="utf-8")
    junit = tmp_path / "junit.xml"
    junit.write_text(MIXED_JUNIT, encoding="utf-8")
    written = _run(
        REPO / "scripts" / "ci_shard.py",
        "--write-timings", junit, "--collected", collected,
    )
    assert written.returncode != 0
    assert "--label" in written.stderr


# ---------------------------------------------------------------------------
# Reading pytest's collection output
# ---------------------------------------------------------------------------

#: A realistic sample. Every awkward shape in it is one this suite actually
#: produces: a parameter holding a PATH, a parameter holding SPACES, a
#: parameter holding a COLON, and a warnings block whose lines look enough like
#: node ids to fool a looser reader.
#:
#: The colon-bearing parameter is a TIMESTAMP rather than the urn this suite
#: more often parametrises over, and the warning's path is relative rather than
#: the runner's absolute one. Both were the realistic spelling first and both
#: were changed because scripts/identity_gate.py refused them -- correctly: an
#: exact allowlist has no way to know a urn was invented for a docstring, and a
#: guard that has to be argued with costs more than a sample that argues for
#: itself. Neither shape is what this sample is testing.
SAMPLE = """\
tests/test_auth.py::test_login
tests/test_auth.py::test_logout
tests/test_no_committed_credential.py::test_file[tests/fixtures/a.html]
tests/test_no_committed_credential.py::test_file[scripts/ci_shard.py]
tests/test_prose.py::test_claim[the docstring says five and it is six]
tests/test_shape.py::test_deadline[2026-09-05 11:04:07]

=============================== warnings summary ===============================
tests/test_auth.py:12
  tests/test_auth.py:12: UserWarning: x
    warnings.warn("x")

6 tests collected in 0.42s
"""


def test_the_collection_parse_counts_each_file():
    counts = shard.parse_collected(SAMPLE)
    assert counts == {
        "tests/test_auth.py": 2,
        "tests/test_no_committed_credential.py": 2,
        "tests/test_prose.py": 1,
        "tests/test_shape.py": 1,
    }


def test_the_parse_refuses_output_that_does_not_reconcile():
    """The control that matters most, because its absence is invisible.

    Every way the parse could under-read produces a tidy partition OF THE WRONG
    SET -- and a partition test cannot see it, because the set it partitions is
    the set the parse handed it. Only pytest's own total can.
    """
    with pytest.raises(SystemExit) as raised:
        shard.parse_collected(SAMPLE.replace("6 tests collected", "9 tests collected"))
    assert "collection says 9" in str(raised.value)


def test_the_parse_refuses_output_with_no_total():
    with pytest.raises(SystemExit) as raised:
        shard.parse_collected("tests/test_auth.py::test_login\n")
    assert "no 'N tests collected' line" in str(raised.value)


def test_the_parse_refuses_a_collection_that_errored():
    """A module that failed to import is a file with no tests, and sharding
    that list drops every test in it with no shard able to report a gap."""
    with pytest.raises(SystemExit) as raised:
        shard.parse_collected(
            "tests/test_auth.py::test_login\n\n1 test collected, 3 errors in 0.4s\n"
        )
    assert "3 error" in str(raised.value)


def test_the_parse_reads_a_windows_run_the_same_way():
    """Node ids are posix on both platforms; a backslash would mean the split
    was made from a path pytest never printed."""
    counts = shard.parse_collected(SAMPLE)
    assert not any("\\" in path for path in counts)


# ---------------------------------------------------------------------------
# The cross-shard totals guard, shown failing four ways
# ---------------------------------------------------------------------------

CELLS = [
    {"os": "ubuntu-latest", "python-version": "3.13"},
    {"os": "windows-latest", "python-version": "3.13"},
]
LABELS = [totals.cell_label(cell) for cell in CELLS]


def reports_for(of: int = 3, collected: int = 300) -> list[dict]:
    """One complete, honest set: every cell, every shard, nothing skipped."""
    per_shard = collected // of
    return [
        {
            "cell": label,
            "index": index,
            "of": of,
            "collected_total": collected,
            "shard_expected": per_shard,
            "ran": per_shard,
            "skipped": 0,
            "failures": 0,
            "errors": 0,
        }
        for label in LABELS
        for index in range(of)
    ]


def test_a_complete_set_of_reports_passes():
    """THE CONTROL FOR THE CONTROLS, again. Without it, a guard that refused
    every run would satisfy all four failures below."""
    assert totals.problems_in(reports_for(), LABELS, 3) == []


def test_a_missing_shard_is_caught_and_named():
    """THE CASE THE WHOLE FILE EXISTS FOR. A cancelled shard leaves no
    artifact, and every artifact that DID arrive reconciles perfectly."""
    reports = [report for report in reports_for() if report["index"] != 1]
    problems = totals.problems_in(reports, LABELS, 3)

    # Both cells lost shard 1, and each says so by INDEX. A message that only
    # said "a shard is missing" would send somebody to read six job logs.
    named = [problem for problem in problems if "reported NOTHING" in problem]
    assert len(named) == len(LABELS), problems
    assert all("[1]" in problem for problem in named), named
    assert {label for label in LABELS if any(label in p for p in named)} == set(LABELS)

    # And the arithmetic catches it a second, independent way: the shards that
    # DID report ran 200 of the 300 tests the cell collected. Either detection
    # alone would do; having both means a message somebody softens later does
    # not silently take the gate with it.
    assert sum("a gap of 100" in problem for problem in problems) == len(LABELS), problems


def test_a_duplicated_shard_is_caught():
    reports = reports_for()
    reports.append(dict(reports[0]))
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("more than once" in problem for problem in problems), problems


def test_a_short_total_is_caught_with_the_size_of_the_gap():
    """Every shard reported; together they ran 40 fewer tests than the cell
    collected. Nothing inside any single shard's numbers is wrong."""
    reports = reports_for()
    reports[0]["ran"] -= 40
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("a gap of 40" in problem for problem in problems), problems


def test_skipped_tests_do_not_pass_as_executed():
    """junit's ``tests`` attribute counts skips, so a guard that compared only
    that number would wave through a run where a shard executed nothing."""
    reports = reports_for()
    reports[0]["skipped"] = 40
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("SKIPPED" in problem for problem in problems), problems
    assert any("a gap of 40" in problem for problem in problems), problems


def test_the_totals_job_names_the_skipped_tests_across_every_shard():
    """The one place the whole picture exists. Each shard log holds its own
    skips; a reader hunting four of them across eighteen jobs is doing by hand
    what one line can do."""
    reports = reports_for()
    reports[0] = dict(
        reports[0], skipped=1, skipped_tests=["tests.test_uploads::test_a_symlink"]
    )
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("tests.test_uploads::test_a_symlink" in p for p in problems), problems


def test_a_cell_that_reported_nothing_at_all_is_caught():
    """Not a missing shard -- a missing CELL. If the matrix loses a leg, every
    report present still reconciles."""
    reports = [report for report in reports_for() if report["cell"] != LABELS[1]]
    problems = totals.problems_in(reports, LABELS, 3)
    assert any(LABELS[1] in problem and "[0, 1, 2]" in problem for problem in problems), problems


def test_a_report_from_an_unexpected_cell_is_caught():
    reports = reports_for()
    reports[0] = dict(reports[0], cell="macos-latest py3.13")
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("not one of the" in problem for problem in problems), problems


def test_shards_disagreeing_about_the_denominator_is_caught():
    """Two shards of one cell reporting different collected totals cannot both
    be right, and summing against either would be summing against a guess."""
    reports = reports_for()
    reports[0]["collected_total"] = 299
    problems = totals.problems_in(reports, LABELS, 3)
    assert any("disagree about how many tests" in problem for problem in problems), problems


def test_a_cell_without_os_and_python_cannot_be_labelled():
    with pytest.raises(SystemExit) as raised:
        totals.cell_label({"os": "ubuntu-latest"})
    assert "python-version" in str(raised.value)


# ---------------------------------------------------------------------------
# The two scripts, end to end, through their command lines
# ---------------------------------------------------------------------------

JUNIT = """\
<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" errors="0" failures="0" skipped="0"
 tests="{tests}" time="1.0"><testcase classname="tests.test_x" name="test_y"
 file="tests/test_x.py" time="0.1"/></testsuite></testsuites>
"""


def _run(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *[str(arg) for arg in args]],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def _shard_files(tmp_path, index, ran, collected=300, of=2):
    """One shard's plan and junit, as the workflow's two steps would leave
    them, then recorded through the real command line."""
    plan = tmp_path / f"plan-{index}.json"
    plan.write_text(
        json.dumps(
            {
                "index": index,
                "of": of,
                "files": ["tests/test_x.py"],
                "tests": collected // of,
                "collected_total": collected,
                "files_total": 2,
            }
        ),
        encoding="utf-8",
    )
    junit = tmp_path / f"junit-{index}.xml"
    junit.write_text(JUNIT.format(tests=ran), encoding="utf-8")
    return plan, junit


def test_record_writes_what_verify_reads(tmp_path):
    """The seam where two scripts drift: one writes a field, the other reads a
    different one, and both files look correct on their own."""
    reports = tmp_path / "reports"
    cell = json.dumps({"os": "ubuntu-latest", "python-version": "3.13"})
    for index in (0, 1):
        plan, junit = _shard_files(tmp_path, index, ran=150)
        written = _run(
            REPO / "scripts" / "ci_shard_totals.py", "record",
            "--plan", plan, "--junit", junit, "--cell", cell,
            "--out", reports / f"ubuntu-{index}.json",
        )
        assert written.returncode == 0, written.stderr

    checked = _run(
        REPO / "scripts" / "ci_shard_totals.py", "verify",
        "--reports", reports, "--of", "2", "--cells", json.dumps([json.loads(cell)]),
    )
    assert checked.returncode == 0, checked.stderr + checked.stdout
    assert "OK: every one of 1 cell" in checked.stdout


def test_verify_goes_red_when_a_shard_artifact_never_arrives(tmp_path):
    """SHOWN FAILING THROUGH THE COMMAND LINE, which is how CI calls it. The
    surviving shard's report is perfect; the run is still incomplete."""
    reports = tmp_path / "reports"
    cell = json.dumps({"os": "ubuntu-latest", "python-version": "3.13"})
    plan, junit = _shard_files(tmp_path, 0, ran=150)
    _run(
        REPO / "scripts" / "ci_shard_totals.py", "record",
        "--plan", plan, "--junit", junit, "--cell", cell,
        "--out", reports / "ubuntu-0.json",
    )

    checked = _run(
        REPO / "scripts" / "ci_shard_totals.py", "verify",
        "--reports", reports, "--of", "2", "--cells", json.dumps([json.loads(cell)]),
    )
    assert checked.returncode == 1, checked.stdout
    assert "shard(s) [1] reported NOTHING" in checked.stderr


def test_verify_goes_red_when_a_shard_ran_fewer_tests_than_it_collected(tmp_path):
    """Both artifacts arrive; one of them ran 30 tests short."""
    reports = tmp_path / "reports"
    cell = json.dumps({"os": "ubuntu-latest", "python-version": "3.13"})
    for index, ran in ((0, 150), (1, 120)):
        plan, junit = _shard_files(tmp_path, index, ran=ran)
        _run(
            REPO / "scripts" / "ci_shard_totals.py", "record",
            "--plan", plan, "--junit", junit, "--cell", cell,
            "--out", reports / f"ubuntu-{index}.json",
        )

    checked = _run(
        REPO / "scripts" / "ci_shard_totals.py", "verify",
        "--reports", reports, "--of", "2", "--cells", json.dumps([json.loads(cell)]),
    )
    assert checked.returncode == 1, checked.stdout
    assert "a gap of 30" in checked.stderr


def test_the_splitter_command_line_prints_one_file_per_line(tmp_path):
    collected = tmp_path / "collected.txt"
    collected.write_text(SAMPLE, encoding="utf-8")
    listed = _run(
        REPO / "scripts" / "ci_shard.py",
        "--index", "0", "--of", "2", "--collected", collected,
    )
    assert listed.returncode == 0, listed.stderr
    printed = listed.stdout.split()
    assert printed and all(name.endswith(".py") for name in printed), listed.stdout

    other = _run(
        REPO / "scripts" / "ci_shard.py",
        "--index", "1", "--of", "2", "--collected", collected,
    )
    assert set(printed).isdisjoint(other.stdout.split())
    assert set(printed) | set(other.stdout.split()) == set(
        shard.parse_collected(SAMPLE)
    )


def test_the_file_list_is_newline_separated_with_no_carriage_returns(tmp_path):
    """A Windows-only break that no Linux runner could ever show.

    The workflow reads this list back with ``$(cat shard-files.txt)``. Git Bash
    splits on IFS -- space, tab, newline -- and a carriage return is none of
    those, so Python's text mode on the Windows cell would hand pytest
    ``tests/test_auth.py\\r`` and it would report the file as missing. Captured
    as BYTES on purpose: ``text=True`` translates line endings and would hide
    exactly the character being asserted about.
    """
    collected = tmp_path / "collected.txt"
    collected.write_text(SAMPLE, encoding="utf-8")
    listed = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "ci_shard.py"),
            "--index", "0", "--of", "2", "--collected", str(collected),
        ],
        capture_output=True,
        cwd=REPO,
    )
    assert listed.returncode == 0, listed.stderr
    assert b"\r" not in listed.stdout, listed.stdout


# ---------------------------------------------------------------------------
# An xfail is not a skip -- the correction of 2026-09-05
# ---------------------------------------------------------------------------
#
# MEASURED, NOT SUPPOSED. A full serial run of this suite in a clean clone of
# e0dc8f9 finished "3655 passed, 4 skipped, 1 xfailed" -- and
# scripts/ci_full_run_check.py exited 1 reporting FIVE skips. junit writes one
# <skipped> element for both outcomes and separates them only by ``type``,
# while the ``skipped=`` attribute adds them together. The one xfail is
# tests/test_click_is_not_its_own_evidence.py's deliberate
# ``xfail(strict=True)`` over a known defect, so every cell of the matrix would
# have gone red on the first run this workflow ever had, for a marker doing
# exactly its job.

MIXED_JUNIT = """\
<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" errors="0" failures="0" skipped="2" tests="4">
<testcase classname="tests.test_a" name="test_passes" time="0.1"/>
<testcase classname="tests.test_a" name="test_also_passes" time="0.1"/>
<testcase classname="tests.test_b" name="test_could_not_run" time="0.0">
  <skipped type="pytest.skip" message="no symlink privilege here">reason</skipped>
</testcase>
<testcase classname="tests.test_c" name="test_known_defect" time="0.2">
  <skipped type="pytest.xfail" message="KNOWN DEFECT, recorded on purpose">x</skipped>
</testcase>
</testsuite></testsuites>
"""

ONLY_XFAIL_JUNIT = MIXED_JUNIT.replace('skipped="2"', 'skipped="1"').replace(
    """<testcase classname="tests.test_b" name="test_could_not_run" time="0.0">
  <skipped type="pytest.skip" message="no symlink privilege here">reason</skipped>
</testcase>
""",
    "",
).replace('tests="4"', 'tests="3"')


@pytest.mark.parametrize("script", ["totals", "full_run"])
def test_both_guards_count_an_xfail_apart_from_a_skip(script, tmp_path):
    """The same rule in two files, so both are shown holding it."""
    junit = tmp_path / "junit.xml"
    junit.write_text(MIXED_JUNIT, encoding="utf-8")
    module = {"totals": totals, "full_run": full_run}[script]
    counted = module.junit_totals(str(junit))
    assert counted["skipped"] == 1, counted
    assert counted["xfailed"] == 1, counted
    assert counted["tests"] == 4, counted


@pytest.mark.parametrize("script", ["totals", "full_run"])
def test_both_guards_refuse_a_report_whose_two_skip_counts_disagree(script, tmp_path):
    """The attribute is kept as a cross-check, not discarded.

    If the elements and the attribute disagree, this is not the report shape
    either number was read off, and choosing one would be certifying
    arithmetic rather than a run.
    """
    junit = tmp_path / "junit.xml"
    junit.write_text(MIXED_JUNIT.replace('skipped="2"', 'skipped="7"'), encoding="utf-8")
    module = {"totals": totals, "full_run": full_run}[script]
    with pytest.raises(SystemExit) as raised:
        module.junit_totals(str(junit))
    assert "skipped=7" in str(raised.value)


def test_the_full_run_check_passes_a_run_whose_only_skip_is_an_xfail(tmp_path):
    """THE REGRESSION, END TO END. This exact input exited 1 before the fix."""
    junit = tmp_path / "junit.xml"
    junit.write_text(ONLY_XFAIL_JUNIT, encoding="utf-8")
    collected = tmp_path / "collected.txt"
    collected.write_text("3 tests collected in 0.1s\n", encoding="utf-8")

    checked = _run(REPO / "scripts" / "ci_full_run_check.py", collected, junit)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "xfailed 1" in checked.stdout
    assert "skipped 0" in checked.stdout


def test_the_full_run_check_still_refuses_a_real_skip(tmp_path):
    """THE CONTROL FOR THAT CONTROL. Softening the xfail case must not soften
    the case the check exists for -- a test that decided it could not run."""
    junit = tmp_path / "junit.xml"
    junit.write_text(MIXED_JUNIT, encoding="utf-8")
    collected = tmp_path / "collected.txt"
    collected.write_text("4 tests collected in 0.1s\n", encoding="utf-8")

    checked = _run(REPO / "scripts" / "ci_full_run_check.py", collected, junit)
    assert checked.returncode == 1, checked.stderr
    assert "1 test(s) SKIPPED" in checked.stderr

    # AND IT NAMES THE TEST. "4 skipped, run with -rs to see which" asks the
    # reader to re-run a 27-minute suite for something the report in front of
    # them already holds -- and on a sharded run, to find which of eighteen
    # jobs held it. The xfail must NOT be in that list.
    assert "tests.test_b::test_could_not_run" in checked.stderr
    assert "test_known_defect" not in checked.stderr


# ---------------------------------------------------------------------------
# Declared skips: the gate has to be able to PASS
# ---------------------------------------------------------------------------
#
# tests/test_no_committed_identity.py's exact-value sweep needs
# _audit/_sanitisation_key.json, which is gitignored on purpose and must never
# reach a public runner. It skips in every clone, so the zero-skip rule made a
# gate that could never pass on any cell -- which is the failure this
# repository names in the first sentence of
# tests/test_prose_that_makes_a_claim.py. scripts/ci_expected_skips.json is the
# narrow answer: a skip passes only if somebody wrote down why it is
# structural, and everything else still fails, by name.


def test_the_declaration_file_is_a_reason_and_not_just_a_list():
    """An allowlist entry with no argument behind it is how a tolerated skip
    outlives the thing that made it necessary."""
    document = json.loads(
        (REPO / "scripts" / "ci_expected_skips.json").read_text(encoding="utf-8")
    )
    assert document["_why"].strip() and document["_measured"].strip()
    assert document["expected"], "an empty declaration should be no file at all"
    for test_id, reason in document["expected"].items():
        assert "::" in test_id, test_id
        assert len(reason) > 80, (test_id, reason)


def test_both_guards_read_the_same_declaration_file():
    """One file, two readers. The per-shard check and the cross-shard sum have
    to agree about which skips are structural, and the cheapest way for two
    guards to agree is for there to be nothing to disagree about."""
    assert totals.expected_skips() == full_run.expected_skips()
    assert totals.expected_skips(), "the repository's own declaration is empty"


@pytest.mark.parametrize("script", ["totals", "full_run"])
def test_a_missing_declaration_file_means_the_strict_original_rule(script, tmp_path):
    """ats-jobs holds a byte-shared copy of ci_full_run_check.py and no such
    file. Absent must mean "no skip is tolerated", never "all are"."""
    module = {"totals": totals, "full_run": full_run}[script]
    absent = tmp_path / "nothing.json"
    assert module.expected_skips(type(module.EXPECTED_SKIPS_PATH)(absent)) == {}


def test_a_declared_skip_passes_the_per_shard_gate(tmp_path):
    """CAN-IT-PASS, which for this gate is the property in doubt."""
    junit = tmp_path / "junit.xml"
    declared = sorted(full_run.expected_skips())[0]
    classname, _, name = declared.partition("::")
    junit.write_text(
        MIXED_JUNIT.replace('classname="tests.test_b" name="test_could_not_run"',
                            f'classname="{classname}" name="{name}"'),
        encoding="utf-8",
    )
    collected = tmp_path / "collected.txt"
    collected.write_text("4 tests collected in 0.1s\n", encoding="utf-8")

    checked = _run(REPO / "scripts" / "ci_full_run_check.py", collected, junit)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert "1 declared" in checked.stdout
    # And it is PRINTED on the green run, because a tolerated skip nobody sees
    # is a tolerated skip that outlives its reason.
    assert f"declared skip: {declared}" in checked.stdout


def test_a_declared_skip_closes_the_cross_shard_arithmetic():
    """The gap is allowed exactly as far as it is EXPLAINED -- not "skips are
    fine now". Every missing test still has to be accounted for."""
    declared = sorted(totals.expected_skips())[0]
    reports = reports_for()
    reports[0] = dict(reports[0], skipped=1, skipped_tests=[declared])
    assert totals.problems_in(reports, LABELS, 3, totals.expected_skips()) == []
    # ... and without the declaration in hand, the same reports are refused.
    assert totals.problems_in(reports, LABELS, 3, {}) != []


def test_an_undeclared_skip_beside_a_declared_one_is_still_refused():
    """THE CONTROL FOR THE TOLERANCE. A list that swallowed its neighbours
    would satisfy the test above and gut the rule."""
    declared = sorted(totals.expected_skips())[0]
    reports = reports_for()
    reports[0] = dict(
        reports[0],
        skipped=2,
        ran=reports[0]["ran"],
        skipped_tests=[declared, "tests.test_uploads::test_a_symlink"],
    )
    problems = totals.problems_in(reports, LABELS, 3, totals.expected_skips())
    assert any("test_a_symlink" in problem for problem in problems), problems
    assert not any(declared in problem for problem in problems), problems


def test_skips_that_no_report_names_cannot_be_matched_and_are_refused():
    """A count with no observations behind it cannot be checked against the
    declaration at all, so it is refused rather than assumed innocent."""
    reports = reports_for()
    reports[0] = dict(reports[0], skipped=1)
    reports[0].pop("skipped_tests", None)
    problems = totals.problems_in(reports, LABELS, 3, totals.expected_skips())
    assert any("do not name them" in problem for problem in problems), problems


def test_a_shard_report_carries_the_xfail_count_separately(tmp_path):
    """The totals job sums ``ran`` minus ``skipped`` per cell. An xfail counted
    as a skip would make every cell short by one and report a completeness gap
    that never happened -- the loudest possible false alarm on the one guard
    that has to be believed."""
    junit = tmp_path / "junit.xml"
    junit.write_text(MIXED_JUNIT, encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {"index": 0, "of": 1, "files": ["tests/test_a.py"], "tests": 4,
             "collected_total": 4, "files_total": 1}
        ),
        encoding="utf-8",
    )
    out = tmp_path / "report.json"
    recorded = _run(
        REPO / "scripts" / "ci_shard_totals.py", "record",
        "--plan", plan, "--junit", junit,
        "--cell", json.dumps({"os": "ubuntu-latest", "python-version": "3.13"}),
        "--out", out,
    )
    assert recorded.returncode == 0, recorded.stderr
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["skipped"] == 1 and report["xfailed"] == 1, report

    # And the sum a cell is judged on: 4 reported, 1 genuinely skipped, so 3
    # executed against 4 collected -- the skip is a gap and the xfail is not.
    problems = totals.problems_in([report], [report["cell"]], 1)
    assert any("a gap of 1" in problem for problem in problems), problems
