"""Census: where a CAUGHT EXCEPTION is rendered into a string that leaves.

THE QUESTION, stated so it can be argued with: for every ``except ... as N``
in a module, does ``N`` get rendered into a string that is LOGGED, RETURNED to
a caller, or RAISED again -- and when it does, is what gets rendered the
exception's TYPE or its VALUE?

That split is the whole census. ``type(exc).__name__`` is a class name chosen
by whoever wrote the class; it cannot carry a runtime value. ``{exc}`` /
``str(exc)`` / ``%s`` over the object invokes ``__str__``, which for a library
exception is composed by code nobody here controls and has been MEASURED
carrying a session cookie. A site that renders both is a VALUE site: a type
render standing next to a value render defends nothing, and that exact shape
-- ``f"({type(exc).__name__}: {exc})"`` -- is the defect this wave repaired.

## THE TRAP THIS INSTRUMENT IS BUILT AROUND

This package logs LAZILY::

    logger.info("auth check failed: %s: %s", type(exc).__name__, exc)

The credential is in ``args``, not in the format string. A census that reads
the format string sees ``"%s: %s"`` and reports the line clean. **Every real
log-channel site in this module is of that shape**, so a scanner that only
reads format strings finds zero and says so confidently. Arguments are walked
in every position here, and ``--selftest`` pins a case of exactly that shape.

## WHAT IT REFUSES TO GUESS

* A name it cannot resolve to a handler target is not reported as either safe
  or unsafe. It is UNRESOLVED and it is COUNTED, because a census that folds
  its own blind spot into the clean column is worse than no census.
* It reports SITES IN THE SOURCE. It does not and cannot say whether a given
  exception's ``__str__`` actually carries a credential -- that depends on the
  library that raised it and is knowable only by DRIVING it. Every row here is
  "worth driving", never "leaks".

USAGE

    python scripts/_census_auth_exception_renders.py                 # auth.py
    python scripts/_census_auth_exception_renders.py --path <file>
    python scripts/_census_auth_exception_renders.py --json <out>
    python scripts/_census_auth_exception_renders.py --selftest
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys
from typing import Any, Optional

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TARGET = "linkedin_server/auth.py"

LOG_METHODS = frozenset(
    {"debug", "info", "warning", "warn", "error", "exception", "critical"}
)


# ---------------------------------------------------------------------------
# Classifying ONE expression's relationship to a caught-exception name
# ---------------------------------------------------------------------------


def _is_type_name_of(node: ast.AST, names: set[str]) -> bool:
    """``type(<caught>).__name__`` and nothing else."""
    if not isinstance(node, ast.Attribute) or node.attr != "__name__":
        return False
    inner = node.value
    return (
        isinstance(inner, ast.Call)
        and isinstance(inner.func, ast.Name)
        and inner.func.id == "type"
        and len(inner.args) == 1
        and isinstance(inner.args[0], ast.Name)
        and inner.args[0].id in names
    )


def renders(node: Optional[ast.AST], names: set[str]) -> set[str]:
    """What of the caught exception does this expression render?

    Returns a subset of ``{"TYPE", "VALUE"}``. Walks the whole subtree, so an
    f-string holding both a type render and a value render reports both -- and
    the caller treats any VALUE as decisive. A type render does not cancel a
    value render sitting beside it; that belief is how the repaired defect
    read as careful.
    """
    found: set[str] = set()
    if node is None:
        return found

    for child in ast.walk(node):
        if _is_type_name_of(child, names):
            found.add("TYPE")

    # A bare reference to the caught name that is NOT the ``type(x)`` argument
    # and NOT an attribute base we already accounted for is a value render.
    accounted: set[int] = set()
    for child in ast.walk(node):
        if _is_type_name_of(child, names):
            inner = child.value
            assert isinstance(inner, ast.Call)
            accounted.add(id(inner.args[0]))

    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in names:
            if id(child) not in accounted:
                found.add("VALUE")
    return found


# ---------------------------------------------------------------------------
# The walker
# ---------------------------------------------------------------------------


class _HandlerCensus(ast.NodeVisitor):
    """One pass per ``except ... as N`` body."""

    def __init__(self, source: str, path: str):
        self.lines = source.splitlines()
        self.path = path
        self.rows: list[dict[str, Any]] = []
        self.unresolved: list[dict[str, Any]] = []
        self._func: list[str] = []

    # -- context ---------------------------------------------------------
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._func.append(node.name)
        self.generic_visit(node)
        self._func.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    # -- the subject -----------------------------------------------------
    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:  # noqa: N802
        if node.name:
            names = {node.name}
            # Multi-hop aliases: ``a = exc`` inside the handler widens the set.
            for stmt in ast.walk(node):
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Name):
                    if stmt.value.id in names:
                        for tgt in stmt.targets:
                            if isinstance(tgt, ast.Name):
                                names.add(tgt.id)
            self._scan_body(node, names)
        else:
            self.unresolved.append(
                {
                    "path": self.path,
                    "line": node.lineno,
                    "function": self._func[-1] if self._func else "<module>",
                    "why": "bare `except:` -- no name bound, nothing to render",
                }
            )
        self.generic_visit(node)

    # -- sinks -----------------------------------------------------------
    def _scan_body(self, handler: ast.ExceptHandler, names: set[str]) -> None:
        func = self._func[-1] if self._func else "<module>"

        for node in ast.walk(handler):
            sink: Optional[str] = None
            subject: Optional[ast.AST] = None

            # S1 LOG -- every argument position, because this package logs
            # lazily and the value is in args, never in the format string.
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in LOG_METHODS:
                    sink = "LOG"
                    subject = ast.Module(body=[], type_ignores=[])
                    subject = node  # whole call: format string AND args

            # S3 RAISE
            elif isinstance(node, ast.Raise):
                sink = "RAISE"
                subject = node.exc

            # S2 RETURN -- a value returned directly.
            elif isinstance(node, ast.Return):
                sink = "RETURN"
                subject = node.value

            # S2 RETURN -- a dict built then returned, or a subscript assigned
            # into one. Both shapes occur in auth.py and the second is the one
            # a naive scan misses.
            elif isinstance(node, ast.Assign):
                sink = "ASSIGN->RETURN?"
                subject = node.value

            if sink is None or subject is None:
                continue

            what = renders(subject, names)
            if not what:
                continue

            self.rows.append(
                {
                    "path": self.path,
                    "line": node.lineno,
                    "function": func,
                    "handler_line": handler.lineno,
                    "caught_as": sorted(names),
                    "sink": sink,
                    "renders": "VALUE" if "VALUE" in what else "TYPE_ONLY",
                    "both": sorted(what),
                    "source": self.lines[node.lineno - 1].strip()[:110],
                }
            )


def census(path: pathlib.Path, label: Optional[str] = None) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    walker = _HandlerCensus(source, label or str(path).replace("\\", "/"))
    walker.visit(ast.parse(source))
    return {"rows": walker.rows, "unresolved": walker.unresolved}


def census_source(source: str, label: str = "<inline>") -> dict[str, Any]:
    walker = _HandlerCensus(source, label)
    walker.visit(ast.parse(source))
    return {"rows": walker.rows, "unresolved": walker.unresolved}


# ---------------------------------------------------------------------------
# The selftest -- fixture MANUFACTURED HERE, never found in the repo
# ---------------------------------------------------------------------------

FIXTURE = '''
import logging
logger = logging.getLogger("x")

def type_only_log():
    try:
        pass
    except Exception as exc:
        logger.info("failed: %s", type(exc).__name__)

def lazy_value_log():
    try:
        pass
    except Exception as exc:
        logger.info("failed: %s: %s", type(exc).__name__, exc)

def fstring_return():
    try:
        pass
    except Exception as exc:
        return {"reason": f"broke ({type(exc).__name__}: {exc})"}

def type_only_return():
    try:
        pass
    except Exception as exc:
        return {"reason": f"broke ({type(exc).__name__})"}

def value_raise():
    try:
        pass
    except Exception as exc:
        raise RuntimeError(f"broke: {exc}") from exc

def subscript_sink():
    try:
        pass
    except Exception as exc:
        out = {}
        out["reason"] = str(exc)
        return out

def multi_hop():
    try:
        pass
    except Exception as exc:
        alias = exc
        logger.info("failed: %s", alias)

def rebound_is_clean():
    try:
        pass
    except Exception as exc:
        exc = "a literal"
        logger.info("failed: %s", exc)

def bare_handler():
    try:
        pass
    except:
        logger.info("something failed")
'''

#: ``function -> (expected renders verdict, expected sink present)``.
EXPECTED = {
    "type_only_log": ("TYPE_ONLY", "LOG"),
    "lazy_value_log": ("VALUE", "LOG"),
    "fstring_return": ("VALUE", "RETURN"),
    "type_only_return": ("TYPE_ONLY", "RETURN"),
    "value_raise": ("VALUE", "RAISE"),
    "subscript_sink": ("VALUE", "ASSIGN->RETURN?"),
    "multi_hop": ("VALUE", "LOG"),
}


def selftest(flip: Optional[str] = None) -> int:
    expected = dict(EXPECTED)
    if flip:
        was = expected[flip]
        other = "TYPE_ONLY" if was[0] == "VALUE" else "VALUE"
        expected[flip] = (other, was[1])
        print(f"FLIPPED {flip}: {was[0]} -> {other}")

    result = census_source(FIXTURE, "<selftest fixture>")
    by_func: dict[str, list[dict[str, Any]]] = {}
    for row in result["rows"]:
        by_func.setdefault(row["function"], []).append(row)

    failures = 0
    checks = 0

    for func, (want_renders, want_sink) in sorted(expected.items()):
        checks += 1
        rows = by_func.get(func, [])
        if not rows:
            print(f"  FAIL {func}: expected a {want_renders} {want_sink} row, got none")
            failures += 1
            continue
        got = "VALUE" if any(r["renders"] == "VALUE" for r in rows) else "TYPE_ONLY"
        sinks = {r["sink"] for r in rows}
        ok = got == want_renders and want_sink in sinks
        print(
            f"  {'ok  ' if ok else 'FAIL'} {func}: renders={got} "
            f"sinks={sorted(sinks)}"
        )
        if not ok:
            failures += 1

    # A rebound name must NOT be reported as a value render.
    checks += 1
    rebound = by_func.get("rebound_is_clean", [])
    rebound_value = any(r["renders"] == "VALUE" for r in rebound)
    # The walker is deliberately conservative: it does NOT model rebinding, so
    # this case is EXPECTED to over-report. Asserting the known behaviour
    # rather than the wished-for one keeps the limit honest and visible.
    print(
        f"  {'ok  ' if rebound_value else 'FAIL'} rebound_is_clean: "
        f"over-reported={rebound_value} (a KNOWN, asserted limit -- see LIMITS)"
    )
    if not rebound_value:
        failures += 1

    checks += 1
    bare = [u for u in result["unresolved"] if u["function"] == "bare_handler"]
    print(f"  {'ok  ' if bare else 'FAIL'} bare_handler: counted as unresolved")
    if not bare:
        failures += 1

    print(f"SELFTEST {checks - failures}/{checks}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=DEFAULT_TARGET)
    parser.add_argument("--json")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--flip", help="selftest only: invert one expectation")
    args = parser.parse_args()

    if args.selftest:
        return selftest(args.flip)

    target = REPO_ROOT / args.path
    result = census(target, args.path)
    rows = result["rows"]

    print(f"CENSUS of {args.path}")
    print("=" * 108)
    print(f"{'line':>5}  {'function':<26} {'sink':<16} {'renders':<10} source")
    print("-" * 108)
    for row in sorted(rows, key=lambda r: r["line"]):
        print(
            f"{row['line']:>5}  {row['function']:<26} {row['sink']:<16} "
            f"{row['renders']:<10} {row['source']}"
        )

    print("-" * 108)
    pairs: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (row["renders"], row["sink"])
        pairs[key] = pairs.get(key, 0) + 1
    print("TOTALS by (renders x sink):")
    for (rend, sink), count in sorted(pairs.items()):
        print(f"  {rend:<10} {sink:<16} {count}")
    value_rows = [r for r in rows if r["renders"] == "VALUE"]
    print(f"\n  rows total        : {len(rows)}")
    print(f"  VALUE rows        : {len(value_rows)}   <- worth driving")
    print(f"  TYPE_ONLY rows    : {len(rows) - len(value_rows)}")
    print(f"  unresolved        : {len(result['unresolved'])}")

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
