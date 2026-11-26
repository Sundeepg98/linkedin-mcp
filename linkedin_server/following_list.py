"""The PEOPLE he follows: his own following list, each member a people record (census ``N 38``).

ONE ADMITTED ADDRESS, :data:`FOLLOWING_URL`. ``readonly.py`` admits it by a
two-gate pair (an anchored allowlist line and a pattern exemption excusing
``/follow`` for this one address; lane A, READ-PAST-AN-ACT-SUBSTRING). This
module never navigates: the tool loads that address once and hands the open
page here. Nothing is pressed: each row's ``Following`` button is read as
LinkedIn's word and never clicked.

THE SIBLING LIST IS HIS FOLLOWERS (``followers_list.py``, census ``P L2b``),
on the same page's other tab. LinkedIn redrew the page between the two
captures: session 2's followers list is ``data-view-name`` rows with
``role=tab`` buttons, and session 11's following list is the new markup --
a ``nav`` of two links, the open one ``aria-current="true"``, and each member
a link card. So this is a reader of its own, measured on its own capture.

MEASURED on the live lane's session-11 capture (load 16; tracked copy
``tests/fixtures/live11/following.html``), in a local headless engine: one
``main``; a ``nav`` of two links -- ``Following``, current, to
``.../people-follow/following``, and the followers tab; twenty member cards,
each ONE link to a member's profile holding the member's name (the card's one
paragraph with no child element), a headline (the one paragraph holding a
span) and exactly one button whose visible word is ``Following``.

WHAT COMES BACK. Per card read, one :class:`people_data.Person` envelope --
name, headline, canonical profile link -- under PEOPLE-DATA-MITIGATIONS:
declared fields only; sanitised and marked; never stored; bounded to one page,
the first render, at most :data:`MAX_ROWS_READ` cards
(MEMBER-ROSTERS-AS-BOUNDED-READS); visible only; never a target -- this module
acts on nobody, and the button's ``aria-label`` (live, it names the member)
is never read.

THE SIDE IS READ FROM LINKEDIN'S OWN WORD. The link whose text is
``Following`` must be the current one; on the followers tab it is not, and the
read refuses rather than return his followers as people he follows.

AN EMPTY LIST RAISES: no capture draws it empty, so a zero cannot be
corroborated.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from . import people_data
from .config import BASE_URL
from .errors import ExtractionFailedError

#: THE ONE ADDRESS, admitted in ``readonly.py``.
FOLLOWING_URL = f"{BASE_URL}/mynetwork/network-manager/people-follow/following/"

_HOST = "www.linkedin.com"
_PATH = "/mynetwork/network-manager/people-follow/following"

#: LinkedIn's own word: the open tab's text, and each card's button.
FOLLOWING_WORD = "Following"

_FOLLOWING_EXACTLY = re.compile(r"^\s*" + FOLLOWING_WORD + r"\s*$")

#: Which tab is open.
SIDES = ("following", "followers", "unknown")

#: Why a whole read refuses. Closed.
REFUSALS = ("not_the_following_side", "side_unreadable", "landed_elsewhere")

#: Why one card was not read as a record. Closed.
CARD_GAPS = ("not_one_button", "name_unread", "unreadable")

#: Cards read per call, at most (measured: twenty on the first render).
MAX_ROWS_READ = 100

#: How long one element's text read may wait, in ms.
TEXT_TIMEOUT_MS = 2000

SCOPE = (
    "The people he follows, the following list's first render only: one page, "
    "no scroll and no press, so cards past the first render are not read and "
    "cards_seen is not how many people he follows. Each comes back as a people "
    "record (PEOPLE-DATA-MITIGATIONS, MEMBER-ROSTERS-AS-BOUNDED-READS): "
    "declared fields only, sanitised and marked as another member's words, "
    "never stored. The Following button is read as a word and never pressed; "
    "no control's label is read. A zero raises."
)


def landed_on_the_list(landed: Any) -> bool:
    """Did the load land on the following list itself? PURE."""
    if not isinstance(landed, str) or not landed:
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return parts.scheme == "https" and parts.netloc == _HOST and parts.path.rstrip("/") == _PATH


def _reading() -> dict[str, Any]:
    """The answer's shape, every count at zero. Every key is fixed here."""
    return {
        "surface": "own_following_list",
        "side": "unknown",
        "refused": None,
        "tab_links_seen": 0,
        "cards_seen": 0,
        "cards_read": 0,
        "following": [],
        "card_gaps": {gap: 0 for gap in CARD_GAPS},
        "one_page": True,
        "beyond_first_render": "not_read",
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the list."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


async def _side(main: Any) -> tuple[str, int]:
    """``(side, tab links seen)`` from counts alone: exactly one navigation
    link whose text is ``Following``, and it current."""
    links = main.locator("nav a")
    seen = await links.count()
    if await links.filter(has_text=_FOLLOWING_EXACTLY).count() != 1:
        return "unknown", seen
    current = main.locator('nav a[aria-current="true"]')
    if await current.count() != 1:
        return "unknown", seen
    if await current.filter(has_text=_FOLLOWING_EXACTLY).count() == 1:
        return "following", seen
    return "followers", seen


async def _followed_member(card: Any) -> Optional[dict[str, Any]]:
    """One card's member as a person envelope, or None.

    THE LINK is the card's own href. THE NAME is the card's one paragraph with
    no child element; THE HEADLINE the one paragraph holding a span (absent
    unless exactly one). The button's label is never read.
    """
    href = people_data.canonical_profile_link(await card.get_attribute("href"))
    if href is None:
        return None
    names = card.locator("p:not(:has(*))")
    if await names.count() != 1:
        return None
    lines = card.locator("p:has(> span)")
    headline = None
    if await lines.count() == 1:
        headline = await lines.first.inner_text(timeout=TEXT_TIMEOUT_MS)
    person = people_data.Person.from_page(
        name=await names.first.inner_text(timeout=TEXT_TIMEOUT_MS),
        headline=headline,
        href=href,
    )
    return person.envelope() if person is not None else None


async def read_following_list(page: Any) -> dict[str, Any]:
    """The people he follows, on the already-open following list.

    The page must already be at :data:`FOLLOWING_URL`. One read of the first
    render; no navigation, press or scroll. Refuses on the followers tab
    (``not_the_following_side``) or a strip it cannot read
    (``side_unreadable``). Raises when no member card is drawn.
    """
    out = _reading()
    main = page.locator("main")
    if await main.count() != 1:
        out["refused"] = "side_unreadable"
        return out
    side, out["tab_links_seen"] = await _side(main)
    out["side"] = side
    if side != "following":
        out["refused"] = "not_the_following_side" if side == "followers" else "side_unreadable"
        return out
    marker = page.locator("button").filter(has_text=_FOLLOWING_EXACTLY)
    cards = main.locator('a[href*="/in/"]').filter(has=marker)
    out["cards_seen"] = await cards.count()
    if out["cards_seen"] == 0:
        raise ExtractionFailedError(
            "the following list drew no member card (a member link holding a "
            "Following button), and no empty state for this list has ever been "
            "captured to corroborate a zero, so it is reported as a failure.",
            url=FOLLOWING_URL,
        )
    to_read = min(out["cards_seen"], MAX_ROWS_READ)
    for index in range(to_read):
        card = cards.nth(index)
        try:
            if await card.locator("button").count() != 1:
                out["card_gaps"]["not_one_button"] += 1
                continue
            member = await _followed_member(card)
        except Exception:  # noqa: BLE001 -- the card is unreadable; nothing of it is kept
            out["card_gaps"]["unreadable"] += 1
            continue
        if member is None:
            out["card_gaps"]["name_unread"] += 1
            continue
        out["following"].append(member)
    out["cards_read"] = to_read
    out["readable"] = bool(out["following"])
    return out
