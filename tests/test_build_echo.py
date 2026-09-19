"""What code is this process actually running, and since when.

A fix committed to disk changes nothing for a server that is already up. On
2026-08-21 that cost real time across this family of servers: a stale process
was diagnosed as a regression and an agent was dispatched to re-fix a bug whose
fix was already on disk. Every check available at the time was a BEHAVIOURAL
FINGERPRINT -- does this field appear, is that count right -- which cannot
distinguish "the fix is not loaded" from "the fix is wrong".

These tests pin the non-behavioural answer: ``linkedin_server_info`` reports the
commit the running process was imported from, so it can be compared against
``git rev-parse HEAD`` on disk.
"""

from __future__ import annotations

import pytest

from linkedin_server import buildinfo
from linkedin_server.server import BUILD, linkedin_server_info


async def test_the_build_block_carries_a_commit_and_a_dirty_flag():
    """The two facts that make the stamp actionable rather than decorative."""
    code = (await linkedin_server_info())["build"]["code"]

    assert code["source"] == "git", code
    assert code["commit"], code
    assert len(code["commit"]) == buildinfo.SHORT_HASH_LENGTH
    assert code["commit_full"].startswith(code["commit"])
    # dirty is a real tri-state: True/False are answers, None means git status
    # itself failed and is reported as unknown rather than guessed as clean.
    assert code["dirty"] in (True, False), code
    assert code["resolved_at"], code


async def test_the_stamp_is_not_re_resolved_per_call():
    """THE FREEZE IS THE POINT, not a performance note.

    A per-call ``git rev-parse`` run from a STALE process reports the NEW commit
    sitting on disk. That is worse than reporting nothing: it reads as
    confirmation that the fix is loaded, and the thing it confirms is false.

    The instrument is a git that cannot run. If the tool re-resolves, it must
    touch ``subprocess.run``; wiring that to raise and counting the calls makes
    a re-resolution impossible to miss and impossible to fake.
    """
    calls: list[tuple] = []

    def exploding_run(*args, **kwargs):
        calls.append(args)
        raise RuntimeError("git must not be run on a request path")

    import unittest.mock as _mock

    with _mock.patch.object(buildinfo.subprocess, "run", exploding_run):
        first = (await linkedin_server_info())["build"]["code"]
        second = (await linkedin_server_info())["build"]["code"]

    assert calls == [], "the tool shelled out to git on a request path"
    assert first["commit"] == second["commit"] == BUILD.commit
    assert first["resolved_at"] == second["resolved_at"] == BUILD.resolved_at


async def test_the_payload_says_plainly_that_there_is_no_jobcore_here():
    """An absent field is indistinguishable from a field nobody wrote.

    The sibling naukri, uplers and instahyre servers DO report a jobcore stamp
    in this block. A reader comparing two servers must not be left guessing why
    this one has none, so the absence is stated as a value rather than left as
    a hole.
    """
    build = (await linkedin_server_info())["build"]

    assert "jobcore" in build, sorted(build)
    text = str(build["jobcore"]).lower()
    assert "vendor" in text, build["jobcore"]
    # It must not fabricate a second stamp.
    assert not isinstance(build["jobcore"], dict) or "commit" not in build["jobcore"]


async def test_the_process_block_says_when_this_process_came_up():
    """Which code, and since when. Uptime is derived fresh; a cached one lies."""
    process = (await linkedin_server_info())["build"]["process"]

    import os

    assert process["pid"] == os.getpid()
    assert process["started_at"]
    assert isinstance(process["uptime_seconds"], float)
    assert process["uptime_seconds"] >= 0.0


async def test_version_and_build_commit_are_two_different_facts():
    """``version`` is a hand-maintained label; ``build.code.commit`` is measured.

    They are kept as separate fields because they fail differently: a label goes
    stale when somebody forgets to bump it, and it keeps reporting the same
    string forever whether or not the code moved. The commit cannot go stale
    without the process being stale, which is the question being asked.
    """
    info = await linkedin_server_info()

    assert info["version"], "the hand-maintained label must survive"
    assert info["build"]["code"]["commit"] != info["version"]

    doc = (linkedin_server_info.__doc__ or "").lower()
    assert "rev-parse" in doc, "the docstring must say how to USE the stamp"
    assert "stale" in doc


@pytest.mark.parametrize("name", ["BUILD", "CLOCK"])
def test_the_stamp_is_resolved_once_at_import_into_a_module_constant(name):
    """Held in a module constant, so the request path only ever reads it."""
    import linkedin_server.server as server

    assert hasattr(server, name), f"{name} must be a module-level constant"
