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
