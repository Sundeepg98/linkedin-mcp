"""The intro editor's two unnamed switches, recognised by STRUCTURE (lane L7 follow-up, 2026-09-24).

The ruling ``SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED`` does not count
condition 1 met while the edit dialog draws a switch it cannot NAME, "until a
capture identifies that switch". The live lane's capture of the intro editor
identified its two -- 'Open Profile' and 'Profile Premium Badge' -- by the text
of their section. ``profile_editor.recognise_intro_editor_switches`` ties a
switch the gate sees to that identification WITHOUT reading that text: by its
position under the one element above it the page names (the dialog's
scrolling column, by its test id) and the shape the capture draws around it
(an ARIA ``role=switch`` wrapper, a two-part setting block, one settings row of
exactly two blocks), matched by attribute presence, never by a label. Every
question it asks the page is a ``locator(...).count()``.

The fixture is ``tests/fixtures/synthetic/intro_editor_switches.html``, built
from that capture by ``scripts/_build_intro_editor_switches_fixture.py``:
structure carried over, every text, id and key invented.

What these tests hold:
  * each switch is recognised, in the recorded order, and neither is treated as
    a notify control;
  * a third, still-unnamed switch keeps code 6 -- planted outside the row, and
    planted as a third block inside it;
  * a switch that is not UNNAMED is not recognised even when every attribute
    matches, so recognition can never lift code 6 for switches it did not see;
  * the gate still refuses when condition 1 is not established;
  * the recognition reads no label: the titles moved, blanked, or the wrapper's
    own name changed, the answer does not move.

NOTHING HERE REACHES LINKEDIN. A local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from linkedin_server import profile_editor
from tests.test_writes import browser_page  # noqa: F401 -- fixture

REPO = pathlib.Path(__file__).resolve().parents[1]
FIXTURE = REPO / "tests" / "fixtures" / "synthetic" / "intro_editor_switches.html"
BASE = FIXTURE.read_text(encoding="utf-8")
BUILDER = REPO / "scripts" / "_build_intro_editor_switches_fixture.py"

BOTH = ["open_profile", "profile_premium_badge"]
SAVE_BUTTON = '<button type="button">Save</button>'
COLUMN = '<div data-testid="lazy-column">'
#: Where the row ends: its own closing tag, then the column's, then Save.
ROW_END = "</div></div>\n" + SAVE_BUTTON


def planted_switch(key: str) -> str:
    """A switch in the shape of an ordinary unnamed toggle, NOT the recorded
    one: no setting block, no settings row. Invented."""
    return (
        '<div role="switch" aria-checked="false"><label for="planted-' + key + '"></label>'
        '<input id="planted-' + key + '" type="checkbox" role="switch"></div>'
    )


async def _load(page, html: str) -> None:
    await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)


def _blocks(html: str) -> tuple[str, str, str]:
    """(before the first block, the two blocks as one string, from the row's
    closing tag on)."""
    start = html.index("<div><div><p>Placeholder setting A")
    end = html.index(ROW_END)
    return html[:start], html[start:end], html[end:]


def _row(html: str) -> str:
    """The whole settings row, leading paragraph to closing tag."""
    start = html.index(COLUMN) + len(COLUMN)
    return html[start:html.index(ROW_END) + len("</div>")]


# ---------------------------------------------------------------------------
# 1. Each switch is recognised, and neither is a notify control
# ---------------------------------------------------------------------------


async def test_each_switch_is_recognised_and_neither_is_a_notify_control(browser_page):
    await _load(browser_page, BASE)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["error"] is None
    assert seen["containers"] == 1 and seen["rows"] == 1 and seen["checkables"] == 2
    assert seen["recognised"] == 2 and seen["identities"] == BOTH
    assert seen["checked"] == [True, True]
    gate = await profile_editor.read_save_gate(browser_page)
    assert gate["notify_network"] == "not_drawn"
    assert gate["unnamed_switches"] == 2
    assert gate["recognised_switches"] == BOTH
    assert gate["unresolved_switches"] == 0


async def test_with_his_account_setting_read_off_the_recognised_pair_does_not_block(browser_page):
    """The one case the recognition exists to open: the dialog draws no notify
    control, its only unnamed switches are the two the capture identified,
    and the account-level setting was read OFF -- so condition 1 holds."""
    await _load(browser_page, BASE)
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["proceed"] is True, gate["why"]
    assert gate["condition_1"] == "account_setting_off"
    assert profile_editor.notify_network_note(gate).startswith("CONFIRMED OFF AT THE ACCOUNT")
    assert "capture identified" in profile_editor.notify_network_note(gate)


async def test_the_states_are_read_per_identity_and_a_disagreement_is_none(browser_page):
    """Checked state by identity, from the input AND its wrapper: the second
    switch drawn off reads False; an input and wrapper that disagree read None
    rather than either one's word."""
    off = BASE.replace(
        '<div role="switch" aria-checked="true" tabindex="0" aria-label="Tap to toggle setting">'
        '<div><div><p></p></div><div><span>Placeholder state</span><div>'
        '<label for="intro-switch-2"></label><input role="switch" type="checkbox" checked="" id="intro-switch-2">',
        '<div role="switch" aria-checked="false" tabindex="0" aria-label="Tap to toggle setting">'
        '<div><div><p></p></div><div><span>Placeholder state</span><div>'
        '<label for="intro-switch-2"></label><input role="switch" type="checkbox" id="intro-switch-2">',
    )
    assert off != BASE
    await _load(browser_page, off)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["identities"] == BOTH and seen["checked"] == [True, False]
    torn = BASE.replace('aria-checked="true"', 'aria-checked="false"', 1)
    await _load(browser_page, torn)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["identities"] == BOTH and seen["checked"] == [None, True]


# ---------------------------------------------------------------------------
# 2. A third, still-unnamed switch keeps code 6
# ---------------------------------------------------------------------------


async def test_a_third_unnamed_switch_outside_the_row_keeps_code_6(browser_page):
    await _load(browser_page, BASE.replace(SAVE_BUTTON, planted_switch("a") + SAVE_BUTTON))
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["unnamed_switches"] == 3
    assert gate["recognised_switches"] == BOTH
    assert gate["unresolved_switches"] == 1
    assert gate["proceed"] is False
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"


async def test_a_third_block_inside_the_row_recognises_none(browser_page):
    """A row of three blocks is not the recorded row, so NEITHER original
    switch is recognised any more: all three are unresolved."""
    before, blocks, after = _blocks(BASE)
    second = blocks[blocks.index("<div><div><p>Placeholder setting B"):]
    third = second.replace("intro-switch-2", "intro-switch-3")
    await _load(browser_page, before + blocks + third + after)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["recognised"] == 0 and seen["identities"] == []
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["unnamed_switches"] == 3 and gate["unresolved_switches"] == 3
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"


async def test_a_second_copy_of_the_row_recognises_none(browser_page):
    """Two rows of the recorded shape: which one the capture identified is not
    something structure can say, so neither is recognised."""
    row = _row(BASE)
    copy = row.replace("intro-switch-1", "intro-switch-3").replace("intro-switch-2", "intro-switch-4")
    await _load(browser_page, BASE.replace(COLUMN + row, COLUMN + row + copy))
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["rows"] == 2 and seen["recognised"] == 0
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["unnamed_switches"] == 4 and gate["unresolved_switches"] == 4
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"


async def test_a_switch_outside_the_recorded_shape_is_not_recognised(browser_page):
    """The first wrapper loses its ARIA ``role=switch``: that block no longer
    has the recorded shape, the row no longer holds two such blocks, and
    recognition is all or nothing."""
    html = BASE.replace('<div role="switch" aria-checked="true"', '<div aria-checked="true"', 1)
    await _load(browser_page, html)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["recognised"] == 0
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"
    assert gate["unresolved_switches"] == 2


async def test_the_row_must_sit_under_the_column_the_page_names(browser_page):
    """The anchor is the column's test id. The same row under any other
    parent is not the recorded position, and recognises none."""
    await _load(browser_page, BASE.replace(COLUMN, '<div data-testid="some-other-column">'))
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["rows"] == 0 and seen["recognised"] == 0
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"


async def test_a_row_of_the_same_outline_without_switches_does_not_confuse_it(browser_page):
    """The column draws other rows too (the capture's has ten). One with the
    same outline -- a paragraph and two two-part divs -- but no switch is not
    the settings row and does not make the count ambiguous."""
    decoy = (
        "<div><p>Placeholder other</p>"
        "<div><div><p>Placeholder x</p></div><div><p>Placeholder y</p></div></div>"
        "<div><div><p>Placeholder x</p></div><div><p>Placeholder y</p></div></div></div>"
    )
    await _load(browser_page, BASE.replace(COLUMN, COLUMN + decoy))
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["rows"] == 1 and seen["identities"] == BOTH


async def test_a_switch_the_page_NAMES_elsewhere_is_not_recognised(browser_page):
    """THE CASE THE ACCESSIBLE-NAME HALF EXISTS FOR. Two labels elsewhere in
    the dialog name the row's two inputs, and two ordinary unnamed switches are
    planted outside the row. Every ATTRIBUTE the recognition reads still
    matches -- so a recogniser that asked attributes alone would say "the
    capture's two", the fields reader would count the two PLANTED ones as the
    unnamed switches, and the gate would press Save over two switches nobody
    identified. The row's inputs have names, so they are not the capture's
    unnamed pair, and nothing is recognised."""
    names = (
        '<label for="intro-switch-1">Planted name one</label>'
        '<label for="intro-switch-2">Planted name two</label>'
    )
    html = BASE.replace(SAVE_BUTTON, names + planted_switch("a") + planted_switch("b") + SAVE_BUTTON)
    await _load(browser_page, html)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["rows"] == 1 and seen["recognised"] == 0
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["unnamed_switches"] == 2
    assert gate["recognised_switches"] == [] and gate["unresolved_switches"] == 2
    assert gate["proceed"] is False
    assert gate["refused_condition"] == "6_unnamed_switch_unresolved"


async def test_a_hidden_switch_is_still_recognised(browser_page):
    """The fields reader counts a control whether or not it is drawn visibly,
    so the recognition must too: a checkbox a stylesheet hides (common for a
    styled toggle) is the same switch, and missing it would leave code 6
    standing over a pair the capture identified."""
    html = BASE.replace('type="checkbox" checked=""', 'type="checkbox" checked="" style="display:none"')
    assert html.count('style="display:none"') == 2
    await _load(browser_page, html)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["recognised"] == 2 and seen["identities"] == BOTH
    gate = await profile_editor.read_save_gate(browser_page, account_share_updates="off")
    assert gate["unnamed_switches"] == 2 and gate["proceed"] is True, gate["why"]


# ---------------------------------------------------------------------------
# 3. The gate still refuses when condition 1 is not established
# ---------------------------------------------------------------------------


async def test_the_gate_still_refuses_when_condition_1_is_not_established(browser_page):
    await _load(browser_page, BASE)
    for account in (None, "on", "unknown", "OFF"):
        gate = await profile_editor.read_save_gate(browser_page, account_share_updates=account)
        assert gate["proceed"] is False, account
        assert gate["refused_condition"] == "5_condition_1_not_established", account
        assert gate["recognised_switches"] == BOTH
        assert "NEEDS-OPERATOR" in gate["why"]


# ---------------------------------------------------------------------------
# 4. No label is read
# ---------------------------------------------------------------------------


async def test_the_titles_are_never_read(browser_page):
    """Swap the two blocks' titles, or blank every paragraph: identity follows
    the recorded ORDER, so a recogniser that read the titles would move here
    and this one does not."""
    swapped = (
        BASE.replace("Placeholder setting A", "@@")
        .replace("Placeholder setting B", "Placeholder setting A")
        .replace("@@", "Placeholder setting B")
    )
    blank = re.sub(r"<p>[^<]*</p>", "<p></p>", BASE)
    for html in (swapped, blank):
        await _load(browser_page, html)
        seen = await profile_editor.recognise_intro_editor_switches(browser_page)
        assert seen["identities"] == BOTH


async def test_the_wrapper_name_is_not_read_either(browser_page):
    html = BASE.replace('aria-label="Tap to toggle setting"', 'aria-label="Anything at all"')
    await _load(browser_page, html)
    seen = await profile_editor.recognise_intro_editor_switches(browser_page)
    assert seen["recognised"] == 2 and seen["identities"] == BOTH


# ---------------------------------------------------------------------------
# 5. The verdict's own rule, the reader's failure mode, the shared anchor
# ---------------------------------------------------------------------------


_SAVE = {"name": "Save", "name_source": "text", "tag": "button", "type": None,
         "role": None, "disabled": False, "checked": None}
_UNNAMED = {"name": "", "name_source": "none", "tag": "input", "type": "checkbox",
            "role": "switch", "disabled": False, "checked": True}


def test_recognition_is_all_or_nothing_in_the_verdict():
    fields = {"fields": [_SAVE, dict(_UNNAMED), dict(_UNNAMED)]}
    for reading in (
        None,
        {"identities": ["open_profile"]},
        {"identities": ["open_profile", "open_profile"]},
        {"identities": ["open_profile", "somebody_else"]},
        {"identities": "open_profile profile_premium_badge"},
    ):
        gate = profile_editor.save_gate_verdict(
            fields, account_share_updates="off", recognised_switches=reading
        )
        assert gate["recognised_switches"] == [], reading
        assert gate["refused_condition"] == "6_unnamed_switch_unresolved", reading
    # More recognised than the fields reader counts unnamed: recognise none.
    gate = profile_editor.save_gate_verdict(
        {"fields": [_SAVE, dict(_UNNAMED)]},
        account_share_updates="off",
        recognised_switches={"identities": BOTH},
    )
    assert gate["recognised_switches"] == [] and gate["unresolved_switches"] == 1


class _FailingLocator:
    """Every locator composes; every question to the page raises, quoting a
    planted name as a Playwright message can quote page content."""

    def locator(self, *_args, **_kwargs):
        return self

    def get_by_role(self, *_args, **_kwargs):
        return self

    def and_(self, *_args, **_kwargs):
        return self

    async def count(self):
        raise RuntimeError("Plantedname Plantedsurname")


class _FailingPage(_FailingLocator):
    pass


async def test_a_reader_failure_recognises_nothing_and_says_only_its_type():
    seen = await profile_editor.recognise_intro_editor_switches(_FailingPage())
    assert seen["recognised"] == 0 and seen["identities"] == []
    assert seen["error"] == "RuntimeError"
    assert "Planted" not in repr(seen)


def test_the_dialog_is_found_by_the_press_selectors_own_halves():
    """The recognition scopes to the dialog the press aims in: the two halves
    it composes are exactly :data:`profile_editor.SAVE_SELECTOR`."""
    assert (
        profile_editor._EDITOR_DIALOG + " >> " + profile_editor._SAVE_CONTROL
        == profile_editor.SAVE_SELECTOR
    )


def test_the_builder_signature_holds_on_the_fixture_and_refuses_elsewhere(tmp_path):
    ok = subprocess.run(
        [sys.executable, str(BUILDER), "--check", str(FIXTURE)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert "one settings row, 2 switch blocks" in ok.stdout
    for name, html in (
        ("no_row.html", BASE.replace("<p>Placeholder section</p>", "<span>Placeholder section</span>")),
        ("no_column.html", BASE.replace(COLUMN, '<div data-testid="some-other-column">')),
    ):
        stray = tmp_path / name
        stray.write_text(html, encoding="utf-8")
        refused = subprocess.run(
            [sys.executable, str(BUILDER), "--check", str(stray)],
            capture_output=True, text=True, cwd=REPO,
        )
        assert refused.returncode != 0, name
        assert "NO --" in refused.stdout, name
