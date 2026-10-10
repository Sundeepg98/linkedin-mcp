"""An EMPTY original is restored by a CLEAR, end to end -- census row P A8 (2026-10-10).

THE DEFECT, MEASURED LIVE. P A8 ("Additional name") reads EMPTY on his own
profile, and its live proof is "test, then restore": set a harmless value with
``linkedin_update_profile_field``, verify it, put the original back, verify
that. The original is ``""`` and the restore could not be expressed -- the
empty value was refused -- while the first write's receipt printed that very
call under ``to_put_it_back``.

WHAT ``writes.perform`` NOW DOES, driven here through the real preview,
consume and perform over frozen worlds:

* after a VERIFIED write on the FILL path whose prior value it read as
  exactly ``""``, it writes ONE restore record (``field_restore``), and the
  receipt's ``to_put_it_back`` names the clear call with its terms: ONCE,
  within the record's life, in this process only;
* a None prior (unread), or a write that was not stored, records nothing and
  offers no call;
* the clear's preview says CLEAR; at the click the field must still hold
  EXACTLY what this server typed, or nothing is typed; the fill types the
  empty slice of the target; the fill path's wait waits for ``""``; Save is
  pressed only if no other field moved; the fresh render must read ``""``;
  and then -- only then -- the record is spent, so a second clear is refused.

How the record and the admission behave on their own is
``tests/test_an_empty_value_is_admitted_only_as_a_clear.py``.

THE WORLDS.

* ``tests/fixtures/synthetic/intro_editor_switches.html`` -- the intro editor
  built from session 1's capture: one dialog, City, the settings row with its
  two switches, one Save -- with the field P A8 names planted beside City in
  the shape today's capture draws it (section 2 holds that shape to the
  capture), and a notify control read off (condition 1, as every editor world
  in this suite plants it). Values persist ONLY on a Save press. A late-fill
  variant uses ``scripts/_build_intro_editor_late_press_fixture.py``'s own
  ``make_late_press``.
* ``tests/fixtures/live4/editor.html`` -- the tracked skeleton of his editor,
  every text of his an ``x``. Its one optional text field holding ``""`` is
  given LinkedIn's label for P A8, the same notify control is planted, and a
  Save listener persists the field. Sixteen other real controls sit beside it,
  and the fill path's "only the field moved" rule is asked over all of them.

RED FIRST: every test in section 1 failed against the module before
``perform`` was wired (the clear's preview was refused, or no record was
written, or the receipt offered the refused ``value=''`` call); three guards
were then shown failing by one-line mutations of ``writes.py``. The runs are in
the lane's child-C report.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import re

import pytest

from linkedin_server import field_restore, profile_editor, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import consume, preview, spec_for_action
from tests.test_an_empty_value_is_admitted_only_as_a_clear import (  # noqa: F401 -- the autouse fixture
    FIELD,
    TYPED,
    _no_record_survives_a_test,
)
from tests.test_profile_editor_commit import (
    _EDITOR_URL,
    _LANDED_EDITOR,
    _LANDED_PROFILE,
    _PROFILE_HTML,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

REPO = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"
SWITCHES = REPO / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"
LIVE_EDITOR = REPO / "tests" / "fixtures" / "live4" / "editor.html"
LATE_PRESS_BUILDER = REPO / "scripts" / "_build_intro_editor_late_press_fixture.py"

_ACTION = "update_profile_field"
_SPEC = spec_for_action(_ACTION)

#: INVENTED, distinctive so a leak would be visible: his hand edit.
EDITED = "Zzhandedited"
#: Late enough that a read straight after the fill sees nothing; far inside
#: the bound (``profile_editor.PRESS_STATE_POLLS`` x ``PRESS_STATE_POLL_MS``).
LATE_MS = 1200


def _builder():
    spec = importlib.util.spec_from_file_location(
        "_build_intro_editor_late_press_fixture", LATE_PRESS_BUILDER
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD = _builder()


# ---------------------------------------------------------------------------
# The worlds
# ---------------------------------------------------------------------------


_CITY_ROW = '<label for="intro-city">City</label><input id="intro-city" type="text" value="Placeholdertown">'
_SAVE_BUTTON = '<button type="button">Save</button>'
_NOTIFY_OFF = '<label for="np-notify">Notify network</label><input id="np-notify" type="checkbox" role="switch">'


class _IntroWorld:
    """The intro editor fixture with P A8's field planted beside City.

    ``store`` is what LinkedIn has STORED; the dialog renders it, and Save --
    the only thing that stores -- writes both text fields into
    ``window.__saved`` and closes the dialog. ``goto`` collects a save on the
    page it is leaving before rendering the next one, so a dialog nobody saved
    is discarded at the next navigation, as on the site.
    """

    def __init__(self, *, additional: str = "", notify: str = "off",
                 fill_ms: int | None = None, required: bool = False):
        self.store = {FIELD: additional, "City": "Placeholdertown"}
        self.notify = notify
        self.fill_ms = fill_ms
        self.required = required
        self.gotos: list[str] = []
        self.saves = 0

    def editor_html(self) -> str:
        html = SWITCHES.read_text(encoding="ascii")
        assert html.count(_CITY_ROW) == 1 and html.count(_SAVE_BUTTON) == 1, "the fixture moved"
        planted = (
            '<label for="intro-additional">' + FIELD + "</label>"
            '<input id="intro-additional" type="text" value="' + self.store[FIELD] + '"'
            + (" required" if self.required else "") + ">"
            '<label for="intro-city">City</label>'
            '<input id="intro-city" type="text" value="' + self.store["City"] + '">'
        )
        notify = _NOTIFY_OFF.replace('role="switch">', 'role="switch" checked>') if self.notify == "on" else _NOTIFY_OFF
        handler = (
            "window.__saved = JSON.stringify({'" + FIELD + "': "
            "document.getElementById('intro-additional').value, "
            "'City': document.getElementById('intro-city').value}); "
            "this.closest('dialog').remove()"
        )
        html = html.replace(_CITY_ROW, planted, 1)
        html = html.replace(_SAVE_BUTTON, notify + '<button type="button" onclick="' + handler + '">Save</button>', 1)
        if self.fill_ms is not None:
            html = BUILD.make_late_press(html, None, None, self.fill_ms)
        return html

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
            raise AssertionError("the write asked for " + repr(url) + ", which this world does not serve")
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return landed


#: An optional text input holding the empty string: ``type="text"``,
#: ``value=""`` and no ``required``, as today's capture draws P A8's row.
_OPTIONAL_EMPTY_TEXT = re.compile(r'<input(?![^>]*\brequired\b)[^>]*\btype="text"[^>]*\bvalue=""[^>]*>')


def _live_field_id(html: str) -> str:
    """The dom id of today's capture's ONE optional empty text input."""
    found = _OPTIONAL_EMPTY_TEXT.findall(html)
    assert len(found) == 1, len(found)
    return re.search(r'\bid="([^"]+)"', found[0]).group(1)


class _LiveWorld(_IntroWorld):
    """The tracked skeleton of his editor, its one optional empty text field
    given LinkedIn's label for P A8, a notify control read off planted beside
    it, and a Save listener that persists that field and closes the dialog."""

    def editor_html(self) -> str:
        html = LIVE_EDITOR.read_text(encoding="ascii")
        dom_id = _live_field_id(html)
        html, labels = re.subn(
            r'(<label[^>]*\bfor="' + re.escape(dom_id) + r'"[^>]*>\s*<div[^>]*>\s*)x(\s*</div>\s*</label>)',
            lambda m: m.group(1) + FIELD + m.group(2), html,
        )
        assert labels == 1, labels
        html, inputs = re.subn(
            r'(<input[^>]*\bid="' + re.escape(dom_id) + r'"[^>]*\bvalue=")("[^>]*>)',
            lambda m: m.group(1) + self.store[FIELD] + m.group(2) + _NOTIFY_OFF, html,
        )
        assert inputs == 1, inputs
        listener = (
            "<script>document.addEventListener('click', function (e) {"
            " var b = e.target && e.target.closest ? e.target.closest('button') : null;"
            " if (!b || (b.textContent || '').trim() !== 'Save') { return; }"
            " window.__saved = JSON.stringify({'" + FIELD + "': document.getElementById('" + dom_id + "').value});"
            " var d = b.closest('dialog'); if (d) { d.remove(); } }, true);</script>"
        )
        assert html.count("</body>") == 1
        return html.replace("</body>", listener + "</body>", 1)


async def _preview(page, world, value: str, field: str = FIELD) -> dict:
    return await preview(_SPEC, target={"field": field, "value": value}, navigator=world, page=page)


async def _write(page, world, value: str, field: str = FIELD) -> dict:
    """The real two calls -- preview (mints), consume (redeems), perform --
    then the next navigation a following tool call would make, which persists
    a save that happened and discards a dialog nobody saved."""
    target = {"field": field, "value": value}
    block = await _preview(page, world, value, field)
    grant = consume(block["to_confirm"], action=_ACTION, target=target)
    receipt = await writes.perform(world, page, grant)
    await world.goto(page, writes.PROFILE_URL)
    return receipt


def _call_of(receipt: dict) -> tuple[str, str, str]:
    """``to_put_it_back`` parsed: (field, value, the terms after the ``#``)."""
    call, _, terms = receipt["restore"]["to_put_it_back"].partition("#")
    node = ast.parse(call.strip(), mode="eval").body
    assert isinstance(node, ast.Call) and node.func.id == "linkedin_update_profile_field"
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in node.keywords}
    return kwargs["field"], kwargs["value"], terms


# ---------------------------------------------------------------------------
# 0. ONE place records, and the same place spends
# ---------------------------------------------------------------------------


def _callers(source: str, name: str) -> set[str]:
    """Every function in ``source`` calling ``<anything>.name(...)`` or
    ``name(...)``, attributed to the INNERMOST enclosing function."""
    found: set[str] = set()
    for func in ast.walk(ast.parse(source)):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stack = list(func.body)
        while stack:
            node = stack.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(node, ast.Call):
                callee = node.func
                called = callee.attr if isinstance(callee, ast.Attribute) else getattr(callee, "id", None)
                if called == name:
                    found.add(func.name)
            stack.extend(ast.iter_child_nodes(node))
    return found


@pytest.mark.parametrize("name", ["record_empty_prior", "spend"])
def test_writes_perform_is_the_one_place_that_records_or_spends(name):
    """RED before ``perform`` was wired: ``set()``."""
    sites = {
        (path.name, caller)
        for path in sorted(PACKAGE.glob("*.py"))
        for caller in _callers(path.read_text(encoding="utf-8"), name)
    }
    assert sites == {("writes.py", "perform")}, sites


def test_that_walk_would_notice_a_second_caller():
    """The control, at the shape it exists to reject."""
    smuggled = (
        "async def perform(g):\n"
        "    field_restore.record_empty_prior('a', 'b')\n"
        "\n"
        "def helpful_shortcut():\n"
        "    def inner():\n"
        "        record_empty_prior('a', 'b')\n"
    )
    assert _callers(smuggled, "record_empty_prior") == {"perform", "inner"}


# ---------------------------------------------------------------------------
# 1. End to end, over the intro editor fixture
# ---------------------------------------------------------------------------


async def test_a_write_over_an_empty_original_records_one_clear(writes_on, browser_page):
    """RED before the build: nothing was recorded, and ``to_put_it_back``
    printed ``value=''`` -- a call the preview refused."""
    world = _IntroWorld()
    receipt = await _write(browser_page, world, TYPED)
    assert receipt["performed"] is True, receipt["verification"]
    assert world.store[FIELD] == TYPED
    restore = receipt["restore"]
    assert restore["previous_value"] == "" and "before the write" in restore["how_it_was_read"]
    record = field_restore.live_record(FIELD)
    assert record is not None and record.typed == TYPED and record.used is False
    field, value, terms = _call_of(receipt)
    assert (field, value) == (FIELD, "")
    assert "ONCE" in terms and "30 minutes" in terms and "this process only" in terms, terms
    assert restore["clear"]["recorded"] is True and restore["clear"]["within_seconds"] == 1800


async def test_the_clear_says_so_restores_the_empty_original_and_is_spent(writes_on, browser_page):
    world = _IntroWorld()
    first = await _write(browser_page, world, TYPED)
    assert first["performed"] is True and world.store[FIELD] == TYPED

    block = await _preview(browser_page, world, "")
    assert block["clear"] is True
    assert block["this_is_a_clear"] == field_restore.CLEAR_SENTENCE
    assert block["clear_admissible"]["once"] is True
    assert block["clear_admissible"]["in_this_process_only"] is True
    assert 0 < block["clear_admissible"]["seconds_left"] <= 1800
    assert block["where"]["field"] == FIELD and block["where"]["value"] == ""
    assert block["where"]["target"] == FIELD + writes.TARGET_JOIN
    grant = consume(block["to_confirm"], action=_ACTION, target={"field": FIELD, "value": ""})
    receipt = await writes.perform(world, browser_page, grant)
    await world.goto(browser_page, writes.PROFILE_URL)

    assert world.store[FIELD] == "", "the clear did not leave the field empty"
    assert world.store["City"] == "Placeholdertown"
    assert receipt["performed"] is True and receipt["verified"] is True, receipt["verification"]
    assert receipt["verification"]["observed_state"] == "field_changed"
    assert receipt["target"]["subject"] == FIELD and receipt["target"]["value"] == ""
    assert receipt["clicked"]["clicks_made"] == 1
    press = receipt["field_press"]
    assert press["waited_for_the_requested_state"]["reached"] is True
    assert press["only_the_field_moved"]["proceed"] is True
    assert receipt["restore"]["previous_value"] == TYPED
    assert _call_of(receipt)[:2] == (FIELD, TYPED)
    spent = receipt["restore"]["clear"]
    assert spent["this_write_was_a_clear"] is True and spent["record_spent"] is True, spent
    assert field_restore.live_record(FIELD) is None

    # A SECOND CLEAR IS REFUSED, before any page is loaded.
    loads = list(world.gotos)
    with pytest.raises(WriteAttemptError) as excinfo:
        await _preview(browser_page, world, "")
    assert "already been used" in str(excinfo.value)
    assert world.gotos == loads


async def test_a_late_clear_is_waited_for(writes_on, browser_page):
    """The fill path's wait waits for "" exactly: the field reads the empty
    string only ``LATE_MS`` after the fill, and Save still waits for it."""
    world = _IntroWorld(fill_ms=LATE_MS)
    assert (await _write(browser_page, world, TYPED))["performed"] is True
    receipt = await _write(browser_page, world, "")
    assert world.store[FIELD] == ""
    assert receipt["performed"] is True, receipt["verification"]
    waited = receipt["field_press"]["waited_for_the_requested_state"]
    assert waited["reached"] is True and waited["polls"] > 1, waited


async def test_the_clear_refuses_a_field_changed_since(writes_on, browser_page):
    """THIS SERVER ONLY CLEARS WHAT IT WROTE. He edits the field by hand after
    the write; the clear's preview is admitted (the record lives), and the
    click-time read refuses before anything is typed."""
    world = _IntroWorld()
    assert (await _write(browser_page, world, TYPED))["performed"] is True
    world.store[FIELD] = EDITED
    saves = world.saves
    block = await _preview(browser_page, world, "")
    grant = consume(block["to_confirm"], action=_ACTION, target={"field": FIELD, "value": ""})
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(world, browser_page, grant)
    await world.goto(browser_page, writes.PROFILE_URL)
    message = str(excinfo.value)
    assert "ONLY CLEARS WHAT IT WROTE" in message, message
    assert EDITED not in message and TYPED not in message, message
    assert world.store[FIELD] == EDITED and world.saves == saves
    assert field_restore.live_record(FIELD) is not None, "a refused clear spent the record"


async def test_an_unread_prior_records_nothing(writes_on, browser_page, monkeypatch):
    """None is not empty: a prior that could not be read admits no clear, and
    the receipt offers no call."""
    real = writes._editor_value_of

    async def unread_before(page, field, *, when="after the write"):
        if when == "before the write":
            return None, "it could not be read (planted)."
        return await real(page, field, when=when)

    monkeypatch.setattr(writes, "_editor_value_of", unread_before)
    world = _IntroWorld()
    receipt = await _write(browser_page, world, TYPED)
    assert receipt["performed"] is True and world.store[FIELD] == TYPED
    assert receipt["restore"]["previous_value"] is None
    assert receipt["restore"]["to_put_it_back"] is None
    assert field_restore._RECORDS == {}
    with pytest.raises(WriteAttemptError):
        await _preview(browser_page, world, "")


async def test_a_write_that_was_not_stored_records_nothing(writes_on, browser_page):
    """Notify read ON: Save is not pressed, nothing is stored, and no clear is
    recorded -- the receipt says why and offers no call."""
    world = _IntroWorld(notify="on")
    receipt = await _write(browser_page, world, TYPED)
    assert receipt["performed"] is False and world.store[FIELD] == ""
    assert receipt["restore"]["previous_value"] == ""
    assert receipt["restore"]["to_put_it_back"] is None
    assert receipt["restore"]["clear"]["recorded"] is False
    assert field_restore._RECORDS == {}


async def test_a_required_field_is_still_never_emptied(writes_on, browser_page):
    """The existing EMPTY-INTO-REQUIRED refusal holds on the clear path too."""
    world = _IntroWorld(required=True)
    assert (await _write(browser_page, world, TYPED))["performed"] is True
    block = await _preview(browser_page, world, "")
    grant = consume(block["to_confirm"], action=_ACTION, target={"field": FIELD, "value": ""})
    with pytest.raises(WriteAttemptError) as excinfo:
        await writes.perform(world, browser_page, grant)
    assert "REQUIRED" in str(excinfo.value)
    await world.goto(browser_page, writes.PROFILE_URL)
    assert world.store[FIELD] == TYPED


async def test_the_badge_clear_is_refused_before_any_page_loads(writes_on, browser_page):
    field_restore.record_empty_prior(profile_editor.PREMIUM_BADGE_TITLE, "on")
    world = _IntroWorld()
    with pytest.raises(WriteAttemptError):
        await _preview(browser_page, world, "", field=profile_editor.PREMIUM_BADGE_TITLE)
    assert world.gotos == []


# ---------------------------------------------------------------------------
# 2. On the tracked skeleton of his editor
# ---------------------------------------------------------------------------


async def _fetch_nothing(page) -> None:
    """The skeleton still names its stylesheet, icon and preloads by address
    (every one an ``https://x/...`` placeholder), and Chromium fetches them
    under ``set_content``. The capture is served whole by ``set_content``, so
    THIS PAGE aborts everything it would fetch -- a page route, which outranks
    the suite's network guard (``tests/network_guard.py``) -- and nothing it
    names leaves the machine or is waited on."""

    async def abort(route) -> None:
        await route.abort("blockedbyclient")

    await page.route("**/*", abort)


async def test_todays_capture_draws_one_optional_field_holding_the_empty_string(browser_page):
    """The shape the worlds plant, held to the capture by the shipped readers:
    inside the one dialog holding Save, exactly one text input is named
    through ``label-for``, is not required, and holds exactly ``""``."""
    from linkedin_server import dom

    await _fetch_nothing(browser_page)
    await browser_page.set_content(LIVE_EDITOR.read_text(encoding="ascii"), wait_until="domcontentloaded")
    values = await dom.read_self_owned_editor_values(browser_page)
    labels = await dom.read_self_owned_editor_fields(browser_page)
    assert not values.get("refused") and not labels.get("refused")
    assert len(values["fields"]) == len(labels["fields"])
    empty_optional = [
        index for index, (value, label) in enumerate(zip(values["fields"], labels["fields"]))
        if value["tag"] == "input" and value["type"] == "text"
        and value["name_source"] == "label-for" and value["value"] == ""
        and label["required"] is False
    ]
    assert len(empty_optional) == 1, empty_optional


async def test_the_round_trip_on_todays_capture(writes_on, browser_page):
    """Write, clear, refuse a second clear -- on his editor's own structure,
    with sixteen other controls beside the field and none of them moving."""
    await _fetch_nothing(browser_page)
    world = _LiveWorld()
    first = await _write(browser_page, world, TYPED)
    assert first["performed"] is True, first["verification"]
    assert world.store[FIELD] == TYPED
    assert first["field_press"]["only_the_field_moved"]["proceed"] is True
    assert _call_of(first)[:2] == (FIELD, "")

    clear = await _write(browser_page, world, "")
    assert clear["performed"] is True, clear["verification"]
    assert world.store[FIELD] == ""
    assert clear["field_press"]["only_the_field_moved"]["proceed"] is True
    assert clear["restore"]["clear"]["record_spent"] is True

    with pytest.raises(WriteAttemptError):
        await _preview(browser_page, world, "")
