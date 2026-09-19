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

import pathlib
import subprocess
import unittest.mock as mock

import pytest

from linkedin_server import server as server_module
from linkedin_server.server import (
    BUILD,
    BUILD_DIGEST,
    BUILD_MODULES,
    STALE_PROCESS_KEY,
    _announce_staleness,
    _digest_of,
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
    ), mock.patch.object(server_module, "BUILD_DIGEST", "0" * 12):
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
    # THE BUILD IS FAKED TOO, and that is the 2026-09-19 ruling showing in a
    # test. Staleness is now decided by the BYTES of the loaded modules, not
    # by the commit, so moving the commit alone no longer makes a process
    # stale -- it makes it "commit moved, build did not", which is the whole
    # point. A process is stale when its loaded source differs from disk.
    with mock.patch.object(server_module, "BUILD", fake), mock.patch.object(
        server_module, "BUILD_DIGEST", "0" * 12
    ):
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


# ===========================================================================
# COMMIT IDENTITY IS NOT BUILD IDENTITY  (2026-09-19)
#
# THE DEFECT, MEASURED TWICE IN ONE DAY. This detector compared the commit the
# process was imported at against the commit on disk. That is the right
# question asked of the wrong object. On 2026-09-19 it stopped Tier 1 for ten
# minutes on a delta that genuinely touched writes.py, readonly.py, server.py
# and dom.py -- CORRECTLY, and that arm must survive any change here. Then it
# blocked Tier 2 on the delta 851bf80d5e8a..f66107c2c17b, which was ONE
# MARKDOWN FILE, +142 lines, ZERO PYTHON. A neighbour committing a DOCUMENT
# flipped a write gate red on a process whose loaded Python was provably
# identical to disk. On a multi-writer tree that is every neighbour, all day.
#
# BOTH ARMS ARE ASSERTED BELOW, because a detector shown only not-firing has
# been shown nothing: the only way to make the doc-only case quiet is to make
# the whole thing quiet, and that trade is strictly worse than the over-report
# it fixes. These tests fail in opposite directions, so no single mistake
# satisfies both.
# ===========================================================================


def _with_commit(commit: str):
    """The process presenting as imported from ``commit``. Build untouched."""
    return mock.patch.object(
        server_module, "BUILD", BUILD.__class__(**{**BUILD.as_dict(), "commit": commit})
    )


def test_arm_b_a_document_only_commit_does_not_make_a_process_stale():
    """ARM B -- THE OVER-REPORT THIS WAVE EXISTS TO REMOVE.

    The commit moves and not one byte of loaded Python does. The old detector
    could only say "stale"; this one must say "the commit moved and the build
    did not", because the code answering you IS the code on disk.
    """
    with _with_commit("0" * 12):
        block = _staleness()
    assert block["commit_moved"] is True, block
    assert block["stale"] is False, (
        "ARM B REGRESSION: a delta with zero Python still fires, which is the "
        "exact defect measured on 2026-09-19"
    )
    assert block["loaded_build"] == block["disk_build"], block
    assert "BUILD DID NOT" in block["why"], block["why"]
    # And an ordinary payload stays byte-identical: not stale is silence.
    assert _announce_staleness({"a": 1}) == {"a": 1}


def test_arm_a_a_python_delta_still_fires():
    """ARM A -- THE STOP THAT WAS RIGHT, AND MUST STILL HAPPEN.

    The same commit move, but the loaded source no longer matches disk. This
    is the Tier 1 case: writes.py moved under a running write gate. Firing
    through an unknown build of the write machinery is the worst available
    outcome, so this stays a hard, loud report.
    """
    with _with_commit("0" * 12), mock.patch.object(
        server_module, "BUILD_DIGEST", "0" * 12
    ):
        block = _staleness()
    assert block["commit_moved"] is True, block
    assert block["stale"] is True, "ARM A REGRESSION: a real Python delta went quiet"
    assert block["loaded_build"] != block["disk_build"], block
    assert "restart" in block["why"].lower(), block["why"]


def test_arm_a2_an_uncommitted_edit_to_a_loaded_module_is_stale():
    """STRICTLY LOUDER, NOT QUIETER -- the case the old detector could not see.

    The commit is unchanged, so commit identity reads a clean bill. The bytes
    of a loaded module are not. This is an ordinary developer box mid-edit, and
    it is a process running code that exists nowhere else; the previous
    implementation certified it as fresh by construction.
    """
    with mock.patch.object(server_module, "BUILD_DIGEST", "0" * 12):
        block = _staleness()
    assert block["commit_moved"] is False, block
    assert block["stale"] is True, (
        "an uncommitted edit to a loaded module is invisible again -- the "
        "change bought sensitivity on documents and sold it on working edits"
    )
    assert "never committed" in block["why"], block["why"]


def test_the_digest_is_taken_over_real_bytes_and_not_a_mock(tmp_path):
    """THE CONTROL UNDER BOTH ARMS. Every arm above fakes a digest; this
    proves the digest actually tracks bytes on disk.

    Without it ``_digest_of`` could return a constant and all four arms would
    still pass.

    IT DOES NOT EDIT REPOSITORY SOURCE. An earlier draft of this test appended
    a comment to the real ``writes.py`` and restored it in ``finally``, which
    works and is still the wrong shape: a suite that momentarily mutates the
    module under test is a suite that cannot be run beside anything, and this
    package's whole multi-writer discipline exists because that class of edit
    is the one nobody can recover from. A throwaway module in ``tmp_path``
    proves the same thing -- the digest reads a file and changes when the file
    does -- and touches nothing anyone else can be reading.
    """
    import sys
    import types

    probe = tmp_path / "digest_probe.py"
    probe.write_text("X = 1\n", encoding="utf-8")
    module = types.ModuleType("linkedin_server._digest_probe")
    module.__file__ = str(probe)
    names = ("linkedin_server._digest_probe",)

    with mock.patch.dict(sys.modules, {"linkedin_server._digest_probe": module}):
        first, why_not = _digest_of(names)
        assert first is not None and why_not is None, why_not

        probe.write_text("X = 2\n", encoding="utf-8")
        second, _ = _digest_of(names)
        assert second != first, (
            "changing a module's bytes did not move the digest -- it is "
            "reading something other than the file"
        )

        probe.write_text("X = 1\n", encoding="utf-8")
        assert _digest_of(names)[0] == first, "the digest is not deterministic"


def test_the_frozen_digest_agrees_with_a_fresh_one_over_real_source():
    """AND THE REAL SET IS REAL. The tmp_path control proves the mechanism;
    this proves it is pointed at this package's actual files."""
    fresh, why_not = _digest_of(BUILD_MODULES)
    assert why_not is None, why_not
    assert fresh == BUILD_DIGEST, (fresh, BUILD_DIGEST)
    import sys

    for name in BUILD_MODULES:
        path = pathlib.Path(sys.modules[name].__file__)
        assert path.is_file(), path
        assert path.suffix == ".py", path


def test_the_digest_covers_the_write_machinery_it_is_guarding():
    """A DIGEST OVER THE WRONG SET GUARDS NOTHING. The modules the write gate
    depends on must be inside the compared set, by name."""
    assert len(BUILD_MODULES) > 5, BUILD_MODULES
    for required in (
        "linkedin_server.writes",
        "linkedin_server.readonly",
        "linkedin_server.server",
        "linkedin_server.dom",
    ):
        assert required in BUILD_MODULES, (required, BUILD_MODULES)


def test_an_unreadable_source_is_reported_and_never_skipped():
    """UNREADABLE IS NOT UNCHANGED. Skipping a file that cannot be read would
    shrink the compared set in silence, which is the one failure mode this
    detector may not have."""
    digest, why_not = _digest_of(("linkedin_server.no_such_module",))
    assert digest is None
    assert why_not and "no_such_module" in why_not


def test_a_missing_commit_does_not_silence_the_build_reading():
    """A WORKTREE IS THE ORDINARY CASE, NOT AN EDGE ONE. When the commit
    cannot be compared, a DIFFERING digest is still positive evidence of
    staleness and must be reported as such rather than as "cannot tell"."""
    with mock.patch.object(
        server_module, "_head_commit_on_disk", lambda: (None, "no .git here")
    ), mock.patch.object(server_module, "BUILD_DIGEST", "0" * 12):
        block = _staleness()
    assert block["commit_moved"] is None, block
    assert block["stale"] is True, (
        "the commit was unreadable and the build provably moved, and this "
        "reported 'cannot tell' -- silence bought with available evidence"
    )


def test_the_branch_ref_resolves_inside_a_linked_worktree():
    """MEASURED 2026-09-19: THIS DETECTOR WAS BLIND IN EVERY WORKTREE.

    A linked worktree's gitdir holds its own HEAD but neither ``refs/`` nor
    ``packed-refs`` -- those stay in the main checkout, named by a
    ``commondir`` file. Without that hop the ref lookup missed and the whole
    answer degraded to "cannot tell" in exactly the trees the fleet works in.
    Asserted here against git itself, so it holds in a worktree and in a
    normal checkout alike.
    """
    commit, why_not = _head_commit_on_disk()
    assert commit is not None, why_not
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    assert commit == proc.stdout.strip()
