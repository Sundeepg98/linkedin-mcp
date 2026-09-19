"""The version-skew gate, shown refusing and shown allowing.

The failure this exists to stop is on the record: playwright's chromium was
pointed at a profile a NEWER Chrome had stamped, Chromium ran its downgrade
migration, moved the profile aside and started clean, and the operator signed
in again and again (2026-08-25). Until this gate, the rule was PROSE -- a
comment in ``browser.py``, a docstring in ``scripts/start_chrome.ps1``, a
paragraph in a handoff file -- and prose is enforced only for as long as
everyone who edits the call site has read it.

A gate that only ever passes certifies nothing, so every arm is exercised
BOTH ways:

* stamp NEWER than the chromium  -> REFUSES, and the message names both
  versions and the route out;
* stamp OLDER                    -> ALLOWS;
* stamp EQUAL                    -> ALLOWS;
* no stamp file at all           -> ALLOWS (that is first-run);
* a stamp that will not parse    -> ALLOWS, and does not raise.

Two more, because each is a way the gate could be right in the small and
useless in the large:

* the COMPARISON is numeric, not textual. ``152`` vs ``151`` sorts correctly
  as strings and would pass a review; ``9`` vs ``10`` does not. There is a
  test whose only job is to fail if the comparison ever becomes a string one.
* the gate is WIRED. A refusal proved only against the function would still
  ship if ``browser.start()`` stopped calling it, so the refusal is also
  taken at the call site, and the profile lock is checked to be untaken --
  the ORDER is the design, and a version problem reported as a locked
  profile sends the operator after the wrong thing.

EVERY PROFILE DIRECTORY HERE IS SYNTHETIC. Nothing points at
``_state/chrome-profile``: a real Chrome holds that profile, and a test that
raced it could cost the very session the gate protects.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from linkedin_server import profile_version
from linkedin_server.errors import BrowserUnavailableError

#: The versions this wave actually measured on this machine, 2026-09-19.
#: Used as the fixture values so the arms are the real skew rather than an
#: invented one.
PLAYWRIGHT_CHROMIUM = "151.0.7922.34"
PROFILE_STAMPED_NEWER = "153.0.8010.48"


def make_chromium(tmp_path: Path, version: str = PLAYWRIGHT_CHROMIUM) -> str:
    """A synthetic copy of Chrome for Testing's on-disk layout.

    The executable, and beside it the ``<version>.manifest`` file whose NAME
    is how this module learns the version. Returns the executable path, which
    is what ``preflight`` hands the gate in production.
    """
    exe_dir = tmp_path / "browsers" / "chromium-1234" / "chrome-win64"
    exe_dir.mkdir(parents=True)
    exe = exe_dir / "chrome.exe"
    exe.write_text("stand-in for the chromium binary", encoding="utf-8")
    (exe_dir / f"{version}.manifest").write_text("", encoding="utf-8")
    return str(exe)


def make_profile(tmp_path: Path, stamp: str | None) -> Path:
    """A synthetic user-data-dir, optionally carrying a ``Last Version``."""
    profile = tmp_path / "chrome-profile"
    profile.mkdir()
    if stamp is not None:
        (profile / profile_version.PROFILE_STAMP_FILE).write_text(
            stamp, encoding="utf-8"
        )
    return profile


# ---------------------------------------------------------------------------
# 1. The five arms
# ---------------------------------------------------------------------------


def test_a_newer_stamped_profile_is_refused(tmp_path):
    """The arm the gate exists for. It raises; it does not warn."""
    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    exe = make_chromium(tmp_path)

    with pytest.raises(BrowserUnavailableError) as excinfo:
        profile_version.assert_no_downgrade(profile, exe)

    message = str(excinfo.value)
    assert PROFILE_STAMPED_NEWER in message
    assert PLAYWRIGHT_CHROMIUM in message


def test_an_older_stamped_profile_is_allowed(tmp_path):
    """A forward upgrade. Chromium does this routinely and nothing is lost."""
    profile = make_profile(tmp_path, "149.0.7000.10")
    verdict = profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))
    assert verdict["ok"] is True
    assert verdict["reason"] == "older_or_equal"


def test_an_equally_stamped_profile_is_allowed(tmp_path):
    """The everyday case: the profile was last opened by this same build."""
    profile = make_profile(tmp_path, PLAYWRIGHT_CHROMIUM)
    verdict = profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))
    assert verdict["ok"] is True
    assert verdict["reason"] == "older_or_equal"


def test_a_profile_with_no_stamp_file_is_allowed(tmp_path):
    """First run. A gate that refuses a brand-new profile has broken it."""
    profile = make_profile(tmp_path, None)
    verdict = profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))
    assert verdict["ok"] is True
    assert verdict["reason"] == "no_stamp_file"


def test_a_directory_that_does_not_exist_at_all_is_allowed(tmp_path):
    """The same case one step earlier: the profile dir has yet to be made."""
    verdict = profile_version.assert_no_downgrade(
        tmp_path / "not-created-yet", make_chromium(tmp_path)
    )
    assert verdict["ok"] is True
    assert verdict["reason"] == "no_stamp_file"


@pytest.mark.parametrize(
    "stamp",
    ["garbage", "", "   ", "153.0.8010.48 (extra)", "not.a.version", "\x00\x01"],
)
def test_a_malformed_stamp_is_allowed_and_does_not_raise(tmp_path, stamp):
    """Fail OPEN on an unreadable stamp, deliberately.

    You cannot prove a downgrade you cannot read. Failing closed here would
    let one corrupt byte in a one-line file block every tool in the server,
    to prevent a failure nobody had evidence of.
    """
    profile = make_profile(tmp_path, stamp)
    verdict = profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))
    assert verdict["ok"] is True
    assert verdict["reason"] in {"no_stamp_file", "stamp_unparseable"}


def test_a_stamp_written_with_a_bom_is_still_refused(tmp_path):
    """The fail-open rule's sharpest edge, and why the read is utf-8-sig.

    Every unreadable path in this module ALLOWS, so a decoding wrinkle does
    not surface as an error -- it surfaces as a silent pass on exactly the
    input the gate exists to refuse. Written with this test failing first:
    under plain ``utf-8`` the stamp reads ``\\ufeff153.0.8010.48``, misses the
    version pattern, and the downgrade sails through as
    ``stamp_unparseable``.
    """
    profile = tmp_path / "chrome-profile"
    profile.mkdir()
    (profile / profile_version.PROFILE_STAMP_FILE).write_bytes(
        b"\xef\xbb\xbf" + PROFILE_STAMPED_NEWER.encode("ascii")
    )
    assert profile_version._read_profile_stamp(profile) == PROFILE_STAMPED_NEWER

    with pytest.raises(BrowserUnavailableError):
        profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))


def test_a_stamp_with_trailing_whitespace_and_a_newline_is_read(tmp_path):
    """Control for the reader itself: it is not fooled by ordinary file ends."""
    profile = tmp_path / "chrome-profile"
    profile.mkdir()
    (profile / profile_version.PROFILE_STAMP_FILE).write_text(
        PROFILE_STAMPED_NEWER + "  \r\n", encoding="utf-8"
    )
    assert profile_version._read_profile_stamp(profile) == PROFILE_STAMPED_NEWER


def test_an_unresolvable_chromium_version_is_allowed(tmp_path):
    """Same principle from the other side: no version, no opinion.

    The profile here is stamped NEWER -- so this passes only because the
    chromium version could not be read, which is what makes it a control on
    the fail-open rule rather than a second copy of the older-stamp test.
    """
    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    orphan = tmp_path / "somewhere" / "chrome.exe"
    orphan.parent.mkdir(parents=True)
    orphan.write_text("", encoding="utf-8")

    verdict = profile_version.assert_no_downgrade(profile, str(orphan))
    assert verdict["ok"] is True
    assert verdict["reason"] == "chromium_version_unresolved"
    assert verdict["chromium_version"] is None


def test_a_missing_executable_path_is_allowed(tmp_path):
    """``preflight`` can return ``None`` for the path. Not this gate's call."""
    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    verdict = profile_version.assert_no_downgrade(profile, None)
    assert verdict["ok"] is True
    assert verdict["reason"] == "chromium_version_unresolved"


# ---------------------------------------------------------------------------
# 2. The comparison is numeric. This is the test that fails if it stops being.
# ---------------------------------------------------------------------------


def test_the_comparison_is_not_a_string_comparison(tmp_path):
    """``"9.0.1.0" > "10.0.1.0"`` is True as text and false as versions.

    The real skew on this machine (152 vs 151, later 153 vs 151) sorts
    correctly either way, which is exactly why this needs its own case: the
    bug would not show up on the data anyone was looking at.
    """
    assert "9.0.1.0" > "10.0.1.0"  # the trap, stated

    profile = make_profile(tmp_path, "9.0.1.0")
    verdict = profile_version.assert_no_downgrade(
        profile, make_chromium(tmp_path, "10.0.1.0")
    )
    assert verdict["ok"] is True, "9 was read as newer than 10"
    assert verdict["reason"] == "older_or_equal"


def test_the_numeric_comparison_still_refuses_the_real_direction(tmp_path):
    """The control for the test above: 10 over 9 IS a downgrade."""
    profile = make_profile(tmp_path, "10.0.1.0")
    with pytest.raises(BrowserUnavailableError):
        profile_version.assert_no_downgrade(
            profile, make_chromium(tmp_path, "9.0.1.0")
        )


@pytest.mark.parametrize(
    "text,expected",
    [
        ("151.0.7922.34", (151, 0, 7922, 34)),
        ("153.0.8010.48", (153, 0, 8010, 48)),
        ("  151.0.7922.34  ", (151, 0, 7922, 34)),
        ("9", (9,)),
        ("garbage", None),
        ("", None),
        (None, None),
        ("151.0.7922.34-beta", None),
        ("v151.0.7922.34", None),
    ],
)
def test_parse_version(text, expected):
    assert profile_version.parse_version(text) == expected


# ---------------------------------------------------------------------------
# 3. Where the chromium version comes from
# ---------------------------------------------------------------------------


def test_the_version_is_read_off_the_manifest_beside_the_binary(tmp_path):
    """Primary route: the file whose NAME is the version."""
    exe = make_chromium(tmp_path, "151.0.7922.34")
    assert (
        profile_version.chromium_version_from_executable(exe) == "151.0.7922.34"
    )


def test_a_non_version_manifest_is_not_mistaken_for_one(tmp_path):
    """Control: the route matches a VERSION, not merely a ``.manifest``.

    The revision here is deliberately one no real playwright pins. Written
    first with ``chromium-1234``, this test FAILED -- the browsers.json
    fallback resolved that revision against the installed playwright and
    answered 151.0.7922.34, correctly. That is a useful accident: it is the
    fallback route demonstrated against the real package rather than a
    planted one. Isolating the manifest route needs a revision nothing knows.
    """
    exe_dir = tmp_path / "chromium-99999" / "chrome-win64"
    exe_dir.mkdir(parents=True)
    exe = exe_dir / "chrome.exe"
    exe.write_text("", encoding="utf-8")
    (exe_dir / "chrome.exe.manifest").write_text("", encoding="utf-8")

    # No version manifest and no browsers.json entry for this revision, so it
    # declines to answer rather than returning "chrome.exe".
    assert profile_version.chromium_version_from_executable(str(exe)) is None


def test_the_browsers_json_fallback_maps_a_revision_to_a_version(
    tmp_path, monkeypatch
):
    """Fallback route, for a layout with no manifest beside the binary.

    A synthetic playwright package is planted so this measures the mapping
    rather than whatever the installed playwright happens to pin today.
    """
    exe_dir = tmp_path / "browsers" / "chromium-7777" / "chrome-linux"
    exe_dir.mkdir(parents=True)
    exe = exe_dir / "chrome"
    exe.write_text("", encoding="utf-8")

    fake_pkg = tmp_path / "fake_playwright"
    (fake_pkg / "driver" / "package").mkdir(parents=True)
    (fake_pkg / "driver" / "package" / "browsers.json").write_text(
        json.dumps(
            {
                "browsers": [
                    {
                        "name": "chromium",
                        "revision": "7777",
                        "browserVersion": "177.0.1.2",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    class FakePlaywrightPackage:
        __file__ = str(fake_pkg / "__init__.py")

    monkeypatch.setitem(
        __import__("sys").modules, "playwright", FakePlaywrightPackage()
    )
    assert (
        profile_version.chromium_version_from_executable(str(exe)) == "177.0.1.2"
    )


def test_the_headless_shell_carries_the_same_version_as_the_headful_binary():
    """The assumption a HEADLESS launch rests on, turned into a check.

    Playwright publishes ONE executable path and it is the headful binary; a
    headless launch uses a separate ``chrome-headless-shell`` whose path the
    Python API does not expose -- ``preflight``'s docstring records measuring
    exactly that. So in headless mode this gate reads the version of a binary
    that is NOT the one about to run, and it is right only because playwright
    rolls the two together at one revision and one version.

    That is an assumption about somebody else's release process, which is the
    kind that stops being true silently. Asserted here against the installed
    package's own manifest, so a playwright that ever decouples them turns
    this red instead of quietly making the gate read the wrong binary.

    Not pinned to a number: what is asserted is that the two AGREE, whatever
    they are.
    """
    playwright = pytest.importorskip("playwright")
    manifest = Path(playwright.__file__).resolve().parent.joinpath(
        "driver", "package", "browsers.json"
    )
    if not manifest.is_file():  # pragma: no cover - a layout without it
        pytest.skip("this playwright ships no browsers.json")

    versions = {
        entry["name"]: (entry.get("revision"), entry.get("browserVersion"))
        for entry in json.loads(manifest.read_text(encoding="utf-8"))["browsers"]
        if entry.get("name") in {"chromium", "chromium-headless-shell"}
    }
    assert set(versions) == {"chromium", "chromium-headless-shell"}
    assert versions["chromium"] == versions["chromium-headless-shell"], (
        "playwright has decoupled the headless shell from chromium; in "
        "headless mode this gate now reads the wrong binary's version"
    )


def test_the_shipped_playwright_reports_a_parseable_version():
    """The resolver answers for the playwright THIS repo has installed.

    Not pinned to a number -- pinning 151 here would need editing on every
    ``pip install -U playwright`` and would be wrong in the direction of
    passing. What is asserted is that the route produces a version at all,
    because a resolver that silently returns ``None`` on the real install
    would make the whole gate fail open forever and every test above would
    still be green.
    """
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as pw:
        resolved = pw.chromium.executable_path
    version = profile_version.chromium_version_from_executable(str(resolved))
    assert profile_version.parse_version(version) is not None


# ---------------------------------------------------------------------------
# 4. The message. Somebody reads it at 2am with no brief in front of them.
# ---------------------------------------------------------------------------


def test_the_message_names_the_route_out(tmp_path):
    """Both versions, the profile, and how to actually proceed."""
    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    with pytest.raises(BrowserUnavailableError) as excinfo:
        profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))

    message = str(excinfo.value)
    assert str(profile) in message
    assert "LINKEDIN_CDP_ATTACH=1" in message
    assert "scripts/start_chrome.ps1" in message
    assert "DOWNGRADE" in message


def test_a_message_that_only_said_version_skew_would_fail_this_bar():
    """The control for the test above -- it can be failed.

    Same shape as ``test_preflight``'s bar on its own message: a check that
    every plausible string passes is not a check.
    """
    useless = "profile version skew detected"
    assert PLAYWRIGHT_CHROMIUM not in useless
    assert "LINKEDIN_CDP_ATTACH=1" not in useless


def test_the_message_is_pure_ascii(tmp_path):
    """This package logs through a handler that encodes cp1252 on Windows.

    A non-ASCII character in a message raises ``UnicodeEncodeError`` at the
    moment it is printed, which turns a diagnosable refusal into a second
    unrelated traceback. Measured while writing ``preflight``.
    """
    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    with pytest.raises(BrowserUnavailableError) as excinfo:
        profile_version.assert_no_downgrade(profile, make_chromium(tmp_path))
    str(excinfo.value).encode("ascii")


# ---------------------------------------------------------------------------
# 5. THE GATE IS WIRED, AND IT RUNS BEFORE THE LOCK
# ---------------------------------------------------------------------------


class _FakeContext:
    def __init__(self) -> None:
        self.pages: list = []
        self.closed = False

    def set_default_timeout(self, timeout_ms) -> None:
        pass

    async def close(self) -> None:
        self.closed = True


class _FakeChromium:
    def __init__(self, context, executable_path: str) -> None:
        self.context = context
        self.executable_path = executable_path
        self.launches = 0

    async def launch_persistent_context(self, **kwargs):
        self.launches += 1
        return self.context


class _FakePlaywright:
    def __init__(self, chromium) -> None:
        self.chromium = chromium
        self.stopped = False

    async def stop(self) -> None:
        self.stopped = True


class _FakeFactory:
    def __init__(self, pw) -> None:
        self._pw = pw

    async def start(self):
        return self._pw


@pytest.fixture
def wired_launch(tmp_path, monkeypatch):
    """A ``LinkedInBrowser`` whose launch path can be run with no browser.

    Same four substitutions ``test_launch_boundary`` makes, for the same
    reasons, plus one that matters here specifically: the profile lock file
    is redirected into tmp_path, so this test can observe whether the lock
    was taken WITHOUT being able to take or break the one a live server may
    be holding.
    """
    import playwright.async_api

    from linkedin_server import browser as browser_module
    from linkedin_server import config, profile_lock

    chromium = _FakeChromium(_FakeContext(), make_chromium(tmp_path))
    monkeypatch.setattr(
        playwright.async_api,
        "async_playwright",
        lambda: _FakeFactory(_FakePlaywright(chromium)),
    )

    profile = make_profile(tmp_path, PROFILE_STAMPED_NEWER)
    lock_file = tmp_path / "chrome-profile.lock"
    monkeypatch.setattr(config, "CHROME_PROFILE", profile)
    monkeypatch.setattr(browser_module, "CHROME_PROFILE", profile)
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", lock_file)
    monkeypatch.setattr(browser_module, "CDP_ATTACH", False)
    return chromium, profile, lock_file


async def test_the_runtime_gate_is_the_one_that_ran(wired_launch):
    """``browser.start()`` refuses. Nothing launched, and no lock was taken.

    The lock assertion is the point of the ordering: had the gate run after
    ``profile_lock.acquire()``, this refusal would have been reported to the
    operator alongside a locked profile, which is a different problem with a
    different fix.
    """
    from linkedin_server.browser import LinkedInBrowser

    chromium, profile, lock_file = wired_launch
    browser = LinkedInBrowser()
    try:
        with pytest.raises(BrowserUnavailableError) as excinfo:
            await browser.start()
        assert PROFILE_STAMPED_NEWER in str(excinfo.value)
        assert PLAYWRIGHT_CHROMIUM in str(excinfo.value)
        assert chromium.launches == 0, "the profile was opened anyway"
        assert not lock_file.exists(), "the lock was taken before the refusal"
        assert browser.running is False
    finally:
        await browser.stop()


async def test_the_same_call_site_proceeds_when_the_stamp_is_equal(wired_launch):
    """The control: with the skew removed, the launch goes through.

    Without this, the test above could be passing because ``start()`` is
    broken rather than because the gate fired.
    """
    from linkedin_server.browser import LinkedInBrowser

    chromium, profile, lock_file = wired_launch
    (profile / profile_version.PROFILE_STAMP_FILE).write_text(
        PLAYWRIGHT_CHROMIUM, encoding="utf-8"
    )

    browser = LinkedInBrowser()
    try:
        await browser.start()
        assert chromium.launches == 1
        assert browser.running is True
    finally:
        await browser.stop()
