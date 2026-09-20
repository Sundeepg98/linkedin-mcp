"""Job-search arguments that need a test handle of their own.

Two of them live here, and the reason is the same in both cases: each turns a
caller's string into a search, each can be WRONG in a way that returns a
plausible page rather than an error, and neither can be aimed at its known-bad
input while it lives inside ``linkedin_search_jobs``.

* **The company filter** -- census row ``J 10``. Its refusal must describe the
  SHAPE of a rejected value and never quote it, because the likeliest wrong
  value is a company slug and a slug is an organisation's name. That is the
  first half of this file.
* **Multiple simultaneous locations** -- census row ``J 151``. Both url
  spellings LinkedIn might have accepted were MEASURED WRONG, so the capability
  is several loads rather than one parameter, and the merge that follows is
  pure logic with no browser in it. That is the second half, from
  :data:`LOCATIONS_SEPARATOR` down.

``J 10`` -- filter a job search by company -- was filed against
``COMPANY-ID-RESOLVER`` on the reasoning that ``f_C`` needs a numeric Page id
while a posting only yields a slug. **Both halves of that blocker are now
built** and the row is still GAP, because nothing joined them:

* ``/jobs/search/?f_C=<numeric id>`` has been on the read allowlist since the
  first commit -- ``f_C`` is one more query key on a root this server has always
  opened. Measured, not assumed: ``readonly.is_read_url`` returns True for it at
  29 patterns.
* ``shape.company_id_from_insight_cards`` resolves the id, and
  ``linkedin_job_detail`` already returns it as a VERDICT rather than a bare
  value -- state ``resolved`` only when exactly one card agrees.

So this module is the wire, and it is deliberately a separate file: ``server.py``
has been contended by a dozen waves all day, and two documented incidents this
afternoon swept a neighbour's lines into a commit inside
``linkedin_search_jobs`` specifically.

## WHY THE REFUSAL NAMES A SHAPE AND NEVER THE VALUE

This package's standing rule is that a refusal must report **what it SAW**, not
only what it failed to match -- three rounds were lost to "zero matched" before
that was written down.

**This function is the exception that proves it needs care, and the reason is
the failure mode itself.** The overwhelmingly likely wrong value for ``f_C`` is
a company SLUG, because that is exactly what a posting hands you and exactly
what the blocker was named for. A slug is a third-party organisation's name. So
the obvious, rule-following implementation --

    f"company_id must be digits, got {company_id!r}"

-- publishes a third-party name verbatim into a tool result, every time a caller
makes the single most probable mistake. **A rule about naming what you saw and a
rule about never emitting an identifier collide here, and the collision is won
by the identity rule**, which is the one this repository treats as absolute.

The refusal therefore reports the SHAPE: how many characters, and which
character classes were present. That is enough for a caller to know why
``acme-corp`` was refused (it has letters and a hyphen) without this process
ever putting ``acme-corp`` in an output. ``tests/test_company_job_filter.py``
asserts the value does not survive, using an input whose refusal would otherwise
carry it.

**A digits-only value IS echoed**, and that is a deliberate, narrow exception:
once the value is known to be all digits it is a LinkedIn Page id and nothing
else -- it cannot be a name, because a name cannot be digits. The one case that
can carry a name is the one case that is refused.
"""

from __future__ import annotations

from typing import Any

#: LinkedIn's company filter key on ``/jobs/search/``. Named once so the
#: parameter name and the test that pins it cannot drift apart silently.
COMPANY_FILTER_KEY = "f_C"

#: A Page id is digits. The longest real id seen in this repository's fixtures
#: is seven characters; the ceiling here is deliberately loose because an
#: arbitrary cap would refuse a valid id on a guess, and the harm being guarded
#: against is a NAME reaching an output, which a length cap does not address.
_MAX_ID_LEN = 20


def describe_shape(value: str) -> str:
    """Describe a string by its character classes and length. Never its content.

    Factored OUT of the refusal that consumes it, so it has a handle and can be
    aimed at a known-bad sample directly -- logic living inside an ``assert``
    can never be tested against the input it was written for.
    """

    text = str(value or "")
    classes: list[str] = []
    if any(character.isdigit() for character in text):
        classes.append("digits")
    if any(character.isalpha() for character in text):
        classes.append("letters")
    if any(character in "-_" for character in text):
        classes.append("hyphen-or-underscore")
    if any(character.isspace() for character in text):
        classes.append("whitespace")
    if any(
        not character.isalnum() and character not in "-_" and not character.isspace()
        for character in text
    ):
        classes.append("punctuation")
    if not classes:
        classes.append("empty")
    return f"{len(text)} characters, containing {' + '.join(classes)}"


def company_filter_param(company_id: str) -> dict[str, Any]:
    """Turn a company id into an ``f_C`` query parameter, or refuse it.

    Returns a VERDICT and not a bare value, matching the shape
    ``linkedin_job_detail`` already returns for ``company_id`` -- three states,
    each of which a caller must handle differently:

    ``absent``
        nothing was supplied. Not an error: the filter is optional, and this is
        how "no company filter" arrives. ``param`` is None.
    ``resolved``
        the value is a Page id and ``param`` is the pair to append.
    ``refused``
        the value cannot be a Page id. ``param`` is None and ``why`` describes
        the SHAPE that was rejected, never the value -- see the module
        docstring for why that inverts this package's usual refusal rule.
    """

    text = str(company_id or "").strip()

    if not text:
        return {
            "state": "absent",
            "param": None,
            "why": "no company_id was supplied, so no company filter is applied",
        }

    if not text.isdigit():
        return {
            "state": "refused",
            "param": None,
            "why": (
                "company_id must be a numeric LinkedIn Page id; the value "
                f"supplied is {describe_shape(text)}. A company SLUG is not a "
                "Page id -- resolve one with linkedin_job_detail, whose "
                "company_id verdict reads 'resolved' only when exactly one "
                "insight card agrees. The value is described rather than "
                "quoted because a non-numeric value here is most often an "
                "organisation's name."
            ),
        }

    if len(text) > _MAX_ID_LEN:
        return {
            "state": "refused",
            "param": None,
            "why": (
                f"company_id is {len(text)} digits, longer than the {_MAX_ID_LEN} "
                "this accepts; no LinkedIn Page id of that length is known here"
            ),
        }

    return {
        "state": "resolved",
        "param": (COMPANY_FILTER_KEY, text),
        "why": f"a {len(text)}-digit Page id, appended as {COMPANY_FILTER_KEY}",
    }


# ---------------------------------------------------------------------------
# MULTIPLE SIMULTANEOUS LOCATIONS -- census row ``J 151``.
#
# THE ROW IS NOT PARAMETER WORK, AND THAT IS A MEASUREMENT RATHER THAN AN
# OPINION. ``linkedin_search_jobs``'s own docstring carries the full reading
# taken on 2026-09-05: with city A alone returning seven postings and city B
# alone seven, sharing two --
#
#     location=A%2C%20B      KEPT by LinkedIn, returns seven postings of
#                            which ZERO are A-only and ZERO are B-only. It
#                            geocodes somewhere neither search reaches.
#     location=A&location=B  STRIPPED. LinkedIn serves the LAST city alone,
#                            and a caller who wrote A first never learns it.
#
# Both spellings are WRONG rather than unmeasured, so neither ships, and the
# same docstring names the honest route: "Two searches, one per city".
#
# THIS IS THAT ROUTE, MOVED INSIDE THE TOOL. One load per place, merged and
# de-duplicated here. What it buys is a single call and a single shortlist
# spanning several cities. What it does NOT buy is LinkedIn's own ranking
# ACROSS those cities, because no request is ever made that names two places.
# That distinction is stated in the tool's docstring rather than papered over:
# a merged pair of per-city windows is a different object from one cross-city
# window, and a caller comparing this against LinkedIn's web ui has to know
# which of the two they are holding.
#
# THE SEPARATOR IS A SEMICOLON, AND THAT IS THE WHOLE OF THE SAFETY ARGUMENT.
# A comma is part of a location's OWN spelling -- LinkedIn's typeahead writes
# places as "City, Region, Country" -- so a comma-separated list of locations
# cannot be parsed back into the places that went into it. Both readings fail
# silently and in the direction already measured: split a qualified place on
# its commas and you search three places that are not it; DO NOT split it and
# a caller who comma-separated two cities hands LinkedIn the comma-joined
# string that was measured to geocode somewhere else. No parse is right for
# both, so the ambiguous input is REFUSED rather than guessed at.
# ---------------------------------------------------------------------------

#: What separates one location from the next in the ``locations`` argument.
#: Named once so the parser, the refusal text and the test that pins it cannot
#: drift apart. A semicolon does not occur in LinkedIn's own spelling of a
#: place, which is the property a comma lacks.
LOCATIONS_SEPARATOR = ";"

#: The ceiling on how many places one call may search.
#:
#: **THIS IS A BUDGET AND NOT A MEASUREMENT.** Nothing here has measured a
#: LinkedIn limit on locations; what is bounded is THIS SERVER's cost, because
#: every place is one more page load, one more wait, and one more row in the
#: operator's own recent-search history. Five is the point at which a caller
#: should be asked to mean it. A future reading of an actual LinkedIn limit
#: would replace this number and this note together.
MAX_LOCATIONS = 5


def split_locations(text: str) -> list[str]:
    """Split the ``locations`` argument into places, keeping commas inside them.

    Factored out with a handle of its own for the same reason
    :func:`describe_shape` has one: the interesting input here is a QUALIFIED
    place name -- "City, Region, Country" -- and a splitter that can only be
    reached through the refusal that consumes it can never be aimed at that
    input directly.

    Empty entries are dropped, so a trailing separator or a doubled one is
    benign rather than an error. What is never dropped is a comma: every comma
    survives inside the entry that carried it.
    """

    return [
        part.strip()
        for part in str(text or "").split(LOCATIONS_SEPARATOR)
        if part.strip()
    ]


def comma_count(text: str) -> int:
    """How many commas an entry holds. A count, and never the text around them."""

    return str(text or "").count(",")


def locations_plan(location: str, locations: str) -> dict[str, Any]:
    """Decide which places one search call will visit, or refuse to guess.

    A VERDICT rather than a bare list, matching :func:`company_filter_param`
    beside it. Three states:

    ``single``
        the ordinary case. ``places`` holds exactly one entry, which is the
        ``location`` argument as given and may be the empty string, meaning
        LinkedIn's default. ONE page load, and the url is the one this tool
        has always built.
    ``fanout``
        two or more places. ``places`` holds them in the caller's order with
        duplicates collapsed; the tool loads one search per entry.
    ``refused``
        the arguments cannot be turned into a set of places without guessing.
        ``places`` is empty and ``why`` says what was seen.

    **EVERY REFUSAL BELOW REPORTS COUNTS AND NEVER THE VALUE.** A place name a
    caller typed is not a third party's identity the way a company slug is --
    see this module's first section -- but nothing here NEEDS the text in order
    to explain itself, and a refusal that quotes its input is one edit away
    from quoting an input that should never have been echoed. Counts say
    everything a caller needs in order to act: how many entries were found, and
    how many commas sat inside the one that was ambiguous.
    """

    single = str(location or "").strip()
    raw = str(locations or "")

    if not raw.strip():
        return {
            "state": "single",
            "places": [single],
            "why": (
                "no locations list was supplied, so this is one search at the "
                "location given"
            ),
        }

    if single:
        return {
            "state": "refused",
            "places": [],
            "why": (
                "location and locations were BOTH supplied and they cannot "
                "both be honoured -- one asks for a single search and the "
                "other for several. Pass locations alone for a multi-place "
                "search, or location alone for one place."
            ),
        }

    places = split_locations(raw)

    if not places:
        return {
            "state": "refused",
            "places": [],
            "why": (
                "locations held no place names -- separators and whitespace "
                f"only. Separate places with {LOCATIONS_SEPARATOR!r}, as in "
                f"'City A, Region, Country{LOCATIONS_SEPARATOR} City B, "
                "Region, Country'."
            ),
        }

    if len(places) == 1:
        # THE COMMA TRAP, REFUSED RATHER THAN GUESSED AT. One entry means
        # either a caller who wanted one place and should say so with
        # ``location``, or a caller who separated two cities with a COMMA --
        # and that second reading is the failure measured on 2026-09-05, where
        # LinkedIn keeps the comma-joined string and serves a place that is
        # neither city. Both readings are cleared by the same one-line change
        # on the caller's side, so refusing costs nothing, and guessing costs
        # a shortlist built on a city nobody asked for.
        return {
            "state": "refused",
            "places": [],
            "why": (
                "locations named ONE place, and locations means several. The "
                f"single entry is {describe_shape(places[0])} and holds "
                f"{comma_count(places[0])} comma(s). If you meant one place, "
                "pass it as location instead. If you meant several, separate "
                f"them with {LOCATIONS_SEPARATOR!r} and never with a comma: a "
                "comma is part of a place's own spelling, and LinkedIn was "
                "measured on 2026-09-05 to KEEP a comma-joined pair of cities "
                "and return postings from neither of them."
            ),
        }

    # Duplicates collapse instead of costing a load. Compared case-folded and
    # whitespace-collapsed, because "city a" and "City  A" are one place and
    # would otherwise buy the same seven postings twice.
    kept: list[str] = []
    seen: set[str] = set()
    for place in places:
        key = " ".join(place.casefold().split())
        if key in seen:
            continue
        seen.add(key)
        kept.append(place)

    if len(kept) > MAX_LOCATIONS:
        return {
            "state": "refused",
            "places": [],
            "why": (
                f"locations named {len(kept)} distinct places and this tool "
                f"loads at most {MAX_LOCATIONS} per call, one page load each. "
                "That ceiling is a cost budget on this server, not a LinkedIn "
                "limit anyone here has measured. Run the extras as a second "
                "call."
            ),
        }

    return {
        "state": "fanout",
        "places": kept,
        "why": (
            f"{len(kept)} places, {len(places) - len(kept)} duplicate(s) "
            f"collapsed; one page load each, {len(kept)} loads in total"
        ),
    }


def merge_location_reads(
    reads: list[tuple[str, dict[str, Any]]], *, limit: int
) -> dict[str, Any]:
    """Merge one envelope per place into one envelope, and say what each gave.

    ``reads`` is ``(place, envelope)`` in the order the places were loaded, and
    each envelope is whatever ``shape.envelope`` produced for that load.

    **THE MERGE IS ROUND-ROBIN, AND THAT IS THE ONE DECISION IN THIS FUNCTION
    WORTH ARGUING ABOUT.** Concatenating the places is the obvious merge and it
    is silently wrong at this tool's measured numbers: the search window was
    measured at SEVEN postings per load on 2026-09-05, so three places is up to
    21 rows against a default ``limit`` of 25 and five places is up to 35. A
    concatenated list trimmed to 25 would drop the LAST places entirely, and a
    caller who named five cities would receive four -- with ``capped`` true and
    nothing at all saying which city vanished. Taking one row from each place
    in turn makes the trim fall evenly, and every place that returned anything
    is represented in whatever survives. Order WITHIN a place is untouched, so
    LinkedIn's own ranking for that city is preserved exactly.

    **DE-DUPLICATION IS BY ``job_id`` AND ONLY BY ``job_id``.** A posting can
    legitimately answer two cities -- a remote role is the common case -- and
    returning it twice would inflate the count. A row that carries NO job_id
    cannot be compared against anything and is kept as it stands; ``unkeyed``
    on that place's entry counts them, so a caller can see that the de-dupe had
    rows it could not speak about rather than assuming it had none.

    Every row gains ``found_in``: the place whose search returned it FIRST. It
    is the provenance the row's own ``location`` field cannot supply, because
    that field is LinkedIn's spelling of where the JOB is -- frequently
    "Remote" -- and not a statement about which query found it.
    """

    per_place: list[list[dict[str, Any]]] = []
    searches: list[dict[str, Any]] = []
    seen: set[str] = set()
    dropped = 0

    for place, envelope in reads:
        rows = list(envelope.get("results") or [])
        mine: list[dict[str, Any]] = []
        repeats = 0
        unkeyed = 0
        for row in rows:
            job_id = row.get("job_id")
            if job_id:
                if job_id in seen:
                    repeats += 1
                    continue
                seen.add(job_id)
            else:
                unkeyed += 1
            mine.append({**row, "found_in": place})
        per_place.append(mine)
        dropped += int(envelope.get("unparsed_rows") or 0)
        searches.append(
            {
                "location": place,
                "page_had": int(envelope.get("page_had") or 0),
                "kept": len(mine),
                "already_seen": repeats,
                "unkeyed": unkeyed,
                "source_url": envelope.get("source_url"),
            }
        )

    merged: list[dict[str, Any]] = []
    for index in range(max((len(rows) for rows in per_place), default=0)):
        for rows in per_place:
            if index < len(rows):
                merged.append(rows[index])

    trimmed = merged[:limit]
    kept_by_place: dict[str, int] = {}
    for row in trimmed:
        kept_by_place[row["found_in"]] = kept_by_place.get(row["found_in"], 0) + 1
    for entry in searches:
        entry["in_results"] = kept_by_place.get(entry["location"], 0)

    return {
        "count": len(trimmed),
        "page_had": sum(entry["page_had"] for entry in searches),
        "capped": len(merged) > limit,
        "limit": limit,
        "pages_loaded": len(reads),
        # ONE url where the other tools carry one, and it is the FIRST search's
        # rather than a joined string, because a caller pasting source_url into
        # a browser must land on a page this server actually loaded. Every url
        # is in ``searches``; none of them is hidden.
        "source_url": searches[0]["source_url"] if searches else None,
        "searches": searches,
        # PRESENT ONLY WHEN NON-ZERO, exactly as ``shape.envelope`` emits it.
        # A key that is always there with a 0 in it reads as "nothing was
        # dropped anywhere"; a key that appears only when something was dropped
        # is the signal the rest of this package's results are read with.
        **({"unparsed_rows": dropped} if dropped else {}),
        "results": trimmed,
    }
