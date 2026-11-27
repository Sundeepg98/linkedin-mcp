"""``scripts/lane_ci.py``: ref naming, the refusals before a push, and the
reading of a CI run -- with no network and no remote anywhere.

The push and the gh calls are the only parts that touch GitHub, and both are
injected or monkeypatched here: ``cmd_push`` takes the pusher, ``cmd_clean``
takes the pusher, and ``cmd_wait`` reads ``_git``/``_gh``/``sleep``/``clock``
through names this file replaces. A test that ran the real ``gh`` would be a
test of the account's rate limit.

The refusal tests run on SYNTHETIC repositories in tmp dirs, with the
shipped identity sweep reading a synthetic one-value wordlist, the same
arrangement as ``tests/test_pre_push_ci_refs.py``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

PLANTED = "Quorvexindale Plimbury"  # invented; names no one

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}


def _load(name: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(f"{name}_under_test",
                                                  SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lane = _load("lane_ci")


# ---------------------------------------------------------------------------
# Ref naming and the remote
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("branch, ref", [
    ("worktree-agent-a1b2c3", "refs/heads/ci/worktree-agent-a1b2c3"),
    ("lane/fast", "refs/heads/ci/lane/fast"),
])
def test_a_branch_names_its_ci_ref(branch, ref):
    assert lane.ci_ref_for(branch) == ref


@pytest.mark.parametrize("branch", ["", "HEAD", "two words", "a..b", ".hidden",
                                    "x/.y", "ends.lock"])
def test_a_branch_the_gate_would_refuse_is_refused_here_first(branch):
    with pytest.raises(ValueError):
        lane.ci_ref_for(branch)


@pytest.mark.parametrize("url", [
    "https://github.com/owner-x/repo-y.git",
    "https://github.com/owner-x/repo-y",
    "ssh://github.com/owner-x/repo-y.git",
])
def test_the_repo_slug_comes_from_the_remote(url):
    assert lane.slug_from_url(url) == "owner-x/repo-y"


def test_a_remote_that_is_not_github_is_refused():
    with pytest.raises(ValueError):
        lane.slug_from_url("https://example.com/owner/repo.git")


# ---------------------------------------------------------------------------
# Finding the run BY SHA, and reading it
# ---------------------------------------------------------------------------

SHA = "a" * 40
OTHER = "b" * 40


def _r(i, sha=SHA, branch="ci/lane", event="push", created="2026-10-10T06:00:00Z"):
    return {"databaseId": i, "headSha": sha, "headBranch": branch, "event": event,
            "createdAt": created, "status": "completed", "conclusion": "success"}


def test_a_run_of_another_sha_is_never_the_run():
    assert lane.choose_run([_r(1, sha=OTHER)], SHA, "lane") is None


def test_masters_run_of_the_same_sha_is_never_the_run():
    """After the merge, master's full-matrix run carries the SAME head sha."""
    got = lane.choose_run([_r(1, branch="master"), _r(2, event="pull_request")],
                          SHA, "lane")
    assert got is None


def test_the_exact_ci_branch_wins_and_the_newest_of_it():
    runs = [_r(1, branch="ci/other", created="2026-10-10T07:00:00Z"),
            _r(2, created="2026-10-10T06:00:00Z"),
            _r(3, created="2026-10-10T06:30:00Z")]
    assert lane.choose_run(runs, SHA, "lane")["databaseId"] == 3
    assert lane.choose_run(runs, SHA, None)["databaseId"] == 1


@pytest.mark.parametrize("view, want", [
    ({"status": "queued"}, "pending"),
    ({"status": "in_progress", "conclusion": ""}, "pending"),
    ({"status": "completed", "conclusion": "success"}, "success"),
    ({"status": "completed", "conclusion": "cancelled"}, "cancelled"),
    ({"status": "completed", "conclusion": "failure"}, "failure:failure"),
    ({"status": "completed", "conclusion": "timed_out"}, "failure:timed_out"),
])
def test_the_verdict_comes_from_status_and_conclusion(view, want):
    assert lane.verdict(view) == want


def test_failing_jobs_are_named_and_passing_ones_are_not():
    view = {"jobs": [
        {"name": "shard plan", "conclusion": "success"},
        {"name": "pytest (ubuntu-latest, py3.13, shard 2)", "conclusion": "failure"},
        {"name": "pytest (ubuntu-latest, py3.13, shard 3)", "conclusion": "cancelled"},
        {"name": "every shard reported", "conclusion": "skipped"},
    ]}
    assert lane.failing_jobs(view) == ["pytest (ubuntu-latest, py3.13, shard 2)",
                                       "pytest (ubuntu-latest, py3.13, shard 3)"]


LOG = "\n".join([
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:00.1Z ..........F....",
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:01.1Z "
    "FAILED tests/test_x.py::test_one - AssertionError: assert 1 == 2",
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:01.2Z "
    "FAILED tests/test_x.py::test_one - AssertionError: assert 1 == 2",
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:01.3Z "
    "ERROR tests/test_y.py::test_two - " + "x" * 400,
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:02.0Z "
    "##[error]Process completed with exit code 1.",
    "pytest (shard 2)\tRun this shard\t2026-10-10T06:01:02.1Z 1 failed, 600 passed",
])


def test_the_first_failing_lines_are_cut_deduplicated_and_truncated():
    got = lane.first_failing_lines(LOG, limit=20, width=80)
    assert got[0] == "FAILED tests/test_x.py::test_one - AssertionError: assert 1 == 2"
    assert len(got) == 3, got  # the duplicate collapsed; dots and totals dropped
    assert got[1].startswith("ERROR tests/test_y.py::test_two") and len(got[1]) == 80
    assert got[2].startswith("##[error]")
    assert lane.first_failing_lines(LOG, limit=1, width=80) == got[:1]


def test_the_wall_clock_comes_from_the_runs_own_timestamps():
    view = {"startedAt": "2026-10-10T06:00:00Z", "updatedAt": "2026-10-10T06:05:03Z"}
    assert lane.elapsed(view) == "5m03s"
    assert lane.elapsed({}) == "unknown"


# ---------------------------------------------------------------------------
# The SHARPEST RED RUN THIS REPOSITORY HAS GOTTEN (2026-10-26)
# ---------------------------------------------------------------------------
#
# CI runs the suite with ``-q -rs`` -- NOT ``-rf``. A real ``--log-failed``
# dump therefore carries NO ``FAILED tests/...::test`` lines at all. The
# failing test id rides three other lines:
#
#   * the sub-banner ``______ test_name ______`` that opens each FAILURES block,
#   * the FIRST ``E       AssertionError: ...`` line -- the message --
#   * the ``tests/file.py:NNN: Reason`` reference line that closes it.
#
# The shape below is the ACTUAL ``gh run view <run> --log-failed`` text of a
# red lane run, transcribed verbatim for the classes that matter. Before the
# fix, ``first_failing_lines`` returned exactly ONE line from this log --
# ``##[error]Process completed with exit code 1.`` -- so a red run told
# nobody WHICH test had failed. Those two assertions below are the red:
# they go straight through the unpatched extractor.


_L = "pytest (ubuntu-latest, py3.13, shard 0)\tRun this shard\t"
_TS = "2026-10-10T14:42:45.68"


def _gh_line(ts_suffix: str, body: str) -> str:
    return f"{_L}{_TS}{ts_suffix}Z {body}"


LOG_RS = "\n".join([
    # passing progress lines -- every class must drop them
    _gh_line("679994", "..........                                                               [100%]"),
    _gh_line("680040", "=================================== FAILURES =================================="),
    _gh_line("680077", "____________________ test_no_new_unresolvable_citation_appears ____________________"),
    _gh_line("680118", "[gw2] linux -- Python 3.13.16"),
    _gh_line("680141", ""),
    _gh_line("680199", "measured = ([Site(token='063c9b7', doc='_audit/x.md', line=375, verdict='UNRESOLVED')])"),
    _gh_line("680502", "    "),
    _gh_line("680519", ">       assert not appeared, ("),
    _gh_line("680548", "            f\"NEW unresolvable SHA citation(s): {appeared}.\""),
    _gh_line("680905", "E       AssertionError: NEW unresolvable SHA citation(s): [('0f7e6d0', '_audit/2026-10-10-integration.md', 1)]"),
    _gh_line("681017", "E       assert not [('0f7e6d0', '_audit/2026-10-10-integration.md', 1)]"),
    _gh_line("681037", ""),
    _gh_line("681049", "tests/test_a_cited_sha_resolves.py:779: AssertionError"),
    _gh_line("681080", "=========================== short test summary info ==========================="),
    _gh_line("681120", "SKIPPED [1] tests/test_a_verdict_earns_its_entry.py:298: got empty parameter set"),
    _gh_line("681293", "1 failed, 3389 passed, 4 skipped in 203.96s (0:03:23)"),
    _gh_line("924700", "##[error]Process completed with exit code 1."),
])


def test_the_rs_log_yields_the_failing_test_id_not_just_the_exit_banner():
    """RED BEFORE THE FIX. The unpatched extractor finds no class in the
    sub-banner, in the E lines or in the reference line, so of these sixteen
    lines it prints one -- the process banner. The test name and the file
    reference are the whole point of pulling this log at all."""
    got = lane.first_failing_lines(LOG_RS, limit=20, width=220)
    assert "test_no_new_unresolvable_citation_appears" in " | ".join(got), got
    assert "tests/test_a_cited_sha_resolves.py:779" in " | ".join(got), got


def test_the_second_failure_block_keeps_its_own_identity_lines():
    """Two FAILURES blocks: dedup is per-text, so the second block's
    sub-banner and reference line must still be shown even when its E line
    repeats the first block's. Identifying WHICH test failed is the point;
    one suppressed E line is not a loss of that."""
    log = "\n".join([
        _gh_line("000100", "____________________ test_alpha ____________________"),
        _gh_line("000200", "E       AssertionError: a went wrong"),
        _gh_line("000300", "tests/test_a.py:10: AssertionError"),
        _gh_line("000500", "____________________ test_beta ____________________"),
        _gh_line("000600", "E       AssertionError: a went wrong"),
        _gh_line("000700", "tests/test_b.py:20: AssertionError"),
        _gh_line("000800", "##[error]Process completed with exit code 1."),
    ])
    got = lane.first_failing_lines(log, limit=20, width=220)
    joined = " | ".join(got)
    assert "test_alpha" in joined and "test_beta" in joined, got
    assert "tests/test_b.py:20" in joined, got
    # the repeated E line collapses; both identity lines survive
    assert got.count("E       AssertionError: a went wrong") == 1, got


def test_a_green_log_yields_nothing_not_a_silent_banner_only_section():
    """The negative control. A passing shard's log has no failing class at
    all -- and the section must SAY so rather than print nothing. No
    annotation, no E line, no reference, no FAILED id."""
    GREEN = "\n".join([
        _gh_line("000100", ".................................................................... [100%]"),
        _gh_line("000200", "400 passed in 12.34s"),
    ])
    got = lane.first_failing_lines(GREEN, limit=20, width=220)
    assert got == [], got


def test_the_original_failed_line_shape_still_reads():
    """The ``-rf``-style log the first test file was built on: classes that
    already worked keep working. This is the non-regression half of the
    fix -- the banner and E and reference are ADDITIONS, not replacements."""
    got = lane.first_failing_lines(LOG, limit=20, width=220)
    assert "FAILED tests/test_x.py::test_one" in " | ".join(got), got
    assert "ERROR tests/test_y.py::test_two" in " | ".join(got), got
    assert "##[error]" in " | ".join(got), got


# ---------------------------------------------------------------------------
# A FOUR-FAILURE red run, and a cap that hid one of them (2026-11-25)
# ---------------------------------------------------------------------------
#
# The first live red run the fixed extractor ever read (lane run 40371662148,
# 2026-10-26, two failed shards) had FOUR failing tests. ``wait`` named three:
# the detail view keeps every ``E`` line and every ``tests/...:NNN`` traceback
# frame, so its 20-line cap ran out one block early. The id list is the half
# of the report a reader acts on, so it is extracted on its own and is never
# subject to that cap.
#
# LOG_RS4 is that run's ``--log-failed`` line SHAPES, in their order, two
# shards: every class-bearing line is transcribed, message bodies shortened,
# and a synthetic job id and an object address dropped. The two TRACEBACK
# SEPARATORS (``_ _ _ ... _``, 79 characters, its lines 83 and 97) are in too:
# the first transcription copied only lines the old pattern matched, missed
# them, and so could not see a widened banner pattern take one for a test.


def _job_line(shard: int, body: str) -> str:
    return (f"pytest (ubuntu-latest, py3.13, shard {shard})\tRun this shard\t"
            f"2026-10-26T17:51:00.0000000Z {body}")


FRAME_SEPARATOR = " ".join(["_"] * 40)

LOG_RS4 = "\n".join([
    _job_line(0, "=" * 35 + " FAILURES " + "=" * 35),
    _job_line(0, "______________ test_the_two_receipts_do_not_print_the_same_place _______________"),
    _job_line(0, "    async def test_the_two_receipts_do_not_print_the_same_place("),
    _job_line(0, "tests/test_verification_that_could_not_read.py:394: "),
    _job_line(0, FRAME_SEPARATOR),
    _job_line(0, "tests/test_verification_that_could_not_read.py:211: in _receipt_with_the_read_withheld"),
    _job_line(0, "tests/test_writes.py:1989: in _granted"),
    _job_line(0, "tests/test_writes.py:283: in _gate"),
    _job_line(0, FRAME_SEPARATOR),
    _job_line(0, "E           linkedin_server.errors.WriteAttemptError: refusing to render a confirm gate"),
    _job_line(0, "=" * 27 + " short test summary info " + "=" * 28),
    _job_line(0, "SKIPPED [1] tests/test_sweep_blobs_refuses_a_vacuous_pass.py:339: THE POSITIVE "
                 "CONTROL DID NOT RUN -- never present on CI. The REFUSAL stands."),
    _job_line(0, "##[error]Process completed with exit code 1."),
    _job_line(1, "=" * 35 + " FAILURES " + "=" * 35),
    _job_line(1, "______________________ test_an_apply_now_reaches_the_gate ______________________"),
    _job_line(1, "    The gate is replaced by a recorder that REFUSES, so nothing beyond the"),
    _job_line(1, "E       AssertionError: an apply did not reach the apply gate."),
    _job_line(1, "E       assert 0 == 1"),
    _job_line(1, "E        +  where 0 = len([])"),
    _job_line(1, "tests/test_apply_modal_fixture.py:869: AssertionError"),
    _job_line(1, "_______________ test_a_proceeding_gate_appends_the_second_click ________________"),
    _job_line(1, "E       AssertionError: the gate said proceed and no second click was attempted"),
    _job_line(1, "E       assert (0 == 1)"),
    _job_line(1, "E        +  where 0 = <built-in method count>('#no-such-control-this-test-invented')"),
    _job_line(1, "E        +    where <built-in method count> = ['a[aria-label^=\"Apply\"]'].count"),
    _job_line(1, "tests/test_apply_modal_fixture.py:954: AssertionError"),
    _job_line(1, "_______________ test_the_submit_gates_refusal_reaches_the_caller _______________"),
    _job_line(1, "E       AssertionError: {'action': 'apply_job', 'what': 'Submit an application.'}"),
    _job_line(1, "E       assert None is not None"),
    _job_line(1, "tests/test_apply_modal_fixture.py:1270: AssertionError"),
    _job_line(1, "=" * 27 + " short test summary info " + "=" * 28),
    _job_line(1, "##[error]Process completed with exit code 1."),
])

RS4_IDS = [
    "tests/test_verification_that_could_not_read.py::"
    "test_the_two_receipts_do_not_print_the_same_place",
    "tests/test_apply_modal_fixture.py::test_an_apply_now_reaches_the_gate",
    "tests/test_apply_modal_fixture.py::test_a_proceeding_gate_appends_the_second_click",
    "tests/test_apply_modal_fixture.py::test_the_submit_gates_refusal_reaches_the_caller",
]


def test_the_four_failure_fixture_really_crowds_the_detail_cap():
    """A control on the FIXTURE, and it can fail. The detail view alone must
    run out before the fourth block, exactly as it did on the live run; if
    this fixture stops crowding the cap, the id tests below pass for a reason
    that has nothing to do with the id list."""
    detail = " ".join(lane.first_failing_lines(LOG_RS4))
    assert "test_a_proceeding_gate_appends_the_second_click" in detail
    assert "test_the_submit_gates_refusal_reaches_the_caller" not in detail


def test_a_four_failure_log_names_every_failing_test_through_wait(
        monkeypatch, capsys):
    """RED BEFORE THE FIX: ``wait`` printed the detail view alone, and its cap
    hid the fourth failing test -- one fewer than the run had."""
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log=LOG_RS4)
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    missing = [node for node in RS4_IDS if node not in out]
    assert not missing, (missing, out)
    assert "failing tests (4)" in out, out


def test_failing_test_ids_are_node_ids_paired_inside_their_own_block():
    """Each sub-banner pairs with the first ``tests/`` reference INSIDE its own
    block -- the test's own frame -- so the id is one a reader can run."""
    assert lane.failing_test_ids(LOG_RS4) == RS4_IDS


def test_a_traceback_separator_is_neither_a_test_nor_a_detail_line():
    """pytest draws ``_ _ _ ... _`` between the frames of a long traceback. It
    opens no block, and a banner pattern that admits any fill width must still
    refuse it -- caught by running the code over the real log, after the
    transcribed fixture had passed."""
    assert FRAME_SEPARATOR not in lane.first_failing_lines(LOG_RS4)
    assert [n for n in lane.failing_test_ids(LOG_RS4) if n.startswith("_")] == []


def test_failing_test_ids_read_the_rf_shape_and_the_rs_shape_alike():
    assert lane.failing_test_ids(LOG) == ["tests/test_x.py::test_one",
                                         "tests/test_y.py::test_two"]
    assert lane.failing_test_ids(LOG_RS) == [
        "tests/test_a_cited_sha_resolves.py::"
        "test_no_new_unresolvable_citation_appears"]


def test_a_green_log_carries_no_failing_test_id():
    green = "\n".join([
        _gh_line("000100", "........................................ [100%]"),
        _gh_line("000200", "400 passed in 12.34s"),
    ])
    assert lane.failing_test_ids(green) == []


@pytest.mark.parametrize("banner, ref, want", [
    ("TestReader.test_reads[a.b]", "tests/test_t.py:5: AssertionError",
     "tests/test_t.py::TestReader::test_reads[a.b]"),
    ("ERROR at setup of test_z", "tests/test_t.py:9: ", "ERROR at setup of test_z"),
])
def test_a_class_test_and_a_setup_error_keep_their_pytest_shapes(banner, ref, want):
    """A method's banner reads ``Class.test``, its node id ``Class::test``; a
    setup error's banner is a sentence, and pairing it with a path would
    invent a node id that does not exist, so it is kept as written."""
    log = "\n".join([_gh_line("000100", f"________ {banner} ________"),
                     _gh_line("000200", ref)])
    assert lane.failing_test_ids(log) == [want]


def test_the_same_test_failing_in_three_cells_is_one_id():
    """The full matrix runs three cells, so one broken test appears three
    times in ``--log-failed``; it is one failing test."""
    block = [_gh_line("000100", "________ test_alpha ________"),
             _gh_line("000200", "tests/test_a.py:10: AssertionError")]
    assert lane.failing_test_ids("\n".join(block * 3)) == ["tests/test_a.py::test_alpha"]


#: MEASURED, not assumed (2026-11-25, pytest -q -rs at COLUMNS=80, the width
#: CI falls back to): a name too long for the line is padded with ONE
#: underscore a side. This suite has names past 80 characters, and a pattern
#: that wanted four underscores dropped that test from the report entirely.
LONG = ("test_THIS_CONTROL_CAN_FAIL_a_reader_aimed_at_the_badge_carries_"
        "the_screen_reader_copy")
LOG_LONG = "\n".join([
    _gh_line("000100", f"_ {LONG} _"),
    _gh_line("000200", "E       assert 1 == 2"),
    _gh_line("000300", "tests/test_group_members.py:40: AssertionError"),
])


def test_a_long_name_padded_with_one_underscore_is_still_a_failing_test():
    assert lane.failing_test_ids(LOG_LONG) == [f"tests/test_group_members.py::{LONG}"]
    assert f"_ {LONG} _" in lane.first_failing_lines(LOG_LONG)


def test_a_red_log_with_lines_but_no_test_id_says_no_id_was_found(
        monkeypatch, capsys):
    """What the base extractor printed on a real red run: the exit banner and
    two prose lines that only LOOK like failures (a skip reason and a
    docstring, both matched by ``REFUS``). Lines without an id must say no id
    was found, or the banner passes for one."""
    log = "\n".join([
        _gh_line("000100", "SKIPPED [1] tests/test_s.py:3: The REFUSAL stands."),
        _gh_line("000200", "##[error]Process completed with exit code 1."),
    ])
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log=log)
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "no failing test id found" in out.lower(), out


def test_more_failing_tests_than_the_id_limit_says_how_many_it_withheld(
        monkeypatch, capsys):
    """The id list is never cut SILENTLY. Past the limit, the count of what
    was not printed is printed, with where to read the rest."""
    extra = 7
    rows = []
    for i in range(lane.ID_LIMIT + extra):
        rows += [_gh_line("000100", f"________ test_case_{i:03d} ________"),
                 _gh_line("000200", f"tests/test_many.py:{i + 1}: AssertionError")]
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log="\n".join(rows))
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert f"failing tests ({lane.ID_LIMIT + extra})" in out, out
    assert f"... and {extra} more" in out, out
    assert f"test_case_{lane.ID_LIMIT - 1:03d}" in out
    assert f"test_case_{lane.ID_LIMIT:03d}" not in out


# ---------------------------------------------------------------------------
# wait: the polling loop over canned gh answers
# ---------------------------------------------------------------------------


class FakeGh:
    """Canned ``gh`` answers in order; the last one repeats."""

    def __init__(self, lists, views, log=""):
        self.lists, self.views, self.log, self.calls = list(lists), list(views), log, []

    def __call__(self, *args):
        self.calls.append(args)
        if args[:2] == ("run", "list"):
            return 0, json.dumps(self.lists.pop(0) if len(self.lists) > 1
                                 else self.lists[0]), ""
        if "--log-failed" in args:
            return 0, self.log, ""
        answer = self.views.pop(0) if len(self.views) > 1 else self.views[0]
        if isinstance(answer, tuple):
            return answer
        return 0, json.dumps(answer), ""


def _git_for_wait(*args):
    if args[:2] == ("remote", "get-url"):
        return 0, "https://github.com/owner-x/repo-y.git", ""
    if args[:1] == ("symbolic-ref",):
        return 0, "lane", ""
    raise AssertionError(args)


def _wait(monkeypatch, gh, bound=60):
    ticks = iter(range(0, 10_000, 20))
    monkeypatch.setattr(lane, "_git", _git_for_wait)
    monkeypatch.setattr(lane, "_gh", gh)
    return lane.cmd_wait(SHA, poll=20, bound=bound, sleep=lambda s: None,
                         clock=lambda: next(ticks))


DONE_OK = {"status": "completed", "conclusion": "success",
           "startedAt": "2026-10-10T06:00:00Z", "updatedAt": "2026-10-10T06:05:00Z",
           "jobs": [{"name": "j", "status": "completed", "conclusion": "success"}] * 6}
DONE_RED = dict(DONE_OK, conclusion="failure",
                jobs=[{"name": "pytest (ubuntu-latest, py3.13, shard 1)",
                       "status": "completed", "conclusion": "failure"}])


def test_wait_reports_a_green_run_after_polling(monkeypatch, capsys):
    gh = FakeGh(lists=[[], [_r(7)]],
                views=[{"status": "in_progress", "jobs": []}, DONE_OK])
    assert _wait(monkeypatch, gh) == 0
    out = capsys.readouterr().out
    assert "run 7: success  jobs=6  wall=5m00s" in out, out


def test_wait_reports_a_red_run_with_its_failing_lines(monkeypatch, capsys):
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log=LOG)
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "failed job: pytest (ubuntu-latest, py3.13, shard 1)" in out, out
    assert "FAILED tests/test_x.py::test_one" in out, out


def test_a_403_is_not_a_verdict_and_the_bound_ends_it(monkeypatch, capsys):
    """gh run watch exits 0 on a 403; this reads the view, and a failing view
    is NO verdict, held until the bound -- then 2, never 0."""
    gh = FakeGh(lists=[[_r(7)]], views=[(1, "", "HTTP 403: rate limit")])
    assert _wait(monkeypatch, gh, bound=100) == 2
    assert "NO VERDICT" in capsys.readouterr().err


def test_a_run_that_never_appears_is_no_verdict(monkeypatch, capsys):
    gh = FakeGh(lists=[[_r(7, sha=OTHER), _r(8, branch="master")]], views=[{}])
    assert _wait(monkeypatch, gh, bound=100) == 2
    assert "never appeared" in capsys.readouterr().err


def test_a_superseded_run_is_no_verdict_rather_than_a_failure(monkeypatch, capsys):
    gh = FakeGh(lists=[[_r(7)]], views=[dict(DONE_OK, conclusion="cancelled")])
    assert _wait(monkeypatch, gh) == 2


def test_a_red_run_whose_log_has_no_failing_lines_says_so(monkeypatch, capsys):
    """The NEGATIVE CONTROL at the ``wait`` level. A red run whose
    ``--log-failed`` dump carries none of the known failing classes must
    print a ``no failing lines found``-style line, not a silent section.
    A red verdict that shows no test id is the reading that costs the most:
    it looks like the log had nothing when in fact it had something the
    extractor could not name."""
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log="")
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "no failing lines" in out.lower(), out
    assert "run 7: failure:failure" in out, out


def test_a_red_run_whose_log_is_only_progress_lines_says_so(
        monkeypatch, capsys):
    """Same control, log NON-EMPTY but class-free: the progress line and the
    totals line are all there is. The section must still say ``no failing
    lines`` rather than print nothing, and must not pass the banner through
    as though it were a test id."""
    progress_only = "\n".join([
        "pytest (ubuntu-latest, py3.13, shard 0)\tRun this shard\t"
        "2026-10-10T14:42:45.0001234Z .......F......",
        "pytest (ubuntu-latest, py3.13, shard 0)\tRun this shard\t"
        "2026-10-10T14:42:45.0009876Z 1 failed, 3389 passed in 203.96s",
    ])
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log=progress_only)
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "no failing lines" in out.lower(), out


def test_the_rs_log_through_wait_prints_the_failing_test_id(monkeypatch, capsys):
    """The end-to-end half of the fix: a red run whose log is the real
    ``-rs`` shape prints the sub-banner, the first E line and the
    reference line -- the test id, not only the exit-code banner."""
    gh = FakeGh(lists=[[_r(7)]], views=[DONE_RED], log=LOG_RS)
    assert _wait(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "test_no_new_unresolvable_citation_appears" in out, out
    assert "tests/test_a_cited_sha_resolves.py:779" in out, out


# ---------------------------------------------------------------------------
# push and clean: the refusals before anything leaves
# ---------------------------------------------------------------------------


class World:
    def __init__(self, root: Path) -> None:
        self.repo = root / "work"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "master")
        self.base = self.commit({"base.txt": "the published history\n"})
        self.git("update-ref", "refs/remotes/origin/master", self.base)

    def git(self, *args: str) -> str:
        env = dict(os.environ)
        env.update(_GIT_ENV)
        out = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=.nohooks",
             *args], cwd=self.repo, capture_output=True, text=True, env=env,
            timeout=60)
        assert out.returncode == 0, (args, out.stderr)
        return out.stdout.strip()

    def commit(self, files: dict[str, str]) -> str:
        for name, text in files.items():
            (self.repo / name).write_text(text, encoding="utf-8")
            self.git("add", name)
        self.git("commit", "-q", "--no-verify", "-m", "fixture commit")
        return self.git("rev-parse", "HEAD")


@pytest.fixture
def world(tmp_path, monkeypatch):
    w = World(tmp_path)
    key = tmp_path / "synthetic_key.json"
    key.write_text(json.dumps({"synthetic_needles": [PLANTED]}), encoding="utf-8")
    import sweep_tracked_for_identity  # noqa: PLC0415 -- on sys.path via _load
    monkeypatch.setattr(sweep_tracked_for_identity, "KEY_PATH", key)
    for name, value in _GIT_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("GIT_DIR", raising=False)
    monkeypatch.delenv("GIT_WORK_TREE", raising=False)
    monkeypatch.chdir(w.repo)
    monkeypatch.setattr(lane, "hook_gate_knows_ci", lambda path: True)
    return w


def _never(*args):
    raise AssertionError(f"pushed although a refusal was due: {args}")


def test_a_branch_not_descending_from_master_is_refused_before_the_push(
        world, capsys):
    world.git("checkout", "-q", "--orphan", "stray")
    world.git("rm", "-rq", "--cached", ".")
    (world.repo / "base.txt").unlink()
    world.commit({"lane.txt": "a lane's own new work\n"})
    assert lane.cmd_push(pusher=_never) == 1
    assert "NOT an ancestor" in capsys.readouterr().err


def test_a_dirty_tree_is_refused_before_anything_else(world, capsys):
    world.git("checkout", "-q", "-b", "lane")
    world.commit({"lane.txt": "a lane's own new work\n"})
    (world.repo / "forgotten.py").write_text("x = 1\n", encoding="utf-8")
    assert lane.cmd_push(pusher=_never) == 1
    assert "dirty" in capsys.readouterr().err


def test_a_detached_head_is_refused(world, capsys):
    world.git("checkout", "-q", "--detach")
    assert lane.cmd_push(pusher=_never) == 1
    assert "detached" in capsys.readouterr().err


def test_a_main_checkout_gate_that_predates_ci_refs_is_refused(
        world, monkeypatch, capsys):
    monkeypatch.setattr(lane, "hook_gate_knows_ci", lambda path: False)
    world.git("checkout", "-q", "-b", "lane")
    world.commit({"lane.txt": "a lane's own new work\n"})
    assert lane.cmd_push(pusher=_never) == 1
    assert "MAIN checkout" in capsys.readouterr().err


def test_a_clean_lane_branch_is_pushed_to_its_ci_ref_and_the_sha_printed(
        world, capsys):
    """The positive control for the refusals above."""
    world.git("checkout", "-q", "-b", "lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    pushed = []
    assert lane.cmd_push(pusher=lambda s, r: pushed.append((s, r)) or 0) == 0
    assert pushed == [(sha, "refs/heads/ci/lane")]
    assert capsys.readouterr().out.strip().splitlines()[-1] == sha


def test_push_leaves_the_sweep_to_the_hook(world, monkeypatch, capsys):
    """ONE SWEEP PER PUSH. The hook runs the gate's full check, sweep
    included, on every ci/ push; the helper running it first as well paid the
    sweep twice. The helper keeps the cheap clause (ancestry) so a stale
    branch is refused before any network call, and leaves the sweep to the
    hook -- this fails the test if the helper reaches the sweep at all."""
    def no_sweep(rev_range):
        raise AssertionError(f"the helper ran the sweep itself over {rev_range}")
    monkeypatch.setattr(lane.gate, "_sweep", no_sweep)
    world.git("checkout", "-q", "-b", "lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    pushed = []
    assert lane.cmd_push(pusher=lambda s, r: pushed.append((s, r)) or 0) == 0
    assert pushed == [(sha, "refs/heads/ci/lane")]


def test_the_hook_path_still_sweeps(world, monkeypatch):
    """The other half: the gate's own check, as the hook calls it, must still
    reach the sweep -- or "left to the hook" would mean "left to nobody"."""
    calls = []
    monkeypatch.setattr(lane.gate, "_sweep",
                        lambda rev_range: calls.append(rev_range) or (0, ""))
    world.git("checkout", "-q", "-b", "lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    assert lane.gate.git_ci_check(sha) == []
    assert calls == [f"{world.base}..{sha}"], calls


def test_clean_deletes_exactly_the_ci_ref_and_nothing_else():
    seen = []
    assert lane.cmd_clean("lane", pusher=lambda argv: seen.append(argv) or 0) == 0
    assert seen == [["git", "push", "--no-follow-tags", "origin", ":refs/heads/ci/lane"]]
    assert lane.cmd_clean("HEAD", pusher=_never) == 1


def test_the_hook_probe_reads_the_gate_this_lane_ships():
    """The probe is a literal; if the gate renames it, this goes red here."""
    assert lane.hook_gate_knows_ci(SCRIPTS / "pre_push_ref_gate.py")
    assert not lane.hook_gate_knows_ci(SCRIPTS / "lane_ci_no_such_file.py")


# ---------------------------------------------------------------------------
# wait --full: the full matrix on a lane's own ci/ ref (lane ci8, 2026-11-27)
# ---------------------------------------------------------------------------
#
# RULED 22:55: before master is fast-forwarded, a branch's ci/ ref gets the
# FULL matrix -- three cells x six shards, which ci.yml gives a
# workflow_dispatch on any ref. ``wait <sha> --full`` waits for the push run
# on ci/<branch> to FINISH first, because the dispatch shares its
# concurrency group and cancel-in-progress would cancel it; then dispatches,
# finds the dispatch run BY HEAD SHA AND EVENT, waits, and reports the
# conclusion and every cell.

import re  # noqa: E402 -- the section's own


def _shard_job(os_name: str, py: str, shard: int, conclusion: str = "success") -> dict:
    return {"name": f"pytest ({os_name}, py{py}, shard {shard})",
            "status": "completed", "conclusion": conclusion}


def _full_jobs(fail: tuple[str, str, int] | None = None, cells=None, shards=6) -> list[dict]:
    cells = cells or [("ubuntu-latest", "3.10"), ("ubuntu-latest", "3.13"),
                      ("windows-latest", "3.13")]
    jobs = [{"name": "shard plan", "status": "completed", "conclusion": "success"}]
    for os_name, py in cells:
        for index in range(shards):
            bad = fail == (os_name, py, index)
            jobs.append(_shard_job(os_name, py, index, "failure" if bad else "success"))
    jobs.append({"name": "every shard reported", "status": "completed",
                 "conclusion": "success"})
    return jobs


def _view(conclusion: str, jobs: list[dict]) -> dict:
    return {"status": "completed", "conclusion": conclusion, "jobs": jobs,
            "startedAt": "2026-11-27T18:00:00Z", "updatedAt": "2026-11-27T18:11:00Z"}


RUNNING = {"status": "in_progress", "jobs": []}


def _run_of(i, event, status="completed", conclusion="success", sha=SHA,
            branch="ci/lane", created="2026-11-27T18:00:00Z", title=None):
    return {"databaseId": i, "headSha": sha, "headBranch": branch, "event": event,
            "status": status, "conclusion": conclusion, "createdAt": created,
            "displayTitle": title or ("CI" if event == "workflow_dispatch" else "a commit")}


class FullGh:
    """Canned gh answers for --full, keyed by what is asked, with every call
    kept so a test can read their ORDER."""

    def __init__(self, push_lists, dispatch_lists, views, log="", dispatch_rc=0):
        self.push_lists = list(push_lists)
        self.dispatch_lists = list(dispatch_lists)
        self.views = {k: list(v) for k, v in views.items()}
        self.log, self.dispatch_rc, self.calls = log, dispatch_rc, []

    @staticmethod
    def _next(queue):
        return queue.pop(0) if len(queue) > 1 else queue[0]

    def __call__(self, *args):
        self.calls.append(args)
        if args[:2] == ("workflow", "run"):
            return self.dispatch_rc, "", "" if self.dispatch_rc == 0 else "HTTP 403"
        if args[:2] == ("run", "list"):
            assert "--commit" in args and SHA in args, args  # BY SHA, always
            event = args[args.index("--event") + 1]
            queue = self.push_lists if event == "push" else self.dispatch_lists
            return 0, json.dumps(self._next(queue)), ""
        if "--log-failed" in args:
            return 0, self.log, ""
        run_id = args[2]
        return 0, json.dumps(self._next(self.views[run_id])), ""

    def index(self, *prefix) -> list[int]:
        return [i for i, call in enumerate(self.calls) if call[:len(prefix)] == prefix]


def _git_for_full(ref_sha=SHA):
    def git(*args):
        if args[:2] == ("remote", "get-url"):
            return 0, "https://github.com/owner-x/repo-y.git", ""
        if args[:1] == ("symbolic-ref",):
            return 0, "lane", ""
        if args[:1] == ("ls-remote",):
            assert args[-1] == "refs/heads/ci/lane", args
            return 0, f"{ref_sha}\trefs/heads/ci/lane", ""
        raise AssertionError(args)
    return git


def _full(monkeypatch, gh, ref_sha=SHA, bound=600):
    ticks = iter(range(0, 100_000, 20))
    monkeypatch.setattr(lane, "_git", _git_for_full(ref_sha))
    monkeypatch.setattr(lane, "_gh", gh)
    return lane.cmd_full(SHA, poll=20, bound=bound, full_bound=bound,
                         sleep=lambda s: None, clock=lambda: next(ticks))


def test_full_waits_for_the_push_run_to_finish_before_it_dispatches(monkeypatch, capsys):
    """The dispatch shares the push run's concurrency group, and
    cancel-in-progress would cancel whichever came first. So the dispatch is
    sent only after the push run's view has read COMPLETED."""
    gh = FullGh(push_lists=[[_run_of(7, "push", status="in_progress")]],
                dispatch_lists=[[], [], [_run_of(9, "workflow_dispatch",
                                                 status="in_progress")]],
                views={"7": [RUNNING, RUNNING, _view("success", [])],
                       "9": [RUNNING, _view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0, capsys.readouterr()
    push_views = gh.index("run", "view", "7")
    assert len(push_views) == 3, ("the push run was not read to completion", gh.calls)
    dispatched = gh.index("workflow", "run")
    assert len(dispatched) == 1 and dispatched[0] > max(push_views), gh.calls
    assert gh.calls[dispatched[0]] == ("workflow", "run", "ci.yml", "-R", "owner-x/repo-y",
                                       "--ref", "ci/lane"), gh.calls[dispatched[0]]


def test_full_reports_the_conclusion_and_every_cell(monkeypatch, capsys):
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[], [_run_of(9, "workflow_dispatch", status="in_progress")]],
                views={"7": [_view("success", [])],
                       "9": [_view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0
    out = capsys.readouterr().out
    assert "run 9: success  jobs=20  wall=11m00s" in out, out
    for cell in ("ubuntu-latest py3.10", "ubuntu-latest py3.13", "windows-latest py3.13"):
        assert re.search(rf"{re.escape(cell)}: 6 of 6 shards success", out), out
    assert "3 cells x 6 shards = 18 shard jobs" in out, out
    assert "every shard reported: success" in out, out


def test_full_finds_the_dispatch_run_by_sha_and_event_never_the_latest(monkeypatch, capsys):
    """Right after a dispatch the newest run in the repository is somebody
    else's. The run is the one whose head sha, event and ref are ours and
    which did not exist before the dispatch."""
    other = _run_of(99, "workflow_dispatch", status="in_progress", sha=OTHER,
                    created="2026-11-27T19:00:00Z")
    push = _run_of(7, "push", created="2026-11-27T18:30:00Z")
    stranger_ref = _run_of(98, "workflow_dispatch", status="in_progress",
                           branch="ci/someone-else", created="2026-11-27T18:59:00Z")
    ours = _run_of(9, "workflow_dispatch", status="in_progress",
                   created="2026-11-27T18:40:00Z")
    gh = FullGh(push_lists=[[push]],
                dispatch_lists=[[other, stranger_ref], [other, stranger_ref, push, ours]],
                views={"7": [_view("success", [])],
                       "9": [_view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0
    assert "run 9: success" in capsys.readouterr().out
    listed = [call for call in gh.calls if call[:2] == ("run", "list")]
    assert listed and all("--limit" in c and c[c.index("--limit") + 1] != "1"
                          for c in listed), listed


def test_a_dispatch_already_running_is_waited_on_never_sent_again(monkeypatch, capsys):
    """A wait the shell cut short is RESUMED: a second dispatch would cancel
    the first through the same concurrency group."""
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[_run_of(9, "workflow_dispatch", status="in_progress")]],
                views={"7": [_view("success", [])],
                       "9": [RUNNING, _view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0
    assert gh.index("workflow", "run") == [], gh.calls
    assert "already dispatched" in capsys.readouterr().err


def test_a_completed_dispatch_of_this_sha_is_read_not_repeated(monkeypatch, capsys):
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[_run_of(9, "workflow_dispatch")]],
                views={"7": [_view("success", [])],
                       "9": [_view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0
    assert gh.index("workflow", "run") == [], gh.calls
    captured = capsys.readouterr()
    assert "already ran on this sha" in captured.err and "run 9: success" in captured.out


def test_a_cancelled_dispatch_is_dispatched_again(monkeypatch, capsys):
    """And the OLD run is never taken for the new one: right after the
    dispatch the list still shows only the cancelled run, whose verdict is
    no verdict on anything."""
    cancelled = _run_of(9, "workflow_dispatch", conclusion="cancelled")
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[cancelled], [cancelled],
                                [cancelled,
                                 _run_of(10, "workflow_dispatch", status="in_progress",
                                         created="2026-11-27T18:50:00Z")]],
                views={"7": [_view("success", [])],
                       "9": [_view("cancelled", [])],
                       "10": [_view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0
    assert len(gh.index("workflow", "run")) == 1, gh.calls
    assert "run 10: success" in capsys.readouterr().out


def test_full_refuses_when_the_ci_ref_does_not_hold_the_sha(monkeypatch, capsys):
    """A dispatch runs the REF's head. If ci/<branch> holds another commit,
    the full matrix would certify that one under this sha's name."""
    gh = FullGh(push_lists=[[]], dispatch_lists=[[]], views={})
    assert _full(monkeypatch, gh, ref_sha=OTHER) == 1
    assert gh.calls == [], gh.calls
    assert "holds " + OTHER[:12] in capsys.readouterr().err


def test_full_sends_nothing_after_a_red_push_run(monkeypatch, capsys):
    """The full matrix cannot certify a sha whose lane run is red, and it
    would spend eighteen jobs of the shared pool learning so."""
    gh = FullGh(push_lists=[[_run_of(7, "push", conclusion="failure")]],
                dispatch_lists=[[]],
                views={"7": [_view("failure", [_shard_job("ubuntu-latest", "3.13", 1,
                                                          "failure")])]})
    assert _full(monkeypatch, gh) == 1
    assert gh.index("workflow", "run") == [], gh.calls
    assert "not dispatched" in capsys.readouterr().err


def test_a_red_cell_is_named_with_its_shard(monkeypatch, capsys):
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[], [_run_of(9, "workflow_dispatch", status="in_progress")]],
                views={"7": [_view("success", [])],
                       "9": [_view("failure", _full_jobs(fail=("windows-latest", "3.13", 1)))]})
    assert _full(monkeypatch, gh) == 1
    out = capsys.readouterr().out
    assert "windows-latest py3.13: 5 of 6 shards success; shard 1 failure" in out, out
    assert "ubuntu-latest py3.10: 6 of 6 shards success" in out, out


def test_a_one_cell_run_is_not_the_full_matrix(monkeypatch, capsys):
    """Green, and the wrong shape: one cell is the fast lane's. Reported as
    not the full matrix, never as its certificate."""
    jobs = _full_jobs(cells=[("ubuntu-latest", "3.13")], shards=4)
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[], [_run_of(9, "workflow_dispatch", status="in_progress")]],
                views={"7": [_view("success", [])], "9": [_view("success", jobs)]})
    assert _full(monkeypatch, gh) == 1
    assert "NOT THE FULL MATRIX" in capsys.readouterr().out


def test_a_dispatch_that_never_appears_is_no_verdict(monkeypatch, capsys):
    gh = FullGh(push_lists=[[_run_of(7, "push")]], dispatch_lists=[[]],
                views={"7": [_view("success", [])]})
    assert _full(monkeypatch, gh, bound=100) == 2
    assert "NO VERDICT" in capsys.readouterr().err


def test_a_refused_dispatch_is_no_verdict(monkeypatch, capsys):
    gh = FullGh(push_lists=[[_run_of(7, "push")]], dispatch_lists=[[]],
                views={"7": [_view("success", [])]}, dispatch_rc=1)
    assert _full(monkeypatch, gh) == 2
    assert "dispatch failed" in capsys.readouterr().err


def test_the_cell_reader_parses_the_job_name_ci_yml_writes():
    """The shard job's name is a template in the workflow; the reader is
    held to what that template renders, so a rename goes red here."""
    import yaml

    template = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"))["jobs"]["test"]["name"]
    name = (template.replace("${{ matrix.cell.os }}", "windows-latest")
            .replace("${{ matrix.cell['python-version'] }}", "3.13")
            .replace("${{ matrix.shard }}", "5"))
    assert "${{" not in name, name
    cells = lane.cells_of({"jobs": [{"name": name, "conclusion": "success"}]})
    assert cells == {"windows-latest py3.13": {5: "success"}}, cells


def test_the_full_plan_passes_the_shape_check_and_the_fast_plan_does_not(tmp_path):
    """The shape check, held to the plan step itself: the outputs ci.yml
    gives a workflow_dispatch on a ci/ ref pass it, and the fast lane's fail
    it, so neither can drift away from the check unnoticed."""
    from tests.test_ci_fast_lane import _run_plan

    def jobs_for(plan):
        return {"jobs": [_shard_job(c["os"], c["python-version"], s)
                         for c in plan["cells"] for s in plan["shards"]]}

    full = _run_plan(tmp_path, "workflow_dispatch", "refs/heads/ci/lane")
    fast = _run_plan(tmp_path, "push", "refs/heads/ci/lane")
    assert lane.matrix_problems(lane.cells_of(jobs_for(full))) == []
    assert lane.matrix_problems(lane.cells_of(jobs_for(fast))) != []


def test_wait_full_is_one_command():
    """``lane_ci.py wait <sha> --full`` parses to the full-matrix path."""
    calls = []
    original = lane.cmd_full
    try:
        lane.cmd_full = lambda sha, **kw: calls.append(sha) or 0
        assert lane.main(["lane_ci.py", "wait", SHA, "--full"]) == 0
    finally:
        lane.cmd_full = original
    assert calls == [SHA]


# ---------------------------------------------------------------------------
# read-map <sha>: the impact gate's read map, recorded on CI (lane ci8, 2026-11-28)
# ---------------------------------------------------------------------------
#
# A dispatch of ci.yml with record_read_map runs the whole suite under the
# recorder on one cell, sharded, and uploads the merged map. It is a
# workflow_dispatch run of ci.yml on the sha, exactly like the full matrix's,
# so the two are told apart by the recording's run name, and neither command
# may ever take the other's run for its own.

RECORDING = "read-map recording"


def _recording_view(conclusion="success", merge="success"):
    jobs = _full_jobs(cells=[("ubuntu-latest", "3.13")], shards=6)
    jobs.append({"name": "the read map, merged and pruned", "status": "completed",
                 "conclusion": merge})
    return _view(conclusion, jobs)


def _read_map(monkeypatch, gh, fetched, ref_sha=SHA, bound=600):
    ticks = iter(range(0, 100_000, 20))
    monkeypatch.setattr(lane, "_git", _git_for_full(ref_sha))
    monkeypatch.setattr(lane, "_gh", gh)

    def fetcher(run_id, sha, **kwargs):
        fetched.append((run_id, sha, kwargs.get("slug")))
        return 0

    return lane.cmd_read_map(SHA, poll=20, bound=bound, sleep=lambda s: None,
                             clock=lambda: next(ticks), fetcher=fetcher)


def test_the_recordings_name_is_the_recipes(tmp_path):
    """lane_ci tells a recording by the recipe's own constant, which ci.yml's
    run-name writes (tests/test_ci_fast_lane.py holds that half)."""
    assert lane.RECORDING_RUN_NAME == RECORDING


def test_a_recording_of_the_same_sha_is_never_taken_for_the_full_matrix(monkeypatch, capsys):
    """SHOWN FAILING before --full read the run name: it took the running
    recording for a full-matrix dispatch already sent, and waited on it."""
    recording = _run_of(8, "workflow_dispatch", status="in_progress", title=RECORDING)
    gh = FullGh(push_lists=[[_run_of(7, "push")]],
                dispatch_lists=[[recording],
                                [recording, _run_of(9, "workflow_dispatch", status="in_progress",
                                                    created="2026-11-27T18:40:00Z")]],
                views={"7": [_view("success", [])],
                       "8": [_recording_view()],
                       "9": [_view("success", _full_jobs())]})
    assert _full(monkeypatch, gh) == 0, capsys.readouterr()
    assert len(gh.index("workflow", "run")) == 1, gh.calls
    assert "run 9: success" in capsys.readouterr().out


def test_read_map_dispatches_a_recording_and_installs_its_map(monkeypatch, capsys):
    fetched = []
    gh = FullGh(push_lists=[[]],
                dispatch_lists=[[], [_run_of(11, "workflow_dispatch", status="in_progress",
                                             title=RECORDING)]],
                views={"11": [RUNNING, _recording_view()]})
    assert _read_map(monkeypatch, gh, fetched) == 0, capsys.readouterr()
    dispatched = [gh.calls[i] for i in gh.index("workflow", "run")]
    assert dispatched == [("workflow", "run", "ci.yml", "-R", "owner-x/repo-y", "--ref",
                           "ci/lane", "-f", "record_read_map=true")], gh.calls
    assert fetched == [("11", SHA, "owner-x/repo-y")], fetched


def test_read_map_never_takes_a_full_matrix_run_for_a_recording(monkeypatch, capsys):
    fetched = []
    full = _run_of(9, "workflow_dispatch")          # the full matrix's, finished
    gh = FullGh(push_lists=[[]],
                dispatch_lists=[[full], [full, _run_of(12, "workflow_dispatch",
                                                       status="in_progress", title=RECORDING,
                                                       created="2026-11-27T19:00:00Z")]],
                views={"9": [_view("success", _full_jobs())], "12": [_recording_view()]})
    assert _read_map(monkeypatch, gh, fetched) == 0, capsys.readouterr()
    assert len(gh.index("workflow", "run")) == 1, gh.calls
    assert fetched == [("12", SHA, "owner-x/repo-y")], fetched


def test_read_map_resumes_a_recording_already_running(monkeypatch, capsys):
    fetched = []
    running = _run_of(13, "workflow_dispatch", status="in_progress", title=RECORDING)
    gh = FullGh(push_lists=[[]], dispatch_lists=[[running]],
                views={"13": [RUNNING, _recording_view()]})
    assert _read_map(monkeypatch, gh, fetched) == 0
    assert gh.index("workflow", "run") == [], gh.calls
    assert fetched == [("13", SHA, "owner-x/repo-y")], fetched


def test_read_map_installs_nothing_when_the_merge_did_not_run(monkeypatch, capsys):
    fetched = []
    gh = FullGh(push_lists=[[]],
                dispatch_lists=[[], [_run_of(14, "workflow_dispatch", status="in_progress",
                                             title=RECORDING)]],
                views={"14": [_recording_view(conclusion="failure", merge="skipped")]},
                log="")
    assert _read_map(monkeypatch, gh, fetched) == 1
    assert fetched == [], fetched
    assert "merged and pruned" in capsys.readouterr().out


def test_read_map_refuses_when_the_ci_ref_does_not_hold_the_sha(monkeypatch, capsys):
    fetched = []
    gh = FullGh(push_lists=[[]], dispatch_lists=[[]], views={})
    assert _read_map(monkeypatch, gh, fetched, ref_sha=OTHER) == 1
    assert gh.calls == [] and fetched == []
