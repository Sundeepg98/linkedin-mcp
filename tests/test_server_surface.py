"""The tool surface: nine tools, and not one of them offers a write.

The brief for this server drew a hard line -- no writes, not now, not stubbed,
not "for later". This file is that line expressed as assertions, including on
the docstrings, because a tool that merely SOUNDS like it can apply to a job
will be called as though it can.
"""

from __future__ import annotations

import pytest

from linkedin_own_server import readonly
from linkedin_own_server.server import mcp

EXPECTED_TOOLS = {
    "linkedin_auth_status",
    "linkedin_login_browser",
    "linkedin_who_viewed_me",
    "linkedin_my_applications",
    "linkedin_saved_jobs",
    "linkedin_search_jobs",
    "linkedin_my_profile",
    "linkedin_notifications",
    "linkedin_server_info",
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


async def test_the_surface_is_exactly_the_nine_reads(tools):
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 9


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
    from linkedin_own_server.server import linkedin_server_info

    info = await linkedin_server_info()
    assert info["read_only"] is True
    assert info["writes_available"] == []
    assert info["rate_discipline"]["auto_paging"] is False
    assert info["rate_discipline"]["scheduled_or_background_activity"] is False
    assert info["browser"]["detection_evasion"].startswith("none")
    # The side effects are disclosed here too, not only in one docstring.
    joined = " ".join(info["known_side_effects"]).lower()
    assert "badge" in joined and "recent-search history" in joined


async def test_the_server_instructions_tell_a_caller_not_to_look_for_writes():
    text = (mcp.instructions or "").lower()
    assert "read-only" in text
    assert "no apply" in text
