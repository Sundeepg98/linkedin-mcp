"""His Advertising data settings page: which ad-data settings it lists, and each one's state (census ``P P15``).

ONE ADMITTED ADDRESS, :data:`ADS_URL`. ``readonly.py`` admits it by its exact
address and a pattern exemption excusing ``/mypreferences/d/categories/`` for
it alone (lane A, ONE-NAMED-SETTINGS-PAGE-AT-A-TIME, ratified by
NAMED-SETTINGS-PAGES-RATIFIED). This module never navigates and presses
nothing: the page is an index of LinkedIn's own setting links, and each
setting's control lives on a page of its own (below), which the boundary does
not admit and this module never opens.

MEASURED on the live lane's session-11 capture (load 10; the raw page kept,
his own settings page drawing no other member; tracked copy
``tests/fixtures/live11/ads.html``, and the copy with LinkedIn's path words put
back by keyed shape, ``tests/fixtures/synthetic/live11_ads_words.html``,
written by ``scripts/_build_live11_word_fixtures.py``): one ``main``; 0 form
controls in it; SIXTEEN setting links, each to
``/mypreferences/m/settings/<setting>/`` (fifteen) or
``/mypreferences/m/interest-categories/`` (one), under three section headings
-- ``Profile data`` (eight), ``Activity and inferred data`` (four) and a third
(four) whose heading's hyphen is not ASCII's. Twelve links draw a state line
reading LinkedIn's word ``On``; three draw a line that is not a state word
(it carries a count); one, the interest categories, draws none.

WHAT COMES BACK: CLOSED WORDS AND INTEGERS ONLY. A setting is named by its
address's last path word, compared against :data:`SETTINGS` -- the sixteen
measured -- and returned as that literal; a link whose word is not on the list
is COUNTED (``unknown_settings``) and never returned, because its word is the
page's. A state is ``on`` or ``off`` (LinkedIn's ``On`` / ``Off``, compared
exactly; ``Off`` is the template's other word, DERIVED: every switch the
capture drew read ``On``), ``other`` for a line that is neither, ``none`` for
no line. The section is :data:`SECTION_OF`, measured on the capture. Nothing
about him -- what a setting uses -- is read: the page shows none of it.

A ZERO RAISES: a page that draws no setting link is not an answer.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlsplit

from .config import BASE_URL
from .errors import ExtractionFailedError

#: THE ONE ADDRESS, admitted in ``readonly.py``.
ADS_URL = f"{BASE_URL}/mypreferences/d/categories/ads"

_HOST = "www.linkedin.com"
_PATH = "/mypreferences/d/categories/ads"

#: The sixteen settings the page lists, by their address's own last path word,
#: and the section each sits under -- MEASURED on session 11's capture, in the
#: page's order. ``profile_data`` and ``activity_and_inferred_data`` are
#: LinkedIn's headings ``Profile data`` and ``Activity and inferred data``,
#: verified by keyed shape; ``off_linkedin_data`` is the third heading, 15
#: letters in 17 characters, whose hyphen is not ASCII's, so it was read by its
#: shape alone.
SECTION_OF: dict[str, str] = {
    "ads-connections": "profile_data",
    "ads-companies-followed": "profile_data",
    "ads-based-on-groups": "profile_data",
    "ads-education": "profile_data",
    "ads-job-information": "profile_data",
    "ads-employer": "profile_data",
    "ads-personalization": "profile_data",
    "ads-location": "profile_data",
    "ads-inferred-location": "activity_and_inferred_data",
    "interest-categories": "activity_and_inferred_data",
    "ads-by-age": "activity_and_inferred_data",
    "ads-by-gender": "activity_and_inferred_data",
    "ads-beyond-linkedin": "off_linkedin_data",
    "ads-interactions-with-business": "off_linkedin_data",
    "ads-related-actions": "off_linkedin_data",
    "share-data-with-select-partners": "off_linkedin_data",
}
SETTINGS: tuple[str, ...] = tuple(SECTION_OF)
SECTIONS = ("profile_data", "activity_and_inferred_data", "off_linkedin_data")

#: A setting link's address, as the page draws it: ``/mypreferences/m/`` (or
#: ``/d/``), then ``settings/<word>/`` or the interest categories' own word.
_SETTING_PATH = re.compile(
    r"^/mypreferences/[md]/(?:settings/([a-z][a-z-]{1,60})|(interest-categories))/?$"
)

#: Why a whole read refuses. Closed.
REFUSALS = ("main_unreadable", "landed_elsewhere")

#: A state line's word, and what it means. Compared exactly.
STATES = ("on", "off", "other", "none")
_ON = re.compile(r"^\s*On\s*$")
_OFF = re.compile(r"^\s*Off\s*$")

SCOPE = (
    "His Advertising data settings page: which ad-data settings it lists and "
    "the state each draws, as closed words. One page, no press: each setting's "
    "own switch lives on a page of its own, which is not opened. A setting the "
    "page lists under a word this server has not measured is counted, never "
    "named. A zero raises."
)


def landed_on_the_page(landed: Any) -> bool:
    """Did the load land on the Advertising data page itself? PURE."""
    if not isinstance(landed, str) or not landed:
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return parts.scheme == "https" and parts.netloc == _HOST and parts.path.rstrip("/") == _PATH


def setting_of(href: Any) -> str | None:
    """The measured setting a link's address names, or ``None``. PURE: the
    address is compared, and only a literal of :data:`SETTINGS` comes back."""
    if not isinstance(href, str):
        return None
    try:
        parts = urlsplit(href)
    except ValueError:
        return None
    if parts.netloc not in ("", _HOST):
        return None
    found = _SETTING_PATH.match(parts.path)
    if found is None:
        return None
    word = found.group(1) or found.group(2)
    for setting in SETTINGS:
        if word == setting:
            return setting
    return None


def _reading() -> dict[str, Any]:
    """The answer's shape, every count at zero. Every key is fixed here."""
    return {
        "surface": "own_advertising_data_settings",
        "refused": None,
        "setting_links_seen": 0,
        "settings": [],
        "unknown_settings": 0,
        "states": {state: 0 for state in STATES},
        "form_controls_in_main": 0,
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the page."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


async def _state_of(link: Any) -> str:
    """One setting link's state, by counts of LinkedIn's two words."""
    spans = link.locator("span")
    if await spans.filter(has_text=_ON).count() == 1:
        return "on"
    if await spans.filter(has_text=_OFF).count() == 1:
        return "off"
    if await link.locator("p").count() >= 2:
        return "other"
    return "none"


async def read_advertising_data(page: Any) -> dict[str, Any]:
    """His Advertising data page, already open: its settings and their states.

    The page must already be at :data:`ADS_URL`. One read; no navigation,
    press or scroll. Raises when the page draws no setting link at all.
    """
    out = _reading()
    main = page.locator("main")
    if await main.count() != 1:
        out["refused"] = "main_unreadable"
        return out
    out["form_controls_in_main"] = await main.locator(
        "input, select, textarea, [role=switch], [role=checkbox], [role=radio]"
    ).count()
    links = main.locator('a[href*="/mypreferences/"]')
    total = await links.count()
    for index in range(total):
        link = links.nth(index)
        setting = setting_of(await link.get_attribute("href"))
        if setting is None:
            if _looks_like_a_setting(await link.get_attribute("href")):
                out["setting_links_seen"] += 1
                out["unknown_settings"] += 1
            continue
        out["setting_links_seen"] += 1
        state = await _state_of(link)
        out["states"][state] += 1
        out["settings"].append(
            {"setting": setting, "section": SECTION_OF[setting], "state": state}
        )
    if out["setting_links_seen"] == 0:
        raise ExtractionFailedError(
            "the Advertising data page drew no setting link, so nothing about "
            "his ad-data settings can be said; reported as a failure rather "
            "than as an empty page.",
            url=ADS_URL,
        )
    out["readable"] = bool(out["settings"])
    return out


def _looks_like_a_setting(href: Any) -> bool:
    """Is this a setting link at all -- the address shape, whatever its word?"""
    if not isinstance(href, str):
        return False
    try:
        return bool(_SETTING_PATH.match(urlsplit(href).path))
    except ValueError:
        return False
