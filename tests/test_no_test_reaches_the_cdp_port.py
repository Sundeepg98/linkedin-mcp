"""The CDP port guard, shown refusing, shown failing a test by name, shown
leaving every other connection alone -- and the harness that reached the port,
shown reaching it no more.

``tests/cdp_port_guard.py`` refuses every connection a test makes to the port
``linkedin_server.config.CDP_PORT`` names, where the live lane's Chrome
listens. NOTHING HERE CAN CONNECT TO THAT PORT, and not only because the guard
refuses: each in-process test that aims at it first checks that the guard is
armed and stops if it is not, and the loud-failure control's own pytest
process is pointed at a port nothing listens on, so even a broken guard there
reaches nothing.
"""
from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path

from tests import cdp_port_guard

REPO = Path(__file__).resolve().parents[1]


def _armed() -> bool:
    """Is ``socket.socket.connect`` the guard's wrapper in this process?"""
    return "guarded_connect" in getattr(socket.socket.connect, "__qualname__", "")


def test_the_guard_is_registered_and_armed_in_this_run_with_no_flag(request):
    """``tests/conftest.py`` registers it, so every run has it, armed."""
    assert request.config.pluginmanager.hasplugin("tests.cdp_port_guard")
    assert _armed()


def test_the_shipped_probe_is_refused_before_it_connects(request):
    """THE REFUSAL, on the package's own probe. It answers as a closed port
    does, and the attempt is recorded against this test -- then taken here, so
    the report does not fail this test for the attempt it set out to make."""
    from linkedin_server import cdp_bridge

    assert _armed(), "the guard is not armed: refusing to run the probe at all"
    cdp_port_guard.take_refused()
    result = asyncio.run(cdp_bridge.probe())
    refused = cdp_port_guard.take_refused()
    assert result["reachable"] is False, result
    assert [where for _nodeid, where in refused] == [
        f"127.0.0.1:{cdp_port_guard.the_port()}"
    ], refused
    assert refused[0][0] == request.node.nodeid, refused


def test_connect_ex_to_the_port_answers_as_a_closed_port():
    """The non-raising form: the closed port's own error number, recorded."""
    assert _armed(), "the guard is not armed: refusing to aim at the port at all"
    cdp_port_guard.take_refused()
    with socket.socket() as client:
        answer = client.connect_ex(("127.0.0.1", cdp_port_guard.the_port()))
    assert answer == cdp_port_guard.REFUSED_ERRNO
    assert len(cdp_port_guard.take_refused()) == 1


def test_a_connection_to_any_other_port_is_untouched():
    """THE GUARD IS ABOUT ONE PORT. A listener this test opens on an ephemeral
    loopback port accepts the connection, and nothing is recorded."""
    cdp_port_guard.take_refused()
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        assert port != cdp_port_guard.the_port()
        with socket.socket() as client:
            client.connect(("127.0.0.1", port))
            accepted, _peer = server.accept()
            accepted.close()
    assert cdp_port_guard.take_refused() == []


def test_the_envelope_harness_drives_the_cdp_tool_without_reaching_the_port():
    """THE ONE MEASURED REACHER, FIXED AT ITS SOURCE. The tool-envelope
    harness drove ``linkedin_cdp_status`` with the probe live, one connection
    to the port per run (lane S, 2026-09-28). It stubs the probe now, so the
    drive makes no attempt at all -- the guard records none -- and the tool
    still returns its envelope, without reading a page."""
    from linkedin_server import server

    from tests import test_tool_envelopes_emit_no_page_string as envelopes

    assert _armed(), "the guard is not armed: refusing to drive the probe at all"
    cdp_port_guard.take_refused()
    row = envelopes.drive_tool("linkedin_cdp_status", server.linkedin_cdp_status)
    assert cdp_port_guard.take_refused() == []
    assert row["verdict"] == envelopes.NOT_DRIVEN, row
    assert row["reason"] == "never read the page", row


_A_TEST_THAT_PROBES_THE_PORT = '''
import asyncio

from linkedin_server import cdp_bridge


def test_it_probes():
    asyncio.run(cdp_bridge.probe())
'''


def _a_port_nothing_listens_on() -> int:
    """An ephemeral loopback port, bound and released: closed when used."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def test_a_test_that_probes_the_port_fails_loudly_by_name(tmp_path):
    """THE LOUD HALF, in its own pytest process with only this guard loaded:
    a test whose probe swallowed the refusal -- ``probe()`` never raises --
    still FAILS, and the failure names the test and the address. That process
    is given ``LINKEDIN_CDP_PORT`` = a port nothing listens on, so the guard
    and the probe there both aim at it, and 9224 is never the subject."""
    port = _a_port_nothing_listens_on()
    planted = tmp_path / "test_probes_the_port.py"
    planted.write_text(_A_TEST_THAT_PROBES_THE_PORT, encoding="ascii")
    env = dict(os.environ, PYTHONPATH=str(REPO), LINKEDIN_CDP_PORT=str(port))
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "tests.cdp_port_guard", "-p", "no:cacheprovider",
         "-q", "-o", "addopts=", "--rootdir", str(tmp_path), str(planted)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=180,
    )
    output = done.stdout + done.stderr
    assert done.returncode == 1, output[-2000:]
    assert "1 failed" in output, output[-2000:]
    assert "test_probes_the_port.py::test_it_probes REACHED FOR THE CDP PORT" in output, output[-2000:]
    assert f"127.0.0.1:{port}" in output, output[-2000:]


#: A test that logs through the package logger, passing or failing on request.
_A_TEST_THAT_LOGS = '''
import os

from linkedin_server.config import logger


def test_it_logs():
    logger.warning("SENTINEL-PACKAGE-LOG-7F3A")
    assert os.environ.get("PLANTED_LOG_TEST_FAILS") != "1"
'''


def _run_the_logging_test(tmp_path: Path, *, fails: bool) -> str:
    """The planted test under ``-n 2``, with only this guard loaded."""
    planted = tmp_path / "test_logs.py"
    planted.write_text(_A_TEST_THAT_LOGS, encoding="ascii")
    env = dict(os.environ, PYTHONPATH=str(REPO), PLANTED_LOG_TEST_FAILS="1" if fails else "0")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "tests.cdp_port_guard", "-p", "no:cacheprovider",
         "-q", "-o", "addopts=", "-n", "2", "--rootdir", str(tmp_path), str(planted)],
        cwd=str(tmp_path), env=env, capture_output=True, text=True, timeout=180,
    )
    output = done.stdout + done.stderr
    assert done.returncode == (1 if fails else 0), output[-2000:]
    return output


def test_the_guard_leaves_a_passing_tests_package_log_in_pytests_capture(tmp_path):
    """THE GUARD MAY NOT MOVE THE PACKAGE'S LOG OUT OF PYTEST'S CAPTURE.

    Its configure hook once read the port by importing
    ``linkedin_server.config``, which built the package logger's
    ``StreamHandler`` in an xdist worker BEFORE that worker's capture began:
    the handler held the worker's real stderr, and every package log line of
    a ``-n auto`` run reached the console, a passing test's included -- 5,000+
    lines in one full run, measured 2026-09-28 (lane G, the addendum of
    06:20). The port is read at the first connection now. RED on the eager
    read: the passing test's sentinel on the console.

    THE CONTROL: the same test, failing, shows the sentinel -- pytest prints
    what it captured -- so the absence above is the capture working, not a
    test that never logged."""
    passing = _run_the_logging_test(tmp_path, fails=False)
    assert "1 passed" in passing, passing[-2000:]
    assert "SENTINEL-PACKAGE-LOG-7F3A" not in passing, passing[-2000:]
    failing = _run_the_logging_test(tmp_path, fails=True)
    assert "1 failed" in failing, failing[-2000:]
    assert "SENTINEL-PACKAGE-LOG-7F3A" in failing, failing[-2000:]
