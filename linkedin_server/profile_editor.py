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
* **Whether condition 1 of the ruling is established.** The ruling
  ``SELF-PROFILE-EDITS-NOT-OUTWARD`` permits a live proof only with "notify
  network" confirmed off. A control this module can NAME as a notify-network
  control that reads checked (or unreadable) REFUSES the press; one that reads
  unchecked establishes condition 1 in the dialog. Where the dialog draws NO
  such control, the condition is established only by his account-level
  setting read OFF before the edit -- the amendment described at
  :data:`ACCOUNT_READINGS`, whose reader does not exist yet -- so today the
  gate REFUSES there (``5_condition_1_not_established``, NEEDS-OPERATOR).
  Switches drawn with NO accessible name are COUNTED, because an unnamed
  switch may be exactly that control and this module will not guess.
  **UNTIL 2026-09-24 (lane L7 integration) a dialog drawing no notify control
  did not refuse:** the gate pressed Save and only the receipt's words said
  "NOT DRAWN" or "NOT CONFIRMED", leaving condition 1 to be judged after the
  press. It refuses before the press now.
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

#: THE SEAM FOR THE AMENDED CONDITION 1 -- DELIBERATELY NOT WIRED (2026-09-24).
#:
#: Condition 1 of ``SELF-PROFILE-EDITS-NOT-OUTWARD`` is amended by the ruling
#: ``SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED`` (registered 2026-09-24, in
#: ``_audit/2026-09-24-rulings-notify-veto-and-who-which.md``): where the edit
#: dialog draws no notify control, his ACCOUNT-LEVEL setting "Share profile
#: updates with your network", read OFF BEFORE the edit, satisfies the
#: condition; where neither that nor a dialog control read off is established,
#: the write is NEEDS-OPERATOR.
#:
#: The account-level reading enters here and nowhere else: the keyword
#: ``account_share_updates`` of :func:`save_gate_verdict` and
#: :func:`read_save_gate`, one of these values, or ``None`` for "not read".
#: NOTHING SUPPLIES IT YET. The reader is the live lane's to build, and
#: ``writes.perform`` calls :func:`read_save_gate` without it -- so the gate
#: presses only on a dialog control read off, and refuses wherever the dialog
#: draws none. Wiring is the caller's whole job when the reader lands: take the
#: reading BEFORE the change is entered (the amendment's word), pass it here;
#: no rule in this module moves.
#:
#: AN UNNAMED SWITCH REFUSES UNTIL A CAPTURE IDENTIFIES IT, AND THE AMENDMENT
#: SAYS SO: a switch the dialog cannot name is not evidence either way -- the
#: condition is not met while one is present, even with the account setting
#: read OFF, until a capture identifies that switch
#: (``6_unnamed_switch_unresolved``). The live lane's capture of the intro
#: editor identified its two ('Open Profile' and 'Profile Premium Badge',
#: `_audit/2026-09-23-live-lane-session-1.md`, Entry 5), and this gate ties a
#: switch it sees to that identification BY STRUCTURE -- see
#: :data:`INTRO_SWITCH_BLOCKS` -- so for the intro editor, and only there,
#: those two no longer block. Any other unnamed switch still does.
ACCOUNT_READINGS: tuple[str, ...] = ("off", "on", "unknown")

#: THE INTRO EDITOR'S TWO UNNAMED SWITCHES, RECOGNISED BY STRUCTURE, NEVER BY A
#: LABEL (2026-09-24, lane L7 follow-up).
#:
#: WHAT THE CAPTURE DRAWS, measured offline on the one render on record: both
#: switches are ``input[type=checkbox][role=switch]`` whose own ``label`` is
#: drawn EMPTY, each the only input inside a wrapper ``div`` carrying
#: ``role=switch`` and ``aria-checked``. Each wrapper sits in a SETTING BLOCK of
#: exactly two parts -- a text part holding paragraphs and no control, then the
#: part holding the wrapper -- and both blocks sit in one SETTINGS ROW: a
#: leading paragraph, then exactly those two blocks. That row is a direct child
#: of the dialog's scrolling column, which the page names with a test id. The
#: two blocks are identical in EVERY attribute but two random ones: a
#: ``componentkey`` of random-UUID (version 4) shape and an input id of the
#: shape React generates -- random BY THOSE SHAPES, since one render is on
#: record. **The capture draws no section element, no heading, no heading id and
#: no aria-describedby** around either switch, so the anchor is the nearest
#: element above them that the page itself names -- that column -- and the row
#: under it is found by structure and attribute PRESENCE: the press rules'
#: discipline, an enumerated shape and never a label. The only text the
#: identification rests on, each block's title paragraph, is never read.
#:
#: IDENTITY IS THE BLOCK'S ORDER IN THAT ROW, as the capture recorded it:
#: :data:`INTRO_SWITCH_IDENTITIES`. That is enough to LIFT CODE 6 -- the two are
#: both identified as not notify controls, so which is which changes nothing
#: there -- and it is NOT enough to AIM a press at one of them: order is
#: position, and this module refuses to press one of several by position. A
#: row that draws a third block, a third unnamed switch anywhere in the dialog,
#: or a switch in any other shape is not recognised, and code 6 stands for it.
#:
#: NO NEW SCRIPT AND NO NEW WAIVER, the same promise as the rest of this
#: module: every question below is a ``locator(...).count()``, so the page runs
#: nothing it did not already run, and what comes back is an integer.
INTRO_SWITCH_IDENTITIES: tuple[str, ...] = ("open_profile", "profile_premium_badge")

#: The anchor above the row: the dialog's scrolling column, by the test id the
#: capture shows the page drawing on it. An attribute VALUE, as ``role="switch"``
#: is -- a name in LinkedIn's code, never text a viewer reads.
INTRO_SWITCH_COLUMN: str = '[data-testid="lazy-column"]'

#: The dialog the fields reader scopes to, found the same way: a ``dialog`` /
#: ``[role=dialog]`` holding the one control named :data:`SAVE_CONTROL_NAME`.
_EDITOR_DIALOG: str = 'css=:is(dialog, [role="dialog"])'
_SAVE_CONTROL: str = 'role=button[name="' + SAVE_CONTROL_NAME + '"s]'

#: From a setting block down to its wrapper: the block's second part, and the
#: ``role=switch`` + ``aria-checked`` element directly inside it.
_INTRO_WRAPPER_PATH: str = ' > div:last-child > div[role="switch"][aria-checked]'

#: THE SETTINGS ROW: a direct child of the column whose element children are
#: exactly a paragraph and then two blocks, the second and third children each
#: holding a wrapper with a checkbox in it. Several ``:has()`` side by side and
#: none inside another, because CSS does not nest them.
INTRO_SWITCH_ROW: str = (
    INTRO_SWITCH_COLUMN
    + " > div:has(> p:first-child + div + div:last-child)"
    + ":has(> div:nth-child(2)" + _INTRO_WRAPPER_PATH + ' input[type="checkbox"])'
    + ":has(> div:nth-child(3)" + _INTRO_WRAPPER_PATH + ' input[type="checkbox"])'
)

#: THE ENUMERATED SHAPES, one setting block per identity in the recorded order:
#: the row's second element child is ``INTRO_SWITCH_IDENTITIES[0]``, its third
#: is ``[1]``. Each is exactly two parts, the first holding a paragraph and no
#: control. Exact membership, as in ``press.SANCTIONED_SHAPES``: each shape
#: must match exactly one element, or nothing is recognised.
INTRO_SWITCH_BLOCKS: tuple[str, ...] = tuple(
    INTRO_SWITCH_ROW
    + " > div:nth-child(" + str(position) + ")"
    + ":has(> div:first-child + div:last-child)"
    + ":has(> div:first-child p)"
    + ":not(:has(> div:first-child :is(input, button, select, textarea, a[href], [role])))"
    for position in (2, 3)
)

#: THE SWITCH ITSELF, inside its wrapper: the capture's pairing of an EMPTY
#: label immediately before an ``input[type=checkbox][role=switch]`` that
#: carries no naming attribute and sits inside no label. The accessible-name
#: half of "unnamed" -- a non-empty label pointing at it from anywhere -- is
#: asked of Playwright's own name computation beside this, in
#: :func:`recognise_intro_editor_switches`.
_INTRO_SWITCH_INPUT: str = (
    ' label:empty + input[type="checkbox"][role="switch"]'
    ":not([aria-label]):not([aria-labelledby]):not([title]):not(label *)"
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


def save_gate_verdict(
    reading: dict[str, Any],
    *,
    account_share_updates: Optional[str] = None,
    recognised_switches: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Decide the ``Save`` press from one reading of the editor container.

    PURE, so every refusal is testable without a browser. ``reading`` is what
    ``dom.read_self_owned_editor_fields`` returned (no dom ids -- this decides
    whether to press, it does not aim by id). ``account_share_updates`` is the
    seam described at :data:`ACCOUNT_READINGS`; nothing passes it today.
    ``recognised_switches`` is :func:`recognise_intro_editor_switches`'s reading;
    absent, no switch is recognised. Returns the gate block ``writes.perform``
    reports:

        proceed            True only when every condition below holds
        selector           :data:`SAVE_SELECTOR`, whether or not it proceeds
        refused_condition  None on proceed, else a numbered code
        why                built from counts and constants, never page text
        save_controls      how many controls in the container are named Save
        notify_network     'off' | 'not_drawn' | 'on' | 'unknown' | 'ambiguous'
        unnamed_switches   checkable controls with no accessible name
        recognised_switches  the capture-identified ones among them, by
                           identity from :data:`INTRO_SWITCH_IDENTITIES`
        unresolved_switches  unnamed and NOT recognised -- what code 6 counts
        condition_1        on proceed, what established it:
                           'dialog_control_off' | 'account_setting_off'

    THE CONDITIONS, in the order they refuse:

    0. the container is found at all (the reader's own anchor rule);
    1. exactly one control in it is named ``Save``;
    2. that control is not disabled;
    3. at most one control is named for notifying the network;
    4. if one is, it reads unchecked;
    5. if none is, the account-level setting was read ``'off'``;
    6. and, on that account-level route, every unnamed switch in the dialog
       is one a capture identified (the ruling's own words).
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": SAVE_SELECTOR,
        "refused_condition": None,
        "why": "",
        "save_controls": 0,
        "notify_network": None,
        "unnamed_switches": 0,
        "recognised_switches": [],
        "unresolved_switches": 0,
        "condition_1": None,
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
    identities = _recognised_identities(recognised_switches, out["unnamed_switches"])
    out["recognised_switches"] = identities
    out["unresolved_switches"] = out["unnamed_switches"] - len(identities)

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
        out["condition_1"] = "dialog_control_off"
    else:
        out["notify_network"] = "not_drawn"
        unresolved = coerce.as_count(out["unresolved_switches"])
        # THE ACCOUNT-LEVEL ROUTE, the only other basis condition 1 can have.
        # Anything but the exact reading 'off' -- not read, 'on', unreadable,
        # or a value this module does not recognise -- establishes nothing.
        account = (
            account_share_updates
            if account_share_updates in ACCOUNT_READINGS
            else None
        )
        if account != "off":
            out["refused_condition"] = "5_condition_1_not_established"
            heard = {
                None: "was not read before the edit (nothing supplies that reading yet)",
                "on": "was read ON before the edit",
                "unknown": "could not be read before the edit",
            }[account]
            out["why"] = (
                "the edit dialog draws no control named for notifying the "
                "network, and his account-level 'Share profile updates with your "
                f"network' setting {heard}. Condition 1 of the ruling is "
                "established by neither route, so this is NEEDS-OPERATOR: Save "
                "was not pressed, and the change sits unsaved until the "
                "verification's fresh navigation discards it."
                + (
                    f" {unresolved} switch(es) in the dialog carry no accessible "
                    "name and no capture identifies them, and either could be a "
                    "per-edit notify control."
                    if unresolved
                    else ""
                )
            )
            return out
        if unresolved:
            out["refused_condition"] = "6_unnamed_switch_unresolved"
            out["why"] = (
                "his account-level 'Share profile updates with your network' "
                "setting was read OFF before the edit, but "
                f"{unresolved} switch(es) in the dialog carry no accessible name "
                "and are not among the switches a capture identified, and either "
                "could be a per-edit notify control this gate cannot read. The "
                "ruling does not count the condition met while one is present, "
                "until a capture identifies it. NEEDS-OPERATOR: Save was not "
                "pressed."
            )
            return out
        out["condition_1"] = "account_setting_off"

    out["proceed"] = True
    basis = {
        "dialog_control_off": (
            "a control named for notifying the network reads unchecked in the "
            "edit dialog"
        ),
        "account_setting_off": (
            "the dialog draws no notify control, every unnamed switch in it is "
            "one a capture identified, and his account-level setting was read "
            "off before the edit"
        ),
    }[out["condition_1"]]
    out["why"] = (
        f"exactly one {SAVE_CONTROL_NAME!r} control is drawn in the editor and it "
        f"is enabled; condition 1 is established because {basis}."
    )
    return out


def _recognised_identities(
    reading: Optional[dict[str, Any]], unnamed: int
) -> list[str]:
    """The identities the structural reading ties to the capture -- or none.

    ALL OR NOTHING, and conservative in every other case: the reading must name
    exactly :data:`INTRO_SWITCH_IDENTITIES`, each once, drawn from that closed
    tuple rather than from anything the page returned, and there must be at
    least as many unnamed switches in the fields reading as it recognised. A
    reading that disagrees with the fields reader recognises nothing, so the
    switches stay unresolved and code 6 stands.
    """
    identities = (reading or {}).get("identities")
    if not isinstance(identities, list):
        return []
    if sorted(identities) != sorted(INTRO_SWITCH_IDENTITIES):
        return []
    if coerce.as_count(unnamed) < len(identities):
        return []
    return [i for i in INTRO_SWITCH_IDENTITIES if i in identities]


async def recognise_intro_editor_switches(page: Any) -> dict[str, Any]:
    """Recognise the intro editor's two capture-identified switches. Never raises.

    Every question is a ``locator(...).count()`` against the shapes above, so
    what comes back from the page is integers. Returns:

        recognised   0, or the number of :data:`INTRO_SWITCH_IDENTITIES`
        identities   in row order, from that closed tuple -- never page text
        checked      the same order's checked states; ``None`` where the input
                     and its ``aria-checked`` wrapper disagree
        containers   dialogs holding the one ``Save`` control (1 required)
        rows         settings rows of the recorded shape under the column
                     (1 required)
        checkables   ``input[type=checkbox]`` in that dialog, for the receipt
        error        an exception's TYPE if the reading failed

    Recognition is all or nothing: one dialog, one row, and for EACH identity
    exactly one block holding exactly one checkbox, which is the recorded
    unnamed switch by its attributes AND has no accessible name by
    Playwright's own computation (hidden or not, as the fields reader counts
    hidden controls too). Anything else recognises none, and the gate's code 6
    then counts every unnamed switch.
    """
    out: dict[str, Any] = {
        "recognised": 0,
        "identities": [],
        "checked": [],
        "containers": 0,
        "rows": 0,
        "checkables": 0,
        "error": None,
    }
    try:
        dialog = page.locator(_EDITOR_DIALOG, has=page.locator(_SAVE_CONTROL))
        out["containers"] = coerce.as_count(await dialog.count())
        if out["containers"] != 1:
            return out
        out["checkables"] = coerce.as_count(
            await dialog.locator('css=input[type="checkbox"]').count()
        )
        out["rows"] = coerce.as_count(
            await dialog.locator("css=" + INTRO_SWITCH_ROW).count()
        )
        if out["rows"] != 1:
            return out
        unnamed_switch = dialog.get_by_role(
            "switch", name="", exact=True, include_hidden=True
        )
        states: list[Optional[bool]] = []
        for block in INTRO_SWITCH_BLOCKS:
            wrapper = block + _INTRO_WRAPPER_PATH
            switch = wrapper + _INTRO_SWITCH_INPUT
            held = await dialog.locator(
                "css=" + block + ' input[type="checkbox"]'
            ).count()
            wrappers = await dialog.locator("css=" + wrapper).count()
            shaped = await dialog.locator("css=" + switch).count()
            unnamed = await dialog.locator("css=" + switch).and_(unnamed_switch).count()
            if any(coerce.as_count(n) != 1 for n in (held, wrappers, shaped, unnamed)):
                return out
            on = coerce.as_count(
                await dialog.locator("css=" + switch + ":checked").count()
            )
            wrapper_on = coerce.as_count(
                await dialog.locator(
                    "css=" + block + _INTRO_WRAPPER_PATH + '[aria-checked="true"]'
                ).count()
            )
            states.append((on == 1) if (on == 1) == (wrapper_on == 1) else None)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
        return out
    out["recognised"] = len(INTRO_SWITCH_IDENTITIES)
    out["identities"] = list(INTRO_SWITCH_IDENTITIES)
    out["checked"] = states
    return out


async def read_save_gate(
    page: Any, *, account_share_updates: Optional[str] = None
) -> dict[str, Any]:
    """Read the open editor and decide the press. Never raises.

    A reader failure is a refusal carrying the exception's TYPE and nothing
    else: a Playwright message can quote a selector, and through it page
    content, while a class name cannot. ``account_share_updates`` is passed
    through to :func:`save_gate_verdict` unchanged; see :data:`ACCOUNT_READINGS`
    for why no caller supplies it yet.
    """
    try:
        reading = await dom.read_self_owned_editor_fields(page)
    except Exception as exc:  # noqa: BLE001 - reported as a refusal
        verdict = save_gate_verdict(
            {"refused": type(exc).__name__},
            account_share_updates=account_share_updates,
        )
        return verdict
    # Only a reading that FOUND the container is worth recognising in: a
    # refusal is code 0 whatever the switches are.
    switches = (
        await recognise_intro_editor_switches(page)
        if isinstance(reading, dict) and "fields" in reading
        else None
    )
    return save_gate_verdict(
        reading,
        account_share_updates=account_share_updates,
        recognised_switches=switches,
    )


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
    unresolved = coerce.as_count(gate.get("unresolved_switches"))
    known = len(gate.get("recognised_switches") or [])
    code = gate.get("refused_condition")
    if gate.get("condition_1") == "dialog_control_off":
        return "CONFIRMED OFF: a control named for notifying the network was read unchecked in the edit dialog."
    if gate.get("condition_1") == "account_setting_off":
        return (
            "CONFIRMED OFF AT THE ACCOUNT: no control in the edit dialog is named "
            "for notifying the network, "
            + (
                f"its {known} unnamed switch(es) are the ones a capture identified, "
                "recognised by structure, "
                if known
                else "none is unnamed, "
            )
            + "and his account-level 'Share profile updates with your network' "
            "setting was read OFF before the edit."
        )
    if code == "5_condition_1_not_established":
        return (
            "NOT ESTABLISHED -- NEEDS-OPERATOR: no control in the edit dialog is "
            "named for notifying the network, and his account-level setting was "
            "not read OFF before the edit"
            + (
                f"; {unresolved} checkable control(s) in the dialog carry no name "
                "and no capture identifies them, and either could be it"
                if unresolved
                else ""
            )
            + ". Save was not pressed."
        )
    if code == "6_unnamed_switch_unresolved":
        return (
            "NOT ESTABLISHED -- NEEDS-OPERATOR: his account-level setting was read "
            f"OFF, but {unresolved} checkable control(s) in the dialog carry no name "
            "and no capture identifies them, and either could be a per-edit notify "
            "control. Save was not pressed."
        )
    if state in ("on", "unknown", "ambiguous"):
        return f"REFUSED ON IT: the notify-network reading was {state!r}, so Save was not pressed."
    return (
        "not reached: the gate refused before condition 1 was read "
        f"({code!r}), so nothing was pressed."
    )
