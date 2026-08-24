"""The tool surface: seventeen tools, fourteen of which read LinkedIn.

WHAT THIS FILE USED TO ASSERT, AND WHY IT NO LONGER CAN. The brief for this
server drew a hard line -- no writes, not now, not stubbed, not "for later" --
and this file was that line expressed as assertions. On 2026-08-23 the operator
authorised two: ``linkedin_save_job`` and ``linkedin_unsave_job``. On
2026-08-24 a third arrived, ``linkedin_unfollow_company``, and the counts in
this docstring are re-measured rather than carried -- they were wrong for a day
before anybody noticed, which is the smallest possible version of the failure
this whole file is about.

The line did not move; it acquired a gate. Every check below still runs against
every tool, and the writes are exempted BY NAME through
``writes.SANCTIONED_WRITES`` rather than by loosening the check -- so a fourth
write-shaped tool, or a read tool that grows a write-shaped docstring, still
fails exactly as before. Each exemption is paired with a positive control
asserting the check DOES fire on the exempted names, because an exemption that
silently covered everything would leave a file full of tests that cannot fail.

AND NOTE WHAT IS NOT ON THE SURFACE. ``apply_job`` is a fully specced,
sanctioned action that registers NO TOOL and stays on ``FORBIDDEN_TOOLS``,
because its flow has never been captured. Being sanctioned in ``writes.py``
does not by itself exempt a name here; the two boundaries are separate, and
``test_the_exemption_covers_only_those_two`` is where that is shown.

``linkedin_logout`` writes to LOCAL DISK and to nothing else: it erases this
machine's cookie jar and issues no request. It gets its own assertions at the
bottom of this file, because "performs nothing without confirm" is a promise
somebody has to hold to.
"""

from __future__ import annotations

import pytest

from linkedin_server import readonly
from linkedin_server.server import mcp
from linkedin_server.writes import SANCTIONED_WRITES

#: The tools that write, resolved from the module that gates them rather
#: than typed again here. A name cannot appear on this exemption without
#: appearing in the sanctioned set, and the sanctioned set is what
#: ``test_writes.py``'s conservation law polices.
SANCTIONED_WRITE_TOOLS = frozenset(SANCTIONED_WRITES) & {
    "linkedin_save_job",
    "linkedin_unsave_job",
    # 2026-08-24. The intersection is the mechanism and it still is: a name
    # written here that is NOT in SANCTIONED_WRITES buys nothing, so this list
    # cannot exempt a tool the write boundary has not admitted.
    "linkedin_unfollow_company",
}

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
    # The two writes, authorised 2026-08-23.
    "linkedin_save_job",
    "linkedin_unsave_job",
    # The third, 2026-08-24. NOT accompanied by linkedin_apply_job: apply is
    # sanctioned and specced and registers NO TOOL, because its flow has never
    # been captured -- exactly the condition linkedin_set_open_to_work is in.
    # A tool that could only ever refuse would have moved a name off the
    # forbidden list to buy nothing.
    "linkedin_unfollow_company",
}

#: Names a reader must never grow. Listed explicitly so that adding one is a
#: failing test rather than a code review someone might skim.
#:
#: ``linkedin_save_job`` and ``linkedin_unsave_job`` LEFT THIS SET on
#: 2026-08-23. That is the only sanctioned way off it: the conservation law in
#: ``test_writes.py`` asserts every originally-forbidden name is still
#: accounted for by ``FORBIDDEN_TOOLS | SANCTIONED_WRITES``, so a name may MOVE
#: across the boundary and may never simply be deleted from it. The frozen
#: original set lives in that file precisely so this one cannot shrink quietly.
FORBIDDEN_TOOLS = {
    "linkedin_apply",
    "linkedin_apply_job",
    "linkedin_easy_apply",
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


async def test_the_surface_is_exactly_the_seventeen_tools(tools):
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 17
    # And the split is asserted, not just the total: fourteen reads and the
    # three named writes. A future tool arriving as a write would otherwise
    # only have to bump a number.
    assert set(tools) & SANCTIONED_WRITE_TOOLS == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_unfollow_company",
    }
    # THE READ COUNT IS UNCHANGED AT FOURTEEN, and that is the half worth
    # asserting separately: this wave added a write and added a FIELD to an
    # existing read (job_detail's apply_path) rather than a new read tool, so a
    # fourteen here is evidence the read surface did not quietly grow too.
    assert len(set(tools) - SANCTIONED_WRITE_TOOLS) == 14


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
    """No tool name implies a write EXCEPT the two whose names should.

    The exemption is a set difference against the sanctioned names, not a
    relaxed check: ``name_implies_write`` still runs on all sixteen, and a
    seventeenth tool called ``linkedin_apply_job`` still lands in ``offenders``.
    """
    offenders = [
        name
        for name in tools
        if readonly.name_implies_write(name) and name not in SANCTIONED_WRITE_TOOLS
    ]
    assert offenders == [], offenders


async def test_the_two_exempted_names_do_in_fact_trip_the_name_check(tools):
    """THE CONTROL for the exemption above.

    Without it, ``name_implies_write`` could be broken so that it returns False
    for everything and the check would pass on a surface full of writes. These
    two names are exempted BECAUSE they announce themselves; assert that they
    still do.
    """
    for name in sorted(SANCTIONED_WRITE_TOOLS):
        assert name in tools, name
        assert readonly.name_implies_write(name) is True, name


async def test_the_exemption_covers_only_those_two(tools):
    """A write-shaped tool OUTSIDE the set is not covered by it.

    ``linkedin_apply_job`` is the right probe for this and got MORE apt on
    2026-08-24, not less: apply is now a sanctioned ACTION with a full spec,
    and it still registers no tool. So this asserts something real -- that
    being sanctioned in ``writes.py`` does not by itself exempt a NAME on the
    tool surface. The two boundaries are separate and this is where they are
    shown to be.
    """
    assert SANCTIONED_WRITE_TOOLS == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_unfollow_company",
    }
    assert "linkedin_apply_job" not in set(tools)
    pretend = set(tools) | {"linkedin_apply_job"}
    offenders = [
        name
        for name in pretend
        if readonly.name_implies_write(name) and name not in SANCTIONED_WRITE_TOOLS
    ]
    assert offenders == ["linkedin_apply_job"], offenders


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
    """A docstring may say what a tool cannot do; it may not claim it does.

    Unless it is one of the two that DO. The exemption is by name, so a read
    tool whose docstring drifts into claiming a write still fails here.
    """
    offenders: dict[str, list] = {}
    for name, tool in tools.items():
        if name in SANCTIONED_WRITE_TOOLS:
            continue
        claims = readonly.docstring_write_claims(tool.description or "")
        if claims:
            offenders[name] = claims
    assert offenders == {}, offenders


async def test_the_two_write_docstrings_do_claim_a_write(tools):
    """THE CONTROL. The exemption above must be covering something real.

    If these two stopped claiming a write -- because somebody softened the
    prose into sounding like a read -- the exemption would be silently
    unnecessary and the surface would be advertising a write as a read. That
    is the failure this pins.
    """
    for name in sorted(SANCTIONED_WRITE_TOOLS):
        claims = readonly.docstring_write_claims(tools[name].description or "")
        assert claims, f"{name} does not describe itself as a write"


async def test_the_docstring_exemption_does_not_cover_the_reads(tools):
    """Plant a write claim in a READ tool's docstring; the loop must catch it.

    Runs the EXACT loop from ``test_no_docstring_claims_a_write`` over a
    descriptions map in which one read tool has been given a write-claiming
    description. If the exemption had been written as "skip anything that
    claims a write" -- the tempting shape -- this would come back empty.
    """
    descriptions = {name: tool.description or "" for name, tool in tools.items()}
    victim = "linkedin_saved_jobs"
    assert victim in descriptions and victim not in SANCTIONED_WRITE_TOOLS
    descriptions[victim] = (
        "This tool will apply to the job and send the recruiter a note."
    )

    offenders = {
        name: readonly.docstring_write_claims(text)
        for name, text in descriptions.items()
        if name not in SANCTIONED_WRITE_TOOLS
        and readonly.docstring_write_claims(text)
    }
    assert set(offenders) == {victim}, offenders


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


async def test_server_info_reports_writes_off_when_the_flag_is_unset(monkeypatch):
    """The DEFAULT posture, and the one a fresh clone is in.

    This test used to assert ``read_only is True`` flat, and after the write
    landed it still passed -- because the flag is unset in a test process, so
    the computed value is True for the right reason. That is exactly the shape
    of a check that has quietly stopped testing what it says: it would have
    gone on passing if the field had been hardcoded back to a literal. Both
    halves of the computation are now exercised, here and below.
    """
    from linkedin_server.server import linkedin_server_info
    from linkedin_server.writes import WRITES_FLAG

    monkeypatch.delenv(WRITES_FLAG, raising=False)
    info = await linkedin_server_info()
    assert info["read_only"] is True
    assert info["writes_available"] == []
    assert info["rate_discipline"]["auto_paging"] is False
    assert info["rate_discipline"]["scheduled_or_background_activity"] is False
    # The side effects are disclosed here too, not only in one docstring.
    joined = " ".join(info["known_side_effects"]).lower()
    assert "badge" in joined and "recent-search history" in joined


async def test_server_info_stops_claiming_read_only_once_writes_are_on(monkeypatch):
    """A SERVER THAT CAN WRITE AND SAYS IT CANNOT IS WORSE THAN ONE THAT NEVER
    COULD, because the claim is what a caller trusts INSTEAD of reading the
    source.

    This is the control for the test above: hardcoding either field back to its
    old literal passes that one and fails this one.
    """
    from linkedin_server.server import linkedin_server_info
    from linkedin_server.writes import WRITES_FLAG

    monkeypatch.setenv(WRITES_FLAG, "1")
    info = await linkedin_server_info()
    assert info["read_only"] is False
    assert info["writes_available"] == [
        "save_job",
        "unfollow_company",
        "unsave_job",
    ]


async def test_the_capability_is_reported_even_with_the_flag_off(monkeypatch):
    """``writes_sanctioned`` is about the CODE and never about the process.

    Without it, a reader of a default process would see read_only true and an
    empty writes list and conclude this package has no write path. It has one.
    The capability may not hide behind an unset environment variable.
    """
    from linkedin_server.server import linkedin_server_info
    from linkedin_server.writes import WRITES_FLAG

    monkeypatch.delenv(WRITES_FLAG, raising=False)
    info = await linkedin_server_info()
    assert info["writes_sanctioned"] == [
        "save_job",
        "unfollow_company",
        "unsave_job",
    ]
    assert "OFF" in info["writes_note"]
    assert "unsave_job" in info["writes_note"]

    # AND THE THIRD LAYER, which is the one a caller needs to tell "not
    # offered" from "examined and refused". Every sanctioned action that is
    # not performable must appear here with a reason, or the field is a subset
    # pretending to be a list.
    not_performed = info["writes_sanctioned_but_not_performed"]
    assert set(not_performed) == {
        "apply_job",
        "follow_company",
        "set_open_to_work",
    }
    for action, entry in not_performed.items():
        assert len(entry["why_not"]) > 80, action
    # The two with no measured surface cannot even hold a grant, and the field
    # says so rather than leaving a reader to infer it from a missing url.
    assert not_performed["apply_job"]["can_hold_a_grant"] is False
    assert not_performed["set_open_to_work"]["can_hold_a_grant"] is False
    assert not_performed["follow_company"]["can_hold_a_grant"] is True


async def test_no_stale_entry_survives_on_the_out_of_scope_list():
    """A stale entry on this list is a lie a caller acts on.

    REWRITTEN 2026-08-24, and the rewrite is the point. This test used to
    assert the literal phrase "applying to jobs", which had exactly the wrong
    effect the moment applying was examined: it pinned the SHAPE of a refusal
    rather than its truth, so the honest new entry -- which distinguishes the
    measured apply control from the uncaptured apply flow -- failed a test
    whose job was to stop the list going stale.

    So it asserts the two properties that actually matter and neither of them
    is a phrase. First, nothing on the list is contradicted by what the server
    reports elsewhere. Second, EVERY entry declares which KIND of no it is,
    because "we refuse this on principle", "we measured it and it will not
    work", and "nobody has looked" are three different statements and a list
    that flattens them is how an unexamined gap comes to read as a design
    decision. That is the exact claim this server had to retract about its own
    write path across four documents.
    """
    from linkedin_server.server import linkedin_server_info

    info = await linkedin_server_info()
    entries = info["out_of_scope_by_design"]
    scope = " ".join(entries)

    # The things this server DOES do may not appear as things it does not.
    assert "saving or unsaving jobs" not in scope
    for performed in info["writes_available"] or info["writes_sanctioned"]:
        assert f"{performed}:" not in scope, performed

    # Every entry is classified with a KNOWN label, and more than one label is
    # in play -- a list where every entry wore the same one would pass a "has a
    # label" check while carrying no information.
    #
    # AMENDED 2026-08-24, and for the second time this test has made the same
    # mistake in a new costume. It previously required the set of labels to
    # equal all three, which made "UNMEASURED must appear" an invariant -- so
    # the moment the last unexamined gap was actually measured (inbox reading),
    # this test failed for the offence of the list becoming MORE honest. That
    # is the same defect the docstring above describes: pinning the shape of
    # the list rather than the property that makes it worth having. An empty
    # UNMEASURED category is a legitimate and good state, and a test may not
    # demand that an unexamined gap exist forever.
    #
    # The second loop below was also replaced. It asserted that each entry's
    # label was in `classes` -- a set built from those same entries one line
    # earlier -- so it was TRUE BY CONSTRUCTION and could not fail for any
    # input whatsoever, including an entry labelled "BANANA". It now checks
    # against the known vocabulary, which is what it was always meant to say.
    known = {"POLICY", "MEASURED", "UNMEASURED"}
    classes = {entry.split(":", 1)[0] for entry in entries}
    assert classes <= known, f"unknown label(s): {classes - known}"
    assert len(classes) > 1, f"every entry wears the same label: {classes}"
    for entry in entries:
        assert entry.split(":", 1)[0] in known, entry

    # The two refusals most likely to be quietly dropped are still named, by
    # subject rather than by wording.
    assert "collecting data about other members" in scope
    assert "off-site applicant-tracking system" in scope
    # Following is still refused, and applying is still not performed -- but
    # neither is claimed to be unexamined any more.
    assert "following a company" in scope
    assert "submitting a LinkedIn-hosted application" in scope

    # EVERY UNMEASURED ENTRY MUST NAME WHAT WOULD MEASURE IT. An honest "we
    # have not looked" that does not say how to look is just a nicer-sounding
    # version of the claim it replaced.
    #
    # CONDITIONAL, from 2026-08-24, and for the same reason as the label-set
    # assertion above: this required EXACTLY ONE unmeasured entry, so measuring
    # the last one broke it. The requirement was never "an unexamined gap must
    # exist" -- it was "an unexamined gap must be actionable". Zero of them
    # satisfies that vacuously and correctly.
    #
    # Note what this does NOT do: it does not name _probe_messaging.py. Pinning
    # the instrument for a specific entry is what made this assertion die when
    # that entry graduated. Any entry claiming nobody has looked must point at
    # something runnable; which script that is, is not this test's business.
    unmeasured = [e for e in entries if e.startswith("UNMEASURED")]
    for entry in unmeasured:
        assert ".py" in entry or "scripts/" in entry, (
            "an UNMEASURED refusal must name the instrument that would settle "
            f"it, otherwise it is an excuse rather than a gap: {entry}"
        )


async def test_the_server_instructions_name_every_write_that_ships():
    """The instructions are the first thing a client model reads.

    They used to say "Every tool reads; none of them changes anything on
    LinkedIn. There is no apply, no save..." -- which was true, and which the
    write made into the most load-bearing false sentence in the package.

    COUNTED RATHER THAN SPELLED, from 2026-08-24. The old assertion looked for
    the words "two write", which meant the instructions and the tool registry
    could disagree while the test stayed green -- a third write would only have
    to leave the sentence alone. It now derives the number from
    ``writes.PERFORMABLE`` and requires every performable action's TOOL NAME to
    appear, so a write that ships without being announced fails here.

    It also pins the apply paragraph, and that is not decoration: this file is
    read INSTEAD of the source by every client model, so "applying is out of
    scope" living here would recreate, in the worst possible place, the exact
    claim four documents had to retract.
    """
    from linkedin_server import writes

    text = (mcp.instructions or "").lower()
    words = {2: "two", 3: "three", 4: "four", 5: "five"}
    assert f"{words[len(writes.PERFORMABLE)]} write" in text
    for action in writes.PERFORMABLE:
        tool = writes.spec_for_action(action).tool_name
        assert tool.lower() in text, tool
    assert "performs nothing" in text
    assert "never confirm on his behalf" in text

    # The apply paragraph: it must offer the half that ships and refuse the
    # half that does not, WITHOUT calling the refusal a scoping decision.
    assert "apply_path" in text
    assert "does not submit applications" in text or "not submit" in text
    assert "out of scope" not in text

    # And it must not still be calling itself read-only.
    assert "read-only window" not in text


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


async def test_server_info_reports_irreversibility_before_a_caller_commits(
    monkeypatch,
):
    """A preview names irreversibility for the ONE action being confirmed, and
    by then the caller has decided to try. This answers it beforehand.

    TWO LISTS, AND BOTH ARE PRINTED EVEN WHEN ONE IS EMPTY. "Nothing this
    process can perform is irreversible" is the reassuring half, and on its own
    it is indistinguishable from "we have no actions at all" -- an empty list
    is evidence of a check having run only when something else shows the check
    can produce a result. So the second list must be non-empty for the first
    one's emptiness to mean anything, and that relationship is what is
    asserted here rather than the two values separately.
    """
    from linkedin_server import writes
    from linkedin_server.server import linkedin_server_info

    info = await linkedin_server_info()
    block = info["irreversible"]

    # Derived from the specs, so a new irreversible action shows up here
    # without anybody remembering to add it.
    expected = sorted(
        spec.action
        for spec in writes.SANCTIONED_WRITES.values()
        if spec.irreversible
    )
    assert block["sanctioned_and_irreversible"] == expected
    assert expected, "the second list must not be empty or the first says nothing"

    # Nothing performable is irreversible, and that is a real property of this
    # design rather than an accident of which specs exist: every action
    # perform() will execute names its own inverse.
    assert block["performable_and_irreversible"] == []
    for action in writes.PERFORMABLE:
        assert writes.spec_for_action(action).irreversible is False, action

    # And the irreversible one is genuinely unreachable, not merely absent from
    # a list -- checked against the OTHER field rather than trusting this one.
    for action in block["sanctioned_and_irreversible"]:
        assert action in info["writes_sanctioned_but_not_performed"], action
        assert (
            info["writes_sanctioned_but_not_performed"][action]["irreversible"]
            is True
        ), action


async def test_that_irreversibility_report_would_notice_a_performable_one(
    monkeypatch,
):
    """THE CONTROL. Without it the assertion above passes on a field hardcoded
    to two empty lists, or on one that filters by the wrong predicate.

    Flips the one performable action whose spec is nearest to hand into an
    irreversible one and re-reads the report: it must move into BOTH lists.
    Nothing on LinkedIn changes; this edits a frozen dataclass in memory.
    """
    from linkedin_server import writes
    from linkedin_server.server import linkedin_server_info

    save = writes.spec_for_action("save_job")
    flipped = writes.WriteSpec(**{**save.__dict__, "irreversible": True})
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", flipped)

    block = (await linkedin_server_info())["irreversible"]
    assert "save_job" in block["performable_and_irreversible"]
    assert "save_job" in block["sanctioned_and_irreversible"]


async def test_server_info_declares_the_request_that_is_not_a_page_load():
    """The boundary block covered NAVIGATIONS and read as though it covered
    everything.

    ``assert_read_url`` is the only door to ``page.goto`` -- precise, and
    narrower than the prose around it suggests. ``auth.py`` issues one
    ``page.request.get`` that never reaches it, and the endpoint it uses is
    NOT on the read allowlist, so this server's own boundary would refuse the
    call it has always made.

    Nothing is wrong with the request; what was wrong is that a reader of
    ``linkedin_server_info`` could not have known the path existed. Declared
    now, and pinned here so the declaration cannot quietly go away while the
    call stays.
    """
    from linkedin_server import readonly
    from linkedin_server.config import ME_API
    from linkedin_server.server import linkedin_server_info

    declared = (await linkedin_server_info())["direct_api_reads"]
    assert declared, "the path exists; the block must say so"

    text = " ".join(declared)
    assert ME_API in text
    # It must say the allowlist does NOT cover it -- the whole point of the
    # entry. A declaration that named the endpoint and implied it was gated
    # would be worse than none.
    assert "NOT covered" in text
    assert readonly.is_read_url(ME_API) is False

    # AND THE SCOPE IS STATED IN ITS OWN FIELD, not only inferable from the
    # entry beside it. "There is one uncovered path" and "the boundary covers
    # navigations" are different facts: the first is an exception a reader
    # files away, the second tells them how to reason about the NEXT thing
    # somebody adds. A caller who only saw the exception would assume any new
    # read is gated.
    scope = (await linkedin_server_info())["read_boundary_scope"]
    assert "NAVIGATION-ONLY" in scope
    assert "page.request.get" in scope
    assert "assert_read_url" in scope


async def test_that_declaration_is_not_a_hardcoded_string():
    """THE CONTROL. The field must describe the package, not repeat a
    sentence somebody typed once.

    If the enumerated call-site list and the declaration disagree, one of them
    is stale -- and the dangerous direction is a declaration surviving after
    the call it describes has moved. Cross-checked against the AST
    enumeration that ``test_api_call_sites.py`` owns.
    """
    from linkedin_server.server import linkedin_server_info
    from tests.test_api_call_sites import SANCTIONED_API_CALLS, _api_call_sites

    declared = " ".join((await linkedin_server_info())["direct_api_reads"])
    sites = _api_call_sites()

    # DERIVED, NEVER LITERAL. This line read `== 1` until 2026-08-24 and that
    # was the very defect the test exists to catch, committed inside the test
    # itself: a hardcoded count that agreed with the world until the world
    # moved, then failed for the right reason and looked like a regression.
    # The invariant is that the three views AGREE, not that any of them is a
    # particular number.
    assert len(sites) == len(SANCTIONED_API_CALLS)
    assert len((await linkedin_server_info())["direct_api_reads"]) == len(sites)
    assert "GET" in declared

    # Every enumerated call site's MODULE must be named somewhere in the
    # declaration, so a second call added with a copied-and-pasted entry that
    # describes the first one still fails.
    for module, _verb, _arg in sites:
        stem = module.replace(".py", "")
        assert stem in declared or stem.replace("_", " ") in declared, module
