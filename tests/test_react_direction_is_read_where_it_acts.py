"""The direction ``react_to_item`` prints must be read where the click lands.

THE DEFECT THIS FILE WAS WRITTEN AGAINST, measured live on 2026-09-05 while
previewing an un-react on one of the operator's own items::

    where.read_from_url        https://www.linkedin.com/feed/
    where.url                  https://www.linkedin.com/feed/update/<urn>/
    same_page_as_the_action    false
    what_the_page_showed       controls 3, off_state 3, permalinks 0
    direction.currently        no_reaction
    direction.after            reacted

All three controls it read were on ``/feed/`` and belonged to OTHER PEOPLE'S
posts. The item itself already carried a reaction -- measured independently
through ``linkedin_surface_census(surface="feed_item")``, which loads that
item's own permalink and found one control and one ``1 reaction 1``. So the
gate offered ``no_reaction -> reacted`` for an item that was already reacted,
and the operator's confirm decision rested on a reading of three strangers'
posts.

WHY THE SUITE DID NOT ALREADY CATCH IT. The verification after the click asks
whether the control MOVED. A toggle moves in either direction, so it reports
success whichever way it went -- a direction check that cannot report the
wrong direction is the defect one level up, and this repo has catalogued ten
instances of exactly that.

WHERE IT CAME FROM, established from history rather than inferred.
``state_from="feed_item"`` was correct while ``react_to_item`` REFUSED: the
read existed to give a refusal a fresh measurement and there was no
``url_template`` to point at -- ``_SURFACE_READS``'s own comment still says
"none holds a url_template". Commit ``d74178f`` (2026-09-01) gave the spec its
``url_template`` and its ``url_pattern`` and did not touch ``state_from``; the
diff contains no ``state_from`` line at all. It is a leftover, not a boundary
and not a page-load budget.

THE FOUR CASES, and the first three are the ones the wave was asked to prove
in both directions:

  1. a target that is ALREADY REACTED must never be offered as
     ``no_reaction -> reacted``
  2. an UNREACTED target must still be offered as ``no_reaction -> reacted``
  3. a MIXED page must still refuse
  4. the reading must be taken on the page the click lands on, and the block
     must say so

TWO MORE ARE HERE BECAUSE THE FIX MOVED WHICH READING DECIDES, and neither
was asked for. A page that drew NOTHING must read unknown and never
``no_reaction`` -- absent is not off, and this repo has ten catalogued
instances of that collapse, four of them in instruments built to catch it.
And the preview's reading must agree with ``_live_control``'s, over the same
frozen world, on all three worlds: those two are compared against ONE
``from_state`` field at opposite ends of a write, and until this fix they came
off different pages, so their agreement was a property of nothing.

RED, ON THE CODE BEFORE THE FIX. All eight cases below failed against
``HEAD`` (``e0dc8f9``) on 2026-09-05, run in an isolated copy of the tree so
nothing was stashed out from under a concurrent writer::

  case 1   Failed: DID NOT RAISE <class 'WriteAttemptError'>
  case 2   AssertionError: the gate asked for
           'https://www.linkedin.com/feed/', which this test did not freeze.
           It froze ['https://www.linkedin.com/feed/update/urn:li:activity:
           7400000000000000004/'].
  case 3   the same navigator AssertionError, raised out of pytest.raises
           rather than caught by it
  case 3b  the same, on the empty page
  case 4   assert False is True, on same_page_as_the_action
  parity   the same navigator AssertionError, on all three worlds

AND THE PRE-FIX BLOCK ITSELF, printed by a throwaway probe over the SAME two
frozen worlds -- the sharpest statement of the defect there is, because the
two columns are one block::

                          permalink UNREACTED     permalink REACTED
  gotos                   ['.../feed/']           ['.../feed/']
  read.facts_url          .../feed/               .../feed/
  read.state_url          .../feed/               .../feed/
  same_page_as_the_action false                   false
  where.url               .../feed/update/<urn>/  .../feed/update/<urn>/
  what_the_page_showed    controls 3, off 3       controls 3, off 3
  direction.currently     no_reaction             no_reaction
  direction.after         reacted                 reacted
  to_confirm issued       True                    True

**THE TWO COLUMNS ARE IDENTICAL.** The gate's direction was not merely read
from the wrong page -- it was INSENSITIVE TO THE TARGET'S OWN STATE, and it
issued a confirm token either way. ``where.url`` named the permalink the whole
time, so the block told him the right page and measured the wrong one.

``read.page_loads`` READ 1 IN BOTH COLUMNS AND STILL DOES. It is derived from
``facts_url == state_url``, and both were the feed, so the one number that
looks like it would notice a two-surface gate reported the honest answer for a
gate whose two ends were the same wrong page. It is not asserted below.

Every page here is built from ``linkedin_server.dom``'s own measured
constants, never typed a second time, so a fixture cannot drift away from the
strings the reader looks for.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    REACTED_ITEM,
    FixtureNavigator,
    browser_page,
    writes_on,
)
from tests.test_writes import _REACTION_ON_LABEL

#: THE PERMALINK SHAPE: exactly one reaction control, which is what the item
#: permalink was MEASURED to draw on 2026-08-31 -- the same census reading 3
#: on the feed and 8 on his profile. That count is the whole reason this
#: action is aimed at a permalink, and it is the shape ``_live_control``
#: already requires at click time.
_ONE_OFF = (
    "<html><body>"
    '<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>'
    "</body></html>"
)

#: The same page with the ON label substituted. The LABEL is not derived -- it
#: was measured 2026-09-04 as ``Reaction button state: Like`` -- but a page
#: wearing it has to be built, because every capture in this repo predates the
#: operator's first reaction.
_ONE_ON = (
    "<html><body>"
    '<button aria-label="' + _REACTION_ON_LABEL + '"></button>'
    "</body></html>"
)
assert _ONE_ON != _ONE_OFF, (
    "the reacted page and the unreacted page are the same string, so every "
    "case below would run against one world and could never turn red."
)

#: TWO CONTROLS DISAGREEING. Not a page anybody has seen on a permalink --
#: which is the point: it is the shape whose direction cannot be settled, and
#: the gate must refuse rather than pick one.
_MIXED = (
    "<html><body>"
    '<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>'
    '<button aria-label="' + _REACTION_ON_LABEL + '"></button>'
    "</body></html>"
)

#: THE FEED, standing in for what the defect actually read: three controls,
#: all OFF, all on other people's posts. Count 3 is the number the live
#: preview reported on 2026-09-05.
#: PARENTHESISED, and it was not on the first draft: ``*`` binds tighter than
#: ``+``, so ``"<button ...>" + LABEL + '"></button>' * 3`` builds ONE button
#: with three closing fragments. Measured -- the reader reported ``controls
#: 1`` for a page this file called three. A fixture that does not draw what
#: its name says makes every count asserted over it a fiction.
_FEED = (
    "<html><body>"
    + ('<button aria-label="' + dom.REACTION_OFF_LABEL + '"></button>') * 3
    + "</body></html>"
)

#: EVERY FIXTURE DRAWS WHAT ITS NAME SAYS, checked at import. Cheap, and it is
#: the guard the ``_FEED`` slip walked straight past: the reader counts
#: ``button[aria-label^="Reaction button state:"]``, so counting that prefix in
#: the string is the same question one layer earlier. Without this the counts
#: asserted below would be counts over whatever the concatenation happened to
#: build.
for _name, _page, _want in (
    ("_ONE_OFF", _ONE_OFF, 1),
    ("_ONE_ON", _ONE_ON, 1),
    ("_MIXED", _MIXED, 2),
    ("_FEED", _FEED, 3),
):
    _drawn = _page.count('aria-label="' + dom.REACTION_STATE_PREFIX)
    assert _drawn == _want, (
        "%s draws %d reaction control(s) and this file calls it %d. A fixture "
        "that does not draw what its name says makes every count asserted "
        "over it a fiction." % (_name, _drawn, _want)
    )


def _item_url() -> str:
    spec = spec_for_action("react_to_item")
    return spec.url_template.format(target=REACTED_ITEM)


async def _preview_over(page, pages: dict):
    """Drive the REAL gate. No argument chooses the surface -- ``observe``
    picks it from the spec's own ``state_from``, and the navigator records
    what was actually asked for, so the choice is asserted rather than
    assumed."""
    nav = FixtureNavigator(pages)
    block = await preview(
        spec_for_action("react_to_item"),
        target=REACTED_ITEM,
        navigator=nav,
        page=page,
    )
    return block, nav


async def test_an_already_reacted_target_is_never_offered_as_no_reaction(
    writes_on, browser_page
):
    """CASE 1 -- the live defect, reproduced.

    BOTH surfaces are frozen, and that is what makes this the strongest of the
    four: nothing here fails for want of a fixture. The feed is served exactly
    as the live run found it -- three controls, all OFF -- and the permalink
    wears the ON label. A gate reading the feed renders and offers to react; a
    gate reading the permalink refuses, because ``react_to_item`` is valid only
    from ``no_reaction``.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _preview_over(
            browser_page, {writes.FEED_URL: _FEED, _item_url(): _ONE_ON}
        )
    message = str(caught.value)
    assert "'reacted'" in message, message
    assert "no_reaction" in message, message
    # The refusal has to say WHAT IT SAW, not only what it declined. A message
    # that names neither the state nor the surface is half a measurement.
    assert "ALREADY CARRIES A REACTION" in message, message
    assert _REACTION_ON_LABEL in message, message
    # AND IT MUST EXPLAIN ITSELF IN TERMS OF THIS ACTION. Until the direction
    # was read here this arm was effectively dead, and it was inheriting the
    # default wrong-state sentence -- a correct toggle warning illustrated
    # entirely with SAVING A JOB. A refusal about a reaction that talks about
    # unsaving a posting is the misdescription ``wrong_state_note`` exists for.
    assert "TAKE IT BACK" in message, message
    assert "UNSAVE it" not in message, message


async def test_an_unreacted_target_is_still_offered_as_no_reaction(
    writes_on, browser_page
):
    """CASE 2 -- the direction that must survive the fix.

    ONLY the permalink is frozen. A gate that reaches for ``/feed/`` fails
    here on the navigator rather than on an assertion, which is the point: the
    surface is pinned by what the gate ASKS FOR, not by what it concludes.
    """
    block, nav = await _preview_over(browser_page, {_item_url(): _ONE_OFF})
    assert block["direction"]["currently"] == "no_reaction"
    assert block["direction"]["after"] == "reacted"
    assert nav.gotos == [_item_url()], nav.gotos
    # A token exists: this is the state the action is FOR.
    assert block["to_confirm"] is not None


async def test_a_mixed_page_still_refuses(writes_on, browser_page):
    """CASE 3 -- two controls disagreeing, and the gate declines to pick.

    On the feed this was refused because a mixed page cannot say which item a
    direction belongs to. On the permalink the reason is narrower and stronger:
    more than one control means this is not the single-item render the action
    was measured against, so pressing either would be picking by position.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _preview_over(browser_page, {_item_url(): _MIXED})
    message = str(caught.value)
    assert "unknown" in message, message
    assert "2 reaction control(s)" in message, message


async def test_a_page_that_drew_nothing_is_unknown_and_never_no_reaction(
    writes_on, browser_page
):
    """CASE 3b -- ABSENT IS NOT OFF, on the surface that now decides.

    Not in the four the wave was asked for, and added because the count this
    reader keys on is the one that can be zero for a reason that has nothing
    to do with reactions. A permalink that had not drawn the item renders no
    reaction control at all, and "no control is wearing the ON label" is
    satisfied by a page with no controls on it -- which is how an unrendered
    page becomes a confident ``no_reaction`` and a click on nothing.

    This repo has ten catalogued instances of that shape, four of them in
    instruments written to catch it. ``_live_control`` already refuses zero;
    this pins the preview refusing it too, so the two ends cannot disagree
    about an empty page either.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _preview_over(browser_page, {_item_url(): "<html><body></body></html>"})
    message = str(caught.value)
    assert "unknown" in message, message
    assert "0 reaction control(s)" in message, message
    assert "never 'no reaction'" in message, message


async def test_the_direction_is_read_on_the_page_the_click_lands_on(
    writes_on, browser_page
):
    """CASE 4 -- the block must SAY where it read, and it must be one page.

    Both surfaces are frozen and both would be served, so the feed is not
    opened because the gate does not ask for it. ``same_page_as_the_action``
    is the field the operator reads to know whether the direction and the act
    can drift apart, and for this action they now cannot.
    """
    block, nav = await _preview_over(
        browser_page, {writes.FEED_URL: _FEED, _item_url(): _ONE_OFF}
    )
    where = block["direction"]
    assert where["same_page_as_the_action"] is True, where
    assert where["read_from_url"] == _item_url(), where
    assert nav.gotos == [_item_url()], nav.gotos
    assert "at no extra page load" in where["what_that_means"], where
    # And the facts printed beside it came off the same page, so the counts he
    # reads and the control that would move are the same objects.
    assert block["where"]["url"] == _item_url(), block["where"]
    assert block["where"]["what_the_page_showed"]["controls"] == 1, block["where"]
    # ``page_loads`` IS NOT THE DISCRIMINATOR AND IS NOT ASSERTED HERE. It is
    # derived from ``facts_url == state_url``, and pre-fix BOTH were the feed
    # -- so it read 1, honestly, for a gate whose two ends were the same wrong
    # page. MEASURED against HEAD before the fix. What moved is WHICH page,
    # which is why the urls are asserted and the count is not.
    assert block["read"]["facts_url"] == block["read"]["state_url"] == _item_url()
    assert block["read"]["same_page_as_the_action"] is True, block["read"]


@pytest.mark.parametrize(
    "html,expected",
    [(_ONE_OFF, "no_reaction"), (_ONE_ON, "reacted"), (_MIXED, "unknown")],
)
async def test_the_preview_reading_and_the_click_reading_agree(
    writes_on, browser_page, html, expected
):
    """THE PARITY THIS FIX IS FOR, asserted rather than assumed.

    ``from_state`` is compared against a live reading TWICE -- once by
    ``_direction`` on the preview's observation, once by ``valid_from`` on what
    ``_live_control`` read off the control about to be pressed. Before the fix
    those two readings came off DIFFERENT PAGES, so agreement between them was
    not a property of anything. They now read one page, and this pins that:
    over the same frozen world, the preview's state and the click's state are
    the same string.

    ``tests/test_preview_state_and_click_state.py`` asks whether the two ends
    compare the same FIELD. This asks whether they read the same PAGE, which is
    the half that was false.
    """
    spec = spec_for_action("react_to_item")

    block_state = None
    try:
        block, _nav = await _preview_over(browser_page, {_item_url(): html})
        block_state = block["direction"]["currently"]
    except WriteAttemptError as exc:
        # A refusal IS a reading -- ``_direction`` raises on ``unknown`` and on
        # the wrong state, and the state it saw is in the sentence.
        block_state = "reacted" if "'reacted'" in str(exc) else "unknown"
    assert block_state == expected, block_state

    await browser_page.set_content(html, wait_until="domcontentloaded")
    grant = writes.WriteGrant(
        action="react_to_item",
        target=REACTED_ITEM,
        token="not-a-minted-token",
        minted_at=0.0,
    )
    live_state, why, _selector = await writes._live_control(
        browser_page, spec, grant, dom.REACTION_OFF_LABEL
    )
    assert live_state == expected, (live_state, why)
