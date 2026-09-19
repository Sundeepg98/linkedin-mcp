"""The three tools wired on 2026-09-05 keep the properties their readers were built to.

**A PROPERTY ASSERTED ONLY IN A DOCSTRING IS THE DEFECT THIS REPOSITORY HAS
NAMED MORE THAN ONCE**, and each of these three modules says so about itself:
``groups.py`` asserts its name-freedom on ``inspect.signature`` rather than in
prose, ``premium.py`` prints its three-state split on every branch it can
return, and ``notify_cost.py`` says it contains no code that could open the
notifications page. **Wiring a reader is exactly where such a property is
undone**, because the tool is a new consumer and a careless payload can flatten
what the reader was careful to keep apart.

So these are STRUCTURAL checks over ``server.py``'s own syntax tree, not
behavioural ones. Nothing here opens a browser. Each is shown FAILING on a
planted mutation before it is asserted against the real source, because a check
that cannot fail certifies nothing -- and in a file this size a check that
merely greps would pass on anything.

## WHAT IS NOT CLAIMED

These do not test that the tools WORK. Live verification was attempted on
2026-09-05 and blocked -- the shared Chrome was down -- and no page has been
opened through any of them. What is pinned here is the SHAPE of what they may
say, which is the half a later edit is most likely to break by accident.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SERVER = REPO / "linkedin_server" / "server.py"

#: Words that would name a collapsed premium answer. **THE POINT OF THIS TOOL
#: IS THAT THERE IS NO SUCH FIELD.** Three states were named about Premium and
#: one load of the entitlement page refutes at most one of them, so a boolean
#: -- or any single key promising an answer -- would silently pick between the
#: two that stay live.
COLLAPSING_KEYS = (
    "is_premium",
    "has_premium",
    "premium",
    "entitled",
    "premium_active",
    "subscribed",
)


def _tree(source: str) -> ast.AST:
    return ast.parse(source)


def _function(source: str, name: str) -> ast.AsyncFunctionDef:
    for node in ast.walk(_tree(source)):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError("%s is not defined in this source" % name)


def _returned_dicts(func: ast.AST) -> list[ast.Dict]:
    return [
        node.value
        for node in ast.walk(func)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)
    ]


# ---------------------------------------------------------------------------
# The detectors, each shown failing on a plant, before anything is asserted
# ---------------------------------------------------------------------------


def _verdict_is_spread_whole(source: str) -> bool:
    """True when every returned dict carries a ``**`` spread of the verdict.

    A spread is what keeps ``settles`` and ``leaves_open`` on the payload
    whatever branch ``premium_entitlement`` took. Naming a few fields by hand
    is how they get dropped.
    """
    func = _function(source, "linkedin_premium_status")
    dicts = _returned_dicts(func)
    if not dicts:
        return False
    for node in dicts:
        starred = [
            value
            for key, value in zip(node.keys, node.values)
            if key is None and isinstance(value, ast.Name) and value.id == "verdict"
        ]
        if not starred:
            return False
    return True


def _publishes_no_collapsing_key(source: str) -> bool:
    func = _function(source, "linkedin_premium_status")
    for node in _returned_dicts(func):
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if key.value in COLLAPSING_KEYS:
                    return False
    return True


def _never_names_the_notifications_page(source: str) -> bool:
    """True when the precondition tool holds no notifications address.

    The module it wires contains no code that could open that page, ON PURPOSE
    -- taking the AFTER reading spends the operator's unread state. A tool that
    reintroduced the address would undo the one property the module was built
    around, and it would look like a convenience in a diff.
    """
    func = _function(source, "linkedin_notify_cost_precondition")

    # THE DOCSTRING IS EXCLUDED, AND THAT IS A DECISION RATHER THAN A
    # CONVENIENCE. This check fired on the real tool the first time it ran --
    # on the sentence in its own docstring saying it never opens that page.
    # **A DOCSTRING CANNOT NAVIGATE.** The property is about code that could
    # open the surface, and a guard that cannot tell a quotation from a claim
    # forces the prose to stop naming the thing it promises not to do, which
    # makes the documentation worse to protect a check. This repository has
    # already paid for that once, on a different guard, and the note it left
    # was to describe the term without spelling it -- the better fix, where the
    # structure allows it, is the one taken here.
    body = list(func.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]

    for statement in body:
        for node in ast.walk(statement):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if "notification" in node.value.lower() and "/" in node.value:
                    return False
            if isinstance(node, ast.Attribute) and node.attr in {
                "NOTIFICATIONS_URL",
                "cost_delta",
            }:
                return False
    return True


def test_the_spread_detector_fires_on_a_flattened_payload():
    """PLANT: the verdict picked apart into hand-named fields."""
    planted = (
        "async def linkedin_premium_status():\n"
        "    reading = None\n"
        "    verdict = None\n"
        "    return {'ok': True, 'state': verdict['state']}\n"
    )
    assert not _verdict_is_spread_whole(planted)


def test_the_spread_detector_stays_silent_on_a_spread_payload():
    """The other direction. A detector that flags everything is not one."""
    planted = (
        "async def linkedin_premium_status():\n"
        "    verdict = None\n"
        "    return {'ok': True, **verdict}\n"
    )
    assert _verdict_is_spread_whole(planted)


def test_the_collapsing_key_detector_fires_on_a_planted_boolean():
    """PLANT: the single boolean this tool exists not to publish."""
    planted = (
        "async def linkedin_premium_status():\n"
        "    verdict = None\n"
        "    return {'ok': True, 'is_premium': True, **verdict}\n"
    )
    assert not _publishes_no_collapsing_key(planted)


def test_the_notifications_detector_fires_on_a_planted_address():
    """PLANT: the address whose load spends the thing being measured."""
    planted = (
        "async def linkedin_notify_cost_precondition():\n"
        "    url = 'https://www.linkedin.com/notifications/'\n"
        "    return {'ok': True}\n"
    )
    assert not _never_names_the_notifications_page(planted)


def test_the_notifications_detector_fires_on_the_after_half():
    """PLANT: cost_delta, the function that needs the reading nobody may take.

    A SECOND PLANT BECAUSE THE PROPERTY HAS TWO WAYS TO BE BROKEN and an
    address check only sees one of them. Calling the delta shaper is the other,
    and it is the likelier of the two -- it reads as finishing the job.
    """
    planted = (
        "async def linkedin_notify_cost_precondition():\n"
        "    return {'ok': True, 'delta': notify_cost.cost_delta(a, b)}\n"
    )
    assert not _never_names_the_notifications_page(planted)


def test_the_notifications_detector_does_not_fire_on_a_docstring():
    """A DOCSTRING CANNOT NAVIGATE, and this is why that is asserted.

    The check fired on the real tool the first time it ran -- on the sentence
    in its own docstring promising it never opens that page. A guard that
    cannot tell a quotation from a claim makes the prose stop naming the thing
    it promises not to do, which is a worse document bought to keep a check
    quiet. The plant below is the exact shape that fired.

    IT IS PINNED IN BOTH DIRECTIONS: the plant above, with the address in a
    STATEMENT, still fails. So the exclusion is a scope decision rather than a
    hole.
    """
    planted = (
        "async def linkedin_notify_cost_precondition():\n"
        '    """It never opens /notifications/ and cannot."""\n'
        "    return {'ok': True}\n"
    )
    assert _never_names_the_notifications_page(planted)


def test_the_notifications_detector_stays_silent_on_the_precondition_shape():
    planted = (
        "async def linkedin_notify_cost_precondition():\n"
        "    reading = await notify_cost.read_notifications_badge(page)\n"
        "    return {'ok': True, **notify_cost.measurability(reading)}\n"
    )
    assert _never_names_the_notifications_page(planted)


# ---------------------------------------------------------------------------
# The assertions, through detectors that have been shown able to fail
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def source() -> str:
    return SERVER.read_text(encoding="utf-8")


def test_premium_returns_the_verdict_whole(source):
    """THE THREE-STATE PROPERTY. Every branch keeps its settles/leaves_open.

    ``premium_entitlement`` names one of five states and prints, on every one
    of them, what the reading settles and what it leaves open -- because a load
    of the entitlement page separates "not entitled" from "entitled" and does
    NOTHING about whether a Premium panel renders on a job posting. Spreading
    the verdict is what carries that sentence to the caller. Picking fields out
    by hand is how it gets lost, and it would look tidier in a diff.
    """
    assert _verdict_is_spread_whole(source)


def test_premium_publishes_no_single_collapsed_answer(source):
    """The same property from the other side, and the likelier regression.

    Adding ``is_premium`` beside the verdict would not remove anything; it
    would just give a caller a field to read INSTEAD of the split. That is the
    failure mode, and it is why this checks for the key rather than for the
    absence of the split.
    """
    assert _publishes_no_collapsing_key(source), COLLAPSING_KEYS


def test_the_precondition_tool_cannot_spend_what_it_measures(source):
    """It never names the notifications page and never calls the delta shaper.

    ``notify_cost`` ships a PRECONDITION rather than a measurement: it answers
    whether today is a day on which the cost could be measured, from a badge
    reading that costs no page load. The AFTER half spends the operator's
    unread state and is his to spend, so the module contains no code that could
    take it -- and this asserts the tool did not put it back.
    """
    assert _never_names_the_notifications_page(source)


def test_the_newsletter_tool_refuses_on_every_badge_condition(source):
    """Three refusals, not one: unreadable BEFORE, unreadable AFTER, and MOVED.

    The reader states the obligation and does not discharge it -- the caller
    owns reading the pending-invitation badge either side of the load and
    refusing when it cannot be read. A tool that checked only the before
    reading would look like it had done this and would answer over a load that
    consumed an invitation.
    """
    func = _function(source, "linkedin_newsletter_subscriptions")
    refusals = [
        node
        for node in ast.walk(func)
        if isinstance(node, ast.Return)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "_badge_refusal"
    ]
    assert len(refusals) == 3, (
        "expected three badge refusals (unreadable before, unreadable after, "
        "moved); found %d" % len(refusals)
    )


def test_the_helper_is_not_on_the_tool_surface(source):
    """``_badge_refusal`` sits BEFORE the first decorator, never between one
    and its def.

    This block added four defs at once and one of them is not a tool. The
    defect ``tests/test_every_tool_is_on_the_surface.py`` exists for is exactly
    a helper inserted between an ``@mcp.tool()`` and the ``async def`` it
    decorated -- the tool silently deregisters and the helper takes its place,
    with the COUNT UNCHANGED. That guard asks the registry; this one asks the
    syntax tree, so the two cannot fail the same way.
    """
    tree = _tree(source)
    decorated: dict[str, bool] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            decorated[node.name] = bool(node.decorator_list)
    assert decorated.get("_badge_refusal") is False, (
        "_badge_refusal carries a decorator; if it took an @mcp.tool() it is "
        "now published as a tool and something else stopped being one"
    )
    for name in (
        "linkedin_premium_status",
        "linkedin_newsletter_subscriptions",
        "linkedin_notify_cost_precondition",
    ):
        assert decorated.get(name) is True, "%s lost its decorator" % name
