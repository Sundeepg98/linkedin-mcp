"""The unfollow control, keyed to ONE company row, and the ways that goes wrong.

WHY THIS SURFACE GETS ITS OWN MODULE. Every other reader in this package
answers a question. This one picks the thing that gets CLICKED, on a write that
REMOVES something, so being wrong here is not a misreported fact -- it is an
unfollow performed on a company the operator never named. One asymmetry runs
through every assertion below: matching NOTHING is a safe failure, because the
write refuses on a count that is not exactly one. Matching the WRONG ROW is
not a failure at all from the code's point of view. It looks like success.

THE ANCHOR AND THE KEY ARE DIFFERENT THINGS, and that separation is what this
module pins. The button is FOUND by its accessible name -- ``Click to stop
following <Page>``, a label that states the inverse action outright and is the
strongest anchor in this package. The ROW is found by the company's numeric
id. Both must agree. The label alone is the weakest possible key: display
names collide, they change, and somebody else chooses them -- and, measured on
2026-08-24, LinkedIn renders the IDENTICAL label template over PEOPLE on
another surface, twenty member rows with no company link anywhere in them. A
selector anchored on the label alone matched all twenty. That case is built in
this module rather than captured, because this server cannot reach that
surface to capture it.

WHAT THIS MODULE ALREADY CAUGHT, which is why the safety case is a PAIR rather
than a test. Written first against the shipped selector, the twenty-row
fixture returned ``{'label': None, 'count': 0}`` for ALL TWENTY ids -- the
write path carried its own copy of the row predicate which had silently
dropped the company-link condition, so its scope resolved to the bare ``<div>``
wrapping the button, a scope holding zero links, and nothing ever matched.
The defect is repaired at the cause: there is now ONE predicate string and
both paths consume it, which
``test_the_read_and_write_paths_share_one_row_predicate`` pins. The other half
of the lesson lives in the pair below. Written FLAT, the safety case PASSED
against that broken selector. Written NESTED -- the way the real capture nests
it -- it did not. A control that cannot fail certifies nothing, and the flat
form was exactly that.

WHAT IS PINNED AND WHAT IS DERIVED. These fixtures are sanitised: every name
and id in them is invented, so they are safe to assert on verbatim. Even so
the id-to-name mapping is PARSED out of the fixture at runtime rather than
typed in, so a regenerated capture cannot leave a stale expectation quietly
passing. Exactly one id is written down -- ``902611`` -- because the near-miss
and safety cases need one specific row to be about.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import dom, writes
from linkedin_server.errors import ExtractionFailedError

FIXTURE_DIR = Path(__file__).parent / "fixtures"

FIXTURES = {
    # The same Manage Pages list before and after it settles. Everything below
    # runs on the settled one; the sparse one is here so the count assertions
    # are contrasted against a render that drew half as many rows.
    "pages": FIXTURE_DIR / "manage_pages_following.html",
    "pages_hydrated": FIXTURE_DIR / "manage_pages_following_hydrated.html",
}

#: Rows each render actually drew, and what LinkedIn's own heading says the
#: total is. These numbers ARE the hazard this module keeps naming: twenty of
#: fifty-eight is why an absent row proves nothing.
ROWS_RENDERED = {"pages": 10, "pages_hydrated": 20}
TOTAL_FOLLOWED_TEXT = "58 Pages"

#: Two hrefs per row -- a logo link and a name link, same id in both.
LINKS_PER_ROW = 2

#: The one id written down anywhere in this file. Taken from the sanitised
#: fixture, where it is invented. The near-miss and safety cases need a
#: specific row to be about; everything else is derived from the parse.
ANCHOR_ID = "902611"

#: An id of the right SHAPE that belongs to no row. Asserted absent before it
#: is used, so a regenerated fixture that happened to contain it cannot turn
#: that test into a test of nothing.
ABSENT_ID = "7777777"

#: The near-miss pair: a strict prefix of the anchor and a strict extension of
#: it. Both are valid ids by SHAPE, so the guard lets them through and the
#: SELECTOR has to be the thing that rejects them.
PREFIX_OF_ANCHOR = "90261"
EXTENSION_OF_ANCHOR = "9026110"


# ---------------------------------------------------------------------------
# The browser harness -- the pattern from test_follow_state_fixture.py
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await browser.close()


def markup(which: str) -> str:
    return FIXTURES[which].read_text(encoding="ascii")


# ---------------------------------------------------------------------------
# Parsing the fixture WITHOUT dom.py, so the expectation is independent
# ---------------------------------------------------------------------------

_BUTTON_LABEL = re.compile(r'aria-label="(Click to stop following [^"]*)"')
_COMPANY_HREF = re.compile(r'href="https://www\.linkedin\.com/company/(\d+)/"')


def _rows(which: str) -> list:
    """Every row of the fixture, split on its list items.

    Deliberately a dumb regex over ``<li`` chunks and NOT a call into
    ``dom.py``. The expectation this builds is what ``dom.py`` gets checked
    against, so deriving it with the code under test would make every
    assertion below a tautology -- the selector would be compared against
    itself and could never be caught disagreeing with the markup.
    """
    out = []
    for chunk in markup(which).split("<li"):
        labels = _BUTTON_LABEL.findall(chunk)
        if not labels:
            continue
        out.append({"labels": labels, "ids": _COMPANY_HREF.findall(chunk)})
    return out


def expected_names(which: str) -> dict:
    """id -> the label that actually belongs to that id, out of the markup."""
    rows = _rows(which)
    mapping = {}
    for row in rows:
        assert len(row["labels"]) == 1, f"row with {len(row['labels'])} buttons"
        ids = set(row["ids"])
        assert len(ids) == 1, f"row naming {len(ids)} companies: {sorted(ids)}"
        mapping[ids.pop()] = row["labels"][0]
    assert len(mapping) == len(rows), "two rows share one company id"
    return mapping


# ---------------------------------------------------------------------------
# 0. The fixture is the shape everything below assumes
# ---------------------------------------------------------------------------


def test_the_fixture_is_the_shape_every_assertion_below_assumes():
    """Pins the measured facts the rest of this module is built on.

    Delete this and a regenerated capture -- nineteen rows, a duplicated id, a
    row that lost its logo link -- silently degrades the tests below into
    weaker ones that still pass. The near-miss case in particular is only
    meaningful while the anchor id is genuinely present and the absent id
    genuinely absent, and both are checked here rather than assumed at their
    point of use.
    """
    for which, expected in ROWS_RENDERED.items():
        path = FIXTURES[which]
        assert path.exists(), f"missing fixture: {path}"
        raw = path.read_bytes()
        assert raw, f"empty fixture: {path}"
        raw.decode("ascii")

        rows = _rows(which)
        assert len(rows) == expected, f"{which}: {len(rows)} rows, not {expected}"
        for row in rows:
            assert len(row["labels"]) == 1
            assert len(row["ids"]) == LINKS_PER_ROW
            assert len(set(row["ids"])) == 1

        assert len(expected_names(which)) == expected, "ids are not distinct"

        # LinkedIn's own stated total, beside a render that drew a fraction of
        # it, and no control anywhere to fetch the rest. This is the whole
        # basis for the absence test refusing to read 0 as "not following".
        assert TOTAL_FOLLOWED_TEXT in markup(which)
        assert "artdeco-pagination" not in markup(which)

    settled = expected_names("pages_hydrated")
    assert ANCHOR_ID in settled, f"the anchor id {ANCHOR_ID} left the fixture"
    assert settled[ANCHOR_ID].startswith(writes.UNFOLLOW_ANCHOR_PREFIX)
    assert ABSENT_ID not in settled, f"{ABSENT_ID} is no longer absent"


# ---------------------------------------------------------------------------
# A. The guard, which is why a caller's string never reaches a click
# ---------------------------------------------------------------------------


BAD_IDS = [
    "",                   # nothing at all
    None,                 # the field was never populated
    "   ",                # whitespace, which strips to nothing
    "Gridwell",           # the display NAME -- the weakest possible key
    "gridwell-systems",   # the vanity SLUG, which a job posting hands you
    "902",                # numeric, but too short to be a company id
    "90'26]11",           # a quote and a bracket: the injection shape
    "902611 or 1=1",      # a predicate smuggled in behind a real id
]


@pytest.mark.parametrize("bad", BAD_IDS)
def test_the_selector_refuses_anything_that_is_not_a_numeric_page_id(bad):
    """The guard that stops a selector being assembled out of a caller's string.

    This is a string a CLICK is built from. Without the guard, ``Gridwell``
    builds a selector that matches whichever row happens to wear that name;
    the slug builds one that matches nothing in a way nobody can read; and the
    quote and bracket cases escape the quoting and widen the predicate into
    something the author never wrote. Delete this and the only thing standing
    between a caller's typo and an unfollow is that no caller has typed one
    yet.

    The MESSAGE is asserted, not just the exception type, because the caller
    who trips this is holding a slug or a name and needs telling WHICH key the
    surface takes -- an ExtractionFailedError with a vague message just sends
    them away guessing at the id.
    """
    with pytest.raises(ExtractionFailedError) as caught:
        dom.unfollow_control_selector(bad)

    message = str(caught.value)
    assert repr(bad) in message, message
    lowered = message.casefold()
    assert "numeric" in lowered, message
    assert "company id" in lowered, message


def test_the_guard_admits_a_real_id_so_it_is_not_merely_refusing_everything():
    """The positive control for the guard above.

    Without this, ``unfollow_control_selector`` could be a one-line ``raise``
    and every parametrised case above would still be green -- a guard that
    refuses EVERYTHING passes a suite that only ever checks refusals. So the
    admitted case is asserted here, and the id has to actually reach the
    selector rather than being dropped on the floor.
    """
    selector = dom.unfollow_control_selector(ANCHOR_ID)
    assert selector.startswith("xpath=")
    assert f"/company/{ANCHOR_ID}/" in selector
    assert writes.UNFOLLOW_ANCHOR_PREFIX in selector


@pytest.mark.asyncio
async def test_the_refusal_reaches_the_caller_instead_of_reading_as_absent():
    """MEASURED, not assumed: the raise propagates out of the READER too.

    ``read_unfollow_control`` builds its selector OUTSIDE its try block, so a
    bad id raises rather than being swallowed. That placement is the whole
    point, and it is asserted here because the alternative is silent and
    plausible: a swallowed refusal would return ``count: 0``, which on this
    surface is the perfectly ordinary "that row is not on the page" -- so a
    caller holding a SLUG would be told the company is absent from the list,
    rather than that it asked the wrong question. Delete this and a future
    broadened ``except`` turns a refusal into a fact.

    Exercised through ``read_unfollow_control`` specifically, rather than
    through the builder the tests above already cover, because propagation
    ACROSS THAT BOUNDARY is the property at issue.
    """

    async def work(page):
        for bad in ("gridwell-systems", "902", None):
            with pytest.raises(ExtractionFailedError):
                await dom.read_unfollow_control(page, bad)
        # The same reader, on the same page, answers a well-formed id instead
        # of raising for everything.
        assert await dom.read_unfollow_control(page, ANCHOR_ID) == {
            "label": None,
            "count": 0,
        }
        return True

    assert await _with_html("<html><body></body></html>", work)


# ---------------------------------------------------------------------------
# B. One row, and the RIGHT one
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_keyed_read_finds_exactly_one_row_and_the_right_one():
    """The core claim: an id selects its OWN row, not merely SOME row.

    Two assertions, and the second is the one that matters. ``count == 1``
    only says the selector was specific; it says nothing about WHICH row it
    landed on, and a selector that always returned the first button would
    satisfy it for every id. So the label is compared against the name that
    actually belongs to that id in the markup -- a mapping parsed here, from
    the fixture, so a regenerated capture cannot leave a stale expectation
    passing.

    Delete this and the unfollow is only known to click SOMETHING.
    """
    mapping = expected_names("pages_hydrated")
    # Five spread across the id-length range, DERIVED rather than typed, plus
    # the anchor. Derived so a fixture regeneration cannot strand them.
    sample = sorted(mapping, key=int)[::4]
    assert len(sample) >= 5, f"only {len(sample)} sampled ids"
    sample = sorted(set(sample) | {ANCHOR_ID}, key=int)

    async def work(page):
        seen = {}
        for company_id in sample:
            seen[company_id] = await dom.read_unfollow_control(page, company_id)
        return seen

    results = await _with_html(markup("pages_hydrated"), work)

    for company_id in sample:
        got = results[company_id]
        assert got["count"] == 1, f"{company_id}: count {got['count']}"
        assert got["label"] is not None, company_id
        assert got["label"].startswith(writes.UNFOLLOW_ANCHOR_PREFIX), got["label"]
        assert got["label"] == mapping[company_id], (
            f"{company_id} resolved to {got['label']!r}, but that id's own row "
            f"is {mapping[company_id]!r} -- the selector left its row"
        )


# ---------------------------------------------------------------------------
# C. Nothing found, and what that does NOT mean
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_company_absent_from_the_rendered_rows_reads_zero_not_unfollowed():
    """Count 0 means THE ROW IS NOT ON THIS PAGE. It does NOT mean unfollowed.

    That distinction is the reason this reader returns a count instead of a
    boolean. The fixture's own heading says the account follows fifty-eight
    Pages while the settled render draws TWENTY of them, and the capture
    carries no pagination control at all -- so roughly two thirds of the
    followed Pages are absent from any given render BY CONSTRUCTION, and every
    one of them reads exactly like this test's invented id.

    A caller that collapsed count 0 into "not following" would therefore
    report a confident, wrong "you do not follow them" across most of the
    list, and hand a confirm gate the wrong direction. Reconciling the count
    against LinkedIn's stated total is the CALLER's job
    (``shape.followed_page_state``); this reader does not pretend to do it.
    Delete this test and the absence of that pretence stops being checked.
    """
    assert ABSENT_ID not in expected_names("pages_hydrated")

    async def work(page):
        return (
            await dom.read_unfollow_control(page, ABSENT_ID),
            await dom.read_unfollow_control(page, ANCHOR_ID),
        )

    absent, present = await _with_html(markup("pages_hydrated"), work)

    assert absent == {"label": None, "count": 0}
    # The present case, off the same page, so this "count 0" cannot be coming
    # from a reader that returns 0 for everything.
    assert present["count"] == 1

    # The evidence for the paragraph above, asserted rather than described.
    assert TOTAL_FOLLOWED_TEXT in markup("pages_hydrated")
    assert len(_rows("pages_hydrated")) == ROWS_RENDERED["pages_hydrated"]


# ---------------------------------------------------------------------------
# D. The near miss
# ---------------------------------------------------------------------------


def test_no_fixture_id_is_a_substring_of_another():
    """Records WHY the near-miss case below is constructed rather than found.

    MEASURED 2026-08-24 over the settled fixture: not one of the twenty ids is
    a substring of any other, so the fixture contains no natural collision
    pair and the near miss has to be built from the anchor. This is ASSERTED
    rather than written in a comment so that a regenerated capture which DOES
    contain such a pair becomes visible right here -- at which point that pair
    is a stronger case than the constructed one and should be used instead.
    """
    ids = list(expected_names("pages_hydrated"))
    pairs = [(a, b) for a in ids for b in ids if a != b and a in b]
    assert not pairs, (
        f"the fixture now contains substring id pairs {pairs} -- use one as "
        "the near-miss case, it is stronger than the constructed one"
    )


@pytest.mark.asyncio
async def test_a_prefix_or_suffix_of_a_real_id_matches_no_row():
    """THE TRAILING SLASH, proved rather than commented.

    The selector matches on ``/company/<id>/`` -- with the closing slash --
    and this is what that slash is for. Drop it and ``contains()`` turns every
    id into a PREFIX MATCH: asking for ``90261`` would match ``902611``'s row,
    and the unfollow would land on a company whose id merely STARTS the way
    the caller's does. That is the worst failure available to this module,
    because it is silent, it returns count 1, and the label it reports back is
    a real company's real name -- just not the one that was asked for.

    Both directions are checked. The prefix is what a truncated id produces;
    the extension is what a concatenation or an off-by-one paste produces. The
    genuine id is read on the SAME page immediately afterwards, so a zero
    cannot be coming from a page that simply failed to load.
    """

    async def work(page):
        return {
            "prefix": await dom.read_unfollow_control(page, PREFIX_OF_ANCHOR),
            "extension": await dom.read_unfollow_control(page, EXTENSION_OF_ANCHOR),
            "exact": await dom.read_unfollow_control(page, ANCHOR_ID),
        }

    got = await _with_html(markup("pages_hydrated"), work)

    assert got["prefix"] == {"label": None, "count": 0}, got["prefix"]
    assert got["extension"] == {"label": None, "count": 0}, got["extension"]
    assert got["exact"]["count"] == 1
    assert got["exact"]["label"] == expected_names("pages_hydrated")[ANCHOR_ID]

    # The near miss is only a near miss while these really are neighbours in
    # string space; if the constants drift apart this stops testing anything.
    assert ANCHOR_ID.startswith(PREFIX_OF_ANCHOR)
    assert EXTENSION_OF_ANCHOR.startswith(ANCHOR_ID)


# ---------------------------------------------------------------------------
# E. THE SAFETY CASE, and its control -- written as a pair on purpose
# ---------------------------------------------------------------------------

#: Two rows wearing the IDENTICAL button label. One is a company row with a
#: ``/company/`` link; the other has no company link at all and carries a
#: member-shaped urn, which is how LinkedIn draws PEOPLE on a surface this
#: server cannot reach. Everything here is invented -- the urn is not a real
#: member id, and the company id is the sanitised fixture's.
#:
#: NESTED: the button sits inside its own wrapper ``<div>``, the way the real
#: capture nests it. This is the shape that DISCRIMINATES.
_MEMBER_ROW_NESTED = """<html><body><div id="list">
  <div class="row">
    <a href="https://www.linkedin.com/company/902611/">Gridwell</a>
    <div class="actions">
      <button id="row-with-company-link"
        aria-label="Click to stop following Gridwell">Following</button>
    </div>
  </div>
  <div class="row" data-urn="urn:li:member:INVENTED-FOR-THIS-TEST">
    <span>Gridwell</span>
    <div class="actions">
      <button id="row-with-no-company-link"
        aria-label="Click to stop following Gridwell">Following</button>
    </div>
  </div>
</div></body></html>"""

#: FLAT: the same two rows, but with the button as a direct sibling of the
#: link. Retained as a CONTROL rather than as coverage -- see its test.
_MEMBER_ROW_FLAT = """<html><body><div id="list">
  <div class="row">
    <a href="https://www.linkedin.com/company/902611/">Gridwell</a>
    <button id="row-with-company-link"
      aria-label="Click to stop following Gridwell">Following</button>
  </div>
  <div class="row" data-urn="urn:li:member:INVENTED-FOR-THIS-TEST">
    <span>Gridwell</span>
    <button id="row-with-no-company-link"
      aria-label="Click to stop following Gridwell">Following</button>
  </div>
</div></body></html>"""


async def _match_on(html: str) -> dict:
    """Which button the keyed selector picks, identified by an id it ignores."""

    async def work(page):
        controls = page.locator(dom.unfollow_control_selector(ANCHOR_ID))
        count = int(await controls.count())
        return {
            "count": count,
            "id": await controls.first.get_attribute("id") if count else None,
            "label_only": int(await page.locator(dom.FOLLOWED_PAGE_BUTTON).count()),
        }

    return await _with_html(html, work)


@pytest.mark.asyncio
async def test_a_row_with_no_company_link_is_not_matched_when_nested_as_captured():
    """THE SAFETY TEST. A row with no company link must never be clicked.

    This encodes a real measurement, not a hypothetical. On 2026-08-24 a
    census found LinkedIn rendering the IDENTICAL label template -- ``Click to
    stop following <name>`` -- over PEOPLE on ``/feed/following/``: twenty
    rows, ``urn:li:member:`` urns, and no company link anywhere in them. A
    selector anchored on the label alone matched all twenty. This server
    cannot reach that surface today, which is exactly why the requirement has
    to be in the selector NOW: the day it meets a page nobody predicted is too
    late to add it.

    Both rows here wear the same label BY CONSTRUCTION, so the label cannot
    discriminate and the ``/company/`` link is the whole of the difference.
    The match is identified by an ``id`` the selector never looks at, which
    upgrades "matched one" to "matched WHICH one" -- with two identical labels
    on the page, a count of 1 alone would not tell them apart.

    NESTED because that is the shape that discriminates -- see the flat
    control beside it.
    """
    got = await _match_on(_MEMBER_ROW_NESTED)

    assert got["label_only"] == 2, (
        "both rows must wear the same label or this test proves nothing"
    )
    assert got["count"] == 1, f"matched {got['count']} buttons, not 1"
    assert got["id"] == "row-with-company-link", (
        f"matched {got['id']!r} -- the selector picked the member-shaped row"
    )


@pytest.mark.asyncio
async def test_the_same_case_written_flat_is_a_control_that_could_not_fail():
    """The flat twin of the test above, kept for what it FAILED to catch.

    MEASURED, and this is the reason the pair exists. Against the selector as
    it shipped on 2026-08-24 -- whose row predicate had dropped the
    company-link condition -- these two markups disagreed:

        FLAT   (button a sibling of the link)  -> count 1, correct row. PASSED.
        NESTED (button in its own wrapper div) -> count 0. FAILED.

    and the real capture NESTS it. So the flat form was green while the
    selector matched NOTHING across all twenty rows of the actual page: a
    safety test that could not fail, certifying a selector that did not work.
    The nesting is chosen by whoever writes the markup, which is what makes
    this trap available at all -- and the flat form is the one a person
    naturally writes.

    Both pass now that the predicate is shared and climbs to a scope holding
    the link. This one is retained as the CONTROL: it records that AGREEMENT
    between the two shapes is the property to keep, so that if a future change
    makes them diverge again the pair says so, instead of one of them quietly
    carrying the suite.
    """
    got = await _match_on(_MEMBER_ROW_FLAT)

    assert got["label_only"] == 2
    assert got["count"] == 1, f"matched {got['count']} buttons, not 1"
    assert got["id"] == "row-with-company-link", (
        f"matched {got['id']!r} -- the selector picked the member-shaped row"
    )

    # The pair's actual claim: the two nestings agree. Asserted here so a
    # divergence is reported AS a divergence, rather than as one red test.
    nested = await _match_on(_MEMBER_ROW_NESTED)
    assert got["count"] == nested["count"], (
        f"flat matched {got['count']} and nested matched {nested['count']} -- "
        "the selector has become sensitive to row nesting again, which is the "
        "defect measured on 2026-08-24"
    )
    assert got["id"] == nested["id"]


# ---------------------------------------------------------------------------
# F. Row isolation, across every row on the page
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_every_rendered_row_reads_its_own_label_and_never_a_neighbours():
    """All twenty rows at once: no id may read its NEIGHBOUR's label.

    The sampled test above could pass on a selector that happens to be right
    for five ids. This runs the full page and requires twenty ones and twenty
    DISTINCT labels, which is the property a selector drifting one row up or
    down breaks immediately -- an off-by-one row hop still returns count 1 and
    still returns a real company name, and only collides once you look at all
    of them together.

    Delete this and the isolation of a row from the one drawn beside it is
    checked over a fifth of the page.
    """
    mapping = expected_names("pages_hydrated")
    assert len(mapping) == ROWS_RENDERED["pages_hydrated"]

    async def work(page):
        out = {}
        for company_id in mapping:
            out[company_id] = await dom.read_unfollow_control(page, company_id)
        return out

    results = await _with_html(markup("pages_hydrated"), work)

    wrong = {
        company_id: got
        for company_id, got in results.items()
        if got["count"] != 1 or got["label"] != mapping[company_id]
    }
    assert not wrong, f"rows that did not read their own label: {wrong}"

    labels = [got["label"] for got in results.values()]
    assert len(set(labels)) == len(mapping), (
        "two ids resolved to the same label -- one of them read the other's row"
    )


# ---------------------------------------------------------------------------
# G. The can-it-fail control
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_keyed_selector_is_not_the_label_only_selector():
    """Proves this module cannot pass against a stub that ignores the id.

    The page carries TWENTY buttons matching the label alone. An
    ``unfollow_control_selector`` that returned the label-only locator --
    ignoring its argument entirely, which is the most natural stub anyone
    would write -- would therefore report count 20 here, and every keyed read
    in this module would resolve to ``count != 1`` and refuse. So this
    assertion FAILS against that stub, which is what makes the count-1
    assertions elsewhere mean something.

    The two numbers are asserted TOGETHER, off the same page in the same run.
    Asserting the 1 on its own would not distinguish a working selector from a
    page that only ever drew one row.
    """

    async def work(page):
        return {
            "label_only": int(await page.locator(dom.FOLLOWED_PAGE_BUTTON).count()),
            "keyed": await dom.read_unfollow_control(page, ANCHOR_ID),
        }

    got = await _with_html(markup("pages_hydrated"), work)

    assert got["label_only"] == ROWS_RENDERED["pages_hydrated"] == 20
    assert got["keyed"]["count"] == 1
    assert got["keyed"]["count"] < got["label_only"], (
        "the keyed selector matched as widely as the label-only one -- it is "
        "not discriminating on the company id at all"
    )


# ---------------------------------------------------------------------------
# The regression test for the defect this module was written against
# ---------------------------------------------------------------------------


def test_the_read_and_write_paths_share_one_row_predicate():
    """Pins the SHARING, because pinning the two strings apart is what failed.

    THE DEFECT, measured 2026-08-24. The write path carried its OWN copy of
    the row predicate, above a comment asserting it was "reused verbatim" from
    the reader's. It was not: the copy had dropped
    ``[.//a[contains(@href,'/company/')]]``. Without that condition the scope
    hop stops at the NEAREST ancestor holding exactly one unfollow button,
    which on the real capture is the bare ``<div>`` wrapping the button -- a
    scope holding zero company links. Consequence on the twenty-row fixture:
    ALL TWENTY ids returned ``{'label': None, 'count': 0}``. Every unfollow
    would have refused, indefinitely, while the reader beside it worked
    perfectly and reported all twenty rows with their hrefs.

    WHY THIS TEST IS SHAPED THIS WAY. A test that pinned each string against
    its own expected literal would have been GREEN throughout: both strings
    were exactly what such a test would have said they were. What was false
    was the RELATIONSHIP -- and the only thing asserting it was a comment. A
    comment claiming two strings are identical is worth nothing; being the
    same string is worth what the comment claimed. So this asserts the
    identity, and then asserts the condition whose loss was the actual bug, so
    that a future edit which keeps them shared but strips the condition from
    BOTH is still caught.
    """
    assert dom._FOLLOWED_PAGE_ID_SCOPE == "xpath=" + dom._ROW_SCOPE, (
        "the read and write paths no longer share one row predicate -- this is "
        "the exact drift that made every unfollow refuse on 2026-08-24"
    )

    link_condition = "[.//a[contains(@href,'/company/')]]"
    assert link_condition in dom._ROW_SCOPE, (
        "the row predicate has lost its company-link condition; the scope hop "
        "will stop at the bare div wrapping the button and match nothing"
    )

    # And the condition has to survive into the ASSEMBLED selector, not just
    # into the constant -- the builder splices the string rather than
    # referencing it.
    assert link_condition in dom.unfollow_control_selector(ANCHOR_ID)
