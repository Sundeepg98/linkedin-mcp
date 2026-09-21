"""AST census: does a value the SESSION or a DEPENDENCY chose reach a string
that ``linkedin_server/auth.py`` then LOGS, RETURNS, or RAISES?

THE ONE QUESTION THIS ANSWERS, stated once so every row below can be read
against it: a name is a TAINTED SOURCE only if it is bound from an
``except ... as name:`` handler (T1), from an ``await``ed call on a
``page`` / ``context`` / ``request`` / ``response`` receiver -- or the
``BROWSER.goto(page, ...)`` shape, which is the one named exception to the
receiver rule (T2) -- or from reading an attribute off such a name (T3). A
tainted name is a HIT only where it (or a multi-hop alias of it, or a
rendered string built from it) reaches one of three sinks: a ``logger.*``
call in any argument position (LOG), a dict-literal value or dict-subscript
assignment whose dict is returned by the same function, directly or as an
argument threaded into that function's own ``return`` call (RETURN), or an
argument to the call inside a ``raise`` statement (RAISE).

WHY AN AST WALK AND NOT A GREP. This file's own log lines use %-style lazy
arguments (``logger.info("...: %s", exc)``) -- the tainted name sits in
argument position 2+, never inside the format-string literal, so a search
that only reads the quoted string sees nothing. And the same exception
object routinely crosses a dict literal (``result = {"reason": f"...{exc}"}``)
and a helper call (``return await _maybe_corroborate(page, result, ...)``)
before it reaches this function's own ``return`` -- a text search has no way
to connect those two lines.

THE METHOD, so a reader can audit it without reading the source below.

A fresh per-function walker processes each module-level ``def`` /
``async def`` in source order, threading a ``name -> TaintInfo`` map forward
through the statements. Branches (``if``/``else``, each ``try`` body and
handler, one pass of a loop body) are each walked from an independent copy
of the pre-branch state, then MERGED BY UNION: a name is tainted after the
branch point if it was made tainted on ANY path into it. This is
deliberately the conservative direction -- a branch that in fact always
returns before reaching the code after it still contributes its state to
that union, which can over-flag but cannot hide a real flow the way an
under-approximation would. A name assigned from a plain literal or from any
expression this walker does not recognise as taint-preserving is dropped
from the map from that point on ("rebound to clean").

Taint propagates through an assignment RHS only for these exact shapes:
a bare tainted Name (direct alias), a tainted Name's ``.attr`` (T3), an
explicit ``str(tainted)`` call, the T1/T2 binding shapes themselves, and
``<list-name>.append(<tainted string-shaped expr>)`` (a documented EXTENSION
beyond the enumerated T1-T3 sources, added because ``linkedin_server/auth.py``
itself builds an error list this way in ``logout()`` -- see LIMITS in the
report for why this one extension exists and nothing broader does). ANY
OTHER call wrapping a tainted argument (``scrub(...)``, ``landing.withheld(...)``,
``.get(...)`` on a dict) is treated as an OPAQUE BOUNDARY: the result is
NOT propagated as tainted. This is a real, named limitation -- see LIMITS --
but it is also what lets the walker correctly stay silent on this file's own
sanctioned sanitisers instead of flagging every use of one as a leak.

A hit's ``renders`` field classifies the INTERPOLATION SITE's syntax, not
the ultimate origin of the value: ``type(x).__name__`` alone is TYPE_ONLY;
a bare tainted Name, ``str(tainted)``, or a tainted Name used as a lazy
``%s``/``.format()``/``.join()`` argument is VALUE; a direct ``x.attr``
expression written AT the interpolation site is ATTR. A name populated
earlier from ``response.status`` (T3) but interpolated later as a bare
``{status}`` is reported VALUE, not ATTR, because the attribute access is
not visible at that use site -- the origin is still shown in the ``source``
column. A single hit can contain more than one rendered part (an f-string
with both a ``type(exc).__name__`` and a bare ``{exc}``); the headline
``renders`` for that row is the WORST part present, by precedence
VALUE > ATTR > TYPE_ONLY, and the full set is kept alongside it.

For the RETURN sink specifically (only), a bare tainted Name or Attribute
used as an entire dict value with NO string-building operation at that site
(``"http_status": status``, ``"failed": failures``) is NOT counted, unless
the name's own origin was itself already a rendered string (e.g. a name
last built from an f-string). The reasoning: an HTTP status code or a raw
list object placed into a JSON-shaped result is not "interpolated into a
string" in the sense the brief asks about; it is a structured field with no
prose construction step to inspect. LOG and RAISE sinks get NO such
exemption -- passing a bare tainted value as a logger argument or a raise
argument counts every time, because logging's own %-substitution (or an
exception's own str()) is the rendering step, whether or not the call site
additionally wraps it.

Usage::

    python scripts/_census_auth_exception_interpolation.py [--json PATH]
    python scripts/_census_auth_exception_interpolation.py --selftest
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGET = REPO_ROOT / "linkedin_server" / "auth.py"

TAINTED_PAGE_RECEIVERS = {"page", "context", "request", "response"}

RENDER_TYPE_ONLY = "TYPE_ONLY"
RENDER_VALUE = "VALUE"
RENDER_ATTR = "ATTR"
_RENDER_PRECEDENCE = {RENDER_VALUE: 0, RENDER_ATTR: 1, RENDER_TYPE_ONLY: 2}

SINK_LOG = "LOG"
SINK_RETURN = "RETURN"
SINK_RAISE = "RAISE"

SHAPE_FSTRING = "F1"
SHAPE_PERCENT = "F2"
SHAPE_FORMAT_JOIN = "F3"
SHAPE_CONCAT = "F4"

LOG_LEVELS = {"debug", "info", "warning", "error", "critical", "exception"}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class TaintInfo:
    kind: str  # "T1" | "T2" | "T3" | "rendered" | "collection"
    origin: str
    origin_line: int


@dataclass
class TaintPart:
    name: str
    kind: str
    render: str
    attr: Optional[str] = None


@dataclass
class SubscriptTaint:
    key: Any
    parts: list
    shapes: set
    line: int
    value_node: ast.AST


@dataclass
class Hit:
    line: int
    function: str
    source: str
    renders: str
    sink: str
    shape: str
    text: str

    def as_dict(self) -> dict:
        return {
            "line": self.line,
            "function": self.function,
            "source": self.source,
            "renders": self.renders,
            "sink": self.sink,
            "shape": self.shape,
            "text": self.text,
        }


@dataclass
class UnresolvedSite:
    line: int
    function: str
    text: str

    def as_dict(self) -> dict:
        return {"line": self.line, "function": self.function, "text": self.text}


# ---------------------------------------------------------------------------
# Small AST helpers, shared by the classifier and the statement walker
# ---------------------------------------------------------------------------


def _chain_root(node: ast.AST) -> tuple:
    """Walk an Attribute chain down to its base.

    Returns ("name", id) when the base is a plain Name, else ("other", node)
    -- the caller decides what "other" means (clean, or UNRESOLVED, per
    context; a Subscript/Call/IfExp base is never guessed at).
    """
    while isinstance(node, ast.Attribute):
        node = node.value
    if isinstance(node, ast.Name):
        return ("name", node.id)
    return ("other", node)


def base_name_of(node: ast.AST) -> Optional[str]:
    kind, val = _chain_root(node)
    return val if kind == "name" else None


def receiver_info(func_expr: ast.AST) -> tuple:
    """For a Call.func, classify the receiver of a method call.

    Returns (root_name_or_None, status), status in
    {"resolved", "unresolved", "not_a_method_call"}.
    """
    if not isinstance(func_expr, ast.Attribute):
        return None, "not_a_method_call"
    kind, val = _chain_root(func_expr.value)
    if kind == "name":
        return val, "resolved"
    return None, "unresolved"


def is_type_name_idiom(node: ast.AST) -> bool:
    """Match `type(<anything>).__name__` exactly -- the SAFE-BY-SPEC shape."""
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "__name__"
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == "type"
    )


def is_bare_str_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
        and not node.keywords
    )


# ---------------------------------------------------------------------------
# The expression classifier -- the discrimination the brief is testing
# ---------------------------------------------------------------------------


def classify_single(node: ast.AST, state: dict) -> list:
    """Classify ONE non-compound expression for a tainted render.

    Handles: the ``type(x).__name__`` idiom, a bare ``str(tainted)`` call, a
    direct ``x.attr`` off a tainted name, and a bare tainted Name. Does NOT
    recurse into f-strings / %-ops / .format()/.join() / +-concat -- that is
    :func:`walk_stringy`'s job, and it calls back into this function for
    each leaf it finds.
    """
    if is_type_name_idiom(node):
        inner = node.value.args[0] if node.value.args else None
        name = base_name_of(inner) if inner is not None else None
        if name and name in state:
            return [TaintPart(name, state[name].kind, RENDER_TYPE_ONLY)]
        return []

    if is_bare_str_call(node):
        name = base_name_of(node.args[0])
        if name and name in state:
            return [TaintPart(name, state[name].kind, RENDER_VALUE)]
        return []

    if isinstance(node, ast.Attribute):
        name = base_name_of(node.value)
        if name and name in state:
            return [TaintPart(name, state[name].kind, RENDER_ATTR, attr=node.attr)]
        return []

    if isinstance(node, ast.Name):
        if node.id in state:
            return [TaintPart(node.id, state[node.id].kind, RENDER_VALUE)]
        return []

    return []


def walk_stringy(node: ast.AST, state: dict, shapes_out: set, parts_out: list) -> None:
    """Recursively find every tainted part rendered by a string-building
    expression: an f-string (F1), a %-BinOp (F2), a .format()/.join() call
    (F3), or a +-concat / bare str() (F4). Appends into shapes_out/parts_out.
    """
    if isinstance(node, ast.JoinedStr):
        shapes_out.add(SHAPE_FSTRING)
        for v in node.values:
            if isinstance(v, ast.FormattedValue):
                parts = classify_single(v.value, state)
                if parts:
                    parts_out.extend(parts)
                else:
                    walk_stringy(v.value, state, shapes_out, parts_out)
        return

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        shapes_out.add(SHAPE_PERCENT)
        right = node.right
        elts = right.elts if isinstance(right, ast.Tuple) else [right]
        for e in elts:
            parts = classify_single(e, state)
            if parts:
                parts_out.extend(parts)
            else:
                walk_stringy(e, state, shapes_out, parts_out)
        return

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        shapes_out.add(SHAPE_CONCAT)
        for side in (node.left, node.right):
            parts = classify_single(side, state)
            if parts:
                parts_out.extend(parts)
            else:
                walk_stringy(side, state, shapes_out, parts_out)
        return

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in ("format", "join")
    ):
        shapes_out.add(SHAPE_FORMAT_JOIN)
        args = list(node.args) + [kw.value for kw in node.keywords]
        for a in args:
            parts = classify_single(a, state)
            if parts:
                parts_out.extend(parts)
            else:
                walk_stringy(a, state, shapes_out, parts_out)
        return

    if is_bare_str_call(node):
        shapes_out.add(SHAPE_CONCAT)
        parts_out.extend(classify_single(node, state))
        return

    # Fallback: a bare tainted Name/Attribute/type-idiom used directly (e.g.
    # as a raw logger argument with no additional wrapping).
    parts_out.extend(classify_single(node, state))


def choose_headline_render(parts: list) -> str:
    kinds = {p.render for p in parts}
    headline = min(kinds, key=lambda k: _RENDER_PRECEDENCE[k])
    if len(kinds) > 1:
        return headline + " (" + "+".join(sorted(kinds, key=lambda k: _RENDER_PRECEDENCE[k])) + ")"
    return headline


def is_string_shaped_hit(parts: list, shapes: set) -> bool:
    """Gate applied ONLY to the RETURN sink (see module docstring): a bare
    tainted value with no string-building operation at the dict-value /
    subscript site counts only if its own origin was already a rendered
    string (a passthrough of prose built earlier), never a raw object.
    """
    if shapes:
        return True
    if parts and all(p.kind == "rendered" for p in parts):
        return True
    return False


def source_repr(parts: list) -> str:
    seen = []
    for p in sorted(parts, key=lambda p: (p.name, p.kind)):
        tag = f"{p.name} ({p.kind}" + (f", .{p.attr}" if p.attr else "") + ")"
        if tag not in seen:
            seen.append(tag)
    return "; ".join(seen)


# ---------------------------------------------------------------------------
# The per-function walker
# ---------------------------------------------------------------------------


class Walker:
    def __init__(self, source: str):
        self.source = source
        self.hits: list = []
        self.unresolved: list = []
        self.func_name = "<module>"
        self.dict_literal_taint: dict = {}
        self.subscript_taint: dict = {}
        self.returned_names: set = set()

    # -- text -----------------------------------------------------------
    def text_of(self, node: ast.AST) -> str:
        seg = ast.get_source_segment(self.source, node)
        if seg is None:
            return "<unavailable>"
        return " ".join(seg.split())

    def key_text(self, node: ast.AST):
        if isinstance(node, ast.Constant):
            return node.value
        seg = ast.get_source_segment(self.source, node)
        return seg if seg else "<key>"

    # -- entry point ------------------------------------------------------
    def census_function(self, node) -> None:
        prev = (
            self.func_name,
            self.dict_literal_taint,
            self.subscript_taint,
            self.returned_names,
        )
        self.func_name = node.name
        self.dict_literal_taint = {}
        self.subscript_taint = {}
        self.returned_names = set()

        self.walk_block(node.body, {})

        for name in self.returned_names:
            for entry in self.dict_literal_taint.get(name, []):
                self.emit_hit_from_entry(entry, SINK_RETURN)
            for entry in self.subscript_taint.get(name, []):
                self.emit_hit_from_entry(entry, SINK_RETURN)

        (
            self.func_name,
            self.dict_literal_taint,
            self.subscript_taint,
            self.returned_names,
        ) = prev

    # -- block / statement walk -------------------------------------------
    def walk_block(self, stmts: list, state: dict) -> dict:
        state = dict(state)
        for stmt in stmts:
            state = self.walk_stmt(stmt, state)
        return state

    def walk_stmt(self, stmt: ast.AST, state: dict) -> dict:
        if isinstance(stmt, ast.Try):
            s0 = dict(state)
            s_try = self.walk_block(stmt.body, dict(s0))
            candidates = [s_try]
            for h in stmt.handlers:
                s_h = dict(s0)
                if h.name:
                    s_h[h.name] = TaintInfo("T1", f"except ... as {h.name}", h.lineno)
                s_h = self.walk_block(h.body, s_h)
                candidates.append(s_h)
            merged = self._union_merge(candidates)
            if stmt.orelse:
                merged = self.walk_block(stmt.orelse, merged)
            if stmt.finalbody:
                merged = self.walk_block(stmt.finalbody, merged)
            return merged

        if isinstance(stmt, ast.If):
            s0 = dict(state)
            s_then = self.walk_block(stmt.body, dict(s0))
            s_else = self.walk_block(stmt.orelse, dict(s0)) if stmt.orelse else dict(s0)
            return self._union_merge([s_then, s_else])

        if isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
            s0 = dict(state)
            s_body = self.walk_block(stmt.body, dict(s0))
            merged = self._union_merge([s0, s_body])
            if stmt.orelse:
                merged = self.walk_block(stmt.orelse, merged)
            return merged

        if isinstance(stmt, (ast.With, ast.AsyncWith)):
            return self.walk_block(stmt.body, state)

        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            return self.handle_assign(stmt, state)

        if isinstance(stmt, ast.AugAssign):
            return self.handle_augassign(stmt, state)

        if isinstance(stmt, ast.Expr):
            self.handle_expr_stmt(stmt, state)
            return state

        if isinstance(stmt, ast.Return):
            self.handle_return(stmt, state)
            return state

        if isinstance(stmt, ast.Raise):
            self.handle_raise(stmt, state)
            return state

        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.census_function(stmt)
            return state

        return state

    @staticmethod
    def _union_merge(states: list) -> dict:
        merged: dict = {}
        for s in states:
            for k, v in s.items():
                if k not in merged:
                    merged[k] = v
        return merged

    # -- assignment ---------------------------------------------------------
    def handle_assign(self, stmt, state: dict) -> dict:
        state = dict(state)
        if isinstance(stmt, ast.AnnAssign):
            targets = [stmt.target]
            value = stmt.value
        else:
            targets = stmt.targets
            value = stmt.value
        if value is None:
            return state

        if len(targets) == 1 and isinstance(targets[0], ast.Subscript):
            self.handle_subscript_assign(targets[0], value, state, stmt.lineno)
            return state

        if len(targets) == 1 and isinstance(targets[0], ast.Attribute):
            return state  # not a pattern this file uses; no taint tracking

        if len(targets) == 1 and isinstance(targets[0], ast.Tuple):
            elt_names = [e.id for e in targets[0].elts if isinstance(e, ast.Name)]
            tainted = self._try_t2(value, stmt.lineno)
            for name in elt_names:
                if tainted:
                    state[name] = tainted
                else:
                    state.pop(name, None)
            return state

        name_targets = [t.id for t in targets if isinstance(t, ast.Name)]
        if not name_targets:
            return state

        if isinstance(value, ast.Dict):
            for nm in name_targets:
                self.record_dict_literal(nm, value, state)
                state.pop(nm, None)
            return state

        if (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "dict"
        ):
            for nm in name_targets:
                state.pop(nm, None)
            return state

        t2 = self._try_t2(value, stmt.lineno)
        if t2:
            for nm in name_targets:
                state[nm] = t2
            return state

        if isinstance(value, ast.Attribute):
            root = base_name_of(value.value)
            if root and root in state:
                for nm in name_targets:
                    state[nm] = TaintInfo("T3", f"{root}.{value.attr}", stmt.lineno)
                return state

        if isinstance(value, ast.Name) and value.id in state:
            src = state[value.id]
            for nm in name_targets:
                state[nm] = TaintInfo(src.kind, f"alias of {value.id}", stmt.lineno)
            return state

        shapes_found: set = set()
        parts_found: list = []
        walk_stringy(value, state, shapes_found, parts_found)
        if parts_found:
            for nm in name_targets:
                state[nm] = TaintInfo("rendered", f"built at line {stmt.lineno}", stmt.lineno)
            return state

        for nm in name_targets:
            state.pop(nm, None)
        return state

    def _try_t2(self, value: ast.AST, lineno: int) -> Optional[TaintInfo]:
        """Recognise the T2 await shapes. Returns a TaintInfo or None; also
        records an UNRESOLVED site when an awaited method call's receiver
        cannot be reduced to a simple dotted name.
        """
        if not isinstance(value, ast.Await):
            return None
        call_expr = value.value
        if not isinstance(call_expr, ast.Call) or not isinstance(call_expr.func, ast.Attribute):
            return None

        root, status = receiver_info(call_expr.func)
        method = call_expr.func.attr

        if status == "unresolved":
            self.unresolved.append(
                UnresolvedSite(lineno, self.func_name, self.text_of(call_expr))
            )
            return None

        if root in TAINTED_PAGE_RECEIVERS:
            return TaintInfo("T2", f"await {root}.{method}(...)", lineno)

        if method == "goto" and call_expr.args:
            first = call_expr.args[0]
            first_name = first.id if isinstance(first, ast.Name) else None
            if first_name in TAINTED_PAGE_RECEIVERS:
                return TaintInfo(
                    "T2", f"await {root}.goto({first_name}, ...)", lineno
                )

        return None

    def handle_augassign(self, stmt: ast.AugAssign, state: dict) -> dict:
        state = dict(state)
        if not isinstance(stmt.target, ast.Name) or not isinstance(stmt.op, ast.Add):
            return state
        name = stmt.target.id
        shapes_found: set = set()
        parts_found: list = []
        walk_stringy(stmt.value, state, shapes_found, parts_found)
        shapes_found.add(SHAPE_CONCAT)
        if name in state or parts_found:
            if parts_found:
                state[name] = TaintInfo("rendered", f"+= built at line {stmt.lineno}", stmt.lineno)
            # else: name was already tainted (or not); += with a clean RHS
            # leaves an already-tainted prefix tainted (conservative), and a
            # clean name stays absent -- no change needed either way.
        return state

    def record_dict_literal(self, name: str, dict_node: ast.Dict, state: dict) -> None:
        entries = self.classify_dict_literal(dict_node, state)
        if entries:
            self.dict_literal_taint.setdefault(name, []).extend(entries)

    def classify_dict_literal(self, dict_node: ast.Dict, state: dict) -> list:
        entries = []
        for k, v in zip(dict_node.keys, dict_node.values):
            if k is None:
                continue  # a **spread; not walked (see LIMITS)
            shapes_found: set = set()
            parts_found: list = []
            walk_stringy(v, state, shapes_found, parts_found)
            if parts_found and is_string_shaped_hit(parts_found, shapes_found):
                entries.append(
                    SubscriptTaint(self.key_text(k), parts_found, shapes_found, v.lineno, v)
                )
        return entries

    def handle_subscript_assign(self, target: ast.Subscript, value: ast.AST, state: dict, lineno: int) -> None:
        dict_name = base_name_of(target.value)
        if not dict_name:
            return
        shapes_found: set = set()
        parts_found: list = []
        walk_stringy(value, state, shapes_found, parts_found)
        if parts_found and is_string_shaped_hit(parts_found, shapes_found):
            key = self.key_text(target.slice)
            self.subscript_taint.setdefault(dict_name, []).append(
                SubscriptTaint(key, parts_found, shapes_found, lineno, value)
            )

    # -- statements that are themselves calls ------------------------------
    def handle_expr_stmt(self, stmt: ast.Expr, state: dict) -> None:
        call = stmt.value
        if isinstance(call, ast.Await):
            call = call.value
        if not isinstance(call, ast.Call):
            return

        if (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "logger"
            and call.func.attr in LOG_LEVELS
        ):
            self._handle_log_call(stmt.lineno, call, state)
            return

        if (
            isinstance(call.func, ast.Attribute)
            and call.func.attr == "append"
            and isinstance(call.func.value, ast.Name)
            and call.args
        ):
            list_name = call.func.value.id
            shapes_found: set = set()
            parts_found: list = []
            walk_stringy(call.args[0], state, shapes_found, parts_found)
            if parts_found:
                state[list_name] = TaintInfo(
                    "collection", f".append() at line {stmt.lineno}", stmt.lineno
                )

    def _handle_log_call(self, lineno: int, call: ast.Call, state: dict) -> None:
        all_parts: list = []
        all_shapes: set = set()
        for a in list(call.args) + [kw.value for kw in call.keywords]:
            shapes_found: set = set()
            parts_found: list = []
            walk_stringy(a, state, shapes_found, parts_found)
            all_parts.extend(parts_found)
            all_shapes |= shapes_found
        if not all_parts:
            return
        if (
            call.args
            and isinstance(call.args[0], ast.Constant)
            and isinstance(call.args[0].value, str)
            and len(call.args) > 1
        ):
            all_shapes.add(SHAPE_PERCENT)
        self._emit(lineno, SINK_LOG, all_parts, all_shapes, call)

    def handle_return(self, stmt: ast.Return, state: dict) -> None:
        value = stmt.value
        if value is None:
            return

        if isinstance(value, ast.Dict):
            for entry in self.classify_dict_literal(value, state):
                self.emit_hit_from_entry(entry, SINK_RETURN)
            return

        call_expr = value.value if isinstance(value, ast.Await) else value

        if isinstance(value, ast.Name):
            self.returned_names.add(value.id)
            return

        if isinstance(call_expr, ast.Call):
            for a in list(call_expr.args) + [kw.value for kw in call_expr.keywords]:
                if isinstance(a, ast.Name):
                    self.returned_names.add(a.id)
                elif isinstance(a, ast.Dict):
                    # An inline dict literal handed DIRECTLY as an argument
                    # to the call this function returns -- e.g.
                    # `return await _maybe_corroborate(page, {...}, ...)`.
                    # Distinct from the Name case above: there is no
                    # intermediate variable to defer through, so classify
                    # and emit immediately rather than queuing by name.
                    for entry in self.classify_dict_literal(a, state):
                        self.emit_hit_from_entry(entry, SINK_RETURN)

    def handle_raise(self, stmt: ast.Raise, state: dict) -> None:
        exc = stmt.exc
        if exc is None or not isinstance(exc, ast.Call):
            return
        all_parts: list = []
        all_shapes: set = set()
        for a in list(exc.args) + [kw.value for kw in exc.keywords]:
            shapes_found: set = set()
            parts_found: list = []
            walk_stringy(a, state, shapes_found, parts_found)
            all_parts.extend(parts_found)
            all_shapes |= shapes_found
        if all_parts:
            self._emit(stmt.lineno, SINK_RAISE, all_parts, all_shapes, exc)

    # -- hit emission -------------------------------------------------------
    def _emit(self, line: int, sink: str, parts: list, shapes: set, node: ast.AST) -> None:
        self.hits.append(
            Hit(
                line=line,
                function=self.func_name,
                source=source_repr(parts),
                renders=choose_headline_render(parts),
                sink=sink,
                shape=",".join(sorted(shapes)) if shapes else "(none)",
                text=self.text_of(node),
            )
        )

    def emit_hit_from_entry(self, entry: SubscriptTaint, sink: str) -> None:
        self.hits.append(
            Hit(
                line=entry.value_node.lineno,
                function=self.func_name,
                source=source_repr(entry.parts),
                renders=choose_headline_render(entry.parts),
                sink=sink,
                shape=",".join(sorted(entry.shapes)) if entry.shapes else "(none)",
                text=f"{entry.key!r}: {self.text_of(entry.value_node)}",
            )
        )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def census_source(source: str, filename: str) -> tuple:
    tree = ast.parse(source, filename=filename)
    walker = Walker(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            walker.census_function(node)
    # sort for stable, readable output
    hits = sorted(walker.hits, key=lambda h: (h.line, h.sink))
    unresolved = sorted(walker.unresolved, key=lambda u: u.line)
    return hits, unresolved


def print_table(hits: list, unresolved: list, target: str) -> None:
    print(f"# AST census: {target}")
    print(f"# {len(hits)} hit(s), {len(unresolved)} unresolved receiver(s)")
    print()
    header = ("line", "function", "renders", "sink", "shape", "source", "text")
    print(" | ".join(header))
    for h in hits:
        text = h.text if len(h.text) <= 100 else h.text[:97] + "..."
        print(
            " | ".join(
                [str(h.line), h.function, h.renders, h.sink, h.shape, h.source, text]
            )
        )
    print()
    totals: dict = {}
    for h in hits:
        key = (h.renders.split(" ")[0], h.sink)
        totals[key] = totals.get(key, 0) + 1
    print("# totals by (renders x sink)")
    for (renders, sink), n in sorted(totals.items()):
        print(f"  {renders:10s} x {sink:7s} : {n}")
    if unresolved:
        print()
        print("# UNRESOLVED receivers (folded into neither bucket, counted here):")
        for u in unresolved:
            print(f"  line {u.line} in {u.function}: {u.text}")


# ---------------------------------------------------------------------------
# Selftest -- an inline fixture manufactured in this file, never read from
# ambient repo state, never read from auth.py.
# ---------------------------------------------------------------------------

SELFTEST_FIXTURE = '''
import logging

logger = logging.getLogger(__name__)


async def type_only_log_example(page):
    """One TYPE_ONLY log: only the exception's class name is rendered."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        logger.info("request failed: %s", type(exc).__name__)
        return {"ok": False}
    return {"ok": True, "status": response.status}


async def value_log_lazy_percent_example(page):
    """One VALUE log reached via lazy %-style logger arguments."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        logger.info("request failed: %s", exc)
        return {"ok": False}
    return {"ok": True}


async def value_return_fstring_dict_example(page):
    """One VALUE return: an f-string inside a dict literal that is
    returned two calls later (Case: threaded through a helper's return)."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        result = {"ok": False, "reason": f"failed: {exc}"}
        return _wrap(result)
    return {"ok": True}


def _wrap(result):
    return result


async def value_return_inline_dict_threaded_example(page):
    """One VALUE return where the tainted dict is built INLINE as an
    argument to the function's own return call, with no intermediate name
    -- the auth.py shape this check exists because a first draft of this
    walker missed (`return await _maybe_corroborate(page, {...}, ...)`)."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        return _wrap({"ok": False, "reason": f"failed inline: {exc}"})
    return {"ok": True}


async def value_raise_example(page):
    """One VALUE raise: the exception's own text re-raised as a new one."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        raise RuntimeError(f"could not read: {exc}") from exc
    return {"ok": True}


async def dict_subscript_sink_example(page):
    """One dict-subscript assignment sink, returned directly."""
    out = {"ok": False}
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        out["reason"] = f"failed: {exc}"
    return out


async def multi_hop_alias_example(page):
    """One multi-hop alias: exc -> first_alias -> second_alias -> raise."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        first_alias = exc
        second_alias = first_alias
        raise RuntimeError(f"aliased: {second_alias}") from exc
    return {"ok": True}


async def rebound_to_clean_example(page):
    """One rebind-to-clean: a tainted local is overwritten with a literal
    before it reaches the logger, so the census must NOT flag this line."""
    try:
        response = await page.request.get("https://example.invalid")
    except Exception as exc:
        message = f"failed: {exc}"
        message = "a fixed, non-tainted message"
        logger.info("safe now: %s", message)
    return {"ok": True}


async def unresolvable_receiver_example(get_page):
    """One deliberately unresolvable receiver: the awaited call's receiver
    is a Call result, not a simple dotted name, so T2 cannot be decided."""
    try:
        response = await get_page().request.get("https://example.invalid")
    except Exception as exc:
        logger.info("unresolvable case: %s", exc)
    return {"ok": True}
'''


def _find(hits: list, function: str):
    return [h for h in hits if h.function == function]


def run_selftest(mutate: bool = False) -> bool:
    """Runs the fixture through the census and asserts each expected
    verdict. `mutate=True` deliberately breaks one expectation, to prove
    this control can fail (see the report's CONTROL section).
    """
    hits, unresolved = census_source(SELFTEST_FIXTURE, "<selftest-fixture>")

    checks = []

    def check(label, condition):
        checks.append((label, bool(condition)))

    type_only = _find(hits, "type_only_log_example")
    check(
        "type_only_log_example: exactly one LOG hit, renders TYPE_ONLY",
        len(type_only) == 1
        and type_only[0].sink == SINK_LOG
        and type_only[0].renders == (RENDER_VALUE if mutate else RENDER_TYPE_ONLY),
    )

    value_log = _find(hits, "value_log_lazy_percent_example")
    check(
        "value_log_lazy_percent_example: one LOG hit, renders VALUE, shape includes F2",
        len(value_log) == 1
        and value_log[0].sink == SINK_LOG
        and value_log[0].renders == RENDER_VALUE
        and SHAPE_PERCENT in value_log[0].shape,
    )

    value_return = _find(hits, "value_return_fstring_dict_example")
    check(
        "value_return_fstring_dict_example: one RETURN hit, renders VALUE, shape F1",
        len(value_return) == 1
        and value_return[0].sink == SINK_RETURN
        and value_return[0].renders == RENDER_VALUE
        and value_return[0].shape == SHAPE_FSTRING,
    )

    inline_threaded = _find(hits, "value_return_inline_dict_threaded_example")
    check(
        "value_return_inline_dict_threaded_example: one RETURN hit (inline dict, no intermediate name)",
        len(inline_threaded) == 1
        and inline_threaded[0].sink == SINK_RETURN
        and inline_threaded[0].renders == RENDER_VALUE,
    )

    value_raise = _find(hits, "value_raise_example")
    check(
        "value_raise_example: one RAISE hit, renders VALUE",
        len(value_raise) == 1
        and value_raise[0].sink == SINK_RAISE
        and value_raise[0].renders == RENDER_VALUE,
    )

    subscript = _find(hits, "dict_subscript_sink_example")
    check(
        "dict_subscript_sink_example: one RETURN hit via subscript assignment",
        len(subscript) == 1
        and subscript[0].sink == SINK_RETURN
        and "'reason'" in subscript[0].text,
    )

    alias = _find(hits, "multi_hop_alias_example")
    check(
        "multi_hop_alias_example: one RAISE hit, source names second_alias (2-hop)",
        len(alias) == 1
        and alias[0].sink == SINK_RAISE
        and "second_alias" in alias[0].source,
    )

    rebound = _find(hits, "rebound_to_clean_example")
    check(
        "rebound_to_clean_example: NO hit at all (rebind-to-clean must hold)",
        len(rebound) == 0,
    )

    # The fixture's except-handler ALSO logs `exc` directly -- that is a
    # genuine, independent T1 LOG hit and must still fire. What must NOT
    # happen is `response` (bound from the unresolvable receiver) being
    # folded into either the tainted or the clean bucket: it must produce
    # an UNRESOLVED entry instead of silently defaulting to clean.
    unresolved_here = [u for u in unresolved if u.function == "unresolvable_receiver_example"]
    unresolved_hits = _find(hits, "unresolvable_receiver_example")
    check(
        "unresolvable_receiver_example: one UNRESOLVED receiver (the awaited call)",
        len(unresolved_here) == 1
        and "get_page()" in unresolved_here[0].text,
    )
    check(
        "unresolvable_receiver_example: the handler's OWN exc log still fires (LOG, VALUE)",
        len(unresolved_hits) == 1
        and unresolved_hits[0].sink == SINK_LOG
        and unresolved_hits[0].renders == RENDER_VALUE,
    )

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    for label, ok in checks:
        print(("PASS" if ok else "FAIL") + f": {label}")
    print(f"SELFTEST {passed}/{total}")
    return passed == total


# ---------------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", metavar="PATH", help="write machine-readable rows here")
    parser.add_argument(
        "--selftest", action="store_true", help="run the inline fixture control and exit"
    )
    parser.add_argument(
        "--selftest-mutate",
        action="store_true",
        help=(
            "run --selftest with one expectation deliberately inverted (the "
            "type_only_log_example check), to prove the control can fail. "
            "For the report's CONTROL section only -- exits 1 by design."
        ),
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help="file to census (default: linkedin_server/auth.py)",
    )
    args = parser.parse_args(argv)

    if args.selftest_mutate:
        ok = run_selftest(mutate=True)
        return 0 if ok else 1

    if args.selftest:
        ok = run_selftest()
        return 0 if ok else 1

    target = Path(args.target)
    source = target.read_text(encoding="utf-8")
    hits, unresolved = census_source(source, str(target))

    try:
        rel = target.relative_to(REPO_ROOT)
    except ValueError:
        rel = target
    print_table(hits, unresolved, str(rel).replace("\\", "/"))

    if args.json:
        payload = {
            "target": str(rel).replace("\\", "/"),
            "hits": [h.as_dict() for h in hits],
            "unresolved": [u.as_dict() for u in unresolved],
        }
        Path(args.json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\n# wrote {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
