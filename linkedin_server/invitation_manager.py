"""His invitation manager, both tabs: the invitations he has RECEIVED (census ``N 13``) and the ones he has SENT (``N 9``).

TWO ADMITTED ADDRESSES, :data:`RECEIVED_URL` and :data:`SENT_URL`. ``readonly.py``
admits each by a two-gate pair (an anchored allowlist line and a pattern
exemption excusing ``invitation`` for that address alone; lane A,
READ-PAST-AN-ACT-SUBSTRING). This module never navigates: the tool loads the
address and hands the open page here. Nothing is pressed: Accept, Ignore and
Withdraw are read as LinkedIn's WORDS on the rows they mark, and none of them
is ever clicked by this module.

MEASURED on the live lane's session-11 captures (loads 14 and 15; tracked
copies ``tests/fixtures/live11/invitations.html`` and
``invitations_sent.html``, and the copies with LinkedIn's words put back by
keyed shape, ``tests/fixtures/synthetic/live11_invitations_words.html`` and
``live11_invitations_sent_words.html``, written by
``scripts/_build_live11_word_fixtures.py``):

* ONE ``main``; one tab strip of two links, ``Received`` and ``Sent``, the
  open tab's link ``aria-current="true"``. ``Sent`` is the one word the
  tracked copies keep, so the SIDE is read from it alone: the strip's link
  whose own text is ``Sent`` is current on the sent tab and not on the
  received one.
* RECEIVED: three invitations, each a ``role=listitem`` holding exactly two
  buttons whose visible words are ``Ignore`` and ``Accept``. Two are a
  member's -- one paragraph holding the member's link and LinkedIn's fixed
  ``wants to connect`` -- and one a Page's: a ``/company/`` link and the fixed
  ``invited you to subscribe to`` before a newsletter's title. The same page
  draws nineteen suggestion cards, each a ``role=listitem`` with a ``Connect``
  button and no Accept, which is why a row is a list item WITH an Accept.
  No row draws a headline; the lines under the name are mutual-connection
  insights naming other members, and they are never read.
* SENT: five invitations, each a ``role=listitem`` holding exactly one link
  whose visible word is ``Withdraw`` (an action link to the site root), one
  member link (the picture), the member's name as the row's one paragraph
  with no child element, a headline, and LinkedIn's relative time, ``Sent 2
  weeks ago`` (three rows) or ``Sent 1 month ago`` (two). The tab draws one
  category link, ``.../sent/CONNECTION/``, current: people invitations only.

WHAT COMES BACK. Per row read, a people record (:mod:`people_data`): the
member (:class:`people_data.Person` -- name, headline where drawn, canonical
profile link) or, for a Page's invitation, the Page
(:class:`people_data.Organisation` -- its name, its link only when numeric);
beside it closed words and integers only: the invitation's ``kind``, the
sent invitation's age as ``{"count", "unit"}``. Under PEOPLE-DATA-MITIGATIONS:
declared fields only; sanitised and marked; never stored (nothing here writes,
logs or caches); bounded to one page, the first render, at most
:data:`MAX_ROWS_READ` rows (MEMBER-ROSTERS-AS-BOUNDED-READS); visible only;
never a target -- this module acts on nobody, and no button's or link's
``aria-label`` (live, it carries the member's name) is ever read.

AN EMPTY LIST RAISES. No capture draws either tab empty, so no empty state is
measured that could corroborate a zero: a tab that reads no row raises
:class:`ExtractionFailedError`, which never quotes the page.

AIMED BY ROLE, STRUCTURE AND LINKEDIN'S OWN WORDS, NEVER BY POSITION OR A
CLASS NAME (NO-INDEX-PINNED-JUDGEMENTS): the classes on these pages are hashed
tokens that change between builds, and no row is chosen by its place.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from . import people_data
from .config import BASE_URL
from .errors import ExtractionFailedError

#: THE TWO ADDRESSES, admitted in ``readonly.py``; nothing here builds another.
RECEIVED_URL = f"{BASE_URL}/mynetwork/invitation-manager/"
SENT_URL = f"{BASE_URL}/mynetwork/invitation-manager/sent/"

_HOST = "www.linkedin.com"
#: The received tab's path: the admitted address, and only it. LinkedIn's own
#: tab strip links the tab as ``/mynetwork/invitation-manager/received``
#: (measured), a spelling the boundary does not admit; ``readonly.py``'s
#: admission says a redirect there is RECORDED and gets its own line, so a
#: landing on it refuses as ``landed_elsewhere`` rather than being read.
_RECEIVED_PATHS = ("/mynetwork/invitation-manager",)
_SENT_PATH = "/mynetwork/invitation-manager/sent"

#: LinkedIn's own words, compared exactly and never returned.
SENT_TAB_WORD = "Sent"
ACCEPT_WORD = "Accept"
IGNORE_WORD = "Ignore"
WITHDRAW_WORD = "Withdraw"
CONNECT_PHRASE = "wants to connect"
NEWSLETTER_PHRASE = "invited you to subscribe to"

#: A whole element text equal to a word, whitespace aside.
def _exactly(word: str) -> "re.Pattern[str]":
    return re.compile(r"^\s*" + re.escape(word) + r"\s*$")


#: A paragraph whose own text ENDS with a phrase: the received row's subject
#: line, ``<name> wants to connect``.
def _ending_with(phrase: str) -> "re.Pattern[str]":
    return re.compile(r"(^|\s)" + re.escape(phrase) + r"\s*$")


#: The kinds a received invitation may be read as. ``connection`` and
#: ``newsletter`` are MEASURED (session 11); every other invitation -- a
#: Page, an event, a group -- is ``other``, counted, its sender not read,
#: because no capture draws one.
KINDS = ("connection", "newsletter", "other")

#: Which side of the manager is open.
SIDES = ("received", "sent", "unknown")

#: Why a whole read refuses. Closed.
REFUSALS = ("not_the_received_side", "not_the_sent_side", "side_unreadable", "landed_elsewhere")

#: Why one row was not read in full. Closed.
ROW_GAPS = ("controls_not_the_measured_pair", "sender_unread", "age_unread", "unreadable")

#: LinkedIn's relative time on a sent invitation: ``Sent today``, ``Sent
#: yesterday``, or ``Sent <n> <unit>(s) ago``. MEASURED: ``Sent 2 weeks ago``
#: and ``Sent 1 month ago``; the other units are the same template, DERIVED.
_SENT_AGO = re.compile(
    r"^\s*Sent (?:(today|yesterday)|(\d{1,3}) (minute|hour|day|week|month|year)s? ago)\s*$"
)
AGE_UNITS = ("minute", "hour", "day", "week", "month", "year")

#: Rows read per call, at most. The first renders draw three and five; the
#: bound exists so a page that draws hundreds cannot turn a call into a sweep.
MAX_ROWS_READ = 100

#: How long one element's text read may wait, in ms.
TEXT_TIMEOUT_MS = 2000

SCOPE_RECEIVED = (
    "His received invitations, the invitation manager's first render only: one "
    "page, no scroll and no press, so rows past the first render are not read "
    "and rows_seen is not his pending count. Each invitation comes back with "
    "its kind and its sender as a people record (PEOPLE-DATA-MITIGATIONS, "
    "MEMBER-ROSTERS-AS-BOUNDED-READS): a member as a person record, a Page as "
    "an organisation record; declared fields only, sanitised and marked as "
    "another member's words, never stored. Accept and Ignore are read as "
    "words and never pressed; no control's label is read. A zero raises."
)
SCOPE_SENT = (
    "The invitations he has sent and not yet seen answered, the Sent tab's "
    "first render only: one page, no scroll and no press. Each comes back as "
    "a person record beside its age in LinkedIn's own words reduced to a count "
    "and a unit (PEOPLE-DATA-MITIGATIONS, MEMBER-ROSTERS-AS-BOUNDED-READS). "
    "The Withdraw link is read as a word and never pressed; no control's label "
    "is read. A zero raises."
)


def _path_of(landed: Any) -> Optional[str]:
    if not isinstance(landed, str) or not landed:
        return None
    try:
        parts = urlsplit(landed)
    except ValueError:
        return None
    if parts.scheme != "https" or parts.netloc != _HOST:
        return None
    return parts.path.rstrip("/")


def landed_on_received(landed: Any) -> bool:
    """Did the load land on the received tab? Scheme, host and path; a query
    or fragment is ignored. PURE."""
    return _path_of(landed) in _RECEIVED_PATHS


def landed_on_sent(landed: Any) -> bool:
    """Did the load land on the sent tab? PURE."""
    return _path_of(landed) == _SENT_PATH


def _reading(surface: str, scope: str, items_key: str) -> dict[str, Any]:
    """An answer's shape with every count at zero. Every key is fixed here."""
    return {
        "surface": surface,
        "side": "unknown",
        "refused": None,
        "tab_links_seen": 0,
        "rows_seen": 0,
        "rows_read": 0,
        items_key: [],
        "row_gaps": {gap: 0 for gap in ROW_GAPS},
        "one_page": True,
        "beyond_first_render": "not_read",
        "readable": False,
        "scope": scope,
    }


def received_landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the received tab. Nothing
    was read, and nothing of the landing is said: its address is LinkedIn's."""
    out = _received_reading()
    out["refused"] = "landed_elsewhere"
    return out


def sent_landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the sent tab."""
    out = _sent_reading()
    out["refused"] = "landed_elsewhere"
    return out


def _received_reading() -> dict[str, Any]:
    out = _reading("received_invitations", SCOPE_RECEIVED, "invitations")
    out["kinds"] = {kind: 0 for kind in KINDS}
    return out


def _sent_reading() -> dict[str, Any]:
    return _reading("sent_invitations", SCOPE_SENT, "invitations")


async def _side(main: Any) -> tuple[str, int]:
    """``(side, tab links seen)`` from COUNTS ALONE -- no tab's text is read.

    The manager's strip draws exactly one link whose own text is ``Sent``:
    current on the sent tab, not current on the received one. Exactly one
    current link in the strip's navigation is required either way; anything
    else is ``unknown``.
    """
    links = main.locator("nav a")
    seen = await links.count()
    sent = links.filter(has_text=_exactly(SENT_TAB_WORD))
    sent_links = await sent.count()
    sent_current = await main.locator('nav a[aria-current="true"]').filter(
        has_text=_exactly(SENT_TAB_WORD)
    ).count()
    if sent_links != 1:
        return "unknown", seen
    if sent_current == 1:
        return "sent", seen
    received_current = await main.locator('nav a[aria-current="true"]').count()
    return ("received", seen) if received_current >= 1 else ("unknown", seen)


def _rows_marked_by(page: Any, main: Any, tag: str, word: str) -> Any:
    """The list items of ``main`` that hold an element ``tag`` whose whole
    visible text is ``word``. The inner locator is built on ``page``, as
    Playwright requires of ``filter(has=...)``; it is evaluated inside each
    item."""
    marker = page.locator(tag).filter(has_text=_exactly(word))
    return main.get_by_role("listitem").filter(has=marker)


async def _received_controls_are_the_pair(row: Any) -> bool:
    """Exactly two buttons, whose visible words are Ignore and Accept, once
    each -- counted by text match, never read out."""
    buttons = row.locator("button")
    if await buttons.count() != 2:
        return False
    accept = await buttons.filter(has_text=_exactly(ACCEPT_WORD)).count()
    ignore = await buttons.filter(has_text=_exactly(IGNORE_WORD)).count()
    return accept == 1 and ignore == 1


async def _received_kind_and_sender(row: Any) -> tuple[str, Optional[dict[str, Any]]]:
    """``(kind, sender envelope or None)`` for one received row.

    A member's invitation is the one paragraph whose text ends with
    ``wants to connect``, holding exactly one member link: the name is that
    link's text. A Page's newsletter invitation is the one paragraph holding
    ``invited you to subscribe to``, with exactly one ``/company/`` link: the
    Page's name is that link's text, its link kept only when numeric. Any
    other row is ``other`` and its sender is not read.
    """
    connect = row.locator("p").filter(has_text=_ending_with(CONNECT_PHRASE))
    if await connect.count() == 1:
        links = connect.locator('a[href*="/in/"]')
        if await links.count() != 1:
            return "connection", None
        link = links.first
        href = people_data.canonical_profile_link(await link.get_attribute("href"))
        if href is None:
            return "connection", None
        person = people_data.Person.from_page(
            name=await link.inner_text(timeout=TEXT_TIMEOUT_MS), href=href
        )
        return "connection", (person.envelope() if person is not None else None)
    newsletter = row.locator("p").filter(has_text=re.compile(re.escape(NEWSLETTER_PHRASE)))
    if await newsletter.count() == 1:
        pages = newsletter.locator('a[href*="/company/"]')
        if await pages.count() != 1:
            return "newsletter", None
        page_link = pages.first
        organisation = people_data.Organisation.from_page(
            name=await page_link.inner_text(timeout=TEXT_TIMEOUT_MS),
            href=await page_link.get_attribute("href"),
        )
        return "newsletter", (organisation.envelope() if organisation is not None else None)
    return "other", None


async def read_received_invitations(page: Any) -> dict[str, Any]:
    """His received invitations on the already-open received tab.

    The page must already be at :data:`RECEIVED_URL` (the tool loads it and
    checks the landing). One read of the first render; no navigation, press or
    scroll. Refuses -- the denominators kept, nothing read -- when the strip
    says the sent tab is open (``not_the_received_side``) or cannot say
    (``side_unreadable``). Raises when no invitation row is drawn.
    """
    out = _received_reading()
    main = page.locator("main")
    if await main.count() != 1:
        out["refused"] = "side_unreadable"
        return out
    side, out["tab_links_seen"] = await _side(main)
    out["side"] = side
    if side != "received":
        out["refused"] = "not_the_received_side" if side == "sent" else "side_unreadable"
        return out
    rows = _rows_marked_by(page, main, "button", ACCEPT_WORD)
    out["rows_seen"] = await rows.count()
    if out["rows_seen"] == 0:
        raise ExtractionFailedError(
            "the received tab drew no invitation row (a list item holding an "
            "Accept button), and no empty state for this tab has ever been "
            "captured to corroborate a zero. Reporting none would be "
            "indistinguishable from a page that did not render, so it is "
            "reported as a failure instead.",
            url=RECEIVED_URL,
        )
    to_read = min(out["rows_seen"], MAX_ROWS_READ)
    for index in range(to_read):
        row = rows.nth(index)
        try:
            if not await _received_controls_are_the_pair(row):
                out["row_gaps"]["controls_not_the_measured_pair"] += 1
                continue
            kind, sender = await _received_kind_and_sender(row)
        except Exception:  # noqa: BLE001 -- the row is unreadable; nothing of it is kept
            out["row_gaps"]["unreadable"] += 1
            continue
        out["kinds"][kind] += 1
        if sender is None:
            out["row_gaps"]["sender_unread"] += 1
        out["invitations"].append({"kind": kind, "sender": sender})
    out["rows_read"] = to_read
    # READABLE MEANS A SENDER WAS READ, not that a row was counted: a row
    # whose sender could not be read is still listed, with its kind.
    out["readable"] = any(item["sender"] is not None for item in out["invitations"])
    return out


def parse_sent_age(text: Any) -> Optional[dict[str, Any]]:
    """LinkedIn's ``Sent ...`` line as ``{"count": int, "unit": str}``, or
    ``None``. ``Sent today`` is ``{"count": 0, "unit": "day"}`` and ``Sent
    yesterday`` ``{"count": 1, "unit": "day"}``. PURE; the text is compared,
    never returned."""
    if not isinstance(text, str):
        return None
    found = _SENT_AGO.match(text)
    if found is None:
        return None
    if found.group(1) == "today":
        return {"count": 0, "unit": "day"}
    if found.group(1) == "yesterday":
        return {"count": 1, "unit": "day"}
    return {"count": int(found.group(2)), "unit": found.group(3)}


#: A paragraph whose whole text is LinkedIn's sent-age line.
_SENT_AGO_LINE = re.compile(_SENT_AGO.pattern)


async def _sent_row(row: Any) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]], tuple[str, ...]]:
    """``(member envelope, age, gaps)`` for one sent row.

    THE MEMBER: the row's one member link (the picture) gives the link; the
    name is the row's one paragraph with no child element; the headline is
    the one other paragraph that is not the age line. THE AGE: the one
    paragraph matching LinkedIn's sent-age template.
    """
    gaps: list[str] = []
    links = row.locator('a[href*="/in/"]')
    names = row.locator("p:not(:has(*))")
    member = None
    if await links.count() == 1 and await names.count() == 1:
        href = people_data.canonical_profile_link(await links.first.get_attribute("href"))
        lines = row.locator("p:has(> span)")
        headline_lines = lines.filter(has_not_text=_SENT_AGO_LINE)
        headline = None
        if await headline_lines.count() == 1:
            headline = await headline_lines.first.inner_text(timeout=TEXT_TIMEOUT_MS)
        if href is not None:
            person = people_data.Person.from_page(
                name=await names.first.inner_text(timeout=TEXT_TIMEOUT_MS),
                headline=headline,
                href=href,
            )
            member = person.envelope() if person is not None else None
    if member is None:
        gaps.append("sender_unread")
    age = None
    ages = row.locator("p").filter(has_text=_SENT_AGO_LINE)
    if await ages.count() == 1:
        age = parse_sent_age(await ages.first.inner_text(timeout=TEXT_TIMEOUT_MS))
    if age is None:
        gaps.append("age_unread")
    return member, age, tuple(gaps)


async def read_sent_invitations(page: Any) -> dict[str, Any]:
    """The invitations he has sent, on the already-open sent tab.

    The page must already be at :data:`SENT_URL`. One read of the first
    render; no navigation, press or scroll. Refuses when the strip says the
    received tab is open (``not_the_sent_side``) or cannot say
    (``side_unreadable``). Raises when no invitation row is drawn.
    """
    out = _sent_reading()
    main = page.locator("main")
    if await main.count() != 1:
        out["refused"] = "side_unreadable"
        return out
    side, out["tab_links_seen"] = await _side(main)
    out["side"] = side
    if side != "sent":
        out["refused"] = "not_the_sent_side" if side == "received" else "side_unreadable"
        return out
    rows = _rows_marked_by(page, main, "a", WITHDRAW_WORD)
    out["rows_seen"] = await rows.count()
    if out["rows_seen"] == 0:
        raise ExtractionFailedError(
            "the sent tab drew no invitation row (a list item holding a "
            "Withdraw link), and no empty state for this tab has ever been "
            "captured to corroborate a zero. Reporting none would be "
            "indistinguishable from a page that did not render, so it is "
            "reported as a failure instead.",
            url=SENT_URL,
        )
    to_read = min(out["rows_seen"], MAX_ROWS_READ)
    for index in range(to_read):
        row = rows.nth(index)
        try:
            if await row.locator("a").filter(has_text=_exactly(WITHDRAW_WORD)).count() != 1:
                out["row_gaps"]["controls_not_the_measured_pair"] += 1
                continue
            member, age, gaps = await _sent_row(row)
        except Exception:  # noqa: BLE001 -- the row is unreadable; nothing of it is kept
            out["row_gaps"]["unreadable"] += 1
            continue
        for gap in gaps:
            out["row_gaps"][gap] += 1
        out["invitations"].append({"member": member, "sent_ago": age})
    out["rows_read"] = to_read
    # READABLE MEANS A MEMBER WAS READ, not that a row was counted.
    out["readable"] = any(item["member"] is not None for item in out["invitations"])
    return out
