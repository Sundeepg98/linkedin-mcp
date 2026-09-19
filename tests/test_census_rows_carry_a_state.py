"""A capability row in a state-bearing census table must carry a parseable state.

WHY THIS EXISTS. On 2026-09-05 the four census slices held 117 table rows that
`scripts/count_census_states.py` could not see, and a row it cannot see leaves
the NUMERATOR and the DENOMINATOR at the same instant -- it is counted neither
as a gap nor as covered. Thirty-seven of those were capability rows that should
have been countable. The class was found by LOSING A RACE, not by review: only a
git diff against a dated commit exposed `N 132`, whose state cell had been
replaced with a live-read sentence. Two independent parsers agreed on the same
wrong total because both shared the assumption. Agreement between instruments
sharing a defect is not corroboration.

WHAT IT CHECKS, AND THE ONE THING THAT MAKES IT MEANINGFUL. It does NOT assert
"no unstated rows" -- 78 rows in these files are correctly stateless (summary
tables, table headers, a Help-Center URL reference table, a hole-verdict table,
the build-cost roll-up whose rows restate rows counted elsewhere). Asserting
over all of them would be a check nobody could keep green, and it would be
deleted within the week. So the scope is exactly the rows where a missing state
is a DEFECT: a row sitting in a table whose own HEADER declares a `state`
column. That table promised a state for every row in it; this test holds it to
the promise.

IT IMPORTS THE SHIPPED PARSER RATHER THAN REIMPLEMENTING IT. Four waves
reimplemented a shipped instrument in this repo in one day and three got a
broken one. If `count_census_states.state_of` and this guard ever disagreed
about where a state lives, the guard would certify a count the counter cannot
take.

SHOWN FAILING BEFORE IT WAS TRUSTED. Planted a prose state cell in a real
census row, ran this file, watched it red and name the row; restored the cell,
watched it green. A guard that has not been shown failing certifies nothing --
ten checks that could not fire were found in this repository in two days.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import count_census_states as C  # noqa: E402

#: Rows the census DECLARES stateless in its own prose. The bar for entry is
#: that the slice says so itself, in words, with a reason -- not that somebody
#: found the row inconvenient. `jobs.md` on row 58: "a thing LinkedIn itself
#: does not offer, so it takes no state. The denominator is 150 distinct job
#: capabilities". Removing a row from here must turn this test RED, which is
#: the only way an exemption stays honest.
DECLARED_STATELESS = {
    ("J", "58"),
    # messaging C53: "*(retired -- see C52)*", every cell `--`, and the note
    # says "Retired rather than kept, and recorded rather than deleted". A row
    # kept as a deliberate tombstone so the id is not silently reused.
    ("M", "C53"),
}


def _is_capability_table(header: list[str]) -> bool:
    """True for a table that PROMISES a state per row.

    The `state` column must exist and must not be the FIRST column. That one
    extra condition is load-bearing: every slice opens with a SUMMARY table
    headed `| state | count | share | ... |`, where `state` names the ROW
    rather than a cell in it -- `| GAP | 99 | 66.0% | 81 |`. Scoping on the
    header word alone flagged all four summary tables as defective capability
    tables, which is a guard failing on the one thing it was built to ignore.
    """
    return "state" in header and header[0] != "state"


def _tables(path: pathlib.Path):
    """Yield (header_cells, [(lineno, cells, raw)]) for each markdown table."""
    header: list[str] | None = None
    body: list[tuple[int, list[str], str]] = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), 1
    ):
        if not line.startswith("|"):
            if header is not None:
                yield header, body
            header, body = None, []
            continue
        c = C.cells(line)
        if c and c[0] and set(c[0]) <= set("-: "):
            continue  # the |---|---| separator
        if header is None:
            header = [x.strip().lower().replace("*", "").replace("`", "") for x in c]
            continue
        body.append((lineno, c, line))
    if header is not None:
        yield header, body


def _offenders(letter: str, path: pathlib.Path) -> list[str]:
    out: list[str] = []
    for header, body in _tables(path):
        if not _is_capability_table(header):
            continue
        for lineno, c, raw in body:
            if len(c) < 3 or not C.ROW.match(raw):
                continue
            if c[0].lower() in C.HEADERS:
                continue
            if (letter, c[0]) in DECLARED_STATELESS:
                continue
            if C.state_of(c):
                continue
            out.append(f"{letter} {c[0]} (line {lineno}): {c[1][:70]}")
    return out


@pytest.mark.parametrize("letter,name", sorted(C.SLICES.items()))
def test_every_row_in_a_state_bearing_table_carries_a_state(letter, name):
    offenders = _offenders(letter, C.CENSUS / name)
    assert not offenders, (
        f"{len(offenders)} row(s) in {name} sit in a table whose header declares a "
        f"`state` column and carry no state this repository's own counter can read.\n"
        f"Such a row is in NEITHER the numerator NOR the denominator: it leaves the "
        f"census silently and no diff looks like a state change.\n"
        f"THE FIX IS THE CELL, NOT THIS TEST: the state cell holds a state and the "
        f"finding goes in the note beside it. If the state is spelled in a dialect "
        f"(`XR` was one, used 23 times and unknown to the counter for a fortnight), "
        f"teach `scripts/count_census_states.py` the spelling instead of rewriting "
        f"the rows. Only add to DECLARED_STATELESS when the slice itself says in "
        f"prose that the row takes no state, and quote that prose.\n  "
        + "\n  ".join(offenders)
    )


def test_the_declared_stateless_rows_really_are_stateless():
    """The exemption list must not accumulate rows that have since been fixed.

    An allowlist nobody prunes stops being an allowlist and becomes a blind
    spot. If a declared-stateless row acquires a state, this fails and the
    entry comes out -- so the list can only ever shrink by measurement.
    """
    still_bare = set()
    for letter, name in C.SLICES.items():
        for header, body in _tables(C.CENSUS / name):
            if "state" not in header:
                continue
            for _lineno, c, raw in body:
                if (letter, c[0]) in DECLARED_STATELESS and not C.state_of(c):
                    still_bare.add((letter, c[0]))
    assert still_bare == DECLARED_STATELESS, (
        f"DECLARED_STATELESS is {sorted(DECLARED_STATELESS)} but only "
        f"{sorted(still_bare)} are still stateless in a state-bearing table. "
        f"Remove the entries that now carry a state."
    )
