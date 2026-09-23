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

## LANE R, 2026-09-23: THE SIX ROWS ARE GAP NOW, AND THE BINDING PINS THEIR BLOCKER

All six were returned to GAP on the orchestrator's delegated call
(``_audit/2026-09-23-exclusion-returns.md`` section 3.6): the operator's typing
ruling reaches them only through an agent's reading, and
``MENTION-COMPOSITION-RULING`` permits the mechanism, so whether a mention the
caller NAMES is text the caller supplied is his question and not a settled
exclusion. **The assertion still ships and is now each row's NAMED BLOCKER.** So
the table below requires ``GAP`` rather than ``EXCLUDED-RULED``, and a row must
name the shipped test in its own cell. The coupling survives in the direction
that still matters: delete a name from ``FORBIDDEN_PARAMETER_NAMES`` and the
rows whose blocker it was turn red here, instead of sitting in GAP behind a
blocker that no longer exists. Emptying the table was not an option: an empty
parameter set is a skip, and a skip nobody declared fails this repository's CI.

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
#:
#: WIDENED 2026-09-19 from ``C\d+`` to ``[CM]\d+``. The messaging slice holds
#: two id families and this read only one of them, so ``M23`` -- a mention row
#: in the same action class as ``C10`` and ``C28`` -- could not have been bound
#: here at all. A reader scoped to one prefix does not report the other as
#: missing; it passes over it, which is the failure mode this file's own
#: readability control exists to catch one level up.
_ROW = re.compile(r"^\|\s*([CM]\d+)\s*\|[^|]*\|[^|]*\|\s*\*{0,2}([A-Z-]+)\*{0,2}\s*\|")

#: row id -> (required state, the shipped name it rests on, why in one line).
#:
#: Every entry names a parameter in ``FORBIDDEN_PARAMETER_NAMES``, which is
#: the tested surface promise that this server will not take another member's
#: identity as an argument to a publishing tool. The rows below were retired
#: BECAUSE of that promise, so they may not outlive it.
RETIRED_ON_A_SHIPPED_ASSERTION: dict[str, tuple[str, str, str]] = {
    "C10": (
        "GAP",
        "mentions",
        "a mention in a post is bytes the server inserts into his text at a "
        "position it chooses, which the operator's typing ruling forbids",
    ),
    "C28": (
        "GAP",
        "mentions",
        "a mention in a comment is the same act on a shorter surface",
    ),
    "C55": (
        "GAP",
        "collaborators",
        "inviting a named collaborator carries a third party's identity into "
        "content this server publishes, and the invitee is notified",
    ),
    # -- added 2026-09-19: the half of the action-class ruling never applied --
    #
    # `_audit/2026-09-05-article-publish.md:82` reached the ruling and said
    # what was still owed: "The ruling reaches the ACTION CLASS -- compose a
    # mention or a tag into published content -- and whoever holds the map
    # should apply it ROW BY ROW rather than take my count." It enumerated
    # FOUR mention rows. Two were applied in `58ba421`; these were not.
    #
    # `C9` is deliberately absent. The same document is headed "why
    # celebration is conditional and not ruled outright" and says the template
    # naming a third party was expected, not verified. Two waves have declined
    # it for that reason and a third declining is the precondition still being
    # unmet, not indecision.
    #
    # `C87`, `C88`, `C89` are deliberately absent too, and the same source
    # rules them out BY ARTICLE ID: they are self-scoped privacy controls
    # governing who may tag HIM, and "nothing above touches them".
    "M23": (
        "GAP",
        "mentions",
        "a mention in a group chat is the same composition act as C10 and C28 "
        "on a conversational surface -- an entity the composer inserts, not "
        "text, so typing @Name produces no mention",
    ),
    "C66": (
        "GAP",
        "mentions",
        "mentioning group members in a conversation names third parties to "
        "every other member of it, and is the fourth of the four mention rows "
        "the ruling's own document enumerates",
    ),
    "C86": (
        "GAP",
        "tagged_people",
        "a coordinate-anchored tag names a third party on media published to "
        "others -- the TAG half of the action class, which is why five of the "
        "thirteen forbidden names are tag spellings",
    ),
}


def _line_of(row: str) -> str:
    """The raw census line of ``row``, or '' when the row is absent."""
    for line in _CENSUS.read_text(encoding="utf-8").splitlines():
        found = _ROW.match(line)
        if found is not None and found.group(1) == row:
            return line
    return ""


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
        f"census row {row} reads {states[row]!r}, not {required!r}. It rests on "
        f"this assertion because {why}. If its state has legitimately moved, "
        "change it in RETIRED_ON_A_SHIPPED_ASSERTION with the reason -- a row "
        "whose state and this table disagree is how a count starts disagreeing "
        "with itself."
    )
    if required == "GAP":
        # A GAP row must NAME the blocker this table binds it to, in its own
        # cell -- the census's convention for a returned row, checked here.
        line = _line_of(row)
        assert "test_no_write_tool_names_a_third_party" in line, (
            f"census row {row} is GAP on this assertion but its cell does not "
            "name tests/test_no_write_tool_names_a_third_party.py as its blocker"
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
