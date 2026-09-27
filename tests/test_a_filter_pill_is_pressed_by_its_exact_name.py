"""A messaging filter pill is pressed by its EXACT name, or not at all.

THE ORDER (orchestrator, 2026-09-27, lane G): ``dom.activate_messaging_filter``
aims the filter pill by EXACT name. ``message_filter="other"`` presses only the
pill whose accessible name equals the filter word, and refuses -- saying what
it saw -- when no pill matches exactly.

THE DEFECT, found by lane G's cold verification the same day
(``scratchpad/lane-g/cold2/r03b_filter_click_label.py``): the activator located
the pill by ``get_by_role("button", name=word, exact=False)``, a
case-insensitive SUBSTRING match. The composer's list draws no "Other" pill --
"Focused" and "Other" are a folder dropdown, not pills -- so asking for
``other`` pressed whichever button's name merely CONTAINED the word, and
published that control's whole label as ``pill_label``. A sanctioned click on a
read path, landing on a control nobody named.

EVERY PAGE HERE IS REAL MARKUP IN A REAL HEADLESS CHROMIUM (the ``over``
fixture), so Playwright's own accessible-name matching is what is exercised,
not a double's idea of it. Each button records its own press in
``window.__pressed``, so "was it pressed" is read off the page rather than off
the activator's report. The decoys carry ``tests.plantedpage.PLANT``, so a
label that leaks into the result is found by the same hunt every page-string
guard uses.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom
from tests.plantedpage import PLANT, carries_the_plant
from tests.test_apply_modal_fixture import over  # noqa: F401 -- fixture

_RECORDER = "<script>window.__pressed = [];</script>"


def _button(label: str, key: str) -> str:
    return (
        '<button type="button" onclick="window.__pressed.push(%r)">%s</button>'
        % (key, label)
    )


async def _activate(page, name: str):
    result = await dom.activate_messaging_filter(page, name)
    pressed = await page.evaluate("window.__pressed")
    return result, pressed


@pytest.fixture(autouse=True)
def _no_settle(monkeypatch):
    """The two-second settle is for a live list redrawing; nothing redraws here."""
    monkeypatch.setattr(dom, "FILTER_SETTLE_MS", 0)


async def test_a_decoy_whose_label_contains_the_word_is_not_pressed(over):
    """THE REPRODUCTION. No pill is named exactly ``other``; one control's name
    CONTAINS it. Nothing is pressed, the refusal says what it saw -- as counts,
    because a label it did not press is page text -- and no label leaks."""
    html = _RECORDER + _button("Others from " + PLANT, "decoy") + _button("Unread", "unread")
    result, pressed = await over(html, lambda page: _activate(page, "other"))

    assert pressed == [], "the decoy was pressed: %r" % pressed
    assert result["activated"] is False, result
    assert result["found"] == 0 and result["containing"] == 1, result
    assert carries_the_plant(result) == [], result


async def test_the_exact_pill_is_pressed_and_the_decoy_beside_it_is_not(over):
    """An exact pill AND a decoy containing its word. The pill is pressed, the
    decoy is not, and the published label is the pill's own -- which by
    construction equals the permitted word."""
    html = (
        _RECORDER
        + _button("InMail from " + PLANT, "decoy")
        + _button("InMail", "inmail")
    )
    result, pressed = await over(html, lambda page: _activate(page, "inmail"))

    assert pressed == ["inmail"], pressed
    assert result["activated"] is True, result
    assert result["pill_label"] == "InMail", result
    assert carries_the_plant(result) == [], result


async def test_two_exact_pills_are_refused_rather_than_guessed_between(over):
    html = _RECORDER + _button("Starred", "one") + _button(" starred ", "two")
    result, pressed = await over(html, lambda page: _activate(page, "starred"))

    assert pressed == [], pressed
    assert result["activated"] is False and result["found"] == 2, result


async def test_every_pill_the_composer_draws_is_found_by_its_exact_name(over):
    """THE MEASURED SHAPE STILL WORKS: the tracked compose-list fixture, whose
    pill structure is measured, draws five pills, and each is pressed by its
    exact name. ``other`` is not a pill there -- it lives in the folder menu --
    and refuses, where substring matching pressed any control containing it.

    ``focused`` IS PRESSED, AND THAT IS PINNED AS MEASURED, NOT ENDORSED: the
    folder dropdown's trigger is named exactly "Focused", so the exact rule
    finds it. Pressing it opens the folder menu rather than filtering a view;
    it sends nothing, as the substring rule's press did before. Whether the
    activator should require a pill's own markers (``aria-pressed``, the
    filter-pill hook) is its owner's call, and this line moves when it is."""
    from pathlib import Path

    fixture = (
        Path(__file__).parent / "fixtures" / "synthetic" / "messaging_compose_list.html"
    ).read_text(encoding="ascii")

    async def every(page):
        verdicts = {}
        for name in dom.MESSAGING_FILTERS:
            result = await dom.activate_messaging_filter(page, name)
            verdicts[name] = (result["activated"], result.get("found"))
        return verdicts

    verdicts = await over(fixture, every)
    assert verdicts == {
        "focused": (True, None),
        "other": (False, 0),
        "unread": (True, None),
        "jobs": (True, None),
        "connections": (True, None),
        "inmail": (True, None),
        "starred": (True, None),
    }, verdicts


@pytest.mark.parametrize(
    "label, expected",
    [
        ("InMail", True),
        ("inmail", True),
        ("  InMail  ", True),
        ("InMail messages", False),
        ("Filter by InMail", False),
        ("InMail 1 new", False),
        ("", False),
    ],
)
def test_the_shared_rule_is_exact_equality_case_and_space_folded(label, expected):
    """ONE PREDICATE, BOTH PATHS: the enumerator and the activator still call
    ``dom.filter_name_matches``, so they cannot disagree -- and it is now exact."""
    assert dom.filter_name_matches(label, "inmail") is expected
