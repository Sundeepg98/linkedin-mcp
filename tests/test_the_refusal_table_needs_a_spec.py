"""A refusal keyed by an action nobody registered is unreachable, and this says so.

WHY THIS FILE EXISTS, AND IT IS A ROUTING SCAR RATHER THAN A HYPOTHESIS.

``writes._NINE_REFUSALS`` maps an action to a refusal sentence naming its own
blocker, and its header defines exactly two blocker shapes: NO CONTROL (the
thing that would be clicked has never been observed) and NO SURFACE (the
address is refused by the forbidden list). Those two shapes are exactly what a
census row whose surface nobody has opened occupies -- so the table READS like
the boundary-free place to file such a row, at no cost, while a full
``WriteSpec`` cannot even be written for a surface nobody has photographed.

TWO WAVES REACHED THAT CONCLUSION AND IT IS WRONG, for a reason that is
nowhere in the table's own documentation:

    the only consumer is ``_refuse_unperformable(spec: WriteSpec)``, and its
    argument is a SPEC. An action with no entry in ``SANCTIONED_WRITES`` has no
    spec, ``spec_for_action`` raises for it, and no call site can construct
    one. A key for such an action is dead on arrival.

So the table is the home for a SANCTIONED action that cannot perform -- not for
an UNREGISTERED one. The registration is the cost, and the table does not avoid
it. This file turns that from a paragraph two waves had to rediscover into an
assertion that fires.

THE VACUITY PROBLEM IS THE WHOLE DIFFICULTY HERE, and it is named because this
package has already lost checks to it: ``_NINE_REFUSALS`` is EMPTY at this
tree, so "every key is registered" passes over zero keys and certifies nothing.
Three checks in ``tests/test_writes_nine.py`` stopped running on 2026-09-01
in exactly this way, in silence. Every assertion below is therefore PAIRED with
a planted key that makes it fire -- one registered, one not -- so the check is
shown discriminating rather than shown passing.

NOTHING HERE MUTATES THE SHIPPED TABLE. The plants are built as local dicts and
the shipped one is read, never written.
"""

from __future__ import annotations

import pytest

from linkedin_server import writes


#: An action string that is deliberately not registered anywhere. It is the
#: shape a wave would reach for when filing a census row whose surface nobody
#: has opened -- "create a job alert" was the live example.
UNREGISTERED_ACTION = "create_job_alert"

#: An action that IS registered and cannot perform. The one member of that set.
REGISTERED_AND_REFUSING = "set_open_to_work"


def _sanctioned_actions() -> set[str]:
    return {spec.action for spec in writes.SANCTIONED_WRITES.values()}


def _keys_missing_a_spec(table: dict[str, str]) -> list[str]:
    """The property under test, computed over ANY table so it can be planted."""
    return sorted(set(table) - _sanctioned_actions())


# ---------------------------------------------------------------------------
# 1. The property, and the plants that make it non-vacuous
# ---------------------------------------------------------------------------


def test_the_shipped_table_has_no_key_without_a_spec():
    """The real assertion. It is vacuous today and the next test is why that is
    not an excuse to skip it."""
    assert _keys_missing_a_spec(writes._NINE_REFUSALS) == []


def test_the_check_fires_on_a_planted_unregistered_key():
    """SHOWN FAILING. Without this, the test above passes over zero keys."""
    planted = {UNREGISTERED_ACTION: "a refusal nobody could ever read"}
    assert _keys_missing_a_spec(planted) == [UNREGISTERED_ACTION]


def test_the_check_passes_a_planted_key_that_does_have_a_spec():
    """The other half: a check that flags everything is not a check either."""
    planted = {REGISTERED_AND_REFUSING: "a refusal a caller can actually reach"}
    assert _keys_missing_a_spec(planted) == []


def test_the_two_plants_are_genuinely_different_cases():
    """Guards the fixtures themselves, because a plant that is secretly
    registered would make the pair agree for the wrong reason."""
    actions = _sanctioned_actions()
    assert REGISTERED_AND_REFUSING in actions
    assert UNREGISTERED_ACTION not in actions


# ---------------------------------------------------------------------------
# 2. WHY an unregistered key is unreachable, asserted rather than reasoned
# ---------------------------------------------------------------------------


def test_spec_for_action_refuses_an_unregistered_action():
    """The mechanical reason. ``_refuse_unperformable`` takes a spec, and this
    is the only way a caller gets one -- so an unregistered action cannot even
    reach the function that would read the table."""
    with pytest.raises(Exception):
        writes.spec_for_action(UNREGISTERED_ACTION)


def test_the_registered_refusing_action_does_reach_a_refusal():
    """The positive control beside it. Without this, the test above would pass
    on a ``spec_for_action`` that raised for EVERYTHING."""
    spec = writes.spec_for_action(REGISTERED_AND_REFUSING)
    assert spec.action == REGISTERED_AND_REFUSING
    with pytest.raises(writes.WriteAttemptError):
        writes._refuse_unperformable(spec)


def test_a_spec_may_exist_before_its_surface_has_been_opened():
    """The half that is NOT a blocker, and it is the half that decides the
    roadmap for a row whose surface nobody has loaded.

    ``WriteSpec.url_template`` is Optional precisely so that an action may be
    REGISTERED before its surface is photographed -- and the one registered,
    non-performable action is in exactly that state. So "no page has been
    opened" does not prevent registration; it prevents PERFORMING. The cost of
    filing a blocked action in the refusal table is the registration and the
    decision at the empty-table assertion, and there is no cheaper door.
    """
    spec = writes.spec_for_action(REGISTERED_AND_REFUSING)
    assert spec.url_template is None
    assert writes.grant_is_possible(spec) is False


def test_every_other_sanctioned_spec_carries_a_surface():
    """The split, re-derived here rather than quoted from an audit.

    Twelve specs carry a url and can hold a grant; one does not and cannot.
    A count that never moves under a change that should move it is a number
    about the instrument, so this asserts the RELATION -- that the two
    partitions are the same partition -- rather than pinning 12 and 1.
    """
    with_surface = {
        spec.action
        for spec in writes.SANCTIONED_WRITES.values()
        if spec.url_template is not None
    }
    can_hold_a_grant = {
        spec.action
        for spec in writes.SANCTIONED_WRITES.values()
        if writes.grant_is_possible(spec)
    }
    assert with_surface == can_hold_a_grant
    assert REGISTERED_AND_REFUSING not in with_surface
