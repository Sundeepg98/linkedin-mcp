"""The read-only route to the save control, and why it had to exist.

THE CIRCULARITY THIS BREAKS. ``shape.SAVE_LABELS`` holds ONE row -- the OFF
state, ``"Save the job"``. ``writes.anchor_label_for`` reads that table
BACKWARDS, from the state an action is valid from to the accessible name the
control would have to be wearing, so ``save_job`` has an anchor and
``unsave_job`` has none and refuses. The missing row could not be measured
because nothing was saved on the account to observe it on: no posting anywhere
would draw the ON label.

That stopped being true on 2026-08-30, when the operator authorised the first
save in this server's life. It did NOT stop being circular. The only instrument
that could see the ON label -- the sweep behind ``writes.perform``'s refusal --
lives in gate 5, reachable only by redeeming a confirm token. So re-measuring
the label cost ANOTHER supervised write, and a toggle whose ON label can only
be read by toggling it is a measurement nobody should have to pay twice for.

``linkedin_job_detail`` already loads the posting and already reads the FOLLOW
control off it. Reading the SAVE control off the same rendering costs no
navigation and no write. That is the whole change.

WHAT IS NOT DONE HERE, deliberately. No row is added to ``shape.SAVE_LABELS``.
The label a live posting reports through this route still has to be OBSERVED
before it is written down, and the tests below assert that the vocabulary is
untouched and that a name reported here cannot become a click by having been
reported. ``test_the_on_label_would_be_reported_if_a_posting_wore_it`` is the
proof that the route WORKS -- driven over a DERIVED page, which is a model of
the state and never evidence about LinkedIn.

Every reading is taken by the REAL reader over a REAL parsed DOM in a local
headless Chromium. Nothing here reaches the network or an account. Every page
is DERIVED from ``fixtures/job_detail_hydrated.html`` by an explicit, asserted
edit, and is labelled DERIVED where it is used.

EVERY TEST HERE WAS SHOWN FAILING at the mutation named in its docstring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape
from linkedin_server.server import _read_save_control_state

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The one string every derivation below is anchored on.
SAVE_ATTR = 'aria-label="Save the job"'

#: The label the operator's first save reported through ``perform``'s post-click
#: re-read, on job 4423880462 at about 18:30 IST on 2026-08-30. ONE reading, and
#: it is used here ONLY as the string a derived page wears -- nothing below
#: treats it as measured vocabulary, and it is deliberately NOT in
#: ``shape.SAVE_LABELS``.
REPORTED_ON_LABEL = "Unsave the job"

#: The other plausible ON label, and the one the production comment in
#: ``shape.SAVE_LABELS`` names as ambiguous about direction: it can be read as
#: a state ("this job is saved") or as an imperative. Kept here so the route is
#: shown reporting a name WITHOUT the report settling what the name means.
AMBIGUOUS_ON_LABEL = "Saved"

#: A member name that satisfies the SUBSTRING rule this reader used to run and
#: not the whole-word rule it runs now. Invented; it names nobody.
MEMBER_NAME = "Savita Krishnan"


def base() -> str:
    return (FIXTURE_DIR / "job_detail_hydrated.html").read_text(encoding="ascii")


def derive(old: str, new: str, *, src: str | None = None) -> str:
    """One DERIVED page, plus a receipt that the edit actually landed."""
    src = base() if src is None else src
    out = src.replace(old, new, 1)
    assert out != src, (
        f"the derivation anchored on {old!r} changed nothing, so this variant "
        "is the base fixture wearing another name. Repoint the anchor, and do "
        "NOT delete this assertion."
    )
    return out


async def _with_html(html: str, work):
    """Run ``work(page)`` over frozen markup in a LOCAL headless Chromium."""
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        chromium = await pw.chromium.launch(headless=True)
        try:
            page = await chromium.new_page()
            await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
            return await work(page)
        finally:
            await chromium.close()


async def read(html: str) -> dict:
    return await _with_html(html, _read_save_control_state)


# ---------------------------------------------------------------------------
# 1. The measured state still reads as the measured state
# ---------------------------------------------------------------------------


async def test_the_captured_posting_reads_not_saved():
    """The one row in the table, end to end through the read path.

    SHOWN FAILING by pointing ``dom.SAVE_CONTROL`` at another label::

        AssertionError: {'state': 'unknown', ...} != not_saved
    """
    verdict = await read(base())
    assert verdict["state"] == "not_saved", verdict
    assert repr(SAVE_ATTR.split('"')[1]) in verdict["why"], verdict


async def test_a_known_state_does_not_pay_for_a_second_sweep():
    """The wider look runs ONLY where the first read is about to say nothing.

    A state that came back KNOWN was read off a label the verdict already
    names, so sweeping there is a round trip spent on repetition. This is the
    rule ``writes._live_control`` already runs on, asserted rather than
    restated.

    SHOWN FAILING by sweeping unconditionally::

        AssertionError: 'observed' in {'state': 'not_saved', 'why': ...,
        'observed': {...}} -- a known state paid for a sweep it cannot use
    """
    verdict = await read(base())
    assert "observed" not in verdict, verdict


# ---------------------------------------------------------------------------
# 2. THE POINT: an unmeasured label is REPORTED rather than guessed at
# ---------------------------------------------------------------------------


async def test_the_on_label_would_be_reported_if_a_posting_wore_it():
    """DERIVED: the save control wearing the label the first save reported.

    THIS IS THE WHOLE DELIVERABLE OF THE READ-ONLY ROUTE. It shows that a
    posting drawing an unmeasured save label comes back as ``unknown`` PLUS the
    name that was actually on the page -- so the ON label can be re-measured by
    calling a READ tool on a saved posting, as many times as anybody likes,
    instead of by performing another write.

    It does NOT establish that LinkedIn's ON label is this string. The page
    here wears it because this test put it there.

    SHOWN FAILING by dropping the ``observed`` sweep from
    ``_read_save_control_state``::

        AssertionError: 'observed' not in {'state': 'unknown', 'why': "the
        control is labelled None..."} -- the refusal reports nothing it saw
    """
    verdict = await read(derive(SAVE_ATTR, f'aria-label="{REPORTED_ON_LABEL}"'))
    assert verdict["state"] == shape.SAVE_UNKNOWN, verdict
    assert verdict["observed"]["candidates"] == [REPORTED_ON_LABEL], verdict
    assert verdict["observed"]["matched_total"] == 1, verdict
    assert verdict["observed"]["scan_complete"] is True, verdict


async def test_an_ambiguous_label_is_reported_without_being_resolved():
    """DERIVED: the other plausible ON label. Reported, and still ``unknown``.

    The route REPORTS a name. It does not decide what the name MEANS, and the
    difference is the reason no table row is added by this wave: ``Saved`` can
    be read as a state or as an imperative, and a label mapped to the wrong
    state points a click at the opposite action.

    SHOWN FAILING by promoting a lone observed candidate to a state at the end
    of ``_read_save_control_state`` -- which is the shortcut a future session
    is likeliest to reach for, having just been handed the name::

        if len(verdict["observed"]["candidates"]) == 1:
            verdict["state"] = "saved"

        AssertionError: 'saved' != 'unknown' -- a name was promoted to a state
        by having been observed

    NOT reproducible by mutating ``shape.save_state``'s ``known is None``
    branch, and that was measured rather than assumed. ``dom.SAVE_CONTROL`` is
    built from ``SAVE_LABELS_SEEN``, which holds one string, so a page wearing
    any other label matches ZERO elements and ``save_state`` returns from its
    ``count == 0`` guard without ever reaching the unrecognised-label branch.
    That branch is unreachable through this route today -- it needs
    ``SAVE_LABELS_SEEN`` to hold a name ``SAVE_LABELS`` does not map -- so
    nothing here guards it and this docstring does not pretend otherwise.
    """
    verdict = await read(derive(SAVE_ATTR, f'aria-label="{AMBIGUOUS_ON_LABEL}"'))
    assert verdict["state"] == shape.SAVE_UNKNOWN, verdict
    assert verdict["observed"]["candidates"] == [AMBIGUOUS_ON_LABEL], verdict


async def test_a_control_renamed_off_the_vocabulary_is_a_different_finding():
    """DERIVED: renamed clean off the save vocabulary. Zero candidates.

    A rename to a word outside the set shows up as zero candidates against a
    NON-ZERO scan, which is itself the finding and a bigger one than a rename
    inside the vocabulary.

    SHOWN FAILING by reporting every labelled control instead of the
    save-worded ones::

        AssertionError: ['Bookmark this job', 'Dismiss', ...] != []
    """
    verdict = await read(derive(SAVE_ATTR, 'aria-label="Bookmark this job"'))
    assert verdict["state"] == shape.SAVE_UNKNOWN, verdict
    assert verdict["observed"]["candidates"] == [], verdict
    assert verdict["observed"]["buttons_total"] > 0, verdict


# ---------------------------------------------------------------------------
# 3. Reporting is not vocabulary, and reporting is not a click
# ---------------------------------------------------------------------------


async def test_the_vocabulary_is_untouched_by_this_route():
    """No row was added to either table by adding a way to read them.

    SHOWN FAILING by writing the observed label into ``shape.SAVE_LABELS``::

        AssertionError: {'Save the job': 'not_saved', 'Unsave the job':
        'saved'} != {'Save the job': 'not_saved'}
    """
    assert shape.SAVE_LABELS == {"Save the job": "not_saved"}
    assert set(dom.SAVE_LABELS_SEEN) == {"Save the job"}


async def test_a_reported_label_still_cannot_become_a_click():
    """The selector refuses every name outside the measured set.

    This is the property that makes reporting SAFE. It is asserted here as
    well as in the writes tests because this route is a NEW way for a name to
    reach a reader, and the guard has to hold on the new path too.

    SHOWN FAILING by widening ``dom.SAVE_LABELS_SEEN`` with the observed
    label::

        Failed: DID NOT RAISE ExtractionFailedError
    """
    from linkedin_server.errors import ExtractionFailedError

    for label in (REPORTED_ON_LABEL, AMBIGUOUS_ON_LABEL, "Bookmark this job"):
        with pytest.raises(ExtractionFailedError):
            dom.save_control_selector(label)


async def test_unsave_still_has_no_anchor_and_says_so():
    """``unsave_job`` is unchanged by this wave. Stated as an assertion.

    The read-only route makes the missing row MEASURABLE. It does not supply
    it, and until somebody has actually seen the live label this must keep
    returning None.

    SHOWN FAILING by adding the observed label to ``shape.SAVE_LABELS``::

        AssertionError: 'Unsave the job' is not None -- unsave acquired an
        anchor from a table row nobody measured
    """
    from linkedin_server import writes

    spec = writes.SANCTIONED_WRITES["linkedin_unsave_job"]
    assert spec.from_state == "saved", spec
    assert writes.anchor_label_for(spec) is None
    # And its measured sibling still has one, so this is a missing ROW rather
    # than a broken lookup.
    assert writes.anchor_label_for(
        writes.SANCTIONED_WRITES["linkedin_save_job"]
    ) == "Save the job"


# ---------------------------------------------------------------------------
# 4. Privacy -- a posting names people, and this route walks its controls
# ---------------------------------------------------------------------------


async def test_a_member_name_containing_sav_is_not_reported():
    """DERIVED: a hiring-team control named for a member whose name has "sav".

    The filter is a WHOLE WORD and not a substring, and the boundary is
    load-bearing: a job posting draws a hiring team and a "people also viewed"
    rail, so its accessible names include real members'.

    SHOWN FAILING by reverting the filter to ``"sav" in text.casefold()``::

        AssertionError: ['Savita Krishnan', 'Unsave the job'] != ['Unsave the
        job']
    """
    relabelled = derive(SAVE_ATTR, f'aria-label="{REPORTED_ON_LABEL}"')
    with_member = derive(
        f'aria-label="{REPORTED_ON_LABEL}"',
        f'aria-label="{REPORTED_ON_LABEL}"></button>'
        f'<button type="button" aria-label="{MEMBER_NAME}"',
        src=relabelled,
    )
    verdict = await read(with_member)
    assert verdict["observed"]["candidates"] == [REPORTED_ON_LABEL], verdict
    assert MEMBER_NAME not in str(verdict), verdict
