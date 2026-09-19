"""Rate discipline and the profile lock, without launching Chromium.

Two guarantees are checked here, and both are about restraint rather than
capability: the browser will not navigate anywhere it was not allowed to, and
it will not navigate faster than the configured floor. The third, the
cross-process profile lock, is checked against a temporary lock file -- two
processes on one Chromium user-data dir is what cost a sibling server a
37-minute outage, and reclaiming a lock wrongly would cause exactly that.
"""

from __future__ import annotations

import os
import time

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import profile_lock
from linkedin_server.browser import LinkedInBrowser
from linkedin_server.errors import BrowserUnavailableError, WriteAttemptError
from tests.conftest import FakePage


# ---------------------------------------------------------------------------
# The allowlist is enforced at the navigation boundary
# ---------------------------------------------------------------------------


async def test_a_forbidden_url_is_refused_before_anything_is_loaded():
    """The url is checked FIRST. A blocked navigation must not reach the page."""
    browser = LinkedInBrowser()
    page = FakePage()
    with pytest.raises(WriteAttemptError):
        await browser.goto(page, "https://www.linkedin.com/jobs/application/1")
    assert page.gotos == []


async def test_an_allowed_url_navigates_and_returns_the_final_url():
    browser = LinkedInBrowser()
    page = FakePage()
    page.redirect_to = "https://www.linkedin.com/login"
    final = await browser.goto(page, "https://www.linkedin.com/feed/")
    assert page.gotos == ["https://www.linkedin.com/feed/"]
    assert final == "https://www.linkedin.com/login"


async def test_a_navigation_failure_is_raised_not_swallowed():
    class ExplodingPage(FakePage):
        async def goto(self, url, **kwargs):
            raise RuntimeError("net::ERR_CONNECTION_RESET")

    browser = LinkedInBrowser()
    with pytest.raises(BrowserUnavailableError):
        await browser.goto(ExplodingPage(), "https://www.linkedin.com/feed/")


# ---------------------------------------------------------------------------
# Rate discipline
# ---------------------------------------------------------------------------


async def test_consecutive_navigations_are_spaced_by_the_configured_floor(
    monkeypatch,
):
    monkeypatch.setattr(browser_module, "MIN_NAVIGATION_INTERVAL_S", 0.25)
    browser = LinkedInBrowser()
    page = FakePage()

    started = time.monotonic()
    await browser.goto(page, "https://www.linkedin.com/feed/")
    await browser.goto(page, "https://www.linkedin.com/notifications/")
    elapsed = time.monotonic() - started

    assert elapsed >= 0.25, elapsed
    assert page.gotos == [
        "https://www.linkedin.com/feed/",
        "https://www.linkedin.com/notifications/",
    ]


async def test_the_first_navigation_is_not_delayed(monkeypatch):
    """Spacing applies BETWEEN loads. A cold server should not stall on call one."""
    monkeypatch.setattr(browser_module, "MIN_NAVIGATION_INTERVAL_S", 5.0)
    browser = LinkedInBrowser()
    started = time.monotonic()
    await browser.goto(FakePage(), "https://www.linkedin.com/feed/")
    assert time.monotonic() - started < 1.0


async def test_the_rate_gate_is_shown_actually_waiting(monkeypatch):
    """The spacing check, shown failing: with the floor at zero, no wait happens."""
    monkeypatch.setattr(browser_module, "MIN_NAVIGATION_INTERVAL_S", 0.0)
    browser = LinkedInBrowser()
    page = FakePage()
    started = time.monotonic()
    await browser.goto(page, "https://www.linkedin.com/feed/")
    await browser.goto(page, "https://www.linkedin.com/notifications/")
    assert time.monotonic() - started < 0.2


async def test_a_failed_navigation_still_consumes_its_rate_slot(monkeypatch):
    """A page that errors still hit LinkedIn, so it must still count."""
    monkeypatch.setattr(browser_module, "MIN_NAVIGATION_INTERVAL_S", 0.25)

    class ExplodingPage(FakePage):
        async def goto(self, url, **kwargs):
            raise RuntimeError("boom")

    browser = LinkedInBrowser()
    with pytest.raises(BrowserUnavailableError):
        await browser.goto(ExplodingPage(), "https://www.linkedin.com/feed/")

    started = time.monotonic()
    waited = await browser.wait_for_rate_slot()
    assert waited > 0, waited
    assert time.monotonic() - started >= 0.2


def test_nothing_in_the_package_schedules_background_work():
    """No timer, no cron, no polling loop. Every call is one the operator made."""
    from pathlib import Path

    package = Path(browser_module.__file__).resolve().parent
    banned = ("schedule.every", "APScheduler", "BackgroundScheduler", "crontab")
    offenders = {}
    for module in package.glob("*.py"):
        source = module.read_text(encoding="utf-8")
        hits = [token for token in banned if token in source]
        if hits:
            offenders[module.name] = hits
    assert offenders == {}, offenders


# ---------------------------------------------------------------------------
# The cross-process profile lock
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_lock(tmp_path, monkeypatch):
    lock_file = tmp_path / "chrome-profile.lock"
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", lock_file)
    yield lock_file


def test_acquiring_writes_our_pid(temp_lock):
    profile_lock.acquire()
    assert profile_lock.held_by() == os.getpid()
    profile_lock.release()
    assert profile_lock.held_by() is None


def test_acquiring_twice_from_the_same_process_is_allowed(temp_lock):
    """The idle-close timer stops the browser; the next call starts it again."""
    profile_lock.acquire()
    profile_lock.acquire()
    assert profile_lock.held_by() == os.getpid()
    profile_lock.release()


def test_a_live_holder_blocks_us(temp_lock, monkeypatch):
    """The whole point: never touch a profile another live process is using."""
    temp_lock.write_text("424242\n", encoding="utf-8")
    monkeypatch.setattr(profile_lock, "_pid_is_alive", lambda pid: True)
    with pytest.raises(profile_lock.ProfileLockedError) as excinfo:
        profile_lock.acquire()
    assert excinfo.value.holder_pid == 424242
    # The lock must be left exactly as it was found.
    assert temp_lock.read_text(encoding="utf-8").strip() == "424242"


def test_a_dead_holders_lock_is_reclaimed(temp_lock, monkeypatch):
    """A crashed instance must not deadlock the next one on a corpse."""
    temp_lock.write_text("424242\n", encoding="utf-8")
    monkeypatch.setattr(profile_lock, "_pid_is_alive", lambda pid: False)
    profile_lock.acquire()
    assert profile_lock.held_by() == os.getpid()
    profile_lock.release()


def test_a_garbage_lock_file_is_treated_as_stale(temp_lock):
    temp_lock.write_text("not-a-pid\n", encoding="utf-8")
    profile_lock.acquire()
    assert profile_lock.held_by() == os.getpid()
    profile_lock.release()


def test_release_never_removes_someone_elses_lock(temp_lock, monkeypatch):
    """A late shutdown racing a new owner must not unlock the new owner."""
    temp_lock.write_text("424242\n", encoding="utf-8")
    profile_lock.release()
    assert temp_lock.exists()
    assert profile_lock.held_by() == 424242


def test_release_is_safe_when_nothing_was_ever_acquired(temp_lock):
    profile_lock.release()
    profile_lock.release()
    assert profile_lock.held_by() is None


# ---------------------------------------------------------------------------
# The browser preflight, at the launch boundary
# ---------------------------------------------------------------------------
#
# What is pinned here is ORDER, and it is not cosmetic. On 2026-08-22 every
# tool in this server died at browser launch and the traceback was
# misdiagnosed, because it carried the resolved path and nothing else. If the
# missing-executable check ran AFTER the profile lock, a machine with no
# browser installed would report "the profile is locked by pid N" instead --
# a true statement about the wrong problem, sending the operator somewhere
# else entirely. So: preflight, then flags, then lock, then launch.


class _FakeContext:
    def __init__(self) -> None:
        self.pages: list = []
        self.timeout_set_to = None
        self.closed = False

    def set_default_timeout(self, ms) -> None:
        self.timeout_set_to = ms

    async def close(self) -> None:
        self.closed = True


class _FakeChromium:
    def __init__(self, executable_path, launch_error=None) -> None:
        self._path = executable_path
        self._launch_error = launch_error
        self.launches = 0

    @property
    def executable_path(self):
        return self._path

    async def launch_persistent_context(self, **kwargs):
        self.launches += 1
        if self._launch_error is not None:
            raise self._launch_error
        return _FakeContext()


class _FakePlaywright:
    def __init__(self, chromium) -> None:
        self.chromium = chromium
        self.stopped = False

    async def stop(self) -> None:
        self.stopped = True


class _FakeAsyncPlaywright:
    def __init__(self, pw) -> None:
        self._pw = pw

    async def start(self):
        return self._pw


@pytest.fixture
def launch_harness(monkeypatch, tmp_path):
    """A launch path with no Chromium, no profile and no real lock behind it.

    Returns a callable taking the executable path Playwright should resolve
    and an optional launch error, and handing back the browser plus a record
    of whether the profile lock was ever claimed.
    """
    monkeypatch.setattr(browser_module, "CDP_ATTACH", False)
    monkeypatch.setattr(browser_module, "CHROME_PROFILE", tmp_path / "profile")
    monkeypatch.setenv("PLAYWRIGHT_BROWSERS_PATH", str(tmp_path / "browsers"))

    claimed: list[str] = []
    monkeypatch.setattr(
        browser_module.profile_lock, "acquire", lambda: claimed.append("acquire")
    )
    monkeypatch.setattr(
        browser_module.profile_lock, "release", lambda: claimed.append("release")
    )

    def build(executable_path, launch_error=None):
        chromium = _FakeChromium(executable_path, launch_error)
        pw = _FakePlaywright(chromium)
        monkeypatch.setattr(
            "playwright.async_api.async_playwright",
            lambda: _FakeAsyncPlaywright(pw),
        )
        return LinkedInBrowser(), pw, chromium, claimed

    return build


async def test_a_missing_browser_is_reported_before_the_profile_lock_is_taken(
    launch_harness, tmp_path
):
    missing = str(tmp_path / "browsers" / "chromium-1234" / "chrome.exe")
    browser, pw, chromium, claimed = launch_harness(missing)

    with pytest.raises(BrowserUnavailableError) as excinfo:
        await browser.start()

    message = str(excinfo.value)
    assert missing in message
    assert "PLAYWRIGHT_BROWSERS_PATH" in message
    # The whole point of the ordering.
    assert claimed == [], claimed
    assert chromium.launches == 0
    # And no driver is left running behind the failure.
    assert pw.stopped is True
    assert browser.running is False


async def test_a_present_browser_does_take_the_profile_lock(
    launch_harness, tmp_path
):
    """The control. Without it the assertion above would pass on a lock that
    is never taken at all, which would be a very quiet way to lose it."""
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    browser, pw, chromium, claimed = launch_harness(str(real))

    await browser.start()
    try:
        assert claimed == ["acquire"], claimed
        assert chromium.launches == 1
        assert browser.running is True
    finally:
        await browser.stop()
    assert claimed == ["acquire", "release"], claimed


async def test_a_launch_that_dies_on_a_missing_executable_is_translated(
    launch_harness, tmp_path
):
    """The headless-shell case: the preflight passes and the launch still dies.

    Playwright resolves and publishes ONE path, the headful chrome.exe. A
    headless launch uses a separate chrome-headless-shell binary it does not
    publish a path for -- measured on this machine. So the preflight cannot
    catch this one, and the launch's own error has to be translated instead.
    """
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    shell = str(tmp_path / "chromium_headless_shell-1234" / "shell.exe")
    browser, pw, chromium, claimed = launch_harness(
        str(real),
        launch_error=RuntimeError(
            "BrowserType.launch_persistent_context: Executable doesn't exist "
            "at " + shell
        ),
    )

    with pytest.raises(BrowserUnavailableError) as excinfo:
        await browser.start()

    message = str(excinfo.value)
    assert shell in message
    assert "PLAYWRIGHT_BROWSERS_PATH" in message
    # It got far enough to take the lock, so it must have given it back.
    assert claimed == ["acquire", "release"], claimed


async def test_an_unrelated_launch_failure_is_not_dressed_up_as_a_missing_browser(
    launch_harness, tmp_path
):
    """The control for the translation, and the more important half of it.

    A translator that reshaped everything would tell the operator to
    reinstall Chromium when what actually happened was a crash or a timeout.
    """
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    boom = RuntimeError("Target page, context or browser has been closed")
    browser, pw, chromium, claimed = launch_harness(str(real), launch_error=boom)

    with pytest.raises(RuntimeError) as excinfo:
        await browser.start()

    assert excinfo.value is boom
    assert "PLAYWRIGHT_BROWSERS_PATH" not in str(excinfo.value)
    assert claimed == ["acquire", "release"], claimed
