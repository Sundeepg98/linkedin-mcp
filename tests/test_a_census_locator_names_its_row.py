"""A locator into a census slice must NAME the row it is evidence for.

WHAT THIS MODULE PINS, AND WHY THE PIN IS EMPTY. The sibling module
`test_an_asserted_name_resolves.py` pins four live defects because its wave
detected them and deliberately did not repair them. This wave DID repair: all
76 line-number locators in `_audit/_census/blocker-assignments.tsv` were
converted to row-label citations in the same commit that added the guard, so
the expected set of failures is EMPTY.

AN EMPTY PIN IS THE MOST DANGEROUS KIND OF GREEN, so it is not resting on
itself. `zero findings` and `a detector that cannot find anything` look
identical from the outside, and this repository has removed several checks that
turned out to be the second. Four controls stand between them:

    1. `test_the_resolver_can_say_RESOLVES` -- a MANUFACTURED census, six rows
       written into this file, whose true locations were confirmed by hand.
       If the resolver cannot say RESOLVES on that, every green below is
       meaningless. It is manufactured rather than found in the repo because a
       control that reads ambient repo state passes on the box it was written
       on and fails in every clone.
    2. `test_every_verdict_is_reachable` -- each failing verdict is earned on
       the same fixture. A verdict the resolver cannot emit is a class of
       defect it cannot report.
    3. `test_a_planted_wrong_row_locator_is_convicted` -- the plant goes into a
       COPY of the REAL file and through the REAL `run()`, because a mechanism
       proven only on a synthetic corpus has not been shown to reach the
       corpus that matters.
    4. `test_a_row_label_is_a_unique_key` -- the whole repair rests on the
       claim that a row label identifies one row. Measured here, not assumed.

NOTHING IN THIS MODULE MUTATES THE TREE. Four other waves are moving census
rows; the plant is written to a temp copy.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import time

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_census_locators_resolve as guard  # noqa: E402
import count_census_states as census  # noqa: E402


#: (row_id, verdict) pairs expected to FAIL on the live file. EMPTY BY REPAIR.
#: A new entry here must name the row and say why it cannot be converted.
PINNED: frozenset[tuple[str, str]] = frozenset()


# --------------------------------------------------------------------------
# THE MANUFACTURED CENSUS
#
# Hand-written, and the line numbers in the comments were confirmed by counting
# them. It carries every shape the real slices carry: bare numeric labels, an
# `L`-prefixed label (profile.md really numbers its section L that way, which
# is the collision that makes shape-based kind detection wrong), a bold
# grouping row, and a compound cost row whose own first cell is `2-3`.
# --------------------------------------------------------------------------
FIXTURE = "\n".join([
    "# A census slice that does not exist",          # line 1
    "",                                              # 2
    "| # | capability | R/W | state | note |",        # 3
    "|---|---|---|---|---|",                          # 4
    "| 1 | the first thing | R | GAP | none |",       # 5
    "| 2 | the second thing | W | COVERED-PROVEN | none |",   # 6
    "| 3 | the third thing | R | GAP | none |",       # 7
    "| L1 | an L-prefixed row | R | GAP | none |",    # 8
    "",                                              # 9
    "| rows | gap | shape |",                        # 10
    "|---|---|---|",                                 # 11
    "| 2-3 | a compound cost row | a shape |",       # 12
    "| **Grouped roll-up** (a, b, c) | 1, 2, 3 (3) | R | REV | none |",  # 13
    "",
])

#: Confirmed by hand against the list above, and asserted in the first test so
#: that an edit to FIXTURE which moves a row fails loudly instead of quietly
#: invalidating every expectation below.
TRUE_LINES = {"1": 5, "2": 6, "3": 7, "L1": 8, "2-3": 12, "Grouped roll-up": 13}


@pytest.fixture(scope="module")
def fixture_index():
    return guard.build_index(FIXTURE, "X")


@pytest.fixture(scope="module")
def measured():
    return guard.run(REPO)


# --------------------------------------------------------------------------
# CONTROLS
# --------------------------------------------------------------------------
def test_the_resolver_can_say_RESOLVES(fixture_index):
    """THE POSITIVE CONTROL. An all-negative run from an uncontrolled
    instrument is indistinguishable from an instrument that cannot say yes.

    The fixture's true locations are stated above and checked here first, so
    this control cannot drift into agreeing with a broken index.
    """
    for label, line in TRUE_LINES.items():
        assert label in fixture_index.labels, (
            f"the manufactured census has a row labelled {label!r} on line "
            f"{line} and the index did not find it. Every expectation in this "
            "module rests on this index, so nothing below means anything until "
            "it holds."
        )
        assert fixture_index.labels[label] == [line], (
            f"{label!r} was indexed at {fixture_index.labels[label]}, and it "
            f"is on line {line}. Either FIXTURE was edited without updating "
            "TRUE_LINES, or the indexer is off."
        )

    for row_id, locator in (
        ("X 1", "1"),                              # the plainest citation
        ("X 2", "2-3"),                            # a LITERAL compound label
        ("X 3", "1-3"),                            # a RANGE over labels
        ("X L1", "L1"),                            # kind decided from data
        ("X 1", "1, Grouped roll-up"),             # a row plus its roll-up
        ("X 2", "2 (with an annotation the resolver ignores)"),
    ):
        verdict, named, detail = guard.resolve(row_id, locator, fixture_index)
        assert verdict == "RESOLVES", (
            f"the resolver said {verdict} for row {row_id} cited as {locator!r} "
            f"({detail}). It named {named}. This is a citation that is CORRECT; "
            "an instrument that cannot return RESOLVES on a correct citation "
            "cannot be believed when it returns anything else."
        )


def test_every_verdict_is_reachable(fixture_index):
    """Each failing verdict earned on the same fixture. A verdict that cannot
    be emitted is a class of defect that cannot be reported."""
    cases = {
        # a citation that resolves to a REAL BUT DIFFERENT row: the defect
        # class this whole guard exists for.
        ("X 1", "2"): "NAMES-ANOTHER-ROW",
        # a label that is nowhere in the slice
        ("X 1", "77"): "NO-SUCH-ROW",
        # a line number, refused by shape once the label lookup misses
        ("X 1", "L5"): "LINE-NUMBER",
        ("X 1", "L5-L9"): "LINE-NUMBER",
        # a good label AND a stale line number: the refusal must outrank
        ("X 1", "1, L5"): "LINE-NUMBER",
        ("X 1", ""): "UNREADABLE",
    }
    for (row_id, locator), want in cases.items():
        got, _named, _detail = guard.resolve(row_id, locator, fixture_index)
        assert got == want, (
            f"row {row_id} cited as {locator!r} was judged {got}, expected "
            f"{want}. A verdict this resolver cannot reach is a defect it "
            "cannot report, and the pin above would then be green for the "
            "wrong reason."
        )


def test_the_line_number_refusal_is_decided_by_data_not_by_shape(fixture_index):
    """`L1` is a ROW in the fixture and a LINE NUMBER anywhere without one.

    profile.md really does number its section L rows `L1` .. `L8`. A guard that
    reads the `L<digits>` shape and stops would refuse the four correct
    citations in that slice that use those labels and report them as rot, which
    is the false-positive failure that gets a guard suppressed.
    """
    resolves, _n, _d = guard.resolve("X L1", "L1", fixture_index)
    assert resolves == "RESOLVES"

    bare = guard.build_index(
        "| # | capability | state |\n|---|---|---|\n| 1 | a thing | GAP |\n", "Y")
    refused, _n, _d = guard.resolve("Y 1", "L1", bare)
    assert refused == "LINE-NUMBER", (
        "`L1` was not refused in a slice that has no L-prefixed rows. The kind "
        "of a token is a fact about the slice it points into, not about its "
        "spelling, and this is the half that catches real rot."
    )


def test_the_index_cannot_absorb_a_label_from_its_own_instruments():
    """The index may not be fed by commentary about the census.

    The sibling guard shipped with a registry that read `scripts/` and
    `tests/`, absorbed the example names out of its own docstring, and reported
    the corpus clean inside an hour. Writing ABOUT a row is not the row
    existing. `row_labels` reads the four slice files and nothing else, and
    this asserts it rather than trusting the reading.
    """
    index = guard.row_labels(REPO)
    assert set(index) == set(census.SLICES), (
        f"the index covers {sorted(index)}, and the census has "
        f"{sorted(census.SLICES)}. A slice that stopped being indexed makes "
        "every locator into it unresolvable, or -- worse -- unchecked."
    )
    # This label is written HERE, in a test, in the same table shape the census
    # uses. If it ever appears in the index, the index has started reading its
    # own instruments:
    #   | ZZZ-NOT-A-CENSUS-ROW | planted in a test | R | GAP | none |
    for letter, idx in index.items():
        assert "ZZZ-NOT-A-CENSUS-ROW" not in idx.labels, (
            f"slice {letter} has absorbed a row label planted in this test "
            "file. The four census slices ARE the census; a test, a script and "
            "an `_audit/` sentence are all just prose that mentions a row."
        )


def test_a_row_label_is_a_unique_key():
    """The repair rests on this. Measured, not assumed.

    A line number was replaced by a row label because a label identifies ONE
    row. If two stated rows in a slice ever share a label, a locator citing it
    is ambiguous and the repair has quietly recreated the problem in a form
    that no longer announces itself.
    """
    index = guard.row_labels(REPO)
    total = 0
    for letter, idx in index.items():
        total += len(idx.stated)
        collisions = sorted(
            label for label in idx.stated
            if len(idx.labels[label]) > 1
            and idx.labels[label][0] != idx.stated[label]
        )
        assert collisions == [], (
            f"in slice {letter} these labels name a stated capability row that "
            f"is NOT the first row carrying that label: {collisions}. A "
            "locator citing one of them resolves to whichever the index "
            "happened to keep."
        )
    # 704 -> 747 on 2026-09-24: lane Y2's completeness admission added 43
    # GAP rows (J 16, P 10, M 11, N 6), each under a label no row held.
    assert total == 747, (
        f"the four slices hold {total} stated rows with distinct labels, and "
        "the census holds 747. If the census really moved, re-run "
        "`scripts/count_census_states.py` and re-derive; if it did not, this "
        "index has started merging or dropping labels and every RESOLVES it "
        "prints is resting on a set that moved."
    )


def test_a_planted_wrong_row_locator_is_convicted(tmp_path):
    """THE RED PROOF, on a COPY of the real file, through the real `run()`.

    A mechanism shown working only on a synthetic fixture has not been shown to
    reach the corpus that matters. Here a real assignment row has its locator
    repointed at a real but different row -- exactly the shape of the 55
    wrong-row citations measured on 2026-09-21 -- and the guard must name it.
    """
    work = tmp_path / "repo"
    (work / "_audit" / "_census").mkdir(parents=True)
    for name in census.SLICES.values():
        shutil.copy2(REPO / "_audit" / "_census" / name,
                     work / "_audit" / "_census" / name)
    live = (REPO / guard.ASSIGNMENTS).read_text(encoding="utf-8")

    clean = work / guard.ASSIGNMENTS
    clean.write_text(live, encoding="utf-8", newline="\n")
    _found, bad = guard.run(work)
    assert [(f.row_id, f.verdict) for f in bad] == [], (
        "the UNMUTATED control is already failing on the copy, so the mutation "
        f"below would prove nothing: {[str(f) for f in bad]}"
    )

    planted = []
    for line in live.splitlines():
        fields = line.split("\t")
        if len(fields) >= 5 and fields[1] == "J 57":
            fields[4] = "112"       # a real jobs.md row, and not this one
            line = "\t".join(fields)
        planted.append(line)
    clean.write_text("\n".join(planted) + "\n", encoding="utf-8", newline="\n")

    _found, bad = guard.run(work)
    assert [(f.row_id, f.verdict) for f in bad] == [("J 57", "NAMES-ANOTHER-ROW")], (
        "a locator repointed from row 57 to row 112 -- a REAL row, in the right "
        f"file, of the right shape -- was not convicted. Got {[str(f) for f in bad]}. "
        "This is the precise failure the guard exists for: it does not rot into "
        "a dangling reference, it rots into a plausible wrong answer."
    )


def test_the_guard_stays_cheap_enough_to_gate():
    """A slow guard gets excluded from the gate and then protects nothing."""
    start = time.monotonic()
    guard.run(REPO)
    elapsed = time.monotonic() - start
    assert elapsed < 10.0, (
        f"the guard took {elapsed:.1f}s. It reads four files once and indexes "
        "them; anything near this bound means a per-row re-read."
    )


# --------------------------------------------------------------------------
# THE PIN
# --------------------------------------------------------------------------
def test_no_census_locator_points_elsewhere(measured):
    _found, bad = measured
    seen = {(f.row_id, f.verdict) for f in bad}
    appeared = sorted(seen - PINNED)
    repaired = sorted(PINNED - seen)
    assert not appeared, (
        f"these locators no longer name the row they are evidence for: "
        f"{appeared}. A citation that resolves to the WRONG row is worse than "
        "one that dangles -- it stops the reader instead of sending them "
        "looking. Cite the row label, never a line number: "
        "`venv/Scripts/python.exe scripts/check_census_locators_resolve.py`."
    )
    assert not repaired, (
        f"these pinned failures are gone: {repaired}. If they were repaired, "
        "narrow PINNED in the same commit -- a record of a defect may not "
        "outlive the defect. If instead the detector stopped seeing them, "
        "check `test_the_resolver_can_say_RESOLVES` first."
    )
