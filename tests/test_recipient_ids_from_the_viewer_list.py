"""The member id was on screen the whole time and the harvest threw it away.

WHAT THIS UNBLOCKS. Addressing a message recipient by NAME is a measured dead
end -- three stable live census runs, and an offset instrument that found the
needle at eleven distinct positions across ten rows with accessible names 49 to
178 characters long. The replacement is addressing by IDENTIFIER, and the
identifier has to come from somewhere that costs no extra page load and opens
no third party's profile, which is permanently forbidden and would leave that
person a durable record.

**IT COMES FROM A PAGE THIS SERVER ALREADY OPENS.** `linkedin_who_viewed_me`
loads the analytics surface and harvests rows anchored on the PERSON link. Every
row that offers one also draws a Message button, and that button is an anchor
into the compose surface carrying the viewer's member id. The harvest is
anchored on the wrong link and discards it -- so the id was being thrown away
rather than being unavailable. Same class as the analytics aggregates: value on
a page already loaded, dropped on the floor.

## THE PAGE HAS THREE STATES, NOT TWO, AND THE FIXTURE PROVES IT

The obvious model is "named rows have an id, anonymous rows do not". The
captured page refutes it. Of FOUR named viewers, only TWO carry a Message
button; the others offer Connect or Follow, because LinkedIn draws the action
the RELATIONSHIP allows rather than the action the visibility allows.

    named + Message button    an id
    named + Connect/Follow    NO id -- a fact about the connection
    anonymous, no link        NO id -- a fact about visibility

So "no id" has two different causes and neither is "empty". A row without a
button does not appear in this reader's output at all, rather than appearing
with `recipient: ""` -- because an empty string and an absent button would then
be one value, and this package has already lost measurements to exactly that
collapse.

## THE VALUES ARE IDENTIFIERS AND THIS FILE TREATS THEM AS SUCH

A member id names a real person as surely as a name does. Nothing in the reader
logs one, and the tests below assert counts, slugs and shapes -- never an id's
value in an assertion message. The ids in the fixture are sanitised inventions
and are still not printed, because the habit is the protection.

## What these tests are and are not

They run the REAL injected script over the COMMITTED frozen markup, in a real
browser, on both renders. That proves the reader against the page as it was
captured. It proves nothing about the page as LinkedIn serves it today -- the
fixture is a freeze, and a freeze is a claim about a moment.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import dom

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURES = {
    "pre_hydration": FIXTURE_DIR / "profile_views_analytics.html",
    "hydrated": FIXTURE_DIR / "profile_views_analytics_hydrated.html",
}
BOTH = sorted(FIXTURES)

#: Named viewers on the frozen page who are MESSAGEABLE -- they carry a Message
#: button. Two of the four named viewers; the other two offer Connect and
#: Follow, which is the distinction this whole file exists to keep visible.
MESSAGEABLE = 2

#: Their slugs, which are invented and already public in the fixture. Slugs are
#: asserted; ids are not, and that asymmetry is deliberate.
MESSAGEABLE_SLUGS = {"priya-sharma-8a41b207", "rohan-desai-71f2e004"}

#: Named viewers who are NOT messageable. Their presence is what makes
#: "named" and "has an id" different questions.
NOT_MESSAGEABLE_SLUGS = {"arun-balakrishnan-4c19d833", "meera-iyer"}


async def _read(which: str):
    """Run the REAL injected script over one frozen page."""
    playwright = pytest.importorskip("playwright.async_api")
    html = FIXTURES[which].read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await dom.read_recipient_ids(page)
        finally:
            await browser.close()


# ---------------------------------------------------------------------------
# The fixture, before any browser -- so the browser tests cannot go vacuous
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("which", BOTH)
def test_the_fixture_still_draws_message_buttons(which):
    """A fixture regenerated without buttons would make every test below true
    of nothing at all."""
    html = FIXTURES[which].read_text(encoding="utf-8")
    assert html.count("/messaging/compose/?profileUrn=") == MESSAGEABLE, which
    # THE RAW MARKUP IS ENTITY-ESCAPED AND THE DOM IS NOT, which is why this
    # check cannot reuse the reader's own pattern. In the file the separator
    # is `&amp;`; `getAttribute("href")` hands the reader back `&`. The reader
    # matching `[?&]recipient=` is therefore correct AND this assertion would
    # read zero with it -- two right answers to two different questions, and
    # a fixture check that borrowed the reader's regex would have failed while
    # the reader worked.
    assert (
        len(re.findall(r"(?:\?|&amp;|&)recipient=", html)) == MESSAGEABLE
    ), which


@pytest.mark.parametrize("which", BOTH)
def test_the_fixture_has_named_viewers_who_cannot_be_messaged(which):
    """THE THREE-STATE CASE, pinned in the markup itself.

    If LinkedIn ever draws a Message button on every named row, this fails and
    the distinction below stops being testable -- which is worth knowing,
    because the reader's contract is built on it.
    """
    html = FIXTURES[which].read_text(encoding="utf-8")
    for slug in NOT_MESSAGEABLE_SLUGS:
        assert slug in html, slug
    assert "Invite " in html or "Follow " in html, which


# ---------------------------------------------------------------------------
# The reader, over the frozen markup, on BOTH renders
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.parametrize("which", BOTH)
async def test_it_finds_one_id_per_message_button(which):
    reading = await _read(which)
    assert reading["error"] is None, reading["error"]
    assert reading["buttons"] == MESSAGEABLE, reading["buttons"]
    assert len(reading["rows"]) == MESSAGEABLE, len(reading["rows"])


@pytest.mark.asyncio
@pytest.mark.parametrize("which", BOTH)
async def test_every_id_is_attributed_to_the_right_person(which):
    """THE JOIN IS THE POINT. An id nobody can attribute is worse than none.

    The reader climbs from the Message button to the row and reads the person
    link there. Asserting the SLUGS -- not the ids -- is what proves the climb
    landed in the right row rather than merely landing somewhere.
    """
    reading = await _read(which)
    assert {row["slug"] for row in reading["rows"]} == MESSAGEABLE_SLUGS, reading[
        "rows"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("which", BOTH)
async def test_a_named_viewer_without_a_button_is_absent_not_empty(which):
    """ABSENT AND EMPTY ARE DIFFERENT, and this is where they diverge.

    Two named viewers offer Connect and Follow instead of Message. They do NOT
    appear here with an empty id -- they do not appear at all, so a caller
    joining by slug finds nothing and knows it found nothing. An empty string
    would have made "not messageable" and "id unreadable" the same value.
    """
    reading = await _read(which)
    slugs = {row["slug"] for row in reading["rows"]}
    for slug in NOT_MESSAGEABLE_SLUGS:
        assert slug not in slugs, slug
    assert not [row for row in reading["rows"] if not row["recipient"]], reading[
        "rows"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("which", BOTH)
async def test_the_id_matches_the_shape_the_compose_route_admits(which):
    """THE READER FEEDS AN ADMITTED URL, so its output must fit that pattern.

    ``readonly`` admits the compose address with an id class of
    ``[A-Za-z0-9_-]{1,64}``. An id this reader returned that could not be put
    into that url would be a value nobody can use -- so the two are asserted
    against each other rather than each against its own idea of an id.
    """
    reading = await _read(which)
    for row in reading["rows"]:
        assert re.fullmatch(r"[A-Za-z0-9_-]{1,64}", row["recipient"]), row["slug"]


@pytest.mark.asyncio
@pytest.mark.parametrize("which", BOTH)
async def test_the_climb_stays_inside_the_row(which):
    """A WALK THAT GOES FAR ENOUGH TO LEAVE THE ROW FINDS THE WRONG PERSON.

    The hop count is reported so this is checkable rather than assumed: a
    climb that needed most of its budget is one page-structure change away
    from attributing a message button to its neighbour.
    """
    reading = await _read(which)
    for row in reading["rows"]:
        assert 0 < row["hops"] < dom.RECIPIENT_ROW_HOPS, row


# ---------------------------------------------------------------------------
# It is an identifier
# ---------------------------------------------------------------------------


def test_the_reader_never_logs_an_identifier():
    """THE CHEAPEST WAY NOT TO LOG ONE IS TO HAVE NOWHERE THAT DOES.

    Asserted on the source rather than described in prose, because a docstring
    promising restraint is the exact class of claim this repository converts
    into checks. Comment lines are stripped first so prose ABOUT logging does
    not read as logging.
    """
    import inspect

    source = inspect.getsource(dom.read_recipient_ids)
    code = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    for sink in ("logger.", "print(", "logging."):
        assert sink not in code, sink


def test_no_identifier_appears_in_this_files_own_assertions():
    """AND THE TEST FILE HOLDS ITSELF TO THE SAME RULE.

    Slugs are asserted because they are already in the committed fixture and
    are how the join is proved. IDS ARE NEVER WRITTEN DOWN HERE -- not as an
    expected value, not in a failure message. A test that pinned an id would
    put an identifier in a tracked file to prove the reader handles
    identifiers carefully.
    """
    source = Path(__file__).read_text(encoding="utf-8")
    # BUILT FROM PARTS, because the first version of this line WAS the literal
    # it was banning and failed on itself. A self-referential guard is not a
    # false positive to be exempted -- it is the guard telling you it cannot
    # name the thing it forbids and still forbid it.
    marker = "ACo" + "AA"
    assert marker not in source, "an id-shaped literal reached this file"
