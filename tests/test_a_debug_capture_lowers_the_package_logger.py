"""A log capture lowered to DEBUG on the ROOT alone cannot hear this package.

THE SHAPE, found at 18 sites on 2026-09-28 (lane G, the order of 04:25, item
4): ``caplog.at_level(logging.DEBUG)`` or ``caplog.set_level(logging.DEBUG)``
with no ``logger=``, around a call whose log the test then asserts CLEAN.

WHY IT CANNOT FAIL. ``linkedin_server/config.py`` gives the ``linkedin``
logger a level of its own (INFO unless ``LINKEDIN_LOG_LEVEL`` says otherwise)
and ``propagate = False``. The capture's HANDLER reaches that logger --
``tests/conftest.py`` attaches it by name -- but a record below the logger's
own level is dropped before any handler sees it, and a call that names no
logger lowers only the root. So "no record carries the value" passed on a
build that logged the value at DEBUG: each of the 18 was measured green with
exactly that record planted inside the call it guards.

THE RULE, read by PARSING every function under ``tests/``: a caplog level
call at DEBUG (or at a level the parser cannot read) that names no logger
must sit, in the same function, beside one that names a logger at DEBUG (or
at a level the parser cannot read). The fixed sites do exactly that, each
through a helper that lowers both and proves a DEBUG control record comes
back.

WHAT IT DOES NOT READ: a capture that names the package logger at WARNING
and then asserts the absence of a value the code might log at DEBUG -- three
sites had that shape, and whether one is vacuous depends on the level the
code logs at, which no parse of the test can see. Nor a capture taken through
a fixture under another name than ``caplog``.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent

#: The level calls on a caplog fixture.
LEVEL_CALLS = {"at_level", "set_level"}

#: Levels the rule reads as BELOW the package logger's INFO.
LOW = {"logging.DEBUG", "logging.NOTSET", "'DEBUG'", "'NOTSET'", "10", "0"}

#: Levels the rule reads as AT OR ABOVE it. Anything in neither set is read as
#: low: a level the parser cannot read may be DEBUG, and a guard errs wide.
HIGH = {"logging.INFO", "logging.WARNING", "logging.ERROR", "logging.CRITICAL",
        "'INFO'", "'WARNING'", "'ERROR'", "'CRITICAL'", "20", "30", "40", "50"}


def _is_caplog(node: ast.AST) -> bool:
    return ((isinstance(node, ast.Name) and node.id == "caplog")
            or (isinstance(node, ast.Attribute) and node.attr == "caplog"))


def _level_and_logger(call: ast.Call) -> tuple[str, bool]:
    """``(the level as written, does the call name a logger)``."""
    level = ast.unparse(call.args[0]) if call.args else "<none>"
    named = len(call.args) > 1 and not (
        isinstance(call.args[1], ast.Constant) and call.args[1].value is None)
    for keyword in call.keywords:
        if keyword.arg == "level":
            level = ast.unparse(keyword.value)
        elif keyword.arg == "logger":
            named = not (isinstance(keyword.value, ast.Constant)
                         and keyword.value.value is None)
    return level, named


class _Calls(ast.NodeVisitor):
    """Every caplog level call, filed under its INNERMOST enclosing function
    (the module, for one outside any function)."""

    def __init__(self) -> None:
        self.stack: list[str] = ["<module>"]
        self.by_scope: dict[str, list[tuple[int, str, bool]]] = {}

    def _scope(self, node: ast.AST, name: str) -> None:
        self.stack.append(f"{name}@{node.lineno}")
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scope(node, node.name)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._scope(node, node.name)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr in LEVEL_CALLS
                and _is_caplog(func.value)):
            level, named = _level_and_logger(node)
            self.by_scope.setdefault(self.stack[-1], []).append(
                (node.lineno, level, named))
        self.generic_visit(node)


def root_only_debug_captures(source: str) -> tuple[list[str], int]:
    """``(offending calls as "scope:line level", how many level calls were read)``."""
    visitor = _Calls()
    visitor.visit(ast.parse(source))
    offending: list[str] = []
    seen = 0
    for scope, calls in visitor.by_scope.items():
        seen += len(calls)
        low = [(line, level, named) for line, level, named in calls
               if level not in HIGH]
        if any(named for _line, _level, named in low):
            continue
        offending.extend(f"{scope}:{line} {level}"
                         for line, level, named in low if not named)
    return sorted(offending), seen


def test_no_capture_lowers_only_the_root_to_debug() -> None:
    """Every test module, parsed. A hit names the function and the line."""
    hits: list[str] = []
    seen = 0
    modules = sorted(TESTS.glob("*.py"))
    assert len(modules) > 100, len(modules)
    for path in modules:
        found, read = root_only_debug_captures(path.read_text(encoding="utf-8"))
        seen += read
        hits.extend(f"{path.name}::{hit}" for hit in found)
    assert not hits, (
        "a caplog capture lowered to DEBUG without naming a logger, and no "
        "call beside it names one: the package logger stays at its own INFO, "
        "so an absence asserted over this capture passes on a build that logs "
        "the value at DEBUG. Lower the package logger too "
        "(caplog.at_level(logging.DEBUG, logger='linkedin')) and prove a DEBUG "
        f"control record comes back. {hits}"
    )
    # A parse that found no level call at all would pass this vacuously.
    assert seen >= 10, f"only {seen} caplog level calls read: the parse broke"


#: THE CONTROL: planted sources, each with the verdict the rule must give.
PLANTS = {
    "root-only at_level": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    with caplog.at_level(logging.DEBUG):\n"
        "        pass\n", True),
    "root-only set_level, the level spelled as a string": (
        "def test_x(caplog):\n"
        "    caplog.set_level('DEBUG')\n", True),
    "a level the parser cannot read": (
        "def test_x(caplog, level):\n"
        "    caplog.set_level(level)\n", True),
    "the package logger lowered beside it": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    with caplog.at_level(logging.DEBUG), caplog.at_level(\n"
        "            logging.DEBUG, logger='linkedin'):\n"
        "        pass\n", False),
    "the logger named positionally": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    caplog.set_level(logging.DEBUG, 'linkedin')\n", False),
    "the companion only at WARNING": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    caplog.set_level(logging.DEBUG)\n"
        "    caplog.set_level(logging.WARNING, logger='linkedin')\n", True),
    "logger=None names no logger": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    caplog.set_level(logging.DEBUG, logger=None)\n", True),
    "the companion in ANOTHER function": (
        "import logging\n"
        "def helper(caplog):\n"
        "    caplog.set_level(logging.DEBUG, logger='linkedin')\n"
        "def test_x(caplog):\n"
        "    caplog.set_level(logging.DEBUG)\n", True),
    "root at INFO is not this shape": (
        "import logging\n"
        "def test_x(caplog):\n"
        "    caplog.set_level(logging.INFO)\n", False),
}


@pytest.mark.parametrize("case", sorted(PLANTS))
def test_the_rule_reads_each_planted_capture(case: str) -> None:
    """Each plant red or clean as declared -- so neither a rule that flags
    nothing nor one that flags every level call passes this."""
    source, offends = PLANTS[case]
    found, seen = root_only_debug_captures(source)
    assert seen >= 1, case
    assert bool(found) is offends, (case, found)
