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

from linkedin_server import dom, writes
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

FIXTURE_DIR = Path(__file__).parent / "fixtures"

#: Fixed so that a visibility answer is reproducible. ``read_apply_modal``
#: calls ``is_visible()`` on every control it considers, and a test that let
#: the viewport float would be reading a different page on a different machine.
VIEWPORT = {"width": 1280, "height": 720}


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


async def test_an_advance_control_past_the_fortieth_button_is_not_seen(over):
    """FINDING, PINNED RATHER THAN FIXED. THE SAFETY FIELD HAS A CEILING.

    The advance scan walks ``range(min(total, 40))``. A modal with more than
    forty buttons has its tail read by nobody, and an advance control in that
    tail is reported as absent -- which the gate reads as "single-screen flow"
    and allows.

    THE NUMBER MATTERS. The one apply modal ever observed was recorded as
    having 43 buttons. Whether all 43 sat inside the dialog was never written
    down, so this is not a claim that the live flow trips the cap -- it is the
    observation that the only number anybody recorded is ABOVE THE CEILING,
    which makes the margin somewhere between three buttons and unknown.

    Both halves are asserted, because the first alone would not distinguish a
    cap from a reader that never sees anything:

      * a "Next" placed after 41 filler buttons is NOT collected;
      * THE SAME "Next", on a page with THE SAME button count, placed first,
        IS collected.

    One edit apart, opposite answers. That is the cap, isolated.

    NOT FIXED HERE. Raising or removing the bound is a production change and a
    decision for whoever owns dom.py; this module adds coverage only. What
    would settle the risk is a recount of the live modal that records how many
    buttons are inside the dialog rather than on the page.

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

    # THE FINDING: the same control, past the cap, vanishes.
    assert hidden["advance_names"] == []
    # THE CONTROL ON THE FINDING: it is the position, not the reader.
    assert seen["advance_names"] == ["next"]


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


async def test_perform_cannot_reach_the_apply_gate_at_all(writes_on, browser_page):
    """BLOCKER, PINNED. ``perform`` refuses ``apply_job`` BEFORE the click loop.

    THIS IS THE TEST THAT WAS MEANT TO BE THE END-TO-END APPLY, and it cannot
    be, because the path does not reach that far. Measured 2026-08-26 by
    driving the real path -- preview, consume, perform -- with a real redeemed
    grant:

        anchor_label_for(spec) returns None for apply_job, and perform raises
        "'apply_job' has no measured anchor and will not be performed".

    WHY. ``anchor_label_for`` answers from ``shape.SAVE_LABELS``, which maps
    accessible names to SAVE states and holds exactly one row,
    ``{"Save the job": "not_saved"}``. ``apply_job`` is valid from
    ``linkedin_apply``, which is not a save state and is not in that table, so
    the lookup falls through to ``None`` and perform takes the branch written
    for ``unsave_job`` -- whose message then explains, on an APPLY, that the
    save control's ON state has never been photographed.

    WHAT IS THEREFORE UNREACHABLE FROM ``perform`` TODAY: the two-click loop,
    ``TWO_CLICK_ACTIONS``, ``_apply_submit_gate``, and ``dom.read_apply_modal``
    -- the entire subsystem this module tests. Every one of those is exercised
    above by calling it directly, which is worth having and is NOT the same
    claim as "apply works end to end". Nobody should read this file as saying
    that.

    NOT FIXED HERE, and deliberately so. Whether apply should get an anchor,
    or be exempted from the anchor gate the way it is already exempted from the
    save family everywhere else, is a production change and a decision for
    whoever owns writes.py. This test exists so the dead subsystem cannot be
    forgotten, and it is EXPECTED TO GO RED the moment that decision is taken
    -- at which point it should be replaced by the real end-to-end apply, not
    relaxed.
    """
    grant = await _granted(browser_page, "apply_job", target=JOB)
    assert grant.consumed is True
    assert grant.observation is not None

    with pytest.raises(WriteAttemptError) as excinfo:
        await _perform(browser_page, grant)

    message = str(excinfo.value)
    assert "no measured anchor" in message, message
    assert "linkedin_apply" in message, message
    # The message a caller gets is the SAVE family's, on an apply. Pinned
    # because it is part of the finding: the refusal is not merely early, it
    # explains itself in terms of a control this action never touches.
    assert "the save control wears" in message, message
