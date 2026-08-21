"""Turning a rendered card into a compact typed record.

Everything here is a pure function over strings. That is deliberate: the
parsing is the part most likely to be wrong, so it is the part that must be
testable without a browser, a network, or a LinkedIn account.

Two properties the shapers hold to:

* **Compact.** Fields are trimmed to :data:`config.MAX_TEXT_CHARS`. A tool
  result is a handful of short strings per row, never page text.
* **Absent, not invented.** A field that could not be read is omitted or
  ``None``. There is no "unknown company" placeholder that later reads like
  data.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional

from linkedin_own_server.config import MAX_TEXT_CHARS

# ---------------------------------------------------------------------------
# Text hygiene
# ---------------------------------------------------------------------------

_WS = re.compile(r"\s+")


def trim(text: Optional[str], limit: int = MAX_TEXT_CHARS) -> Optional[str]:
    """Collapse whitespace and cut to ``limit`` characters with an ellipsis."""
    if text is None:
        return None
    cleaned = _WS.sub(" ", str(text)).strip()
    if not cleaned:
        return None
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def clean_lines(text: str) -> list[str]:
    """Split card text into non-empty lines, dropping LinkedIn's echoes.

    LinkedIn renders many labels twice -- once visually and once in a
    screen-reader-only span -- so raw ``innerText`` is full of consecutive
    duplicates. Collapsing them is not cosmetic: without it the company name
    of a job card is whatever the duplicate of the title happens to be.
    """
    out: list[str] = []
    for raw in str(text or "").splitlines():
        line = _WS.sub(" ", raw).strip()
        if not line:
            continue
        if out and out[-1].casefold() == line.casefold():
            continue
        out.append(line)
    return out


#: Button and chrome labels that are never content.
_CHROME = {
    "message",
    "connect",
    "follow",
    "following",
    "save",
    "saved",
    "share",
    "more",
    "see more",
    "see all",
    "show more",
    "view profile",
    "dismiss",
    "remove",
    "easy apply",
    "apply",
    "promoted",
    "actively recruiting",
    "be an early applicant",
    "new",
    # The button on a privacy-limited profile-view row, where a named row
    # carries Message/Connect/Follow instead. Without it, "Search" is the
    # only line left after the name and becomes the anonymous viewer's
    # headline.
    "search",
}


#: Punctuation that decorates a chrome label without being part of it.
#: chr(0xB7) is the middle dot LinkedIn uses as a separator and chr(0x2022)
#: the bullet in front of a connection-degree badge; both are spelled this
#: way so the source file stays pure ASCII.
_LABEL_PUNCTUATION = " .*-" + chr(0xB7) + chr(0x2022)


def is_chrome(line: str) -> bool:
    """True for interface labels that should never be read as content."""
    return line.casefold().strip(_LABEL_PUNCTUATION) in _CHROME


#: Connection-degree badges. LinkedIn renders these as their own line
#: immediately under the name, so on a profile-view row the badge is the
#: FIRST candidate for the headline and wins it -- every viewer comes back
#: headlined "3rd" with their real headline discarded. Not chrome: a degree
#: is real information, it is simply not a headline.
_DEGREES = {"1st", "2nd", "3rd"}


def is_degree_badge(line: str) -> bool:
    """True for a line that is only a connection-degree badge."""
    return line.casefold().strip(_LABEL_PUNCTUATION) in _DEGREES


def content_lines(text: str) -> list[str]:
    """``clean_lines`` with interface chrome removed."""
    return [ln for ln in clean_lines(text) if not is_chrome(ln)]


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------

_TIME_AGO = re.compile(
    r"\b(\d+)\s*(second|minute|hour|day|week|month|year)s?\s+ago\b", re.I
)

#: LinkedIn's compact form: "Viewed 3d ago", "Viewed 1w ago", "Viewed 2mo
#: ago". The spelled-out pattern above misses every one of them, which is why
#: a profile-view row whose text plainly reads "Viewed 3d ago" came back with
#: ``viewed: null``. ``mo`` is listed before ``m`` on purpose -- alternation
#: is first-match, so the other order reads "2mo ago" as two MINUTES.
#: The literal word "ago" is still required, so a company called "3M" or a
#: line reading "1 reaction" cannot be mistaken for a time.
_TIME_AGO_COMPACT = re.compile(r"\b(\d+)\s*(mo|s|m|h|d|w|y)\s+ago\b", re.I)

_COMPACT_UNITS = {
    "s": "second",
    "m": "minute",
    "h": "hour",
    "d": "day",
    "w": "week",
    "mo": "month",
    "y": "year",
}

_RELATIVE_WORD = re.compile(r"\b(today|yesterday|just now)\b", re.I)


def has_time_ago(line: str) -> bool:
    """True when a line contains a relative timestamp in any of its forms."""
    text = str(line or "")
    return bool(
        _TIME_AGO.search(text)
        or _TIME_AGO_COMPACT.search(text)
        or _RELATIVE_WORD.search(text)
    )


def is_timestamp_line(line: str) -> bool:
    """True when a line is a timestamp and essentially nothing else.

    Distinct from "contains a timestamp" on purpose. A notification body like
    "Your application was viewed today by Acme" carries its time INLINE, and
    dropping that whole line to avoid repeating the time would throw away the
    notification.
    """
    remainder = _TIME_AGO.sub("", str(line or ""))
    remainder = _TIME_AGO_COMPACT.sub("", remainder)
    remainder = _RELATIVE_WORD.sub("", remainder)
    if remainder == line:
        return False
    return len(remainder.strip(" .,-|*/()")) < 3


def _spell(count: str, unit: str) -> str:
    """``('3', 'day')`` -> ``'3 days ago'``."""
    return f"{count} {unit}" + ("s ago" if count != "1" else " ago")


def find_time_ago(lines: Iterable[str]) -> Optional[str]:
    """Return the first relative timestamp found, e.g. ``'3 days ago'``.

    Compact forms are normalised to the spelled-out one, so a caller never
    has to know which of LinkedIn's two notations a given surface used.
    """
    for line in lines:
        match = _TIME_AGO.search(line)
        if match:
            return _spell(match.group(1), match.group(2).lower())
        compact = _TIME_AGO_COMPACT.search(line)
        if compact:
            return _spell(
                compact.group(1), _COMPACT_UNITS[compact.group(2).lower()]
            )
        word = _RELATIVE_WORD.search(line)
        if word:
            return word.group(1).lower()
    return None


_JOB_ID = re.compile(r"/jobs/view/(?:[^/?#]*-)?(\d{6,})")
_JOB_ID_PARAM = re.compile(r"[?&]currentJobId=(\d{6,})")
_PROFILE_SLUG = re.compile(r"/in/([A-Za-z0-9\-_%]+)")


def job_id_from(href: str) -> Optional[str]:
    """Pull the numeric job id out of a LinkedIn job url."""
    for pattern in (_JOB_ID, _JOB_ID_PARAM):
        match = pattern.search(href or "")
        if match:
            return match.group(1)
    return None


def profile_slug_from(href: str) -> Optional[str]:
    """Pull the public identifier out of a ``/in/<slug>`` url."""
    match = _PROFILE_SLUG.search(href or "")
    if not match:
        return None
    slug = match.group(1)
    return None if slug.lower() == "me" else slug


def absolute_url(href: str) -> Optional[str]:
    """Make a LinkedIn href absolute and strip its tracking query string."""
    if not href:
        return None
    url = href if href.startswith("http") else "https://www.linkedin.com" + href
    return url.split("?", 1)[0]


# ---------------------------------------------------------------------------
# Card shapers
# ---------------------------------------------------------------------------

#: Lines that mean "this row is a privacy-limited viewer", not a name.
#:
#: This list is a SECOND opinion, never the only one. The reliable signal is
#: structural: LinkedIn draws a privacy-limited viewer with no link at all,
#: so a row that produced no profile slug is anonymous whatever its text
#: says. That matters because the phrasing varies with how much the viewer
#: chose to reveal -- "Someone at Acme", "Recruiter at Acme", "Business
#: Analyst at Acme" -- and a list of phrases would always be one LinkedIn
#: wording behind.
_ANONYMOUS_MARKERS = (
    "linkedin member",
    "someone at",
    "anonymous linkedin member",
    "private mode",
    "viewer from",
)

#: "N mutual connections" is a relationship fact, not a headline, and it sits
#: exactly where a headline would on a row whose headline is missing.
_MUTUALS = re.compile(r"^\d+\s+mutual\s+connections?$", re.I)

#: A line that says something VIEWED THE PROFILE is about the page, not about
#: a person on it. Two real strings match: the page heading "Who's viewed
#: your profile", and the roll-up card "2 recruiters viewed your profile"
#: that sits in the middle of the list. Both have been emitted as viewers --
#: the heading four times over, each with a different real viewer's link
#: attached to it, which is a worse failure than returning nothing.
_ABOUT_THE_PAGE = re.compile(r"viewed your profile", re.I)


def parse_person_card(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Shape one profile-view row.

    ``record`` is ``{"href": ..., "text": ...}`` as harvested from the page.
    Returns ``None`` when the row is not a viewer, so callers can count what
    was dropped rather than emit blanks -- or worse, emit page furniture
    wearing a person's link.

    Two invariants decide whether a row is a person, and both are properties
    of the surface rather than a list of strings to keep up to date:

    * it does not claim something viewed the profile -- that is the page
      talking about itself;
    * it carries a "Viewed <when>" line. Every row LinkedIn draws here has
      one. Requiring it is what rejects the heading block and the recruiter
      roll-up without needing to recognise them by name, and if LinkedIn ever
      drops the timestamp this reads as zero rows, which the tool reports as
      a failure. That is the intended trade: a loud nothing beats a confident
      wrong.
    """
    lines = content_lines(record.get("text", ""))
    if not lines:
        return None

    name = trim(lines[0], 120)
    if not name:
        return None
    if _ABOUT_THE_PAGE.search(name):
        return None

    when = find_time_ago(lines)
    if not when:
        return None

    headline = None
    for line in lines[1:]:
        if has_time_ago(line) or is_degree_badge(line) or _MUTUALS.match(line):
            continue
        headline = trim(line)
        if headline:
            break

    slug = profile_slug_from(record.get("href", ""))
    anonymous = slug is None or any(
        marker in name.casefold() for marker in _ANONYMOUS_MARKERS
    )
    out: dict[str, Any] = {
        "name": name,
        "headline": headline,
        "viewed": when,
        "anonymous": anonymous,
    }
    if slug and not anonymous:
        out["profile"] = f"https://www.linkedin.com/in/{slug}"
    return out


#: A status is a line that IS a status, not a line that contains a status
#: word. Anchoring matters: "Applied Scientist" is a job title, and a
#: substring match would eat it as the status and shift every other field up
#: by one.
_JOB_STATUS_LINE = re.compile(
    r"^\s*(application (?:viewed|sent|submitted)|applied|viewed|"
    r"resume downloaded|no longer accepting applications|not selected|"
    r"in review|interview)"
    r"(?:\s*(?:[-.,]|on\b|\d).*)?\s*$",
    re.I,
)


def parse_job_card(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Shape one job row (saved, applied, or a search result).

    The first three content lines of a LinkedIn job card are title, company
    and location in that order. Anything matching a status or a relative
    timestamp is lifted out first so it cannot be mistaken for one of them.
    """
    lines = content_lines(record.get("text", ""))
    if not lines:
        return None

    status = None
    when = find_time_ago(lines)
    remaining: list[str] = []
    for line in lines:
        match = _JOB_STATUS_LINE.match(line)
        if match:
            # Every status-shaped line is lifted out, not just the first. A
            # second one falling through would land in title or company.
            if status is None:
                status = match.group(1).lower()
            continue
        if has_time_ago(line):
            continue
        remaining.append(line)

    if not remaining:
        return None

    job_id = job_id_from(record.get("href", ""))
    out: dict[str, Any] = {
        "title": trim(remaining[0], 120),
        "company": trim(remaining[1], 100) if len(remaining) > 1 else None,
        "location": trim(remaining[2], 100) if len(remaining) > 2 else None,
    }
    if status:
        out["status"] = status
    if when:
        out["when"] = when
    if job_id:
        out["job_id"] = job_id
        out["url"] = f"https://www.linkedin.com/jobs/view/{job_id}"
    return out


def parse_notification(record: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Shape one notification row into a single line of text plus a link."""
    lines = content_lines(record.get("text", ""))
    if not lines:
        return None
    when = find_time_ago(lines)
    # Drop lines that ARE the timestamp; keep lines that merely contain one,
    # or a notification reading "viewed your profile today" loses its text.
    body = " ".join(ln for ln in lines if not is_timestamp_line(ln))
    body = trim(body)
    if not body:
        return None
    out: dict[str, Any] = {"text": body}
    if when:
        out["when"] = when
    link = absolute_url(record.get("href", ""))
    if link:
        out["link"] = link
    return out


# ---------------------------------------------------------------------------
# Result envelope
# ---------------------------------------------------------------------------


def envelope(
    rows: list[dict[str, Any]],
    *,
    limit: int,
    source_url: str,
    pages_loaded: int = 1,
    dropped: int = 0,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Wrap rows with the honesty fields every tool result carries.

    ``capped`` says whether the limit trimmed the list, and ``page_had``
    counts the CARDS the single page load produced -- parsed rows plus any
    that could not be read. Counting only the parsed ones would make a page
    of 28 cards report ``page_had: 25, capped: false``, and the operator
    would conclude he had reached the end of the list when he had not.
    """
    found = len(rows)
    trimmed = rows[:limit]
    out: dict[str, Any] = {
        "count": len(trimmed),
        "page_had": found + dropped,
        "capped": found > limit,
        "limit": limit,
        "pages_loaded": pages_loaded,
        "source_url": source_url,
    }
    if dropped:
        out["unparsed_rows"] = dropped
    if extra:
        out.update(extra)
    out["results"] = trimmed
    return out
