"""The recovery path: reading through a browser this server did not start.

ATTACH mode exists for one situation -- the persistent profile's session has
died and a fresh automated sign-in is being refused -- and it is dangerous in
a way the primary path is not, because the browser belongs to the operator.
Three things must therefore be true of it, and each has a test here:

* it takes NO profile lock, because it owns no profile;
* it never drives a tab he opened, only one of its own;
* tearing down disconnects and leaves his browser running.

The last of those was measured against a real Chrome before it was written
down: after Playwright's ``close()`` on a CDP connection, the DevTools
endpoint still answered. These tests hold the code to that measurement.

The read-only boundary is unchanged in this mode, and the final test says so.
"""

from __future__ import annotations

import os

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import cdp_bridge, profile_lock
from linkedin_server.browser import LinkedInBrowser
from linkedin_server.errors import BrowserUnavailableError, WriteAttemptError
from tests.conftest import FakePage


# ---------------------------------------------------------------------------
# The endpoint
# ---------------------------------------------------------------------------


def test_the_endpoint_is_a_literal_ipv4_address():
    """``localhost`` is not a synonym here.

    Chrome binds the DevTools port on IPv4 only, so ``localhost`` resolves to
    ``[::1]`` first, is refused, and falls back -- measured on this machine at
    2085 ms against 35 ms. The name is the slow path, not the tidy one.
    """
    assert cdp_bridge.endpoint() == f"http://127.0.0.1:{cdp_bridge.CDP_PORT}"
    assert "localhost" not in cdp_bridge.endpoint()


def test_the_port_does_not_collide_with_the_sibling_server():
    """Naukri's browser already owns 9223 on this machine.

    Two servers on one port is not a shared port: the second to start gets no
    port at all, and finds out by failing to attach much later.
    """
    assert cdp_bridge.CDP_PORT != 9223


def test_the_start_command_is_reported_not_described():
    """An error that says "start Chrome with the flag" is not actionable.

    The command is quoted, has the port in it, and names the flag, so the
    operator can paste it rather than reconstruct it.
    """
    assert "--remote-debugging-port=" in cdp_bridge.START_COMMAND
    assert str(cdp_bridge.CDP_PORT) in cdp_bridge.START_COMMAND
    assert "chrome.exe" in cdp_bridge.START_COMMAND.lower()
    # And the second form, for the case where quitting Chrome is not on.
    assert "--user-data-dir=" in cdp_bridge.START_COMMAND_SEPARATE_PROFILE


def test_the_requirements_name_the_singleton_trap():
    """Measured: with Chrome running, the flag opens no port and says nothing.

    An operator who does not know that will run the command, see no error, and
    conclude this server is broken.
    """
    text = cdp_bridge.ATTACH_REQUIREMENTS.lower()
    assert "already running" in text
    assert "quit" in text
    assert "--user-data-dir" in text
    assert "/json/version" in text


# ---------------------------------------------------------------------------
# probe()
# ---------------------------------------------------------------------------


async def test_probe_reports_an_unreachable_port_with_the_fix(monkeypatch):
    def refuse():
        raise ConnectionRefusedError("no listener")

    monkeypatch.setattr(cdp_bridge, "_read_version", refuse)
    result = await cdp_bridge.probe()

    assert result["reachable"] is False
    assert "ConnectionRefusedError" in result["reason"]
    assert "--remote-debugging-port" in result["how_to_fix"]


async def test_probe_reports_what_answered(monkeypatch):
    monkeypatch.setattr(
        cdp_bridge,
        "_read_version",
        lambda: '{"Browser": "Chrome/151.0.7922.170", "Protocol-Version": "1.3"}',
    )
    result = await cdp_bridge.probe()

    assert result["reachable"] is True
    assert result["browser"] == "Chrome/151.0.7922.170"
    assert result["protocol_version"] == "1.3"


async def test_probe_never_raises_it_answers(monkeypatch):
    """A diagnostic that throws is one more thing to diagnose."""

    def explode():
        raise RuntimeError("something unexpected")

    monkeypatch.setattr(cdp_bridge, "_read_version", explode)
    result = await cdp_bridge.probe()
    assert result["reachable"] is False


# ---------------------------------------------------------------------------
# Fakes for a browser this process did not start
# ---------------------------------------------------------------------------


class FakeAttachedContext:
    """The operator's own browser context. Closing it closes HIS window."""

    def __init__(self, existing_pages=None):
        self.pages = list(existing_pages or [])
        self.closed = False
        self.new_pages: list[FakePage] = []
        self.timeout = None

    def set_default_timeout(self, ms):
        self.timeout = ms

    async def new_page(self):
        page = FakePage()
        self.pages.append(page)
        self.new_pages.append(page)
        return page

    async def close(self):
        self.closed = True


class FakeCdpClient:
    """What ``connect_over_cdp`` hands back. ``close()`` only disconnects."""

    def __init__(self, context):
        self.contexts = [context]
        self.disconnected = False

    async def close(self):
        self.disconnected = True


class FakePlaywrightHandle:
    def __init__(self):
        self.stopped = False

    async def stop(self):
        self.stopped = True


@pytest.fixture
def attached(monkeypatch, tmp_path):
    """Put the browser in ATTACH mode over a fake CDP connection."""
    operators_tab = FakePage(url="https://news.example.com/something-he-was-reading")
    context = FakeAttachedContext(existing_pages=[operators_tab])
    client = FakeCdpClient(context)
    handle = FakePlaywrightHandle()

    async def fake_attach():
        return handle, client, context

    monkeypatch.setattr(browser_module, "CDP_ATTACH", True)
    monkeypatch.setattr(cdp_bridge, "attach", fake_attach)
    # A lock file under tmp_path, so "no lock was taken" is a real assertion
    # rather than an accident of where the real one lives.
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", tmp_path / "chrome-profile.lock")
    return {
        "context": context,
        "client": client,
        "handle": handle,
        "operators_tab": operators_tab,
    }


# ---------------------------------------------------------------------------
# What attach mode must and must not do
# ---------------------------------------------------------------------------


async def test_attach_mode_takes_no_profile_lock(attached):
    """It owns no profile. Claiming a lock on his would block the real path."""
    browser = LinkedInBrowser()
    try:
        await browser.start()
        assert browser.running is True
        assert browser.attached is True
        assert profile_lock.held_by() is None
    finally:
        await browser.stop()


async def test_launch_mode_does_take_the_lock(monkeypatch, tmp_path):
    """The control. Without it, "no lock" above could mean the test is inert."""
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", tmp_path / "chrome-profile.lock")
    profile_lock.acquire()
    try:
        assert profile_lock.held_by() == os.getpid()
    finally:
        profile_lock.release()


async def test_attach_mode_opens_its_own_tab_and_leaves_his_alone(attached):
    """His tab is where he was. Navigating it away is not ours to do.

    A probe of this machine also found extensions opening and driving tabs of
    their own inside a brand-new profile, so "the first tab is mine" is not
    only rude -- it is wrong.
    """
    browser = LinkedInBrowser()
    try:
        async with browser.session() as page:
            assert page is not attached["operators_tab"]
            assert page in attached["context"].new_pages
            assert attached["operators_tab"].gotos == []
    finally:
        await browser.stop()


async def test_attach_mode_reuses_its_own_tab_across_calls(attached):
    """One tab, not one per tool call. His window is not ours to fill up."""
    browser = LinkedInBrowser()
    try:
        async with browser.session() as first:
            pass
        async with browser.session() as second:
            pass
        assert first is second
        assert len(attached["context"].new_pages) == 1
    finally:
        await browser.stop()


async def test_tearing_down_disconnects_and_leaves_his_browser_running(attached):
    """The measured contract: close() on a CDP client disconnects, no more.

    Closing the CONTEXT would close his window, so the teardown must not, and
    this asserts on the context's own flag rather than on the absence of an
    error.
    """
    browser = LinkedInBrowser()
    await browser.start()
    async with browser.session() as page:
        our_tab = page
    await browser.stop()

    assert attached["client"].disconnected is True
    assert attached["handle"].stopped is True
    assert attached["context"].closed is False, (
        "attach-mode teardown closed the operator's browser context"
    )
    assert our_tab.is_closed() is True
    assert attached["operators_tab"].is_closed() is False


async def test_the_teardown_check_would_notice_a_closed_context(attached):
    """The assertion above, shown failing, by running the wrong branch.

    ``_teardown`` closes the context when there is no CDP client -- which is
    correct on the launch path, where the context is ours. Clearing the client
    by hand puts the attach-mode teardown down that branch, and the operator's
    window closes. That is precisely the outcome the test above forbids, so
    this is what proves the check can fire at all.
    """
    browser = LinkedInBrowser()
    await browser.start()
    browser._cdp_client = None  # what a regression to the launch branch does
    await browser.stop()

    assert attached["context"].closed is True
    assert attached["client"].disconnected is False


async def test_a_refused_attach_says_how_to_fix_it(monkeypatch, tmp_path):
    """No browser on the port is the common case, not an exceptional one."""

    async def refuse():
        raise BrowserUnavailableError(
            f"could not attach to a browser at {cdp_bridge.endpoint()}. "
            f"{cdp_bridge.ATTACH_REQUIREMENTS}"
        )

    monkeypatch.setattr(browser_module, "CDP_ATTACH", True)
    monkeypatch.setattr(cdp_bridge, "attach", refuse)
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", tmp_path / "chrome-profile.lock")

    browser = LinkedInBrowser()
    with pytest.raises(BrowserUnavailableError) as excinfo:
        await browser.start()

    assert "--remote-debugging-port" in str(excinfo.value)
    assert profile_lock.held_by() is None


async def test_the_read_only_allowlist_still_binds_in_attach_mode(attached):
    """Attaching to his browser widens what this server CAN reach, not what
    it MAY. The same gate stands in front of every navigation."""
    browser = LinkedInBrowser()
    try:
        async with browser.session() as page:
            with pytest.raises(WriteAttemptError):
                await browser.goto(
                    page, "https://www.linkedin.com/jobs/application/1"
                )
            assert page.gotos == []
    finally:
        await browser.stop()


async def test_the_mode_is_reported_honestly(attached):
    browser = LinkedInBrowser()
    assert browser.mode == "attach"
    try:
        await browser.start()
        assert browser.attached is True
    finally:
        await browser.stop()


def test_launch_is_the_default_mode(monkeypatch):
    monkeypatch.setattr(browser_module, "CDP_ATTACH", False)
    browser = LinkedInBrowser()
    assert browser.mode == "launch"
    assert browser.attached is False
