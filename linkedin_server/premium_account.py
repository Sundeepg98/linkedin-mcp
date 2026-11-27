"""His Manage Premium account settings page: which subscription he holds, and which of its controls are drawn (census ``P N22``).

ONE ADMITTED ADDRESS, :data:`PREMIUM_ACCOUNT_URL`. ``readonly.py`` admits it by
its exact address (lane admit26, 2026-11-25, a named settings page in its own
commit; it trips no forbidden substring). This module never navigates and
presses nothing: every control on the page that changes or cancels the plan is
a purchase act this server does not build (PURCHASES-STAY-MANUAL).

MEASURED on the live lane's session-12 capture (load 33, served exact; the raw
page withheld by the people gate, the keyed skeleton kept; tracked copy
``tests/fixtures/live12/premium_manage_account.html`` and, with LinkedIn's
words written where their keyed shapes matched,
``tests/fixtures/live12/premium_manage_account_words.html``, written by
``scripts/_build_live12_settings_word_skeletons.py``). Ember markup whose class
names and ``data-test-*`` hooks the skeleton keeps:

* one ``main``; in it the banner's ``h1`` (``data-test-header-title``)
  reading ``Manage Premium account``, beside a ``Back`` link to
  ``/mypreferences/d/categories/account``;
* one list, ``[data-test-premium-subscription-overview-settings-card]``, of
  ONE ``li`` -- a subscription card -- holding:
  - its header, ``[data-test-premium-subscription-overview-settings-card__header]``,
    an ``h2`` reading ``Premium Career``;
  - its description, two ``p`` lines carrying NO DIGIT: the page draws no
    renewal date, no billing date and no price (measured on the keyed shapes'
    digit counts; their words matched no candidate and stay unread);
  - three action links, each
    ``[data-test-premium-subscription-overview-settings-card__action-link]``:
    ``Switch plans`` (to a ``/premium/`` page with an upsell origin),
    ``Manage subscription`` (to his purchase page,
    ``/manage/purchases-payments/purchases/<his purchase id>``, which the
    boundary refuses) and ``Cancel subscription`` (to
    ``/premium/cancellation/``). None is opened or pressed here, and no
    address is returned: the manage link carries his purchase id.

WHAT COMES BACK: CLOSED WORDS AND INTEGERS ONLY. A plan is its header compared
exactly against :data:`PLANS` and returned as that literal; any other is
``other``, COUNTED (``unknown_plans``) and never named. An action is its link's
words compared exactly against :data:`ACTIONS`; any other is counted
(``unknown_actions``) and never named. A description line is counted, and
counted again if it carries a digit (a date or an amount would); its text
never leaves this function.

THE ZERO RULE: a page whose heading is not drawn, or on which no subscription
card is read, raises -- no other state of this page (no plan, a trial, a
lapsed plan) has been captured.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from .config import BASE_URL
from .errors import ExtractionFailedError

#: THE ONE ADDRESS, admitted in ``readonly.py``, in the spelling session 12
#: loaded and was served exactly (load 33).
PREMIUM_ACCOUNT_URL = f"{BASE_URL}/mypreferences/d/premium-manage-account/"

_HOST = "www.linkedin.com"
_PATH = "/mypreferences/d/premium-manage-account"

#: The page's heading, MEASURED.
PAGE_HEADING = "Manage Premium account"

#: Each plan, by its card header, MEASURED, and the literal it is returned as.
PLANS: dict[str, str] = {"Premium Career": "premium_career"}

#: Each card control, by its words, MEASURED, and the literal it is returned
#: as. Read, never pressed: the first and the last are purchase acts.
ACTIONS: dict[str, str] = {
    "Switch plans": "switch_plans",
    "Manage subscription": "manage_subscription",
    "Cancel subscription": "cancel_subscription",
}

#: Why a whole read refuses. Closed.
REFUSALS = ("main_unreadable", "landed_elsewhere")

#: Milliseconds any one read may wait, and the most parts read on a page.
READ_TIMEOUT_MS = 2000
MAX_PARTS = 20

_CARDS = "[data-test-premium-subscription-overview-settings-card] li"
_HEADER = "[data-test-premium-subscription-overview-settings-card__header]"
_DESCRIPTION = "[data-test-premium-subscription-overview-settings-card__description] p"
_ACTION = "[data-test-premium-subscription-overview-settings-card__action-link]"

SCOPE = (
    "His Manage Premium account page: each subscription card's plan as a "
    "closed word, the card's controls by LinkedIn's words, and how many of its "
    "lines carry a digit. One page, nothing pressed, no address returned. A "
    "plan or a control under a word this server has not measured is counted, "
    "never named. No card read raises."
)


def landed_on_the_page(landed: Any) -> bool:
    """Did the load land on the Manage Premium account page itself? PURE."""
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
        "surface": "own_premium_account",
        "refused": None,
        "page_heading_drawn": False,
        "subscriptions": [],
        "subscriptions_seen": 0,
        "unknown_plans": 0,
        "unknown_actions": 0,
        "reads_failed": 0,
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the page."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


def _collapsed(text: Any) -> str:
    return " ".join(text.split()) if isinstance(text, str) else ""


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _text(locator: Any, failed: list[int]) -> str:
    try:
        value = await locator.inner_text(timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return ""
    return _collapsed(value)


async def _subscription_card(card: Any, out: dict[str, Any], failed: list[int]) -> dict[str, Any]:
    """One subscription card, closed words and counts. Its text stays here."""
    headers = card.locator(_HEADER)
    header = await _text(headers.nth(0), failed) if await _count(headers, failed) == 1 else ""
    plan = PLANS.get(header)
    if plan is None:
        out["unknown_plans"] += 1
        plan = "other"
    lines = card.locator(_DESCRIPTION)
    total = min(await _count(lines, failed), MAX_PARTS)
    with_digits = 0
    for index in range(total):
        if any(ch.isdigit() for ch in await _text(lines.nth(index), failed)):
            with_digits += 1
    actions: list[str] = []
    links = card.locator(_ACTION)
    for index in range(min(await _count(links, failed), MAX_PARTS)):
        action = ACTIONS.get(await _text(links.nth(index), failed))
        if action is None:
            out["unknown_actions"] += 1
            continue
        actions.append(action)
    return {
        "plan": plan,
        "actions": actions,
        "description_lines": total,
        "description_lines_with_digits": with_digits,
    }


async def read_premium_account(page: Any) -> dict[str, Any]:
    """His Manage Premium account page, already open: each subscription card.

    The page must already be at :data:`PREMIUM_ACCOUNT_URL`. One read; no
    navigation, press or scroll. Raises when the heading is not drawn or no
    subscription card is read.
    """
    out = _reading()
    failed = [0]
    main = page.locator("main")
    if await _count(main, failed) != 1:
        out["refused"] = "main_unreadable"
        out["reads_failed"] = failed[0]
        return out
    region = main.nth(0)
    headings = region.locator("h1")
    titles = [await _text(headings.nth(i), failed) for i in range(min(await _count(headings, failed), 4))]
    out["page_heading_drawn"] = titles.count(PAGE_HEADING) == 1
    cards = region.locator(_CARDS)
    for index in range(min(await _count(cards, failed), MAX_PARTS)):
        out["subscriptions_seen"] += 1
        out["subscriptions"].append(await _subscription_card(cards.nth(index), out, failed))
    out["reads_failed"] = failed[0]
    if not out["page_heading_drawn"]:
        raise ExtractionFailedError(
            "the Manage Premium account page drew no heading this reader "
            "knows, so nothing on it is read.",
            url=PREMIUM_ACCOUNT_URL,
        )
    if not out["subscriptions"]:
        raise ExtractionFailedError(
            "no subscription card was read on the Manage Premium account page, "
            "and no other state of it has been captured; an empty list here "
            "would be indistinguishable from a broken read.",
            url=PREMIUM_ACCOUNT_URL,
        )
    out["readable"] = True
    return out
