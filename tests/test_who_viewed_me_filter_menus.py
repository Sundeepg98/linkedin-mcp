"""``linkedin_who_viewed_me(open_filter_menus=True)`` -- the gate's first package caller.

Added 2026-09-23 (`_audit/2026-09-23-readers-four-rows.md`). The tool opens
each filter pill on his profile-views analytics through ``press.disclose`` and
reports what the pill disclosed, in the gate's closed reading. These tests pin
the CALLER's half of that contract, with the gate replaced by a recorder:

* nothing is pressed unless the caller asked for it;
* the pills are chosen by STRUCTURE inside ``main`` -- ``role="button"``,
  visible, wrapping a ``<label>`` -- never by a label's text, and never by a
  page-wide index (page-wide, the first matches are the nav);
* the press is always scoped to ``main`` and always names the reading key;
* it stops at the first press the gate does not permit;
* it presses NOTHING when the counters that must price it do not read;
* what it publishes is the package's own words and integers.

No browser, no network. The gate's own behaviour is tested in
``tests/test_press.py`` and ``tests/test_press_open_reading.py``.
"""
from __future__ import annotations

import pytest

from linkedin_server import press, server

# ---------------------------------------------------------------------------
# A page made of structure, and nothing else
# ---------------------------------------------------------------------------


class _Count:
    def __init__(self, n):
        self.n = n

    async def count(self):
        return self.n


class _Control:
    def __init__(self, role, visible, labels):
        self.role = role
        self.visible = visible
        self.labels = labels

    async def get_attribute(self, name):
        assert name == "role", name
        return self.role

    async def is_visible(self):
        return self.visible

    def locator(self, selector):
        assert selector == "label", selector
        return _Count(self.labels)


class _Candidates:
    def __init__(self, controls):
        self.controls = controls

    async def count(self):
        return len(self.controls)

    def nth(self, index):
        return self.controls[index]


class _Main:
    def __init__(self, controls):
        self.controls = controls

    def locator(self, selector):
        assert selector == "[aria-expanded]", selector
        return _Candidates(self.controls)


class _Page:
    """``main`` holds, in order: a plain button (the info control), three
    pills, and a label-less footer dropdown -- the capture's shape."""

    url = "https://www.linkedin.com/analytics/profile-views/"

    def __init__(self, controls=None):
        self.controls = controls or [
            _Control(None, True, 0),      # info button: not role=button
            _Control("button", True, 1),  # pill
            _Control("button", True, 1),  # pill
            _Control("button", True, 1),  # pill
            _Control("button", True, 0),  # footer dropdown: no label
        ]

    def locator(self, selector):
        assert selector == "main", (
            "the pills must be looked for inside main; page-wide, the first "
            "disclosure controls are the nav"
        )
        return _Main(self.controls)


def _permitted(appeared=("time_range",), value=None):
    terms = {term: {"numeral": "no_digit_run", "value": None} for term in appeared}
    if value is not None:
        terms[appeared[0]] = {"numeral": "plain_digits", "value": value}
    return {
        "pressed": True,
        "permitted": True,
        "read_at_both_ends": ["headline_viewers"],
        "witness": {"disclosed": True, "moved": ["expanded_true"]},
        "reading": {
            "key": server.PROFILE_VIEWS_MENU_READING,
            "before": {"read": True, "terms": {}},
            "open": {"read": True, "terms": terms},
            "appeared": list(appeared),
            "held": [],
            "gone": [],
            "new_lines": 4,
        },
    }


@pytest.fixture
def gate(monkeypatch):
    """Replace the gate with a recorder; each call pops the next verdict."""
    calls: list[dict] = []
    verdicts: list[dict] = []

    async def fake_disclose(page, **kwargs):
        calls.append(kwargs)
        return verdicts.pop(0) if verdicts else _permitted()

    monkeypatch.setattr(press, "disclose", fake_disclose)
    return calls, verdicts


@pytest.fixture
def counters(monkeypatch):
    """A reader whose first value set is controllable."""
    state = {"values": {"headline_viewers": 27}}

    async def factory(_page):
        async def read():
            return dict(state["values"])

        return read

    monkeypatch.setattr(server, "_profile_views_press_counters", factory)
    return state


# ---------------------------------------------------------------------------
# 1. WHICH CONTROLS, AND HOW THE GATE IS ASKED
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_each_pill_is_chosen_by_structure_inside_main(gate, counters):
    calls, _ = gate
    out = await server._open_profile_views_filter_menus(_Page())
    assert [call["index"] for call in calls] == [1, 2, 3], calls
    for call in calls:
        assert call["scope"] == "main", call
        assert call["shape"] == "[aria-expanded]", call
        assert call["reading"] == server.PROFILE_VIEWS_MENU_READING, call
        assert callable(call["read_counters"]), call
    assert out["pills_found"] == 3 and out["stopped"] is None, out
    assert [menu["pill"] for menu in out["menus"]] == [0, 1, 2], out


@pytest.mark.asyncio
async def test_an_invisible_control_is_never_a_pill(gate, counters):
    calls, _ = gate
    page = _Page([
        _Control("button", False, 1),   # hidden: a press could not land on it
        _Control("button", True, 1),
    ])
    await server._open_profile_views_filter_menus(page)
    assert [call["index"] for call in calls] == [1], calls


@pytest.mark.asyncio
async def test_it_stops_at_the_first_press_not_permitted(gate, counters):
    calls, verdicts = gate
    verdicts.extend([
        _permitted(),
        {"pressed": False, "refused": "not_restored", "reachable_by_this_route": True,
         "witness": {"disclosed": True, "moved": ["menus"]}},
    ])
    out = await server._open_profile_views_filter_menus(_Page())
    assert len(calls) == 2, "no third pill may be pressed on a page nobody classified"
    assert out["stopped"] == "pill 1 was not permitted", out
    assert out["menus"][1]["refused"] == "not_restored", out


@pytest.mark.asyncio
async def test_no_press_at_all_when_the_counters_do_not_read(gate, counters):
    """The gate would read these, CLICK, and only then refuse. So the caller
    refuses first, with nothing touched."""
    calls, _ = gate
    counters["values"] = {"headline_viewers": None}
    out = await server._open_profile_views_filter_menus(_Page())
    assert calls == [], calls
    assert out["stopped"] == "counters_unreadable_before_any_press", out
    assert out["menus"] == [], out


@pytest.mark.asyncio
async def test_never_more_pills_than_the_cap(gate, counters):
    calls, _ = gate
    page = _Page([_Control("button", True, 1) for _ in range(6)])
    out = await server._open_profile_views_filter_menus(page)
    assert len(calls) == server.PROFILE_VIEWS_MAX_PILLS, calls
    assert out["pills_found"] == 6, out


# ---------------------------------------------------------------------------
# 2. WHAT IS PUBLISHED
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_summary_is_the_packages_own_words_and_integers(gate, counters):
    _, verdicts = gate
    verdicts.append(_permitted(appeared=("recruiters", "time_range"), value=3))
    out = await server._open_profile_views_filter_menus(_Page())
    menu = out["menus"][0]
    assert set(menu) == {
        "pill", "permitted", "refused", "reachable_by_this_route", "disclosed",
        "witness_moved", "appeared", "held", "values", "new_lines",
        "read_at_both_ends",
    }, sorted(menu)
    assert menu["appeared"] == ["recruiters", "time_range"], menu
    assert menu["values"] == {"recruiters": 3}, menu
    terms = {term for term, _phrase in press.open_reading(
        server.PROFILE_VIEWS_MENU_READING)["phrases"]}
    assert set(menu["appeared"]) <= terms, menu
    assert "before" not in menu and "open" not in menu, (
        "the reading's per-moment detail is not copied through"
    )


# ---------------------------------------------------------------------------
# 3. THE TOOL: NOTHING PRESSED UNLESS ASKED, AND ONE LOAD EITHER WAY
# ---------------------------------------------------------------------------


@pytest.fixture
def tool_page(monkeypatch):
    """The tool, driven over a page whose reads are all stubbed."""
    from contextlib import asynccontextmanager

    from linkedin_server import browser as browser_module

    navigations: list[str] = []
    opened: list[object] = []
    fake = _Page()

    @asynccontextmanager
    async def fake_session():
        yield fake

    async def fake_goto(_page, url, **_kwargs):
        navigations.append(url)
        return url

    async def harvest(*_args, **_kwargs):
        return [{"href": "/in/placeholder-member/", "text": "A Viewer\nA headline\n2d ago"}]

    async def insights(_page):
        return {"headline": {"value": "27", "label": "Profile viewers"}}

    async def no_ids(_page, _rows):
        return None

    async def opener(page):
        opened.append(page)
        return {"pills_found": 3, "menus": [], "stopped": None}

    monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
    monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
    monkeypatch.setattr(server.dom, "harvest_linked_cards", harvest)
    monkeypatch.setattr(server.dom, "read_profile_views_insights", insights)
    monkeypatch.setattr(server, "_attach_recipient_ids", no_ids)
    monkeypatch.setattr(server, "_open_profile_views_filter_menus", opener)
    return navigations, opened


@pytest.mark.asyncio
async def test_the_default_call_opens_nothing(tool_page):
    navigations, opened = tool_page
    result = await server.linkedin_who_viewed_me(limit=25)
    assert opened == [], "the default call must be this tool exactly as it was"
    assert "filter_menus" not in result, sorted(result)
    assert result["pages_loaded"] == 1 and len(navigations) == 1, result


@pytest.mark.asyncio
async def test_asked_it_opens_the_pills_on_the_same_load(tool_page):
    navigations, opened = tool_page
    result = await server.linkedin_who_viewed_me(limit=25, open_filter_menus=True)
    assert len(opened) == 1, opened
    assert result["filter_menus"]["pills_found"] == 3, result["filter_menus"]
    assert result["pages_loaded"] == 1 and len(navigations) == 1, (
        "opening the pills loads no page"
    )


# ---------------------------------------------------------------------------
# 4. THE COUNTER READER THE PRESSES ARE PRICED WITH
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_counter_set_is_fixed_at_the_first_read(monkeypatch):
    """A badge that read at the first read stays in the set; if it stops
    reading it comes back None and the gate refuses -- a badge vanishing
    across a press is a change nobody can price. A badge that never read is
    never in the set. The headline is always in it."""
    badges = iter([
        {"pending": 0}, {"pending": None},
    ])
    unread = iter([{"unread": None}, {"unread": 5}])

    async def insights(_page):
        return {"headline": {"value": "1,234", "label": "x"}}

    async def nothing(_page):
        return {}

    monkeypatch.setattr(server.dom, "read_profile_views_insights", insights)
    monkeypatch.setattr(server.dom, "read_invitation_badge", nothing)
    monkeypatch.setattr(server.notify_cost, "read_notifications_badge", nothing)
    monkeypatch.setattr(server.shape, "invitation_badge", lambda _r: next(badges))
    monkeypatch.setattr(
        server.notify_cost, "notifications_badge", lambda _r: next(unread)
    )
    read = await server._profile_views_press_counters(object())
    first = await read()
    second = await read()
    assert first == {"headline_viewers": 1234, "invitations": 0}, first
    assert second == {"headline_viewers": 1234, "invitations": None}, second


def test_a_decorated_number_is_not_a_count():
    assert server._as_count("27") == 27
    assert server._as_count("1,234") == 1234
    for decorated in ("50%", "2K", "1.5", "", None, "twenty"):
        assert server._as_count(decorated) is None, decorated
