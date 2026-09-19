"""The reader that decides whether an irreversible submit may be pressed.

WHAT WAS MISSING, stated plainly because it is the reason this module exists.
``linkedin_apply_job`` submits an application, and it cannot be undone -- not
"this server has no withdraw", but nobody has established that LINKEDIN offers
one. The only thing standing between a confirm token and that submit is
``writes._apply_submit_gate``, and the gate decides by reading the modal
through ``dom.read_apply_modal``.

That reader had NEVER BEEN EXECUTED BY ANY TEST. It was only ever monkeypatched
away (``tests/test_writes.py`` hands the gate a fixed dict). So the gate's
DECISION was well covered and the READER THAT PRODUCES THE INPUT to that
decision was not covered at all -- and that is the worst possible split, because
a reader that mis-reports makes the gate decide correctly on wrong input while
every existing test goes on passing. Nothing in the suite could tell the
difference between "the modal has no Next" and "the reader failed to see one".

Every test below runs the REAL reader over a REAL parsed DOM in a local
headless Chromium. Nothing here reaches the network or an account.

THE FIXTURE IS DERIVED AND IS NOT EVIDENCE ABOUT LINKEDIN. It is written to six
remembered counts from a single 2026-08-24 observation whose capture no longer
exists; see the comment at the top of ``fixtures/apply_modal_derived.html``,
which says so at length. Every variant below is derived from that file by an
explicit, asserted edit, and is labelled DERIVED where it is used. A fixture is
the artefact most likely to be mistaken for evidence about the real page, so
the caveat is repeated rather than assumed -- and
``test_the_single_observation_caveat_is_still_stated_in_full`` pins the
production sentence that says so, byte for byte, precisely so that adding these
tests cannot become a reason to soften it.

TWO FINDINGS CAME OUT OF WRITING THIS, both pinned below as tests rather than
left in a report, and NEITHER IS FIXED HERE -- this module adds coverage and
changes no production behaviour:

* ``test_a_dialog_with_no_hooked_control_and_no_dialog_at_all_read_differently``
  -- the two failures produce a BYTE-IDENTICAL ``why``. They are separable, but
  only by ``modal_present``, not by the sentence.
* ``test_an_advance_control_past_the_fortieth_button_is_not_seen`` -- the
  advance scan stops at 40 buttons, and the one modal ever observed was
  recorded as having 43. THE SAFETY FIELD HAS A CEILING.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_server import dom, shape, writes
from linkedin_server.errors import WriteAttemptError
from tests.test_writes import (  # noqa: F401 - fixtures are used by injection
    JOB,
    SAVED_JOB,
    SAVED_LIST_CONTAINING,
    _granted,
    _no_grants_survive_a_test,
    _perform,
    browser_page,
    writes_on,
)

# ALIASED, because this module already has a zero-argument ``markup`` FIXTURE
# of its own and the two are different things: that one is this file's apply
# modal, this one loads any fixture by name. Importing it unaliased would
# shadow the fixture, and every test taking it would receive a function.
from tests.test_writes import markup as fixture_markup

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: Fixed so that a visibility answer is reproducible. ``read_apply_modal``
#: calls ``is_visible()`` on every control it considers, and a test that let
#: the viewport float would be reading a different page on a different machine.
VIEWPORT = {"width": 1280, "height": 720}


class _NoWaitPage:
    """A page for gate tests whose modal dict is fixed, not read from a DOM.

    ``_apply_submit_gate`` polls up to fifteen times with a one-second
    ``wait_for_timeout`` between attempts. Every dict handed to it below has
    ``modal_present`` and ``submit_present`` both true, so it breaks on the
    first pass and this never sleeps -- but the method has to EXIST, and it
    records its calls so a future edit that starts sleeping fails loudly here
    rather than adding fifteen seconds to the suite in silence.
    """

    def __init__(self) -> None:
        self.waits: list[int] = []

    async def wait_for_timeout(self, ms: int) -> None:
        self.waits.append(ms)


async def _gate_over_modal(modal: dict) -> dict:
    """Drive the REAL gate over one fixed modal reading.

    Swaps the reader rather than building a DOM, because what is under test
    here is the GATE'S RESPONSE to a reading -- specifically to one that says
    it did not finish, which is a state no fixture can produce without also
    building a two-hundred-button page for every case. The reader's own
    behaviour over real markup is covered above, on real markup.

    Restored in a ``finally`` so a failure cannot leak the patch into the next
    test; ``monkeypatch`` is not used because these tests take no fixture.
    """
    original = dom.read_apply_modal

    async def _fixed(_page):
        return dict(modal)

    dom.read_apply_modal = _fixed
    page = _NoWaitPage()
    try:
        verdict = await writes._apply_submit_gate(page)
    finally:
        dom.read_apply_modal = original
    assert page.waits == [], "the gate slept on a dict that satisfies it"
    return verdict


def markup() -> str:
    """The DERIVED base fixture, read the way the rest of the suite reads one.

    ``encoding="ascii"`` is not decoration. It is the second half of the write
    discipline in this repo: a fixture is written as ASCII bytes, and read back
    as ASCII, so a smart quote pasted in from prose fails HERE, loudly, instead
    of surviving into a comparison that then quietly never matches.
    """
    return (FIXTURE_DIR / "apply_modal_derived.html").read_text(encoding="ascii")


def derive(base: str, old: str, new: str, count: int = 1) -> str:
    """One DERIVED variant, plus a receipt that the edit actually landed.

    THE ASSERTION IS THE POINT, and the repo has already paid for the lesson
    once: ``test_a_second_click_inside_perform_is_still_caught`` was built on a
    literal that stopped matching the source, at which point its ``replace``
    became a silent no-op and the test went on passing while testing nothing.
    A derivation that cannot prove it changed anything is not a derivation, it
    is a copy with a different variable name.
    """
    out = base.replace(old, new, count)
    assert out != base, (
        f"the derivation anchored on {old!r} changed nothing, so this variant "
        "is the base fixture wearing another name. The anchor has drifted out "
        "of apply_modal_derived.html -- repoint it, and do NOT delete this "
        "assertion, which is the only thing keeping the variant honest."
    )
    return out


# ---------------------------------------------------------------------------
# The browser harness
# ---------------------------------------------------------------------------
#
# COPIED from ``tests/test_apply_fixture.py``'s ``_with_html`` rather than
# imported, and the reason is cost. ``_with_html`` launches AND CLOSES a
# Chromium on every single call; this module takes roughly two dozen readings.
# ``tests/test_writes.py``'s ``browser_page`` already measured the tradeoff on
# this machine -- a cold launch-and-close is 1.35s while five ``set_content``
# loads on a running browser cost 0.89s between them -- so practically the
# entire price is the launch. One browser per TEST, one fresh isolated CONTEXT
# per READING: the isolation that matters is per-measurement, and it is cheap,
# while the launch is not.


@pytest.fixture
async def over():
    """Run ``work(page)`` over frozen markup. One browser, a context per read.

    ``window.innerWidth`` is asserted on EVERY measurement, not once at setup.
    The reader's answers depend on ``is_visible()``, which is a question about
    a laid-out document, so a reading taken at an unknown width is a reading
    whose conditions were not recorded. This makes the width part of the
    measurement rather than part of the environment.
    """
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(html: str, work):
            context = await browser.new_context(viewport=dict(VIEWPORT))
            try:
                page = await context.new_page()
                await page.set_content(
                    html, wait_until="domcontentloaded", timeout=60_000
                )
                width = await page.evaluate("window.innerWidth")
                assert width == VIEWPORT["width"], (
                    f"the page laid out at {width}px, not {VIEWPORT['width']}px. "
                    "Every visibility answer below was taken at an unrecorded "
                    "width and none of them mean what they say."
                )
                return await work(page)
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


async def _shape_counts(page):
    """The four counts the fixture claims to have been built to."""
    return {
        "forms": int(await page.locator("form").count()),
        "file_inputs": int(await page.locator("input[type=file]").count()),
        "dialogs": int(await page.locator(dom.APPLY_MODAL_SELECTOR).count()),
        "buttons": int(await page.locator("button").count()),
    }


# ---------------------------------------------------------------------------
# The DERIVED variants, each one edit away from the base
# ---------------------------------------------------------------------------
#
# ALL DERIVED, all from the same file, and none of them is a capture. The
# anchors are pulled from ``dom`` wherever ``dom`` owns the string, so renaming
# the hook or the modal selector in production drags these with it instead of
# leaving them pointing at a name LinkedIn no longer uses.

_IN_DIALOG = "<h2>Apply to Staff Engineer</h2>"
_SUBMIT_LABEL = 'aria-label="Submit application"'
_HOOKED_BUTTON = (
    f"<button {dom.APPLY_SUBMIT_HOOK} {_SUBMIT_LABEL} "
    'type="button">Submit application</button>'
)


def two_hooked(base: str) -> str:
    """A SECOND control wearing the submit hook. The count != 1 branch."""
    return derive(base, _IN_DIALOG, f"{_IN_DIALOG}\n  {_HOOKED_BUTTON}")


def no_hooked(base: str) -> str:
    """The dialog renders, and nothing in it carries the hook."""
    return derive(
        base, dom.APPLY_SUBMIT_HOOK, "data-derived-hook-that-is-not-the-hook", 1
    )


def no_dialog(base: str) -> str:
    """Nothing on the page carries ``role=dialog``, and nothing carries the hook.

    This is the exact negative of what the reader means by "the modal
    rendered": ``modal_present`` is ``count([role=dialog]) > 0`` and nothing
    else, so removing the role is removing the modal as far as it can tell.
    """
    return derive(no_hooked(base), 'role="dialog"', 'role="region"')


def advance(base: str, word: str) -> str:
    """A control inside the dialog whose name carries an advance word."""
    button = f'<button type="button">{word.capitalize()}</button>'
    return derive(base, _IN_DIALOG, f"{_IN_DIALOG}\n  {button}")


# ---------------------------------------------------------------------------
# 1. The measured shape, and the fixture's own derivation
# ---------------------------------------------------------------------------


async def test_the_measured_shape_reads_as_the_measured_shape(over):
    """THE POSITIVE CASE, and it goes first.

    Everything after this asserts a refusal, and a wall of refusals passes
    perfectly against a reader that returns False for everything -- which is
    exactly the failure this module was written to be able to see. If the
    reader ever degenerates into a constant, this is the test that goes red.

    DERIVED INPUT, and the conclusion is about the READER, not about LinkedIn:
    what is shown is that markup of this shape is reported accurately, not that
    a live apply modal has this shape.
    """
    reading = await over(markup(), dom.read_apply_modal)

    assert reading["modal_present"] is True
    assert reading["submit_present"] is True
    assert reading["submit_enabled"] is True
    assert reading["submit_name"] == "Submit application"
    assert reading["advance_names"] == []
    assert reading["why"] == ""
    # ADDED 2026-08-26 with the ceiling fix. "No advance controls" is only
    # worth something next to "and the search finished", so the reader now
    # reports both and this pins both on the shape it was derived from.
    assert reading["advance_scan_complete"] is True
    assert reading["buttons_total"] > 0

    # THE SCRATCH KEYS MUST NOT SURVIVE. The reader stashes the disabled and
    # aria-disabled attributes under private names and pops them again, and it
    # pops them in a short-circuiting boolean expression -- so on any input
    # where the first operand is False the pops inside the expression never
    # run and only the trailing cleanup removes them. That is a real edge and
    # a leaked key would be a field the gate never asked for, so the whole key
    # set is pinned rather than spot-checked.
    assert set(reading) == {
        "modal_present",
        "submit_present",
        "submit_enabled",
        "submit_name",
        "advance_names",
        "buttons_total",
        "advance_scan_complete",
        "why",
    }


async def test_the_fixture_answers_to_the_counts_it_claims_to_be_derived_from(
    over,
):
    """The derivation, checked rather than asserted in a comment.

    The fixture's header claims six numbers from 2026-08-24. Four of them are
    countable on the parsed document, and a fixture whose header and body
    disagree is worse than an unlabelled one: it carries a claim about where it
    came from that nothing enforces.

    THIS IS STILL NOT EVIDENCE ABOUT LINKEDIN. It shows the file matches the
    remembered counts. The counts are a memory of one posting, and the capture
    they were taken from no longer exists.
    """
    counts = await over(markup(), _shape_counts)
    assert counts == {
        "forms": 2,
        "file_inputs": 1,
        "dialogs": 1,
        "buttons": 43,
    }


def test_the_single_observation_caveat_is_still_stated_in_full():
    """The caveat may not be softened, and least of all BY THIS MODULE.

    Adding tests to a reader is the most natural-sounding reason in the world
    to start describing its input as established. It is not. These fixtures are
    derived from one remembered observation, and coverage of the reader says
    nothing whatever about how many apply flows LinkedIn draws.

    So the sentence in production that says so is pinned here, byte for byte,
    in the module that created the temptation.

    PINNED ON THE SOURCE FILE AND NOT ON ``__doc__``, which is not a detail:
    Python 3.13 strips the common leading indentation from docstrings at
    compile time, so the same sentence has different bytes in ``__doc__`` on
    3.12 and on 3.13. A pin that reads the attribute would be asserting a
    property of the interpreter. The claim being guarded is about what is
    WRITTEN in writes.py, so that is what is read.
    """
    source = Path(writes.__file__).read_text(encoding="utf-8")
    caveat = (
        "    WHY THIS IS THE WHOLE SAFETY ARGUMENT. Exactly ONE posting's "
        "apply flow has\n"
        "    ever been observed: a single screen, one enabled \"Submit "
        "application\", no\n"
        "    Next. Generalising from one observation to every posting on "
        "LinkedIn would\n"
        "    be a guess, and the thing guessed about cannot be taken back."
    )
    assert caveat in source, (
        "the single-observation caveat in _apply_submit_gate has been edited. "
        "If that was done because 'there are tests now', put it back: these "
        "tests execute the reader over DERIVED markup and establish nothing "
        "whatever about how many apply flows LinkedIn draws."
    )


# ---------------------------------------------------------------------------
# 2. Two hooked controls -- the branch that had never run
# ---------------------------------------------------------------------------


async def test_two_controls_wearing_the_submit_hook_are_refused(over):
    """THE MOST IMPORTANT TEST HERE, because this branch was dead.

    ``read_apply_modal`` refuses unless EXACTLY ONE control carries LinkedIn's
    submit hook, and until now no test had ever produced a second one -- the
    gate's own tests hand it a finished dict, so ``count != 1`` was reachable
    only from a real DOM that no test built.

    WHY MORE THAN ONE IS THE DANGEROUS CASE and not merely an odd one: with two
    hooked controls, ``page.locator(...)`` resolves to two elements and a click
    would have to pick one BY POSITION. Choosing by position, on a control that
    submits an application nobody can withdraw, is the single worst thing this
    package could do. The reader refuses to name one instead.

    The refusal must NAME THE COUNT, because "expected exactly one" without the
    number leaves the reader of the message unable to tell two from zero -- and
    those are different problems with different fixes.

    DERIVED: the base fixture with one extra hooked button in the dialog.
    """
    reading = await over(two_hooked(markup()), dom.read_apply_modal)

    assert reading["modal_present"] is True
    assert reading["submit_present"] is False
    assert reading["submit_enabled"] is False
    assert reading["submit_name"] is None
    assert "2" in reading["why"], reading["why"]
    assert dom.APPLY_SUBMIT_HOOK in reading["why"]


# ---------------------------------------------------------------------------
# 3. Zero hooked controls, with and without a modal
# ---------------------------------------------------------------------------


async def test_a_dialog_with_no_hooked_control_is_refused(over):
    """A modal that rendered and carries nothing this reader recognises.

    DERIVED: the base fixture with the hook renamed, so the button is still
    there and is no longer the one the reader is looking for. That models the
    live hazard exactly -- LinkedIn renaming its own test hook -- and the right
    answer is a refusal, not a guess at whichever button looks like a submit.
    """
    reading = await over(no_hooked(markup()), dom.read_apply_modal)

    assert reading["modal_present"] is True
    assert reading["submit_present"] is False
    assert "0" in reading["why"], reading["why"]


async def test_a_dialog_with_no_hooked_control_and_no_dialog_at_all_read_differently(
    over,
):
    """FINDING, PINNED RATHER THAN FIXED. Two failures, one sentence.

    These are genuinely different problems. "The modal opened and I do not
    recognise anything in it" means LinkedIn changed the modal. "No modal
    opened" means the page never hydrated -- the same non-hydration that makes
    postings read as having no apply control at all. They want different
    responses from a human.

    The reader SEPARATES THEM, but not where a reader of the message would
    look: ``modal_present`` differs and ``why`` DOES NOT. Both cases produce
    the byte-identical sentence "expected exactly one ... and found 0", because
    the count really is 0 in both and ``why`` is written from the count alone.

    That is asserted here in both directions rather than smoothed over: the
    record distinguishes them, the sentence does not. It is survivable only
    because ``_apply_submit_gate`` tests ``modal_present`` FIRST and writes its
    own "never rendered" message before it ever consults this one -- which is
    checked below in ``test_the_gate_reads_the_real_modal_and_proceeds`` and
    its siblings. Anything else that ever reads ``why`` alone will not be able
    to tell these two apart.

    NOT FIXED HERE. This module adds coverage and changes no production
    behaviour; whether the reader should say two different things is a call for
    whoever owns writes.py.
    """
    base = markup()
    rendered = await over(no_hooked(base), dom.read_apply_modal)
    absent = await over(no_dialog(base), dom.read_apply_modal)

    # Both refuse, and neither invents a submit.
    assert rendered["submit_present"] is False
    assert absent["submit_present"] is False

    # THE DISTINCTION EXISTS, and this is the field carrying it.
    assert rendered["modal_present"] is True
    assert absent["modal_present"] is False
    assert rendered != absent

    # THE DISTINCTION IS NOT IN THE MESSAGE. Pinned as a finding: if somebody
    # makes these two sentences differ, this assertion is the one to delete,
    # and deleting it should be a deliberate act rather than a surprise.
    assert rendered["why"] == absent["why"]


# ---------------------------------------------------------------------------
# 4. Disabled, both ways of learning it
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "addition,what",
    [
        (" disabled", "the HTML disabled attribute"),
        (' aria-disabled="true"', "the ARIA disabled state"),
    ],
    ids=["disabled attribute", "aria-disabled=true"],
)
async def test_a_submit_the_page_calls_disabled_is_reported_disabled(
    over, addition, what
):
    """BOTH ROUTES, as separate cases, because they are separate reads.

    The reader learns "disabled" two independent ways and they fail
    differently. ``disabled`` is an HTML attribute whose PRESENCE is the whole
    signal -- ``get_attribute`` returns the empty string for it, not the
    element's name, so a test of this branch is also a test that the reader
    compares against ``None`` and not against falsiness. ``aria-disabled`` is a
    STRING that must equal "true"; a widget that sets it to "false" is enabled
    and a reader keyed on presence would call it disabled.

    Both are honoured. That is a MEASUREMENT taken on 2026-08-26 and not an
    assumption: had only one been honoured, the other case here would be red
    and would be reported as a finding rather than quietly dropped.

    WHAT A WRONG ANSWER WOULD COST: the gate refuses a disabled submit because
    "the form wants something it has not got" and nobody has measured what.
    A reader that called a disabled control enabled would send the gate past
    its own third condition and put a click on a control the page is refusing.

    DERIVED: the base fixture with one attribute added to the submit.
    """
    html = derive(markup(), _SUBMIT_LABEL, f"{_SUBMIT_LABEL}{addition}")
    reading = await over(html, dom.read_apply_modal)

    # It is still FOUND -- this is not the reader losing the control.
    assert reading["submit_present"] is True, what
    assert reading["submit_name"] == "Submit application"
    assert reading["submit_enabled"] is False, what


async def test_aria_disabled_false_is_not_read_as_disabled(over):
    """The control on the control above.

    If the reader tested ``aria-disabled`` for PRESENCE rather than for the
    value "true", both cases above would pass and the reader would also call
    every explicitly-enabled control disabled. That failure is invisible from
    the disabled side, so it is checked from the other one.
    """
    html = derive(markup(), _SUBMIT_LABEL, f'{_SUBMIT_LABEL} aria-disabled="false"')
    reading = await over(html, dom.read_apply_modal)

    assert reading["submit_present"] is True
    assert reading["submit_enabled"] is True


# ---------------------------------------------------------------------------
# 5. Advance controls -- the safety field
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("word", dom.APPLY_ADVANCE_WORDS)
async def test_each_advance_word_is_collected_not_dropped(over, word):
    """One case per word, PARAMETRISED OFF THE PRODUCTION TUPLE.

    Deliberately not a hand-written list of three: a fourth word added to
    ``dom.APPLY_ADVANCE_WORDS`` acquires a case here automatically, where a
    copied list would silently leave the new word untested. The tuple is the
    specification and this reads it.

    THIS IS THE FIELD THE WHOLE GATE RESTS ON. Condition five of
    ``_apply_submit_gate`` is "ZERO advance controls are visible", and it is
    what catches the case nobody has measured -- a multi-step posting. Only a
    single-screen flow has ever been observed. If the reader silently dropped
    an advance control, the gate would see an empty list, conclude single
    screen, and drive a flow this package has never watched finish, toward a
    submit that cannot be withdrawn.

    DERIVED: the base fixture with one extra button in the dialog carrying the
    word.
    """
    reading = await over(advance(markup(), word), dom.read_apply_modal)

    assert reading["submit_present"] is True
    assert reading["advance_names"] == [word], reading["advance_names"]


async def test_an_advance_control_outside_the_dialog_is_not_collected(over):
    """SCOPING, and nothing pinned it before this.

    The advance scan runs over ``[role=dialog] button`` -- modal-scoped by
    construction. Nothing tested that, and the failure it prevents is not
    hypothetical: a real posting page carries page chrome, navigation and
    footers, and "Next" is an ordinary word on a job board. A scan that
    escaped the modal would find advance controls on almost every page and
    refuse almost every apply -- a gate that refuses everything is as useless
    as one that refuses nothing, and it would be read as "LinkedIn changed
    something" rather than as a bug here.

    DERIVED: one of the 42 page-chrome buttons OUTSIDE the dialog relabelled
    "Next". The modal itself is untouched, so the correct answer is the same
    one the base fixture gives.
    """
    html = derive(markup(), "Page control 01", "Next")
    reading = await over(html, dom.read_apply_modal)

    assert reading["modal_present"] is True
    assert reading["submit_present"] is True
    assert reading["submit_enabled"] is True
    assert reading["advance_names"] == []


async def test_an_advance_control_past_the_fortieth_button_is_now_seen(over):
    """THE DEFECT THIS TEST WAS WRITTEN TO PIN IS FIXED, so it now pins the fix.

    IT USED TO ASSERT THE OPPOSITE. The advance scan walked
    ``range(min(total, 40))``, so a "Next" past the fortieth button in the
    dialog came back as ``advance_names: []`` -- and the gate reads an empty
    list as "single-screen flow" and proceeds to submit. The one modal ever
    observed was recorded at 43 buttons, so the margin was three.

    The old assertions are kept in this docstring rather than deleted, because
    the reversal is the point: ``assert hidden["advance_names"] == []`` was a
    true statement about this reader on 2026-08-26 and is a false one now.

    WHAT IS ASSERTED NOW, and it is still a PAIR so that a reader which sees
    nothing anywhere would fail it:

      * a "Next" placed after 41 filler buttons IS collected;
      * THE SAME "Next", same button count, placed first, is ALSO collected.

    Position no longer decides. That is the fix, isolated the same way the
    defect was.

    DERIVED: the base fixture with 41 filler buttons and one "Next" inserted
    into the dialog, in two orders.
    """
    fillers = "".join(
        f'<button type="button">Filler {i:02d}</button>' for i in range(41)
    )
    next_button = '<button type="button">Next</button>'

    buried = derive(markup(), _IN_DIALOG, f"{_IN_DIALOG}{fillers}{next_button}")
    leading = derive(markup(), _IN_DIALOG, f"{_IN_DIALOG}{next_button}{fillers}")

    # The two pages differ ONLY in where the Next sits. Asserted, so that a
    # future edit cannot turn this pair into two different pages and leave the
    # comparison below meaning nothing.
    assert len(buried) == len(leading)
    assert buried != leading

    hidden = await over(buried, dom.read_apply_modal)
    seen = await over(leading, dom.read_apply_modal)

    assert hidden["advance_names"] == ["next"], "the tail is read now"
    assert seen["advance_names"] == ["next"]
    # And both scans FINISHED -- 42 buttons is well inside the tripwire, so
    # neither of these is the incomplete case covered below.
    assert hidden["advance_scan_complete"] is True
    assert seen["advance_scan_complete"] is True


async def test_a_modal_past_the_tripwire_reports_incomplete_rather_than_empty(
    over,
):
    """AN EMPTY RESULT AND AN UNFINISHED SCAN MUST NOT BE THE SAME VALUE.

    This is the rule the old ceiling broke, and it is the same rule this server
    already applies to a nav badge that did not render: absent is not zero.

    A dialog carrying more buttons than ``dom.APPLY_ADVANCE_SCAN_LIMIT`` is not
    sampled. It is not scanned AT ALL -- walking hundreds of controls would
    spend round trips to reach an answer the reader already has -- and it
    reports ``advance_scan_complete: False``.

    THE DISCRIMINATION IS THE ASSERTION. ``advance_names`` is ``[]`` here and
    ``[]`` on a genuinely single-screen modal, and those two pages MUST be
    distinguishable by something. They are, by exactly one field.
    """
    over_limit = dom.APPLY_ADVANCE_SCAN_LIMIT + 1
    fillers = "".join(
        f'<button type="button">Filler {i:03d}</button>' for i in range(over_limit)
    )
    crowded = derive(markup(), _IN_DIALOG, f"{_IN_DIALOG}{fillers}")

    swamped = await over(crowded, dom.read_apply_modal)
    ordinary = await over(markup(), dom.read_apply_modal)

    # Both report no advance controls ...
    assert swamped["advance_names"] == []
    assert ordinary["advance_names"] == []
    # ... and they are NOT the same answer.
    assert swamped["advance_scan_complete"] is False
    assert ordinary["advance_scan_complete"] is True
    assert swamped["buttons_total"] > dom.APPLY_ADVANCE_SCAN_LIMIT


async def test_the_gate_refuses_a_scan_that_did_not_finish():
    """The half that matters: the gate ACTS on the distinction.

    A reader that reports incompleteness into a gate that ignores it has moved
    the defect rather than fixed it. So this drives the real gate over a modal
    dict whose scan did not finish and asserts it stops -- and that the reason
    it gives is the scan, not a missing submit or a disabled one.
    """
    modal = {
        "modal_present": True,
        "submit_present": True,
        "submit_enabled": True,
        "submit_name": "Submit application",
        "advance_names": [],
        "buttons_total": dom.APPLY_ADVANCE_SCAN_LIMIT + 7,
        "advance_scan_complete": False,
    }
    verdict = await _gate_over_modal(modal)
    assert verdict["proceed"] is False
    why = verdict["why"].casefold()
    assert "did not finish" in why, verdict["why"]
    assert "absent is not zero" in why, verdict["why"]


async def test_an_older_modal_dict_without_the_field_refuses():
    """THE DEFAULT REFUSES, which is the only safe direction for a new field.

    Anything handing the gate a dict that predates ``advance_scan_complete``
    -- a stale fake in a future test, a partially-built payload -- must stop
    rather than proceed. ``.get`` returning None has to read as "did not
    finish", never as "finished and found nothing".
    """
    modal = {
        "modal_present": True,
        "submit_present": True,
        "submit_enabled": True,
        "submit_name": "Submit application",
        "advance_names": [],
    }
    verdict = await _gate_over_modal(modal)
    assert verdict["proceed"] is False
    assert "did not finish" in verdict["why"].casefold()


# ---------------------------------------------------------------------------
# 6. The gate, driven over a REAL modal for the first time
# ---------------------------------------------------------------------------
#
# Until now every test of ``_apply_submit_gate`` monkeypatched the reader away,
# so the pair had never been run joined up. These do -- the real gate, calling
# the real reader, over a real parsed DOM.
#
# ONLY THE SHAPES WHERE THE MODAL AND THE SUBMIT ARE BOTH PRESENT are driven
# here, and the reason is mechanical rather than a matter of taste: the gate
# polls up to fifteen times with a one-second ``wait_for_timeout`` between
# attempts, and against a REAL page that sleep is real. A shape that never
# satisfies the break condition costs fifteen seconds per case. Those shapes
# are covered at the reader level above and by the existing dict-driven gate
# tests in tests/test_writes.py; what could only be checked here is that the
# gate and the reader agree when joined, and that is what these do.


async def test_the_gate_reads_the_real_modal_and_proceeds(over):
    """The joined-up positive case. DERIVED input, real reader, real gate."""
    verdict = await over(markup(), writes._apply_submit_gate)

    assert verdict["proceed"] is True, verdict["why"]
    assert verdict["selector"] == dom.APPLY_SUBMIT_SELECTOR
    assert "zero advance controls" in verdict["why"].casefold()


async def test_the_gate_refuses_a_real_multi_step_modal(over):
    """The advance control reaches the gate as a REFUSAL, not just as a field.

    The chain that matters is reader-sees-it -> gate-refuses, and both halves
    had to be assumed before this: the reader was never run, and the gate was
    only ever shown a hand-written list.
    """
    verdict = await over(advance(markup(), "next"), writes._apply_submit_gate)

    assert verdict["proceed"] is False
    assert "more than one step" in verdict["why"].casefold(), verdict["why"]


async def test_the_gate_refuses_a_real_disabled_submit(over):
    """A disabled control, read off the DOM, arriving as the disabled refusal."""
    html = derive(markup(), _SUBMIT_LABEL, f"{_SUBMIT_LABEL} disabled")
    verdict = await over(html, writes._apply_submit_gate)

    assert verdict["proceed"] is False
    assert "disabled" in verdict["why"].casefold(), verdict["why"]


async def test_the_gate_refuses_when_the_hook_and_the_name_disagree(over):
    """Condition four, over a real DOM: both fields must agree.

    The hook still says "easy-apply" and the accessible name says "Submit", and
    each has its own way of being wrong -- so the gate requires corroboration
    rather than trusting whichever it read first.

    DERIVED: only the aria-label is changed, because the aria-label is exactly
    the field the gate reads as ``submit_name``. The replacement carries no
    advance word, so the earlier conditions do not fire first and this really
    is the name branch answering.
    """
    html = derive(markup(), _SUBMIT_LABEL, 'aria-label="Send my application"')
    verdict = await over(html, writes._apply_submit_gate)

    assert verdict["proceed"] is False
    assert "corroborate" in verdict["why"].casefold(), verdict["why"]


# ---------------------------------------------------------------------------
# 7. TWO_CLICK_ACTIONS, and how far perform() actually gets
# ---------------------------------------------------------------------------


async def test_a_save_never_consults_the_apply_gate(writes_on, browser_page,
                                                    monkeypatch):
    """``TWO_CLICK_ACTIONS`` is CONSULTED, shown by execution rather than by
    a string match on the source.

    A test that greps writes.py for the name of a set proves the name is typed
    there. It cannot tell whether the branch runs, and it would go on passing
    against a ``perform`` that had stopped consulting the set entirely.

    So this drives a REAL save the whole way through ``perform``, with the gate
    replaced by something that records being called, and asserts the recorder
    stayed empty. ``save_job`` is not in ``TWO_CLICK_ACTIONS``; one click, no
    gate. The other half of this pair -- an apply that DOES reach the gate --
    is the test immediately below, and it cannot be written yet. See there.

    DERIVED: the saved list served afterwards is ``SAVED_LIST_CONTAINING``,
    already labelled DERIVED where it is defined.
    """
    calls: list[object] = []

    async def _recording_gate(page):
        calls.append(page)
        return {"proceed": False, "selector": "", "modal": {}, "why": "recorded"}

    monkeypatch.setattr(writes, "_apply_submit_gate", _recording_gate)

    grant = await _granted(browser_page, "save_job", target=SAVED_JOB)
    block, _nav = await _perform(
        browser_page, grant, saved=SAVED_LIST_CONTAINING
    )

    assert block["performed"] is True
    assert block["clicked"]["error"] is None
    assert calls == [], (
        "a save consulted the apply gate. Only apply takes two clicks, and a "
        "save that reaches this gate is a save being asked whether it may "
        "submit an application."
    )


async def test_an_apply_now_reaches_the_gate(writes_on, browser_page, monkeypatch):
    """THE MIRROR OF THE SAVE ABOVE, and the test that replaced a blocker pin.

    IT USED TO ASSERT THE OPPOSITE, under the name
    ``test_perform_cannot_reach_the_apply_gate_at_all``. ``anchor_label_for``
    answered only from ``shape.SAVE_LABELS``; ``apply_job`` is valid from
    ``linkedin_apply``, which is not a save state, so the lookup fell through
    to None and perform raised -- explaining itself, on an APPLY, in terms of
    the save control's unphotographed ON state. The two-click loop,
    ``TWO_CLICK_ACTIONS``, ``_apply_submit_gate`` and ``dom.read_apply_modal``
    were all unreachable from ``perform``.

    That old test said it was "EXPECTED TO GO RED the moment that decision is
    taken -- at which point it should be replaced by the real end-to-end apply,
    not relaxed". This is that replacement.

    ``save_job`` is not in ``TWO_CLICK_ACTIONS`` and leaves the recorder empty;
    ``apply_job`` is, and reaches it. One pair, opposite answers, both by
    execution rather than by a string match on the source.

    The gate is replaced by a recorder that REFUSES, so nothing beyond the
    first click is attempted here -- the proceeding case is the test below.
    """
    calls: list[object] = []

    async def _recording_gate(page):
        calls.append(page)
        return {"proceed": False, "selector": "", "modal": {}, "why": "recorded"}

    monkeypatch.setattr(writes, "_apply_submit_gate", _recording_gate)

    grant = await _granted(browser_page, "apply_job", target=JOB)
    assert grant.consumed is True
    assert grant.observation is not None

    block, _nav = await _perform(
        browser_page, grant, applied="jobs_tracker_empty"
    )

    assert len(calls) == 1, (
        "an apply did not reach the apply gate. This is the blocker this test "
        "replaced coming back: perform refused before the click loop."
    )
    # THIS COMMENT SAID "unknown" WAS THE HONEST ANSWER HERE, and it was --
    # while the verification read the SAVED tab, whose three answers do not
    # include "applied", so nothing it could return would ever confirm or deny
    # an application. The read moved to ``?stage=applied`` on 2026-08-31 and
    # the honest answer got better: the tab reads zero and corroborates it, so
    # this is FALSE. It did not happen, and he is told so rather than told to
    # go and look.
    #
    # The Applied tab is served explicitly for that reason. Without it the
    # navigator has no page for that url, the verification read RAISES, and
    # ``unknown`` comes back for a reason that has nothing to do with the
    # gate -- which would be this test passing on the wrong mechanism.
    assert block["performed"] is False, block
    # AND NEVER True, which is the assertion that actually matters: the gate
    # refused, so no submit was pressed, and a True here would be a claim that
    # an irreversible act happened.
    assert block["performed"] is not True, block


async def test_a_proceeding_gate_appends_the_second_click(
    writes_on, browser_page, monkeypatch
):
    """The second half of the two-click loop, observed rather than assumed.

    ``TWO_CLICK_ACTIONS`` only matters if a PROCEED actually appends a second
    click, and until now nothing had ever run that line. The second click is
    aimed at a selector that matches nothing, so the attempt FAILS -- and the
    failure is the observation: ``clicked.error`` naming that selector can only
    be produced by a second ``page.click`` having been issued.

    Nothing is submitted. A selector matching nothing cannot press anything,
    which is why this is the safe way to prove the branch runs.
    """
    sentinel = "#no-such-control-this-test-invented"

    async def _proceeding_gate(page):
        return {"proceed": True, "selector": sentinel, "modal": {}, "why": "test"}

    monkeypatch.setattr(writes, "_apply_submit_gate", _proceeding_gate)

    grant = await _granted(browser_page, "apply_job", target=JOB)
    block, _nav = await _perform(browser_page, grant)

    error = str((block.get("clicked") or {}).get("error") or "")
    assert sentinel in error, (
        "the gate said proceed and no second click was attempted, so the "
        f"append in the click loop did not run. clicked.error was {error!r}"
    )
    # The click failed, so nothing was pressed. ``performed`` reports
    # "unknown" rather than False, and that is the design rather than a
    # shortfall: a click that raised on the way out MAY still have dispatched,
    # so the verification -- not the click -- decides, and it could not read an
    # applied state off a fixture. True is the only forbidden value.
    assert block["performed"] is not True, block


def test_the_apply_anchor_is_the_apply_control_and_not_a_save_label():
    """The one-line cause of the blocker, pinned where it lived.

    ``anchor_label_for`` must answer for apply from the apply control's own
    measured prefix -- the same constant ``dom.APPLY_CONTROL`` and
    ``shape.apply_route`` are built from, so the anchor, the classifier and
    the selector cannot drift apart -- and it must NOT answer from a save
    label, which is what falling through to ``SAVE_LABELS`` produced.
    """
    spec = writes.SANCTIONED_WRITES["linkedin_apply_job"]
    anchor = writes.anchor_label_for(spec)

    assert anchor == shape.LINKEDIN_APPLY_PREFIX
    assert anchor is not None, "the blocker is back"
    assert anchor not in shape.SAVE_LABELS, (
        "apply is anchored on a SAVE label, which is the fall-through that "
        "caused the blocker rather than a fix for it."
    )


async def test_gate_five_re_reads_the_apply_control_not_the_save_button(
    writes_on, browser_page
):
    """Gate 5 must re-read THE VERY CONTROL the click will land on.

    Without an apply branch, ``_live_control`` fell through to
    ``dom.read_save_control`` -- so on an apply it corroborated the SAVE
    button, which is the wrong element and would have built the wrong
    selector.

    The selector it returns is ``dom.LINKEDIN_APPLY_CONTROL``, which is
    narrower than ``dom.APPLY_CONTROL`` on purpose: the off-site refusal rests
    on never driving the other route's control, and a selector that CANNOT
    match it is worth more than one that merely does not today.
    """
    spec = writes.SANCTIONED_WRITES["linkedin_apply_job"]
    grant = await _granted(browser_page, "apply_job", target=JOB)

    state, why, selector = await writes._live_control(
        browser_page, spec, grant, writes.anchor_label_for(spec)
    )

    assert state == "linkedin_apply", why
    assert selector == dom.LINKEDIN_APPLY_CONTROL
    assert selector != dom.APPLY_CONTROL, (
        "gate 5 handed back the two-route finder as a click target. That "
        "selector also matches 'Apply on company website'."
    )


async def test_gate_five_refuses_an_offsite_posting_and_hands_back_no_selector(
    writes_on, browser_page, over
):
    """THE MOST IMPORTANT PROPERTY OF THE NEW APPLY BRANCH IN GATE 5.

    An off-site posting submits on a third party's applicant-tracking system,
    on their domain, under their terms. That refusal does not rest on anything
    that a better capture could lift -- it is not this server's form to drive
    -- so gate 5 must refuse it, and must refuse it by returning NO SELECTOR,
    since a selector is what the caller requires before it clicks.

    Written because the branch is new: before 2026-08-26 ``_live_control``
    fell through to the save control for apply, so this path did not exist to
    be got wrong. A new branch that decides whether an irreversible action may
    proceed gets its refusal tested on the first day, not the second.

    The state is asserted as ``offsite`` specifically rather than merely "not
    linkedin_apply", because a job-id mismatch between the grant and the
    fixture would ALSO refuse -- and would refuse for a reason that has nothing
    to do with the route, leaving this test passing while testing nothing.
    """
    spec = writes.SANCTIONED_WRITES["linkedin_apply_job"]
    grant = await _granted(browser_page, "apply_job", target=JOB)
    offsite = (FIXTURE_DIR / "job_detail_following_hydrated.html").read_text(
        encoding="ascii"
    )

    async def work(page):
        return await writes._live_control(
            page, spec, grant, writes.anchor_label_for(spec)
        )

    state, why, selector = await over(offsite, work)

    assert selector == "", (
        "gate 5 handed back a click target for an OFF-SITE posting. The "
        f"caller clicks whatever this returns. why={why!r}"
    )
    assert state != "linkedin_apply", why
    assert state == "offsite", (
        "refused, but not as an off-site posting -- so this test is not "
        f"measuring the route refusal. state={state!r} why={why!r}"
    )


# ---------------------------------------------------------------------------
# THE TWO DEFECTS A LIVE APPLY EXPOSED, 2026-08-31
# ---------------------------------------------------------------------------
#
# The operator authorised his first apply and it was performed. It did NOT
# submit -- the gate held, on an irreversible action, on a real posting with a
# real employer at the other end, and that is the design working. What it
# could not do was explain itself, and what it DID say was read off the wrong
# surface entirely.


#: The tracker with an APPLIED count of one and a row on it. DERIVED, and
#: labelled as such: the Applied tab has read ZERO on every reading anybody
#: has taken, so a page showing an application cannot be photographed and has
#: to be built. The row's job id is the one these tests act on.
#:
#: THE ASSERTIONS ARE NOT DECORATION. A ``replace`` whose anchor has drifted is
#: a silent no-op, and a verification test running against a tracker that
#: still says zero would pass while proving nothing.
#:
#: DERIVED TWICE, and both halves are labelled. The frozen row carries
#: ``SAVED_JOB`` and the posting fixture an apply is previewed against is
#: ``JOB``, and the gate REFUSES a control belonging to a different posting --
#: measured, by writing this test the other way round first. So the id is
#: rewritten as well as the count.
APPLIED_LIST_OF_ONE = (
    fixture_markup("jobs_tracker_row")
    .replace("Applied &#183; 0", "Applied &#183; 1")
    .replace(SAVED_JOB, JOB)
)
assert APPLIED_LIST_OF_ONE != fixture_markup("jobs_tracker_row")
assert "Applied &#183; 1" in APPLIED_LIST_OF_ONE
assert JOB in APPLIED_LIST_OF_ONE and SAVED_JOB not in APPLIED_LIST_OF_ONE, (
    "the id rewrite anchored on something that has drifted, so the positive "
    "verification test would assert a MISS and pass while proving nothing."
)

#: The tracker as the LIVE ACCOUNT READS IT: Applied 0, corroborated empty.
#: Used unmodified, because this one IS the measured shape -- the lead read
#: exactly this on 2026-08-31 after the live apply.
APPLIED_LIST_EMPTY = "jobs_tracker_empty"


async def test_an_apply_is_verified_against_the_applied_tab(
    writes_on, browser_page, monkeypatch
):
    """DEFECT 1: it was verified against the SAVED tab.

    NOT A WRONG STRING -- A CHECK THAT COULD NOT PASS. ``apply_job``'s
    ``to_state`` is ``"applied"`` and ``_read_saved_state`` returns
    ``"saved"``, ``"not_saved"`` or ``"unknown"``, so ``verified_state ==
    "applied"`` was FALSE on every reading it could ever take. Every apply this
    server can perform was going to report ``performed: "unknown"``, and the
    live one did -- while reporting that the posting is still in his Saved
    list, which is true and is not evidence about an application.

    Reading ``?stage=applied`` answers it outright. The lead did exactly that
    by hand, in one call, and got a corroborated zero.
    """

    async def _proceeding_gate(page):
        return {
            "proceed": True,
            "selector": "#nothing",
            "modal": {},
            "why": "test",
            "refused_condition": None,
        }

    monkeypatch.setattr(writes, "_apply_submit_gate", _proceeding_gate)
    grant = await _granted(browser_page, "apply_job", target=JOB)
    block, nav = await _perform(browser_page, grant, applied=APPLIED_LIST_OF_ONE)

    assert block["verification"]["read_from"] == writes.APPLIED_LIST_URL, block[
        "verification"
    ]
    assert writes.SAVED_LIST_URL not in nav.gotos, (
        "the verification loaded the Saved tab, which cannot answer this "
        f"question. gotos={nav.gotos}"
    )
    assert writes.APPLIED_LIST_URL in nav.gotos, nav.gotos
    assert block["verification"]["observed_state"] == "applied"
    assert block["performed"] is True, block


async def test_an_apply_that_did_not_submit_reports_false_not_unknown(
    writes_on, browser_page, monkeypatch
):
    """THE LIVE CASE, and the answer it should have given.

    The gate refused, nothing was submitted, and the Applied tab reads zero
    and corroborates it. That is not "nobody could tell" -- it is "it did not
    happen", and the difference is the whole value of the field on an action
    the caller MUST NOT retry to find out.

    ``"not_applied"`` is a state of its own rather than ``from_state``,
    because ``from_state`` is ``"linkedin_apply"`` -- a claim about which
    ROUTE the posting's control takes, which a tracker read establishes
    nothing about. ``WriteSpec.not_performed_state`` is what maps it.
    """

    async def _refusing_gate(page):
        return {
            "proceed": False,
            "selector": "",
            "modal": {},
            "why": "test refusal",
            "refused_condition": "3_submit_disabled",
        }

    monkeypatch.setattr(writes, "_apply_submit_gate", _refusing_gate)
    grant = await _granted(browser_page, "apply_job", target=JOB)
    block, _nav = await _perform(browser_page, grant, applied=APPLIED_LIST_EMPTY)

    assert block["verification"]["observed_state"] == "not_applied", block[
        "verification"
    ]
    assert block["performed"] is False, block
    # AND NEVER True. Everything else here is about precision; this is about
    # not telling him an irreversible act happened when it did not.
    assert block["performed"] is not True


async def test_a_partial_applied_tab_is_unknown_rather_than_not_applied(
    writes_on, browser_page, monkeypatch
):
    """ABSENCE FROM A PARTIAL LIST IS NOT ABSENCE, and it matters more here.

    On the Saved tab that rule means a save cannot be confirmed. On the
    APPLIED tab, read as an answer, it would mean telling him an irreversible
    act did not happen when the row is merely below the fold. So a tab whose
    own count disagrees with the rows drawn comes back ``unknown``, and
    ``unknown`` is the honest answer there.
    """

    async def _refusing_gate(page):
        return {
            "proceed": False,
            "selector": "",
            "modal": {},
            "why": "test refusal",
            "refused_condition": "1_modal_absent",
        }

    monkeypatch.setattr(writes, "_apply_submit_gate", _refusing_gate)
    partial = fixture_markup("jobs_tracker_row").replace(
        "Applied &#183; 0", "Applied &#183; 9"
    )
    assert "Applied &#183; 9" in partial
    grant = await _granted(browser_page, "apply_job", target=JOB)
    block, _nav = await _perform(browser_page, grant, applied=partial)

    assert block["verification"]["observed_state"] == writes.UNKNOWN, block[
        "verification"
    ]
    assert block["performed"] == writes.UNKNOWN
    assert "fraction of itself" in block["verification"]["why"]


async def test_the_submit_gates_refusal_reaches_the_caller(
    writes_on, browser_page, monkeypatch
):
    """DEFECT 2: the gate named its condition and nobody was told.

    ``_apply_submit_gate`` produces a specific sentence for whichever of its
    five conditions refused. ``perform`` assigned that dict to a local and
    NEVER READ IT AGAIN, so the caller received ``performed`` and no way to
    learn why -- on the one action where re-running to find out is exactly
    what the docstring forbids, because a retry on something that may have
    half-landed is the failure being guarded against.
    """
    observed = {
        "modal_present": True,
        "submit_present": True,
        "submit_enabled": False,
        "submit_name": "Submit application",
        "advance_names": [],
        "advance_scan_complete": True,
        "buttons_total": 4,
    }

    async def _refusing_gate(page):
        return {
            "proceed": False,
            "selector": "",
            "modal": dict(observed),
            "why": "the submit control is present but disabled",
            "refused_condition": "3_submit_disabled",
        }

    monkeypatch.setattr(writes, "_apply_submit_gate", _refusing_gate)
    grant = await _granted(browser_page, "apply_job", target=JOB)
    block, _nav = await _perform(browser_page, grant, applied=APPLIED_LIST_EMPTY)

    gate = block["submit_gate"]
    assert gate is not None, block
    assert gate["proceeded"] is False
    assert gate["refused_condition"] == "3_submit_disabled"
    assert "disabled" in gate["why"]
    # THE READING, not just the verdict. An unfinished advance scan is why
    # "no advance controls" can mean UNKNOWN rather than none, so the caller
    # needs the scan's own completion flag beside the list.
    assert gate["observed"] == observed
    assert gate["scan_limit"] == dom.APPLY_ADVANCE_SCAN_LIMIT
    # AND IT DOES NOT OVERSTATE ITSELF. One reading of a modal is not evidence
    # that the posting cannot be applied to.
    assert gate["what_this_is_not"].startswith("a verdict about the posting")
    assert "establish which condition failed" in gate["what_this_is_not"]


async def test_an_action_with_no_submit_gate_carries_none(
    writes_on, browser_page
):
    """THE FIELD IS ALWAYS PRESENT AND IS ``None`` WHERE THERE WAS NO GATE.

    A key that appears only sometimes is a key a caller learns to guess at.
    ``save_job`` has one click and no gate between two, so the honest value is
    ``None`` -- distinct from a gate that ran and refused.
    """
    grant = await _granted(browser_page, "save_job", target=JOB)
    block, _nav = await _perform(browser_page, grant, saved=SAVED_LIST_CONTAINING)
    assert "submit_gate" in block
    assert block["submit_gate"] is None


@pytest.mark.parametrize(
    "modal,expected",
    [
        ({"modal_present": False}, "1_modal_absent"),
        ({"modal_present": True, "submit_present": False}, "2_no_submit_control"),
        (
            {
                "modal_present": True,
                "submit_present": True,
                "advance_scan_complete": False,
                "buttons_total": 40,
            },
            "5_advance_scan_incomplete",
        ),
        (
            {
                "modal_present": True,
                "submit_present": True,
                "advance_scan_complete": True,
                "advance_names": ["Next"],
            },
            "5_multi_step_flow",
        ),
        (
            {
                "modal_present": True,
                "submit_present": True,
                "advance_scan_complete": True,
                "advance_names": [],
                "submit_enabled": False,
            },
            "3_submit_disabled",
        ),
        (
            {
                "modal_present": True,
                "submit_present": True,
                "advance_scan_complete": True,
                "advance_names": [],
                "submit_enabled": True,
                "submit_name": "Continue",
            },
            "4_name_does_not_corroborate",
        ),
    ],
    ids=lambda v: str(v)[:32],
)
async def test_each_of_the_five_conditions_names_itself(
    monkeypatch, modal, expected
):
    """ALL FIVE, EACH REACHED, EACH NAMING ITSELF.

    The docstring has listed five conditions since apply shipped and the
    result named none of them. Naming them in prose only would leave a caller
    parsing sentences; a code is branchable, and the prose stays beside it.

    Condition 5 has TWO codes because it has two ways of failing and they are
    not the same fact: a flow that HAS a Next, and a scan that could not
    finish and therefore cannot say whether one exists. Absent is not zero,
    which is the rule the whole reader is built on.
    """

    async def _reading(page):
        return dict(modal)

    class _NoWait:
        async def wait_for_timeout(self, _ms):
            return None

    monkeypatch.setattr(dom, "read_apply_modal", _reading)
    out = await writes._apply_submit_gate(_NoWait())
    assert out["proceed"] is False
    assert out["refused_condition"] == expected, out["why"]
    assert out["why"], "a refusal with no sentence beside its code"
