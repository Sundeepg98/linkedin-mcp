"""THE GUARDS CAN ONLY REPORT ON FILES THEY CAN READ, and five of them stopped.

WHAT HAPPENED, MEASURED. Run 35441013901, 2026-09-19: fourteen failures on
ubuntu py3.10 across four test files. Ten were one defect --
``scripts/_probe_add_section_menu.py`` put an escaped quote inside an f-string
EXPRESSION, legal from 3.12 under PEP 701 and a SyntaxError before it. The file
did not parse on 3.10, so every guard that walks the package with ``ast.parse``
raised SyntaxError instead of returning a verdict:

    test_navigation_is_never_derived      the goto rule and its census
    the page-text sink rule               the output-violation twin
    the sanitiser-claimant sweep
    the relation-definition byte check

**NOT ONE OF THOSE TEN WAS REPORTING A RULE VIOLATION.** They were reporting
that they could not read a file, in a traceback shaped exactly like a rule
violation, ten times. The suite's own summary said fourteen reds; the tree had
one.

WHY A LOCAL RUN COULD NOT SEE IT. This box is 3.13, where the construct is
legal. ``ast.parse(source, feature_version=(3, 10))`` does not help --
measured, it accepts the construct, because ``feature_version`` never reached
the tokenizer PEP 701 replaced. So a guard that asks the RUNNING interpreter
can only ever discover this on the runner that has the old one.

THIS FILE IS THE FIX FOR THE CLASS, NOT FOR THE FILE. It reads the source for
constructs the declared floor refuses, so the answer does not depend on which
interpreter is asking. When it goes red, it goes red ONCE and names the file --
instead of N guards crashing and the reader counting tracebacks.

It is deliberately narrow: ``scripts/py_baseline_lint.py`` knows two
constructs, both f-string forms, because that is where PEP 701 moved the line
and the only place this repository has tripped. A file it passes may still fail
to compile on the floor for a reason nobody here has met. The repair when that
happens is a third rule with the offending line as its control -- the same
shape as the two below.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _load(name: str, filename: str):
    """Load a script as a module, the way tests/test_ci_shard.py does."""
    path = REPO / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lint = _load("_py_baseline_lint", "py_baseline_lint.py")

#: Scanned ONCE. Three tests read this and the scan is ~4s over 311 files; at
#: module scope that is 4s and at function scope it is 12s, on a suite that
#: already costs 24 minutes. The scan is a pure read of tracked files, so one
#: result serves every assertion below.
UNPARSEABLE, OFFENCES = lint.scan(REPO)


#: The defect, verbatim, as ``08ceb1e`` found it. Pinned as TEXT rather than
#: fetched with ``git show`` on purpose: CI runs on a branch with no ancestry,
#: where every historical SHA is unresolvable, and a control that evaporates on
#: the branch it is meant to protect is not a control. Note it sits inside an
#: ordinary string literal, so this file's own tokenizer never meets it and
#: this file stays legal on the floor it is policing.
THE_DEFECT_AS_IT_SHIPPED = '''
async def structure(page, when):
    print(f"    {when:7s} "
          f"menus={await page.locator('[role=\\"menu\\"]').count()}  "
          f"dialogs={await page.locator('[role=\\"dialog\\"]').count()}")
'''

#: The repair, also verbatim. A rule that only ever sees offending input is
#: half a measurement: this is the half that says the repair is actually a
#: repair and not merely different.
THE_REPAIR_AS_IT_LANDED = '''
async def structure(page, when):
    n_menus = await page.locator('[role="menu"]').count()
    n_dialogs = await page.locator('[role="dialog"]').count()
    print(f"    {when:7s} "
          f"menus={n_menus}  "
          f"dialogs={n_dialogs}")
'''


# ---------------------------------------------------------------------------
# The baseline itself, which is two numbers that must agree
# ---------------------------------------------------------------------------


def test_the_declared_floor_is_a_version_ci_actually_runs():
    """DECLARED and RUN are two facts and a lint pinned to one is pinned to air.

    ``pyproject.toml`` says ``>=3.10``; the workflow matrix runs 3.10 and 3.13.
    If someone drops 3.10 from the matrix without touching pyproject, this
    file would keep policing a version nothing tests -- and if someone raises
    pyproject past PEP 701 without touching the matrix, it would stop policing
    a version that still runs.
    """
    floor = lint.minimum_python_from_pyproject(REPO)
    in_ci = lint.python_versions_in_ci(REPO)
    assert in_ci, "no python-version found in .github/workflows/ci.yml"
    assert floor == in_ci[0], (
        f"pyproject declares {floor} but the lowest version CI runs is "
        f"{in_ci[0]} -- one of the two moved and the other did not"
    )


def test_the_floor_is_below_pep_701_so_these_rules_still_apply():
    """A repository whose floor reaches 3.12 should DELETE this file.

    Stated as an assertion rather than a comment so the day it stops being
    true arrives as a red with instructions, not as a file nobody notices is
    checking for something the language now allows everywhere.
    """
    floor = lint.minimum_python_from_pyproject(REPO)
    assert floor < lint.PEP_701, (
        f"the floor is now {floor}, at or past PEP 701 -- both rules in "
        "scripts/py_baseline_lint.py are about constructs 3.12 legalised, so "
        "this file and that script should go rather than be maintained"
    )


# ---------------------------------------------------------------------------
# THE RULE
# ---------------------------------------------------------------------------


def test_there_is_a_package_to_scan():
    """A rule asserted over zero files passes loudly and certifies nothing."""
    files = lint.tracked_python_files(REPO)
    assert len(files) > 100, len(files)


def test_every_tracked_file_parses_under_the_running_interpreter():
    """The louder half, kept separate because its repair is different.

    A file that will not parse HERE is broken for everyone; a file that will
    not parse on the FLOOR is broken only where nobody is looking. Folding the
    two together would report them with one message and send the reader to the
    wrong repair.
    """
    assert not UNPARSEABLE, (
        "these files do not parse under the interpreter running this test, so "
        "every ast.parse guard in this suite is also failing on them and NONE "
        "of those failures is a rule violation: " + repr(UNPARSEABLE)
    )


def test_no_tracked_file_uses_an_f_string_form_the_floor_refuses():
    """THE RULE. What this box cannot see, the source can still be asked.

    The message names the file, the line and the expression, because a refusal
    that reports only a count is half a measurement -- and because the reader
    of this red is about to go looking for a rule violation that is not there.
    """
    assert not OFFENCES, (
        "f-string expressions PEP 701 legalised in 3.12 and this package's "
        "declared floor refuses. Each one is a SyntaxError on the floor, which "
        "means the file does not parse there AT ALL and every ast.parse guard "
        "in this suite reports a crash instead of a verdict:\n"
        + "\n".join(
            f"  {name}:{line}  {rule}  {text}"
            for name, line, rule, text in OFFENCES
        )
    )


# ---------------------------------------------------------------------------
# CAN IT FAIL -- on the defect that caused this file to exist
# ---------------------------------------------------------------------------


def test_the_lint_convicts_the_defect_that_caused_this_file():
    """The strongest control available: the thing that actually happened.

    BELOW THE FLOOR THE PARSER CONVICTS IT INSTEAD, and that is not a weaker
    result -- it is the defect's ORIGINAL SIGNATURE. This whole file exists
    because that source "did not parse on 3.10 at all, so every guard in this
    suite that walks the package with ast.parse raised SyntaxError instead of
    returning a verdict". Reproducing that on 3.10 is the same event, seen from
    the other side of the boundary.

    Measured on a real CPython 3.10 2026-09-19, after CI found it on
    ubuntu-latest py3.10 shard 0.
    """
    try:
        found = lint.violations(THE_DEFECT_AS_IT_SHIPPED, "_probe_add_section_menu.py")
    except SyntaxError as error:
        assert sys.version_info < (3, 12), (
            "an interpreter at or above PEP 701 refused source it should "
            "accept: %s" % error
        )
        return
    assert len(found) == 2, found
    assert {rule for _, rule, _ in found} == {lint.BACKSLASH}, found
    assert all("page.locator" in text for _, _, text in found), found


def test_the_lint_clears_the_repair_that_landed():
    """AND THE CONTROL FOR THE CONTROL. A rule that refuses everything convicts
    the defect too, and is useless in the way that gets a gate deleted."""
    assert lint.violations(THE_REPAIR_AS_IT_LANDED, "_probe_add_section_menu.py") == []


@pytest.mark.parametrize(
    "source, rule",
    [
        # PEP 701's other half: before 3.12 the expression could not contain
        # the quote that terminates the literal.
        ('x = f"key={d["k"]}"', lint.REUSED_QUOTE),
        ("x = f'key={d['k']}'", lint.REUSED_QUOTE),
        # And the backslash form, in its smallest shape.
        ('x = f"n={len("a\\tb")}"', lint.BACKSLASH),
    ],
)
def test_each_rule_fires_on_its_own_smallest_case(source, rule):
    """The construct is refused on the floor, by whichever mechanism applies.

    **THIS TEST USED TO ASSUME IT WAS ALWAYS RUNNING ABOVE THE FLOOR**, and CI
    caught that on 2026-09-19 (run 35450659149, ubuntu-latest py3.10 shard 0,
    4 failed). ``lint.violations`` calls ``ast.parse``, which on 3.10 REFUSES
    these fixtures outright -- ``SyntaxError: f-string: unmatched '('`` -- so
    the rule never got the chance to fire and the test errored instead of
    passing. The guard written to prove the package survives its floor could
    not itself run on that floor.

    THERE ARE TWO MECHANISMS AND BOTH ARE A PASS, because the claim is
    "the floor refuses this", not "the linter flags this":

    * ABOVE the floor (3.12+, where PEP 701 made it legal) the source parses
      and the RULE must convict it. That is the interesting direction and the
      reason the linter exists -- nothing else would notice.
    * AT OR BELOW the floor the PARSER refuses it, which is a STRONGER verdict
      than the rule gives and is the exact outcome the rule exists to predict.

    Each branch asserts on its own terms, so neither is a silent pass.
    """
    try:
        found = lint.violations(source)
    except SyntaxError as error:
        assert sys.version_info < (3, 12), (
            "the running interpreter refused a fixture it should accept: this "
            "branch is only correct at or below the PEP 701 boundary, and here "
            "it fired on %s. Error: %s" % (sys.version.split()[0], error)
        )
        return
    assert found, source
    assert {name for _, name, _ in found} == {rule}, found


@pytest.mark.parametrize(
    "source",
    [
        # The legal twin of each case above: a DIFFERENT quote inside, which
        # every version has always allowed.
        'x = f"key={d[\'k\']}"',
        "x = f'key={d[\"k\"]}'",
        # A triple-quoted f-string whose expression contains a lone quote. The
        # lone quote never terminated anything, so flagging it would be a false
        # positive on every version -- which is why _quote_of looks for the
        # whole terminating sequence and not for one character.
        'x = f"""key={d[\'k\']} and {other["j"]}"""',
        # No f-string at all, but text that looks like one. The scan is over
        # the AST, so a plain string mentioning an f-string is not one.
        "pattern = r'f\"{BASE}/x\\\\?q=1\"'",
        # Ordinary f-strings, which must stay silent or the rule is unusable.
        'x = f"n={len(items)} of {total}"',
        'x = f"{when:7s} {count}"',
    ],
)
def test_the_legal_twins_stay_silent(source):
    assert lint.violations(source) == [], source
