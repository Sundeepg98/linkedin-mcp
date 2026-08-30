"""The job-tracker readiness wait, and the evidence its refusal now carries.

WHAT WAS WRONG. On 2026-08-30 the operator performed the first save in this
server's life, on job 4423880462. LinkedIn's own Saved tab then read 1, and
``linkedin_saved_jobs`` could not show it to him::

    no saved jobs could be read, and the page does not corroborate an empty
    list: LinkedIn's own Saved tab says 1, and no empty state was drawn.

The refusal is CORRECT -- it refuses to let a failed read look like "you have
none" -- and it is also the whole of what the failure taught anybody. It names
LinkedIn's count and its own zero and NOTHING about the page those two
disagree over, which is the identical defect the save refusal was rebuilt for
earlier the same day: a gate that made a correct decision and then threw away
the evidence for it.

THE MEASUREMENT THAT SHAPED THIS FILE, and it is why the wait is not sold here
as the cure. Driven live through one process at ``42a68aa``, inside one
ten-minute window, alternating with ``linkedin_search_jobs`` as the control:

    surface                     attempts   read the list
    linkedin_saved_jobs             6            0
    linkedin_draft_applications     2            2
    linkedin_my_applications        2            2
    linkedin_search_jobs (control)  2            2

All three tracker tools are ONE function -- ``server._read_tracker`` -- loading
one url shape through one loader. A settle race does not produce 6-0 on one
stage while its siblings go 4-0. So the readiness wait below closes a real hole
that all three tabs had, and it is NOT established as the cause of the Saved
tab's failure. ``dom.read_tracker_evidence`` is the half that will name that
cause, on the next live call, by reporting what the page actually held.

WHY A WAIT AND NOT A BIGGER NUMBER. Settled already, and not re-opened here:
``browser.goto`` has exactly two settle durations about seven seconds apart, so
every candidate number sits inside an unmeasured bracket, and a flat floor
taxes every surface for one surface's missing check. See
``_audit/2026-08-30-jobs-view-reliability.md``.

Every reading below is taken by the REAL reader over a REAL parsed DOM in a
local headless Chromium. Nothing here reaches the network or an account. The
SHELL page is DERIVED from ``fixtures/jobs_tracker_empty.html`` by an explicit,
asserted edit and is labelled DERIVED wherever it is used -- it is a model of
the failing state, never evidence about LinkedIn.

EVERY TEST HERE WAS SHOWN FAILING at the mutation named in its docstring. The
mutations are applied at RUNTIME against this module's own copies, so no source
file is edited to produce them.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from linkedin_server import browser as browser_module
from linkedin_server import dom, shape
from linkedin_server.errors import ExtractionFailedError
from linkedin_server.server import linkedin_saved_jobs

FIXTURE_DIR = Path(__file__).parent / "fixtures"

SAVED_URL = "https://www.linkedin.com/jobs-tracker/?stage=saved"

#: The two anchors the SHELL derivation is built on. Both are asserted to
#: change something, because a ``replace`` whose anchor has drifted is a silent
#: no-op and this repo has already shipped one test built on that.
EMPTY_HEADING = ">No jobs here</h2>"
SAVED_TAB_ZERO = "Saved &#183; 0"

#: A settle reading standing for "the navigation took the fast branch". The
#: branch name is ``shape.SETTLE_EARLY`` rather than a literal, so a rename
#: there cannot leave a stale copy here.
SETTLED_EARLY = {"branch": shape.SETTLE_EARLY, "settled_ms": 1004}


def markup(which: str) -> str:
    """A capture, read as ASCII exactly as every other fixture module reads."""
    return (FIXTURE_DIR / f"{which}.html").read_text(encoding="ascii")


def derive(src: str, old: str, new: str, *, count: int = 1) -> str:
    """One DERIVED page, plus a receipt that the edit actually landed."""
    out = src.replace(old, new, count)
    assert out != src, (
        f"the derivation anchored on {old!r} changed nothing, so this variant "
        "is the base fixture wearing another name. Repoint the anchor, and do "
        "NOT delete this assertion."
    )
    return out


def shell() -> str:
    """DERIVED: the tracker with its tab strip drawn and its LIST not.

    This is the operator's live failure modelled exactly: LinkedIn's own Saved
    count reads 1, no row is present, and no empty state is present. Built from
    the EMPTY capture rather than the row one so that the only difference from
    a legitimately empty tab is the thing under test -- the empty state itself.
    """
    out = derive(markup("jobs_tracker_empty"), EMPTY_HEADING, "></h2>")
    # BOTH copies of the strip: LinkedIn draws it once per layout, and
    # parse_tracker_tabs reads whichever comes last.
    return derive(out, SAVED_TAB_ZERO, "Saved &#183; 1", count=-1)


#: The three states, in the order every table below reports them.
STATES = ["shell", "empty", "row"]


def page_html(which: str) -> str:
    if which == "shell":
        return shell()
    return markup(f"jobs_tracker_{which}")


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium.

    ``page.set_content`` touches no profile and makes no network request.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        chromium = await pw.chromium.launch(headless=True)
        try:
            page = await chromium.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await chromium.close()


class ServedPage:
    """A REAL Playwright page whose ``goto`` serves frozen local markup.

    The point of it is that everything else on the page is genuine: the
    readiness wait runs a real locator, ``read_tracker_evidence`` counts real
    anchors, and ``harvest_linked_cards`` executes its real JS over a real DOM.
    A stub page cannot reproduce this defect at all -- it has no ``locator``,
    so the wait degrades to its instrument-failed value, which is correct
    behaviour and useless as a reproduction.
    """

    def __init__(self, page, html: str):
        self._page = page
        self._html = html
        self.url = ""

    async def goto(self, url: str, **kwargs) -> None:
        self.url = url
        await self._page.set_content(
            self._html, wait_until="domcontentloaded", timeout=60_000
        )

    def __getattr__(self, name):
        return getattr(self._page, name)


@asynccontextmanager
async def served(html: str, monkeypatch):
    """Point BROWSER at a real page serving ``html``, for one call."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        chromium = await pw.chromium.launch(headless=True)
        try:
            wrapped = ServedPage(await chromium.new_page(), html)

            @asynccontextmanager
            async def fake_session():
                yield wrapped

            async def fake_goto(target_page, url, **kwargs):
                await target_page.goto(url)
                return target_page.url

            monkeypatch.setattr(browser_module.BROWSER, "session", fake_session)
            monkeypatch.setattr(browser_module.BROWSER, "goto", fake_goto)
            monkeypatch.setattr(
                type(browser_module.BROWSER),
                "last_settle",
                property(lambda self: dict(SETTLED_EARLY)),
            )
            yield wrapped
        finally:
            await chromium.close()


class UnreadablePage:
    """A page whose every locator raises something that is NOT a timeout."""

    def locator(self, selector: str):
        raise RuntimeError("browser is gone")

    async def inner_text(self, selector: str) -> str:
        raise RuntimeError("browser is gone")


# ---------------------------------------------------------------------------
# 1. The anchor, and the anchor it is not
# ---------------------------------------------------------------------------

#: MEASURED over the three states. The SHELL's zero is the whole property: an
#: anchor that cannot report zero in the state the wait exists to detect
#: certifies nothing.
EXPECTED_ANCHOR_HITS = [0, 1, 2]

#: What the TAB STRIP reports over the same three, kept as an executable
#: contrast rather than as a sentence in a comment. It is the obvious anchor
#: and it is wrong in the dangerous direction.
TAB_STRIP_SELECTOR = 'main a[href*="/jobs-tracker/"]'


async def test_the_tracker_anchor_separates_a_drawn_list_from_a_shell():
    """The selector, driven over shell, empty and row.

    SHOWN FAILING by swapping the anchor to the tab strip, which is the
    mistake a reader would make from the markup alone::

        AssertionError: [1, 1, 4] != [0, 1, 2]
        the tab strip is present on the SHELL, whose list never drew

    That is the dangerous direction: it reports READY in precisely the state
    the wait exists to detect. It is also not hypothetical -- the six live
    failures on 2026-08-30 all reported LinkedIn's own tab count, so the strip
    had demonstrably drawn while the list had not.
    """
    hits = []
    for which in STATES:

        async def work(page, _w=which):
            return int(await page.locator(dom.tracker_list_selector()).count())

        hits.append(await _with_html(page_html(which), work))
    assert hits == EXPECTED_ANCHOR_HITS, (
        f"{hits} != {EXPECTED_ANCHOR_HITS}; the anchor no longer separates a "
        "drawn list from a shell"
    )


async def test_the_tab_strip_would_have_been_the_wrong_anchor():
    """The contrast, asserted rather than described.

    SHOWN FAILING by pointing this at ``dom.tracker_list_selector()``, which
    is the assertion above and reports 0 on the shell::

        AssertionError: assert 0 > 0
    """

    async def work(page):
        return int(await page.locator(TAB_STRIP_SELECTOR).count())

    on_shell = await _with_html(shell(), work)
    assert on_shell > 0, (
        "the tab strip is supposed to be PRESENT on the shell -- that is why "
        "it cannot be the readiness anchor. If this fails the contrast has "
        "gone stale and the docstring above is no longer true."
    )


# ---------------------------------------------------------------------------
# 2. The disjunction, and what each half buys
# ---------------------------------------------------------------------------


async def test_an_empty_tab_is_not_delayed(monkeypatch):
    """A legitimately empty tab satisfies the wait at once.

    THIS IS THE WHOLE REASON THE ANCHOR IS A DISJUNCTION. Waiting only for a
    row would spend the full bound on every empty tab -- and the operator has
    two of them.

    SHOWN FAILING by dropping the empty half, which is the obvious anchor::

        AssertionError: attached=False after 304ms of a 300ms bound
        waiting only for rows makes an empty tab pay the full ceiling
    """
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async def work(page):
        return await dom.wait_for_tracker_list(page)

    verdict = await _with_html(markup("jobs_tracker_empty"), work)
    assert verdict["attached"] is True, verdict
    assert verdict["waited_ms"] < 300, (
        f"attached={verdict['attached']} after {verdict['waited_ms']}ms of a "
        "300ms bound; an empty tab is paying the ceiling"
    )


async def test_the_empty_half_is_derived_from_shape_and_not_copied():
    """Every marker ``shape`` owns is waited on, without being written twice.

    SHOWN FAILING by hardcoding the two markers in ``tracker_list_selector``::

        AssertionError: 'Nothing saved yet' is not waited on
        the selector holds a copy of the markers instead of deriving them
    """
    for marker in shape.TRACKER_EMPTY_MARKERS:
        assert f'"{marker}"' in dom.tracker_list_selector(), marker


async def test_a_marker_added_to_shape_is_waited_on_immediately(monkeypatch):
    """The derivation, driven rather than asserted about.

    SHOWN FAILING by the same hardcoding mutation as above::

        AssertionError: assert 'Nothing saved yet' in 'main a[href*=...]'
    """
    monkeypatch.setattr(
        shape, "TRACKER_EMPTY_MARKERS", ("No jobs here", "Nothing saved yet")
    )
    assert "Nothing saved yet" in dom.tracker_list_selector()


async def test_the_row_selector_in_the_note_has_not_drifted():
    """``shape`` names the selector; ``dom`` owns it. They must agree.

    ``shape`` imports no sibling module, so the string is written down twice
    by necessity. This is the guard that makes that safe.

    SHOWN FAILING by editing either copy::

        AssertionError: 'main a[href*="/jobs/view/"]' != 'main a[href*="/jobs/"]'
    """
    assert shape.TRACKER_ROW_LINK_NOTE == dom.TRACKER_ROW_LINK


# ---------------------------------------------------------------------------
# 3. Three-valued, and the third value is not decoration
# ---------------------------------------------------------------------------


async def test_the_shell_is_a_finding_and_says_so(monkeypatch):
    """A bound spent with nothing drawn is a FINDING about the page.

    SHOWN FAILING by anchoring the wait on the tab strip, which resolves on
    the shell::

        AssertionError: attached is True, so a page that never drew its list
        was reported ready
    """
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async def work(page):
        return await dom.wait_for_tracker_list(page)

    verdict = await _with_html(shell(), work)
    assert verdict["attached"] is False, verdict
    assert verdict["failure"] == "TimeoutError", verdict
    assert verdict["waited_ms"] >= 300, verdict


async def test_a_broken_readiness_check_is_not_a_finding():
    """A locator that RAISES says nothing about LinkedIn. None, never False.

    Collapsing this into False would report a broken instrument as a finding
    about the page -- the same class of error as a gate printing an unmeasured
    reversibility claim, and the exact mutation that came back green on first
    pass in the save wave.

    SHOWN FAILING by treating every exception as a timeout::

        AssertionError: attached is False, so an instrument failure was
        reported as evidence that the list did not draw
    """
    verdict = await dom.wait_for_tracker_list(UnreadablePage())
    assert verdict["attached"] is None, verdict
    assert verdict["failure"] == "RuntimeError", verdict
    assert "says nothing about the page" in verdict["why"]


# ---------------------------------------------------------------------------
# 4. The evidence -- counts, never text
# ---------------------------------------------------------------------------

#: MEASURED over the three states: (anchors_total, rows_matching).
EXPECTED_EVIDENCE = {"shell": (2, 0), "empty": (2, 0), "row": (6, 2)}


async def test_the_evidence_counts_what_was_actually_there():
    """The anchor walk, driven over all three states.

    THE SHELL AND THE EMPTY PAGE AGREE HERE (2 links, 0 rows) and that is the
    point rather than a defect: a link count alone cannot separate them, which
    is exactly why the note refuses to read one without the readiness verdict
    beside it, and why no threshold on this number is asserted anywhere.

    SHOWN FAILING by counting all anchors on the document instead of under
    <main>::

        AssertionError: ('row', 8, 2) != ('row', 6, 2)
    """
    for which in STATES:

        async def work(page):
            return await dom.read_tracker_evidence(page)

        got = await _with_html(page_html(which), work)
        assert got["main_present"] is True, (which, got)
        assert got["scan_complete"] is True, (which, got)
        assert (got["anchors_total"], got["rows_matching"]) == EXPECTED_EVIDENCE[
            which
        ], (which, got)


async def test_the_evidence_reports_unknown_rather_than_zero_when_it_cannot_look():
    """A page that cannot be read must not come back looking like an empty one.

    SHOWN FAILING by initialising the counts to 0 instead of None::

        AssertionError: main_present is False, which claims the page drew no
        <main> -- the strongest thing this evidence could possibly say, from a
        read that never happened
    """
    got = await dom.read_tracker_evidence(UnreadablePage())
    assert got["main_present"] is None, got
    assert got["anchors_total"] is None, got
    assert got["rows_matching"] is None, got
    assert got["scan_complete"] is False, got


async def test_a_page_that_cannot_be_read_says_so_in_the_note():
    """And the note built from it claims nothing.

    SHOWN FAILING by letting the unknown branch fall through to the counted
    sentence::

        AssertionError: 'WHAT WAS ON THE PAGE: a <main> carrying None
        characters and None links' -- a measurement rendered out of nothing
    """
    note = shape.tracker_read_note(
        await dom.read_tracker_evidence(UnreadablePage()),
        await dom.wait_for_tracker_list(UnreadablePage()),
        SETTLED_EARLY,
    )
    assert "WHAT WAS ON THE PAGE IS UNKNOWN" in note, note
    assert "READINESS CHECK ITSELF DID NOT COMPLETE" in note, note


# ---------------------------------------------------------------------------
# 5. The order, which is the whole of the fix's value
# ---------------------------------------------------------------------------


async def test_the_wait_runs_before_the_rows_are_harvested(monkeypatch):
    """Readiness first, harvest second. The other order buys nothing.

    After the cards have been harvested, waiting for the list changes nothing
    about what was read -- it would spend up to ten seconds to produce a field
    describing a page that had already been parsed.

    SHOWN FAILING by moving the wait below the harvest in ``_read_tracker``::

        AssertionError: ['harvest', 'wait'] != ['wait', 'harvest']
    """
    order: list[str] = []
    real_wait = dom.wait_for_tracker_list
    real_harvest = dom.harvest_linked_cards

    async def spy_wait(page):
        order.append("wait")
        return await real_wait(page)

    async def spy_harvest(page, **kwargs):
        order.append("harvest")
        return await real_harvest(page, **kwargs)

    monkeypatch.setattr(dom, "wait_for_tracker_list", spy_wait)
    monkeypatch.setattr(dom, "harvest_linked_cards", spy_harvest)
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async with served(shell(), monkeypatch):
        await linkedin_saved_jobs(limit=25)

    assert order == ["wait", "harvest"], order


# ---------------------------------------------------------------------------
# 6. End to end -- the refusal the operator actually met
# ---------------------------------------------------------------------------


async def test_the_refusal_the_operator_saw_now_says_when_it_looked(monkeypatch):
    """``linkedin_saved_jobs`` over the DERIVED shell, through the real tool.

    Everything but the navigation is genuine here: a real DOM, the real
    readiness wait, the real anchor walk, and the real harvest JS returning a
    real zero. The sentence the operator met is reproduced first, so this fails
    at the defect rather than at a missing attribute.

    SHOWN FAILING against the unfixed production code, which produced the
    first two assertions and not the third::

        assert "no saved jobs could be read" in message      # passes
        assert "Saved tab says 1" in message                 # passes
    >   assert "WHAT WAS ON THE PAGE" in message, message
    E   AssertionError: no saved jobs could be read, and the page does not
    E   corroborate an empty list: LinkedIn's own Saved tab says 1, and no
    E   empty state was drawn. Reporting nothing here would be
    E   indistinguishable from you genuinely having none, so it is reported as
    E   a failure instead.
    """
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async with served(shell(), monkeypatch):
        result = await linkedin_saved_jobs(limit=25)

    message = str(result.get("message") or "")
    assert result.get("error") == "extraction_failed", result
    # The refusal the operator met, unchanged.
    assert "no saved jobs could be read" in message, message
    assert "Saved tab says 1" in message, message
    assert "no empty state was drawn" in message, message
    # And the evidence it used to throw away.
    assert "WHAT WAS ON THE PAGE" in message, message
    assert "NEVER RESOLVED" in message, message
    assert shape.SETTLE_EARLY in message, message


async def test_a_drawn_empty_tab_is_still_reported_empty_and_not_refused(
    monkeypatch,
):
    """Behaviour did not change on the path that already worked.

    The empty capture's own Saved count is 0 and it draws its empty state, so
    this is the corroborated-empty case -- and it must stay a successful empty
    list rather than becoming a refusal because a new wait was added.

    SHOWN FAILING by making the wait's False branch raise instead of report::

        AssertionError: {'error': 'extraction_failed', ...} -- an empty tab
        was turned into a failure by the readiness wait
    """
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async with served(markup("jobs_tracker_empty"), monkeypatch):
        result = await linkedin_saved_jobs(limit=25)

    assert "error" not in result, result
    assert result["empty"] is True, result
    assert result["empty_state"] == "No jobs here", result
    assert result["results"] == [], result


async def test_the_wait_is_reported_and_never_gates(monkeypatch):
    """A list that never resolved does NOT by itself refuse a read.

    The wait reports; ``empty_is_believable`` decides. That separation is what
    keeps a future LinkedIn rename of the empty-state wording from turning
    every legitimately empty tab into an error -- the wait would time out and
    the read would still succeed on LinkedIn's own count plus a marker the
    text parser still matched.

    SHOWN FAILING by raising on ``attached is False``::

        ExtractionFailedError: the list did not resolve
    """
    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)
    # An empty tab whose empty-state ELEMENT the anchor cannot see, while the
    # text parser still can: the marker is split across two nodes.
    split = derive(
        markup("jobs_tracker_empty"), EMPTY_HEADING, "><span>No jobs</span> here</h2>"
    )

    async with served(split, monkeypatch):
        result = await linkedin_saved_jobs(limit=25)

    assert "error" not in result, result
    assert result["empty"] is True, result


# ---------------------------------------------------------------------------
# 7. The write gate reads the same page and inherits the same wait
# ---------------------------------------------------------------------------


async def test_the_saved_state_read_carries_the_evidence_too(monkeypatch):
    """``unsave_job`` takes its DIRECTION from this read, so it matters more.

    A saved list read before it drew does not merely produce an empty answer
    for the gate -- it produces ``unknown``, and the gate refuses. Measured
    2026-08-30, that is exactly what the operator met.

    SHOWN FAILING before ``_read_saved_state`` was given the note::

        assert state == "unknown"                           # passes
    >   assert "WHAT WAS ON THE PAGE" in why, why
    E   AssertionError: no saved rows could be read AND the page does not
    E   corroborate an empty list: the Saved tab count reads 1 and the empty
    E   state (None) is what would have to show. Nothing here distinguishes an
    E   empty list from a read that failed.
    """
    from linkedin_server import writes

    monkeypatch.setattr(dom, "TRACKER_LIST_TIMEOUT_MS", 300)

    async def work(page):
        return await writes._read_saved_state(page, "4423880462")

    state, why = await _with_html(shell(), work)
    assert state == "unknown", (state, why)
    assert "WHAT WAS ON THE PAGE" in why, why
    assert "NEVER RESOLVED" in why, why


async def test_the_refusal_never_quotes_a_row(monkeypatch):
    """COUNTS, NEVER TEXT. A tracker row names a company and a job.

    The row capture carries a real-shaped employer and title; neither may
    reach a diagnostic. The save sweep took the same ruling, for the same
    reason.

    SHOWN FAILING by adding the harvested row texts to the evidence payload::

        AssertionError: 'Ashgrove Systems' leaked into the refusal note
    """

    async def work(page):
        return shape.tracker_read_note(
            await dom.read_tracker_evidence(page),
            await dom.wait_for_tracker_list(page),
            SETTLED_EARLY,
        )

    note = await _with_html(markup("jobs_tracker_row"), work)
    for secret in ("Ashgrove Systems", "Platform Integration Engineer", "Fairhaven"):
        assert secret not in note, f"{secret!r} leaked into the refusal note"
