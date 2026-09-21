"""Census: every ``ast.Subscript`` in ``tests/**/*.py`` whose key is a STRING
CONSTANT and whose base is a NAME this module classifies as RESULT-BOUND -- a
bare ``result["key"]``-shaped read that raises an uninformative ``KeyError``
(naming only the missing key, never what the call actually returned) instead
of the ``.get("key")`` pattern ``tests/test_editor_fields.py`` documents as
its own convention just above its ``names_of()`` helper.

## WHY THIS EXISTS

``tests/test_editor_fields.py`` carries this comment immediately above
``names_of()``, stating the module's own convention:

    ``.get("refused")`` rather than ``result["refused"]`` in every refusal
    check below, and that is about the FAILURE TEXT rather than about
    strictness. A subscript on a result that stopped refusing raises
    ``KeyError: 'refused'``, which says nothing about what the tool returned
    instead; ``.get`` with the whole result as the assertion message prints
    the answer a caller would have received.

and then ``names_of`` itself does exactly the thing the comment warns
against: ``return [field["name"] for field in result["fields"]]``. On CI
this produced ``KeyError: 'fields'`` when the tool had actually returned
``{'error': 'unexpected', 'message': 'TimeoutError: Page.set_content: ...'}``
-- the KeyError named a key that was merely absent and said nothing about
the real answer.

This census finds every OTHER instance of that same shape across the whole
suite, by AST -- not by grep/regex, which cannot tell a result-bound ``x``
apart from an unrelated dict literal ``x`` that happens to share the name.

## WHAT COUNTS AS "RESULT-BOUND" -- five rules, defined once, here

A name is result-bound in its enclosing def/async def/module scope if ANY of
the following binds it, anywhere in that same scope:

  (a) ``x = await <anything>``                       -- direct await.
  (b) ``x, *rest = await <anything>``                 -- tuple/list-unpack of
      an await; only the names actually unpacked count (one level of
      ``Starred`` is unwrapped; a nested tuple target is not, since none
      were observed in this suite's await-unpacks, which are uniformly
      flat).
  (c) ``x = <call to a name/attr ending in run_tool, call_tool, invoke,
      tool, or _run>``                                -- sync wrappers
      around an async fixture ("async fixtures in this repo return the
      envelope"). Matched by SUFFIX on the Call's ``func`` (a bare ``Name``
      or the trailing ``Attribute``), so a bare ``_run(...)`` and a chained
      ``client.call_tool(...)`` both match.
  (d) the name is a FUNCTION PARAMETER named one of: result, results,
      answer, envelope, payload, reply, response.
  (e) ``x = json.loads(...)``, but ONLY when the enclosing scope already has
      an (a)-(d) result-bound name for some other (or the same) name -- an
      (e) binding is recorded but marked ``indirect``, since a
      ``json.loads`` call sitting in a function that is already visibly
      working an API envelope is probably parsing a serialised one too.

Binding existence is SCOPE-LOCAL: a nested ``def`` does not inherit its
outer ``def``'s bindings for the purposes of this census (real Python
closures could still read an outer local without rebinding it, but this
census follows the brief's own scoping rule rather than full closure
semantics -- the motivating instance, ``names_of``, is a top-level function
with no outer scope to inherit from anyway).

Decorator expressions and parameter DEFAULT VALUES are not scanned for
bindings or subscripts, the same exclusion ``_census_quoting_callees.py``
already uses for annotations, and for the same reason: every real instance
this run found lives in a function BODY, and scanning decorators/defaults
would need its own proven positive control before being trusted rather than
just being bolted on speculatively.

## WHAT "LINE" AND "COL" MEAN IN THE OUTPUT

Per brief: ast END positions (``end_lineno``/``end_col_offset``), reported
verbatim (0-indexed column, exactly as ast gives it -- no hand adjustment).
For the overwhelming majority of subscripts here (a single physical line)
this is identical to the start position. ``line_start``/``col_start`` (ast's
``lineno``/``col_offset``) are ALSO carried as bonus fields for navigation,
since the two diverge only when a subscript expression itself spans more
than one physical line.

## CONTROLS

Run with ``--self-test`` to execute all controls across all three passes
(pass 1: 3 controls; pass A: 2; pass B: 1) and print their verbatim output;
no census file is written in that mode.

## PASS A and PASS B (follow-up census, same instrument, same scope walk)

``--pass-a`` enumerates the SHAPE the CI failure actually had: a non-test_,
non-fixture helper that takes a rule-(d) result-shaped parameter and
subscripts it with a string constant, with no guard (an ``if <k> in
param:``, a ``.get``, a try/except KeyError, an assert naming the param, or
an ``if <k> not in param: <exit>`` bail-out) visible before that subscript.
Writes ``_audit/_census-result-subscripts-passA.json``.

``--pass-b`` classifies every file under ``tests/`` by whether it PRACTISES
the ``.get()``-with-whole-result-as-message convention, BREAKS it (Pass 1's
own subscript census), does both (MIXED), or neither, plus a ``tokenize``-
based (never grep) flag for a comment block that states the convention.
Writes ``_audit/_census-result-subscripts-passB.json``.

Run:
    venv/Scripts/python.exe scripts/_census_result_subscripts.py
    venv/Scripts/python.exe scripts/_census_result_subscripts.py --pass-a
    venv/Scripts/python.exe scripts/_census_result_subscripts.py --pass-b
    venv/Scripts/python.exe scripts/_census_result_subscripts.py --self-test
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import sys
import textwrap
import tokenize
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
TESTS_DIR = REPO / "tests"
OUT_JSON = REPO / "_audit" / "_census-result-subscripts.json"
PASS_A_JSON = REPO / "_audit" / "_census-result-subscripts-passA.json"
PASS_B_JSON = REPO / "_audit" / "_census-result-subscripts-passB.json"

#: Rule (c) -- suffixes matched against a Call's func Name.id or Attribute.attr.
RESULT_CALL_SUFFIXES = ("run_tool", "call_tool", "invoke", "tool", "_run")

#: Rule (d) -- function PARAMETER names that count as result-bound on sight.
RESULT_PARAM_NAMES = frozenset(
    {"result", "results", "answer", "envelope", "payload", "reply", "response"}
)

#: The known instance CONTROL 1 must find -- test_editor_fields.py's names_of().
KNOWN_POSITIVE = {
    "file": "tests/test_editor_fields.py",
    "name": "result",
    "key": "fields",
}

#: PASS A -- decorator names that mark a function as a pytest fixture (bare
#: ``@fixture``/``@pytest.fixture`` or the called form, either spelling).
FIXTURE_DECORATOR_NAMES = frozenset({"fixture"})

#: PASS B -- the two comment substrings that, alongside ``.get(``, identify a
#: comment block STATING the module's own .get()-over-subscript convention.
CONVENTION_MARKERS = ("KeyError", "says nothing about what the tool returned")


# ---------------------------------------------------------------------------
# Slice / call-target extraction
# ---------------------------------------------------------------------------


def string_slice_value(node: ast.Subscript) -> Optional[str]:
    """The subscript's key, if and only if it is a STRING CONSTANT.

    Handles both the >=3.9 shape (``node.slice`` is the expression itself)
    and the <3.9 shape (``node.slice`` is an ``ast.Index`` wrapper), even
    though this repo's own interpreter (3.13, confirmed before writing this
    file) only ever produces the former -- cheap to keep, costs nothing.
    """
    sl = node.slice
    if sl.__class__.__name__ == "Index":  # pragma: no cover -- pre-3.9 shape
        sl = sl.value  # type: ignore[attr-defined]
    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
        return sl.value
    return None


def call_target_name(func: ast.AST) -> Optional[str]:
    """The bare name (``Name.id``) or trailing attribute (``Attribute.attr``)
    of a Call's ``func``, or ``None`` for any other shape (a call result, a
    subscript, a lambda, ...)."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def matches_result_call(func: ast.AST) -> bool:
    """Rule (c): does this Call's func end in one of RESULT_CALL_SUFFIXES."""
    name = call_target_name(func)
    if name is None:
        return False
    return any(name.endswith(suffix) for suffix in RESULT_CALL_SUFFIXES)


def is_json_loads_call(value: ast.AST) -> bool:
    """``json.loads(...)`` exactly -- the object must be the bare name
    ``json``. An aliased import or a ``from json import loads`` form is not
    matched; none were observed in this repo's tests (see the report)."""
    return (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == "loads"
        and isinstance(value.func.value, ast.Name)
        and value.func.value.id == "json"
    )


# ---------------------------------------------------------------------------
# Binding collection -- rules (a)-(e)
# ---------------------------------------------------------------------------


def _assign_targets_and_value(node: ast.AST) -> tuple[list[ast.AST], Optional[ast.AST]]:
    if isinstance(node, ast.Assign):
        return list(node.targets), node.value
    if isinstance(node, ast.AnnAssign) and node.value is not None:
        return [node.target], node.value
    return [], None


def _names_from_unpack_target(target: ast.AST) -> list[ast.Name]:
    """Names actually assigned by a Tuple/List unpack target, unwrapping one
    level of ``Starred`` (``x, *rest = ...``)."""
    names: list[ast.Name] = []
    for elt in target.elts:  # type: ignore[attr-defined]
        if isinstance(elt, ast.Starred):
            elt = elt.value
        if isinstance(elt, ast.Name):
            names.append(elt)
    return names


def bindings_from_assign(node: ast.AST) -> list[tuple[str, str, int]]:
    """Rules (a)/(b)/(c) for one Assign/AnnAssign node.

    Returns a list of (name, rule, lineno) triples -- usually zero or one,
    more than one only for a chained ``x = y = await ...``.
    """
    targets, value = _assign_targets_and_value(node)
    if value is None:
        return []
    out: list[tuple[str, str, int]] = []
    for target in targets:
        if isinstance(target, ast.Name):
            if isinstance(value, ast.Await):
                out.append((target.id, "a", node.lineno))
            elif isinstance(value, ast.Call) and matches_result_call(value.func):
                out.append((target.id, "c", node.lineno))
        elif isinstance(target, (ast.Tuple, ast.List)) and isinstance(value, ast.Await):
            for name_node in _names_from_unpack_target(target):
                out.append((name_node.id, "b", node.lineno))
    return out


def bindings_from_json_loads(node: ast.AST) -> list[tuple[str, str, int]]:
    """Rule (e) candidates for one Assign/AnnAssign node. The CALLER decides
    whether the enclosing scope actually qualifies (an a-d binding must
    already exist there) before folding these in."""
    targets, value = _assign_targets_and_value(node)
    if value is None or not is_json_loads_call(value):
        return []
    return [(t.id, "e", node.lineno) for t in targets if isinstance(t, ast.Name)]


def param_bindings(fn: ast.AST) -> list[tuple[str, int]]:
    """Rule (d): parameters named one of RESULT_PARAM_NAMES -> (name, lineno)."""
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return []
    a = fn.args
    all_args = list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs)
    if a.vararg is not None:
        all_args.append(a.vararg)
    if a.kwarg is not None:
        all_args.append(a.kwarg)
    out: list[tuple[str, int]] = []
    for arg in all_args:
        if arg.arg in RESULT_PARAM_NAMES:
            out.append((arg.arg, getattr(arg, "lineno", fn.lineno)))
    return out


# ---------------------------------------------------------------------------
# Scope walking -- stays inside ONE def/async def/module/class, never crosses
# into a nested def/async def/class (each of those gets its own later pass).
# ---------------------------------------------------------------------------


class _ScopeCollector(ast.NodeVisitor):
    """One pass over a scope's own statements, yielding two products: every
    Assign/AnnAssign directly in THIS scope (not inside a nested def/class),
    and every nested def/async def/class directly in this scope, to recurse
    into separately afterwards as ITS OWN scope."""

    def __init__(self) -> None:
        self.assigns: list[ast.AST] = []
        self.nested: list[ast.AST] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.nested.append(node)  # do NOT descend -- a separate scope

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.nested.append(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.nested.append(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return  # a lambda body is one expression; cannot hold an Assign stmt

    def visit_Assign(self, node: ast.Assign) -> None:
        self.assigns.append(node)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.assigns.append(node)
        self.generic_visit(node)


def collect_scope_bindings(
    scope_node: ast.AST, is_function: bool
) -> tuple[dict[str, list[tuple[int, str]]], list[ast.AST]]:
    """All result-bound names directly in ``scope_node`` -> list of
    (lineno, rule) bindings, plus the nested def/async def/class nodes to
    recurse into next."""
    collector = _ScopeCollector()
    for stmt in scope_node.body:  # type: ignore[attr-defined]
        collector.visit(stmt)

    bindings: dict[str, list[tuple[int, str]]] = {}

    def _add(name: str, rule: str, lineno: int) -> None:
        bindings.setdefault(name, []).append((lineno, rule))

    for assign in collector.assigns:
        for name, rule, lineno in bindings_from_assign(assign):
            _add(name, rule, lineno)

    if is_function:
        for name, lineno in param_bindings(scope_node):
            _add(name, "d", lineno)

    if bindings:  # rule (e) requires an existing (a)-(d) name in THIS scope
        for assign in collector.assigns:
            for name, rule, lineno in bindings_from_json_loads(assign):
                _add(name, rule, lineno)

    return bindings, collector.nested


def _nearest_binding(binding_list: list[tuple[int, str]], usage_line: int) -> tuple[int, str]:
    """The binding a reader would call "the" binding for a usage at
    ``usage_line``: the closest one AT OR BEFORE it; if none precede, the
    earliest one overall (a forward reference)."""
    preceding = [b for b in binding_list if b[0] <= usage_line]
    if preceding:
        return max(preceding, key=lambda b: b[0])
    return min(binding_list, key=lambda b: b[0])


# ---------------------------------------------------------------------------
# Subscript discovery, scoped the same way (never crosses into a nested def)
# ---------------------------------------------------------------------------


class _SubscriptFinder(ast.NodeVisitor):
    def __init__(
        self,
        bindings: dict[str, list[tuple[int, str]]],
        enclosing: str,
        rel_file: str,
        source_lines: list[str],
    ) -> None:
        self.bindings = bindings
        self.enclosing = enclosing
        self.rel_file = rel_file
        self.source_lines = source_lines
        self._assert_stack: list[ast.Assert] = []
        self.records: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return  # a nested scope; handled by its own pass

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Assert(self, node: ast.Assert) -> None:
        self._assert_stack.append(node)
        self.generic_visit(node)
        self._assert_stack.pop()

    def visit_Subscript(self, node: ast.Subscript) -> None:
        key = string_slice_value(node)
        if key is not None and isinstance(node.value, ast.Name):
            name = node.value.id
            binding_list = self.bindings.get(name)
            if binding_list:
                bind_line, rule = _nearest_binding(binding_list, node.lineno)
                in_assert = bool(self._assert_stack)
                has_msg = bool(self._assert_stack[-1].msg) if in_assert else False
                end_line = node.end_lineno if node.end_lineno is not None else node.lineno
                end_col = node.end_col_offset if node.end_col_offset is not None else node.col_offset
                src_idx = end_line - 1
                source_line = (
                    self.source_lines[src_idx].strip()
                    if 0 <= src_idx < len(self.source_lines)
                    else ""
                )
                self.records.append(
                    {
                        "file": self.rel_file,
                        "line": end_line,
                        "col": end_col,
                        "line_start": node.lineno,
                        "col_start": node.col_offset,
                        "name": name,
                        "key": key,
                        "binding": {"rule": rule, "line": bind_line, "indirect": rule == "e"},
                        "enclosing": self.enclosing,
                        "source_line": source_line,
                        "in_assert": in_assert,
                        "has_msg": has_msg,
                    }
                )
        self.generic_visit(node)


def _process_scope(
    scope_node: ast.AST,
    enclosing: str,
    rel_file: str,
    source_lines: list[str],
    records_out: list[dict[str, Any]],
    finder_factory: Optional[type] = None,
) -> None:
    """Walks ``scope_node`` and every scope nested in it, running
    ``finder_factory(bindings, enclosing, rel_file, source_lines)`` (an
    ``ast.NodeVisitor`` exposing a ``.records`` list, same constructor shape
    as ``_SubscriptFinder``) over each scope's own statements.

    Defaults to ``_SubscriptFinder`` (Pass 1's subscript census). PASS B
    reuses this SAME scope-walk-and-bind machinery with ``_GetHonourFinder``
    instead, per the brief's "<name> is result-bound by your existing rules"
    -- one binding computation, two different node-shapes to look for.
    """
    if finder_factory is None:
        finder_factory = _SubscriptFinder
    is_function = isinstance(scope_node, (ast.FunctionDef, ast.AsyncFunctionDef))
    bindings, nested = collect_scope_bindings(scope_node, is_function)

    finder = finder_factory(bindings, enclosing, rel_file, source_lines)
    for stmt in scope_node.body:  # type: ignore[attr-defined]
        finder.visit(stmt)
    records_out.extend(finder.records)

    for child in nested:
        child_name = getattr(child, "name", "<module>")
        _process_scope(child, child_name, rel_file, source_lines, records_out, finder_factory)


def census_one_file(path: Path, finder_factory: Optional[type] = None) -> list[dict[str, Any]]:
    rel_file = path.relative_to(REPO).as_posix()
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=rel_file)
    source_lines = source.splitlines()
    records: list[dict[str, Any]] = []
    _process_scope(tree, "<module>", rel_file, source_lines, records, finder_factory)
    return records


def _iter_test_files(tests_dir: Path = TESTS_DIR) -> list[Path]:
    return sorted(tests_dir.rglob("*.py"))


# ---------------------------------------------------------------------------
# Whole-suite census
# ---------------------------------------------------------------------------


def run_census(tests_dir: Path = TESTS_DIR) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = _iter_test_files(tests_dir)
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in files:
        rel_file = path.relative_to(REPO).as_posix()
        try:
            records.extend(census_one_file(path))
        except Exception as exc:  # noqa: BLE001 -- one bad file must not abort the census
            errors.append({"file": rel_file, "error": f"{type(exc).__name__}: {exc}"})

    records.sort(key=lambda r: (r["file"], r["line_start"], r["col_start"]))

    by_file: dict[str, int] = {}
    by_rule: dict[str, int] = {"a": 0, "b": 0, "c": 0, "d": 0, "e": 0}
    not_in_assert = 0
    for rec in records:
        by_file[rec["file"]] = by_file.get(rec["file"], 0) + 1
        by_rule[rec["binding"]["rule"]] = by_rule.get(rec["binding"]["rule"], 0) + 1
        if not rec["in_assert"]:
            not_in_assert += 1

    summary = {
        "total": len(records),
        "by_file": dict(sorted(by_file.items())),
        "by_binding_rule": by_rule,
        "not_in_assert": not_in_assert,
        "files_scanned": len(files),
        "errors": errors,
    }
    return records, summary


# ---------------------------------------------------------------------------
# PASS A -- the names_of SHAPE: a non-test, non-fixture helper that takes a
# result-shaped parameter (rule d) and subscripts it with a string constant,
# with no guard visible before that subscript. names_of is exactly this
# shape: a plain function (not test_*, not a fixture) whose parameter is
# named ``result``, subscripted once, with nothing guarding the access.
# ---------------------------------------------------------------------------


def is_fixture_function(node: ast.AST) -> bool:
    """True if ``node`` (a FunctionDef/AsyncFunctionDef) carries a decorator
    naming ``fixture`` -- bare (``@fixture``, ``@pytest.fixture``) or called
    (``@pytest.fixture(scope=...)``)."""
    decorators = getattr(node, "decorator_list", [])
    for dec in decorators:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Name) and target.id in FIXTURE_DECORATOR_NAMES:
            return True
        if isinstance(target, ast.Attribute) and target.attr in FIXTURE_DECORATOR_NAMES:
            return True
    return False


class _GuardAwareWalker(ast.NodeVisitor):
    """One pass over ONE candidate function's OWN body (stops at a nested
    def/async def/class, exactly like ``_SubscriptFinder``): finds every
    string-subscript on ``param_names``, plus the four guard SIGNALS the
    brief names -- tracked precisely enough to answer "guards THIS
    subscript, specifically":

      * try/except KeyError, and ``if <x> in P:``       -- BLOCK-scoped:
        true ancestor-nesting (a stack pushed only while visiting the
        protecting block's own body, so a SIBLING statement after the
        block is correctly seen as unprotected by it).
      * ``.get(...)`` on P, an assert naming P            -- FLAT: must
        appear at a line at-or-before the subscript's own line.
      * ``if <x> not in P: <return/raise/continue/break>`` (the early-exit
        "bail out, then use it unconditionally" pattern)  -- FLAT: must
        appear at a STRICTLY earlier line. This one is a POSITIONAL
        heuristic (line order within the function), not a proven
        control-flow-dominance check -- it does not confirm the bail-out
        if and the subscript share a branch. Flagged here and in the
        report; every candidate's full source is carried in the Pass A
        output specifically so this can be confirmed by eye.
    """

    def __init__(self, param_names: set[str]) -> None:
        self.param_names = param_names
        self.sites: list[dict[str, Any]] = []
        self.get_calls: list[tuple[str, int]] = []
        self.assert_lines: list[tuple[str, int]] = []
        self.notin_exit_lines: list[tuple[str, int]] = []
        self._if_in_stack: list[set[str]] = []
        self._try_stack: list[bool] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_If(self, node: ast.If) -> None:
        prot_in = self._names_compared(node.test, ast.In) & self.param_names
        prot_notin = self._names_compared(node.test, ast.NotIn) & self.param_names
        if prot_notin and self._body_terminates(node.body):
            for p in prot_notin:
                self.notin_exit_lines.append((p, node.lineno))
        self._if_in_stack.append(prot_in)
        for stmt in node.body:
            self.visit(stmt)
        self._if_in_stack.pop()
        for stmt in node.orelse:
            self.visit(stmt)

    def visit_Try(self, node: ast.Try) -> None:
        catches = any(self._handles_keyerror(h) for h in node.handlers)
        self._try_stack.append(catches)
        for stmt in node.body:
            self.visit(stmt)
        self._try_stack.pop()
        for h in node.handlers:
            self.visit(h)
        for stmt in node.orelse:
            self.visit(stmt)
        for stmt in node.finalbody:
            self.visit(stmt)

    def visit_Assert(self, node: ast.Assert) -> None:
        mentioned = {n.id for n in ast.walk(node.test) if isinstance(n, ast.Name)}
        for p in mentioned & self.param_names:
            self.assert_lines.append((p, node.lineno))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.param_names
        ):
            self.get_calls.append((node.func.value.id, node.lineno))
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> None:
        key = string_slice_value(node)
        if key is not None and isinstance(node.value, ast.Name) and node.value.id in self.param_names:
            param = node.value.id
            wrapped_if_in = any(param in frame for frame in self._if_in_stack)
            wrapped_try = any(self._try_stack)
            self.sites.append(
                {
                    "node_line": node.lineno,
                    "node_col": node.col_offset,
                    "param": param,
                    "key": key,
                    "wrapped_if_in": wrapped_if_in,
                    "wrapped_try_except": wrapped_try,
                }
            )
        self.generic_visit(node)

    @staticmethod
    def _names_compared(test: ast.AST, op_type: type) -> set[str]:
        """Names compared with ``op_type`` (``ast.In``/``ast.NotIn``) inside
        ``test``, following a top-level ``and``/``or`` chain."""
        out: set[str] = set()

        def walk(expr: ast.AST) -> None:
            if isinstance(expr, ast.Compare):
                for op, comparator in zip(expr.ops, expr.comparators):
                    if isinstance(op, op_type) and isinstance(comparator, ast.Name):
                        out.add(comparator.id)
            elif isinstance(expr, ast.BoolOp):
                for v in expr.values:
                    walk(v)

        walk(test)
        return out

    @staticmethod
    def _body_terminates(body: list[ast.AST]) -> bool:
        return bool(body) and isinstance(body[-1], (ast.Return, ast.Raise, ast.Continue, ast.Break))

    @staticmethod
    def _handles_keyerror(handler: ast.ExceptHandler) -> bool:
        t = handler.type
        if t is None:
            return True  # bare except
        names: list[str] = []
        if isinstance(t, ast.Name):
            names = [t.id]
        elif isinstance(t, ast.Tuple):
            names = [e.id for e in t.elts if isinstance(e, ast.Name)]
        return any(n in ("KeyError", "Exception", "BaseException") for n in names)


def _site_guard_reasons(site: dict[str, Any], walker: _GuardAwareWalker) -> list[str]:
    reasons: list[str] = []
    if site["wrapped_try_except"]:
        reasons.append("try_except_keyerror")
    if site["wrapped_if_in"]:
        reasons.append("if_in")
    line, param = site["node_line"], site["param"]
    for p, ln in walker.get_calls:
        if p == param and ln <= line:
            reasons.append(f"get@{ln}")
    for p, ln in walker.assert_lines:
        if p == param and ln <= line:
            reasons.append(f"assert@{ln}")
    for p, ln in walker.notin_exit_lines:
        if p == param and ln < line:
            reasons.append(f"notin_exit@{ln}")
    return reasons


def analyze_pass_a_function(node: ast.AST, source: str) -> Optional[dict[str, Any]]:
    """``None`` if ``node`` is not a Pass A candidate; else its full row.

    A candidate: a FunctionDef/AsyncFunctionDef, name not starting with
    ``test_``, not fixture-decorated, with >=1 parameter rule (d) already
    classifies as result-shaped (reusing ``param_bindings`` -- the SAME
    function Pass 1 uses for rule d, not a re-derived copy), and >=1
    string-constant subscript directly on that parameter in its own body.
    """
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return None
    if node.name.startswith("test_"):
        return None
    if is_fixture_function(node):
        return None
    qualifying = param_bindings(node)  # [(name, lineno), ...] -- rule (d), reused
    if not qualifying:
        return None
    param_names = {name for name, _ln in qualifying}

    walker = _GuardAwareWalker(param_names)
    for stmt in node.body:
        walker.visit(stmt)
    if not walker.sites:
        return None  # a qualifying param, but never actually subscripted

    sites_out: list[dict[str, Any]] = []
    any_unguarded = False
    for site in walker.sites:
        reasons = _site_guard_reasons(site, walker)
        guarded = bool(reasons)
        any_unguarded = any_unguarded or not guarded
        sites_out.append(
            {
                "line": site["node_line"],
                "col": site["node_col"],
                "param": site["param"],
                "key": site["key"],
                "guarded": guarded,
                "guard_reasons": reasons,
            }
        )
    src = ast.get_source_segment(source, node) or ""
    return {
        "function": node.name,
        "def_line": node.lineno,
        "params": sorted(param_names),
        "sites": sites_out,
        "function_guarded": not any_unguarded,
        "in_defect_set": any_unguarded,
        "source": src,
    }


def run_pass_a(tests_dir: Path = TESTS_DIR) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    files = _iter_test_files(tests_dir)
    for path in files:
        rel_file = path.relative_to(REPO).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=rel_file)
        except Exception as exc:  # noqa: BLE001 -- one bad file must not abort the pass
            errors.append({"file": rel_file, "error": f"{type(exc).__name__}: {exc}"})
            continue
        for node in ast.walk(tree):
            row = analyze_pass_a_function(node, source)
            if row is not None:
                row = dict(row)
                row["file"] = rel_file
                candidates.append(row)

    candidates.sort(key=lambda r: (r["file"], r["def_line"]))
    defect_set = [c for c in candidates if c["in_defect_set"]]
    by_file: dict[str, int] = {}
    for c in candidates:
        by_file[c["file"]] = by_file.get(c["file"], 0) + 1

    summary = {
        "candidate_count": len(candidates),
        "defect_count": len(defect_set),
        "guarded_count": len(candidates) - len(defect_set),
        "by_file": dict(sorted(by_file.items())),
        "files_scanned": len(files),
        "errors": errors,
    }
    return {"summary": summary, "candidates": candidates}


# ---------------------------------------------------------------------------
# PASS B -- which files PRACTISE the .get()-with-whole-result-as-message
# convention, which ones BREAK it (Pass 1's own census), which do both, and
# which do neither -- plus a tokenize-based (never grep) flag for a comment
# block that STATES the convention.
# ---------------------------------------------------------------------------


class _GetHonourFinder(ast.NodeVisitor):
    """Same scope/binding contract as ``_SubscriptFinder`` (constructed and
    driven identically by ``_process_scope``), looking for
    ``<result-bound-name>.get("<literal>")`` calls sitting in an Assert's
    TEST (never its message -- tracked explicitly, not just "somewhere in
    the assert statement"), and classifying that assert's message.
    """

    def __init__(
        self,
        bindings: dict[str, list[tuple[int, str]]],
        enclosing: str,
        rel_file: str,
        source_lines: list[str],
    ) -> None:
        self.bindings = bindings
        self.enclosing = enclosing
        self.rel_file = rel_file
        self.source_lines = source_lines
        self._assert_stack: list[ast.Assert] = []
        self._in_test = False
        self.records: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Assert(self, node: ast.Assert) -> None:
        self._assert_stack.append(node)
        was_in_test = self._in_test
        self._in_test = True
        self.visit(node.test)
        self._in_test = was_in_test
        if node.msg is not None:
            self.visit(node.msg)
        self._assert_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if (
            self._in_test
            and self._assert_stack
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.bindings
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            name = node.func.value.id
            key = node.args[0].value
            current_assert = self._assert_stack[-1]
            msg = current_assert.msg
            strict = isinstance(msg, ast.Name) and msg.id == name
            weak = msg is not None and any(
                isinstance(n, ast.Name) and n.id == name for n in ast.walk(msg)
            )
            src_idx = node.lineno - 1
            source_line = (
                self.source_lines[src_idx].strip()
                if 0 <= src_idx < len(self.source_lines)
                else ""
            )
            self.records.append(
                {
                    "file": self.rel_file,
                    "line": node.lineno,
                    "enclosing": self.enclosing,
                    "name": name,
                    "key": key,
                    "assert_line": current_assert.lineno,
                    "strict": strict,
                    "weak": weak,
                    "msg_text": ast.unparse(msg) if msg is not None else None,
                    "source_line": source_line,
                }
            )
        self.generic_visit(node)


def collect_get_honour_records(
    tests_dir: Path = TESTS_DIR,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in _iter_test_files(tests_dir):
        rel_file = path.relative_to(REPO).as_posix()
        try:
            records.extend(census_one_file(path, finder_factory=_GetHonourFinder))
        except Exception as exc:  # noqa: BLE001 -- one bad file must not abort the pass
            errors.append({"file": rel_file, "error": f"{type(exc).__name__}: {exc}"})
    return records, errors


def file_has_convention_comment(source: str) -> bool:
    """True iff a COMMENT TOKEN (``tokenize``, never grep/regex on raw text)
    anywhere in the file contains ``.get(`` and either ``KeyError`` or
    ``says nothing about what the tool returned`` -- gathered across ALL
    comment tokens in the whole file, not just one line: the real example
    (``test_editor_fields.py``) spreads this across a multi-line ``#:``
    block where each physical line is its OWN COMMENT token, so a
    single-token check would miss it entirely."""
    comments: list[str] = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type == tokenize.COMMENT:
            comments.append(tok.string.lstrip("#").strip())
    blob = " ".join(comments)
    return ".get(" in blob and any(marker in blob for marker in CONVENTION_MARKERS)


def run_pass_b(tests_dir: Path = TESTS_DIR) -> dict[str, Any]:
    honour_records, honour_errors = collect_get_honour_records(tests_dir)
    _breaking_records, breaking_summary = run_census(tests_dir)  # Pass 1, unchanged

    honour_by_file: dict[str, list[dict[str, Any]]] = {}
    for rec in honour_records:
        honour_by_file.setdefault(rec["file"], []).append(rec)

    files = _iter_test_files(tests_dir)
    rows: list[dict[str, Any]] = []
    class_counts = {"PRACTISES": 0, "MIXED": 0, "PURE_SUBSCRIPT": 0, "NEITHER": 0}
    comment_errors: list[dict[str, str]] = []
    for path in files:
        rel_file = path.relative_to(REPO).as_posix()
        h_recs = honour_by_file.get(rel_file, [])
        honouring_strict = sum(1 for r in h_recs if r["strict"])
        honouring_weak = sum(1 for r in h_recs if r["weak"])
        breaking = breaking_summary["by_file"].get(rel_file, 0)

        if honouring_weak >= 1 and breaking == 0:
            cls = "PRACTISES"
        elif honouring_weak >= 1 and breaking >= 1:
            cls = "MIXED"
        elif honouring_weak == 0 and breaking >= 1:
            cls = "PURE_SUBSCRIPT"
        else:
            cls = "NEITHER"
        class_counts[cls] += 1

        try:
            has_comment = file_has_convention_comment(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 -- one bad file must not abort the pass
            has_comment = False
            comment_errors.append({"file": rel_file, "error": f"{type(exc).__name__}: {exc}"})

        rows.append(
            {
                "file": rel_file,
                "honouring_strict": honouring_strict,
                "honouring_weak": honouring_weak,
                "breaking": breaking,
                "class": cls,
                "has_convention_comment": has_comment,
            }
        )

    summary = {
        "files_scanned": len(files),
        "class_counts": class_counts,
        "convention_comment_files": sorted(r["file"] for r in rows if r["has_convention_comment"]),
        "honour_errors": honour_errors,
        "breaking_errors": breaking_summary["errors"],
        "comment_errors": comment_errors,
    }
    return {"summary": summary, "files": rows, "honour_records": honour_records}


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------


def _print_record_line(rec: dict[str, Any]) -> None:
    b = rec["binding"]
    print(
        f"    {rec['file']}:{rec['line']} (start {rec['line_start']}) "
        f"in {rec['enclosing']}()  {rec['name']}[{rec['key']!r}]  "
        f"binding=({b['rule']}@{b['line']}, indirect={b['indirect']})  "
        f"in_assert={rec['in_assert']} has_msg={rec['has_msg']}"
    )
    print(f"      source: {rec['source_line']}")


def _run_control_3(real_source: str) -> dict[str, Any]:
    """Patch the REAL names_of() source in memory and show the record for
    result["fields"] disappear when the subscript becomes a .get() call."""
    tree = ast.parse(real_source, filename="tests/test_editor_fields.py")
    target = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "names_of":
            target = node
            break
    if target is None:
        raise RuntimeError(
            "CONTROL 3 SURPRISE: names_of() was not found in the real source"
        )
    before_src = ast.get_source_segment(real_source, target)
    if not before_src:
        raise RuntimeError("CONTROL 3 SURPRISE: ast.get_source_segment returned nothing")

    before_tree = ast.parse(before_src, filename="<control3-before>")
    before_records: list[dict[str, Any]] = []
    _process_scope(before_tree, "<module>", "<control3-before>", before_src.splitlines(), before_records)

    after_src = before_src.replace('result["fields"]', 'result.get("fields", [])')
    if after_src == before_src:
        raise RuntimeError("CONTROL 3 SURPRISE: the replacement matched nothing in the source")

    after_tree = ast.parse(after_src, filename="<control3-after>")
    after_records: list[dict[str, Any]] = []
    _process_scope(after_tree, "<module>", "<control3-after>", after_src.splitlines(), after_records)

    return {
        "before_source": before_src,
        "after_source": after_src,
        "before_records": before_records,
        "after_records": after_records,
    }


def self_test_pass1() -> int:
    print("=" * 78)
    print("CONTROL 1 -- POSITIVE: the known instance must be found")
    print("=" * 78)
    records, summary = run_census()
    if summary["errors"]:
        print(f"SURPRISE: {len(summary['errors'])} file(s) failed to parse/read:")
        for e in summary["errors"]:
            print(f"  {e['file']}: {e['error']}")
        return 1
    hits = [
        r
        for r in records
        if r["file"] == KNOWN_POSITIVE["file"]
        and r["name"] == KNOWN_POSITIVE["name"]
        and r["key"] == KNOWN_POSITIVE["key"]
    ]
    print(f"  matches for {KNOWN_POSITIVE}: {len(hits)}")
    for rec in hits:
        _print_record_line(rec)
    if not hits:
        print(
            "  CONTROL 1 FAILED -- the known instance was not found. "
            "The instrument is broken; fix the instrument, not this control."
        )
        return 1
    print("  CONTROL 1 PASSED")
    print()

    print("=" * 78)
    print("CONTROL 2 -- NEGATIVE / MUTATION: one true positive, one .get() decoy,")
    print("one non-result-bound decoy, in a synthetic in-memory module")
    print("=" * 78)
    synthetic = textwrap.dedent(
        """\
        async def sample(payload):
            ok = payload["ok"]
            safe = payload.get("ok")
            plain = {"ok": 1}
            bad = plain["ok"]
            return ok, safe, bad
        """
    )
    print("  synthetic module:")
    for line in synthetic.splitlines():
        print(f"    {line}")
    syn_tree = ast.parse(synthetic, filename="<control2-synthetic>")
    syn_records: list[dict[str, Any]] = []
    _process_scope(syn_tree, "<module>", "<control2-synthetic>", synthetic.splitlines(), syn_records)
    names_and_keys = {(r["name"], r["key"]) for r in syn_records}
    print(f"  records found: {len(syn_records)} -> {sorted(names_and_keys)}")
    for rec in syn_records:
        _print_record_line(rec)
    verdict_i = "FOUND (correct)" if ("payload", "ok") in names_and_keys else "MISSING -- WRONG"
    verdict_iii = "absent (correct)" if ("plain", "ok") not in names_and_keys else "FOUND -- WRONG"
    print(f'  (i)   payload["ok"]      (result-bound via param rule d) : {verdict_i}')
    print('  (ii)  payload.get("ok")  (a Call, not a Subscript at all) : '
          "structurally cannot match; not applicable")
    print(f'  (iii) plain["ok"]        (plain is NOT result-bound)     : {verdict_iii}')
    control2_pass = names_and_keys == {("payload", "ok")}
    if not control2_pass:
        print("  CONTROL 2 FAILED")
        return 1
    print("  CONTROL 2 PASSED -- exactly one record, and it is (i)")
    print()

    print("=" * 78)
    print("CONTROL 3 -- SHOW IT GOING QUIET: patch names_of(), watch the record vanish")
    print("=" * 78)
    real_source = (TESTS_DIR / "test_editor_fields.py").read_text(encoding="utf-8")
    c3 = _run_control_3(real_source)
    print("  BEFORE (real names_of source, read from disk):")
    for line in c3["before_source"].splitlines():
        print(f"    {line}")
    print(f"  BEFORE records: {len(c3['before_records'])}")
    for rec in c3["before_records"]:
        _print_record_line(rec)
    print()
    print('  AFTER (result["fields"] replaced with result.get("fields", [])):')
    for line in c3["after_source"].splitlines():
        print(f"    {line}")
    print(f"  AFTER records: {len(c3['after_records'])}")
    for rec in c3["after_records"]:
        _print_record_line(rec)
    control3_pass = len(c3["before_records"]) >= 1 and len(c3["after_records"]) == 0
    print()
    if not control3_pass:
        print("  CONTROL 3 FAILED")
        return 1
    print("  CONTROL 3 PASSED -- present before the patch, gone after it")
    print()

    print("ALL THREE PASS 1 CONTROLS PASSED")
    return 0


def self_test_pass_a() -> int:
    print("=" * 78)
    print("PASS A CONTROL 1 -- POSITIVE: names_of must be in the defect set")
    print("=" * 78)
    result = run_pass_a()
    if result["summary"]["errors"]:
        print(f"SURPRISE: {len(result['summary']['errors'])} file(s) failed to parse:")
        for e in result["summary"]["errors"]:
            print(f"  {e['file']}: {e['error']}")
        return 1
    hits = [
        c
        for c in result["candidates"]
        if c["file"] == "tests/test_editor_fields.py" and c["function"] == "names_of"
    ]
    print(f"  matches: {len(hits)}")
    for c in hits:
        print(
            f"    {c['file']}:{c['def_line']} {c['function']}({', '.join(c['params'])})"
            f"  in_defect_set={c['in_defect_set']}"
        )
        for s in c["sites"]:
            print(
                f"      site line={s['line']} {s['param']}[{s['key']!r}]"
                f"  guarded={s['guarded']} reasons={s['guard_reasons']}"
            )
    ok1 = len(hits) == 1 and hits[0]["in_defect_set"] is True
    if not ok1:
        print(
            "  PASS A CONTROL 1 FAILED -- names_of must be found, exactly once, "
            "and unguarded. The instrument is broken; fix it, not this control."
        )
        return 1
    print("  PASS A CONTROL 1 PASSED")
    print()

    print("=" * 78)
    print("PASS A CONTROL 2 -- NEGATIVE: three synthetic helpers, none in the")
    print("defect set, each for a DIFFERENT reason")
    print("=" * 78)
    synthetic = textwrap.dedent(
        """\
        def helper_a(result):
            if "k" not in result:
                return None
            return result["k"]


        def helper_b(result):
            result.get("k")
            return result["k"]


        def test_helper_c(result):
            return result["k"]
        """
    )
    print("  synthetic module:")
    for line in synthetic.splitlines():
        print(f"    {line}")
    syn_tree = ast.parse(synthetic, filename="<passA-control2-synthetic>")
    syn_candidates: list[dict[str, Any]] = []
    for node in ast.walk(syn_tree):
        row = analyze_pass_a_function(node, synthetic)
        if row is not None:
            syn_candidates.append(row)
    by_name = {c["function"]: c for c in syn_candidates}
    print(f"  candidates found: {sorted(by_name)}")
    for name, c in sorted(by_name.items()):
        print(f"    {name}: in_defect_set={c['in_defect_set']}")
        for s in c["sites"]:
            print(f"      line={s['line']} guarded={s['guarded']} reasons={s['guard_reasons']}")
    verdict_a = (
        "correct (not in defect set, via not-in early exit)"
        if "helper_a" in by_name and not by_name["helper_a"]["in_defect_set"]
        else "WRONG"
    )
    verdict_b = (
        "correct (not in defect set, via .get before the subscript)"
        if "helper_b" in by_name and not by_name["helper_b"]["in_defect_set"]
        else "WRONG"
    )
    verdict_c = (
        "correct (excluded at the test_ name filter, never became a candidate)"
        if "test_helper_c" not in by_name
        else "WRONG -- became a candidate despite its test_ name"
    )
    print(f"  (a) if <k> not in result: <exit>, then subscript : {verdict_a}")
    print(f"  (b) .get(...) before the subscript                : {verdict_b}")
    print(f"  (c) a test_ function subscripting its own result  : {verdict_c}")
    ok2 = (
        "helper_a" in by_name
        and not by_name["helper_a"]["in_defect_set"]
        and "helper_b" in by_name
        and not by_name["helper_b"]["in_defect_set"]
        and "test_helper_c" not in by_name
    )
    if not ok2:
        print("  PASS A CONTROL 2 FAILED")
        return 1
    print("  PASS A CONTROL 2 PASSED")
    print()
    return 0


def self_test_pass_b() -> int:
    print("=" * 78)
    print("PASS B CONTROL -- test_editor_fields.py must classify PRACTISES or MIXED")
    print("=" * 78)
    result = run_pass_b()
    row = next((r for r in result["files"] if r["file"] == "tests/test_editor_fields.py"), None)
    if row is None:
        print("  SURPRISE: tests/test_editor_fields.py not found in Pass B's file list")
        return 1
    print(
        f"  classification: {row['class']}  honouring_strict={row['honouring_strict']}"
        f"  honouring_weak={row['honouring_weak']}  breaking={row['breaking']}"
        f"  has_convention_comment={row['has_convention_comment']}"
    )
    sites = [r for r in result["honour_records"] if r["file"] == "tests/test_editor_fields.py"]
    print(f"  honouring sites found in this file ({len(sites)}):")
    for s in sites:
        print(
            f"    line={s['line']} in {s['enclosing']}()  {s['name']}.get({s['key']!r})"
            f"  strict={s['strict']} weak={s['weak']} msg={s['msg_text']}"
        )
        print(f"      source: {s['source_line']}")
    ok = row["class"] in ("PRACTISES", "MIXED")
    if not ok:
        print(
            "  PASS B CONTROL FAILED -- the honouring-site detector is wrong. "
            "Fix the detector; do not adjust this control."
        )
        return 1
    print("  PASS B CONTROL PASSED")
    print()
    return 0


def self_test() -> int:
    """All controls, all three passes. Writes no file in any mode."""
    r1 = self_test_pass1()
    print()
    r2 = self_test_pass_a()
    print()
    r3 = self_test_pass_b()
    print("=" * 78)
    if r1 == 0 and r2 == 0 and r3 == 0:
        print("ALL CONTROLS PASSED (pass 1: 3, pass A: 2, pass B: 1)")
        return 0
    print(
        f"CONTROL FAILURE -- pass1={'OK' if r1 == 0 else 'FAILED'}  "
        f"passA={'OK' if r2 == 0 else 'FAILED'}  passB={'OK' if r3 == 0 else 'FAILED'}"
    )
    return 1


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def main_pass_a() -> int:
    result = run_pass_a()
    summary = result["summary"]

    PASS_A_JSON.parent.mkdir(parents=True, exist_ok=True)
    with PASS_A_JSON.open("w", encoding="ascii", newline="\n") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    print(f"scanned {summary['files_scanned']} file(s) under tests/")
    if summary["errors"]:
        print(f"PARSE ERRORS ({len(summary['errors'])}) -- these files were NOT analysed:")
        for e in summary["errors"]:
            print(f"  {e['file']}: {e['error']}")
    print()
    print(
        "CANDIDATES (non-test_, non-fixture, rule-d param, "
        f">=1 string subscript on it): {summary['candidate_count']}"
    )
    print(f"  DEFECT SET (>=1 unguarded site)   : {summary['defect_count']}")
    print(f"  guarded (0 unguarded sites)       : {summary['guarded_count']}")
    print()
    if summary["defect_count"]:
        print("DEFECT SET, listed in full:")
        for c in result["candidates"]:
            if not c["in_defect_set"]:
                continue
            print(f"  {c['file']}:{c['def_line']} {c['function']}({', '.join(c['params'])})")
            for s in c["sites"]:
                mark = "OK" if s["guarded"] else "UNGUARDED"
                print(f"    line {s['line']}: {s['param']}[{s['key']!r}]  {mark}  {s['guard_reasons']}")
        print()
    print(f"wrote {PASS_A_JSON.relative_to(REPO).as_posix()}")
    return 1 if summary["errors"] else 0


def main_pass_b() -> int:
    result = run_pass_b()
    summary = result["summary"]

    PASS_B_JSON.parent.mkdir(parents=True, exist_ok=True)
    with PASS_B_JSON.open("w", encoding="ascii", newline="\n") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    print(f"scanned {summary['files_scanned']} file(s) under tests/")
    errs = summary["honour_errors"] + summary["breaking_errors"] + summary["comment_errors"]
    if errs:
        print(f"PARSE ERRORS ({len(errs)}):")
        for e in errs:
            print(f"  {e['file']}: {e['error']}")
    print()
    print("CLASS COUNTS:")
    for cls in ("PRACTISES", "MIXED", "PURE_SUBSCRIPT", "NEITHER"):
        print(f"  {cls:15s} {summary['class_counts'][cls]}")
    print()
    print(f"files with a convention-stating comment (tokenize-detected): "
          f"{len(summary['convention_comment_files'])}")
    for f in summary["convention_comment_files"]:
        print(f"  {f}")
    print()
    for cls in ("PRACTISES", "MIXED"):
        rows = [r for r in result["files"] if r["class"] == cls]
        print(f"{cls} ({len(rows)}):")
        for r in rows:
            print(
                f"  {r['file']:60s} honour(strict={r['honouring_strict']},"
                f"weak={r['honouring_weak']}) breaking={r['breaking']}"
            )
        print()
    print(f"wrote {PASS_B_JSON.relative_to(REPO).as_posix()}")
    return 1 if errs else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run all controls (pass 1 + pass A + pass B) and exit; writes no census file",
    )
    parser.add_argument(
        "--pass-a",
        action="store_true",
        help="run PASS A (names_of-shaped unguarded-helper defect census) and write its JSON",
    )
    parser.add_argument(
        "--pass-b",
        action="store_true",
        help="run PASS B (convention-practice file classification) and write its JSON",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.pass_a:
        return main_pass_a()
    if args.pass_b:
        return main_pass_b()

    records, summary = run_census()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUT_JSON.open("w", encoding="ascii", newline="\n") as fh:
        json.dump({"summary": summary, "records": records}, fh, indent=2, ensure_ascii=True)
        fh.write("\n")

    print(f"scanned {summary['files_scanned']} file(s) under tests/")
    if summary["errors"]:
        print(f"PARSE ERRORS ({len(summary['errors'])}) -- these files were NOT censused:")
        for e in summary["errors"]:
            print(f"  {e['file']}: {e['error']}")
    print()
    print(f"TOTAL RECORDS: {summary['total']}")
    print(f"  not in an assert: {summary['not_in_assert']}")
    print("  by binding rule:")
    for rule in "abcde":
        print(f"    {rule}: {summary['by_binding_rule'].get(rule, 0)}")
    print(f"  by file, {len(summary['by_file'])} file(s) with at least one record "
          "(top 20 by count):")
    for fname, count in sorted(summary["by_file"].items(), key=lambda kv: -kv[1])[:20]:
        print(f"    {count:4d}  {fname}")
    print()
    print(f"wrote {OUT_JSON.relative_to(REPO).as_posix()}")
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
