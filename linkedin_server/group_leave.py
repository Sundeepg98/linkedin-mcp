"""Leaving one LinkedIn group he belongs to (census ``M C63`` and ``N 64``).

ONE CAPABILITY COUNTED TWICE by two census slices, and the WriteSpec was
written on 2026-09-05 (``_audit/2026-09-05-leave-group-writespec.md``) without
being built. This module is the build's reading half: selectors, locator COUNT
readers and pure verdicts. ``writes.py`` holds the spec and the arms that call
in here, the same split ``company_interest`` set for ``mark_company_interest``.

## THE RULINGS IT IS BUILT UNDER

* ``OUTWARD-CLASSES-BUILT-BEHIND-GRANTS`` (2026-09-24): withdrawing one of HIS
  OWN items is built behind the single-use grant, off by default, and fired
  only at a target he names in that call. His membership of a group is his.
* ``PAGE-MAY-VETO-NEVER-SUPPLY`` (2026-09-24): the only address this action
  ever loads is the CONSTANT :data:`GROUPS_URL`. The group id comes from the
  caller; the page may only refuse it (the id is not one of his memberships),
  never supply one.
* ``PEOPLE-DATA-MITIGATIONS`` item 6: a target is an id the caller supplies,
  never a name. **A GROUP NAME IS NOT READ ANYWHERE IN THIS MODULE.** No
  selector names a label that carries one, no reader returns text, and every
  ``why`` is built from counts and the caller's own digits. A group named after
  a person is the precise case ``groups.py`` exists for, and its rule governs
  here: a group is addressed by its NUMERIC id.

## WHAT IS MEASURED, AND WHERE

``scripts/_probe_groups_menu.py`` (2026-09-05) opened all five per-row menus on
his own ``/groups/`` page, pressed nothing inside them, and read three labels:
``Update your settings`` (x10), ``Copy link to group`` (x5), ``Leave this
group`` (x5) -- one leave item per membership row, none on a suggestion row. A
2026-09-20 capture of the same page (gitignored) holds that menu content IN THE
DOM while it is closed, inside an ``aria-hidden="true"`` container, as
``div[role=button]`` items in a list inside the row.

THE ROW IS FOUND FROM THE CONTROL, NEVER FROM THE ANCHOR, and that is the
measured rule rather than a preference: from each button declaring
``aria-expanded``, walk up; the FIRST ancestor holding a numeric group anchor
is the row, and the control is ROW-SCOPED only if that row holds anchors of
EXACTLY ONE group id. Five of the page's ten such buttons qualified; the other
five stop at the suggestion block or the whole page, which hold five and ten
ids. The same walk run from the anchor resolved ZERO rows -- a containment rule
is not symmetric.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **What pressing ``Leave this group`` does.** Nobody has watched it. LinkedIn
  may leave at once or open a confirmation. If a visible dialog is on the page
  after the press, NOTHING further is pressed: :func:`read_after_press` counts
  the dialogs and their buttons, and the verification -- a FRESH render of
  ``/groups/`` -- decides ``performed``. The first supervised press is the
  measurement, the shape ``mark_company_interest`` and ``send_message``
  shipped in.
* **Whether the menu opens in place.** The closed menu sits inside the row; an
  open one drawn anywhere else (a portal at the end of the document, say) is
  not provably this row's, and :func:`menu_item_gate` refuses it.
* **How the open menu is exposed.** Measured only closed. The leave item is
  counted through Playwright's ROLE engine, which skips ``aria-hidden``
  subtrees and hidden elements, and then required to be visible -- so an item
  still inside the closed container is never pressable, whatever its CSS.
* **Whether a group left can be rejoined.** See the spec's reversibility
  fields in ``writes.py``: treated as irreversible.

## THE SELECTORS ARE XPATH 1.0, BUILT FROM CONSTANTS AND ONE VALIDATED ID

Nothing the page wrote is spliced into a selector. The one variable is the
caller's group id, admitted only as a bounded run of the ten ASCII digits by
:func:`checked_group_id` -- which reuses ``group_page.group_page_url``, the
builder that already refuses a slug, because a slug is a name. The id is
compared EXACTLY: an anchor's segment after ``/groups/`` is cut at the first
``/``, ``?`` or ``#`` and compared with ``=``, so ``1000`` never matches
``10001``.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce, group_page

#: The Groups root: the ONE address this action loads, for the preview, the
#: click and the verification alike. A constant -- the group id never enters a
#: navigation, which is ``PAGE-MAY-VETO-NEVER-SUPPLY`` by construction.
GROUPS_URL: str = "https://www.linkedin.com/groups/"

#: The menu item that performs the leave, as the per-row menu draws it
#: (measured 2026-09-05, five of five membership rows). LinkedIn's own UI
#: words: it names no group.
LEAVE_LABEL: str = "Leave this group"

#: The two states this action knows, and the one it answers when it cannot
#: tell. ``unknown`` is the same string ``writes.UNKNOWN`` spells.
MEMBER: str = "member"
NOT_MEMBER: str = "not_member"
UNKNOWN: str = "unknown"

#: The bound on a group id, taken from ``group_page`` (which takes it from
#: ``groups``) rather than written again.
MAX_IDENTIFIER_DIGITS: int = group_page.MAX_IDENTIFIER_DIGITS

_DIGITS = "0123456789"


def checked_group_id(candidate: Any) -> tuple[Optional[str], str]:
    """``(digits, "")`` for a usable group id, else ``(None, why)``.

    THE WHY NEVER REPEATS THE CANDIDATE. The commonest wrong value is a group's
    NAME or slug, and a group named after a person makes that a person's name;
    ``group_page.group_page_url`` refuses by SHAPE (character classes and a
    length) for exactly that reason, and this reuses it rather than restating
    the rule.
    """
    text = str(candidate if candidate is not None else "").strip()
    verdict = group_page.group_page_url(text)
    if verdict.get("built"):
        return str(verdict["identifier"]), ""
    return None, (
        f"refused as {verdict.get('refused')} ({verdict.get('saw')}). "
        f"{verdict.get('why')}"
    )


def _required_digits(identifier: Any) -> str:
    """The id, re-checked where a selector is BUILT from it. Raises ValueError.

    Belt and braces: every caller has already validated it, and a selector is
    the one place a stray quote could widen a predicate. The message carries a
    shape, never the value.
    """
    digits, why = checked_group_id(identifier)
    if digits is None:
        raise ValueError(
            "refusing to build a group selector: the id is not a bounded run of "
            "the ten ASCII digits. " + why
        )
    return digits


def _segment(href: str) -> str:
    """XPath 1.0: the path segment after the first ``/groups/`` in ``href``.

    Cut at the first ``/``, ``?`` or ``#`` -- the query and fragment are never
    part of an id, the same rule ``groups.group_identifier`` applies by
    dropping them first. ``href`` is an XPath expression: ``@href`` for the
    anchor in context, or a path whose FIRST node's string value is used.
    """
    rest = f"substring-after({href},'/groups/')"
    cut_slash = f"substring-before(concat({rest},'/'),'/')"
    cut_query = f"substring-before(concat({cut_slash},'?'),'?')"
    return f"substring-before(concat({cut_query},'#'),'#')"


_SEGMENT = _segment("@href")

#: A predicate body true of an ``<a>`` whose href names a group by a bounded
#: run of the ten ASCII digits. ``translate`` deletes the digits, so an empty
#: remainder means digits only -- XPath has no ``isdigit`` to be fooled by
#: other scripts. The root link (``/groups/`` with nothing after it) fails the
#: length test, which is ``group_root_carries_no_identifier`` in ``groups.py``.
NUMERIC_GROUP_ANCHOR: str = (
    f"contains(@href,'/groups/') and string-length({_SEGMENT}) > 0 "
    f"and string-length({_SEGMENT}) <= {MAX_IDENTIFIER_DIGITS} "
    f"and translate({_SEGMENT},'{_DIGITS}','') = ''"
)

#: From any node: its ROW, the nearest ancestor holding a numeric group
#: anchor. ``ancestor`` is a reverse axis, so ``[1]`` is the NEAREST one.
_ROW_OF = f"ancestor::*[.//a[{NUMERIC_GROUP_ANCHOR}]][1]"

#: Every disclosure on the page, row-scoped or not: the denominator.
DISCLOSURES: str = "xpath=//button[@aria-expanded]"

#: From an anchor inside a row holding exactly ONE disclosure: the segment of
#: that row's FIRST numeric group anchor. The nearest ancestor of the anchor
#: that holds a disclosure is the row itself -- the lowest common ancestor of
#: the anchor and the row's one disclosure, which cannot sit below the row,
#: because the row is the nearest ancestor of the disclosure holding an
#: anchor. XPath 1.0 has no variables, and this is how a predicate on one
#: anchor reaches its row's first.
_FIRST_SEGMENT_IN_ROW = _segment(
    "ancestor::*[.//button[@aria-expanded]][1]"
    f"/descendant::a[{NUMERIC_GROUP_ANCHOR}][1]/@href"
)

#: EVERY ROW-SCOPED DISCLOSURE, whatever its id: a disclosure whose row holds
#: exactly one disclosure and numeric group anchors of exactly ONE id. It is
#: the HYDRATION witness -- the page drew at least one membership row -- and
#: it may UNDER-count (a row holding two disclosures is not counted), which
#: only ever turns ``not_member`` into ``unknown``.
ROW_SCOPED_DISCLOSURES: str = (
    "xpath=//button[@aria-expanded]"
    f"[{_ROW_OF}[count(.//button[@aria-expanded]) = 1]"
    f"[not(.//a[({NUMERIC_GROUP_ANCHOR}) and {_SEGMENT} != {_FIRST_SEGMENT_IN_ROW}])]]"
)

#: The leave item wherever it is in the DOM, open or closed, exposed or not.
#: A FACT reported beside the verdict, never an aim. Exact after whitespace
#: normalisation.
LEAVE_ITEMS_IN_DOM: str = (
    f"xpath=//*[@role='button'][normalize-space(.)='{LEAVE_LABEL}']"
)

#: The leave item as a PRESSABLE control: through the ROLE engine, which does
#: not match inside an ``aria-hidden`` subtree or a hidden element, and then
#: required visible. The ``s`` suffix is Playwright's case-sensitive whole-name
#: match. A closed menu's item -- in the DOM, inside ``aria-hidden="true"`` --
#: is never counted here.
LEAVE_ITEM_PRESSABLE: str = f'role=button[name="{LEAVE_LABEL}"s] >> visible=true'

#: Visible dialogs, for the after-press reading. Role selectors skip hidden
#: elements, so a dialog template left in the markup does not count. Both
#: roles, because a confirmation is as likely to be an ``alertdialog``.
VISIBLE_DIALOGS: str = "role=dialog"
VISIBLE_ALERTDIALOGS: str = "role=alertdialog"
BUTTONS_IN_DIALOGS: str = "role=dialog >> role=button"
BUTTONS_IN_ALERTDIALOGS: str = "role=alertdialog >> role=button"


def _carries_only(identifier: str) -> str:
    """Predicates on a ROW: it holds an anchor naming ``identifier`` and no
    numeric group anchor naming any other id. Exactly one distinct id."""
    return (
        f"[.//a[({NUMERIC_GROUP_ANCHOR}) and {_SEGMENT} = '{identifier}']]"
        f"[not(.//a[({NUMERIC_GROUP_ANCHOR}) and {_SEGMENT} != '{identifier}'])]"
    )


def disclosure_selector(identifier: Any) -> str:
    """The row-scoped disclosure of the ONE row carrying ``identifier``.

    Every button declaring ``aria-expanded`` whose row holds anchors of exactly
    one group id, and that id is the caller's. The CLICK SELECTOR for the first
    press: the verdict requires it to match exactly one element, and
    Playwright's strict mode refuses the click if that stops being true. It
    never names the button's label, which carries the group's name.
    """
    digits = _required_digits(identifier)
    return f"xpath=//button[@aria-expanded][{_ROW_OF}{_carries_only(digits)}]"


def row_selector(identifier: Any) -> str:
    """The ROW carrying ``identifier`` and only it, reached from its disclosure.

    The same walk as :func:`disclosure_selector`, ending on the row rather
    than on the button. XPath (no engine prefix), for chaining.
    """
    digits = _required_digits(identifier)
    return f"//button[@aria-expanded]/{_ROW_OF}{_carries_only(digits)}"


def leave_item_in_row_selector(identifier: Any) -> str:
    """The pressable leave item INSIDE the row carrying ``identifier``.

    The CLICK SELECTOR for the second press, appended only by
    :func:`menu_item_gate` and only when it resolves to exactly one element
    that is also the only pressable leave item on the page.
    """
    return f"xpath={row_selector(identifier)} >> {LEAVE_ITEM_PRESSABLE}"


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def read_rows(page: Any, identifier: Any) -> dict[str, Any]:
    """COUNTS ONLY, off the Groups page already open. Never raises.

    ``error`` is an exception TYPE name, never its message: a Playwright
    message can quote a selector and, through it, page content.
    """
    out: dict[str, Any] = {
        "disclosures": 0,
        "row_scoped_disclosures": 0,
        "disclosures_for_target": 0,
        "leave_items_in_dom": 0,
        "leave_items_pressable": 0,
        "error": None,
    }
    try:
        target_selector = disclosure_selector(identifier)
        out["disclosures"] = await _count(page, DISCLOSURES)
        out["row_scoped_disclosures"] = await _count(page, ROW_SCOPED_DISCLOSURES)
        out["disclosures_for_target"] = await _count(page, target_selector)
        out["leave_items_in_dom"] = await _count(page, LEAVE_ITEMS_IN_DOM)
        out["leave_items_pressable"] = await _count(page, LEAVE_ITEM_PRESSABLE)
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def _error_kind(value: Any) -> str:
    """An exception TYPE name is echoed only if it is spelled like one."""
    text = str(value or "")
    if text and len(text) <= 64 and (text[0].isalpha() or text[0] == "_") and all(
        character.isascii() and (character.isalnum() or character == "_")
        for character in text
    ):
        return text
    return "an exception"


def membership_verdict(
    reading: dict[str, Any], identifier: Any, *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for one group id, from ONE reading. PURE.

    Shared by the preview, the click and the verification, so the three ends
    of a write cannot disagree about what a page says:

        member      exactly ONE row-scoped disclosure's row carries this id
        not_member  the page drew at least one row-scoped disclosure and no
                    row-scoped disclosure's row carries this id -- the id may
                    be a suggestion row, or not on the page at all
        unknown     everything else, and the why says which, in counts

    EVERY ``why`` IS BUILT FROM COUNTS AND THE CALLER'S OWN DIGITS. The
    preview raises with it appended and ``perform`` raises with the click-time
    one, so whatever a why quotes can leave the process inside an exception.
    """
    reading = reading if isinstance(reading, dict) else {}
    digits, _why = checked_group_id(identifier)
    shown = digits if digits is not None else "(an id that is not digits)"
    facts: dict[str, Any] = {
        "group_id": digits,
        "disclosures_on_the_page": coerce.as_count(reading.get("disclosures")),
        "row_scoped_disclosures": coerce.as_count(
            reading.get("row_scoped_disclosures")
        ),
        "row_scoped_disclosures_for_this_id": coerce.as_count(
            reading.get("disclosures_for_target")
        ),
        "leave_items_in_the_dom": coerce.as_count(reading.get("leave_items_in_dom")),
        "leave_items_pressable": coerce.as_count(
            reading.get("leave_items_pressable")
        ),
        "group_name_read": False,
    }
    if digits is None:
        return (
            facts,
            UNKNOWN,
            "the group id is not a bounded run of the ten ASCII digits, so no "
            "row can be matched against it. It is not repeated here.",
        )
    if landed_elsewhere:
        return (
            facts,
            UNKNOWN,
            "the browser did not land on the Groups page this action reads, so "
            "nothing on the page it did land on says anything about group "
            f"{shown}. THE LANDING IS WITHHELD rather than named.",
        )
    if reading.get("error"):
        return (
            facts,
            UNKNOWN,
            f"the Groups page could not be read ({_error_kind(reading.get('error'))} "
            "was raised inside the reader, and its message is not repeated "
            "here). A gate whose read failed reports the failure rather than a "
            "state.",
        )
    total = facts["disclosures_on_the_page"]
    scoped = facts["row_scoped_disclosures"]
    mine = facts["row_scoped_disclosures_for_this_id"]
    if mine > 1:
        return (
            facts,
            UNKNOWN,
            f"{mine} row-scoped disclosures have rows carrying group {shown} and "
            "no other id, where exactly one is required. Pressing one of "
            "several would be choosing by position, which is refused for a "
            "write everywhere in this package.",
        )
    if mine == 1:
        return (
            facts,
            MEMBER,
            f"exactly one row-scoped disclosure on the Groups page has a row "
            f"carrying group {shown} and no other id -- the per-row control "
            "LinkedIn draws only on his memberships, found by walking up from "
            f"the control ({scoped} row-scoped of {total} disclosures on the "
            "page). The group's name is not read.",
        )
    if scoped == 0:
        return (
            facts,
            UNKNOWN,
            f"the page drew {total} disclosure(s) and NO row-scoped one, so it "
            "shows no membership row at all. That is a page that had not "
            "drawn its rows, or an account with no memberships, and the two "
            f"look the same from here -- so nothing is said about group {shown}.",
        )
    return (
        facts,
        NOT_MEMBER,
        f"the page drew {scoped} row-scoped disclosure(s), each on a row "
        f"carrying exactly one group id, and none of those rows carries group "
        f"{shown}. It may be a suggestion row, which draws no row-scoped "
        "control, or not on the page at all; either way it is not one of the "
        "memberships the page lists.",
    )


async def read_state(page: Any, identifier: Any) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading, off the Groups page already open."""
    return membership_verdict(await read_rows(page, identifier), identifier)


def verification_verdict(
    before: Any, reading: dict[str, Any], identifier: Any
) -> tuple[dict[str, Any], str, str]:
    """The FRESH render's answer, held against what the preview counted. PURE.

    ``membership_verdict`` alone says ``not_member`` whenever the page drew
    ANY membership row and none carries the id -- which a page that has drawn
    SOME of its rows, and not yet the target's, satisfies too. After an
    irreversible press that would print ``performed: True`` for a leave that
    may not have landed (finding F-6 of lane L8's cold verification,
    2026-09-27). So the verification asks one more thing of a ``not_member``:
    the fresh render must draw EXACTLY ONE membership row fewer than the
    preview counted -- the one that was left -- and every other.

    Any other count is ``unknown``, and the why says it in counts: fewer is a
    page still drawing (or more than one membership gone), the same count or
    more is a list that changed in between. ``member`` and ``unknown`` pass
    through unchanged. ``before`` is the preview's facts, as
    ``membership_verdict`` returned them.
    """
    facts, state, why = membership_verdict(reading, identifier)
    if state != NOT_MEMBER:
        return facts, state, why
    before = before if isinstance(before, dict) else {}
    counted = coerce.as_count(before.get("row_scoped_disclosures"))
    drawn = facts["row_scoped_disclosures"]
    facts = {**facts, "membership_rows_the_preview_counted": counted}
    if counted < 1 or drawn != counted - 1:
        return (
            facts,
            UNKNOWN,
            f"the fresh render drew {drawn} membership row(s) and none carries "
            f"the group, but the preview counted {counted}; a finished leave "
            f"draws exactly {max(counted - 1, 0)}. A page still drawing its "
            "rows looks like this, and so does a list that changed in between, "
            "so it is not reported as a leave.",
        )
    return (
        facts,
        NOT_MEMBER,
        why
        + f" And the page drew exactly one membership row fewer than the "
        f"preview counted ({drawn} of {counted}): the one that was left.",
    )


#: THE MENU IS POLLED RATHER THAN WAITED FOR, briefly, because a menu still
#: opening reads as absent and one read would refuse a press that was about to
#: be fine. Two numbers for the reason ``writes.APPLY_MODAL_POLLS`` gives: the
#: COUNT is the property, the INTERVAL is pacing a test may push down.
MENU_POLLS: int = 8
MENU_POLL_MS: int = 250


async def read_menu(page: Any, identifier: Any) -> dict[str, Any]:
    """COUNTS ONLY, after the disclosure press. Never raises."""
    out: dict[str, Any] = {
        "pressable_on_the_page": 0,
        "pressable_in_the_target_row": 0,
        "leave_items_in_dom": 0,
        "target_rows": 0,
        "expanded_in_the_target_row": 0,
        "error": None,
    }
    try:
        row = row_selector(identifier)
        out["pressable_on_the_page"] = await _count(page, LEAVE_ITEM_PRESSABLE)
        out["pressable_in_the_target_row"] = await _count(
            page, leave_item_in_row_selector(identifier)
        )
        out["leave_items_in_dom"] = await _count(page, LEAVE_ITEMS_IN_DOM)
        out["target_rows"] = await _count(page, "xpath=" + row)
        out["expanded_in_the_target_row"] = await _count(
            page, f"xpath={row}//button[@aria-expanded='true']"
        )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def menu_verdict(reading: dict[str, Any], identifier: Any) -> dict[str, Any]:
    """Whether the SECOND press -- the leave itself -- may be queued. PURE.

    Exactly one pressable ``Leave this group`` on the whole page, and it is
    inside the row carrying the caller's id. Anything else queues NOTHING and
    says why in counts; the disclosure press stays the only press, and a menu
    left open is discarded by the verification's fresh navigation.
    """
    reading = reading if isinstance(reading, dict) else {}
    digits, _why = checked_group_id(identifier)
    shown = digits if digits is not None else "(an id that is not digits)"
    observed = {
        key: coerce.as_count(reading.get(key))
        for key in (
            "pressable_on_the_page",
            "pressable_in_the_target_row",
            "leave_items_in_dom",
            "target_rows",
            "expanded_in_the_target_row",
        )
    }
    observed["error"] = (
        _error_kind(reading.get("error")) if reading.get("error") else None
    )

    def refuse(condition: str, why: str) -> dict[str, Any]:
        return {
            "proceed": False,
            "selector": "",
            "refused_condition": condition,
            "why": why + " NOTHING further was pressed: the disclosure press is "
            "the only press this call made.",
            "observed": observed,
        }

    if digits is None:
        return refuse("no_target", "the group id is not digits.")
    if observed["error"]:
        return refuse(
            "unreadable",
            f"the menu could not be read after the disclosure press "
            f"({observed['error']} was raised inside the reader).",
        )
    page_wide = observed["pressable_on_the_page"]
    in_row = observed["pressable_in_the_target_row"]
    if page_wide == 0:
        return refuse(
            "leave_item_not_visible",
            f"after the disclosure press no visible {LEAVE_LABEL!r} control is "
            f"on the page ({observed['leave_items_in_dom']} in the DOM, none "
            "exposed and visible). The menu did not open, or opened without "
            "that item.",
        )
    if page_wide > 1:
        return refuse(
            "leave_item_not_unique",
            f"{page_wide} visible {LEAVE_LABEL!r} controls are on the page where "
            "exactly one is required. Pressing one of several would be choosing "
            "by position.",
        )
    if in_row != 1:
        return refuse(
            "leave_item_outside_the_target_row",
            f"the one visible {LEAVE_LABEL!r} control is NOT inside the row "
            f"carrying group {shown} ({observed['target_rows']} such row(s) on "
            "the page). A menu that cannot be shown to belong to the row the "
            "grant names is not pressed.",
        )
    return {
        "proceed": True,
        "selector": leave_item_in_row_selector(digits),
        "refused_condition": None,
        "why": (
            f"exactly one visible {LEAVE_LABEL!r} control is on the page and it "
            f"is inside the row carrying group {shown} and no other id -- the "
            "menu the disclosure press opened is that row's."
        ),
        "observed": observed,
    }


async def menu_item_gate(page: Any, identifier: Any) -> dict[str, Any]:
    """Read the menu after the disclosure press, briefly polled, and decide.

    It stops polling as soon as the target row shows a pressable leave item or
    the page shows more than one; either reading is final. The decision is
    :func:`menu_verdict`'s.
    """
    reading = await read_menu(page, identifier)
    polls = 1
    while (
        polls < MENU_POLLS
        and not reading.get("error")
        and coerce.as_count(reading.get("pressable_in_the_target_row")) == 0
        and coerce.as_count(reading.get("pressable_on_the_page")) <= 1
    ):
        await page.wait_for_timeout(MENU_POLL_MS)
        reading = await read_menu(page, identifier)
        polls += 1
    verdict = menu_verdict(reading, identifier)
    verdict["polls"] = polls
    return verdict


async def read_after_press(page: Any, identifier: Any) -> dict[str, Any]:
    """What the leave press left on the page, BEFORE anything navigates.

    COUNTS ONLY, and it decides nothing -- the verification's fresh render
    does. It is the one reading that can say a further step OPENED (a dialog
    appeared) rather than only that the leave did not land, and taking it is
    what a first supervised press exists for.
    """
    out: dict[str, Any] = {
        "dialogs": 0,
        "alertdialogs": 0,
        "buttons_in_dialogs": 0,
        "leave_items_pressable": 0,
        "row_scoped_disclosures_for_this_id": 0,
        "error": None,
    }
    try:
        out["dialogs"] = await _count(page, VISIBLE_DIALOGS)
        out["alertdialogs"] = await _count(page, VISIBLE_ALERTDIALOGS)
        out["buttons_in_dialogs"] = await _count(
            page, BUTTONS_IN_DIALOGS
        ) + await _count(page, BUTTONS_IN_ALERTDIALOGS)
        out["leave_items_pressable"] = await _count(page, LEAVE_ITEM_PRESSABLE)
        out["row_scoped_disclosures_for_this_id"] = await _count(
            page, disclosure_selector(identifier)
        )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def after_press_note(reading: dict[str, Any]) -> dict[str, Any]:
    """The after-press reading as the receipt prints it: counts and a sentence.

    A DIALOG ON THE PAGE AFTER THE PRESS IS A FURTHER STEP THAT OPENED AND WAS
    NOT TAKEN, and this says so in those words. Whether the leave landed is
    the verification's answer, not this reading's.
    """
    reading = reading if isinstance(reading, dict) else {}
    counts = {
        key: coerce.as_count(reading.get(key))
        for key in (
            "dialogs",
            "alertdialogs",
            "buttons_in_dialogs",
            "leave_items_pressable",
            "row_scoped_disclosures_for_this_id",
        )
    }
    error = _error_kind(reading.get("error")) if reading.get("error") else None
    opened = counts["dialogs"] + counts["alertdialogs"]
    if error:
        sentence = (
            f"the page could not be read after the leave press ({error}), so "
            "whether a further step opened is not known."
        )
    elif opened:
        sentence = (
            f"A FURTHER STEP OPENED AND WAS NOT TAKEN: {opened} visible "
            f"dialog(s) holding {counts['buttons_in_dialogs']} button(s) were on "
            "the page after 'Leave this group' was pressed, and NOTHING in them "
            "was pressed -- this server has never seen that step and does not "
            "choose inside it. The fresh render below says whether the leave "
            "landed; a confirmation left unanswered means it did not."
        )
    else:
        sentence = (
            "no dialog was visible after 'Leave this group' was pressed. The "
            "fresh render below says whether the leave landed."
        )
    return {
        **counts,
        "error": error,
        "further_step_opened": bool(opened) if not error else None,
        "what_this_means": sentence,
    }
