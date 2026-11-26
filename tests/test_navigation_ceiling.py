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
    assert "already made 3 page load(s)" in message and "its ceiling is 3" in message
    assert "a /jobs/ page" in message, message
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
    """The live runner's and the probes' path: their own ledger, not this."""
    browser = browser_module.LinkedInBrowser()
    page = FakePage()
    for _ in range(5):
        await browser.goto(page, FEED)
    assert len(page.gotos) == 5 and call_ceiling.made() is None


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


def test_spend_refuses_with_the_ceiling_error_and_counts_the_loads():
    with call_ceiling.per_call(2):
        call_ceiling.spend(FEED)
        call_ceiling.spend(FEED)
        assert call_ceiling.made() == 2
        with pytest.raises(NavigationCeilingError):
            call_ceiling.spend(FEED)
        assert call_ceiling.made() == 2
    assert call_ceiling.made() is None


def test_the_real_server_arms_the_ceiling_on_every_tool_call():
    assert [m for m in server.mcp.middleware if isinstance(m, call_ceiling.PerCallCeiling)], \
        server.mcp.middleware


def test_the_ceiling_is_the_measured_maximum_and_the_people_bound_is_its_own():
    assert config.MAX_NAVIGATIONS_PER_CALL == 3
    assert config.PAGE_AND_ITS_FALLBACK == 2
    assert call_ceiling.MAX_FAN_OUT_LOADS == jobfilter.MAX_LOCATIONS == 5


def test_the_fan_out_has_one_caller_and_it_is_the_search_over_its_places():
    callers = []
    for path in sorted((REPO / "linkedin_server").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and (
                        (isinstance(node.func, ast.Attribute) and node.func.attr == "allow_fan_out")
                        or (isinstance(node.func, ast.Name) and node.func.id == "allow_fan_out")):
                    callers.append((path.name, fn.name, ast.unparse(node.args[0])))
    assert callers == [("server.py", "linkedin_search_jobs", "len(places)")], callers


def test_goto_spends_before_the_rate_slot_and_the_page():
    """Read with ast: the spend is the first thing after the doors."""
    tree = ast.parse((REPO / "linkedin_server" / "browser.py").read_text(encoding="utf-8"))
    goto = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "goto")
    order = [ast.unparse(s) for s in goto.body if not isinstance(s, ast.Expr)
             or not isinstance(s.value, ast.Constant)]
    spend = next(i for i, s in enumerate(order) if "call_ceiling.spend(url)" in s)
    slot = next(i for i, s in enumerate(order) if "wait_for_rate_slot" in s)
    assert spend < slot, order[:4]


def test_no_statement_claims_a_lower_ceiling():
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert "One page load per tool call" not in readme
    assert "At most three page loads per tool call" in readme
    assert "linkedin_search_jobs" in readme.split("At most three page loads per tool call", 1)[1][:900]
    source = (REPO / "linkedin_server" / "config.py").read_text(encoding="utf-8")
    doc = source.split("MAX_NAVIGATIONS_PER_CALL = ", 1)[0].rsplit("\n\n", 1)[-1]
    assert "ENFORCED" in doc and "call_ceiling" in doc, doc
