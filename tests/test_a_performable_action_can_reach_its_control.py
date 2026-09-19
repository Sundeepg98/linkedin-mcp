"""A performable action must be able to REACH the control it would press.

THE THIRD TERM NOBODY ENUMERATED. ``tests/test_addressing_is_not_permission.py``
was written on 2026-09-02 for the defect class that cost this wave nine sites,
and it pins TWO facts against each other:

    membership   the action is in ``writes.PERFORMABLE``
    addressing   its spec carries a ``url_template``

Both are true of every performable action today, that file asserts it, and it
is a real instrument -- ``writes.grant_is_possible`` exists because those two
were computed separately in three places and disagreed the moment one action
acquired a url while still refusing.

**IT CANNOT SEE WHETHER AN ADDRESSED, PERMITTED ACTION CAN ACTUALLY ACT.**
There is a third term in that chain and this file is it:

    aiming       ``anchor_label_for`` returns the accessible name the control
                 must be wearing, so ``perform`` can build a selector

``perform`` reads all three, in that order, and the aiming one is checked
FIRST -- before ``assert_write_url``, before the navigation, before any read.
An action that fails it never loads a page at all.

## The failure this reproduces, measured 2026-09-02

``update_profile_field`` entered ``PERFORMABLE`` on 2026-09-02 in ``a540461``,
described in its own commit subject as "the eleventh, and the best verified".
Driven end to end with writes enabled, a real target and a redeemed grant:

    RAISED WriteAttemptError:
      'update_profile_field' has no measured anchor and will not be
      performed. ... anchor_label_for has no branch for
      'update_profile_field' ...

    NAVIGATIONS ATTEMPTED: []

Zero navigations. ``anchor_label_for`` has arms for ``comment_on_item``,
``publish_post``, ``send_invitation``, ``react_to_item``, ``update_setting``,
``unfollow_company``, ``follow_company`` and ``apply_job``, then falls through
to a reverse lookup in ``shape.SAVE_LABELS``. ``editor_addressed`` is in no
label table, so the lookup returns ``None``, and the action is not in
``_SAVE_FAMILY``, so the guard raises.

AND THE GATE STILL ASKS HIM TO CONFIRM IT. ``writes.grant_is_possible``
returns ``True`` -- membership passes and the url is real -- so ``mint`` issues
a live ``confirm_token`` off a real read of his profile. He is shown a preview,
he confirms, and the second call dies at the first guard. That is worse than a
capability that refuses: it is one that asks for authorisation and then
refuses.

## This is the SAME DEFECT, in the SAME FUNCTION, seven days earlier

From ``anchor_label_for``'s own comment on the arm added 2026-08-26:

    ADDED 2026-08-26, and its absence was not a subtlety: apply fell through
    to the SAVE_LABELS lookup below, matched nothing, and perform refused
    every apply with a sentence about the save control's unphotographed ON
    state. The action was registered, listed in PERFORMABLE, and reported by
    server_info as performable and irreversible -- and could not run.

Registered, listed, reported, and could not run. Every clause of that
describes ``update_profile_field`` today. The comment recording the previous
occurrence sits in the function where the next one happened.

**THAT IS WHY THIS FILE IS A TEST AND NOT A FIX.** A comment describing a
defect did not stop the defect recurring in the function it is written in. The
standing rule this repo keeps arriving at is the one that applies: when an
invariant holds, ask whether anyone RULED it -- and "every performable action
resolves an anchor" was true for months, was never asserted, and something
depended on it.

## What this file asserts, and what it deliberately does not

IT ASSERTS REACHABILITY, NOT CORRECTNESS. That ``anchor_label_for`` returns a
non-empty label says the action can get past ``perform``'s first guard. It says
NOTHING about whether the label is the right one -- that is a question about a
measurement, answered by the capture that produced the label, and no test can
substitute for it.

The neighbouring half -- that ``_live_control`` then returns a usable selector
-- lives in ``tests/test_preview_state_and_click_state.py``, which drives ten
of the eleven actions through their real fixtures and records the eleventh in
its ``CANNOT_REACH`` table with the reason. Between the two files the chain is
covered end to end. Neither alone is the claim, which is why both exist.

THE SAVE FAMILY IS THE ONE PLACE ``None`` IS NOT A DEFECT, and the carve-out is
narrow and asserted rather than assumed: ``perform`` lets a save-family action
past a ``None`` anchor into a second, more specific raise, because for that
family a missing anchor means ``shape.SAVE_LABELS`` lost a row rather than that
nobody wrote a branch. Both members resolve an anchor today, so the carve-out
is exercised as a fact about the table and not as an exemption.
"""
from __future__ import annotations

import pytest

from linkedin_server import writes
from linkedin_server.writes import spec_for_action

#: A canonical target per target kind, because ``anchor_label_for`` takes one
#: for the multi-state action and ignores it for every other. These are shapes,
#: not data: no job id here is a job he has seen and no member string is a
#: person. ``_target_for`` normalises each into the form the real gate uses, so
#: a kind that changed shape fails here rather than being fed a stale spelling.
#: THE URN IS BUILT, NOT WRITTEN OUT, and this file learned that from
#: ``tests/test_typed_bytes.py``, which records why in its own comment: a urn
#: literal there held HIS REAL POST until 2026-09-01 and reached a commit on a
#: PUBLIC repo before ``test_no_committed_identity`` caught it.
#:
#: THE FIRST DRAFT OF THIS FILE WROTE ONE OUT, with invented digits, and the
#: sweep refused it -- "2 unallowed urn id hit(s), 0 declared" -- BEFORE the
#: commit. That refusal is correct and the invented digits are not a defence:
#: the rule is SHAPE-based on purpose, because a reviewer reading a diff
#: cannot tell an invented activity id from a real one, and a guard that
#: required them to would not be a guard. Constructing it keeps the measured
#: shape and puts no urn in the source at all.
_ACTIVITY_URN = "urn:li:" + "activity:" + ("1234567890" * 2)[:19]

_TARGETS: dict[str, object] = {
    "job_id": "1234567890",
    "company_id": "1234567",
    "item_urn": _ACTIVITY_URN,
    "member": "a needle nobody is",
    "post_text": "some text",
    "item_and_text": {"item": _ACTIVITY_URN, "text": "some text"},
    "field_and_value": {"field": "City", "value": "somewhere"},
    "setting_and_value": {"setting": "dark mode", "value": "Always on"},
    "member_and_text": {"member": "a needle nobody is", "text": "some text"},
}


def _canonical(action: str) -> str:
    """The target ``perform`` would hold for this action, normalised."""
    spec = spec_for_action(action)
    assert spec.target_kind in _TARGETS, (
        f"{action!r} is addressed by target_kind {spec.target_kind!r}, which "
        "this file has no shape for. Add one -- a new kind reaching "
        "PERFORMABLE without a row here makes this whole file skip it "
        "silently, which is the shape of hole it exists to close."
    )
    return writes._target_for(spec, _TARGETS[spec.target_kind])


def test_the_target_shapes_cover_every_performable_kind():
    """The corpus is not allowed to be quietly incomplete.

    A fan-out over a table is only as good as the table, and a missing row
    here would make the parametrised test below pass by never running for the
    action that needed it. Asserted before the fan-out rather than after.
    """
    kinds = {spec_for_action(a).target_kind for a in writes.PERFORMABLE}
    missing = sorted(kinds - set(_TARGETS))
    assert not missing, missing
    assert writes.PERFORMABLE, "PERFORMABLE is empty; this file certifies nothing"


@pytest.mark.parametrize("action", sorted(writes.PERFORMABLE))
def test_every_performable_action_resolves_an_anchor(action):
    """THE CHECK. A performable action must name the control it would press.

    ``perform`` runs this before it navigates, so an action failing here
    cannot reach its own surface, cannot read its own control and cannot
    click -- while ``mint`` will still have handed out a live confirm token
    for it, because membership and addressing both pass.

    IT IS EXPECTED TO FAIL FOR ``update_profile_field`` until the missing arm
    lands. That failure is the deliverable of this file rather than a defect
    in it: the action is in ``PERFORMABLE``, the server reports it as
    performable, and it raises at the first guard with zero navigations.
    """
    spec = spec_for_action(action)
    anchor = writes.anchor_label_for(spec, _canonical(action))

    if action in writes._SAVE_FAMILY:
        # THE ONE CARVE-OUT, and it is exercised rather than exempted. For
        # this family ``perform`` has a second, more specific raise, because
        # a None here means shape.SAVE_LABELS lost a row -- a regression in a
        # measured table -- rather than that nobody wrote a branch. Both
        # members resolve today and this asserts that they do.
        assert anchor, (
            f"{action!r} resolves no anchor, which for the save family means "
            "shape.SAVE_LABELS no longer maps a name to "
            f"{spec.from_state!r}. It currently holds "
            f"{sorted(__import__('linkedin_server.shape', fromlist=['x']).SAVE_LABELS)}. "
            "That is a regression in the table, not a missing measurement."
        )
        return

    assert anchor, (
        f"{action!r} is in PERFORMABLE and anchor_label_for returns None for "
        "it, so writes.perform raises at its FIRST guard -- before "
        "assert_write_url, before the navigation, before any control is read. "
        "The action cannot act. It is not refused honestly either: "
        f"grant_is_possible is {writes.grant_is_possible(spec)!r}, so mint "
        "issues a live confirm_token, he is asked to authorise it, and the "
        "second call dies. This is the defect apply_job carried until "
        "2026-08-26, recorded in a comment inside anchor_label_for itself."
    )


def test_the_check_fires_when_an_arm_goes_missing(monkeypatch):
    """SHOWN FAILING, because a check that has never fired certifies nothing.

    The mutation is the defect itself: an action whose spec is otherwise
    complete and for which ``anchor_label_for`` answers ``None``. Fired
    against ``react_to_item``, which resolves a real anchor today from its own
    branch, so the mutation removes a working arm rather than confirming an
    already-broken one.
    """
    real = writes.anchor_label_for

    def _no_arm(spec, target=None):
        if spec.action == "react_to_item":
            return None
        return real(spec, target)

    monkeypatch.setattr(writes, "anchor_label_for", _no_arm)
    assert writes.anchor_label_for(spec_for_action("react_to_item"), None) is None
    with pytest.raises(AssertionError):
        test_every_performable_action_resolves_an_anchor("react_to_item")


#: WHERE ``/in/me/`` LANDS, MEASURED LIVE 2026-09-01 and recorded in
#: ``_audit/2026-08-31-linkedin-perform.md`` under "Item 1 -- ANSWERED":
#:
#:     landed_paths    editor /in/<member>/edit/intro
#:
#: The vanity form, and no trailing slash. That is not an accident to be
#: normalised away -- it is the documented behaviour of the address:
#: ``readonly``'s own allowlist comment reads "Own profile. /in/me/ redirects
#: to whoever is signed in", and that redirect is the entire reason ``/in/me/``
#: is the ONLY profile spelling admitted, since it is the one form that cannot
#: be aimed at a third party.
#:
#: A SANITISED SHAPE, not his slug. The member segment here is the placeholder
#: the committed audits already use -- ``scripts/sweep_tracked_for_identity.py``
#: passes over those files -- so nothing in this line is his.
#:
#: BOTH LANDINGS ARE MEASURED, and they are two separate recordings:
#:
#:   profile  ``/in/<member>/``            _audit/_slice-editor-fields.md:347
#:   editor   ``/in/<member>/edit/intro``  _audit/2026-08-31-linkedin-perform.md
#:
#: which matters because TWO shipped actions navigate to a ``/in/me/`` url and
#: both are affected, not one.
_MEASURED_LANDINGS: dict[str, str] = {
    "send_invitation": "https://www.linkedin.com/in/alex-r-12ab34/",
    "update_profile_field":
        "https://www.linkedin.com/in/alex-r-12ab34/edit/intro",
}


def test_the_self_profile_actions_are_the_ones_this_defect_reaches():
    """The affected set is DERIVED from the specs, never typed.

    A hardcoded pair here would be a second place for "which actions use a
    ``/in/me/`` surface" to be true, and the whole finding is that nobody had
    asked the question. Ask it of the specs instead, so a third action landing
    on that surface joins the fan-out below without anybody remembering to add
    it.
    """
    derived = {
        action
        for action in writes.PERFORMABLE
        if "/in/me/" in str(spec_for_action(action).url_template or "")
    }
    assert derived == set(_MEASURED_LANDINGS), sorted(
        derived.symmetric_difference(_MEASURED_LANDINGS)
    )
    # And none of them takes the job-id branch, which is the branch that
    # would have made the whole-url comparison irrelevant.
    for action in derived:
        assert spec_for_action(action).target_kind != "job_id", action


@pytest.mark.parametrize("action", sorted(_MEASURED_LANDINGS))
def test_the_landing_check_accepts_the_url_this_action_actually_lands_on(action):
    """THE SECOND GUARD, AND IT WAS A SEPARATE BLOCKER FROM THE ANCHOR.

    ``perform`` runs three checks in order and an action must pass ALL of
    them to reach its control:

        anchor_label_for          before any navigation
        _assert_landed_on_target  after the navigation
        _live_control             the control itself

    ``update_profile_field`` fails the first and the third; this pins the
    SECOND, which sits between them and would surface only after the first was
    repaired. Fixed one at a time, that is three rounds.

    AND IT IS NOT ONE ACTION. ``send_invitation`` -- shipped 2026-09-01 as
    "THE EIGHTH, and the FIRST that reaches another person" -- navigates to
    ``/in/me/`` and RESOLVES ITS ANCHOR CLEANLY (`' to connect'`), so it
    passes the first check and then fails this one. It is a second shipped
    capability that cannot act, with a different blocker count and the same
    cause.

    WHY IT FAILS. ``_assert_landed_on_target`` has two shapes. A POSTING is
    compared by the job id inside its url, because LinkedIn also serves a slug
    form of the same posting. Everything else is compared WHOLE -- which is
    correct for a list surface that has one address, and false for any
    ``/in/me/`` url, whose whole purpose is that it redirects.

    So the comparison is:

        built by perform   .../in/me/edit/intro/
        actually landed    .../in/<member>/edit/intro

    ``/in/me/`` REDIRECTING IS NOT AN EDGE CASE. It is the entire reason that
    spelling is the only profile form on the read allowlist, and ``readonly``
    says so beside the pattern. A whole-url comparison was never going to hold
    against it; it held only because nothing had ever navigated there to
    WRITE.

    **THIS TEST WAS WRITTEN INVERTED AND FLIPPED WHEN THE FIX LANDED.** It
    first asserted the RAISE -- this repo's own "record a known defect so it
    FAILS when the defect is fixed" pattern -- so the repair could not land
    while the marker stood. It went red the instant the fix went in, which is
    the marker doing its job, and this is its post-fix form.

    The landed urls are MEASURED, not imagined: ``/in/<member>/edit/intro``
    from a live run on 2026-09-01, and ``/in/<member>/`` from the editor
    slice. That is what separates this from a guess about a redirect.
    """
    spec = spec_for_action(action)
    grant = writes.WriteGrant(
        action=spec.action,
        target=_canonical(action),
        token="not-a-real-token",
        minted_at=0.0,
        consumed=True,
    )
    # No raise. The member segment may differ; nothing else may.
    writes._assert_landed_on_target(spec, grant, _MEASURED_LANDINGS[action])


@pytest.mark.parametrize("action", sorted(_MEASURED_LANDINGS))
def test_the_relaxation_holds_the_path_after_the_member_exact(action):
    """WHAT THE RELAXATION DOES NOT BUY, and this is the half that matters.

    Allowing the member segment to differ is not allowing the url to differ.
    The path AFTER the segment is still compared exactly, so a redirect
    landing on a different surface -- the skills editor instead of the intro
    editor, the profile root instead of an editor -- is refused as before.

    WITHOUT THIS THE FIX WOULD BE A HOLE RATHER THAN A REPAIR. The first
    version tried was running BOTH sides through ``shape.census_substitute``,
    which normalises every member segment to the same ``<member>`` token --
    so his editor and A STRANGER'S editor compare EQUAL. Measured before it
    was rejected, and a comparison that cannot tell those apart is not a
    landing check.

    WHAT MAKES THE ACCEPTED CASE SAFE is a property of the REQUEST rather than
    of the landing: the url is rebuilt from the grant by ``assert_write_url``,
    ``readonly`` admits only the ``/in/me/`` spelling, and ``/in/me/`` can
    resolve to exactly one member -- the one signed in. So the guard accepts
    "LinkedIn told us who you are" and refuses everything else.
    """
    spec = spec_for_action(action)
    grant = writes.WriteGrant(
        action=spec.action,
        target=_canonical(action),
        token="not-a-real-token",
        minted_at=0.0,
        consumed=True,
    )
    landed = _MEASURED_LANDINGS[action]

    # A DIFFERENT SURFACE ON THE SAME PROFILE. Same member, wrong page.
    with pytest.raises(writes.WriteAttemptError) as caught:
        writes._assert_landed_on_target(
            spec, grant, landed.rstrip("/") + "/somewhere-else"
        )
    assert "the path after it is not" in str(caught.value), str(caught.value)

    # AND A LANDING THAT LEFT THE PROFILE FAMILY ALTOGETHER.
    with pytest.raises(writes.WriteAttemptError) as caught:
        writes._assert_landed_on_target(
            spec, grant, "https://www.linkedin.com/feed/"
        )
    assert "not a /in/<member>/ url" in str(caught.value), str(caught.value)


def test_the_refusal_no_longer_calls_a_profile_edit_a_list_write():
    """THE BORROWED PROSE, IN A GATE RATHER THAN A RECEIPT.

    ``3742a2d`` removed this defect family from ``perform``'s receipt. This is
    the same family in a REFUSAL, and a refusal is the worse place for it: a
    receipt describes what happened, a refusal is what he reads while the
    server is STOPPING him, and a wrong explanation there teaches him the
    wrong model of what is safe.

    Until 2026-09-02 every action reaching the whole-url comparison was told
    "A list write is anchored to a row on one page", which is true of exactly
    one target kind. The sentence is now the action's own, and the one action
    it was always true of still says it.
    """
    setting = spec_for_action("update_setting")
    grant = writes.WriteGrant(
        action=setting.action,
        target=_canonical("update_setting"),
        token="not-a-real-token",
        minted_at=0.0,
        consumed=True,
    )
    with pytest.raises(writes.WriteAttemptError) as caught:
        writes._assert_landed_on_target(
            setting, grant, "https://www.linkedin.com/mypreferences/d/elsewhere"
        )
    message = str(caught.value)
    assert "list write" not in message, message
    assert "one measured surface" in message, message

    unfollow = spec_for_action("unfollow_company")
    grant = writes.WriteGrant(
        action=unfollow.action,
        target=_canonical("unfollow_company"),
        token="not-a-real-token",
        minted_at=0.0,
        consumed=True,
    )
    with pytest.raises(writes.WriteAttemptError) as caught:
        writes._assert_landed_on_target(
            unfollow, grant, "https://www.linkedin.com/feed/"
        )
    assert "list write" in str(caught.value), str(caught.value)


def test_the_landing_check_passes_for_the_surfaces_that_do_not_redirect():
    """THE CONTROL, so the test above is a finding rather than a tautology.

    ``_assert_landed_on_target``'s whole-url comparison is CORRECT for the
    actions it was written for: a list surface has exactly one address and
    landing anywhere else genuinely does mean the row is not on screen. If
    this control ever fails, the check has broken generally and the test above
    is measuring that instead of the redirect.
    """
    spec = spec_for_action("update_setting")
    target = _canonical("update_setting")
    grant = writes.WriteGrant(
        action=spec.action,
        target=target,
        token="not-a-real-token",
        minted_at=0.0,
        consumed=True,
    )
    landed = str(spec.url_template).format(target=target)
    writes._assert_landed_on_target(spec, grant, landed)


def test_an_action_that_cannot_aim_still_gets_a_token(monkeypatch):
    """THE HALF THAT MAKES THIS URGENT RATHER THAN TIDY.

    ``grant_is_possible`` asks two questions -- membership and addressing --
    and neither of them is aiming. So an action that cannot reach its control
    is still granted a live token, and the refusal arrives AFTER he has
    confirmed rather than instead of the offer.

    Asserted with the real ``update_profile_field`` spec, because it is the
    action this is true of today. When its arm lands this test still passes:
    it is a statement about what ``grant_is_possible`` does NOT check, and
    that stays true whether or not any action currently trips it.
    """
    spec = spec_for_action("update_profile_field")
    assert writes.grant_is_possible(spec) is True, (
        "grant_is_possible has started consulting the anchor. If that is "
        "deliberate, this test should be rewritten to say so -- but note "
        "mint's own comment: it keeps membership and addressing as SEPARATE "
        "refusals because a caller needs to know WHICH applies."
    )
