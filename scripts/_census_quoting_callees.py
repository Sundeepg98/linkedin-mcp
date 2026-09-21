"""Census: which STDLIB CALLABLES quote their refused input, and where this
package calls them.

## THE CLASS THIS COUNTS, stated once (inherited from coerce.py's finding)

``int()`` writes the value it refused VERBATIM into its own ``ValueError``::

    ValueError: invalid literal for int() with base 10: '<a label from the page>'

That exception leaves the reader, ``server._error`` catches it, and
``config.scrub`` substitutes THIS SERVER'S OWN FILESYSTEM PATHS and nothing
else -- a person's name has no shape to scrub, so it reaches the caller
intact. ``linkedin_server/coerce.py`` closed this for ``int``. This census
asks the wider question: WHICH OTHER STDLIB CALLABLES SHARE THE PROPERTY, and
where in this package are they actually called.

## PART 1 IS A MEASUREMENT, NOT A GUESS

Every candidate below is CALLED, in this interpreter, with a distinctive ASCII
sentinel, inside a try/except, and the verdict is whatever ``str(exc)``
actually contains. Two pairs in the candidate list exist SPECIFICALLY because
they look alike and are not: ``list.remove`` raises a STATIC message
(``"list.remove(x): x not in list"``, no interpolation) while ``list.index``
interpolates ``repr(x)`` into ``"... is not in list"``; ``str.index`` raises
the static ``"substring not found"`` while ``list.index`` does not. A census
that assumed attribute-name alone decided quoting would have been wrong on
both. This was RE-MEASURED here rather than trusted from memory, and the
directly-run smoke test before this file was written confirmed exactly this
divergence.

## PART 2: WHERE THE PROVEN-QUOTING CALLABLES ARE ACTUALLY CALLED

An AST walk over ``linkedin_server/*.py`` (never ``tests/`` or ``scripts/``).
Two resolution strategies, used for different call shapes:

* MODULE-QUALIFIED calls (``re.compile``, ``json.loads``, ``uuid.UUID``,
  ``ipaddress.ip_address``, ``decimal.Decimal``, and bare builtins ``int``/
  ``float``/``complex``/``getattr``) are resolved through each file's OWN
  import table, so ``import re; re.compile(...)`` matches and an unrelated
  object with a same-named ``.compile()`` method does not.
* METHOD-STYLE calls whose receiver's type cannot be known statically
  (``.index``, ``.remove``, ``.fromhex``, ``.pop``) are matched by ATTRIBUTE
  NAME ALONE, the same heuristic ``scripts/_census_page_coercions.py`` already
  uses for ``.strptime``/``.fromisoformat``/``.index``. This is a KNOWN
  OVER-APPROXIMATION for ``.index`` specifically: a call on a proven-safe
  receiver (a string) cannot be distinguished here from a call on a
  proven-hazardous one (a list), and the census says so rather than hiding it.

## ARGUMENT SOURCE CLASSIFICATION -- DELIBERATELY NARROW, NOT A DATAFLOW ENGINE

Four buckets, applied to the ONE argument each callee family actually quotes
(``args[0]`` for most; ``args[1]`` for ``getattr``, because the exception
quotes the ATTRIBUTE NAME, never the object; the subscript key for ``x[y]``):

  LITERAL        -- a constant, or a bare Name resolving to a module-level
                    constant that is not shadowed locally.
  LOCAL_COMPUTED -- a bare Name bound somewhere in the IMMEDIATE enclosing
                    function, with no page/param origin this walk can see.
  PAGE_OR_ARG    -- a parameter of the immediate enclosing function; OR a name
                    assigned from ``await <expr>`` where the awaited chain's
                    ROOT identifier is ``page``/``locator``/``el``/``node``/
                    ``handle``; OR a ``.get(...)`` call or subscript ONE HOP
                    off a name already in this set.
  UNCLASSIFIED   -- anything this narrow walk does not recognise.

"Immediate enclosing function" means the walk does NOT climb into an outer
function's parameters for a nested ``def``, and it does NOT chase a value
through a ``.append()`` into a list built across a loop. Both are real gaps,
not lies-by-omission: the module docstring's own worked example
(``groups_page.py``'s ``remaining.remove(href)``) is a genuine, manually
confirmed PAGE_OR_ARG site by inspection that THIS classifier scores
LOCAL_COMPUTED, because ``href`` reaches it through a ``for href in
with_control`` loop over a list built by repeated ``.append(await ...)``
calls -- one indirection past what the brief's rules cover. UNCLASSIFIED is
therefore reported IN FULL, per site, rather than forced toward zero.

## WHY ANNOTATIONS ARE EXCLUDED FROM BOTH WALKS

This package writes ``from __future__ import annotations`` and modern hints
everywhere: ``-> dict[str, Any]``, ``x: Optional[int]``. Those are
``ast.Subscript`` nodes INDISTINGUISHABLE in shape from a real dict/list
access. A subscript census that did not exclude ``FunctionDef.returns``,
argument ``.annotation`` fields and ``AnnAssign.annotation`` would report
thousands of type hints as "possible KeyError" sites. Both walks in this file
visit a function's decorators, default values and body, and SKIP its
annotations and return type on purpose.

    venv/Scripts/python scripts/_census_quoting_callees.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

SENTINEL = "ZZQUOTESENTINELZZ"


# ---------------------------------------------------------------------------
# PART 1 -- prove the quoting property by running it
# ---------------------------------------------------------------------------


def _probe_urlparse() -> tuple[str, bool, str]:
    import urllib.parse

    try:
        urllib.parse.urlparse(SENTINEL)
    except Exception as exc:  # noqa: BLE001 -- the exception is the subject
        return type(exc).__name__, SENTINEL in str(exc), ""
    return "(no exception raised)", False, "urlparse did not raise on the sentinel, as expected"


def _probe_str_encode() -> tuple[str, bool, str]:
    # A lone surrogate cannot be UTF-8 encoded. Sentinel is placed as a
    # PREFIX so a message that ever echoed surrounding text would show it.
    bad = SENTINEL + "\ud800"
    try:
        bad.encode("utf-8")
    except Exception as exc:  # noqa: BLE001
        return type(exc).__name__, SENTINEL in str(exc), "bad = SENTINEL + one lone surrogate"
    return "(no exception raised)", False, "encode did not raise (unexpected)"


def _probe_list_pop_index() -> tuple[str, bool, str]:
    """``list.pop(index)`` takes an INT, so the string sentinel cannot stand
    in directly -- a distinctive out-of-range integer is used instead, found
    necessary only after the AST census turned up real ``.pop(index)`` call
    sites that ``dict.pop(key)`` alone (the brief's own candidate) does not
    speak for. Same family, different receiver, and (as with
    ``list.remove``/``set.remove``) not the same behaviour.
    """
    marker = 999999
    try:
        [1, 2, 3].pop(marker)
    except Exception as exc:  # noqa: BLE001
        return (
            type(exc).__name__,
            str(marker) in str(exc),
            f"marker={marker}, an int standing in for the sentinel (an index cannot be a string)",
        )
    return "(no exception raised)", False, "did not raise (unexpected)"


def _probe_str_decode() -> tuple[str, bool, str]:
    # 0xFF is never a valid UTF-8 start byte; it fails at position 0, before
    # any sentinel bytes would be reached.
    bad = b"\xff" + SENTINEL.encode("ascii")
    try:
        bad.decode("utf-8")
    except Exception as exc:  # noqa: BLE001
        return type(exc).__name__, SENTINEL in str(exc), "bad = b'\\xff' + SENTINEL.encode('ascii')"
    return "(no exception raised)", False, "decode did not raise (unexpected)"


def probe_quoting() -> list[dict[str, Any]]:
    """Call each candidate for real; report whether the sentinel survived.

    Three rows are NOT from the brief's own list and are added here, each
    flagged ``added=True`` in its row: ``str.index`` (contrasted against
    ``list.index``), ``set.remove`` (contrasted against ``list.remove``, a
    different exception TYPE), and ``dict.pop`` with no default (a KeyError
    reachable through a METHOD call, which the brief's subscript table
    ``x[y]`` cannot see since ``.pop(...)`` is a ``Call``, not a
    ``Subscript``).
    """
    import decimal
    import datetime
    import enum
    import ipaddress
    import json
    import uuid

    class _ProbeEnum(enum.Enum):
        A = 1

    def _run(label: str, fn, added: bool = False) -> dict[str, Any]:
        try:
            fn()
        except BaseException as exc:  # noqa: BLE001 -- the exception is the subject
            return {
                "label": label,
                "raised": type(exc).__name__,
                "echoed": SENTINEL in str(exc),
                "added": added,
            }
        return {"label": label, "raised": "(no exception raised)", "echoed": False, "added": added}

    rows: list[dict[str, Any]] = []
    rows.append(_run("int(s)", lambda: int(SENTINEL)))
    rows.append(_run("float(s)", lambda: float(SENTINEL)))
    rows.append(_run("complex(s)", lambda: complex(SENTINEL)))
    rows.append(_run("decimal.Decimal(s)", lambda: decimal.Decimal(SENTINEL)))
    rows.append(
        _run(
            'datetime.datetime.strptime(s, "%Y")',
            lambda: datetime.datetime.strptime(SENTINEL, "%Y"),
        )
    )
    rows.append(
        _run("datetime.date.fromisoformat(s)", lambda: datetime.date.fromisoformat(SENTINEL))
    )
    rows.append(
        _run(
            "datetime.datetime.fromisoformat(s)",
            lambda: datetime.datetime.fromisoformat(SENTINEL),
        )
    )
    rows.append(_run('re.compile("[" + s)', lambda: __import__("re").compile("[" + SENTINEL)))
    rows.append(_run("{}[s]", lambda: {}[SENTINEL]))
    rows.append(_run("[].index(s)", lambda: [].index(SENTINEL)))
    rows.append(_run('"".index(s)', lambda: "".index(SENTINEL), added=True))
    rows.append(_run("[].remove(s)", lambda: [].remove(SENTINEL)))
    rows.append(_run("set().remove(s)", lambda: set().remove(SENTINEL), added=True))
    rows.append(_run("getattr(object(), s)", lambda: getattr(object(), SENTINEL)))
    rows.append(_run("json.loads(s)", lambda: json.loads(SENTINEL)))
    rows.append(_run("uuid.UUID(s)", lambda: uuid.UUID(SENTINEL)))
    rows.append(_run("ipaddress.ip_address(s)", lambda: ipaddress.ip_address(SENTINEL)))
    rows.append(_run("enum.Enum lookup E(s)", lambda: _ProbeEnum(SENTINEL)))

    raised, echoed, note = _probe_urlparse()
    rows.append({"label": "urllib.parse.urlparse(s)", "raised": raised, "echoed": echoed, "added": False, "note": note})

    rows.append(_run("int(s, 10)", lambda: int(SENTINEL, 10)))
    rows.append(_run("int(s, 16)", lambda: int(SENTINEL, 16)))
    rows.append(_run("bytes.fromhex(s)", lambda: bytes.fromhex(SENTINEL)))
    rows.append(_run("{}.pop(s)  [no default]", lambda: {}.pop(SENTINEL), added=True))
    raised, echoed, note = _probe_list_pop_index()
    rows.append({"label": "[].pop(idx)  [int index]", "raised": raised, "echoed": echoed, "added": True, "note": note})

    raised, echoed, note = _probe_str_encode()
    rows.append({"label": "str.encode round trip", "raised": raised, "echoed": echoed, "added": True, "note": note})
    raised, echoed, note = _probe_str_decode()
    rows.append({"label": "bytes.decode round trip", "raised": raised, "echoed": echoed, "added": True, "note": note})

    for row in rows:
        row.setdefault("note", "")
    return rows


#: Maps each PROBE ROW LABEL to the CALLEE FAMILY it belongs to, for folding
#: multiple probe rows (e.g. three "int" variants) into one Part-2 search
#: target. A family is included in Part 2 if ANY of its rows echoed.
FAMILY_OF_LABEL: dict[str, str] = {
    "int(s)": "int",
    "int(s, 10)": "int",
    "int(s, 16)": "int",
    "float(s)": "float",
    "complex(s)": "complex",
    "decimal.Decimal(s)": "decimal.Decimal",
    'datetime.datetime.strptime(s, "%Y")': "datetime.datetime.strptime",
    "datetime.date.fromisoformat(s)": "datetime.date.fromisoformat",
    "datetime.datetime.fromisoformat(s)": "datetime.datetime.fromisoformat",
    're.compile("[" + s)': "re.compile",
    "{}[s]": "SUBSCRIPT",  # handled by the separate subscript table, not a Call family
    "[].index(s)": ".index",
    '"".index(s)': ".index",
    "[].remove(s)": ".remove",
    "set().remove(s)": ".remove",
    "getattr(object(), s)": "getattr",
    "json.loads(s)": "json.loads",
    "uuid.UUID(s)": "uuid.UUID",
    "ipaddress.ip_address(s)": "ipaddress.ip_address",
    "enum.Enum lookup E(s)": "ENUM_LOOKUP",
    "urllib.parse.urlparse(s)": "urllib.parse.urlparse",
    "bytes.fromhex(s)": ".fromhex",
    "{}.pop(s)  [no default]": ".pop",
    "[].pop(idx)  [int index]": ".pop",
    "str.encode round trip": ".encode",
    "bytes.decode round trip": ".decode",
}

#: Module-qualified families resolved through each file's OWN import table.
#: value = dotted path from the file's root binding (see resolve_dotted()).
MODULE_QUALIFIED_FAMILIES: frozenset[str] = frozenset(
    {
        "decimal.Decimal",
        "datetime.datetime.strptime",
        "datetime.date.fromisoformat",
        "datetime.datetime.fromisoformat",
        "re.compile",
        "json.loads",
        "uuid.UUID",
        "ipaddress.ip_address",
        "urllib.parse.urlparse",  # defensive: kept out of `families` unless PROVEN echoing
    }
)

#: Bare builtins -- no import needed, matched by plain Name.
BUILTIN_BARE_FAMILIES: frozenset[str] = frozenset({"int", "float", "complex", "getattr"})

#: Attribute-name-only heuristic families (receiver type unknowable statically).
HEURISTIC_ATTR_FAMILIES: dict[str, str] = {
    "index": ".index",
    "remove": ".remove",
    "fromhex": ".fromhex",
    "pop": ".pop",
    "encode": ".encode",
    "decode": ".decode",
}


# ---------------------------------------------------------------------------
# PART 2 -- import resolution
# ---------------------------------------------------------------------------


def build_import_alias_map(tree: ast.Module) -> dict[str, str]:
    """local name -> canonical dotted path, from this module's OWN imports."""
    aliases: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                # `import X.Y as Z` -> Z: X.Y ; `import X.Y` (no asname) binds
                # the bare top-level name X, mapped to itself.
                if alias.asname:
                    aliases[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    aliases[top] = top
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue  # relative import -- never a stdlib target, skip safely
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                aliases[local] = f"{module}.{alias.name}" if module else alias.name
    return aliases


def resolve_dotted(call_func: ast.AST, alias_map: dict[str, str]) -> Optional[str]:
    """The full canonical dotted path of a Call's ``func``, or ``None``.

    Walks a chain of ``Attribute``/``Name`` nodes to build the chain as
    written, then substitutes the LEFTMOST identifier through this module's
    import alias map. Anything whose base is not a plain traceable Name (a
    call result, a subscript, an f-string) is unresolvable and returns
    ``None`` -- those fall through to the attribute-name heuristic instead.
    """
    chain: list[str] = []
    node: ast.AST = call_func
    while isinstance(node, ast.Attribute):
        chain.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    chain.append(node.id)
    chain.reverse()
    base, rest = chain[0], chain[1:]
    if base in alias_map:
        resolved_base = alias_map[base]
        return resolved_base if not rest else f"{resolved_base}.{'.'.join(rest)}"
    if base in {"bytes", "bytearray"} and rest:
        return f"{base}.{'.'.join(rest)}"
    return None


# ---------------------------------------------------------------------------
# PART 2 -- module-level constants and Enum subclass discovery
# ---------------------------------------------------------------------------


def module_level_constants(tree: ast.Module) -> set[str]:
    """Names assigned at MODULE scope only (never inside a def/class)."""
    out: set[str] = set()
    for node in tree.body:
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign) and node.target is not None:
            targets = [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                out.add(target.id)
    return out


_ENUM_BASE_NAMES = frozenset({"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"})
_ENUM_DOTTED = frozenset(f"enum.{n}" for n in _ENUM_BASE_NAMES)


def enum_subclass_names(tree: ast.Module, alias_map: dict[str, str]) -> set[str]:
    """Class names in THIS module whose bases resolve to an ``enum`` type."""
    out: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for base in node.bases:
            dotted = resolve_dotted(base, alias_map) if isinstance(base, (ast.Attribute, ast.Name)) else None
            if isinstance(base, ast.Name) and (base.id in _ENUM_BASE_NAMES or dotted in _ENUM_DOTTED):
                out.add(node.name)
            elif dotted in _ENUM_DOTTED:
                out.add(node.name)
    return out


# ---------------------------------------------------------------------------
# PART 2 -- scope-respecting helpers (never cross a nested def/lambda/class)
# ---------------------------------------------------------------------------


def _walk_own_scope(root: ast.AST):
    """Descendants of ``root``, stopping at a nested def/lambda/class.

    Used to compute ONE function's own parameters/locals/taint without
    pulling in a nested helper's internals, and without a nested helper
    inheriting the outer function's locals as its own.
    """
    stack: list[ast.AST] = list(reversed(list(ast.iter_child_nodes(root))))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue  # boundary -- do not descend into a nested scope
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _param_names(fn: ast.AST) -> set[str]:
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return set()
    a = fn.args
    names = {p.arg for p in a.posonlyargs} | {p.arg for p in a.args} | {p.arg for p in a.kwonlyargs}
    if a.vararg:
        names.add(a.vararg.arg)
    if a.kwarg:
        names.add(a.kwarg.arg)
    return names


def _has_page_param(fn: ast.AST) -> bool:
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    a = fn.args
    names = [p.arg for p in a.posonlyargs] + [p.arg for p in a.args] + [p.arg for p in a.kwonlyargs]
    return "page" in names


_PAGEISH_ROOTS = frozenset({"page", "locator", "el", "node", "handle"})


def _await_root_is_pageish(await_node: ast.Await) -> bool:
    """Root identifier of the awaited chain is page/locator/el/node/handle."""
    node: ast.AST = await_node.value
    while True:
        if isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            break
    return isinstance(node, ast.Name) and node.id in _PAGEISH_ROOTS


def _assign_targets_and_value(node: ast.AST) -> tuple[list[ast.AST], Optional[ast.AST]]:
    if isinstance(node, ast.Assign):
        return list(node.targets), node.value
    if isinstance(node, ast.AnnAssign) and node.value is not None:
        return ([node.target] if node.target is not None else []), node.value
    if isinstance(node, ast.AugAssign):
        return [node.target], node.value
    if isinstance(node, (ast.For, ast.AsyncFor)):
        return [node.target], node.iter
    if isinstance(node, ast.comprehension):
        return [node.target], node.iter
    return [], None


def _names_in_target(target: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(target) if isinstance(n, ast.Name)}


class _FnScope:
    """Everything the argument-source classifier needs about ONE function."""

    __slots__ = ("node", "name", "params", "tainted", "locally_bound")

    def __init__(self, node: Optional[ast.AST], name: str) -> None:
        self.node = node
        self.name = name
        self.params: set[str] = _param_names(node) if node is not None else set()
        self.locally_bound: set[str] = set()
        self.tainted: set[str] = set(self.params)
        if node is None:
            return
        # Pass 1: direct assignment targets, and seed taint from `x = await ...pageish...`.
        for sub in _walk_own_scope(node):
            targets, value = _assign_targets_and_value(sub)
            if not targets:
                continue
            for t in targets:
                self.locally_bound |= _names_in_target(t)
            if isinstance(value, ast.Await) and _await_root_is_pageish(value):
                for t in targets:
                    self.tainted |= _names_in_target(t)
        # Pass 2..N: propagate ONE hop at a time through `.get(...)`/subscript
        # off an already-tainted name, to a small fixed point.
        for _ in range(4):
            before = set(self.tainted)
            for sub in _walk_own_scope(node):
                targets, value = _assign_targets_and_value(sub)
                if not targets or value is None:
                    continue
                if _expr_is_tainted_one_hop(value, self.tainted):
                    for t in targets:
                        self.tainted |= _names_in_target(t)
            if self.tainted == before:
                break


def _expr_is_tainted_one_hop(expr: ast.AST, tainted: set[str]) -> bool:
    """``tainted_name.get(...)`` or ``tainted_name[...]`` or a bare tainted Name."""
    if isinstance(expr, ast.Name):
        return expr.id in tainted
    if isinstance(expr, ast.Subscript):
        return _expr_is_tainted_one_hop(expr.value, tainted)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "get":
        return _expr_is_tainted_one_hop(expr.func.value, tainted)
    return False


# ---------------------------------------------------------------------------
# PART 2 -- the four-bucket argument-source classifier
# ---------------------------------------------------------------------------

LITERAL = "LITERAL"
LOCAL_COMPUTED = "LOCAL_COMPUTED"
PAGE_OR_ARG = "PAGE_OR_ARG"
UNCLASSIFIED = "UNCLASSIFIED"


def classify(expr: ast.AST, scope: _FnScope, module_constants: set[str]) -> str:
    if isinstance(expr, ast.Constant):
        return LITERAL
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, (ast.USub, ast.UAdd)) and isinstance(
        expr.operand, ast.Constant
    ):
        return LITERAL
    if isinstance(expr, ast.Name):
        if expr.id in scope.tainted:
            return PAGE_OR_ARG
        if expr.id in module_constants and expr.id not in scope.locally_bound:
            return LITERAL
        if expr.id in scope.locally_bound:
            return LOCAL_COMPUTED
        return UNCLASSIFIED
    if isinstance(expr, ast.Subscript):
        inner = classify(expr.value, scope, module_constants)
        return inner if inner in (PAGE_OR_ARG, LOCAL_COMPUTED) else UNCLASSIFIED
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "get":
        inner = classify(expr.func.value, scope, module_constants)
        return inner if inner in (PAGE_OR_ARG, LOCAL_COMPUTED) else UNCLASSIFIED
    return UNCLASSIFIED


# ---------------------------------------------------------------------------
# PART 2 -- the walker
# ---------------------------------------------------------------------------


class Site:
    __slots__ = ("module", "function", "callee", "source", "has_page_param", "line", "is_store")

    def __init__(
        self,
        module: str,
        function: str,
        callee: str,
        source: str,
        has_page_param: bool,
        line: int,
        is_store: bool = False,
    ) -> None:
        self.module = module
        self.function = function
        self.callee = callee
        self.source = source
        self.has_page_param = has_page_param
        self.line = line
        self.is_store = is_store


def _hazard_argument(callee: str, call: ast.Call) -> Optional[ast.AST]:
    """The ONE argument whose value the proven exception actually quotes."""
    if callee == "getattr":
        if len(call.args) >= 2:
            return call.args[1]
        return None
    if callee == ".pop":
        # Only the no-default, 1-positional-arg shape can raise KeyError at all.
        if len(call.args) == 1 and not call.keywords:
            return call.args[0]
        return None
    if callee in (".encode", ".decode"):
        # The hazard is the STRING/BYTES being encoded/decoded -- the receiver,
        # not an argument. Handled by the caller via the Attribute's .value.
        return None
    if call.args:
        return call.args[0]
    return None


class _Walker(ast.NodeVisitor):
    def __init__(self, module_name: str, alias_map: dict[str, str], module_constants: set[str], enum_names: set[str], families: set[str]) -> None:
        self.module_name = module_name
        self.alias_map = alias_map
        self.module_constants = module_constants
        self.enum_names = enum_names
        self.families = families
        self.call_sites: list[Site] = []
        self.subscript_sites: list[Site] = []
        self._fn_stack: list[_FnScope] = []

    # -- scope plumbing, skipping annotations -------------------------------
    def _enter_fn(self, node: ast.AST) -> None:
        name = getattr(node, "name", "<lambda>")
        self._fn_stack.append(_FnScope(node, name))
        # Visit decorators, defaults, and body -- but NOT annotations/returns.
        for dec in getattr(node, "decorator_list", []):
            self.visit(dec)
        args = node.args
        for d in args.defaults:
            self.visit(d)
        for d in args.kw_defaults:
            if d is not None:
                self.visit(d)
        for stmt in node.body:
            self.visit(stmt)
        self._fn_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._enter_fn(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._enter_fn(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # Lambdas are not pushed as their own scope for this census -- a
        # coercion inside one is vanishingly rare here (12 lambdas total, none
        # observed to contain a hazard call) and is attributed to the
        # enclosing def, which is the more useful reading for this census.
        self.visit(node.body)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # SKIP node.annotation -- see module docstring on why.
        if node.value is not None:
            self.visit(node.value)
        self.visit(node.target)

    # -- the sites -----------------------------------------------------------
    def _current_scope(self) -> _FnScope:
        return self._fn_stack[-1] if self._fn_stack else _FnScope(None, "<module>")

    def _enclosing_name(self) -> str:
        return self._fn_stack[-1].name if self._fn_stack else "<module>"

    def _any_page_param(self) -> bool:
        return any(_has_page_param(f.node) for f in self._fn_stack if f.node is not None)

    def visit_Call(self, node: ast.Call) -> None:
        callee = self._resolve_callee(node)
        if callee is not None and callee in self.families:
            hazard_arg: Optional[ast.AST]
            if callee in (".encode", ".decode") and isinstance(node.func, ast.Attribute):
                hazard_arg = node.func.value  # the string/bytes being (en|de)coded
            else:
                hazard_arg = _hazard_argument(callee, node)
            if hazard_arg is not None:
                scope = self._current_scope()
                source = classify(hazard_arg, scope, self.module_constants)
                self.call_sites.append(
                    Site(
                        module=self.module_name,
                        function=self._enclosing_name(),
                        callee=callee,
                        source=source,
                        has_page_param=self._any_page_param(),
                        line=node.lineno,
                    )
                )
        self.generic_visit(node)

    def _resolve_callee(self, node: ast.Call) -> Optional[str]:
        func = node.func
        # Bare-name builtins.
        if isinstance(func, ast.Name):
            if func.id in BUILTIN_BARE_FAMILIES:
                return func.id
            if func.id in self.enum_names:
                return "ENUM_LOOKUP"
            # A bare name might ALSO be a `from X import Y` alias resolving to
            # a module-qualified family (e.g. `from uuid import UUID`).
            dotted = self.alias_map.get(func.id)
            if dotted in MODULE_QUALIFIED_FAMILIES:
                return dotted
            return None
        if isinstance(func, ast.Attribute):
            dotted = resolve_dotted(func, self.alias_map)
            if dotted in MODULE_QUALIFIED_FAMILIES:
                return dotted
            # Fall through to the attribute-name heuristic.
            if func.attr in HEURISTIC_ATTR_FAMILIES:
                return HEURISTIC_ATTR_FAMILIES[func.attr]
            return None
        return None

    def visit_Subscript(self, node: ast.Subscript) -> None:
        # Any Subscript reached here is in VALUE context: annotations are
        # already excluded upstream (visit_AnnAssign skips .annotation,
        # _enter_fn skips arg annotations and .returns), so this can never be
        # a type hint like `dict[str, Any]`.
        self.visit(node.value)
        if not isinstance(node.slice, ast.Slice) and not _is_literal_int_index(node.slice):
            scope = self._current_scope()
            source = classify(node.slice, scope, self.module_constants)
            # STORE context (`x[y] = v`) matters: dict.__setitem__ NEVER
            # raises KeyError for a missing key -- only a LIST receiver can
            # still raise (IndexError, out of range). Reported, not dropped,
            # because this census cannot tell a dict receiver from a list one
            # any more than it can for `.index`/`.remove` above; a real site
            # measured this way (`dom.py:6689/6691`, a dict target) is
            # discussed by hand in the accompanying report.
            self.subscript_sites.append(
                Site(
                    module=self.module_name,
                    function=self._enclosing_name(),
                    callee="[]",
                    source=source,
                    has_page_param=self._any_page_param(),
                    line=node.lineno,
                    is_store=isinstance(node.ctx, ast.Store),
                )
            )
        self.visit(node.slice)


def _is_literal_int_index(expr: ast.AST) -> bool:
    if isinstance(expr, ast.Constant) and isinstance(expr.value, int) and not isinstance(expr.value, bool):
        return True
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, (ast.USub, ast.UAdd)) and isinstance(expr.operand, ast.Constant):
        v = expr.operand.value
        return isinstance(v, int) and not isinstance(v, bool)
    return False


def census(families: set[str], package: Path = PACKAGE) -> tuple[list[Site], list[Site], dict[str, int]]:
    call_sites: list[Site] = []
    subscript_sites: list[Site] = []
    unresolved_hazard_arg = 0
    for path in sorted(package.glob("*.py")):
        rel = path.relative_to(REPO).as_posix()
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=rel)
        alias_map = build_import_alias_map(tree)
        mconsts = module_level_constants(tree)
        enums = enum_subclass_names(tree, alias_map)
        walker = _Walker(rel, alias_map, mconsts, enums, families)
        walker.visit(tree)
        call_sites.extend(walker.call_sites)
        subscript_sites.extend(walker.subscript_sites)
    return call_sites, subscript_sites, {"unresolved_hazard_arg": unresolved_hazard_arg}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    print("PART 1 -- proving the quoting property by running it")
    print()
    print(f"  sentinel = {SENTINEL!r}")
    print()
    header = f"  {'callee':32s} {'exception type':24s} {'echoed':6s}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    rows = probe_quoting()
    proven_yes = 0
    for row in rows:
        mark = "YES" if row["echoed"] else "NO"
        added = " [ADDED]" if row["added"] else ""
        print(f"  {row['label']:32s} {row['raised']:24s} {mark:6s}{added}")
        if row["echoed"]:
            proven_yes += 1
    print()
    for row in rows:
        if row["added"] and row["note"]:
            print(f"  note ({row['label']}): {row['note']}")
    print()

    # Fold probe rows into Part-2 search families.
    families: set[str] = set()
    family_any_yes: dict[str, bool] = {}
    for row in rows:
        family = FAMILY_OF_LABEL.get(row["label"])
        if family is None or family == "SUBSCRIPT":
            continue
        family_any_yes[family] = family_any_yes.get(family, False) or row["echoed"]
    for family, any_yes in family_any_yes.items():
        if any_yes:
            families.add(family)

    print("PROVEN-ECHOING FAMILIES carried into Part 2:")
    for family in sorted(families):
        print(f"  {family}")
    excluded = sorted(set(family_any_yes) - families)
    if excluded:
        print("EXCLUDED (tested, did not echo):")
        for family in excluded:
            print(f"  {family}")
    print()

    print("PART 2 -- where these are called in linkedin_server/")
    print()
    call_sites, subscript_sites, meta = census(families)

    def _print_table(sites: list[Site], title: str, show_ctx: bool = False) -> None:
        print(f"{title} -- {len(sites)} site(s)")
        print()
        if show_ctx:
            col = f"  {'module':26s} {'function':30s} {'callee':6s} {'source':15s} {'page-param':10s} {'ctx':6s} line"
        else:
            col = f"  {'module':26s} {'function':30s} {'callee':10s} {'source':15s} {'page-param':10s} line"
        print(col)
        print("  " + "-" * (len(col) - 2))
        for s in sorted(sites, key=lambda s: (s.module, s.line)):
            pg = "YES" if s.has_page_param else "NO"
            if show_ctx:
                ctx = "STORE" if s.is_store else "LOAD"
                print(f"  {s.module:26s} {s.function:30s} {s.callee:6s} {s.source:15s} {pg:10s} {ctx:6s} {s.line}")
            else:
                print(f"  {s.module:26s} {s.function:30s} {s.callee:10s} {s.source:15s} {pg:10s} {s.line}")
        print()

    _print_table(call_sites, "CALL SITES")
    _print_table(subscript_sites, "SUBSCRIPT SITES (separate; y not a literal int)", show_ctx=True)

    unclassified = [s for s in call_sites if s.source == UNCLASSIFIED]
    page_or_arg = [s for s in call_sites if s.source == PAGE_OR_ARG]
    with_page = [s for s in page_or_arg if s.has_page_param]
    without_page = [s for s in page_or_arg if not s.has_page_param]
    literal_n = sum(1 for s in call_sites if s.source == LITERAL)
    local_n = sum(1 for s in call_sites if s.source == LOCAL_COMPUTED)

    print("COUNTS")
    print()
    print(f"  callees proven echoing        {proven_yes} of {len(rows)} tested")
    print(f"  call sites found               {len(call_sites)}")
    print(f"  of those, PAGE_OR_ARG          {len(page_or_arg)}")
    print(f"  of those, in a fn WITH page    {len(with_page)}")
    print(f"  of those, in a fn WITHOUT page {len(without_page)}")
    print(f"  UNCLASSIFIED                   {len(unclassified)}")
    print(f"  subscript sites (separate)     {len(subscript_sites)}")
    print()
    print("  (bonus, not in the required block above)")
    print(f"  LITERAL                        {literal_n}")
    print(f"  LOCAL_COMPUTED                 {local_n}")
    print(f"  sum check (should == call sites found): {literal_n + local_n + len(page_or_arg) + len(unclassified)}")
    print()

    sub_page = [s for s in subscript_sites if s.source == PAGE_OR_ARG]
    sub_page_with = [s for s in sub_page if s.has_page_param]
    sub_page_without = [s for s in sub_page if not s.has_page_param]
    sub_literal = sum(1 for s in subscript_sites if s.source == LITERAL)
    sub_local = sum(1 for s in subscript_sites if s.source == LOCAL_COMPUTED)
    sub_unclass_n = sum(1 for s in subscript_sites if s.source == UNCLASSIFIED)
    sub_store_n = sum(1 for s in subscript_sites if s.is_store)
    sub_load_n = len(subscript_sites) - sub_store_n
    page_load = [s for s in sub_page if not s.is_store]
    page_store = [s for s in sub_page if s.is_store]
    print("  (bonus: the same breakdown for the 970-scale subscript table --")
    print("   the brief's required line is the single total above)")
    print(f"  subscript LITERAL              {sub_literal}")
    print(f"  subscript LOCAL_COMPUTED       {sub_local}")
    print(f"  subscript PAGE_OR_ARG          {len(sub_page)}")
    print(f"    of those, in a fn WITH page    {len(sub_page_with)}")
    print(f"    of those, in a fn WITHOUT page {len(sub_page_without)}")
    print(f"  subscript UNCLASSIFIED         {sub_unclass_n}")
    print(f"  sum check (should == subscript sites found): {sub_literal + sub_local + len(sub_page) + sub_unclass_n}")
    print()
    print("  LOAD vs STORE context -- a STORE subscript (`x[y] = v`) can only")
    print("  raise on a LIST receiver (IndexError); on a dict receiver")
    print("  `__setitem__` NEVER raises KeyError for a missing key. Receiver")
    print("  type is not resolved here (same limitation as .index/.remove),")
    print("  so this is reported rather than folded into one number.")
    print(f"  subscript sites, LOAD           {sub_load_n}")
    print(f"  subscript sites, STORE          {sub_store_n}")
    print(f"  PAGE_OR_ARG in LOAD context     {len(page_load)}  <- the actionable subset")
    print(f"  PAGE_OR_ARG in STORE context    {len(page_store)}  <- hazard only if receiver is a list")
    print()

    if sub_page:
        print(f"SUBSCRIPT PAGE_OR_ARG sites ({len(sub_page)}), listed in full:")
        for s in sorted(sub_page, key=lambda s: (s.module, s.line)):
            pg = "YES" if s.has_page_param else "NO"
            ctx = "STORE" if s.is_store else "LOAD"
            print(f"  {s.module}:{s.line} in {s.function}() -- page-param {pg}, {ctx}")
        print()

    if unclassified:
        print(f"UNCLASSIFIED call sites ({len(unclassified)}), listed in full:")
        for s in sorted(unclassified, key=lambda s: (s.module, s.line)):
            print(f"  {s.module}:{s.line} in {s.function}() -- callee {s.callee}")
        print()

    sub_unclassified = [s for s in subscript_sites if s.source == UNCLASSIFIED]
    if sub_unclassified:
        print(f"UNCLASSIFIED subscript sites ({len(sub_unclassified)}), listed in full:")
        for s in sorted(sub_unclassified, key=lambda s: (s.module, s.line)):
            print(f"  {s.module}:{s.line} in {s.function}()")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
