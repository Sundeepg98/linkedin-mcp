"""The four properties ``linkedin_group_memberships`` was built to hold.

A property argued in a docstring is the defect this repository has named more
than once. These are the four claims the groups wiring makes, asserted over
the syntax tree and over behaviour, with every detector SHOWN FAILING on a
plant before anything is asserted through it.

    1. NO NAME CAN LEAVE IT -- and the tool takes no parameter at all, which
       is the strongest available form of the ruling ``groups.py`` implements.
    2. IT ADDS NOTHING TO ``dom.py`` -- the module ``server.py``
       feature-detects on, where a name can re-arm an irreversible broadcast.
    3. THE WALK CARRIES NO ``page.evaluate`` WAIVER -- the reason the reader
       could live outside ``dom.py`` at all.
    4. NO BRANCH REPORTS A COST OF ZERO -- a badge at zero cannot distinguish
       "consumed nothing" from "nothing to consume", and a silent zero is the
       failure this whole cost path exists to prevent.

**NOTHING HERE OPENS A BROWSER.** Every assertion is over source or over pure
functions.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from linkedin_server import groups, groups_page, server

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

TOOL = "linkedin_group_memberships"


def _tree(name: str) -> ast.AST:
    return ast.parse((PACKAGE / name).read_text(encoding="utf-8"))


def _function(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == name:
                return node
    return None


# ---------------------------------------------------------------------------
# 1. NO NAME CAN LEAVE IT
# ---------------------------------------------------------------------------

def test_the_tool_takes_no_parameter_at_all():
    """THE RULING IN ITS STRONGEST FORM.

    ``groups.py`` asserts that no NAME is a parameter of any of its functions.
    The tool goes one step further and takes NOTHING -- so there is no
    argument a caller could pass that a future edit might forward into a
    reader, and no slug, id or needle can enter this surface from outside.
    """
    node = _function(_tree("server.py"), TOOL)
    assert node is not None, f"{TOOL} is not defined in server.py"
    args = node.args
    assert not args.args and not args.posonlyargs and not args.kwonlyargs
    assert args.vararg is None and args.kwarg is None


def test_the_reader_takes_a_page_and_nothing_else():
    """The same property one level down, asserted on the live signature."""
    params = list(
        inspect.signature(groups_page.read_group_memberships).parameters
    )
    assert params == ["page"]


def test_the_shaper_below_it_is_still_name_free():
    """``groups.py``'s own property, re-asserted from its new consumer.

    Wiring a module is exactly when its safety property is most likely to be
    quietly widened -- somebody adds a ``name`` parameter "just in case" the
    caller has one. It has no such parameter today and this fails the day it
    does, from the file that would benefit.
    """
    for name in ("group_identifier", "membership_tally", "disjoint"):
        params = set(inspect.signature(getattr(groups, name)).parameters)
        assert not (params & {"name", "title", "label", "text", "slug"}), (
            f"groups.{name} grew a name-shaped parameter: {sorted(params)}"
        )


def test_the_tool_hands_every_href_to_the_shaper_and_holds_none(monkeypatch):
    """Behavioural, not structural: what the reader RETURNS carries no href.

    ``groups.membership_tally`` publishes a CONSTANT ``href_shape`` literal,
    never a shape of its input, so the only variable strings in the payload
    are the numeric identifiers. This asserts that over the real return value
    rather than trusting the chain.
    """
    tally = groups.membership_tally(
        ["/groups/12345678/?invitedBy=SOMETOKEN", "/groups/nodejs-people/"]
    )
    assert tally["identifiers"] == ["12345678"]
    assert tally["href_shape"] == groups.PUBLISHED_HREF
    assert tally["refused"] == {"identifier_is_not_numeric": 1}
    for value in tally["identifiers"]:
        assert set(value) <= set("0123456789")


# ---------------------------------------------------------------------------
# 2. IT ADDS NOTHING TO ``dom.py``
# ---------------------------------------------------------------------------

def test_the_feature_detected_name_is_still_undefined_on_dom():
    """DEFINING THIS NAME ON ``dom`` RE-ARMS AN IRREVERSIBLE BROADCAST.

    ``server.py`` lifts ``linkedin_publish_post``'s audience refusal with
    ``callable(getattr(dom, "read_post_composer_audience", None))``. It is the
    only feature-detection site in the package. This wave put its reader in a
    module of its own precisely so that it could not touch that one, and this
    is the assertion rather than the promise.
    """
    from linkedin_server import dom

    assert not callable(getattr(dom, "read_post_composer_audience", None))
    assert server._composer_audience_is_readable() is False


def test_the_groups_reader_does_not_live_in_dom():
    """The structural half. A future tidy-up that moves it back turns red."""
    dom_names = {
        node.name
        for node in ast.walk(_tree("dom.py"))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "read_group_memberships" not in dom_names
    assert "_stopping_ancestor" not in dom_names


# ---------------------------------------------------------------------------
# 3. NO ``page.evaluate`` WAIVER
# ---------------------------------------------------------------------------

def _evaluate_calls(source: str) -> list[str]:
    """Every ``.evaluate``/``.evaluate_handle`` attribute call in a source."""
    out: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in {"evaluate", "evaluate_handle"}:
                out.append(node.func.attr)
    return out


def test_the_evaluate_detector_fires_on_a_plant():
    """A CHECK THAT CANNOT FAIL CERTIFIES NOTHING."""
    assert _evaluate_calls("async def f(page):\n    return await page.evaluate('1')\n")
    assert _evaluate_calls(
        "async def f(page):\n    return await page.evaluate_handle('1')\n"
    )


def test_the_evaluate_detector_is_not_a_grep():
    """The other direction: the WORD in a docstring is not a call.

    Without this the detector could be a grep wearing an AST's costume -- and
    ``groups_page.py``'s own docstring says ``page.evaluate`` four times while
    calling it zero times, so this distinction is load-bearing here rather
    than hypothetical.
    """
    assert not _evaluate_calls('"""We do not call page.evaluate here."""\n')


def test_the_groups_reader_calls_no_evaluate():
    """THE PROPERTY THAT LET THIS MODULE EXIST OUTSIDE ``dom.py``."""
    source = (PACKAGE / "groups_page.py").read_text(encoding="utf-8")
    assert "page.evaluate" in source, (
        "the docstring should still explain why there is no evaluate here; if "
        "that prose is gone this test is checking nothing interesting"
    )
    assert _evaluate_calls(source) == []


def test_the_tool_body_calls_no_evaluate_either():
    """The wiring is where a shortcut would actually be taken."""
    node = _function(_tree("server.py"), TOOL)
    assert _evaluate_calls(ast.unparse(node)) == []


# ---------------------------------------------------------------------------
# 4. NO BRANCH REPORTS A COST OF ZERO
# ---------------------------------------------------------------------------

def _reading(state: str, value=None, key: str = "pending") -> dict:
    return {"state": state, key: value}


ZERO_PAIR = {"invitations": _reading("read", 0)}
ABOVE_PAIR = {"invitations": _reading("read", 3)}
UNREADABLE = {"invitations": _reading("unreadable")}


@pytest.mark.parametrize(
    "before, after, state, measured",
    [
        (ZERO_PAIR, ZERO_PAIR, "degenerate", False),
        (ABOVE_PAIR, ABOVE_PAIR, "unmoved", True),
        (ABOVE_PAIR, {"invitations": _reading("read", 2)}, "moved", True),
        (UNREADABLE, ZERO_PAIR, "uncertified", False),
        (ZERO_PAIR, UNREADABLE, "uncertified", False),
        ({}, {}, "uncertified", False),
    ],
)
def test_every_verdict_is_reachable_and_labelled(before, after, state, measured):
    """All four verdicts, each from an input where it is the only answer."""
    out = groups_page.cost_certification(before, after)
    assert out["state"] == state
    assert out["measured"] is measured


def test_a_zero_pair_is_never_reported_as_a_cost_of_zero():
    """THE ONE THAT MATTERS. A 0 -> 0 pair looks perfectly good.

    Both halves readable, no error anywhere, nothing moved -- and the honest
    answer is still "this measured nothing". A payload carrying a zero here
    would read as "no cost" and mean "no experiment".
    """
    out = groups_page.cost_certification(ZERO_PAIR, ZERO_PAIR)
    assert out["state"] == "degenerate"
    assert out["measured"] is False
    assert out["certifies"] is None

    # NO TOP-LEVEL FIELD IS A NUMERIC ZERO. The raw counter readings under
    # ``counters`` are exempt on purpose -- that is the evidence, and a
    # before/after of 0 belongs there. What must not exist is a SUMMARY field
    # a caller could read as "the cost was zero".
    #
    # ``bool`` IS EXCLUDED BY TYPE AND THAT IS NOT PEDANTRY. The first version
    # of this assertion was ``0 not in [...]`` and it FAILED -- on
    # ``measured: False``, because ``False == 0`` in Python. A test asserting
    # "no zero here" that fires on a boolean is a test that would have to be
    # weakened to pass, and weakening it is how the real check gets lost.
    summary = [
        value for key, value in out.items() if key != "counters"
    ]
    numeric_zeros = [
        value
        for value in summary
        if isinstance(value, (int, float)) and not isinstance(value, bool)
        and value == 0
    ]
    assert numeric_zeros == [], numeric_zeros
    assert "UNMEASURABLE" in out["why"]


def test_a_move_outranks_a_degenerate_sibling():
    """A counter that moved is the finding, whatever the others did."""
    out = groups_page.cost_certification(
        {"invitations": _reading("read", 0),
         "notifications": _reading("read", 2, key="unread")},
        {"invitations": _reading("read", 0),
         "notifications": _reading("read", 1, key="unread")},
    )
    assert out["state"] == "moved"
    assert "notifications" in out["why"]


def test_a_second_counter_rescues_a_degenerate_bracket():
    """WHY THE TOOL BRACKETS WITH TWO COUNTERS AND NOT ONE.

    This is the exact reading the first live run produced -- invitations at
    zero, notifications at one, neither moving -- and it is the reason the
    verdict was NOT degenerate. **The cheapest repair for a degenerate
    instrument is a second instrument, not a better argument about the first.**
    """
    pair = {
        "invitations": _reading("read", 0),
        "notifications": _reading("read", 1, key="unread"),
    }
    out = groups_page.cost_certification(pair, dict(pair))
    assert out["state"] == "unmoved"
    assert out["counters"]["invitations"]["verdict"] == "unmoved_at_zero"
    assert out["counters"]["notifications"]["verdict"] == "unmoved_above_zero"


def test_unmoved_still_refuses_to_certify_that_the_load_is_free():
    """THE LIMIT NO FUTURE NON-ZERO BADGE REPAIRS.

    Every counter this package can read is a nav badge for a DIFFERENT
    surface. Nothing establishes that a groups load touches one, so the
    strongest verdict speaks for those counters and not for this load. A
    caller reading ``unmoved`` as "free" is the misreading this string exists
    to block, so the string is asserted rather than trusted to survive edits.
    """
    out = groups_page.cost_certification(ABOVE_PAIR, ABOVE_PAIR)
    assert out["state"] == "unmoved"
    assert "DIFFERENT surface" in out["certifies"]
    assert "not a statement that the load is free" in out["certifies"]


# ---------------------------------------------------------------------------
# The third navigation, which is the whole answer to the predecessor's blocker
# ---------------------------------------------------------------------------

def test_the_tool_returns_to_the_feed_to_take_the_after_reading():
    """THE PREDECESSOR'S BLOCKER, ANSWERED IN THE CONTROL FLOW.

    A wave declined to wire this on the grounds that the groups page carries
    no counter. It does not -- measured, both counters read UNREADABLE there.
    The answer is that a tool need not certify its cost from the page it
    loads: it navigates BACK to a page that carries the instrument. That third
    navigation is the entire cost of the ruling and it is asserted here so
    that removing it as an "optimisation" turns this red.
    """
    node = _function(_tree("server.py"), TOOL)
    targets: list[str] = []
    for call in [n for n in ast.walk(node) if isinstance(n, ast.Call)]:
        if isinstance(call.func, ast.Attribute) and call.func.attr == "goto":
            for arg in call.args:
                targets.append(ast.unparse(arg))
    gotos = [t for t in targets if "URL" in t]
    assert len(gotos) == 3, gotos
    assert gotos[0].endswith("FEED_URL")
    assert "GROUPS_URL" in gotos[1]
    assert gotos[2].endswith("FEED_URL")


def test_the_tool_declares_the_page_loads_it_takes():
    """Three loads, said out loud in the payload rather than left to count."""
    source = ast.unparse(_function(_tree("server.py"), TOOL))
    assert "'pages_loaded': 3" in source or '"pages_loaded": 3' in source


# ---------------------------------------------------------------------------
# 5. A ZERO IS NEVER PUBLISHED AS "HE BELONGS TO NO GROUP"
# ---------------------------------------------------------------------------

def _zero_reading(**over) -> dict:
    base = {
        "anchors": 10,
        "controls": 22,
        "climbs_exhausted": 0,
        "memberships": {"distinct": 0},
    }
    base.update(over)
    return base


def test_a_zero_from_a_blind_reader_is_about_the_instrument():
    """Three separate ways the reader can be blind, each landing correctly.

    A zero from a reader that could not see is a fact about the instrument.
    Reporting it as a fact about the account is the defect this repository has
    recorded on three surfaces; here it is asserted rather than avoided.
    """
    for over in (
        {"anchors": 0},
        {"controls": 0},
        {"climbs_exhausted": 3},
    ):
        out = groups_page.interpret_zero(_zero_reading(**over))
        assert out["state"] == "instrument", over
        assert out["about_the_account"] is False


def test_a_clean_walk_resolving_nothing_is_AMBIGUOUS_and_says_so():
    """THE HONEST BRANCH, AND IT IS NOT A HEDGE.

    A page of suggestions alone -- which is what a group-less account draws --
    is indistinguishable from a restyle that moved the per-row control,
    because no known-empty groups account exists to test against. The reader
    must not pick the flattering branch.
    """
    out = groups_page.interpret_zero(_zero_reading())
    assert out["state"] == "ambiguous"
    assert out["about_the_account"] is None
    assert "NOTHING HERE CAN SEPARATE THEM" in out["why"]


def test_no_branch_ever_says_he_belongs_to_no_group():
    """The claim that must not exist, asserted over every reachable branch."""
    # THE FORBIDDEN PHRASES INCLUDE THEIR NEGATIONS, and the first draft of
    # this test tried to exempt one by string surgery -- stripping the exact
    # sentence "It is not reported as 'he belongs to no group'." before
    # checking. THAT WAS THE WRONG FIX and this repository already has the
    # rule for it: a NEGATED write verb still reads as a write, so the
    # exemption list carries a control asserting each entry really does make
    # the claim. Parking a negation in an exemption is how the real check
    # gets lost. The prose was reworded instead, so the phrase does not
    # appear here in any form and this test needs no exemption at all.
    forbidden = ("belongs to no group", "has no groups", "no memberships")
    for reading in (
        _zero_reading(),
        _zero_reading(anchors=0),
        _zero_reading(controls=0),
        _zero_reading(climbs_exhausted=1),
        _zero_reading(memberships={"distinct": 5}),
    ):
        why = groups_page.interpret_zero(reading)["why"]
        for claim in forbidden:
            assert claim not in why, (claim, why)


def test_a_nonzero_reading_has_no_zero_to_interpret():
    out = groups_page.interpret_zero(_zero_reading(memberships={"distinct": 5}))
    assert out["state"] == "not_zero"
    assert out["about_the_account"] is None


def test_the_reader_attaches_the_zero_interpretation_to_every_reading():
    """Structural: the field cannot be forgotten by a future edit."""
    source = (PACKAGE / "groups_page.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = _function(tree, "read_group_memberships")
    body = ast.unparse(node)
    assert "interpret_zero" in body
    assert "zero_reading" in body
