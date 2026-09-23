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
location in one search), ``N 85`` and ``N 172`` (the connections of a member).

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
(``_audit/2026-09-24-lane-s-people-search.md`` section 2):

    keywords        LinkedIn-authored, space written '+'           MEASURED
    currentCompany  LinkedIn-authored as a JSON LIST (company root) MEASURED
                    and bare (profile views, a job page)
    pastCompany     LinkedIn-authored BARE only (a job page)        list DERIVED
    geoUrn          LinkedIn-authored BARE only (profile views)     list DERIVED
    connectionOf    never LinkedIn-authored; named by a test        list DERIVED

LinkedIn's FACETED grammar on this surface is JSON -- a list per facet
(``currentCompany``, ``activelyHiringForJobTitles``) or a JSON string
(``activelyHiring``). Every facet here is sent in that grammar, one code path,
and the list form is the only one that can carry more than one value, which is
what ``N 94`` asks for. **A two-member list is on record for no facet at all**;
it is the same grammar with a second member, and it is DERIVED. The tool reports
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
:func:`boundary_verdict` puts the composed address to ``readonly.assert_read_url``
-- the door itself, not a second copy of its decision -- before any session
opens, and a refusal comes back structured: the boundary's own kind, the
substring (published only when it is a member of the boundary's own tuple), the
argument that carried it, and a sentence written for a person who was
searching, not "not a read surface". Nothing is loaded.
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

#: ``(tool argument, LinkedIn query key, value kind, most values per call)``.
#: ORDER IS THE ADDRESS ORDER: keywords first, then these, as listed.
#:
#: THE MEMBER FACET TAKES ONE VALUE, deliberately narrower than the others:
#: the rows it serves ask about ONE member's connections, and a call that
#: named several other people at once would carry more third-party ids than
#: any row needs.
FACETS: tuple[tuple[str, str, str, int], ...] = (
    ("current_company_ids", "currentCompany", ORGANISATION_ID, 5),
    ("past_company_ids", "pastCompany", ORGANISATION_ID, 5),
    ("location_ids", "geoUrn", GEO_ID, 5),
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

#: The boundary's own refusal sentence, read the way
#: ``scripts/check_read_addresses.kind_of_refusal`` reads it -- the gate's own
#: words, pinned by two committed tests in ``tests/test_readonly.py``.
#: ``tests/test_people_search_readers.py`` drives both readers over the same
#: refusals so the two cannot drift apart.
_FORBIDDEN_SENTENCE = re.compile(r" contains '([^']+)', which is not a read surface")
_PATTERN_WOULD_ADMIT = "A READ PATTERN DOES ADMIT THIS ADDRESS"
_NO_PATTERN_EITHER = "AND NO READ PATTERN ADMITS THIS ADDRESS EITHER"
_NOT_ON_THE_ALLOWLIST = "is not on the read-only allowlist"


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


def compose(
    *,
    keywords: Any = "",
    current_company_ids: Any = "",
    past_company_ids: Any = "",
    location_ids: Any = "",
    connections_of: Any = "",
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

    PURE: arguments in, a dict out. It reads no page, no file, no clock and
    no network, and it never raises.
    """
    given = {
        "current_company_ids": current_company_ids,
        "past_company_ids": past_company_ids,
        "location_ids": location_ids,
        "connections_of": connections_of,
    }
    pairs: list[tuple[str, str]] = []
    applied: dict[str, int] = {}

    text = str(keywords or "").strip()
    if text:
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
        pairs.append((KEYWORDS_KEY, text))
    applied["keywords"] = 1 if text else 0

    for argument, key, kind, most in FACETS:
        verdict = _values(argument, kind, most, given[argument])
        if not verdict.get("ok"):
            return verdict
        values = verdict["values"]
        if values:
            # LinkedIn's faceted grammar: a JSON list of strings, no spaces.
            pairs.append((key, json.dumps(values, separators=(",", ":"))))
        applied[argument] = len(values)

    url = BASE_URL + ("?" + urlencode(pairs) if pairs else "")
    return {"built": True, "url": url, "applied": applied}


def _pairs_of(url: str) -> list[tuple[str, str]]:
    """The decoded query pairs of an address this module composed."""
    return parse_qsl(urlsplit(url).query, keep_blank_values=True)


def boundary_verdict(url: str) -> dict[str, Any]:
    """Put a composed address to the READ BOUNDARY. Before any session opens.

    ``{"admitted": True}``, or a refusal carrying the boundary's own reading::

        {"admitted": False,
         "boundary_kind": <WriteAttemptError.kind>,
         "boundary_refusal": "FORBIDDEN" | "NO-PATTERN" | "UNREADABLE",
         "forbidden_substring": <one of the boundary's own substrings> | None,
         "a_read_pattern_admits_the_address": True | False | None,
         "arguments_carrying_it": [<argument>, ...],
         "why": <sentence>}

    THE DOOR DECIDES, THIS ONLY REPORTS. ``readonly.assert_read_url`` is called
    -- the same function ``BROWSER.goto`` calls first -- and its exception is
    READ, never re-derived. The substring is taken off the boundary's own
    sentence and published ONLY if it is a member of the boundary's own
    forbidden tuple, so nothing a caller typed can come back through this
    field. The exception's text, which quotes the whole address, is not
    returned.
    """
    try:
        readonly.assert_read_url(url)
    except readonly.WriteAttemptError as exc:
        message = str(exc)
        substring: Optional[str] = None
        pattern_admits: Optional[bool] = None
        hit = _FORBIDDEN_SENTENCE.search(message)
        if hit and hit.group(1) in readonly._FORBIDDEN_URL_SUBSTRINGS:
            substring = hit.group(1)
            kind = "FORBIDDEN"
            if _PATTERN_WOULD_ADMIT in message:
                pattern_admits = True
            elif _NO_PATTERN_EITHER in message:
                pattern_admits = False
        elif _NOT_ON_THE_ALLOWLIST in message:
            kind = "NO-PATTERN"
            pattern_admits = False
        else:
            kind = "UNREADABLE"

        carrying: list[str] = []
        if substring is not None:
            keys = dict((key, argument) for argument, key in ARGUMENT_KEYS)
            for key, value in _pairs_of(url):
                encoded = urlencode([(key, value)]).lower()
                argument = keys.get(key)
                if argument and substring in encoded and argument not in carrying:
                    carrying.append(argument)

        if kind == "FORBIDDEN":
            why = (
                f"the read boundary refuses ANY address carrying "
                f"'{substring}', query included, because that substring guards "
                "a write surface -- and the ruling that admitted this search "
                "forbids narrowing that list for it. So this search cannot be "
                "run by this server with that word in it. Nothing was loaded "
                "and no search was spent; the value is not quoted back. Search "
                "again without that word."
            )
        elif kind == "NO-PATTERN":
            why = (
                "the read boundary does not admit this address. A composed "
                "people search should always be admitted, so this is a defect "
                "in the composition, not in the arguments. Nothing was loaded."
            )
        else:
            why = (
                "the read boundary refused this address and its refusal could "
                "not be read -- reported rather than guessed. Nothing was "
                "loaded."
            )
        return {
            "admitted": False,
            "boundary_kind": readonly.WriteAttemptError.kind,
            "boundary_refusal": kind,
            "forbidden_substring": substring,
            "a_read_pattern_admits_the_address": pattern_admits,
            "arguments_carrying_it": carrying,
            "why": why,
        }
    return {"admitted": True}


def refusal_envelope(verdict: dict[str, Any]) -> dict[str, Any]:
    """The tool's answer to a refusal from :func:`compose` or
    :func:`boundary_verdict`. Zero pages loaded, and nothing quoted back."""
    if "boundary_refusal" in verdict:
        return {
            "ok": False,
            "error": "refused_by_the_read_boundary",
            "boundary_kind": verdict["boundary_kind"],
            "boundary_refusal": verdict["boundary_refusal"],
            "forbidden_substring": verdict["forbidden_substring"],
            "a_read_pattern_admits_the_address": verdict[
                "a_read_pattern_admits_the_address"
            ],
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
    return frozenset(KEPT_VERDICTS) | {"FORBIDDEN", "NO-PATTERN", "UNREADABLE"}
