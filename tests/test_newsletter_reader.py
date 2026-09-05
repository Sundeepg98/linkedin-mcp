"""The newsletter-subscription reader, run over real markup in a real page.

WHY THESE TESTS LOAD A BROWSER RATHER THAN FAKING ``page.evaluate``. The whole
risk on this surface is in the AIM, and a fake ``evaluate`` returning a canned
dict exercises the Python half while asserting nothing whatever about the
selector, the paragraph choice or the deduplication. This package has already
shipped one aim that resolved ZERO against the live DOM and would have read as
"he has no pending invitations" -- so a reader whose selector is never executed
is precisely the instrument this file exists to refuse.

``tests/fixtures/newsletter_subscriptions.html`` is SYNTHETIC in its content
and MEASURED in its structure. The measurement is on the live page of
2026-09-05 16:19 IST: ten anchors, five newsletters, every row drawn twice, an
illustration anchor with no paragraph at all and a text anchor with exactly
two, one ``h2`` carrying the product word immediately above them, and a second
``h2`` belonging to an advertisement below them.

**IT IS NOT A COPY OF THAT PAGE AND ONE ANCHOR IS THERE ON PURPOSE.** The
fixture draws ELEVEN anchors, because a mutation survived against ten: deleting
the deduplication changed nothing any assertion could see, since the
illustration anchors are dropped by the paragraph check before the dedup is
reached. A fixture that only mirrors the page leaves a live branch unexercised,
and a branch no input reaches is a branch the suite is not testing however many
times it runs.

THE FIVE ROWS EACH CARRY A JOB, and none of them is decoration:

    1  a person-shaped title       the redactor MUST fire
    2  a lower-case title          the redactor must NOT, and that is the
                                   declared floor rather than a bug
    3  an uncertifiable title      <opaque>, a refusal that keeps its marker
    4  the paragraphs SWAPPED      the aiming control must go False
    5  a member's newsletter tab   the foreign-marker branch must refuse
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import newsletters, shape

FIXTURE = Path(__file__).parent / "fixtures" / "newsletter_subscriptions.html"

#: What the fixture draws, MEASURED off the file by an independent parse below
#: rather than transcribed here -- the same discipline the connections fixture
#: keeps, and for the same reason: a number typed into a test is a number that
#: can disagree with the file it claims to describe.
EXPECTED_DISTINCT = 5

#: ELEVEN, NOT THE LIVE PAGE'S TEN, AND THE EXTRA ONE IS DELIBERATE. Row 2 is
#: drawn with a SECOND text anchor on the same href, because without it the
#: deduplication branch had no reaching input: the illustration anchors are
#: dropped by the paragraph check before the dedup is consulted, so deleting
#: the dedup entirely changed nothing any test could see. A fixture that only
#: mirrors the page leaves a live branch unexercised.
EXPECTED_ANCHORS = 11

#: The five illustration anchors -- one per row, no paragraph, no text at all.
#: They are what makes the anchor count wrong as an answer.
EXPECTED_WITHOUT_TEXT = 5


async def _open(html: str, factory):
    """Load markup into a real headless page and run ``factory`` over it."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1280, "height": 900})
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await factory(page)
        finally:
            await browser.close()


async def _read(html: str | None = None):
    if html is None:
        html = FIXTURE.read_text(encoding="utf-8")
    return await _open(html, newsletters.read_newsletter_subscriptions)


# ---------------------------------------------------------------------------
# The fixture describes itself, so the numbers below are not transcriptions
# ---------------------------------------------------------------------------


def _anchors_in_the_file() -> list[str]:
    """Every newsletter href in the fixture, by a DIFFERENT instrument.

    A regex over the source text rather than a DOM walk, so this is a
    cross-check and not the reader agreeing with itself.
    """
    source = FIXTURE.read_text(encoding="utf-8")
    return re.findall(r'href="(https://www\.linkedin\.com/[^"]*newsletters/[^"]*)"', source)


def test_the_fixture_draws_more_anchors_than_rows_which_is_why_distinct_exists():
    """MORE ANCHORS THAN NEWSLETTERS -- the fact the count rule turns on."""
    hrefs = _anchors_in_the_file()
    assert len(hrefs) == EXPECTED_ANCHORS
    assert len({href.rstrip("/") for href in hrefs}) == EXPECTED_DISTINCT


@pytest.mark.asyncio
async def test_it_publishes_distinct_newsletters_and_not_anchors():
    """THE ONE NUMBER THIS WHOLE SURFACE WAS OPENED TO SETTLE.

    A reader publishing the anchor count answers TEN to *how many newsletters
    does he subscribe to*, and looks entirely correct doing it. That is the
    failure this assertion exists for; it is not a tidiness check.
    """
    out = await _read()
    assert out["error"] is None
    assert out["anchors"] == EXPECTED_ANCHORS
    assert out["distinct"] == EXPECTED_DISTINCT
    assert out["anchors_without_text"] == EXPECTED_WITHOUT_TEXT
    assert len(out["rows"]) == EXPECTED_DISTINCT


@pytest.mark.asyncio
async def test_the_heading_control_reads_the_word_and_not_the_position():
    """The advertisement below the rows draws an h2 too."""
    out = await _read()
    assert out["heading_seen"] == 1


@pytest.mark.asyncio
async def test_no_row_publishes_a_title_as_written():
    """THE PROPERTY THE WHOLE SURFACE TURNS ON.

    Every published name is a marker, a redaction, or a lower-case string the
    declared floor lets through. What must never appear is a capitalised title
    verbatim -- and the person-shaped row is the one that proves it, because a
    person's name survives every identity substitution untouched.
    """
    out = await _read()
    published = [row for row in out["rows"] if row.get("published")]
    assert published, "nothing published -- the aim, not the assertion, is wrong"
    for row in published:
        name = str(row.get("name") or "")
        assert "Savita" not in name
        assert "Krishnan" not in name


@pytest.mark.asyncio
async def test_the_person_shaped_title_comes_back_redacted_with_its_shape_intact():
    """``<redacted> by <redacted>`` STILL SAYS THE THING IS AUTHORED.

    That is the measured difference from ``membership_row``, whose owner
    declined this same fix because every plausible group name is a capitalised
    run and unconditional redaction would blank the payload along with the
    leak. Here the shape survives, which is why redact-always is right on this
    function and wrong on that one.
    """
    out = await _read()
    names = [str(row.get("name") or "") for row in out["rows"] if row.get("published")]
    shaped = [name for name in names if shape.CENSUS_REDACTED in name]
    assert shaped, "the redactor never fired on any row"
    assert any(" by " in name for name in shaped), (
        "every redacted title collapsed to a bare marker -- the readable shape "
        "is the reason this gate is worth more than a count"
    )


@pytest.mark.asyncio
async def test_the_lower_case_title_survives_and_that_is_the_declared_floor():
    """A LIMIT ASSERTED IN THE SUITE, NOT CONFESSED IN A DOCSTRING.

    ``census_redact_rare`` is a CAPITALISED-RUN rule and not a name detector.
    A title spelling its author in lower case walks straight through it. If
    this test ever fails because the floor ROSE, re-measure and rewrite it --
    do not delete it, because it is the record of what this package cannot do.
    """
    out = await _read()
    names = [str(row.get("name") or "") for row in out["rows"] if row.get("published")]
    assert "data weekly" in names


@pytest.mark.asyncio
async def test_an_uncertifiable_title_is_opaque_rather_than_emitted():
    """A REFUSAL THAT KEEPS ITS OWN MARKER.

    Measured on the live page: with the aim reading the whole card rather than
    the first paragraph, all five real titles came back ``<opaque>`` -- which
    is how the aim was discovered to be wrong. A gate that dropped the field
    instead would have shown five blank rows and no reason.
    """
    out = await _read()
    names = [str(row.get("name") or "") for row in out["rows"] if row.get("published")]
    assert shape.CENSUS_OPAQUE in names


@pytest.mark.asyncio
async def test_a_members_own_newsletter_tab_is_refused_and_names_what_it_saw():
    """The foreign-marker branch, reached through the reader rather than by a
    direct call -- which is the only way to know the reader can reach it."""
    out = await _read()
    refused = [row for row in out["rows"] if not row.get("published")]
    assert len(refused) == 1
    assert refused[0]["refused"] == "href_identifies_another_kind_of_entity"
    assert refused[0]["saw"], "a refusal that reports only what it did NOT match"
    assert out["published"] == EXPECTED_DISTINCT - 1


# ---------------------------------------------------------------------------
# The aiming control
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_aiming_control_fires_on_the_row_whose_paragraphs_are_swapped():
    """THE ASSERTION THAT MAKES THE PARAGRAPH CHOICE A MEASUREMENT.

    The reader takes the FIRST paragraph as the title. Nothing in the markup
    says it is one -- the classes are hashed, the order is LinkedIn's, and a
    swap is invisible to any structural rule. The slug is an INDEPENDENT
    WITNESS: it is derived from the title, so a title that is not a prefix of
    it is not the title.

    Four rows must match and the swapped one must not. A run where all five
    matched would mean the control cannot fail.
    """
    out = await _read()
    matched = [row for row in out["rows"] if row.get("title_matches_slug") is True]
    missed = [row for row in out["rows"] if row.get("title_matches_slug") is not True]
    assert out["titles_matching_slug"] == len(matched)
    assert out["titles_unmatched"] == len(missed)

    # THE POPULATION IS THE PUBLISHED ROWS, and that scoping was forced by a
    # red rather than chosen. The member's-newsletter-tab row is unmatched too
    # -- its href ends in a placeholder, so there is no slug for a title to be
    # a prefix of -- and counting it here made a control designed to catch ONE
    # row report TWO. That row is REFUSED: its title is never published, so
    # whether the reader aimed at the right paragraph in it is not a question
    # anybody is relying on the answer to.
    published_missed = [
        row for row in out["rows"]
        if row.get("published") and row.get("title_matches_slug") is not True
    ]
    assert len(published_missed) == 1, (
        "the swapped row must be the only PUBLISHED row that fails -- if none "
        "fails the control is decorative, and if several fail the aim is wrong"
    )
    assert len(missed) == 2, (
        "the refused row is unmatched as well, and it is asserted rather than "
        "filtered out of sight: a number that quietly excludes a case is a "
        "number nobody can check"
    )


def test_the_control_separates_absent_from_false():
    """``None`` AND ``False`` ARE DIFFERENT ANSWERS AND STAY THAT WAY.

    Merging "the question could not be put" into "the answer is no" deletes
    the vocabulary needed to test for the bug. Both inputs below are real:
    a row with no title text, and a href with nothing after the last slash.
    """
    assert newsletters.title_matches_slug(
        "https://www.linkedin.com/newsletters/data-weekly-4822/", "data weekly"
    ) is True
    assert newsletters.title_matches_slug(
        "https://www.linkedin.com/newsletters/data-weekly-4822/", "something else"
    ) is False
    assert newsletters.title_matches_slug(
        "https://www.linkedin.com/newsletters/data-weekly-4822/", ""
    ) is None
    assert newsletters.title_matches_slug("", "data weekly") is None


def test_the_control_returns_a_bit_and_never_a_fragment_of_its_input():
    """A CONTROL COMPUTED FROM THE TWO MOST DANGEROUS STRINGS ON THE PAGE.

    Its whole safety argument is that the answer is one bit. If it ever
    returned a reason, a diff or a normalised form, it would be publishing a
    title through the back door of a boolean -- which is the shape of every
    leak this repository has recorded.
    """
    verdict = newsletters.title_matches_slug(
        "https://www.linkedin.com/newsletters/weekly-notes-by-savita-krishnan-4821/",
        "Weekly Notes by Savita Krishnan",
    )
    assert verdict in (True, False, None)
    assert isinstance(verdict, bool)


# ---------------------------------------------------------------------------
# A zero must say which kind of zero it is
# ---------------------------------------------------------------------------


_HEADING_NO_ROWS = """
<html><body><section><h2>Newsletters</h2>
<div class="rows"></div></section></body></html>
"""

_ROWS_NO_HEADING = """
<html><body><section>
<a href="https://www.linkedin.com/newsletters/data-weekly-4822/"><p>data weekly</p><p>x</p></a>
</section></body></html>
"""

_NEITHER = "<html><body><section><h2>Something else</h2></section></body></html>"


@pytest.mark.asyncio
async def test_zero_rows_with_the_heading_present_is_a_fact_about_his_account():
    out = await _read(_HEADING_NO_ROWS)
    assert out["heading_seen"] == 1
    assert out["distinct"] == 0
    assert out["anchors"] == 0


@pytest.mark.asyncio
async def test_zero_rows_with_no_heading_is_a_fact_about_the_instrument():
    """THE PAIR IS THE POINT, AND EITHER HALF ALONE IS UNINTERPRETABLE.

    Both cases below return zero rows. They mean opposite things, and a reader
    that reported the first when it measured the second would answer the whole
    blocker backwards -- confidently, and with a number.
    """
    out = await _read(_NEITHER)
    assert out["heading_seen"] == 0
    assert out["distinct"] == 0


@pytest.mark.asyncio
async def test_rows_without_the_heading_still_read_because_the_control_is_not_a_gate():
    """The control REPORTS; it does not refuse.

    A heading check that suppressed the rows would make a LinkedIn copy change
    look like an empty subscription list, which is the same failure one layer
    up. It is an annotation on a zero, never a condition on a read.
    """
    out = await _read(_ROWS_NO_HEADING)
    assert out["heading_seen"] == 0
    assert out["distinct"] == 1
    assert out["published"] == 1


@pytest.mark.asyncio
async def test_a_page_that_cannot_be_evaluated_reports_the_class_and_the_message():
    """A HANDLER THAT KEEPS THE CLASS AND DROPS THE MESSAGE IS A SCAR HERE.

    The diagnostic named its own cause and was nearly discarded, three times in
    one day. The error carries neither a title nor an href: the strings go INTO
    the page and nothing is interpolated back out.
    """

    class Exploding:
        async def evaluate(self, _script, _cfg=None):
            raise RuntimeError("frame was detached")

    out = await newsletters.read_newsletter_subscriptions(Exploding())
    assert out["error"] == "RuntimeError: frame was detached"
    assert out["rows"] == []
    assert out["distinct"] == 0
    assert out["heading_seen"] == 0
