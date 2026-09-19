"""A LATE payload read returns the residue and looks exactly like an empty page.

THE RECEIPT, and it is mine. On 2026-09-19 I read ``payload_chars`` once on a
profile (2,146), compared it against this package's own recorded 1,091,238,
took a 5,063,129 reading on the feed IN THE SAME RUN as the control that said
the instrument was fine, and published *"this address serves a 2 KB shell"* as
a priority finding affecting every profile reader here. It was escalated to a
lead and broadcast to two waves.

It was wrong, and what killed it was the same reader returning **2,146 for the
feed** minutes later -- the number I had just called anomalous.

**THE MECHANISM, MEASURED RATHER THAN GUESSED.** One load, sampled out to 90
seconds, with a second address as a concurrent control::

    feed     t=0  5,112,866   t=5  5,112,866   t=10  2,146   t=90  2,146
    profile  t=0      2,146                                  t=90  2,146

LinkedIn DISCARDS its bootstrap payload about ten seconds after navigation. So
``payload_chars`` does not measure what an address carries -- it measures
**whether you sampled before or after cleanup**, and every reading is a race.
``2,146`` is the residue a hydrated page keeps.

## WHY THIS IS A TEST AND NOT A PARAGRAPH

The paragraph existed. ``read_sdui_actions``'s docstring presented 1,091,238 as
what the profile carries, and a caller reading it would take a small number for
an absent payload -- which is precisely what I did, holding that docstring open.

**A docstring that must be remembered is the thing that failed here.** So the
reader now returns ``residue_suspected`` and this file asserts it, because the
next caller will read a field in their own payload and may never read either
docstring.
"""

from __future__ import annotations

import pytest

from linkedin_server import dom


class _Page:
    """A page that returns one canned reading, like the sibling SDUI tests."""

    def __init__(self, reading: dict) -> None:
        self._reading = reading

    async def evaluate(self, _script, _cfg=None):
        return self._reading


def _reading(**kw) -> dict:
    base = {
        "script_blocks": 3,
        "payload_chars": 5_112_866,
        "needle_hits": 1,
        "global": {k: 0 for k in dom.SDUI_ACTION_TOKENS},
        "scoped": {k: 0 for k in dom.SDUI_ACTION_TOKENS},
    }
    base["global"].update(kw.pop("whole", None) or {})
    base.update(kw)
    return base


def test_the_residue_constant_is_a_named_measurement() -> None:
    """A bare threshold is a magic number; this one carries its measurement."""
    assert dom.MEASURED_POST_CLEANUP_RESIDUE == 2146
    source = dom.__doc__ or ""
    # The measurement lives beside the constant rather than here.
    assert isinstance(dom.MEASURED_POST_CLEANUP_RESIDUE, int)


async def test_a_pre_cleanup_read_is_not_flagged_as_residue() -> None:
    """The ordinary case, so the flag below cannot pass by firing always."""
    page = _Page(_reading(whole={"navigate": 40}))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["residue_suspected"] is False
    assert out["readable"] is True


async def test_a_POST_CLEANUP_read_is_flagged() -> None:
    """2,146 chars is a hydrated page that has tidied up, not an empty one."""
    page = _Page(_reading(payload_chars=dom.MEASURED_POST_CLEANUP_RESIDUE,
                          script_blocks=2))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["residue_suspected"] is True, (
        "a reading at the measured residue must be flagged. Without it a "
        "caller sees a small number and concludes the address is empty -- "
        "the mistake this file is the receipt for."
    )


async def test_a_genuinely_empty_payload_is_also_flagged() -> None:
    """Zero is below the residue, so it flags too -- and that is correct.

    The field does not claim to distinguish "tidied up" from "never had one".
    It claims the reading is TOO SMALL TO CONCLUDE FROM, which is true of both.
    """
    page = _Page(_reading(payload_chars=0, script_blocks=0))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["residue_suspected"] is True
    assert out["readable"] is False


@pytest.mark.parametrize(
    "chars,flagged",
    [(0, True), (2145, True), (2146, True), (2147, False), (5_112_866, False)],
)
async def test_the_boundary_is_where_the_measurement_put_it(
    chars: int, flagged: bool
) -> None:
    """Pinned either side, so a silent change to the threshold fails here."""
    page = _Page(_reading(payload_chars=chars))
    out = await dom.read_sdui_actions(page, "opento_preview_otw")
    assert out["residue_suspected"] is flagged


async def test_this_guard_can_fail(monkeypatch: pytest.MonkeyPatch) -> None:
    """SHOWN FAILING: raise the threshold and a real payload reads as residue.

    The mutation is the plausible wrong edit -- somebody widening the constant
    to catch "small-looking" payloads -- and it asserts the SPECIFIC harm:
    a five-megabyte reading, which is as un-residue as a reading gets, would
    be flagged and a caller would discard a good measurement.
    """
    page = _Page(_reading(payload_chars=5_112_866))
    before = await dom.read_sdui_actions(page, "x")
    assert before["residue_suspected"] is False

    monkeypatch.setattr(dom, "MEASURED_POST_CLEANUP_RESIDUE", 10_000_000)
    after = await dom.read_sdui_actions(page, "x")
    assert after["residue_suspected"] is True, (
        "widening the constant did NOT change the verdict, which would mean "
        "the flag is not computed from it and the pin guards nothing"
    )
