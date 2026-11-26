"""Answering ONE pending invitation he names, on his own invitation manager: accept it (census ``N 15``), ignore it (``N 16``), or withdraw one he sent (``N 10``).

THE BUILD'S READING HALF -- selectors, locator COUNT readers and pure
verdicts -- the split ``group_leave`` set for ``withdraw_from_group``:
``writes.py`` holds the three specs and the arms that call in here, and this
module presses nothing, navigates nowhere and returns no page text.

## THE RULINGS IT IS BUILT UNDER

* ``WRITE-CLASS-B`` and ``OPERATOR-NAMES-THE-TARGET``: an accept is ruling
  (b)'s CONNECT, toward the inviter; it fires only at an invitation he names.
  One gated accept he names is not the auto-accept
  ``auto_accept_or_auto_reply`` forbids -- nothing here loops, sweeps or
  answers an invitation nobody named.
* ``EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS``: ignoring an invitation is an act
  toward the inviter, built behind the grant and fired only at one he names.
* ``OUTWARD-CLASSES-BUILT-BEHIND-GRANTS``: withdrawing a pending invitation he
  SENT is withdrawing one of his own items (``outward_classes``
  ``withdraw_invitation``).
* ``PAGE-MAY-VETO-NEVER-SUPPLY``: the only addresses loaded are the two
  CONSTANTS ``invitation_manager`` admits. The member comes from the caller's
  own argument; the page may only refuse it (no aimable row carries that
  member), never supply one.
* ``PEOPLE-DATA-MITIGATIONS`` item 6: THE TARGET IS A PROFILE LINK (or a member
  id) HE SUPPLIES, NEVER A NAME. No name is read anywhere in this module: no
  selector names a label -- every button's and link's ``aria-label`` carries
  the member's name live -- and every answer is counts and closed words.
* ``J-19-BUILT-BEHIND-THE-GRANT``, for the withdraw: built behind the grant and
  REFUSING until its confirm dialog is captured. LinkedIn documents one
  (Help Center a568295: Withdraw, then Withdraw again in a pop-up). This server
  presses NOTHING in any dialog: :func:`read_after_press` counts what the press
  drew, by closed words, and the verification's fresh render -- a new
  navigation, which discards the dialog -- decides. So the first supervised
  withdraw at an invitation he names is expected to stop at that pop-up having
  withdrawn nothing, and its receipt IS the pop-up's capture.

## WHAT IS MEASURED, AND WHERE

Live session 11 (loads 14 and 15), read by lane readers-net26 on the tracked
copies with LinkedIn's words put back by keyed shape
(``tests/fixtures/synthetic/live11_invitations_words.html`` and
``live11_invitations_sent_words.html``):

* THE RECEIVED TAB: three invitations, each a ``role=listitem`` holding exactly
  two buttons whose whole visible words are ``Ignore`` and ``Accept``. A
  member's invitation holds one paragraph ending with LinkedIn's fixed ``wants
  to connect``, the member's link inside it; the row's picture links the same
  member. A Page's newsletter invitation holds a ``/company/`` link instead --
  never a member link -- so no member aim can reach it.
* THE SENT TAB: five invitations, each a ``role=listitem`` holding exactly one
  link whose whole visible word is ``Withdraw`` (an action link whose address
  is the site root) beside one member link, the picture.

THE ROW IS THE CONTROL'S NEAREST ``role=listitem`` ANCESTOR, and the aim is
that row's own member links: every ``/in/`` link in it must name the member
the caller linked, and at least one must. On the received tab the member link
must also sit inside the ``wants to connect`` paragraph, so the aim reaches a
CONNECTION invitation and no other kind of invitation a member might send.
The comparison runs in the page (XPath 1.0, evaluated by the browser) and
comes back as a COUNT -- the same rule ``dom.rail_invite_control_selector``
applies to his profile's rail, and its segment expression, imported.

## WHAT IS NOT MEASURED, AND WHICH WAY EACH GAP FAILS

* **What a press draws.** No capture holds the page after an Accept, an Ignore
  or a Withdraw. :func:`read_after_press` counts visible dialogs, the buttons
  in them by a closed list of LinkedIn's words, whether the address moved (the
  Withdraw link's address is the site root) and whether the row is still
  drawn. It decides nothing; nothing in a dialog is pressed.
* **Rows past the first render.** The tab is read as it first renders, no
  scroll: an invitation below it reads as not pending, and the preview refuses.
* **Member ids.** The rows' links are profile links as LinkedIn draws them; a
  member id the caller passes matches a row only if the row's link carries it.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import coerce, dom, invitation_manager

# ---------------------------------------------------------------------------
# The three actions, their tabs and their controls
# ---------------------------------------------------------------------------

#: THE NAMES CARRY A VERB THE CONSERVATION BASELINE KNOWS. A sanctioned write's
#: tool name must announce a write (``readonly.name_implies_write``) with a verb
#: the original forbidden list already named (``tests/test_writes.py``'s
#: renaming law). ``accept`` is a write verb the baseline never named, and
#: ``ignore`` is not a write verb at all, so the two received-tab acts are
#: named by the census rows' own words -- "Accept an invitation to connect",
#: "Ignore an invitation to connect" -- whose ``connect`` the baseline names.
#: ``withdraw`` is the baseline's (``linkedin_withdraw_application``), and
#: ``withdraw_invitation`` is ``outward_classes``' own record name.
ACCEPT = "accept_invitation_to_connect"
IGNORE = "ignore_invitation_to_connect"
WITHDRAW = "withdraw_invitation"
ACTIONS: tuple[str, ...] = (ACCEPT, IGNORE, WITHDRAW)

#: The two addresses ``invitation_manager`` admits, and nothing built here.
RECEIVED_URL: str = invitation_manager.RECEIVED_URL
SENT_URL: str = invitation_manager.SENT_URL

#: Each action's tab: ``received`` or ``sent``.
SIDE: dict[str, str] = {ACCEPT: "received", IGNORE: "received", WITHDRAW: "sent"}

#: Each action's control, as ``(tag, LinkedIn's whole visible word)``. The
#: words are ``invitation_manager``'s, compared exactly and never returned.
CONTROL: dict[str, tuple[str, str]] = {
    ACCEPT: ("button", invitation_manager.ACCEPT_WORD),
    IGNORE: ("button", invitation_manager.IGNORE_WORD),
    WITHDRAW: ("a", invitation_manager.WITHDRAW_WORD),
}

#: The states this module knows. ``UNKNOWN`` is ``writes.UNKNOWN``'s spelling.
PENDING: str = "invitation_pending"
NOT_PENDING: str = "invitation_not_pending"
UNKNOWN: str = "unknown"

#: The words a dialog's buttons are COUNTED against after a press, closed and
#: never read out. ``Withdraw`` is the Help Center's (a568295); the others are
#: LinkedIn interface words a confirmation or a follow-up commonly draws. A
#: button whose word is none of these is counted as ``other``. The list buys a
#: reading of a dialog nobody has captured; it never aims a press.
DIALOG_WORDS: tuple[str, ...] = (
    "Withdraw",
    "Cancel",
    "Dismiss",
    "Close",
    "Accept",
    "Ignore",
    "Report",
    "Undo",
    "Got it",
    "Done",
)

#: How a link's member segment is read, and what makes a link a member link:
#: ``dom``'s own expressions for his rail's cards, imported so one spelling of
#: the rule exists (case-folded vanity segments; the segment cut at the next
#: ``/``, ``?`` or ``#``).
_SEGMENT: str = dom._XPATH_LINK_SEGMENT
_MEMBER_LINK: str = dom._XPATH_MEMBER_LINK
_SAFE_SEGMENT = dom._RAIL_SEGMENT
_FOLD = dom._ASCII_LOWER

#: From a control: its ROW, the nearest ``role=listitem`` ancestor. ``ancestor``
#: is a reverse axis, so ``[1]`` is the nearest.
_ROW_OF: str = "ancestor::*[@role='listitem'][1]"


def _whole(word: str) -> str:
    """XPath: an element whose whole visible text, whitespace normalised, is
    ``word``. The words are this module's constants, never a caller's."""
    return f"normalize-space(.)='{word}'"


_CONNECT_PHRASE: str = invitation_manager.CONNECT_PHRASE

#: A paragraph whose normalised text ENDS with LinkedIn's ``wants to connect``.
_ENDS_WITH_CONNECT: str = (
    "substring(normalize-space(.), string-length(normalize-space(.)) - "
    f"{len(_CONNECT_PHRASE) - 1}) = '{_CONNECT_PHRASE}'"
)

#: Each tab's ROW SHAPE, as predicates on a row: exactly the controls the
#: capture draws on an invitation, and nothing more.
_ROW_SHAPE: dict[str, str] = {
    "received": (
        "[count(.//button) = 2]"
        f"[count(.//button[{_whole(invitation_manager.ACCEPT_WORD)}]) = 1]"
        f"[count(.//button[{_whole(invitation_manager.IGNORE_WORD)}]) = 1]"
        f"[.//p[{_ENDS_WITH_CONNECT}]]"
    ),
    "sent": f"[count(.//a[{_whole(invitation_manager.WITHDRAW_WORD)}]) = 1]",
}

#: The tab strip, read by COUNTS: the link whose whole word is ``Sent`` is
#: current on the sent tab and not on the received one (``invitation_manager``'s
#: rule, as XPath). ``Sent`` is a word the tracked copies keep verbatim.
_SENT_LINKS: str = f"xpath=//main//nav//a[{_whole(invitation_manager.SENT_TAB_WORD)}]"
_SENT_CURRENT: str = (
    f"xpath=//main//nav//a[@aria-current='true'][{_whole(invitation_manager.SENT_TAB_WORD)}]"
)
_ANY_CURRENT: str = "xpath=//main//nav//a[@aria-current='true']"

#: Visible dialogs, for the after-press reading (role selectors skip hidden
#: elements, so a dialog template left in the markup does not count).
VISIBLE_DIALOGS: str = "role=dialog"
VISIBLE_ALERTDIALOGS: str = "role=alertdialog"


# ---------------------------------------------------------------------------
# The target: a member segment, checked where a selector is built from it
# ---------------------------------------------------------------------------


def checked_segment(segment: Any) -> Optional[str]:
    """The segment, ASCII-folded, if it is safe to put inside an expression;
    else ``None``. A segment comes from ``named_profile.profile_segment`` --
    letters, digits, hyphens, underscores, percent-encoded octets -- and
    anything else is refused here, so no quote or bracket can reach XPath."""
    text = str(segment if segment is not None else "")
    if not _SAFE_SEGMENT.fullmatch(text):
        return None
    return text.translate(_FOLD)


def _required(segment: Any) -> str:
    folded = checked_segment(segment)
    if folded is None:
        raise ValueError(
            "refusing to build an invitation selector: the profile segment is "
            "not letters, digits, hyphens, underscores or percent-encoded octets."
        )
    return folded


def _carries(segment: str) -> str:
    """Predicates on a ROW: a member link naming ``segment``, none naming another."""
    return (
        f"[.//a[{_MEMBER_LINK} and {_SEGMENT} = '{segment}']]"
        f"[not(.//a[{_MEMBER_LINK} and {_SEGMENT} != '{segment}'])]"
    )


def _inviter_in_the_phrase(segment: str) -> str:
    """Received tab only: the member link sits in the ``wants to connect`` line."""
    return f"[.//p[{_ENDS_WITH_CONNECT}]//a[{_MEMBER_LINK} and {_SEGMENT} = '{segment}']]"


def control_selector(action: str, segment: Any) -> str:
    """THE control this action presses, in the ONE row of the member linked.

    The control wearing the action's whole word, whose nearest ``listitem`` is
    an invitation of its tab's shape, linking ``segment`` and no other member.
    The CLICK SELECTOR: the verdict requires it to match exactly one element,
    and ``perform`` presses it strictly, so a second match drawn between the
    reading and the press throws rather than choosing.
    """
    folded = _required(segment)
    side = SIDE[action]
    tag, word = CONTROL[action]
    extra = _inviter_in_the_phrase(folded) if side == "received" else ""
    return (
        f"xpath=//{tag}[{_whole(word)}]"
        f"[{_ROW_OF}{_ROW_SHAPE[side]}{_carries(folded)}{extra}]"
    )


def rows_selector(action: str) -> str:
    """Every invitation row of this action's tab, whoever it is from: the
    action's control in a row of the tab's shape. The denominator."""
    side = SIDE[action]
    tag, word = CONTROL[action]
    return f"xpath=//{tag}[{_whole(word)}][{_ROW_OF}{_ROW_SHAPE[side]}]"


def member_rows_selector(segment: Any) -> str:
    """Every ``listitem`` linking the member at all, whatever it draws: a fact
    beside the verdict (the member is on the page, but not as an aimable
    invitation), never an aim."""
    folded = _required(segment)
    return f"xpath=//*[@role='listitem'][.//a[{_MEMBER_LINK} and {_SEGMENT} = '{folded}']]"


# ---------------------------------------------------------------------------
# Landing and side
# ---------------------------------------------------------------------------


def tab_url(action: str) -> str:
    return RECEIVED_URL if SIDE[action] == "received" else SENT_URL


def landed_on_tab(action: str, landed: Any) -> bool:
    """Did the load land on this action's tab? Scheme, host and path, as
    ``invitation_manager`` reads a landing. PURE."""
    if SIDE[action] == "received":
        return invitation_manager.landed_on_received(landed)
    return invitation_manager.landed_on_sent(landed)


def side_of(reading: dict[str, Any]) -> str:
    """``received``, ``sent`` or ``unknown``, from the strip's counts. PURE."""
    if coerce.as_count(reading.get("sent_links")) != 1:
        return "unknown"
    if coerce.as_count(reading.get("sent_current")) == 1:
        return "sent"
    return "received" if coerce.as_count(reading.get("any_current")) >= 1 else "unknown"


# ---------------------------------------------------------------------------
# The readers: COUNTS ONLY, off the tab already open. Never raise.
# ---------------------------------------------------------------------------


async def _count(page: Any, selector: str) -> int:
    return coerce.as_count(await page.locator(selector).count())


async def read_rows(page: Any, action: str, segment: Any) -> dict[str, Any]:
    """The tab's strip, its invitation rows, and the rows of the member linked.

    ``error`` is an exception TYPE name, never its message: a Playwright message
    can quote a selector and, through it, the member's segment.
    """
    out: dict[str, Any] = {
        "sent_links": 0,
        "sent_current": 0,
        "any_current": 0,
        "rows": 0,
        "rows_for_target": 0,
        "listitems_linking_target": 0,
        "error": None,
    }
    try:
        target = control_selector(action, segment)
        member_rows = member_rows_selector(segment)
        out["sent_links"] = await _count(page, _SENT_LINKS)
        out["sent_current"] = await _count(page, _SENT_CURRENT)
        out["any_current"] = await _count(page, _ANY_CURRENT)
        out["rows"] = await _count(page, rows_selector(action))
        out["rows_for_target"] = await _count(page, target)
        out["listitems_linking_target"] = await _count(page, member_rows)
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


_WORDS: dict[str, str] = {ACCEPT: "accept", IGNORE: "ignore", WITHDRAW: "withdraw"}


def row_verdict(
    reading: dict[str, Any], action: str, *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """``(facts, state, why)`` for one member's invitation, from ONE reading. PURE.

    Shared by the preview, the click and the verification, so the three ends
    of a write cannot disagree about what a page says:

        invitation_pending      exactly ONE row of the tab's shape carries the
                                member linked, and no other member
        invitation_not_pending  the tab drew at least one invitation row and
                                none of them is that member's
        unknown                 everything else, and the why says which

    EVERY ``why`` IS BUILT FROM COUNTS: the member's link is not repeated in
    it, because the why leaves the process inside an exception.
    """
    reading = reading if isinstance(reading, dict) else {}
    side = SIDE.get(action)
    if side is None:
        # NOT ONE OF THIS MODULE'S ACTS: refused, never raised -- an exception
        # would carry the value it was handed out of the process.
        return (
            {"names_read": False},
            UNKNOWN,
            "this reading answers only the invitation acts this module names, "
            "and was asked about another.",
        )
    _tag, word = CONTROL[action]
    facts: dict[str, Any] = {
        "tab": side,
        "tab_read": side_of(reading),
        "invitation_rows_on_the_tab": coerce.as_count(reading.get("rows")),
        "rows_of_the_member_you_linked": coerce.as_count(reading.get("rows_for_target")),
        "list_items_linking_that_member": coerce.as_count(
            reading.get("listitems_linking_target")
        ),
        "names_read": False,
    }
    if landed_elsewhere:
        return (
            facts,
            UNKNOWN,
            f"the browser did not land on your invitation manager's {side} tab, "
            "so nothing on the page it did land on says anything about this "
            "invitation. THE LANDING IS WITHHELD rather than named.",
        )
    if reading.get("error"):
        return (
            facts,
            UNKNOWN,
            f"the {side} tab could not be read ({_error_kind(reading.get('error'))} "
            "was raised inside the reader, and its message is not repeated "
            "here). A gate whose read failed reports the failure, not a state.",
        )
    if facts["tab_read"] != side:
        return (
            facts,
            UNKNOWN,
            f"the manager's tab strip does not read as the {side} tab "
            f"({facts['tab_read']}), so its rows are not the invitations this "
            "act answers.",
        )
    rows = facts["invitation_rows_on_the_tab"]
    mine = facts["rows_of_the_member_you_linked"]
    if mine > 1:
        return (
            facts,
            UNKNOWN,
            f"{mine} invitation rows carry the member you linked and no other, "
            "where exactly one is required. Pressing one of several would be "
            "choosing by position, which no write in this package does.",
        )
    if mine == 1:
        return (
            facts,
            PENDING,
            f"exactly one invitation row on the {side} tab carries the member "
            f"you linked and no other member, with its {word!r} control "
            f"drawn once ({rows} invitation row(s) on the tab). The comparison "
            "ran in the page and came back as a count; no name was read.",
        )
    if rows == 0:
        return (
            facts,
            UNKNOWN,
            f"the {side} tab drew no invitation row at all, so it shows no "
            "pending invitation: a page that had not drawn its rows and a tab "
            "with nothing pending look the same from here, so nothing is said "
            "about this one.",
        )
    linked = facts["list_items_linking_that_member"]
    return (
        facts,
        NOT_PENDING,
        f"the {side} tab drew {rows} invitation row(s) and none of them carries "
        "the member you linked"
        + (
            f" -- though {linked} list item(s) link that member without being an "
            "invitation of the shape this act answers"
            if linked
            else ""
        )
        + ". The invitation may be answered already, below the first render "
        "(which is all this reads), or the link may name someone else.",
    )


async def read_state(
    page: Any, action: str, segment: Any, *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """The preview's and the click's reading, off the tab already open."""
    return row_verdict(
        await read_rows(page, action, segment), action, landed_elsewhere=landed_elsewhere
    )


def verification_verdict(
    before: Any, reading: dict[str, Any], action: str, *, landed_elsewhere: bool = False
) -> tuple[dict[str, Any], str, str]:
    """The FRESH render's answer, held against what the preview counted. PURE.

    ``row_verdict`` alone says ``invitation_not_pending`` whenever the tab drew
    ANY invitation row and none is the member's -- which a tab that has drawn
    SOME of its rows, and not yet that one, satisfies too. So the verification
    asks one thing more, ``group_leave.verification_verdict``'s rule: the fresh
    render must draw EXACTLY ONE invitation row fewer than the preview counted.
    Any other count is ``unknown``. ``invitation_pending`` and ``unknown`` pass
    through unchanged.
    """
    facts, state, why = row_verdict(reading, action, landed_elsewhere=landed_elsewhere)
    if state != NOT_PENDING:
        return facts, state, why
    before = before if isinstance(before, dict) else {}
    counted = coerce.as_count(before.get("invitation_rows_on_the_tab"))
    drawn = facts["invitation_rows_on_the_tab"]
    facts = {**facts, "invitation_rows_the_preview_counted": counted}
    if counted < 1 or drawn != counted - 1:
        return (
            facts,
            UNKNOWN,
            f"the fresh render drew {drawn} invitation row(s) and none carries the "
            f"member, but the preview counted {counted}; an answered invitation "
            f"leaves exactly {max(counted - 1, 0)}. A tab still drawing its rows "
            "looks like this, and so does a list that changed in between, so it "
            "is not reported as answered.",
        )
    return (
        facts,
        NOT_PENDING,
        why + f" And the tab drew exactly one invitation row fewer than the "
        f"preview counted ({drawn} of {counted}): the one this act answered.",
    )


# ---------------------------------------------------------------------------
# After the press: what it drew, before anything navigates
# ---------------------------------------------------------------------------


async def read_after_press(
    page: Any, action: str, segment: Any, *, address_before: Optional[str] = None
) -> dict[str, Any]:
    """COUNTS AND CLOSED WORDS ONLY. Never raises, presses nothing, decides
    nothing: the verification's fresh render decides.

    It is the one reading that can say a further step OPENED -- a dialog, a
    confirmation -- rather than only that the act did not land, and taking it
    is what a first supervised press exists for. For the withdraw it IS the
    capture of the confirmation LinkedIn documents.

    ``address_before`` is the page's address taken just before the press; the
    address now is compared with it, in a condition, and neither is returned.
    ``None`` -- either one unreadable -- reports ``address_moved`` as unknown.
    """
    out: dict[str, Any] = {
        "dialogs": 0,
        "alertdialogs": 0,
        "buttons_in_dialogs": 0,
        "dialog_buttons_by_word": {word: 0 for word in DIALOG_WORDS},
        "rows_for_target": 0,
        "address_moved": None,
        "error": None,
    }
    try:
        out["dialogs"] = await _count(page, VISIBLE_DIALOGS)
        out["alertdialogs"] = await _count(page, VISIBLE_ALERTDIALOGS)
        both = ":is([role=dialog], [role=alertdialog])"
        out["buttons_in_dialogs"] = await _count(page, f"{both} >> role=button")
        for word in DIALOG_WORDS:
            out["dialog_buttons_by_word"][word] = await _count(
                page, f'{both} >> role=button[name="{word}"s]'
            )
        out["rows_for_target"] = await _count(page, control_selector(action, segment))
        try:
            here: Optional[str] = str(page.url)
        except Exception:  # noqa: BLE001 - absent means "cannot tell"
            here = None
        out["address_moved"] = (
            None if (here is None or address_before is None) else here != address_before
        )
    except Exception as exc:  # noqa: BLE001 - the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def after_press_note(reading: dict[str, Any], action: str) -> dict[str, Any]:
    """The after-press reading as the receipt prints it: counts, closed words
    and one sentence. Whether the act landed is the verification's answer."""
    reading = reading if isinstance(reading, dict) else {}
    words = reading.get("dialog_buttons_by_word")
    words = words if isinstance(words, dict) else {}
    by_word = {word: coerce.as_count(words.get(word)) for word in DIALOG_WORDS}
    counts = {
        key: coerce.as_count(reading.get(key))
        for key in ("dialogs", "alertdialogs", "buttons_in_dialogs", "rows_for_target")
    }
    named = sum(by_word.values())
    moved = reading.get("address_moved")
    error = _error_kind(reading.get("error")) if reading.get("error") else None
    opened = counts["dialogs"] + counts["alertdialogs"]
    _tag, word = CONTROL.get(action, ("", "the control"))
    if error:
        sentence = (
            f"the page could not be read after the {word!r} press ({error}), so "
            "whether a further step opened is not known."
        )
    elif opened:
        sentence = (
            f"A FURTHER STEP OPENED AND WAS NOT TAKEN: {opened} visible dialog(s) "
            f"holding {counts['buttons_in_dialogs']} button(s) -- "
            f"{named} of them wearing a word on this server's closed list, "
            f"{max(counts['buttons_in_dialogs'] - named, 0)} not -- were on the "
            f"page after {word!r} was pressed, and NOTHING in them was pressed: "
            "this server has never seen that step and does not choose inside it. "
            "The fresh render below says whether the act landed; a confirmation "
            "left unanswered means it did not."
        )
    else:
        sentence = (
            f"no dialog was visible after {word!r} was pressed. The fresh render "
            "below says whether the act landed."
        )
    if moved is True:
        sentence += (
            " THE ADDRESS MOVED off the tab after the press: the control's own "
            "address took the browser elsewhere. The landing is withheld."
        )
    return {
        **counts,
        "dialog_buttons_by_word": by_word,
        "address_moved": moved if moved in (True, False) else None,
        "error": error,
        "further_step_opened": bool(opened) if not error else None,
        "what_this_means": sentence,
    }


def describe_target(action: str) -> str:
    """What the preview tells him he named, in words, with no name in them."""
    side = SIDE[action]
    return (
        f"the one pending invitation on your invitation manager's {side} tab "
        "whose row links the profile you gave, and no other member. The page "
        "confirmed it by a count; the person's name is not read -- check the "
        "link against linkedin_received_invitations or "
        "linkedin_sent_invitations before confirming."
    )
