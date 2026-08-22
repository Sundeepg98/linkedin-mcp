"""What session_info says when the browser is the thing that is broken.

The tool exists to answer "is my sign-in still good?" after a week away. The
day that question matters most is the day nothing else works -- and until
now, asking it launched a full persistent Chrome, so a broken browser took
the answer down with it.

The expiry dates were never in the browser. They are in the profile's own
sqlite cookie jar, and ``cookie_jar.py`` reads them straight off disk. What
this module pins is the line that read must not cross.

    A COOKIE IS NOT A SESSION.

``li_at`` sitting in a jar, present and unexpired, is what a healthy login
looks like. It is ALSO what a login LinkedIn revoked this morning looks like,
because revocation happens at LinkedIn and leaves the jar untouched. Three
login bugs in this family of servers came from substituting the one for the
other. So the offline path reports ``authenticated: null`` and says why, next
to the jar facts under their own labels -- two fields, never one blurred one.

Every check below has a control. The most important one is
``test_the_online_path_does_still_say_true...``: without it, "offline returns
null" would be satisfied by a function that returns null always, which would
pin nothing at all.
"""

from __future__ import annotations

import json
import time

import pytest

from linkedin_server import auth as auth_module
from linkedin_server import server as server_module
from linkedin_server.cookie_jar import WEBKIT_EPOCH_OFFSET_S
from linkedin_server.errors import BrowserUnavailableError
from tests.conftest import FakePage, me_response
from tests.test_cookie_jar import PLANTED_SECRET, cookie_row, make_profile

#: A stand-in for the message the preflight produces, carrying the two facts
#: that make it actionable. It has to survive the whole way out to the tool
#: result, or a broken browser is once again undiagnosable.
PREFLIGHT_MESSAGE = (
    r"No Playwright browser executable at C:\Users\Dell\AppData\Local"
    r"\ms-playwright\chromium-1234\chrome-win64\chrome.exe. "
    "PLAYWRIGHT_BROWSERS_PATH is unset in this server's own environment"
)


def webkit_us_in_days(days: float) -> int:
    """A Chrome ``expires_utc`` for a cookie lapsing ``days`` from now."""
    return int((time.time() + days * 86400.0 + WEBKIT_EPOCH_OFFSET_S) * 1000000)


def healthy_profile(tmp_path, days: float = 300.0):
    """A profile whose jar holds exactly what a good login looks like."""
    return make_profile(
        tmp_path,
        [
            cookie_row(
                "li_at",
                expires_utc=webkit_us_in_days(days),
                has_expires=1,
                is_persistent=1,
            ),
            cookie_row("JSESSIONID"),
        ],
    )


class _FailingSession:
    """``BROWSER.session()`` on a machine with no usable browser."""

    def __init__(self, error):
        self._error = error

    async def __aenter__(self):
        raise self._error

    async def __aexit__(self, *exc):
        return False


# ---------------------------------------------------------------------------
# The honesty contract
# ---------------------------------------------------------------------------


def test_a_perfectly_healthy_cookie_is_still_not_called_authenticated(tmp_path):
    """The whole point. The jar could not look better, and the answer is null."""
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )

    assert info["authenticated"] is None
    assert info["session_cookie"]["present"] is True
    assert info["session_cookie"]["persistent"] is True
    assert info["session_cookie"]["expired"] is False
    assert 299 <= info["session_cookie"]["expires_in_days"] <= 301


async def test_the_online_path_does_still_say_true(patched_navigation):
    """The control, and the one that gives the test above its meaning.

    "Offline returns null" is worth nothing if the live path returns null
    too -- that would be a server that had quietly stopped measuring. With
    the identity endpoint answering, the verdict is a real True.
    """
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["authenticated"] is True
    assert info["live_check"]["attempted"] is True
    assert info["live_check"]["completed"] is True
    assert info["cookie_source"] == "the live browser's own cookie jar"


def test_the_offline_result_says_in_words_that_a_cookie_is_not_a_session(
    tmp_path,
):
    """A null nobody reads is a null nobody acts on."""
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    explanation = info["live_check"]["what_it_means"].lower()

    assert "not a session" in explanation
    assert "null" in explanation
    assert info["live_check"]["attempted"] is False
    assert info["live_check"]["completed"] is False


def test_the_reason_the_live_check_could_not_run_travels_with_the_result(
    tmp_path,
):
    """The preflight's diagnosis must reach the operator, not stop at a log."""
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path),
        mode="launch",
        why_no_live_check=PREFLIGHT_MESSAGE,
    )
    assert PREFLIGHT_MESSAGE in info["live_check"]["why_not"]
    assert "PLAYWRIGHT_BROWSERS_PATH" in json.dumps(info)


def test_the_offline_path_labels_where_the_cookies_came_from(tmp_path):
    """Two sources, two labels. A reader must never have to guess which."""
    offline = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    assert "on-disk" in offline["cookie_source"]
    assert "without launching a browser" in offline["cookie_source"]


def test_the_offline_path_never_returns_a_cookie_value(tmp_path):
    """The jar's value column is planted with a token. It must not come back."""
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    assert PLANTED_SECRET not in json.dumps(info)


def test_that_leak_check_can_actually_fail():
    """The control for the assertion above, driven at input it must reject."""
    assert PLANTED_SECRET in json.dumps({"cookie": PLANTED_SECRET})


def test_an_expired_cookie_is_reported_expired_without_a_browser(tmp_path):
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path, days=-3.0),
        mode="launch",
        why_no_live_check="no browser",
    )
    assert info["session_cookie"]["expired"] is True
    assert info["session_cookie"]["expires_in_days"] < 0
    # Still not a verdict. An expired cookie is strong evidence, not a
    # measurement, and this path does not upgrade evidence into one.
    assert info["authenticated"] is None


def test_a_missing_login_reads_as_missing_rather_than_as_an_error(tmp_path):
    profile = make_profile(tmp_path, [cookie_row("JSESSIONID")])
    info = auth_module.session_info_offline(
        profile, mode="launch", why_no_live_check="no browser"
    )
    assert info["session_cookie"]["present"] is False
    assert info["csrf_cookie"]["name"] == "JSESSIONID"


def test_both_routes_failing_reports_both_reasons(tmp_path):
    """No browser AND no readable jar. Each reason is more use than a crash."""
    info = auth_module.session_info_offline(
        tmp_path / "profile-that-does-not-exist",
        mode="launch",
        why_no_live_check=PREFLIGHT_MESSAGE,
    )

    assert info["authenticated"] is None
    assert PREFLIGHT_MESSAGE in info["live_check"]["why_not"]
    assert "jar_error" in info
    assert "does not exist" in info["jar_error"]
    assert info["session_cookie"]["present"] is False


def test_the_durability_block_survives_the_offline_path(tmp_path):
    """The operator's real question -- "must I do this again?" -- is answered
    on both paths, or the fallback is a downgrade dressed as a fallback."""
    info = auth_module.session_info_offline(
        healthy_profile(tmp_path), mode="launch", why_no_live_check="no browser"
    )
    assert info["durability"]["survives_server_restart"] is True
    assert info["durability"]["survives_machine_reboot"] is True
    assert "linkedin_login_browser" in info["on_expiry"]


# ---------------------------------------------------------------------------
# The tool, end to end
# ---------------------------------------------------------------------------


async def test_the_tool_falls_back_to_the_jar_when_no_browser_can_start(
    tmp_path, monkeypatch
):
    """The failure of 2026-08-22, put to this tool.

    Every browser-backed tool dies. This one keeps answering, because the
    fact it reports was never in the browser to begin with.
    """
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    monkeypatch.setattr(
        server_module.BROWSER,
        "session",
        lambda: _FailingSession(BrowserUnavailableError(PREFLIGHT_MESSAGE)),
    )

    info = await server_module.linkedin_session_info()

    assert info["authenticated"] is None
    assert PREFLIGHT_MESSAGE in info["live_check"]["why_not"]
    # It DID try. Reporting this as "not attempted" would describe the same
    # null as a choice rather than as a failure, and the operator acts
    # differently on each.
    assert info["live_check"]["attempted"] is True
    assert info["live_check"]["completed"] is False
    assert info["session_cookie"]["present"] is True
    assert info["session_cookie"]["expires_at"].endswith("Z")
    # It must not have degraded into the generic error blob, which carries
    # none of the jar facts this tool is for.
    assert "error" not in info


async def test_the_tool_still_measures_when_the_browser_does_work(
    tmp_path, monkeypatch, patched_navigation
):
    """The control: the fallback must not have replaced the measurement."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": time.time() + 300 * 86400},
        responses=[me_response()],
    )

    class _WorkingSession:
        async def __aenter__(self):
            return page

        async def __aexit__(self, *exc):
            return False

    monkeypatch.setattr(server_module.BROWSER, "session", lambda: _WorkingSession())

    info = await server_module.linkedin_session_info()

    assert info["authenticated"] is True
    assert info["live_check"]["attempted"] is True


def _session_recorder(monkeypatch, error=None):
    """Replace BROWSER.session with something that RECORDS being called.

    Deliberately a recorder rather than a booby trap. A trap that raises
    proves nothing here: the tool catches every exception from the browser
    path on purpose, so an AssertionError raised inside it is swallowed into
    the offline fallback and the test passes either way. Measured -- the
    first version of this check passed against a mutation that removed the
    verify_live branch entirely. An external record cannot be swallowed.
    """
    calls: list[str] = []

    def session():
        calls.append("session")
        return _FailingSession(error or BrowserUnavailableError(PREFLIGHT_MESSAGE))

    monkeypatch.setattr(server_module.BROWSER, "session", session)
    return calls


async def test_verify_live_false_does_not_touch_the_browser_at_all(
    tmp_path, monkeypatch
):
    """The cheap path, and the proof that it is cheap."""
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    calls = _session_recorder(monkeypatch)

    info = await server_module.linkedin_session_info(verify_live=False)

    assert calls == [], "the browser was started for a browserless answer"
    assert info["authenticated"] is None
    assert info["live_check"]["attempted"] is False
    assert "verify_live" in info["live_check"]["why_not"]
    assert info["session_cookie"]["present"] is True


async def test_the_default_does_reach_for_the_browser(tmp_path, monkeypatch):
    """The control, and the one that gives the assertion above its teeth.

    'calls == []' is only a finding if the SAME recorder fills up on the
    default path. Without this, deleting the verify_live branch would leave
    the test above green -- which is exactly what happened when this pair was
    a raising trap instead of a recorder.
    """
    monkeypatch.setattr(server_module, "CHROME_PROFILE", healthy_profile(tmp_path))
    calls = _session_recorder(monkeypatch)

    info = await server_module.linkedin_session_info()

    assert calls == ["session"]
    # It reached for the browser, did not get one, and said so.
    assert info["authenticated"] is None
    assert info["live_check"]["attempted"] is True
    assert PREFLIGHT_MESSAGE in info["live_check"]["why_not"]
