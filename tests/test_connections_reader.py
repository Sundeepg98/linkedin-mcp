"""The connections list: his own network, and the id needed to reach anyone on it.

**WHAT WAS BUILT AND WHY IT STILL REFUSES.** ``5e33aa9`` admitted
``/mynetwork/invite-connect/connections/`` on 2026-09-03 and **nothing read
it** -- the state ``_audit/2026-09-03-linkedin-gap-blockers.md`` A10 calls "a
boundary opened with nothing behind it", where "the refusal is gone and the
answer is still unavailable, and nothing in the tool surface would tell you
which of those two states you are in". This file certifies the reader that was
built behind that refusal. ``linkedin_connections`` still declines, because the
pending-invitation cost of opening the page is unmeasured and the badge that
would measure it reads zero -- and a zero before against a zero after cannot
tell "consumed nothing" from "there was nothing to consume".

## THE FIXTURE IS INVENTED AND SAYS SO

``tests/fixtures/connections_list.html`` is **not a capture.** That page has
never been opened by this server, because opening it is exactly the cost the
tool refuses to spend. Its STRUCTURE is assembled from things measured
elsewhere -- LinkedIn's own Help Center for the per-row Message control, the
committed profile-views capture for the shape of the Message href, this repo's
audit for the nav badge's label tail -- and its names, slugs and ids are
invented. Every claim below is therefore a claim about **the reader against a
page of that shape**, and none of them is a claim about LinkedIn today.

## TWO DEFECTS THIS FIXTURE FOUND, BOTH BEFORE THE CODE WAS TRUSTED

**1. The recipient-id climb left the row and blamed a stranger.** A Message
control with no person row of its own -- a promo block offering to message a
recruiter -- climbed TWO hops, reached the list container, and was attributed
to the FIRST person on the page. The hop budget is eight, so no cap could have
caught it: the walk had no containment rule at all. Measured, not read off the
source::

    before   slug='farhan-qureshi-2b8e77c4'   hops=2      <-- a stranger's id
    after    slug=''  left_the_row=True       hops=2

The fix is ``rowOf``'s own stop condition, which the sibling walk in
``HARVEST_LINKED_CARDS_JS`` has run on every surface this package reads:
an ancestor holding more than one distinct person is not this button's row.
``tests/test_recipient_ids_from_the_viewer_list.py`` still passes on the
committed profile-views captures, so the measured surface is unchanged and the
unmeasured one is strictly safer.

**2. Every headline was the name printed twice.** ``innerText`` welds a
``.visually-hidden`` copy of the name onto the visible one, so the doubled
string is not equal to the name and the "skip the name" test never fired::

    before   headline='Farhan Qureshi Farhan Qureshi'
    after    headline='Engineering Manager at Umbrella Systems'

## THE ONE PROPERTY THIS FILE EXISTS FOR

**The join is by SLUG and index pairing gets every row wrong here.** The
fixture's FIRST row has no Message control, which shifts the two lists apart
from the top: pairing them by position attaches a stranger's identifier to
every single row rather than to none of them or to one. A fixture where index
pairing accidentally works cannot fail on the defect it is written to catch,
and ``test_index_pairing_would_attach_a_strangers_identifier`` runs the wrong
algorithm on purpose to show that it does.

## IDENTIFIERS

A member id names a real person as surely as a name does. Slugs are asserted
because they are in the committed fixture and are how the join is proved. **No
id is written down in this file** -- not as an expected value, not in a failure
message -- and the expected ids are DERIVED from the fixture by an independent
parse rather than transcribed. ``test_no_identifier_appears_in_this_files_own_assertions``
holds this file to that.
"""

from __future__ import annotations

import ast
import inspect
import re
import sys
import textwrap
from pathlib import Path

import pytest

from linkedin_server import dom, server, shape

FIXTURE = Path(__file__).parent / "fixtures" / "connections_list.html"

#: The people the fixture draws, in DOM order.
ROW_SLUGS = [
    "farhan-qureshi-2b8e77c4",
    "anita-krishnan-9d2f4a11",
    "daniel-okonkwo-77bd9f02",
    "lakshmi-menon-51ac0e39",
    "sunita-rao-3ef1a6d8",
]

#: The ones LinkedIn drew a Message control for. Two of the five are NOT here,
#: and their absence is the point: "is a connection" and "can be messaged from
#: this page" are different questions, exactly as they were on the viewer list.
MESSAGEABLE_SLUGS = {
    "anita-krishnan-9d2f4a11",
    "lakshmi-menon-51ac0e39",
    "sunita-rao-3ef1a6d8",
}

#: The row whose whole card sits inside the person anchor, so its name cannot
#: be read off the link.
NAMED_OFF_THE_ROW = "sunita-rao-3ef1a6d8"

#: Message controls the fixture draws: one per messageable row, plus the promo
#: block that has no row at all.
MESSAGE_CONTROLS = len(MESSAGEABLE_SLUGS) + 1

#: THE LAST COMMIT WHERE THIS FILE STILL CALLED THE TOOL BARE, so the guard
#: below can be shown failing against the real thing rather than a mock-up.
#: Measured, not remembered: of the four commits touching this file,
#: ``400e761`` and ``84dccba`` carry the bare-calling test and the two after
#: them do not.
#:
#: IT IS A SHA AND A REWRITE IS PLANNED FOR THIS REPOSITORY, so the test that
#: reads it SKIPS on a git failure rather than going red -- and its synthetic
#: control runs either way, so a rewrite cannot turn that guard into a check
#: over nothing.
PRE_FIX_COMMIT = "84dccba"

#: The recipient parameter AS THE SOURCE FILE SPELLS IT. Html escapes the
#: separator, so a query string reads ``?a=1&amp;recipient=...`` on disk and
#: ``?a=1&recipient=...`` once a browser has parsed it. ``dom.RECIPIENT_ID_HREF``
#: is correct for the DOM and wrong for the file, which is a real trap: it
#: matched ONE of the four controls here and reported the fixture malformed.
RECIPIENT_IN_SOURCE = r"(?:[?&]|&amp;)recipient="


# ---------------------------------------------------------------------------
# Running the real code over the fixture
# ---------------------------------------------------------------------------


async def _open(page_factory):
    """Load the fixture into a real headless page."""
    playwright = pytest.importorskip("playwright.async_api")
    html = FIXTURE.read_text(encoding="utf-8")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page(
                viewport={"width": 1280, "height": 900}
            )
            await page.set_content(
                html, wait_until="domcontentloaded", timeout=60_000
            )
            return await page_factory(page)
        finally:
            await browser.close()


async def _read_rows():
    """``server._read_connection_rows`` over the fixture, as the tool runs it."""

    async def run(page):
        return await server._read_connection_rows(page, limit=25)

    return await _open(run)


async def _read_buttons():
    """``dom.read_recipient_ids`` over the fixture -- the raw button list."""
    return await _open(dom.read_recipient_ids)


def _ids_by_slug_from_the_fixture() -> dict[str, str]:
    """The expected join, DERIVED from the fixture by an independent parse.

    Blocks of ``<li>`` text and two regexes -- deliberately a different
    instrument from the reader's DOM climb, so this is a cross-check rather
    than the same algorithm agreeing with itself. And it is why no identifier
    is transcribed into this file: the expected values come out of the
    committed markup at run time.
    """
    html = FIXTURE.read_text(encoding="utf-8")
    person = re.compile(r'href="/in/([A-Za-z0-9\-_%]{2,})/"')
    recipient = re.compile(RECIPIENT_IN_SOURCE + r"([A-Za-z0-9_-]{1,64})")
    out: dict[str, str] = {}
    for block in html.split("<li")[1:]:
        block = block.split("</li>")[0]
        slugs = person.findall(block)
        ids = recipient.findall(block)
        if len(slugs) == 1 and len(ids) == 1:
            out[slugs[0]] = ids[0]
    return out


# ---------------------------------------------------------------------------
# The fixture draws what this file says it draws
# ---------------------------------------------------------------------------


def test_the_fixture_is_arranged_so_index_pairing_cannot_pass_by_luck():
    """A fixture that cannot fail certifies nothing, and this is where it
    would silently stop being able to.

    The property is POSITIONAL: the first row must be one WITHOUT a Message
    control, because that is what shifts the button list against the row list
    from the very top. If somebody later reorders the fixture so the first row
    is messageable, index pairing starts agreeing with the slug join on some
    rows and the red control below goes quietly green.
    """
    assert ROW_SLUGS[0] not in MESSAGEABLE_SLUGS
    assert len(MESSAGEABLE_SLUGS) < len(ROW_SLUGS)


def test_the_fixture_draws_the_shapes_these_tests_assume():
    """Read off the committed markup, so a fixture edit fails here first."""
    html = FIXTURE.read_text(encoding="utf-8")
    # /in/me/ is the nav's link to HIS profile and is not a connection, so it
    # is subtracted here rather than being allowed to inflate the count.
    assert len(re.findall(r'href="/in/(?!me/)', html)) == len(ROW_SLUGS)
    assert len(re.findall(r'href="/in/me/"', html)) == 1
    # THE SOURCE SPELLS THE SEPARATOR ``&amp;`` AND THE DOM SPELLS IT ``&``.
    # A regex over the file that assumed the DOM's spelling found ONE of the
    # four controls and reported the fixture malformed -- worth the comment,
    # because every cross-check in this file reads the file rather than the
    # page and would make the same mistake.
    assert len(re.findall(RECIPIENT_IN_SOURCE, html)) == MESSAGE_CONTROLS
    # TWO NETWORK CONTROLS, AND THE SPELLINGS ARE THE LIVE ONES. Measured on
    # the feed 2026-09-04: the BADGED control's href has no trailing slash and
    # the unbadged one does. Written this way round because the fixture had it
    # backwards and the live nav refuted it -- see
    # test_the_pre_fix_badge_aim_finds_nothing_on_the_live_spelling.
    assert len(re.findall(r'href="[^"]*/mynetwork', html)) == 2
    assert 'href="https://www.linkedin.com/mynetwork"' in html
    assert len(re.findall(r'href="[^"]*/mynetwork/', html)) == 1
    assert html.count(dom.INVITATION_BADGE_TAIL + "s\"") >= 1
    # His own profile is drawn in the nav and is not a connection.
    assert 'href="/in/me/"' in html


@pytest.mark.asyncio
async def test_the_reader_returns_one_row_per_connection():
    rows, census = await _read_rows()
    assert [row["profile"].rsplit("/", 1)[-1] for row in rows] == ROW_SLUGS
    # SIX keyed anchors, FIVE rows: the nav's own /in/me/ link is the sixth
    # and it is dropped structurally by profile_slug_from, not by a rule
    # written for the nav.
    assert census["anchors_keyed"] == len(ROW_SLUGS) + 1
    assert census["rows_parsed"] == len(ROW_SLUGS)
    assert census["rows_unparsed"] == 1


@pytest.mark.asyncio
async def test_the_headline_is_the_headline_and_not_the_name_twice():
    """DEFECT 2, pinned. Before the screen-reader subtraction ran, every row
    came back headlined with its own name printed twice -- because innerText
    welds the visually-hidden copy onto the visible one, so the doubled string
    was never equal to the name and the skip never fired.
    """
    rows, _ = await _read_rows()
    for row in rows:
        assert row["headline"], row["profile"]
        assert row["name"] not in row["headline"], row["headline"]
        assert row["headline"] != row["name"] + " " + row["name"]


@pytest.mark.asyncio
async def test_the_name_comes_off_the_link_where_the_link_names_one_thing():
    """``named_by`` reports which route named the row, and the two are not
    equally trustworthy -- so a page that quietly moved to the weaker one is
    visible in the census rather than only in a wrong answer later."""
    rows, census = await _read_rows()
    by_slug = {row["profile"].rsplit("/", 1)[-1]: row for row in rows}
    for slug, row in by_slug.items():
        expected = "row" if slug == NAMED_OFF_THE_ROW else "link"
        assert row["named_by"] == expected, slug
    assert census["named_by_link"] == len(ROW_SLUGS) - 1
    assert census["named_by_row"] == 1


# ---------------------------------------------------------------------------
# The join
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_each_row_carries_the_identifier_from_its_own_row():
    """The join, checked against an INDEPENDENT parse of the same fixture.

    The reader climbs the DOM; this expectation comes from splitting the
    committed markup on ``<li>`` and running two regexes. Two different
    instruments over one page is what makes this a check rather than the
    algorithm agreeing with itself.
    """
    rows, _ = await _read_rows()
    expected = _ids_by_slug_from_the_fixture()
    assert set(expected) == MESSAGEABLE_SLUGS
    for row in rows:
        slug = row["profile"].rsplit("/", 1)[-1]
        assert row["recipient_id"] == expected.get(slug), slug


@pytest.mark.asyncio
async def test_index_pairing_would_attach_a_strangers_identifier():
    """THE RED CONTROL: the wrong algorithm, run on purpose.

    A check that only ever runs the right algorithm cannot show that the
    property it asserts is doing any work. So this pairs the button list to
    the row list BY POSITION -- the defect the join exists to prevent -- and
    asserts the two answers disagree, and disagree on EVERY row rather than on
    a lucky one.
    """
    rows, _ = await _read_rows()
    reading = await _read_buttons()
    buttons = [e["recipient"] for e in reading["rows"] if e["recipient"]]

    correct = [row["recipient_id"] for row in rows]
    by_position = [
        buttons[index] if index < len(buttons) else None
        for index in range(len(rows))
    ]

    assert len(buttons) != len(rows), (
        "the two lists are the same length here, so index pairing cannot be "
        "shown wrong -- the fixture has stopped being able to fail"
    )
    disagreements = sum(
        1 for a, b in zip(correct, by_position) if a != b
    )
    assert disagreements == len(rows), (correct.count(None), disagreements)


@pytest.mark.asyncio
async def test_a_row_with_no_message_control_is_none_and_never_empty():
    """ABSENT IS NOT EMPTY, and the collapse is what this package has already
    lost measurements to. Two of the five are named connections LinkedIn drew
    no Message control for -- a fact about the relationship, not about
    visibility -- and they get ``None``."""
    rows, census = await _read_rows()
    for row in rows:
        slug = row["profile"].rsplit("/", 1)[-1]
        if slug in MESSAGEABLE_SLUGS:
            assert row["recipient_id"], slug
        else:
            assert row["recipient_id"] is None, slug
            assert row["recipient_id"] != ""
    assert census["with_recipient_id"] == len(MESSAGEABLE_SLUGS)


@pytest.mark.asyncio
async def test_no_two_rows_carry_the_same_identifier():
    """An off-by-one that handed everybody the same id would satisfy every
    other assertion here."""
    rows, _ = await _read_rows()
    ids = [row["recipient_id"] for row in rows if row["recipient_id"]]
    assert len(set(ids)) == len(ids) == len(MESSAGEABLE_SLUGS)


# ---------------------------------------------------------------------------
# The climb stays inside the row
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_a_control_with_no_row_is_unattributable_not_misattributed():
    """DEFECT 1, pinned.

    The promo block draws a Message control with no person row of its own.
    Before the containment rule, its id was attributed to the first person on
    the page in two hops -- comfortably inside a budget of eight, which is why
    the hop cap was never what kept the walk honest.
    """
    reading = await _read_buttons()
    assert reading["buttons"] == MESSAGE_CONTROLS
    stray = [e for e in reading["rows"] if not e["slug"]]
    assert len(stray) == 1
    assert stray[0]["left_the_row"] is True
    assert stray[0]["recipient"], "the id was read; only its owner is unknown"
    # And it reached nobody: no row carries it.
    rows, census = await _read_rows()
    assert stray[0]["recipient"] not in {r["recipient_id"] for r in rows}
    assert census["ids_unattributable"] == 1


@pytest.mark.asyncio
async def test_an_attributed_climb_reports_that_it_stayed_in_the_row():
    reading = await _read_buttons()
    for entry in reading["rows"]:
        if entry["slug"]:
            assert entry["left_the_row"] is False, entry["slug"]
            assert 0 < entry["hops"] < dom.RECIPIENT_ROW_HOPS, entry["slug"]


@pytest.mark.asyncio
async def test_the_containment_rule_is_what_stops_it_and_the_hop_cap_is_not():
    """THE CONTROL FOR THE FIX: show the OLD walk failing on this same page.

    The repair is only worth the change if the thing it replaced was actually
    broken here. So the pre-fix script is reconstructed -- the climb without
    the distinct-person stop -- and run against the fixture, and it is asserted
    to produce the misattribution. If a future edit made the old walk correct,
    this fails and the fix's justification has to be re-argued.
    """
    old_js = """
    (cfg) => {
      const personRe = new RegExp(cfg.personPattern);
      const recipientRe = new RegExp(cfg.recipientPattern);
      const out = [];
      for (const anchor of Array.from(document.querySelectorAll('a[href]'))) {
        const href = anchor.getAttribute('href') || '';
        const found = href.match(recipientRe);
        if (!found) continue;
        let node = anchor;
        let slug = '';
        let hops = 0;
        while (node && hops < cfg.maxHops && !slug) {
          node = node.parentElement;
          hops += 1;
          if (!node || !node.querySelectorAll) continue;
          for (const link of Array.from(node.querySelectorAll('a[href]'))) {
            const person = (link.getAttribute('href') || '').match(personRe);
            if (person) { slug = person[1]; break; }
          }
        }
        out.push({slug: slug, hops: hops});
      }
      return out;
    }
    """

    async def run(page):
        return await page.evaluate(
            old_js,
            {
                "personPattern": dom.PERSON_HREF,
                "recipientPattern": dom.RECIPIENT_ID_HREF,
                "maxHops": dom.RECIPIENT_ROW_HOPS,
            },
        )

    old = await _open(run)
    assert len(old) == MESSAGE_CONTROLS
    # THE STRAY CONTROL GOT A NAME -- somebody else's -- and it got there well
    # inside the hop budget.
    stray = old[-1]
    assert stray["slug"] == ROW_SLUGS[0]
    assert stray["hops"] < dom.RECIPIENT_ROW_HOPS
    # Every control was attributed, which is what "no containment rule" means.
    assert all(entry["slug"] for entry in old)


# ---------------------------------------------------------------------------
# The pending-invitation badge
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_the_badge_selector_narrows_two_network_controls_to_one():
    """``read_messaging_badge`` beside it takes ``.first``; this may not.

    The page draws a nav badge and a plain link into the same product, and
    those two controls are not interchangeable. The aim is the conjunction of
    the href and the measured label tail, so it resolves to exactly one.
    """

    async def run(page):
        return (
            await page.locator(
                'a[href*="%s"]' % dom.INVITATION_BADGE_HREF
            ).count(),
            await page.locator(dom.invitation_badge_selector()).count(),
        )

    links, badges = await _open(run)
    assert links == 2
    assert badges == 1


@pytest.mark.asyncio
async def test_the_pre_fix_badge_aim_finds_nothing_on_the_live_spelling():
    """THE CONTROL FOR THE FIX, and it is the second one this file carries.

    The aim required ``/mynetwork/`` WITH a trailing slash until 2026-09-04.
    Run against the live feed it resolved ZERO badge controls, while the badge
    it was looking for read ONE -- because the badged control's href has no
    trailing slash and the only control that does is a newsletters link
    carrying no label at all::

        a  aria-label with a count   href="https://www.linkedin.com/mynetwork"
        a  no aria-label             href=".../mynetwork/network-manager/newsletters/"

    So the old aim is rebuilt here and asserted to find NOTHING on a page
    drawn the way the live one is. Without this, the fix is a string somebody
    changed and the reason lives only in a commit message.

    IT FAILED CLOSED, WHICH IS WHY IT MATTERED. A miss that reports zero is
    indistinguishable from an absence, and "no badge" would have been read as
    "no pending invitations" -- the wrong answer to the exact question the
    tool is blocked on. What saved it was the refusal naming what it DID see:
    ``mynetwork_links=1, links_carrying_a_count=0`` says an element was found
    and rejected, which no bare zero can say.
    """
    pre_fix = 'a[href*="/mynetwork/"][aria-label*="%s"]' % dom.INVITATION_BADGE_TAIL

    async def run(page):
        return (
            await page.locator(pre_fix).count(),
            await page.locator(dom.invitation_badge_selector()).count(),
        )

    old, new = await _open(run)
    assert old == 0, "the pre-fix aim now resolves, so this control is stale"
    assert new == 1


@pytest.mark.asyncio
async def test_the_badge_reads_its_count_off_the_page():
    reading = await _open(dom.read_invitation_badge)
    assert reading["links"] == 2
    assert reading["badge_links"] == 1
    assert reading["error"] is None
    verdict = shape.invitation_badge(reading)
    assert verdict["state"] == "read"
    assert verdict["pending"] == 3


@pytest.mark.asyncio
async def test_a_page_with_no_badge_refuses_and_says_what_it_saw():
    """THE CONTROL FOR THE BADGE READER, and the reason it is a real page
    rather than a hand-built dict: a reader that cannot come back empty is a
    reader whose empty branch nobody has run."""

    async def run(page):
        await page.set_content(
            "<!doctype html><html><body><main>"
            '<a href="/mynetwork/">grow</a><a href="/feed/">home</a>'
            "</main></body></html>",
            wait_until="domcontentloaded",
        )
        return await dom.read_invitation_badge(page)

    reading = await _open(run)
    assert reading["links"] == 1
    assert reading["badge_links"] == 0
    verdict = shape.invitation_badge(reading)
    assert verdict["state"] == "unreadable"
    assert verdict["pending"] is None
    # NOT "zero matched". The refusal carries both counts, so a nav that never
    # hydrated and a label whose shape changed are distinguishable without
    # opening a browser.
    assert verdict["saw"]["mynetwork_links"] == 1
    assert verdict["saw"]["links_carrying_a_count"] == 0


def test_zero_is_a_reading_and_is_not_unreadable():
    """The distinction the whole cost measurement rests on. A badge at zero
    and a badge that never rendered look identical to a caller that collapses
    them -- and the reason this cost has never been measured is precisely that
    a zero cannot fail."""
    zero = shape.invitation_badge(
        {
            "links": 1,
            "badge_links": 1,
            "label": "<redacted>, 0 new notifications",
            "error": None,
        }
    )
    assert zero["state"] == "read"
    assert zero["pending"] == 0
    assert zero["pending"] is not None


def test_the_badge_prefix_is_never_matched():
    """THE PREFIX IS NOT A STRING THIS REPOSITORY HOLDS.

    The audit records this badge as ``<redacted>, 0 new notifications`` on two
    surfaces; its leading word was redacted by the census shaper. So the parse
    must work whatever precedes the comma -- which is also why the href, not
    the wording, is what says WHICH badge this is.
    """
    for prefix in ("<redacted>", "Nav", "Mon reseau", "<opaque>", ""):
        verdict = shape.invitation_badge(
            {
                "links": 1,
                "badge_links": 1,
                "label": prefix + ", 7 new notifications",
                "error": None,
            }
        )
        assert verdict["pending"] == 7, prefix


def test_the_singular_reading_is_not_reported_unreadable():
    """"1 new notification" is a real reading, and a plural-only pattern would
    call the one case that matters most a failure."""
    verdict = shape.invitation_badge(
        {"links": 1, "badge_links": 1, "label": "x, 1 new notification", "error": None}
    )
    assert verdict["pending"] == 1


def test_every_unreadable_branch_carries_what_it_saw():
    """Each refusal shown FIRING, and each carrying its evidence.

    Four ways the badge is unreadable, and they want four different repairs.
    A shared "zero matched" would make them one.
    """
    branches = [
        {"links": None, "badge_links": None, "label": None, "error": "TimeoutError: x"},
        {"links": 0, "badge_links": 0, "label": None, "error": None},
        {"links": 3, "badge_links": 2, "label": None, "error": None},
        {"links": 1, "badge_links": 1, "label": "<opaque>", "error": None},
    ]
    reasons = set()
    for reading in branches:
        verdict = shape.invitation_badge(reading)
        assert verdict["state"] == "unreadable", reading
        assert verdict["pending"] is None
        assert verdict["saw"]["mynetwork_links"] == reading["links"]
        assert verdict["saw"]["links_carrying_a_count"] == reading["badge_links"]
        reasons.add(verdict["why"])
    assert len(reasons) == len(branches), reasons


# ---------------------------------------------------------------------------
# The tool: what it refuses, and what it would do if the cost were recorded
# ---------------------------------------------------------------------------


class _FakeBrowser:
    """``BROWSER`` for the verdict branches: navigates, remembers, loads nothing."""

    def __init__(self, page):
        self._page = page
        self.gotos: list[str] = []

    def session(self):
        page = self._page
        class _Session:
            async def __aenter__(self_inner):
                return page

            async def __aexit__(self_inner, *exc):
                return False

        return _Session()

    async def goto(self, page, url):
        self.gotos.append(url)
        return url


def unfaked_callers(source: str, *, call: str, fake: str) -> list[str]:
    """Functions in ``source`` that call ``call`` without installing ``fake``.

    THE DETECTOR, factored out of its assertion so it can be pointed at a
    sample that MUST fail. A guard whose logic exists only inside the
    ``assert`` that consumes it can never be shown working -- which is the
    same defect, one level up, as the coincidence it was written to catch.

    Generic in both names on purpose: the property is not about LinkedIn. It
    is "a call that acts for real must not be reachable from a test unless
    that test installed the substitute", and every package that fakes a
    network, a clock or a filesystem has the same exposure.
    """
    tree = ast.parse(source)
    offenders: list[str] = []
    for func in ast.walk(tree):
        if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        called = {
            node.func.attr
            for node in ast.walk(func)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        if call not in called:
            continue
        body = ast.get_source_segment(source, func) or ""
        if fake not in body:
            offenders.append(func.name)
    return offenders


def test_no_test_in_this_file_may_call_the_tool_without_a_fake_browser():
    """THE HAZARD THAT ARRIVED WITH THE GATE CHANGE, pinned so it cannot
    return.

    Until 2026-09-04 ``linkedin_connections`` refused from a constant BEFORE
    opening anything, so calling it in a test was free. Removing that
    pre-flight refusal made the very same call NAVIGATE -- and a test here did
    exactly that on the next run: the log shows a profile lock acquired and a
    real Chrome started, against his real account, from a unit test, which put
    five real people's names and member ids into a pytest assertion message.

    **IT WAS CAUGHT ONLY BECAUSE THAT ASSERTION HAPPENED TO FAIL.** Had the
    marker not matched, a green test would have been reading his live network
    on every run, silently, forever.

    So this asserts BY AST that every call to the tool in this file sits in a
    function that also installs the fake browser. A reviewer cannot be asked
    to notice this by eye: the failure is silent, it looks like a slow test,
    and it only happens on the machine that has a live session.
    """
    offenders = unfaked_callers(
        Path(__file__).read_text(encoding="utf-8"),
        call="linkedin_connections",
        fake="_FakeBrowser",
    )
    assert offenders == [], offenders


def test_the_unfaked_caller_detector_catches_the_real_pre_fix_file():
    """SHOWN FAILING -- against the file as it ACTUALLY was, not a mock-up.

    The guard above passes, and a guard that has only ever passed is a guard
    nobody has seen work. So the detector is pointed at THE COMMITTED
    PRE-FIX VERSION of this very file, read out of git, where
    ``test_no_identifier_reaches_the_shipped_refusal`` called the tool bare.

    It must name that function. If a future edit makes the historical file
    stop offending -- or makes the detector stop noticing -- this fails, and
    the guard's justification cannot quietly rot.

    THE HISTORICAL READ IS NOT A DEPENDENCY ON HISTORY STAYING PUT. A rewrite
    is planned for this repository; if the commit becomes unresolvable the
    test SKIPS on the git error rather than failing, and the synthetic control
    below still runs. What must never happen is this file passing because it
    silently checked nothing.
    """
    import subprocess

    proc = subprocess.run(
        ["git", "show", "%s:tests/test_connections_reader.py" % PRE_FIX_COMMIT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(Path(__file__).resolve().parents[1]),
    )
    if proc.returncode != 0:
        pytest.skip("pre-fix commit unresolvable (history rewritten?)")

    offenders = unfaked_callers(
        proc.stdout, call="linkedin_connections", fake="_FakeBrowser"
    )
    assert "test_no_identifier_reaches_the_shipped_refusal" in offenders, offenders


def test_the_unfaked_caller_detector_can_fail_and_can_pass():
    """THE SYNTHETIC CONTROL, which runs even when git does not.

    Both directions, because a detector that flags everything is as useless
    as one that flags nothing -- and the passing half is the one that would
    have made this guard unusable by firing on every honest test.
    """
    offends = (
        "async def t():\n"
        "    out = await server.linkedin_connections(limit=5)\n"
        "    assert out\n"
    )
    assert unfaked_callers(
        offends, call="linkedin_connections", fake="_FakeBrowser"
    ) == ["t"]

    clean = (
        "async def t(monkeypatch):\n"
        "    browser = _FakeBrowser(object())\n"
        "    monkeypatch.setattr(server, 'BROWSER', browser)\n"
        "    out = await server.linkedin_connections(limit=5)\n"
    )
    assert unfaked_callers(
        clean, call="linkedin_connections", fake="_FakeBrowser"
    ) == []

    # AND IT MUST NOT FIRE ON A FILE THAT NEVER CALLS THE TOOL, or every
    # module in the repo becomes an offender.
    assert unfaked_callers(
        "def t():\n    assert 1\n", call="linkedin_connections", fake="_FakeBrowser"
    ) == []


@pytest.mark.asyncio
async def test_a_zero_badge_returns_the_rows_and_says_it_proved_nothing(
    monkeypatch,
):
    """THE GATE CHANGE OF 2026-09-04, and the case it was made for.

    The old pre-flight refusal demanded a recorded cost, and that cost needs a
    NON-ZERO badge nobody can arrange. It had blocked the capability
    indefinitely -- on the surface ``network.md`` calls the most consequential
    in the census for his actual job hunt.

    A ZERO BADGE IS TWO DIFFERENT ANSWERS TO TWO DIFFERENT QUESTIONS, and the
    old gate ran them together:

      * "does this page consume a badge, in general?" -- UNANSWERABLE at zero.
        Unchanged is the only outcome available, so the reading cannot fail.
      * "will this call consume one of HIS invitations?" -- ANSWERED, and
        answered safe. The badge counts what is unseen; at zero there is
        nothing to consume.

    So the rows come back AND ``cost.proven`` is false, with the reason. A
    result that quietly claimed the page was free would be the manufactured
    no-change this repository keeps meeting.
    """
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _reading(0), _reading(0))

    async def fake_rows(page, limit):
        return [{"name": "x", "recipient_id": None}], {"rows_parsed": 1}

    monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

    out = await server.linkedin_connections(limit=5)
    assert out["count"] == 1, "the rows are returned, which is the whole change"
    assert out["cost"]["proven"] is False
    assert "nothing to consume" in out["cost"]["why_the_call_was_safe_anyway"]
    assert "could not have failed" in out["cost"]["what_this_run_showed"]
    assert server.CONNECTIONS_URL in browser.gotos


@pytest.mark.asyncio
async def test_a_non_zero_badge_that_held_is_the_measurement(monkeypatch):
    """AND THE OTHER HALF, which is what makes ``proven`` mean anything.

    A badge that stood at three and still stands at three COULD have fallen.
    That is a real measurement of the page, obtained as a side effect of an
    ordinary call rather than from an experiment nobody can schedule -- and
    the result says so and asks for it to be recorded.
    """
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _reading(3), _reading(3))

    async def fake_rows(page, limit):
        return [{"name": "x"}], {"rows_parsed": 1}

    monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

    out = await server.linkedin_connections(limit=5)
    assert out["cost"]["proven"] is True
    assert "COULD have fallen and did" in out["cost"]["what_this_run_showed"]
    assert "record" in out["cost"]["record_it"]


def _patch_badges(monkeypatch, before, after):
    """Hand the tool two badge readings in order."""
    queue = [before, after]

    async def fake_read(page):
        return queue.pop(0)

    monkeypatch.setattr(dom, "read_invitation_badge", fake_read)


def _reading(pending):
    return {
        "links": 1,
        "badge_links": 1,
        "label": "x, %d new notifications" % pending,
        "error": None,
    }


_UNREADABLE = {"links": 0, "badge_links": 0, "label": None, "error": None}


@pytest.mark.asyncio
async def test_an_unreadable_badge_BEFORE_refuses_without_opening_the_page(
    monkeypatch,
):
    """The refusal that actually prevents something. Nothing is spent, and the
    proof is the navigation list: the connections address was never visited."""
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "CONNECTIONS_BADGE_COST", {"before": 0, "after": 0})
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _UNREADABLE, _reading(0))

    out = await server.linkedin_connections(limit=5)
    assert out["readable"] is False
    assert "BEFORE" in out["refused"]
    assert out["pages_loaded"] == 1
    assert server.CONNECTIONS_URL not in browser.gotos
    assert browser.gotos == [server.FEED_URL]


@pytest.mark.asyncio
async def test_an_unreadable_badge_AFTER_withholds_the_rows_it_already_read(
    monkeypatch,
):
    """The page is open by then, so the cost is already spent -- and the tool
    says so rather than hiding it. What it withholds is the RESULT, because a
    tool gated on a cost it could not confirm may not hand back a clean answer
    as though it had."""
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "CONNECTIONS_BADGE_COST", {"before": 0, "after": 0})
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _reading(2), _UNREADABLE)

    async def fake_rows(page, limit):
        return [{"name": "x", "recipient_id": None}], {"rows_parsed": 1}

    monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

    out = await server.linkedin_connections(limit=5)
    assert out["readable"] is False
    assert "AFTER" in out["refused"]
    assert out["rows"] == []
    assert out["pages_loaded"] == 2
    assert server.CONNECTIONS_URL in browser.gotos
    # It reports what it saw rather than only that it failed.
    assert out["census"]["rows_parsed"] == 1
    assert out["badge_before"]["pending"] == 2


@pytest.mark.asyncio
async def test_a_badge_that_MOVED_refuses_in_both_directions(monkeypatch):
    """Only an unchanged badge certifies that the load consumed nothing.

    A DROP is the harm. A RISE cannot be told apart from a drop masked by an
    invitation arriving mid-read, so it refuses too -- and both refusals name
    the constant they have just falsified.
    """
    for before, after in ((3, 2), (3, 4)):
        browser = _FakeBrowser(object())
        monkeypatch.setattr(
            server, "CONNECTIONS_BADGE_COST", {"before": 3, "after": 3}
        )
        monkeypatch.setattr(server, "BROWSER", browser)
        _patch_badges(monkeypatch, _reading(before), _reading(after))

        async def fake_rows(page, limit):
            return [{"name": "x"}], {"rows_parsed": 1}

        monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

        out = await server.linkedin_connections(limit=5)
        assert out["readable"] is False, (before, after)
        assert "MOVED" in out["refused"]
        assert out["rows"] == []
        assert out["badge_before"]["pending"] == before
        assert out["badge_after"]["pending"] == after
        # A REFUSAL THAT DOES NOT NAME THE CONSTANT IT JUST CONTRADICTED
        # leaves the next reader trusting a number this run disproved.
        assert "and_this_falsifies_the_recorded_cost" in out
        assert "CONNECTIONS_BADGE_COST" in out[
            "and_this_falsifies_the_recorded_cost"
        ]


@pytest.mark.asyncio
async def test_an_unchanged_badge_returns_the_rows(monkeypatch):
    """THE PASSING CASE, which is what makes the three refusals above mean
    something. Without it they could all be true of a tool that never
    returns."""
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "CONNECTIONS_BADGE_COST", {"before": 3, "after": 3})
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _reading(3), _reading(3))

    async def fake_rows(page, limit):
        return (
            [{"name": "x", "recipient_id": None}],
            {"rows_parsed": 1, "rows_unparsed": 0},
        )

    monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

    out = await server.linkedin_connections(limit=5)
    assert out.get("readable") is None, "the success shape is an envelope"
    assert out["count"] == 1
    assert out["pages_loaded"] == 2
    assert out["badge_before"]["pending"] == out["badge_after"]["pending"] == 3
    assert out["census"]["rows_parsed"] == 1


# ---------------------------------------------------------------------------
# It is an identifier
# ---------------------------------------------------------------------------


#: The names that put a string somewhere it outlives the call.
SINKS = ("print", "logger", "logging", "warn", "warnings")

#: Parsed module sources, keyed by path. Cached because several checks below
#: read the same three files, and because re-reading a file another agent is
#: writing gives two checks in one run two different answers.
_AST_CACHE: dict[str, ast.AST] = {}


def _module_ast(path: Path) -> ast.AST:
    key = str(path)
    if key not in _AST_CACHE:
        _AST_CACHE[key] = ast.parse(path.read_text(encoding="utf-8"))
    return _AST_CACHE[key]


def _sink_calls(func) -> list[str]:
    """Every logging-or-printing CALL in a function, found by AST.

    NOT A SUBSTRING SCAN, and the difference is not pedantry. A string search
    reads ``logger.`` inside a docstring or a comment as a call, and reads
    ``getattr(logger, level)(value)`` as clean -- wrong in both directions. It
    also cannot see into a nested ``def``, which is exactly where a
    convenience helper would hide one. ``ast`` answers the question actually
    being asked: does this function CALL something that emits?

    AND NOT ``inspect.getsource`` EITHER, WHICH IS THE SECOND LESSON. This
    used ``ast.parse(textwrap.dedent(inspect.getsource(func)))`` and it FAILED
    on 2026-09-04 with a SyntaxError pointing at the middle of a docstring.
    ``getsource`` resolves a function by the line number recorded when the
    module was IMPORTED and then reads the file from DISK -- so in a tree that
    another agent is writing, the two disagree and it returns a slice of the
    wrong lines. Five agents were committing to this repository at the time.

    So the module file is parsed ONCE and the function is located BY NAME.
    That is immune to the race, and it is the right instrument anyway: the
    question is about the source on disk, not about the object in memory.
    """
    module = sys.modules[func.__module__]
    tree = _module_ast(Path(module.__file__))
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == func.__name__
        ):
            tree = node
            break
    else:  # pragma: no cover - a renamed function must fail loudly
        raise AssertionError(
            "%s is not defined in %s -- this check would otherwise pass by "
            "scanning nothing" % (func.__name__, module.__file__)
        )
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if isinstance(target, ast.Name) and target.id in SINKS:
            found.append(target.id)
        elif isinstance(target, ast.Attribute):
            root = target.value
            if isinstance(root, ast.Name) and root.id in SINKS:
                found.append(root.id + "." + target.attr)
    return found


def test_nothing_on_this_path_logs_or_prints_an_identifier():
    """THE CHEAPEST WAY NOT TO LOG ONE IS TO HAVE NOWHERE THAT DOES.

    Every function a member id passes through, checked by AST rather than by
    searching the source for a substring.
    """
    for func in (
        server._read_connection_rows,
        server._connections_refusal,
        server._attach_recipient_ids,
        dom.read_recipient_ids,
        dom.read_invitation_badge,
        shape.parse_connection_card,
    ):
        assert _sink_calls(func) == [], func.__name__


def test_the_sink_check_can_fail():
    """THE CONTROL. A sweep that has never seen a sink cannot show that it
    would recognise one, and every function above is clean -- so the detector
    is pointed at three shapes it must all catch, including the two a
    substring scan gets wrong.
    """

    def logs_directly():
        logger.debug("x")  # noqa: F821 - never executed

    def logs_through_a_module():
        logging.getLogger(__name__).info("x")  # noqa: F821

    def prints_inside_a_nested_def():
        def helper():
            print("x")

        return helper

    assert _sink_calls(logs_directly) == ["logger.debug"]
    assert "logging.getLogger" in _sink_calls(logs_through_a_module)
    assert _sink_calls(prints_inside_a_nested_def) == ["print"]

    # AND IT DOES NOT FIRE ON PROSE. A docstring naming a sink is not a call,
    # and the substring scan this replaced could not tell the two apart -- it
    # would have failed on this very function.
    def only_talks_about_logging():
        """Nothing here logs: no logger. call, no print( anywhere."""
        return 1

    assert _sink_calls(only_talks_about_logging) == []


def test_the_connections_path_adds_no_injected_script():
    """NO NEW ``page.evaluate`` WAS SPENT ON THIS CAPABILITY.

    ``tests/test_readonly.py`` pins the waiver budget for the whole package;
    this asserts the narrower thing that file cannot -- that the reader built
    here runs only scripts already declared, rather than that a total happened
    not to move.
    """
    called = {
        node.func.attr
        for node in ast.walk(
            ast.parse(
                textwrap.dedent(inspect.getsource(server._read_connection_rows))
            )
        )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "evaluate" not in called
    # It reaches the page only through readers that already exist.
    assert {"harvest_census", "read_recipient_ids"} <= called


@pytest.mark.asyncio
async def test_the_census_counts_identifiers_without_holding_one():
    """THE THIRD SINK, and the one the taint rule does not model.

    The rule covers ``goto`` and ``print``. A RETURNED identifier is a third
    sink: the census travels beside the rows into a model's context and into
    transcripts, so a census that carried a LIST of ids would publish them to
    every reader of the result. Every id-shaped value in it is asserted absent
    -- the counters are lengths.
    """
    rows, census = await _read_rows()
    ids = {row["recipient_id"] for row in rows if row["recipient_id"]}
    assert ids, "nothing to leak means nothing was tested"
    flat = repr(census)
    for value in ids:
        assert value not in flat
    for key, value in census.items():
        assert value is None or isinstance(value, (int, str)), (key, value)
    assert census["with_recipient_id"] == len(ids)


@pytest.mark.asyncio
async def test_no_identifier_reaches_a_refusal_payload(monkeypatch):
    """A refusal is the payload most likely to be read, quoted and pasted, so
    it is the one that must carry no identifier.

    IT USED TO CALL THE TOOL BARE, AND THAT BECAME A LIVE LEAK THE MOMENT THE
    PRE-FLIGHT REFUSAL WENT. Recorded because the diff that caused it looked
    entirely safe: this test asserted "no id in the result" and passed for as
    long as the result was a constant. With the constant gone, the same line
    opened his real session, loaded the real connections list, and put five
    real people's names and member ids into a pytest assertion message. The
    assertion FAILED, which is the only reason anybody saw it -- had the
    marker not matched, a green test would have been quietly reading his
    network on every run.

    THE LESSON IS NOT ABOUT THIS TEST. A test whose safety rests on the code
    under test declining to act has no safety at all; it has a coincidence.
    ``test_no_test_in_this_file_may_call_the_tool_without_a_fake_browser``
    is the structural fix, and this is now driven by the fake browser like
    every other call in this file.
    """
    browser = _FakeBrowser(object())
    monkeypatch.setattr(server, "BROWSER", browser)
    _patch_badges(monkeypatch, _reading(2), _UNREADABLE)

    async def fake_rows(page, limit):
        # A row carrying an id, so the refusal has something it COULD leak.
        # A refusal proved clean against rows that never held one proves
        # nothing at all.
        return [{"name": "x", "recipient_id": "ACo" + "AA" + "synthetic"}], {
            "rows_parsed": 1
        }

    monkeypatch.setattr(server, "_read_connection_rows", fake_rows)

    out = await server.linkedin_connections(limit=5)
    assert out["readable"] is False
    assert out["rows"] == []
    marker = "ACo" + "AA"
    assert marker not in repr(out), "the withheld rows reached the refusal"


#: Landings this tool could plausibly be handed, built rather than written.
#: The two query cases are the ones that used to leak.
def _source_url_probes() -> list[tuple[str, str, str]]:
    base = "https://www.linkedin.com"
    token = "AC" + "oAAB" + "0" * 4 + "xyz"
    slug = "some-real-slug-99"
    return [
        ("the admitted address", server.CONNECTIONS_URL, token),
        ("token in a query", server.CONNECTIONS_URL + "?u=" + token, token),
        ("token in a recipient query", base + "/messaging/compose/?recipient=" + token, token),
        ("redirect to a profile", base + "/in/" + slug + "/", slug),
        ("token as an /in/ segment", base + "/in/" + token + "/", token),
        ("composite urn in a path",
         base + "/x/urn" + ":li:fsd_profileGeo:(" + token + ",GEO)/", token),
        # THE TWO THE FIRST PROBE SET MISSED, and their absence WAS the
        # defect. A member token outside an `/in/` segment survived
        # census_substitute untouched, because `/in/` is the only member shape
        # that predicate knows. The six cases above were chosen to match what
        # I already believed the risk was; these two are why the shipped fix
        # is a closed vocabulary rather than a shaping pass.
        ("token in a NON-/in/ path", base + "/messaging/thread/" + token + "/", token),
        ("token in a mynetwork path", base + "/mynetwork/" + token + "/", token),
        ("auth wall carrying a slug", base + "/authwall?sessionRedirect=/in/" + slug, slug),
        ("empty landed", "", token),
    ]


@pytest.mark.parametrize(
    "label,landed,secret", _source_url_probes(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_no_identifier_leaves_through_source_url(label, landed, secret):
    """``source_url`` is the one field on this tool read off the PAGE.

    The rows publish third parties' identifiers on purpose; this field does
    not, and it is the only place where a redirect could smuggle one out of a
    surface made entirely of other people.
    """
    assert secret not in server._connections_source_url(landed), label


def test_the_source_url_closure_was_shown_leaking_first():
    """THE CONTROL, and it is a control over MY OWN FIRST ATTEMPT.

    The first version of ``_connections_source_url`` shaped the whole landed
    url on the mismatch branch, and its comment claimed the member-token class
    was removed. Measured, it was not: the claim held on the MATCHING branch
    and failed on the only branch where a token can appear.

        shape.census_substitute(".../connections/?u=<token>")
            -> unchanged. TOKEN SURVIVED.

    So the pre-fix behaviour is reconstructed here and asserted to leak. If
    the shared predicate ever learns bare member tokens this fails, and the
    query-dropping in the helper can be revisited deliberately rather than
    left in place because nobody rechecked.
    """
    token = "AC" + "oAAB" + "0" * 4 + "xyz"
    base = "https://www.linkedin.com"

    # ATTEMPT 1, rebuilt: shape the WHOLE landed url. Leaks on a query.
    query_landing = server.CONNECTIONS_URL + "?u=" + token
    assert token in shape.census_substitute(query_landing), (
        "the shared predicate now covers bare member tokens in a query -- "
        "revisit _connections_source_url rather than keeping its vocabulary "
        "for a reason that has expired"
    )

    # ATTEMPT 2, rebuilt: shape the landed PATH, query dropped. STILL LEAKS,
    # and this is the one that was missed the first time round -- a member
    # token outside an `/in/` segment is invisible to that predicate.
    path_landing = base + "/messaging/thread/" + token + "/"
    from urllib.parse import urlsplit

    assert token in shape.census_substitute(urlsplit(path_landing).path), (
        "the shared predicate now covers member tokens in a non-/in/ path "
        "segment -- the closed vocabulary can be revisited deliberately"
    )

    # AND THE SHIPPED BODY LEAKS NEITHER.
    assert token not in server._connections_source_url(query_landing)
    assert token not in server._connections_source_url(path_landing)


def test_the_docstrings_on_this_path_carry_no_identifier():
    """A docstring is a sink too: it ships in the tool description and reaches
    every model that lists the surface."""
    marker = "ACo" + "AA"
    for obj in (
        server.linkedin_connections,
        server._read_connection_rows,
        server._attach_recipient_ids,
        dom.read_recipient_ids,
        dom.read_invitation_badge,
        shape.parse_connection_card,
        shape.invitation_badge,
    ):
        assert marker not in (obj.__doc__ or "")


def test_no_identifier_appears_in_this_files_own_assertions():
    """AND THIS FILE HOLDS ITSELF TO THE SAME RULE.

    Slugs are asserted because they are already in the committed fixture and
    are how the join is proved. Ids are never written down here: the expected
    values are DERIVED from the fixture at run time by
    :func:`_ids_by_slug_from_the_fixture`.

    BUILT FROM PARTS, because a literal ban written literally fails on itself
    -- which is the guard telling you it cannot name the thing it forbids and
    still forbid it.
    """
    marker = "ACo" + "AA"
    assert marker not in Path(__file__).read_text(encoding="utf-8")
