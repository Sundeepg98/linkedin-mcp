"""A recommendation-surface reader that publishes COUNTS AND RELATIONS AND
NO NAMES -- and, unlike its sibling ``groups.py``, NO IDENTIFIER EITHER.

THIS IS A RULING BEING IMPLEMENTED, NOT A REFACTOR, and the ruling is the
wave lead's: a LinkedIn recommendation is written BY a named third party
ABOUT the operator (the "received" side) or BY the operator ABOUT a named
third party (the "given" side). Either way the surface is other people's
words sitting under their own names, so this reader publishes reads as
COUNTS and RELATIONS, never names and never text.

## WHY THIS MODULE CANNOT COPY GROUPS.PY'S OTHER HALF

``groups.py`` achieves name-freedom two ways at once: no name is a
parameter of any function in it, AND it still publishes a numeric
identifier, because a group id names a GROUP rather than a person. That
second half does not transfer here, and the reason is the SHAPE OF THE
HREF rather than a stricter mood:

    a group id is an OPAQUE NUMBER. A group's NAME can happen to be a
    person's name -- that is the whole finding ``groups.py`` answers --
    but no run of digits is one.

    a recommendation author's href is a member profile link, and
    LinkedIn's OWN DEFAULT is to BUILD that link's slug out of the
    person's real name. The identifier here is not occasionally
    name-shaped; it is name-shaped BY CONSTRUCTION, on every profile
    that has never hand-edited its public url.

So there is no publishable identifier on this surface at all, and the
structural property this module keeps is STRONGER than ``groups.py``'s:

    **NO PUBLIC FUNCTION IN THIS MODULE RETURNS ANY STRING DERIVED FROM
    ITS INPUT.** Every value in every returned dict is an int, a bool, or
    a string drawn from a CLOSED VOCABULARY of module-level literals
    (:data:`RELATIONS`, :data:`REFUSALS`, :data:`PUBLISHED_HREF`).
    Distinctness is computed from the inputs INTERNALLY, by a private
    helper whose output never crosses a ``return`` in a public function,
    and is published only as a COUNT.

``test_recommendation_tally.py`` asserts both halves of that sentence on
the signatures and on real payloads, because a property asserted only in a
docstring is the defect this repository has named more than once.

## WHY A DIGEST WAS REJECTED, AND WHY IT IS WORSE HERE THAN FOR A GROUP

``groups.py`` considered and rejected hashing an eight-digit group id,
because a digest over an eight-digit domain is brute-forceable end to end
and would look like a redaction while being a lookup table. The same
reasoning applies here and the domain is WORSE, not merely equal:

* a slug is not a bounded numeric run to exhaustively hash -- it is short
  alphanumeric text, and the realistic attack is not "hash every possible
  slug" but "hash the one or two names I already suspect" -- a colleague,
  a manager, a specific candidate -- and compare. A targeted guess-and-
  check needs no brute force at all;
* LinkedIn's default slug already carries the structure a guesser needs
  (given name, family name, a numeric disambiguator), so the space a real
  adversary explores is not "every string of this length" but "every
  plausible spelling of a name they already have," which is small;
* and a digest would still answer the one question this module exists to
  refuse -- "did a specific named person appear here." Hashing the slug
  does not remove that oracle, it just makes the reader feel safer
  publishing it.

So no identifier, hashed or plain, is published by any function below.

## THE MARKER, IMPORTED WHERE IT EXISTS AND DERIVED WHERE IT DOES NOT

``shape._CENSUS_ENTITY_HREFS`` already carries the member marker alongside
company, newsletter, school, group and event -- but unlike
``_MEMBERSHIP_HREF_MARKER`` or ``_SUBSCRIPTION_HREF_MARKER``, ``shape.py``
has no standalone constant naming the member marker on its own, because no
existing reader needed to select it as the ONE kind a row is allowed to be
about. :data:`MEMBER_MARKER` below is therefore DERIVED locally by
filtering the shared tuple for its member entry, rather than copied as a
new literal -- so a future edit to that entry in ``shape.py`` is still
picked up automatically, the same inheritance ``groups.py`` gets from
importing ``_MEMBERSHIP_FOREIGN_MARKERS`` outright.

## WHAT THIS MODULE IS NOT

* It is **not** a replacement for a name-publishing reader, because this
  codebase has none for this surface. ``shape.py`` carries no
  recommendation-row counterpart to ``membership_row`` -- searched for and
  not found. If one is written later, the same argument that makes this
  module name-free applies to it without needing a new ruling.
* It **does not open a page.** It takes hrefs somebody else read, the same
  precondition ``groups.py`` states for itself.
* It makes no claim about which section a row sat under. The caller
  supplies ``relation`` (``"received"`` or ``"given"``); this module
  trusts that label and counts what it is handed under it.
* It is **not** the write side. Requesting a recommendation, writing one
  for somebody, or accepting or declining a request are outward-facing
  acts that name a real person, and none of them is implemented here. A
  related action, ``endorse_or_recommend``, already sits in
  ``writes.PERMANENTLY_FORBIDDEN`` for adjacent reasons (measured zero
  endorse controls across every tracked fixture and his own live
  profile) -- but that entry was not re-verified for this module, and
  this paragraph makes no claim about recommendation-specific writes
  beyond: they are not here.

## MEASURED VERSUS ASSERTED

**Nothing below has been run against a live capture of the
Recommendations surface.** The branch structure -- foreign-marker check
before member check, query and fragment dropped first, a bare member
root refused -- is carried over from ``groups.py``'s measured design and
from the shapes ``shape._CENSUS_ENTITY_HREFS`` already carries, not from
an observed Recommendations page. Anywhere a comment below describes an
href shape, that shape is ASSERTED from the general member-profile-link
convention documented elsewhere in ``shape.py``, never claimed as
something this module's author watched LinkedIn render.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import urlsplit

from linkedin_server import shape

#: THE MEMBER MARKER, DERIVED RATHER THAN RETYPED. ``shape.py`` has no
#: ``_MEMBER_HREF_MARKER``-style constant of its own (see the module
#: docstring), so this filters the shared entity tuple for the one entry
#: that names a member profile, selecting on the durable structural
#: prefix rather than the full placeholder text -- a rename of the
#: bracketed part in ``shape.py`` still resolves correctly here.
MEMBER_MARKER = next(
    marker for marker in shape._CENSUS_ENTITY_HREFS if marker.startswith("/in/")
)

#: EVERY OTHER ENTITY KIND SHAPE KNOWS ABOUT. Derived, not copied, so a
#: SEVENTH entity kind added to ``shape._CENSUS_ENTITY_HREFS`` tomorrow
#: becomes a refusal here automatically rather than a hole -- the same
#: property ``groups.FOREIGN_MARKERS`` gets from importing its own tuple
#: outright, reproduced here because no ready-made tuple excludes only
#: the member marker.
FOREIGN_MARKERS = tuple(
    marker for marker in shape._CENSUS_ENTITY_HREFS if marker != MEMBER_MARKER
)

#: THE SAME MARKERS AS PATH SEGMENTS. This module matches on THESE, an
#: exact segment comparison, rather than running ``census_substitute``
#: over the path -- see ``groups.py``'s own module docstring for why that
#: coupling is backwards: the substitution buys nothing once the path is
#: already split into segments, and it blanks the very digit-and-letter
#: run this module would otherwise need to detect the presence of.
FOREIGN_SEGMENTS = tuple(marker.split("/")[1] for marker in FOREIGN_MARKERS)

#: The path segment that introduces a member profile link ("in"), taken
#: from the marker rather than written again so the two cannot disagree.
_PATH_KEY = MEMBER_MARKER.split("/")[1]

#: THE ONE STRING THIS MODULE EVER PUBLISHES, and it is deliberately NOT
#: shaped like a url. ``groups.py`` and ``newsletter.py`` publish a
#: marker-shaped literal (``/groups/<group>/``) because their surfaces
#: DO have a safe identifier to gesture at the shape of. This surface has
#: none -- see the module docstring's first section -- so the published
#: literal does not even resemble an href, which is the whole point: a
#: reader of this module's output cannot mistake it for a redacted real
#: value, because it was never shaped like one.
PUBLISHED_HREF = "<a recommender>"

#: THE CLOSED RELATION VOCABULARY. A recommendation row is either
#: something a third party wrote ABOUT the operator, or something the
#: operator wrote about a third party -- there is no third relation on
#: this surface.
RELATIONS = ("received", "given")

#: THE CLOSED REFUSAL VOCABULARY. The first four come from
#: :func:`_member_segment`'s branch structure; the fifth is
#: :func:`recommendation_tally`'s own gate on ``relation`` and is never
#: produced by anything that parses an href.
REFUSALS = (
    "no_href",
    "href_identifies_another_kind_of_entity",
    "not_a_member_href",
    "member_root_carries_no_identifier",
    "invalid_relation",
)

#: Internal parse status -> public refusal reason, so the mapping lives in
#: exactly one place and the two vocabularies cannot drift apart.
_REFUSAL_FOR_STATUS = {
    "no_href": REFUSALS[0],
    "foreign": REFUSALS[1],
    "absent": REFUSALS[2],
    "root": REFUSALS[3],
}


def _member_segment(href: Optional[str]):
    """INTERNAL PARSER, shared by presence-checking and internal dedup keys.

    Returns ``(status, segment, foreign)``:

    * ``status`` is one of ``"ok"``, ``"no_href"``, ``"foreign"``,
      ``"absent"`` or ``"root"``;
    * ``segment`` is the raw slug text, and ONLY present (non-``None``)
      when ``status == "ok"``;
    * ``foreign`` is the list of foreign markers seen, non-empty only
      when ``status == "foreign"``.

    **``segment`` NEVER LEAVES THIS MODULE THROUGH A PUBLIC RETURN.**
    :func:`author_present` reduces it to a boolean; :func:`recommendation_tally`
    and :func:`relation_split` (via :func:`_distinct_keys`) reduce sets of
    it to a COUNT. This function itself is private and is not part of the
    contract the test file's signature sweep certifies -- what that sweep
    certifies is that nothing derived from ITS OUTPUT reaches a public
    return, which is checked behaviourally rather than by this docstring.

    THE ORDER OF THE CHECKS IS PART OF THE CONTRACT, the same order
    ``groups.group_identifier`` uses and for the same reasons:

    1. an empty href refuses before anything is parsed;
    2. the query and fragment are dropped via ``urlsplit(href).path``
       BEFORE any marker is looked for, so nothing riding in a query
       string or fragment -- safe or not -- can influence a classification
       that only the PATH is supposed to decide;
    3. the FOREIGN markers are checked before the member marker, so a
       path carrying both -- a company or group link that also contains a
       member segment -- is refused as foreign rather than accepted as an
       author link. The conservative direction is the one where an
       ambiguous row is never counted as a person.
    """
    if not href or not str(href).strip():
        return "no_href", None, []

    # THE QUERY AND FRAGMENT GO FIRST AND ARE NOT LOOKED AT. urlsplit().path
    # returns the path alone.
    path = urlsplit(str(href).strip()).path

    segments = [segment for segment in path.split("/") if segment]

    # AN EXACT SEGMENT MATCH, not a substring search over a shaped string.
    # See FOREIGN_SEGMENTS above for why the shaper was left out of this path.
    foreign = [
        marker
        for marker, key in zip(FOREIGN_MARKERS, FOREIGN_SEGMENTS)
        if key in segments
    ]
    if foreign:
        return "foreign", None, foreign

    if _PATH_KEY not in segments:
        return "absent", None, []

    index = segments.index(_PATH_KEY)
    if index + 1 >= len(segments):
        return "root", None, []

    return "ok", segments[index + 1], []


def author_present(href: Optional[str]) -> dict[str, Any]:
    """Does this href identify a PERSON who authored a recommendation?

    Returns one of two shapes and never raises, because one unusable row
    on a page of a handful is not an error:

    ``{"present": True, "href_shape": PUBLISHED_HREF}``
    ``{"present": False, "refused": <one of REFUSALS>, "saw": [...], "why": "..."}``

    **NEVER RETURNS THE SLUG, THE PATH, OR ANY SUBSTRING OF HREF.** Unlike
    ``groups.group_identifier``, which this module's docstring explains
    cannot be copied here, this function does not attempt to hand back an
    identifier even on success -- the ``present: True`` shape carries
    nothing but the fact and the one published literal.

    A REFUSAL REPORTS WHAT IT DID SEE, drawn from the closed marker
    vocabulary and never a substring of the actual href -- see
    ``groups.group_identifier`` for why a refusal naming only the absence
    is half a measurement.

    THE QUERY AND FRAGMENT ARE DROPPED FIRST, via ``urlsplit(href).path``,
    before any marker is looked for -- see :func:`_member_segment`.

    AND THE FOREIGN CHECK RUNS BEFORE THE MEMBER CHECK, so a path carrying
    both a foreign marker and a member segment is refused as foreign
    rather than accepted as an author link -- the conservative direction,
    same as ``groups.group_identifier``.

    MEASURED: nothing. See the module docstring's final section.
    """
    status, _segment, foreign = _member_segment(href)

    if status == "ok":
        return {"present": True, "href_shape": PUBLISHED_HREF}

    if status == "no_href":
        return {
            "present": False,
            "refused": _REFUSAL_FOR_STATUS["no_href"],
            "saw": [],
            "why": (
                "a row with no destination cannot be shown to identify a "
                "recommendation's author, and this gate refuses what it "
                "cannot establish."
            ),
        }

    if status == "foreign":
        return {
            "present": False,
            "refused": _REFUSAL_FOR_STATUS["foreign"],
            "saw": foreign,
            "why": (
                "this row points at something other than a member "
                "profile. It is REFUSED rather than counted as an author "
                "-- a row counted as an author because nothing refused it "
                "is worse than one refused."
            ),
        }

    if status == "root":
        return {
            "present": False,
            "refused": _REFUSAL_FOR_STATUS["root"],
            "saw": [MEMBER_MARKER],
            "why": (
                "the member segment carries no slug after it, so this "
                "points at profile-root or navigation furniture rather "
                "than at a specific person."
            ),
        }

    # status == "absent": the foreign check above already covers every
    # OTHER entity kind shape._CENSUS_ENTITY_HREFS knows about, so by the
    # time this branch is reached there is genuinely nothing left in the
    # closed vocabulary to report having seen -- unlike the foreign
    # branch, an empty "saw" here is the honest answer rather than a
    # missed one.
    return {
        "present": False,
        "refused": _REFUSAL_FOR_STATUS["absent"],
        "saw": [],
        "why": (
            "no member segment in the path. An author is identified by "
            "where the row points, never by which section of the page it "
            "sits under."
        ),
    }


def _distinct_keys(hrefs: Iterable[Optional[str]]) -> set:
    """INTERNAL ONLY: the set of raw slug segments found present.

    Used solely for local set arithmetic (distinct counts, reciprocal
    overlap). NEVER returned to a caller -- every public function that
    uses this reduces the result to a COUNT before anything crosses a
    ``return``.
    """
    keys: set = set()
    for href in hrefs:
        status, segment, _foreign = _member_segment(href)
        if status == "ok":
            keys.add(segment)
    return keys


def recommendation_tally(hrefs: Iterable[Optional[str]], relation: str) -> dict[str, Any]:
    """Count a list of recommendation-row hrefs under one relation.

    ``relation`` MUST be one of :data:`RELATIONS`. AN OUT-OF-VOCABULARY
    RELATION IS REFUSED EXPLICITLY rather than raised, and ``hrefs`` is
    NOT EVEN ITERATED in that case: this function will not read a
    caller-supplied iterable whose shape it has already decided not to
    trust. The return then carries ``"relation": None`` -- never the
    invalid value the caller passed, because :data:`RELATIONS` is a
    closed vocabulary and this field only ever echoes a MEMBER of it.

    Returns::

        {
            "relation":         the validated relation, or None if refused,
            "rows":             hrefs handed in (0 if the relation was refused),
            "authors":          how many were identified as an author link,
            "distinct_authors": how many DISTINCT authors those carried,
            "refused":          {reason: count},
            "href_shape":       the one literal this module ever publishes,
        }

    ``rows`` and ``authors`` are reported separately for the reason
    ``groups.membership_tally`` gives: a caller handed ten rows and shown
    six authors can see that four were refused, where a bare
    ``authors: 6`` reads identically whether four were refused or none
    were offered.

    ``distinct_authors`` IS NOT ``authors``, for the same reason
    ``groups.py`` computes ``distinct`` separately from ``groups``: the
    SAME author can appear on a page twice, written as a relative href on
    one row and an absolute href on another (measured for group hrefs on
    the Groups surface; asserted here by the general member-profile-link
    convention rather than by a capture of this specific surface -- see
    the module docstring's MEASURED VERSUS ASSERTED section). The
    precondition this surface exists to answer is a DISTINCT count, so it
    is computed here rather than left to a caller to get right.
    """
    if relation not in RELATIONS:
        return {
            "relation": None,
            "rows": 0,
            "authors": 0,
            "distinct_authors": 0,
            "refused": {"invalid_relation": 1},
            "href_shape": PUBLISHED_HREF,
        }

    keys: list = []
    refused: dict[str, int] = {}
    rows = 0
    for href in hrefs:
        rows += 1
        status, segment, _foreign = _member_segment(href)
        if status == "ok":
            keys.append(segment)
            continue
        reason = _REFUSAL_FOR_STATUS[status]
        refused[reason] = refused.get(reason, 0) + 1

    return {
        "relation": relation,
        "rows": rows,
        "authors": len(keys),
        "distinct_authors": len(set(keys)),
        "refused": refused,
        "href_shape": PUBLISHED_HREF,
    }


def relation_split(
    received: Iterable[Optional[str]], given: Iterable[Optional[str]]
) -> dict[str, Any]:
    """Do the same people appear on both sides? COUNTS ONLY, NO IDENTIFIER.

    ``received`` and ``given`` are hrefs from the two sides of the
    Recommendations surface. Returns::

        {
            "received_distinct":  how many distinct authors wrote TO him,
            "given_distinct":     how many distinct people he wrote FOR,
            "reciprocal":         how many appear on BOTH sides,
            "reciprocal_present": whether that count is nonzero,
        }

    ``reciprocal`` is the deciding measurement this function exists for --
    the same role ``groups.disjoint`` plays for group membership -- and it
    is answerable ONLY because distinctness is computed INTERNALLY from
    the actual slug text for the sole purpose of set membership. That text
    never leaves this function: two sets are intersected and only their
    SIZES cross the return.
    """
    received_keys = _distinct_keys(received)
    given_keys = _distinct_keys(given)
    common = received_keys & given_keys
    return {
        "received_distinct": len(received_keys),
        "given_distinct": len(given_keys),
        "reciprocal": len(common),
        "reciprocal_present": bool(common),
    }
