"""A membership reader that publishes COUNTS AND IDENTIFIERS AND NO NAMES.

THIS IS A RULING BEING IMPLEMENTED, NOT A REFACTOR, and the ruling is written
down in ``shape.membership_row``'s own docstring, by the wave that measured why
that function cannot close its own hole:

    A group NAMED AFTER A PERSON ships its name verbatim. A plain human name
    carries no urn, no ``/in/`` path, no possessive and no six-digit run, so
    the identity check cannot see one. The count rule is the only thing that
    separates them and it is unavailable on a per-record path by
    construction. Applying it unconditionally destroys the payload: every
    plausible group name is a run of two or more capitalised words, so the
    singleton rule blanks the answer and the leak together.

    WHAT WOULD ACTUALLY CLOSE IT IS A RULING, NOT A REFACTOR: a membership
    reader that publishes COUNTS AND IDENTIFIERS AND NO NAMES.

**THE NAME IS NOT A PARAMETER OF ANY FUNCTION IN THIS MODULE.** That is the
whole design and it is deliberately structural rather than a filter: a reader
that is never handed a name cannot leak one, whatever LinkedIn calls a group
tomorrow and whatever a future edit does to a substitution table. A filter has
to keep up; an absent parameter does not. ``test_membership_tally.py`` asserts
the signature, because a property asserted only in prose is the defect this
repository has named more than once.

## WHAT THE PRECONDITION ACTUALLY NEEDED, AND IT IS ALL COUNTS

``/groups/`` was admitted to answer one question: does he belong to any group?
The answer that came back is four counts -- five under the membership heading,
five under the suggestion heading, zero identifiers in common, five per-row
management controls -- and **not one of them needs a name.** A surface opened
for a counting question is answered by a counting reader.

## THE IDENTIFIER IS THE NUMERIC PATH SEGMENT AND NOTHING ELSE

Two refusals do the work, and both are structural rather than tuned:

1. **THE QUERY AND FRAGMENT ARE DISCARDED BEFORE ANYTHING IS READ.** Not
   shaped, not substituted -- dropped. ``membership_row`` records the measured
   escape this closes: ``/groups/12345678/?invitedBy=<a token>`` survives the
   census substitutions with the token intact, because ``/in/`` is the only
   member shape they know. A part that is never read cannot carry anything.
2. **A NON-NUMERIC SEGMENT IS REFUSED, BECAUSE A SLUG IS A NAME.** This is the
   same disease one level down: a group named after a person gets a slug made
   of that person's name, and publishing it as an "identifier" would ship the
   name this module exists to keep out, wearing an identifier's clothes.

**THE NUMERIC RULE REFUSES NOTHING REAL, and that is measured rather than
hoped.** Over the eleven ``/groups/`` hrefs in a live capture of his own Groups
page: ten entity segments, ALL pure digits at lengths 5, 6, 7 and 8, ZERO
non-numeric, ZERO carrying a query string, and one root link with no segment at
all -- which is also the reconciliation for the census's ten against this
walk's eleven.

## WHY AN IDENTIFIER MAY BE PUBLISHED WHEN A NAME MAY NOT

They are different things and the boundary comment in ``readonly.py`` already
draws the line: *which groups he belongs to is HIS OWN DATA, the same class as
his own profile.* A group id names a GROUP. A group's NAME can be a person's
name -- that is the entire finding this module answers -- and no numeric group
id can be.

**AND A DIGEST WOULD HAVE BEEN WORSE THAN EITHER.** Hashing the id was
considered and rejected: LinkedIn group ids run to eight digits, so a digest
over that domain is brute-forceable end to end. It would have looked like a
redaction and been a lookup table, which is the shape of thing this repository
calls worse than the leak -- a redaction that buys the reader's trust.

## WHAT THIS MODULE IS NOT

* It is **not** a replacement for ``shape.membership_row``. That function
  publishes a name under a stated, tested limit and its tests assert the hole
  so that closing it turns a test red. This module is the ruling's answer, and
  the two are allowed to coexist: a caller that needs a name takes the
  documented risk knowingly, and a caller that needs the precondition answered
  takes this one and cannot take the risk at all.
* It **does not open a page.** It takes hrefs somebody else read.
* It makes no claim about which section a row sat under. Section membership is
  the caller's fact; this module counts what it is handed.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import urlsplit

from linkedin_server import shape

#: THE MARKERS, IMPORTED RATHER THAN RE-STATED, from the one place they are
#: derived. ``shape._MEMBERSHIP_FOREIGN_MARKERS`` is every census entity marker
#: EXCEPT the group one, so a sixth entity kind added to
#: ``shape._CENSUS_ENTITY_HREFS`` tomorrow becomes a refusal here automatically
#: rather than a hole -- the same property that tuple was built to give
#: ``membership_row``, inherited instead of copied.
#:
#: ``test_membership_tally.py`` asserts these ARE shape's, so a copy that
#: drifted would be a test failure rather than a silent divergence.
FOREIGN_MARKERS = shape._MEMBERSHIP_FOREIGN_MARKERS
GROUP_MARKER = shape._MEMBERSHIP_HREF_MARKER

#: THE SAME MARKERS AS PATH SEGMENTS, and this module matches on THESE rather
#: than running ``census_substitute`` over the path.
#:
#: **THAT CHANGE WAS FORCED BY A GUARD AND IT IMPROVED THE DESIGN, which is
#: the guard working rather than the guard being satisfied.** The first version
#: shaped the path and looked for markers in the result. That made this module
#: a new consumer of ``census_substitute``, and
#: ``test_the_consumers_of_this_predicate_are_the_ones_that_were_considered``
#: went red -- a consent guard that exists so a new caller "shows up in a diff
#: instead of in an INCIDENT". The available remedy was to declare the caller.
#: The better one was to look at why it was there at all:
#:
#: * the substitution buys nothing here. This function already splits the path
#:   into segments to find the identifier, so an EXACT segment match is
#:   available and is strictly tighter than a substring search over a shaped
#:   string;
#: * and the coupling was backwards. ``census_substitute`` blanks runs of six
#:   or more digits, which is exactly the shape of the identifier this module
#:   publishes. Depending on it to decide what a group href IS, while stepping
#:   around it to read the id out, is a relationship that would eventually
#:   break in the quiet direction.
#:
#: Derived from the same tuple, so the automatic-refusal property survives:
#: a sixth entity kind added to ``shape._CENSUS_ENTITY_HREFS`` tomorrow lands
#: in this set with no edit here.
FOREIGN_SEGMENTS = tuple(
    marker.split("/")[1] for marker in FOREIGN_MARKERS
)

#: The one href string this module ever publishes, and it is a LITERAL.
#: Same value and same reason as ``shape._MEMBERSHIP_PUBLISHED_HREF``: an
#: arbitrary string that never crosses can never carry an identifier.
PUBLISHED_HREF = shape._MEMBERSHIP_PUBLISHED_HREF

#: The path segment that names a group, and the whole of what may be published
#: as an identifier.
#:
#: THE TEN ASCII DIGITS ONLY. Not a "safe charset" -- a charset wide enough to
#: hold a slug is wide enough to hold a person's name, and a group named after
#: a person is the precise input this module exists for. Bounded above because
#: an unbounded repetition on attacker-shaped input is a cost nobody chose;
#: twenty digits is more than twice the longest id measured on his own page.
_MAX_IDENTIFIER_DIGITS = 20

#: THE TEN ASCII DIGITS, WRITTEN OUT, BECAUSE ``str.isdigit()`` IS NOT THIS.
#:
#: Found on a fresh-eyes re-read before the freeze, not by a test.
#: ``"12345".isdigit()`` is True and so is the same run written in
#: Arabic-Indic digits, in Extended Arabic-Indic digits, or as superscripts --
#: measured, three scripts, all True. ``int()`` cannot even parse the
#: superscript form.
#:
#: **THAT MATTERS BECAUSE OF WHAT THIS MODULE CLAIMS, not because LinkedIn is
#: likely to serve one.** The whole design rests on one sentence: *a charset
#: wide enough to hold a slug is wide enough to hold a name.* ``isdigit()``
#: admits a charset materially wider than the ten characters the docstring
#: promises, so the promise was an overclaim -- small in practice and exactly
#: the shape of thing this repository has been caught by twice, where a check
#: is correct for the inputs it was imagined against.
#:
#: A membership test against a literal set cannot widen behind anybody's back.
_ASCII_DIGITS = frozenset("0123456789")

#: The path segment that introduces a group. Taken from the marker rather than
#: written again, so the two cannot disagree.
_PATH_KEY = GROUP_MARKER.split("/")[1]


def group_identifier(href: Optional[str]) -> dict[str, Any]:
    """The numeric identifier in a group href, or a refusal naming what it saw.

    Returns one of two shapes and never raises, because one unusable row on a
    page of thirty is not an error:

    ``{"identified": True, "identifier": <digits>, "href_shape": <literal>}``
    ``{"identified": False, "refused": <reason>, "saw": [<markers>]}``

    **A REFUSAL REPORTS WHAT IT DID SEE.** Three rounds were lost in this
    project to refusals that reported only what they failed to match, and the
    rule that came out of it is written into ``membership_row`` beside this
    one: a refusal that names only the absence is half a measurement.

    THE ORDER OF THE CHECKS IS PART OF THE CONTRACT. The query is dropped
    FIRST, before any marker is looked for, so no branch below can ever be
    reading a string that still has one attached.

    AND THE FOREIGN CHECK RUNS BEFORE THE GROUP CHECK, so a path carrying both
    -- ``/groups/<id>/in/<member>/`` -- is refused as foreign rather than
    accepted as a group. The conservative direction is the one where a row
    pointing at a person cannot be counted, and a row that is genuinely a group
    is cheap to lose.
    """
    if not href or not str(href).strip():
        return {
            "identified": False,
            "refused": "no_href",
            "saw": [],
            "why": (
                "a row with no destination cannot be shown to be about a "
                "group, and this gate refuses what it cannot establish."
            ),
        }

    # THE QUERY AND FRAGMENT GO FIRST AND ARE NOT LOOKED AT. urlsplit().path
    # returns the path alone; the token in ``?invitedBy=`` is dropped here and
    # no line below can read it.
    path = urlsplit(str(href).strip()).path

    segments = [segment for segment in path.split("/") if segment]

    # AN EXACT SEGMENT MATCH, not a substring search over a shaped string.
    # See FOREIGN_SEGMENTS for why the shaper was taken out of this path.
    foreign = [
        marker
        for marker, key in zip(FOREIGN_MARKERS, FOREIGN_SEGMENTS)
        if key in segments
    ]
    if foreign:
        return {
            "identified": False,
            "refused": "href_identifies_another_kind_of_entity",
            "saw": foreign,
            "why": (
                "this row points at something that is not a group. It is "
                "DROPPED rather than counted -- a row counted as a group "
                "because nothing refused it is worse than one refused."
            ),
        }

    if _PATH_KEY not in segments:
        return {
            "identified": False,
            "refused": "not_a_group_href",
            "saw": [
                marker
                for marker, key in zip(
                    shape._CENSUS_ENTITY_HREFS,
                    [m.split("/")[1] for m in shape._CENSUS_ENTITY_HREFS],
                )
                if key in segments
            ],
            "why": (
                "no group segment in the path. A membership row is identified "
                "by where it points, never by where it sits on the page."
            ),
        }

    index = segments.index(_PATH_KEY)
    if index + 1 >= len(segments):
        return {
            "identified": False,
            "refused": "group_root_carries_no_identifier",
            "saw": [GROUP_MARKER],
            "why": (
                "this is the Groups root itself, which the page links to from "
                "its own navigation. It is a link to the surface rather than "
                "to a group, and counting it would inflate every tally by "
                "exactly one."
            ),
        }

    segment = segments[index + 1]
    if (
        not segment
        or not set(segment) <= _ASCII_DIGITS
        or len(segment) > _MAX_IDENTIFIER_DIGITS
    ):
        return {
            "identified": False,
            "refused": "identifier_is_not_numeric",
            "saw": [GROUP_MARKER],
            "why": (
                "a group segment that is not a bounded run of the TEN "
                "ASCII DIGITS is a SLUG, and a slug is a name -- a group "
                "named after a person gets that person's name in its slug. "
                "Publishing it as an identifier would ship the name this "
                "module exists to keep out, wearing an identifier's clothes. "
                "The ten are named explicitly because str.isdigit() is true "
                "of several other scripts' digits as well."
            ),
        }

    return {
        "identified": True,
        "identifier": segment,
        # THE LITERAL, never a shape of the input. See the module docstring.
        "href_shape": PUBLISHED_HREF,
    }


def membership_tally(hrefs: Iterable[Optional[str]]) -> dict[str, Any]:
    """Count a list of group hrefs. NO NAME IS A PARAMETER OF THIS FUNCTION.

    THE SIGNATURE IS THE SAFETY PROPERTY. Every other reader on this surface
    takes a name and decides whether to publish it; this one is never handed
    one, so no edit to a substitution table, no new LinkedIn label and no
    future group named after a person can put a name in its output. That is
    checked by a test on the signature itself rather than argued here.

    Returns::

        {
            "rows":        how many hrefs were handed in,
            "groups":      how many were identified as groups,
            "distinct":    how many DISTINCT identifiers those carried,
            "identifiers": the sorted distinct identifiers,
            "refused":     {reason: count},
            "href_shape":  the one href literal this module publishes,
        }

    ``rows`` and ``groups`` are both reported and the difference is the point:
    a caller handed ten anchors and shown five groups can see that five were
    refused, whereas a bare ``groups: 5`` reads identically whether five were
    refused or none were offered.

    ``distinct`` IS NOT ``groups``. LinkedIn writes the same group as a
    relative and an absolute href on one page, and a page that draws a group
    twice would otherwise be counted as two memberships. The precondition this
    surface was opened for is a DISTINCT count, so it is computed here rather
    than left to a caller to remember.
    """
    identifiers: list[str] = []
    refused: dict[str, int] = {}
    rows = 0
    for href in hrefs:
        rows += 1
        verdict = group_identifier(href)
        if verdict.get("identified"):
            identifiers.append(str(verdict["identifier"]))
            continue
        reason = str(verdict.get("refused") or "unknown")
        refused[reason] = refused.get(reason, 0) + 1

    return {
        "rows": rows,
        "groups": len(identifiers),
        "distinct": len(set(identifiers)),
        "identifiers": sorted(set(identifiers)),
        "refused": refused,
        "href_shape": PUBLISHED_HREF,
    }


def disjoint(first: Iterable[Optional[str]],
             second: Iterable[Optional[str]]) -> dict[str, Any]:
    """Do two lists of group hrefs share any group? COUNTS ONLY.

    THE DECIDING MEASUREMENT OF THE WHOLE PRECONDITION, and it is the reason
    identifiers are published at all rather than counts alone. Two sections
    listing the SAME groups are one set drawn twice; two sections listing
    DISJOINT groups are two sets, and if LinkedIn's own heading calls one of
    them suggestions then the other one is not.

    Returns counts and a boolean. **It returns no identifier**, because the
    question is about the relationship between two sets and an overlap of zero
    says everything an overlap of zero can say.
    """
    left = set(membership_tally(first)["identifiers"])
    right = set(membership_tally(second)["identifiers"])
    common = left & right
    return {
        "first_distinct": len(left),
        "second_distinct": len(right),
        "in_common": len(common),
        "disjoint": not common,
    }
