"""An editor write WAITS, after its press, for the control to read the
requested state -- and Save stays conditional on exactly that field having
moved (the live lane's session 5, 2026-09-28).

THE DEFECT, MEASURED LIVE. P B9's restore pressed the Premium badge switch
once, and the in-dialog read taken straight after the press still showed the
badge off (``the_badge_did_not_move``), so the write -- rightly -- did not
press Save and stored nothing: his badge was left hidden until the ordered
recovery, the same press about two minutes later, flipped it. The
press-then-read is intermittent. The select path (P A21, P A19) read its field
the same way -- straight after ``select_option`` -- and pressed Save without
asking whether the field had moved at all.

THE REPAIR. ``profile_editor.wait_for_state``: a bounded liveness wait
(``PRESS_STATE_POLLS`` polls of ``PRESS_STATE_POLL_MS``) that re-reads until
the reading reaches the requested state, and DECIDES NOTHING. The switch path
waits for the badge to read the requested state and then asks
``badge_moved_alone`` exactly as before; the select path waits for the field to
read the requested option, and Save is pressed only if
``profile_editor.only_the_field_moved`` holds -- every other value-bearing
control reads what it read before the change.

THE WORLD. ``tests/fixtures/synthetic/intro_editor_late_press.html``, built by
``scripts/_build_intro_editor_late_press_fixture.py`` (digest pinned below),
which refuses unless today's capture draws the two selects it is shaped on.
The write worlds are ``test_premium_badge``'s and ``test_profile_editor_commit``'s,
made late by the builder's own ``make_late_press``.

RED FIRST: every test in sections 2 and 3 but the controls failed against the
module before the repair (the lane record carries the run).

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib

import pytest

from linkedin_server import profile_editor, writes
from tests.test_premium_badge import BADGE_ID, OTHER_ID, _BadgeWorld
from tests.test_premium_badge import _write as _badge_write
from tests.test_profile_editor_commit import _CONFIRMABLE, _NEW_CITY, _OLD_CITY, _EditorWorld
from tests.test_profile_editor_commit import _write as _field_write
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parents[1]
BUILDER = REPO / "scripts" / "_build_intro_editor_late_press_fixture.py"
LATE = REPO / "tests" / "fixtures" / "synthetic" / "intro_editor_late_press.html"

#: The committed world's digest, over its TEXT (a CRLF checkout reads the same).
LATE_PRESS_SHA256 = "87ca795a2011231d4727b8d448117a92ff98689d8ac426d19bed37770271b97c"

#: Late enough that a read straight after the press sees nothing; far inside
#: the bound.
LATE_MS = 1200


def _builder():
    spec = importlib.util.spec_from_file_location("_build_intro_editor_late_press_fixture", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = _builder()


class _LateBadgeWorld(_BadgeWorld):
    """The badge world, its switch press landing ``switch_ms`` late."""

    def __init__(self, *, switch_ms: int = LATE_MS, **kwargs):
        super().__init__(**kwargs)
        self.switch_ms = switch_ms

    def editor_html(self) -> str:
        return BUILD.make_late_press(super().editor_html(), self.switch_ms, None)


class _LateSelectWorld(_EditorWorld):
    """The editor world of ``test_profile_editor_commit`` (City typed into,
    Month chosen), its select's change landing ``select_ms`` late -- and, with
    ``moves_city``, a change of Month also rewriting the City field."""

    def __init__(self, *, select_ms: int = LATE_MS, moves_city: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.select_ms = select_ms
        self.moves_city = moves_city

    def editor_html(self) -> str:
        html = BUILD.make_late_press(super().editor_html(), None, self.select_ms)
        if self.moves_city:
            html = html.replace(
                "</body>",
                "<script>document.addEventListener('change', function (e) {"
                " if (e.target && e.target.id === 'e-month') {"
                " document.getElementById('e-city').value = 'Elsewhereville'; } });</script></body>",
                1,
            )
        return html


# ---------------------------------------------------------------------------
# 1. The world: built by its builder, pinned, and late
# ---------------------------------------------------------------------------


def test_the_late_press_world_is_the_builders_output_and_its_digest_is_pinned():
    text = LATE.read_text(encoding="ascii")
    assert text == BUILD.build(), "the committed fixture is not the builder's output: re-run the builder"
    assert hashlib.sha256(text.encode("ascii")).hexdigest() == LATE_PRESS_SHA256


def test_the_builders_badge_title_is_the_packages():
    assert BUILD.BADGE_TITLE == profile_editor.PREMIUM_BADGE_TITLE


def test_the_builder_refuses_a_capture_without_the_two_selects():
    """The precondition can fail: a page drawing one select, or selects that do
    not open on an unset option, is refused."""
    with pytest.raises(ValueError):
        BUILD.check_today('<select><option value="">u</option><option value="x">x</option></select>'
                          '<input role="switch"><input role="switch">')
    shaped = "".join('<select>' + "".join('<option value="x">x</option>' for _ in range(n)) + "</select>"
                     for n in (5, 2))
    with pytest.raises(ValueError):
        BUILD.check_today(shaped + '<input role="switch"><input role="switch">')
    BUILD.check_today(BUILD._selects_html() + '<input role="switch"><input role="switch">')


async def test_the_late_press_world_answers_late(browser_page):
    await browser_page.set_content(LATE.read_text(encoding="ascii"), wait_until="domcontentloaded")
    badge = await profile_editor.read_premium_badge(browser_page)
    assert badge["aimable"] is True, badge
    await browser_page.click(badge["selector"])
    at_once = await profile_editor.read_premium_badge(browser_page)
    assert at_once["badge_checked"] is badge["badge_checked"], "a late world that flips at once tests nothing"
    await browser_page.wait_for_timeout(BUILD.DEFAULT_SWITCH_MS + 600)
    later = await profile_editor.read_premium_badge(browser_page)
    assert later["badge_checked"] is (not badge["badge_checked"])
    await browser_page.select_option("#intro-pronouns", label="Option B")
    at_once = await browser_page.eval_on_selector("#intro-pronouns", "s => s.selectedIndex")
    assert at_once == 0, "a late select that applies at once tests nothing"
    await browser_page.wait_for_timeout(BUILD.DEFAULT_SELECT_MS + 600)
    assert await browser_page.eval_on_selector("#intro-pronouns", "s => s.selectedIndex") == 2


# ---------------------------------------------------------------------------
# 2. The write waits -- the switch in both directions, the select
# ---------------------------------------------------------------------------


async def test_a_late_switch_is_waited_for_off(writes_on, browser_page):
    """RED before the repair: the_badge_did_not_move, no Save, performed false
    -- today's live failure, the other way round."""
    world = _LateBadgeWorld()
    receipt = await _badge_write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["switch_press"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}
    assert receipt["switch_press"]["waited_for_the_requested_state"]["reached"] is True


async def test_a_late_switch_is_waited_for_on(writes_on, browser_page):
    """RED before the repair: today's live failure exactly -- off -> on, the
    switch flipping after the read."""
    world = _LateBadgeWorld(badge=False)
    receipt = await _badge_write(browser_page, world, "on")
    assert receipt["performed"] is True, receipt["switch_press"]
    assert world.store == {OTHER_ID: True, BADGE_ID: True}


async def test_a_late_select_is_waited_for_and_saved(writes_on, browser_page):
    """RED before the repair: Save pressed while the select still read the old
    option -- the store unchanged, performed false."""
    world = _LateSelectWorld(**_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "Month", "March")
    assert world.store["Month"] == "March"
    assert receipt["performed"] is True, receipt["verification"]
    press = receipt["field_press"]
    assert press["waited_for_the_requested_state"]["reached"] is True
    assert press["only_the_field_moved"]["proceed"] is True


async def test_a_select_that_moves_another_field_is_not_saved(writes_on, browser_page):
    """RED before the repair: Save was pressed, the City field stored changed
    beside the one asked for. Now: not saved, and the reason is on the receipt."""
    world = _LateSelectWorld(select_ms=0, moves_city=True, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "Month", "March")
    assert world.saves == 0, "Save was pressed over a second field's change"
    assert world.store["Month"] == "January" and world.store["City"] != "Elsewhereville"
    assert receipt["performed"] is False
    assert receipt["field_press"]["only_the_field_moved"]["code"] == "another_field_moved"


# ---------------------------------------------------------------------------
# 3. It decides nothing: a control that never moves still refuses
# ---------------------------------------------------------------------------


async def test_a_switch_that_never_flips_still_refuses(writes_on, browser_page, monkeypatch):
    monkeypatch.setattr(profile_editor, "PRESS_STATE_POLLS", 3)
    world = _LateBadgeWorld(switch_ms=-1)
    receipt = await _badge_write(browser_page, world, "off")
    assert receipt["performed"] is False
    assert receipt["switch_press"]["only_the_badge_moved"]["code"] == "the_badge_did_not_move"
    assert receipt["switch_press"]["waited_for_the_requested_state"] == {"reached": False, "polls": 3}
    assert world.saves == 0


async def test_a_select_that_never_updates_is_not_saved(writes_on, browser_page, monkeypatch):
    monkeypatch.setattr(profile_editor, "PRESS_STATE_POLLS", 3)
    world = _LateSelectWorld(select_ms=-1, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "Month", "March")
    assert world.saves == 0 and world.store["Month"] == "January"
    assert receipt["performed"] is False
    assert receipt["field_press"]["only_the_field_moved"]["code"] == "the_field_did_not_move"


async def test_a_prompt_select_is_saved_at_the_first_poll(writes_on, browser_page):
    """The control: a select that applies at once is saved as it always was,
    the wait reaching the state on its first poll."""
    world = _LateSelectWorld(select_ms=0, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "Month", "March")
    assert receipt["performed"] is True and world.store["Month"] == "March"
    assert receipt["field_press"]["waited_for_the_requested_state"]["polls"] <= 2


def test_only_the_field_moved_holds_its_own_rules():
    def reading(**values):
        return {"fields": [{"name": k, "value": v} for k, v in values.items()]}

    before = reading(City="A", Month="January", Button=None)
    ok = profile_editor.only_the_field_moved(before, reading(City="A", Month="March", Button=None),
                                             "Month", "March")
    assert ok["proceed"] is True
    assert profile_editor.only_the_field_moved(before, reading(City="B", Month="March"), "Month",
                                               "March")["code"] == "another_field_moved"
    assert profile_editor.only_the_field_moved(before, reading(City="A", Month="January"), "Month",
                                               "March")["code"] == "the_field_did_not_move"
    assert profile_editor.only_the_field_moved({"refused": "no_anchor"}, before, "Month",
                                               "March")["code"] == "unreadable"
    assert profile_editor.only_the_field_moved(before, {"fields": []}, "Month",
                                               "March")["code"] == "not_one_field"


# ---------------------------------------------------------------------------
# 4. THE FILL PATH (the orchestrator's follow-up of 21:57): the same rule
# ---------------------------------------------------------------------------


class _LateFillWorld(_EditorWorld):
    """The editor world, its City input's typed value landing ``fill_ms`` late
    -- and, with ``moves_month``, typing into City also changing Month."""

    def __init__(self, *, fill_ms: int = LATE_MS, moves_month: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.fill_ms = fill_ms
        self.moves_month = moves_month

    def editor_html(self) -> str:
        html = BUILD.make_late_press(super().editor_html(), None, None, self.fill_ms)
        if self.moves_month:
            html = html.replace(
                "</body>",
                "<script>document.addEventListener('input', function (e) {"
                " if (e.target && e.target.id === 'e-city') {"
                " document.getElementById('e-month').selectedIndex = 2; } });</script></body>",
                1,
            )
        return html


async def test_a_late_fill_is_waited_for_and_saved(writes_on, browser_page):
    """RED before the follow-up: Save pressed while the input still held the
    old value -- the store unchanged, performed false."""
    world = _LateFillWorld(**_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert world.store["City"] == _NEW_CITY
    assert receipt["performed"] is True, receipt["verification"]
    press = receipt["field_press"]
    assert press["waited_for_the_requested_state"]["reached"] is True
    assert press["only_the_field_moved"]["proceed"] is True


async def test_a_fill_that_moves_another_field_is_not_saved(writes_on, browser_page):
    """RED before the follow-up: Save was pressed and Month was stored changed
    beside the City asked for. Now: nothing pressed, nothing stored."""
    world = _LateFillWorld(fill_ms=0, moves_month=True, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert world.saves == 0, "Save was pressed over a second field's change"
    assert world.store == {"City": _OLD_CITY, "Month": "January"}
    assert receipt["performed"] is False
    assert receipt["field_press"]["only_the_field_moved"]["code"] == "another_field_moved"


async def test_a_fill_that_never_lands_is_not_saved(writes_on, browser_page, monkeypatch):
    monkeypatch.setattr(profile_editor, "PRESS_STATE_POLLS", 3)
    world = _LateFillWorld(fill_ms=-1, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert world.saves == 0 and world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False
    assert receipt["field_press"]["only_the_field_moved"]["code"] == "the_field_did_not_move"


async def test_a_prompt_fill_is_saved_at_the_first_poll(writes_on, browser_page):
    """The control: a fill that lands at once is saved as it always was."""
    world = _LateFillWorld(fill_ms=0, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert receipt["performed"] is True and world.store["City"] == _NEW_CITY
    assert receipt["field_press"]["waited_for_the_requested_state"]["polls"] <= 2
