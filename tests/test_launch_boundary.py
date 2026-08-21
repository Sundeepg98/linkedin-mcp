"""The launch boundary, checked rather than promised.

This server hands Chromium exactly two command-line flags and imports no
anti-detection library. Both halves of that are easy to state and easy to
lose, and the way they get lost is specific: a sign-in stops working one day,
somebody reaches for "just one more flag" or a stealth package to fix it, and
the change reads as reasonable in the diff because nothing in the repo says
where the line was drawn or why.

So the line is executable here. Two things are checked, and the second is the
one that is easy to skip:

* the CONSTANT -- ``config.LAUNCH_ARGS`` is exactly the two permitted flags;
* the WIRING -- what ``browser.py`` actually passes to Playwright is that
  same list. A test that only reads the constant would still pass if the
  launch call appended a flag of its own on the way out.

Every guard is also shown FAILING on something that should trip it, because a
guard that cannot fail certifies nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_own_server import browser as browser_module
from linkedin_own_server import config, profile_lock, readonly
from linkedin_own_server.browser import LinkedInBrowser
from linkedin_own_server.errors import WriteAttemptError

PACKAGE_DIR = Path(readonly.__file__).resolve().parent
MODULES = sorted(PACKAGE_DIR.glob("*.py"))


# ---------------------------------------------------------------------------
# 1. The flags themselves
# ---------------------------------------------------------------------------


def test_the_launch_args_are_exactly_the_two_permitted_flags():
    """Spelled out literally, so a third flag anywhere fails right here.

    Written as an equality against the whole tuple on purpose: a membership
    check would pass with a proxy or a spoofed user agent sitting beside the
    two that are allowed.
    """
    assert config.LAUNCH_ARGS == (
        "--disable-blink-features=AutomationControlled",
        f"--remote-debugging-port={config.CDP_PORT}",
    )


def test_the_flags_this_server_passes_are_permitted():
    """The list in config has to survive the gate in readonly."""
    assert readonly.assert_launch_flags_permitted(config.LAUNCH_ARGS) is None


def test_the_permitted_list_has_not_grown_ahead_of_what_is_used():
    """A permit for a flag nobody passes is the boundary moving in advance.

    Widening the boundary then means editing two files that have to agree,
    which is the visibility this check buys.
    """
    used = {arg.partition("=")[0] for arg in config.LAUNCH_ARGS}
    assert set(readonly.PERMITTED_LAUNCH_FLAGS) == used


# ---------------------------------------------------------------------------
# 2. The gate, shown refusing things
# ---------------------------------------------------------------------------

#: Each entry is (flag, the name the refusal must name). The last one is the
#: subtle case: the flag NAME is permitted and the value merely has something
#: appended, which is how a check that only looked at names would be talked
#: into disabling arbitrary Blink features.
FORBIDDEN_FLAGS = [
    ("--user-agent=Mozilla/5.0", "--user-agent"),
    ("--proxy-server=http://1.2.3.4:8080", "--proxy-server"),
    ("--disable-web-security", "--disable-web-security"),
    (
        "--disable-blink-features=AutomationControlled,AutomationControlledExtra",
        "--disable-blink-features",
    ),
]


@pytest.mark.parametrize("flag,offender", FORBIDDEN_FLAGS)
def test_a_flag_outside_the_boundary_is_refused(flag: str, offender: str):
    """The gate, shown failing. Without this the checks above prove nothing.

    The refusal has to NAME the flag: a message that only says "not
    permitted" leaves the next reader diffing two lists by eye.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        readonly.assert_launch_flags_permitted([flag])
    assert offender in str(excinfo.value)


def test_a_forbidden_flag_is_caught_alongside_the_permitted_ones():
    """The realistic shape of the failure: one flag appended to the two.

    Nothing gets replaced when this happens -- the working flags stay exactly
    where they were and a third joins them, which is why the check has to
    look at every argument rather than at the first one.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        readonly.assert_launch_flags_permitted(
            list(config.LAUNCH_ARGS) + ["--user-agent=Mozilla/5.0"]
        )
    assert "--user-agent" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 3. The wiring: what actually reaches Playwright
# ---------------------------------------------------------------------------


class FakeContext:
    """A persistent context, recording the little that browser.py asks of it."""

    def __init__(self) -> None:
        self.pages: list = []
        self.default_timeout = None
        self.closed = False

    def set_default_timeout(self, timeout_ms) -> None:
        self.default_timeout = timeout_ms

    async def close(self) -> None:
        self.closed = True


class FakeChromium:
    """``pw.chromium`` -- records the launch kwargs, hands back a context."""

    def __init__(self, context: FakeContext) -> None:
        self.context = context
        self.launch_kwargs: dict = {}
        self.launches = 0

    async def launch_persistent_context(self, **kwargs):
        self.launches += 1
        self.launch_kwargs = kwargs
        return self.context


class FakePlaywright:
    """What ``async_playwright().start()`` returns."""

    def __init__(self, chromium: FakeChromium) -> None:
        self.chromium = chromium
        self.stopped = False

    async def stop(self) -> None:
        self.stopped = True


class FakePlaywrightFactory:
    """What ``async_playwright()`` returns: something with an async ``start``."""

    def __init__(self, pw: FakePlaywright) -> None:
        self._pw = pw

    async def start(self) -> FakePlaywright:
        return self._pw


@pytest.fixture
def recorded_launch(tmp_path, monkeypatch) -> FakeChromium:
    """A LinkedInBrowser that can be started with no browser and no profile.

    Four things are replaced, and each one is something this test must not be
    able to touch:

    * ``async_playwright`` -- patched on ``playwright.async_api`` rather than
      on ``browser``, because ``start()`` imports it from there at call time;
    * the profile directory -- pointed at tmp_path, so the operator's real
      signed-in Chrome profile is neither read nor created;
    * the profile lock file -- likewise, so a test run can neither take nor
      break the lock a live server may be holding;
    * ATTACH mode -- forced off, since it launches nothing at all and an
      environment with the attach flag set would make this test measure
      nothing while still passing.
    """
    import playwright.async_api

    chromium = FakeChromium(FakeContext())
    pw = FakePlaywright(chromium)
    monkeypatch.setattr(
        playwright.async_api,
        "async_playwright",
        lambda: FakePlaywrightFactory(pw),
    )

    profile = tmp_path / "chrome-profile"
    monkeypatch.setattr(config, "CHROME_PROFILE", profile)
    monkeypatch.setattr(browser_module, "CHROME_PROFILE", profile)
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", tmp_path / "chrome-profile.lock")
    monkeypatch.setattr(browser_module, "CDP_ATTACH", False)
    return chromium


async def test_the_browser_passes_exactly_the_permitted_flags_to_chromium(
    recorded_launch: FakeChromium, tmp_path
):
    """The constant is not the boundary; what reaches Chromium is.

    This captures the real kwargs of ``launch_persistent_context`` and puts
    them back through the same gate, so the guarantee covers the call site
    rather than the tuple that call site is supposed to be reading.
    """
    browser = LinkedInBrowser()
    try:
        await browser.start()
        args = recorded_launch.launch_kwargs["args"]
        assert args == list(config.LAUNCH_ARGS)
        assert readonly.assert_launch_flags_permitted(args) is None
        # And the profile it opened is the temporary one, which is how we know
        # the fixture rather than the operator's real profile was in play.
        assert recorded_launch.launch_kwargs["user_data_dir"] == str(
            tmp_path / "chrome-profile"
        )
    finally:
        await browser.stop()
    assert recorded_launch.context.closed is True


async def test_a_flag_smuggled_into_browser_py_never_reaches_chromium(
    recorded_launch: FakeChromium, monkeypatch
):
    """The gate, shown failing, at the place it actually runs.

    ``start()`` puts its own flag list through the boundary before it launches
    anything, so this is not a test-time check that a future edit could ship
    around: a proxy patched into the tuple ``browser.py`` hands to Playwright
    stops the launch outright. Patching ``browser_module`` rather than
    ``config`` is what makes that meaningful -- it is the value at the call
    site, not the one the test could have re-read for itself.
    """
    monkeypatch.setattr(
        browser_module,
        "LAUNCH_ARGS",
        config.LAUNCH_ARGS + ("--proxy-server=http://127.0.0.1:9",),
    )
    browser = LinkedInBrowser()
    try:
        with pytest.raises(WriteAttemptError) as excinfo:
            await browser.start()
        assert "--proxy-server" in str(excinfo.value)
        # Nothing was launched: the refusal came before Chromium started.
        assert recorded_launch.launch_kwargs == {}
        assert browser.running is False
    finally:
        await browser.stop()


async def test_the_runtime_gate_is_the_one_that_ran(recorded_launch: FakeChromium):
    """A control for the test above: unpatched, the same path launches fine.

    Without this, a start() that raised for some unrelated reason would look
    exactly like the boundary working.
    """
    browser = LinkedInBrowser()
    try:
        await browser.start()
        assert recorded_launch.launch_kwargs["args"] == list(config.LAUNCH_ARGS)
    finally:
        await browser.stop()


# ---------------------------------------------------------------------------
# 4. No anti-detection library anywhere in the package
# ---------------------------------------------------------------------------


def test_there_are_modules_to_scan_for_evasion_imports():
    """Guards against a scan that passes because it found nothing to look at."""
    assert len(MODULES) >= 9, [m.name for m in MODULES]


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_no_module_imports_an_evasion_library(module: Path):
    source = module.read_text(encoding="utf-8")
    hits = readonly.scan_source_for_evasion(source)
    assert hits == [], (
        f"{module.name} imports an anti-detection library: {hits}. The two "
        "launch flags are the whole boundary; a stealth, captcha, "
        "fingerprint or TLS-spoofing dependency is past it, and adding one "
        "is the operator's call rather than a code review's."
    )


def test_every_named_evasion_family_has_a_pattern():
    """The families the boundary was drawn around, none quietly dropped."""
    labels = {label for label, _ in readonly.EVASION_IMPORT_PATTERNS}
    assert {
        "stealth",
        "undetected",
        "captcha",
        "useragent_spoofing",
        "tls_spoofing",
        "fingerprint",
    } <= labels, labels


#: One import line per family in EVASION_IMPORT_PATTERNS, written in the
#: shapes these packages are actually imported in.
PLANTED_EVASION_SOURCE = """
import playwright_stealth
from selenium_stealth import stealth
import undetected_chromedriver as uc
from twocaptcha import TwoCaptcha
from fake_useragent import UserAgent
from curl_cffi import requests as cffi_requests
import browserforge
"""


def test_the_evasion_scanner_catches_a_planted_import_for_every_label():
    """The scanner, shown failing. This is what makes the sweep above mean something.

    Compared against the table rather than a hardcoded set, so a family added
    to ``EVASION_IMPORT_PATTERNS`` without a line in this sample fails here:
    an unproven pattern is worth exactly as much as no pattern.
    """
    hits = readonly.scan_source_for_evasion(PLANTED_EVASION_SOURCE)
    fired = {label for _, label, _ in hits}
    expected = {label for label, _ in readonly.EVASION_IMPORT_PATTERNS}
    assert fired == expected, (fired, expected, hits)


#: The same techniques, discussed in sentences. This is what the README and
#: the docstrings in this package look like.
PROSE_ABOUT_THE_BOUNDARY = """
This server does not use playwright_stealth and never spoofs a user agent.
It does not reach for undetected_chromedriver, does not route requests
through curl_cffi or tls_client, and has no capsolver or twocaptcha account.
Fingerprint patching with browserforge is out of scope and always will be.
"""


def test_the_evasion_scanner_does_not_fire_on_prose_about_the_boundary():
    """A check that forbids documenting the boundary is worse than no check.

    The patterns anchor on an import STATEMENT for this reason: this package
    has to be able to say in plain sentences what it does not do, and the way
    it says that is by naming the libraries.
    """
    assert readonly.scan_source_for_evasion(PROSE_ABOUT_THE_BOUNDARY) == []
