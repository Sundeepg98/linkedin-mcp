"""The search-appearances reader, and what it refuses to say.

**THE FIXTURE UNDER THIS FILE IS SYNTHETIC AND THAT CHANGES WHAT THESE TESTS
CAN CLAIM.** Every other fixture-driven module here runs over a page LinkedIn
served. ``tests/fixtures/search_appearances_synthetic.html`` is a page nobody
in this repository has opened; it was hand-built to carry the leak shapes a
reader of this surface would have to refuse.

So these tests prove ONE DIRECTION: given a page containing companies,
titles and a linked member, the reader publishes none of them. They prove
NOTHING about whether the reader reads the real surface -- not the panel
layout, not the metric labels, not whether the real page links searchers at
all. The live capture replaces the fixture; it does not join it.

WHY THAT DISTINCTION IS WORTH A PARAGRAPH. This repository's most expensive
recurring defect is an instrument that returns nothing because it cannot see
the thing, read as a negative result. A refusal test over an invented page is
in exactly that family if it is quoted as evidence about the real one, so it
is labelled here rather than in a commit message somebody will not read.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape

#: **IN ``fixtures/synthetic/``, NOT IN ``fixtures/``, AND THE DIRECTORY IS
#: THE POINT RATHER THAN TIDYING.** Everything directly under ``fixtures/`` is
#: a page LinkedIn served, and ``tests/test_surface_census.py`` treats that
#: directory as a CORPUS: it globs ``fixtures/*.html`` non-recursively and
#: pins measurements over the whole of it -- ``FIXTURE_CONTROLS = 553``, a
#: per-file movement inventory, "29 of the 553 carry a non-null checked".
#:
#: Dropping this file in beside the captures took that denominator to 557 and
#: made every one of those numbers a measurement over twenty real pages PLUS
#: ONE INVENTION, with nothing in the corpus to say which was which. The
#: numbers would still have been arithmetically right and would have stopped
#: meaning what their own comments say they mean.
#:
#: So the subdirectory keeps the capture corpus pure and every other wave's
#: pins untouched. The cost is real and is stated rather than glossed: this
#: fixture is NOT swept by the census guards, so its invented names get no
#: free proof that the shaping pipeline would redact them. The tests in this
#: module assert that directly instead.
FIXTURE = (
    Path(__file__).parent / "fixtures" / "synthetic" /
    "search_appearances_synthetic.html"
)

#: Every string in the fixture that names a third party. NONE of these may
#: appear anywhere in the reader's output, at any depth, under any key.
THIRD_PARTY_STRINGS = (
    "Northgate Analytics",
    "Hillcrest",
    "Talent Acquisition Lead",
    "Priya Sharma",
    "priya-sharma-8a41b207",
    "Recruiting at Northgate Analytics",
    # THE ONE NEITHER REDACTION RULE CAN CATCH: one capitalised word, seen
    # once, in a row with no anchor. Only the in-page withholding stops it,
    # which is what makes that rule provable on its own.
    "Rivermouth",
)

#: The two labels the page's own furniture carries. These are what the reader
#: EXISTS to return, so a build that redacted them too would be a reader that
#: cannot report -- the same defect as one that returns zero because it cannot
#: see. Asserted positively for that reason.
HEADLINE_LABEL = "Search appearances"
DELTA_LABEL = "vs. prior week"


def _walk(value):
    """Every string anywhere in a nested result, flattened."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _walk(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk(item)


async def _read():
    """Run the REAL injected script over the frozen synthetic markup."""
    playwright = pytest.importorskip("playwright.async_api")
    html = FIXTURE.read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await dom.read_search_appearances(page)
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# 1. The fixture itself
# ---------------------------------------------------------------------------
#
# Without these the refusal tests below go vacuous: a fixture quietly emptied
# would make "no third party's name is in the output" true of nothing.


def test_the_fixture_carries_every_shape_the_reader_must_refuse():
    html = FIXTURE.read_text(encoding="utf-8")
    for name in THIRD_PARTY_STRINGS:
        assert name in html, name
    assert 'href="/in/priya-sharma-8a41b207/"' in html
    assert "/company/northgate-analytics/" in html


def test_the_fixture_says_it_is_synthetic():
    """A capture and an invention must never be told apart by guesswork."""
    html = FIXTURE.read_text(encoding="utf-8")
    assert "SYNTHETIC" in html
    assert "NOT A CAPTURE" in html


def test_the_fixture_carries_no_session_material():
    html = FIXTURE.read_text(encoding="utf-8")
    for token in ("li_at", "JSESSIONID", "csrfToken", "urn:li:member", "Bearer "):
        assert token not in html, token


# ---------------------------------------------------------------------------
# 2. The label pipeline, with no browser
# ---------------------------------------------------------------------------
#
# _search_appearance_labels is pure, so the aggregation rule can be tested
# without Playwright. These are the cases the guards exist for.


def test_a_singleton_two_capital_word_label_is_redacted():
    """The rule census_redact_rare implements, exercised on this reader."""
    out = dom._search_appearance_labels(
        [{"label": "Northgate Analytics", "entity_linked": "no"}]
    )
    assert out == [shape.CENSUS_REDACTED]


def test_the_pages_own_furniture_survives_the_same_pipeline():
    """The control. A redactor that blanks everything certifies nothing."""
    out = dom._search_appearance_labels(
        [
            {"label": HEADLINE_LABEL, "entity_linked": "no"},
            {"label": DELTA_LABEL, "entity_linked": "no"},
        ]
    )
    assert out == [HEADLINE_LABEL, DELTA_LABEL]


def test_an_entity_linked_label_is_refused_whatever_it_says():
    """The structural rule, which does not depend on the string or the tally.

    ``Hillcrest`` is ONE capitalised word appearing once, so
    ``census_redact_rare`` cannot touch it -- its own docstring says the run
    length is two. This is the case that proves the entity rule is doing work
    the count rule cannot.
    """
    out = dom._search_appearance_labels(
        [{"label": "Hillcrest", "entity_linked": "yes"}]
    )
    assert out == [shape.CENSUS_REDACTED]


def test_an_unwalked_row_is_treated_as_linked_and_not_as_unlinked():
    """A budget that ran out is not a finding that there was nothing there."""
    out = dom._search_appearance_labels(
        [{"label": "Hillcrest", "entity_linked": "unwalked"}]
    )
    assert out == [shape.CENSUS_REDACTED]


def test_a_withheld_label_stays_none_rather_than_becoming_a_string():
    out = dom._search_appearance_labels([{"label": None, "entity_linked": "no"}])
    assert out == [None]


def test_the_tally_is_over_this_pages_labels_and_not_a_global():
    """A shape seen twice on one page is not a singleton, and that is the rule.

    Recorded as a KNOWN LIMIT rather than as a feature: this is the exact
    escape ``census_href_identifies_entity`` was added for, and it is open
    here too whenever a label repeats and its row carries no entity link.
    """
    out = dom._search_appearance_labels(
        [
            {"label": "Northgate Analytics", "entity_linked": "no"},
            {"label": "Northgate Analytics", "entity_linked": "no"},
        ]
    )
    assert out == ["Northgate Analytics", "Northgate Analytics"]


# ---------------------------------------------------------------------------
# 3. The reader, over the frozen markup
# ---------------------------------------------------------------------------


async def test_no_third_party_string_reaches_the_output():
    """The whole privacy property, asserted over every string at every depth."""
    result = await _read()
    blob = "\n".join(_walk(result))
    for name in THIRD_PARTY_STRINGS:
        assert name not in blob, (name, blob)


async def test_the_headline_and_delta_are_readable():
    """The control for the test above. A reader that says nothing is not safe.

    If this fails while the refusal test passes, the reader has stopped being
    an instrument and become a blank -- which is the failure this repository
    keeps mistaking for a negative result.
    """
    result = await _read()
    assert result["headline"] == {
        "value": "18",
        "label_shape": HEADLINE_LABEL,
        "label_withheld": False,
        "entity_linked": "no",
    }
    assert result["delta"]["value"] == "12%"
    assert result["delta"]["label_shape"] == DELTA_LABEL


async def test_every_breakdown_pair_has_its_label_withheld_in_the_page():
    """Past the first two, the label never crosses the boundary at all."""
    result = await _read()
    beyond = result["metrics"][dom.SEARCH_APPEARANCES_LABELLED_PAIRS :]
    assert beyond, "the fixture no longer has breakdown rows -- it regressed"
    for row in beyond:
        assert row["label_withheld"] is True, row
        assert row["label_shape"] is None, row
    assert result["observed"]["pairs_withheld"] == len(beyond)


async def test_the_person_anchor_count_is_non_zero_on_a_page_with_a_member():
    """The measurement this whole surface was opened for.

    A non-zero count means the page draws links to individual members, so
    whatever LinkedIn records about a search IDENTIFIES the people in it. A
    zero would mean this page draws none -- which is NOT the same as a search
    emitting nothing, and the reader's docstring says so.
    """
    result = await _read()
    assert result["anchors"]["person"] >= 1
    assert result["anchors"]["company"] >= 2
    assert result["anchors"]["total"] >= result["anchors"]["person"]


async def test_the_breakdown_rows_are_seen_as_entity_linked():
    """The walk stops short of the root, so a row inside a link answers yes."""
    result = await _read()
    linked = [
        row for row in result["metrics"] if row["entity_linked"] == "yes"
    ]
    assert len(linked) >= 3, result["metrics"]


async def test_observed_distinguishes_absent_from_zero():
    """A page that rendered nothing must not look like a page with no data."""
    result = await _read()
    observed = result["observed"]
    assert observed["paragraphs_seen"] > 0
    assert observed["pairs_seen"] == len(result["metrics"])
    assert observed["main_present"] is True
    assert observed["main_chars"] > 0
    assert "search-appearance-searcher" in observed["view_name_counts"]


async def test_an_empty_page_reports_none_rather_than_zero():
    """Absent is not zero, on the only surface where the difference decides.

    A headline of ``0`` would read as "he appeared in no searches". ``None``
    reads as "no metric was found", which is what an empty render is.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(
                "<html><body><main></main></body></html>",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            result = await dom.read_search_appearances(page)
        finally:
            await browser.close()
    assert result["headline"] is None
    assert result["delta"] is None
    assert result["metrics"] == []
    assert result["anchors"]["person"] == 0
    assert result["observed"]["main_present"] is True
    assert result["observed"]["paragraphs_seen"] == 0


# ---------------------------------------------------------------------------
# 4. The boundary
# ---------------------------------------------------------------------------


def test_the_address_this_reader_names_is_the_one_the_boundary_admits():
    from linkedin_server import readonly

    assert readonly.is_read_url(dom.SEARCH_APPEARANCES_URL)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.linkedin.com/analytics/",
        "https://www.linkedin.com/analytics/creator/",
        "https://www.linkedin.com/analytics/search-appearances/detail/",
        "https://www.linkedin.com/analytics/search-appearances/?keywords=x",
        "https://www.linkedin.com/in/someone-else/search-appearances/",
        "https://www.linkedin.com/me/search-appearances/",
        "https://www.linkedin.com/search/results/people/?keywords=x",
    ],
)
def test_the_neighbours_of_that_address_are_still_refused(url):
    """One address was admitted, not a tree and not the surface next door.

    The last case is the point of the whole exercise: this reading exists to
    inform a ruling on people search, and admitting the page under
    consideration would be using one load of it as the evidence that
    authorises it.
    """
    from linkedin_server import readonly

    assert not readonly.is_read_url(url), url


@pytest.mark.parametrize(
    "suffix", ["\n", "\r", " ", "\t", "\n/in/someone-else/"]
)
def test_a_whitespace_spelling_of_the_address_is_refused(suffix):
    """The trailing-newline class, and THE ANCHOR IS NOT WHAT REFUSES IT.

    Handed to this wave by ``groups-events``, whose own boundary additions
    carry these spellings as controls: in Python ``$`` matches at the end of
    the string OR just before a trailing newline, so an anchored pattern is
    not by itself a defence against ``.../search-appearances/\\n``.

    MEASURED, AND THE MECHANISM IS NOT THE ONE THE CONTROL SUGGESTS. The bare
    regex DOES admit it -- ``pattern.match(url + "\\n")`` is True. What refuses
    it is a whole-string whitespace guard at the TOP of
    ``readonly.assert_read_url``, before any pattern is consulted::

        if any(character.isspace() for character in url):
            raise WriteAttemptError(...)

    So this test passes for a reason other than the one it looks like it is
    testing, and that is worth writing down rather than enjoying: **it
    certifies the upstream guard, not this entry's anchoring.** Every
    ``$``-anchored pattern in that file rests on the same line -- this wave's,
    the groups and events roots, and the twenty-odd that predate all of them.
    If that guard is ever removed or narrowed, they all admit a trailing
    newline together, and this test would go red along with its siblings,
    which is the behaviour to want.
    """
    from linkedin_server import readonly

    url = "https://www.linkedin.com/analytics/search-appearances/" + suffix
    assert not readonly.is_read_url(url), repr(url)
