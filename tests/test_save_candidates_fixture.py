"""The save refusal, and whether it reports what it saw.

WHAT WAS WRONG, and it is not the vocabulary. On 2026-08-30 the operator
authorised his first save. It refused, twice, ninety seconds apart, on a live
posting whose title and employer the preview had just read correctly::

    refusing to click: 'save_job' is valid only from 'not_saved' and the
    control on the page reads 'unknown'. no save control rendered in a state
    this reader recognises.

That sentence is the whole of what a failed save taught anybody. It names no
label, no count, and no scan, so the only route to the real label was to guess
one and try again -- and a guessed label on a TOGGLE performs the opposite
action, which is precisely the failure the refusal exists to prevent. The gate
made a correct decision and then threw away the evidence for it.

THE MECHANISM, verified here rather than assumed. ``dom.SAVE_CONTROL`` is the
literal CSS ``button[aria-label="Save the job"]``, assembled from a
``dom.SAVE_LABELS_SEEN`` holding one string. A posting drawing the control
under any other accessible name matches ZERO elements, so
``dom.read_save_control`` returns ``{"label": None, "count": 0}``: it never
reads an attribute at all. ``shape.save_state`` then takes its ``count == 0``
branch, which is where that sentence comes from -- NOT the unrecognised-label
branch. ``test_the_refusal_the_operator_saw_is_the_count_zero_branch`` pins
that distinction, because it decides the shape of the fix: there is nothing to
print better from the first reading, since nothing was read. The diagnostic has
to be a SECOND, wider look.

WHAT IS AND IS NOT FIXED HERE. The refusal now reports what the page drew. The
VOCABULARY is untouched: ``shape.SAVE_LABELS`` still holds one row, an
unrecognised state still refuses, and no fallback clicks on one. Every test
below that reaches ``perform`` asserts it still raises.

Every reading is taken by the REAL reader over a REAL parsed DOM in a local
headless Chromium. Nothing here reaches the network or an account, and no
fixture in this module is evidence about LinkedIn: every page is DERIVED from
``fixtures/job_detail_hydrated.html`` by an explicit, asserted edit, and is
labelled DERIVED where it is used.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from linkedin_server import dom, shape, writes
from linkedin_server.errors import WriteAttemptError
from tests.test_apply_modal_fixture import (  # noqa: F401 - used by injection
    over,
)
from tests.test_writes import (  # noqa: F401 - fixtures are used by injection
    JOB,
    FixtureNavigator,
    _granted,
    _no_grants_survive_a_test,
    browser_page,
    writes_on,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: The one string every derivation below is anchored on.
SAVE_ATTR = 'aria-label="Save the job"'

#: A member name that satisfies the SUBSTRING rule this reader used to run
#: (``"sav" in text.casefold()``) and not the whole-word rule it runs now.
#: Invented; it names nobody, and the assertion that it beats the old rule is
#: made in the test rather than asserted here.
MEMBER_NAME = "Savita Krishnan"

#: A readiness reading standing for "the control layer HAD attached". Used by
#: every enumeration test below, because those are about what the sweep reports
#: on a page that drew -- not about hydration, which has its own section.
READY = {"ready": True, "waited_ms": 12, "timeout_ms": 10_000, "failure": None}

#: The opposite, as Playwright actually reports a genuine expiry.
TIMED_OUT = {
    "ready": False,
    "waited_ms": 10_004,
    "timeout_ms": 10_000,
    "failure": "TimeoutError",
}


def base() -> str:
    """The captured hydrated posting, read as ASCII like every fixture here."""
    return (FIXTURE_DIR / "job_detail_hydrated.html").read_text(encoding="ascii")


def derive(old: str, new: str, *, src: str | None = None) -> str:
    """One DERIVED page, plus a receipt that the edit actually landed.

    Copied from ``test_apply_modal_fixture.derive`` for the same reason it
    exists there: a ``replace`` whose anchor has drifted is a silent no-op, and
    this repo has already shipped one test built on that.
    """
    src = base() if src is None else src
    out = src.replace(old, new, 1)
    assert out != src, (
        f"the derivation anchored on {old!r} changed nothing, so this variant "
        "is the base fixture wearing another name. Repoint the anchor, and do "
        "NOT delete this assertion."
    )
    return out


#: DERIVED: the save control wearing an accessible name this reader has never
#: seen. The string is chosen because it is one of the two the production
#: comment in ``shape.SAVE_LABELS`` names as PLAUSIBLE AND UNMEASURED -- so it
#: models the real ambiguity rather than an obvious rename.
RELABELLED = derive(SAVE_ATTR, 'aria-label="Saved"')

#: DERIVED: the control renamed clean off the save vocabulary.
RENAMED_AWAY = derive(SAVE_ATTR, 'aria-label="Bookmark this job"')

#: DERIVED: the relabelled page, plus a hiring-team control named for a member
#: whose name contains "sav".
WITH_MEMBER = derive(
    'aria-label="Saved"',
    f'aria-label="Saved"></button><button type="button" aria-label="{MEMBER_NAME}"',
    src=RELABELLED,
)


def swamped(count: int) -> str:
    """DERIVED: the RELABELLED page carrying ``count`` extra filler controls.

    Built on the relabelled page rather than the captured one on purpose, so
    the crowded case models a real refusal -- a save control this reader cannot
    name, on a page too busy to sweep -- rather than a crowded page that would
    have resolved cleanly anyway.
    """
    fillers = "".join(
        f'<button type="button" aria-label="Filler {i:03d}"></button>'
        for i in range(count)
    )
    return derive(
        'aria-label="Saved"',
        f'aria-label="Saved"></button>{fillers}<button ',
        src=RELABELLED,
    )


# ---------------------------------------------------------------------------
# 1. The mechanism, pinned before anything is built on it
# ---------------------------------------------------------------------------


async def test_the_refusal_the_operator_saw_is_the_count_zero_branch(over):
    """WHICH BRANCH FIRED DECIDES WHAT THE FIX HAS TO BE.

    Two different readings can end at ``unknown``: a control whose label was
    READ and not recognised, and a control that was never located at all. Only
    the first has something to print. This asserts the live refusal was the
    SECOND -- ``count`` 0 and ``label`` None -- which is why the diagnostic
    below is a fresh sweep and not a better print of what ``read_save_control``
    already had.
    """
    reading = await over(RELABELLED, dom.read_save_control)
    assert reading == {"label": None, "count": 0}

    verdict = shape.save_state(reading["label"], count=reading["count"])
    assert verdict["state"] == shape.SAVE_UNKNOWN
    # The sentence the operator saw, verbatim, from the branch that produced it.
    assert verdict["why"].startswith(
        "no save control rendered in a state this reader recognises."
    )
    # And the page was NOT bare: the reader walked past real controls.
    assert (await over(RELABELLED, dom.read_save_candidates))["buttons_total"] > 1


# ---------------------------------------------------------------------------
# 2. The refusal reports what it saw
# ---------------------------------------------------------------------------


async def test_the_refusal_names_the_label_the_page_actually_drew(
    writes_on, browser_page
):
    """THE DEFECT, DRIVEN THROUGH THE REAL GATE.

    A full grant, redeemed the way the tool redeems one, performed against a
    DERIVED posting whose save control wears an unmeasured name. The refusal
    must still happen AND must carry the label, the count, and the fact that
    the scan finished.
    """
    grant = await _granted(browser_page, "save_job", target=JOB)
    nav = FixtureNavigator({f"https://www.linkedin.com/jobs/view/{JOB}/": RELABELLED})

    with pytest.raises(WriteAttemptError) as caught:
        await writes.perform(nav, browser_page, grant)

    message = str(caught.value)
    # It still refuses, for the reason it always did ...
    assert "refusing to click" in message
    assert "reads 'unknown'" in message
    # ... and it now says what was there.
    assert "'Saved'" in message, message
    assert "labelled controls" in message, message
    assert "ALL of them read" in message, message
    # The click never happened: perform verifies from the saved list AFTER a
    # click, so a run that only ever asked for the posting did not get there.
    assert nav.gotos == [f"https://www.linkedin.com/jobs/view/{JOB}/"]


async def test_a_reported_label_still_cannot_become_a_click():
    """REPORTING A NAME MUST NOT BE A ROUTE TO PRESSING IT.

    The diagnostic publishes an accessible name into a message a caller reads.
    If that name could be fed back in and turned into a selector, the whole
    refusal would be a formality. It cannot: the selector builder is anchored
    on ``SAVE_LABELS_SEEN`` and refuses everything else, unchanged by any of
    this.
    """
    from linkedin_server.errors import ExtractionFailedError

    with pytest.raises(ExtractionFailedError):
        dom.save_control_selector("Saved")
    assert set(dom.SAVE_LABELS_SEEN) == {"Save the job"}
    assert shape.SAVE_LABELS == {"Save the job": "not_saved"}


# ---------------------------------------------------------------------------
# 3. Absent is not zero
# ---------------------------------------------------------------------------


async def test_an_empty_list_and_an_unfinished_scan_do_not_look_alike(over):
    """THE RULE THE APPLY SCAN ALREADY PAYS FOR, applied to this one.

    Two pages both report ``candidates: []``. On one, every control was read
    and none carried a save word -- a real finding. On the other nothing was
    read at all. They MUST be separable, and by more than a count that a reader
    has to interpret: the two sentences differ.
    """
    over_limit = dom.SAVE_SCAN_LIMIT + 1
    crowded = await over(swamped(over_limit), dom.read_save_candidates)
    ordinary = await over(RENAMED_AWAY, dom.read_save_candidates)

    assert crowded["candidates"] == []
    assert ordinary["candidates"] == []

    assert crowded["scan_complete"] is False
    assert ordinary["scan_complete"] is True
    assert crowded["buttons_total"] > dom.SAVE_SCAN_LIMIT
    assert ordinary["buttons_total"] < dom.SAVE_SCAN_LIMIT

    crowded_note = writes._save_candidates_note(crowded, waited=READY)
    ordinary_note = writes._save_candidates_note(ordinary, waited=READY)
    assert crowded_note != ordinary_note
    assert "UNKNOWN" in crowded_note
    assert "not run at all" in crowded_note
    assert "ALL of them read" in ordinary_note
    assert "NOT ONE carries a save word" in ordinary_note


async def test_a_control_that_would_not_read_makes_the_scan_incomplete():
    """A BUTTON THAT WOULD NOT READ IS A BUTTON THAT CANNOT BE RULED OUT.

    Driven over a fake, because a DOM cannot be made to fail one
    ``get_attribute`` and not its neighbours. The old sweep's ``continue`` on
    this path turned a failed read into "nothing found here", which is the same
    class of lie the limit used to tell.
    """

    class _Boom:
        async def get_attribute(self, _name):
            raise RuntimeError("detached")

    class _Fine:
        def __init__(self, label):
            self.label = label

        async def get_attribute(self, _name):
            return self.label

    class _Locator:
        def __init__(self, nodes):
            self.nodes = nodes

        async def count(self):
            return len(self.nodes)

        def nth(self, index):
            return self.nodes[index]

    class _Page:
        def __init__(self, nodes):
            self._loc = _Locator(nodes)

        def locator(self, _selector):
            return self._loc

    reading = await dom.read_save_candidates(
        _Page([_Fine("Saved"), _Boom(), _Fine("More options")])
    )
    assert reading["candidates"] == ["Saved"]
    assert reading["buttons_total"] == 3
    assert reading["scan_complete"] is False, (
        "one unreadable control among three, and the scan called itself "
        "finished -- so 'Saved' reads as the only save-worded control on the "
        "page when it is merely the only one that could be read."
    )
    assert "ONLY PARTLY KNOWN" in writes._save_candidates_note(reading, waited=READY)


def test_a_reading_that_predates_a_field_refuses():
    """THE DEFAULT REFUSES, the only safe direction for a new field.

    A payload built before ``scan_complete`` existed -- a stale fake in a
    future test, a half-built dict -- must read as "did not finish", never as
    "finished and found nothing".
    """
    note = writes._save_candidates_note(
        {"candidates": [], "buttons_total": 7}, waited=READY
    )
    assert "ONLY PARTLY KNOWN" in note
    assert "DID NOT FINISH" in note


# ---------------------------------------------------------------------------
# 4. Member privacy
# ---------------------------------------------------------------------------


async def test_a_member_name_containing_sav_is_not_reported(over):
    """THE FILTER IS A WORD BECAUSE A SUBSTRING WAS NOT ENOUGH.

    A job posting draws a hiring team and a "people also viewed" rail, so its
    accessible names include real members'. The old rule -- ``"sav" in
    text.casefold()`` -- is asserted here to MATCH the member name, which is
    what makes the tightening a fix rather than a preference.
    """
    assert "sav" in MEMBER_NAME.casefold(), (
        "this test's whole point is that the OLD rule matched this name; if it "
        "does not, the name has drifted and the test proves nothing."
    )

    reading = await over(WITH_MEMBER, dom.read_save_candidates)
    assert reading["scan_complete"] is True
    assert reading["candidates"] == ["Saved"]
    assert reading["matched_total"] == 1
    # The member's control WAS on the page and WAS walked ...
    assert reading["buttons_total"] > (
        await over(RELABELLED, dom.read_save_candidates)
    )["buttons_total"]
    # ... and did not come back.
    assert MEMBER_NAME not in writes._save_candidates_note(reading, waited=READY)

    # The same guard on the OTHER path that publishes a raw label: the
    # post-click read-back, whose value is printed for a human to copy.
    became = await over(WITH_MEMBER, dom.read_any_save_control_label)
    assert became == "Saved"
    assert became != MEMBER_NAME


async def test_a_save_worded_label_is_still_reduced_before_it_is_printed(over):
    """THE WORD FILTER IS NOT THE ONLY GATE, and it should not be.

    A control can carry a save word AND a member's name, or a whole sentence.
    ``shape.census_shape`` is the repo's own reduction and it runs second, so
    anything over its length or outside its ASCII class comes back opaque
    rather than verbatim.
    """
    long_label = "Saved " + "x" * shape.CENSUS_NAME_LIMIT
    page = derive(SAVE_ATTR, f'aria-label="{long_label}"')
    reading = await over(page, dom.read_save_candidates)

    assert reading["matched_total"] == 1, "the word filter passed it"
    assert reading["candidates"] == [shape.CENSUS_OPAQUE], reading["candidates"]
    assert "x" * 20 not in writes._save_candidates_note(reading, waited=READY)


def test_the_diagnostic_says_that_it_filtered():
    """A FILTERED LIST THAT DOES NOT SAY SO READS AS A COMPLETE ONE.

    Which would be the worse error of the two this change could make: a reader
    told "no save control here" by a list that silently dropped one would stop
    looking, where a reader told the list is filtered knows to go and look.
    """
    for reading in (
        {"candidates": ["Saved"], "matched_total": 1, "buttons_total": 7,
         "scan_complete": True},
        {"candidates": [], "matched_total": 0, "buttons_total": 7,
         "scan_complete": True},
        {"candidates": [], "matched_total": 0, "buttons_total": 9_999,
         "scan_complete": False},
    ):
        note = writes._save_candidates_note(reading, waited=READY)
        assert "Filtered, and deliberately" in note, reading
        assert "hiring team" in note, reading


# ---------------------------------------------------------------------------
# 5. Behaviour is unchanged
# ---------------------------------------------------------------------------


async def test_a_recognised_control_still_reads_not_saved_and_costs_no_sweep(over):
    """THE HAPPY PATH DOES NOT PAY FOR THE DIAGNOSTIC.

    The second reading is taken only where the first one refused. A page whose
    control this reader knows must resolve exactly as it always did.
    """
    reading = await over(base(), dom.read_save_control)
    assert reading == {"label": "Save the job", "count": 1}
    verdict = shape.save_state(reading["label"], count=reading["count"])
    assert verdict["state"] == "not_saved"
    assert verdict["why"] == "the control is labelled 'Save the job'"


# ---------------------------------------------------------------------------
# 6. Readiness -- the second wave
# ---------------------------------------------------------------------------
#
# WHAT THE LIVE MEASUREMENT SAID, and why it changed the diagnosis. The
# diagnostic above shipped, and two live redemptions of a confirm token against
# one posting, roughly forty seconds apart, returned:
#
#     attempt 1: 2 labelled controls, ALL of them read, and NOT ONE carries a
#                save word
#     attempt 2: 1 labelled controls, ALL of them read, and NOT ONE carries a
#                save word
#
# THE COUNT MOVED. A renamed control gives a STABLE count, so 2-then-1 is not a
# vocabulary problem -- it is the reader arriving before the page has finished
# drawing. And the sentence the refusal printed on that reading was actively
# wrong: "So this is not a save control wearing a new name -- either the
# posting renders no save control at all, or it renders one worded in a way no
# rule here anticipated" states a conclusion about LINKEDIN'S VOCABULARY that a
# page which never rendered cannot support.
#
# THE DISCRIMINATOR IS MEASURED, and the first test below pins it: the
# un-hydrated shell capture draws ZERO buttons under <main>, and every posting
# capture that actually rendered draws between two and twelve.

#: DERIVED: the hydrated posting with every ``<button>`` removed and everything
#: else left alone. Models the state the live measurement is consistent with --
#: server-rendered text and anchors present, the BUTTON layer not attached.
#: What SURVIVES is the interesting half: a believable title, a believable
#: employer, and the apply control, which is an ``<a>``. That is why apply
#: cannot be the readiness signal, and a test below asserts it.
UNATTACHED = re.sub(r"<button\b[^>]*>.*?</button>", "", base(), flags=re.S)
assert UNATTACHED != base(), "the button-stripping derivation matched nothing"


def test_the_hydration_discriminator_is_measured_not_argued():
    """THE PREMISE THE WHOLE DIAGNOSIS RESTS ON, pinned as a number.

    Every readiness sentence this module prints claims that zero buttons under
    ``<main>`` means the control layer did not attach. That claim is worth
    something only while the captures say so. If a future capture of a
    genuinely rendered posting draws zero or one button, the diagnosis is
    unfounded -- and this test is where that should be found, not in a live
    refusal telling somebody the page never rendered.
    """
    from html.parser import HTMLParser

    class _Buttons(HTMLParser):
        def __init__(self):
            super().__init__()
            self.count = 0

        def handle_starttag(self, tag, attrs):
            if tag == "button":
                self.count += 1

    def buttons(name: str) -> int:
        parser = _Buttons()
        parser.feed((FIXTURE_DIR / f"{name}.html").read_text(encoding="ascii"))
        return parser.count

    shell = buttons("job_detail_shell")
    rendered = {
        name: buttons(name)
        for name in (
            "job_detail",
            "job_detail_hydrated",
            "job_detail_following",
            "job_detail_following_hydrated",
        )
    }

    assert shell == 0, (
        f"the un-hydrated shell draws {shell} buttons, not zero -- and the "
        "whole 'zero buttons means unattached' reading is built on this."
    )
    assert min(rendered.values()) >= 2, rendered
    assert shell < min(rendered.values()), (shell, rendered)


async def test_a_ready_page_costs_the_wait_nothing(over):
    """THE HAPPY PATH MUST NOT PAY FOR THE FIX.

    A readiness condition that charged every save ten seconds would be traded
    away the first time somebody was in a hurry. An already-attached element
    satisfies the wait at once, so this asserts the cost is a small fraction of
    the ceiling rather than pinning a wall-clock number.
    """

    async def work(page):
        return await dom.wait_for_save_control(page, 5_000)

    waited = await over(base(), work)
    assert waited["ready"] is True
    assert waited["failure"] is None
    assert waited["waited_ms"] < 1_000, waited


async def test_an_unattached_page_and_a_renamed_control_are_diagnosed_apart(over):
    """THE DISCRIMINATION, WHICH IS THE WHOLE POINT OF THIS WAVE.

    Both pages refuse and both find no save word. The question that matters is
    not what was found, it is whether the page had DRAWN: one of these is a
    vocabulary finding and the other is a timing one, they want opposite
    responses, and before this wave they printed the same verdict.
    """

    async def work(page):
        waited = await dom.wait_for_save_control(page, 900)
        return waited, await dom.read_save_candidates(page)

    ready_waited, ready_reading = await over(RENAMED_AWAY, work)
    unready_waited, unready_reading = await over(UNATTACHED, work)

    # Neither is ready by the save control's own measure ...
    assert ready_waited["ready"] is False
    assert unready_waited["ready"] is False
    # ... and both find no save word ...
    assert ready_reading["candidates"] == []
    assert unready_reading["candidates"] == []
    # ... so the ONLY thing that can tell them apart is the button layer.
    assert ready_reading["main_buttons_total"] >= 2, ready_reading
    assert unready_reading["main_buttons_total"] == 0, unready_reading

    ready_note = writes._save_candidates_note(ready_reading, waited=ready_waited)
    unready_note = writes._save_candidates_note(unready_reading, waited=unready_waited)
    assert "THE PAGE WAS READY" in ready_note, ready_note
    assert "NEVER BECAME READY" in unready_note, unready_note
    assert "DO NOT WIDEN" in unready_note
    assert "DO NOT WIDEN" not in ready_note


async def test_the_unattached_page_still_reads_a_believable_title(over):
    """WHY A CORRECT TITLE AND EMPLOYER WERE NOT CORROBORATION.

    The live refusals came back alongside the posting's real title and
    employer, which reads as proof the page was fine. It is not. A page with NO
    buttons at all still yields a believable title, a believable employer AND
    an apply control -- all three survive because they are server-rendered or
    are anchors. Only the buttons are missing, and the buttons are what a save
    needs.
    """

    async def work(page):
        identity = await dom.read_job_identity(page)
        detail = shape.parse_job_detail(
            await dom.read_main_text(page),
            company=identity.get("company"),
            document_title=identity.get("document_title"),
        )
        return (
            shape.job_detail_is_believable(detail),
            detail.get("company"),
            int(await page.locator(dom.APPLY_CONTROL).count()),
            int(await page.locator(dom.MAIN_BUTTONS).count()),
        )

    believable, company, apply_n, buttons = await over(UNATTACHED, work)
    assert believable is True, "a page with no buttons still reads as a posting"
    assert company
    assert apply_n == 1, (
        "the apply control survives with the button layer gone, which is why "
        "it cannot be the readiness signal"
    )
    assert buttons == 0


async def test_the_split_makes_the_live_two_interpretable(over):
    """THE FIELD THAT WAS MISSING WHEN THE LIVE READING CAME BACK.

    "2 labelled controls" was uninterpretable because the total merged buttons
    and anchors. Split, the same page says: zero labelled BUTTONS, two labelled
    LINKS, zero buttons of any kind -- a page whose anchors drew and whose
    buttons did not, rather than a page with two mysterious controls on it.
    """
    reading = await over(UNATTACHED, dom.read_save_candidates)
    assert reading["buttons_total"] == 2, reading
    assert reading["labelled_buttons"] == 0, reading
    assert reading["labelled_links"] == 2, reading
    assert reading["main_buttons_total"] == 0, reading

    note = writes._save_candidates_note(reading, waited=TIMED_OUT)
    assert "0 button(s) and 2 link(s)" in note, note


async def test_a_readiness_check_that_could_not_run_is_not_a_finding():
    """A BROKEN INSTRUMENT MUST NOT MANUFACTURE A HYDRATION FINDING.

    ``ready: False`` arrives from two different worlds: the page was asked and
    had not drawn, or the question never reached the page. Collapsing them
    would let a detached frame print "THE PAGE NEVER BECAME READY", which is a
    claim about LinkedIn assembled out of a local failure.
    """

    class _Exploding:
        def locator(self, _selector):
            raise RuntimeError("target closed")

    waited = await dom.wait_for_save_control(_Exploding(), 50)
    assert waited["ready"] is False, "a failure must never open the gate"
    assert waited["failure"] == "RuntimeError"

    note = writes._save_readiness_note({"main_buttons_total": 0}, waited)
    assert "READINESS CHECK ITSELF FAILED" in note, note
    assert "NEVER BECAME READY" not in note, (
        "a locator that could not be asked was reported as a page that had "
        "not drawn -- a finding about LinkedIn invented from a local error."
    )


async def test_a_button_count_that_failed_is_reported_as_unreported():
    """THE DISCRIMINATOR'S OWN DEFAULT, driven where it is actually set.

    Written after a mutation exposed the gap: flipping the sweep's
    ``main_buttons_total`` default from None to 0 left every test green,
    because the note tests all hand-build their own dict and never reach the
    sweep. A default nothing exercises is a default nobody is defending, and
    THIS one decides whether a page gets told it never rendered.
    """

    class _Ok:
        async def count(self):
            return 0

    class _Broken:
        async def count(self):
            raise RuntimeError("detached")

        def nth(self, index):  # pragma: no cover - never reached
            raise AssertionError("must not walk a locator that would not count")

    class _Page:
        """Counts the sweep and the labelled buttons; FAILS on main buttons."""

        def locator(self, selector):
            return _Broken() if selector == dom.MAIN_BUTTONS else _Ok()

    reading = await dom.read_save_candidates(_Page())
    assert reading["main_buttons_total"] is None, (
        "the button count failed and came back as 0, which is the value that "
        "means 'the page drew nothing' -- so a broken count would print the "
        "strongest sentence this module has."
    )
    assert "IS UNKNOWN" in writes._save_readiness_note(reading, TIMED_OUT)


def test_an_unreported_button_count_is_not_a_count_of_zero():
    """ABSENT IS NOT ZERO, applied to the discriminator itself.

    Zero buttons is the evidence for the strongest sentence this module
    prints. A count that could not be TAKEN must never reach that sentence, or
    the diagnosis is asserted from a measurement nobody made.
    """
    unknown = writes._save_readiness_note({"main_buttons_total": None}, TIMED_OUT)
    zero = writes._save_readiness_note({"main_buttons_total": 0}, TIMED_OUT)

    assert "IS UNKNOWN" in unknown, unknown
    assert "NEVER BECAME READY" not in unknown
    assert "NEVER BECAME READY" in zero
    assert unknown != zero


async def test_an_unready_page_still_refuses_and_still_clicks_nothing(
    writes_on, browser_page, monkeypatch
):
    """BEHAVIOUR IS UNCHANGED: the fix makes the refusal right, not permissive.

    The readiness apparatus must not become a route to proceeding. A posting
    whose control layer never attached is refused, the click never happens, and
    the message says which of the two failures it was.
    """
    monkeypatch.setattr(dom, "SAVE_READY_TIMEOUT_MS", 700)
    grant = await _granted(browser_page, "save_job", target=JOB)
    nav = FixtureNavigator({f"https://www.linkedin.com/jobs/view/{JOB}/": UNATTACHED})

    with pytest.raises(WriteAttemptError) as caught:
        await writes.perform(nav, browser_page, grant)

    message = str(caught.value)
    assert "refusing to click" in message
    assert "NEVER BECAME READY" in message, message
    assert "DO NOT WIDEN" in message, message
    # Never reached the post-click verification, so nothing was pressed.
    assert nav.gotos == [f"https://www.linkedin.com/jobs/view/{JOB}/"]


def test_the_production_timeout_is_bounded_and_named():
    """A READINESS WAIT WITHOUT A CEILING IS A HANG.

    Pinned because the monkeypatch above proves the mechanism at 700ms and
    would go on passing if the real constant were deleted or set to something
    no human would wait through.
    """
    assert isinstance(dom.SAVE_READY_TIMEOUT_MS, int)
    assert 1_000 <= dom.SAVE_READY_TIMEOUT_MS <= 30_000, dom.SAVE_READY_TIMEOUT_MS
