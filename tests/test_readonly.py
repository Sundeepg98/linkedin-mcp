"""The read-only invariant, checked rather than claimed.

Every check here is shown FAILING on a deliberately bad sample before it is
trusted on the real package. A check that cannot fail certifies nothing, and
a read-only guarantee backed by a check that cannot fail is worse than no
guarantee at all -- it manufactures confidence.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from linkedin_server import dom, readonly
from linkedin_server.errors import WriteAttemptError

PACKAGE_DIR = Path(readonly.__file__).resolve().parent
MODULES = sorted(PACKAGE_DIR.glob("*.py"))


# ---------------------------------------------------------------------------
# 1. No mutating Playwright call anywhere in the package
# ---------------------------------------------------------------------------


def test_there_are_modules_to_scan():
    """Guards against a scan that passes because it found nothing to look at."""
    assert len(MODULES) >= 9, [m.name for m in MODULES]


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_no_module_contains_an_UNSANCTIONED_mutating_call(module: Path):
    """Every mutating call in the package is one of the ones named in advance.

    THIS CHECK CHANGED SHAPE ON 2026-08-23 AND DID NOT WEAKEN. It used to assert
    the scan came back EMPTY for every module. The package now contains exactly
    one mutating call -- the click in ``writes.perform`` -- so an empty-scan
    assertion could only have been kept by teaching the scanner to stop seeing
    it, which would have destroyed the only instrument that can see the next
    one.

    So the SCAN is untouched and unconditional, and what is asserted is the
    partition: nothing outside ``readonly.SANCTIONED_MUTATIONS``. The tests
    below hold that list to being complete, exact, and narrow.
    """
    source = module.read_text(encoding="utf-8")
    _sanctioned, unsanctioned = readonly.partition_mutation_hits(
        f"linkedin_server/{module.name}", source
    )
    assert unsanctioned == [], (
        f"{module.name} contains calls that could change state and are not "
        f"sanctioned: {unsanctioned}. If the call is genuinely a read, waive "
        "that single line with a trailing '# readonly-ok' so the waiver shows "
        "up in the diff. If it is genuinely a write, it needs an entry in "
        "readonly.SANCTIONED_MUTATIONS and the operator's say-so -- adding "
        "one is the review moment this check exists to create."
    )


def test_the_sanctioned_list_is_exactly_these_three_calls():
    """The allowlist, read out loud, so widening it is visible in a diff.

    A guard whose allowlist is checked only for "does it cover what we found"
    grows by one entry at a time and nobody notices. This pins the CONTENTS.

    IT GREW BY ONE ON 2026-08-26, from one entry to two, which is precisely
    the event this test exists to make visible. The second is on a READ path,
    which is why it had to argue for itself rather than being waved through:

    * ``writes.perform`` -- the write click, behind the two-call token gate;
    * ``dom.activate_messaging_filter`` -- activates one of seven NAMED filter
      pills on the messaging surface. All six were measured as buttons with no
      href, so that surface is unreachable by navigation. A pill sends nothing
      and changes nothing on LinkedIn's servers, so counted by EFFECT -- which
      is how this family classifies everything -- a view filter is a read. And
      ``linkedin_open_messaging`` already opens somebody's conversation and may
      fire a read receipt: refusing the lesser act while performing the greater
      one is backwards.

    IT GREW BY ONE AGAIN ON 2026-09-01, from two to three, and this one is
    NOT A CLICK. The previous version of this docstring ended "A THIRD click
    fails here whatever its justification, and has to come and write one" --
    so here it is, written.

    * ``writes.perform`` -- ONE ``page.fill``, draining a queue exactly as the
      click does. THE QUEUE IS THE DESIGN: the scanner counts CALL SITES, so
      one drain point keeps the guarantee this list exists to give -- there is
      one place in this package that types, and a reviewer reads it.

    WHAT MAKES IT ARGUABLE RATHER THAN A WIDENING. The text is never composed
    by this server: it is a slice of the GRANT's canonical target, the same
    string the preview printed and the token was minted against, and
    ``consume`` has already refused any token whose target did not match. And
    a fill is not a publish -- typing into a composer sends nothing. The act
    that reaches LinkedIn is the click after it, gated separately on a MEASURED
    transition: the publish control is drawn disabled on an empty composer, so
    a fill that worked is observable and one that did not is refused.

    WHAT THE PACKAGE STOPPED BEING ABLE TO SAY. "It types nothing" was true,
    was printed in three places, and is now false. Those places were corrected
    in the same commit rather than left to be found.

    THE COUNT IS STILL PINNED, which is the part that matters. A FOURTH entry
    fails here whatever its justification, and has to come and write one.
    """
    assert readonly.SANCTIONED_MUTATIONS == (
        ("linkedin_server/writes.py", "perform", "click"),
        ("linkedin_server/dom.py", "activate_messaging_filter", "click"),
        ("linkedin_server/writes.py", "perform", "fill"),
    )
    assert len(readonly.SANCTIONED_MUTATIONS) == 3
    # EXACTLY ONE non-click, asserted separately. The count alone would let a
    # click be swapped for a fill without moving the number, and those are
    # different capabilities: a click presses what is already there, a fill
    # puts his words on a page.
    kinds = sorted(kind for _p, _f, kind in readonly.SANCTIONED_MUTATIONS)
    assert kinds == ["click", "click", "fill"], kinds


def test_every_sanctioned_entry_is_actually_present():
    """The other direction: a stale entry is as bad as a missing one.

    An allowlist keyed on a function that no longer exists, or on a call that
    was removed, quietly grants permission to a future edit that recreates the
    name. Both halves are asserted, so the list cannot rot either way.
    """
    found: set[tuple[str, str, str]] = set()
    for module in MODULES:
        rel = f"linkedin_server/{module.name}"
        source = module.read_text(encoding="utf-8")
        for lineno, kind, _line in readonly.scan_source_for_mutations(source):
            found.add((rel, readonly.enclosing_function(source, lineno), kind))
    assert set(readonly.SANCTIONED_MUTATIONS) == found, (
        "the sanctioned list and what the scanner actually finds have "
        f"diverged. list={sorted(readonly.SANCTIONED_MUTATIONS)} "
        f"found={sorted(found)}"
    )


def test_the_package_contains_exactly_as_many_mutating_calls_as_are_listed():
    """COUNT, not just membership -- and this closes a real hole.

    ``test_every_sanctioned_entry_is_actually_present`` compares SETS, so it
    cannot see a duplicate: a SECOND click added inside ``perform`` is the same
    ``(path, function, kind)`` triple as the first and passes a set comparison
    unchanged. That is the hardest case, because it is in the sanctioned file,
    in the sanctioned function, of the sanctioned kind -- and it must still
    fail, because the list admits ONE call and not a licence.

    Shown failing on exactly that edit in
    ``test_writes.py::test_a_second_click_inside_perform_is_still_caught``.
    """
    total = sum(
        len(readonly.scan_source_for_mutations(m.read_text(encoding="utf-8")))
        for m in MODULES
    )
    # TWO from 2026-08-26, THREE from 2026-09-01 when one page.fill entered.
    # The equality against the allowlist LENGTH is the load-bearing half and
    # is unchanged -- an unlisted mutating call still fails whatever its kind
    # -- while the literal is what makes growth visible in a diff.
    assert total == len(readonly.SANCTIONED_MUTATIONS) == 3, total


def test_the_partition_conserves_every_hit():
    """Nothing is dropped on the way through the filter.

    The failure this prevents is a partition that quietly swallows a hit --
    which would look identical to a clean package from every caller's side.
    """
    for module in MODULES:
        source = module.read_text(encoding="utf-8")
        sanctioned, unsanctioned = readonly.partition_mutation_hits(
            f"linkedin_server/{module.name}", source
        )
        assert (
            sorted(sanctioned + unsanctioned)
            == sorted(readonly.scan_source_for_mutations(source))
        ), module.name


@pytest.mark.parametrize(
    "label, path, source",
    [
        # The sanctioned call, but in the wrong FILE.
        (
            "wrong file",
            "linkedin_server/dom.py",
            "async def perform(page, grant):\n    await page.click('b')\n",
        ),
        # The sanctioned file and kind, but the wrong FUNCTION.
        (
            "wrong function",
            "linkedin_server/writes.py",
            "async def _helper(page, grant):\n    await page.click('b')\n",
        ),
        # The sanctioned file and function, but the wrong KIND.
        #
        # THIS CASE USED page.fill UNTIL 2026-09-01, when fill inside
        # perform became sanctioned. It is RE-AIMED rather than deleted:
        # the property under test is that the KIND half of the triple
        # discriminates at all, and dropping the case because its example
        # got promoted would remove the only proof of that half.
        # page.type is what a future edit reaches for once typing is
        # permitted in principle, which makes it the right example now.
        (
            "wrong kind",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n    await page.type('#n', 'x')\n",
        ),
        # A SECOND WRONG KIND, same day. Two of them, because the entry
        # that arrived buys exactly fill -- and press and keyboard are the
        # two verbs that would let somebody type without calling it typing.
        (
            "wrong kind, keyboard",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n    await page.press('#n', 'a')\n",
        ),
        # The sanctioned triple in every respect EXCEPT that the call is
        # buried one scope down. Attribution is innermost, so the closure is
        # named as itself and inherits nothing.
        (
            "nested inside the sanctioned function",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n"
            "    async def _go():\n"
            "        await page.click('b')\n"
            "    return _go\n",
        ),
        # Module level, inside the sanctioned file. No enclosing function at
        # all, so nothing to match.
        (
            "module level",
            "linkedin_server/writes.py",
            "page.click('b')\n",
        ),
    ],
)
def test_the_exception_does_not_widen(label, path, source):
    """SHOWN FAILING on the five ways this exemption could be stretched.

    Each of these is one edit away from the real entry, and every one of them
    has to come back UNSANCTIONED. Without this the triple could be reduced to
    "a click somewhere in writes.py" and no test would notice.
    """
    sanctioned, unsanctioned = readonly.partition_mutation_hits(path, source)
    assert sanctioned == [], (label, sanctioned)
    assert unsanctioned, (label, "the scanner did not even see it")


def test_the_real_entry_IS_admitted():
    """THE POSITIVE CONTROL for all five refusals above.

    Five tests asserting "not sanctioned" pass perfectly on a partition that
    sanctions nothing at all. This is the one that would fail if it did.
    """
    source = "async def perform(page, grant):\n    await page.click('b')\n"
    sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", source
    )
    assert len(sanctioned) == 1, sanctioned
    assert unsanctioned == []


@pytest.mark.parametrize(
    "spelling",
    [
        "linkedin_server/writes.py",
        "linkedin_server\\writes.py",
        "./linkedin_server/writes.py",
    ],
)
def test_the_path_is_matched_in_every_spelling_a_checkout_produces(spelling):
    """Windows separators and a leading ./ must not silently un-sanction it.

    Three CI cells, two of them posix and one Windows. A path comparison that
    worked on one and not the others would turn this check into a test that
    passes for the wrong reason on two thirds of the matrix.
    """
    source = "async def perform(page, grant):\n    await page.click('b')\n"
    sanctioned, _ = readonly.partition_mutation_hits(spelling, source)
    assert len(sanctioned) == 1, spelling


def test_the_mutation_scanner_catches_a_planted_write():
    """The scanner, shown failing. Without this the check above proves nothing."""
    bad = (
        "async def apply(page):\n"
        "    await page.click('#easy-apply')\n"
        "    await page.fill('#note', 'hire me')\n"
        "    await page.request.post('https://www.linkedin.com/voyager/api/x')\n"
    )
    hits = readonly.scan_source_for_mutations(bad)
    kinds = {kind for _, kind, _ in hits}
    assert {"click", "fill", "http_post"} <= kinds, hits


def test_nothing_in_this_package_can_reach_a_file_input():
    """The composer draws two file inputs. Nothing here may touch them.

    MEASURED 2026-09-01 on /messaging/compose/: ``file_inputs: 2``, named
    ``Attach a file for your draft conversation`` and ``Attach an image for
    your draft conversation``, both in ``form#0``. They sit on a surface this
    server now loads, beside a Send control it is being built to press.

    ``set_input_files`` is on :data:`_MUTATION_CALL_PATTERNS` and is NOT on
    ``SANCTIONED_MUTATIONS``, so the scanner would catch one. This asserts the
    same thing from the other side and by NAME, because "nobody has written
    that call" is a fact about today and this is a fact about the rule: a
    control nothing reaches today is one refactor from being reachable.

    UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in
    a box; a file input puts a FILE from this machine into somebody else's
    inbox, chosen by a path string. Nothing in this package should be one edit
    away from that, and the operator has never been asked about it.
    """
    for module in MODULES:
        source = module.read_text(encoding="utf-8")
        for lineno, kind, line in readonly.scan_source_for_mutations(source):
            assert kind != "set_input_files", (module.name, lineno, line)

    # AND THE PATTERN ITSELF MUST STILL BITE, or the loop above is a loop over
    # nothing. A rule that cannot fire certifies nothing.
    planted = (
        "async def send(page):\n"
        "    await page.set_input_files('#f', p)\n"
    )
    hits = readonly.scan_source_for_mutations(planted)
    assert [kind for _line, kind, _src in hits] == ["set_input_files"], hits

    # It is not on the allowlist, so even inside perform it would be refused.
    assert not any(
        kind == "set_input_files" for _p, _f, kind in readonly.SANCTIONED_MUTATIONS
    )


def test_evaluate_is_flagged_unless_explicitly_waived():
    """An unwaived evaluate() must trip the scanner; a waived one must not."""
    unwaived = "result = await page.evaluate(SOME_SCRIPT)\n"
    assert readonly.scan_source_for_mutations(unwaived)

    waived = "result = await page.evaluate(SOME_SCRIPT)  # readonly-ok\n"
    assert readonly.scan_source_for_mutations(waived) == []


def test_only_dom_module_waives_evaluate():
    """The waiver is a narrow allowance, not a habit spreading through the code."""
    waived_in: dict[str, int] = {}
    for module in MODULES:
        count = sum(
            1
            for line in module.read_text(encoding="utf-8").splitlines()
            if line.strip().endswith("# readonly-ok")
        )
        if count:
            waived_in[module.name] = count
    assert set(waived_in) <= {"dom.py"}, waived_in
    # SIX FROM 2026-08-30, up from four. The budget is what stops an
    # evaluate() waiver spreading: every one of them is a place where "we
    # only call read methods in Python" stops being a sufficient argument,
    # so the number is pinned and a new one has to move it in a reviewable
    # diff. The fourth is CENSUS_JS, read by dom.read_surface_census.
    #
    # THE FIFTH AND SIXTH were added to diagnose a tracker read returning zero
    # rows from a page carrying four job-row anchors, eight times out of eight.
    # dom.harvest_census re-runs HARVEST_LINKED_CARDS_JS under a flag -- the
    # SAME script, so the diagnostic cannot drift from the walk it describes --
    # and dom.read_tracker_row_shape runs TRACKER_ROW_SHAPE_JS, which reports
    # tag names and character counts and no text at all.
    #
    # A THIRD WAS PROPOSED AND NOT SPENT: main's textContent length is read
    # through locator.text_content(), Playwright's own API, because a waiver
    # that a plain call replaces is a waiver nobody should be asked to review.
    #
    # SEVEN FROM 2026-08-31, and this is the first waiver on this list spent to
    # buy a PRIVACY guarantee rather than a reading. INVITE_NEEDLE_JS, run by
    # dom.read_invitation_surface.
    #
    # The other six count controls, and every one of them could in principle
    # have been a locator chain -- which is the test the paragraph above
    # applies, and it is why the third was refused. THIS ONE FAILS THAT TEST IN
    # THE OTHER DIRECTION. It has to COMPARE an aria-label against a needle,
    # and on this surface the label IS A THIRD PARTY'S NAME. A locator chain
    # doing that comparison in Python would have to fetch the label into this
    # process first, and the operator's 2026-08-31 ruling on invitation
    # targeting is that this server may RECEIVE one identity per call and must
    # not persist it -- no identity in any file, log, cache or audit. A name
    # that reaches Python can reach a traceback, an exception message, a cache
    # key or an audit line, and no care downstream un-rings that.
    #
    # So the waiver is what makes "never stored" ENFORCEABLE rather than
    # promised: the comparison happens in the page and the script returns three
    # numbers -- total, matches, index -- and no label, no name, and no
    # fragment of either. The cheap side of the usual trade is the unacceptable
    # one here, which is the argument, and it is the only reason this number
    # moved.
    #
    # EIGHT FROM 2026-08-31, and it is the SECOND waiver spent on privacy
    # rather than on a reading -- EDITOR_FIELDS_JS, run by
    # dom.read_self_owned_editor_fields. It is the inverse of the seventh: that
    # one keeps a name OUT of this process, this one lets a name IN, and both
    # need the work done in the page for the same structural reason.
    #
    # WHY A LOCATOR CHAIN CANNOT BUY IT. The read is "every control inside the
    # nearest dialog ancestor of the one control named Save". Playwright can
    # find descendants of a known element and it cannot walk UP from one --
    # there is no locator for closest(). Doing it in Python would mean
    # enumerating every dialog on the page, reading each one's controls, and
    # deciding containment from the two lists, which is the adjacency-guessing
    # that the container measurement was taken to end. And the counting rule
    # this reader lives by -- exactly one anchor or it refuses -- has to be
    # decided over the whole document at one instant, not across a series of
    # separate locator calls against a page that is still settling.
    #
    # NINE FROM 2026-08-31, and it is the second waiver on this list spent
    # to buy a PRIVACY guarantee. ACTIVITY_ITEMS_JS, run by
    # dom.read_own_activity_items, compares an author string against the
    # page's own h1 and returns a BOOLEAN. A locator chain doing that
    # comparison in Python would have to fetch both strings into this
    # process, which is the one thing the ruling on that reader forbids --
    # so it fails the cheap-alternative test in the same direction
    # INVITE_NEEDLE_JS does, and for the same reason.
    # TEN FROM 2026-09-01, up from nine. The tenth is SDUI_ACTIONS_JS, and it
    # is the one waiver that exists to make a RULING measurable rather than to
    # read a page: the operator ruled that a click issuing no `ServerRequest`
    # is by effect a read, so something has to count them, and the counting
    # can only happen inside the page. It returns INTEGERS -- the profile's
    # flight payload is ~1.09 MB and is where his identity lives, which is why
    # the sanitised fixtures here carry zero script characters.
    assert waived_in.get("dom.py", 0) <= 10, waived_in


# ---------------------------------------------------------------------------
# 2. The injected JavaScript only reads
# ---------------------------------------------------------------------------

INJECTED_SCRIPTS = {
    "HARVEST_LINKED_CARDS_JS": dom.HARVEST_LINKED_CARDS_JS,
    "HARVEST_BLOCK_CARDS_JS": dom.HARVEST_BLOCK_CARDS_JS,
    "READ_PROFILE_JS": dom.READ_PROFILE_JS,
    # 2026-08-26. The surface census reads the CONTROLS on a page rather than
    # its content, which means it is the one script here that goes looking at
    # buttons -- so it is the one whose scan matters most, and it is scanned by
    # exactly the same check as the other three rather than by a special case.
    "CENSUS_JS": dom.CENSUS_JS,
    # 2026-08-30. The row-shape reader, which climbs from a job-row anchor and
    # reports each level as a tag name and two character counts. It exists
    # purely to describe a page this package could not read, and it is held to
    # the same scan as the rest. It also carries the strictest privacy rule in
    # the module: no text and no attribute value leaves it, because a tracker
    # row names a company and a job.
    "TRACKER_ROW_SHAPE_JS": dom.TRACKER_ROW_SHAPE_JS,
    # 2026-09-01. The SDUI action counter. Declared here for the ordinary
    # reason -- an executed script that is not declared is one nobody reviewed
    # -- and it needs the scan more than most, because it is the only script
    # in this module that reads the FLIGHT PAYLOAD rather than the DOM. That
    # payload is ~1.09 MB of his profile, so the script returns integers and a
    # hit count and nothing else; there is no path by which a payload string
    # reaches this process.
    "SDUI_ACTIONS_JS": dom.SDUI_ACTIONS_JS,
    # 2026-08-31. The invitation needle. It is declared here for the ordinary
    # reason -- every script this package executes is scanned, and one that is
    # not declared is one nobody reviewed -- and declaring it ENROLS it in
    # test_every_script_this_package_executes_cannot_mutate, which is the
    # point of the list rather than a side effect of joining it.
    #
    # It is also the only script here whose OUTPUT shape is part of the
    # boundary rather than only its input. It reads aria-labels carrying real
    # people's names and returns three integers, so the privacy property is
    # structural: there is no string in the return value to leak. The test that
    # certifies THAT lives with the reader, not here.
    "INVITE_NEEDLE_JS": dom.INVITE_NEEDLE_JS,
    # 2026-08-31. The self-owned editor reader. Declared for the ordinary
    # reason -- an undeclared script is one nobody reviewed -- and declaring it
    # ENROLS it in test_every_script_this_package_executes_cannot_mutate.
    #
    # It is the one script here whose OUTPUT is deliberately LESS shaped than
    # the census's: it publishes accessible names ungated, on the operator's
    # 2026-08-31 ruling that a container measured to be his own holds no third
    # party. That makes the mutation scan more load-bearing rather than less --
    # a script that both reads labels and could touch the page would be the
    # worst combination available here -- and it is why the scan is asserted a
    # second time in tests/test_editor_fields.py rather than only from this
    # list.
    "EDITOR_FIELDS_JS": dom.EDITOR_FIELDS_JS,
    # 2026-08-31. The own-activity item reader. Declared for the ordinary
    # reason -- an undeclared script is one nobody reviewed -- and declaring
    # it ENROLS it in test_every_script_this_package_executes_cannot_mutate.
    #
    # It is the ninth, and it is the FIRST script here that publishes a REAL
    # IDENTIFIER: item urns, unshaped, because a substituted urn is <urn> and
    # that is the useless answer the reader exists to replace. Everything
    # else it returns is an integer or a boolean, and the author strings it
    # compares never leave the document -- so its privacy property, like
    # INVITE_NEEDLE_JS's, is structural rather than a matter of shaping on
    # the way out. The gate that decides whether the urn list crosses at all
    # lives INSIDE this script, which is why the scan matters here: a script
    # that both holds a privacy gate and could touch the page would be the
    # worst combination available. Asserted a second time in
    # tests/test_activity_items.py.
    "ACTIVITY_ITEMS_JS": dom.ACTIVITY_ITEMS_JS,
}


def evaluate_targets(source: str) -> list[tuple[str, str, int]]:
    """Return what every ``.evaluate(...)`` in ``source`` is handed, by AST.

    Each entry is ``(kind, value, lineno)`` where kind is ``"name"`` (a
    module-level constant, value is its identifier) or ``"inline"`` (a literal
    string, value is the string itself). An argument that is neither -- an
    f-string, a concatenation, a function call, a variable built at runtime --
    comes back as ``"unresolvable"``, because a script this check cannot read
    is a script it cannot certify.
    """
    out: list[tuple[str, str, int]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr.startswith("evaluate")):
            continue
        if not node.args:
            out.append(("unresolvable", "<no argument>", node.lineno))
            continue
        first = node.args[0]
        if isinstance(first, ast.Name):
            out.append(("name", first.id, first.lineno))
        elif isinstance(first, ast.Constant) and isinstance(first.value, str):
            out.append(("inline", first.value, first.lineno))
        else:
            out.append(("unresolvable", type(first).__name__, first.lineno))
    return out


def _scripts_this_package_executes() -> dict[str, str]:
    """The scripts actually reaching ``evaluate``, resolved from the call sites."""
    import importlib

    executed: dict[str, str] = {}
    for module in MODULES:
        targets = evaluate_targets(module.read_text(encoding="utf-8"))
        if not targets:
            continue
        imported = importlib.import_module(f"linkedin_server.{module.stem}")
        for kind, value, lineno in targets:
            label = f"{module.stem}:{lineno}"
            if kind == "inline":
                executed[label] = value
                continue
            if kind == "unresolvable":
                raise AssertionError(
                    f"{module.name}:{lineno} passes {value} to evaluate(). This "
                    "check can only certify a script it can read, so an "
                    "injected script must be a module-level constant or a "
                    "literal."
                )
            script = getattr(imported, value, None)
            assert isinstance(script, str), (
                f"{module.name}:{lineno} passes {value} to evaluate() and it is "
                f"not a module-level string ({type(script).__name__})."
            )
            executed[f"{label} {value}"] = script
    return executed


#: Resolved from the CALL SITES, not from a naming convention. See below.
EXECUTED_SCRIPTS = _scripts_this_package_executes()


@pytest.mark.parametrize("name", sorted(EXECUTED_SCRIPTS))
def test_every_script_this_package_executes_cannot_mutate(name: str):
    """The scan, bound to what RUNS rather than to what is named a certain way.

    The previous version of this check scanned a hand-written dict of three
    names, guarded by a second check that enumerated ``dir(dom)`` for names
    ending in ``_JS``. Both sets happened to coincide, and nothing anywhere
    looked at the first argument of an ``evaluate`` call -- so a script named
    without the suffix could be injected and no test would ever read it. A cold
    review demonstrated exactly that: a constant called ``EVIL_INLINE``,
    carrying ``localStorage.setItem`` and ``fetch(``, passed at the existing
    call site, shipped with the whole suite green.
    """
    found = readonly.scan_js_for_mutations(EXECUTED_SCRIPTS[name])
    assert found == [], f"{name} contains mutating tokens: {found}"


def test_the_scripts_executed_are_exactly_the_ones_declared():
    """No script runs that this module does not know the name of.

    TWO COUNTS, AND THEY ARE DIFFERENT QUESTIONS. The NAMES must match the
    declaration exactly -- an undeclared script is the thing this file exists
    to catch. The number of CALL SITES is pinned separately, and it is allowed
    to exceed the number of scripts: one script may legitimately run from more
    than one place.

    SIX FROM 2026-08-30, up from four, and both additions are one script run a
    second time rather than new surface area. ``dom.harvest_census`` runs
    ``HARVEST_LINKED_CARDS_JS`` -- the SAME script the harvest runs, under a
    flag, precisely so a diagnostic cannot drift from the walk it describes --
    and ``dom.read_tracker_row_shape`` runs ``TRACKER_ROW_SHAPE_JS``.

    SEVEN FROM 2026-08-31, and unlike the two before it this one IS new
    surface area: ``INVITE_NEEDLE_JS``, run once from
    ``dom.read_invitation_surface``. The argument for spending an evaluate
    waiver on it is with the budget in
    ``test_only_dom_module_waives_evaluate`` -- in short, it is the only
    script here that exists to keep a value OUT of this process rather than to
    bring one in.

    EIGHT FROM 2026-08-31, new surface area again: ``EDITOR_FIELDS_JS``, run
    once from ``dom.read_self_owned_editor_fields``. It is the mirror of the
    seventh -- that one keeps an identity out of this process, this one lets
    accessible names in, ungated, from inside a container measured to be the
    operator's own. Its waiver argument is with the budget in
    ``test_only_dom_module_waives_evaluate``.

    NINE FROM 2026-08-31, new surface area again: ``ACTIVITY_ITEMS_JS``, run
    once from ``dom.read_own_activity_items``. It is the third of these three
    that exists for a privacy reason rather than a reading reason, and it is
    the only one that does BOTH halves at once -- it keeps two name strings out
    of this process AND publishes a real identifier, and which of those two it
    does is decided by a gate inside the script itself.
    """
    names = {label.split()[-1] for label in EXECUTED_SCRIPTS if " " in label}
    assert names == set(INJECTED_SCRIPTS), names
    assert len(EXECUTED_SCRIPTS) == 10, sorted(EXECUTED_SCRIPTS)


def test_the_call_site_resolver_sees_a_script_hiding_behind_a_name():
    """The control, and the exact attack the cold review used.

    ``EVIL_INLINE`` does not end in ``_JS``, so the old convention-based check
    was blind to it. The resolver reports it because it reads the call.
    """
    planted = (
        "EVIL_INLINE = \"() => { fetch('https://evil.example/x'); }\"\n"
        "async def read(page):\n"
        "    return await page.evaluate(EVIL_INLINE, cfg)  # readonly-ok\n"
    )
    assert evaluate_targets(planted) == [("name", "EVIL_INLINE", 3)]


def test_the_call_site_resolver_refuses_a_script_it_cannot_read():
    """A script assembled at runtime cannot be certified, so it is rejected."""
    planted = (
        "async def read(page):\n"
        "    return await page.evaluate(BASE + tail())  # readonly-ok\n"
    )
    kinds = {kind for kind, _, _ in evaluate_targets(planted)}
    assert kinds == {"unresolvable"}, evaluate_targets(planted)


def test_the_js_scanner_catches_a_planted_mutation():
    """The JS scanner, shown failing."""
    bad = """
    () => {
      document.querySelector('#apply').click();
      document.querySelector('#note').value = 'hi';
      fetch('/voyager/api/whatever', {method: 'POST'});
    }
    """
    found = readonly.scan_js_for_mutations(bad)
    assert ".click(" in found and ".value =" in found and "fetch(" in found, found


def test_every_injected_script_is_scanned():
    """Catches a fourth script being added to dom.py without a scan."""
    declared = {
        name
        for name in dir(dom)
        if name.endswith("_JS") and isinstance(getattr(dom, name), str)
    }
    assert declared == set(INJECTED_SCRIPTS), declared


# ---------------------------------------------------------------------------
# 3. The navigation allowlist
# ---------------------------------------------------------------------------

ALLOWED = [
    "https://www.linkedin.com/analytics/profile-views/",
    "https://www.linkedin.com/me/profile-views/",
    "https://www.linkedin.com/jobs-tracker/?stage=saved",
    "https://www.linkedin.com/jobs-tracker/?stage=applied",
    # THE THIRD STAGE, allowed 2026-08-26. The tab LinkedIn labels "In
    # Progress" is addressed as ``?stage=draft`` -- the token read off
    # LinkedIn's own anchors in the tracked fixture jobs_tracker_row.html,
    # not guessed from the label, which is a different word.
    "https://www.linkedin.com/jobs-tracker/?stage=draft",
    "https://www.linkedin.com/jobs/search/?keywords=node&f_WT=2",
    "https://www.linkedin.com/in/me/",
    "https://www.linkedin.com/in/alex-r/details/skills/",
    "https://www.linkedin.com/notifications/",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/login",
    # One job posting, addressed by its numeric id and nothing else.
    "https://www.linkedin.com/jobs/view/4600000042",
    "https://www.linkedin.com/jobs/view/4600000042/",
    # HIS OWN MESSAGE SURFACE, allowed 2026-08-26 on the operator's ruling.
    # Both forms, because asking for the first LANDS on the second: LinkedIn
    # redirects /messaging/ into a conversation it chooses, measured twice.
    "https://www.linkedin.com/messaging/",
    "https://www.linkedin.com/messaging/thread/2-abc/",
    # THE TWO ADDRESSES THE OPERATOR RULED ON 2026-08-31, and each is ONE url
    # rather than a family. The intro editor on HIS OWN profile, in the
    # ``/in/me/`` spelling only -- that spelling redirects to whoever is signed
    # in, so it can only ever reach him -- and ONE NAMED settings page. The
    # rest of both families is in BLOCKED below, which is where the narrowness
    # of this pair is actually asserted.
    "https://www.linkedin.com/in/me/edit/intro/",
    "https://www.linkedin.com/mypreferences/d/dark-mode",
    # THE FOUR THE OPERATOR RULED ON 2026-08-31, each named individually and
    # never as a family. The narrowness of every one of them is asserted in
    # BLOCKED below, which is the half of this pair that does the work: an
    # ALLOWED entry says a url opens, and only the refused neighbours say the
    # permission stopped where it was supposed to.
    #
    # ONE ITEM PERMALINK, in both spellings LinkedIn serves. The urn shape is
    # the anchored one dom.ACTIVITY_ITEMS_JS already requires before it will
    # emit a key, so the only urns this server can build are the only ones the
    # pattern admits.
    "https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/",
    "https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001",
    # THE TWO PUBLISHING COMPOSERS. Both were measured as real anchors -- an
    # <a> with an href, count 1 each -- before either was written down.
    "https://www.linkedin.com/preload/sharebox/",
    "https://www.linkedin.com/article/new/",
    # THE MESSAGE COMPOSER, and this one url ONLY. It is bought past
    # ``/messaging/compose`` by an EXACT-url exemption, so the trailing-slash
    # spelling opens and nothing else in that family does -- see BLOCKED.
    "https://www.linkedin.com/messaging/compose/",
    # HIS OWN SUBSCRIPTION PAGE, 2026-09-01. One named address, admitted to
    # answer one question -- whether an InMail balance is countable -- and
    # its neighbours are in BLOCKED below, which is where the narrowness is
    # actually asserted. /premium/ carries purchase and upgrade flows.
    "https://www.linkedin.com/premium/my-premium/",
]

BLOCKED = [
    # Actions on LinkedIn.
    "https://www.linkedin.com/jobs/application/12345",
    # SENDING. The messaging READ surface left this list on 2026-08-26 when
    # the operator ruled that reading his own inbox is his to do; the composer
    # did not, and it is the entry that keeps sending impossible. It is the
    # pre-filled compose overlay LinkedIn opens from a job page.
    "https://www.linkedin.com/messaging/compose/?body=hello&interop=msgOverlay",
    # THE COMPOSER'S NEIGHBOURS, added 2026-08-31 in the same commit that
    # admitted ONE composer url. They are the whole of the evidence that the
    # exemption is an EQUALITY rather than a prefix: the pre-filled overlay
    # above still refuses, and so do these.
    "https://www.linkedin.com/messaging/compose/?recipient=someone",
    "https://www.linkedin.com/messaging/compose/new/",
    # AND THE ITEM PERMALINK'S NEIGHBOURS. ``/feed/update`` left the forbidden
    # tuple to buy the permalink, so these are what proves the family's
    # DANGEROUS half is still refused -- by ``/edit/``, ``/delete``,
    # ``action=`` and the anchored pattern respectively.
    "https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/edit/",
    "https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/delete",
    "https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/?action=delete",
    "https://www.linkedin.com/feed/update/",
    "https://www.linkedin.com/feed/update/urn%3Ali%3Aactivity%3A7400000000000000001/",
    # And the two composers' neighbours, for the same reason.
    "https://www.linkedin.com/preload/sharebox/publish",
    # THE SUBSCRIPTION PAGE'S NEIGHBOURS. /premium/ has purchase and upgrade
    # flows under it and this admission is ONE page: the family root, a
    # sub-path, and a query string all refuse.
    "https://www.linkedin.com/premium/",
    "https://www.linkedin.com/premium/my-premium/upgrade",
    "https://www.linkedin.com/premium/products/",
    "https://www.linkedin.com/article/edit/7400000000000000001/",
    "https://www.linkedin.com/mynetwork/invitation-manager/",
    "https://www.linkedin.com/in/someone/edit/topcard/",
    "https://www.linkedin.com/psettings/open-to-work",
    "https://www.linkedin.com/voyager/api/relationships/invitations",
    "https://www.linkedin.com/notifications/?action=markAllRead",
    # Other people's data at scale, and other hosts entirely.
    "https://www.linkedin.com/search/results/people/?keywords=cto",
    "https://www.linkedin.com/company/acme/people/",
    "https://evil.example.com/steal",
    "http://www.linkedin.com/feed/",
    "javascript:alert(1)",
    "file:///C:/Users/<user>/.claude/.credentials.json",
    "",
    # The job tracker, which the allowlist admits at exactly three addresses.
    # A wildcard query would have let every one of these through.
    "https://www.linkedin.com/jobs-tracker/",
    "https://www.linkedin.com/jobs-tracker/?stage=withdraw",
    "https://www.linkedin.com/jobs-tracker/?stage=archived",
    # The stages LinkedIn's own payload names and this server still refuses,
    # listed since 2026-08-26 because that is the day the enumeration grew and
    # a widening is only narrow if the things it did NOT admit are asserted.
    "https://www.linkedin.com/jobs-tracker/?stage=interview",
    "https://www.linkedin.com/jobs-tracker/?stage=clicked_apply",
    "https://www.linkedin.com/jobs-tracker/?apply=1",
    "https://www.linkedin.com/jobs-tracker/?stage=saved&save=1",
    "https://www.linkedin.com/jobs-tracker/?a%63tion=delete",
    "https://www.linkedin.com/jobs-tracker/?stage=saved#/../messaging/",
    "https://www.linkedin.com.evil.example/jobs-tracker/?stage=saved",
    # The address the tracker replaced. Nothing builds it any more, so it is
    # off the list -- a pattern kept for a url the server never opens is a
    # door with nobody watching it.
    "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",
    # A job posting, at every address this server does NOT build. The tool
    # takes an integer and formats it, so the numeric form is the only one
    # that can ever be produced -- and the pattern permits only that. A slug
    # carries a job title, which is a string, which is the thing an allowlist
    # exists to keep out of a url.
    "https://www.linkedin.com/jobs/view/senior-node-engineer-at-acme-4600000042/",
    "https://www.linkedin.com/jobs/view/4600000042/?refId=abc",
    "https://www.linkedin.com/jobs/view/4600000042/applying",
    "https://www.linkedin.com/jobs/view/12345",
    "https://www.linkedin.com/jobs/view/",
    "https://www.linkedin.com/jobs/view/abc/",
    # Whitespace, which every anchored pattern would otherwise swallow: "$"
    # matches before a trailing newline and "[^#]*" matches a CRLF.
    "https://www.linkedin.com/feed/\n",
    "https://www.linkedin.com/jobs-tracker/?stage=saved\n",
    "https://www.linkedin.com/notifications/?x=1\r\nX: y",
    " https://www.linkedin.com/feed/",
    # THE TWO MOST DESTRUCTIVE ADDRESSES ON THE ACCOUNT. Measured off a live
    # census 2026-08-31: LinkedIn's own settings index links to "Close and
    # delete account" at ``/mypreferences/d/close-accounts`` and to "Hibernate
    # account" at ``/mypreferences/d/hibernate-account``. NEITHER contains
    # ``categories/``, so until that day the only thing refusing them was the
    # anchored allowlist -- for a list that documents itself as a second,
    # independent gate, the two worst addresses had no second gate at all.
    # Which gate refuses them now is asserted in
    # ``test_the_two_account_destroying_addresses_are_refused_by_the_denylist``;
    # here they are simply refused.
    "https://www.linkedin.com/mypreferences/d/close-accounts",
    "https://www.linkedin.com/mypreferences/d/hibernate-account",
    # THE REST OF THE /edit/ FAMILY, which is the whole family bar one url.
    # ``/in/me/edit/intro/`` is exempted from the ``/edit/`` substring by
    # NAME and by EXACT MATCH; nothing else in the family is, and a prefix is
    # not a match.
    "https://www.linkedin.com/in/me/edit/",
    "https://www.linkedin.com/in/me/edit/topcard/",
    "https://www.linkedin.com/in/me/edit/forms/next-action/",
    "https://www.linkedin.com/in/me/edit/intro/../../evil",
    "https://www.linkedin.com/in/me/edit/intro/?action=delete",
    # ANOTHER MEMBER'S INTRO EDITOR, and the reason no member-slug pattern was
    # written: ``linkedin_who_viewed_me`` has MEASURED that loading a third
    # party's profile leaves them a durable record, so a pattern that can
    # address anybody but him is refused on that ground alone.
    "https://www.linkedin.com/in/alex-r-12ab34/edit/intro/",
    # THE SPELLING THE ALLOWLIST PATTERN ADMITS AND THE EXEMPTION DOES NOT,
    # recorded rather than left for somebody to trip over. The pattern ends
    # ``intro/?$`` so the slashless form matches it; the exemption is keyed on
    # the EXACT url the census builds, which carries the trailing slash. So
    # this one is refused by the forbidden gate. That is the conservative
    # direction -- a narrower exemption than the pattern, never a wider one.
    "https://www.linkedin.com/in/me/edit/intro",
    # THE REST OF /mypreferences/d/. ``dark-mode`` is ONE named page and the
    # family is not admitted with it: the two settings pages that were
    # considered and refused would each have needed ``"/settings/"`` narrowed,
    # and the category pages carry the toggles.
    "https://www.linkedin.com/mypreferences/d/settings/language",
    "https://www.linkedin.com/mypreferences/d/settings/autoplay-videos",
    "https://www.linkedin.com/mypreferences/d/categories/account",
    "https://www.linkedin.com/mypreferences/d/dark-mode/extra",
    "https://www.linkedin.com/mypreferences/d/dark-mode?theme=dark",
    "https://www.linkedin.com/mypreferences/d/data-privacy",
]


def test_the_forbidden_gate_is_what_stops_an_edit_url_not_the_allowlist():
    """Belt and braces, shown to be two separate things.

    ``dom.SKILL_HREF`` matches an inline edit affordance, and the argument that
    it can never become a navigation rests on ``/edit/`` being refused BEFORE
    the allowlist is consulted. Both gates refuse this url, so a test that only
    checked for a raise could not say which -- the message is what distinguishes
    them, and this pins the forbidden one.
    """
    url = "https://www.linkedin.com/in/alex-rivera-8c21/details/skills/edit/forms/2/"
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    assert "/edit/" in str(caught.value)
    assert "not a read surface" in str(caught.value)


@pytest.mark.parametrize("url", ALLOWED)
def test_read_surfaces_are_allowed(url: str):
    assert readonly.assert_read_url(url) == url


@pytest.mark.parametrize("url", BLOCKED)
def test_write_and_foreign_urls_are_blocked(url: str):
    with pytest.raises(WriteAttemptError):
        readonly.assert_read_url(url)


def test_the_tracker_allowlist_admits_three_stages_and_no_more():
    """THE THIRD STAGE, and the evidence that admitting it stayed narrow.

    ``?stage=draft`` was added on 2026-08-26 so the In Progress list could be
    read at all. The hazard in that edit is not the stage it names -- it is
    the shape the NEXT person reaches for: one ``[a-z_]+`` where the
    alternation is, and every stage LinkedIn has becomes openable, including
    the ones this server has no business on.

    So both halves are pinned. The permitted set is asserted EXACTLY, and each
    refused stage is named rather than left to a wildcard's absence: a test
    that only checked the three permitted ones would pass unchanged against
    ``(saved|applied|draft|interview|archived|clicked_apply)``.
    """
    from linkedin_server.config import BASE_URL

    permitted = {"saved", "applied", "draft"}
    refused = {"interview", "archived", "clicked_apply", "withdraw", "in_progress"}
    assert permitted & refused == set()

    for stage in sorted(permitted):
        url = f"{BASE_URL}/jobs-tracker/?stage={stage}"
        assert readonly.is_read_url(url), stage

    for stage in sorted(refused):
        url = f"{BASE_URL}/jobs-tracker/?stage={stage}"
        assert not readonly.is_read_url(url), stage

    # SHOWN NOT PASSING VACUOUSLY, which for a refusal test is the whole
    # question. Every refused url above matches the wildcard somebody might
    # reach for, so the ENUMERATION is the only thing standing between this
    # server and all five -- and the loop above is what fails on the day it
    # stops being an enumeration.
    wildcard = re.compile(r"^https://www\.linkedin\.com/jobs-tracker/\?stage=[a-z_]+$")
    for stage in sorted(refused):
        assert wildcard.match(f"{BASE_URL}/jobs-tracker/?stage={stage}"), stage


def test_the_two_ruled_surfaces_are_admitted_and_their_families_are_not():
    """THE 2026-08-31 RULING, and the evidence that admitting it stayed narrow.

    Two urls were ruled readable: the intro editor on his own profile, and ONE
    named settings page. The hazard in both is the same one the tracker stages
    have -- the shape the next person reaches for. For the editor it is
    ``/in/[A-Za-z0-9-]+/edit/intro/``, which reads like the neighbourly
    generalisation and is the one thing that must never be written: this
    server has MEASURED, on ``linkedin_who_viewed_me``, that loading a third
    party's profile leaves them a durable record. ``/in/me/`` redirects to
    whoever is signed in, so it can only ever reach him. For the settings page
    it is ``/mypreferences/d/[a-z-]+``, which would admit the two addresses in
    the BLOCKED list above that can end an account.

    So both halves are pinned: the pair is admitted, and each family member
    that is not is named rather than left to a wildcard's absence.
    """
    assert readonly.is_read_url("https://www.linkedin.com/in/me/edit/intro/")
    assert readonly.is_read_url("https://www.linkedin.com/mypreferences/d/dark-mode")

    for refused in (
        "https://www.linkedin.com/in/me/edit/",
        "https://www.linkedin.com/in/me/edit/topcard/",
        "https://www.linkedin.com/in/alex-r-12ab34/edit/intro/",
        "https://www.linkedin.com/mypreferences/d/settings/language",
        "https://www.linkedin.com/mypreferences/d/settings/autoplay-videos",
        "https://www.linkedin.com/mypreferences/d/categories/account",
        "https://www.linkedin.com/mypreferences/d/close-accounts",
        "https://www.linkedin.com/mypreferences/d/hibernate-account",
    ):
        assert not readonly.is_read_url(refused), refused

    # SHOWN NOT PASSING VACUOUSLY, which for a refusal test is the whole
    # question. Every refused address above matches the pattern somebody would
    # reach for, so the loop is what fails on the day one of them is written.
    tempting = (
        re.compile(r"^https://www\.linkedin\.com/in/[A-Za-z0-9\-_%]+/edit/intro/?$"),
        re.compile(r"^https://www\.linkedin\.com/mypreferences/d/[a-z\-/]+$"),
    )
    for refused in (
        "https://www.linkedin.com/in/alex-r-12ab34/edit/intro/",
        "https://www.linkedin.com/mypreferences/d/close-accounts",
        "https://www.linkedin.com/mypreferences/d/hibernate-account",
        "https://www.linkedin.com/mypreferences/d/settings/language",
    ):
        assert any(pattern.match(refused) for pattern in tempting), refused


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/mypreferences/d/close-accounts",
        "https://www.linkedin.com/mypreferences/d/hibernate-account",
    ],
)
def test_the_two_account_destroying_addresses_are_refused_by_the_denylist(url):
    """WHICH GATE REFUSES, because the refusal itself never changed.

    Both addresses were refused before 2026-08-31 and both are refused now, so
    a test that only checked for a raise would pass identically across the
    change and certify nothing about it. What changed is the GATE. The
    settings audit assumed "Close and delete account" and "Hibernate account"
    were covered by the ``/mypreferences/d/categories/`` entry; measured off a
    live census that day, their real addresses are
    ``/mypreferences/d/close-accounts`` and
    ``/mypreferences/d/hibernate-account`` and NEITHER contains ``categories/``.
    The only thing that had ever refused them was the anchored allowlist.

    ``readonly.py`` documents its substring list as a "second, independent
    gate ... belt and braces", and for the two most destructive addresses on
    the account there was no second gate at all. This asserts that there is
    one, by the message -- which is the only thing that tells the two gates
    apart.
    """
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    message = str(caught.value)
    assert "not a read surface" in message, message
    assert "not on the read-only allowlist" not in message, message
    # And the substring itself, so the test cannot pass on some other entry
    # happening to match.
    expected = "/close-accounts" if "close" in url else "/hibernate-account"
    assert repr(expected) in message, message
    assert expected in readonly._FORBIDDEN_URL_SUBSTRINGS


def test_the_exemption_table_is_exactly_one_url_for_exactly_one_substring():
    """The allowlist inside the denylist, read out loud.

    ``_FORBIDDEN_SUBSTRING_EXEMPTIONS`` is the second structure in this module
    that GRANTS rather than refuses, and a granting list that is only checked
    for "does it cover what we needed" grows an entry at a time with nobody
    noticing. So the CONTENTS are pinned here, the way
    ``SANCTIONED_MUTATIONS`` is pinned above: one url, one substring, both
    spelled out.

    The value is checked too, not just the key. An entry mapped to ``/delete``
    would buy past a different gate entirely while looking identical in a
    listing of keys.
    """
    assert readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS == {
        "https://www.linkedin.com/in/me/edit/intro/": "/edit/",
        # THE SECOND ENTRY, 2026-08-31, on the operator's ruling admitting the
        # message composer. It is here rather than being bought by shortening
        # the forbidden tuple, which is the difference that matters: every
        # other spelling under /messaging/compose is refused by the same gate
        # it always was, because this key is an EQUALITY and not a prefix.
        "https://www.linkedin.com/messaging/compose/": "/messaging/compose",
    }
    # The exempted substring must really be on the forbidden list; an
    # exemption for a substring nobody forbids is a dead entry that reads like
    # a live permission.
    for substring in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS.values():
        assert substring in readonly._FORBIDDEN_URL_SUBSTRINGS, substring
    # And the key must be stored lowercased, because that is what it is
    # compared against.
    for key in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS:
        assert key == key.lower(), key


def test_an_exemption_buys_past_one_substring_and_not_a_second(monkeypatch):
    """THE PER-SUBSTRING PROPERTY, shown on a url that carries two.

    The real table has one entry and that url contains one forbidden
    substring, so the property cannot be demonstrated on live data -- and a
    property that cannot be demonstrated is one a later refactor can drop
    without a single test going red. So the table is replaced with a hostile
    one: a url exempted for ``/edit/`` that ALSO contains ``/delete``.

    The exemption is per-substring, so ``/delete`` still refuses it. An
    implementation that exempted the URL rather than the PAIR would let this
    through, which is the whole reason the value in that dict is a substring
    and not a ``True``.
    """
    hostile = "https://www.linkedin.com/in/me/edit/intro/delete"
    monkeypatch.setattr(
        readonly,
        "_FORBIDDEN_SUBSTRING_EXEMPTIONS",
        {hostile: "/edit/"},
    )
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(hostile)
    message = str(caught.value)
    assert "'/delete'" in message, message
    assert "not a read surface" in message, message


def test_the_exemption_does_not_buy_past_the_allowlist(monkeypatch):
    """ONE GATE, NEVER BOTH.

    An exemption is permission to carry a forbidden substring. It is not
    permission to be opened -- the anchored allowlist still has to admit the
    url afterwards. Shown on a third party's intro editor, which is exactly
    the url an over-broad exemption would reach: with the substring gate
    bought past, the refusal has to come from the allowlist, and the message
    is what proves it did.
    """
    stranger = "https://www.linkedin.com/in/alex-r-12ab34/edit/intro/"
    monkeypatch.setattr(
        readonly,
        "_FORBIDDEN_SUBSTRING_EXEMPTIONS",
        {stranger: "/edit/"},
    )
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(stranger)
    assert "not on the read-only allowlist" in str(caught.value), str(caught.value)


def test_the_exemption_is_matched_with_equality_and_never_as_a_prefix():
    """``==``, and the control that shows what ``startswith`` would have cost.

    ``writes.WriteSpec.exempt_substring`` states the discipline this mirrors:
    "Compared with ``==`` against the entry in the forbidden list -- never as
    a shape, because a loose exemption is how a real write hides." The same
    applies one level up, to the url.

    Every url below has the exempted url as a PREFIX and is a different
    address. Each is refused -- but so is every one of them under a
    ``startswith`` lookup, because the allowlist pattern is anchored and no
    suffix can match it. A test that only asserted the refusal would therefore
    pass identically against both implementations and certify nothing.

    WHAT DISTINGUISHES THEM IS WHICH GATE REFUSES. Under ``==`` none of these
    is exempted, so the ``/edit/`` entry stops all four and says so. Under a
    prefix lookup all four would be waved past ``/edit/`` and would be stopped
    later or elsewhere -- by the allowlist, or by ``action=``, or by
    ``/delete``. So the message is the instrument, exactly as it is for the
    two account-ending addresses above.
    """
    exempted = "https://www.linkedin.com/in/me/edit/intro/"
    assert readonly.is_read_url(exempted)

    escapes = (
        exempted + "../../evil",
        exempted + "?action=delete",
        exempted + "delete",
        exempted + "forms/next-action/",
    )
    for url in escapes:
        with pytest.raises(WriteAttemptError) as caught:
            readonly.assert_read_url(url)
        assert "'/edit/'" in str(caught.value), (url, str(caught.value))

    # AND THE PREFIX RELATION HOLDS, so the paragraph above is about this code
    # and not about four urls that happen not to be prefixes at all.
    for url in escapes:
        assert any(
            url.lower().startswith(key)
            for key in readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS
        ), url


def test_a_keyword_cannot_smuggle_a_forbidden_path_into_a_search_url():
    """Tool arguments reach the url builder; the allowlist is what stops them."""
    hostile = (
        "https://www.linkedin.com/jobs/search/?keywords=x"
        "#/../messaging/thread/2-abc/"
    )
    # The fragment cannot escape the allowlist pattern, which is anchored.
    with pytest.raises(WriteAttemptError):
        readonly.assert_read_url(hostile)


# ---------------------------------------------------------------------------
# 4. Every url the server builds is a permitted read surface
# ---------------------------------------------------------------------------


def test_the_urls_the_server_actually_builds_all_pass_the_allowlist():
    from linkedin_server.config import BASE_URL, FEED_URL, LOGIN_URL

    built = [
        f"{BASE_URL}/analytics/profile-views/",
        f"{BASE_URL}/me/profile-views/",
        f"{BASE_URL}/jobs-tracker/?stage=applied",
        f"{BASE_URL}/jobs-tracker/?stage=saved",
        f"{BASE_URL}/jobs-tracker/?stage=draft",
        f"{BASE_URL}/in/me/",
        f"{BASE_URL}/in/alex-r/details/skills/",
        f"{BASE_URL}/notifications/",
        f"{BASE_URL}/mypreferences/d/",
        # THE TWO CENSUS SURFACES ADDED 2026-08-31. Both are built in
        # server.py's CENSUS_SURFACES and both had to be admitted deliberately.
        f"{BASE_URL}/in/me/edit/intro/",
        f"{BASE_URL}/mypreferences/d/dark-mode",
        FEED_URL,
        LOGIN_URL,
    ]
    for url in built:
        assert readonly.is_read_url(url), url


def test_that_list_is_the_urls_the_server_really_builds():
    """The list above is hand-written, so it can go stale -- and it did.

    It still named ``/my-items/saved-jobs/?cardType=...`` for a release after
    the server stopped building it, and never named the tracker urls that
    replaced them, so the one line this change added to the allowlist was
    covered by nothing. This reads the f-string literals out of ``server.py``
    instead of trusting the list.
    """
    source = (Path(readonly.__file__).resolve().parent / "server.py").read_text(
        encoding="utf-8"
    )
    built_paths = set(re.findall(r'f"\{BASE_URL\}(/[^"?]*)', source))
    assert "/jobs-tracker/" in built_paths, built_paths
    assert "/my-items/saved-jobs/" not in built_paths, (
        "server.py still builds the retired saved-jobs url"
    )

# ---------------------------------------------------------------------------
# 6. The denylist's DIRECTION, and the addresses it is supposed to catch
# ---------------------------------------------------------------------------
#
# WHY THESE LIVE HERE AND NOT IN test_readonly_boundary_invariant.py, where
# they were first written. That file freezes the boundary by reading
# readonly.py AS TEXT and hashing its AST -- deliberately, so the freeze does
# not depend on importing the thing it is policing. These two checks need the
# opposite: the live tuple and the live function. They are behaviour, and
# behaviour is what this file is for.

#: Every substring that has EVER been on ``_FORBIDDEN_URL_SUBSTRINGS``.
#:
#: A ROSTER, NOT A SNAPSHOT, and the difference is the point. The digests
#: above answer "did this list change"; they cannot answer "did it change in
#: the safe direction", and for a denylist that is the only question worth
#: asking. This one is a SUBSET assertion, so a growing list keeps passing
#: without an edit and a shrinking one cannot.
#:
#: An entry leaves this roster only if somebody deliberately deletes it here,
#: in the same commit that deletes it from the boundary, having written down
#: why an address this repository once refused should now be reachable.
FORBIDDEN_SUBSTRINGS_EVER = (
    "/jobs/application",
    "easyapply",
    "easy-apply",
    # NARROWED 2026-08-26 from a blanket "/messaging" to the compose surface
    # alone, on the operator's ruling that reading his own inbox is his to do.
    # That narrowing PREDATES this roster, so the blanket entry is not on it;
    # what is on it is the entry that survived, which is the one that keeps
    # sending impossible.
    "/messaging/compose",
    "/invite",
    "invitation",
    "/connect",
    "/follow",
    "/unfollow",
    "/endorse",
    "/post/",
    "/feed/update",
    "sharing/share",
    "/settings/",
    "opentowork",
    "open-to-work",
    # Added 2026-08-30 with the settings-index census. See readonly.py.
    "/mypreferences/d/categories/",
    "/psettings/",
    "/edit/",
    "action=",
    "/delete",
    "/withdraw",
    # ADDED 2026-08-31, and they join the roster on the day they join the
    # boundary because they close a hole rather than tidy one. The settings
    # audit assumed the two account-ending pages were covered by
    # ``/mypreferences/d/categories/``; measured off a live census, they are
    # at ``/mypreferences/d/close-accounts`` and
    # ``/mypreferences/d/hibernate-account`` and neither contains
    # ``categories/``. They had no second gate at all.
    "/close-accounts",
    "/hibernate-account",
)

#: THE ONE SUBSTRING THAT HAS EVER LEFT THE FORBIDDEN LIST, and the reason.
#:
#: The roster above is asserted as a SUBSET of the live tuple, so a deletion
#: cannot pass without an edit here. This is that edit, and it is DELIBERATELY
#: SHAPED AS AN EXCEPTION RATHER THAN A DELETION: the entry stays in
#: ``FORBIDDEN_SUBSTRINGS_EVER``, because a substring quietly removed from the
#: roster is indistinguishable from one that was never on it, and the whole
#: value of that roster is that it remembers.
#:
#: ``/feed/update`` was removed on 2026-08-31, on the operator's ruling
#: admitting ONE NAMED ITEM PERMALINK PER CALL. It could not be kept, and the
#: reason is mechanical rather than a matter of appetite: this gate matches
#: SUBSTRINGS, so it cannot say "the permalink but nothing beneath it", and
#: the exemption table is keyed on an EXACT url while the urn varies per call.
#: Neither mechanism can express the ruling.
#:
#: WHAT WAS AND WAS NOT GIVEN UP, and it is asserted rather than argued --
#: ``test_the_removed_substring_did_not_take_the_family_with_it`` below puts
#: the dangerous members of that family through the real guard. ``/edit/``,
#: ``/delete``, ``/withdraw`` and ``action=`` all remain and all still catch
#: them. What was given up is a blanket refusal of a surface that renders one
#: of HIS OWN items.
#:
#: An entry here is a boundary decision. Adding a second one means writing
#: down the same three things: which ruling, why the substring could not be
#: kept, and what still refuses the rest of its family.
FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED = {
    "/feed/update",
}

#: Addresses that must stay unreadable, whatever the two lists look like.
#:
#: THE ROSTER ABOVE IS ABOUT STRINGS; THIS IS ABOUT BEHAVIOUR, and it is the
#: one that would have caught the defect measured on 2026-08-30. ``/settings/``
#: sat on the forbidden list for the whole life of this repository and matched
#: NOTHING LinkedIn serves -- so a roster check on that string passed every
#: day while the surface it was named for had no second gate at all. A list of
#: strings cannot notice that; a list of ADDRESSES can.
#:
#: Each entry is a real address, put through the real guard.
MUST_STAY_UNREADABLE = (
    "https://www.linkedin.com/mypreferences/d/categories/account",
    "https://www.linkedin.com/psettings/",
    "https://www.linkedin.com/settings/",
    # ``https://www.linkedin.com/messaging/compose/`` WAS HERE UNTIL
    # 2026-08-31 and is now READABLE, by the operator's ruling and by an
    # exact-url exemption. It is recorded rather than silently dropped, and
    # what replaces it is the set of neighbours the exemption must NOT have
    # carried with it -- which is a stronger check than the single entry was,
    # because the risk was never that one url opened. It was that a family
    # did.
    "https://www.linkedin.com/messaging/compose",
    "https://www.linkedin.com/messaging/compose/new/",
    "https://www.linkedin.com/messaging/compose/?recipient=someone",
    "https://www.linkedin.com/mynetwork/invitation-manager/",
    "https://www.linkedin.com/mynetwork/",
    "https://www.linkedin.com/company/example-co/",
    "https://www.linkedin.com/feed/following/",
    "https://www.linkedin.com/in/me/edit/",
    # ADDED 2026-08-31, in the commit that admitted ONE url out of each of two
    # families. These are the addresses that must not travel with it -- the
    # two that can end the account, the rest of his own editor, another
    # member's editor, and the escape that proves the exemption is an
    # equality and not a prefix.
    "https://www.linkedin.com/mypreferences/d/close-accounts",
    "https://www.linkedin.com/mypreferences/d/hibernate-account",
    "https://www.linkedin.com/mypreferences/d/settings/language",
    "https://www.linkedin.com/in/me/edit/topcard/",
    "https://www.linkedin.com/in/alex-r-12ab34/edit/intro/",
    "https://www.linkedin.com/in/me/edit/intro/../../evil",
)





def test_the_forbidden_list_has_only_ever_grown():
    """THE DIRECTION, which no digest above can report.

    A digest says the forbidden list is not what it was. It says nothing about
    which way, and the two directions are not remotely equivalent: adding a
    substring refuses more, removing one makes an address reachable that this
    repository had decided was not. Re-baselining a digest is the same edit in
    both cases.

    So the roster is asserted as a SUBSET. Growth needs no edit here; a
    deletion cannot pass without one, and making that edit means writing down
    why an address once refused should now be readable.
    """
    live = set(readonly._FORBIDDEN_URL_SUBSTRINGS)
    lost = [
        entry
        for entry in FORBIDDEN_SUBSTRINGS_EVER
        if entry not in live
        and entry not in FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED
    ]
    assert not lost, (
        f"these substrings left the forbidden list: {lost}. Each one was a "
        "refusal somebody wrote deliberately. Removing one is a boundary "
        "change, not a tidy-up -- if it was intended, record it in "
        "FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED with the ruling, which is "
        "an edit somebody reviews rather than a digest somebody re-bakes."
    )
    # AND THE EXCEPTION LIST CANNOT ROT INTO A BLANKET. Every entry in it must
    # name a substring the roster remembers AND one that is really gone; an
    # entry for a live substring would sit there granting nothing and hiding
    # the next real removal behind a stale name.
    for entry in FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED:
        assert entry in FORBIDDEN_SUBSTRINGS_EVER, entry
        assert entry not in live, (
            f"{entry!r} is recorded as deliberately removed and is on the "
            "live forbidden list. One of the two is wrong."
        )


#: The members of the ``/feed/update`` family that must stay refused now that
#: the substring guarding all of them is gone. Each is a real address put
#: through the real guard, and each names the entry that is expected to catch
#: it, so a refusal that started coming from somewhere else is visible.
FEED_UPDATE_FAMILY_STILL_REFUSED = (
    ("https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/edit/", "/edit/"),
    ("https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/delete", "/delete"),
    ("https://www.linkedin.com/feed/update/urn:li:activity:7400000000000000001/?action=delete", "action="),
)


@pytest.mark.parametrize(
    "url,expected_gate", FEED_UPDATE_FAMILY_STILL_REFUSED, ids=lambda v: str(v)[:40]
)
def test_the_removed_substring_did_not_take_the_family_with_it(url, expected_gate):
    """THE PRICE OF THE REMOVAL, PAID IN ASSERTIONS RATHER THAN IN PROSE.

    ``/feed/update`` left the forbidden tuple so that ONE item permalink could
    be admitted. The argument for that being acceptable is that the family's
    DESTRUCTIVE members are caught by other entries which are all still there
    -- and an argument of that shape is exactly the kind this repository has
    twice found to be false when finally measured. ``/settings/`` sat on the
    list for the life of the repo matching nothing LinkedIn served; the two
    account-ending pages were assumed covered by a substring that does not
    appear in either address.

    So this does not reason about it. It puts each address through
    ``assert_read_url`` and reads back WHICH substring refused it, so a
    refusal that quietly started coming from the allowlist instead -- which is
    a single loosened pattern away from not coming at all -- fails here.
    """
    with pytest.raises(readonly.WriteAttemptError) as excinfo:
        readonly.assert_read_url(url)
    message = str(excinfo.value)
    assert expected_gate in message, message
    # THE GATE, NOT MERELY THE ANSWER. The forbidden loop and the allowlist
    # produce different sentences, and only the first is the second,
    # independent gate this family now depends on entirely.
    assert "is not a read surface" in message, message


def test_the_permalink_that_bought_the_removal_is_the_only_thing_it_bought():
    """AND THE NARROWNESS, from the other side.

    One url shape opens. The bare family root does not, a percent-encoded urn
    does not -- that spelling has never been observed in this position -- and
    a query string does not, so LinkedIn's own tracking parameters cannot ride
    in on it.
    """
    urn = "urn:li:activity:7400000000000000001"
    base = "https://www.linkedin.com/feed/update/"
    assert readonly.is_read_url(f"{base}{urn}/")
    assert readonly.is_read_url(f"{base}{urn}")
    assert not readonly.is_read_url(base)
    assert not readonly.is_read_url(f"{base}{urn}/?trk=feed")
    assert not readonly.is_read_url(
        base + "urn%3Ali%3Aactivity%3A7400000000000000001/"
    )
    # THE SHAPE IS THE READER'S OWN, not a second spelling written here. The
    # only urns this server can build a permalink from are the ones
    # dom.ACTIVITY_ITEMS_JS will emit, and if that shape ever widened without
    # this pattern following, a key would come back that no url could be built
    # from -- which fails loudly rather than opening anything, and is still
    # worth catching here.
    assert "urn:li:[A-Za-z]+:[0-9]+" in dom.ACTIVITY_ITEMS_JS.replace(
        "^urn:li:[A-Za-z]+:[0-9]+$", "urn:li:[A-Za-z]+:[0-9]+"
    )
    assert any(
        "urn:li:[A-Za-z]+:[0-9]+" in pattern.pattern
        for pattern in readonly._ALLOWED_URL_PATTERNS
    )


def test_that_roster_check_can_fail_on_a_deletion():
    """SHOWN FAILING, on the exact edit it exists to catch.

    Without this the test above is a subset assertion that a list which never
    shrinks would pass forever without anyone knowing whether it CAN fail.
    """
    weakened = tuple(
        entry
        for entry in readonly._FORBIDDEN_URL_SUBSTRINGS
        if entry != "/messaging/compose"
    )
    assert len(weakened) == len(readonly._FORBIDDEN_URL_SUBSTRINGS) - 1
    lost = [
        entry
        for entry in FORBIDDEN_SUBSTRINGS_EVER
        if entry not in set(weakened)
        and entry not in FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED
    ]
    assert lost == ["/messaging/compose"], lost
    # THE CONTROL ON THE EXCEPTION MECHANISM ITSELF, added with it. A recorded
    # removal must silence EXACTLY its own entry and nothing else, or the list
    # is an off switch rather than a ledger.
    assert "/messaging/compose" not in FORBIDDEN_SUBSTRINGS_DELIBERATELY_REMOVED


@pytest.mark.parametrize("url", MUST_STAY_UNREADABLE)
def test_no_previously_forbidden_address_became_readable(url):
    """THE BEHAVIOURAL FREEZE, and it exists because the string freeze missed
    something for the entire life of this repository.

    ``"/settings/"`` has been on the forbidden list since the beginning. On
    2026-08-30 it was measured against LinkedIn's actual settings addresses --
    ``/mypreferences/d/`` and ``/psettings/`` -- and matched NEITHER. The
    roster check above would have passed every single day of that, because the
    string was present; what was absent was any address it caught.

    A boundary is a set of addresses that cannot be opened, not a set of
    strings that appear in a tuple. This asserts the addresses.
    """
    assert not readonly.is_read_url(url), (
        f"{url} became readable. Every url here is one this repository has "
        "decided it will not open, and each is refused today."
    )
