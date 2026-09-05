"""The two highest-traffic count claims in this repository were guarded by nothing.

``server.py``'s module docstring names the tool counts and IS pinned, by
``tests/test_prose_that_makes_a_claim.py::test_the_server_docstring_numbers_are_derived``.
**Finding that took three steps and the first two were wrong**, which is worth
recording here because it is the thing this file is about: ``server.py``'s own
docstring cited the guard under a name that exists nowhere, and placed it in a
file it is not in. The guard was passing the whole time and its POINTER was
dangling, so following the citation suggested the numbers were unchecked.

**Two other files carry the same counts and were checked by no test at all**, and on 2026-09-05 both were found
stale within the same hour -- neither by a test, because no test looked:

    README.md            the opening headline    stale by NINE TOOLS
    linkedin_server/     the package docstring   understated the WRITE surface
      __init__.py                                by nine tools and the mutating
                                                 calls by four

**THE SECOND ONE HAD ALREADY DIAGNOSED ITSELF, IN THE PARAGRAPH DIRECTLY
ABOVE THE STALE SENTENCE**: *"the package docstring is the first thing a
reader trusts and was the last thing updated."* That sentence was written
after the same file claimed the package was read-only for a day past being
true. Then it happened again, in the same direction -- **because the remedy
chosen was to write a better sentence rather than to build something that
would notice.** This file is the something.

## WHY IT PINS A SENTENCE RATHER THAN A NUMBER

A test that greps for a digit cannot tell a tool count from a line number, and
these two claims are written in WORDS. So the expected sentence is CONSTRUCTED
from the live registry and asserted verbatim: when a count moves, the failure
message contains the exact text the file must now carry, which is the
difference between a guard that reports a problem and one that also hands over
the fix.

**AND THE WORDS ARE WHY THIS GAP EXISTED.** A census run over this tree for
the digits ``41`` and ``29`` found the four sites that carry them and missed
``server.py:77``, which spells the same count in title case, and missed the
test whose NAME glues ``forty`` to ``one`` because a Python identifier cannot
hold a hyphen. **Number words are the blind spot, so this file matches on
words only.**

## WHAT IT DELIBERATELY DOES NOT DO

It does not widen ``test_the_server_docstring_numbers_are_derived`` to cover
three files. That guard belongs to ``server.py``'s docstring and its failure
message is written for that reader. Overlapping guards that disagree are worse
than a gap -- the sibling inventory file says exactly that about ``dom.py`` --
so this one owns two files the other has never looked at, and says so.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import readonly
from linkedin_server.server import mcp
from tests.test_server_surface import SANCTIONED_WRITE_TOOLS

REPO = Path(__file__).resolve().parents[1]

#: Number words as this repository spells them. Written out rather than
#: generated, because the interesting failure is a count moving past the
#: largest word anybody thought to include -- and a missing key raises here,
#: loudly, instead of silently matching nothing.
WORDS = {
    0: "Zero", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten",
    11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen",
    15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen",
    19: "Nineteen", 20: "Twenty",
}
for _tens, _word in ((20, "Twenty"), (30, "Thirty"), (40, "Forty"),
                     (50, "Fifty"), (60, "Sixty"), (70, "Seventy"),
                     (80, "Eighty"), (90, "Ninety")):
    WORDS[_tens] = _word
    for _unit in range(1, 10):
        WORDS[_tens + _unit] = f"{_word}-{WORDS[_unit].lower()}"


def word(value: int) -> str:
    """The word for a count, or a loud failure if nobody spelled it."""
    if value not in WORDS:
        raise AssertionError(
            f"no spelling for {value}; extend WORDS rather than deleting a "
            "claim that has outgrown this table"
        )
    return WORDS[value]


async def _counts() -> tuple[int, int, int]:
    names = {tool.name for tool in await mcp.list_tools()}
    writes = names & SANCTIONED_WRITE_TOOLS
    return len(names), len(names - writes), len(writes)


def _mutations() -> int:
    return len(readonly.SANCTIONED_MUTATIONS)


def _readme() -> str:
    """Whitespace-normalised for the same reason as the package docstring."""
    return " ".join((REPO / "README.md").read_text(encoding="utf-8").split())


def _package_docstring() -> str:
    """WHITESPACE-NORMALISED, because a prose pin must survive a reflow.

    The first version matched the raw text and went red on a sentence that
    was CORRECT -- the words wrapped between "five" and "sanctioned", so the
    substring existed in the file and not on any one line. A guard that fires
    when somebody re-wraps a paragraph teaches its reader to edit the guard.
    """
    raw = (REPO / "linkedin_server" / "__init__.py").read_text(
        encoding="utf-8"
    )
    return " ".join(raw.split())


# ---------------------------------------------------------------------------
# The spelling table, shown behaving, before anything is asserted through it
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "value, spelled",
    [(0, "Zero"), (5, "Five"), (12, "Twelve"), (20, "Twenty"),
     (29, "Twenty-nine"), (30, "Thirty"), (41, "Forty-one"),
     (42, "Forty-two"), (99, "Ninety-nine")],
)
def test_the_spelling_table_spells(value, spelled):
    assert word(value) == spelled


def test_a_count_nobody_spelled_fails_loudly_rather_than_matching_nothing():
    """THE FAILURE MODE THIS TABLE COULD HAVE HAD.

    A ``.get(value, "")`` would make every assertion below pass vacuously the
    day the surface grows past the table -- a guard that stops guarding by
    growing out of its own vocabulary, silently.
    """
    with pytest.raises(AssertionError, match="no spelling for 100"):
        word(100)


# ---------------------------------------------------------------------------
# README.md's opening headline
# ---------------------------------------------------------------------------

async def test_the_readme_headline_agrees_with_the_registry():
    """THE FIRST SENTENCE ANY READER OF THIS REPOSITORY SEES.

    Found stale by nine tools on 2026-09-05 -- *"Thirty-three tools ship.
    Twenty-one read. Five write"* against a measured 42 / 30 / 12 -- by a grep
    run while waiting for a test suite, because no test looked here.
    """
    total, reads, writes = await _counts()
    expected = (
        f"**{word(total)} tools ship. {word(reads)} read. "
        f"{word(writes)} write."
    )
    assert expected in _readme(), (
        "README.md's opening headline no longer agrees with the registry.\n"
        f"  it must contain: {expected}\n"
        "  Correct the headline; do not relax this test. Keep the stale text "
        "beside it, the way that file already does for two earlier drifts."
    )


async def test_the_readme_module_listing_names_the_right_number():
    """The same count, lower down, in the tree diagram. It drifted too."""
    total, _reads, _writes = await _counts()
    assert f"the {word(total).lower()} tools" in _readme()


def test_the_headline_check_would_catch_a_wrong_number():
    """A CHECK THAT CANNOT FAIL CERTIFIES NOTHING.

    The plant is the real stale text this guard was built for, so the
    demonstration and the incident are the same string.
    """
    stale = "**Thirty-three tools ship. Twenty-one read. Five write."
    assert stale not in _readme(), (
        "the exact stale headline is back in README.md"
    )


# ---------------------------------------------------------------------------
# linkedin_server/__init__.py -- the package's front door
# ---------------------------------------------------------------------------

async def test_the_package_docstring_agrees_about_writes_and_mutations():
    """UNDERSTATING THE WRITE SURFACE IS THE DANGEROUS DIRECTION.

    This file said three write tools and one mutating call. Measured: twelve
    and five. A reader who trusts the front door and stops there believes this
    package can save, unsave and unfollow, and does not learn that it can
    apply to a job, publish a post, send an invitation, send a message or
    comment on an item -- five irreversible acts.
    """
    _total, _reads, writes = await _counts()
    expected = (
        f"{word(writes).lower()} write tools ship, {word(_mutations()).lower()} "
        "sanctioned mutating calls exist"
    )
    assert expected in _package_docstring(), (
        "linkedin_server/__init__.py no longer agrees with the package.\n"
        f"  it must contain: {expected}\n"
        "  This is the first docstring anyone importing the package reads, "
        "and it has now gone stale twice in the SAME direction."
    )


def test_the_package_docstring_check_would_catch_the_old_claim():
    """The plant is the incident, again."""
    stale = "Three write tools ship: save, unsave and unfollow."
    assert stale not in _package_docstring()


def test_the_front_door_points_at_the_guarded_docstring_for_counts():
    """THE PART A NUMBER CANNOT CARRY.

    Three files hold these counts and only ``server.py``'s is read by the
    older guard. Until that changes, the front door should say which one is
    checked -- so a reader who needs a number knows where the checked copy
    lives rather than trusting whichever they opened first.
    """
    text = _package_docstring()
    assert "server.py" in text and "checked" in text


# ---------------------------------------------------------------------------
# The premise, asserted, so this file dies when it should
# ---------------------------------------------------------------------------

def test_the_older_guard_still_owns_only_the_server_docstring():
    """IF THE SIBLING WIDENS, DELETE THIS FILE RATHER THAN ADJUST IT.

    Overlapping guards that disagree are worse than a gap. This one exists
    because ``test_this_modules_docstring_numbers_are_derived`` reads one
    file. The day it reads three, this file is redundant and should go.
    """
    sibling = (REPO / "tests" / "test_prose_that_makes_a_claim.py").read_text(
        encoding="utf-8"
    )
    assert "def test_the_server_docstring_numbers_are_derived" in sibling, (
        "the sibling guard is gone; re-read the premise of this file"
    )
    body = sibling.split("def test_the_server_docstring_numbers_are_derived")
    assert len(body) > 1
    scope = body[1][:4000]
    assert "README" not in scope and "__init__" not in scope, (
        "the sibling now reads README.md or __init__.py as well -- delete "
        "this file instead of maintaining two guards over one claim"
    )


def test_all_three_files_carry_the_same_count_right_now():
    """The whole point, in one assertion: they agree at this tree."""
    server_doc = (REPO / "linkedin_server" / "server.py").read_text(
        encoding="utf-8"
    )[:6000]
    headline = re.search(r"\*\*([A-Z][a-z]+(?:-[a-z]+)?) tools ship\.", _readme())
    assert headline, "README.md has no headline of the expected shape"
    assert headline.group(1).lower() in server_doc.lower(), (
        f"README says {headline.group(1)} tools and server.py's docstring "
        "does not use that word"
    )
