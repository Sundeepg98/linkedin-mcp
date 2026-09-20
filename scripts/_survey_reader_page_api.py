"""Which page API does each hazard-bucket reader actually touch?

The census says WHERE the coercions are. This says WHAT it would take to drive
each one offline, which is the difference between a site this wave can measure
and a site it can only file. A reader that only ever calls ``page.evaluate``
can be driven by a dict; one that walks ``page.locator(...).nth(i).inner_text()``
needs a locator double, and one that calls ``page.goto`` wants a browser.

Output is a table, and ``--json`` for the harness to consume.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts._census_page_coercions import census  # noqa: E402

PACKAGE = REPO / "linkedin_server"

#: Calling any of these means a browser, not a double.
NAVIGATIONAL = frozenset({"goto", "click", "fill", "set_input_files", "close",
                          "select_option", "keyboard", "wait_for_timeout"})


def _attr_chain(node: ast.AST) -> list[str]:
    out: list[str] = []
    while isinstance(node, (ast.Attribute, ast.Call, ast.Await, ast.Subscript)):
        if isinstance(node, ast.Attribute):
            out.append(node.attr)
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Await):
            node = node.value
        else:
            node = node.value
    if isinstance(node, ast.Name):
        out.append(node.id)
    return list(reversed(out))


def survey() -> list[dict[str, Any]]:
    wanted: dict[tuple[str, str], set[str]] = {}
    for row in census():
        if row["bucket"] == "PAGE_DERIVED":
            wanted.setdefault((row["module"], row["function"]), set())

    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            key = (path.name, fn.name)
            if key not in wanted:
                continue
            for node in ast.walk(fn):
                chain = _attr_chain(node) if isinstance(node, ast.Attribute) else []
                if len(chain) >= 2 and chain[0] == "page":
                    wanted[key].add(chain[1])
                # dom.<helper>(page, ...) -- the boundary this repo funnels through
                if isinstance(node, ast.Call):
                    c = _attr_chain(node.func)
                    if len(c) == 2 and c[0] == "dom":
                        wanted[key].add(f"dom.{c[1]}")

    out: list[dict[str, Any]] = []
    for (module, function), methods in sorted(wanted.items()):
        direct = {m for m in methods if not m.startswith("dom.")}
        via_dom = sorted(m for m in methods if m.startswith("dom."))
        if direct & NAVIGATIONAL:
            drivable = "browser"
        elif direct - {"evaluate"} or (not direct and not via_dom):
            drivable = "locator-double"
        else:
            drivable = "evaluate-double"
        out.append(
            {
                "module": module,
                "function": function,
                "page_methods": sorted(direct),
                "dom_helpers": via_dom,
                "drivable": drivable,
            }
        )
    return out


def main(argv: list[str]) -> int:
    rows = survey()
    if "--json" in argv:
        print(json.dumps(rows, indent=2))
        return 0
    buckets: dict[str, int] = {}
    for row in rows:
        buckets[row["drivable"]] = buckets.get(row["drivable"], 0) + 1
    print(f"{len(rows)} hazard-bucket readers")
    print()
    for name, count in sorted(buckets.items(), key=lambda kv: -kv[1]):
        print(f"  {name:18s} {count:3d}")
    print()
    for row in rows:
        methods = ",".join(row["page_methods"]) or "-"
        helpers = ",".join(h[4:] for h in row["dom_helpers"]) or "-"
        print(f"  {row['drivable']:16s} {row['module']:20s} {row['function']:32s}")
        print(f"      page: {methods}")
        print(f"      dom : {helpers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
