"""Endorse one skill of a member he names, and withdraw it -- built to REFUSE.

Census rows ``P E4`` / ``N 111`` (endorse) and ``P E5`` / ``N 113`` (remove an
endorsement he gave). Two writes in ``writes``, ``endorse_skill`` and its
inverse ``withdraw_endorsement``, both SANCTIONED AND NOT PERFORMABLE (lane
builds-26, 2026-11-24). This module holds what their previews read and the
verdict they print. It presses nothing.

## WHAT IS MEASURED, AND WHAT IS NOT

MEASURED as an ABSENCE: ZERO endorse controls in every tracked capture.
``outward_classes.OUTWARD_CLASS_SPECS['endorse_skill']`` carries the 2026-08-30
census (13 fixtures, his own skills surface, 222 controls on his own profile,
all zero) and lane builds-26 re-took it over ``tests/fixtures/`` on
2026-10-26: no file draws the word. The one third-party profile captured --
the live skeleton the named-person acts were measured on -- draws no skill
card at all. You cannot endorse yourself, so the control lives only on the
named member's own profile, and that profile's Skills section has never been
captured.

NOT MEASURED: the per-skill control's label in either state, where it sits
relative to the skill's name, and what pressing it does. Nothing in this
module names a label it has not seen, and no selector here aims a press.

## WHAT A PREVIEW THEREFORE DOES

It loads the profile HE NAMED, through the named-profile door
(``THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET``: inside the act he names, never as
a measurement on a stranger), confirms the page is that one person's profile
(``named_profile.identity_confirmed``), and COUNTS, in the page, the buttons
whose accessible name carries "endorse" and those that also carry the skill
he gave (:func:`read_skill_controls`). Integers only: no label, no name and no
skill text leaves the page. Then it REFUSES -- the act is not performable --
and prints the counts. The first supervised preview on a member he names is
therefore the first reading this server has ever taken of the control, inside
the act it would be part of, and it costs that member one profile view, as
the named-person acts' previews do.

## THE ROUND TRIP, FOR WHEN A CAPTURE ARMS THEM

Both directions are built together so the inverse exists before any forward
press can: an endorsement is pressed on a member only after the withdraw's
own anchor -- the label an endorsed skill wears -- is measured on that member,
so the act can be taken back the same session (the round-trip rule). Today
neither label is measured, so neither press exists.
"""
from __future__ import annotations

import re
from typing import Any

from linkedin_server import coerce, named_profile

#: The state both previews are valid FROM: the page is the one person's
#: profile its own title names. Not a control state -- no control is read.
PROFILE_IDENTIFIED: str = "profile_identified"
UNKNOWN: str = "unknown"

#: The two actions, by direction.
ENDORSE: str = "endorse_skill"
WITHDRAW: str = "withdraw_endorsement"
ACTIONS: tuple[str, ...] = (ENDORSE, WITHDRAW)

#: The longest skill name this server will compare. Its own cap, not
#: LinkedIn's: nobody here has measured LinkedIn's.
MAX_SKILL_CHARS: int = 100

#: The word every endorse-shaped control is expected to carry. A COUNT is
#: taken of controls whose accessible name contains it, case folded; it aims
#: nothing, so a wrong guess costs a zero, never a press.
_ENDORSE_WORD = re.compile("endors", re.IGNORECASE)


def checked_skill(candidate: Any) -> tuple[str, str]:
    """``(skill, "")`` for a usable skill name, else ``("", why)``. PURE. The
    why reports a SHAPE, never the value."""
    text = " ".join(str(candidate if candidate is not None else "").split())
    if not text:
        return "", "no skill was given; the act endorses one skill, named by you."
    if len(text) > MAX_SKILL_CHARS:
        return "", (
            f"the skill is {len(text)} characters long; this server compares at "
            f"most {MAX_SKILL_CHARS}. It is not repeated here."
        )
    if "/" in text or text.casefold().startswith("http"):
        return "", (
            "the skill looks like an address, not a skill name. It is not "
            "repeated here."
        )
    return text, ""


async def read_skill_controls(page: Any, skill: str) -> dict[str, Any]:
    """COUNTS ONLY, off the named profile already open. Never raises.

    ``endorse_controls``           buttons whose accessible name carries
                                   "endors", anywhere on the page
    ``endorse_controls_for_skill`` of those, the ones whose name also
                                   carries the skill he gave (substring,
                                   case folded, compared by Playwright's role
                                   engine -- the skill never enters a selector
                                   string)
    ``skill_controls``             buttons whose name carries the skill at all

    ``error`` is an exception TYPE name, never its message.
    """
    out: dict[str, Any] = {
        "endorse_controls": 0,
        "endorse_controls_for_skill": 0,
        "skill_controls": 0,
        "error": None,
    }
    try:
        endorse = page.get_by_role("button", name=_ENDORSE_WORD, include_hidden=True)
        out["endorse_controls"] = coerce.as_count(await endorse.count())
        if skill:
            named = page.get_by_role("button", name=skill, include_hidden=True)
            out["skill_controls"] = coerce.as_count(await named.count())
            out["endorse_controls_for_skill"] = coerce.as_count(
                await endorse.and_(named).count()
            )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def control_facts(counts: dict[str, Any]) -> dict[str, Any]:
    """The counts as a confirm block prints them. Integers and a type name."""
    counts = counts if isinstance(counts, dict) else {}
    return {
        "endorse_controls": coerce.as_count(counts.get("endorse_controls")),
        "endorse_controls_for_skill": coerce.as_count(counts.get("endorse_controls_for_skill")),
        "skill_controls": coerce.as_count(counts.get("skill_controls")),
        "skill_controls_error": counts.get("error"),
        "control_label_measured": False,
    }


def preview_state(reading: dict[str, Any], counts: dict[str, Any], *, action: str) -> tuple[str, str]:
    """``(state, why)`` for either direction's preview. PURE.

    ``profile_identified`` when the page is the one person's profile its own
    title names; ``unknown`` otherwise, with the identity check's own why.
    The counts are reported in the why; they never change the state, because
    no count can stand in for a label nobody has measured.
    """
    if action not in ACTIONS:
        return UNKNOWN, "this module answers for endorse_skill and withdraw_endorsement only."
    if not named_profile.identity_confirmed(reading):
        return UNKNOWN, (
            "the page did not show one person's profile in the shape the "
            "named-person acts measured -- a profile title, exactly one topcard, "
            "its first heading the title's name, compared in the page -- so it "
            "is not identified, nothing on it is counted for this act, and "
            "nothing is aimed at a page this server cannot identify."
        )
    facts = control_facts(counts)
    direction = "endorse" if action == ENDORSE else "withdraw an endorsement of"
    return PROFILE_IDENTIFIED, (
        "the page is the profile of the person its own title names. On it, "
        f"{facts['endorse_controls']} button(s) carry 'endors' in their "
        f"accessible name and {facts['endorse_controls_for_skill']} of those "
        f"also carry the skill you gave ({facts['skill_controls']} button(s) "
        "carry the skill at all) -- counted in the page, no label read. NO "
        f"LABEL IS MEASURED for the control that would {direction} a skill, "
        "so nothing is pressed and no token is issued: these counts are the "
        "first reading this server has taken of that control."
    )
