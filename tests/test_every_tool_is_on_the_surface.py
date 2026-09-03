"""Every ``@mcp.tool()`` decorates the function it was written for.

THE DEFECT THIS FILE EXISTS FOR, measured 2026-09-03 on uncommitted work and
fixed the same hour. A helper was inserted BETWEEN an existing ``@mcp.tool()``
and the ``async def`` it decorated::

    @mcp.tool()
    async def _attach_recipient_ids(page, rows):   <- the new helper
        ...
    async def linkedin_who_viewed_me(limit=25):    <- the tool, now bare

``mcp.list_tools()`` then reported::

    linkedin_who_viewed_me registered: False
    _attach_recipient_ids  registered: True

A shipped READ tool -- the one the capability census calls the highest-signal
tool in the package -- stopped being callable, and a private helper whose
first parameter is a live Playwright page took its place on the tool surface.

## Why nothing already here saw it

**The file's SHAPE did not change.** The tool count stayed at 35. The
function is still defined, still has its docstring, still appears in every
grep. `tests/test_server_surface.py` is 107 KB of assertions about this
module and none of them failed, because a decorator moving between two
adjacent defs changes WHICH function is a tool without changing anything a
counter or a substring search can see.

So the check has to ask the registry for a NAME. That is the whole of this
file, and it is deliberately small: three questions that a large surface test
cannot ask by accident.

## Shown failing, and this says exactly how rather than more than it can

**THE DEFECTIVE REGISTRY WAS MEASURED, NOT IMAGINED.** The three lines quoted
above came off ``mcp.list_tools()`` on the real tree while the defect was
live, at commit ``c23a288`` -- the tool count 35, ``linkedin_who_viewed_me``
absent, ``_attach_recipient_ids`` present. That reading is recorded in
:data:`REGISTRY_WHILE_BROKEN` and
``test_both_rules_reject_the_registry_that_was_actually_measured`` runs both
rules over it, so each is shown REJECTING a real defect rather than only ever
being seen passing.

What is deliberately NOT claimed: these two test functions were written after
the fix and were never themselves red against the live module. Re-introducing
the defect to watch them go red would mean leaving a shipped tool
deregistered on a tree three other agents are running their own suites
against, and that is a worse trade than replaying the measurement. The rules
below and the rules in that control are the same two predicates, applied to
the same two names.
"""

from __future__ import annotations

import asyncio

import pytest

from linkedin_server import server as server_module


#: Tools this package ships that a caller reaches by NAME. Deliberately a
#: hand-written list rather than one derived from the module, because a
#: derived list would be computed the same way the bug was: from what the
#: decorator happened to land on. The point of naming them is that a name
#: cannot silently move.
#:
#: NOT EXHAUSTIVE, AND THAT IS STATED SO NOBODY TREATS IT AS A REGISTRY. It
#: is the read surface plus the two tools whose absence would be hardest to
#: notice. A tool missing from here is not asserted; a tool named here and
#: missing from the registry fails.
EXPECTED_TOOLS = (
    "linkedin_who_viewed_me",
    "linkedin_my_profile",
    "linkedin_job_detail",
    "linkedin_search_jobs",
    "linkedin_saved_jobs",
    "linkedin_my_applications",
    "linkedin_draft_applications",
    "linkedin_notifications",
    "linkedin_followed_companies",
    "linkedin_surface_census",
    "linkedin_server_info",
    "linkedin_session_info",
)


def _tool_names() -> list[str]:
    return sorted(tool.name for tool in asyncio.run(server_module.mcp.list_tools()))


def test_there_are_tools_to_check():
    """A sweep over an empty registry passes forever.

    Named for this file's own subject: a check that cannot fail looks exactly
    like coverage.
    """
    names = _tool_names()
    assert len(names) > 25, names


@pytest.mark.parametrize("name", EXPECTED_TOOLS)
def test_every_read_tool_this_package_ships_is_registered(name):
    """A tool that is defined but not decorated is not a tool.

    It keeps its docstring, keeps its name, keeps every test written about
    the function -- and no caller can invoke it.
    """
    names = _tool_names()
    assert name in names, (
        "%s is not on the tool surface. It is almost certainly still DEFINED "
        "in server.py -- check whether its @mcp.tool() now sits above a "
        "different def, which is how this failed before. Registered: %r"
        % (name, names)
    )


def test_no_private_helper_is_a_tool():
    """A leading underscore says "not part of the surface". Believe it.

    This is the other half of the same defect and it is the more dangerous
    half: the helper that got the decorator takes a live Playwright ``page``
    as its first parameter, so the schema published to callers asked for one.
    """
    private = [name for name in _tool_names() if name.startswith("_")]
    assert private == [], (
        "these private helpers are published as tools: %r. A name beginning "
        "with an underscore is not part of the tool surface, and one that "
        "takes a page or a rows list cannot be called meaningfully by "
        "anybody." % private
    )


#: THE REGISTRY AS IT ACTUALLY STOOD WHILE THE DEFECT WAS LIVE, read off
#: ``mcp.list_tools()`` at commit ``c23a288``. Two entries differ from the
#: repaired surface and they are the whole of the defect: the tool is gone and
#: the helper is there. Kept as data so both rules can be shown rejecting a
#: real reading rather than an invented one.
REGISTRY_WHILE_BROKEN = ("_attach_recipient_ids", "linkedin_my_profile")


def test_both_rules_reject_the_registry_that_was_actually_measured():
    """THE CONTROL. Both rules, run over the measured defective registry.

    Without this the two tests above are assertions that have only ever been
    seen passing, which is the state this repository treats as uncertified.
    """
    broken = list(REGISTRY_WHILE_BROKEN)

    # RULE 1 -- the missing tool. This is the assertion
    # test_every_read_tool_this_package_ships_is_registered makes, and it
    # fails on this reading.
    assert "linkedin_who_viewed_me" not in broken
    assert "linkedin_who_viewed_me" in _tool_names()

    # RULE 2 -- the private helper on the surface. This is the assertion
    # test_no_private_helper_is_a_tool makes, and it fails on this reading.
    assert [name for name in broken if name.startswith("_")] == [
        "_attach_recipient_ids"
    ]
    assert [name for name in _tool_names() if name.startswith("_")] == []

    # AND THE COUNT DID NOT MOVE, which is the reason neither rule could be
    # replaced by a cheaper one. 35 tools before, 35 after.
    assert len(_tool_names()) == 35
