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
  :data:`ACCOUNT_READINGS`. Its reader, :func:`read_account_share_updates`,
  exists since 2026-09-27 and ``writes.perform`` takes its reading before the
  editor is opened; anything but OFF refuses there
  (``5_condition_1_not_established``, NEEDS-OPERATOR). Until 2026-09-27 no
  reader existed and the gate refused there always.
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
from urllib.parse import urlsplit

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
#: closed dialog's leftover button cannot be the one pressed. The strict half
#: is TRUE SINCE LANE L5'S MERGE OF MASTER 52b55b6 (2026-09-27), when
#: ``perform`` began pressing ``update_profile_field`` strictly
#: (``writes.STRICT_PRESS_ACTIONS``); until then the press passed no
#: ``strict=``.
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

#: THE SEAM FOR THE AMENDED CONDITION 1 -- BUILT UNWIRED 2026-09-24 (lane L7),
#: WIRED 2026-09-27 (the live lane).
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
#: SUPPLIED SINCE 2026-09-27: ``writes.perform`` loads the setting's page
#: (:data:`ACCOUNT_SETTING_URL`) BEFORE the editor, reads it with
#: :func:`read_account_share_updates`, and passes the answer to every
#: :func:`read_save_gate` call it makes -- ``None`` when the page could not be
#: read at all. It was NOT SUPPLIED until then, and the gate pressed only on
#: a dialog control read off. No rule in this module moved when it was wired;
#: only the input arrived.
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

#: A SETTING BLOCK'S SHAPE, wherever it sits: exactly two parts, the first
#: holding a paragraph and no control. Shared by the recognition's blocks and
#: the Premium badge's (:data:`PREMIUM_BADGE_ROW_BLOCKS`), so the two cannot
#: come apart.
_INTRO_BLOCK_SHAPE: str = (
    ":has(> div:first-child + div:last-child)"
    ":has(> div:first-child p)"
    ":not(:has(> div:first-child :is(input, button, select, textarea, a[href], [role])))"
)

#: THE ENUMERATED SHAPES, one setting block per identity in the recorded order:
#: the row's second element child is ``INTRO_SWITCH_IDENTITIES[0]``, its third
#: is ``[1]``. Each is exactly two parts, the first holding a paragraph and no
#: control. Exact membership, as in ``press.SANCTIONED_SHAPES``: each shape
#: must match exactly one element, or nothing is recognised.
INTRO_SWITCH_BLOCKS: tuple[str, ...] = tuple(
    INTRO_SWITCH_ROW + " > div:nth-child(" + str(position) + ")" + _INTRO_BLOCK_SHAPE
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
    require_save: bool = True,
) -> dict[str, Any]:
    """Decide the ``Save`` press from one reading of the editor container.

    PURE, so every refusal is testable without a browser. ``reading`` is what
    ``dom.read_self_owned_editor_fields`` returned (no dom ids -- this decides
    whether to press, it does not aim by id). ``account_share_updates`` is the
    seam described at :data:`ACCOUNT_READINGS`; ``writes.perform`` passes its
    reading since 2026-09-27.
    ``recognised_switches`` is :func:`recognise_intro_editor_switches`'s reading;
    absent, no switch is recognised. ``require_save=False`` is the reading
    taken BEFORE a switch is pressed: a switch may store itself the moment
    it is pressed, so condition 1 cannot wait for Save -- conditions 1 and 2
    (the Save control) are skipped and every notify condition is kept.
    Returns the gate block ``writes.perform`` reports:

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

    if require_save and len(saves) != 1:
        out["refused_condition"] = "1_save_not_exactly_one"
        out["why"] = (
            f"{len(saves)} controls in the editor are named "
            f"{SAVE_CONTROL_NAME!r}, where exactly one is required. Pressing "
            "one of several would be pressing by position. Nothing was saved."
        )
        return out
    if require_save and saves[0].get("disabled") is True:
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
                None: "was not read before the edit (the reading could not be taken)",
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
        if require_save
        else "condition 1 is established because "
        + basis
        + ". Read BEFORE the switch is pressed, because a switch may store "
        "itself when pressed; the Save control is checked when it is about to "
        "be pressed."
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


async def _read_switch_block(
    dialog: Any, block: str, unnamed_switch: Any
) -> tuple[bool, Optional[bool]]:
    """One setting block's switch: ``(in the recorded shape, checked state)``.

    In the recorded shape means: the block holds exactly one checkbox, its
    part holds exactly one ``role=switch`` + ``aria-checked`` wrapper, the
    wrapper holds the recorded unnamed switch by its attributes, and that
    switch has no accessible name by Playwright's own computation. The state
    is None where the checkbox and its wrapper disagree. Counts only; the
    caller catches.
    """
    wrapper = block + _INTRO_WRAPPER_PATH
    switch = wrapper + _INTRO_SWITCH_INPUT
    held = await dialog.locator("css=" + block + ' input[type="checkbox"]').count()
    wrappers = await dialog.locator("css=" + wrapper).count()
    shaped = await dialog.locator("css=" + switch).count()
    unnamed = await dialog.locator("css=" + switch).and_(unnamed_switch).count()
    if any(coerce.as_count(n) != 1 for n in (held, wrappers, shaped, unnamed)):
        return (False, None)
    on = coerce.as_count(await dialog.locator("css=" + switch + ":checked").count())
    wrapper_on = coerce.as_count(
        await dialog.locator("css=" + wrapper + '[aria-checked="true"]').count()
    )
    return (True, (on == 1) if (on == 1) == (wrapper_on == 1) else None)


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
            in_shape, state = await _read_switch_block(dialog, block, unnamed_switch)
            if not in_shape:
                return out
            states.append(state)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
        return out
    out["recognised"] = len(INTRO_SWITCH_IDENTITIES)
    out["identities"] = list(INTRO_SWITCH_IDENTITIES)
    out["checked"] = states
    return out


#: THE PREMIUM BADGE'S AIM -- P B9, built 2026-09-24 (lane L7) on the
#: orchestrator's ruling of 09:15, relayed by the coordinator's order. The
#: switch's block title is a LinkedIn UI string, not his data, and it may aim
#: the press when ALL of these hold; each is held here or in ``writes``:
#:
#: 1. IT IS COMPARED INSIDE THE PAGE. It rides in a selector the page's own
#:    engine evaluates (``:text-is``: exact, case-sensitive, whitespace
#:    collapsed), and what comes back is a count. No text is read out or
#:    returned.
#: 2. IT MATCHES EXACTLY ONE SETTINGS ROW in the intro editor's column, or the
#:    write refuses (:func:`read_premium_badge`).
#: 3. A NON-ENGLISH UI REFUSES, because the string will not match: the count
#:    is 0 and the refusal is the same one. Fail-closed BY CONSTRUCTION, not
#:    by a language check that could itself be wrong.
#: 4. A BEFORE/AFTER READING PROVES THAT ONLY THAT SWITCH CHANGED, and that
#:    the other switch in its row -- Open Profile, row ``P B10``, by the
#:    capture -- did not: in the dialog after the press and before Save
#:    (:func:`badge_moved_alone`), and on a fresh render after the write
#:    (:func:`badge_verification`).
#: 5. THE RESTORE IS THE SAME WRITE WITH THE OTHER VALUE, checked the same
#:    way.
#:
#: ONE STRING, written here and never composed from a caller's input. The
#: write is ``update_profile_field`` with this title as its ``field``: the
#: family's grant, off by default, its preview and token, and its restore
#: block.
PREMIUM_BADGE_TITLE: str = "Profile Premium Badge"

#: The two values the write takes, and the checked state each means. ``on`` is
#: the badge SHOWN: on the one render on record the switch reads checked and
#: his profile draws the Premium icon. DERIVED from that render, not from a
#: press, which is why the verification compares STATES and never meanings.
PREMIUM_BADGE_STATES: dict[str, bool] = {"on": True, "off": False}

#: The title paragraph, compared in the page. The constant carries no quote or
#: backslash, so it cannot end the selector's own quoting.
_BADGE_TITLE_P: str = 'p:text-is("' + PREMIUM_BADGE_TITLE + '")'

#: Any row directly under the column carrying the title ANYWHERE in it, of any
#: shape. Condition 2 is counted over this: a second row carrying it, in
#: whatever shape, makes the aim ambiguous.
PREMIUM_BADGE_ANY_ROW: str = INTRO_SWITCH_COLUMN + " > div:has(" + _BADGE_TITLE_P + ")"

#: The recorded-shape row one of whose blocks carries the title in its text
#: part. One ``:has()`` with a relative path, never nested.
PREMIUM_BADGE_ROW: str = (
    INTRO_SWITCH_ROW + ":has(> div > div:first-child " + _BADGE_TITLE_P + ")"
)

#: The two blocks of THAT row, by position, in the recorded shape.
PREMIUM_BADGE_ROW_BLOCKS: tuple[str, ...] = tuple(
    PREMIUM_BADGE_ROW + " > div:nth-child(" + str(position) + ")" + _INTRO_BLOCK_SHAPE
    for position in (2, 3)
)

#: A block whose text part carries the title.
_BADGE_TITLED: str = ":has(> div:first-child " + _BADGE_TITLE_P + ")"

#: Why the badge cannot be aimed, by code. Built from constants only.
PREMIUM_BADGE_REFUSALS: dict[str, str] = {
    "0_editor_not_found": (
        "the intro editor's dialog -- the one holding the one Save control -- "
        "was not found exactly once."
    ),
    "1_title_not_drawn": (
        "no settings row in the editor's column carries the title "
        + repr(PREMIUM_BADGE_TITLE)
        + ". A UI in another language lands here by construction: the English "
        "string matches nothing, so nothing is aimed."
    ),
    "2_title_in_more_than_one_row": (
        "more than one row in the editor's column carries the title "
        + repr(PREMIUM_BADGE_TITLE)
        + ", and pressing one of several would be choosing by position."
    ),
    "3_not_the_recorded_row": (
        "the row carrying the title is not the recorded settings row -- a "
        "leading paragraph and exactly two setting blocks."
    ),
    "4_title_not_on_exactly_one_block": (
        "the title is not on exactly one of the row's two setting blocks."
    ),
    "5_switch_not_the_recorded_shape": (
        "a switch in the row is not in the recorded shape: one unnamed "
        "checkbox switch, in a wrapper carrying role=switch and aria-checked."
    ),
    "6_state_unreadable": (
        "a switch's checkbox and its aria-checked wrapper disagree, so its "
        "state cannot be read."
    ),
    "7_reading_failed": "the reading itself failed; only its exception type is kept.",
}


def _badge_refusal(out: dict[str, Any], code: str) -> dict[str, Any]:
    out["aimable"] = False
    out["refused"] = code
    out["why"] = (
        "the Premium badge switch was not aimed because "
        + PREMIUM_BADGE_REFUSALS[code]
        + " Nothing was pressed."
    )
    return out


async def read_premium_badge(page: Any) -> dict[str, Any]:
    """Find the Premium badge switch BY ITS TITLE, compared in the page. Never raises.

    Every question is a ``locator(...).count()``, so the page runs nothing it
    did not already run and what comes back is integers. Returns:

        aimable            True only when every check below holds
        refused / why      a code from :data:`PREMIUM_BADGE_REFUSALS`, and its
                           sentence -- constants and counts, never page text
        containers         dialogs holding the one Save control (1 required)
        rows_titled        column rows carrying the title anywhere (1 required)
        recorded_rows_titled  recorded-shape rows carrying it (1 required)
        badge_position     1 or 2: the badge block's order in its row
        badge_checked / other_checked   the two switches' states
        selector           the press, when aimable: the wrapper of the titled
                           block, at that position, in the titled row, in the
                           dialog -- so the click itself re-checks the title
        error              an exception's TYPE if the reading failed

    THE OTHER SWITCH is the row's other setting block. The capture identifies
    it as Open Profile; it is read here BY STRUCTURE only, so that condition 4
    of the ruling can prove it did not move.
    """
    out: dict[str, Any] = {
        "aimable": False,
        "refused": None,
        "why": "",
        "containers": 0,
        "rows_titled": 0,
        "recorded_rows_titled": 0,
        "badge_position": None,
        "badge_checked": None,
        "other_checked": None,
        "selector": "",
        "error": None,
    }
    try:
        dialog = page.locator(_EDITOR_DIALOG, has=page.locator(_SAVE_CONTROL))
        out["containers"] = coerce.as_count(await dialog.count())
        if out["containers"] != 1:
            return _badge_refusal(out, "0_editor_not_found")
        out["rows_titled"] = coerce.as_count(
            await dialog.locator("css=" + PREMIUM_BADGE_ANY_ROW).count()
        )
        if out["rows_titled"] == 0:
            return _badge_refusal(out, "1_title_not_drawn")
        if out["rows_titled"] > 1:
            return _badge_refusal(out, "2_title_in_more_than_one_row")
        out["recorded_rows_titled"] = coerce.as_count(
            await dialog.locator("css=" + PREMIUM_BADGE_ROW).count()
        )
        if out["recorded_rows_titled"] != 1:
            return _badge_refusal(out, "3_not_the_recorded_row")
        titled = [
            coerce.as_count(await dialog.locator("css=" + block + _BADGE_TITLED).count())
            for block in PREMIUM_BADGE_ROW_BLOCKS
        ]
        if sorted(titled) != [0, 1]:
            return _badge_refusal(out, "4_title_not_on_exactly_one_block")
        badge = titled.index(1)
        unnamed_switch = dialog.get_by_role(
            "switch", name="", exact=True, include_hidden=True
        )
        badge_ok, badge_checked = await _read_switch_block(
            dialog, PREMIUM_BADGE_ROW_BLOCKS[badge], unnamed_switch
        )
        other_ok, other_checked = await _read_switch_block(
            dialog, PREMIUM_BADGE_ROW_BLOCKS[1 - badge], unnamed_switch
        )
        if not (badge_ok and other_ok):
            return _badge_refusal(out, "5_switch_not_the_recorded_shape")
        out["badge_position"] = badge + 1
        out["badge_checked"] = badge_checked
        out["other_checked"] = other_checked
        if badge_checked is None or other_checked is None:
            return _badge_refusal(out, "6_state_unreadable")
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
        return _badge_refusal(out, "7_reading_failed")
    out["aimable"] = True
    out["selector"] = (
        _EDITOR_DIALOG
        + " >> css="
        + PREMIUM_BADGE_ROW_BLOCKS[badge]
        + _BADGE_TITLED
        + _INTRO_WRAPPER_PATH
    )
    out["why"] = (
        "exactly one settings row in the editor's column carries the title "
        + repr(PREMIUM_BADGE_TITLE)
        + ", compared in the page; it is the recorded row, the title is on its "
        + ("first" if badge == 0 else "second")
        + " setting block, and both of the row's switches are in the recorded "
        "shape with readable states."
    )
    return out


def premium_badge_value(reading: Optional[dict[str, Any]]) -> tuple[Optional[str], str]:
    """The badge's state as the write names it, ``'on'`` or ``'off'`` -- or None.

    None means it could not be read, never that it was off.
    """
    reading = reading or {}
    if not reading.get("aimable"):
        return (None, str(reading.get("why") or "the badge switch was not read."))
    checked = reading.get("badge_checked")
    for value, state in PREMIUM_BADGE_STATES.items():
        if checked is state:
            return (
                value,
                "read live from the editor before the write, off the switch "
                "whose block carries the title, compared in the page.",
            )
    return (None, "the badge switch's state could not be read.")


def premium_badge_aim(reading: Optional[dict[str, Any]], value: str) -> dict[str, Any]:
    """Gate 5 for the badge: whether, and where, to press. PURE.

    Refuses a value outside :data:`PREMIUM_BADGE_STATES`, a reading that is
    not aimable, and a badge already in the requested state -- pressing that
    one would switch it the OTHER way.
    """
    out: dict[str, Any] = {"proceed": False, "selector": "", "why": ""}
    if value not in PREMIUM_BADGE_STATES:
        out["why"] = (
            "the Premium badge switch takes 'on' or 'off', and "
            + repr(value)
            + " is neither."
        )
        return out
    reading = reading or {}
    if not reading.get("aimable"):
        out["why"] = str(reading.get("why") or "the badge switch was not read.")
        return out
    if reading.get("badge_checked") is PREMIUM_BADGE_STATES[value]:
        out["why"] = (
            "the Premium badge switch is already "
            + repr(value)
            + ". Pressing it would switch it the other way, so nothing is pressed."
        )
        return out
    out["proceed"] = True
    out["selector"] = str(reading.get("selector") or "")
    out["why"] = str(reading.get("why") or "")
    return out


def badge_moved_alone(
    before: Optional[dict[str, Any]], after: Optional[dict[str, Any]], value: str
) -> dict[str, Any]:
    """In the dialog, after the press and BEFORE Save: did the badge -- and only
    the badge -- move? PURE. Save is pressed only on ``proceed``; otherwise the
    change sits unsaved and the verification's fresh navigation discards it.
    """
    out: dict[str, Any] = {"proceed": False, "code": None, "why": ""}
    before = before or {}
    after = after or {}
    if not (before.get("aimable") and after.get("aimable")):
        out["code"] = "unreadable"
        out["why"] = "the switches could not be read before and after the press."
        return out
    if after.get("badge_position") != before.get("badge_position"):
        out["code"] = "the_row_changed"
        out["why"] = "the badge's block moved within its row between the two readings."
        return out
    if after.get("other_checked") is not before.get("other_checked"):
        out["code"] = "the_other_switch_moved"
        out["why"] = (
            "THE OTHER SWITCH IN THE ROW MOVED -- Open Profile, by the capture. "
            "Save was not pressed, so nothing the dialog holds is stored by this "
            "write; if the switch stores itself when pressed, check Open "
            "Profile by hand."
        )
        return out
    if after.get("badge_checked") is not PREMIUM_BADGE_STATES.get(value):
        out["code"] = "the_badge_did_not_move"
        out["why"] = "the badge switch did not reach the requested state; Save was not pressed."
        return out
    out["proceed"] = True
    out["why"] = "the badge switch moved to the requested state and the other switch did not."
    return out


def badge_verification(
    before: Optional[dict[str, Any]], after: Optional[dict[str, Any]], value: str
) -> tuple[Optional[str], str]:
    """On a FRESH RENDER after the write: ``field_changed`` when the badge holds
    the requested state and the other switch holds its own before-state,
    ``value_unchanged`` when neither moved, and None -- unknown -- otherwise.
    PURE.
    """
    before = before or {}
    after = after or {}
    if not (before.get("aimable") and after.get("aimable")):
        return (
            None,
            "the switches could not be read on the fresh render: "
            + str(after.get("why") or ""),
        )
    if after.get("other_checked") is not before.get("other_checked"):
        return (
            None,
            "THE OTHER SWITCH IN THE ROW -- Open Profile, by the capture -- no "
            "longer holds the state it held before this write. Check it by hand.",
        )
    if after.get("badge_checked") is PREMIUM_BADGE_STATES.get(value):
        return (
            "field_changed",
            "the badge switch reads the requested state on a fresh render, and "
            "the other switch is unchanged.",
        )
    if after.get("badge_checked") is before.get("badge_checked"):
        return (
            "value_unchanged",
            "neither switch moved: the badge reads what it read before this write.",
        )
    return (None, "the badge switch reads neither the requested state nor its previous one.")


async def read_save_gate(
    page: Any,
    *,
    account_share_updates: Optional[str] = None,
    require_save: bool = True,
) -> dict[str, Any]:
    """Read the open editor and decide the press. Never raises.

    A reader failure is a refusal carrying the exception's TYPE and nothing
    else: a Playwright message can quote a selector, and through it page
    content, while a class name cannot. ``account_share_updates`` is passed
    through to :func:`save_gate_verdict` unchanged; see :data:`ACCOUNT_READINGS`
    for where ``writes.perform`` takes it.
    """
    try:
        reading = await dom.read_self_owned_editor_fields(page)
    except Exception as exc:  # noqa: BLE001 - reported as a refusal
        verdict = save_gate_verdict(
            {"refused": type(exc).__name__},
            account_share_updates=account_share_updates,
            require_save=require_save,
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
        require_save=require_save,
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


#: HOW LONG AN EDITOR WRITE WAITS FOR ITS DIALOG TO BE DRAWN: this many polls,
#: this far apart -- 10 s. A LIVENESS BOUND, NOT A SAFETY ONE. MEASURED LIVE
#: 2026-09-28 (the live lane's session 4): P B9's write loaded his intro editor
#: and its gate read the dialog the moment the address loaded -- refused,
#: ``0_editor_not_found``, nothing pressed -- while another load of the same
#: address found the dialog already drawn when the navigation returned. So
#: LinkedIn draws the dialog on its own schedule, and a reader that looks at
#: once can lose the race (``_audit/2026-09-23-live-lane-session-1.md``,
#: "Live session 4").
EDITOR_DIALOG_POLLS: int = 50
EDITOR_DIALOG_POLL_MS: int = 200


async def wait_for_editor_dialog(
    page: Any,
    *,
    polls: Optional[int] = None,
    poll_ms: Optional[int] = None,
) -> dict[str, Any]:
    """After a navigation to the intro editor's own address: poll, BOUNDED,
    until exactly one dialog holding the one Save control is drawn.

    Returns ``drawn`` (True / False / None), the ``polls`` taken and the last
    count of such ``dialogs``. ``None`` means the reading itself failed, which
    is not the same answer as "not drawn". IT DECIDES NOTHING: every gate after
    it reads the page for itself and refuses on what it finds, so a dialog
    never drawn -- or drawn twice -- refuses exactly as it did before this wait
    existed; the wait only bounds how long a reader looks before it reads.
    Taken by ``writes.perform`` after the editor's landing and before its gate
    reads the control, and by the fresh-render verification before it reads
    the stored value. Counts only; nothing is pressed.
    """
    total = coerce.as_count(EDITOR_DIALOG_POLLS if polls is None else polls)
    gap = coerce.as_count(EDITOR_DIALOG_POLL_MS if poll_ms is None else poll_ms)
    taken = 0
    drawn = 0
    for index in range(max(1, total)):
        taken += 1
        try:
            drawn = coerce.as_count(
                await page.locator(_EDITOR_DIALOG, has=page.locator(_SAVE_CONTROL)).count()
            )
        except Exception:  # noqa: BLE001 - a measurement, not a gate
            return {"drawn": None, "polls": taken, "dialogs": None}
        if drawn == 1:
            return {"drawn": True, "polls": taken, "dialogs": 1}
        if index + 1 < max(1, total):
            await page.wait_for_timeout(gap)
    return {"drawn": False, "polls": taken, "dialogs": drawn}


#: HOW LONG AN EDITOR WRITE WAITS, AFTER ITS PRESS, FOR THE CONTROL TO READ THE
#: REQUESTED STATE: this many polls, this far apart -- 5 s. A LIVENESS BOUND,
#: NOT A SAFETY ONE. MEASURED LIVE 2026-09-28 (the live lane's session 5): P
#: B9's restore pressed the badge switch once and the read taken straight after
#: the press still showed the old state -- so Save was not pressed and the
#: badge was left hidden -- while the same press about two minutes later
#: flipped it in the read (``_audit/2026-09-23-live-lane-session-1.md``, "Live
#: session 5").
PRESS_STATE_POLLS: int = 25
PRESS_STATE_POLL_MS: int = 200


async def wait_for_state(
    page: Any,
    read: Any,
    reached: Any,
    *,
    polls: Optional[int] = None,
    poll_ms: Optional[int] = None,
) -> tuple[Any, dict[str, Any]]:
    """After an editor press: call ``read()`` again, BOUNDED, until
    ``reached(reading)`` holds. Returns ``(the last reading, {"reached",
    "polls"})``.

    IT DECIDES NOTHING. The caller asks its own question of the last reading
    -- ``badge_moved_alone`` on the switch path, ``only_the_field_moved`` on
    the select path -- exactly as it did of the one reading it took before
    this wait existed; the wait only bounds how long the control is given to
    answer the press. A ``reached`` that raises counts as not reached.
    """
    total = max(1, coerce.as_count(PRESS_STATE_POLLS if polls is None else polls))
    gap = coerce.as_count(PRESS_STATE_POLL_MS if poll_ms is None else poll_ms)
    reading: Any = None
    for index in range(total):
        reading = await read()
        try:
            done = bool(reached(reading))
        except Exception:  # noqa: BLE001 - a reading that cannot be judged has not reached it
            done = False
        if done:
            return reading, {"reached": True, "polls": index + 1}
        if index + 1 < total:
            await page.wait_for_timeout(gap)
    return reading, {"reached": False, "polls": total}


def badge_reads(reading: Optional[dict[str, Any]], value: str) -> bool:
    """Whether a badge reading is aimable and reads ``value``. PURE."""
    reading = reading or {}
    want = PREMIUM_BADGE_STATES.get(value)
    return bool(reading.get("aimable")) and want is not None and reading.get("badge_checked") is want


def _field_values(reading: Optional[dict[str, Any]], field: str) -> list[str]:
    records = (reading or {}).get("fields") or []
    return [str(r.get("value")) for r in records
            if str(r.get("name") or "") == field and r.get("value") is not None]


def field_reads(reading: Optional[dict[str, Any]], field: str, requested: str) -> bool:
    """Whether exactly one value-bearing control named ``field`` reads
    ``requested``, in an editor values reading. PURE."""
    values = _field_values(reading, field)
    return len(values) == 1 and values[0] == requested


def only_the_field_moved(
    before: Optional[dict[str, Any]],
    after: Optional[dict[str, Any]],
    field: str,
    requested: str,
) -> dict[str, Any]:
    """In the dialog, after the change and BEFORE Save: did ``field`` -- and
    only ``field`` -- move? PURE. Save is pressed only on ``proceed``;
    otherwise the change sits unsaved and the verification's fresh navigation
    discards it (2026-09-28, the live lane's session 5).

    ``before`` and ``after`` are editor VALUES readings. Every value-bearing
    control other than ``field`` must read, as a multiset of (name, value),
    exactly what it read before, and exactly one control named ``field`` must
    read ``requested``. A control carrying no value (a button, a switch) is
    not compared: its state is not a value, and the switch path has its own
    rule.
    """
    out: dict[str, Any] = {"proceed": False, "code": None, "why": ""}
    if not isinstance(before, dict) or not isinstance(after, dict) or "fields" not in before \
            or "fields" not in after:
        out["code"] = "unreadable"
        out["why"] = "the editor's values could not be read before and after the change; Save was not pressed."
        return out

    def others(reading: dict[str, Any]) -> list[tuple[str, str]]:
        return sorted(
            (str(r.get("name") or ""), str(r.get("value")))
            for r in reading["fields"]
            if r.get("value") is not None and str(r.get("name") or "") != field
        )

    values = _field_values(after, field)
    if len(values) != 1:
        out["code"] = "not_one_field"
        out["why"] = (str(len(values)) + " value-bearing control(s) carry the field's name after the "
                      "change, where exactly one is required; Save was not pressed.")
        return out
    if values[0] != requested:
        out["code"] = "the_field_did_not_move"
        out["why"] = "the field does not read the requested value after the change; Save was not pressed."
        return out
    if others(before) != others(after):
        out["code"] = "another_field_moved"
        out["why"] = ("ANOTHER FIELD'S VALUE CHANGED beside the one asked for; Save was not pressed, "
                      "so nothing the dialog holds is stored by this write.")
        return out
    out["proceed"] = True
    out["why"] = "the field reads the requested value and no other field moved."
    return out


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


#: HIS ACCOUNT-LEVEL SETTING'S PAGE -- THE READER BEHIND THE SEAM ABOVE
#: (2026-09-27, the live lane, session-2 preparation item (b)).
#:
#: The address is admitted for READING ONLY, on the orchestrator's
#: application of ONE-NAMED-SETTINGS-PAGE-AT-A-TIME (see its line in
#: ``readonly._ALLOWED_URL_PATTERNS``). ``writes.perform`` loads it for an
#: editor write BEFORE the editor -- so before the change is entered, the
#: amendment's word -- and hands :func:`read_account_share_updates`' answer
#: to :func:`read_save_gate` as ``account_share_updates``. It decides nothing
#: by itself: the save gate decides, with it.
ACCOUNT_SETTING_URL: str = (
    "https://www.linkedin.com/mypreferences/d/settings/notify-network-for-updates"
)

#: THE SWITCH'S OWN ACCESSIBLE NAME ON THE SETTING'S PAGE, measured live by the
#: live lane on 2026-09-28: an ``input`` checkbox with role switch, named
#: through ``aria-labelledby`` by a label reading "Share key profile updates",
#: under the page heading "Share profile updates". The first value here was
#: "Sharing profile edits" -- the settings INDEX's display name for the key
#: ``notifyNetworkForUpdates``, captured in session 1 -- and the page itself
#: draws no control of that name: session 2's live read found 0 and read
#: nothing. A LinkedIn UI string, never his data, and it is COMPARED INSIDE THE
#: PAGE -- Playwright's role-and-name engine, exact -- so what comes back is a
#: count, never text: the discipline :data:`PREMIUM_BADGE_TITLE` set. A UI in
#: another language matches nothing, and nothing is read: 'unknown', by
#: construction. Held on today's capture of the page by
#: ``tests/test_account_share_updates.py``.
ACCOUNT_SETTING_NAME: str = "Share key profile updates"

#: The roles a control holding this setting's on/off state can carry. Both
#: are asked, and exactly ONE control of either, of this exact name, may be
#: drawn: a second is ambiguity, and ambiguity reads 'unknown'.
_ACCOUNT_SETTING_ROLES: tuple[str, ...] = ("switch", "checkbox")


def served_at_account_setting(landed: Optional[str]) -> bool:
    """Did the page keep its own address? PURE.

    AN ADMITTED ADDRESS IS NOT A SERVED ONE. The address is derived, never seen
    drawn; if LinkedIn redirects it -- to the other candidate, to the category
    page that lists this setting among others -- the page read is not the one
    admitted, and the reading does not count (``writes.perform`` makes it
    'unknown'). The PATH is compared, host fixed, trailing slash and query
    ignored: a tracking parameter on a served page is the same page.
    """
    if not landed:
        return False
    parts = urlsplit(str(landed).strip())
    want = urlsplit(ACCOUNT_SETTING_URL)
    return (
        parts.scheme == want.scheme
        and parts.netloc == want.netloc
        and parts.path.rstrip("/") == want.path.rstrip("/")
    )


async def read_account_share_updates(page: Any) -> dict[str, Any]:
    """Read his "Share key profile updates" switch. READ ONLY, and never raises.

    ONE CONTROL, ITS NAME BY EXACT EQUALITY, ITS STATE FROM ``checked``. Every
    question is a ``count()``: the page runs nothing it did not already run,
    and what comes back is integers. Returns:

        reading    one of :data:`ACCOUNT_READINGS` -- 'off' | 'on' | 'unknown'
        named      controls of role switch or checkbox whose accessible name
                   is exactly :data:`ACCOUNT_SETTING_NAME` (1 required)
        input      1 when that control is an ``input[type=checkbox]``
        aria       'true' | 'false' | None -- its ``aria-checked``
        why        built from constants and counts, never page text
        error      an exception's TYPE if the reading failed

    THE STATE: an ``input[type=checkbox]`` answers through the browser's own
    ``checked`` PROPERTY (the ``:checked`` pseudo-class), and if it also
    carries ``aria-checked`` the two must agree; any other control answers
    through ``aria-checked`` alone, and one with neither holds no state this
    reader can read. EVERY DOUBT IS 'unknown' AND 'unknown' IS NEVER 'off':
    no control of that name, two of them, a name that only contains it, a
    disagreement, no state, a failure.

    IT PRESSES NOTHING. The setting is his; condition 1 asks for OFF to be
    READ, never made so. Turning it off is a settings write, and since
    2026-10-10 one exists -- ``linkedin_set_admitted_setting`` (lane S,
    HIS-OWN-SETTINGS-NOT-OUTWARD), behind its own single-use grant, never
    called from here and never by an editor write.
    """
    out: dict[str, Any] = {
        "reading": "unknown",
        "named": 0,
        "input": None,
        "aria": None,
        "why": "",
        "error": None,
    }
    try:
        named = page.get_by_role(
            _ACCOUNT_SETTING_ROLES[0],
            name=ACCOUNT_SETTING_NAME,
            exact=True,
            include_hidden=True,
        ).or_(
            page.get_by_role(
                _ACCOUNT_SETTING_ROLES[1],
                name=ACCOUNT_SETTING_NAME,
                exact=True,
                include_hidden=True,
            )
        )
        out["named"] = coerce.as_count(await named.count())
        if out["named"] != 1:
            out["why"] = (
                f"{out['named']} controls of role switch or checkbox are named "
                f"exactly {ACCOUNT_SETTING_NAME!r} on the page, where exactly "
                "one is required; the setting is not read."
            )
            return out
        out["input"] = coerce.as_count(
            await named.and_(page.locator('input[type="checkbox"]')).count()
        )
        aria_on = coerce.as_count(
            await named.and_(page.locator('[aria-checked="true"]')).count()
        )
        aria_off = coerce.as_count(
            await named.and_(page.locator('[aria-checked="false"]')).count()
        )
        aria: Optional[bool] = True if aria_on == 1 else (False if aria_off == 1 else None)
        out["aria"] = None if aria is None else ("true" if aria else "false")
        if out["input"] == 1:
            checked = (
                coerce.as_count(await named.and_(page.locator(":checked")).count()) == 1
            )
            if aria is not None and aria is not checked:
                out["why"] = (
                    "the switch's checked property and its aria-checked "
                    "disagree, so its state is not read."
                )
                return out
            state = checked
        elif aria is None:
            out["why"] = (
                "the control of that name is not a checkbox and carries no "
                "aria-checked, so it holds no state this reader can read."
            )
            return out
        else:
            state = aria
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
        out["why"] = "the reading itself failed; only its exception type is kept."
        return out
    out["reading"] = "on" if state else "off"
    out["why"] = (
        f"exactly one control is named {ACCOUNT_SETTING_NAME!r}, and it reads "
        + ("ON." if state else "OFF.")
    )
    return out
