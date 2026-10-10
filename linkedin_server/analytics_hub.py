"""His ANALYTICS HUB (``/dashboard/``): the four metric cards, as integers and closed words.

Census row ``P L8``, *Analytics and tools hub*. The address is admitted,
anchored, in ``readonly.py`` (lane L1, 2026-09-23), and the live lane's
session 1 captured it the same night (``_audit/2026-09-23-live-lane-session-1.md``,
Entry 5). This module is written against that capture's tracked skeleton,
``tests/fixtures/live1/overview.html``.

## WHAT THE PAGE DRAWS, MEASURED ON THE CAPTURE

``main`` holds an analytics nav (``Overview`` current, then the content and
audience analytics links) and ONE ``section``. Inside it, under LinkedIn's
heading ``Track performance``, FOUR metric cards. Each card is ONE link whose
address is an analytics page, holding exactly four ``p`` texts and, beside the
delta, a direction icon::

    /analytics/creator/content/      Post impressions in 7 days    vs. prior 7 days
    /analytics/creator/audience/     Total followers               vs. prior 7 days
    /analytics/profile-views/        Profile viewers in 90 days    vs. prior 7 days
    /analytics/search-appearances/   Search appearances <Mon d-d>  vs. <Mon d-d>

Each card's other two texts are a value (ASCII digits) and a delta (``<n>%``).
The icon is an ``svg`` whose id is LinkedIn's icon name: ``caret-up-small``
(its geometry measured pointing UP) or ``caret-small`` (DOWN); the
search-appearances card drew none. The page ALSO draws his profile card -- his
name and headline -- in an ``aside`` inside ``main``, outside the section.
This reader never reads it: every selector here is scoped to ``main section``.

## HOW A CARD IS KNOWN: TWO CLOSED VOCABULARIES THAT MUST AGREE

A card is identified by its LINK's analytics path words AND by its LABEL --
never by its position on the page (NO-INDEX-PINNED-JUDGEMENTS). The address
alone would accept a card LinkedIn relabelled into something else; the label
alone would accept a sentence that only resembles one. So:

* a link whose address is not under ``/analytics/`` is NOT A CARD
  (``links_not_cards``);
* an analytics link outside the four addresses is a card nobody named
  (``paths_unrecognised``), counted and not returned;
* a card whose label is outside :data:`LABELS` and the one dated grammar, or
  names a different metric than its address, is ``labels_unrecognised`` --
  counted, never returned, and its text goes nowhere.

## WHAT COMES BACK, AND WHY NOTHING ELSE CAN

Per metric: ``value`` (int or None), ``delta`` (the drawn percentage, signed
by the icon, int or None), ``direction`` (``increase`` / ``decrease`` /
``unchanged`` or None), ``window`` and ``period`` (closed words or None).
Then the denominators that make a zero readable: ``cards_seen``,
``cards_parsed``, ``labels_unrecognised``, ``paths_unrecognised``,
``links_seen``, ``links_not_cards``. **Integers, booleans, None and this
module's own words only** (:func:`emitted_alphabet`): a page string has no
field to land in, and no conversion here can raise -- digits are matched by an
anchored ASCII pattern BEFORE ``int()`` sees them.

A delta is signed only by an icon this module names. A non-zero delta drawn
with no icon, or with an icon it does not know, is ``None``: the magnitude
without its direction would be a claim the page did not make.

## WHAT IT CANNOT TELL YOU

``readable`` is False when no card parsed, and then every absence is about the
reader, not the account. The windows differ by card (7 days, 90 days, total,
one dated week), as LinkedIn draws them; nothing here re-bases them.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from . import coerce
from .config import BASE_URL

HUB_URL = f"{BASE_URL}/dashboard/"

#: Every link in the one metric section. Structure, not position.
LINK_SELECTOR = "main section a[href]"
#: A card's texts: the four ``p`` it draws.
TEXT_SELECTOR = "p"
#: A card's direction icon: an ``svg`` carrying LinkedIn's icon name as its id.
ICON_SELECTOR = "svg[id]"

#: Bounds, so a page drawing something unexpected cannot stream it in.
MAX_LINKS = 30
MAX_TEXTS = 8
MAX_ICONS = 4
MAX_TEXT_CHARS = 60

#: The four card addresses, by LinkedIn's own path words. CLOSED.
CARD_PATHS: dict[str, str] = {
    "/analytics/creator/content/": "post_impressions",
    "/analytics/creator/audience/": "followers",
    "/analytics/profile-views/": "profile_viewers",
    "/analytics/search-appearances/": "search_appearances",
}

#: LinkedIn's label words -> (metric, window). CLOSED; each measured on the
#: capture by keyed hash.
LABELS: dict[str, tuple[str, str]] = {
    "Post impressions in 7 days": ("post_impressions", "7_days"),
    "Total followers": ("followers", "total"),
    "Profile viewers in 90 days": ("profile_viewers", "90_days"),
}

#: LinkedIn's comparison phrase -> its closed name. Measured on three cards.
PERIODS: dict[str, str] = {
    "vs. prior 7 days": "vs_prior_7_days",
}

_EN_DASH = chr(0x2013)
_MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
#: A date range as the search-appearances card draws it: ``Mon d<EN DASH>d``
#: (measured). The second month is accepted for a range that crosses one --
#: UNVERIFIED, no capture shows it; without it the card would go unread for
#: the last days of every month.
_RANGE = _MONTH + r" [0-9]{1,2}" + _EN_DASH + r"(?:" + _MONTH + r" )?[0-9]{1,2}"
_DATED_LABEL = re.compile(r"^Search appearances " + _RANGE + r"$")
_DATED_PERIOD = re.compile(r"^vs\. " + _RANGE + r"$")

#: The value: ASCII digits -- a plain run, or grouped by thousands commas.
#: Anchored both ends. MEASURED: 2 and 3 plain digits on the capture; the
#: longer and grouped forms are LinkedIn's number format elsewhere, accepted
#: so a larger account does not read None. An abbreviation ("1.2K") reads None.
_VALUE = re.compile(r"^(?:[0-9]{1,9}|[0-9]{1,3}(?:,[0-9]{3}){1,3})$")
#: The delta, as drawn: ``<n>%``, no sign (the icon carries it).
_DELTA = re.compile(r"^(?P<n>[0-9]{1,4})%$")

#: LinkedIn's icon names -> the direction each draws (geometry measured on
#: the capture: ``caret-up-small`` wide at the bottom, ``caret-small`` wide at
#: the top). CLOSED: an icon not named here signs nothing.
DIRECTION_ICONS: dict[str, int] = {
    "caret-up-small": 1,
    "caret-small": -1,
}

DIRECTIONS = {1: "increase", -1: "decrease", 0: "unchanged"}

SCOPE = (
    "the metric cards on his analytics hub (/dashboard/): each card's value and "
    "its change as LinkedIn draws them, over the window its own label names. A "
    "card is returned only when its address and its label name the same metric; "
    "readable is False when no card parsed, and then nothing here is a reading "
    "about the account."
)


def _text(value: Any) -> Optional[str]:
    """A page text, whitespace-normalised and bounded, or None."""
    if not isinstance(value, str):
        return None
    text = " ".join(value.split())
    if not text or len(text) > MAX_TEXT_CHARS:
        return None
    return text


def _digits(text: str) -> int:
    """``text`` already matched an anchored ASCII-digit pattern; cannot raise."""
    return int(text.replace(",", ""))


def classify_href(href: Any) -> tuple[str, Optional[str]]:
    """``("card", metric)``, ``("card", None)`` for an analytics address
    outside the four, or ``("not_a_card", None)``. Never raises."""
    if not isinstance(href, str) or len(href) > 300:
        return ("not_a_card", None)
    try:
        parts = urlsplit(href.strip())
    except ValueError:
        return ("not_a_card", None)
    if parts.netloc not in ("", "www.linkedin.com") or parts.scheme not in ("", "https"):
        return ("not_a_card", None)
    path = parts.path if parts.path.endswith("/") else parts.path + "/"
    if not path.startswith("/analytics/"):
        return ("not_a_card", None)
    return ("card", CARD_PATHS.get(path))


def classify_label(text: Any) -> Optional[tuple[str, str]]:
    """``(metric, window)`` for a label in the closed vocabulary, else None."""
    text = _text(text)
    if text is None:
        return None
    if text in LABELS:
        return LABELS[text]
    if _DATED_LABEL.match(text):
        return ("search_appearances", "dated_range")
    return None


def classify_period(text: Any) -> Optional[str]:
    """The comparison phrase's closed name, else None."""
    text = _text(text)
    if text is None:
        return None
    if text in PERIODS:
        return PERIODS[text]
    if _DATED_PERIOD.match(text):
        return "vs_prior_dated_range"
    return None


def read_card(metric: str, texts: list[Any], icons: list[Any]) -> Optional[dict[str, Any]]:
    """One card's reading, or None when its label does not name ``metric``.

    PURE. ``texts`` are the card's ``p`` texts and ``icons`` its icon ids, in
    any order: each text is judged by its SHAPE (a closed label, a closed
    period, a value, a delta), never by where it stands. A role drawn twice
    is ambiguous and reads None.
    """
    labels, periods, values, deltas = [], [], [], []
    for raw in texts:
        text = _text(raw)
        if text is None:
            continue
        label = classify_label(text)
        period = classify_period(text)
        if label is not None:
            labels.append(label)
        elif period is not None:
            periods.append(period)
        elif _VALUE.match(text):
            values.append(_digits(text))
        else:
            match = _DELTA.match(text)
            if match:
                deltas.append(_digits(match.group("n")))
    if len(labels) != 1 or labels[0][0] != metric:
        return None
    signs = {DIRECTION_ICONS[i] for i in icons if isinstance(i, str) and i in DIRECTION_ICONS}
    magnitude = deltas[0] if len(deltas) == 1 else None
    if magnitude is None:
        delta, direction = None, None
    elif magnitude == 0:
        delta, direction = 0, DIRECTIONS[0]
    elif len(signs) == 1:
        sign = signs.pop()
        delta, direction = sign * magnitude, DIRECTIONS[sign]
    else:
        delta, direction = None, None
    return {
        "value": values[0] if len(values) == 1 else None,
        "delta": delta,
        "direction": direction,
        "window": labels[0][1],
        "period": periods[0] if len(periods) == 1 else None,
    }


def tally(cards: list[tuple[Any, list[Any], list[Any]]], links_seen: int) -> dict[str, Any]:
    """``(href, texts, icons)`` per link -> the reading. PURE."""
    metrics: dict[str, dict[str, Any]] = {}
    duplicated: set[str] = set()
    cards_seen = paths_unrecognised = labels_unrecognised = 0
    for href, texts, icons in cards:
        kind, metric = classify_href(href)
        if kind != "card":
            continue
        cards_seen += 1
        if metric is None:
            paths_unrecognised += 1
            continue
        reading = read_card(metric, texts, icons)
        if reading is None:
            labels_unrecognised += 1
            continue
        if metric in metrics or metric in duplicated:
            duplicated.add(metric)
            metrics.pop(metric, None)
            continue
        metrics[metric] = reading
    return {
        "metrics": dict(sorted(metrics.items())),
        "cards_seen": cards_seen,
        "cards_parsed": len(metrics),
        "labels_unrecognised": labels_unrecognised,
        "paths_unrecognised": paths_unrecognised,
        "metrics_drawn_twice": len(duplicated),
        "links_seen": links_seen,
        "links_not_cards": links_seen - cards_seen,
        "readable": len(metrics) > 0,
        "scope": SCOPE,
    }


async def _attributes(locator: Any, name: str, limit: int) -> list[Any]:
    out: list[Any] = []
    try:
        total = coerce.as_count(await locator.count())
    except Exception:  # noqa: BLE001 - a dead locator reads as nothing
        return out
    for index in range(min(total, limit)):
        try:
            out.append(await locator.nth(index).get_attribute(name))
        except Exception:  # noqa: BLE001
            out.append(None)
    return out


async def read_analytics_hub(page: Any) -> dict[str, Any]:
    """The reading, off the already-open hub page. Takes no url; navigates nowhere.

    Locator reads only -- ``count``, ``get_attribute`` and
    ``all_text_contents`` -- so no script is injected. A link that cannot be
    read is counted (``unreadable_links``), never raised: an exception here
    could carry page text into an envelope.
    """
    links = page.locator(LINK_SELECTOR)
    try:
        total = coerce.as_count(await links.count())
    except Exception:  # noqa: BLE001
        total = 0
    cards: list[tuple[Any, list[Any], list[Any]]] = []
    unreadable = 0
    for index in range(min(total, MAX_LINKS)):
        link = links.nth(index)
        try:
            href = await link.get_attribute("href")
        except Exception:  # noqa: BLE001
            unreadable += 1
            continue
        if classify_href(href)[0] != "card":
            cards.append((href, [], []))
            continue
        try:
            texts = list(await link.locator(TEXT_SELECTOR).all_text_contents())[:MAX_TEXTS]
        except Exception:  # noqa: BLE001
            unreadable += 1
            continue
        icons = await _attributes(link.locator(ICON_SELECTOR), "id", MAX_ICONS)
        cards.append((href, texts, icons))
    reading = tally(cards, links_seen=min(total, MAX_LINKS) - unreadable)
    reading["unreadable_links"] = unreadable
    reading["links_beyond_bound"] = max(0, total - MAX_LINKS)
    return reading


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can publish, keys included: its own words."""
    words = {
        "metrics", "cards_seen", "cards_parsed", "labels_unrecognised",
        "paths_unrecognised", "metrics_drawn_twice", "links_seen", "links_not_cards",
        "readable", "scope", "unreadable_links", "links_beyond_bound",
        "value", "delta", "direction", "window", "period", SCOPE,
    }
    words |= set(CARD_PATHS.values())
    words |= {window for _, window in LABELS.values()} | {"dated_range"}
    words |= set(PERIODS.values()) | {"vs_prior_dated_range"}
    words |= set(DIRECTIONS.values())
    return frozenset(words)
