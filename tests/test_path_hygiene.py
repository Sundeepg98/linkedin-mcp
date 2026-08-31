"""No tool result publishes this machine's directory layout.

A live sweep across this family of servers on 2026-08-20 found
``D:\\Sundeep\\projects\\...`` sitting inside MCP tool results. That is wrong
twice over: it publishes the operator's directory layout into any transcript the
result is pasted into, and it is paid for in tokens on every response carrying
it.

The ruling is RELATIVISE, NOT DELETE. "Where does my session actually live" is a
real question these fields answer, and a ``null`` trades a leak for a field that
answers nothing -- the same defect wearing different clothes. So the assertions
below come in pairs: no path survives, AND the field still names the directory.

ON THE DETECTOR, which is the part that is easy to get wrong. The primary check
is :func:`contains` -- the exact path string this box built, asserted ABSENT.
The drive-letter regex in :func:`leaks` is a SECOND OPINION only. jobcore learnt
this the hard way at ``d1720c3``: its leak tests detected with a drive-letter
regex, and on an ubuntu runner the leaked path is ``/tmp/pytest-of-runner/...``
with no drive letter at all, so every assertion passed while detecting nothing.
The whole file was green on Linux and certified nothing. linkedin has no CI
today, but the suite written now is the one whoever adds it will inherit.
"""

from __future__ import annotations

import os
import re

import pytest

from linkedin_server import preflight
from linkedin_server.auth import logout, session_info_offline
from linkedin_server.config import CHROME_PROFILE, REPO_ROOT, display, scrub
from linkedin_server.server import _error, linkedin_server_info

# ---------------------------------------------------------------------------
# The instruments
# ---------------------------------------------------------------------------

#: The naive drive-letter form. Kept ONLY as the control below: it is wrong, and
#: the way it is wrong is not visible by reading it.
LOOSE_DRIVE_LETTER = re.compile(r"[A-Za-z]:[\\/]")

#: The form actually used. The lookbehind is the whole fix: without it the
#: pattern matches the ``s:/`` inside ``https://``, so it fires on every correct
#: LinkedIn URL this server emits, and a sweep that cries wolf on correct output
#: gets suppressed or deleted rather than fixed.
DRIVE_LETTER = re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/]")

#: The ONE subtree allowed to carry an absolute path, and why.
#:
#: ``preflight`` answers "there is no browser to launch -- is that because it is
#: missing, or because PLAYWRIGHT_BROWSERS_PATH never reached this process".
#: Both halves of that diagnosis ARE absolute paths, and relativising them
#: destroys it: the point of the 2026-08-22 incident was telling
#: ``D:\\dev-cache\\ms-playwright`` apart from the per-user default under
#: ``%LOCALAPPDATA%``, and the tail form renders both as
#: ``.../chromium-1234/chrome-win64/chrome.exe``. ``test_preflight.py`` pins
#: this deliberately -- it asserts the raw environment value is reported
#: verbatim, and that ``ok`` equals ``os.path.isfile(resolved_path)``, which a
#: relativised path cannot satisfy.
#:
#: So the exemption is NAMED here rather than left silent, and the test below
#: pins its BOUNDARY so it cannot quietly widen to cover a real leak.
EXEMPT = ("browser.preflight",)


def walk_strings(node, prefix=""):
    """Yield ``(dotted.path, text)`` for every string anywhere in a payload."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk_strings(value, f"{prefix}.{key}" if prefix else str(key))
    elif isinstance(node, (list, tuple)):
        for i, value in enumerate(node):
            yield from walk_strings(value, f"{prefix}[{i}]")
    elif isinstance(node, str):
        yield prefix, node


def _exempt(where):
    return any(where == e or where.startswith(e + ".") for e in EXEMPT)


def contains(payload, needle):
    """Every ``(where, text)`` holding ``needle``. THE PRIMARY DETECTOR.

    Asks the only question that means the same thing on every operating system:
    is the exact path this machine built present in the output.
    """
    return [
        (where, text)
        for where, text in walk_strings(payload)
        if not _exempt(where) and needle in text
    ]


def leaks(payload):
    """Every ``(where, text)`` matching the drive-letter form. SECOND OPINION.

    Catches a path that arrived from somewhere the test did not plant, which is
    the class :func:`contains` cannot see. Inert on Linux by construction -- so
    it is never the only assertion.
    """
    return [
        (where, text)
        for where, text in walk_strings(payload)
        if not _exempt(where) and DRIVE_LETTER.search(text)
    ]


def assert_clean(payload):
    """Both detectors, primary first, with the payload in the failure message."""
    for needle in (str(CHROME_PROFILE), str(REPO_ROOT)):
        assert contains(payload, needle) == [], (needle, payload)
    assert leaks(payload) == [], payload


def offline_result():
    return session_info_offline(
        CHROME_PROFILE,
        mode="launch",
        why_no_live_check="constructed offline by the test suite",
        attempted=False,
    )


# ---------------------------------------------------------------------------
# The instruments' own controls -- a sweep nobody can trust is worse than none
# ---------------------------------------------------------------------------


def test_the_primary_detector_can_fail():
    """Shown failing, on any OS. This is the control jobcore's suite lacked."""
    planted = {"browser": {"profile_dir": str(CHROME_PROFILE)}}

    found = contains(planted, str(CHROME_PROFILE))
    assert found and found[0][0] == "browser.profile_dir", found


def test_the_loose_pattern_fires_on_an_https_url_and_the_tightened_one_does_not():
    """Why the lookbehind is there, pinned so nobody 'simplifies' it away.

    Every job URL this server returns is ``https://www.linkedin.com/...``, and
    the obvious drive-letter pattern matches the ``s:/`` in it.
    """
    url = "https://www.linkedin.com/jobs/view/4123456789"

    assert LOOSE_DRIVE_LETTER.search(url), "control is inert; the point is lost"
    assert not DRIVE_LETTER.search(url)

    for real in (r"D:\workspace\projects\linkedin", "C:/Users/<user>/AppData", " D:\\x"):
        assert DRIVE_LETTER.search(real), real


def test_the_second_opinion_can_fail_and_is_honest_about_where_it_cannot():
    """The regex detector, shown failing -- and its blind spot stated as a fact."""
    planted = {"browser": {"profile_dir": r"D:\workspace\projects\x\_state\profile"}}
    found = leaks(planted)
    assert found and found[0][0] == "browser.profile_dir", found

    # The blind spot, asserted rather than described: a posix leak is invisible
    # to it. This is exactly why it is never the only assertion.
    posix_leak = {"browser": {"profile_dir": "/tmp/pytest-of-runner/pytest-0/profile"}}
    assert leaks(posix_leak) == []
    assert contains(posix_leak, "/tmp/pytest-of-runner/pytest-0/profile")


def test_the_preflight_exemption_is_bounded_to_preflight():
    """The named exemption must not be a hole the next leak falls through."""
    planted = {
        "browser": {
            "preflight": {"resolved_path": r"D:\dev-cache\ms-playwright\chrome.exe"},
            "profile_dir": r"D:\workspace\projects\x\_state\profile",
        }
    }
    found = dict(leaks(planted))

    assert "browser.profile_dir" in found
    assert not any(where.startswith("browser.preflight") for where in found)


# ---------------------------------------------------------------------------
# The sweep
# ---------------------------------------------------------------------------


async def test_server_info_carries_no_absolute_path():
    assert_clean(await linkedin_server_info())


def test_the_offline_session_result_carries_no_absolute_path():
    assert_clean(offline_result())


def test_the_logout_preview_names_files_without_publishing_the_layout():
    """The preview's whole job is naming files, which makes it the one payload
    in this server that is MADE of paths -- and therefore the easiest place to
    reintroduce the leak this file exists to stop.

    Nothing is erased here: confirm is not given, so the call performs nothing
    at all -- and the path it is handed is a probe under ``_state``, never the
    real profile.
    """
    # A profile path rooted in this checkout but NOT the operator's real one.
    # It exercises the relativiser against the exact prefix the primary
    # detector hunts for, while keeping every test in this suite away from the
    # one directory whose loss costs a day. Nothing is read or written either
    # way: an unconfirmed logout makes no filesystem call at all.
    probe = REPO_ROOT / "_state" / "chrome-profile-hygiene-probe"

    result = logout(probe, confirm=False)
    assert_clean(result)

    would_erase = result["preview"]["would_erase"]
    assert len(would_erase) == 4, would_erase
    # ...and still an ANSWER. A relativised path nobody can act on would be
    # the same defect wearing different clothes.
    for name in would_erase:
        assert probe.name in name, name
        assert "Cookies" in name, name


def test_an_oserror_carrying_an_absolute_path_is_scrubbed_from_the_error_payload():
    """The error path leaks what the happy path does not.

    ``_error`` is the funnel every tool routes its failures through, and it
    renders the exception as ``f"{type(exc).__name__}: {exc}"``. An OSError
    stringifies with the filename it failed on, so a call site that publishes no
    path field of its own still publishes a path. A happy-path sweep cannot see
    this class at all; only an error-path case can.
    """
    leaked = str(CHROME_PROFILE / "Default" / "Network" / "Cookies")
    payload = _error(OSError(2, "No such file or directory", leaked))

    assert contains(payload, leaked) == [], payload
    assert_clean(payload)

    # Scrubbed, not swallowed: it is still an error and still says what failed.
    assert payload["error"] == "unexpected"
    assert "chrome-profile" in payload["message"], payload
    assert "No such file or directory" in payload["message"], payload


def test_an_oserror_spells_its_filename_with_doubled_backslashes():
    """The trap that the path-string detector alone would have missed.

    ``OSError.__str__`` renders its filename through ``repr()``, so the message
    carries ``D:\\a\\b`` where the path is ``D:\a\b``. An exact
    substitution for the single-backslash form finds nothing, and the primary
    detector -- which looks for that same single-backslash form -- reports the
    payload CLEAN. It was the drive-letter second opinion that caught it.

    Both spellings are therefore registered as known paths. That keeps the
    substitution exact rather than heuristic: it is still only replacing strings
    this server knows it emitted, just in both of the ways Python spells them.
    """
    leaked = str(CHROME_PROFILE / "Default" / "Network" / "Cookies")
    message = str(OSError(2, "No such file or directory", leaked))

    # The mechanism, pinned. If a future Python stops repr-ing the filename,
    # this fails and the extra known_paths entries can be retired knowingly.
    if os.sep == "\\":
        assert leaked not in message, message
        assert leaked.replace("\\", "\\\\") in message, message

    out = scrub(message)
    assert not DRIVE_LETTER.search(out), out
    assert "chrome-profile" in out, out


def test_the_error_scrub_survives_a_path_baked_into_prose():
    """Renaming a field does not help when the path was interpolated mid-sentence.

    ``cookie_jar`` raises with the profile directory inside the message, and
    ``auth`` forwards that string into ``cookie_source``.
    """
    baked = f"chrome profile directory does not exist: {CHROME_PROFILE} -- no jar"

    out = scrub(baked)
    assert str(CHROME_PROFILE) not in out, out
    assert not DRIVE_LETTER.search(out), out
    assert "chrome-profile" in out, out


# ---------------------------------------------------------------------------
# ...and it is still an ANSWER
# ---------------------------------------------------------------------------


async def test_profile_dir_still_names_the_profile_directory():
    """Relativised, not nulled. A null would answer nothing."""
    profile_dir = (await linkedin_server_info())["browser"]["profile_dir"]

    assert profile_dir, "the field must not be null or empty"
    assert CHROME_PROFILE.name in profile_dir, profile_dir
    assert str(CHROME_PROFILE) not in profile_dir
    assert not DRIVE_LETTER.search(profile_dir)


def test_stored_in_is_relativised_on_BOTH_session_results():
    """``_durability`` is shared by the live and the offline path.

    Fixing it at the shared helper is what makes one edit cover two tool
    results; this test is what stops the second one being forgotten.
    """
    offline = offline_result()["durability"]["stored_in"]

    assert offline and CHROME_PROFILE.name in offline
    assert str(CHROME_PROFILE) not in offline
    assert not DRIVE_LETTER.search(offline)

    from linkedin_server.auth import _durability

    live = _durability("launch")["stored_in"]
    assert live == offline, "one directory must not get two spellings"


def test_attach_mode_still_says_the_session_is_not_ours():
    """The non-launch branch answers a different question and must be untouched."""
    from linkedin_server.auth import _durability

    text = _durability("attach")["stored_in"]
    assert "attached" in text and CHROME_PROFILE.name not in text


@pytest.mark.parametrize(
    "left,right",
    [
        (
            os.path.join("C:" + os.sep, "Users", "Dell", "Temp", "pytest-a", "profile"),
            os.path.join("C:" + os.sep, "Users", "Dell", "Temp", "pytest-b", "profile"),
        ),
        ("/tmp/pytest-of-runner/pytest-a/profile", "/tmp/pytest-of-runner/pytest-b/profile"),
    ],
)
def test_two_different_profile_dirs_do_not_render_to_the_same_string(left, right):
    """The defect the bare-basename fallback had: every dir renders identically.

    A renderer that collapses distinct directories to one string is not
    leak-free, it is uninformative -- and it hides the case where the server is
    pointed at the wrong profile entirely.
    """
    assert display(left) != display(right), display(left)


def test_scrub_leaves_text_that_holds_no_known_path_untouched():
    """Substitution is exact, never heuristic.

    A scrubber hunting for path-shaped text would eventually eat a URL or a
    quoted fragment of user content, which is how a scrubber does more damage
    than the leak it was written for.
    """
    text = "loading https://www.linkedin.com/jobs/ failed: timeout after 45000ms"

    assert scrub(text) is text
    assert preflight.BROWSERS_PATH_ENV in scrub(preflight.BROWSERS_PATH_ENV)


# ---------------------------------------------------------------------------
# The cookie-jar error paths, forced rather than waited for
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "failure,where",
    [
        (OSError(13, "being used by another process"), "_copy_jar"),
        (OSError(2, "No such file or directory"), "_copy_jar"),
    ],
    ids=["jar locked by a live Chrome", "jar vanished mid-read"],
)
def test_a_cookie_jar_failure_never_returns_an_absolute_path(
    monkeypatch, failure, where
):
    """FORCED, because waiting for this condition is how it went unnoticed.

    ``cookie_jar`` builds its errors as ``f"...{jar}...{exc}"``, and an
    ``OSError`` STRINGIFIES WITH THE FILENAME it failed on -- so a path
    reaches a caller through the exception text even when every interpolation
    of this server's own is relativised.

    THE GUARD THAT EXISTED WAS INTERMITTENT, and that is the real defect being
    fixed here. ``test_the_offline_session_result_carries_no_absolute_path``
    can only see this leak when something ELSE holds the jar's SQLite lock,
    which in practice means a live Chrome during the test run. It passed for a
    long time, then failed once a browser happened to be open, then passed
    again the moment the browser closed. A check whose firing depends on
    whether an unrelated process is running is not a check.

    So this forces the failure instead of hoping for it: the same class fires
    on every run, on every machine, with no browser involved.
    """
    from linkedin_server import cookie_jar

    def boom(*args, **kwargs):
        raise failure

    monkeypatch.setattr(cookie_jar, where, boom)

    with pytest.raises(cookie_jar.CookieJarUnavailableError) as excinfo:
        cookie_jar.read_jar(CHROME_PROFILE, ["li_at"])

    message = str(excinfo.value)
    assert DRIVE_LETTER.search(message) is None, message
    assert str(CHROME_PROFILE) not in message, message
    assert str(REPO_ROOT) not in message, message
    # The REASON has to survive the scrubbing -- a message stripped of both
    # its path and its explanation would be hygienic and useless.
    assert "cookie jar" in message.lower()


def test_that_forced_failure_can_actually_fail(monkeypatch):
    """The control. An unscrubbed message must trip the same assertion.

    Without this, the test above would pass just as happily against a build
    where scrubbing had been removed entirely -- it would simply never see a
    path, because it never checked that it COULD.
    """
    from linkedin_server import cookie_jar

    def boom(*args, **kwargs):
        raise OSError(13, "being used by another process")

    monkeypatch.setattr(cookie_jar, "_copy_jar", boom)
    # Neuter the scrubber the way a regression would.
    monkeypatch.setattr(cookie_jar, "scrub", lambda text: text)

    with pytest.raises(cookie_jar.CookieJarUnavailableError) as excinfo:
        cookie_jar.read_jar(CHROME_PROFILE, ["li_at"])

    assert DRIVE_LETTER.search(str(excinfo.value)) is not None, (
        "the unscrubbed message carried no drive letter, so the assertion "
        "above proves nothing on this platform"
    )
