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

AND, SINCE 2026-09-28, ONE READ (section 6). Ruling
``NAMED-PROFILE-READ-BEHIND-A-GRANT`` (the operator, verbatim: "Yes, I'm giving
you permission."; ``_audit/2026-09-28-rulings-named-profile-read.md``) permits
a read of the profile of a member he names, by link or member id, behind the
single-use grant -- its preview loading NOTHING and saying that LinkedIn may
show the member the view -- with the declared fields returned as people
records, one page per call, nothing stored, never for a measurement. It is
``linkedin_read_named_profile``, and it reaches the second door through
:func:`load_the_confirmed_profile` alone, with a token its own preview minted.

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
import secrets
import string
import time
from dataclasses import dataclass
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
    segment compared with percent-encoding decoded and ASCII case folded --
    vanity names are case-insensitive there -- and a MEMBER ID compared
    exactly: ``ACoAA...`` ids are case-sensitive. Anything else is a landing
    the page chose, and it VETOES the act: a member id LinkedIn redirects to a
    vanity address reads False here, and the act refuses rather than adopting
    an address the page supplied.

    ASCII FOLDING, NOT ``casefold()`` (the cold check of 2026-09-28): full
    Unicode case folding said a landing on ``strasse`` was the profile named
    ``stra<sharp s>e``, that the Kelvin sign is a ``k``, a ligature two letters
    and a long s an s, and that two member ids differing in case were one.
    Each is a different address, and the docstring had always said ASCII.
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
    return same_segment(path.group(1), str(segment))


#: Upper-case ASCII letters to lower-case, and nothing else.
_ASCII_LOWER = str.maketrans(string.ascii_uppercase, string.ascii_lowercase)


def same_segment(landed: str, named: str) -> bool:
    """Is a landed profile segment the one named? Percent-decoded both sides;
    a member id exactly; a vanity name with ASCII case folded and nothing
    else folded."""
    here, there = unquote(landed), unquote(named)
    if MEMBER_ID.fullmatch(here) or MEMBER_ID.fullmatch(there):
        return here == there
    return here.translate(_ASCII_LOWER) == there.translate(_ASCII_LOWER)


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
    "invite_in_topcard", "invite_controls_in_topcard", "invite_visible_in_topcard",
    "invite_owner_visible_in_topcard", "invite_foreign_in_topcard",
    "message_controls", "message_matches", "message_tag", "message_href",
    "message_in_topcard", "message_controls_in_topcard", "message_kind_in_topcard",
    "message_visible_in_topcard", "message_owner_visible_in_topcard",
    "message_foreign_in_topcard", "invite_kind_in_topcard", "topcard_all_headings",
    "topcard_members", "topcard_member_id", "more_in_topcard", "more_visible_in_topcard",
    "more_actions", "dialogs", "composer_editors", "composer_editors_pierced",
    "conversation_bubbles",
    "named_controls", "dialog_controls", "dialog_note_fields", "error",
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
        "measured on your own profile and on the one third party's profile "
        f"captured (first-degree, 2026-09-28): title shape {reading.get('title_shape')!r}, "
        f"{coerce.as_count(reading.get('topcards'))} topcard(s), first heading "
        f"matching the title: {reading.get('heading_matches_title')!r}. A shape "
        "no capture shows is NEEDS-CAPTURE C-P1 in the record, and nothing is "
        "aimed at a page this server cannot identify."
    )


def _the_one_visible_and_theirs(
    reading: dict[str, Any], kind: str, prefix: str, named_as: str
) -> Optional[str]:
    """Why the owner's topcard does not draw exactly ONE VISIBLE control of this
    kind, and that one the owner's, or ``None`` when it does.

    THE PRESS CARRIES NO POSITION (see :func:`dom.topcard_invite_control_selector`):
    it is the topcard-scoped, VISIBLE-only selector, pressed strictly, so it can
    only ever mean "the one visible control of this kind in the topcard". This
    is where that one is required, and required to be the owner's: a control
    of the kind that names somebody else -- visible or not -- refuses the act,
    because the owner's own topcard has no reason to draw one.

    REBUILT 2026-09-28 over the live skeleton (the orchestrator's addendum of
    08:43). The live topcard draws each action TWICE, one of the two hidden,
    and draws its Message control named by its own text, with no label: the
    old reader counted labelled controls only, page-wide, found none naming
    the owner, and refused every live Message. It counts now what the press
    can reach -- the visible controls inside the topcard -- and what makes one
    the owner's is settled in the page.
    """
    visible = coerce.as_count(reading.get(prefix + "_visible_in_topcard"))
    owners = coerce.as_count(reading.get(prefix + "_owner_visible_in_topcard"))
    foreign = coerce.as_count(reading.get(prefix + "_foreign_in_topcard"))
    # ONE PERSON'S CARD FIRST (the cold check of 2026-09-28): a stranger's card
    # drawn inside the owner's topcard brings a heading of its own, or a link
    # to its own person, and a control inside it can pass for the owner's --
    # by an unlabelled "Message", or by a same-name label. The live topcard
    # holds one heading and links one member; anything else refuses.
    headings = coerce.as_count(reading.get("topcard_all_headings"))
    members = coerce.as_count(reading.get("topcard_members"))
    if headings != 1 or members > 1:
        return (
            f"the person's topcard is not one person's card: it draws {headings} "
            f"heading(s) and links {members} distinct member(s), where the "
            "measured topcard draws one heading, the owner's name, and links at "
            "most the owner. A card of somebody else's inside it could hold the "
            "control this act would press. Refused before anything is pressed."
        )
    if foreign:
        return (
            f"the person's topcard draws {foreign} {kind} control(s) that are not "
            f"theirs -- {named_as} -- and the owner's own topcard has no reason "
            "to draw one: pressing any control there could reach somebody else. "
            "Refused before anything is pressed."
        )
    if visible == 1 and owners == 1:
        return None
    return (
        f"the person's topcard draws {visible} VISIBLE {kind} control(s), "
        f"{owners} of them theirs, where exactly one, visible and theirs, is the "
        "only shape this act presses: the press names no position and reaches "
        "only what is visible, so two would leave it choosing, and it is "
        "pressed strictly so that a second appearing mid-press stops it. (The "
        "live topcard draws each action twice and hides one -- measured on the "
        "live skeleton of 2026-09-28 -- so the visible one is the only one "
        "counted.)"
    )


def connect_state(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` -- is there exactly one Connect for THIS person?

    ``connect_control_drawn`` needs the identity confirmed, exactly ONE VISIBLE
    Connect-shaped control inside the owner's topcard, that one named
    ``Invite <owner> to connect`` (compared in the page), no Connect-shaped
    control there naming anybody else, and no dialog already open. Nothing
    about the control crosses: the press is
    :func:`dom.topcard_invite_control_selector`, visible-only, pressed strictly.
    (It carried a POSITION -- first in the whole page's list, then in the
    topcard's -- until two re-checks of 2026-09-27 showed a re-render could
    hand either position to a stranger's control; and it counted hidden
    controls until the live skeleton of 2026-09-28 showed the topcard hides
    a duplicate of each action.) A same-name stranger's control OUTSIDE the
    topcard is not the press's to reach and is not counted.
    """
    if not identity_confirmed(reading):
        return UNKNOWN, _identity_why(reading)
    if (
        coerce.as_count(reading.get("invite_visible_in_topcard")) == 0
        and coerce.as_count(reading.get("invite_foreign_in_topcard")) == 0
    ):
        degree = reading.get("degree")
        return UNKNOWN, (
            "this person's topcard draws no visible Connect control naming them "
            f"(degree read: {degree!r}; "
            f"{coerce.as_count(reading.get('more_visible_in_topcard'))} visible "
            "'More' control(s) in the topcard). You may already be connected, an "
            "invitation may be pending, or Connect sits inside the 'More' menu -- "
            "which has never been captured and which this act does not open. "
            "NEEDS-CAPTURE C-P1."
        )
    why_not = _the_one_visible_and_theirs(
        reading, "Connect", "invite", "named for inviting somebody else"
    )
    if why_not:
        return UNKNOWN, why_not
    if coerce.as_count(reading.get("dialogs")):
        return UNKNOWN, (
            f"{coerce.as_count(reading.get('dialogs'))} dialog(s) are already "
            "open on the profile. Connect is not pressed underneath one."
        )
    return CONNECT_FROM, (
        "exactly one visible control named for inviting this person to connect "
        "-- the label shape measured 44 times on other surfaces -- and it is the "
        "only visible Connect control in the topcard of a page that names the "
        "same person. PRESSING IT MAY SEND THE INVITATION AT ONCE, with no further "
        "step: that is how Connect is known to behave, and this is the last point "
        "at which nothing has happened."
    )


def message_state(reading: dict[str, Any]) -> tuple[str, str]:
    """``(state, why)`` -- is there exactly one Message for THIS person, of a
    shape this act may press?

    The one VISIBLE Message-shaped control inside the owner's topcard, and it
    the owner's: a control LABELLED ``Message <owner>``, or -- the live page's
    shape, measured 2026-09-28 -- one with no label whose own text is exactly
    "Message" (see :data:`dom.TOPCARD_MESSAGE_CONTROL`). Pressable: a
    ``<button>``, or an ``<a>`` whose address is the composer -- the
    destination measured on 16 of the 18 labelled Message controls captured
    and on both of the live topcard's. A link anywhere else would navigate to
    an address the page supplied, which PAGE-MAY-VETO-NEVER-SUPPLY forbids.
    And no conversation composer may already be open: the one that opens must
    be the one this act types into.
    """
    if not identity_confirmed(reading):
        return UNKNOWN, _identity_why(reading)
    if (
        coerce.as_count(reading.get("message_visible_in_topcard")) == 0
        and coerce.as_count(reading.get("message_foreign_in_topcard")) == 0
    ):
        return UNKNOWN, (
            "this person's topcard draws no visible Message control -- "
            f"{coerce.as_count(reading.get('message_kind_in_topcard'))} of the "
            "kind drawn, none visible. The profile may draw Message only for "
            "connections, or in a menu never captured (NEEDS-CAPTURE C-P4)."
        )
    why_not = _the_one_visible_and_theirs(
        reading, "Message", "message",
        "labelled for somebody else, or saying something other than 'Message'",
    )
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
    # A COMPOSER ALREADY OPEN, BY EITHER ENGINE (the cold review of
    # 2026-09-28): the page's own script cannot see into the overlay's
    # shadow root, where the live overlay is; Playwright's engine can.
    already = max(
        coerce.as_count(reading.get("composer_editors")),
        coerce.as_count(reading.get("composer_editors_pierced")),
    )
    if already:
        return UNKNOWN, (
            f"{already} conversation "
            "composer(s) are already open on this page. Close them first: the "
            "composer this act types into must be the one its own press opens."
        )
    degree = reading.get("degree")
    return MESSAGE_FROM, (
        "exactly one visible Message control in this person's topcard, and it "
        "is theirs, of a shape this act may press, and no composer already "
        "open."
        + (
            " The profile reads '1st': the words are typed only if, after the "
            "press, exactly one empty composer sits in a conversation titled "
            "with exactly that person's name -- or, where no conversation "
            "exists yet, in the one new message the press opened, addressed "
            "to exactly them and nobody else."
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
    # somebody else's and says nothing about this invitation. VISIBLE ONLY
    # since 2026-09-28: the live topcard draws each action twice and hides
    # one, and a hidden duplicate counted here would read two.
    still = coerce.as_count(fresh.get("invite_owner_visible_in_topcard"))
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
#
# THE FIRST CONTACT, MEASURED 2026-09-28 (the live lane's session 3, on a
# first-degree profile the operator named): with NO conversation between
# them, the press opens a NEW-MESSAGE bubble, still on the profile -- one
# title reading "New message", a recipient box holding ONE committed
# recipient (a pill whose text is their name), a card linking their profile,
# the form empty and Send disabled -- and the conversation gate refused it,
# by design, for drawing no title with the name. The chain that makes that
# recipient certain (the orchestrator's addendum of 13:03), each link a
# condition that refuses on doubt:
#
#   1. the target is the link he gave, and the topcard's identity holds;
#   2. the pressed control is the owner's one visible Message link, and its
#      address names the profile's own member (``dom`` ``message_member_bound``);
#   3. after the press, exactly one bubble holds a composer: a new-message
#      bubble, one recipient box, ONE committed recipient whose text IS the
#      topcard's name, the whole of it, an empty search field, and a recipient
#      card linking the topcard's own profile;
#   4. only then are his words typed, and Send is pressed only while all of 3
#      still holds; afterwards a conversation must exist, headed by that name,
#      holding his words -- the receipt, read in place, the name never
#      recorded. SINCE THE ORDER OF 17:37 (session 4, measured live): the
#      check waits, bounded, for Send to turn on first -- LinkedIn turns it
#      on after the words land -- and a box that ALREADY holds exactly his
#      words, whole and nothing else (a draft LinkedIn kept), is not typed
#      into again: it goes straight to that wait and that check;
#   5. and the bubble is closed by its header's close control, found by its
#      text: Escape does not close it (measured).
#
# THE OVERLAY IS IN A SHADOW ROOT (the same session): the page's own
# ``querySelectorAll`` does not see it, so ``dom.NAMED_PROFILE_JS``'s bubble
# fields read nothing there. The first contact therefore asks every question
# about its bubble through Playwright's piercing engine (``dom.read_bubbles``),
# and the one precondition both paths share -- no composer open BEFORE the
# press -- is counted by that engine too (``composer_editors_pierced``).
#
# THE CONVERSATION PATH IS LEFT AS IT WAS, as the addendum of 13:03 ordered:
# its "whose conversation" is the page's own reading, which cannot see into
# the shadow root, so where LinkedIn draws the conversation there it refuses
# at 6 -- which conversation bubbles are drawn there is DERIVED; session 3
# opened only a new message. Giving it the piercing reading as well was
# built on 2026-09-28 and taken out the same day: the cold review showed it
# let the path type into a conversation already open before the press,
# which the page's own count could not see (lane L5's record, "The
# first-contact path").

BUBBLE_SELECTOR = dom.OVERLAY_BUBBLE
COMPOSER_EDITOR_SELECTOR = dom.OVERLAY_COMPOSER_EDITOR
COMPOSER_SEND_SELECTOR = dom.OVERLAY_SEND_CONTROL

#: HOW LONG THE GATE WAITS for a composer to be drawn after the Message press,
#: before it reads. A LIVENESS BOUND, NOT A SAFETY ONE: the gate refuses on
#: whatever it then finds, so a composer drawn later than this only means the
#: act stops having typed nothing. How long LinkedIn's overlay takes to draw is
#: part of NEEDS-CAPTURE C-P4, which the receipt records as ``composer_waited_ms``.
#:
#: 3 s -> 12 s ON 2026-09-28 (lane L5, the first-contact path), MEASURED LIVE by
#: the live lane's session 3 (``M M1``'s cell): at 12:54 the gate refused at
#: condition 5 with NO composer drawn inside 3 s; at 12:57, with the bound raised
#: to 12 s in the runner's process on the orchestrator's approval, the press drew
#: a new-message composer in 1.5 s. The first press of a session is the slow one,
#: and a liveness bound that refuses it only costs his act.
OPENED_COMPOSER_WAIT_MS = 12_000

#: HOW LONG A FIRST CONTACT'S SEND IS GIVEN to draw his words as the new
#: conversation's message before it is read. A LIVENESS BOUND, like the one
#: above: it decides nothing, and a message drawn later reads UNKNOWN.
SENT_WORDS_WAIT_MS = 5_000

#: HOW LONG, AFTER HIS WORDS ARE IN THE BOX, A FIRST CONTACT'S SEND IS GIVEN
#: TO TURN ON before the last-moment check reads it. A LIVENESS BOUND, NOT A
#: SAFETY ONE: the wait decides nothing, and the check refuses on what it then
#: finds. MEASURED LIVE 2026-09-28 (the live lane's session 4): every link of
#: the chain held and his words went in, 65 of 65, and the check refused at 4
#: because Send read DISABLED straight after the fill; a skeleton of the same
#: bubble about a second later drew Send WITHOUT ``disabled``. LinkedIn turns
#: it on after the words land, not as they do.
SEND_ENABLED_WAIT_MS = 5_000
#: The new message's Send as the wait looks for it: drawn without ``disabled``.
_SEND_ENABLED_SELECTOR = COMPOSER_SEND_SELECTOR + ":not([disabled])"

#: THE BUBBLE'S CLOSE CONTROL -- a header control whose accessible name opens
#: on the word "Close", pressed strictly. MEASURED 2026-09-28: the header's
#: two controls carry their labels as text, and Escape does NOT close the
#: bubble (after it: one bubble, one editor, one dialog). THE FIRST WORD IS
#: MEASURED: in session 4 the bubble reader counted exactly one header
#: control of the live bubble whose text opens on "Close". The rest of
#: "Close your draft conversation" is DERIVED from the reduced words' shape
#: (26 letters in four words) and the form's own "... for your draft
#: conversation" labels, and is never read. If the live control reads
#: otherwise, the close gate refuses and the bubble stays on his screen.
#: The gate also requires the one element this selects to be one of the
#: bubble's header controls.
BUBBLE_CLOSE_SELECTOR = (
    dom.OVERLAY_BUBBLE + " .msg-overlay-bubble-header__controls"
    + " >> role=button[name=/^Close\\b/]"
)
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
        # THE BOX HOLDS EXACTLY HIS WORDS, whole and nothing else -- the draft
        # rule's reading (the order of 2026-09-28 17:37). Compared in this
        # process, as the send gate compares them; only the boolean crosses.
        "editor_holds_the_words": None,
        "send_disabled": None,
        "events": 0,
        "events_with_text": None,
        "last_from": "unknown",
        "last_has_text": None,
        "inmail_words": None,
        "credit_words": None,
        "error": None,
        # THE ONE BUBBLE HOLDING A COMPOSER, through the piercing engine
        # (2026-09-28; ``dom.read_bubbles``). None when not exactly one does.
        "holding_title_kind": None,
        "holding_boxes": None,
        "holding_pills": None,
        "holding_pill_names_owner": None,
        "holding_search_empty": None,
        "holding_card_matches": None,
        "holding_close_controls": None,
        "holding_sends": None,
        "bubble_facts_error": None,
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
            held = _normalise(await editors.first.inner_text())
            out["editor_empty"] = held == ""
            if text is not None:
                out["editor_holds_the_words"] = held == _normalise(text)
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
    out.update(await holding_bubble(page))
    return out


async def holding_bubble(page: Any) -> dict[str, Any]:
    """The one overlay bubble holding a composer, through Playwright's
    PIERCING engine (``dom.read_bubbles``): its title as a closed token, its
    recipients counted, and three comparisons made in the page -- the one
    recipient's text with the profile's name, the recipient card's profile
    with the topcard's, and the search field's emptiness. Every field None
    when not exactly one bubble holds a composer."""
    facts = await dom.read_bubbles(page)
    holding = [b for b in facts["bubbles"] if b["editor"]]
    one = holding[0] if len(holding) == 1 else {}
    return {
        "holding_title_kind": one.get("title_kind"),
        "holding_boxes": one.get("boxes"),
        "holding_pills": one.get("pills"),
        "holding_pill_names_owner": one.get("pill_names_owner"),
        "holding_search_empty": one.get("search_empty"),
        "holding_card_matches": one.get("card_matches"),
        "holding_close_controls": one.get("close_controls"),
        "holding_sends": one.get("sends"),
        "bubble_facts_error": facts["error"],
    }


async def wait_for_sent_words(
    page: Any, *, text: str, timeout_ms: Optional[int] = None
) -> dict[str, Any]:
    """After a first contact's Send: wait, BOUNDED, for his words to be drawn
    as a message in the bubble holding the composer. DECIDES NOTHING -- the
    verdict reads everything afterwards; ``failure`` is an exception's TYPE."""
    bound = SENT_WORDS_WAIT_MS if timeout_ms is None else int(timeout_ms)
    out: dict[str, Any] = {"appeared": False, "waited_ms": 0, "failure": None}
    started = time.monotonic()
    try:
        holding = page.locator(BUBBLE_SELECTOR).filter(has=page.locator(COMPOSER_EDITOR_SELECTOR))
        await (
            holding.locator(_EVENT)
            .filter(has=page.get_by_text(_normalise(text), exact=True))
            .first.wait_for(state="attached", timeout=bound)
        )
        out["appeared"] = True
    except Exception as exc:  # noqa: BLE001 - a timeout is a reading, not a fault
        out["failure"] = type(exc).__name__
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


async def wait_for_send_enabled(
    page: Any, *, timeout_ms: Optional[int] = None
) -> dict[str, Any]:
    """A first contact, his words in the box: wait, BOUNDED, for the Send
    inside the one bubble holding the composer to be drawn without
    ``disabled`` -- through Playwright's piercing engine, the bubble being in
    a shadow root. DECIDES NOTHING: :func:`composer_send_gate` reads
    everything afterwards and refuses on what it finds. ``failure`` is an
    exception's TYPE only."""
    bound = SEND_ENABLED_WAIT_MS if timeout_ms is None else int(timeout_ms)
    out: dict[str, Any] = {"enabled": False, "waited_ms": 0, "failure": None}
    started = time.monotonic()
    try:
        holding = page.locator(BUBBLE_SELECTOR).filter(has=page.locator(COMPOSER_EDITOR_SELECTOR))
        await holding.locator(_SEND_ENABLED_SELECTOR).first.wait_for(
            state="attached", timeout=bound
        )
        out["enabled"] = True
    except Exception as exc:  # noqa: BLE001 - a timeout is a reading, not a fault
        out["failure"] = type(exc).__name__
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


async def bubble_close_gate(page: Any) -> dict[str, Any]:
    """May the bubble be closed? The last step of a first contact, taken only
    after the send read SENT in place. Refuses, pressing nothing, unless:

    1. exactly one overlay bubble is drawn, and it holds the composer;
    2. its header draws exactly one control whose text opens on "Close";
    3. the close selector resolves exactly one element, and it is one of the
       bubble's header controls -- the press is strict;
    4. the composer is empty: a box still holding words is not closed over.
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": BUBBLE_CLOSE_SELECTOR,
        "refused_condition": None,
        "why": "",
        "observed": {},
    }
    try:
        facts = await dom.read_bubbles(page)
        holding = [b for b in facts["bubbles"] if b["editor"]]
        editors = page.locator(COMPOSER_EDITOR_SELECTOR)
        observed = {
            "bubbles": len(facts["bubbles"]),
            "bubbles_with_editor": len(holding),
            "close_controls": holding[0]["close_controls"] if len(holding) == 1 else None,
            "matches": coerce.as_count(await page.locator(BUBBLE_CLOSE_SELECTOR).count()),
            # THE ELEMENT THE PRESS WILL TAKE IS ONE OF THE BUBBLE'S HEADER
            # CONTROLS (the cold review of 2026-09-28): the count above is by
            # accessible name, the page's count by class and text.
            "matches_as_control": coerce.as_count(
                await page.locator(BUBBLE_CLOSE_SELECTOR)
                .and_(page.locator(dom.OVERLAY_BUBBLE + " " + dom.OVERLAY_BUBBLE_CONTROL))
                .count()
            ),
            "editor_empty": None,
            "error": facts["error"],
        }
        if coerce.as_count(await editors.count()) == 1:
            observed["editor_empty"] = _normalise(await editors.first.inner_text()) == ""
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["refused_condition"] = "0_read_failed"
        out["why"] = f"the bubble could not be read ({type(exc).__name__}). Nothing was closed."
        return out
    out["observed"] = observed
    if observed["error"] or observed["bubbles"] != 1 or observed["bubbles_with_editor"] != 1:
        out["refused_condition"] = "1_not_one_bubble"
        out["why"] = (
            f"{observed['bubbles']} bubble(s) drawn, {observed['bubbles_with_editor']} holding "
            "a composer: the close step presses only in the one bubble the message was "
            "sent from. Nothing was closed; the bubble stays on your screen."
        )
        return out
    if observed["close_controls"] != 1:
        out["refused_condition"] = "2_not_one_close_control"
        out["why"] = (
            f"the bubble's header draws {observed['close_controls']} control(s) whose text "
            "opens on 'Close'. Escape does not close this bubble, and no other control is "
            "pressed in its place. Nothing was closed."
        )
        return out
    if observed["matches"] != 1 or observed["matches_as_control"] != 1:
        out["refused_condition"] = "3_selector_count"
        out["why"] = (
            f"the close selector resolves {observed['matches']} element(s), "
            f"{observed['matches_as_control']} of them a header control of the "
            "bubble: it must be one, and that one. Nothing was closed."
        )
        return out
    if observed["editor_empty"] is not True:
        out["refused_condition"] = "4_words_in_the_box"
        out["why"] = (
            "the composer is not empty, and a bubble holding words is never closed over "
            "them. Nothing was closed."
        )
        return out
    out["proceed"] = True
    out["why"] = (
        "one bubble, its one close control, the composer empty: that control "
        "is the one pressed."
    )
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
       (NEEDS-CAPTURE C-P4 otherwise). A FIRST CONTACT may instead find the
       box ALREADY holding exactly his words, whole and nothing else -- a
       draft LinkedIn kept from an earlier attempt (the order of 17:37):
       then nothing is typed, and Send's state is left to the bounded wait
       and the last-moment check. Any other text in the box refuses;
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
        # THE FIRST CONTACT'S READINGS (2026-09-28), each from the piercing
        # engine or the pressed control -- see this section's head. The
        # conversation path decides on none of them.
        "title_kind": conversation.get("holding_title_kind"),
        "recipient_boxes_in_bubble": conversation.get("holding_boxes"),
        "recipient_pills": conversation.get("holding_pills"),
        "recipient_is_theirs": conversation.get("holding_pill_names_owner"),
        "recipient_search_empty": conversation.get("holding_search_empty"),
        "recipient_card_is_theirs": conversation.get("holding_card_matches"),
        "send_in_bubble": conversation.get("holding_sends"),
        "press_names_their_member": profile_after.get("message_member_bound"),
        "bubble_facts_error": conversation.get("bubble_facts_error"),
        "recipient_boxes": conversation.get("recipient_boxes"),
        "editor_empty": conversation.get("editor_empty"),
        "editor_holds_the_words": conversation.get("editor_holds_the_words"),
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
        # WHICH COMPOSER THE PRESS OPENED: "conversation" (one headed by the
        # person) or "first_contact" (a new message addressed to them), once
        # condition 5 has been passed; None before.
        "path": None,
        # HIS WORDS ARE ALREADY IN THE BOX (the draft rule, a first contact
        # only): nothing is to be typed.
        "words_in_place": False,
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
    if coerce.as_count(observed["recipient_boxes"]):
        # A RECIPIENT BOX: A NEW MESSAGE, NOT A CONVERSATION. Since
        # 2026-09-28 that is the FIRST-CONTACT path, held to its own chain.
        out["path"] = "first_contact"
        refusal = _first_contact_refusal(observed)
        if refusal is not None:
            out["refused_condition"], out["why"] = refusal
            return out
    else:
        out["path"] = "conversation"
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
                "typed. (The page's own script cannot see into a shadow root; the "
                "piercing reading, which this path does not act on, reads the "
                f"title as {observed['title_kind']!r}.)"
            )
            return out
    if (
        out["path"] == "first_contact"
        and observed["editor_empty"] is False
        and observed["editor_holds_the_words"] is True
    ):
        # THE DRAFT RULE (the orchestrator's order of 2026-09-28 17:37): a
        # first contact refused after its words went in leaves them in the
        # box, and LinkedIn may keep them as a draft that the next press
        # opens with. Exactly his words, whole and nothing else, are not
        # typed again; any other text still refuses below.
        out["words_in_place"] = True
    elif observed["editor_empty"] is not True or observed["send_disabled"] is not True:
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
    if out["path"] == "first_contact":
        out["why"] = (
            "still on the profile you named, a first-degree connection, and a "
            "FIRST CONTACT: the pressed Message link names that profile's own "
            "member, and it opened one new-message composer addressed to exactly "
            "one recipient, whose name is the profile's name and whose card links "
            "that profile, nobody else being added: "
            + (
                "the box already holds exactly your words, whole and nothing "
                "else -- a draft LinkedIn kept -- so nothing will be typed."
                if out["words_in_place"]
                else "empty, Send disabled."
            )
        )
    else:
        out["why"] = (
            "still on the profile you named, a first-degree connection, and "
            "exactly one conversation composer after the press, in a conversation "
            "whose title reads exactly that person's name: empty, Send disabled, "
            "no recipient box."
        )
    return out


def _first_contact_refusal(observed: dict[str, Any]) -> Optional[tuple[str, str]]:
    """The first-contact chain's links 2 and 3, in order: ``(condition, why)``
    for the first that fails, or None. Every doubt refuses; nothing is typed."""
    if observed.get("bubble_facts_error"):
        return "4_unreadable", (
            "the new message could not be read through the engine that sees "
            f"into the overlay ({observed.get('bubble_facts_error')}). Nothing "
            "was typed."
        )
    if coerce.as_count(observed.get("bubbles")) != 1:
        return "6f_not_one_bubble", (
            f"{observed.get('bubbles')} overlay bubble(s) are drawn: a first "
            "contact is typed only into the one bubble on the page, the one the "
            "press opened -- the measured shape, none before the press and one "
            "after. Nothing was typed."
        )
    if not coerce.as_count(observed.get("recipient_pills")):
        return "7_recipient_box", (
            f"{observed.get('recipient_boxes')} recipient box(es) are drawn with "
            "nobody committed in them: a new-message composer addressed to no "
            "one, not a conversation with the person you named. Nothing was typed."
        )
    if observed.get("title_kind") != "new_message":
        return "6f_not_a_new_message", (
            "a recipient box is drawn, but the bubble holding it is not a "
            f"new-message composer (its title reads as {observed.get('title_kind')!r}, "
            "compared in the page). Only the measured first-contact shape is typed "
            "into. Nothing was typed."
        )
    if (
        coerce.as_count(observed.get("recipient_boxes")) != 1
        or coerce.as_count(observed.get("recipient_boxes_in_bubble")) != 1
        or coerce.as_count(observed.get("recipient_pills")) != 1
    ):
        return "6f_not_one_recipient", (
            f"{observed.get('recipient_boxes')} recipient box(es) on the page, "
            f"{observed.get('recipient_boxes_in_bubble')} in the new message, "
            f"holding {observed.get('recipient_pills')} committed recipient(s): "
            "a first contact goes to exactly one, in its own box. Nothing was "
            "typed."
        )
    if observed.get("recipient_is_theirs") is not True:
        return "6f_recipient_not_theirs", (
            "the one committed recipient's name is not exactly the name on the "
            "profile (compared in the page, the whole of it). Your words would "
            "reach somebody you did not name. Nothing was typed."
        )
    if observed.get("recipient_search_empty") is not True:
        return "6f_another_recipient_on_the_way", (
            "the recipient box's search field is not empty: a second recipient "
            "may be on the way in. Nothing was typed."
        )
    if observed.get("press_names_their_member") is not True:
        return "6f_press_not_bound_to_them", (
            "the Message link pressed does not name the profile's own member "
            "in its address (compared in the page), so the recipient LinkedIn "
            "committed cannot be tied to the link you gave. Nothing was typed."
        )
    if observed.get("recipient_card_is_theirs") is not True:
        return "6f_card_not_theirs", (
            "the new message's recipient card does not link the profile you "
            "named, and only that profile (compared in the page). Nothing was "
            "typed."
        )
    if coerce.as_count(observed.get("send_in_bubble")) != 1:
        return "6f_send_not_in_the_bubble", (
            f"the new message's bubble holds {observed.get('send_in_bubble')} Send "
            "control(s): the one Send on the page must be its own. Nothing was "
            "typed."
        )
    return None


async def composer_send_gate(
    page: Any, *, text: str, first_contact: bool = False
) -> dict[str, Any]:
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

    A FIRST CONTACT (2026-09-28) keeps its recipient box -- that is the shape
    -- so condition 1 does not apply to it, and its condition 6 is its own:
    the bubble is still the new-message composer, holding exactly one
    committed recipient whose name is the profile's, whose card links the
    profile, with nobody else on the way in -- re-read with his words in the
    box, the last moment before the message is irreversible.
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
        # A FIRST CONTACT'S CHAIN, read again with his words in the box,
        # through the piercing engine (2026-09-28). The conversation path
        # reads none of it.
        holding: dict[str, Any] = {}
        observed["bubbles"] = None
        if first_contact:
            holding = await holding_bubble(page)
            observed["bubbles"] = coerce.as_count(await page.locator(BUBBLE_SELECTOR).count())
        observed["title_kind"] = holding.get("holding_title_kind")
        observed["recipient_boxes_in_bubble"] = holding.get("holding_boxes")
        observed["recipient_pills"] = holding.get("holding_pills")
        observed["recipient_is_theirs"] = holding.get("holding_pill_names_owner")
        observed["recipient_search_empty"] = holding.get("holding_search_empty")
        observed["recipient_card_is_theirs"] = holding.get("holding_card_matches")
        observed["send_in_bubble"] = holding.get("holding_sends")
        observed["bubble_facts_error"] = holding.get("bubble_facts_error")
        observed["first_contact"] = bool(first_contact)
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the composer could not be read after the fill "
            f"({type(exc).__name__}). Send was not pressed."
        )
        return out
    out["observed"] = observed
    if first_contact and observed["bubble_facts_error"]:
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            "the new message could not be read through the engine that sees "
            f"into the overlay ({observed['bubble_facts_error']}). Send was not "
            "pressed, and the words are still in the composer on your screen."
        )
        return out
    if observed["recipient_boxes"] and not first_contact:
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
    if first_contact:
        if not (
            coerce.as_count(observed["bubbles"]) == 1
            and observed["title_kind"] == "new_message"
            and coerce.as_count(observed["recipient_boxes"]) == 1
            and coerce.as_count(observed["recipient_boxes_in_bubble"]) == 1
            and coerce.as_count(observed["recipient_pills"]) == 1
            and observed["recipient_is_theirs"] is True
            and observed["recipient_search_empty"] is True
            and observed["recipient_card_is_theirs"] is True
            and coerce.as_count(observed["send_in_bubble"]) == 1
        ):
            out["refused_condition"] = "6f_recipient_changed"
            out["why"] = (
                "your words are in the box, but the new message is no longer "
                f"addressed to exactly the person you named: {observed['bubbles']} "
                f"bubble(s), title {observed['title_kind']!r}, "
                f"{observed['recipient_boxes']} box(es), "
                f"{observed['recipient_boxes_in_bubble']} in the bubble, "
                f"its Send there: {observed['send_in_bubble']!r}, "
                f"{observed['recipient_pills']} committed recipient(s), the one "
                f"named for them: {observed['recipient_is_theirs']!r}, nobody else "
                f"on the way in: {observed['recipient_search_empty']!r}, the card "
                f"theirs: {observed['recipient_card_is_theirs']!r}. A message "
                "cannot be taken back. Send was not pressed, and the words are "
                "still in the composer on your screen."
            )
            return out
    elif observed["conversation_names_the_owner"] is not True:
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
    if first_contact:
        out["why"] = (
            "the composer holds exactly the words you confirmed and Send went "
            "from disabled to enabled, in the new message addressed to exactly "
            "the person you named -- one committed recipient, named as the "
            "profile is, the card linking that profile, nobody else being added."
        )
        return out
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
    say more than ``send_message``'s in-place reading could (that action was
    retired on 2026-09-27): the number of
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

#: The topcard's "Contact info" line -- the separator the topcard parser was
#: measured against (name, pronouns, headline, location, THEN Contact info).
#: The headline and the location sit above it; below it come the connection
#: count and, on a third party's profile, the action buttons -- Message,
#: Connect, More -- whose labels the parser's chrome list, measured on HIS
#: profile, does not know. So the lines are CUT here before parsing: with no
#: headline drawn above Contact info, the parser falls back to the first
#: eligible line anywhere, and printed the buttons' labels as the person's
#: headline (measured at lane L5's merge of master 52b55b6 on the synthetic
#: profile: "Message Connect More"). DERIVED, like everything read off a third
#: party's topcard: no capture holds one (C-P1).
_CONTACT_INFO_LINE = re.compile(r"\s*contact info[\s.:]*", re.IGNORECASE)


def _above_contact_info(lines: list[Any]) -> list[Any]:
    """The topcard's lines above its Contact info line, or all of them when it
    draws none."""
    for index, line in enumerate(lines):
        if _CONTACT_INFO_LINE.fullmatch(str(line)):
            return lines[:index]
    return lines


def person_from_the_topcard(
    fields: dict[str, Any], *, segment: str, degree: Any = None
) -> Optional[dict[str, Any]]:
    """The people record a profile's topcard names, or ``None``. PURE: it reads
    no page, only :func:`dom.read_profile_fields`' reading of one.

    THE ONE PARSE BOTH ROUTES MAKE (2026-09-28): the named acts' preview
    (:func:`name_the_profile_target`) and the read he names
    (:func:`read_the_confirmed_profile`) name the member with the same rules --
    the title without its notification count, the topcard picked BY THAT NAME,
    degree lines dropped, the lines cut at Contact info, and the name the parser
    reads HELD TO THE NAME THE TITLE GIVES, so a section picked by position
    rather than by name names nobody. Split out of the preview's namer rather
    than copied, because two copies of a rule that decides whom a record names
    are two rules.

    ``segment`` is the caller's own; the record's link is the address this
    server COMPOSED from it, never a link read off the page. ``degree`` is what
    the caller read, or ``None`` -- ABSENT, the read's choice: no capture shows
    a third party's degree line.
    """
    title = _COUNT_PREFIX.sub("", str(fields.get("title") or ""))
    top = shape.pick_topcard(fields.get("sections") or [], title)
    # A LINE WITH NO LETTER AND NO DIGIT IS NEVER A HEADLINE OR A PLACE
    # (2026-09-28): the live skeleton's topcard draws two such lines between
    # the name and the headline -- a two-character one whose words the
    # skeleton does not keep, and a separator -- and the parser takes the
    # first eligible line for the headline.
    lines = [
        line
        for line in (top or {}).get("lines") or []
        if not _DEGREE_LINE.fullmatch(str(line).strip())
        and any(character.isalnum() for character in str(line))
    ]
    parsed = shape.parse_profile_topcard(_above_contact_info(lines))
    wanted = shape.name_from_title(title)
    if not wanted or str(parsed.get("name") or "").casefold() != wanted.casefold():
        return None
    return people_seam.person(
        name=parsed.get("name"),
        headline=parsed.get("headline"),
        href=profile_url(segment),
        degree=degree,
    )


async def name_the_profile_target(
    page: Any, spec: Any, observation: Any, block: dict[str, Any], *, segment: str
) -> dict[str, Any]:
    """Print WHOM this act resolved to, in the confirm block and nowhere else.

    PEOPLE-DATA-MITIGATIONS item 6: "An outward act fires at the exact member
    the operator names, by link or id, and the tool reports whom it resolved
    before it acts." The four declared fields -- name, headline, link,
    degree -- as a people record built by :func:`people_seam.person`: lane G's
    ``people_data.Person``, sanitised, capped and marked as another member's
    words (mitigation 2, adopted at lane L5's merge of master 52b55b6), its
    headline ABSENT (``None``) when the topcard draws none
    (PREVIEW-NAMES-THE-RESOLVED-TARGET, as the orchestrator applied it to
    these previews).

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
            # THE TITLE WITHOUT ITS NOTIFICATION COUNT, which 21 of 95
            # captures carry as a leading "(N) ", and THE NAME READ HELD TO
            # THE NAME THE TITLE GIVES -- both in the one parse the read he
            # names shares (:func:`person_from_the_topcard`, 2026-09-28).
            person = person_from_the_topcard(
                await dom.read_profile_fields(page),
                segment=segment,
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


# ---------------------------------------------------------------------------
# 6. THE READ HE NAMES -- ruling NAMED-PROFILE-READ-BEHIND-A-GRANT
# ---------------------------------------------------------------------------
#
# THE RULING (the operator, 2026-09-28 08:01, verbatim: "Yes, I'm giving you
# permission."; ``_audit/2026-09-28-rulings-named-profile-read.md``, registered
# as NAMED-PROFILE-READ-BEHIND-A-GRANT): a read of a member's profile HE NAMES
# in the call -- by link or member id, never a name read off a page -- behind
# the single-use grant; the preview states that LinkedIn may show the member
# the view; the declared fields leave as people records under
# PEOPLE-DATA-MITIGATIONS; never for a measurement. It amends his own
# 2026-09-04 removal of the third-party profile pattern (the exclusion family
# NO-THIRD-PARTY-PROFILE-LOAD) for exactly this read, and unblocks ``N 178``.
#
# THE PREVIEW LOADS NOTHING, AND THAT IS THE RULING'S OWN CONDITION. The
# mitigation he approved reads "a single-use confirmation for each view,
# stating the possible trace". The view IS the load, so the confirmation has
# to come before it. The two named-person WRITES load the profile at their
# preview because that load is part of the act he ordered toward that person;
# for this read the load is the whole act. So the preview names the member by
# the ONE address it resolved from his argument -- a link says WHO -- and says
# plainly that it has not read the name: a people record cannot be built
# without one (``people_data.Person`` requires a name), and the name is on the
# page whose load is being confirmed. The record comes back from the confirmed
# call, read once.
#
# ONE PAGE PER CALL: the preview loads none; the confirmed call exactly one --
# this profile, through the second door, with no scroll and no press.
#
# THE GRANT HAS THE WRITES' SHAPE AND ITS OWN REGISTRY. ``writes.mint`` issues
# a grant only for a sanctioned WRITE, only against a reading a preview LOADED,
# and only with writes switched on: three facts about writes that this read
# does not share. So this read keeps its own grants with the same properties
# -- a token of 24 random bytes, bound to the canonical link, valid for
# :data:`READ_GRANT_TTL_SECONDS` (the writes' 120, pinned equal by a test),
# single-use at BOTH doors (consumed once, loaded once), swept on every mint
# and consume, held in this process's memory and nowhere else. What a grant
# holds is HIS OWN ARGUMENT, canonicalised -- never a page string.
#
# WHAT IS MEASURED AND WHAT IS NOT. The name and the headline are read with
# the parse the named acts' preview uses (:func:`person_from_the_topcard`),
# over :func:`dom.read_profile_fields`, the reader ``linkedin_my_profile`` uses
# -- measured on his OWN profile's topcard (six captures); on a third party's
# page the same template is DERIVED (NEEDS-CAPTURE C-P1), and the result says
# so. The degree line and the member's GROUPS are ABSENT: no capture shows
# either on a third party's profile, and a field no capture shows is not
# read. ``N 178`` -- the groups a member belongs to -- waits on the capture
# spec C-P7 in ``_audit/2026-09-24-lane-l5-messaging.md``, taken inside the
# first confirmed read on a member he names; the one count this read takes
# for it, :data:`GROUP_LINK_SELECTOR`, is a hint for that capture and reads
# nobody's groups.

#: The action a read grant is bound to. Not a write: it is in no
#: ``writes.SANCTIONED_WRITES`` table and no write door accepts it.
READ_ACTION = "read_named_profile"

#: How long a read grant lives. The writes' ``GRANT_TTL_SECONDS``, restated
#: here because ``writes`` imports this module; ``tests/test_named_profile_read.py``
#: pins the two equal.
READ_GRANT_TTL_SECONDS = 120.0

#: THE ONE COUNT THE READ TAKES FOR THE CAPTURE C-P7 NEEDS: how many links on
#: the loaded page point under ``/groups/``. An integer and a hint, read once
#: -- it says whether a group link was drawn at load, without a scroll, which
#: tells the capture whether that load's DOM can show a member's groups at
#: all. It names no group, and no field is built on it.
GROUP_LINK_SELECTOR = 'a[href*="/groups/"]'


@dataclass
class ReadGrant:
    """Permission for ONE load of ONE profile he named, once, soon."""

    #: The canonical link composed from HIS argument -- the whole target.
    target: str
    token: str
    minted_at: float
    consumed: bool = False
    #: SET BEFORE THE ONE NAVIGATION and refused on a second: single-use at
    #: the load as well as at the token, as ``writes.WriteGrant.performed``
    #: is at ``perform``.
    loaded: bool = False

    def expired(self) -> bool:
        return time.monotonic() - self.minted_at > READ_GRANT_TTL_SECONDS


#: Live read grants, by token. Process-local by construction.
_READ_GRANTS: dict[str, ReadGrant] = {}


def _sweep_read_grants() -> int:
    """Drop every read grant past its lifetime. Returns how many went."""
    stale = [token for token, grant in _READ_GRANTS.items() if grant.expired()]
    for token in stale:
        _READ_GRANTS.pop(token, None)
    return len(stale)


def mint_read_grant(segment: str) -> ReadGrant:
    """Issue a single-use grant for ONE confirmed load of the profile he named.

    Only :func:`read_preview` calls this, and it loads nothing: a grant here is
    permission for a view that has not happened, which is the ruling's point.
    """
    grant = ReadGrant(
        target=profile_url(segment),
        token=secrets.token_urlsafe(24),
        minted_at=time.monotonic(),
    )
    _READ_GRANTS[grant.token] = grant
    # AFTER the insert, as ``writes.mint`` sweeps: the new grant is never the
    # one swept, and every stale one goes now.
    _sweep_read_grants()
    return grant


def consume_read_grant(token: Any, segment: str) -> ReadGrant:
    """Redeem a token for the ONE profile it was minted against, or raise.

    Every refusal is a view he did not confirm: no token, an unknown or used
    one, an expired one, or one minted for another profile. None of the
    messages quotes a link -- a profile link can carry a person's name, and
    an error is printed.
    """
    if not isinstance(token, str) or not token.strip():
        raise WriteAttemptError(
            "no confirm token. This read loads a profile only with the token "
            "from its own preview: call it once without confirm_token, read "
            "what the preview says, then pass the token it hands you."
        )
    grant = _READ_GRANTS.get(token.strip())
    if grant is None or grant.consumed:
        raise WriteAttemptError(
            "unknown or already-used confirm token. A read token works once; "
            "run the preview again for a new one."
        )
    if grant.expired():
        _READ_GRANTS.pop(grant.token, None)
        raise WriteAttemptError(
            f"this confirm token expired after {READ_GRANT_TTL_SECONDS:.0f}s. "
            "Run the preview again and read it before confirming."
        )
    if grant.target != profile_url(segment):
        raise WriteAttemptError(
            "this confirm token was minted for a different profile than the "
            "one passed now. Nothing was loaded; run the preview for the "
            "profile you mean."
        )
    grant.consumed = True
    _READ_GRANTS.pop(grant.token, None)
    _sweep_read_grants()
    return grant


def discard_read_grants() -> None:
    """Drop every live read grant."""
    _READ_GRANTS.clear()


def check_read_token(token: Any, segment: str) -> None:
    """Raise :func:`consume_read_grant`'s refusal for a token it would refuse,
    WITHOUT consuming anything -- so the tool refuses a bad token before it
    opens a browser session (the cold check of 2026-09-28 found each refusal
    opening one). The redeeming is still :func:`load_the_confirmed_profile`'s."""
    if not isinstance(token, str) or not token.strip():
        raise WriteAttemptError(
            "no confirm token. This read loads a profile only with the token "
            "from its own preview: call it once without confirm_token, read "
            "what the preview says, then pass the token it hands you."
        )
    grant = _READ_GRANTS.get(token.strip())
    if grant is None or grant.consumed or grant.loaded:
        raise WriteAttemptError(
            "unknown or already-used confirm token. A read token works once; "
            "run the preview again for a new one."
        )
    if grant.expired():
        _READ_GRANTS.pop(grant.token, None)
        raise WriteAttemptError(
            f"this confirm token expired after {READ_GRANT_TTL_SECONDS:.0f}s. "
            "Run the preview again and read it before confirming."
        )
    if grant.target != profile_url(segment):
        raise WriteAttemptError(
            "this confirm token was minted for a different profile than the "
            "one passed now. Nothing was loaded; run the preview for the "
            "profile you mean."
        )


def _door_address(segment: str) -> str:
    """The one address the read may load, through the named-profile door --
    or a refusal that QUOTES NOTHING. The door's own message names the
    address, and an address can carry a person's name; the cold check of
    2026-09-28 found the read's confirmed call returning it in its error."""
    try:
        return readonly.assert_named_profile_url(readonly.named_profile_url(segment))
    except WriteAttemptError:
        raise WriteAttemptError(
            "the profile address you gave carries a word this server's "
            "navigation boundary refuses in any address (a settings, "
            "verification or invitation word, say), so the named-profile door "
            "will not load it. Nothing was loaded and no token was issued."
        ) from None


def read_preview(segment: str) -> dict[str, Any]:
    """The first call: NOTHING IS LOADED. Whom it resolved, what the view
    costs, and a single-use token.

    ``segment`` is :func:`profile_segment`'s, so a name never reaches here.
    THE DOOR IS ASKED FIRST (the cold check of 2026-09-28): a segment that
    passes the shape and carries a word the boundary refuses used to get a
    token its confirmed call could never use; it is refused here, with no
    token.
    """
    _door_address(segment)
    grant = mint_read_grant(segment)
    as_member_id = bool(MEMBER_ID.fullmatch(segment))
    block: dict[str, Any] = {
        "action": READ_ACTION,
        "loaded": False,
        "pages_loaded": 0,
        "profile_this_loads": grant.target,
        "given_as": "a member id" if as_member_id else "a profile link",
        "whom_this_resolves_to": None,
        "whom_this_resolves_to_why": (
            "NOT READ, AND ON PURPOSE: the name and headline are on the "
            "profile page, and loading it IS the view this confirmation asks "
            "you for. So the preview names the member by the one address it "
            "resolved from your argument -- the link above -- and the "
            "confirmed call reads the name and headline once and returns them "
            "as a people record. CHECK THE LINK: a link that names the wrong "
            "person is the one failure this preview cannot catch for you."
        ),
        "they_may_see_this_view": (
            "LinkedIn may show this member that you viewed their profile -- "
            "among the people who viewed it, in the way your own "
            "profile-viewing setting presents you -- and a view cannot be "
            "taken back. Confirming loads their profile ONCE; this preview "
            "loaded nothing."
        ),
        "on_confirm": {
            "pages_loaded": 1,
            "person": (
                "name, headline and link, as a people record: the member's own "
                "words, sanitised, capped and marked as another member's text"
            ),
            "groups": (
                "ABSENT: no capture shows a member's groups on their profile "
                "(NEEDS-CAPTURE C-P7), and a field no capture shows is not read"
            ),
            "degree": "ABSENT: no capture shows a third party's degree line",
        },
        "confirm_token": grant.token,
        "expires_in_seconds": int(READ_GRANT_TTL_SECONDS),
        "kept": (
            "nothing: what the confirmed read returns is in no grant, no log "
            "and no file of this server's"
        ),
    }
    if as_member_id:
        block["member_id_landing"] = (
            "LinkedIn may answer a member id by redirecting to the member's own "
            "address. If it does, this read returns NOTHING -- a landing this "
            "server did not compose names nobody it can vouch for "
            "(PAGE-MAY-VETO-NEVER-SUPPLY) -- and the view may already have "
            "been recorded. Whether it redirects has never been captured "
            "(NEEDS-CAPTURE C-P6); pass the profile link to avoid the question."
        )
    return block


async def load_the_confirmed_profile(
    navigator: Any, page: Any, *, token: str, segment: str
) -> str:
    """The ONE load a confirmed read makes. Returns the landing for the reader
    to COMPARE, and never for anything to navigate by or print.

    THE SECOND DOOR'S ONLY READ CALLER. The token is redeemed FIRST -- an
    unconfirmed, replayed, expired or foreign token raises before any address
    is composed -- and the grant is marked loaded BEFORE the navigation, so a
    grant can reach the door once. The address is composed by the boundary
    from the caller's own segment (``readonly.named_profile_url``), checked by
    ``readonly.assert_named_profile_url`` here and again by the navigator,
    and loaded with ``named_profile=True``: the read door refuses every such
    address, as it did before this ruling.
    """
    from linkedin_server.auth import assert_not_authwall

    grant = consume_read_grant(token, segment)
    if grant.loaded:
        raise WriteAttemptError(
            "this grant has already loaded its profile once. A read token "
            "buys one load."
        )
    grant.loaded = True
    # THE LOCALS ARE NAMED FOR THIS FUNCTION, as in ``writes._read_account_share_updates``:
    # the navigation guard tracks a tainted NAME across the whole module, and a
    # landing bound to ``landed`` here tainted every ``landed`` parameter above,
    # spread through ``parts`` and ``path`` into ``profile_segment``'s
    # ``segment``, and read this very navigation as one the page chose
    # (measured 2026-09-28, ``tests/test_navigation_is_never_derived.py``).
    profile_address = readonly.assert_named_profile_url(_door_address(segment))
    # AN EMPTY LANDING IS NOT THE NAMED ADDRESS (the cold check of 2026-09-28):
    # it used to default to the composed address, which then passed the veto.
    # Returned as it came, it reads as no landing and vetoes the read.
    read_landing = str(await navigator.goto(page, profile_address, named_profile=True) or "")
    assert_not_authwall(read_landing, surface="profile")
    return read_landing


async def read_the_confirmed_profile(
    page: Any, *, segment: str, landed: str
) -> dict[str, Any]:
    """The confirmed read's answer, off the page :func:`load_the_confirmed_profile`
    loaded. Reads; never navigates, presses or scrolls.

    A LANDING ELSEWHERE VETOES THE WHOLE READ -- a member id LinkedIn
    redirected, a profile that moved -- and nothing is read off a page this
    server did not compose the address of (PAGE-MAY-VETO-NEVER-SUPPLY). THE
    PAGE MUST NAME ONE PERSON: the title a profile title, exactly one
    topcard, its first heading the title's name (compared in the page). Then
    the person, as a people record whose name is held to the title's; the
    groups and the degree ABSENT; and one hint count for the capture C-P7.
    """
    link = profile_url(segment)
    out: dict[str, Any] = {
        "action": READ_ACTION,
        "loaded": True,
        "pages_loaded": 1,
        "profile_loaded": link,
        "landed_on_the_named_profile": False,
        "identity_confirmed": False,
        "person": None,
        "person_why": "",
        "groups": None,
        "groups_why": (
            "ABSENT: no capture shows a member's groups on their profile, and "
            "a field no capture shows is not read (NEEDS-CAPTURE C-P7)."
        ),
        "what_the_page_showed": {},
        "capture_hints": {},
        "the_view": (
            "the profile was loaded once: LinkedIn may show this member that "
            "you viewed it, and that cannot be undone."
        ),
        "kept": "nothing: this answer is in no grant, no log and no file.",
    }
    if not landed_on_profile(landed, segment):
        out["person_why"] = (
            "the browser did not land on the profile you named -- a member id "
            "LinkedIn redirected (NEEDS-CAPTURE C-P6), or an address the page "
            "chose -- so nothing is read off that page: a landing this server "
            "did not compose names nobody it can vouch for. The landing is "
            "withheld. Pass the profile link itself."
        )
        return out
    out["landed_on_the_named_profile"] = True
    reading = await dom.read_named_profile(page)
    out["what_the_page_showed"] = {
        key: reading.get(key)
        for key in ("title_shape", "topcards", "topcard_headings", "heading_matches_title")
    }
    if not identity_confirmed(reading):
        out["person_why"] = _identity_why(reading)
        return out
    out["identity_confirmed"] = True
    person = None
    try:
        person = person_from_the_topcard(await dom.read_profile_fields(page), segment=segment)
    except Exception as exc:  # noqa: BLE001 - the type is logged, never the words
        logger.debug("named profile read unreadable: %s", type(exc).__name__)
        person = None
    out["person"] = person
    out["person_why"] = (
        "READ ONCE OFF THE PROFILE YOU NAMED, with the reader measured on your "
        "own profile's topcard; on a third party's page that template is "
        "derived (NEEDS-CAPTURE C-P1), so check it against the link. The name "
        "is held to the one the page's own title gives."
        if person
        else "the page named one person, but its topcard did not yield that "
        "name on a re-read, so no record is returned rather than a guess."
    )
    try:
        links = coerce.as_count(await page.locator(GROUP_LINK_SELECTOR).count())
    except Exception as exc:  # noqa: BLE001 - a hint; a failure is its type
        logger.debug("group link count unreadable: %s", type(exc).__name__)
        links = None
    out["capture_hints"] = {
        "group_links_drawn": links,
        "note": (
            "for NEEDS-CAPTURE C-P7 only: how many links on this load point "
            "under /groups/, read once without a scroll. It names no group and "
            "is not a reading of anybody's groups."
        ),
    }
    return out
