"""A feed reader that publishes COUNTS AND KINDS AND NOTHING ELSE -- no
name, no identifier, and no post text, enforced by the SIGNATURE rather
than by a filter.

THIS IS A RULING BEING IMPLEMENTED, NOT A REFACTOR. The wave lead's
ruling, verbatim in substance:

    reading the feed means reading other people's posts. COUNTS AND
    RELATIONS ONLY, NEVER TEXT OR NAMES, built structurally as
    ``recommendations.py`` and ``groups.py`` were. ``census_substitute``
    returns a person's name UNCHANGED, so no shape-based guard will save
    you -- the property has to be in the SIGNATURE, not in a filter.

That last clause is the whole design and it is why this module is not
simply a third copy of ``groups.py``.

## WHY A FILTER CANNOT DEFEND THIS SURFACE, AND THE SIGNATURE CAN

``census_substitute`` is a SHAPE detector. It finds urns, ``/in/`` paths,
possessives, long digit runs. A person's name carries none of those, and
the measurement exists: a newsletter title of the form
``<publication> by <author>`` passed through it INTACT, and that defect is
live in a shipped gate one surface over. Names are not detectable by
shape, so a reader that accepts free text and filters it afterwards is
defending the feed with an instrument that cannot see the thing it is
aimed at.

The feed is the worst possible surface for that arrangement. A feed row's
payload is, by construction:

* a post BODY written by somebody else, in which a name is ordinary prose;
* an author's DISPLAY NAME, which is a person's name with nothing around
  it at all;
* a "reason" header (*so-and-so commented on this*), which is a name
  inside a sentence.

Every one of those defeats a shape filter completely. So this module does
not filter them.

    **NO PUBLIC FUNCTION IN THIS MODULE ACCEPTS FREE TEXT, AND NO PUBLIC
    FUNCTION RETURNS A STRING DERIVED FROM ITS INPUT.**

Both halves are asserted in ``tests/test_feed_tally.py``, and the first
half is the one that is new here. ``recommendations.py`` guarantees only
the RETURN side, which is sufficient for a surface whose input is a list
of hrefs. It is NOT sufficient here, because the obvious next commit on a
feed reader is a ``text=`` or ``author_name=`` parameter added in good
faith by somebody who intends to count something with it. **A leak needs
a route in before it needs a route out.** Closing the input side means
the dangerous version of this module cannot be written without deleting a
test that says so.

Concretely: the signature test enumerates every public callable and
asserts each parameter name is drawn from a CLOSED, declared set
(:data:`_PERMITTED_PARAMETER_NAMES`). Adding ``text`` turns it red before
anything has been printed anywhere.

## WHAT IT PUBLISHES INSTEAD: THE KIND, NEVER THE ENTITY

An author on the feed is one of the six entity kinds
``shape._CENSUS_ENTITY_HREFS`` already knows about. This module resolves
an href to its KIND and stops there.

    /in/<member>          -> "member"
    /company/<company>    -> "company"
    /newsletters/<...>    -> "newsletter"
    /school/<school>      -> "school"
    /groups/<group>       -> "group"
    /events/<event>       -> "event"

**No identifier is published for ANY kind, including the kinds where one
would arguably be safe.** ``groups.py`` publishes an opaque numeric group
id and argues correctly that no run of digits is a person's name. That
argument is available here for groups and events and is deliberately not
taken, for two reasons:

1. a UNIFORM guarantee is testable in one sentence and a per-kind one is
   not. "This module returns no string derived from its input" is a
   property a signature sweep can certify mechanically. "This module
   returns identifiers for two of six kinds" needs a case analysis that
   drifts the first time a seventh kind is added;
2. a company slug is not always a company. A personal-brand Page is named
   after its owner, and ``/company/<a person's name>`` is an ordinary
   shape on LinkedIn. So the one kind where publishing an identifier
   looks obviously harmless is a kind where it is sometimes a name.

The cost is real and is stated rather than hidden: **a caller cannot ask
this module WHICH author dominated the feed, only THAT one did.** See
:func:`authorship_concentration`, which computes exactly that and
publishes it as an integer.

## THE AMBIGUITY BRANCH IS WHERE THIS DIFFERS FROM ITS TWO SIBLINGS

``groups.py`` and ``recommendations.py`` each nominate ONE kind as the
kind their surface is about and refuse every other as "foreign". The feed
has no such privileged kind -- a member post and a company post are both
ordinary feed content -- so "foreign" is not a category here at all.

That removes a refusal and creates a new one. A path carrying TWO entity
segments (``/company/<x>/people/in/<y>``, and LinkedIn draws paths of
that family) would, under a first-match-wins rule, be silently attributed
to whichever check happened to run first. **An ordering accident is not a
classification.** So:

    :func:`author_kind` collects EVERY entity segment present and refuses
    outright when more than one is found.

The conservative direction is the one where an ambiguous row is counted
as nothing, never as a person. This is the branch the mutation control in
the test file is aimed at, because it is the branch whose absence is
invisible in the output -- a wrong kind and a right kind are both just a
word.

**MEASURED, and it is worse than first-match-wins sounds.** With that
check neutralised, ``/company/<x>/people/in/<y>`` resolves to
``kind: "member"``, not to ``"company"`` -- because this module inherits
``shape._CENSUS_ENTITY_HREFS``' ordering, in which ``in`` comes first. So
the failure mode of a first-match-wins rule on this surface is to
attribute a COMPANY's people directory TO A PERSON, which is the one
thing the ruling behind this module exists to prevent. The author of this
docstring guessed ``"company"`` and the mutation said otherwise.

## THE QUERY AND FRAGMENT GO FIRST, AND THAT IS PART OF THE CONTRACT

``urlsplit(href).path`` is taken BEFORE any marker is looked for, so
nothing riding in a query string or a fragment can influence a
classification that only the path is supposed to decide. Feed hrefs carry
tracking parameters routinely, and some of them carry the very segment
names this module matches on.

## BOUNDARY COST: ZERO, AND IT WAS RE-DERIVED RATHER THAN RECALLED

``readonly._ALLOWED_URL_PATTERNS`` already admits the feed root, and
``/feed/update/`` is separately admitted. **This module adds no pattern,
edits no list, and touches no digest.** It also opens no page: like
``recommendations.py`` it is handed hrefs somebody else read.

## MEASURED VERSUS ASSERTED -- read this before quoting anything here

**NOTHING BELOW HAS BEEN RUN AGAINST A LIVE CAPTURE OF THE FEED.** No
page was opened for this module. What IS measured, elsewhere and cited
rather than re-derived:

* the six entity markers and the fact that they were originally written
  FOR the feed (``shape._CENSUS_ENTITY_HREFS``, whose own comments say
  so);
* that a name survives ``census_substitute`` unchanged;
* that the feed root is already admitted by the read boundary.

What is ASSERTED and labelled as such: that a feed row's author control
points at one of those six kinds, and that two-entity paths occur. The
branch structure is carried over from ``groups.py``'s measured design,
not from an observed feed. **This module deliberately does NOT contain a
DOM reader**, for the reason the newsletter wave gave for declining one:
an invented selector fails closed and returns "his feed has no authors",
which is indistinguishable from the answer the surface exists to produce.
Whoever opens the page first writes that half, and their zero will mean
something because this half already refuses to publish a name.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import urlsplit

from linkedin_server import shape

#: THE SIX ENTITY KINDS, DERIVED FROM ``shape.py`` RATHER THAN RETYPED, so
#: a SEVENTH kind added there tomorrow becomes a resolvable kind here
#: automatically instead of a silent hole. The key is the path segment
#: (``in``, ``company``, ...); the value is the public kind word.
#:
#: The kind word is derived from the segment rather than written beside
#: it, so the two cannot disagree: a marker renamed in ``shape.py``
#: renames the published word too, and a test pins the mapping so that a
#: rename is visible in a diff rather than silent.
_SEGMENT_FOR_MARKER = {
    marker.split("/")[1]: marker.split("/")[1] for marker in shape._CENSUS_ENTITY_HREFS
}

#: The published kind word for each path segment. Two segments are
#: PLURAL in the path and singular as a kind (``newsletters`` ->
#: ``newsletter``, ``groups`` -> ``group``, ``events`` -> ``event``);
#: these three are the only entries that are not the segment verbatim,
#: and they are spelled out so a reader can see exactly which words this
#: module can emit.
_KIND_FOR_SEGMENT = {
    "in": "member",
    "company": "company",
    "newsletters": "newsletter",
    "school": "school",
    "groups": "group",
    "events": "event",
}

#: THE CLOSED KIND VOCABULARY -- every word :func:`author_kind` can put in
#: its ``kind`` field. Built by intersecting the two dicts above so that a
#: kind exists here ONLY if ``shape.py`` still carries its marker. An
#: entry removed from ``shape._CENSUS_ENTITY_HREFS`` disappears from this
#: tuple rather than lingering as a word this module can still emit.
AUTHOR_KINDS = tuple(
    _KIND_FOR_SEGMENT[segment]
    for segment in _SEGMENT_FOR_MARKER
    if segment in _KIND_FOR_SEGMENT
)

#: The path segments this module recognises, in the same order.
_ENTITY_SEGMENTS = tuple(
    segment for segment in _SEGMENT_FOR_MARKER if segment in _KIND_FOR_SEGMENT
)

#: THE ONE STRING THIS MODULE EVER PUBLISHES OFF AN HREF, and as in
#: ``recommendations.py`` it is deliberately NOT shaped like a url. A
#: reader of this module's output must not be able to mistake it for a
#: redacted real value, because it was never shaped like one.
PUBLISHED_HREF = "<a feed author>"

#: THE CLOSED REFUSAL VOCABULARY. Four reasons, each produced by exactly
#: one branch of :func:`_entity_key`.
REFUSALS = (
    "no_href",
    "not_an_entity_href",
    "entity_root_carries_no_identifier",
    "ambiguous_multiple_entity_kinds",
)

#: Internal parse status -> public refusal reason, so the mapping lives in
#: one place and the two vocabularies cannot drift.
_REFUSAL_FOR_STATUS = {
    "no_href": REFUSALS[0],
    "absent": REFUSALS[1],
    "root": REFUSALS[2],
    "ambiguous": REFUSALS[3],
}

#: EVERY PARAMETER NAME ANY PUBLIC CALLABLE IN THIS MODULE IS PERMITTED TO
#: HAVE. This is the signature half of the ruling, and it is enforced by
#: ``tests/test_feed_tally.py`` rather than by convention.
#:
#: A name like ``text``, ``body``, ``author_name``, ``headline``,
#: ``title`` or ``reason`` is absent from this set ON PURPOSE. Adding one
#: turns a test red at the moment the parameter is written, which is
#: before it has carried anything anywhere. That is the property the
#: ruling asked for: a leak needs a route IN before it needs a route out,
#: and this closes the route in.
_PERMITTED_PARAMETER_NAMES = frozenset({"href", "hrefs", "first", "second"})


def _entity_key(href: Optional[str]):
    """INTERNAL PARSER, shared by kind resolution and internal dedup keys.

    Returns ``(status, kind, key, saw)``:

    * ``status`` is ``"ok"``, ``"no_href"``, ``"absent"``, ``"root"`` or
      ``"ambiguous"``;
    * ``kind`` is a member of :data:`AUTHOR_KINDS`, only when ``ok``;
    * ``key`` is ``(kind, raw segment text)``, only when ``ok``;
    * ``saw`` is the list of KIND WORDS observed -- a closed-vocabulary
      report, never a substring of the href.

    **``key`` NEVER LEAVES THIS MODULE THROUGH A PUBLIC RETURN.** Every
    public function that touches it reduces sets of it to a COUNT first.
    It exists because distinctness cannot be computed without the actual
    text, and the whole trick of this family of modules is that the text
    is used INTERNALLY for set arithmetic and only its cardinality
    crosses a return.

    THE KEY CARRIES THE KIND, not just the slug. ``/company/<x>`` and
    ``/in/<x>`` are different entities that can share a segment spelling,
    and a key of the segment alone would silently merge them and
    under-report the distinct count.

    THE ORDER OF THE CHECKS IS PART OF THE CONTRACT:

    1. an empty href refuses before anything is parsed;
    2. the query and fragment are dropped via ``urlsplit(href).path``
       BEFORE any marker is looked for;
    3. ALL entity segments are collected, and more than one refuses as
       ambiguous -- see the module docstring. This runs before the
       root check, so an ambiguous path is reported as ambiguous even
       when one of its segments happens to be bare.
    """
    if not href or not str(href).strip():
        return "no_href", None, None, []

    # THE QUERY AND FRAGMENT GO FIRST AND ARE NEVER LOOKED AT.
    path = urlsplit(str(href).strip()).path
    segments = [segment for segment in path.split("/") if segment]

    # AN EXACT SEGMENT MATCH, not a substring search over a shaped string.
    present = [segment for segment in _ENTITY_SEGMENTS if segment in segments]

    if len(present) > 1:
        return (
            "ambiguous",
            None,
            None,
            [_KIND_FOR_SEGMENT[segment] for segment in present],
        )

    if not present:
        return "absent", None, None, []

    marker_segment = present[0]
    kind = _KIND_FOR_SEGMENT[marker_segment]
    index = segments.index(marker_segment)
    if index + 1 >= len(segments):
        return "root", None, None, [kind]

    return "ok", kind, (kind, segments[index + 1]), [kind]


def author_kind(href: Optional[str]) -> dict[str, Any]:
    """What KIND of entity authored this feed row? Never WHICH one.

    Returns one of two shapes and never raises, because one unusable row
    on a feed of many is not an error:

    ``{"identified": True, "kind": <one of AUTHOR_KINDS>, "href_shape": PUBLISHED_HREF}``
    ``{"identified": False, "refused": <one of REFUSALS>, "saw": [...], "why": "..."}``

    **NEVER RETURNS THE SLUG, THE PATH, OR ANY SUBSTRING OF ``href``.**
    The ``identified: True`` shape carries the kind word, the fact, and
    the one published literal -- nothing that varies with which entity it
    was.

    ``saw`` REPORTS WHAT WAS SEEN, drawn from the closed kind vocabulary,
    never a substring of the actual href: a refusal that names only what
    it did NOT match is half a measurement, and this repository has lost
    three rounds to that shape.

    MEASURED: nothing. See the module docstring's final section.
    """
    status, kind, _key, saw = _entity_key(href)

    if status == "ok":
        return {"identified": True, "kind": kind, "href_shape": PUBLISHED_HREF}

    if status == "no_href":
        return {
            "identified": False,
            "refused": _REFUSAL_FOR_STATUS["no_href"],
            "saw": [],
            "why": (
                "a row with no destination cannot be shown to identify an "
                "author of any kind, and this gate refuses what it cannot "
                "establish."
            ),
        }

    if status == "ambiguous":
        return {
            "identified": False,
            "refused": _REFUSAL_FOR_STATUS["ambiguous"],
            "saw": saw,
            "why": (
                "this path carries more than one entity segment, so which "
                "one authored the row is decided by nothing but the order "
                "the checks happen to run in. An ordering accident is not "
                "a classification, so it is refused rather than attributed."
            ),
        }

    if status == "root":
        return {
            "identified": False,
            "refused": _REFUSAL_FOR_STATUS["root"],
            "saw": saw,
            "why": (
                "the entity segment carries nothing after it, so this "
                "points at a section root or navigation furniture rather "
                "than at a specific author."
            ),
        }

    # status == "absent". The kind vocabulary is closed and none of it was
    # present, so an empty "saw" is the honest answer here rather than a
    # missed one -- unlike the ambiguous branch, there is genuinely
    # nothing in the vocabulary to report having seen.
    return {
        "identified": False,
        "refused": _REFUSAL_FOR_STATUS["absent"],
        "saw": [],
        "why": (
            "no entity segment in the path. An author is identified by "
            "where the row points, never by what the row says."
        ),
    }


def _distinct_keys(hrefs: Iterable[Optional[str]]) -> set:
    """INTERNAL ONLY: the set of ``(kind, segment)`` keys found present.

    Used solely for local set arithmetic. NEVER returned to a caller --
    every public function that uses it reduces the result to a COUNT
    before anything crosses a ``return``.
    """
    keys: set = set()
    for href in hrefs:
        status, _kind, key, _saw = _entity_key(href)
        if status == "ok":
            keys.add(key)
    return keys


def feed_tally(hrefs: Iterable[Optional[str]]) -> dict[str, Any]:
    """Count a list of feed author hrefs. COUNTS AND KINDS ONLY.

    Returns::

        {
            "rows":             hrefs handed in,
            "identified":       how many resolved to an author kind,
            "distinct_authors": how many DISTINCT authors those carried,
            "by_kind":          {kind: count}, kinds from AUTHOR_KINDS only,
            "refused":          {reason: count}, reasons from REFUSALS only,
            "href_shape":       the one literal this module publishes,
        }

    ``rows`` and ``identified`` are reported separately for the reason
    ``groups.membership_tally`` gives: a caller handed forty rows and
    shown twelve authors can see that twenty-eight were refused, where a
    bare ``identified: 12`` reads identically whether twenty-eight were
    refused or twelve were all that was offered.

    ``distinct_authors`` IS NOT ``identified``. The feed is the surface
    where those two diverge hardest -- the same author appearing four
    times in one scroll is the ordinary case, not the exotic one -- and
    the distinct count is the number the precondition actually wants. It
    is computed here rather than left to a caller, because a caller
    computing it would need the identifiers this module refuses to hand
    over.

    ``by_kind`` OMITS kinds with a zero count rather than listing every
    member of :data:`AUTHOR_KINDS` at zero. The difference matters: this
    function reports what it SAW, and a caller wanting the full frame can
    read :data:`AUTHOR_KINDS`, which is public for that purpose.
    """
    keys: list = []
    by_kind: dict[str, int] = {}
    refused: dict[str, int] = {}
    rows = 0
    for href in hrefs:
        rows += 1
        status, kind, key, _saw = _entity_key(href)
        if status == "ok":
            keys.append(key)
            by_kind[kind] = by_kind.get(kind, 0) + 1
            continue
        reason = _REFUSAL_FOR_STATUS[status]
        refused[reason] = refused.get(reason, 0) + 1

    return {
        "rows": rows,
        "identified": len(keys),
        "distinct_authors": len(set(keys)),
        "by_kind": by_kind,
        "refused": refused,
        "href_shape": PUBLISHED_HREF,
    }


def authorship_concentration(hrefs: Iterable[Optional[str]]) -> dict[str, Any]:
    """Is this feed dominated by a few authors? AN INTEGER, NOT A NAME.

    Returns::

        {
            "identified":            rows that resolved to an author,
            "distinct_authors":      how many distinct authors those were,
            "largest_author_rows":   rows contributed by the single most
                                     frequent author,
            "concentrated":          whether one author carried more than
                                     half the identified rows,
        }

    **THIS IS THE FUNCTION THAT PAYS FOR THE MODULE'S COST.** The
    docstring's opening section admits that a caller cannot ask WHICH
    author dominated the feed. This answers the question that was
    actually worth asking -- whether one did -- and answers it as an
    integer, so the name was never needed.

    ``largest_author_rows`` is a count over an internal key set; the key
    itself never crosses this return. With no identified rows it is 0 and
    ``concentrated`` is False: an empty feed is not a concentrated one,
    and a caller must not read a vacuous True as a finding.

    ``concentrated`` uses a STRICT majority (``> identified / 2``) so that
    a two-author feed split evenly is not reported as concentrated. The
    threshold is stated here because a boolean derived from a threshold
    is only as honest as its published rule.
    """
    tallies: dict = {}
    for href in hrefs:
        status, _kind, key, _saw = _entity_key(href)
        if status == "ok":
            tallies[key] = tallies.get(key, 0) + 1

    identified = sum(tallies.values())
    largest = max(tallies.values()) if tallies else 0
    return {
        "identified": identified,
        "distinct_authors": len(tallies),
        "largest_author_rows": largest,
        "concentrated": bool(identified) and largest * 2 > identified,
    }


def overlap(
    first: Iterable[Optional[str]], second: Iterable[Optional[str]]
) -> dict[str, Any]:
    """Do the same authors appear in two href sets? COUNTS ONLY.

    ``first`` and ``second`` are href lists a caller already holds -- two
    scrolls of the feed, or the feed against some other surface's author
    links. Returns::

        {
            "first_distinct":   distinct authors in the first set,
            "second_distinct":  distinct authors in the second set,
            "common":           how many appear in BOTH,
            "disjoint":         whether the two sets share nobody,
        }

    This is the direct analogue of ``groups.disjoint`` and
    ``recommendations.relation_split``, and it is answerable ONLY because
    distinctness is computed INTERNALLY from the actual segment text for
    the sole purpose of set membership. **That text never leaves this
    function: two sets are intersected and only their SIZES cross the
    return.**

    ``disjoint`` is True for two EMPTY sets, which is arithmetically
    correct and easy to misread. A caller distinguishing "shares nobody"
    from "had nobody to share" must read the two distinct counts, which
    is why both are returned rather than the intersection alone -- the
    same three-state discipline ``notify_cost.measurability`` keeps for a
    badge at zero.
    """
    first_keys = _distinct_keys(first)
    second_keys = _distinct_keys(second)
    common = first_keys & second_keys
    return {
        "first_distinct": len(first_keys),
        "second_distinct": len(second_keys),
        "common": len(common),
        "disjoint": not common,
    }
