"""His Learning library's SAVED list passes no act substring, and the press gate refuses every control on it.

Census row ``J 175`` (lane jobs7, 2026-11-27). The orchestrator's check of
14:30 IST: does ``/learning/me/my-library/saved/`` pass any act substring of
the write guard or the press gate ("save" is the one to check)? If it did,
READ-PAST-AN-ACT-SUBSTRING's condition would bind -- the press gate still
refusing every control on the page -- the way lane msg7 measured it for
``/feed/hashtag/``.

MEASURED, on the shipped guards, never a grep:

* THE WRITE GUARD, ``readonly.assert_read_url``: none of its forbidden URL
  substrings is in the address, and none of them holds "save";
* THE PRESS GATE, ``press.check_address``: none of its composer and editor
  markers is in the address;
* ``press.sensitivity_basis`` declares NO basis for the address, so the gate
  refuses every sanctioned shape there before any page contact
  (``no_sensitivity_basis``) -- the condition READ-PAST-AN-ACT-SUBSTRING sets.

SHOWN ABLE TO FAIL: with a planted basis whose marker the address contains
(``/learning/``, matched by containment as ``/feed/`` reached
``/feed/hashtag/``), the basis probe answers and the gate no longer refuses
on a missing basis -- the test below would go red on such an entry.
"""
from __future__ import annotations

import pytest

from linkedin_server import press, readonly

SAVED = "https://www.linkedin.com/learning/me/my-library/saved/"
SPELLINGS = (SAVED, SAVED.rstrip("/"))


def test_the_address_is_admitted_for_reading():
    for url in SPELLINGS:
        assert readonly.is_read_url(url) is True


def test_no_act_substring_of_the_write_guard_is_in_the_address():
    for url in SPELLINGS:
        assert [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url.lower()] == []
    assert [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if "save" in s] == []


def test_no_composer_or_editor_marker_of_the_press_gate_is_in_the_address():
    for url in SPELLINGS:
        assert [m for m in press._COMPOSER_MARKERS if m in url.lower()] == []
        assert press.check_address(url) == {"pressed": False, "admitted": True}


def test_the_press_gate_declares_no_basis_for_the_page():
    for url in SPELLINGS:
        assert press.sensitivity_basis(url) is None
        for shape in press.SANCTIONED_SHAPES:
            assert press.sensitivity_basis(url, shape) is None


@pytest.mark.parametrize("shape", press.SANCTIONED_SHAPES)
def test_every_sanctioned_shape_is_refused_there_before_any_contact(shape):
    verdict = press.evaluate(url=SAVED, shape=shape)
    assert verdict.get("refused") == "no_sensitivity_basis", verdict
    assert verdict.get("pressed") is not True


def test_the_probe_can_fail_a_planted_containment_basis_reaches_the_page(monkeypatch):
    """THE CONTROL: the checks above would see a basis if one reached the page."""
    planted = (("/learning/", {"kind": "sensitive", "counters": ("off_state",)}),)
    monkeypatch.setattr(press, "SENSITIVITY_BASES", planted + tuple(press.SENSITIVITY_BASES))
    assert press.sensitivity_basis(SAVED) is not None
    verdict = press.evaluate(url=SAVED, shape=press.SANCTIONED_SHAPES[0])
    assert verdict.get("refused") != "no_sensitivity_basis", verdict
