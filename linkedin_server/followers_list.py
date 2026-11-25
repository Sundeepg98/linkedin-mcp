"""His own FOLLOWER LIST: each follower a people record, and the counts (census ``P L2b``).

ONE ADMITTED ADDRESS, :data:`FOLLOWERS_URL`. ``readonly.py`` admits it by a
two-gate pair (an anchored allowlist line and a pattern exemption excusing
``/follow`` for this one address; ``tests/test_l1_follower_list_carve_out.py``
proves each half). This module never navigates: the tool loads that address
once and hands the open page here.

THE COUNTS FIRST. The page is a list of PEOPLE -- the members who follow him.
The admission's own comment (2026-09-23) says what a reader of it owes:
"COUNTS AND RELATIONS ONLY, structurally, the ``groups.py`` way". That comment
predates NAMES-AT-RUNTIME (2026-09-24), under which a row whose payload is WHO
returns the people themselves (the records below); the counts stay, as the
denominators every record is read against. So:

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

THE COUNTS HOLD NO PAGE TEXT. Every count field is an integer, a boolean, or a
word from a closed tuple below. Live, the follow-state button's ``aria-label``
carries the member's NAME, so this module never reads it: the word is read
from the button's visible text slot and only ever compared.

AND THE PEOPLE COME BACK AS RECORDS (added 2026-10-10 on the lane B1 lead's
ruling: the row's payload is WHO, so WHO-WHICH-COUNTS-ARE-NOT-DELIVERY and
NAMES-AT-RUNTIME call for the names). ``followers`` holds, per row read, one
:class:`people_data.Person` envelope -- name, headline, canonical profile link,
no degree -- beside that row's relation (``he_follows_back``: True, False, or
None when unknown). Under PEOPLE-DATA-MITIGATIONS: declared fields only (the
record's four, and the relation beside it); sanitised and marked as another
member's words (``Person.from_page``); never stored (nothing here writes,
logs or caches); bounded to one page, the first render, at most
:data:`MAX_ROWS_READ` rows; visible only (the name is the row's own link
text, a "LinkedIn Member" stays that); never a target (this module acts on
nobody). MEMBER-ROSTERS-AS-BOUNDED-READS (one page per call, no automatic
pagination, inside the live budget) bounds the read.

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

from typing import Any, Optional
from urllib.parse import urlsplit

from . import people_data
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

#: A row's subtitle -- the member's headline -- by LinkedIn's typography
#: classes for it. MEASURED on the session-2 skeleton: exactly one per row,
#: under the title block.
SUBTITLE_SELECTOR = "div.t-14.t-black.t-normal"

#: A row's relation, as each follower record carries it: True, False, or
#: None for a row whose follow state is unknown.
FOLLOWS_BACK_OF: dict[str, Optional[bool]] = {
    "he_follows_back": True,
    "he_does_not_follow_back": False,
}

#: What every answer says about its own reach. A constant: no page text.
SCOPE = (
    "His own follower list, first render only: one page, no scroll and no "
    "press (SCROLL-NOT-SANCTIONED), so rows past the first render are not read "
    "and rows_seen is not his follower count. Each follower comes back as a "
    "people record beside its relation (PEOPLE-DATA-MITIGATIONS, "
    "MEMBER-ROSTERS-AS-BOUNDED-READS): declared fields only, sanitised and "
    "marked as another member's words, never stored; no button label is read. "
    "A zero is a reading only when readable is true."
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
        "followers": [],
        "names_unread": 0,
        "headlines_unread": 0,
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


async def _member_of(row: Any) -> Optional[tuple[dict[str, Any], bool]]:
    """One row's member as a people record's envelope, and whether a headline
    was read; ``None`` when no record can be built.

    THE NAME is the text of the row's ONE link the accessibility tree exposes
    -- the picture link is ``aria-hidden`` and is not one -- and that link must
    be a member's profile link, or no record is built. THE HEADLINE is the
    row's one subtitle; none, or more than one, leaves it ABSENT. Both go
    through ``people_data.Person.from_page`` (sanitised, capped, marked); the
    link is reduced to its canonical profile form there. The button's label
    is never read.
    """
    links = row.get_by_role("link")
    if await links.count() != 1:
        return None
    link = links.first
    href = people_data.canonical_profile_link(await link.get_attribute("href"))
    if href is None:
        return None
    name = await link.inner_text(timeout=WORD_TIMEOUT_MS)
    subtitles = row.locator(SUBTITLE_SELECTOR)
    headline = None
    if await subtitles.count() == 1:
        headline = await subtitles.first.inner_text(timeout=WORD_TIMEOUT_MS)
    person = people_data.Person.from_page(name=name, headline=headline, href=href)
    if person is None:
        return None
    return person.envelope(), headline is not None


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
        row = rows.nth(index)
        try:
            relation = await _relation_of(row)
        except Exception:  # noqa: BLE001 -- the row is unreadable; nothing of it is kept
            relation = "unreadable"
        if relation in ("he_follows_back", "he_does_not_follow_back"):
            out[relation] += 1
        else:
            out["unknown"] += 1
            out["unknown_why"][relation] += 1
        try:
            member = await _member_of(row)
        except Exception:  # noqa: BLE001 -- no record; nothing of the row is kept
            member = None
        if member is None:
            out["names_unread"] += 1
            continue
        envelope, headline_read = member
        if not headline_read:
            out["headlines_unread"] += 1
        out["followers"].append(
            {"member": envelope, "he_follows_back": FOLLOWS_BACK_OF.get(relation)}
        )
    out["rows_read"] = to_read
    out["readable"] = to_read > 0
    return out
