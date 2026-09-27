"""The seven capabilities that arrived sanctioned and refusing, certified.

On 2026-08-30 seven actions were added to ``SANCTIONED_WRITES`` as full
``WriteSpec`` entries -- publish a post, comment, react, edit a profile field,
change a setting, send an invitation, send a message -- and an eighth,
``follow_company``, became performable. This file is about the seven. It is
NOT about follow, which is covered where the performable actions are.

THE SEVEN ARE NOW ONE, AND THE FILE IS NOT ABOUT SEVEN THINGS ANY MORE. All
seven shipped between 2026-08-31 and 2026-09-02 -- the last, ``send_message``,
as the twelfth performable write -- and each left by becoming performable,
which is the only exit this file admits. What remains sanctioned and refusing
is ``set_open_to_work`` alone, so the corpus is named ``REFUSING`` and derived
from the registry rather than typed and named for a count that has now been
wrong three times. ``LIFTED`` records every departure with its date and its
reason, and the checks below run against whatever still refuses.

TWO CONSEQUENCES OF THAT ARRIVAL WORTH READING BEFORE THE SECTIONS, because
both changed what the checks assert rather than merely which action they run
on. First, ``writes._NINE_REFUSALS`` IS EMPTY: every entry left with its
action, and ``set_open_to_work`` refuses from a sibling branch of the same
function, so section 3 reads the refusal a CALLER GETS by invoking
``_refuse_unperformable`` rather than by indexing a table. Second,
``writes._SURFACE_READS`` is the FALLBACK FAMILY and not the routing table --
``observe`` handles this action's surface in a branch above it -- so section 2
resolves the expected url through a helper that knows the difference.

WHAT MAKES THIS AN UNUSUAL THING TO TEST. Every action in the corpus is
sanctioned and none of them can act. That combination is only worth anything if it is
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

# INERT AT RUNTIME AND STILL WRONG WITHOUT IT. `from __future__ import
# annotations` stores TO_STATES' annotation as the STRING
# "dict[str, Optional[str]]", so importing this module never raised --
# but typing.get_type_hints() on it raised NameError, measured 2026-09-02.
from typing import Optional

from linkedin_server import dom, readonly, shape, writes
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
    REACTED_ITEM,
    FixtureNavigator,
    _bare_grant,
    browser_page,
    writes_on,
)

#: The ones that are sanctioned and STILL REFUSE, DERIVED from the registry.
#:
#: IT WAS CALLED ``SEVEN`` AND IT WAS TYPED OUT, until 2026-09-02. Both of
#: those were wrong and they were wrong in different ways, so they are recorded
#: separately.
#:
#: THE NAME WAS A COUNT, AND A CORPUS NAMED FOR ITS SIZE LIES THE MOMENT THE
#: SIZE CHANGES. It changed three times in three days -- seven on 2026-08-30,
#: six on 08-31, two on 09-01, one on 09-02 -- and the constant went on being
#: called SEVEN through all of it, so every sentence in this file that said
#: "the seven" was describing a population that had not existed for days. The
#: name is now what it is: the actions that refuse.
#:
#: THE OLD COMMENT ARGUED AGAINST DERIVING IT and the argument is quoted
#: because it was half right: "A derived list would be satisfied by somebody
#: deleting a spec, which is the move these tests exist to make visible." That
#: hazard is real and it is covered -- by
#: ``test_nothing_left_the_refusing_set_except_by_shipping``, which reconciles
#: this corpus, ``LIFTED`` and ``PERFORMABLE`` against the whole sanctioned
#: set, so a deleted spec goes missing from the TOTAL. What the typed tuple
#: bought on top of that was nothing, and what it cost was two stale-corpus
#: failures in two days.
#:
#: WHY IT NOW INCLUDES ``set_open_to_work``, WHICH THE TYPED VERSION EXCLUDED.
#: The old derivation filtered on ``spec.tool_name == name`` and then
#: explicitly discarded this one, on the ground that it has no registered MCP
#: tool. That was a fact about REACHABILITY and this corpus is about
#: REFUSAL -- and scoping a refusal corpus by whether a tool happens to be
#: registered is what emptied it: with ``send_message`` shipped, the filter
#: returned nothing at all and every check below would have run zero cases.
REFUSING = tuple(
    sorted(
        spec.action
        for spec in SANCTIONED_WRITES.values()
        if spec.action not in writes.PERFORMABLE
    )
)

#: THE ACTIONS RULED TO HAVE NO ADDRESS TO NAME, and the only ones whose
#: refusal may take the second arm of the address check below.
#:
#: ONE MEMBER, and it earned the exemption with an enumeration rather than a
#: phrase: ``set_open_to_work``'s refusal contains no slash because ITS ENTIRE
#: MEASURED CONTENT IS THAT NO URL EXISTS -- 237 distinct urls and 37 payload
#: paths enumerated across five profile captures, zero of which reach the
#: editor, which is fetched by an SDUI RPC and opens as a modal from a control
#: on his own profile.
#:
#: IT IS A SET RATHER THAN A CONDITION IN THE TEST because "names a page OR
#: says it has none" is a disjunction, and the second arm is satisfiable by any
#: refusal that happens to carry the phrase. Pinning the membership is what
#: stops the exemption widening by prose.
MAY_CLAIM_NO_ADDRESS: frozenset = frozenset({"set_open_to_work"})


#: What has left ``REFUSING``, and when. An action may only be here if it is in
#: ``writes.PERFORMABLE``, which is asserted below -- so this cannot become a
#: place to park something that merely stopped passing.
LIFTED = {
    "update_setting": "2026-08-31",
    # THE SIXTH DEPARTURE, 2026-09-02, and the only one that left because
    # everything its refusal named as missing was BUILT rather than measured
    # away, ruled around, or declared. The refusal said "/edit/ is forbidden
    # and no field inside any editor has ever been observed"; by the time it
    # left, the editor was addressed by an exact-url exemption, its controls
    # were readable, a fourth mutation kind existed to choose among them, and
    # the value could be read back afterwards.
    #
    # IT IS ALSO THE BEST-VERIFIED WRITE IN THIS PACKAGE, which none of the
    # five before it can say: publish_post declared its outcome unverifiable,
    # send_invitation ships with none at all, and apply_job can only establish
    # that it did NOT happen. This one reads the field back.
    "update_profile_field": "2026-09-02",
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
    # THE FIFTH DEPARTURE, same day, and the only one that left with a blocker
    # still OPEN and UNRULED: comment_on_item's submit control has never been
    # observed, and no ruling can measure a control. It ships with a gate that
    # finds the submit by ARRIVAL and refuses with the observation when it
    # cannot -- so the first refusal is what produces the measurement.
    "comment_on_item": "2026-09-01",
    # THE SEVENTH DEPARTURE, 2026-09-02, and it was THE LAST ONE WITH A
    # REGISTERED TOOL. Its blocker was not a missing control but a missing
    # AIM: the recipient box is a typeahead nobody had typed into, and "Send
    # became enabled" says LinkedIn thinks the message is sendable, not that
    # the recipient is the person he named. It ships on a gate that requires
    # exactly ONE committed recipient whose accessible name carries his own
    # needle, compared inside the page with integers only coming back, run
    # BETWEEN the two fills so his words are never typed until the recipient
    # is confirmed.
    #
    # ITS DEPARTURE IS WHY THIS FILE WAS RESTRUCTURED rather than merely
    # edited. It emptied ``writes._NINE_REFUSALS`` -- the table began with
    # seven entries on 2026-08-30 and every one of them left by shipping -- and
    # the checks below were reading that table directly. See the section 3
    # comment for what they read instead.
    "send_message": "2026-09-02",
}


def test_nothing_left_the_refusing_set_except_by_shipping():
    """THE LEDGER'S OWN GUARD, and it is the whole reason ``LIFTED`` is a dict
    rather than a deleted line.

    An action can leave ``REFUSING`` for two reasons that look identical in a
    diff: it became performable, or its checks became inconvenient. This
    asserts the first. Every name recorded as lifted must really be in
    ``writes.PERFORMABLE``, no name may be in both, and the two together must
    still account for every sanctioned action -- so a spec quietly deleted
    goes missing from the total instead of going unnoticed.

    THIS IS ALSO WHAT MAKES DERIVING ``REFUSING`` SAFE, and it is the reason
    the old typed tuple could be retired on 2026-09-02. The objection to a
    derived corpus was that deleting a spec would silently shrink it. It
    cannot shrink silently past this line: the reconciliation is against the
    WHOLE sanctioned set, so a deleted spec fails here whichever side of the
    performable line it was on.

    THE ``{"set_open_to_work"}`` TERM IS GONE from the union below, and its
    absence is the point rather than a tidy-up. It was there because the old
    corpus deliberately excluded that action, so the total did not add up
    without putting it back by hand. ``REFUSING`` now contains it, so the term
    would be redundant -- and a redundant term in a reconciliation is worse
    than untidy: it would go on making the sum work after the corpus stopped
    covering that action, which is exactly the failure this line exists to
    catch.
    """
    for action, when in LIFTED.items():
        assert action in writes.PERFORMABLE, action
        assert action not in REFUSING, action
        assert when
    sanctioned = {spec.action for spec in SANCTIONED_WRITES.values()}
    accounted = set(REFUSING) | set(LIFTED) | set(writes.PERFORMABLE)
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

#: THE TARGET SINCE 2026-09-27: the person's PROFILE LINK (lane L5, the
#: orchestrator's order of 23:36). ``MEMBER`` above stays as the NAME the
#: card's control and link draw -- read back only by the preview -- and is no
#: longer anything a caller passes. The segment carries ``example``, a
#: declared synthetic slug token.
MEMBER_LINK = "https://www.linkedin.com/in/somebody-example-7f3c/"

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

#: THE PROFILE OWNER'S DISPLAY NAME ON THE FAKE TOPCARD.
#:
#: A PLACEHOLDER, and deliberately not the name on the frozen capture in
#: ``tests/fixtures/``. This file builds its pages rather than reading them,
#: and a real name typed into a tracked source file is the thing
#: ``tests/test_no_committed_identity.py`` exists to refuse. The reader only
#: needs SOME name -- ``_read_profile_state`` refuses to render a gate when the
#: topcard drew none, and echoes whatever it found into ``facts`` -- so the
#: content is irrelevant and its absence is not.
#:
#: It deliberately does not contain ``MEMBER``. The invitation section counts
#: controls whose accessible name carries that needle, and a topcard heading
#: that happened to include it would be a fixture quietly feeding the aiming
#: tests an extra match.
PROFILE_OWNER = "A Placeholder Person"

#: THE TOPCARD, ADDED 2026-09-02 WHEN ``set_open_to_work`` ENTERED THE CORPUS.
#:
#: Until then no test here previewed an action that reads ``profile_topcard``,
#: so this page carried only the editor link and the invitation control -- and
#: the preview refused with "the topcard drew no name" rather than rendering
#: the block. That is the gate working: it will not describe whose setting is
#: being changed without having read the profile. The fixture was the thing
#: that was wrong.
#:
#: WHAT ``READ_PROFILE_JS`` ACTUALLY NEEDS, which is why this shape and not a
#: simpler one: a ``<main>``, at least one ``h1/h2/h3`` inside it, and the
#: section's lines are the innerText of the block that heading climbs to. With
#: no ``<title>``, ``shape.pick_topcard`` falls back to the FIRST section, and
#: ``shape.parse_profile_topcard`` takes the first line as the name -- so the
#: heading must be both first and the name. The editor link and the invitation
#: control stay OUTSIDE ``<main>`` so they cannot land in the topcard's lines
#: and be read as a headline.
#:
#: THE MIDDLE DOT IS TAKEN FROM ``shape.MIDDLE_DOT`` rather than typed. It is
#: the separator LinkedIn draws between the label and the audience, it is
#: non-ASCII, and this file is ASCII-only -- so the one place it may exist is
#: the constant the production regex is built from, which also means the
#: fixture cannot drift away from what that regex matches.
#:
#: THE AUDIENCE IS NOT VALIDATED HERE AND DOES NOT NEED TO BE. If it were not
#: one of the strings the spec has seen LinkedIn render, ``_read_profile_state``
#: returns UNKNOWN, ``_direction`` refuses to render a gate on an unknown, and
#: the preview tests fail loudly. The check is the test, not an assertion here.
PROFILE_TOPCARD_MARKUP = (
    "<main><div>"
    "<h1>" + PROFILE_OWNER + "</h1>"
    "<p>Open to work " + shape.MIDDLE_DOT + " Recruiters only</p>"
    "</div></main>"
)

PROFILE_MARKUP = (
    "<html><body>" + PROFILE_TOPCARD_MARKUP
    + '<a href="https://www.linkedin.com/in/somebody'
    + dom.PROFILE_EDITOR_HREFS[0]
    + '">Edit intro</a>'
    # A RAIL CARD, as MEASURED on his own profile's suggestion rail (32 of 32
    # controls): the nearest element holding a profile link holds ONE member's
    # link and ONE invitation control, and the link's text names the person
    # the control names. The aim is that link, compared in the page with the
    # caller's (``dom.rail_invite_control_selector``) -- never the label. The
    # label is another person's name, so the fake carries a placeholder, read
    # back only by the preview.
    + '<div class="rail-card"><a href="' + MEMBER_LINK + '">' + MEMBER + "</a>"
    + '<button aria-label="Invite ' + MEMBER + dom.INVITE_CONTROL_SUFFIX + '"></button></div>'
    + "</body></html>"
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
#: CORRECTED 2026-09-03 TO THE SHAPE THAT WAS MEASURED, after the first live
#: fire. This fixture drew ``<span>`` elements and inputs carrying NO id --
#: right about the naming route and wrong about the element. The live page
#: binds a real ``<label for>`` to an input that HAS an id, and the aim now
#: presses that label because the input itself is covered by a decorative div
#: and cannot be clicked. Without ids here there is no ``for`` to bind, so the
#: activation check correctly refused and three tests went red against a page
#: LinkedIn does not serve.
#: THE THREE ROWS, AS DATA. ``(input id, label id, visible text)``.
_DM_ROWS = (
    ("dm-r-off", "dm-off", "Always off"),
    ("dm-r-on", "dm-on", "Always on"),
    ("dm-r-dev", "dm-dev", "Device settings"),
)


def _dm_row(
    input_id: str,
    label_id: str,
    text: str,
    *,
    checked: bool = False,
    kind: str = "radio",
    tag: str = "",
) -> str:
    """ONE settings row, built rather than spelled.

    **EVERY VARIANT IN THIS FILE IS BUILT THROUGH HERE, and that is a repair to
    a whole CLASS rather than to one fixture.** These pages used to be derived
    by string-replacing literal ``<input ...>`` tags out of
    ``DARK_MODE_MARKUP``. On 2026-09-03 that markup was corrected to the shape
    the live page actually has -- real ids, a real ``<label for>`` -- and FOUR
    derivations anchored on the old literals silently became no-ops in the same
    edit.

    Two of them had guards that caught it (``assert 'role="switch"' in broken``
    and ``assert both.count("checked") == 2``). One had a guard too WEAK to:
    ``assert after.count("checked") == 1`` was satisfied by the unmodified
    page, because the before-state also has exactly one checked -- so the test
    ran the whole flow against a page that never changed and failed on
    ``performed`` with no hint why.

    A derivation that can silently no-op needs a guard. A derivation that
    cannot no-op needs none, and this is that: the variant and the base are
    generated from the same three tuples, so a change to the row shape moves
    both at once and there is no literal left to fall out of step.

    ``tag`` replaces the whole ``<input>`` element for the one test that needs
    a non-input control; everything else varies only ``checked`` and ``kind``.
    """
    control = tag or (
        '<input type="' + kind + '" name="dm" id="' + input_id + '"'
        ' aria-labelledby="' + label_id + '"' + (" checked" if checked else "") + ">"
    )
    return (
        control
        + '<label for="'
        + input_id
        + '" id="'
        + label_id
        + '">'
        + text
        + "</label>"
    )


def _dm_page(
    *,
    checked: str = "Always off",
    kind: str = "radio",
    also_checked: str = "",
    replace: tuple = (),
) -> str:
    """The dark-mode surface, with exactly the variation asked for.

    ``checked`` names the row that is checked; ``also_checked`` names a SECOND
    one, for the two-checked refusal; ``replace`` is ``(text, tag)`` and swaps
    one row's control for an arbitrary element.
    """
    swap_text, swap_tag = (replace + ("", ""))[:2]
    rows = []
    for input_id, label_id, text in _DM_ROWS:
        rows.append(
            _dm_row(
                input_id,
                label_id,
                text,
                checked=(text == checked or text == also_checked),
                kind=kind,
                tag=swap_tag if (swap_text and text == swap_text) else "",
            )
        )
    return "<html><body>" + "".join(rows) + "</body></html>"


DARK_MODE_MARKUP = _dm_page()


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
TO_STATES: dict[str, Optional[str]] = {
    "update_setting": "Always on",
    # ADDED 2026-09-02 with set_open_to_work. It is the SECOND multi-state
    # action and it has three audiences, so ``_direction`` refuses to derive a
    # destination for it exactly as it does for dark mode.
    #
    # ``off`` RATHER THAN ``all linkedin members``, and the choice is not
    # arbitrary even though nothing is performed here. The fixture's current
    # state is "Recruiters only", so the destination has to differ from it or
    # the gate refuses with "already X, nothing to change" and these tests
    # would exercise that refusal instead of the block. Of the two remaining,
    # ``all linkedin members`` is the one that draws a public #OpenToWork
    # frame his employer can see -- so a fixture standing permanently in the
    # suite asking for it would be modelling the most dangerous call in the
    # design as the ordinary one.
    "set_open_to_work": "off",
}


#: A well-formed target for each of the seven, in the shape its own
#: ``target_kind`` is addressed by.
TARGETS: dict[str, object] = {
    "publish_post": "Shipping a small thing today.",
    "comment_on_item": {"item": ITEM, "text": COMMENT_A},
    "react_to_item": ITEM,
    "update_profile_field": {"field": "headline", "value": "Node.js engineer"},
    "update_setting": {"setting": "dark-mode", "value": "Always on"},
    "send_invitation": MEMBER_LINK,
    "send_message": {"member": MEMBER, "text": "Hello, are you hiring?"},
    # ADDED 2026-09-02, when the corpus stopped excluding this action. Its
    # target_kind is ``self`` -- the write lands on his own account and names
    # nothing else -- and ``_canonical_target`` accepts exactly "self", "me" or
    # the empty string for that kind, so this is not a placeholder standing in
    # for an id. There is no id.
    "set_open_to_work": "self",
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
    # ``send_reply``'s subject, 2026-09-24: a conversation id in the read
    # allowlist's own shape (a digit first). SYNTHETIC, as every thread id in
    # this suite is.
    "thread": "2-SYNTHETICCLEANTHREAD==",
    # ``message_from_profile``'s subject, 2026-09-27: a profile LINK, because
    # a bare word is refused as a possible name. The segment carries the
    # declared synthetic slug token ``someone``.
    "profile": "https://www.linkedin.com/in/someone-clean-example/",
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


#: EVERY SANCTIONED ACTION WITH A COMPOSITE TARGET, not just the refusing ones.
#:
#: DERIVED FROM THE REFUSING SET UNTIL 2026-09-02, AND THAT WAS ALWAYS WRONG.
#: It is the identical mistake ``OPAQUE_ACTIONS`` was carrying until
#: 2026-09-01, for the identical reason, and it is recorded twice rather than
#: fixed quietly because one file making the same scoping error twice in three
#: days is the thing worth noticing.
#:
#: The checks these feed are about how a composite TARGET IS NORMALISED -- the
#: separator refusal, the empty component, the character cap, the control
#: characters, the non-dict. Not one of them has anything to do with whether
#: the action performs. Scoping them to the refusing set meant the coverage
#: SHRANK every time a capability shipped, so the suite tested least exactly
#: where the most was happening: on 2026-09-02 it was down to ONE action and
#: TWO component cases, and ``send_message`` shipping would have taken it to
#: zero -- which does not fail, it just quietly stops running.
#:
#: Derived from the registry it is 5 actions and 9 component cases, and the
#: four that were never being checked are the four that type: publish_post,
#: comment_on_item, update_profile_field and update_setting.
COMPOSITE_ACTIONS = tuple(
    sorted(
        spec.action
        for spec in SANCTIONED_WRITES.values()
        if spec.target_kind in writes._COMPOSITE_TARGET_KINDS
    )
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


def test_the_refusing_corpus_really_refuses():
    """``REFUSING`` must be the registry's answer AND every member must refuse.

    ADDED 2026-09-01 AS A DRIFT DETECTOR, REPURPOSED 2026-09-02 WHEN THE DRIFT
    BECAME IMPOSSIBLE. It was written after the suite shrank by four and nobody
    could see why: ``comment_on_item`` shipped, left the typed tuple, and cost
    **20 collected cases**, noticed only by a hand-diff of two totals. Its job
    was to compare a TYPED tuple against the registry, in both directions.

    THE TYPED TUPLE IS GONE, so that comparison would now be a tautology --
    ``REFUSING`` is built from the registry, so asserting it equals the
    registry asserts nothing. A check that cannot fail is worse than no check,
    and rather than delete this one it was pointed at the claim that CAN still
    be wrong.

    WHAT IT ASSERTS NOW IS BEHAVIOUR RATHER THAN MEMBERSHIP: every member of
    this corpus, put through the function a caller actually reaches, really
    does refuse. That is not derivable from the registry -- ``PERFORMABLE``
    membership is a set operation, refusing is what ``_refuse_unperformable``
    does -- so the two can disagree, and this is where they would be caught.

    IT STILL DOES NOT PIN AN ABSOLUTE CASE COUNT, and that is a judgement
    rather than an omission. A pinned total fires on every legitimate change,
    and this package has watched exactly that train a reader to bump a number
    without reading it -- the module docstring in server.py rotted SEVEN times
    while carrying counts somebody re-typed each time. A check that cries wolf
    on every commit is how the real signal gets ignored.

    WHAT SERVES THE VISIBILITY INSTEAD is ``LIFTED``: one line per departure,
    with its date and its reason. The gap on 2026-09-01 was not a missing test
    -- the departure WAS recorded -- it was that the commit message stated the
    membership change and never its consequence. That is a reporting habit,
    and it is cheaper to fix than a noisy assertion.
    """
    from_registry = {
        spec.action
        for spec in SANCTIONED_WRITES.values()
        if spec.action not in writes.PERFORMABLE
    }
    assert set(REFUSING) == from_registry, {
        "in the corpus but no longer refusing": sorted(
            set(REFUSING) - from_registry
        ),
        "refusing but missing from the corpus": sorted(
            from_registry - set(REFUSING)
        ),
    }
    # AND THE HALF THAT IS NOT A TAUTOLOGY. A spec can sit outside PERFORMABLE
    # and still be waved through, if the function that refuses ever stops
    # agreeing with the set that defines it -- which is not hypothetical:
    # _refuse_unperformable returns EARLY for anything in PERFORMABLE and then
    # picks its message from two different places, and one of those places is
    # now empty.
    for action in REFUSING:
        with pytest.raises(WriteAttemptError):
            writes._refuse_unperformable(spec_for_action(action))


def test_no_parametrized_corpus_in_this_file_is_empty():
    """A parametrized test over an empty tuple SKIPS, and a skip reads as a pass.

    This is the guard for the failure that produced the comment above: three
    checks stopped running and nothing said so louder than one grey line. Any
    tuple this file fans out over must be non-empty, asserted by name so the
    failure says WHICH corpus emptied.

    ALL FIVE CORPORA ARE NOW DERIVED FROM ``SANCTIONED_WRITES``, as of
    2026-09-02, and that makes this guard MORE necessary rather than less. A
    typed tuple empties only when somebody edits it; a derived one empties when
    the system changes shape, silently, on a commit that touched no test. Both
    of this file's silent-emptying incidents were derived corpora --
    OPAQUE_ACTIONS on 09-01, and COMPOSITE_ACTIONS which would have gone the
    same way on 09-02 had it not been re-derived first.

    NONE OF THE FIVE CAN LEGITIMATELY EMPTY TODAY, so all five are asserted
    non-empty with no exceptions. ``REFUSING`` is the one to watch: it holds
    exactly ``set_open_to_work``, whose refusal rests on a payload that is
    absent by the time this server can look at the page. If that is ever
    resolved and the action ships, this line fires -- and the right answer then
    is to say so here, in the assertion, rather than to drop the corpus from
    the list.
    """
    for name, corpus in (
        ("REFUSING", REFUSING),
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
# 1. No grant can exist for any refusing action
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", REFUSING)
def test_no_refusing_action_names_a_write_surface(action):
    """Both url fields empty, per action rather than as a claim about the set.

    A set-level assertion ("the surfaceless set is these eight") is satisfied
    by the set being right; it says nothing about WHICH field is empty, and
    ``assert_write_url`` needs BOTH -- it refuses on a missing template or a
    missing pattern, so a spec carrying one of the two would slip past a
    membership test while being half-armed.

    THE UPDATE_PROFILE_FIELD EXEMPTION LIVED HERE FOR ONE DAY and is gone,
    which is worth a paragraph because deleting a carve-out normally means
    somebody softened something. This is the opposite. On 2026-09-02 that
    action was addressed-but-unperformable -- the first thing ever to be
    both -- and this assertion, like three others in two other files, had
    encoded "unperformable implies unaddressed" without anybody ruling it. It
    then SHIPPED later the same day, so it is no longer in this corpus at all
    and the branch was unreachable. Removed rather than kept, on the rule this
    file already applies to ``LIFTED``: a branch for a shipped action is dead
    text that reads like a live exception.

    WHAT THE ACCIDENT TAUGHT SURVIVES ANYWAY, and it is why the sentence stays
    here rather than going with the branch: THE ABSENCE OF A URL IS NOT WHAT
    MAKES A GRANT IMPOSSIBLE. ``PERFORMABLE`` membership is, checked in
    ``mint`` itself, and ``test_mint_refuses_a_grant_at_issue`` below is the
    one that actually holds the line. This test pins a narrower and still
    useful thing: that no action in the refusing set is half-armed.
    """
    spec = spec_for_action(action)
    assert spec.url_template is None, action
    assert spec.url_pattern is None, action


@pytest.mark.parametrize("action", REFUSING)
def test_mint_refuses_a_grant_at_issue(writes_on, action):
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


def _expected_surface_url(spec) -> str:
    """The url ``observe`` will load for this spec, without indexing one table.

    ``writes._SURFACE_READS`` IS ONLY THE FALLBACK FAMILY, and reading it as
    though it were the whole routing table was a wrong assumption in this file
    rather than a gap in ``writes``. ``observe`` dispatches on ``state_from``
    through a chain of its own branches -- ``posting_page``, ``apply_control``,
    ``followed_pages``, ``saved_list``, ``profile_topcard`` -- and only then
    falls through to that dict. Indexing it directly therefore raised KeyError
    for ``set_open_to_work`` the moment that action entered this corpus on
    2026-09-02, which looked like a missing entry and was not one. NOTHING WAS
    ADDED TO ``_SURFACE_READS`` TO MAKE THE LOOKUP WORK: an entry there would
    have changed which branch of ``observe`` runs in production, to make a test
    convenient.

    IT RAISES RATHER THAN GUESSING for a state this file has not been taught.
    A default would silently assert against the wrong page, which is the same
    class of defect as the KeyError and quieter.
    """
    if spec.state_from in writes._SURFACE_READS:
        url, _surface, _reader = writes._SURFACE_READS[spec.state_from]
        return url
    if spec.state_from == "profile_topcard":
        return writes.PROFILE_URL
    raise AssertionError(
        "no expected surface url is known for state_from=%r (action %r). "
        "observe routes this through one of its own branches; add it here "
        "with the url that branch loads, and do NOT add it to "
        "writes._SURFACE_READS, which would change production routing."
        % (spec.state_from, spec.action)
    )


@pytest.mark.parametrize("action", REFUSING)
async def test_a_preview_issues_no_confirm_token(
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
    # And it says WHY there is no token rather than leaving him to infer it.
    # For everything in this corpus the reason is the surface: it has never
    # been loaded, so the block cannot even name the page the action would act
    # on.
    #
    # THERE WAS AN UPDATE_PROFILE_FIELD BRANCH HERE FOR ONE DAY, asserting the
    # opposite -- that the block names the REAL page, because that action was
    # addressed and still unperformable. It shipped later the same day and
    # left this corpus, so the branch became unreachable and was removed
    # rather than left looking live. The distinction it drew is still true and
    # is recorded on test_no_refusing_action_names_a_write_surface: an address
    # is not a permission, and the two only ever agreed by coincidence.
    assert "UNMEASURED" in block["where"]["url"], action


@pytest.mark.parametrize("action", REFUSING)
async def test_each_refusal_is_a_fresh_reading_of_the_specs_own_surface(
    writes_on, browser_page, action
):
    """The point of these previews: a refusal that LOOKED, not one that
    remembers.

    All three surfaces are frozen for every action, so a reader pointed at the
    wrong one would be served rather than erroring. What catches it is the
    navigator's record: exactly one load, and it must be the url this spec's
    own ``state_from`` names.
    """
    spec = spec_for_action(action)
    expected = _expected_surface_url(spec)
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
#
# THESE READ THE REFUSAL FROM THE FUNCTION, NOT FROM A TABLE, since 2026-09-02,
# and the change is the lesson of the day rather than a refactor.
#
# They used to index ``writes._NINE_REFUSALS[action]``. That worked for as long
# as the table happened to be where every refusal lived -- and it stopped the
# moment the corpus contained an action whose refusal lives in a SIBLING BRANCH
# of the same function. ``set_open_to_work`` raises from an explicit
# ``if spec.action == "set_open_to_work"`` clause, four thousand characters of
# it, and the table lookup raised KeyError on an action that refuses perfectly
# well. The test was checking one of two STORAGE LOCATIONS instead of the one
# FUNCTION they both feed.
#
# ``_NINE_REFUSALS`` IS NOW EMPTY -- seven entries on 2026-08-30, every one
# gone by shipping -- so reading it would today check nothing at all. Reading
# the function is what a CALLER does, it is invariant to a refusal moving
# between the two places, and it is the only version of these checks that
# survived the move.


#: A distinctive fragment of ``_refuse_unperformable``'s generic backstop.
#:
#: Quoted here so the checks below can prove a caller did NOT reach it. The
#: backstop says "%r is not performable. The complete performable set is [...],
#: and it is deliberately smaller than the sanctioned set." -- true of every
#: refusing action and explanatory of none, which is exactly why an action
#: reaching it must fail these tests.
_GENERIC_BACKSTOP = "is not performable. The complete performable set is"


def _refusal_for(action: str) -> str:
    """What a caller actually gets when this action is refused."""
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._refuse_unperformable(spec_for_action(action))
    return str(excinfo.value)


@pytest.mark.parametrize("action", REFUSING)
def test_every_refusal_names_its_own_fix_and_a_measured_artefact(action):
    """A refusal that does not name its own fix is indistinguishable from one
    nobody intends to lift.

    Four things are required and each fails on its own: the length, because a
    one-line "cannot" is the shape that goes stale unnoticed; the phrase naming
    the fix; a MEASURED COUNT, because "this was measured" with nothing
    measured beside it is the confident string this package exists to refuse;
    and the refusal being the action's OWN rather than the generic backstop.

    THE ADDRESS REQUIREMENT IS NOW SELF-POLICING, and that is a real narrowing
    with a reason rather than an assertion dropped because it failed. It used
    to be a flat ``re.search(r"/[a-z]", reason)`` -- name a page. That is a
    fair demand of a refusal whose blocker is a forbidden or unmeasured url,
    which is what all seven of the original entries had. It is an incoherent
    demand of ``set_open_to_work``, whose refusal contains no slash at all
    because ITS ENTIRE CONTENT IS THAT NO URL EXISTS: 237 distinct urls and 37
    payload paths enumerated across five profile captures, zero of which reach
    the editor, which opens as a modal from a control on his own profile.
    Requiring an address of the one action whose measured finding is the
    absence of an address would have forced either a softened check or a
    fictional url in a refusal.

    SO THE EXEMPTION HAS TO BE EARNED BY THE REFUSAL ITSELF. Either it names a
    page, or it SAYS IN WORDS that there is no page to name. A refusal that
    simply forgot to mention where it acts satisfies neither and still fails,
    which is the property the flat version was protecting.

    AND THE SECOND ARM IS ITSELF PINNED, because a disjunction is exactly where
    a check rots. "Names a page OR says it has none" is satisfied by ANY
    refusal that happens to contain the phrase, so the escape hatch would widen
    silently the first time somebody wrote it into a refusal that could
    perfectly well have named an address. :data:`MAY_CLAIM_NO_ADDRESS` is the
    closed set of actions permitted to take it, checked in BOTH directions
    below: a new action taking it FAILS until somebody rules on it, and a
    member that stops taking it fails too, so the entry cannot outlive its
    reason.

    A CHECK THAT WAS FLAT AND IS NOW CONDITIONAL NEEDS THE CONDITION CHECKED,
    or the narrowing is the last thing anybody verified about it. Same shape as
    the empty ``CANNOT_REACH`` table kept rather than deleted: the structure
    carries a claim its absence would not.
    """
    reason = _refusal_for(action)
    assert len(reason) > 200, (action, len(reason))
    assert "WHAT WOULD LIFT IT" in reason.upper(), action
    assert "MEASURED" in reason, action
    assert re.search(r"\d", reason), action
    assert _GENERIC_BACKSTOP not in reason, action
    names_a_page = bool(re.search(r"/[a-z]", reason))
    if not names_a_page:
        assert action in MAY_CLAIM_NO_ADDRESS, (
            "%s refuses without naming a page. Only %s is ruled to have no "
            "address to name -- its measured finding IS the absence of one. "
            "A new action claiming this needs a ruling, not a phrase: say "
            "which enumeration establishes that no url reaches it, and add it "
            "to MAY_CLAIM_NO_ADDRESS with that reason."
            % (action, sorted(MAY_CLAIM_NO_ADDRESS))
        )
        assert "not addressed by a url" in reason, (
            "%s refuses without naming a page AND without saying it has no "
            "page to name. One or the other: an address, or the measured "
            "finding that there is no address." % action
        )
    else:
        # THE OTHER DIRECTION, so an entry cannot outlive its reason. If a
        # member of the exempt set starts naming a page, the exemption is
        # stale -- and a stale exemption is an escape hatch nobody is
        # watching, which is the state the flat check was narrowed out of.
        assert action not in MAY_CLAIM_NO_ADDRESS, (
            "%s is listed in MAY_CLAIM_NO_ADDRESS and its refusal now names a "
            "page. The exemption has outlived the finding that earned it; "
            "remove the entry." % action
        )


@pytest.mark.parametrize("action", REFUSING)
def test_refuse_unperformable_raises_this_actions_own_refusal(action):
    """The caller reaches a refusal written for THIS action, not the backstop.

    IT ASSERTED EQUALITY WITH ``_NINE_REFUSALS[action]`` UNTIL 2026-09-02.
    That was the right idea aimed at the wrong thing: the point was never that
    a dict and a raise agree, it was that the GENERIC BACKSTOP is not what he
    would read. Equality with a table proved that only while the table was
    where the refusal lived, and it broke -- with a KeyError, on an action that
    refuses correctly -- as soon as one did not.

    Asserting the property directly is both narrower and stronger: it holds
    however the refusal is stored, and it is the thing that was actually being
    protected.
    """
    reason = _refusal_for(action)
    assert _GENERIC_BACKSTOP not in reason, (
        "%s falls through to the generic backstop, which says 'not "
        "performable' -- true of every refusing action and explanatory of "
        "none. Give it a reason of its own." % action
    )
    # AND IT IS ABOUT THIS ACTION, which is what stops one action's reason
    # being reachable for another. The backstop names the action too, so this
    # is only meaningful beside the assertion above.
    assert action in reason, action


def test_the_refusals_are_different_strings():
    """THE CONTROL for the two tests above.

    N gaps printing one sentence would satisfy every per-action assertion in
    this section and teach a reader that the sentence carries no information.
    They are distinct, and distinct in their first hundred characters rather
    than only in a trailing clause.

    WITH ONE ACTION IN THE CORPUS, PAIRWISE DISTINCTNESS IS VACUOUSLY TRUE, and
    a check that is vacuously true is one that has stopped running. It was
    called ``test_the_seven_refusals_are_seven_different_strings`` and it
    compared seven strings; the corpus is one, so the comparison it was named
    for cannot happen.

    WHAT REPLACES IT IS THE SAME CLAIM AGAINST A FIXED POINT. The hazard was
    never "two refusals collide" in the abstract -- it was that a refusal
    carries no information. The one string that carries none is the generic
    backstop, so every refusal is required to differ from THAT, whatever the
    corpus size. The pairwise check is kept as well and starts doing work again
    the moment a second action refuses.
    """
    reasons = [_refusal_for(action) for action in REFUSING]
    assert len(set(reasons)) == len(REFUSING)
    assert len({reason[:100] for reason in reasons}) == len(REFUSING)
    # THE FIXED POINT, which does not go vacuous at any corpus size.
    for action, reason in zip(REFUSING, reasons):
        assert _GENERIC_BACKSTOP not in reason, action


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

    IT DRIVES ``preview`` DIRECTLY SINCE 2026-09-05, and the reason is a real
    behaviour change rather than a test convenience. This action's preview
    used to read ``/feed/``, so ``ITEM`` -- deliberately opaque, "an item key
    this server has never parsed" -- never reached a navigation and the block
    rendered for it. The preview now loads THE ITEM'S OWN PERMALINK, so an
    unaddressable item is refused by the READ DOOR before any block exists:

        navigation blocked: 'https://www.linkedin.com/feed/update/an-item-key-
        this-server-has-never-parsed/' is not on the read-only allowlist

    THAT IS THE GUARANTEE GETTING EARLIER, not weaker. ``test_opaque_targets``
    already pins that an opaque target is stopped by ``url_pattern`` on the way
    OUT; it is now also stopped on the way IN, by an allowlist that refuses to
    open a page whose address nobody has measured. So this test asserts what it
    always asserted -- the words, in full, beside what binds them -- over a
    target the gate can actually address.

    AND THE URL IS THE OTHER HALF OF THE BINDING. It is asserted here because
    this is the block that prints it: until 2026-09-05 ``where.url`` was built
    by formatting the WHOLE canonical target, so this very block named the page
    it would act on as ".../feed/update/<urn> :: <his comment>/" -- his words
    inside an address. The words belong in ``text``. They do not belong in a
    url.
    """
    editor = (
        '<div role="textbox" contenteditable="true" aria-label="'
        + dom.COMMENT_EDITOR_LABEL
        + '"></div>'
    )
    permalink = "https://www.linkedin.com/feed/update/%s/" % REACTED_ITEM
    nav = FixtureNavigator({permalink: "<html><body>" + editor + "</body></html>"})
    block = await preview(
        spec_for_action("comment_on_item"),
        target={"item": REACTED_ITEM, "text": COMMENT_A},
        navigator=nav,
        page=browser_page,
    )
    where = block["where"]
    assert where["item"] == REACTED_ITEM
    assert where["text"] == COMMENT_A
    assert where["target"] == REACTED_ITEM + TARGET_JOIN + COMMENT_A
    assert where["target_kind"] == "item_and_text"
    assert where["url"] == permalink, where["url"]
    assert COMMENT_A not in where["url"], where["url"]
    assert nav.gotos == [permalink], nav.gotos


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


def test_every_surface_these_actions_read_is_already_on_the_read_boundary():
    """THE LOAD-BEARING CLAIM OF THE WHOLE WAVE.

    Seven capabilities were added and the read boundary was not touched. That
    is checkable rather than assertable: every url these readers open goes
    through the SAME read door every read tool uses, so if one of them had
    needed a new allowlist entry it would fail here.

    The dict is also checked for CONTENT before it is iterated. A ``for url in
    {}`` loop passes, and a test that passes on an empty dict certifies
    nothing -- so the six surfaces are counted and reconciled against the
    ``state_from`` of the specs themselves.
    """
    # FIVE SURFACES, reconciled rather than counted. ``update_setting`` left
    # the refusing set when it shipped and its surface did NOT leave
    # ``_SURFACE_READS`` -- ``observe`` still reads that page at preview, so
    # the claim being made here still has to hold for it. Dropping it from this
    # reconciliation would have quietly stopped checking the read boundary for
    # an action that now performs on it, which is exactly backwards.
    #
    # IT WAS SIX UNTIL 2026-09-05, and the one that left is the opposite case
    # to ``update_setting``'s: ``feed_item`` lost its LAST CLAIMANT rather
    # than keeping a claimant that stopped refusing. Both actions that
    # declared it were moved onto the page they act on, so the entry pointed
    # at a reader nothing could reach -- and the equality below is what said
    # so, before anybody noticed.
    assert len(writes._SURFACE_READS) == 5
    covered = set(REFUSING) | set(LIFTED)
    state_froms = {spec_for_action(a).state_from for a in covered}
    # THIS WAS A FLAT EQUALITY UNTIL 2026-09-02 and it could not survive
    # ``set_open_to_work`` entering the corpus, for the same reason the preview
    # test could not index ``_SURFACE_READS``: that dict is the FALLBACK
    # FAMILY, not the whole routing table, and this action's surface is read by
    # a branch of ``observe`` above it.
    #
    # SPLIT RATHER THAN LOOSENED, so both directions still bite. Every entry in
    # ``_SURFACE_READS`` must still be claimed by one of these actions -- an
    # orphan entry is a reader nothing reaches -- and every state_from that is
    # NOT in it must be one this file has named, so a new unrouted surface
    # fails here instead of being absorbed.
    assert state_froms & set(writes._SURFACE_READS) == set(writes._SURFACE_READS)
    # THREE BRANCH SURFACES SINCE 2026-09-05, and TWO of them arrived exactly
    # the way this assertion was written to make them arrive: each failed here
    # rather than being absorbed. ``react_to_item`` and then ``comment_on_item``
    # moved off ``feed_item`` -- which loads /feed/ -- onto their own item's
    # permalink, because each was reading a page that was not the one it acts
    # on: the reaction's direction came off other people's controls, and the
    # comment's presence check counted the feed's affordances.
    assert state_froms - set(writes._SURFACE_READS) == {
        "profile_topcard",
        "item_permalink",
        "item_comment_box",
    }
    # AND ``feed_item`` LEFT ``_SURFACE_READS`` WITH ITS LAST CLAIMANT on the
    # same day. The equality above already refuses an orphan -- it is what
    # caught this one -- so the count is asserted separately rather than as a
    # literal that has to be edited every time the table moves.
    assert "feed_item" not in writes._SURFACE_READS
    # AND THE BOUNDARY CLAIM HOLDS FOR THE BRANCH SURFACES TOO. They are
    # asserted separately because none comes with a reader in the table:
    # ``observe`` loads PROFILE_URL directly for one, and formats the spec's
    # own ``url_template`` for the other two.
    assert readonly.is_read_url(writes.PROFILE_URL)
    # THE PERMALINK IS PER-TARGET, which is why these are branches and not
    # table entries -- there is no constant url to put in one. The claim being
    # checked is the same claim: neither fix opened a new surface. This address
    # has been on the read allowlist since 2026-08-31 and both actions have
    # been LOADING it at click time since 2026-09-01; all that changed is that
    # the previews load it too.
    #
    # BOTH ACTIONS ARE BUILT THE SAME WAY HERE, through ``url_target_of``,
    # which is the derivation the write door itself uses. That matters for
    # ``comment_on_item``: its target is ``item :: text``, and formatting the
    # WHOLE target -- which every site did until 2026-09-05 -- produced an
    # address with the operator's comment inside it that this very pattern
    # then refused.
    for action in ("react_to_item", "comment_on_item"):
        spec = spec_for_action(action)
        target = writes._target_for(
            spec,
            REACTED_ITEM
            if action == "react_to_item"
            else {"item": REACTED_ITEM, "text": "Congratulations on the launch."},
        )
        permalink = spec.url_template.format(
            target=writes.url_target_of(spec, str(target))
        )
        # THE TWO ACTIONS MUST BUILD THE SAME STRING for the same item, which
        # is the whole content of the composite-target repair: one of these
        # targets carries a text half and the other does not, and the address
        # cannot know the difference.
        expected = "https://www.linkedin.com/feed/update/%s/" % REACTED_ITEM
        assert permalink == expected, (action, permalink)
        assert readonly.is_read_url(permalink), (action, permalink)
        # THE CONTROL, because "is_read_url returned True" proves nothing
        # unless it can return False on this same family. A query string is
        # the shape the anchored pattern refuses -- and it is also the shape
        # the FEED's own anchors were never read on, which is why no reader
        # here has ever been able to say whether a key on that page is
        # followable.
        assert readonly.is_read_url(permalink + "?utm_source=share") is False
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
    """What survived the 2026-08-30 dissolution, and where each is now.

    ``repost_or_share`` was the quarter of the old speech entry that was about
    somebody ELSE'S item rather than about taste. ``endorse_or_recommend``
    kept its name and lost its reason. The third was NEW that day, and it is
    the rule the endorsement ruling rested on rather than a restatement of it.

    ON 2026-09-24 TWO OF THE THREE LEFT, and this test used to assert all
    three present. OUTWARD-CLASSES-BUILT-BEHIND-GRANTS builds reposting and
    endorsing behind the grant, so both entries moved VERBATIM to
    ``outward_classes.RETIRED_PERMANENT_REFUSALS`` -- kept, not deleted, so the
    measurements they carried can still be found. The third stays: loading a
    third party's profile FOR A MEASUREMENT is a mitigation, and the ruling
    keeps exactly the entries whose grounds are mitigations.
    """
    from linkedin_server import outward_classes

    for name in ("repost_or_share", "endorse_or_recommend"):
        assert name not in PERMANENTLY_FORBIDDEN, name
        assert name in outward_classes.RETIRED_PERMANENT_REFUSALS, name
        assert len(outward_classes.RETIRED_PERMANENT_REFUSALS[name]) > 40, name
    survivor = "load_a_third_partys_profile_to_measure_a_control"
    assert survivor in PERMANENTLY_FORBIDDEN
    assert len(PERMANENTLY_FORBIDDEN[survivor]) > 40


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
    # RETIRED 2026-09-24 and read from where it now lives, VERBATIM. Every
    # claim below is about the TEXT, which did not change; what changed is
    # that the text is a record of a measurement rather than a refusal, so
    # the last lines also pin that the measured counts reached the spec that
    # needs them.
    from linkedin_server import outward_classes

    reason = outward_classes.RETIRED_PERMANENT_REFUSALS["endorse_or_recommend"]

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

    # CARRIED, NOT THROWN AWAY: the counts are the reason endorsing routes
    # through a named member's profile, so they sit in that spec's facts.
    carried = outward_classes.OUTWARD_CLASS_SPECS["endorse_skill"].carried_facts
    for fact in ("13 tracked fixtures", "222 controls", "THIRD PARTY'S PROFILE"):
        assert fact in carried, fact


def test_the_repost_refusal_says_what_survived_and_what_did_not():
    """The narrowing is recorded IN the reason, so the three quarters that
    went cannot be mistaken for something nobody got round to.

    Read from ``outward_classes.RETIRED_PERMANENT_REFUSALS`` since 2026-09-24,
    where the whole entry moved verbatim; its measurement -- the Repost
    control is a disclosure whose menu has never been opened -- is the
    capture ``repost_item`` still needs, and is pinned there too.
    """
    from linkedin_server import outward_classes

    reason = outward_classes.RETIRED_PERMANENT_REFUSALS["repost_or_share"]
    assert "NARROWED" in reason
    assert "post_or_comment_or_like_or_share" in reason
    # What survives is about somebody ELSE'S item, which is the part that was
    # never taste.
    assert "SOMEBODY ELSE'S" in reason.upper()
    carried = outward_classes.OUTWARD_CLASS_SPECS["repost_item"].carried_facts
    assert "aria-expanded='false'" in carried
    assert "3 on the feed and 8 on his profile" in carried


def test_the_claims_that_depend_on_the_destruction_refusal_are_the_measured_ones():
    """A refusal other claims lean on, pinned from BOTH ends and by NAME.

    ``delete_or_withdraw_anything`` carried a note saying five specs cite it in
    ``reversible_by`` (six, once lane L5's ``send_reply`` joined on master).
    THE NOTE WAS WRONG WHEN THIS TEST WAS FIRST WRITTEN, and
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

    THE ENTRY WAS RETIRED 2026-09-24 (OUTWARD-CLASSES-BUILT-BEHIND-GRANTS) AND
    THIS TEST WAS REWRITTEN WITH IT, because "shortening it would silently make
    five reversibility claims wrong at once" was the warning, and the answer
    to the warning is to restate the five, each by name, not to keep the
    entry. This test used to assert the entry present and each of the five
    saying NOBODY with the word "forbidden" in it. What it asserts now is the
    RESTATEMENT: each names the retirement and, where one exists, the record
    in ``outward_classes`` that governs its undo; the three whose undo is still
    NOBODY (an application, a message, a reply) say so on a ground that is not
    this server's refusal; and the record's STATUS in each sentence is the
    record's real status -- so a record that later moves to BUILT turns its
    spec's sentence red until the sentence moves too.

    SIX SINCE THE MERGE OF MASTER, 2026-09-27. ``send_reply`` was built on lane
    L5's branch while this lane retired the entry on its own, and it arrived
    leaning on the refusal. It is restated like the other five, and the rule
    below this test reads EVERY sanctioned spec, so a seventh cannot arrive
    the same way unseen.

    EIGHT SINCE LANE L5'S MERGE OF MASTER 52b55b6, the same day, and the rule
    below is what made that visible rather than a reader: lane L5's follow-up
    built ``connect_from_profile`` and ``message_from_profile`` on its branch
    with the same lean ("Withdrawing an invitation is destruction, which is in
    PERMANENTLY_FORBIDDEN"; "Deletion is permanently forbidden here"). Both are
    restated by name above -- the invitation onto ``withdraw_invitation``'s
    record, as ``send_invitation``'s is, and the message onto delivery, as
    ``send_message``'s is.
    """
    from linkedin_server import outward_classes

    assert "delete_or_withdraw_anything" not in PERMANENTLY_FORBIDDEN
    note = outward_classes.RETIRED_PERMANENT_REFUSALS["delete_or_withdraw_anything"]
    # The retired note still names its own correction -- kept verbatim.
    assert "CORRECTED" in note
    assert "react_to_item does not lean on this" in note

    # THE SIX, BY NAME, and the record each one's undo now rests on -- EIGHT
    # since lane L5's merge of master 52b55b6 (see the docstring).
    restated = {
        "apply_job": ("withdraw_application", "NOBODY"),
        "publish_post": ("delete_own_post", "NOT YET"),
        "comment_on_item": ("delete_own_comment", "NOT YET"),
        "send_invitation": ("withdraw_invitation", "NOT YET"),
        "send_message": (None, "NOBODY"),
        # The sixth, from lane L5, restated at this lane's merge of master.
        "send_reply": (None, "NOBODY"),
        # The seventh and eighth, from lane L5's follow-up, restated at its
        # merge of master 52b55b6. An invitation sent from a profile lands in
        # the same Sent list as send_invitation's, so its undo is the same
        # record; a message sent from a profile is delivered like any other.
        "connect_from_profile": ("withdraw_invitation", "NOT YET"),
        "message_from_profile": (None, "NOBODY"),
    }
    for action, (record, verdict) in restated.items():
        text = spec_for_action(action).reversible_by
        assert text.startswith(verdict), (action, text[:60])
        assert outward_classes.OUTWARD_CLASSES_RULING in text, action
        # The retired refusal appears only as a QUOTED RETRACTION -- "used to
        # say" ahead of the quote -- never as the live reason.
        if "PERMANENTLY_FORBIDDEN" in text:
            head = text[: text.index("PERMANENTLY_FORBIDDEN")]
            assert "used to say" in head, action
        if record is not None:
            status = outward_classes.OUTWARD_CLASS_SPECS[record].status
            assert record in text, (action, record)
            assert status in text, (action, record, status)
    # The four NOBODY verdicts rest on grounds outside this server: LinkedIn's
    # own Help Center for an application, delivery itself for a message, a
    # reply and a message sent from a profile. (Three until lane L5's merge of
    # master 52b55b6 brought message_from_profile.)
    assert "a512388" in spec_for_action("apply_job").reversible_by
    assert "cannot be recalled" in spec_for_action("send_message").reversible_by
    assert "cannot be recalled" in spec_for_action("send_reply").reversible_by
    assert "cannot be recalled" in spec_for_action("message_from_profile").reversible_by

    # THE ONE NAMED IN THE ORIGINAL NOTE THAT DOES NOT BELONG, and what it
    # actually rests on. If somebody later rewrites react's reversible_by to
    # lean on the destruction entry, this is what makes that visible.
    reaction = spec_for_action("react_to_item").reversible_by
    assert "NOBODY" not in reaction
    assert "ON label unmeasured" in reaction


#: The printed fields that state whether, and how, an action can be undone.
_REVERSIBILITY_FIELDS = (
    "reversibility",
    "reversibility_evidence",
    "reversible_by",
    "reversibility_procedure",
)


#: THE PHRASINGS THE TREE USED FOR THE RETIRED REFUSAL, beyond its key names.
#: MEASURED, NOT IMAGINED: "permanently forbidden" was the only one at first,
#: and the cold verification of lane L8 (2026-09-27) then found two TOOL
#: DESCRIPTIONS stating the refusal live in words it did not match --
#: "forbids deletion permanently" (``linkedin_comment_on_item``) and
#: "Deletion is forbidden in this design" (``linkedin_send_reply``). A NEW
#: PHRASING ESCAPES THIS RULE. That is its stated limit, and the reason the
#: needles are listed here rather than implied.
_RETIRED_REFUSAL_PHRASINGS = (
    r"permanently[\s_]+forbidden",
    r"forbids?\s+deletion",
    r"(?:deletion|deleting|withdrawing|withdrawal)\s+(?:is|stays|remains)\s+"
    r"(?:permanently\s+)?forbidden",
    r"forbidden\s+in\s+this\s+design",
)


def _live_retired_refusals(text: str) -> list[str]:
    """Every statement of a retired refusal in ``text`` that is LIVE.

    The needles are the retired keys' own names, read off
    ``outward_classes.RETIRED_PERMANENT_REFUSALS``, and the phrasings above.
    None of the six surviving refusals is an undo, so nothing that states how
    an action is undone has a live reason to cite one. A match is allowed only
    as a QUOTED RETRACTION -- the two-part test
    ``tests/test_a_spec_may_not_assert_what_the_code_denies.py`` applies,
    imported rather than re-derived.
    """
    from linkedin_server import outward_classes
    from tests.test_a_spec_may_not_assert_what_the_code_denies import (
        _is_a_quoted_retraction,
    )

    needle = re.compile(
        "|".join(
            [re.escape(key) for key in outward_classes.RETIRED_PERMANENT_REFUSALS]
            + list(_RETIRED_REFUSAL_PHRASINGS)
        ),
        re.IGNORECASE,
    )
    text = text or ""
    return [
        match.group(0)
        for match in needle.finditer(text)
        if not _is_a_quoted_retraction(text, match)
    ]


def _leans_on_a_retired_refusal(spec: writes.WriteSpec) -> list[tuple[str, str]]:
    """Every place a reversibility field states a retired refusal LIVE."""
    found = []
    for field in _REVERSIBILITY_FIELDS:
        for hit in _live_retired_refusals(getattr(spec, field, None) or ""):
            found.append((field, hit))
    return found


def test_no_sanctioned_spec_states_a_retired_refusal_as_its_undo():
    """ACROSS THE WHOLE SANCTIONED SET, not the six named above.

    The test above names the specs it checks, so it cannot see a seventh --
    which is exactly how the sixth arrived: ``send_reply`` reached this lane's
    merge of master saying "Deletion is permanently forbidden here at any
    confirm level (delete_or_withdraw_anything)", a reversibility claim
    resting on a refusal that no longer existed.
    """
    leaning = {}
    for spec in SANCTIONED_WRITES.values():
        found = _leans_on_a_retired_refusal(spec)
        if found:
            leaning[spec.action] = found
    assert not leaning, (
        "A printed reversibility field states a permanent refusal as a live "
        "reason: %r. Since 2026-09-24 writes.PERMANENTLY_FORBIDDEN holds only "
        "the six mitigations, none of them an undo. Quote the old sentence as "
        "a retraction and say what the undo rests on now." % (leaning,)
    )


def test_the_rule_convicts_the_text_send_reply_arrived_with():
    """SHOWN FAILING on the words that reached the merge, and passing on
    their quoted retraction -- a rule that cannot fail certifies nothing."""
    arrived = (
        "NOBODY, through this server. Deletion is permanently forbidden "
        "here at any confirm level (delete_or_withdraw_anything), so an "
        "un-send does not exist in this design."
    )
    spec = spec_for_action("send_reply")
    planted = dataclasses.replace(spec, reversible_by=arrived)
    assert _leans_on_a_retired_refusal(planted) == [
        ("reversible_by", "Deletion is permanently forbidden"),
        ("reversible_by", "delete_or_withdraw_anything"),
    ]
    quoted = dataclasses.replace(
        spec,
        reversible_by='NOBODY. This field used to say "%s"; it no longer does.'
        % arrived,
    )
    assert _leans_on_a_retired_refusal(quoted) == []
    # And the spec as shipped says it only that way.
    assert _leans_on_a_retired_refusal(spec) == []


async def test_no_sanctioned_write_tool_description_states_a_retired_refusal():
    """THE TOOL DESCRIPTIONS OF THE SANCTIONED WRITES, which a client model
    reads INSTEAD of the spec. The spec-field rule above could not see them,
    and the cold verification of lane L8 found two stating the retired refusal
    live (see ``_RETIRED_REFUSAL_PHRASINGS``). Read off the registry a client
    reads, not off the source."""
    from linkedin_server.server import mcp

    tools = {tool.name: tool for tool in await mcp.list_tools()}
    leaning = {}
    for name in SANCTIONED_WRITES:
        if name in tools:
            found = _live_retired_refusals(tools[name].description or "")
            if found:
                leaning[name] = found
    assert not leaning, (
        "A write tool's description states a retired PERMANENTLY_FORBIDDEN "
        "refusal as live: %r. Quote the old sentence as a retraction and say "
        "what the undo rests on now." % (leaning,)
    )


def test_the_description_rule_convicts_the_two_sentences_it_was_built_for():
    """SHOWN FAILING on the two sentences the verification found, verbatim,
    and passing on their quoted retractions."""
    found = [
        "Not by this server, which forbids deletion permanently and should not "
        "now try to aim one.",
        "Deletion is forbidden in this design at any confirm level, and even "
        "where LinkedIn lets a sender delete a message it does not un-send the "
        "email or un-read what was read.",
    ]
    for sentence in found:
        assert _live_retired_refusals(sentence), sentence
        quoted = 'This used to say "%s"; that refusal was retired.' % sentence
        assert _live_retired_refusals(quoted) == [], quoted


# ---------------------------------------------------------------------------
# 8. (RETIRED 2026-09-27) Aiming ONE invitation control by a NEEDLE
# ---------------------------------------------------------------------------
#
# THIS SECTION HELD THE NEEDLE'S TESTS -- ``dom.INVITE_NEEDLE_JS``,
# ``dom.read_invitation_surface`` and ``writes.aim_invitation`` -- and they
# left with the needle, on the orchestrator's order of 2026-09-27 23:36 (lane
# L5; PEOPLE-DATA-MITIGATIONS, mitigation 6: no write is aimed by a name).
# What they certified -- a third party's name never enters this process to
# AIM -- is kept, and more strongly: the aim is the person's profile LINK,
# compared by the browser against each rail card's own link, and nothing
# compares a name at all. Its tests are
# ``tests/test_an_invitation_is_aimed_by_a_link.py``; the one label the
# preview reads is section 10's, below.


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
#: Derived by MOVING the checked attribute, and the two asserts below are what
#: keep the derivation honest: if a fixture edit stops these replacements
#: matching, DARK_MODE_AFTER silently equals DARK_MODE_MARKUP and every test
#: that verifies "the page changed" passes against a page that did not. That
#: is exactly what happened on 2026-09-03 when the markup gained ids and
#: labels -- caught at collection by the first assert rather than by a green
#: run, which is why it is an assert and not a comment.
DARK_MODE_AFTER = _dm_page(checked="Always on")
# THE GUARDS STAY EVEN THOUGH THE DERIVATION CAN NO LONGER NO-OP. They cost
# nothing and they are what caught this constant the last time the markup
# moved; a guard removed because "it cannot fail now" is a guard nobody
# reinstates when the reason changes.
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
    # **THE CLICK TARGET MOVED ON 2026-09-03 AND THIS ASSERTION MOVED WITH
    # IT.** It pinned the radio input. The first live update_setting proved the
    # input cannot be clicked: LinkedIn covers it with a decorative div, and
    # Playwright retried 23 times over ten seconds with every attempt
    # intercepted, coming back clicks_made 0 with the state correctly reported
    # unchanged.
    #
    # So the aim is the <label> that ACTIVATES the radio. This is a corrected
    # expectation and not a weakened one -- the round trip then landed on the
    # real account, both directions verified, which is what a moved assertion
    # has to be able to point at.
    assert page.clicks == [
        'xpath=//label[normalize-space(.)="Always on"]'
    ], page.clicks
    # AND IT IS STILL A NAME AIM, which is the property that survived the move
    # and the one worth asserting rather than the string alone: the destination
    # appears in the selector, so a page that redrew its three rows in a
    # different order still gets this one.
    assert TO_STATES["update_setting"] in page.clicks[0]
    assert "nth" not in page.clicks[0] and "[1]" not in page.clicks[0]
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
    both = _dm_page(checked="Always off", also_checked="Always on")
    assert both != DARK_MODE_MARKUP
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
DARK_MODE_AS_CHECKBOXES = _dm_page(kind="checkbox")
assert DARK_MODE_AS_CHECKBOXES != DARK_MODE_MARKUP
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

    after = _dm_page(checked="Always on", kind="checkbox")
    # **THE INEQUALITY IS THE GUARD THAT WAS MISSING HERE**, and its absence is
    # why this test failed on ``performed`` rather than on its own setup: the
    # old derivation no-opped, the count guard was satisfied by the UNCHANGED
    # page (the before-state also has exactly one checked), and the whole flow
    # then ran against a page that never moved.
    assert after != DARK_MODE_AS_CHECKBOXES
    assert after.count("checked") == 1
    page = _ClickRecordingPage(browser_page, nav, after)
    result = await writes.perform(nav, page, grant)

    assert page.clicks == [
        'role=checkbox[name="Always on"s]'
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
    # BUILT, NOT REPLACED, for the reason ``_dm_row`` gives at length: the four
    # derivations in this file that were string-replacements all silently
    # no-opped when the markup was corrected, and this one's guard is what
    # caught it.
    #
    # A BUTTON RATHER THAN A DIV, and that is not cosmetic: a bare
    # ``div[role=switch]`` matches no arm of CENSUS_CONTROL_SELECTOR and so
    # produces NO ROW AT ALL -- the first attempt at this test used one and
    # refused at "0 controls are named 'Always on'", one step before the branch
    # it was written for. A button is censused, carries aria-checked, and
    # therefore arrives at the role check.
    broken = _dm_page(
        replace=(
            "Always on",
            '<button role="switch" aria-checked="false" '
            'aria-labelledby="dm-on"></button>',
        )
    )
    assert broken != DARK_MODE_MARKUP
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
        == 'role=radio[name="Always on"s]'
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
    # A PEOPLE RECORD since 2026-09-27 (PREVIEW-NAMES-THE-RESOLVED-TARGET):
    # the name the label carries, sanitised and marked; the rest is held by
    # tests/test_a_preview_names_the_resolved_target.py. Its link is the one
    # HE gave, and its headline ABSENT -- the rail card's is uncaptured.
    assert named["name"] == MEMBER, named
    assert named["link"] == MEMBER_LINK and named["headline"] is None, named
    # IT TELLS HIM TO CHECK IT, and says what it cannot catch. A word that
    # uniquely selects the WRONG person is the one failure this gate has no
    # way to see, and a block that printed a name without saying so would read
    # as corroboration it has not got.
    check = block.get("who_this_would_reach_check", "")
    assert "CHECK IT" in check
    assert "no grant" in check


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
    # HIS TARGET IS NOT WHAT IS BEING SWEPT FOR: his link appears in the
    # retained block legitimately, as ``target`` -- the caller-supplied target
    # a receipt may carry. What must not be there is the string LINKEDIN wrote
    # -- the accessible name of somebody else's control. (His target was his
    # WORD for the person until 2026-09-27; it is the person's link now.)
    label = "Invite " + MEMBER + dom.INVITE_CONTROL_SUFFIX
    assert "who_this_would_reach" not in grant.preview, grant.preview
    assert label not in json.dumps(grant.preview), grant.preview
    assert grant.target == MEMBER_LINK
    # AND NOT IN THE OBSERVATION, which is retained on the grant too -- which
    # is exactly why _read_profile_invitations does not read the label at all.
    assert grant.observation is not None
    assert label not in json.dumps(grant.observation.facts)
    # The returned block DOES carry the person it names, which is the whole
    # point of the pair -- since 2026-09-27 as a people record holding the
    # name inside the label, not the label itself.
    assert block["who_this_would_reach"]["name"] == MEMBER


async def test_two_matches_print_no_name(writes_on, browser_page):
    """THE OTHER MUTATION THE RULING NAMED: a label reaching a SECOND
    control's row.

    Exactly ONE label, the one the needle uniquely selected. Two matches is
    where a name would be least safe to print and most tempting to print
    anyway -- he would be shown one of two people and confirm against it.

    The preview refuses outright here, which is the older half of the rule:
    two cards linking to the profile he gave are AMBIGUOUS, because choosing
    between indistinguishable controls is choosing by position. (The two
    matches were two labels carrying his WORD until 2026-09-27; they are two
    cards carrying his LINK now.)
    """
    two = PROFILE_MARKUP.replace(
        "</body>",
        '<div class="rail-card"><a href="' + MEMBER_LINK + '">x</a>'
        '<button aria-label="Invite Somebody Else'
        + dom.INVITE_CONTROL_SUFFIX
        + '"></button></div></body>',
    )
    assert two != PROFILE_MARKUP
    pages = _nine_pages()
    pages[writes.PROFILE_URL] = two
    nav = FixtureNavigator(pages)
    spec = spec_for_action("send_invitation")

    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(
            spec, target=MEMBER_LINK, navigator=nav, page=browser_page, to_state=None
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
    # His link DOES legitimately appear as the target; what must not appear
    # anywhere else is the LABEL LinkedIn wrote.
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
    real = dom.read_invitation_rail
    calls = {"n": 0}

    async def _ungated(page, segment=None, **kwargs):
        calls["n"] += 1
        reading = dict(await real(page, segment, **kwargs))
        if calls["n"] > 1:
            # A reading that lost its exactly-one condition: two cards now
            # carry his link, and the label read must not happen.
            reading["matches"] = 2
        return reading

    monkeypatch.setattr(dom, "read_invitation_rail", _ungated)
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
    real = dom.read_invitation_rail

    async def _wandered(page, segment=None, **kwargs):
        calls["n"] += 1
        reading = await real(page, segment, **kwargs)
        if calls["n"] > 1:
            # The SECOND read -- the one the label would come from -- finds a
            # different rail. In production that is a page that re-rendered
            # between the aim and the read; here it is arranged, because the
            # guard has to be shown refusing and a fixture page does not move
            # on its own.
            reading = dict(reading)
            reading["controls"] = int(reading["controls"]) + 3
        return reading

    monkeypatch.setattr(dom, "read_invitation_rail", _wandered)
    block, _nav = await _preview_the_refusal(browser_page, "send_invitation")
    assert calls["n"] >= 2, "the label read did not happen at all"
    assert "who_this_would_reach" not in block, block
