"""The unfollow's CONFIRMATION, and the press that drew nothing (2026-10-10).

MEASURED LIVE, the live lane's session 7: ``linkedin_unfollow_company`` on the
first Page of Manage Pages made ONE press, and the fresh reload read the row
still ``following`` -- ``performed`` false. Two causes fit, and nothing had
measured either: LinkedIn drew a confirmation that nothing pressed, or the
press landed on a control that was not yet ready. ``writes._unfollow_confirm_gate``
now reads what the press drew, before anything navigates, and presses a
confirmation's own confirm control -- through the same click call site --
only when exactly one dialog is drawn and exactly one button in it is named,
exactly, LinkedIn's word for the inverse action.

WRITTEN FIRST AND RUN RED against the write path as it stood: the first test
below read ``performed`` False with one press made.

THE WORLD IS INVENTED around the tracked Manage Pages capture: a click on any
row's inverse-action control draws a confirmation (or, in one world, takes
effect in place), and the reload serves the row gone -- LinkedIn's stated total
down by one -- only if the confirmation's Unfollow was pressed. NOTHING HERE
REACHES LINKEDIN: a local headless Chromium over ``set_content``.
"""
from __future__ import annotations

import json

import pytest

from linkedin_server import writes
from tests.test_writes import (  # noqa: F401 -- fixtures
    FOLLOWED_COMPANY,
    FOLLOWED_COMPANY_NAME,
    _granted,
    _manage_pages,
    browser_page,
    writes_on,
)

#: Fewer polls than the shipped bound, so a world that draws nothing does not
#: spend three seconds per test finding that out. The bound is a liveness
#: bound and decides nothing; the reading at its end does.
FAST_POLLS = 3


def _confirmation(words: tuple[str, ...]) -> str:
    """The dialog a press draws: a Cancel, and one button per word given."""
    buttons = "".join(
        '<button type="button" onclick="window.__confirmed = (this.dataset.w === \'Unfollow\'); '
        "this.closest('[role=dialog]').remove()\" data-w=\"" + word + '">' + word + "</button>"
        for word in words
    )
    return (
        '<div role="dialog" aria-modal="true"><h2>Unfollow this Page?</h2>'
        '<button type="button" onclick="this.closest(\'[role=dialog]\').remove()">Cancel</button>'
        + buttons
        + "</div>"
    )


class _ConfirmWorld:
    """Manage Pages whose unfollow press draws a confirmation (``words``), or,
    with ``in_place``, takes effect at once; ``dialogs`` draws that many. The
    reload serves the row gone, and the total down by one, only once the
    confirmation's Unfollow was pressed -- or the in-place press landed."""

    def __init__(self, *, words: tuple[str, ...] = ("Unfollow",), dialogs: int = 1,
                 in_place: bool = False):
        self.words = words
        self.dialogs = dialogs
        self.in_place = in_place
        self.confirmed = False
        self.gotos: list[str] = []

    def _before(self) -> str:
        dialog = json.dumps(_confirmation(self.words) * self.dialogs)
        act = ("window.__confirmed = true;" if self.in_place
               else "document.body.insertAdjacentHTML('beforeend', " + dialog + ");")
        script = (
            "<script>document.addEventListener('click', function (e) {"
            " const b = e.target.closest('button[aria-label^=\"Click to stop following \"]');"
            " if (!b) { return; } e.preventDefault(); " + act + " }, true);</script>"
        )
        return _manage_pages() + script

    async def goto(self, page, url: str) -> str:
        try:
            self.confirmed = self.confirmed or bool(
                await page.evaluate("() => window.__confirmed === true"))
        except Exception:  # noqa: BLE001 - a fresh page holds nothing
            pass
        self.gotos.append(url)
        html = (_manage_pages(without=FOLLOWED_COMPANY_NAME, total=57) if self.confirmed
                else self._before())
        await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
        return url


async def _unfollow(page, world: _ConfirmWorld) -> dict:
    grant = await _granted(page, "unfollow_company", target=FOLLOWED_COMPANY)
    return await writes.perform(world, page, grant)


@pytest.fixture
def fast_gate(monkeypatch):
    # raising=False so the red run against the unfixed path reaches the
    # behaviour it is about, rather than stopping on a missing constant.
    monkeypatch.setattr(writes, "UNFOLLOW_CONFIRM_POLLS", FAST_POLLS, raising=False)


async def test_an_unfollow_that_draws_a_confirmation_presses_its_confirm(writes_on, browser_page, fast_gate):
    """THE LIVE FAILURE, as this world draws it: the press opens a confirmation.
    The gate reads exactly one dialog and one Unfollow in it, presses it through
    the same call site, and the reload reads the row gone and the total down."""
    world = _ConfirmWorld()
    block = await _unfollow(browser_page, world)
    # THE BEHAVIOUR FIRST, so the red run says what went wrong live.
    assert block["performed"] is True, (block["clicked"], block["verification"])
    assert world.confirmed is True
    assert block["clicked"]["clicks_made"] == 2
    assert block["verification"]["observed_state"] == "not_following"
    gate = block["unfollow_confirm_gate"]
    assert gate is not None and gate["proceed"] is True, gate
    assert gate["dialogs"] == 1 and gate["confirm_controls"] == 1
    assert gate["other_buttons"] == 1 and gate["other_button_names"] == ["W6"]


async def test_a_confirmation_with_two_confirm_controls_is_not_pressed(writes_on, browser_page, fast_gate):
    world = _ConfirmWorld(words=("Unfollow", "Unfollow"))
    block = await _unfollow(browser_page, world)
    gate = block["unfollow_confirm_gate"]
    assert gate["proceed"] is False and gate["code"] == "confirm_not_exactly_one", gate
    assert block["clicked"]["clicks_made"] == 1
    assert world.confirmed is False
    assert block["performed"] is False


async def test_a_confirmation_whose_control_wears_another_word_is_not_pressed(writes_on, browser_page, fast_gate):
    """A guessed word is how a confirm becomes a cancel: only the closed
    vocabulary is pressed, and what WAS drawn is reported, shaped."""
    world = _ConfirmWorld(words=("Stop following",))
    block = await _unfollow(browser_page, world)
    gate = block["unfollow_confirm_gate"]
    assert gate["proceed"] is False and gate["code"] == "confirm_not_exactly_one", gate
    assert gate["confirm_controls"] == 0 and gate["other_buttons"] == 2
    assert set(gate["other_button_names"]) == {"W6", "Stop following"}
    assert block["clicked"]["clicks_made"] == 1 and world.confirmed is False
    assert block["performed"] is False


async def test_two_confirmations_at_once_are_not_pressed(writes_on, browser_page, fast_gate):
    world = _ConfirmWorld(dialogs=2)
    block = await _unfollow(browser_page, world)
    gate = block["unfollow_confirm_gate"]
    assert gate["proceed"] is False and gate["code"] == "dialogs_not_one", gate
    assert block["clicked"]["clicks_made"] == 1 and world.confirmed is False


async def test_a_press_that_takes_effect_in_place_is_unchanged(writes_on, browser_page, fast_gate):
    """No confirmation drawn: nothing further is pressed and the reload decides,
    as before the gate existed."""
    world = _ConfirmWorld(in_place=True)
    block = await _unfollow(browser_page, world)
    gate = block["unfollow_confirm_gate"]
    assert gate["proceed"] is False and gate["code"] == "no_dialog_drawn", gate
    assert gate["polls"] == FAST_POLLS
    assert block["clicked"]["clicks_made"] == 1
    assert block["performed"] is True, block["verification"]


async def test_no_page_name_leaves_through_the_gate(writes_on, browser_page, fast_gate):
    """The confirmation's heading and a planted button name do not reach the
    receipt: only closed words, counts and shapes do."""
    world = _ConfirmWorld(words=("Plantedsecret",))
    block = await _unfollow(browser_page, world)
    text = json.dumps(block["unfollow_confirm_gate"])
    assert "Plantedsecret" not in text and "Unfollow this Page" not in text
    assert block["unfollow_confirm_gate"]["other_button_names"] == ["W6", "W13"]
