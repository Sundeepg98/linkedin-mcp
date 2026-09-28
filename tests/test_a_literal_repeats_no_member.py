"""A literal that repeats a member says less than it looks. A set keeps one of
the two; a dict keeps the LATER value and the earlier one is unreachable.
Python raises on neither.

WHAT WAS FOUND (the orchestrator's call of 2026-09-28 12:32, lane L5).
``_FETCH_NAMES`` in ``tests/test_api_call_sites.py`` read
``frozenset({"urlopen", "urlretrieve", "urlretrieve"})`` from ``fbedfca``
(2026-08-24) until that day: three names written, two held. Nothing broke --
which is the point. A reader counted three fetch names the walker hunts, and
the third was never there. Two scratch walkers found it (the live lane's and
this lane's, 2026-09-28) while checking dict keys; nothing in the suite had
ever asked, so it was left twice for its owner.

WHAT THIS FILE HOLDS, over every Python file a commit could carry -- tracked
plus untracked-not-ignored, the identity sweep's own set
(``committable_files``):

1. no SET display -- ``{a, b}``, and ``set(...)`` or ``frozenset(...)`` over a
   list, tuple or set display -- holds two members Python would collapse into
   one;
2. no DICT display holds two keys Python would collapse into one.

WHAT COUNTS AS A REPEAT is what Python itself collapses: equal constant values
(compared by value after ``ast.literal_eval``, so ``1`` and ``True`` are one,
as the set would make them one), and two members spelled by the same bare name
or dotted attribute. A member holding a call, a comprehension, a starred
expression or an f-string is never compared: it may evaluate differently each
time, and a guard that guessed would convict the innocent.

A FILE THAT DOES NOT PARSE is a failure here, never a skip: a sweep that skips
what it cannot read passes vacuously on exactly the files it did not check.

SHOWN FAILING: on ``tests/test_api_call_sites.py`` as it stood (the lane L5
record carries the red run), and by the controls below, each on a planted
literal.
"""
from __future__ import annotations

import ast
import collections

import pytest

from tests.test_no_committed_credential import REPO, committable_files

#: The constructors whose single literal argument is a set in all but syntax.
SET_CONSTRUCTORS = frozenset({"set", "frozenset"})

#: Every Python file this sweep reads, as repo-relative posix strings.
PYTHON = sorted(rel for rel in committable_files() if rel.endswith(".py"))


def member_key(node: ast.AST):
    """A member's identity as Python would collapse it, or None: not compared.

    A constant (or a tuple of constants) is compared by VALUE, so the key is
    what the set or dict would hash; a bare name or dotted attribute by its
    spelling. Anything else may evaluate differently each time.
    """
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        pass
    else:
        try:
            hash(value)
        except TypeError:
            return None
        return ("value", value)
    probe = node
    while isinstance(probe, ast.Attribute):
        probe = probe.value
    if isinstance(probe, ast.Name):
        return ("spelled", ast.dump(node))
    return None


def literals_in(tree: ast.AST):
    """Every set and dict display in a parsed file: ``(line, kind, members)``.

    A ``set(...)`` / ``frozenset(...)`` over a LIST or TUPLE display counts as
    a set display; over a SET display it is not counted twice, because the walk
    reaches that inner display on its own.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Set):
            yield node.lineno, "set", node.elts
        elif isinstance(node, ast.Dict):
            yield node.lineno, "dict", [key for key in node.keys if key is not None]
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in SET_CONSTRUCTORS
            and len(node.args) == 1
            and not node.keywords
            and isinstance(node.args[0], (ast.List, ast.Tuple))
        ):
            yield node.lineno, "set", node.args[0].elts


def repeats(members) -> list[tuple[str, int]]:
    """The members Python would collapse: ``(first spelling, times written)``."""
    counts: collections.Counter = collections.Counter()
    spelled: dict = {}
    for member in members:
        key = member_key(member)
        if key is None:
            continue
        counts[key] += 1
        spelled.setdefault(key, ast.unparse(member))
    return [(spelled[key], n) for key, n in counts.items() if n > 1]


def repeats_in(source: str, filename: str = "<planted>") -> list[tuple[int, str, str, int]]:
    """``(line, kind, member, times)`` for every repeat in one source text."""
    found = []
    for line, kind, members in literals_in(ast.parse(source, filename=filename)):
        for member, times in repeats(members):
            found.append((line, kind, member, times))
    return found


# ---------------------------------------------------------------------------
# The sweep
# ---------------------------------------------------------------------------


def _sweep() -> tuple[list[str], collections.Counter]:
    offenders: list[str] = []
    looked: collections.Counter = collections.Counter()
    for rel in PYTHON:
        try:
            source = (REPO / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            offenders.append(f"{rel}: unreadable ({type(exc).__name__})")
            continue
        try:
            tree = ast.parse(source, filename=rel)
        except SyntaxError as exc:
            offenders.append(f"{rel}: does not parse on this interpreter ({exc.msg}, line {exc.lineno})")
            continue
        looked["files"] += 1
        for line, kind, members in literals_in(tree):
            looked[kind] += 1
            for member, times in repeats(members):
                offenders.append(f"{rel}:{line} a {kind} display repeats {member} ({times} times)")
    return offenders, looked


def test_no_literal_in_the_repository_repeats_a_member():
    offenders, _looked = _sweep()
    assert not offenders, (
        "a literal repeats a member Python would collapse -- a set keeps one, a "
        "dict keeps the later value. Drop the repeat, or put in the member that "
        "was meant:\n  " + "\n  ".join(offenders)
    )


def test_the_sweep_actually_looked():
    """A sweep passes vacuously over an empty file list, or one it cannot parse.

    MEASURED 2026-09-28, the day it was written, under Python 3.13 and 3.10
    alike: 596 committable Python files, every one parsed, 732 set displays
    and 4449 dict displays read, one repeat -- the one above. The floors are
    far below that and far above zero."""
    _offenders, looked = _sweep()
    assert len(PYTHON) >= 400, len(PYTHON)
    assert looked["files"] == len(PYTHON), looked
    assert looked["set"] >= 300, looked
    assert looked["dict"] >= 2000, looked


# ---------------------------------------------------------------------------
# The controls: each plants a literal and shows the check convicting it
# ---------------------------------------------------------------------------


def test_THIS_CONTROL_CAN_FAIL_the_line_as_it_stood_is_convicted():
    """The literal ``fbedfca`` wrote, verbatim."""
    planted = '_FETCH_NAMES = frozenset({"urlopen", "urlretrieve", "urlretrieve"})\n'
    assert repeats_in(planted) == [(1, "set", "'urlretrieve'", 2)]


@pytest.mark.parametrize(
    "planted, kind, member",
    [
        ('X = {"a": 1, "a": 2}\n', "dict", "'a'"),
        ("X = {1, True}\n", "set", "1"),
        ("X = {('a', 'b'), ('a', 'b')}\n", "set", "('a', 'b')"),
        ("X = {NAME, NAME}\n", "set", "NAME"),
        ("X = {mod.NAME: 1, mod.NAME: 2}\n", "dict", "mod.NAME"),
        ('X = frozenset(["a", "a"])\n', "set", "'a'"),
        ('X = set(("a", "a"))\n', "set", "'a'"),
        ("def f():\n    return {-1, -1}\n", "set", "-1"),
    ],
)
def test_THIS_CONTROL_CAN_FAIL_every_kind_of_repeat_is_convicted(planted, kind, member):
    found = repeats_in(planted)
    assert [(k, m) for _line, k, m, _n in found] == [(kind, member)], found


@pytest.mark.parametrize(
    "planted",
    [
        "X = {f(), f()}\n",
        "X = {*a, *a}\n",
        "X = {**a, **a}\n",
        'X = {f"{a}", f"{a}"}\n',
        'X = {1, "1", 1.5, b"1"}\n',
        'X = {"a": 1, "b": 1}\n',
        'X = frozenset({"urlopen", "urlretrieve"})\n',
    ],
)
def test_a_member_that_may_differ_or_does_differ_is_not_convicted(planted):
    assert repeats_in(planted) == []


def test_a_set_display_inside_a_constructor_is_counted_once():
    """``frozenset({...})``: the walk reaches the inner display itself, so the
    constructor adds no second report of the same repeat."""
    assert len(repeats_in('X = frozenset({"a", "a"})\n')) == 1
