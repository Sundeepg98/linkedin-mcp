"""``scripts/build_read_map.py``: the recorder's filters, and its CI half.

ADDED 2026-11-28 (lane ci8). The impact gate's observed read map was a
recording of 2026-09-22, two months stale, because the recipe is a full-suite
run and the full suite does not run on the shared box. So the full recording
became a free CI job (``.github/workflows/ci.yml``, a workflow_dispatch with
``record_read_map``): every shard runs under the recorder, a merge job merges
and prunes the recordings with this script's own ``merge_shards`` and
``prune``, and uploads the map; ``--fetch`` installs it by run id and sha.

WHAT IS PINNED, each part shown failing before it existed:

* a git WORKTREE's ``.git`` is a FILE, and reading it is not a read of
  anything a diff can name (lane ci8's scoped re-record recorded it);
* the merge reads recordings in per-shard SUBDIRECTORIES, the shape a CI
  artifact download leaves;
* ``--merge`` stamps the map with the run id and the head it recorded, and
  refuses a shard whose pytest could not run;
* ``--fetch`` takes a run by its id and its head sha, and refuses a run of
  another sha, a run that is not a recording, and a map whose stamp is not
  that run's.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "build_read_map.py"


def _load():
    spec = importlib.util.spec_from_file_location("_build_read_map_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


recipe = _load()


# ---------------------------------------------------------------------------
# The recorder's filters
# ---------------------------------------------------------------------------


@pytest.fixture()
def worktree(tmp_path):
    """A repository root the way a git worktree lays one out: ``.git`` is a
    FILE naming the real git directory, beside a tracked data file."""
    root = tmp_path / "work"
    (root / "tests").mkdir(parents=True)
    (root / ".git").write_text("gitdir: ../elsewhere/.git/worktrees/x\n", encoding="utf-8")
    (root / "tests" / "data.txt").write_text("a fixture\n", encoding="utf-8")
    return root


def test_a_worktrees_git_file_is_not_a_read(worktree):
    """SHOWN FAILING before the fix: ``_rel`` returned ``.git``, because the
    filter was the PREFIX ``.git/`` and a worktree's ``.git`` has none."""
    assert recipe._rel(str(worktree / ".git"), worktree) is None
    assert recipe._rel(str(worktree / "tests" / "data.txt"), worktree) == "tests/data.txt"


def test_prune_keeps_no_git_file_either(worktree):
    """The same file reaching ``prune`` from a recording made before the fix."""
    kept = recipe.prune({"tests/test_x.py": [".git", "tests/data.txt"]}, worktree)
    assert kept == {"tests/test_x.py": ["tests/data.txt"]}, kept


def test_an_argv_item_too_long_to_be_a_name_is_not_a_read(worktree, monkeypatch):
    """THE FIRST CI RECORDING (run 46065815443) FAILED THREE TESTS. Tests that
    run ``python -c <code>`` hand the code to the recorder as a candidate
    path, and on Linux ``exists()`` of a name past NAME_MAX raises
    ENAMETOOLONG instead of answering False. Emulated here on any platform:
    a name longer than 255 raises, as Linux's does. SHOWN FAILING before
    ``_rel`` caught it: the OSError reached the test."""
    import errno
    import pathlib

    real_exists = pathlib.Path.exists

    def linux_exists(self, *args, **kwargs):
        if any(len(part) > 255 for part in self.parts):
            raise OSError(errno.ENAMETOOLONG, "File name too long", str(self))
        return real_exists(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "exists", linux_exists)
    code = "import sys; print(sys.argv)" * 12
    assert len(code) > 255
    assert recipe._rel(str(worktree / code), worktree) is None
    assert recipe._rel(str(worktree / "tests" / "data.txt"), worktree) == "tests/data.txt"


def test_the_recorder_never_breaks_the_call_it_observes(tmp_path):
    """An instrument that raises inside the test it observes reports itself
    as the test's failure. Run in a child, because installing the recorder
    rebinds this process's ``open`` and ``subprocess``: a recorder whose
    every record raises must still let ``open`` and ``subprocess.run`` work.
    SHOWN FAILING before the tracers caught it."""
    script = tmp_path / "child.py"
    script.write_text(
        "import subprocess, sys\n"
        f"sys.path.insert(0, {str(REPO / 'scripts')!r})\n"
        "import build_read_map as r\n"
        "class Broken(r._Recorder):\n"
        "    def record(self, target):\n"
        "        raise RuntimeError('the recorder broke')\n"
        f"r._install(Broken(__import__('pathlib').Path({str(tmp_path)!r})))\n"
        f"open({str(script)!r}).close()\n"
        "done = subprocess.run([sys.executable, '-c', 'print(7)'], capture_output=True, text=True)\n"
        "print(done.stdout.strip())\n",
        encoding="utf-8")
    done = subprocess.run([__import__("sys").executable, str(script)], capture_output=True,
                          text=True, timeout=60)
    assert done.returncode == 0, done.stderr[-800:]
    assert done.stdout.strip().splitlines()[-1] == "7", done.stdout


# ---------------------------------------------------------------------------
# The merge, as the CI job runs it
# ---------------------------------------------------------------------------


def _recording(directory: Path, pid: int, edges: dict, unattributed=()) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"shard-{pid}.json").write_text(
        json.dumps({"edges": edges, "unattributed": list(unattributed)}), encoding="utf-8")


def _run_file(directory: Path, shard: int, code: int, seconds: int) -> None:
    (directory / recipe.RUN_FILE).write_text(
        json.dumps({"shard": shard, "exit": code, "seconds": seconds}), encoding="utf-8")


def test_the_merge_reads_recordings_in_per_shard_directories(tmp_path):
    """A CI download lays each shard's recordings in its own directory. SHOWN
    FAILING before the merge walked down: it found none of them."""
    _recording(tmp_path / "shard-0", 101, {"tests/test_a.py": ["tests/data.txt"]})
    _recording(tmp_path / "shard-1", 102, {"tests/test_b.py": ["tests/data.txt"]}, ["x.txt"])
    edges, unattributed = recipe.merge_shards(tmp_path)
    assert edges == {"tests/test_a.py": ["tests/data.txt"],
                     "tests/test_b.py": ["tests/data.txt"]}, edges
    assert unattributed == ["x.txt"]


def _merge(tmp_path, repo, *extra):
    out = tmp_path / "out" / "map.json"
    code = recipe.main(["--merge", str(tmp_path / "rec"), "--out", str(out),
                        "--run-id", "4242", "--head", "abc1234def", "--repo-root", str(repo),
                        *extra])
    return code, out


def test_merge_stamps_the_map_with_its_run_and_head(tmp_path, worktree):
    for shard in (0, 1):
        _recording(tmp_path / "rec" / f"shard-{shard}", 200 + shard,
                   {f"tests/test_{shard}.py": ["tests/data.txt", ".git", "gone.txt"]})
        _run_file(tmp_path / "rec" / f"shard-{shard}", shard, shard, 30)
    code, out = _merge(tmp_path, worktree)
    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["run_id"] == "4242" and payload["head"] == "abc1234def", payload
    assert payload["scope"].startswith("full-suite"), payload["scope"]
    assert payload["pytest_exit"] == 1 and payload["seconds"] == 60, payload
    assert payload["edges"] == {"tests/test_0.py": ["tests/data.txt"],
                                "tests/test_1.py": ["tests/data.txt"]}, payload["edges"]
    assert payload["test_files"] == 2


def test_merge_refuses_a_shard_whose_pytest_could_not_run(tmp_path, worktree):
    """The recipe's own rule: exit 0 or 1 is a run, anything else is not, and
    a map built from a run that did not happen is not written."""
    _recording(tmp_path / "rec" / "shard-0", 300, {"tests/test_0.py": ["tests/data.txt"]})
    _run_file(tmp_path / "rec" / "shard-0", 0, 4, 1)
    code, out = _merge(tmp_path, worktree)
    assert code == 1 and not out.exists()


def test_merge_refuses_a_recording_with_no_run_file(tmp_path, worktree):
    _recording(tmp_path / "rec" / "shard-0", 301, {"tests/test_0.py": ["tests/data.txt"]})
    code, out = _merge(tmp_path, worktree)
    assert code == 1 and not out.exists()


# ---------------------------------------------------------------------------
# The fetch, by run id and head sha
# ---------------------------------------------------------------------------

SHA = "a" * 40
OTHER = "b" * 40


def _view(sha=SHA, title=None, job="success", event="workflow_dispatch"):
    return {"databaseId": 4242, "headSha": sha, "event": event, "status": "completed",
            "conclusion": "success", "displayTitle": title or recipe.RECORDING_RUN_NAME,
            "jobs": [{"name": recipe.MERGE_JOB_NAME, "conclusion": job}]}


def _map(run_id="4242", head=SHA[:7]):
    return {"taken_at": "2026-11-28", "head": head, "run_id": run_id, "seconds": 1.0,
            "scope": "full-suite (GitHub Actions)", "pytest_exit": 0, "test_files": 1,
            "edges": {"tests/test_a.py": ["tests/data.txt"]}, "unattributed": []}


class FakeGh:
    def __init__(self, view, payload):
        self.view, self.payload, self.calls = view, payload, []

    def __call__(self, *args):
        self.calls.append(args)
        if args[:2] == ("run", "view"):
            return 0, json.dumps(self.view), ""
        if args[:2] == ("run", "download"):
            directory = Path(args[args.index("-D") + 1])
            directory.mkdir(parents=True, exist_ok=True)
            (directory / recipe.MAP_PATH.name).write_text(json.dumps(self.payload),
                                                         encoding="utf-8")
            return 0, "", ""
        raise AssertionError(args)


def _fetch(tmp_path, gh):
    target = tmp_path / "installed.json"
    code = recipe.fetch("4242", SHA, slug="owner-x/repo-y", gh=gh, map_path=target)
    return code, target


def test_fetch_installs_the_recording_of_that_run_and_sha(tmp_path):
    gh = FakeGh(_view(), _map())
    code, target = _fetch(tmp_path, gh)
    assert code == 0
    assert json.loads(target.read_text(encoding="utf-8"))["run_id"] == "4242"
    assert ("run", "download", "4242", "-R", "owner-x/repo-y", "-n", recipe.MAP_ARTIFACT) == \
        gh.calls[1][:7], gh.calls


@pytest.mark.parametrize(("view", "payload", "why"), [
    ({"sha": OTHER}, {}, "another sha"),
    ({"title": "CI"}, {}, "not a recording"),
    ({"job": "failure"}, {}, "the merge job did not succeed"),
    ({}, {"run_id": "999"}, "a stamp from another run"),
    ({}, {"head": "bbbbbbb"}, "a stamp from another head"),
], ids=["another-sha", "not-a-recording", "merge-failed", "another-run", "another-head"])
def test_fetch_refuses_what_is_not_that_runs_recording(tmp_path, view, payload, why):
    code, target = _fetch(tmp_path, FakeGh(_view(**view), _map(**payload)))
    assert code == 1, why
    assert not target.exists(), why


def test_the_module_still_imports_as_a_pytest_plugin_with_no_side_effect():
    """``-p build_read_map`` imports it in every worker; importing must arm
    nothing unless the shard directory is set."""
    done = subprocess.run(
        [__import__("sys").executable, "-c",
         "import sys; sys.path.insert(0, 'scripts'); import build_read_map, builtins, io; "
         "print(builtins.open is io.open and builtins.open.__module__ in ('io', '_io'))"],
        cwd=REPO, capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "True", done.stdout
