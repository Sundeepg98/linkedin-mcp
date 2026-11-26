"""His own profile, asserted after LinkedIn stopped writing ``isSelfProfile``.

THE REGRESSION. On 2026-11-25 (the live lane's session 11) both loads of
``/in/me/`` landed on his member path with NO query string, and the page drew
the marker nowhere -- the 28 ``?isSelfProfile=`` links of every older self
capture are plain member links now. Every gate that anchored on the marker
refused his own profile: the self-profile loader (the editor tools, the
activity reader, the census's item veto), the press gate's ``self_landing``,
and the live harness's two self-profile steps.

THE SIGNAL, measured before anything was built on it. LinkedIn draws EDIT
CONTROLS for the landed member -- ``<a aria-label=... href=
"https://www.linkedin.com/in/<that member>/edit/...">`` -- on its owner's
profile and on nobody else's: 4 on the new landing, 4 on each of the three
older self captures, 0 on each of the three tracked captures of another
member's profile. :func:`test_the_signal_on_every_tracked_profile_capture` is
that measurement, kept as a test.

THE FIXTURE. ``tests/fixtures/live11/in_me_profile.html`` is session 11's
skeleton of the landing, the live lane's tracked copy through the harness's
own ``tracked_copy`` (this lane built the same copy byte for byte from the same
skeleton, and kept the live lane's): every value is ``x``, so every member
segment is ``x`` and a page landed at ``/in/x/`` is the page this markup was
captured at. Landed at ``/in/y/`` the same markup is a page whose edit
controls belong to somebody else.

EVERY BEHAVIOURAL TEST HERE DRIVES A SHIPPED ENTRY POINT -- a tool, the press
gate, the live harness -- and was RED before the fix, refusing his profile.
The controls (another member's real profile, and the real landing under a
different member path) refuse before and after.

ONE BROWSER PER TEST, SEVERAL PAGES IN IT. A launch measured 8-10 s on the
lane's box with the live session running, so each test takes one site through
every scenario it has rather than launching once per scenario.

NOTHING HERE REACHES LINKEDIN. Each page is served by its own route from a
tracked file; every other request is aborted by that route.
"""
from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Awaitable, Callable

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import press
from linkedin_server.server import (
    SELF_PROFILE_EDIT_INTRO_URL,
    SELF_PROFILE_URL,
    linkedin_my_activity_items,
    linkedin_profile_editor_fields,
    linkedin_profile_editor_values,
    linkedin_surface_census,
)
from tests import test_activity_items as rail

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import _probe_live_lane_session_2 as harness  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"

#: Session 11's landing of ``/in/me/`` (2026-11-25 23:23), as a tracked copy.
NEW_LANDING = FIXTURES / "live11" / "in_me_profile.html"

#: The same session's landing with a top-card menu open and with the photo
#: dialog open -- the photo dialog adds editor links, four of them with NO
#: accessible name, which is the route-versus-control line drawn by LinkedIn's
#: own markup: (named controls, all routes) for the landed member.
SESSION_11_OPEN_STATES = (
    (FIXTURES / "live11" / "in_me_more_open.html", (4, 4, 0)),
    (FIXTURES / "live11" / "in_me_photo_open.html", (7, 11, 0)),
)

#: The three older self captures, from sessions 2, 3 and 8, which still carried
#: the marker -- 28 times each.
OLDER_SELF = (
    FIXTURES / "live2" / "in_me.html",
    FIXTURES / "live3" / "in_me.html",
    FIXTURES / "live8" / "in_me.html",
)

#: Every tracked capture of ANOTHER member's profile root: a first-degree
#: connection (session 2), a named profile (session 3), and a named profile
#: after its Message press (session 3).
OTHER_MEMBERS = (
    FIXTURES / "live2" / "first_degree_profile.html",
    FIXTURES / "live3" / "named_profile.html",
    FIXTURES / "live3" / "m1_after_press.html",
)

#: His intro editor, session 7, tracked: what ``/in/me/edit/intro/`` draws.
EDITOR = FIXTURES / "live7" / "editor.html"

#: Where the tracked copies put every member: one shaped segment.
LANDED = "https://www.linkedin.com/in/x/"
#: The same markup, landed under a different member path.
LANDED_ELSEWHERE = "https://www.linkedin.com/in/y/"
#: The editor as it lands: the member path, no trailing slash (measured).
EDITOR_LANDED = "https://www.linkedin.com/in/x/edit/intro"
#: An item page, for the census's veto: his item, by the synthetic urn.
ITEM_PAGE = f"https://www.linkedin.com/feed/update/{rail.HIS_ITEM_ONE}/"

#: Every refusal the ownership gate itself can return, before any reader runs.
OWNERSHIP_REFUSALS = (
    "not_self_profile",
    "self_assertion_unreadable",
    "self_profile_ambiguous",
    "profile_path_unreadable",
    "editor_path_unreadable",
    "different_member",
)

#: The three counts the structural reading takes.
COUNTS = (
    "edit_controls_on_landed_member",
    "edit_routes_on_landed_member",
    "edit_routes_on_another_member",
)


def _html(path: Path) -> str:
    return path.read_text(encoding="ascii")


def _with_a_plain_link_to_its_own_editor(html: str) -> str:
    """Another member's real profile with what a member's OWN text could put
    there: a plain link to that member's editor, named by its text and not by
    an accessible name -- a linkified url. It is an edit ROUTE for the landed
    member and NOT an edit CONTROL, so it must establish nothing. (Unmeasured
    whether LinkedIn ever draws one: section 2 of the record says so; this
    pins the rule for the day it does.)"""
    opening = html.index("<main ")
    close = html.index(">", opening) + 1
    link = (
        '<a href="https://www.linkedin.com/in/x/edit/intro/">'
        "https://www.linkedin.com/in/x/edit/intro/</a>"
    )
    return html[:close] + link + html[close:]


def _with_his_rail(html: str) -> str:
    """The real landing with a SYNTHETIC rail of his items inside ``main``, and
    an ``h1`` naming its owner -- the tracked copy's own rail reads ``x`` for
    every label, so it can never carry an author. The edit controls, the
    landing and everything else are the capture's."""
    opening = html.index("<main ")
    close = html.index(">", opening) + 1
    items = (
        rail.H1_OWNER
        + rail.item(rail.AUTHOR_SHORT, rail.HIS_ITEM_ONE, extra=rail.permalink(rail.HIS_ITEM_ONE, "2w"))
        + rail.item(rail.AUTHOR_SHORT, rail.HIS_ITEM_TWO)
    )
    derived = html[:close] + items + html[close:]
    assert derived != html
    return derived


# ---------------------------------------------------------------------------
# A browser whose pages are served from tracked files, and a world around it
# ---------------------------------------------------------------------------


@pytest.fixture
async def chromium():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            yield browser
        finally:
            await browser.close()


class _World:
    """``BROWSER.session`` and ``BROWSER.goto`` over ONE local page.

    ``served`` maps a REQUESTED address to ``(landed, markup)``: a navigation to
    the requested address loads ``landed`` and the page's own route answers it
    with ``markup``. Every other request the page makes -- the skeleton keeps
    its stylesheet and image addresses -- is aborted by that route. Every
    navigation installs a click counter, so a test can say nothing was pressed.
    """

    def __init__(self, page: Any, served: dict[str, tuple[str, str]]) -> None:
        self.page = page
        self.served = dict(served)
        self.navigations: list[str] = []
        self._markup = {landed: markup for landed, markup in self.served.values()}

    async def install(self) -> "_World":
        async def answer(route: Any) -> None:
            body = self._markup.get(route.request.url)
            if body is None:
                await route.abort()
            else:
                await route.fulfill(status=200, content_type="text/html", body=body)

        await self.page.route("**/*", answer)
        return self

    @asynccontextmanager
    async def session(self):
        yield self.page

    async def goto(self, _page: Any, url: str, **_kwargs: Any) -> str:
        self.navigations.append(url)
        landed, _markup = self.served[url]
        await self.page.goto(landed, wait_until="domcontentloaded")
        await self.page.evaluate(
            "() => document.addEventListener('click',"
            " () => { window.__clicks = (window.__clicks || 0) + 1; }, true)"
        )
        return self.page.url

    async def clicks(self) -> int:
        return int(await self.page.evaluate("() => window.__clicks || 0"))


async def _drive(
    chromium: Any,
    monkeypatch: Any,
    served: dict[str, tuple[str, str]],
    call: Callable[[], Awaitable[Any]],
) -> tuple[Any, _World]:
    """One scenario: a fresh page and world in the shared browser, the
    package's ``BROWSER`` pointed at them, and the entry point called."""
    page = await chromium.new_page()
    world = await _World(page, served).install()
    monkeypatch.setattr(browser_module.BROWSER, "session", world.session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", world.goto)
    return await call(), world


async def _served(chromium: Any, markup: str, landed: str) -> _World:
    """A page already sitting on ``landed``, drawing ``markup``."""
    world = await _World(await chromium.new_page(), {landed: (landed, markup)}).install()
    await world.goto(world.page, landed)
    return world


def _profile(markup: str, landed: str = LANDED) -> dict[str, tuple[str, str]]:
    return {SELF_PROFILE_URL: (landed, markup)}


# ---------------------------------------------------------------------------
# 0. The fixture, and the rule as pure functions
# ---------------------------------------------------------------------------


def test_the_new_landing_is_a_tracked_copy_and_draws_no_marker():
    text = NEW_LANDING.read_bytes().decode("ascii")
    assert text.startswith("<!doctype html>")
    assert not harness._KEYED_SHAPE.search(text), "a keyed shape survived the copy"
    assert "isSelfProfile" not in text, "the regression is that the marker is gone"
    for path in OLDER_SELF:
        assert _html(path).count("isSelfProfile") == 28, path.name


def _reading(controls: Any, routes: Any, another: Any) -> dict[str, Any]:
    return {
        "read": True,
        "landed_on_member_path": True,
        "edit_controls_on_landed_member": controls,
        "edit_routes_on_landed_member": routes,
        "edit_routes_on_another_member": another,
    }


@pytest.mark.parametrize(
    "marker,reading,state",
    [
        ("true", None, "true"),
        ("true", _reading(0, 0, 4), "true"),
        ("false", _reading(4, 4, 0), "false"),
        ("absent", _reading(4, 4, 0), "true"),
        ("absent", _reading(1, 1, 0), "true"),
        ("absent", _reading(0, 3, 0), "absent"),
        ("absent", _reading(0, 0, 0), "absent"),
        ("absent", _reading(4, 4, 1), "ambiguous"),
        ("absent", _reading(0, 0, 4), "ambiguous"),
        ("absent", None, "absent"),
        ("absent", {"read": False, "landed_on_member_path": True, "unreadable": "TimeoutError"}, "absent"),
        ("absent", {"read": False, "landed_on_member_path": False, "unreadable": None}, "absent"),
        ("absent", _reading("4", 4, 0), "absent"),
        ("absent", _reading(4, 4, True), "absent"),
    ],
)
def test_the_rule_is_the_marker_if_it_answered_else_the_structure(marker, reading, state):
    """THE WHOLE RULE AS A TABLE. An edit route for the landed member with no
    accessible name is not a control (a viewer's 'complete your profile' link
    draws none); a count that is not an integer is no count at all."""
    from linkedin_server import self_profile

    assert self_profile.self_state(marker, reading) == state


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/in/me/",
        "https://www.linkedin.com/in/ME",
        "https://www.linkedin.com/in/x/details/experience/",
        "https://www.linkedin.com/in/x/edit/intro/",
        "https://www.linkedin.com/in/",
        "http://www.linkedin.com/in/x/",
        "https://linkedin.com/in/x/",
        "https://example.test/in/x/",
        "https://www.linkedin.com/in/x'y/",
        "https://www.linkedin.com/in/x]y/",
        "https://www.linkedin.com/company/x/",
        "",
        None,
    ],
)
def test_only_a_member_profile_root_is_ever_read(url):
    """NEVER ANY PROFILE UNDER /in/: the self alias, a page beneath a root,
    another scheme or host, and a segment outside the closed alphabet are not
    member landings -- and a selector is never built from one."""
    from linkedin_server import self_profile

    assert self_profile.landed_member_segment(url) is None
    assert self_profile.wants_structure(url) is False


@pytest.mark.parametrize("segment", ["x'y", 'x"y', "x]y", "x y", "", "x/y", "x)or(1=1"])
def test_a_segment_outside_the_alphabet_never_reaches_a_selector(segment):
    from linkedin_server import self_profile

    with pytest.raises(ValueError):
        self_profile.edit_route_selectors(segment)


def test_the_marker_still_answers_where_it_rides():
    """The url marker is kept as an accepted signal and read exactly as it
    was: the loader takes any ``true``, the press gate needs every value to."""
    from linkedin_server import self_profile

    both = "https://www.linkedin.com/in/x/?isSelfProfile=true&isSelfProfile=false"
    assert self_profile.url_marker(both) == "true"
    assert self_profile.url_marker(both, unanimous=True) == "false"
    assert self_profile.url_marker("https://www.linkedin.com/in/x/?isSelfProfile=TRUE") == "true"
    assert self_profile.url_marker("https://www.linkedin.com/in/x/?isSelfProfile=") == "absent"
    assert self_profile.url_marker(LANDED) == "absent"


# ---------------------------------------------------------------------------
# 1. The measurement, kept as a test: the shipped reader over every capture
# ---------------------------------------------------------------------------


async def test_the_signal_on_every_tracked_profile_capture(chromium):
    """4 edit controls for the landed member on every self capture, old and
    new (7 named of 11 routes with the photo dialog open); none on any other
    member's; and the new landing's 4 belong to ANOTHER member once it is
    landed under a different path. The whole table is compared at once, so a
    failure prints every row."""
    from linkedin_server import self_profile

    cases = (
        [(NEW_LANDING, LANDED, (4, 4, 0), _html)]
        + [(path, LANDED, counts, _html) for path, counts in SESSION_11_OPEN_STATES]
        + [(path, LANDED, (4, 4, 0), _html) for path in OLDER_SELF]
        + [(path, LANDED, (0, 0, 0), _html) for path in OTHER_MEMBERS]
        + [(NEW_LANDING, LANDED_ELSEWHERE, (0, 0, 4), _html)]
        # A plain link to the member's own editor, with no accessible name,
        # inside another member's real profile: a ROUTE, not a CONTROL.
        + [(OTHER_MEMBERS[1], LANDED, (0, 1, 0), lambda p: _with_a_plain_link_to_its_own_editor(_html(p)))]
    )
    expected, measured = {}, {}
    for path, landed, counts, markup in cases:
        name = f"{path.parent.name}/{path.name}@{landed}" + ("" if markup is _html else "+plain link")
        world = await _served(chromium, markup(path), landed)
        reading = await self_profile.read_edit_routes(world.page, landed)
        expected[name] = (True, counts)
        measured[name] = (reading["read"], tuple(reading.get(count) for count in COUNTS))
        await world.page.close()
    assert measured == expected


# ---------------------------------------------------------------------------
# 2. The self-profile loader, through the two editor tools
# ---------------------------------------------------------------------------


async def test_the_editor_gate_establishes_his_ownership_on_the_new_landing(chromium, monkeypatch):
    """RED BEFORE THE FIX, for both tools: ``self_assertion_unreadable`` after
    two loads of ``/in/me/``, and the editor never opened. Whatever the editor
    READER then says of the session-7 editor is its own business; the gate's
    refusals are the ones that must not come back."""
    served = {
        SELF_PROFILE_URL: (LANDED, _html(NEW_LANDING)),
        SELF_PROFILE_EDIT_INTRO_URL: (EDITOR_LANDED, _html(EDITOR)),
    }
    for tool in (linkedin_profile_editor_fields, linkedin_profile_editor_values):
        result, world = await _drive(chromium, monkeypatch, served, tool)
        assert result.get("refused") not in OWNERSHIP_REFUSALS, (tool.__name__, result)
        assert result["self_ownership"]["established"] is True, (tool.__name__, result)
        assert result["self_ownership"]["same_member"] is True
        assert result["self_ownership"]["self_signal"] == "edit_controls"
        assert world.navigations == [SELF_PROFILE_URL, SELF_PROFILE_EDIT_INTRO_URL]
        assert result["pages_loaded"] == 2
        assert await world.clicks() == 0
        await world.page.close()


async def test_the_editor_gate_refuses_every_other_landing_and_names_what_it_saw(chromium, monkeypatch):
    """THE CONTROLS. Another member's real profile, landed the way the new
    landing lands, draws no edit control for its member: refused, retried once
    as an unread answer, the editor never loaded -- and the refusal names what
    it saw, in integers and closed words, never the landing. The REAL new
    landing at ``/in/y/``: its four edit controls belong to a member the url
    does not name -- ambiguous, refused at once, never retried."""
    result, world = await _drive(
        chromium, monkeypatch, _profile(_html(OTHER_MEMBERS[1])), linkedin_profile_editor_fields
    )
    assert result.get("refused") == "self_assertion_unreadable", result
    assert "fields" not in result and result["self_ownership"]["established"] is False
    assert world.navigations == [SELF_PROFILE_URL, SELF_PROFILE_URL], world.navigations
    saw = result.get("self_evidence")
    assert saw is not None, result
    assert saw["url_marker"] == "absent"
    assert saw["landed_on_member_path"] is True and saw["structure_read"] is True
    assert tuple(saw[name] for name in COUNTS) == (0, 0, 0), saw
    assert "/in/x" not in repr(result)
    await world.page.close()

    result, world = await _drive(
        chromium,
        monkeypatch,
        _profile(_html(NEW_LANDING), LANDED_ELSEWHERE),
        linkedin_profile_editor_fields,
    )
    assert result.get("refused") == "self_profile_ambiguous", result
    assert "fields" not in result
    assert result["self_evidence"]["edit_routes_on_another_member"] == 4, result
    assert world.navigations == [SELF_PROFILE_URL], world.navigations
    assert result["pages_loaded"] == 1
    assert "/in/y" not in repr(result)
    await world.page.close()

    # A PLAIN LINK TO THE MEMBER'S OWN EDITOR, no accessible name, inside
    # another member's real profile: an edit ROUTE, not a CONTROL -- counted,
    # named in the refusal, and it establishes nothing.
    result, world = await _drive(
        chromium,
        monkeypatch,
        _profile(_with_a_plain_link_to_its_own_editor(_html(OTHER_MEMBERS[1]))),
        linkedin_profile_editor_fields,
    )
    assert result.get("refused") == "self_assertion_unreadable", result
    assert tuple(result["self_evidence"][name] for name in COUNTS) == (0, 1, 0), result
    assert world.navigations == [SELF_PROFILE_URL, SELF_PROFILE_URL]


# ---------------------------------------------------------------------------
# 3. C1 of the authorship check in linkedin_my_activity_items
# ---------------------------------------------------------------------------


async def test_c1_of_the_authorship_check_holds_on_the_new_landing(chromium, monkeypatch):
    """RED BEFORE THE FIX: refused ``self_assertion_unreadable`` after two
    loads, the rail never read.

    * The landing as captured: C1 holds on the first load, and the refusal
      comes from the RAIL -- the tracked copy's labels are all ``x``, so no
      overflow control carries an author. C2's refusal, not C1's.
    * The landing with a synthetic rail of his items in ``main``: every
      condition holds and his item keys come back.
    * THE CONTROL: the same rail inside another member's real profile -- C1
      does not hold and no item key is published.
    """
    result, world = await _drive(
        chromium, monkeypatch, _profile(_html(NEW_LANDING)), linkedin_my_activity_items
    )
    assert result.get("refused") == "no_overflow_controls", result
    assert result["authorship"]["self_assertion_present"] is True, result
    assert world.navigations == [SELF_PROFILE_URL] and result["pages_loaded"] == 1
    await world.page.close()

    result, world = await _drive(
        chromium,
        monkeypatch,
        _profile(_with_his_rail(_html(NEW_LANDING))),
        linkedin_my_activity_items,
    )
    assert result.get("refused") is None, result
    assert result["items"] == [rail.HIS_ITEM_ONE, rail.HIS_ITEM_TWO], result
    assert result["authorship"]["established"] is True
    assert result["authorship"]["self_signal"] == "edit_controls"
    assert result["pages_loaded"] == 1
    await world.page.close()

    result, world = await _drive(
        chromium,
        monkeypatch,
        _profile(_with_his_rail(_html(OTHER_MEMBERS[0]))),
        linkedin_my_activity_items,
    )
    assert result.get("refused") == "self_assertion_unreadable", result
    assert "items" not in result


# ---------------------------------------------------------------------------
# 4. The census's item veto, the fourth site on the loader
# ---------------------------------------------------------------------------


async def test_the_census_item_veto_reads_his_rail_on_the_new_landing(chromium, monkeypatch):
    """RED BEFORE THE FIX: the census refused ``self_assertion_unreadable``.
    Now the veto reads his rail, finds the item named, and the census loads
    the item's page -- one profile load, then the item. THE CONTROL: on
    another member's profile the veto refuses and the item page is never
    loaded."""

    async def census() -> Any:
        return await linkedin_surface_census("feed_item", item=rail.HIS_ITEM_ONE)

    served = {
        SELF_PROFILE_URL: (LANDED, _with_his_rail(_html(NEW_LANDING))),
        ITEM_PAGE: (ITEM_PAGE, "<!doctype html><html><body><main></main></body></html>"),
    }
    result, world = await _drive(chromium, monkeypatch, served, census)
    assert result.get("refused") is None, result
    assert result["aimed_at"]["verified"] is True, result
    assert world.navigations == [SELF_PROFILE_URL, ITEM_PAGE], world.navigations
    assert result["pages_loaded"] == 2
    await world.page.close()

    served[SELF_PROFILE_URL] = (LANDED, _with_his_rail(_html(OTHER_MEMBERS[0])))
    result, world = await _drive(chromium, monkeypatch, served, census)
    assert result.get("refused") == "self_assertion_unreadable", result
    assert ITEM_PAGE not in world.navigations


# ---------------------------------------------------------------------------
# 5. The press gate
# ---------------------------------------------------------------------------


async def _counters() -> dict[str, int]:
    return {"invitations": 0, "messaging": 0, "off_state": 3}


async def test_the_press_gate_sees_his_profile_on_the_new_landing(chromium):
    """RED BEFORE THE FIX: ``address_not_admitted``, terminal -- the gate read
    the landed member path and found no marker. Now the page is admitted as
    ``/in/me/``'s landing and reaches its per-control judgements
    (IN-ME-NO-BLANKET-BAR), which exist for his profile alone. Nothing is
    pressed: neither control is judged a disclosure.

    THE CONTROLS: another member's real profile, the real landing under a
    path its edit controls do not name, and another member's profile carrying
    a plain link to its own editor (a route with no accessible name, which is
    not a control) are refused exactly as before."""
    world = await _served(chromium, _html(NEW_LANDING), LANDED)
    for shape, reason in (
        ("[aria-haspopup]", "control_judged_an_action"),
        ("[aria-expanded]", "control_not_judged"),
    ):
        verdict = await press.disclose(world.page, shape=shape, read_counters=_counters)
        assert verdict.get("refused") == reason, (shape, verdict)
    assert await world.clicks() == 0
    await world.page.close()

    for markup_path, landed, derive in (
        (OTHER_MEMBERS[0], LANDED, None),
        (OTHER_MEMBERS[1], LANDED, None),
        (NEW_LANDING, LANDED_ELSEWHERE, None),
        # what a member's own text could draw: a plain link to their editor
        (OTHER_MEMBERS[1], LANDED, _with_a_plain_link_to_its_own_editor),
    ):
        markup = _html(markup_path) if derive is None else derive(_html(markup_path))
        world = await _served(chromium, markup, landed)
        verdict = await press.disclose(world.page, shape="[aria-expanded]", read_counters=_counters)
        assert verdict.get("refused") == "address_not_admitted", (markup_path.name, landed, verdict)
        assert verdict["reachable_by_this_route"] is False
        assert await world.clicks() == 0
        await world.page.close()


async def test_the_pure_press_gate_takes_the_structural_reading_and_says_so(chromium):
    """``check_address`` with the reading the gate takes says it admitted the
    page AS his landing, never as the allowlist's own address; without one it
    is the url-only gate it always was."""
    from linkedin_server import self_profile

    world = await _served(chromium, _html(NEW_LANDING), LANDED)
    reading = await self_profile.read_edit_routes(world.page, LANDED)
    assert press.check_address(LANDED)["refused"] == "address_not_admitted"
    assert press.check_address(LANDED, edit_routes=reading) == {
        "pressed": False,
        "admitted": True,
        "self_landing": True,
    }
    assert press.admitted_address(LANDED, edit_routes=reading) == press.SELF_PROFILE_ADDRESS


# ---------------------------------------------------------------------------
# 6. The live harness's two self-profile steps
# ---------------------------------------------------------------------------


class _Reached(Exception):
    """Raised by a stand-in for the step AFTER the self check."""


async def test_the_live_harness_sees_his_profile_on_the_new_landing(chromium, monkeypatch, tmp_path):
    """RED BEFORE THE FIX: ``_in_me`` raised ``self_assertion_not_true`` and
    ``_in_me_more`` stopped ``not_on_his_profile``. With no stylesheet both of
    the top card's bars draw, so ``_in_me_more`` now stops at the opener rule
    instead -- AFTER seeing his profile, with nothing pressed. THE CONTROL:
    another member's real profile still stops at ``not_on_his_profile``."""

    async def reached(_page: Any, _where: str) -> None:
        raise _Reached()

    monkeypatch.setattr(harness, "_health", reached)
    # The harness's own state goes to the test's directory, as its own tests
    # direct it (``quick`` in tests/test_live_lane_session_2_harness.py).
    monkeypatch.setattr(harness, "STATE", tmp_path)
    monkeypatch.setattr(harness, "SHAPE_KEY_FILE", tmp_path / "shape.key")

    async def profile_step() -> Any:
        return await harness._in_me(False)

    with pytest.raises(_Reached):
        await _drive(chromium, monkeypatch, _profile(_html(NEW_LANDING)), profile_step)

    for markup_path, expected_stop in ((NEW_LANDING, "opener_not_exactly_one"), (OTHER_MEMBERS[0], "not_on_his_profile")):
        world = await _served(chromium, _html(markup_path), LANDED)

        class _Served:
            @asynccontextmanager
            async def session(self, page: Any = world.page):
                yield page

        monkeypatch.setattr(harness, "BROWSER", _Served())
        result = await harness._in_me_more(False)
        assert result.get("stopped") == expected_stop, (markup_path.name, result)
        assert await world.clicks() == 0
        await world.page.close()
