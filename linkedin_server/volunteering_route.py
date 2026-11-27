"""HIS ROOT'S LINKS, MATCHED EXACTLY -- AND HIS VOLUNTEERING PAGE, THE ID FROM HIM.

THE ONE MATCHER SESSION 14 IMPORTS, for every press on his own profile root:
queue lines 30, 31, 64, 67 and 68 through :func:`exact_link_verdict`, and line
69, his volunteering page, through :func:`match_verdict`, which forms its
address and hands it to the same function. One matcher, not two.

## THE MATCH RULE (SELF-ROOT-LINK-PRESS-BY-EXACT-MATCH, amended 2026-11-27 13:10,
## and EXACT-MATCH-REFUSES-ANY-WHITESPACE, 2026-11-27 17:20)

A link (or a menu item's declared address) drawn on his root may be pressed
only when :func:`exact_link_verdict` answers ``match``:

1. THE TARGET IS NEVER NORMALISED. Nothing is stripped, folded, decoded or
   re-spelled before it is compared; the raw string the page drew is the
   string judged.
2. ANY OF THESE, ANYWHERE IN IT, REFUSES (``unsafe_character``): a character
   with ``str.isspace()`` true; a C0 or C1 control, or DEL; any character
   outside printable ASCII. In one closed range: every character must lie in
   ``!`` to ``~`` (U+0021 to U+007E), so the space itself refuses too.
3. ANY PERCENT ESCAPE OF WHITESPACE OR A CONTROL REFUSES (``encoded_unsafe``):
   ``%00`` to ``%20``, ``%7F``, and any escaped UTF-8 sequence that decodes to
   whitespace, a control, a format character (a zero-width space, a byte-order
   mark), a separator, or nothing valid (``%C2%A0``, ``%C2%85``, ``%E3%80%80``,
   ``%E2%80%8B`` and the like); so does a ``%`` that does not begin a
   two-hex-digit escape. An escaped LETTER -- how a vanity segment outside
   ASCII is drawn -- is not refused by this clause.
4. THEN THE RAW STRING IS COMPARED, CHARACTER FOR CHARACTER, with the address
   ``readonly.py`` admits for that line. Its only two equivalences: the
   admission's own constant query is part of the address (rank 31's
   ``profileFormEntryPoint=identityModuleMirror``), and ``me`` may be written
   as his landed member -- the segment the self-profile loader landed on and
   proved his, EXACTLY as it landed, with no case folded. Nothing else:
   another member, case, query, parameter, fragment or path refuses.
5. The address must itself be one ``readonly.py`` admits, on his own
   ``/in/me/`` spelling (``not_admitted`` otherwise): a runner cannot widen the
   match by passing some other address.

WHY (the cold verifier, 2026-11-27): the first version compared
``urlsplit(str(target).strip())``. ``str.strip`` removes Unicode whitespace the
browser's URL parser KEEPS -- that parser strips only C0 controls and the
space -- and ``urlsplit`` drops tabs and newlines on its own terms. So a page
could draw an href with a leading U+00A0, or a trailing U+3000, U+00A0 or
U+0085, that read ``match`` here while the browser followed it to another
address. A page that can SUPPLY a lookalike target defeats the rule; a
matcher that never normalises cannot be shown one.

## HIS VOLUNTEERING PAGE

LinkedIn draws his "Open to volunteering" page (census ``P D24``) only as
``/in/<member>/opportunities/volunteering/education/?profileId=<his own id>``:
on his profile root's card link and in the ``Open to`` menu's item, both
measured (``_audit/2026-11-27-prof7.md``; ``_audit/_slice-otw-census.md``).
VOLUNTEERING-BARE-SPELLING-FIRST (the orchestrator, 2026-11-25) took the bare
spelling first -- "if it does not land, profileId from tool arguments at
runtime (his own id, never stored)" -- and the bare spelling landed on his
profile root (the live lane's session 12, load 22). So the fallback has its
boundary (VOLUNTEERING-FALLBACK-BOUNDARY, the orchestrator, 2026-11-27):

* ``readonly`` admits the ``/in/me/`` spelling with ONE ``profileId`` of the
  member-id shape (``named_profile.MEMBER_ID``), and nothing else;
* the id comes ONLY from the caller's arguments at runtime, validated by that
  shape; a missing or ill-shaped id REFUSES (:class:`ProfileIdRefused`, whose
  message never quotes it);
* THE PAGE NEVER SUPPLIES IT: :func:`match_verdict` forms the address from his
  argument, and the drawn target must equal it by the rule above.

## WHAT THIS MODULE NEVER DOES

It logs nothing, prints nothing, writes nothing and stores nothing, and it
never navigates: the formed address goes back to its caller and nowhere else,
and the verdicts are closed words (:data:`MATCH_WORDS`) and booleans. A
refusal names what was wrong in closed words, never the value.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional
from urllib.parse import parse_qsl, urlsplit

from linkedin_server import named_profile, readonly, self_profile

#: His volunteering page, the bare spelling, as ``readonly`` already admits it.
VOLUNTEERING_ADDRESS = "https://www.linkedin.com/in/me/opportunities/volunteering/education/"

#: The one parameter the drawn spelling carries.
PROFILE_ID_PARAM = "profileId"

#: A member's profile root, and his own under the self alias.
_MEMBER_ROOT = "https://www.linkedin.com/in/"
_ALIAS_ROOT = _MEMBER_ROOT + self_profile.SELF_ALIAS + "/"

#: The match's closed verdicts. ``match`` is the one that permits a press.
MATCH_WORDS = (
    "match",             # exactly the admitted address: the press may be made
    "refused",           # his argument is missing or ill-shaped: no address formed
    "not_admitted",      # the address is not one readonly.py admits on his /in/me/ spelling
    "unsafe_character",  # whitespace, a control or a character outside printable ASCII
    "encoded_unsafe",    # a percent escape of whitespace or a control, or a broken escape
    "not_his_member",    # the landing is not a member, or the target names another
    "address",           # not an absolute https address on LinkedIn's host
    "path",              # a different page beneath the member
    "query",             # not exactly the admission's own query
    "fragment",          # a fragment rides on it
    "id_differs",        # the page's id is not his argument
)

#: A run of percent escapes, and a percent sign that begins none.
_ESCAPE_RUN = re.compile(r"(?:%[0-9A-Fa-f]{2})+")
_BROKEN_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")

#: Unicode categories an escaped character may not decode into: controls,
#: format characters, surrogates, private use, unassigned, and separators.
_UNSAFE_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Co", "Cn", "Zs", "Zl", "Zp"})


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


def _has_unsafe_character(raw: str) -> bool:
    """Clause 2: anything outside ``!`` to ``~``. PURE."""
    return any(not ("!" <= character <= "~") for character in raw)


def _has_encoded_unsafe(raw: str) -> bool:
    """Clause 3: a broken escape, or escapes decoding to whitespace, a control,
    a format character, a separator or no valid UTF-8. PURE."""
    if _BROKEN_ESCAPE.search(raw):
        return True
    for run in _ESCAPE_RUN.findall(raw):
        octets = bytes.fromhex(run.replace("%", ""))
        if any(octet < 0x21 or octet == 0x7F for octet in octets):
            return True
        try:
            decoded = octets.decode("utf-8")
        except UnicodeDecodeError:
            return True
        for character in decoded:
            if character.isspace() or unicodedata.category(character) in _UNSAFE_CATEGORIES:
                return True
    return False


def _admitted_on_his_root(admitted: Any) -> bool:
    """Clause 5: an address readonly.py admits, on his own /in/me/ spelling. PURE."""
    return (
        isinstance(admitted, str)
        and admitted.startswith(_ALIAS_ROOT)
        and not _has_unsafe_character(admitted)
        and readonly.is_read_url(admitted)
    )


def exact_link_verdict(target: Any, admitted: Any, landed_member: Optional[str]) -> str:
    """THE ONE MATCHER: is ``target``, as drawn, exactly ``admitted``? PURE.

    ``target`` is the href (or the menu item's declared address) the page
    drew, judged RAW; ``admitted`` is the address readonly.py admits for the
    line, on his ``/in/me/`` spelling; ``landed_member`` is the member segment
    of his root as the self-profile loader landed and proved it. Returns one of
    :data:`MATCH_WORDS`, ``match`` only by the module's rule.
    """
    if not _admitted_on_his_root(admitted):
        return "not_admitted"
    member = landed_member if isinstance(landed_member, str) else ""
    if self_profile.landed_member_segment(_MEMBER_ROOT + member + "/") != member:
        return "not_his_member"
    if not isinstance(target, str) or not target:
        return "address"
    if _has_unsafe_character(target):
        return "unsafe_character"
    if _has_encoded_unsafe(target):
        return "encoded_unsafe"
    as_drawn = _MEMBER_ROOT + member + "/" + admitted[len(_ALIAS_ROOT):]
    if target == as_drawn or target == admitted:
        return "match"
    return _why_not(target, as_drawn)


def _why_not(target: str, as_drawn: str) -> str:
    """WHICH PART DIFFERS, for a refusal to name -- never ``match``: it runs
    only after the exact comparison failed, on a target already clear of every
    unsafe character, so nothing here can turn a refusal into a press."""
    got, want = urlsplit(target), urlsplit(as_drawn)
    if (got.scheme, got.netloc) != (want.scheme, want.netloc) or not got.path.startswith("/in/"):
        return "address"
    got_member, slash, got_rest = got.path[len("/in/"):].partition("/")
    want_member, _slash, want_rest = want.path[len("/in/"):].partition("/")
    if not slash:
        return "path"
    if got_member not in (want_member, self_profile.SELF_ALIAS):
        return "not_his_member"
    if got_rest != want_rest:
        return "path"
    if got.fragment or "#" in target:
        return "fragment"
    got_pairs = parse_qsl(got.query, keep_blank_values=True)
    want_pairs = parse_qsl(want.query, keep_blank_values=True)
    if (
        len(got_pairs) == len(want_pairs) == 1
        and got_pairs[0][0] == want_pairs[0][0] == PROFILE_ID_PARAM
    ):
        return "id_differs"
    return "query"


def match_verdict(target: Any, profile_id: Any, landed_member: Optional[str]) -> str:
    """HIS VOLUNTEERING PAGE'S MATCH: the address formed from HIS ARGUMENT,
    judged by :func:`exact_link_verdict`, the one matcher. PURE.

    ``refused`` when his argument is missing or ill-shaped -- whatever the
    page drew, the page never stands in for his argument.
    """
    try:
        formed = volunteering_address(profile_id)
    except ProfileIdRefused:
        return "refused"
    return exact_link_verdict(target, formed, landed_member)


def link_matches(target: Any, profile_id: Any, landed_member: Optional[str]) -> bool:
    """True only on :func:`match_verdict`'s ``match``. PURE."""
    return match_verdict(target, profile_id, landed_member) == "match"
