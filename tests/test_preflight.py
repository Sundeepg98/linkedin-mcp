"""The browser preflight, and the wrong diagnosis it exists to prevent.

Every check here is written as a PAIR: the guard firing, and a control
showing the same guard can fail. A preflight that cannot fail is worse than
none, because it manufactures confidence at exactly the moment the operator
is deciding whether to download 150 MB onto a full drive.

The scenario being pinned is real and is reproduced verbatim in
``test_the_exact_failure_of_2026_08_22``: Playwright resolved
``C:\\Users\\Dell\\AppData\\Local\\ms-playwright\\...\\chrome.exe``, that path
did not exist, ``chromium-1234`` was present at ``D:\\dev-cache\\ms-playwright``
the whole time, and the only reason the two facts did not meet is that a
stdio MCP client spawned the server without passing
``PLAYWRIGHT_BROWSERS_PATH``.

Nothing here launches a browser or starts a Playwright driver. The driver is
faked, because what is under test is what this server SAYS about a path, not
Playwright's ability to resolve one.
"""

from __future__ import annotations

import os

import pytest

from linkedin_server import preflight
from linkedin_server.errors import BrowserUnavailableError

#: The path Playwright resolved on the day this module was written, when the
#: environment variable did not reach the server process.
DESKTOP_FALLBACK_PATH = (
    r"C:\Users\Dell\AppData\Local\ms-playwright\chromium-1234"
    r"\chrome-win64\chrome.exe"
)

#: Where the browsers actually were.
REAL_BROWSERS_PATH = r"D:\dev-cache\ms-playwright"

#: Measured 2026-08-22: what a HEADLESS launch asks for, which is a different
#: binary in a differently-named directory from the one above. Playwright's
#: Python API publishes no path for it, so the preflight cannot predict it and
#: the launch failure is what has to be translated.
HEADLESS_SHELL_PATH = (
    r"D:\dev-cache\ms-playwright\chromium_headless_shell-1234"
    r"\chrome-headless-shell-win64\chrome-headless-shell.exe"
)

#: Playwright's own error text, reproduced from a real failure including the
#: box-drawing banner it appends. The banner is why nothing downstream quotes
#: this message wholesale: this package logs through a StreamHandler that
#: encodes cp1252 on a Windows console, where those characters raise.
REAL_PLAYWRIGHT_ERROR = (
    "BrowserType.launch_persistent_context: Executable doesn't exist at "
    + HEADLESS_SHELL_PATH
    + "\n\u2554\u2550\u2550\u2550\u2557\n"
    "\u2551 Looks like Playwright was just installed or updated.       \u2551\n"
    "\u2551     playwright install                                     \u2551\n"
    "\u255a\u2550\u2550\u2550\u255d\n"
)


class FakeChromium:
    def __init__(self, executable_path):
        self._path = executable_path

    @property
    def executable_path(self):
        if isinstance(self._path, Exception):
            raise self._path
        return self._path


class FakePlaywright:
    """Stands in for a started Playwright. Launches nothing."""

    def __init__(self, executable_path):
        self.chromium = FakeChromium(executable_path)
        self.stopped = False

    async def stop(self):
        self.stopped = True


@pytest.fixture
def no_browsers_path(monkeypatch):
    """The environment as the MCP client actually handed it over."""
    monkeypatch.delenv(preflight.BROWSERS_PATH_ENV, raising=False)


@pytest.fixture
def browsers_path_set(monkeypatch):
    monkeypatch.setenv(preflight.BROWSERS_PATH_ENV, REAL_BROWSERS_PATH)


# ---------------------------------------------------------------------------
# The message carries BOTH facts, always
# ---------------------------------------------------------------------------


def test_the_message_names_the_resolved_path(no_browsers_path):
    message = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    assert DESKTOP_FALLBACK_PATH in message


def test_the_message_names_the_env_var_and_says_it_is_unset(no_browsers_path):
    message = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    assert "PLAYWRIGHT_BROWSERS_PATH" in message
    assert "unset" in message.lower()


def test_the_message_names_the_env_var_value_when_it_is_set(browsers_path_set):
    message = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    assert REAL_BROWSERS_PATH in message
    assert "unset" not in message.lower()


def test_the_two_env_states_produce_different_messages(monkeypatch):
    """The control for the pair above: if the value were ignored, these would
    be the same string, and the message would be carrying no diagnosis."""
    monkeypatch.delenv(preflight.BROWSERS_PATH_ENV, raising=False)
    unset = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    monkeypatch.setenv(preflight.BROWSERS_PATH_ENV, REAL_BROWSERS_PATH)
    was_set = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    assert unset != was_set


def test_an_empty_env_value_counts_as_unset(monkeypatch):
    """Playwright ignores an empty value and falls back, so reporting it as
    'set to ""' would describe the config rather than the behaviour."""
    monkeypatch.setenv(preflight.BROWSERS_PATH_ENV, "   ")
    assert preflight.browsers_path_setting() is None
    assert "unset" in preflight.missing_browser_message("X").lower()


def test_the_message_is_pure_ascii(browsers_path_set):
    """Nothing this module writes may carry the characters that raised a
    UnicodeEncodeError when Playwright's own banner met a cp1252 console."""
    message = preflight.missing_browser_message(DESKTOP_FALLBACK_PATH)
    message.encode("ascii")


def test_the_ascii_check_would_catch_the_banner():
    """The control for the check above, run against the real banner."""
    with pytest.raises(UnicodeEncodeError):
        REAL_PLAYWRIGHT_ERROR.encode("ascii")


# ---------------------------------------------------------------------------
# The failure of 2026-08-22, reproduced
# ---------------------------------------------------------------------------


def test_the_exact_failure_of_2026_08_22(no_browsers_path):
    """A message that would have prevented the wrong diagnosis.

    The client saw only "Executable doesn't exist at <C: path>" and concluded
    Playwright had been updated without re-downloading its browsers. What it
    could not see was that the variable pointing at the real install had not
    reached the server process. Both facts are in this one line.
    """
    playwright = FakePlaywright(DESKTOP_FALLBACK_PATH)
    with pytest.raises(BrowserUnavailableError) as excinfo:
        preflight.assert_ready(playwright, headless=False)

    message = str(excinfo.value)
    assert DESKTOP_FALLBACK_PATH in message
    assert preflight.BROWSERS_PATH_ENV in message
    assert "unset" in message.lower()
    # The mechanism, without which "unset" is just another word.
    assert "env block" in message.lower()
    assert "stdio" in message.lower()


def test_a_message_that_only_said_browser_missing_would_fail_this_bar():
    """The control. The assertions above are only worth something if a
    message lacking the pair actually fails them -- this is the message the
    server used to effectively produce, checked against the same bar."""
    poor = "No Playwright browser found. Run: playwright install chromium"
    assert DESKTOP_FALLBACK_PATH not in poor
    assert preflight.BROWSERS_PATH_ENV not in poor


def test_the_preflight_passes_when_the_executable_is_really_there(
    tmp_path, browsers_path_set
):
    """The control for the raise: the same call must NOT raise on a real file.

    Without this, the guard above could be a function that always throws.
    """
    real = tmp_path / "chrome.exe"
    real.write_text("not really chrome, but it is a file")
    verdict = preflight.assert_ready(FakePlaywright(str(real)), headless=False)
    assert verdict["ok"] is True
    assert verdict["verified_for_this_mode"] is True
    assert "message" not in verdict


def test_a_directory_is_not_an_executable(tmp_path, browsers_path_set):
    """os.path.exists would pass a directory. The check wants a FILE."""
    with pytest.raises(BrowserUnavailableError):
        preflight.assert_ready(FakePlaywright(str(tmp_path)), headless=False)


# ---------------------------------------------------------------------------
# Headless: the mode the preflight cannot cover, and says so
# ---------------------------------------------------------------------------


def test_headless_is_not_claimed_as_verified(tmp_path, browsers_path_set):
    """chrome.exe being present says nothing about chrome-headless-shell.exe.

    Measured 2026-08-22: pointing PLAYWRIGHT_BROWSERS_PATH at a directory
    holding only chromium-1234 let executable_path resolve happily and the
    headless launch still died, asking for chromium_headless_shell-1234. So
    the verdict must not claim to have covered this mode.
    """
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    verdict = preflight.check(FakePlaywright(str(real)), headless=True)
    assert verdict["ok"] is True
    assert verdict["verified_for_this_mode"] is False
    assert "chrome-headless-shell" in verdict["note"]


def test_headful_with_the_same_file_is_claimed_as_verified(
    tmp_path, browsers_path_set
):
    """The control: the field above must be able to be True, or it is decoration."""
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    verdict = preflight.check(FakePlaywright(str(real)), headless=False)
    assert verdict["verified_for_this_mode"] is True


# ---------------------------------------------------------------------------
# Translating Playwright's own failure -- the net under the preflight
# ---------------------------------------------------------------------------


def test_a_real_playwright_error_becomes_the_actionable_line(browsers_path_set):
    """The headless-shell case, which no preflight could have predicted."""
    original = RuntimeError(REAL_PLAYWRIGHT_ERROR)
    translated = preflight.translate_launch_failure(original, headless=True)

    assert isinstance(translated, BrowserUnavailableError)
    assert translated is not original
    message = str(translated)
    # The path Playwright named, not one this module guessed.
    assert HEADLESS_SHELL_PATH in message
    assert preflight.BROWSERS_PATH_ENV in message
    assert REAL_BROWSERS_PATH in message
    # And the banner did not come along for the ride.
    message.encode("ascii")


def test_an_unrelated_error_passes_through_untouched():
    """The control, and the guarantee that matters most.

    A translator that reshaped every error would turn a timeout, a locked
    profile or a crashed browser into a confident lie about a missing binary.
    Identity is asserted, not just type.
    """
    original = RuntimeError("net::ERR_CONNECTION_RESET")
    assert preflight.translate_launch_failure(original, headless=False) is original

    timeout = TimeoutError("Timeout 45000ms exceeded")
    assert preflight.translate_launch_failure(timeout, headless=False) is timeout


def test_our_own_error_is_not_translated_twice(no_browsers_path):
    """assert_ready already said it better; re-wrapping would lose its wording."""
    ours = BrowserUnavailableError("the good message")
    assert preflight.translate_launch_failure(ours, headless=False) is ours


def test_the_extractor_finds_the_path_on_a_one_line_error(browsers_path_set):
    """No trailing newline, no banner -- the regex must not need either."""
    original = RuntimeError(
        "BrowserType.launch: Executable doesn't exist at " + DESKTOP_FALLBACK_PATH
    )
    translated = preflight.translate_launch_failure(original, headless=False)
    assert DESKTOP_FALLBACK_PATH in str(translated)


# ---------------------------------------------------------------------------
# The unresolvable case
# ---------------------------------------------------------------------------


def test_a_driver_that_cannot_name_a_path_still_reports_the_env_var(
    no_browsers_path,
):
    """Even with no path to report, the half of the diagnosis we DO have goes out."""
    playwright = FakePlaywright(RuntimeError("driver is broken"))
    verdict = preflight.check(playwright, headless=False)
    assert verdict["ok"] is False
    assert verdict["resolved_path"] is None
    assert preflight.BROWSERS_PATH_ENV in verdict["message"]
    assert "driver is broken" in verdict["message"]


async def test_report_never_raises_even_when_the_driver_explodes(no_browsers_path):
    """server_info must stay answerable when the browser is what is broken."""
    verdict = await preflight.report(
        headless=False, playwright=FakePlaywright(RuntimeError("boom"))
    )
    assert verdict["ok"] is False
    assert preflight.BROWSERS_PATH_ENV in verdict["message"]


async def test_report_uses_a_supplied_driver_rather_than_starting_one(tmp_path):
    """When the browser is already up, the diagnostic costs nothing extra."""
    real = tmp_path / "chrome.exe"
    real.write_text("x")
    playwright = FakePlaywright(str(real))
    verdict = await preflight.report(headless=False, playwright=playwright)
    assert verdict["ok"] is True
    assert playwright.stopped is False


async def test_report_against_the_real_installation():
    """One end-to-end run against this machine's actual Playwright.

    Starts a driver, resolves a path, stops the driver. No browser launches
    and no profile is opened. This is the only test here that would notice
    the fake diverging from the real API -- executable_path becoming a
    method, say -- which is the failure mode a suite of fakes cannot see.
    """
    verdict = await preflight.report(headless=False)
    assert verdict["resolved_path"], verdict
    assert verdict["browsers_path_env"] == os.environ.get(
        preflight.BROWSERS_PATH_ENV
    )
    assert verdict["ok"] is os.path.isfile(verdict["resolved_path"])
