"""The PEOPLE his Premium networking matches suggest: members hiring for a job, each a people record beside that job (census ``N 199``).

ONE ADMITTED ADDRESS, :data:`MATCHES_URL`. ``readonly.py`` admits it by one
anchored line (lane A, 2026-10-10, the allowlist-silence clause of
READ-PAST-AN-ACT-SUBSTRING). This module never navigates: the tool loads that
address once and hands the open page here. Nothing is pressed or followed:
each match's Message link and job link are read for their addresses only.

MEASURED on the live lane's session-12 capture (load 26, served exact; tracked
copy ``tests/fixtures/live12/premium_matches.html``, LinkedIn's words put back
by keyed shape in ``tests/fixtures/synthetic/live12_premium_matches_words.html``;
lane net7's record, section 2.6): one ``main``; a heading block; then two
MATCH CARDS, each

* ONE link to a member's profile, holding the member's picture and three lines:
  the NAME (a paragraph holding a span), beside a paragraph with no child
  element that draws the DEGREE, and in the next block the HEADLINE (a
  paragraph holding a span);
* ONE link to a job, ``/jobs/view/<id>/``, whose line reads ``Hiring for``
  <strong>title</strong> ``at`` <strong>organisation</strong> -- the two words
  LinkedIn's, measured;
* one ``Message`` link to ``/messaging/compose/``, never followed.

THE CARD IS FOUND BY LINKEDIN'S OWN WORDS: a job link whose text opens
``Hiring for`` (matched in the page, so no text crosses to find it), and the
card is that link's nearest enclosing block holding a member link. Nothing is
aimed by a position among cards or by a class name, which are generated
hashes. Each card is resolved ONCE to a handle before any text is read, and
its member link read AGAIN after the text: a card whose link moved meanwhile is
skipped and counted, never returned -- ``people_results``' rule.

WHAT COMES BACK. Per card read, ``person`` -- one :class:`people_data.Person`
envelope (name, headline, canonical profile link, degree) under
PEOPLE-DATA-MITIGATIONS: declared fields only; sanitised and marked as another
member's words; never stored; bounded to one page, the first render, at most
:data:`MAX_MATCHES_READ` cards; visible only; never a target -- and
``hiring_for_job_id``, the job's id as ``linkedin_job_detail`` takes it, or
``None`` when the link carries none. The job's title and organisation are NOT
returned: ``linkedin_job_detail`` reads the job itself. The Message link's
member token is never read.

AN EMPTY PAGE RAISES: no capture draws it empty, so a zero cannot be
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
MATCHES_URL = f"{BASE_URL}/premium/matches/"

_HOST = "www.linkedin.com"
_PATH = "/premium/matches"

#: LinkedIn's own words on each card's job line, measured by keyed shape on
#: session 12's capture (load 26): ``Hiring for`` <title> ``at`` <organisation>.
HIRING_FOR = "Hiring for"
AT = "at"

#: The job line, as the page's text: opening with LinkedIn's words. Matched
#: inside the page (``has_text``), so the title and organisation never cross.
_HIRING_LINE = re.compile(r"^\s*" + HIRING_FOR + r"\s")

#: A member link and a job link, each in the two spellings a page writes one.
MEMBER_LINK = 'a[href^="https://www.linkedin.com/in/"], a[href^="/in/"]'
JOB_LINK = 'a[href^="https://www.linkedin.com/jobs/view/"], a[href^="/jobs/view/"]'

_MEMBER_HREF = (
    "starts-with(@href, 'https://www.linkedin.com/in/') "
    "or starts-with(@href, '/in/')"
)

#: A card: the job link's nearest enclosing block that holds a member link.
CARD = f"xpath=ancestor::div[.//a[{_MEMBER_HREF}]][1]"

#: Inside the member link: the degree line is the one paragraph with no child
#: element; the name is the paragraph holding a span in the block before it;
#: the headline the paragraph holding a span in the block after its own.
DEGREE_LINE = "xpath=.//p[not(*)]"
NAME_LINE = "xpath=.//p[not(*)]/preceding-sibling::*//p[span]"
HEADLINE_LINE = "xpath=.//p[not(*)]/parent::*/following-sibling::*//p[span]"

#: A job's id in its link, the digits ``linkedin_job_detail`` takes.
_JOB_ID = re.compile(r"/jobs/view/([0-9]{1,20})/?$")

#: Cards read per call, at most (measured: two on the first render). A budget
#: above the capture, not a measurement of anything LinkedIn does.
MAX_MATCHES_READ = 25

#: Why a whole read refuses. Closed.
REFUSALS = ("landed_elsewhere", "main_unreadable")

#: Why one card was not returned, in the order they are checked. Closed.
SKIP_REASONS: tuple[str, ...] = (
    "no_card",
    "not_one_member_link",
    "no_member_link",
    "not_one_name",
    "no_name",
    "changed_while_read",
    "already_returned",
)

SCOPE = (
    "The members his Premium networking matches suggest -- each hiring for a "
    "job -- on the page's first render only: one page, no scroll and no press, "
    "so cards past the first render are not read. Each comes back as a people "
    "record (PEOPLE-DATA-MITIGATIONS): declared fields only, sanitised and "
    "marked as another member's words, never stored; beside it the id of the "
    "job the member is hiring for, which linkedin_job_detail reads. No Message "
    "link is followed and no control is pressed. A zero raises."
)


def landed_on_the_matches(landed: Any) -> bool:
    """Did the load land on the matches page itself? PURE."""
    if not isinstance(landed, str) or not landed:
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return parts.scheme == "https" and parts.netloc == _HOST and parts.path.rstrip("/") == _PATH


def job_id_of(href: Any) -> Optional[str]:
    """The job's id in a job link, or ``None``. PURE."""
    text = str(href or "").strip()
    if not text:
        return None
    try:
        path = urlsplit(text).path
    except ValueError:
        return None
    found = _JOB_ID.search(path)
    return found.group(1) if found else None


def _reading() -> dict[str, Any]:
    """The answer's shape, every count at zero. Every key is fixed here."""
    return {
        "surface": "premium_networking_matches",
        "refused": None,
        "cards_seen": 0,
        "cards_attempted": 0,
        "matches": [],
        "skipped": {reason: 0 for reason in SKIP_REASONS},
        "failed": {},
        "headline_unread": 0,
        "one_page": True,
        "beyond_first_render": "not_read",
        "readable": False,
        "scope": SCOPE,
    }


def landed_elsewhere() -> dict[str, Any]:
    """The refusal for a load that did not land on the matches page."""
    out = _reading()
    out["refused"] = "landed_elsewhere"
    return out


async def _one(handle: Any, selector: str) -> Optional[Any]:
    """The one element ``selector`` finds under ``handle``, or ``None``."""
    found = list(await handle.query_selector_all(selector))
    return found[0] if len(found) == 1 else None


async def _match(job_link: Any) -> Any:
    """One card: ``(person, job id, headline read)`` or the SKIP_REASONS
    entry that stopped it."""
    card = await job_link.query_selector(CARD)
    if card is None:
        return "no_card"
    members = list(await card.query_selector_all(MEMBER_LINK))
    if len(members) != 1:
        return "not_one_member_link"
    member = members[0]
    link = people_data.canonical_profile_link(await member.get_attribute("href"))
    if link is None:
        return "no_member_link"
    name_line = await _one(member, NAME_LINE)
    if name_line is None:
        return "not_one_name"
    name = await name_line.inner_text()
    degree_line = await _one(member, DEGREE_LINE)
    degree = await degree_line.inner_text() if degree_line is not None else None
    headline_line = await _one(member, HEADLINE_LINE)
    headline = await headline_line.inner_text() if headline_line is not None else None
    job_id = job_id_of(await job_link.get_attribute("href"))
    # THE LINK AGAIN, AFTER EVERY TEXT READ: a node the page reused for another
    # member meanwhile would pair one person's name with another's link.
    if people_data.canonical_profile_link(await member.get_attribute("href")) != link:
        return "changed_while_read"
    person = people_data.Person.from_page(name=name, headline=headline, href=link, degree=degree)
    if person is None:
        return "no_name"
    return person, job_id, headline is not None


async def read_matches(page: Any) -> dict[str, Any]:
    """The members the matches page suggests, on the already-open page.

    The page must already be at :data:`MATCHES_URL`. One read of the first
    render; no navigation, press or scroll. Refuses when the page draws no
    single ``main`` (``main_unreadable``). Raises when no match card is drawn.
    Every string returned sits inside a :class:`people_data.Person` envelope;
    the rest are integers, closed literals, job ids and exception TYPE names.
    """
    out = _reading()
    main = page.locator("main")
    if await main.count() != 1:
        out["refused"] = "main_unreadable"
        return out
    job_links = list(
        await main.locator(JOB_LINK).filter(has_text=_HIRING_LINE).element_handles()
    )
    out["cards_seen"] = len(job_links)
    if not job_links:
        raise ExtractionFailedError(
            "the Premium networking matches page drew no match card (a job link "
            "opening 'Hiring for' beside a member link), and no empty state for "
            "this page has ever been captured to corroborate a zero, so it is "
            "reported as a failure.",
            url=MATCHES_URL,
        )
    to_read = min(len(job_links), MAX_MATCHES_READ)
    returned: set[str] = set()
    for job_link in job_links[:to_read]:
        try:
            verdict = await _match(job_link)
        except Exception as exc:  # noqa: BLE001 -- counted by TYPE, never quoted
            kind = type(exc).__name__
            out["failed"][kind] = out["failed"].get(kind, 0) + 1
            continue
        if isinstance(verdict, str):
            out["skipped"][verdict] += 1
            continue
        person, job_id, headline_read = verdict
        if person.link in returned:
            out["skipped"]["already_returned"] += 1
            continue
        returned.add(person.link)
        if not headline_read:
            out["headline_unread"] += 1
        out["matches"].append({"person": person.envelope(), "hiring_for_job_id": job_id})
    out["cards_attempted"] = to_read
    out["readable"] = bool(out["matches"])
    return out
