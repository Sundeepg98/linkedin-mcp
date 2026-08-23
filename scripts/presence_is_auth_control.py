"""A PRESENCE-IS-AUTH build of this server's session report, for showing the
honesty tests can fail.

WHY THIS FILE IS IN THE REPO
----------------------------
``tests/test_auth_lifecycle.py`` and ``tests/test_session_info_offline.py``
assert that ``authenticated`` stays null when the live identity call could not
be made -- even with a perfectly healthy ``li_at`` sitting in the jar. Those
assertions are only worth something if they are capable of going red. A check
that has never been shown failing is a claim, not a measurement, and this
family of repos spent a week finding out what a library of such checks is
worth.

This pytest plugin re-creates the exact bug those tests exist to catch: the
one a sibling server shipped, where ``authenticated`` was derived from the
session cookie being PRESENT in the jar instead of from an authenticated
request. Here that is reproduced by letting the real functions run and then
overwriting their verdict with ``bool(credential["present"])`` on the way out,
which is what "a cookie is an answer" looks like when it is written down.

Both module bindings are patched. ``server.py`` does ``from
linkedin_server.auth import session_info, session_info_offline`` at import, so
patching ``auth`` alone would leave every TOOL-level test running the honest
build and the control would look far weaker than it is.

``check_auth`` is deliberately LEFT ALONE. The bug being reproduced is about
the reported ``authenticated`` field in the shared auth-lifecycle shape, which
is what the contract names; patching the identity measurement itself would
turn most of ``test_auth.py`` red for a reason that has nothing to do with the
guard under test, and a control whose blast radius nobody can read certifies
nothing.

HOW TO RUN IT
-------------
    PYTHONPATH=scripts pytest tests/test_auth_lifecycle.py \
        tests/test_session_info_offline.py -p presence_is_auth_control

    # PowerShell
    $env:PYTHONPATH="scripts"; venv/Scripts/python -m pytest `
        tests/test_auth_lifecycle.py tests/test_session_info_offline.py `
        -p presence_is_auth_control

MEASURED 2026-08-23, and RE-MEASURED twice the same day as ``renewal`` grew
-- first the three ``session_lapses_*`` keys, then ``uses_browser`` and
``mechanism``. The failing twelve are unchanged by both additions, which is the
expected result: they added shape, not verdict. Verbatim tail of the latest
run::

    FAILED tests/test_auth_lifecycle.py::test_the_offline_path_still_answers_null_and_not_false
    FAILED tests/test_auth_lifecycle.py::test_the_browser_failed_path_still_answers_null
    FAILED tests/test_auth_lifecycle.py::test_a_refusal_is_a_false_and_a_shrug_is_a_null
    FAILED tests/test_auth_lifecycle.py::test_why_not_is_present_exactly_when_the_check_did_not_complete
    FAILED tests/test_session_info_offline.py::test_a_perfectly_healthy_cookie_is_still_not_called_authenticated
    FAILED tests/test_session_info_offline.py::test_the_offline_result_says_in_words_that_a_cookie_is_not_a_session
    FAILED tests/test_session_info_offline.py::test_the_reason_the_live_check_could_not_run_travels_with_the_result
    FAILED tests/test_session_info_offline.py::test_an_expired_cookie_is_reported_expired_without_a_browser
    FAILED tests/test_session_info_offline.py::test_both_routes_failing_reports_both_reasons
    FAILED tests/test_session_info_offline.py::test_the_tool_falls_back_to_the_jar_when_no_browser_can_start
    FAILED tests/test_session_info_offline.py::test_verify_live_false_does_not_touch_the_browser_at_all
    FAILED tests/test_session_info_offline.py::test_the_default_does_reach_for_the_browser
    12 failed, 58 passed in 3.17s

The same two files run 70 passed with the plugin off, so every one of those
twelve is a real flip and none of them is a collection error.

The 58 that survive are supposed to survive, and reading the list is as much
the point as the failures:

* ``test_the_live_path_does_still_say_true`` stays green. It is the POSITIVE
  control -- a signed-in page with a present cookie reads True either way --
  and a control build that flipped it too would prove nothing about WHERE the
  verdict came from.
* every ``linkedin_logout`` test stays green. Logout reports no measured
  verdict, so this bug cannot reach it, and a control that broke it would be
  measuring blast radius rather than the guard.
* the shape tests -- credential, supporting, renewal (including every
  ``session_lapses_*`` assertion and both mechanism-declaration tests),
  durability, and
  ``test_expiry_source_says_why_when_there_is_no_date`` -- stay green,
  because the permissive build still returns the RIGHT SHAPE. Only the
  verdict inside it is wrong. That asymmetry is the whole lesson: a wrong
  answer in a right shape is exactly what shipped last time, and a suite that
  only checked shape would have passed it.

Two failures name the mechanism rather than a field. ``test_a_refusal_is_a_
false_and_a_shrug_is_a_null`` goes red on the shrug -- an HTTP 999 with a
cookie present becomes True -- and ``test_the_default_does_reach_for_the_
browser`` goes red because a null it expected turned into a verdict.

If the injection below ever silently stops working, the guarded tests go
green under it and this docstring stops matching the run -- which is the
failure mode a re-measurement catches.
"""


def _presence_is_auth(payload):
    """Overwrite a measured verdict with a cookie's presence. The bug, exactly."""
    if not isinstance(payload, dict):
        return payload
    credential = payload.get("credential") or {}
    payload["authenticated"] = bool(credential.get("present"))
    live_check = payload.get("live_check")
    if isinstance(live_check, dict):
        # The pre-fix build had no separate "did the round trip happen" field
        # at all: a cookie in the jar WAS the completed check.
        live_check["completed"] = True
        live_check.pop("why_not", None)
    return payload


def pytest_sessionstart(session):
    from linkedin_server import auth, server

    real_offline = auth.session_info_offline
    real_live = auth.session_info

    def offline(*args, **kwargs):
        return _presence_is_auth(real_offline(*args, **kwargs))

    async def live(*args, **kwargs):
        return _presence_is_auth(await real_live(*args, **kwargs))

    auth.session_info_offline = offline
    auth.session_info = live
    # server.py bound its own names at import; patching only auth would leave
    # every tool-level test running the honest build.
    server.session_info_offline = offline
    server.session_info = live

    print(
        "\n[presence_is_auth_control] session_info now derives "
        "'authenticated' from li_at being PRESENT -- the pre-fix bug shape"
    )
