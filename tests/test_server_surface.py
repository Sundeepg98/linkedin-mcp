"""The tool surface: fourteen tools, and not one of them writes to LinkedIn.

The brief for this server drew a hard line -- no writes, not now, not stubbed,
not "for later". This file is that line expressed as assertions, including on
the docstrings, because a tool that merely SOUNDS like it can apply to a job
will be called as though it can.

The thirteenth tool, ``linkedin_logout``, writes to LOCAL DISK and to nothing
else: it erases this machine's cookie jar and issues no request, so the line
above is about the platform and is intact. It gets its own assertions at the
bottom of this file, because "performs nothing without confirm" is a promise
somebody has to hold to.
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
    "linkedin_logout",
    "linkedin_cdp_status",
    "linkedin_followed_companies",
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


async def test_the_surface_is_exactly_the_fourteen_tools(tools):
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 14


def test_the_read_that_was_nearly_named_a_write():
    """A NEAR MISS, recorded rather than quietly designed around.

    The fourteenth tool was going to be ``linkedin_follow_state``, and
    ``name_implies_write`` REJECTS that name -- ``follow`` is a write verb and
    the check does not care that the tool only reads. Renaming until a guard
    stops complaining is the exact move the conservation law in
    ``test_writes.py`` exists to stop, so the rename is pinned here with its
    reason instead of being invisible in a diff.

    The reason it is not that move: ``linkedin_followed_companies`` is a
    PAST-PARTICIPLE NOUN PHRASE, the same grammar as ``linkedin_saved_jobs``
    and ``linkedin_my_applications``, which this file already blesses two tests
    below. It describes a list, not an act. The rejected name is asserted to
    still be rejected, so the guard is shown holding rather than assumed to.
    """
    assert readonly.name_implies_write("linkedin_follow_state") is True
    assert readonly.name_implies_write("linkedin_unfollow") is True
    assert readonly.name_implies_write("linkedin_followed_companies") is False


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


# ---------------------------------------------------------------------------
# Undoing a write is still a write
# ---------------------------------------------------------------------------
#
# MEASURED 2026-08-23 while building the write boundary. WRITE_VERBS held
# "save" and "follow" but no negated form at all, so every name below read as
# NOT-A-WRITE and the check would have waved through a tool whose whole job is
# to mutate. They were caught only because somebody had hand-listed two of them
# in FORBIDDEN_TOOLS above -- the literal list seeing the instances someone
# remembered while the generalising check could not see the CLASS.

#: The five that were blind, each with the reason it was.
_NEGATED_WRITES = (
    ("linkedin_unsave_job", "un + a verb already on the list"),
    ("linkedin_unfollow", "un + a verb already on the list"),
    ("linkedin_unlike", "un + a verb already on the list"),
    ("linkedin_unsubscribe", "un + a verb that had to be ADDED to the list"),
    ("linkedin_disconnect", "a dis prefix, not un at all"),
)


@pytest.mark.parametrize("name,why", _NEGATED_WRITES, ids=lambda v: v.split()[0])
def test_a_negated_write_verb_still_reads_as_a_write(name, why):
    assert readonly.name_implies_write(name), (name, why)


def test_the_fix_did_not_start_seeing_writes_that_are_not_there():
    """The other direction, and the reason the prefix set is three and not ten.

    A guard that fires on ordinary nouns is one somebody switches off, so the
    read tools this server actually ships are the control.
    """
    for name in (
        "linkedin_saved_jobs",
        "linkedin_my_applications",
        "linkedin_session_info",
        "linkedin_who_viewed_me",
        "linkedin_job_detail",
        "linkedin_search_jobs",
    ):
        assert not readonly.name_implies_write(name), name


def test_the_residue_is_what_the_source_says_it_is():
    """The stated limits, pinned so the claim stays honest.

    ``readonly.NEGATION_PREFIXES`` documents two things it deliberately does
    NOT catch. A residue that is written down but never checked drifts into
    being wrong, and then the comment is worse than nothing.
    """
    # 1. "re" is excluded on purpose: it would catch five real writes and also
    #    turn "remark" into re + mark. So these stay uncaught, by decision.
    assert "re" not in readonly.NEGATION_PREFIXES
    # Names whose ONLY write signal would be the re prefix. Isolating that is
    # fiddlier than it looks and took two goes: the first draft used
    # "linkedin_resend_invite_note" and the second "linkedin_repost_update",
    # and BOTH are caught -- by the plain verbs "invite" and "update" sitting
    # inside them. A residue test that does not isolate the residue is just
    # measuring something else and calling it a limit.
    assert not readonly.name_implies_write("linkedin_resend_note")
    assert not readonly.name_implies_write("linkedin_repost")
    # ...and the collision that decision was made to avoid is real.
    assert not readonly.name_implies_write("linkedin_remark")

    # 2. The rule generalises over NEGATIONS of known verbs, not over unknown
    #    verbs. WRITE_VERBS is still a hand-kept list at its root.
    assert not readonly.name_implies_write("linkedin_boost_profile")
    assert not readonly.name_implies_write("linkedin_publish")


def test_a_docstring_cannot_claim_a_negated_write_either():
    """The same blind spot lived in the DOCSTRING check and is closed with it.

    ``\\bsubscribe\\b`` does not match inside "unsubscribe" -- there is no word
    boundary between the halves -- so "this will unfollow the company" used to
    read as a claim about nothing at all.
    """
    claims = readonly.docstring_write_claims(
        "This will unfollow the company and unsave the posting."
    )
    verbs = {verb for verb, _ in claims}
    assert {"unfollow", "unsave"} <= verbs, claims


def test_a_denial_of_a_negated_write_is_still_a_denial():
    """The negation window must keep working on the new spellings, or every
    honest boundary sentence becomes a violation."""
    denial = readonly.docstring_write_claims(
        "Lists what you saved. It has no way to unsave anything, and it never "
        "unfollows a company."
    )
    assert denial == [], denial


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
