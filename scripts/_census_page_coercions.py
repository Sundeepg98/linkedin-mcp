"""Enumerate every COERCION SITE in ``linkedin_server/`` and classify each one.

THE CLASS THIS COUNTS, stated once. ``int()`` puts the value it refused
VERBATIM into its own ``ValueError``. An exception is not a return value, so a
reader whose declared return type is integers-only still carries a page string
out of the process the moment the page answers with one: the exception leaves
the reader, ``server._error`` catches it, and ``config.scrub`` substitutes this
server's own PATHS and nothing else -- a name has no shape to scrub.

    AN INTEGER-ONLY RETURN VALUE DOES NOT MAKE A FUNCTION INTEGER-ONLY.

## WHY THIS IS AN AST WALK AND NOT A GREP, with the number that forces it

``grep -c "int(\\|float("`` over ``linkedin_server/`` reports **118 hits in
dom.py alone**, and dom.py is where the in-page JavaScript lives. ``parseInt``
inside a JS string literal is not a Python coercion and cannot raise a Python
ValueError; counting it inflates the denominator with sites that cannot hold
the defect. An AST walk sees Python ``Call`` nodes and is blind to the contents
of string literals, which is exactly the discrimination this census needs.
:func:`grep_contrast` prints both numbers side by side so the gap is stated
rather than hidden.

## THE CONSTRUCTOR LIST IS MEASURED, NOT ASSUMED

:func:`probe_constructors` calls each candidate with a marker and reports
whether the marker survives into ``str(exc)``, ``repr(exc)`` or ``exc.args``.
``int`` and ``float`` quote; ``complex`` and ``uuid.UUID`` do not. A census
that assumed the list would be wrong in both directions, and the repository's
standing law is that a check entering the register has been shown failing --
which starts with knowing what it is checking for.

## THE FIVE BUCKETS, AND WHY "GUARDED" IS NOT "SAFE"

* ``LITERAL``    -- the argument is a constant. Cannot carry page data.
* ``GUARDED``    -- lexically inside a ``try`` whose handler catches
  ValueError/TypeError/Exception. The exception cannot escape AS ITSELF. It is
  still reported, because a handler that re-raises or logs ``str(exc)`` carries
  the value anyway, and this census cannot see which.
* ``PAGE_READER``-- unguarded, inside an ``async def`` that takes a ``page``.
  This is the hazard bucket: the value being coerced came off a document.
* ``DOWNSTREAM`` -- unguarded, in a function a reader's output flows into.
* ``OFF_PAGE``   -- unguarded, and its input is config, env or an argument the
  server itself constructed.

**A STATIC BUCKET IS A HYPOTHESIS, NEVER A VERDICT.** Which sites LEAK is
settled by driving the real readers with a page that answers in strings --
``tests/test_readers_emit_no_page_string.py`` does that. This file supplies the
DENOMINATOR that measurement is scored against, so that "we repaired the ones
that leak" is a fraction rather than a feeling.

    venv/Scripts/python scripts/_census_page_coercions.py [--json]
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterator, Optional

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

#: Builtins whose exception message quotes the value they refused. MEASURED by
#: :func:`probe_constructors`, not assumed -- see the module docstring.
QUOTING_BUILTINS: tuple[str, ...] = ("int", "float")

#: Attribute-style coercions with the same property. ``strptime`` renders the
#: data it could not parse; ``fromisoformat`` renders the string; ``.index``
#: renders the item it could not find.
QUOTING_ATTRS: tuple[str, ...] = ("strptime", "fromisoformat", "index")

#: Exception types whose capture means an ``int``/``float`` ValueError cannot
#: escape the ``try`` as itself.
CATCHING: frozenset[str] = frozenset(
    {"ValueError", "TypeError", "Exception", "BaseException", "ArithmeticError"}
)


# ---------------------------------------------------------------------------
# 1. The measurement that decides which constructors belong in the census
# ---------------------------------------------------------------------------

#: Long, and carrying ``example`` so the identity guard passes it on sight --
#: the same reasoning ``anchors.control_fixture`` gives for its slugs.
PROBE_MARKER = "Exampleperson Markersurname"


def probe_constructors() -> list[dict[str, Any]]:
    """Call each candidate with a marker; report whether the marker survives.

    The point is that the census's own subject list is a measurement. A
    constructor that does NOT quote its input is not in the hazard class, and
    including it would inflate every count downstream.
    """
    import datetime
    import uuid

    candidates: tuple[tuple[str, Any], ...] = (
        ("int", lambda v: int(v)),
        ("float", lambda v: float(v)),
        ("complex", lambda v: complex(v)),
        ("uuid.UUID", lambda v: uuid.UUID(v)),
        ("int(base=10)", lambda v: int(v, 10)),
        ("datetime.strptime", lambda v: datetime.datetime.strptime(v, "%Y")),
        ("datetime.fromisoformat", lambda v: datetime.datetime.fromisoformat(v)),
        ("list.index", lambda v: [1, 2].index(v)),
        ("json.loads", lambda v: __import__("json").loads(v)),
        ("dict[key]", lambda v: {}[v]),
    )
    rows: list[dict[str, Any]] = []
    for label, call in candidates:
        try:
            call(PROBE_MARKER)
        except BaseException as exc:  # noqa: BLE001 -- the exception is the subject
            surfaces = {
                "str": PROBE_MARKER in str(exc),
                "repr": PROBE_MARKER in repr(exc),
                "args": any(PROBE_MARKER in str(a) for a in getattr(exc, "args", ())),
            }
            rows.append(
                {
                    "constructor": label,
                    "raised": type(exc).__name__,
                    "quotes": any(surfaces.values()),
                    "surfaces": sorted(k for k, v in surfaces.items() if v),
                }
            )
        else:
            rows.append(
                {
                    "constructor": label,
                    "raised": "",
                    "quotes": False,
                    "surfaces": [],
                }
            )
    return rows


# ---------------------------------------------------------------------------
# 2. The walk
# ---------------------------------------------------------------------------


def _is_coercion(node: ast.AST) -> Optional[str]:
    """The coercion's name if this node is one of the quoting calls."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if isinstance(func, ast.Name) and func.id in QUOTING_BUILTINS:
        return func.id
    if isinstance(func, ast.Attribute) and func.attr in QUOTING_ATTRS:
        return f".{func.attr}"
    return None


def _takes_a_page(fn: ast.AST) -> bool:
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    names = [a.arg for a in fn.args.args] + [a.arg for a in fn.args.posonlyargs]
    names += [a.arg for a in fn.args.kwonlyargs]
    return "page" in names


def _argument_shape(node: ast.Call) -> str:
    """What is being coerced, as a short structural label."""
    if not node.args:
        return "no-arg"
    arg = node.args[0]
    if isinstance(arg, ast.Constant):
        return "literal"
    if isinstance(arg, ast.Name):
        return f"name:{arg.id}"
    if isinstance(arg, ast.Subscript):
        return "subscript"
    if isinstance(arg, ast.Call):
        inner = arg.func
        if isinstance(inner, ast.Attribute):
            return f"call:.{inner.attr}"
        if isinstance(inner, ast.Name):
            return f"call:{inner.id}"
        return "call"
    if isinstance(arg, ast.Attribute):
        return f"attr:.{arg.attr}"
    if isinstance(arg, ast.BoolOp):
        return "boolop"
    return type(arg).__name__.lower()


def _names_in(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


# ---------------------------------------------------------------------------
# WHICH AWAITS CAN HAND BACK A PAGE STRING, AND WHICH CANNOT
# ---------------------------------------------------------------------------
#
# THIS IS THE DISTINCTION THAT DECIDES THE WHOLE CENSUS, and it is not about
# whether a value was awaited. ``await locator.count()`` is awaited and CANNOT
# be a string: Playwright computes that number itself and its return type is
# part of its API. ``await page.evaluate(...)`` is awaited and can be ANYTHING
# the document's JavaScript returned, including a name.
#
#     A VALUE IS PAGE-CONTROLLED WHEN THE DOCUMENT CHOOSES IT,
#     NOT WHEN A COROUTINE PRODUCED IT.
#
# Getting this wrong in the permissive direction would convict ``events.py``
# and ``groups_page.py`` of leaks they cannot have -- both coerce nothing but
# ``.count()`` results and ``len()`` of text -- and a census that cries wolf on
# sites which are structurally safe is one nobody acts on.

#: Playwright computes these; the return type is Playwright's contract.
PLAYWRIGHT_TYPED: frozenset[str] = frozenset(
    {"count", "is_visible", "is_enabled", "is_disabled", "is_checked",
     "is_editable", "is_hidden", "bounding_box"}
)

#: The document chooses these. Every one of them can be a name.
PAGE_CONTROLLED: frozenset[str] = frozenset(
    {"evaluate", "evaluate_handle", "eval_on_selector", "eval_on_selector_all",
     "inner_text", "text_content", "inner_html", "content", "title",
     "input_value", "get_attribute", "all_text_contents", "all_inner_texts"}
)

#: Builtins whose RESULT TYPE is fixed regardless of the argument. ``len`` of a
#: page string is an integer, and coercing it cannot quote anything.
TYPE_FIXING: frozenset[str] = frozenset(
    {"len", "bool", "sum", "abs", "round", "ord", "id", "hash", "int", "float"}
)

#: Builtins that carry their argument's content through into the result.
TYPE_PRESERVING: frozenset[str] = frozenset(
    {"str", "list", "dict", "tuple", "set", "sorted", "reversed", "next",
     "iter", "repr", "format", "max", "min"}
)


def _callee_name(func: ast.AST) -> str:
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _await_is_page_controlled(node: ast.Await) -> bool:
    """Can this ``await`` hand back a string the document chose?

    Unknown callees answer YES. A local helper this census cannot follow might
    return page text, and the safe direction for a hazard census is to keep the
    site in the set and let the MEASUREMENT acquit it.
    """
    inner = node.value
    if isinstance(inner, ast.Call):
        name = _callee_name(inner.func)
        if name in PLAYWRIGHT_TYPED:
            return False
        if name in PAGE_CONTROLLED:
            return True
    return True


def _can_be_page_string(expr: ast.AST, tainted: set[str]) -> bool:
    """Whether ``expr`` can evaluate to a string the document chose.

    A small abstract interpretation over the shapes this package actually
    writes. Anything it does not recognise answers YES, so the set it produces
    is a superset of the true hazard set by construction.
    """
    if isinstance(expr, ast.Constant):
        return False
    if isinstance(expr, ast.Await):
        return _await_is_page_controlled(expr)
    if isinstance(expr, ast.Name):
        return expr.id in tainted
    if isinstance(expr, ast.Call):
        name = _callee_name(expr.func)
        if name in TYPE_FIXING:
            return False
        if name in PLAYWRIGHT_TYPED:
            return False
        if name in PAGE_CONTROLLED:
            return True
        if name in TYPE_PRESERVING:
            return any(_can_be_page_string(a, tainted) for a in expr.args)
        if name in {"get", "pop", "setdefault"} and isinstance(expr.func, ast.Attribute):
            # A lookup INTO a mapping carries that mapping's contents out.
            return _can_be_page_string(expr.func.value, tainted)
        if isinstance(expr.func, ast.Attribute):
            return _can_be_page_string(expr.func.value, tainted)
        return True
    if isinstance(expr, ast.BoolOp):
        return any(_can_be_page_string(v, tainted) for v in expr.values)
    if isinstance(expr, ast.IfExp):
        return any(_can_be_page_string(v, tainted) for v in (expr.body, expr.orelse))
    if isinstance(expr, (ast.Attribute, ast.Starred)):
        return _can_be_page_string(expr.value, tainted)
    if isinstance(expr, ast.Subscript):
        return _can_be_page_string(expr.value, tainted)
    if isinstance(expr, ast.BinOp):
        return any(_can_be_page_string(v, tainted) for v in (expr.left, expr.right))
    if isinstance(expr, (ast.Compare, ast.UnaryOp)):
        return False
    if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
        return any(_can_be_page_string(v, tainted) for v in expr.elts)
    if isinstance(expr, ast.Dict):
        return any(_can_be_page_string(v, tainted) for v in expr.values if v)
    if isinstance(expr, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
        return _can_be_page_string(expr.elt, tainted)
    if isinstance(expr, ast.DictComp):
        return _can_be_page_string(expr.value, tainted)
    if isinstance(expr, ast.JoinedStr):
        return True
    return True


def _tainted_names(fn: ast.AST) -> set[str]:
    """Names in ``fn`` that can hold a string the document chose.

    Run to a fixed point, because the shipped shape is two hops::

        raw = await dom.read_anchor_classes(...)         # taints `raw`
        counts = list((raw or {}).get("counts") or [])   # taints `counts`
        [int(value) for value in counts]                 # the site

    A one-hop analysis calls that site clean, which is how a reader that
    obviously coerces page data reads as safe. Comprehension and ``for``
    targets are taken too: ``for value in counts`` binds ``value`` from a
    tainted iterable.
    """
    tainted: set[str] = set()
    for _ in range(8):  # a fixed point; 8 hops is far past anything observed
        before = set(tainted)
        for node in ast.walk(fn):
            targets: list[ast.AST] = []
            value: Optional[ast.AST] = None
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                value = node.value
                targets = list(getattr(node, "targets", [])) or [node.target]
            elif isinstance(node, ast.comprehension):
                value = node.iter
                targets = [node.target]
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                value = node.iter
                targets = [node.target]
            elif isinstance(node, ast.withitem):
                value = node.context_expr
                targets = [node.optional_vars] if node.optional_vars else []
            if value is None:
                continue
            if not _can_be_page_string(value, tainted):
                continue
            for target in targets:
                if target is not None:
                    tainted |= _names_in(target)
        if tainted == before:
            break
    return tainted


class _Walker(ast.NodeVisitor):
    """Collect coercion sites with their enclosing function and try context."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.sites: list[dict[str, Any]] = []
        self._fn_stack: list[ast.AST] = []
        self._try_catches: list[bool] = []
        self._taint_stack: list[set[str]] = []

    # -- scopes ------------------------------------------------------------
    def _visit_fn(self, node: ast.AST) -> None:
        self._fn_stack.append(node)
        self._taint_stack.append(_tainted_names(node))
        self.generic_visit(node)
        self._taint_stack.pop()
        self._fn_stack.pop()

    visit_FunctionDef = _visit_fn
    visit_AsyncFunctionDef = _visit_fn

    def visit_Try(self, node: ast.Try) -> None:
        catches = any(
            _handler_catches(handler) for handler in node.handlers
        )
        self._try_catches.append(catches)
        for stmt in node.body:
            self.visit(stmt)
        self._try_catches.pop()
        # Handlers, else and finally are NOT protected by this try.
        for handler in node.handlers:
            self.visit(handler)
        for stmt in node.orelse + node.finalbody:
            self.visit(stmt)

    # -- the sites ---------------------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        name = _is_coercion(node)
        if name is not None:
            self.sites.append(self._record(node, name))
        self.generic_visit(node)

    def _record(self, node: ast.Call, name: str) -> dict[str, Any]:
        enclosing = self._fn_stack[-1] if self._fn_stack else None
        fn_name = getattr(enclosing, "name", "<module>")
        page_scope = any(_takes_a_page(fn) for fn in self._fn_stack)
        guarded = any(self._try_catches)
        shape = _argument_shape(node)
        tainted = set().union(*self._taint_stack) if self._taint_stack else set()
        derived = bool(node.args) and _can_be_page_string(node.args[0], tainted)
        return {
            "module": self.path.name,
            "line": node.lineno,
            "coercion": name,
            "function": fn_name,
            "in_page_reader": page_scope,
            "page_derived": derived,
            "guarded": guarded,
            "arg": shape,
            "bucket": _bucket(shape, guarded, page_scope, derived),
        }


def _handler_catches(handler: ast.ExceptHandler) -> bool:
    kind = handler.type
    if kind is None:  # bare except
        return True
    names: list[str] = []
    if isinstance(kind, ast.Tuple):
        names = [n.id for n in kind.elts if isinstance(n, ast.Name)]
    elif isinstance(kind, ast.Name):
        names = [kind.id]
    elif isinstance(kind, ast.Attribute):
        names = [kind.attr]
    return any(n in CATCHING for n in names)


def _bucket(shape: str, guarded: bool, page_scope: bool, derived: bool) -> str:
    """The five buckets, in the order that decides them.

    ``BOUND_ONLY`` is the distinction the brief asks for by name: a site inside
    a page reader whose argument is a CALLER-SUPPLIED BOUND -- ``int(max_items)``,
    ``int(timeout_ms)`` -- is inside the reader but its input never touched the
    document. It coerces, and it cannot carry a page string, and saying so is a
    different finding from a leak.
    """
    if shape == "literal":
        return "LITERAL"
    if guarded:
        return "GUARDED"
    if page_scope and derived:
        return "PAGE_DERIVED"
    if page_scope:
        return "BOUND_ONLY"
    return "OFF_PAGE"


def census(package: Path = PACKAGE) -> list[dict[str, Any]]:
    """Every coercion site in the package, classified. Sorted for diffability."""
    out: list[dict[str, Any]] = []
    for path in sorted(package.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        walker = _Walker(path)
        walker.visit(tree)
        out.extend(walker.sites)
    return sorted(out, key=lambda row: (row["module"], row["line"]))


# ---------------------------------------------------------------------------
# 3. The contrast that justifies the method
# ---------------------------------------------------------------------------


def grep_contrast(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per module: what a text search counts, against what the AST counts."""
    try:
        proc = subprocess.run(
            ["git", "grep", "-c", "-e", r"int(", "-e", r"float(", "--", "linkedin_server/"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=60,
        )
        textual: dict[str, int] = {}
        for line in proc.stdout.splitlines():
            if ":" not in line:
                continue
            where, _, count = line.rpartition(":")
            textual[Path(where).name] = int(count) if count.isdigit() else 0
    except (OSError, subprocess.SubprocessError):
        textual = {}

    ast_counts: dict[str, int] = {}
    for row in rows:
        ast_counts[row["module"]] = ast_counts.get(row["module"], 0) + 1

    modules = sorted(set(textual) | set(ast_counts))
    return [
        {
            "module": name,
            "grep_lines": textual.get(name, 0),
            "ast_sites": ast_counts.get(name, 0),
        }
        for name in modules
    ]


# ---------------------------------------------------------------------------
# 4. Report
# ---------------------------------------------------------------------------


def _tabulate(rows: list[dict[str, Any]], key: str) -> Iterator[tuple[str, int]]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row[key])] = counts.get(str(row[key]), 0) + 1
    yield from sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def main(argv: list[str]) -> int:
    rows = census()

    if "--json" in argv:
        print(json.dumps({"sites": rows, "contrast": grep_contrast(rows)}, indent=2))
        return 0

    print("CONSTRUCTORS -- which ones quote the value they refused (measured)")
    print()
    for row in probe_constructors():
        mark = "QUOTES" if row["quotes"] else "silent"
        surfaces = ",".join(row["surfaces"]) or "-"
        print(f"  {row['constructor']:24s} {row['raised']:22s} {mark:7s} {surfaces}")
    print()

    print("GREP vs AST -- why this is a parse and not a text search")
    print()
    print(f"  {'module':26s} {'grep lines':>10s} {'ast sites':>10s}")
    total_grep = total_ast = 0
    for row in grep_contrast(rows):
        total_grep += row["grep_lines"]
        total_ast += row["ast_sites"]
        if row["grep_lines"] != row["ast_sites"]:
            print(f"  {row['module']:26s} {row['grep_lines']:>10d} {row['ast_sites']:>10d}")
    print(f"  {'TOTAL':26s} {total_grep:>10d} {total_ast:>10d}")
    print()

    modules = sorted({row["module"] for row in rows})
    print(f"CENSUS -- {len(rows)} coercion sites in {len(modules)} modules")
    print()
    for bucket, count in _tabulate(rows, "bucket"):
        print(f"  {bucket:14s} {count:4d}")
    print()

    hazard = [r for r in rows if r["bucket"] == "PAGE_DERIVED"]
    hazard_modules = sorted({r["module"] for r in hazard})
    print(
        f"HAZARD BUCKET -- {len(hazard)} unguarded page-DERIVED sites, "
        f"in {len(hazard_modules)} modules"
    )
    print()
    per_fn: dict[tuple[str, str], int] = {}
    for row in hazard:
        key = (row["module"], row["function"])
        per_fn[key] = per_fn.get(key, 0) + 1
    for (module, function), count in sorted(per_fn.items()):
        print(f"  {module:24s} {function:34s} {count:3d} site(s)")
    print()
    print("A STATIC BUCKET IS A HYPOTHESIS. Which of these actually leak is")
    print("settled by driving the real readers:")
    print("  tests/test_readers_emit_no_page_string.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
