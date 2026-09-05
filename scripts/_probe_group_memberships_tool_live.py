"""``linkedin_group_memberships`` called LIVE, through the registry.

WHY THROUGH THE REGISTRY RATHER THAN THE FUNCTION. Calling the undecorated
body would exercise the code and prove nothing about the tool: three defects
in this repository's history lived in the wiring rather than in the reader,
and one of them shipped a write-capable tool that raised at its first guard
without ever loading a page while still issuing a confirm token. So this
resolves the tool BY NAME out of ``mcp`` and calls what a client would call.

**THE RUNNING HTTP SERVER CANNOT DO THIS.** It holds the code it started with,
so it has the previous tool count and cannot see this tool at all. Restarting
a server a dozen waves share, to prove one wave's work, is not a trade this
wave makes -- so the package is imported directly and the tool is invoked in
this process.

WHAT IS PRINTED. Counts, states and verdicts. **No identifier and no href.**
The module publishes identifiers on purpose -- a caller computing overlap
needs them -- and a transcript is not that caller. The operator's slug reached
a transcript three times before the output sink was added to the taint guard.

Usage::

    LINKEDIN_CDP_ATTACH_TIMEOUT_MS=120000 LINKEDIN_CDP_ATTACH=1 \\
        LINKEDIN_CDP_PORT=9224 venv/Scripts/python.exe \\
        scripts/_probe_group_memberships_tool_live.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server import config  # noqa: E402
from linkedin_server.server import mcp  # noqa: E402

TOOL = "linkedin_group_memberships"


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        return 2

    tools = {tool.name: tool for tool in await mcp.list_tools()}
    print(f"=== REGISTRY: {len(tools)} tools; {TOOL} present: {TOOL in tools}")
    if TOOL not in tools:
        return 1

    result = await mcp.call_tool(TOOL, {})
    payload = getattr(result, "structured_content", None) or result
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    if not isinstance(payload, dict):
        print(f"    UNEXPECTED PAYLOAD TYPE: {type(payload).__name__}")
        return 1

    print(f"\n=== ok={payload.get('ok')}  "
          f"pages_loaded={payload.get('pages_loaded')}  "
          f"redirected={payload.get('redirected')}")
    if not payload.get("ok"):
        print(f"    error: {payload.get('error')}")
        print(f"    why:   {payload.get('why') or payload.get('message')}")
        return 1

    print(f"    anchors {payload.get('anchors')}, controls "
          f"{payload.get('controls')}, row-scoped "
          f"{payload.get('rows_found')}, not row-scoped "
          f"{payload.get('rows_not_row_scoped')}, climbs exhausted "
          f"{payload.get('climbs_exhausted')}")
    print(f"    stopping widths: {payload.get('stopping_widths')}")
    memberships = dict(payload.get("memberships") or {})
    others = dict(payload.get("others") or {})
    overlap = dict(payload.get("overlap") or {})
    print(f"    MEMBERSHIPS  rows {memberships.get('rows')}, groups "
          f"{memberships.get('groups')}, DISTINCT "
          f"{memberships.get('distinct')}, refused "
          f"{memberships.get('refused')}")
    print(f"    OTHERS       rows {others.get('rows')}, groups "
          f"{others.get('groups')}, DISTINCT {others.get('distinct')}, "
          f"refused {others.get('refused')}")
    print(f"    in common {overlap.get('in_common')}, DISJOINT "
          f"{overlap.get('disjoint')}")
    print(f"    agrees with the four corroborating instruments: "
          f"{payload.get('agrees_with_corroborated')} "
          f"(they say {payload.get('corroborated_memberships')})")

    cost = dict(payload.get("cost") or {})
    print(f"\n=== COST: {cost.get('state')}  measured={cost.get('measured')}")
    for name, entry in sorted(dict(cost.get("counters") or {}).items()):
        print(f"    {name}: {entry}")
    print(f"    why: {cost.get('why')}")
    print(f"    certifies: {cost.get('certifies')}")
    print(f"    counter states ON the groups page: "
          f"{payload.get('counter_states_on_the_groups_page')}")

    # THE NAME CHECK, DONE OVER THE PAYLOAD RATHER THAN CLAIMED ABOUT IT.
    # Every string field is enumerated; the only strings that may carry a
    # variable part are the identifiers, and those are runs of ASCII digits by
    # ``groups.group_identifier``'s own refusal.
    ids = list(memberships.get("identifiers") or []) + list(
        others.get("identifiers") or []
    )
    non_numeric = [i for i in ids if not set(str(i)) <= set("0123456789")]
    print(f"\n=== IDENTIFIERS RETURNED: {len(ids)} -- "
          f"non-numeric among them: {len(non_numeric)} "
          "(a non-numeric segment is a SLUG and a slug is a NAME)")
    print("    NOT PRINTED HERE. The reader may publish them; a transcript "
          "is not the caller that needs them.")

    print("\n=== VERDICT")
    if memberships.get("distinct") != payload.get("corroborated_memberships"):
        print("    THE TOOL DISAGREES WITH FOUR INSTRUMENTS. That is a "
              "finding about THE TOOL, not about his account.")
        return 1
    if non_numeric:
        print("    A NON-NUMERIC IDENTIFIER CROSSED. Stop and read "
              "groups.group_identifier -- this should be impossible.")
        return 1
    if cost.get("state") == "degenerate" and cost.get("measured"):
        print("    A DEGENERATE COST REPORTED AS MEASURED. Contradiction.")
        return 1
    print("    SUCCESS PATH EXERCISED END TO END through the registry.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
