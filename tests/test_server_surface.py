"""The tool surface: twenty-three tools, nineteen of which do not write.

THE HEADLINE SAID "nineteen tools, fifteen of which read LinkedIn" UNTIL
2026-08-25, and both halves of that sentence changed for the same small
reason. The count moved because the login tool was renamed to
``linkedin_login`` -- the spelling its three sibling servers use -- and the old
``linkedin_login_browser`` was KEPT as a registered deprecated alias rather
than deleted, so the surface grew a name without growing a capability. And
"read LinkedIn" was never quite what the second number counted: login, logout,
``linkedin_cdp_status`` and ``linkedin_server_info`` were always inside it and
none of them reads a LinkedIn page. It counts NON-WRITES, and now says so.

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
boundaries are separate, and ``test_the_exemption_covers_only_the_names_on_it`` is
where that is shown -- with ``set_open_to_work`` as the probe apply used to be.

``linkedin_logout`` writes to LOCAL DISK and to nothing else: it erases this
machine's cookie jar and issues no request. It gets its own assertions at the
bottom of this file, because "performs nothing without confirm" is a promise
somebody has to hold to.
"""

from __future__ import annotations

import json

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
    # THE FIFTH PERFORMABLE WRITE, 2026-08-30. follow_company had been
    # sanctioned since August and registered no tool, on the ground that this
    # server cannot aim its own unfollow at what a follow creates. That fact
    # is unchanged and was re-measured the same day; what moved is that it now
    # lives on the SPEC, in reversible_by, which the confirm block prints --
    # rather than here, deciding for him on a ground he can read.
    "linkedin_follow_company",
    # SIX TOOLS THAT ARE REGISTERED AND CANNOT ACT, added 2026-08-30. They are
    # on this exemption for one reason only: their NAMES announce a write, and
    # the check below is about names. It is not a claim that any of them can
    # perform anything -- none is in writes.PERFORMABLE, none holds a
    # url_template, and writes.mint refuses them a grant at issue, so no
    # confirm token exists for any of them to redeem.
    #
    # THE INTERSECTION IS STILL THE MECHANISM: every name here is also a key
    # in writes.SANCTIONED_WRITES, so this list cannot exempt a tool the write
    # boundary has not admitted.
    #
    # ``linkedin_update_setting`` IS DELIBERATELY ABSENT and its absence is a
    # finding rather than an omission. It is a sanctioned write and
    # ``readonly.name_implies_write`` returns False for it, because "change" is
    # on no write-verb list -- and it was measured on 2026-08-30 that adding it
    # would fire the docstring check on three READ tools that use the word to
    # describe the boundary. So the verb was left off, the residue is written
    # down in readonly.py beside WRITE_VERBS, and this name is not put on an
    # exemption it does not need: doing so would break
    # ``test_the_exempted_names_do_in_fact_trip_the_name_check``, which is the
    # control that stops this set from being a way to wave a name through.
    "linkedin_publish_post",
    "linkedin_comment_on_item",
    "linkedin_react_to_item",
    "linkedin_update_profile_field",
    "linkedin_update_setting",
    "linkedin_send_invitation",
    "linkedin_send_message",
}

#: THE DOCSTRING EXEMPTION IS THE SAME SET AS THE NAME EXEMPTION, and it took
#: one wrong turn on 2026-08-30 to establish that it should be.
#:
#: A separate ``DOCSTRING_WRITE_TOOLS`` was built that day for exactly one
#: name. ``linkedin_change_setting`` was a sanctioned write whose docstring
#: necessarily claims a write -- it warns that two of the 33 settings addresses
#: are "Close and delete account" and "Hibernate account", the most important
#: sentence in it -- while its NAME did not trip ``name_implies_write``,
#: because "change" is on no write-verb list.
#:
#: THE SECOND SET WAS THE WRONG FIX AND THE RIGHT FIX WAS SMALLER: rename the
#: tool. ``linkedin_update_setting`` uses a verb the frozen conservation
#: baseline already knows, announces the write the old name concealed, and is
#: no less accurate. One exemption set again, and the machinery that had been
#: built to accommodate an under-declaring name went with the name.
DOCSTRING_WRITE_TOOLS = SANCTIONED_WRITE_TOOLS

EXPECTED_TOOLS = {
    "linkedin_auth_status",
    # THE LOGIN TOOL ANSWERS TO TWO NAMES from 2026-08-25, and BOTH belong on
    # this list because both are registered. ``linkedin_login`` is canonical --
    # the sibling servers spell it ``naukri_login``, ``instahyre_login`` and
    # ``uplers_login``, and this one being the odd name out was a wall for
    # anybody who had met the others. ``linkedin_login_browser`` is a
    # DEPRECATED ALIAS that forwards to it, kept because things already call
    # it and breaking a name that used to work is the worse failure.
    #
    # This is the only pair on the surface, and the only reason a name may
    # appear here without a capability behind it. A second alias arriving
    # would land as a set-equality failure below and should have to argue for
    # itself the same way. ``test_both_login_names_are_registered_and_the_old_
    # one_forwards`` is where the pair is shown actually behaving as one tool
    # rather than merely being listed twice.
    "linkedin_login",
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
    # A READ, added 2026-08-25 and RENAMED 2026-08-26. It shipped as
    # linkedin_unread_messages, which was a false heading over a true number:
    # the nav badge counts NEW-SINCE-LAST-VISIT and resets when the Messaging
    # tab is opened, so it read 0 with an unread recruiter InMail on screen.
    # The old name is GONE rather than aliased -- a deprecated alias is right
    # for a name that merely got better, and wrong for one that asserted
    # something false.
    "linkedin_new_messages",
    # A READ, added 2026-08-26. The third of the tracker's stages to get a
    # tool, and the one nothing could reach until the navigation allowlist was
    # deliberately widened by one alternative to admit ``?stage=draft``. Its
    # NAME is the past-participle noun phrase this file blesses two tests
    # below -- it describes a list of drafts, not the act of drafting -- and
    # ``draft`` is on no write-verb list, so nothing here is a rename dodging
    # a guard. What it reads is the tab LinkedIn labels "In Progress".
    "linkedin_draft_applications",
    # 2026-08-26. NOT A JOB-SEARCH TOOL, and the only name on this list that
    # is not: linkedin_surface_census measures what controls a page carries so
    # that the capabilities this server refuses can be costed from a reading
    # instead of a guess. It reads one page, clicks nothing, and reports
    # SHAPES rather than names -- see its own docstring and test_surface_census.py.
    "linkedin_surface_census",
    # THE MESSAGING SURFACE ITSELF, 2026-08-26, on the operator's ruling that
    # reading his own inbox is his to do. Named for what it DOES rather than
    # what the path suggests: /messaging/ does not stay on a list, LinkedIn
    # redirects it into one conversation of its own choosing, so a tool called
    # read_inbox would describe an operation the product does not offer.
    "linkedin_open_messaging",
    # THE EIGHT ADDED 2026-08-30, on the standing ruling that whatever is
    # technically possible should be achieved. ONE of them can act --
    # linkedin_follow_company, the fifth performable write. The other seven
    # are BUILT, GATED AND REFUSING: each holds a full spec, reads its own
    # surface live when previewed, and refuses with what it just saw plus the
    # one measurement that would complete it. None holds a url_template, so
    # writes.mint refuses each a grant at ISSUE and no confirm token for any of
    # them can exist.
    #
    # WHY THEY ARE ON THE SURFACE AT ALL, since a tool that can only refuse
    # looks like a name bought for nothing -- which is exactly the argument
    # this file used against registering apply in August. The difference is
    # what the alternative was. The server's instructions said "There is no
    # message, no connection request, no InMail, no profile edit, and no post
    # -- do not look for them or suggest they exist", and that sentence
    # conflates "this server will not" with "LinkedIn cannot". A tool that
    # reads the surface and names the missing measurement is discoverable and
    # correctable; a silence is neither, and a silence is what went stale.
    #
    # NOT ONE OF THEM WIDENED THE READ BOUNDARY. Each previews on a page that
    # was already allowed, and all six frozen AST digests in
    # test_readonly_boundary_invariant.py are unchanged across the commit that
    # added them -- which is checkable, and is the load-bearing half.
    "linkedin_follow_company",
    "linkedin_publish_post",
    "linkedin_comment_on_item",
    "linkedin_react_to_item",
    "linkedin_update_profile_field",
    "linkedin_update_setting",
    "linkedin_send_invitation",
    "linkedin_send_message",
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
    # 2026-08-31. A READ, and the SECOND instrument on this list rather than a
    # capability the operator would call for its own sake --
    # linkedin_surface_census is the first, and this one exists because of what
    # that one refuses to publish.
    #
    # IT IS THE ONE TOOL HERE THAT PUBLISHES NAMES. The census reports SHAPES
    # and never names, so the controls linkedin_update_profile_field would
    # target came back <opaque> from the 2026-08-31 capture of the intro
    # editor: read by the instrument and deliberately not published. The
    # operator ruled that a reader scoped to ONE container, MEASURED to be his
    # own, may publish what the document-wide gate would redact -- and the
    # measurement is per call, from LinkedIn's own isSelfProfile=true assertion
    # plus the same member segment on both landed urls.
    #
    # THE CENSUS IS UNTOUCHED, which is the half worth checking in a diff:
    # shape.census_shape behaves exactly as it did, CENSUS_SURFACES is still
    # five keys, and tests/test_editor_fields.py reads server.py's source to
    # assert the census's body has no path into the relaxed reader. A caller
    # cannot reach this behaviour through the instrument it relaxes.
    #
    # ITS NAME CARRIES "editor" AND THAT IS NOT A DODGE. "edit" is a write verb
    # on readonly.WRITE_VERBS and "editor" is not it -- name_implies_write
    # splits on non-letters and looks up whole segments, so the two are
    # different words to the guard as well as to a reader. The tool is a noun
    # phrase describing a list of fields, in the same family as
    # linkedin_draft_applications, and it loads two pages and touches nothing.
    "linkedin_profile_editor_fields",
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
#:
#: WHAT THIS LIST STOPPED MEANING ON 2026-08-30, said plainly because a list
#: nobody re-reads is how a claim goes stale. It forbids SPELLINGS, and on that
#: date seven capabilities arrived under spellings that are not on it --
#: ``linkedin_publish_post`` beside ``linkedin_post``,
#: ``linkedin_send_invitation`` beside ``linkedin_invite`` and
#: ``linkedin_connect``, ``linkedin_update_profile_field`` beside
#: ``linkedin_update_profile``. So "no write tool exists under any of its
#: obvious names" is still exactly true and is no longer a summary of what the
#: server does: posting, commenting, reacting, profile editing, settings,
#: invitations and messaging all EXIST here now, as specs behind the gate, and
#: every one of them refuses. The name that MOVED is ``linkedin_send_message``,
#: because the tool is registered under that very spelling.
#:
#: ``linkedin_endorse`` STAYS AND IS THE ONE ENTRY THAT STILL MEANS WHAT IT
#: ALWAYS DID: there is no endorsement capability under any spelling, because
#: measuring one requires loading a third party's profile and that is
#: permanently refused. It is the only one of the nine with no tool at all.
FORBIDDEN_TOOLS = {
    "linkedin_apply",
    "linkedin_easy_apply",
    # ``linkedin_send_message`` WAS HERE UNTIL 2026-08-30 and has MOVED into
    # SANCTIONED_WRITE_TOOLS, which is the only sanctioned way off this list
    # and is the route save, unsave, unfollow and apply all took. Note what
    # the move does and does not mean: the tool is registered and it CANNOT
    # SEND ANYTHING -- '/messaging/compose' is still on the read boundary's
    # forbidden substrings, no composer has ever been observed, and the tool
    # holds no url_template so no grant can be minted for it. What changed is
    # that a caller asking about messaging now meets a tool that reads the
    # nav badge, states the measured cost of opening messaging, and refuses --
    # instead of meeting nothing.
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


async def test_the_surface_is_exactly_the_thirtytwo_tools(tools):
    """RENAMED THREE TIMES ON 2026-08-25, from ``..._seventeen_tools`` through
    ``..._eighteen_tools`` and ``..._nineteen_tools``, and the rename is the
    honest half of the edit rather than noise in a diff.

    This test has now been renamed four times -- it shipped as
    ``..._nine_reads`` -- and the rule it follows is that a test name is a
    CLAIM like any other: a name saying nineteen over a body asserting
    twenty is the exact species of stale claim this file exists to catch.

    THE FOURTH RENAME IS NOT LIKE THE FIRST THREE and the difference is worth
    more than the number. Each of those moved because a tool arrived: a write
    was authorised, or a read was built. This one moved because a tool that
    was already here was RENAMED and its old name kept working --
    ``linkedin_login_browser`` became an alias for ``linkedin_login``. The
    surface is twenty NAMES over nineteen capabilities, which is why the count
    alone would be a misleading thing to read off this file, and why the
    comment beside the pair in ``EXPECTED_TOOLS`` says which two they are.

    THE FIFTH RENAME, 2026-08-26, is back to the first kind: a tool arrived.
    ``linkedin_draft_applications`` is a genuinely new READ -- the tracker's
    In Progress list, which no tool could reach because the navigation
    allowlist enumerated two stages and this is a third. So twenty-two names
    over twenty-one capabilities; the login pair is still the only pair.

    THE SIXTH RENAME, 2026-08-26, is the same kind again and the tool is an
    odd one: ``linkedin_surface_census`` is an INSTRUMENT, not a capability
    the operator would ever call for its own sake. It is counted here anyway,
    because this file counts what is REGISTERED -- a tool that is exempt from
    the surface count because somebody classified it as internal is exactly
    the hole this set-equality exists to close.

    THE SEVENTH RENAME, 2026-08-30, is the largest single move this file has
    recorded and it is the FIRST of the expensive kind that is mostly made of
    refusals. Eight tools arrived. One of them, ``linkedin_follow_company``,
    can act -- it was specced in August and deliberately unregistered, and what
    changed is not a measurement but who decides: the slug-to-id gap that held
    it back is a REVERSIBILITY fact, and the gate prints reversibility to him.
    The other seven are BUILT, GATED AND REFUSING, and counting them here is
    not a courtesy. This file counts what is REGISTERED, and it says so two
    paragraphs up about the census instrument: a tool exempt from the count
    because somebody classified it as not-really-a-capability is the hole this
    set-equality exists to close, and "it only refuses" is exactly that
    classification wearing a modest face.

    THIRTY-ONE NAMES OVER THIRTY CAPABILITIES; the login pair is still the only
    pair.

    THE EIGHTH RENAME, 2026-08-31, is the smallest kind and the test name has
    now moved five times for a tool arriving and twice for other reasons -- so
    the number in the name is doing exactly the job it was given, which is to
    make a quiet addition impossible. ``linkedin_profile_editor_fields`` is a
    genuinely new READ: it names the controls inside the intro editor on his
    own profile, which nothing here could do, because the census that reads
    that page reports shapes and refuses to publish those particular names.

    THIRTY-TWO NAMES OVER THIRTY-ONE CAPABILITIES; the login pair is still the
    only pair.
    """
    assert set(tools) == EXPECTED_TOOLS
    assert len(tools) == 32
    # And the split is asserted, not just the total. A future tool arriving as
    # a write would otherwise only have to bump a number.
    #
    # THE WRITE-SHAPED SET MOVED FROM FOUR TO TWELVE ON 2026-08-30, which is
    # the largest jump this line has taken, and the number on its own would
    # be alarming in the wrong direction. FIVE of the twelve can actually
    # perform anything -- writes.PERFORMABLE -- and the other seven hold no
    # url_template at all, so writes.mint refuses them a grant at issue. The
    # split that matters is asserted separately below, against
    # writes.PERFORMABLE rather than against this name list, because a name is
    # not a capability and this file has twice been the place that confused
    # them.
    assert set(tools) & SANCTIONED_WRITE_TOOLS == {
        "linkedin_save_job",
        "linkedin_unsave_job",
        "linkedin_unfollow_company",
        "linkedin_apply_job",
        "linkedin_follow_company",
        "linkedin_publish_post",
        "linkedin_comment_on_item",
        "linkedin_react_to_item",
        "linkedin_update_profile_field",
        "linkedin_update_setting",
        "linkedin_send_invitation",
        "linkedin_send_message",
    }
    # THE NON-WRITE COUNT MOVES TO SIXTEEN, and the reason is NOT the reason
    # it moved last time. The comment here said: "THE READ COUNT MOVES OFF
    # FOURTEEN, for the first time in three waves... It moved deliberately on
    # the third: linkedin_unread_messages is a genuinely new READ, added
    # because 'do I have messages waiting' is answerable off an already-loaded
    # surface at no cost, while 'show me my inbox' is not." That was a real
    # capability arriving and the number earned its move.
    #
    # This move is the cheap kind and must not be mistaken for the other:
    # nothing new can be done with this server since fifteen. ``linkedin_login``
    # is the login tool's canonical name and ``linkedin_login_browser`` is the
    # same function under its retired one, so a reader treating sixteen as
    # sixteen distinct things would be wrong by one. The number is still
    # asserted rather than dropped, because the next quiet growth -- an actual
    # one -- still has to fail here.
    #
    # AND EIGHTEEN, 2026-08-26, is the expensive kind again rather than the
    # cheap one: linkedin_draft_applications does something no name here could
    # do before it. The write count is unmoved at four, which is the half of
    # this line worth checking -- a read arriving must not be able to hide a
    # write arriving beside it.
    #
    # AND NINETEEN, 2026-08-30, which is the number BARELY MOVING while the
    # surface grew by eight -- it went up by one, and the one is the
    # deprecated login alias being counted, not a capability. That is the
    # whole shape of the wave: not one new READ shipped, and every one of
    # the eight new names is write-shaped and on the exemption. Seven of
    # them cannot act at all -- see the grant-incapability assertions in
    # test_writes.py -- so a reader must not take the pair of numbers on
    # this page as twelve things that write. FIVE things write.
    #
    # AND TWENTY, 2026-08-31, the expensive kind: linkedin_profile_editor_fields
    # answers a question no name here could answer, and the write count is
    # unmoved at twelve -- which is the half of this line worth checking, since
    # a read arriving must not be able to hide a write arriving beside it. It
    # is also the one addition on this line that widened a PRIVACY boundary
    # rather than the read boundary: no new url, no new navigation pattern, and
    # one container's worth of accessible names now published where the census
    # publishes none. tests/test_editor_fields.py is where that trade is held
    # to its measurement.
    assert len(set(tools) - SANCTIONED_WRITE_TOOLS) == 20


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
    and lives in ``test_the_exemption_covers_only_the_names_on_it``, which is where it
    is actually executed rather than merely described.
    """
    offenders = [
        name
        for name in tools
        if readonly.name_implies_write(name) and name not in SANCTIONED_WRITE_TOOLS
    ]
    assert offenders == [], offenders


async def test_the_exempted_names_do_in_fact_trip_the_name_check(tools):
    """THE CONTROL for the exemption above.

    RENAMED 2026-08-30 from ``..._the_two_exempted_names_...``. The set has
    held more than two names since 2026-08-24 and the name said two for six
    days, which is the smallest possible version of the stale claim this
    whole file is about. It now says nothing about the count, so it cannot
    go stale again.

    Without it, ``name_implies_write`` could be broken so that it returns False
    for everything and the check would pass on a surface full of writes. These
    two names are exempted BECAUSE they announce themselves; assert that they
    still do.
    """
    for name in sorted(SANCTIONED_WRITE_TOOLS):
        assert name in tools, name
        assert readonly.name_implies_write(name) is True, name


async def test_the_exemption_covers_only_the_names_on_it(tools):
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
        "linkedin_follow_company",
        "linkedin_publish_post",
        "linkedin_comment_on_item",
        "linkedin_react_to_item",
        "linkedin_update_profile_field",
        "linkedin_update_setting",
        "linkedin_send_invitation",
        "linkedin_send_message",
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


def test_the_open_to_work_reason_no_longer_makes_the_claim_the_live_page_refutes():
    """A LOAD-BEARING CLAIM THAT WENT FALSE, corrected rather than deleted.

    ``server._WHY_NOT_PERFORMED["set_open_to_work"]`` said, in full: "its
    editor is not addressed by a url at all -- 237 urls and 37 payload paths
    measured across five profile captures, zero of which reach it."

    EVERY NUMBER IN THAT SENTENCE IS STILL TRUE OF THE CAPTURES AND THE
    CONCLUSION IS FALSE OF THE SITE. A live census of his own profile on
    2026-08-30 found three profile editors carried as ordinary anchors --
    /in/<member>/edit/intro/, /in/<member>/edit/forms/summary/new/ and
    /in/<member>/overlay/contact-info/ -- and 2 forms where every frozen
    fixture in this repo carries none. That is the exact failure mode of
    measuring once and never re-measuring, and it is why this test asserts the
    SHAPE of the claim rather than a phrase: the entry must not say a profile
    editor is unreachable by url, and it must still say what remains true --
    that none of those anchors reaches the OPEN TO WORK editor specifically.

    The wider claim is what a reader would have acted on. The narrower one is
    what was measured.
    """
    from linkedin_server.server import _WHY_NOT_PERFORMED

    reason = _WHY_NOT_PERFORMED["set_open_to_work"]
    lowered = reason.lower()
    # THE REFUTED CLAIM, asserted absent. Its old wording is the thing that
    # must not come back, so it is matched as the words a rewrite would reuse
    # rather than as one exact sentence.
    assert "not addressed by a url at all" not in lowered
    # AND THE CORRECTION MUST BE PRESENT, or "absent" would be satisfied by
    # somebody simply deleting the entry's evidence.
    assert "url-addressed" in lowered or "url addressed" in lowered
    assert "narrowed" in lowered
    # WHAT SURVIVED, which is the whole point of narrowing rather than
    # deleting: this setting's editor is still not reachable.
    assert "open to work" in lowered
    assert "modal" in lowered
    # And the sibling capability that the same measurement UNBLOCKED is a
    # registered tool, so the correction is not merely textual.
    assert "linkedin_update_profile_field" in {
        spec.tool_name for spec in SANCTIONED_WRITES.values()
    }


def test_the_rename_that_closed_a_write_verb_gap_rather_than_widening_one():
    """WHY ``linkedin_update_setting`` is not called ``linkedin_change_setting``.

    THIS TEST WAS FIRST WRITTEN AS A RESIDUE and the residue was then removed,
    so it is now the record of the removal. It read
    ``test_a_sanctioned_write_can_sit_outside_the_name_check`` and asserted
    that ``linkedin_change_setting`` was a sanctioned write which
    ``name_implies_write`` did not recognise -- a real hole, pinned so it could
    not be mistaken for an oversight.

    THE HOLE HAD TWO POSSIBLE FIXES AND THE MEASUREMENT CHOSE BETWEEN THEM.
    Adding "change" to WRITE_VERBS would also arm the DOCSTRING check, which
    shares that list, and across every registered tool description "change"
    appears as a whole word in six -- three of them READS using it to describe
    the boundary. Renaming the tool onto "update" cost nothing, uses a verb the
    frozen conservation baseline in test_writes.py already knows, and makes the
    name announce the write it was concealing.

    READ THE DIRECTION OF THIS RENAME BEFORE READING IT AS A DODGE. The move
    ``test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed`` exists to
    stop is renaming until a write passes as a read. This is the opposite: the
    guard reported an under-declaring name and the name was corrected to
    declare more. What is asserted below is both halves -- the new name trips
    the check, and the REJECTED spelling still would not, so the judgement
    about "change" is preserved rather than forgotten.
    """
    assert readonly.name_implies_write("linkedin_update_setting") is True
    assert readonly.name_implies_write("linkedin_update_profile_field") is True
    # The rejected spellings, kept as the record of what was measured. Neither
    # is a live tool; both are what the guard would still miss, so a future
    # linkedin_change_* or linkedin_edit_* has to meet this comment first.
    assert readonly.name_implies_write("linkedin_change_setting") is False
    # "edit" IS a write verb, so the old profile name announced itself fine --
    # it was rejected for a different reason: "edit" is not on the frozen
    # conservation baseline, and test_writes.py's rename law refuses a verb the
    # original forbidden list never named.
    assert readonly.name_implies_write("linkedin_edit_profile_field") is True
    # And the verb that WAS added that day is shown working, so this test is
    # not only a record of something not happening.
    assert readonly.name_implies_write("linkedin_react_to_item") is True


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
        if name in DOCSTRING_WRITE_TOOLS:
            continue
        claims = readonly.docstring_write_claims(tool.description or "")
        if claims:
            offenders[name] = claims
    assert offenders == {}, offenders


async def test_every_exempted_docstring_does_claim_a_write(tools):
    """THE CONTROL. The exemption above must be covering something real.

    If these two stopped claiming a write -- because somebody softened the
    prose into sounding like a read -- the exemption would be silently
    unnecessary and the surface would be advertising a write as a read. That
    is the failure this pins.
    """
    for name in sorted(DOCSTRING_WRITE_TOOLS):
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
    assert victim in descriptions and victim not in DOCSTRING_WRITE_TOOLS
    descriptions[victim] = (
        "This tool will apply to the job and send the recruiter a note."
    )

    offenders = {
        name: readonly.docstring_write_claims(text)
        for name, text in descriptions.items()
        if name not in DOCSTRING_WRITE_TOOLS
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
    """THE PROMISE FOLLOWED THE CANONICAL NAME on 2026-08-25.

    This read ``tools["linkedin_login_browser"]`` until the rename. It is the
    one tool a password is typed anywhere near, so its description carrying
    the promise verbatim is the point of the test, and after the rename that
    description is ``linkedin_login``'s -- the alias's own docstring says the
    property is the same but does not repeat the sentence, so leaving the
    lookup on the old name would have been asserting the promise against the
    wrong text.

    The alias is not left uncovered by the move: it is asserted registered in
    ``EXPECTED_TOOLS``, its description is held to the same minimum length as
    every other tool's by ``test_every_tool_documents_itself``, and the test
    below drives it to prove it forwards.
    """
    text = (tools["linkedin_login"].description or "").lower()
    assert "never sees, types, stores or transmits a password" in text


async def test_both_login_names_are_registered_and_the_old_one_forwards(
    tools, monkeypatch
):
    """THE ALIAS, SHOWN WORKING -- not merely shown listed.

    ``linkedin_login_browser`` was the login tool's only name until 2026-08-25.
    Keeping it registered is a promise to everything that already calls it, and
    a promise a set-membership check cannot verify: a name can sit in
    ``mcp.list_tools()`` while the function behind it has quietly rotted, and
    nothing else in this suite would notice, because every other assertion
    about login now looks at the canonical name.

    So this drives the deprecated name and measures where the call LANDS.
    ``login_via_browser`` is the one step that opens a window and waits for a
    human, and it is stubbed here because the promise being tested is about
    routing, not about signing in: the alias must reach the same sign-in with
    the same argument and hand back its answer unchanged. A stub that recorded
    nothing, or an alias that grew its own copy of the login logic, both fail.
    """
    from contextlib import asynccontextmanager

    from linkedin_server import browser as browser_module
    from linkedin_server import server as server_module

    assert "linkedin_login" in tools
    assert "linkedin_login_browser" in tools

    waits: list[int] = []

    @asynccontextmanager
    async def fake_session():
        yield object()

    async def fake_login(page, wait_seconds):
        waits.append(wait_seconds)
        return {"authenticated": True, "waited_for": wait_seconds}

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(server_module, "login_via_browser", fake_login)

    from_alias = await server_module.linkedin_login_browser(wait_seconds=7)

    assert waits == [7], "the alias never reached the sign-in it forwards to"
    assert from_alias == {"authenticated": True, "waited_for": 7}

    # THE CONTROL. Without it the assertions above would also pass on an alias
    # that had drifted into its own implementation -- what makes them mean
    # "forwards" is that the canonical name is measured doing the identical
    # thing through the identical stub.
    from_canonical = await server_module.linkedin_login(wait_seconds=7)

    assert waits == [7, 7]
    assert from_alias == from_canonical


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
    info = await linkedin_server_info(verbose=True)
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
    info = await linkedin_server_info(verbose=True)
    assert info["read_only"] is False
    # apply_job JOINED THIS LIST ON 2026-08-25. It is listed rather than
    # derived on purpose: the whole value of this assertion is that a write
    # arriving on the surface has to be typed in here by whoever added it, so
    # deriving it from PERFORMABLE would make the test agree with any change.
    assert info["writes_available"] == [
        "apply_job",
        "follow_company",
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
    info = await linkedin_server_info(verbose=True)
    assert info["writes_sanctioned"] == [
        "apply_job",
        "follow_company",
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
    #
    # FOLLOW_COMPANY LEFT THIS FIELD ON 2026-08-30 and SEVEN NAMES ARRIVED, so
    # the same line moved in both directions at once. Follow left because it
    # became performable; the blocker it carried -- that this server cannot aim
    # its own unfollow at what a follow creates -- is unchanged, was
    # re-measured that day, and now lives on the spec in ``reversible_by``,
    # which the confirm block prints to him. The seven arrived because the
    # capabilities the operator asked for were built as specs that refuse, and
    # a capability that is built and refuses is precisely what this field
    # exists to distinguish from one that was never considered.
    #
    # NOTE THE SHAPE OF THE NEW ENTRIES: every one of the seven reports
    # ``can_hold_a_grant: False``. None holds a url_template, so writes.mint
    # refuses each a grant at ISSUE -- there is no confirm token for any of
    # them anywhere in the process, which is a stronger statement than "the
    # tool declines to act".
    not_performed = info["writes_sanctioned_but_not_performed"]
    assert set(not_performed) == {
        "set_open_to_work",
        "publish_post",
        "comment_on_item",
        "react_to_item",
        "update_profile_field",
        "update_setting",
        "send_invitation",
        "send_message",
    }
    for action, entry in not_performed.items():
        assert len(entry["why_not"]) > 80, action
        # EVERY refusal must name its own fix or the field is a wall of
        # "cannot" that nobody can act on. Checked as a class rather than
        # per-action, so an eighth entry has to satisfy it too.
        assert entry["can_hold_a_grant"] is False, action
    # The one with no measured surface cannot even hold a grant, and the field
    # says so rather than leaving a reader to infer it from a missing url.
    assert not_performed["set_open_to_work"]["can_hold_a_grant"] is False
    assert "follow_company" not in not_performed
    assert "follow_company" in info["writes_sanctioned"]
    # AND THE DEPARTURE IS ASSERTED FROM BOTH SIDES, because "absent from a
    # refusal list" and "present as a capability" are different claims and only
    # the pair rules out apply having simply been dropped from the report.
    assert "apply_job" not in not_performed
    assert "apply_job" in info["writes_sanctioned"]


async def test_server_info_is_cheap_by_default_and_complete_on_request():
    """The routine call should not cost what the full explanation costs.

    MEASURED BEFORE THE SPLIT, because a context-budget claim without a number
    is just a feeling: the whole block was ~3136 tokens, of which
    ``not_yet_measured`` alone -- the twelve-item roadmap, each entry naming
    the instrument that would settle it -- was 772. That is 24.6% of a call a
    client makes to find out what version is running.

    The default now answers "what is running and what can it do"; the
    reasoning is behind ``verbose=True``. Nothing was deleted.
    """
    from linkedin_server.server import linkedin_server_info

    lean = await linkedin_server_info()
    full = await linkedin_server_info(verbose=True)

    def size(block):
        return len(json.dumps(block, default=str))

    # A real reduction, not a rounding one. Pinned as a ratio rather than a
    # literal token count so that adding a field to either view does not fail
    # this for the wrong reason.
    assert size(lean) < size(full) / 2, (size(lean), size(full))

    # Verbose is a superset: the split may not lose a field.
    assert set(full) - set(lean) == set(lean["omitted"]["fields"])
    assert set(lean) - {"omitted"} <= set(full)


async def test_the_lean_view_never_drops_a_hazard():
    """A shorter answer that omits a warning is not an improvement.

    THIS IS THE ASSERTION THAT MATTERS in the context-budget work. Trimming a
    payload is a mechanical change with one dangerous failure mode -- the
    thing trimmed away being the thing a caller needed in order to be careful.
    These three stay in the DEFAULT view, and a future edit that moves any of
    them behind the flag fails here rather than being noticed by somebody
    reading a diff.

    Reversibility text also stays inline on the tools that WRITE, which is a
    separate guarantee asserted elsewhere: linkedin_apply_job's own docstring
    carries the finding that nobody has established LinkedIn offers a withdraw
    at all, and that has to reach a caller at confirm time.
    """
    from linkedin_server.server import linkedin_server_info

    lean = await linkedin_server_info()
    for hazard in ("irreversible", "known_side_effects", "recovery_path"):
        assert hazard in lean, f"{hazard} was trimmed out of the default view"

    # And the caller is TOLD what is missing, by name. A short dict with no
    # note is indistinguishable from a server that stopped reporting its
    # boundary -- which is the exact absence-versus-decision confusion this
    # package spent a day removing from its own refusal list.
    assert lean["omitted"]["fields"], "omitted must name what it left out"
    assert "verbose=True" in lean["omitted"]["why"]


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

    info = await linkedin_server_info(verbose=True)

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

    info = await linkedin_server_info(verbose=True)
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

    # THE SEVEN THAT REFUSE, added to this check on 2026-08-30 and the reason
    # is the sentence it replaced. The instructions ended: "There is no
    # message, no connection request, no InMail, no profile edit, and no post
    # -- do not look for them or suggest they exist." Every clause of that was
    # true when written and every one became false the moment those tools were
    # registered. Worse than false: it is the paragraph an assistant answers
    # FROM, so a stale denial there is repeated to him as fact.
    #
    # Asserted at two shapes, because either alone can be satisfied wrongly.
    # The old sentence must be ABSENT -- a check that only looked for the new
    # names would pass on a paragraph that says both things. And every one of
    # the seven must be NAMED, so a tool cannot ship unmentioned.
    #
    # THE OLD SENTENCE IS PRESENT AND MUST BE, which is not the assertion that
    # was first written here. "not in text" was tried and is RED, because this
    # package quotes a claim it is correcting rather than swapping it silently
    # -- the convention that makes every earlier reversal in these files
    # legible. So the check is the stronger one that ask was reaching for: it
    # may appear ONCE, and only inside a frame that says it is what the
    # paragraph used to say.
    denial = "do not look for them or suggest they exist"
    assert text.count(denial) == 1
    quoted_at = text.index(denial)
    frame = text[max(0, quoted_at - 400):quoted_at]
    assert "said the opposite until 2026-08-30" in frame
    assert "it read" in frame
    # And the correction must follow it, not merely precede it.
    assert "every one of those now exists as a tool" in text
    for spec in writes.SANCTIONED_WRITES.values():
        if spec.action in writes.PERFORMABLE or spec.url_template is not None:
            continue
        if spec.tool_name == "linkedin_set_open_to_work":
            continue  # registers no tool; nothing to name.
        assert spec.tool_name.lower() in text, spec.tool_name
    # AND THE PARAGRAPH MUST SAY THEY CANNOT ACT, or naming them is worse than
    # silence: it would advertise capabilities that refuse.
    assert "none of them can act" in text
    # The two whose refusal has a COST attached must say so where an assistant
    # reads it, not only in the tool's own docstring.
    assert "does not open messaging" in text
    assert "mynetwork" in text

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

    posture = (await linkedin_server_info(verbose=True))["automation_posture"]

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

    posture = (await linkedin_server_info(verbose=True))["automation_posture"]
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

    recovery = (await linkedin_server_info(verbose=True))["recovery_path"]
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

    info = await linkedin_server_info(verbose=True)
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

    block = (await linkedin_server_info(verbose=True))["irreversible"]
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

    declared = (await linkedin_server_info(verbose=True))["direct_api_reads"]
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
    scope = (await linkedin_server_info(verbose=True))["read_boundary_scope"]
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

    declared = " ".join((await linkedin_server_info(verbose=True))["direct_api_reads"])
    sites = _api_call_sites()

    # DERIVED, NEVER LITERAL. This line read `== 1` until 2026-08-24 and that
    # was the very defect the test exists to catch, committed inside the test
    # itself: a hardcoded count that agreed with the world until the world
    # moved, then failed for the right reason and looked like a regression.
    # The invariant is that the three views AGREE, not that any of them is a
    # particular number.
    assert len(sites) == len(SANCTIONED_API_CALLS)
    assert len((await linkedin_server_info(verbose=True))["direct_api_reads"]) == len(sites)
    assert "GET" in declared

    # Every enumerated call site's MODULE must be named somewhere in the
    # declaration, so a second call added with a copied-and-pasted entry that
    # describes the first one still fails.
    for module, _verb, _arg in sites:
        stem = module.replace(".py", "")
        assert stem in declared or stem.replace("_", " ") in declared, module
