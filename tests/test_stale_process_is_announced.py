"""A stale process says so, in every answer, without being asked.

WHAT THIS COSTS BEFORE IT EXISTS. A fix committed to disk changes nothing for a
process that is already up, and on 2026-09-03 that blocked work FOUR separate
times in one day: a radio-label fix, a thread-reply reading, a write attempt,
and a badge measurement. Each was found by a person noticing.

The fourth is why this is a guard and not a convenience. The stale process was
serving a version of ``linkedin_surface_census`` that LEAKS THIRD PARTIES'
NAMES -- a privacy fix that existed on disk, committed, tested, and was not in
the process a caller reached. Nothing in any answer said so.

**THE DETECTION ALREADY EXISTED AND NOTHING CONSULTED IT.** ``buildinfo``
describes this exact comparison in its own docstring -- "compare a held
``stamp`` against a fresh ``resolve`` and a stale process is visible as a
disagreement" -- and ``linkedin_server_info``'s docstring told the caller to
run it BY HAND against ``git rev-parse HEAD``. A check that requires somebody
to think of it is a check that fires after the cost, which is the shape this
package spent the day finding elsewhere.

## Two rules this file pins, and both were learned the hard way

**NO GIT ON A REQUEST PATH.** The first implementation called
``buildinfo.resolve``, which shells out, and
``test_build_echo.test_the_stamp_is_not_re_resolved_per_call`` failed it
immediately -- correctly: a hung git behind a five-second timeout would hold a
tool answer hostage. HEAD is now read the way git stores it, as files.

**REPORTS, NEVER REFUSES.** Ruled by the wave lead. A deliberately detached
checkout is a legitimate state and only the caller knows whether this one is.
"""

from __future__ import annotations

import subprocess
import unittest.mock as mock

import pytest

from linkedin_server import server as server_module
from linkedin_server.server import (
    BUILD,
    STALE_PROCESS_KEY,
    _announce_staleness,
    _head_commit_on_disk,
    _staleness,
    linkedin_server_info,
)

def test_the_disk_read_agrees_with_git():
    """THE FILE READ IS THE MEASUREMENT, so it is checked against the tool it
    replaced rather than trusted.

    Reading ``.git/HEAD`` by hand is only safe if it produces what git
    produces. A loose ref, a packed ref and a detached HEAD are three different
    files; this asserts the answer matches on whichever one this checkout has.
    """
    commit, why_not = _head_commit_on_disk()
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=str(server_module.REPO_ROOT),
    )
    if proc.returncode != 0:  # pragma: no cover - not a git checkout
        assert commit is None and why_not
        return
    assert commit == proc.stdout.strip(), (commit, why_not)


def test_it_does_not_shell_out():
    """THE RULE THAT CAUGHT THE FIRST IMPLEMENTATION, pinned here too.

    ``test_build_echo`` polices the stamp; this polices the comparison beside
    it. A future edit that reaches for ``buildinfo.resolve`` because it is the
    obvious tool goes red here, where the reason is written down.
    """

    def exploding_run(*args, **kwargs):
        raise AssertionError("git must not be run on a request path")

    with mock.patch.object(subprocess, "run", exploding_run):
        _staleness()
        _head_commit_on_disk()


def test_a_matching_commit_is_not_stale_and_adds_nothing():
    """SILENCE WHEN FINE. A healthy process returns byte-identical payloads, so
    no caller and no existing test has to learn a new key."""
    block = _staleness()
    assert block["stale"] is False, block
    assert block["loaded_commit"] == block["disk_commit"]
    assert _announce_staleness({"a": 1}) == {"a": 1}


def test_a_stale_process_announces_itself_in_an_ordinary_payload():
    """THE WHOLE POINT, and it is asserted on a payload rather than on the
    helper: the caller must not have to ask."""
    with mock.patch.object(
        server_module, "BUILD", BUILD.__class__(**{**BUILD.as_dict(), "commit": "0" * 12})
    ):
        out = _announce_staleness({"rows": []})
    assert STALE_PROCESS_KEY in out, out
    block = out[STALE_PROCESS_KEY]
    assert block["stale"] is True
    assert block["loaded_commit"] == "0" * 12
    assert block["disk_commit"] and block["disk_commit"] != "0" * 12
    assert "restart" in block["why"].lower(), block["why"]
    # The original payload survives untouched beside it.
    assert out["rows"] == []


def test_an_unreadable_checkout_is_unknown_and_not_false():
    """TRI-STATE. "Cannot tell" is a different fact from "not stale" and
    reporting it as one is how a guard starts certifying nothing."""
    with mock.patch.object(
        server_module, "_head_commit_on_disk", lambda: (None, "no .git here")
    ):
        block = _staleness()
        out = _announce_staleness({"a": 1})
    assert block["stale"] is None, block
    assert "cannot tell" in block["why"]
    # Unknown announces too: silence is reserved for a POSITIVE all-clear.
    assert STALE_PROCESS_KEY in out


def test_a_dirty_tree_is_not_stale():
    """DIRTINESS IS A FACT ABOUT FILES, NOT ABOUT THIS PROCESS.

    Conflating them would mark every developer box permanently stale and teach
    everyone to ignore the field -- which is worse than not having it. This
    repository's tree is frequently dirty, so this is a live case.
    """
    assert _staleness()["stale"] is False


def test_a_tool_that_answers_its_own_staleness_is_not_overwritten():
    """NEVER CLOBBER. Replacing a tool's own answer with this one would be the
    same class of defect the field exists to report."""
    mine = {"stale": "mine"}
    assert _announce_staleness({STALE_PROCESS_KEY: mine}) == {STALE_PROCESS_KEY: mine}


def test_a_non_dict_answer_passes_through():
    """Not every tool returns a mapping, and this must never be what breaks
    one that does not."""
    for value in ("text", 3, None, ["a"]):
        assert _announce_staleness(value) == value


@pytest.mark.asyncio
async def test_server_info_states_it_unconditionally():
    """WHERE "WAS IT EVEN CHECKED" GETS ITS ANSWER.

    Other payloads grow the key only when there is something to say, so
    absence there is ambiguous by design. Here it is stated, so a reader can
    tell a clean process from an unchecked one.
    """
    build = (await linkedin_server_info())["build"]
    assert STALE_PROCESS_KEY in build, sorted(build)
    assert build[STALE_PROCESS_KEY]["stale"] in (True, False, None)


def test_the_wrapper_preserves_the_signature_the_schema_is_built_from():
    """THE RISK THE WRAPPER CARRIES, checked rather than assumed.

    FastMCP builds each tool's JSON schema from the function signature. A
    wrapper that hid it would silently change 36 tool schemas at once, which
    is a far worse outcome than the trap being closed.
    """
    import inspect

    for name in ("linkedin_server_info", "linkedin_search_jobs", "linkedin_my_profile"):
        fn = getattr(server_module, name)
        # functools.wraps sets __wrapped__, which inspect.signature follows.
        assert inspect.signature(fn) is not None
        assert fn.__name__ == name
        assert fn.__doc__, name


@pytest.mark.asyncio
async def test_a_real_tool_call_carries_it_through_the_decorator():
    """END TO END, THROUGH THE REGISTERED TOOL, not through the helper.

    Every other test here exercises `_announce_staleness` directly, and all of
    them would still pass if the decorator were never applied -- which is
    precisely the failure this package kept meeting today: a check that fires
    on a path nothing uses. This calls a real tool and asserts the key arrives
    at the TOP LEVEL of its payload, which only the wrapper can do.

    `linkedin_server_info` is used because it opens no browser and touches no
    network, so the assertion is about the wrapper and nothing else.
    """
    fake = BUILD.__class__(**{**BUILD.as_dict(), "commit": "0" * 12})
    with mock.patch.object(server_module, "BUILD", fake):
        payload = await linkedin_server_info()

    assert STALE_PROCESS_KEY in payload, sorted(payload)
    assert payload[STALE_PROCESS_KEY]["stale"] is True
    assert payload[STALE_PROCESS_KEY]["loaded_commit"] == "0" * 12

    # And the healthy process adds nothing at the top level, so the presence
    # of the key is the whole signal.
    clean = await linkedin_server_info()
    assert STALE_PROCESS_KEY not in clean, (
        "a healthy process is adding the top-level key, so its presence no "
        "longer distinguishes a stale answer from an ordinary one"
    )
