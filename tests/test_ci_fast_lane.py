"""The CI plan job gives a ``ci/`` push the small matrix and everything else
the full one -- shown by RUNNING the plan step, not by reading it.

WHY RUN IT. The matrix is decided by a bash script inside
``.github/workflows/ci.yml``'s plan job, and every downstream job (the shards,
the totals guard) reads that script's outputs. A regex over the YAML would
certify the literals and not the branch that picks between them -- and the
branch is the whole change. So this file loads the workflow, takes the plan
step's ``run`` text and its ``env`` names, and executes it under bash once per
event shape, with ``GITHUB_OUTPUT`` pointed at a temp file, exactly the
contract a runner gives it.

THE CONTROLS ARE THE NEIGHBOURS OF ``ci/``. ``ci-offload`` is a real
published ref name, ``cilane`` shares the prefix without the slash, a TAG
under ``ci/`` is not a branch, and a ``workflow_dispatch`` on a ``ci/`` ref is
a person asking for the full matrix. Each must get the FULL shape; a
condition loose enough to catch any of them would hand a non-lane run four
shards and one platform.

actionlint is not installed on the box this was written on, so the YAML is
validated by loading it and by the structural checks below; that limit is
recorded in ``_audit/2026-10-10-lane-ci-fastlane.md``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
WORKFLOW = REPO / ".github" / "workflows" / "ci.yml"

FULL_CELLS = [
    {"os": "ubuntu-latest", "python-version": "3.10"},
    {"os": "ubuntu-latest", "python-version": "3.13"},
    {"os": "windows-latest", "python-version": "3.13"},
]
FULL = {"count": "6", "shards": list(range(6)), "cells": FULL_CELLS}
FAST = {"count": "4", "shards": list(range(4)),
        "cells": [{"os": "ubuntu-latest", "python-version": "3.13"}]}


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _bash() -> str:
    """Git's bash on Windows (System32's bash.exe is WSL), PATH's elsewhere."""
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            for root in Path(git).resolve().parents:
                candidate = root / "bin" / "bash.exe"
                if candidate.is_file():
                    return str(candidate)
    found = shutil.which("bash")
    if found and "system32" not in found.lower():
        return found
    pytest.fail("no bash to run the plan step with -- this check cannot "
                "speak without one, and a skip would read as a pass")


def _run_plan(tmp_path: Path, event: str, ref: str) -> dict:
    step = _workflow()["jobs"]["plan"]["steps"][0]
    assert step.get("id") == "plan", step

    shim_dir = tmp_path / "shim"
    shim_dir.mkdir(exist_ok=True)
    shim = shim_dir / "python3"
    interpreter = sys.executable.replace("\\", "/")
    shim.write_text(f'#!/bin/sh\nexec "{interpreter}" "$@"\n', encoding="utf-8",
                    newline="\n")
    shim.chmod(0o755)
    script = tmp_path / "plan.sh"
    script.write_text(step["run"], encoding="utf-8", newline="\n")
    output = tmp_path / f"out-{event}-{ref.replace('/', '_')}.txt"
    output.write_text("", encoding="utf-8")

    env = dict(os.environ)
    env.update({
        "EVENT": event,
        "REF": ref,
        "GITHUB_OUTPUT": str(output).replace("\\", "/"),
        "PATH": str(shim_dir) + os.pathsep + env.get("PATH", ""),
    })
    done = subprocess.run([_bash(), str(script).replace("\\", "/")], env=env,
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr

    got: dict = {}
    for line in output.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        got[key] = value if key == "count" else json.loads(value)
    return got


@pytest.mark.parametrize("event, ref", [
    ("push", "refs/heads/master"),
    ("pull_request", "refs/pull/7/merge"),
    ("workflow_dispatch", "refs/heads/master"),
    ("workflow_dispatch", "refs/heads/ci/lane"),
    ("push", "refs/heads/ci-offload"),
    ("push", "refs/heads/cilane"),
    ("push", "refs/tags/ci/lane"),
    ("push", "refs/heads/lane"),
])
def test_everything_but_a_ci_push_gets_the_full_matrix(tmp_path, event, ref):
    assert _run_plan(tmp_path, event, ref) == FULL


@pytest.mark.parametrize("ref", ["refs/heads/ci/lane", "refs/heads/ci/lane/nested"])
def test_a_ci_push_gets_one_ubuntu_cell_in_four_shards(tmp_path, ref):
    assert _run_plan(tmp_path, "push", ref) == FAST


def test_the_fast_lane_fits_five_runs_in_the_free_concurrency(tmp_path):
    """Six jobs a run, never more than four at once: plan before, totals after."""
    fast = _run_plan(tmp_path, "push", "refs/heads/ci/lane")
    concurrent = len(fast["cells"]) * len(fast["shards"])
    assert concurrent == 4
    assert 5 * concurrent <= 20
    assert 1 + concurrent + 1 == 6


def test_the_matrix_and_the_totals_guard_read_the_same_plan():
    """The single-literal design the plan job's comment describes: if either
    consumer stopped reading the plan's outputs, the fast lane would change
    one and not the other, and the totals guard would expect a shape that
    never ran."""
    jobs = _workflow()["jobs"]
    matrix = jobs["test"]["strategy"]["matrix"]
    assert matrix["cell"] == "${{ fromJSON(needs.plan.outputs.cells) }}"
    assert matrix["shard"] == "${{ fromJSON(needs.plan.outputs.shards) }}"
    verify = jobs["totals"]["steps"][-1]["run"]
    assert "--of ${{ needs.plan.outputs.count }}" in verify
    assert "--cells '${{ needs.plan.outputs.cells }}'" in verify


def test_the_plan_reads_the_event_and_ref_through_env_not_the_script_text():
    """A ref name is input. ``${{ github.ref }}`` written inside ``run:`` is
    pasted into bash verbatim, so the plan reads both through ``env``."""
    step = _workflow()["jobs"]["plan"]["steps"][0]
    assert step.get("env") == {"EVENT": "${{ github.event_name }}",
                               "REF": "${{ github.ref }}"}, step.get("env")
    assert "${{" not in step["run"], "an expression is spliced into the script"


def test_the_triggers_and_the_jobs_are_still_there():
    flow = _workflow()
    # PyYAML reads the bare key `on` as the boolean True (YAML 1.1).
    triggers = flow.get("on", flow.get(True))
    assert set(triggers) == {"push", "pull_request", "workflow_dispatch"}, triggers
    assert set(flow["jobs"]) == {"plan", "test", "totals"}, list(flow["jobs"])
