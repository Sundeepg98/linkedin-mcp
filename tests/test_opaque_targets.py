"""An opaque target may become performable only if something constrains it.

``writes._opaque_target`` DECLINES TO VALIDATE, deliberately and honestly: a
feed item is addressed by a urn and a member by a needle, and this server has
never read either unshaped -- ``linkedin_surface_census`` substitutes ``<urn>``
and ``<member>`` out before anything is counted, so a census cannot publish an
identifier. A normaliser enforcing ``urn:li:activity:<digits>`` would be
asserting a shape nobody has measured, which is what this package refuses to
do with a selector.

THAT WAS SAFE ONLY WHILE NO OPAQUE-KIND ACTION COULD ACT, and the docstring
said so: *"Both actions that use this hold no url_template, so mint refuses
them a grant at ISSUE... If either is ever made performable, THIS FUNCTION IS
THE FIRST THING THAT MUST CHANGE."*

``react_to_item`` became performable on 2026-09-01 and that guarantee stopped
being true the same day. **The function did not have to change**, and the old
warning aimed at the wrong place: the protection is not validation on the way
IN, it is :data:`writes.WriteSpec.url_pattern` on the way OUT, enforced by
``assert_write_url``, which rebuilds the url from the grant and refuses it
unless the whole string matches an anchored pattern. That is strictly stronger
than validating on arrival, because it also catches a target that changed
between the two.

SO THE WARNING BECOMES A CHECK, which is the point of this file. Every
performable action with an opaque target kind must satisfy ONE of two things:

  * its ``url_template`` interpolates ``{target}``, and its ``url_pattern``
    REJECTS a target that is not the measured shape -- proven here by building
    a url from garbage and asserting the pattern refuses it; or
  * its ``url_template`` never interpolates the target at all, so the target
    cannot reach a navigation. ``send_invitation`` is this case: its target is
    a NEEDLE, which has no shape to enforce, and its aiming is done by
    ``aim_invitation`` refusing anything but exactly one match.

A prose warning nobody re-reads is how this became stale in the first place.
"""

import pytest

from linkedin_server import writes

#: Targets a caller could plausibly send that must never reach a navigation.
#: Not exotic: a slug, a path fragment, a full url, and a traversal attempt.
GARBAGE_TARGETS = [
    "not-a-urn",
    "12345",
    "../../../etc/passwd",
    "https://evil.example.com/",
    "urn:li:activity:111/../../feed",
    "urn:li:activity:abc",
]

_OPAQUE_PERFORMABLE = sorted(
    action
    for action in writes.PERFORMABLE
    if writes.spec_for_action(action).target_kind in writes._OPAQUE_TARGET_KINDS
)


def test_there_is_something_to_check():
    """A parametrized loop over an empty set passes silently.

    If every opaque-kind action stopped being performable this file would go
    green while checking nothing, and the next one to arrive would meet no
    rule at all.
    """
    assert _OPAQUE_PERFORMABLE, (
        "no performable action has an opaque target kind -- if that is "
        "genuinely true this file is dormant, and the assertion is here so "
        "that it is dormant LOUDLY rather than passing as coverage"
    )


@pytest.mark.parametrize("action", _OPAQUE_PERFORMABLE)
def test_an_opaque_target_is_constrained_before_it_can_reach_a_url(action):
    """One of the two protections must hold, and which one is reported."""
    spec = writes.spec_for_action(action)
    assert spec.url_template is not None, action

    if spec.target_kind == "member":
        # A NEEDLE HAS NO SHAPE TO ENFORCE, so the rule for it is absolute
        # rather than pattern-based: it must never reach a url at all. Stated
        # as its own assertion rather than inferred from the template's
        # current text, because "there is no {target} today" and "a needle may
        # never be interpolated" are different claims and only the second is
        # the rule. FOUND BY MUTATION: a template that started interpolating
        # passed the shape-inferred version of this check.
        assert "{target}" not in spec.url_template, (
            "%s addresses a NEEDLE -- the operator's own word for a person -- "
            "and its url_template interpolates it. A needle in a url is a "
            "third party's identity in a navigation." % action
        )

    if "{target}" not in spec.url_template:
        # ROUTE TWO: the target never reaches a navigation. Assert that
        # positively rather than treating it as the absence of route one --
        # a template that silently stopped interpolating would otherwise look
        # like compliance.
        for garbage in GARBAGE_TARGETS:
            built = spec.url_template.format(target=garbage)
            assert garbage not in built, (action, garbage)
        # AND THE CONSTANT URL MUST STILL MATCH ITS OWN PATTERN. Route two
        # skips the garbage-rejection check, which left nothing here asserting
        # the pattern is usable at all -- a pattern of ``^$`` would have
        # passed while making the action permanently unable to build a url.
        # FOUND BY MUTATION.
        assert spec.url_pattern is not None, action
        assert spec.url_pattern.match(spec.url_template), (
            "%s cannot match its own constant url against its own pattern, so "
            "assert_write_url would refuse every call it ever makes."
            % action
        )
        return

    # ROUTE ONE: the pattern must actually refuse what the normaliser accepts.
    assert spec.url_pattern is not None, action
    for garbage in GARBAGE_TARGETS:
        built = spec.url_template.format(target=garbage)
        assert not spec.url_pattern.match(built), (
            "%s builds %r from a garbage target and its own url_pattern "
            "ACCEPTS it. _opaque_target declines to validate on the way in, "
            "so this pattern is the only thing between a caller's string and "
            "a navigation." % (action, built)
        )


@pytest.mark.parametrize("action", _OPAQUE_PERFORMABLE)
def test_the_constraint_still_admits_a_real_target(action):
    """The other half: a rule that refuses everything protects nothing.

    A pattern of ``^$`` would pass the test above and make the action
    unusable, which is a different failure and an invisible one -- nobody
    reports a write that silently never works.
    """
    spec = writes.spec_for_action(action)
    if "{target}" not in spec.url_template:
        # NOT A SKIP, for the reason the sibling file records: a greyed-out
        # line reads like a pass. Route two has the same "still usable" claim
        # in a different shape -- the CONSTANT url must match its own
        # pattern, or assert_write_url refuses every call this action could
        # ever make. Asserted rather than skipped, so both routes leave a
        # green line that means something.
        assert spec.url_pattern.match(spec.url_template), (
            action,
            spec.url_template,
        )
        return
    # BUILT RATHER THAN WRITTEN OUT. It must have the measured SHAPE, and
    # test_no_committed_identity greps tracked SOURCE for urn-shaped
    # literals -- it caught the real one here, correctly, on a public repo
    # under his real name. Constructing it keeps the shape and puts no
    # urn literal in the file.
    real = "urn:li:" + "activity:" + ("1234567890" * 2)[:19]
    built = spec.url_template.format(target=real)
    assert spec.url_pattern.match(built), (action, built)


def test_the_opaque_docstring_records_the_guarantee_it_lost():
    """The correction must stay recorded, so nobody reinstates the warning.

    A PROSE PIN, and a weak instrument -- which is exactly why the two
    executable tests above exist. This guards one thing only: that the
    docstring still says the old guarantee STOPPED BEING TRUE and still names
    where the protection actually lives. The old sentence is quoted inside the
    correction on purpose, so asserting its absence would be wrong.
    """
    doc = (writes._opaque_target.__doc__ or "").upper()
    assert "DECLINES TO VALIDATE" in doc
    assert "URL_PATTERN" in doc
    assert "STOPPED BEING TRUE" in doc
    assert "ASSERT_WRITE_URL" in doc
