"""The impact selector must find the test that a census-data edit breaks.

WHY THIS EXISTS, and it is a receipt rather than a worry. On 2026-09-20 an
edit to `_audit/2026-09-03-linkedin-gap-blockers.md` -- one line, a
`**CORRECTED BY:**` marker inserted between a table header and its first data
row -- broke `scripts/build_blocker_map.py`, whose `_table_after()` takes rows
until the first non-pipe line and therefore took zero. Every blocker came back
unknown to the ledger parse. `tests/test_blocker_map_is_derived.py` was the
only thing in the repository that noticed.

THE MEASUREMENT THAT MAKES THIS FILE NECESSARY. That same change was staged in
a worktree and put to `scripts/pre_commit_boundary_gate.py`, whose coupling
rule is the one an impact gate would naturally be built on. It exited **0,
with no output at all**, while the coupled test was red in 3.07s. Its
`staged_paths()` keeps only `*.py`, so a `.md` never reaches the coupling rule
at all; and even reaching it would not help, because the rule matches
module-level CONSTANT names and a data file defines none.

    AN IMPACT GATE KEYED ON THAT RULE WOULD HAVE RETURNED ZERO TESTS AND
    WAVED THE BREAKAGE THROUGH -- faster than the full suite, and wrong in
    the one direction that matters.

That is the entire difference between a gate and a rubber stamp, so it is
pinned here rather than trusted to a docstring.

WHAT IS ASSERTED, AND WHY EACH TEST CAN FAIL.

This repository has produced three checks in two days that could not fail --
a control that could not fire on linux, a guard disarmed in every worktree, a
floor guard that could not run on its own floor. A selector is unusually
exposed to that disease, because a selector that returns EVERYTHING and a
selector that returns NOTHING both look calm from outside: one never refuses,
the other never fires. So every test below is written with the arm that shows
it discriminating:

  * the POSITIVE arm asserts the target is selected;
  * the NEGATIVE arm reverts the coupling rule -- `data_coupling=False` -- and
    asserts the SAME target is no longer found. That is the rule "shown
    failing", executed on every run rather than described in prose. If the
    selector is ever changed to return everything, the negative arm goes red;
    if it is changed to return nothing, the positive arm goes red. There is no
    version of a broken selector that passes both.
  * `test_the_shipped_constant_rule_is_still_blind_to_this` pins the DEFECT
    itself, so that a later simplification back onto the boundary gate's rule
    fails loudly instead of quietly restoring the hole.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import impact_gate as G  # noqa: E402
import pre_commit_boundary_gate as boundary  # noqa: E402

#: The change that actually happened, and the test that actually caught it.
LEDGER = "_audit/2026-09-03-linkedin-gap-blockers.md"
EVIDENCE_TSV = "_audit/_census/blocker-assignments.tsv"
THE_TEST = "tests/test_blocker_map_is_derived.py"
THE_SCRIPT = "scripts/build_blocker_map.py"


def _skip_if_moved(*paths: str) -> None:
    """These tests are about REAL files. If one is renamed, say so loudly.

    Deliberately a failure and not a skip: the coupling this file defends is
    a property of those specific artifacts, and a silent skip when one moves
    is how a guard stops guarding without anyone being told.
    """
    missing = [p for p in paths if not (_ROOT / p).exists()]
    if missing:
        pytest.fail(
            f"{missing} no longer exist(s). This file pins the data-coupling "
            "rule against the real 2026-09-20 defect; if those artifacts were "
            "renamed, re-aim these tests rather than deleting them."
        )


# --------------------------------------------------------------------------
# THE POSITIVE ARM.
# --------------------------------------------------------------------------

def test_the_census_ledger_selects_the_test_that_caught_it():
    """The whole point, stated as an assertion."""
    _skip_if_moved(LEDGER, THE_TEST, THE_SCRIPT)
    impact = G.impact_set([LEDGER])
    assert THE_TEST in impact.test_files, (
        f"an edit to {LEDGER} must select {THE_TEST}. It is the only test in "
        "this repository that noticed when that file's table was split on "
        f"2026-09-20. Selected instead: {impact.test_files}"
    )


def test_the_census_evidence_table_selects_it_too():
    """The second data shape: a TSV the same script reads.

    Included because the ledger is a `.md` and a rule that happened to work
    only for markdown would pass the test above while remaining blind to the
    census tables, which are the files this repository edits most often.
    """
    _skip_if_moved(EVIDENCE_TSV, THE_TEST)
    impact = G.impact_set([EVIDENCE_TSV])
    assert THE_TEST in impact.test_files, (
        f"{EVIDENCE_TSV} is read by {THE_SCRIPT} as EVIDENCE and must select "
        f"{THE_TEST}. Selected: {impact.test_files}"
    )


def test_the_selection_travels_the_two_hop_chain_and_not_a_coincidence():
    """Provenance, not just membership.

    A selector can return the right answer for the wrong reason -- a stray
    prose match would put this test in the set while proving nothing about
    whether the DATA -> SCRIPT -> TEST chain is understood. So the edges are
    asserted, in both halves.
    """
    _skip_if_moved(LEDGER, THE_TEST, THE_SCRIPT)
    impact = G.impact_set([LEDGER])
    edges = {(a, b) for a, b, _ in impact.edges}
    assert (LEDGER, THE_SCRIPT) in edges, (
        f"hop 1 missing: {THE_SCRIPT} opens that ledger as "
        '`ROOT / "_audit" / "<name>"`, so the basename is the only token that '
        "survives the composition and the data rule must match it."
    )
    assert (THE_SCRIPT, THE_TEST) in edges, (
        f"hop 2 missing: {THE_TEST} does `import build_blocker_map` after "
        "putting scripts/ on sys.path, so the import rule must index bare "
        "module names as well as dotted ones."
    )


# --------------------------------------------------------------------------
# THE NEGATIVE ARM -- the coupling rule REVERTED, and the selection gone.
# --------------------------------------------------------------------------

def test_reverting_the_data_rule_loses_the_test_again():
    """THE CONTROL. Turn the rule off; the census case must go dark.

    Without this, every assertion above is satisfiable by a selector that
    returns the whole suite -- which would be a rubber stamp wearing a
    selector's output format. This is the arm that proves the rule is doing
    the work, and it runs on every CI cycle rather than living in a comment.
    """
    _skip_if_moved(LEDGER, THE_TEST)
    reverted = G.impact_set([LEDGER], data_coupling=False)
    assert THE_TEST not in reverted.selected, (
        "with data coupling reverted, the census ledger must NOT reach "
        f"{THE_TEST} -- that is the 2026-09-20 hole. It was found anyway, so "
        "either some other rule is silently over-selecting (and the gate's "
        "narrowing claim is fiction) or this control no longer controls "
        f"anything. Found: {reverted.test_files}"
    )
    assert not reverted.selected, (
        "a data path with the data rule off should SELECT nothing at all; "
        f"got {reverted.selected}. Note this asserts on .selected, not on "
        ".test_files -- the corpus-wide floor is in the plan on every run "
        "and would mask this assertion completely."
    )


def test_the_shipped_constant_rule_is_still_blind_to_this():
    """Pin the DEFECT, so a simplification back onto it cannot be quiet.

    `coupled_test_files` is a good rule for the class it was built for and
    this is not that class. Asserting its blindness here means that if anyone
    later decides the impact gate can just call the boundary gate and be done,
    this test tells them exactly what they would be giving up.
    """
    _skip_if_moved(LEDGER)
    assert boundary.coupled_test_files([LEDGER]) == [], (
        "the boundary gate's constant rule is expected to return NOTHING for "
        "a data path -- it matches module-level constant names and a .md "
        "defines none. If it now returns something, the rule changed and the "
        "argument in impact_gate.py's docstring needs rewriting, not deleting."
    )


# --------------------------------------------------------------------------
# A CITATION IS NOT A DEPENDENCY.
# --------------------------------------------------------------------------

def test_a_docstring_that_cites_the_ledger_is_not_coupled_to_it():
    """The prose strip, shown discriminating on a real file.

    `linkedin_server/server.py` quotes that ledger in its module docstring and
    `linkedin_server/readonly.py` cites it in a `#` comment. Neither opens it.
    Following those mentions selected 93 of 170 test files when it was tried,
    because the package is imported by most of the suite -- a "selector" that
    returns 93% of the tree is laundering a full run through a narrowing story,
    which is worse than an honest full run because it claims to have reasoned.

    Asserted on BOTH sides so it cannot rot into a check that always passes:
    the raw source must still contain the citation (otherwise this test is
    measuring nothing) and the stripped code must not.
    """
    citing = _ROOT / "linkedin_server" / "server.py"
    _skip_if_moved("linkedin_server/server.py")
    raw = citing.read_text(encoding="utf-8", errors="replace")
    needle = "2026-09-03-linkedin-gap-blockers.md"
    if needle not in raw:
        pytest.fail(
            f"{citing.name} no longer cites {needle}, so this test has nothing "
            "to discriminate. Re-aim it at another prose citation rather than "
            "deleting it -- the distinction it guards is still live."
        )
    assert needle not in G.code_text(citing), (
        "the citation survived the prose strip, so comments and docstrings "
        "are being read as dependencies again. That is the 93-of-170 failure."
    )


# --------------------------------------------------------------------------
# AN EMPTY SET IS A LOUD EVENT.
# --------------------------------------------------------------------------

def test_an_unreachable_path_widens_instead_of_passing_quietly(capsys):
    """An empty selection must never read as a pass.

    From outside, a selector that found nothing and a selector that is BROKEN
    produce exactly the same output, so the gate may not treat the first as
    good news. It widens to the full suite and says why.

    **THE SENTINEL IS ASSEMBLED RATHER THAN WRITTEN, and the reason is a
    finding.** Spelled as one literal, the first version of this test failed:
    the gate selected THIS FILE, because this file's own source named the
    path, which is exactly what the data rule is supposed to do. A sentinel
    meant to be unreachable cannot be spelled in the corpus it is unreachable
    from. Leaving it split keeps the empty case genuinely empty, and the
    accident is worth recording -- it is the rule demonstrating itself against
    a file written to have no dependencies at all.
    """
    unreachable = "zzzz-no-such" + "-dir/zzzz-no-such" + "-file.md"
    code = G.main(["--paths", unreachable, "--plan-only"])
    said = capsys.readouterr().err
    assert code == 0
    assert "WIDENING TO THE FULL SUITE" in said, (
        "an empty impact set printed no widening notice; a gate that goes "
        f"quiet here has stopped being a gate. Said: {said!r}"
    )
    assert "EMPTY impact set" in said


def test_a_runner_wide_change_refuses_to_scope(capsys):
    """`tests/conftest.py` holds AUTOUSE fixtures: loaded by all, named by none.

    It is the sharpest member of the class the analyser has no model of, and
    scoping on it would be a guess dressed as an analysis.
    """
    code = G.main(["--paths", "tests/conftest.py", "--plan-only"])
    said = capsys.readouterr().err
    assert code == 0
    assert "WIDENING TO THE FULL SUITE" in said
    assert "NO MODEL OF" in said


# --------------------------------------------------------------------------
# THE GATE MAY NOT CLAIM MORE THAN IT CHECKED.
# --------------------------------------------------------------------------

def test_a_scoped_plan_names_what_it_did_not_run(capsys):
    """The honesty requirement, asserted on the gate's real output.

    A gate that prints PASS after running a handful of 6081 tests has told a
    dangerous half-truth: the word means "everything I check is green" to
    whoever wrote it and "this change is fine" to whoever reads it. The
    unrun count is therefore part of the verdict, not a footnote, and this
    test fails if it is ever demoted to one.
    """
    _skip_if_moved(LEDGER)
    impact = G.impact_set([LEDGER])
    assert impact.test_files, "precondition: the ledger must select something"
    G.report_scope(impact.test_files, ran=41, seconds=1.0)
    said = capsys.readouterr().err
    assert "NOT CHECKED" in said
    assert "windows-only" in said.lower(), (
        "the scope report must say this is a single-platform signal. CI runs "
        "three platforms and is the certifier; a green gate here is not a "
        "reason to shrink that matrix."
    )


# --------------------------------------------------------------------------
# THE CORPUS-WIDE FLOOR -- the category no coupling rule can reach.
# --------------------------------------------------------------------------

#: The two proven members, named by a sibling wave that shipped red to CI
#: TWICE in one day without them: "a local selection that ran the files I
#: touched and their neighbours and missed guards whose names connect to
#: nothing I was working on".
PROVEN_CORPUS_WIDE = (
    "tests/test_no_committed_identity.py",
    "tests/test_page_text_is_never_printed.py",
)


def test_the_floor_is_derived_and_still_finds_the_two_proven_guards():
    """The derivation is CHECKED, not believed.

    `always_run_files` detects corpus-wide sweeps by looking for an
    enumeration the diff cannot narrow -- `git ls-files`, a walk of the repo
    root, or a sweep spanning two or more top-level folders. A hand-written
    list would have been correct for exactly these two names and blind to the
    next one, which is the mistake the boundary gate's docstring already warns
    about in its own domain.

    So the list is derived, and this pins the derivation against the two cases
    that are known to have cost CI cycles. If a refactor ever narrows the
    detector past them, this fails and names them rather than letting the
    floor quietly shrink.
    """
    floor = {rel for rel, _ in G.always_run_files(G.Corpus())}
    for proven in PROVEN_CORPUS_WIDE:
        assert proven in floor, (
            f"{proven} fell out of the corpus-wide floor. It sweeps the whole "
            "tracked set and names nothing, so NO coupling rule will ever "
            "select it -- the floor is the only thing that runs it. A sibling "
            "wave shipped red twice in one day for exactly this."
        )


def test_the_floor_runs_even_when_the_diff_couples_to_nothing():
    """A diff with an empty selection still gets the corpus-wide guards.

    This is the whole point of the category: `test_no_committed_identity.py`
    sweeps every tracked file INCLUDING `.md` and `.tsv`, so a census edit can
    trip it while naming nothing the analyser can follow.
    """
    unreachable = "zzzz-no-such" + "-dir/zzzz-no-such" + "-file.md"
    impact = G.impact_set([unreachable])
    assert not impact.selected, "precondition: nothing should be selected"
    for proven in PROVEN_CORPUS_WIDE:
        assert proven in impact.test_files, (
            f"{proven} must be in the plan even when the selector finds "
            "nothing at all."
        )


def test_the_floor_does_not_mask_an_empty_selection(capsys):
    """THE TRAP, asserted so it cannot be reintroduced.

    The floor is never empty. If the gate's "empty impact set" alarm were
    tested against the PLAN rather than against the SELECTION, adding this
    category would have made that alarm unreachable forever -- a check that
    cannot fail, introduced by the very change meant to make the gate safer,
    and invisible because everything would still look green.

    So: a change that couples to nothing must STILL widen and STILL say why,
    with the floor present in the plan.
    """
    unreachable = "zzzz-no-such" + "-dir/zzzz-no-such" + "-file.md"
    impact = G.impact_set([unreachable])
    assert impact.always_run, "precondition: the floor must be non-empty"
    G.main(["--paths", unreachable, "--plan-only"])
    said = capsys.readouterr().err
    assert "EMPTY impact set" in said, (
        "the floor masked an empty selection. The alarm must test "
        "`impact.selected`, never `impact.test_files` -- the floor is a "
        f"guarantee about the corpus, not evidence the analyser ran. {said!r}"
    )


def test_turning_the_floor_off_removes_exactly_the_floor():
    """The floor shown ABSENT, so its presence elsewhere means something.

    A category that is always on is indistinguishable from one hard-coded
    into the plan; this arm separates them.
    """
    _skip_if_moved(LEDGER)
    with_floor = G.impact_set([LEDGER])
    without = G.impact_set([LEDGER], always_run=False)
    assert without.always_run == []
    assert without.selected == with_floor.selected, (
        "turning the floor off changed the SELECTION, so the two categories "
        "are entangled. They must be computed independently."
    )
    for proven in PROVEN_CORPUS_WIDE:
        if proven not in with_floor.selected:
            assert proven not in without.test_files, (
                f"{proven} survived with the floor off, so something else is "
                "pulling it in and the floor is not what is protecting us."
            )
