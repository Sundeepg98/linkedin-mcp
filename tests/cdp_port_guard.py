"""No test connects to the CDP port: enforced, not asked.

THE PORT. ``linkedin_server.config.CDP_PORT`` -- 9224 unless
``LINKEDIN_CDP_PORT`` says otherwise -- is where the operator's own Chrome
listens when a live session attaches to it, and every lane's brief says never
touch it. ``tests/network_guard.py`` makes "no test reaches the network" true
for every BROWSER a test opens, and says what it leaves out: a request made
outside a browser, such as ``urllib``. It also said no test makes one. One
test does.

WHAT REACHED IT, MEASURED 2026-09-28 (lane S, while gating the offline
frontier): ``tests/test_tool_envelopes_emit_no_page_string.py`` drives every
tool on a planted page, ``linkedin_cdp_status`` among them, and that tool's
``cdp_bridge.probe()`` opens ``http://127.0.0.1:<CDP_PORT>/json/version``
with ``urllib`` -- loopback, which the network guard admits by design. A
recording plugin counted one connection per run, from that module's
``verdicts`` fixture. Where nothing listens (CI, and this box when no live
session is up) the port refuses it; while a live session is attached, the
operator's Chrome answers it. The harness stubs the probe now (its
``drive_tool``); this plugin is what makes the next one impossible.

WHAT THIS DOES, for every test in every run -- CI and local, no flag, because
``tests/conftest.py`` registers it. At configure time it wraps
``socket.socket.connect`` and ``connect_ex``. A connection to
``(any host, CDP_PORT)`` is REFUSED before it is attempted --
``ConnectionRefusedError``, what a closed port answers, so the caller behaves
exactly as it does on a box where nothing listens -- and RECORDED against the
test that was running; that test then FAILS, LOUDLY, naming itself and the
address. Every other connection is untouched.

WHAT IT DOES NOT COVER, named rather than implied: a connection from a
SUBPROCESS a test starts, which this process cannot wrap -- and that includes
Playwright's ``connect_over_cdp``, which its driver process makes; the tests
of the attach path stub ``cdp_bridge.attach`` (``tests/test_cdp_attach.py``).
Nor an asyncio stream opened on Windows' proactor loop, whose connect is an
overlapped ``ConnectEx`` rather than ``socket.connect``; nothing in the
package opens one. What it does cover is every connection Python makes
through ``socket.connect`` -- ``urllib``, ``http.client``, the probe.
"""
from __future__ import annotations

import errno
import socket
from typing import Any

import pytest

#: Every refused attempt since the last report: ``(test node id, "host:port")``.
#: One list per process, which under xdist is one per worker.
_REFUSED: list[tuple[str, str]] = []

#: The test running now, so an attempt is attributed to the test that made it.
_RUNNING: dict[str, str] = {"nodeid": "<no test running>"}

#: ``(attribute, original)`` for each wrap, so unconfigure restores it.
_WRAPPED: list[tuple[str, Any]] = []

#: What a refused attempt raises, and ``connect_ex`` returns: a closed port's
#: answer on this platform (10061 on Windows, 111 on Linux, 61 on macOS), so no
#: caller can tell this guard from a port with nothing on it.
REFUSED_ERRNO = errno.ECONNREFUSED


def the_port() -> int:
    """The CDP port this package would probe, read from its own config."""
    from linkedin_server import config

    return int(config.CDP_PORT)


def take_refused() -> list[tuple[str, str]]:
    """The attempts refused since the last report, and forget them. A test
    that plants one on purpose -- this guard's own controls -- takes it here,
    so the report does not fail it for the attempt it set out to make."""
    taken = list(_REFUSED)
    _REFUSED.clear()
    return taken


def _aimed_at_the_port(address: Any, port: int) -> bool:
    try:
        return int(address[1]) == port
    except (TypeError, ValueError, IndexError):
        return False


def pytest_configure(config: Any) -> None:
    port = the_port()
    connect = socket.socket.connect
    connect_ex = socket.socket.connect_ex

    def guarded_connect(self: Any, address: Any) -> Any:
        if _aimed_at_the_port(address, port):
            _REFUSED.append((_RUNNING["nodeid"], f"{address[0]}:{address[1]}"))
            raise ConnectionRefusedError(
                REFUSED_ERRNO, "the CDP port is refused to every test (tests/cdp_port_guard.py)"
            )
        return connect(self, address)

    def guarded_connect_ex(self: Any, address: Any) -> Any:
        if _aimed_at_the_port(address, port):
            _REFUSED.append((_RUNNING["nodeid"], f"{address[0]}:{address[1]}"))
            return REFUSED_ERRNO
        return connect_ex(self, address)

    _WRAPPED.extend([("connect", connect), ("connect_ex", connect_ex)])
    socket.socket.connect = guarded_connect
    socket.socket.connect_ex = guarded_connect_ex


def pytest_unconfigure(config: Any) -> None:
    while _WRAPPED:
        name, original = _WRAPPED.pop()
        setattr(socket.socket, name, original)


def pytest_runtest_logstart(nodeid: str, location: Any) -> None:
    _RUNNING["nodeid"] = nodeid


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Any, call: Any) -> Any:
    outcome = yield
    report = outcome.get_result()
    refused = take_refused()
    if not refused:
        return
    lines = "\n".join(f"    {where}  (refused while {nodeid} ran)" for nodeid, where in refused)
    message = (
        f"{item.nodeid} REACHED FOR THE CDP PORT during {report.when}: "
        f"{len(refused)} connection(s), each refused before it was attempted "
        f"(tests/cdp_port_guard.py):\n{lines}\n"
        "The live lane's Chrome listens there. Stub the probe "
        "(cdp_bridge._read_version) the way tests/test_cdp_attach.py does."
    )
    if report.failed:
        report.sections.append(("cdp port guard", message))
    else:
        report.outcome = "failed"
        report.longrepr = message
