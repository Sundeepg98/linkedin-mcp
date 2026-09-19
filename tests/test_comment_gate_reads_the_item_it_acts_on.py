"""``comment_on_item``'s gate must read, and name, the item it acts on.

THE SIBLING OF ``tests/test_react_direction_is_read_where_it_acts.py``, which
fixed the same surface mismatch on ``react_to_item`` on 2026-09-05. Read that
file first: it carries the origin, the history, and the pre-fix block. This one
is the second instance, found from the first, and it turned out to carry two
more defects that the reaction did not.

THE TEST SHAPE, and it is the finding the reaction wave ended on rather than a
convention. The live report that started all this was "the gate said
no_reaction about an item that carried a reaction" -- true, and weaker than
what the frozen worlds showed: **the confirm block was byte-identical across a
reacted and an unreacted world, with a token issued in both.** A gate whose
output does not change when the target changes is not misreading the target,
it is not reading it. So the question asked here is not "does it report
correctly" but **"do two frozen worlds produce different output"** -- and a
check that cannot answer yes is decorative regardless of what it prints.

THREE DEFECTS, ALL MEASURED 2026-09-05 by driving the real gate over frozen
worlds (``<scratchpad>/_probe_comment_gate.py``), not read off source.

**A -- THE SURFACE MISMATCH.** ``state_from`` is ``feed_item``, which
``_SURFACE_READS`` points at ``/feed/``, while the action acts on
``/feed/update/<urn>/``. Same origin as the reaction's, established from
history: the spec was authored 2026-08-30 in ``050349f`` while the action
REFUSED and had no ``url_template`` to aim at, and ``1fb3c15`` made it
performable on 2026-09-01, added the template and the pattern, and did not
touch ``state_from`` -- that diff contains no such line. MEASURED: an item
permalink drawing a comment box and one drawing NOTHING produced the same
``state``, the same ``why``, the same ``what_the_page_showed``, and a confirm
token in both.

**B -- THE TWO ENDS MEASURE DIFFERENT PROPERTIES.** Even on the right page
they would not agree. The preview asks how many controls are NAMED
``Comment``; ``_live_control``'s comment arm asks how many EDITORS named
``Text editor for creating comment`` rendered, and requires exactly one. Two
different measurements, compared against one ``from_state`` string. That is
the invariant ``tests/test_preview_state_and_click_state.py`` exists for, one
level down: that file asks whether the two ends compare the same FIELD, and
this asks whether they measure the same THING.

**C -- THE URL IS BUILT FROM THE WHOLE COMPOSITE TARGET, AND THE ACTION
CANNOT ACT.** ``comment_on_item``'s target is ``item :: text``, and all the
``url_template.format(target=...)`` sites were handed the canonical string
whole. MEASURED::

    url it will build:
      'https://www.linkedin.com/feed/update/urn:li:activity:<id> ::
       Congratulations on the launch./'
    pattern matches  : False
    PERFORM RAISED   : WriteAttemptError
      write blocked: '...' fails its own pattern
    gotos before raising: []

So: the confirm block named THE PAGE THIS ACTION WOULD ACT ON as a malformed
address with the operator's own comment text spliced into it, and
``assert_write_url`` then rebuilt the same string and refused it. Zero
navigations. **This action is in ``PERFORMABLE``, mints real confirm tokens,
and cannot act** -- the shape ``update_profile_field`` shipped in on
2026-09-02 and was repaired the same day. Its own spec asserted the opposite:
"only the ITEM half reaches this url, because assert_write_url formats the
SUBJECT."

**AND C IS A CLASS OF ONE ONLY BY COINCIDENCE.** Counted off the live specs:
five actions carry a composite target, and ``comment_on_item`` is the ONLY one
whose ``url_template`` also carries a ``{target}`` placeholder -- the other
four address constants, so ``format`` has nothing to substitute and the bug
cannot show. Nothing ever required a composite target's url to receive the
subject half. It is the same unruled coincidence that cost nine sites when
url-presence and performability turned out not to coincide, and like those it
is exposed by the first action to violate it.

RED, at commit ``5046a3b``, all seven cases below, in an isolated copy of the
tree built with ``git archive HEAD`` -- never by stashing under a concurrent
writer.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import assert_write_url, preview, spec_for_action
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    REACTED_ITEM,
    FixtureNavigator,
    _bare_grant,
    browser_page,
    writes_on,
)

#: The item. Reuses the declared synthetic urn from tests/test_writes.py rather
#: than minting a second one -- a synthetic value that has to be argued for
#: costs more than one that argues for itself, and that one is already declared
#: in tests/test_no_committed_identity.py's SYNTHETIC_IDS.
ITEM = REACTED_ITEM

#: HIS WORDS. Load-bearing in two of the cases below: it is the half of the
#: target that was ending up inside a url, so a case that asserts it is absent
#: needs it to be a string that could not arrive there by chance.
TEXT = "Congratulations on the launch."

TARGET = {"item": ITEM, "text": TEXT}

#: THE PERMALINK AS MEASURED 2026-08-31: exactly one contenteditable named
#: ``Text editor for creating comment``, which every previous census of every
#: readable surface reported as zero, beside the ``Comment`` affordance.
_EDITOR = (
    '<div role="textbox" contenteditable="true" aria-label="'
    + dom.COMMENT_EDITOR_LABEL
    + '"></div>'
)
_COMMENT_BUTTON = "<button>" + dom.COMMENT_CONTROL_NAME + "</button>"

ITEM_WITH_BOX = "<html><body>" + _EDITOR + _COMMENT_BUTTON + "</body></html>"

#: A PAGE THAT HAD NOT ARRIVED. Not a page with no comment box -- there is no
#: such thing on this surface that this server can tell apart from one that did
#: not render, which is why the reader must say UNKNOWN rather than zero.
ITEM_BARE = "<html><body></body></html>"

#: THE SHAPE THAT SEPARATES DEFECT B FROM DEFECT A. Three ``Comment``
#: affordances and NO editor: everything the preview used to count, and nothing
#: the click requires. A gate reading the right page and the wrong property
#: passes every other case in this file and fails this one.
ITEM_AFFORDANCES_ONLY = "<html><body>" + _COMMENT_BUTTON * 3 + "</body></html>"

#: THE FEED, as measured 2026-08-30: three text-named ``Comment`` buttons, each
#: belonging to somebody else's post.
FEED = "<html><body>" + _COMMENT_BUTTON * 3 + "</body></html>"

for _name, _page, _editors, _buttons in (
    ("ITEM_WITH_BOX", ITEM_WITH_BOX, 1, 1),
    ("ITEM_BARE", ITEM_BARE, 0, 0),
    ("ITEM_AFFORDANCES_ONLY", ITEM_AFFORDANCES_ONLY, 0, 3),
    ("FEED", FEED, 0, 3),
):
    assert _page.count(dom.COMMENT_EDITOR_LABEL) == _editors, _name
    assert _page.count(">" + dom.COMMENT_CONTROL_NAME + "<") == _buttons, _name


def _permalink() -> str:
    return "https://www.linkedin.com/feed/update/%s/" % ITEM


async def _preview_over(page, pages: dict):
    """Drive the REAL gate. Nothing here chooses a surface -- ``observe`` picks
    it from the spec's own ``state_from`` and the navigator records the ask."""
    nav = FixtureNavigator(pages)
    block = await preview(
        spec_for_action("comment_on_item"),
        target=TARGET,
        navigator=nav,
        page=page,
    )
    return block, nav


def _fingerprint(block: dict) -> dict:
    """Everything in the block that is SUPPOSED to describe the target.

    The confirm token is excluded because it is random per call, which is the
    one field guaranteed to differ between two runs and says nothing about
    what was read. Whether a token exists AT ALL is kept, because that is an
    outcome rather than a nonce.
    """
    where = dict(block.get("where") or {})
    direction = dict(block.get("direction") or {})
    return {
        "state": direction.get("currently"),
        "why": direction.get("why"),
        "read_from_url": direction.get("read_from_url"),
        "same_page": direction.get("same_page_as_the_action"),
        "what_the_page_showed": where.get("what_the_page_showed"),
        "url": where.get("url"),
        "token_issued": block.get("to_confirm") is not None,
    }


async def _outcome(page, item_world: str):
    """What the gate does about one frozen world for the TARGET, as a value
    that can be compared against another world's."""
    try:
        block, nav = await _preview_over(
            page, {writes.FEED_URL: FEED, _permalink(): item_world}
        )
        return ("minted", _fingerprint(block), tuple(nav.gotos))
    except WriteAttemptError as exc:
        return ("refused", str(exc), None)
    finally:
        writes.discard_all()


async def test_two_frozen_worlds_for_the_target_produce_different_output(
    writes_on, browser_page
):
    """CASE 1, AND THE ONE THE OTHERS ARE COMMENTARY ON.

    BOTH surfaces are frozen in both runs, so neither fails for want of a
    fixture and the only thing that moves is the TARGET's own page. An item
    that drew a comment box and an item that drew nothing at all must not
    produce the same confirm block.

    MEASURED BEFORE THE FIX: they did. Same ``state``, same ``why``, same
    ``what_the_page_showed``, same ``url``, token issued in both -- because
    every one of those was read off ``/feed/``, which did not change between
    the runs and does not belong to this item either way.
    """
    with_box = await _outcome(browser_page, ITEM_WITH_BOX)
    bare = await _outcome(browser_page, ITEM_BARE)
    assert with_box != bare, (
        "the gate produced identical output for an item that drew a comment "
        "box and one that drew nothing. It is not reading the target."
    )
    # AND THE DIRECTION EACH WENT, so this cannot pass on any two differences.
    assert with_box[0] == "minted", with_box
    assert bare[0] == "refused", bare


async def test_an_item_that_drew_nothing_is_unknown_and_refuses(
    writes_on, browser_page
):
    """CASE 2 -- ABSENT IS NOT ZERO, on the surface that decides.

    A permalink that had not rendered draws no editor, and "no editor" must
    not be reported as a state. ``_live_control`` already refuses this at
    click time with those words; this pins the preview refusing it too, so the
    two ends cannot disagree about an empty page.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _preview_over(browser_page, {_permalink(): ITEM_BARE})
    message = str(caught.value)
    assert "unknown" in message, message
    assert "0 comment editor(s)" in message, message
    assert "never an empty comment box" in message, message


async def test_a_page_of_affordances_with_no_editor_still_refuses(
    writes_on, browser_page
):
    """CASE 3 -- THE TWO ENDS MUST MEASURE THE SAME THING, not just read the
    same page.

    This world draws THREE controls named ``Comment`` and NO editor. The old
    preview counted exactly those controls and would have called it
    ``comment_control_present``; ``_live_control`` counts editors and refuses.
    Reading the right page is not enough if the property read is not the
    property the click requires -- a gate can be pointed at the target and
    still be answering a different question about it.
    """
    with pytest.raises(WriteAttemptError) as caught:
        await _preview_over(browser_page, {_permalink(): ITEM_AFFORDANCES_ONLY})
    message = str(caught.value)
    assert "unknown" in message, message
    assert "0 comment editor(s)" in message, message


async def test_the_gate_reads_the_permalink_and_says_where(
    writes_on, browser_page
):
    """CASE 4 -- one load, of the page the fill lands on, and the block says so."""
    block, nav = await _preview_over(
        browser_page, {writes.FEED_URL: FEED, _permalink(): ITEM_WITH_BOX}
    )
    direction = block["direction"]
    assert direction["currently"] == "comment_control_present"
    assert direction["same_page_as_the_action"] is True, direction
    assert direction["read_from_url"] == _permalink(), direction
    assert nav.gotos == [_permalink()], nav.gotos
    assert block["read"]["facts_url"] == block["read"]["state_url"] == _permalink()
    assert block["what_happens_next"], block


async def test_the_url_the_block_names_is_the_item_and_not_his_words(
    writes_on, browser_page
):
    """CASE 5 -- HIS COMMENT TEXT MUST NOT BE INSIDE A URL.

    ``where.url`` is the field that tells him WHICH PAGE this acts on, and it
    was built by formatting the whole canonical target into the template --
    so it read ``.../feed/update/<urn> :: Congratulations on the launch./``.
    That is not a page, it is a sentence wearing an address's shape, printed
    where the one thing he is meant to check the target against goes.
    """
    block, _nav = await _preview_over(
        browser_page, {writes.FEED_URL: FEED, _permalink(): ITEM_WITH_BOX}
    )
    url = block["where"]["url"]
    assert url == _permalink(), url
    assert TEXT not in url, url
    assert writes.TARGET_JOIN not in url, url
    # The two halves are still both printed -- beside the url, as themselves.
    assert block["where"]["item"] == ITEM, block["where"]
    assert block["where"]["text"] == TEXT, block["where"]


def test_the_action_can_reach_its_own_write_door(writes_on):
    """CASE 6 -- THE ONE THAT SAYS WHETHER IT CAN ACT AT ALL.

    ``assert_write_url`` REBUILDS the url from the grant and compares; a
    caller cannot hand one in. So if the rebuild produces a string the
    action's own ``url_pattern`` refuses, the action is unreachable behind its
    own door however good everything upstream is -- and it was: MEASURED,
    ``perform`` raised ``fails its own pattern`` with ZERO navigations, on an
    action sitting in ``PERFORMABLE`` and minting real confirm tokens.

    No browser and no fixture: this is a claim about a string, settled as one.
    """
    spec = spec_for_action("comment_on_item")
    canonical = str(writes._target_for(spec, TARGET))
    assert writes.TARGET_JOIN in canonical, canonical
    grant = _bare_grant("comment_on_item", canonical)
    assert assert_write_url(_permalink(), grant) == _permalink()


async def test_perform_reaches_the_editor_instead_of_its_own_door(
    writes_on, browser_page
):
    """CASE 6b -- THE END-TO-END CLAIM, because case 6 is about a string.

    ``assert_write_url`` accepting the url proves the DOOR is right; it does
    not prove the action can reach it, and this wave measured why that
    distinction is not pedantry. FOUR SITES built this url from the canonical
    target, and fixing them one at a time produced three different refusals in
    a row, each locally accurate and each about the same defect:

        fails its own pattern                    (door rebuilt it wrongly)
        is not this grant's target               (caller built it wrongly)
        landed on ... and that is not it         (landing check, same)

    Only the fourth run navigated. So this drives the real ``perform`` and
    asserts it got as far as the CONTROL: the editor selector, on the
    permalink, no error.

    IT DOES NOT ASSERT A COMMENT WAS PUBLISHED, and must not. This fixture
    grows no submit control after the fill, so the delta gate refuses and
    ``performed`` is ``unknown`` -- which is the action's own designed
    first-use refusal and is covered by tests/test_comment_delta_gate.py. What
    is asserted here is the thing that was false: that it can get there at all.
    """
    block, _nav = await _preview_over(
        browser_page, {writes.FEED_URL: FEED, _permalink(): ITEM_WITH_BOX}
    )
    grant = writes.consume(
        block["to_confirm"], action="comment_on_item", target=TARGET
    )
    perform_nav = FixtureNavigator({_permalink(): ITEM_WITH_BOX})
    result = await writes.perform(perform_nav, browser_page, grant)

    assert perform_nav.gotos == [_permalink()], perform_nav.gotos
    clicked = result["clicked"]
    assert clicked["selector"] == dom.comment_editor_selector(), clicked
    assert clicked["on"] == _permalink(), clicked
    assert clicked["error"] is None, clicked
    assert clicked["state_before"] == "comment_control_present", clicked


@pytest.mark.parametrize(
    "html,expected",
    [
        (ITEM_WITH_BOX, "comment_control_present"),
        (ITEM_BARE, "unknown"),
        (ITEM_AFFORDANCES_ONLY, "unknown"),
    ],
)
async def test_the_preview_reading_and_the_click_reading_agree(
    writes_on, browser_page, html, expected
):
    """CASE 7 -- the two ends, over one frozen world, must return one string.

    ``from_state`` is compared against a live reading TWICE, and until this
    fix the two readings came off different pages AND measured different
    properties, so their agreement was a property of nothing at all.
    """
    spec = spec_for_action("comment_on_item")

    try:
        block, _nav = await _preview_over(browser_page, {_permalink(): html})
        preview_state = block["direction"]["currently"]
    except WriteAttemptError:
        preview_state = "unknown"
    finally:
        writes.discard_all()
    assert preview_state == expected, preview_state

    await browser_page.set_content(html, wait_until="domcontentloaded")
    grant = _bare_grant("comment_on_item", str(writes._target_for(spec, TARGET)))
    live_state, why, _selector = await writes._live_control(
        browser_page, spec, grant, dom.COMMENT_EDITOR_LABEL
    )
    assert live_state == expected, (live_state, why)
