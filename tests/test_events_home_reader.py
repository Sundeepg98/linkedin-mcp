"""The events root reads ZERO, and a zero is the one answer that must argue.

``events.read_events_home`` exists to answer "how many events is he registered
for". The answer, measured live on 2026-09-05 with a control passing at both
ends of the session and two agreeing readings, is **zero** -- and zero is the
exact string a broken reader returns, an unhydrated page returns, and a
renamed section returns. This repository has shipped that conflation before,
which is why every test below is about telling those apart rather than about
the happy path.

## THE STUB IS A SELECTOR ENGINE, DELIBERATELY, AND IT IS SHOWN DISCRIMINATING

A stub that answered ``count()`` with a number chosen by the test would prove
nothing about the SELECTORS, and the selectors are where the only defect found
in this reader lived: the first version matched
``section[class*="discovery-card"]`` and read **54 rows where there are 18**,
because each row contains a ``__details`` and a ``__controls`` descendant whose
class tokens start with the row's own. So the stub carries the class strings
MEASURED on the live page and implements the three attribute operators the
reader actually uses, and one test drives the broken selector through it to
show 54 coming back.

**The class strings are structure, not identity.** No event title, no
organiser, no identifier and no heading text off the real page appears in this
file; the headings used are this file's own inventions chosen to exercise the
redaction rules.
"""
from __future__ import annotations

import re

import pytest

from linkedin_server import events


# ---------------------------------------------------------------------------
# A stub with enough of a selector engine to be wrong in the same ways
# ---------------------------------------------------------------------------

#: The class attribute of a top-level card, measured live 2026-09-05. Two of
#: the three carry this exact string; the promoted one differs and is below.
CARD_CLASS = (
    "artdeco-card events-card-container__container display-flex "
    "flex-column full-width events-events-home__card-container"
)

#: The promoted card's class attribute. It shares exactly ONE token with the
#: other two, which is why the reader matches on that token.
PROMOTED_CARD_CLASS = (
    "artdeco-card premium-events-card-container__container--premium "
    "premium-accent-bar display-flex flex-column full-width "
    "events-events-home__card-container"
)

#: A row, and its two descendants. The descendants are the whole reason the
#: substring form over-counts: their tokens begin with the row's token.
ROW_CLASS = "artdeco-card events-components-shared-discovery-card"
ROW_DETAILS_CLASS = "events-components-shared-discovery-card__details"
ROW_CONTROLS_CLASS = "events-components-shared-discovery-card__controls"

#: Anchors per row, measured: 54 anchors over 18 rows.
ANCHORS_PER_ROW = 3


class _Node:
    def __init__(self, tag, classes="", href=None, text="", children=()):
        self.tag = tag
        self.classes = classes
        self.href = href
        self.text = text
        self.children = list(children)

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()


_ATTR = re.compile(
    r'^(?P<tag>[a-z0-9]+)?'
    r'(?:\[(?P<attr>[a-z-]+)(?P<op>[~*]?=)"(?P<value>[^"]+)"\])?$'
)


def _matches(node, selector):
    """The three operators this reader uses, and no others.

    ``~=`` is a whitespace-separated TOKEN match; ``*=`` is a SUBSTRING match.
    Implemented separately rather than reduced to one, because the difference
    between them is the defect this file exists to pin.
    """
    parsed = _ATTR.match(selector.strip())
    if parsed is None:  # pragma: no cover - a typo in a test's selector
        raise AssertionError(f"stub cannot parse selector {selector!r}")
    tag = parsed.group("tag")
    if tag and node.tag != tag:
        return False
    attr = parsed.group("attr")
    if attr is None:
        return True
    value = parsed.group("value")
    op = parsed.group("op")
    haystack = node.classes if attr == "class" else (node.href or "")
    if op == "~=":
        return value in haystack.split()
    if op == "*=":
        return value in haystack
    return haystack == value


class _Loc:
    def __init__(self, nodes):
        self.nodes = list(nodes)

    async def count(self):
        return len(self.nodes)

    def nth(self, index):
        return _Loc([self.nodes[index]])

    @property
    def first(self):
        return _Loc(self.nodes[:1])

    def locator(self, selector):
        found = []
        for node in self.nodes:
            found.extend(
                child for child in node.walk() if _matches(child, selector)
            )
        return _Loc(found)

    async def inner_text(self, timeout=None):
        del timeout
        return self.nodes[0].text if self.nodes else ""


class _FakePage:
    def __init__(self, root):
        self.root = root

    def locator(self, selector):
        return _Loc(
            node for node in self.root.walk() if _matches(node, selector)
        )


def _row():
    anchors = [
        _Node("a", href="/events/an-event-identifier/")
        for _ in range(ANCHORS_PER_ROW)
    ]
    return _Node(
        "section",
        ROW_CLASS,
        children=[
            _Node("section", ROW_DETAILS_CLASS),
            _Node("section", ROW_CONTROLS_CLASS, children=anchors),
        ],
    )


def _card(heading, rows, classes=CARD_CLASS):
    children = [_Node("header", children=[_Node("h2", text=heading)])]
    children.extend(_row() for _ in range(rows))
    return _Node("section", classes, children=children)


def _page(
    own_heading="Your events",
    own_rows=0,
    promoted_rows=3,
    recommended_rows=15,
):
    """The events root as MEASURED, with each count a parameter.

    Defaults reproduce the live reading exactly: 3 cards, 0/3/15 rows,
    0/9/45 anchors.
    """
    cards = [
        _card(own_heading, own_rows),
        _card("Exclusive for a tier name", promoted_rows, PROMOTED_CARD_CLASS),
        _card("Recommended for you", recommended_rows),
    ]
    return _FakePage(_Node("body", children=cards))


# ---------------------------------------------------------------------------
# The stub, shown discriminating before anything is asserted through it
# ---------------------------------------------------------------------------

def test_the_stub_tells_a_token_match_from_a_substring_match():
    """THE STUB'S OWN CONTROL. Without this every test below is decorative.

    If ``~=`` and ``*=`` behaved the same in this engine, the regression test
    for the real defect would pass whatever the reader did.
    """
    page = _page()
    token = page.locator(
        'section[class~="events-components-shared-discovery-card"]'
    )
    substring = page.locator('section[class*="discovery-card"]')
    import asyncio

    assert asyncio.run(token.count()) == 18
    assert asyncio.run(substring.count()) == 54


# ---------------------------------------------------------------------------
# The reading, reproduced
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_the_reader_reproduces_the_live_reading():
    """3 cards, 0/3/15 rows, 0/9/45 links, zero registered, corroborated."""
    reading = await events.read_events_home(_page())
    assert reading["cards_read"] == 3
    assert [card["rows"] for card in reading["cards"]] == [0, 3, 15]
    assert [card["event_links"] for card in reading["cards"]] == [0, 9, 45]
    assert reading["rows_total"] == 18
    assert reading["verdict"] == "empty_beside_full_siblings"
    assert reading["registered_events"] == 0
    assert reading["error"] is None


@pytest.mark.asyncio
async def test_the_self_scoped_card_is_identified_by_a_key_not_by_its_text():
    reading = await events.read_events_home(_page())
    known = [card["known"] for card in reading["cards"]]
    assert known == ["your_events", None, None]
    assert set(known) <= {"your_events", None}, (
        "``known`` must only ever carry a value from this module's own closed "
        "set -- the moment it carries LinkedIn's string it is a name channel"
    )


# ---------------------------------------------------------------------------
# THE DEFECT THAT WAS REAL, PINNED AS A MUTATION
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_a_substring_row_selector_reads_fifty_four_rows_where_there_are_eighteen(
    monkeypatch,
):
    """The shipped selector's predecessor, driven through the same stub.

    THE POINT IS NOT THAT 54 IS WRONG. It is that 54 looked RIGHT: in the live
    run that found this, ``rows`` and ``event_links`` came back 9/9 and 45/45
    -- two selectors agreeing exactly -- because this page draws three anchors
    per row and the broken selector counted three sections per row. Two
    instruments agreeing is evidence only when their errors are independent.
    """
    monkeypatch.setattr(
        events, "EVENTS_HOME_ROW_SELECTOR", 'section[class*="discovery-card"]'
    )
    broken = await events.read_events_home(_page())
    assert [card["rows"] for card in broken["cards"]] == [0, 9, 45]
    assert broken["rows_total"] == 54

    # THE MUTATION MUST BE LIFTED BEFORE THE CONTROL RUNS. Without this the
    # second reading is taken through the SAME broken selector and asserts 18
    # against 54 -- which is how this line was written the first time, and it
    # failed loudly rather than quietly, which is the only reason it is right
    # now.
    monkeypatch.undo()
    shipped = await events.read_events_home(_page())
    assert shipped["rows_total"] == 18
    assert "~=" in events.EVENTS_HOME_ROW_SELECTOR


# ---------------------------------------------------------------------------
# The zero, refused in every case where it would be a lie
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_an_unhydrated_page_refuses_instead_of_reporting_zero():
    """EVERY card empty is a fact about the read, not about his account."""
    reading = await events.read_events_home(
        _page(own_rows=0, promoted_rows=0, recommended_rows=0)
    )
    assert reading["cards_read"] == 3
    assert reading["verdict"] == "page_unhydrated"
    assert reading["registered_events"] is None


@pytest.mark.asyncio
async def test_a_renamed_section_refuses_and_says_what_it_saw():
    """A LABEL CHANGE MUST NOT ARRIVE AS A ZERO.

    It arrives as a refusal carrying the card count and each card's row count,
    so a reader can tell "LinkedIn renamed it" from "the page did not load"
    without opening a browser. That distinction is the one
    ``refusals must name what they saw`` was written for.
    """
    reading = await events.read_events_home(_page(own_heading="My events"))
    assert reading["verdict"] == "heading_unmatched"
    assert reading["registered_events"] is None
    assert reading["cards_read"] == 3
    assert reading["rows_total"] == 18
    assert all(card["known"] is None for card in reading["cards"])


@pytest.mark.asyncio
async def test_a_page_with_no_cards_refuses():
    reading = await events.read_events_home(_FakePage(_Node("body")))
    assert reading["cards_read"] == 0
    assert reading["verdict"] == "no_cards"
    assert reading["registered_events"] is None


@pytest.mark.asyncio
async def test_rows_under_the_self_scoped_card_are_reported_as_the_count():
    """The branch nobody can exercise on this account, asserted anyway.

    He is registered for zero events today. When that changes this is the
    branch that fires, and a branch first exercised in production is a branch
    nobody has tested.
    """
    reading = await events.read_events_home(_page(own_rows=4))
    assert reading["verdict"] == "rows_present"
    assert reading["registered_events"] == 4


def test_only_one_verdict_may_carry_a_number():
    """THE WHOLE DECISION TABLE, and the property that matters across it.

    Exactly one verdict returns an integer zero, and it requires both halves
    of the corroborator. Delete either half and this goes red.
    """
    table = {
        (False, 0, 0, 0): (None, "no_cards"),
        (False, 0, 18, 3): (None, "heading_unmatched"),
        (True, 4, 18, 3): (4, "rows_present"),
        (True, 0, 0, 3): (None, "page_unhydrated"),
        (True, 0, 18, 3): (0, "empty_beside_full_siblings"),
    }
    for (found, own, other, cards), expected in table.items():
        assert events._events_home_verdict(
            found=found, own_rows=own, other_rows=other, cards=cards
        ) == expected
    zero_carrying = [
        verdict for verdict, _name in table.values() if verdict == 0
    ]
    assert len(zero_carrying) == 1


# ---------------------------------------------------------------------------
# What the heading channel does and does not redact -- DECLARED, not implied
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_a_person_named_heading_does_not_ship():
    """The hole recorded on ``shape.membership_row`` is NOT in this reader.

    A two-token capitalised run seen once is redacted by the shipped rule, and
    the identification does not depend on the text surviving -- ``known``
    carries a key this module owns. So a card headed with somebody's name is
    reported as a card with a row count and no name.
    """
    reading = await events.read_events_home(_page(own_heading="Ada Lovelace"))
    shapes = [card["heading_shape"] for card in reading["cards"]]
    assert "Ada Lovelace" not in shapes
    assert shapes[0] == "<redacted>"


@pytest.mark.asyncio
async def test_a_single_token_heading_ships_and_that_limit_is_declared_here():
    """A KNOWN LIMIT, WRITTEN AS A PASSING TEST SO THAT FIXING IT TURNS RED.

    ``census_redact_rare`` fires on a capitalised run of TWO OR MORE seen once.
    A one-token heading survives -- which is correct for ``Your events`` and
    ``Events``, and is also why a section headed with a single-word company or
    product name would ship that word.

    THE TRADE IS THE SAME ONE ``membership_row`` RECORDS AND THE ANSWER IS
    DIFFERENT, because the payload is different: this reader's usefulness does
    not depend on the heading at all. If that word is ever judged too much,
    the fix is to stop emitting ``heading_shape`` entirely -- the row counts
    and ``known`` carry the whole answer -- and this test is the thing that
    will go red and say so.
    """
    reading = await events.read_events_home(_page(own_heading="Acme"))
    assert reading["cards"][0]["heading_shape"] == "Acme"
    assert reading["cards"][0]["known"] is None
    assert reading["verdict"] == "heading_unmatched"
