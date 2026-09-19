"""THE DISCLOSING PRESS, bounded mechanically rather than by judgement.

Implements `_audit/2026-09-19-the-disclosing-press-ruling.md`. Read that first:
the four conditions are CONJUNCTIVE, and the reasoning is what makes the list
narrow. This module is the guard that bounds the ruling, and the ruling's last
line is that nobody presses anything until this exists -- *a ruling is not a
permission to act ahead of the guard that bounds it.*

## WHICH RULE GOVERNS A CALL SITE, because the confusion cost a fortnight

**THIS MODULE GOVERNS THE PACKAGE.** Any press from `linkedin_server/*.py` goes
through :func:`disclose` and is bound by all four conditions below.

**PROBES UNDER ``scripts/`` ARE GOVERNED BY A DIFFERENT RULE** --
``tests/test_probe_interaction_budget.py``, which splits verbs into OPEN and
GATED and lets a probe click freely while requiring a declaration for anything
that persists or sends.

The two are not in competition and they are not the same bar. A probe
legitimately opens a menu to find out what is in it; the package may only do so
under conditions 1-4. **The reason this distinction is stated at the top of the
file rather than inferred is that nobody stated it before**: the package rule
never covered ``scripts/`` at all, so the fleet's restraint was tacit, and for a
fortnight "we do not press" was simultaneously true of the package and false of
the probes, with no test anywhere able to tell the difference.

**TYPING IS REFUSED BY BOTH.** ``page.fill`` is not a press. The one ``fill``
measured in ``scripts/`` is refused by this ruling's own terms whatever the
probe rule concludes about it.

## THE FOUR CONDITIONS, and each is mechanically checkable

1. **THE PAGE IS ALREADY ADMITTED**, by :func:`readonly.is_read_url`, checked
   BEFORE any press. **A press NEVER extends reach.** If the address is refused,
   every control on it is refused. This closes the laundering path -- load an
   admitted page, press into a refused one.
2. **THE CONTROL MATCHES AN ENUMERATED SHAPE, BY ATTRIBUTE** --
   :data:`SANCTIONED_SHAPES`, exact membership, never a label. A label is page
   text and this server does not read page text into decisions.
3. **THE PRESS IS SHOWN NOT TO MOVE AN OUTWARD COUNTER**, read before and after.
   **Where no counter can price the press, UNMEASURABLE RESOLVES AGAINST IT.**
4. **IT IS CLOSED AND THE CLOSURE VERIFIED** -- the toggle restored and the page
   confirmed as found.

## WHY THE CALLER CANNOT HAND IN A SELECTOR

:func:`disclose` takes a SHAPE KEY from a closed tuple, not a selector string.
An arbitrary string can never become a press target -- the same property
``dom.MESSAGING_FILTERS`` gives the one sanctioned read-path click already in
the package, and the same reason: a permission phrased as "may press on that
page" is a different and much wider thing than "may press one of these shapes".

## WHAT IS REFUSED REGARDLESS, and one of these is a finding of this repository

* **COMPOSERS AND EDITORS.** The autosave class. `/article/new/` is admitted for
  READING and opening it may autosave a draft **no surface here can detect** --
  17 draft-listing addresses were run against the boundary and all 17 refused.
  A composer is not a disclosure even when it renders like one.
* **NAVIGATION AND SUBMISSION.**
* **THIRD-PARTY SURFACES.** A press that could register an interaction visible
  to another person is outward-facing, and outward-facing is not the lead's to
  grant. A profile view is the clear case: it discloses content to this server
  AND discloses this server to the person.
* **TYPING.**

## NOT-YET versus NEVER-BY-THIS-ROUTE, and why the distinction is in the output

Every refusal carries ``reachable_by_this_route``. A caller must be able to tell
a control that this mechanism will reach once something else lands from one it
will NEVER reach, because -- in the words of the wave that measured it --
*"filing either as blocked-on-the-mechanism would have been wrong in a way that
looks patient."*

**A DEFERRAL THAT WILL NEVER RESOLVE IS WORSE THAN A REFUSAL, because it
consumes a future wave.** Measured cases that are NEVER, not yet:

* the contact-info control carries **neither** sanctioned attribute. It is
  wired -- ``getEventListeners`` shows a click listener, against a negative
  control of NONE on three static nodes -- but **it declares nothing**, so the
  only way to match it is by LABEL TEXT, which condition 2 forbids. It is also
  refused a second time for opening an editor.
* the intro editor's 11 fields: **0 carry either attribute**, every ``id``
  shapes to opaque, no field has a ``name``.

**AND A LISTENER-PRESENCE MATCHER IS NOT THE ANSWER.** It would admit nearly
every interactive node on the page -- the family wildcard condition 2 exists to
forbid, the same shape as the settings-family pattern that would have admitted
six account-ending spellings. If a third shape is ever needed it is a RULING
REQUEST with a measured blast radius, not an edit here.
"""
from __future__ import annotations

from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from linkedin_server import readonly

#: THE ENUMERATED DISCLOSURE SHAPES. The whole of what may be pressed.
#:
#: Attribute selectors, matched by EXACT MEMBERSHIP in this tuple. A caller
#: names a shape; it cannot supply one. The list grows only by a further
#: ruling, exactly as the URL allowlist does.
SANCTIONED_SHAPES: tuple[str, ...] = (
    "[aria-expanded]",
    "[aria-haspopup]",
)

#: Address fragments that mark a COMPOSER OR EDITOR. Refused for pressing even
#: when the address is admitted for READING -- which `/article/new/` is.
#:
#: **THE PRESS ALLOWLIST IS A STRICT SUBSET OF THE READ ALLOWLIST**, and this
#: tuple is the difference. Stated explicitly because the tempting shortcut is
#: to treat "readable" as "pressable", and the autosave class is precisely the
#: counterexample: a page this server may open is not thereby a page whose
#: controls it may activate.
_COMPOSER_MARKERS: tuple[str, ...] = (
    "/article/new",
    "/preload/sharebox",
    "/messaging/compose",
    "/edit/",
    "/newsletter/new",
    "/post/new",
)

#: A member path segment that is NOT his own. ``/in/me/`` resolves to whoever
#: is signed in; anything else under ``/in/`` is a third party's surface.
_SELF_SEGMENTS = frozenset({"me"})


def _refuse(reason: str, why: str, *, terminal: bool) -> dict[str, Any]:
    """A refusal that names what it saw and says whether it can ever pass.

    ``reachable_by_this_route`` is the half a caller cannot derive and must not
    guess. See the module docstring: a deferral that will never resolve costs a
    future wave, so NEVER is reported as NEVER rather than as not-yet.
    """
    return {
        "pressed": False,
        "refused": reason,
        "why": why,
        "reachable_by_this_route": not terminal,
    }


def check_address(url: Optional[str]) -> dict[str, Any]:
    """Conditions 1 and the composer/third-party refusals. PURE.

    Separated from the press so the whole gate is testable with no browser at
    all, which is what let this module be written and proven while the ruling's
    own instruction stood: nobody presses anything until the mechanism exists,
    including to test it.
    """
    if not url or not str(url).strip():
        return _refuse(
            "no_address",
            "a press with no address cannot be shown to be on an admitted "
            "page, and this gate refuses what it cannot establish.",
            terminal=True,
        )

    address = str(url).strip()
    if not readonly.is_read_url(address):
        return _refuse(
            "address_not_admitted",
            "the page is not on the read allowlist. A PRESS NEVER EXTENDS "
            "REACH: if the address is refused, every control on it is "
            "refused, and no press is a route to a surface the allowlist "
            "will not admit.",
            terminal=True,
        )

    path = urlsplit(address).path.lower()

    for marker in _COMPOSER_MARKERS:
        if marker in path:
            return _refuse(
                "composer_or_editor",
                "composers and editors are refused for pressing even when "
                "admitted for reading. Opening one may autosave a draft this "
                "server has no reachable surface to detect -- 17 candidate "
                "draft-listing addresses were run against the boundary and "
                "all 17 were refused. A composer is not a disclosure even "
                "when it renders like one.",
                terminal=True,
            )

    segments = [segment for segment in path.split("/") if segment]
    if "in" in segments:
        index = segments.index("in")
        member = segments[index + 1] if index + 1 < len(segments) else ""
        if member not in _SELF_SEGMENTS:
            return _refuse(
                "third_party_surface",
                "a press on another person's surface could register an "
                "interaction visible to them. That is outward-facing, and "
                "outward-facing is not this ruling's to grant.",
                terminal=True,
            )

    return {"pressed": False, "admitted": True}


def check_shape(shape: Optional[str]) -> dict[str, Any]:
    """Condition 2. PURE, and it is exact membership rather than a pattern."""
    if shape not in SANCTIONED_SHAPES:
        return _refuse(
            "shape_not_sanctioned",
            "the control does not match an enumerated disclosure shape. Only "
            f"{list(SANCTIONED_SHAPES)} may be pressed, matched BY ATTRIBUTE "
            "and never by label text -- a label is page text and this server "
            "does not read page text into decisions. A control that is wired "
            "but declares neither attribute can only be matched by its label, "
            "which is why it is refused here and why a listener-presence "
            "matcher is not the remedy: that would admit nearly every "
            "interactive node on the page.",
            terminal=True,
        )
    return {"pressed": False, "shape_ok": True}


def check_counters(before: Optional[dict], after: Optional[dict]) -> dict[str, Any]:
    """Condition 3. PURE.

    Each argument is a mapping of counter name to an integer, or None where the
    counter could not be read. **An unreadable counter is not a zero**, and a
    press it cannot price is refused -- UNMEASURABLE RESOLVES AGAINST THE PRESS.
    """
    if not before or not after:
        return _refuse(
            "no_counter_reading",
            "a press must be SHOWN not to move an outward counter, before and "
            "after. With no reading at either end there is nothing to show, "
            "and unmeasurable resolves AGAINST the press rather than for it.",
            terminal=False,
        )

    unreadable = sorted(
        name for name, value in before.items() if value is None
    ) + sorted(
        name for name, value in after.items() if value is None
    )
    if unreadable:
        return _refuse(
            "counter_unreadable",
            f"these counters did not read: {sorted(set(unreadable))}. An "
            "unreadable counter is not a zero and is never treated as one.",
            terminal=False,
        )

    shared = set(before) & set(after)
    if not shared:
        return _refuse(
            "no_counter_prices_this_press",
            "no counter was read at BOTH ends, so nothing prices this press. "
            "Where no counter can price it, the press is not permitted.",
            terminal=False,
        )

    moved = sorted(name for name in shared if before[name] != after[name])
    if moved:
        return _refuse(
            "counter_moved",
            f"these counters moved across the press: {moved}. A PRESS THAT "
            "MOVES AN OUTWARD COUNTER IS A WRITE, whatever it looked like. "
            "This is the condition that catches the autosave class "
            "empirically rather than by enumeration.",
            terminal=True,
        )

    return {"pressed": False, "counters_ok": True, "priced_by": sorted(shared)}


def check_closure(expanded_before: Any, expanded_after: Any) -> dict[str, Any]:
    """Condition 4. PURE.

    A disclosure left open is a change to the rendered state the next reader
    inherits, so the toggle must read as it did before the press.
    """
    if expanded_before is None or expanded_after is None:
        return _refuse(
            "closure_unverifiable",
            "the control's expanded state did not read at one end, so the "
            "closure cannot be verified. An unverified closure is treated as "
            "an open one.",
            terminal=False,
        )
    if expanded_before != expanded_after:
        return _refuse(
            "not_restored",
            f"the control was {expanded_before!r} before and "
            f"{expanded_after!r} after. The page was not left as it was "
            "found.",
            terminal=False,
        )
    return {"pressed": False, "closed": True}


def evaluate(
    *,
    url: Optional[str],
    shape: Optional[str],
    before: Optional[dict] = None,
    after: Optional[dict] = None,
    expanded_before: Any = None,
    expanded_after: Any = None,
) -> dict[str, Any]:
    """THE WHOLE GATE, PURE AND BROWSER-FREE. Conjunctive, in order.

    **THE ORDER IS PART OF THE CONTRACT.** Address first, shape second, and only
    then anything that requires the press to have happened. A caller that runs
    this with no counters gets a refusal BEFORE pressing, which is the point:
    the pre-press half can be evaluated on its own and must pass before any
    control is touched.

    Returns the first refusal, or a permit. It never raises: one unusable
    control is not an error.
    """
    verdict = check_address(url)
    if verdict.get("refused"):
        return verdict
    verdict = check_shape(shape)
    if verdict.get("refused"):
        return verdict

    if before is None and after is None:
        # The PRE-PRESS verdict: everything checkable without acting.
        return {
            "pressed": False,
            "permitted_to_attempt": True,
            "still_to_show": ["counters_unmoved", "closure_verified"],
        }

    verdict = check_counters(before, after)
    if verdict.get("refused"):
        return verdict
    priced_by = verdict.get("priced_by")
    verdict = check_closure(expanded_before, expanded_after)
    if verdict.get("refused"):
        return verdict

    return {
        "pressed": True,
        "permitted": True,
        "priced_by": priced_by,
        "shape": shape,
    }


async def disclose(
    page: Any,
    *,
    shape: str,
    index: int = 0,
    read_counters: Optional[Callable] = None,
) -> dict[str, Any]:
    """Press ONE enumerated disclosure control, or refuse and touch nothing.

    ``shape`` is a KEY FROM :data:`SANCTIONED_SHAPES`, never a selector. An
    arbitrary string cannot become a press target.

    ``read_counters`` is an async callable returning a mapping of counter name
    to int-or-None. It is REQUIRED: with no way to price the press, condition 3
    refuses before anything is touched.

    **THE PRE-PRESS GATE RUNS FIRST AND RETURNS BEFORE ANY CONTROL IS
    TOUCHED.** That ordering is the difference between a guard and a report.
    """
    pre = evaluate(url=getattr(page, "url", None), shape=shape)
    if pre.get("refused"):
        return pre

    if read_counters is None:
        return _refuse(
            "no_counter_reader_supplied",
            "condition 3 requires the press to be SHOWN not to move an "
            "outward counter. Without a reader there is no way to show it, "
            "and unmeasurable resolves against the press.",
            terminal=False,
        )

    locator = page.locator(shape).nth(index)
    try:
        if not int(await page.locator(shape).count()):
            return _refuse(
                "shape_absent_on_this_page",
                "the page draws no control of this shape. That is a fact "
                "about this page, not about the shape.",
                terminal=False,
            )
        expanded_before = await locator.get_attribute("aria-expanded")
        before = await read_counters()
        await locator.click(timeout=CLICK_TIMEOUT_MS)
        after = await read_counters()
        # CLOSE IT. Escape first, because it is the dismissal this repository's
        # probes already use and it closes a menu that has no toggle.
        await page.keyboard.press("Escape")
        expanded_after = await locator.get_attribute("aria-expanded")
    except Exception as exc:  # noqa: BLE001
        # ONLY THE EXCEPTION TYPE. A library's message is composed by code
        # nobody here controls and has been measured carrying selectors and
        # urls.
        return _refuse(
            "press_failed",
            f"the press raised {type(exc).__name__}. Nothing is claimed about "
            "what the page did; a failure is not a refusal and is not a "
            "success.",
            terminal=False,
        )

    return evaluate(
        url=getattr(page, "url", None),
        shape=shape,
        before=before,
        after=after,
        expanded_before=expanded_before,
        expanded_after=expanded_after,
    )


#: The one timeout, named here rather than inline so a reviewer finds it.
CLICK_TIMEOUT_MS = 5_000
