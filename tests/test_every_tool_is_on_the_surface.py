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
    #
    # 36 FROM 2026-09-03: ``linkedin_connections``, a READ that ships
    # refusing because its side-effect cost is unmeasured. The count is
    # updated in the commit that adds the tool, which is the review moment
    # this assertion exists to create.
    #
    # 37 FROM 2026-09-05: ``linkedin_search_appearances``, a READ, and the
    # review moment this assertion creates was USED rather than waved
    # through. It was going to ship as an unwired reader with no tool at all,
    # on the argument that a docstring should not describe a page its author
    # has not opened. ``test_reader_reachability`` refused that, and it was
    # right: its allowlist is EMPTY, no reader in this package has ever been
    # exempted, and "not wired yet" would have been filed as "by design".
    # The honest fix was to register the tool and put the ignorance in the
    # docstring, where a caller reads it.
    # 38 FROM 2026-09-05: ``linkedin_events_home``, a READ. **THE PIN MOVED
    # BECAUSE THE SURFACE MOVED, AND HERE IS THE TOOL THAT MOVED IT** -- that
    # ordering is the whole difference between recording a fact and faking
    # one, and a count pin is the class this repository is most careful about
    # precisely because bumping a number is the cheapest way to clear a test.
    #
    # IT DOES NOT WEAKEN THE CONTROL ABOVE. Both rules are run over
    # REGISTRY_WHILE_BROKEN, a two-entry reading compared BY CONTENT, so
    # nothing in the demonstration reads this number. What the number is for
    # is the sentence above it -- the defect did not move the count, which is
    # why neither rule could be replaced by a cheaper one -- and the review
    # moment that a bump forces on whoever adds a tool.
    #
    # THE REVIEW MOMENT WAS USED. The reader behind this tool answers ZERO,
    # and zero is the one number a read can get wrong in a way that looks like
    # success, so it is returned as an integer only when four independent
    # facts hold: the section present, no rows, a body holding neither text
    # nor elements, and a non-empty sibling. See ``linkedin_server/events.py``.
    #
    # 41 FROM 2026-09-05 EVENING: THREE AT ONCE, AND ALL THREE ARE READS.
    # **THE PIN MOVED BECAUSE THE SURFACE MOVED, AND HERE ARE THE TOOLS THAT
    # MOVED IT:**
    #
    #     linkedin_premium_status             premium.read_premium_surface
    #     linkedin_newsletter_subscriptions   newsletters.read_newsletter_subscriptions
    #     linkedin_notify_cost_precondition   notify_cost.read_notifications_badge
    #
    # MEASURED, NOT COUNTED BY HAND: 38 before the edit and 41 after, both off
    # ``mcp.list_tools()`` on this tree, and each new name present in the
    # sorted registry. The three readers were BUILT EARLIER THE SAME DAY and
    # NONE could be called -- they sat in
    # ``tests/test_readers_outside_dom_are_a_pinned_inventory.py`` as a pinned
    # inventory of exactly that state, and their three lines are deleted in
    # the same commit as this bump. That file's list is now EMPTY, which is
    # the end state its own docstring said could not be committed that day.
    #
    # THE REVIEW MOMENT THIS ASSERTION EXISTS TO CREATE WAS USED, per tool,
    # and the answers differ:
    #
    #   * premium publishes NO boolean and NO single number, because three
    #     states were named about Premium and one load of /premium/my-premium/
    #     refutes at most one of them. Every branch carries ``settles`` and
    #     ``leaves_open`` so a caller cannot read "entitled" and quietly
    #     assume a job-posting panel renders;
    #   * newsletters REFUSES rather than answering when the pending-invitation
    #     badge cannot be read either side of the load, or when it moved --
    #     the obligation that address inherits from /mynetwork/, discharged in
    #     the tool because the reader states it and does not do it;
    #   * notify_cost ships a PRECONDITION and spends nothing. It loads the
    #     feed and reads a nav badge; it never opens /notifications/, and
    #     ``notify_cost.cost_delta`` is deliberately left with no caller,
    #     because wiring the AFTER half is what would consume the operator's
    #     unread state.
    #
    # IT STILL DOES NOT WEAKEN THE CONTROL ABOVE, for the reason already
    # written: both rules run over REGISTRY_WHILE_BROKEN, a two-entry reading
    # compared BY CONTENT, and nothing in that demonstration reads this
    # number. That was re-checked after this bump rather than assumed --
    # ``test_both_rules_reject_the_registry_that_was_actually_measured`` was
    # run against a deliberately wrong pin and against the real one, and it
    # is the count assertion alone that moves.
    #
    # 42 FROM 2026-09-05, ~22:15 BY THE BOX: linkedin_group_memberships,
    # a READ, wiring linkedin_server/groups_page.read_group_memberships.
    # MEASURED off ``mcp.list_tools()``: 41 before the edit and 42 after.
    #
    # THE REVIEW MOMENT, USED. A predecessor wave DECLINED to wire
    # ``groups.py`` on the reasoning that *a groups tool cannot certify
    # its own cost from the page it loads* -- which is true and one step
    # short. ``linkedin_notify_cost_precondition``, wired in the bump
    # above, reads a badge on /feed/ to say something about
    # /notifications/: bracketing a load with a reading taken ELSEWHERE
    # is this package's pattern, not a workaround. So this tool loads the
    # feed, the groups page, and the feed again, and reports the cost as
    # DEGENERATE -- an honest 'I cannot measure this' rather than a zero.
    #
    # AND IT ADDS NOTHING TO ``dom.py``. Not one line. The walk this
    # reader needed was written as a ``page.evaluate`` in a probe, which
    # would have forced it into the one module ``_composer_audience_is_
    # readable`` feature-detects on; it was re-expressed with locators
    # instead and reproduced the validated split on its first live run.
    #
    # 44 FROM 2026-09-19: TWO AT ONCE, BOTH READS, AND THIS PIN WAS NOT THE
    # LAST SITE TO MOVE -- IT IS THE ONE THAT GOT MISSED.
    #
    #     linkedin_job_collections     b64580a, 11:13
    #     linkedin_creator_analytics   a8a7556, 12:42
    #
    # MEASURED OFF THE REGISTRY, NOT THE SOURCE, and not relayed from the
    # commit that moved the other sites: ``len(_tool_names())`` reads 44 on
    # this tree and both names are in it. An AST count of the ``@mcp.tool()``
    # decorator returned 46 on this same tree the same afternoon and was wrong,
    # which is why the registry is the instrument and the decorator is not.
    #
    # ``a4565cb`` moved four sites -- ``EXPECTED_TOOLS``, the count assertion
    # in ``test_server_surface.py``, the read split, and that test's own name
    # -- under a message reading "the pin was the LAST site to move". It was
    # not. This fifth site sat at forty-two, and the file left stale was the
    # one whose own comments say a bump is the cheapest way to clear a test.
    # **A COUNT PINNED IN TWO FILES IS TWO PINS**, and a rename sweep that
    # greps for the number it is moving finds the sites spelled in digits and
    # misses none; a sweep that greps for the test NAME finds only its own
    # file. The second is what happened.
    #
    # IT STILL DOES NOT WEAKEN THE CONTROL ABOVE, and that was re-measured
    # rather than assumed: with the pin standing at 42 against a real 44, this
    # test failed HERE and nowhere else -- both rule assertions ran green over
    # ``REGISTRY_WHILE_BROKEN`` first. The demonstration compares a two-entry
    # reading BY CONTENT and reads no count, so the number moving cannot reach
    # it.
    assert len(_tool_names()) == 44
