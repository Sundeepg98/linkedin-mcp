"""At most three page loads per tool call: the ceiling, enforced.

NAVIGATION-CEILING-MADE-TRUE (ruled 2026-11-26, lane pace20's first
question), built as NAVIGATION-CEILING-PER-TOOL-CALL (the lead's ruling on
lane infra26's measurement; record ``_audit/2026-11-26-infra26.md`` section 2).
``config.MAX_NAVIGATIONS_PER_CALL`` was DOCUMENTED as a ceiling ("Nothing may
exceed this ceiling") at 2, and enforced nowhere, while 31 tools reached 3.
The measured maximum is now the ceiling, and this module enforces it.

HOW. Every MCP ``tools/call`` runs inside :class:`PerCallCeiling`, a fastmcp
middleware that server.py registers once. It arms a per-call budget in a
context variable. ``browser.LinkedInBrowser.goto`` counts each load against
that budget (:func:`count_load`, not "spend": that verb is the grant
model's, held to ``writes.perform`` alone) BEFORE it waits for the rate slot
or touches the page. The load that would exceed the budget is REFUSED there
with a :class:`~linkedin_server.errors.NavigationCeilingError` that names
what it saw: the tool, the loads already made, the ceiling, and the refused
page's family (its first path segment, never the address).

WHAT IS NOT A TOOL CALL IS NOT COUNTED. The live lane's runner and the
tracked probes drive ``BROWSER.goto`` themselves, many loads to one browser
session, under their own ledger (LIVE-BUDGET-40-LOADS). Tests that call a
tool function directly are not counted either. The scope is the MCP tool
call because that is what the ruling bounds. A per-SESSION counter was
measured wrong first: the runner loads five company tabs inside one session.

THE ONE DECLARED EXCEPTION is ``linkedin_search_jobs`` with ``locations``:
one search per place, ``jobfilter.MAX_LOCATIONS`` (5) at most, the fan-out its
docstring prices. That tool, and only that tool (an AST test holds the call
site), calls :func:`allow_fan_out` with its place count before its first load.
The allowance can raise this call's budget to at most ``MAX_LOCATIONS``, never
past it, and outside a tool call it does nothing.
"""
from __future__ import annotations

import contextvars
import re
from contextlib import contextmanager
from typing import Any, Iterator, Optional
from urllib.parse import urlsplit

from fastmcp.server.middleware import Middleware

from linkedin_server.config import MAX_NAVIGATIONS_PER_CALL
from linkedin_server.errors import NavigationCeilingError
from linkedin_server.jobfilter import MAX_LOCATIONS

#: The most loads a declared fan-out may raise one call's budget to.
MAX_FAN_OUT_LOADS = MAX_LOCATIONS


#: A tool's name as the refusal prints it: the server's own closed vocabulary
#: (``linkedin_*``). Anything else a client sends is not echoed.
_TOOL_NAME = re.compile(r"^[A-Za-z0-9_]{1,64}$")


class _Budget:
    __slots__ = ("ceiling", "fan_out", "made", "tool")

    def __init__(self, ceiling: int, tool: Optional[str] = None) -> None:
        self.ceiling = int(ceiling)
        self.fan_out = 0
        self.made = 0
        self.tool = tool if isinstance(tool, str) and _TOOL_NAME.match(tool) else None

    @property
    def limit(self) -> int:
        return max(self.ceiling, self.fan_out)


_BUDGET: contextvars.ContextVar[Optional[_Budget]] = contextvars.ContextVar(
    "linkedin_navigation_budget", default=None
)


@contextmanager
def per_call(ceiling: int = MAX_NAVIGATIONS_PER_CALL,
             tool: Optional[str] = None) -> Iterator[None]:
    """Arm one tool call's budget for the duration of the block."""
    token = _BUDGET.set(_Budget(ceiling, tool))
    try:
        yield
    finally:
        _BUDGET.reset(token)


def allow_fan_out(loads: int) -> int:
    """Raise THIS call's budget to ``loads``, capped at :data:`MAX_FAN_OUT_LOADS`.

    Returns the budget granted, or 0 outside a tool call. Never lowers it."""
    budget = _BUDGET.get()
    if budget is None:
        return 0
    budget.fan_out = max(budget.fan_out, min(int(loads), MAX_FAN_OUT_LOADS))
    return budget.limit


def count_load(url: str) -> None:
    """Count one page load against the armed budget, or refuse it unloaded.

    Called by ``LinkedInBrowser.goto`` after its door and before its rate slot.
    Outside a tool call there is no budget and nothing is counted."""
    budget = _BUDGET.get()
    if budget is None:
        return
    if budget.made >= budget.limit:
        family = urlsplit(url).path.strip("/").split("/")[0] or "root"
        fan_out = (" with this call's declared fan-out of %d" % budget.fan_out
                   if budget.fan_out > budget.ceiling else "")
        who = ("the tool call %s" % budget.tool) if budget.tool else "this tool call"
        raise NavigationCeilingError(
            "navigation refused before loading: %s has already made "
            "%d page load(s) and its ceiling is %d (MAX_NAVIGATIONS_PER_CALL = %d%s). "
            "The refused load was to a /%s/ page."
            % (who, budget.made, budget.limit, budget.ceiling, fan_out, family)
        )
    budget.made += 1


def made() -> Optional[int]:
    """Loads this tool call has made so far, or None outside a tool call."""
    budget = _BUDGET.get()
    return None if budget is None else budget.made


class PerCallCeiling(Middleware):
    """Every ``tools/call`` gets its own budget of MAX_NAVIGATIONS_PER_CALL.

    fastmcp runs this before the tool is looked up or its arguments are
    validated, so no registered tool reaches its body without a budget armed;
    ``tests/test_navigation_ceiling.py`` calls every registered tool through
    it to hold that."""

    async def on_call_tool(self, context: Any, call_next: Any) -> Any:
        tool = getattr(getattr(context, "message", None), "name", None)
        with per_call(MAX_NAVIGATIONS_PER_CALL, tool=tool):
            return await call_next(context)
