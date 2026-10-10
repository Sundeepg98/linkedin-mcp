"""A reaction says WHOSE post it lands on, and it has an inverse.

Lane NP, child B, 2026-10-10. Three things, each red before it was built:

B1  THE TARGET IS A TOOL ARGUMENT, NOT ONLY HIS OWN ITEM. Nothing in the react
    gate refuses an item that is not his -- ``writes._target_for`` checks the
    urn's SHAPE and ``assert_write_url`` its anchored pattern, and nothing
    anywhere asks whose it is. The tool's Args said "Get it from
    linkedin_my_activity_items, which returns keys only for items established
    to be yours", which described where keys came from while that was the only
    reader handing one out, and read as a gate. It now says where a key can
    come from and what reacting to another member's post costs.

Every page here is SYNTHETIC: built from ``linkedin_server.dom``'s own
measured constants and from the STRUCTURE measured on his own post's
permalink capture (``tests/fixtures/live2/own_post.html``), and peopled only
with invented values -- slugs carrying a declared synthetic token, names that
belong to nobody, and the suite's declared item urn.
"""

from __future__ import annotations

import pytest

from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    REACTED_ITEM,
    FixtureNavigator,
    browser_page,
    writes_on,
)


async def _tool(tool_name: str):
    """What a CLIENT reads: the registered tool, not the source."""
    from linkedin_server.server import mcp

    tools = {tool.name: tool for tool in await mcp.list_tools()}
    return tools[tool_name]


def _flat(text: str) -> str:
    """Whitespace collapsed to single spaces. A docstring WRAPS, so a phrase
    split across two source lines is not ``in`` the raw text -- and a ``not
    in`` over raw text then passes on the very sentence it is meant to forbid.
    MEASURED on this file's first run: the old Args line carried "keys only
    for items" and "established to be yours" on two lines, and the negative
    check passed against it."""
    return " ".join(str(text or "").split())


async def _description(tool_name: str) -> str:
    """The registered description, flattened. FastMCP lifts a docstring's
    ``Args:`` section OUT of it and into each parameter's schema, so an
    argument's sentence is read with :func:`_argument` instead."""
    return _flat((await _tool(tool_name)).description or "")


async def _argument(tool_name: str, argument: str) -> str:
    """The sentence a client reads for ONE argument: its schema description,
    flattened."""
    tool = await _tool(tool_name)
    properties = (tool.parameters or {}).get("properties") or {}
    return _flat((properties.get(argument) or {}).get("description") or "")


# ---------------------------------------------------------------------------
# B1 -- the item is the caller's argument, and it need not be his
# ---------------------------------------------------------------------------


async def test_the_react_tool_says_its_key_comes_from_its_arguments():
    """THE ARGUMENT'S SENTENCE NAMES EVERY SOURCE OF A KEY AND WHAT ANOTHER
    MEMBER'S POST COSTS.

    Red before: the ``item`` argument read "Get it from
    linkedin_my_activity_items, which returns keys only for items established
    to be yours" and named no other source -- while nothing in the gate checks
    whose the item is.
    """
    item = await _argument("linkedin_react_to_item", "item")
    assert item, "the item argument carries no description at all"
    assert "keys only for items established to be yours" not in item, item
    assert "linkedin_my_activity_items" in item, item
    assert "linkedin_read_named_profile" in item, item
    assert "author kind" in item, item
    assert "notifies that member" in item, item


async def test_the_react_tool_says_nothing_checks_whose_item_it_is():
    """THE GATE'S REAL SHAPE, stated where a caller reads it. The urn's shape
    is checked; its owner is not."""
    description = await _description("linkedin_react_to_item")
    assert "NOTHING IN THIS GATE CHECKS WHOSE ITEM IT IS" in description, (
        description
    )


async def test_a_post_that_is_not_his_previews_like_any_other(writes_on, browser_page):
    """THE BEHAVIOUR B1 DESCRIBES, pinned rather than asserted in prose: the
    preview reads the item's own permalink, finds its one OFF toggle, and
    mints a token -- for an item no reader of his own activity returned. No
    ownership refusal exists to fire."""
    from linkedin_server import dom
    from linkedin_server.writes import preview, spec_for_action

    spec = spec_for_action("react_to_item")
    item_url = spec.url_template.format(target=REACTED_ITEM)
    page = (
        "<html><body><main>"
        '<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>'
        "</main></body></html>"
    )
    nav = FixtureNavigator({item_url: page})
    block = await preview(spec, target=REACTED_ITEM, navigator=nav, page=browser_page)
    assert nav.gotos == [item_url], nav.gotos
    assert block["direction"]["currently"] == "no_reaction"
    assert block["to_confirm"] is not None
