"""Describing an address THE SITE chose, without republishing it.

## THE DEFECT, STATED ONCE

``auth.assert_not_authwall`` wrote the landed url verbatim into its own
refusal::

    f"loading the {surface} page landed on {final_url}, which is ..."

That exception escapes the tool, ``server._error`` renders it through
``config.scrub``, and scrub substitutes THIS SERVER'S OWN FILESYSTEM PATHS and
nothing else -- a name has no shape to scrub. **It knows paths. It does not
know urls and it does not know names.** TWENTY-SEVEN tool-facing call sites
raise through that one function (28 calls in ``linkedin_server/``, one of them
inside ``server.py``'s own local helper), and 7 more live in ``scripts/``.
Counted by AST; a grep for the name returns 30 because it also matches the two
``import`` lines.

    A LANDING IS A STRING THE REMOTE SITE CHOSE, AND THIS PROCESS HAS NO
    ALLOWLIST FOR IT.

**That sentence is the defect, and no particular query parameter is.** The
strongest known instance is the authwall's redirect convention -- a signed-out
bounce carries the address it bounced inside its own query, and the canonical
form of an organisation address is a SLUG, which is a name: a sole trader, an
eponymous firm or a personal brand puts a person's name in one, and
``/company/<slug>/`` and ``/school/<slug>/`` are both on this server's read
allowlist. But the repair does not rest on that convention being present. It
rests on provenance: a value LinkedIn chose, published into text a scrubber
cannot clean, is out of this process whatever it happens to hold today.

This is the third instance of one law in three days. ``int()`` quotes the value
it refused into its own ``ValueError`` -- 14 of 115 readers leaked, closed by
``coerce.py``. ``assert_not_authwall`` interpolates the landing -- this module.
**``scrub()`` knowing only paths is the common cause of both.**

## WHY THE REPAIR IS NOT IN ``scrub()``, WHICH IS THE REAL DECISION

``config.scrub`` is the one boundary every tool funnels its failures through,
so it looks like the cheapest place to close a class -- and it is, for the
class it was built for. It is the wrong place for this one, for four reasons
and not for a preference:

1. **ITS ENGINE REFUSES THIS JOB IN WRITING, AND THE FILE MAY NOT BE EDITED.**
   ``scrub`` is ``paths.relativise_known``, a vendored copy carrying a
   DO-NOT-EDIT header. That function says: *"SUBSTITUTION IS EXACT, NEVER
   HEURISTIC [...] A regex that hunted for path-shaped text in arbitrary prose
   would eventually eat a Naukri API route, A URL, or a Windows drive letter
   inside quoted user content -- which is how a scrubber does more damage than
   the leak it was written for."* A url is named there as the COLLATERAL. Doing
   the opposite inside the same call is not an extension of that reasoning, it
   is its refutation.

2. **THERE IS NOTHING TO PUT ON THE ALLOWLIST.** ``scrub`` substitutes values
   the server ALREADY KNOWS it may have emitted -- its own five directories,
   read fresh so an environment override is covered. The leaking value here is
   chosen by LinkedIn at the moment of the bounce. An allowlist of what the
   server may publish does not close it either: this package assembles
   addresses at runtime from caller-supplied numeric ids, so "known good" is a
   pattern set, which is a heuristic wearing an allowlist's clothes.

3. **PROVENANCE DECIDES PUBLISHABILITY, AND THE SINK CANNOT SEE PROVENANCE.**
   ``https://www.linkedin.com/company/5417062/`` is an address this package
   ASSEMBLED and publishes on purpose -- ``source_url``, ``company_page_url``.
   (That id is the suite's invented one, already in
   ``tests/test_no_committed_identity.SYNTHETIC_IDS``. The first draft of this
   paragraph used a made-up four-digit id and the shape guard refused the
   file -- correctly: a reviewer cannot tell an invented id from a real one,
   which is why the rule is on the SHAPE.)
   ``https://www.linkedin.com/authwall?sessionRedirect=...`` is an address
   LinkedIn chose. Same shape, opposite verdicts, and only the raise site knows
   which one it is holding. A path is different in exactly the way that makes
   ``scrub`` right FOR PATHS: this machine's absolute layout may never be
   published whatever its provenance, so a sink-side exact substitution is
   correct there. **What transfers from that finding is the OBSERVATION -- a
   value reaches a caller through error text -- never the REMEDY.**

4. **BLAST RADIUS, FROM A WAVE THAT CANNOT RUN THE BROWSER.** ``scrub`` is
   applied to ``str(exc)`` for every exception this server ever reports,
   including Playwright's and the standard library's, whose messages carry
   addresses that ARE the diagnosis. Rewriting all of them is the single
   highest-blast-radius edit available here, and it is the edit the coercion
   wave refused for the same reason when it declined to sweep 42 write-gate
   sites it could not exercise.

## AND THE HONEST HALF OF THAT ARGUMENT

A raise-site repair leaves the next interpolation free to repeat the defect.
That is a real cost and this module does not pretend otherwise. It is paid the
way ``coerce.py`` paid it: **one importable home, so the class closes for
functions nobody has written yet**, plus a standing guard that DISCOVERS its
subjects instead of listing them --
``tests/test_no_message_publishes_a_landing.py`` walks the package's AST and
fails on a message-bearing interpolation of a url-shaped expression that is not
already ruled. A twenty-eighth local fix would have closed one site; this
closes all twenty-seven and fails loudly on the twenty-eighth.

## WHAT MAY BE SAID ABOUT A LANDING

Every string this module can emit is a literal declared below, an integer, or a
boolean -- the same property ``anchors.py`` states about its route classifier
and ``coerce.py`` about its return values. There is no path by which a
character LinkedIn chose becomes part of a descriptor:

* the MARKER that matched, from ``config.AUTHWALL_MARKERS``;
* the HOST, from :data:`HOSTS`, or a refusal literal;
* the ROUTE class of the landing, and of the address it says it bounced from,
  from :data:`ROUTE_CLASSES`;
* counts: path segments, query parameters, how many parameter values hold an
  address;
* the NAMES of those parameters, and only when the name is in
  :data:`ADDRESS_PARAMS` -- a closed set this package declares. A parameter
  LinkedIn invents tomorrow is COUNTED, never quoted;
* ``jobfilter.describe_shape`` of the whole url: a length and a set of
  character classes. That is this repository's shipped "describe without
  quoting" instrument and it is imported rather than re-written.

**THE DESCRIPTOR IS SAFE TO LOG AS WELL AS TO RAISE**, because a log record is
another way out of the process and the rule ``coerce.as_count`` follows --
name the type, never the value -- applies here unchanged.

**AND IT IS NOT LOGGED ANYWAY, WHICH IS A SEPARATE FACT AND NOT A RETRACTION
OF THAT ONE.** ``auth.assert_not_authwall`` logs the SURFACE and nothing
derived from the landing, because ``test_no_navigation_derived_value_reaches
_an_output_sink`` follows the binding from ``final_url`` and a logger call is
one of its sinks. That guard is right about the taint and wrong about the
hazard, and the sanctioned way to tell it so is a ``_SANITISERS`` entry that
this wave did not earn. See the comment at that call site and
``_audit/2026-09-21-the-landed-url.md``.

## WHAT IS DELIBERATELY NOT DONE

**No descriptor is attached to the exception as an attribute.** ``server._error``
publishes ``getattr(exc, "url", "")`` INTO THE PAYLOAD UNSCRUBBED -- that is how
``ExtractionFailedError`` carries its url on purpose. Giving a
``NotAuthenticatedError`` a ``url`` would put the landing straight back on the
wire past every argument above. The descriptor travels in the MESSAGE TEXT,
which is name-free by construction -- and that is the channel the caller
reads.

## WHY THE ROUTE TABLE IS COPIED AND NOT IMPORTED

``anchors.ROUTE_TABLE`` is the same data with the same segment-equality rule,
and this repository's own law is to import the shipped instrument. It is copied
anyway, for one reason: ``anchors`` imports ``dom``, and ``auth`` deliberately
keeps its module-level imports to ``config`` and ``errors`` so that the
authentication path does not drag the page-reading machinery in behind it.

**The copy is not left to drift.** ``tests/test_landing.py`` asserts that every
row here appears in ``anchors.ROUTE_TABLE`` and that every class token this
module can emit is in ``anchors.ROUTE_CLASSES``, so the two vocabularies are
held together by an assertion rather than by discipline.

The rule itself is ``anchors.py``'s scar and is followed rather than
re-derived: **A ROUTE TERM MUST BE A WHOLE PATH SEGMENT AT A FIXED POSITION** --
never a substring of one. Measured there: containment reclassified a help
article, a messaging thread and a school page as member profiles, because the
term ``in`` is a substring of ``linkedin``.
"""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qsl, unquote, urlsplit

from linkedin_server.config import AUTHWALL_MARKERS
from linkedin_server.jobfilter import describe_shape

#: Hosts this server navigates to. Anything else is reported as
#: :data:`HOST_OTHER` rather than named: a bounce can in principle land on a
#: partner domain, and a hostname this package never chose is site-chosen text
#: like any other.
HOSTS: tuple[str, ...] = ("www.linkedin.com", "linkedin.com", "m.linkedin.com")

#: Refusal literals for the host slot. Three states, not one, because "the url
#: had no host" and "the url could not be parsed at all" are different readings
#: and a describer that collapses them describes less than it could.
HOST_OTHER = "another_host"
HOST_NONE = "no_host"
HOST_UNPARSEABLE = "unparseable"

#: ``(class token, first segment, required second segment or "")``. A SUBSET of
#: ``anchors.ROUTE_TABLE``, held to it by ``tests/test_landing.py``. Matching is
#: SEGMENT EQUALITY at these FIXED POSITIONS -- see the module docstring for the
#: scar that rule closes.
ROUTE_TABLE: tuple[tuple[str, str, str], ...] = (
    ("member_profile", "in", ""),
    ("company_page", "company", ""),
    ("school_page", "school", ""),
    ("job_posting", "jobs", "view"),
    ("job_collection", "jobs", "collections"),
    ("job_search", "jobs", "search"),
    ("premium_surface", "premium", ""),
    ("feed_update", "feed", "update"),
    ("messaging", "messaging", ""),
    ("help_article", "help", ""),
)

#: A refusal, and a literal like everything else here. Same spelling as
#: ``anchors.UNCLASSIFIED`` on purpose.
ROUTE_UNCLASSIFIED = "other_internal"

#: The url carried no path at all. NOT the same as "a path I could not place",
#: for the reason the three host states exist.
ROUTE_NONE = "no_path"

#: Every class token this module can emit, so a caller can assert against a
#: closed set rather than against whatever it happened to see.
ROUTE_CLASSES: tuple[str, ...] = tuple(row[0] for row in ROUTE_TABLE) + (
    ROUTE_UNCLASSIFIED,
    ROUTE_NONE,
)

#: Query parameter names this package is willing to REPEAT in a message,
#: because they are LinkedIn's own vocabulary and carry no third-party text in
#: the name itself. A parameter outside this set is COUNTED and never quoted --
#: the vocabulary-in / index-out discipline ``search_results.py`` and
#: ``anchors.py`` are built on, applied to parameter names.
ADDRESS_PARAMS: tuple[str, ...] = (
    "sessionRedirect",
    "session_redirect",
    "redirect",
    "redirectUrl",
    "redirect_uri",
    "returnUrl",
    "return_to",
    "original_referer",
    "fromSignIn",
    "trk",
)

#: The marker slot when nothing matched.
MARKER_NONE = "none"

#: How many times a percent-encoded parameter value is unwrapped before it is
#: looked at. ONE. A bounded number rather than a loop: the value this package
#: cares about is encoded once by the site, and an unbounded unwrap on
#: site-chosen text is a decoder a page controls the run time of.
_UNQUOTE_ROUNDS = 1


def authwall_marker(url: Any) -> Optional[str]:
    """Which ``config.AUTHWALL_MARKERS`` entry this url matched, or ``None``.

    Factored out of the refusal that consumes it so it has a handle and can be
    aimed at a known-bad sample directly -- ``jobfilter.describe_shape``'s
    argument, and the reason it is a function rather than an ``any(...)``
    inside an ``if``.

    The VERDICT is identical to the ``any(marker in url ...)`` this replaces.
    Only the reported marker is new, and it is the first match in the order
    ``AUTHWALL_MARKERS`` declares -- ``/uas/login-submit`` contains ``/login``,
    so more than one can match and the order is what makes the answer
    deterministic rather than arbitrary.
    """
    text = url if isinstance(url, str) else ""
    for marker in AUTHWALL_MARKERS:
        if marker in text:
            return marker
    return None


def _route_of(path: str) -> str:
    """Classify a path by WHOLE SEGMENTS at fixed positions. Never containment."""
    segments = [part for part in str(path or "").split("/") if part]
    if not segments:
        return ROUTE_NONE
    first = segments[0]
    second = segments[1] if len(segments) > 1 else ""
    for token, want_first, want_second in ROUTE_TABLE:
        if first == want_first and (not want_second or second == want_second):
            return token
    return ROUTE_UNCLASSIFIED


def _looks_like_an_address(value: str) -> bool:
    """Does this parameter value hold an address? Shape only, never content."""
    text = str(value or "")
    if not text:
        return False
    lowered = text.lower()
    return (
        "://" in lowered
        or "%3a%2f%2f" in lowered
        or text.startswith("/")
        or lowered.startswith("%2f")
    )


def _split(url: str):
    """``urlsplit`` that cannot raise. Returns ``None`` when it could not parse.

    ``urlsplit`` raises ``ValueError`` on a malformed IPv6 literal, and this
    runs on an ERROR PATH: a describer that can raise turns one failure into a
    different, less informative failure. The refusal is a literal, so an
    unparseable landing is still described rather than dropped.
    """
    try:
        return urlsplit(str(url or ""))
    except ValueError:
        return None


def describe_landing(url: Any) -> dict[str, Any]:
    """Everything about a landed address that is safe to publish.

    Integers, booleans, and literals declared in this module. No character the
    remote site chose is anywhere in the return value -- see the module
    docstring for the alphabet and for why that is the whole property.

    ``bounced_from`` is the most useful field and the reason this function
    parses the query at all: it says the CLASS of the address the landing
    claims to have bounced from -- *you were bounced off a company page* --
    which is what a debugger needs and is a literal, not a name.
    """
    text = url if isinstance(url, str) else ""
    parts = _split(text)

    if parts is None:
        return {
            "marker": authwall_marker(text) or MARKER_NONE,
            "host": HOST_UNPARSEABLE,
            "route": ROUTE_UNCLASSIFIED,
            "path_segments": 0,
            "query_params": 0,
            "params_with_an_address": 0,
            "named_address_params": (),
            "unnamed_address_params": 0,
            "bounced_from": ROUTE_NONE,
            "shape": describe_shape(text),
        }

    host = (parts.netloc or "").lower()
    if not host:
        host_token = HOST_NONE
    elif host in HOSTS:
        host_token = host
    else:
        host_token = HOST_OTHER

    try:
        pairs = parse_qsl(parts.query, keep_blank_values=True)
    except ValueError:  # pragma: no cover - parse_qsl is permissive by default
        pairs = []

    named: list[str] = []
    unnamed = 0
    carrying = 0
    bounced_from = ROUTE_NONE
    for name, value in pairs:
        if not _looks_like_an_address(value):
            continue
        carrying += 1
        if name in ADDRESS_PARAMS:
            if name not in named:
                named.append(name)
        else:
            unnamed += 1
        if bounced_from == ROUTE_NONE:
            decoded = value
            for _ in range(_UNQUOTE_ROUNDS):
                decoded = unquote(decoded)
            inner = _split(decoded)
            bounced_from = _route_of(inner.path if inner is not None else decoded)

    return {
        "marker": authwall_marker(text) or MARKER_NONE,
        "host": host_token,
        "route": _route_of(parts.path),
        "path_segments": len([part for part in (parts.path or "").split("/") if part]),
        "query_params": len(pairs),
        "params_with_an_address": carrying,
        "named_address_params": tuple(sorted(named)),
        "unnamed_address_params": unnamed,
        "bounced_from": bounced_from,
        "shape": describe_shape(text),
    }


def render(described: dict[str, Any]) -> str:
    """One ASCII line a refusal or a log record can carry.

    Every fragment below is built from a key of :func:`describe_landing`, so
    this function cannot introduce a string the descriptor did not already
    certify. It is separate from the descriptor because a caller that wants to
    ASSERT on fields should not have to parse prose, and a caller that wants
    prose should not have to re-derive it.
    """
    parts = [
        "matched " + str(described.get("marker", MARKER_NONE)),
        "host " + str(described.get("host", HOST_NONE)),
        "route " + str(described.get("route", ROUTE_NONE)),
        "{} path segment(s)".format(described.get("path_segments", 0)),
        "{} query parameter(s)".format(described.get("query_params", 0)),
    ]
    carrying = described.get("params_with_an_address", 0)
    if carrying:
        named = described.get("named_address_params", ()) or ()
        unnamed = described.get("unnamed_address_params", 0)
        detail = "{} of them carrying an address".format(carrying)
        if named:
            detail += " (" + ", ".join(str(name) for name in named) + ")"
        if unnamed:
            detail += " plus {} under a parameter name this package does " \
                      "not repeat".format(unnamed)
        parts.append(detail)
        parts.append("bounced from " + str(described.get("bounced_from", ROUTE_NONE)))
    parts.append(str(described.get("shape", "")))
    return "; ".join(part for part in parts if part)


def withheld(url: Any) -> str:
    """:func:`render` of :func:`describe_landing`. The one-call form."""
    return render(describe_landing(url))
