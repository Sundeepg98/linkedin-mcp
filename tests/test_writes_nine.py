"""The seven capabilities that arrived sanctioned and refusing, certified.

On 2026-08-30 seven actions were added to ``SANCTIONED_WRITES`` as full
``WriteSpec`` entries -- publish a post, comment, react, edit a profile field,
change a setting, send an invitation, send a message -- and an eighth,
``follow_company``, became performable. This file is about the seven. It is
NOT about follow, which is covered where the performable actions are.

WHAT MAKES THE SEVEN AN UNUSUAL THING TO TEST. Every one of them is sanctioned
and none of them can act. That combination is only worth anything if it is
STRUCTURAL rather than a habit: a capability that cannot act because nobody
wired the click is one click away from acting, and a capability that cannot
act because no grant may exist for it is not. So the load-bearing claims here
are about the ABSENCE of a route -- which is exactly the shape that passes
forever on machinery that does nothing -- and each is therefore paired with
the positive case that would fire if the machinery were inert. Section 1 shows
mint reaching a DIFFERENT refusal for an action that does have a surface;
section 4 shows a token that DOES redeem beside the one that does not; section
5 shows the checks that DO run beside the shape check that deliberately does
not; section 6 shows the read door returning False.

THE FAKE SURFACES BELOW ARE BUILT HERE, and that is a deviation from the rest
of the write suite worth stating. ``tests/test_writes.py`` drives its gate over
FROZEN CAPTURES in ``tests/fixtures/``, and its ``_pages`` helper serves four
of them: a posting, the saved list, the profile topcard and the Manage Pages
list. Six of the seven specs read surfaces that helper does not serve -- the
feed and the settings index have no capture in this repo at all -- so a
minimal page is built here for each. Every selector in them is taken FROM
``linkedin_server.dom``'s own measured constants rather than typed a second
time, so a page here cannot drift away from the strings the readers look for;
what these fakes exercise is THE GATE'S LOGIC, and they measure nothing about
LinkedIn. The navigator, the browser fixture and the write-enable fixture are
imported from ``tests/test_writes.py`` rather than re-written, which is the
same cross-test import that file already makes of
``tests/test_server_surface.py``.

ONE ASSERTION IN SECTION 7 IS NOT THE ONE THIS FILE WAS ASKED FOR, and the
reason is a measurement rather than a preference. See the block comment there:
the superseded endorsement sentence is still present inside the new reason,
deliberately and as a marked quotation, so "that string is absent" would be
false today and would also be the WEAKER claim. What is asserted instead is
that the reason is not that sentence, that every occurrence of it sits inside
a superseded-quotation frame, and that the refusal now rests on named measured
counts.
"""

from __future__ import annotations

import re

import pytest

from linkedin_server import dom, readonly, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import (
    PERMANENTLY_FORBIDDEN,
    SANCTIONED_WRITES,
    TARGET_JOIN,
    consume,
    mint,
    preview,
    spec_for_action,
)
from tests.test_writes import (  # noqa: F401 -- three of these are fixtures
    JOB,
    FixtureNavigator,
    _bare_grant,
    browser_page,
    writes_on,
)

#: The seven, written out rather than derived from ``SANCTIONED_WRITES``. A
#: derived list would be satisfied by somebody deleting a spec, which is the
#: move these tests exist to make visible.
SEVEN = (
    "publish_post",
    "comment_on_item",
    "react_to_item",
    "update_profile_field",
    "update_setting",
    "send_invitation",
    "send_message",
)

#: A feed item key and a member key. Both are INVENTED, and inventing them is
#: allowed here precisely because of what section 5 certifies: this server has
#: never read either shape unshaped, so it validates neither, so no fixture
#: could be more honest than a placeholder. A test that used a real-looking
#: urn would be asserting a shape nobody has measured.
ITEM = "an-item-key-this-server-has-never-parsed"
MEMBER = "a-member-key-this-server-has-never-parsed"

#: Two different comments on the SAME item. The whole of section 4 is the
#: distance between these two strings surviving into the canonical target.
COMMENT_A = "Congratulations on the launch."
COMMENT_B = "Please send me your bank details."


# ---------------------------------------------------------------------------
# The minimum pages the six new readers can be run over
# ---------------------------------------------------------------------------
#
# Each is the SMALLEST markup that makes its reader return a settled state
# rather than ``unknown``, because ``_direction`` refuses to render a gate on
# an unknown and the block would never be reached. The counts here are 1 where
# the live census measured 1, 3, 8, 9 or 33; the number is not what is being
# tested, the presence of the control is.

FEED_MARKUP = (
    "<html><body>"
    # A div with role=button and no href, which is what the census measured.
    '<div role="button">' + dom.COMPOSER_CONTROL_NAME + "</div>"
    # The toggle whose accessible name carries its own state.
    '<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>'
    # Named by its TEXT, not by an aria-label, exactly as measured.
    "<button>" + dom.COMMENT_CONTROL_NAME + "</button>"
    '<a href="https://www.linkedin.com/messaging/" '
    'aria-label="Messaging, 0 new notifications">Messaging</a>'
    "</body></html>"
)

PROFILE_MARKUP = (
    "<html><body>"
    '<a href="https://www.linkedin.com/in/somebody'
    + dom.PROFILE_EDITOR_HREFS[0]
    + '">Edit intro</a>'
    # The label LinkedIn writes here is another person's name, so the fake
    # carries a placeholder and the reader never reads it -- see
    # dom.read_invitation_surface, which returns a count and nothing else.
    '<button aria-label="Invite Somebody' + dom.INVITE_CONTROL_SUFFIX + '"></button>'
    "</body></html>"
)

SETTINGS_MARKUP = (
    "<html><body>"
    '<a href="https://www.linkedin.com'
    + dom.SETTINGS_LINK_PREFIX
    + 'dark-mode">Dark mode</a>'
    "</body></html>"
)


def _nine_pages() -> dict[str, str]:
    """All three surfaces at once, so a reader asking for the wrong one is
    served rather than erroring -- the goto RECORD is what catches it."""
    return {
        writes.FEED_URL: FEED_MARKUP,
        writes.PROFILE_URL: PROFILE_MARKUP,
        writes.SETTINGS_URL: SETTINGS_MARKUP,
    }


#: A well-formed target for each of the seven, in the shape its own
#: ``target_kind`` is addressed by.
TARGETS: dict[str, object] = {
    "publish_post": "Shipping a small thing today.",
    "comment_on_item": {"item": ITEM, "text": COMMENT_A},
    "react_to_item": ITEM,
    "update_profile_field": {"field": "headline", "value": "Node.js engineer"},
    "update_setting": {"setting": "dark-mode", "value": "on"},
    "send_invitation": MEMBER,
    "send_message": {"member": MEMBER, "text": "Hello, are you hiring?"},
}

#: A clean value for every component name the five composite kinds use, so a
#: bad component can be injected into an otherwise valid target.
CLEAN_COMPONENT = {
    "text": "a real body of text",
    "item": ITEM,
    "field": "headline",
    "value": "a real value",
    "setting": "dark-mode",
    "member": MEMBER,
}


def _components(action: str) -> tuple[str, ...]:
    """The component names THIS action's target is addressed by.

    Read off ``_COMPOSITE_TARGET_KINDS`` rather than written down here, so the
    parametrisation cannot drift away from the module it is testing: adding a
    sixth composite kind widens these tests by itself.
    """
    spec = spec_for_action(action)
    first, second = writes._COMPOSITE_TARGET_KINDS[spec.target_kind]
    return (first, second) if second else (first,)


COMPOSITE_ACTIONS = tuple(
    action
    for action in SEVEN
    if spec_for_action(action).target_kind in writes._COMPOSITE_TARGET_KINDS
)
TWO_PART_ACTIONS = tuple(a for a in COMPOSITE_ACTIONS if len(_components(a)) == 2)
OPAQUE_ACTIONS = tuple(
    action
    for action in SEVEN
    if spec_for_action(action).target_kind in writes._OPAQUE_TARGET_KINDS
)

#: (action, component) for every component of every composite target.
COMPONENT_CASES = tuple(
    (action, name) for action in COMPOSITE_ACTIONS for name in _components(action)
)


def _target_with(action: str, component: str, value: object) -> object:
    """A target for ``action`` that is clean except for ``component``."""
    names = _components(action)
    if len(names) == 1:
        return value
    return {
        name: (value if name == component else CLEAN_COMPONENT[name])
        for name in names
    }


@pytest.fixture(autouse=True)
def _nothing_this_file_registers_outlives_it():
    """Belt and braces beside ``writes_on``'s own teardown. Section 4 puts a
    hand-built grant into ``_GRANTS`` directly, and a grant that leaked into
    the next test would be a grant nobody minted."""
    yield
    writes.discard_all()


async def _preview_the_refusal(page, action: str):
    """Drive the REAL gate for one of the seven. Returns ``(block, navigator)``.

    No argument chooses which surface is opened: ``observe`` picks it from the
    spec's own ``state_from``, and the navigator records what was actually
    asked for so that choice can be asserted rather than assumed.
    """
    spec = spec_for_action(action)
    nav = FixtureNavigator(_nine_pages())
    block = await preview(spec, target=TARGETS[action], navigator=nav, page=page)
    return block, nav


# ---------------------------------------------------------------------------
# 1. No grant can exist for any of the seven
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", SEVEN)
def test_none_of_the_seven_names_a_write_surface(action):
    """Both url fields empty, per action rather than as a claim about the set.

    A set-level assertion ("the surfaceless set is these eight") is satisfied
    by the set being right; it says nothing about WHICH field is empty, and
    ``assert_write_url`` needs BOTH -- it refuses on a missing template or a
    missing pattern, so a spec carrying one of the two would slip past a
    membership test while being half-armed.
    """
    spec = spec_for_action(action)
    assert spec.url_template is None, action
    assert spec.url_pattern is None, action


@pytest.mark.parametrize("action", SEVEN)
def test_mint_refuses_each_of_the_seven_a_grant_at_issue(writes_on, action):
    """Refused at ISSUE, not merely at use, and the message must say so.

    The distinction is the whole guarantee. If these were stopped only by
    ``assert_write_url`` there would be a live confirm token for a post in the
    process, and the single thing between it and a navigation would be a check
    a future click has to remember to run. There is no token at all.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        mint(action, TARGETS[action], receipt="anything")
    message = str(excinfo.value)
    assert "no grant is minted for" in message, message
    assert action in message, message


def test_mint_reaches_a_different_refusal_for_an_action_that_has_a_surface(
    writes_on,
):
    """THE CONTROL, and it is the one that matters for the seven tests above.

    ``mint`` refuses a great many things, and a test that only asserted "it
    raised" would pass on a mint that refused everything -- including a save,
    including a disabled flag. So the same call is made for ``save_job``, which
    DOES name a surface, and it must fall through to a different refusal
    entirely: the missing read receipt. Two different doors, and the seven are
    stopped at the first one.
    """
    with pytest.raises(WriteAttemptError) as excinfo:
        mint("save_job", JOB, receipt="not-a-real-receipt")
    message = str(excinfo.value)
    assert "no grant is minted for" not in message, message
    assert "read receipt" in message, message


# ---------------------------------------------------------------------------
# 2. A preview renders the warning block and issues no token
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", SEVEN)
async def test_a_preview_of_each_of_the_seven_issues_no_confirm_token(
    writes_on, browser_page, action
):
    """The block he reads is a WARNING and not an offer.

    Three fields carry that and all three are asserted, because they fail
    independently: ``to_confirm`` is the token itself, ``performed`` is what
    happened, and ``what_happens_next`` is the sentence he actually reads. A
    block could carry a null token and still tell him to confirm.
    """
    block, _nav = await _preview_the_refusal(browser_page, action)
    assert block["to_confirm"] is None, action
    assert block["performed"] is False, action
    assert "NO CONFIRM TOKEN IS ISSUED" in block["what_happens_next"], action
    # And it says WHY there is no token rather than leaving him to infer it:
    # the surface has never been loaded, so the block cannot even name the
    # page the action would act on.
    assert "UNMEASURED" in block["where"]["url"], action


@pytest.mark.parametrize("action", SEVEN)
async def test_each_refusal_is_a_fresh_reading_of_the_specs_own_surface(
    writes_on, browser_page, action
):
    """The point of these previews: a refusal that LOOKED, not one that
    remembers.

    All three surfaces are frozen for every action, so a reader pointed at the
    wrong one would be served rather than erroring. What catches it is the
    navigator's record: exactly one load, and it must be the url this spec's
    own ``state_from`` names. That also pins the restraint in send_message,
    which reads the messaging badge off the FEED precisely so that it never
    opens messaging.
    """
    spec = spec_for_action(action)
    expected, _surface, _reader = writes._SURFACE_READS[spec.state_from]
    _block, nav = await _preview_the_refusal(browser_page, action)
    assert nav.gotos == [expected], (action, nav.gotos)


async def test_the_message_gate_never_opens_messaging(writes_on, browser_page):
    """THE ONE COST THIS DESIGN REFUSES TO PAY ON A STRANGER'S BEHALF, made
    structural.

    Loading /messaging/ is measured to redirect into one specific conversation
    of LinkedIn's choosing and to reset the very badge that counts what is
    new. So the gate reads the badge off a page already open. This asserts the
    absence rather than trusting the comment that explains it.
    """
    _block, nav = await _preview_the_refusal(browser_page, "send_message")
    assert not any("/messaging" in url for url in nav.gotos), nav.gotos


# ---------------------------------------------------------------------------
# 3. Every refusal names its own fix
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", SEVEN)
def test_every_refusal_names_its_own_fix_and_a_measured_artefact(action):
    """A refusal that does not name its own fix is indistinguishable from one
    nobody intends to lift.

    Three things are required and each fails on its own: the length, because a
    one-line "cannot" is the shape that goes stale unnoticed; the phrase
    naming the fix; and a CONCRETE MEASURED ARTEFACT -- a count and an address
    -- because "this was measured" with nothing measured beside it is the
    confident string this package exists to refuse.
    """
    reason = writes._NINE_REFUSALS[action]
    assert len(reason) > 200, (action, len(reason))
    assert "WHAT WOULD LIFT IT" in reason.upper(), action
    assert "MEASURED" in reason, action
    assert re.search(r"\d", reason), action
    assert re.search(r"/[a-z]", reason), action


@pytest.mark.parametrize("action", SEVEN)
def test_refuse_unperformable_raises_the_actions_own_refusal_verbatim(action):
    """The dict and the raise are the same string, not two that agree today.

    ``_refuse_unperformable`` has a generic backstop at the bottom -- "not
    performable", true of all of them and explanatory of none. Asserting
    equality with the dict entry is what proves the backstop is not what he
    would actually read.
    """
    spec = spec_for_action(action)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._refuse_unperformable(spec)
    assert str(excinfo.value) == writes._NINE_REFUSALS[action], action


def test_the_seven_refusals_are_seven_different_strings():
    """THE CONTROL for the two tests above.

    Seven gaps printing one sentence would satisfy every per-action assertion
    in this section and teach a reader that the sentence carries no
    information. They are distinct, and distinct in their first hundred
    characters rather than only in a trailing clause.
    """
    reasons = [writes._NINE_REFUSALS[action] for action in SEVEN]
    assert len(set(reasons)) == len(SEVEN)
    assert len({reason[:100] for reason in reasons}) == len(SEVEN)


# ---------------------------------------------------------------------------
# 4. Content is bound into the target
# ---------------------------------------------------------------------------
#
# THE MOST IMPORTANT SECTION HERE, and the one with the least machinery behind
# it. There is no second gate binding a confirm token to the words a preview
# showed: the words ARE the target, ``consume`` already refuses a token whose
# target does not match, and the tool rebuilds the same canonical string from
# the same arguments on both calls. So "he approved these words" is carried
# entirely by ``_composite_target`` producing a different string for different
# text -- and by the four refusals that stop two different targets from
# canonicalising into one.


@pytest.mark.parametrize("action", TWO_PART_ACTIONS)
def test_a_composite_target_changes_when_only_the_content_changes(action):
    """The whole binding mechanism, stated as the property it is.

    Same subject, different content, different canonical string -- and the
    subject alone is NOT the target, which is the part that would silently be
    true if the content were dropped on the way through.
    """
    spec = spec_for_action(action)
    first, second = _components(action)
    subject = CLEAN_COMPONENT[first]
    one = writes._target_for(spec, {first: subject, second: COMMENT_A})
    two = writes._target_for(spec, {first: subject, second: COMMENT_B})
    assert one != two, action
    assert one == subject + TARGET_JOIN + COMMENT_A, action
    assert two == subject + TARGET_JOIN + COMMENT_B, action
    # The content is IN the string rather than hashed or summarised into it,
    # because the same string is what the gate prints for him to read.
    assert COMMENT_A in one and COMMENT_A not in two, action


@pytest.mark.parametrize("action,component", COMPONENT_CASES)
def test_the_target_separator_inside_a_component_is_refused(action, component):
    """The hole this refusal closes is ambiguity, not injection.

    With the separator allowed inside a component, ``{"item": "a :: b",
    "text": "c"}`` and ``{"item": "a", "text": "b :: c"}`` canonicalise to one
    string -- so a token bound to one is a token bound to the other, and a
    token bound to an ambiguous target is bound to nothing.
    """
    spec = spec_for_action(action)
    bad = _target_with(action, component, "before" + TARGET_JOIN + "after")
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec, bad)
    assert repr(TARGET_JOIN) in str(excinfo.value), (action, component)


@pytest.mark.parametrize("action,component", COMPONENT_CASES)
@pytest.mark.parametrize("empty", ["", "   "])
def test_an_empty_component_is_refused(action, component, empty):
    """Same failure as the separator, reached from the other side: an empty
    component makes ``a :: `` and `` :: a`` collapse toward each other.

    Whitespace is included because the value is stripped BEFORE it is checked,
    so a space-only component is an empty one wearing a disguise.
    """
    spec = spec_for_action(action)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec, _target_with(action, component, empty))
    assert "needs" in str(excinfo.value), (action, component)


@pytest.mark.parametrize("action,component", COMPONENT_CASES)
def test_a_component_over_the_character_cap_is_refused(action, component):
    """The cap is THIS SERVER'S, and the refusal says so.

    Nobody here has measured LinkedIn's own limit on a post, a comment or an
    InMail, so the message may not cite one. What the ceiling is for is
    bounding a string that ends up inside a grant, a confirm block and several
    error messages.
    """
    spec = spec_for_action(action)
    oversize = "x" * (writes.MAX_TARGET_CHARS + 1)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec, _target_with(action, component, oversize))
    message = str(excinfo.value)
    assert str(writes.MAX_TARGET_CHARS) in message, (action, component)
    assert "not LinkedIn's" in message, message


@pytest.mark.parametrize("action,component", COMPONENT_CASES)
@pytest.mark.parametrize("character", ["\r", "\n", "\t"])
def test_a_control_character_inside_a_component_is_refused(
    action, component, character
):
    """A newline is how a reader is shown one thing while another is bound.

    The character is placed in the MIDDLE of the value on purpose: the
    component is stripped before it is checked, so a leading or trailing
    newline would be gone before the check and would prove nothing.
    """
    spec = spec_for_action(action)
    bad = _target_with(action, component, "one" + character + "two")
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec, bad)
    assert "control character" in str(excinfo.value), (action, component)


@pytest.mark.parametrize("action", TWO_PART_ACTIONS)
def test_a_two_part_target_handed_a_non_dict_is_refused(action):
    """A bare string for a two-part target would silently become the subject
    with no content at all, which is the preview showing words that are bound
    to nothing."""
    spec = spec_for_action(action)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec, "just one string")
    message = str(excinfo.value)
    assert "mapping" in message, (action, message)
    first, second = _components(action)
    assert repr(first) in message and repr(second) in message, message


def test_a_one_part_target_does_take_a_bare_string():
    """THE CONTROL for the refusal above.

    ``post_text`` is a composite kind with ONE component, so it takes the bare
    value -- which is what makes "a non-dict is refused" a statement about
    arity rather than about composites in general.
    """
    spec = spec_for_action("publish_post")
    assert writes._target_for(spec, "a post body") == "a post body"
    assert TARGET_JOIN not in writes._target_for(spec, "a post body")


def test_a_confirm_token_bound_to_one_comment_is_refused_for_another(writes_on):
    """THE HOLE, SHOWN CLOSED -- and how this grant came to exist matters.

    NO GRANT CAN BE MINTED FOR A COMPOSITE ACTION TODAY. Section 1 is the
    proof: none of the five names a write surface, so ``mint`` refuses each at
    issue. This grant is therefore BUILT BY HAND and put into ``_GRANTS``
    directly. It is not a mint by another route and it is not a claim that one
    exists; it is the only way to reach ``consume`` with a composite target,
    and ``consume`` is where the binding actually lives. If any of the five is
    ever made performable, this is the check that will already be standing.

    The refusal is asserted BY ITS MESSAGE and not merely by the raise,
    because a hand-built grant that failed to register would raise too --
    "unknown or already-discarded confirm token" -- and that would be this
    test passing on the wrong door.
    """
    spec = spec_for_action("comment_on_item")
    approved = writes._target_for(spec, {"item": ITEM, "text": COMMENT_A})
    substituted = writes._target_for(spec, {"item": ITEM, "text": COMMENT_B})
    assert approved != substituted

    grant = _bare_grant(action="comment_on_item", target=approved)
    writes._GRANTS[grant.token] = grant

    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="comment_on_item", target=substituted)
    message = str(excinfo.value)
    assert "was minted for target" in message, message
    assert "already-discarded" not in message, message
    assert COMMENT_B in message, message

    # THE POSITIVE CASE. Without it the refusal above passes on a consume that
    # refuses everything, which is the exact shape this file exists to avoid.
    redeemed = consume(grant.token, action="comment_on_item", target=approved)
    assert redeemed.target == approved
    assert redeemed.consumed is True


async def test_the_gate_prints_the_words_in_full_beside_what_binds_them(
    writes_on, browser_page
):
    """The operator-facing half of the binding claim.

    A comment is published under his name, so "he approved a comment" means
    nothing unless he was shown the words. The block prints the subject and
    the content as separate readable fields AND the canonical string beside
    them, because if those two ever disagree the canonical one is what would
    act. Truncation here would be the defect.
    """
    block, _nav = await _preview_the_refusal(browser_page, "comment_on_item")
    where = block["where"]
    assert where["item"] == ITEM
    assert where["text"] == COMMENT_A
    assert where["target"] == ITEM + TARGET_JOIN + COMMENT_A
    assert where["target_kind"] == "item_and_text"


# ---------------------------------------------------------------------------
# 5. An opaque target declines to validate, and says so
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", OPAQUE_ACTIONS)
@pytest.mark.parametrize(
    "raw",
    [
        "urn:li:activity:0000000000000000000",
        "nothing-like-a-urn-at-all",
        "  padded and stripped  ",
    ],
)
def test_an_opaque_target_accepts_any_clean_string(action, raw):
    """DECLINING TO VALIDATE IS THE HONEST ANSWER, not a gap.

    A feed item is addressed by a urn and a member by a slug, and this server
    has read NEITHER unshaped -- ``linkedin_surface_census`` substitutes
    ``<urn>`` and ``<member>`` out before anything is counted, deliberately, so
    a census cannot publish an identifier. A normaliser enforcing
    ``urn:li:activity:<digits>`` would be asserting a shape nobody has seen,
    which is precisely what this package refuses to do with a selector.

    The three inputs are the point: a urn-shaped string and a string that
    looks nothing like one are treated IDENTICALLY, which is what "no shape is
    enforced" means when it is true.
    """
    spec = spec_for_action(action)
    assert writes._target_for(spec, raw) == raw.strip()


@pytest.mark.parametrize("action", OPAQUE_ACTIONS)
def test_an_opaque_target_is_still_checked_for_what_is_checkable(action):
    """Declining to validate the SHAPE is not declining to validate anything.

    Empty, oversize, separator and control characters are refused here exactly
    as they are for a composite component, because those four are properties
    of the string rather than claims about LinkedIn's format. This is the
    control that keeps the permissiveness above from reading as no check at
    all.
    """
    spec = spec_for_action(action)
    for bad in ["", "   ", "a" + TARGET_JOIN + "b", "one\ntwo"]:
        with pytest.raises(WriteAttemptError):
            writes._target_for(spec, bad)
    with pytest.raises(WriteAttemptError):
        writes._target_for(spec, "x" * (writes.MAX_TARGET_CHARS + 1))


def test_the_module_says_why_an_opaque_target_declines_to_validate():
    """The reason is load-bearing and lives in the code, not in a review.

    If either of these actions is ever made performable, ``_opaque_target`` is
    the first thing that must change -- and the docstring is where that is
    recorded. A refusal whose reason lives only in a wave document is a
    refusal the next agent deletes.
    """
    doc = (writes._opaque_target.__doc__ or "").upper()
    assert "DECLINES TO VALIDATE" in doc
    assert "READ NEITHER UNSHAPED" in doc
    assert "FIRST THING THAT MUST CHANGE" in doc


@pytest.mark.parametrize("action", OPAQUE_ACTIONS)
def test_an_opaque_target_still_cannot_reach_a_grant(writes_on, action):
    """WHY ACCEPTING AN UNVALIDATED STRING IS SAFE TODAY, asserted rather than
    argued.

    Both opaque actions hold no ``url_template``, so ``mint`` refuses them at
    issue and no target of this kind can reach a navigation or a click. That
    is the entire safety argument for the permissiveness above, so it is
    pinned here beside it rather than left in section 1 where a future reader
    would have to go looking for it.
    """
    spec = spec_for_action(action)
    assert spec.url_template is None
    with pytest.raises(WriteAttemptError) as excinfo:
        mint(action, MEMBER, receipt="anything")
    assert "no grant is minted for" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 6. The seven do not widen the read boundary
# ---------------------------------------------------------------------------


def test_every_surface_the_seven_read_is_already_on_the_read_boundary():
    """THE LOAD-BEARING CLAIM OF THE WHOLE WAVE.

    Seven capabilities were added and the read boundary was not touched. That
    is checkable rather than assertable: every url these readers open goes
    through the SAME read door every read tool uses, so if one of them had
    needed a new allowlist entry it would fail here.

    The dict is also checked for CONTENT before it is iterated. A ``for url in
    {}`` loop passes, and a test that passes on an empty dict certifies
    nothing -- so the six surfaces are counted and reconciled against the
    ``state_from`` of the seven specs themselves.
    """
    assert len(writes._SURFACE_READS) == 6
    assert {spec_for_action(a).state_from for a in SEVEN} == set(
        writes._SURFACE_READS
    )
    for state_from, (url, _surface, reader) in writes._SURFACE_READS.items():
        assert readonly.is_read_url(url), (state_from, url)
        assert callable(reader), state_from


def test_the_read_door_is_the_same_door_and_would_refuse_a_widened_surface():
    """THE CONTROL for the test above.

    ``is_read_url`` returning True for three urls proves nothing unless it can
    return False. /mynetwork/ is the right probe because it is the surface
    ``send_invitation`` would obviously have used and did not -- loading it
    consumes the pending-invitation badge -- so this is the check that would
    have fired had the invitation gate taken the obvious route.
    """
    assert readonly.is_read_url("https://www.linkedin.com/mynetwork/") is False


# ---------------------------------------------------------------------------
# 7. The permanent refusals still say why, and the corrected ones say the
#    right why
# ---------------------------------------------------------------------------


def test_the_dissolved_policy_entries_are_gone_from_the_permanent_refusals():
    """The operator dissolved the POLICY bucket on 2026-08-30.

    A refusal survives there only if the thing is IMPOSSIBLE with a
    measurement behind it, or if performing it would be unattended. These two
    were neither, and each is now a sanctioned spec refusing on a measured
    blocker -- which is a refusal with a fix attached, where the entries they
    replaced were refusals with a preference attached.
    """
    assert "post_or_comment_or_like_or_share" not in PERMANENTLY_FORBIDDEN
    assert "profile_edit_beyond_open_to_work" not in PERMANENTLY_FORBIDDEN
    # And the capabilities they used to cover exist as specs instead, so this
    # reads as a MOVE rather than as a permission being quietly dropped.
    sanctioned = {spec.action for spec in SANCTIONED_WRITES.values()}
    for action in ("publish_post", "comment_on_item", "react_to_item"):
        assert action in sanctioned
    assert "update_profile_field" in sanctioned


def test_the_three_surviving_permanent_refusals_are_still_named():
    """What survived the dissolution, and it is not the same set as before.

    ``repost_or_share`` is the quarter of the old speech entry that was about
    somebody ELSE'S item rather than about taste. ``endorse_or_recommend``
    kept its name and lost its reason. The third is NEW that day, and it is
    the rule the endorsement ruling now rests on rather than a restatement of
    it.
    """
    for name in (
        "repost_or_share",
        "endorse_or_recommend",
        "load_a_third_partys_profile_to_measure_a_control",
    ):
        assert name in PERMANENTLY_FORBIDDEN, name
        assert len(PERMANENTLY_FORBIDDEN[name]) > 40, name


#: THE SENTENCE THE ENDORSEMENT REFUSAL USED TO REST ON, and the assertion
#: below is NOT the one this file was asked to make about it.
#:
#: THE ASK: assert this string is ABSENT from the reason.
#: THE MEASUREMENT: it is PRESENT, and deliberately so. The module's own
#: comment above PERMANENTLY_FORBIDDEN says "THREE ENTRIES WERE REWRITTEN OR
#: REMOVED ON 2026-08-30 AND THE OLD TEXT IS QUOTED IN EACH, because the
#: reason they went is the point", and this entry opens "REASON REPLACED
#: 2026-08-30. It used to read '<this sentence>' -- which was POLICY".
#:
#: So "absent" would be RED today, and it would also be the WEAKER claim: a
#: reason that had deleted its own history would satisfy it. What is asserted
#: instead is strictly stronger and is what the ask was reaching for -- the
#: reason IS NOT that sentence, every occurrence of it sits inside a
#: superseded-quotation frame, and the refusal now stands on named measured
#: counts. Recorded here rather than resolved silently.
#:
#: SECOND CORRECTION, same entry: the word "MEASURED" does not appear in it.
#: The words present are MEASUREMENT, measurement and measures. The ask
#: allowed either that word or a measured count, and the counts are what is
#: pinned below.
_OLD_ENDORSE_POLICY = (
    "a statement ABOUT ANOTHER PERSON, which is not his to automate"
)


def test_the_endorsement_refusal_rests_on_a_measurement_not_on_the_old_policy():
    reason = PERMANENTLY_FORBIDDEN["endorse_or_recommend"]

    # IT IS NOT THAT SENTENCE, which is the claim that was actually wanted.
    assert reason != _OLD_ENDORSE_POLICY
    assert not reason.startswith(_OLD_ENDORSE_POLICY)

    # AND WHERE IT SURVIVES IT IS MARKED AS SUPERSEDED. Every occurrence sits
    # inside a quotation frame that says so, so the entry cannot drift back to
    # arguing the old ground while keeping the new preamble.
    assert reason.startswith("REASON REPLACED")
    occurrences = list(re.finditer(re.escape(_OLD_ENDORSE_POLICY), reason))
    assert len(occurrences) == 1
    for match in occurrences:
        assert "It used to read" in reason[: match.start()]
        assert "which was POLICY" in reason[match.end() :]

    # AND IT NOW STANDS ON COUNTS, named rather than gestured at. These are
    # the measured artefacts the refusal cites; a reason rewritten back into a
    # policy sentence loses them.
    assert "13 tracked fixtures" in reason
    assert "222 controls" in reason
    assert "zero endorse controls" in reason
    assert "IMPOSSIBLE AS SPECIFIED" in reason


def test_the_repost_refusal_says_what_survived_and_what_did_not():
    """The narrowing is recorded IN the reason, so the three quarters that
    went cannot be mistaken for something nobody got round to."""
    reason = PERMANENTLY_FORBIDDEN["repost_or_share"]
    assert "NARROWED" in reason
    assert "post_or_comment_or_like_or_share" in reason
    # What survives is about somebody ELSE'S item, which is the part that was
    # never taste.
    assert "SOMEBODY ELSE'S" in reason.upper()


def test_the_claims_that_depend_on_the_destruction_refusal_are_the_measured_ones():
    """A refusal other claims lean on, pinned from BOTH ends and by NAME.

    ``delete_or_withdraw_anything`` carries a note saying five specs cite it in
    ``reversible_by``. THE NOTE WAS WRONG WHEN THIS TEST WAS FIRST WRITTEN, and
    the way it was wrong is why this is asserted by name rather than by count:
    it read "a post, a comment, a reaction, an invitation and a message",
    which NAMED react (which does not cite the entry) and OMITTED apply (which
    does). The number happened to be right while both ends of the list were
    wrong -- a count cannot catch that, and this test is written at the shape
    that can.

    ``react_to_item`` is the interesting exclusion and it is asserted
    explicitly. Its ``reversible_by`` leans on a different gap entirely -- the
    ON-state label has never been observed, so there is no selector for the
    inverse whatever any refusal list says. Shortening the destruction entry
    would break four claims and leave react's exactly as true, which is a fact
    about where each one actually rests.
    """
    assert "delete_or_withdraw_anything" in PERMANENTLY_FORBIDDEN
    # Across the WHOLE sanctioned set, not just the seven: apply_job is the
    # fifth and it predates this wave.
    leaning = tuple(
        sorted(
            spec.action
            for spec in SANCTIONED_WRITES.values()
            if "NOBODY" in spec.reversible_by
        )
    )
    assert leaning == (
        "apply_job",
        "comment_on_item",
        "publish_post",
        "send_invitation",
        "send_message",
    ), leaning
    for action in leaning:
        assert "forbidden" in spec_for_action(action).reversible_by.lower(), action
    # THE ONE NAMED IN THE ORIGINAL NOTE THAT DOES NOT BELONG, and what it
    # actually rests on. If somebody later rewrites react's reversible_by to
    # lean on the destruction entry, this is what makes that visible.
    reaction = spec_for_action("react_to_item").reversible_by
    assert "NOBODY" not in reaction
    assert "ON label unmeasured" in reaction
    # And the corrected note must name its own correction rather than having
    # been silently swapped -- this repo's convention, and the reason the
    # original error is legible at all.
    note = PERMANENTLY_FORBIDDEN["delete_or_withdraw_anything"]
    assert "CORRECTED" in note
    assert "react_to_item does not lean on this" in note
