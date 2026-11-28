"""LinkedIn Learning, read: the courses its home lists, his in-progress list, his career goal.

Census rows ``J 152`` (*Browse LinkedIn Learning's home: the courses it lists*),
``J 154`` (*View the courses in progress in your LinkedIn Learning library*)
and ``J 156`` (*See his career goal on LinkedIn Learning's "My career
journey"*) -- each the captured half its row kept when LEARNING-ROWS-SPLIT
split it (the orchestrator, 2026-11-27). Lane build28, 2026-11-28, over the
live lane's session-12 captures, LinkedIn's words measured by keyed shape
(``scripts/_build_build28_word_skeletons.py``):

* load 23, ``/learning/`` (``tests/fixtures/live12/learning_words.html``): in
  ``main``, ONE hero item (``data-view-name="learning-home-hero-item"``, an
  ``h3`` headline and a badge, ``Popular``) and THREE carousels of FIVE cards
  each on the first render (``data-view-name="learning-home-carousel-card"``):
  each card a link to ``/learning/<course>``, a type label (``Course`` on all
  fifteen), a headline (the course's title), a thumbnail label (its duration,
  ``1h 9m`` .. ``59m``, fifteen distinct) and, on three, a badge
  (``Popular``). Every title, section heading and instructor ``x``.
* load 25, ``/learning/me/my-library/`` redirected one level deeper, to the
  IN-PROGRESS tab (``learning_library_words.html``): the library's tab links,
  the one marked ``aria-current="page"`` reading
  ``/learning/me/my-library/in-progress``; ONE card
  (``data-view-name="learning-my-learning-content-card"``, carrying
  ``data-live-test-in-progress-card``): a headline, ``Course``, ``1h 17m``,
  ``Updated Apr 2022``, an authors line opening ``By:``.
* load 24, ``/learning/career-journey/`` (``learning_journey_words.html``):
  ONE ``section`` labelled ``Career goal``, its ``h3`` reading ``Goal``, a
  button reading ``Edit goal``, and one line under them -- its words ``x``,
  ONE run of them in bold. No link in ``main``.

## WHAT LEAVES, AND UNDER WHICH RULING

* A COURSE'S TITLE is an item of other people's content -- NAMES-AT-RUNTIME:
  returned at runtime as a ``people_data.OrganisationProse`` record
  (``read_from`` ``learning_course_title``), sanitised, bounded, marked
  untrusted, never stored. Beside it only closed words and integers: its type
  (``course``, else ``other``), its duration in seconds by LinkedIn's own
  grammar, its badge (``popular``, else counted), whether it is the hero.
  NEVER READ: its link (the slug is its title spelled again), its instructor
  (a person this row does not ask for), its screen-reader copy, its viewer
  count, any section heading.
* HIS CAREER GOAL is his own text -- HIS-OWN-TEXT-AT-RUNTIME: the section's
  one line as drawn, and the bold run in it, sanitised and bounded, never
  stored; the tool-envelope guard admits it through ``ADMITTED_OWN_TEXT``.
  The ``Edit goal`` button is read for its word and never pressed; setting a
  goal is row ``J 172``.

## THE ZERO RULE

No card read, on a page whose own markers drew, is not "none": no empty home,
no empty in-progress tab and no page without a goal has ever been captured,
so each raises rather than answer an empty list.

## IT PRESSES NOTHING

Every read is a locator read in the skeleton grammar. Nothing is clicked,
scrolled or typed; no carousel is advanced past its first render.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import coerce, people_data
from linkedin_server.errors import ExtractionFailedError

#: The three pages, each the read boundary's admitted address for it.
HOME_URL = "https://www.linkedin.com/learning/"
IN_PROGRESS_URL = "https://www.linkedin.com/learning/me/my-library/in-progress/"
JOURNEY_URL = "https://www.linkedin.com/learning/career-journey/"

#: Each page's own path, as a landing must keep it.
HOME_PATH = "/learning"
IN_PROGRESS_PATH = "/learning/me/my-library/in-progress"
JOURNEY_PATH = "/learning/career-journey"

MAIN = "main"

#: THE HOME, MEASURED (load 23).
HERO = MAIN + ' div[data-view-name="learning-home-hero-item"]'
HERO_TITLE = 'h3[class*="hero-item__headline"]'
HERO_BADGE = 'span[class*="hero-item__badge"]'
HOME_CARDS = MAIN + ' div[data-view-name="learning-home-carousel-card"]'

#: THE IN-PROGRESS TAB, MEASURED (load 25).
LIBRARY_TABS = MAIN + ' div[role="navigation"] a[aria-current="page"]'
LIBRARY_CARDS = MAIN + ' div[data-view-name="learning-my-learning-content-card"]'

#: A card's parts, the same class words on both pages' cards.
CARD_TITLE = 'span[class*="lls-card-headline"]'
CARD_TYPE = 'span[class*="lls-card-entity-type"]'
CARD_DURATION = 'div[class*="lls-card-thumbnail-label"]'
CARD_BADGE = 'div[class*="lls-card-badge"]'
CARD_UPDATED = 'span[class*="lls-card-released-on"]'
CARD_LINK = 'a[href*="/learning/"]'

#: THE CAREER GOAL, MEASURED (load 24).
GOAL_SECTION = MAIN + ' section[aria-label="Career goal"]'
GOAL_HEADING_WORD = "Goal"
GOAL_LINE = 'div[class*="career-goal__subtext"]'
GOAL_EDIT_WORD = "Edit goal"

#: A card's type label, to this module's own word. Measured: ``Course``.
TYPES: dict[str, str] = {"Course": "course"}
#: A card's badge, to this module's own word. Measured: ``Popular``.
BADGES: dict[str, str] = {"Popular": "popular"}

#: LinkedIn's duration grammar, MEASURED as ``1h 9m``, ``3h``, ``27m``; the
#: screen-reader copy's ``27m 10s`` form is the same grammar, seconds last.
_DURATION = re.compile(r"(?:([0-9]{1,3})h)? ?(?:([0-9]{1,2})m)? ?(?:([0-9]{1,2})s)?")

#: The update line, MEASURED as ``Updated Apr 2022``.
_UPDATED = re.compile(r"(Updated|Released) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ([0-9]{4})")
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

#: The source word a course title's record carries.
COURSE_TITLE = "learning_course_title"

#: The most cards read on one page: the first render draws sixteen on the
#: home and one in the library. A cost ceiling, not a LinkedIn limit.
MAX_CARDS = 60

#: The longest goal line kept. LinkedIn's own cap is not measured; a longer
#: line is cut and ``goal_truncated`` says so.
GOAL_CAP = 300

READ_TIMEOUT_MS = 2000


def collapsed(text: Any) -> str:
    """White space collapsed and the ends trimmed; ``""`` for a non-string."""
    return " ".join(text.split()) if isinstance(text, str) else ""


def landed_on(landed: Any, path: str) -> bool:
    """Whether the one load kept ``path``. A yes or a no; the address goes nowhere."""
    if not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.netloc.lower() == "www.linkedin.com"
        and parts.path.rstrip("/") == path
    )


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not keep its page's path."""
    return {
        "ok": False,
        "pages_loaded": 1,
        "refused": "landed_elsewhere",
        "why": (
            "the load did not keep the Learning page's own address, so the page "
            "was not read."
        ),
    }


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        return coerce.as_count(await locator.count())
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0


async def _text(locator: Any, failed: list[int]) -> str:
    try:
        return collapsed(await locator.inner_text(timeout=READ_TIMEOUT_MS))
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return ""


async def _only_text(scope: Any, selector: str, failed: list[int]) -> Optional[str]:
    """The text of the ONE element ``selector`` matches in ``scope``, else
    ``None`` (none, or more than one)."""
    found = scope.locator(selector)
    if await _count(found, failed) != 1:
        return None
    return await _text(found, failed)


def duration_seconds(line: Any) -> Optional[int]:
    """A thumbnail's duration in seconds, by LinkedIn's grammar, or ``None``. PURE."""
    text = collapsed(line)
    found = _DURATION.fullmatch(text) if text else None
    if not found or not any(found.groups()):
        return None
    hours, minutes, seconds = (int(g) if g else 0 for g in found.groups())
    if minutes > 59 or seconds > 59:
        return None
    return hours * 3600 + minutes * 60 + seconds


def updated_month(line: Any) -> Optional[dict[str, str]]:
    """``{"kind": "updated"|"released", "month": "YYYY-MM"}`` off a card's
    update line, or ``None``. PURE."""
    found = _UPDATED.fullmatch(collapsed(line))
    if not found:
        return None
    return {
        "kind": found.group(1).lower(),
        "month": "%s-%02d" % (found.group(3), _MONTHS.index(found.group(2)) + 1),
    }


async def _course(card: Any, failed: list[int], *, title_selector: str,
                  badge_selector: str, featured: bool) -> tuple[Optional[dict[str, Any]], dict[str, int]]:
    """One card, or ``(None, tally)`` when its title does not read. The title
    leaves as a record; everything else as a closed word or an integer."""
    tally = {"unknown_types": 0, "unknown_badges": 0}
    title = await _only_text(card, title_selector, failed)
    record = people_data.OrganisationProse.from_page(text=title, read_from=COURSE_TITLE)
    if record is None:
        return None, tally
    kind_word = await _only_text(card, CARD_TYPE, failed)
    kind = TYPES.get(kind_word or "")
    if kind is None and kind_word is not None:
        tally["unknown_types"] += 1
    badge_word = await _only_text(card, badge_selector, failed)
    badge = BADGES.get(badge_word or "")
    if badge is None and badge_word:
        tally["unknown_badges"] += 1
    duration = duration_seconds(await _only_text(card, CARD_DURATION, failed))
    return {
        "title": record.envelope(),
        "type": kind or ("other" if kind_word is not None else None),
        "duration_seconds": duration,
        "badge": badge,
        "featured": featured,
    }, tally


async def read_learning_home(page: Any) -> dict[str, Any]:
    """The courses the Learning home ``page`` already shows: the hero, then
    every carousel card on its first render, in page order.

    Raises ``ExtractionFailedError`` (its ``url`` the address this module asks
    for) when no course is read: no empty home has been captured.
    """
    failed = [0]
    courses: list[dict[str, Any]] = []
    out: dict[str, Any] = {"unknown_types": 0, "unknown_badges": 0, "cards_seen": 0,
                           "cards_withheld": 0, "cards_unlinked": 0}

    async def take(card: Any, **kw: Any) -> None:
        out["cards_seen"] += 1
        if await _count(card.locator(CARD_LINK), failed) < 1 and not kw["featured"]:
            out["cards_unlinked"] += 1
        course, tally = await _course(card, failed, **kw)
        for key, value in tally.items():
            out[key] += value
        if course is None:
            out["cards_withheld"] += 1
        else:
            courses.append(course)

    hero = page.locator(HERO)
    if await _count(hero, failed) == 1:
        await take(hero, title_selector=HERO_TITLE, badge_selector=HERO_BADGE, featured=True)
    cards = page.locator(HOME_CARDS)
    total = await _count(cards, failed)
    for index in range(min(total, MAX_CARDS)):
        await take(cards.nth(index), title_selector=CARD_TITLE, badge_selector=CARD_BADGE,
                   featured=False)
    out["cards_beyond_bound"] = max(total - MAX_CARDS, 0)
    out["reads_failed"] = failed[0]
    if not courses:
        raise ExtractionFailedError(
            "no course was read on the LinkedIn Learning home, and no empty home "
            "has ever been captured; an empty list here would be "
            f"indistinguishable from a broken read ({out['cards_seen']} card(s) "
            "seen).",
            url=HOME_URL,
        )
    return {"courses": courses, "course_count": len(courses), **out}


async def read_in_progress(page: Any) -> dict[str, Any]:
    """The courses on his library's in-progress tab ``page`` already shows.

    Raises ``ExtractionFailedError`` when the tab marked current is not the
    in-progress one, or when no course is read: no empty in-progress tab has
    been captured.
    """
    failed = [0]
    tabs = page.locator(LIBRARY_TABS)
    current: Optional[str] = None
    if await _count(tabs, failed) == 1:
        try:
            href = await tabs.get_attribute("href", timeout=READ_TIMEOUT_MS)
        except Exception:  # noqa: BLE001 -- counted; the message may quote the page
            failed[0] += 1
            href = None
        current = "in_progress" if isinstance(href, str) and urlsplit(href).path.rstrip("/") == IN_PROGRESS_PATH else "other"
    if current != "in_progress":
        raise ExtractionFailedError(
            "his library does not mark its in-progress tab as the one shown, so "
            "no card on it is read as a course in progress.",
            url=IN_PROGRESS_URL,
        )
    courses: list[dict[str, Any]] = []
    out: dict[str, Any] = {"unknown_types": 0, "unknown_badges": 0, "cards_seen": 0,
                           "cards_withheld": 0}
    cards = page.locator(LIBRARY_CARDS)
    total = await _count(cards, failed)
    for index in range(min(total, MAX_CARDS)):
        card = cards.nth(index)
        out["cards_seen"] += 1
        course, tally = await _course(card, failed, title_selector=CARD_TITLE,
                                      badge_selector=CARD_BADGE, featured=False)
        for key, value in tally.items():
            out[key] += value
        if course is None:
            out["cards_withheld"] += 1
            continue
        course.pop("featured")
        course["updated"] = updated_month(await _only_text(card, CARD_UPDATED, failed))
        courses.append(course)
    out["cards_beyond_bound"] = max(total - MAX_CARDS, 0)
    out["reads_failed"] = failed[0]
    if not courses:
        raise ExtractionFailedError(
            "no course was read on his library's in-progress tab, and no empty "
            "tab has ever been captured; an empty list here would be "
            f"indistinguishable from a broken read ({out['cards_seen']} card(s) "
            "seen).",
            url=IN_PROGRESS_URL,
        )
    return {"tab": "in_progress", "courses": courses, "course_count": len(courses), **out}


async def read_career_goal(page: Any) -> dict[str, Any]:
    """His career goal, off the "My Career Journey" ``page`` already shows.

    Raises ``ExtractionFailedError`` when the page draws no section labelled
    ``Career goal`` with its heading ``Goal`` -- once -- or no goal line in
    it: no page without a goal has been captured.
    """
    failed = [0]
    sections = page.locator(GOAL_SECTION)
    if await _count(sections, failed) != 1:
        raise ExtractionFailedError(
            "the career journey page does not draw exactly one section labelled "
            "'Career goal', so no goal is read off it.",
            url=JOURNEY_URL,
        )
    headings = sections.locator("h3")
    words = [await _text(headings.nth(i), failed) for i in range(min(await _count(headings, failed), 5))]
    line = await _only_text(sections, GOAL_LINE, failed)
    if words.count(GOAL_HEADING_WORD) != 1 or not line:
        raise ExtractionFailedError(
            "the 'Career goal' section does not draw its heading 'Goal' once and "
            "one goal line under it, so it is not the section measured and no "
            "goal is read off it.",
            url=JOURNEY_URL,
        )
    goal_line = people_data.sanitise(line, cap=GOAL_CAP)
    bold = sections.locator(GOAL_LINE + " b")
    bold_runs = await _count(bold, failed)
    goal = people_data.sanitise(await _text(bold, failed), cap=GOAL_CAP) if bold_runs == 1 else None
    buttons = sections.locator("button")
    edit = [await _text(buttons.nth(i), failed) for i in range(min(await _count(buttons, failed), 5))]
    return {
        "goal_line": goal_line,
        "goal": goal or None,
        "goal_truncated": len(people_data.sanitise(line, cap=2 * GOAL_CAP)) > len(goal_line),
        "bold_runs": bold_runs,
        "edit_control_drawn": edit.count(GOAL_EDIT_WORD) == 1,
        "reads_failed": failed[0],
    }
