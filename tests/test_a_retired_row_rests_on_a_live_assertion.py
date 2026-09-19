"""A census row retired on a shipped assertion goes RED when that assertion leaves.

THE LAW THIS DISCHARGES was written by the article-publish wave and is the
last section of ``_audit/2026-09-05-article-publish.md``:

    A RULING NOT ATTACHED TO THE ROW IT DECIDES GETS RE-DERIVED. Four of this
    wave's six blockers were answerable from documents already in the tree --
    the operator's typing ruling living in a TEST DOCSTRING, A9's
    closed-vocabulary decision, the ledger's own merge rule, and an existing
    EXCLUDED-RULED note. Nobody had joined any of them to the rows they
    settle.

It wrote that down and could do nothing else with it, because prose in an audit
document is read once and is asserted by nothing. This file is the mechanism:
for each row below, the census STATE and the SHIPPED ASSERTION it rests on are
checked together, so removing the assertion turns the row red instead of
leaving a retirement standing on a rule that no longer exists.

**THE DIRECTION MATTERS AND IT IS THE WHOLE DESIGN.** This does not assert that
a row is correctly retired -- no test can, that is a judgement. It asserts that
the retirement and its stated reason cannot be separated. A future editor who
deletes ``collaborator`` from ``FORBIDDEN_PARAMETER_NAMES`` has made a ruling
change, and this file is where they find out that three census rows were
resting on it.

## WHY THIS IS NOT THE CENSUS COUNTER WEARING A SECOND HAT

``scripts/count_census_states.py`` counts states. It cannot know WHY a row
carries one, so it reads a row retired on a live rule and a row retired on a
rule somebody deleted last week as the same green. The gap between those two is
the entire subject here.

## WHAT IS DELIBERATELY NOT ASSERTED

* **No row is required to be retired.** The table holds only rows whose
  retirement this repository has already written down. A GAP row is absent
  from it and that is not an omission.
* **The reverse implication is not asserted either.** A live assertion does
  not require any row to be retired -- other rows may rest on the same rule
  for other reasons, and enumerating them is not this file's job.

SHOWN FAILING before admission, three ways, each against a COPY so no contended
file was edited: a state flipped in the census copy (red, naming the row), a
row id deleted from the census copy (red, naming the row as missing rather
than passing over an absent row), and a name removed from the shipped
forbidden set (red, naming the assertion). Recorded in
``_audit/2026-09-19-content-tail.md``.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from tests.test_no_write_tool_names_a_third_party import FORBIDDEN_PARAMETER_NAMES

_CENSUS = (
    pathlib.Path(__file__).resolve().parent.parent
    / "_audit"
    / "_census"
    / "messaging-and-content.md"
)

#: A census table row: ``| C55 | capability | source | STATE | ...``.
_ROW = re.compile(r"^\|\s*(C\d+)\s*\|[^|]*\|[^|]*\|\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|")

#: row id -> (required state, the shipped name it rests on, why in one line).
#:
#: Every entry names a parameter in ``FORBIDDEN_PARAMETER_NAMES``, which is
#: the tested surface promise that this server will not take another member's
#: identity as an argument to a publishing tool. The rows below were retired
#: BECAUSE of that promise, so they may not outlive it.
RETIRED_ON_A_SHIPPED_ASSERTION: dict[str, tuple[str, str, str]] = {
    "C10": (
        "EXCLUDED-RULED",
        "mentions",
        "a mention in a post is bytes the server inserts into his text at a "
        "position it chooses, which the operator's typing ruling forbids",
    ),
    "C28": (
        "EXCLUDED-RULED",
        "mentions",
        "a mention in a comment is the same act on a shorter surface",
    ),
    "C55": (
        "EXCLUDED-RULED",
        "collaborators",
        "inviting a named collaborator carries a third party's identity into "
        "content this server publishes, and the invitee is notified",
    ),
}


def _states() -> dict[str, str]:
    """Every ``C`` row in the messaging slice and the state cell it carries."""
    out: dict[str, str] = {}
    for line in _CENSUS.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found is not None:
            out.setdefault(found.group(1), found.group(2))
    return out


def test_the_census_is_readable_at_all() -> None:
    """The control, and it is the one this repository has been bitten without.

    A guard that reads an empty corpus refuses nothing. If the slice is
    renamed, its table reformatted, or the ``C`` prefix changed, every
    assertion below would pass over zero rows and read as coverage.
    """
    states = _states()
    assert len(states) >= 80, f"only {len(states)} C rows parsed out of {_CENSUS.name}"
    assert "C1" in states, "the first content row is missing; the reader is not reading"


def test_the_forbidden_set_is_readable_at_all() -> None:
    """The second control. The imported set must be non-empty and real."""
    assert len(FORBIDDEN_PARAMETER_NAMES) >= 10, (
        "FORBIDDEN_PARAMETER_NAMES is smaller than the set that was shipped; "
        "if that is deliberate, the rows in this file need re-opening first"
    )


@pytest.mark.parametrize("row", sorted(RETIRED_ON_A_SHIPPED_ASSERTION))
def test_the_row_is_present_and_carries_its_retired_state(row: str) -> None:
    """A row that has vanished from the census fails HERE rather than silently.

    Separated from the assertion check below on purpose: "the row is gone" and
    "the row changed state" are different events with different remedies, and
    a single test would report them with one message.
    """
    required, _, why = RETIRED_ON_A_SHIPPED_ASSERTION[row]
    states = _states()
    assert row in states, (
        f"census row {row} is not in {_CENSUS.name} any more. It was retired "
        f"because {why}. A retired row may be re-opened or re-numbered, but "
        "not deleted without amending this table."
    )
    assert states[row] == required, (
        f"census row {row} reads {states[row]!r}, not {required!r}. It was "
        f"retired because {why}. If it has been legitimately re-opened, remove "
        "it from RETIRED_ON_A_SHIPPED_ASSERTION in this file with the reason -- "
        "a row moved back to GAP while this table still claims it retired is "
        "how a count starts disagreeing with itself."
    )


@pytest.mark.parametrize("row", sorted(RETIRED_ON_A_SHIPPED_ASSERTION))
def test_the_assertion_the_row_rests_on_is_still_shipped(row: str) -> None:
    """The coupling. Delete the rule and the rows resting on it turn red."""
    _, rests_on, why = RETIRED_ON_A_SHIPPED_ASSERTION[row]
    assert rests_on in FORBIDDEN_PARAMETER_NAMES, (
        f"census row {row} is retired because {why} -- and the assertion it "
        f"rests on is gone: {rests_on!r} is no longer in "
        "FORBIDDEN_PARAMETER_NAMES. That is a RULING CHANGE. Either restore "
        f"the name, or re-open {row} in the census and remove it here. A "
        "retirement standing on a deleted rule is a row nobody is counting and "
        "nobody ruled."
    )
