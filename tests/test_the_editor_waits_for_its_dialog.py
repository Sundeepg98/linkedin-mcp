"""The intro editor's dialog is WAITED FOR before an editor write reads it,
and an autocomplete field is refused rather than typed into (the live lane's
session 4, 2026-09-28).

THE DEFECT, MEASURED LIVE. P B9's test write loaded his intro editor and its
gate read the dialog the moment the address loaded: ``write_attempt_blocked``,
``0_editor_not_found`` -- the dialog holding the one Save control was not
found exactly once; nothing was pressed. A read that waited 3 s found the
badge aimable, and another load found the dialog already drawn when the
navigation returned: an intermittent race. The fresh-render VERIFICATION
reads the same way, so a clean save could come back ``unknown``.

THE REPAIR. ``profile_editor.wait_for_editor_dialog``: a bounded liveness
wait -- ``EDITOR_DIALOG_POLLS`` polls of ``EDITOR_DIALOG_POLL_MS`` -- for
exactly one dialog holding the one Save control. ``writes.perform`` takes it
after the editor's landing and before the gate reads the control, and the
verification takes it after its fresh load and before it reads the value. It
DECIDES NOTHING: a dialog never drawn, or drawn twice, refuses exactly as it
did before the wait existed.

THE AUTOCOMPLETE REFUSAL. His editor draws Country/Region, City and Industry
as inputs carrying ``aria-autocomplete`` (measured live in the same session):
LinkedIn stores the entry picked from its list, and this write types text. So
an input carrying ``aria-autocomplete`` (other than ``none``), a combobox role
or a ``list`` attribute is refused before anything is typed.

THE WORLD. ``tests/fixtures/synthetic/intro_editor_late.html`` is built by
``scripts/_build_intro_editor_late_fixture.py`` -- the switch fixture's
structure, its one dialog held in a template and drawn by the page's own
script after ``data-late-ms`` -- and its digest is pinned below. The builder
refuses unless today's capture draws exactly one dialog holding Save. The
worlds reuse the badge and editor worlds of ``test_premium_badge`` and
``test_profile_editor_commit``, made late by the builder's own ``make_late``.

RED FIRST: every test in sections 2 and 3 but the controls failed against
the module before the repair (the lane record carries the run).

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib

import pytest

from linkedin_server import profile_editor, writes
from linkedin_server.errors import WriteAttemptError
from tests.test_premium_badge import BADGE_ID, OTHER_ID, _BadgeWorld
from tests.test_premium_badge import _refused as _badge_refused
from tests.test_premium_badge import _write as _badge_write
from tests.test_profile_editor_commit import _CONFIRMABLE, _NEW_CITY, _OLD_CITY, _EditorWorld
from tests.test_profile_editor_commit import _write as _field_write
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parents[1]
BUILDER = REPO / "scripts" / "_build_intro_editor_late_fixture.py"
LATE = REPO / "tests" / "fixtures" / "synthetic" / "intro_editor_late.html"

#: The committed late world's digest. Rebuild with the builder, never by hand.
LATE_SHA256 = "bc2398495fda1181144117b2323188006918c918e2cb08e397a4b31911b3d2b6"

#: Late enough that a read at the landing sees nothing; far inside the bound.
LATE_MS = 1500


def _builder():
    spec = importlib.util.spec_from_file_location("_build_intro_editor_late_fixture", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = _builder()
_DIALOG = profile_editor._EDITOR_DIALOG
_SAVE = profile_editor._SAVE_CONTROL


class _LateBadgeWorld(_BadgeWorld):
    """The badge world, its editor's dialog drawn ``late`` ms after each load
    -- or, with ``verify_late``, prompt on the write's load and late on the
    verification's."""

    def __init__(self, *, late: int = LATE_MS, verify_late: int | None = None, **kwargs):
        super().__init__(**kwargs)
        self.late = late
        self.verify_late = verify_late
        self.editor_loads = 0

    def editor_html(self) -> str:
        self.editor_loads += 1
        late = self.late
        if self.verify_late is not None:
            late = 0 if self.editor_loads == 1 else self.verify_late
        return BUILD.make_late(super().editor_html(), late)


class _LateFieldWorld(_EditorWorld):
    """The editor world of ``test_profile_editor_commit`` (City typed into,
    Month chosen, a planted notify control read off), drawn late."""

    def __init__(self, *, late: int = LATE_MS, verify_late: int | None = None, **kwargs):
        super().__init__(**kwargs)
        self.late = late
        self.verify_late = verify_late
        self.editor_loads = 0

    def editor_html(self) -> str:
        self.editor_loads += 1
        late = self.late
        if self.verify_late is not None:
            late = 0 if self.editor_loads == 1 else self.verify_late
        return BUILD.make_late(super().editor_html(), late)


class _MarkedFieldWorld(_EditorWorld):
    """The editor world with its City input carrying one autocomplete mark."""

    def __init__(self, *, mark: str, **kwargs):
        super().__init__(**kwargs)
        self.mark = mark

    def editor_html(self) -> str:
        html = super().editor_html()
        return html.replace('<input id="e-city" type="text"', '<input id="e-city" type="text" ' + self.mark, 1)


# ---------------------------------------------------------------------------
# 1. The world: built by its builder, pinned, and late
# ---------------------------------------------------------------------------


def test_the_late_world_is_the_builders_output_and_its_digest_is_pinned():
    text = LATE.read_bytes().decode("ascii")
    assert text == BUILD.build(), "the committed fixture is not the builder's output: re-run the builder"
    assert hashlib.sha256(text.encode("ascii")).hexdigest() == LATE_SHA256


def test_the_builder_refuses_a_page_whose_editor_is_not_one_dialog_holding_save():
    """The precondition can fail: a page with no editor open draws dialogs,
    none holding Save; a page with two editors is refused by make_late."""
    assert BUILD.dialog_counts("<body><dialog><button>Close</button></dialog></body>") == (1, 0)
    assert BUILD.dialog_counts(LATE.read_text(encoding="ascii").replace("<template", "<div", 1)) == (1, 1)
    with pytest.raises(ValueError):
        BUILD.make_late("<body><dialog>a</dialog><dialog>b</dialog></body>")
    with pytest.raises(ValueError):
        BUILD.make_late("<body><p>no dialog</p></body>")


async def test_the_late_world_draws_no_editor_until_its_script_runs(browser_page):
    await browser_page.set_content(LATE.read_text(encoding="ascii"), wait_until="domcontentloaded")
    dialog = browser_page.locator(_DIALOG, has=browser_page.locator(_SAVE))
    assert await dialog.count() == 0, "a late world that draws its dialog at once tests nothing"
    reading = await profile_editor.wait_for_editor_dialog(browser_page)
    assert reading["drawn"] is True and reading["dialogs"] == 1
    assert reading["polls"] > 1, "the dialog was there before the first poll"


# ---------------------------------------------------------------------------
# 2. The write waits -- the badge's switch path, the field path, the verification
# ---------------------------------------------------------------------------


async def test_a_badge_write_waits_for_a_late_dialog(writes_on, browser_page):
    """RED before the repair: refused, 0_editor_not_found, nothing pressed."""
    world = _LateBadgeWorld()
    receipt = await _badge_write(browser_page, world, "off")
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store == {OTHER_ID: True, BADGE_ID: False}
    assert receipt["editor_dialog_wait"]["drawn"] is True


async def test_a_field_write_waits_for_a_late_dialog(writes_on, browser_page):
    """RED before the repair: the fields reader found no Save anchor, and the
    write refused before typing."""
    world = _LateFieldWorld(**_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store["City"] == _NEW_CITY


async def test_the_verification_waits_for_a_late_fresh_render(writes_on, browser_page):
    """The write's own load draws the dialog at once; the verification's fresh
    load draws it late. RED before the repair: performed 'unknown' over a value
    that WAS stored."""
    world = _LateFieldWorld(verify_late=LATE_MS, **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert world.store["City"] == _NEW_CITY
    assert receipt["performed"] is True, receipt["verification"]
    assert receipt["verification"]["observed_state"] == "field_changed"


async def test_the_badge_verification_waits_too(writes_on, browser_page):
    world = _LateBadgeWorld(verify_late=LATE_MS)
    receipt = await _badge_write(browser_page, world, "off")
    assert world.store[BADGE_ID] is False
    assert receipt["performed"] is True, receipt["verification"]


# ---------------------------------------------------------------------------
# 3. It decides nothing: never drawn, or drawn twice, still refuses
# ---------------------------------------------------------------------------


async def test_a_dialog_never_drawn_still_refuses_and_presses_nothing(writes_on, browser_page, monkeypatch):
    """The control: a dialog that never arrives is refused exactly as before
    -- the wait only bounds how long the gate looks."""
    monkeypatch.setattr(profile_editor, "EDITOR_DIALOG_POLLS", 3)
    world = _LateBadgeWorld(late=-1)
    message = await _badge_refused(browser_page, world, "off")
    assert "was not found exactly once" in message, message
    assert world.store == {OTHER_ID: True, BADGE_ID: True} and world.saves == 0


async def test_two_editors_still_refuse(writes_on, browser_page, monkeypatch):
    monkeypatch.setattr(profile_editor, "EDITOR_DIALOG_POLLS", 3)

    class _Twice(_BadgeWorld):
        def editor_html(self) -> str:
            html = super().editor_html()
            start, end = html.index("<dialog"), html.index("</dialog>") + len("</dialog>")
            return html[:end] + html[start:end] + html[end:]

    world = _Twice()
    message = await _badge_refused(browser_page, world, "off")
    assert "was not found exactly once" in message, message
    assert world.saves == 0


async def test_the_wait_reports_what_it_saw_and_never_raises(browser_page):
    await browser_page.set_content("<body><p>nothing here</p></body>")
    reading = await profile_editor.wait_for_editor_dialog(browser_page, polls=2, poll_ms=10)
    assert reading == {"drawn": False, "polls": 2, "dialogs": 0}

    class _Broken:
        def locator(self, *args, **kwargs):
            raise RuntimeError("a page that cannot be read")

    reading = await profile_editor.wait_for_editor_dialog(_Broken(), polls=2, poll_ms=10)
    assert reading == {"drawn": None, "polls": 1, "dialogs": None}


# ---------------------------------------------------------------------------
# 4. An autocomplete field is refused before anything is typed
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mark", [
    'aria-autocomplete="list"',
    'aria-autocomplete="both"',
    'role="combobox"',
    'list="e-city-options"',
])
async def test_an_autocomplete_input_is_refused_before_typing(writes_on, browser_page, mark):
    """RED before the repair: the write typed into the City input and saved."""
    world = _MarkedFieldWorld(mark=mark, **_CONFIRMABLE)
    target = {"field": "City", "value": _NEW_CITY}
    block = await writes.preview(writes.spec_for_action("update_profile_field"), target=target,
                                 navigator=world, page=browser_page)
    grant = writes.consume(block["to_confirm"], action="update_profile_field",
                           target=writes._target_for(writes.spec_for_action("update_profile_field"), target))
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(world, browser_page, grant)
    assert "AUTOCOMPLETE" in str(excinfo.value), str(excinfo.value)
    await world.goto(browser_page, writes.PROFILE_URL)
    assert world.store["City"] == _OLD_CITY and world.saves == 0


async def test_an_autocomplete_none_input_is_still_written(writes_on, browser_page):
    """The control: aria-autocomplete="none" says there is no list, and the
    plain write goes through as it always did."""
    world = _MarkedFieldWorld(mark='aria-autocomplete="none"', **_CONFIRMABLE)
    receipt = await _field_write(browser_page, world, "City", _NEW_CITY)
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store["City"] == _NEW_CITY
