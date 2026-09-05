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

#: The card's body. Measured on the live page: on the self-scoped card its
#: inner HTML is a framework empty-binding comment and whitespace -- 0
#: characters of text and 0 descendant elements.
BODY_CLASS = (
    "events-events-card-container__main display-flex "
    "align-items-flex-start flex-wrap"
)

#: A skeleton, as a shimmer bar with no text. THE SHAPE THE OBJECTION
#: DESCRIBES: a container that has arrived before its contents, which counts
#: zero rows and zero characters and is NOT an empty list.
SHIMMER_CLASS = "artdeco-loader events-shimmer__bar"

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
    if selector.strip() == "*":
        return True
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
        """The node's own text plus its descendants', as a browser returns it.

        The first version returned only the node's OWN text, which made every
        body read 0 characters however full it was -- so the ``body_not_empty``
        branch could not be reached through a rendered empty state, and the
        test for it would have passed for the wrong reason.
        """
        del timeout
        if not self.nodes:
            return ""
        node = self.nodes[0]
        parts = [node.text] + [child.text for child in node.walk()]
        return " ".join(part for part in parts if part).strip()


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


#: The card's footer. On the self-scoped card, measured EMPTY. On a sibling it
#: carries the control that announces how many events the section really has.
FOOTER_CLASS = "events-events-card-container__footer display-flex justify-center"


def _card(heading, rows, classes=CARD_CLASS, body_extra=(), footer_extra=()):
    """A card: a header carrying the heading, a body of rows, and a footer.

    ``body_extra`` puts something in the body that is NOT a row -- a shimmer,
    an empty-state paragraph -- which is how the hydration branch is reached.
    ``footer_extra`` puts a paging control in the footer, which is how the
    partial-count branch is reached.
    """
    body = _Node(
        "main",
        BODY_CLASS,
        children=[_row() for _ in range(rows)] + list(body_extra),
    )
    footer = _Node("footer", FOOTER_CLASS, children=list(footer_extra))
    return _Node(
        "section",
        classes,
        children=[
            _Node("header", children=[_Node("h2", text=heading)]),
            body,
            footer,
        ],
    )


def _page(
    own_heading="Your events",
    own_rows=0,
    promoted_rows=3,
    recommended_rows=15,
    own_body_extra=(),
    own_body=True,
    own_footer_extra=(),
):
    """The events root as MEASURED, with each count a parameter.

    Defaults reproduce the live reading exactly: 3 cards, 0/3/15 rows,
    0/9/45 anchors, and a self-scoped body holding neither text nor elements.
    """
    own = _card(
        own_heading,
        own_rows,
        body_extra=own_body_extra,
        footer_extra=own_footer_extra,
    )
    if not own_body:
        # THE BODY GONE ENTIRELY, which is what a markup change looks like.
        own = _Node(
            "section",
            CARD_CLASS,
            children=[_Node("header", children=[_Node("h2", text=own_heading)])],
        )
    cards = [
        own,
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


@pytest.mark.asyncio
async def test_a_shimmer_in_the_body_refuses_instead_of_reporting_zero():
    """A CONTAINER ARRIVES BEFORE ITS CONTENTS, and this is that case.

    A card holding a skeleton bar has zero rows and zero characters of text,
    so a reader concluding from the ROWS alone would answer "he is registered
    for zero events" about a card that has not finished loading.
    ``unhydrated`` is not ``absent``.

    **The sibling-card corroborator does not close this on its own** -- the
    siblings here are full and the answer is still a refusal -- because
    different cards hydrate from different calls, so full siblings prove the
    PAGE hydrated and not that THIS card did. That gap is the whole reason the
    body is read directly.
    """
    reading = await events.read_events_home(
        _page(own_body_extra=[_Node("div", SHIMMER_CLASS)])
    )
    assert reading["cards"][0]["rows"] == 0
    assert reading["cards"][0]["body_elements"] == 1
    assert reading["cards"][0]["body_text_chars"] == 0
    assert reading["verdict"] == "body_not_empty"
    assert reading["registered_events"] is None


@pytest.mark.asyncio
async def test_a_rendered_empty_state_also_refuses():
    """TEXT IN THE BODY IS ALSO NOT A ZERO.

    If LinkedIn one day draws "you have no upcoming events" there, that is an
    answer this reader does not know how to read, and the honest response is
    to say so rather than to agree with it by coincidence.
    """
    reading = await events.read_events_home(
        _page(own_body_extra=[_Node("p", text="No upcoming events")])
    )
    assert reading["cards"][0]["body_text_chars"] > 0
    assert reading["verdict"] == "body_not_empty"
    assert reading["registered_events"] is None


@pytest.mark.asyncio
async def test_a_missing_body_refuses_rather_than_falling_back_to_the_rows():
    """No body, no evidence. The rows alone were never enough."""
    reading = await events.read_events_home(_page(own_body=False))
    assert reading["cards"][0]["body_found"] is False
    assert reading["verdict"] == "body_unreadable"
    assert reading["registered_events"] is None


@pytest.mark.asyncio
async def test_a_paging_control_makes_the_count_a_floor_and_says_so():
    """``rows`` COUNTS WHAT IS DRAWN, AND A SECTION CAN DRAW A SUBSET.

    Measured on the live page: a sibling card draws THREE rows and its footer
    control announces FIFTY events. A reader taking ``rows`` as a total would
    be wrong by a factor of seventeen with nothing about the reading looking
    suspicious.

    It does not touch the zero -- a card drawing nothing has nothing to page
    through, and the self-scoped card's footer is measured empty. It touches
    ``rows_present``, which is why the verdict changes rather than the number.
    """
    reading = await events.read_events_home(
        _page(own_rows=4, own_footer_extra=[_Node("button", text="Show all")])
    )
    assert reading["cards"][0]["footer_found"] is True
    assert reading["cards"][0]["footer_elements"] == 1
    assert reading["verdict"] == "rows_present_may_be_partial"
    assert reading["registered_events"] == 4

    plain = await events.read_events_home(_page(own_rows=4))
    assert plain["cards"][0]["footer_elements"] == 0
    assert plain["verdict"] == "rows_present"


@pytest.mark.asyncio
async def test_an_empty_footer_does_not_turn_the_zero_into_a_refusal():
    """The footer is EVIDENCE ABOUT A COUNT, not a third hydration signal.

    The self-scoped card has a footer; it is empty. If the footer had been
    folded into the body check, the measured page would refuse instead of
    answering, which would be a reader that cannot read the one page it was
    written for.
    """
    reading = await events.read_events_home(_page())
    assert reading["cards"][0]["footer_found"] is True
    assert reading["cards"][0]["footer_elements"] == 0
    assert reading["verdict"] == "empty_beside_full_siblings"
    assert reading["registered_events"] == 0


def test_only_one_verdict_may_carry_a_number():
    """THE WHOLE DECISION TABLE, and the property that matters across it.

    Exactly one verdict returns an integer zero, and reaching it takes FOUR
    independent facts: the card present, no rows, a body holding neither text
    nor elements, and a non-empty sibling. Delete any one and this goes red.
    """
    def call(
        found, own, other, cards, body=True, chars=0, elements=0, footer=0
    ):
        return events._events_home_verdict(
            found=found,
            own_rows=own,
            other_rows=other,
            cards=cards,
            body_found=body,
            body_text_chars=chars,
            body_elements=elements,
            footer_content=footer,
        )

    table = [
        (call(False, 0, 0, 0), (None, "no_cards")),
        (call(False, 0, 18, 3), (None, "heading_unmatched")),
        (call(True, 4, 18, 3), (4, "rows_present")),
        (call(True, 4, 18, 3, footer=1), (4, "rows_present_may_be_partial")),
        (call(True, 0, 18, 3, body=False), (None, "body_unreadable")),
        (call(True, 0, 18, 3, elements=1), (None, "body_not_empty")),
        (call(True, 0, 18, 3, chars=26), (None, "body_not_empty")),
        (call(True, 0, 0, 3), (None, "page_unhydrated")),
        (call(True, 0, 18, 3), (0, "empty_beside_full_siblings")),
    ]
    for actual, expected in table:
        assert actual == expected
    zero_carrying = [actual for actual, _ in table if actual[0] == 0]
    assert len(zero_carrying) == 1
    assert zero_carrying[0][1] == "empty_beside_full_siblings"


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
