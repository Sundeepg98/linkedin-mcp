"""A name a tracked `_audit/` document ASSERTS must resolve in the tree.

WHAT THIS MODULE PINS, AND IT IS TODAY'S DEFECT RATHER THAN THE FIX. Four
asserted-and-absent citations are live in the corpus right now. This wave
DETECTED them and is deliberately not repairing them -- the fixer should not be
the detector, and three sibling waves hold the documents involved. So the pin
below is an EXACT set, and it fails in both directions on purpose:

    a NEW bad citation appears   -> RED. The guard did its job.
    a pinned one is repaired     -> RED, saying so, and asking for the pin to
                                    be narrowed. A record of a defect may not
                                    outlive the defect, and a repair must not
                                    be able to happen in silence.

GREEN HERE DOES NOT MEAN THE CORPUS IS CLEAN. It means the corpus holds exactly
the four defects that were measured on 2026-09-20 and no others.

THE CONTROLS ARE NOT DECORATION, and this repository has an expensive reason
for saying so: a sibling wave measured that 56 of 88 probe files carry a control
that is computed, printed, and never branched on. Each control below ASSERTS.

    1. `test_the_detector_finds_a_planted_assertion` -- the guard's guaranteed
       failure mode is finding NOTHING, at which point the pin passes for the
       wrong reason forever. A fabricated name is pushed through the real
       classifier in each of the three slot forms and must come back
       ASSERTED-ABSENT.
    2. `test_every_marker_class_fires_on_the_real_corpus` -- a suppressor that
       never fires is dead code that looks like rigour, and a dead suppressor
       is how this guard would quietly widen into a guard that convicts
       everybody. Every one of the six marker verdicts must be earned by a real
       corpus line.
    3. `test_the_table_slot_still_reproduces_the_registry` -- the blocker slot's
       whole claim to precision is that, over the corpus, it selects exactly the
       ledger's 97 names. If that stops being true the slot has drifted and
       every count in `_audit/2026-09-20-names-that-do-not-exist.md` is stale.
    4. `test_the_guard_stays_cheap_enough_to_gate` -- the two 120-second
       scripts in this repository got that way one convenience at a time.
"""
from __future__ import annotations

import pathlib
import sys
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_asserted_names_resolve as guard  # noqa: E402


#: (kind, name, document, occurrences) -- measured at 8b58dcb, 2026-09-20.
#: Named in `_audit/2026-09-20-names-that-do-not-exist.md` with the evidence.
PINNED: set[tuple[str, str, str, int]] = {
    ("BLOCKER", "ALERTS-PAGE-UNREAD",
     "_audit/2026-09-20-the-contingent-writeoffs.md", 1),
    ("BLOCKER", "PROXIMITY-NOT-PARSED",
     "_audit/2026-09-20-the-contingent-writeoffs.md", 2),
    ("TOOL", "linkedin_applied_jobs",
     "_audit/2026-09-20-the-contingent-writeoffs.md", 1),
}

#: Every verdict the classifier can hand down other than the finding itself.
#: Kept as an explicit list so that ADDING a suppressor without a corpus
#: example fails control 2 rather than passing unnoticed.
MARKERS = (
    "MARKED-HYPOTHETICAL",
    "MARKED-PROPOSAL",
    "MARKED-PROPOSAL-DOC",
    "MARKED-PROPOSAL-TABLE",
    "MARKED-ABSENT",
    "MARKED-SPEC-DOC",
)


@pytest.fixture(scope="module")
def measured():
    sites, bad = guard.run(REPO)
    return sites, bad


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------
def test_the_registry_cannot_absorb_a_name_from_its_own_instruments():
    """The guard may not be fed by its own commentary. THIS ONE ALREADY FIRED.

    The registry shipped reading `linkedin_server/`, `scripts/` AND `tests/`,
    and was measured correct at 4 findings. Then the guard was committed. Its
    docstring names `linkedin_applied_jobs` as the worked example; the control
    below plants `linkedin_zzz_not_a_real_tool`. Both strings landed in
    `scripts/` and `tests/`, the registry swallowed them, and the next run
    reported ZERO absent tool names -- with the pin going red in the direction
    that reads "these defects were repaired". Nothing was repaired.

    **Writing ABOUT a name is not the name existing.** That is the corpus defect
    this whole wave is about, and the guard committed it against itself inside
    an hour. The three names below are the exact ones that did it, so this
    assertion is a regression test for a real event rather than a hypothetical.
    """
    registry = guard.tool_registry(REPO)
    absorbed = [
        name for name in (
            "linkedin_zzz_not_a_real_tool",   # planted in THIS file, below
            "linkedin_zzz_quoted_output",     # planted in THIS file, below
            "linkedin_applied_jobs",          # named in the guard's docstring
            "linkedin_leave_group",           # named in the guard's docstring
        )
        if name in registry
    ]
    assert absorbed == [], (
        f"the tool registry has absorbed {absorbed} from the guard's own "
        "instruments. A name mentioned in a test, a script or a document is "
        "prose; only `linkedin_server/` is the server. A registry that reads "
        "its own commentary goes silently blind exactly where it is being "
        "written about, which is where the defects are."
    )
    assert len(registry) > 40, (
        f"the registry holds only {len(registry)} names. It was 59. A registry "
        "that has collapsed convicts the whole corpus; check that "
        "`git ls-files linkedin_server` still answers before widening anything."
    )


def test_the_partial_parse_refusal_can_actually_fire(monkeypatch):
    """The guard REFUSES to run on a partial ledger parse. Prove the refusal.

    An unproven refusal is the same disease as an unproven check. This one
    matters more than most: if `ledger_counts()` ever returns a partial parse --
    a renamed table header is enough, and it has happened here before -- then
    real blockers read as absent and the guard convicts the corpus for the
    PARSER's failure, loudly and wrongly, in the most credible-looking way
    available to it.

    Driven both directions, because a refusal that fires on everything is as
    useless as one that fires on nothing.
    """
    import build_blocker_map as bbm

    monkeypatch.setattr(bbm, "ledger_counts", lambda: {"ONLY-ONE": 1})
    with pytest.raises(RuntimeError) as caught:
        guard.blocker_registry(REPO)
    assert "not ~97" in str(caught.value), (
        "the refusal fired but did not say what it saw. A refusal that reports "
        "only what it did NOT match is half a measurement."
    )

    monkeypatch.undo()
    assert len(guard.blocker_registry(REPO)) == 97, (
        "the refusal now fires on the REAL ledger parse, or the ledger no "
        "longer holds 97 blockers. Either way every blocker verdict in this "
        "module is resting on a set that moved."
    )


def test_the_detector_finds_a_planted_assertion():
    """The detector can speak -- in every slot form, on a name it cannot know.

    Run through the REAL classifier, not a copy of its logic. A control that
    re-implements the thing it is controlling proves only that the author can
    write the same bug twice (INSTRUMENTS 1.3, `GUARDS-ITS-OWN-COPY`).
    """
    planted = {
        "_audit/_planted.md": [
            "Row `J 1` -- **GAP**, blocker `ZZZ-NOT-A-REAL-BLOCKER`, queue BUILD.",
            "A single `ZZZ-SECOND-FAKE` blocker holds the rest.",
            "",
            "| row | blocker | note |",
            "|---|---|---|",
            "| `J 2` | `ZZZ-THIRD-FAKE` | a cell under a blocker header |",
            "",
            "Rows 1-3 are COVERED-PROVEN, `linkedin_zzz_not_a_real_tool`.",
        ]
    }
    sites = guard.classify(
        planted, guard.tool_registry(REPO), set(guard.blocker_registry(REPO))
    )
    found = {(s.kind, s.name) for s in sites if s.verdict == "ASSERTED-ABSENT"}
    assert found == {
        ("BLOCKER", "ZZZ-NOT-A-REAL-BLOCKER"),
        ("BLOCKER", "ZZZ-SECOND-FAKE"),
        ("BLOCKER", "ZZZ-THIRD-FAKE"),
        ("TOOL", "linkedin_zzz_not_a_real_tool"),
    }, (
        "the detector did not convict a planted, unmarked, unresolvable name in "
        f"every slot form. It found {sorted(found)}. Until this passes, every "
        "other assertion in this module passes for the wrong reason -- a "
        "detector that finds nothing cannot fail."
    )


def test_a_marked_name_is_not_convicted():
    """The other half of the control: the marks must actually suppress.

    Without this, the detector above could be passing because it convicts
    EVERYTHING, which is the failure mode that gets a guard suppressed rather
    than the one that gets it ignored.
    """
    planted = {
        "_audit/_planted_marked.md": [
            "**New blocker: `ZZZ-MINTED-HERE` -- 2 rows, queue BUILD.**",
            "A `ZZZ-HYPOTHETICAL` blocker would have merged the two.",
            "",
            "| rows | successor blocker (proposed) | note |",
            "|---|---|---|",
            "| `J 2` | `ZZZ-PROPOSED-CELL` | under a proposal header |",
            "",
            "```",
            "E  assert {'linkedin_zzz_quoted_output'} == set()",
            "```",
            "",
            "    FORBIDDEN = {",
            "        \"linkedin_zzz_indented_quote\",",
            "    }",
            "",
            "Rows 1-3 are COVERED-PROVEN, `ZZZ-INDENTED-BLOCKER` under it.",
        ]
    }
    sites = guard.classify(
        planted, guard.tool_registry(REPO), set(guard.blocker_registry(REPO))
    )
    convicted = [s for s in sites if s.verdict == "ASSERTED-ABSENT"]
    assert convicted == [], (
        "a marked proposal, a modal, a proposal-table cell or fenced tool "
        f"output was convicted: {[str(s) for s in convicted]}. A guard that "
        "cannot be satisfied is a guard that gets suppressed."
    )
    for quoted in ("linkedin_zzz_quoted_output", "linkedin_zzz_indented_quote"):
        assert not any(s.name == quoted for s in sites), (
            f"{quoted} reached the classifier at all. Quoted source is not the "
            "document speaking, and this corpus quotes it BOTH ways -- ``` "
            "fences and 4-space indented blocks."
        )

    # THE INDENTED HALF IS EXERCISED HERE BECAUSE THE CORPUS NO LONGER
    # EXERCISES IT. A red-proof deleted `fenced()`'s indent handling entirely
    # and the guard's corpus-wide candidate count did not move by one: the
    # document that motivated it -- `_slice-parity-census.md` quoting
    # `FORBIDDEN_TOOLS` -- is independently covered by `CONTRACT_MODULES`, and
    # no other indented block in 167 files carries a candidate-shaped name.
    # So the mechanism is CORRECT and currently LOAD-BEARING NOWHERE, which is
    # precisely the state in which a component rots unnoticed. This synthetic
    # block is the only thing that will notice.


def test_every_marker_class_fires_on_the_real_corpus(measured):
    """No suppressor may be dead code."""
    sites, _bad = measured
    seen = {s.verdict for s in sites}
    missing = [m for m in MARKERS if m not in seen]
    assert missing == [], (
        f"these suppressors matched nothing in the whole corpus: {missing}. A "
        "suppressor with no example is untested width -- it can only ever "
        "excuse something in future, and nothing has ever shown it excusing "
        "the right thing. Either find its corpus example and cite it in "
        "`_audit/2026-09-20-names-that-do-not-exist.md`, or delete it."
    )


#: Every header spelling the predicate recognises in this corpus, with the
#: table-cell selections each one actually brings. They sum to the measured
#: total of 360, which is the check that caught the first version of this list:
#: an earlier count attributed each selection to EVERY blocker column in its
#: table, so a two-blocker-column table double-counted and the parts summed to
#: 20 against a total of 13. The numbers now reconcile.
#:
#: `first blocker, corrected` carries ZERO cells and is kept deliberately. It is
#: a real header the predicate matches; its column simply holds no UPPER-KEBAB
#: name today. Dropping it would narrow the list to what the corpus happens to
#: exercise, which is how a predicate quietly stops covering its own domain.
BLOCKER_HEADER_SPELLINGS = (
    "blocker",                        # 347 selections
    "successor blocker (proposed)",   #   5
    "the blocker",                    #   4
    "new blocker",                    #   2
    "blocker name",                   #   2
    "first blocker, corrected",       #   0 -- matched, and carries no names
)


def test_the_table_slot_still_recognises_every_header_spelling():
    """The header predicate, tested DIRECTLY -- because the union test could not.

    **THIS ASSERTION REPLACES ONE THAT COULD NOT FAIL, AND THE REPLACEMENT IS
    THE POINT.** The first version asked whether all 97 ledger blockers still
    appear SOMEWHERE in the table-cell slot's output, and its docstring called
    that "the whole precision argument for the slot, asserted rather than
    believed". It was not. A red-proof narrowed the header predicate from a
    substring test to an exact match -- removing twelve genuinely
    blocker-labelled columns across the corpus -- and the test **passed
    cleanly**, because this corpus is redundant enough that every one of the 97
    is also cited under a bare `blocker` header or in a backtick phrase slot
    somewhere else. A union claim over a redundant corpus cannot see a
    narrowing. It was a check that could not fail, in the module whose own
    docstring says why that is the expensive kind.

    So the predicate is exercised directly, on a synthetic table per spelling,
    through the real `table_headers` / `_blocker_candidates` path. Narrow the
    predicate and this goes red on the first spelling it drops.
    """
    ledger_name = sorted(guard.blocker_registry(REPO))[0]
    missed = []
    for spelling in BLOCKER_HEADER_SPELLINGS:
        lines = [
            f"| row | {spelling} | note |",
            "|---|---|---|",
            f"| `J 1` | `{ledger_name}` | a cell under a blocker header |",
        ]
        _heads, cols = guard.table_headers(lines)
        found = [
            name for name, form in guard._blocker_candidates(lines[2], cols[3])
            if form == "table-cell"
        ]
        if found != [ledger_name]:
            missed.append(spelling)
    assert missed == [], (
        f"the header predicate no longer recognises these spellings as blocker "
        f"columns: {missed}. Every one of them carries real blocker cells in "
        "the corpus today. A narrowing here does not announce itself -- the "
        "guard simply stops looking at those columns, and the union of names it "
        "still finds elsewhere hides the loss completely."
    )


def test_the_table_slot_still_reproduces_the_registry():
    """The slot's coverage claim: all 97, plus a floor on how much it selects.

    Kept alongside the predicate test above, not instead of it. This one
    catches a slot that COLLAPSES; that one catches a slot that NARROWS. The
    red-proof showed they are different failures and only one of them was
    covered.
    """
    corpus = guard.load_corpus(REPO)
    ledger = set(guard.blocker_registry(REPO))
    picked: set[str] = set()
    selections = 0
    for lines in corpus.values():
        _heads, cols = guard.table_headers(lines)
        for n, line in enumerate(lines, 1):
            for name, form in guard._blocker_candidates(line, cols[n]):
                if form == "table-cell":
                    picked.add(name)
                    selections += 1
    assert ledger <= picked, (
        f"{len(ledger - picked)} of the ledger's blockers are no longer "
        "selected by the table-cell slot: "
        f"{sorted(ledger - picked)[:8]}. The slot has narrowed, so the guard is "
        "now blind wherever those names are cited."
    )
    assert selections >= 340, (
        f"the table-cell slot now makes {selections} selections, down from 360. "
        "A drop of that size means whole columns stopped being recognised. The "
        "set of names may still look complete because the corpus cites most "
        "blockers in several places -- check "
        "`test_the_table_slot_still_recognises_every_header_spelling` before "
        "lowering this floor."
    )
    stray = picked - ledger
    assert len(stray) <= 6, (
        f"the table-cell slot now picks up {len(stray)} names the ledger does "
        f"not know, up from 5: {sorted(stray)}. Either real new blockers were "
        "minted (re-measure and re-pin) or the slot has widened into some "
        "other vocabulary, which is how this guard loses its precision."
    )


def test_the_guard_stays_cheap_enough_to_gate():
    """A slow guard gets excluded from the gate and then protects nothing.

    The bound is deliberately loose. It is not a benchmark; it is a tripwire
    for the QUADRATIC rewrite -- `scripts/find_blocker_reason.py` re-scans the
    corpus once per blocker and takes over 120 seconds. Measured here at ~2s.
    """
    start = time.monotonic()
    guard.run(REPO)
    elapsed = time.monotonic() - start
    assert elapsed < 25.0, (
        f"the guard took {elapsed:.1f}s. It was 2s when written, and the "
        "difference between those two numbers is almost always a per-item "
        "re-scan of the corpus. Read it once and index it."
    )


# --------------------------------------------------------------------------
# THE PIN
# --------------------------------------------------------------------------
def test_no_new_asserted_name_is_absent(measured):
    _sites, bad = measured
    current: dict[tuple[str, str, str], int] = {}
    for s in bad:
        current[(s.kind, s.name, s.doc)] = current.get((s.kind, s.name, s.doc), 0) + 1
    seen = {(k[0], k[1], k[2], n) for k, n in current.items()}

    appeared = sorted(seen - PINNED)
    repaired = sorted(PINNED - seen)
    assert not appeared, (
        f"a document now asserts a name that resolves nowhere in the tree: "
        f"{appeared}. This is the defect class four separate waves tripped over "
        "on 2026-09-20 -- it does not read as a dangling reference, it reads as "
        "a plausible wrong answer, so the next reader stops instead of looking. "
        "Either the name should exist and does not, or the document should mark "
        "it (see the marks enumerated in "
        "`scripts/check_asserted_names_resolve.py`)."
    )
    assert not repaired, (
        f"these pinned defects are gone: {repaired}. If they were REPAIRED, "
        "that is good and the pin above must be narrowed in the same commit -- "
        "a record of a defect may not outlive the defect. If instead the "
        "DETECTOR stopped seeing them, the pin just hid a regression, so check "
        "`test_the_detector_finds_a_planted_assertion` before editing PINNED."
    )
