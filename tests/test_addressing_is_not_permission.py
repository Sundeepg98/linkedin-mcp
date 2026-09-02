"""Every place url-presence could stand in for permission, pinned as an inventory.

WHY THIS FILE EXISTS. On 2026-09-02 a ruling gave ``update_profile_field`` a
url while leaving it outside ``PERFORMABLE``. That broke NINE separate things,
and every one of them had been correct only because no unperformable action
happened to carry an address -- an invariant nobody had ever ruled:

    1-2  assertions in tests/test_writes.py
    3    an assertion in tests/test_server_surface.py
    4    can_hold_a_grant, which DERIVED a safety property from it
    5    _verify_after's unguarded .format, which would have raised
         AttributeError AFTER the click had already landed
    6    an assertion in tests/test_writes_nine.py
    7    mint()'s refusal -- a LIVE CONFIRM TOKEN for an action that cannot act
    8    preview()'s decision whether to mint, which turned a refusal block
         into an escaping exception
    9    a loop that silently STOPPED CHECKING one action

**When an invariant holds, ask whether anyone RULED it. If not, it is a
coincidence, and something is already depending on it.**

WHAT THIS CHECKS, AND WHY IT IS AN INVENTORY RATHER THAN A RULE. Whether a
given read of ``url_template`` is about ADDRESSING or about PERMISSION cannot
be decided mechanically -- it depends on what the surrounding code does with
the answer. So this does not try. It pins the SET of places that read those
fields, each already judged by a person, and fails when the set changes.

A new read is not a defect. It is a site somebody has to look at once and
classify, and this makes that unavoidable rather than optional.

AST, NEVER A SUBSTRING SEARCH. These names appear in docstrings, comments and
refusal strings all over ``writes.py``; a grep counts every one of them as a
use. Only real attribute reads are inventoried, which is the same lesson
``tests/test_reader_reachability.py`` was written for.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from linkedin_server import writes

PACKAGE = pathlib.Path(writes.__file__).resolve().parent
FIELDS = {"url_template", "url_pattern", "exempt_substring"}

#: (module, function, field) for every production read, each judged once.
#: EVERY ENTRY IS ADDRESSING. If a permission question ever needs one of these
#: fields, it belongs in :func:`writes.grant_is_possible` instead, which is the
#: one place allowed to combine them.
EXPECTED_READS: set[tuple[str, str, str]] = {
    # The url gate itself: validating a url is the addressing question.
    ("writes.py", "assert_write_url", "url_template"),
    ("writes.py", "assert_write_url", "url_pattern"),
    ("writes.py", "assert_write_url", "exempt_substring"),
    # Building the url to navigate to. All guarded with `or ""`.
    ("writes.py", "observe", "url_template"),
    ("writes.py", "perform", "url_template"),
    ("writes.py", "_assert_landed_on_target", "url_template"),
    # The preview's `where.url`, and its UNMEASURED sentence when there is none.
    ("writes.py", "_render", "url_template"),
    # The post-click verification: a guard added 2026-09-02, and the .format it
    # protects. Before the guard this would have raised AttributeError after
    # the write had already landed.
    ("writes.py", "_verify_after", "url_template"),
    # mint's SECOND refusal -- performable with nothing to act on. Kept
    # separate from the membership refusal because a caller needs to know
    # WHICH, and this one fires before the click.
    ("writes.py", "mint", "url_template"),
    # The one place permitted to combine addressing with permission.
    ("writes.py", "grant_is_possible", "url_template"),
    # server_info's `has_a_measured_surface`, which genuinely IS about the url.
    # Its neighbour `can_hold_a_grant` asked the same way until 2026-09-02 and
    # was wrong to; it now calls grant_is_possible.
    ("server.py", "linkedin_server_info", "url_template"),
}


def _reads() -> set[tuple[str, str, str]]:
    """Every production read of the three fields, by enclosing function."""
    found: set[tuple[str, str, str]] = set()
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute) or node.attr not in FIELDS:
                continue
            # NARROWED, NOT getattr'd with a default: ast.walk yields AST and
            # only some subclasses carry positions. A default would silently
            # attribute every read to <module>, which is the same failure this
            # file exists to catch, one level down.
            if not isinstance(node, (ast.expr, ast.stmt)):
                continue
            enclosing = "<module>"
            best = -1
            for fn in functions:
                end = fn.end_lineno or fn.lineno
                if fn.lineno <= node.lineno <= end and fn.lineno > best:
                    enclosing, best = fn.name, fn.lineno
            found.add((path.name, enclosing, node.attr))
    return found


def test_every_production_read_of_a_url_field_has_been_classified():
    """A new read is a site somebody must classify, not a defect.

    THE FAILURE MESSAGE IS THE POINT. A set comparison names the site that
    appeared or vanished; a count would say only that something moved, and two
    changes that cancelled would pass -- which is exactly how site nine hid.
    """
    actual = _reads()
    added = actual - EXPECTED_READS
    removed = EXPECTED_READS - actual
    assert not added, (
        "NEW read(s) of a url field, unclassified: "
        + str(sorted(added))
        + " -- decide for each whether it is ADDRESSING (fine) or PERMISSION "
        "(it must call writes.grant_is_possible instead), then add it here."
    )
    assert not removed, (
        "read(s) disappeared: "
        + str(sorted(removed))
        + " -- if the behaviour moved, move the entry; if it was deleted, "
        "delete the entry. An inventory that quietly over-lists is the same "
        "defect as one that under-lists."
    )


def test_the_inventory_is_not_vacuous():
    """A pinned set that matched nothing would pass forever.

    The control on the control: the walk must actually find reads, and it must
    find them inside NAMED functions rather than attributing everything to
    <module>, which is what a broken position lookup would produce.
    """
    actual = _reads()
    assert len(actual) >= 10, actual
    assert all(fn != "<module>" for _, fn, _ in actual), sorted(actual)


def test_only_one_function_may_combine_addressing_with_permission():
    """``grant_is_possible`` is the single place the two questions meet.

    Three consumers each computed "could this act?" from the url alone --
    mint's refusal, preview's decision, and can_hold_a_grant -- and they failed
    three different ways when the coincidence broke. They now share this.

    If a fourth place ever needs both facts, it calls this rather than
    recomputing them, and this test is where that gets noticed.
    """
    import inspect

    source = inspect.getsource(writes.grant_is_possible)
    assert "PERFORMABLE" in source
    assert "url_template" in source

    # AND IT ANSWERS BOTH HALVES -- ON A SPEC BUILT FOR THE PURPOSE, because
    # the registry no longer contains a discriminating one.
    #
    # THIS IS WORTH THE SENTENCE. Until 2026-09-02 update_profile_field WAS
    # the addressed-but-unperformable case, and it was the reason this
    # assertion could tell the two halves apart. Then it shipped, and every
    # addressed action became performable again -- so a test that kept using
    # the registry would have gone on passing while no longer discriminating
    # anything. That is the permissive-skip shape from section 93, arriving in
    # a test whose subject is precisely that defect.
    #
    # So the pair is CONSTRUCTED. An addressed spec whose action is not in
    # PERFORMABLE must be refused a grant, and the only thing that can refuse
    # it is the membership half.
    import dataclasses

    real = writes.spec_for_action("save_job")
    assert writes.grant_is_possible(real) is True

    addressed_but_unperformable = dataclasses.replace(
        real, action="not_a_sanctioned_action"
    )
    assert addressed_but_unperformable.url_template is not None
    assert addressed_but_unperformable.action not in writes.PERFORMABLE
    assert writes.grant_is_possible(addressed_but_unperformable) is False

    # And the mirror: performable but unaddressed is refused by the other half.
    performable_but_unaddressed = dataclasses.replace(
        real, url_template=None
    )
    assert performable_but_unaddressed.action in writes.PERFORMABLE
    assert writes.grant_is_possible(performable_but_unaddressed) is False


def test_the_three_consumers_call_the_predicate_rather_than_recompute_it():
    """THE HALF THE INVENTORY CANNOT SEE, and it was missing until it was shown.

    The inventory above catches a read APPEARING or VANISHING. It cannot catch
    a read that stays in the same function and CHANGES MEANING -- which is
    exactly what site four was: ``can_hold_a_grant`` reverting from the shared
    predicate to ``url_template is not None`` leaves the inventory identical.

    Found by applying the register's second law to this file on the day it was
    written: an instrument enters only if it has been shown failing, and the
    first mutation it was shown against produced NOTHING. A new unclassified
    read failed loudly; the proxy coming back did not. So this is the other
    half, and it is here because the demonstration demanded it rather than
    because anybody predicted it.
    """
    import inspect

    from linkedin_server import server

    # server_info's field is one line inside a large function, so it is read
    # through a window; preview is read WHOLE, because a window into a module
    # is sized by guesswork and this test failed on a clean tree the first time
    # for exactly that reason -- preview's docstring is longer than the window.
    info = inspect.getsource(server)
    start = info.index('"can_hold_a_grant"')
    assert "grant_is_possible" in info[start : start + 200], (
        "server_info's can_hold_a_grant no longer calls grant_is_possible -- "
        "it is deciding 'could this act?' for itself again, which is how a "
        "live token appeared for an action that cannot act."
    )

    preview_source = inspect.getsource(writes.preview)
    assert "grant_is_possible" in preview_source, (
        "preview no longer asks grant_is_possible whether to mint. When it "
        "decided from the url alone, mint's refusal escaped as an exception "
        "where a refusal BLOCK belongs, and the caller got a traceback "
        "instead of a gate explaining itself."
    )

    # mint is the deliberate exception and must NOT be consolidated into the
    # predicate: it needs the two refusals separately, because a caller has to
    # know WHICH applies. Asserted so a future tidy-up has to argue with it.
    mint_source = inspect.getsource(writes.mint)
    assert "PERFORMABLE" in mint_source
    assert "url_template" in mint_source
    assert "grant_is_possible" not in mint_source


@pytest.mark.parametrize("action", sorted({"send_message", "set_open_to_work"}))
def test_no_unperformable_action_can_hold_a_grant(action):
    """The layer itself, asserted on the artifact rather than on the report.

    ``can_hold_a_grant`` in ``linkedin_server_info`` was corrected to say "url
    AND membership" while ``mint`` went on deciding from the url alone. The
    description was right and the layer was gone, and a live confirm token
    existed for an action that cannot act.

    A PROPERTY IS NOT TESTED BY ASSERTING WHAT THE SYSTEM SAYS ABOUT IT.
    """
    spec = writes.spec_for_action(action)
    assert spec.action not in writes.PERFORMABLE
    assert writes.grant_is_possible(spec) is False
