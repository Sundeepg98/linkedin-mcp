"""The unwired-reader guard stops at ``dom.py``, and readers no longer live only there.

``tests/test_reader_reachability.py`` refuses a reader nobody can call, its
allowlist is EMPTY, and ``server.py``'s own module docstring cites it as the
reason a reader gets registered rather than left sitting: *"not wired yet" is
not "by design"*. Three instances of that defect in one week are written up in
its docstring.

**IT SCANS ``dom.py`` AND NOTHING ELSE.** Its ``_dom_functions()`` parses one
file, and its reachability walk follows that one file's call graph. That was
the whole package when it was written.

**ON 2026-09-05 THREE NEW MODULES APPEARED IN ``linkedin_server/`` IN ONE
DAY** -- ``events.py``, ``groups.py`` and ``newsletters.py`` -- each created
for the same measured reason: ``dom.py`` is 460 KB with several waves writing
it at once, and ``git commit --only`` does not protect a neighbour's LINES
inside a path you name. That decision was correct. Its side effect was not
noticed by anybody, including the author of this file: **the one guard that
refuses an unwired reader now cannot see where new readers are being put.**

This is not a criticism of that guard. A check is scoped to what existed when
it was written, and this is what it looks like when the codebase moves out
from under one. The lesson is the guard's own: *a thing that exists and cannot
be reached passes every test it has* -- applied one level up, to the guard.

## WHY A PINNED INVENTORY AND NOT A FLAT REFUSAL

A flat "every reader must be wired" is the right end state and cannot be
committed today: a reader is unwired at this moment, for a stated reason, and a
red suite is not a way to communicate that. **It was TWO when this file
landed** -- ``events.read_events_home`` was the other, and it came off the list
in the same commit that wired it, which is the mechanism working rather than a
document being tidied. So this takes the shape this repository already uses for
exactly this situation -- a list of sites KNOWN to be in a state, explicitly
not a list cleared to be in it:

* an entry that is no longer unwired FAILS. Wiring a reader means deleting its
  line here, in the same commit, so the fix and the bookkeeping cannot drift;
* a reader NOT on the list that is unwired FAILS. A new one shows up in a diff
  instead of in an incident;
* every entry carries WHY, so the list cannot quietly become a place where
  readers are parked.

``dom.py`` is excluded because the other guard owns it. Overlapping guards
that disagree are worse than a gap.
"""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "linkedin_server"

#: Owned by ``tests/test_reader_reachability.py``. Not re-checked here.
COVERED_ELSEWHERE = {"dom.py"}

#: THE INVENTORY. Every reader outside ``dom.py`` that no other module calls,
#: with the reason it is in that state. **Not a list of readers cleared to be
#: unwired** -- a list of readers KNOWN to be, so the next one arrives in a
#: diff.
KNOWN_UNWIRED: dict[str, str] = {
    "newsletters.read_newsletter_subscriptions": (
        "Built 2026-09-05 by the newsletter wave. Not this wave's to wire, "
        "and named here rather than left invisible -- it is the reader that "
        "made the scope gap above measurable rather than theoretical, since "
        "two independent waves reached the same state on the same day."
    ),
}


def _called_names(tree: ast.AST) -> set[str]:
    """Names that are CALLED, never names that merely appear.

    The same distinction ``test_reader_reachability`` makes and for the same
    measured reason: a reader named in a docstring is not a reference, and a
    grep cannot tell the difference.
    """
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                out.add(func.id)
            elif isinstance(func, ast.Attribute):
                out.add(func.attr)
    return out


def _readers_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("read_")
    ]


def _unwired(modules: dict[str, str]) -> set[str]:
    """``module.reader`` for every reader no OTHER module calls.

    Takes the sources as a mapping so the detector can be run over a planted
    module and SHOWN FAILING, which is the only thing that makes its green
    worth reading.
    """
    parsed = {name: ast.parse(source) for name, source in modules.items()}
    unwired: set[str] = set()
    for name, tree in parsed.items():
        if name in COVERED_ELSEWHERE:
            continue
        readers = [
            node.name
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("read_")
        ]
        if not readers:
            continue
        elsewhere: set[str] = set()
        for other, other_tree in parsed.items():
            if other == name:
                continue
            elsewhere |= _called_names(other_tree)
        stem = name[:-3] if name.endswith(".py") else name
        for reader in readers:
            if reader not in elsewhere:
                unwired.add(f"{stem}.{reader}")
    return unwired


def _package_sources() -> dict[str, str]:
    return {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE.glob("*.py"))
    }


# ---------------------------------------------------------------------------
# The detector, shown failing, before anything is asserted through it
# ---------------------------------------------------------------------------

def test_the_detector_fires_on_a_planted_unwired_reader():
    """A CHECK THAT CANNOT FAIL CERTIFIES NOTHING.

    Two plants, because the detector has two ways to be wrong and only one of
    them is "misses a real one".
    """
    sources = _package_sources()
    sources["_planted.py"] = "async def read_planted_surface(page):\n    return {}\n"
    assert "_planted.read_planted_surface" in _unwired(sources)


def test_the_detector_stays_silent_on_a_planted_reader_that_is_called():
    """The other direction. A detector that flags everything is not one."""
    sources = _package_sources()
    sources["_planted.py"] = "async def read_planted_surface(page):\n    return {}\n"
    sources["_caller.py"] = (
        "from linkedin_server import _planted\n\n"
        "async def go(page):\n"
        "    return await _planted.read_planted_surface(page)\n"
    )
    assert "_planted.read_planted_surface" not in _unwired(sources)


def test_a_docstring_mention_is_not_a_call():
    """The exact confusion the sibling guard measured, reproduced here.

    Without this the detector could be a grep wearing an AST's costume.
    """
    sources = _package_sources()
    sources["_planted.py"] = "async def read_planted_surface(page):\n    return {}\n"
    sources["_caller.py"] = (
        '"""See _planted.read_planted_surface for details."""\n'
    )
    assert "_planted.read_planted_surface" in _unwired(sources)


# ---------------------------------------------------------------------------
# The scope gap this file exists for, asserted rather than described
# ---------------------------------------------------------------------------

def test_the_sibling_guard_scans_only_dom_and_readers_now_live_elsewhere():
    """THE PREMISE. If either half stops holding, this file should be deleted.

    Half one: the sibling guard parses one file. Half two: there are readers
    outside it. The day the sibling widens its scope, this goes red and the
    right response is to delete this file rather than to adjust it.
    """
    sibling = (REPO / "tests" / "test_reader_reachability.py").read_text(
        encoding="utf-8"
    )
    assert 'DOM = ' in sibling or "dom.py" in sibling
    tree = ast.parse(sibling)
    parses_one_file = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_dom_functions"
    ]
    assert parses_one_file, (
        "the sibling guard no longer has _dom_functions; re-read its scope "
        "before trusting this file's premise"
    )

    outside = {
        name: _readers_in(PACKAGE / name)
        for name in _package_sources()
        if name not in COVERED_ELSEWHERE
    }
    assert any(outside.values()), (
        "no reader lives outside dom.py any more -- delete this file"
    )


def test_the_unwired_readers_are_exactly_the_pinned_inventory():
    """(A) THE ASSERTION. Both directions, so neither half can rot alone."""
    measured = _unwired(_package_sources())
    pinned = set(KNOWN_UNWIRED)
    assert measured == pinned, (
        "unwired readers have changed.\n"
        f"  newly unwired (add with a reason, or wire it): "
        f"{sorted(measured - pinned)}\n"
        f"  no longer unwired (delete its line here, in the same commit as "
        f"the wiring): {sorted(pinned - measured)}"
    )


def test_every_pinned_entry_carries_a_reason():
    """A list of names is a silencer. A list of reasons is a record."""
    thin = [
        name for name, reason in KNOWN_UNWIRED.items() if len(reason) < 80
    ]
    assert not thin, thin
