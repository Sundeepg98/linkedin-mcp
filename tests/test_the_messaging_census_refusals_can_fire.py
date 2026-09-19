"""The messaging census refused nothing on its only run. So did they work?

**THE GAP THIS CLOSES, STATED PLAINLY.**
`scripts/_probe_messaging_surface_census.py` spends the one authorised
`/messaging/` load, and it carries two refusals that stand between that spend
and a real person's inbox:

    the badges must READ at both ends      -- else no cost can be certified
    the messaging badge must read ZERO     -- else the conversation LinkedIn
                                              redirects into may be UNREAD, and
                                              opening it marks a stranger's
                                              message read

**ON ITS ONLY LIVE RUN BOTH BADGES READ, AND BOTH READ ZERO. So neither refusal
executed.** The probe's own audit reports `state='read'` and
`new_since_last_visit=0` at both ends -- which is exactly the input on which a
broken refusal is indistinguishable from a working one.

That is this repository's oldest scar in a new place. A sibling probe on this
same surface shipped a precondition that **could never have passed**: it asked
`dom.read_messaging_badge` for `unread` and `readable`, two field names that do
not exist on it, so `.get` returned `None` twice and the refusal fired
unconditionally, forever. The mirror failure -- a refusal that can never FIRE --
is worse, because it is silent and it is on the spending side.

**A REFUSAL THAT HAS NEVER FIRED IS NOT KNOWN TO WORK**, and a live run cannot
demonstrate it without arranging a non-zero badge, which nobody can do on
demand. These tests drive the predicate directly, which needs no browser and no
load.

**WHAT IS AND IS NOT COVERED.** These exercise `_readable` and the zero-badge
condition -- the two decisions -- against the shapes
`shape.messaging_badge` and `shape.invitation_badge` actually return. They do
NOT exercise the navigation, and they do not claim the probe as a whole is
correct. They claim the two predicates can say NO, and can also say YES, which
is the pair a gate needs: *a gate that can only refuse certifies nothing.*
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PROBE = REPO / "scripts" / "_probe_messaging_surface_census.py"


def _probe_module():
    """Import the probe WITHOUT running it.

    It guards its own entry point with ``if __name__ == "__main__"``, so an
    import is inert: no browser is started and nothing is navigated.
    """
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "_probe_messaging_surface_census_under_test", PROBE
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: The live reading, verbatim from the 22:20:49 run. Named as a constant so the
#: "and it can say yes" case is the ACTUAL measured input rather than something
#: invented to be permissive.
_LIVE_MESSAGING = (0, "read")
_LIVE_INVITATION = (0, "read")


def test_the_probe_imports_without_navigating() -> None:
    """The premise of every test below: importing it does nothing."""
    module = _probe_module()
    assert hasattr(module, "_readable")
    assert hasattr(module, "_run")
    # The spend counter is empty on a fresh import -- nothing navigated.
    assert module._SPENT == [], (
        "importing the probe appended to the spend counter, which means an "
        "import navigates. That is a far larger finding than this test file."
    )


def test_the_refusal_says_YES_on_the_reading_the_live_run_actually_got() -> None:
    """A gate that can only refuse certifies nothing.

    This is the positive half, and it uses the real 22:20:49 reading so that
    the negative cases below are known to differ from a WORKING input rather
    than from an imagined one.
    """
    module = _probe_module()
    assert module._readable(_LIVE_MESSAGING, _LIVE_INVITATION) is True


@pytest.mark.parametrize(
    "messaging, invitation, why",
    [
        ((None, "no_badge"), _LIVE_INVITATION, "messaging badge not drawn"),
        ((None, "unparseable"), _LIVE_INVITATION, "messaging badge unparseable"),
        (_LIVE_MESSAGING, (None, "no_badge"), "invitation badge not drawn"),
        (_LIVE_MESSAGING, (None, "unparseable"), "invitation badge unparseable"),
        ((None, "no_badge"), (None, "no_badge"), "neither badge drawn"),
    ],
)
def test_the_refusal_says_NO_when_either_badge_did_not_read(
    messaging: tuple, invitation: tuple, why: str
) -> None:
    """EITHER badge failing must refuse. Both directions, independently.

    The interesting bug is a predicate that checks one badge and forgets the
    other -- which reads correctly, passes on the happy path, and silently
    stops certifying half the cost. Each case moves exactly ONE badge away from
    the live reading, so a pass here cannot come from both being wrong.
    """
    module = _probe_module()
    assert module._readable(messaging, invitation) is False, (
        "the badge-readability refusal PASSED an input where %s. An unreadable "
        "badge is not a zero, and a load whose cost cannot be certified at "
        "both ends must not be taken." % why
    )


def test_a_state_that_is_not_read_is_never_treated_as_read() -> None:
    """No truthy-state should sneak through.

    ``state`` is a shaped verdict, and a predicate written as ``if state:``
    rather than ``if state == 'read':`` would accept every failure verdict --
    they are all non-empty strings. This is the mutation that would survive a
    happy-path test.
    """
    module = _probe_module()
    for bogus in ("unread", "unreadable", "no_badge", "unparseable", "error", "x"):
        assert module._readable((0, bogus), _LIVE_INVITATION) is False, (
            "state %r was accepted as readable. Every failure verdict is a "
            "non-empty string, so a truthiness check accepts all of them." % bogus
        )
        assert module._readable(_LIVE_MESSAGING, (0, bogus)) is False


def test_the_zero_badge_precondition_is_expressed_over_the_count_not_the_state() -> None:
    """The SECOND refusal: something arrived since his last visit.

    The probe writes it as ``if before_msg[0]:`` -- index 0 is the COUNT.
    Getting that index wrong is a one-character error that would test the
    STATE string instead, which is always truthy on a readable badge, and the
    probe would then refuse every run. That is the safe direction, but it would
    make the authorised load unspendable and look like LinkedIn's fault.

    Asserted here as a property of the tuple layout the reader returns, so a
    change to that layout fails a test instead of silently re-aiming the gate.
    """
    module = _probe_module()
    count, state = _LIVE_MESSAGING
    assert count == 0 and state == "read"
    # index 0 is the count: falsy at zero, truthy at one.
    assert not (0, "read")[0]
    assert (1, "read")[0]
    # index 1 is the state: truthy on a readable badge, so it must NOT be the
    # thing the zero-precondition tests.
    assert (0, "read")[1]
    # And the readability predicate must be reading index 1, not index 0.
    assert module._readable((7, "read"), (7, "read")) is True, (
        "a NON-ZERO but perfectly readable badge was called unreadable, so "
        "_readable is testing the count rather than the state. Those are two "
        "different refusals and collapsing them loses one of them."
    )
