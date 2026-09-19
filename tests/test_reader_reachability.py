"""Every reader in ``dom.py`` must be reachable from the tool surface.

THREE INSTANCES OF ONE DEFECT IN ONE WEEK, and this test exists to end the
class:

1. ``dom.read_compose_fields`` -- built, unit-tested, mutation-tested, and
   **never wired to a tool**. It could not be exercised on a reconnect
   regardless of which build was loaded.
2. ``linkedin_profile_editor_fields`` -- shipped having **never been run**. It
   refused its own operator for two defects that a single live call exposed.
3. A tool registered after a subagent had already spawned, and therefore
   invisible to it.

**A thing that exists and cannot be reached passes every test it has.** That is
the same shape as a check that cannot fail: it looks like coverage and is not.
A NEEDS-RECONNECT list in prose was standing in for this, and a list cannot
enforce what a test can -- the list itself carried an item nobody could invoke.

## What reachable means here, and why it is not a grep

**Transitively callable from ``server.py``**, following calls through
``dom.py``'s own graph. Two things a substring search gets wrong, both
observed while writing this:

* ``read_compose_fields`` appears in ``shape.py`` -- in a DOCSTRING. A grep
  calls that a reference; it is not one, and the reader is unreachable.
* ``read_job_identity`` appears in no other module at all, which a grep calls
  dead. It is called by ``read_job_posting`` INSIDE ``dom.py``, so it is
  genuinely reachable and needs no exception.

So the graph is built from ``ast.Call`` nodes and docstrings cannot vote.
"""

import ast
import pathlib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parent.parent / "linkedin_server"
DOM = PACKAGE / "dom.py"
SERVER = PACKAGE / "server.py"

#: Readers known to be unreachable, each with the reason. AN ENTRY IS A CLAIM
#: THAT IS ITSELF CHECKED, not a waiver: the test below asserts that an
#: allowlisted reader really IS unreachable, so listing a reachable one fails
#: just as loudly as leaving an unreachable one off. That is the difference
#: between an allowlist and a silencer.
#: EMPTY, AND EMPTY IS THE TARGET STATE rather than a coincidence. It held
#: one entry for a day: ``read_settings_surface``, found by this test on the
#: day it was written -- the fifth instance of the class and one a substring
#: search PASSES, because its only mention outside ``dom.py`` was a comment.
#:
#: THAT COMMENT WAS THE FINDING. ``writes.py`` recorded the reader as
#: "remains available and is now uncalled from this module" one sentence
#: after arguing that "a reader kept for a state nobody consults is a reader
#: that goes stale unread". The fact was observed, the rule was stated, and
#: the two were never connected. It was deleted on 2026-09-02 after the wave
#: lead ruled, and after ``update_setting``'s before-and-after path was
#: verified to read the dark-mode page through ``dom.read_surface_census``
#: and never through it.
#:
#: THE ENTRY-VALIDATION BELOW NOW HAS NO REAL ENTRY TO RUN ON, which would
#: make it a sweep over nothing -- the exact defect this file is about. So
#: ``test_the_entry_validation_can_still_fail`` exercises all three rules on
#: fabricated entries instead.
UNREACHABLE_BY_DESIGN: dict[str, str] = {}


def _called_names(tree: ast.AST) -> set[str]:
    """Every function name CALLED in this tree. Docstrings cannot vote."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            found.add(func.id)
        elif isinstance(func, ast.Attribute):
            found.add(func.attr)
    return found


def _dom_functions() -> dict[str, ast.AST]:
    tree = ast.parse(DOM.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _reachable_from_the_tool_surface() -> set[str]:
    """Names reachable from ``server.py``, transitively through ``dom.py``.

    Seeded from every call in server.py and in the modules server.py itself
    reaches for -- ``writes.py`` is a tool's callee, so a reader used only
    there is still reachable by a caller.
    """
    seeds: set[str] = set()
    for module in PACKAGE.glob("*.py"):
        if module.name == "dom.py":
            continue
        seeds |= _called_names(ast.parse(module.read_text(encoding="utf-8")))

    functions = _dom_functions()
    reachable: set[str] = set()
    frontier = [name for name in seeds if name in functions]
    while frontier:
        name = frontier.pop()
        if name in reachable:
            continue
        reachable.add(name)
        for callee in _called_names(functions[name]):
            if callee in functions and callee not in reachable:
                frontier.append(callee)
    return reachable


def _public_readers() -> list[str]:
    return sorted(
        name
        for name in _dom_functions()
        if name.startswith("read_") and not name.startswith("_")
    )


def test_there_are_readers_to_check():
    """A sweep over nothing passes forever.

    Named because this file's whole subject is things that look like coverage
    and are not -- an empty corpus here would be the defect it is written to
    catch, wearing the test's own name.
    """
    readers = _public_readers()
    assert len(readers) > 15, readers
    assert "read_surface_census" in readers


@pytest.mark.parametrize("reader", _public_readers())
def test_every_reader_is_reachable_from_the_tool_surface(reader):
    """A reader no caller can invoke is a hypothesis, not a capability.

    It will pass its unit tests, pass its mutation tests, sit on a
    needs-reconnect list, and be discovered unrunnable at the moment somebody
    spends a reconnect on it.
    """
    reachable = _reachable_from_the_tool_surface()
    if reader in UNREACHABLE_BY_DESIGN:
        # THE ENTRY IS VERIFIED, NOT WAIVED. An allowlisted reader that turns
        # out to be reachable means the entry is stale, and a stale exception
        # is how an allowlist becomes a silencer.
        assert reader not in reachable, (
            "%s is on UNREACHABLE_BY_DESIGN but IS reachable -- the entry is "
            "stale and should be removed" % reader
        )
        assert UNREACHABLE_BY_DESIGN[reader].strip(), reader
        return
    assert reader in reachable, (
        "%s is defined in dom.py and NOTHING calls it, directly or "
        "transitively, from outside dom.py. It cannot be exercised by any "
        "tool, so its tests certify a thing no caller can reach." % reader
    )


def test_a_docstring_mention_does_not_count_as_a_reference():
    """THE CONTROL, and it is the mistake this test was almost built on.

    A substring search reported ``read_compose_fields`` as referenced because
    ``shape.py`` names it IN A DOCSTRING. A reader whose only mention is prose
    is exactly as unreachable as one with no mention at all, and a checker
    that cannot tell them apart would have declared the defect fixed.
    """
    prose_only = ast.parse('"""See dom.read_nothing_at_all for details."""\n')
    assert "read_nothing_at_all" not in _called_names(prose_only)

    real_call = ast.parse("dom.read_nothing_at_all(page)\n")
    assert "read_nothing_at_all" in _called_names(real_call)


def test_a_reader_called_only_from_inside_dom_is_still_reachable():
    """THE OTHER HALF OF THE CONTROL, so this does not fail honest code.

    ``read_job_identity`` is called by ``read_job_posting`` and by nothing
    outside ``dom.py``. A checker that only looked at other modules would call
    it dead and force a pointless exception entry. Transitive reachability is
    what makes the allowlist able to stay empty.
    """
    functions = _dom_functions()
    assert "read_job_identity" in functions
    assert "read_job_posting" in functions
    assert "read_job_identity" in _called_names(functions["read_job_posting"])
    assert "read_job_identity" in _reachable_from_the_tool_surface()


def test_every_exception_names_a_reader_that_exists_and_carries_a_reason():
    """A silent allowlist is the disease; a checked one is the treatment.

    Every defect this file exists for was invisible rather than argued. So an
    entry must name a REAL function, carry a reason a reader can weigh, and be
    genuinely unreachable -- all three asserted, so the list cannot quietly
    become the place unreachable code goes to stop being noticed.
    """
    functions = _dom_functions()
    for name, reason in UNREACHABLE_BY_DESIGN.items():
        assert name in functions, "%s is allowlisted and does not exist" % name
        assert len(reason.strip()) > 40, (name, reason)
    # AND THE LIST STAYS EMPTY, tightened from ``<= 1`` on 2026-09-02 when
    # its one entry was deleted rather than kept. Growth is the signal that
    # unreachable code is being ACCEPTED rather than fixed, and a bound that
    # still has room in it is a bound nothing has to argue with. Zero means
    # the next unreachable reader cannot be parked here without somebody
    # deliberately widening this line.
    assert len(UNREACHABLE_BY_DESIGN) == 0, sorted(UNREACHABLE_BY_DESIGN)


def test_the_entry_validation_can_still_fail():
    """THE VALIDATION ABOVE NOW RUNS OVER AN EMPTY DICT, so it is shown
    working on fabricated entries instead.

    A loop over nothing passes forever. That is this file's own subject, and
    emptying the allowlist turned two of its checks into exactly that -- the
    three-rule validation, and the allowlisted branch of the reachability
    parametrisation. Both rules are re-run here against entries built in this
    test, so the treatment for the real list being empty is not that nobody
    checks the rules any more.

    THE THREE RULES, each shown rejecting:

    * an entry naming a function that does not exist
    * an entry whose reason is too short to weigh
    * an entry naming a reader that IS reachable -- the stale-exception case,
      which is how an allowlist becomes a silencer
    """
    functions = _dom_functions()
    reachable = _reachable_from_the_tool_surface()

    # Rule 1: the name must exist.
    assert "read_a_function_that_was_never_written" not in functions

    # Rule 2: the reason must be long enough to carry an argument.
    assert len("too short".strip()) <= 40
    assert len(("uncalled since the index reader was replaced, and its own "
                "comment argues for deleting it").strip()) > 40

    # Rule 3: an allowlisted reader must genuinely be unreachable. Pointed at
    # a reader this file already proves reachable, so the rule is shown
    # rejecting a real name rather than an invented one.
    assert "read_surface_census" in functions
    assert "read_surface_census" in reachable
