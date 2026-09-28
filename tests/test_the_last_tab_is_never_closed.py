"""His browser's last tab is never closed by this repository: fix 1 of the live lane's session 2.

THE DAY IT MATTERED. 2026-09-28, the live lane's session 2, attached to the
Chrome he had started on port 9224. At 08:48:45 the last run's teardown did
what every run's did -- closed the tab it had opened, then disconnected CDP
-- and at 08:49:16 the next attach found nothing listening and no process on
the profile. Closing the last tab of the last window ends Chrome. That our
tab was the last is plausible, not proven; the orchestrator's order of 08:52
was to make it impossible either way, with a test.

WHAT IS HELD HERE, over fake contexts that count every open page at every
moment -- no browser, no network:

* ours beside his: ours closes, his stays;
* ours alone: a KEEPER tab opens first, ours closes after, and the context
  never reaches zero open pages -- the shape the old teardown could not keep;
* no keeper possible, or pages that cannot be counted: ours is LEFT OPEN;
* the attach-mode teardown itself, end to end through ``LinkedInBrowser``,
  with ours as his browser's only tab: his browser keeps a tab and is not
  closed, and the CDP client still disconnects.

THE CORPUS HALF -- that no script and no module closes a page any other way --
is ``tests/test_a_probe_closes_its_own_tab.py``'s third check.
"""
from __future__ import annotations

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import cdp_bridge, profile_lock
from linkedin_server.browser import (
    TAB_ALREADY_CLOSED,
    TAB_CLOSED,
    TAB_CLOSED_AFTER_A_KEEPER,
    TAB_KEPT_THE_LAST,
    TAB_KEPT_UNCOUNTABLE,
    TAB_NONE,
    LinkedInBrowser,
    close_tab_keeping_the_window,
)


class _Tab:
    """A page that reports to its context at every close."""

    def __init__(self, context: "_Context", mine: bool = False) -> None:
        self.context = context
        self.mine = mine
        self._closed = False

    def is_closed(self) -> bool:
        return self._closed

    async def close(self) -> None:
        self._closed = True
        self.context.record()


class _Context:
    """His browser's context: its pages, and the fewest ever open at once."""

    def __init__(self, his: int = 0, keeper_fails: bool = False, uncountable: bool = False) -> None:
        self._pages: list[_Tab] = [_Tab(self) for _ in range(his)]
        self.keeper_fails = keeper_fails
        self.uncountable = uncountable
        self.keepers: list[_Tab] = []
        self.fewest_open: list[int] = []
        self.closed = False

    @property
    def pages(self) -> list[_Tab]:
        if self.uncountable:
            raise RuntimeError("the context went away")
        return list(self._pages)

    def open_count(self) -> int:
        return sum(1 for page in self._pages if not page.is_closed())

    def record(self) -> None:
        self.fewest_open.append(self.open_count())

    async def new_page(self) -> _Tab:
        if self.keeper_fails:
            raise RuntimeError("no new tab")
        tab = _Tab(self)
        self._pages.append(tab)
        self.keepers.append(tab)
        return tab

    def ours(self) -> _Tab:
        tab = _Tab(self, mine=True)
        self._pages.append(tab)
        return tab

    async def close(self) -> None:
        self.closed = True

    def set_default_timeout(self, _ms: int) -> None:
        return None


async def test_ours_beside_his_is_closed_and_his_stays() -> None:
    context = _Context(his=1)
    ours = context.ours()
    assert await close_tab_keeping_the_window(ours, context) == TAB_CLOSED
    assert ours.is_closed() and context.keepers == []
    assert context.fewest_open == [1]


async def test_ours_alone_opens_a_keeper_first_and_the_browser_never_reaches_zero() -> None:
    """THE CASE OF 08:48:45. The old teardown closed ours and left zero."""
    context = _Context(his=0)
    ours = context.ours()
    assert await close_tab_keeping_the_window(ours, context) == TAB_CLOSED_AFTER_A_KEEPER
    assert ours.is_closed()
    assert len(context.keepers) == 1 and not context.keepers[0].is_closed()
    assert min(context.fewest_open) >= 1


async def test_no_keeper_means_ours_stays_open() -> None:
    context = _Context(his=0, keeper_fails=True)
    ours = context.ours()
    assert await close_tab_keeping_the_window(ours, context) == TAB_KEPT_THE_LAST
    assert not ours.is_closed() and context.fewest_open == []


async def test_pages_that_cannot_be_counted_keep_ours_open() -> None:
    context = _Context(his=1, uncountable=True)
    ours = _Tab(context, mine=True)
    assert await close_tab_keeping_the_window(ours, context) == TAB_KEPT_UNCOUNTABLE
    assert not ours.is_closed()


async def test_the_page_s_own_context_is_the_default() -> None:
    context = _Context(his=0)
    ours = context.ours()
    assert await close_tab_keeping_the_window(ours) == TAB_CLOSED_AFTER_A_KEEPER
    assert len(context.keepers) == 1


async def test_nothing_to_close_is_said_so() -> None:
    context = _Context(his=1)
    ours = context.ours()
    await ours.close()
    assert await close_tab_keeping_the_window(ours, context) == TAB_ALREADY_CLOSED
    assert await close_tab_keeping_the_window(None, context) == TAB_NONE


async def test_the_browsers_close_tab_is_the_same_rule() -> None:
    context = _Context(his=0)
    ours = context.ours()
    assert await LinkedInBrowser().close_tab(ours) == TAB_CLOSED_AFTER_A_KEEPER
    assert min(context.fewest_open) >= 1


class _Client:
    def __init__(self, context: _Context) -> None:
        self.contexts = [context]
        self.disconnected = False

    async def close(self) -> None:
        self.disconnected = True


class _Driver:
    async def stop(self) -> None:
        return None


@pytest.fixture()
def attached_alone(monkeypatch, tmp_path):
    """ATTACH mode over a context holding NO tab of his: ours will be its only."""
    context = _Context(his=0)
    client = _Client(context)

    async def fake_attach():
        return _Driver(), client, context

    monkeypatch.setattr(browser_module, "CDP_ATTACH", True)
    monkeypatch.setattr(cdp_bridge, "attach", fake_attach)
    monkeypatch.setattr(profile_lock, "_LOCK_FILE", tmp_path / "chrome-profile.lock")
    monkeypatch.setattr(context, "new_page", _opener(context))
    return context, client


def _opener(context: _Context):
    """The first new page is the one ``_page()`` opens for us; any later one
    is a keeper."""
    async def new_page() -> _Tab:
        if not any(page.mine for page in context._pages):
            return context.ours()
        tab = _Tab(context)
        context._pages.append(tab)
        context.keepers.append(tab)
        return tab
    return new_page


async def test_the_attach_teardown_leaves_his_browser_a_tab(attached_alone) -> None:
    """END TO END: session, then stop, with ours the only tab. Red before the
    fix: the teardown closed ours and the context was left with zero open
    pages -- the state that ends a real Chrome."""
    context, client = attached_alone
    browser = LinkedInBrowser()
    async with browser.session() as page:
        ours = page
    await browser.stop()
    assert ours.is_closed()
    assert context.open_count() == 1 and len(context.keepers) == 1
    assert min(context.fewest_open) >= 1
    assert client.disconnected is True
    assert context.closed is False
