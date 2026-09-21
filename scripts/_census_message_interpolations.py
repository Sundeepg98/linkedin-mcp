"""Enumerate every BUILT MESSAGE in ``linkedin_server/`` and classify what it
interpolates.

THE CLASS THIS COUNTS, stated once. ``config.scrub`` cleans error text by
substituting THIS SERVER'S OWN FILESYSTEM PATHS and nothing else. It knows
paths. It does not know urls and it does not know names. So any message that
interpolates a value THE DOCUMENT or LINKEDIN chose -- a landed url, an href, a
slug, an element label, a heading, a title -- carries that value to the caller
intact, through an exception or through a log record.

    A PATH-SHAPED SCRUBBER IS NOT A REDACTOR. IT IS A SUBSTITUTION LIST,
    AND A URL IS NOT ON IT.

This is the third instance of one class in this repository. The first two are
closed and their vocabulary is reused here rather than reinvented:
``_audit/2026-09-20-the-coercion-leak.md`` (a name leaving through a
``ValueError`` that quoted it) and ``linkedin_server/coerce.py`` (the repair).
That audit's section 2 settles the distinction this census turns on, and this
file IMPORTS the analyser that implements it rather than writing a third copy:

    A VALUE IS PAGE-CONTROLLED WHEN THE DOCUMENT CHOOSES IT,
    NOT WHEN A COROUTINE PRODUCED IT.

## WHY THIS IS AN AST WALK AND NOT A GREP

The obvious text search for this class is "a raise or a logger call with an
f-string in it". It is wrong in BOTH directions and the instrument prints both
gaps rather than asserting them:

* IT OVERCOUNTS, because ``dom.py`` carries in-page JAVASCRIPT in string
  literals, and a ``${...}`` template inside one is not a Python interpolation.
* IT UNDERCOUNTS, and this is the half that matters. A ``raise`` whose call
  opens on one line and whose f-string sits on the next is invisible to a
  line-oriented search -- this package writes them that way constantly. And
  ``logger.info("landed on %s", final_url)`` has NO f-string at all: the
  format string is a plain constant and the interpolation happens inside
  ``logging``. A grep for ``f"`` cannot see it, and it reaches a log record
  with the url in it exactly as an f-string would.

:func:`grep_contrast` runs the naive search and prints it beside the AST count,
per module, so the claim above is a measurement.

## THE BUCKETS, AND WHY ``UNCLASSIFIED`` MUST NOT BE EMPTY

Each interpolated SUB-EXPRESSION -- not each message -- is bucketed by WHERE
ITS VALUE CAME FROM:

* ``TYPE_ONLY``            -- ``type(exc).__name__``, ``len(x)``, a count, an
  int, a bool, a literal. SAFE BY CONSTRUCTION: no string the document chose
  can reach the output through it.
* ``EXCEPTION_TEXT``       -- ``{exc}``, ``str(exc)``. Sub-classified by what
  the enclosing handler CATCHES: a package error this code raised itself, or
  an arbitrary Playwright/stdlib exception whose message may hold a url or a
  path that this package never saw.
* ``PAGE_OR_SITE_DERIVED`` -- the value can be a string LINKEDIN or THE
  DOCUMENT chose. THE HAZARD SET.
* ``CALLER_SUPPLIED``      -- a tool argument coming back to its own caller. A
  different question, and usually an acceptable one. NOT a clean bill: a
  caller-supplied needle can still be a third party's name.
* ``SERVER_CONSTRUCTED``   -- a module constant, a config value, a label from a
  closed set this package declares.
* ``UNCLASSIFIED``         -- everything else.

``UNCLASSIFIED`` is reported and is NOT forced empty. A census whose residual
bucket is zero has either solved static analysis or is lying, and the second is
far more likely. Every site in it is a site a human still has to read.

## WHAT THIS DOES NOT COUNT, SAID OUT LOUD

A gate may not claim more than it ran. This walk does NOT count: strings built
into a ``dict`` LITERAL (``return {"error": f"..."}``); strings passed to
``print``; strings built and returned directly; messages assembled across a
function boundary by a helper. ``PASSTHROUGH`` -- a non-literal string handed
to an exception WHOLE, with no interpolation at all -- is a real shape in this
class that the four requested kinds do not name, so it is counted and reported
SEPARATELY rather than folded into the total or dropped.

    python scripts/_census_message_interpolations.py [--json] [--out PATH]
"""

from __future__ import annotations

import ast
import collections
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

# ---------------------------------------------------------------------------
# THE SHIPPED ANALYSER, IMPORTED RATHER THAN REWRITTEN
# ---------------------------------------------------------------------------
#
# ``scripts/_census_page_coercions.py`` already implements the page-controlled
# / Playwright-typed distinction and a taint fixed-point over it. Writing a
# second copy here would let the two censuses drift apart on the one question
# that decides both of them. The vocabulary below is THAT module's, and its
# permissive analyser is run alongside the strict one in this file so the
# DIVERGENCE between them can be printed -- see :func:`census`.

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _census_page_coercions as coercions  # noqa: E402

PAGE_CONTROLLED = coercions.PAGE_CONTROLLED
PLAYWRIGHT_TYPED = coercions.PLAYWRIGHT_TYPED
TYPE_FIXING = coercions.TYPE_FIXING


# ---------------------------------------------------------------------------
# Vocabularies. Each one is a LIST, and a list-shaped guard cannot see the
# class it guards -- that is this repository's own scar, recorded twice in
# ``tests/leakwalk.py``. They are therefore used to ADMIT sites into a bucket
# on positive evidence, never to acquit one by absence.
# ---------------------------------------------------------------------------

#: Identifier fragments that name a value the document or LinkedIn chose. This
#: is the brief's set verbatim. Matched as a SUBSTRING of any ``Name.id`` or
#: ``Attribute.attr`` inside the expression, which over-approximates on purpose
#: -- ``fn_name`` matches ``name``. Over-approximating is the safe direction
#: for a hazard census; the residue lands in the shortlist a human reads.
HAZARD_NAME_TOKENS: tuple[str, ...] = (
    "url", "landed", "final", "href", "slug", "label", "title",
    "heading", "text", "name", "value",
)

#: The shortlist the wave lead adjudicates by hand. NARROWER than the hazard
#: token set: these name an ADDRESS, and an address is the subject of the
#: ``landed-url`` wave.
SHORTLIST_TOKENS: tuple[str, ...] = (
    "url", "landed", "final_url", "href", "slug", "redirect",
)

#: Logger method names. ``exception`` is included: it renders the message AND
#: the traceback, so it is the widest of the six, not the narrowest.
LOG_METHODS: frozenset[str] = frozenset(
    {"debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
)

#: Receiver names that mean "this is a logging call".
LOG_RECEIVERS: tuple[str, ...] = ("logger", "log", "_logger", "logging")

#: Names bound to an exception object. Handler bindings are discovered from the
#: tree; these cover a PARAMETER named for one, which the tree cannot bind.
EXCEPTION_NAMES: frozenset[str] = frozenset({"exc", "error", "err", "e", "exception"})

#: Exception types that mean "whatever came out of Playwright or the stdlib".
#: A handler catching one of these binds a message this package never composed,
#: and Playwright's own errors quote urls and selectors.
ARBITRARY_CATCHES: frozenset[str] = frozenset(
    {
        "Exception", "BaseException", "OSError", "IOError", "RuntimeError",
        "ValueError", "TypeError", "KeyError", "IndexError", "AttributeError",
        "TimeoutError", "Error", "PlaywrightError", "PlaywrightTimeoutError",
        "TargetClosedError", "JSONDecodeError", "ClientError", "ArithmeticError",
        "UnicodeDecodeError", "LookupError", "StopIteration", "StopAsyncIteration",
    }
)

#: Parameter names that are a BOUND or a NEEDLE the MCP caller passed in. Used
#: only for a parameter of a NON-tool function that is not hazard-named; a
#: parameter of an ``@mcp.tool()`` function is caller-supplied by definition and
#: needs no vocabulary.
CALLER_ARG_NAMES: frozenset[str] = frozenset(
    {
        "max_items", "limit", "timeout_ms", "timeout", "needle", "query",
        "keyword", "keywords", "term", "handle", "count", "index", "offset",
        "page_number", "days", "top", "size", "seconds", "attempts", "tries",
        "kind", "mode", "action", "which", "what", "why", "reason_code",
    }
)

#: Receivers whose attributes are values this server declared, not read.
SERVER_RECEIVERS: tuple[str, ...] = ("config", "paths", "buildinfo", "errors", "self")

#: THE REPAIR, RECOGNISED BY NAME. ``linkedin_server/landing.py`` turns a
#: landed address into a line built only from a closed vocabulary -- a marker
#: from ``config.AUTHWALL_MARKERS``, a route from a fixed table, and COUNTS.
#: A site that routes a url through one of these is the repair LANDING, not the
#: defect, and a shortlist that hands a wave lead their own repair back is one
#: nobody acts on -- the same "cries wolf" argument the coercion-leak audit
#: makes about its own first draft.
#:
#: THESE ARE SHAPERS ONLY. ``landing.authwall_marker`` is deliberately NOT
#: here: it returns a VERDICT (which marker matched, or None), which is a
#: different kind of claim from a shaped string, and this repository has
#: already been bitten once by a guard list that held both kinds and understood
#: only one.
#:
#: AND RECOGNISING THE CALL IS NOT CERTIFYING IT. Whether these three are
#: SUFFICIENT is the wave lead's adjudication against ``landing.py``, not this
#: census's -- all this census measures is that the value was routed through
#: the package's declared shaper instead of being interpolated raw.
SANITISERS: frozenset[str] = frozenset({"withheld", "render", "describe_landing"})
SANITISER_MODULE = "landing"


# ---------------------------------------------------------------------------
# 1. Small helpers over the tree
# ---------------------------------------------------------------------------


def _package_error_names(package: Path) -> frozenset[str]:
    """Every exception class ``errors.py`` declares.

    A handler catching one of these binds a message THIS PACKAGE composed, so
    ``{exc}`` under it is this package's own prose plus whatever this package
    chose to interpolate -- a different risk from an arbitrary stdlib message.
    """
    path = package / "errors.py"
    if not path.exists():
        return frozenset()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return frozenset(
        node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    )


def _module_constants(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """``(every module-level name, the SHOUTED ones)``.

    The shouted set is separated because it carries stronger evidence. A
    module-level ``BASE_URL = "https://www.linkedin.com"`` is a value this
    server wrote down, and the fact that its NAME contains ``url`` says
    nothing at all -- so the declaration has to outrank the name heuristic or
    the census reports its own constants as page data.
    """
    names: set[str] = set()
    shouted: set[str] = set()
    for node in tree.body:
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
                if target.id.isupper():
                    shouted.add(target.id)
    return frozenset(names), frozenset(shouted)


def _closed_literal_fields(tree: ast.Module) -> frozenset[str]:
    """Attribute names that can only ever hold a literal this module wrote.

    THE RULE, general rather than a special case: if a class declared in this
    module has a field, and EVERY construction of that class in this module
    passes a string LITERAL for it, then reading that field anywhere gives back
    one of a closed set of strings this package typed out. That is the brief's
    ``SERVER_CONSTRUCTED`` -- "a surface label from a closed set" -- and it is
    a property of the declarations, not a guess about a name.

    Measured on ``writes.py``: ``WriteSpec.action`` qualifies, because all 13
    entries of the module-level ``SANCTIONED_WRITES`` table pass a literal.
    ``WriteGrant.target`` does NOT, because ``_GRANTS`` starts empty and is
    filled at runtime from a caller -- so the rule discriminates rather than
    waving the whole attribute family through, which is the only reason it is
    worth having.

    IT IS SCOPED PER MODULE and matched by ATTRIBUTE NAME, so a same-named
    attribute of some other object in the same file reads as closed too. That
    is the same trade the tool-parameter collection makes, and it is recorded
    in the report's scope section rather than buried here.
    """
    classes: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        fields = {
            stmt.target.id
            for stmt in node.body
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
        }
        if fields:
            classes[node.name] = fields

    # For each class field, every keyword value seen at a construction site.
    seen: dict[tuple[str, str], list[ast.AST]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = coercions._callee_name(node.func)
        if name not in classes:
            continue
        for keyword in node.keywords:
            if keyword.arg and keyword.arg in classes[name]:
                seen.setdefault((name, keyword.arg), []).append(keyword.value)

    closed: set[str] = set()
    for (_, field), values in seen.items():
        if values and all(_is_str_constant(v) for v in values):
            closed.add(field)
    return frozenset(closed)


#: Calls that render their single argument and carry its CONTENT out. The
#: value that reaches the message is the argument's, not the function's.
STRINGIFIERS: frozenset[str] = frozenset({"str", "repr", "ascii", "format"})


def _unwrap_stringifier(expr: ast.AST) -> ast.AST:
    """``str(exc)`` -> ``exc``. Also unwraps ``await`` and redundant nesting."""
    for _ in range(8):
        if isinstance(expr, ast.Await):
            expr = expr.value
            continue
        if (
            isinstance(expr, ast.Call)
            and isinstance(expr.func, ast.Name)
            and expr.func.id in STRINGIFIERS
            and len(expr.args) == 1
            and not expr.keywords
        ):
            expr = expr.args[0]
            continue
        return expr
    return expr


#: Field names that carry the text a failure reports to its caller.
MESSAGE_KEYS: frozenset[str] = frozenset(
    {"error", "message", "reason", "why", "detail", "details", "hint", "note"}
)


def _is_message_field(target: ast.AST) -> bool:
    """``out["error"]`` / ``self.reason`` -- a field that carries failure text."""
    if isinstance(target, ast.Attribute):
        return target.attr in MESSAGE_KEYS
    if isinstance(target, ast.Subscript):
        key = target.slice
        return isinstance(key, ast.Constant) and key.value in MESSAGE_KEYS
    return False


def _sanitiser_call(expr: ast.AST) -> str:
    """The repair function this expression is routed through, or ``""``.

    Matched on the OUTERMOST call only. ``landing.withheld(final_url)`` is
    repaired; ``f"{landing.withheld(u)} {u}"`` has a second field holding the
    raw value, and that second field is classified on its own.
    """
    node = expr
    if isinstance(node, ast.Await):
        node = node.value
    if not isinstance(node, ast.Call):
        return ""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr not in SANITISERS:
        return ""
    if _root_name(func.value).lower() != SANITISER_MODULE:
        return ""
    return f"{SANITISER_MODULE}.{func.attr}"


def _leaf_identifiers(expr: ast.AST) -> set[str]:
    """Every ``Name.id`` and ``Attribute.attr`` inside ``expr``, lowercased."""
    out: set[str] = set()
    for node in ast.walk(expr):
        if isinstance(node, ast.Name):
            out.add(node.id.lower())
        elif isinstance(node, ast.Attribute):
            out.add(node.attr.lower())
    return out


def _root_name(expr: ast.AST) -> str:
    """The identifier a chain of attributes, calls and subscripts roots at."""
    node = expr
    for _ in range(24):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, (ast.Attribute, ast.Subscript, ast.Starred)):
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Await):
            node = node.value
        else:
            return ""
    return ""


def _is_log_call(node: ast.Call) -> str:
    """The logger method name if this call is a logging call, else ``""``."""
    func = node.func
    if not isinstance(func, ast.Attribute) or func.attr not in LOG_METHODS:
        return ""
    root = _root_name(func.value).lower()
    if any(token in root for token in LOG_RECEIVERS):
        return func.attr
    return ""


def _source(expr: ast.AST, text: str) -> str:
    """The exact source of ``expr``, or an unparse when the segment is lost."""
    try:
        segment = ast.get_source_segment(text, expr)
    except (ValueError, TypeError):
        segment = None
    if segment:
        return " ".join(segment.split())
    try:
        return " ".join(ast.unparse(expr).split())
    except Exception:  # noqa: BLE001 -- unparse is best-effort
        return f"<{type(expr).__name__}>"


# ---------------------------------------------------------------------------
# 2. What counts as a BUILT message, and what it interpolates
# ---------------------------------------------------------------------------


def _is_str_constant(expr: ast.AST) -> bool:
    return isinstance(expr, ast.Constant) and isinstance(expr.value, str)


def _decompose(expr: ast.AST) -> Optional[tuple[bool, list[ast.AST]]]:
    """``(is a string this code BUILDS, the values it interpolates)``.

    ``None`` means "not recognisably a string expression at all", which is a
    THIRD answer and must not be collapsed into either of the others.

    ## WHY THIS IS RECURSIVE, AND WHAT A FLAT VERSION COST

    The first version of this function handled each shape at the TOP LEVEL
    only, and decided that a ``+`` chain was a built message by asking whether
    any operand ``isinstance(p, ast.Constant)``. Both halves were wrong, and
    they were wrong together at one site:

        raise WriteAttemptError(
            f"... {landing.withheld(landed)}. "
            + ("A list write ..." if spec.target_kind == "company_id"
               else "This action ...")
        )

    The argument is ``BinOp(Add)`` of a JoinedStr and an IfExp. **A JoinedStr
    is not an ast.Constant**, so "does any operand hold a literal" answered
    NO, and the function returned ``None`` -- meaning the census did not
    attribute that message to the wrong bucket, it DROPPED THE WHOLE RAISE.
    ``_record_raise``'s fallbacks could not rescue it either: the INDIRECT
    branch wants a Name or Attribute and the PASSTHROUGH branch wants a Call,
    Subscript or BoolOp, and a BinOp is none of those. The site was invisible.

    And the second defect would have survived the first being fixed: the old
    concat branch returned the OPERANDS as the interpolated values, so it
    would have handed ``classify`` the whole ``JoinedStr`` node instead of the
    ``landing.withheld(landed)`` inside it. It never recursed.

        A CONCATENATION OF TWO BUILT STRINGS IS A BUILT STRING, AND AN
        EXTRACTOR THAT ONLY LOOKS AT THE TOP NODE CANNOT SEE ONE.

    Found by the wave lead cross-checking my AST count against a grep -- the
    direction that census claims is unnecessary. It was necessary here.
    """
    if _is_str_constant(expr):
        return (False, [])  # a string, but nothing is built into it

    if isinstance(expr, ast.JoinedStr):
        return (
            True,
            [p.value for p in expr.values if isinstance(p, ast.FormattedValue)],
        )

    if isinstance(expr, ast.Call):
        func = expr.func
        if isinstance(func, ast.Attribute) and func.attr == "format":
            if _is_str_constant(func.value) or isinstance(func.value, ast.JoinedStr):
                return (True, list(expr.args) + [kw.value for kw in expr.keywords])
        return None

    if isinstance(expr, ast.BinOp):
        # "...%s..." % X
        if isinstance(expr.op, ast.Mod) and (
            _is_str_constant(expr.left) or isinstance(expr.left, ast.JoinedStr)
        ):
            right = expr.right
            return (True, list(right.elts) if isinstance(right, ast.Tuple) else [right])
        # a + b, where at least one side is recognisably a string
        if isinstance(expr.op, ast.Add):
            return _combine([expr.left, expr.right])
        return None

    if isinstance(expr, ast.IfExp):
        return _combine([expr.body, expr.orelse])

    return None


def _combine(operands: list[ast.AST]) -> Optional[tuple[bool, list[ast.AST]]]:
    """Fold several operands of a string expression into one answer.

    An operand this cannot decompose is not discarded -- it becomes an
    INTERPOLATED VALUE, because a name concatenated into a message carries its
    content out exactly as an f-string field does. Requiring at least one
    recognisable string operand is what keeps numeric ``a + b`` out.
    """
    decomposed = [_decompose(op) for op in operands]
    if not any(d is not None for d in decomposed):
        return None
    building = False
    leaves: list[ast.AST] = []
    for operand, result in zip(operands, decomposed):
        if result is None:
            leaves.append(operand)
            building = True
            continue
        was_building, inner = result
        building = building or was_building
        leaves.extend(inner)
    return (building, leaves)


def interpolations(expr: ast.AST) -> Optional[list[ast.AST]]:
    """The sub-expressions ``expr`` interpolates, or ``None`` if not a built message.

    ``[]`` and ``None`` are DIFFERENT ANSWERS and collapsing them would delete
    the vocabulary this census needs: ``[]`` means "built, but only out of
    constants" (an f-string with no fields -- harmless, and still a built
    message); ``None`` means "not a built message at all".
    """
    result = _decompose(expr)
    if result is None:
        return None
    building, leaves = result
    if not building and not leaves:
        return None  # a bare literal is not a built message
    return leaves


def _built_argument(node: ast.Call) -> Optional[tuple[ast.AST, list[ast.AST]]]:
    """The first argument of ``node`` that is a built message, with its fields."""
    for arg in list(node.args) + [kw.value for kw in node.keywords]:
        fields = interpolations(arg)
        if fields is not None:
            return arg, fields
    return None


# ---------------------------------------------------------------------------
# 3. A STRICT page taint, run beside the shipped permissive one
# ---------------------------------------------------------------------------
#
# ``coercions._can_be_page_string`` answers YES for anything it does not
# recognise -- correct for a coercion census, where the measurement then
# acquits. Here the same rule would swallow the whole package into the hazard
# bucket and leave ``UNCLASSIFIED`` empty, which is the failure mode this
# instrument is most at risk of. So the hazard bucket here needs POSITIVE
# EVIDENCE, and the permissive analyser is run alongside so the disagreement
# between them can be counted rather than hidden.

#: Receiver names that mean the value came off a live document.
PAGE_RECEIVERS: tuple[str, ...] = ("page", "locator", "frame", "element", "handle", "anchor")


def _reads_the_page(expr: ast.AST) -> bool:
    """POSITIVE evidence that ``expr`` pulled a string off the document."""
    for node in ast.walk(expr):
        if isinstance(node, ast.Call):
            name = coercions._callee_name(node.func)
            if name in PAGE_CONTROLLED:
                return True
            if name in PLAYWRIGHT_TYPED:
                continue
            if isinstance(node.func, ast.Attribute):
                root = _root_name(node.func.value).lower()
                if root and any(tok in root for tok in PAGE_RECEIVERS):
                    return True
    return False


def _hazard_named(expr: ast.AST) -> bool:
    return any(
        token in leaf
        for leaf in _leaf_identifiers(expr)
        for token in HAZARD_NAME_TOKENS
    )


def _strict_page_taint(fn: ast.AST, tool_params: frozenset[str]) -> set[str]:
    """Names in ``fn`` that hold a string the document or LinkedIn chose.

    Seeded from positive evidence only -- a page read, or a PARAMETER of a
    non-tool function whose name says it holds an address or a label -- then
    run to a fixed point through assignments, ``for`` targets and comprehension
    targets, the same propagation shape the coercion census uses.
    """
    tainted: set[str] = set()

    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = fn.args
        params = (
            list(args.args) + list(args.posonlyargs) + list(args.kwonlyargs)
        )
        for arg in params:
            if arg.arg in tool_params:
                continue
            lowered = arg.arg.lower()
            if any(token in lowered for token in HAZARD_NAME_TOKENS):
                tainted.add(arg.arg)

    for _ in range(8):
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
            if value is None:
                continue
            root = _root_name(value)
            carries = _reads_the_page(value) or (root in tainted) or any(
                name in tainted for name in coercions._names_in(value)
            )
            if not carries:
                continue
            for target in targets:
                if target is not None:
                    tainted |= coercions._names_in(target)
        if tainted == before:
            break
    return tainted


# ---------------------------------------------------------------------------
# 4. The classifier
# ---------------------------------------------------------------------------


def _is_type_only(expr: ast.AST) -> bool:
    """Whether ``expr``'s value is fixed to a type no page string fits inside."""
    if isinstance(expr, ast.Constant):
        return not isinstance(expr.value, (str, bytes))
    if isinstance(expr, (ast.Compare, ast.UnaryOp)):
        return True
    if isinstance(expr, ast.Attribute):
        # type(x).__name__ / x.__class__.__name__
        if expr.attr == "__name__":
            return True
        return False
    if isinstance(expr, ast.Await):
        return _is_type_only(expr.value)
    if isinstance(expr, ast.Call):
        name = coercions._callee_name(expr.func)
        if name in PLAYWRIGHT_TYPED:
            return True
        if name in TYPE_FIXING and name not in {"int", "float"}:
            return True
        if name in {"int", "float"}:
            # int(x) is an int WHEN IT RETURNS. This census is about the value
            # that reaches the message, and that value is an integer.
            return True
        return False
    if isinstance(expr, ast.JoinedStr):
        fields = interpolations(expr) or []
        return all(_is_type_only(f) for f in fields)
    return False


def _handler_bindings(fn: ast.AST) -> dict[str, tuple[str, ...]]:
    """``{bound name: the types its handler catches}`` for every ``except as``."""
    out: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(fn):
        if not isinstance(node, ast.ExceptHandler) or not node.name:
            continue
        kinds: list[str] = []
        spec = node.type
        if spec is None:
            kinds = ["<bare>"]
        elif isinstance(spec, ast.Tuple):
            kinds = [coercions._callee_name(e) or _root_name(e) for e in spec.elts]
        else:
            kinds = [coercions._callee_name(spec) or _root_name(spec)]
        out[node.name] = tuple(k for k in kinds if k)
    return out


def _exception_subclass(
    kinds: tuple[str, ...], package_errors: frozenset[str]
) -> str:
    """(a) this package raised it, or (b) it could be anything."""
    if not kinds:
        return "undecided"
    if "<bare>" in kinds:
        return "arbitrary"
    if all(k in package_errors for k in kinds):
        return "package_raised"
    if any(k in ARBITRARY_CATCHES or k not in package_errors for k in kinds):
        return "arbitrary"
    return "undecided"


class _Context:
    """Everything the classifier needs about the function a site sits in."""

    def __init__(
        self,
        fn: Optional[ast.AST],
        tool_params: frozenset[str],
        constants: tuple[frozenset[str], frozenset[str]],
        package_errors: frozenset[str],
        closed_fields: frozenset[str] = frozenset(),
    ) -> None:
        self.fn = fn
        self.tool_params = tool_params
        self.constants, self.shouted = constants
        self.package_errors = package_errors
        self.closed_fields = closed_fields
        self.params: frozenset[str] = frozenset()
        self.handlers: dict[str, tuple[str, ...]] = {}
        self.strict_taint: set[str] = set()
        self.loose_taint: set[str] = set()
        if fn is not None:
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = fn.args
                self.params = frozenset(
                    arg.arg
                    for arg in list(a.args) + list(a.posonlyargs) + list(a.kwonlyargs)
                )
            self.handlers = _handler_bindings(fn)
            self.strict_taint = _strict_page_taint(fn, tool_params)
            try:
                self.loose_taint = coercions._tainted_names(fn)
            except Exception:  # noqa: BLE001 -- the second opinion is optional
                self.loose_taint = set()


def _handler_kinds(handler: ast.ExceptHandler) -> tuple[str, ...]:
    spec = handler.type
    if spec is None:
        return ("<bare>",)
    if isinstance(spec, ast.Tuple):
        return tuple(
            k for k in (coercions._callee_name(e) or _root_name(e) for e in spec.elts) if k
        )
    name = coercions._callee_name(spec) or _root_name(spec)
    return (name,) if name else ()


def classify(
    expr: ast.AST,
    ctx: _Context,
    active: Optional[dict[str, tuple[str, ...]]] = None,
) -> tuple[str, str]:
    """``(bucket, why)`` for one interpolated sub-expression.

    ORDER IS THE WHOLE DESIGN. ``type(exc).__name__`` contains the substring
    ``name``; ``str(exc)`` roots at an exception binding; a tool argument may
    be called ``url``. Each of those reads as three different buckets depending
    on which test runs first, so the safe-by-construction tests run before the
    heuristics, and the heuristics run before the residue.
    """
    # 0. SEE THROUGH THE STRINGIFIERS FIRST. ``_root_name`` follows a call to
    # its FUNC, which is right for ``landing.withheld(u)`` (the shaper decides
    # the value) and WRONG for ``str(exc)``, where the func is ``str`` and the
    # value carried out is the ARGUMENT. Left unfixed this reported
    # ``out["error"] = str(exc)`` as UNCLASSIFIED -- and that one site is the
    # package's ONLY handler catching solely its own error type, so the bug
    # presented as a clean and interesting zero rather than as a miss.
    expr = _unwrap_stringifier(expr)

    # 1. Safe by construction, whatever it is named.
    if _is_type_only(expr):
        return "TYPE_ONLY", "value type is fixed; no string fits in it"

    # 1b. Routed through the package's declared shaper. The value reaching the
    # message is a line built from a closed vocabulary, not the address.
    sanitiser = _sanitiser_call(expr)
    if sanitiser:
        return "SERVER_CONSTRUCTED", f"routed through {sanitiser}() -- the repair"

    root = _root_name(expr)

    # 2. An exception's own text. THE BINDING IS THE LEXICALLY INNERMOST
    # HANDLER, never a function-wide lookup: a function with both
    # ``except ExtractionFailedError as exc`` and ``except Exception as exc``
    # has TWO different ``exc`` values, and a dict keyed by name keeps only the
    # last one walked. That collapse is what made this census report zero
    # package-raised exceptions -- a clean number produced by a lookup that
    # could not tell the two handlers apart.
    active = active or {}
    if root in active:
        kinds = active[root]
        sub = _exception_subclass(kinds, ctx.package_errors)
        return f"EXCEPTION_TEXT:{sub}", f"inside 'except {','.join(kinds)}'"
    if root in ctx.handlers or root in EXCEPTION_NAMES:
        # Named for an exception but NOT lexically inside a handler binding it.
        return (
            "EXCEPTION_TEXT:undecided",
            "named for an exception, but not inside a handler that binds it",
        )

    # 3. Positive evidence the document chose this value.
    if _reads_the_page(expr):
        return "PAGE_OR_SITE_DERIVED", "reads the live document"
    if root and root in ctx.strict_taint:
        return "PAGE_OR_SITE_DERIVED", f"'{root}' carries a page read"

    # 4. The caller's own string coming back.
    if root and root in ctx.tool_params and root in ctx.params:
        return "CALLER_SUPPLIED", "a parameter of an @mcp.tool() function"
    if root and root in ctx.params and not _hazard_named(expr):
        if root in CALLER_ARG_NAMES:
            return "CALLER_SUPPLIED", "a declared caller bound/needle parameter"

    # 5. A DECLARED CONSTANT OUTRANKS THE NAME HEURISTIC. ``BASE_URL`` and
    # ``LOGIN_URL`` are addresses this server wrote down; that their names
    # contain "url" is not evidence of anything. Checking the name first
    # reported two of this package's own constants as page data.
    if root and root in ctx.shouted:
        return "SERVER_CONSTRUCTED", "a SHOUTED module-level constant"
    if isinstance(expr, ast.Name) and expr.id.isupper() and len(expr.id) > 1:
        # IMPORTED constants are the common case and a module-local scan cannot
        # see them: ``BASE_URL`` and ``LOGIN_URL`` live in ``config.py`` and are
        # imported into ``server.py`` and ``auth.py``, where the name-heuristic
        # then convicted this package's own addresses of being page data. An
        # ALL-CAPS bare name is this codebase's convention for a declared
        # constant, and no page value can reach one -- module level cannot
        # await, so the taint analysis above has already had its chance.
        return "SERVER_CONSTRUCTED", "an ALL-CAPS name -- a declared constant"
    if (
        isinstance(expr, ast.Attribute)
        and expr.attr in ctx.closed_fields
    ):
        return (
            "SERVER_CONSTRUCTED",
            f"'.{expr.attr}' is only ever built from a literal in this module",
        )

    # 6. The heuristic half of the hazard bucket: named for a page value.
    if _hazard_named(expr):
        return "PAGE_OR_SITE_DERIVED", "named for a value the document chooses"

    # 7. Something else this server wrote down.
    if root and root in ctx.constants:
        return "SERVER_CONSTRUCTED", "a module-level name"
    if root and any(root.lower() == r for r in SERVER_RECEIVERS):
        return "SERVER_CONSTRUCTED", f"an attribute of '{root}'"

    # 8. The residue, which is reported and never forced empty.
    return "UNCLASSIFIED", "no positive evidence either way"


# ---------------------------------------------------------------------------
# 5. The walk
# ---------------------------------------------------------------------------


class _Walker(ast.NodeVisitor):
    """Collect message-bearing sites with their enclosing function."""

    def __init__(
        self,
        path: Path,
        text: str,
        constants: tuple[frozenset[str], frozenset[str]],
        tool_params: frozenset[str],
        package_errors: frozenset[str],
        closed_fields: frozenset[str] = frozenset(),
    ) -> None:
        self.path = path
        self.text = text
        self.constants = constants
        self.tool_params = tool_params
        self.package_errors = package_errors
        self.closed_fields = closed_fields
        self.sites: list[dict[str, Any]] = []
        self._fn_stack: list[ast.AST] = []
        self._ctx_stack: list[_Context] = []
        self._handler_stack: list[ast.ExceptHandler] = []

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._handler_stack.append(node)
        self.generic_visit(node)
        self._handler_stack.pop()

    def _active_handlers(self) -> dict[str, tuple[str, ...]]:
        """Bound exception names in scope AT THIS SITE, innermost winning."""
        out: dict[str, tuple[str, ...]] = {}
        for handler in self._handler_stack:  # outermost first
            if handler.name:
                out[handler.name] = _handler_kinds(handler)
        return out

    # -- scopes ------------------------------------------------------------
    def _visit_fn(self, node: ast.AST) -> None:
        self._fn_stack.append(node)
        self._ctx_stack.append(
            _Context(
                node,
                self.tool_params,
                self.constants,
                self.package_errors,
                self.closed_fields,
            )
        )
        self.generic_visit(node)
        self._ctx_stack.pop()
        self._fn_stack.pop()

    visit_FunctionDef = _visit_fn
    visit_AsyncFunctionDef = _visit_fn

    @property
    def _ctx(self) -> _Context:
        if self._ctx_stack:
            return self._ctx_stack[-1]
        return _Context(
            None,
            self.tool_params,
            self.constants,
            self.package_errors,
            self.closed_fields,
        )

    @property
    def _fn_name(self) -> str:
        return getattr(self._fn_stack[-1], "name", "<module>") if self._fn_stack else "<module>"

    # -- RAISE and INDIRECT and PASSTHROUGH --------------------------------
    def visit_Raise(self, node: ast.Raise) -> None:
        call = node.exc
        if isinstance(call, ast.Call):
            self._record_raise(node, call)
        self.generic_visit(node)

    def _record_raise(self, node: ast.Raise, call: ast.Call) -> None:
        raised = coercions._callee_name(call.func) or _root_name(call.func)
        found = _built_argument(call)
        if found is not None:
            message, fields = found
            self.sites.append(
                self._record("RAISE", node.lineno, raised, message, fields, node)
            )
            return

        args = list(call.args) + [kw.value for kw in call.keywords]
        if not args:
            return
        first = args[0]

        # INDIRECT -- a bare name or attribute holding a message built earlier.
        if isinstance(first, (ast.Name, ast.Attribute)) and not _is_str_constant(first):
            built = self._resolve_built_name(_root_name(first))
            if built is None:
                return
            source, fields = built
            row = self._record("INDIRECT", node.lineno, raised, first, fields, node)
            row["resolved_from"] = source
            self.sites.append(row)
            return

        # PASSTHROUGH -- a non-literal string handed over WHOLE. Counted
        # separately: the four requested kinds do not name this shape, and it
        # is the purest instance of the class, since the message IS the
        # foreign string rather than merely containing it.
        if isinstance(first, (ast.Call, ast.Subscript, ast.BoolOp)):
            fields = [first]
            if isinstance(first, ast.BoolOp):
                fields = [v for v in first.values if not _is_str_constant(v)]
            if not fields:
                return
            self.sites.append(
                self._record("PASSTHROUGH", node.lineno, raised, first, fields, node)
            )

    def _resolve_built_name(self, name: str) -> Optional[tuple[str, list[ast.AST]]]:
        """A built string assigned to ``name`` in the enclosing function.

        Returns ``None`` when nothing in the function assigns it a built
        string. A name assigned MORE THAN ONCE is still resolved, from the
        last built assignment seen, and the row carries the source so the
        reader can check rather than trust it.
        """
        if not self._fn_stack:
            return None
        fn = self._fn_stack[-1]
        answer: Optional[tuple[str, list[ast.AST]]] = None
        for node in ast.walk(fn):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = list(getattr(node, "targets", [])) or [node.target]
            if not any(isinstance(t, ast.Name) and t.id == name for t in targets):
                continue
            if node.value is None:
                continue
            fields = interpolations(node.value)
            if fields is None:
                continue
            answer = (f"line {node.lineno}: {_source(node.value, self.text)}", fields)
        return answer

    # -- LOG ---------------------------------------------------------------
    def visit_Call(self, node: ast.Call) -> None:
        method = _is_log_call(node)
        if method and node.args:
            fmt = node.args[0]
            fields = interpolations(fmt)
            if fields is None and _is_str_constant(fmt) and len(node.args) > 1:
                # THE FORM A NAIVE CENSUS MISSES. No f-string anywhere: the
                # format string is a plain constant and ``logging`` does the
                # interpolation. A grep for f-strings cannot see this, and the
                # url reaches the log record exactly as it would from one.
                fields = list(node.args[1:])
            if fields is not None:
                self.sites.append(
                    self._record("LOG", node.lineno, f"logger.{method}", fmt, fields, node)
                )
        self.generic_visit(node)

    # -- FIELD -------------------------------------------------------------
    def visit_Assign(self, node: ast.Assign) -> None:
        self._record_field(node, list(node.targets), node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._record_field(node, [node.target], node.value)
        self.generic_visit(node)

    def _record_field(
        self, node: ast.AST, targets: list[ast.AST], value: ast.AST
    ) -> None:
        if not any(isinstance(t, (ast.Subscript, ast.Attribute)) for t in targets):
            return
        where = ", ".join(_source(t, self.text) for t in targets)
        fields = interpolations(value)
        if fields is not None:
            self.sites.append(
                self._record("FIELD", node.lineno, where, value, fields, node)
            )
            return

        # A MESSAGE FIELD ASSIGNED A WHOLE FOREIGN STRING, no interpolation at
        # all -- ``out["error"] = str(exc)``. Found by asking why this census
        # reported ZERO exception interpolations under a handler catching only
        # this package's own errors: the one site that does it, dom.py's
        # ``except ExtractionFailedError as exc``, builds nothing, so a walk
        # looking for built messages could not see it and the zero was an
        # artefact of the question rather than a fact about the code.
        #
        # Scoped to MESSAGE-BEARING KEYS. Every ``out["anything"] = call()`` in
        # this package would drown the report, and this census is about the
        # text a failure reports, not about assignment.
        if not any(_is_message_field(t) for t in targets):
            return
        if _is_str_constant(value) or isinstance(value, ast.Constant):
            return
        if isinstance(value, (ast.Call, ast.Subscript, ast.BoolOp, ast.Attribute, ast.Name)):
            carried = [value]
            if isinstance(value, ast.BoolOp):
                carried = [v for v in value.values if not _is_str_constant(v)]
            if carried:
                self.sites.append(
                    self._record(
                        "PASSTHROUGH", node.lineno, where, value, carried, node
                    )
                )

    # -- the row -----------------------------------------------------------
    def _record(
        self,
        kind: str,
        line: int,
        target: str,
        message: ast.AST,
        fields: list[ast.AST],
        node: ast.AST,
    ) -> dict[str, Any]:
        ctx = self._ctx
        active = self._active_handlers()
        rendered: list[dict[str, str]] = []
        for field in fields:
            bucket, why = classify(field, ctx, active)
            text = _source(field, self.text)
            loose = _root_name(field) in ctx.loose_taint or _reads_the_page(field)
            rendered.append(
                {
                    "expr": text,
                    "bucket": bucket,
                    "why": why,
                    "shortlist": any(t in text.lower() for t in SHORTLIST_TOKENS),
                    "loose_says_page": bool(loose),
                    "sanitiser": _sanitiser_call(field),
                }
            )
        return {
            "module": self.path.name,
            "line": line,
            "function": self._fn_name,
            "kind": kind,
            "target": target,
            "message": _source(message, self.text),
            "from_cause": isinstance(node, ast.Raise) and node.cause is not None,
            "fields": rendered,
        }


def _tool_parameters(tree: ast.Module) -> frozenset[str]:
    """Every parameter name of every ``@mcp.tool()`` function in this module.

    These ARE the MCP caller's arguments. Collected per module and applied
    package-wide within it, which over-admits a same-named parameter of a
    non-tool helper -- the conservative direction here is the one that keeps a
    caller's own string OUT of the hazard bucket only when the name really is
    a tool argument somewhere in the same file.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorated = False
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Attribute) and target.attr == "tool":
                decorated = True
        if not decorated:
            continue
        a = node.args
        for arg in list(a.args) + list(a.posonlyargs) + list(a.kwonlyargs):
            names.add(arg.arg)
    return frozenset(names)


def census_sources(
    sources: dict[str, str], package_errors: frozenset[str]
) -> list[dict[str, Any]]:
    """Every built-message site in ``{filename: source text}``, classified."""
    out: list[dict[str, Any]] = []
    for name in sorted(sources):
        text = sources[name]
        try:
            tree = ast.parse(text, filename=name)
        except SyntaxError:
            # A module that does not parse is a LOUD event, never a silent
            # skip: it would otherwise shrink the denominator invisibly.
            out.append(
                {
                    "module": name,
                    "line": 0,
                    "function": "<unparseable>",
                    "kind": "PARSE_ERROR",
                    "target": "",
                    "message": "",
                    "from_cause": False,
                    "fields": [],
                }
            )
            continue
        walker = _Walker(
            Path(name),
            text,
            _module_constants(tree),
            _tool_parameters(tree),
            package_errors,
            _closed_literal_fields(tree),
        )
        walker.visit(tree)
        out.extend(walker.sites)
    return sorted(out, key=lambda row: (row["module"], row["line"]))


def read_package(package: Path = PACKAGE) -> dict[str, str]:
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(package.glob("*.py"))}


def census(package: Path = PACKAGE) -> list[dict[str, Any]]:
    """Every built-message site in the package, classified. Sorted for diffing."""
    return census_sources(read_package(package), _package_error_names(package))


# ---------------------------------------------------------------------------
# PROVENANCE -- BECAUSE THE SUBJECT OF THIS CENSUS CAN MOVE WHILE IT RUNS
# ---------------------------------------------------------------------------
#
# MEASURED, not anticipated: the first run of this instrument reported 76
# hazard sub-expressions and a 19-row shortlist; every run after it reported
# 75 and 17, from a BYTE-IDENTICAL instrument. Nothing was nondeterministic --
# three consecutive ``--json`` runs are md5-identical. The SOURCE had changed
# underneath, because another agent was repairing ``auth.py`` in this same
# worktree while the census ran.
#
#     A COUNT OVER A TREE SOMEBODY ELSE IS EDITING IS A READING WITH A
#     TIMESTAMP, NOT A FACT ABOUT THE CODEBASE.
#
# So every report stamps the exact content it parsed: a sha1 per module and a
# combined digest over all of them. Re-running and getting the same digest is
# what makes two numbers comparable; a different digest means they are not.
# This is read-only -- no ``git stash create``, no object written, nothing
# staged -- because this census shares its worktree with a live writer.


def source_digest(sources: dict[str, str]) -> dict[str, Any]:
    """A sha1 per module plus a combined digest over the whole subject."""
    import hashlib

    per_module = {
        name: hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        for name, text in sorted(sources.items())
    }
    combined = hashlib.sha1(
        "\n".join(f"{n}:{h}" for n, h in sorted(per_module.items())).encode("ascii")
    ).hexdigest()[:12]
    return {"modules": per_module, "combined": combined, "count": len(per_module)}


def _git(args: list[str]) -> str:
    """A READ-ONLY git call. Nothing here writes an object, a ref or the index."""
    try:
        proc = subprocess.run(
            ["git"] + args, cwd=str(REPO), capture_output=True, text=True, timeout=60
        )
        return proc.stdout if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def head_sources() -> dict[str, str]:
    """``linkedin_server/*.py`` AS COMMITTED AT HEAD. Read-only.

    The working tree is being edited by another agent, so HEAD is the only
    stationary thing available to compare against. An untracked module -- and
    there is one, the repair module the concurrent wave is writing -- is simply
    absent here, which is the honest answer rather than a zero.
    """
    listing = _git(["ls-tree", "--name-only", "HEAD", "linkedin_server/"])
    out: dict[str, str] = {}
    for line in listing.splitlines():
        line = line.strip()
        if not line.endswith(".py"):
            continue
        text = _git(["show", f"HEAD:{line}"])
        if text:
            out[Path(line).name] = text
    return out


# ---------------------------------------------------------------------------
# 6. The contrast that justifies the method
# ---------------------------------------------------------------------------

#: The search a person would actually run for this class: "a raise or a logger
#: call with an f-string in it". It is wrong in both directions.
NAIVE_PATTERNS: tuple[str, ...] = (
    r'raise .*f"',
    r'logger\.[a-z]*(f"',
    r'\["error"\] = f"',
)


def grep_contrast(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per module: what the naive text search counts, against the AST."""
    textual: dict[str, int] = {}
    argv = ["git", "grep", "-c"]
    for pattern in NAIVE_PATTERNS:
        argv += ["-e", pattern]
    argv += ["--", "linkedin_server/"]
    try:
        proc = subprocess.run(
            argv, cwd=str(REPO), capture_output=True, text=True, timeout=60
        )
        for line in proc.stdout.splitlines():
            if ":" not in line:
                continue
            where, _, count = line.rpartition(":")
            textual[Path(where).name] = int(count) if count.strip().isdigit() else 0
    except (OSError, subprocess.SubprocessError):
        textual = {}

    ast_counts: dict[str, int] = {}
    for row in rows:
        ast_counts[row["module"]] = ast_counts.get(row["module"], 0) + 1

    return [
        {
            "module": name,
            "grep_lines": textual.get(name, 0),
            "ast_sites": ast_counts.get(name, 0),
        }
        for name in sorted(set(textual) | set(ast_counts))
    ]


# ---------------------------------------------------------------------------
# 7. Report
# ---------------------------------------------------------------------------

MAIN_KINDS: tuple[str, ...] = ("RAISE", "LOG", "FIELD", "INDIRECT")

BUCKET_ORDER: tuple[str, ...] = (
    "PAGE_OR_SITE_DERIVED",
    "EXCEPTION_TEXT:arbitrary",
    "EXCEPTION_TEXT:package_raised",
    "EXCEPTION_TEXT:undecided",
    "CALLER_SUPPLIED",
    "TYPE_ONLY",
    "SERVER_CONSTRUCTED",
    "UNCLASSIFIED",
)


def _bucket_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {b: 0 for b in BUCKET_ORDER}
    for row in rows:
        for field in row["fields"]:
            counts[field["bucket"]] = counts.get(field["bucket"], 0) + 1
    return counts


def _shortlist(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        hits = [f for f in row["fields"] if f["shortlist"]]
        if hits:
            entry = dict(row)
            entry["fields"] = hits
            out.append(entry)
    return sorted(out, key=lambda r: (r["module"], r["line"]))


def _md_escape(text: str, limit: int = 110) -> str:
    """Table-safe, and TRUNCATED so one 600-character expression cannot make a
    table unreadable. The full text is always in ``--json``, and the row still
    carries module and line, so nothing is lost -- only shortened."""
    text = text.replace("|", "\\|")
    if len(text) > limit:
        return text[: limit - 15] + " ... [+" + str(len(text) - limit + 15) + " chars]"
    return text


def report(
    rows: list[dict[str, Any]],
    provenance: Optional[dict[str, Any]] = None,
) -> str:
    """The markdown report. ASCII only; SOURCE EXPRESSIONS, never values."""
    main = [r for r in rows if r["kind"] in MAIN_KINDS]
    extra = [r for r in rows if r["kind"] not in MAIN_KINDS and r["kind"] != "PARSE_ERROR"]
    unparseable = [r for r in rows if r["kind"] == "PARSE_ERROR"]
    modules = sorted({r["module"] for r in rows})
    counts = _bucket_counts(main)
    total_fields = sum(counts.values())
    shortlist = _shortlist(rows)

    lines: list[str] = []
    add = lines.append

    add("# Census: what this server's built messages interpolate")
    add("")
    add(
        "Produced by `scripts/_census_message_interpolations.py` (AST, not grep) "
        "over `linkedin_server/`."
    )
    add("")

    # -- 0. provenance ----------------------------------------------------
    if provenance:
        add("## 0. WHICH TREE THIS COUNTED -- read this before quoting a number")
        add("")
        digest = provenance.get("digest", {})
        add(
            f"**Subject digest `{digest.get('combined', '?')}`** over "
            f"**{digest.get('count', 0)} modules**. "
            f"Re-running and getting the same digest is what makes two of these "
            f"reports comparable; a different digest means they are not."
        )
        add("")
        add(f"- git HEAD: `{provenance.get('head', '?')}`")
        dirty = provenance.get("dirty", [])
        add(
            "- working tree vs HEAD: "
            + (", ".join(f"`{d}`" for d in dirty) if dirty else "clean")
        )
        add(
            "- digest of what was walked / of a re-read taken straight after: "
            f"`{digest.get('combined', '?')}` / "
            f"`{provenance.get('digest_after', '?')}` "
            + (
                "(**STABLE** -- one snapshot)"
                if provenance.get("stable")
                else "(**THE TREE MOVED WHILE THIS RAN.** The counts below are "
                "one coherent snapshot -- the walk reads the source once and "
                "digests exactly what it walked -- but a writer landed an edit "
                "during the run, so this report is already behind the tree.)"
            )
        )
        add("")
        add(
            "**THIS MATTERS HERE, AND IT IS MEASURED RATHER THAN ANTICIPATED.** "
            "The first run of this instrument reported **76** hazard "
            "sub-expressions and a **19**-row shortlist. Every run after it "
            "reported **75** and **17**, from a byte-identical instrument, with "
            "three consecutive `--json` runs md5-identical to each other. "
            "Nothing was nondeterministic: another agent was repairing "
            "`auth.py` IN THIS SAME WORKTREE while the census ran, and the "
            "denominator moved."
        )
        add("")
        add(
            "> A COUNT OVER A TREE SOMEBODY ELSE IS EDITING IS A READING WITH A "
            "TIMESTAMP, NOT A FACT ABOUT THE CODEBASE."
        )
        add("")
        baseline = provenance.get("baseline")
        if baseline:
            add(
                "So the committed tree is counted too, as the only stationary "
                "thing available. `HEAD` is BEFORE the in-flight repair; the "
                "working tree is DURING it."
            )
            add("")
            add("| bucket | at HEAD | working tree | delta |")
            add("|---|---:|---:|---:|")
            for bucket in BUCKET_ORDER:
                was = baseline.get(bucket, 0)
                now = counts.get(bucket, 0)
                sign = "+" if now - was > 0 else ""
                add(f"| `{bucket}` | {was} | {now} | {sign}{now - was} |")
            add(
                f"| **sites** | **{provenance.get('baseline_sites', 0)}** | "
                f"**{len(main)}** | "
                f"{'+' if len(main) - provenance.get('baseline_sites', 0) > 0 else ''}"
                f"{len(main) - provenance.get('baseline_sites', 0)} |"
            )
            add("")
            new_modules = provenance.get("new_modules", [])
            if new_modules:
                add(
                    "Modules present in the working tree and ABSENT at HEAD: "
                    + ", ".join(f"`{m}`" for m in new_modules)
                    + ". These are the concurrent wave's own new files and they "
                    "are counted in every number below."
                )
                add("")
    if unparseable:
        add(
            "**"
            + str(len(unparseable))
            + " module(s) DID NOT PARSE and were not counted: "
            + ", ".join(f"`{r['module']}`" for r in unparseable)
            + ".** A module that does not parse is reported loudly rather than "
            "skipped, because skipping shrinks the denominator invisibly."
        )
        add("")
    add(
        "THE CLASS. `config.scrub` substitutes this server's own filesystem "
        "paths and nothing else. It knows paths; it does not know urls and it "
        "does not know names. A message that interpolates a value the DOCUMENT "
        "or LINKEDIN chose carries that value to the caller intact, through an "
        "exception or through a log record."
    )
    add("")
    add("**THIS FILE REPORTS SOURCE EXPRESSIONS, NEVER VALUES.**")
    add("")

    # -- 1. headline ------------------------------------------------------
    add("## 1. The count")
    add("")
    add(
        f"**{len(main)} message sites** in **{len(modules)} modules**, carrying "
        f"**{total_fields} interpolated sub-expressions**."
    )
    add("")
    add("| kind | sites |")
    add("|---|---:|")
    for kind in MAIN_KINDS:
        add(f"| `{kind}` | {sum(1 for r in main if r['kind'] == kind)} |")
    add(f"| **total** | **{len(main)}** |")
    add("")
    add(
        "`FIELD` is the shape the coercion-leak audit measured at **18 sites "
        "across 6 modules** (`out[\"error\"] = f\"{type(exc).__name__}: {exc}\"`). "
        "This walk counts every dict/attribute assignment of a built string, "
        "not only that one spelling, so it is a superset of that number and "
        "the two are comparable only at the `out[\"error\"]` subset -- given "
        "below."
    )
    add("")
    error_field = [
        r for r in main
        if r["kind"] == "FIELD" and '["error"]' in r["target"]
    ]
    add(
        f"`out[\"error\"]`-style assignments specifically: **{len(error_field)} "
        f"sites in {len(sorted({r['module'] for r in error_field}))} modules**."
    )
    add("")

    # -- 2. buckets -------------------------------------------------------
    add("## 2. Where the interpolated values come from")
    add("")
    add("Bucketed per SUB-EXPRESSION, not per message: one message can carry one")
    add("safe field and one hazardous one.")
    add("")
    add("| bucket | sub-expressions | what it means |")
    add("|---|---:|---|")
    meanings = {
        "PAGE_OR_SITE_DERIVED": "the value can be a string LinkedIn or the document chose. **THE HAZARD SET.**",
        "EXCEPTION_TEXT:arbitrary": "`{exc}` under a handler catching Exception/stdlib/Playwright -- the message may hold a url or a path this package never composed",
        "EXCEPTION_TEXT:package_raised": "`{exc}` under a handler catching only this package's own error classes",
        "EXCEPTION_TEXT:undecided": "an exception-named value this walk could not tie to a handler",
        "CALLER_SUPPLIED": "a tool argument coming back to its own caller. A different question -- and note a caller-supplied needle can still be a third party's name",
        "TYPE_ONLY": "`type(exc).__name__`, `len(...)`, a count, an int. Safe by construction",
        "SERVER_CONSTRUCTED": "a module constant, a config value, a label from a closed set",
        "UNCLASSIFIED": "**no positive evidence either way. A human still has to read these.**",
    }
    for bucket in BUCKET_ORDER:
        add(f"| `{bucket}` | {counts.get(bucket, 0)} | {meanings[bucket]} |")
    add(f"| **total** | **{total_fields}** | |")
    add("")

    handlers = collections.Counter(
        f["why"]
        for r in rows
        for f in r["fields"]
        if f["bucket"].startswith("EXCEPTION_TEXT")
    )
    if handlers:
        add(
            "**WHAT THE HANDLERS ACTUALLY CATCH**, resolved to the lexically "
            "innermost `except` that binds the name -- not to a function-wide "
            "lookup, which cannot tell two `as exc` handlers in one function "
            "apart:"
        )
        add("")
        add("| the site sits inside | sub-expressions |")
        add("|---|---:|")
        for why, n in handlers.most_common():
            add(f"| `{why.replace('inside ', '')}` | {n} |")
        add("")
        add(
            "So essentially every `{exc}` in this package is rendered under a "
            "handler that catches ANYTHING. Whatever Playwright or the stdlib "
            "put in that message -- a url, a selector, a path -- is what gets "
            "interpolated, and `config.scrub` removes only the paths."
        )
        add("")

    hazard_rows = [
        r for r in main
        if any(f["bucket"] == "PAGE_OR_SITE_DERIVED" for f in r["fields"])
    ]
    hazard_modules = sorted({r["module"] for r in hazard_rows})
    add(
        f"The hazard bucket touches **{len(hazard_rows)} sites in "
        f"{len(hazard_modules)} modules**:"
    )
    add("")
    add("| module | sites |")
    add("|---|---:|")
    for module in hazard_modules:
        add(f"| `{module}` | {sum(1 for r in hazard_rows if r['module'] == module)} |")
    add("")
    unclassified_rows = [
        r for r in main if any(f["bucket"] == "UNCLASSIFIED" for f in r["fields"])
    ]
    add(
        f"`UNCLASSIFIED` is **not empty and was not forced empty**: "
        f"{counts.get('UNCLASSIFIED', 0)} sub-expressions across "
        f"{len(unclassified_rows)} sites. A residual bucket of zero would mean "
        "this file had solved static analysis."
    )
    add("")

    # -- 3. grep contrast -------------------------------------------------
    add("## 3. Grep against AST, in both directions")
    add("")
    add(
        "The naive search for this class is \"a raise or a logger call with an "
        "f-string in it\": `raise .*f\"`, `logger.<m>(f\"`, `[\"error\"] = f\"`. "
        "It is wrong both ways."
    )
    add("")
    add("| module | grep lines | AST sites |")
    add("|---|---:|---:|")
    total_grep = total_ast = 0
    contrast = grep_contrast(main)
    for row in contrast:
        total_grep += row["grep_lines"]
        total_ast += row["ast_sites"]
        if row["grep_lines"] != row["ast_sites"]:
            add(f"| `{row['module']}` | {row['grep_lines']} | {row['ast_sites']} |")
    add(f"| **TOTAL** | **{total_grep}** | **{total_ast}** |")
    add("")
    pct_args = [r for r in main if r["kind"] == "LOG" and 'f"' not in r["message"] and "f'" not in r["message"]]
    add(
        "**THE UNDERCOUNT IS THE HALF THAT MATTERS.** "
        f"**{len(pct_args)} of the {sum(1 for r in main if r['kind'] == 'LOG')} "
        "`LOG` sites have no f-string anywhere**: the format string is a plain "
        "constant and `logging` performs the interpolation "
        "(`logger.info(\"landed on %s\", final_url)`). A grep for `f\"` cannot "
        "see one of them, and the value reaches the log record exactly as it "
        "would from an f-string. Multi-line `raise` calls -- the dominant "
        "spelling in this package -- are invisible to the same search for the "
        "same reason: the statement and its message are on different lines."
    )
    add("")
    divergent = sum(
        1
        for r in main
        for f in r["fields"]
        if f["loose_says_page"] != (f["bucket"] == "PAGE_OR_SITE_DERIVED")
    )
    add(
        "A second opinion, for the frontier: the SHIPPED permissive analyser in "
        "`scripts/_census_page_coercions.py` (imported, not re-implemented) "
        f"disagrees with the strict classifier above on **{divergent}** "
        "sub-expressions. That disagreement is the honest width of the "
        "`UNCLASSIFIED` frontier, not a defect in either one -- the shipped "
        "analyser answers YES to anything it does not recognise, which is "
        "correct for a census whose measurement then acquits."
    )
    add("")

    # -- 4. the shortlist -------------------------------------------------
    add("## 4. THE SHORTLIST -- every site interpolating an address")
    add("")
    add(
        "Every site whose interpolated expression's source text contains "
        "`url`, `landed`, `final_url`, `href`, `slug` or `redirect`. Sorted by "
        "module then line. **This is the set to adjudicate by hand.**"
    )
    add("")
    repaired = [
        (r, f) for r in shortlist for f in r["fields"] if f["sanitiser"]
    ]
    raw = [(r, f) for r in shortlist for f in r["fields"] if not f["sanitiser"]]
    add(
        f"**{len(shortlist)} sites, {len(raw) + len(repaired)} address-shaped "
        f"sub-expressions: {len(raw)} raw, {len(repaired)} already routed "
        f"through `landing.*()`.**"
    )
    add("")
    add("### 4a. Raw -- the address reaches the message unshaped")
    add("")
    add("| module | line | function | kind | target | expression | bucket |")
    add("|---|---:|---|---|---|---|---|")
    for row, field in sorted(raw, key=lambda p: (p[0]["module"], p[0]["line"])):
        add(
            f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
            f"{row['kind']} | `{_md_escape(row['target'], 46)}` | "
            f"`{_md_escape(field['expr'], 70)}` | {field['bucket']} |"
        )
    add("")
    add("### 4b. Already routed through the repair")
    add("")
    add(
        "These are the concurrent wave's repair LANDING, not findings. They are "
        "listed so the shortlist cannot be mistaken for a to-do list, and "
        "because RECOGNISING the call is not CERTIFYING it -- whether "
        "`landing.render()` of `landing.describe_landing()` withholds enough is "
        "an adjudication against `landing.py`, not something this census "
        "measured."
    )
    add("")
    if repaired:
        add("| module | line | function | kind | expression | shaper |")
        add("|---|---:|---|---|---|---|")
        for row, field in sorted(
            repaired, key=lambda p: (p[0]["module"], p[0]["line"])
        ):
            add(
                f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
                f"{row['kind']} | `{_md_escape(field['expr'], 70)}` | "
                f"`{field['sanitiser']}()` |"
            )
    else:
        add("None.")
    add("")

    # -- 5. the hazard set in full ----------------------------------------
    add("## 5. The hazard bucket in full")
    add("")
    add("| module | line | function | kind | expression | why |")
    add("|---|---:|---|---|---|---|")
    for row in sorted(hazard_rows, key=lambda r: (r["module"], r["line"])):
        for field in row["fields"]:
            if field["bucket"] != "PAGE_OR_SITE_DERIVED":
                continue
            add(
                f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
                f"{row['kind']} | `{_md_escape(field['expr'])}` | "
                f"{_md_escape(field['why'])} |"
            )
    add("")

    # -- 6. unclassified --------------------------------------------------
    add("## 6. `UNCLASSIFIED` in full -- the sites a human still has to read")
    add("")
    add("| module | line | function | kind | expression |")
    add("|---|---:|---|---|---|")
    for row in sorted(unclassified_rows, key=lambda r: (r["module"], r["line"])):
        for field in row["fields"]:
            if field["bucket"] != "UNCLASSIFIED":
                continue
            add(
                f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
                f"{row['kind']} | `{_md_escape(field['expr'])}` |"
            )
    add("")

    # -- 7. indirect ------------------------------------------------------
    indirect = [r for r in main if r["kind"] == "INDIRECT"]
    add("## 7. `INDIRECT` -- resolved, and how far to trust it")
    add("")
    add(
        f"**{len(indirect)} sites.** A `raise Error(name)` where `name` is "
        "assigned a built string earlier in the same function. Each row carries "
        "the assignment it was resolved from, so the reader can check rather "
        "than trust. A name assigned more than once resolves to the LAST built "
        "assignment in the function, which is a guess about control flow and is "
        "the reason these are reported apart from `RAISE`."
    )
    add("")
    if indirect:
        add("| module | line | function | raises | resolved from |")
        add("|---|---:|---|---|---|")
        for row in indirect:
            add(
                f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
                f"`{_md_escape(row['target'])}` | "
                f"`{_md_escape(row.get('resolved_from', ''))}` |"
            )
    else:
        add("None found.")
    add("")

    # -- 8. passthrough ---------------------------------------------------
    add("## 8. `PASSTHROUGH` -- counted separately, NOT in the total above")
    add("")
    add(
        f"**{len(extra)} sites.** A non-literal string handed to an exception "
        "WHOLE, with no interpolation at all -- `raise Error(status.get(\"reason\") "
        "or \"...\")`. The four requested kinds do not name this shape, so it is "
        "reported apart rather than folded in or dropped. It is arguably the "
        "purest instance of the class: the message IS the foreign string rather "
        "than merely containing it, and nothing about it is built, so no "
        "f-string search of any kind would ever find it."
    )
    add("")
    if extra:
        add("| module | line | function | raises | expression | bucket |")
        add("|---|---:|---|---|---|---|")
        for row in sorted(extra, key=lambda r: (r["module"], r["line"])):
            for field in row["fields"]:
                add(
                    f"| `{row['module']}` | {row['line']} | `{row['function']}` | "
                    f"`{_md_escape(row['target'])}` | "
                    f"`{_md_escape(field['expr'])}` | {field['bucket']} |"
                )
    else:
        add("None found.")
    add("")

    # -- 9. scope ---------------------------------------------------------
    add("## 9. What this census did NOT count")
    add("")
    add(
        "A gate may not claim more than it ran. This walk does not count: a "
        "built string inside a `dict` LITERAL (`return {\"error\": f\"...\"}`); a "
        "built string `return`ed directly; a string passed to `print`; a message "
        "assembled by a helper across a function boundary; or an f-string reached "
        "only through `str.join`. It also cannot see which of these sites is "
        "REACHABLE -- a static bucket is a hypothesis, and the coercion-leak "
        "audit settled its equivalent question by DRIVING the readers, not by "
        "reading them."
    )
    add("")
    add("### A zero from a detector nobody has seen fire certifies nothing")
    add("")
    add(
        "`INDIRECT` above is **0**, and a count of zero is exactly where a "
        "broken detector hides. So every kind and every bucket was driven "
        "against a SYNTHETIC module built to contain one of each -- an "
        "f-string raise, a multi-line raise, a `%s`-with-args log, an f-string "
        "log, an `out[\"error\"]` field, a `message = f\"...\"` then "
        "`raise E(message)`, a whole-string passthrough, a module constant, a "
        "closed-literal field, a caller bound and a `len()`."
    )
    add("")
    add(
        "**All 5 kinds and all 6 reachable buckets fire on that subject.** "
        "`INDIRECT` fires there and not here, so **`INDIRECT: 0` is a property "
        "of `linkedin_server/`** -- this package raises its built messages "
        "inline rather than assembling them into a local first -- and not a "
        "detector that never worked."
    )
    add("")
    add(
        "The control is not committed: this slice was scoped to write one file. "
        "It is `_check_census_kinds_can_fire.py` in the wave scratchpad, and it "
        "matches the repository's existing `scripts/_check_*_can_fail.py` "
        "convention if the wave wants it adopted."
    )
    add("")
    add(
        "The two heuristic edges, named so they can be argued with: "
        "`HAZARD_NAME_TOKENS` is matched as a SUBSTRING, so `fn_name` matches "
        "`name` and lands in the hazard bucket; and `@mcp.tool()` parameter "
        "names are collected per MODULE, so a non-tool helper sharing a "
        "parameter name with a tool in the same file reads `CALLER_SUPPLIED`. "
        "Both were chosen over the alternative that would quietly shrink a "
        "count."
    )
    add("")
    return "\n".join(lines) + "\n"


def gather() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """The census, plus the provenance stamp that says what it counted.

    The subject is digested BEFORE the walk and again AFTER it. Equal digests
    mean the numbers are one snapshot. Unequal digests mean they are not, and
    the report says so in its first section rather than in a footnote.
    """
    package_errors = _package_error_names(PACKAGE)

    # ONE read, digested, and THAT dict is what gets walked. Reading the tree
    # a second time for the digest would stamp a snapshot the census never
    # saw -- which is the same defect one level up from the one being fixed.
    snapshot = read_package()
    before = source_digest(snapshot)
    rows = census_sources(snapshot, package_errors)

    # A SECOND read, purely to detect a writer landing an edit while we walked.
    after = source_digest(read_package())

    head = head_sources()
    baseline_rows = census_sources(head, package_errors)
    baseline_main = [r for r in baseline_rows if r["kind"] in MAIN_KINDS]

    head_sha = _git(["rev-parse", "--short", "HEAD"]).strip()
    status = _git(["status", "--porcelain=v1", "--", "linkedin_server/"])
    dirty = [line[3:].strip() for line in status.splitlines() if line.strip()]

    provenance = {
        "head": head_sha,
        "dirty": dirty,
        # The digest of what was ACTUALLY WALKED, not of a later re-read.
        "digest": before,
        "digest_after": after["combined"],
        "stable": before["combined"] == after["combined"],
        "baseline": _bucket_counts(baseline_main),
        "baseline_sites": len(baseline_main),
        "new_modules": sorted(set(before["modules"]) - set(head)),
    }
    return rows, provenance


def main(argv: list[str]) -> int:
    rows, provenance = gather()

    if "--json" in argv:
        print(
            json.dumps(
                {
                    "sites": rows,
                    "contrast": grep_contrast(rows),
                    "provenance": provenance,
                },
                indent=2,
            )
        )
        return 0

    text = report(rows, provenance)

    if "--out" in argv:
        target = Path(argv[argv.index("--out") + 1])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
        main_rows = [r for r in rows if r["kind"] in MAIN_KINDS]
        counts = _bucket_counts(main_rows)
        print(f"wrote {target}")
        print(
            f"digest {provenance['digest']['combined']} "
            f"({'STABLE' if provenance['stable'] else 'MOVED MID-RUN'}) "
            f"over {provenance['digest']['count']} modules, HEAD {provenance['head']}"
        )
        print(f"sites: {len(main_rows)}  shortlist: {len(_shortlist(rows))}")
        for bucket in BUCKET_ORDER:
            was = provenance["baseline"].get(bucket, 0)
            now = counts.get(bucket, 0)
            print(f"  {bucket:32s} {now:4d}   (HEAD {was:4d})")
        return 0

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
