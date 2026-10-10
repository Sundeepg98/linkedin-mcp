"""ONE admitted settings page, ONE control on it, changed behind the grant.

Lane S (settings), 2026-10-10, applying ``HIS-OWN-SETTINGS-NOT-OUTWARD``
(the orchestrator, 2026-09-28, ``_audit/2026-09-28-rulings-build-classes.md``
section 2): a setting of his own account is not an outward act; it is built
behind the single-use grant and live-proven read, benign value, read back,
restore the exact original, read back -- one setting at a time, and any failed
restore is STOP-ALL.

WHAT THIS MODULE IS. The verdicts and the readers for the generic settings
writer ``linkedin_set_admitted_setting`` (action :data:`ACTION`). It presses
NOTHING: ``readonly.SANCTIONED_MUTATIONS`` grants a press to
``writes.perform`` alone, so ``perform`` drains this writer's press through
its one click site (or its one ``select_option`` site), and asks this module
three questions around it -- what the control reads, did ONLY that control
move, and is there a Save to press. Every reader here answers in COUNTS and
booleans through Playwright's role engine; no page text is returned, and the
one value a select holds is compared in this process and never put on a
receipt.

THE ADMISSION RULE, AND WHY THE REGISTRY HOLDS ONE PAGE.
``ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`` (the operator, 2026-08-31): *"ONE NAMED
settings page below /mypreferences/d/ is admitted, one at a time"*, and
``MESSAGING-SETTINGS-CAPABILITY-LEVEL`` makes that capability-level: a setting
is admitted BY NAME or not at all, whatever its address. So a page enters
:data:`ADMITTED_PAGES` only by its NAME -- the heading LinkedIn draws on it --
with every control on it described from a REAL capture of that page, never
from a help article or a guess. Today one page qualifies: "Share profile
updates", whose capture (the live lane's session 2, 2026-09-28) is the tracked
skeleton ``tests/fixtures/live2/setting.html``, and whose address the read
boundary already admits for reading by the same ruling's application. Every
other settings row waits on its page's capture; ``_audit/2026-09-28-lane-s-
settings.md`` holds the capture queue.

WHAT THE WRITER REFUSES, BY NAME. Only three kinds of control hold a value
this writer can set and read back exactly: a SWITCH, a RADIO GROUP and a
SELECT (:data:`CONTROL_KINDS`). A typed field, an autocomplete, a button, a
link and a file input are refused by name (:data:`REFUSED_KINDS`) -- a page
carrying one is not admitted for it.

THE EXCLUSIONS THE RULING NAMES ARE CARRIED, NOT DROPPED. A control records
whether its live proof is permitted (:data:`LIVE_PROOF_ALLOWED`) or which
exclusion holds it -- credential settings, a setting that cannot be put back
exactly, a sensitive personal attribute -- and the preview prints that class
and its reason. The writer itself is the same for all of them: the ruling says
they are BUILT, and never live-proven unless he names them.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import coerce, profile_editor
from linkedin_server.dom import _SELECTOR_UNSAFE, settings_radio_label_selector
from linkedin_server.errors import WriteAttemptError

#: The action this module serves, its tool, and the ruling it rests on.
ACTION = "set_admitted_setting"
TOOL_NAME = "linkedin_set_admitted_setting"
RULING = "HIS-OWN-SETTINGS-NOT-OUTWARD"

#: The ``WriteSpec.state_from`` that routes ``writes.observe`` here.
STATE_FROM = "admitted_settings_page"

#: How the page and the control are joined inside the target's SETTING half.
#: The whole target is ``<page> / <control> :: <value>``; ``writes.TARGET_JOIN``
#: separates the value, and this separates the two names. A name containing it
#: is refused, for the reason a component containing ``TARGET_JOIN`` is: two
#: different targets must never canonicalise to one string.
SETTING_JOIN = " / "

#: The three control kinds this writer may set. Each holds ONE value the page
#: reads back exactly, which is what the restore step of the ruling needs.
SWITCH = "switch"
RADIO_GROUP = "radio_group"
SELECT = "select"
CONTROL_KINDS: tuple[str, ...] = (SWITCH, RADIO_GROUP, SELECT)

#: A switch's two values, in the words the preview prints.
SWITCH_ON = "on"
SWITCH_OFF = "off"
SWITCH_VALUES: tuple[str, ...] = (SWITCH_ON, SWITCH_OFF)

#: THE KINDS REFUSED, BY NAME, with why. Asking :func:`check_kind` about any
#: of these -- or any other word -- refuses; the sentence is what the refusal
#: says.
REFUSED_KINDS: dict[str, str] = {
    "text field": (
        "a typed field holds whatever was typed, and 'put back exactly' would "
        "need the old text read verbatim and retyped -- the profile editor's "
        "path, not this one"
    ),
    "textarea": "a textarea is a typed field; see 'text field'",
    "autocomplete": (
        "an autocomplete stores the entry picked from LinkedIn's list, and "
        "nothing here picks an entry (the queue AUTOCOMPLETE-ENTRY-PICK)"
    ),
    "checkbox list": (
        "a list of checkboxes is several controls; admit each one as its own "
        "switch, by its own label"
    ),
    "button": (
        "a button performs an act and holds no value this writer can read "
        "back, so there is nothing to restore"
    ),
    "link": "a link navigates; it holds no value",
    "file input": (
        "a file input uploads, which is the operator's own ruling of "
        "2026-09-04 and its own verbs (linkedin_server/uploads.py)"
    ),
}

#: Whether a control's live proof is permitted, or which exclusion of the
#: ruling holds it. All four are BUILT the same way; only the live proof
#: differs, and the preview prints which applies.
LIVE_PROOF_ALLOWED = "ALLOWED"
NEVER_CREDENTIAL = "CREDENTIAL-SETTINGS-NEED-THE-OPERATOR"
NEVER_CANNOT_PUT_BACK = "CANNOT-BE-PUT-BACK-EXACTLY"
NEVER_SENSITIVE = "SENSITIVE-PERSONAL-ATTRIBUTE"
LIVE_PROOF_CLASSES: tuple[str, ...] = (
    LIVE_PROOF_ALLOWED,
    NEVER_CREDENTIAL,
    NEVER_CANNOT_PUT_BACK,
    NEVER_SENSITIVE,
)

#: The most controls of one role :func:`snapshot` will read. A settings page
#: draws a handful; past this the page is not one this writer has measured,
#: and the snapshot says so rather than reading on.
SNAPSHOT_MAX_PER_ROLE: int = 120

#: The roles :func:`snapshot` reads checked state from, in a fixed order.
_CHECKABLE_ROLES: tuple[str, ...] = ("switch", "checkbox", "radio")

#: What the reader answers when it cannot answer. Never a value.
UNKNOWN = "unknown"


@dataclass(frozen=True)
class AdmittedControl:
    """One control on an admitted page, as its capture drew it."""

    #: The control's accessible name EXACTLY as LinkedIn draws it -- for a
    #: radio group, the group's name; each radio's own name is a value.
    label: str
    kind: str
    #: The values it can hold, in LinkedIn's words: ``on``/``off`` for a
    #: switch, each radio's name for a group, each option's text for a select.
    values: tuple[str, ...]
    #: What each value means for him and for anyone else, one sentence each,
    #: keyed by value. Printed in the preview.
    meanings: tuple[tuple[str, str], ...]
    #: Whether a change shows to other people. If so the live proof restores
    #: it inside the same minute and reads it before and after.
    visible_to_others: bool
    #: One of :data:`LIVE_PROOF_CLASSES`, and why.
    live_proof: str
    live_proof_why: str
    #: The census rows this control carries.
    rows: tuple[str, ...]
    #: Anything else a live proof must respect, in one sentence.
    while_changed: str = ""


@dataclass(frozen=True)
class AdmittedPage:
    """One settings page admitted BY NAME, described from its own capture."""

    #: The page's heading as LinkedIn draws it -- the name it is admitted by.
    name: str
    #: The page's ADDRESS: the read boundary's admitted constant for it.
    #: Named ``address`` and never ``url``: the navigation guard reads
    #: every ``.url`` attribute as an address the BROWSER chose
    #: (``tests/test_navigation_is_never_derived.py``), and a registry
    #: constant read under that name is indistinguishable from one.
    address: str
    #: The accessible name of the page's Save control, or ``None`` when the
    #: page draws none and the press itself stores the value -- MEASURED on
    #: the capture, never assumed.
    save_label: Optional[str]
    controls: tuple[AdmittedControl, ...]
    #: A SENTENCE naming the capture the record was measured on and its
    #: tracked skeleton -- a sentence, because a package module names a tracked
    #: data file only inside one (the impact gate's sentence rule rests on it;
    #: ``tests/test_impact_gate_selects_data_dependencies.py``).
    capture: str
    #: Which ruling's application admitted it, and when.
    admitted_by: str


#: "Share profile updates" -- the one page with a real capture. MEASURED on
#: ``tests/fixtures/live2/setting.html`` (the live lane's session 2,
#: 2026-09-28, reduced to a skeleton): its ``main`` draws the heading "Share
#: profile updates", ONE ``input[type=checkbox][role=switch]`` named through
#: ``aria-labelledby`` "Share key profile updates", the visible text "Off"
#: beside it, a Back link, and NO button and NO form -- so the press is the
#: store. The address is the read boundary's own admitted line for it
#: (``readonly._ALLOWED_URL_PATTERNS``, the orchestrator's application of
#: ONE-NAMED-SETTINGS-PAGE-AT-A-TIME, 2026-09-27); this module adds the WRITE
#: to that one control and nothing else on the page.
SHARE_PROFILE_UPDATES = AdmittedPage(
    name="Share profile updates",
    address=profile_editor.ACCOUNT_SETTING_URL,
    save_label=None,
    controls=(
        AdmittedControl(
            label=profile_editor.ACCOUNT_SETTING_NAME,
            kind=SWITCH,
            values=SWITCH_VALUES,
            meanings=(
                (
                    SWITCH_ON,
                    "key profile updates he makes while it is on may be "
                    "shared with his network",
                ),
                (
                    SWITCH_OFF,
                    "his key profile updates are not shared with his network "
                    "by this setting",
                ),
            ),
            # The switch is his; nobody sees its state. What it changes is
            # what a LATER profile edit does, which is why its live proof
            # restores it inside the same minute and runs nothing between.
            visible_to_others=False,
            live_proof=LIVE_PROOF_ALLOWED,
            live_proof_why=(
                "a switch of his own account that is not a credential, holds "
                "one of two values and is put back exactly by pressing it "
                "again, and records no personal attribute"
            ),
            # ``P O17``, split from ``P O6-O20`` on 2026-10-10 because this
            # switch's state moved and the fourteen toggles beside it did not
            # (COMPOUND-ROW-SPLITS-ONLY-ON-STATE). It named the parent row
            # until a cold review read the preview print the stale one.
            rows=("P O17",),
            while_changed=(
                "while it reads on, a profile edit could be shared with his "
                "network, so no profile edit runs until it is restored, and "
                "the intro-edit rows' condition 1 reads it off before any edit "
                "(SELF-PROFILE-EDIT-NOTIFY-CONDITION-AMENDED)"
            ),
        ),
    ),
    capture=(
        "the live lane's capture of 2026-09-28 (session 2), tracked as the "
        "skeleton tests/fixtures/live2/setting.html"
    ),
    admitted_by=(
        "ONE-NAMED-SETTINGS-PAGE-AT-A-TIME, the orchestrator's application of "
        "2026-09-27 (read); the write to its one control, lane S, 2026-10-10, "
        "under HIS-OWN-SETTINGS-NOT-OUTWARD"
    ),
)

#: EVERY admitted page. One, until another page's capture admits it by name.
ADMITTED_PAGES: tuple[AdmittedPage, ...] = (SHARE_PROFILE_UPDATES,)


def _squash(text: Any) -> str:
    """Whitespace runs to one space, ends stripped. NOT case-folded: a name is
    admitted EXACTLY, and case is part of what LinkedIn draws."""
    return " ".join(str(text if text is not None else "").split())


def admitted_names() -> list[str]:
    """Every admitted ``page / control`` pair, for a refusal to list."""
    return [
        page.name + SETTING_JOIN + control.label
        for page in ADMITTED_PAGES
        for control in page.controls
    ]


def check_kind(kind: Any) -> str:
    """Return ``kind`` if this writer may set a control of it; else refuse BY
    NAME. PURE."""
    word = _squash(kind).casefold()
    if word in CONTROL_KINDS:
        return word
    why = REFUSED_KINDS.get(word)
    raise WriteAttemptError(
        f"a {word or 'nameless'!r} control is refused: this writer sets only a "
        f"switch, a radio group or a select ({list(CONTROL_KINDS)})"
        + (f" -- {why}." if why else ", and this kind is none of them.")
    )


def resolve(page_name: Any, control_label: Any) -> tuple[AdmittedPage, AdmittedControl]:
    """The admitted page and control these EXACT names identify, or refuse.

    A page is admitted by its name and a control by its label, both exactly as
    LinkedIn draws them -- whitespace runs aside, nothing is folded, nothing
    is guessed. A refusal names what IS admitted, so the caller can see the
    whole surface.
    """
    page_text = _squash(page_name)
    label_text = _squash(control_label)
    for page in ADMITTED_PAGES:
        if page.name != page_text:
            continue
        for control in page.controls:
            if control.label == label_text:
                check_kind(control.kind)
                return page, control
        raise WriteAttemptError(
            f"the admitted page {page.name!r} draws no admitted control named "
            f"{label_text!r}. Its admitted controls are "
            f"{[c.label for c in page.controls]}. Nothing was loaded."
        )
    raise WriteAttemptError(
        f"{page_text!r} is not an admitted settings page. A settings page is "
        "admitted BY NAME, one at a time, and only from a real capture of it "
        "(ONE-NAMED-SETTINGS-PAGE-AT-A-TIME, MESSAGING-SETTINGS-CAPABILITY-"
        f"LEVEL). Admitted today: {admitted_names()}. Nothing was loaded."
    )


def canonical_value(control: AdmittedControl, value: Any) -> str:
    """The value as the control spells it, or refuse. PURE.

    A switch takes ``on`` or ``off``; a radio group or a select takes one of
    the names its capture drew. Compared without case, returned in the
    control's own spelling, so the token binds to LinkedIn's words.
    """
    asked = _squash(value)
    for known in control.values:
        if asked.casefold() == known.casefold():
            return known
    raise WriteAttemptError(
        f"{asked!r} is not a value {control.label!r} holds. Its values are "
        f"{list(control.values)}; a value the capture did not draw is refused "
        "before any token exists for it."
    )


def split_setting(setting: Any) -> tuple[str, str]:
    """``<page> / <control>`` into its two names, or refuse. PURE."""
    text = _squash(setting)
    if text.count(SETTING_JOIN) != 1:
        raise WriteAttemptError(
            f"the setting must name ONE page and ONE control as "
            f"'<page>{SETTING_JOIN}<control>', exactly one separator; got "
            f"{text!r}. Admitted: {admitted_names()}."
        )
    page_name, _, control_label = text.partition(SETTING_JOIN)
    return page_name, control_label


def canonical_target(canonical: str, join: str) -> str:
    """Re-spell a ``setting :: value`` target in the admitted names' own words.

    ``join`` is ``writes.TARGET_JOIN``, passed in rather than imported so this
    module imports nothing from ``writes``. Refuses an unadmitted page, an
    unadmitted control, a refused kind and a value the control does not hold
    -- each BEFORE a token exists for it, because ``writes._target_for`` is the
    one point both ``observe`` and ``mint`` pass through.
    """
    setting, sep, value = str(canonical).partition(join)
    if not sep:
        raise WriteAttemptError(
            "a settings target is '<page> / <control> :: <value>'; the value "
            "half is missing."
        )
    page_name, control_label = split_setting(setting)
    page, control = resolve(page_name, control_label)
    return page.name + SETTING_JOIN + control.label + join + canonical_value(control, value)


def resolve_target(canonical: str, join: str) -> tuple[AdmittedPage, AdmittedControl, str]:
    """The page, the control and the canonical destination a target names."""
    respelled = canonical_target(canonical, join)
    setting, _, value = respelled.partition(join)
    page_name, control_label = split_setting(setting)
    page, control = resolve(page_name, control_label)
    return page, control, value


def audiences() -> dict[str, str]:
    """The write spec's ``audiences``: every admitted control's values, keyed
    by the value as the generic branches expect, each with its page, control
    and meaning. PURE.

    REFUSES A COLLISION. Keyed by the bare value, two admitted controls that
    both hold "on" would overwrite one another in a dict with no error, and a
    generic branch would print the wrong control's meaning (a cold review's
    finding, latent while one control is admitted). So a second control whose
    value spells the same word with a different meaning raises here, at
    import, and the registry has to be keyed some other way before it can be
    admitted.
    """
    out: dict[str, str] = {}
    for admitted in ADMITTED_PAGES:
        for control in admitted.controls:
            for value, sentence in control.meanings:
                key = value.casefold()
                text_for = (
                    f"{admitted.name}{SETTING_JOIN}{control.label}: "
                    + (sentence or "his own setting")
                )
                if key in out and out[key] != text_for:
                    raise ValueError(
                        f"two admitted controls hold the value {value!r} with "
                        "different meanings; the write spec's audiences are "
                        "keyed by the bare value and would overwrite one "
                        "another. Key them some other way before admitting "
                        "the second."
                    )
                out[key] = text_for
    return out


def meaning_of(control: AdmittedControl, value: str) -> str:
    """The one sentence the preview prints for ``value``. PURE."""
    for known, sentence in control.meanings:
        if known == value:
            return sentence
    return ""


def landed_path(address: Optional[str]) -> tuple[str, str, str]:
    """``(scheme, host, path without its trailing slash)`` of an address, or
    three empty strings for none. PURE, never raises. The query is dropped: a
    tracking parameter on a served page is the same page.

    ``writes`` COMPARES two of these rather than passing a landing into a
    call: the navigation guard treats a call's result as derived from any
    address handed to it, and a comparison's result as a boolean, which is
    what this question is."""
    if not address:
        return ("", "", "")
    parts = urlsplit(str(address).strip())
    return (parts.scheme, parts.netloc, parts.path.rstrip("/"))


def served_at(admitted: AdmittedPage, landed: Optional[str]) -> bool:
    """Did the page keep its own address? PURE. The path is compared, host
    fixed, trailing slash and query ignored -- the rule
    ``profile_editor.served_at_account_setting`` set for the same page."""
    if not landed:
        return False
    return landed_path(landed) == landed_path(admitted.address)


def admitted_address_pattern() -> "re.Pattern[str]":
    """The write door's pattern: the admitted pages' addresses, anchored, and
    nothing else."""
    return re.compile(
        "^(?:"
        + "|".join(re.escape(admitted.address.rstrip("/")) for admitted in ADMITTED_PAGES)
        + ")/?$"
    )


def page_url_for_target(canonical: str, join: str) -> str:
    """The address a target acts on: the admitted page's CONSTANT, chosen by
    the page's name. A page may veto an act; it never supplies its address."""
    admitted, _control, _value = resolve_target(canonical, join)
    return admitted.address


#: The host every admitted page lives on; the write spec's template is this
#: plus ``{target}``, filled by :func:`page_path_for_target`.
HOST_PREFIX = "https://www.linkedin.com/"


def page_path_for_target(canonical: str, join: str) -> str:
    """The admitted page's address AFTER :data:`HOST_PREFIX`, for the write
    spec's template. NEVER RAISES, as ``writes.url_target_of`` may not: a
    target that does not resolve comes back unchanged, and the anchored
    pattern refuses the address it builds."""
    try:
        url = page_url_for_target(canonical, join)
    except WriteAttemptError:
        return str(canonical)
    if not url.startswith(HOST_PREFIX):
        return str(canonical)
    return url[len(HOST_PREFIX):]


def _role_selector(role: str, name: str) -> str:
    """``role=<role>[name="<name>"s]`` -- the form ``dom.named_role_selector``
    builds -- for a role that module does not map (switch, combobox). Refuses
    a name that would escape its quotes rather than escaping it."""
    if role not in ("switch", "checkbox", "radio", "combobox", "button"):
        raise WriteAttemptError(f"no selector is built for role {role!r}")
    if not name or any(bad in name for bad in _SELECTOR_UNSAFE):
        raise WriteAttemptError(
            "refusing to build a selector from this name: it is empty or "
            "carries a character that would end the selector's own quoting."
        )
    return f'role={role}[name="{name}"s]'


def press_for(control: AdmittedControl, destination: str, reading: dict[str, Any]) -> tuple[str, str]:
    """The selector ``perform`` presses and the press KIND, or refuse. PURE.

    A switch is pressed by its own name in the role its reading found (switch
    or checkbox). A radio group is pressed on the ``<label for>`` OF the radio
    named for the destination -- the radio is page-wide unique, which the
    reader required, and ``writes._live_control`` reads that the label is
    BOUND to it (``dom.read_radio_label_binding``) before this selector is
    used. Never the input: LinkedIn covers a settings radio's input with a
    decorative element that takes the pointer, measured on the dark-mode page
    (``dom.settings_radio_label_selector``), so a press on the input times out
    having set nothing -- a cold review's finding against this writer's first
    form, which aimed at the input. A select is chosen from: ``perform``'s one
    ``select_option`` site, by the option's label, which is the grant's value
    half.
    """
    if control.kind == SWITCH:
        role = str(reading.get("role") or "")
        if role not in ("switch", "checkbox"):
            raise WriteAttemptError("the switch's role was not read; nothing is pressed")
        return _role_selector(role, control.label), "click"
    if control.kind == RADIO_GROUP:
        if not destination or any(bad in destination for bad in _SELECTOR_UNSAFE):
            raise WriteAttemptError(
                "refusing to build a selector from this name: it is empty or "
                "carries a character that would end the selector's own quoting."
            )
        return settings_radio_label_selector(destination), "click"
    if control.kind == SELECT:
        return _role_selector("combobox", control.label), "select_option"
    check_kind(control.kind)
    raise WriteAttemptError("unreachable: a checked kind with no press")


# ---------------------------------------------------------------------------
# Readers -- COUNTS and booleans through the role engine, never page text
# ---------------------------------------------------------------------------


def _blank(control: AdmittedControl) -> dict[str, Any]:
    return {
        "reading": UNKNOWN,
        "kind": control.kind,
        "role": None,
        "named": 0,
        "why": "",
        "error": None,
    }


async def _checked(page: Any, locator: Any) -> Optional[bool]:
    """One control's state: an ``input`` through the browser's own ``checked``
    property (and its ``aria-checked`` must agree when present), anything
    else through ``aria-checked`` alone. ``None`` when neither answers or the
    two disagree. Counts only."""
    is_input = coerce.as_count(
        await locator.and_(page.locator('input[type="checkbox"], input[type="radio"]')).count()
    )
    aria_on = coerce.as_count(await locator.and_(page.locator('[aria-checked="true"]')).count())
    aria_off = coerce.as_count(await locator.and_(page.locator('[aria-checked="false"]')).count())
    aria: Optional[bool] = True if aria_on == 1 else (False if aria_off == 1 else None)
    if is_input == 1:
        checked = coerce.as_count(await locator.and_(page.locator(":checked")).count()) == 1
        if aria is not None and aria is not checked:
            return None
        return checked
    return aria


async def read_control(page: Any, control: AdmittedControl) -> dict[str, Any]:
    """What ONE admitted control reads, as one of its values or ``unknown``.

    READ ONLY, and never raises. EVERY DOUBT IS ``unknown`` AND ``unknown`` IS
    NEVER A VALUE: no control of that name, two of them, an undeclared choice
    drawn beside the declared ones, a declared one missing, a state that
    cannot be read, a failure. Returns ``reading``, the ``role`` found, the
    ``named`` count and a ``why`` built from constants and counts.
    """
    out = _blank(control)
    try:
        if control.kind == SWITCH:
            switch = page.get_by_role("switch", name=control.label, exact=True, include_hidden=True)
            box = page.get_by_role("checkbox", name=control.label, exact=True, include_hidden=True)
            n_switch = coerce.as_count(await switch.count())
            n_box = coerce.as_count(await box.count())
            out["named"] = n_switch + n_box
            if out["named"] != 1:
                out["why"] = (
                    f"{out['named']} switch or checkbox controls are named exactly "
                    f"{control.label!r}, where exactly one is required."
                )
                return out
            locator = switch if n_switch == 1 else box
            out["role"] = "switch" if n_switch == 1 else "checkbox"
            state = await _checked(page, locator)
            if state is None:
                out["why"] = (
                    "the control holds no state this reader can read, or its "
                    "checked property and aria-checked disagree."
                )
                return out
            out["reading"] = SWITCH_ON if state else SWITCH_OFF
            out["why"] = f"exactly one control is named {control.label!r}, and it reads {out['reading']}."
            return out

        if control.kind == RADIO_GROUP:
            group = page.get_by_role(
                "radiogroup", name=control.label, exact=True, include_hidden=True
            ).or_(page.get_by_role("group", name=control.label, exact=True, include_hidden=True))
            out["named"] = coerce.as_count(await group.count())
            if out["named"] != 1:
                out["why"] = (
                    f"{out['named']} radio groups are named exactly {control.label!r}, "
                    "where exactly one is required."
                )
                return out
            out["role"] = "radio"
            drawn = coerce.as_count(await group.get_by_role("radio", include_hidden=True).count())
            if drawn != len(control.values):
                out["why"] = (
                    f"the group draws {drawn} radios and its capture drew "
                    f"{len(control.values)}: a choice was added or removed, and "
                    "a group this record does not describe is not read."
                )
                return out
            on: list[str] = []
            for value in control.values:
                radio = group.get_by_role("radio", name=value, exact=True, include_hidden=True)
                page_wide = page.get_by_role("radio", name=value, exact=True, include_hidden=True)
                if coerce.as_count(await radio.count()) != 1 or coerce.as_count(await page_wide.count()) != 1:
                    out["why"] = (
                        "a declared choice is not drawn exactly once in the group "
                        "and exactly once on the page, so it cannot be pressed by "
                        "its name alone."
                    )
                    return out
                state = await _checked(page, radio)
                if state is None:
                    out["why"] = "a declared choice holds no state this reader can read."
                    return out
                if state:
                    on.append(value)
            if len(on) != 1:
                out["why"] = (
                    f"{len(on)} of the group's {len(control.values)} declared choices "
                    "read checked, where exactly one is the only readable state."
                )
                return out
            out["reading"] = on[0]
            out["why"] = f"the group {control.label!r} draws its {drawn} declared choices and exactly one is checked."
            return out

        if control.kind == SELECT:
            # PAGE-WIDE FIRST, THEN THE NATIVE ONE: the press is
            # ``role=combobox[name=...]``, which matches ANY element of that
            # role and name, so the reader counts what the press would match
            # -- a second combobox wearing the name, drawn as a div, is a
            # second match, not something to step past (a cold review's
            # finding: this reader counted only native selects).
            any_combobox = page.get_by_role(
                "combobox", name=control.label, exact=True, include_hidden=True
            )
            select = any_combobox.and_(page.locator("select"))
            n_any = coerce.as_count(await any_combobox.count())
            n_native = coerce.as_count(await select.count())
            out["named"] = n_any
            if n_any != 1 or n_native != 1:
                out["why"] = (
                    f"{n_any} controls of role combobox are named exactly "
                    f"{control.label!r}, {n_native} of them a native select, "
                    "where exactly one, and that one a select, is required."
                )
                return out
            out["role"] = "combobox"
            drawn = coerce.as_count(await select.locator("option").count())
            if drawn != len(control.values):
                out["why"] = (
                    f"the select draws {drawn} options and its capture drew "
                    f"{len(control.values)}: an option was added or removed, and "
                    "a select this record does not describe is not read."
                )
                return out
            chosen: list[str] = []
            for value in control.values:
                option = select.get_by_role("option", name=value, exact=True, include_hidden=True)
                if coerce.as_count(await option.count()) != 1:
                    out["why"] = "a declared option is not drawn exactly once in the select."
                    return out
                if coerce.as_count(await option.and_(page.locator("option:checked")).count()) == 1:
                    chosen.append(value)
            if len(chosen) != 1:
                out["why"] = f"{len(chosen)} declared options read selected, where exactly one is required."
                return out
            out["reading"] = chosen[0]
            out["why"] = f"the select {control.label!r} draws its {drawn} declared options and exactly one is selected."
            return out
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
        out["why"] = "the reading itself failed; only its exception type is kept."
        return out
    out["why"] = f"{control.kind!r} is not a kind this writer reads."
    return out


def reads(reading: Optional[dict[str, Any]], value: str) -> bool:
    """Whether a reading is the value ``value``. PURE; the wait's question."""
    return bool(reading) and (reading or {}).get("reading") == value


def state_of(
    reading: Optional[dict[str, Any]], control: AdmittedControl, *, served: bool
) -> tuple[str, str]:
    """``(state, why)`` for the gate: one of the control's values, or
    ``unknown``. A page that did not keep its own address reads ``unknown``
    whatever it drew. PURE."""
    if not served:
        return UNKNOWN, (
            "the page did not keep the admitted address, so what it drew is "
            "not the admitted page and is not read."
        )
    reading = reading or {}
    value = reading.get("reading")
    if value in control.values:
        return str(value), str(reading.get("why") or "")
    return UNKNOWN, str(reading.get("why") or "the control could not be read.")


def _digest(value: Any) -> str:
    """A select's value reduced to a digest INSIDE the reader: only equality is
    ever asked of it, and a digest answers that while carrying none of the
    text the page wrote (``tests/test_readers_emit_no_page_string.py`` holds
    that no page string leaves a reader except as a people record)."""
    return hashlib.sha256(str(value).encode("utf-8", "replace")).hexdigest()[:16]


#: An aria snapshot's head line, ``- <role> "<name>"`` and whatever follows
#: (a state such as ``[checked]``, a select's options). MEASURED 2026-10-10 on
#: Playwright 1.63 over a local page: ``- switch "Alpha switch"``, ``- switch
#: "Foxtrot" [checked]``, ``- checkbox`` for a nameless one, ``''`` for a
#: hidden one (display none, visibility hidden, aria-hidden) -- never a raise --
#: and ``- combobox "Hotel select":`` before its options.
_ARIA_HEAD = re.compile(r'^\s*-\s*([A-Za-z]+)(?:\s+"((?:[^"\\]|\\.)*)")?')


async def _identity(locator: Any) -> str:
    """WHICH control sits at a position: a DIGEST of its role and accessible
    name as the browser's accessibility snapshot spells them, its state and
    anything after the name dropped -- so one control reads one identity in
    either state, and a control drawn in its place reads another. The name is
    text the page wrote and never leaves this function."""
    head = _ARIA_HEAD.match(str(await locator.aria_snapshot() or ""))
    return _digest(f"{head.group(1)}|{head.group(2) or ''}" if head else "")


async def snapshot(page: Any) -> dict[str, Any]:
    """EVERY switch, checkbox, radio and native select, position by position.

    For ``only_that_control_moved``: each switch, checkbox and radio on the
    page by role, in document order, as ``is_checked()``; each ``select`` as
    a DIGEST of its ``input_value()`` -- the value itself never leaves this
    function, because a select's value is text the page chose -- and, under
    ``ids``, each position's IDENTITY (:func:`_identity`), so a control
    replaced by another of the same role is seen as a redraw rather than
    compared as if it were the same one (a cold review's finding: the counts
    alone let a same-count redraw through).

    WHAT IT DOES NOT READ, said rather than implied: a button's pressed state,
    a menu item's checked state, a custom listbox, a typed value. A press that
    moved one of those is not seen here. READ ONLY; never raises; a failure is
    its exception type.
    """
    out: dict[str, Any] = {role: [] for role in _CHECKABLE_ROLES}
    out["select"] = []
    out["ids"] = {role: [] for role in _CHECKABLE_ROLES + ("select",)}
    out["error"] = None
    out["too_many"] = False
    try:
        for role in _CHECKABLE_ROLES:
            locator = page.get_by_role(role, include_hidden=True)
            drawn = coerce.as_count(await locator.count())
            if drawn > SNAPSHOT_MAX_PER_ROLE:
                out["too_many"] = True
                return out
            for index in range(drawn):
                one = locator.nth(index)
                out[role].append(bool(await one.is_checked()))
                out["ids"][role].append(await _identity(one))
        selects = page.locator("select")
        drawn = coerce.as_count(await selects.count())
        if drawn > SNAPSHOT_MAX_PER_ROLE:
            out["too_many"] = True
            return out
        for index in range(drawn):
            one = selects.nth(index)
            out["select"].append(_digest(await one.input_value()))
            out["ids"]["select"].append(await _identity(one))
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def snapshot_readable(shot: Optional[dict[str, Any]]) -> bool:
    """Whether a snapshot can be compared at all: read, without error, and
    within :data:`SNAPSHOT_MAX_PER_ROLE`. PURE. ``writes.perform`` presses
    nothing when the BEFORE snapshot is not -- the check after the press could
    never pass, and on a page that stores on the press an unchecked press is
    one nobody can say anything about (a cold review's finding)."""
    return isinstance(shot, dict) and not shot.get("error") and not shot.get("too_many")


def snapshot_counts(shot: Optional[dict[str, Any]]) -> dict[str, Any]:
    """What of a snapshot may leave this process: how many of each kind."""
    shot = shot or {}
    return {
        "switches": len(shot.get("switch") or []),
        "checkboxes": len(shot.get("checkbox") or []),
        "radios": len(shot.get("radio") or []),
        "selects": len(shot.get("select") or []),
        "error": shot.get("error"),
        "too_many": bool(shot.get("too_many")),
    }


#: How many positions a press of each kind moves, by snapshot list. A switch
#: flips one checkable (it may be drawn as role switch or checkbox); a radio
#: group unchecks one radio and checks another; a select changes one value.
_EXPECTED_MOVES: dict[str, dict[str, int]] = {
    SWITCH: {"switch+checkbox": 1, "radio": 0, "select": 0},
    RADIO_GROUP: {"switch+checkbox": 0, "radio": 2, "select": 0},
    SELECT: {"switch+checkbox": 0, "radio": 0, "select": 1},
}


def only_that_control_moved(
    before: Optional[dict[str, Any]],
    after: Optional[dict[str, Any]],
    control: AdmittedControl,
    *,
    reached: bool,
) -> dict[str, Any]:
    """After the press: did THIS control -- and nothing else on the page --
    move? PURE. The settings page's form of ``profile_editor.only_the_field_
    moved``.

    ``reached`` is whether the control reads the requested value after the
    bounded wait. The snapshots are compared POSITION BY POSITION, and by each
    position's IDENTITY where both snapshots carry one, so a page that redrew
    a different set of controls -- fewer, more, or as many but not the same --
    is refused rather than matched. Since the gate required the control to
    read something OTHER than the destination before the press, a control
    that now reads the destination has moved -- so when it reached it and the
    page moved EXACTLY as many positions as one press of its kind moves, the
    moved positions are its own.

    WHAT "NOTHING ELSE MOVED" COVERS: the switches, checkboxes, radios and
    native selects :func:`snapshot` reads, and nothing else on the page.
    """
    out: dict[str, Any] = {"proceed": False, "code": None, "why": "", "moved": None}
    for shot in (before, after):
        if not snapshot_readable(shot):
            out["code"] = "unreadable"
            out["why"] = (
                "the page's controls could not be read before and after the "
                "press, so nothing can say only this one moved."
            )
            return out
    for role in _CHECKABLE_ROLES + ("select",):
        if len(before.get(role) or []) != len(after.get(role) or []):
            out["code"] = "page_redrew"
            out["why"] = (
                f"the page drew {len(before.get(role) or [])} {role} control(s) "
                f"before the press and {len(after.get(role) or [])} after it: "
                "a different set of controls, so no position can be compared."
            )
            return out
    ids_before = before.get("ids") or {}
    ids_after = after.get("ids") or {}
    for role in _CHECKABLE_ROLES + ("select",):
        if (ids_before.get(role) or []) != (ids_after.get(role) or []):
            out["code"] = "page_redrew"
            out["why"] = (
                f"the page drew as many {role} controls after the press as "
                "before, but not the same ones -- a control was replaced -- "
                "so no position can be compared."
            )
            return out

    def moved(role: str) -> int:
        return sum(1 for a, b in zip(before.get(role) or [], after.get(role) or []) if a != b)

    seen = {
        "switch+checkbox": moved("switch") + moved("checkbox"),
        "radio": moved("radio"),
        "select": moved("select"),
    }
    out["moved"] = seen
    if not reached:
        out["code"] = "the_control_did_not_move"
        out["why"] = "the control does not read the requested value after the press."
        return out
    if seen != _EXPECTED_MOVES[control.kind]:
        out["code"] = "another_control_moved"
        out["why"] = (
            "ANOTHER CONTROL MOVED beside the one asked for: the page moved "
            f"{seen}, where one press of a {control.kind} moves "
            f"{_EXPECTED_MOVES[control.kind]}."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "the control reads the requested value, and no other switch, checkbox, "
        "radio or native select on the page moved -- the four kinds this check "
        "reads; nothing else on the page is read."
    )
    return out


#: Why a page that stores on the press must STOP, by the check's code. Read by
#: :func:`press_stop`; every code the check can return except a pass, and the
#: code ``not_run`` for a press whose check never ran.
_STOP_WHY: dict[str, str] = {
    "another_control_moved": (
        "another control on it moved beside the one asked for, so both changes "
        "are already stored"
    ),
    "the_control_did_not_move": (
        "the control did not read the value asked for after the press, and a "
        "press on a switch of his has been measured landing minutes late, so "
        "what the page stores now is not known"
    ),
    "page_redrew": (
        "the page drew a different set of controls after the press, so nothing "
        "can say what the press changed"
    ),
    "unreadable": (
        "its controls could not be read after the press, so nothing can say "
        "what the press changed"
    ),
    "not_run": (
        "the press raised before its outcome could be read, and it may have "
        "landed"
    ),
}


def press_stop(
    admitted: Optional[AdmittedPage],
    check: Optional[dict[str, Any]],
    *,
    attempted: bool,
) -> Optional[str]:
    """The receipt's STOP sentence, or ``None``. PURE.

    A page that STORES ON THE PRESS (its capture drew no Save) has nothing to
    discard: whatever the press did is already stored. So every press there
    whose check did not pass -- whatever the reason, including a press that
    raised before its check ran -- is a STOP. Not one shape of the five, which
    is what this writer first shipped (a cold review's HIGH finding: only
    ``another_control_moved`` set it, and no test read it). A page with a Save
    presses Save only on a passing check, so a failed one stored nothing; and
    a press never attempted -- refused before it -- stored nothing either.
    """
    if admitted is None or admitted.save_label is not None or not attempted:
        return None
    if check is not None and check.get("proceed") is True:
        return None
    code = str((check or {}).get("code") or "not_run")
    why = _STOP_WHY.get(code, "the check after the press did not pass")
    return (
        f"STOP. This page stores on the press, and {why}. Open the page, read "
        "every control on it, and put each one back by hand before anything "
        "else runs."
    )


async def save_gate(page: Any, admitted: AdmittedPage) -> dict[str, Any]:
    """Whether to press the page's Save, and its selector. READ ONLY.

    A page whose capture drew no Save stores on the press: there is nothing
    to press, and that is said. A page with a Save is pressed only if exactly
    ONE enabled control of role button carries its exact name.
    """
    out: dict[str, Any] = {"needed": admitted.save_label is not None, "proceed": False, "selector": "", "why": ""}
    if admitted.save_label is None:
        out["why"] = (
            "the page draws no Save (measured on its capture): the press is the "
            "store, so there is nothing further to press."
        )
        return out
    try:
        save = page.get_by_role("button", name=admitted.save_label, exact=True)
        drawn = coerce.as_count(await save.count())
        enabled = coerce.as_count(await save.and_(page.locator(":enabled")).count())
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["why"] = f"the Save could not be read ({type(exc).__name__}); it is not pressed."
        return out
    if drawn != 1 or enabled != 1:
        out["why"] = (
            f"{drawn} control(s) named {admitted.save_label!r}, {enabled} enabled; "
            "exactly one enabled is required, so Save is not pressed."
        )
        return out
    out["proceed"] = True
    out["selector"] = _role_selector("button", admitted.save_label)
    out["why"] = f"exactly one enabled {admitted.save_label!r}."
    return out


def preview_facts(
    admitted: AdmittedPage, control: AdmittedControl, reading: Optional[dict[str, Any]]
) -> dict[str, Any]:
    """What the confirm block prints about the page and the control. PURE.

    The page, the control, its kind, the values it can hold and what each
    means, whether a change shows to others, how the change is stored, and
    which live-proof class holds it. The CURRENT and REQUESTED values are
    printed by the direction block beside this.
    """
    reading = reading or {}
    return {
        "page": admitted.name,
        "address": admitted.address,
        "control": control.label,
        "kind": control.kind,
        "values": list(control.values),
        "what_each_value_means": {value: sentence for value, sentence in control.meanings},
        "visible_to_others": control.visible_to_others,
        "stored_by": (
            "the press itself -- the page draws no Save"
            if admitted.save_label is None
            else f"the page's {admitted.save_label!r}, pressed only if this control and no other moved"
        ),
        "live_proof": control.live_proof,
        "live_proof_why": control.live_proof_why,
        "while_changed": control.while_changed,
        "rows": list(control.rows),
        "ruling": RULING,
        "read": {
            "named": coerce.as_count(reading.get("named")),
            "role": reading.get("role"),
            "error": reading.get("error"),
        },
    }


def direction_block(
    control: AdmittedControl, current: str, destination: str
) -> dict[str, Any]:
    """The direction ``writes._direction`` prints: from, to, and what each
    means. Refuses a value the control does not hold, and a no-op. PURE."""
    if current not in control.values:
        raise WriteAttemptError(
            f"the control reads {current!r}, which is not one of its values "
            f"{list(control.values)}; a state that cannot be named is not moved from."
        )
    if destination not in control.values:
        raise WriteAttemptError(
            f"{destination!r} is not one of {control.label!r}'s values {list(control.values)}."
        )
    if current == destination:
        raise WriteAttemptError(f"{control.label!r} already reads {current!r}. Nothing to change.")
    return {
        "currently": current,
        "after": destination,
        "what_it_means_now": meaning_of(control, current),
        "what_it_will_mean": meaning_of(control, destination),
        "who_can_see_the_change": (
            "other members can see it: the live proof restores it inside the same minute"
            if control.visible_to_others
            else "nobody else sees this setting itself"
        ),
        # THE KEY ``writes.preview`` prints as ``who_can_see_it`` for any spec
        # that carries audiences; without it that field printed null.
        "who_will_see_it_after": (
            "other members can see it"
            if control.visible_to_others
            else "nobody else sees this setting itself"
        ),
    }


def restore_call(admitted: AdmittedPage, control: AdmittedControl, previous: Optional[str]) -> Optional[str]:
    """The exact call that puts ``previous`` back, or ``None`` if it was not
    read. PURE. Never run here: restoring is a write with its own token."""
    if previous is None or previous not in control.values:
        return None
    return (
        f"{TOOL_NAME}(settings_page={admitted.name!r}, control={control.label!r}, "
        f"value={previous!r})  # then confirm the token it returns"
    )
