"""The census DENOMINATOR is pinned, so it cannot move without somebody saying so.

`stated rows 704` is the number every completion figure in this repository
divides by. It is printed by 15 documents under `_audit/` -- measured the day
this guard was written, and the guard COMPUTES that figure rather than carrying
it, because it became 16 the moment this wave's own audit document landed.
**Nothing asserted the number itself until this file.** The invariant held because each wave
was asked to check it by hand, which is the condition an invariant is in just
before it quietly stops being true -- and this repository has already paid for
that exact shape twice, with `XR` (23 rows invisible for a fortnight) and
`CANNOT-DELIVER` (2 rows missing from the freeze the number 409 rests on).

## WHAT THE NEIGHBOURS DO AND DO NOT COVER, MEASURED RATHER THAN ASSUMED

    tests/test_census_rows_carry_a_state.py   every row in a table whose HEADER
                                              declares `state` carries one
    tests/test_state_cell_dialects_refuse_loudly.py
                                              a cell spelled in a DIALECT
                                              refuses instead of returning ''
    THIS FILE                                 the POPULATION those two count
                                              over is the one we pinned

The first two are cell-shaped: they inspect a row and judge it. **Neither
counts.** That is the whole hole, and it is not a coverage gap -- measured at
HEAD, `test_census_rows_carry_a_state.py` inspects 706 rows against the
counter's 704 (the two extra are its `DECLARED_STATELESS` pair, `J 58` and
`M C53`), so **every counted row is already inspected**. The neighbours look at
every row and still cannot see the population change, because looking at a row
one at a time is a different question from asking how many there are.

So a row ADDED with a perfectly well-formed state cell passes both of them and
moves the denominator from 704 to 705 in silence. That case is demonstrated,
with both neighbours run and shown staying green, in
`scripts/_check_the_census_row_pin_can_fail.py`.

## WHAT IT PINS, AND THE LINE IT DELIBERATELY DOES NOT CROSS

**THE POPULATION, NEVER THE ADJUDICATION.** A row moving GAP ->
COVERED-PROVEN does not fire this guard and must not: several waves move census
rows every day, and a guard that fired on each of them would be switched off
inside a week. A guard everybody has learned to ignore is worse than none.

What fires is a row ENTERING or LEAVING the set the shipped counter can see --
the event that silently rewrites every percentage in the corpus at once.

## THE THIRD LEG: THE VOCABULARY ITSELF

`count_census_states.STATES` is the vocabulary. Widen it and rows that were
invisible become visible, so the denominator moves WITHOUT ANY CENSUS FILE
CHANGING. That has happened twice and both times it was right to do -- and both
times the counter's own docstring demanded a receipt that nothing enforced.
Pinning the vocabulary makes the receipt a review moment. The counter says it
in its own words: *"Do not widen the counter to guess."*

## HOW TO CLEAR IT WHEN IT FIRES

1. `python scripts/pin_census_rows.py` -- it names every row that moved, and
   says whether a missing row was DELETED or has become UNREADABLE.
2. `python scripts/pin_census_rows.py --write`
3. **In the SAME commit, say what moved the census population and why.**

Step 3 is unverifiable from here and that is the design, borrowed intact from
`test_the_tool_surface_is_pinned_so_a_row_must_move.py`: the guard buys the
moment, a human supplies the judgement.

## SHOWN FAILING BEFORE IT WAS TRUSTED

Three ways, against real census rows in a scratch copy of the tree, never in
the live one -- `scripts/_check_the_census_row_pin_can_fail.py` replants all
three and the output is pasted into
`_audit/2026-09-21-what-100-percent-means.md`. A check that has not been shown
failing certifies nothing, and ten that could not fire were found in this
repository in two days.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import count_census_states as C  # noqa: E402
import pin_census_rows as P  # noqa: E402

#: The denominator, as a literal, so a reader of this file learns the number
#: without opening the JSON and so an emptied pin cannot pass quietly.
#: 704 -> 747 on 2026-09-24: lane Y2's completeness admission added 43 GAP rows
#: (J 152-167, P S1-S10, M M52-M53 and C93-C101, N 195-200), each a capability
#: LinkedIn drew on a captured page that no row carried -- see
#: `_audit/2026-09-24-lane-y2-admission.md`. No row left.
PINNED_ROW_TOTAL = 747

#: Per slice, because a delta of zero across four slices is reachable by two
#: errors cancelling -- one row added to `jobs.md` and one dropped from
#: `network.md` sum to the same total and are not the same census.
PINNED_SLICE_ROWS = {
    "J": 166,   # jobs.md                    (150 + 16)
    "P": 213,   # profile.md                 (203 + 10)
    "M": 153,   # messaging-and-content.md   (142 + 11)
    "N": 215,   # network.md                 (209 + 6)
}

#: Every spelling `count_census_states` will honour. Two of these were taught
#: to the counter AFTER rows had gone missing under them, and each entry there
#: carries its receipt in a comment. This pin is what makes the next such
#: widening a review moment rather than a diff nobody reads.
#:
#: `XR`             jobs.md's short EXCLUDED-RULED -- 23 rows, invisible for a
#:                  fortnight.
#: `CANNOT-DELIVER` messaging's first spelling of COVERED-CANNOT-DELIVER -- cost
#:                  `M M1` and `M M2` their membership across 11 commits,
#:                  including the freeze the number 409 is taken from.
PINNED_STATE_VOCABULARY = frozenset({
    "GAP", "CP", "CU", "CCD", "ER", "XR",
    "EXCLUDED-RULED", "COVERED-PROVEN", "COVERED-UNFIRED",
    "COVERED-CANNOT-DELIVER", "MEASURED-ABSENT",
    "CANNOT-DELIVER",
})


#: Documents are searched for the pinned total as a STANDALONE TOKEN, so
#: `14,704` in a fixture blurb does not count and `704` in a sentence does.
_TOKEN = None


def _documents_quoting_the_total() -> int:
    """How many tracked `_audit` documents print the pinned total.

    COMPUTED, NEVER HARDCODED, AND IT CAUGHT ITS OWN AUTHOR. The first draft of
    this file wrote `21 tracked documents` into the failure text. That number
    came from `git grep -l "704"` -- a SUBSTRING match, which also counts six
    documents where those digits sit inside a longer number. **The error was
    found by building this function and watching it disagree**, and the same
    wrong 21 had already gone into an audit document and a commit message. **A
    guard against stale numbers must not carry one**, and a count in a message
    nobody re-derives is the same defect one level down.

    It is INDICATIVE, not a citation index: a token match cannot tell a
    denominator from a coincidence, and it does not try. It exists to say how
    far the blast radius reaches, which is the thing a reader needs in order to
    care.
    """
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = __import__("re").compile(rf"(?<!\d){PINNED_ROW_TOTAL}(?!\d)")
    audit = _ROOT / "_audit"
    return sum(
        1 for path in audit.rglob("*.md")
        if _TOKEN.search(path.read_text(encoding="utf-8", errors="replace"))
    )


def _live() -> "object":
    """The live population, or a skip-free failure if a dialect is open.

    A dialect is a DIFFERENT finding with a DIFFERENT owner
    (`test_state_cell_dialects_refuse_loudly.py`), and reporting it as a
    population drift would send the reader to the wrong file. So it fails here
    in its own words rather than being folded into an added/removed list.
    """
    try:
        return P.population()
    except P.DialectOpen as exc:
        pytest.fail(
            "The census population cannot be measured while a state cell is "
            "spelled in a dialect: such a row is in NEITHER the numerator NOR "
            "the denominator, so any total taken now is short by it.\n"
            f"{exc}"
        )


def test_the_pin_itself_is_not_empty_and_agrees_with_the_literals():
    """A guard whose pin can be emptied is a guard that can be switched off.

    This is the assertion that stops `--write` on a broken tree from becoming
    a way to make the suite green: the JSON must agree with the numbers
    written out longhand above, and those a human has to edit by hand.
    """
    pinned = P.load()
    assert pinned, (
        f"{P.PIN} is missing or empty. The census denominator is unpinned and "
        f"nothing in this suite is holding it. Run "
        f"`python scripts/pin_census_rows.py --write`."
    )
    assert sum(pinned.values()) == PINNED_ROW_TOTAL, (
        f"{P.PIN.name} holds {sum(pinned.values())} rows but this file's "
        f"literal PINNED_ROW_TOTAL says {PINNED_ROW_TOTAL}. The JSON and the "
        f"literal are two halves of one pin and they must move together -- the "
        f"literal exists so a re-pin cannot happen without a human editing a "
        f"number and, in the same commit, saying what moved."
    )
    assert P.per_slice(pinned) == PINNED_SLICE_ROWS, (
        f"{P.PIN.name} is per-slice {P.per_slice(pinned)} against this file's "
        f"literal {PINNED_SLICE_ROWS}."
    )


def test_no_census_row_appeared_or_vanished_without_a_decision():
    """The population is the pin -- and the failure NAMES what moved.

    A scalar pin can only ever say `704 -> 705`, after which somebody spends an
    afternoon diffing 592 KB of markdown across four files to find out which
    row. This names it, and says whether a missing row was DELETED from its
    slice or is still sitting there with a state cell nothing can read.
    """
    live = _live()
    pinned = P.load()
    added, removed = P.delta(pinned, live)
    assert not (added or removed), (
        f"THE CENSUS POPULATION MOVED: {len(added)} added, {len(removed)} "
        f"removed (total {sum(pinned.values())} -> {sum(live.values())}).\n"
        f"This is the DENOMINATOR under every completion figure in this "
        f"repository -- {_documents_quoting_the_total()} documents under "
        f"`_audit/` print {PINNED_ROW_TOTAL}. Each of them now divides by a "
        f"number that is no longer true.\n"
        f"{P.describe(added, removed)}\n"
        f"TO CLEAR: `python scripts/pin_census_rows.py --write`, update "
        f"PINNED_ROW_TOTAL and PINNED_SLICE_ROWS in this file, and IN THE SAME "
        f"COMMIT say what moved the census population and why. This guard "
        f"cannot check whether the move was correct; it buys the moment."
    )


@pytest.mark.parametrize("letter", sorted(PINNED_SLICE_ROWS))
def test_each_slice_holds_the_rows_it_is_pinned_at(letter):
    """Per slice, because two opposite errors sum to the right grand total."""
    live = P.per_slice(_live())
    assert live[letter] == PINNED_SLICE_ROWS[letter], (
        f"{C.SLICES[letter]} holds {live[letter]} stated rows, pinned at "
        f"{PINNED_SLICE_ROWS[letter]} "
        f"(delta {live[letter] - PINNED_SLICE_ROWS[letter]:+d}). "
        f"Run `python scripts/pin_census_rows.py` to see which rows."
    )


def test_the_state_vocabulary_has_not_widened_or_narrowed():
    """Widening the vocabulary moves the denominator with no census edit at all.

    This is the leg the other two guards cannot have, because it is not about
    a row: teaching `STATES` a new spelling makes previously-invisible rows
    countable, and the total changes while every census file stays byte for
    byte the same. Both past widenings were CORRECT, and both should have been
    a review moment. Now they are.
    """
    added = sorted(C.STATES - PINNED_STATE_VOCABULARY)
    gone = sorted(PINNED_STATE_VOCABULARY - C.STATES)
    assert C.STATES == set(PINNED_STATE_VOCABULARY), (
        f"THE CENSUS STATE VOCABULARY MOVED. added={added} removed={gone}.\n"
        f"A spelling added here makes rows countable that were not, so the "
        f"denominator moves WITHOUT ANY CENSUS FILE CHANGING -- `XR` moved it "
        f"by 23 and `CANNOT-DELIVER` by 2.\n"
        f"If the new spelling is real, add it to STATES under its own key WITH "
        f"ITS RECEIPT, re-pin the population, and update "
        f"PINNED_STATE_VOCABULARY here. The counter's own words: do not widen "
        f"the counter to guess."
    )
