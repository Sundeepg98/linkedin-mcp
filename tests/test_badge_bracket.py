"""The pending-invitation badge around the three ``/mynetwork/`` lists: the verdict, and the tools that obey it.

``linkedin_server/badge_bracket.py`` judges two readings of the badge -- off the
feed before, off the list's own navigation after -- and the three tools that
open ``/mynetwork/`` pages (``linkedin_received_invitations``,
``linkedin_sent_invitations``, ``linkedin_my_following_list``) hand their
readings to it. Each outcome is planted here and each verdict checked:

* held at zero: the list comes back, ``proven`` False;
* held above zero: the list comes back, ``proven`` True;
* MOVED: the sent tab and the following list WITHHOLD what they read; the
  received tab returns it beside the measured cost;
* unreadable AFTER: the same split;
* unreadable BEFORE: the tool opens nothing but the feed.

AND THE LABEL NEVER LEAVES: the badge reader's label, which its own docstring
says to read as name-bearing, is reduced to a state and an integer.

NOTHING HERE REACHES LINKEDIN: the tools run over a browser double that
loads nothing, with the badge readings handed in.
"""
from __future__ import annotations

from typing import Any

import pytest

from linkedin_server import badge_bracket, dom, server
from tests.plantedpage import PLANT

LIST = {"surface": "x", "readable": True, "rows": ["a record"], "scope": "s"}


def _reading(pending: int) -> dict[str, Any]:
    return {"state": "read", "pending": pending, "why": "w",
            "saw": {"shaped_label": f"{PLANT}, {pending} new notifications"}}


UNREADABLE = {"state": "unreadable", "pending": None, "why": "w", "saw": {"shaped_label": PLANT}}


@pytest.mark.parametrize("surface", sorted(badge_bracket.WITHHOLDS_ON_MOVE))
def test_a_badge_that_held_at_zero_returns_the_list_and_proves_nothing(surface):
    out = badge_bracket.judge(surface, dict(LIST), _reading(0), _reading(0))
    assert out["rows"] == ["a record"] and out["readable"] is True
    assert out["cost"] == {"outcome": "held", "proven": False}
    assert out["badge_before"] == {"state": "read", "pending": 0}
    assert out["pages_loaded"] == 2


@pytest.mark.parametrize("surface", sorted(badge_bracket.WITHHOLDS_ON_MOVE))
def test_a_non_zero_badge_that_held_is_the_measurement(surface):
    out = badge_bracket.judge(surface, dict(LIST), _reading(3), _reading(3))
    assert out["cost"] == {"outcome": "held", "proven": True}
    assert out["rows"] == ["a record"]


@pytest.mark.parametrize("surface", ["sent_invitations", "own_following_list"])
@pytest.mark.parametrize(("before", "after"), [(2, 1), (1, 2)])
def test_a_moved_badge_withholds_the_sent_tab_and_the_following_list(surface, before, after):
    out = badge_bracket.judge(surface, dict(LIST), _reading(before), _reading(after))
    assert out["refused"] == "badge_moved" and out["readable"] is False
    assert "rows" not in out
    assert out["cost"] == {"outcome": "moved", "proven": True, "before": before, "after": after}


def test_a_fallen_badge_on_the_received_tab_is_its_passive_cost_and_the_list_returns():
    out = badge_bracket.judge("received_invitations", dict(LIST), _reading(3), _reading(0))
    assert out["rows"] == ["a record"] and out["readable"] is True
    assert out["cost"] == {"outcome": "moved", "proven": True, "before": 3, "after": 0}
    assert out.get("refused") is None


@pytest.mark.parametrize(
    ("surface", "withheld"),
    [("sent_invitations", True), ("own_following_list", True), ("received_invitations", False)],
)
def test_an_unreadable_after_withholds_only_where_a_move_would(surface, withheld):
    out = badge_bracket.judge(surface, dict(LIST), _reading(0), UNREADABLE)
    assert out["cost"]["outcome"] == "after_unreadable"
    assert ("rows" not in out) is withheld
    if withheld:
        assert out["refused"] == "badge_unreadable_after"


def test_the_badge_label_never_leaves():
    for reading in (_reading(0), _reading(4), UNREADABLE):
        out = badge_bracket.judge("received_invitations", dict(LIST), reading, reading)
        assert PLANT not in repr(out)
    assert PLANT not in repr(badge_bracket.before_unreadable(UNREADABLE))


def test_a_surface_the_bracket_does_not_judge_is_an_error():
    with pytest.raises(KeyError):
        badge_bracket.judge("connections", dict(LIST), _reading(0), _reading(0))


# ---------------------------------------------------------------------------
# The three tools, over a browser that loads nothing
# ---------------------------------------------------------------------------


class _FakeBrowser:
    """``BROWSER`` for the verdict branches: navigates, remembers, loads nothing."""

    def __init__(self, landing: dict[str, str]) -> None:
        self.gotos: list[str] = []
        self._landing = landing

    def session(self):
        class _Session:
            async def __aenter__(self_inner):
                return object()

            async def __aexit__(self_inner, *exc):
                return False

        return _Session()

    async def goto(self, page, url):
        self.gotos.append(url)
        return self._landing.get(url, url)


def _patch(monkeypatch, browser, before, after):
    queue = [before, after]

    async def fake_badge(page):
        return queue.pop(0)

    monkeypatch.setattr(server, "BROWSER", browser)
    monkeypatch.setattr(dom, "read_invitation_badge", fake_badge)


def _raw(pending: Any) -> dict[str, Any]:
    """A raw ``dom.read_invitation_badge`` reading the shipped parser reads."""
    if pending is None:
        return {"links": 0, "badge_links": 0, "label": None, "error": None}
    return {"links": 1, "badge_links": 1, "label": f"x, {pending} new notifications", "error": None}


TOOLS = [
    ("linkedin_received_invitations", "invitation_manager", "read_received_invitations",
     "https://www.linkedin.com/mynetwork/invitation-manager/"),
    ("linkedin_sent_invitations", "invitation_manager", "read_sent_invitations",
     "https://www.linkedin.com/mynetwork/invitation-manager/sent/"),
    ("linkedin_my_following_list", "following_list", "read_following_list",
     "https://www.linkedin.com/mynetwork/network-manager/people-follow/following/"),
]


def _tool(name: str):
    fn = getattr(server, name)
    return getattr(fn, "fn", fn)


@pytest.mark.parametrize(("tool", "module", "reader", "url"), TOOLS)
async def test_an_unreadable_badge_before_opens_nothing_but_the_feed(monkeypatch, tool, module, reader, url):
    browser = _FakeBrowser({})
    _patch(monkeypatch, browser, _raw(None), _raw(0))
    out = await _tool(tool)()
    assert browser.gotos == [server.FEED_URL]
    assert out["refused"] == "badge_unreadable_before" and out["pages_loaded"] == 1


@pytest.mark.parametrize(("tool", "module", "reader", "url"), TOOLS)
async def test_a_held_badge_returns_the_lists_reading(monkeypatch, tool, module, reader, url):
    browser = _FakeBrowser({})
    _patch(monkeypatch, browser, _raw(0), _raw(0))
    target = getattr(server, module)

    async def fake_read(page):
        return dict(LIST)

    monkeypatch.setattr(target, reader, fake_read)
    out = await _tool(tool)()
    assert browser.gotos == [server.FEED_URL, url]
    assert out["rows"] == ["a record"] and out["cost"]["outcome"] == "held"


@pytest.mark.parametrize(("tool", "module", "reader", "url"), TOOLS)
async def test_a_landing_off_the_list_reads_nothing(monkeypatch, tool, module, reader, url):
    browser = _FakeBrowser({url: "https://www.linkedin.com/mynetwork/"})
    _patch(monkeypatch, browser, _raw(0), _raw(0))
    target = getattr(server, module)

    async def must_not_read(page):  # pragma: no cover - the assertion is that it is not called
        raise AssertionError("the list was read off its own address")

    monkeypatch.setattr(target, reader, must_not_read)
    out = await _tool(tool)()
    assert out["refused"] == "landed_elsewhere"
