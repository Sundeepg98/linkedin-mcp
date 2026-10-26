"""Read an organisation People tab's INSIGHT CARDS: categories and counts, never people.

Census row ``J 108`` -- *Company Page People tab (titles, study areas, skills,
how you are connected)*. Under the WHO/WHICH rule as extended by lane S's
follow-up (item 3), those four facets are the People tab's insight
DISTRIBUTIONS: an aggregate, which a reader delivers without saying who anyone
is. The address, ``/company/<numeric id>/people/``, is admitted by
``MEMBER-ROSTERS-AS-BOUNDED-READS`` and composed only by
``member_rosters.compose("company_people", <id>)``.

## WHAT IT IS BUILT ON -- REAL CAPTURED MARKUP, MEASURED

The live lane's session-2 capture of one organisation's People tab
(2026-09-28), committed as ``tests/fixtures/live2/company_people.html`` and,
with the carousel's words measured, as
``tests/fixtures/live2/company_people_insights.html``
(``scripts/_build_company_people_insights_skeleton.py``). Measured there by
hashing candidate LinkedIn words with the session's key against the keyed
skeleton (2026-10-10, lane B4):

* one carousel of SIX cards, each an ``li`` whose ``h3`` is one of
  :data:`CARDS`' headings, all drawn on load;
* each card's rows are ``a[role="checkbox"]`` links to the People tab with
  ONE ``facet...`` query parameter -- the card's own, also in :data:`CARDS`;
* each row draws two paragraphs: the LABEL (letters) then the COUNT (digits,
  with a thousands separator from four digits up);
* the connection card's rows are DEGREE WORDS -- ``3rd+`` and ``2nd`` were
  drawn -- with counts. Not people.

## THE PAGE IS READ IN DOCUMENT ORDER, AND ATTRIBUTION IS CHECKED

:data:`CARD_PARTS` asks for every ``h3`` and every facet row at once, which
Playwright answers in document order. A heading opens a card and the rows
after it are that card's -- and a row is kept ONLY when its own facet
parameter is the one the heading's card is measured to carry. So a row the
document order misattributes is withheld and counted, never filed under the
wrong facet. (``company_root`` is this repository's record of a count that
was consistent, plausible and not attributable; this check is that lesson.)

## WHAT LEAVES, AND HOW

* A KNOWN card -- its heading in :data:`CARDS`, compared whole after its
  white space is collapsed -- comes back as its facet key and LinkedIn's
  heading, both THIS MODULE'S constants, with up to :data:`ROWS_PER_CARD`
  rows. A card whose heading is not in the vocabulary, or a second card with
  a heading already seen, is COUNTED and never returned: its label text is
  not even read.
* A row's LABEL leaves only as a ``people_data.Category`` record -- sanitised
  by ``people_data.sanitise``, capped at ``people_data.CAPS["label"]`` with a
  ``label_truncated`` flag, marked as a third party's words.
* A row's COUNT is an integer read from plain or grouped digits; anything
  else -- an abbreviation, a decimal, a percentage, a word -- withholds the
  row and is tallied by its shape, NEVER rounded and never quoted.
* THE CONNECTION CARD IS WHO-SAFE BY CONSTRUCTION. Its rows come back as
  ``{"degree": <one of people_data.DEGREES>, "count": n}`` and nothing else:
  a label there that is not exactly a degree word -- a name, if LinkedIn ever
  drew one -- is withheld and counted as ``not_a_degree``, and no record is
  built for it. So the facet the census flagged as possibly WHO can only ever
  leave as counts.

Nothing read off the page is logged, stored, or put into an exception: every
read is wrapped, a failure is COUNTED under ``reads_failed`` and its message
is dropped (a Playwright error can quote the element it failed on).

## IT OPENS NOTHING AND PRESSES NOTHING

:func:`read_people_insights` reads the page it is handed: no navigation, no
scroll, no press -- the toggles ("Filter by ...") and the carousel's "Next"
are never touched; all six cards are in the document on load. The one tool
that loads the page, ``server.linkedin_company_people_insights``, loads ONE.
"""

from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import people_data

#: ``(facet key, LinkedIn's heading, the facet query parameter its rows carry)``.
#: MEASURED 2026-10-10 on the session-2 capture (lane B4's report, section 1):
#: every heading and parameter here was drawn, and nothing else was.
#: UNMEASURED and therefore ABSENT: the apostrophe spellings ("What they're
#: skilled at", "How you're connected") -- hashed, not drawn on that capture.
CARDS: tuple[tuple[str, str, str], ...] = (
    ("where_they_live", "Where they live", "facetGeoRegion"),
    ("where_they_studied", "Where they studied", "facetSchool"),
    ("what_they_do", "What they do", "facetCurrentFunction"),
    ("what_they_are_skilled_at", "What they are skilled at", "facetSkills"),
    ("what_they_studied", "What they studied", "facetEducation"),
    ("how_you_are_connected", "How you are connected", "facetConnection"),
)

#: The card whose rows are connection degrees, returned as degree words only.
CONNECTION_CARD = "how_you_are_connected"

#: Every card heading and every facet row, in document order. A heading is the
#: one part with no ``href``.
CARD_PARTS = 'h3, a[role="checkbox"][href*="/people/?facet"]'

#: A row's paragraphs: the label, then the count.
PARAGRAPHS = "p"

#: THE BOUNDS. Rows kept per card: twice the five LinkedIn drew per card.
#: Parts read at most: the capture's headings and 27 rows with room to
#: spare. A label's characters considered before sanitising: four caps' worth.
ROWS_PER_CARD = 10
MAX_PARTS = 120
LABEL_READ_CAP = 4 * people_data.CAPS["label"]

#: Milliseconds any one read may wait. Playwright waits 30 s by default for an
#: element that is gone, and a row can vanish between the count and its read.
READ_TIMEOUT_MS = 2000

#: How a count's text is classified. Position 0 is a refusal, so a value that
#: lands on the default carries no number. Only the two digit shapes carry one.
COUNT_SHAPES: tuple[str, ...] = (
    "not_a_count",
    "plain_digits",
    "grouped_digits",
    "abbreviated_refused",
    "decimal_refused",
    "percent_refused",
    "too_long_refused",
)

#: Why a row of a KNOWN card was withheld. Closed.
ROW_REFUSALS: tuple[str, ...] = (
    "facet_parameter_disagrees",
    "no_label_and_count",
    "label_empty",
    "not_a_degree",
    "count_refused",
)

_HEADING_TO_CARD = {heading: (key, heading, facet) for key, heading, facet in CARDS}
_PLAIN = re.compile(r"[0-9]{1,9}")
_GROUPED = re.compile(r"[0-9]{1,3}(?:,[0-9]{3}){1,2}")
_ABBREVIATED = re.compile(r"[0-9][0-9.,]*\s?[KkMmBb]\+?")
_DECIMAL = re.compile(r"[0-9]+\.[0-9]+")
_PERCENT = re.compile(r"[0-9][0-9.,]*\s?%")
_LONG = re.compile(r"[0-9]{10,}")


def collapsed(text: Any) -> str:
    """White space collapsed and the ends trimmed; ``""`` for a non-string."""
    return " ".join(text.split()) if isinstance(text, str) else ""


def count_of(text: Any) -> tuple[str, Optional[int]]:
    """``(shape, value)`` for a count's text; ``value`` only for digit shapes.

    PURE, NEVER RAISES, NEVER QUOTES: ``int()`` is called only on a string
    the patterns above have already proven is ASCII digits.
    """
    value = collapsed(text)
    if _PLAIN.fullmatch(value):
        return "plain_digits", int(value)
    if _GROUPED.fullmatch(value):
        return "grouped_digits", int(value.replace(",", ""))
    if _LONG.fullmatch(value):
        return "too_long_refused", None
    if _ABBREVIATED.fullmatch(value):
        return "abbreviated_refused", None
    if _PERCENT.fullmatch(value):
        return "percent_refused", None
    if _DECIMAL.fullmatch(value):
        return "decimal_refused", None
    return "not_a_count", None


def facet_parameter(href: Any) -> Optional[str]:
    """The ONE ``facet...`` query parameter NAME of a People-tab address, or
    ``None``. The value is never read; the name is compared against
    :data:`CARDS` and never returned."""
    if not isinstance(href, str):
        return None
    try:
        parts = urlsplit(href)
    except ValueError:
        return None
    if not re.fullmatch(r"/(?:company|school)/[^/]+/people/", parts.path or ""):
        return None
    names = [pair.partition("=")[0] for pair in (parts.query or "").split("&") if pair]
    facets = [name for name in names if name.startswith("facet")]
    return facets[0] if len(facets) == 1 else None


#: An organisation's People tab, by number or by the slug LinkedIn
#: canonicalises a number to; nothing after ``people/`` but a query.
_PEOPLE_TAB = re.compile(r"/company/[^/?#]{1,200}/people/?")
_LINKEDIN_HOSTS = ("www.linkedin.com", "linkedin.com")


def landed_on_a_people_tab(landed: Any) -> bool:
    """Whether a navigation LANDED on an organisation's People tab.

    THE LANDING MAY VETO, NEVER SUPPLY: this answers a yes or a no about where
    the one load went, and nothing it reads becomes an address, an argument or
    a returned value. LinkedIn serves the numeric address by redirecting to
    the slug form, so both are a People tab; a landing anywhere else -- the
    Page root, an unavailable-organisation page, the feed -- is not, and the
    page is then not read at all.
    """
    if not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    if parts.scheme != "https" or parts.netloc.lower() not in _LINKEDIN_HOSTS:
        return False
    return bool(_PEOPLE_TAB.fullmatch(parts.path or "")) and not parts.path.startswith(
        "/company/unavailable/"
    )


class _Card:
    def __init__(self, entry: Optional[tuple[str, str, str]]) -> None:
        self.entry = entry
        self.rows: list[dict[str, Any]] = []
        self.rows_seen = 0
        self.rows_beyond_bound = 0
        self.refused = {reason: 0 for reason in ROW_REFUSALS}
        self.count_shapes_refused = {shape: 0 for shape in COUNT_SHAPES if shape not in
                                     ("plain_digits", "grouped_digits")}


async def _attribute(part: Any, name: str, failed: list[int]) -> Optional[str]:
    try:
        value = await part.get_attribute(name, timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def _text(part: Any, failed: list[int]) -> Optional[str]:
    try:
        value = await part.inner_text(timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _read_row(card: _Card, part: Any, href: str, failed: list[int]) -> None:
    key, _heading, facet = card.entry  # type: ignore[misc]
    if facet_parameter(href) != facet:
        card.refused["facet_parameter_disagrees"] += 1
        return
    paragraphs = part.locator(PARAGRAPHS)
    if await _count(paragraphs, failed) < 2:
        card.refused["no_label_and_count"] += 1
        return
    label_text = await _text(paragraphs.nth(0), failed)
    count_text = await _text(paragraphs.nth(1), failed)
    if label_text is None or count_text is None:
        card.refused["no_label_and_count"] += 1
        return
    shape, value = count_of(count_text)
    if value is None:
        card.refused["count_refused"] += 1
        card.count_shapes_refused[shape] += 1
        return
    if key == CONNECTION_CARD:
        degree = people_data.sanitise(label_text[:LABEL_READ_CAP], cap=8)
        if degree not in people_data.DEGREES:
            card.refused["not_a_degree"] += 1
            return
        card.rows.append({"degree": degree, "count": value})
        return
    bounded = label_text[:LABEL_READ_CAP]
    whole = people_data.sanitise(bounded, cap=LABEL_READ_CAP)
    record = people_data.Category.from_page(label=bounded)
    if record is None:
        card.refused["label_empty"] += 1
        return
    card.rows.append({
        "label": record.envelope(),
        "label_truncated": len(label_text) > LABEL_READ_CAP or len(whole) > people_data.CAPS["label"],
        "count": value,
    })


async def read_people_insights(page: Any) -> dict[str, Any]:
    """The insight cards on the People tab ``page`` already shows.

    Returns ``cards`` -- one entry per KNOWN card, in page order -- and the
    counters that say what else was there. Never raises on page content.
    """
    failed = [0]
    parts = page.locator(CARD_PARTS)
    total = await _count(parts, failed)
    cards: list[_Card] = []
    current: Optional[_Card] = None
    seen: set[str] = set()
    tallies = {
        "headings_unrecognised": 0,
        "headings_repeated": 0,
        "rows_in_unreturned_cards": 0,
        "rows_before_any_heading": 0,
    }
    for index in range(min(total, MAX_PARTS)):
        part = parts.nth(index)
        href = await _attribute(part, "href", failed)
        if href is None:
            entry = _HEADING_TO_CARD.get(collapsed(await _text(part, failed)))
            if entry is None:
                tallies["headings_unrecognised"] += 1
                current = _Card(None)
            elif entry[0] in seen:
                tallies["headings_repeated"] += 1
                current = _Card(None)
            else:
                seen.add(entry[0])
                current = _Card(entry)
                cards.append(current)
            continue
        if current is None:
            tallies["rows_before_any_heading"] += 1
            continue
        current.rows_seen += 1
        if current.entry is None:
            tallies["rows_in_unreturned_cards"] += 1
            continue
        if len(current.rows) >= ROWS_PER_CARD:
            current.rows_beyond_bound += 1
            continue
        await _read_row(current, part, href, failed)

    out_cards = []
    for card in cards:
        key, heading, _facet = card.entry  # type: ignore[misc]
        out_cards.append({
            "facet": key,
            "heading": heading,
            "rows": card.rows,
            "rows_seen": card.rows_seen,
            "rows_beyond_bound": card.rows_beyond_bound,
            "truncated": card.rows_beyond_bound > 0,
            "rows_withheld": dict(card.refused),
            "counts_refused_by_shape": dict(card.count_shapes_refused),
        })
    parts_beyond_bound = max(0, total - MAX_PARTS)
    return {
        "cards": out_cards,
        "cards_returned": len(out_cards),
        "card_vocabulary": [key for key, _heading, _facet in CARDS],
        "parts_seen": total,
        "parts_beyond_bound": parts_beyond_bound,
        "truncated": parts_beyond_bound > 0 or any(c["truncated"] for c in out_cards),
        "bounds": {
            "rows_per_card": ROWS_PER_CARD,
            "parts": MAX_PARTS,
            "label_characters": people_data.CAPS["label"],
        },
        "reads_failed": failed[0],
        **tallies,
    }
