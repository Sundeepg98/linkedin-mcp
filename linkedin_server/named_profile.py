"""A person the operator NAMES, reached through that person's own profile.

RULING ``THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET`` (the orchestrator,
2026-09-24, applying WRITE-CLASS-B and OPERATOR-NAMES-THE-TARGET; registered in
``_audit/2026-09-24-rulings-notify-veto-and-who-which.md``): a third party's
profile, ``/in/<slug>/``, may be loaded ONLY inside an outward act whose target
the operator names in that call -- the slug from the tool's arguments only,
never from page content, never for a measurement. It unblocks ``N 1``
(connect through the profile), ``N 4``, ``N 5`` (the note) and ``M M1`` /
``M M6`` (Message on the profile) as builds. Lane L5's follow-up, 2026-09-27.

WHAT LIVES HERE. Everything the two named-person acts need that is not the
write pipeline itself: the caller's target and the one address it composes,
the landing veto, the verdicts over :func:`dom.read_named_profile`'s integers,
the conversation a Message press opens, and the one step that prints WHOM the
act resolved to. ``writes.py`` holds the specs and calls in.

WHAT IS MEASURED AND WHAT IS NOT, because an act on a person is exactly where
a derived claim must not pass for a measured one. MEASURED over every capture
on disk (2026-09-27): the ``Invite <name> to connect`` control, a ``<button>``
44 times; the ``Message <name>`` control, an ``<a>`` 18 times and never a
``<button>``, on ``/messaging/compose/`` 16 times; the profile template's
topcard (his own, 6 captures) and its title. The reply form, its Send
transition and its message list (lane L5, 2026-09-24). NEVER CAPTURED: a third
party's profile at all; what Connect turns into once pressed; the invitation
dialog; what a profile's Message press opens; the composer a non-connection
gets. Every one of those is a VETO below -- the act refuses unless the page
shows the measured shape -- and each refusal reports what it found, so the
first supervised act on a person he names IS the capture. The record lists
them: ``_audit/2026-09-24-lane-l5-messaging.md``, "Follow-up: the named-person
route".

A PAGE MAY VETO, NEVER SUPPLY (``PAGE-MAY-VETO-NEVER-SUPPLY``). Nothing here
returns an address, an id or a name read off the page for anything to
navigate by. The landing is compared in a condition and withheld; a control
is pressed as THE ONLY CONTROL OF ITS KIND INSIDE THE OWNER'S TOPCARD -- which
the page's own script checks, with a comparison that never leaves the page --
by a selector that carries no name and no position, pressed strictly.
"""

from __future__ import annotations

import re
import time
from typing import Any, Optional
from urllib.parse import unquote, urlsplit

from linkedin_server import coerce, dom, people_seam, readonly, shape, threads
from linkedin_server.config import logger
from linkedin_server.errors import WriteAttemptError

# ---------------------------------------------------------------------------
# 1. The caller's target, and the one address it composes
# ---------------------------------------------------------------------------

#: A LinkedIn member id as it appears in a profile address or a urn. Matched
#: as a whole value; nothing is extracted from a longer string.
MEMBER_ID = re.compile(r"^ACoAA[A-Za-z0-9_\-]{10,80}$")
_MEMBER_URN = re.compile(r"^urn:li:(?:fsd_profile|member):(ACoAA[A-Za-z0-9_\-]{10,80})$")

#: LinkedIn's hosts as a profile link may spell them: the bare domain, ``www``,
#: or a two- or three-letter country host (``in.linkedin.com``). The address
#: this module COMPOSES is always ``www.linkedin.com``; the host is only
#: accepted on the way in.
_LINK_HOST = re.compile(r"^(?:www\.|[a-z]{2,3}\.)?linkedin\.com$")
_LINK_PATH = re.compile(r"^/in/([^/]+)/?$")


def profile_segment(value: Any) -> str:
    """The profile segment a caller's argument names, or raise.

    Accepted: a profile LINK (``https://www.linkedin.com/in/<segment>/``, with
    or without the scheme, ``www`` or a trailing slash; a query or fragment is
    dropped), a member id (``ACoAA...``), or a member urn. NEVER A NAME -- and
    that is enforced by shape rather than by trust: a bare word that is
    neither a link nor an id is refused, because a one-word name and a vanity
    segment are the same shape and this server will not guess which it was
    handed. A sub-page (``/in/<segment>/details/...``) is refused too: the link
    names WHO, and a longer path is not a longer who.
    """
    text = str(value if value is not None else "").strip()
    if not text:
        raise WriteAttemptError(
            "this act needs the profile of the person you name: their profile "
            "link or member id. Nothing was given."
        )
    if any(character.isspace() or ord(character) < 32 for character in text):
        raise WriteAttemptError(
            "the profile you gave contains a space or a control character, and "
            "a profile link or member id never does. A NAME IS NEVER ACCEPTED "
            "as the target: pass the person's profile link, "
            "https://www.linkedin.com/in/<segment>/, or their member id."
        )
    urn = _MEMBER_URN.fullmatch(text)
    if urn:
        return urn.group(1)
    if MEMBER_ID.fullmatch(text):
        return text
    looks_like_a_link = "/in/" in text or text.lower().startswith(
        ("http:", "https:", "linkedin.com", "www.linkedin.com")
    )
    if not looks_like_a_link:
        raise WriteAttemptError(
            "a bare word is not accepted as the person: it cannot be told "
            "from a name, and a name is never the target. Pass their profile "
            "link, https://www.linkedin.com/in/<segment>/, or their member id."
        )
    candidate = text if "://" in text else "https://" + text
    parts = urlsplit(candidate)
    if parts.scheme not in ("http", "https") or not _LINK_HOST.fullmatch(parts.netloc.lower()):
        raise WriteAttemptError(
            "the profile link you gave is not on LinkedIn's own host, so it "
            "names nobody this server may reach."
        )
    path = _LINK_PATH.fullmatch(parts.path or "")
    if not path:
        raise WriteAttemptError(
            "the link you gave is not a profile address of the form "
            "/in/<segment>/ -- a sub-page or another path names no person by "
            "itself. Pass the profile's own address."
        )
    segment = path.group(1)
    if not readonly.valid_named_profile_segment(segment) or segment.lower() == "me":
        raise WriteAttemptError(
            "the profile segment in the link you gave is not one this server "
            "can address (three to a hundred letters, digits, hyphens, "
            "underscores or percent-encoded non-ASCII letters -- an encoded "
            "space, slash or other ASCII character is refused), or it is your "
            "own /in/me/, which is not a person you name."
        )
    return segment


def profile_url(segment: str) -> str:
    """The ONE address a named act loads, composed by the boundary itself."""
    return readonly.named_profile_url(segment)


def landed_on_profile(landed: Any, segment: str) -> bool:
    """Did the browser land on THIS profile? A comparison, never an address.

    LinkedIn's own host, ``/in/<segment>/`` with or without the slash, the
    segment compared with percent-encoding and ASCII case folded -- vanity
    names are case-insensitive there. Anything else is a landing the page
    chose, and it VETOES the act: a member id LinkedIn redirects to a vanity
    address reads False here, and the act refuses rather than adopting an
    address the page supplied.
    """
    try:
        parts = urlsplit(str(landed or ""))
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc.lower() != "www.linkedin.com":
        return False
    path = _LINK_PATH.fullmatch(parts.path or "")
    if not path:
        return False
    return unquote(path.group(1)).casefold() == unquote(str(segment)).casefold()


# ---------------------------------------------------------------------------
# 2. What the profile draws, as the gate reads it
# ---------------------------------------------------------------------------

#: The states the two acts are valid FROM, the ones they aim at, and the ones
#: that mean "it did not happen".
CONNECT_FROM = "connect_control_drawn"
INVITATION_SENT = "invitation_sent"
CONNECT_STILL_DRAWN = "connect_control_still_drawn"
MESSAGE_FROM = "message_control_drawn"
MESSAGE_SENT = "message_sent"
MESSAGE_NOT_SENT = "message_not_sent"
UNKNOWN = "unknown"

#: The keys of :func:`dom.read_named_profile` a preview may print. Integers,
#: booleans and closed tokens -- nothing else is in that reading to print.
_FACT_KEYS = (
    "title_shape", "topcards", "topcard_headings", "heading_matches_title",
    "degree", "degree_tokens", "invite_controls", "invite_matches",
    "invite_in_topcard", "invite_controls_in_topcard", "message_controls",
    "message_matches", "message_tag", "message_href", "message_in_topcard",
    "message_controls_in_topcard", "more_actions", "dialogs",
    "composer_editors", "conversation_bubbles", "named_controls",
    "dialog_controls", "dialog_note_fields", "error",
)


def profile_facts(reading: dict[str, Any]) -> dict[str, Any]:
    """The reading as a confirm block prints it -- and as the capture a first
    supervised act records. Nothing in it names anybody."""
    out = {key: reading.get(key) for key in _FACT_KEYS}
    out["identity_confirmed"] = identity_confirmed(reading)
    return out


def identity_confirmed(reading: dict[str, Any]) -> bool:
    """Is this page the profile of the person its own title names?

    All three, each measured on his own profile and DERIVED on a third
    party's: the title is a profile title, there is exactly ONE topcard, and
    that topcard's first heading is the title's name -- compared in the page.
    """
    return (
        not reading.get("error")
        and reading.get("title_shape") == "profile"
        and coerce.as_count(reading.get("topcards")) == 1
        and reading.get("heading_matches_title") is True
    )


def _identity_why(reading: dict[str, Any]) -> str:
    if reading.get("error"):
        return f"the profile could not be read ({reading['error']})."
    return (
        "the page did not show one person's topcard in the shape this server "
        f"measured on your own profile: title shape {reading.get('title_shape')!r}, "
        f"{coerce.as_count(reading.get('topcards'))} topcard(s), first heading "
        f"matching the title: {reading.get('heading_matches_title')!r}. A third "
        "party's profile has never been captured, so this is the first reading "
        "of one -- NEEDS-CAPTURE C-P1 in the record -- and nothing is aimed at a "
        "page this server cannot identify."
    )


def _the_only_one_in_the_topcard(reading: dict[str, Any], key: str, kind: str) -> Optional[str]:
    """Why the topcard does not hold exactly ONE control of this kind, or None.

    THE PRESS CARRIES NO POSITION (see :func:`dom.topcard_invite_control_selector`):
    it is the topcard-scoped selector, pressed strictly, so it can only ever
    mean "the one control of this kind in the topcard". This is where that
    one is required -- whatever its label -- beside the page's own check that
    it is the owner's.
    """
    count = coerce.as_count(reading.get(key))
    if count == 1:
        return None
    return (
        f"the person's topcard draws {count} {kind} control(s) of any label, "
        "where exactly one -- theirs -- is the only shape this act presses: "
        "the press names no position, so a second control of the kind would "
        "leave it choosing, and it is pressed strictly so that one appearing "
        "mid-press stops it. Where a third party's profile draws its own "
        "controls has never been captured (NEEDS-CAPTURE C-P1)."
    )


def connect_state(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` -- is there exactly one Connect for THIS person?

    ``connect_control_drawn`` needs the identity confirmed, exactly one control
    named ``Invite <owner> to connect`` on the page (compared in the page),
    that one INSIDE the owner's topcard and the ONLY Connect-shaped control
    there, and no dialog already open. Nothing about the control crosses: the
    press is :func:`dom.topcard_invite_control_selector`, pressed strictly.
    (It carried a POSITION -- first in the whole page's list, then in the
    topcard's -- until two re-checks of 2026-09-27 showed a re-render could
    hand either position to a stranger's control.)
    """
    if not identity_confirmed(reading):
        return UNKNOWN, _identity_why(reading)
    matches = coerce.as_count(reading.get("invite_matches"))
    if matches == 0:
        degree = reading.get("degree")
        return UNKNOWN, (
            "this person's profile draws no Connect control naming them "
            f"(degree read: {degree!r}; {coerce.as_count(reading.get('more_actions'))} "
            "'More actions' control(s)). You may already be connected, an "
            "invitation may be pending, or Connect sits inside the 'More' menu -- "
            "which has never been captured and which this act does not open. "
            "NEEDS-CAPTURE C-P1."
        )
    if matches > 1:
        return UNKNOWN, (
            f"{matches} controls are named for inviting this person, and that "
            "is a refusal rather than a choice: pressing one would be choosing "
            "by position."
        )
    if coerce.as_count(reading.get("invite_in_topcard")) != 1:
        return UNKNOWN, (
            "the one control named for inviting this person is NOT inside "
            "their topcard. It may belong to somebody else with the same name "
            "-- a card in 'People also viewed', say -- and an invitation there "
            "would reach a stranger. Where a third party's profile draws its "
            "own Connect has never been captured (NEEDS-CAPTURE C-P1)."
        )
    why_not = _the_only_one_in_the_topcard(reading, "invite_controls_in_topcard", "Connect")
    if why_not:
        return UNKNOWN, why_not
    if coerce.as_count(reading.get("dialogs")):
        return UNKNOWN, (
            f"{coerce.as_count(reading.get('dialogs'))} dialog(s) are already "
            "open on the profile. Connect is not pressed underneath one."
        )
    return CONNECT_FROM, (
        "exactly one control named for inviting this person to connect -- the "
        "label shape measured 44 times on other surfaces -- and it is the only "
        "Connect control in the topcard of a page that names the same person. "
        "PRESSING IT MAY SEND THE INVITATION AT ONCE, with no further step: that "
        "is how Connect is known to behave, and this is the last point at which "
        "nothing has happened."
    )


def message_state(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` -- is there exactly one Message for THIS person, of a
    shape this act may press?

    Pressable: a ``<button>``, or an ``<a>`` whose address is the composer --
    the destination measured on 16 of the 18 Message controls captured. A link
    anywhere else would navigate to an address the page supplied, which
    PAGE-MAY-VETO-NEVER-SUPPLY forbids. It must be the only Message-shaped
    control in the owner's topcard, for :func:`connect_state`'s reason. And no
    conversation composer may already be open: the one that opens must be the
    one this act types into.
    """
    if not identity_confirmed(reading):
        return UNKNOWN, _identity_why(reading)
    matches = coerce.as_count(reading.get("message_matches"))
    if matches != 1:
        return UNKNOWN, (
            f"{matches} Message control(s) are named for this person, where "
            "exactly one is the only aimable number. None may mean the profile "
            "draws Message only for connections, or in a menu never captured "
            "(NEEDS-CAPTURE C-P4)."
        )
    if coerce.as_count(reading.get("message_in_topcard")) != 1:
        return UNKNOWN, (
            "the one Message control named for this person is NOT inside "
            "their topcard. It may belong to somebody else with the same name, "
            "and a message there would reach a stranger. Where a third party's "
            "profile draws its own Message has never been captured "
            "(NEEDS-CAPTURE C-P1)."
        )
    why_not = _the_only_one_in_the_topcard(reading, "message_controls_in_topcard", "Message")
    if why_not:
        return UNKNOWN, why_not
    tag = reading.get("message_tag")
    href = reading.get("message_href")
    if tag not in ("a", "button") or (tag == "a" and href != "compose"):
        return UNKNOWN, (
            f"the Message control is a {tag!r} with destination {href!r}. A "
            "link that is not the composer would take the browser to an "
            "address the page chose, and that is refused before anything is "
            "pressed (PAGE-MAY-VETO-NEVER-SUPPLY). NEEDS-CAPTURE C-P4."
        )
    if coerce.as_count(reading.get("composer_editors")):
        return UNKNOWN, (
            f"{coerce.as_count(reading.get('composer_editors'))} conversation "
            "composer(s) are already open on this page. Close them first: the "
            "composer this act types into must be the one its own press opens."
        )
    degree = reading.get("degree")
    return MESSAGE_FROM, (
        "exactly one Message control named for this person, the only one in "
        "their topcard, of a shape this act may press, and no composer "
        "already open."
        + (
            " The profile reads '1st': the words are typed only if, after the "
            "press, exactly one empty composer sits in a conversation titled "
            "with exactly that person's name."
            if degree == "1st"
            else f" THE PROFILE READS DEGREE {degree!r}, NOT '1st': confirming "
            "will press Message, record what opens, and STOP BEFORE TYPING -- "
            "a message to anyone who is not a first-degree connection may be "
            "an InMail that spends a credit, and that composer has never been "
            "captured (NEEDS-CAPTURE C-P5). Nothing will be sent."
        )
    )


# ---------------------------------------------------------------------------
# 3. Connect: did it land? Read on a FRESH render of the same profile
# ---------------------------------------------------------------------------


def connect_verdict(
    before: dict[str, Any], in_place: dict[str, Any], fresh: dict[str, Any]
) -> tuple[str, str]:
    """``(state, why)`` for a Connect press. Its NEGATIVE is strong; its
    positive is never claimed.

    ``before`` is the preview's facts, ``in_place`` the page right after the
    press (before any reload), ``fresh`` a new render of the profile he named.
    The Connect control for this person drawn again on the fresh render means
    NO INVITATION WAS SENT. Gone means it changed into something this server
    has never seen, and that is reported as unknown with what it became, as
    closed tokens -- the capture that lets a later build name the sent state
    (NEEDS-CAPTURE C-P2).
    """
    dialogs_before = coerce.as_count(before.get("dialogs"))
    dialogs_after = coerce.as_count(in_place.get("dialogs"))
    opened = dialogs_after > dialogs_before
    dialog_note = (
        f" A DIALOG OPENED after the press ({dialogs_before} before, "
        f"{dialogs_after} after), drawing controls read as "
        f"{list(in_place.get('dialog_controls') or [])} and "
        f"{coerce.as_count(in_place.get('dialog_note_fields'))} note field(s) "
        "(closed tokens and a count, read in the page), and nothing in it was "
        "pressed -- it has never been captured (NEEDS-CAPTURE C-P3); the "
        "reload discarded it."
        if opened
        else " No dialog opened after the press."
    )
    # WHAT THE PRESS LEFT IN PLACE, and why a fresh render alone cannot say
    # NOT SENT (the second warm re-check, 2026-09-27). The strict press binds
    # the COUNT of Connect controls in the topcard, not the person: if the
    # page replaced this person's control IN PLACE with somebody else's while
    # the press waited, the one match was the other person's, and a fresh
    # render then draws this person's Connect again -- which used to read NO
    # INVITATION WAS SENT while an invitation went to someone else. So when,
    # right after the press, the page draws NO control naming this person at
    # all -- their Connect gone, and nothing it turned into -- the press
    # cannot be shown to have been theirs, and the verdict is unknown.
    if (
        identity_confirmed(in_place)
        and coerce.as_count(in_place.get("invite_matches")) == 0
        and not list(in_place.get("named_controls") or [])
    ):
        return UNKNOWN, (
            "right after the press, the page drew NO control naming this "
            "person -- their Connect was gone and nothing naming them took "
            "its place -- so this server cannot show that the control pressed "
            "was theirs: a control redrawn in its place while the press waited "
            "would have been pressed instead. What a pressed Connect becomes "
            "has never been captured (NEEDS-CAPTURE C-P2)."
            + dialog_note
            + " Look at My Network > Manage > Sent before doing anything else. "
            "DO NOT RETRY."
        )
    if not identity_confirmed(fresh):
        return UNKNOWN, (
            "the fresh render did not show the named person's topcard in the "
            "measured shape, so it says nothing about the invitation."
            + dialog_note
            + " Open your Sent invitations and look before doing anything else."
        )
    # THE OWNER'S OWN CONNECT, counted inside the topcard -- the only place
    # the act would press one. A same-name control elsewhere on the page is
    # somebody else's and says nothing about this invitation.
    still = coerce.as_count(fresh.get("invite_in_topcard"))
    tokens = list(fresh.get("named_controls") or [])
    if still == 1:
        return CONNECT_STILL_DRAWN, (
            "a FRESH render of the profile you named draws the Connect control "
            "for this person again, so NO INVITATION WAS SENT." + dialog_note
        )
    if still == 0:
        return UNKNOWN, (
            "the Connect control for this person is no longer drawn on a fresh "
            f"render; controls naming them now read as {tokens} (closed "
            "tokens). What a sent invitation leaves on a profile has never been "
            "captured, so this server does NOT call it sent -- that is "
            "NEEDS-CAPTURE C-P2, and this receipt is its first reading."
            + dialog_note
            + " Look at My Network > Manage > Sent. DO NOT RETRY: a second "
            "press on a control that changed is not the same act."
        )
    return UNKNOWN, (
        f"{still} Connect controls for this person on the fresh render, where "
        "one or none are the only readable answers." + dialog_note
    )


# ---------------------------------------------------------------------------
# 4. Message: the conversation the press opens, and the send inside it
# ---------------------------------------------------------------------------
#
# THE REPLY FORM IS MEASURED; WHERE IT OPENS FROM A PROFILE IS NOT. Lane L5
# measured the conversation's form, its Send drawn DISABLED while empty, and
# its message list, on the composer and the thread pages -- inside ``main``.
# A profile's Message press is expected to open the same form in LinkedIn's
# conversation overlay, OUTSIDE ``main``, and that has never been captured.
# So these readers are PAGE-WIDE and the gate is strict: no composer before
# the press, exactly one after, inside exactly one overlay conversation WHOSE
# TITLE READS EXACTLY THE NAMED PERSON'S NAME, no recipient box, empty, Send
# disabled. Anything else stops before a word is typed, and the reading is
# the capture (NEEDS-CAPTURE C-P4).
#
# WHOSE CONVERSATION WAS ADDED BY THE COLD RE-CHECK OF 2026-09-27. Counts
# alone -- none before the press, one after -- could not tell a conversation
# the press opened with the named person from one headed by somebody else:
# a press that opened another person's conversation, and a press that opened
# nothing while a restored conversation appeared, both took his words and
# read SENT. The title is compared in the page (``dom.NAMED_PROFILE_JS``) and
# only a boolean crosses.

BUBBLE_SELECTOR = dom.OVERLAY_BUBBLE
COMPOSER_EDITOR_SELECTOR = dom.OVERLAY_COMPOSER_EDITOR
COMPOSER_SEND_SELECTOR = 'form.msg-form button.msg-form__send-button[type="submit"]'

#: HOW LONG THE GATE WAITS for a composer to be drawn after the Message press,
#: before it reads. A LIVENESS BOUND, NOT A SAFETY ONE: the gate refuses on
#: whatever it then finds, so a composer drawn later than this only means the
#: act stops having typed nothing. How long LinkedIn's overlay takes to draw is
#: part of NEEDS-CAPTURE C-P4, which the receipt records as ``composer_waited_ms``.
OPENED_COMPOSER_WAIT_MS = 3_000
_PAGE_RECIPIENT_BOX_SELECTOR = (
    '.msg-connections-typeahead [role="combobox"], '
    "input.msg-connections-typeahead__search-field"
)
_EVENT = "li.msg-s-message-list__event"

#: WORDS THAT WOULD SAY A COMPOSER SPENDS SOMETHING -- NEEDS-CAPTURE C-P5's
#: first reading. Matched inside the opened overlay conversation and returned
#: as BOOLEANS: whether an element there says "InMail", or "credit". A HINT
#: for the capture and nothing more: no gate reads them, and they may match a
#: message body as easily as a notice.
_INMAIL_WORD = re.compile(r"\bInMail\b", re.I)
_CREDIT_WORD = re.compile(r"\bcredits?\b", re.I)


def _normalise(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


async def wait_for_opened_composer(
    page: Any, *, timeout_ms: Optional[int] = None
) -> dict[str, Any]:
    """After the Message press: wait, BOUNDED, for a composer to be drawn.

    The gate read the page the instant the press returned, and an overlay
    drawn a moment later was refused as "not one conversation" -- safe, and
    an act that could not proceed on the page it was built for (the cold
    re-check's liveness note, 2026-09-27). This waits up to
    :data:`OPENED_COMPOSER_WAIT_MS` for :data:`COMPOSER_EDITOR_SELECTOR` to be
    attached and DECIDES NOTHING: the gate still reads everything and refuses
    on what it finds. ``failure`` is an exception's TYPE only.
    """
    bound = OPENED_COMPOSER_WAIT_MS if timeout_ms is None else int(timeout_ms)
    out: dict[str, Any] = {"appeared": False, "waited_ms": 0, "failure": None}
    started = time.monotonic()
    try:
        await page.locator(COMPOSER_EDITOR_SELECTOR).first.wait_for(
            state="attached", timeout=bound
        )
        out["appeared"] = True
    except Exception as exc:  # noqa: BLE001 - a timeout is a reading, not a fault
        out["failure"] = type(exc).__name__
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


async def read_opened_conversation(page: Any, *, text: Optional[str] = None) -> dict[str, Any]:
    """The conversation a Message press opened, as counts, booleans and tokens.

    ``text`` is HIS words; it is compared inside the page and only counts come
    back, exactly as :func:`threads.read_thread` does it. The conversation is
    the one overlay bubble that holds the composer, and its messages are
    counted inside that bubble only.
    """
    out: dict[str, Any] = {
        "editors": 0,
        "send_controls": 0,
        "recipient_boxes": 0,
        "bubbles": 0,
        "bubbles_with_editor": 0,
        "editor_empty": None,
        "send_disabled": None,
        "events": 0,
        "events_with_text": None,
        "last_from": "unknown",
        "last_has_text": None,
        "inmail_words": None,
        "credit_words": None,
        "error": None,
    }
    try:
        editors = page.locator(COMPOSER_EDITOR_SELECTOR)
        out["editors"] = coerce.as_count(await editors.count())
        sends = page.locator(COMPOSER_SEND_SELECTOR)
        out["send_controls"] = coerce.as_count(await sends.count())
        out["recipient_boxes"] = coerce.as_count(
            await page.locator(_PAGE_RECIPIENT_BOX_SELECTOR).count()
        )
        bubbles = page.locator(BUBBLE_SELECTOR)
        out["bubbles"] = coerce.as_count(await bubbles.count())
        out["inmail_words"] = coerce.as_count(await bubbles.get_by_text(_INMAIL_WORD).count()) > 0
        out["credit_words"] = coerce.as_count(await bubbles.get_by_text(_CREDIT_WORD).count()) > 0
        holding = bubbles.filter(has=page.locator(COMPOSER_EDITOR_SELECTOR))
        out["bubbles_with_editor"] = coerce.as_count(await holding.count())
        if out["editors"] == 1:
            out["editor_empty"] = _normalise(await editors.first.inner_text()) == ""
        if out["send_controls"] == 1:
            out["send_disabled"] = bool(await sends.first.is_disabled())
        if out["bubbles_with_editor"] == 1:
            bubble = holding.first
            events = bubble.locator(_EVENT)
            count = coerce.as_count(await events.count())
            out["events"] = count
            if count:
                last = events.nth(count - 1)
                items = coerce.as_count(await last.locator(threads.ITEM_SELECTOR).count())
                others = coerce.as_count(
                    await last.locator(threads.OTHER_ITEM_SELECTOR).count()
                )
                if items == 1 and others == 1:
                    out["last_from"] = "other"
                elif items == 1 and others == 0:
                    out["last_from"] = "him"
                if text is not None:
                    matcher = page.get_by_text(_normalise(text), exact=True)
                    out["events_with_text"] = coerce.as_count(
                        await events.filter(has=matcher).count()
                    )
                    out["last_has_text"] = (
                        coerce.as_count(await last.filter(has=matcher).count()) == 1
                    )
            elif text is not None:
                out["events_with_text"] = 0
                out["last_has_text"] = False
    except Exception as exc:  # noqa: BLE001 - reported as a type, never raised
        out["error"] = type(exc).__name__
        logger.debug("opened conversation unreadable: %s", type(exc).__name__)
    return out


def opened_conversation_gate(
    profile_after: dict[str, Any],
    conversation: dict[str, Any],
    *,
    still_on_the_profile: bool,
    composer_wait: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """After the Message press, BEFORE a word is typed: may the words go in?

    ``profile_after`` is :func:`dom.read_named_profile` re-read after the
    press, ``conversation`` :func:`read_opened_conversation` with his words,
    ``composer_wait`` what :func:`wait_for_opened_composer` saw (recorded,
    never decided on). ``proceed`` needs ALL of, and refuses IN THIS ORDER:

    1. the browser is still on the profile he named -- a press that navigated
       went to an address the page chose;
    2. the profile still names the same person;
    3. its degree reads ``1st``. A message to anyone else may be an InMail
       that spends one of his credits, or a message request, and neither
       composer has ever been captured: the act stops here, having pressed
       Message and typed nothing, and this reading is ``M M6``'s capture
       (NEEDS-CAPTURE C-P5);
    4. the page could be read;
    5. exactly one composer on the page, inside exactly one overlay
       conversation, with one Send;
    6. THAT CONVERSATION IS THE NAMED PERSON'S: its one title reads exactly
       the name the profile's own title gives, compared in the page. Added
       by the cold re-check of 2026-09-27 -- see this section's head;
    7. no recipient box;
    8. empty, and its Send DISABLED -- the measured empty state of the form
       (NEEDS-CAPTURE C-P4 otherwise);
    9. the number of messages already carrying his exact words was counted
       -- the before-count the SENT verdict diffs against.
    """
    waited = composer_wait or {}
    observed = {
        "still_on_the_profile": bool(still_on_the_profile),
        "identity_confirmed": identity_confirmed(profile_after),
        "degree": profile_after.get("degree"),
        "editors": conversation.get("editors"),
        "bubbles": conversation.get("bubbles"),
        "bubbles_with_editor": conversation.get("bubbles_with_editor"),
        # WHOSE CONVERSATION: the holding bubble's titles, counted, and
        # whether its one title reads exactly the owner's name -- both from
        # the page's own comparison, so no name crosses.
        "conversation_titles": profile_after.get("bubble_titles"),
        "conversation_names_the_owner": profile_after.get("bubble_title_names_owner"),
        "recipient_boxes": conversation.get("recipient_boxes"),
        "editor_empty": conversation.get("editor_empty"),
        "send_controls": conversation.get("send_controls"),
        "send_disabled": conversation.get("send_disabled"),
        "events": conversation.get("events"),
        "events_with_text": conversation.get("events_with_text"),
        # C-P4 and C-P5's first readings: hints only, and no condition below
        # reads them -- whether the one title CONTAINS the owner's name (a
        # title that reads more than the name), how long the composer took
        # to be drawn, and whether the opened conversation says "InMail" or
        # "credit".
        "title_contains_the_owner": profile_after.get("bubble_title_contains_owner"),
        "composer_appeared": waited.get("appeared"),
        "composer_waited_ms": waited.get("waited_ms"),
        "inmail_words": conversation.get("inmail_words"),
        "credit_words": conversation.get("credit_words"),
        "error": conversation.get("error") or profile_after.get("error"),
    }
    out: dict[str, Any] = {
        "proceed": False,
        "refused_condition": None,
        "why": "",
        "observed": observed,
    }
    if not still_on_the_profile:
        out["refused_condition"] = "1_navigated_away"
        out["why"] = (
            "the Message press took the browser away from the profile you "
            "named, to an address the page chose. Nothing was typed."
        )
        return out
    if not observed["identity_confirmed"]:
        out["refused_condition"] = "2_identity_lost"
        out["why"] = (
            "after the press the page no longer shows the named person's "
            "topcard in the measured shape. Nothing was typed."
        )
        return out
    if observed["degree"] != "1st":
        out["refused_condition"] = "3_not_a_first_degree_connection"
        out["why"] = (
            f"the profile's degree reads {observed['degree']!r}, not '1st'. A "
            "message to someone who is not a first-degree connection may be an "
            "InMail that spends one of your credits, or a message request, and "
            "the composer either opens has never been captured. Message was "
            "pressed and NOTHING WAS TYPED; the counts in this block are the "
            "capture (NEEDS-CAPTURE C-P5)."
        )
        return out
    if observed["error"]:
        out["refused_condition"] = "4_unreadable"
        out["why"] = (
            f"the opened conversation could not be read ({observed['error']}). "
            "Nothing was typed."
        )
        return out
    if (
        coerce.as_count(observed["editors"]) != 1
        or coerce.as_count(observed["bubbles_with_editor"]) != 1
        or coerce.as_count(observed["send_controls"]) != 1
    ):
        out["refused_condition"] = "5_not_one_conversation"
        out["why"] = (
            f"{observed['editors']} composer(s), {observed['bubbles_with_editor']} "
            f"overlay conversation(s) holding one, {observed['send_controls']} "
            "Send control(s): exactly one of each is the only shape this act "
            "types into, and what a profile's Message press opens has never "
            "been captured (NEEDS-CAPTURE C-P4). Nothing was typed."
        )
        return out
    if observed["conversation_names_the_owner"] is not True:
        out["refused_condition"] = "6_not_their_conversation"
        out["why"] = (
            "the one conversation holding a composer is not headed by the "
            "person you named: it draws "
            f"{coerce.as_count(observed['conversation_titles'])} title(s), and "
            "none reads exactly the name on the profile (compared in the page; "
            "the title contains that name: "
            f"{observed['title_contains_the_owner']!r}). A conversation this "
            "press did not open, or somebody else's, would take your words to "
            "a person you did not name. How a person's conversation title is "
            "drawn has never been captured (NEEDS-CAPTURE C-P4). Nothing was "
            "typed."
        )
        return out
    if coerce.as_count(observed["recipient_boxes"]):
        out["refused_condition"] = "7_recipient_box"
        out["why"] = (
            f"{observed['recipient_boxes']} recipient box(es) are drawn: this is "
            "a new-message composer with nobody committed, not a conversation "
            "with the person you named. Nothing was typed."
        )
        return out
    if observed["editor_empty"] is not True or observed["send_disabled"] is not True:
        out["refused_condition"] = "8_not_empty"
        out["why"] = (
            "the composer is not in the measured empty state -- it holds text, "
            "or Send is already enabled, most likely a draft LinkedIn restored. "
            "A fill REPLACES, and this will not type over words it cannot read "
            "back. Nothing was typed."
        )
        return out
    if not isinstance(observed["events_with_text"], int):
        out["refused_condition"] = "9_no_before_count"
        out["why"] = (
            "the number of messages already carrying your words could not be "
            "counted, and the SENT verdict needs it. Nothing was typed."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "still on the profile you named, a first-degree connection, and "
        "exactly one conversation composer after the press, in a conversation "
        "whose title reads exactly that person's name: empty, Send disabled, "
        "no recipient box."
    )
    return out


async def composer_send_gate(page: Any, *, text: str) -> dict[str, Any]:
    """May Send be pressed? :func:`threads.reply_send_gate`'s conditions, on
    the page-wide composer the Message press opened -- and one more.

    The same five refusals in the same order -- no recipient box, one
    editor, one Send, the fill landed (Send enabled, box not empty), and the
    box holds EXACTLY his words -- so a message on this route is held to the
    bar a reply is. THEN A SIXTH, added by the cold re-check of 2026-09-27:
    with his words in the box and nothing pressed, the conversation holding
    them must STILL be the one whose title reads exactly the named person's
    name, compared in the page by :data:`dom.NAMED_PROFILE_JS`. The opened
    gate checked it before the fill; this is the last moment it can be
    checked before the message is irreversible.
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": COMPOSER_SEND_SELECTOR,
        "observed": {},
        "why": "",
        "refused_condition": None,
    }
    try:
        editors = page.locator(COMPOSER_EDITOR_SELECTOR)
        sends = page.locator(COMPOSER_SEND_SELECTOR)
        observed = {
            "editors": coerce.as_count(await editors.count()),
            "send_controls": coerce.as_count(await sends.count()),
            "recipient_boxes": coerce.as_count(
                await page.locator(_PAGE_RECIPIENT_BOX_SELECTOR).count()
            ),
            "send_enabled": None,
            "editor_empty": None,
            "words_exact": None,
            "held_characters": None,
            "grant_characters": len(_normalise(text)),
        }
        if observed["send_controls"] == 1:
            observed["send_enabled"] = bool(await sends.first.is_enabled())
        if observed["editors"] == 1:
            held = _normalise(await editors.first.inner_text())
            observed["editor_empty"] = held == ""
            observed["words_exact"] = held == _normalise(text)
            observed["held_characters"] = len(held)
        # WHOSE CONVERSATION, read by the page's own script: a count and two
        # booleans cross, never the title.
        again = await dom.read_named_profile(page)
        observed["conversation_titles"] = again.get("bubble_titles")
        observed["conversation_names_the_owner"] = (
            not again.get("error") and again.get("bubble_title_names_owner") is True
        )
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the composer could not be read after the fill "
            f"({type(exc).__name__}). Send was not pressed."
        )
        return out
    out["observed"] = observed
    if observed["recipient_boxes"]:
        out["refused_condition"] = "1_not_a_conversation"
        out["why"] = (
            f"{observed['recipient_boxes']} recipient box(es) after the fill. "
            "Send was not pressed."
        )
        return out
    if observed["editors"] != 1:
        out["refused_condition"] = "2_editor_count"
        out["why"] = f"{observed['editors']} composer(s) after the fill. Send was not pressed."
        return out
    if observed["send_controls"] != 1:
        out["refused_condition"] = "3_send_count"
        out["why"] = (
            f"{observed['send_controls']} Send control(s) after the fill. Send "
            "was not pressed."
        )
        return out
    if observed["send_enabled"] is not True or observed["editor_empty"] is not False:
        out["refused_condition"] = "4_fill_not_landed"
        out["why"] = (
            "Send is not enabled, or the box reads empty, after the fill; the "
            "words did not land. Send was not pressed."
        )
        return out
    if observed["words_exact"] is not True:
        out["refused_condition"] = "5_words_not_exact"
        out["why"] = (
            "Send turned on, but the box does not hold exactly the words you "
            f"confirmed ({observed['held_characters']} characters in the box, "
            f"{observed['grant_characters']} confirmed). A message cannot be "
            "taken back. Send was not pressed."
        )
        return out
    if observed["conversation_names_the_owner"] is not True:
        out["refused_condition"] = "6_not_their_conversation"
        out["why"] = (
            "your words are in the box, but the conversation holding them is "
            "no longer one whose title reads exactly the name of the person "
            f"you named ({coerce.as_count(observed['conversation_titles'])} "
            "title(s) drawn). A message cannot be taken back. Send was not "
            "pressed, and the words are still in the composer on your screen."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "the composer holds exactly the words you confirmed and Send went from "
        "disabled to enabled, in the conversation whose title reads exactly "
        "the name of the person you named. No recipient box is drawn."
    )
    return out


async def composer_holds(page: Any, text: str) -> Optional[bool]:
    """In place, after the attempt: does the composer still hold his words?

    ``True`` when exactly one composer holds exactly ``text`` and Send is
    still enabled -- words never dispatched. ``False`` when it is empty.
    ``None`` when it cannot be told.
    """
    try:
        editors = page.locator(COMPOSER_EDITOR_SELECTOR)
        if coerce.as_count(await editors.count()) != 1:
            return None
        held = _normalise(await editors.first.inner_text())
        sends = page.locator(COMPOSER_SEND_SELECTOR)
        enabled = (
            bool(await sends.first.is_enabled())
            if coerce.as_count(await sends.count()) == 1
            else None
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("composer unreadable: %s", type(exc).__name__)
        return None
    if held == "":
        return False
    if held == _normalise(text) and enabled is True:
        return True
    return None


def message_verdict(
    opened: Optional[dict[str, Any]],
    after: dict[str, Any],
    *,
    held_in_place: Optional[bool],
    typed: bool,
    conversation_is_theirs: Optional[bool] = None,
) -> tuple[str, str]:
    """``(state, why)`` for a Message sent from a profile. IN PLACE, WITH A
    BEFORE-COUNT, and weaker than a reply's verdict for a stated reason.

    A reply is confirmed on a FRESH LOAD of the conversation its caller named.
    This conversation's address is on the page -- page-derived -- and this
    route never navigates to it (PAGE-MAY-VETO-NEVER-SUPPLY). So it is read
    where it opened, and the before-count taken when it opened is what lets it
    say more than ``send_message``'s in-place reading can: the number of
    messages carrying exactly his words must rise by EXACTLY ONE, and his
    words must be the last message, with no ``--other`` modifier.
    """
    if not typed or opened is None or not opened.get("proceed"):
        why = (opened or {}).get("why") or "the act stopped before typing."
        return MESSAGE_NOT_SENT, "NOTHING WAS TYPED, SO NOTHING WAS SENT: " + str(why)
    if held_in_place is True:
        return MESSAGE_NOT_SENT, (
            "the composer still holds your words with Send enabled: NOTHING "
            "WAS DISPATCHED. The words are still in the composer on your screen."
        )
    if after.get("error"):
        return UNKNOWN, (
            f"the conversation could not be re-read after Send ({after['error']}). "
            "Open it and look. Do NOT retry: a retry on a message that landed "
            "sends it twice."
        )
    # WHOSE CONVERSATION, ONE LAST TIME (the second warm re-check,
    # 2026-09-27): the strict Send press binds the COUNT of Send controls,
    # not the conversation, so a conversation swapped in place while the press
    # waited would have been the one sent from. If the conversation holding
    # the composer after Send is not titled with this person's name, nothing
    # read in it speaks for this message.
    if conversation_is_theirs is not True:
        return UNKNOWN, (
            "after Send, the conversation holding the composer is NOT titled "
            "with the name of the person you named (compared in the page), so "
            "what was sent, and to whom, cannot be read from it: a conversation "
            "redrawn in place while the press waited would have been the one "
            "sent from. Open your messages and look now. Do NOT retry."
        )
    was = (opened.get("observed") or {}).get("events_with_text")
    now = after.get("events_with_text")
    if not isinstance(was, int) or not isinstance(now, int):
        return UNKNOWN, (
            "a before- or after-count of messages carrying your exact words is "
            "missing, so no delta can be computed. Open the conversation and "
            "look. Do NOT retry."
        )
    if after.get("last_from") == "him" and after.get("last_has_text") is True and now == was + 1:
        return MESSAGE_SENT, (
            "read IN PLACE, in the conversation the press opened: your words "
            "are its last message, carrying no '--other' modifier, and the "
            f"number of messages carrying exactly those words went from {was} "
            f"to {now}. Not a fresh load -- this conversation's address is "
            "page-supplied and this route never navigates to it -- so it is the "
            "page's own redraw that says so, with a before-count behind it."
        )
    return UNKNOWN, (
        f"messages carrying your exact words: {was} before, {now} after; last "
        f"message from: {after.get('last_from')}; last carries your words: "
        f"{after.get('last_has_text')}; composer held them in place: "
        f"{held_in_place}. That combination proves neither outcome. Open the "
        "conversation and look. Do NOT retry: a retry on a message that landed "
        "sends it twice."
    )


# ---------------------------------------------------------------------------
# 5. WHOM the act resolved to -- in the confirm block and nowhere else
# ---------------------------------------------------------------------------

#: The notification count some titles lead with -- ``(3) `` -- measured on 21
#: of 95 captures. The same rule :data:`dom.NAMED_PROFILE_JS` applies in the
#: page, so both languages read one name out of one title.
_COUNT_PREFIX = re.compile(r"^\(\d+\)\s*")

#: A topcard line that is ONLY a connection degree, with or without the middle
#: dot -- the same shape :data:`dom.NAMED_PROFILE_JS` reads the degree from.
#: DERIVED: no capture holds a third party's topcard. Dropped before the
#: topcard parser runs, because that parser, measured on his own profile
#: (which draws no degree), would otherwise take it for the headline.
_DEGREE_LINE = re.compile(r"(?:\u00b7\s*)?(?:1st|2nd|3rd\+?)")


async def name_the_profile_target(
    page: Any, spec: Any, observation: Any, block: dict[str, Any], *, segment: str
) -> dict[str, Any]:
    """Print WHOM this act resolved to, in the confirm block and nowhere else.

    PEOPLE-DATA-MITIGATIONS item 6: "An outward act fires at the exact member
    the operator names, by link or id, and the tool reports whom it resolved
    before it acts." The four declared fields -- name, headline, link,
    degree -- through :mod:`people_seam`, which is where lane G's sanitiser and
    marker adopt them (mitigation 2, PENDING until that merge).

    THE SAME DISCIPLINE AS ``_name_the_invitation_recipient`` and
    ``threads.name_the_reply_recipient``: added to a NEW dict after
    ``grant.preview`` was assigned, so the retained block never held it; never
    in the grant's target, which stays the caller's link; never in the
    observation; never in a log. NO SECOND LOAD: the preview's load is still
    on screen, and a re-read must still confirm the same person before
    anything is read off it.

    THE NAME AND HEADLINE ARE READ WITH THE READER ``linkedin_my_profile``
    USES on his own profile -- ``dom.read_profile_fields`` and
    ``shape.parse_profile_topcard`` -- measured on that template. On a third
    party's page that reading is DERIVED and this block says so.
    """
    facts = dict(getattr(observation, "facts", None) or {})
    out = dict(block)
    if facts.get("landed_on_the_named_profile") is not True or facts.get(
        "identity_confirmed"
    ) is not True:
        out["whom_this_resolves_to"] = None
        out["whom_this_resolves_to_why"] = (
            "the preview did not confirm one person's profile, so there is "
            "nobody to name and nothing to confirm."
        )
        return out
    person = None
    try:
        again = await dom.read_named_profile(page)
        if identity_confirmed(again):
            fields = await dom.read_profile_fields(page)
            # THE TITLE WITHOUT ITS NOTIFICATION COUNT, which 21 of 95
            # captures carry as a leading "(N) " -- otherwise the topcard is
            # not found BY NAME and the first section stands in for it.
            title = _COUNT_PREFIX.sub("", str(fields.get("title") or ""))
            top = shape.pick_topcard(fields.get("sections") or [], title)
            lines = [
                line
                for line in (top or {}).get("lines") or []
                if not _DEGREE_LINE.fullmatch(str(line).strip())
            ]
            parsed = shape.parse_profile_topcard(lines)
            # THE NAME READ MUST BE THE NAME THE TITLE GIVES. The page's own
            # script already compared the topcard's heading with the title;
            # this holds the reader's first line to the same name, so a
            # section picked by position rather than by name names nobody.
            wanted = shape.name_from_title(title)
            if wanted and str(parsed.get("name") or "").casefold() == wanted.casefold():
                person = people_seam.person(
                    name=parsed.get("name"),
                    headline=parsed.get("headline"),
                    href=profile_url(segment),
                    degree=facts.get("degree"),
                )
    except Exception as exc:  # noqa: BLE001 - a read for a human, never raised
        logger.debug("named profile identity unreadable: %s", type(exc).__name__)
        person = None
    out["whom_this_resolves_to"] = person
    out["whom_this_resolves_to_why"] = (
        "READ OFF THE PROFILE YOU NAMED, already on screen from this preview's "
        "load, with the reader measured on your own profile's topcard -- on a "
        "third party's page that reading is derived, so CHECK IT: a link that "
        "names the WRONG person is the one failure this gate cannot catch for "
        "you. This server keeps no copy: it is in no grant, no log and no file."
        if person
        else "the profile's topcard did not yield a name on a re-read, so this "
        "server cannot tell you whom the act would reach. Open the profile "
        "yourself and check it before confirming."
    )
    return out
