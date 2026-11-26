"""The people he UNFOLLOWED, from his own settings page: each a people record (census ``N 39``).

ONE ADMITTED ADDRESS, :data:`UNFOLLOWED_URL`. ``readonly.py`` admits it by its
exact address and a pattern exemption excusing ``/unfollow`` for it alone
(lane A, READ-PAST-AN-ACT-SUBSTRING and ONE-NAMED-SETTINGS-PAGE-AT-A-TIME,
ratified by NAMED-SETTINGS-PAGES-RATIFIED). This module never navigates: the
tool loads that address once and hands the open page here. Nothing is
pressed: each row's ``Follow`` button -- a re-follow, a write with its own
spec -- is read as LinkedIn's word and never clicked.

MEASURED on the live lane's session-11 capture (load 9; tracked copy
``tests/fixtures/live11/unfollowed.html``), in a local headless engine. The
page is his settings page's older markup, which carries LinkedIn's test hooks
as attributes: one ``main``; one card ``[data-test-unfollowed-card]`` holding
one list of 44 rows; each row a list item holding the member's name in
``[data-test-profile-card-name]``, an empty ``[data-test-profile-distance]``,
and one ``button[data-test-unfollowed-member__follow-btn]`` whose visible word
is ``Follow``. NO ROW CARRIES A LINK OR AN ID OF THE MEMBER: measured on the
kept raw page, 0 profile addresses and 0 member urns in 44 rows -- the picture
link has no ``href``. So a member comes back with a name and no link, and no
write can be aimed at one from this page (the record of lane readers-net26,
the row ``N 40``).

WHAT COMES BACK. Per row read, one :class:`people_data.Person` envelope -- the
name, no headline, no link -- beside ``he_follows`` (False on ``Follow``,
True on ``Following``, None otherwise), under PEOPLE-DATA-MITIGATIONS:
declared fields only; sanitised and marked; never stored; bounded to one page,
the first render, at most :data:`MAX_ROWS_READ` rows; visible only; never a
target -- the button's ``aria-label`` (live, ``Follow`` and the member's
name) is never read.

AN EMPTY LIST RAISES: no capture draws the page empty, so a zero cannot be
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
UNFOLLOWED_URL = f"{BASE_URL}/mypreferences/d/unfollowed"

_HOST = "www.linkedin.com"
_PATH = "/mypreferences/d/unfollowed"

#: LinkedIn's test hooks on this page, measured. Attributes, not classes.
CARD_SELECTOR = "[data-test-unfollowed-card]"
NAME_SELECTOR = "[data-test-profile-card-name]"
BUTTON_SELECTOR = "button[data-test-unfollowed-member__follow-btn]"

#: A row's follow-state word and what it says about HIM. Anything else is
#: ``None``.
FOLLOWS_OF_WORD: dict[str, bool] = {"Follow": False, "Following": True}
_WORD = re.compile(r"^\s*(Follow|Following)\s*$")

#: Why a whole read refuses. Closed.
REFUSALS = ("card_unreadable", "landed_elsewhere")

#: Why one row was not read in full. Closed.
ROW_GAPS = ("not_one_button", "other_word", "name_unread", "unreadable")

#: Rows read per call, at most (measured: 44 on the first render).
MAX_ROWS_READ = 100

#: How long one element's text read may wait, in ms.
TEXT_TIMEOUT_MS = 2000

SCOPE = (
    "The members he unfollowed, from his own settings page's first render: "
    "one page, no scroll and no press. Each comes back as a people record "
    "with a name and NO link -- LinkedIn draws none on this page -- beside "
    "whether he follows them now (PEOPLE-DATA-MITIGATIONS, "
    "MEMBER-ROSTERS-AS-BOUNDED-READS): declared fields only, sanitised and "
    "marked as another member's words, never stored. The Follow button is "
    "read as a word and never pressed; no control's label is read. A zero "
    "raises."
)


def landed_on_the_page(landed: Any) -> bool:
    """Did the load land on the unfollowed page itself? PURE."""
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
        "surface": "own_unfollowed_list",
        "refused": None,
        "cards_seen": 0,
        "rows_seen": 0,
        "rows_read": 0,
        "unfollowed": [],
        "row_gaps": {gap: 0 for gap in ROW_GAPS},
        "one_page": True,
        "beyond_first_render": "not_read",
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the page."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


async def _unfollowed_row(row: Any) -> tuple[Optional[dict[str, Any]], Optional[bool], Optional[str]]:
    """``(member envelope, he_follows, gap)`` for one row."""
    buttons = row.locator(BUTTON_SELECTOR)
    if await buttons.count() != 1:
        return None, None, "not_one_button"
    he_follows = None
    if await buttons.filter(has_text=re.compile(r"^\s*Following\s*$")).count() == 1:
        he_follows = FOLLOWS_OF_WORD["Following"]
    elif await buttons.filter(has_text=re.compile(r"^\s*Follow\s*$")).count() == 1:
        he_follows = FOLLOWS_OF_WORD["Follow"]
    names = row.locator(NAME_SELECTOR)
    if await names.count() != 1:
        return None, he_follows, "name_unread"
    person = people_data.Person.from_page(name=await names.first.inner_text(timeout=TEXT_TIMEOUT_MS))
    if person is None:
        return None, he_follows, "name_unread"
    return person.envelope(), he_follows, (None if he_follows is not None else "other_word")


async def read_unfollowed_list(page: Any) -> dict[str, Any]:
    """The members he unfollowed, on the already-open unfollowed page.

    The page must already be at :data:`UNFOLLOWED_URL`. One read of the first
    render; no navigation, press or scroll. Refuses when the page does not
    draw exactly one unfollowed card (``card_unreadable``); raises when the
    card draws no row.
    """
    out = _reading()
    cards = page.locator("main").locator(CARD_SELECTOR)
    out["cards_seen"] = await cards.count()
    if out["cards_seen"] != 1:
        out["refused"] = "card_unreadable"
        return out
    marker = page.locator(BUTTON_SELECTOR)
    rows = cards.first.locator("li").filter(has=marker)
    out["rows_seen"] = await rows.count()
    if out["rows_seen"] == 0:
        raise ExtractionFailedError(
            "the unfollowed card drew no member row (a list item holding its "
            "Follow button), and no empty state for this page has ever been "
            "captured to corroborate a zero, so it is reported as a failure.",
            url=UNFOLLOWED_URL,
        )
    to_read = min(out["rows_seen"], MAX_ROWS_READ)
    for index in range(to_read):
        try:
            member, he_follows, gap = await _unfollowed_row(rows.nth(index))
        except Exception:  # noqa: BLE001 -- the row is unreadable; nothing of it is kept
            out["row_gaps"]["unreadable"] += 1
            continue
        if gap is not None:
            out["row_gaps"][gap] += 1
        if member is not None:
            out["unfollowed"].append({"member": member, "he_follows": he_follows})
    out["rows_read"] = to_read
    out["readable"] = bool(out["unfollowed"])
    return out
