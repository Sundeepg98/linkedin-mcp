"""The write boundary's confirm gate: the block a human reads, built from a
read the gate performed itself.

SPLIT OUT OF ``tests/test_writes.py`` ON 2026-11-27 (lane ci8). That file took
about 137 s alone, over the two-minute cap on a local gate, so it was split
by concern into six files, each well under it. This one holds its
section 5 (the gate a human reads), moved
verbatim, with their banners and their prose. The fixtures, the navigator,
the frozen captures and the helpers stay in ``tests/test_writes.py``, which
69 test files already import them from; its module docstring is the account
of the whole write boundary these files test, and it still applies here.
"""

from __future__ import annotations

import re

import pytest

from linkedin_server import writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    SANCTIONED_WRITES,
    preview,
    spec_for_action,
)
from tests.test_writes import (  # noqa: F401 -- fixtures are used by injection
    _no_grants_survive_a_test,
    browser_page,
    writes_on,
    FOLLOWED_COMPANY,
    JOB,
    SAVED_JOB,
    SAVED_LIST_OF_ONE,
    _gate,
    markup,
)


# ---------------------------------------------------------------------------
# 5. The gate a human reads -- built from a read the gate performed itself
# ---------------------------------------------------------------------------

#: The verdict each action carries, PINNED PER ACTION. It used to be asserted
#: as ``in {"REVERSIBLE", "IRREVERSIBLE", "STILL-UNKNOWN"}`` -- the set of all
#: values that exist, one of which is the dataclass default -- so a cold review
#: flipped all four specs to IRREVERSIBLE and the whole suite stayed green
#: while the gate printed IRREVERSIBLE beside "reversible by unsaving the same
#: posting". A check that cannot distinguish a verdict from its opposite is
#: not checking the verdict.
#: The sanctioned actions whose reversibility is NOT measured. Named here once
#: and used by both the coverage assertion above and the tables below, so the
#: two cannot disagree about which half of the split an action is in.
#:
#: SEVEN ARRIVED ON 2026-08-30 AND EVERY ONE OF THEM IS UNMEASURED, which is
#: the honest shape rather than a gap to be tidied. Each would act on a surface
#: this server has never opened, so nothing about undoing any of them has been
#: observed -- and the most tempting of the seven to call reversible is
#: react_to_item, where LinkedIn writes the state into the control's own name.
#: A control whose name reports a state is almost certainly a toggle; almost
#: certainly is not a measurement, and the ON-state label has never been seen.
_UNMEASURED_REVERSIBILITY = {
    "apply_job",
    "publish_post",
    "comment_on_item",
    "react_to_item",
    "update_profile_field",
    "update_setting",
    "send_invitation",
    # (send_message, retired 2026-09-27.)
    # 2026-09-24 (census row P I14). Its removal is P I15, which presses an
    # ON-state control no capture holds, so nothing about undoing it has been
    # observed on this surface.
    "mark_company_interest",
    # 2026-10-10 (lane B4). The alert pair: each is the other's inverse and
    # both are BUILT, but the On shape has never been captured, so whether the
    # switch returns to the state it left is unmeasured.
    "set_similar_jobs_alert",
    "unset_similar_jobs_alert",
    # 2026-11-25 (lane build-jmn26). The search-alert pair, the same way:
    # both BUILT, the on shape never captured.
    "set_search_job_alert",
    "unset_search_job_alert",
    # 2026-11-26 (lane build-jobs2, J 163). No answer has been sent or
    # watched; nothing that withdraws one is drawn.
    "send_recommendations_feedback",
    # 2026-11-26 (lane build-msg2). The conversation-menu acts: mute and
    # unmute are BUILT and the muted menu never captured; the unread mark's
    # way back (opening it) is believed, not measured; archive's restore is
    # not built; delete has no inverse at all.
    "set_conversation_muted",
    "unset_conversation_muted",
    "mark_conversation_unread",
    "set_conversation_archived",
    "set_conversation_deleted",
    # 2026-11-26 (lane build-msg2, census M C64). Whether a group post can be
    # deleted has never been observed; no delete is built.
    "publish_group_post",
    # 2026-09-24. Whether LinkedIn lets a sent reply be recalled has never
    # been observed. This comment used to add "and recalling one is
    # destruction this server may not perform at any confirm level either
    # way"; that refusal was retired the same day (OUTWARD-CLASSES-BUILT-
    # BEHIND-GRANTS) and restated at lane L8's merge of master: no delete is
    # built, and a delivered reply is not recalled from an inbox either way.
    "send_reply",
    # 2026-10-10 (lane U). Whether LinkedIn lets a sent attachment be
    # recalled has never been observed; no delete is built, and a file the
    # person downloaded is not recalled by anything.
    "send_attachment",
    # 2026-09-27 (census rows M C63 / N 64). No rejoin has ever been observed
    # and nothing here joins a group; its spec treats it as irreversible.
    "withdraw_from_group",
    # 2026-11-26 (lane build-net2). What each invitation answer's press draws
    # has never been captured; no undo of an accept, an ignore or a withdraw
    # is built, and LinkedIn bars a new invitation for weeks after a withdraw.
    "accept_invitation_to_connect",
    "ignore_invitation_to_connect",
    "withdraw_invitation",
    # 2026-11-26 (lane build-net2, N 154). The undo LinkedIn draws after Not
    # interested has never been captured.
    "mark_not_interested",
    # 2026-11-27 (lane msg7, M C36). What a save draws, and the Unsave a saved
    # item's menu is expected to draw, have never been captured.
    "save_post",
    # 2026-09-27 (lane L5's follow-up). What a pressed Connect becomes on a
    # profile has never been captured, so neither has a withdraw control; and
    # whether a message sent from a profile can be recalled has never been
    # observed here. Neither undo is built: an invitation's withdraw is
    # outward_classes' withdraw_invitation, BLOCKED, and no message delete
    # exists. This comment used to end "Both undo routes are destruction,
    # forbidden here at any confirm level"; that refusal was retired
    # 2026-09-24 (OUTWARD-CLASSES-BUILT-BEHIND-GRANTS) and restated at lane
    # L5's merge of master 52b55b6.
    "connect_from_profile",
    "message_from_profile",
    # 2026-10-10 (lane S, settings). Its inverse is itself with the value the
    # preview read, and no round trip has been performed live yet: the live
    # proof is planned in _audit/2026-09-28-lane-s-settings.md, section 6.
    "set_admitted_setting",
    # 2026-10-10 (lane NP). Whether pressing a measured ON name gives the
    # reaction back has never been observed: the live proof reads it.
    "withdraw_reaction",
    # 2026-11-24 (lane builds-26). No stage move has ever been made or seen,
    # and no endorsement given or withdrawn has ever been seen.
    "set_tracker_stage",
    "endorse_skill",
    "withdraw_endorsement",
    # 2026-11-26 (lane build-jobs2, J 19). No clear has been made or watched.
    "set_recent_job_searches_cleared",
}

REVERSIBILITY_CLASS = {
    "save_job": "REVERSIBLE",
    "unsave_job": "REVERSIBLE",
    "follow_company": "REVERSIBLE",
    "unfollow_company": "REVERSIBLE",
    "publish_post": "STILL-UNKNOWN",
    "comment_on_item": "STILL-UNKNOWN",
    "react_to_item": "STILL-UNKNOWN",
    "update_profile_field": "STILL-UNKNOWN",
    "update_setting": "STILL-UNKNOWN",
    "send_invitation": "STILL-UNKNOWN",
    "send_reply": "STILL-UNKNOWN",
    "send_attachment": "STILL-UNKNOWN",
    # THE ONE THAT IS NOT, and it is the whole reason this table is per-action
    # rather than a claim about the set. apply_job is STILL-UNKNOWN because the
    # surface that would settle it -- his applied list -- is empty, so there is
    # nothing there to look for a withdraw control on. It carries
    # irreversible=True regardless, on the separate and certain ground that
    # LinkedIn offers no withdraw of a submitted application (Help Center
    # a512388). That ground read "withdrawing is permanently forbidden here in
    # either direction" until 2026-09-24, when OUTWARD-CLASSES-BUILT-BEHIND-
    # GRANTS retired the refusal; the verdict did not move, its reason did.
    "apply_job": "STILL-UNKNOWN",
    "set_open_to_work": "REVERSIBLE",
    # 2026-09-23. REVERSIBLE on the same measurement as unfollow_company --
    # every followed Page carries its own unfollow control on Manage Pages --
    # and the undo is keyed by the same numeric id this action is granted on.
    "follow_company_page": "REVERSIBLE",
    # 2026-09-24. STILL-UNKNOWN: LinkedIn's Help describes removing an
    # interest, but the control that would do it has never been captured.
    "mark_company_interest": "STILL-UNKNOWN",
    # 2026-10-10 (lane B4). STILL-UNKNOWN, both: see _UNMEASURED_REVERSIBILITY.
    "set_similar_jobs_alert": "STILL-UNKNOWN",
    "unset_similar_jobs_alert": "STILL-UNKNOWN",
    # 2026-11-25 (lane build-jmn26). STILL-UNKNOWN, both: see _UNMEASURED_REVERSIBILITY.
    "set_search_job_alert": "STILL-UNKNOWN",
    "unset_search_job_alert": "STILL-UNKNOWN",
    # 2026-11-26 (lane build-jobs2). See _UNMEASURED_REVERSIBILITY.
    "send_recommendations_feedback": "STILL-UNKNOWN",
    # 2026-11-26 (lane build-msg2). STILL-UNKNOWN, all five: see
    # _UNMEASURED_REVERSIBILITY.
    "set_conversation_muted": "STILL-UNKNOWN",
    "unset_conversation_muted": "STILL-UNKNOWN",
    "mark_conversation_unread": "STILL-UNKNOWN",
    "set_conversation_archived": "STILL-UNKNOWN",
    "set_conversation_deleted": "STILL-UNKNOWN",
    # 2026-11-26 (lane build-msg2). STILL-UNKNOWN: see _UNMEASURED_REVERSIBILITY.
    "publish_group_post": "STILL-UNKNOWN",
    # 2026-09-27. STILL-UNKNOWN whether a group left can be rejoined; it
    # carries irreversible=True regardless, because no join is built here and
    # an approval-gated group needs a manager to let him back in.
    "withdraw_from_group": "STILL-UNKNOWN",
    # 2026-11-26 (lane build-net2). STILL-UNKNOWN, all three: see
    # _UNMEASURED_REVERSIBILITY.
    "accept_invitation_to_connect": "STILL-UNKNOWN",
    "ignore_invitation_to_connect": "STILL-UNKNOWN",
    "withdraw_invitation": "STILL-UNKNOWN",
    "mark_not_interested": "STILL-UNKNOWN",
    "save_post": "STILL-UNKNOWN",
    # 2026-09-27 (lane L5's follow-up). STILL-UNKNOWN, both: see
    # _UNMEASURED_REVERSIBILITY.
    "connect_from_profile": "STILL-UNKNOWN",
    "message_from_profile": "STILL-UNKNOWN",
    # 2026-10-10 (lane S, settings). STILL-UNKNOWN until its live proof: see
    # _UNMEASURED_REVERSIBILITY.
    "set_admitted_setting": "STILL-UNKNOWN",
    # 2026-10-10 (lane NP): see _UNMEASURED_REVERSIBILITY.
    "withdraw_reaction": "STILL-UNKNOWN",
    # 2026-11-24 (lane builds-26): see _UNMEASURED_REVERSIBILITY.
    "set_tracker_stage": "STILL-UNKNOWN",
    "endorse_skill": "STILL-UNKNOWN",
    "withdraw_endorsement": "STILL-UNKNOWN",
    # 2026-11-26 (lane build-jobs2): see _UNMEASURED_REVERSIBILITY.
    "set_recent_job_searches_cleared": "STILL-UNKNOWN",
}

#: Which actions have had their reversibility MEASURED. Split out from the
#: class table because the two say different things and one spec now
#: distinguishes them: a class of STILL-UNKNOWN with measured=False is the
#: honest pairing, and a class of STILL-UNKNOWN with measured=True would be a
#: contradiction the renderer refuses.
REVERSIBILITY_MEASURED = {
    "save_job": True,
    "unsave_job": True,
    "follow_company": True,
    "unfollow_company": True,
    "apply_job": False,
    "set_open_to_work": True,
    "publish_post": False,
    "comment_on_item": False,
    "react_to_item": False,
    "update_profile_field": False,
    "update_setting": False,
    "send_invitation": False,
    "follow_company_page": True,
    "mark_company_interest": False,
    "set_similar_jobs_alert": False,
    "unset_similar_jobs_alert": False,
    "set_search_job_alert": False,
    "unset_search_job_alert": False,
    "send_recommendations_feedback": False,
    "set_conversation_muted": False,
    "unset_conversation_muted": False,
    "mark_conversation_unread": False,
    "set_conversation_archived": False,
    "set_conversation_deleted": False,
    "publish_group_post": False,
    "send_reply": False,
    "send_attachment": False,
    "withdraw_from_group": False,
    "accept_invitation_to_connect": False,
    "ignore_invitation_to_connect": False,
    "withdraw_invitation": False,
    "mark_not_interested": False,
    "save_post": False,
    "connect_from_profile": False,
    "message_from_profile": False,
    "set_admitted_setting": False,
    "withdraw_reaction": False,
    "set_tracker_stage": False,
    "endorse_skill": False,
    "withdraw_endorsement": False,
    "set_recent_job_searches_cleared": False,
}

def test_the_two_reversibility_tables_agree_with_each_other():
    """A THIRD TABLE WOULD DRIFT, so the two that exist are reconciled here.

    ``REVERSIBILITY_MEASURED`` and ``_UNMEASURED_REVERSIBILITY`` are the same
    fact written twice, in opposite polarity, for two different callers. The
    renderer refuses to print a measured class over an unmeasured claim; this
    refuses to let the TEST FILE hold the contradiction the renderer would
    catch at runtime.
    """
    unmeasured = {a for a, m in REVERSIBILITY_MEASURED.items() if not m}
    assert unmeasured == _UNMEASURED_REVERSIBILITY


async def test_the_gate_names_the_target_in_words_a_person_can_check(
    writes_on,
    browser_page,
):
    block, _nav = await _gate(browser_page, "save_job")
    assert block["performed"] is False
    assert block["where"]["job_id"] == JOB
    assert block["to_confirm"] in writes._GRANTS
    assert "NOTHING has been done" in block["what_happens_next"]
    # The title and employer came OFF THE PAGE. Asserted by finding them in
    # the frozen markup rather than by typing the invented company name into
    # this file, which is the convention the fixture suites already keep.
    posting = markup("job_detail")
    assert block["where"]["title"] and block["where"]["company"]
    assert block["where"]["company"] in posting


async def test_the_facts_track_the_page_and_not_the_request(writes_on, browser_page):
    """THE CONTROL for the assertion above, and the one that would have caught
    the old defect on its own: two identical requests over two different
    postings must not produce the same block."""
    one, _ = await _gate(browser_page, "save_job", posting="job_detail")
    two, _ = await _gate(browser_page, "save_job", posting="job_detail_following_hydrated")
    assert one["where"]["company"] != two["where"]["company"]
    assert one["where"]["title"] != two["where"]["title"]


async def test_the_gate_refuses_when_the_posting_did_not_render(
    writes_on,
    browser_page,
):
    """An id is not something a human can check, so a gate that could not read
    the posting names nothing he can verify and refuses.

    ``job_detail_following.html`` is the honest shape of this: a real capture,
    taken before the page settled, carrying LinkedIn's server-rendered document
    title and no posting behind it.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job", posting="job_detail_following")
    assert "no posting could be read from it" in str(excinfo.value)


async def test_the_gate_prints_every_measured_verdict_with_its_evidence(
    writes_on,
    browser_page,
):
    """THE RULE, ratified 2026-08-23, and what happened to it.

    When it landed, all four specs printed UNMEASURED, and the rule was
    described as "biting its own author". The measurement was then performed --
    entirely through READS -- so all four now print a verdict. That is the rule
    being satisfied, not relaxed, and this test is the half that says so: a
    verdict must arrive with its EVIDENCE, its OWNER and its RESIDUE, because a
    bare "reversible" is the confident string the rule exists to stop whether
    or not somebody has since done the measuring.
    """
    cases = {
        "save_job": {},
        "unsave_job": {"target": SAVED_JOB, "saved": SAVED_LIST_OF_ONE},
        "follow_company": {},
        "unfollow_company": {"target": FOLLOWED_COMPANY},
        "set_open_to_work": {
            "target": "self",
            "to_state": "All LinkedIn members",
        },
        # 2026-09-23. Measured REVERSIBLE on the unfollow's own evidence; its
        # surface is the organisation Page root, which ``_gate`` does not
        # freeze, so the loop below serves it from the action's own module.
        "follow_company_page": {},
    }
    # THE UNMEASURED ACTIONS ARE DELIBERATELY NOT HERE: their reversibility is
    # unmeasured, so they belong to the sibling test below rather than being
    # quietly dropped out of the coverage assertion. It was one name until
    # 2026-08-30 (apply_job) and is eight since, and the eight are LISTED
    # rather than derived from the specs -- a derived set would be satisfied by
    # somebody flipping a spec to unmeasured, which is the move this coverage
    # assertion exists to make visible.
    assert set(cases) | _UNMEASURED_REVERSIBILITY == {
        spec.action for spec in SANCTIONED_WRITES.values()
    }

    for action, kwargs in cases.items():
        spec = spec_for_action(action)
        if action == "follow_company_page":
            # THE PAGE ROOT, served by the navigator and the synthetic fixture
            # that live with the action's own tests -- imported here, never
            # rebuilt, so this loop reads the same world those tests assert on.
            # Imported inside the function because that module imports this
            # one at its top.
            from tests import test_follow_company_page as page_root

            block = await preview(
                spec,
                target=page_root.COMPANY_PAGE_FOLLOW_ID,
                navigator=page_root._navigator(
                    page_root.COMPANY_PAGE_FOLLOW_MARKUP,
                    page_root.COMPANY_PAGE_FOLLOW_ID,
                ),
                page=browser_page,
            )
        else:
            block, _nav = await _gate(browser_page, action, **kwargs)
        assert spec.reversibility_measured is True, action
        assert block["reversibility_measured"] is True
        assert "UNMEASURED" not in block["reversibility"]
        assert block["reversibility_class"] == REVERSIBILITY_CLASS[action], action
        # A verdict with no evidence line is the thing this rule forbids. The
        # DATE is matched as a shape rather than as a literal: pinning one
        # day's date meant the next measurement had to either lie about when it
        # was taken or fail a test about evidence, which is the wrong pressure
        # to put on the field that records when something was measured.
        assert re.search(
            r"MEASURED 20\d\d-\d\d-\d\d", block["reversibility_evidence"]
        ), (action, block["reversibility_evidence"][:120])
        assert len(block["reversible_by"]) > 40, action
        assert len(block["what_it_cannot_undo"]) > 40, action


async def test_an_unmeasured_verdict_prints_as_unmeasured_and_names_its_fix(
    writes_on,
    browser_page,
):
    """THE OTHER HALF OF THE RULE, and until 2026-08-24 nothing exercised it.

    The rule is not "print a verdict"; it is "do not print a verdict you have
    not measured". Every spec carried a measured one, so the branch that
    renders ``UNMEASURED`` was live code with no live spec behind it -- it
    could have been deleted and the suite would have stayed green.
    ``apply_job`` is now the spec that goes down it, which is fitting: the
    action with the largest consequence is the one whose reversibility nobody
    has established.

    What the block must do is say so LOUDLY and then name what would settle it,
    because a caveat that does not name its own fix reads as an apology.

    THE TAIL OF THIS TEST INVERTED ON 2026-08-25 AND GOT SHARPER FOR IT. It
    used to close with "No surface, so no grant. The warning is not an offer",
    asserting ``to_confirm is None`` and ``"NO CONFIRM TOKEN IS ISSUED"`` in
    the block -- true while apply had no ``url_template``. Apply has one now
    (the posting page), so the warning IS an offer, and the situation this
    test covers is strictly more dangerous than the one it was written for: an
    UNMEASURED reversibility verdict on an IRREVERSIBLE action that a caller
    can actually confirm. The loud half is therefore unchanged and the quiet
    half is asserted the other way round -- a token IS issued, and it is issued
    behind, not instead of, the warning.

    The surface-less branch did not lose its coverage when apply left it:
    ``set_open_to_work`` still renders it and
    ``test_open_to_work_has_no_measured_surface_and_issues_no_token`` still
    pins every string this test used to.
    """
    spec = spec_for_action("apply_job")
    assert spec.reversibility_measured is False
    block, _nav = await _gate(browser_page, "apply_job")

    assert block["reversibility_measured"] is False
    assert "UNMEASURED" in block["reversibility"]
    assert block["reversibility_class"] == "STILL-UNKNOWN"
    # It names its own fix, in the rendered block rather than only in source.
    assert "What would settle it" in block["reversibility"]
    assert len(block["reversibility"]) > 200

    # And the separate, CERTAIN half is not softened by the uncertain one: this
    # server can never undo an application whatever LinkedIn permits.
    assert block["irreversible"] is True
    assert "NOBODY" in block["reversible_by"]

    # A SURFACE, SO A GRANT -- and the grant is real, checked in the registry
    # rather than believed from a string that looks like a token.
    assert spec.url_template is not None
    token = block["to_confirm"]
    assert token and token in writes._GRANTS
    # It is still a PREVIEW: nothing has been submitted by getting this far.
    assert block["performed"] is False

    nxt = block["what_happens_next"]
    # THE REFUSAL BRANCH MUST NOT BE THE ONE THAT RAN. Asserted as an absence
    # because the dangerous regression here is silent: if apply ever fell back
    # to the surface-less path it would print a reassuring refusal while the
    # tool that calls it goes on believing it can apply.
    assert "NO CONFIRM TOKEN IS ISSUED" not in nxt
    assert "confirm_token" in nxt
    assert "once" in nxt

    # AND THE TWO ACTIONS HAVE PARTED, which is the fact the old version of
    # this stanza asserted in its opposite form. It ran over
    # ``("apply_job", "set_open_to_work")`` requiring BOTH to be surface-less,
    # under a comment about the refusal wording having to fit both -- it had
    # said "its EDITOR has never been loaded" and "change it yourself if you
    # want it CHANGED", true of a profile setting behind an editor and nonsense
    # on an application. Apply no longer renders that string at all, so the
    # constraint retires and what replaces it is the split itself.
    assert spec_for_action("set_open_to_work").url_template is None


def test_every_verdict_is_pinned_to_ITS_ACTION_not_to_the_set_of_verdicts():
    """2c, repaired at the spec.

    The mutation that used to survive: set every ``reversibility_class`` to
    IRREVERSIBLE. Under the old assertion all four still passed, because
    IRREVERSIBLE is a member of the set of values that exist. Pinning per
    action is what makes the headline claim of the wave -- all four REVERSIBLE
    -- an assertion rather than a sentence in a commit message.
    """
    assert set(REVERSIBILITY_CLASS) == {s.action for s in SANCTIONED_WRITES.values()}
    for spec in SANCTIONED_WRITES.values():
        assert spec.reversibility_class == REVERSIBILITY_CLASS[spec.action], spec.action
        assert (
            spec.reversibility_measured is REVERSIBILITY_MEASURED[spec.action]
        ), spec.action

    # THE TABLE MUST NOT BE UNIFORM, which is a property of the ASSERTION and
    # not of the specs. When every action carried the same verdict, pinning
    # per action and pinning the set were indistinguishable, and a mutation
    # that flipped all of them was invisible. One action now disagrees, so
    # this check has something to lose.
    assert len(set(REVERSIBILITY_CLASS.values())) > 1
    assert len(set(REVERSIBILITY_MEASURED.values())) > 1


async def test_a_verdict_that_contradicts_its_own_sentence_will_not_render(
    writes_on,
    monkeypatch,
    browser_page,
):
    """2c, repaired as a MECHANISM rather than only as an assertion.

    Pinning the class per action stops THIS repo drifting. It does not stop the
    two fields disagreeing -- a future spec could carry IRREVERSIBLE beside
    "reversible by unsaving the same posting" and the pin would simply be
    updated to match. So the gate now refuses to render a block whose one-word
    verdict contradicts the sentence printed beside it: two fields in
    disagreement tell the reader less than one field saying nothing, because he
    cannot tell which half to believe.
    """
    save = spec_for_action("save_job")
    flipped = writes.WriteSpec(
        **{**save.__dict__, "reversibility_class": "IRREVERSIBLE"}
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", flipped)
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job")
    assert "IRREVERSIBLE while the sentence beside it" in str(excinfo.value)


async def test_that_refusal_does_not_fire_on_the_specs_as_they_stand(
    writes_on,
    browser_page,
):
    """THE CONTROL. Without it the refusal above passes on a renderer that has
    started refusing everything."""
    for spec in SANCTIONED_WRITES.values():
        assert writes._reversibility_disagreement(spec) is None, spec.action
    block, _ = await _gate(browser_page, "save_job")
    assert block["reversibility_class"] == "REVERSIBLE"


async def test_the_gate_still_refuses_to_print_an_unmeasured_claim(
    writes_on,
    monkeypatch,
    browser_page,
):
    """THE CONTROL for the measured-reversibility rule, and it matters more now
    than when it was written.

    Every real spec is measured today, so the assertions above would pass on a
    renderer that had lost the ability to say UNMEASURED at all -- which is
    precisely how a rule dies: not repealed, just never exercised again. So the
    refusal is driven against a spec that is unmeasured by construction.
    """
    unmeasured = writes.WriteSpec(
        **{
            **spec_for_action("save_job").__dict__,
            "reversibility_measured": False,
            "reversibility_class": "STILL-UNKNOWN",
        }
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", unmeasured)
    block, _ = await _gate(browser_page, "save_job")
    assert block["reversibility_measured"] is False
    assert block["reversibility"].startswith("UNMEASURED")
    assert unmeasured.reversibility_procedure in block["reversibility"]
    assert not block["reversibility"].startswith("reversible")


async def test_an_unmeasured_claim_may_not_wear_a_measured_verdict(
    writes_on,
    monkeypatch,
    browser_page,
):
    """The half of the rule the class field was quietly outside of: printing
    UNMEASURED prose beside ``reversibility_class: REVERSIBLE`` is the
    confident string with an extra step."""
    half = writes.WriteSpec(
        **{
            **spec_for_action("save_job").__dict__,
            "reversibility_measured": False,
        }
    )
    monkeypatch.setitem(writes.SANCTIONED_WRITES, "linkedin_save_job", half)
    with pytest.raises(WriteAttemptError) as excinfo:
        await _gate(browser_page, "save_job")
    assert "UNMEASURED" in str(excinfo.value)


async def test_a_follow_says_plainly_that_this_server_cannot_take_it_back(
    writes_on,
    browser_page,
):
    """The field most likely to mislead, and 2b: it was NOT being asserted.

    "Reversible" reads as "this tool can undo it". For ``follow_company`` that
    is FALSE -- no unfollow is sanctioned, so a follow performed here is one
    only he can reverse, by hand. Two of the four are undoable by this server
    and two are not, and the gate has to say which it is holding.

    THE MUTATION THAT USED TO SURVIVE: rewrite ``save_job.reversible_by`` to
    "HIM, by hand. NOT this server..." -- the exact inversion -- and the old
    ``assert "this server" in by_server`` still passed, because "NOT this
    server" CONTAINS "this server". The positive half was a substring of the
    negative half. It is now asserted in both directions.
    """
    by_server = spec_for_action("save_job").reversible_by
    assert "this server" in by_server
    assert "NOT this server" not in by_server
    assert "Not this server" not in by_server

    for action in ("follow_company", "set_open_to_work"):
        by_hand = spec_for_action(action).reversible_by
        assert "NOT this server" in by_hand or "Not this server" in by_hand, action

    # 2026-08-24: follow_company nearly LOST this assertion, and the near-miss
    # is worth recording because it is the exact failure mode the field exists
    # to catch. Building unfollow made it tempting to soften the sentence to
    # "possibly by this server", which would have been a capability claim
    # resting on a resolution step nobody has. The answer is unchanged -- not
    # this server -- and only the REASON moved. So the reason is asserted too,
    # or the field could drift back to a comfortable sentence at the next edit.
    follow_by = spec_for_action("follow_company").reversible_by
    assert "slug" in follow_by
    assert "numeric company id" in follow_by

    # apply_job is stronger than either: not undoable by anybody through this
    # server, in either direction, and the field must not blur that into the
    # by-hand case.
    apply_by = spec_for_action("apply_job").reversible_by
    assert "NOBODY" in apply_by

    # unfollow_company is performable, so its own undo -- a follow -- is the
    # one this server does NOT do. The pair must not both claim to cover each
    # other; that would be a cycle of two half-truths reading as one whole one.
    #
    # THIS WAS AN ``or`` UNTIL 2026-09-03, AND THE ``or`` PINNED A LIE IN:
    #
    #     assert "NOT this server" in unfollow_by or "not performed" in unfollow_by
    #
    # The second arm accepted "linkedin_follow_company is sanctioned but is
    # not performed" as a SATISFYING condition. That sentence went false on
    # 2026-08-30, the day follow_company entered PERFORMABLE, and went on
    # being printed to him because this test was happy either way. A test that
    # will accept either of two reasons cannot notice when one of them stops
    # being true -- it is not merely failing to catch the drift, it is the
    # reason the drift reads as intentional to the next person who looks.
    #
    # The verdict and the reason are now asserted SEPARATELY, and the reason
    # is the aiming gap, which is a property of two address spaces rather than
    # a permission that can be flipped by one line in a frozenset.
    unfollow_by = spec_for_action("unfollow_company").reversible_by
    assert "NOT this server" in unfollow_by
    aiming = unfollow_by.casefold()
    assert "slug" in aiming
    assert "numeric company id" in aiming

    # And the distinction survives into the block he actually reads, which is
    # the only place it can do him any good.
    save_block, _ = await _gate(browser_page, "save_job")
    follow_block, _ = await _gate(browser_page, "follow_company")
    assert save_block["reversible_by"] != follow_block["reversible_by"]
    assert "NOT this server" in follow_block["reversible_by"]
    assert "NOT this server" not in save_block["reversible_by"]


def test_every_sanctioned_spec_carries_a_procedure_that_would_settle_it():
    """An unmeasured claim must name its own fix, or it is just a caveat."""
    for spec in SANCTIONED_WRITES.values():
        assert len(spec.reversibility_procedure) > 60, spec.action
