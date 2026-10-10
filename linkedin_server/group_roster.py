"""Read ONE page of a group's member list as people records.

Census rows ``N 165`` (view the full member list of a group you belong to)
and ``N 177`` (find people you know through shared group membership). Lane B5,
2026-10-10.

## WHAT DECIDED IT

* ``MEMBER-ROSTERS-AS-BOUNDED-READS`` (the orchestrator's delegated call,
  2026-09-24): a roster he can open himself is read under five conditions --
  one page per call with no automatic pagination; the group id from the tool's
  arguments only; no member's name or id stored in a tracked file; inside the
  live budget; the rows GAP until an admission and a reader. The admission is
  the roster line at the end of ``readonly._ALLOWED_URL_PATTERNS`` and the
  address is ``member_rosters.compose``'s; this module is the reader.
* ``NAMES-AT-RUNTIME`` (the operator, 2026-09-24 08:11): a read whose
  capability is people returns people's names as its result.
* ``PEOPLE-DATA-MITIGATIONS`` (the orchestrator): the six mitigations, each
  enforced by code here and shown failing in ``tests/test_group_members.py``.

``N 177`` asks for the people he KNOWS among a group's members, and the
declared field that says so is the connection degree LinkedIn draws on each
row: a member drawn ``1st`` is one of his connections. The reader returns the
degree beside every member it reads; it does not filter, because the row asks
him to find them, and a filter would hide what the page drew.

## THE CAPTURE THIS IS BUILT OVER, AND NOTHING ELSE

The live lane's session 2 (2026-09-28) loaded the member list of one group his
memberships returned and tracked its skeleton,
``tests/fixtures/live2/group_members.html`` -- every member's text reduced to
``x``, the markup LinkedIn served kept. What it draws, measured on all twenty
rows and not on a sample:

* ONE LIST, ``ul.groups-members-list__results-list``, labelled ``Members``,
  whose children are the rows: twenty ``li.groups-members-list__typeahead-
  result``.
* EACH ROW HOLDS EXACTLY ONE MEMBER LINK, ``a.ui-entity-action-row__link`` to
  ``/in/<slug>/``, and inside it one entity lockup: the NAME in
  ``.artdeco-entity-lockup__title`` (its own text, no child element), the
  HEADLINE in ``.artdeco-entity-lockup__subtitle`` (on all twenty), and a
  badge holding the DEGREE in ``.artdeco-entity-lockup__degree`` -- an
  ``aria-hidden`` span, the visible copy -- beside a screen-reader copy in
  ``.a11y-text``. Sixteen rows draw the degree; four draw an empty badge.
* BESIDE THE LINK, NOT INSIDE IT: a ``Message`` button whose ``aria-label``
  carries the member's name, and nothing else.
* AFTER THE LIST: a finite-scroll ``load`` button -- more members exist, and
  LinkedIn serves them on a press. This module never presses it.

The classes read here are LinkedIn's own component names (``artdeco-*``,
``groups-members-list__*``, ``ui-entity-action-row__*``), not generated
hashes: the capture serves the same names on every row.

## WHAT IS READ, AND ALL THAT IS READ

    link      the row's ONE member link's href, reduced by
              people_data.canonical_profile_link
    name      the title element's own text -- exactly one title inside the
              link, visible, holding no child element that carries text
    degree    the visible degree span's text, reduced to the closed
              vocabulary by people_data.canonical_degree; ``None`` when the
              row draws none (four of the capture's twenty)
    headline  the subtitle's text -- exactly one, visible -- else ABSENT
              (people_data.ABSENT, ``None``), and counted

NEVER READ: the screen-reader copy of the degree; the ``Message`` button and
its label, which names the member; the presence indicator's hidden text; the
photo's ``alt``; a badge icon's label; the group's own title above the list;
the search box. The only attribute read is the member link's ``href``.

## THE SIX MITIGATIONS, WHERE EACH LIVES

1. DECLARED FIELDS ONLY -- a :class:`people_data.Person` envelope per member,
   and nothing else about anybody.
2. SANITISED AND MARKED -- ``Person.from_page``: every string sanitised, the
   untrusted-third-party-text marker on every record.
3. NEVER STORED -- this module writes to nothing: no file, no log, no cache,
   no module-level container. A failure is counted by its exception's TYPE
   NAME, never its message, because a message can quote a page.
4. ONE PAGE -- it reads the page it is handed and loads none; the tool loads
   one. At most :data:`MAX_ROWS_READ` rows per call, above the twenty the
   capture drew. The ``load`` control is counted, never pressed, and nothing
   scrolls.
5. VISIBLE ONLY -- a row, a name or a headline the page does not show is not
   read. A member LinkedIn draws as "LinkedIn Member" comes back as exactly
   that, and nothing here looks anywhere else for who it was.
6. NOT A TARGET BY ITSELF -- no write path in this package reaches this
   module, and every write takes a link or an id its caller names.

## WHAT IT DOES NOT CLAIM

That these are all of the group's members (one page, as drawn: the capture's
list continues behind a control nobody presses here); that a name is unique
(two members can share one -- the link says which); or that the rules fit a
page drawn differently from the capture. Every rule refuses rather than
guesses, and each refusal is counted in ``people_denominators``.
"""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import group_page, people_data

#: The roster this module reads, by ``member_rosters.ROSTERS``' own name.
ROSTER = "group_members"

#: The member list: one per page on the capture.
MEMBER_LIST = "ul.groups-members-list__results-list"

#: A ROW: a direct child of the member list. Direct, so a list nested inside a
#: row (none on the capture) is never read as rows of its own.
MEMBER_ROW = (
    "ul.groups-members-list__results-list > li.groups-members-list__typeahead-result"
)

#: A MEMBER LINK, in the two spellings a LinkedIn page writes one. The capture
#: draws the relative form on all twenty rows.
MEMBER_LINK = 'a[href^="https://www.linkedin.com/in/"], a[href^="/in/"]'

#: Inside the row's one member link: the name, the headline and the visible
#: degree. Each is required to be exactly one element where it is read.
NAME = ".artdeco-entity-lockup__title"
HEADLINE = ".artdeco-entity-lockup__subtitle"
DEGREE = ".artdeco-entity-lockup__degree"

#: The finite-scroll control after the list: COUNTED, never pressed.
MORE_MEMBERS_CONTROL = "button.scaffold-finite-scroll__load-button"

#: The name element's child elements. The capture's title holds none.
NESTED = "xpath=./*"

#: The most rows one call reads. The capture drew twenty; the ceiling is a
#: budget above that, not a measurement of anything LinkedIn does.
MAX_ROWS_READ = 25

#: The closed reasons a row is not returned, in the order they are checked.
SKIP_REASONS: tuple[str, ...] = (
    "no_member_link",
    "more_than_one_member_link",
    "not_visible",
    "no_single_name",
    "name_has_nested_text",
    "no_name",
    "changed_while_read",
    "already_returned",
)


def landed_on_the_members_page(
    landed: Optional[str], identifier: Optional[str]
) -> Optional[bool]:
    """Did the navigation land on THIS group's member list? A BOOLEAN.

    ``True`` only for ``/groups/<the same digits>/members/`` on LinkedIn's
    host; ``False`` for any other page that names a group or a members tab;
    ``None`` when the landing names no group at all -- an auth wall, the feed,
    an error page. A group LinkedIn does not show him its members for
    redirects off this page, and a reading taken there would be attributed to
    a list that was never drawn, so the tool reads nothing unless this says
    ``True``.

    THE LANDING IS NEVER PUBLISHED: its path is split into segments and
    compared here, and only the boolean leaves.
    """
    digits = str(identifier or "").strip()
    if not digits:
        return None
    try:
        parts = urlsplit(str(landed or "").strip())
    except ValueError:
        return None
    segments = [segment for segment in parts.path.split("/") if segment]
    if "groups" not in segments:
        return None
    host = parts.netloc.lower()
    return (
        host in ("www.linkedin.com", "linkedin.com")
        and segments == ["groups", digits, "members"]
        and group_page.group_page_url(digits).get("built") is True
    )


async def _href(handle: Any) -> Optional[str]:
    """A handle's href as a canonical profile link, or ``None``."""
    return people_data.canonical_profile_link(await handle.get_attribute("href"))


async def _one(handle: Any, selector: str) -> Any:
    """The ONE element ``selector`` matches under ``handle``, else ``None``."""
    found = list(await handle.query_selector_all(selector))
    return found[0] if len(found) == 1 else None


async def _visible_text(element: Any) -> Optional[str]:
    """The element's rendered text if it is shown, else ``None``."""
    if element is None or not await element.is_visible():
        return None
    return await element.inner_text()


async def _read_row(row: Any) -> Any:
    """One row: a :class:`people_data.Person` and whether its headline was
    read, or the SKIP_REASONS entry that stopped it."""
    links = list(await row.query_selector_all(MEMBER_LINK))
    if not links:
        return "no_member_link"
    if len(links) > 1:
        return "more_than_one_member_link"
    link_handle = links[0]
    link = await _href(link_handle)
    if link is None:
        return "no_member_link"
    if not await row.is_visible() or not await link_handle.is_visible():
        return "not_visible"
    title = await _one(link_handle, NAME)
    if title is None:
        return "no_single_name"
    for child in await title.query_selector_all(NESTED):
        if str(await child.text_content() or "").strip():
            return "name_has_nested_text"
    name = await _visible_text(title)
    if name is None:
        return "not_visible"
    degree = await _visible_text(await _one(link_handle, DEGREE))
    headline = await _visible_text(await _one(link_handle, HEADLINE))
    # THE LINK AGAIN, AFTER EVERY TEXT READ. A row the page reused for another
    # member meanwhile would pair one person's name with another's link; a
    # row whose link moved is skipped, never returned.
    if await _href(link_handle) != link:
        return "changed_while_read"
    person = people_data.Person.from_page(
        name=name, headline=headline, href=link, degree=degree
    )
    if person is None:
        return "no_name"
    return person, headline is not None


async def _count(page: Any, selector: str) -> Optional[int]:
    """A locator count, or ``None`` when the page could not be asked."""
    try:
        value = await page.locator(selector).count()
    except Exception:  # noqa: BLE001 -- a count that failed is not a zero
        return None
    return value if isinstance(value, int) and not isinstance(value, bool) else None


async def read_group_members(page: Any) -> dict[str, Any]:
    """The members the list draws, as people-record envelopes.

    Returns ``{"people": [<envelope>, ...], "people_denominators": {...}}``.
    Every string in ``people`` sits inside a :class:`people_data.Person`
    envelope; ``people_denominators`` holds integers, ``None`` for a count the
    page could not answer, and exception TYPE names. ``rows_attempted``
    counts the rows the call TRIED, at most :data:`MAX_ROWS_READ`; each one
    tried is returned, skipped for a counted reason, or counted as failed.
    ``more_members_control_drawn`` counts the list's own ``load`` control,
    which says LinkedIn holds more members than this page drew -- it is
    never pressed. Reads the page it is handed; loads nothing, presses
    nothing, scrolls nothing, and never raises.
    """
    skipped = {reason: 0 for reason in SKIP_REASONS}
    failed: dict[str, int] = {}
    people: list[dict[str, Any]] = []
    returned: set[str] = set()
    headline_unread = 0
    degree_drawn = 0

    try:
        rows = list(await page.locator(MEMBER_ROW).element_handles())
    except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
        failed[type(exc).__name__] = 1
        rows = []
    to_read = min(len(rows), MAX_ROWS_READ)

    for row in rows[:to_read]:
        try:
            verdict = await _read_row(row)
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            failed[kind] = failed.get(kind, 0) + 1
            continue
        if isinstance(verdict, str):
            skipped[verdict] += 1
            continue
        person, headline_read = verdict
        if person.link in returned:
            skipped["already_returned"] += 1
            continue
        returned.add(person.link)
        if not headline_read:
            headline_unread += 1
        if person.degree is not None:
            degree_drawn += 1
        people.append(person.envelope())

    return {
        "people": people,
        "people_denominators": {
            "member_lists_seen": await _count(page, MEMBER_LIST),
            "rows_seen": len(rows),
            "rows_attempted": to_read,
            "people_returned": len(people),
            "degree_drawn": degree_drawn,
            "skipped": skipped,
            "headline_unread": headline_unread,
            "more_members_control_drawn": await _count(page, MORE_MEMBERS_CONTROL),
            "failed": failed,
        },
    }
