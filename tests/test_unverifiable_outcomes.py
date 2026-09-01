"""The pairing rule that keeps ``apply_job``'s defect from coming back.

THE OPERATOR LIFTED THE VERIFICATION STANDARD ON 2026-09-01. An unverifiable
outcome became a shippable outcome, provided the gate SAYS SO -- names what
would have confirmed the act, why this server cannot read it, and what he must
do himself to find out.

THAT LIFT IS NOT A LICENCE TO SHIP THE OLD DEFECT AGAIN. It is the opposite,
and the distinction is the entire content of the ruling:

    A check that CANNOT PASS may never ship as though it might.

``apply_job`` carried exactly that for months. Its ``to_state`` was
``"applied"`` and it was compared against a reader returning ``saved`` /
``not_saved`` / ``unknown``, so the comparison was false on every reading it
could ever take -- and it was presented as a verification. Nothing caught it
because nothing asserted that the surface could answer the question.

So the rule these tests enforce has two halves, and each fails a different
thing:

1. **THE PAIRING.** Every performable action has EXACTLY ONE of {a branch in
   ``_verify_after``, a declared ``unverifiable``}. Neither is an action that
   silently falls through to somebody else's reader -- which is how apply
   ended up reading the Saved tab. Both is worse: a declaration used as cover
   for a comparison that still runs.

2. **THE ANSWERABILITY.** Where a branch exists, the reader it calls must be
   able to RETURN the value the branch compares against. This is checked from
   the same objects the branch uses, not from a list kept beside them.

And one behavioural proof, because the first two are structural: a declared
unverifiable action must reach NO comparison at all. Not a comparison that
returns early -- none. It is given a navigator that detonates on contact.
"""

import ast
import dataclasses

import pytest

from linkedin_server import writes

_SOURCE = open(writes.__file__, encoding="utf-8").read()
_TREE = ast.parse(_SOURCE)


def _function(name: str):
    for node in ast.walk(_TREE):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    raise AssertionError("%s not found in writes.py" % name)


def _actions_named_in(node) -> set[str]:
    """Every action name this subtree compares ``spec.action`` against.

    Reads ``==`` and ``in (...)`` alike, because a branch written either way
    is a branch. A NEGATIVE comparison (``!=``) is deliberately NOT counted as
    a branch for the action it names -- ``spec.action != "unfollow_company"``
    is the fallback that swallowed apply, and treating it as a branch for
    unfollow would let exactly that fallthrough look like coverage.
    """
    found: set[str] = set()
    for cmp_node in ast.walk(node):
        if not isinstance(cmp_node, ast.Compare):
            continue
        left = cmp_node.left
        if not (
            isinstance(left, ast.Attribute)
            and left.attr == "action"
            and isinstance(left.value, ast.Name)
            and left.value.id == "spec"
        ):
            continue
        for op, comparator in zip(cmp_node.ops, cmp_node.comparators):
            if isinstance(op, ast.NotEq):
                continue
            for const in ast.walk(comparator):
                if isinstance(const, ast.Constant) and isinstance(const.value, str):
                    found.add(const.value)
    return found


def _branch_for(action: str):
    """The ``if`` node whose test names this action, or None."""
    for node in ast.walk(_function("_verify_after")):
        if isinstance(node, ast.If) and action in _actions_named_in(node.test):
            return node
    return None


def _verified_actions() -> set[str]:
    return _actions_named_in(_function("_verify_after"))


def test_the_branch_reader_finds_the_branches_that_exist():
    """The AST reader is an instrument, so it gets a control.

    A NAMING CHANGE IN ``_verify_after`` WOULD OTHERWISE EMPTY THIS FILE
    SILENTLY, and an empty corpus passes every test below it. This asserts the
    reader still finds the branches known to be there.
    """
    found = _verified_actions()
    for action in ("update_setting", "follow_company", "apply_job"):
        assert action in found, (action, sorted(found))
    # The negative comparison must NOT register as a branch -- that fallback
    # is what swallowed apply, and counting it would hide the next one.
    assert "unfollow_company" not in _actions_named_in(
        ast.parse('if spec.action != "unfollow_company":\n    pass\n')
    )


@pytest.mark.parametrize("action", sorted(writes.PERFORMABLE))
def test_every_performable_action_either_verifies_or_declares_it_cannot(action):
    """EXACTLY ONE of {a verification branch, a declared unverifiable}.

    NEITHER is the ``apply_job`` shape: an action with no branch of its own,
    falling through to a reader built for a different question. BOTH is worse
    -- a declaration that says the outcome cannot be confirmed, sitting on top
    of a comparison that runs anyway and produces something a reader will
    treat as evidence.
    """
    spec = writes.spec_for_action(action)
    has_branch = _branch_for(action) is not None
    declares = spec.unverifiable is not None

    assert has_branch or declares, (
        "%s is performable with NO verification branch and NO unverifiable "
        "declaration. It will fall through to another action's reader, which "
        "is exactly what apply_job did." % action
    )
    assert not (has_branch and declares), (
        "%s both declares its outcome unverifiable AND carries a branch in "
        "_verify_after. One of the two is a lie, and the dangerous one is the "
        "branch: a comparison that runs is a comparison somebody reads as "
        "evidence." % action
    )


def _stage_states_for(action: str) -> set[str] | None:
    """The states this action's branch can return, from the stage it reads.

    Two AST hops, both to the REAL objects: the branch names a reader, the
    reader names a ``_TrackerStage``, and the stage declares ``present`` and
    ``absent``. Nothing here is a list kept alongside the code -- a list is
    what drifts, and drift is the disease.
    """
    branch = _branch_for(action)
    if branch is None:
        return None
    readers = {
        node.func.id
        for node in ast.walk(branch)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    states: set[str] = set()
    for reader in readers:
        try:
            fn = _function(reader)
        except AssertionError:
            continue
        for name in ast.walk(fn):
            if isinstance(name, ast.Name) and name.id.endswith("_STAGE"):
                stage = getattr(writes, name.id, None)
                if stage is not None:
                    states.add(stage.present)
                    states.add(stage.absent)
    return states or None


@pytest.mark.parametrize("action", sorted(writes.PERFORMABLE))
def test_a_tracker_verification_can_return_the_state_it_compares_against(action):
    """THE ANSWERABILITY HALF, checked where it can be checked exactly.

    This is ``apply_job``'s bug stated as an assertion. Its branch read the
    Saved stage, whose states are ``saved`` / ``not_saved``, while its
    ``to_state`` was ``applied`` -- so no reading the branch could take would
    ever equal what it was compared against.

    Actions whose branch reads no tracker stage are skipped rather than
    guessed at: ``update_setting`` re-reads a radio group and
    ``follow_company`` re-reads a list, and inventing a check for them here
    would be a check that could not fail, which is the disease one floor up.
    """
    spec = writes.spec_for_action(action)
    states = _stage_states_for(action)
    if states is None:
        pytest.skip("%s does not verify through a tracker stage" % action)
    assert spec.to_state in states, (
        "%s compares its outcome against to_state=%r, and the tracker stage "
        "its branch reads can only ever return %s. That comparison cannot "
        "pass on any reading it could take -- which is the exact shape "
        "apply_job carried until 2026-08-31."
        % (action, spec.to_state, sorted(states))
    )


class _Detonates:
    """Any attribute touched at all is a failure.

    Not a mock that records calls -- one that makes the call impossible. The
    property under test is that a declared-unverifiable action reaches NO
    comparison, and a recorder would let the navigation happen and then
    complain about it afterwards.
    """

    def __init__(self, what: str):
        self._what = what

    def __getattr__(self, name):
        raise AssertionError(
            "a declared-unverifiable action touched %s.%s -- it must not read, "
            "navigate or compare anything, because there is nothing that "
            "could answer it" % (self._what, name)
        )


async def test_a_declared_unverifiable_action_reaches_no_comparison():
    """The behavioural proof, because the two tests above are structural.

    ``_verify_after`` is handed a navigator and a page that raise on ANY
    attribute access. If the declaration is honoured, neither is touched.
    """
    spec = dataclasses.replace(
        writes.spec_for_action("save_job"),
        unverifiable=writes.Unverifiable(
            surface_that_would_confirm="a surface that does not exist",
            why_it_cannot="it does not exist",
            what_he_must_do="go and look yourself",
        ),
    )
    state, why, landed = await writes._verify_after(
        _Detonates("navigator"),
        _Detonates("page"),
        spec,
        writes.WriteGrant(
            action=spec.action, target="1234567", token="t", minted_at=0.0
        ),
        None,
    )
    assert state == writes.UNKNOWN
    assert landed == ""
    assert "go and look yourself" in why
    assert "DECLARED unverifiable outcome" in why


async def test_the_detonating_double_actually_detonates():
    """The control for the test above.

    A double that quietly returned ``None`` would make that test pass whether
    or not the early return exists. This is the smallest possible proof that
    the instrument bites.
    """
    with pytest.raises(AssertionError, match="must not read, navigate"):
        _Detonates("navigator").goto
