"""The auth ``reason`` may not republish the request Playwright renders at it.

## THE DEFECT THIS PINS

``page.request.get`` failing does not raise a short message. It renders THE
WHOLE REQUEST into its own exception text -- method, address, and every
request header, one per line, ``cookie:`` among them. ``check_auth``'s
request-failure handler used to interpolate that text verbatim into a field it
RETURNS and into a line it LOGS, so the session credential reached the model
and the log file on any transport failure.

Measured end to end on 2026-09-21 with a real chromium against loopback:
``scripts/_probe_auth_reason_leak.py``. Write-up:
``_audit/2026-09-21-the-auth-reason-leak.md``.

## WHY THE SUITE WAS ALREADY GREEN, WHICH IS THE PART WORTH KEEPING

Two tests in ``tests/test_auth.py`` bracketed this defect for weeks without
touching it, and neither was wrong:

* ``test_a_transport_failure_is_unknown_not_signed_out`` drives the LEAKING
  branch -- with ``cookies={"li_at": "x"}`` and ``RuntimeError("connection
  reset")``. A one-character jar and a fixture-authored message. Nothing that
  could leak was present, so nothing leaked.
* ``test_no_cookie_value_ever_reaches_a_tool_result`` uses the PLANTED
  credential and ``leakwalk.assert_no_leak`` -- down the SUCCESS branch, which
  interpolates no exception at all.

**The needle and the branch never met.** Three things have to coincide before
this defect is visible: the planted credential in the jar, the request-failure
branch, and an exception whose text is the LIBRARY'S rather than the fixture's.
Each test had one or two. Neither had three.

So the property this module holds is not "check_auth does not leak". It is:
**every branch of check_auth that can compose a ``reason`` is driven with a
credential-shaped needle in the jar and a library-shaped exception on the
wire.** A future branch that starts quoting an exception has to be added to
``REASON_BRANCHES`` to be tested at all, and the count assertion at the bottom
is what makes forgetting that loud.

## THE FIXTURE IS MANUFACTURED HERE, NOT FOUND

``_playwright_shaped_failure`` builds the specimen from a template in this
file. It is NOT read from ``scripts/_probe_auth_reason_leak.json``, and it does
not launch a browser. A control that finds its fixture in ambient repo state
passes on the box it was written on and fails in every clone; a control that
needs a browser does not run in CI, and a guard that does not run is not one.

The template is a faithful transcription of what Playwright 1.x actually
emitted -- captured, masked and committed by the probe above -- including the
U+2192 in its call log, which is also proof the string was composed by
something outside this repository. ``test_the_needle_is_really_in_the_haystack``
asserts the specimen carries the credential before anything asserts it is
absent downstream, because an absence check over an empty haystack passes
perfectly and certifies nothing.
"""

from __future__ import annotations

import logging

import pytest

from linkedin_server import auth as auth_module
from linkedin_server.auth import check_auth, require_auth
from linkedin_server.config import API_TIMEOUT_MS
from linkedin_server.errors import AuthUnknownError, NotAuthenticatedError
from tests.conftest import FakePage, FakeResponse
from tests.leakwalk import PLANTED_JSESSIONID, PLANTED_LI_AT, assert_no_leak

# ---------------------------------------------------------------------------
# The specimen
# ---------------------------------------------------------------------------

#: What a failing ``APIRequestContext.get`` renders, transcribed from a real
#: capture. ``{credential}`` is filled at call time with the planted value so
#: no credential-shaped literal is committed in this file.
#:
#: The arrow is U+2192, exactly as Playwright writes it. It is kept because a
#: sanitiser or a serialiser that chokes on non-ASCII would otherwise be
#: exercised only in production, and because it is the cheapest evidence that
#: this string is not one this repository composed.
_CALL_LOG_TEMPLATE = (
    "APIRequestContext.get: {headline}\n"
    "Call log:\n"
    "  - \u2192 GET https://www.linkedin.com/voyager/api/me\n"
    "    - user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/153.0.8010.12 "
    "Safari/537.36\n"
    "    - accept: */*\n"
    "    - accept-encoding: gzip,deflate,br\n"
    "    - cookie: li_at={credential}; JSESSIONID={csrf}\n"
)

_HEADLINES = {
    "connect_refused": ("Error", "connect ECONNREFUSED 127.0.0.1:443"),
    "timeout": ("TimeoutError", f"Timeout {API_TIMEOUT_MS}ms exceeded."),
    "socket_hangup": ("Error", "socket hang up"),
}


def _playwright_shaped_failure(kind: str) -> Exception:
    """An exception whose ``str()`` carries the credential, as the library's does.

    The CLASS is synthesised rather than imported from
    ``playwright._impl._errors``. What ``check_auth`` does with an exception
    turns on its TEXT and its TYPE NAME, never on its identity, and importing
    a private module would make this guard depend on a path the vendor may
    rename. The type name is set to the real one so the positive assertions
    about what ``reason`` DOES say are testing the real string.
    """
    type_name, headline = _HEADLINES[kind]
    text = _CALL_LOG_TEMPLATE.format(
        headline=headline, credential=PLANTED_LI_AT, csrf=PLANTED_JSESSIONID
    )
    return type(type_name, (Exception,), {})(text)


def planted_page(**kwargs) -> FakePage:
    """A jar holding the planted credential, for EVERY branch -- not just one."""
    return FakePage(
        cookies={"li_at": PLANTED_LI_AT, "JSESSIONID": PLANTED_JSESSIONID},
        **kwargs,
    )


#: Every branch of ``check_auth`` that composes a ``reason``, with the wire
#: response that reaches it. Named rather than inlined so the count below can
#: assert the set has not silently shrunk.
REASON_BRANCHES: dict[str, object] = {
    # The three that go through the request-failure handler -- the defect.
    "request_connect_refused": _playwright_shaped_failure("connect_refused"),
    "request_timeout": _playwright_shaped_failure("timeout"),
    "request_socket_hangup": _playwright_shaped_failure("socket_hangup"),
    # The three that compose a reason from a RESPONSE rather than an exception.
    # They are here because the property is about the branch set, not about the
    # one branch that was found leaking.
    "http_401_refusal": FakeResponse(401, ""),
    "http_999_unservable": FakeResponse(999, ""),
    "http_200_empty_body": FakeResponse(200, ""),
}


# ---------------------------------------------------------------------------
# The positive control -- run FIRST, because everything below is an absence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kind", sorted(_HEADLINES))
def test_the_needle_is_really_in_the_haystack(kind: str):
    """The specimen must CARRY the credential, or every assertion below is vacuous.

    This is the assertion that makes the rest of the module mean something. If
    the template stopped interpolating, or the plant were shortened below
    ``leakwalk.MIN_SECRET``, every ``assert_no_leak`` here would pass on an
    empty haystack and this file would certify a property it never tested.
    """
    from tests.leakwalk import find_leaks

    text = str(_playwright_shaped_failure(kind))
    assert PLANTED_LI_AT in text
    assert find_leaks(text, PLANTED_LI_AT), (
        "the specimen does not carry the planted credential, so no absence "
        "assertion in this module proves anything"
    )


def test_every_reason_branch_is_covered():
    """A new reason branch must arrive in this table or this count goes red.

    Pinned by COUNT rather than left implicit. The defect this module exists
    for was invisible precisely because the branch that leaked was never
    driven with the needle that would show it, and the cheapest way for that
    to happen again is a seventh branch nobody adds here.
    """
    assert len(REASON_BRANCHES) == 6, (
        "REASON_BRANCHES changed size. If check_auth grew a branch that "
        "composes a reason, drive it here with the planted jar; if one was "
        "removed, drop it and update this count."
    )


# ---------------------------------------------------------------------------
# 1. THE MODEL CHANNEL and 2. THE LOG CHANNEL, over every branch
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("branch", sorted(REASON_BRANCHES))
async def test_no_branch_of_check_auth_publishes_the_credential(branch, caplog):
    """The planted jar, on EVERY reason branch. This is the crossing that was missing.

    ``assert_no_leak`` reads the whole returned object AND the log -- every
    encoding, every 12-character run, keys as well as values. ``caplog`` hears
    the ``linkedin`` logger because ``tests/conftest.py`` attaches its handler
    to that logger by name; without that autouse fixture the log half of this
    assertion would read an empty channel and pass on anything.
    """
    page = planted_page(responses=[REASON_BRANCHES[branch]])

    with caplog.at_level(logging.DEBUG):
        result = await check_auth(page, warm=False)

    # The branch really was taken: every one of these is a non-True verdict
    # carrying a reason. A result that came back authenticated would mean the
    # fixture missed the branch and the leak assertion below tested nothing.
    assert result.get("authenticated") is not True
    assert result.get("reason"), f"{branch} produced no reason to check"

    assert_no_leak(result, PLANTED_LI_AT, caplog=caplog)
    assert_no_leak(result, PLANTED_JSESSIONID, caplog=caplog)


# ---------------------------------------------------------------------------
# 3. THE EXCEPTION CHANNEL -- reason becomes an exception message
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("branch", sorted(REASON_BRANCHES))
async def test_require_auth_does_not_raise_the_credential(branch, caplog):
    """``require_auth`` raises ``...Error(status["reason"])``: a THIRD channel.

    A field that becomes an exception message is published by every envelope
    that renders an exception, which in this package is all 48 tool bodies via
    ``server._error``. ``_corroboration_note``'s own docstring records the
    previous time this channel was found the hard way, with the authwall
    landing.
    """
    page = planted_page(responses=[REASON_BRANCHES[branch]])

    raised: Exception | None = None
    with caplog.at_level(logging.DEBUG):
        try:
            await require_auth(page)
        except (AuthUnknownError, NotAuthenticatedError) as exc:
            raised = exc

    assert raised is not None, f"{branch} did not refuse, so nothing was raised"
    assert_no_leak(str(raised), PLANTED_LI_AT, caplog=caplog)
    assert_no_leak(list(raised.args), PLANTED_LI_AT)
    assert_no_leak(str(raised), PLANTED_JSESSIONID, caplog=caplog)


# ---------------------------------------------------------------------------
# 4. THE session_info CHANNEL -- live_check.why_not is a second published field
# ---------------------------------------------------------------------------


async def test_session_info_why_not_does_not_publish_the_credential(
    patched_navigation, caplog
):
    """``session_info`` copies ``reason`` into ``live_check.why_not`` AND top level.

    Driven down the request-failure branch specifically. The existing
    ``test_session_info_never_returns_a_cookie_value`` drives the SUCCESS
    branch with the same needle, which is why it never saw this.
    """
    page = planted_page(responses=[_playwright_shaped_failure("timeout")])

    with caplog.at_level(logging.DEBUG):
        result = await auth_module.session_info(page)

    assert result["authenticated"] is None
    # The field is REPORTED, not merely absent -- a guard that passes because
    # the diagnosis vanished is the failure mode this repair must not have.
    assert result["live_check"]["why_not"], "the null lost its explanation"
    assert_no_leak(result, PLANTED_LI_AT, caplog=caplog)
    assert_no_leak(result, PLANTED_JSESSIONID, caplog=caplog)


# ---------------------------------------------------------------------------
# 5. THE login_via_browser CHANNEL -- the reason is CONCATENATED into another
# ---------------------------------------------------------------------------


@pytest.fixture
def fast_polling(monkeypatch):
    """Collapse the poll and recheck intervals so the wait loop is testable."""
    monkeypatch.setattr(auth_module, "LOGIN_POLL_S", 0.001)
    monkeypatch.setattr(auth_module, "LOGIN_RECHECK_S", 0.0)


async def test_login_result_does_not_republish_the_credential(
    patched_navigation, fast_polling, caplog
):
    """``linkedin_login`` builds ITS reason by concatenating check_auth's.

    ``login_via_browser``::

        "could not determine whether the sign-in succeeded: "
        + str(last_status.get("reason", ...))

    A fifth exit, on a different tool, reached by string concatenation rather
    than by returning the dict -- which is why following the FIELD rather than
    the VALUE would have missed it. The existing
    ``test_no_cookie_value_leaks_from_the_login_result`` drives this function
    with a 401 then a success, so it never reaches the concatenation at all.
    """
    # QUEUED, NOT ``default_response``. ``FakeRequestContext`` RETURNS its
    # default and only RAISES a queued item, so an exception handed to
    # ``default_response`` would come back as a return value, fail on
    # ``.status``, and be caught as an AttributeError -- a green test driving
    # a branch it was not aiming at. One per possible poll, generously.
    page = planted_page(
        responses=[
            _playwright_shaped_failure("timeout")
            for _ in range(auth_module.LOGIN_MAX_CHECKS + 10)
        ],
    )

    with caplog.at_level(logging.DEBUG):
        result = await auth_module.login_via_browser(page, wait_seconds=1)

    assert result.get("authenticated") is not True
    assert result.get("reason"), "the login result lost its explanation"
    assert_no_leak(result, PLANTED_LI_AT, caplog=caplog)
    assert_no_leak(result, PLANTED_JSESSIONID, caplog=caplog)


# ---------------------------------------------------------------------------
# WHAT THE REASON DOES SAY -- absence is half a property
# ---------------------------------------------------------------------------
#
# "The reason is shorter now" and "the reason does not contain li_at" are both
# satisfied by deleting the field. A refusal that says nothing is its own
# defect and this repository has a standing rule against it, so the diagnosis
# is asserted as positively as the leak is asserted absent.


@pytest.mark.parametrize(
    "kind,expected_type",
    [("connect_refused", "Error"), ("timeout", "TimeoutError")],
)
async def test_the_reason_still_names_the_exception_type(kind, expected_type):
    """The TYPE is the diagnosis that survives, and it is the useful half.

    ``TimeoutError`` means LinkedIn did not answer inside the ceiling;
    anything else means the request could not be made at all. Those are
    different problems with different remedies, and a caller that cannot tell
    them apart has lost the only thing the library's message was good for.
    """
    page = planted_page(responses=[_playwright_shaped_failure(kind)])
    result = await check_auth(page, warm=False)

    reason = result["reason"]
    assert expected_type in reason
    assert "not a verdict" in reason
    # It says WHY it is terse, so a reader does not file the missing detail as
    # a bug in the field.
    assert "withheld" in reason.lower()
    # And it prices the wait, which is the one number the library's message
    # carried that this server can publish safely: the ceiling is ours.
    assert str(API_TIMEOUT_MS) in reason


async def test_the_reason_is_ascii_and_short_enough_to_read():
    """A field a model reads should not be a 900-character transcript.

    Not a floor standing in for the leak check -- the leak check is above and
    is exact. This pins the OTHER regression: the pre-fix field was a
    multi-line call log with a U+2192 in it, in a repository that is strict
    ASCII everywhere else.
    """
    page = planted_page(responses=[_playwright_shaped_failure("timeout")])
    result = await check_auth(page, warm=False)

    reason = result["reason"]
    reason.encode("ascii")  # raises if the library's text survived
    assert "Call log:" not in reason
    assert "user-agent:" not in reason
    assert "cookie:" not in reason
