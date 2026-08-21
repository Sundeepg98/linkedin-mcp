"""The login gate: a cookie is a reason to ask, never an answer.

A sibling server shipped the opposite of this yesterday -- it reported success
the moment a session cookie appeared, and an anonymous cookie handed to a
signed-out visitor looks exactly like a signed-in one. Every test in this file
exists to make that specific failure impossible here, which is why several of
them assert on the REQUEST LOG rather than only on the verdict: a server can
return the right answer for the wrong reason, and that is the bug.
"""

from __future__ import annotations

import json

import pytest

from linkedin_own_server import auth as auth_module
from linkedin_own_server.auth import (
    assert_not_authwall,
    check_auth,
    login_via_browser,
    require_auth,
)
from linkedin_own_server.config import ME_API
from linkedin_own_server.errors import AuthUnknownError, NotAuthenticatedError
from tests.conftest import FakePage, FakeResponse, me_response


# ---------------------------------------------------------------------------
# check_auth
# ---------------------------------------------------------------------------


async def test_a_live_session_is_confirmed_by_the_identity_endpoint(signed_in_page):
    result = await check_auth(signed_in_page)
    assert result["authenticated"] is True
    assert result["member"] == "Alex R"
    assert result["public_identifier"] == "sundeep-g"
    assert result["checked_against"] == f"GET {ME_API}"


async def test_a_session_cookie_with_a_refused_endpoint_is_not_a_login(signed_out_page):
    """THE regression test. The cookie is present and the answer is still no."""
    result = await check_auth(signed_out_page)
    assert result["authenticated"] is False
    assert result["session_cookie_present"] is True
    assert "cookie presence is never proof" in result["reason"]


async def test_the_verdict_is_always_backed_by_an_actual_request(signed_in_page):
    """A true verdict must be traceable to a request that was really made."""
    result = await check_auth(signed_in_page)
    assert result["authenticated"] is True
    assert len(signed_in_page.request.calls) == 1
    assert signed_in_page.request.calls[0]["url"] == ME_API


async def test_no_cookie_at_all_is_still_measured_not_assumed():
    """Even with an empty jar the endpoint gets asked. Absence is not a verdict."""
    page = FakePage(cookies={}, responses=[FakeResponse(401, "")])
    result = await check_auth(page)
    assert result["authenticated"] is False
    assert result["session_cookie_present"] is False
    assert len(page.request.calls) == 1


async def test_the_csrf_header_comes_from_the_session_cookie(signed_in_page):
    """LinkedIn's own web app copies JSESSIONID into csrf-token, quotes stripped."""
    await check_auth(signed_in_page)
    headers = signed_in_page.request.calls[0]["headers"]
    assert headers["csrf-token"] == "ajax:99"
    assert headers["x-restli-protocol-version"] == "2.0.0"


async def test_an_unservable_status_is_unknown_not_signed_out():
    """LinkedIn answers 999 to requests it declines. That is not a 'no'."""
    page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(999, "")])
    result = await check_auth(page)
    assert result["authenticated"] is None
    assert "unknown" in result["reason"]


async def test_a_transport_failure_is_unknown_not_signed_out():
    page = FakePage(cookies={"li_at": "x"}, responses=[RuntimeError("connection reset")])
    result = await check_auth(page)
    assert result["authenticated"] is None
    assert "not a verdict" in result["reason"]


async def test_a_200_with_unparseable_body_is_unknown():
    page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(200, "")])
    result = await check_auth(page)
    assert result["authenticated"] is None


# ---------------------------------------------------------------------------
# Corroboration
# ---------------------------------------------------------------------------


async def test_an_authwall_redirect_turns_unknown_into_signed_out(patched_navigation):
    page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(999, "")])
    page.redirect_to = "https://www.linkedin.com/login?session_redirect=%2Ffeed"
    result = await check_auth(page, corroborate=True)
    assert result["authenticated"] is False
    assert "signed-out wall" in result["reason"]
    assert patched_navigation == ["https://www.linkedin.com/feed/"]


async def test_corroboration_never_upgrades_unknown_into_signed_in(patched_navigation):
    """Landing on the feed proves less than the identity endpoint answering.

    An unknown that reaches the feed stays unknown. A server that promoted a
    verdict on weaker evidence would be doing exactly what the cookie bug did.
    """
    page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(999, "")])
    result = await check_auth(page, corroborate=True)
    assert result["authenticated"] is None
    assert result["corroborated_with"].endswith("https://www.linkedin.com/feed/")


async def test_corroboration_is_skipped_unless_asked_for(signed_in_page):
    result = await check_auth(signed_in_page, corroborate=False)
    assert "corroborated_with" not in result
    assert signed_in_page.gotos == []


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/login",
        "https://www.linkedin.com/authwall?trk=x",
        "https://www.linkedin.com/uas/login-submit",
        "https://www.linkedin.com/checkpoint/challenge/",
    ],
)
def test_authwall_urls_are_recognised_as_signed_out(url: str):
    with pytest.raises(NotAuthenticatedError):
        assert_not_authwall(url, surface="test")


def test_a_normal_page_url_is_not_an_authwall():
    assert_not_authwall("https://www.linkedin.com/notifications/", surface="test")


# ---------------------------------------------------------------------------
# require_auth
# ---------------------------------------------------------------------------


async def test_require_auth_passes_a_live_session_through(signed_in_page):
    assert (await require_auth(signed_in_page))["authenticated"] is True


async def test_require_auth_raises_not_authenticated_on_a_refusal(signed_out_page):
    with pytest.raises(NotAuthenticatedError):
        await require_auth(signed_out_page)


async def test_require_auth_distinguishes_unknown_from_signed_out():
    """Two different exceptions, because they call for two different actions."""
    page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(999, "")])
    with pytest.raises(AuthUnknownError):
        await require_auth(page)


# ---------------------------------------------------------------------------
# The login wait
# ---------------------------------------------------------------------------


@pytest.fixture
def fast_polling(monkeypatch):
    """Collapse the poll and recheck intervals so the wait loop is testable."""
    monkeypatch.setattr(auth_module, "LOGIN_POLL_S", 0.001)
    monkeypatch.setattr(auth_module, "LOGIN_RECHECK_S", 0.0)


async def test_an_already_live_session_returns_without_opening_a_window(
    signed_in_page, patched_navigation, fast_polling
):
    result = await login_via_browser(signed_in_page, wait_seconds=5)
    assert result["authenticated"] is True
    assert result["already_signed_in"] is True
    assert patched_navigation == []


async def test_the_wait_ends_only_when_the_endpoint_confirms(
    patched_navigation, fast_polling
):
    """The cookie is there from the first tick; the wait continues regardless."""
    page = FakePage(
        cookies={"li_at": "pending", "JSESSIONID": '"ajax:7"'},
        responses=[
            FakeResponse(401, ""),  # the opening check
            FakeResponse(401, ""),  # first poll: cookie present, still refused
            me_response(),          # second poll: the real thing
        ],
    )
    result = await login_via_browser(page, wait_seconds=5)
    assert result["authenticated"] is True
    assert result["already_signed_in"] is False
    # 3 requests spent in total: the opening check, then two polls.
    assert result["checks_run"] == 3
    assert page.gotos == ["https://www.linkedin.com/login"]


async def test_a_cookie_that_never_becomes_a_session_times_out_as_false(
    patched_navigation, fast_polling
):
    """The exact shipped bug, in reverse: cookie present the whole time, no login."""
    page = FakePage(
        cookies={"li_at": "anonymous", "JSESSIONID": '"ajax:1"'},
        responses=[FakeResponse(401, "")],
        default_response=FakeResponse(401, ""),
    )
    result = await login_via_browser(page, wait_seconds=0.05)
    assert result["authenticated"] is False
    assert result["session_cookie_present"] is True
    assert "not a live session" in result["reason"]
    assert result["checks_run"] >= 1


async def test_a_closed_window_is_reported_as_false_with_a_recovery_hint(
    patched_navigation, fast_polling
):
    page = FakePage(cookies={}, responses=[FakeResponse(401, "")])
    page.close_window()
    result = await login_via_browser(page, wait_seconds=5)
    assert result["authenticated"] is False
    assert "closed" in result["reason"]
    assert "linkedin_auth_status" in result["reason"]


async def test_an_inconclusive_login_reports_unknown_not_false(
    patched_navigation, fast_polling
):
    page = FakePage(
        cookies={"li_at": "x"},
        responses=[FakeResponse(401, "")],
        default_response=FakeResponse(999, ""),
    )
    result = await login_via_browser(page, wait_seconds=0.05)
    assert result["authenticated"] is None
    assert "could not determine" in result["reason"]


async def test_the_wait_caps_how_many_requests_it_will_spend(
    patched_navigation, monkeypatch
):
    """Rate discipline: a long wait must not become an unbounded poll."""
    monkeypatch.setattr(auth_module, "LOGIN_POLL_S", 0.0)
    monkeypatch.setattr(auth_module, "LOGIN_RECHECK_S", 0.0)
    monkeypatch.setattr(auth_module, "LOGIN_MAX_CHECKS", 3)
    page = FakePage(
        cookies={"li_at": "x"},
        responses=[FakeResponse(401, "")],
        default_response=FakeResponse(401, ""),
    )
    result = await login_via_browser(page, wait_seconds=0.2)
    assert result["authenticated"] is False
    assert result["checks_run"] <= 3


# ---------------------------------------------------------------------------
# Nothing sensitive leaks out
# ---------------------------------------------------------------------------


async def test_no_cookie_value_ever_reaches_a_tool_result(signed_in_page):
    """Cookie VALUES are credentials. Only their presence may be reported."""
    result = await check_auth(signed_in_page)
    blob = json.dumps(result)
    assert "live" not in blob
    assert "ajax:99" not in blob
    assert result["session_cookie_present"] is True


async def test_no_cookie_value_leaks_from_the_login_result(
    patched_navigation, fast_polling
):
    page = FakePage(
        cookies={"li_at": "secret-token-value", "JSESSIONID": '"ajax:55"'},
        responses=[FakeResponse(401, ""), me_response()],
    )
    result = await login_via_browser(page, wait_seconds=5)
    blob = json.dumps(result)
    assert "secret-token-value" not in blob
    assert "ajax:55" not in blob


# ---------------------------------------------------------------------------
# The cold start
# ---------------------------------------------------------------------------
#
# The trap this section exists for, measured in this repo's own Chrome
# profile: li_at is a PERSISTENT cookie and JSESSIONID is a SESSION one
# (is_persistent=0, expires=NULL). So every time the browser starts, the jar
# holds a perfectly good login and no csrf cookie. A server that asked the
# identity endpoint straight away would send a request with no csrf-token,
# LinkedIn would refuse it, and the operator would be told to sign in again
# while his session was fine. One page load fixes it, because LinkedIn issues
# the session cookie to anyone who loads a page.


async def test_a_cold_browser_loads_a_page_before_asking_who_it_is(
    patched_navigation,
):
    """The fix: no csrf cookie -> load the feed -> now ask, with the token."""
    page = FakePage(
        cookies={"li_at": "live"},  # persistent login, no session cookie yet
        cookies_after_goto={"JSESSIONID": '"ajax:cold"'},
        responses=[me_response()],
    )
    result = await check_auth(page)

    assert result["authenticated"] is True
    assert patched_navigation == ["https://www.linkedin.com/feed/"]
    # The request that decided it carried the token the warm-up earned.
    assert page.request.calls[0]["headers"]["csrf-token"] == "ajax:cold"


async def test_without_the_warm_up_the_identity_call_goes_out_without_a_token(
    patched_navigation,
):
    """The warm-up, shown failing.

    ``warm=False`` is the behaviour this server had before: it asks with no
    csrf-token at all. The check above proves the fix only because this one
    proves the fix was needed.
    """
    page = FakePage(
        cookies={"li_at": "live"},
        cookies_after_goto={"JSESSIONID": '"ajax:cold"'},
        responses=[FakeResponse(401, "")],
    )
    result = await check_auth(page, warm=False)

    assert patched_navigation == []
    assert "csrf-token" not in page.request.calls[0]["headers"]
    assert result["authenticated"] is False


async def test_a_warm_browser_does_not_spend_a_page_load(patched_navigation):
    """The warm-up fires on a cold jar only. A live one must not pay for it."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        responses=[me_response()],
    )
    result = await check_auth(page)
    assert result["authenticated"] is True
    assert patched_navigation == []


async def test_the_warm_up_load_doubles_as_the_corroborating_read(
    patched_navigation,
):
    """Having loaded the feed once, an inconclusive answer must not reload it.

    Corroboration and the warm-up ask the same question of the same page.
    Spending a second request on it would be this server hitting LinkedIn
    twice to learn something it already knew.
    """
    page = FakePage(
        cookies={"li_at": "stale"},
        cookies_after_goto={"JSESSIONID": '"ajax:cold"'},
        responses=[FakeResponse(999, "")],
    )
    page.redirect_to = "https://www.linkedin.com/authwall"

    result = await check_auth(page, corroborate=True)

    assert patched_navigation == ["https://www.linkedin.com/feed/"]
    assert result["authenticated"] is False
    assert "authwall" in result["corroborated_with"]


async def test_a_failed_warm_up_does_not_become_a_verdict(monkeypatch):
    """The warm-up is best effort. Losing it must not decide the question."""
    from linkedin_own_server import browser as browser_module

    async def exploding_goto(page, url, **kwargs):
        raise RuntimeError("net::ERR_NAME_NOT_RESOLVED")

    monkeypatch.setattr(browser_module.BROWSER, "goto", exploding_goto)

    page = FakePage(cookies={"li_at": "live"}, responses=[me_response()])
    result = await check_auth(page)
    assert result["authenticated"] is True


async def test_the_half_typed_login_page_is_never_navigated_away(
    patched_navigation, fast_polling
):
    """The login wait polls with warm=False, and it has to.

    The warm-up navigates. Navigating while he is typing into the sign-in form
    would throw the form away, so the wait loop must never do it -- the page
    starts at /login and no /feed/ load may follow.
    """
    page = FakePage(
        cookies={"li_at": "pending"},
        responses=[FakeResponse(401, ""), me_response()],
    )
    result = await login_via_browser(page, wait_seconds=5)

    assert result["authenticated"] is True
    assert "https://www.linkedin.com/feed/" not in patched_navigation[1:]


# ---------------------------------------------------------------------------
# session_info: how long the sign-in has left
# ---------------------------------------------------------------------------


def _in_days(days: float) -> float:
    import time as _time

    return _time.time() + days * 86400.0


async def test_session_info_reports_the_expiry_it_reads_from_the_jar(
    patched_navigation,
):
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": _in_days(300)},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["authenticated"] is True
    assert info["session_cookie"]["name"] == "li_at"
    assert info["session_cookie"]["present"] is True
    assert info["session_cookie"]["persistent"] is True
    assert 299 <= info["session_cookie"]["expires_in_days"] <= 301
    assert info["session_cookie"]["expired"] is False
    assert info["session_cookie"]["expires_at"].endswith("Z")


async def test_session_info_calls_the_csrf_cookie_what_it_is(patched_navigation):
    """JSESSIONID has no expiry date because it has no life past the browser."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": _in_days(300)},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["csrf_cookie"]["present"] is True
    assert info["csrf_cookie"]["persistent"] is False
    assert info["csrf_cookie"]["expires_at"] is None


async def test_session_info_says_the_login_outlives_a_restart(patched_navigation):
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": _in_days(300)},
        responses=[me_response()],
    )
    info = await auth_module.session_info(page)

    assert info["durability"]["survives_server_restart"] is True
    assert info["durability"]["survives_machine_reboot"] is True
    assert "chrome-profile" in info["durability"]["stored_in"].lower()
    assert "linkedin_login_browser" in info["on_expiry"]


async def test_session_info_reports_a_missing_login_as_missing(patched_navigation):
    """No li_at at all. The absence is reported, not papered over."""
    page = FakePage(
        cookies={"JSESSIONID": '"ajax:99"'},
        responses=[FakeResponse(401, "")],
    )
    info = await auth_module.session_info(page)

    assert info["authenticated"] is False
    assert info["session_cookie"]["present"] is False
    assert "expires_at" not in info["session_cookie"]


async def test_session_info_flags_an_expired_cookie_as_expired(patched_navigation):
    page = FakePage(
        cookies={"li_at": "long-dead", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": _in_days(-2)},
        responses=[FakeResponse(401, "")],
    )
    info = await auth_module.session_info(page)

    assert info["session_cookie"]["expired"] is True
    assert info["session_cookie"]["expires_in_days"] < 0
    assert info["authenticated"] is False


async def test_session_info_never_returns_a_cookie_value(patched_navigation):
    """An expiry date is a fact about the session. The token is the session."""
    page = FakePage(
        cookies={"li_at": "secret-token-value", "JSESSIONID": '"ajax:55"'},
        expiries={"li_at": _in_days(300)},
        responses=[me_response()],
    )
    blob = json.dumps(await auth_module.session_info(page))

    assert "secret-token-value" not in blob
    assert "ajax:55" not in blob


async def test_session_info_does_not_guess_when_the_endpoint_will_not_say(
    patched_navigation,
):
    """Three-valued here too: unknown stays unknown, it does not become false."""
    page = FakePage(
        cookies={"li_at": "live", "JSESSIONID": '"ajax:99"'},
        expiries={"li_at": _in_days(300)},
        responses=[FakeResponse(999, "")],
    )
    info = await auth_module.session_info(page)

    assert info["authenticated"] is None
    assert "999" in info["reason"]
    # The expiry is still reported: it is read from the jar, not from LinkedIn.
    assert info["session_cookie"]["persistent"] is True
