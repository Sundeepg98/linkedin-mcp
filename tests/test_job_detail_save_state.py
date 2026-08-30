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

WHAT THIS MODULE SAID UNTIL 2026-08-30, and what happened next. It said "no row
is added to ``shape.SAVE_LABELS``. The label a live posting reports through this
route still has to be OBSERVED before it is written down." That was the right
restraint at the time: the label rested on ONE reading, taken by the write path
on the operator's first save, and this repo had been burned five times that day
by single readings of a page.

The route then produced the observations that lifted it. Called twice on the
saved posting, sixty seconds apart, and once more later, it returned
``candidates: ["Unsave the job"]`` every time, on a page reporting 32 buttons
drawn -- so four readings across two independent routes, three of them costing
no write. The row went into ``shape.SAVE_LABELS`` and ``dom.SAVE_LABELS_SEEN``
on that evidence.

THE TESTS BELOW MOVED WITH IT. Five of them asserted the un-widened vocabulary
and are replaced by successors asserting what is now true -- visibly successors,
because a suite that still pinned the old refusal would be pinning a claim the
evidence no longer supports. What did NOT move: reporting a name still cannot
become a click, and a label outside the measured pair is still refused rather
than guessed at. Those are the properties that made it safe to publish the label
before anybody had decided what it meant, and they are unchanged.

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

#: The ON label, MEASURED four times on 2026-08-30 across two routes and now in
#: ``shape.SAVE_LABELS``. It was a bare string in this file before that; it is
#: read from the table now, so a future edit to the table cannot leave this
#: module testing a label the server no longer knows.
MEASURED_ON_LABEL = "Unsave the job"

#: The other spelling this repo considered plausible for the ON state, and the
#: one the production comment names as ambiguous about direction: it reads
#: equally as a state ("this job is saved") and as an imperative. It was NOT
#: what LinkedIn draws, and it stays here as the worked example of a name the
#: route REPORTS without the report settling anything -- which is the property
#: that has to survive the vocabulary growing.
UNMEASURED_LABEL = "Saved"

#: A name outside the save vocabulary entirely, for the case that is a bigger
#: finding than a rename inside it.
RENAMED_AWAY_LABEL = "Bookmark this job"

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


async def test_a_saved_posting_now_reads_saved():
    """THE SUCCESSOR to ``test_the_on_label_would_be_reported_if_a_posting_wore_it``.

    That test drove a page wearing the ON label and asserted it came back
    ``unknown`` PLUS the observed name -- because the label was unmeasured and
    the route's job was to REPORT it. The route did its job: the readings it
    produced are what put the row in ``shape.SAVE_LABELS``, and a page wearing
    that label is now simply READ.

    Note what this does not need any more. There is no ``observed`` block here,
    and its absence is the improvement: the sweep is a diagnostic for a name
    nobody can name, and a recognised control does not need one.

    DERIVED, and that is worth flagging rather than forgetting: no fixture in
    this repo carries the ON label. Every capture predates the operator's first
    save, so a saved posting has to be modelled by relabelling the control. The
    live readings that justify the row were taken against LinkedIn, not here.

    SHOWN FAILING by removing the row from ``shape.SAVE_LABELS``::

        AssertionError: assert 'unknown' == 'saved'
    """
    verdict = await read(derive(SAVE_ATTR, f'aria-label="{MEASURED_ON_LABEL}"'))
    assert verdict["state"] == "saved", verdict
    assert repr(MEASURED_ON_LABEL) in verdict["why"], verdict
    assert "observed" not in verdict, verdict


async def test_the_unsaved_and_saved_readings_are_each_other_s_inverse():
    """Both states, off the same base capture, differing by one attribute.

    A toggle reader that returns the same answer either way is the failure
    this whole design exists to prevent, and asserting the two states in
    separate tests would not catch a reader that had collapsed them.

    SHOWN FAILING by mapping both labels to the same state in
    ``shape.SAVE_LABELS``::

        AssertionError: assert 'saved' != 'saved'
    """
    off = await read(base())
    on = await read(derive(SAVE_ATTR, f'aria-label="{MEASURED_ON_LABEL}"'))
    assert off["state"] == "not_saved", off
    assert on["state"] == "saved", on
    assert off["state"] != on["state"]


async def test_an_ambiguous_label_is_reported_without_being_resolved():
    """DERIVED: the other plausible ON label. Reported, and still ``unknown``.

    The route REPORTS a name. It does not decide what the name MEANS, and that
    separation SURVIVED the vocabulary growing -- which is the point of keeping
    this test rather than retiring it with its siblings. ``Saved`` is still not
    in the table, and it is still not resolved to a state by having turned up
    in a sweep.

    IT IS ALSO THE COUNTERFACTUAL. ``Saved`` was one of the two spellings this
    repo named as plausible for the ON state. Had the measurement come back
    this string, the row would still be missing on 2026-08-30: it reads equally
    as a state and as an imperative, where ``Unsave the job`` names its own
    inverse. The row went in because of WHICH label was measured, not because a
    label was measured.

    SHOWN FAILING by promoting a lone observed candidate to a state at the end
    of ``_read_save_control_state`` -- which is the shortcut a future session
    is likeliest to reach for, having just been handed the name::

        if len(verdict["observed"]["candidates"]) == 1:
            verdict["state"] = "saved"

        AssertionError: 'saved' != 'unknown' -- a name was promoted to a state
        by having been observed

    NOT reproducible by mutating ``shape.save_state``'s ``known is None``
    branch, and that was measured rather than assumed. ``dom.SAVE_CONTROL`` is
    built from ``SAVE_LABELS_SEEN``, so a page wearing a label outside it
    matches ZERO elements and ``save_state`` returns from its ``count == 0``
    guard without ever reaching the unrecognised-label branch. That stayed true
    when the tables were widened on 2026-08-30, because they were widened
    TOGETHER -- the branch becomes reachable only if one is widened and the
    other is not, which
    ``test_writes.py::test_the_selector_and_the_vocabulary_cannot_drift_apart``
    is what catches.
    """
    verdict = await read(derive(SAVE_ATTR, f'aria-label="{UNMEASURED_LABEL}"'))
    assert verdict["state"] == shape.SAVE_UNKNOWN, verdict
    assert verdict["observed"]["candidates"] == [UNMEASURED_LABEL], verdict
    assert UNMEASURED_LABEL not in shape.SAVE_LABELS, (
        "the counterfactual label has been written into the table; this test "
        "no longer tests what it says it tests"
    )


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


async def test_the_vocabulary_grew_by_exactly_the_measured_row():
    """THE SUCCESSOR to ``test_the_vocabulary_is_untouched_by_this_route``.

    That test asserted BOTH tables held exactly one row, and it was the guard
    that stopped this route from quietly promoting a name it had merely
    reported. It was correct while the label rested on a single reading taken
    by the write path.

    The restraint was DISCHARGED, not abandoned: three read-only readings
    through this route agreed with that first one, and the row went in on the
    strength of four observations across two independent routes. So the claim
    worth pinning is no longer "nothing was added" -- it is "exactly the
    measured row was added, and nothing else came with it".

    THE COUNTERFACTUALS ARE THE POINT of the second half. ``Saved`` was named
    as equally plausible and is NOT here; the sweep has reported it in this
    very file and reporting did not admit it.

    SHOWN FAILING by adding any further label to either table::

        AssertionError: {'Save the job': ..., 'Unsave the job': ..., 'Saved':
        'saved'} != {'Save the job': 'not_saved', 'Unsave the job': 'saved'}
    """
    assert shape.SAVE_LABELS == {
        "Save the job": "not_saved",
        "Unsave the job": "saved",
    }
    assert set(dom.SAVE_LABELS_SEEN) == {"Save the job", "Unsave the job"}
    for never_measured in (UNMEASURED_LABEL, RENAMED_AWAY_LABEL, "Unsave", "Save"):
        assert never_measured not in shape.SAVE_LABELS, never_measured
        assert never_measured not in dom.SAVE_LABELS_SEEN, never_measured


async def test_a_reported_label_still_cannot_become_a_click():
    """The selector refuses every name outside the measured set.

    This is the property that makes reporting SAFE, and it is the property
    that had to SURVIVE the vocabulary growing -- otherwise "we measured it"
    becomes a route by which anything the sweep prints ends up clickable. The
    measured pair is clickable because four readings and a human decision put
    it there. Nothing else is, including the label this repo spent a month
    naming as equally plausible.

    SHOWN FAILING by widening ``dom.SAVE_LABELS_SEEN`` with a reported name::

        Failed: DID NOT RAISE ExtractionFailedError
    """
    from linkedin_server.errors import ExtractionFailedError

    for label in (UNMEASURED_LABEL, RENAMED_AWAY_LABEL, "Unsave", "Save"):
        with pytest.raises(ExtractionFailedError):
            dom.save_control_selector(label)


async def test_unsave_has_its_anchor_and_it_came_from_the_table():
    """THE SUCCESSOR to ``test_unsave_still_has_no_anchor_and_says_so``.

    That test asserted ``anchor_label_for`` returned None for unsave -- correct
    restraint while the label rested on one reading, and the guard that stopped
    the row being written from a single observation. The row is now written, on
    four observations across two routes, so the assertion is inverted rather
    than deleted: the reader that made the extra readings possible is in this
    same file, and the anchor it unblocked is asserted here.

    WHAT DID NOT CHANGE. The anchor comes from ``shape.SAVE_LABELS`` and
    nowhere else -- no code path was added, which is exactly what
    ``anchor_label_for``'s indirection was built to make possible.

    SHOWN FAILING by removing the row from ``shape.SAVE_LABELS``::

        AssertionError: assert None == 'Unsave the job'
    """
    from linkedin_server import writes

    spec = writes.SANCTIONED_WRITES["linkedin_unsave_job"]
    assert spec.from_state == "saved", spec
    assert writes.anchor_label_for(spec) == MEASURED_ON_LABEL
    # And its sibling is unchanged, so the table GAINED a row rather than
    # having been rewritten.
    assert writes.anchor_label_for(
        writes.SANCTIONED_WRITES["linkedin_save_job"]
    ) == "Save the job"
    # The anchor is a real selector now, not merely a non-None string.
    assert dom.save_control_selector(MEASURED_ON_LABEL) == (
        'button[aria-label="Unsave the job"]'
    )


# ---------------------------------------------------------------------------
# 4. Privacy -- a posting names people, and this route walks its controls
# ---------------------------------------------------------------------------


async def test_a_member_name_containing_sav_is_not_reported():
    """DERIVED: a hiring-team control named for a member whose name has "sav".

    The filter is a WHOLE WORD and not a substring, and the boundary is
    load-bearing: a job posting draws a hiring team and a "people also viewed"
    rail, so its accessible names include real members'.

    REPOINTED 2026-08-30, and the reason matters more than the edit. This drove
    a page wearing ``"Unsave the job"``, because that was then an UNMEASURED
    label and so reached the diagnostic sweep. It is measured now, so such a
    page is simply read and no sweep runs -- the test would have passed while
    exercising nothing. It is pointed at a label still outside the vocabulary
    instead. The privacy property under test never changed; only the state that
    reaches the sweep did.

    SHOWN FAILING by reverting the filter to ``"sav" in text.casefold()``::

        AssertionError: ['Saved', 'Savita Krishnan'] != ['Saved']
    """
    relabelled = derive(SAVE_ATTR, f'aria-label="{UNMEASURED_LABEL}"')
    with_member = derive(
        f'aria-label="{UNMEASURED_LABEL}"',
        f'aria-label="{UNMEASURED_LABEL}"></button>'
        f'<button type="button" aria-label="{MEMBER_NAME}"',
        src=relabelled,
    )
    verdict = await read(with_member)
    # The sweep MUST have run, or this test proves nothing about the filter.
    assert verdict["state"] == shape.SAVE_UNKNOWN, verdict
    assert verdict["observed"]["candidates"] == [UNMEASURED_LABEL], verdict
    assert MEMBER_NAME not in str(verdict), verdict
