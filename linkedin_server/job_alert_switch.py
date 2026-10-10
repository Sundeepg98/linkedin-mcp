"""The similar-jobs alert switch on one job posting: read it, aim it, verify it.

Census row ``J 161`` -- *create a job alert for similar jobs from a posting*.
Two writes act through it, each the other's inverse, built in one change
(``HIS-OWN-CURATION-NOT-OUTWARD``: a job alert is his own saved query; nobody
else sees it): ``set_similar_jobs_alert`` (off -> on) and
``unset_similar_jobs_alert`` (on -> off). The selectors, the readings and the
verdicts live here; ``writes`` delegates to them, as it does to
``company_interest`` for "I'm interested".

## WHAT IS MEASURED, AND WHAT IS NOT

MEASURED on live session 8's posting (2026-10-10, load 17; the tracked
skeleton is ``tests/fixtures/live8/posting.html``): ONE block whose ``h2`` reads
exactly :data:`HEADING`; inside it, a line naming the posting's title and place,
then a state container drawing a ``span`` with the visible state word ``Off``
beside a toggle -- an empty ``label`` pointing at the switch, the switch
itself, ``input[role=switch][type=checkbox]`` with
``aria-label="Set alert for similar jobs as <title>"`` (``dom.JOB_ALERT_HEADING_PREFIX``),
and a knob ``span``. The input carries NO ``aria-checked`` and no ``checked``
attribute: its state is its ``checked`` PROPERTY, and the word beside it.

MEASURED IN AUGUST, A DIFFERENT SHAPE (``tests/fixtures/job_detail_hydrated.html``):
``div[role=switch][aria-checked=false]`` carrying the same label. LinkedIn
moved the control between the two captures. This module reads the CURRENT
shape only; the older one reads ``unknown`` here (no input switch in the
block), never a state.

NOT MEASURED (DERIVED, and every verdict that rests on it says so): the ON
state -- the word ``On`` and the property ``checked=true``. ``On`` and ``Off``
are both words the session-2 skeleton vocabulary already keeps for LinkedIn's
switches (``_probe_live_lane_session_2.FURNITURE``), and an input's ``checked``
property is what a checkbox switch IS; but no capture holds this switch on.

NOT MEASURED EITHER: WHETHER A CLICK CAN REACH IT. Live session 8 found the
SAME LinkedIn toggle component in his profile editor (census ``P B9``) with an
input that "draws no box, is not visible", whose trial click timed out, inside
a toggle container (52 x 32) holding the empty label, the input and a knob,
that WAS visible and trial-actionable. So the press is aimed at the TOGGLE
CONTAINER -- the switch input's own parent, found from the input and nothing
else -- and :func:`trial_press` runs Playwright's actionability checks on it
(``click(trial=True)``: nothing is dispatched) at preview and at click time.

## WHAT NEVER LEAVES THIS MODULE

The switch's label carries the posting's TITLE; the line under the heading
carries the title and the place. Neither is read into Python: every selector
matches the label by its PREFIX inside the page, and the readings are counts,
booleans and the closed state word.
"""
from __future__ import annotations

from typing import Any

from linkedin_server import coerce, dom

#: The block's heading, exact. LinkedIn's words, measured on session 8.
HEADING = "Set alert for similar jobs"

#: The block: the heading's own parent, which holds the heading and the
#: switch's container (session 8).
BLOCK = f"xpath=//h2[normalize-space(.)='{HEADING}']/parent::*"

#: Every input switch in the block, and the one wearing the measured prefix.
SWITCHES_IN_BLOCK = (
    f"xpath=//h2[normalize-space(.)='{HEADING}']/parent::*//input[@role='switch']"
)
SWITCH = (
    f"xpath=//h2[normalize-space(.)='{HEADING}']/parent::*"
    f"//input[@role='switch'][starts-with(@aria-label, '{dom.JOB_ALERT_HEADING_PREFIX}')]"
)
#: Switches wearing the prefix ANYWHERE on the page -- a second one outside
#: the block makes the aim ambiguous and is refused.
SWITCH_ANYWHERE = (
    f"xpath=//input[@role='switch'][starts-with(@aria-label, '{dom.JOB_ALERT_HEADING_PREFIX}')]"
)
#: The visible state word: the span drawn beside the toggle container.
STATE_WORD = SWITCH + "/parent::*/preceding-sibling::span"
#: THE PRESS TARGET: the toggle container, the switch input's own parent.
TOGGLE = SWITCH + "/parent::*"

#: The states. ``alert_off`` is measured; ``alert_on`` is DERIVED.
ALERT_OFF: str = "alert_off"
ALERT_ON: str = "alert_on"
UNKNOWN: str = "unknown"

#: The visible word for each state. ``Off`` measured; ``On`` DERIVED.
STATE_WORDS: dict[str, str] = {"Off": ALERT_OFF, "On": ALERT_ON}

#: How long a trial press may wait for actionability. Bounded, one wait.
TRIAL_TIMEOUT_MS = 2500


async def read_switch(page: Any) -> dict[str, Any]:
    """COUNTS, ONE BOOLEAN AND ONE CLOSED WORD, off the posting already open.
    Never raises; ``error`` is an exception TYPE name, never its message."""
    out: dict[str, Any] = {
        "blocks": 0,
        "switches_in_block": 0,
        "prefixed_in_block": 0,
        "prefixed_anywhere": 0,
        "state_word": None,
        "checked": None,
        "error": None,
    }
    try:
        out["blocks"] = coerce.as_count(await page.locator(BLOCK).count())
        out["switches_in_block"] = coerce.as_count(await page.locator(SWITCHES_IN_BLOCK).count())
        out["prefixed_in_block"] = coerce.as_count(await page.locator(SWITCH).count())
        out["prefixed_anywhere"] = coerce.as_count(await page.locator(SWITCH_ANYWHERE).count())
        if out["prefixed_in_block"] == 1:
            words = page.locator(STATE_WORD)
            if coerce.as_count(await words.count()) == 1:
                word = " ".join(str(await words.first.inner_text()).split())
                # A CLOSED WORD OR NOTHING: anything else is recorded as its
                # absence, never as text.
                out["state_word"] = word if word in STATE_WORDS else "other"
            out["checked"] = bool(await page.locator(SWITCH).first.is_checked())
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def switch_verdict(reading: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for the posting's similar-jobs alert switch. PURE.

    ``alert_off``  exactly one block, exactly one switch in it and on the page
                   wearing the prefix, the word beside it ``Off`` and its
                   ``checked`` property false -- MEASURED shape
    ``alert_on``   the same, with ``On`` and ``checked`` true -- DERIVED shape
    ``unknown``    everything else, and the why says which, in counts
    """
    reading = dict(reading or {})
    facts: dict[str, Any] = {
        "blocks": coerce.as_count(reading.get("blocks")),
        "switches_in_block": coerce.as_count(reading.get("switches_in_block")),
        "prefixed_in_block": coerce.as_count(reading.get("prefixed_in_block")),
        "prefixed_on_page": coerce.as_count(reading.get("prefixed_anywhere")),
        "state_word": reading.get("state_word"),
        "checked": reading.get("checked"),
    }
    if reading.get("error"):
        return (facts, UNKNOWN, "the alert switch could not be read "
                f"({str(reading.get('error'))[:64]}); refused rather than guessed.")
    if facts["blocks"] != 1:
        return (facts, UNKNOWN, f"{facts['blocks']} blocks headed {HEADING!r} on the "
                "posting, where exactly one is required.")
    if facts["switches_in_block"] != 1 or facts["prefixed_in_block"] != 1:
        return (facts, UNKNOWN, f"the block draws {facts['switches_in_block']} input "
                f"switch(es), {facts['prefixed_in_block']} wearing LinkedIn's label prefix; "
                "exactly one of each is required. The August shape (a div switch) "
                "reads here, and is not acted on.")
    if facts["prefixed_on_page"] != 1:
        return (facts, UNKNOWN, f"{facts['prefixed_on_page']} switches on the page wear "
                "the alert label's prefix; a second outside the block makes the aim "
                "ambiguous.")
    word = facts["state_word"]
    if word not in STATE_WORDS:
        return (facts, UNKNOWN, "the block draws no single closed state word beside the "
                "switch (Off or On), so its state is not read off the page's own words.")
    state = STATE_WORDS[word]
    if (state == ALERT_ON) is not (facts["checked"] is True):
        return (facts, UNKNOWN, f"the word beside the switch reads {word!r} and the "
                f"switch's checked property reads {facts['checked']!r}: they disagree, "
                "so neither is believed.")
    if state == ALERT_OFF:
        return (facts, ALERT_OFF, "exactly one similar-jobs alert switch, in its block, "
                "reading Off beside an unchecked switch -- the shape MEASURED on live "
                "session 8.")
    return (facts, ALERT_ON, "exactly one similar-jobs alert switch, in its block, "
            "reading On beside a checked switch. The ON shape is DERIVED: no capture "
            "holds this switch on.")


async def read_state(page: Any) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading, off the posting already open."""
    return switch_verdict(await read_switch(page))


async def trial_press(page: Any) -> dict[str, Any]:
    """Whether the TOGGLE CONTAINER can take a click: Playwright's actionability
    checks only (``trial=True``), nothing dispatched. Never raises."""
    out: dict[str, Any] = {"toggles": 0, "actionable": False, "error": None}
    try:
        toggles = page.locator(TOGGLE)
        out["toggles"] = coerce.as_count(await toggles.count())
        if out["toggles"] == 1:
            await toggles.first.click(trial=True, timeout=TRIAL_TIMEOUT_MS)
            out["actionable"] = True
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def verification_verdict(reading: dict[str, Any], wanted: str) -> tuple[str, str]:
    """``(state, why)`` off a FRESH render of the posting, after the press.

    The switch carries both states on one control, so the answer is strong in
    both directions: the state it reads is the state LinkedIn stored. ``wanted``
    is the destination; the verdict is the state read, and the caller compares.
    """
    _facts, state, why = switch_verdict(reading)
    if state == wanted:
        return (state, "on a fresh render of the posting the switch reads "
                f"{state}: the change was stored. " + why)
    return (state, f"on a fresh render of the posting the switch reads {state}, not "
            f"{wanted}. " + why)
