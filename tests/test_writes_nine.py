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
feed and the dark-mode settings page have no capture in this repo at all -- so
a minimal page is built here for each. (That clause said "the settings index"
until 2026-08-31, when ``update_setting`` stopped reading the index and started
reading the one page that carries a VALUE.) Every selector in them is taken FROM
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

import dataclasses
import json
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

#: The ones that are sanctioned and STILL REFUSE, written out rather than
#: derived from ``SANCTIONED_WRITES``. A derived list would be satisfied by
#: somebody deleting a spec, which is the move these tests exist to make
#: visible.
#:
#: SEVEN UNTIL 2026-08-31, SIX FROM THAT DAY, THREE FROM 2026-09-01. ``update_setting`` left this tuple on the
#: day it entered ``writes.PERFORMABLE``, and it LEFT rather than being kept
#: with an exception, because every check below asserts that its subject
#: CANNOT be performed -- an action in both places would be asserted to be two
#: things at once, and one of the two assertions would have to be softened to
#: let it pass. Softening a check to accommodate a shipped capability is how a
#: check stops being one.
#:
#: The constant keeps its name so the link to the seven the operator asked
#: about is not lost; ``LIFTED`` below is where the difference is recorded.
SEVEN = (
    "comment_on_item",
    "update_profile_field",
    "send_message",
)

#: What has left ``SEVEN``, and when. An action may only be here if it is in
#: ``writes.PERFORMABLE``, which is asserted below -- so this cannot become a
#: place to park something that merely stopped passing.
LIFTED = {
    "update_setting": "2026-08-31",
    # THE SECOND DEPARTURE, and it left for a different reason from the first.
    # ``update_setting`` left because its last blocker was MEASURED away.
    # ``react_to_item`` left with one blocker still open -- which reaction the
    # toggle applies, and the never-seen ON label -- because the operator
    # lifted the standard on 2026-09-01 and admitted a write that applies
    # something this server cannot name, provided the gate says so. The
    # blocker did not close; it became a disclosure, and it is printed from
    # the spec's ``residue``.
    "react_to_item": "2026-09-01",
    # THE THIRD DEPARTURE, same day as the second and on the other half of the
    # same ruling. react_to_item kept a real verification and disclosed its
    # limit; send_invitation has NO verification and ships on the declaration.
    # Both left by shipping, which is the only way out of this tuple.
    "send_invitation": "2026-09-01",
    # THE FOURTH DEPARTURE, same day, and the one that changed what this
    # package IS: publish_post is the first action that TYPES. Its typing was
    # a permission the operator granted; its verification did not close and
    # was declared instead.
    "publish_post": "2026-09-01",
}


def test_nothing_left_the_refusing_set_except_by_shipping():
    """THE LEDGER'S OWN GUARD, and it is the whole reason ``LIFTED`` is a dict
    rather than a deleted line.

    An action can leave ``SEVEN`` for two reasons that look identical in a
    diff: it became performable, or its checks became inconvenient. This
    asserts the first. Every name recorded as lifted must really be in
    ``writes.PERFORMABLE``, no name may be in both, and the two together must
    still account for every sanctioned action -- so a spec quietly deleted
    goes missing from the total instead of going unnoticed.
    """
    for action, when in LIFTED.items():
        assert action in writes.PERFORMABLE, action
        assert action not in SEVEN, action
        assert when
    sanctioned = {spec.action for spec in SANCTIONED_WRITES.values()}
    accounted = (
        set(SEVEN) | set(LIFTED) | set(writes.PERFORMABLE) | {"set_open_to_work"}
    )
    assert sanctioned == accounted, sanctioned.symmetric_difference(accounted)

#: A feed item key and a member key. Both are INVENTED, and inventing them is
#: allowed here precisely because of what section 5 certifies: this server has
#: never read either shape unshaped, so it validates neither, so no fixture
#: could be more honest than a placeholder. A test that used a real-looking
#: urn would be asserting a shape nobody has measured.
ITEM = "an-item-key-this-server-has-never-parsed"

#: THE NEEDLE, and it changed on 2026-08-31 from a placeholder to a word that
#: MATCHES the invitation control in PROFILE_MARKUP below.
#:
#: It was ``"a-member-key-this-server-has-never-parsed"``, on the reasoning
#: that this server has never read a member key unshaped so no fixture could
#: be more honest than a placeholder. That reasoning is still right about a
#: member KEY and it was wrong about this field: the target here is a NEEDLE,
#: a word the operator types to pick one control out of several, and a needle
#: that matches nothing can only ever exercise the refusal.
#:
#: The wiring landed the same day made that visible immediately -- with the
#: needle finally reaching a live read, every invitation preview refused with
#: "nobody matched", which is a real answer to the wrong question.
MEMBER = "Somebody"

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

#: THE DARK-MODE PAGE, and it REPLACED a settings-INDEX markup on 2026-08-31.
#: The old one carried a single anchor, because the old reader counted how
#: many settings the index ADDRESSES -- a number that says nothing about any
#: setting's value. This carries the three radios the live page carries, named
#: the way the live page names them (``aria-labelledby``, not ``aria-label``),
#: with exactly one checked, because "exactly one checked" is the only state
#: ``_read_dark_mode`` will describe.
#:
#: No ``<form>``, deliberately: the live page measures ``forms: 0`` on all six
#: readings, and a fixture that wrapped these in one would be testing a page
#: LinkedIn does not serve.
DARK_MODE_MARKUP = (
    "<html><body>"
    '<span id="dm-off">Always off</span>'
    '<input type="radio" name="dm" aria-labelledby="dm-off" checked>'
    '<span id="dm-on">Always on</span>'
    '<input type="radio" name="dm" aria-labelledby="dm-on">'
    '<span id="dm-dev">Device settings</span>'
    '<input type="radio" name="dm" aria-labelledby="dm-dev">'
    "</body></html>"
)


def _nine_pages() -> dict[str, str]:
    """All three surfaces at once, so a reader asking for the wrong one is
    served rather than erroring -- the goto RECORD is what catches it."""
    return {
        writes.FEED_URL: FEED_MARKUP,
        writes.PROFILE_URL: PROFILE_MARKUP,
        writes.DARK_MODE_URL: DARK_MODE_MARKUP,
    }


#: THE DESTINATION a multi-state action requires, keyed by action. Only
#: ``update_setting`` has one: ``_direction`` derives the destination for a
#: binary toggle from the state it measured, and refuses to derive one for an
#: action with three.
#:
#: ``Always on`` rather than ``Always off``, and that is load-bearing: the
#: fixture above has ``Always off`` CHECKED, and ``_direction`` refuses a
#: destination equal to the current state with "the setting is already X.
#: Nothing to change." A test asking for the state it is already in would
#: exercise that refusal instead of the gate.
TO_STATES: dict[str, Optional[str]] = {"update_setting": "Always on"}


#: A well-formed target for each of the seven, in the shape its own
#: ``target_kind`` is addressed by.
TARGETS: dict[str, object] = {
    "publish_post": "Shipping a small thing today.",
    "comment_on_item": {"item": ITEM, "text": COMMENT_A},
    "react_to_item": ITEM,
    "update_profile_field": {"field": "headline", "value": "Node.js engineer"},
    "update_setting": {"setting": "dark-mode", "value": "Always on"},
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
#: EVERY SANCTIONED ACTION WITH AN OPAQUE TARGET, not just the refusing ones.
#:
#: THIS WAS DERIVED FROM ``SEVEN`` UNTIL 2026-09-01 AND THAT WENT SILENTLY
#: EMPTY. ``react_to_item`` and ``send_invitation`` are the only two opaque
#: kinds there are, both shipped that day, both left ``SEVEN`` -- and the
#: three tests parametrized over this tuple stopped running. pytest reported
#: them as SKIPPED with "got empty parameter set", which in a run of 2361
#: passing tests reads exactly like a pass.
#:
#: The checks below are about how an opaque TARGET is normalised, which has
#: nothing to do with whether the action performs. Scoping them to the
#: refusing set was always wrong; it only became visible when the set emptied.
OPAQUE_ACTIONS = tuple(
    spec.action
    for spec in SANCTIONED_WRITES.values()
    if spec.target_kind in writes._OPAQUE_TARGET_KINDS
)


def test_no_parametrized_corpus_in_this_file_is_empty():
    """A parametrized test over an empty tuple SKIPS, and a skip reads as a pass.

    This is the guard for the failure that produced the comment above: three
    checks stopped running and nothing said so louder than one grey line. Any
    tuple this file fans out over must be non-empty, asserted by name so the
    failure says WHICH corpus emptied.
    """
    for name, corpus in (
        ("SEVEN", SEVEN),
        ("OPAQUE_ACTIONS", OPAQUE_ACTIONS),
        ("COMPOSITE_ACTIONS", COMPOSITE_ACTIONS),
        ("TWO_PART_ACTIONS", TWO_PART_ACTIONS),
        ("COMPONENT_CASES", COMPONENT_CASES),
    ):
        assert corpus, (
            "%s is empty, so every test parametrized over it now SKIPS "
            "instead of running. That is not coverage." % name
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
    block = await preview(
        spec,
        target=TARGETS[action],
        navigator=nav,
        page=page,
        to_state=TO_STATES.get(action),
    )
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

    # THE MAPPING, NOT THE CANONICAL STRING, and the change is what the tool
    # actually does. ``consume`` normalises through ``_target_for`` since
    # 2026-08-31, so it takes what the TOOL took -- which is the only way its
    # normalisation and ``mint``'s can be the same one. This handed it a
    # pre-canonicalised string until then, which is a shape no caller in this
    # server produces: ``_write_tool`` passes the mapping straight through.
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(
            grant.token,
            action="comment_on_item",
            target={"item": ITEM, "text": COMMENT_B},
        )
    message = str(excinfo.value)
    assert "was minted for target" in message, message
    assert "already-discarded" not in message, message
    assert COMMENT_B in message, message

    # THE POSITIVE CASE. Without it the refusal above passes on a consume that
    # refuses everything, which is the exact shape this file exists to avoid.
    redeemed = consume(
        grant.token,
        action="comment_on_item",
        target={"item": ITEM, "text": COMMENT_A},
    )
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
    # THIS PINNED THE OLD WARNING UNTIL 2026-09-01: "if either is ever made
    # performable, THIS FUNCTION IS THE FIRST THING THAT MUST CHANGE".
    # react_to_item became performable and the function did NOT have to
    # change -- the warning aimed at the wrong place. What replaced it is an
    # executable rule in tests/test_opaque_targets.py: an opaque-kind action
    # that becomes performable must either keep its target out of the url
    # entirely, or carry a url_pattern that provably REFUSES a garbage
    # target. A warning became a check, which is the only honest upgrade.
    assert "STOPPED BEING TRUE" in doc
    assert "URL_PATTERN" in doc


# ``test_an_opaque_target_still_cannot_reach_a_grant`` WAS HERE AND WAS
# REMOVED ON 2026-09-01, because its premise stopped being true rather than
# because it became inconvenient. It asserted that no opaque-kind action could
# obtain a grant, and its stated reason was the one ``_opaque_target``'s
# docstring gave: neither held a ``url_template``, so ``mint`` refused at
# issue. Both shipped that day. The test would have to be SOFTENED to pass
# now, and a check softened to accommodate a capability has stopped being one.
#
# WHAT REPLACED IT IS STRONGER AND LIVES IN ``tests/test_opaque_targets.py``:
# an opaque target no longer needs to be unreachable, it needs to be
# CONSTRAINED. Every performable opaque-kind action must either keep its
# target out of the url entirely -- absolute for a NEEDLE, which has no shape
# to enforce -- or carry a ``url_pattern`` proven to REFUSE a garbage target
# AND proven to still admit a real one. Both directions are asserted and both
# were shown failing at mutations before being accepted.
#
# Recorded here rather than left as a deleted line, because a test that
# vanished and a test that was superseded look identical in a diff.


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
    # SIX SURFACES AND SIX REFUSING ACTIONS PLUS THE LIFTED ONE, reconciled
    # rather than counted. ``update_setting`` left ``SEVEN`` when it shipped
    # and its surface did NOT leave ``_SURFACE_READS`` -- ``observe`` still
    # reads that page at preview, so the claim being made here still has to
    # hold for it. Dropping it from this reconciliation would have quietly
    # stopped checking the read boundary for the one action that now performs
    # on it, which is exactly backwards.
    assert len(writes._SURFACE_READS) == 6
    covered = set(SEVEN) | set(LIFTED)
    assert {spec_for_action(a).state_from for a in covered} == set(
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


# ---------------------------------------------------------------------------
# 8. Aiming ONE invitation control, and the name that never reaches Python
# ---------------------------------------------------------------------------
#
# RULED 2026-08-31: this server MAY receive a person's identity as a call-time
# argument and MUST NOT persist it -- no identity in any file, log, cache or
# audit. Everything in this section exists to make the second half of that
# ENFORCEABLE rather than promised, and the load-bearing test is
# ``test_no_planted_name_survives_into_python``: it plants names in a page,
# runs the real reader over it, and asserts that nothing which comes back
# contains any fragment of them.
#
# THAT TEST HAS BEEN SHOWN FAILING. With ``INVITE_NEEDLE_JS`` altered to put
# the matched label in its return value, it reports the leak by name. The
# receipt is in ``_audit/_slice-invitation-needle.md``; without it this whole
# section would be a set of assertions about a mechanism nobody had ever seen
# break, which is the shape that certifies nothing.
#
# WHAT IS *NOT* TESTED HERE, because it does not exist: no click, no anchor, no
# grant. ``send_invitation`` still refuses, sections 1 through 7 above still
# certify that it cannot hold a grant, and this section adds a READER and a
# DECISION, not a route. The index it produces is re-derivable on demand and
# is deliberately not stored anywhere, so nothing can act on a stale one.

#: The measured suffix, and the ONLY thing about these labels this server has
#: ever read. The prefixes below are INVENTED AND DELIBERATELY INCONSISTENT --
#: one bare name, one lowercase, one a strict superstring of another -- so no
#: assertion in this section can come to depend on a prefix form. LinkedIn's
#: real prefix has never been observed and is not guessed here or anywhere
#: else in this package.
#:
#: Every name is nonsense on purpose. ``tests/test_no_committed_identity.py``
#: cannot detect a personal name -- names have no shape -- so the protection
#: against a real one landing in a fixture is that the fixture is written to be
#: obviously synthetic, and these are.
UNIQUE_NAME = "Marigold Underbough"
SHARED_NAME = "Quill Featherstone"
SHARED_LONGER = "Quill Featherstone the Younger"
LOWER_NAME = "tobias winterbottom"
DECOY_NAME = "Pemberley Voss"

#: Every planted name, for the leak sweep. Swept as WORDS as well as whole
#: strings: a reader that returned only a surname would still have collected
#: one, and a whole-string check would call that clean.
PLANTED_NAMES = (
    UNIQUE_NAME, SHARED_NAME, SHARED_LONGER, LOWER_NAME, DECOY_NAME,
)

#: The control that must NOT be counted. Its label ends in something else
#: entirely, so it is not part of the suffix-matched list and cannot be aimed
#: at even by a needle that names it. Without this row every count below would
#: pass against a reader that had dropped the suffix predicate altogether.
DECOY_SUFFIX = " to send a message"

#: Five controls, four of which wear the suffix. The order is the thing the
#: index is an index INTO, so it is fixed here and asserted before use.
INVITE_MARKUP = (
    "<html><body>"
    '<button aria-label="' + SHARED_NAME + dom.INVITE_CONTROL_SUFFIX + '"></button>'
    '<button aria-label="' + UNIQUE_NAME + dom.INVITE_CONTROL_SUFFIX + '"></button>'
    '<button aria-label="' + DECOY_NAME + DECOY_SUFFIX + '"></button>'
    '<button aria-label="' + LOWER_NAME + dom.INVITE_CONTROL_SUFFIX + '"></button>'
    '<button aria-label="' + SHARED_LONGER + dom.INVITE_CONTROL_SUFFIX + '"></button>'
    "</body></html>"
)

#: Suffix-matched controls in the markup above, and where each sits. Written
#: down rather than derived from the reader, so the reader is compared against
#: the markup instead of against itself.
SUFFIX_CONTROLS = 4
POSITION_OF_UNIQUE = 1
POSITION_OF_LOWER = 2

#: A page with the suffix nowhere on it. The zero-match case above is "nobody
#: matched"; this is "there is nothing here at all", and they are different
#: refusals that a single fixture would have collapsed into one.
BARE_MARKUP = '<html><body><button aria-label="Nothing at all"></button></body></html>'

#: Fixed width, asserted on every reading. Nothing this reader answers is
#: laid-out -- it counts attributes -- but a measurement whose conditions were
#: not recorded is a measurement that cannot be repeated, and the cost is one
#: integer comparison.
INVITE_VIEWPORT = {"width": 1280, "height": 900}


@pytest.fixture
async def over_invites():
    """One browser, a FRESH ISOLATED CONTEXT per reading.

    The pattern is ``tests/test_apply_modal_fixture.py``'s, for its stated
    reason: the launch is what costs, so paying it once per test and taking
    the isolation per MEASUREMENT is both cheaper and stricter than a page
    shared across readings.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(html: str, work):
            context = await browser.new_context(viewport=dict(INVITE_VIEWPORT))
            try:
                page = await context.new_page()
                await page.set_content(
                    html, wait_until="domcontentloaded", timeout=60_000
                )
                width = await page.evaluate("window.innerWidth")
                assert width == INVITE_VIEWPORT["width"], (
                    f"the page laid out at {width}px, not "
                    f"{INVITE_VIEWPORT['width']}px -- the reading below was "
                    "taken under conditions nobody recorded."
                )
                return await work(page)
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


async def _read(runner, needle, html=INVITE_MARKUP):
    """One reading of the real reader, over frozen markup."""
    return await runner(html, lambda page: dom.read_invitation_surface(page, needle))


# --- the fixture is the shape every assertion below assumes ----------------


def test_the_invitation_fixture_is_the_shape_this_section_assumes():
    """Pins the markup, so a later edit degrades tests loudly instead of quietly.

    The ambiguity case is only a test of ambiguity while two labels genuinely
    share a substring, and the decoy is only a test of the suffix predicate
    while its label genuinely ends in something else. Both are checked here
    rather than assumed where they are used.
    """
    assert INVITE_MARKUP.count(dom.INVITE_CONTROL_SUFFIX + '"') == SUFFIX_CONTROLS
    assert DECOY_SUFFIX in INVITE_MARKUP
    assert not DECOY_SUFFIX.endswith(dom.INVITE_CONTROL_SUFFIX)
    # The ambiguity is a real one: SHARED_NAME is a strict prefix of the other.
    assert SHARED_LONGER.startswith(SHARED_NAME) and SHARED_LONGER != SHARED_NAME
    # And the case-insensitivity case is real: the label is not title case.
    assert LOWER_NAME != LOWER_NAME.title()
    assert dom.INVITE_CONTROL_SUFFIX not in BARE_MARKUP


# --- the reader ------------------------------------------------------------


async def test_a_unique_needle_aims_at_exactly_one_control(over_invites):
    """The only aimable state, and the index is the aim."""
    reading = await _read(over_invites, UNIQUE_NAME)
    assert reading["controls"] == SUFFIX_CONTROLS
    assert reading["matches"] == 1
    assert reading["index"] == POSITION_OF_UNIQUE
    assert writes.aim_invitation(reading)[0] == writes.INVITE_AIMED
    assert writes.aim_invitation(reading)[2] == POSITION_OF_UNIQUE


async def test_a_needle_nobody_carries_matches_nothing_and_aims_at_nothing(
    over_invites,
):
    """Zero is a READ answer: the question was put and nobody carried it."""
    reading = await _read(over_invites, "Nobody Whatsoever")
    assert reading["controls"] == SUFFIX_CONTROLS
    assert reading["matches"] == 0
    assert reading["index"] is None
    state, why, index = writes.aim_invitation(reading)
    assert state == writes.INVITE_NO_MATCH
    assert index is None
    assert str(SUFFIX_CONTROLS) in why


async def test_two_matches_are_ambiguous_and_the_aim_is_erased(over_invites):
    """THE REFUSAL THAT MATTERS. Two controls, no way to tell them apart.

    ``SHARED_NAME`` is a strict prefix of ``SHARED_LONGER``, which is exactly
    how this goes wrong in the world: a needle that looks specific matches a
    second person whose name merely extends it. Picking either would be
    picking by position.
    """
    reading = await _read(over_invites, SHARED_NAME)
    assert reading["matches"] == 2
    assert reading["index"] is None, "an index survived an ambiguous read"
    state, why, index = writes.aim_invitation(reading)
    assert state == writes.INVITE_AMBIGUOUS
    assert index is None
    assert "position" in why


async def test_the_match_is_case_insensitive(over_invites):
    """Folded on BOTH sides, and the second half is why this is two cases.

    Written first with only the top half, this test could not fail. Both
    needles there are variations of a label that is ALREADY lowercase, so
    folding the NEEDLE alone satisfies them -- and a mutation that removed the
    fold from the LABEL side left the suite green. The bottom half is the
    control: an uppercase label reached by a lowercase needle can only match
    if the label is folded too.
    """
    # A lowercase label, reached by needles that are not.
    for needle in (LOWER_NAME.upper(), LOWER_NAME.title()):
        reading = await _read(over_invites, needle)
        assert reading["matches"] == 1, needle
        assert reading["index"] == POSITION_OF_LOWER, needle
    # A title-case label, reached by a lowercase needle. THIS is the half that
    # exercises the fold on the label.
    assert UNIQUE_NAME != UNIQUE_NAME.lower(), "the control needs a cased label"
    reading = await _read(over_invites, UNIQUE_NAME.lower())
    assert reading["matches"] == 1
    assert reading["index"] == POSITION_OF_UNIQUE


async def test_a_control_ending_differently_is_neither_counted_nor_aimable(
    over_invites,
):
    """The suffix predicate, shown doing work.

    The decoy is on the page and carries a name. It is absent from the count,
    and a needle naming it directly still matches nothing -- so the suffix is
    a filter on the SET, not merely on what gets reported.
    """
    reading = await _read(over_invites, DECOY_NAME)
    assert reading["controls"] == SUFFIX_CONTROLS, "the decoy was counted"
    assert reading["matches"] == 0, "the decoy was aimable"
    assert writes.aim_invitation(reading)[0] == writes.INVITE_NO_MATCH


async def test_a_surface_drawing_no_invitation_control_reads_zero(over_invites):
    """Nothing here at all, which is a different answer from nobody matched."""
    reading = await _read(over_invites, UNIQUE_NAME, html=BARE_MARKUP)
    assert reading == {
        "controls": 0,
        "matches": 0,
        "index": None,
        "label": None,
    }


async def test_no_needle_is_a_count_only_and_says_it_did_not_look(over_invites):
    """The unchanged path: no needle, no comparison, and ``None`` says so.

    ``matches is None`` and ``matches == 0`` are DIFFERENT ANSWERS and this is
    what keeps them apart -- one means nobody asked, the other means nobody
    carried it. A reader that returned 0 for both would let the aiming rule
    report a confident "nobody matched" about a question never put.
    """
    reading = await over_invites(
        INVITE_MARKUP, lambda page: dom.read_invitation_surface(page)
    )
    assert reading == {
        "controls": SUFFIX_CONTROLS,
        "matches": None,
        "index": None,
        # ``None`` for TWO reasons here and either alone is enough: nobody
        # asked for a label, and no needle was given for one to be selected
        # by. ``matches: None`` is itself the "nobody asked" answer, which is
        # a different fact from a zero.
        "label": None,
    }
    state, why, index = writes.aim_invitation(reading)
    assert state == writes.INVITE_UNASKED
    assert index is None
    assert "not an aim" in why


async def test_an_empty_needle_is_not_a_needle(over_invites):
    """A blank string is a substring of every label. It is refused as unasked.

    Passed through, it would report four matches on four controls -- true,
    useless, and indistinguishable from a genuine ambiguity. Reported as
    ``None`` it stays separable from both.
    """
    for blank in ("", "   ", "\t"):
        reading = await _read(over_invites, blank)
        assert reading["matches"] is None, repr(blank)
        assert writes.aim_invitation(reading)[0] == writes.INVITE_UNASKED


async def test_the_css_suffix_selector_and_the_scripts_endswith_agree(over_invites):
    """The two predicates are written in different languages. They must agree.

    ``controls`` comes from a Playwright locator over a CSS ``$=`` selector
    when no needle is given, and from the script's own ``endsWith`` when one
    is. Nothing else compares them, so a drift between the CSS engine and the
    script would silently change which controls an index is an index into.
    """
    without = await over_invites(
        INVITE_MARKUP, lambda page: dom.read_invitation_surface(page)
    )
    with_needle = await _read(over_invites, UNIQUE_NAME)
    assert without["controls"] == with_needle["controls"] == SUFFIX_CONTROLS


# --- THE TESTS THAT CERTIFY THE RULING -------------------------------------


class _RecordingPage:
    """A real page whose ``evaluate`` RETURN VALUES are kept verbatim.

    WHY A SPY AND NOT JUST THE READER'S OUTPUT. The ruling is that a third
    party's name must never enter this process -- not that the reader must
    decline to forward one. Those are different claims, and the difference is
    not academic: it was measured. With the script altered to return the
    matched label, ``test_no_planted_name_survives_into_python`` below STAYED
    GREEN, because the reader copies three fields out of the payload and drops
    the rest. The name had crossed the boundary and was sitting in a local
    variable; the only test watching was looking one step too late.

    This watches the boundary itself. Everything ``evaluate`` hands back is
    recorded before the reader gets to filter it.
    """

    def __init__(self, page):
        self._page = page
        self.returned: list = []

    def __getattr__(self, name):
        return getattr(self._page, name)

    async def evaluate(self, script, arg=None):
        value = await self._page.evaluate(script, arg)
        self.returned.append(value)
        return value


async def test_nothing_carrying_a_name_crosses_out_of_the_page(over_invites):
    """THE RULING AS AN ASSERTION, taken AT THE BOUNDARY.

    Whatever the script hands back is what entered Python. It must contain no
    planted name, no fragment of one, and no echo of the needle -- and it must
    contain something, or this is a test of a reader that never ran.
    """

    async def work(page):
        spy = _RecordingPage(page)
        reading = await dom.read_invitation_surface(spy, UNIQUE_NAME)
        return reading, list(spy.returned)

    reading, crossed = await over_invites(INVITE_MARKUP, work)
    assert crossed, "the reader executed no script, so nothing was certified"
    assert reading["matches"] == 1, reading
    blob = repr(crossed)
    for name in PLANTED_NAMES:
        assert name not in blob, f"{name!r} crossed out of the page: {blob}"
        for word in name.split():
            if len(word) < 4:
                continue
            assert word not in blob, (
                f"the fragment {word!r} of a planted name crossed out of the "
                f"page: {blob}"
            )
    assert UNIQUE_NAME not in blob, f"the needle was echoed back: {blob}"
    # Every value that crossed is a number or nothing. A label is neither.
    for payload in crossed:
        assert isinstance(payload, dict), payload
        for key, value in payload.items():
            assert isinstance(value, (int, bool, type(None))), (
                f"the script returned {key}={value!r}, a "
                f"{type(value).__name__}. Only integers may cross."
            )


async def test_no_planted_name_survives_into_python(over_invites):
    """NOTHING THAT COMES BACK CONTAINS ANY FRAGMENT OF A PLANTED NAME.

    This is the whole ruling as an assertion. Every other test here would pass
    against a reader that fetched all four labels, compared them in Python and
    returned the right numbers -- and that reader would have collected four
    strangers' names into a process that logs, caches and renders. This one
    would not.

    It sweeps the WHOLE returned structure as text, and it sweeps individual
    WORDS as well as whole names, because a reader that returned only a
    surname has still collected one.
    """
    for needle in (UNIQUE_NAME, SHARED_NAME, "Nobody Whatsoever", DECOY_NAME):
        reading = await _read(over_invites, needle)
        blob = repr(reading)
        for name in PLANTED_NAMES:
            assert name not in blob, f"the reader returned {name!r}: {blob}"
            for word in name.split():
                if len(word) < 4:
                    continue
                assert word not in blob, (
                    f"the reader returned the fragment {word!r} of a planted "
                    f"name: {blob}"
                )
        # AND THE NEEDLE ITSELF IS NOT ECHOED. It is his to type, not this
        # server's to keep, and a result that carried it would be a result a
        # caller could store without ever deciding to.
        assert needle not in blob, f"the reading echoed the needle: {blob}"


async def test_only_numbers_come_back(over_invites):
    """The return shape, enforced by TYPE rather than by reading the source.

    A label is a string. If every value that crosses the boundary is an int,
    a bool or ``None``, then no label crossed it -- which is a stronger claim
    than any assertion about particular keys, and it survives somebody adding
    a field.
    """
    for needle in (UNIQUE_NAME, SHARED_NAME, "Nobody Whatsoever", None):
        reading = await _read(over_invites, needle)
        for key, value in reading.items():
            assert isinstance(value, (int, bool, type(None))), (
                f"{key} came back as {type(value).__name__}, and only "
                f"integers cross this boundary: {value!r}"
            )


def test_the_script_emits_a_label_only_behind_two_conditions():
    """Read the script itself: WHEN it may hand back a label, and when not.

    THIS TEST ASSERTED THAT IT NEVER COULD, and that property was deliberately
    changed by the operator on 2026-08-31 rather than eroded. So it is
    REWRITTEN to assert the new, narrower thing rather than deleted -- a guard
    that is removed when its subject moves leaves nothing behind, and this is
    the line in this package that can emit a third party's name.

    THE RULING, and the distinction it turned on: loading a stranger's PROFILE
    stays refused because it EMITS -- ``linkedin_who_viewed_me`` measures the
    receiving end -- so the cost falls on somebody who did not agree to it.
    Reading one accessible name off a page already rendered on HIS OWN profile
    emits nothing at all. And he already knows the name: he supplied the
    needle, so reading the label back CONFIRMS that the control his own word
    selected is the person he meant, which is verification of his input rather
    than collection.

    TWO CONDITIONS IN THE SCRIPT, ``&&``-ed rather than nested, and a THIRD in
    Python. Three gates in two languages, so no single edit opens them all.
    """
    js = dom.INVITE_NEEDLE_JS
    # The caller has to ask, AND the needle has to have picked out one.
    assert "cfg.revealSingleMatch === true" in js
    assert "(matches === 1)" in js
    assert "const reveal = (cfg.revealSingleMatch === true) && (matches === 1)" in js
    # And the emission is that flag, not the label directly.
    assert "label: reveal ? only : null" in js
    # A SECOND MATCH ERASES IT, exactly as it erases the index. There is
    # nothing to check if the word picked out two people.
    assert "only = (matches === 1) ? label : null;" in js
    # Still counted, still never pushed to an array or accumulated.
    assert "out.push" not in js
    # And the suffix is matched AS A SUFFIX -- never rebuilt into a whole
    # label from a prefix nobody has measured.
    assert "endsWith(cfg.suffix)" in js


async def test_the_label_is_withheld_unless_the_caller_asks(browser_page):
    """THE DEFAULT IS OFF, and the default is what every existing caller gets.

    ``read_invitation_surface`` grew a keyword rather than changing behaviour,
    so the reader the gate uses -- which must never hold a name, because its
    answer becomes a retained Observation -- is unaffected by the ruling.
    """
    await browser_page.set_content(PROFILE_MARKUP)
    off = await dom.read_invitation_surface(browser_page, MEMBER)
    assert off["matches"] == 1
    assert off["label"] is None, off

    on = await dom.read_invitation_surface(
        browser_page, MEMBER, reveal_single_match=True
    )
    assert on["matches"] == 1
    assert on["label"] and MEMBER in on["label"], on


async def test_two_matches_erase_the_label_even_when_asked(browser_page):
    """CONDITION 1 OF THE RULING: exactly ONE label, the one the needle
    uniquely selected. Zero or more than one reads nothing.

    A word matching two controls is precisely the case where a name would be
    least safe to print and most tempting to print anyway -- he would see one
    of two people and confirm against it.
    """
    two = PROFILE_MARKUP.replace(
        "</body>",
        '<button aria-label="Invite Somebody Else'
        + dom.INVITE_CONTROL_SUFFIX
        + '"></button></body>',
    )
    assert two != PROFILE_MARKUP
    await browser_page.set_content(two)
    reading = await dom.read_invitation_surface(
        browser_page, MEMBER, reveal_single_match=True
    )
    assert reading["matches"] == 2
    assert reading["label"] is None, reading
    assert reading["index"] is None


# --- the aiming rule, without a browser ------------------------------------


@pytest.mark.parametrize(
    "reading,expected",
    [
        ({"controls": 9, "matches": None, "index": None}, "no_needle"),
        ({"controls": 9, "matches": 0, "index": None}, "no_match"),
        ({"controls": 9, "matches": 2, "index": None}, "ambiguous"),
        ({"controls": 9, "matches": 9, "index": None}, "ambiguous"),
        # TWO MATCHES *AND* AN INDEX, and this row exists because without it
        # this whole parametrisation had a case that could not fail. The
        # script erases the index on a second match, so every ambiguous
        # reading it produces carries ``index: None`` -- which means the
        # ambiguity refusal here was being satisfied by the missing-index
        # guard further down rather than by the count check it is testing.
        # Weakening ``matches > 1`` left the suite green. It does not now.
        ({"controls": 9, "matches": 2, "index": 3}, "ambiguous"),
        ({"controls": 9, "matches": 1, "index": 0}, "aimed"),
        ({"controls": 9, "matches": 1, "index": 8}, "aimed"),
        # ONE MATCH AND NO POSITION, which the script cannot produce and a
        # hand-built or half-read dict can. The safe answer is the ambiguous
        # refusal, never a guess at position 0.
        ({"controls": 9, "matches": 1, "index": None}, "ambiguous"),
    ],
)
def test_the_aiming_rule_is_exactly_one_or_nothing(reading, expected):
    state, why, index = writes.aim_invitation(reading)
    assert state == expected, why
    assert (index is not None) == (expected == "aimed"), why
    if index is not None:
        assert index == reading["index"]


def test_no_aiming_verdict_can_carry_a_name():
    """The signature is the enforcement: this function never sees a needle.

    Asserted rather than merely stated, because "it takes a dict of integers"
    is a property somebody could break by adding a convenience argument, and
    the first thing such an argument would be used for is a friendlier
    message.
    """
    import inspect

    parameters = list(inspect.signature(writes.aim_invitation).parameters)
    assert parameters == ["reading"], parameters
    for matches in (None, 0, 1, 2, 9):
        reading = {"controls": 9, "matches": matches, "index": 3}
        why = writes.aim_invitation(reading)[1]
        for name in PLANTED_NAMES:
            assert name not in why
        assert why == why.strip()


# ---------------------------------------------------------------------------
# 8. THE ONE THAT LIFTED: update_setting, end to end
# ---------------------------------------------------------------------------
#
# Everything above this line asserts a refusal, and a file of refusals passes
# perfectly against a gate that raises unconditionally. This section is the
# one that fails if the capability goes back to being a preview.
#
# IT PERFORMS NOTHING ON LINKEDIN. The navigator is a fixture server over
# frozen markup and the page is a fake; what is being exercised is this
# server's own gate chain -- observe, mint, consume, perform, verify -- over
# markup shaped like the six agreeing readings of the live page.


#: The same three radios with ``Always on`` CHECKED instead of ``Always off``:
#: the world as it would be AFTER the click. Built by moving the attribute
#: rather than by editing the whole string, and ASSERTED to have moved, so a
#: fixture that silently failed to change could not pass for one that did.
DARK_MODE_AFTER = DARK_MODE_MARKUP.replace(
    '<input type="radio" name="dm" aria-labelledby="dm-off" checked>',
    '<input type="radio" name="dm" aria-labelledby="dm-off">',
).replace(
    '<input type="radio" name="dm" aria-labelledby="dm-on">',
    '<input type="radio" name="dm" aria-labelledby="dm-on" checked>',
)
assert DARK_MODE_AFTER != DARK_MODE_MARKUP
assert DARK_MODE_AFTER.count("checked") == 1


class _ClickRecordingPage:
    """A page that records the selector it was clicked with, then swaps the
    markup underneath it.

    THE SWAP IS THE POINT. ``perform`` verifies from a FRESH NAVIGATION, so a
    fake that kept serving the before-state would make a successful click
    indistinguishable from one that changed nothing -- and the test would pass
    either way.
    """

    def __init__(self, page, navigator, after: str):
        self._page = page
        self._navigator = navigator
        self._after = after
        self.clicks: list[str] = []

    def __getattr__(self, name):
        return getattr(self._page, name)

    async def click(self, selector, **_kwargs):
        self.clicks.append(selector)
        self._navigator.pages[writes.DARK_MODE_URL] = self._after


async def _setting_grant(nav, page, *, to_state: str = "Always on"):
    """A real, redeemed grant for update_setting. The long way round --
    preview, then consume the token it printed -- because ``perform`` requires
    a grant ``consume`` has already burned."""
    spec = spec_for_action("update_setting")
    block = await preview(
        spec,
        target=TARGETS["update_setting"],
        navigator=nav,
        page=page,
        to_state=to_state,
    )
    grant = consume(
        block["to_confirm"],
        action="update_setting",
        target=TARGETS["update_setting"],
    )
    return block, grant


async def test_update_setting_runs_end_to_end_and_is_verified_from_a_reload(
    writes_on, browser_page
):
    """THE POSITIVE CASE for the first capability lifted in this wave.

    Every gate in the chain is real: the direction is read off the page, the
    token is minted only from that reading, ``consume`` burns it, ``perform``
    re-reads the control before clicking, and the verification is a FRESH
    NAVIGATION and a re-read of the group's own ``checked`` property.

    WHAT MAKES THE VERDICT WORTH ANYTHING is the last of those. The fixture
    served after the click has ``Always on`` checked and ``Always off`` not,
    so ``performed: True`` is a statement about a re-read page rather than
    about the click having returned without raising.
    """
    nav = FixtureNavigator(_nine_pages())
    block, grant = await _setting_grant(nav, browser_page)

    # A TOKEN NOW EXISTS FOR THIS ACTION, which is the whole of what changed.
    assert block["to_confirm"], block
    assert block["direction"]["currently"] == "Always off"
    assert block["direction"]["after"] == "Always on"
    # The operator is shown the three controls and which one is on.
    shown = block["where"]["what_the_page_showed"]["rows"]
    assert {row["shape"] for row in shown} == set(writes.DARK_MODE_STATES)
    assert [row["shape"] for row in shown if row["checked"]] == ["Always off"]
    assert {row["input_type"] for row in shown} == {"radio"}
    # ``role`` IS ON THE ROW, and it is asserted because it was MISSING when
    # this projection was written -- dom.aria_role_of consults it first, so
    # every control was being answered as though it had no role attribute.
    # The mutation that narrows the role guard is what surfaced it.
    assert {row["role"] for row in shown} == {None}

    page = _ClickRecordingPage(browser_page, nav, DARK_MODE_AFTER)
    result = await writes.perform(nav, page, grant)

    # THE SELECTOR IS BUILT FROM THE ROLE THE PAGE REPORTED, not an assumed
    # one. That is what ``input_type`` was added to the census for.
    assert page.clicks == ['role=radio[name="Always on"][exact=true]'], page.clicks
    assert result["performed"] is True, result
    assert result["verified"] is True
    assert result["verification"]["observed_state"] == "Always on"
    assert result["verification"]["expected_state"] == "Always on"
    assert writes.DARK_MODE_URL in result["verification"]["read_from"]
    # AND THE BLOCK DOES NOT CLAIM A SECOND SURFACE IT DOES NOT HAVE. There is
    # exactly one page for a setting; the sentence beside the verdict says so
    # rather than borrowing the save pair's "a DIFFERENT surface", which it
    # did until this action shipped.
    assert "THE SAME PAGE, RELOADED" in result["verification"]["surface"]
    assert "saved list" not in result["verification"]["surface"]


async def test_a_setting_that_did_not_move_reports_false_rather_than_unknown(
    writes_on, browser_page
):
    """THE NEGATIVE HALF, and it is the one that pins ``expected_after``.

    A click that changed nothing must report ``performed: False`` -- he is
    told it did not happen -- and not ``"unknown"``, which sends him off to
    look at a page that is exactly as he left it. The two were the SAME answer
    until 2026-08-31, because the comparison ran against ``spec.to_state``,
    which is ``None`` for a multi-state action: every outcome fell through to
    unknown, INCLUDING a change that landed perfectly.
    """
    nav = FixtureNavigator(_nine_pages())
    _block, grant = await _setting_grant(nav, browser_page)
    # The world does NOT change: the after-markup is the before-markup.
    page = _ClickRecordingPage(browser_page, nav, DARK_MODE_MARKUP)
    result = await writes.perform(nav, page, grant)
    assert result["performed"] is False, result
    assert result["verified"] is False
    assert result["verification"]["observed_state"] == "Always off"


async def test_perform_refuses_a_destination_the_setting_is_already_in(
    writes_on, browser_page
):
    """GATE 5 IS FRESHER THAN THE PREVIEW, on a setting where that matters.

    The preview's reading may be up to two minutes old and he may have moved
    the setting in another tab. So the origin is re-checked at click time, and
    a grant whose destination is where the page now already sits is refused
    rather than clicked -- a click there is not harmless, it is a click on a
    control whose meaning changed after he was shown it.

    Reached by minting against one world and performing against another, which
    is the only way to model the gap the check exists to cover.
    """
    nav = FixtureNavigator(_nine_pages())
    _block, grant = await _setting_grant(nav, browser_page)
    # Somebody else moved it in between.
    nav.pages[writes.DARK_MODE_URL] = DARK_MODE_AFTER
    page = _ClickRecordingPage(browser_page, nav, DARK_MODE_AFTER)
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, page, grant)
    assert "already reads" in str(excinfo.value), str(excinfo.value)
    assert page.clicks == []


async def test_an_unreadable_group_refuses_rather_than_choosing_by_position(
    writes_on, browser_page
):
    """TWO CHECKED IS A REFUSAL AT CLICK TIME, not only at preview.

    ``_read_dark_mode`` refuses zero and two-or-more, and gate 5 runs the same
    reader -- so a group that stopped behaving as radios between the preview
    and the click is refused there too. Without this the freshest reading in
    the chain would be the one least able to say no.
    """
    nav = FixtureNavigator(_nine_pages())
    _block, grant = await _setting_grant(nav, browser_page)
    both = DARK_MODE_MARKUP.replace(
        '<input type="radio" name="dm" aria-labelledby="dm-on">',
        '<input type="radio" name="dm" aria-labelledby="dm-on" checked>',
    )
    assert both.count("checked") == 2
    nav.pages[writes.DARK_MODE_URL] = both
    page = _ClickRecordingPage(browser_page, nav, both)
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, page, grant)
    assert "choosing by position" in str(excinfo.value)
    assert page.clicks == []


#: THE SAME THREE CONTROLS AS CHECKBOXES. Not a page LinkedIn is known to
#: serve -- and that is the point rather than a weakness. Six readings
#: establish three CHECKABLE inputs and none of them establishes which of the
#: two checkable types they are, because the census's ``checked`` gate admits
#: radio and checkbox alike. So "they are radios" is an assumption this server
#: must not be making, and the only way to show it is not making one is to
#: serve it the other type and watch the selector follow.
DARK_MODE_AS_CHECKBOXES = DARK_MODE_MARKUP.replace(
    '<input type="radio"', '<input type="checkbox"'
)
assert DARK_MODE_AS_CHECKBOXES.count('type="checkbox"') == 3
assert 'type="radio"' not in DARK_MODE_AS_CHECKBOXES


async def test_a_checkbox_group_is_clicked_as_a_checkbox_not_as_a_radio(
    writes_on, browser_page
):
    """THE ROLE IS READ, AND THIS IS THE CHECK THAT CAN SAY SO.

    ``test_the_role_is_read_off_the_row_and_never_assumed`` exercises
    ``dom.aria_role_of`` directly, which a hardcoded ``role = "radio"`` in
    ``_live_control`` sails straight past -- MEASURED: that mutation left the
    whole file green. A unit test of a helper cannot certify that the helper
    is the thing being called.

    So this serves the same three controls as CHECKBOXES and asserts the
    selector followed. On a radio fixture an assumed role and a read one are
    the same string, and any test built on one alone is certifying nothing.
    """
    nav = FixtureNavigator(_nine_pages())
    nav.pages[writes.DARK_MODE_URL] = DARK_MODE_AS_CHECKBOXES
    _block, grant = await _setting_grant(nav, browser_page)

    after = DARK_MODE_AS_CHECKBOXES.replace(
        '<input type="checkbox" name="dm" aria-labelledby="dm-off" checked>',
        '<input type="checkbox" name="dm" aria-labelledby="dm-off">',
    ).replace(
        '<input type="checkbox" name="dm" aria-labelledby="dm-on">',
        '<input type="checkbox" name="dm" aria-labelledby="dm-on" checked>',
    )
    assert after.count("checked") == 1
    page = _ClickRecordingPage(browser_page, nav, after)
    result = await writes.perform(nav, page, grant)

    assert page.clicks == [
        'role=checkbox[name="Always on"][exact=true]'
    ], page.clicks
    assert result["performed"] is True, result


async def test_a_destination_wearing_an_unmapped_role_refuses_rather_than_raising(
    writes_on, browser_page
):
    """AN UNMAPPED ROLE IS A GATE REFUSAL, not an exception on the way past.

    THE FIRST VERSION OF THIS TEST COULD NOT FIRE THE BRANCH IT WAS WRITTEN
    FOR, and finding that out is what the test was worth. It replaced the
    destination with a TEXT input -- which ``_read_dark_mode`` filters out
    before ``_live_control`` ever sees it, because a text box has no
    ``checked`` at all, so the refusal came from "0 controls are named
    'Always on'" one step earlier. The role branch was unreachable from an
    input of any type: an input has a ``checked`` reading only when it is a
    radio or a checkbox, and both are mapped.

    WHAT CAN ACTUALLY ARRIVE is an element carrying ``aria-checked``. A
    ``div[role=switch]`` named for the destination IS a checkable row whose
    role this package maps nothing from -- so it reaches the branch, and
    without the branch it would reach ``dom.named_role_selector``, which
    RAISES. Safe, and the wrong shape: a raise skips the gate's own
    ``wrong_state_note`` and reports an extraction failure for what is a
    refusal to act.
    """
    nav = FixtureNavigator(_nine_pages())
    _block, grant = await _setting_grant(nav, browser_page)
    # The destination becomes a switch. The other two inputs still carry the
    # group's state, so the reading still settles and the direction still
    # renders -- this isolates the ROLE question and nothing else.
    broken = DARK_MODE_MARKUP.replace(
        '<input type="radio" name="dm" aria-labelledby="dm-on">',
        # A BUTTON rather than a div, and that is not cosmetic: a bare
        # ``div[role=switch]`` matches no arm of CENSUS_CONTROL_SELECTOR and
        # so produces NO ROW AT ALL -- the first attempt at this test used one
        # and refused at "0 controls are named 'Always on'", one step before
        # the branch it was written for. A button is censused, carries
        # aria-checked, and therefore arrives at the role check.
        '<button role="switch" aria-checked="false" aria-labelledby="dm-on">'
        "</button>",
    )
    assert 'role="switch"' in broken
    nav.pages[writes.DARK_MODE_URL] = broken
    page = _ClickRecordingPage(browser_page, nav, broken)
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(nav, page, grant)
    message = str(excinfo.value)
    assert "not a shape this server has seen" in message, message
    assert "switch" in message, message
    assert page.clicks == []


def test_the_anchor_is_the_destination_and_only_a_measured_one():
    """``anchor_label_for`` GAINED A TARGET, and the guard came with it.

    For every other action the anchor is a property of the SPEC. For this one
    the control to click is the one named for the destination, which is
    per-call -- so the parameter exists, and with it the risk that a caller's
    string reaches a selector. It cannot: the destination is matched against
    the three states this server has seen rendered, and anything else returns
    ``None``, which ``perform`` refuses on.
    """
    spec = spec_for_action("update_setting")
    for state in writes.DARK_MODE_STATES:
        canonical = writes._target_for(
            spec, {"setting": "dark-mode", "value": state}
        )
        assert writes.anchor_label_for(spec, canonical) == state
    # Case and spacing normalise to the CANONICAL string, so what reaches the
    # selector is LinkedIn's spelling rather than the caller's.
    loose = writes._target_for(
        spec, {"setting": "dark-mode", "value": "  always ON "}
    )
    assert writes.anchor_label_for(spec, loose) == "Always on"
    # And anything else is refused rather than passed through.
    invented = writes._target_for(
        spec, {"setting": "dark-mode", "value": "Always sepia"}
    )
    assert writes.anchor_label_for(spec, invented) is None
    assert writes.anchor_label_for(spec, "") is None


def test_the_click_selector_refuses_an_unmeasured_role_and_an_unsafe_name():
    """THE OTHER HALF OF THE CLICK, guarded the way the url is.

    ``assert_write_url`` rebuilds the url from the grant so a caller cannot
    influence it. This is the same discipline on the selector: the ROLE must
    be one this package maps from a measured control type, and the NAME may
    not carry a character that would end the selector's own quoting. Both
    REFUSE rather than escape -- an escaping rule is a thing to get subtly
    wrong, and what a wrong one produces here is a click on a different
    control.
    """
    assert (
        dom.named_role_selector("radio", "Always on")
        == 'role=radio[name="Always on"][exact=true]'
    )
    for bad_role in ("button", "link", "", "RADIO"):
        with pytest.raises(Exception):
            dom.named_role_selector(bad_role, "Always on")
    for bad_name in ('Always "on"', "Always on]", "", "Always\non"):
        with pytest.raises(Exception):
            dom.named_role_selector("radio", bad_name)


def test_the_role_is_read_off_the_row_and_never_assumed():
    """AN INPUT'S ROLE IS ITS TYPE'S, and an unmeasured type has none here.

    Six readings of the live dark-mode page establish three checkable inputs
    and NONE of them establishes which of the two checkable types they are --
    the census's ``checked`` gate admits radio and checkbox alike. So the role
    is read at click time, and a type this package has not mapped returns
    ``None`` rather than a plausible default.
    """
    assert dom.aria_role_of({"tag": "input", "input_type": "radio"}) == "radio"
    assert (
        dom.aria_role_of({"tag": "input", "input_type": "checkbox"}) == "checkbox"
    )
    # An explicit role attribute wins, because it is what the browser honours.
    assert (
        dom.aria_role_of({"tag": "div", "role": "radio", "input_type": None})
        == "radio"
    )
    # And the refusals. ``None`` means THIS READER WILL NOT NAME IT, which is
    # not "this element has no role" -- every rendered element has one.
    assert dom.aria_role_of({"tag": "input", "input_type": "text"}) is None
    assert dom.aria_role_of({"tag": "input", "input_type": None}) is None
    assert dom.aria_role_of({"tag": "button", "input_type": None}) is None


def test_consume_normalises_its_target_the_way_mint_did(writes_on):
    """ONE NORMALISER, BOTH DOORS -- and this is the defect it closed.

    ``consume`` compared ``grant.target`` against ``str(target)``, raw, while
    ``mint`` had stored a value put through ``_target_for``. For a job id the
    two agree, because normalising one is a strip. FOR A COMPOSITE TARGET THEY
    NEVER CAN: ``mint`` stores ``"dark-mode :: Always on"`` and the tool layer
    hands ``consume`` a mapping, whose ``str()`` is its repr. Every composite
    action's token was unredeemable BY CONSTRUCTION -- not refused for a
    reason, just never equal -- and nothing caught it, because no composite
    action could reach ``mint`` either.
    """
    spec = spec_for_action("update_setting")
    canonical = writes._target_for(spec, TARGETS["update_setting"])
    assert TARGET_JOIN in canonical
    # The shape the TOOL passes, which is the one that used to fail.
    assert str(TARGETS["update_setting"]) != canonical

    grant = _bare_grant(action="update_setting", target=canonical)
    writes._GRANTS[grant.token] = grant
    redeemed = consume(
        grant.token, action="update_setting", target=TARGETS["update_setting"]
    )
    assert redeemed.target == canonical
    assert redeemed.consumed is True


# ---------------------------------------------------------------------------
# 9. THE GRANT SWEEPER
# ---------------------------------------------------------------------------


def test_an_expired_grant_is_dropped_rather_than_held_for_the_process(
    writes_on, monkeypatch
):
    """THE TTL BOUNDED WHEN A GRANT COULD BE USED, NOT HOW LONG IT WAS HELD.

    A grant was written at ``mint`` and removed only by ``consume`` or
    ``discard_all`` -- no timer, no task, no ``atexit`` -- so a minted and
    never-confirmed grant kept its target in process memory for the life of
    the process, long after the token had stopped working.

    IT MATTERS MORE FROM 2026-08-31 THAN IT DID BEFORE, which is why it is
    fixed now rather than noted again. Until today no composite action could
    be granted at all, so every held target was a job id or a company id.
    ``update_setting`` is performable, so a PREVIEW mints -- and previews are
    the common case while confirmations are the rare one. Held targets are
    about to be the normal state.
    """
    writes.discard_all()
    stale = _bare_grant(action="save_job", target="4600000042")
    writes._GRANTS[stale.token] = stale
    assert stale.token in writes._GRANTS

    # Age it past the TTL by moving the clock, not by sleeping.
    now = [stale.minted_at + writes.GRANT_TTL_SECONDS + 1.0]
    monkeypatch.setattr(writes.time, "monotonic", lambda: now[0])
    assert stale.expired()
    # STILL HELD until something sweeps: this is the state the fix is about.
    assert stale.token in writes._GRANTS

    assert writes._sweep_expired_grants() == 1
    assert stale.token not in writes._GRANTS
    # AND IT IS NOT A CLEAR-ALL. A live grant beside a dead one survives, or
    # the "sweeper" is just discard_all wearing a gentler name.
    live = _bare_grant(action="save_job", target="4600000043")
    live.minted_at = now[0]
    writes._GRANTS[live.token] = live
    assert writes._sweep_expired_grants() == 0
    assert live.token in writes._GRANTS
    writes.discard_all()


def test_minting_sweeps_what_previous_previews_left_behind(
    writes_on, monkeypatch
):
    """THE SWEEP RUNS ON A PATH THAT ALREADY RUNS, rather than on a timer.

    A timer is a background task, and a background task holding write grants
    is exactly what ``GRANT_TTL_SECONDS`` exists to make impossible. So the
    sweep happens on mint and on consume, and this asserts the first -- on the
    call that CREATES the pressure, since one preview per confirmation is the
    optimistic ratio and the real one is worse.
    """
    writes.discard_all()
    stale = _bare_grant(action="save_job", target="4600000042")
    writes._GRANTS[stale.token] = stale
    now = [stale.minted_at + writes.GRANT_TTL_SECONDS + 1.0]
    monkeypatch.setattr(writes.time, "monotonic", lambda: now[0])

    spec = spec_for_action("save_job")
    observation = writes._record(
        spec,
        target="4600000099",
        facts={"title": "A posting", "company": "A company"},
        facts_url="https://www.linkedin.com/jobs/view/4600000099/",
        state="not_saved",
        state_why="read off the list",
        state_url=writes.SAVED_LIST_URL,
        same_page_as_action=False,
    )
    fresh = mint("save_job", "4600000099", receipt=observation.receipt)

    assert stale.token not in writes._GRANTS, "the stale grant survived a mint"
    assert fresh.token in writes._GRANTS, "the new grant was swept by its own mint"
    writes.discard_all()


def test_the_expired_token_keeps_its_own_answer_rather_than_the_sweepers(
    writes_on, monkeypatch
):
    """AND THE SWEEP DOES NOT EAT THE MESSAGE, which it did at first.

    Sweeping before the lookup in ``consume`` was the obvious placement and it
    cost something real: an expired token stopped getting "this confirm token
    expired after 120s -- run the preview again and read it before confirming"
    and started getting "unknown or already-discarded confirm token". Both
    refuse. Only one tells him what to do, and the difference lands on
    somebody who has just taken too long over a block this design asked him to
    read carefully.
    """
    writes.discard_all()
    grant = _bare_grant(action="save_job", target="4600000042")
    writes._GRANTS[grant.token] = grant
    monkeypatch.setattr(
        writes.time,
        "monotonic",
        lambda: grant.minted_at + writes.GRANT_TTL_SECONDS + 1.0,
    )
    with pytest.raises(WriteAttemptError) as excinfo:
        consume(grant.token, action="save_job", target="4600000042")
    message = str(excinfo.value)
    assert "expired" in message, message
    assert "Run the preview again" in message, message
    writes.discard_all()


# ---------------------------------------------------------------------------
# 10. THE ONE LABEL: printed for him, and provably nowhere else
# ---------------------------------------------------------------------------
#
# RULED 2026-08-31. The distinction it turns on: loading a stranger's PROFILE
# stays refused because it EMITS -- linkedin_who_viewed_me reads the receiving
# end of exactly that signal -- so the cost lands on somebody who did not agree
# to it. Reading ONE accessible name off a page already rendered on HIS OWN
# profile emits nothing: nobody is notified, no record is created, the person
# is not made aware. And he already knows the name, because he supplied the
# needle; reading the label back CONFIRMS the control his own word selected is
# the person he meant, which is verification of his input.


def _grantable_invitation(monkeypatch):
    """Make ``send_invitation`` grantable, so ``grant.preview`` exists to be
    checked. It holds no ``url_template`` in production, so no grant is minted
    and there is nothing for a label to leak INTO -- which would make the
    leak test vacuous today and useless on the day that changes.

    The url is his own profile, which ``observe`` already loads for this
    action, so nothing about what the test drives changes.
    """
    spec = spec_for_action("send_invitation")
    grantable = dataclasses.replace(
        spec,
        url_template=writes.PROFILE_URL,
        url_pattern=re.compile(r"^https://www\\.linkedin\\.com/in/me/?$"),
    )
    monkeypatch.setitem(SANCTIONED_WRITES, "linkedin_send_invitation", grantable)
    return grantable


async def test_the_confirm_block_names_who_the_invitation_would_reach(
    writes_on, browser_page
):
    """THE BLOCKER THIS LIFTS, and it was never the boundary.

    ``send_invitation``'s route costs no badge, its anchor is measured, and
    its aiming works. What stopped it was that the confirm block could say a
    COUNT and a POSITION and not WHO -- and every other action here names its
    target in terms he can check.
    """
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")

    named = block.get("who_this_would_reach")
    assert named, block
    assert MEMBER in named, named
    # IT TELLS HIM TO CHECK IT, and says what it cannot catch. A word that
    # uniquely selects the WRONG person is the one failure this gate has no
    # way to see, and a block that printed a name without saying so would read
    # as corroboration it has not got.
    assert "CHECK IT" in named
    assert "no grant" in named


async def test_the_label_does_not_reach_the_grant(writes_on, browser_page, monkeypatch):
    """CONDITION 2 OF THE RULING, and the mutation it named.

    ``grant.preview`` is a RETAINED object -- it lives in ``_GRANTS`` for the
    life of the grant. The label reaches the returned block and must not reach
    that. It is enforced by ORDER rather than by scrubbing: the block is
    assigned to the grant BEFORE the label exists, and the label is added to a
    NEW dict afterwards, so the retained object provably never held it.

    Driven through a spec made grantable on purpose -- see the helper. In
    production this action mints nothing, so without that the check would pass
    on an absence and prove nothing.
    """
    _grantable_invitation(monkeypatch)
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")

    assert block.get("to_confirm"), "the spec was not made grantable"
    assert MEMBER in str(block.get("who_this_would_reach") or "")

    grants = list(writes._GRANTS.values())
    assert len(grants) == 1, grants
    grant = grants[0]
    # NOT IN THE RETAINED BLOCK -- neither the key nor the LABEL.
    #
    # THE NEEDLE IS NOT WHAT IS BEING SWEPT FOR, and getting that wrong was
    # this test's first draft: ``MEMBER`` is HIS OWN WORD and appears in the
    # retained block legitimately, as ``target``. That is the guarantee this
    # design declined to trade away rather than a leak. What must not be there
    # is the string LINKEDIN wrote -- the accessible name of somebody else's
    # control.
    label = "Invite " + MEMBER + dom.INVITE_CONTROL_SUFFIX
    assert "who_this_would_reach" not in grant.preview, grant.preview
    assert label not in json.dumps(grant.preview), grant.preview
    assert grant.target == MEMBER
    # AND NOT IN THE OBSERVATION, which is retained on the grant too -- which
    # is exactly why _read_profile_invitations does not read the label at all.
    assert grant.observation is not None
    assert label not in json.dumps(grant.observation.facts)
    # The returned block DOES carry it, which is the whole point of the pair.
    assert label in str(block.get("who_this_would_reach") or "")


async def test_two_matches_print_no_name(writes_on, browser_page):
    """THE OTHER MUTATION THE RULING NAMED: a label reaching a SECOND
    control's row.

    Exactly ONE label, the one the needle uniquely selected. Two matches is
    where a name would be least safe to print and most tempting to print
    anyway -- he would be shown one of two people and confirm against it.

    The preview refuses outright here, which is the older half of the rule:
    ``aim_invitation`` calls two matches AMBIGUOUS because choosing between
    indistinguishable controls is choosing by position.
    """
    two = PROFILE_MARKUP.replace(
        "</body>",
        '<button aria-label="Invite Somebody Else'
        + dom.INVITE_CONTROL_SUFFIX
        + '"></button></body>',
    )
    assert two != PROFILE_MARKUP
    pages = _nine_pages()
    pages[writes.PROFILE_URL] = two
    nav = FixtureNavigator(pages)
    spec = spec_for_action("send_invitation")

    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(
            spec, target=MEMBER, navigator=nav, page=browser_page, to_state=None
        )
    message = str(excinfo.value)
    assert "ambiguous" in message.lower() or "choosing by position" in message
    # AND NO NAME IN THE REFUSAL. This is the path where a leak would be
    # easiest to miss, because a refusal reads as safe.
    assert "Somebody Else" not in message


async def test_no_other_part_of_the_answer_carries_the_name(
    writes_on, browser_page
):
    """A SWEEP, not a field check. The block is one field richer than it was
    and every OTHER field must be exactly as clean as before -- a name that
    reached ``where`` or ``direction`` or a refusal string would satisfy any
    per-field assertion aimed at the new one."""
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    rest = {
        key: value
        for key, value in block.items()
        if key != "who_this_would_reach"
    }
    blob = json.dumps(rest)
    # The needle IS his own word and DOES legitimately appear as the target;
    # what must not appear anywhere else is the LABEL LinkedIn wrote.
    assert "Invite " + MEMBER not in blob, rest
    assert dom.INVITE_CONTROL_SUFFIX not in blob, rest


async def test_the_python_gate_holds_when_the_script_stops_gating(
    writes_on, browser_page, monkeypatch
):
    """DEFENCE IN DEPTH, MADE REACHABLE -- and it was not, when first written.

    The ruling asked for the label to be gated in two languages so that no
    single edit opens both. It is: the script requires the caller to have
    asked AND exactly one match, and ``_name_the_invitation_recipient``
    re-checks the match count in Python.

    THE PYTHON HALF COULD NOT FAIL. Measured, by the mutation that deletes it:
    the suite stayed green, because the script's own gate meant a reading with
    two matches never carried a label for the Python check to catch. A gate
    that cannot fail certifies nothing -- so rather than delete it, this
    reaches it the only way it can be reached: by simulating a SCRIPT that has
    stopped gating, which is precisely the failure defence in depth exists
    for.
    """
    real = dom.read_invitation_surface
    calls = {"n": 0}

    async def _ungated(page, needle=None, **kwargs):
        calls["n"] += 1
        reading = dict(await real(page, needle, **kwargs))
        if calls["n"] > 1:
            # A script that lost its ``matches === 1`` condition: two
            # controls matched and it handed back a name anyway.
            reading["matches"] = 2
            reading["label"] = "Invite Somebody" + dom.INVITE_CONTROL_SUFFIX
        return reading

    monkeypatch.setattr(dom, "read_invitation_surface", _ungated)
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    assert calls["n"] >= 2, "the label read did not happen at all"
    assert "who_this_would_reach" not in block, block


async def test_a_page_that_moved_is_not_read_for_a_name(
    writes_on, browser_page, monkeypatch
):
    """THE SETTLE PRECONDITION, applied to the one read that can emit a name.

    This reads the page ``observe`` just measured, without loading anything.
    That is only safe while the page IS the one it measured -- so the re-read
    must find the SAME RAIL, and the needle must still pick out exactly one.

    THE RAIL RATHER THAN THE URL, and the first draft used the url. A url
    comparison is the obvious guard and it is the weaker one: a page can
    re-render at the same address, and what matters is whether the control the
    name is read off is the control the aim was taken on. It was also
    untestable through this harness, where the page's url is not a LinkedIn
    address at all -- which is its own argument that it was checking the wrong
    thing.
    """
    calls = {"n": 0}
    real = dom.read_invitation_surface

    async def _wandered(page, needle=None, **kwargs):
        calls["n"] += 1
        reading = await real(page, needle, **kwargs)
        if calls["n"] > 1:
            # The SECOND read -- the one the label would come from -- finds a
            # different rail. In production that is a page that re-rendered
            # between the aim and the read; here it is arranged, because the
            # guard has to be shown refusing and a fixture page does not move
            # on its own.
            reading = dict(reading)
            reading["controls"] = int(reading["controls"]) + 3
        return reading

    monkeypatch.setattr(dom, "read_invitation_surface", _wandered)
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    assert calls["n"] >= 2, "the label read did not happen at all"
    assert "who_this_would_reach" not in block, block
