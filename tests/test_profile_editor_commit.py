"""The profile editor's COMMIT: ``update_profile_field`` presses Save, and says so.

THE DEFECT, reproduced before the repair (lane L7, 2026-09-24). The shipped
write filled or selected the field and NEVER PRESSED ``Save``: after its fill
it fell through to the POST composer's gate, which found no post editor on the
intro editor and pressed nothing. Its verification then re-read THE SAME,
still-open dialog and reported ``field_changed``. Driven end to end over the
world below, whose stored value changes ONLY if Save is pressed before the
next navigation, the unrepaired module returned::

    performed        true
    observed_state   field_changed
    clicks_made      0
    stored value     unchanged

``test_performed_true_means_the_stored_value_changed`` is that measurement as
an assertion. Against the unrepaired ``writes.py`` it FAILS (performed true,
stored value unchanged); the lane record carries the run.

WHAT IS MEASURED AND WHAT IS INVENTED. Measured, 2026-08-31, on his live intro
editor: the dialog's commit control is named ``Save`` and is enabled, and the
editor's fields are named through ``label-for`` (``_audit/2026-08-31-linkedin-
finish.md`` section 2g). Everything else here is INVENTED markup: a value that
persists only on a Save press is how a server-backed form behaves, and a
notify-network switch is a control NOTHING ON RECORD says the intro editor
draws -- it is planted so the refusal that guards it can be seen firing.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import ast
import json
import re

import pytest

from linkedin_server import dom, profile_editor, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_surface_census import MEMBER_SLUG
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

_ACTION = "update_profile_field"
_SPEC = spec_for_action(_ACTION)
_EDITOR_URL = _SPEC.url_template

#: Where LinkedIn lands the two addresses: slugged, and the editor with no
#: trailing slash -- the measured shapes ``tests/test_editor_fields.py`` uses.
_LANDED_PROFILE = f"https://www.linkedin.com/in/{MEMBER_SLUG}/?isSelfProfile=true"
_LANDED_EDITOR = f"https://www.linkedin.com/in/{MEMBER_SLUG}/edit/intro"

#: The profile page: one editor anchor, which is all the preview reads.
_PROFILE_HTML = (
    "<!doctype html><html><body><main>"
    '<a href="https://www.linkedin.com/in/me/edit/intro/" aria-label="Edit profile">'
    "Edit</a></main></body></html>"
)

#: INVENTED values, distinctive so a leak would be visible.
_OLD_CITY = "Oldtownvale"
_NEW_CITY = "Newtownvale"


class _EditorWorld:
    """A frozen world whose editor values PERSIST ONLY ON A SAVE PRESS.

    The Save button's handler writes the form's values into ``window.__saved``
    and removes its dialog, the way LinkedIn closes the editor on a successful
    save. ``goto`` -- the only door a write has to the next page -- first
    collects anything saved on the page it is leaving, then renders the next
    one from the STORE. So a value typed into a dialog nobody saved is gone at
    the next navigation, exactly as it would be on the site.
    """

    def __init__(
        self,
        *,
        notify: str | None = None,
        unnamed_switch: bool = False,
        save_disabled: bool = False,
        save_rejects: bool = False,
    ):
        self.store = {"City": _OLD_CITY, "Month": "January"}
        self.notify = notify
        self.unnamed_switch = unnamed_switch
        self.save_disabled = save_disabled
        self.save_rejects = save_rejects
        self.gotos: list[str] = []
        self.saves = 0

    def editor_html(self) -> str:
        months = "".join(
            f"<option{' selected' if m == self.store['Month'] else ''}>{m}</option>"
            for m in ("January", "February", "March")
        )
        notify = ""
        if self.notify is not None:
            checked = " checked" if self.notify == "on" else ""
            notify = (
                '<label for="e-notify">Notify network</label>'
                f'<input id="e-notify" type="checkbox" role="switch"{checked}>'
            )
        switch = (
            '<input id="e-unnamed" type="checkbox" role="switch">'
            if self.unnamed_switch
            else ""
        )
        if self.save_rejects:
            # LinkedIn declining the value: the dialog stays open and nothing
            # is stored. A validation message is drawn instead.
            handler = "document.getElementById('e-error').textContent='Please select a value'"
        else:
            handler = (
                "window.__saved = JSON.stringify({"
                "City: document.getElementById('e-city').value, "
                "Month: document.getElementById('e-month').value}); "
                "this.closest('dialog').remove()"
            )
        disabled = " disabled" if self.save_disabled else ""
        return (
            "<!doctype html><html><body><main><h1>Profile</h1></main>"
            "<dialog open>"
            '<label for="e-city">City</label>'
            f'<input id="e-city" type="text" value="{self.store["City"]}">'
            '<label for="e-month">Month</label>'
            f'<select id="e-month">{months}</select>'
            f"{notify}{switch}"
            '<p id="e-error"></p>'
            f'<button type="button" onclick="{handler}"{disabled}>Save</button>'
            "</dialog></body></html>"
        )

    async def goto(self, page, url: str) -> str:
        try:
            saved = await page.evaluate(
                "() => { const s = window.__saved; delete window.__saved; "
                "return (typeof s === 'string') ? s : null; }"
            )
        except Exception:  # noqa: BLE001 - a fresh page holds nothing
            saved = None
        if saved:
            self.store.update(json.loads(saved))
            self.saves += 1
        self.gotos.append(url)
        if url == writes.PROFILE_URL:
            html, landed = _PROFILE_HTML, _LANDED_PROFILE
        elif url == _EDITOR_URL:
            html, landed = self.editor_html(), _LANDED_EDITOR
        else:
            raise AssertionError(f"the write asked for {url!r}, which this world does not serve")
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


async def _write(page, world: _EditorWorld, field: str, value: str) -> dict:
    """The real two calls: preview (mints), consume (redeems), perform."""
    target = {"field": field, "value": value}
    block = await preview(_SPEC, target=target, navigator=world, page=page)
    grant = consume(
        block["to_confirm"], action=_ACTION, target=writes._target_for(_SPEC, target)
    )
    receipt = await writes.perform(world, page, grant)
    # One more navigation, as the next tool call would make: it persists a
    # save that happened and discards a dialog nobody saved.
    await world.goto(page, writes.PROFILE_URL)
    return receipt


# ---------------------------------------------------------------------------
# 1. The defect, as an invariant: performed true means the value was STORED
# ---------------------------------------------------------------------------


async def test_performed_true_means_the_stored_value_changed(writes_on, browser_page):
    """SHOWN FAILING against the unrepaired module: there, this returned
    ``performed: true`` with ``clicks_made: 0`` and the store unchanged."""
    world = _EditorWorld()
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store["City"] == _NEW_CITY, (
        "performed was reported true and the stored value did not change"
    )
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["editor_save_gate"]["proceeded"] is True
    assert receipt["editor_save_gate"]["editor_closed_after_save"] is True
    assert receipt["verification"]["read_from"] == _EDITOR_URL
    assert MEMBER_SLUG not in receipt["verification"]["read_from"]


async def test_without_the_press_the_verification_now_says_not_performed(
    writes_on, browser_page, monkeypatch
):
    """The verification can FAIL. With the save gate forced to decline, the
    change sits in an unsaved dialog, the fresh render reads the stored value,
    and the write reports ``performed: false`` -- where the shipped code read
    the unsaved dialog and reported true."""

    async def declines(_page):
        gate = profile_editor.save_gate_verdict({"refused": "no_anchor"})
        return gate

    monkeypatch.setattr(profile_editor, "read_save_gate", declines)
    world = _EditorWorld()
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    assert receipt["clicked"]["clicks_made"] == 0
    assert world.store["City"] == _OLD_CITY
    assert receipt["verification"]["observed_state"] == "value_unchanged"
    assert receipt["performed"] is False


async def test_a_chosen_value_is_saved_too(writes_on, browser_page):
    """A select drains BEFORE the click loop, so the gate is asked there too."""
    world = _EditorWorld()
    receipt = await _write(browser_page, world, "Month", "March")
    assert world.store["Month"] == "March"
    assert receipt["performed"] is True
    assert receipt["clicked"]["clicks_made"] == 1


async def test_linkedin_declining_the_value_reads_as_not_performed(writes_on, browser_page):
    """The press happens, the dialog stays open, nothing is stored."""
    world = _EditorWorld(save_rejects=True)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    assert receipt["clicked"]["clicks_made"] == 1
    assert receipt["editor_save_gate"]["editor_closed_after_save"] is False
    assert world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False


# ---------------------------------------------------------------------------
# 2. Condition 1 of SELF-PROFILE-EDITS-NOT-OUTWARD: notify-network
# ---------------------------------------------------------------------------


async def test_a_notify_network_control_that_is_on_refuses_the_press(writes_on, browser_page):
    world = _EditorWorld(notify="on")
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "4_notify_network_not_off"
    assert gate["notify_network"] == "on"
    assert receipt["clicked"]["clicks_made"] == 0
    assert world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False


async def test_a_notify_network_control_that_is_off_is_confirmed_off(writes_on, browser_page):
    world = _EditorWorld(notify="off")
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["proceeded"] is True and gate["notify_network"] == "off"
    assert gate["notify_network_means"].startswith("CONFIRMED OFF")
    assert world.store["City"] == _NEW_CITY


async def test_an_unnamed_switch_is_not_confirmed_off(writes_on, browser_page):
    """The measured intro editor draws two switches with NO accessible name.
    Either could be a notify toggle, so 'not drawn' beside them is not
    'confirmed off', and the receipt must say so rather than imply it."""
    world = _EditorWorld(unnamed_switch=True)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["notify_network"] == "not_drawn"
    assert gate["unnamed_switches"] == 1
    assert gate["notify_network_means"].startswith("NOT CONFIRMED")


async def test_a_disabled_save_is_not_pressed(writes_on, browser_page):
    world = _EditorWorld(save_disabled=True)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    assert receipt["editor_save_gate"]["refused_condition"] == "2_save_disabled"
    assert receipt["clicked"]["clicks_made"] == 0
    assert world.store["City"] == _OLD_CITY


# ---------------------------------------------------------------------------
# 3. The restore path, itself tested: write, restore, before == after
# ---------------------------------------------------------------------------


def _restore_call(receipt: dict) -> tuple[str, str]:
    """Parse the receipt's own ``to_put_it_back`` -- the exact call he would
    make -- rather than re-deriving the old value here."""
    call = receipt["restore"]["to_put_it_back"].split("#", 1)[0].strip()
    node = ast.parse(call, mode="eval").body
    assert isinstance(node, ast.Call) and node.func.id == "linkedin_update_profile_field"
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
    return kwargs["field"], kwargs["value"]


async def _reading(page, world: _EditorWorld) -> dict:
    """The before/after reading: a fresh render of the editor, values read by
    the shipped values reader -- what ``linkedin_profile_editor_values`` uses."""
    await world.goto(page, _EDITOR_URL)
    reading = await dom.read_self_owned_editor_values(page)
    return {
        f["name"]: f.get("value")
        for f in reading.get("fields") or []
        if f.get("name") in ("City", "Month")
    }


async def test_the_restore_path_round_trips_and_the_readings_prove_it(writes_on, browser_page):
    world = _EditorWorld()
    before = await _reading(browser_page, world)
    assert before == {"City": _OLD_CITY, "Month": "January"}

    first = await _write(browser_page, world, "City", _NEW_CITY)
    assert first["performed"] is True
    assert first["restore"]["previous_value"] == _OLD_CITY
    assert "before the write" in first["restore"]["how_it_was_read"]
    middle = await _reading(browser_page, world)
    assert middle["City"] == _NEW_CITY

    field, value = _restore_call(first)
    assert (field, value) == ("City", _OLD_CITY)
    second = await _write(browser_page, world, field, value)
    assert second["performed"] is True

    after = await _reading(browser_page, world)
    assert after == before, "the restore did not put the editor back as it was"


# ---------------------------------------------------------------------------
# 4. The three grant controls, for this action
# ---------------------------------------------------------------------------


async def test_control_1_no_grant_moves_nothing(monkeypatch, browser_page):
    world = _EditorWorld()
    monkeypatch.delenv(writes.WRITES_FLAG, raising=False)
    with pytest.raises(WriteAttemptError, match="disabled"):
        await preview(_SPEC, target={"field": "City", "value": _NEW_CITY},
                      navigator=world, page=browser_page)
    monkeypatch.setenv(writes.WRITES_FLAG, "1")
    target = writes._target_for(_SPEC, {"field": "City", "value": _NEW_CITY})
    for bogus in ("", None, "not-a-real-token"):
        with pytest.raises(WriteAttemptError):
            consume(bogus, action=_ACTION, target=target)
    unredeemed = writes.WriteGrant(action=_ACTION, target=target, token="t", minted_at=0.0)
    with pytest.raises(WriteAttemptError, match="not been redeemed"):
        await writes.perform(world, browser_page, unredeemed)
    assert world.gotos == [] and world.store["City"] == _OLD_CITY
    writes.discard_all()


async def test_control_2_a_grant_for_another_value_or_field_is_refused(writes_on, browser_page):
    world = _EditorWorld()
    block = await preview(_SPEC, target={"field": "City", "value": _NEW_CITY},
                          navigator=world, page=browser_page)
    for other in ({"field": "City", "value": "Elsewhere"},
                  {"field": "Month", "value": _NEW_CITY}):
        with pytest.raises(WriteAttemptError, match="minted for target"):
            consume(block["to_confirm"], action=_ACTION,
                    target=writes._target_for(_SPEC, other))


async def test_control_3_a_grant_is_spent_once(writes_on, browser_page):
    world = _EditorWorld()
    target = {"field": "City", "value": _NEW_CITY}
    block = await preview(_SPEC, target=target, navigator=world, page=browser_page)
    canonical = writes._target_for(_SPEC, target)
    grant = consume(block["to_confirm"], action=_ACTION, target=canonical)
    with pytest.raises(WriteAttemptError, match="unknown or already-discarded"):
        consume(block["to_confirm"], action=_ACTION, target=canonical)
    await writes.perform(world, browser_page, grant)
    before = list(world.gotos)
    with pytest.raises(WriteAttemptError, match="already been used once"):
        await writes.perform(world, browser_page, grant)
    assert world.gotos == before


# ---------------------------------------------------------------------------
# 5. The verdict itself, without a browser
# ---------------------------------------------------------------------------


def _field(name, *, tag="input", source="label-for", **extra):
    base = {"name": name, "name_source": source, "tag": tag, "type": None,
            "role": None, "disabled": False, "checked": None, "required": None}
    base.update(extra)
    return base


_SAVE = _field("Save", tag="button", source="text")
_CITY = _field("City", type="text")


@pytest.mark.parametrize(
    "reading, code",
    [
        ({"refused": "no_anchor", "reason": "x"}, "0_editor_not_found"),
        ({"fields": [_CITY]}, "1_save_not_exactly_one"),
        ({"fields": [_SAVE, dict(_SAVE), _CITY]}, "1_save_not_exactly_one"),
        ({"fields": [dict(_SAVE, disabled=True), _CITY]}, "2_save_disabled"),
        ({"fields": [_SAVE, _field("Notify network", type="checkbox", checked=False),
                     _field("Share with network", type="checkbox", checked=False)]},
         "3_notify_network_ambiguous"),
        ({"fields": [_SAVE, _field("Notify network", type="checkbox", checked=True)]},
         "4_notify_network_not_off"),
        ({"fields": [_SAVE, _field("Notify network", role="switch", checked=None)]},
         "4_notify_network_not_off"),
    ],
    ids=["no-editor", "no-save", "two-saves", "save-disabled", "two-notify",
         "notify-on", "notify-unreadable"],
)
def test_every_refusal_has_its_own_code(reading, code):
    gate = profile_editor.save_gate_verdict(reading)
    assert gate["proceed"] is False and gate["refused_condition"] == code
    assert gate["selector"] == profile_editor.SAVE_SELECTOR


def test_a_button_named_like_a_notify_control_is_not_the_setting():
    """Only a CHECKABLE control is a setting the save carries."""
    gate = profile_editor.save_gate_verdict(
        {"fields": [_SAVE, _field("Share with network", tag="button", source="text")]}
    )
    assert gate["proceed"] is True and gate["notify_network"] == "not_drawn"


def test_no_why_quotes_a_control_name_the_page_chose():
    planted = "Notify network about Exampleperson Markersurname"
    gate = profile_editor.save_gate_verdict(
        {"fields": [_SAVE, _field(planted, type="checkbox", checked=True)]}
    )
    assert gate["refused_condition"] == "4_notify_network_not_off"
    assert "Markersurname" not in gate["why"]
    assert "Markersurname" not in profile_editor.notify_network_note(gate)


def test_the_save_name_is_the_container_anchor_and_not_a_second_copy():
    assert profile_editor.SAVE_CONTROL_NAME == dom.EDITOR_ANCHOR_NAME == "Save"
    assert '"Save"s]' in profile_editor.SAVE_SELECTOR


async def test_the_save_selector_matches_the_one_visible_save_and_nothing_after(browser_page):
    world = _EditorWorld()
    await browser_page.set_content(world.editor_html())
    assert await browser_page.locator(profile_editor.SAVE_SELECTOR).count() == 1
    # A CLOSED dialog's button is not drawn, so it cannot be pressed.
    await browser_page.evaluate("() => document.querySelector('dialog').close()")
    assert await browser_page.locator(profile_editor.SAVE_SELECTOR).count() == 0
    # And a Save outside any dialog is not this editor's.
    await browser_page.set_content("<button>Save</button>")
    assert await browser_page.locator(profile_editor.SAVE_SELECTOR).count() == 0


def test_the_action_is_the_only_editor_save_action():
    assert writes.EDITOR_SAVE_ACTIONS == frozenset({_ACTION})
    assert _ACTION in writes.PERFORMABLE
    assert re.search(r"fresh navigation", writes._VERIFIED_FROM[_ACTION], re.I)
