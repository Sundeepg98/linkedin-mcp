"""``set_admitted_setting`` end to end: preview, token, press, verification.

Lane S, 2026-10-10, under ``HIS-OWN-SETTINGS-NOT-OUTWARD``. The generic
settings writer behind the single-use grant: ONE admitted settings page, ONE
control on it, named by the label LinkedIn draws. Its verdicts and readers are
held by ``tests/test_settings_writer.py``; this file drives the REAL preview,
the REAL token door and the REAL ``writes.perform`` over frozen worlds.

THE REAL PAGE. "Share profile updates", the live lane's capture of 2026-09-28
(``tests/fixtures/live2/setting.html``): the switch reads off; the AFTER world
is the same capture with the switch's ``checked`` set, which is what a fresh
render after a landed press would draw. Whether LinkedIn stores the press is
the live proof's question, and this file claims nothing about it.

THE SYNTHETIC PATTERNS are registered AT THE ADMITTED ADDRESS for a test (the
registry is monkeypatched; the read door, the write door and the spec are the
shipped ones), so a radio group and a select with a Save run through the same
doors the real page does. Their names are invented.

NOTHING HERE REACHES LINKEDIN: every load is ``set_content`` of a frozen world,
and every request a page would make is refused first.
"""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from linkedin_server import server, settings_writer as sw, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_settings_writer import (
    RADIO_MARKUP,
    SELECT_MARKUP,
    SWITCH_MARKUP,
    SYN_RADIO,
    SYN_SELECT,
    SYN_SWITCH,
    world,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_ACTION = "set_admitted_setting"
_REAL = (Path(__file__).parent / "fixtures" / "live2" / "setting.html").read_text(encoding="ascii")
_SWITCH_TAG = 'role="switch" type="checkbox">'
#: The capture as a fresh render would draw it after the switch was turned on.
_REAL_ON = _REAL.replace(_SWITCH_TAG, 'role="switch" type="checkbox" checked>')
_URL = sw.SHARE_PROFILE_UPDATES.url
_SETTING = "Share profile updates / Share key profile updates"


def _spec():
    return spec_for_action(_ACTION)


async def _refused(route) -> None:
    await route.abort()


class _Navigator:
    """Serves frozen worlds for the ONE admitted address, in order, and
    records every ask; the last world repeats. ``witness`` holds, per load,
    the page's own counters read BEFORE the next world replaces it."""

    def __init__(self, *worlds: str, landed: str = ""):
        self.worlds = list(worlds)
        self.gotos: list[str] = []
        self.landed = landed
        self.witness: list[dict] = []

    async def goto(self, page, url: str) -> str:
        self.gotos.append(url)
        if url != _URL:
            raise AssertionError(f"the gate asked for {url!r}, which this test did not freeze")
        self.witness.append(await page.evaluate(
            "() => ({presses: window.__presses || 0, saves: window.__saves || 0})"))
        html = self.worlds.pop(0) if len(self.worlds) > 1 else self.worlds[0]
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return self.landed or url


@pytest.fixture(autouse=True)
def _no_grants_survive_a_test():
    yield
    writes.discard_all()


async def _granted(page, value: str, *worlds: str, setting: str = _SETTING):
    """A real preview over frozen worlds, then the real token door."""
    nav = _Navigator(*worlds)
    target = {"setting": setting, "value": value}
    block = await preview(_spec(), target=target, navigator=nav, page=page, to_state=value)
    return consume(block["to_confirm"], action=_ACTION, target=target), block, nav


def test_the_action_is_sanctioned_performable_and_its_tool_takes_page_control_value():
    # writes.py spells the action and the tool as LITERALS, as every spec
    # does (its source scanners match literal action names); the module's
    # constants must be the same strings.
    assert (sw.ACTION, sw.TOOL_NAME) == (_ACTION, "linkedin_set_admitted_setting")
    spec = _spec()
    assert spec.tool_name == sw.TOOL_NAME
    assert spec.action in writes.PERFORMABLE
    assert spec.state_from == sw.STATE_FROM
    assert spec.target_kind == "setting_and_value"
    assert spec.url_pattern.match(_URL)
    assert not spec.url_pattern.match("https://www.linkedin.com/mypreferences/d/settings/language")
    assert writes.assert_write_url is not None
    tool = getattr(server, sw.TOOL_NAME)
    params = list(inspect.signature(getattr(tool, "fn", tool)).parameters)
    assert params == ["page", "control", "value", "confirm_token"]


def test_the_write_door_admits_the_admitted_page_and_exempts_only_its_own_two_substrings():
    grant = writes.WriteGrant(
        action=_ACTION, target=_SETTING + " :: on", token="t", minted_at=0.0
    )
    assert writes.assert_write_url(_URL, grant) == _URL
    for other in (
        "https://www.linkedin.com/mypreferences/d/settings/language",
        "https://www.linkedin.com/mypreferences/d/dark-mode",
        _URL + "/x",
    ):
        with pytest.raises(WriteAttemptError):
            writes.assert_write_url(other, grant)
    # THE EXEMPTION IS EXACT: the spec excuses the two substrings the
    # address carries and no others.
    assert set(_spec().exempt_substrings) == {"/settings/", "settings"}


async def test_the_real_page_end_to_end_off_to_on_verified_on_a_fresh_render(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    grant, block, nav = await _granted(page, "on", _REAL, _REAL, _REAL_ON)
    text = json.dumps(block)
    assert "Share profile updates" in text and "Share key profile updates" in text
    assert block["direction"]["currently"] == "off" and block["direction"]["after"] == "on"
    act = _Navigator(_REAL, _REAL_ON)
    receipt = await writes.perform(act, page, grant)
    assert receipt["performed"] is True, receipt
    assert act.gotos == [_URL, _URL]
    press = receipt["setting_press"]
    assert press["check"]["code"] is None and press["check"]["proceed"] is True, press
    assert press["save"]["needed"] is False
    assert receipt["restore"]["previous_value"] == "off"
    assert "value='off'" in receipt["restore"]["to_put_it_back"]


async def test_a_fresh_render_still_off_is_not_performed_and_another_value_is_refused(writes_on, browser_page):
    page = browser_page
    await page.route("**/*", _refused)
    grant, _block, _nav = await _granted(page, "on", _REAL)
    receipt = await writes.perform(_Navigator(_REAL, _REAL), page, grant)
    assert receipt["performed"] is False, receipt

    # THE TOKEN BINDS THE VALUE: a token shown for "on" does not confirm "off".
    nav = _Navigator(_REAL)
    block = await preview(_spec(), target={"setting": _SETTING, "value": "on"},
                          navigator=nav, page=page, to_state="on")
    with pytest.raises(WriteAttemptError):
        consume(block["to_confirm"], action=_ACTION, target={"setting": _SETTING, "value": "off"})

    # A NO-OP IS REFUSED: the page reads off, and off is asked for.
    with pytest.raises(WriteAttemptError):
        await preview(_spec(), target={"setting": _SETTING, "value": "off"},
                      navigator=_Navigator(_REAL), page=page, to_state="off")


async def test_an_unadmitted_page_control_or_value_loads_nothing_and_mints_nothing(writes_on, browser_page):
    page = browser_page
    for setting, value in (
        ("Sharing profile edits / Share key profile updates", "on"),
        ("Share profile updates / Sharing profile edits", "on"),
        ("Dark mode / Always on", "on"),
        (_SETTING, "sometimes"),
        ("Share profile updates", "on"),
    ):
        nav = _Navigator(_REAL)
        with pytest.raises(WriteAttemptError):
            await preview(_spec(), target={"setting": setting, "value": value},
                          navigator=nav, page=page, to_state=value)
        assert nav.gotos == [], (setting, value)
    assert writes._GRANTS == {}


def _synthetic_page(control, save_label=None, name="Synthetic page"):
    """A synthetic page registered AT THE ADMITTED ADDRESS, for a test."""
    return sw.AdmittedPage(
        name=name,
        url=_URL,
        save_label=save_label,
        controls=(control,),
        capture="synthetic",
        admitted_by="synthetic",
    )


def _after(markup: str, old: str, new: str) -> str:
    assert markup.count(old) == 1, old
    return markup.replace(old, new)


async def test_the_three_patterns_through_the_shipped_doors(writes_on, browser_page, monkeypatch):
    """Each pattern, registered at the admitted address: what was pressed,
    whether Save was pressed (the page's own witness, read before the
    verification replaced the page), and what the receipt decided."""
    page = browser_page
    select_page = _synthetic_page(SYN_SELECT, save_label="Save")
    select_after = _after(SELECT_MARKUP, '<option value="v-b" selected>Beta</option>',
                          '<option value="v-b">Beta</option>')
    select_after = _after(select_after, '<option value="v-c">Gamma</option>',
                          '<option value="v-c" selected>Gamma</option>')
    radio_after = _after(RADIO_MARKUP, 'id="r-never" aria-labelledby="l-never" checked>',
                         'id="r-never" aria-labelledby="l-never">')
    radio_after = _after(radio_after, 'id="r-always" aria-labelledby="l-always">',
                         'id="r-always" aria-labelledby="l-always" checked>')
    switch_after = _after(SWITCH_MARKUP, 'aria-checked="false" aria-labelledby="lbl-alerts"',
                          'aria-checked="true" aria-labelledby="lbl-alerts"')
    scenarios = [
        # label, page record, value, world at the press, world after, performed, code, saves
        ("select, clean, Save pressed", select_page, "Gamma",
         world(SELECT_MARKUP), world(select_after), True, None, 1),
        ("select, another select moved, no Save", select_page, "Gamma",
         world(SELECT_MARKUP, alsoChange=True), world(SELECT_MARKUP), False, "another_control_moved", 0),
        ("select, late choice waited for", select_page, "Gamma",
         world(SELECT_MARKUP, lateMs=500), world(select_after), True, None, 1),
        ("radio, late, waited for", _synthetic_page(SYN_RADIO), "Always",
         world(RADIO_MARKUP, lateMs=500), world(radio_after), True, None, 0),
        ("switch stores on press, another moved", _synthetic_page(SYN_SWITCH), "on",
         world(SWITCH_MARKUP, alsoFlip=True), world(switch_after), True, "another_control_moved", 0),
        ("switch, inert press", _synthetic_page(SYN_SWITCH), "on",
         world(SWITCH_MARKUP, inert=True), world(SWITCH_MARKUP), False, "the_control_did_not_move", 0),
    ]
    for label, record, value, at_press, after, performed, code, saves in scenarios:
        monkeypatch.setattr(sw, "ADMITTED_PAGES", (record,))
        setting = record.name + " / " + record.controls[0].label
        grant, block, _nav = await _granted(page, value, at_press, setting=setting)
        act = _Navigator(at_press, after)
        receipt = await writes.perform(act, page, grant)
        assert receipt["performed"] is performed, (label, receipt)
        press = receipt["setting_press"]
        assert press["check"]["code"] == code, (label, press)
        assert act.witness[1]["saves"] == saves, (label, act.witness)
        if code is not None:
            assert press["save"]["proceed"] is False, (label, press)
        writes.discard_all()
