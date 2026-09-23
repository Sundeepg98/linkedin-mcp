"""THE PROFILE EDITOR'S COMMIT STEP: the one ``Save`` press, and the reading that decides it.

## THE DEFECT THIS MODULE EXISTS TO CLOSE, reproduced before it was written

``linkedin_update_profile_field`` shipped on 2026-09-02 as "the best-verified
write this server has", and until 2026-09-24 it never pressed ``Save``.
``writes.perform`` filled (or selected) the field and then ran the gate that
follows every fill -- which for this action fell through to the POST
composer's gate, found no post editor on the intro editor, and declined to
click anything. The verification then re-read THE SAME, STILL-OPEN DIALOG, saw
the value that had just been typed into it, and reported ``field_changed`` --
so the write returned ``performed: true`` for an edit LinkedIn never stored.

MEASURED, lane L7, over a frozen world whose field value persists only if the
dialog's ``Save`` was pressed before the next navigation (the real preview,
``consume`` and ``perform``, in a local headless Chromium):

    performed               true
    observed_state          field_changed
    clicks_made             0
    the stored value        UNCHANGED

Six census rows (``P A8``, ``A11``, ``A13``, ``A17``, ``A19``, ``A21``) file
this tool COVERED-UNFIRED. A live proof run on the shipped code would have
reported success, restored nothing (nothing had changed), and banked six rows
on a check that could not fail -- the ``apply_job`` shape, in the write this
package called its best verified.

## WHAT THIS MODULE DECIDES, and nothing else

* **Whether to press ``Save``.** Read off the SAME self-owned container the
  write aimed in -- ``dom.read_self_owned_editor_fields`` finds it by the one
  control named :data:`SAVE_CONTROL_NAME`, and that anchor is ``Save`` itself,
  MEASURED 2026-08-31 as enabled inside the editor's dialog (section 2g of
  ``_audit/2026-08-31-linkedin-finish.md``). No new script, no new waiver.
* **Whether a notify-network control is ON.** The ruling
  ``SELF-PROFILE-EDITS-NOT-OUTWARD`` permits a live proof only with "notify
  network" confirmed off in the edit dialog. A control this module can NAME as
  a notify-network control that reads checked REFUSES the press; one that
  reads unchecked is reported ``off``; none drawn is reported ``not_drawn``;
  and the switches the editor draws with NO accessible name are COUNTED,
  because an unnamed switch may be exactly that control and this module will
  not guess. ``not_drawn`` beside a non-zero unnamed count is NOT "confirmed
  off", and the receipt says so in words.
* **Whether the editor closed after the press.** Polled with a read, so the
  verification's fresh navigation does not race LinkedIn's own save request.
  A timeout here decides nothing: the verification reads the stored value
  either way.

## WHAT IT DOES NOT DO

It clicks nothing. The press is ``writes.perform``'s one sanctioned click,
drained from the same queue every other action uses; this module only says
whether a selector may join that queue. It reads no VALUE -- the fields reader
it calls returns labels and states, never ``.value``.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce, dom

#: The commit control's accessible name. NOT a second copy of a measurement:
#: it IS ``dom.EDITOR_ANCHOR_NAME``, the name the self-owned container is found
#: by, so "the container this write aimed in" and "the control this module
#: presses" cannot come apart by one of them being re-typed.
SAVE_CONTROL_NAME: str = dom.EDITOR_ANCHOR_NAME

#: The click selector, built from that constant and nothing a caller supplied.
#: A ``button`` role named EXACTLY ``Save`` (the trailing ``s`` makes the match
#: case-sensitive and whole), inside a dialog -- the container shape
#: ``dom.EDITOR_CONTAINER_SELECTOR`` admits. Playwright's strict mode holds the
#: click to exactly one element, and role selectors skip hidden controls, so a
#: closed dialog's leftover button cannot be the one pressed.
SAVE_SELECTOR: str = (
    'css=:is(dialog, [role="dialog"]) >> role=button[name="'
    + SAVE_CONTROL_NAME
    + '"s]'
)

#: WHAT COUNTS AS A NOTIFY-NETWORK CONTROL, as sets of words that must ALL be
#: in the control's accessible name (case-folded). A closed vocabulary, grown
#: by adding a set here, never by returning a name. LinkedIn's own editors are
#: documented as drawing "Notify network" on the position form; nothing on
#: record says the intro editor draws one at all.
NOTIFY_NETWORK_WORDS: tuple[tuple[str, ...], ...] = (
    ("notify",),
    ("share", "network"),
    ("share", "profile", "update"),
)

#: How long to wait, after the press, for the editor to close before the
#: verification navigates away. Ten polls half a second apart: a save is one
#: request, and navigating while it is in flight can abort it -- which would
#: turn a write that worked into one that reads ``value_unchanged``.
EDITOR_CLOSE_POLLS: int = 10
EDITOR_CLOSE_POLL_MS: int = 500


def _is_notify_control(name: str) -> bool:
    folded = str(name or "").casefold()
    if not folded:
        return False
    return any(all(word in folded for word in words) for words in NOTIFY_NETWORK_WORDS)


def _is_checkable(control: dict[str, Any]) -> bool:
    """A control that HOLDS an on/off state, rather than one that is pressed.

    A button that happened to be named "Share with network" would be a thing
    somebody clicks, not a setting the save carries; only a checkable control
    can be the notify-network SETTING the ruling asks about.
    """
    role = str(control.get("role") or "").casefold()
    kind = str(control.get("type") or "").casefold()
    return (
        control.get("checked") is not None
        or role in ("switch", "checkbox", "radio")
        or kind in ("checkbox", "radio")
    )


def _is_unnamed_switch(control: dict[str, Any]) -> bool:
    """A checkable control with no accessible name by any route.

    The two unnamed ``input[type=checkbox][role=switch]`` controls measured in
    the intro editor on 2026-09-19 are the reason this is counted: either could
    be a notify-network toggle, and a name is the only thing this module
    classifies by.
    """
    if str(control.get("name_source") or "none") != "none":
        return False
    return _is_checkable(control)


def save_gate_verdict(reading: dict[str, Any]) -> dict[str, Any]:
    """Decide the ``Save`` press from one reading of the editor container.

    PURE, so every refusal is testable without a browser. ``reading`` is what
    ``dom.read_self_owned_editor_fields`` returned (no dom ids -- this decides
    whether to press, it does not aim by id). Returns the gate block
    ``writes.perform`` reports:

        proceed            True only when every condition below holds
        selector           :data:`SAVE_SELECTOR`, whether or not it proceeds
        refused_condition  None on proceed, else a numbered code
        why                built from counts and constants, never page text
        save_controls      how many controls in the container are named Save
        notify_network     'off' | 'not_drawn' | 'on' | 'unknown' | 'ambiguous'
        unnamed_switches   checkable controls with no accessible name

    THE CONDITIONS, in the order they refuse:

    0. the container is found at all (the reader's own anchor rule);
    1. exactly one control in it is named ``Save``;
    2. that control is not disabled;
    3. at most one control is named for notifying the network;
    4. if one is, it reads unchecked.
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": SAVE_SELECTOR,
        "refused_condition": None,
        "why": "",
        "save_controls": 0,
        "notify_network": None,
        "unnamed_switches": 0,
    }
    refused = (reading or {}).get("refused")
    if refused or not isinstance((reading or {}).get("fields"), list):
        # THE REFUSAL CODE, NOT ITS REASON TEXT. The code is one of three
        # constants the reader defines; its reason is built from constants and
        # counts too, but a code is the whole of what this block needs.
        out["refused_condition"] = "0_editor_not_found"
        out["why"] = (
            "the editor container could not be found after the change was "
            f"entered (the reader answered {str(refused or 'no fields')!r}), so "
            "there is no Save control this gate can say belongs to it. Nothing "
            "was pressed; the change sits unsaved and is discarded by the "
            "verification's fresh navigation."
        )
        return out

    fields = [f for f in reading["fields"] if isinstance(f, dict)]
    saves = [f for f in fields if str(f.get("name") or "") == SAVE_CONTROL_NAME]
    out["save_controls"] = len(saves)
    out["unnamed_switches"] = sum(1 for f in fields if _is_unnamed_switch(f))

    if len(saves) != 1:
        out["refused_condition"] = "1_save_not_exactly_one"
        out["why"] = (
            f"{len(saves)} controls in the editor are named "
            f"{SAVE_CONTROL_NAME!r}, where exactly one is required. Pressing "
            "one of several would be pressing by position. Nothing was saved."
        )
        return out
    if saves[0].get("disabled") is True:
        out["refused_condition"] = "2_save_disabled"
        out["why"] = (
            f"the editor's {SAVE_CONTROL_NAME!r} control is drawn DISABLED after "
            "the change was entered. A disabled control is not pressed to find "
            "out what happens; LinkedIn is saying the form will not save as it "
            "stands. Nothing was saved."
        )
        return out

    notify = [
        f for f in fields
        if _is_checkable(f) and _is_notify_control(str(f.get("name") or ""))
    ]
    if len(notify) > 1:
        out["notify_network"] = "ambiguous"
        out["refused_condition"] = "3_notify_network_ambiguous"
        out["why"] = (
            f"{len(notify)} controls in the editor are named for notifying the "
            "network, where at most one can be read as THE setting. Refused "
            "rather than guessed: the ruling permits a live proof only with "
            "notify-network confirmed off. Nothing was saved."
        )
        return out
    if len(notify) == 1:
        checked = notify[0].get("checked")
        state = "on" if checked is True else ("off" if checked is False else "unknown")
        out["notify_network"] = state
        if state != "off":
            out["refused_condition"] = "4_notify_network_not_off"
            out["why"] = (
                "the editor draws a control named for notifying the network and "
                f"it reads {state!r}. A save with it on is a broadcast, and a "
                "save with it unreadable is a broadcast nobody can rule out -- "
                "so this gate does not press Save, and it does not switch the "
                "control off either: that would be a second change nobody "
                "confirmed. Turn it off yourself and run the write again. "
                "Nothing was saved."
            )
            return out
    else:
        out["notify_network"] = "not_drawn"

    out["proceed"] = True
    unnamed = coerce.as_count(out["unnamed_switches"])
    out["why"] = (
        f"exactly one {SAVE_CONTROL_NAME!r} control is drawn in the editor and it "
        "is enabled; notify-network reads "
        f"{out['notify_network']!r}"
        + (
            f", and {unnamed} switch(es) in the editor carry NO accessible "
            "name, so 'not_drawn' here is not 'confirmed off' -- either of them "
            "could be that control."
            if unnamed and out["notify_network"] == "not_drawn"
            else "."
        )
    )
    return out


async def read_save_gate(page: Any) -> dict[str, Any]:
    """Read the open editor and decide the press. Never raises.

    A reader failure is a refusal carrying the exception's TYPE and nothing
    else: a Playwright message can quote a selector, and through it page
    content, while a class name cannot.
    """
    try:
        reading = await dom.read_self_owned_editor_fields(page)
    except Exception as exc:  # noqa: BLE001 - reported as a refusal
        verdict = save_gate_verdict({"refused": type(exc).__name__})
        return verdict
    return save_gate_verdict(reading)


async def wait_for_editor_to_close(
    page: Any,
    *,
    polls: int = EDITOR_CLOSE_POLLS,
    poll_ms: int = EDITOR_CLOSE_POLL_MS,
) -> dict[str, Any]:
    """After the press: poll until no ``Save`` control is drawn in a dialog.

    Returns ``closed`` (True / False / None) and ``polls`` taken. ``None``
    means the reading itself failed, which is not the same answer as "still
    open". NOTHING IS DECIDED FROM THIS -- it exists so the verification does
    not navigate away while LinkedIn's save request may still be in flight, and
    so the receipt can say whether the editor closed. A dialog that stays open
    after Save is usually LinkedIn declining the value (a validation message);
    the verification's fresh read of the stored value is still what decides.
    """
    taken = 0
    for _ in range(max(1, coerce.as_count(polls))):
        taken += 1
        try:
            drawn = coerce.as_count(await page.locator(SAVE_SELECTOR).count())
        except Exception:  # noqa: BLE001 - a measurement, not a gate
            return {"closed": None, "polls": taken}
        if drawn == 0:
            return {"closed": True, "polls": taken}
        await page.wait_for_timeout(coerce.as_count(poll_ms))
    return {"closed": False, "polls": taken}


def notify_network_note(gate: Optional[dict[str, Any]]) -> str:
    """The sentence the receipt prints about condition 1 of the ruling.

    Kept here, beside the reading it describes, so the words and the states
    cannot drift apart.
    """
    if not gate:
        return (
            "not read: the save gate did not run, so nothing was pressed and "
            "there is no notify-network reading for this write."
        )
    state = gate.get("notify_network")
    unnamed = coerce.as_count(gate.get("unnamed_switches"))
    if state == "off":
        return "CONFIRMED OFF: a control named for notifying the network was read unchecked in the edit dialog."
    if state == "not_drawn" and not unnamed:
        return (
            "NOT DRAWN: no control in the edit dialog is named for notifying the "
            "network, and every checkable control in it carries a name. This "
            "editor offers no per-edit notify setting to confirm; the account-wide "
            "'share profile updates' setting is a settings-family page this server "
            "does not open."
        )
    if state == "not_drawn":
        return (
            f"NOT CONFIRMED: no control in the edit dialog is NAMED for notifying "
            f"the network, but {unnamed} checkable control(s) carry no name at "
            "all and either could be it. That is not 'confirmed off'."
        )
    return f"REFUSED ON IT: the notify-network reading was {state!r}, so Save was not pressed."
