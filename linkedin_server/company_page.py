"""Shape an ORGANISATION Page. No slug, name or address crosses the boundary.

``COMPANY-PAGE-SURFACE`` is the largest BUILD in the census -- 18 published
rows, 16 of them filed -- and every one of them is filed behind the same
sentence: *no ``/company/`` pattern on the read allowlist.* This module is the
name-free shaper that the admission of that pattern ships WITH, in one commit,
on the condition ``search_results.py`` states about itself and this entry
inherits by argument rather than by family resemblance.

## WHY A SHAPER IS OWED HERE AT ALL, AND THE EVIDENCE IS THIS REPOSITORY'S OWN

The precedent that decides the shape of the argument was set on one day.
A ``/groups/<id>/`` admission was GRANTED because a group id is NUMERIC, so the
address names nobody. A ``/search/results/`` admission was REFUSED bare because
the page is a list of other people, and held on the condition that its shaper
land in the same commit. **A company address is BOTH of those, depending on
which spelling LinkedIn hands you**, and that is measured here rather than
supposed:

``scripts/_probe_company_path_segments.py`` walks every HTML document this
repository has committed -- 22 documents, 86 ``/company/`` hits, **28 distinct
path segments: 21 NUMERIC and 7 SLUGS.** The numeric spellings are what the
Manage-Pages list and the notification rail address a Page by. The slugs are
what a JOB POSTING hands you. And one of the seven, in the corpus, is a
SURNAME with a word after it.

So the sentence ``groups.py`` refuses a non-numeric segment with -- *a slug is
a name: a group named after a person gets that person's name in its slug* --
reaches this surface unchanged, and reaches it with a live example rather than
a worry. Sole traders, eponymous firms and personal brands are not an edge
case on LinkedIn; they are a category of Page.

**THEREFORE THE NUMERIC SPELLING IS THE GROUPS CASE AND THE SLUG SPELLING IS
THE SEARCH-RESULTS CASE, and the admission is granted on the stricter of the
two.** This module is what makes that grant payable.

## WHAT THE ADMISSION HAD TO INCLUDE THE SLUG FORM, WHICH IS NOT OBVIOUS

The tempting narrow entry is ``/company/[0-9]{1,20}/?$`` alone -- the groups
pattern with a different word, admitting the spelling that names nobody and
nothing else. Measured against the family corpus it newly admits TWO addresses
against the shipped entry's FOUR, so it looks strictly safer.

**It is not, and the reason is the landing page.** LinkedIn canonicalises an
organisation address: the numeric form redirects to the slug form. A boundary
that admits only the numeric form therefore admits the REQUEST and refuses the
LANDING -- and ``readonly.assert_read_url``'s refusal interpolates the url it
refused. That is not a hypothetical failure mode in this repository. It is the
defect ``tests/test_navigation_is_never_derived.py`` was built for, where
``/in/me/`` resolved to a decorated member path and *the operator's vanity slug
went into a traceback*.

So a numeric-only admission buys a narrower pattern and pays for it with a
third party's slug in an exception, on the ordinary path, every time. The
entry admits both spellings and this module carries the cost of the wider one.

**WHAT IS STILL A HYPOTHESIS AND IS NOT DRESSED AS ANYTHING ELSE:** that the
numeric form redirects to the slug form. Nobody in this repository has opened
a company Page. What IS measured is that BOTH spellings are addresses LinkedIn
itself draws -- ``notifications.html`` links a Page by ``/company/5417062``
and every tracked posting links one by ``/company/<slug>/`` -- so both are
real, and the admission covers what the product emits either way.

## THE MECHANISM IS THE SHIPPED ONE: VOCABULARY IN, INDEX OUT

``groups.py`` -> ``menus.py`` -> ``anchors.py`` -> ``search_results.py``, each
sharper than the last, and all four run one engine: the vocabulary is defined
HERE, the document answers with an INTEGER INDEX into a table defined HERE, and
the mapping back to a word happens in Python. **Nothing a document holds is
ever a return value.**

This module keeps that engine and adds nothing to it. What it adds is a second
hazard class the earlier four did not have to name.

## THE TWO HAZARD CLASSES UNDER THIS ONE ROOT, BOTH NAMED BECAUSE A FAMILY
## PATTERN OPENS THEM AND NOTHING ELSE REFUSES THEM

Measured with the shipped predicate over 107 concrete addresses
(``scripts/_probe_company_family_blast.py``): the family pattern
``^https://www\\.linkedin\\.com/company/.*$`` newly admits **35 addresses, and
every one of them is defended by nothing but the absence of a rule.** Two
classes in that 35 are worth naming, because neither is a tab:

``people_tab``
    ``/company/<x>/people/`` is a MEMBER ROSTER. It is the same objection that
    put ``N 165`` -- a group's member roster -- out of scope by name, and the
    same one that kept ``/school/<x>/people/`` shut on 2026-09-05. It is first
    in :data:`TAB_KINDS` for the reason ``person_result`` is first in
    ``search_results.RESULT_KINDS``: it is the class anything misclassified
    INTO or OUT OF is the defect the rules exist to prevent.

``admin_surface`` and ``page_creation``
    ``/company/<x>/admin/``, ``/company/<x>/admin/dashboard/`` and
    ``/company/setup/new/`` are the WRITE half of this root -- Page
    administration, and the flow that CREATES an organisation Page. **None of
    the three carries a forbidden substring.** ``/create`` is on the denylist
    and LinkedIn does not spell this one with it. So they are refused today by
    the anchor on the allowlist entry and by nothing else, which is exactly
    the standing boundary trap: *a tidy family pattern admits the expensive
    irreversible act as a side effect, with nothing in the diff naming it.*

They are classified here rather than merely refused there, so a caller that
ever meets one gets a COUNT of it instead of silence.

## NO NAME, SLUG, ADDRESS OR ID IS A RETURN VALUE OF ANYTHING HERE

Asserted on ``inspect.signature`` and on the outputs in
``tests/test_company_page.py``, the way ``groups.py`` and ``search_results.py``
assert it.

**TWO FUNCTIONS TAKE AN IDENTIFIER AND THAT IS THE DELIBERATE EXCEPTION**, for
the reason ``jobfilter.py`` already ruled on this exact surface: a BUILDER has
to be handed the thing it builds from. :func:`company_identifier` and
:func:`company_page_url` are that pair, they take a candidate, and **neither
one ever echoes it** -- a refusal from either reports the SHAPE, through
``jobfilter.describe_shape``, which is the shipped instrument for exactly this
and is imported rather than rewritten.

**AND THE BUILDER BUILDS THE NUMERIC FORM ONLY.** The allowlist admits the
slug spelling because LinkedIn emits it; this package will not ASSEMBLE one.
A url this repository authored out of a numeric id names nobody, and a url
assembled from a slug a page handed us is a third party's name in a navigation
-- which is the sink ``test_navigation_is_never_derived.py`` guards. The
asymmetry is the whole point: **admit what the product serves, build only what
names nobody.**

## WHAT THIS MODULE DOES NOT DO

* **It opens nothing.** There is no page function here. The address is on the
  allowlist and no tool in this package navigates to it, so this buys a
  PRECONDITION and a vocabulary, not a page read -- the same honest accounting
  the ``/groups/<id>/`` entry wrote for itself.
* **It fires nothing.** No function here presses, submits or takes a confirm
  token. ``J 86`` ("I'm interested") and ``N 47`` (follow from the Page) are
  the two WRITES in this blocker and neither is touched.
* **It has never seen a company Page.** Every number attached to it comes from
  committed fixtures and from the shipped predicate.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional
from urllib.parse import urlsplit

from linkedin_server import jobfilter

#: The path segment that introduces an organisation Page.
ORGANISATION_MARKER = "/company/"

#: The path segment that introduces a MEMBER, checked before the company
#: segment for the reason ``groups.group_identifier`` checks its foreign
#: marker first: an address carrying both is refused as foreign rather than
#: accepted as an organisation. The conservative direction is the one where a
#: route pointing at a person cannot be counted as a company.
MEMBER_MARKER = "/in/"

#: THE LITERAL PUBLISHED IN PLACE OF AN HREF. Never a shape of the input, for
#: the reason ``groups.PUBLISHED_HREF`` exists: a "shape" derived from the
#: value is a channel, and a constant is not.
PUBLISHED_HREF = "/company/<company>/"

#: The ten ASCII digits, written out, because ``str.isdigit()`` is not this.
#: ``groups.py`` found it on a fresh-eyes read and the sentence governs here
#: too: a charset wide enough to hold a slug is wide enough to hold a name.
#: ``"1234".isdigit()`` is True and so is the Arabic-Indic, Extended
#: Arabic-Indic, Devanagari and fullwidth spelling of the same run.
_ASCII_DIGITS = frozenset("0123456789")

#: THE BOUND, AND IT IS ``groups.py``'s NUMBER RATHER THAN A NEW ONE. An
#: unbounded repetition on attacker-shaped input is a cost nobody chose, and
#: an identifier cap that disagrees with the allowlist pattern is a boundary
#: that opens an address its own shaper then refuses -- the divergence the
#: groups coupling test caught on its first run.
MAX_IDENTIFIER_DIGITS = 20

#: THE BOUND ON A SLUG, taken from the ``/school/`` entry admitted 2026-09-05
#: so the two organisation surfaces do not disagree about how long an
#: organisation's name may be.
MAX_SLUG_CHARS = 100

#: The characters a slug may hold. **A DOT IS DELIBERATELY OUTSIDE IT**, the
#: same refusal the ``/school/`` entry states for itself: a dotted slug is a
#: real if uncommon spelling, and admitting it also admits a segment of
#: ``..``, which the browser normalises AWAY -- turning an admitted
#: organisation address into some other page entirely.
_SLUG_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "%-_"
)

#: THE CLOSED OUTPUT ALPHABET. Order is the contract: a reading is a POSITION
#: in this tuple, so reordering silently renames every reading ever taken.
#: ``tests/test_company_page.py`` pins it.
#:
#: ``people_tab`` IS THE HAZARD CLASS and is first on purpose. See the module
#: docstring: it is a member roster, it is the one surface under this root the
#: member-profile cause reaches, and it is out of scope by the same ruling
#: that put a group's roster out of scope by name.
TAB_KINDS: tuple[str, ...] = (
    "people_tab",
    "home_tab",
    "about_tab",
    "posts_tab",
    "jobs_tab",
    "life_tab",
    "products_tab",
    "services_tab",
    "insights_tab",
    "events_tab",
    "videos_tab",
    "admin_surface",
    "page_creation",
    "traversal_refused",
    "unclassified",
    "off_company",
    "no_href",
)

#: ``(kind token, segment 2)``. Segment 0 is compared to ``company`` and
#: segment 2 to this table, BY EQUALITY -- closed segments, which is the
#: amended condition ``search_results.py`` records: anchoring was MEASURED to
#: admit exactly as much as a bare wildcard, and equality was what actually
#: closed the route.
TAB_TABLE: tuple[tuple[str, str], ...] = (
    ("about_tab", "about"),
    ("people_tab", "people"),
    ("posts_tab", "posts"),
    ("jobs_tab", "jobs"),
    ("life_tab", "life"),
    ("products_tab", "products"),
    ("services_tab", "services"),
    ("insights_tab", "insights"),
    ("events_tab", "events"),
    ("videos_tab", "videos"),
)

#: The ADMIN sub-paths, kept out of :data:`TAB_TABLE` because they are not
#: tabs -- they are the write half of this root, and a reader that filed them
#: beside ``life`` would be describing a dashboard as a marketing page.
ADMIN_SEGMENTS: frozenset[str] = frozenset({"admin", "admin-v2"})

#: The segment LinkedIn spells its Page-CREATION flow with. It carries no
#: forbidden substring, so it is refused by the allowlist anchor and by
#: nothing else -- which is why it is named here instead of being left to the
#: ``unclassified`` bucket.
CREATION_SEGMENT = "setup"

#: A refusal, and a literal like everything else here.
UNCLASSIFIED = "unclassified"

#: The class a dot segment produces. A nonzero count here means the page
#: offered a route whose leading segments LIE about where it goes.
TRAVERSAL_REFUSED = "traversal_refused"

#: The segments that trigger it. Position-free on purpose: a traversal's harm
#: does not depend on where in the path it sits. **A TRAVERSAL IS REFUSED,
#: NEVER RESOLVED** -- resolving it would mean this module deciding what a
#: traversal means, which is the browser's job, and a shaper that guesses has
#: invented a second, disagreeing URL parser inside the guard.
DOT_SEGMENTS: frozenset[str] = frozenset({"..", "."})

#: The only host an organisation route may name.
#:
#: **A RELATIVE HREF CARRIES NO HOST AND MUST STILL CLASSIFY** -- LinkedIn
#: writes ``/company/<id>`` bare in the notification rail, measured in
#: ``tests/fixtures/notifications.html`` -- so an EMPTY netloc is accepted and
#: a NON-EMPTY one must match this exactly.
#:
#: THE FIRST VERSION OF THIS MODULE DEFINED THIS CONSTANT AND NEVER READ IT,
#: which is worse than not having it: ``https://evil.example/company/x/``
#: classified as ``home_tab`` and was counted as a LinkedIn organisation. A
#: count is a claim about what a page links to, and one that cannot tell
#: LinkedIn's own routes from a foreign host's is making a different claim
#: than the one its name makes.
_HOST = "www.linkedin.com"
_SCHEME_HOST = "https://" + _HOST


def _parts(href: Optional[str]):
    """Split an href, or ``None`` if it cannot be split or is off-host.

    **``urlsplit`` RAISES**, which is the reason this exists rather than being
    inlined three times. ``urlsplit("https://[")`` is a ``ValueError`` --
    Invalid IPv6 URL -- and MEASURED before this function existed,
    ``tally`` propagated it straight out of ``linkedin_job_detail``. One
    malformed href anywhere on a posting would have failed a read that had
    already succeeded, turning a route this module could not classify into a
    tool that returns nothing.

    A route this module cannot parse is a route it cannot judge, and the whole
    discipline here is that an unjudgeable route is COUNTED as unjudgeable
    rather than guessed at. So the refusal is total and silent to the caller:
    ``classify_route`` reports ``unclassified``, which is a visible integer.
    """
    if href is None:
        return None
    text = str(href).strip()
    if not text:
        return None
    try:
        parts = urlsplit(text)
    except ValueError:
        return None
    if parts.netloc and parts.netloc != _HOST:
        return None
    return parts

#: The one address form this package will ASSEMBLE. The slug form is admitted
#: by the boundary and is deliberately not buildable here -- see the module
#: docstring's asymmetry.
_URL_TEMPLATE = _SCHEME_HOST + "/company/{identifier}/"


def company_identifier(candidate: Optional[str]) -> dict[str, Any]:
    """A numeric organisation id, or a refusal that names what it SAW.

    Returns one of two shapes and never raises, because one unusable value in
    a batch of thirty is not an error::

        {"identified": True,  "identifier": <digits>, "href_shape": <literal>}
        {"identified": False, "refused": <reason>, "saw": <shape>, "why": ...}

    **THE REFUSAL REPORTS A SHAPE AND NEVER THE VALUE**, and this is the one
    place in this repository where the rule "a refusal names what it saw"
    yields to the identity rule. ``jobfilter.py`` ruled it on this exact
    surface and the reasoning is imported with the function: the overwhelmingly
    likely wrong value here is a company SLUG, because that is precisely what a
    posting hands you -- so the rule-following refusal ``got {candidate!r}``
    publishes a third party's name verbatim on the single most probable
    mistake. ``jobfilter.describe_shape`` is the shipped answer and is called
    rather than re-written.

    ACCEPTS THE TEN ASCII DIGITS ONLY, bounded at
    :data:`MAX_IDENTIFIER_DIGITS`. Not ``str.isdigit()``, which is true of
    several other scripts' digits; not ``\\d``, which matches any Unicode
    decimal digit and which -- measured on this surface -- admits SIX
    addresses where the closed class admits TWO.

    **THE CHARACTER CHECK RUNS BEFORE THE LENGTH CHECK, AND THE FIRST VERSION
    OF THIS FUNCTION HAD IT THE OTHER WAY.** Its own test caught it: a real
    slug is routinely longer than twenty characters, so a length-first order
    answered the commonest wrong input with ``identifier_too_long`` -- true,
    and the WRONG DIAGNOSIS. What a caller needs to be told is *that is a
    name, not an id*, because that is the mistake and the refusal is the only
    place it gets said. ``identifier_too_long`` is what you say about an
    over-long DIGIT RUN, which is a different and much rarer thing.
    """
    text = str(candidate or "").strip()
    if not text:
        return {
            "identified": False,
            "refused": "no_identifier",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "an organisation cannot be addressed by an empty value, and "
                "this gate refuses what it cannot establish."
            ),
        }
    if not set(text) <= _ASCII_DIGITS:
        return {
            "identified": False,
            "refused": "identifier_is_not_numeric",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "an organisation segment that is not a bounded run of the TEN "
                "ASCII DIGITS is a SLUG, and a slug is a name -- a sole "
                "trader, an eponymous firm or a personal brand gets a "
                "person's name in its slug, and this repository's own corpus "
                "carries one. Publishing it as an identifier would ship the "
                "name this module exists to keep out, wearing an "
                "identifier's clothes. The ten are named explicitly because "
                "str.isdigit() is true of several other scripts' digits."
            ),
        }
    if len(text) > MAX_IDENTIFIER_DIGITS:
        return {
            "identified": False,
            "refused": "identifier_too_long",
            "saw": jobfilter.describe_shape(text),
            "why": (
                "a digit run longer than "
                f"{MAX_IDENTIFIER_DIGITS} characters is not a LinkedIn "
                "organisation id, and an unbounded repetition on "
                "caller-shaped input is a cost nobody chose."
            ),
        }
    return {
        "identified": True,
        "identifier": text,
        # THE LITERAL, never a shape of the input.
        "href_shape": PUBLISHED_HREF,
    }


def company_page_url(candidate: Optional[str]) -> dict[str, Any]:
    """The one organisation address this package will assemble, or a refusal.

    **NUMERIC ONLY, AND THAT IS THE ASYMMETRY THE MODULE DOCSTRING ARGUES
    FOR.** The allowlist admits the slug spelling because LinkedIn emits it
    and a landing page that the boundary refuses puts a third party's slug in
    a traceback. It does not follow that this package should ASSEMBLE one.

    Returns::

        {"built": True,  "url": <url>, "identifier": <digits>}
        {"built": False, "refused": <reason>, "saw": <shape>, "why": ...}

    The url is a template this repository authored, filled from a value this
    function has already proven is ten-ASCII-digit only, so nothing that
    reaches ``goto`` through here can carry a name. It is NOT checked against
    the allowlist here on purpose: ``readonly.assert_read_url`` is the door
    and a second copy of the decision inside the builder is the two-guards-
    that-drift failure this repository has paid for twice.
    """
    verdict = company_identifier(candidate)
    if not verdict.get("identified"):
        out = dict(verdict)
        out.pop("identified", None)
        out["built"] = False
        return out
    identifier = str(verdict["identifier"])
    return {
        "built": True,
        "url": _URL_TEMPLATE.format(identifier=identifier),
        "identifier": identifier,
    }


def classify_route(href: Optional[str]) -> str:
    """Which organisation surface an href points at. A TOKEN, never content.

    The order of the checks is part of the contract:

    1. **The query and fragment go first and are never looked at.** A query on
       this root is where a filter naming a person would arrive, and the rule
       ``groups.py`` states governs here: a part never read cannot carry
       anything.
    2. **A dot segment ANYWHERE refuses the route.** Measured on the family
       corpus: ``/company/<x>/../../mypreferences/d/close-account`` normalises
       onto an ACCOUNT-ENDING address and ``/company/<x>/../../in/<member>/``
       onto a member profile, and NO FORBIDDEN SUBSTRING NAMES EITHER. A
       classifier that read only the leading segments would report both as an
       organisation.
    3. **A member marker refuses before the company marker is looked for**, so
       a path carrying both is ``off_company`` rather than a company tab.
    4. Only then are segment 0 and segment 2 compared, BY EQUALITY.

    Matching is CASE SENSITIVE and the miss lands on the safe side:
    ``/COMPANY/<x>/`` is ``off_company`` -- not recognised as an organisation
    at all -- rather than admitted as one. A case-insensitive comparison is
    the dangerous repair, because it widens what matches a table whose whole
    job is to be narrow.

    ONE ORDERING CONSEQUENCE, RECORDED SO IT IS NOT DISCOVERED LATER. The
    ``setup`` check sits BEFORE the two-segment check, so an organisation
    whose slug is literally ``setup`` classifies as ``page_creation`` rather
    than as a home tab. That is the conservative direction -- a route named
    as the creation flow is COUNTED and never mistaken for a Page -- and the
    alternative ordering has the dangerous miss: LinkedIn's Page-creation
    flow read as somebody's organisation Page.
    """
    if href is None or not str(href).strip():
        return "no_href"

    parts = _parts(href)
    if parts is None:
        # Unparseable, or a host this module has no business classifying.
        # ``off_company`` would be a CLAIM about where it points; this one
        # says only that it could not be judged.
        return UNCLASSIFIED
    segments = [segment for segment in parts.path.split("/") if segment]

    if any(segment in DOT_SEGMENTS for segment in segments):
        return TRAVERSAL_REFUSED
    if MEMBER_MARKER.strip("/") in segments:
        return "off_company"
    if not segments or segments[0] != ORGANISATION_MARKER.strip("/"):
        return "off_company"
    if len(segments) == 1:
        # ``/company/`` alone -- the product root, which is not a Page.
        return UNCLASSIFIED
    if segments[1] == CREATION_SEGMENT:
        return "page_creation"
    if len(segments) == 2:
        return "home_tab"
    if segments[2] in ADMIN_SEGMENTS:
        return "admin_surface"
    for token, segment in TAB_TABLE:
        if segments[2] == segment:
            return token
    return UNCLASSIFIED


def identifier_kind(href: Optional[str]) -> str:
    """``numeric``, ``slug`` or ``none`` for an organisation href's segment 1.

    **THE SPELLING IS PUBLISHABLE AND THE VALUE IS NOT**, which is the whole
    reason this is a separate function from :func:`classify_route`. A caller
    needs to know whether the address it met names nobody (the groups case) or
    can name somebody (the search-results case). It does not need the string,
    and this function is incapable of returning it.
    """
    parts = _parts(href)
    if parts is None:
        return "none"
    segments = [segment for segment in parts.path.split("/") if segment]
    if any(segment in DOT_SEGMENTS for segment in segments):
        return "none"
    if len(segments) < 2 or segments[0] != ORGANISATION_MARKER.strip("/"):
        return "none"
    segment = segments[1]
    if segment and set(segment) <= _ASCII_DIGITS:
        return "numeric"
    return "slug"


def slug_is_addressable(href: Optional[str]) -> bool:
    """Would the shipped boundary's character class accept this segment?

    A BOOLEAN, so the answer can be published without the question being
    quotable. It exists because the honest report for a posting is *this
    employer's Page is reachable* or *it is not*, and the un-honest one is the
    slug.

    Mirrors the admitted pattern's class exactly -- the ``/school/`` class,
    bounded at :data:`MAX_SLUG_CHARS`, with the dot OUTSIDE -- **AND ITS
    REFUSAL OF A QUERY, which the first version of this function did not
    have.** Its own coupling test caught that: every other function here
    drops the query before reading, on the rule that a part never read cannot
    carry anything, and this one inherited the habit where it is exactly
    wrong. The admitted pattern takes NO query and NO fragment, so a predicate
    that ignores one reported an address as reachable that the door refuses --
    the shaper LOOSER than the boundary, which is the direction that matters.

    If the two ever disagree again, ``tests/test_company_page.py`` is what
    says so: it drives this predicate and ``readonly.is_read_url`` over one
    list and asserts they agree address for address.

    **ONE DOCUMENTED ASYMMETRY REMAINS AND IT IS IN THE SAFE DIRECTION.** A
    slug carrying a forbidden substring -- ``connect``, ``invite``, ``follow``
    -- is refused by ``_FORBIDDEN_URL_SUBSTRINGS``, which is checked BEFORE
    the allowlist and which this predicate knows nothing about. So the door
    can be STRICTER than this function and never looser. That case is
    asserted on its own rather than folded into the agreement list, because a
    coupling check that quietly tolerates a mismatch has stopped coupling
    anything.
    """
    parts = _parts(href)
    if parts is None:
        return False
    if parts.query or parts.fragment:
        return False
    segments = [segment for segment in parts.path.split("/") if segment]
    if len(segments) != 2 or segments[0] != ORGANISATION_MARKER.strip("/"):
        return False
    segment = segments[1]
    if not segment or len(segment) > MAX_SLUG_CHARS:
        return False
    return set(segment) <= _SLUG_CHARS


def tally(hrefs: Iterable[Optional[str]]) -> dict[str, Any]:
    """Count a list of organisation hrefs. NO NAME IS A PARAMETER OF THIS.

    **THE SIGNATURE IS HALF THE SAFETY PROPERTY** -- this function is never
    handed a name, only addresses it then refuses to publish -- and the
    RETURN is the other half: counts positionally aligned to
    :data:`TAB_KINDS`, plus four integers. No string from any document is in
    the output, by construction.

    ``page_roots`` is the count a caller actually acts on: how many of these
    hrefs are an organisation ROOT whose segment the shipped boundary would
    accept. It answers *is this employer's Page reachable* with an integer.

    Returns::

        {
            "hrefs":        how many hrefs were handed in,
            "counts":       per-kind counts, aligned to TAB_KINDS,
            "distinct":     how many DISTINCT organisations were named,
            "numeric":      how many carried a NUMERIC segment (names nobody)
            "slug":         how many carried a SLUG (can name somebody)
            "page_roots":   how many were an addressable Page root
            "queries":      how many carried a query string at all
        }

    ``distinct`` counts organisations WITHOUT naming one: the segments are
    hashed into a set inside this function and the set's LENGTH is returned.
    The set itself never leaves.
    """
    rows = list(hrefs)
    counts = [0] * len(TAB_KINDS)
    index = {kind: position for position, kind in enumerate(TAB_KINDS)}
    seen: set[str] = set()
    numeric = 0
    slug = 0
    page_roots = 0
    queries = 0

    for href in rows:
        kind = classify_route(href)
        counts[index[kind]] += 1
        parts = _parts(href)
        if parts is not None and parts.query:
            queries += 1
        # ``page_creation`` IS IN THIS SKIP SET AND THE OTHERS ARE OBVIOUS.
        # ``/company/setup/new/`` puts the literal ``setup`` in segment 1,
        # which ``identifier_kind`` would read as a slug and ``distinct``
        # would then count as an organisation. It names none: it is the flow
        # that creates one. Counting it would inflate ``distinct`` by a
        # product route on any page that links the creation flow.
        if kind in {
            "off_company", "no_href", "page_creation", TRAVERSAL_REFUSED
        }:
            continue
        spelling = identifier_kind(href)
        if spelling == "numeric":
            numeric += 1
        elif spelling == "slug":
            slug += 1
        if spelling != "none" and parts is not None:
            segments = [s for s in parts.path.split("/") if s]
            if len(segments) >= 2:
                seen.add(segments[1])
        if slug_is_addressable(href):
            page_roots += 1

    return {
        "hrefs": len(rows),
        "counts": counts,
        "distinct": len(seen),
        "numeric": numeric,
        "slug": slug,
        "page_roots": page_roots,
        "queries": queries,
    }


def term_for(position: int) -> str:
    """The word for an index into :data:`TAB_KINDS`. The mapping back to a
    word happens HERE, in Python, and never in the document."""
    if not isinstance(position, int) or isinstance(position, bool):
        raise TypeError("a kind is addressed by an integer position")
    if not 0 <= position < len(TAB_KINDS):
        raise IndexError(
            f"position {position} is outside the {len(TAB_KINDS)} kinds this "
            "module defines; a reading taken against a different alphabet "
            "cannot be translated by this one"
        )
    return TAB_KINDS[position]
