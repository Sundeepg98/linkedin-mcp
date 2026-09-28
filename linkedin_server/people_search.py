"""Compose a PEOPLE SEARCH from a tool's arguments. The one place a keyword or a
facet becomes part of an address.

## WHAT CHANGED, AND WHO DECIDED IT

``linkedin_people_search_shape`` shipped on 2026-09-20 taking NO parameter, on
the argument that a search query is where a person's name is typed. Two
delegated calls registered on 2026-09-23 decided the question that argument
held open:

* ``D1-SEARCH-AS-READS`` -- search keywords and LinkedIn-written facets are
  permitted as READS. Values come from the tool's arguments ONLY, never from
  page content, and the navigation-derivation guard still applies.
* ``OTHER-MEMBER-IDS-AS-READS`` -- another member's id in a search facet
  (``connectionOf``) is permitted as a read when it comes from the tool's
  arguments, never from page content, and is never stored in a tracked file.

This module is those two calls turned into code, and nothing wider. Census
rows (``_audit/_census/network.md``): ``N 79`` and ``N 194`` (a keyword),
``N 84`` and ``N 87`` (current and past company), ``N 94`` (more than one
location in one search), ``N 85``, ``N 172`` and ``N 30`` (the connections of
a member), and ``N 31`` (the connections he shares with a member: the member's
connections narrowed by LinkedIn's ``network`` facet to his own first degree).

## IT TOUCHES NO PAGE, AND THAT IS THE DERIVATION PROOF

No function here takes a page, imports the browser or ``dom``, or navigates.
:func:`compose` is a pure function of the tool's own arguments: nothing a page
drew can reach the address it returns, because nothing a page drew can reach
this module at all. ``tests/test_people_search_readers.py`` asserts that on the
module's AST, and the repository's navigation-derivation guard
(``tests/test_navigation_is_never_derived.py``) covers the tool that calls it.

The one function here that is HANDED a site-chosen value is
:func:`landing_verdict`, and it only COMPARES it: it takes the address the
browser settled on and the address this module composed, and returns literals
from a closed alphabet. The landing never leaves it.

## THE SPELLINGS, AND THE EVIDENCE CLASS OF EACH

Read off every LinkedIn-authored people-search href in the 25 raw captures and
the tracked fixtures, by parameter NAME and value SHAPE only
(``_audit/2026-09-24-lane-s-people-search.md`` section 2), and, for the last
two, off a first-degree profile's topcard (2026-09-28):

    keywords        LinkedIn-authored, space written '+'           MEASURED
    currentCompany  LinkedIn-authored as a JSON LIST (company root) MEASURED
                    and bare (profile views, a job page)
    pastCompany     LinkedIn-authored BARE only (a job page)        list DERIVED
    geoUrn          LinkedIn-authored BARE only (profile views)     list DERIVED
    connectionOf    LinkedIn-authored as a JSON LIST, encoded       MEASURED
                    (a first-degree profile's topcard, links 2, 3)
    network         LinkedIn-authored as a JSON LIST: ["F"]         MEASURED
                    encoded (links 2, 3), ["F","S"] raw (link 1);
                    also alone on the connections page, its value
                    shape unread there

``connectionOf`` read ``never LinkedIn-authored; named by a test`` -- DERIVED --
from 2026-09-24 until the live lane's first-degree capture was read for its
shapes on 2026-09-28 (``tests/fixtures/live2/first_degree_profile.html``: every
value an ``x``; the value shapes lane L5 measured off the capture's skeleton).
Links 2 and 3 are LinkedIn's shared-connections links, and they write
``network`` then ``connectionOf``, each a percent-encoded list -- exactly what
:func:`compose` sends for ``connections_of`` with ``network``.

LinkedIn's FACETED grammar on this surface is JSON -- a list per facet
(``currentCompany``, ``activelyHiringForJobTitles``) or a JSON string
(``activelyHiring``). Every facet here is sent in that grammar, one code path,
and the list form is the only one that can carry more than one value, which is
what ``N 94`` asks for. **A two-member list is on record for one facet only**,
``network``'s ``["F","S"]`` on link 1, written raw; for every other facet it is
the same grammar with a second member, and it is DERIVED. The tool reports
per argument what LinkedIn did with each value in the address it settled on
(:func:`landing_verdict`), so a spelling LinkedIn drops or rewrites is a
visible literal on the first fire rather than a silently unfiltered search --
the failure ``linkedin_search_jobs`` measured twice for its own multi-location
spellings.

``origin`` is not sent. LinkedIn wrote a keywords-only href with no ``origin``
(the badges capture), so it is not required, and every value on record names a
page this module is not.

## NOTHING COMES BACK

No keyword, organisation id, geo id or member token is ever returned by this
module or published by the tool: the payload carries COUNTS of what was applied
and a closed-alphabet verdict per argument. A refusal describes the SHAPE of a
rejected value with ``jobfilter.describe_shape`` and never quotes it -- the
likeliest wrong value for an organisation is its slug, for a member their
profile slug, and a slug is a name.

## A KEYWORD THE BOUNDARY REFUSES GETS THE BOUNDARY'S OWN ANSWER

The read boundary scans the WHOLE lowered address, query included, for its
forbidden substrings, and 8 of 11 ordinary keywords trip one
(``_audit/2026-09-19-search-admission-preconditions.md`` B.4: ``password``,
``settings``, ``invitation`` ...). That audit hands the tool a requirement: decide
in advance what happens, WITHOUT narrowing the denylist. So
:func:`boundary_verdict` asks the door -- ``readonly.is_read_url``, the
non-raising form ``press.py`` already uses as a pre-check -- before any
session opens, and a refusal comes back structured: the kind ``BROWSER.goto``
would raise, the boundary's OWN forbidden substrings the address carries (read
off its tuple, so only this package's constants can appear), the argument
that carried them, and a sentence written for a person who was searching, not
"not a read surface". Nothing is loaded.

``readonly.assert_read_url`` IS NOT CALLED HERE, and that is a measurement's
consequence rather than a style: its call sites are pinned to the two
navigation paths by ``tests/test_api_call_sites.py``, which caught the first
version of this module calling it (the lane's impact gate, 2026-09-24).
``BROWSER.goto`` still calls it on every address this admits.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit

from linkedin_server import company_page, jobfilter, readonly, search_results

#: The address every composition starts from, and the WHOLE address when no
#: argument is given -- so the no-argument call opens exactly what
#: ``linkedin_people_search_shape`` opened before it took arguments.
BASE_URL = search_results.PEOPLE_SEARCH_URL

_HOST = "www.linkedin.com"

#: The vertical's closed path segments, compared by EQUALITY -- the amended
#: condition 2 of the search admission, restated for the landing check.
_PEOPLE_SEGMENTS: tuple[str, ...] = ("search", "results", "people")

#: The keyword's query key. LinkedIn-authored on 21 hrefs across the captures.
KEYWORDS_KEY = "keywords"

#: What a facet value is, decided here and never read off a page.
ORGANISATION_ID = "organisation_id"
GEO_ID = "geo_id"
MEMBER_TOKEN = "member_token"
NETWORK_DEGREE = "network_degree"

#: LINKEDIN'S ``network`` FACET, AS THE CAPTURE WRITES IT (census ``N 31``,
#: 2026-09-28). Its values are degrees of HIS OWN network, in LinkedIn's
#: letters: ``F`` his first degree, ``S`` his second. CLOSED TO THE TWO THE
#: CAPTURE HOLDS, in the order link 1 lists them -- LinkedIn's letter for a
#: third degree is on record nowhere here, so it is refused, not guessed.
NETWORK_DEGREES: tuple[str, ...] = ("F", "S")

#: ``(tool argument, LinkedIn query key, value kind, most values per call)``.
#: ORDER IS THE ADDRESS ORDER: keywords first, then these, as listed.
#:
#: THE MEMBER FACET TAKES ONE VALUE, deliberately narrower than the others:
#: the rows it serves ask about ONE member's connections, and a call that
#: named several other people at once would carry more third-party ids than
#: any row needs.
#:
#: ``network`` SITS BEFORE ``connectionOf`` because LinkedIn's own
#: shared-connections links write them in that order (links 2 and 3 of a
#: first-degree profile's topcard), and it is only ever sent beside a member
#: this server was handed: see :func:`compose`.
FACETS: tuple[tuple[str, str, str, int], ...] = (
    ("current_company_ids", "currentCompany", ORGANISATION_ID, 5),
    ("past_company_ids", "pastCompany", ORGANISATION_ID, 5),
    ("location_ids", "geoUrn", GEO_ID, 5),
    ("network", "network", NETWORK_DEGREE, len(NETWORK_DEGREES)),
    ("connections_of", "connectionOf", MEMBER_TOKEN, 1),
)

#: Every tool argument this module reads, in address order, with its key.
ARGUMENT_KEYS: tuple[tuple[str, str], ...] = (("keywords", KEYWORDS_KEY),) + tuple(
    (argument, key) for argument, key, _kind, _most in FACETS
)

#: THE KEYWORD'S LENGTH CEILING IS A BUDGET, NOT A MEASUREMENT. Nothing here
#: measured LinkedIn's own limit. A caller's search that runs past this many
#: characters is refused rather than truncated, because a truncated search is
#: a different search that looks like the one asked for.
MAX_KEYWORD_CHARS = 200

#: What separates ids inside one argument. An id is a run of digits or a
#: member token, and neither can hold a comma, so a comma is unambiguous here
#: -- unlike ``linkedin_search_jobs(locations=...)``, whose members are place
#: NAMES that carry commas of their own and are therefore split on ';'.
ID_SEPARATOR = ","

#: THE TEN ASCII DIGITS, WRITTEN OUT, for the geo id rule -- restated from
#: ``company_page`` (which organisation ids go through, called rather than
#: copied) because no shipped validator exists for a geo id. ``str.isdigit()``
#: is true of several other scripts' digits and ``\\d`` of every Unicode decimal
#: digit; the read allowlist spells its digit segments ``[0-9]`` for the same
#: reason.
_ASCII_DIGITS = frozenset("0123456789")

#: The same bound ``company_page`` holds an organisation id to.
MAX_ID_DIGITS = company_page.MAX_IDENTIFIER_DIGITS

#: THE MEMBER TOKEN'S SHAPE, and it is the repository's recorded one rather
#: than a new guess: ``tests/test_no_committed_identity.MEMBER_TOKEN_SHAPE``
#: recognises a member token as ``ACoAA`` followed by ten or more of
#: ``[A-Za-z0-9_-]``, and the read boundary's compose-with-recipient pattern
#: bounds a recipient id at 64 characters of the same class. A profile SLUG --
#: which is a NAME -- does not open ``ACoAA``, so it is refused by shape.
_MEMBER_TOKEN = re.compile(r"ACoAA[A-Za-z0-9_-]{10,59}")

#: The closed alphabet :func:`landing_verdict` may return per argument.
#:
#:     verbatim          the settled address carries the key with exactly the
#:                       value this module sent
#:     same_values       the key is there, spelled differently, carrying the
#:                       same values (a list LinkedIn re-serialised, a keyword
#:                       re-spaced or re-cased)
#:     different_values  the key is there and its values are not the ones sent
#:                       -- a FINDING, never a pass
#:     absent            the settled address does not carry the key at all
#:     unreadable        the settled address could not be parsed
#:
#: NONE OF THEM SAYS THE FILTER WAS APPLIED TO THE RESULTS. Kept is a fact
#: about the address LinkedIn settled on, not about which people it listed.
KEPT_VERDICTS: tuple[str, ...] = (
    "verbatim",
    "same_values",
    "different_values",
    "absent",
    "unreadable",
)

#: The closed alphabet of :func:`boundary_verdict`'s ``boundary_refusal``.
#:
#:     FORBIDDEN     the address carries at least one of the boundary's own
#:                   forbidden substrings, and each is listed
#:     NOT-ADMITTED  the boundary refuses it and its tuple explains nothing --
#:                   for an address this module composed, a defect in the
#:                   composition, never a guess at a reason
BOUNDARY_REFUSALS: tuple[str, ...] = ("FORBIDDEN", "NOT-ADMITTED")


def _refused(argument: str, refused: str, value: str, why: str) -> dict[str, Any]:
    """A refusal that names the ARGUMENT and describes the value's SHAPE."""
    return {
        "built": False,
        "argument": argument,
        "refused": refused,
        "saw": jobfilter.describe_shape(value),
        "why": why,
    }


def _one_id(argument: str, kind: str, text: str) -> dict[str, Any]:
    """One value of one facet: ``{"ok": True, "value": v}`` or a refusal.

    Never raises, and never puts the value in anything but ``value`` on the
    accepted path -- a rejected value is described, not quoted.
    """
    if kind == ORGANISATION_ID:
        verdict = company_page.company_identifier(text)
        if verdict.get("identified"):
            return {"ok": True, "value": str(verdict["identifier"])}
        return _refused(
            argument,
            str(verdict.get("refused") or "identifier_refused"),
            text,
            "each organisation must be LinkedIn's NUMERIC id -- the digits "
            "linkedin_job_detail returns as company_id, or the ones "
            "linkedin_followed_companies reads off Manage Pages -- never a "
            "company name or slug, because a slug is a name. "
            + str(verdict.get("why") or ""),
        )
    if kind == GEO_ID:
        if not text or not set(text) <= _ASCII_DIGITS:
            return _refused(
                argument,
                "identifier_is_not_numeric",
                text,
                "each location must be LinkedIn's NUMERIC geo id (the digits "
                "LinkedIn writes under geoUrn), never a place name: a place "
                "name is a search of its own and LinkedIn geocodes it where "
                "it likes. The ten ASCII digits only; str.isdigit() is true "
                "of other scripts' digits as well.",
            )
        if len(text) > MAX_ID_DIGITS:
            return _refused(
                argument,
                "identifier_too_long",
                text,
                f"a digit run longer than {MAX_ID_DIGITS} characters is not a "
                "LinkedIn geo id, and an unbounded run on caller-shaped input "
                "is a cost nobody chose.",
            )
        return {"ok": True, "value": text}
    if kind == MEMBER_TOKEN:
        if _MEMBER_TOKEN.fullmatch(text):
            return {"ok": True, "value": text}
        return _refused(
            argument,
            "not_a_member_token",
            text,
            "connections_of takes LinkedIn's opaque MEMBER TOKEN -- the value "
            "linkedin_connections returns as recipient_id, which opens ACoAA "
            "-- and never a profile address, a slug or a name: a slug is a "
            "name, and OTHER-MEMBER-IDS-AS-READS permits an id, not a name. "
            "The value is described rather than quoted.",
        )
    if kind == NETWORK_DEGREE:
        if text in NETWORK_DEGREES:
            return {"ok": True, "value": text}
        return _refused(
            argument,
            "not_a_network_degree",
            text,
            "network takes LinkedIn's own letters for a degree of YOUR "
            "network, as its shared-connections link writes them: F for your "
            "1st degree, S for your 2nd, comma-separated. Nothing else is on "
            "record, so a third degree is not guessed, and a lower-case letter "
            "or a word is not LinkedIn's spelling. The value is described "
            "rather than quoted.",
        )
    return _refused(argument, "unknown_value_kind", text, "no such value kind")


def _values(argument: str, kind: str, most: int, raw: Any) -> dict[str, Any]:
    """Every value of one facet argument, in order, or the first refusal.

    ``{"ok": True, "values": [...]}`` -- an EMPTY list means the argument was
    not given, which is not an error: every facet is optional.
    """
    text = str(raw or "").strip()
    if not text:
        return {"ok": True, "values": []}
    pieces = [piece.strip() for piece in text.split(ID_SEPARATOR)]
    if any(not piece for piece in pieces):
        return _refused(
            argument,
            "empty_value",
            text,
            f"{argument} holds an empty member between separators; ids are "
            f"separated by a single '{ID_SEPARATOR}' with nothing empty "
            "between them.",
        )
    if len(pieces) > most:
        return _refused(
            argument,
            "too_many_values",
            text,
            f"{argument} takes at most {most} value(s) per call -- a budget "
            "on this server, not a LinkedIn limit anybody here measured.",
        )
    values: list[str] = []
    for piece in pieces:
        verdict = _one_id(argument, kind, piece)
        if not verdict.get("ok"):
            return verdict
        if verdict["value"] in values:
            return _refused(
                argument,
                "duplicate_value",
                text,
                f"{argument} names the same id twice; each is sent once, and "
                "a repeated one is refused rather than silently dropped.",
            )
        values.append(verdict["value"])
    return {"ok": True, "values": values}


def validated_keywords(keywords: Any) -> dict[str, Any]:
    """A search's keywords, stripped, or the refusal :func:`compose` returns.

    ``{"ok": True, "text": <str>}`` -- an EMPTY ``text`` means no keyword was
    given, which is not an error here -- or a refusal in :func:`_refused`'s
    shape. Split out of :func:`compose` on 2026-09-24, unchanged, so that
    ``search_verticals.compose`` validates a keyword by the SAME code rather
    than by a copy of it that could drift.

    PURE, and it never raises.
    """
    text = str(keywords or "").strip()
    if not text:
        return {"ok": True, "text": ""}
    if len(text) > MAX_KEYWORD_CHARS:
        return _refused(
            "keywords",
            "keywords_too_long",
            text,
            f"keywords run past {MAX_KEYWORD_CHARS} characters -- a budget "
            "on this server, not a LinkedIn limit anybody here measured. "
            "A search is refused rather than truncated, because a "
            "truncated search is a different search.",
        )
    # CONTROL CHARACTERS ONLY (Unicode category Cc), and deliberately not
    # ``str.isprintable()``: that is False for a no-break space and for
    # the zero-width joiners several Indian scripts need inside a word, so
    # it would refuse ordinary names typed in those scripts.
    if any(unicodedata.category(ch) == "Cc" for ch in text):
        return _refused(
            "keywords",
            "keywords_carry_a_control_character",
            text,
            "keywords carry a control character (a newline, a tab, ...). "
            "A search box holds one line of text, and a control character "
            "inside an address is how an anchored pattern is talked past.",
        )
    return {"ok": True, "text": text}


def compose(
    *,
    keywords: Any = "",
    current_company_ids: Any = "",
    past_company_ids: Any = "",
    location_ids: Any = "",
    connections_of: Any = "",
    network: Any = "",
) -> dict[str, Any]:
    """The people-search address for these arguments, or a refusal.

    Returns one of::

        {"built": True,  "url": <address>, "applied": {<argument>: <int>}}
        {"built": False, "argument": <name>, "refused": <literal>,
         "saw": <shape>, "why": <sentence>}

    ``applied`` counts what each argument contributed -- 1 or 0 for
    ``keywords``, the number of ids for a facet -- and carries no value.
    ``url`` is the ONLY field that carries one, and it exists to be handed to
    ``BROWSER.goto``; the tool never publishes it.

    ``network`` IS NEVER SENT WITHOUT A MEMBER. The rows it serves are about
    ONE member's connections -- with ``connections_of``, ``F`` is the
    connections he shares with that member, the search LinkedIn's own
    shared-connections links write -- and the order that added it
    (2026-09-28 15:10) made a named member its condition. Given alone it is
    refused. LinkedIn DOES write it alone, once, on the connections-page
    capture (``tests/fixtures/live2/n23.html``: ``network`` and ``origin``,
    no member) -- a search of his own network by degree, which is census
    ``N 81``'s question and is not built here.

    PURE: arguments in, a dict out. It reads no page, no file, no clock and
    no network, and it never raises.
    """
    given = {
        "current_company_ids": current_company_ids,
        "past_company_ids": past_company_ids,
        "location_ids": location_ids,
        "network": network,
        "connections_of": connections_of,
    }
    pairs: list[tuple[str, str]] = []
    applied: dict[str, int] = {}

    checked = validated_keywords(keywords)
    if not checked.get("ok"):
        return checked
    text = checked["text"]
    if text:
        pairs.append((KEYWORDS_KEY, text))
    applied["keywords"] = 1 if text else 0

    for argument, key, kind, most in FACETS:
        verdict = _values(argument, kind, most, given[argument])
        if not verdict.get("ok"):
            return verdict
        values = verdict["values"]
        if kind == NETWORK_DEGREE:
            # THE CAPTURE'S ORDER, whatever order the caller wrote them in:
            # link 1 lists ``["F","S"]``.
            values = [degree for degree in NETWORK_DEGREES if degree in values]
        if values:
            # LinkedIn's faceted grammar: a JSON list of strings, no spaces.
            pairs.append((key, json.dumps(values, separators=(",", ":"))))
        applied[argument] = len(values)

    if applied["network"] and not applied["connections_of"]:
        return _refused(
            "network",
            "network_needs_a_named_member",
            str(network or "").strip(),
            "network narrows ONE MEMBER'S connections to degrees of your own "
            "network -- with connections_of, F is the connections you share "
            "with that member, the search LinkedIn's own shared-connections "
            "link writes. It is not sent without a member: name one with "
            "connections_of. Nothing was loaded.",
        )

    url = BASE_URL + ("?" + urlencode(pairs) if pairs else "")
    return {"built": True, "url": url, "applied": applied}


def _pairs_of(url: str) -> list[tuple[str, str]]:
    """The decoded query pairs of an address this module composed."""
    return parse_qsl(urlsplit(url).query, keep_blank_values=True)


def boundary_verdict(url: str) -> dict[str, Any]:
    """Ask the READ BOUNDARY about a composed address. Before any session opens.

    ``{"admitted": True}``, or a refusal::

        {"admitted": False,
         "boundary_kind": <the kind BROWSER.goto would raise on it>,
         "boundary_refusal": "FORBIDDEN" | "NOT-ADMITTED",
         "forbidden_substrings": [<the boundary's own substrings it carries>],
         "arguments_carrying_it": [<argument>, ...],
         "why": <sentence>}

    THE DOOR DECIDES; THIS ONLY EXPLAINS. The decision is
    ``readonly.is_read_url`` -- the door's own non-raising form, the pre-check
    ``press.py`` already makes before a press -- and nothing here can admit an
    address it refuses. ``readonly.assert_read_url`` is deliberately NOT
    called: its call sites are pinned to the two navigation paths
    (``tests/test_api_call_sites.py``), and ``BROWSER.goto`` still calls it on
    every address this admits.

    THE EXPLANATION is which of the boundary's OWN forbidden substrings the
    lowered address carries, in the tuple's order -- the method
    ``scripts/_probe_landed_address_sweep._why_refused`` uses -- so every
    string it can publish is one of this package's constants and never a
    caller's value. The first one listed is the one the gate names first; the
    lane's tests hold the two readings together with the census instrument's
    ``check_read_addresses.refusal_of``. A refusal the tuple cannot explain
    lists nothing and says so rather than guessing.
    """
    if readonly.is_read_url(url):
        return {"admitted": True}
    lowered = url.lower()
    found = [bad for bad in readonly._FORBIDDEN_URL_SUBSTRINGS if bad in lowered]

    carrying: list[str] = []
    keys = {key: argument for argument, key in ARGUMENT_KEYS}
    for key, value in _pairs_of(url):
        encoded = urlencode([(key, value)]).lower()
        argument = keys.get(key)
        if argument and argument not in carrying and any(bad in encoded for bad in found):
            carrying.append(argument)

    if found:
        named = ", ".join(f"'{bad}'" for bad in found)
        why = (
            f"the read boundary refuses ANY address carrying {named}, query "
            "included, because each guards a write surface -- and the ruling "
            "that admitted this search forbids narrowing that list for it. So "
            "this search cannot be run by this server with that in it. Nothing "
            "was loaded and no search was spent; the value is not quoted back. "
            "Search again without it."
        )
        kind = "FORBIDDEN"
    else:
        why = (
            "the read boundary does not admit this address, and it carries "
            "none of the boundary's forbidden substrings. A composed people "
            "search should always be admitted, so this is a defect in the "
            "composition, not in the arguments. Nothing was loaded."
        )
        kind = "NOT-ADMITTED"
    return {
        "admitted": False,
        "boundary_kind": readonly.WriteAttemptError.kind,
        "boundary_refusal": kind,
        "forbidden_substrings": found,
        "arguments_carrying_it": carrying,
        "why": why,
    }


def refusal_envelope(verdict: dict[str, Any]) -> dict[str, Any]:
    """The tool's answer to a refusal from :func:`compose` or
    :func:`boundary_verdict`. Zero pages loaded, and nothing quoted back."""
    if "boundary_refusal" in verdict:
        return {
            "ok": False,
            "error": "refused_by_the_read_boundary",
            "boundary_kind": verdict["boundary_kind"],
            "boundary_refusal": verdict["boundary_refusal"],
            "forbidden_substrings": list(verdict["forbidden_substrings"]),
            "arguments_carrying_it": list(verdict["arguments_carrying_it"]),
            "pages_loaded": 0,
            "why": verdict["why"],
        }
    return {
        "ok": False,
        "error": "bad_argument",
        "argument": verdict.get("argument"),
        "refused": verdict.get("refused"),
        "saw": verdict.get("saw"),
        "pages_loaded": 0,
        "why": verdict.get("why"),
    }


def _segments(path: str) -> tuple[str, ...]:
    return tuple(segment for segment in path.split("/") if segment)


def _members(key: str, values: list[str]) -> Optional[frozenset[str]]:
    """The set of values one query key carries, whichever spelling it uses.

    A JSON list is read as its members; a bare value as itself; a repeated key
    as the union. ``None`` when a list cannot be parsed -- which is not the
    same answer as an empty set, and is reported as ``different_values``.
    """
    out: set[str] = set()
    for value in values:
        text = value.strip()
        if key == KEYWORDS_KEY:
            out.add(" ".join(text.split()).casefold())
            continue
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except ValueError:
                return None
            if not isinstance(parsed, list):
                return None
            out.update(str(item).strip() for item in parsed)
        else:
            out.add(text)
    return frozenset(out)


def landing_verdict(landed: Any, asked: str) -> dict[str, Any]:
    """What LinkedIn did with each argument, read off the address it settled on.

    ``landed`` is a value THE SITE chose. It is parsed, compared with the
    address this module composed (``asked``), and dropped: what comes back is
    one boolean and one literal from :data:`KEPT_VERDICTS` per argument that
    was sent. No value from either address is returned.

    ``on_people_search`` is True only when the settled address is the people
    vertical by CLOSED SEGMENT EQUALITY on this host -- the rule the search
    admission's amended condition 2 set -- so a redirect to another vertical
    or to a wall reads False.
    """
    asked_pairs = _pairs_of(asked)
    sent: dict[str, list[str]] = {}
    for key, value in asked_pairs:
        sent.setdefault(key, []).append(value)
    arguments = [(argument, key) for argument, key in ARGUMENT_KEYS if key in sent]

    try:
        parts = urlsplit(str(landed or ""))
        landed_pairs = parse_qsl(parts.query, keep_blank_values=True)
    except ValueError:
        return {
            "on_people_search": False,
            "query_kept": {argument: "unreadable" for argument, _key in arguments},
        }

    segments = _segments(parts.path)
    on_people = (
        parts.scheme == "https"
        and parts.netloc == _HOST
        and segments == _PEOPLE_SEGMENTS
    )

    got: dict[str, list[str]] = {}
    for key, value in landed_pairs:
        got.setdefault(key, []).append(value)

    kept: dict[str, str] = {}
    for argument, key in arguments:
        sent_values = sent[key]
        landed_values = got.get(key)
        if not landed_values:
            kept[argument] = "absent"
        elif landed_values == sent_values:
            kept[argument] = "verbatim"
        else:
            want = _members(key, sent_values)
            have = _members(key, landed_values)
            if want is not None and have is not None and want == have:
                kept[argument] = "same_values"
            else:
                kept[argument] = "different_values"
    return {"on_people_search": on_people, "query_kept": kept}


def emitted_alphabet() -> frozenset[str]:
    """Every string :func:`landing_verdict` and the refusal kinds can publish
    that is not a sentence or a shape."""
    return frozenset(KEPT_VERDICTS) | frozenset(BOUNDARY_REFUSALS)
