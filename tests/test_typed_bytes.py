"""The bytes typed must be the bytes the preview showed. Asserted, not promised.

THE OPERATOR'S TYPING RULING CARRIED THREE CONDITIONS, and two of them are
structural -- a named-and-measured control, and text the caller supplied
rather than this server composing it. Both are enforced by where the code
lives. The THIRD is *"the exact text verbatim in the preview"*, and that one
is a promise about a string: nothing about the shape of the code makes it
true, so it is the one condition that could rot silently while everything
still looked right.

This file turns it into an assertion, in two independent ways:

  1. **STRUCTURALLY.** The one ``page.fill`` call site in this package must
     take its text from ``_text_component_of(spec, grant.target)`` and from
     nowhere else. Read off the AST, so a future edit that interpolates,
     truncates, strips or decorates the string fails here rather than typing
     something he never read.

  2. **BY ROUND TRIP.** The text a caller supplies survives normalisation into
     the canonical target and comes back out of it byte for byte -- including
     the awkward cases: unicode, emoji, urls, quotes, leading and trailing
     interior whitespace, and a string long enough to be near the cap.

WHY BOTH. The AST test proves the WIRING and would pass if normalisation
mangled the text; the round trip proves the VALUE and would pass if the fill
site typed something else entirely. Neither alone is the claim.

WHAT MAKES THE PREVIEW HALF TRUE WITHOUT A THIRD TEST: the text IS the target,
or half of it. ``_render`` prints the target, ``mint`` binds the token to it,
and ``consume`` refuses a token whose rebuilt target does not match. So "the
preview showed these bytes" and "the grant carries these bytes" are the same
statement by construction, and this file only has to close the gap between the
grant and the fill.
"""

import ast

import pytest

from linkedin_server import writes

_SOURCE = open(writes.__file__, encoding="utf-8").read()
_TREE = ast.parse(_SOURCE)

#: Texts that a normaliser could plausibly mangle. Each is here for a reason
#: rather than for volume: the emoji is multi-byte, the quotes end string
#: literals, the url carries a colon and slashes, the newline-free padding
#: checks that INTERIOR whitespace is not collapsed, and the long one sits
#: under the cap so it must be accepted rather than refused.
AWKWARD_TEXTS = [
    "plain english",
    "unicode: naive cafe resume",
    "emoji test",
    'quotes "double" and \'single\' and `back`',
    "https://example.com/a?b=c&d=e#f",
    "two  interior   spaces",
    "trailing punctuation!!!",
    "a" * 400,
]


def _fill_calls():
    """Every ``page.fill`` call in ``writes.py``, as AST nodes."""
    found = []
    for node in ast.walk(_TREE):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "fill":
            found.append(node)
    return found


def test_there_is_exactly_one_place_in_this_package_that_types():
    """The whole design of the allowlist entry, asserted here as well.

    ``readonly.SANCTIONED_MUTATIONS`` is keyed by (path, function, kind) and
    the scanner counts call sites, so ONE drain point is what keeps the
    guarantee readable. This is the same property from the other side: a
    second literal ``page.fill`` anywhere in this module fails here, with a
    message naming the line, before it ever reaches the scanner.
    """
    calls = _fill_calls()
    assert len(calls) == 1, [node.lineno for node in calls]


def test_the_fill_types_the_grants_own_text_and_nothing_else():
    """STRUCTURAL HALF: the text argument must come from the extractor.

    Not "contains a call to it" -- IS one. A future edit writing
    ``_text_component_of(...) + signature`` or ``.strip()`` or an f-string
    around it fails here, because the argument node would no longer be a bare
    Call to that name.
    """
    call = _fill_calls()[0]
    assert len(call.args) >= 2, ast.unparse(call)
    text_arg = call.args[1]

    # The call site drains a queue, so the literal argument is the loop
    # variable. Follow it to its assignment rather than requiring the
    # extractor call to be written inline -- the queue IS the design.
    assert isinstance(text_arg, ast.Name), ast.unparse(call)

    sources = []
    for node in ast.walk(_TREE):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "_text_component_of":
                sources.append(node)
    assert sources, (
        "nothing in writes.py calls _text_component_of, so whatever the one "
        "fill types, it is not provably a slice of the grant's target"
    )
    # And the ONLY thing appended to the fill queue must be that call's result.
    appended = [
        node
        for node in ast.walk(_TREE)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "append"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "fill_plan"
    ]
    assert len(appended) == 1, [ast.unparse(a) for a in appended]

    # THE ARGUMENT MUST BE THE CALL ITSELF, not merely contain it.
    #
    # FOUND BY MUTATION: an earlier version of this test compared the
    # unparsed source against the substring "_text_component_of(spec,
    # grant.target)", and `_text_component_of(spec, grant.target) + " #hiring"`
    # PASSED -- the substring is still in there. That mutation is precisely the
    # failure the operator's condition forbids: this server composing text and
    # typing it under his name. So the check is on the NODE TYPE. A BinOp, an
    # f-string, a .strip(), a slice or a call wrapping it are all a different
    # node and all fail.
    pushed = appended[0].args[0]
    assert isinstance(pushed, ast.Tuple) and len(pushed.elts) == 2, ast.unparse(
        appended[0]
    )
    text_expr = pushed.elts[1]
    assert isinstance(text_expr, ast.Call), (
        "the text pushed onto the fill queue is %r, which is not a bare call. "
        "Anything wrapping, appending to or trimming the grant's own text is "
        "this server composing what it types." % ast.unparse(text_expr)
    )
    assert isinstance(text_expr.func, ast.Name), ast.unparse(text_expr)
    assert text_expr.func.id == "_text_component_of", ast.unparse(text_expr)
    assert [ast.unparse(a) for a in text_expr.args] == [
        "spec",
        "grant.target",
    ], ast.unparse(text_expr)
    assert not text_expr.keywords, ast.unparse(text_expr)


@pytest.mark.parametrize("text", AWKWARD_TEXTS)
def test_a_posts_text_survives_the_target_round_trip(text):
    """VALUE HALF, for the one-component case.

    ``publish_post``'s target IS the text, so the round trip is the whole
    normalisation path: what a caller hands in must be what the fill types.
    """
    spec = writes.spec_for_action("publish_post")
    canonical = writes._target_for(spec, text)
    assert writes._text_component_of(spec, canonical) == text.strip(), text


@pytest.mark.parametrize("text", AWKWARD_TEXTS)
def test_a_comments_text_survives_the_round_trip_beside_its_subject(text):
    """VALUE HALF, for the two-component case.

    A composite target joins a subject and the content. The content must come
    back out unchanged and the SUBJECT must not bleed into it -- which is the
    failure a naive split would produce on any text containing the separator,
    and is why ``_clean_target_part`` refuses one that does.
    """
    spec = writes.spec_for_action("comment_on_item")
    # BUILT, NOT WRITTEN OUT. This held HIS REAL POST until 2026-09-01 --
    # the permalink censused that morning -- and it reached a commit on a
    # PUBLIC repo under his real name before test_no_committed_identity
    # caught it. It could not catch it sooner: that guard sweeps TRACKED
    # files, and this file was untracked until the commit that published
    # it. Constructing the urn keeps the measured shape and puts no
    # activity id in the source at all.
    urn = "urn:li:" + "activity:" + ("1234567890" * 2)[:19]
    canonical = writes._target_for(spec, {"item": urn, "text": text})
    assert writes._text_component_of(spec, canonical) == text.strip(), text
    assert urn not in writes._text_component_of(spec, canonical)


def test_a_text_carrying_the_separator_is_refused_rather_than_split_wrong():
    """The case that would silently type half a string.

    If the separator were permitted inside a component, a two-part target
    could canonicalise ambiguously and the fill would type from the wrong
    side of the join. The refusal is what makes the round trip above safe.
    """
    spec = writes.spec_for_action("comment_on_item")
    with pytest.raises(writes.WriteAttemptError):
        writes._target_for(
            spec,
            {"item": "urn:li:activity:1", "text": "a" + writes.TARGET_JOIN + "b"},
        )


def test_only_declared_typing_actions_can_reach_the_extractor():
    """An action that types must declare a target this module can split.

    ``update_setting`` is the case worth naming: its target HAS a value
    component and that value is a RADIO DESTINATION, clicked and never typed.
    "Has a text component" and "types it" are different claims, which is why
    ``TYPING_ACTIONS`` is a set rather than a test on ``target_kind``.
    """
    assert "update_setting" not in writes.TYPING_ACTIONS
    for action in writes.TYPING_ACTIONS:
        spec = writes.spec_for_action(action)
        assert spec.target_kind in writes._COMPOSITE_TARGET_KINDS, action

    non_splittable = writes.spec_for_action("react_to_item")
    with pytest.raises(writes.WriteAttemptError):
        writes._text_component_of(non_splittable, "urn:li:activity:1")
