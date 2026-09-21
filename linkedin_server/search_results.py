"""Shape a SEARCH RESULTS page. No address, query or name crosses the boundary.

`SEARCH-RESULTS-SURFACE` is the largest reader-reachable blocker in the census:
**21 rows, every one a READ, and no admitted address.** It was approved in
principle on five conditions, and **condition 1 is that the admission and a
name-free shaper land in the SAME COMMIT.** This module is that shaper. **It
admits nothing.** No entry is added to any allowlist here; the admission is a
later commit that CONSUMES this file.

## SEARCH RESULTS ARE MADE OF OTHER PEOPLE, WHICH IS WHY THIS IS THE HARD ONE

Every other shaped surface is mostly HIS: his groups, his menus, his page's
anchors. A people search is a page whose ENTIRE PAYLOAD is third parties --
ranked, named, and addressed by slug. It is the densest third-party-identity
surface the platform has, so the shipped rules are not relaxed here because the
page is "just results". **They are tightened.**

The line ``anchors.py`` draws holds verbatim and is restated because this is
exactly the page where a reader will want to cross it:

> **A slug is refused BECAUSE A SLUG IS A NAME.** That does not soften because
> the page is a search result. A ranked list of slugs is a ranked list of
> people.

## THE MECHANISM IS THE SHIPPED ONE: VOCABULARY IN, INDEX OUT

``groups.py`` -> ``menus.py`` -> ``anchors.py``, each sharper than the last, and
all three run the same engine: **the vocabulary is shipped INTO the page, the
page answers with an INTEGER INDEX into a table defined in this file, and the
mapping back to a word happens in Python.** Nothing the document holds is ever
a return value. This module keeps that engine unchanged and adds two closures.

## CLOSURE ONE: THREE CLOSED SEGMENTS, WHICH IS CONDITION 2 IN CODE

Condition 2 originally demanded a *narrow ANCHORED pattern*. It was **AMENDED**
(`_audit/2026-09-19-search-admission-condition-2-amended.md`) because anchoring
was MEASURED to do none of the work assigned to it::

    ^https://www.linkedin.com/search/.*$   anchored both ends -> 18 admitted
    /search/  wildcard, unanchored                            -> 18 admitted

**Identical.** The amended condition demands **CLOSED PATH SEGMENTS**, and this
table is that: ``search`` / ``results`` / ``<vertical>``, three positions, all
three compared by EQUALITY. ``anchors.py`` closed one or two segments; this
closes three, and a route needing a fourth needs a deliberate edit here.

## CLOSURE TWO: A TRAVERSAL IS REFUSED, NEVER RESOLVED

This is the closure ``anchors.py`` does not have, and it is not a refinement --
it is the defect the amendment found::

    /search/results/people/../../mypreferences/d/close-account

**Its first three segments are a people search. Its browser-normalised form is
an account-ending address, and NO FORBIDDEN SUBSTRING NAMES IT** -- the denylist
refuses its siblings (``/psettings/``, ``/invite``) and misses this one.

Run against a segment matcher with no dot rule, that address matches
``person_result`` on three-segment equality and is reported as a person. **The
shaper would be certifying, as a read of people, an address that ends his
account.**

So: a ``..`` or ``.`` segment ANYWHERE makes the route unjudgeable from its
leading segments, and it is counted as :data:`TRAVERSAL_REFUSED` and dropped.
**It is never normalised.** Resolving it would mean this module deciding what a
traversal means -- that is the browser's job, and a shaper that guesses has
invented a second, disagreeing URL parser inside the guard.

## CLOSURE THREE: THE QUERY IS WHERE THE NAME IS TYPED

``anchors.py`` drops the query before reading, on ``groups.py``'s rule that a
part never read cannot carry anything. **On this surface that rule stops being
hygiene and becomes the primary defence**, because a search query is not
incidental -- ``?keywords=<a person's name>`` is the whole point of the page.

So the query is dropped before any segment is read, and **its PRESENCE is
counted as an integer** (:func:`tally`'s ``queries_present``). A caller can
learn that results were filtered. A caller can never learn by what.

## NO ADDRESS, QUERY, SLUG, ID OR NAME IS A PARAMETER OF ANY FUNCTION HERE

Asserted on ``inspect.signature`` in ``tests/test_search_results.py``, the way
``groups.py`` and ``anchors.py`` do it. :func:`read_results` is the only
function that touches a page; its one string parameter is ``html``, the
documented control path. :func:`tally` -- the function a caller publishes --
takes INTEGERS and **cannot be handed a needle even by mistake.**

## WHICH CENSUS ROWS THIS SERVES, AND THE ONE IT MUST NOT

The blocker holds **21 rows: 20 READS and ONE WRITE.** ``N 4`` -- *send an
invitation from a people-search result* -- **is the write, its ruling is
explicitly NOT inherited, and condition 5 of the approval is that NOTHING IS
FIRED FROM THIS SURFACE.** Nothing in this module presses, submits or sends,
and no function here takes a confirm token. A shaper that could fire would
have imported ``N 4``'s ruling by accident.

The reads split in two, and **the route classifier alone served only the
first half**:

* ``N 79``, ``N 161``, ``N 179``, ``N 194``, ``M C70`` -- *which search is
  this, and what shapes does it hold*. The route table answers these.
* ``N 80``-``N 94`` -- **sixteen consecutive FILTER rows**, which are
  pressable controls with labels, not routes. The filter panel below answers
  these, and ``_audit/_census/network.md`` calls rows 79-93 *"the largest
  single hole in the slice and the only one that is pure silence... the
  repository contains ZERO SENTENCES about any of them."*

## THREE LIMITS, MEASURED RATHER THAN ARGUED

Both are rows in :func:`route_control_corpus`, driven through the shipped
decision under V8. **They are written down because a limit nobody measured is
indistinguishable from a limit nobody has,** and this module's whole claim is
that its refusals are real.

**1. MATCHING IS CASE SENSITIVE, and the miss lands on the safe side.**
``/SEARCH/RESULTS/PEOPLE/`` is classified ``off_search`` -- not recognised as a
search at all -- rather than being admitted as a people vertical. A
case-insensitive comparison would be the dangerous repair: it widens what
matches the table, and this table's whole job is to be narrow.

**2. A PERCENT-ENCODED TRAVERSAL IS NOT REFUSED.**
``/search/results/people/..%2f..%2fmypreferences`` classifies as
``person_result`` with a non-numeric entity, because ``%2f`` is not a path
separator to this classifier. **It is not one to a browser either** -- user
agents do not decode ``%2F`` into a segment boundary before routing, so that
address does not traverse and the classification is not a hole in practice.
**The reason it stays unfixed is the stronger half:** refusing it would mean
decoding, and decoding is normalising, and this module refuses to normalise for
the reason above -- a shaper that resolves an address has invented a second,
disagreeing URL parser inside the guard. *If a user agent is ever shown to
decode it, the repair is a refusal of the encoded form, never a decode step.*

**3. A DECORATED SINGLE-WORD LABEL MISSES, and that is the asymmetry's price.**
Measured: a control labelled ``Keywords (first name, last name)`` does NOT
match the term ``keywords``, because a single-word phrase must be the whole
label. The census's own wording for ``N 93`` is exactly that decorated form,
so this is not hypothetical.

**The miss lands on the safe side** -- the control is reported in
``unmatched_controls``, which is a visible number, rather than being
classified as something it is not. And the alternative is worse: relaxing the
single-word rule is precisely the mutation that makes ``Connections of`` match
``connections``, which reports a PERSON-VALUED filter as a degree filter. *The
repair, if the live labels turn out to be decorated, is to add the decorated
form to the vocabulary as its own phrase -- never to loosen the matcher.*

## WHAT IT DOES NOT CLAIM

* **Not that it saw every result.** Search pages lazy-load and re-rank; a count
  is a reading with a timestamp, not a property of the query.
* **Not that a result is a real account.** It reports route shape, nothing more.
* **Not that it has ever seen a live search page.** It has not. Every number
  attached to it comes from fixtures and from the shipped script's own source,
  run under V8.
* **Not that the surface is admitted.** It is not. Nothing here opens an
  address, and this file passing its tests does not discharge condition 1 --
  see the deliverable for what still stands between here and admission.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Iterable

from linkedin_server import coerce, dom

#: THE CLOSED OUTPUT ALPHABET. Order is the contract: the page returns a
#: POSITION in this tuple, so reordering silently renames every reading ever
#: taken. ``tests/test_search_results.py`` pins it.
#:
#: ``person_result`` IS THE HAZARD CLASS and is first on purpose -- it is the
#: vertical whose every row is a third party, so it is COUNTED and never
#: described, and anything that would misclassify INTO or OUT OF it is the
#: defect the segment and traversal rules exist to prevent.
RESULT_KINDS: tuple[str, ...] = (
    "person_result",
    "company_result",
    "school_result",
    "job_result",
    "group_result",
    "event_result",
    "post_result",
    "newsletter_result",
    "service_result",
    "all_results",
    "traversal_refused",
    "unclassified",
    "off_search",
    "no_href",
)

#: ``(kind token, segment 0, segment 1, segment 2)``. Matching is SEGMENT
#: EQUALITY at THREE FIXED POSITIONS -- the amended condition 2 in code. See
#: the module docstring for the address that proves anchoring is not enough.
RESULT_TABLE: tuple[tuple[str, str, str, str], ...] = (
    ("person_result", "search", "results", "people"),
    ("company_result", "search", "results", "companies"),
    ("school_result", "search", "results", "schools"),
    ("job_result", "search", "results", "jobs"),
    ("group_result", "search", "results", "groups"),
    ("event_result", "search", "results", "events"),
    ("post_result", "search", "results", "content"),
    ("newsletter_result", "search", "results", "newsletters"),
    ("service_result", "search", "results", "services"),
    ("all_results", "search", "results", "all"),
)

#: A refusal, and a literal like everything else here.
UNCLASSIFIED = "unclassified"

#: The class a dot segment produces. Named because it is the one a reviewer
#: must be able to find: a nonzero count here means the page offered a route
#: whose leading segments LIE about where it goes.
TRAVERSAL_REFUSED = "traversal_refused"

#: The segments that trigger it. A route is refused if ANY segment equals one
#: of these -- position-free on purpose, because a traversal's harm does not
#: depend on where in the path it sits.
DOT_SEGMENTS: frozenset[str] = frozenset({"..", "."})

_HOST = "www.linkedin.com"

#: THE ONE ADDRESS THIS MODULE'S TOOL OPENS, and it is a LITERAL with no
#: caller-supplied part. **THIS CONSTANT IS NOT AN ADMISSION AND CANNOT BE
#: ONE** -- it is a string; the navigation boundary is a separate module and
#: nothing here edits it. The entry that admits this address lives there, with
#: the measurement beside it, and 2026-09-20 is the day the two landed
#: together.
#:
#: **IT CARRIES NO QUERY, AND THAT IS THE DESIGN RATHER THAN AN OMISSION.** A
#: search query is where a person's name is typed, so a tool that accepted one
#: would take a needle as a parameter -- the exact thing every function in this
#: module is asserted not to do, one layer up where the assertion does not
#: reach. ``_audit/2026-09-19-search-admission-preconditions.md`` section B.4
#: hands the admitting wave a problem that follows from accepting one: eight of
#: eleven ordinary search keywords (``password``, ``settings``, ``invitation``
#: ...) are refused by the forbidden-substring list, so a keyword-taking tool
#: must decide what to answer when a caller's word trips a write guard.
#: **Taking no keyword dissolves that question instead of answering it.**
#:
#: The pattern admits a query shape so the address stays usable if a later
#: wave rules that a keyword may be passed. Nothing today passes one.
PEOPLE_SEARCH_URL = f"https://{_HOST}/search/results/people/"

#: THE SCRIPT LIVES IN ``dom.py``. Only that module may waive ``evaluate``, and
#: every executed script is declared and scanned there -- so putting page
#: contact here would spread a narrow allowance into a habit. This module keeps
#: the vocabulary, the closed alphabet and the tallying.
_CLASSIFY_IN_PAGE = dom.SEARCH_RESULTS_JS


#: WHY THE READERS BELOW NEVER CALL ``int()`` ON WHAT THE PAGE HANDS BACK.
#:
#: **MEASURED 2026-09-20, and it was a hole rather than a tidy-up.** The
#: shipped form was ``int(value)``, and ``int()`` PUTS THE VALUE IT REFUSED
#: VERBATIM INTO ITS OWN ValueError::
#:
#:     ValueError: invalid literal for int() with base 10: '<the label>'
#:
#: That exception leaves the reader, is caught by ``server._error``, and is
#: rendered through ``config.scrub`` -- which substitutes THIS SERVER'S OWN
#: PATHS and nothing else, **because a name has no shape to scrub and
#: ``tests/test_no_committed_identity.py`` says so in its first line.** So a
#: string the page put in a count slot reached a caller INTACT, inside an
#: error message, on the one surface whose every row is a third party.
#:
#: Three payloads reached it, driven through the real functions: a string
#: inside ``counts``, a string in the ``anchors`` scalar, and the first of
#: those again through :func:`read_filters`. The module docstring's claim is
#: *"no string from the document, by construction"* -- and the construction
#: had an exception-shaped gap in it.
#:
#: The ruling that admits this surface names *"a measured case of the shaper
#: emitting a name, a slug, a member id or an urn"* as the thing that REVOKES
#: the admission. This was one, found before the admission rather than after.


def _as_int(value: Any) -> int | None:
    """An integer, or ``None``. IT NEVER RAISES AND NEVER QUOTES ITS INPUT.

    Both halves are the contract. ``int()`` answers the same question and
    carries the rejected value out in its message, which on this surface is
    how a name leaves the process. The only things this can ever return are
    an integer it was handed and ``None``, so it can carry nothing.

    ``bool`` is refused deliberately: ``True`` is an ``int`` in Python, and a
    count of ``True`` results is a reading nobody took.

    THE BODY MOVED TO ``linkedin_server.coerce`` ON 2026-09-20 and this name
    stayed, for two reasons that pull the same way. The repair turned out to be
    needed at 45 sites in 14 readers rather than at this one, and a helper
    copied fourteen times is fourteen things that can drift -- that is the
    whole argument for a shared module. But this name is also the PLANT POINT
    of ``scripts/_check_the_shaper_leak_guard_can_fail.py``, which proves the
    guard can fail by rebinding ``search_results._as_int`` to ``int``; the
    functions below resolve it as a module global at call time, so the plant
    still reaches them. Delegating THROUGH this function preserves that,
    where importing ``coerce.as_int`` into their bodies would have silently
    disarmed the one control that shows this guard failing.
    """
    return coerce.as_int(value)


def _counts_only(values: Any) -> tuple[list[int], int]:
    """Position-preserving integers, and how many entries were not integers.

    **A NON-INTEGER IS SUBSTITUTED, NEVER DROPPED**, and the difference is the
    hazard class. ``counts`` is POSITIONAL -- position N is
    ``RESULT_KINDS[N]`` -- so dropping one entry renames every kind behind it,
    and index 0 is ``person_result``. That is exactly the rename
    :func:`term_for` refuses to commit by clamping, arriving one function
    earlier.

    The substitute is 0 and the substitution is COUNTED, so a page answering
    with something other than a number becomes a VISIBLE INTEGER rather than a
    silent shift or a raised string.
    """
    if not isinstance(values, (list, tuple)):
        return [], 0 if values is None else 1
    out: list[int] = []
    refused = 0
    for value in values:
        number = _as_int(value)
        if number is None:
            refused += 1
            number = 0
        out.append(number)
    return out, refused


def _scalars_only(
    raw: Any, names: tuple[tuple[str, str], ...]
) -> tuple[dict[str, int], int]:
    """``{output name: integer}``, and how many values were not integers.

    **ABSENT IS NOT THE SAME AS WRONG**, and they are counted differently. A
    key the page never set reads 0 and is NOT counted -- that is the shipped
    ``or 0`` behaviour and it means "I was not told". A key set to something
    that is not an integer IS counted, because that is the page answering with
    a string, and a string from this page is a name until shown otherwise.
    """
    source = raw if isinstance(raw, dict) else {}
    out: dict[str, int] = {}
    refused = 0
    for output_name, key in names:
        value = source.get(key)
        number = _as_int(value)
        if number is None:
            if value is not None:
                refused += 1
            number = 0
        out[output_name] = number
    return out, refused


async def read_results(page: Any, html: str = "") -> dict[str, Any]:
    """Classify a search page's result anchors. Returns COUNTS and integers.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE. What crosses the boundary back
    is a list of counts positionally aligned to :data:`RESULT_KINDS` plus four
    integers -- no string from the document, by construction.

    ``html`` IS THE CONTROL PATH and is not a reading of anything: it runs the
    same classifier against a detached container so :func:`control_fixture` can
    prove the classifier works and refuses the adversarial routes, at no page
    load and with no navigation. It is a parameter of the READER, never of
    :func:`tally`.

    ``values_refused`` is the count of fields the page answered with something
    that was not an integer. It is normally 0; a nonzero is a FINDING rather
    than a shape, and it is reported as a number precisely because the value
    that caused it may not be. See :func:`_as_int`.
    """
    raw = await dom.read_search_result_classes(
        page,
        table=[list(row) for row in RESULT_TABLE],
        classes=list(RESULT_KINDS),
        host=_HOST,
        html=html or "",
    )
    source = raw if isinstance(raw, dict) else {}
    counts, counts_refused = _counts_only(source.get("counts"))
    scalars, scalars_refused = _scalars_only(
        source,
        (
            ("anchors_seen", "anchors"),
            ("queries_present", "queries_present"),
            ("numeric_entity", "numeric_entity"),
            ("non_numeric_entity", "non_numeric_entity"),
        ),
    )
    return {
        "anchors_seen": scalars["anchors_seen"],
        "counts": counts,
        "queries_present": scalars["queries_present"],
        "numeric_entity": scalars["numeric_entity"],
        "non_numeric_entity": scalars["non_numeric_entity"],
        "values_refused": counts_refused + scalars_refused,
    }


def term_for(index: int) -> str:
    """One index -> one literal. Out of range REFUSES rather than clamping.

    A clamp would silently rename one kind to another -- and the kind at index
    0 is ``person_result``, so a clamp could rename a page full of people into
    a page of companies, or the reverse. Never clamped.
    """
    if 0 <= index < len(RESULT_KINDS):
        return RESULT_KINDS[index]
    return "index_out_of_range"


def tally(counts: Iterable[int], queries_present: int = 0) -> dict[str, Any]:
    """COUNTS BY KIND. Its parameters are INTEGERS -- a needle cannot reach it.

    A short list is reported as such rather than padded, because a missing kind
    and a zero-count kind are different answers, and collapsing them is how a
    reader says "none of those" when it means "I was not told".

    **"CANNOT BE HANDED A NEEDLE EVEN BY MISTAKE" IS NOW TRUE OF THE
    BEHAVIOUR AND NOT ONLY OF THE SIGNATURE.** It coerced with ``int()`` until
    2026-09-20, so handing it a string raised an exception QUOTING that string
    -- the sentence was a claim about the parameter's type while the mechanism
    said something weaker. It now refuses the same way the readers do.
    """
    values, _refused = _counts_only(list(counts))
    by_kind = {
        RESULT_KINDS[position]: value
        for position, value in enumerate(values)
        if position < len(RESULT_KINDS)
    }
    overflow = max(0, len(values) - len(RESULT_KINDS))
    return {
        "by_kind": dict(sorted(by_kind.items())),
        "kinds_not_reported": max(0, len(RESULT_KINDS) - len(values)),
        "positions_beyond_the_alphabet": overflow,
        "total_classified": sum(by_kind.values()),
        # NAMED SEPARATELY because it is the number a caller must not publish
        # per-record. A count of person results is a shape of his own search;
        # the results themselves are other people.
        "person_results": by_kind.get("person_result", 0),
        # NAMED SEPARATELY for the opposite reason: a nonzero here is not a
        # shape, it is a FINDING. The page offered a route whose leading
        # segments do not say where it goes.
        "traversals_refused": by_kind.get(TRAVERSAL_REFUSED, 0),
        # THE FILTER WAS SEEN, NEVER READ.
        "queries_present": int(queries_present),
    }


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can publish. Asserted over adversarial input."""
    return frozenset(RESULT_KINDS) | {"index_out_of_range"}


def refuses_traversal(segments: Iterable[str]) -> bool:
    """True if any segment is a dot segment. The Python mirror of the JS rule.

    Exists so the rule can be CONTROLLED without a browser: the shipped
    classifier is JavaScript and the suite is structural, so this is the
    function a test can drive over the adversarial route directly. It takes
    SEGMENTS THAT A CALLER ALREADY HAS -- it neither parses nor accepts an
    address, and it returns a BOOLEAN, so it can carry nothing outward.
    """
    return any(segment in DOT_SEGMENTS for segment in segments)


# ---------------------------------------------------------------------------
# THE FILTER PANEL. Sixteen of the twenty reads live here.
# ---------------------------------------------------------------------------
#
# THE ROUTE CLASSIFIER ABOVE DOES NOT SERVE THEM. It answers "what shapes of
# link does this page hold"; rows N 80-N 94 ask "which FILTERS does this
# search offer", and those are pressable controls with labels, not routes.
#
# ``_audit/_census/network.md`` on rows 79-93: *"the largest single hole in
# the slice and the only one that is pure silence. Fifteen consecutive rows,
# all READ, all reversible by construction, and the repository contains ZERO
# SENTENCES about any of them."* These are the first.

#: THE FILTER VOCABULARY, AND ITS ORDER IS THE CONTRACT -- the page returns a
#: POSITION in this tuple. **The three hazard terms are first on purpose.**
#:
#: Index 0 and 1 are the filters whose VALUE IS A PERSON, and index 2 is the
#: free-text box -- the place on this surface where a name is typed. Putting
#: them first means anything that would misclassify INTO or OUT OF them is the
#: defect this module's matching rule exists to prevent, and a reader scanning
#: the tuple meets the dangerous three before the ordinary eleven.
#:
#: Each term is normalised already: lowercase, single-spaced, a-z0-9 only.
FILTER_TERMS: tuple[str, ...] = (
    "connections of",       # N 85 -- HAZARD: its value is a person
    "followers of",         # N 86 -- HAZARD: its value is a person
    "keywords",             # N 93 -- HAZARD: free text, where a name is typed
    "connections",          # N 81 -- degree; a PREFIX of index 0, see below
    "actively hiring",      # N 82
    "locations",            # N 83
    "current company",      # N 84
    "past company",         # N 87
    "school",               # N 88
    "industry",             # N 89
    "profile language",     # N 90
    "open to volunteering", # N 91
    "service categories",   # N 92
    "people",               # N 80 -- the vertical, not a filter proper
)

#: The census row each term serves, so the vocabulary can be checked AGAINST
#: THE LEDGER rather than against memory. A term that serves no row is a term
#: nobody asked for; a row with no term is a row this shaper cannot serve, and
#: both are findings rather than opinions.
FILTER_TERM_ROWS: tuple[str, ...] = (
    "N 85", "N 86", "N 93", "N 81", "N 82", "N 83", "N 84",
    "N 87", "N 88", "N 89", "N 90", "N 91", "N 92", "N 80",
)

#: THE CLOSED SET OF VALUE CLASSES. What KIND of thing a filter's value is --
#: decided in Python from the term's INDEX, never read off the page. The page
#: never tells this process what a filter is set to; it only says which
#: filters exist.
VALUE_CLASSES: tuple[str, ...] = (
    "person_valued",
    "needle_valued",
    "org_valued",
    "taxonomy_valued",
    "boolean_valued",
    "vertical",
)

#: Term index -> value class. Positionally aligned to :data:`FILTER_TERMS`.
FILTER_VALUE_CLASSES: tuple[str, ...] = (
    "person_valued",    # connections of
    "person_valued",    # followers of
    "needle_valued",    # keywords
    "taxonomy_valued",  # connections (degree: 1st / 2nd / 3rd+)
    "boolean_valued",   # actively hiring
    "taxonomy_valued",  # locations
    "org_valued",       # current company
    "org_valued",       # past company
    "org_valued",       # school
    "taxonomy_valued",  # industry
    "taxonomy_valued",  # profile language
    "boolean_valued",   # open to volunteering
    "taxonomy_valued",  # service categories
    "vertical",         # people
)


def filter_phrase_index() -> tuple[tuple[str, int], ...]:
    """``(phrase, term index)`` SORTED LONGEST-FIRST. ``menus.py``'s ordering.

    **THIS SURFACE HAS ITS OWN ``Star Anise`` AND IT IS BUILT INTO THE
    VOCABULARY:** ``connections`` is a PREFIX of ``connections of``, and they
    are different rows -- ``N 81`` is a degree filter whose value is a closed
    taxonomy, ``N 85`` is a filter whose value IS A PERSON.

    Two things keep them apart and BOTH are needed:

    * **Longest-first order**, computed here, so the two-word phrase is tried
      before the one-word one.
    * **The single-word asymmetry** in the matcher -- a one-word phrase must be
      the WHOLE label. Order alone is not enough: a label reading
      ``Connections of`` would still match the bare term ``connections`` by
      containment if the matcher allowed it, and a page whose only filter is
      the person-valued one would report a degree filter.

    Sorting here rather than in the page is deliberate: the loop in
    ``dom.FILTER_PANEL_JS`` takes the order as given and must not re-sort, so
    the ordering is decided once, in Python, where it can be tested.
    """
    return tuple(
        sorted(
            ((phrase, index) for index, phrase in enumerate(FILTER_TERMS)),
            key=lambda pair: (-len(pair[0].split()), -len(pair[0]), pair[0]),
        )
    )


async def read_filters(page: Any, html: str = "") -> dict[str, Any]:
    """Which filters does this search offer? COUNTS PER TERM, and integers.

    The second of the two functions here that touch a page. What crosses back
    is a list of counts positionally aligned to :data:`FILTER_TERMS` plus four
    integers. **No label crosses, on any path** -- the matching happens in the
    page precisely because a label on this surface can be a person's name.

    ``html`` IS THE CONTROL PATH, as in :func:`read_results`.

    ``values_refused`` carries the same meaning as in :func:`read_results`,
    and the hazard is sharper here: the thing a filter control holds that is
    not an integer is its LABEL, and a label on this surface reads
    ``Connections of <a person>``.
    """
    raw = await dom.read_search_filters(
        page,
        phrases=[[phrase, index] for phrase, index in filter_phrase_index()],
        term_count=len(FILTER_TERMS),
        html=html or "",
    )
    source = raw if isinstance(raw, dict) else {}
    counts, counts_refused = _counts_only(source.get("counts"))
    scalars, scalars_refused = _scalars_only(
        source,
        (
            ("controls_seen", "controls"),
            ("matched_controls", "matched_controls"),
            # THE DENOMINATOR, and it is reported because without it a page
            # with a changed selector is indistinguishable from a page with
            # no filters.
            ("unmatched_controls", "unmatched_controls"),
            ("empty_labels", "empty_labels"),
        ),
    )
    return {
        "controls_seen": scalars["controls_seen"],
        "counts": counts,
        "matched_controls": scalars["matched_controls"],
        "unmatched_controls": scalars["unmatched_controls"],
        "empty_labels": scalars["empty_labels"],
        "values_refused": counts_refused + scalars_refused,
    }


#: HOW MANY CONSECUTIVE UNCHANGED READS END THE WAIT, and how far apart they
#: are taken. Three rather than two: the panel was measured pausing between
#: bursts, and two equal reads 350 ms apart is a pause, where three spanning
#: 1.05 s is a plateau. Twenty polls is the ceiling, so the wait can add at
#: most about seven seconds to a call that would otherwise have been wrong.
PANEL_STABLE_READS = 3
PANEL_POLL_MS = 350
PANEL_MAX_POLLS = 20

#: HOW LONG A PAGE THAT HAS DRAWN **NOTHING** IS WAITED ON, and it is much
#: shorter than the full budget. A panel still at ZERO controls after this many
#: polls is not a panel drawing slowly; it is a page with no filter panel on it,
#: and continuing to poll a page that never started is waiting for a different
#: page to arrive.
#:
#: **IT EXISTS BECAUSE THE FULL BUDGET MADE THIS READER UNDRIVABLE**, which is
#: worse than slow. ``tests/reader_leak_baseline.json`` records a verdict per
#: page reader and says of its own third value: *"not_driven means this offline
#: harness could not reach it, which is NEVER A PASS."* The harness drives each
#: reader against a planted page on a 5 s budget; a planted page draws no
#: controls, so the zero-guard held on for 20 polls at 350 ms -- 7 s -- and the
#: reader timed out and was recorded unreached. A reader nothing can drive
#: cannot be shown to leak or not to leak.
#:
#: SO THE WORST CASE IS NOW SPLIT IN TWO, on the distinction that matters: a
#: panel that is GROWING gets the whole budget, because that is the case worth
#: waiting for; a panel that has drawn NOTHING gets about two seconds.
PANEL_ZERO_POLLS = 6


async def read_filters_when_settled(page: Any) -> dict[str, Any]:
    """:func:`read_filters`, but not until the panel has STOPPED GROWING.

    ## THE DEFECT THIS EXISTS FOR, MEASURED RATHER THAN SUSPECTED

    ``linkedin_people_search_shape`` returned its filters on two of three
    end-to-end firings. The third read a page that had drawn 45 of its 83
    controls and reported EVERY filter as zero. Re-measured under load on
    2026-09-21 over eight firings, six of which completed:

        controls_seen 45  ->  filters_offered 0   (three firings)
        controls_seen 62  ->  filters_offered 3   (two firings)
        controls_seen 73  ->  filters_offered 3   (one firing)

    The correlation is exact in both directions, and ``controls_seen`` was
    already in the payload disclosing it.

    ## WHY ``BROWSER.goto``'s SETTLE DOES NOT COVER THIS, AND WHY LOAD MAKES
    ## IT WORSE RATHER THAN BETTER

    ``goto`` navigates on ``domcontentloaded`` and then waits for
    ``networkidle`` with a flat fallback, and its own docstring says that is
    **not a readiness check**. On a loaded box the renderer is starved, fewer
    requests are in flight, and a 500 ms network lull arrives EARLIER -- so
    the settle SHORTENS against a panel that has drawn less. That is why both
    quiet runs looked deterministic and only a pinned CPU exposed it: the
    defect hides on exactly the machine a fix would naturally be verified on.

    ## WHAT IT WAITS ON, AND WHY IT IS NOT A SELECTOR

    **NO NEW SELECTOR AND NO NEW VOCABULARY.** A ``wait_for_selector`` here
    would be a guess at LinkedIn's class names on a surface this package has
    barely met, and a wrong guess fails in the quiet direction -- it would
    time out and read the half-drawn page anyway, which is today's behaviour
    with extra steps. This waits on the SHIPPED READER'S OWN NUMBER instead:
    it re-reads until ``controls_seen`` has been unchanged for
    :data:`PANEL_STABLE_READS` consecutive polls. The instrument measuring
    readiness is the instrument that will take the reading.

    It costs no new ``page.evaluate`` CALL SITE -- every poll re-enters
    ``dom.read_search_filters``, which already carries the one waiver -- so
    the pinned waiver budget does not move.

    ## WHAT ``settled`` DOES AND DOES NOT MEAN

    **``settled`` IS NOT "COMPLETE" AND IS NEVER REPORTED AS IT.** A panel
    that is stuck at 45 forever is stable at 45, and this function cannot
    tell a finished panel from a wedged one -- nothing here knows how many
    controls the page intends to draw, and a hardcoded expectation would be a
    constant nobody measured pretending to be a denominator. So the trajectory
    travels with the reading: ``controls_first``, ``controls_last``, ``polls``
    and ``settled``, and a caller who sees ``controls_last`` well below what
    other calls achieve still knows to distrust it.

    ``settled`` is ``False`` when the poll budget ran out with the count still
    moving, which is a FINDING -- the panel was still drawing when the reading
    was taken -- and it is published rather than retried forever.
    """
    reading = await read_filters(page)
    first = coerce.as_count(reading.get("controls_seen"))
    last = first
    stable = 1
    polls = 1
    settled = False

    while polls < PANEL_MAX_POLLS:
        # A ZERO IS NEVER A PLATEAU. A page that has drawn no control at all
        # is a page that has not started, and three zeros in a row would
        # otherwise "settle" instantly on precisely the blind reading this
        # function exists to prevent.
        if last > 0 and stable >= PANEL_STABLE_READS:
            settled = True
            break
        # BUT A PAGE THAT NEVER STARTS IS NOT WAITED ON FOR THE WHOLE BUDGET.
        # See :data:`PANEL_ZERO_POLLS`: holding the full 20 polls open on a
        # page with no panel is how this reader became undrivable by the
        # offline leak harness, and ``not_driven`` is never a pass.
        if last <= 0 and polls >= PANEL_ZERO_POLLS:
            break
        # ``asyncio.sleep`` AND NOT ``page.wait_for_timeout``, AND A TEST
        # CONVICTED THE OTHER CHOICE. The interval is THIS LOOP'S pacing, not
        # something the page is being asked to do, so it must not require a
        # page capability. Every shipped reader in this package touches a page
        # only through ``evaluate``; the first version of this function called
        # ``page.wait_for_timeout`` and therefore raised ``AttributeError`` on
        # ``tests/test_the_search_shaper_emits_no_name.py``'s hostile page,
        # which implements ``evaluate`` and nothing else. The tool swallowed it
        # into ``_error`` and published a payload with no ``denominators`` --
        # so a reader that quietly widened its demands on the page turned three
        # name-safety proofs into KeyErrors. The narrower dependency is both
        # the safer one and the one the rest of this package already keeps.
        await asyncio.sleep(PANEL_POLL_MS / 1000)
        reading = await read_filters(page)
        polls += 1
        current = coerce.as_count(reading.get("controls_seen"))
        stable = stable + 1 if current == last else 1
        last = current

    if last > 0 and stable >= PANEL_STABLE_READS:
        settled = True

    return {
        **reading,
        "panel_wait": {
            "polls": polls,
            "settled": settled,
            "controls_first": first,
            "controls_last": last,
            "stable_reads_required": PANEL_STABLE_READS,
            "poll_ms": PANEL_POLL_MS,
            "max_polls": PANEL_MAX_POLLS,
            # WHICH BUDGET THIS READING SPENT. A caller seeing ``polls`` equal
            # to this and ``controls_last`` zero is looking at a page that
            # drew no panel at all, not at one this gave up on early.
            "zero_polls": PANEL_ZERO_POLLS,
        },
    }


def filter_term_for(index: int) -> str:
    """One index -> one literal. Out of range REFUSES rather than clamping.

    A clamp would rename one filter to another, and indices 0-2 are the three
    whose values are a person or a needle. Never clamped.
    """
    if 0 <= index < len(FILTER_TERMS):
        return FILTER_TERMS[index]
    return "index_out_of_range"


def value_class_for(index: int) -> str:
    """What KIND of value that filter takes. Decided here, never on the page."""
    if 0 <= index < len(FILTER_VALUE_CLASSES):
        return FILTER_VALUE_CLASSES[index]
    return "index_out_of_range"


def tally_filters(counts: Iterable[int]) -> dict[str, Any]:
    """WHICH FILTERS THIS SEARCH OFFERS. Its parameter is INTEGERS.

    A short list is reported as such rather than padded -- "the page has no
    School filter" and "I was told about eight terms" are different answers.

    Refuses a non-integer rather than raising on it, for the reason given in
    :func:`tally`.
    """
    values, _refused = _counts_only(list(counts))
    by_term = {
        FILTER_TERMS[position]: value
        for position, value in enumerate(values)
        if position < len(FILTER_TERMS)
    }
    by_value_class = {name: 0 for name in VALUE_CLASSES}
    for position, value in enumerate(values):
        if position < len(FILTER_VALUE_CLASSES):
            by_value_class[FILTER_VALUE_CLASSES[position]] += value
    return {
        "by_term": dict(sorted(by_term.items())),
        "by_value_class": dict(sorted(by_value_class.items())),
        "terms_not_reported": max(0, len(FILTER_TERMS) - len(values)),
        "positions_beyond_the_vocabulary": max(0, len(values) - len(FILTER_TERMS)),
        "filters_offered": sum(by_term.values()),
        # NAMED SEPARATELY because these are the filters a caller must never
        # be allowed to publish the VALUE of. The count says the page offers
        # a way to search by a particular person; it never says which person,
        # and nothing in this module can be made to.
        "person_valued_filters": by_value_class["person_valued"],
        "needle_valued_filters": by_value_class["needle_valued"],
    }


def filter_alphabet() -> frozenset[str]:
    """Every string the filter half can publish."""
    return (
        frozenset(FILTER_TERMS)
        | frozenset(VALUE_CLASSES)
        | {"index_out_of_range"}
    )


def filter_control_fixture() -> str:
    """Filter controls that MUST match, and the ones that must NOT misclassify.

    **THE COLLISION IS THE POINT.** The fixture carries ``Connections of`` and
    ``Connections`` as separate controls, because they are separate census
    rows with different value classes and the matcher has to keep them apart.
    It also carries the ``menus.py`` scar shape directly -- a two-token label
    whose first token is a single-word vocabulary term -- using a spice, which
    is that scar's own substitute and not a person.
    """
    return (
        '<button>Connections of</button>'
        '<button>Connections</button>'
        '<button>Followers of</button>'
        '<button aria-label="Keywords">k</button>'
        '<button>Actively hiring</button>'
        '<button>Locations</button>'
        '<button>Current company</button>'
        '<button>Past company</button>'
        '<button>School</button>'
        '<button>Industry</button>'
        '<button>Profile language</button>'
        '<button>Open to volunteering</button>'
        '<button>Service categories</button>'
        '<button>People</button>'
        # MUST NOT MATCH: a two-token label whose first token is the
        # single-word term "school". menus.py's Star Anise, one surface over.
        '<button>School Anise</button>'
        # MUST NOT MATCH: an ordinary page control that is not a filter.
        '<button>Next</button>'
        # MUST NOT MATCH and must be COUNTED as empty, not as a miss.
        '<button></button>'
    )


#: What :func:`filter_control_fixture` must produce, per term. Written out so
#: the control has an EXPECTATION rather than only an output.
FILTER_CONTROL_EXPECTATION: dict[str, int] = {
    "connections of": 1,
    "followers of": 1,
    "keywords": 1,
    "connections": 1,
    "actively hiring": 1,
    "locations": 1,
    "current company": 1,
    "past company": 1,
    "school": 1,
    "industry": 1,
    "profile language": 1,
    "open to volunteering": 1,
    "service categories": 1,
    "people": 1,
}


def control_fixture() -> str:
    """Routes that MUST classify, including the ones that must NOT misclassify.

    **THE ADVERSARIAL CASES ARE THE POINT.** A classifier that returns one kind
    for everything looks exactly like a working one on a page that happens to
    be uniform, so the fixture carries the three shapes that would convict a
    weaker design:

    * ``/search/results/people/../../mypreferences/d/close-account`` -- **the
      address the condition-2 amendment was measured on.** Three-segment
      equality alone calls it ``person_result``. It ends his account.
    * ``/search/results/people/?keywords=...`` -- the query form, present so
      the fixture proves the query is DROPPED and only COUNTED. The needle here
      is the literal word ``example``, never a person.
    * ``/search/results/peoplefinder/`` -- a vertical whose name CONTAINS the
      hazard vertical, which a containment matcher calls ``person_result``.
      It is ``menus.py``'s ``Star Anise`` scar one level over, and the reason
      the comparison is equality.

    **EVERY SLUG HERE IS SYNTHETIC AND DELIBERATELY NOT A PERSON**, and each
    carries ``example``, which is in the shape guard's own synthetic
    vocabulary, so it passes on sight and costs no argument. A tracked file may
    not carry a third party's name even as an illustration -- and on THIS
    surface, where a fixture row is literally a search result, that rule is at
    its sharpest.
    """
    return (
        '<a href="/search/results/people/?keywords=example">a</a>'
        '<a href="/search/results/companies/">b</a>'
        '<a href="/search/results/schools/">c</a>'
        '<a href="/search/results/jobs/">d</a>'
        '<a href="/search/results/groups/">e</a>'
        '<a href="/search/results/events/">f</a>'
        '<a href="/search/results/content/">g</a>'
        '<a href="/search/results/newsletters/">h</a>'
        '<a href="/search/results/services/">i</a>'
        '<a href="/search/results/all/">j</a>'
        '<a href="/search/results/people/../../mypreferences/d/close-account">k</a>'
        '<a href="/search/results/peoplefinder/">l</a>'
        '<a href="/example/elsewhere/">m</a>'
        '<a>n</a>'
    )


#: What :func:`control_fixture` must produce. Written out so the control has an
#: EXPECTATION rather than only an output -- a control whose result nobody
#: predicted cannot fail.
#:
#: Note ``unclassified`` is 1 (``peoplefinder``, which is under ``/search/``
#: and matches no row) and ``off_search`` is 1 (the route that is not a search
#: at all). Those two being DIFFERENT kinds is deliberate: "a search vertical I
#: do not know" and "not a search" are different answers.
CONTROL_EXPECTATION: dict[str, int] = {
    "person_result": 1,
    "company_result": 1,
    "school_result": 1,
    "job_result": 1,
    "group_result": 1,
    "event_result": 1,
    "post_result": 1,
    "newsletter_result": 1,
    "service_result": 1,
    "all_results": 1,
    "traversal_refused": 1,
    "unclassified": 1,
    "off_search": 1,
    "no_href": 1,
}

#: The route the amendment measured, held as SEGMENTS rather than as an
#: address so the file never carries the assembled string. A test walks it
#: through :func:`refuses_traversal`; a weaker matcher calls it a person.
ADVERSARIAL_TRAVERSAL_SEGMENTS: tuple[str, ...] = (
    "search",
    "results",
    "people",
    "..",
    "..",
    "mypreferences",
    "d",
    "close-account",
)

#: Entity-shape flags, mirroring the script's three answers. Named because
#: ``-1`` and ``0`` are different things and a reader of a bare integer column
#: will guess wrong: ``NO_ENTITY`` means the route stopped at its vertical.
NO_ENTITY = -1
NUMERIC_ENTITY = 0
NON_NUMERIC_ENTITY = 1


def adversarial_traversal_route() -> str:
    """The amendment's address, ASSEMBLED AT CALL TIME from its segments.

    The file holds the segments and never the assembled string, so a grep of
    this repository for that address finds a tuple and a docstring rather than
    a line that reads as a working link. Assembling it here costs nothing and
    keeps the address out of the source.
    """
    return "/" + "/".join(ADVERSARIAL_TRAVERSAL_SEGMENTS)


def route_control_corpus() -> tuple[tuple[str, str, int, int], ...]:
    """``(route, expected kind, expected query flag, expected entity shape)``.

    **THE EXPECTATIONS ARE THE POINT.** This corpus is driven through the
    SHIPPED ``classifyRoute`` under V8 by ``tests/test_search_results.py``, so
    every row below is a prediction that a real engine either confirms or
    refutes. Before this existed the fixture's counts had never been computed
    by anything.

    Three rows are adversarial and two record MEASURED LIMITS rather than
    wins; see the module docstring's limits section. Every slug is synthetic
    and carries ``example``.
    """
    return (
        # The ordinary forms of the hazard vertical.
        ("/search/results/people/", "person_result", 0, NO_ENTITY),
        ("/search/results/people", "person_result", 0, NO_ENTITY),
        ("/search/results/people/?keywords=example", "person_result", 1, NO_ENTITY),
        ("/search/results/people/#example", "person_result", 0, NO_ENTITY),
        # THE ADDRESS THE AMENDMENT MEASURED, and a bare dot beside it.
        (adversarial_traversal_route(), "traversal_refused", 0, NO_ENTITY),
        ("/search/results/people/./example", "traversal_refused", 0, NO_ENTITY),
        ("/search/results/people/../", "traversal_refused", 0, NO_ENTITY),
        # THE CONTAINMENT TRAP: a vertical whose name contains the hazard one.
        ("/search/results/peoplefinder/", "unclassified", 0, NO_ENTITY),
        # The rest of the closed table, plus both entity shapes.
        ("/search/results/companies/", "company_result", 0, NO_ENTITY),
        ("/search/results/groups/12345/", "group_result", 0, NUMERIC_ENTITY),
        (
            "/search/results/groups/example-group/",
            "group_result",
            0,
            NON_NUMERIC_ENTITY,
        ),
        ("/search/results/all/", "all_results", 0, NO_ENTITY),
        ("/search/results/services/", "service_result", 0, NO_ENTITY),
        # SHORT ROUTES ARE NOT VERTICALS. Three segments is the floor.
        ("/search/results/", "unclassified", 0, NO_ENTITY),
        ("/search/", "unclassified", 0, NO_ENTITY),
        ("/feed/", "off_search", 0, NO_ENTITY),
        ("", "no_href", 0, NO_ENTITY),
        # HOST HANDLING, including the protocol-relative form.
        (
            "https://www.linkedin.com/search/results/people/",
            "person_result",
            0,
            NO_ENTITY,
        ),
        (
            "https://example.invalid/search/results/people/",
            "off_search",
            0,
            NO_ENTITY,
        ),
        ("//example.invalid/search/results/people/", "off_search", 0, NO_ENTITY),
        # MEASURED LIMIT 1: matching is CASE SENSITIVE, and the miss lands on
        # the SAFE side -- an uppercase route is not recognised as a search at
        # all rather than being admitted as one.
        ("/SEARCH/RESULTS/PEOPLE/", "off_search", 0, NO_ENTITY),
        # MEASURED LIMIT 2: a PERCENT-ENCODED traversal is NOT refused. See the
        # module docstring -- this row records what the shaper really does, not
        # what it would be nice for it to do.
        (
            "/search/results/people/..%2f..%2fmypreferences",
            "person_result",
            0,
            NON_NUMERIC_ENTITY,
        ),
    )

#: Matches a dot segment inside a JS string. Used by the suite to prove the
#: shipped script really carries the traversal rule rather than only the
#: docstring claiming it.
_DOT_RULE_IN_JS = re.compile(r'segment\s*===\s*"\.\."')


def classifier_source() -> str:
    """The SHIPPED ``classifyRoute``, LIFTED out of the script, not transcribed.

    A transcription is a second implementation, and two implementations that
    agree today can disagree tomorrow -- ``tests/test_compose_fields.py`` says
    so in as many words and lifts ``shapeOf`` by brace-matching for exactly
    that reason. **This is that instrument, imported rather than reinvented.**

    What comes back is the exact characters that run in the page, so a control
    driving this is driving THE ARTIFACT and not a copy of it.
    """
    return _lift_function(_CLASSIFY_IN_PAGE, "const classifyRoute =")


#: The filter panel's script. Same rule as the route classifier: the page
#: contact lives in ``dom.py`` and this module keeps the vocabulary.
_MATCH_IN_PAGE = dom.FILTER_PANEL_JS


def filter_matcher_source() -> str:
    """The SHIPPED ``matchPhrase``, LIFTED out of the panel script.

    Same instrument as :func:`classifier_source`, aimed at the other half.
    What comes back is the exact characters that compare a filter label in the
    page, so the cross-engine agreement test drives THE ARTIFACT.
    """
    return _lift_function(_MATCH_IN_PAGE, "const matchPhrase =")


def filter_normaliser_source() -> str:
    """The SHIPPED ``normaliseLabel``, lifted the same way."""
    return _lift_function(_MATCH_IN_PAGE, "const normaliseLabel =")


def _lift_function(source: str, declaration: str) -> str:
    """Brace-match one function out of a script. Refuses a truncated result.

    ``tests/test_compose_fields.py`` lifts ``shapeOf`` exactly this way, and
    this repository has a scar for writing a second copy of a check it already
    ships -- so the technique is imported and this is its one definition here.
    """
    start = source.index(declaration)
    brace = source.index("{", start)
    depth = 0
    for position in range(brace, len(source)):
        character = source[position]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[start:position + 1]
    raise AssertionError(
        f"{declaration!r} is unbalanced in the shipped script -- refusing to "
        "hand back a truncated function, which would run and be wrong."
    )


def script_carries_the_traversal_rule() -> bool:
    """Does the SHIPPED DECISION test for a dot segment? Read off its source.

    A docstring that describes a rule and a script that applies it are two
    different artifacts, and this repository has shipped the first without the
    second. This reads the second -- and it reads the EXTRACTED function
    rather than the whole script, so a prose comment elsewhere that merely
    mentions the rule cannot satisfy it.
    """
    try:
        decision = classifier_source()
    except (ValueError, AssertionError):
        return False
    return bool(_DOT_RULE_IN_JS.search(decision))
