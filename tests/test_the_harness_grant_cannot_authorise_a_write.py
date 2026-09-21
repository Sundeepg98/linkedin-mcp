"""The object ``tests/refusinggrant.py`` supplies may not become permission.

## WHY THIS FILE EXISTS SEPARATELY FROM THE SCRIPT

``scripts/_check_the_refusing_grant_can_fail.py`` shows the four refusals going
red on objects that lack them, which is this repository's condition for a check
counting as one. **A script is not a runner.** Nothing in an ordinary test run
executes it, so a future edit that weakened ``RefusingGrant`` -- a real
timestamp, a token, ``consumed=True`` -- would go green everywhere and the
harness would be handing ``writes.perform`` an object one step from being
permission.

So the property is asserted HERE, where the suite reaches it, and the script
keeps its separate job of proving the assertion can fail.

## THE CONTROL IS IN THIS FILE, NOT ONLY IN THE SCRIPT

``test_the_refusal_check_convicts_an_ordinary_grant`` builds a plain
``writes.WriteGrant`` with a live timestamp and a token -- the shape
``tests/test_writes.py::_bare_grant`` ships -- and requires
``refusal_failures`` to convict it. Without that, every assertion below passes
on a function that returns ``[]`` unconditionally.
"""

from __future__ import annotations

import time

import pytest

from linkedin_server import writes
from tests import refusinggrant
from tests.plantedpage import PlantedPage

SHIPPED = [writes.SANCTIONED_WRITES[k] for k in sorted(writes.SANCTIONED_WRITES)]


@pytest.mark.parametrize("spec", SHIPPED, ids=[s.action for s in SHIPPED])
def test_every_supplied_grant_carries_all_four_refusals(spec):
    """One per sanctioned action, because the harness builds one per action."""
    grant = refusinggrant.grant_for(spec)
    assert refusinggrant.refusal_failures(grant) == []
    assert isinstance(grant, writes.WriteGrant), (
        "perform() does isinstance(grant, WriteGrant); an object that fails "
        "that check would be refused for the wrong reason and would stop "
        "measuring the reader."
    )


def test_the_refusal_check_convicts_an_ordinary_grant():
    """THE CONTROL. Without it the assertions above prove nothing."""
    spec = writes.SANCTIONED_WRITES["linkedin_send_message"]
    ordinary = writes.WriteGrant(
        action=spec.action,
        target=refusinggrant.synthetic_target(spec),
        token="a-token-shaped-string",
        minted_at=time.monotonic(),
    )
    failures = refusinggrant.refusal_failures(ordinary)
    assert failures, (
        "refusal_failures() convicted nothing on a grant holding a live "
        "timestamp and a token, so it cannot fail and its empty list above "
        "certifies nothing."
    )


def test_building_a_grant_registers_nothing():
    """A grant becomes redeemable by entering ``_GRANTS``, and only ``mint``
    puts one there. Building one may not.
    """
    before = dict(writes._GRANTS)
    grants = [refusinggrant.grant_for(spec) for spec in SHIPPED]
    assert writes._GRANTS == before
    assert all(g.token not in writes._GRANTS for g in grants)


async def test_building_an_observation_mints_no_receipt():
    """``writes._record`` is the only writer of ``_OBSERVED``; this is not it.

    An Observation is redeemable only while its receipt is live in that map --
    the class's own docstring says so -- which is what makes a hand-built one
    inert.
    """
    before = dict(writes._OBSERVED)
    page = PlantedPage()
    for spec in SHIPPED:
        observation = await refusinggrant.observation_for(page, spec)
        assert observation.receipt not in writes._OBSERVED
        assert observation.expired(), (
            "an observation the harness builds must be past its TTL, or a "
            "future mint() path would treat it as a live reading."
        )
    assert writes._OBSERVED == before


def test_the_harness_never_turns_writes_on():
    """The process-wide door is the one thing none of this may touch.

    Asserted against the SOURCE as well as the runtime: a module that reads
    False today and sets the flag inside a helper nobody called would pass a
    runtime check and fail this one.
    """
    assert writes.writes_enabled() is False
    from pathlib import Path

    for name in ("refusinggrant.py", "test_readers_emit_no_page_string.py"):
        text = (Path(__file__).parent / name).read_text(encoding="utf-8")
        assert writes.WRITES_FLAG not in text, (
            f"tests/{name} names the writes flag. This harness drives READERS; "
            f"the flag is the boundary it must never move."
        )
        assert "writes_enabled =" not in text, (
            f"tests/{name} rebinds writes_enabled. Only "
            f"scripts/_check_the_refusing_grant_can_fail.py may do that, and "
            f"only to show a refusal is about the grant rather than the door."
        )
