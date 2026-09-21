"""Census: every Playwright STRICT MODE call site in linkedin_server/*.py.

THE MEASURED FACT THIS SERVES. Playwright 1.63.0, driven against a planted
local page (``scripts/_probe_what_playwright_quotes.py``), raises a STRICT
MODE VIOLATION whose message enumerates every matched element with its FULL
OUTER HTML -- id, class, every attribute value, its text -- plus an
``aka get_by_text("<the element's text>")`` suggestion, whenever a ``Locator``
method that resolves to exactly one element is called on a locator that
matches 2+. A ``Page``/``Frame``-level selector method (``page.text_content(sel)``,
``page.click(sel)``) is NOT strict by default -- measured: it silently picks
the first of several matches -- unless ``strict=True`` is passed. So a call
site of this shape is a place PAGE CONTENT CAN ENTER AN EXCEPTION STRING, and
this script enumerates every one of them in this package and says whether it
can actually be reached with 2+ matches, as far as a static, non-executing
read can tell.

## THE TWO DEFINITIONS, verbatim from the brief this script implements

STRICT_METHODS -- Locator methods that resolve to exactly one element and
therefore raise strict mode violation when the locator matches 2+ (37 names):
``text_content``, ``inner_text``, ``inner_html``, ``get_attribute``,
``input_value``, ``click``, ``fill``, ``check``, ``uncheck``, ``hover``,
``press``, ``type``, ``select_option``, ``set_input_files``, ``focus``,
``blur``, ``tap``, ``dblclick``, ``is_visible``, ``is_hidden``, ``is_enabled``,
``is_disabled``, ``is_checked``, ``is_editable``, ``bounding_box``,
``element_handle``, ``screenshot``, ``scroll_into_view_if_needed``,
``wait_for``, ``evaluate``, ``evaluate_handle``, ``dispatch_event``,
``drag_to``, ``clear``, ``press_sequentially``, ``aria_snapshot``,
``content_frame``. (``text_contents`` -- plural -- is explicitly NOT one of
these; it is a distractor name and is not matched.)

NON_STRICT_METHODS -- Locator methods that operate on the whole match set and
CANNOT raise strict mode violation: ``count``, ``all``, ``all_text_contents``,
``all_inner_texts``, ``first``, ``last``, ``nth``, ``filter``, ``locator``,
``get_by_*`` (the whole family: role/text/label/placeholder/alt_text/title/
test_id), ``or_``, ``and_``, ``evaluate_all``, ``element_handles``,
``frame_locator``, ``highlight``, ``describe``. These never appear as a
VULNERABLE/IMMUNE candidate site in the tables below -- they cannot raise the
violation this census is about, so counting them would inflate the
denominator with sites that cannot hold the defect.

PLUS ONE PAGE/FRAME-ONLY METHOD outside both lists: ``wait_for_selector``
exists on ``Page``/``Frame`` and not on ``Locator`` at all (``Locator`` has
``wait_for`` instead, which IS in STRICT_METHODS above). It shares the same
``strict=`` switch as the Page-level members of STRICT_METHODS and is always
routed through that rule here.

## QUALIFICATION -- what makes a site IMMUNE rather than VULNERABLE

A locator expression is QUALIFIED (strict-IMMUNE by construction) if its
chain ends in ``.first``, ``.last``, or ``.nth(<any>)`` IMMEDIATELY before the
strict method is called -- ``.nth(...)`` is a call, ``.first``/``.last`` are
attributes. It is also IMMUNE if the strict method is reached on a
``Page``/``Frame`` object with a selector argument and no ``strict=True``
keyword (Page/Frame-level calls default to ``strict=False``); if ``strict=True``
IS passed, it is VULNERABLE. A ``for``/``async for`` loop variable bound from
``await <expr>.all()`` or from ``<expr>.element_handles()`` is also IMMUNE --
each element of that iteration is a SINGLE element, never a multi-match
locator -- and is reported under the same ``.all() element`` bucket as the
loop's own name suggests, folding the (structurally identical) ElementHandle
case into it rather than inventing a sixth reason the report never asked for.

Everything else that calls a STRICT_METHOD on a locator-valued expression is
VULNERABLE. If a receiver cannot be resolved by this walk at all, it is
UNRESOLVED -- never guessed into either bucket. See ``classify_receiver`` and
``_is_recognized_root`` for the exact algorithm, and the CONTROL/METHOD
sections of ``_audit/_slice-strict-call-sites.md`` for what this walk does
and does not see.

## USAGE

    venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py
    venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py --json PATH
    venv/Scripts/python.exe scripts/_census_strict_mode_call_sites.py --selftest

Pure stdlib ``ast``. No side effects, no network, no browser. Reads
``linkedin_server/*.py`` (non-recursive -- the package has no subpackages)
and nothing else, except under ``--selftest``, which parses only an inline
fixture string manufactured in this file.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, NamedTuple, Optional

# ---------------------------------------------------------------------------
# Paths -- resolved relative to this file, never hard-coded.
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
PACKAGE = REPO / "linkedin_server"

# ---------------------------------------------------------------------------
# The two definitions (see module docstring). Both are MEASURED against the
# real Playwright 1.63.0 API by scripts/_probe_what_playwright_quotes.py,
# not guessed here.
# ---------------------------------------------------------------------------

STRICT_METHODS: frozenset[str] = frozenset({
    "text_content", "inner_text", "inner_html", "get_attribute", "input_value",
    "click", "fill", "check", "uncheck", "hover", "press",
    "type", "select_option", "set_input_files", "focus", "blur", "tap", "dblclick",
    "is_visible", "is_hidden", "is_enabled", "is_disabled", "is_checked",
    "is_editable", "bounding_box", "element_handle", "screenshot",
    "scroll_into_view_if_needed", "wait_for", "evaluate", "evaluate_handle",
    "dispatch_event", "drag_to", "clear", "press_sequentially", "aria_snapshot",
    "content_frame",
})
assert len(STRICT_METHODS) == 37, "transcription error against the brief"
assert "text_contents" not in STRICT_METHODS, "the plural is a distractor, not a member"

NON_STRICT_METHODS: frozenset[str] = frozenset({
    "count", "all", "all_text_contents", "all_inner_texts", "first", "last",
    "nth", "filter", "locator", "or_", "and_", "evaluate_all",
    "element_handles", "frame_locator", "highlight", "describe",
})

#: Page/Frame-only method sharing the strict=True/False switch; not a Locator
#: method at all (see module docstring).
PAGE_ONLY_SELECTOR_METHOD = "wait_for_selector"

#: Every attribute name that is a candidate SITE for the VULNERABLE/IMMUNE
#: classification below.
CANDIDATE_METHODS: frozenset[str] = STRICT_METHODS | {PAGE_ONLY_SELECTOR_METHOD}

#: Attribute names (called, not accessed) that QUALIFY a chain -- their
#: presence as the OUTERMOST operation of a receiver expression means that
#: receiver can only ever be a single element.
_QUALIFYING_ATTR = ("first", "last")  # accessed, not called
_QUALIFYING_CALL = "nth"              # called: .nth(i)

#: Operations (besides the qualifiers above) that still produce a
#: LOCATOR-VALUED result -- possibly still multi-match. Combined with the
#: get_by_* family (matched by prefix, see _is_locator_producing).
_LOCATOR_PRODUCING_ATTR = frozenset({"locator", "filter", "or_", "and_"})

#: Parameter/root names this walk recognises as pointing at a Playwright
#: Page/Frame or an already-scoped Locator handed to a helper.
PAGE_FRAME_NAMES = frozenset({"page", "frame"})
TRACKED_ROOTS = frozenset({"page", "frame", "root", "el", "container", "scope"})

#: The four call-site families the interpolated-selector table inspects.
#: ":has-text(...)" from the brief is Playwright's `has_text=` keyword,
#: available on .locator()/.filter()/.get_by_text() -- see the METHOD
#: section of the slice report for why this table checks that keyword
#: explicitly rather than only positional arguments.
INTERP_TARGET_ATTRS: frozenset[str] = frozenset(
    {"locator", "get_by_text", "filter", PAGE_ONLY_SELECTOR_METHOD}
)


def _is_get_by(attr: str) -> bool:
    return attr.startswith("get_by_")


def _is_locator_producing(attr: str) -> bool:
    return attr in _LOCATOR_PRODUCING_ATTR or _is_get_by(attr)


# ---------------------------------------------------------------------------
# Scope walking -- each FunctionDef/AsyncFunctionDef (at ANY nesting depth)
# and the module's own top-level code are independent scopes. A nested def
# is a BOUNDARY: its body is not pulled into the enclosing scope's bindings,
# and its own calls are not attributed to the enclosing function -- it is
# visited separately, as its own scope, by the module-level scope finder.
# ---------------------------------------------------------------------------

_SCOPE_BOUNDARY = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _iter_own_scope(node: ast.AST):
    """Yield every descendant of ``node`` that belongs to node's OWN scope --
    i.e. do not descend into a nested function/lambda/class body. ``node``
    itself is not yielded."""
    for child in ast.iter_child_nodes(node):
        yield child
        if isinstance(child, _SCOPE_BOUNDARY):
            continue
        yield from _iter_own_scope(child)


def _iter_scopes(module: ast.Module):
    """Yield (name, node) for every scope in the module: "<module>" for the
    top level, then every FunctionDef/AsyncFunctionDef at any depth, each
    named by its own ``.name`` (a nested def or a method is reported by its
    own name only, not dotted to its parent -- see the METHOD section for
    what this costs when two scopes share a name)."""
    yield "<module>", module
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node.name, node


# ---------------------------------------------------------------------------
# Bindings: name -> every assignment to it in this scope, with the line it
# was written on. ALL plain-Name assignments are recorded, regardless of
# what shape the value is -- not just locator-looking ones -- so that a
# LATER, non-qualifying reassignment correctly SHADOWS an earlier qualifying
# one at resolution time (see case_reassignment_shadow in the selftest
# fixture). Classification of whichever binding is nearest-above a given use
# happens structurally, in classify_receiver, not at collection time.
# ---------------------------------------------------------------------------


class Binding(NamedTuple):
    lineno: int
    value: ast.AST
    is_all_element: bool


def _strip_await(node: ast.AST) -> ast.AST:
    return node.value if isinstance(node, ast.Await) else node


def _is_all_or_element_handles_call(node: ast.AST) -> bool:
    inner = _strip_await(node)
    return (
        isinstance(inner, ast.Call)
        and isinstance(inner.func, ast.Attribute)
        and inner.func.attr in ("all", "element_handles")
    )


def _collect_bindings(scope: ast.AST) -> dict[str, list[Binding]]:
    bindings: dict[str, list[Binding]] = {}

    def add(name: str, lineno: int, value: ast.AST, is_all_element: bool = False) -> None:
        bindings.setdefault(name, []).append(Binding(lineno, value, is_all_element))

    for node in _iter_own_scope(scope):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            value = node.value
            if value is None:  # AnnAssign with no value (a bare annotation)
                continue
            targets = list(getattr(node, "targets", [])) or [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    add(target.id, node.lineno, value)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            if isinstance(node.target, ast.Name):
                all_elem = _is_all_or_element_handles_call(node.iter)
                add(node.target.id, node.lineno, node.iter, all_elem)
        elif isinstance(node, ast.withitem):
            if isinstance(node.optional_vars, ast.Name):
                # withitem carries no lineno of its own; the context_expr does.
                lineno = getattr(node.context_expr, "lineno", 0)
                add(node.optional_vars.id, lineno, node.context_expr)

    return bindings


def _nearest_binding(bindings: dict[str, list[Binding]], name: str,
                      use_lineno: int) -> Optional[Binding]:
    entries = bindings.get(name)
    if not entries:
        return None
    candidates = [b for b in entries if b.lineno <= use_lineno]
    if not candidates:
        return None
    return max(candidates, key=lambda b: b.lineno)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

HOP_LIMIT = 8


def _is_recognized_root(expr: ast.AST, bindings: dict[str, list[Binding]],
                         use_lineno: int, hops: int = 0) -> bool:
    """Can this expression be confirmed, by local static resolution, to be
    the page/frame object, a helper parameter conventionally holding an
    already-scoped locator (root/el/container/scope), or a further chain
    built on top of one of those? False means "not locally decidable" --
    the caller must then answer UNRESOLVED rather than guess VULNERABLE.
    """
    if hops > HOP_LIMIT:
        return False
    if isinstance(expr, ast.Name):
        # A LOCAL BINDING (this name was assigned somewhere above, in this
        # scope) always takes priority over treating the name as an opaque
        # incoming parameter -- a local `container = page.locator(x).first`
        # shadows the parameter-convention meaning of "container" and must
        # resolve through its actual assignment, not around it. Only when
        # no local binding exists at all is bare TRACKED_ROOTS membership
        # (a genuine incoming parameter) the answer.
        nearest = _nearest_binding(bindings, expr.id, use_lineno)
        if nearest is not None:
            if nearest.is_all_element:
                return True
            return _is_recognized_root(nearest.value, bindings, nearest.lineno, hops + 1)
        if expr.id in TRACKED_ROOTS:
            return True
        return False
    if isinstance(expr, ast.Attribute) and expr.attr in _QUALIFYING_ATTR:
        return _is_recognized_root(expr.value, bindings, use_lineno, hops + 1)
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
        if expr.func.attr == _QUALIFYING_CALL or _is_locator_producing(expr.func.attr):
            return _is_recognized_root(expr.func.value, bindings, use_lineno, hops + 1)
    return False


def classify_receiver(expr: ast.AST, bindings: dict[str, list[Binding]],
                       use_lineno: int, hops: int = 0) -> tuple[str, str]:
    """Classify a strict-method call's RECEIVER expression.

    Returns (verdict, reason) with verdict in {"QUALIFIED", "VULNERABLE",
    "UNRESOLVED"}. QUALIFIED/VULNERABLE map onto the report's IMMUNE/
    VULNERABLE buckets; UNRESOLVED is never folded into either.
    """
    if hops > HOP_LIMIT:
        return "UNRESOLVED", "hop-limit"

    # 1. Syntactic qualification at the OUTERMOST node -- no resolution
    #    needed: `x.first.method()` is immune regardless of what `x` is.
    if isinstance(expr, ast.Attribute) and expr.attr in _QUALIFYING_ATTR:
        return "QUALIFIED", expr.attr
    if (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute)
            and expr.func.attr == _QUALIFYING_CALL):
        return "QUALIFIED", "nth"

    # 2. A bare Name -- a LOCAL BINDING (nearest lineno above) always takes
    #    priority over the opaque-parameter reading: `container = page.
    #    locator(x).first` followed by a bare `container.inner_text()` must
    #    resolve through that assignment, not be treated as an unnarrowed
    #    parameter just because "container" is also a recognised root name.
    if isinstance(expr, ast.Name):
        nearest = _nearest_binding(bindings, expr.id, use_lineno)
        if nearest is not None:
            if nearest.is_all_element:
                return "QUALIFIED", "all-element"
            return classify_receiver(nearest.value, bindings, nearest.lineno, hops + 1)
        if expr.id in TRACKED_ROOTS:
            # A bare root/el/container/scope PARAMETER used directly as the
            # receiver, with no local binding and no chain operator applied
            # to it in this scope. This walk cannot see how the CALLER
            # constructed it -- it might already be a single element, or
            # might not be. Not decidable locally, so UNRESOLVED rather than
            # a guess either way. (page/frame never reach this branch:
            # classify_site() routes a bare page/frame receiver through the
            # page-level rule before this function is ever called on it.)
            return "UNRESOLVED", "opaque-root-param"
        return "UNRESOLVED", "no-binding"

    # 3. A directly-written locator-producing call: `X.locator(sel)`,
    #    `X.get_by_text(t)`, `X.filter(...)`, `X.or_(...)`, `X.and_(...)`.
    #    Unqualified at THIS level regardless of what it resolves to further
    #    down -- `.first.locator(b)` narrows then re-searches, which can
    #    match 2+ again, so it is correctly VULNERABLE here even though its
    #    own receiver was itself qualified.
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) \
            and _is_locator_producing(expr.func.attr):
        if _is_recognized_root(expr.func.value, bindings, use_lineno, hops + 1):
            return "VULNERABLE", "bare:." + expr.func.attr
        return "UNRESOLVED", "unrecognised-root"

    # 4. Anything else this walk does not recognise.
    return "UNRESOLVED", "unrecognised-shape:" + type(expr).__name__


def classify_site(attr: str, receiver: ast.AST, call: ast.Call,
                   bindings: dict[str, list[Binding]],
                   use_lineno: int) -> tuple[str, str]:
    """Classify one candidate call site. Returns (verdict, reason) with
    verdict in {"VULNERABLE", "IMMUNE", "UNRESOLVED"} -- the report-facing
    three-way split (QUALIFIED from classify_receiver becomes IMMUNE here).
    """
    is_bare_page_frame = isinstance(receiver, ast.Name) and receiver.id in PAGE_FRAME_NAMES

    if attr == PAGE_ONLY_SELECTOR_METHOD or is_bare_page_frame:
        # Page/Frame-level call: defaults to strict=False. wait_for_selector
        # is ALWAYS routed here -- Locator has no such method in the real
        # API, so any appearance of this name is assumed Page/Frame-level
        # regardless of receiver shape (see module docstring).
        strict_kw = next((kw.value for kw in call.keywords if kw.arg == "strict"), None)
        strict_true = isinstance(strict_kw, ast.Constant) and strict_kw.value is True
        if strict_true:
            return "VULNERABLE", "page-level-strict-true"
        return "IMMUNE", "page-level-non-strict"

    verdict, reason = classify_receiver(receiver, bindings, use_lineno)
    if verdict == "QUALIFIED":
        return "IMMUNE", reason
    if verdict == "VULNERABLE":
        return "VULNERABLE", reason
    return "UNRESOLVED", reason


#: The five IMMUNE reason buckets the report breaks down by, in this order.
#: A reason string from classify_site that does not literally match one of
#: these is folded to "other" -- kept distinct from the five so the report
#: cannot silently mis-bucket a reason it does not recognise.
IMMUNE_REASON_BUCKETS = ("first", "last", "nth", "page-level-non-strict", "all-element")


def _immune_bucket(reason: str) -> str:
    return reason if reason in IMMUNE_REASON_BUCKETS else "other"


# ---------------------------------------------------------------------------
# Interpolated-selector detection (a separate, independent question from
# VULNERABLE/IMMUNE -- see module docstring and the brief's own framing:
# "You are NOT asked to decide whether the interpolated value is page-
# derived -- only to enumerate the sites". This checks the FIRST positional
# argument of every call to one of INTERP_TARGET_ATTRS, AND a `has_text=`
# keyword argument if present (Playwright's structured form of :has-text()).
# ---------------------------------------------------------------------------


def _interp_shape(node: ast.AST) -> Optional[str]:
    """None if `node` is a plain literal (not interpolated); otherwise a
    short label for the non-literal shape. Broader than the brief's four
    named forms (f-string / %-format / .format() / + concat / variable) --
    ANY non-constant argument is flagged, sub-labelled by shape, because a
    bare call to a selector-building helper (this package has several,
    e.g. ``named_role_selector(role, name)``) is exactly the hazard shape
    and none of the four named forms would have caught it. See the METHOD
    section of the slice report."""
    if isinstance(node, ast.Constant):
        return None
    if isinstance(node, ast.JoinedStr):
        return "f-string"
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mod):
            return "percent-format"
        if isinstance(node.op, ast.Add):
            return "concat"
        return "binop-other"
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"):
        return "dot-format"
    if isinstance(node, ast.Name):
        return "name"
    return "other-non-literal:" + type(node).__name__


# ---------------------------------------------------------------------------
# The walk over one module -- produces both tables for that module.
# ---------------------------------------------------------------------------


def census_module(tree: ast.Module, module_name: str,
                   source_lines: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Returns (sites, interpolations) for one already-parsed module."""
    sites: list[dict[str, Any]] = []
    interpolations: list[dict[str, Any]] = []

    for fn_name, scope in _iter_scopes(tree):
        bindings = _collect_bindings(scope)
        for node in _iter_own_scope(scope):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                continue
            attr = node.func.attr
            lineno = node.lineno
            src = source_lines[lineno - 1].strip() if 0 < lineno <= len(source_lines) else ""

            if attr in CANDIDATE_METHODS:
                verdict, reason = classify_site(attr, node.func.value, node, bindings, lineno)
                sites.append({
                    "module": module_name,
                    "function": fn_name,
                    "line": lineno,
                    "attr": attr,
                    "verdict": verdict,
                    "reason": reason,
                    "immune_bucket": _immune_bucket(reason) if verdict == "IMMUNE" else "",
                    "source": src,
                })

            if attr in INTERP_TARGET_ATTRS:
                if node.args:
                    shape = _interp_shape(node.args[0])
                    if shape is not None:
                        interpolations.append({
                            "module": module_name, "function": fn_name, "line": lineno,
                            "attr": attr, "arg_kind": "positional", "shape": shape,
                            "source": src,
                        })
                for kw in node.keywords:
                    if kw.arg == "has_text":
                        shape = _interp_shape(kw.value)
                        if shape is not None:
                            interpolations.append({
                                "module": module_name, "function": fn_name, "line": lineno,
                                "attr": attr, "arg_kind": "has_text=", "shape": shape,
                                "source": src,
                            })

    return sites, interpolations


def census(package: Path = PACKAGE) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Every candidate site and every interpolated-selector site across
    every module in `package`, sorted for diffability."""
    all_sites: list[dict[str, Any]] = []
    all_interp: list[dict[str, Any]] = []
    for path in sorted(package.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        sites, interp = census_module(tree, path.name, text.splitlines())
        all_sites.extend(sites)
        all_interp.extend(interp)
    all_sites.sort(key=lambda r: (r["module"], r["line"]))
    all_interp.sort(key=lambda r: (r["module"], r["line"]))
    return all_sites, all_interp


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def _totals(sites: list[dict[str, Any]]) -> dict[str, Any]:
    out = {"VULNERABLE": 0, "IMMUNE": 0, "UNRESOLVED": 0}
    immune_by_reason = {b: 0 for b in IMMUNE_REASON_BUCKETS}
    immune_by_reason["other"] = 0
    for row in sites:
        out[row["verdict"]] += 1
        if row["verdict"] == "IMMUNE":
            immune_by_reason[row["immune_bucket"]] += 1
    out["immune_by_reason"] = immune_by_reason
    return out


def _per_module(sites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    modules = sorted({r["module"] for r in sites})
    rows = []
    for m in modules:
        subset = [r for r in sites if r["module"] == m]
        t = _totals(subset)
        rows.append({"module": m, "vulnerable": t["VULNERABLE"],
                     "immune": t["IMMUNE"], "unresolved": t["UNRESOLVED"],
                     "total": len(subset)})
    return rows


def print_report(sites: list[dict[str, Any]], interp: list[dict[str, Any]]) -> None:
    totals = _totals(sites)
    print(f"CANDIDATE SITES: {len(sites)}  "
          f"(STRICT_METHODS or {PAGE_ONLY_SELECTOR_METHOD}, called on an "
          f"Attribute receiver, across {len(set(r['module'] for r in sites))} modules)")
    print()
    print(f"  VULNERABLE  {totals['VULNERABLE']:4d}")
    print(f"  IMMUNE      {totals['IMMUNE']:4d}")
    print(f"  UNRESOLVED  {totals['UNRESOLVED']:4d}")
    print()
    print("  IMMUNE by reason:")
    for bucket in (*IMMUNE_REASON_BUCKETS, "other"):
        print(f"    {bucket:22s} {totals['immune_by_reason'][bucket]:4d}")
    print()
    print(f"  {'module':28s} {'vuln':>5s} {'immune':>7s} {'unres':>6s} {'total':>6s}")
    for row in _per_module(sites):
        print(f"  {row['module']:28s} {row['vulnerable']:5d} {row['immune']:7d} "
              f"{row['unresolved']:6d} {row['total']:6d}")
    print()
    vuln = [r for r in sites if r["verdict"] == "VULNERABLE"]
    print(f"VULNERABLE SITES ({len(vuln)}):")
    for row in vuln:
        print(f"  {row['module']}::{row['function']}  L{row['line']}  .{row['attr']}(")
        print(f"    {row['source']}")
    print()
    print(f"INTERPOLATED SELECTORS ({len(interp)}):")
    for row in interp:
        print(f"  {row['module']}::{row['function']}  L{row['line']}  "
              f".{row['attr']}({row['arg_kind']})  [{row['shape']}]")
        print(f"    {row['source']}")


# ---------------------------------------------------------------------------
# --selftest -- an inline fixture, NOT found anywhere in the repo, with
# hand-declared expected verdicts. Runs the REAL classify_site/classify_
# receiver code above, not a reimplementation.
# ---------------------------------------------------------------------------

FIXTURE_SOURCE = '''
async def case_qualified_first(page):
    row = page.locator(".card")
    card = row.first
    return await card.text_content()


async def case_qualified_last(page):
    row = page.locator(".card")
    card = row.last
    return await card.inner_text()


async def case_qualified_nth(page):
    row = page.locator(".card")
    card = row.nth(0)
    return await card.get_attribute("data-id")


async def case_bare_vulnerable(page):
    row = page.locator(".card")
    return await row.text_content()


async def case_bare_vulnerable_inline(page):
    return await page.locator(".card").click()


async def case_page_level_non_strict(page):
    return await page.text_content(".card")


async def case_page_level_strict_true(page):
    return await page.text_content(".card", strict=True)


async def case_wait_for_selector_non_strict(page):
    return await page.wait_for_selector(".card")


async def case_wait_for_selector_strict(page):
    return await page.wait_for_selector(".card", strict=True)


async def case_all_loop_element(page):
    out = []
    for card in await page.locator(".card").all():
        out.append(await card.text_content())
    return out


async def case_element_handles_loop(page):
    out = []
    for card in await page.locator(".card").element_handles():
        out.append(await card.get_attribute("data-id"))
    return out


async def case_unresolved_receiver(page, mystery):
    return await mystery.text_content()


async def case_unresolved_opaque_root(root):
    return await root.text_content()


async def case_tracked_root_name_locally_shadowed(page):
    # A LOCAL variable happens to share a name with TRACKED_ROOTS
    # ("container") -- its own assignment must win over treating it as an
    # opaque incoming parameter. Regression case for the real dom.py
    # read_company_about_card site this walk mis-scored before the fix
    # (L1028/L1046 -- "container = page.locator(...).first" then a bare
    # "container.inner_text()").
    container = page.locator(".about").first
    return await container.inner_text()


async def case_non_strict_method_not_a_site(page):
    row = page.locator(".card")
    return await row.count()


async def case_reassignment_shadow(page, other):
    x = page.locator(".card").first
    x = other
    return await x.text_content()


async def case_multihop_alias(page):
    a = page.locator(".card")
    b = a
    c = b.nth(2)
    return await c.get_attribute("data-id")


async def case_nested_locator_after_first(page):
    row = page.locator(".card").first
    inner = row.locator(".title")
    return await inner.text_content()


async def case_container_root_chain(container):
    links = container.locator("a[href]")
    return await links.nth(0).get_attribute("href")


async def case_fstring_selector(page, tag):
    loc = page.locator(f".card-{tag}")
    return await loc.first.text_content()


async def case_percent_format_selector(page, tag):
    return await page.locator(".card-%s" % tag).count()


async def case_concat_selector(page, tag):
    return await page.locator(".card-" + tag).count()


async def case_dot_format_selector(page, tag):
    return await page.locator(".card-{}".format(tag)).count()


async def case_literal_selector_not_interpolated(page):
    return await page.locator(".card").count()


async def case_get_by_text_variable(page, label):
    return await page.get_by_text(label).count()


async def case_has_text_kwarg_variable(page, needle):
    return await page.locator(".card").filter(has_text=needle).count()


async def case_has_text_kwarg_literal(page):
    return await page.locator(".card").filter(has_text="Open").count()
'''.lstrip("\n")

# Expected (verdict, reason) for the STRICT_METHODS/wait_for_selector site
# in each case function that has exactly one. Functions not listed here are
# checked only for absence (case_non_strict_method_not_a_site) or are
# exercised for the interpolation table instead (checked separately below).
EXPECTED_SITES: dict[str, tuple[str, str]] = {
    "case_qualified_first": ("IMMUNE", "first"),
    "case_qualified_last": ("IMMUNE", "last"),
    "case_qualified_nth": ("IMMUNE", "nth"),
    "case_bare_vulnerable": ("VULNERABLE", "bare:.locator"),
    "case_bare_vulnerable_inline": ("VULNERABLE", "bare:.locator"),
    "case_page_level_non_strict": ("IMMUNE", "page-level-non-strict"),
    "case_page_level_strict_true": ("VULNERABLE", "page-level-strict-true"),
    "case_wait_for_selector_non_strict": ("IMMUNE", "page-level-non-strict"),
    "case_wait_for_selector_strict": ("VULNERABLE", "page-level-strict-true"),
    "case_all_loop_element": ("IMMUNE", "all-element"),
    "case_element_handles_loop": ("IMMUNE", "all-element"),
    "case_unresolved_receiver": ("UNRESOLVED", "no-binding"),
    "case_unresolved_opaque_root": ("UNRESOLVED", "opaque-root-param"),
    "case_tracked_root_name_locally_shadowed": ("IMMUNE", "first"),
    "case_reassignment_shadow": ("UNRESOLVED", "no-binding"),
    "case_multihop_alias": ("IMMUNE", "nth"),
    "case_nested_locator_after_first": ("VULNERABLE", "bare:.locator"),
    "case_container_root_chain": ("IMMUNE", "nth"),
}

#: Functions that must produce ZERO candidate sites at all.
EXPECTED_NO_SITE = ("case_non_strict_method_not_a_site",)

# Expected interpolation-table rows, keyed by function name -> list of
# (attr, arg_kind, shape). A function absent here must produce NONE.
EXPECTED_INTERP: dict[str, list[tuple[str, str, str]]] = {
    "case_fstring_selector": [("locator", "positional", "f-string")],
    "case_percent_format_selector": [("locator", "positional", "percent-format")],
    "case_concat_selector": [("locator", "positional", "concat")],
    "case_dot_format_selector": [("locator", "positional", "dot-format")],
    "case_get_by_text_variable": [("get_by_text", "positional", "name")],
    "case_has_text_kwarg_variable": [("filter", "has_text=", "name")],
}
EXPECTED_NO_INTERP = ("case_literal_selector_not_interpolated", "case_has_text_kwarg_literal")


def run_selftest() -> int:
    tree = ast.parse(FIXTURE_SOURCE, filename="<selftest-fixture>")
    lines = FIXTURE_SOURCE.splitlines()
    sites, interp = census_module(tree, "<selftest-fixture>", lines)

    sites_by_fn: dict[str, list[dict[str, Any]]] = {}
    for row in sites:
        sites_by_fn.setdefault(row["function"], []).append(row)
    interp_by_fn: dict[str, list[dict[str, Any]]] = {}
    for row in interp:
        interp_by_fn.setdefault(row["function"], []).append(row)

    failures = 0
    checked = 0

    def check(label: str, ok: bool, expected: str, actual: str) -> None:
        nonlocal failures, checked
        checked += 1
        mark = "ok  " if ok else "FAIL"
        print(f"  [{mark}] {label:46s} expected={expected:34s} actual={actual}")
        if not ok:
            failures += 1

    print(f"SELFTEST -- {len(EXPECTED_SITES)} site cases, "
          f"{len(EXPECTED_NO_SITE)} no-site cases, "
          f"{len(EXPECTED_INTERP)} interpolation cases, "
          f"{len(EXPECTED_NO_INTERP)} no-interpolation cases")
    print()

    for fn_name, (exp_verdict, exp_reason) in sorted(EXPECTED_SITES.items()):
        rows = sites_by_fn.get(fn_name, [])
        if len(rows) != 1:
            check(fn_name, False, f"exactly 1 site ({exp_verdict},{exp_reason})",
                  f"{len(rows)} site(s)")
            continue
        row = rows[0]
        actual = (row["verdict"], row["reason"])
        check(fn_name, actual == (exp_verdict, exp_reason),
              f"{exp_verdict},{exp_reason}", f"{actual[0]},{actual[1]}")

    for fn_name in EXPECTED_NO_SITE:
        rows = sites_by_fn.get(fn_name, [])
        check(fn_name, len(rows) == 0, "0 sites", f"{len(rows)} site(s)")

    for fn_name, expected_rows in sorted(EXPECTED_INTERP.items()):
        actual_rows = sorted((r["attr"], r["arg_kind"], r["shape"])
                              for r in interp_by_fn.get(fn_name, []))
        expected_sorted = sorted(expected_rows)
        check(fn_name, actual_rows == expected_sorted,
              str(expected_sorted), str(actual_rows))

    for fn_name in EXPECTED_NO_INTERP:
        rows = interp_by_fn.get(fn_name, [])
        check(fn_name, len(rows) == 0, "0 interpolation rows",
              f"{len(rows)} row(s)")

    print()
    print(f"SELFTEST: {checked - failures}/{checked} passed, {failures} failed.")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", metavar="PATH", default=None,
                     help="write the machine-readable census to PATH instead "
                          "of printing the human report")
    ap.add_argument("--selftest", action="store_true",
                     help="run the inline-fixture control and exit non-zero "
                          "on any mismatch")
    args = ap.parse_args(argv)

    if args.selftest:
        return run_selftest()

    sites, interp = census()

    if args.json:
        payload = {
            "definitions": {
                "strict_methods": sorted(STRICT_METHODS),
                "non_strict_methods": sorted(NON_STRICT_METHODS),
                "page_only_selector_method": PAGE_ONLY_SELECTOR_METHOD,
                "interp_target_attrs": sorted(INTERP_TARGET_ATTRS),
            },
            "totals": _totals(sites),
            "per_module": _per_module(sites),
            "sites": sites,
            "interpolated_selectors": interp,
        }
        out_path = Path(args.json)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="ascii")
        print(f"wrote {len(sites)} sites and {len(interp)} interpolation rows to {out_path}")
        return 0

    print_report(sites, interp)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
