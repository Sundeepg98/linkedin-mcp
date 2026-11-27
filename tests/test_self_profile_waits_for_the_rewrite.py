"""His own profile, asserted after LinkedIn began rewriting ``/in/me/`` client-side.

THE REGRESSION, measured live on 2026-11-26 (the live lane's session 12, E1,
loads 1 and 2). ``linkedin_my_activity_items`` refused his own profile
``self_assertion_unreadable`` after two loads; its evidence, in closed words:
url marker absent, ``landed_on_member_path`` false, structure not read. The
dedicated profile's browsing history (a copy, closed classes only) showed why:
``/in/me/`` visited, then his member path about a second later as a SEPARATE
link-type visit with no redirect qualifier. LinkedIn now serves the self alias
as its own document and rewrites the address client-side; the shipped loader
read the landing before the rewrite, saw the self alias, and refused -- fail
closed, as designed. Selfprofile26's rule held. Its moment of reading did not.

THE FAKE PAGE. A local page served AT ``/in/me/`` whose own script moves its
address with ``history.replaceState`` after a delay: the same-document address
change that history recorded, made by the page and by nothing else. Its markup
is session 11's tracked landing (``tests/fixtures/live11/in_me_profile.html``,
every member segment ``x``), so a page that moves to ``/in/x/`` is the page that
markup was captured at, and one that moves to ``/in/y/`` is a page whose edit
controls belong to somebody else.

THE FIX UNDER TEST. ``self_profile.await_rewrite`` waits, bounded, while the
page still names the bare self alias; the loader and the press gate read the
url again after it and run selfprofile26's structure check on THAT url,
unchanged. THE PAGE MAY VETO; IT NEVER SUPPLIES THE ADDRESS: the member path is
waited for and asserted, never navigated to, and every navigation in every test
here is a constant of this repository.

RED BEFORE THE FIX, each on an ASSERTION about a shipped entry point (the
helper's own contract tests in sections 0 and 1 fail on its absence, which is
not counted as red): the three loader callers in section 2 refused his profile
exactly as E1 did; the press gate in section 4 pressed a page before it had
arrived -- on one that went on to name another member, too; and the live
harness's press step in section 5 stopped ``not_on_his_profile``. The CONTROLS
in section 3 refuse before and after.

NOTHING HERE REACHES LINKEDIN. Each page is served by its own route from a
tracked file; every other request is aborted by that route.
"""
from __future__ import annotations

import ast
import asyncio
import inspect
import json
import time
from contextlib import asynccontextmanager
from typing import Any, Optional
from unittest import mock

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import press, self_profile, server
from linkedin_server.errors import NotAuthenticatedError
from linkedin_server.server import (
    SELF_PROFILE_EDIT_INTRO_URL,
    SELF_PROFILE_URL,
    linkedin_my_activity_items,
    linkedin_profile_editor_fields,
    linkedin_surface_census,
)
from tests import test_activity_items as rail
from tests import test_press as press_tests
from tests import test_self_profile_without_the_url_marker as marker_gone

harness = marker_gone.harness

#: The self alias, as the loader requests it and as LinkedIn now serves it.
ALIAS = SELF_PROFILE_URL
#: Where the tracked landing's markup belongs: every member segment is ``x``.
HIS_PATH = "/in/x/"
#: A member path the landing's edit controls do NOT name.
ANOTHER_PATH = "/in/y/"
#: The measured gap between the alias and its rewrite: about a second.
MEASURED_DELAY_MS = 1000
#: For the press gate and the harness, which must be asked BEFORE the rewrite
#: lands: long enough that a loaded box still asks first.
PRESS_DELAY_MS = 1500
#: A short bound, for the controls that wait it out, so they do not idle the
#: shipped five seconds twice each.
SHORT_BOUND_S = 0.5

NEW_LANDING = marker_gone.NEW_LANDING
OTHER_MEMBER = marker_gone.OTHER_MEMBERS[1]
EDITOR = marker_gone.EDITOR
EDITOR_LANDED = marker_gone.EDITOR_LANDED
ITEM_PAGE = marker_gone.ITEM_PAGE
OWNERSHIP_REFUSALS = marker_gone.OWNERSHIP_REFUSALS
COUNTS = marker_gone.COUNTS

_html = marker_gone._html
_with_his_rail = marker_gone._with_his_rail


def _rewriting(markup: str, to: Optional[str], after_ms: Optional[int]) -> str:
    """The markup with a script of the page's OWN that moves its address to
    ``to`` after ``after_ms`` -- or, with ``to`` None, never moves it. It also
    records where the page was when anything was pressed, so a test can say
    whether a press came before the page arrived."""
    script = (
        "<script>"
        "document.addEventListener('click', function () {"
        " window.__presses = (window.__presses || 0) + 1;"
        " window.__pressedAt = location.pathname; }, true);"
    )
    if to is not None:
        script += (
            "setTimeout(function () { history.replaceState(null, '', "
            + json.dumps(to)
            + "); }, "
            + str(int(after_ms or 0))
            + ");"
        )
    script += "</script>"
    assert markup.count("</body>") == 1
    return markup.replace("</body>", script + "</body>")


async def _presses(page: Any) -> tuple[int, Optional[str]]:
    return (
        int(await page.evaluate("() => window.__presses || 0")),
        await page.evaluate("() => window.__pressedAt || null"),
    )


@pytest.fixture
async def chromium():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


def _at_the_alias(markup: str) -> dict[str, tuple[str, str]]:
    """The loader's one request, landed EXACTLY where it was asked for: the
    self alias served as its own document."""
    return {ALIAS: (ALIAS, markup)}


# ---------------------------------------------------------------------------
# 0. The rule, pure: which landings are waited on, and for how long at most
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "url,waited",
    [
        ("https://www.linkedin.com/in/me/", True),
        ("https://www.linkedin.com/in/me", True),
        ("https://www.linkedin.com/in/ME/", True),
        ("https://www.linkedin.com/in/me/?trk=x", True),
        # THE MARKER ANSWERED: decided by it exactly as before, never waited on
        ("https://www.linkedin.com/in/me/?isSelfProfile=true", False),
        ("https://www.linkedin.com/in/me/?isSelfProfile=false", False),
        # ALREADY ARRIVED: a member path is the rewrite's result, not its cause
        ("https://www.linkedin.com/in/x/", False),
        # beneath a root, another scheme or host, or no address at all
        ("https://www.linkedin.com/in/me/details/recommendations/", False),
        ("https://www.linkedin.com/in/me/edit/intro/", False),
        ("http://www.linkedin.com/in/me/", False),
        ("https://linkedin.com/in/me/", False),
        ("https://example.test/in/me/", False),
        ("https://www.linkedin.com/feed/", False),
        ("https://www.linkedin.com/in/", False),
        ("", False),
        (None, False),
    ],
)
def test_only_the_bare_self_alias_is_waited_on(url, waited):
    """ONE LANDING IS WAITED ON: the self alias's own profile root, on
    LinkedIn's host, carrying no marker. A landing the marker answered is
    decided by the marker, untouched; a member path has already arrived."""
    assert self_profile.awaits_rewrite(url) is waited


def test_the_wait_is_bounded_and_short():
    """A BOUND, NOT A LOOP: a few seconds, polled well inside it, so a LinkedIn
    change can never turn the wait into an open one against his account."""
    bound = self_profile.SELF_REWRITE_BOUND_S
    poll = self_profile.SELF_REWRITE_POLL_S
    assert isinstance(bound, float) and isinstance(poll, float)
    assert 1.0 <= bound <= 10.0, bound
    assert 0.0 < poll < bound, poll
    # MEASURED: the rewrite came about a second after the alias; the bound
    # covers that several times over.
    assert bound * 1000 >= 3 * MEASURED_DELAY_MS


# ---------------------------------------------------------------------------
# 1. The wait, on a page that is nothing but an address
# ---------------------------------------------------------------------------


class _MovingAddress:
    """A page that is NOTHING BUT AN ADDRESS: ``first`` until ``after_s`` has
    passed, then ``then``. Anything else asked of it raises, so a wait that
    touched the page any other way could not report that it arrived."""

    def __init__(self, first: Any, then: Optional[str] = None, after_s: float = 0.0) -> None:
        self._first = first
        self._then = then
        self._after = after_s
        self._t0 = time.monotonic()
        self.reads = 0

    @property
    def url(self) -> Any:
        self.reads += 1
        if self._then is not None and time.monotonic() - self._t0 >= self._after:
            return self._then
        return self._first

    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"the wait asked the page for {name!r}")


class _UnreadableAddress:
    """A page whose address raises, quoting a page string in its message."""

    @property
    def url(self) -> Any:
        raise RuntimeError("a page string: Someone Example")


_WORDS = {"not_needed", "arrived", "not_within_bound", "unreadable"}


def _closed(outcome: dict[str, Any]) -> None:
    """Closed words and integers, and nothing else, ever."""
    assert set(outcome) == {"rewrite", "waited_ms", "polls"}, outcome
    assert outcome["rewrite"] in _WORDS, outcome
    for key in ("waited_ms", "polls"):
        assert isinstance(outcome[key], int) and not isinstance(outcome[key], bool), outcome
        assert outcome[key] >= 0


async def test_the_wait_ends_when_the_address_leaves_the_alias():
    page = _MovingAddress(ALIAS, "https://www.linkedin.com" + HIS_PATH, after_s=0.3)
    started = time.monotonic()
    outcome = await self_profile.await_rewrite(page)
    elapsed = time.monotonic() - started
    _closed(outcome)
    assert outcome["rewrite"] == "arrived", outcome
    assert outcome["polls"] >= 1
    assert 0.25 <= elapsed < self_profile.SELF_REWRITE_BOUND_S, elapsed
    assert page.url == "https://www.linkedin.com" + HIS_PATH


async def test_the_wait_gives_up_at_its_bound_and_never_raises(monkeypatch):
    monkeypatch.setattr(self_profile, "SELF_REWRITE_BOUND_S", 0.4)
    still = _MovingAddress(ALIAS)
    started = time.monotonic()
    outcome = await self_profile.await_rewrite(still)
    elapsed = time.monotonic() - started
    _closed(outcome)
    assert outcome["rewrite"] == "not_within_bound", outcome
    assert 0.4 <= elapsed < 0.4 + self_profile.SELF_REWRITE_POLL_S + 0.5, elapsed

    # A LATE REWRITE IS NOT WAITED FOR: the bound binds.
    late = _MovingAddress(ALIAS, "https://www.linkedin.com" + HIS_PATH, after_s=1.5)
    assert (await self_profile.await_rewrite(late))["rewrite"] == "not_within_bound"

    # NOT THE ALIAS: no wait at all, and the address read once.
    arrived = _MovingAddress("https://www.linkedin.com" + HIS_PATH)
    started = time.monotonic()
    outcome = await self_profile.await_rewrite(arrived)
    assert outcome == {"rewrite": "not_needed", "waited_ms": outcome["waited_ms"], "polls": 0}
    assert time.monotonic() - started < 0.2 and arrived.reads == 1

    # AN ADDRESS THAT RAISES: closed words back, nothing raised, nothing quoted.
    outcome = await self_profile.await_rewrite(_UnreadableAddress())
    _closed(outcome)
    assert outcome["rewrite"] == "unreadable" and "Someone" not in repr(outcome)
    assert (await self_profile.await_rewrite(None))["rewrite"] == "unreadable"


def test_the_wait_reads_the_address_and_nothing_else():
    """STRUCTURAL: the only thing the wait asks of the page is its ``url``. It
    never navigates, never reloads, never runs a script and never presses --
    the page can move its own address and the wait can only watch it."""
    tree = ast.parse(inspect.getsource(self_profile.await_rewrite))
    asked = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "page"
    }
    assert asked == {"url"}, asked
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    for verb in ("goto", "reload", "go_back", "go_forward", "evaluate", "click",
                 "press", "wait_for_url", "set_content", "locator"):
        assert verb not in called, verb


# ---------------------------------------------------------------------------
# 2. The loader's three callers, on a page whose address moves after a delay
# ---------------------------------------------------------------------------


async def test_his_profile_is_asserted_after_the_rewrite_by_every_loader_caller(chromium, monkeypatch):
    """RED BEFORE THE FIX, three times: each caller refused his own profile
    ``self_assertion_unreadable`` after TWO loads with ``landed_on_member_path``
    false -- session 12's E1, reproduced. Now each sees his profile on ONE
    load, by his edit controls, once the page has moved to his member path;
    and the loader navigated to its own constant and nothing else.

    The editor tool's second page is served at the member path as it landed in
    session 7: what ``/in/me/edit/intro/`` does under the new self alias was
    not captured (session 12 did not load it), so only the ownership gate is
    under test here.
    """
    his = _rewriting(_with_his_rail(_html(NEW_LANDING)), HIS_PATH, MEASURED_DELAY_MS)

    result, world = await marker_gone._drive(
        chromium, monkeypatch, _at_the_alias(his), linkedin_my_activity_items
    )
    assert result.get("refused") is None, result
    assert result["items"] == [rail.HIS_ITEM_ONE, rail.HIS_ITEM_TWO], result
    assert result["authorship"]["established"] is True
    assert result["authorship"]["self_signal"] == "edit_controls"
    assert result["pages_loaded"] == 1
    assert world.navigations == [ALIAS], world.navigations
    assert world.page.url == "https://www.linkedin.com" + HIS_PATH
    await world.page.close()

    served = {
        ALIAS: (ALIAS, _rewriting(_html(NEW_LANDING), HIS_PATH, MEASURED_DELAY_MS)),
        SELF_PROFILE_EDIT_INTRO_URL: (EDITOR_LANDED, _html(EDITOR)),
    }
    result, world = await marker_gone._drive(chromium, monkeypatch, served, linkedin_profile_editor_fields)
    assert result.get("refused") not in OWNERSHIP_REFUSALS, result
    assert result["self_ownership"]["established"] is True, result
    assert result["self_ownership"]["same_member"] is True
    assert result["self_ownership"]["self_signal"] == "edit_controls"
    assert world.navigations == [ALIAS, SELF_PROFILE_EDIT_INTRO_URL], world.navigations
    assert result["pages_loaded"] == 2
    await world.page.close()

    async def census() -> Any:
        return await linkedin_surface_census("feed_item", item=rail.HIS_ITEM_ONE)

    served = {
        ALIAS: (ALIAS, his),
        ITEM_PAGE: (ITEM_PAGE, "<!doctype html><html><body><main></main></body></html>"),
    }
    result, world = await marker_gone._drive(chromium, monkeypatch, served, census)
    assert result.get("refused") is None, result
    assert result["aimed_at"]["verified"] is True, result
    assert world.navigations == [ALIAS, ITEM_PAGE], world.navigations
    await world.page.close()


async def test_the_loader_reports_the_wait_and_never_follows_the_page(chromium, monkeypatch):
    """RED BEFORE THE FIX: the loader returned the self alias as its landing.
    Now it returns the address the page moved to -- READ, never built -- with
    the wait's outcome beside it in closed words and integers, and it made
    exactly one navigation: to its own constant."""
    his = _rewriting(_html(NEW_LANDING), HIS_PATH, MEASURED_DELAY_MS)
    page = await chromium.new_page()
    world = await marker_gone._World(page, _at_the_alias(his)).install()
    monkeypatch.setattr(browser_module.BROWSER, "goto", world.goto)
    landed, state, loads, saw = await server._goto_self_profile_asserted(page)
    assert (state, loads) == (server.SELF_ASSERTION_TRUE, 1), (state, loads, saw)
    assert landed == "https://www.linkedin.com" + HIS_PATH
    assert world.navigations == [ALIAS]
    assert saw["self_signal"] == "edit_controls" and saw["landed_on_member_path"] is True
    assert saw["self_alias_rewrite"] == "arrived", saw
    assert isinstance(saw["self_alias_waited_ms"], int)
    assert 0 < saw["self_alias_waited_ms"] < self_profile.SELF_REWRITE_BOUND_S * 1000
    await page.close()


# ---------------------------------------------------------------------------
# 3. The controls: every other landing is refused, before the fix and after
# ---------------------------------------------------------------------------


#: A bound the moving cases below cannot miss on a loaded box: they move at
#: the measured second, inside it.
MOVING_BOUND_S = 3.0


def _not_his_cases() -> dict[str, tuple[str, float]]:
    """Every landing of the alias that is not his, by name: ``(markup, bound)``.
    The bound is patched per case so the cases that wait it out do not idle
    the shipped five seconds twice each; the moving cases move at the measured
    second, inside theirs."""
    base = _with_his_rail(_html(NEW_LANDING))
    stranger = _with_his_rail(_html(OTHER_MEMBER))
    return {
        "never moves": (_rewriting(base, None, None), SHORT_BOUND_S),
        "moves after the bound": (_rewriting(base, HIS_PATH, 2500), SHORT_BOUND_S),
        "moves to the feed": (_rewriting(base, "/feed/", MEASURED_DELAY_MS), MOVING_BOUND_S),
        "moves beneath a profile root": (
            _rewriting(base, HIS_PATH + "details/experience/", MEASURED_DELAY_MS),
            MOVING_BOUND_S,
        ),
        "moves to another member's path": (_rewriting(base, ANOTHER_PATH, MEASURED_DELAY_MS), MOVING_BOUND_S),
        "another member's profile at his path": (_rewriting(stranger, HIS_PATH, MEASURED_DELAY_MS), MOVING_BOUND_S),
    }


async def test_every_landing_that_is_not_his_is_still_refused(chromium, monkeypatch):
    """THE CONTROLS, refused BEFORE THE FIX AND AFTER IT (they pass on both
    trees; the next test pins the refusal codes the wait makes possible). No
    ownership is ever established, nothing is published, and every navigation
    is the loader's own constant:

    * the alias never moves;
    * it moves only AFTER the bound;
    * it moves to a page that is not a member's profile root (the feed; a page
      beneath his profile root);
    * it moves to his markup under ANOTHER member's path;
    * it moves to his path while drawing ANOTHER member's real profile.
    """
    for name, (markup, bound) in _not_his_cases().items():
        monkeypatch.setattr(self_profile, "SELF_REWRITE_BOUND_S", bound, raising=False)
        result, world = await marker_gone._drive(
            chromium, monkeypatch, _at_the_alias(markup), linkedin_my_activity_items
        )
        assert result.get("refused") in OWNERSHIP_REFUSALS, (name, result)
        assert "items" not in result, (name, result)
        assert result["authorship"]["established"] is False, (name, result)
        assert set(world.navigations) == {ALIAS}, (name, world.navigations)
        assert "/in/x" not in repr(result) and "/in/y" not in repr(result), (name, result)
        await world.page.close()


async def test_the_refusals_name_where_the_page_went(chromium, monkeypatch):
    """THE REFUSAL CODES THE WAIT MAKES POSSIBLE, and what each names.

    RED BEFORE THE FIX on the cases that need the page's real address: the
    alias moving to another member's path read as unread (2 loads) instead of
    AMBIGUOUS (refused at once, 1 load), and no refusal could say whether the
    alias ever moved. The structure check itself is selfprofile26's,
    unchanged: another member's real profile at his path draws no edit control
    for him, and the real landing under another path draws four for a member
    the url does not name. The whole table is compared at once, so a failure
    prints every row.
    """
    expected = {
        # name: (refused, loads, the wait's word, landed on a member path, counts)
        "never moves": ("self_assertion_unreadable", 2, "not_within_bound", False, (None, None, None)),
        "moves after the bound": ("self_assertion_unreadable", 2, "not_within_bound", False, (None, None, None)),
        "moves to the feed": ("self_assertion_unreadable", 2, "arrived", False, (None, None, None)),
        "moves beneath a profile root": ("self_assertion_unreadable", 2, "arrived", False, (None, None, None)),
        "moves to another member's path": ("self_profile_ambiguous", 1, "arrived", True, (0, 0, 4)),
        "another member's profile at his path": ("self_assertion_unreadable", 2, "arrived", True, (0, 0, 0)),
    }
    measured, reasons = {}, {}
    for name, (markup, bound) in _not_his_cases().items():
        monkeypatch.setattr(self_profile, "SELF_REWRITE_BOUND_S", bound, raising=False)
        result, world = await marker_gone._drive(
            chromium, monkeypatch, _at_the_alias(markup), linkedin_my_activity_items
        )
        saw = result.get("self_evidence") or {}
        measured[name] = (
            result.get("refused"),
            result.get("pages_loaded"),
            saw.get("self_alias_rewrite"),
            saw.get("landed_on_member_path"),
            tuple(saw.get(count) for count in COUNTS),
        )
        reasons[name] = str(result.get("reason"))
        await world.page.close()
    assert measured == expected
    # WHAT A REFUSAL SAYS IT SAW: the alias that never moved is named as such,
    # and the one that moved off a member path is named as having moved.
    assert "self alias" in reasons["never moves"], reasons["never moves"]
    assert "rewrote" in reasons["moves to the feed"], reasons["moves to the feed"]


async def test_an_alias_that_moves_onto_the_signed_out_wall_is_the_wall(chromium, monkeypatch):
    """THE PAGE MAY VETO: an alias whose address moves onto the signed-out wall
    raises the wall's own error, as a landing there always has. RED BEFORE THE
    FIX: the loader read the alias, saw no wall, and refused it as unread
    twice -- the wall it moved to was never looked at."""
    wall = _rewriting(_html(NEW_LANDING), "/authwall?trk=x", MEASURED_DELAY_MS)
    page = await chromium.new_page()
    world = await marker_gone._World(page, _at_the_alias(wall)).install()
    monkeypatch.setattr(browser_module.BROWSER, "goto", world.goto)
    with pytest.raises(NotAuthenticatedError):
        await server._goto_self_profile_asserted(page)
    assert world.navigations == [ALIAS]
    await page.close()


# ---------------------------------------------------------------------------
# 4. The press gate: judged where the page arrives, pressed only after it has
# ---------------------------------------------------------------------------


async def test_the_press_gate_judges_the_page_where_it_arrives(chromium):
    """RED BEFORE THE FIX, twice. The committed table judges no control on his
    profile a disclosure, so the one that reaches a press is PLANTED, exactly
    as ``tests/test_press.py``'s positive control plants it.

    * His landing, still at the alias when the gate is asked: before the fix
      the gate judged the alias and PRESSED AT ONCE, before the page had
      arrived (``__pressedAt`` the alias). Now it waits, the page moves to his
      member path, the structure says his, and the press is made THERE.
    * The same markup moving to ANOTHER member's path: before the fix it was
      pressed on the alias all the same. Now it is refused
      ``address_not_admitted`` and nothing is pressed -- the page vetoed.
    """
    planted = press_tests._with_control("[aria-expanded]", press_tests._PLANTED_DISCLOSURE)
    with mock.patch.object(press, "SENSITIVITY_BASES", planted):
        world = await marker_gone._served(
            chromium, _rewriting(_html(NEW_LANDING), HIS_PATH, PRESS_DELAY_MS), ALIAS
        )
        verdict = await press.disclose(world.page, shape="[aria-expanded]", read_counters=marker_gone._counters)
        assert verdict.get("pressed") is True, verdict
        assert await _presses(world.page) == (1, HIS_PATH), "pressed before the page arrived"
        await world.page.close()

        world = await marker_gone._served(
            chromium, _rewriting(_html(NEW_LANDING), ANOTHER_PATH, PRESS_DELAY_MS), ALIAS
        )
        verdict = await press.disclose(world.page, shape="[aria-expanded]", read_counters=marker_gone._counters)
        assert verdict.get("refused") == "address_not_admitted", verdict
        assert verdict["self_evidence"]["edit_routes_on_another_member"] == 4, verdict
        assert await _presses(world.page) == (0, None)
        assert "/in/y" not in repr(verdict)
        await world.page.close()


async def test_the_press_gate_waits_on_the_alias_and_on_nothing_else(chromium, monkeypatch):
    """THE CONTROL: a page already at a member path, or anywhere that is not
    the bare alias, is judged with no wait at all -- the gate asks the page
    exactly what it asked before the fix."""
    calls: list[Any] = []

    async def spy(page: Any) -> dict[str, Any]:
        calls.append(page)
        return {"rewrite": "not_needed", "waited_ms": 0, "polls": 0}

    monkeypatch.setattr(self_profile, "await_rewrite", spy, raising=False)
    for markup, landed in (
        (_html(NEW_LANDING), marker_gone.LANDED),
        (_html(OTHER_MEMBER), marker_gone.LANDED),
    ):
        world = await marker_gone._served(chromium, markup, landed)
        await press.disclose(world.page, shape="[aria-expanded]", read_counters=marker_gone._counters)
        assert await world.clicks() == 0
        await world.page.close()
    assert calls == []


# ---------------------------------------------------------------------------
# 5. The live harness's press step, which reads his landing as the gate does
# ---------------------------------------------------------------------------


async def test_the_live_harness_press_step_sees_his_profile_after_the_rewrite(chromium, monkeypatch):
    """RED BEFORE THE FIX: ``_in_me_more`` read the alias and stopped
    ``not_on_his_profile``. Now it waits as the gate does, and -- with no
    stylesheet both of the top card's bars draw -- stops at the opener rule
    instead, AFTER seeing his profile, with nothing pressed. THE CONTROL:
    another member's real profile, moving to his path, still stops
    ``not_on_his_profile``."""
    for markup, expected_stop in (
        (_html(NEW_LANDING), "opener_not_exactly_one"),
        (_html(OTHER_MEMBER), "not_on_his_profile"),
    ):
        world = await marker_gone._served(chromium, _rewriting(markup, HIS_PATH, PRESS_DELAY_MS), ALIAS)

        class _Served:
            @asynccontextmanager
            async def session(self, page: Any = world.page):
                yield page

        monkeypatch.setattr(harness, "BROWSER", _Served())
        result = await harness._in_me_more(False)
        assert result.get("stopped") == expected_stop, (expected_stop, result)
        assert await _presses(world.page) == (0, None)
        await world.page.close()


def test_the_wait_is_one_function_its_callers_share():
    """ONE WAIT, so the loader, the press gate and the harness cannot drift
    onto three bounds: each calls ``self_profile.await_rewrite`` and none of
    them sleeps on its own."""
    for function in (server._goto_self_profile_asserted, press.disclose, harness._in_me_more):
        source = inspect.getsource(function)
        assert "self_profile.await_rewrite(" in source, function.__name__
        assert "self_profile.awaits_rewrite(" in source, function.__name__
        assert "asyncio.sleep" not in source and "wait_for_timeout" not in source, function.__name__


def test_asyncio_is_imported_where_the_wait_sleeps():
    """The wait sleeps with ``asyncio.sleep``, never a page timer, so a page
    that is nothing but an address can be waited on (section 1)."""
    assert "asyncio.sleep(" in inspect.getsource(self_profile.await_rewrite)
    assert asyncio.iscoroutinefunction(self_profile.await_rewrite)
