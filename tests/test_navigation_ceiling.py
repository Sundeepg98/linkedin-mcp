"""NAVIGATION-CEILING-MADE-TRUE: at most three page loads per tool call, enforced.

Ruled 2026-11-26 (lane pace20's first question). ``MAX_NAVIGATIONS_PER_CALL``
was documented as a ceiling of 2, enforced nowhere, while 31 tools reached 3.
It is the measured maximum now, 3, and ``LinkedInBrowser.goto`` enforces it
through ``linkedin_server/call_ceiling.py``. The record is
``_audit/2026-11-26-infra26.md``, section 2.

RED FIRST: a planted tool asking for a fourth load in ONE MCP tool call is
refused before the fourth load reaches the page, and the refusal names what
it saw. On the tree before this lane, all four loads reached the page.
The controls: exactly three pass; outside a tool call nothing is counted,
which is the live runner's and the probes' path; the one declared fan-out
(``linkedin_search_jobs``' places) is capped at ``jobfilter.MAX_LOCATIONS``
and has one caller; the real server registers the ceiling.
"""
from __future__ import annotations

import ast
import contextlib
import json
from pathlib import Path

import pytest
from fastmcp import Client, FastMCP

from linkedin_server import browser as browser_module
from linkedin_server import call_ceiling, config, jobfilter, server
from linkedin_server.errors import LinkedInReaderError, NavigationCeilingError
from tests.conftest import FakePage

REPO = Path(__file__).resolve().parent.parent
FEED = "https://www.linkedin.com/feed/"
JOBS = "https://www.linkedin.com/jobs/search/?keywords=example"


def _planted_app(urls, *, fan_out=None):
    """A throwaway server with the real middleware and ONE planted tool that
    loads ``urls`` through a real LinkedInBrowser over a fake page."""
    browser = browser_module.LinkedInBrowser()
    page = FakePage()
    app = FastMCP("planted")
    app.add_middleware(call_ceiling.PerCallCeiling())

    @app.tool()
    async def planted() -> dict:
        try:
            if fan_out is not None:
                call_ceiling.allow_fan_out(fan_out)
            for url in urls:
                await browser.goto(page, url)
        except LinkedInReaderError as exc:
            return server._error(exc)
        return {"loads": len(page.gotos)}

    return app, page


async def _call(app) -> dict:
    async with Client(app) as client:
        result = await client.call_tool("planted", {})
    return json.loads(result.content[0].text)


async def test_RED_FIRST_a_planted_fourth_navigation_is_refused_before_it_loads():
    app, page = _planted_app([FEED, FEED, FEED, JOBS])
    got = await _call(app)
    assert page.gotos == [FEED, FEED, FEED], "the fourth load reached the page"
    assert got["error"] == "navigation_ceiling", got
    message = got["message"]
    assert "the tool call planted has already made 3 page load(s)" in message, message
    assert "its ceiling is 3" in message and "a /jobs/ page" in message, message
    assert "keywords" not in message and JOBS not in message, "the refusal named the address"


async def test_THIS_CONTROL_CAN_PASS_three_loads_in_one_call_are_allowed():
    app, page = _planted_app([FEED, JOBS, FEED])
    assert await _call(app) == {"loads": 3}
    assert len(page.gotos) == 3


async def test_each_tool_call_gets_its_own_budget():
    app, page = _planted_app([FEED, FEED, FEED])
    assert await _call(app) == {"loads": 3}
    assert await _call(app) == {"loads": 6}, "a second call inherited the first one's count"


async def test_outside_a_tool_call_nothing_is_counted():
    """The live runner's and the probes' path: their own ledger (40 loads,
    20 s apart), not this. Seven loads, the most one phase of session 11's
    runner made in one browser session (its own pages), all go through."""
    browser = browser_module.LinkedInBrowser()
    page = FakePage()
    for _ in range(7):
        await browser.goto(page, FEED)
    assert len(page.gotos) == 7 and call_ceiling.made() is None


async def test_the_declared_fan_out_is_capped_at_the_search_places_ceiling():
    app, page = _planted_app([JOBS] * 6, fan_out=jobfilter.MAX_LOCATIONS)
    got = await _call(app)
    assert len(page.gotos) == jobfilter.MAX_LOCATIONS == 5
    assert got["error"] == "navigation_ceiling" and "declared fan-out of 5" in got["message"]
    app, page = _planted_app([JOBS] * 6, fan_out=50)
    await _call(app)
    assert len(page.gotos) == call_ceiling.MAX_FAN_OUT_LOADS == 5, "the fan-out passed its cap"


def test_a_fan_out_outside_a_tool_call_does_nothing_and_never_lowers_a_budget():
    assert call_ceiling.allow_fan_out(5) == 0
    with call_ceiling.per_call(3):
        assert call_ceiling.allow_fan_out(1) == 3
        assert call_ceiling.allow_fan_out(4) == 4
        assert call_ceiling.allow_fan_out(2) == 4


def test_count_load_refuses_with_the_ceiling_error_and_counts_the_loads():
    with call_ceiling.per_call(2):
        call_ceiling.count_load(FEED)
        call_ceiling.count_load(FEED)
        assert call_ceiling.made() == 2
        with pytest.raises(NavigationCeilingError):
            call_ceiling.count_load(FEED)
        assert call_ceiling.made() == 2
    assert call_ceiling.made() is None


def test_the_real_server_arms_the_ceiling_on_every_tool_call():
    assert [m for m in server.mcp.middleware if isinstance(m, call_ceiling.PerCallCeiling)], \
        server.mcp.middleware


class _Reached(Exception):
    """Raised by the probe budget, so no tool body ever runs in the census."""


async def tools_that_reach_the_ceiling(app, monkeypatch) -> tuple[set, set]:
    """(every tool the server lists, the tools whose call armed a budget).

    Each tool is called through a real fastmcp Client with no arguments. The
    budget the middleware arms is replaced by a probe that records the tool
    and raises before ``call_next``. fastmcp runs middleware before it looks
    the tool up or validates its arguments, so a tool that goes through the
    ceiling never runs its body. A tool that did NOT go through it would run;
    the browser's start is made to raise, so even then nothing launches."""
    reached: set = set()

    @contextlib.contextmanager
    def probe(ceiling=config.MAX_NAVIGATIONS_PER_CALL, tool=None):
        reached.add(tool)
        raise _Reached(tool)
        yield  # pragma: no cover

    async def no_browser(*args, **kwargs):
        raise RuntimeError("a tool reached the browser without a budget")

    monkeypatch.setattr(call_ceiling, "per_call", probe)
    monkeypatch.setattr(browser_module.BROWSER, "start", no_browser)
    async with Client(app) as client:
        listed = {t.name for t in await client.list_tools()}
        for name in sorted(listed):
            await client.call_tool(name, {}, raise_on_error=False)
    return listed, reached


async def test_every_registered_tool_goes_through_the_ceiling(monkeypatch):
    """A tool registered by any path the served server knows is called with a
    budget armed; one that dodged the middleware would be listed and not
    reached."""
    listed, reached = await tools_that_reach_the_ceiling(server.mcp, monkeypatch)
    assert len(listed) > 50, "the census listed only %d tools" % len(listed)
    assert sorted(listed - reached) == [], "tools that dodge the ceiling"


async def test_THIS_CONTROL_CAN_FAIL_a_server_without_the_ceiling_is_caught(monkeypatch):
    bare = FastMCP("bare")

    @bare.tool()
    async def harmless() -> dict:
        return {}

    listed, reached = await tools_that_reach_the_ceiling(bare, monkeypatch)
    assert sorted(listed - reached) == ["harmless"], (listed, reached)


def fastmcp_constructions(sources) -> list:
    """(file, line) of every ``FastMCP(...)`` call in the given sources."""
    return [(rel, node.lineno) for rel, text in sources for node in ast.walk(ast.parse(text))
            if isinstance(node, ast.Call) and (
                (isinstance(node.func, ast.Name) and node.func.id == "FastMCP")
                or (isinstance(node.func, ast.Attribute) and node.func.attr == "FastMCP"))]


def _package_sources():
    paths = sorted((REPO / "linkedin_server").glob("*.py")) + [REPO / "linkedin.py"]
    return [(p.relative_to(REPO).as_posix(), p.read_text(encoding="utf-8")) for p in paths]


def test_the_package_builds_one_server_the_one_that_carries_the_ceiling():
    """A second FastMCP would be a registration path this middleware never
    sees. The entry points serve ``server.mcp``."""
    found = fastmcp_constructions(_package_sources())
    assert [rel for rel, _line in found] == ["linkedin_server/server.py"], found
    entry = (REPO / "linkedin.py").read_text(encoding="utf-8")
    assert "from linkedin_server.server import main, mcp" in entry and "serve_http(mcp)" in entry


def test_THIS_CONTROL_CAN_FAIL_a_second_server_is_found():
    planted = ("linkedin_server/planted.py",
               "from fastmcp import FastMCP\n\nside = FastMCP('side')\n")
    found = fastmcp_constructions(_package_sources() + [planted])
    assert [rel for rel, _line in found] == ["linkedin_server/server.py",
                                             "linkedin_server/planted.py"], found


async def test_the_login_wait_loads_no_page_per_poll(patched_navigation, monkeypatch):
    """linkedin_login and linkedin_login_browser are census-unbounded: their
    wait is a while loop, and the census cannot see that check_auth(warm=False)
    loads nothing. Measured here: the page loads stay the same, at most two
    (the opening check's warm load and the login page), however many times the
    loop polls. That is inside the ceiling of three."""
    from linkedin_server import auth as auth_module
    from tests.conftest import FakeResponse

    monkeypatch.setattr(auth_module, "LOGIN_POLL_S", 0.0)
    monkeypatch.setattr(auth_module, "LOGIN_RECHECK_S", 0.0)
    loads = {}
    for checks in (2, 6):
        monkeypatch.setattr(auth_module, "LOGIN_MAX_CHECKS", checks)
        patched_navigation.clear()
        page = FakePage(cookies={"li_at": "x"}, responses=[FakeResponse(401, "")],
                        default_response=FakeResponse(401, ""))
        result = await auth_module.login_via_browser(page, wait_seconds=0.3)
        assert result["checks_run"] == checks, result
        loads[checks] = len(patched_navigation)
    assert loads[2] == loads[6] and 1 <= loads[6] <= 2, loads


def test_the_ceiling_is_the_measured_maximum_and_the_people_bound_is_its_own():
    assert config.MAX_NAVIGATIONS_PER_CALL == 3
    assert config.PAGE_AND_ITS_FALLBACK == 2
    assert call_ceiling.MAX_FAN_OUT_LOADS == jobfilter.MAX_LOCATIONS == 5


def fan_out_callers(sources) -> list:
    """(file, function, first argument) of every ``allow_fan_out`` call,
    whether called by name, as an attribute, or through ``getattr``."""
    callers = []
    for rel, text in sources:
        tree = ast.parse(text)
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                named = ((isinstance(f, ast.Attribute) and f.attr == "allow_fan_out")
                         or (isinstance(f, ast.Name) and f.id == "allow_fan_out"))
                by_getattr = (isinstance(f, ast.Call) and isinstance(f.func, ast.Name)
                              and f.func.id == "getattr" and len(f.args) >= 2
                              and isinstance(f.args[1], ast.Constant)
                              and f.args[1].value == "allow_fan_out")
                if named or by_getattr:
                    first = ast.unparse(node.args[0]) if node.args else ""
                    callers.append((rel.rsplit("/", 1)[-1], fn.name, first))
    return callers


def test_the_fan_out_has_one_caller_and_it_is_the_search_over_its_places():
    callers = fan_out_callers(_package_sources())
    assert callers == [("server.py", "linkedin_search_jobs", "len(places)")], callers


@pytest.mark.parametrize("spelling", [
    "call_ceiling.allow_fan_out(9)",
    "allow_fan_out(9)",
    "getattr(call_ceiling, 'allow_fan_out')(9)",
])
def test_THIS_CONTROL_CAN_FAIL_a_planted_second_caller_is_found(spelling):
    planted = ("linkedin_server/planted.py",
               "from linkedin_server import call_ceiling\n"
               "from linkedin_server.call_ceiling import allow_fan_out\n\n\n"
               "async def linkedin_planted():\n    %s\n" % spelling)
    callers = fan_out_callers(_package_sources() + [planted])
    assert ("planted.py", "linkedin_planted", "9") in callers, callers
    assert callers != [("server.py", "linkedin_search_jobs", "len(places)")]


def test_goto_counts_the_load_before_the_rate_slot_and_the_page():
    """Read with ast: the count is the first thing after the doors."""
    tree = ast.parse((REPO / "linkedin_server" / "browser.py").read_text(encoding="utf-8"))
    goto = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "goto")
    order = [ast.unparse(s) for s in goto.body if not isinstance(s, ast.Expr)
             or not isinstance(s.value, ast.Constant)]
    counted = next(i for i, s in enumerate(order) if "call_ceiling.count_load(url)" in s)
    slot = next(i for i, s in enumerate(order) if "wait_for_rate_slot" in s)
    assert counted < slot, order[:4]


#: The ruled wording (NAVIGATION-CEILING-PER-TOOL-CALL, 2026-11-26).
RULED_SENTENCE = ("at most 3 page loads per tool call, each at least 20 s apart; "
                  "a job search across N places loads N, at most 5")


def test_no_statement_claims_a_lower_ceiling():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    flat = " ".join(readme.split())
    assert "One page load per tool call" not in readme
    assert flat.count(RULED_SENTENCE) >= 2, "the risk table and the rate bullet carry it"
    source = (REPO / "linkedin_server" / "config.py").read_text(encoding="utf-8")
    doc = source.split("MAX_NAVIGATIONS_PER_CALL = ", 1)[0].rsplit("\n\n", 1)[-1]
    assert "ENFORCED" in doc and "call_ceiling" in doc, doc
