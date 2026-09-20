"""Which LinkedIn ITEM ADDRESSES a page drew, and -- only on request -- which items.

WHY THIS EXISTS. The messaging-and-content census records, at row ``C42``,
the constraint that blocks more of its content half than any single missing
control does:

    To open ``/feed/update/<urn>/`` you need a urn, and **no tool in this
    server returns one.**

That sentence was written before ``linkedin_my_activity_items`` shipped and is
no longer literally true -- that tool returns item keys for his own items, off
``/in/me/``, and says so in its own docstring. **What is still true is the part
that matters: that route has never returned an item.** Every recorded live run
refused (``no_page_owner_heading``, then ``no_self_assertion`` on five
consecutive calls), so the census files it ``COVERED-UNFIRED`` and the
addressing primitive remains, in practice, unavailable.

**THIS MODULE IS A SECOND ROUTE TO THE SAME PRIMITIVE, ON A PAGE THAT IS
MEASURED TO SERVE.** ``/analytics/creator/content/`` is on the read allowlist,
and ``linkedin_creator_analytics`` has fired against it and returned a complete
seven-point series -- the census banks that as ``C40`` COVERED-PROVEN. A page
that renders is worth more than a page that argues, and this one draws item
addresses in its own hrefs.

## WHAT WAS MEASURED, AND WHERE THE NUMBERS COME FROM

Measured offline on 2026-09-20 against a capture of that page taken by a
sibling wave at 11:46 by the box and held in the gitignored ``_state/``
directory -- raw captures are never committed. **The capture is not the
evidence chain**: ``scripts/_probe_item_addresses_in_capture.py`` re-derives
every figure below from any capture of this surface, and
``tests/fixtures/synthetic/creator_content_addresses.html`` is the committed
artefact the tests run against.

    anchors parsed                                   27
    /feed/update/urn:li:share:<digits>/               4 hrefs, 2 distinct urns
    /analytics/post-summary/urn:li:activity:<digits>/ 2 hrefs, 2 distinct urns
    distinct urns                                     4

**THE COUNT IS ``distinct_urns`` AND IT IS DELIBERATELY NOT CALLED POSTS.**
The field was named ``distinct_items`` for about an hour, until the probe was
run and the two urn FAMILIES appeared: LinkedIn draws a permalink under
``urn:li:share:`` and a per-post analytics address under ``urn:li:activity:``,
and their digit runs DO NOT MATCH -- measured, overlap 0 over four 19-digit
runs. So 4 distinct urns are consistent with 2 posts drawn twice and equally
consistent with 4 posts, **and nothing in this reading separates those.** A
field called ``items`` would have answered *four* to a question it cannot
answer, which is the defect ``newsletters.py`` records in its own docstring:
ten anchors, five newsletters. Whoever pairs the two families gets to publish
a post count; this module does not.

**THE SECOND MARKER IS THE FINDING.** ``/analytics/post-summary/`` is a
PER-POST analytics address. The census's ``C38`` (*View post analytics*) has
carried ``allowlist +1`` for an address nobody could name -- its own cell says
*"Per-post needs a per-post surface this address does not serve"* -- and this
repository has now recorded a ninth instance of the same shape, that a blocker
billing one allowlist pattern names no in-product address to put in it. Here
LinkedIn names it, on a page this server already opens. **This module does not
admit that address and does not open it**: an admitted address is not a served
one, only a load can tell them apart, and this wave is forbidden the load.

## WHAT MAY LEAVE THIS MODULE

A LinkedIn item urn is an IDENTIFIER OF A REAL POST BY A REAL PERSON, and
``tests/test_no_committed_identity.py`` sweeps every tracked file for exactly
its shape. So the default is COUNTS, and identifiers come back only when the
caller asks for them by name:

* ``include_identifiers=False`` (the default) -- **no string in the return is a
  substring of any input.** That is the same OUT guarantee ``feed.py`` carries,
  asserted the same way.
* ``include_identifiers=True`` -- the ONLY substrings that may leave are whole
  anchored ``urn:li:<letters>:<digits>`` matches. Never a slug, never a query
  string, never a label, never a fragment of a path.

The narrow opt-in is copied from ``linkedin_open_messaging``'s ``include_names``
and for its reason: this output lands in a model's context and in transcripts,
where an identifier outlives the question that fetched it.

## WHAT THIS MODULE DOES NOT ESTABLISH

**Authorship.** ``linkedin_my_activity_items`` establishes that an item is his
on three independent conditions before it publishes a key, and it is right to.
This module establishes NOTHING of the kind: it reports what a page drew. The
only reason its output can be read as his is that its reader is bound to ONE
address, his own analytics page, and that binding lives in
:func:`read_item_addresses` rather than in a caller's assumption. Point it at a
feed and it will happily classify other people's posts, which is why nothing
here takes a url.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

from .dom import ACTIVITY_PERMALINK_MARKER

#: THE PER-POST ANALYTICS MARKER, measured 2026-09-20 in a capture of
#: ``/analytics/creator/content/``: two hrefs carried it, each with a distinct
#: item urn. It is NOT on the read allowlist and this module does not propose
#: adding it -- see the module docstring.
POST_SUMMARY_MARKER = "/analytics/post-summary/"

#: The permalink marker is IMPORTED rather than retyped. ``dom.py`` measured
#: it and quotes the census reading beside it; a second spelling here would be
#: a second thing to keep true.
PERMALINK_MARKER = ACTIVITY_PERMALINK_MARKER

#: THE CLOSED KIND VOCABULARY -- every word :func:`classify` can put in a
#: ``kind`` field. Two entries, one per marker, in the order the markers are
#: checked.
ADDRESS_KINDS = ("permalink", "post_summary")

#: Marker -> kind, so the two cannot drift apart.
_KIND_FOR_MARKER = {
    PERMALINK_MARKER: "permalink",
    POST_SUMMARY_MARKER: "post_summary",
}

#: THE CLOSED REFUSAL VOCABULARY. Four reasons, each produced by exactly one
#: branch of :func:`classify`, and each naming WHAT WAS SEEN rather than only
#: what was not matched -- three rounds were lost in this repository to
#: refusals that reported only the miss.
REFUSALS = (
    "no_href",
    "no_item_marker",
    "both_markers",
    "not_urn_shaped",
)

#: The urn prefix this repository admits. The SHAPE is
#: ``urn:li:<letters>:<digits>`` and it is not invented here -- it is the
#: shape ``readonly._ALLOWED_URL_PATTERNS`` anchors the ``/feed/update/``
#: entry on, the shape ``writes.py`` normalises ``react_to_item`` targets to,
#: and the shape ``dom.py`` ships into the page as ``urnShape``. Parsed with
#: string methods rather than a pattern so that the check reads as the
#: sentence above rather than as an escape sequence.
_URN_PREFIX = "urn:li:"

#: The one string this module publishes in place of an identifier it will not
#: disclose. Deliberately NOT shaped like a urn, so a reader cannot mistake it
#: for a redacted real value -- the same reasoning as ``feed.PUBLISHED_HREF``.
WITHHELD = "<an item this page drew>"


def _is_urn(candidate: str) -> bool:
    """Does ``candidate`` match ``urn:li:<letters>:<digits>`` exactly?

    Whole-string, never a containment test. A containment test would accept
    a query string that happens to carry a urn among other things, and the
    whole safety argument here is that only a WHOLE anchored match may leave.
    """
    if not candidate.startswith(_URN_PREFIX):
        return False
    rest = candidate[len(_URN_PREFIX):]
    kind, sep, digits = rest.partition(":")
    if not sep:
        return False
    if not kind.isascii() or not kind.isalpha():
        return False
    if not digits.isascii() or not digits.isdigit():
        return False
    return True


def _segment_after(href: str, marker: str) -> Optional[str]:
    """The path segment immediately after ``marker``, or ``None``.

    The segment ends at the next ``/``, ``?`` or ``#``. A urn contains
    colons, which is why the delimiter set is spelled out rather than left to
    a split on ``:``.
    """
    index = href.find(marker)
    if index < 0:
        return None
    rest = href[index + len(marker):]
    for delimiter in ("/", "?", "#"):
        cut = rest.find(delimiter)
        if cut >= 0:
            rest = rest[:cut]
    return rest


def classify(href: Optional[str]) -> dict[str, Any]:
    """Which KIND of item address is this href, and which item?

    Returns one of two shapes and never raises, because one unusable href on
    a page of many is not an error:

    ``{"recognised": True, "kind": <one of ADDRESS_KINDS>, "urn": <str>}``
    ``{"recognised": False, "refused": <one of REFUSALS>, "saw": [...]}``

    ``urn`` is the WHOLE anchored match and nothing else. ``saw`` carries only
    words from :data:`ADDRESS_KINDS`, never a substring of ``href``.
    """
    if not isinstance(href, str) or not href:
        return {"recognised": False, "refused": "no_href", "saw": []}

    seen = [
        _KIND_FOR_MARKER[marker]
        for marker in (PERMALINK_MARKER, POST_SUMMARY_MARKER)
        if marker in href
    ]

    if not seen:
        return {"recognised": False, "refused": "no_item_marker", "saw": []}

    if len(seen) > 1:
        # An href carrying BOTH markers is decided by nothing but the order
        # these checks happen to run in, and an ordering accident is not a
        # classification. Refused rather than attributed -- the same rule
        # ``feed.author_kind`` applies to an ambiguous entity path.
        return {"recognised": False, "refused": "both_markers", "saw": seen}

    kind = seen[0]
    marker = PERMALINK_MARKER if kind == "permalink" else POST_SUMMARY_MARKER
    segment = _segment_after(href, marker)

    if segment is None or not _is_urn(segment):
        return {"recognised": False, "refused": "not_urn_shaped", "saw": seen}

    return {"recognised": True, "kind": kind, "urn": segment}


def tally(
    hrefs: Iterable[Optional[str]], include_identifiers: bool = False
) -> dict[str, Any]:
    """Count the item addresses on a page; disclose the items only on request.

    ``include_identifiers`` defaults to False and the default answer is made
    of integers and of this module's own literals. Pass True when you have
    decided to hold real post identifiers: they are identifiers for real posts
    and this repository's own guard sweeps every tracked file for their shape.

    Returns ``hrefs_seen``, ``recognised``, ``by_kind`` (every word in
    :data:`ADDRESS_KINDS`, present even at zero, so an absent kind is a zero
    rather than a missing key), ``refused`` (every word in :data:`REFUSALS`,
    same reason), ``distinct_urns``, ``distinct_by_kind``, and ``urns``.

    **``distinct_urns`` IS NOT A POST COUNT** and this module will not publish
    one -- see the module docstring. ``by_kind`` counts HREFS and
    ``distinct_by_kind`` counts URNS, and they differ on a real page: LinkedIn
    draws a permalink twice per post.

    ``urns`` is a list of urns when ``include_identifiers`` is True, and a
    list of :data:`WITHHELD` of the same length when it is False -- the LENGTH
    is the answer to *how many addresses*, and it is available either way.
    """
    by_kind = {kind: 0 for kind in ADDRESS_KINDS}
    distinct_by_kind: dict[str, set[str]] = {kind: set() for kind in ADDRESS_KINDS}
    refused = {reason: 0 for reason in REFUSALS}
    order: list[str] = []
    seen_urns: set[str] = set()
    hrefs_seen = 0
    recognised = 0

    for href in hrefs:
        hrefs_seen += 1
        verdict = classify(href)
        if not verdict["recognised"]:
            refused[verdict["refused"]] += 1
            continue
        recognised += 1
        by_kind[verdict["kind"]] += 1
        urn = verdict["urn"]
        distinct_by_kind[verdict["kind"]].add(urn)
        if urn not in seen_urns:
            seen_urns.add(urn)
            order.append(urn)

    return {
        "hrefs_seen": hrefs_seen,
        "recognised": recognised,
        "by_kind": by_kind,
        "distinct_by_kind": {k: len(v) for k, v in distinct_by_kind.items()},
        "refused": refused,
        "distinct_urns": len(order),
        "urns": list(order) if include_identifiers else [WITHHELD] * len(order),
        "disclosed": bool(include_identifiers),
    }


async def read_item_addresses(
    page: Any, include_identifiers: bool = False
) -> dict[str, Any]:
    """The item addresses on the already-open content-analytics page.

    The page must already be at ``creator_analytics.CONTENT_ANALYTICS_URL``;
    navigation is the caller's, so this stays testable and does no IO of its
    own beyond reading attributes. **The binding to that one address is the
    only thing that makes the items his**, and it is stated rather than
    assumed: this function takes no url and cannot be pointed elsewhere.

    ``route`` travels with the reading for the same reason it does in
    ``creator_analytics.read_content_analytics``: a caller seeing
    ``recognised`` 0 cannot otherwise tell "this page drew no posts" from
    "LinkedIn changed the address shape and this route is dead".
    """
    hrefs: list[Optional[str]] = []
    locator = page.locator("a[href]")
    try:
        total = int(await locator.count())
    except Exception:  # noqa: BLE001
        total = 0
    for index in range(total):
        try:
            hrefs.append(await locator.nth(index).get_attribute("href"))
        except Exception:  # noqa: BLE001
            hrefs.append(None)

    reading = tally(hrefs, include_identifiers=include_identifiers)
    reading["route"] = (
        "href markers on the creator content-analytics page. Measured "
        "2026-09-20 against a capture: 27 anchors, 4 permalink hrefs over 2 "
        "distinct urns and 2 post-summary hrefs over 2 distinct urns. "
        "distinct_urns is not a post count -- the two urn families do not "
        "share digit runs. If recognised is 0 while hrefs_seen is large, the "
        "page still renders but this route no longer finds item addresses."
    )
    return reading
