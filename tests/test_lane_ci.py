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


def test_clean_deletes_exactly_the_ci_ref_and_nothing_else():
    seen = []
    assert lane.cmd_clean("lane", pusher=lambda argv: seen.append(argv) or 0) == 0
    assert seen == [["git", "push", "--no-follow-tags", "origin", ":refs/heads/ci/lane"]]
    assert lane.cmd_clean("HEAD", pusher=_never) == 1


def test_the_hook_probe_reads_the_gate_this_lane_ships():
    """The probe is a literal; if the gate renames it, this goes red here."""
    assert lane.hook_gate_knows_ci(SCRIPTS / "pre_push_ref_gate.py")
    assert not lane.hook_gate_knows_ci(SCRIPTS / "lane_ci_no_such_file.py")
