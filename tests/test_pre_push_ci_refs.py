"""The pre-push gate admits a ``ci/`` ref only when it publishes nothing new
but the lane's own swept commits -- shown on SYNTHETIC repositories.

WHY THESE TESTS DRIVE ``main()`` AND NOT ``verdicts()``. A ``ci/`` verdict is
not a pure function of git's stdin: it asks the pushing repository two
questions (is ``origin/master`` an ancestor of the pushed commit; does the
identity blob sweep read PASS over ``origin/master..<sha>``). So every test
here builds a real repository in a tmp dir, writes git's own pre-push line
format to stdin, and calls the gate's ``main`` exactly as the hook does. The
repository's own remote is never named, never fetched and never pushed to.

THE WORDLIST IS SYNTHETIC. The sweep is the SHIPPED instrument,
``scripts/sweep_blobs_for_identity.py``, reached through its own
``load_wordlist``; the only thing a test changes is the key file that loader
reads (``sweep_tracked_for_identity.KEY_PATH``), pointed at a one-value json in
the tmp dir. The planted value below is invented for this file and names no
one.

RED FIRST. Against the gate as it stood at 3c8edc2 (master only), the two
ALLOW tests here fail -- a clean ``ci/`` push and a ``ci/`` delete were both
refused -- and every REFUSE test passes, because the old gate refused
everything that was not master. The refusals are therefore pinned by their
REASON as well as their exit code: a gate that refused a non-descending push
for being "not master" would pass on the exit code alone, so each refusal
test also names the clause that must have fired.
"""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

ZERO = "0" * 40

#: Invented for this file. It must never be a real value: the point of the
#: test is that the sweep can see a value it was told to look for, and any
#: string at all proves that.
PLANTED = "Quorvexindale Plimbury"

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}


def _load_gate():
    spec = importlib.util.spec_from_file_location(
        "pre_push_ref_gate_ci_refs", SCRIPTS / "pre_push_ref_gate.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _tracked_sweep_module():
    """The module whose ``KEY_PATH`` the shipped blob sweep loads through."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sweep_tracked_for_identity  # noqa: PLC0415
    return sweep_tracked_for_identity


class World:
    """A synthetic repository whose ``origin/master`` is a known commit."""

    def __init__(self, root: Path) -> None:
        self.repo = root / "work"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "master")
        self.base = self.commit({"base.txt": "the published history\n"})
        self.git("update-ref", "refs/remotes/origin/master", self.base)

    def git(self, *args: str) -> str:
        import os
        env = dict(os.environ)
        env.update(_GIT_ENV)
        out = subprocess.run(
            ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=.nohooks",
             *args],
            cwd=self.repo, capture_output=True, text=True, env=env, timeout=60)
        assert out.returncode == 0, (args, out.stderr)
        return out.stdout.strip()

    def commit(self, files: dict[str, str | None]) -> str:
        for name, text in files.items():
            path = self.repo / name
            if text is None:
                self.git("rm", "-q", name)
                continue
            path.write_text(text, encoding="utf-8")
            self.git("add", name)
        self.git("commit", "-q", "--no-verify", "-m", "fixture commit")
        return self.git("rev-parse", "HEAD")

    def branch_from_base(self, name: str) -> None:
        self.git("checkout", "-q", "-B", name, self.base)

    def orphan(self, name: str) -> None:
        self.git("checkout", "-q", "--orphan", name)
        self.git("rm", "-rq", "--cached", ".")
        for child in self.repo.iterdir():
            if child.name != ".git" and child.is_file():
                child.unlink()


@pytest.fixture
def world(tmp_path, monkeypatch):
    w = World(tmp_path)
    key = tmp_path / "synthetic_key.json"
    key.write_text(json.dumps({"synthetic_needles": [PLANTED]}), encoding="utf-8")
    monkeypatch.setattr(_tracked_sweep_module(), "KEY_PATH", key)
    for name, value in _GIT_ENV.items():
        monkeypatch.setenv(name, value)
    monkeypatch.delenv("LINKEDIN_MCP_ALLOW_ANY_REF", raising=False)
    monkeypatch.delenv("GIT_DIR", raising=False)
    monkeypatch.delenv("GIT_WORK_TREE", raising=False)
    monkeypatch.chdir(w.repo)
    return w


def _push(lines: list[str], monkeypatch, capsys, remote: str = "origin"):
    """Run the gate the way the hook does: argv from git, ref lines on stdin."""
    gate = _load_gate()
    monkeypatch.setattr(sys, "stdin", io.StringIO("".join(f"{x}\n" for x in lines)))
    rc = gate.main(["pre-push", remote, "fixture-remote-url"])
    captured = capsys.readouterr()
    return rc, captured.out + captured.err


def _line(local_ref: str, sha: str, remote_ref: str, remote_sha: str = ZERO) -> str:
    return f"{local_ref} {sha} {remote_ref} {remote_sha}"


# ---------------------------------------------------------------------------
# The two ALLOW paths -- these are the tests the old gate fails
# ---------------------------------------------------------------------------


def test_a_clean_ci_push_descending_from_master_is_allowed(world, monkeypatch, capsys):
    """THE POSITIVE CONTROL. Every refusal below is worth nothing without it."""
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("refs/heads/lane", sha, "refs/heads/ci/lane")],
                     monkeypatch, capsys)
    assert rc == 0, said
    assert "PASS" in said, said  # the sweep spoke, and said so


def test_deleting_a_ci_ref_is_allowed(world, monkeypatch, capsys):
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("(delete)", ZERO, "refs/heads/ci/lane", sha)],
                     monkeypatch, capsys)
    assert rc == 0, said


# ---------------------------------------------------------------------------
# The refusals, each pinned by the clause that must have fired
# ---------------------------------------------------------------------------


def test_a_ci_push_not_descending_from_master_is_refused(world, monkeypatch, capsys):
    """Content CLEAN on purpose: only the ancestry clause can refuse this."""
    world.orphan("stray")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("refs/heads/stray", sha, "refs/heads/ci/stray")],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert "NOT an ancestor" in said, said


def test_a_ci_push_carrying_a_planted_identity_value_is_refused(
        world, monkeypatch, capsys):
    world.branch_from_base("lane")
    sha = world.commit({"notes.md": f"a line naming {PLANTED} in prose\n"})
    rc, said = _push([_line("refs/heads/lane", sha, "refs/heads/ci/lane")],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert "identity sweep" in said, said
    assert PLANTED not in said, "the gate printed the value it was hunting"


def test_a_value_removed_in_a_later_commit_is_still_refused(
        world, monkeypatch, capsys):
    """The blob sweep's reason to exist: a clean TIP says nothing about its
    ancestors, and a push publishes every one of them."""
    world.branch_from_base("lane")
    world.commit({"notes.md": f"a line naming {PLANTED} in prose\n"})
    sha = world.commit({"notes.md": None})
    rc, said = _push([_line("refs/heads/lane", sha, "refs/heads/ci/lane")],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert "identity sweep" in said, said


@pytest.mark.parametrize("remote_ref", [
    "refs/heads/lane",
    "refs/heads/ci-offload",
    "refs/heads/cilane",
    "refs/tags/ci/lane",
    "refs/heads/ci/",
    "refs/heads/ci/../master",
])
def test_a_non_ci_non_master_ref_is_still_refused(
        world, monkeypatch, capsys, remote_ref):
    """Clean, descending content: the NAME is the only thing wrong here."""
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("refs/heads/lane", sha, remote_ref)],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert remote_ref in said, said


def test_a_ci_ref_rides_alone_or_not_at_all(world, monkeypatch, capsys):
    """``--all`` and ``--mirror`` offer many refs at once. A ci/ ref is
    admitted only as the ONLY ref of its push, so neither can carry one."""
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([
        _line("refs/heads/master", world.base, "refs/heads/master"),
        _line("refs/heads/lane", sha, "refs/heads/ci/lane"),
    ], monkeypatch, capsys)
    assert rc == 1, said
    assert "alone" in said.lower(), said


def test_a_ci_push_to_another_remote_is_refused(world, monkeypatch, capsys):
    """The allowance is measured against ORIGIN's master and means nothing
    about what any other remote already serves."""
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("refs/heads/lane", sha, "refs/heads/ci/lane")],
                     monkeypatch, capsys, remote="elsewhere")
    assert rc == 1, said
    assert "origin" in said, said


def test_a_missing_wordlist_refuses_rather_than_allows(
        world, monkeypatch, capsys, tmp_path):
    """A sweep that cannot load its needles has measured nothing."""
    monkeypatch.setattr(_tracked_sweep_module(), "KEY_PATH",
                        tmp_path / "no_such_key.json")
    world.branch_from_base("lane")
    sha = world.commit({"lane.txt": "a lane's own new work\n"})
    rc, said = _push([_line("refs/heads/lane", sha, "refs/heads/ci/lane")],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert "wordlist" in said, said


def test_master_itself_on_a_ci_ref_is_refused_as_nothing_to_test(
        world, monkeypatch, capsys):
    rc, said = _push([_line("refs/heads/master", world.base, "refs/heads/ci/lane")],
                     monkeypatch, capsys)
    assert rc == 1, said
    assert "nothing above origin/master" in said, said


def test_an_unwired_content_check_refuses_rather_than_allows():
    """``verdicts()`` without a checker must answer like the OLD gate did. A
    caller that forgets to wire the clauses gets a refusal, never an allow."""
    gate = _load_gate()
    got = gate.verdicts([_line("refs/heads/lane", "1" * 40, "refs/heads/ci/lane")])
    assert [v for v, _r, _w in got] == ["REFUSE"], got


def test_the_content_check_is_what_decides_a_ci_update():
    """Both directions through the same line, so neither answer is a default."""
    gate = _load_gate()
    line = [_line("refs/heads/lane", "1" * 40, "refs/heads/ci/lane")]
    ok = gate.verdicts(line, ci_check=lambda sha: [])
    bad = gate.verdicts(line, ci_check=lambda sha: ["planted problem"])
    assert ok[0][0] == "ALLOW", ok
    assert bad[0][0] == "REFUSE" and "planted problem" in bad[0][2], bad


def test_a_master_push_is_still_allowed_without_any_sweep(
        world, monkeypatch, capsys, tmp_path):
    """The master path must not grow a dependency on the wordlist: CI runners
    have none, and the master push is the one the orchestrator makes."""
    monkeypatch.setattr(_tracked_sweep_module(), "KEY_PATH",
                        tmp_path / "no_such_key.json")
    rc, said = _push([_line("refs/heads/master", world.base, "refs/heads/master")],
                     monkeypatch, capsys)
    assert rc == 0, said
