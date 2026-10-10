"""P B9, the Premium badge's show / hide: the press AIMED BY THE BLOCK'S TITLE (lane L7, 2026-09-24).

THE RULING, relayed by the coordinator's order of 2026-09-24 (the
orchestrator's call, 09:15): the switch's block title, "Profile Premium Badge",
is a LinkedIn UI string and not his data, and it may aim the press when ALL of
these hold -- and each has its test below:

1. it is compared INSIDE THE PAGE, never read out or returned;
2. it matches EXACTLY ONE settings row in the intro editor's column, or the
   write refuses;
3. a non-English UI refuses, because the string will not match -- fail-closed
   by construction;
4. a before/after reading proves that ONLY that switch changed, and that the
   other switch in its row (Open Profile, P B10, by the capture) did not;
5. the restore, switching it back, is tested the same way.

WRITTEN BEFORE THE BUILD, as the order asked: the first four tests -- two rows
carrying the title, none, a swapped order, a non-English title -- were run
against the module as it stood and failed (the record carries the run).

THE WORLD IS INVENTED around the capture's STRUCTURE: the settings row of
``tests/fixtures/synthetic/intro_editor_switches.html``, with the one real
string the ruling admits placed on the badge's block. Two switches whose state
persists only when the dialog's ``Save`` is pressed (or, in one world, the
moment the switch is pressed -- which one LinkedIn does is NOT MEASURED, and the
write is built to be safe under both). Condition 1 of
``SELF-PROFILE-EDITS-NOT-OUTWARD`` is established the only way the unwired gate
accepts: a planted notify control read off, as in
``tests/test_profile_editor_commit.py``.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re

import pytest

from linkedin_server import profile_editor, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_surface_census import MEMBER_SLUG
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"
BASE = FIXTURE.read_text(encoding="utf-8")

_ACTION = "update_profile_field"
_SPEC = spec_for_action(_ACTION)
_EDITOR_URL = _SPEC.url_template
_LANDED_PROFILE = "https://www.linkedin.com/in/" + MEMBER_SLUG + "/?isSelfProfile=true"
_LANDED_EDITOR = "https://www.linkedin.com/in/" + MEMBER_SLUG + "/edit/intro"
_PROFILE_HTML = (
    "<!doctype html><html><body><main>"
    '<a href="https://www.linkedin.com/in/me/edit/intro/" aria-label="Edit profile">'
    "Edit</a></main></body></html>"
)

#: The one string the ruling admits, and the field name the write is called by.
TITLE = "Profile Premium Badge"
#: A non-English UI's title for the same block. Invented for the test; what
#: matters is only that it is not the English string.
FOREIGN_TITLE = "Insignia Premium del perfil"

BADGE_ID = "intro-switch-2"
OTHER_ID = "intro-switch-1"

_SAVE_BUTTON = '<button type="button">Save</button>'
_BLOCK_A_START = "<div><div><p>Placeholder setting A"
_BLOCK_B_START = "<div><div><p>Placeholder setting B"
_ROW_END = "</div></div>\n" + _SAVE_BUTTON

#: The component's behaviour, INVENTED: pressing a wrapper flips it; a Save
#: press writes both switches' states into ``window.__saved`` and closes the
#: dialog. ``data-press-moves`` plants the two failures the write must catch:
#: a press that moves nothing, and a press that moves the other switch too.
#: IN THE SECOND RECORDED SHAPE THE PRESS LANDS ON THE TOGGLE (the live lane's
#: session 8, 2026-10-10): the named input draws no box, so the toggle that
#: holds it -- its empty label, the input and the knob -- is what a press
#: reaches, and pressing it flips the input; the planted 'both' failure flips
#: the other toggle too.
_SCRIPT = (
    "<script>"
    "window.__flip = function (w) {"
    " const input = w.querySelector('input[type=\"checkbox\"]');"
    " const on = !input.checked;"
    " if (w.hasAttribute('aria-checked')) { w.setAttribute('aria-checked', on ? 'true' : 'false'); }"
    " input.checked = on; };"
    "window.__commit = function () {"
    " const s = {};"
    " document.querySelectorAll('input[role=\"switch\"][id^=\"intro-switch-\"]')"
    ".forEach(function (i) { s[i.id] = i.checked; });"
    " window.__saved = JSON.stringify(s); };"
    "window.__press = function (event, w) {"
    " const mode = document.body.dataset.pressMoves;"
    " event.preventDefault();"
    " if (mode === 'nothing') { return; }"
    " window.__flip(w);"
    " if (mode === 'both') {"
    " document.querySelectorAll(w.hasAttribute('role') ? 'div[role=\"switch\"]' : 'div[data-toggle]')"
    ".forEach(function (x) { if (x !== w) { window.__flip(x); } }); }"
    " if (document.body.dataset.commitsOnPress === 'yes') { window.__commit(); } };"
    "</script>"
)

#: THE SECOND RECORDED SWITCH SHAPE, MEASURED 2026-10-10 (the live lane's
#: session 7, two loads of his intro editor): the wrapper carries none of
#: role, aria-checked, tabindex or aria-label, and the checkbox input carries
#: the label beside the role=switch it always had. The label below is the
#: fixture's invented one; the live label was measured only as a shape.
#: AND WHERE A PRESS CAN LAND, MEASURED THE SAME DAY (session 8, two
#: read-only loads): the named input draws no box and is not visible; the
#: div holding its empty label, the input and the knob is drawn, 52 x 32.
_WRAPPER = re.compile(
    r'<div role="switch" aria-checked="(?:true|false)" tabindex="0" aria-label="Tap to toggle setting">'
)
_INPUT_OPEN = '<input role="switch" type="checkbox"'
#: The toggle around the input, as the capture draws it: one div holding the
#: empty label, the input and the knob.
_TOGGLE_OPEN = "<div><label for="


def _as_named_input(block: str, *, label: str = "Tap to toggle setting", toggle: str = "drawn") -> str:
    """One setting block redrawn in the second shape, AS SESSION 8 MEASURED IT.

    The input carries the label and draws no box; the toggle holding it is
    drawn at the live size and is what a press reaches. ``toggle`` plants the
    two ways it can fail to be a press target: ``"hidden"`` draws no box for
    the toggle either, and ``"absent"`` draws the input's parent as a span,
    so no div holds the label and the input together.
    """
    assert len(_WRAPPER.findall(block)) == 1, "the block no longer draws the recorded wrapper"
    assert block.count(_INPUT_OPEN) == 1, "the block no longer draws one switch input"
    assert block.count(_TOGGLE_OPEN) == 1, "the block no longer draws one toggle around its input"
    block = _WRAPPER.sub("<div>", block)
    block = block.replace(_INPUT_OPEN, _INPUT_OPEN + ' aria-label="' + label + '" hidden=""', 1)
    style = "display:none" if toggle == "hidden" else "display:inline-block;width:52px;height:32px"
    tag = "span" if toggle == "absent" else "div"
    block = block.replace(
        _TOGGLE_OPEN,
        "<" + tag + ' data-toggle="" style="' + style + '" onclick="__press(event, this)"><label for=',
        1,
    )
    if tag == "span":
        assert block.count("<span></span></div>") == 1, "the knob no longer closes the toggle"
        block = block.replace("<span></span></div>", "<span></span></span>", 1)
    return block


def _split(html: str) -> tuple[str, str, str, str]:
    """(everything before block A, block A, block B, the row's end onward)."""
    a = html.index(_BLOCK_A_START)
    b = html.index(_BLOCK_B_START)
    end = html.index(_ROW_END)
    return html[:a], html[a:b], html[b:end], html[end:]


def _with_state(block: str, on: bool) -> str:
    block = block.replace('aria-checked="true"', 'aria-checked="' + ("true" if on else "false") + '"')
    return block if on else block.replace(' checked=""', "")


def _pressable(block: str) -> str:
    return block.replace('<div role="switch"', '<div role="switch" onclick="__press(event, this)"')


class _BadgeWorld:
    """A frozen intro editor holding the capture's settings row.

    ``store`` is what LinkedIn has STORED, keyed by the switch's invented id --
    so identity follows the switch, never its position, and a test can say
    which one moved whatever order the row was drawn in.
    """

    def __init__(
        self,
        *,
        badge: bool = True,
        other: bool = True,
        swapped: bool = False,
        badge_title: str = TITLE,
        second_titled_row: bool = False,
        notify: bool = True,
        press_moves: str = "self",
        commits_on_press: bool = False,
        other_title: str = "Placeholder setting A",
        description: str = "Placeholder description B",
        named_input: bool = False,
        named_other: "bool | None" = None,
        empty_label: bool = False,
        toggle: str = "drawn",
    ):
        self.store = {OTHER_ID: other, BADGE_ID: badge}
        #: The second recorded shape (2026-10-10), on the badge's block, and on
        #: the other block unless ``named_other`` says otherwise -- a row that
        #: draws the two shapes at once is a world of its own.
        self.named_input = named_input
        self.named_other = named_input if named_other is None else named_other
        self.empty_label = empty_label
        #: The badge's toggle in the second shape: drawn, hidden or absent.
        self.toggle = toggle
        self.swapped = swapped
        self.badge_title = badge_title
        self.second_titled_row = second_titled_row
        self.notify = notify
        self.press_moves = press_moves
        self.commits_on_press = commits_on_press
        self.other_title = other_title
        self.description = description
        self.gotos: list[str] = []
        self.saves = 0

    def editor_html(self) -> str:
        head, block_a, block_b, tail = _split(BASE)
        block_a = _with_state(block_a, self.store[OTHER_ID])
        block_b = _with_state(block_b, self.store[BADGE_ID])
        label = "" if self.empty_label else "Tap to toggle setting"
        block_a = _as_named_input(block_a, label=label) if self.named_other else _pressable(block_a)
        block_b = (
            _as_named_input(block_b, label=label, toggle=self.toggle)
            if self.named_input
            else _pressable(block_b)
        )
        block_a = block_a.replace("Placeholder setting A", self.other_title)
        block_b = block_b.replace("Placeholder setting B", self.badge_title)
        block_b = block_b.replace("Placeholder description B", self.description)
        blocks = block_b + block_a if self.swapped else block_a + block_b
        extra = ""
        if self.second_titled_row:
            copy = "<div><p>Placeholder section</p>" + block_a + block_b + "</div>"
            extra = copy.replace(OTHER_ID, "intro-switch-3").replace(BADGE_ID, "intro-switch-4")
        tail = tail.replace("</div></div>\n", "</div>" + extra + "</div>\n", 1)
        notify = (
            '<label for="e-notify">Notify network</label>'
            '<input id="e-notify" type="checkbox" role="switch">'
            if self.notify
            else ""
        )
        save = (
            '<button type="button" '
            "onclick=\"__commit(); this.closest('dialog').remove()\">Save</button>"
        )
        tail = tail.replace(_SAVE_BUTTON, notify + save, 1)
        body_attrs = (
            ' data-press-moves="' + self.press_moves + '"'
            + ' data-commits-on-press="' + ("yes" if self.commits_on_press else "no") + '"'
        )
        html = head.replace("<body>", "<body" + body_attrs + ">" + _SCRIPT, 1)
        return html + blocks + tail

    async def goto(self, page, url: str) -> str:
        try:
            saved = await page.evaluate(
                "() => { const s = window.__saved; delete window.__saved; "
                "return (typeof s === 'string') ? s : null; }"
            )
        except Exception:  # noqa: BLE001 - a fresh page holds nothing
            saved = None
        if saved:
            for key, value in json.loads(saved).items():
                if key in self.store:
                    self.store[key] = bool(value)
            self.saves += 1
        self.gotos.append(url)
        if url == writes.PROFILE_URL:
            html, landed = _PROFILE_HTML, _LANDED_PROFILE
        elif url == _EDITOR_URL:
            html, landed = self.editor_html(), _LANDED_EDITOR
        else:
            raise AssertionError("the write asked for " + repr(url) + ", which this world does not serve")
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


async def _write(page, world: _BadgeWorld, value: str) -> dict:
    """The real preview (mints), consume (redeems) and perform, then the next
    navigation a following tool call would make, which persists a Save that
    happened and discards a dialog nobody saved."""
    target = {"field": TITLE, "value": value}
    block = await preview(_SPEC, target=target, navigator=world, page=page)
    grant = consume(block["to_confirm"], action=_ACTION, target=writes._target_for(_SPEC, target))
    receipt = await writes.perform(world, page, grant)
    await world.goto(page, writes.PROFILE_URL)
    return receipt


async def _refused(page, world: _BadgeWorld, value: str) -> str:
    """A write that must refuse BEFORE anything moves: returns the message."""
    target = {"field": TITLE, "value": value}
    block = await preview(_SPEC, target=target, navigator=world, page=page)
    grant = consume(block["to_confirm"], action=_ACTION, target=writes._target_for(_SPEC, target))
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(world, page, grant)
    await world.goto(page, writes.PROFILE_URL)
    return str(excinfo.value)


# ---------------------------------------------------------------------------
# 1. THE FOUR THE ORDER NAMED, written first
# ---------------------------------------------------------------------------


async def test_two_rows_carrying_the_title_refuse(writes_on, browser_page):
    world = _BadgeWorld(second_titled_row=True)
    message = await _refused(browser_page, world, "off")
    assert "more than one" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


async def test_no_row_carrying_the_title_refuses(writes_on, browser_page):
    world = _BadgeWorld(badge_title="Placeholder setting B")
    message = await _refused(browser_page, world, "off")
    assert "no settings row" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


async def test_a_swapped_order_presses_the_badge_by_its_title(writes_on, browser_page):
    """The render draws the badge's block FIRST. An aim by order would press
    Open Profile here; the aim by title presses the badge, and only it."""
    world = _BadgeWorld(swapped=True)
    receipt = await _write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}
    assert receipt["switch_press"]["before"]["badge_position"] == 1


async def test_a_non_english_ui_refuses_by_construction(writes_on, browser_page):
    """Not a language check: the English string simply matches nothing, so the
    count is 0 and the refusal is the no-row refusal -- fail-closed by
    construction."""
    world = _BadgeWorld(badge_title=FOREIGN_TITLE)
    message = await _refused(browser_page, world, "off")
    assert "no settings row" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


# ---------------------------------------------------------------------------
# 2. Only that switch changes, proven before Save and after it -- and back
# ---------------------------------------------------------------------------


async def test_switching_the_badge_off_moves_only_the_badge(writes_on, browser_page):
    world = _BadgeWorld()
    receipt = await _write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}
    press = receipt["switch_press"]
    assert press["before"] == {"badge_on": True, "other_on": True, "badge_position": 2}
    assert press["after_the_press"] == {"badge_on": False, "other_on": True}
    assert press["only_the_badge_moved"]["proceed"] is True
    assert press["condition_1_before_the_press"]["proceeded"] is True
    assert press["after_a_fresh_render"] == {"badge_on": False, "other_on": True}
    assert receipt["clicked"]["clicks_made"] == 2
    assert receipt["editor_save_gate"]["proceeded"] is True
    assert receipt["verification"]["observed_state"] == "field_changed"
    assert receipt["restore"]["previous_value"] == "on"


def _restore_value(receipt: dict) -> str:
    """The value in the receipt's own ``to_put_it_back`` call, parsed."""
    call = receipt["restore"]["to_put_it_back"].split("#", 1)[0].strip()
    node = ast.parse(call, mode="eval").body
    assert isinstance(node, ast.Call) and node.func.id == "linkedin_update_profile_field"
    kwargs = {k.arg: ast.literal_eval(k.value) for k in node.keywords}
    assert kwargs["field"] == TITLE
    return kwargs["value"]


async def test_the_restore_switches_it_back_the_same_way(writes_on, browser_page):
    world = _BadgeWorld()
    before = dict(world.store)
    first = await _write(browser_page, world, "off")
    assert first["performed"] is True and world.store[BADGE_ID] is False
    second = await _write(browser_page, world, _restore_value(first))
    assert second["performed"] is True, second["verification"]
    assert second["switch_press"]["only_the_badge_moved"]["proceed"] is True
    assert second["switch_press"]["after_a_fresh_render"] == {"badge_on": True, "other_on": True}
    assert world.store == before, "before and after the round trip differ"


async def test_a_press_that_also_moves_open_profile_is_not_saved(writes_on, browser_page):
    """The in-dialog reading after the press sees the other switch move, so
    Save is not pressed and the next navigation discards the dialog."""
    world = _BadgeWorld(press_moves="both")
    receipt = await _write(browser_page, world, "off")
    press = receipt["switch_press"]
    assert press["only_the_badge_moved"]["proceed"] is False
    assert press["only_the_badge_moved"]["code"] == "the_other_switch_moved"
    assert receipt["clicked"]["clicks_made"] == 1
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0
    assert receipt["performed"] is False


async def test_a_press_that_moves_nothing_is_not_saved(writes_on, browser_page):
    world = _BadgeWorld(press_moves="nothing")
    receipt = await _write(browser_page, world, "off")
    assert receipt["switch_press"]["only_the_badge_moved"]["code"] == "the_badge_did_not_move"
    assert receipt["clicked"]["clicks_made"] == 1
    assert world.store == {OTHER_ID: True, BADGE_ID: True}
    assert receipt["verification"]["observed_state"] == "value_unchanged"
    assert receipt["performed"] is False


async def test_a_press_that_commits_on_its_own_is_still_verified(writes_on, browser_page):
    """If LinkedIn stores the switch the moment it is pressed, the fresh
    render says so -- whatever Save then does."""
    world = _BadgeWorld(commits_on_press=True)
    receipt = await _write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}


# ---------------------------------------------------------------------------
# 3. Nothing is pressed until it may be
# ---------------------------------------------------------------------------


async def test_condition_1_is_read_before_the_switch_is_pressed(writes_on, browser_page):
    """A SWITCH MAY COMMIT ON ITS OWN, so condition 1 cannot wait for Save.
    In a world where the press itself stores the change and nothing
    establishes condition 1, the switch is never pressed at all."""
    world = _BadgeWorld(notify=False, commits_on_press=True)
    receipt = await _write(browser_page, world, "off")
    gate = receipt["switch_press"]["condition_1_before_the_press"]
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "5_condition_1_not_established"
    assert receipt["clicked"]["clicks_made"] == 0
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0
    assert receipt["performed"] is False


async def test_a_badge_already_in_the_requested_state_is_not_pressed(writes_on, browser_page):
    """Pressing it would switch it the OTHER way."""
    world = _BadgeWorld(badge=False)
    message = await _refused(browser_page, world, "off")
    assert "already" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: False}


async def test_a_value_the_switch_cannot_take_is_refused_before_a_token(writes_on, browser_page):
    world = _BadgeWorld()
    with pytest.raises(WriteAttemptError) as excinfo:
        await preview(_SPEC, target={"field": TITLE, "value": "hide"}, navigator=world, page=browser_page)
    assert "'on' or 'off'" in str(excinfo.value)
    assert world.gotos == []


async def test_no_page_text_leaves_through_the_receipt(writes_on, browser_page):
    """Condition 1 of the ruling: the title is compared in the page and nothing
    the page draws comes back. Planted strings in the badge's description and
    in the other block's title do not reach the receipt."""
    world = _BadgeWorld(other_title="Plantedsecretone", description="Plantedsecrettwo")
    receipt = await _write(browser_page, world, "off")
    assert receipt["performed"] is True
    text = json.dumps(receipt)
    assert "Plantedsecret" not in text


# ---------------------------------------------------------------------------
# 4. The reader and the verdicts, without a write
# ---------------------------------------------------------------------------


async def test_the_reader_returns_counts_positions_and_states_only(browser_page):
    world = _BadgeWorld(other_title="Plantedsecretone")
    await browser_page.set_content(world.editor_html(), wait_until="domcontentloaded")
    reading = await profile_editor.read_premium_badge(browser_page)
    assert reading["aimable"] is True, reading["why"]
    assert reading["rows_titled"] == 1 and reading["recorded_rows_titled"] == 1
    assert reading["badge_position"] == 2
    assert reading["badge_checked"] is True and reading["other_checked"] is True
    assert "Plantedsecret" not in repr(reading)
    assert ':text-is("' + TITLE + '")' in reading["selector"]


async def test_a_reader_failure_refuses_and_says_only_its_type():
    class _Failing:
        def locator(self, *_a, **_k):
            return self

        def get_by_role(self, *_a, **_k):
            return self

        def and_(self, *_a, **_k):
            return self

        async def count(self):
            raise RuntimeError("Plantedname Plantedsurname")

    reading = await profile_editor.read_premium_badge(_Failing())
    assert reading["aimable"] is False and reading["error"] == "RuntimeError"
    assert "Planted" not in repr(reading)


def test_the_save_gate_can_be_read_before_a_press_without_save():
    """``require_save=False`` skips conditions 1 and 2 (the Save control) and
    keeps every notify condition: the pre-press reading of condition 1."""
    notify_off = {"name": "Notify network", "name_source": "label-for", "tag": "input",
                  "type": "checkbox", "role": "switch", "disabled": False, "checked": False}
    saveless = {"fields": [notify_off]}
    assert profile_editor.save_gate_verdict(saveless)["refused_condition"] == "1_save_not_exactly_one"
    early = profile_editor.save_gate_verdict(saveless, require_save=False)
    assert early["proceed"] is True and early["condition_1"] == "dialog_control_off"
    unestablished = profile_editor.save_gate_verdict({"fields": []}, require_save=False)
    assert unestablished["refused_condition"] == "5_condition_1_not_established"


def test_the_verdicts_hold_their_own_rules():
    before = {"aimable": True, "badge_position": 2, "badge_checked": True, "other_checked": True,
              "selector": "css=x"}
    aim = profile_editor.premium_badge_aim(before, "off")
    assert aim["proceed"] is True and aim["selector"] == "css=x"
    assert profile_editor.premium_badge_aim(before, "on")["proceed"] is False
    assert profile_editor.premium_badge_aim(before, "shown")["proceed"] is False
    assert profile_editor.premium_badge_aim({"aimable": False, "why": "w"}, "off")["proceed"] is False
    moved = dict(before, badge_checked=False)
    assert profile_editor.badge_moved_alone(before, moved, "off")["proceed"] is True
    both = dict(moved, other_checked=False)
    assert profile_editor.badge_moved_alone(before, both, "off")["code"] == "the_other_switch_moved"
    shifted = dict(moved, badge_position=1)
    assert profile_editor.badge_moved_alone(before, shifted, "off")["code"] == "the_row_changed"
    assert profile_editor.badge_verification(before, moved, "off")[0] == "field_changed"
    assert profile_editor.badge_verification(before, before, "off")[0] == "value_unchanged"
    assert profile_editor.badge_verification(before, both, "off")[0] is None
    assert profile_editor.premium_badge_value(before) == ("on", profile_editor.premium_badge_value(before)[1])


# ---------------------------------------------------------------------------
# 5. THE SECOND RECORDED SHAPE (2026-10-10): the switch named on its own input
# ---------------------------------------------------------------------------
#
# MEASURED on two loads of his intro editor in the live lane's session 7: the
# reader answered ``3_not_the_recorded_row`` on both, because the setting
# block's wrapper no longer carries role=switch, aria-checked, tabindex or
# aria-label, and the checkbox input carries the label itself. These were
# written first and run red against the reader as it stood.


async def test_the_reader_reads_the_switch_named_on_its_input(browser_page):
    """The badge is still found by its block's title, compared in the page; the
    switch inside that block by its own role, on the input that carries it."""
    world = _BadgeWorld(named_input=True, other_title="Plantedsecretone")
    await browser_page.set_content(world.editor_html(), wait_until="domcontentloaded")
    reading = await profile_editor.read_premium_badge(browser_page)
    assert reading["aimable"] is True, reading["why"]
    assert reading["switch_shape"] == "named_input"
    assert reading["badge_position"] == 2
    assert reading["badge_checked"] is True and reading["other_checked"] is True
    assert ':text-is("' + TITLE + '")' in reading["selector"]
    assert "Plantedsecret" not in repr(reading)


async def test_the_reader_still_reads_the_first_shape_and_says_which(browser_page):
    world = _BadgeWorld()
    await browser_page.set_content(world.editor_html(), wait_until="domcontentloaded")
    reading = await profile_editor.read_premium_badge(browser_page)
    assert reading["aimable"] is True, reading["why"]
    assert reading["switch_shape"] == "wrapper"


async def test_switching_the_badge_off_on_the_named_input_moves_only_the_badge(writes_on, browser_page):
    world = _BadgeWorld(named_input=True)
    receipt = await _write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}
    press = receipt["switch_press"]
    assert press["only_the_badge_moved"]["proceed"] is True
    assert press["after_a_fresh_render"] == {"badge_on": False, "other_on": True}
    assert receipt["clicked"]["clicks_made"] == 2


async def test_the_restore_on_the_named_input_switches_it_back(writes_on, browser_page):
    world = _BadgeWorld(named_input=True)
    before = dict(world.store)
    first = await _write(browser_page, world, "off")
    assert first["performed"] is True and world.store[BADGE_ID] is False
    second = await _write(browser_page, world, _restore_value(first))
    assert second["performed"] is True, second["verification"]
    assert world.store == before, "before and after the round trip differ"


async def test_a_named_input_press_that_also_moves_open_profile_is_not_saved(writes_on, browser_page):
    world = _BadgeWorld(named_input=True, press_moves="both")
    receipt = await _write(browser_page, world, "off")
    assert receipt["switch_press"]["only_the_badge_moved"]["code"] == "the_other_switch_moved"
    assert receipt["clicked"]["clicks_made"] == 1
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0
    assert receipt["performed"] is False


async def test_a_row_drawing_the_two_shapes_at_once_is_refused(writes_on, browser_page):
    """One block named on its input, the other still in its wrapper: a row in
    NEITHER recorded shape, so nothing is aimed and nothing is pressed."""
    world = _BadgeWorld(named_input=True, named_other=False)
    message = await _refused(browser_page, world, "off")
    assert "neither recorded" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


async def test_a_named_input_whose_label_computes_no_name_is_refused(writes_on, browser_page):
    """The second shape is a NAMED switch: an aria-label that computes no name
    is not it, and is refused rather than read as either shape."""
    world = _BadgeWorld(named_input=True, empty_label=True)
    message = await _refused(browser_page, world, "off")
    assert "not in a recorded shape" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


# ---------------------------------------------------------------------------
# 6. THE PRESS LANDS ON THE TOGGLE (2026-10-10, the live lane's session 8)
# ---------------------------------------------------------------------------
#
# MEASURED on two read-only loads of his intro editor: the reader aimed the
# badge -- named_input, position 2, both on -- and no press could land. The
# named input draws no box and is not visible, and a trial click on it timed
# out; its parent, the toggle holding the empty label, the input and the
# knob, is drawn (52 x 32) and trial-actionable. Section 5's world now draws
# exactly that, so its writes ran red against the press aimed at the input;
# these were written beside them, first.


async def test_the_press_is_aimed_at_the_drawn_toggle_holding_the_badges_input(browser_page):
    world = _BadgeWorld(named_input=True)
    await browser_page.set_content(world.editor_html(), wait_until="domcontentloaded")
    assert await browser_page.locator("#" + BADGE_ID).is_visible() is False, "the world must hide the input"
    reading = await profile_editor.read_premium_badge(browser_page)
    assert reading["aimable"] is True, reading["why"]
    target = browser_page.locator(reading["selector"])
    assert await target.count() == 1
    assert await target.is_visible(), "the press is aimed at a control that draws no box"
    held = await target.evaluate(
        "el => Array.from(el.querySelectorAll('input[role=\"switch\"]')).map((i) => i.id)"
    )
    assert held == [BADGE_ID], held
    assert reading["press_target_drawn"] is True


async def test_a_toggle_that_draws_no_box_is_refused_before_any_press(writes_on, browser_page):
    """A reader that says aimable must have aimed at a control a click can
    reach: a badge whose toggle draws no box is refused by name, before any
    press -- never a click that times out after the token is spent."""
    world = _BadgeWorld(named_input=True, toggle="hidden")
    message = await _refused(browser_page, world, "off")
    assert "draws no box" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


async def test_a_named_input_that_no_toggle_holds_is_refused(writes_on, browser_page):
    """The press target is the input's own parent, a div holding its empty
    label: drawn any other way, the block is in no recorded shape and nothing
    is aimed."""
    world = _BadgeWorld(named_input=True, toggle="absent")
    message = await _refused(browser_page, world, "off")
    assert "not in a recorded shape" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0
