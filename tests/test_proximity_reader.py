"""The per-job network-proximity reader -- census row ``J 40``.

WHAT THIS FILE IS FOR. ``tests/test_proximity_is_on_a_read_surface.py`` pinned
the evidence that the field is DRAWN on two committed captures and read by
nothing. This file is the other half: the reader that now reads it, and the
proof that it cannot carry a name out.

THE HAZARD, STATED ONCE. LinkedIn draws the search-card insight TWICE, and the
two copies differ:

    <span aria-hidden="true">       1 company alum works here
    <span class="visually-hidden">  1 <ORG> company alum works here

The ACCESSIBLE copy is the one carrying the employer. So the three things that
have to be true, and each has a section below:

  1. THE READER RETURNS INTEGERS.  Relation is a position in an alphabet this
     package authored; count is accumulated digit by digit. There is no path
     that returns a substring of a page, so even a total failure of the
     subtraction upstream costs a wrong COUNT and never a name. Section 3
     drives the reader over the leaked line DIRECTLY and asserts the output
     carries nothing from it.
  2. THE NEGATIVE CONTROLS HOLD.  The un-hydrated twins of both captures --
     the same two pages before the client-side render -- must read NOTHING.
     Same reader, same pages, opposite answer, so a pass means the reader
     discriminates rather than matching prose. Section 4.
  3. THE ANCHORING IS UNDISTURBED.  ``parse_job_card``'s docstring records
     that an inserted line became the ``company`` on 5 of 14 rows measured
     live, and names "an alumni line" as able to do the same. Section 4 checks
     title, company and location on every row of every render against the
     values the committed fixture test already pins.

SHOWN FAILING BEFORE ADMISSION -- receipts in
``_audit/2026-09-21-the-proximity-field.md`` section 4. Every check here was
run red first: the containment law by adding a containing phrase, the leak
guard by pointing the reader at ``record["text"]`` instead of the subtracted
lines, the de-duplication by counting matches instead of facts, the numeral
refusals by accepting a decimal, and the fixture assertions by deleting the
insight from a COPY of the capture and by swapping each control's file for its
hydrated twin.

No network, no LinkedIn account, no writes. Sections 1-3 need no browser at
all; section 4 renders four committed files in a local headless Chromium.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The employer named ONLY in the hidden, name-carrying copy of the insight on
#: ``jobs_search_hydrated.html``. It is invented, like every name in these
#: captures. It is the needle for the leak checks: this string is on the page,
#: it is in ``record["hidden"]``, and it must never reach a parsed row.
LEAKED_ORG = "Marlowe Consulting"

#: The line as the page's ACCESSIBLE copy draws it -- the one that leaks.
LEAKED_LINE = "1 %s company alum works here" % LEAKED_ORG

#: The line as the page's ``aria-hidden`` copy draws it -- the safe one.
SAFE_LINE = "1 company alum works here"

#: The job detail page's only proximity rendering. It carries the employer and
#: NO count, which is why detail is a relation and never a number.
DETAIL_ORG = "Fernhollow Technology"
DETAIL_LINE = "Company alumni from %s" % DETAIL_ORG


def resolved(reading):
    """A reading with its positions resolved to literals, for readable asserts."""
    if reading is None:
        return None
    return (
        shape.state_for(reading["state"]),
        None if reading["relation"] is None
        else shape.relation_for(reading["relation"]),
        reading["count"],
    )


# ---------------------------------------------------------------------------
# 1. The alphabets and the phrase table
# ---------------------------------------------------------------------------
#
# Static properties of constants. They cost nothing to run and they are what
# keeps the rest of the file from certifying a table that has quietly drifted.


def test_the_phrase_table_is_not_empty_and_every_relation_is_declared():
    """Anti-vacuity. An empty table makes every reader test below pass."""
    assert shape.PROXIMITY_PHRASES, "no phrases -- every reader check is vacuous"
    assert shape.PROXIMITY_RELATIONS, "no relations -- nothing can be reported"
    for relation, phrase, _counted in shape.PROXIMITY_PHRASES:
        assert relation in shape.PROXIMITY_RELATIONS, (
            "phrase %r names relation %r, which is not in the alphabet, so a "
            "reading off it cannot be resolved" % (phrase, relation)
        )


def test_no_shipped_phrase_contains_another():
    """THE DE-DUPLICATION LAW, enforced on the constants rather than at runtime.

    Two phrases where one contains the other match the same line and produce
    two readings of ONE fact. Downstream that reads either as corroboration or
    as a disagreement with itself -- both are wrong, and both are invisible.
    ``company_root.COUNT_PHRASES`` carries the same law for the same reason.
    """
    phrases = [phrase for _relation, phrase, _counted in shape.PROXIMITY_PHRASES]
    assert len(phrases) == len(set(phrases)), "a phrase is listed twice"
    for outer in phrases:
        for inner in phrases:
            if outer is inner:
                continue
            assert inner not in outer, (
                "phrase %r contains %r: any line matching the second matches "
                "the first too, so one fact is read twice" % (outer, inner)
            )


def test_every_phrase_is_already_in_the_form_the_reader_compares_against():
    """The reader lowercases and collapses whitespace, then calls ``str.find``.

    A phrase carrying a capital or a double space can therefore never match
    anything, and would fail SILENTLY -- as a field that is simply never read.
    """
    for _relation, phrase, _counted in shape.PROXIMITY_PHRASES:
        assert phrase == phrase.lower(), "%r is not lowercase" % phrase
        assert phrase == re.sub(r"\s+", " ", phrase).strip(), (
            "%r is not single-spaced and stripped" % phrase
        )
        assert phrase, "an empty phrase matches every line"


def test_the_named_state_positions_still_name_those_states():
    """The index constants are spelled as literals; this is what binds them.

    Reordering ``PROXIMITY_STATES`` without moving these renames every reading
    ever taken -- silently, because an integer looks the same whatever it now
    means.
    """
    assert shape.PROXIMITY_STATES[shape._PROX_NOT_DRAWN] == "not_drawn"
    assert shape.PROXIMITY_STATES[shape._PROX_RELATION_ONLY] == "relation_only"
    assert shape.PROXIMITY_STATES[shape._PROX_NUMERAL_REFUSED] == "numeral_refused"
    assert shape.PROXIMITY_STATES[shape._PROX_DISAGREEMENT] == "disagreement"
    assert shape.PROXIMITY_STATES[shape._PROX_COUNT_READ] == "count_read"


@pytest.mark.parametrize(
    "resolver,alphabet",
    [
        (shape.relation_for, shape.PROXIMITY_RELATIONS),
        (shape.state_for, shape.PROXIMITY_STATES),
    ],
)
def test_a_position_resolver_refuses_out_of_range_and_never_clamps(resolver, alphabet):
    """A clamp would silently rename one term to another -- position 0 in both
    alphabets is a real term, so folding onto it is a wrong answer, not a
    degraded one."""
    for position, term in enumerate(alphabet):
        assert resolver(position) == term
    for bad in (-1, len(alphabet), len(alphabet) + 50):
        assert resolver(bad) == "position_out_of_range"


def test_the_alphabet_helper_covers_everything_a_reading_resolves_to():
    published = shape.proximity_alphabet()
    for position in range(len(shape.PROXIMITY_STATES)):
        assert shape.state_for(position) in published
    for position in range(len(shape.PROXIMITY_RELATIONS)):
        assert shape.relation_for(position) in published
    assert shape.relation_for(9999) in published


# ---------------------------------------------------------------------------
# 2. The reader, over lines. No browser.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line,expected",
    [
        # MEASURED -- the line the search capture actually draws.
        (SAFE_LINE, ("count_read", "company_alum", 1)),
        # MEASURED -- the line the detail capture actually draws. No count.
        (DETAIL_LINE, ("relation_only", "company_alum", None)),
        # The singular/plural siblings.
        ("4 company alums work here", ("count_read", "company_alum", 4)),
        ("2 company alumni work here", ("count_read", "company_alum", 2)),
        ("1 school alum works here", ("count_read", "school_alum", 1)),
        ("7 school alums work here", ("count_read", "school_alum", 7)),
        ("1 connection works here", ("count_read", "connection", 1)),
        ("11 connections work here", ("count_read", "connection", 11)),
        # Grouped digits.
        ("1,234 company alums work here", ("count_read", "company_alum", 1234)),
        # A phrase with no numeral in front of it is a relation, not a zero.
        ("company alums work here", ("relation_only", "company_alum", None)),
        # Nothing proximity-shaped at all.
        ("Promoted", ("not_drawn", None, None)),
        ("Actively reviewing applicants", ("not_drawn", None, None)),
        # A bare "alum" is NOT a proximity fact -- it is how an alumni FILTER
        # label or a school page would drag this reader into reporting one.
        ("Alumni", ("not_drawn", None, None)),
        ("See alumni", ("not_drawn", None, None)),
    ],
)
def test_one_line_reads_as_the_fact_it_states(line, expected):
    assert resolved(shape.find_proximity([line])) == expected


@pytest.mark.parametrize(
    "line",
    [
        "1.5 company alums work here",       # a decimal
        "10k company alums work here",       # an abbreviation
        "80% company alums work here",       # a percentage
        "1,23 company alums work here",      # malformed grouping
        "1,2345 company alums work here",    # malformed grouping
        "12,34,567 company alums work here", # malformed grouping
        "1234567 company alums work here",   # a run longer than the ceiling
        # THE DIGIT RUN IS PART OF SOMETHING LARGER. Each of these would read
        # as a plausible wrong number if the walk-back stopped at the digits
        # and did not look at what precedes them: 21, 2, 30, 50.
        "2026-09-21 company alums work here",   # a date
        "1/2 company alums work here",          # a fraction
        "12:30 company alums work here",        # a clock time
        "up 50% company alums work here",       # a percentage
    ],
)
def test_a_numeral_this_reader_will_not_commit_to_is_refused_not_guessed(line):
    """A REFUSAL IS NEVER A COUNT AND NEVER A ZERO.

    Each of these carries a numeral in a shape the reader does not read. The
    dangerous outcome is not the missing number, it is reading ``1.5`` as 5 or
    ``10k`` as 10 -- a plausible wrong number in a real field, which nothing
    downstream can tell from a right one.
    """
    reading = shape.find_proximity([line])
    assert reading["count"] is None, (
        "%r produced a count of %r; a numeral the reader does not understand "
        "must be refused, not repaired" % (line, reading["count"])
    )
    assert shape.state_for(reading["state"]) == "numeral_refused"


@pytest.mark.parametrize(
    "line",
    [
        # The phrase at the very start of the line -- nothing precedes it.
        "company alum works here",
        # A WORD where the numeral would be. This case was added after a
        # mutation survived: setting the "no digit run" branch of
        # ``_digits_before`` to report a refusal did NOT turn this test red,
        # because both original cases returned before reaching that branch --
        # one has the phrase at position 0, the other uses an uncounted
        # phrase. The branch was untested and the check could not fail.
        "several company alums work here",
        "your company alums work here",
        # The detail page's phrase, which carries no numeral by construction.
        DETAIL_LINE,
    ],
)
def test_a_relation_with_no_numeral_is_not_reported_as_a_refusal(line):
    """``relation_only`` and ``numeral_refused`` are different answers.

    The first says the page stated a relation and no number; the second says it
    stated a number this reader would not read. Collapsing them loses the only
    signal that the phrase table has gone stale against LinkedIn's numerals.
    """
    assert shape.state_for(shape.find_proximity([line])["state"]) == "relation_only"


def test_the_same_fact_rendered_twice_is_one_fact():
    """DE-DUPLICATION IS ON THE FACT, NOT ON THE MATCH.

    The measured case is one insight rendered twice, 95 characters apart.
    Counting matches would report that as two readings of one card and, worse,
    a reader that compared match COUNTS would call it corroboration.
    """
    once = shape.find_proximity([SAFE_LINE])
    twice = shape.find_proximity([SAFE_LINE, SAFE_LINE])
    welded = shape.find_proximity(["%s %s" % (SAFE_LINE, SAFE_LINE)])
    assert resolved(once) == ("count_read", "company_alum", 1)
    assert resolved(twice) == resolved(once)
    assert resolved(welded) == resolved(once)


def test_two_different_relations_on_one_card_are_refused_rather_than_picked():
    """Both may be true and this reader has one slot. Choosing invents a fact
    about which one the card meant.

    **THE COUNTS ARE DELIBERATELY EQUAL**, and that is the whole case. An
    earlier version of this check used counts 1 and 3, so the reading was
    refused by the COUNT-disagreement branch and the relation branch was never
    reached -- a mutation that disabled the relation branch outright left this
    test green. With one shared count only the relation branch can produce a
    refusal, so a pass now means what the name says.
    """
    reading = shape.find_proximity(
        ["1 company alum works here", "1 connection works here"]
    )
    assert resolved(reading) == ("disagreement", None, None)


def test_two_different_counts_for_one_relation_are_refused_rather_than_picked():
    """The other disagreement, kept separate so each branch has its own check."""
    reading = shape.find_proximity(
        ["1 company alum works here", "4 company alums work here"]
    )
    assert shape.state_for(reading["state"]) == "disagreement"
    assert reading["count"] is None
    assert reading["relation"] is None


def test_a_refused_numeral_suppresses_a_clean_one_elsewhere_on_the_card():
    """The two copies disagree about what the page says, and adjudicating that
    is not this module's job."""
    reading = shape.find_proximity([SAFE_LINE, "1.5 company alums work here"])
    assert reading["count"] is None
    assert shape.state_for(reading["state"]) == "numeral_refused"


@pytest.mark.parametrize(
    "hostile",
    [
        None,
        "",
        "   ",
        "\x00\x01",
        "company alum works here" * 400,
        "1" * 5000 + " company alums work here",
        ",,,, company alums work here",
        "- company alums work here",
        "\u00a0\u00a03\u00a0connections work here",  # non-breaking spaces
    ],
)
def test_the_reader_never_raises_on_hostile_input(hostile):
    """It must answer, never raise. A raised exception from a page-derived
    value is how ``int()`` puts that value into a traceback -- see
    ``coerce``'s module docstring."""
    reading = shape.find_proximity([hostile])
    assert set(reading) == {"state", "relation", "count"}


def test_the_reader_tolerates_a_non_list_and_an_empty_one():
    assert resolved(shape.find_proximity([])) == ("not_drawn", None, None)
    assert resolved(shape.find_proximity(None)) == ("not_drawn", None, None)
    assert resolved(shape.find_proximity(())) == ("not_drawn", None, None)


# ---------------------------------------------------------------------------
# 3. THE LEAK CHECKS. The reader is pointed straight at the name.
# ---------------------------------------------------------------------------
#
# Sections 1 and 2 test what the reader does with safe input. These test what
# it does with the input the safety mechanism exists to remove -- because a
# guarantee that depends on an upstream subtraction is a guarantee about the
# subtraction, not about this module.

#: Lines that carry a person's or an employer's name INTO the reader. Every
#: one of these is what a card looks like when ``strip_screen_reader_copies``
#: has not run, has been passed the wrong argument, or has silently stopped
#: matching because LinkedIn renamed its screen-reader class.
LEAKY_LINES = [
    LEAKED_LINE,
    DETAIL_LINE,
    "1 Marlowe Consulting company alum works here",
    "Company alumni from Fernhollow Technology",
    "3 connections work here at Marlowe Consulting",
    "1 company alum works here Marlowe Consulting",
    "School alumni from Riverton Institute of Technology",
]


@pytest.mark.parametrize("line", LEAKY_LINES)
def test_a_reading_carries_no_text_from_the_line_it_was_read_from(line):
    """THE CORE GUARANTEE, and it is asserted structurally rather than by
    searching the output for known names.

    Searching for the specific employer would pass for any name this test did
    not think of. So this asserts the TYPE: every value in a reading is an
    ``int`` or ``None``, which no string on any page can satisfy.
    """
    reading = shape.find_proximity([line])
    for field, value in reading.items():
        assert value is None or isinstance(value, int), (
            "field %r came back as %s. A reading is integers and None; any "
            "other type is a channel a page can write to." % (field, type(value).__name__)
        )
        assert not isinstance(value, str)


def test_the_leaked_copy_and_the_safe_copy_read_as_one_fact_not_two():
    """THE SUBTRACTION-FAILURE SIMULATION.

    This is the card as it would arrive if ``.visually-hidden`` stopped being
    matched: BOTH copies present, 95 characters apart, saying the same thing in
    different words. The reader must report ONE fact, must still refuse to
    return the employer, and must not mistake the pair for a disagreement.
    """
    reading = shape.find_proximity([SAFE_LINE, LEAKED_LINE])
    assert resolved(reading) == ("count_read", "company_alum", 1), (
        "the two copies of one insight were not folded into one fact"
    )
    assert LEAKED_ORG not in json.dumps(reading)


def test_the_word_before_the_phrase_is_never_read_as_a_count():
    """The leaked copy puts the EMPLOYER where the count sits on the safe one.

    If the count reader walked back over anything other than digits it would
    read the employer's last word. It must answer "no numeral here" instead.
    """
    reading = shape.find_proximity([LEAKED_LINE])
    assert reading["count"] is None, (
        "a count was read out of %r, where the characters before the phrase "
        "are an employer's name and not a numeral" % LEAKED_LINE
    )


def test_no_line_of_this_reader_calls_int_or_float_on_page_text():
    """``int("Jane Smith")`` raises ``ValueError: invalid literal for int()
    with base 10: 'Jane Smith'`` -- the constructor quotes the value it refused
    into its own message and that propagates out of a function whose return
    type promised no strings. This repository measured it: **14 of 115 readers
    carried a planted name out through a ValueError**, 2026-09-20, recorded in
    ``linkedin_server/coerce.py``'s module docstring.

    So the count is accumulated with ``ord()``. This asserts the source, not
    the behaviour, because the behaviour only shows the leak on the inputs a
    test happened to try.
    """
    import ast
    import inspect
    import textwrap

    for function in (shape._digits_before, shape.find_proximity):
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert "int" not in called, (
            "%s calls int() -- on a refusal that quotes the page value into a "
            "ValueError and out of the process" % function.__name__
        )
        assert "float" not in called, "%s calls float()" % function.__name__


# ---------------------------------------------------------------------------
# 4. The committed captures, through a real browser
# ---------------------------------------------------------------------------

SEARCH_HYDRATED = "jobs_search_hydrated.html"
SEARCH_PRE = "jobs_search.html"
DETAIL_HYDRATED = "job_detail_following_hydrated.html"
DETAIL_PRE = "job_detail_following.html"

_STYLE_BLOCK = re.compile(r"<style>.*?</style>", re.S)

#: The job on ``jobs_search_hydrated.html`` that carries the insight, and the
#: fact it states. Written out rather than derived: "some row has proximity"
#: is true of a reader that tagged every row, so an assertion that does not
#: name the answer cannot see that bug.
CARRIER = "4600000014"
CARRIER_FACT = ("count_read", "company_alum", 1)


def markup(name: str, *, styled: bool = True) -> str:
    """The capture, optionally with LinkedIn's screen-reader rule removed.

    UNSTYLED IS THE SECOND LAYOUT, not a broken one. Without the rule the
    hidden copy is inline and ``innerText`` welds it onto its neighbour rather
    than giving it a line -- so the name-carrying copy arrives in a different
    SHAPE, and ``strip_screen_reader_copies`` has to take it out as a substring
    instead of as a line. Both renders are real; which one arrives depends on
    whether the stylesheet had loaded. The answer must not depend on it.
    """
    html = (FIXTURE_DIR / name).read_text(encoding="utf-8")
    return html if styled else _STYLE_BLOCK.sub("", html)


async def _with_html(html: str, work):
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


async def _rows(name: str, *, styled: bool = True):
    """The parsed rows of a capture.

    ``parse_all`` returns ``(rows, dropped)`` and the dropped count is checked
    here rather than discarded: a row that failed to parse leaves no entry to
    assert against, so every check below would pass by its absence.
    """
    async def work(page):
        return await dom.harvest_linked_cards(
            page, href_pattern=dom.JOB_HREF, max_items=60
        )

    records = await _with_html(markup(name, styled=styled), work)
    rows, dropped = dom.parse_all(records, shape.parse_job_card)
    assert dropped == 0, (
        "%s: %d of %d records failed to parse. A dropped row cannot fail an "
        "assertion about its contents." % (name, dropped, len(records))
    )
    return rows


async def _detail(name: str):
    async def work(page):
        return await dom.read_main_text(page)

    main_text = await _with_html(markup(name), work)
    return shape.parse_job_detail(main_text, company=None, document_title=None)


@pytest.mark.parametrize("styled", [True, False])
async def test_the_hydrated_search_card_reads_the_fact_the_page_states(styled):
    """POSITIVE. One named row, one named fact, in both layouts."""
    rows = await _rows(SEARCH_HYDRATED, styled=styled)
    assert rows, "an empty harvest would make every assertion here vacuous"
    by_id = {row.get("job_id"): row for row in rows}
    assert CARRIER in by_id, (
        "the capture no longer holds job %s -- it was replaced, and this "
        "module is no longer testing what it was calibrated against" % CARRIER
    )
    assert resolved(by_id[CARRIER].get("proximity")) == CARRIER_FACT


@pytest.mark.parametrize("styled", [True, False])
async def test_exactly_one_row_of_the_hydrated_search_carries_the_field(styled):
    """A reader that tagged every row would satisfy the positive check above.

    The page draws the insight on ONE of its seven jobs, so this is the check
    that the reader is reading the page rather than decorating it.
    """
    rows = await _rows(SEARCH_HYDRATED, styled=styled)
    carriers = sorted(row.get("job_id") for row in rows if row.get("proximity"))
    assert carriers == [CARRIER], (
        "expected exactly [%r] to carry proximity, got %r" % (CARRIER, carriers)
    )


@pytest.mark.parametrize("styled", [True, False])
async def test_no_row_of_the_un_hydrated_twin_carries_the_field(styled):
    """THE CONTROL, and it is the tightest one available: the SAME page before
    the client-side render, the same reader, the opposite answer.

    Without it a pass above would be consistent with a reader that matches
    LinkedIn chrome present on every job page.
    """
    rows = await _rows(SEARCH_PRE, styled=styled)
    assert rows, "an empty harvest would make this control vacuous"
    carried = {row.get("job_id"): resolved(row.get("proximity"))
               for row in rows if row.get("proximity")}
    assert carried == {}, (
        "the un-hydrated capture produced proximity readings %r. The reader "
        "has stopped discriminating, so the positive result means nothing."
        % carried
    )


@pytest.mark.parametrize("styled", [True, False])
async def test_no_parsed_row_carries_the_employer_named_only_in_the_hidden_copy(styled):
    """THE END-TO-END LEAK CHECK, over the real capture.

    ``%s`` appears on that page exactly once, inside the ``.visually-hidden``
    copy of the insight -- it is not the row's employer, which is a different
    invented company. So its presence anywhere in a serialised row is proof the
    accessible copy reached the output.

    This runs in BOTH layouts because the unstyled render is where the hidden
    copy welds onto its neighbour instead of taking a line of its own, which is
    a different subtraction path.
    """ % LEAKED_ORG
    rows = await _rows(SEARCH_HYDRATED, styled=styled)
    assert rows, "an empty harvest would make this leak check vacuous"
    blob = json.dumps(rows)
    assert LEAKED_ORG not in blob, (
        "%r reached a parsed row. The screen-reader subtraction did not remove "
        "the accessible copy, or something downstream read the raw card text."
        % LEAKED_ORG
    )


@pytest.mark.parametrize("styled", [True, False])
async def test_the_new_field_moved_no_existing_field_on_any_row(styled):
    """THE ANCHORING CHECK.

    ``parse_job_card``'s docstring records a measured field shift -- on 5 of 14
    live rows an inserted screen-reader line became the ``company`` and pushed
    the real company into ``location`` -- and names "an alumni line" among the
    insertions able to do it. This asserts the three anchored fields on every
    row of the capture that actually carries an alumni line.

    If this is red, the anchoring is right and the reader is wrong.
    """
    rows = await _rows(SEARCH_HYDRATED, styled=styled)
    by_id = {row.get("job_id"): row for row in rows}
    expected = {
        "4600000014": ("Software Engineer", "Grandview Networks",
                       "Fairhaven, Riverton, Westland (On-site)"),
        "4600000001": ("Senior Software Engineer", "Northwind Labs",
                       "Fairhaven, Riverton, Westland (On-site)"),
        "4600000015": ("Senior Backend Developer (Node.js / NestJS)",
                       "Harborline Finance",
                       "Fairhaven, Riverton, Westland (On-site)"),
    }
    for job_id, (title, company, location) in expected.items():
        assert job_id in by_id, "row %s left the capture" % job_id
        row = by_id[job_id]
        assert (row.get("title"), row.get("company"), row.get("location")) == (
            title, company, location
        ), "row %s: the proximity field displaced an anchored field" % job_id


async def test_the_hydrated_detail_page_reads_a_relation_and_no_count():
    """The detail capture draws "Company alumni from <ORG>" -- no name-free
    twin, no numeral, and not one ``.visually-hidden`` element on the page. A
    count is not available there and must not be invented."""
    detail = await _detail(DETAIL_HYDRATED)
    assert resolved(detail.get("proximity")) == ("relation_only", "company_alum", None)
    assert DETAIL_ORG not in json.dumps(detail.get("proximity"))


async def test_the_un_hydrated_detail_twin_reads_nothing():
    """THE DETAIL CONTROL. Same page before the render, same reader, no field."""
    detail = await _detail(DETAIL_PRE)
    assert detail.get("proximity") is None, (
        "the un-hydrated detail capture produced %r" % (detail.get("proximity"),)
    )


async def test_the_detail_reader_does_not_read_the_job_description():
    """SCOPE. The reader runs over the header region, not the whole page.

    A description is prose an employer wrote, and it can contain the phrase --
    "company alumni from our graduate programme" -- which read as proximity
    would report a fact about the account's own network from marketing copy.
    The measured header is 13 lines of 222; this drives the boundary directly.
    """
    body = "\n".join([
        "Vantrex Systems",
        "Settlement Platform Analyst",
        "Riverton, Fairhaven",
        "About the job",
        "We hire company alumni from many places and 4 company alums work here.",
    ])
    detail = shape.parse_job_detail(body, company=None, document_title=None)
    assert detail.get("proximity") is None, (
        "a sentence in the job description was read as a proximity fact: %r"
        % (detail.get("proximity"),)
    )
    assert detail.get("description"), (
        "the description came back empty, so the assertion above passed for "
        "the wrong reason -- the body was never parsed at all"
    )
