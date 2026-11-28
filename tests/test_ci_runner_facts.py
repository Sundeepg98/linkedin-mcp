"""Every CI shard records the runner it ran on: workers, CPUs, free memory.

WHY. ``_audit/2026-09-21-the-windows-shard.md`` asked for it in its 7.1, and
lane masterfix7 asked again (its record, Q2): master run 46030101439's windows
shard 1 stalled in its parallel phase, two 60 s ``set_content`` bounds ran
out, and the re-run passed. Nothing in the job said how many xdist workers
``-n auto`` had started, how many CPUs the runner had, or how much memory was
free, so the stall could only be read back out of junit durations. One step
in ``.github/workflows/ci.yml`` now records those three facts before the run,
into the job log and into the shard's report, and the totals job prints them
for every shard.

WHAT IS PINNED HERE, each part of which went red before it existed:

* the script measures all three facts on the machine running this test --
  ubuntu and windows both, because CI runs this file on both;
* the worker count is XDIST'S OWN resolution of ``-n auto``, not a guess
  beside it: ``PYTEST_XDIST_AUTO_NUM_WORKERS`` moves it, which a script that
  read ``os.cpu_count()`` would not follow;
* the workflow runs the step after the install and before the run, and the
  report step hands its file to ``ci_shard_totals.py record``;
* the shard report carries the facts, a missing facts file is recorded as
  missing rather than crashing the report, and ``verify`` shows every shard's.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
FACTS = REPO / "scripts" / "ci_runner_facts.py"
TOTALS = REPO / "scripts" / "ci_shard_totals.py"
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"


def _run(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *[str(arg) for arg in args]],
                          capture_output=True, text=True, cwd=REPO, env=env,
                          timeout=60)


def _facts(tmp_path, env=None) -> tuple[dict, str]:
    out = tmp_path / "runner-facts.json"
    done = _run(FACTS, "--out", out, env=env)
    assert done.returncode == 0, done.stderr
    return json.loads(out.read_text(encoding="utf-8")), done.stdout


# ---------------------------------------------------------------------------
# The script, on the machine running this test
# ---------------------------------------------------------------------------


def test_the_three_facts_are_measured_on_this_runner(tmp_path):
    facts, stdout = _facts(tmp_path)
    assert isinstance(facts["cpu_count"], int) and facts["cpu_count"] >= 1, facts
    assert isinstance(facts["xdist_workers"], int) and facts["xdist_workers"] >= 1, facts
    total, free = facts["memory_total_bytes"], facts["memory_available_bytes"]
    assert isinstance(total, int) and isinstance(free, int), facts
    assert 0 < free <= total, facts
    # The three facts are known everywhere this runs. Affinity is the one a
    # platform may not expose (Windows before Python 3.13), and it is said so.
    assert set(facts["unknown"]) <= {"cpus_usable"}, facts["unknown"]
    lines = [line for line in stdout.splitlines() if line.startswith("runner:")]
    assert len(lines) == 1, stdout
    line = lines[0]
    assert f"{facts['cpu_count']} CPUs" in line, line
    assert f"-n auto starts {facts['xdist_workers']} workers" in line, line
    assert "GiB available" in line, line


def test_the_worker_count_is_xdists_own_resolution(tmp_path, monkeypatch):
    """xdist reads PYTEST_XDIST_AUTO_NUM_WORKERS before anything else. A
    script that asked ``os.cpu_count()`` would report the CPUs, not 3."""
    env = dict(os.environ, PYTEST_XDIST_AUTO_NUM_WORKERS="3")
    facts, _stdout = _facts(tmp_path, env=env)
    assert facts["xdist_workers"] == 3, facts
    assert "PYTEST_XDIST_AUTO_NUM_WORKERS" in facts["xdist_rule"], facts

    monkeypatch.delenv("PYTEST_XDIST_AUTO_NUM_WORKERS", raising=False)
    facts, _stdout = _facts(tmp_path, env=dict(os.environ))
    from xdist.plugin import pytest_xdist_auto_num_workers

    class _Option:
        numprocesses = "auto"

    class _Config:
        option = _Option()

    assert facts["xdist_workers"] == pytest_xdist_auto_num_workers(_Config()), facts


# ---------------------------------------------------------------------------
# The workflow
# ---------------------------------------------------------------------------


def _steps() -> list[dict]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["test"]["steps"]


def _index(steps: list[dict], needle: str) -> int:
    found = [i for i, s in enumerate(steps) if needle in (s.get("run") or "")]
    assert len(found) == 1, (needle, found)
    return found[0]


#: Where the facts file goes: the runner's own temp directory, OUTSIDE the
#: checkout. Lane run 46052436870 wrote it into the checkout, after the
#: shard's collection and before its run, and the two tracked-file guards
#: (test_no_committed_identity, test_no_committed_credential) sweep the
#: worktree's untracked files too: each collected one more case at run time
#: than the shard had counted, and shards 0 and 1 and the totals job went red
#: with "collection found 4227 but only 4228 reached the report".
FACTS_PATH = '"$RUNNER_TEMP/runner-facts.json"'


def test_the_workflow_records_the_runner_before_the_run_and_reports_it():
    steps = _steps()
    facts = _index(steps, "scripts/ci_runner_facts.py")
    install = _index(steps, "pip install -r requirements.txt")
    run = _index(steps, "--junitxml=junit.xml")
    report = _index(steps, "scripts/ci_shard_totals.py record")
    assert install < facts < run < report, (install, facts, run, report)
    assert f"--out {FACTS_PATH}" in steps[facts]["run"], steps[facts]["run"]
    assert f"--runner {FACTS_PATH}" in steps[report]["run"], steps[report]["run"]
    assert "if" not in steps[facts], "the facts step is skipped on some runs"


def test_no_step_between_the_shard_count_and_the_run_writes_into_the_checkout():
    """The shard's denominator is collected BEFORE the facts step, and any file
    a step then leaves in the checkout is swept by the tracked-file guards at
    run time, so the shard runs more than it counted. Every path the facts
    step writes is under ``$RUNNER_TEMP``."""
    steps = _steps()
    counted = _index(steps, "--collect-only -q $(cat shard-files.txt)")
    run = _index(steps, "--junitxml=junit.xml")
    between = [s.get("run") or "" for s in steps[counted + 1:run]]
    assert between, "no step sits between the shard's count and its run"
    for text in between:
        for target in re.findall(r"--out\s+(\S+)|>\s*(\S+)", text):
            path = next(t for t in target if t)
            assert path.startswith('"$RUNNER_TEMP/'), (path, text)


# ---------------------------------------------------------------------------
# The shard report and the totals job
# ---------------------------------------------------------------------------

JUNIT = """\
<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" errors="0" failures="0" skipped="0"
 tests="{tests}" time="1.0"><testcase classname="tests.test_x" name="test_y"
 file="tests/test_x.py" time="0.1"/></testsuite></testsuites>
"""

RUNNER = {
    "cpu_count": 4, "cpus_usable": 4, "xdist_workers": 2,
    "xdist_rule": "psutil present: physical cores",
    "memory_total_bytes": 16 * 1024 ** 3,
    "memory_available_bytes": 13 * 1024 ** 3,
    "memory_source": "/proc/meminfo MemAvailable",
    "platform": "Linux", "python": "3.13.0", "unknown": {},
}


def _shard(tmp_path, index: int, runner: dict | None, of: int = 2):
    plan = tmp_path / f"plan-{index}.json"
    plan.write_text(json.dumps({
        "index": index, "of": of, "files": ["tests/test_x.py"], "tests": 150,
        "collected_total": 300, "files_total": 2}), encoding="utf-8")
    junit = tmp_path / f"junit-{index}.xml"
    junit.write_text(JUNIT.format(tests=150), encoding="utf-8")
    facts = tmp_path / f"runner-{index}.json"
    if runner is not None:
        facts.write_text(json.dumps(runner), encoding="utf-8")
    out = tmp_path / "reports" / f"ubuntu-{index}.json"
    done = _run(TOTALS, "record", "--plan", plan, "--junit", junit,
                "--cell", json.dumps({"os": "ubuntu-latest", "python-version": "3.13"}),
                "--runner", facts, "--out", out)
    assert done.returncode == 0, done.stderr
    return json.loads(out.read_text(encoding="utf-8")), done.stdout


def test_the_shard_report_carries_the_runner_facts(tmp_path):
    report, stdout = _shard(tmp_path, 0, RUNNER)
    assert report["runner"] == RUNNER, report
    assert "4 CPUs" in stdout and "-n auto starts 2 workers" in stdout, stdout
    assert "13.0 GiB available of 16.0" in stdout, stdout


def test_a_missing_facts_file_is_recorded_as_missing_not_a_crash(tmp_path):
    """The report step runs ``if: always()``: a shard whose facts step never
    ran must still report its counts, and say the facts are missing."""
    report, stdout = _shard(tmp_path, 0, None)
    assert report["runner"] is None, report
    assert report["ran"] == 150, report
    assert "runner facts: not recorded" in stdout, stdout


def test_the_totals_job_shows_every_shards_runner(tmp_path):
    _shard(tmp_path, 0, RUNNER)
    _shard(tmp_path, 1, None)
    done = _run(TOTALS, "verify", "--reports", tmp_path / "reports", "--of", "2",
                "--cells", json.dumps([{"os": "ubuntu-latest", "python-version": "3.13"}]))
    assert done.returncode == 0, done.stdout + done.stderr
    lines = done.stdout.splitlines()
    zero = [line for line in lines if "shard 0 runner:" in line]
    one = [line for line in lines if "shard 1 runner" in line]
    assert len(zero) == 1 and "4 CPUs" in zero[0] and "2 workers" in zero[0], lines
    assert len(one) == 1 and "not recorded" in one[0], lines


# ---------------------------------------------------------------------------
# The memory reader's two platforms, each shown failing on the other's input
# ---------------------------------------------------------------------------


def _load_facts():
    spec = importlib.util.spec_from_file_location("_ci_runner_facts", FACTS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_proc_meminfo_is_read_in_kibibytes():
    facts = _load_facts()
    text = "MemTotal:       16303460 kB\nMemFree:         1000000 kB\nMemAvailable:   13631488 kB\n"
    assert facts.meminfo_bytes(text) == (16303460 * 1024, 13631488 * 1024)


@pytest.mark.parametrize("text", ["", "MemTotal: 10 kB\n", "MemAvailable: x kB\nMemTotal: 1 kB\n"])
def test_a_meminfo_without_both_numbers_is_unknown_not_zero(text):
    assert _load_facts().meminfo_bytes(text) is None
