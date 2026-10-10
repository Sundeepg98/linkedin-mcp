"""VIEWER DEMOGRAPHICS of one of his posts, off its per-post analytics page. Census row ``M C38``.

The page is ``/analytics/post-summary/urn:li:activity:<digits>/``, admitted on
the read allowlist with an obligation stated on its own line: the page reports
viewer demographics -- other people, aggregated -- so a reader owes
``census_shape`` plus ``census_redact_rare``. This module is that reader. The
impressions half of ``M C38`` is read elsewhere (``P G6``,
``linkedin_creator_analytics``'s ``per_post``).

## WHAT THE PAGE DRAWS, MEASURED (lane B3, 2026-10-10)

On the live lane's session-1 capture (2026-09-23; the tracked skeleton is
``tests/fixtures/live1/post_summary.html``), one card, by LinkedIn's words::

    "Top demographics"                       the card's title, drawn once
    nav: 7 buttons                           "All" (aria-current="true"), then
                                             the six CATEGORY words
    5 rows, each:
      p     a category word                  e.g. "Seniority"
      div   p  the VALUE                     a job title, a location, ... of
            p  the PERCENTAGE "<n>%"         the people who viewed the post
      svg role=progressbar                   aria-valuenow = the same n,
                                             aria-valuemax = 100

No anchor and no member link inside the card. The page's OTHER card of people
-- a Premium list of members with Message and Follow controls -- is outside it
and nothing here selects it. Session 1's reading found nothing because it ran
the creator-analytics ``aria-label`` parser: these numbers are TEXT and
``aria-valuenow``, under words that vocabulary does not hold.

## SELECTION: STRUCTURE AND LINKEDIN'S FIXED WORDS, NEVER POSITION

The card is the nearest ancestor of the one :data:`CARD_TITLE` text that
holds a ``nav``. Tabs are that nav's buttons; a tab counts only if its text is
in the CLOSED vocabulary (:data:`CATEGORY_WORDS` plus :data:`ALL_TAB`). A row
is the nearest ancestor of a ``role=progressbar`` with a ``p`` child: exactly
one such ``p`` (the category, which must be in the vocabulary) and exactly
two ``p`` in its ``div`` -- the one whose text has the measured percentage
shape is the number, the other is the value. A row that does not hold exactly
that is counted in ``unparsed_rows``, never guessed at.

## WHAT LEAVES, AND WHAT NEVER DOES

Integers, booleans, LinkedIn's category words from the closed vocabulary, this
module's own sentence -- and each row's VALUE, ONLY as
:func:`shaped_value` returns it: ``shape.census_shape`` (urns, member and
entity paths and long digit runs substituted; anything over 60 characters or
outside a narrow ASCII alphabet becomes ``<opaque>``) and then
``shape.census_redact_rare`` AT COUNT ONE. The count is fixed at one on
purpose: that function separates furniture from a person by how often a shape
repeats, and a demographics panel draws each bucket once, so every value is
treated as the singleton it is and any run of two or more capitalised words
is ``<redacted>``. A value is never read for a row whose category is outside
the vocabulary.

**THE RESIDUAL GAP, STATED.** A value that is ONE capitalised word -- a
one-word location, company or industry -- survives the redactor, exactly as
``shape.census_redact_rare`` documents for itself. It is a bucket's name over
his post's viewers, never a viewer: the page draws no viewer here.

## THE ZERO, AND READABLE (the creator-analytics semantics)

    points_found 0   no row parsed into a category and a percentage. NOT
                     "no viewers": the demographics are UNMEASURED.
    points_found >0  the rows are a reading.

``readable`` is ``points_found > 0``. ``labels_seen`` (rows drawn) beside it
separates a page that drew no card from one whose numbers stopped parsing: the
tracked skeleton reads ``labels_seen`` 5 and ``points_found`` 0, because its
numbers are ``x``. ``percent_disagreements`` counts a row whose text and
progressbar disagree; such a row is not a point.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from . import shape
from .config import BASE_URL

#: The page, for ONE activity urn the caller names. The allowlist admits
#: exactly this form: ``urn:li:activity:`` and one to twenty ASCII digits.
POST_SUMMARY_TEMPLATE = f"{BASE_URL}/analytics/post-summary/{{urn}}/"

#: The caller's key, closed: the one urn family the allowlist admits.
ACTIVITY_URN = re.compile(r"^urn:li:activity:[0-9]{1,20}$")

#: LinkedIn's title over the card, measured once on the capture.
CARD_TITLE = "Top demographics"

#: The card's first tab, ``aria-current`` on the capture.
ALL_TAB = "All"

#: The six category words, CLOSED, in the order the capture's tabs draw them.
CATEGORY_WORDS: tuple[str, ...] = (
    "Job title", "Location", "Seniority", "Company", "Industry", "Company size",
)

#: The closed alphabet of tab words.
TAB_WORDS: frozenset[str] = frozenset(CATEGORY_WORDS) | {ALL_TAB}

CARD_XPATH = "xpath=ancestor::div[.//nav][1]"
TAB_SELECTOR = "nav button"
BAR_SELECTOR = '[role="progressbar"]'
ROW_XPATH = "xpath=ancestor::div[p][1]"
CATEGORY_XPATH = "xpath=./p"
PAIR_XPATH = "xpath=./div/p"

#: Bounds: the capture draws 7 tabs and 5 rows.
MAX_TABS = 12
MAX_ROWS = 12
MAX_TEXT_CHARS = 120

#: The measured percentage: one to three ASCII digits and a percent sign.
_PERCENT = re.compile(r"^\s*([0-9]{1,3})\s*%\s*$")
_DIGITS = re.compile(r"^\s*([0-9]{1,3})\s*$")

ROUTE = (
    "the 'Top demographics' card of the per-post analytics page: category "
    "words from its tabs and rows, each row's percentage from its text, "
    "checked against its progressbar, and each value only as census_shape "
    "then census_redact_rare at count one. If points_found is 0 while "
    "labels_seen is not, the card drew but its numbers did not parse."
)


def address_for(urn: Optional[str]) -> Optional[str]:
    """The per-post page for the CALLER's activity urn, or None. PURE.

    PAGE-MAY-VETO-NEVER-SUPPLY: the urn is the caller's argument, checked
    against a closed shape; nothing read off a page composes this address.
    """
    if not isinstance(urn, str) or not ACTIVITY_URN.match(urn):
        return None
    return POST_SUMMARY_TEMPLATE.format(urn=urn)


def percent_of(text: Optional[str]) -> Optional[int]:
    """A drawn percentage ``"<n>%"`` -> n in 0..100, or None. PURE; never raises."""
    if not isinstance(text, str) or len(text) > MAX_TEXT_CHARS:
        return None
    found = _PERCENT.match(text)
    if found is None:
        return None
    value = int(found.group(1))
    return value if value <= 100 else None


def _valuenow(text: Optional[str]) -> Optional[int]:
    if not isinstance(text, str) or len(text) > MAX_TEXT_CHARS:
        return None
    found = _DIGITS.match(text)
    if found is None:
        return None
    value = int(found.group(1))
    return value if value <= 100 else None


def shaped_value(text: Optional[str]) -> str:
    """A row's value as it may leave: census_shape, then census_redact_rare at
    count one. PURE. See the module docstring for why the count is one."""
    return shape.census_redact_rare(shape.census_shape(text), 1)


def _word(text: Optional[str]) -> Optional[str]:
    """A tab or category text, if it is one of LinkedIn's closed words."""
    if not isinstance(text, str) or len(text) > MAX_TEXT_CHARS:
        return None
    cleaned = " ".join(text.split())
    return cleaned if cleaned in TAB_WORDS else None


async def _count(locator: Any) -> int:
    try:
        return max(0, int(await locator.count()))
    except Exception:  # noqa: BLE001 -- a failed count is zero, never raised
        return 0


async def _text(locator: Any) -> Optional[str]:
    try:
        value = await locator.inner_text()
    except Exception:  # noqa: BLE001
        return None
    return value if isinstance(value, str) else None


async def _row(bar: Any) -> tuple[str, Optional[dict[str, Any]]]:
    """One progressbar's row -> (verdict, row). Verdicts: ``point``,
    ``unrecognised``, ``unparsed``, ``disagreement``."""
    row = bar.locator(ROW_XPATH)
    if await _count(row) != 1:
        return "unparsed", None
    categories = row.locator(CATEGORY_XPATH)
    if await _count(categories) != 1:
        return "unparsed", None
    category = _word(await _text(categories))
    if category is None or category == ALL_TAB:
        return "unrecognised", None
    pair = row.locator(PAIR_XPATH)
    if await _count(pair) != 2:
        return "unparsed", None
    texts = [await _text(pair.nth(0)), await _text(pair.nth(1))]
    percents = [percent_of(text) for text in texts]
    if sum(value is not None for value in percents) != 1:
        return "unparsed", None
    which = 0 if percents[0] is not None else 1
    percent = percents[which]
    try:
        drawn = _valuenow(await bar.get_attribute("aria-valuenow"))
    except Exception:  # noqa: BLE001
        drawn = None
    if drawn is not None and drawn != percent:
        return "disagreement", None
    return "point", {
        "category": category,
        "value": shaped_value(texts[1 - which]),
        "percent": percent,
    }


async def read_post_viewer_demographics(page: Any) -> dict[str, Any]:
    """The reading, off the already-open per-post analytics page.

    Takes no url; navigates nowhere. Locator reads only -- ``count``,
    ``inner_text``, ``get_attribute`` -- so no script is injected. A locator
    call that fails is counted, never raised.
    """
    reading: dict[str, Any] = {
        "readable": False,
        "points_found": 0,
        "labels_seen": 0,
        "card_found": False,
        "categories": [],
        "selected": None,
        "rows": [],
        "unrecognised_tabs": 0,
        "unrecognised_categories": 0,
        "unparsed_rows": 0,
        "percent_disagreements": 0,
        "rows_beyond_bound": 0,
        "route": ROUTE,
    }
    title = page.locator("main").get_by_text(CARD_TITLE, exact=True)
    if await _count(title) != 1:
        return reading
    card = title.locator(CARD_XPATH)
    if await _count(card) != 1:
        return reading
    reading["card_found"] = True

    tabs = card.locator(TAB_SELECTOR)
    categories: list[str] = []
    for index in range(min(await _count(tabs), MAX_TABS)):
        tab = tabs.nth(index)
        word = _word(await _text(tab))
        if word is None:
            reading["unrecognised_tabs"] += 1
            continue
        try:
            current = await tab.get_attribute("aria-current")
        except Exception:  # noqa: BLE001
            current = None
        if current == "true" and reading["selected"] is None:
            reading["selected"] = word
        if word != ALL_TAB and word not in categories:
            categories.append(word)
    reading["categories"] = categories

    bars = card.locator(BAR_SELECTOR)
    total = await _count(bars)
    reading["labels_seen"] = total
    reading["rows_beyond_bound"] = max(0, total - MAX_ROWS)
    rows: list[dict[str, Any]] = []
    for index in range(min(total, MAX_ROWS)):
        verdict, row = await _row(bars.nth(index))
        if verdict == "point" and row is not None:
            rows.append(row)
        elif verdict == "unrecognised":
            reading["unrecognised_categories"] += 1
        elif verdict == "disagreement":
            reading["percent_disagreements"] += 1
        else:
            reading["unparsed_rows"] += 1
    reading["rows"] = rows
    reading["points_found"] = len(rows)
    reading["readable"] = len(rows) > 0
    return reading
