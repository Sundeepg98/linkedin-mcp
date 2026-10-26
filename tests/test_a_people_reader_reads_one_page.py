"""A PEOPLE READER READS ONE PAGE: no paging parameter, no pagination helper,
and no loop that navigates past one page and its fallback.

THE RULING. The operator's NAMES-AT-RUNTIME (2026-09-24 08:11) lets a read
whose capability is people return people, and the orchestrator's
PEOPLE-DATA-MITIGATIONS (``_audit/2026-09-24-rulings-names-at-runtime.md``)
returns them under six mitigations. This file holds the fourth:

    4. BOUNDED. One page per call, no automatic pagination, and inside the
       live budget. No loop, sweep or schedule.

with the orchestrator's order for it: "A people reader returns one page and
takes no page or cursor parameter. There is no pagination helper. A planted
loop is refused."

WHAT EACH ASSERTION HOLDS

1. THE PEOPLE-TOOL SET IS DERIVED, AND HELD EQUAL TO THE DECLARED ONE.
   ``people_data.PEOPLE_TOOLS`` names the tools every rule below applies to,
   so a tool that began returning records without joining it would escape
   all of them. The derivation reads the source of every module in
   ``linkedin_server``:

   (a) a RECORD BUILDER is a module-level function whose body references
       ``Person``, ``Group`` or ``Event`` through ``people_data`` -- as an
       attribute of the module under any name it was imported as, or as a
       name imported from it. ``people_data``'s own helpers name the classes
       as their definer and are not counted: they re-validate, they read no
       page;
   (b) then a FIXED POINT: a module-level function in ANY module whose body
       references a collected function -- as an attribute, or as a bare name
       it does not bind itself -- joins;
   (c) the people tools are the ``@mcp.tool()`` functions in that set.

   REFERENCES, NOT CALLS, and that is measured rather than preferred: the one
   reader on this tree never CALLS its builder. ``linkedin_who_viewed_me`` and
   ``_profile_views_switch`` hand ``shape.parse_person_card`` to
   ``dom.parse_all`` as a value, so a call-only derivation finds NO people
   tool here (measured 2026-09-27), and a control below shows it missing a
   builder handed over that way. ANY MODULE, NOT ONLY ``server.py``: a wrapper
   around a builder in ``dom.py`` would otherwise hide the tool calling it.

   The decorator this reads is held equal to the registered tool surface
   (``mcp.list_tools()``), so a tool registered some other way cannot fall
   outside step (c) unnoticed.

2. NO PAGING PARAMETER. No people tool takes a parameter named in
   :data:`PAGING_PARAMETERS` -- read from its signature AND from the schema
   FastMCP publishes, which is what a caller actually sees. Nor does any
   function in the derived set, or any package function a people tool names
   directly, with ONE measured exception: ``page`` is this package's name for
   the browser tab. All 157 parameters called ``page`` across every definition
   in the package are annotated ``Any`` or not at all; 152 come first (after
   ``self``) and the other 5 come right after ``navigator`` (re-measured
   2026-09-27 on lane G's merge of master 2eb90ad; 147, 142 and 5 on the
   branch before it). So on a HELPER ``page`` is the tab unless it is
   annotated as a number, and on a TOOL it is always paging: a caller cannot
   hand a tool a tab. The name check stops one hop out ON PURPOSE. Further
   down the vocabulary changes meaning: ``press.check_counters(before,
   after)`` and its siblings take READINGS, and every ``before`` and
   ``after`` parameter in the package (13 and 9 after the merge; 9 and 6
   before it) is a reading taken around an
   action -- counters, an address -- never a position in a list. Iteration
   further down is assertion 4's job, which reads loops rather than names.

3. NO PAGINATION HELPER. No function defined anywhere in the package --
   module level, nested or a method -- has a name of a pagination shape:
   :data:`PAGINATION_SHAPES`, a closed list matched on whole ``_``-separated
   tokens, so ``page`` inside an ordinary name never counts. A control shows
   every listed shape matched and every ordinary name left alone, including
   all 20 definitions in the package whose names contain "page" (none
   contains "scroll"; 2026-09-27).

4. EVERY NAVIGATION A PEOPLE TOOL REACHES IS BOUNDED. Over each people tool
   and every package function it reaches by name, transitively, every loop --
   ``for``, ``async for``, ``while`` and every comprehension -- that
   NAVIGATES, directly (a ``.goto(``, ``.reload(``, ``.go_back(`` or
   ``.go_forward(`` call) or by naming a package function that navigates,
   must be a plain ``for`` over an unstepped SLICE whose upper bound is a name
   the module imports ONCE from ``linkedin_server.config``, or over
   ``enumerate()`` of one: ``urls[:MAX_NAVIGATIONS_PER_CALL]``. The value is
   read from ``config`` and must be at most 2 -- one page and its fallback
   address, not paging. A navigating function that reaches itself is refused
   too: recursion is a loop without a loop statement. And every people tool
   must navigate at all, or be declared in :data:`READS_NO_PAGE`: a reader in
   which the detector sees no navigation shows the detector blind, not the
   reader bounded.

5. A PLANTED LOOP IS REFUSED. Source built in this file -- a ``cursor``
   parameter, ``while True``, ``range(pages)``, a ``load_more`` helper, and
   the holes past those four -- is convicted by :func:`audit`, the one
   function every real-tree assertion above reads too. The REAL
   ``linkedin_who_viewed_me``, audited from its own syntax tree, passes; the
   same tree with its slice removed, its bound raised or its ``for`` turned
   into a ``while`` is refused; and a plant dropped into the real package is
   found, with nothing else found beside it.

LIMITS, stated plainly.

* It reads NAMES and LOOP SHAPES, not behaviour. Resolution is by name: a
  builder, a helper or a navigation reached through a module-level import
  alias (``... import parse_person_card as parse_viewer`` at the top of a
  module), a variable, ``getattr``, a table of callables,
  ``functools.partial`` or a method of an object is invisible -- to a NEW
  reader silently; a DECLARED reader that moves behind one stops deriving and
  fails assertion 1 loudly. An aliased import made inside a function is
  followed. A name collision errs the other way: a set grows and a test fails
  loudly.
* A record built by another route -- ``people_data.as_record`` over a dict,
  or a dict shaped like an envelope -- makes no builder. (Three routes that
  still name a record class were added on lane G's cold verification,
  2026-09-27: another module's ``people_data`` attribute, ``RECORD_TYPES``
  and ``getattr(people_data, "Person")``.) A tool that returns such records
  and is driven by the tool-envelope guard is refused there unless it is in
  ``PEOPLE_TOOLS``; one that is not driven is invisible to both.
* A page fetched without a navigation verb is invisible to assertion 4: an
  API request, a ``fetch`` inside ``evaluate``, pressing a "next" control, a
  scroll. Those are held elsewhere: the mutation scanner in ``readonly.py``,
  where scrolling is not sanctioned (``SCROLL-NOT-SANCTIONED``), and the
  press gates.
* Iteration without a loop node -- ``map``, ``asyncio.gather`` over a list
  built elsewhere, a scheduler -- is invisible, and so is recursion through
  an alias. A slice is trusted to bound: an object whose ``__getitem__``
  ignores the slice is not caught.
* The pagination-name list is closed. A helper named outside it, or bound by
  assignment rather than ``def``, passes.
* THE LIVE BUDGET ITSELF IS HELD ELSEWHERE. ``LIVE-BUDGET-40-LOADS``
  (``_audit/RULINGS.md``) is enforced by the live lane's harness,
  ``scripts/_probe_live_lane_session_1.py``, whose ledger wraps
  ``BROWSER.goto`` and refuses the 41st load before navigating (held offline
  by ``tests/test_live_lane_session_harness.py``). Spacing inside one process
  is ``config.MIN_NAVIGATION_INTERVAL_S``, taken by ``BROWSER.goto``'s rate
  slot in ``browser.py``. The per-call ceiling is
  ``config.MAX_NAVIGATIONS_PER_CALL``, which assertion 4 reads. "No loop,
  sweep or schedule" for WRITES is ``writes.PERMANENTLY_FORBIDDEN``.
"""

from __future__ import annotations

import ast
import asyncio
import copy
import functools
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, FrozenSet, Iterable, Iterator, List
from typing import Mapping, Optional, Set, Tuple

import pytest

from linkedin_server import config, people_data

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "linkedin_server"

# ---------------------------------------------------------------------------
# The vocabulary, closed
# ---------------------------------------------------------------------------

#: The record classes. A function whose body references one through
#: ``people_data`` builds records. Held equal to ``people_data.RECORD_TYPES``
#: by :func:`test_every_record_type_is_a_record_class_here`.
#: ``Organisation`` joined 2026-10-10 (lane G2): a followed Page's name.
#: ``OrganisationProse`` joined 2026-10-10 (lane B4, census row ``J 110``): an
#: organisation Page's prose is third-party text returned at runtime, so the
#: tool that builds one is a people reader and every rule here binds it.
RECORD_CLASSES = frozenset(
    {"Person", "Group", "Event", "Post", "Organisation", "OrganisationProse"}
)


def test_every_record_type_is_a_record_class_here():
    """A RECORD TYPE THIS GUARD CANNOT NAME IS A READER IT CANNOT SEE
    (2026-10-10, lane G2, when ``people_data.Post`` was declared). The closure
    finds record readers by these names, so a type added to the module and not
    here would let a reader build it with no bound on how many pages it
    reads."""
    declared = {record.__name__ for record in people_data.RECORD_TYPES}
    assert set(RECORD_CLASSES) == declared, sorted(declared ^ set(RECORD_CLASSES))

#: A parameter by one of these names asks for a page, an offset or a cursor.
#: Closed and exact: ``pages_loaded`` or ``max_items`` is not one.
PAGING_PARAMETERS = frozenset({
    "page", "pages", "page_no", "page_number", "cursor", "offset", "start",
    "after", "before", "next", "next_page", "page_token", "continuation",
    "more", "load_more", "scroll", "all", "all_pages", "max_pages",
})

#: THE SHAPES OF A PAGINATION HELPER'S NAME, closed. Each is matched against
#: whole ``_``-separated tokens (camelCase is split first), so ``page`` inside
#: an ordinary name -- ``read_page_views``, ``_landing_page``,
#: ``harvest_followed_pages`` -- never counts. DELIBERATELY ABSENT:
#: ``show_more``, ``see_more`` and ``read_more``, which on LinkedIn reveal
#: more of the page already loaded (``show_more_analytics`` is exactly that
#: here); ``parse_all``, which parses a list it was handed; and a bare
#: ``<verb>_pages``, because LinkedIn calls a company's presence a "Page" and
#: ``harvest_followed_pages`` reads his followed ones.
PAGINATION_SHAPES: Tuple[str, ...] = (
    r"paginat[a-z0-9]*",                                    # paginate, pagination
    r"(?:next|prev|previous)_pages?",                       # next_page
    r"(?:load|fetch|get)_more",                             # load_more
    r"more_pages",                                          # has_more_pages
    r"(?:fetch|load|get|harvest|collect|gather|crawl|sweep)_all",  # fetch_all
    r"(?:all|every|each)_pages?",                           # all_pages, for_each_page
    r"(?:iterate|iter|walk|crawl|sweep|loop|visit)_pages",  # iterate_pages
    r"pages?_through",                                      # page_through
    r"scroll_(?:to_)?(?:end|bottom)",                       # scroll_to_end
    r"scroll_(?:until|more|down|all|through)",              # scroll_until
    r"(?:infinite|auto)_?scroll[a-z0-9]*",                  # infinite_scroll
    r"(?:next|page)_cursor",                                # next_cursor
)

#: A call to one of these, on any receiver, loads a page. ``BROWSER.goto`` is
#: the package's one door (``browser.py`` holds the only raw ``page.goto``);
#: the other three are here so a reload loop cannot pass for a read.
NAVIGATION_VERBS = frozenset({"goto", "reload", "go_back", "go_forward"})

#: The most one call may load: the reader's address and its one fallback.
ONE_PAGE_AND_ITS_FALLBACK = 2

#: PEOPLE TOOLS THAT LOAD NO PAGE THROUGH A NAVIGATION VERB, each with its
#: reason. Empty: every people tool today navigates where the detector can see
#: it. An entry is a claim a human makes, and a stale one fails.
READS_NO_PAGE: Dict[str, str] = {}

#: WHERE THE DERIVATION STOPS: THE WRITE DOOR (2026-09-27,
#: PREVIEW-NAMES-THE-RESOLVED-TARGET). A write's preview names whom the tool
#: resolved inside a people record -- the ruling's identity check -- and the
#: derivation reaches those builders by NAME, through ``writes.preview`` and
#: then ``server._write_tool``, the one door every write tool calls
#: (``tests/test_no_write_is_aimed_by_a_name.py`` holds that it is the only
#: caller of the write path). Crossing it would declare every write tool a
#: people READER and hold the write path to reader rules it was never under.
#: A write returns one record, in one preview, of the one member it resolved,
#: under the write gate's own rules: a single-use grant, and the target the
#: caller named. So the reader derivation stops at the door, and the builders
#: only the door reaches are declared below and held equal to what is found
#: behind it -- a new one fails until somebody decides which side it is on.
WRITE_DOOR: "Key" = ("server", "_write_tool")

#: The record builders the write door reaches: the builders of the previews
#: that name a third party.
#:
#: MASTER'S SET, AND THIS LANE'S, MET AT LANE L5'S MERGE OF MASTER b6993e5
#: (2026-09-27), and the set below is what the derivation MEASURED on the
#: merged tree, not a union typed by hand:
#:
#: * ``("people_seam", "person")`` -- the named-person previews
#:   (``named_profile.name_the_profile_target``) and, since lane L5's merge of
#:   master 52b55b6, the invitation's (``writes._name_the_invitation_recipient``
#:   calls it and builds nothing, which is why that function left this set);
#: * ``("threads", "name_the_reply_recipient")`` -- the reply preview builds its
#:   person record itself (lane G's, on master; it went through the seam on
#:   this lane's branch from the 52b55b6 merge until this one);
#: * ``("threads", "conversation_with")`` -- the builder the reply preview
#:   shares with ``linkedin_list_conversations`` for a GROUP conversation's
#:   title record (2026-09-27). That one is ALSO a reader's builder, reached
#:   through ``threads.list_result``, and the stop does not hide it from that
#:   path: the list tool is still derived a people reader
#:   (``test_the_write_door_stops_only_itself`` holds the stop to itself).
#: * ``("writes", "_read_followed_state")`` -- the unfollow's preview and its
#:   verification read the Manage Pages row, and since 2026-10-10 (lane G2,
#:   on the orchestrator's ruling) the followed Page's name leaves that read
#:   only as an organisation record. Measured behind the door and only
#:   there: the unfollow is a write tool, so no read tool is derived through
#:   it.
PREVIEW_BUILDERS: FrozenSet["Key"] = frozenset(
    {
        ("people_seam", "person"),
        ("threads", "name_the_reply_recipient"),
        ("threads", "conversation_with"),
        ("writes", "_read_followed_state"),
    }
)

# ---------------------------------------------------------------------------
# The instruments -- one set, read by the real-tree assertions AND the plants
# ---------------------------------------------------------------------------

#: A module-level function of the package, as ``(module, name)``.
Key = Tuple[str, str]

_FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
_COMPREHENSIONS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_LOOPS = (ast.For, ast.AsyncFor, ast.While) + _COMPREHENSIONS
_RECORD_MODULE = ("linkedin_server.people_data", ".people_data")
_RECORD_PACKAGE = ("linkedin_server", ".")
_CONFIG_MODULE = ("linkedin_server.config", ".config")


def parse_sources(sources: Mapping[str, str]) -> Dict[str, ast.Module]:
    """Modules by name, parsed. Never imported and never run."""
    return {name: ast.parse(text, filename=name + ".py") for name, text in sources.items()}


@functools.lru_cache(maxsize=1)
def package_modules() -> Dict[str, ast.Module]:
    """Every module of ``linkedin_server``, read from disk once per run.

    Shared: a caller that adds a module copies the dict first."""
    return parse_sources({
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE.glob("*.py"))
    })


def _dotted(node: ast.AST) -> Optional[str]:
    """``a.b.c`` for a chain of attributes on a bare name, else None."""
    parts: List[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def _imported_from(node: ast.ImportFrom) -> str:
    return "." * node.level + (node.module or "")


def _body(function: ast.AST) -> Iterator[ast.AST]:
    """Every node under a function's BODY, nested functions included -- never
    its signature: an annotation that names a record builds nothing."""
    for statement in function.body:
        yield from ast.walk(statement)


def module_functions(modules: Mapping[str, ast.Module]) -> Dict[Key, ast.AST]:
    return {
        (module, node.name): node
        for module, tree in modules.items()
        for node in tree.body
        if isinstance(node, _FUNCTIONS)
    }


def definitions(modules: Mapping[str, ast.Module]) -> Iterator[Tuple[str, ast.AST]]:
    """Every function DEFINED anywhere: module level, nested, or a method."""
    for module, tree in modules.items():
        for node in ast.walk(tree):
            if isinstance(node, _FUNCTIONS):
                yield module, node


def _parameters(function: ast.AST) -> List[ast.arg]:
    spec = function.args
    extra = [arg for arg in (spec.vararg, spec.kwarg) if arg is not None]
    return [*spec.posonlyargs, *spec.args, *spec.kwonlyargs, *extra]


def _local_names(function: ast.AST) -> FrozenSet[str]:
    """Every name a function binds to a value of its own: its parameters, and
    every name assigned or defined anywhere inside it.

    NOT A NAME IT IMPORTS. ``from linkedin_server.shape import
    parse_person_card`` inside a tool binds a local that IS the package's
    function, and this codebase imports inside functions routinely."""
    names: Set[str] = set()
    for node in ast.walk(function):
        if isinstance(node, _FUNCTIONS + (ast.Lambda,)):
            names.update(arg.arg for arg in _parameters(node))
        if node is not function and isinstance(node, _FUNCTIONS + (ast.ClassDef,)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            names.add(node.id)
    return frozenset(names)


def _imported_symbols(function: ast.AST) -> Set[str]:
    """What a function imports FROM a package module, by its own name, however
    it is aliased: ``from linkedin_server.shape import parse_person_card as
    parse`` names ``parse_person_card``. A package MODULE imported by name
    (``from linkedin_server import reveal``) is not a function and is left out:
    read as one, it would be ``reveal.reveal``."""
    found: Set[str] = set()
    for node in _body(function):
        if isinstance(node, ast.ImportFrom):
            source = _imported_from(node)
            if source.startswith("linkedin_server.") or (source.startswith(".") and source != "."):
                found.update(alias.name for alias in node.names if alias.name != "*")
    return found


def _loaded(nodes: Iterable[ast.AST], local: FrozenSet[str] = frozenset()) -> Set[str]:
    """Attribute names loaded, and bare names loaded that are not ``local``.

    A bare name the function binds for itself is ITS OWN, not the package's:
    ``linkedin_who_viewed_me`` loads its parameter ``view_switch``, and read
    as a package name that is ``view_switch.view_switch`` -- a function the
    reader never touches (measured 2026-09-27, before this rule)."""
    found: Set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
            if node.id not in local:
                found.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
            found.add(node.attr)
    return found


def references(function: ast.AST) -> FrozenSet[str]:
    """The names a function's body LOADS -- as an attribute, or as a bare name
    it does not bind itself -- and the package functions it imports.

    A builder handed to a mapper as a value --
    ``dom.parse_all(records, shape.parse_person_card)`` -- is a reference and
    not a call, and it is how the one reader on this tree reaches its builder.
    """
    found = _loaded(_body(function), _local_names(function))
    return frozenset(found | _imported_symbols(function))


def calls(function: ast.AST) -> FrozenSet[str]:
    """The names a function's body CALLS, by the same scoping and with the same
    imports. The narrower edge, kept only for the control that shows what it
    misses."""
    local = _local_names(function)
    found: Set[str] = set(_imported_symbols(function))
    for node in _body(function):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id not in local:
                found.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                found.add(node.func.attr)
    return frozenset(found)


def closure(
    edges: Mapping[Key, FrozenSet[str]],
    seed: Iterable[Key],
    stop: FrozenSet[Key] = frozenset(),
) -> FrozenSet[Key]:
    """The seed, then every function whose edge names a collected function, to
    a fixed point. By NAME: which module the name lives in is not asked. A key
    in ``stop`` never joins, so nothing reaches past it through it."""
    collected = set(seed)
    while True:
        names = {name for _module, name in collected}
        grown = {
            key
            for key, named in edges.items()
            if key not in collected and key not in stop and named & names
        }
        if not grown:
            return frozenset(collected)
        collected |= grown


def record_aliases(tree: ast.Module) -> Tuple[FrozenSet[str], FrozenSet[str]]:
    """``(module names, class names)`` by which one module reaches the records.

    Every import in the module counts, a function-local one included:
    ``import linkedin_server.people_data [as pd]``,
    ``from linkedin_server import people_data [as pd]``, and
    ``from linkedin_server.people_data import Person [as Viewer]`` or ``*``.
    """
    via_module: Set[str] = set()
    via_class: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == _RECORD_MODULE[0]:
                    via_module.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            source = _imported_from(node)
            for alias in node.names:
                if source in _RECORD_PACKAGE and alias.name == "people_data":
                    via_module.add(alias.asname or alias.name)
                elif source in _RECORD_MODULE and alias.name == "*":
                    via_class |= RECORD_CLASSES
                elif source in _RECORD_MODULE and alias.name in RECORD_REFERENCES:
                    via_class.add(alias.asname or alias.name)
    return frozenset(via_module), frozenset(via_class)


#: What else names a record class through ``people_data``: the tuple of them.
#: Added 2026-09-27 with the two routes below, on lane G's cold verification.
RECORD_REFERENCES = RECORD_CLASSES | {"RECORD_TYPES"}


def _names_people_data(node: Optional[ast.AST], via_module: FrozenSet[str]) -> bool:
    """Is ``node`` the ``people_data`` module -- under an alias this module
    imported, or reached as an attribute of another module
    (``shape.people_data``)?"""
    dotted = _dotted(node) if node is not None else None
    if dotted is None:
        return False
    return dotted in via_module or dotted.rsplit(".", 1)[-1] == "people_data"


def record_builders(modules: Mapping[str, ast.Module]) -> FrozenSet[Key]:
    """Step (a): module-level functions whose body references a record class
    through ``people_data`` -- by attribute, under any import alias or through
    another module's ``people_data`` attribute; by a name imported from it;
    through ``RECORD_TYPES``; or by ``getattr(people_data, "Person")``."""
    found: Set[Key] = set()
    for module, tree in modules.items():
        via_module, via_class = record_aliases(tree)
        for node in tree.body:
            if not isinstance(node, _FUNCTIONS):
                continue
            for sub in _body(node):
                through_module = (
                    isinstance(sub, ast.Attribute)
                    and sub.attr in RECORD_REFERENCES
                    and _names_people_data(sub.value, via_module)
                )
                by_name = (
                    isinstance(sub, ast.Name)
                    and isinstance(sub.ctx, ast.Load)
                    and sub.id in via_class
                )
                by_getattr = (
                    isinstance(sub, ast.Call)
                    and _dotted(sub.func) == "getattr"
                    and len(sub.args) >= 2
                    and _names_people_data(sub.args[0], via_module)
                    and isinstance(sub.args[1], ast.Constant)
                    and sub.args[1].value in RECORD_REFERENCES
                )
                if through_module or by_name or by_getattr:
                    found.add((module, node.name))
                    break
    return frozenset(found)


def is_tool(function: ast.AST) -> bool:
    """``@mcp.tool()`` or ``@mcp.tool``: the decorator the surface registers by."""
    for decorator in function.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        if _dotted(target) == "mcp.tool":
            return True
    return False


_A_NUMBER = re.compile(r"\b(?:int|float)\b")


def paging_parameters(function: ast.AST) -> List[str]:
    """The function's parameters named in :data:`PAGING_PARAMETERS`.

    ``page`` on a HELPER is the browser tab -- this package's name for it at
    every one of its 157 uses (the module docstring) -- unless it is
    annotated as a number. On a TOOL
    it is always paging: a caller cannot hand a tool a tab.
    """
    tool = is_tool(function)
    found: List[str] = []
    for arg in _parameters(function):
        if arg.arg not in PAGING_PARAMETERS:
            continue
        numbered = arg.annotation is not None and bool(
            _A_NUMBER.search(ast.unparse(arg.annotation))
        )
        if arg.arg == "page" and not tool and not numbered:
            continue
        found.append(arg.arg)
    return found


_PAGINATION = re.compile("_(?:" + "|".join(PAGINATION_SHAPES) + ")_")
_CAMEL_HUMP = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def is_pagination_name(name: str) -> bool:
    """True when ``name``, split into ``_`` tokens, holds a pagination shape."""
    tokens = re.sub("_+", "_", _CAMEL_HUMP.sub("_", name)).strip("_").lower()
    return bool(_PAGINATION.search("_" + tokens + "_"))


def pagination_helpers(modules: Mapping[str, ast.Module]) -> List[str]:
    return sorted(
        module + "." + node.name
        for module, node in definitions(modules)
        if is_pagination_name(node.name)
    )


def _navigation_verbs(nodes: Iterable[ast.AST]) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in NAVIGATION_VERBS
        for node in nodes
    )


def _route(loop: ast.AST, navigating: FrozenSet[str], local: FrozenSet[str]) -> Optional[str]:
    """How a loop navigates -- ``"directly"`` or ``"through <names>"`` -- or None."""
    inner = list(ast.walk(loop))
    if _navigation_verbs(inner):
        return "directly"
    through = sorted(_loaded(inner, local) & navigating)
    return "through " + ", ".join(through) if through else None


def _module_scope(tree: ast.Module) -> Iterator[ast.AST]:
    """Every node at module scope. The walk never enters a def, class or lambda."""
    pending: List[ast.AST] = list(tree.body)
    while pending:
        node = pending.pop()
        yield node
        if not isinstance(node, _FUNCTIONS + (ast.ClassDef, ast.Lambda)):
            pending.extend(ast.iter_child_nodes(node))


def config_ceilings(tree: ast.Module) -> Dict[str, Tuple[str, Any]]:
    """The names a module imports ONCE from ``linkedin_server.config``, each
    mapped to ``(its name in config, config's value)``.

    ONCE: a name bound again anywhere at module scope, or declared ``global``
    or ``nonlocal`` in any function, could hold something else by the time a
    loop reads it, so it is no ceiling. The value is config's own, read here,
    never the source text's.
    """
    bound: Counter = Counter()
    for node in _module_scope(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound[node.id] += 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound[alias.asname or alias.name.split(".")[0]] += 1
        elif isinstance(node, _FUNCTIONS + (ast.ClassDef,)):
            bound[node.name] += 1
    rebindable = {
        name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Global, ast.Nonlocal))
        for name in node.names
    }
    ceilings: Dict[str, Tuple[str, Any]] = {}
    for node in tree.body:
        if not (isinstance(node, ast.ImportFrom) and _imported_from(node) in _CONFIG_MODULE):
            continue
        for alias in node.names:
            name = alias.asname or alias.name
            if bound[name] == 1 and name not in rebindable and hasattr(config, alias.name):
                ceilings[name] = (alias.name, getattr(config, alias.name))
    return ceilings


def _head(loop: ast.AST) -> str:
    if isinstance(loop, ast.While):
        text = "while " + ast.unparse(loop.test)
    elif isinstance(loop, (ast.For, ast.AsyncFor)):
        prefix = "async for " if isinstance(loop, ast.AsyncFor) else "for "
        text = prefix + ast.unparse(loop.target) + " in " + ast.unparse(loop.iter)
    else:
        text = ast.unparse(loop)
    return text if len(text) <= 100 else text[:97] + "..."


def loop_verdict(
    loop: ast.AST,
    route: str,
    ceilings: Mapping[str, Tuple[str, Any]],
    local: FrozenSet[str],
) -> Tuple[Optional[str], Optional[str], Any]:
    """``(refusal, bound, value)`` for one loop that navigates; no refusal admits it.

    THE ONE ADMITTED SHAPE is the real reader's: a plain ``for`` over an
    unstepped slice whose upper bound is a name its module imports once from
    ``linkedin_server.config``, holding 1 or 2 -- or over ``enumerate()`` of
    such a slice.
    """
    shown = "`" + _head(loop) + "` navigates (" + route + ")"
    if isinstance(loop, ast.While):
        return "a while loop " + shown, None, None
    if isinstance(loop, ast.AsyncFor):
        return "an async for " + shown, None, None
    if not isinstance(loop, ast.For):
        return "a comprehension " + shown, None, None
    iterable = loop.iter
    if (
        isinstance(iterable, ast.Call)
        and _dotted(iterable.func) == "enumerate"
        and iterable.args
    ):
        iterable = iterable.args[0]
    if not (isinstance(iterable, ast.Subscript) and isinstance(iterable.slice, ast.Slice)):
        return "a for " + shown + ", and what it iterates is not a slice", None, None
    piece = iterable.slice
    if piece.step is not None:
        return "a for " + shown + " over a stepped slice", None, None
    if not isinstance(piece.upper, ast.Name):
        what = "nothing" if piece.upper is None else "`" + ast.unparse(piece.upper) + "`"
        return "a for " + shown + ", and its slice is bounded by " + what + ", not a name", None, None
    name = piece.upper.id
    if name in local:
        return (
            "a for " + shown + ", bounded by `" + name + "`, a parameter or local "
            "of its function", name, None,
        )
    if name not in ceilings:
        return (
            "a for " + shown + ", bounded by `" + name + "`, which is not a name its "
            "module imports once from linkedin_server.config", name, None,
        )
    config_name, value = ceilings[name]
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= ONE_PAGE_AND_ITS_FALLBACK
    ):
        return (
            "a for " + shown + ", bounded by config." + config_name + " = " + repr(value)
            + "; one page and its fallback is at most " + str(ONE_PAGE_AND_ITS_FALLBACK),
            config_name, value,
        )
    return None, config_name, value


@dataclass(frozen=True)
class NavigatingLoop:
    """One loop that navigates, inside the reach of one people tool."""

    reader: str
    function: str
    line: int
    head: str
    bound: Optional[str]
    value: Any
    refusal: Optional[str]


@dataclass(frozen=True)
class Audit:
    """Everything this file asks of one set of modules."""

    builders: FrozenSet[Key]
    derived: FrozenSet[Key]
    tools: FrozenSet[str]
    paging_scope: FrozenSet[str]
    paging: Dict[str, List[str]]
    helpers: List[str]
    loops: List[NavigatingLoop]
    recursions: List[str]
    silent: List[str]

    @property
    def refused(self) -> List[str]:
        return [
            loop.function + ", line " + str(loop.line) + ": " + loop.refusal
            for loop in self.loops
            if loop.refusal
        ]

    def findings(self) -> Dict[str, List[str]]:
        """Everything this audit convicts, by the rule that convicts it."""
        return {
            "paging": [
                where + ": " + ", ".join(names) for where, names in sorted(self.paging.items())
            ],
            "helpers": list(self.helpers),
            "loops": self.refused,
            "recursions": list(self.recursions),
            "silent": list(self.silent),
        }


def audit(modules: Mapping[str, ast.Module]) -> Audit:
    """The whole rule, over a set of modules: the real package or a plant."""
    functions = module_functions(modules)
    edges = {key: references(function) for key, function in functions.items()}
    by_name: Dict[str, List[Key]] = {}
    for key in functions:
        by_name.setdefault(key[1], []).append(key)

    def named_by(key: Key) -> List[Key]:
        return [other for name in edges[key] for other in by_name.get(name, ())]

    def reach(start: Iterable[Key]) -> Set[Key]:
        seen: Set[Key] = set()
        pending = list(start)
        while pending:
            key = pending.pop()
            if key not in seen:
                seen.add(key)
                pending.extend(named_by(key))
        return seen

    # 1. Builders, the fixed point -- stopped at the write door -- and the
    #    tools in it.
    builders = record_builders(modules)
    derived = closure(edges, builders, stop=frozenset({WRITE_DOOR}))
    readers = sorted(key for key in derived if is_tool(functions[key]))

    # 2. Paging parameters: every reader, the derived set, and what a reader
    #    names directly -- one hop, on purpose (see the module docstring).
    scope: Set[Key] = set(derived)
    for reader in readers:
        scope.update(named_by(reader))
    paging: Dict[str, List[str]] = {}
    for key in sorted(scope):
        found = paging_parameters(functions[key])
        if found:
            paging[".".join(key)] = found

    # 4. Every navigating loop in each reader's reach, and recursion.
    navigating = closure(
        edges,
        [key for key, function in functions.items() if _navigation_verbs(_body(function))],
    )
    navigating_names = frozenset(name for _module, name in navigating)
    ceilings = {module: config_ceilings(tree) for module, tree in modules.items()}
    loops: List[NavigatingLoop] = []
    recursions: List[str] = []
    silent: List[str] = []
    for reader in readers:
        if reader not in navigating:
            silent.append(reader[1])
        for key in sorted(reach([reader])):
            function = functions[key]
            local = _local_names(function)
            for node in _body(function):
                if not isinstance(node, _LOOPS):
                    continue
                route = _route(node, navigating_names, local)
                if route is None:
                    continue
                refusal, bound, value = loop_verdict(node, route, ceilings[key[0]], local)
                loops.append(NavigatingLoop(
                    reader[1], ".".join(key), node.lineno, _head(node), bound, value, refusal,
                ))
            if key in navigating and key in reach(named_by(key)):
                recursions.append(
                    ".".join(key) + " navigates and reaches itself by name -- a loop "
                    "with no loop statement (in the reach of " + reader[1] + ")"
                )
    return Audit(
        builders=builders,
        derived=derived,
        tools=frozenset(name for _module, name in readers),
        paging_scope=frozenset(".".join(key) for key in scope),
        paging=paging,
        helpers=pagination_helpers(modules),
        loops=loops,
        recursions=recursions,
        silent=silent,
    )


@functools.lru_cache(maxsize=1)
def real_audit() -> Audit:
    return audit(package_modules())


@functools.lru_cache(maxsize=1)
def registered_tools() -> Dict[str, Any]:
    """The tool surface as FastMCP registered it, by name."""
    from linkedin_server import server

    return {tool.name: tool for tool in asyncio.run(server.mcp.list_tools())}


# ---------------------------------------------------------------------------
# 1. The people-tool set is derived and held equal to the declared one
# ---------------------------------------------------------------------------


def test_the_derivation_finds_a_builder_and_a_reader():
    """A derivation that finds nothing equals an empty declaration forever."""
    found = real_audit()
    assert found.builders, (
        "no function in linkedin_server references Person, Group or Event through "
        "people_data. Either the records stopped being built, or the import this "
        "reads changed shape -- and then every rule below is vacuous."
    )
    assert found.tools, "builders %s reach no @mcp.tool()" % sorted(found.builders)


def test_the_derived_people_tools_are_the_declared_ones():
    found = real_audit()
    assert found.tools == people_data.PEOPLE_TOOLS, (
        "derived people tools %s; declared people_data.PEOPLE_TOOLS %s. Derived "
        "through the builders %s and the set %s. A tool whose code builds a people "
        "record IS a people reader: declare it in PEOPLE_TOOLS in the same change, "
        "and one page, no cursor and no pagination helper apply to it from then on. "
        "A declared tool this cannot derive has stopped building records -- or "
        "builds them through an alias this file cannot follow, a limit its "
        "docstring names."
        % (
            sorted(found.tools),
            sorted(people_data.PEOPLE_TOOLS),
            sorted(found.builders),
            sorted(found.derived),
        )
    )


def test_the_decorator_the_derivation_reads_is_the_registered_surface():
    """Step (c) reads ``@mcp.tool()`` off the syntax tree; FastMCP registers by
    running it. If the two ever disagree, a tool can be a reader without
    being seen as one."""
    decorated = sorted(
        name
        for (_module, name), function in module_functions(package_modules()).items()
        if is_tool(function)
    )
    registered = sorted(registered_tools())
    assert decorated == registered, (
        "decorated but not registered: %s; registered but not decorated: %s"
        % (sorted(set(decorated) - set(registered)), sorted(set(registered) - set(decorated)))
    )


# ---------------------------------------------------------------------------
# 2. No paging parameter
# ---------------------------------------------------------------------------


def test_no_people_tool_nor_a_function_it_names_takes_a_paging_parameter():
    found = real_audit()
    readers_examined = {label.rsplit(".", 1)[-1] for label in found.paging_scope}
    assert found.tools <= readers_examined, "the scope did not include the readers themselves"
    assert found.paging == {}, (
        "paging parameters %s, over a scope of %d functions. A people reader "
        "returns ONE page and takes no page, offset or cursor: paging people is "
        "the loop PEOPLE-DATA-MITIGATIONS 4 refuses, however deliberate each call."
        % (found.paging, len(found.paging_scope))
    )


@pytest.mark.parametrize("tool", sorted(people_data.PEOPLE_TOOLS))
def test_the_schema_a_people_tool_publishes_asks_for_no_page(tool):
    """The signature is what the code says; the schema is what a CALLER sees."""
    registered = registered_tools()
    assert tool in registered, "%s is declared a people tool and is not registered" % tool
    schema = registered[tool].parameters
    assert isinstance(schema, dict) and isinstance(schema.get("properties"), dict), (
        "%s publishes no parameter schema this can read: %r" % (tool, schema)
    )
    asked = sorted(set(schema["properties"]) & PAGING_PARAMETERS)
    assert asked == [], "%s publishes paging parameters %s" % (tool, asked)


# ---------------------------------------------------------------------------
# 3. No pagination helper
# ---------------------------------------------------------------------------


def test_no_pagination_helper_is_defined_anywhere_in_the_package():
    names = [node.name for _module, node in definitions(package_modules())]
    assert any("page" in name.lower() for name in names), (
        "the walk saw no definition whose name mentions a page -- it is not "
        "reading the package, and a clean result from it means nothing"
    )
    helpers = real_audit().helpers
    assert helpers == [], (
        "pagination-shaped definitions %s. A people reader reads one page; a "
        "helper that fetches the next one is the thing the ruling refuses, "
        "whoever calls it today." % helpers
    )


# ---------------------------------------------------------------------------
# 4. Every navigation a people tool reaches is bounded
# ---------------------------------------------------------------------------


def test_every_people_tool_navigates_where_the_detector_can_see_it():
    found = real_audit()
    unexplained = sorted(set(found.silent) - set(READS_NO_PAGE))
    assert unexplained == [], (
        "people tools %s show the detector no navigation at all. A reader reads "
        "a page, so either it fetches one by a route this file cannot see -- an "
        "API request, a fetch inside evaluate -- and the loop rule cannot vouch "
        "for it, or it genuinely loads none: then declare it in READS_NO_PAGE "
        "with the reason." % unexplained
    )
    stale = sorted(set(READS_NO_PAGE) - set(found.silent))
    assert stale == [], "READS_NO_PAGE names %s, which navigate or read no people" % stale


def test_every_navigating_loop_a_people_tool_reaches_is_bounded():
    found = real_audit()
    assert found.refused == [], (
        "navigating loops refused: %s. The one admitted shape is a for over an "
        "unstepped slice bounded by a ceiling imported from linkedin_server.config "
        "-- for attempt, url in enumerate(urls[:MAX_NAVIGATIONS_PER_CALL], start=1)."
        % found.refused
    )
    assert found.recursions == [], found.recursions


def test_the_bound_is_a_config_ceiling_of_at_most_two():
    ceiling = config.MAX_NAVIGATIONS_PER_CALL
    assert isinstance(ceiling, int) and 1 <= ceiling <= ONE_PAGE_AND_ITS_FALLBACK, (
        "config.MAX_NAVIGATIONS_PER_CALL = %r. A people reader's loop is bounded "
        "by it, and above 2 it is paging rather than one page and its fallback."
        % (ceiling,)
    )
    for loop in real_audit().loops:
        if loop.refusal is not None:
            continue
        value = getattr(config, loop.bound, None)
        assert value == loop.value and 1 <= value <= ONE_PAGE_AND_ITS_FALLBACK, (
            "%s line %d is bounded by config.%s = %r" % (loop.function, loop.line, loop.bound, value)
        )


# ---------------------------------------------------------------------------
# 5. Controls: the real reader, audited alone and changed by one node
# ---------------------------------------------------------------------------

_READER = "linkedin_who_viewed_me"

_READER_HEADER = "from linkedin_server.config import MAX_LIMIT, MAX_NAVIGATIONS_PER_CALL\n"

#: The real reader names its builder as ``shape.parse_person_card``; this is
#: a builder of that name, and nothing else.
_BUILDER_BESIDE_THE_READER = '''\
from linkedin_server import people_data


def parse_person_card(record):
    return people_data.Person.from_page(name=record.get("text"))
'''


def _the_real_reader() -> ast.AST:
    """A private copy of the real reader's syntax tree, decorator included."""
    for node in package_modules()["server"].body:
        if isinstance(node, _FUNCTIONS) and node.name == _READER:
            return copy.deepcopy(node)
    pytest.fail(
        "%s is no longer defined in server.py; re-aim these controls at the "
        "reader that replaced it" % _READER
    )


def _its_navigating_for(function: ast.AST) -> ast.For:
    found = [
        node for node in _body(function)
        if isinstance(node, ast.For) and _navigation_verbs(ast.walk(node))
    ]
    if len(found) != 1:
        pytest.fail(
            "%s holds %d navigating for loops, not the one these mutations change; "
            "re-aim them" % (_READER, len(found))
        )
    return found[0]


class _DropSlices(ast.NodeTransformer):
    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        self.generic_visit(node)
        return node.value if isinstance(node.slice, ast.Slice) else node


def _slice_removed(reader: ast.AST) -> None:
    loop = _its_navigating_for(reader)
    loop.iter = _DropSlices().visit(loop.iter)


def _bound_raised(reader: ast.AST) -> None:
    loop = _its_navigating_for(reader)
    for node in ast.walk(loop.iter):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice):
            node.slice.upper = ast.Name(id="MAX_LIMIT", ctx=ast.Load())


def _for_made_while(reader: ast.AST) -> None:
    loop = _its_navigating_for(reader)
    replacement = ast.copy_location(
        ast.While(test=ast.Constant(value=True), body=loop.body, orelse=[]), loop
    )
    for parent in ast.walk(reader):
        for _field, value in ast.iter_fields(parent):
            if isinstance(value, list):
                for index, item in enumerate(value):
                    if item is loop:
                        value[index] = replacement
                        return
    pytest.fail("the navigating for has no statement list to be replaced in")


def _reader_alone(mutate: Optional[Callable[[ast.AST], None]] = None) -> Audit:
    reader = _the_real_reader()
    if mutate is not None:
        mutate(reader)
    module = ast.parse(_READER_HEADER)
    module.body.append(reader)
    ast.fix_missing_locations(module)
    return audit({"server": module, "shape": ast.parse(_BUILDER_BESIDE_THE_READER)})


def test_the_real_reader_audited_alone_passes():
    found = _reader_alone()
    assert found.tools == {_READER}
    assert found.findings() == {
        "paging": [], "helpers": [], "loops": [], "recursions": [], "silent": [],
    }, found.findings()
    admitted = [(loop.bound, loop.value) for loop in found.loops]
    assert admitted == [("MAX_NAVIGATIONS_PER_CALL", config.MAX_NAVIGATIONS_PER_CALL)], (
        "the real reader should hold exactly one navigating loop, bounded by the "
        "config ceiling; found %s" % [(loop.head, loop.bound) for loop in found.loops]
    )


#: One node of the real reader changed, and the phrase its refusal must carry.
_MUTATIONS: Dict[str, Tuple[Callable[[ast.AST], None], str]] = {
    "slice-removed": (_slice_removed, "what it iterates is not a slice"),
    "bound-raised-to-MAX_LIMIT": (_bound_raised, "bounded by config.MAX_LIMIT"),
    "for-made-while": (_for_made_while, "a while loop"),
}


@pytest.mark.parametrize("mutation", sorted(_MUTATIONS))
def test_the_real_reader_changed_by_one_node_is_refused(mutation):
    mutate, phrase = _MUTATIONS[mutation]
    found = _reader_alone(mutate)
    assert found.tools == {_READER}
    assert any(phrase in item for item in found.refused), (
        "the real reader with its %s passed the loop rule; refused: %s"
        % (mutation, found.refused)
    )


# ---------------------------------------------------------------------------
# 5. Controls: planted shapes, each refused by the rule it breaks and no other
# ---------------------------------------------------------------------------

#: Every plant sits under this: a builder, two ceilings from config, two
#: addresses and a module literal. All synthetic; nothing here is run.
_PLANT_HEADER = '''\
from linkedin_server import people_data
from linkedin_server.config import MAX_LIMIT, MAX_NAVIGATIONS_PER_CALL

ADDRESSES = ("/analytics/profile-views/", "/me/profile-views/")
PAGES = 50


def _record(row):
    return people_data.Person.from_page(name=row.get("name"))
'''

_A_READER = frozenset({"linkedin_planted"})


@dataclass(frozen=True)
class Plant:
    source: str
    #: rule -> a phrase one of that rule's findings must carry
    convicts: Dict[str, str]
    readers: FrozenSet[str] = _A_READER


PLANTS: Dict[str, Plant] = {
    # --- the order's four -------------------------------------------------
    "cursor-parameter": Plant('''
@mcp.tool()
async def linkedin_planted(cursor: str = "") -> dict:
    async with BROWSER.session() as page:
        await BROWSER.goto(page, ADDRESSES[0])
        return {"rows": [_record(row) for row in await harvest(page)]}
''', {"paging": "plant.linkedin_planted: cursor"}),
    "while-true": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        while True:
            await BROWSER.goto(page, ADDRESSES[0])
            rows.extend(_record(row) for row in await harvest(page))
            if len(rows) >= limit:
                return {"rows": rows[:limit]}
''', {"loops": "a while loop `while True` navigates (directly)"}),
    "range-of-pages": Plant('''
@mcp.tool()
async def linkedin_planted(pages: int = 3) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for number in range(pages):
            await BROWSER.goto(page, ADDRESSES[0] + "?page=" + str(number))
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows}
''', {"loops": "what it iterates is not a slice", "paging": "plant.linkedin_planted: pages"}),
    "load-more-helper": Plant('''
async def load_more(page):
    return await harvest(page)
''', {"helpers": "plant.load_more"}, readers=frozenset()),
    # --- the holes past those four ----------------------------------------
    "bound-is-a-large-config-ceiling": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for address in ADDRESSES[:MAX_LIMIT]:
            await BROWSER.goto(page, address)
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows[:limit]}
''', {"loops": "bounded by config.MAX_LIMIT"}),
    "bound-is-a-parameter": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for address in ADDRESSES[:limit]:
            await BROWSER.goto(page, address)
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows}
''', {"loops": "a parameter or local"}),
    "bound-is-a-module-literal": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for address in ADDRESSES[:PAGES]:
            await BROWSER.goto(page, address)
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows[:limit]}
''', {"loops": "not a name its module imports once"}),
    "stepped-slice": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for address in ADDRESSES[:MAX_NAVIGATIONS_PER_CALL:-1]:
            await BROWSER.goto(page, address)
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows[:limit]}
''', {"loops": "over a stepped slice"}),
    "navigating-comprehension": Plant('''
@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    async with BROWSER.session() as page:
        landed = [await BROWSER.goto(page, address) for address in ADDRESSES]
        return {"rows": [_record(row) for row in await harvest(page)][:limit], "n": len(landed)}
''', {"loops": "a comprehension"}),
    "loop-through-a-navigating-helper": Plant('''
async def _open(page, address):
    return await BROWSER.goto(page, address)


@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        for address in ADDRESSES:
            await _open(page, address)
            rows.extend(_record(row) for row in await harvest(page))
    return {"rows": rows[:limit]}
''', {"loops": "navigates (through _open)"}),
    "async-for-over-a-paging-generator": Plant('''
async def _batches(page):
    address = ADDRESSES[0]
    while address:
        await BROWSER.goto(page, address)
        yield await harvest(page)
        address = await following(page)


@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    rows = []
    async with BROWSER.session() as page:
        async for batch in _batches(page):
            rows.extend(_record(row) for row in batch)
    return {"rows": rows[:limit]}
''', {"loops": "an async for"}),
    "recursion": Plant('''
async def _read_from(page, address, rows):
    await BROWSER.goto(page, address)
    rows.extend(_record(row) for row in await harvest(page))
    following = await next_address(page)
    return await _read_from(page, following, rows) if following else rows


@mcp.tool()
async def linkedin_planted(limit: int = 25) -> dict:
    async with BROWSER.session() as page:
        return {"rows": (await _read_from(page, ADDRESSES[0], []))[:limit]}
''', {"recursions": "plant._read_from navigates and reaches itself"}),
    "reads-no-page": Plant('''
@mcp.tool()
async def linkedin_planted(rows: list) -> dict:
    return {"rows": [_record(row) for row in rows]}
''', {"silent": "linkedin_planted"}),
}


@pytest.mark.parametrize("name", sorted(PLANTS))
def test_a_planted_shape_is_refused_by_the_rule_it_breaks_and_no_other(name):
    plant = PLANTS[name]
    found = audit(parse_sources({"plant": _PLANT_HEADER + plant.source}))
    assert found.tools == plant.readers, (
        "the plant's reader was not derived, so no rule would reach it: %s" % sorted(found.tools)
    )
    findings = found.findings()
    for rule, phrase in sorted(plant.convicts.items()):
        assert any(phrase in item for item in findings[rule]), (
            "the %s rule did not convict the plant %r with %r; it found %s"
            % (rule, name, phrase, findings[rule])
        )
    others = {rule: items for rule, items in findings.items() if rule not in plant.convicts and items}
    assert others == {}, "rules other than %s fired on %r: %s" % (sorted(plant.convicts), name, others)


def test_a_plant_in_the_real_package_is_found_and_nothing_else_is():
    """The plant-only audits prove the rules; this proves the REAL walk.

    One planted module is added to the real package's parsed modules (in
    memory: no file is written) holding an undeclared reader with a cursor and
    a ``while True`` navigation, and a ``load_more`` helper. Every real-tree
    assertion above would fail on it, and on nothing of the real package's.
    """
    modules = dict(package_modules())
    modules["zz_plant"] = ast.parse('''\
from linkedin_server import people_data


def _zz_planted_record(row):
    return people_data.Person.from_page(name=row)


async def load_more(page):
    return []


@mcp.tool()
async def linkedin_zz_planted_roster(cursor: str = "") -> dict:
    rows = []
    async with BROWSER.session() as page:
        while True:
            await BROWSER.goto(page, "/mynetwork/")
            rows.extend(_zz_planted_record(row) for row in await load_more(page))
''')
    found = audit(modules)
    assert people_data.PEOPLE_TOOLS <= found.tools
    assert found.tools - people_data.PEOPLE_TOOLS == {"linkedin_zz_planted_roster"}
    assert found.paging == {"zz_plant.linkedin_zz_planted_roster": ["cursor"]}, found.paging
    assert found.helpers == ["zz_plant.load_more"], found.helpers
    assert found.refused, "the planted while True was not refused"
    assert all(item.startswith("zz_plant.linkedin_zz_planted_roster, line") for item in found.refused), (
        found.refused
    )
    assert found.recursions == [] and found.silent == [], (found.recursions, found.silent)


# ---------------------------------------------------------------------------
# 5. Controls: the derivation, the page parameter, the pagination pattern
# ---------------------------------------------------------------------------


def test_the_derivation_follows_an_alias_a_wrapper_and_a_builder_passed_as_a_value():
    """Step (a) through two import spellings; step (b) across modules and
    through an aliased import made inside a tool; and the reason the edge is a
    REFERENCE: a call-only closure, run over the same modules by the same
    :func:`closure`, misses the builder handed over as a value -- which is how
    the real reader holds its own. And the other side: a tool whose PARAMETER
    shares a builder's name references its parameter, not the builder, and is
    not a reader."""
    modules = parse_sources({
        "records": (
            "from linkedin_server.people_data import Group as Circle\n\n\n"
            "def circle(row):\n"
            "    return Circle.from_page(title=row)\n"
        ),
        "aliased": (
            "import linkedin_server.people_data as pd\n\n\n"
            "def event(row):\n"
            "    return pd.Event.from_page(title=row)\n"
        ),
        "wrapper": (
            "def circles(rows):\n"
            "    return [circle(row) for row in rows]\n"
        ),
        "server": (
            "@mcp.tool()\n"
            "async def linkedin_by_wrapper() -> dict:\n"
            "    return {'rows': circles([])}\n\n\n"
            "@mcp.tool()\n"
            "async def linkedin_by_value() -> dict:\n"
            "    return {'rows': parse_all([], event)}\n\n\n"
            "@mcp.tool()\n"
            "async def linkedin_by_local_import() -> dict:\n"
            "    from linkedin_server.records import circle as make\n"
            "    return {'rows': [make(row) for row in []]}\n\n\n"
            "@mcp.tool()\n"
            "async def linkedin_no_people(circle: str = '') -> dict:\n"
            "    return {'count': len(circle)}\n"
        ),
    })
    found = audit(modules)
    assert found.builders == {("records", "circle"), ("aliased", "event")}, found.builders
    assert found.tools == {
        "linkedin_by_wrapper", "linkedin_by_value", "linkedin_by_local_import",
    }, found.tools

    functions = module_functions(modules)
    call_edges = {key: calls(function) for key, function in functions.items()}
    call_only = {
        name for (module, name) in closure(call_edges, found.builders)
        if is_tool(functions[(module, name)])
    }
    assert call_only == {"linkedin_by_wrapper", "linkedin_by_local_import"}, (
        "a call-only closure should miss the builder passed as a value, and only "
        "that; it found %s" % call_only
    )


def builders_behind_the_write_door(modules: Mapping[str, ast.Module]) -> FrozenSet[Key]:
    """Record builders from which the write door is reached, had the
    derivation not stopped there."""
    functions = module_functions(modules)
    edges = {key: references(function) for key, function in functions.items()}
    return frozenset(
        builder
        for builder in record_builders(modules)
        if WRITE_DOOR in closure(edges, [builder])
    )


def test_the_builders_behind_the_write_door_are_the_declared_previews():
    """WHAT THE STOP SETS ASIDE, HELD EXACTLY: the builder the previews that
    name a third party go through (PREVIEW-NAMES-THE-RESOLVED-TARGET) -- two
    preview functions until lane L5's merge of master 52b55b6, one seam since.
    A new builder behind the door fails here until somebody decides it is a
    preview, not a reader."""
    behind = builders_behind_the_write_door(package_modules())
    assert behind == PREVIEW_BUILDERS, (
        "record builders behind the write door: %s; declared previews: %s"
        % (sorted(behind), sorted(PREVIEW_BUILDERS))
    )


def test_the_write_door_stops_only_itself():
    """THE CONTROL. The door hides a builder reached THROUGH it and nothing else:
    the same builder reached by a tool directly is still derived. And a function
    of the door's NAME in another module is not the door: it is derived -- and,
    because the derivation resolves by name, it re-opens the real door's path
    too, so the set GROWS and the declared-set test fails loudly, the direction
    this file's limits give a name collision."""
    only_the_door = {
        key: value
        for key, value in _DOOR_PLANT.items()
        if key != "elsewhere"
    }
    found = audit(parse_sources(only_the_door))
    assert found.tools == {"linkedin_planted_reader"}, found.tools
    assert builders_behind_the_write_door(parse_sources(only_the_door)) == {
        ("writes", "_name_the_invitation_recipient")
    }
    disguised = audit(parse_sources(_DOOR_PLANT))
    assert disguised.tools == {
        "linkedin_planted_reader", "linkedin_planted_disguise", "linkedin_planted_write",
    }, disguised.tools


#: A write door, a preview builder behind it, a reader reaching the builder
#: directly, and a function of the door's name in another module.
_DOOR_PLANT = {
    "writes": (
        "from linkedin_server import people_data\n\n\n"
        "def _name_the_invitation_recipient(label):\n"
        "    return people_data.Person.from_page(name=label)\n\n\n"
        "def preview(label):\n"
        "    return _name_the_invitation_recipient(label)\n"
    ),
    "server": (
        "async def _write_tool(label):\n"
        "    return writes.preview(label)\n\n\n"
        "@mcp.tool()\n"
        "async def linkedin_planted_write(item: str = '') -> dict:\n"
        "    return await _write_tool(item)\n\n\n"
        "@mcp.tool()\n"
        "async def linkedin_planted_reader() -> dict:\n"
        "    return {'rows': [writes._name_the_invitation_recipient('x')]}\n"
    ),
    "elsewhere": (
        "async def _write_tool(label):\n"
        "    return writes.preview(label)\n\n\n"
        "@mcp.tool()\n"
        "async def linkedin_planted_disguise() -> dict:\n"
        "    return await _write_tool('x')\n"
    ),
}


def test_the_derivation_follows_another_modules_attribute_the_tuple_and_getattr():
    """Three routes lane G's cold verification built records through without
    being derived (2026-09-27), each a builder now. The fourth it found -- an
    envelope dict built by hand -- names no record class and stays outside
    this derivation, a limit the module docstring states; when such a tool is
    driven, the tool-envelope guard refuses a ``returns_records`` verdict from
    any tool not in ``PEOPLE_TOOLS``."""
    modules = parse_sources({
        "via_module": (
            "from linkedin_server import shape\n\n\n"
            "def viewer(row):\n"
            "    return shape.people_data.Person.from_page(name=row)\n"
        ),
        "via_tuple": (
            "from linkedin_server import people_data\n\n\n"
            "def viewer(row):\n"
            "    return people_data.RECORD_TYPES[0].from_page(name=row)\n"
        ),
        "via_getattr": (
            "from linkedin_server import people_data\n\n\n"
            "def viewer(row):\n"
            "    return getattr(people_data, 'Person').from_page(name=row)\n"
        ),
        "by_hand": (
            "def viewer(row):\n"
            "    return {'name': row, 'headline': '', 'link': None, 'degree': None}\n"
        ),
    })
    assert record_builders(modules) == {
        ("via_module", "viewer"), ("via_tuple", "viewer"), ("via_getattr", "viewer"),
    }


def test_page_is_the_tab_on_a_helper_and_never_on_a_tool():
    tree = ast.parse(
        "async def _tab(page: Any, rows): ...\n"
        "async def _bare(page): ...\n"
        "async def _second(navigator, page: Any, spec): ...\n"
        "async def _numbered(page: int = 1): ...\n"
        "async def _optional(page: Optional[int] = None): ...\n"
        "async def _starting(tab, start: int = 0): ...\n"
        "@mcp.tool()\n"
        "async def linkedin_planted(page: Any = None): ...\n"
    )
    got = {node.name: paging_parameters(node) for node in tree.body}
    assert got == {
        "_tab": [],
        "_bare": [],
        "_second": [],
        "_numbered": ["page"],
        "_optional": ["page"],
        "_starting": ["start"],
        "linkedin_planted": ["page"],
    }, got


#: Names the pattern MUST match: the order's own examples, then the same shapes
#: as they would be written in this package.
PAGINATION_NAMES = (
    "paginate", "next_page", "load_more", "fetch_all", "all_pages",
    "iterate_pages", "page_through", "scroll_to_end",
    "_paginate_viewers", "read_viewers_paginated", "fetch_all_viewers",
    "_load_more_rows", "for_each_page", "_next_page_of_results",
    "scroll_to_bottom", "infinite_scroll", "loadMore", "has_more_pages",
    "next_cursor",
)

#: Names the pattern must LEAVE ALONE: the order's two examples; every
#: definition in the package whose name contains "page" (20 definitions, 18
#: names -- ``from_page`` is a method on each of the three records; measured
#: 2026-09-27, and none contains "scroll"); the package's names nearest the
#: vocabulary; and the reveals.
ORDINARY_NAMES = (
    "read_page_views", "_landing_page",
    "_page_is_dead", "_page", "company_page_url", "harvest_followed_pages",
    "read_company_page_follow", "group_page_url", "read_group_page",
    "page_identifier", "from_page", "linkedin_company_page_counts",
    "linkedin_follow_company_page", "linkedin_group_page",
    "linkedin_page_plugin_snippet", "_pages", "followed_page_state",
    "parse_followed_pages", "_read_company_page_follow",
    "company_page_follow_verdict",
    "parse_all", "discard_all", "_sweep_save_shaped", "_sweep_expired_grants",
    "iter_write_verbs_in", "_profile_views_more_analytics",
    "read_profile_views_more_insights", "allow_empty", "tally_filters",
    "show_more_analytics", "see_more", "read_more",
)


@pytest.mark.parametrize("name", PAGINATION_NAMES)
def test_the_pagination_pattern_matches_every_shape(name):
    assert is_pagination_name(name), name


@pytest.mark.parametrize("name", ORDINARY_NAMES)
def test_the_pagination_pattern_leaves_an_ordinary_name_alone(name):
    assert not is_pagination_name(name), name
