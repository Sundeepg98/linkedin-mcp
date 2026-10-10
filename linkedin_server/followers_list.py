"""His own FOLLOWER LIST, read as COUNTS AND RELATIONS ONLY (census ``P L2b``).

ONE ADMITTED ADDRESS, :data:`FOLLOWERS_URL`. ``readonly.py`` admits it by a
two-gate pair (an anchored allowlist line and a pattern exemption excusing
``/follow`` for this one address; ``tests/test_l1_follower_list_carve_out.py``
proves each half). This module never navigates: the tool loads that address
once and hands the open page here.

WHAT IT RETURNS, AND WHY ONLY THAT. The page is a list of PEOPLE -- the members
who follow him. The admission's own comment says what a reader of it owes:
"COUNTS AND RELATIONS ONLY, structurally, the ``groups.py`` way". So:

* how many rows the first render draws, and how many lists hold them -- the
  denominators that make a zero readable;
* for each row, ONE RELATION: does HE follow that follower back? LinkedIn
  draws it as the row's single follow-state button, whose own visible word is
  ``Following`` (he follows them) or ``Follow`` (he does not). Anything else
  -- no button, more than one, another word, a read that failed -- is
  ``unknown`` and counted by reason, never guessed;
* which SIDE of the tab strip is selected. The page's sibling tab is the list
  of people HE follows; a reading taken there is about other people, so the
  read refuses unless the selected tab is NOT the one LinkedIn labels
  ``Following``.

NO FIELD CAN HOLD PAGE TEXT. Every value is an integer, a boolean, or a word
from a closed tuple below. No name, member id, link, headline or button label
is returned, logged or kept -- and live the follow-state button's
``aria-label`` carries the member's NAME, so this module never reads it: the
word is read from the button's visible text slot and only ever compared.
PEOPLE-DATA-MITIGATIONS (declared fields only; bounded to one page per call;
visible only) and MEMBER-ROSTERS-AS-BOUNDED-READS (one page per call, no
automatic pagination, inside the live budget) are what bound it.

ONE PAGE, FIRST RENDER ONLY. No scroll and no press: SCROLL-NOT-SANCTIONED.
Rows LinkedIn draws only after a scroll are NOT READ, so ``rows_seen`` is not
his follower count and the answer says so (``one_page``,
``beyond_first_render``).

AIMED BY ROLE, ``data-view-name`` AND LINKEDIN'S OWN WORDS, NEVER BY POSITION
(NO-INDEX-PINNED-JUDGEMENTS). Every row is treated alike; no row, tab or list is
chosen by its place in the document.

MEASURED on the tracked skeleton of the live lane's session-2 capture
(``tests/fixtures/live2/followers.html``), in a local headless engine: one
``main``; one tab strip of two tabs, the one reading ``Following`` not
selected; one list holding ten rows; each row one button whose visible word is
``Following`` (9 rows) or ``Follow`` (1 row), and whose ``aria-label`` is the
skeleton's ``x`` where the live page drew a name. An accessible-name query for
a button named ``Following`` finds NONE of them -- the label overrides the
name -- which is why the word is read from the text slot.
"""
from __future__ import annotations

from typing import Any
from urllib.parse import urlsplit

from .config import BASE_URL

#: THE ONE ADDRESS. Admitted in ``readonly.py`` (``P L2b``'s pair); nothing
#: here builds another, and a page never supplies one.
FOLLOWERS_URL = f"{BASE_URL}/mynetwork/network-manager/people-follow/followers/"

#: The admitted address's host and path, which a landing must match.
_LIST_HOST = "www.linkedin.com"
_LIST_PATH = "/mynetwork/network-manager/people-follow/followers"

#: A row of the list, by LinkedIn's own template name for it.
ROW_SELECTOR = '[data-view-name="search-entity-result-universal-template"]'

#: The visible-word slot of LinkedIn's button component. The word is read
#: HERE and nowhere else: the button's accessible name is its ``aria-label``,
#: which live carries the member's name.
WORD_SLOT_SELECTOR = "span.artdeco-button__text"

#: LinkedIn's own label on the OTHER tab -- the people he follows.
FOLLOWING_TAB_WORD = "Following"

#: THE CLOSED VOCABULARY of a row's follow-state word, and what each means
#: about HIM. Anything not exactly one of these is ``other_word``.
RELATION_OF_WORD: dict[str, str] = {
    "Following": "he_follows_back",
    "Follow": "he_does_not_follow_back",
}

#: Which side of the tab strip is selected.
SIDES = ("followers", "following", "unknown")

#: Why a whole read refuses. Closed.
REFUSALS = ("not_the_followers_side", "side_unreadable", "landed_elsewhere")

#: Why one row's relation is ``unknown``. Closed.
UNKNOWN_REASONS = ("no_button", "several_buttons", "other_word", "unreadable")

#: Rows classified per call, at most. The first render draws about ten
#: (measured: 10); the bound exists so a page that draws thousands cannot
#: turn one call into a sweep. Rows past it are counted in ``rows_seen`` and
#: not classified.
MAX_ROWS_READ = 100

#: How long one row's word read may wait, in ms. A row that vanishes between
#: the count and the read is ``unreadable``, not a thirty-second stall.
WORD_TIMEOUT_MS = 2000

#: What every answer says about its own reach. A constant: no page text.
SCOPE = (
    "His own follower list, first render only: one page, no scroll and no "
    "press (SCROLL-NOT-SANCTIONED), so rows past the first render are not read "
    "and rows_seen is not his follower count. Counts and relations only "
    "(PEOPLE-DATA-MITIGATIONS, MEMBER-ROSTERS-AS-BOUNDED-READS): no name, "
    "member id, link, headline or label is returned. A zero is a reading only "
    "when readable is true."
)


def landed_on_the_list(landed: Any) -> bool:
    """Did the navigation land on the admitted list itself?

    Scheme, host and path must be the admitted address's (a trailing slash
    either way). A query or fragment is ignored -- it cannot move the browser
    and nothing reads it -- and any other path, including the sibling
    FOLLOWING list and the family root, is elsewhere. Pure.
    """
    if not isinstance(landed, str) or not landed:
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.netloc == _LIST_HOST
        and parts.path.rstrip("/") == _LIST_PATH
    )


def classify_word(word: Any) -> str:
    """A follow-state word's relation, or ``other_word``. Exact, after the
    surrounding whitespace only: ``following`` or ``Follow back`` is another
    word, never a near match. Pure; the word is compared, never returned."""
    if not isinstance(word, str):
        return "other_word"
    return RELATION_OF_WORD.get(str(word).strip(), "other_word")


def _reading(side: str, tabs_seen: int, lists_seen: int, rows_seen: int) -> dict[str, Any]:
    """The answer's shape, every relation at zero. Every key is fixed here."""
    return {
        "surface": "own_follower_list",
        "side": side,
        "refused": None,
        "tabs_seen": tabs_seen,
        "lists_seen": lists_seen,
        "rows_seen": rows_seen,
        "rows_read": 0,
        "he_follows_back": 0,
        "he_does_not_follow_back": 0,
        "unknown": 0,
        "unknown_why": {reason: 0 for reason in UNKNOWN_REASONS},
        "one_page": True,
        "beyond_first_render": "not_read",
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a landing that is not the list. Nothing was read, and
    nothing about the landing is said: its address is LinkedIn's string."""
    out = _reading("unknown", 0, 0, 0)
    out["refused"] = "landed_elsewhere"
    return out


async def _side(main: Any) -> tuple[str, int]:
    """``(side, tabs_seen)`` from COUNTS ALONE -- no tab's text is read.

    ``followers`` needs exactly one selected tab and exactly one tab LinkedIn
    labels ``Following``, and that one NOT selected. The Following tab
    selected is ``following``; any other strip is ``unknown``.
    """
    tabs_seen = await main.get_by_role("tab").count()
    selected = await main.get_by_role("tab", selected=True).count()
    following = await main.get_by_role(
        "tab", name=FOLLOWING_TAB_WORD, exact=True
    ).count()
    if selected != 1 or following != 1:
        return "unknown", tabs_seen
    following_selected = await main.get_by_role(
        "tab", name=FOLLOWING_TAB_WORD, exact=True, selected=True
    ).count()
    return ("following" if following_selected else "followers"), tabs_seen


async def _relation_of(row: Any) -> str:
    """One row's relation, by its SINGLE button's own visible word.

    The row's buttons are found by role. None, or more than one, is unknown --
    which of two is the follow state is not guessed. The one button's word is
    read from its text slot (exactly one slot, else ``other_word``) and only
    compared; its ``aria-label`` is never read.
    """
    buttons = row.get_by_role("button")
    count = await buttons.count()
    if count == 0:
        return "no_button"
    if count > 1:
        return "several_buttons"
    slots = buttons.locator(WORD_SLOT_SELECTOR)
    if await slots.count() != 1:
        return "other_word"
    return classify_word(await slots.first.inner_text(timeout=WORD_TIMEOUT_MS))


async def read_followers_list(page: Any) -> dict[str, Any]:
    """His follower list on the already-open page: counts and relations.

    The page must already be at :data:`FOLLOWERS_URL` (the tool loads it and
    checks the landing). One read of the first render; no navigation, press
    or scroll. Refuses -- relations all zero, the denominators kept -- when
    the selected tab is the Following side (``not_the_followers_side``) or
    the tab strip cannot say which side is open (``side_unreadable``).
    """
    main = page.locator("main")
    if await main.count() != 1:
        out = _reading("unknown", 0, 0, 0)
        out["refused"] = "side_unreadable"
        return out
    side, tabs_seen = await _side(main)
    lists = main.get_by_role("list")
    rows = lists.locator(ROW_SELECTOR)
    out = _reading(side, tabs_seen, await lists.count(), await rows.count())
    if side != "followers":
        out["refused"] = (
            "not_the_followers_side" if side == "following" else "side_unreadable"
        )
        return out
    to_read = min(out["rows_seen"], MAX_ROWS_READ)
    for index in range(to_read):
        try:
            relation = await _relation_of(rows.nth(index))
        except Exception:  # noqa: BLE001 -- the row is unreadable; nothing of it is kept
            relation = "unreadable"
        if relation in ("he_follows_back", "he_does_not_follow_back"):
            out[relation] += 1
        else:
            out["unknown"] += 1
            out["unknown_why"][relation] += 1
    out["rows_read"] = to_read
    out["readable"] = to_read > 0
    return out
