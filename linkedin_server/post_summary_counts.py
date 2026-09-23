"""Per-item IMPRESSIONS and ENGAGEMENTS, off the analytics links drawn beside HIS posts.

Census row ``P G6`` -- *per-post analytics* -- has filed its blocker as an
address: ``/analytics/post-summary/urn:li:activity:<id>/`` was refused, so the
per-post surface was out of reach. That address is admitted by lane L1 on
2026-09-23 and still NEEDS A CAPTURE. **But the headline numbers were never
behind it.** LinkedIn prints them on the LINK TO it, and the link is drawn on a
page this server already opens and has already fired against.

## WHAT WAS MEASURED, AND WHERE

Offline, 2026-09-23, on two raw captures held in the gitignored ``_state/``
directory (never committed; the structure is reproduced in
``tests/fixtures/synthetic/post_summary_counts.html``)::

    /analytics/creator/content/   2 post-summary anchors, each drawing
                                  "<n> impressions <dot> <n> engagements"
                                  then "View analytics"
    his own profile               3 post-summary anchors, each drawing
                                  "<n> impressions" then "View analytics"

Every one is ``urn:li:activity:`` with a 19-digit id, and every one sits
inside ``<main>``. On the analytics page they are the page's "Top posts"
section, so the reading is **the items LinkedIn chose to feature**, not a
complete list of everything he has published -- the scope field says so.

## THE ROUTE IS THE LINK, NOT THE PAGE BEHIND IT

The anchor's FIRST LINE is parsed and nothing else is kept. Selection is by
STRUCTURE -- an ``<a>`` whose href carries the post-summary marker and an
activity urn -- never by position, and the line must match one anchored,
closed shape: an integer and ``impressions``, optionally a separator, an
integer and ``engagements``. Anything else is counted in ``unparsed`` and
discarded. There is no field a word of page text could land in.

## NO IDENTIFIER, NO TEXT, NO NAME LEAVES THIS MODULE

The output is integers, booleans and this module's own literals. The urn is
used INSIDE this process only to de-duplicate (a page may draw one link
twice); it is never returned. A caller that needs identifiers already has
``item_addresses.read_item_addresses(include_identifiers=True)`` and makes that
decision there.

## WHAT IT CANNOT TELL YOU

A zero here is the self-controlling kind. ``readable`` is False when no link
parsed -- the section did not render, or LinkedIn changed its words -- and a
caller must read it before believing a total. **An item he has never been
shown analytics for is not in this reading at all**, and nothing here can
count what was not drawn.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional

from . import item_addresses

#: The marker is IMPORTED, not retyped: ``item_addresses`` measured it.
MARKER = item_addresses.POST_SUMMARY_MARKER

#: Structure, not position: a link inside ``main`` carrying the marker.
SELECTOR = 'main a[href*="/analytics/post-summary/"]'

#: Bounds, so a page that draws something unexpected cannot stream it in.
MAX_ANCHORS = 50
MAX_LINE_CHARS = 120

#: The ONLY urn family ever drawn at this address; the allowlist admits the
#: same one and no other.
URN_KIND = "activity"

#: The two metric words this module will recognise. CLOSED.
METRICS = ("impressions", "engagements")

#: "7 impressions <dot> 0 engagements" or "352 impressions". Anchored at both
#: ends, ASCII digits only, bounded runs. The separator is ONE non-space
#: character (LinkedIn draws a middle dot) and is never kept.
_LINE = re.compile(
    r"^\s*(?P<impressions>[0-9][0-9,]{0,14})\s+impressions?"
    r"(?:\s*\S\s*(?P<engagements>[0-9][0-9,]{0,14})\s+engagements?)?\s*$",
    re.IGNORECASE,
)

SCOPE = (
    "the analytics links LinkedIn draws beside his own posts: impressions, "
    "and engagements where drawn. On /analytics/creator/content/ that is the "
    "items the page features, not everything he has published. A total is "
    "a reading about the account only when readable is True."
)


def _as_int(digits: Optional[str]) -> Optional[int]:
    """Digits with thousands commas -> int, or None. Never raises."""
    if not isinstance(digits, str):
        return None
    cleaned = digits.replace(",", "")
    if not cleaned.isascii() or not cleaned.isdigit():
        return None
    return int(cleaned)


def first_line(text: Optional[str]) -> Optional[str]:
    """The first non-blank line of a link's rendered text, bounded, or None."""
    if not isinstance(text, str):
        return None
    for line in text.splitlines():
        if line.strip():
            return line if len(line) <= MAX_LINE_CHARS else None
    return None


def parse_line(line: Optional[str]) -> Optional[dict[str, Optional[int]]]:
    """One link's first line -> ``{"impressions": int, "engagements": int|None}``.

    None when the line does not have EXACTLY the measured shape. Never a
    partial reading and never an exception carrying the text.
    """
    if not isinstance(line, str) or len(line) > MAX_LINE_CHARS:
        return None
    match = _LINE.match(line)
    if match is None:
        return None
    impressions = _as_int(match.group("impressions"))
    if impressions is None:
        return None
    engagements_raw = match.group("engagements")
    engagements = _as_int(engagements_raw) if engagements_raw is not None else None
    if engagements_raw is not None and engagements is None:
        return None
    return {"impressions": impressions, "engagements": engagements}


def _activity_key(href: Optional[str]) -> Optional[str]:
    """The link's urn if it is an ACTIVITY post-summary address, else None.

    Kept in-process for de-duplication only. ``item_addresses.classify`` does
    the parsing, so the two modules cannot disagree about what a urn is.
    """
    verdict = item_addresses.classify(href)
    if not verdict.get("recognised") or verdict.get("kind") != "post_summary":
        return None
    urn = verdict.get("urn") or ""
    if urn.split(":")[2:3] != [URN_KIND]:
        return None
    return urn


def tally(pairs: Iterable[tuple[Optional[str], Optional[str]]]) -> dict[str, Any]:
    """``(href, rendered text)`` pairs -> the reading. Pure; no page involved.

    One entry per DISTINCT activity urn, in the order the page drew them. A
    second link to the same item is counted in ``duplicate_links`` and does
    not add a second entry.
    """
    anchors_seen = 0
    not_activity = 0
    duplicates = 0
    unparsed = 0
    seen: set[str] = set()
    impressions: list[int] = []
    engagements: list[Optional[int]] = []
    for href, text in pairs:
        anchors_seen += 1
        key = _activity_key(href)
        if key is None:
            not_activity += 1
            continue
        if key in seen:
            duplicates += 1
            continue
        parsed = parse_line(first_line(text))
        if parsed is None:
            unparsed += 1
            continue
        seen.add(key)
        impressions.append(int(parsed["impressions"] or 0))
        engagements.append(parsed["engagements"])
    drawn_engagements = [value for value in engagements if value is not None]
    return {
        "anchors_seen": anchors_seen,
        "items_read": len(impressions),
        "impressions": impressions,
        "engagements": engagements,
        "total_impressions": sum(impressions),
        "total_engagements": (
            sum(drawn_engagements) if drawn_engagements else None
        ),
        "engagements_drawn_for": len(drawn_engagements),
        "not_activity_links": not_activity,
        "duplicate_links": duplicates,
        "unparsed": unparsed,
        "readable": len(impressions) > 0,
        "scope": SCOPE,
    }


async def read_post_summary_counts(page: Any) -> dict[str, Any]:
    """The reading, off the already-open page. Takes no url; navigates nowhere.

    Locator reads only -- ``count``, ``get_attribute`` and ``inner_text`` --
    so no script is injected and the evaluate waiver budget does not move. A
    locator call that fails is counted, never raised: one unreadable link on
    a page of many is not an error, and an exception here could carry page
    text into an envelope.
    """
    pairs: list[tuple[Optional[str], Optional[str]]] = []
    unreadable = 0
    locator = page.locator(SELECTOR)
    try:
        total = int(await locator.count())
    except Exception:  # noqa: BLE001
        total = 0
    for index in range(min(total, MAX_ANCHORS)):
        node = locator.nth(index)
        try:
            href = await node.get_attribute("href")
            text = await node.inner_text()
        except Exception:  # noqa: BLE001
            unreadable += 1
            continue
        pairs.append((href, text))
    reading = tally(pairs)
    reading["unreadable_links"] = unreadable
    reading["links_beyond_bound"] = max(0, total - MAX_ANCHORS)
    return reading


def emitted_alphabet() -> frozenset[str]:
    """Every string VALUE this module can publish: its own scope sentence.

    Everything else in a reading is an integer, a boolean or None.
    """
    return frozenset({SCOPE})
