"""The description readiness wait, and the timing evidence a refusal now carries.

WHAT THIS FILE IS ABOUT, stated as the defect rather than as the feature.
``/jobs/view/<id>`` was believed to draw sometimes and not others -- blamed on
LinkedIn, on throttling, on expired postings, and on a second reader. It was
none of them. ``browser.goto`` settles every navigation like this::

    await page.goto(url, wait_until="domcontentloaded", ...)
    try:
        await page.wait_for_load_state("networkidle", timeout=settle_ms)
    except Exception:
        await page.wait_for_timeout(settle_ms)

There are exactly TWO possible settle durations and nothing between them. If
networkidle resolves the read is taken about a second after DOMContentLoaded,
before LinkedIn's client has fetched the description; if it times out, the flat
wait runs as well and the read lands about seven seconds in, on a drawn page.
Measured over 37 recorded loads the fast branch ran 28 times, with nothing
between 3 s and 6 s. Across the 15 reads whose outcome was recorded the split
was total: 13 of 13 early reads refused for a missing description, 2 of 2 late
reads drew the posting in full. **The `except` fallback did all the useful work
and only ran when the `try` failed.**

The full evidence is ``_audit/2026-08-30-jobs-view-reliability.md``.

WHY THE FIX IS A READINESS WAIT AND NOT A BIGGER NUMBER. The settle is binary
by construction, so nothing measured through the shipped build can distinguish
"2 s would be enough" from "6 s would be enough" -- every candidate sits inside
an unmeasured bracket of (1 s, 7 s]. Picking one would be a round number that
sounds safe, and it would tax every surface for one surface's missing check. A
readiness wait is correct precisely because it waits for the thing it needs and
no longer: ``test_a_ready_page_is_not_delayed`` below is what holds that.

EVERY TEST HERE WAS SHOWN FAILING at the mutation named in its docstring. The
mutations are applied at RUNTIME, against this module's own copies, so no
source file is edited to produce them.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from linkedin_server import dom, shape

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: All five job captures, in the order the reliability audit tabulates them.
#: The pair either side of the boundary is the point: ``job_detail_following``
#: carries the SLOT and not its content, which is the state this wait exists to
#: detect and the state the obvious anchor is blind to.
CAPTURES = [
    "job_detail_shell",
    "job_detail_following",
    "job_detail",
    "job_detail_hydrated",
    "job_detail_following_hydrated",
]

#: MEASURED, and re-counted independently before this shipped. The first two
#: have no drawn description; the last three do.
EXPECTED_ANCHOR_HITS = [0, 0, 1, 1, 1]

#: What the SLOT id reports over the same five, and the reason it is not the
#: anchor: it is drawn before its content, so it says READY on
#: ``job_detail_following``. Kept here as an executable contrast rather than a
#: sentence in a comment.
SLOT_ID_HITS = [0, 1, 1, 1, 1]

SLOT_ID_SELECTOR = 'main [id^="JobDetails_AboutTheJob_"]'


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium.

    Copied from ``test_job_detail_fixture.py`` rather than imported, because
    that module's copy is bound to its own three-fixture map and this file
    needs all five. ``page.set_content`` touches no profile and no network.
    """
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
    return (FIXTURE_DIR / f"{which}.html").read_text(encoding="ascii")


# ---------------------------------------------------------------------------
# 1. The anchor, and the anchor it is not
# ---------------------------------------------------------------------------


async def test_the_description_anchor_separates_drawn_from_not_drawn():
    """The selector, driven over all five captures.

    SHOWN FAILING by swapping the anchor to the slot id, which is the mistake
    a reader would make from the markup alone:

        AssertionError: [0, 1, 1, 1, 1] != [0, 0, 1, 1, 1]
        the slot id is present on job_detail_following, whose description
        is ABSENT

    That is the dangerous direction: it reports READY in precisely the state
    the wait exists to detect.
    """
    hits = []
    for which in CAPTURES:

        async def work(page):
            return int(await page.locator(dom.JOB_DESCRIPTION_SLOT).count())

        hits.append(await _with_html(markup(which), work))
    assert hits == EXPECTED_ANCHOR_HITS, dict(zip(CAPTURES, hits))


async def test_the_slot_id_would_have_been_the_wrong_anchor():
    """THE CONTRAST, executed rather than asserted in a comment.

    Without this, "the sdui attribute is the right anchor" is a claim with
    nothing behind it -- both selectors return 1 on three of the five captures
    and a reader could reasonably pick either. The whole difference lives on
    ``job_detail_following``, and this is where it is shown.
    """
    hits = []
    for which in CAPTURES:

        async def work(page):
            return int(await page.locator(SLOT_ID_SELECTOR).count())

        hits.append(await _with_html(markup(which), work))
    assert hits == SLOT_ID_HITS, dict(zip(CAPTURES, hits))
    # The two disagree on EXACTLY ONE capture, and that capture is the one
    # whose description is missing.
    disagreements = [
        which
        for which, a, b in zip(CAPTURES, EXPECTED_ANCHOR_HITS, SLOT_ID_HITS)
        if a != b
    ]
    assert disagreements == ["job_detail_following"], disagreements


# ---------------------------------------------------------------------------
# 2. The three outcomes
# ---------------------------------------------------------------------------


async def test_a_drawn_page_reports_attached():
    async def work(page):
        return await dom.wait_for_job_description(page)

    verdict = await _with_html(markup("job_detail_hydrated"), work)
    assert verdict["attached"] is True
    assert verdict["failure"] is None


@pytest.mark.parametrize("which", ["job_detail_shell", "job_detail_following"])
async def test_a_page_that_never_draws_the_description_is_reported_not_attached(
    which, monkeypatch
):
    """A page with no description: ``attached`` False, and NOTHING RAISED.

    SHOWN FAILING by making the wait re-raise instead of returning:

        playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout
        200ms exceeded.

    A raise here would be wrong twice over. The caller cannot then choose --
    ``read_job_posting`` would abort before reading anything, so the refusal
    would lose ``main_present`` and ``main_chars``, the two fields that tell a
    shell from a drawn page whose parse failed. And an exception carries no
    ``waited_ms``, so the refusal could not say the bound had actually been
    spent.

    The timeout is shortened here rather than the real ten seconds being
    spent. What is under test is the CLASSIFICATION, not the constant.
    """
    monkeypatch.setattr(dom, "JOB_DESCRIPTION_TIMEOUT_MS", 200)

    async def work(page):
        return await dom.wait_for_job_description(page)

    verdict = await _with_html(markup(which), work)
    assert verdict["attached"] is False
    assert verdict["failure"] == "TimeoutError"
    assert verdict["waited_ms"] >= 150, verdict
    assert "did not attach" in verdict["why"]


async def test_a_locator_failure_is_not_a_timeout():
    """A BROKEN INSTRUMENT IS NOT A FINDING ABOUT LINKEDIN.

    SHOWN FAILING against a bare ``except Exception: attached = False``, which
    is the shape this was nearly written as:

        AssertionError: assert False is None

    Under that mutation a closed page, a detached frame or a malformed
    selector all come back as "LinkedIn did not render this posting" -- a
    confident claim about a third party produced by our own bug. The same
    mutation came back green on first pass in the save wave, which is why this
    test exists rather than a comment saying to be careful.
    """

    class ExplodingPage:
        def locator(self, _selector):
            raise RuntimeError("frame detached")

    verdict = await dom.wait_for_job_description(ExplodingPage())
    assert verdict["attached"] is None
    assert verdict["failure"] == "RuntimeError"
    assert "says nothing about the page" in verdict["why"]


async def test_the_default_verdict_is_unknown_rather_than_a_finding():
    """The dict's own default, which no path should be able to leak as False.

    A path nobody thought about must not arrive claiming to have measured
    LinkedIn. Asserted by reading the function's source for the initialiser,
    because the behaviour itself is only reachable through the branches above.
    """
    import inspect

    source = inspect.getsource(dom.wait_for_job_description)
    initialiser = source.split("started = time.monotonic()")[0]
    assert '"attached": None,' in initialiser
    assert '"attached": False,' not in initialiser


# ---------------------------------------------------------------------------
# 3. The order, which is the whole of the wait's value
# ---------------------------------------------------------------------------


async def test_the_wait_runs_before_the_text_is_read(monkeypatch):
    """READINESS FIRST. After the text is read, waiting for it changes nothing.

    SHOWN FAILING by moving the wait below ``read_main_text``:

        AssertionError: ['read_main_text', 'wait'] != first
        the wait ran after the text was read, where it changes nothing

    A wait in the wrong place is not a weaker fix, it is a NON-fix that costs
    up to ten seconds and produces a field describing a page that was already
    parsed. Nothing about the returned dict would look different, which is
    exactly why this is pinned as ORDER rather than as output.
    """
    calls: list[str] = []
    real_wait = dom.wait_for_job_description
    real_text = dom.read_main_text

    async def spy_wait(page):
        calls.append("wait")
        return await real_wait(page)

    async def spy_text(page):
        calls.append("read_main_text")
        return await real_text(page)

    monkeypatch.setattr(dom, "wait_for_job_description", spy_wait)
    monkeypatch.setattr(dom, "read_main_text", spy_text)

    async def work(page):
        return await dom.read_job_posting(page)

    reading = await _with_html(markup("job_detail_hydrated"), work)
    assert calls[0] == "wait", calls
    assert "read_main_text" in calls, calls
    assert calls.index("wait") < calls.index("read_main_text"), calls
    # And the verdict reaches the caller, or the ordering would be pointless.
    assert reading["description_wait"]["attached"] is True


async def test_read_job_posting_reports_the_verdict_alongside_the_render_evidence():
    """``description_wait`` travels with ``main_present`` and ``main_chars``.

    The three answer different questions and a refusal needs all of them: did
    the page draw a main, how much text was in it, and had the description
    arrived by the time it was parsed.
    """

    async def work(page):
        return await dom.read_job_posting(page)

    reading = await _with_html(markup("job_detail_hydrated"), work)
    assert set(reading) >= {
        "identity",
        "detail",
        "main_present",
        "main_chars",
        "description_wait",
    }
    assert reading["main_present"] is True
    assert reading["main_chars"] > 0


# ---------------------------------------------------------------------------
# 4. A ready page is not delayed
# ---------------------------------------------------------------------------


async def test_a_ready_page_is_not_delayed():
    """THE REASON THIS IS A WAIT AND NOT A BIGGER SETTLE NUMBER.

    SHOWN FAILING against an unconditional floor -- ``wait_for_timeout(3500)``
    substituted for the element wait:

        AssertionError: assert 3502 < 2000
        a ready page paid the floor

    A flat floor would make this test red at the exact cost it exists to
    prevent: every surface paying for one surface's missing readiness check.
    The sibling wait, ``wait_for_save_control``, was measured at 27 ms on a
    ready page. The ceiling here is generous against a loaded CI box; what it
    rules out is a floor, not a slow machine.
    """

    async def work(page):
        started = time.monotonic()
        verdict = await dom.wait_for_job_description(page)
        return verdict, int((time.monotonic() - started) * 1000)

    verdict, elapsed = await _with_html(markup("job_detail_hydrated"), work)
    assert verdict["attached"] is True
    assert elapsed < 2000, elapsed
    assert verdict["waited_ms"] < 2000, verdict


# ---------------------------------------------------------------------------
# 5. The refusal can now say WHEN it looked
# ---------------------------------------------------------------------------

EARLY_SETTLE = {
    "branch": "networkidle_resolved",
    "settled_ms": 4,
    "settle_ms_configured": 3500,
}
LATE_SETTLE = {
    "branch": "networkidle_timed_out",
    "settled_ms": 7003,
    "settle_ms_configured": 3500,
}
NOT_ATTACHED = {
    "attached": False,
    "waited_ms": 10000,
    "timeout_ms": 10000,
    "failure": "TimeoutError",
    "why": "the description section did not attach within the bound",
}
ATTACHED = {
    "attached": True,
    "waited_ms": 31,
    "timeout_ms": 10000,
    "failure": None,
    "why": "the description section attached",
}
CHECK_FAILED = {
    "attached": None,
    "waited_ms": 2,
    "timeout_ms": 10000,
    "failure": "RuntimeError",
    "why": "the readiness check itself failed (RuntimeError)",
}


def test_the_refusal_names_the_settle_branch_and_the_wait():
    """Both pieces of timing evidence reach the human reading the refusal.

    SHOWN FAILING by dropping either argument from the note -- they are
    REQUIRED keyword arguments, so the mutation is a TypeError rather than a
    quieter, weaker sentence:

        TypeError: job_detail_failure_note() missing 1 required keyword-only
        argument: 'settle'

    Required rather than optional on purpose. An optional argument with a None
    default would let a future caller silently produce the old note, which is
    the note this whole change exists to retire.
    """
    note = shape.job_detail_failure_note(
        ["description"],
        main_present=True,
        main_chars=1300,
        description_wait=NOT_ATTACHED,
        settle=EARLY_SETTLE,
    )
    assert "networkidle_resolved" in note
    assert "4ms" in note
    assert "10000ms" in note
    assert "1300 characters" in note


def test_a_read_that_waited_and_found_nothing_is_reported_as_a_finding():
    """The case where "LinkedIn did not render this" is finally sayable.

    And the case where it is STILL not sayable without a caveat: a wrong
    anchor fails identically to a dead page, so the note must offer the rename
    as a live possibility with the action that distinguishes them.
    """
    note = shape.job_read_timing_note(NOT_ATTACHED, LATE_SETTLE)
    assert "NEVER" in note.upper()
    assert "RENAMED THE COMPONENT" in note
    assert "second posting" in note
    # It must NOT tell him to re-read: the wait already ran its course.
    assert "read the posting again" not in note.lower()


def test_a_check_that_failed_is_reported_as_evidence_for_neither():
    note = shape.job_read_timing_note(CHECK_FAILED, EARLY_SETTLE)
    assert "nothing here is evidence" in note
    assert "RuntimeError" in note
    # An instrument failure asks for a re-read, not a conclusion.
    assert "read the posting again" in note.lower()
    assert "RENAMED" not in note


def test_a_drawn_page_whose_fields_are_missing_is_named_a_parser_problem():
    """The fourth combination, and the one that used to be unsayable.

    A page that DID draw and whose fields still could not be parsed is a bug in
    this package, not a timing problem and not a LinkedIn problem. Before the
    readiness wait existed, that case was indistinguishable from a read taken
    too early -- and it was the case the old note's three theories omitted.
    """
    note = shape.job_read_timing_note(ATTACHED, EARLY_SETTLE)
    assert "PARSER problem" in note
    assert "not the read-too-early failure" in note


def test_an_unrecorded_settle_does_not_invent_a_number():
    """Before the first navigation ``last_settle`` is empty. Say so, do not guess.

    A note reading "settled after Nonems" would be a fabricated measurement,
    which is the class of confident string this package keeps refusing to
    print.
    """
    note = shape.job_read_timing_note(NOT_ATTACHED, {})
    assert "not recorded" in note
    assert "Nonems" not in note


def test_a_verdict_that_is_neither_true_nor_false_is_treated_as_unknown():
    """A STRAY VALUE MUST NOT REACH THE "the page drew fine" BRANCH.

    SHOWN FAILING against ``if attached is None:``, which is how this was first
    written:

        AssertionError: assert 'nothing here is evidence' in 'The navigation
        settled on ... and the description DID attach (0ms), so the page had
        drawn by the time it was parsed. ...'

    Under that version anything other than exactly ``None`` -- a string, a 0, a
    typo in a future caller -- falls through both guards into the last branch
    and is reported as a page that rendered. That is a confident claim about
    LinkedIn manufactured out of a local mistake, which is the same failure
    class as the read-too-early refusals this whole change exists to retire,
    one level down.

    ``wait_for_job_description`` cannot produce such a value today. This is a
    guard on the SHAPE rather than on the instance.
    """
    for stray in ("unknown", 0, 1, "", []):
        note = shape.job_read_timing_note(
            {"attached": stray, "waited_ms": 0, "failure": None}, EARLY_SETTLE
        )
        assert "nothing here is evidence" in note, (stray, note)
        assert "DID attach" not in note, (stray, note)
