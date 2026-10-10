"""Read his AUDIENCE analytics: the follower count and the follower DEMOGRAPHICS.

Census row ``P L1``. One admitted page, :data:`AUDIENCE_URL` -- anchored, no
query, no sub-path, on the read allowlist in ``readonly.py`` -- read as LinkedIn
draws it on the FIRST RENDER: no press, no scroll, no second load.

## WHAT THE PAGE DRAWS

MEASURED on the live lane's session-1 capture (2026-09-23, the address served
exactly), by keyed hash and structure, counts only; the tracked skeleton is
``tests/fixtures/live1/audience.html`` (``scripts/_build_audience_fixture.py``):

* a follower count beside the label ``Total followers``: the label's parent
  holds exactly one other text, an integer;
* a demographics nav -- one ``nav`` of the page's four -- holding seven buttons:
  ``All``, the ONE ``aria-current`` marks, and six dimensions in LinkedIn's
  words, :data:`DIMENSIONS`;
* under ``All``, ONE ENTRY PER DIMENSION: a ``role="progressbar"``, the
  dimension word in a ``p`` of the nearest ``div`` above it that holds one, and
  beneath that ``div`` a label paired with a share written ``N%``.

## WHAT IT DOES NOT READ, AND SAYS SO

* **A DIMENSION'S OWN LIST.** Each dimension tab draws its full breakdown only
  after a PRESS, and no press is sanctioned on this page. So every dimension
  tab that is not the view is returned in ``lists_unread``: present, and unread.
  A dimension drawn as a tab with no entry under the view is in
  ``dimensions_unread``.
* **THE ASIDE.** The page draws his profile card in an ``aside``; nothing here
  reads it. The entries are read only inside the nearest container of the
  demographics nav that holds a progressbar.
* **THE FOLLOWER-GROWTH CHART.** Out of this row's scope.

## PEOPLE: THE ENTRIES ARE OTHER PEOPLE'S ATTRIBUTES, AGGREGATED

A label is a job title, a place, an employer -- other people's, aggregated.
Each one leaves this module only as ``census_shape`` of its text, then
``census_redact_rare`` of that shape with ``count`` the number of entries THIS
READ drew under the same shape, exactly as their contracts say: a capitalised
run in a shape drawn once is blanked to ``<redacted>``, a shape the gate refuses
is ``<opaque>``. The contract's own stated residual stands: a label that is ONE
capitalised word and nothing else survives (``shape._CENSUS_CAPS_RUN``). The
dimension words, the view and the field names are closed vocabularies -- a word
the page draws that is not one of them is COUNTED, never returned. Rulings:
PEOPLE-DATA-MITIGATIONS (bounded, declared fields, never stored),
NAMES-AT-RUNTIME, D6-CAPABILITY-OVER-AFFORDANCE.

## READ THE DENOMINATORS BEFORE BELIEVING AN EMPTY READ

``readable`` is False when neither a follower count nor an entry was read.
``denominators`` then says which step found nothing: no label, no nav, a nav
with no word this module knows, progressbars whose entry was not paired.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Optional

from .config import BASE_URL
from .shape import CENSUS_OPAQUE, CENSUS_REDACTED, census_redact_rare, census_shape

AUDIENCE_URL = f"{BASE_URL}/analytics/creator/audience/"

#: The six demographic dimensions, in LinkedIn's own words (MEASURED by keyed
#: hash on the capture: each drawn twice, once as a tab and once as an entry's
#: dimension word).
DIMENSIONS: tuple[str, ...] = (
    "Job title", "Location", "Seniority", "Company", "Industry", "Company size",
)

#: The view word the nav's current button draws on the first render.
VIEW_ALL = "All"

#: Every word the demographics nav may draw that this module returns.
TAB_WORDS: tuple[str, ...] = (VIEW_ALL,) + DIMENSIONS

#: The label beside the follower count.
TOTAL_LABEL = "Total followers"

#: Bounds: a page that draws more than this is read this far and says so.
MAX_NAVS = 10
MAX_TABS = 20
MAX_ENTRIES = 50

#: A text longer than this is not a word of these vocabularies.
MAX_TEXT_CHARS = 200

#: What each read step saw, so an empty read says which step found nothing.
DENOMINATORS: tuple[str, ...] = (
    "total_labels_seen", "navs_matched", "tabs_seen", "tabs_unrecognised",
    "progressbars_seen", "entries_read", "entries_unrecognised_dimension",
    "entries_unpaired",
)

#: Why a follower count is absent. Closed: a failed read counts as nothing
#: seen, so it reads ``absent`` rather than naming a failure it cannot tell
#: apart from an empty page.
TOTAL_WHY = ("absent", "ambiguous", "not-an-integer")

#: Why the view is absent. Closed.
VIEW_WHY = ("no-demographics-nav", "ambiguous-nav", "no-current-tab", "several-current-tabs")

ROUTE = (
    "The follower count beside LinkedIn's 'Total followers' label; the "
    "dimension words on the demographics nav's buttons, the view being the "
    "one aria-current marks; one entry per progressbar inside that nav's "
    "container, its dimension word above it and its label paired with an "
    "'N%' share. Labels are census shapes, redacted when rare. No press, so "
    "a dimension's own list is listed in lists_unread, never read."
)

_INTEGER = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+|[0-9]{1,12}")
_SHARE = re.compile(r"([0-9]{1,3})%")
_DIMENSION_NAME = re.compile("^(?:" + "|".join(re.escape(d) for d in DIMENSIONS) + ")$")


# ---------------------------------------------------------------------------
# The pure half: strings in, closed vocabulary and integers out.
# ---------------------------------------------------------------------------


def normalise(text: Any) -> str:
    """Whitespace collapsed; ``""`` for a non-string or an over-long one."""
    if not isinstance(text, str) or len(text) > MAX_TEXT_CHARS * 4:
        return ""
    flat = " ".join(str.split(text))
    return flat if len(flat) <= MAX_TEXT_CHARS else ""


def classify(text: Any, vocabulary: tuple[str, ...]) -> Optional[str]:
    """The vocabulary's OWN constant equal to the text, else None. The page's
    string is never returned -- the constant is."""
    flat = normalise(text)
    return next((word for word in vocabulary if word == flat), None)


def parse_total(parent_text: Any) -> tuple[Optional[int], Optional[str]]:
    """The integer beside :data:`TOTAL_LABEL` in its parent's text, and why not.

    The parent must hold the label and exactly one integer beside it; anything
    else is ``not-an-integer``. Nothing of the text is ever in the answer.
    """
    flat = normalise(parent_text)
    if TOTAL_LABEL not in flat:
        return None, "not-an-integer"
    rest = flat.replace(TOTAL_LABEL, " ", 1).strip()
    if not _INTEGER.fullmatch(rest):
        return None, "not-an-integer"
    return int(rest.replace(",", "")), None


def parse_share(text: Any) -> Optional[int]:
    """``N%`` with N in 0..100 as an int, else None."""
    match = _SHARE.fullmatch(normalise(text))
    if match is None:
        return None
    value = int(match.group(1))
    return value if value <= 100 else None


def pair(texts: list[Any]) -> tuple[Optional[str], Optional[int]]:
    """(label text, share) from an entry's two texts: the share is the ONE
    that reads ``N%``, the label the other. Anything else pairs nothing."""
    if len(texts) != 2:
        return None, None
    shares = [parse_share(t) for t in texts]
    found = [i for i, s in enumerate(shares) if s is not None]
    if len(found) != 1:
        return None, None
    label = texts[1 - found[0]]
    return (str(label) if isinstance(label, str) else ""), shares[found[0]]


def shape_labels(labels: list[str]) -> tuple[list[str], dict[str, int]]:
    """Each label as ``census_redact_rare(census_shape(label), count)``.

    ``count`` is the number of labels in THIS list with the same shape: the
    surface the shapes were seen on is this read. Returns the shapes and how
    many were redacted, opaque or empty.
    """
    shapes = [census_shape(label) for label in labels]
    tally = Counter(shapes)
    out = [census_redact_rare(s, tally[s]) for s in shapes]
    counts = {
        "labels_redacted": sum(1 for s, o in zip(shapes, out) if CENSUS_REDACTED in o and o != s),
        "labels_opaque": sum(1 for o in out if o == CENSUS_OPAQUE),
        "labels_empty": sum(1 for o in out if o == ""),
    }
    return out, counts


def assemble(
    total: Optional[int],
    total_why: Optional[str],
    tabs: list[str],
    view: Optional[str],
    view_why: Optional[str],
    drawn: list[tuple[str, str, int]],
    denominators: dict[str, int],
) -> dict[str, Any]:
    """The reading, from closed words, integers and raw entry labels; the labels
    are shaped here and nowhere else."""
    labels, label_counts = shape_labels([label for _, label, _ in drawn])
    entries = [
        {"dimension": word, "label": shaped, "share_percent": share}
        for (word, _, share), shaped in zip(drawn, labels)
    ]
    dimensions = [w for w in tabs if w in DIMENSIONS]
    with_entry = {word for word, _, _ in drawn}
    return {
        "total_followers": total,
        "total_followers_why": total_why,
        "view": view,
        "view_why": view_why,
        "dimensions": dimensions,
        "entries": entries,
        "dimensions_drawn": [d for d in DIMENSIONS if d in with_entry],
        "dimensions_unread": [d for d in dimensions if d not in with_entry],
        "lists_unread": [d for d in dimensions if d != view],
        "denominators": {**denominators, **label_counts},
        "readable": total is not None or bool(entries),
        "route": ROUTE,
    }


# ---------------------------------------------------------------------------
# The impure half: one already-open page, read by role, words and structure.
# ---------------------------------------------------------------------------


async def _count(locator: Any) -> int:
    try:
        return int(await locator.count())
    except Exception:  # noqa: BLE001 -- a failed count is zero, never page text
        return 0


async def _text(locator: Any) -> str:
    try:
        value = await locator.inner_text()
    except Exception:  # noqa: BLE001
        return ""
    return value if isinstance(value, str) else ""


async def _attribute(locator: Any, name: str) -> str:
    try:
        value = await locator.get_attribute(name)
    except Exception:  # noqa: BLE001
        return ""
    return value if isinstance(value, str) else ""


async def _read_total(doc: Any, tally: dict[str, int]) -> tuple[Optional[int], Optional[str]]:
    labels = doc.get_by_text(TOTAL_LABEL, exact=True)
    seen = await _count(labels)
    tally["total_labels_seen"] = seen
    if seen == 0:
        return None, "absent"
    if seen > 1:
        return None, "ambiguous"
    return parse_total(await _text(labels.first.locator("xpath=..")))


async def _read_nav(doc: Any, tally: dict[str, int]) -> tuple[Any, list[str], Optional[str], Optional[str]]:
    """(entry scope, tab words, view, why no view) from the demographics nav:
    the one ``nav`` holding a button NAMED by a dimension word."""
    navs = doc.locator("nav").filter(has=doc.get_by_role("button", name=_DIMENSION_NAME))
    found = await _count(navs)
    tally["navs_matched"] = min(found, MAX_NAVS)
    if found == 0:
        return None, [], None, "no-demographics-nav"
    if found > 1:
        return None, [], None, "ambiguous-nav"
    nav = navs.first
    buttons = nav.get_by_role("button")
    total = await _count(buttons)
    tally["tabs_seen"] = min(total, MAX_TABS)
    tabs: list[str] = []
    current: list[str] = []
    unrecognised = 0
    for index in range(min(total, MAX_TABS)):
        button = buttons.nth(index)
        word = classify(await _text(button), TAB_WORDS)
        if word is None:
            unrecognised += 1
            continue
        tabs.append(word)
        if normalise(await _attribute(button, "aria-current")) == "true":
            current.append(word)
    tally["tabs_unrecognised"] = unrecognised
    scope = nav.locator("xpath=ancestor::div[.//*[@role='progressbar']][1]")
    if len(current) == 1:
        return scope, tabs, current[0], None
    return scope, tabs, None, ("no-current-tab" if not current else "several-current-tabs")


async def _read_entries(scope: Any, tally: dict[str, int]) -> list[tuple[str, str, int]]:
    drawn: list[tuple[str, str, int]] = []
    if scope is None:
        return drawn
    bars = scope.get_by_role("progressbar")
    total = await _count(bars)
    tally["progressbars_seen"] = min(total, MAX_ENTRIES)
    for index in range(min(total, MAX_ENTRIES)):
        entry = bars.nth(index).locator("xpath=ancestor::div[p][1]")
        heads = entry.locator("xpath=./p")
        if await _count(heads) != 1:
            tally["entries_unpaired"] += 1
            continue
        word = classify(await _text(heads.first), DIMENSIONS)
        if word is None:
            tally["entries_unrecognised_dimension"] += 1
            continue
        cells = entry.locator("xpath=./div/p")
        if await _count(cells) != 2:
            tally["entries_unpaired"] += 1
            continue
        label, share = pair([await _text(cells.nth(0)), await _text(cells.nth(1))])
        if label is None or share is None:
            tally["entries_unpaired"] += 1
            continue
        drawn.append((word, label, share))
    tally["entries_read"] = len(drawn)
    return drawn


async def read_audience_analytics(page: Any) -> dict[str, Any]:
    """The follower count and the demographics the first render draws.

    The page must already be at :data:`AUDIENCE_URL`; navigation is the
    caller's. Reads attributes and text only: no press, no scroll.
    """
    tally: dict[str, int] = dict.fromkeys(DENOMINATORS, 0)
    total, total_why = await _read_total(page, tally)
    scope, tabs, view, view_why = await _read_nav(page, tally)
    drawn = await _read_entries(scope, tally)
    return assemble(total, total_why, tabs, view, view_why, drawn, tally)
