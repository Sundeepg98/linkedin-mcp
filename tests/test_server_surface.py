"""The tool surface: twelve tools, and not one of them offers a write.

The brief for this server drew a hard line -- no writes, not now, not stubbed,
not "for later". This file is that line expressed as assertions, including on
the docstrings, because a tool that merely SOUNDS like it can apply to a job
will be called as though it can.
"""

from __future__ import annotations

import pytest

from linkedin_server import readonly
from linkedin_server.server import mcp

EXPECTED_TOOLS = {
    "linkedin_auth_status",
    "linkedin_login_browser",
    "linkedin_who_viewed_me",
    "linkedin_my_applications",
    "linkedin_saved_jobs",
    "linkedin_search_jobs",
    "linkedin_job_detail",
    "linkedin_my_profile",
    "linkedin_notifications",
    "linkedin_server_info",
    "linkedin_session_info",
    "linkedin_cdp_status",
}

#: Names a reader must never grow. Listed explicitly so that adding one is a
#: failing test rather than a code review someone might skim.
FORBIDDEN_TOOLS = {
    "linkedin_apply",
    "linkedin_apply_job",
    "linkedin_easy_apply",
    "linkedin_save_job",
    "linkedin_unsave_job",
    "linkedin_send_message",
    "linkedin_send_inmail",
    "linkedin_connect",
    "linkedin_invite",
    "linkedin_endorse",
    "linkedin_follow",
    "linkedin_post",
    "linkedin_update_profile",
    "linkedin_set_open_to_work",
    "linkedin_mark_notification_read",
    "linkedin_withdraw_application",
}


@pytest.fixture
async def tools():
    return {t.name: t for t in await mcp.list_tools()}


async def test_the_surface_is_exactly_the_twelve_reads(tools):
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 12


async def test_no_write_tool_exists_under_any_of_its_obvious_names(tools):
    overlap = set(tools) & FORBIDDEN_TOOLS
    assert overlap == set(), overlap


async def test_no_tool_name_implies_a_write(tools):
    offenders = [name for name in tools if readonly.name_implies_write(name)]
    assert offenders == [], offenders


def test_the_name_check_catches_a_write_tool():
    """The name check, shown failing. Otherwise it proves nothing above."""
    assert readonly.name_implies_write("linkedin_apply_job")
    assert readonly.name_implies_write("linkedin_send_message")
    assert readonly.name_implies_write("linkedin_update_profile")
    # ...and does not fire on the past-participle noun phrases we do ship.
    assert not readonly.name_implies_write("linkedin_saved_jobs")
    assert not readonly.name_implies_write("linkedin_my_applications")


async def test_no_docstring_claims_a_write(tools):
    """A docstring may say what a tool cannot do; it may not claim it does."""
    offenders: dict[str, list] = {}
    for name, tool in tools.items():
        claims = readonly.docstring_write_claims(tool.description or "")
        if claims:
            offenders[name] = claims
    assert offenders == {}, offenders


def test_the_docstring_check_catches_an_affirmative_write_claim():
    """The docstring check, shown failing on a claim and passing on a denial."""
    claims = readonly.docstring_write_claims(
        "Apply to a job and save it to your list, then send the recruiter a note."
    )
    verbs = {verb for verb, _ in claims}
    assert {"apply", "save", "send"} <= verbs, claims

    denial = readonly.docstring_write_claims(
        "Lists what you saved. This tool has no way to add or remove anything, "
        "and it never sends a message."
    )
    assert denial == [], denial


async def test_every_tool_documents_itself(tools):
    """An undocumented tool is one a caller has to guess the boundary of."""
    thin = {
        name: len(tool.description or "")
        for name, tool in tools.items()
        if len(tool.description or "") < 120
    }
    assert thin == {}, thin


async def test_the_notification_side_effect_is_disclosed(tools):
    """Reading that page clears LinkedIn's unread badge, so it has to say so."""
    text = (tools["linkedin_notifications"].description or "").lower()
    assert "side effect" in text
    assert "badge" in text


async def test_the_search_history_side_effect_is_disclosed(tools):
    text = (tools["linkedin_search_jobs"].description or "").lower()
    assert "recent-search history" in text


async def test_the_login_tool_promises_never_to_touch_a_credential(tools):
    text = (tools["linkedin_login_browser"].description or "").lower()
    assert "never sees, types, stores or transmits a password" in text


async def test_the_auth_tool_documents_that_a_cookie_is_not_a_verdict(tools):
    text = (tools["linkedin_auth_status"].description or "").lower()
    assert "cookie" in text
    assert "proves nothing" in text or "never treated as an answer" in text


async def test_server_info_declares_the_boundary_and_lists_no_writes():
    from linkedin_server.server import linkedin_server_info

    info = await linkedin_server_info()
    assert info["read_only"] is True
    assert info["writes_available"] == []
    assert info["rate_discipline"]["auto_paging"] is False
    assert info["rate_discipline"]["scheduled_or_background_activity"] is False
    # The side effects are disclosed here too, not only in one docstring.
    joined = " ".join(info["known_side_effects"]).lower()
    assert "badge" in joined and "recent-search history" in joined


async def test_the_server_instructions_tell_a_caller_not_to_look_for_writes():
    text = (mcp.instructions or "").lower()
    assert "read-only" in text
    assert "no apply" in text


# ---------------------------------------------------------------------------
# The automation posture, declared as fields rather than as a promise
# ---------------------------------------------------------------------------


async def test_server_info_names_the_one_flag_and_denies_every_other_technique():
    """A prose disclaimer cannot be asserted on. These fields can.

    The operator's boundary is one Blink flag and nothing past it. Every
    technique past it is enumerated here as a field, so crossing the line
    means editing a False to a True in a diff rather than quietly adding an
    argument somewhere.
    """
    from linkedin_server.config import LAUNCH_ARGS
    from linkedin_server.server import linkedin_server_info

    posture = (await linkedin_server_info())["automation_posture"]

    assert posture["launch_args"] == list(LAUNCH_ARGS)
    assert posture["navigator_webdriver_disabled"] is True
    for technique in (
        "stealth_plugin",
        "user_agent_spoofing",
        "platform_or_timezone_spoofing",
        "fingerprint_spoofing",
        "proxy",
        "randomised_or_humanised_timing",
        "mouse_movement_simulation",
        "captcha_solving",
    ):
        assert posture[technique] is False, technique


async def test_the_flags_server_info_reports_are_flags_it_is_allowed_to_pass():
    """The report and the gate must not be able to drift apart.

    Putting what the tool SAYS back through the boundary check means a flag
    added to the launch list is caught here too, not only where it is used.
    """
    from linkedin_server.server import linkedin_server_info

    posture = (await linkedin_server_info())["automation_posture"]
    assert readonly.assert_launch_flags_permitted(posture["launch_args"]) is None


async def test_the_posture_check_would_catch_a_third_flag():
    """The check above, shown failing."""
    with pytest.raises(Exception) as excinfo:
        readonly.assert_launch_flags_permitted(
            ["--disable-blink-features=AutomationControlled", "--user-agent=Mozilla"]
        )
    assert "--user-agent" in str(excinfo.value)


# ---------------------------------------------------------------------------
# The two tools added for session durability and recovery
# ---------------------------------------------------------------------------


async def test_the_session_tool_says_the_sign_in_outlives_a_restart(tools):
    """The operator's question is "do I have to do this again?" -- so answer it
    in the description, where he reads it, not only in a field."""
    text = (tools["linkedin_session_info"].description or "").lower()
    assert "profile" in text
    assert "restarting" in text and "rebooting" in text


async def test_the_session_tool_promises_not_to_return_a_cookie_value(tools):
    text = (tools["linkedin_session_info"].description or "").lower()
    assert "cookie values are never returned" in text


async def test_the_recovery_tool_is_labelled_as_recovery(tools):
    """It must not read as an alternative daily path. It is a fallback."""
    text = (tools["linkedin_cdp_status"].description or "").lower()
    assert "not the normal way" in text
    assert "recovery" in text


async def test_the_recovery_tool_states_its_two_hard_requirements(tools):
    """Both were measured. Both silently defeat an operator who does not know.

    A Chrome opened normally has no DevTools port; and a second Chrome
    started with the flag while one is already running hands its arguments to
    the first and opens no port at all, with no error.
    """
    text = (tools["linkedin_cdp_status"].description or "").lower()
    assert "already running" in text
    assert "--remote-debugging-port" in text
    assert "silently" in text
    assert "--user-data-dir" in text


async def test_server_info_points_at_the_recovery_path_without_promoting_it():
    from linkedin_server.server import linkedin_server_info

    recovery = (await linkedin_server_info())["recovery_path"]
    assert recovery["is_the_daily_path"] is False
    assert recovery["check_with"] == "linkedin_cdp_status"
    assert "--remote-debugging-port" in recovery["requires"]


async def test_the_instructions_tell_a_caller_the_sign_in_is_one_time():
    """A caller that thinks the login is per-session will suggest it forever."""
    text = (mcp.instructions or "").lower()
    assert "one-time" in text
    assert "linkedin_session_info" in text
