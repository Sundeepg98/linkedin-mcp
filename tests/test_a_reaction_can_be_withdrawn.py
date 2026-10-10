"""A reaction can be withdrawn -- lane NP, 2026-10-10.

THE ORCHESTRATOR'S RULING OF 14:14: "name it on the verb the law ALREADY
admits. Withdrawing his OWN reaction is 'delete or withdraw one of his own
items' (OUTWARD-CLASSES-BUILT-BEHIND-GRANTS). Do NOT widen
_VERBS_ADMITTED_BY_RULING. BUILD IT NOW, red first ... linkedin_withdraw_reaction(item),
the inverse of the react, with its preview naming the item and its author kind."

WHAT IS PINNED:

1. The name: a verb the conservation law already admits, and the law unwidened.
2. The preview: the item's own permalink, its ONE toggle ON in a MEASURED family,
   the author named as a people record, ``author_kind`` ``unknown`` (the same
   ruling's item 4), a token; an OFF toggle is the wrong state, and an ON name
   nobody measured is refused before a token exists.
3. The press: ONLY a measured ON label is aimed at, by its exact name; the
   verification is a fresh render reading the MEASURED OFF label; a toggle still
   ON after the press is not verified.
4. The reaction's own spec names its inverse.

Every page is SYNTHETIC, built with the reaction tests' own builder over the
structure measured on his own post's permalink capture, peopled with invented
values and the suite's declared item urn. NOTHING HERE REACHES LINKEDIN.
"""

from __future__ import annotations

from typing import Any

import pytest

from linkedin_server import dom, people_data, readonly, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_a_reaction_takes_any_item_and_names_its_author import (
    _AUTHOR_NAME,
    _permalink,
    _tool,
)
from tests.test_writes import (  # noqa: F401 -- two of these are fixtures
    REACTED_ITEM,
    FixtureNavigator,
    _VERBS_ADMITTED_BY_RULING,
    browser_page,
    writes_on,
)

ACTION = "withdraw_reaction"
TOOL = "linkedin_withdraw_reaction"
UNREACT_LIKE = "Unreact Like"
STATE_LIKE = "Reaction button state: Like"
#: An ON name in a measured FAMILY whose KIND nobody has measured.
UNMEASURED_ON = "Unreact Celebrate"
#: The permalink a withdrawal is valid on: its one toggle wearing the ON name
#: measured on an item's own permalink. Imported by
#: tests/test_preview_state_and_click_state.py, never rebuilt there.
WITHDRAW_MARKUP = _permalink(toggle=UNREACT_LIKE)


def _url() -> str:
    return spec_for_action(ACTION).url_template.format(target=REACTED_ITEM)


async def _preview(page, html: str) -> dict[str, Any]:
    return await preview(
        spec_for_action(ACTION),
        target=REACTED_ITEM,
        navigator=FixtureNavigator({_url(): html}),
        page=page,
    )


# ---------------------------------------------------------------------------
# 1. The name
# ---------------------------------------------------------------------------


async def test_the_tool_is_registered_on_a_verb_the_law_already_admits():
    tool = await _tool(TOOL)
    assert tool is not None
    assert set(readonly.iter_write_verbs_in(TOOL)) == {"withdraw"}
    assert _VERBS_ADMITTED_BY_RULING == {"comment", "react"}, "the law was widened"
    assert spec_for_action(ACTION).tool_name == TOOL
    assert ACTION in writes.PERFORMABLE


# ---------------------------------------------------------------------------
# 2. The preview
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("label", [UNREACT_LIKE, STATE_LIKE])
async def test_the_preview_reads_a_measured_on_toggle_and_names_the_author(
    writes_on, browser_page, label
):
    block = await _preview(browser_page, _permalink(toggle=label))
    assert block["direction"]["currently"] == "reacted"
    assert block["to_confirm"] is not None
    record = people_data.as_record(block.get("who_this_would_reach"))
    assert isinstance(record, people_data.Person) and record.name == _AUTHOR_NAME
    assert block["author_kind"] == "unknown"


async def test_an_item_that_carries_no_reaction_is_the_wrong_state(writes_on, browser_page):
    """The preview REFUSES -- no token -- and says the wrong state would react."""
    with pytest.raises(WriteAttemptError) as caught:
        await _preview(browser_page, _permalink(toggle=dom.REACTION_OFF_LABEL))
    message = str(caught.value)
    assert "'no_reaction'" in message and "would REACT" in message, message


async def test_an_on_name_nobody_measured_is_refused_before_a_token(writes_on, browser_page):
    """An ON toggle in a measured FAMILY wearing a KIND nobody measured: the
    preview reads it as unknown and mints nothing."""
    with pytest.raises(WriteAttemptError) as caught:
        await _preview(browser_page, _permalink(toggle=UNMEASURED_ON))
    assert "unknown" in str(caught.value), str(caught.value)


# ---------------------------------------------------------------------------
# 3. The press and the verification
# ---------------------------------------------------------------------------


async def _perform(page, before: str, after: str) -> dict[str, Any]:
    block = await _preview(page, before)
    grant = consume(block["to_confirm"], action=ACTION, target=REACTED_ITEM)
    nav = FixtureNavigator({_url(): [before, after]})
    out = await writes.perform(nav, page, grant)
    out["_gotos"] = list(nav.gotos)
    return out


@pytest.mark.parametrize("label", [UNREACT_LIKE, STATE_LIKE])
async def test_the_press_aims_at_the_measured_label_and_verifies_off(
    writes_on, browser_page, label
):
    block = await _perform(
        browser_page, _permalink(toggle=label), _permalink(toggle=dom.REACTION_OFF_LABEL)
    )
    assert block["clicked"]["selector"] == 'button[aria-label="' + label + '"]'
    assert block["clicked"]["error"] is None
    assert block["performed"] is True and block["verified"] is True
    assert block["verification"]["observed_state"] == "no_reaction"
    assert block["_gotos"] == [_url(), _url()]


async def test_a_toggle_still_on_after_the_press_is_not_verified(writes_on, browser_page):
    block = await _perform(
        browser_page, _permalink(toggle=UNREACT_LIKE), _permalink(toggle=UNREACT_LIKE)
    )
    assert block["performed"] is False
    assert block["verification"]["observed_state"] == "reacted"


async def test_an_unmeasured_off_name_after_the_press_is_not_a_success(writes_on, browser_page):
    """Only the MEASURED OFF label verifies a withdrawal: an OFF name in the
    unmeasured 'React' family is a toggle nobody has read, so it is UNKNOWN."""
    block = await _perform(
        browser_page, _permalink(toggle=UNREACT_LIKE), _permalink(toggle="React Like")
    )
    assert block["verified"] is not True
    assert block["performed"] is not True


# ---------------------------------------------------------------------------
# 4. The reaction names its inverse
# ---------------------------------------------------------------------------


def test_the_reaction_spec_names_its_inverse():
    react = spec_for_action("react_to_item")
    assert TOOL in react.reversible_by
    assert TOOL in react.wrong_state_note
    assert "linkedin_react_to_item" in spec_for_action(ACTION).reversible_by
