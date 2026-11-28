"""The write boundary's law: what may be sanctioned, what stays forbidden,
and the rule that confines a mutating call to a granted function.

SPLIT OUT OF ``tests/test_writes.py`` ON 2026-11-27 (lane ci8). That file took
about 137 s alone, over the two-minute cap on a local gate, so it was split
by concern into six files, each well under it. This one holds its
sections 4 (the conservation law), 7 (the confinement check), 8 (the
permanent refusals say why) and the 2026-09-02 url ruling's control, moved
verbatim, with their banners and their prose. The fixtures, the navigator,
the frozen captures and the helpers stay in ``tests/test_writes.py``, which
69 test files already import them from; its module docstring is the account
of the whole write boundary these files test, and it still applies here.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from linkedin_server import readonly, shape, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    PERMANENTLY_FORBIDDEN,
    SANCTIONED_WRITES,
    mint,
    spec_for_action,
)
from tests.test_server_surface import FORBIDDEN_TOOLS
from tests.test_writes import (  # noqa: F401 -- fixtures are used by injection
    _no_grants_survive_a_test,
    writes_on,
    JOB,
    _VERBS_ADMITTED_BY_RULING,
)


# ---------------------------------------------------------------------------
# 4. The conservation law
# ---------------------------------------------------------------------------

#: The forbidden set as it stood before any write was sanctioned. Frozen here
#: so a future edit cannot shrink FORBIDDEN_TOOLS quietly -- a name may only
#: MOVE across the boundary, visibly, into SANCTIONED_WRITES.
_ORIGINAL_FORBIDDEN = frozenset(
    {
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
)


def test_no_boundary_can_be_deleted_only_moved():
    """THE conservation law. Every originally-forbidden name is still accounted
    for: either still forbidden, or sanctioned with a spec that gates it."""
    accounted = set(FORBIDDEN_TOOLS) | set(SANCTIONED_WRITES)
    missing = _ORIGINAL_FORBIDDEN - accounted
    assert missing == set(), missing


def test_the_conservation_law_would_notice_a_quiet_deletion():
    """The control. Without it the assertion above passes on any superset."""
    pretend_forbidden = set(FORBIDDEN_TOOLS) - {"linkedin_post"}
    accounted = pretend_forbidden | set(SANCTIONED_WRITES)
    assert _ORIGINAL_FORBIDDEN - accounted == {"linkedin_post"}


def test_nothing_is_both_forbidden_and_sanctioned_by_accident():
    """A name in both lists is ambiguous, and ambiguity in a boundary is a hole.

    THIS IS THE ASSERTION THAT MOVED ON 2026-08-23, and it moved by exactly the
    amount the operator authorised. It used to read all THREE sanctioned names,
    with a comment saying they were designed and gated but not shipped, and
    that the day one shipped the mismatch would be a failing test rather than a
    silent divergence. That day came, it was a failing test, and this is the
    edit it demanded.

    Two names left ``FORBIDDEN_TOOLS`` and are now registered. One did not:
    ``linkedin_set_open_to_work`` stays in both, because it stays designed and
    unshipped -- its editor has never been loaded and :func:`mint` refuses it a
    grant at issue. ``linkedin_follow_company`` was never on the forbidden list
    (it is the rename loophole the check below covers) and is sanctioned but
    not performable.

    IT MOVED AGAIN ON 2026-08-24, BY ONE NAME, AND THE MOVE WAS THE SMALLER OF
    THE TWO AVAILABLE. The paragraph that stood here read: "``linkedin_apply_job``
    is now SANCTIONED -- it has a spec, a measured route classifier, and a gate
    -- and it STAYS ON THE FORBIDDEN LIST, because it is in exactly the
    condition ``set_open_to_work`` is in: no ``url_template``, so :func:`mint`
    refuses it a grant at issue, and no tool registers it. The apply CONTROL is
    measured; the apply FLOW is not, in any capture this repo holds. The
    alternative -- registering a tool that always refuses -- would have moved a
    name off the forbidden list to buy nothing."

    THEN IT TOOK THE LARGER MOVE, ON 2026-08-25. The apply flow was captured on
    2026-08-24 -- 2 forms, 1 file input, 1 dialog, and one enabled "Submit
    application" with no Next beside it -- which removed the single premise the
    paragraph above rested on. Apply has a ``url_template`` (the posting page,
    because that is where LinkedIn draws the modal), :func:`mint` issues it
    grants, ``linkedin_apply_job`` registers, and the name LEFT
    ``FORBIDDEN_TOOLS`` by the only route out: arriving in ``SANCTIONED_WRITES``
    with a spec that gates it. The last clause of the old paragraph is the one
    that survived and is why the move was allowed at all -- the tool no longer
    only ever refuses, so the name buys something.

    ``linkedin_set_open_to_work`` is now ALONE in the overlap, still for its
    original reason: its editor is a modal nothing has ever loaded.
    """
    overlap = set(FORBIDDEN_TOOLS) & set(SANCTIONED_WRITES)
    assert overlap == {"linkedin_set_open_to_work"}, overlap
    # And the overlap is not interchangeable with the overlap being non-empty:
    # every name in it must be surface-less, which is the property that earns
    # the double listing rather than the fact of being listed twice.
    for name in overlap:
        assert SANCTIONED_WRITES[name].url_template is None, name
    # THE CONTROL FOR THE DEPARTURE, because "apply is not in the overlap" is
    # satisfied just as well by apply having been deleted from either list.
    # It must be in exactly one of them, and it must be the sanctioned one.
    assert "linkedin_apply_job" in SANCTIONED_WRITES
    assert "linkedin_apply_job" not in FORBIDDEN_TOOLS
    assert SANCTIONED_WRITES["linkedin_apply_job"].url_template is not None


def test_what_ships_is_narrower_than_what_is_sanctioned():
    """Three sets, each smaller than the last, and none of them the same thing.

    Conflating any two of these is how a boundary widens without anybody
    editing a boundary: ``SANCTIONED_WRITES`` is what may hold a GRANT,
    ``PERFORMABLE`` is what :func:`perform` will EXECUTE, and the registered
    tool names are what a CALLER can reach. Asserted as a chain so a future
    edit that grows one has to grow it visibly.

    THE MIDDLE SET GREW ON 2026-08-25 AND THE OUTER ONE DID NOT, which is the
    chain working rather than failing. ``apply_job`` was already sanctioned; it
    crossed into ``PERFORMABLE`` and onto the registered surface in one move,
    and every line below had to be edited by hand for that to be true here --
    which is the whole design of this test. The counts that moved are recorded
    beside the sets they moved in, so a reader can see which boundary widened.
    """
    sanctioned_actions = {spec.action for spec in SANCTIONED_WRITES.values()}
    # SIX UNTIL 2026-08-30, THIRTEEN SINCE, and this is by far the largest move
    # the outer set has made. Seven capabilities the operator asked for were
    # built as specs: publishing, commenting, reacting, a profile field, a
    # setting, an invitation and a message. Being here means only that an
    # action MAY HOLD A GRANT and has somewhere for its refusal to be written
    # down -- and none of the seven can hold one, because none has a
    # url_template and writes.mint refuses at issue. The chain below is what
    # says so.
    assert sanctioned_actions == {
        "save_job",
        "unsave_job",
        "follow_company",
        "unfollow_company",
        "apply_job",
        "set_open_to_work",
        "publish_post",
        "comment_on_item",
        "react_to_item",
        "update_profile_field",
        "update_setting",
        "send_invitation",
        # (send_message left this set on 2026-09-27: RETIRED on lane L5's
        # order of 23:36, because it was aimed by a name. Nineteen became
        # eighteen.)
        # FOURTEEN FROM 2026-09-23: the follow from the Page itself (census
        # row N 47). It entered the outer set and the middle one in the same
        # move, as apply did on 2026-08-25 -- sanctioned and performable at
        # once, on a surface and an anchor already measured.
        "follow_company_page",
        # FIFTEEN FROM 2026-09-24: "I'm interested" (census row P I14, lane
        # L7), sanctioned and performable in the same move, on the posting
        # address save and follow already act on and an anchor measured on
        # three tracked captures.
        "mark_company_interest",
        # LANE B4, 2026-10-10: the similar-jobs alert and its inverse (census
        # J 161), sanctioned and performable in the same move.
        "set_similar_jobs_alert",
        "unset_similar_jobs_alert",
        # LANE BUILD-JMN26, 2026-11-25: a job search's alert and its inverse
        # (census J 31), sanctioned and performable in the same move.
        "set_search_job_alert",
        "unset_search_job_alert",
        # LANE BUILD-JOBS2, 2026-11-26: the recommendations feedback press
        # (census J 163), receipt-only, sanctioned and performable in one move.
        "send_recommendations_feedback",
        # LANE BUILD-MSG2, 2026-11-26: the five acts on one conversation's
        # own options menu (census M M26, M M27, M M29, M M31), sanctioned
        # and performable in the same move.
        "set_conversation_muted",
        "unset_conversation_muted",
        "mark_conversation_unread",
        "set_conversation_archived",
        "set_conversation_deleted",
        # LANE BUILD-MSG2, the same day: a post in one group he names (census
        # M C64), sanctioned and performable in the same move.
        "publish_group_post",
        # SIXTEEN FROM LANE L5'S MERGE OF MASTER 66aaa95, the same day (fifteen
        # on the lane's branch): the reply inside a conversation he names
        # (census M M10), sanctioned and performable in the same move.
        "send_reply",
        # LANE U, 2026-10-10: one file into one conversation he names (census
        # M M14 / M15 / M18), sanctioned and performable in the same move, on
        # the reply's own address and a file input aimed on a real capture.
        "send_attachment",
        # SEVENTEEN FROM LANE L8'S MERGE OF MASTER, 2026-09-27 (sixteen on the
        # lane's branch): leaving one group (census rows M C63 / N 64),
        # sanctioned and performable in the same move, under
        # OUTWARD-CLASSES-BUILT-BEHIND-GRANTS, on the admitted /groups/ root
        # and an item measured on all five membership rows' menus.
        "withdraw_from_group",
        # LANE BUILD-NET2, 2026-11-26: the three invitation answers (census
        # N 15, N 16, N 10), sanctioned and performable in the same move, on
        # the two admitted tabs of his invitation manager.
        "accept_invitation_to_connect",
        "ignore_invitation_to_connect",
        "withdraw_invitation",
        # LANE BUILD-NET2, 2026-11-26: one feed item he names marked Not
        # interested (census N 154), sanctioned and performable in one move.
        "mark_not_interested",
        # LANE MSG7, 2026-11-27: one feed item he names saved (census M C36),
        # sanctioned and performable in one move.
        "save_post",
        # EIGHTEEN AND NINETEEN FROM LANE L5'S MERGE OF MASTER 52b55b6, the
        # same day (seventeen and eighteen on its follow-up branch): Connect
        # and Message on the profile of a person he names (census N 4 by D6,
        # N 2, and M M1), sanctioned and performable in the same move, on
        # ruling THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET.
        "connect_from_profile",
        "message_from_profile",
        # 2026-10-10 (lane S, settings, HIS-OWN-SETTINGS-NOT-OUTWARD): ONE
        # control on ONE admitted settings page, sanctioned and performable in
        # the same move, its press perform()'s own (census P O17).
        "set_admitted_setting",
        # TWENTY FROM 2026-10-10 (lane NP, the orchestrator's ruling of
        # 14:14): the reaction's inverse, sanctioned and performable in the
        # same move, on the reaction's own address and reader.
        "withdraw_reaction",
        # LANE BUILDS-26, 2026-11-24: sanctioned and NOT performable, the
        # set_open_to_work shape -- the stage move on a saved job (census
        # J 54), whose control has never been captured.
        "set_tracker_stage",
        # LANE BUILDS-26, the same change: the endorsement pair (census P E4 /
        # N 111 and P E5 / N 113), sanctioned and NOT performable -- the
        # per-skill control has never been captured.
        "endorse_skill",
        "withdraw_endorsement",
        # LANE BUILD-JOBS2, 2026-11-26: sanctioned and NOT performable --
        # clearing his recent job searches (census J 19), refusing until the
        # dialog its press opens is captured (J-19-BUILT-BEHIND-THE-GRANT).
        "set_recent_job_searches_cleared",
        # LANE BUILD28, 2026-11-28 (census P M3, P M1): the same shape.
        "set_resume_deleted",
        "set_resume_uploaded",
    }
    # THREE UNTIL 2026-08-25, four until 2026-08-30, five since. This line read
    # ``{"save_job", "unsave_job", "unfollow_company"}``.
    #
    # follow_company entered on 2026-08-30 and it is the one entry here whose
    # move was NOT a new measurement. The objection it was held on -- that this
    # server cannot aim its own unfollow at what a follow creates -- is
    # unchanged and was re-measured that day (linkedin_job_detail returns a
    # SLUG company_url, not an id). What moved is that a reversibility fact
    # belongs in the gate the operator reads, not in a list that decides for
    # him.
    #
    # SIX SINCE 2026-08-31, and this entry is the first that is not about a
    # job or a company Page. ``update_setting`` crossed on a measured surface
    # (six agreeing readings of /mypreferences/d/dark-mode), a measured anchor
    # (three inputs, exactly one checked, the ROLE read off the row) and a
    # real verification (a fresh navigation and a re-read of the group's own
    # checked property). NOTHING WAS PERMITTED TO LET IT CROSS:
    # readonly.SANCTIONED_MUTATIONS is the two entries it has been since
    # 2026-08-26, because the click it needs is perform()'s existing one.
    # SEVEN SINCE 2026-09-01, and ``react_to_item`` crossed differently from
    # all six before it. Each of those crossed when its LAST BLOCKER WAS
    # MEASURED AWAY. This one crossed with a blocker still open: which
    # reaction the toggle applies has never been established, and the ON-state
    # label has never been seen. The operator lifted the verification standard
    # that day -- an unverifiable outcome is shippable PROVIDED THE GATE SAYS
    # SO -- and admitted this one with the gap stated in the spec's
    # ``residue``, which the confirm block prints.
    #
    # WHAT DID NOT MOVE, and the distinction is the whole ruling: this action
    # HAS a real verification. A fresh render of the permalink, the control
    # present and no longer wearing the off label, returns ``to_state``. It
    # answers WHETHER it moved and declines to say WHAT TO. That is not the
    # apply_job shape -- a check that could not pass on any reading it could
    # take -- and tests/test_unverifiable_outcomes.py asserts the difference.
    #
    # NOTHING WAS PERMITTED TO LET IT CROSS: readonly.SANCTIONED_MUTATIONS is
    # the two entries it has been since 2026-08-26, because the click it needs
    # is perform()'s existing one.
    assert writes.PERFORMABLE == {
        # THE ELEVENTH, 2026-09-02, on the operator's ruling "I want all
        # capabilities". THE ORDINAL READ "TWELFTH" UNTIL 2026-09-02 AND WAS
        # OFF BY ONE -- writes.py has always called this one the eleventh, and
        # tests/test_receipt_names_its_own_action.py measured PERFORMABLE at
        # eleven with this action already in it. Corrected here on the day a
        # real twelfth arrived, because two entries in one set literal both
        # captioned THE TWELFTH is precisely the rot this file's captions
        # exist to prevent.
        #
        # It is the only member of this set that can verify its
        # own outcome by reading the changed value back -- publish_post
        # declared its outcome unverifiable, send_invitation has none at all,
        # and apply_job can establish only that it did NOT happen. It is also
        # the only one that hands back the value it overwrote, verbatim, with
        # the exact call that restores it and the statement that this server
        # will not run that call for him.
        "update_profile_field",
        "save_job",
        "unsave_job",
        "unfollow_company",
        "apply_job",
        "follow_company",
        "update_setting",
        "react_to_item",
        # THE EIGHTH, same day as the seventh, and it crossed on the OTHER
        # half of the same ruling. react_to_item kept a real verification and
        # disclosed what that verification could not say. This one has NO
        # verification at all -- nothing this server may read can confirm a
        # sent invitation -- and ships on the declaration itself.
        #
        # It is also the SECOND performable action that cannot be undone, and
        # the first that lands on a person rather than a company.
        "send_invitation",
        # THE NINTH, same day, AND THE FIRST THAT TYPES. One page.fill, one
        # drain point, text taken from the grant. It cost the package its "it
        # types nothing" guarantee and readonly.SANCTIONED_MUTATIONS grew from
        # two entries to three -- the first growth that is not a click.
        "publish_post",
        # THE TENTH, same day, and the only one in this set that ships
        # EXPECTING TO REFUSE. Its submit control has never been observed and
        # no ruling can measure one; the gate identifies it by ARRIVAL after
        # the fill and refuses with the observation when two controls share a
        # name. The refusal is what produces the missing measurement.
        "comment_on_item",
        # (THE TWELFTH, send_message, 2026-09-02 to 2026-09-27: it emptied the
        # gap this test is about, and shipped expecting to refuse on a missing
        # AIM -- a name in a typeahead. RETIRED on lane L5's order of 23:36:
        # the aim was a name, which mitigation 6 forbids. The gap stays empty:
        # set_open_to_work is still the one sanctioned action unperformed.)
        # THE THIRTEENTH, 2026-09-23, and the first write added under the
        # operator's reversible-first-round class since that round's own
        # three: a follow performed on the organisation Page root, addressed
        # by the numeric id unfollow_company keys its rows by -- so it is the
        # first follow whose undo this server can aim. Verified on Manage
        # Pages, a different surface. NOTHING WAS PERMITTED TO LET IT CROSS:
        # readonly.SANCTIONED_MUTATIONS is unchanged, because the click is
        # perform()'s existing one, and no boundary moved.
        "follow_company_page",
        # THE FOURTEENTH, 2026-09-24 (census row P I14): "I'm interested" in
        # one posting's About-the-company card, aimed by the card's own
        # employer, verified on a fresh render. Its undo (P I15) presses an
        # ON-state control no capture holds, so it crossed with NO tested
        # restore -- stated in its spec and its census cell, and the reason its
        # live fire waits on that capture. NOTHING WAS PERMITTED TO LET IT
        # CROSS: the click is perform()'s existing one.
        "mark_company_interest",
        # LANE B4, 2026-10-10: the similar-jobs alert and its inverse (census
        # J 161), sanctioned and performable in the same move.
        "set_similar_jobs_alert",
        "unset_similar_jobs_alert",
        # LANE BUILD-JMN26, 2026-11-25: a job search's alert and its inverse
        # (census J 31), sanctioned and performable in the same move.
        "set_search_job_alert",
        "unset_search_job_alert",
        # LANE BUILD-JOBS2, 2026-11-26: the recommendations feedback press
        # (census J 163), receipt-only, sanctioned and performable in one move.
        "send_recommendations_feedback",
        # LANE BUILD-MSG2, 2026-11-26: the five acts on one conversation's
        # own options menu (census M M26, M M27, M M29, M M31), sanctioned
        # and performable in the same move.
        "set_conversation_muted",
        "unset_conversation_muted",
        "mark_conversation_unread",
        "set_conversation_archived",
        "set_conversation_deleted",
        # LANE BUILD-MSG2, the same day: a post in one group he names (census
        # M C64), sanctioned and performable in the same move.
        "publish_group_post",
        # THE FIFTEENTH, 2026-09-24 (the fourteenth on lane L5's branch), and
        # the first write that CONFIRMS ITSELF
        # FROM THE SURFACE A PERSON READS: a reply inside a conversation he
        # names by thread id, typed only into an empty reply box, pressed only
        # when the box holds exactly his words, and SENT only off a FRESH load
        # -- his words the last message, not the other side's, one more copy
        # of them than the preview counted. NOTHING WAS PERMITTED TO LET IT
        # CROSS: readonly.SANCTIONED_MUTATIONS is unchanged -- the fill and
        # the click are perform()'s own -- and the thread address was
        # already on the read allowlist.
        "send_reply",
        # LANE U, 2026-10-10: the FIRST WRITE THAT HANDS A BROWSER A FILE --
        # one file into one conversation he names, its bytes read once,
        # compared with the preview's digest and handed over as a payload,
        # Send pressed only when the form draws the file's name exactly once.
        # NOTHING WAS PERMITTED TO LET IT CROSS: the hand-off is perform()'s
        # one set_input_files, sanctioned 2026-09-04, and the press its one
        # click; readonly.SANCTIONED_MUTATIONS is unchanged.
        "send_attachment",
        # THE SIXTEENTH, 2026-09-27 (census rows M C63 / N 64, lane L8; the
        # fifteenth on its branch until its merge of master brought send_reply):
        # leaving one group he names by numeric id, on the /groups/ root. TWO
        # presses and still NO new permission: the disclosure and the item
        # both drain perform()'s one click queue, the item appended only by
        # a gate that re-reads the menu (writes.MENU_ITEM_ACTIONS). No undo
        # is built here, and its spec says so.
        "withdraw_from_group",
        # LANE BUILD-NET2, 2026-11-26: accept, ignore and withdraw one pending
        # invitation he names by the member's link (census N 15, N 16, N 10).
        # ONE press each and NO new permission; a dialog it draws is counted
        # and never answered, and a fresh render of the tab decides.
        "accept_invitation_to_connect",
        "ignore_invitation_to_connect",
        "withdraw_invitation",
        # LANE BUILD-NET2, 2026-11-26: one feed item he names marked Not
        # interested (census N 154), sanctioned and performable in one move.
        "mark_not_interested",
        # LANE MSG7, 2026-11-27: one feed item he names saved (census M C36),
        # sanctioned and performable in one move.
        "save_post",
        # THE SEVENTEENTH AND EIGHTEENTH, 2026-09-27 (lane L5's follow-up; the
        # sixteenth and seventeenth on its branch until its merge of master
        # 52b55b6 brought withdraw_from_group in first): Connect and Message on
        # the profile of a person he names by link or member id, each printing
        # whom it resolved to before anything is pressed. ONE THING WAS
        # PERMITTED TO LET THEM CROSS, and it is a NAVIGATION, not a mutation:
        # a second door, readonly.assert_named_profile_url, which the read door
        # does not share and which only writes._load_named_profile can ask
        # for. readonly.SANCTIONED_MUTATIONS is unchanged -- the click and the
        # fill are perform()'s own.
        "connect_from_profile",
        "message_from_profile",
        # 2026-10-10 (lane S, settings): the generic settings writer, on the
        # one page admitted by name from a real capture. Nothing was
        # permitted to let it cross: its click and its select are perform()'s
        # own, and readonly.SANCTIONED_MUTATIONS is unchanged.
        "set_admitted_setting",
        # THE NINETEENTH, 2026-10-10 (lane NP): the reaction's inverse,
        # named on "withdraw" -- the law is not widened. NOTHING WAS
        # PERMITTED TO LET IT CROSS: the click is perform()'s existing one.
        "withdraw_reaction",
    }
    assert writes.PERFORMABLE < sanctioned_actions

    # THE GAP IS THE INTERESTING SET, so it is named rather than left as an
    # arithmetic consequence. These actions may hold a spec and will never be
    # executed, and each is here for a DIFFERENT measured reason: see
    # writes._NINE_REFUSALS and writes._refuse_unperformable, which print a
    # distinct one for each. Two until 2026-08-30; eight since, follow_company
    # having left in the same wave that brought seven in.
    # Eight until 2026-08-31, SEVEN since -- ``update_setting`` left by being
    # performed, which is the only way anything is supposed to leave.
    # TWO SINCE 2026-09-02, down from three, and ONE SINCE LATER THE SAME DAY.
    # update_profile_field and then send_message both left by SHIPPING -- the
    # only way anything leaves this set -- and each refusal was removed from
    # _NINE_REFUSALS rather than reworded, on this module's standing rule that
    # a refusal kept for a performable action tells a caller the opposite of
    # the truth.
    assert sanctioned_actions - writes.PERFORMABLE == {
        "set_open_to_work",
        # LANE BUILDS-26, 2026-11-24: the gap grows for the first time since
        # 2026-08-30, and by REGISTRATION, which is the route the refusal
        # table names -- a sanctioned action that cannot perform, with its
        # own refusal naming the missing capture.
        "set_tracker_stage",
        "endorse_skill",
        "withdraw_endorsement",
        # LANE BUILD-JOBS2, 2026-11-26 (census J 19), by registration again.
        "set_recent_job_searches_cleared",
        # LANE BUILD28, 2026-11-28 (census P M3, P M1): the same shape.
        "set_resume_deleted",
        "set_resume_uploaded",
    }
    # AND EVERY ONE OF THEM MUST SAY WHY, individually. The dict is keyed by
    # action, so a fourteenth spec that is not performable and writes no
    # refusal fails here rather than falling through perform()'s generic
    # backstop -- which says "not performable" and explains nothing.
    #
    # THE LOOP BELOW NOW RUNS ZERO BODIES, AND THAT IS SAID OUT LOUD RATHER
    # THAN LEFT TO BE DISCOVERED. The only member of the set above is
    # ``set_open_to_work``, which the loop skips, so with send_message shipped
    # there is nothing left for it to check. A ``for`` over an empty-after-
    # skipping set does not skip and does not fail; it passes in silence,
    # which is the same defect as a parametrized test over an empty sequence
    # and is how three checks in tests/test_writes_nine.py stopped running on
    # 2026-09-01 without anybody noticing.
    #
    # SO THE STATE OF THE TABLE IS ASSERTED DIRECTLY. ``_NINE_REFUSALS`` is
    # EMPTY as of 2026-09-02: it began as seven entries on 2026-08-30 and every
    # one of them left by shipping. That is not a defect -- it is the table
    # doing exactly what it was for -- but it must be a visible fact, because
    # an empty refusal table and a refusal table nobody maintains look
    # identical from here. When a thirteenth sanctioned-and-refusing action
    # arrives, this assertion fails and whoever adds it has to come here and
    # decide, which is the whole point.
    # REFILLED 2026-11-24 (lane builds-26), by exactly the arrival the
    # paragraph above says must come here and decide: a sanctioned-and-
    # refusing action, its refusal itemised by name.
    assert set(writes._NINE_REFUSALS) == {
        "set_tracker_stage", "endorse_skill", "withdraw_endorsement",
        # LANE BUILD-JOBS2, 2026-11-26 (census J 19).
        "set_recent_job_searches_cleared",
        # LANE BUILD28, 2026-11-28 (census P M3, P M1): the same shape.
        "set_resume_deleted",
        "set_resume_uploaded",
    }, sorted(writes._NINE_REFUSALS)
    for action in sanctioned_actions - writes.PERFORMABLE:
        if action == "set_open_to_work":
            continue  # its refusal predates this dict and lives inline.
        assert action in writes._NINE_REFUSALS, action
        reason = writes._NINE_REFUSALS[action]
        assert "WHAT WOULD LIFT IT" in reason.upper(), action
    # THE ONE THAT IS LEFT cannot even hold a grant: no surface has ever been loaded,
    # so mint() refuses at issue rather than leaving the write door as the only
    # thing in the way. This set held apply_job as well until its surface was
    # measured -- and the surface that measurement found is the POSTING page,
    # not an apply url, because navigating to the apply url lands back on the
    # posting with the flow drawn over it.
    #
    # A FALSE SENTENCE STOOD HERE UNTIL 2026-09-02 and it is removed rather
    # than left: "follow_company is the one that COULD be granted and still is
    # not performed, which is why its refusal is the one most likely to be
    # argued with later." follow_company ENTERED PERFORMABLE ON 2026-08-30, so
    # the sentence was false for three days and described a refusal that no
    # longer existed.
    #
    # IT IS NOTED RATHER THAN QUIETLY DELETED because it is the fifth instance
    # of one family found in this wave: prose that was correct when written,
    # became false when the code moved, and had no instrument on it. The
    # sharpest instance is the comment inside ``anchor_label_for`` describing
    # the apply_job defect -- correct, specific, present, and read -- directly
    # above the code that repeated that defect seven days later. Prose is the
    # artifact with no test on it, and the only defence found so far is to
    # convert a claim into an assertion whenever one can be.
    surfaceless = {
        spec.action
        for spec in SANCTIONED_WRITES.values()
        if spec.url_template is None
    }
    # ONE UNTIL 2026-08-30, EIGHT SINCE, and the growth is the mechanism
    # rather than a regression. Every one of the seven capabilities added that
    # day would act on an address readonly._FORBIDDEN_URL_SUBSTRINGS refuses,
    # or on a control nobody has photographed, or both -- so none of them may
    # name a write surface, and writes.mint refuses each a grant at ISSUE. That
    # is a stronger guarantee than "perform declines to run them": there is no
    # confirm token for any of them anywhere in the process.
    #
    # SEVEN SINCE 2026-08-31, SIX SINCE 2026-09-01. Each departure was by
    # being GIVEN a surface, which is the only way anything is meant to leave
    # this set. ``update_setting`` got /mypreferences/d/dark-mode after six
    # agreeing readings; ``react_to_item`` got the item permalink, which was
    # moved off readonly._FORBIDDEN_URL_SUBSTRINGS on 2026-08-31 -- the first
    # removal that list has ever had -- and loaded four times since with no
    # redirect.
    #
    # Everything still here would act on an address the read boundary
    # refuses, or on a control nobody has photographed, or would have to TYPE,
    # which is a mutation class this package sanctions nowhere. Note that the
    # last of those three is now the ONLY thing stopping some of them: the
    # operator lifted the VERIFICATION standard on 2026-09-01, which is a
    # different bar, and lifting it does not photograph a control.
    #
    # ``update_profile_field`` LEFT THIS SET ON 2026-09-02 by being GIVEN an
    # address -- the same way update_setting and react_to_item left it. It is
    # still not performable, and that is the point of the split: the ruling
    # admitted /in/me/edit/intro/ as an exact-url exemption for a write, which
    # is ADDRESSING, while PERFORMABLE membership is PERMISSION and remains the
    # operator's. See test_addressing_the_profile_editor_did_not_make_it_
    # performable for the control that proves the ordering.
    #
    # ``send_message`` LEFT THIS SET ON 2026-09-02, LATER THE SAME DAY, and it
    # left the ordinary way: it was given /messaging/compose/ as an
    # exact-substring exemption and then SHIPPED, so unlike the profile editor
    # it crossed both lines at once. What is left is ONE action, and the two
    # sets in this test have converged on it: the only sanctioned action with
    # no surface is now also the only sanctioned action that is not
    # performable. THAT CONVERGENCE IS A COINCIDENCE OF THE MOMENT AND NOT A
    # RULE, which is why the two are still asserted separately -- this file
    # spent 2026-09-02 unpicking three guards that had quietly fused
    # "unaddressed" with "unperformable" while the two happened to agree.
    assert surfaceless == {
        "set_open_to_work",
        # LANE BUILDS-26, 2026-11-24: refusing, so each names no write surface.
        "set_tracker_stage",
        "endorse_skill",
        "withdraw_endorsement",
        # LANE BUILD-JOBS2, 2026-11-26: refusing (census J 19), the same.
        "set_recent_job_searches_cleared",
        # LANE BUILD28, 2026-11-28 (census P M3, P M1): the same shape.
        "set_resume_deleted",
        "set_resume_uploaded",
    }
    # AND THE ONE THAT LEFT, asserted rather than left as an absence -- the
    # same treatment apply got when its surface was measured.
    setting_spec = spec_for_action("update_setting")
    assert setting_spec.url_template == (
        "https://www.linkedin.com/mypreferences/d/dark-mode"
    )
    assert setting_spec.url_pattern is not None
    # ITS TEMPLATE CARRIES NO ``{target}``, and that is a property worth
    # pinning rather than an omission: the page is ONE fixed address and the
    # destination is chosen by which control is clicked on it, so there is
    # nothing for a target to influence in the url.
    assert "{target}" not in setting_spec.url_template
    # And apply is on the other side of that line now, asserted rather than
    # left as an absence: a surface it can be granted against, and a pattern
    # that will only ever match a posting page.
    apply_spec = spec_for_action("apply_job")
    assert apply_spec.url_template == "https://www.linkedin.com/jobs/view/{target}/"
    assert apply_spec.url_pattern is not None


def test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed():
    """A LOOPHOLE IN MY OWN CONSERVATION LAW, found while reviewing it, closed.

    The law says a name leaves ``FORBIDDEN_TOOLS`` only by arriving in
    ``SANCTIONED_WRITES``. Nothing in it constrains a name that was NEVER on
    the forbidden list -- and ``linkedin_follow_company`` is exactly such a
    name. It sanctions a follow while ``linkedin_follow`` sits on the forbidden
    list looking untouched, which is the quiet widening the law exists to stop,
    achieved by renaming instead of by deleting.

    So a sanctioned name must additionally (a) announce itself as a write to
    the surface check, so it can never pass as a read, and (b) use a verb the
    original forbidden list already named, so a new verb cannot be smuggled in
    under a new noun.
    """
    original_verbs: set[str] = set()
    for forbidden in _ORIGINAL_FORBIDDEN:
        original_verbs |= set(readonly.iter_write_verbs_in(forbidden))

    for name in SANCTIONED_WRITES:
        # The shape check alone is enough now. Until readonly.py learned that
        # undoing a write is still a write, this needed an "or it is on the
        # forbidden list" fallback to pass at all, because linkedin_unsave_job
        # read as not-a-write. The fallback is gone because the hole is.
        assert readonly.name_implies_write(name), f"{name} does not read as a write"
        verbs = set(readonly.iter_write_verbs_in(name))
        assert _verb_is_admissible(verbs, original_verbs), (name, sorted(verbs))


def _verb_is_admissible(verbs: set[str], original_verbs: set[str]) -> bool:
    """Is every verb in a sanctioned name one the original list already knew?

    THE CARVE-OUT AND WHY IT IS THIS NARROW. ``linkedin_unfollow_company``
    arrived on 2026-08-24 and failed the plain rule, correctly: ``unfollow`` is
    not on the original forbidden list. It is not a smuggled capability, it is
    the UNDO of one that is (``linkedin_follow``), and the original list simply
    predates anybody contemplating an unfollow -- ``linkedin_unsave_job`` is on
    it only because whoever wrote it happened to think of the inverse that day.
    The list is the frozen conservation baseline and is not edited.

    So the rule admits ``un`` + an original verb, AND NOTHING ELSE. It does not
    admit a new verb, and it does not admit ``un`` + a new verb -- which is the
    escape a looser reading would open, since anything can be prefixed. The
    control below is written at exactly that shape.
    """
    if verbs & original_verbs:
        return True
    if verbs and verbs <= _VERBS_ADMITTED_BY_RULING:
        return True
    return bool(verbs) and all(
        verb.startswith("un") and verb[2:] in original_verbs for verb in verbs
    )




def test_the_inverse_carve_out_admits_an_undo_and_nothing_else():
    """THE CONTROL for the carve-out above, at the shape it must reject.

    Without this, "un + an original verb" reads as a rule and behaves as a
    doorway: a genuinely new capability could walk in wearing an ``un``. Three
    cases, and the third is the one that matters -- ``unboost`` is the inverse
    of a verb nobody sanctioned, which makes it a new verb with a prefix, not
    an undo.
    """
    original = {"follow", "save", "apply", "connect"}
    assert _verb_is_admissible({"unfollow"}, original) is True
    assert _verb_is_admissible({"save"}, original) is True
    assert _verb_is_admissible({"boost"}, original) is False
    assert _verb_is_admissible({"unboost"}, original) is False
    # And a name carrying one admissible verb beside one that is not gets no
    # credit for the admissible half.
    assert _verb_is_admissible({"unfollow", "boost"}, original) is False
    # A name with no verb at all reads as a read, and a read is not sanctioned
    # through this door.
    assert _verb_is_admissible(set(), original) is False


def test_the_ruling_carve_out_admits_exactly_two_verbs_and_no_derivative():
    """THE CONTROL for the second carve-out, at the shapes it must reject.

    An enumerated exception is only as good as the doorway it refuses to
    become. The first carve-out is a RULE and generalises; this one is a LIST
    and must not. So: the two named verbs pass, a third does not, prefixing one
    of them does not, and a name pairing an admitted verb with an inadmissible
    one gets no credit for the admitted half.
    """
    original = {"follow", "save", "apply", "connect"}
    assert _VERBS_ADMITTED_BY_RULING == {"comment", "react"}
    assert _verb_is_admissible({"comment"}, original) is True
    assert _verb_is_admissible({"react"}, original) is True
    # A third verb from the same family is NOT admitted by association.
    assert _verb_is_admissible({"reply"}, original) is False
    assert _verb_is_admissible({"repost"}, original) is False
    # The un-rule is checked against the ORIGINAL baseline only, so an inverse
    # of an admitted verb does not inherit its admission.
    assert _verb_is_admissible({"uncomment"}, original) is False
    assert _verb_is_admissible({"unreact"}, original) is False
    # And it is a subset test, not an intersection test.
    assert _verb_is_admissible({"comment", "boost"}, original) is False




def test_that_loophole_check_would_catch_a_smuggled_verb():
    """The control, at the shape it is written to reject: a plausible-looking
    tool name whose verb the original list never sanctioned."""
    original_verbs: set[str] = set()
    for forbidden in _ORIGINAL_FORBIDDEN:
        original_verbs |= set(readonly.iter_write_verbs_in(forbidden))

    smuggled = "linkedin_boost_profile"
    assert set(readonly.iter_write_verbs_in(smuggled)) & original_verbs == set()


async def test_exactly_the_performable_writes_are_registered():
    """WHAT THIS TEST USED TO ASSERT: that the surface carried no write at all.

    It carried two, then three, and four from 2026-08-25. The literal pair
    became a literal triple on 2026-08-24 and then stopped being a literal at
    all, which is the real fix and is why the derived assertion below needed no
    edit when apply shipped: THE REGISTERED WRITES MUST EQUAL ``PERFORMABLE``,
    derived rather than listed. A tool registered for an action ``perform``
    will not execute is a button that cannot do anything, and an action
    ``perform`` WILL execute with no tool is a capability nobody can reach or
    audit. Both are failures and a hand-written list catches neither.

    The second half -- that nothing still on ``FORBIDDEN_TOOLS`` is registered
    -- is UNCHANGED and is the half that has always done the work. It is worth
    saying that it did not go green here by being loosened: apply left
    ``FORBIDDEN_TOOLS`` in ``test_server_surface.py``, visibly, under the
    conservation law, and this line is one of the things that forced that to
    happen in the open rather than by exception.
    """
    from linkedin_server.server import mcp

    names = {t.name for t in await mcp.list_tools()}
    performable_tools = {
        spec.tool_name
        for spec in SANCTIONED_WRITES.values()
        if spec.action in writes.PERFORMABLE
    }
    # WIDENED 2026-08-30, and the widening is a REFINEMENT of this rule rather
    # than a relaxation of it -- so the sentence it replaces is quoted. It read
    # ``names & set(SANCTIONED_WRITES) == performable_tools``, on the argument
    # that "a tool registered for an action perform will not execute is a
    # button that cannot do anything".
    #
    # THAT ARGUMENT WAS RIGHT ABOUT ITS HAZARD AND WRONG ABOUT ITS SCOPE, and
    # the difference is whether a grant can exist. A tool for an action that
    # COULD hold a grant and that perform then refuses is exactly the button
    # the old line describes: a token is minted, the operator confirms, and
    # nothing happens. A tool for an action with NO url_template cannot reach
    # that state at all -- writes.mint refuses it at issue, so no token is ever
    # printed and there is nothing to confirm. It is not a button; when called
    # it loads a page, counts what bears on the capability, and returns the
    # measurement with the reason it will not act.
    #
    # The other thing that changed is the alternative. When this line was
    # written, not registering meant the server said nothing, and saying
    # nothing was fine. It stopped being fine when the instructions ended up
    # asserting "there is no message, no connection request, no InMail, no
    # profile edit, and no post -- do not look for them or suggest they exist",
    # which conflates "this server will not" with "LinkedIn cannot".
    #
    # BOTH HALVES OF THE ORIGINAL GUARANTEE SURVIVE and are asserted below:
    # every performable action still has a tool, and no registered write tool
    # can act unless it is performable.
    assert performable_tools <= names & set(SANCTIONED_WRITES)
    for name in (names & set(SANCTIONED_WRITES)) - performable_tools:
        spec = SANCTIONED_WRITES[name]
        assert spec.action not in writes.PERFORMABLE, name
        # AN ADDRESS IS NOT A PERMISSION, and this assertion used to conflate
        # them: it required every non-performable spec to be UNADDRESSED. That
        # held while the two facts happened to coincide and stopped holding on
        # 2026-09-02, when update_profile_field was given its url under an
        # exact-url exemption while staying firmly outside PERFORMABLE.
        #
        # NARROWED RATHER THAN DROPPED. Every OTHER non-performable spec must
        # still be unaddressed -- that is the half of the guard that was always
        # about safety -- and the one exception is named, so a second one is a
        # visible edit here rather than a silent pass.
        if spec.action != "update_profile_field":
            assert spec.url_template is None, name
            assert spec.url_pattern is None, name
    assert names & FORBIDDEN_TOOLS == set()

    # The sanctioned actions that are NOT performable must be unreachable, and
    # they are named individually rather than as a set difference: each is here
    # for a different measured reason and a reader who sees only the arithmetic
    # learns none of them.
    #
    # THERE WERE THREE UNTIL 2026-08-25 and the third line read
    # ``assert "linkedin_apply_job" not in names``. Apply is performed now, so
    # that assertion inverts -- and it is kept as its inverse rather than
    # deleted, because "reachable" is the claim that now needs pinning: a
    # performable action with no registered tool is the failure the derived
    # assertion above catches only if somebody reads it.
    # FOLLOW INVERTED ON 2026-08-30 for the same reason apply did on 08-25,
    # and it is kept as its inverse rather than deleted. The line read
    # ``assert "linkedin_follow_company" not in names``.
    assert "linkedin_follow_company" in names
    assert "linkedin_set_open_to_work" not in names
    assert "linkedin_apply_job" in names
    # UPDATE_SETTING INVERTED ON 2026-08-31, for the same reason apply did on
    # 08-25 and follow on 08-30, and it is kept as its inverse rather than
    # deleted. It was in the grant-incapable list below and it is now the
    # sixth performable write.
    assert "linkedin_update_setting" in names
    assert "update_setting" in writes.PERFORMABLE
    # AND THE SEVEN THAT ARE REACHABLE AND CANNOT ACT. Being registered is not
    # the claim here -- being GRANT-INCAPABLE is. Each is asserted on the
    # property that makes it safe rather than on the fact that perform()
    # declines, because perform() declining is a runtime behaviour and this is
    # a structural one: with no url_template, mint() refuses at issue and no
    # confirm token for these exists anywhere in the process.
    # ``linkedin_react_to_item`` LEFT THIS TUPLE ON 2026-09-01, by SHIPPING.
    # It is removed rather than excepted, for the reason the loop below
    # states: every line here asserts its subject has NO write surface, and an
    # action that has one would need the assertion softened to pass. A check
    # softened to accommodate a shipped capability has stopped being a check.
    # Its departure is asserted positively by the derived test above -- the
    # registered writes must EQUAL PERFORMABLE -- so nothing goes unnoticed by
    # leaving here.
    #
    # linkedin_update_profile_field LEFT THIS LOOP ON 2026-09-02, and the
    # comment above is the reason it needs a sentence rather than a quiet
    # deletion. This is NOT a check softened to accommodate a shipped
    # capability -- nothing shipped. The action is still outside
    # PERFORMABLE and still refuses. What changed is that a RULING gave it
    # an address, and the loop was pinning "unperformable implies
    # unaddressed", which was true by coincidence rather than by design.
    # Three separate guards in this file encoded that same conflation and
    # all three had to be narrowed; that they agreed with each other is
    # not evidence they were right.
    #
    # ``linkedin_send_message`` LEFT THIS LOOP ON 2026-09-02 BY SHIPPING, and
    # it was the LAST MEMBER. It left the way react_to_item left and not the
    # way update_profile_field left: it became performable, so the assertion
    # "this tool cannot act" stopped being true of it rather than stopping
    # being the right question.
    #
    # SO THE TUPLE IS NOW DERIVED, AND THE EMPTY CASE IS ASSERTED. A
    # hand-typed tuple has gone stale here twice in two days; more to the
    # point, a ``for`` over an empty tuple runs no bodies, raises nothing and
    # reports nothing, so the version of this that simply deleted the last
    # name would leave a check that cannot fail sitting where a check used to
    # be. That is the same shape as a parametrized test over an empty sequence
    # -- three of those went silently dead in tests/test_writes_nine.py on
    # 2026-09-01 -- and it is worse here, because there is not even a grey
    # SKIPPED line to notice.
    #
    # WHAT THE DERIVATION IS. Exactly the set the loop forty lines above
    # already iterates: registered tool names that name a sanctioned action
    # ``perform`` will not execute. That loop asserts the same three
    # properties and needs no edit for a thirteenth action, so nothing is lost
    # by not re-typing names here. What is KEPT is the visibility: the
    # membership is asserted, so a registered-but-grant-incapable tool
    # arriving is a failing test that lands a reader on this comment rather
    # than a silent addition.
    #
    # AND IT IS ASSERTED EMPTY RATHER THAN NON-EMPTY, which inverts the usual
    # guard in this suite and is deliberate. Registering a tool that cannot
    # act is ALLOWED here and has been since the 2026-08-30 widening argued
    # for it -- such a tool is not a dead button, it loads a page, counts what
    # bears on the capability and returns the measurement with its reason. So
    # emptiness is a fact about today, not a rule; the assertion exists to
    # make the next departure from it visible, not to forbid one.
    grant_incapable = sorted(
        name
        for name in names & set(SANCTIONED_WRITES)
        if SANCTIONED_WRITES[name].action not in writes.PERFORMABLE
    )
    # NO LONGER EMPTY, 2026-11-24 (lane builds-26), and each entry says which
    # surface it reads and why it refuses, as the message below asks:
    #
    #   linkedin_set_tracker_stage  reads the Saved tab (/jobs-tracker/?stage=
    #       saved) through the reconciled reader save_job's gate uses, and
    #       refuses because the stage move -- an item in the row's 'Overflow
    #       menu' -- has never been captured: the one populated tracker
    #       capture draws that menu closed with an empty item slot.
    #   linkedin_endorse_skill / linkedin_withdraw_endorsement  read the
    #       profile he names through the named-profile door and count the
    #       endorse-shaped buttons; refuse because no capture holds the
    #       per-skill control in either state.
    #   linkedin_set_recent_job_searches_cleared  (lane build-jobs2, 2026-11-26,
    #       census J 19) reads the jobs home -- the card headed Recent job
    #       searches, its one Clear button, its searches, counted -- and
    #       refuses because what the press opens has never been captured.
    #   linkedin_set_resume_deleted and linkedin_set_resume_uploaded (lane
    #       build28, 2026-11-28, census P M3, P M1) read his application
    #       settings page -- the named card's closed trigger; the upload
    #       control, its rule and the file named against it -- and refuse
    #       because what the Delete item opens, and what the page does with a
    #       file, have never been captured.
    assert grant_incapable == [
        "linkedin_endorse_skill",
        "linkedin_set_recent_job_searches_cleared",
        "linkedin_set_resume_deleted",
        "linkedin_set_resume_uploaded",
        "linkedin_set_tracker_stage",
        "linkedin_withdraw_endorsement",
    ], (
        "these write tools are registered and cannot act: %s. That is "
        "permitted -- see the 2026-08-30 argument above -- but it is no "
        "longer true of nothing, so say here which surface each one reads "
        "and why it refuses, the way linkedin_send_message and "
        "linkedin_react_to_item were described before they shipped."
        % grant_incapable
    )
    for tool in grant_incapable:
        assert tool in names, tool
        assert SANCTIONED_WRITES[tool].url_template is None, tool
        assert SANCTIONED_WRITES[tool].action not in writes.PERFORMABLE, tool


# ---------------------------------------------------------------------------
# 7. The check that will police the click when it arrives
# ---------------------------------------------------------------------------


def _mutating_calls_outside_granted_functions(source: str) -> list[str]:
    """Every mutating call in ``source`` NOT inside a function taking a grant.

    This is the confinement rule, written now and driven at synthetic code,
    so that the day ``perform`` gains a body the rule is already load-bearing
    rather than something somebody remembers to add.
    """
    tree = ast.parse(source)
    offences: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = {a.arg for a in node.args.args + node.args.kwonlyargs}
        takes_grant = "grant" in args
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            func = inner.func
            if not isinstance(func, ast.Attribute):
                continue
            if readonly.scan_source_for_mutations(f"x.{func.attr}()"):
                if not takes_grant:
                    offences.append(f"{node.name} calls .{func.attr}() without a grant")
    return offences


def test_the_confinement_rule_accepts_a_granted_write():
    granted = (
        "async def perform(page, grant):\n"
        "    await page.click('button')\n"
    )
    assert _mutating_calls_outside_granted_functions(granted) == []


def test_the_confinement_rule_rejects_an_ungranted_write():
    """The one that matters: a click that nobody confirmed."""
    ungranted = (
        "async def helper(page):\n"
        "    await page.click('button')\n"
    )
    offences = _mutating_calls_outside_granted_functions(ungranted)
    assert offences and "without a grant" in offences[0]


def test_the_write_module_passes_its_own_confinement_rule():
    source = Path(writes.__file__).read_text(encoding="utf-8")
    assert _mutating_calls_outside_granted_functions(source) == []


# ---------------------------------------------------------------------------
# 8. The permanent refusals say why
# ---------------------------------------------------------------------------


def test_every_permanent_refusal_carries_its_reason():
    """An omission that does not explain itself reads as an oversight, and the
    next agent 'fixes' it.

    PINNED BY NAME SINCE 2026-09-24, NOT BY A FLOOR. This said ``>= 8`` and
    the dict held nine; OUTWARD-CLASSES-BUILT-BEHIND-GRANTS then retired three
    (repost or share, endorse or recommend, delete or withdraw), leaving the
    six whose grounds are themselves mitigations. A floor would have gone red
    for the right change and stayed green for a wrong one -- any six names
    pass ``>= 6`` -- so the set is asserted against the ruling's own list in
    ``outward_classes``, and the three retired names are asserted gone.
    """
    from linkedin_server import outward_classes

    assert sorted(PERMANENTLY_FORBIDDEN) == sorted(
        outward_classes.SURVIVING_PERMANENT_REFUSALS
    )
    for retired in outward_classes.RETIRED_PERMANENT_REFUSALS:
        assert retired not in PERMANENTLY_FORBIDDEN, retired
    for name, reason in PERMANENTLY_FORBIDDEN.items():
        assert len(reason) > 40, name


@pytest.mark.parametrize(
    "cut", ["apply", "connect", "send_inmail", "post", "endorse", "mark_read"]
)
def test_these_exact_action_spellings_reach_nothing(writes_on, cut):
    """RENAMED 2026-08-30, because the name asserted a history that has ended.

    It read ``test_the_cut_actions_are_not_reachable_by_any_route`` over a
    docstring saying "apply, connect and InMail were cut by the operator on
    2026-08-23. This is that decision made structural rather than remembered."
    Every clause of that is now false: apply is performed, and an invitation
    and a message are sanctioned specs behind the gate.

    WHAT THE TEST STILL DOES, unchanged and worth keeping, is narrower than
    what its name claimed. These are SPELLINGS, and none of them is the name of
    anything: the capabilities that arrived are ``send_invitation``,
    ``send_message``, ``publish_post`` and ``apply_job``. So this asserts that
    a bare, unqualified action string reaches no spec and mints no grant --
    which stops a caller reaching a capability by guessing a short name, and
    stops a future spec being registered under one.

    ``endorse`` is the only member that still means what the old name meant.
    """
    assert cut not in {s.action for s in SANCTIONED_WRITES.values()}
    with pytest.raises(WriteAttemptError):
        mint(cut, JOB, receipt="anything")
    with pytest.raises(WriteAttemptError):
        spec_for_action(cut)


def test_the_anchors_the_future_click_will_use_are_frozen_at_both_renders():
    """The click does not exist, but its anchor is already pinned.

    Both are anchored on the ACCESSIBLE NAME, which is present in both frozen
    renders -- unlike ``data-view-name`` (absent pre-hydration) and unlike a
    class (a build hash). Freezing this now means the day the body is written,
    the selector is not a guess.
    """
    fixtures = Path(__file__).parent / "fixtures"
    for name in ("job_detail.html", "job_detail_hydrated.html"):
        html = (fixtures / name).read_text(encoding="ascii")
        assert 'aria-label="Save the job"' in html, name
        assert 'aria-label="Follow"' in html, name
        # And the anchor that must NOT be relied on, proving the asymmetry.
        if name == "job_detail.html":
            assert 'data-view-name="job-save-button"' not in html


def test_the_instrumentation_that_must_not_be_relied_on_did_in_fact_vanish():
    """The ban on ``data-view-name`` was a rule; on 2026-08-23 it became a
    measurement.

    ``job_detail_hydrated.html`` was captured on 2026-08-22 carrying fifteen
    ``data-view-name`` attributes. A posting loaded live the NEXT DAY carried
    ZERO -- and the fixtures frozen from that capture carry zero, which is what
    this asserts. Same surface, same account, one day, the whole instrumenting
    layer gone. A reader anchored there would have returned nothing that
    morning with every test still green.

    It is surface-specific rather than a platform-wide removal: Manage Pages,
    loaded minutes later, carried thirty-one. That is the honest form of the
    claim and it is why the fixtures are asserted rather than LinkedIn's
    behaviour.
    """
    fixtures = Path(__file__).parent / "fixtures"
    yesterday = (fixtures / "job_detail_hydrated.html").read_text(encoding="ascii")
    today = (fixtures / "job_detail_following_hydrated.html").read_text(
        encoding="ascii"
    )
    assert yesterday.count("data-view-name") > 0
    assert today.count("data-view-name") == 0
    # The accessible names survived the change in both. That is the point.
    assert 'aria-label="Save the job"' in yesterday
    assert 'aria-label="Save the job"' in today


def test_the_toggle_problem_is_solved_and_the_solution_is_recorded():
    """WHAT THIS TEST USED TO SAY, and why it now says the opposite.

    It used to pin a blocker: both anchors are TOGGLES, the captures only ever
    showed the OFF state, so nothing could tell Save from Unsave, and a gate
    that cannot say which way it moves a toggle is not a gate. All true. The
    inference drawn from it was wrong -- that the write had to come first.

    Measuring a toggle's ON state is a READ. It cost one page load on a posting
    from a company he already follows. So the module now records the measured
    labels rather than the blocker, and the direction rule is enforced in
    ``_direction`` rather than described in prose.

    THE LAST UNMEASURED HALF CLOSED ON 2026-08-30, and it closed the OTHER way
    -- which is why this docstring now argues with itself and should. The SAVE
    control's ON state could not be reached by a read: there was no saved
    posting on the account to read it off, so no page load anybody had failed
    to perform would have produced it. It took the write. That is the one case
    where "measuring a toggle's ON state is a READ" did not hold, and the
    record says so rather than smoothing it.

    AND ONE READING FROM THE WRITE PATH WAS NOT ENOUGH TO ACT ON. A label
    reached by performing its own inverse can only be re-measured by performing
    it again, so the row waited for a read-only route and three further
    agreeing observations. The record now carries that as its general lesson,
    which is what this test's last assertion pins.

    WHERE IT MOVED TO. This used to read ``writes.perform.__doc__``. That
    docstring described a function that refused; the function now acts, and its
    docstring describes what it does. The record was moved to a module constant
    rather than deleted, because the reasoning is the deliverable -- and a
    history kept inside the docstring of the thing it is the history OF is a
    history that gets edited away the next time the thing changes.

    SHOWN FAILING by restoring the retired sentence to the record::

        AssertionError: 'has NOT been observed' is still in the record, which
        now carries the measured ON label two paragraphs above it
    """
    doc = writes.TOGGLE_MEASUREMENT_RECORD
    assert "IS SOLVED" in doc
    assert 'aria-label="Following"' in doc
    assert "linkedin_saved_jobs" in doc
    # The half this used to guard as OPEN is now measured, and the record must
    # carry the measurement rather than the old blocker.
    assert 'aria-label="Unsave the job"' in doc
    assert "has NOT been observed" not in doc, (
        "the record has been reverted to the pre-2026-08-30 claim; the ON "
        "label is measured and the table carries it"
    )
    # AND THE LESSON, not just the label. The expensive half of this episode
    # was not measuring the label once -- it was needing a way to measure it
    # AGAIN without a second irreversible act.
    assert "irreversible act" in doc

    # The measured pairs are what the reader actually uses, so assert THOSE
    # rather than the docstring alone -- a docstring cannot be wrong in a way
    # a caller notices.
    assert shape.FOLLOW_LABELS == {
        "Follow": "not_following",
        "Following": "following",
    }
    # Two entries since 2026-08-30, and the SECOND one is what lets unsave
    # resolve an anchor at all.
    assert shape.SAVE_LABELS == {
        "Save the job": "not_saved",
        "Unsave the job": "saved",
    }
# ---------------------------------------------------------------------------
# Addressing is not permission -- the 2026-09-02 url ruling and its control
# ---------------------------------------------------------------------------


def test_the_profile_editor_shipped_and_membership_is_still_the_gate():
    """THIS TEST FIRED, WHICH IS WHAT IT WAS BUILT TO DO.

    It was ``test_addressing_the_profile_editor_did_not_make_it_performable``,
    written on 2026-09-02 when the editor was given a url while the action
    stayed refused. Its whole purpose was stated at the time: **the day
    somebody flips that frozenset, a red test names what they just turned on.**
    That day was the same day. The operator ruled "I want all capabilities",
    ``update_profile_field`` entered ``PERFORMABLE``, and this went red naming
    it.

    So it is rewritten to the new truth rather than deleted -- a control that
    fires and is then removed taught nothing.

    WHAT IT ASSERTS NOW is that the ordering it proved has not changed:
    membership is STILL the gate, and the address is still not one. The action
    is performable today because somebody added it to a frozenset, not because
    it acquired a url -- and the constructed case below is what keeps that
    distinction observable now that the registry no longer contains a
    naturally-occurring one.
    """
    import dataclasses

    spec = writes.spec_for_action("update_profile_field")

    # IT SHIPPED. Addressed, performable, and it does not raise.
    assert spec.url_template == "https://www.linkedin.com/in/me/edit/intro/"
    assert spec.exempt_substring == "/edit/"
    assert spec.action in writes.PERFORMABLE
    writes._refuse_unperformable(spec)  # must NOT raise

    # AND MEMBERSHIP IS STILL WHAT DECIDES. Take the same spec, keep the
    # address, remove it from the set: it refuses again. The url did nothing.
    original = writes.PERFORMABLE
    try:
        writes.PERFORMABLE = frozenset(original - {"update_profile_field"})
        with pytest.raises(WriteAttemptError) as caught:
            writes._refuse_unperformable(spec)
        assert "update_profile_field" in str(caught.value)
    finally:
        writes.PERFORMABLE = original

    # Restored, or every later test in this file runs against a lie.
    assert "update_profile_field" in writes.PERFORMABLE
    writes._refuse_unperformable(spec)

    # AND THE GRANT DOOR AGREES, on a constructed pair rather than on the
    # registry -- which stopped containing an addressed-but-unperformable
    # action the moment this one shipped.
    addressed_only = dataclasses.replace(spec, action="not_a_sanctioned_action")
    assert addressed_only.url_template is not None
    assert writes.grant_is_possible(addressed_only) is False
    assert writes.grant_is_possible(spec) is True


def test_the_editor_exemption_is_an_exact_url_and_not_a_family():
    """NARROWNESS, asserted in both directions the ruling named.

    ``/edit/`` stays on ``_FORBIDDEN_URL_SUBSTRINGS`` and is NOT relaxed. What
    passes is one exact url, by equality. A loose exemption is how a real write
    hides, and the two cases below are the ones that would hide in it.
    """
    spec = writes.spec_for_action("update_profile_field")
    exact = "https://www.linkedin.com/in/me/edit/intro/"

    assert spec.url_pattern.match(exact)

    # A DIFFERENT MEMBER OF THE SAME FAMILY. Still refused -- the exemption is
    # not "anything under /edit/".
    for sibling in (
        "https://www.linkedin.com/in/me/edit/forms/summary/new/",
        "https://www.linkedin.com/in/me/edit/contact-info/",
        "https://www.linkedin.com/in/someone-else/edit/intro/",
    ):
        assert not spec.url_pattern.match(sibling), sibling

    # A URL THAT MERELY BEGINS WITH THE EXACT ONE -- the traversal shape the
    # exemption table's own docstring names.
    assert not spec.url_pattern.match(exact + "../../evil")

    # AND THE SLASHLESS SPELLING, which is refused ON PURPOSE: the exemption is
    # deliberately NARROWER than the address, the conservative direction, and
    # the same choice already made for the reads.
    assert not spec.url_pattern.match(
        "https://www.linkedin.com/in/me/edit/intro"
    )

    # /edit/ IS STILL FORBIDDEN GLOBALLY. The exemption buys past one gate for
    # one url; it does not soften the tuple.
    assert "/edit/" in readonly._FORBIDDEN_URL_SUBSTRINGS


def test_send_message_is_retired_and_its_name_is_forbidden_again():
    """THE RETIREMENT, PINNED (2026-09-27, lane L5, the orchestrator's order of
    23:36; PEOPLE-DATA-MITIGATIONS, mitigation 6).

    ``send_message`` was aimed by a NAME typed into the composer's recipient
    typeahead -- measured to commit nobody, and never sent. It was RETIRED
    rather than re-aimed: the composer addressed by member id is on the read
    boundary, but it takes no link and whom it addressed could only be read
    off a committed recipient no instrument here has ever observed, while
    ``message_from_profile`` already reaches a person by profile link. This
    test held its not-sent verdict until then (``..._can_report_not_sent_
    from_the_composer``); what it holds now is that the action is GONE from
    every place that could act on it, and that its tool's NAME went back onto
    the forbidden list -- the only route off ``SANCTIONED_WRITES`` that
    ``test_no_boundary_can_be_deleted_only_moved`` accepts.
    """
    from linkedin_server import server as server_module

    actions = {spec.action for spec in SANCTIONED_WRITES.values()}
    assert "send_message" not in actions
    assert "linkedin_send_message" not in SANCTIONED_WRITES
    assert "send_message" not in writes.PERFORMABLE
    assert "send_message" not in writes.TYPING_ACTIONS
    assert not hasattr(server_module, "linkedin_send_message")
    assert "linkedin_send_message" in FORBIDDEN_TOOLS
    # The way a person IS messaged now, by a link, never a name.
    assert "message_from_profile" in writes.PERFORMABLE
    assert spec_for_action("message_from_profile").target_kind == "profile_and_text"
