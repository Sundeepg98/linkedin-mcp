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

AND THEN THE BAR (orchestrator, 2026-09-27 19:52): the exact rule, applied
page-wide, pressed the FOLDER trigger for ``focused`` -- it sits beside the
filter bar, named exactly "Focused". A pill is now found INSIDE the one filter
bar, which is identified by its measured structure (``dom.FILTER_BAR_HOOK``),
and only then matched by exact name. Every page below draws that structure.

EVERY PAGE HERE IS REAL MARKUP IN A REAL HEADLESS CHROMIUM (the ``over``
fixture), so Playwright's own selector and text reading is what is exercised,
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


def _button(label: str, key: str, hook: str = "") -> str:
    """A button that records its own press. ``hook`` is extra attribute text."""
    return (
        '<button type="button" %sonclick="window.__pressed.push(%r)">%s</button>'
        % (hook + " " if hook else "", key, label)
    )


def _pill(label: str, key: str) -> str:
    """A pill as MEASURED: a pressable button carrying the pill hook."""
    return _button(
        label, key,
        'role="button" aria-pressed="false" %s="%s"' % (dom.FILTER_PILL_HOOK, key.upper()),
    )


def _bar(*pills: str) -> str:
    """The filter bar as MEASURED: one radiogroup carrying the bar hook."""
    return '<div role="radiogroup" %s="">%s</div>' % (dom.FILTER_BAR_HOOK, "".join(pills))


#: THE FOLDER, AS MEASURED BESIDE THE BAR: its own dropdown hook, and a trigger
#: named exactly "Focused" carrying the folder hook -- not the pill hook.
_FOLDER = (
    '<div data-test-messaging-inbox-filters__folder-dropdown="">'
    + _button("Focused", "folder", 'data-test-messaging-inbox-filters__folder-pill=""')
    + "</div>"
)


def _page(*parts: str) -> str:
    return _RECORDER + "<main>" + "".join(parts) + "</main>"


async def _activate(page, name: str):
    result = await dom.activate_messaging_filter(page, name)
    pressed = await page.evaluate("window.__pressed")
    return result, pressed


@pytest.fixture(autouse=True)
def _no_settle(monkeypatch):
    """The two-second settle is for a live list redrawing; nothing redraws here."""
    monkeypatch.setattr(dom, "FILTER_SETTLE_MS", 0)


# ---------------------------------------------------------------------------
# THE BAR (orchestrator, 2026-09-27 19:52): a pill is found INSIDE the filter
# bar, identified by structure, and matched by exact name. A control outside
# the bar never matches, even when named exactly the word.
# ---------------------------------------------------------------------------


async def test_the_folder_trigger_named_exactly_focused_is_never_pressed(over):
    """THE DECOY THE ORDER NAMES: the folder dropdown's trigger, beside the bar
    as measured, named exactly "Focused". Nothing in the bar is. Asked for
    ``focused``, nothing is pressed -- the exact-name rule alone pressed it."""
    html = _page(_FOLDER, _bar(_pill("Unread", "unread"), _pill("Jobs", "jobs")))
    result, pressed = await over(html, lambda page: _activate(page, "focused"))

    assert pressed == [], "a control outside the filter bar was pressed: %r" % pressed
    assert result["activated"] is False and result["found"] == 0, result


async def test_a_namesake_outside_the_bar_is_never_pressed(over):
    """A control named exactly a pill's word, OUTSIDE the bar, and no such
    pill in it: refused, nothing pressed."""
    html = _page(_button("Unread", "outside"), _bar(_pill("Jobs", "jobs")))
    result, pressed = await over(html, lambda page: _activate(page, "unread"))

    assert pressed == [], pressed
    assert result["activated"] is False and result["found"] == 0, result


async def test_the_pill_in_the_bar_is_pressed_and_its_namesake_outside_is_not(over):
    """The same word inside the bar and outside it: the pill, and only the
    pill -- where the page-wide exact rule saw two and refused both."""
    html = _page(_FOLDER, _button("Unread", "outside"), _bar(_pill("Unread", "unread")))
    result, pressed = await over(html, lambda page: _activate(page, "unread"))

    assert pressed == ["unread"], pressed
    assert result["activated"] is True and result["pill_label"] == "Unread", result


async def test_a_hooked_pill_outside_any_bar_is_not_a_pill(over):
    """THE HOOK ALONE IS NOT THE BAR: a button wearing the pill hook with no
    bar around it is refused, because the bar is what the page was measured
    to draw."""
    html = _page(_pill("Unread", "stray"))
    result, pressed = await over(html, lambda page: _activate(page, "unread"))

    assert pressed == [], pressed
    assert result["activated"] is False and result["bars"] == 0, result


async def test_two_bars_are_refused_rather_than_guessed_between(over):
    html = _page(_bar(_pill("Unread", "one")), _bar(_pill("Unread", "two")))
    result, pressed = await over(html, lambda page: _activate(page, "unread"))

    assert pressed == [], pressed
    assert result["activated"] is False and result["bars"] == 2, result


async def test_a_decoy_whose_label_contains_the_word_is_not_pressed(over):
    """THE REPRODUCTION. No pill is named exactly ``other``; one pill's name
    CONTAINS it. Nothing is pressed, the refusal says what it saw -- as counts,
    because a label it did not press is page text -- and no label leaks."""
    html = _page(_bar(_pill("Others from " + PLANT, "decoy"), _pill("Unread", "unread")))
    result, pressed = await over(html, lambda page: _activate(page, "other"))

    assert pressed == [], "the decoy was pressed: %r" % pressed
    assert result["activated"] is False, result
    assert result["found"] == 0 and result["pills"] == 2, result
    assert carries_the_plant(result) == [], result


async def test_the_exact_pill_is_pressed_and_the_decoy_beside_it_is_not(over):
    """An exact pill AND a decoy containing its word. The pill is pressed, the
    decoy is not, and the published label is the pill's own -- which by
    construction equals the permitted word."""
    html = _page(_bar(_pill("InMail from " + PLANT, "decoy"), _pill("InMail", "inmail")))
    result, pressed = await over(html, lambda page: _activate(page, "inmail"))

    assert pressed == ["inmail"], pressed
    assert result["activated"] is True, result
    assert result["pill_label"] == "InMail", result
    assert carries_the_plant(result) == [], result


async def test_two_exact_pills_are_refused_rather_than_guessed_between(over):
    html = _page(_bar(_pill("Starred", "one"), _pill(" starred ", "two")))
    result, pressed = await over(html, lambda page: _activate(page, "starred"))

    assert pressed == [], pressed
    assert result["activated"] is False and result["found"] == 2, result


async def test_every_pill_the_composer_draws_is_found_by_its_exact_name(over):
    """THE MEASURED SHAPE STILL WORKS: the tracked compose-list fixture, whose
    bar and pill structure are measured, draws five pills, and each is pressed
    by its exact name.

    ``focused`` AND ``other`` ARE REFUSED: both are the folder dropdown's
    choices, beside the bar, not pills. Until 2026-09-27 ``other`` pressed any
    control containing the word, and then ``focused`` pressed the folder
    trigger, named exactly "Focused" -- the exact rule applied page-wide."""
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
        "focused": (False, 0),
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
