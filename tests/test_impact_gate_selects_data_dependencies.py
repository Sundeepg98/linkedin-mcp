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
    # ALL THREE DATA-REACHING RULES, NOT ONE. When the composed-name rule and
    # the observed read map were added on 2026-09-21 this control went RED
    # with ``data_coupling=False`` alone, and it was RIGHT to: the assertion
    # it makes is "nothing else silently reaches this", and something else
    # now did. A control that names one switch while the code has three has
    # quietly stopped controlling the thing it claims to.
    reverted = G.impact_set([LEDGER], data_coupling=False,
                            composed_coupling=False, observed_coupling=False)
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


# --------------------------------------------------------------------------
# THE COMPOSED-NAME RULE, added 2026-09-21. A positive arm, a negative arm,
# and a NARROWING arm -- because a rule with no narrowing arm cannot be shown
# to discriminate, and a selector that does not discriminate is a floor.
# --------------------------------------------------------------------------

#: A fixture read through a stem the reading file NEVER spells out as a
#: filename: ``tests/test_free_read_panels.py`` holds
#: ``HYDRATED = "job_detail_hydrated"`` and opens ``FIXTURES /
#: f"{HYDRATED}.html"``. Before the composed rule existed, the analyser
#: selected 22 test files for this fixture and that reader was not among them.
COMPOSED_FIXTURE = "tests/fixtures/job_detail_hydrated.html"
COMPOSED_READER = "tests/test_free_read_panels.py"

#: A fixture whose stem is composed TWICE --
#: ``markup(f"jobs_tracker_{which}")`` in ``tests/test_tracker_readiness.py``,
#: which then appends ``.html``. The string ``jobs_tracker_row.html`` appears
#: nowhere in the file that reads it.
TWICE_COMPOSED_FIXTURE = "tests/fixtures/jobs_tracker_row.html"
TWICE_COMPOSED_READER = "tests/test_tracker_readiness.py"

#: A script this suite loads by PATH rather than by import --
#: ``importlib.util.spec_from_file_location``, which no import parser can see.
#: Twenty-five test files here do it, because ``scripts/`` is not a package.
LOADED_BY_PATH = "tests/fixtures/synthetic/drawn_routes.txt"
LOADED_BY_PATH_SCRIPT = "scripts/drawn_route_corpus.py"
LOADED_BY_PATH_READER = "tests/test_premium_four_boundary.py"


def test_a_composed_stem_reaches_the_file_that_composes_it():
    """The positive arm of the rule that made this wave necessary."""
    _skip_if_moved(COMPOSED_FIXTURE, COMPOSED_READER)
    impact = G.impact_set([COMPOSED_FIXTURE])
    assert COMPOSED_READER in impact.selected, (
        f"{COMPOSED_READER} opens {COMPOSED_FIXTURE} through a stem held in a "
        "module constant, so the basename never appears where the file is "
        f"read. Selected: {impact.selected}"
    )


def test_a_twice_composed_stem_reaches_it_too():
    """The harder shape: a literal prefix plus a hole, extension added later."""
    _skip_if_moved(TWICE_COMPOSED_FIXTURE, TWICE_COMPOSED_READER)
    impact = G.impact_set([TWICE_COMPOSED_FIXTURE])
    assert TWICE_COMPOSED_READER in impact.selected, (
        f"{TWICE_COMPOSED_READER} builds this name in two steps and the "
        f"analyser must follow both. Selected: {impact.selected}"
    )


def test_reverting_the_composed_rule_loses_those_readers_again():
    """THE CONTROL. Both specimens must go dark when the rule is disarmed.

    ``observed_coupling`` is disarmed with it, because the recorded read map
    supplies the same edge from another direction and would let this arm pass
    while proving nothing about the rule it names.
    """
    _skip_if_moved(COMPOSED_FIXTURE, COMPOSED_READER,
                   TWICE_COMPOSED_FIXTURE, TWICE_COMPOSED_READER)
    for data_file, reader in ((COMPOSED_FIXTURE, COMPOSED_READER),
                              (TWICE_COMPOSED_FIXTURE, TWICE_COMPOSED_READER)):
        reverted = G.impact_set([data_file], composed_coupling=False,
                                observed_coupling=False)
        assert reader not in reverted.selected, (
            f"with the composed rule reverted, {data_file} must NOT reach "
            f"{reader} -- that is the 2026-09-21 hole. It was found anyway, "
            "so either another rule is over-selecting or this control no "
            f"longer controls anything. Found: {reverted.selected}"
        )


def test_the_composed_rule_refuses_a_shape_the_reader_enumerates():
    """The NARROWING arm, which is what stops the rule being a floor.

    ``f"{x}.html"`` fullmatches every html basename in the tree. A rule that
    coupled on the shape alone would add the same handful of files to EVERY
    fixture change: selection-shaped output with no selection in it. So a file
    that demonstrably ENUMERATES names of that shape as literals, and does not
    enumerate this one, is left out.

    ``tests/test_free_read_panels.py`` names exactly one html literal and it is
    not a tracker capture, so a tracker capture must not drag it in.
    """
    _skip_if_moved(TWICE_COMPOSED_FIXTURE, COMPOSED_READER)
    narrowed = G.impact_set([TWICE_COMPOSED_FIXTURE], observed_coupling=False)
    assert COMPOSED_READER not in narrowed.selected, (
        f"{COMPOSED_READER} does not read {TWICE_COMPOSED_FIXTURE}; it was "
        "selected anyway, so the composed rule has stopped discriminating and "
        f"is coupling on the extension alone. Selected: {narrowed.selected}"
    )


def test_a_script_loaded_by_path_carries_its_data_to_the_loader():
    """``spec_from_file_location`` is an import no import parser can read."""
    _skip_if_moved(LOADED_BY_PATH, LOADED_BY_PATH_SCRIPT, LOADED_BY_PATH_READER)
    impact = G.impact_set([LOADED_BY_PATH], observed_coupling=False)
    assert LOADED_BY_PATH_READER in impact.selected, (
        f"{LOADED_BY_PATH_READER} loads {LOADED_BY_PATH_SCRIPT} by path and "
        f"that script opens {LOADED_BY_PATH}. Selected: {impact.selected}"
    )


def test_reverting_the_import_walk_loses_the_path_loader():
    """THE CONTROL for the hop above."""
    _skip_if_moved(LOADED_BY_PATH, LOADED_BY_PATH_READER)
    reverted = G.impact_set([LOADED_BY_PATH], import_coupling=False,
                            observed_coupling=False)
    assert LOADED_BY_PATH_READER not in reverted.selected, (
        "with the import walk off, a two-hop path-load must not be found. "
        f"Found: {reverted.selected}"
    )


# --------------------------------------------------------------------------
# THE OBSERVED READ MAP. It is a recording, so both of its failure modes are
# pinned: it must only ADD, and its ABSENCE must be spoken rather than read as
# an empty recording.
# --------------------------------------------------------------------------

def test_the_observed_map_only_ever_adds_to_a_plan():
    """A recording may widen a plan. It may never trim one.

    A test written since the recording is absent from it, and absence read as
    "nothing reads this" is the defect this whole gate exists to refuse,
    rebuilt inside the gate out of a cache.
    """
    probed = 0
    for probe in (LEDGER, COMPOSED_FIXTURE, EVIDENCE_TSV):
        if not (_ROOT / probe).exists():
            continue
        probed += 1
        without = set(G.impact_set([probe], observed_coupling=False).test_files)
        with_map = set(G.impact_set([probe]).test_files)
        assert without <= with_map, (
            f"the read map REMOVED {sorted(without - with_map)} from the plan "
            f"for {probe}. It is additive by law; something is reading it as "
            "an authority instead of as an addition."
        )
    assert probed, (
        "no probe path existed, so this test asserted nothing at all -- which "
        "is the shape of a check that cannot fail. Re-aim it."
    )


def test_an_absent_read_map_is_reported_and_never_read_as_empty(monkeypatch):
    """No map on disk is an UNKNOWN, and the gate has to say so.

    ``{}`` and None are the same value to a careless caller and completely
    different findings: one says the recording found nothing, the other says
    there was no recording.
    """
    monkeypatch.setattr(G, "_READ_MAP_CACHE", _ROOT / "no-such-read-map.json")
    assert G.read_map() is None, (
        "a missing read map must read as None, never as an empty recording."
    )
    edges, stamp = G.observed_readers([LEDGER])
    assert edges == {} and stamp is None
    impact = G.impact_set([LEDGER])
    assert impact.read_map_stamp is None, (
        "the Impact must carry the ABSENCE so the report can print it; a "
        "silent default here is how a missing recording becomes invisible."
    )
