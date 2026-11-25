"""``endorse_skill`` and its inverse ``withdraw_endorsement`` -- built to REFUSE.

Census rows ``P E4`` / ``N 111`` (endorse one skill of a member he names) and
``P E5`` / ``N 113`` (withdraw an endorsement he gave). Lane builds-26,
2026-11-24: both SANCTIONED AND NOT PERFORMABLE, built in one change so the
inverse exists before any forward press could. The per-skill control has
never been captured (zero endorse controls in the tracked corpus), so neither
can hold a grant; each preview loads the profile HE NAMES through the
named-profile door, prints whom it resolved to, COUNTS the endorse-shaped
buttons in the page, and mints nothing.

WHAT IS MEASURED HERE AND WHAT IS DERIVED. The profile is the synthetic
named-person fixture the named-person acts are tested on
(``tests/fixtures/synthetic/named_profile.html``); it draws no endorse
control, so its counts are zero. The one world that draws an endorse-shaped
button is DERIVED from it by an asserted insertion, and its label is
invented: it shows the control is COUNTED and never PRESSED, which holds for
any label.

NOTHING HERE REACHES LINKEDIN.
"""
from __future__ import annotations

import asyncio

import pytest

from linkedin_server import endorse_skill, server, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import mint, preview, spec_for_action
from tests.test_named_profile_route import LINK, PROFILE, SEGMENT, _Navigator
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

ACTIONS = (endorse_skill.ENDORSE, endorse_skill.WITHDRAW)
SKILL = "Node.js"
TARGET = {"profile": LINK, "skill": SKILL}

#: DERIVED: the fixture with one endorse-shaped button added to its main
#: column. The label is invented; the press handler marks the body if anything
#: ever presses it.
_INSERT = (
    '<button type="button" aria-label="Endorse ' + SKILL + '" '
    "onclick=\"document.body.setAttribute('data-pressed','endorse')\">Endorse</button>"
)
assert PROFILE.count("<main") == 1
WITH_A_CONTROL = PROFILE.replace("</main>", _INSERT + "</main>", 1)
assert WITH_A_CONTROL != PROFILE


@pytest.mark.parametrize("action", ACTIONS)
def test_both_are_sanctioned_and_cannot_hold_a_grant(writes_on, action):
    spec = spec_for_action(action)
    assert spec.tool_name == "linkedin_" + action
    assert action not in writes.PERFORMABLE
    assert spec.url_template is None and spec.url_pattern is None
    assert writes.grant_is_possible(spec) is False
    with pytest.raises(WriteAttemptError, match="no grant is minted for"):
        mint(action, TARGET, receipt="anything")


@pytest.mark.parametrize("action", ACTIONS)
def test_each_refusal_is_its_own_and_names_the_capture(action):
    with pytest.raises(WriteAttemptError) as caught:
        writes._refuse_unperformable(spec_for_action(action))
    reason = str(caught.value)
    assert reason.startswith(action + " is sanctioned and cannot be performed")
    assert "WHAT WOULD LIFT IT" in reason and "Skills section" in reason
    assert "/in/<segment>/" in reason


def test_each_direction_names_the_other_as_its_undo():
    assert "linkedin_withdraw_endorsement" in spec_for_action("endorse_skill").reversible_by
    assert "linkedin_endorse_skill" in spec_for_action("withdraw_endorsement").reversible_by
    assert "ROUND-TRIP RULE" in spec_for_action("endorse_skill").reversible_by


@pytest.mark.parametrize("action", ACTIONS)
def test_the_target_is_a_link_and_a_skill_never_a_name(action):
    spec = spec_for_action(action)
    canonical = writes._target_for(spec, TARGET)
    assert canonical == LINK + writes.TARGET_JOIN + SKILL
    assert writes._target_for(spec, canonical) == canonical, "not idempotent"
    assert writes.url_target_of(spec, canonical) == SEGMENT
    with pytest.raises(WriteAttemptError):
        writes._target_for(spec, {"profile": "Casey", "skill": SKILL})
    with pytest.raises(WriteAttemptError):
        writes._target_for(spec, {"profile": LINK, "skill": ""})


@pytest.mark.parametrize("value", ["", " ", "x" * 101, "https://example.com/skill", "a/b"])
def test_a_skill_that_is_not_a_skill_name_is_refused_unrepeated(value):
    skill, why = endorse_skill.checked_skill(value)
    assert skill == "" and why
    if value.strip():
        assert value not in why


@pytest.mark.parametrize("action", ACTIONS)
async def test_the_preview_loads_the_named_profile_and_issues_no_token(writes_on, browser_page, action):
    nav = _Navigator(PROFILE)
    block = await preview(spec_for_action(action), target=TARGET, navigator=nav, page=browser_page)
    assert nav.gotos == [LINK] and nav.named == [True]
    assert block["to_confirm"] is None and block["performed"] is False
    assert "NO CONFIRM TOKEN IS ISSUED" in block["what_happens_next"]
    assert block["direction"]["currently"] == endorse_skill.PROFILE_IDENTIFIED
    assert block["where"]["profile"] == LINK and block["where"]["skill"] == SKILL
    shown = block["where"]["what_the_page_showed"]
    assert shown["endorse_controls"] == 0 and shown["endorse_controls_for_skill"] == 0
    assert shown["control_label_measured"] is False
    assert block["whom_this_resolves_to"] is not None
    assert writes._GRANTS == {}


async def test_an_endorse_shaped_button_is_counted_and_never_pressed(writes_on, browser_page):
    nav = _Navigator(WITH_A_CONTROL)
    block = await preview(spec_for_action("endorse_skill"), target=TARGET, navigator=nav, page=browser_page)
    shown = block["where"]["what_the_page_showed"]
    assert shown["endorse_controls"] == 1 and shown["endorse_controls_for_skill"] == 1
    assert block["to_confirm"] is None
    pressed = await browser_page.evaluate(
        "() => document.body.getAttribute('data-pressed') || ''"
    )
    assert pressed == ""


async def test_a_landing_on_another_profile_is_refused(writes_on, browser_page):
    nav = _Navigator(PROFILE, landed="https://www.linkedin.com/in/someone-else-9z9z/")
    with pytest.raises(WriteAttemptError, match="came back 'unknown'"):
        await preview(spec_for_action("withdraw_endorsement"), target=TARGET, navigator=nav, page=browser_page)


@pytest.mark.parametrize("tool", ["linkedin_endorse_skill", "linkedin_withdraw_endorsement"])
def test_the_tool_refuses_a_bad_skill_before_any_page_loads(monkeypatch, tool):
    def _never(*_args, **_kwargs):
        raise AssertionError("the write path was reached for a refused skill")

    monkeypatch.setattr(server, "_write_tool", _never)
    out = asyncio.run(getattr(server, tool)(profile=LINK, skill="https://example.com/x"))
    assert out["error"] == "bad_skill"
    assert out["pages_loaded"] == 0 and out["performed"] is False
    assert "example.com" not in out["message"]


@pytest.mark.parametrize("tool,action", [
    ("linkedin_endorse_skill", "endorse_skill"),
    ("linkedin_withdraw_endorsement", "withdraw_endorsement"),
])
def test_the_tool_hands_the_link_and_the_skill_to_the_gate(monkeypatch, tool, action):
    seen = {}

    async def _fake(act, target, confirm_token):
        seen.update(action=act, target=target)
        return {"action": act, "to_confirm": None}

    monkeypatch.setattr(server, "_write_tool", _fake)
    asyncio.run(getattr(server, tool)(profile=LINK, skill="  Node.js "))
    assert seen == {"action": action, "target": {"profile": LINK, "skill": SKILL}}
