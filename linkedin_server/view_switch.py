"""THE VIEW SWITCH: apply ONE filter on his own page, read the view, and put it back.

Implements the call registered as ``VIEW-SWITCH-PRESS-RESTORED``
(orchestrator, 2026-09-23, delegated): *"VIEW-SWITCH PRESSES are permitted: a
press that changes which rows a view shows, such as a sort or filter control.
The view must be RESTORED afterwards, with readings taken before and after the
press to prove it."*

## WHAT IS PRESSED, AND WHAT IS NOT

One table entry names one surface, one filter pill (by its caption) and one
option in it (by its label). Nothing else on the page is a candidate. The
sequence, all inside :func:`apply_and_restore`:

    open the pill        a disclosure; the pill is [aria-expanded], role=button
    select the option    div[role=checkbox|radio] whose aria-label EQUALS the entry's
    apply                the popover's own "show results" button
    read                 the view, through the caller's ``read_view``
    reopen, deselect, apply again
    read                 the view again -- and it must EQUAL the first reading

Measured before it was written (``_audit/2026-09-23-live-lane-session-1.md``
Entry 3): each option is a ``div[role=checkbox]`` or ``div[role=radio]`` whose
name is its ``aria-label`` and whose state is ``aria-checked``; each popover
carries its own "reset" and "show results" buttons, both plain
``button[type=button]``. **Escape is never used here**: on the same page a
popover that holds a text input stayed open after Escape and the gate refused
it (``not_restored``). "show results" is the control that closes a popover by
design, so it is the one used.

## WHY A LABEL IS COMPARED HERE

The disclosing-press ruling refuses label-matching for DISCLOSURES; this is
not one, and the call that permits it names no aiming rule. A caption or an
option label is compared, by EXACT equality after normalisation (lower-case;
every run outside ``[a-z0-9]`` becomes one space), against a phrase in the
table below -- it yields a boolean and is never returned. The pill is still
found among the page's ``[aria-expanded]`` controls in ``main``, by the same
structural filter the shipped pill opener uses.

## WHAT MUST BE SHOWN

``restored`` is True only if the view read after the restore EQUALS the view
read before the switch (every field ``read_view`` returns, compared whole),
the option reads ``aria-checked="false"`` again, the pill is closed, the url's
path never moved, and no counter moved across the whole sequence. A switch
that applied and could not be restored says so as loudly as it can -- it is
the one outcome this module exists to prevent, and it is reported, never
smoothed.

## THE ONE CALL SITE

``readonly.SANCTIONED_MUTATIONS`` holds ``("linkedin_server/view_switch.py",
"_activate", "click")`` -- ONE line, because the package's count test admits
one call per entry and "not a licence". :func:`_activate` is the drain point
every step of the sequence goes through, and ``tests/test_view_switch.py``
pins that :func:`apply_and_restore` is its only caller. The other helpers
below only read.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from linkedin_server import press

_refuse = press._refuse

_ENTRY_REQUIRED = ("surfaces", "pill_caption", "option", "ruling", "why")

_RULING = (
    "VIEW-SWITCH-PRESS-RESTORED (orchestrator, 2026-09-23, delegated): a press "
    "that changes which rows a view shows is permitted if the view is RESTORED "
    "afterwards and a before/after reading proves it."
)

VIEW_SWITCHES: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "interesting_viewers_verified",
        {
            "surfaces": ("/analytics/profile-views/",),
            "pill_caption": "interesting viewers",
            "option": "verified",
            "ruling": _RULING,
            "why": (
                "The 'Interesting viewers' pill is the census's notable-viewers "
                "surface (N 134). Measured 2026-09-23: two checkbox options, "
                "'works at a company you follow' and 'verified', none checked, "
                "and the popover's own 'show results'."
            ),
        },
    ),
    (
        "interesting_viewers_company_you_follow",
        {
            "surfaces": ("/analytics/profile-views/",),
            "pill_caption": "interesting viewers",
            "option": "works at a company you follow",
            "ruling": _RULING,
            "why": "The same pill's other option, measured the same day.",
        },
    ),
)

#: The popover's apply control: "show results", or "show 365 results", matched
#: AFTER normalisation -- which turns "1,234" into "1 234", so a count is one or
#: more digit groups, each preceded by one space.
APPLY_PATTERN = re.compile(r"^show(?: [0-9]+)* results?$")
#: The option controls a popover draws.
OPTION_SELECTOR = '[role="checkbox"][aria-label], [role="radio"][aria-label]'
#: How long to wait for a popover's options after opening it. Bounded, one wait.
OPEN_WAIT_MS = 5000
#: How long a view is given to re-render after "show results". Bounded, single.
APPLY_SETTLE_MS = 2500
CLICK_TIMEOUT_MS = press.CLICK_TIMEOUT_MS

_NOT_ALNUM = re.compile(r"[^a-z0-9]+")


def normalised(text: Any) -> str:
    """Lower-case; every run outside ``[a-z0-9]`` becomes one space. PURE."""
    return _NOT_ALNUM.sub(" ", str(text or "").lower()).strip()


def view_switch(key: Optional[str]) -> Optional[dict[str, Any]]:
    """The table entry for a key, or None. PURE."""
    for name, entry in VIEW_SWITCHES:
        if name == key:
            return entry
    return None


def check_switch(url: Optional[str], key: Optional[str]) -> dict[str, Any]:
    """The pre-press half. PURE, and every refusal knowable from the address
    and the key is decided here, before the page is asked for anything."""
    entry = view_switch(key)
    if entry is None:
        return _refuse(
            "switch_not_ruled",
            "the key is not in view_switch.VIEW_SWITCHES. A view switch is one "
            "named option on one named surface; a caller names one and cannot "
            "supply one.",
            terminal=True,
        )
    missing = [field for field in _ENTRY_REQUIRED if not entry.get(field)]
    if missing:
        return _refuse(
            "switch_entry_incomplete",
            f"the table entry is missing {missing}; an entry with no ruling or "
            "no option is not an admission.",
            terminal=True,
        )
    address = press.check_address(url)
    if address.get("refused"):
        return address
    if urlsplit(str(url).strip()).path not in entry["surfaces"]:
        return _refuse(
            "switch_not_for_this_surface",
            "the page is not one this switch names. A filter measured on one "
            "surface says nothing about another.",
            terminal=True,
        )
    basis = press.check_basis(url)
    if basis.get("refused"):
        return basis
    return {"pressed": False, "switch_ok": True, "basis": basis.get("basis")}


def _path(url: Any) -> str:
    return urlsplit(str(url or "")).path


async def _activate(target: Any) -> None:
    """THE ONE CLICK IN THIS MODULE. Called only by :func:`apply_and_restore`,
    for each step of its sequence, on a target that function has already
    chosen and checked."""
    await target.click(timeout=CLICK_TIMEOUT_MS)


async def _pill_positions(page: Any, caption: str) -> list[int]:
    """Main-scoped pills whose caption EQUALS ``caption``. READS ONLY."""
    pills = page.locator("main").locator("[aria-expanded]")
    found: list[int] = []
    for position in range(int(await pills.count())):
        pill = pills.nth(position)
        if (await pill.get_attribute("role") or "") != "button":
            continue
        if not await pill.is_visible():
            continue
        if normalised(await pill.inner_text()) == caption:
            found.append(position)
    return found


async def _option_positions(page: Any, option: str) -> list[int]:
    """Visible option controls whose aria-label EQUALS ``option``. READS ONLY."""
    options = page.locator(OPTION_SELECTOR)
    found: list[int] = []
    for position in range(int(await options.count())):
        candidate = options.nth(position)
        if not await candidate.is_visible():
            continue
        if normalised(await candidate.get_attribute("aria-label")) == option:
            found.append(position)
    return found


async def _apply_positions(page: Any) -> list[int]:
    """Visible buttons whose text is 'show [N] results'. READS ONLY."""
    buttons = page.locator("button")
    found: list[int] = []
    for position in range(int(await buttons.count())):
        candidate = buttons.nth(position)
        if not await candidate.is_visible():
            continue
        if APPLY_PATTERN.match(normalised(await candidate.inner_text())):
            found.append(position)
    return found


async def _wait_for_option(page: Any, option: str) -> list[int]:
    """One bounded wait for the popover's options, then one read. READS ONLY."""
    try:
        await page.locator(OPTION_SELECTOR).first.wait_for(state="visible", timeout=OPEN_WAIT_MS)
    except Exception:  # noqa: BLE001 - absence is reported by the read below
        return []
    return await _option_positions(page, option)


async def apply_and_restore(
    page: Any,
    *,
    key: str,
    read_view: Optional[Callable] = None,
    read_counters: Optional[Callable] = None,
) -> dict[str, Any]:
    """Apply ONE ruled filter, read the view, restore it, prove the restore.

    ``read_view`` is an async callable returning a JSON-shaped mapping that
    describes what the view SHOWS (the caller decides what -- rows, a
    headline); it is compared whole, before and after. ``read_counters`` is
    the async counter reader ``press.disclose`` takes. The filtered view comes
    back under ``view_applied``, exactly as ``read_view`` returned it.
    """
    address = getattr(page, "url", None)
    pre = check_switch(address, key)
    if pre.get("refused"):
        return pre
    if read_view is None:
        return _refuse(
            "no_view_reader_supplied",
            "a restore is proven by reading the view before and after; without "
            "a reader there is no proof, so nothing is pressed.",
            terminal=False,
        )
    if read_counters is None:
        return _refuse(
            "no_counter_reader_supplied",
            "a view switch must be shown to move no counter; without a reader "
            "there is no way to show it.",
            terminal=False,
        )
    entry = view_switch(key) or {}
    caption, option = str(entry["pill_caption"]), str(entry["option"])
    pills = page.locator("main").locator("[aria-expanded]")
    options = page.locator(OPTION_SELECTOR)
    buttons = page.locator("button")
    stage = "before_any_press"
    applied = False
    try:
        before = await read_counters()
        if not before or any(value is None for value in before.values()):
            return _refuse(
                "counters_unreadable_before_any_press",
                "a counter did not read before the switch, so it could not be "
                "priced; refused with nothing touched.",
                terminal=False,
            )
        pill_at = await _pill_positions(page, caption)
        if len(pill_at) != 1:
            return _refuse(
                "pill_not_unique",
                f"{len(pill_at)} pills in main carry this entry's caption; "
                "exactly one is required, so nothing was pressed.",
                terminal=False,
            )
        pill = pills.nth(pill_at[0])
        view_before = await read_view()

        # ---- APPLY ---------------------------------------------------------
        stage = "opening"
        await _activate(pill)
        option_at = await _wait_for_option(page, option)
        if len(option_at) != 1:
            await _activate(pill)
            return _refuse(
                "option_not_unique",
                f"{len(option_at)} visible options carry this entry's label "
                "once the pill opened; the pill was closed again and nothing "
                "was selected.",
                terminal=False,
            )
        if (await options.nth(option_at[0]).get_attribute("aria-checked")) != "false":
            await _activate(pill)
            return _refuse(
                "option_already_applied",
                "the option did not read unchecked before the switch, so the "
                "view was not in the state a restore would return to; nothing "
                "was selected.",
                terminal=False,
            )
        stage = "selecting"
        await _activate(options.nth(option_at[0]))
        if (await options.nth(option_at[0]).get_attribute("aria-checked")) != "true":
            await _activate(options.nth(option_at[0]))
            await _activate(pill)
            return _refuse(
                "option_did_not_select",
                "the option did not read checked after the press; it was pressed "
                "again and the pill closed, and nothing was applied.",
                terminal=False,
            )
        apply_at = await _apply_positions(page)
        if len(apply_at) != 1:
            await _activate(options.nth(option_at[0]))
            await _activate(pill)
            return _refuse(
                "apply_control_not_unique",
                f"{len(apply_at)} visible 'show results' buttons; the option "
                "was deselected, the pill closed, and nothing was applied.",
                terminal=False,
            )
        stage = "applying"
        await _activate(buttons.nth(apply_at[0]))
        applied = True
        await page.wait_for_timeout(APPLY_SETTLE_MS)
        closed_after_apply = (await pill.get_attribute("aria-expanded")) == "false"
        path_after_apply = _path(getattr(page, "url", None))
        view_applied = await read_view()

        # ---- RESTORE -------------------------------------------------------
        stage = "reopening"
        await _activate(pill)
        option_at = await _wait_for_option(page, option)
        restore_found = (
            len(option_at) == 1
            and (await options.nth(option_at[0]).get_attribute("aria-checked")) == "true"
        )
        if restore_found:
            stage = "deselecting"
            await _activate(options.nth(option_at[0]))
            deselected = (await options.nth(option_at[0]).get_attribute("aria-checked")) == "false"
            apply_at = await _apply_positions(page)
            if deselected and len(apply_at) == 1:
                stage = "reapplying"
                await _activate(buttons.nth(apply_at[0]))
                applied = False
                await page.wait_for_timeout(APPLY_SETTLE_MS)
        if (await pill.get_attribute("aria-expanded")) == "true":
            # THE RESTORE COULD NOT FINISH AND THE POPOVER IS STILL OPEN. Close
            # it by the same toggle that opened it; ``left_applied`` says the
            # rest, and the refusal below says it loudly.
            stage = "closing"
            await _activate(pill)
        closed_after_restore = (await pill.get_attribute("aria-expanded")) == "false"
        path_after_restore = _path(getattr(page, "url", None))
        view_restored = await read_view()
        after = await read_counters()
    except Exception as exc:  # noqa: BLE001
        failure = _refuse(
            "press_failed",
            f"the switch raised {type(exc).__name__} while {stage}. Nothing is "
            "claimed about what the page did.",
            terminal=False,
        )
        failure["pressed"] = stage != "before_any_press"
        failure["left_applied"] = applied
        return failure

    counters = press.check_counters(before, after, basis=press.sensitivity_basis(address))
    path_before = _path(address)
    restored = bool(
        not applied
        and view_restored == view_before
        and closed_after_restore
        and path_after_restore == path_before
    )
    measured: dict[str, Any] = {
        "pressed": True,
        "key": key,
        "applied_view_differs": view_applied != view_before,
        "closed_after_apply": closed_after_apply,
        "closed_after_restore": closed_after_restore,
        "path_unchanged": path_after_apply == path_before and path_after_restore == path_before,
        "left_applied": applied,
        "restored": restored,
        "counters": counters,
        "view_applied": view_applied,
        "permitted": bool(restored and not counters.get("refused")),
    }
    if measured["permitted"]:
        return measured
    if applied:
        refusal = _refuse(
            "switch_left_applied",
            "THE FILTER WAS APPLIED AND COULD NOT BE TAKEN OFF: the option or "
            "its apply control was not found again. The view is left filtered "
            "on this page.",
            terminal=False,
        )
    elif not restored:
        refusal = _refuse(
            "switch_not_restored",
            "the view read after the restore does not equal the view read "
            "before the switch, or the pill did not close, or the path moved.",
            terminal=False,
        )
    else:
        refusal = _refuse(
            "switch_moved_a_counter",
            "the view was restored, but a counter the surface is priced by did "
            "not read the same at both ends; see counters.",
            terminal=False,
        )
    return {**refusal, **measured}
