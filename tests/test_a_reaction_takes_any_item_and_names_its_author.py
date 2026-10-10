"""A reaction takes any item from its arguments and says WHOSE post it lands on.

Lane NP, child B, 2026-10-10. Two things, each red before it was built. (The
file was first named for a third, the inverse, which was NOT built under the
lead's time box -- its design and the verb-law question its name raises are in
``_audit/2026-10-10-lane-np-named-profile.md``, section B -- and was renamed at
the lead's merge so its name claims only what it holds.)

B1  THE TARGET IS A TOOL ARGUMENT, NOT ONLY HIS OWN ITEM. Nothing in the react
    gate refuses an item that is not his -- ``writes._target_for`` checks the
    urn's SHAPE and ``assert_write_url`` its anchored pattern, and nothing
    anywhere asks whose it is. The tool's Args said "Get it from
    linkedin_my_activity_items, which returns keys only for items established
    to be yours", which described where keys came from while that was the only
    reader handing one out, and read as a gate. It now says where a key can
    come from and what reacting to another member's post costs.

B2  PREVIEW-NAMES-THE-RESOLVED-TARGET. The preview names the RESOLVED POST'S
    AUTHOR -- read off the permalink it would press on, as a people record
    built by ``people_seam.person`` -- and an ``author_kind`` closed token.
    The record lives in the block the preview RETURNS and nowhere a write
    keeps: not ``grant.preview``, not the observation, not a log, not a
    receipt. What is MEASURED and what is DERIVED is in
    ``linkedin_server/item_author.py``'s docstring; the measured shapes are
    pinned against the capture itself below.

Every page here is SYNTHETIC: built from ``linkedin_server.dom``'s own
measured constants and from the STRUCTURE measured on his own post's
permalink capture (``tests/fixtures/live2/own_post.html``), and peopled only
with invented values -- slugs carrying a declared synthetic token, names that
belong to nobody, and the suite's declared item urn.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Optional

import pytest

from linkedin_server import dom, people_data, writes
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    REACTED_ITEM,
    FixtureNavigator,
    browser_page,
    writes_on,
)

FIXTURES = Path(__file__).parent / "fixtures"


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


# ---------------------------------------------------------------------------
# B2 -- the preview names whose post it is
# ---------------------------------------------------------------------------

#: INVENTED PEOPLE. Each slug carries a declared synthetic token (see
#: tests/test_no_committed_identity.py, SYNTHETIC_SLUG_TOKENS); the names and
#: the headline belong to nobody.
_VIEWER_SLUG = "someone-example-viewer"
_VIEWER_NAME = "Sam Example"
_AUTHOR_SLUG = "another-person-example"
_AUTHOR_NAME = "Kai Example"
_AUTHOR_HEADLINE = "Invented headline"
#: A declared synthetic company id (SYNTHETIC_IDS), for an organisation actor.
_ORGANISATION_ID = "902611"


def _actor(*, href: str, name: str, headline: Optional[str]) -> str:
    """ONE actor block, in the structure MEASURED on his own post's permalink
    capture: an image link and a meta link to the same address, the name in
    ``span[dir=ltr] > span[aria-hidden=true]`` inside the title, the degree or
    "You" slot beside it, and the headline inside the description -- the
    title and the description both INSIDE the meta link."""
    description = (
        ""
        if headline is None
        else '<span class="update-components-actor__description">'
        '<span aria-hidden="true">' + headline + "</span>"
        '<span class="visually-hidden">' + headline + "</span></span>"
    )
    return (
        '<div class="update-components-actor__container">'
        '<a class="update-components-actor__image" href="' + href + '">photo</a>'
        '<div class="update-components-actor__meta">'
        '<a class="update-components-actor__meta-link" href="' + href + '">'
        '<span class="update-components-actor__title">'
        '<span class="update-components-actor__single-line-truncate">'
        '<span dir="ltr"><span aria-hidden="true">' + name + "</span>"
        '<span class="visually-hidden">' + name + "</span></span></span>"
        '<span class="update-components-actor__supplementary-actor-info">'
        '<span aria-hidden="true">2nd</span>'
        '<span class="visually-hidden">2nd degree connection</span></span>'
        "</span>" + description + "</a></div></div>"
    )


def _member_href(slug: str) -> str:
    """The actor link's MEASURED shape: the profile, carrying a query."""
    return "https://www.linkedin.com/in/" + slug + "?miniProfileUrn=x"


def _permalink(
    *,
    toggle: str = dom.REACTION_OFF_LABEL,
    actor_href: Optional[str] = None,
    actor_name: str = _AUTHOR_NAME,
    headline: Optional[str] = _AUTHOR_HEADLINE,
    actors: int = 1,
    sidebar: bool = True,
    private_widget: bool = True,
) -> str:
    """One item's permalink, as his own post's capture draws it, with exactly
    the variation asked for. The LEFT SIDEBAR carries HIS identity card and,
    beside it, his private analytics widget -- the pairing measured on the
    capture; the post's ONE toggle sits in its action bar."""
    href = actor_href or _member_href(_AUTHOR_SLUG)
    side = ""
    if sidebar:
        side = (
            '<aside class="scaffold-layout__sidebar">'
            '<div class="profile-card"><a href="/in/' + _VIEWER_SLUG + '/" '
            'class="ember-view profile-card-profile-link">card</a></div>'
            + (
                '<ul class="feed-left-nav-growth-widgets">'
                '<li><a href="/analytics/creator/content/">impressions</a></li></ul>'
                if private_widget
                else ""
            )
            + "</aside>"
        )
    return (
        "<html><body>" + side + "<main>"
        '<div class="feed-shared-update-v2" role="article">'
        + "".join(
            _actor(href=href, name=actor_name, headline=headline)
            for _ in range(actors)
        )
        + '<div class="feed-shared-social-action-bar">'
        '<button aria-label="' + toggle + '">Like</button></div>'
        "</div></main></body></html>"
    )


#: EVERY WORLD DRAWS WHAT ITS NAME SAYS, checked at import -- one reaction
#: toggle each (the shape the gate requires), and the actor count asked for.
for _name, _page, _actors in (
    ("another member's post", _permalink(), 1),
    ("two actors", _permalink(actors=2), 2),
):
    assert _page.count('aria-label="' + dom.REACTION_STATE_PREFIX) == 1, _name
    assert _page.count("update-components-actor__meta-link") == _actors, _name


def _react_url() -> str:
    return spec_for_action("react_to_item").url_template.format(target=REACTED_ITEM)


async def _react_preview(page, html: str) -> dict[str, Any]:
    """The REAL gate, over one frozen permalink. Nothing else is served, so a
    gate reaching for any other page fails on the navigator."""
    return await preview(
        spec_for_action("react_to_item"),
        target=REACTED_ITEM,
        navigator=FixtureNavigator({_react_url(): html}),
        page=page,
    )


def _person(block: dict[str, Any]) -> Any:
    """The record the block names, re-validated as a people record."""
    record = people_data.as_record(block.get("who_this_would_reach"))
    assert isinstance(record, people_data.Person), block.get("who_this_would_reach")
    return record


async def test_the_preview_names_another_members_post_author(writes_on, browser_page):
    """THE CASE THE LIVE PROOF IS FOR: a post by a member he names. The block
    names its author in a people record -- sanitised, marked untrusted -- and
    calls the post another member's."""
    block = await _react_preview(browser_page, _permalink())
    assert block.get("author_kind") == "another_member", block.get("author_kind")
    record = _person(block)
    assert record.name == _AUTHOR_NAME
    assert record.headline == _AUTHOR_HEADLINE
    envelope = block["who_this_would_reach"]
    assert envelope[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    # THE LINK IS NULL BY CONSTRUCTION: the one address this server loaded is
    # the permalink, which is not a profile, and a link read off the page is
    # never put in a preview's record (people_seam's own contract).
    assert envelope["link"] is None
    # No degree: no capture shows another member's degree line on a permalink.
    assert envelope["degree"] is None
    assert block["to_confirm"] is not None
    assert "who_this_would_reach_check" in block


async def test_his_own_post_reads_you(writes_on, browser_page):
    """The actor's link and his own identity card name the same member."""
    block = await _react_preview(
        browser_page,
        _permalink(actor_href=_member_href(_VIEWER_SLUG), actor_name=_VIEWER_NAME),
    )
    assert block.get("author_kind") == "you", block.get("author_kind")
    assert _person(block).name == _VIEWER_NAME


async def test_the_comparison_folds_case_and_percent_encoding(writes_on, browser_page):
    """A vanity segment is case-insensitive on LinkedIn; the comparison is the
    house's own (``named_profile.same_segment``)."""
    shouted = _VIEWER_SLUG.upper().replace("-", "%2D")
    block = await _react_preview(
        browser_page,
        _permalink(actor_href=_member_href(shouted), actor_name=_VIEWER_NAME),
    )
    assert block.get("author_kind") == "you", block.get("author_kind")


async def test_two_actors_name_nobody(writes_on, browser_page):
    """A page drawing two actor blocks -- a reshare carrying the original, say
    -- does not say whose post the ONE toggle belongs to. Nobody is named."""
    block = await _react_preview(browser_page, _permalink(actors=2))
    assert block.get("author_kind") == "unknown"
    assert "who_this_would_reach" in block
    assert block["who_this_would_reach"] is None


async def test_an_organisation_actor_is_not_a_member(writes_on, browser_page):
    """An actor linking to an organisation Page is not ONE member."""
    block = await _react_preview(
        browser_page,
        _permalink(actor_href="https://www.linkedin.com/company/" + _ORGANISATION_ID + "/"),
    )
    assert block.get("author_kind") == "unknown"
    assert "who_this_would_reach" in block
    assert block["who_this_would_reach"] is None


async def test_no_identity_card_names_the_author_and_says_unknown(writes_on, browser_page):
    """WITHOUT HIS OWN CARD THE COMPARISON HAS NOTHING TO COMPARE AGAINST. The
    author is still named -- the page drew one member -- but whether the post
    is his cannot be said."""
    block = await _react_preview(browser_page, _permalink(sidebar=False))
    assert block.get("author_kind") == "unknown"
    assert _person(block).name == _AUTHOR_NAME


async def test_a_card_without_his_private_widget_is_not_proof_of_him(writes_on, browser_page):
    """THE CARD IS HIS ONLY BESIDE SOMETHING ONLY HE IS SHOWN. A profile card
    alone could be an author card a page draws; the private analytics widget
    beside it is what makes it the signed-in member's own."""
    block = await _react_preview(browser_page, _permalink(private_widget=False))
    assert block.get("author_kind") == "unknown"
    assert _person(block).name == _AUTHOR_NAME


async def test_a_headline_not_drawn_is_absent(writes_on, browser_page):
    """ABSENT, never the empty string: ``people_data.ABSENT``."""
    block = await _react_preview(browser_page, _permalink(headline=None))
    assert _person(block).headline is people_data.ABSENT


async def test_the_author_reaches_no_grant_no_observation_and_no_log(
    writes_on, browser_page, caplog
):
    """WHERE THE NAME MUST NOT GO, checked on everything a write keeps. The
    grant's retained preview was assigned BEFORE the namer ran, the
    observation holds the reaction toggle's reading only, and the grant's
    target is the urn he gave."""
    caplog.set_level(logging.DEBUG)
    block = await _react_preview(browser_page, _permalink())
    assert _person(block).name == _AUTHOR_NAME
    grant = writes._GRANTS[block["to_confirm"]]
    assert grant.target == REACTED_ITEM
    for kept in (grant.preview, grant.observation, grant.target):
        assert _AUTHOR_NAME not in repr(kept), type(kept).__name__
        assert _AUTHOR_HEADLINE not in repr(kept), type(kept).__name__
    assert "who_this_would_reach" not in grant.preview
    assert "author_kind" not in grant.preview
    assert _AUTHOR_NAME not in caplog.text
    assert _AUTHOR_SLUG not in caplog.text


async def test_the_author_reaches_no_receipt(writes_on, browser_page):
    """A RECEIPT CARRIES ONLY THE TARGET HE SUPPLIED. The write is driven end
    to end over two frozen renders of the one permalink -- the OFF page gate 5
    presses, the ON page the verification reads -- and the author's name and
    headline are nowhere in what ``perform`` hands back."""
    block = await _react_preview(browser_page, _permalink())
    assert _person(block).name == _AUTHOR_NAME
    grant = consume(block["to_confirm"], action="react_to_item", target=REACTED_ITEM)
    reacted = _permalink(toggle="Reaction button state: Like")
    receipt = await writes.perform(
        FixtureNavigator({_react_url(): [_permalink(), reacted]}), browser_page, grant
    )
    assert receipt["performed"] is True, receipt.get("verification")
    assert _AUTHOR_NAME not in repr(receipt)
    assert _AUTHOR_HEADLINE not in repr(receipt)
    assert "who_this_would_reach" not in receipt


def _observation(state: str) -> writes.Observation:
    """A reading as ``observe`` records one, built directly: what the namer
    compares against is its STATE, and nothing here loads a page."""
    return writes.Observation(
        target=REACTED_ITEM,
        target_kind="item_urn",
        facts={},
        facts_url=_react_url(),
        state=state,
        state_why="",
        state_url=_react_url(),
        same_page_as_action=True,
        receipt="not-a-real-receipt",
        observed_at=time.monotonic(),
    )


class _RaisingPage:
    """A page whose every read raises -- a live render that went away."""

    def locator(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("the page did not read")


async def test_a_failed_read_names_nobody_and_never_raises():
    """A READ FOR A HUMAN NEVER RAISES. Every field comes back unread -- None,
    never a zero standing in -- and the namer names nobody."""
    from linkedin_server import item_author

    reading = await item_author.read_item_author(_RaisingPage())
    assert reading["person"] is None
    assert reading["actor_is_viewer"] is None
    assert reading["actor_links"] is None
    block = item_author.name_the_item_author(
        _observation("no_reaction"), reading, {"marker": "kept"}
    )
    assert block["marker"] == "kept"
    assert block["author_kind"] == "unknown"
    assert block["who_this_would_reach"] is None


def test_a_reading_of_a_different_render_names_nobody():
    """THE PAGE IS CHECKED, NOT ASSUMED: the namer's own re-read of the toggle
    must agree with the observation the grant was minted from, or the author
    it read may be some other render's."""
    from linkedin_server import item_author

    person = people_data.Person.from_page(name=_AUTHOR_NAME).envelope()
    reading = {
        "toggle_state": "reacted",
        "toggles_drawn": 1,
        "actor_links": 1,
        "member_actor_links": 1,
        "names_drawn": 1,
        "headlines_drawn": 0,
        "viewer_cards": 1,
        "analytics_links_in_main": 0,
        "actor_is_viewer": False,
        "person": person,
    }
    block = item_author.name_the_item_author(_observation("no_reaction"), reading, {})
    assert block["author_kind"] == "unknown"
    assert block["who_this_would_reach"] is None
    # And the same reading, agreeing with its observation, names the author.
    agreed = item_author.name_the_item_author(_observation("reacted"), reading, {})
    assert agreed["author_kind"] == "another_member"
    assert agreed["who_this_would_reach"] == person


async def test_his_own_post_capture_draws_the_measured_shapes(browser_page):
    """THE MEASUREMENT, PINNED AGAINST THE CAPTURE IT CAME FROM.

    ``tests/fixtures/live2/own_post.html`` is his own post's permalink. Its
    names and labels are sanitised to ``x``, so it can show the SHAPES and
    nothing about whose they are:

    * one actor meta link in ``main``, to a member (``/in/``), with one name
      and one headline inside it;
    * one identity card in the sidebar beside his private analytics widget;
    * ZERO per-post analytics anchors in ``main`` -- the post-analytics link
      suggested as an own-post signal is ABSENT on his own post's permalink,
      so its absence cannot mean "another member";
    * the comparison returns True over it, and that proves only that it CAN
      return True on his own post: every segment in the capture is the same
      placeholder, so no capture can show it returning False on another
      member's post. That half is DERIVED.
    """
    from linkedin_server import item_author

    async def _refuse(route) -> None:  # noqa: ANN001 - playwright route
        # THE CAPTURE KEEPS ITS IMAGE AND TRACKER ADDRESSES' SHAPES, so a
        # browser loading it fetches them: every request is refused in the
        # page's own route first. The network guard caught this test without
        # it -- fourteen requests, each refused before it left.
        await route.abort()

    await browser_page.route("**/*", _refuse)
    html = (FIXTURES / "live2" / "own_post.html").read_text(encoding="utf-8")
    await browser_page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
    reading = await item_author.read_item_author(browser_page)
    assert reading["actor_links"] == 1, reading
    assert reading["member_actor_links"] == 1, reading
    assert reading["names_drawn"] == 1, reading
    assert reading["headlines_drawn"] == 1, reading
    assert reading["viewer_cards"] == 1, reading
    assert reading["analytics_links_in_main"] == 0, reading
    assert reading["actor_is_viewer"] is True, reading
