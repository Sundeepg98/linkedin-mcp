"""The tool surface: nineteen tools, fifteen of which read LinkedIn.

WHAT THIS FILE USED TO ASSERT, AND WHY IT NO LONGER CAN. The brief for this
server drew a hard line -- no writes, not now, not stubbed, not "for later" --
and this file was that line expressed as assertions. On 2026-08-23 the operator
authorised two: ``linkedin_save_job`` and ``linkedin_unsave_job``. On
2026-08-24 a third arrived, ``linkedin_unfollow_company``. On 2026-08-25 a
fourth, ``linkedin_apply_job``. The counts in this docstring are re-measured
rather than carried -- they were wrong for a day before anybody noticed, which
is the smallest possible version of the failure this whole file is about.

The line did not move; it acquired a gate. Every check below still runs against
every tool, and the writes are exempted BY NAME through
``writes.SANCTIONED_WRITES`` rather than by loosening the check -- so a fifth
write-shaped tool, or a read tool that grows a write-shaped docstring, still
fails exactly as before. Each exemption is paired with a positive control
asserting the check DOES fire on the exempted names, because an exemption that
silently covered everything would leave a file full of tests that cannot fail.

AND NOTE WHAT IS NOT ON THE SURFACE. This paragraph named ``apply_job`` until
2026-08-25 and said it "registers NO TOOL and stays on ``FORBIDDEN_TOOLS``,
because its flow has never been captured". The flow was captured on 2026-08-24,
apply is now performed, and its name has MOVED off ``FORBIDDEN_TOOLS`` into
``SANCTIONED_WRITE_TOOLS`` -- which is the only sanctioned way off that list
and is exactly the route save and unsave took. ``set_open_to_work`` is now the
name in the condition apply used to be in: fully specced, sanctioned, and
registering no tool, because its EDITOR has never been loaded. Being sanctioned
in ``writes.py`` still does not by itself exempt a name here; the two
boundaries are separate, and ``test_the_exemption_covers_only_those_two`` is
where that is shown -- with ``set_open_to_work`` as the probe apply used to be.

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
    # 2026-08-25, and it is the intersection doing its job rather than being
    # waved past: apply was ALREADY in SANCTIONED_WRITES on 2026-08-24 and
    # adding its name here then would still have exempted nothing that shipped,
    # because no tool registered it. What changed is not this line, it is that
    # writes.PERFORMABLE admitted apply_job and server.py registered a tool.
    "linkedin_apply_job",
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
    # The third, 2026-08-24.
    "linkedin_unfollow_company",
    # A READ, added 2026-08-25, and it is the reason the read count moves off
    # fourteen for the first time in three waves. It answers "do I have
    # messages waiting" off the global-nav badge on /feed/ -- a surface
    # already loaded -- which opens nobody's conversation. It is deliberately
    # NOT an inbox reader: /messaging/ does not stay on an inbox, it redirects
    # into one thread LinkedIn picks.
    "linkedin_unread_messages",
    # The fourth WRITE, 2026-08-25, AND THIS COMMENT USED TO SAY THE OPPOSITE. It
    # read: "NOT accompanied by linkedin_apply_job: apply is sanctioned and
    # specced and registers NO TOOL, because its flow has never been captured
    # -- exactly the condition linkedin_set_open_to_work is in. A tool that
    # could only ever refuse would have moved a name off the forbidden list to
    # buy nothing." Every clause of that was true when written and the first
    # one is now false: the apply flow WAS captured, on 2026-08-24, and the
    # tool registered here does not only ever refuse -- it performs, behind the
    # same two-call gate as the other three plus a second gate that re-reads
    # the modal before the submit is pressed. The last clause still holds and
    # is why this name could move at all: it buys something now.
    #
    # linkedin_set_open_to_work is STILL in that condition and still registers
    # no tool, so the sentence above did not lose its subject -- it lost apply.
    "linkedin_apply_job",
}

#: Names a reader must never grow. Listed explicitly so that adding one is a
#: failing test rather than a code review someone might skim.
#:
#: ``linkedin_save_job`` and ``linkedin_unsave_job`` LEFT THIS SET on
#: 2026-08-23, and ``linkedin_apply_job`` on 2026-08-25. That is the only
#: sanctioned way off it: the conservation law in ``test_writes.py`` asserts
#: every originally-forbidden name is still accounted for by
#: ``FORBIDDEN_TOOLS | SANCTIONED_WRITES``, so a name may MOVE across the
#: boundary and may never simply be deleted from it. The frozen original set
#: lives in that file precisely so this one cannot shrink quietly, and
#: ``linkedin_apply_job`` is still in it -- the move is visible there rather
#: than being an absence here.
#:
#: ``linkedin_apply`` and ``linkedin_easy_apply`` STAY. They are not the name
#: that moved: nothing is sanctioned under either spelling, and a write that
#: got itself registered under a shorter alias would be exactly the rename
#: loophole ``test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed``
#: exists to close.
FORBIDDEN_TOOLS = {
    "linkedin_apply",
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


async def test_the_surface_is_exactly_the_nineteen_tools(tools):
    """RENAMED TWICE ON 2026-08-25, from ``..._seventeen_tools`` then
    ``..._eighteen_tools``, and the rename is the
    honest half of the edit rather than noise in a diff.

    This test has now been renamed three times -- it shipped as
    ``..._nine_reads`` -- and the rule it follows is that a test name is a
    CLAIM like any other: a name saying eighteen over a body asserting
    nineteen is the exact species of stale claim this file exists to catch.
    """
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 19
    # And the split is asserted, not just the total: fourteen reads and the
    # four named writes. A future tool arriving as a write would otherwise
    # only have to bump a number.
    assert set(tools) & SANCTIONED_WRITE_TOOLS == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_unfollow_company",
        "linkedin_apply_job",
    }
    # THE READ COUNT MOVES OFF FOURTEEN, for the first time in three waves,
    # and the comment it replaces was the evidence that made that meaningful:
    # "this wave added a write and added a FIELD to an existing read rather
    # than a new read tool, so a fourteen here is evidence the read surface
    # did not quietly grow too. It has now survived two write-adding waves
    # unmoved." It moved deliberately on the third: linkedin_unread_messages
    # is a genuinely new READ, added because "do I have messages waiting" is
    # answerable off an already-loaded surface at no cost, while "show me my
    # inbox" is not. The number is asserted rather than dropped precisely so
    # the NEXT quiet growth still fails here.
    assert len(set(tools) - SANCTIONED_WRITE_TOOLS) == 15


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
    """No tool name implies a write EXCEPT the ones whose names should.

    The exemption is a set difference against the sanctioned names, not a
    relaxed check: ``name_implies_write`` still runs on every tool, and a
    write-shaped name that is not on the exemption still lands in ``offenders``.

    THE EXAMPLE IN THIS DOCSTRING WAS ``linkedin_apply_job`` UNTIL 2026-08-25
    -- "a seventeenth tool called ``linkedin_apply_job`` still lands in
    ``offenders``". That stopped being an example of anything the day apply was
    registered and exempted, so the probe moved to ``linkedin_set_open_to_work``
    and lives in ``test_the_exemption_covers_only_those_two``, which is where it
    is actually executed rather than merely described.
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

    THE PROBE MOVED ON 2026-08-25 AND THE MOVE IS THE POINT. This test used to
    run on ``linkedin_apply_job`` and its docstring said apply "got MORE apt on
    2026-08-24, not less: apply is now a sanctioned ACTION with a full spec,
    and it still registers no tool." The second half of that stopped being true
    the moment apply was registered, and a probe that is on the surface cannot
    prove anything about a name that is off it -- it would assert that the
    exemption fails to cover a name the exemption now names, which is not a
    check, it is a contradiction.

    ``linkedin_set_open_to_work`` inherits the job because it inherits the
    CONDITION, unchanged: a sanctioned action with a full spec in
    ``writes.py``, no ``url_template``, no registered tool. So what is asserted
    here is what was always asserted -- that being sanctioned in ``writes.py``
    does not by itself exempt a NAME on the tool surface. The two boundaries
    are separate and this is where they are shown to be.
    """
    assert SANCTIONED_WRITE_TOOLS == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_unfollow_company",
        "linkedin_apply_job",
    }
    # The probe has to be genuinely sanctioned for this to test the thing it
    # claims to. A name nobody ever specced would only show that made-up names
    # are not exempt, which no reader doubted.
    probe = "linkedin_set_open_to_work"
    assert probe in SANCTIONED_WRITES, probe
    assert probe not in SANCTIONED_WRITE_TOOLS, probe
    assert probe not in set(tools)
    pretend = set(tools) | {probe}
    offenders = [
        name
        for name in pretend
        if readonly.name_implies_write(name) and name not in SANCTIONED_WRITE_TOOLS
    ]
    assert offenders == [probe], offenders


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
    # apply_job JOINED THIS LIST ON 2026-08-25. It is listed rather than
    # derived on purpose: the whole value of this assertion is that a write
    # arriving on the surface has to be typed in here by whoever added it, so
    # deriving it from PERFORMABLE would make the test agree with any change.
    assert info["writes_available"] == [
        "apply_job",
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
        "apply_job",
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
    #
    # APPLY_JOB LEFT THIS FIELD ON 2026-08-25. The line below used to read
    # ``{"apply_job", "follow_company", "set_open_to_work"}`` and the two lines
    # under it used to assert that apply could not even hold a grant, "no
    # measured surface" being the reason. Apply now has a measured surface --
    # the posting page, which is where LinkedIn draws the apply modal -- so it
    # mints grants and is performed, and an entry here would now be the field
    # lying in the one direction that matters: telling a caller a capability is
    # refused when it is not.
    not_performed = info["writes_sanctioned_but_not_performed"]
    assert set(not_performed) == {
        "follow_company",
        "set_open_to_work",
    }
    for action, entry in not_performed.items():
        assert len(entry["why_not"]) > 80, action
    # The one with no measured surface cannot even hold a grant, and the field
    # says so rather than leaving a reader to infer it from a missing url.
    assert not_performed["set_open_to_work"]["can_hold_a_grant"] is False
    assert not_performed["follow_company"]["can_hold_a_grant"] is True
    # AND THE DEPARTURE IS ASSERTED FROM BOTH SIDES, because "absent from a
    # refusal list" and "present as a capability" are different claims and only
    # the pair rules out apply having simply been dropped from the report.
    assert "apply_job" not in not_performed
    assert "apply_job" in info["writes_sanctioned"]


async def test_each_kind_of_refusal_is_reported_in_its_own_field():
    """A wall and a decision may not share a bucket.

    REWRITTEN 2026-08-25, on the operator's instruction, and the rewrite is
    the point twice over.

    WHAT HE SAID: "If something is not technically possible, then refusing it
    is a different story. If something is technically possible and still you
    are refusing it, I don't know why." The single list this replaces could
    not answer that -- three kinds of no wore three prefixes on one list, and
    a prefix is easy to skim past.

    So the KIND IS NOW THE FIELD NAME, and this test no longer has to police
    labels at all. That whole job disappeared into the data structure, which
    is why the two assertions that kept breaking are gone rather than fixed
    again. Their history is worth keeping though, because they failed the same
    way twice: one required all three labels to be present, so measuring the
    last unexamined gap broke the suite for the offence of the list becoming
    MORE honest; the other checked each entry's label against a set built from
    those same entries, so it was true by construction and could not fail for
    any input at all.

    What is asserted now is what each FIELD has to prove about itself.
    """
    from linkedin_server.server import linkedin_server_info

    info = await linkedin_server_info()

    fields = (
        "cannot_be_done",
        "can_be_done_and_is_refused",
        "not_yet_measured",
        "refused_as_policy",
    )
    for field in fields:
        assert field in info, f"{field} is missing from server_info"
        assert isinstance(info[field], list), field

    # The old single field is GONE, not deprecated. A caller who still reads it
    # gets a KeyError rather than a silently stale list, which is the failure
    # mode this whole change exists to remove.
    assert "out_of_scope_by_design" not in info

    everything = " ".join(sum((info[f] for f in fields), []))

    # The things this server DOES do may not appear as things it does not.
    for performed in info["writes_available"] or info["writes_sanctioned"]:
        assert f"{performed}:" not in everything, performed

    # CANNOT must carry its MEASUREMENT, not its decision. An entry here claims
    # the strongest thing this server ever says -- that a capability does not
    # exist -- so it has to show the counting behind it.
    assert info["cannot_be_done"], "something is always impossible; say what"
    for entry in info["cannot_be_done"]:
        assert any(ch.isdigit() for ch in entry), (
            "a CANNOT entry must cite the measurement that proves it, not "
            f"merely assert it: {entry}"
        )

    # NOT-YET-MEASURED must say what would settle it. An honest "nobody has
    # looked" that does not say how to look is a nicer-sounding excuse.
    #
    # THIS IS A STUB FLOOR, NOT A SEMANTIC CHECK, and saying so is the point:
    # a length bound cannot tell whether an entry names its instrument, and a
    # sixty-one character entry saying nothing would sail through. What it DOES
    # catch is the one-line back-reference, which is the real failure mode here
    # -- it caught "SENDING a connection invitation -- same missing surface",
    # an entry that only meant anything if you had just read the one above it.
    # Entries are read one at a time, out of a json blob, by a model. Each has
    # to stand alone.
    for entry in info["not_yet_measured"]:
        assert len(entry) > 60, f"unmeasured entry is a stub: {entry}"
        assert not entry.lower().startswith("same "), entry

    # POLICY must name WHO IT PROTECTS. That is the entire test for belonging
    # here: these are the refusals that are not the operator's to lift, and the
    # only thing that earns that status is protecting somebody who is not him.
    assert info["refused_as_policy"], "policy refusals may not silently vanish"
    for entry in info["refused_as_policy"]:
        assert "Protects:" in entry, (
            "a policy refusal must name who it protects, otherwise it is a "
            f"preference wearing a policy label: {entry}"
        )

    # A POLICY ENTRY MAY ONLY LEAVE WITH A RECORDED DISSOLUTION.
    #
    # AMENDED 2026-08-25. This used to assert that "OTHER MEMBERS" and
    # "APPLICANT-TRACKING SYSTEM" both appear -- pinning two entries by
    # subject, on the reasoning that those were the two most likely to be
    # quietly dropped. The operator then dissolved the member-lookup entry
    # deliberately, and pinning a subject cannot tell a deliberate
    # dissolution from a quiet drop; it fails identically for both, which
    # makes it useless for the case it was written for.
    #
    # So the invariant moved up one level: entries may come and go, but the
    # bucket may never shrink SILENTLY. If it holds fewer than the three it
    # was created with, something has to say who removed one and when.
    policy = " ".join(info["refused_as_policy"])
    assert "APPLICANT-TRACKING SYSTEM" in policy, (
        "the off-site ATS refusal was never part of any ruling -- it is not a "
        "LinkedIn capability at all -- and may not vanish with the others"
    )
    if len(info["refused_as_policy"]) < 3:
        note = info.get("policy_dissolved", "")
        assert note, "policy entries disappeared with no dissolution recorded"
        assert "2026-08-25" in note, note
        assert "operator" in note.casefold(), note


async def test_the_refused_by_choice_field_is_the_one_that_should_empty():
    """The operator's field, and it is meant to shrink to nothing.

    ``can_be_done_and_is_refused`` is the only field on this server that is a
    standing embarrassment by design: every entry is something measured to
    WORK that is not being done anyway. His ruling was that this list should
    not exist, so the test asserts the property that makes each entry
    accountable rather than asserting a count -- pinning a count is what made
    two earlier versions of this test break when the list got better.

    An entry must say WHY, in words a person chose. "The server would rather
    not" is not a reason; it is his account.
    """
    from linkedin_server.server import linkedin_server_info

    info = await linkedin_server_info()
    for entry in info["can_be_done_and_is_refused"]:
        assert "Measured" in entry or "measured" in entry, (
            "an entry here claims something WORKS and is refused anyway, so it "
            f"must cite the measurement that established it works: {entry}"
        )
        assert "pending" in entry.lower() or "because" in entry.lower(), (
            "an entry here must say why it is not done -- a status or a "
            f"reason, never a bare refusal: {entry}"
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

    THE APPLY HALF OF THIS TEST INVERTED ON 2026-08-25 and the inversion is
    recorded rather than overwritten. It used to assert ``"does not submit
    applications" in text or "not submit" in text`` -- the server's refusal,
    pinned so it could not quietly disappear. Apply now ships, so that sentence
    would be the most load-bearing false claim in the package for the second
    time, and the assertion is flipped to catch it coming BACK: the old wording
    is now asserted ABSENT. What has not changed is the shape of the check --
    the paragraph must offer what ships and refuse what does not, and must
    still not call either one a scoping decision.
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
    # THE HALF THAT SHIPS, and its one irreducible warning. A paragraph that
    # announced the capability without the warning would be worse than the old
    # refusal, because a refusal cannot be acted on by mistake.
    assert "can now submit an application" in text
    assert "cannot be taken back" in text
    # THE HALVES THAT DO NOT SHIP, both of them, because each is a different
    # refusal and a caller who heard only one would assume the other works:
    # somebody else's applicant-tracking system, and a flow nobody has watched
    # finish.
    assert "reported and not driven" in text
    assert "applicant-tracking system" in text
    assert "multi-step one is refused" in text
    # AND THE RETRACTED CLAIM MAY NOT COME BACK. This is the assertion that
    # used to be the positive one; keeping it as a negative is what makes the
    # retraction enforceable instead of merely done once.
    assert "does not submit applications" not in text
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

    THE PROPERTY THIS TEST PINNED WAS REVERSED ON 2026-08-25, ON PURPOSE, AND
    THAT IS EXACTLY WHY THE TEST STILL MATTERS. It used to assert
    ``performable_and_irreversible == []`` and then walk ``PERFORMABLE``
    asserting every spec's ``irreversible is False``, under a docstring saying
    that was "a real property of this design rather than an accident of which
    specs exist: every action perform() will execute names its own inverse."

    It was a real property, and it is now false. ``apply_job`` became
    performable and it carries ``irreversible=True`` -- not because its
    reversibility was measured and came back no, but because it was never
    measurable at all and withdrawing is permanently forbidden here in either
    direction. So this server can now do something it cannot undo.

    The old docstring's argument inverted with it and is worth stating in its
    new form rather than deleting. It ran: an empty
    ``performable_and_irreversible`` says "nothing you can do here is
    permanent", which on its own is indistinguishable from "there is nothing
    here at all", so the second list had to be non-empty for the first one's
    emptiness to mean anything. THE FIRST LIST IS NOW THE NON-EMPTY ONE, and
    the burden of proof moves with it: an entry claiming an action is permanent
    means nothing unless the same action is reported as permanent in every
    other field that mentions it. So what is asserted is no longer a value but
    AGREEMENT ACROSS FIELDS -- which is the check that would have caught this
    change silently half-landing.
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
    assert expected, "an irreversible action exists; the report must name it"

    # THE SECOND LIST IS DERIVED THE SAME WAY, and it is the one a caller acts
    # on: sanctioned-and-irreversible includes things nobody can reach, while
    # performable-and-irreversible is the set of permanent things this process
    # will actually do if a token is redeemed.
    expected_performable = sorted(
        action
        for action in writes.PERFORMABLE
        if writes.spec_for_action(action).irreversible
    )
    assert block["performable_and_irreversible"] == expected_performable
    assert expected_performable == ["apply_job"], (
        "apply is the only permanent thing this server performs; a second one "
        "arriving must be typed in here by whoever added it"
    )
    # A performable irreversible action is a SUBSET of the sanctioned ones, and
    # the two lists disagreeing would mean one of them is computed off the
    # wrong predicate -- the failure that would make either list unreadable.
    assert set(expected_performable) <= set(expected)

    # EVERY IRREVERSIBLE ACTION IS REPORTED IRREVERSIBLE WHEREVER IT APPEARS.
    # This loop used to require each of them to be UNREACHABLE, checked against
    # writes_sanctioned_but_not_performed. That is now true of none of them, so
    # the check splits by which side of the boundary the action is on -- and
    # keeps a real assertion on both sides rather than dropping the arm that
    # went empty.
    not_performed = info["writes_sanctioned_but_not_performed"]
    for action in block["sanctioned_and_irreversible"]:
        if action in writes.PERFORMABLE:
            # Reachable AND permanent: it must be advertised as a capability
            # rather than hidden, and it must appear in the list a caller reads
            # before committing.
            assert action in info["writes_sanctioned"], action
            assert action in block["performable_and_irreversible"], action
            assert action not in not_performed, action
        else:
            assert action in not_performed, action
            assert not_performed[action]["irreversible"] is True, action


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
