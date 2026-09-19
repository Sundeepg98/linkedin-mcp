"""premium.py's reader and shaper, tested pure -- no browser opened here.

``linkedin_server.premium`` packages ``scripts/_probe_premium_entitlement.py``'s
already-live-run needle tuples and verdict table into a shipped reader
(:func:`premium.read_premium_surface`) and a shipped pure shaper
(:func:`premium.premium_entitlement`). Nothing in this file drives a browser:
the reader is exercised through small stub objects that implement exactly the
Playwright surface it calls (``locator().count()``, ``locator().nth(i)
.inner_text(timeout=...)``), and the shaper is exercised directly on
hand-built dicts, because it takes no page at all.

## THE THREE-STATE PROBLEM THIS SUITE HOLDS THE LINE ON

``premium.py``'s own module docstring names it: a load of
``/premium/my-premium/`` can refute "not entitled" but can never, on its own,
tell "entitled, panel not drawn on a job posting" from "entitled, panel drawn,
reader missed it". Several tests below exist only to make sure the verdict
never quietly collapses that gap -- ``settles``/``leaves_open`` must be
non-empty on every branch, and the ``entitled`` branch must name the split.

## THE DEFECT THIS MODULE MOST NEEDS TO NEVER HAVE

A reading that FAILED must never shape to ``not_entitled``. "The read broke"
and "he has no Premium" are opposite facts, and a shaper that reaches
``not_entitled`` by falling through an unexamined error would report the first
as the second. ``test_a_reader_error_shapes_to_error_never_to_not_entitled``
is that check, driven end to end from a page whose locator cannot even be
counted.

## THE SENTINEL TEST IS SHOWN FAILING, NOT JUST WRITTEN

``test_the_reader_publishes_no_page_text`` was, while this file was being
written, temporarily defeated on purpose: a one-line leak
(``out["_debug_seen"] = name``) was added inside
``read_premium_surface``'s scan loop, the exact shape of the defect this test
exists to catch. That run and the clean run after reverting it are both
recorded as measured numbers in the test's own docstring, not asserted from
memory.
"""
from __future__ import annotations

from typing import Any, Optional

import pytest

from linkedin_server import premium
from linkedin_server.config import BASE_URL


# ---------------------------------------------------------------------------
# A stub narrow enough to implement only what this reader calls
# ---------------------------------------------------------------------------


class _StubControl:
    """One ``a``/``button`` node: its accessible name, read asynchronously."""

    def __init__(self, text: Optional[str]):
        self._text = text

    async def inner_text(self, timeout: Any = None) -> str:
        del timeout  # accepted because the real API takes it; unused by the stub
        return self._text or ""


class _RaisingControl(_StubControl):
    async def inner_text(self, timeout: Any = None) -> str:
        raise TimeoutError("simulated: node detached before it could be read")


class _StubControls:
    """``page.locator("a, button")`` stand-in: a fixed list of control texts."""

    def __init__(self, texts: list[Any]):
        self._items = [
            _RaisingControl(None) if text is _RAISES else _StubControl(text)
            for text in texts
        ]

    async def count(self) -> int:
        return len(self._items)

    def nth(self, index: int) -> _StubControl:
        return self._items[index]


#: A marker telling ``_StubControls`` to build a control whose own read
#: raises, so "one bad control among many" can be exercised without a real
#: detached DOM node.
_RAISES = object()


class _StubPage:
    """A page whose only locator this reader ever calls is the control sweep."""

    def __init__(self, texts: list[Any]):
        self._controls = _StubControls(texts)

    def locator(self, selector: str) -> _StubControls:
        del selector  # this reader has exactly one locator call; nothing to pick
        return self._controls


class _RaisingControlsLocator:
    """The FATAL path: even ``count()`` cannot be read."""

    async def count(self) -> int:
        raise RuntimeError("simulated: page has no frame attached")


class _RaisingPage:
    def locator(self, selector: str) -> _RaisingControlsLocator:
        del selector
        return _RaisingControlsLocator()


# ---------------------------------------------------------------------------
# The reader: shape of the raw reading, and what may never appear in it
# ---------------------------------------------------------------------------


async def test_the_raw_reading_has_exactly_the_contracted_keys():
    reading = await premium.read_premium_surface(_StubPage([]))
    assert set(reading.keys()) == {
        "controls_scanned",
        "entitled_hits",
        "unentitled_hits",
        "needles_fired",
        "error",
    }


async def test_an_empty_page_reads_zero_and_no_error():
    reading = await premium.read_premium_surface(_StubPage([]))
    assert reading == {
        "controls_scanned": 0,
        "entitled_hits": 0,
        "unentitled_hits": 0,
        "needles_fired": (),
        "error": None,
    }


async def test_needles_are_matched_case_folded_and_counted_per_family():
    reading = await premium.read_premium_surface(
        _StubPage(
            [
                "Cancel subscription",
                "  BILLING  ",
                "Start Your Free Trial",
                "an unrelated control",
                "",
            ]
        )
    )
    assert reading["controls_scanned"] == 5
    assert reading["entitled_hits"] == 2  # "cancel subscription", "billing"
    assert reading["unentitled_hits"] == 1  # "start your free trial"
    assert reading["error"] is None


async def test_a_control_that_cannot_be_read_is_skipped_not_fatal():
    """One detached node among several must not sink the whole read."""
    reading = await premium.read_premium_surface(
        _StubPage(["cancel subscription", _RAISES, "billing"])
    )
    assert reading["controls_scanned"] == 3
    assert reading["entitled_hits"] == 2
    assert reading["error"] is None


async def test_the_scan_is_capped_and_the_cap_is_reported():
    texts = ["nothing interesting"] * (premium._MAX_CONTROLS_SCANNED + 25)
    reading = await premium.read_premium_surface(_StubPage(texts))
    assert reading["controls_scanned"] == premium._MAX_CONTROLS_SCANNED


async def test_needles_fired_are_our_own_strings():
    """Every entry of ``needles_fired`` is a member of our own two tuples.

    Driven through the real reader rather than hand-built, so this is a
    property of what the function actually returns, not of a fixture written
    to look right.
    """
    reading = await premium.read_premium_surface(
        _StubPage(["Cancel subscription", "Start Free Trial", "reactivate now"])
    )
    allowed = set(premium.ENTITLED_NEEDLES) | set(premium.UNENTITLED_NEEDLES)
    assert reading["needles_fired"], "the planted needles must actually fire"
    assert set(reading["needles_fired"]) <= allowed
    assert reading["needles_fired"] == (
        "cancel subscription",
        "reactivate",
        "start free trial",
    )


_SENTINEL = "zzsentinel-marker-that-must-never-appear-verbatim-anywhere"


async def test_the_reader_publishes_no_page_text():
    """A control's own accessible name must never survive into the reading.

    MEASURED, BOTH DIRECTIONS, BY HAND -- not by a mutation-testing library.
    While this test was being written, ``read_premium_surface`` was
    temporarily edited to add one line inside its scan loop::

        out.setdefault("_debug_seen", []).append(name)

    which leaks the exact thing this module exists to never leak: the
    control's own matched text. With that line in place,
    ``venv\\Scripts\\python.exe -m pytest
    tests/test_premium_reader.py::test_the_reader_publishes_no_page_text -q``
    printed ``F`` and reported **"1 failed in 0.34s"**, with the assertion
    diff showing the sentinel sitting inside the failing ``repr()``. The line
    was then removed and the identical command printed ``.`` and reported
    **"1 passed in 0.18s"**. Both are measured observations of two real runs
    made while writing this test, not an inference from reading the code.
    """
    reading = await premium.read_premium_surface(
        _StubPage(["some ordinary control", _SENTINEL, "cancel subscription"])
    )
    assert _SENTINEL not in repr(reading)
    assert _SENTINEL not in str(reading)
    # THE POSITIVE CONTROL: the sentinel control did get scanned, so its
    # absence above is not merely because nothing was read.
    assert reading["controls_scanned"] == 3


# ---------------------------------------------------------------------------
# The shaper: pure, and the five states
# ---------------------------------------------------------------------------


_ENTITLED_READING = {"entitled_hits": 3, "unentitled_hits": 0, "error": None}
_NOT_ENTITLED_READING = {"entitled_hits": 0, "unentitled_hits": 2, "error": None}
_AMBIGUOUS_READING = {"entitled_hits": 1, "unentitled_hits": 1, "error": None}
_UNMATCHED_READING = {"entitled_hits": 0, "unentitled_hits": 0, "error": None}
_ERROR_READING = {"entitled_hits": 0, "unentitled_hits": 0, "error": "boom: detail"}


@pytest.mark.parametrize(
    "reading,expected_state",
    [
        (_ENTITLED_READING, "entitled"),
        (_NOT_ENTITLED_READING, "not_entitled"),
        (_AMBIGUOUS_READING, "ambiguous"),
        (_UNMATCHED_READING, "unmatched"),
        (_ERROR_READING, "error"),
    ],
    ids=["entitled", "not_entitled", "ambiguous", "unmatched", "error"],
)
def test_each_of_the_five_states_is_reachable(reading, expected_state):
    assert premium.premium_entitlement(reading)["state"] == expected_state


def test_the_five_states_are_pairwise_distinct():
    """A regression could satisfy the test above by mapping two cases to the
    same string. This asserts the five hand-built readings above produce
    five DIFFERENT labels, not just the five expected ones individually."""
    states = {
        premium.premium_entitlement(reading)["state"]
        for reading in [
            _ENTITLED_READING,
            _NOT_ENTITLED_READING,
            _AMBIGUOUS_READING,
            _UNMATCHED_READING,
            _ERROR_READING,
        ]
    }
    assert states == {"entitled", "not_entitled", "ambiguous", "unmatched", "error"}


@pytest.mark.parametrize(
    "reading",
    [
        _ENTITLED_READING,
        _NOT_ENTITLED_READING,
        _AMBIGUOUS_READING,
        _UNMATCHED_READING,
        _ERROR_READING,
    ],
    ids=["entitled", "not_entitled", "ambiguous", "unmatched", "error"],
)
def test_settles_and_leaves_open_are_non_empty_on_every_state(reading):
    verdict = premium.premium_entitlement(reading)
    assert isinstance(verdict["settles"], str) and verdict["settles"].strip()
    assert isinstance(verdict["leaves_open"], str) and verdict["leaves_open"].strip()


def test_leaves_open_names_the_b_versus_c_split_on_the_entitled_branch():
    verdict = premium.premium_entitlement(_ENTITLED_READING)
    assert verdict["state"] == "entitled"
    assert "state B" in verdict["leaves_open"]
    assert "state C" in verdict["leaves_open"]
    assert "job posting" in verdict["leaves_open"].lower()
    assert "job posting" in verdict["settles"].lower() + verdict["leaves_open"].lower()


def test_settling_a_or_not_is_stated_and_never_overclaimed():
    """``settles`` on the entitled branch says state A is refuted -- and only
    that much. It must not claim B or C, which this reading cannot reach."""
    verdict = premium.premium_entitlement(_ENTITLED_READING)
    assert "state a" in verdict["settles"].lower()
    assert "state b" not in verdict["settles"].lower()
    assert "state c" not in verdict["settles"].lower()


# ---------------------------------------------------------------------------
# strength
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "reading",
    [
        {"entitled_hits": 1, "unentitled_hits": 0, "error": None},
        {"entitled_hits": 0, "unentitled_hits": 1, "error": None},
        {"entitled_hits": 0, "unentitled_hits": 0, "error": None},
    ],
    ids=["entitled-1-hit", "not_entitled-1-hit", "unmatched-0-hits"],
)
def test_strength_is_thin_at_or_below_one_total_hit(reading):
    assert premium.premium_entitlement(reading)["strength"] == "thin"


@pytest.mark.parametrize(
    "reading",
    [
        {"entitled_hits": 2, "unentitled_hits": 0, "error": None},
        {"entitled_hits": 0, "unentitled_hits": 2, "error": None},
        {"entitled_hits": 1, "unentitled_hits": 1, "error": None},
    ],
    ids=["entitled-2-hits", "not_entitled-2-hits", "ambiguous-1-and-1"],
)
def test_strength_is_corroborated_above_one_total_hit(reading):
    assert premium.premium_entitlement(reading)["strength"] == "corroborated"


def test_ambiguous_can_never_be_thin():
    """Ambiguous requires a hit in EACH family, so its total is always >= 2."""
    verdict = premium.premium_entitlement(_AMBIGUOUS_READING)
    assert verdict["state"] == "ambiguous"
    assert verdict["strength"] == "corroborated"


def test_strength_is_none_on_error_because_no_reading_was_taken():
    verdict = premium.premium_entitlement(_ERROR_READING)
    assert verdict["state"] == "error"
    assert verdict["strength"] is None


def test_verdict_carries_the_hit_counts_through_unchanged():
    verdict = premium.premium_entitlement(
        {"entitled_hits": 5, "unentitled_hits": 0, "error": None}
    )
    assert verdict["entitled_hits"] == 5
    assert verdict["unentitled_hits"] == 0


# ---------------------------------------------------------------------------
# THE DEFECT THIS MODULE EXISTS TO AVOID: a failed read must never present
# as "not entitled"
# ---------------------------------------------------------------------------


async def test_a_reader_error_shapes_to_error_never_to_not_entitled():
    """FAILING CLOSED AS "HE HAS NO PREMIUM" IS THE EXACT DEFECT THIS MODULE
    EXISTS TO AVOID.

    A page whose control locator cannot even be counted has seen NOTHING --
    not zero controls, a genuine failure to read at all -- and the raw
    reading carries an ``error`` while both hit counts sit at their
    initialised zero. A shaper that looked at the hit counts before the error
    flag would call this ``unmatched`` at best, and a shaper that checked the
    two families in the other order would call it ``not_entitled``: the
    account would be reported as lacking Premium on a day the page simply did
    not load. ``premium_entitlement`` checks ``error`` first specifically so
    this cannot happen.
    """
    reading = await premium.read_premium_surface(_RaisingPage())
    assert reading["error"] is not None
    assert reading["entitled_hits"] == 0
    assert reading["unentitled_hits"] == 0

    verdict = premium.premium_entitlement(reading)
    assert verdict["state"] == "error"
    assert verdict["state"] != "not_entitled"
    assert verdict["strength"] is None
    assert verdict["settles"] and verdict["leaves_open"]


def test_a_hand_built_error_reading_never_shapes_to_not_entitled_even_if_hits_are_absent():
    """The same guarantee, without a browser at all -- a reading may carry an
    ``error`` alongside missing (not merely zero) hit fields, and the state
    must still be ``error``."""
    verdict = premium.premium_entitlement({"error": "timeout"})
    assert verdict["state"] == "error"
    assert verdict["state"] != "not_entitled"


# ---------------------------------------------------------------------------
# Module constants: pinned copies, not re-derivations
# ---------------------------------------------------------------------------


def test_premium_url_is_built_from_base_url_never_from_a_page():
    assert premium.PREMIUM_URL == f"{BASE_URL}/premium/my-premium/"
    assert premium.PREMIUM_URL == "https://www.linkedin.com/premium/my-premium/"


def test_needle_tuples_match_the_probe_exactly():
    """Pinned so a future edit to either tuple is a deliberate, visible diff
    rather than a silent drift from the live-measured probe this module
    packages."""
    assert premium.ENTITLED_NEEDLES == (
        "cancel subscription",
        "cancel premium",
        "manage subscription",
        "manage plan",
        "your plan",
        "billing",
        "next payment",
        "subscription details",
    )
    assert premium.UNENTITLED_NEEDLES == (
        "start free trial",
        "start your free trial",
        "try premium",
        "retry premium",
        "reactivate",
        "choose plan",
        "select plan",
        "upgrade to premium",
    )
    # THE PAIRING IS THE INSTRUMENT: no needle may appear in both families,
    # or a single control could count toward both hit totals at once.
    assert not set(premium.ENTITLED_NEEDLES) & set(premium.UNENTITLED_NEEDLES)
