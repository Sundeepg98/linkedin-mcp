"""THE DECIDED REVEALS: plain controls admitted ONE AT A TIME, BY NAME.

The disclosing-press gate (:mod:`linkedin_server.press`) matches a control by
ATTRIBUTE -- ``[aria-expanded]`` or ``[aria-haspopup]`` -- and never by label,
and that is why it cannot reach a plain button. Some plain buttons stand in
front of content the operator wants read. This module presses such a button
only when a call made under the operator's delegation has named it, and
records that call in :data:`DECIDED_REVEALS` beside the one control and the
one surface it covers.

## THIS IS NOT A THIRD SHAPE

``press.SANCTIONED_SHAPES`` is untouched. An entry here names ONE control on
ONE surface by the phrase its label must EQUAL after normalisation
(lower-case; every run of characters outside ``[a-z0-9]`` becomes one space).
The label is compared and never returned -- it yields a boolean, and nothing
the page wrote crosses back. Where the disclosing-press ruling refuses
label-matching as a general mechanism, each entry here is the exception it
would need, written down per control, with who decided it and why.

## WHAT A REVEAL MUST SHOW

Its DECIDED call permits it "as a DISCLOSURE, provided a before/after reading
shows it only reveals content and changes no state". So :func:`reveal`
refuses, BEFORE the click, everything knowable from the address, the key and
the counters -- an undecided key, a surface the entry does not name, an
address the read boundary refuses, a surface with no declared sensitivity
basis, a reading not sanctioned there, a missing counter reader, an
unreadable counter, and anything other than exactly one matching control.
AFTER the click it reports the url unchanged, the counters checked against
the surface's basis by the same :func:`press.check_counters` every press
uses, the page's witness counts, the element count inside ``main``, and the
open-moment reading if one was named. ``permitted`` is True only when the url
did not move and no counter did.

There is NO closure step. The call requires none, and a second press to
collapse what was revealed would be a second press nobody decided.

## THE ONE CLICK

``readonly.SANCTIONED_MUTATIONS`` holds ``("linkedin_server/reveal.py",
"reveal", "click")`` and nothing else for this module, with its argument
beside it. The click is inside :func:`reveal` and nowhere else.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from linkedin_server import press

_refuse = press._refuse

#: What an entry must carry. An entry with no recorded decision, no phrase or
#: no surface is not an admission.
_REVEAL_REQUIRED = ("surfaces", "phrase", "decided", "why")

DECIDED_REVEALS: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "profile_views_show_more_analytics",
        {
            "surfaces": ("/analytics/profile-views/",),
            "phrase": "show more analytics",
            "decided": (
                "DECIDED (orchestrator-delegated, 2026-09-23): 'Show more "
                "analytics' (a plain button) is permitted as a DISCLOSURE, "
                "provided a before/after reading shows it only reveals content "
                "and changes no state."
            ),
            "why": (
                "The control between his profile-views page and the Premium "
                "insights behind it. Measured on the closed page 2026-09-23: a "
                "button[type=button] in main whose only attributes are class, "
                "componentkey and type -- no aria-expanded, no aria-haspopup, no "
                "aria-controls -- so the shape list cannot reach it "
                "(_audit/2026-09-23-live-lane-session-1.md Entry 3). Two plain "
                "buttons of the same shape sit beside it ('all filters', "
                "'reset'); the phrase is what tells them apart, and only this "
                "one is decided."
            ),
        },
    ),
)

#: How long a reveal waits for its content before the after-readings. Bounded
#: and single: whatever has not rendered by then is not claimed.
REVEAL_SETTLE_MS = 1500

#: The control's candidates: buttons inside the page's own content landmark.
CANDIDATE_SCOPE = "main"

_NOT_ALNUM = re.compile(r"[^a-z0-9]+")


def normalised_label(text: Any) -> str:
    """Lower-case; every run outside ``[a-z0-9]`` becomes one space. PURE."""
    return _NOT_ALNUM.sub(" ", str(text or "").lower()).strip()


def decided_reveal(key: Optional[str]) -> Optional[dict[str, Any]]:
    """The table entry for a reveal key, or None. PURE."""
    for name, entry in DECIDED_REVEALS:
        if name == key:
            return entry
    return None


def check_reveal(url: Optional[str], key: Optional[str]) -> dict[str, Any]:
    """The pre-press half of a reveal. PURE, and every refusal is decided here."""
    entry = decided_reveal(key)
    if entry is None:
        return _refuse(
            "reveal_not_decided",
            "the key is not in reveal.DECIDED_REVEALS. A reveal is admitted one "
            "control at a time by a recorded call; a caller names one and "
            "cannot supply one.",
            terminal=True,
        )
    missing = [field for field in _REVEAL_REQUIRED if not entry.get(field)]
    if missing:
        return _refuse(
            "reveal_entry_incomplete",
            f"the table entry is missing {missing}; an entry with no recorded "
            "decision or no phrase is not an admission.",
            terminal=True,
        )
    address = press.check_address(url)
    if address.get("refused"):
        return address
    path = urlsplit(str(url).strip()).path
    if path not in entry["surfaces"]:
        return _refuse(
            "reveal_not_for_this_surface",
            "the page is not one this reveal was decided for. A decision about "
            "one control on one page says nothing about another page.",
            terminal=True,
        )
    basis = press.check_basis(url)
    if basis.get("refused"):
        return basis
    return {"pressed": False, "reveal_ok": True, "basis": basis.get("basis")}


async def reveal(
    page: Any,
    *,
    key: str,
    read_counters: Optional[Callable] = None,
    reading: Optional[str] = None,
) -> dict[str, Any]:
    """Press ONE DECIDED plain control, and show it only revealed content.

    ``key`` names an entry of :data:`DECIDED_REVEALS`; ``reading`` (optional)
    names a ``press.OPEN_READINGS`` entry taken before the click and after it.
    ``read_counters`` is an async callable returning a mapping of counter name
    to int-or-None, as ``press.disclose`` takes it.

    THE CONTROL is the ONE visible button in ``main`` that carries none of
    ``aria-expanded``, ``aria-haspopup`` or ``aria-controls`` and whose label
    EQUALS the entry's phrase after normalisation.
    """
    address = getattr(page, "url", None)
    pre = check_reveal(address, key)
    if pre.get("refused"):
        return pre
    if reading is not None:
        reading_pre = press.check_reading(address, reading)
        if reading_pre.get("refused"):
            return reading_pre
    if read_counters is None:
        return _refuse(
            "no_counter_reader_supplied",
            "a reveal must be SHOWN to change no state, and the counters are "
            "half of how. Without a reader there is no way to show it.",
            terminal=False,
        )
    phrase = str((decided_reveal(key) or {}).get("phrase"))
    buttons = page.locator(CANDIDATE_SCOPE).locator("button")
    reading_before: Optional[dict[str, Any]] = None
    reading_open: Optional[dict[str, Any]] = None
    try:
        # THE COUNTERS FIRST, and an unreadable one ends it here, before the
        # click -- not after it, which is the order press.disclose still has.
        before = await read_counters()
        if not before or any(value is None for value in before.values()):
            return _refuse(
                "counters_unreadable_before_any_press",
                "a counter did not read before the press, so the press could "
                "not be priced; refused with nothing touched.",
                terminal=False,
            )
        chosen: list[int] = []
        for position in range(int(await buttons.count())):
            candidate = buttons.nth(position)
            carries_state = False
            for attribute in ("aria-expanded", "aria-haspopup", "aria-controls"):
                if await candidate.get_attribute(attribute) is not None:
                    carries_state = True
            if carries_state or not await candidate.is_visible():
                continue
            if normalised_label(await candidate.inner_text()) == phrase:
                chosen.append(position)
        if len(chosen) != 1:
            return _refuse(
                "reveal_control_not_unique",
                f"{len(chosen)} visible plain buttons in main carry this "
                "entry's label; exactly one is required, so nothing was "
                "pressed.",
                terminal=False,
            )
        witness_before = await press._read_witness(page)
        elements_before = int(await page.locator(CANDIDATE_SCOPE + " *").count())
        if reading is not None:
            reading_before = await press._take_reading(page, reading)
        await buttons.nth(chosen[0]).click(timeout=press.CLICK_TIMEOUT_MS)
        await page.wait_for_timeout(REVEAL_SETTLE_MS)
        after = await read_counters()
        witness_after = await press._read_witness(page)
        elements_after = int(await page.locator(CANDIDATE_SCOPE + " *").count())
        if reading is not None:
            reading_open = await press._take_reading(page, reading)
        address_after = getattr(page, "url", None)
    except Exception as exc:  # noqa: BLE001
        return _refuse(
            "press_failed",
            f"the reveal raised {type(exc).__name__}. Nothing is claimed about "
            "what the page did.",
            terminal=False,
        )

    counters = press.check_counters(before, after, basis=press.sensitivity_basis(address))
    url_unchanged = address_after == address
    measured: dict[str, Any] = {
        "pressed": True,
        "key": key,
        "url_unchanged": url_unchanged,
        "counters": counters,
        "witness": press.witness_verdict(witness_before, witness_after, control_open=None),
        "main_elements": {"before": elements_before, "after": elements_after},
        "permitted": bool(url_unchanged and not counters.get("refused")),
    }
    if reading is not None:
        measured["reading"] = press.reading_verdict(reading, reading_before, reading_open)
    if measured["permitted"]:
        return measured
    if not url_unchanged:
        refusal = _refuse(
            "reveal_moved_the_url",
            "the page's address changed across the press. A reveal that "
            "navigates is not a disclosure, whatever it showed.",
            terminal=False,
        )
    else:
        refusal = _refuse(
            "reveal_moved_a_counter",
            "a counter the surface is priced by did not read the same after "
            "the press; see counters.",
            terminal=False,
        )
    # THE PRESS HAPPENED, and the refusal says so: its measurements ride with
    # it, and ``pressed`` stays True.
    return {**refusal, **measured}
