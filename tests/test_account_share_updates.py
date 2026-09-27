"""His account-level "Sharing profile edits" setting: read before the change, wired at the seam.

The live lane, 2026-09-27, session-2 preparation item (b). Condition 1 of
SELF-PROFILE-EDITS-NOT-OUTWARD, as amended
(SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED): where the edit dialog draws no
notify control, his account-level "share profile updates with your network"
setting -- LinkedIn's label today, "Sharing profile edits" -- read OFF BEFORE
the edit satisfies it. Lane L7 built the seam
(``profile_editor.ACCOUNT_READINGS``, the ``account_share_updates`` keyword of
``read_save_gate``) and left it unwired; this file is the reader and the
wiring.

THE PAGE IS SYNTHETIC, AND SAYS SO. No capture of the setting's own page
exists: every world below is INVENTED markup in the shapes a settings switch
plausibly takes -- a labelled checkbox switch, an ARIA switch -- and the
refusals it must make are planted beside it. Session 2's plan validates the
reader on the REAL capture, offline and inside the session, before any of the
six edits fires (``_audit/2026-09-27-live-session-2-plan.md``).

THE FOUR THE ORDER NAMED, through the real preview, ``consume`` and
``perform``: OFF passes; ON refuses; unknown refuses; a missing reading
refuses. And the reading is taken BEFORE the change is entered -- before the
editor is even opened, since the setting lives on another page.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import ast
import inspect

import pytest

from linkedin_server import profile_editor, writes
from tests.test_profile_editor_commit import (
    _EDITOR_URL,
    _NEW_CITY,
    _OLD_CITY,
    _EditorWorld,
    _write,
)
from tests.test_writes import browser_page, writes_on  # noqa: F401 -- fixtures

SETTING_URL = profile_editor.ACCOUNT_SETTING_URL
NAME = profile_editor.ACCOUNT_SETTING_NAME


def _page(body: str) -> str:
    return "<!doctype html><html><body><main>" + body + "</main></body></html>"


#: THE WORLDS, each a synthetic settings page. Keyed by what the reader must
#: answer on it.
WORLDS: dict[str, tuple[str, str]] = {
    # A labelled checkbox switch -- the shape the intro editor's own switches
    # take (input[type=checkbox][role=switch]) -- named by its label.
    "labelled_off": (
        "off",
        _page('<label for="s">' + NAME + '</label>'
              '<input id="s" type="checkbox" role="switch">'),
    ),
    "labelled_on": (
        "on",
        _page('<label for="s">' + NAME + '</label>'
              '<input id="s" type="checkbox" role="switch" checked>'),
    ),
    # An ARIA switch whose state is its aria-checked, named by aria-label.
    "aria_off": (
        "off",
        _page('<button type="button" role="switch" aria-checked="false" '
              'aria-label="' + NAME + '"></button>'),
    ),
    "aria_on": (
        "on",
        _page('<button type="button" role="switch" aria-checked="true" '
              'aria-label="' + NAME + '"></button>'),
    ),
    # A plain checkbox (role checkbox), named through aria-labelledby.
    "labelledby_off": (
        "off",
        _page('<span id="t">' + NAME + '</span>'
              '<input type="checkbox" aria-labelledby="t">'),
    ),
    # THE REFUSALS. Each must read 'unknown', never 'off'.
    "no_switch": ("unknown", _page("<h1>Settings</h1><p>" + NAME + "</p>")),
    "unnamed_switch": (
        "unknown",
        _page('<p>' + NAME + '</p><input type="checkbox" role="switch">'),
    ),
    "two_named": (
        "unknown",
        _page('<label for="a">' + NAME + '</label><input id="a" type="checkbox" role="switch">'
              '<label for="b">' + NAME + '</label><input id="b" type="checkbox" role="switch" checked>'),
    ),
    "name_only_contains_it": (
        "unknown",
        _page('<label for="s">' + NAME + ' and more</label>'
              '<input id="s" type="checkbox" role="switch">'),
    ),
    "input_and_aria_disagree": (
        "unknown",
        _page('<input type="checkbox" role="switch" aria-checked="true" '
              'aria-label="' + NAME + '">'),
    ),
    "aria_switch_with_no_state": (
        "unknown",
        _page('<div role="switch" tabindex="0" aria-label="' + NAME + '"></div>'),
    ),
    # A named control that holds no on/off state at all: a button.
    "a_button_of_that_name": (
        "unknown",
        _page('<button type="button">' + NAME + '</button>'),
    ),
}


@pytest.mark.parametrize("world", sorted(WORLDS))
async def test_the_reader_on_every_world(browser_page, world):
    want, html = WORLDS[world]
    await browser_page.set_content(html, wait_until="domcontentloaded")
    reading = await profile_editor.read_account_share_updates(browser_page)
    assert reading["reading"] == want, (world, reading)
    assert reading["reading"] in profile_editor.ACCOUNT_READINGS
    assert reading["error"] is None, reading


async def test_two_controls_of_that_name_refuse_on_the_count_itself(browser_page):
    """AMBIGUITY IS REFUSED WHERE IT IS SEEN, not rescued downstream: the
    reading says how many it found and why that is the stop -- so the first
    check is shown doing the work, and a later count cannot stand in for it."""
    await browser_page.set_content(WORLDS["two_named"][1], wait_until="domcontentloaded")
    reading = await profile_editor.read_account_share_updates(browser_page)
    assert reading["reading"] == "unknown"
    assert reading["named"] == 2, reading
    assert "2 controls" in reading["why"], reading["why"]
    assert reading["input"] is None, "nothing past the count may have been asked"


async def test_the_reader_returns_no_page_text(browser_page):
    """Counts, booleans, constants: a planted name beside the switch never
    reaches the reading, and neither does the setting's own label."""
    planted = "Exampleperson Markersurname"
    await browser_page.set_content(
        _page('<h2>' + planted + '</h2><label for="s">' + NAME + '</label>'
              '<input id="s" type="checkbox" role="switch">'),
        wait_until="domcontentloaded",
    )
    reading = await profile_editor.read_account_share_updates(browser_page)
    assert reading["reading"] == "off"
    flat = repr(reading)
    assert planted not in flat and "Markersurname" not in flat


async def test_a_reader_failure_is_unknown_with_its_type_only():
    class _Raises:
        def get_by_role(self, *_a, **_k):
            raise TimeoutError("a message that could carry page text")

    reading = await profile_editor.read_account_share_updates(_Raises())
    assert reading["reading"] == "unknown"
    assert reading["error"] == "TimeoutError"
    assert "page text" not in repr(reading)


@pytest.mark.parametrize(
    "landed, served",
    [
        (SETTING_URL, True),
        (SETTING_URL + "/", True),
        (SETTING_URL + "?trk=x", True),
        ("https://www.linkedin.com/mypreferences/d/notify-network-for-updates", False),
        ("https://www.linkedin.com/mypreferences/d/categories/profile-visibility", False),
        ("https://www.linkedin.com/mypreferences/d/", False),
        ("https://www.linkedin.com/login", False),
        ("https://example.test/mypreferences/d/settings/notify-network-for-updates", False),
        ("", False),
        (None, False),
    ],
)
def test_served_means_the_page_kept_its_own_path(landed, served):
    """A REDIRECT IS NOT THE PAGE. A category page may draw the same switch, but
    an admitted address is not a served one: landing anywhere else reads
    'unknown' in perform, so the other candidate gets its own admission first."""
    assert profile_editor.served_at_account_setting(landed) is served


def test_the_reader_presses_nothing():
    """READ ONLY, structurally: the reader's body calls no method that acts on
    a page -- counts and role queries only."""
    source = inspect.getsource(profile_editor.read_account_share_updates)
    tree = ast.parse(source.lstrip())
    acting = {
        "click", "dblclick", "press", "fill", "type", "check", "uncheck",
        "set_checked", "tap", "dispatch_event", "evaluate", "select_option",
        "set_input_files", "focus", "hover", "drag_to", "goto",
    }
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert called & acting == set(), called & acting


# ---------------------------------------------------------------------------
# THE WIRING, through the real preview, consume and perform.
# ---------------------------------------------------------------------------


class _AccountWorld(_EditorWorld):
    """Lane L7's editor world, plus his settings page.

    ``account`` is a key of :data:`WORLDS` (the page served at the setting's
    address), ``"refuse"`` (the navigator raises for it -- the reading cannot
    be taken), or ``"redirect"`` (served, but landed on another address).
    """

    def __init__(self, *, account: str, **kwargs):
        super().__init__(**kwargs)
        self.account = account

    async def goto(self, page, url: str) -> str:
        if url != SETTING_URL:
            return await super().goto(page, url)
        self.gotos.append(url)
        if self.account == "refuse":
            raise ConnectionError("synthetic: the settings page did not load")
        if self.account == "redirect":
            await page.set_content(WORLDS["labelled_off"][1], wait_until="domcontentloaded")
            return "https://www.linkedin.com/mypreferences/d/categories/profile-visibility"
        await page.set_content(WORLDS[self.account][1], wait_until="domcontentloaded")
        return SETTING_URL


async def test_off_passes(writes_on, browser_page):
    """THE ONLY BASIS THE INTRO EDITOR CAN HAVE: no notify control in the dialog,
    his account setting read OFF before the edit. Save is pressed and the value
    is stored."""
    world = _AccountWorld(account="labelled_off")
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["proceeded"] is True, gate
    assert gate["condition_1"] == "account_setting_off", gate
    assert gate["notify_network_means"].startswith("CONFIRMED OFF AT THE ACCOUNT")
    assert receipt["account_setting"]["reading"] == "off"
    assert receipt["account_setting"]["served"] is True
    assert world.store["City"] == _NEW_CITY
    assert receipt["performed"] is True


@pytest.mark.parametrize("account", ["labelled_on", "aria_on"])
async def test_on_refuses(writes_on, browser_page, account):
    world = _AccountWorld(account=account)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "5_condition_1_not_established"
    assert "was read ON before the edit" in gate["why"]
    assert receipt["account_setting"]["reading"] == "on"
    assert receipt["clicked"]["clicks_made"] == 0
    assert world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False


@pytest.mark.parametrize("account", ["no_switch", "unnamed_switch", "two_named", "redirect"])
async def test_unknown_refuses(writes_on, browser_page, account):
    world = _AccountWorld(account=account)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "5_condition_1_not_established"
    assert "could not be read before the edit" in gate["why"]
    assert receipt["account_setting"]["reading"] == "unknown"
    assert world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False


async def test_a_missing_reading_refuses(writes_on, browser_page):
    """The settings page cannot be loaded: no reading at all, which is never
    'off'. The editor is still opened -- a dialog control could establish the
    condition on its own -- and here none does, so nothing is saved."""
    world = _AccountWorld(account="refuse")
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    gate = receipt["editor_save_gate"]
    assert gate["refused_condition"] == "5_condition_1_not_established"
    assert "was not read before the edit" in gate["why"]
    assert receipt["account_setting"]["reading"] is None
    assert receipt["account_setting"]["read"] is False
    assert receipt["account_setting"]["error"] == "ConnectionError"
    assert world.store["City"] == _OLD_CITY
    assert receipt["performed"] is False


async def test_the_reading_is_taken_before_the_change_is_entered(writes_on, browser_page):
    """THE AMENDMENT'S WORD: before the edit. The settings page is loaded
    before the editor, so nothing has been typed when it is read."""
    world = _AccountWorld(account="labelled_off")
    await _write(browser_page, world, "City", _NEW_CITY)
    assert SETTING_URL in world.gotos and _EDITOR_URL in world.gotos
    assert world.gotos.index(SETTING_URL) < world.gotos.index(_EDITOR_URL), world.gotos
    assert world.gotos.count(SETTING_URL) == 1, "one reading per write, one load"


async def test_a_dialog_control_still_governs_whatever_the_account_reads(
    writes_on, browser_page
):
    """The reading is an input to the gate, never a verdict of its own: a
    dialog that draws its own notify control is decided by that control."""
    on_but_dialog_off = _AccountWorld(account="labelled_on", notify="off")
    receipt = await _write(browser_page, on_but_dialog_off, "City", _NEW_CITY)
    assert receipt["editor_save_gate"]["condition_1"] == "dialog_control_off"
    assert on_but_dialog_off.store["City"] == _NEW_CITY
    off_but_dialog_on = _AccountWorld(account="labelled_off", notify="on")
    receipt = await _write(browser_page, off_but_dialog_on, "City", _NEW_CITY)
    assert receipt["editor_save_gate"]["refused_condition"] == "4_notify_network_not_off"
    assert off_but_dialog_on.store["City"] == _OLD_CITY


async def test_an_unnamed_switch_still_refuses_with_the_account_off(writes_on, browser_page):
    """Code 6 stands beside an unrecognised unnamed switch, account OFF or not."""
    world = _AccountWorld(account="labelled_off", unnamed_switch=True)
    receipt = await _write(browser_page, world, "City", _NEW_CITY)
    assert receipt["editor_save_gate"]["refused_condition"] == "6_unnamed_switch_unresolved"
    assert world.store["City"] == _OLD_CITY


def test_every_save_gate_call_in_perform_passes_the_reading():
    """THE WIRING, structurally: every ``profile_editor.read_save_gate`` call in
    ``writes.perform`` hands the reading on. One call site that forgot it would
    refuse on 'not read' where the reading said OFF -- or, worse, a future gate
    that treated a missing keyword as anything but 'not read'."""
    tree = ast.parse(inspect.getsource(writes.perform))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "read_save_gate"
    ]
    assert len(calls) >= 4, len(calls)
    for call in calls:
        passed = {kw.arg: kw.value for kw in call.keywords}
        assert "account_share_updates" in passed, ast.unparse(call)
        value = passed["account_share_updates"]
        assert isinstance(value, ast.Name) and value.id == "account_share_updates", (
            ast.unparse(call)
        )


def test_a_write_that_is_not_an_editor_write_reads_no_setting():
    """Only EDITOR_SAVE_ACTIONS pay the load: the reading is condition 1's, and
    condition 1 is the editor's."""
    source = inspect.getsource(writes.perform)
    assert "if spec.action in EDITOR_SAVE_ACTIONS:" in source
    assert writes.EDITOR_SAVE_ACTIONS == frozenset({"update_profile_field"})
