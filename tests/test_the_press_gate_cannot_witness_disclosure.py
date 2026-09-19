"""THE PRESS GATE CANNOT TELL A DISCLOSURE FROM A PRESS THAT MISSED.

This is not a defect in a run. It is a property of :func:`press.disclose`, and
it is visible in the order of four lines::

    expanded_before = await locator.get_attribute("aria-expanded")
    await locator.click(...)
    await page.keyboard.press("Escape")          # <-- DISMISSED FIRST
    expanded_after = await locator.get_attribute("aria-expanded")

**``expanded_after`` is read AFTER the dismissal.** Nothing reads the control
while it is open. So a press that opened a panel and a press that landed on
nothing both leave ``before == after``, and ``check_closure`` -- which requires
exactly that equality -- passes for both.

The first sanctioned press (`_audit/2026-09-19-the-first-sanctioned-press.md`)
recorded that its two readings could not be separated and filed it as a limit
of the run. **It is a limit of the gate**, and the difference is the whole
reason this file exists: a limit of a run is fixed by running again, and this
one is not. Every future press through this gate inherits the same silence.

## What this file proves, by construction rather than by argument

THREE pages are built that differ IN THE WORLD:

    opens    the control really opens     aria-expanded false -> true
    misses   the press lands on nothing   nothing changes
    dialog   it really opens, AS A DIALOG, and the control's own
             aria-expanded never moves

``disclose`` returns **one identical verdict for all three.**

## The control, without which this file certifies nothing

**A test asserting that things are INDISTINGUISHABLE passes trivially if it is
comparing the wrong thing.** So a fourth case is built that differs in a way
the verdict DOES carry -- a moved counter -- and the same comparison is shown
SEPARATING it. Only then is "these three compare equal" a finding about the
gate rather than a fact about a blind comparison.

## What this file does NOT claim

It does not claim the press was unsafe: the four safety conditions are
untouched and still pass, and they are re-asserted at the bottom so nobody
reads this as an argument against the gate. It does not claim the panel failed
to open on the live run -- **that is precisely the thing nobody can currently
say.** It claims the question is unanswerable through this gate as written.

The verified fix is one reading taken between the click and the dismissal, and
`dialog` above is the case that decides its design: a witness that reads only
the control's own attribute reports that real disclosure as a miss.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import press  # noqa: E402

ADMITTED_URL = "https://www.linkedin.com/analytics/profile-views/"
SHAPE = "[aria-expanded]"

#: The three worlds. Named here so a reader sees the space before the fakes.
WORLDS = ("opens", "misses", "dialog")


# ---------------------------------------------------------------------------
# Pages whose aria-expanded is a STATE, which the shipped fakes do not model
# ---------------------------------------------------------------------------


class StatefulLocator:
    """The shipped ``FakeLocator`` hands out a fixed SEQUENCE of readings, so a
    click cannot change what a later read returns. That fake shares the gate's
    blind spot and can never exhibit the difference this file is about."""

    def __init__(self, page, selector):
        self.page = page
        self.selector = selector

    def nth(self, _index):
        return self

    async def count(self):
        return self.page.count_for(self.selector)

    async def get_attribute(self, name):
        assert name == "aria-expanded", name
        self.page.reads.append(self.page.expanded)
        return self.page.expanded

    async def click(self, **_kwargs):
        self.page.clicks.append(self.selector)
        self.page.open_it()


class StatefulKeyboard:
    def __init__(self, page):
        self.page = page

    async def press(self, key):
        self.page.keys.append(key)
        # THE WHOLE POINT: what was true at the instant of dismissal. This is
        # the information the gate discards.
        self.page.state_at_dismissal = self.page.snapshot()
        if key == "Escape":
            self.page.close_it()


class StatefulPage:
    def __init__(self, mode: str):
        assert mode in WORLDS, mode
        self.url = ADMITTED_URL
        self.mode = mode
        self.expanded = "false"
        self.expanded_true = 0
        self.dialogs = 0
        self.state_at_dismissal = None
        self.clicks: list[str] = []
        self.keys: list[str] = []
        self.reads: list[str] = []
        self.keyboard = StatefulKeyboard(self)

    def snapshot(self) -> dict:
        return {
            "expanded": self.expanded,
            "expanded_true": self.expanded_true,
            "dialogs": self.dialogs,
        }

    def open_it(self):
        if self.mode == "opens":
            self.expanded, self.expanded_true = "true", 1
        elif self.mode == "dialog":
            # IT OPENED. Its own attribute did not move.
            self.dialogs = 1

    def close_it(self):
        self.expanded, self.expanded_true, self.dialogs = "false", 0, 0

    def count_for(self, selector):
        if selector == '[aria-expanded="true"]':
            return self.expanded_true
        if selector == '[role="dialog"]':
            return self.dialogs
        return 1

    def locator(self, selector):
        return StatefulLocator(self, selector)


def _steady_counters(values=(0, 6)):
    async def read():
        return {"invitations": values[0], "notifications_unread": values[1]}

    return read


def _moving_counters():
    """A counter that moves on the second reading. The verdict DOES carry this."""
    state = {"n": 0}

    async def read():
        state["n"] += 1
        return {"invitations": 0 if state["n"] == 1 else 1}

    return read


def _press(mode, counters=None):
    page = StatefulPage(mode)
    verdict = asyncio.run(
        press.disclose(page, shape=SHAPE, read_counters=counters or _steady_counters())
    )
    return page, verdict


# ---------------------------------------------------------------------------
# THE CONTROL FIRST. A comparison that cannot separate anything proves nothing.
# ---------------------------------------------------------------------------


def test_the_comparison_can_separate_two_verdicts_when_the_gate_carries_it():
    """SHOWN SEPARATING, before it is trusted to report a collision."""
    _, unmoved = _press("opens")
    _, moved = _press("opens", _moving_counters())

    assert unmoved != moved, (
        "the comparison cannot distinguish a permitted press from a refused "
        "one, so it is not fit to report that anything is indistinguishable"
    )
    assert not unmoved.get("refused")
    assert moved.get("refused") == "counter_moved"


# ---------------------------------------------------------------------------
# THE FINDING
# ---------------------------------------------------------------------------


def test_three_different_worlds_now_return_THREE_DIFFERENT_VERDICTS():
    """REWRITTEN 2026-09-19, WHICH IS WHAT THIS FILE ASKED FOR.

    It used to assert the three verdicts were IDENTICAL, with the instruction
    that if they ever differed the gate had gained a disclosure witness and the
    test should be rewritten rather than deleted. It has, and this is that
    rewrite.

    ``press.disclose`` now takes a third reading BETWEEN the click and the
    dismissal -- the only instant at which disclosure exists to be seen -- and
    reports it as ``witness``, alongside the verdict and never deciding it.
    """
    verdicts = {mode: _press(mode)[1] for mode in WORLDS}

    # PERMISSION IS UNCHANGED IN ALL THREE, which is the half that must not
    # have moved: the witness is a READING, not a fifth condition.
    for mode, verdict in verdicts.items():
        assert verdict.get("permitted") is True, mode

    assert verdicts["opens"]["witness"]["disclosed"] is True
    assert verdicts["dialog"]["witness"]["disclosed"] is True
    assert verdicts["misses"]["witness"]["disclosed"] is False

    # And the three are no longer one object.
    assert verdicts["opens"] != verdicts["misses"]
    assert verdicts["dialog"] != verdicts["misses"]


def test_a_miss_is_reported_as_a_miss_and_not_as_a_failure():
    """A permitted press that disclosed nothing is still a permitted press.

    The wording matters: ``disclosed: False`` must not read as a refusal, or
    the next caller will treat an uninformative press as an unsafe one and the
    witness will have become the fifth condition it was built not to be.
    """
    _, verdict = _press("misses")
    assert verdict["pressed"] is True
    assert verdict["permitted"] is True
    assert verdict["witness"]["disclosed"] is False
    assert "miss" in verdict["witness"]["why"].lower()


def test_an_unread_witness_is_undetermined_and_never_false():
    """None is not False, for the same reason an unreadable counter is not a
    zero: a reading that did not happen and a reading that saw nothing are
    different facts and only one of them is evidence."""
    assert press.witness_verdict(None, None)["disclosed"] is None
    assert press.witness_verdict({}, {})["disclosed"] is None
    assert press.witness_verdict({"a": 1}, {"b": 1})["disclosed"] is None


def test_the_distinguishing_state_IS_NOW_READ():
    """THE FIX LANDED, AND THIS IS THE LINE THAT SHOWS IT.

    The three pages still hold different states at the open moment -- the
    information was never missing from the world. It is now in the verdict
    too.
    """
    pages = {mode: _press(mode)[0] for mode in WORLDS}

    assert pages["opens"].state_at_dismissal == {
        "expanded": "true", "expanded_true": 1, "dialogs": 0
    }
    assert pages["misses"].state_at_dismissal == {
        "expanded": "false", "expanded_true": 0, "dialogs": 0
    }
    assert pages["dialog"].state_at_dismissal == {
        "expanded": "false", "expanded_true": 0, "dialogs": 1
    }

    distinct = {tuple(sorted(p.state_at_dismissal.items())) for p in pages.values()}
    assert len(distinct) == 3, "three worlds, three states, at the open moment"

    # AND THE GATE NOW READS THE CONTROL THREE TIMES, not twice. The third is
    # the one taken while the disclosure is still open.
    for mode, page in pages.items():
        assert len(page.reads) == 3, mode
        assert page.reads[0] == "false", mode
        assert page.reads[2] == "false", mode  # after the dismissal


def test_a_one_attribute_witness_would_call_the_dialog_a_miss():
    """THE CASE THAT DECIDES THE WITNESS DESIGN.

    A witness reading only the pressed control's own ``aria-expanded`` sees
    ``false`` on the dialog page while a dialog is open on it. It would report
    a real disclosure as a press that missed -- the false negative that makes
    a witness worse than none, because it manufactures a confident wrong
    answer where there was an honest silence.
    """
    dialog = _press("dialog")[0]

    assert dialog.state_at_dismissal["expanded"] == "false"
    assert dialog.state_at_dismissal["dialogs"] == 1

    # The page-wide readings are what separate it from a genuine miss.
    miss = _press("misses")[0]
    assert dialog.state_at_dismissal["expanded"] == miss.state_at_dismissal["expanded"]
    assert dialog.state_at_dismissal["dialogs"] != miss.state_at_dismissal["dialogs"]


def test_the_gate_now_takes_THREE_readings_and_the_middle_one_is_inside():
    """REWRITTEN 2026-09-19. The count was the argument and the count moved.

    It used to assert exactly TWO readings, with the note that *a third reading
    between the click and the Escape is exactly what a disclosure witness is*.
    That is now what happens, so the assertion is inverted rather than removed
    -- the sentence was right and the code caught up with it.

    Two readings cannot describe three states. Three can, and the middle one is
    taken at the only instant the disclosure exists.
    """
    page, verdict = _press("opens")

    assert len(page.reads) == 3, (
        "the witness reading between the click and the dismissal is gone; "
        "without it the gate is blind to disclosure again."
    )
    assert page.reads == ["false", "true", "false"], (
        "the middle reading must be taken while the control is OPEN -- before "
        "the press it is closed, and after the dismissal it is closed again."
    )
    assert verdict["witness"]["disclosed"] is True

    # AND STILL EXACTLY ONE CLICK AND ONE DISMISSAL. The witness reads; it
    # must never press. A third observation that cost a second interaction
    # would be a second press wearing an observer's clothes.
    assert page.clicks == [SHAPE]
    assert page.keys == ["Escape"]


def test_closure_passes_on_a_press_that_never_opened_anything():
    """``check_closure`` is a SAFETY check and this is not a bug in it.

    It asks "was the page left as found". A press that did nothing leaves the
    page as found, correctly and trivially. The error would be reading its
    pass as evidence that something was disclosed.
    """
    assert press.check_closure("false", "false") == {"pressed": False, "closed": True}

    # AND THE NAME IS THE WARNING. It reports ``closed``, which is what it
    # measured. It does not report ``opened`` or ``disclosed`` -- two things a
    # reader might hear in it and neither of which it checked.
    verdict = press.check_closure("false", "false")
    assert "opened" not in verdict
    assert "disclosed" not in verdict


# ---------------------------------------------------------------------------
# The safety conditions are untouched by all of the above, re-asserted here so
# that nobody reads this file as an argument against the gate.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("mode", WORLDS)
def test_the_safety_conditions_still_hold_whichever_happened(mode):
    page, verdict = _press(mode)

    assert verdict.get("priced_by") == ["invitations", "notifications_unread"]
    assert verdict.get("shape") == SHAPE
    assert page.clicks == [SHAPE], "exactly one control, and it is the shape"
    assert page.keys == ["Escape"], "it was dismissed"


@pytest.mark.parametrize("mode", WORLDS)
def test_a_moved_counter_is_terminal_in_every_world(mode):
    """Whether anything was disclosed has no bearing on whether it was safe."""
    _, verdict = _press(mode, _moving_counters())
    assert verdict.get("refused") == "counter_moved"
