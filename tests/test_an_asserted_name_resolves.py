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
    assert not any(s.name == "linkedin_zzz_quoted_output" for s in sites), (
        "a name inside a ``` fence reached the classifier at all. Quoted tool "
        "output is not the document speaking."
    )


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


def test_the_table_slot_still_reproduces_the_registry():
    """The blocker table-cell slot selects exactly the ledger's 97 names.

    This is the whole precision argument for the slot, asserted rather than
    believed. It was measured at 358 selected cells, 353 naming a ledger
    blocker, 97 distinct -- the registry, reproduced by position alone.
    """
    corpus = guard.load_corpus(REPO)
    ledger = set(guard.blocker_registry(REPO))
    picked: set[str] = set()
    for lines in corpus.values():
        _heads, cols = guard.table_headers(lines)
        for n, line in enumerate(lines, 1):
            for name, form in guard._blocker_candidates(line, cols[n]):
                if form == "table-cell":
                    picked.add(name)
    assert ledger <= picked, (
        f"{len(ledger - picked)} of the ledger's blockers are no longer "
        "selected by the table-cell slot: "
        f"{sorted(ledger - picked)[:8]}. The slot has narrowed, so the guard is "
        "now blind wherever those names are cited."
    )
    stray = picked - ledger
    assert len(stray) <= 6, (
        f"the table-cell slot now picks up {len(stray)} names the ledger does "
        f"not know, up from 6: {sorted(stray)}. Either real new blockers were "
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
