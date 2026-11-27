"""HIS OWN VOLUNTEERING PAGE, ON THE ONE SPELLING LINKEDIN DRAWS, THE ID FROM HIM.

## WHY THIS MODULE EXISTS

LinkedIn draws his "Open to volunteering" page (census ``P D24``) only as
``/in/<member>/opportunities/volunteering/education/?profileId=<his own id>``:
on his profile root's card link and in the ``Open to`` menu's item, both
measured (``_audit/2026-11-27-prof7.md``; ``_audit/_slice-otw-census.md``).
VOLUNTEERING-BARE-SPELLING-FIRST (the orchestrator, 2026-11-25) took the bare
spelling first -- "if it does not land, profileId from tool arguments at
runtime (his own id, never stored)" -- and the bare spelling landed on his
profile root (the live lane's session 12, load 22). So the fallback has its
boundary now (VOLUNTEERING-FALLBACK-BOUNDARY, the orchestrator, 2026-11-27):

* ``readonly`` admits the ``/in/me/`` spelling with ONE ``profileId`` of the
  member-id shape (``named_profile.MEMBER_ID``), and nothing else;
* the id comes ONLY from the caller's arguments at runtime, validated by that
  shape; a missing or ill-shaped id REFUSES (:class:`ProfileIdRefused`, whose
  message never quotes it);
* THE PAGE NEVER SUPPLIES IT. A link or a menu item drawn on his root may be
  pressed only when its target is EXACTLY the address :func:`volunteering_
  address` forms from his argument, the landed member -- proven his by the
  self-profile loader -- read as ``me`` (SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH,
  amended 2026-11-27 13:10). Any other id, parameter or fragment vetoes.

## WHAT THIS MODULE NEVER DOES

It logs nothing, prints nothing, writes nothing and stores nothing, and it
never navigates: the formed address goes back to its caller and nowhere else,
and the verdicts are closed words (:data:`MATCH_WORDS`) and booleans. A
refusal names what was wrong in closed words, never the value.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qsl, urlsplit

from linkedin_server import named_profile, self_profile

#: His volunteering page, the bare spelling, as ``readonly`` already admits it.
VOLUNTEERING_ADDRESS = "https://www.linkedin.com/in/me/opportunities/volunteering/education/"

#: The one parameter the drawn spelling carries.
PROFILE_ID_PARAM = "profileId"

#: The path beneath a member's root, which a drawn target must carry exactly.
_BENEATH_THE_MEMBER = "/opportunities/volunteering/education/"

_HOST = "www.linkedin.com"

#: ASCII case folding ONLY, as ``self_profile`` folds a vanity segment.
#: ``str.lower`` would fold a Unicode letter onto an ASCII one (the Kelvin sign
#: becomes ``k``), and a page could then draw a segment that is not his.
_ASCII_LOWER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")

#: The match's closed verdicts. ``match`` is the one that permits a press.
MATCH_WORDS = (
    "match",          # exactly the formed address: the press may be made
    "refused",        # his argument is missing or ill-shaped: no address formed
    "not_his_member",  # the landing is not a member, or the target names another
    "address",        # not an absolute https address on LinkedIn's host
    "path",           # a different page beneath the member
    "query",          # not exactly the one profileId parameter
    "fragment",       # a fragment rides on it
    "id_differs",     # the page's id is not his argument
)


class ProfileIdRefused(ValueError):
    """His profile id was missing or not of the member-id shape. The message
    is a closed sentence: the value is never in it."""


def volunteering_address(profile_id: Any) -> str:
    """The admitted spelling, formed from HIS ARGUMENT. PURE.

    Raises :class:`ProfileIdRefused` for a missing id or one not of
    ``named_profile.MEMBER_ID``'s shape -- an exact, case-sensitive match on a
    ``str``, so no space, quote, newline or second value can reach the
    address.
    """
    if profile_id is None or (isinstance(profile_id, str) and not profile_id.strip()):
        raise ProfileIdRefused(
            "no profile id was supplied: his volunteering page is formed only "
            "from the id the caller passes at runtime, and never from a page"
        )
    if not isinstance(profile_id, str) or not named_profile.MEMBER_ID.fullmatch(profile_id):
        raise ProfileIdRefused(
            "the profile id supplied is not shaped like a member id (the "
            "member-id prefix and alphabet, named_profile.MEMBER_ID), so no "
            "address is formed from it"
        )
    return VOLUNTEERING_ADDRESS + "?" + PROFILE_ID_PARAM + "=" + profile_id


def match_verdict(target: Any, profile_id: Any, landed_member: Optional[str]) -> str:
    """IS A DRAWN TARGET EXACTLY THE ADDRESS FORMED FROM HIS ARGUMENT? PURE.

    ``target`` is the href (or the menu item's declared address) the page
    drew; ``profile_id`` is HIS ARGUMENT; ``landed_member`` is the member
    segment of his root as the self-profile loader landed and proved it. The
    target's member segment is read as ``me`` only when it IS that member
    (ASCII case folded, as vanity segments are); everything else must be
    equal exactly. Returns one of :data:`MATCH_WORDS`.
    """
    try:
        formed = volunteering_address(profile_id)
    except ProfileIdRefused:
        return "refused"
    member = str(landed_member or "")
    if self_profile.landed_member_segment("https://" + _HOST + "/in/" + member + "/") is None:
        return "not_his_member"
    try:
        parts = urlsplit(str(target or "").strip())
    except ValueError:
        return "address"
    if parts.scheme != "https" or parts.netloc != _HOST:
        return "address"
    prefix = "/in/"
    if not parts.path.startswith(prefix):
        return "path"
    segment, slash, rest = parts.path[len(prefix):].partition("/")
    if not slash:
        return "path"
    drawn = self_profile.landed_member_segment("https://" + _HOST + "/in/" + segment + "/")
    if drawn is None or drawn.translate(_ASCII_LOWER) != member.translate(_ASCII_LOWER):
        return "not_his_member"
    if "/" + rest != _BENEATH_THE_MEMBER:
        return "path"
    if parts.fragment or "#" in str(target):
        return "fragment"
    pairs = parse_qsl(parts.query, keep_blank_values=True)
    if len(pairs) != 1 or pairs[0][0] != PROFILE_ID_PARAM or "&" in parts.query or ";" in parts.query:
        return "query"
    if pairs[0][1] != profile_id or parts.query != PROFILE_ID_PARAM + "=" + profile_id:
        return "id_differs"
    read_as_me = "https://" + _HOST + "/in/me" + _BENEATH_THE_MEMBER + "?" + parts.query
    return "match" if read_as_me == formed else "id_differs"


def link_matches(target: Any, profile_id: Any, landed_member: Optional[str]) -> bool:
    """True only on :func:`match_verdict`'s ``match``. PURE."""
    return match_verdict(target, profile_id, landed_member) == "match"
