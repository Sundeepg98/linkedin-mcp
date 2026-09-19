"""The employer's numeric Page id, resolved off a posting and refused otherwise.

WHY THIS SURFACE GETS ITS OWN MODULE. ``linkedin_follow_company`` acts from a
JOB POSTING, which names its employer by SLUG. ``linkedin_unfollow_company``
acts on a NUMERIC company id. Both docstrings say, at length, that nothing in
this server resolves one to the other and that the pair therefore cannot be
round-tripped here. ``shape.company_id_from_insight_cards`` is the resolution,
and it reads the id off a link that is already on the page
``linkedin_job_detail`` loads -- so what is being tested is not a new surface
but an attribution: WHICH organisation the number on that link belongs to.

THE HAZARD IS ATTRIBUTION, NOT EXTRACTION, and every assertion below is
shaped by it. The href carries TWO organisations::

    ?origin=JOB_PAGE_CANNED_SEARCH&currentCompany=<employer>&pastCompany=<other>

Getting a number out is trivial. Getting the WRONG one out is silent, and it
ends at a confirm gate that would offer to unfollow, or a search that would
filter by, an organisation the posting never advertised. Matching nothing is
a safe failure here; matching the wrong company is not a failure at all from
the code's point of view.

WHAT THIS MODULE ALREADY CAUGHT, which is why the prefix assertion exists as
a PAIR rather than as one test. The first draft of the name check asked "does
this card mention the employer". LinkedIn's own sentence is "<Employer> hired
6 people from <Other>", so that question is ALSO true of ``pastCompany``'s
organisation -- and the resolver duly returned ``currentCompany``'s id when
asked about the wrong company, against the real tracked fixture, on the first
run. The check is now a PREFIX: the card must OPEN by naming the employer,
which is a position LinkedIn chose and not one this repository invented.
``test_the_other_company_named_on_the_same_card_resolves_to_nothing`` is that
red, kept.

WHAT IS PINNED AND WHAT IS MEASURED. Exactly TWO literals are written down --
the employer's name and the canned-search HREF -- and everything else is
derived: ``EMPLOYER_ID`` is parsed back out of that href, and
``test_the_pinned_href_is_the_fixtures_own`` holds the href itself to the
tracked capture, so a regenerated fixture fails here rather than leaving a
stale expectation passing quietly. Both ids inside the href are INVENTED (see
``scripts/_build_follow_fixtures.py``, whose substitution tables are paired by
index against a gitignored key) and are declared in
``tests/test_no_committed_identity.py``. The href is a literal rather than an
f-string for a reason that is itself a finding -- see the note on ``HREF``.

THE HOP COUNT IS A MEASUREMENT AND IS PINNED AS ONE. ``harvest_linked_cards``
defaults to eight ancestors and eight is the wrong depth on this panel. The
five-depth reading is in ``_audit/_scratch/_probe_canned_search_harvest.py``
and is quoted on ``shape.COMPANY_ID_CARD_HOPS``; the module below re-runs the
THREE depths that carry the argument -- two, three and eight -- and asserts
what each returns, so the constant is backed by a reading this suite takes
itself rather than by a sentence about one somebody took once.
"""

from __future__ import annotations

import asyncio
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The one tracked capture that carries the Premium company-insights panel.
#: The other four job fixtures are the negative controls, and they are real
#: pages that simply do not draw it rather than fixtures built to be empty.
WITH_PANEL = "job_detail_following_hydrated.html"
WITHOUT_PANEL = (
    "job_detail.html",
    "job_detail_hydrated.html",
    "job_detail_following.html",
    "job_detail_shell.html",
)

#: Invented, and declared in tests/test_no_committed_identity.py. The employer
#: name is the sanitiser's substitution for this capture's real employer.
EMPLOYER = "Vantrex Systems"

#: The OTHER organisation the same sentence names. It is the whole reason the
#: name check is a prefix, so it is a named constant rather than a literal.
OTHER_COMPANY = "Fernhollow Technology"

#: LinkedIn's sentence, as the 3-hop harvest returns it. Written down because
#: the pure-function tests need a card and building one by hand from the
#: measured text is honest; the DOM tests below assert the fixture really
#: produces it.
CARD_TEXT = f"{EMPLOYER} hired 6 people from {OTHER_COMPANY}. See all"

#: THE HREF IS SPELLED OUT, AND THE SPELLING IS THE POINT.
#:
#: An earlier draft of this module built this string from
#: ``f"...currentCompany={EMPLOYER_ID}..."`` -- correct, readable, and INVISIBLE
#: to ``tests/test_no_committed_identity.py``, whose ``COMPANY_ID_SHAPE`` is
#: ``(?:/company/|currentCompany=|companyId=)(\d{3,})`` and therefore needs the
#: parameter name and the digits ADJACENT in the source text. Interpolating the
#: id split them, so the guard swept this file and found nothing to check --
#: a green that meant "nothing matched", not "the values are declared".
#:
#: So the url is a literal, every id in this module is written where the guard
#: can see it, and ``EMPLOYER_ID`` below is PARSED BACK OUT rather than written
#: twice. ``test_the_pinned_href_is_the_fixtures_own`` then holds the literal
#: to the tracked capture, so a regenerated fixture cannot leave it stale.
HREF = (
    "https://www.linkedin.com/search/results/people/"
    "?origin=JOB_PAGE_CANNED_SEARCH&currentCompany=610427&pastCompany=26105338"
)

EMPLOYER_ID = parse_qs(urlsplit(HREF).query)["currentCompany"][0]


def card(text: str = CARD_TEXT, href: str = HREF) -> list[dict[str, str]]:
    return [{"href": href, "text": text}]


# ---------------------------------------------------------------------------
# The DOM half: what the page actually carries, read with a local Chromium
# ---------------------------------------------------------------------------


async def _harvest(html: str, hops: int) -> list[dict]:
    """Harvest the people-search links off frozen markup.

    A LOCAL headless Chromium over a committed fixture. It reaches no network
    and no account, and it does not use the persistent Chrome profile, so it
    does not contend for the lock the running MCP server holds. The precedent
    and the reason are ``tests/test_profile_views_fixture.py``'s: the thing
    under test is a DOM walk, and a fake page cannot walk a DOM.
    """
    from playwright import async_api as playwright

    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await dom.harvest_linked_cards(
                page,
                href_pattern=shape.COMPANY_ID_LINK_MARKER,
                max_items=8,
                max_hops=hops,
            )
        finally:
            await browser.close()


@lru_cache(maxsize=None)
def harvest(name: str, hops: int) -> tuple[dict, ...]:
    """One Chromium launch per (fixture, depth), not per assertion.

    MEMOISED BECAUSE THE INPUT IS FROZEN. The fixtures are tracked files and
    the harvest is a pure read of one, so a second call cannot return anything
    a first did not -- there is no assertion here that a fresh launch could
    make true or false. Without this the module launches twelve browsers to
    ask seven questions, which on a loaded box is the difference between a
    slow test and a flaky one, and this repository runs several suites at
    once.

    Returns a TUPLE so the cache cannot hand two tests the same mutable list.
    """
    html = (FIXTURE_DIR / name).read_text(encoding="ascii")
    return tuple(asyncio.run(_harvest(html, hops)))


def test_the_posting_carries_exactly_one_canned_people_search():
    """One link, not "the first of several". The count is the safety case."""
    records = harvest(WITH_PANEL, shape.COMPANY_ID_CARD_HOPS)
    assert len(records) == 1
    assert shape.COMPANY_ID_QUERY_KEY in records[0]["href"]
    assert shape.COMPANY_ID_DECOY_QUERY_KEY in records[0]["href"]


def test_the_pinned_href_is_the_fixtures_own():
    """The literal above is the capture's, not a memory of it.

    ``HREF`` is spelled out so the identity guard can see the ids inside it.
    That is a good reason to write a value down and a bad reason to trust it,
    so the value is held to the fixture here: regenerate the capture and this
    fails, rather than the module quietly asserting against a url LinkedIn
    stopped drawing.
    """
    assert harvest(WITH_PANEL, shape.COMPANY_ID_CARD_HOPS)[0]["href"] == HREF


@pytest.mark.parametrize("name", WITHOUT_PANEL)
def test_the_other_four_job_captures_carry_no_such_link(name):
    """Four real postings that draw no panel -- the negative is not built.

    A fixture constructed to be empty proves that an empty page reads as
    empty. These are captures of the same surface that simply did not render
    the Premium panel, which is the case production will meet.
    """
    assert harvest(name, shape.COMPANY_ID_CARD_HOPS) == ()


def test_the_hop_count_is_the_measurement_it_claims_to_be():
    """Three depths, three different readings, and only one is a card.

    This is the assertion that keeps ``COMPANY_ID_CARD_HOPS`` honest. If a
    future ``harvest_linked_cards`` changes how it climbs, this fails here --
    where the reason is written down -- rather than silently widening the text
    the name check runs over.
    """
    shallow = harvest(WITH_PANEL, 2)[0]["text"]
    pinned = harvest(WITH_PANEL, shape.COMPANY_ID_CARD_HOPS)[0]["text"]
    deep = harvest(WITH_PANEL, 8)[0]["text"]

    assert shallow.strip() == "See all", "two hops is the link, not a card"
    assert pinned.startswith(EMPLOYER), "three hops is LinkedIn's sentence"
    assert OTHER_COMPANY in pinned, "and that sentence names both companies"
    assert not deep.startswith(EMPLOYER), "eight hops is the whole panel"
    assert len(deep) > 10 * len(pinned), "and it is very much bigger"


def test_end_to_end_the_fixture_resolves_to_the_employers_id():
    """The whole path, harvest to id, over tracked markup."""
    records = harvest(WITH_PANEL, shape.COMPANY_ID_CARD_HOPS)
    out = shape.company_id_from_insight_cards(records, company=EMPLOYER)
    assert out["state"] == "resolved"
    assert out["company_id"] == EMPLOYER_ID


def test_at_eight_hops_the_same_page_resolves_to_nothing():
    """The default depth is the wrong depth, and it fails CLOSED.

    Paired with the test above rather than stated in a comment: the harvest
    that absorbs the whole panel does not return somebody else's id, it
    returns none at all.
    """
    records = harvest(WITH_PANEL, 8)
    out = shape.company_id_from_insight_cards(records, company=EMPLOYER)
    assert out["state"] == "unnamed"
    assert out["company_id"] is None


# ---------------------------------------------------------------------------
# The attribution half: pure functions, no browser
# ---------------------------------------------------------------------------


def test_the_other_company_named_on_the_same_card_resolves_to_nothing():
    """THE RED THIS FUNCTION WAS REWRITTEN FOR. Kept, because it passed once.

    Asked about ``pastCompany``'s organisation, a substring name check
    returned ``currentCompany``'s id -- a real capture, a real sentence, and
    an answer that names the wrong company with full confidence.
    """
    out = shape.company_id_from_insight_cards(card(), company=OTHER_COMPANY)
    assert out["state"] == "unnamed"
    assert out["company_id"] is None
    assert OTHER_COMPANY in out["why"]


def test_a_href_carrying_only_the_decoy_key_yields_nothing():
    """``pastCompany`` alone is not a fallback. It is a different company."""
    href = (
        "https://www.linkedin.com/search/results/people/"
        "?pastCompany=26105338"
    )
    assert shape.COMPANY_ID_DECOY_QUERY_KEY in href
    out = shape.company_id_from_insight_cards(
        card(href=href), company=EMPLOYER
    )
    assert out["state"] == "absent"
    assert out["company_id"] is None
    assert shape.COMPANY_ID_DECOY_QUERY_KEY in out["why"]


def test_two_different_values_refuse_rather_than_taking_the_first():
    """Ambiguity is an answer. The Competitors block sits below this panel."""
    second = {
        # Spelled out, not interpolated -- see the note on HREF above. The id
        # is the next member of the 530000xx series already declared in
        # tests/test_no_committed_identity.py.
        "href": (
            "https://www.linkedin.com/search/results/people/"
            "?currentCompany=53000017"
        ),
        "text": f"{EMPLOYER} and one more thing",
    }
    out = shape.company_id_from_insight_cards(card() + [second], company=EMPLOYER)
    assert out["state"] == "ambiguous"
    assert out["company_id"] is None
    assert out["candidates"] == 2


def test_the_same_value_twice_is_not_ambiguous():
    """Two links to one organisation is one answer, not a refusal.

    The gate counts DISTINCT values, and this is the test that says so --
    without it, a page that drew the same canned search twice would refuse
    for a reason that would read as "LinkedIn named two companies".
    """
    out = shape.company_id_from_insight_cards(card() + card(), company=EMPLOYER)
    assert out["state"] == "resolved"
    assert out["company_id"] == EMPLOYER_ID
    assert out["candidates"] == 1


def test_an_unnamed_employer_refuses_rather_than_trusting_the_id():
    """An unhydrated posting names nobody, so there is nothing to agree with."""
    out = shape.company_id_from_insight_cards(card(), company=None)
    assert out["state"] == "unnamed"
    assert out["company_id"] is None


def test_a_value_that_is_not_an_organisation_id_refuses():
    href = (
        "https://www.linkedin.com/search/results/people/"
        "?currentCompany=7"
    )
    out = shape.company_id_from_insight_cards(card(href=href), company=EMPLOYER)
    assert out["state"] == "malformed"
    assert out["company_id"] is None


def test_an_entity_encoded_href_fails_closed_and_says_so():
    """Documented behaviour, asserted rather than described.

    An href copied out of raw markup still spells its separators ``&amp;``,
    and a real query parse then reads the second parameter's name as
    ``amp;currentCompany``. That must resolve to ABSENT -- never to a wrong
    id -- and it is left failing that way rather than normalised behind a
    defensive unescape.
    """
    href = (
        "https://www.linkedin.com/search/results/people/"
        "?origin=JOB_PAGE_CANNED_SEARCH&amp;currentCompany=610427"
    )
    out = shape.company_id_from_insight_cards(card(href=href), company=EMPLOYER)
    assert out["state"] == "absent"
    assert out["company_id"] is None


def test_a_link_outside_the_people_search_family_is_not_read():
    """The marker is checked before the query, so an unrelated link is inert."""
    href = (
        "https://www.linkedin.com/jobs/search/"
        "?currentCompany=610427"
    )
    out = shape.company_id_from_insight_cards(card(href=href), company=EMPLOYER)
    assert out["state"] == "absent"
    assert out["company_id"] is None


def test_nothing_at_all_is_absent_and_says_how_many_links_it_saw():
    """A bare null has cost this repository two wrong diagnoses before."""
    out = shape.company_id_from_insight_cards([], company=EMPLOYER)
    assert out["state"] == "absent"
    assert "0 people-search link(s) seen" in out["why"]
